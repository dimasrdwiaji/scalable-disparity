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


def compute_focal_disparity_surface(
    h3_hexes: list[str],
    values: np.ndarray,
    k_ring: int = 3,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Computes local focal Gini coefficient and Spatial Palma Ratio within a k-ring
    neighborhood on the H3 grid (e.g. k=3 is ~3.5 km).

    Parameters
    ----------
    h3_hexes : list[str]
        List of target H3 hex index strings.
    values : np.ndarray
        Array of feature or PLSI values of shape (N,).
    k_ring : int, default 3
        Neighborhood radius in H3 cells.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        - focal_gini: Array of local Gini scores (N,).
        - focal_palma: Array of local Palma ratios (N,).
    """
    import h3

    hex_to_idx = {h: i for i, h in enumerate(h3_hexes)}
    n = len(h3_hexes)
    focal_gini = np.zeros(n, dtype=np.float32)
    focal_palma = np.zeros(n, dtype=np.float32)

    for i, hex_id in enumerate(h3_hexes):
        neighbors = h3.grid_disk(hex_id, k_ring)
        valid_indices = [hex_to_idx[nbr] for nbr in neighbors if nbr in hex_to_idx]
        if len(valid_indices) > 2:
            local_vals = values[valid_indices]
            focal_gini[i] = compute_gini_coefficient(local_vals)
            focal_palma[i] = compute_palma_ratio(local_vals)
        else:
            focal_gini[i] = 0.0
            focal_palma[i] = 0.0

    return focal_gini, focal_palma


def compute_bivariate_local_moran(
    x: np.ndarray,
    y: np.ndarray,
    edge_index: np.ndarray,
    permutations: int = 999,
    seed: int = 42,
) -> dict[str, np.ndarray]:
    """
    Computes Bivariate Local Moran's I (LISA) as a classical linear spatial baseline (REV-4).

    Identifies High-Low and Low-High spatial outlier boundaries between variable x and y.

    Parameters
    ----------
    x : np.ndarray
        Focal variable array of shape (N,).
    y : np.ndarray
        Neighbor context variable array of shape (N,).
    edge_index : np.ndarray
        Directed graph adjacency edges of shape (2, E).
    permutations : int, default 999
        Number of conditional permutations for pseudo p-values.
    seed : int, default 42
        Random seed for permutations.

    Returns
    -------
    dict[str, np.ndarray]
        - Is: Local Moran statistics (N,).
        - q: Quadrant category (1: HH, 2: LH, 3: LL, 4: HL).
        - p_sim: Empirical pseudo p-values (N,).
        - is_outlier: Boolean mask identifying HL and LH segregation border cells (p < 0.05).
    """
    from esda.moran import Moran_Local_BV
    from libpysal.weights import W

    n = len(x)
    # Build libpysal adjacency dictionary from edge_index
    neighbors: dict[int, list[int]] = {i: [] for i in range(n)}
    src, dst = edge_index[0], edge_index[1]
    for u, v in zip(src, dst):
        neighbors[int(u)].append(int(v))

    # Ensure every node has at least one neighbor for W creation
    for i in range(n):
        if not neighbors[i]:
            neighbors[i] = [i]

    w = W(neighbors)
    w.transform = "R"

    lm_bv = Moran_Local_BV(x, y, w, transformation="r", permutations=permutations, seed=seed)

    # Quadrant 2: Low-High (under-served next to affluent)
    # Quadrant 4: High-Low (affluent next to under-served)
    is_outlier = (lm_bv.p_sim < 0.05) & ((lm_bv.q == 2) | (lm_bv.q == 4))

    return {
        "Is": lm_bv.Is,
        "q": lm_bv.q,
        "p_sim": lm_bv.p_sim,
        "is_outlier": is_outlier,
    }
