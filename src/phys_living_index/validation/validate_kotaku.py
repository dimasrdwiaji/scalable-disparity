"""
Micro-scale ground-truth empirical validation engine benchmarking against the
official Kementerian PUPR SIM-KOTAKU national informal settlement registry.
"""

from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.stats import f_oneway, kruskal, pearsonr, spearmanr
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)


def compute_h3_kotaku_spatial_overlap(
    h3_gdf: gpd.GeoDataFrame,
    kotaku_gdf: gpd.GeoDataFrame,
    overlap_threshold: float = 0.10,
    h3_id_col: str = "h3_index",
) -> gpd.GeoDataFrame:
    """
    Computes spatial polygon intersection between H3 hexagonal cells and KOTAKU
    informal settlement polygons.

    Args:
        h3_gdf: GeoDataFrame containing H3 discrete grid polygons.
        kotaku_gdf: GeoDataFrame containing gazetted informal settlement polygons.
        overlap_threshold: Minimum area overlap fraction [0.0, 1.0] to flag as slum (default 10%).
        h3_id_col: Name of unique H3 identifier column.

    Returns:
        GeoDataFrame of h3_gdf with overlap_pct, is_slum, and propagated ground-truth attributes.
    """
    # Ensure matching CRS
    if h3_gdf.crs != kotaku_gdf.crs:
        kotaku_aligned = kotaku_gdf.to_crs(h3_gdf.crs)
    else:
        kotaku_aligned = kotaku_gdf

    result = h3_gdf.copy()
    result["h3_area"] = result.geometry.area
    result["overlap_area"] = 0.0
    result["overlap_pct"] = 0.0
    result["is_slum"] = 0

    # Project to planar metric coordinate system for accurate area calculations if geographic
    if result.crs.is_geographic:
        # UTM zone 48S (EPSG:32748) covers Western Java (Jakarta, Bodetabek, Karawang)
        h3_proj = result.to_crs(epsg=32748)
        kotaku_proj = kotaku_aligned.to_crs(epsg=32748)
    else:
        h3_proj = result
        kotaku_proj = kotaku_aligned

    h3_proj_areas = h3_proj.geometry.area

    # Spatial intersection
    intersection = gpd.overlay(
        h3_proj[[h3_id_col, "geometry"]],
        kotaku_proj,
        how="intersection",
        keep_geom_type=False,
    )

    if len(intersection) > 0:
        intersection["inter_area"] = intersection.geometry.area

        # Aggregate intersection area per H3 cell
        grouped_area = intersection.groupby(h3_id_col)["inter_area"].sum()
        for h3_id, area in grouped_area.items():
            idx = result[result[h3_id_col] == h3_id].index
            if len(idx) > 0:
                h3_total_area = h3_proj_areas.loc[idx[0]]
                frac = float(area / h3_total_area) if h3_total_area > 0 else 0.0
                result.loc[idx, "overlap_area"] = float(area)
                result.loc[idx, "overlap_pct"] = min(1.0, frac)

        # Propagate categorical and numeric attributes from KOTAKU
        # For each cell, pick the dominant overlapping polygon's attributes
        sorted_inter = intersection.sort_values(by="inter_area", ascending=False)
        dominant = sorted_inter.drop_duplicates(subset=[h3_id_col])

        prop_cols = [c for c in dominant.columns if c not in [h3_id_col, "geometry", "inter_area"]]
        for col in prop_cols:
            if col not in result.columns:
                result[col] = np.nan
            mapping = dominant.set_index(h3_id_col)[col]
            result[col] = result[h3_id_col].map(mapping).combine_first(result[col])

    result["is_slum"] = (result["overlap_pct"] >= overlap_threshold).astype(int)
    result = result.drop(columns=["h3_area"], errors="ignore")
    return result


def evaluate_slum_binary_classification(
    score_values: np.ndarray,
    ground_truth_labels: np.ndarray,
    invert_score: bool = True,
) -> dict[str, Any]:
    """
    Evaluates continuous index scores against binary ground-truth slum labels.

    Args:
        score_values: Continuous predicted score array (e.g. PLSI).
        ground_truth_labels: Binary array (1 = slum, 0 = non-slum).
        invert_score: If True, inverts the score (-score) so higher values indicate
                      higher probability of being a slum (deprived area).

    Returns:
        Dictionary containing roc_auc, pr_auc, optimal_f1, optimal_threshold,
        precision, recall, specificity, confusion_matrix, and sample counts.
    """
    scores = np.asarray(score_values, dtype=float)
    y_true = np.asarray(ground_truth_labels, dtype=int)

    valid_mask = ~np.isnan(scores) & ~np.isnan(y_true)
    scores = scores[valid_mask]
    y_true = y_true[valid_mask]

    n_pos = int(np.sum(y_true == 1))
    n_neg = int(np.sum(y_true == 0))

    if n_pos == 0 or n_neg == 0:
        return {
            "roc_auc": float("nan"),
            "pr_auc": float("nan"),
            "optimal_f1": float("nan"),
            "optimal_threshold": float("nan"),
            "n_positives": n_pos,
            "n_negatives": n_neg,
        }

    # If inverting (e.g. PLSI where lower = worse), map to [0, 1] deficit
    if invert_score:
        max_v = np.max(scores)
        min_v = np.min(scores)
        pred_probs = (max_v - scores) / (max_v - min_v) if max_v > min_v else np.zeros_like(scores)
    else:
        pred_probs = scores

    roc_auc = float(roc_auc_score(y_true, pred_probs))
    pr_auc = float(average_precision_score(y_true, pred_probs))

    fpr, tpr, roc_thresholds = roc_curve(y_true, pred_probs)
    precisions, recalls, pr_thresholds = precision_recall_curve(y_true, pred_probs)

    # Find optimal threshold by F1-score
    denom = precisions + recalls
    f1_scores = np.where(denom > 0, 2 * (precisions * recalls) / denom, 0.0)
    best_idx = int(np.argmax(f1_scores))
    optimal_f1 = float(f1_scores[best_idx])
    optimal_thresh = float(pr_thresholds[best_idx]) if best_idx < len(pr_thresholds) else 0.5

    # Binary confusion matrix at optimal threshold
    y_pred = (pred_probs >= optimal_thresh).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    sensitivity = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0

    return {
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "optimal_f1": optimal_f1,
        "optimal_threshold": optimal_thresh,
        "precision": precision,
        "recall": sensitivity,
        "specificity": specificity,
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
        "n_positives": n_pos,
        "n_negatives": n_neg,
    }


def evaluate_dki_severity_stratification(
    h3_df: pd.DataFrame,
    plsi_col: str = "plsi",
    severity_col: str = "KAT_TEXT",
) -> dict[str, Any]:
    """
    Evaluates whether continuous PLSI scores monotonically and statistically
    differentiate the official 4 severity tiers in DKI Jakarta (Pergub 90/2018).

    Official Tier Order: Berat < Sedang < Ringan < Sangat Ringan.
    """
    valid = h3_df.dropna(subset=[plsi_col, severity_col]).copy()

    ordered_tiers = ["Berat", "Sedang", "Ringan", "Sangat Ringan"]
    present_tiers = [t for t in ordered_tiers if t in valid[severity_col].values]

    tier_groups = [valid[valid[severity_col] == t][plsi_col].values for t in present_tiers]

    if len(tier_groups) < 2:
        return {
            "anova_f": float("nan"),
            "anova_p": float("nan"),
            "kruskal_h": float("nan"),
            "kruskal_p": float("nan"),
            "is_monotonic_decreasing": False,
            "tier_stats": {},
        }

    f_stat, f_p = f_oneway(*tier_groups)
    k_stat, k_p = kruskal(*tier_groups)

    tier_stats = {}
    tier_means = []
    for t in present_tiers:
        vals = valid[valid[severity_col] == t][plsi_col].values
        m = float(np.mean(vals))
        tier_means.append(m)
        tier_stats[t] = {
            "count": int(len(vals)),
            "mean": m,
            "std": float(np.std(vals)),
            "median": float(np.median(vals)),
        }

    # Monotonicity check: Berat < Sedang < Ringan < Sangat Ringan
    is_monotonic = all(tier_means[i] <= tier_means[i + 1] for i in range(len(tier_means) - 1))

    return {
        "anova_f": float(f_stat),
        "anova_p": float(f_p),
        "kruskal_h": float(k_stat),
        "kruskal_p": float(k_p),
        "is_monotonic_decreasing": is_monotonic,
        "tier_stats": tier_stats,
    }


def evaluate_kotaku_subdimension_concordance(
    h3_df: pd.DataFrame,
    pairs: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """
    Evaluates bivariate correlation between continuous 10D sub-dimensions and
    KOTAKU statutory physical defect percentages (Karawang active sub-parameters).

    Args:
        h3_df: DataFrame containing H3 features and overlapped KOTAKU defect columns.
        pairs: List of (feature_col, kotaku_param_col) tuples.
               Defaults to standard physical pairings:
               - ('r_space', 'k1_a_p'): Living space ratio vs. irregular building layout
               - ('a_amenity', 'k2_b_p'): Pedestrian walkability vs. damaged road surface
               - ('z_elev', 'k4_d_p'): Elevation proxy vs. clogged drainage channels
               - ('a_amenity', 'k3_a_p'): Service access vs. unsafe drinking water

    Returns:
        Dictionary of correlation results for each pair.
    """
    if pairs is None:
        pairs = [
            ("r_space", "k1_a_p"),
            ("a_amenity", "k2_b_p"),
            ("z_elev", "k4_d_p"),
            ("a_amenity", "k3_a_p"),
        ]

    concordance: dict[str, Any] = {}
    for feat_col, param_col in pairs:
        pair_key = f"{feat_col}_vs_{param_col}"
        if feat_col not in h3_df.columns or param_col not in h3_df.columns:
            continue

        valid = h3_df.dropna(subset=[feat_col, param_col])
        # Filter out cases where param was unrecorded / 0
        valid = valid[valid[param_col] > 0]
        n_obs = len(valid)

        if n_obs < 3:
            concordance[pair_key] = {
                "pearson_r": float("nan"),
                "pearson_p": float("nan"),
                "spearman_rho": float("nan"),
                "spearman_p": float("nan"),
                "n_samples": n_obs,
            }
            continue

        x = valid[feat_col].values
        y = valid[param_col].values

        if np.isclose(np.std(x), 0) or np.isclose(np.std(y), 0):
            concordance[pair_key] = {
                "pearson_r": 0.0,
                "pearson_p": 1.0,
                "spearman_rho": 0.0,
                "spearman_p": 1.0,
                "n_samples": n_obs,
            }
            continue

        p_r, p_p = pearsonr(x, y)
        s_rho, s_p = spearmanr(x, y)

        concordance[pair_key] = {
            "pearson_r": float(p_r),
            "pearson_p": float(p_p),
            "spearman_rho": float(s_rho),
            "spearman_p": float(s_p),
            "n_samples": n_obs,
        }

    return concordance
