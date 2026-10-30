"""
Integration tests for the dual-layer validation pipeline orchestrator.
"""

import json

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Polygon

from phys_living_index.validation.run_validation import (
    generate_validation_markdown_table,
    run_dual_validation,
)


@pytest.fixture
def mock_pipeline_data():
    rng = np.random.default_rng(42)
    n = 40

    # Synthetic H3 grid polygons around Jakarta
    lats = np.linspace(-6.25, -6.15, 8)
    lons = np.linspace(106.75, 106.85, 5)
    grid_lats, grid_lons = np.meshgrid(lats, lons)
    flat_lats = grid_lats.ravel()[:n]
    flat_lons = grid_lons.ravel()[:n]

    geoms = [
        Polygon(
            [
                (lon - 0.005, lat - 0.005),
                (lon + 0.005, lat - 0.005),
                (lon + 0.005, lat + 0.005),
                (lon - 0.005, lat + 0.005),
                (lon - 0.005, lat - 0.005),
            ]
        )
        for lat, lon in zip(flat_lats, flat_lons, strict=False)
    ]

    h3_gdf = gpd.GeoDataFrame(
        {
            "h3_index": [f"886546{i:04d}" for i in range(n)],
            "latitude": flat_lats,
            "longitude": flat_lons,
            "population": rng.uniform(500, 5000, size=n),
            "plsi": rng.uniform(0.1, 0.9, size=n),
            "r_space": rng.uniform(0.2, 1.5, size=n),
            "a_amenity": rng.uniform(0.1, 0.9, size=n),
            "z_elev": rng.uniform(0.1, 0.8, size=n),
            "lst_inv": rng.uniform(0.2, 0.8, size=n),
            "kabupaten_kota": ["Jakarta Pusat" if i < 20 else "Jakarta Selatan" for i in range(n)],
            "geometry": geoms,
        },
        crs="EPSG:4326",
    )

    # Synthetic RWI points
    rwi_df = pd.DataFrame(
        {
            "latitude": flat_lats[::4],
            "longitude": flat_lons[::4],
            "rwi": rng.normal(0.5, 0.6, size=len(flat_lats[::4])),
            "error": rng.uniform(0.1, 0.2, size=len(flat_lats[::4])),
        }
    )

    # Synthetic KOTAKU polygons
    kotaku_geoms = geoms[:5]
    kotaku_gdf = gpd.GeoDataFrame(
        {
            "id": [f"slum_{i}" for i in range(5)],
            "KAT_TEXT": ["Berat", "Sedang", "Sedang", "Ringan", "Sangat Ringan"],
            "k1_a_p": [80.0, 60.0, 50.0, 30.0, 10.0],
            "k2_b_p": [70.0, 50.0, 40.0, 20.0, 5.0],
            "k4_d_p": [90.0, 75.0, 60.0, 40.0, 20.0],
            "k3_a_p": [60.0, 40.0, 30.0, 15.0, 5.0],
            "geometry": kotaku_geoms,
        },
        crs="EPSG:4326",
    )

    # Synthetic BPS poverty table
    bps_poverty_df = pd.DataFrame(
        {
            "kabupaten_kota": ["Jakarta Pusat", "Jakarta Selatan"],
            "poverty_rate_pct": [3.8, 3.2],
        }
    )

    return h3_gdf, rwi_df, kotaku_gdf, bps_poverty_df


def test_run_dual_validation(mock_pipeline_data, tmp_path):
    h3_gdf, rwi_df, kotaku_gdf, bps_poverty_df = mock_pipeline_data

    out_dir = tmp_path / "validation_output"
    results = run_dual_validation(
        h3_gdf=h3_gdf,
        rwi_df=rwi_df,
        kotaku_gdf=kotaku_gdf,
        bps_df=bps_poverty_df,
        output_dir=str(out_dir),
    )

    # Verify return dictionary contains all required components
    assert "rwi_concordance" in results
    assert "rwi_4quadrant" in results
    assert "kotaku_discrimination" in results
    assert "kotaku_severity_stratification" in results
    assert "kotaku_subdimension_concordance" in results
    assert "bps_macro_audit" in results

    # Verify generated artifact files exist on disk
    assert (out_dir / "validation_summary.json").exists()
    assert (out_dir / "rwi_4quadrant_classification.csv").exists()
    assert (out_dir / "kotaku_ground_truth_benchmark.csv").exists()
    assert (out_dir / "validation_table.md").exists()
    assert (out_dir / "validation_table.tex").exists()

    # Verify json summary is valid JSON and non-empty
    with open(out_dir / "validation_summary.json", encoding="utf-8") as f:
        summary_data = json.load(f)
    assert "rwi_concordance" in summary_data
    assert "kotaku_discrimination" in summary_data


def test_generate_validation_markdown_table():
    summary = {
        "rwi_concordance": {"pearson_r": 0.684, "spearman_rho": 0.652, "n_samples": 2150},
        "kotaku_discrimination": {"roc_auc": 0.835, "pr_auc": 0.742, "optimal_f1": 0.781},
        "kotaku_severity_stratification": {"anova_f": 42.15, "anova_p": 1.2e-8},
        "bps_macro_audit": {"poverty_correlation_r": 0.712, "n_units": 15},
    }
    md_table = generate_validation_markdown_table(summary)
    assert "| Validation Benchmark |" in md_table
    assert "0.684" in md_table
    assert "0.835" in md_table
    assert "42.15" in md_table
