"""
Population-weighted zonal aggregation into BPS administrative units and econometric audit against SUSENAS poverty rates.
"""

import numpy as np
import pandas as pd
from scipy.stats import pearsonr


def zonal_aggregate_bps(
    h3_df: pd.DataFrame,
    bps_poly_col: str = "kabupaten_kota",
    plsi_col: str = "plsi",
    pop_col: str = "population",
) -> pd.DataFrame:
    """
    Computes population-weighted mean PLSI and internal spatial Gini per BPS administrative boundary:
    Mean_PLSI_k = sum(PLSI_i * Pop_i) / sum(Pop_i)
    """

    def _pop_weighted_mean(group):
        weights = group[pop_col]
        values = group[plsi_col]
        total_w = weights.sum()
        if total_w == 0:
            return np.nan
        return (values * weights).sum() / total_w

    aggregated = h3_df.groupby(bps_poly_col).apply(_pop_weighted_mean).reset_index()
    aggregated.columns = [bps_poly_col, "mean_plsi"]
    return aggregated


def audit_bps_poverty_correlation(
    aggregated_bps_df: pd.DataFrame,
    bps_poverty_rate_col: str = "poverty_rate_pct",
) -> dict[str, float]:
    """
    Audits the aggregated physical index against official BPS SUSENAS poverty statistics:
    Poverty_Rate_k = beta_0 + beta_1 * Mean_PLSI_k + epsilon
    """
    valid = aggregated_bps_df.dropna(subset=["mean_plsi", bps_poverty_rate_col])
    r, p = pearsonr(valid["mean_plsi"], valid[bps_poverty_rate_col])
    return {
        "poverty_correlation_r": float(r),
        "p_value": float(p),
        "n_units": len(valid),
    }
