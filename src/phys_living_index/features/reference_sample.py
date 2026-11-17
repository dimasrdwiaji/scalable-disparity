"""
Global reference sample for universal benchmarks (ADR 0003 §2, Stage 3 ticket 14).

1. Select a frozen, stratified set of urban centres (world region × climate × size class).
2. Pool an equal number of randomly drawn residential cells from every city, so no city
   dominates the pooled distribution.
3. Set each reference-derived channel bound to P1/P99 of the pooled, transformed values
   (bounds marked `standard` are kept), and write a new versioned benchmark file.
"""

import math
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from .build_features import BenchmarkSet, apply_transform

SIZE_CLASS_EDGES = (0.0, 300_000.0, 1_000_000.0, 5_000_000.0, math.inf)
SIZE_CLASS_LABELS = ("small", "medium", "large", "megacity")


def size_class(population: pd.Series) -> pd.Series:
    """Bins urban-centre population into small / medium / large / megacity."""
    return pd.cut(population, bins=list(SIZE_CLASS_EDGES), labels=list(SIZE_CLASS_LABELS), right=False).astype(str)


def select_reference_cities(
    centres: pd.DataFrame,
    n_per_stratum: int,
    seed: int,
    strata: Sequence[str] = ("world_region", "climate_class", "size_class"),
) -> pd.DataFrame:
    """
    Stratified random sample of urban centres: up to `n_per_stratum` per stratum.

    Parameters
    ----------
    centres : pd.DataFrame
        One row per urban centre with the `strata` columns (e.g. from the GHS Urban Centre
        Database, with `size_class` from `size_class`).
    n_per_stratum : int
        Cities drawn per stratum (all of them if the stratum is smaller).
    seed : int
        Random seed, frozen with the benchmark version.

    Returns
    -------
    pd.DataFrame
        Selected centres, sorted by stratum then input order.
    """
    rng = np.random.default_rng(seed)
    picked = []
    for _, group in centres.groupby(list(strata), sort=True):
        take = min(n_per_stratum, len(group))
        picked.append(group.iloc[np.sort(rng.choice(len(group), size=take, replace=False))])
    return pd.concat(picked) if picked else centres.iloc[0:0]


def pool_city_cells(
    city_tables: dict[str, pd.DataFrame],
    cells_per_city: int,
    seed: int,
    mask_col: str = "is_residential",
) -> pd.DataFrame:
    """
    Draws the same number of residential cells from each city (all if fewer) and pools them.

    Returns
    -------
    pd.DataFrame
        Pooled rows with a `city` column.
    """
    rng = np.random.default_rng(seed)
    pooled = []
    for city in sorted(city_tables):
        table = city_tables[city]
        residential = table[table[mask_col].astype(bool)]
        take = min(cells_per_city, len(residential))
        rows = residential.iloc[np.sort(rng.choice(len(residential), size=take, replace=False))]
        pooled.append(rows.assign(city=city))
    return pd.concat(pooled)


def reference_bounds(
    pooled: pd.DataFrame,
    benchmarks: BenchmarkSet,
    lower_pct: float = 1.0,
    upper_pct: float = 99.0,
) -> dict[str, dict[str, float]]:
    """
    P1/P99 of each non-standard channel's transformed values over the pooled sample.

    Channels whose `bound_source` is `standard` keep their bounds; a channel with a standard
    lower bound only (e.g. PM2.5 at the WHO guideline) is handled by the caller.
    """
    bounds: dict[str, dict[str, float]] = {}
    for c in benchmarks.channels:
        if c.bound_source == "standard":
            continue
        x = apply_transform(pooled[c.source].to_numpy(), c.transform)
        x = x[~np.isnan(x)]
        if x.size == 0:
            raise ValueError(f"No pooled values for {c.name} ({c.source})")
        bounds[c.name] = {
            "lower": float(np.percentile(x, lower_pct)),
            "upper": float(np.percentile(x, upper_pct)),
            "n": int(x.size),
        }
    return bounds


def city_clip_shares(pooled: pd.DataFrame, benchmarks: BenchmarkSet) -> pd.DataFrame:
    """Per city and channel, the share of pooled cells outside the bounds (dominance check)."""
    rows = []
    for city, group in pooled.groupby("city"):
        for c in benchmarks.channels:
            x = apply_transform(group[c.source].to_numpy(), c.transform)
            x = x[~np.isnan(x)]
            if x.size:
                rows.append({"city": city, "channel": c.name,
                             "share_outside": float(np.mean((x < c.lower) | (x > c.upper)))})
    return pd.DataFrame(rows)


def write_benchmark_version(
    base: dict[str, Any],
    bounds: dict[str, dict[str, float]],
    version: str,
    metadata: dict[str, Any],
    output_path: str | Path,
    keep_standard_lower: Sequence[str] = (
        "air_purity_pm25_inv",
        "space_sufficiency_ratio",
        "residential_plan_area_fraction",
        "terrain_safety_inv",
    ),
) -> Path:
    """
    Writes a new benchmark version from a base document and reference bounds.

    Parameters
    ----------
    base : dict
        Parsed base benchmark YAML (e.g. v0).
    bounds : dict
        Output of `reference_bounds`.
    version : str
        New version label, e.g. 'v1'.
    metadata : dict
        Reference sample record (city list, seed, cells per city, date).
    keep_standard_lower : Sequence[str]
        Channels whose lower bound is a standard and only the upper bound is replaced.
    """
    doc = {**base, "version": version, "provisional": False, "reference_sample": metadata}
    channels = []
    for channel in base["channels"]:
        channel = dict(channel)
        if channel["name"] in bounds:
            b = bounds[channel["name"]]
            if channel["name"] not in keep_standard_lower:
                channel["lower"] = round(b["lower"], 6)
            channel["upper"] = round(b["upper"], 6)
            channel["bound_source"] = "reference_p1_p99"
        channels.append(channel)
    doc["channels"] = channels
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, sort_keys=False)
    return output_path


def smallest_containing_extract(index_features: list[dict[str, Any]], bbox: Sequence[float]) -> dict[str, Any]:
    """
    The smallest Geofabrik extract (from index-v1.json features) whose polygon contains bbox.

    Raises
    ------
    LookupError
        If no extract contains the bounding box.
    """
    from shapely.geometry import box, shape

    target = box(*bbox)
    best = None
    for feature in index_features:
        if not feature.get("geometry") or "pbf" not in feature.get("properties", {}).get("urls", {}):
            continue
        geom = shape(feature["geometry"])
        if geom.contains(target) and (best is None or geom.area < best[0]):
            best = (geom.area, feature["properties"])
    if best is None:
        raise LookupError(f"No Geofabrik extract contains {list(bbox)}")
    return best[1]


def dated_extract_url(latest_url: str, snapshot_date: str) -> str:
    """Geofabrik dated extract URL for a snapshot date (e.g. 2024-01-01 -> -240101.osm.pbf)."""
    stamp = pd.Timestamp(snapshot_date).strftime("%y%m%d")
    if not latest_url.endswith("-latest.osm.pbf"):
        raise ValueError(f"Unexpected Geofabrik URL {latest_url}")
    return latest_url.replace("-latest.osm.pbf", f"-{stamp}.osm.pbf")


def utm_epsg(lon: float, lat: float) -> str:
    """WGS84 UTM zone EPSG code for a point."""
    zone = int((lon + 180.0) // 6.0) + 1
    return f"EPSG:{(32600 if lat >= 0 else 32700) + zone}"


def driest_consecutive_months(monthly_precip: Sequence[float], length: int = 4) -> list[int]:
    """
    Calendar months (1-12) of the driest `length` consecutive months, wrapping around the year.
    This is the documented rule for each reference city's compositing window.
    """
    precip = np.asarray(monthly_precip, dtype=float)
    if precip.size != 12:
        raise ValueError("Expected 12 monthly values")
    sums = [precip[[(s + k) % 12 for k in range(length)]].sum() for s in range(12)]
    start = int(np.argmin(sums))
    return [((start + k) % 12) + 1 for k in range(length)]


def window_tiers(year: int, months: Sequence[int]) -> list[list[list[str]]]:
    """
    Window ladder for a city from its driest months: Tier 1 the driest months, Tier 2 one
    month wider each side, Tier 3 the driest months of the year and the next.
    """

    def span(y: int, first: int, n: int) -> list[str]:
        start = pd.Timestamp(year=y, month=1, day=1) + pd.DateOffset(months=first - 1)
        end = start + pd.DateOffset(months=n)
        return [start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")]

    first, n = int(months[0]), len(months)
    return [
        [span(year, first, n)],
        [span(year, first - 1, n + 2)],
        [span(year, first, n), span(year + 1, first, n)],
    ]
