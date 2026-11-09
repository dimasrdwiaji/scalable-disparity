import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from phys_living_index.data.gee import write_table_with_provenance
from phys_living_index.features.build_features import (
    FEATURE_DIMENSIONS_7D,
)
from phys_living_index.pipeline import stage3

REPO = Path(__file__).resolve().parent.parent


def _synthetic_layers(cells: list[str], rng: np.random.Generator) -> dict[str, pd.DataFrame]:
    n = len(cells)
    idx = pd.Index(cells, name="h3_index")
    urban = np.arange(n) < n // 2
    tiers = rng.choice([1, 2, 3], size=n, p=[0.8, 0.15, 0.05])
    return {
        "sentinel2": pd.DataFrame({
            "ndvi": rng.uniform(0.0, 0.7, n), "ndbi": rng.uniform(-0.3, 0.2, n), "bsi": rng.uniform(-0.2, 0.2, n),
            "s2_n_clear": 8.0, "s2_valid_frac": 1.0, "s2_median_doy": 200.0, "s2_tier": tiers,
        }, index=idx),
        "landsat": pd.DataFrame({
            "lst_k": np.where(urban, 308.0, 300.0) + rng.normal(0, 1, n),
            "lst_n_clear": 4.0, "lst_valid_frac": 1.0, "lst_median_doy": 210.0, "lst_tier": tiers,
        }, index=idx),
        "water": pd.DataFrame({"water_frequency": rng.uniform(0, 0.2, n), "water_n_obs": 40.0,
                               "water_valid_frac": 1.0, "permanent_water_share": 0.0}, index=idx),
        "vegetation_probability": pd.DataFrame({"veg_probability": np.where(urban, 0.1, 0.9)}, index=idx),
        "population": pd.DataFrame({
            "population": np.where(urban, 5000.0, 50.0),
            "built_surface_early_m2": 1e5,
            "built_surface_late_m2": 1.05e5,
            "built_surface_nres_early_m2": 2e4,
            "built_surface_nres_late_m2": 2.1e4,
            "built_surface_total_2023_m2": 1.03e5,
            "built_surface_nres_2023_m2": 2.06e4,
            "residential_ratio": 0.8,
        }, index=idx),
        "settlement_class": pd.DataFrame({"smod_code": np.where(urban, 30, 12)}, index=idx),
        "night_lights": pd.DataFrame({"radiance": np.where(urban, 30.0, 0.5)}, index=idx),
        "no2": pd.DataFrame({"no2": rng.uniform(5e-5, 2e-4, n)}, index=idx),
        "modis_lst": pd.DataFrame({"modis_lst_k": np.where(urban, 309.0, 301.0)}, index=idx),
        "open_buildings_floors": pd.DataFrame({"ob_mean_floors": np.where(urban, 2.0, np.nan),
                                               "ob_presence_sum": 1.0}, index=idx),
        "ghs_built_volume": pd.DataFrame({
            "built_volume_total_m3": np.where(urban, 1.2e5, 0.0),
            "built_volume_nres_m3": np.where(urban, 2.0e4, 0.0),
            "built_volume_res_m3": np.where(urban, 1.0e5, 0.0),
            "ghs_floor_area_m2": np.where(urban, 3.3333e4, 0.0),
        }, index=idx),
        "topographic_hazard": pd.DataFrame({
            "hazard_slope_share": rng.uniform(0.0, 0.1, n),
            "terrain_safety_inv": rng.uniform(0.9, 1.0, n),
        }, index=idx),
        "buildings": pd.DataFrame({
            "building_count": np.where(urban, 500, 0),
            "footprint_area_m2": np.where(urban, 5e4, 0.0),
            "footprint_wall_m2": np.where(urban, 4e4, 0.0),
            "net_res_footprint_m2": np.where(urban, 4e4, 0.0),
            "explicit_floor_area_m2": 0.0,
            "unknown_height_footprint_m2": np.where(urban, 4e4, 0.0),
            "removed_nonres_wall_m2": 0.0,
            "residential_building_count": np.where(urban, 500, 0),
            "buildings_with_height": 0,
            "building_compactness": np.where(urban, 0.75, np.nan),
        }, index=idx),
        "pm25": pd.DataFrame({"pm25": rng.uniform(30, 60, n)}, index=idx),
        "accessibility": pd.DataFrame({"amenities_15m": np.where(urban, 120, 0),
                                       "amenity_categories_15m": np.where(urban, 12, 0),
                                       "snap_distance_m": rng.uniform(0, 300, n)}, index=idx),
    }


@pytest.fixture
def region(tmp_path):
    with open(REPO / "configs" / "default.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    bbox = [106.80, -6.30, 106.95, -6.15]
    config["spatial"]["bbox"] = bbox
    config["heat_island"]["min_background_cells"] = 5
    config_path = tmp_path / "region.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    cells = stage3.generate_h3_grid(bbox, 8)
    layer_dir = tmp_path / "data" / "interim" / "layers"
    for name, df in _synthetic_layers(cells, np.random.default_rng(3)).items():
        write_table_with_provenance(df, layer_dir / f"{name}.parquet", {"synthetic": True})
    return config_path, tmp_path, cells


def test_run_stage3_end_to_end_from_cached_layers(region):
    config_path, root, cells = region
    outputs = stage3.run_stage3(config_path, root, config_dir=REPO / "configs")

    matrix = pd.read_parquet(outputs["matrix"])
    X = np.load(outputs["npy"])
    raw = pd.read_parquet(outputs["raw"])
    qa = json.loads(Path(outputs["qa"]).read_text(encoding="utf-8"))

    assert list(matrix.columns[:7]) == FEATURE_DIMENSIONS_7D
    assert X.shape == (len(cells), 7) and np.isfinite(X).all()
    assert ((X >= 0) & (X <= 1)).all()
    # Rural cells have no buildings -> not residential, so never modelled
    assert matrix["is_residential"].sum() == len(cells) // 2
    assert not matrix.loc[~matrix["is_residential"], "is_modelled"].any()
    assert matrix.loc[matrix["is_residential"], "is_modelled"].all()
    # Urban cells are ~8 K hotter than the rural vegetated background
    assert raw.loc[raw["is_residential"], "heat_island_intensity_k"].median() == pytest.approx(8.0, abs=0.5)
    # Floor area uses Open Buildings mean floors where heights are missing
    urban_cell = raw.index[raw["is_residential"]][0]
    assert raw.loc[urban_cell, "gross_floor_area_m2"] == pytest.approx(8e4)
    assert raw.loc[urban_cell, "floor_area_m2"] == pytest.approx(8e4 * 0.485)
    assert raw.loc[urban_cell, "residential_ratio"] == pytest.approx(0.485)
    assert "gross_space_sufficiency_ratio" in raw.columns
    assert "ghs_floor_area_m2" in raw.columns
    assert "residential_plan_area_fraction" in raw.columns
    assert "building_compactness" in raw.columns
    assert "terrain_safety_inv" in raw.columns
    assert qa["benchmarks_version"] == "v1"
    assert qa["buildings"]["mean_residential_ratio"] == pytest.approx(0.485)
    assert qa["residential_cells"] == len(cells) // 2
    assert "1" in {str(k) for k in qa["window_tier_shares_residential"]["s2"]}


def test_cached_layer_rebuilds_when_grid_changes(region, monkeypatch):
    config_path, root, cells = region
    config = stage3.load_region_config(config_path)
    run = stage3.RegionRun(config, root, cells[:-1], root / "data" / "interim" / "layers")
    calls = []

    def builder(r):
        calls.append(1)
        return pd.DataFrame({"pm25": 1.0}, index=pd.Index(r.cells, name="h3_index")), {}

    out = stage3.cached_layer(run, "pm25", builder)
    assert calls == [1] and len(out) == len(cells) - 1
