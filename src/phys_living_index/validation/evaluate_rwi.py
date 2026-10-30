"""
Continuous spatial concordance and 4-Quadrant Divergence Analysis against Meta's Relative Wealth Index (RWI).
"""

from typing import Any

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import pearsonr, spearmanr


def correlate_with_rwi(plsi_values: np.ndarray, rwi_values: np.ndarray) -> dict[str, float]:
    """
    Computes Pearson, Spearman rank correlation, and coefficient of determination (R^2)
    between unsupervised PLSI and Meta RWI.

    Args:
        plsi_values: Array of PLSI scores.
        rwi_values: Array of Meta RWI scores.

    Returns:
        Dictionary containing pearson_r, pearson_p, spearman_rho, spearman_p, r_squared, n_samples.
    """
    valid_mask = (
        ~np.isnan(plsi_values)
        & ~np.isnan(rwi_values)
        & ~np.isinf(plsi_values)
        & ~np.isinf(rwi_values)
    )
    n_samples = int(np.sum(valid_mask))
    if n_samples < 2:
        return {
            "pearson_r": float("nan"),
            "pearson_p": float("nan"),
            "spearman_rho": float("nan"),
            "spearman_p": float("nan"),
            "r_squared": float("nan"),
            "n_samples": n_samples,
        }

    x = plsi_values[valid_mask]
    y = rwi_values[valid_mask]

    # Guard against zero variance
    if np.isclose(np.std(x), 0) or np.isclose(np.std(y), 0):
        return {
            "pearson_r": 0.0,
            "pearson_p": 1.0,
            "spearman_rho": 0.0,
            "spearman_p": 1.0,
            "r_squared": 0.0,
            "n_samples": n_samples,
        }

    p_corr, p_pval = pearsonr(x, y)
    s_corr, s_pval = spearmanr(x, y)

    return {
        "pearson_r": float(p_corr),
        "pearson_p": float(p_pval),
        "spearman_rho": float(s_corr),
        "spearman_p": float(s_pval),
        "r_squared": float(p_corr**2),
        "n_samples": n_samples,
    }


def match_h3_to_rwi_grid(
    h3_df: pd.DataFrame,
    rwi_df: pd.DataFrame,
    h3_lat_col: str = "latitude",
    h3_lon_col: str = "longitude",
    rwi_lat_col: str = "latitude",
    rwi_lon_col: str = "longitude",
) -> pd.DataFrame:
    """
    Spatially matches H3 cell centroids to nearest Meta RWI 2.4 km grid points using a k-d tree.

    Args:
        h3_df: DataFrame containing H3 cells and coordinates.
        rwi_df: DataFrame containing RWI grid points, coordinates, and RWI values.
        h3_lat_col: Latitude column name in h3_df.
        h3_lon_col: Longitude column name in h3_df.
        rwi_lat_col: Latitude column name in rwi_df.
        rwi_lon_col: Longitude column name in rwi_df.

    Returns:
        DataFrame of h3_df enriched with matched RWI values and distance in km.
    """
    matched = h3_df.copy()

    # Approximate equirectangular projection to meters around Jakarta (~6° S)
    lat_rad = np.radians(h3_df[h3_lat_col].mean())
    cos_lat = np.cos(lat_rad)
    m_per_deg_lat = 111132.954
    m_per_deg_lon = 111132.954 * cos_lat

    rwi_coords_m = np.column_stack([
        rwi_df[rwi_lon_col] * m_per_deg_lon,
        rwi_df[rwi_lat_col] * m_per_deg_lat,
    ])
    h3_coords_m = np.column_stack([
        h3_df[h3_lon_col] * m_per_deg_lon,
        h3_df[h3_lat_col] * m_per_deg_lat,
    ])

    tree = cKDTree(rwi_coords_m)
    distances_m, indices = tree.query(h3_coords_m, k=1)

    matched["rwi"] = rwi_df["rwi"].iloc[indices].values
    if "error" in rwi_df.columns:
        matched["rwi_error"] = rwi_df["error"].iloc[indices].values
    matched["rwi_distance_km"] = distances_m / 1000.0

    return matched


def classify_4quadrant_divergence(
    matched_df: pd.DataFrame,
    rwi_col: str = "rwi",
    plsi_col: str = "plsi",
) -> pd.DataFrame:
    """
    Classifies matched cells into the 4-Quadrant Divergence framework based on standardized z-scores:
      - Quadrant I: z_RWI >= 0, z_PLSI >= 0 (Q1_Concordant_Affluent)
      - Quadrant II: z_RWI < 0, z_PLSI >= 0 (Q2_Rural_Well_Serviced)
      - Quadrant III: z_RWI >= 0, z_PLSI < 0 (Q3_Asset_Rich_Physically_Deprived - informal settlements)
      - Quadrant IV: z_RWI < 0, z_PLSI < 0 (Q4_Chronic_Deprivation)

    Args:
        matched_df: DataFrame containing RWI and PLSI values.
        rwi_col: Column name for Meta RWI.
        plsi_col: Column name for PLSI.

    Returns:
        DataFrame with z_rwi, z_plsi, divergence_z, and quadrant classification.
    """
    df = matched_df.copy()

    # Compute z-scores
    rwi_mean, rwi_std = df[rwi_col].mean(), df[rwi_col].std()
    plsi_mean, plsi_std = df[plsi_col].mean(), df[plsi_col].std()

    df["z_rwi"] = (df[rwi_col] - rwi_mean) / (rwi_std if rwi_std > 0 else 1.0)
    df["z_plsi"] = (df[plsi_col] - plsi_mean) / (plsi_std if plsi_std > 0 else 1.0)

    # Divergence metric: positive = higher asset wealth than physical living standards
    df["divergence_z"] = df["z_rwi"] - df["z_plsi"]

    conditions = [
        (df["z_rwi"] >= 0) & (df["z_plsi"] >= 0),
        (df["z_rwi"] < 0) & (df["z_plsi"] >= 0),
        (df["z_rwi"] >= 0) & (df["z_plsi"] < 0),
        (df["z_rwi"] < 0) & (df["z_plsi"] < 0),
    ]
    labels = [
        "Q1_Concordant_Affluent",
        "Q2_Rural_Well_Serviced",
        "Q3_Asset_Rich_Physically_Deprived",
        "Q4_Chronic_Deprivation",
    ]

    df["quadrant"] = np.select(conditions, labels, default="Unknown")
    return df


def profile_quadrant_deficits(
    matched_df: pd.DataFrame,
    feature_cols: list[str],
    quadrant_col: str = "quadrant",
) -> dict[str, Any]:
    """
    Decomposes physical indicator means across quadrants to identify specific deficits
    in Quadrant III (Asset-Rich, Physically Deprived) relative to Quadrant I.

    Args:
        matched_df: DataFrame containing quadrant assignments and raw/standardized features.
        feature_cols: List of indicator columns to profile.
        quadrant_col: Column name containing quadrant labels.

    Returns:
        Dictionary of mean, std, and Q1-vs-Q3 gap per feature.
    """
    profiles: dict[str, Any] = {}

    grouped = matched_df.groupby(quadrant_col)
    for q_name, group in grouped:
        profiles[str(q_name)] = {
            "count": int(len(group)),
            "features": {
                col: {
                    "mean": float(group[col].mean()),
                    "std": float(group[col].std()),
                }
                for col in feature_cols
                if col in group.columns
            },
        }

    # Specifically compute Q1 vs Q3 physical deficit
    if "Q1_Concordant_Affluent" in profiles and "Q3_Asset_Rich_Physically_Deprived" in profiles:
        q1_feats = profiles["Q1_Concordant_Affluent"]["features"]
        q3_feats = profiles["Q3_Asset_Rich_Physically_Deprived"]["features"]
        gap = {}
        for col in feature_cols:
            if col in q1_feats and col in q3_feats:
                gap[col] = {
                    "q1_mean": q1_feats[col]["mean"],
                    "q3_mean": q3_feats[col]["mean"],
                    "mean_diff": q1_feats[col]["mean"] - q3_feats[col]["mean"],
                }
        profiles["q1_q3_deficit"] = gap

    return profiles


def extract_divergence_outliers(
    matched_df: pd.DataFrame,
    threshold: float = 1.5,
    divergence_col: str = "divergence_z",
) -> pd.DataFrame:
    """
    Identifies extreme divergence outliers (|z_divergence| >= threshold).

    Args:
        matched_df: DataFrame with divergence_z scores.
        threshold: Absolute z-score divergence cutoff (default 1.5 sigma).
        divergence_col: Name of divergence column.

    Returns:
        DataFrame of sorted outlier cells.
    """
    outliers = matched_df[matched_df[divergence_col].abs() >= threshold].copy()
    return outliers.sort_values(by=divergence_col, ascending=False).reset_index(drop=True)
