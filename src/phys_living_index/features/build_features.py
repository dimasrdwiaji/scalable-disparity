"""
Harmonizes and standardizes all 6 features onto Uber H3 Resolution 8 cells (~0.74 km²).
"""

from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
import geopandas as gpd
import h3


def compute_living_space_ratio(
    buildings_df: gpd.GeoDataFrame,
    worldpop_series: pd.Series,
    min_standard_m2: float = 9.0,
    floor_height_m: float = 3.0,
) -> pd.Series:
    """
    Computes Living Space Ratio:
    R_space = (Observed Residential Area per Capita) / 9.0 m²
    """
    floors = np.maximum(1, np.floor(buildings_df["height"] / floor_height_m))
    total_floor_area = buildings_df.geometry.area * floors
    buildings_df["floor_area"] = total_floor_area
    
    # Aggregate by H3 index
    h3_floor_area = buildings_df.groupby("h3_index")["floor_area"].sum()
    pop = np.maximum(worldpop_series, 1.0)
    living_space_per_capita = h3_floor_area / pop
    return living_space_per_capita / min_standard_m2


def normalize_feature_matrix(
    df: pd.DataFrame,
    feature_cols: list[str],
    benchmarks: Dict[str, Tuple[float, float]],
) -> np.ndarray:
    """
    Universal Min-Max scaling to [0, 1] aligned with international standards.
    """
    normalized = np.zeros((len(df), len(feature_cols)), dtype=np.float32)
    for idx, col in enumerate(feature_cols):
        min_val, max_val = benchmarks.get(col, (df[col].min(), df[col].max()))
        val = np.clip(df[col].values, min_val, max_val)
        normalized[:, idx] = (val - min_val) / (max_val - min_val + 1e-8)
    return normalized


def assemble_h3_features(
    h3_hexes: list[str],
    data_sources: Dict[str, Any],
    config: Dict[str, Any],
) -> pd.DataFrame:
    """Assembles all 6 dimensions into a single H3 Resolution 8 table."""
    return pd.DataFrame(index=h3_hexes)
