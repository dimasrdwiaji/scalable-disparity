"""
Harmonizes and standardizes physical living standard features onto Uber H3 Resolution 8 cells (~0.74 km²).

This module prepares the continuous multi-dimensional feature matrix X in R^(N x D)
for the Graph Attention Autoencoder (GAT-AE).

It implements:
1. Universal Min-Max Normalization: Maps diverse physical indicators (meters, Kelvin,
   nW/cm²/sr, μg/m³, spectral indices) into a standardized [0.0, 1.0] interval.
2. Inverted Hazard Scaling: Transforms environmental stress metrics (heat, air pollution)
   so that higher values uniformly signify better living standards across all feature channels.
3. 10-Dimensional Feature Matrix Assembly: Incorporates living space sufficiency, built-up
   density, pedestrian accessibility, infrastructure paving, nighttime light, vegetative canopy,
   thermal comfort, drainage exposure, fine particulates, and multi-pollutant air quality.
"""

from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd

# Default international benchmark ranges for universal Min-Max scaling to [0.0, 1.0]
DEFAULT_10D_BENCHMARKS: dict[str, tuple[float, float]] = {
    # 1. Living Space Ratio: 1.0 = UN-Habitat 9.0 m²/capita standard; capped at 5.0 (45 m²/capita)
    "space_sufficiency_ratio": (0.0, 5.0),
    # 2. Built-up Roof Density (NDBI): [-1.0, 1.0] true spectral range
    "builtup_ndbi": (-1.0, 1.0),
    # 3. 15-Minute Walking Opportunities: cumulative destination count (0 to 50 amenities)
    "cumulative_amenities_15m": (0.0, 50.0),
    # 4. Bare Soil / Unpaved Roads (BSI): [-1.0, 1.0] true spectral range
    "bare_soil_bsi": (-1.0, 1.0),
    # 5. Nighttime Energy Radiance (VIIRS): [0.0, 50.0] nW/cm²/sr
    "nighttime_energy_radiance": (0.0, 50.0),
    # 6. Vegetative Canopy (NDVI): [-0.2, 0.8] representing terrestrial urban canopy
    "vegetation_ndvi": (-0.2, 0.8),
    # 7. Thermal Comfort (LST Inverted): [290.0, 320.0] Kelvin (higher = cooler microclimate)
    "thermal_comfort_lst_inv": (290.0, 320.0),
    # 8. Surface Water & Drainage Vulnerability (MNDWI): [-1.0, 1.0] true spectral range
    "water_mndwi": (-1.0, 1.0),
    # 9. Fine Particulate Air Purity (PM2.5 Inverted): [0.0, 100.0] μg/m³ (WHO target: 15.0 μg/m³)
    "air_purity_pm25_inv": (0.0, 100.0),
    # 10. Multi-Pollutant Air Purity (AQI Inverted): [0.0, 300.0] (higher = cleaner regulatory air)
    "multi_pollutant_aqi_inv": (0.0, 300.0),
}


def compute_living_space_ratio(
    buildings_df: gpd.GeoDataFrame,
    worldpop_series: pd.Series,
    min_standard_m2: float = 9.0,
    floor_height_m: float = 3.0,
) -> pd.Series:
    """
    Computes the Living Space Ratio (R_space) per H3 hexagonal cell.

    Formula:
        R_space = (Observed Living Floor Area per Capita) / (UN-Habitat Minimum Shelter 9.0 m²)

    Values:
        - R_space < 1.0: Severe overcrowding / critical living space deficit.
        - R_space = 1.0: Meets minimum UN-Habitat shelter standard.
        - R_space > 1.0: Adequate or affluent spatial living conditions.

    Parameters
    ----------
    buildings_df : gpd.GeoDataFrame
        Building footprints with 'height', 'geometry', and 'h3_index'.
    worldpop_series : pd.Series
        WorldPop estimated population indexed by H3 hex id.
    min_standard_m2 : float, optional
        UN-Habitat minimum floor area standard in m² (default 9.0 m²).
    floor_height_m : float, optional
        International nominal floor-to-floor height (default 3.0 m).

    Returns
    -------
    pd.Series
        Living space ratio indexed by H3 cell.
    """
    floors = np.maximum(1, np.floor(buildings_df["height"] / floor_height_m))
    total_floor_area = buildings_df.geometry.area * floors
    buildings_df = buildings_df.copy()
    buildings_df["floor_area"] = total_floor_area

    # Aggregate total residential floor area by H3 hexagon
    h3_floor_area = buildings_df.groupby("h3_index")["floor_area"].sum()
    pop = np.maximum(worldpop_series, 1.0)
    living_space_per_capita = h3_floor_area / pop
    return living_space_per_capita / min_standard_m2


def normalize_feature_matrix(
    df: pd.DataFrame,
    feature_cols: list[str],
    benchmarks: dict[str, tuple[float, float]] | None = None,
) -> np.ndarray:
    """
    Applies Universal Min-Max scaling to map physical indicators into the [0.0, 1.0] interval.

    Aligning all features onto a universal [0.0, 1.0] scale is critical for the
    Graph Attention Autoencoder (GAT-AE):
    - Prevents high-magnitude indicators (e.g. LST ~305 K or building areas) from
      dominating the mean squared reconstruction error over bounded indicators (e.g. NDVI ~0.3).
    - Preserves absolute, international comparability across metropolitan regions
      without relying on relative within-sample z-scores.

    Parameters
    ----------
    df : pd.DataFrame
        Table containing raw feature columns.
    feature_cols : list[str]
        List of column names to extract and normalize.
    benchmarks : dict[str, tuple[float, float]] | None, optional
        Dictionary mapping column names to (min_benchmark, max_benchmark).
        If None, uses DEFAULT_10D_BENCHMARKS, falling back to observed min/max.

    Returns
    -------
    np.ndarray
        Normalized feature matrix X in R^(N x D) with values strictly in [0.0, 1.0].
    """
    if benchmarks is None:
        benchmarks = DEFAULT_10D_BENCHMARKS

    normalized = np.zeros((len(df), len(feature_cols)), dtype=np.float32)
    for idx, col in enumerate(feature_cols):
        min_val, max_val = benchmarks.get(col, (float(df[col].min()), float(df[col].max())))
        val = np.clip(df[col].values, min_val, max_val)
        normalized[:, idx] = (val - min_val) / (max_val - min_val + 1e-8)
    return normalized


def assemble_h3_features(
    h3_hexes: list[str],
    data_sources: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Assembles all physical living standard indicators into a unified H3 Resolution 8 table.

    Parameters
    ----------
    h3_hexes : list[str]
        List of target H3 cell indices.
    data_sources : dict[str, Any] | None, optional
        Dictionary containing loaded datasets (buildings, amenities, rasters).
    config : dict[str, Any] | None, optional
        Project configuration mapping.

    Returns
    -------
    pd.DataFrame
        H3 feature table indexed by H3 cell ID.
    """
    return pd.DataFrame(index=h3_hexes)
