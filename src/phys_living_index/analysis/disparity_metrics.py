"""
Disparity metrics: Population-weighted Spatial Gini, Spatial Palma Ratio, and Local Moran's I.
"""

import numpy as np


def compute_gini_coefficient(values: np.ndarray, weights: np.ndarray = None) -> float:
    """
    Computes the population-weighted Gini coefficient.
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
    
    if total_wealth == 0:
        return 0.0
        
    relative_pop = cumulative_weights / total_weight
    relative_wealth = cumulative_wealth / total_wealth
    
    # Area under the Lorenz curve (trapezoidal integration)
    if hasattr(np, "trapezoid"):
        lorenz_area = np.trapezoid(relative_wealth, relative_pop)
    else:
        lorenz_area = np.trapz(relative_wealth, relative_pop)
    gini = 1.0 - 2.0 * lorenz_area
    return float(np.clip(gini, 0.0, 1.0))


def compute_palma_ratio(values: np.ndarray, weights: np.ndarray = None) -> float:
    """
    Computes the Spatial Palma Ratio:
    Share of total living standard held by top 10% / share held by bottom 40%.
    """
    if weights is None:
        weights = np.ones_like(values)
        
    sorted_indices = np.argsort(values)
    sorted_values = values[sorted_indices]
    sorted_weights = weights[sorted_indices]
    
    total_pop = np.sum(sorted_weights)
    cum_pop = np.cumsum(sorted_weights) / total_pop
    
    bottom_40_mask = cum_pop <= 0.40
    top_10_mask = cum_pop > 0.90
    
    bottom_40_total = np.sum(sorted_values[bottom_40_mask] * sorted_weights[bottom_40_mask])
    top_10_total = np.sum(sorted_values[top_10_mask] * sorted_weights[top_10_mask])
    
    if bottom_40_total == 0:
        return float("nan")
        
    return float(top_10_total / bottom_40_total)
