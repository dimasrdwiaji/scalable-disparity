import h3
import numpy as np
import pandas as pd
import pytest

from phys_living_index.data.gee import (
    batch_cells,
    compute_valid_fraction,
    h3_cell_features,
    parse_reduce_regions,
    read_provenance,
    write_table_with_provenance,
)
from phys_living_index.data.gee_layers import (
    COPERNICUS_DEM_GLO30,
    GHS_BUILT_V,
    interpolation_weight,
    select_window_tier,
    tier_table_from_reduction,
)

CELLS = list(h3.grid_disk(h3.latlng_to_cell(-6.2, 106.8, 8), 1))


def test_h3_cell_features_closed_lon_lat_rings():
    features = h3_cell_features(CELLS[:2])

    assert [f["properties"]["h3_index"] for f in features] == CELLS[:2]
    ring = features[0]["geometry"]["coordinates"][0]
    assert ring[0] == ring[-1]
    lon, lat = ring[0]
    assert 106 < lon < 107 and -7 < lat < -6


def test_batch_cells_sizes():
    batches = batch_cells(CELLS, 3)
    assert [len(b) for b in batches] == [3, 3, 1]
    with pytest.raises(ValueError):
        batch_cells(CELLS, 0)


def test_parse_reduce_regions_multi_and_single_band_naming():
    multi = [{"properties": {"h3_index": "a", "ndvi_mean": 0.4, "ndvi_count": 10, "bsi_mean": None, "bsi_count": 0}}]
    df = parse_reduce_regions(multi, ["ndvi", "bsi"], ["mean", "count"])
    assert df.loc["a", "ndvi_mean"] == pytest.approx(0.4)
    assert np.isnan(df.loc["a", "bsi_mean"])

    single = [{"properties": {"h3_index": "b", "sum": 1234.0, "count": 70}}]
    df = parse_reduce_regions(single, ["population"], ["sum", "count"])
    assert df.loc["b", "population_sum"] == pytest.approx(1234.0)
    assert df.loc["b", "population_count"] == 70

    # Multi-band with single uncombined reducer: Earth Engine names outputs by band name, not <band>_<stat>
    uncombined_multi = [{"properties": {"h3_index": "c", "presence": 500.0, "presence_floors": 1200.0}}]
    df_uncombined = parse_reduce_regions(uncombined_multi, ["presence", "presence_floors"], ["sum"])
    assert df_uncombined.loc["c", "presence_sum"] == pytest.approx(500.0)
    assert df_uncombined.loc["c", "presence_floors_sum"] == pytest.approx(1200.0)

    # Single-band with single uncombined reducer where EE names property by band name
    uncombined_single = [{"properties": {"h3_index": "d", "population": 4000.0}}]
    df_pop = parse_reduce_regions(uncombined_single, ["population"], ["sum"])
    assert df_pop.loc["d", "population_sum"] == pytest.approx(4000.0)


def test_compute_valid_fraction_full_and_partial_cells():
    cell = CELLS[0]
    area = h3.cell_area(cell, unit="m^2")
    full = compute_valid_fraction(pd.Series({cell: area / 400.0}), scale_m=20.0)
    half = compute_valid_fraction(pd.Series({cell: area / 800.0}), scale_m=20.0)
    over = compute_valid_fraction(pd.Series({cell: area}), scale_m=20.0)

    assert full[cell] == pytest.approx(1.0)
    assert half[cell] == pytest.approx(0.5)
    assert over[cell] == 1.0


def test_provenance_round_trip(tmp_path):
    df = pd.DataFrame({"x": [1.0, 2.0]}, index=pd.Index(["a", "b"], name="h3_index"))
    path = write_table_with_provenance(df, tmp_path / "t.parquet", {"asset": "X/Y", "tiers": [1, 2]})

    assert read_provenance(path) == {"asset": "X/Y", "tiers": [1, 2]}
    assert pd.read_parquet(path)["x"].tolist() == [1.0, 2.0]


def _tier(values, n_clear, valid_frac, doy=200):
    return pd.DataFrame(
        {"ndvi": values, "n_clear": n_clear, "valid_frac": valid_frac, "median_doy": doy},
        index=pd.Index(["a", "b", "c"], name="h3_index"),
    )


def test_select_window_tier_takes_narrowest_representative_tier():
    tier1 = _tier([0.1, 0.2, 0.3], n_clear=[6, 2, 6], valid_frac=[0.9, 0.9, 0.5])
    tier2 = _tier([0.11, 0.21, 0.31], n_clear=[9, 7, 3], valid_frac=[1.0, 0.95, 0.6])

    out = select_window_tier([tier1, tier2], ["ndvi"], min_clear=5, min_valid_frac=0.8)

    assert out.loc["a", "tier"] == 1 and out.loc["a", "ndvi"] == pytest.approx(0.1)
    assert out.loc["b", "tier"] == 2 and out.loc["b", "ndvi"] == pytest.approx(0.21)
    assert out.loc["c", "tier"] == 0 and np.isnan(out.loc["c", "ndvi"])
    # Failed cells keep the widest tier's QA for reporting
    assert out.loc["c", "n_clear"] == 3


def test_select_window_tier_with_partial_later_tier():
    tier1 = _tier([0.1, 0.2, 0.3], n_clear=[6, 2, 6], valid_frac=[0.9, 0.9, 0.9])
    tier2 = _tier([np.nan, 0.25, np.nan], n_clear=[np.nan, 8, np.nan], valid_frac=[np.nan, 0.9, np.nan])

    out = select_window_tier([tier1, tier2], ["ndvi"], min_clear=5, min_valid_frac=0.8)
    assert out["tier"].tolist() == [1, 2, 1]


def test_tier_table_from_reduction():
    cell = CELLS[0]
    area = h3.cell_area(cell, unit="m^2")
    reduced = pd.DataFrame(
        {"lst_mean": [301.5], "lst_count": [area / 900.0], "n_clear_median": [4.0], "median_doy_median": [210.0]},
        index=[cell],
    )
    table = tier_table_from_reduction(reduced, ["lst"], scale_m=30.0)

    assert table.loc[cell, "lst"] == pytest.approx(301.5)
    assert table.loc[cell, "n_clear"] == 4.0
    assert table.loc[cell, "valid_frac"] == pytest.approx(1.0)


def test_interpolation_weight():
    assert interpolation_weight(2023, 2020, 2025) == pytest.approx(0.6)
    assert interpolation_weight(2020, 2020, 2025) == 0.0
    with pytest.raises(ValueError):
        interpolation_weight(2019, 2020, 2025)


def test_ghs_built_v_and_dem_assets_defined():
    assert GHS_BUILT_V == "JRC/GHSL/P2023A/GHS_BUILT_V"
    assert COPERNICUS_DEM_GLO30 == "COPERNICUS/DEM/GLO30_2024_1"


def test_ghs_built_volume_reduction_and_floor_area():
    from phys_living_index.features.build_features import compute_ghs_residential_floor_area

    total = pd.Series([100000.0, 50000.0, 10000.0], index=["c1", "c2", "c3"])
    nres = pd.Series([20000.0, 50000.0, 15000.0], index=["c1", "c2", "c3"])

    floor_area = compute_ghs_residential_floor_area(total, nres, floor_height_m=3.0)

    # c1: (100k - 20k) / 3.0 = 80k / 3.0 = 26666.67 m²
    assert floor_area["c1"] == pytest.approx(80000.0 / 3.0)
    # c2: (50k - 50k) / 3.0 = 0 m²
    assert floor_area["c2"] == pytest.approx(0.0)
    # c3: (10k - 15k) -> max(0, -5k) / 3.0 = 0 m² (clamped non-negative)
    assert floor_area["c3"] == pytest.approx(0.0)


def test_topographic_hazard_and_safety_inversion():
    from phys_living_index.features.build_features import compute_terrain_safety

    hazard = pd.Series([0.0, 0.25, 0.80, 1.0, 1.5, -0.1], index=["flat", "gentle", "steep", "cliff", "over", "under"])
    safety = compute_terrain_safety(hazard)

    assert safety["flat"] == pytest.approx(1.0)
    assert safety["gentle"] == pytest.approx(0.75)
    assert safety["steep"] == pytest.approx(0.20)
    assert safety["cliff"] == pytest.approx(0.0)
    assert safety["over"] == pytest.approx(0.0)
    assert safety["under"] == pytest.approx(1.0)
