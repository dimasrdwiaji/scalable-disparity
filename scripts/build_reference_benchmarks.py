"""
Build the global reference sample and freeze a universal benchmark version (ADR 0003, ticket 14).

Steps (run in order; each is resumable):

  select   Stratified selection of urban centres from a centre table, frozen with a seed.
           Input CSV columns: name, country, world_region, climate_class, population,
           min_lon, min_lat, max_lon, max_lat (e.g. exported from the GHS Urban Centre
           Database; climate_class = Köppen main class).
  prepare  Per city, derive measurement settings by documented rules and write
           data/reference/<slug>/config.yaml:
             - UTM zone from the bbox centre
             - compositing window = the 4 driest consecutive months (ERA5-Land 2013-2022),
               ladder from `window_tiers`
             - OSM extract = smallest Geofabrik extract containing the bbox, dated to the
               snapshot date when that file exists (otherwise latest, recorded)
  run      Per city: ingest vector inputs, then run the Stage 3 pipeline (raw features).
           Failures are recorded per city and skipped.
  pool     Pool an equal number of residential cells per city, compute P1/P99 bounds and
           write configs/benchmarks/benchmarks_<version>.yaml plus a pooling report.

Usage:
  uv run python scripts/build_reference_benchmarks.py select --centres ucdb.csv --n-per-stratum 2 --seed 20261102
  uv run python scripts/build_reference_benchmarks.py prepare
  uv run python scripts/build_reference_benchmarks.py run
  uv run python scripts/build_reference_benchmarks.py pool --version v1 --cells-per-city 2000
"""

import argparse
import copy
import json
import logging
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import requests
import yaml

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "src"))

from phys_living_index.features.build_features import benchmark_path, load_benchmarks  # noqa: E402
from phys_living_index.features.reference_sample import (  # noqa: E402
    city_clip_shares,
    dated_extract_url,
    driest_consecutive_months,
    pool_city_cells,
    reference_bounds,
    select_reference_cities,
    size_class,
    smallest_containing_extract,
    utm_epsg,
    window_tiers,
    write_benchmark_version,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("reference")

REFERENCE_DIR = repo_root / "data" / "reference"
CITIES_CSV = repo_root / "configs" / "reference" / "cities.csv"
TEMPLATE_CONFIG = repo_root / "configs" / "default.yaml"
GEOFABRIK_INDEX = "https://download.geofabrik.de/index-v1.json"
REQUIRED = ["name", "country", "world_region", "climate_class", "population", "min_lon", "min_lat", "max_lon", "max_lat"]


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def cmd_select(args) -> None:
    centres = pd.read_csv(args.centres)
    missing = [c for c in REQUIRED if c not in centres.columns]
    if missing:
        raise SystemExit(f"Centre table lacks columns {missing}")
    centres["size_class"] = size_class(centres["population"])
    cities = select_reference_cities(centres, args.n_per_stratum, args.seed)
    cities["slug"] = [slugify(f"{n}_{c}") for n, c in zip(cities["name"], cities["country"], strict=True)]
    CITIES_CSV.parent.mkdir(parents=True, exist_ok=True)
    cities.to_csv(CITIES_CSV, index=False)
    meta = {"seed": args.seed, "n_per_stratum": args.n_per_stratum, "source": str(args.centres),
            "selected": len(cities), "date": datetime.now(UTC).date().isoformat()}
    CITIES_CSV.with_suffix(".json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    logger.info("Selected %d cities -> %s", len(cities), CITIES_CSV)


def _url_exists(url: str) -> bool:
    try:
        return requests.head(url, timeout=30, allow_redirects=True).status_code == 200
    except requests.RequestException:
        return False


def cmd_prepare(args) -> None:
    from phys_living_index.data.gee import initialize_ee
    from phys_living_index.data.gee_layers import monthly_precipitation_climatology

    initialize_ee()
    with open(TEMPLATE_CONFIG, encoding="utf-8") as f:
        template = yaml.safe_load(f)
    index = requests.get(GEOFABRIK_INDEX, timeout=120).json()["features"]
    cities = pd.read_csv(CITIES_CSV)
    year = int(template["reference_epoch"]["year"])
    snapshot = template["reference_epoch"]["snapshot_date"]

    for city in cities.itertuples():
        city_dir = REFERENCE_DIR / city.slug
        config_path = city_dir / "config.yaml"
        if config_path.exists():
            continue
        bbox = [city.min_lon, city.min_lat, city.max_lon, city.max_lat]
        months = driest_consecutive_months(monthly_precipitation_climatology(bbox, 2013, 2022), 4)
        tiers = window_tiers(year, months)
        extract = smallest_containing_extract(index, bbox)
        dated = dated_extract_url(extract["urls"]["pbf"], snapshot)
        osm_url = dated if _url_exists(dated) else extract["urls"]["pbf"]

        cfg = copy.deepcopy(template)
        cfg["project"]["study_area"] = city.slug
        cfg["spatial"]["bbox"] = bbox
        cfg["spatial"]["utm_crs"] = utm_epsg((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
        cfg["compositing"]["sentinel2"]["tiers"] = tiers
        cfg["compositing"]["landsat"]["tiers"] = tiers
        cfg["accessibility"]["osm_extract_url"] = osm_url
        cfg["air_quality"]["acag_dir"] = str((repo_root / template["air_quality"]["acag_dir"]).resolve())
        cfg["reference_city"] = {"name": city.name, "country": city.country, "dry_months": months,
                                 "osm_extract_dated": osm_url == dated}
        city_dir.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(cfg, f, sort_keys=False)
        logger.info("%s: dry months %s, %s, %s", city.slug, months, cfg["spatial"]["utm_crs"], osm_url)


def cmd_run(args) -> None:
    from phys_living_index.pipeline.stage3 import run_stage3

    cities = pd.read_csv(CITIES_CSV)
    status = {}
    for city in cities.itertuples():
        city_dir = REFERENCE_DIR / city.slug
        if (city_dir / "data" / "interim" / "h3_features_raw.parquet").exists():
            status[city.slug] = "done"
            continue
        try:
            subprocess.run(
                [sys.executable, str(repo_root / "scripts" / "run_ingestion.py"), "--config", str(city_dir / "config.yaml"),
                 "--root", str(city_dir), "--only", "amenities", "buildings", "osm"],
                check=True,
            )
            run_stage3(city_dir / "config.yaml", city_dir, config_dir=repo_root / "configs")
            status[city.slug] = "done"
        except Exception as exc:  # noqa: BLE001 - recorded per city, run continues
            logger.error("%s failed: %s", city.slug, exc)
            status[city.slug] = f"failed: {exc}"
    (REFERENCE_DIR / "run_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")


def cmd_pool(args) -> None:
    base_path = benchmark_path(args.base_version, repo_root / "configs")
    benchmarks = load_benchmarks(base_path)
    cities = pd.read_csv(CITIES_CSV)
    tables = {}
    for city in cities.itertuples():
        path = REFERENCE_DIR / city.slug / "data" / "interim" / "h3_features_raw.parquet"
        if path.exists():
            tables[city.slug] = pd.read_parquet(path)
    if len(tables) < args.min_cities:
        raise SystemExit(f"Only {len(tables)} cities finished; need at least {args.min_cities}.")

    pooled = pool_city_cells(tables, args.cells_per_city, args.seed)
    bounds = reference_bounds(pooled, benchmarks)
    with open(base_path, encoding="utf-8") as f:
        base = yaml.safe_load(f)
    meta = {"cities": sorted(tables), "cells_per_city": args.cells_per_city, "seed": args.seed,
            "pooled_cells": len(pooled), "date": datetime.now(UTC).date().isoformat(),
            "selection": json.loads(CITIES_CSV.with_suffix(".json").read_text(encoding="utf-8"))}
    out = write_benchmark_version(base, bounds, args.version, meta, benchmark_path(args.version, repo_root / "configs"))

    frozen = load_benchmarks(out)
    report_dir = REFERENCE_DIR / f"report_{args.version}"
    report_dir.mkdir(parents=True, exist_ok=True)
    city_clip_shares(pooled, frozen).to_csv(report_dir / "city_clip_shares.csv", index=False)
    pooled.describe().T.to_csv(report_dir / "pooled_describe.csv")
    logger.info("Wrote %s from %d cities (%d cells).", out, len(tables), len(pooled))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("select")
    p.add_argument("--centres", required=True)
    p.add_argument("--n-per-stratum", type=int, default=2)
    p.add_argument("--seed", type=int, default=20261102)
    sub.add_parser("prepare")
    sub.add_parser("run")
    p = sub.add_parser("pool")
    p.add_argument("--version", default="v1")
    p.add_argument("--base-version", default="v0")
    p.add_argument("--cells-per-city", type=int, default=2000)
    p.add_argument("--seed", type=int, default=20261102)
    p.add_argument("--min-cities", type=int, default=50)
    args = parser.parse_args()
    {"select": cmd_select, "prepare": cmd_prepare, "run": cmd_run, "pool": cmd_pool}[args.command](args)


if __name__ == "__main__":
    main()
