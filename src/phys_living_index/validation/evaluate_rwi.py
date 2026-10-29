"""
Evaluate pixel-to-pixel spatial concordance against Meta's Relative Wealth Index (RWI).
"""

import numpy as np
from scipy.stats import pearsonr, spearmanr


def correlate_with_rwi(plsi_values: np.ndarray, rwi_values: np.ndarray) -> dict[str, float]:
    """
    Computes Pearson and Spearman rank correlation between unsupervised PLSI and Meta RWI.
    """
    valid_mask = ~np.isnan(plsi_values) & ~np.isnan(rwi_values)
    p_corr, p_pval = pearsonr(plsi_values[valid_mask], rwi_values[valid_mask])
    s_corr, s_pval = spearmanr(plsi_values[valid_mask], rwi_values[valid_mask])
    
    return {
        "pearson_r": float(p_corr),
        "pearson_p": float(p_pval),
        "spearman_rho": float(s_corr),
        "spearman_p": float(s_pval),
        "n_samples": int(np.sum(valid_mask)),
    }
