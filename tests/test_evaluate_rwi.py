"""
Unit tests for Meta RWI spatial concordance and 4-Quadrant Divergence Analysis.
"""

import numpy as np
import pandas as pd
import pytest

from phys_living_index.validation.evaluate_rwi import (
    classify_4quadrant_divergence,
    correlate_with_rwi,
    extract_divergence_outliers,
    match_h3_to_rwi_grid,
    profile_quadrant_deficits,
)


@pytest.fixture
def mock_rwi_and_h3_data():
    rng = np.random.default_rng(42)
    n_h3 = 100
    n_rwi = 25

    # Mock RWI grid (coarse 2.4km points)
    rwi_lats = np.linspace(-6.3, -6.1, 5)
    rwi_lons = np.linspace(106.7, 106.9, 5)
    grid_lats, grid_lons = np.meshgrid(rwi_lats, rwi_lons)
    rwi_df = pd.DataFrame(
        {
            "latitude": grid_lats.ravel(),
            "longitude": grid_lons.ravel(),
            "rwi": rng.normal(0.2, 0.8, size=n_rwi),
            "error": rng.uniform(0.1, 0.3, size=n_rwi),
        }
    )

    # Mock H3 data (finer centroids)
    h3_df = pd.DataFrame(
        {
            "h3_index": [f"886546{i:04d}" for i in range(n_h3)],
            "latitude": rng.uniform(-6.3, -6.1, size=n_h3),
            "longitude": rng.uniform(106.7, 106.9, size=n_h3),
            "plsi": rng.uniform(0.1, 0.9, size=n_h3),
            "r_space": rng.uniform(0.2, 1.5, size=n_h3),
            "a_amenity": rng.uniform(0.1, 0.8, size=n_h3),
            "lst_inv": rng.uniform(0.3, 0.9, size=n_h3),
        }
    )

    return h3_df, rwi_df


def test_correlate_with_rwi():
    # Perfectly correlated
    x = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
    y = np.array([1.0, 3.0, 5.0, 7.0, 9.0])
    res = correlate_with_rwi(x, y)
    assert pytest.approx(res["pearson_r"], 1e-4) == 1.0
    assert pytest.approx(res["spearman_rho"], 1e-4) == 1.0
    assert pytest.approx(res["r_squared"], 1e-4) == 1.0
    assert res["n_samples"] == 5

    # Anti-correlated
    res_neg = correlate_with_rwi(x, -y)
    assert pytest.approx(res_neg["pearson_r"], 1e-4) == -1.0
    assert pytest.approx(res_neg["spearman_rho"], 1e-4) == -1.0

    # Handles NaN values
    x_nan = np.array([0.1, np.nan, 0.5, 0.7, 0.9])
    res_nan = correlate_with_rwi(x_nan, y)
    assert res_nan["n_samples"] == 4


def test_match_h3_to_rwi_grid(mock_rwi_and_h3_data):
    h3_df, rwi_df = mock_rwi_and_h3_data
    matched = match_h3_to_rwi_grid(h3_df, rwi_df)

    assert len(matched) == len(h3_df)
    assert "rwi" in matched.columns
    assert "rwi_distance_km" in matched.columns
    # Check that nearest points are reasonably close (<= 10km within bbox)
    assert (matched["rwi_distance_km"] < 10.0).all()


def test_classify_4quadrant_divergence():
    df = pd.DataFrame(
        {
            "plsi": [0.9, 0.8, 0.2, 0.1],  # 2 high, 2 low
            "rwi": [1.5, -0.5, 1.2, -1.0],  # high, low, high, low
        }
    )
    classified = classify_4quadrant_divergence(df, rwi_col="rwi", plsi_col="plsi")

    assert "quadrant" in classified.columns
    assert "z_rwi" in classified.columns
    assert "z_plsi" in classified.columns
    assert "divergence_z" in classified.columns

    # High RWI, High PLSI -> Q1
    # Low RWI, High PLSI -> Q2
    # High RWI, Low PLSI -> Q3
    # Low RWI, Low PLSI -> Q4
    assert classified.loc[0, "quadrant"] == "Q1_Concordant_Affluent"
    assert classified.loc[1, "quadrant"] == "Q2_Rural_Well_Serviced"
    assert classified.loc[2, "quadrant"] == "Q3_Asset_Rich_Physically_Deprived"
    assert classified.loc[3, "quadrant"] == "Q4_Chronic_Deprivation"


def test_profile_quadrant_deficits():
    df = pd.DataFrame(
        {
            "quadrant": [
                "Q1_Concordant_Affluent",
                "Q1_Concordant_Affluent",
                "Q3_Asset_Rich_Physically_Deprived",
                "Q3_Asset_Rich_Physically_Deprived",
            ],
            "r_space": [1.5, 1.3, 0.3, 0.4],
            "lst_inv": [0.8, 0.9, 0.3, 0.4],
        }
    )
    profiles = profile_quadrant_deficits(df, feature_cols=["r_space", "lst_inv"])

    assert "Q1_Concordant_Affluent" in profiles
    assert "Q3_Asset_Rich_Physically_Deprived" in profiles
    assert "q1_q3_deficit" in profiles
    assert profiles["q1_q3_deficit"]["r_space"]["mean_diff"] > 0


def test_extract_divergence_outliers():
    df = pd.DataFrame(
        {
            "h3_index": ["hex1", "hex2", "hex3"],
            "divergence_z": [2.5, -0.2, -2.1],
            "quadrant": [
                "Q3_Asset_Rich_Physically_Deprived",
                "Q1_Concordant_Affluent",
                "Q2_Rural_Well_Serviced",
            ],
        }
    )
    outliers = extract_divergence_outliers(df, threshold=1.5)
    assert len(outliers) == 2
    assert "hex1" in outliers["h3_index"].values
    assert "hex3" in outliers["h3_index"].values
