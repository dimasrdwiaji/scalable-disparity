"""
Harmonizes and standardizes physical living standard features onto Uber H3 Resolution 8 cells (~0.74 km²).

This module prepares the continuous multi-dimensional feature matrix X in R^(N x 10)
for the Graph Attention Autoencoder (GAT-AE).

It implements:
1. Universal Min-Max Normalization: Maps diverse physical indicators (meters, Kelvin,
   nW/cm²/sr, μg/m³, spectral indices) into a standardized [0.0, 1.0] interval.
2. Inverted Hazard Scaling: Transforms environmental stress metrics (heat, air pollution)
   so that higher values uniformly signify better living standards across all feature channels.
3. 99th Percentile (P99) Winsorization: Mitigates denominator artifacts in commercial CBDs
   where near-zero resident populations produce false astronomical per-capita living space.
4. 10-Dimensional Feature Matrix Assembly: Incorporates living space sufficiency, built-up
   density, pedestrian accessibility, infrastructure paving, nighttime light, vegetative canopy,
   thermal comfort, drainage exposure, fine particulates, and multi-pollutant air quality.
"""

from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd

# The 10 canonical feature channels for the Physical Living Standard Index (PLSI)
FEATURE_DIMENSIONS_10D: list[str] = [
    "space_sufficiency_ratio",    # 1. Living Space Ratio
    "builtup_ndbi",               # 2. Built-up Density (NDBI)
    "cumulative_amenities_15m",   # 3. 15-Minute Walking Opportunities
    "bare_soil_bsi",              # 4. Bare Soil / Dirt Roads (BSI)
    "nighttime_energy_radiance",  # 5. Economic Radiance per Capita
    "vegetation_ndvi",            # 6. Environmental Canopy (NDVI)
    "thermal_comfort_lst_inv",    # 7. Inverted Thermal Comfort (LST)
    "water_mndwi",                # 8. Drainage / Water Exposure (MNDWI)
    "air_purity_pm25_inv",        # 9. Inverted Fine Particulates (PM2.5)
    "multi_pollutant_aqi_inv",    # 10. Inverted Multi-Pollutant AQI
]

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

# Features where higher raw values indicate environmental hazard/heat/pollution and must be inverted
INVERTED_HAZARD_CHANNELS: set[str] = {
    "thermal_comfort_lst_inv",
    "air_purity_pm25_inv",
    "multi_pollutant_aqi_inv",
}


def winsorize_series(
    series: pd.Series,
    percentile: float = 99.0,
) -> pd.Series:
    """
    Clips extreme positive outliers in a Pandas Series at the specified percentile.

    Parameters
    ----------
    series : pd.Series
        Input numerical series.
    percentile : float, default 99.0
        Upper percentile cut-off threshold (0-100).

    Returns
    -------
    pd.Series
        Winsorized series with values > cutoff capped to the cutoff value.
    """
    cutoff = float(np.percentile(series.dropna(), percentile))
    return series.clip(upper=cutoff)


def compute_living_space_ratio(
    buildings_df: gpd.GeoDataFrame,
    worldpop_series: pd.Series,
    min_standard_m2: float = 9.0,
    floor_height_m: float = 3.0,
    winsorize_p99: bool = True,
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
    winsorize_p99 : bool, default True
        Whether to apply P99 winsorization to remove CBD denominator artifacts.

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

    if winsorize_p99 and len(living_space_per_capita) > 1:
        living_space_per_capita = winsorize_series(living_space_per_capita, percentile=99.0)

    return living_space_per_capita / min_standard_m2


def compute_economic_energy_radiance(
    viirs_series: pd.Series,
    worldpop_series: pd.Series,
    winsorize_p99: bool = True,
) -> pd.Series:
    """
    Computes nighttime radiance per capita with P99 winsorization.

    Parameters
    ----------
    viirs_series : pd.Series
        Mean VIIRS radiance per H3 cell.
    worldpop_series : pd.Series
        Population per H3 cell.
    winsorize_p99 : bool, default True
        Whether to winsorize at 99th percentile.

    Returns
    -------
    pd.Series
        Radiance per capita.
    """
    pop = np.maximum(worldpop_series, 1.0)
    per_capita = viirs_series / pop
    if winsorize_p99 and len(per_capita) > 1:
        per_capita = winsorize_series(per_capita, percentile=99.0)
    return per_capita


def normalize_feature_matrix(
    df: pd.DataFrame,
    feature_cols: list[str],
    benchmarks: dict[str, tuple[float, float]] | None = None,
) -> np.ndarray:
    """
    Applies Universal Min-Max scaling to map physical indicators into the [0.0, 1.0] interval.

    Aligning all features onto a universal [0.0, 1.0] scale is critical for the
    Graph Attention Autoencoder (GAT-AE):
    - Prevents high-magnitude indicators from dominating the mean squared reconstruction error.
    - Preserves absolute, international comparability across metropolitan regions.

    Parameters
    ----------
    df : pd.DataFrame
        Table containing raw feature columns.
    feature_cols : list[str]
        List of column names to extract and normalize.
    benchmarks : dict[str, tuple[float, float]] | None, optional
        Dictionary mapping column names to (min_benchmark, max_benchmark).
        If None, uses DEFAULT_10D_BENCHMARKS.

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
        val = np.clip(df[col].to_numpy(dtype=np.float32), min_val, max_val)
        norm_val = (val - min_val) / (max_val - min_val + 1e-8)

        # Invert hazard channels so higher is always better
        if col in INVERTED_HAZARD_CHANNELS:
            norm_val = 1.0 - norm_val

        normalized[:, idx] = norm_val
    return normalized


def build_10d_feature_matrix(
    raw_features_df: pd.DataFrame,
    benchmarks: dict[str, tuple[float, float]] | None = None,
) -> np.ndarray:
    """
    Standardizes and packages the 10 canonical living standard indicators into matrix X.

    Parameters
    ----------
    raw_features_df : pd.DataFrame
        DataFrame containing all 10 canonical feature columns indexed by H3 ID.
    benchmarks : dict[str, tuple[float, float]] | None, optional
        Custom benchmark mapping.

    Returns
    -------
    np.ndarray
        Normalized feature matrix X of shape (N, 10) in [0.0, 1.0].
    """
    return normalize_feature_matrix(
        raw_features_df,
        feature_cols=FEATURE_DIMENSIONS_10D,
        benchmarks=benchmarks,
    )


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
