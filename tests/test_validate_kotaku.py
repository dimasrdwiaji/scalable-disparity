"""
Unit tests for Kementerian PUPR KOTAKU micro-scale ground-truth validation engine.
"""

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Polygon

from phys_living_index.validation.validate_kotaku import (
    compute_h3_kotaku_spatial_overlap,
    evaluate_dki_severity_stratification,
    evaluate_kotaku_subdimension_concordance,
    evaluate_slum_binary_classification,
)


@pytest.fixture
def mock_spatial_data():
    # Create two adjacent synthetic H3 grid cells
    poly1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
    poly2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1), (1, 0)])

    h3_gdf = gpd.GeoDataFrame({
        "h3_index": ["hex1", "hex2"],
        "plsi": [0.25, 0.85],
        "r_space": [0.3, 1.2],
        "a_amenity": [0.2, 0.9],
        "z_elev": [0.1, 0.8],
        "geometry": [poly1, poly2],
    }, crs="EPSG:4326")

    # Create a slum polygon overlapping heavily with hex1 (area 0.5 in hex1, 0.0 in hex2)
    slum_poly = Polygon([(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8), (0.2, 0.2)])
    kotaku_gdf = gpd.GeoDataFrame({
        "id": ["slum_1"],
        "KAT_TEXT": ["Sedang"],
        "KAT_NUM": [3],
        "k1_a_p": [65.0],
        "k2_b_p": [40.0],
        "k4_d_p": [80.0],
        "k3_a_p": [50.0],
        "geometry": [slum_poly],
    }, crs="EPSG:4326")

    return h3_gdf, kotaku_gdf


def test_compute_h3_kotaku_spatial_overlap(mock_spatial_data):
    h3_gdf, kotaku_gdf = mock_spatial_data
    overlapped = compute_h3_kotaku_spatial_overlap(h3_gdf, kotaku_gdf, overlap_threshold=0.10)

    assert len(overlapped) == len(h3_gdf)
    assert "overlap_pct" in overlapped.columns
    assert "is_slum" in overlapped.columns

    # hex1 has ~36% overlap with slum_poly
    assert overlapped.loc[overlapped["h3_index"] == "hex1", "is_slum"].iloc[0] == 1
    # hex2 has 0% overlap
    assert overlapped.loc[overlapped["h3_index"] == "hex2", "is_slum"].iloc[0] == 0

    # Attributes propagated
    assert overlapped.loc[overlapped["h3_index"] == "hex1", "KAT_TEXT"].iloc[0] == "Sedang"
    assert overlapped.loc[overlapped["h3_index"] == "hex1", "k1_a_p"].iloc[0] == 65.0


def test_evaluate_slum_binary_classification():
    # Inverted score test: lower PLSI -> higher slum probability
    y_true = np.array([1, 1, 1, 0, 0, 0])
    plsi_scores = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])

    metrics = evaluate_slum_binary_classification(plsi_scores, y_true, invert_score=True)

    assert pytest.approx(metrics["roc_auc"], 1e-4) == 1.0
    assert pytest.approx(metrics["pr_auc"], 1e-4) == 1.0
    assert metrics["optimal_f1"] == 1.0
    assert metrics["n_positives"] == 3
    assert metrics["n_negatives"] == 3


def test_evaluate_dki_severity_stratification():
    df = pd.DataFrame({
        "plsi": [
            0.15, 0.18, 0.20,  # Berat
            0.35, 0.38, 0.40,  # Sedang
            0.55, 0.58, 0.60,  # Ringan
            0.75, 0.78, 0.80,  # Sangat Ringan
        ],
        "KAT_TEXT": [
            "Berat", "Berat", "Berat",
            "Sedang", "Sedang", "Sedang",
            "Ringan", "Ringan", "Ringan",
            "Sangat Ringan", "Sangat Ringan", "Sangat Ringan",
        ],
    })

    res = evaluate_dki_severity_stratification(df, plsi_col="plsi", severity_col="KAT_TEXT")

    assert res["anova_p"] < 0.001
    assert res["kruskal_p"] < 0.05
    assert res["is_monotonic_decreasing"] is True
    assert "tier_stats" in res
    assert res["tier_stats"]["Berat"]["mean"] < res["tier_stats"]["Sedang"]["mean"]


def test_evaluate_kotaku_subdimension_concordance():
    # Lower living space & accessibility -> higher KOTAKU defect percentages
    df = pd.DataFrame({
        "r_space": [0.2, 0.4, 0.6, 0.8, 1.0],
        "a_amenity": [0.1, 0.3, 0.5, 0.7, 0.9],
        "k1_a_p": [90.0, 70.0, 50.0, 30.0, 10.0],
        "k2_b_p": [85.0, 65.0, 45.0, 25.0, 5.0],
    })

    concordance = evaluate_kotaku_subdimension_concordance(
        df,
        pairs=[
            ("r_space", "k1_a_p"),
            ("a_amenity", "k2_b_p"),
        ],
    )

    assert "r_space_vs_k1_a_p" in concordance
    # Expect negative correlation: higher adequacy -> lower defect %
    assert concordance["r_space_vs_k1_a_p"]["pearson_r"] < -0.9
    assert concordance["a_amenity_vs_k2_b_p"]["spearman_rho"] < -0.9
