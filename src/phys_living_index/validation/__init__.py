"""
Validation modules for the Physical Living Standard Index (PLSI) and GAT-AE:
Meta RWI 4-Quadrant divergence, Kementerian PUPR KOTAKU ground truth, and BPS macro audits.
"""

from .audit_bps import audit_bps_poverty_correlation, zonal_aggregate_bps
from .evaluate_rwi import (
    classify_4quadrant_divergence,
    correlate_with_rwi,
    extract_divergence_outliers,
    match_h3_to_rwi_grid,
    profile_quadrant_deficits,
)
from .run_validation import (
    generate_validation_latex_table,
    generate_validation_markdown_table,
    run_dual_validation,
)
from .validate_kotaku import (
    compute_h3_kotaku_spatial_overlap,
    evaluate_dki_severity_stratification,
    evaluate_kotaku_subdimension_concordance,
    evaluate_slum_binary_classification,
)

__all__ = [
    "audit_bps_poverty_correlation",
    "classify_4quadrant_divergence",
    "compute_h3_kotaku_spatial_overlap",
    "correlate_with_rwi",
    "evaluate_dki_severity_stratification",
    "evaluate_kotaku_subdimension_concordance",
    "evaluate_slum_binary_classification",
    "extract_divergence_outliers",
    "generate_validation_latex_table",
    "generate_validation_markdown_table",
    "match_h3_to_rwi_grid",
    "profile_quadrant_deficits",
    "run_dual_validation",
    "zonal_aggregate_bps",
]
