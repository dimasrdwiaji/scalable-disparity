import pytest
import numpy as np
import pandas as pd
from phys_living_index.features.build_features import normalize_feature_matrix
from phys_living_index.analysis.disparity_metrics import compute_gini_coefficient, compute_palma_ratio


def test_normalize_feature_matrix_bounds():
    df = pd.DataFrame({
        "feat1": [1.0, 5.0, 10.0],
        "feat2": [-5.0, 0.0, 5.0],
    })
    benchmarks = {
        "feat1": (0.0, 10.0),
        "feat2": (-10.0, 10.0),
    }
    norm = normalize_feature_matrix(df, ["feat1", "feat2"], benchmarks)
    assert norm.shape == (3, 2)
    assert np.all(norm >= 0.0)
    assert np.all(norm <= 1.0)
    assert norm[0, 0] == pytest.approx(0.1)
    assert norm[2, 0] == pytest.approx(1.0)


def test_gini_coefficient_edge_cases():
    # Perfect equality
    equal_vals = np.ones(100)
    assert compute_gini_coefficient(equal_vals) == pytest.approx(0.0, abs=1e-3)
    
    # Skewed distribution
    unequal_vals = np.zeros(100)
    unequal_vals[-1] = 1000.0
    assert compute_gini_coefficient(unequal_vals) > 0.95


def test_palma_ratio():
    vals = np.linspace(1, 100, 100)
    palma = compute_palma_ratio(vals)
    assert palma > 0.0
    assert not np.isnan(palma)
