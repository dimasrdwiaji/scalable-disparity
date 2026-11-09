"""
Ingest the local (non-Earth-Engine) raw inputs for the Physical Living Standard Index (PLSI).

Raster channels (Sentinel-2, Landsat, Dynamic World, VIIRS, Sentinel-5P, GHSL, Open Buildings
Temporal) are reduced on Earth Engine inside the Stage 3 pipeline (ADR 0002), so this script
only fetches vector and validation inputs:
1. Overture Maps amenities (places + open-space land use) -> GeoParquet
2. Overture Maps building footprints & heights -> GeoParquet
3. Dated OSM extract (nearest the reference snapshot date) for pedestrian routing -> .osm.pbf
4. Open-Meteo hourly air quality medians for the reference year (validation only) -> GeoParquet

ACAG PM2.5 monthly NetCDF files must be downloaded manually (Box links only) into
`air_quality.acag_dir`; see src/phys_living_index/data/ingest_acag.py.

Failures raise; nothing is replaced with placeholder values.
"""

import argparse
import json
import logging
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import geopandas as gpd
import yaml

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "src"))

from phys_living_index.data.ingest_buildings import derive_floor_count  # noqa: E402
from phys_living_index.data.ingest_context import (  # noqa: E402
    fetch_openmeteo_hourly_median,
    generate_sampling_grid,
)
from phys_living_index.data.ingest_overture import (  # noqa: E402
    DEFAULT_OVERTURE_RELEASE,
    get_duckdb_spatial_connection,
)
from phys_living_index.pipeline.stage3 import RegionRun, ensure_osm_extract  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingestion")


def _sql_list(values: list[str]) -> str:
    return ", ".join("'" + v.replace("'", "''") + "'" for v in values)


def ingest_amenities(config: dict, raw_dir: Path, release: str) -> dict:
    bbox = config["spatial"]["bbox"]
    acc = config["accessibility"]
    out = (raw_dir / "overture_amenities.parquet").as_posix()
    con = get_duckdb_spatial_connection()
    con.execute(f"""
    COPY (
        SELECT id, names.primary AS name, coalesce(taxonomy.primary, basic_category) AS category, geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=places/type=place/*', hive_partitioning=true)
        WHERE bbox.xmin >= {bbox[0]} AND bbox.xmax <= {bbox[2]}
          AND bbox.ymin >= {bbox[1]} AND bbox.ymax <= {bbox[3]}
          AND coalesce(taxonomy.primary, basic_category) IN ({_sql_list(acc["amenity_categories"])})
        UNION ALL
        SELECT id, names.primary AS name, subtype AS category, geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=base/type=land_use/*', hive_partitioning=true)
        WHERE bbox.xmin >= {bbox[0]} AND bbox.xmax <= {bbox[2]}
          AND bbox.ymin >= {bbox[1]} AND bbox.ymax <= {bbox[3]}
          AND subtype IN ({_sql_list(acc["open_space_subtypes"])})
    ) TO '{out}' (FORMAT PARQUET);
    """)
    count = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out}')").fetchone()[0]
    con.close()
    return {"file": out, "release": release, "record_count": int(count)}


def ingest_buildings(config: dict, raw_dir: Path, release: str) -> dict:
    bbox = config["spatial"]["bbox"]
    path = raw_dir / "buildings.parquet"
    con = get_duckdb_spatial_connection()
    con.execute(f"""
    COPY (
        SELECT id, height, num_floors, subtype, class, geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=buildings/type=building/*', hive_partitioning=true)
        WHERE bbox.xmin >= {bbox[0]} AND bbox.xmax <= {bbox[2]}
          AND bbox.ymin >= {bbox[1]} AND bbox.ymax <= {bbox[3]}
    ) TO '{path.as_posix()}' (FORMAT PARQUET);
    """)
    con.close()

    gdf = gpd.read_parquet(path)
    gdf["floor_count"] = derive_floor_count(gdf)
    gdf["confidence"] = 0.85  # Standard Overture conflated confidence
    gdf = gdf[["id", "geometry", "height", "confidence", "floor_count"]]
    gdf.to_parquet(path)
    return {
        "file": str(path),
        "release": release,
        "record_count": len(gdf),
        "with_explicit_height": int(gdf["height"].notnull().sum()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", default=str(repo_root / "configs" / "default.yaml"))
    parser.add_argument("--root", default=str(repo_root), help="Region data root (writes <root>/data/raw).")
    parser.add_argument(
        "--only", nargs="*", default=["amenities", "buildings", "osm", "openmeteo"],
        help="Subset of: amenities buildings osm openmeteo",
    )
    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    root = Path(args.root)
    raw_dir = root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    release = DEFAULT_OVERTURE_RELEASE
    year = int(config["reference_epoch"]["year"])

    report: dict = {"execution_time_utc": datetime.now(UTC).isoformat(), "bbox": config["spatial"]["bbox"], "datasets": {}}

    steps = {
        "amenities": lambda: ingest_amenities(config, raw_dir, release),
        "buildings": lambda: ingest_buildings(config, raw_dir, release),
        "osm": lambda: {"file": str(ensure_osm_extract(RegionRun(config, root, [], raw_dir)))},
        "openmeteo": lambda: {"file": str(fetch_openmeteo_hourly_median(
            generate_sampling_grid(tuple(config["spatial"]["bbox"]), config["air_quality"]["openmeteo_validation_step_deg"]),
            f"{year}-01-01", f"{year}-12-31",
            raw_dir / f"openmeteo_hourly_median_{year}.parquet",
        ))},
    }
    for name in args.only:
        logger.info("=== Ingesting %s ===", name)
        t0 = time.time()
        report["datasets"][name] = {**steps[name](), "elapsed_sec": round(time.time() - t0, 1)}

    report_path = raw_dir / "ingestion_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    logger.info("Ingestion report written to %s", report_path)


if __name__ == "__main__":
    main()
