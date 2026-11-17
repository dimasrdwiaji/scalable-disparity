"""
Residential cell mask, population density, and built-stock epoch-gap check (ADR 0002 §1, §6).

A residential cell has population density >= the universal threshold (default 300 persons/km²,
the lowest GHSL Degree of Urbanisation settlement threshold) and at least one building.
Only residential cells enter the training loss and disparity metrics.
"""

from collections.abc import Sequence

import h3
import numpy as np
import pandas as pd


def cell_areas_km2(cells: Sequence[str]) -> pd.Series:
    """Exact area of each H3 cell in km² (cells vary around the 0.737 km² mean)."""
    return pd.Series([h3.cell_area(c, unit="km^2") for c in cells], index=list(cells))


def population_density(population: pd.Series) -> pd.Series:
    """Persons per km² from per-cell population, using each cell's exact area."""
    return population / cell_areas_km2(population.index).to_numpy()


def residential_mask(
    density_per_km2: pd.Series,
    building_count: pd.Series,
    min_density_per_km2: float = 300.0,
    min_building_count: int = 1,
) -> pd.Series:
    """Residential cells: density at or above the threshold and at least `min_building_count` buildings."""
    buildings = building_count.reindex(density_per_km2.index).fillna(0)
    return (density_per_km2.fillna(0.0) >= min_density_per_km2) & (buildings >= min_building_count)


def compute_residential_plan_area_fraction(
    net_res_footprint_m2: pd.Series,
    cells: Sequence[str] | None = None,
    is_residential: pd.Series | None = None,
) -> pd.Series:
    """
    Computes Residential Plan Area Fraction (lambda_p_res):
    Ratio of net residential building wall footprint area to total H3 cell area (m^2),
    bounded strictly in [0.0, 1.0].

    - High values (> 0.60 - 0.85): Hyper-dense informal settlements / kampungs with continuous roof cover.
    - Moderate values (0.25 - 0.45): Planned formal neighborhoods with mandatory setbacks.
    - Non-residential cells (where is_residential is False) are masked to NaN.
    """
    cell_idx = list(cells) if cells is not None else list(net_res_footprint_m2.index)
    areas_m2 = cell_areas_km2(cell_idx) * 1e6

    net_fp = net_res_footprint_m2.reindex(cell_idx).fillna(0.0)
    lambda_p = (net_fp / areas_m2).clip(lower=0.0, upper=1.0)

    if is_residential is not None:
        mask = is_residential.reindex(cell_idx).fillna(False)
        lambda_p = lambda_p.where(mask, np.nan)

    return lambda_p


def mask_sensitivity(
    density_per_km2: pd.Series,
    building_count: pd.Series,
    thresholds_per_km2: Sequence[float],
    indicators: dict[str, pd.Series] | None = None,
    min_building_count: int = 1,
) -> pd.DataFrame:
    """
    Residential cell count and indicator medians/IQR at alternative density thresholds.

    Parameters
    ----------
    density_per_km2, building_count : pd.Series
        Per-cell density and building count.
    thresholds_per_km2 : Sequence[float]
        Density thresholds to compare (e.g. 150, 300, 1500).
    indicators : dict[str, pd.Series] | None
        Raw indicators (e.g. R_space, amenities) summarized over residential cells.

    Returns
    -------
    pd.DataFrame
        One row per threshold.
    """
    rows = []
    for threshold in thresholds_per_km2:
        mask = residential_mask(density_per_km2, building_count, threshold, min_building_count)
        row: dict[str, float] = {"min_density_per_km2": float(threshold), "residential_cells": int(mask.sum())}
        for name, series in (indicators or {}).items():
            values = series.reindex(mask.index)[mask].dropna()
            row[f"{name}_p25"] = float(values.quantile(0.25)) if len(values) else np.nan
            row[f"{name}_median"] = float(values.median()) if len(values) else np.nan
            row[f"{name}_p75"] = float(values.quantile(0.75)) if len(values) else np.nan
        rows.append(row)
    return pd.DataFrame(rows).set_index("min_density_per_km2")


def built_surface_change_share(
    built_early: pd.Series,
    built_late: pd.Series,
    mask: pd.Series,
    relative_threshold: float = 0.10,
) -> dict[str, float]:
    """
    Epoch-gap check: share of masked cells whose built surface changed by more than
    `relative_threshold` between two GHS-BUILT-S epochs.
    """
    early = built_early.reindex(mask.index)[mask]
    late = built_late.reindex(mask.index)[mask]
    with np.errstate(divide="ignore", invalid="ignore"):
        rel = (late - early).abs() / early.where(early > 0)
    changed = (rel > relative_threshold) | ((early <= 0) & (late > 0))
    return {
        "cells": int(mask.sum()),
        "share_changed": float(changed.mean()) if len(changed) else np.nan,
        "median_relative_change": float(rel.median()) if rel.notna().any() else np.nan,
        "relative_threshold": relative_threshold,
    }
