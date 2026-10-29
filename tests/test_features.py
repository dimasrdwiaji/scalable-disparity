import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Polygon

from phys_living_index.analysis.disparity_metrics import (
    compute_gini_coefficient,
    compute_palma_ratio,
)
from phys_living_index.features.build_features import (
    build_10d_feature_matrix,
    compute_economic_energy_radiance,
    compute_living_space_ratio,
    normalize_feature_matrix,
    winsorize_series,
)


def test_winsorize_series():
    # 100 values from 1 to 100 with an extreme outlier spike at index 99
    data = np.arange(1.0, 101.0)
    data[-1] = 10000.0  # extreme spike
    series = pd.Series(data)
    
    winsorized = winsorize_series(series, percentile=95.0)
    
    # 95th percentile of 1..100 with 10000
    p95 = np.percentile(data, 95.0)
    assert winsorized.max() == pytest.approx(p95)
    assert winsorized.iloc[-1] == pytest.approx(p95)
    assert winsorized.iloc[0] == 1.0


def test_compute_living_space_ratio_winsorized():
    # 2 buildings in 2 hexes
    # hex 0: normal building 90 m2, 10 people -> 9 m2/capita -> ratio = 1.0
    # hex 1: commercial high-rise 9000 m2, 1 person -> 9000 m2/capita -> extreme outlier
    buildings_gdf = gpd.GeoDataFrame({
        "h3_index": ["hex_norm", "hex_outlier"],
        "height": [3.0, 30.0],  # 1 floor, 10 floors
        "geometry": [
            Polygon([(0, 0), (0, 9.48), (9.48, 9.48), (9.48, 0)]),  # ~90 m2
            Polygon([(0, 0), (0, 30), (30, 30), (30, 0)]),  # 900 m2 * 10 floors = 9000 m2
        ]
    })
    pop = pd.Series({"hex_norm": 10.0, "hex_outlier": 1.0})
    
    # Compute with winsorize_p99=True
    r_space = compute_living_space_ratio(
        buildings_gdf, 
        pop, 
        min_standard_m2=9.0, 
        floor_height_m=3.0,
        winsorize_p99=True,
    )
    
    assert isinstance(r_space, pd.Series)
    assert r_space["hex_norm"] == pytest.approx(1.0, rel=1e-2)
    # The outlier should be capped by p99
    assert r_space["hex_outlier"] < 1000.0


def test_compute_economic_energy_radiance():
    viirs = pd.Series({"hex1": 10.0, "hex2": 500.0})
    pop = pd.Series({"hex1": 100.0, "hex2": 1.0})
    
    e_night = compute_economic_energy_radiance(viirs, pop, winsorize_p99=True)
    assert isinstance(e_night, pd.Series)
    assert len(e_night) == 2
    assert e_night["hex1"] == pytest.approx(0.1)


def test_build_10d_feature_matrix_all_channels():
    # Create synthetic dataframe with all 10 raw channels for 5 hexes
    n_hexes = 5
    hex_ids = [f"hex_{i}" for i in range(n_hexes)]
    raw_df = pd.DataFrame({
        "space_sufficiency_ratio": [0.5, 1.0, 2.0, 5.0, 10.0],
        "builtup_ndbi": [-0.5, -0.2, 0.0, 0.3, 0.7],
        "cumulative_amenities_15m": [0, 5, 15, 30, 60],
        "bare_soil_bsi": [-0.2, 0.0, 0.2, 0.4, 0.8],
        "nighttime_energy_radiance": [1.0, 5.0, 15.0, 30.0, 80.0],
        "vegetation_ndvi": [0.0, 0.2, 0.4, 0.6, 0.8],
        "thermal_comfort_lst_inv": [315.0, 310.0, 305.0, 300.0, 295.0],  # higher K is hotter, inverted should be higher for cooler
        "water_mndwi": [-0.5, -0.2, 0.0, 0.2, 0.5],
        "air_purity_pm25_inv": [80.0, 50.0, 35.0, 20.0, 10.0],  # higher ug/m3 is dirtier, inverted should be higher for cleaner
        "multi_pollutant_aqi_inv": [200.0, 150.0, 100.0, 50.0, 20.0],
    }, index=hex_ids)
    
    X = build_10d_feature_matrix(raw_df)
    
    assert X.shape == (n_hexes, 10)
    assert np.all(X >= 0.0)
    assert np.all(X <= 1.0)
    assert not np.isnan(X).any()
    assert not np.isinf(X).any()


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


def test_focal_disparity_surface():
    import h3

    from phys_living_index.analysis.disparity_metrics import compute_focal_disparity_surface

    rng = np.random.default_rng(42)
    center_hex = h3.latlng_to_cell(-6.2, 106.8, 8)
    hex_list = list(h3.grid_disk(center_hex, 2))  # 19 hexes
    vals = rng.uniform(0.1, 0.9, size=len(hex_list))

    focal_gini, focal_palma = compute_focal_disparity_surface(hex_list, vals, k_ring=1)
    assert len(focal_gini) == len(hex_list)
    assert len(focal_palma) == len(hex_list)
    assert np.all(focal_gini >= 0.0)


def test_bivariate_local_moran_baseline():
    from phys_living_index.analysis.disparity_metrics import compute_bivariate_local_moran

    n = 20
    # Ring edges
    src = np.arange(n)
    dst = (src + 1) % n
    edge_index = np.stack([np.concatenate([src, dst]), np.concatenate([dst, src])], axis=0)

    # Sharp step function at half
    x = np.concatenate([np.ones(10) * 0.1, np.ones(10) * 0.9])
    y = np.concatenate([np.ones(10) * 0.2, np.ones(10) * 0.8])

    lisa = compute_bivariate_local_moran(x, y, edge_index, permutations=99)
    assert "Is" in lisa
    assert "q" in lisa
    assert "p_sim" in lisa
    assert "is_outlier" in lisa
    assert len(lisa["Is"]) == n

