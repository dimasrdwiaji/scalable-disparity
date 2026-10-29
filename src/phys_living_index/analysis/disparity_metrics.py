"""
Disparity metrics: Population-weighted Spatial Gini and Spatial Palma Ratio.

This module provides macroscopic inequality metrics computed directly over the continuous
Physical Living Standard Index (PLSI) distribution:
1. Population-Weighted Spatial Gini:
   Measures global inequality across metropolitan grid cells, weighted by WorldPop population
   to prevent unpopulated rural cells from skewing the urban distribution.
   Computed via trapezoidal integration of the cumulative Lorenz curve.
2. Spatial Palma Ratio:
   Measures extreme inequality as the ratio of living standard capital held by the richest 10%
   of the population to that held by the poorest 40%. The Palma ratio is widely favored over
   Gini in policy analysis because middle-income shares remain relatively stable across cities,
   isolating divergence at the distribution extremes.
"""

import numpy as np


def compute_gini_coefficient(
    values: np.ndarray,
    weights: np.ndarray | None = None,
) -> float:
    """
    Computes the population-weighted Gini coefficient across spatial units.

    Formula:
        G = 1 - 2 * integral_0^1 L(p) dp
    where L(p) is the cumulative Lorenz curve of living standard capital against
    cumulative population proportion p.

    Compatible with NumPy 2.0+ (np.trapezoid) with fallback to np.trapz for legacy environments.

    Parameters
    ----------
    values : np.ndarray
        Array of living standard index scores per spatial cell.
    weights : np.ndarray | None, optional
        Population weights per cell. If None, equal unit weights are assumed.

    Returns
    -------
    float
        Population-weighted Gini coefficient bounded in [0.0, 1.0].
        0.0 represents perfect spatial equality; 1.0 represents total disparity.
    """
    if weights is None:
        weights = np.ones_like(values)

    sorted_indices = np.argsort(values)
    sorted_values = values[sorted_indices]
    sorted_weights = weights[sorted_indices]

    cumulative_weights = np.cumsum(sorted_weights)
    total_weight = cumulative_weights[-1]

    cumulative_wealth = np.cumsum(sorted_values * sorted_weights)
    total_wealth = cumulative_wealth[-1]

    if total_wealth == 0 or total_weight == 0:
        return 0.0

    relative_pop = cumulative_weights / total_weight
    relative_wealth = cumulative_wealth / total_wealth

    # Area under the Lorenz curve via trapezoidal numerical integration
    if hasattr(np, "trapezoid"):
        lorenz_area = np.trapezoid(relative_wealth, relative_pop)
    else:
        lorenz_area = np.trapz(relative_wealth, relative_pop)  # noqa: NPY201

    gini = 1.0 - 2.0 * lorenz_area
    return float(np.clip(gini, 0.0, 1.0))


def compute_palma_ratio(
    values: np.ndarray,
    weights: np.ndarray | None = None,
) -> float:
    """
    Computes the Spatial Palma Ratio.

    Formula:
        Palma = (Share of living standard capital held by top 10% of population) /
                (Share of living standard capital held by bottom 40% of population)

    Parameters
    ----------
    values : np.ndarray
        Array of living standard index scores per spatial cell.
    weights : np.ndarray | None, optional
        Population weights per cell. If None, equal unit weights are assumed.

    Returns
    -------
    float
        Palma ratio. Values > 1.0 indicate the top decile commands more physical living
        standard capital than the bottom 4 deciles combined.
    """
    if weights is None:
        weights = np.ones_like(values)

    sorted_indices = np.argsort(values)
    sorted_values = values[sorted_indices]
    sorted_weights = weights[sorted_indices]

    total_pop = np.sum(sorted_weights)
    if total_pop == 0:
        return 0.0

    cum_pop = np.cumsum(sorted_weights) / total_pop

    bottom_40_mask = cum_pop <= 0.40
    top_10_mask = cum_pop > 0.90

    bottom_40_total = np.sum(sorted_values[bottom_40_mask] * sorted_weights[bottom_40_mask])
    top_10_total = np.sum(sorted_values[top_10_mask] * sorted_weights[top_10_mask])

    if bottom_40_total <= 0:
        return float("inf") if top_10_total > 0 else 0.0

    return float(top_10_total / bottom_40_total)
