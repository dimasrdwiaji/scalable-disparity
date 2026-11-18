from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from phys_living_index.analysis.disparity_metrics import (
    compute_gini_coefficient,
    compute_palma_ratio,
)
from phys_living_index.features.build_features import (
    FEATURE_DIMENSIONS_7D,
    ChannelBenchmark,
    benchmark_path,
    build_feature_matrix,
    clipped_shares,
    combine_floor_area,
    compute_heat_island_intensity,
    compute_living_space_ratio,
    fill_for_message_passing,
    heat_island_background_mask,
    load_benchmarks,
    scale_channel,
)
from phys_living_index.features.residential import (
    built_surface_change_share,
    compute_residential_plan_area_fraction,
    mask_sensitivity,
    population_density,
    residential_mask,
)

CONFIG_DIR = Path(__file__).resolve().parent.parent / "configs"


@pytest.fixture
def benchmarks():
    return load_benchmarks(benchmark_path("v0", CONFIG_DIR))


def _raw_table(n=5):
    return pd.DataFrame({
        "space_sufficiency_ratio": np.linspace(0.5, 10.0, n),
        "residential_plan_area_fraction": np.linspace(0.1, 0.9, n),
        "building_compactness": np.linspace(0.3, 0.9, n),
        "amenities_15m": np.linspace(0, 2000, n),
        "ndvi": np.linspace(-0.2, 0.9, n),
        "heat_island_intensity_k": np.linspace(-6.0, 16.0, n),
        "terrain_safety_inv": np.linspace(0.0, 1.0, n),
    }, index=[f"hex_{i}" for i in range(n)])


def test_benchmark_file_matches_canonical_channels(benchmarks):
    assert benchmarks.names == FEATURE_DIMENSIONS_7D
    assert benchmarks.group_indices("socio") == [0, 1, 2, 3]
    assert benchmarks.group_indices("bio") == [4, 5, 6]
    compact = benchmarks.channels[FEATURE_DIMENSIONS_7D.index("building_compactness")]
    assert compact.lower == 0.35
    assert compact.upper == 0.85


def test_channel_benchmark_validation():
    with pytest.raises(ValueError, match="upper"):
        ChannelBenchmark("x", "x", "none", 1.0, 1.0, "positive", "socio", "standard")
    with pytest.raises(ValueError, match="orientation"):
        ChannelBenchmark("x", "x", "none", 0.0, 1.0, "sideways", "socio", "standard")


def test_scale_channel_orientation_transform_and_nan():
    positive = ChannelBenchmark("p", "p", "none", 0.0, 10.0, "positive", "socio", "standard")
    inverted = ChannelBenchmark("i", "i", "none", 0.0, 10.0, "inverted", "bio", "standard")
    logged = ChannelBenchmark("l", "l", "log1p", 0.0, float(np.log1p(99.0)), "positive", "socio", "standard")

    values = np.array([-5.0, 2.5, 20.0, np.nan])
    assert np.allclose(scale_channel(values, positive)[:3], [0.0, 0.25, 1.0])
    assert np.allclose(scale_channel(values, inverted)[:3], [1.0, 0.75, 0.0])
    assert np.isnan(scale_channel(values, positive)[3])
    assert scale_channel(np.array([99.0]), logged)[0] == pytest.approx(1.0)


def test_build_feature_matrix_bounds_order_and_orientation(benchmarks):
    raw = _raw_table()
    X = build_feature_matrix(raw, benchmarks)

    assert list(X.columns) == FEATURE_DIMENSIONS_7D
    assert ((X >= 0.0) & (X <= 1.0)).all().all()
    # Higher plan area fraction (crowding) / heat island must score lower (inverted)
    for col in ["residential_plan_area_fraction", "heat_island_intensity_inv"]:
        assert X[col].iloc[0] > X[col].iloc[-1]
    assert X["space_sufficiency_ratio"].iloc[-1] == 1.0  # 10 > 6 cap


def test_scaling_does_not_depend_on_study_area(benchmarks):
    raw = _raw_table()
    full = build_feature_matrix(raw, benchmarks)
    subset = build_feature_matrix(raw.iloc[:2], benchmarks)
    pd.testing.assert_frame_equal(full.iloc[:2], subset)


def test_build_feature_matrix_requires_sources(benchmarks):
    with pytest.raises(KeyError, match="residential_plan_area_fraction"):
        build_feature_matrix(_raw_table().drop(columns=["residential_plan_area_fraction"]), benchmarks)


def test_clipped_shares_flags_only_masked_cells(benchmarks):
    raw = _raw_table()
    mask = pd.Series([True, True, True, False, False], index=raw.index)
    shares = clipped_shares(raw, benchmarks, mask)

    assert shares.loc["residential_plan_area_fraction", "share_below_lower"] == 0.0
    assert shares.loc["terrain_safety_inv", "share_above_upper"] == 0.0


def test_fill_for_message_passing_uses_reference_median():
    scaled = pd.DataFrame({"a": [0.2, 0.4, np.nan, 0.9]})
    filled = fill_for_message_passing(scaled, [True, True, False, False])
    assert filled[2, 0] == pytest.approx(0.3)
    assert filled.dtype == np.float32


def test_combine_floor_area_with_residential_ratio():
    idx = ["a", "b", "c"]
    explicit = pd.Series([1000.0, 0.0, 500.0], index=idx)
    unknown = pd.Series([2000.0, 1000.0, 0.0], index=idx)
    mean_floors = pd.Series([2.0, 3.0, 1.0], index=idx)

    # Without ratio -> gross floor area
    gross = combine_floor_area(explicit, unknown, mean_floors)
    assert gross["a"] == pytest.approx(1000.0 + 2000.0 * 2.0)  # 5000.0
    assert gross["b"] == pytest.approx(1000.0 * 3.0)  # 3000.0
    assert gross["c"] == pytest.approx(500.0)

    # With ratio
    ratio = pd.Series([0.6, 0.0, 1.0], index=idx)
    net = combine_floor_area(explicit, unknown, mean_floors, residential_ratio=ratio)
    assert net["a"] == pytest.approx(5000.0 * 0.6)  # 3000.0
    assert net["b"] == pytest.approx(0.0)
    assert net["c"] == pytest.approx(500.0)


def test_compute_living_space_ratio_undefined_without_population():
    floor_area = pd.Series({"a": 900.0, "b": 500.0, "c": 0.0})
    pop = pd.Series({"a": 10.0, "b": 0.0, "c": 50.0})
    r = compute_living_space_ratio(floor_area, pop, un_habitat_min_m2=9.0)

    assert r["a"] == pytest.approx(10.0)
    assert np.isnan(r["b"])
    assert r["c"] == 0.0


def test_heat_island_intensity_against_rural_background():
    idx = [f"c{i}" for i in range(6)]
    lst = pd.Series([305.0, 306.0, 300.0, 300.0, 302.0, 310.0], index=idx)
    residential = pd.Series([True, True, False, False, False, False], index=idx)
    smod = pd.Series([30, 30, 12, 11, 13, 30], index=idx)
    veg = pd.Series([0.1, 0.1, 0.9, 0.8, 0.6, 0.2], index=idx)

    bg = heat_island_background_mask(residential, smod, veg, [11, 12, 13], 0.5)
    assert bg.tolist() == [False, False, True, True, True, False]

    delta, background = compute_heat_island_intensity(lst, bg, min_background_cells=3)
    assert background == pytest.approx(300.0)
    assert delta["c0"] == pytest.approx(5.0)

    with pytest.raises(ValueError, match="background"):
        compute_heat_island_intensity(lst, bg, min_background_cells=4)


def test_residential_mask_requires_density_and_buildings():
    import h3

    cells = list(h3.grid_disk(h3.latlng_to_cell(-6.2, 106.8, 8), 1))[:3]
    pop = pd.Series([1000.0, 1000.0, 10.0], index=cells)
    buildings = pd.Series([5, 0, 5], index=cells)

    density = population_density(pop)
    assert density.iloc[0] == pytest.approx(1000.0 / h3.cell_area(cells[0], unit="km^2"))

    mask = residential_mask(density, buildings, 300.0, 1)
    assert mask.tolist() == [True, False, False]

    sens = mask_sensitivity(density, buildings, [5.0, 300.0], {"pop": pop})
    assert sens.loc[5.0, "residential_cells"] == 2
    assert sens.loc[300.0, "residential_cells"] == 1


def test_compute_residential_plan_area_fraction():
    import h3

    cells = list(h3.grid_disk(h3.latlng_to_cell(-6.2, 106.8, 8), 1))[:3]
    cell_area_m2 = h3.cell_area(cells[0], unit="km^2") * 1e6

    net_footprint = pd.Series([300000.0, 0.0, 800000.0], index=cells)
    res_mask = pd.Series([True, True, False], index=cells)

    lambda_p = compute_residential_plan_area_fraction(net_footprint, cells=cells, is_residential=res_mask)
    assert lambda_p.iloc[0] == pytest.approx(300000.0 / cell_area_m2, abs=1e-3)
    assert lambda_p.iloc[1] == pytest.approx(0.0)
    assert np.isnan(lambda_p.iloc[2])  # non-residential cell masked


def test_built_surface_change_share():
    idx = ["a", "b", "c"]
    early = pd.Series([100.0, 100.0, 0.0], index=idx)
    late = pd.Series([105.0, 150.0, 20.0], index=idx)
    out = built_surface_change_share(early, late, pd.Series([True, True, True], index=idx))
    assert out["share_changed"] == pytest.approx(2 / 3)


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


def test_benchmark_v2_schema_uses_built_form_and_micro_env_without_population():
    from phys_living_index.features.build_features import (
        DEFAULT_URBAN_SMOD_CODES,
        FEATURE_DIMENSIONS_V2_CORE,
    )

    v2 = load_benchmarks(benchmark_path("v2", CONFIG_DIR))
    assert v2.version == "v2"
    assert v2.names == FEATURE_DIMENSIONS_V2_CORE
    assert v2.urban_smod_codes == DEFAULT_URBAN_SMOD_CODES
    assert v2.min_density_per_km2 is None
    assert v2.un_habitat_min_m2 is None
    assert v2.group_indices("built_form") == [0, 1]
    assert v2.group_indices("micro_env") == [2, 3]


def test_urban_built_up_mask_requires_smod_urban_and_residential_building():
    from phys_living_index.features.residential import urban_built_up_mask

    cells = ["c_urban_ok", "c_urban_no_res", "c_rural_ok", "c_suburban_ok"]
    smod = pd.Series([30, 23, 12, 21], index=cells)
    res_buildings = pd.Series([5, 0, 10, 1], index=cells)

    mask = urban_built_up_mask(smod, res_buildings)
    assert mask.tolist() == [True, False, False, True]
