"""
Validation module comparing model-derived physical living space against BPS Susenas survey targets.

Authoritative BPS benchmarks are stored in `data/external/susenas/bps_susenas_housing_2023.csv`.
Calculates:
- Population-weighted median and mean living space per capita by administrative region.
- Share of population in cells with <= 7.2 m2/capita (SDG 11.1.1 living space standard).
- Ratio and discrepancy against Susenas survey ground truth.
"""

from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd


def compute_pop_weighted_median(values: pd.Series, weights: pd.Series) -> float:
    """Computes population-weighted median of values given weights."""
    valid = values.notna() & weights.notna() & (weights > 0)
    if not valid.any():
        return np.nan
    v = values[valid].to_numpy()
    w = weights[valid].to_numpy()
    sorter = np.argsort(v)
    v_sorted = v[sorter]
    w_sorted = w[sorter]
    cum_w = np.cumsum(w_sorted)
    cutoff = 0.5 * cum_w[-1]
    idx = np.searchsorted(cum_w, cutoff)
    return float(v_sorted[min(idx, len(v_sorted) - 1)])


def evaluate_against_susenas(
    raw_features: pd.DataFrame,
    admin_boundaries_path: str | Path,
    susenas_benchmark_path: str | Path,
    floor_area_col: str = "floor_area_m2",
    pop_col: str = "population",
) -> pd.DataFrame:
    """
    Evaluates cell-level living space estimates against BPS Susenas survey data per regency/city.

    Parameters
    ----------
    raw_features : pd.DataFrame
        DataFrame indexed by H3 hex ID containing lat, lon, population, and floor area.
    admin_boundaries_path : str | Path
        Path to administrative boundaries GeoJSON.
    susenas_benchmark_path : str | Path
        Path to BPS Susenas benchmark CSV.
    floor_area_col : str, default "floor_area_m2"
        Name of floor area column to evaluate.
    pop_col : str, default "population"
        Name of population column.

    Returns
    -------
    pd.DataFrame
        Comparative table by administrative entity.
    """
    adm = gpd.read_file(admin_boundaries_path)
    susenas = pd.read_csv(susenas_benchmark_path)

    # Filter to residential cells with positive population
    res = raw_features[raw_features.get("is_residential", True)].copy()
    res = res[res[pop_col] > 0]
    res["m2_per_capita"] = res[floor_area_col] / res[pop_col]

    pts = gpd.GeoDataFrame(
        res[[pop_col, floor_area_col, "m2_per_capita"]],
        geometry=gpd.points_from_xy(res["lon"], res["lat"]),
        crs="EPSG:4326",
    )

    name_col = "clean_name" if "clean_name" in adm.columns else "name"
    joined = gpd.sjoin(pts, adm[[name_col, "geometry"]].to_crs("EPSG:4326"), predicate="within", how="left")

    records: list[dict[str, Any]] = []
    for clean_name, group in joined.groupby(name_col):
        pop_total = float(group[pop_col].sum())
        fa_total = float(group[floor_area_col].sum())
        pw_mean = fa_total / max(pop_total, 1.0)
        pw_median = compute_pop_weighted_median(group["m2_per_capita"], group[pop_col])
        share_le_7_2 = float((group.loc[group["m2_per_capita"] <= 7.2, pop_col].sum() / max(pop_total, 1.0)) * 100)
        share_le_9_0 = float((group.loc[group["m2_per_capita"] <= 9.0, pop_col].sum() / max(pop_total, 1.0)) * 100)

        records.append({
            "clean_name": clean_name,
            "pop_modeled": pop_total,
            "floor_area_modeled_m2": fa_total,
            "modeled_pw_mean_m2": round(pw_mean, 2),
            "modeled_pw_median_m2": round(pw_median, 2),
            "modeled_pct_le_7_2m2": round(share_le_7_2, 2),
            "modeled_pct_le_9_0m2": round(share_le_9_0, 2),
            "cells_count": len(group),
        })

    summary = pd.DataFrame(records)

    # Name mapping between clean_name in GeoJSON and region in BPS Susenas CSV
    name_mapping = {
        "Jakarta Selatan": "DKI Jakarta",
        "Jakarta Timur": "DKI Jakarta",
        "Jakarta Pusat": "DKI Jakarta",
        "Jakarta Barat": "DKI Jakarta",
        "Jakarta Utara": "DKI Jakarta",
        "Kepulauan Seribu": "DKI Jakarta",
        "Kota Bogor": "Kota Bogor",
        "Kabupaten Bogor": "Kabupaten Bogor",
        "Kota Depok": "Kota Depok",
        "Kota Tangerang": "Kota Tangerang",
        "Tangerang": "Kabupaten Tangerang",
        "South Tangerang City": "Kota Tangerang Selatan",
        "Kota Bekasi": "Kota Bekasi",
        "Kabupaten Bekasi": "Kabupaten Bekasi",
        "Kabupaten Karawang": "Kabupaten Karawang",
        "Cianjur": "Kabupaten Cianjur",
    }
    summary["region_susenas"] = summary["clean_name"].map(name_mapping).fillna(summary["clean_name"])

    merged = summary.merge(susenas, left_on="region_susenas", right_on="region", how="left")
    merged["ratio_median_to_susenas"] = round(merged["modeled_pw_median_m2"] / merged["median_floor_area_per_capita_m2"], 2)
    merged["diff_median_to_susenas_m2"] = round(merged["modeled_pw_median_m2"] - merged["median_floor_area_per_capita_m2"], 2)

    return merged
