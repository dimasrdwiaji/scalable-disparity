import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from phys_living_index.data.gee import write_table_with_provenance
from phys_living_index.features.build_features import FEATURE_DIMENSIONS_V2_CORE
from phys_living_index.pipeline import stage3

REPO = Path(__file__).resolve().parent.parent


def _synthetic_layers(cells: list[str], rng: np.random.Generator) -> dict[str, pd.DataFrame]:
    n = len(cells)
    idx = pd.Index(cells, name="h3_index")
    urban = np.arange(n) < n // 2
    tiers = rng.choice([1, 2, 3], size=n, p=[0.8, 0.15, 0.05])
    return {
        "sentinel2": pd.DataFrame({
            "ndvi": rng.uniform(0.0, 0.7, n),
            "s2_res_glcm_contrast": np.where(urban, rng.uniform(5.0, 40.0, n), np.nan),
            "s2_res_glcm_homogeneity": np.where(urban, rng.uniform(0.2, 0.8, n), np.nan),
            "s2_n_clear": 8.0, "s2_valid_frac": 1.0, "s2_median_doy": 200.0, "s2_tier": tiers,
        }, index=idx),
        "landsat": pd.DataFrame({
            "lst_k": np.where(urban, 308.0, 300.0) + rng.normal(0, 1, n),
            "lst_n_clear": 4.0, "lst_valid_frac": 1.0, "lst_median_doy": 210.0, "lst_tier": tiers,
        }, index=idx),
        "settlement_class": pd.DataFrame({"smod_code": np.where(urban, 30, 12)}, index=idx),
        "ghs_residential": pd.DataFrame({
            "ghs_built_total_m2": np.where(urban, 1.0e5, 0.0),
            "ghs_built_nres_m2": np.where(urban, 2.0e4, 0.0),
        }, index=idx),
        "buildings": pd.DataFrame({
            "building_count": np.where(urban, 500, 0),
            "residential_building_count": np.where(urban, 450, 0),
            "res_share_lt50": np.where(urban, 0.4, np.nan),
            "res_share_lt60": np.where(urban, 0.55, np.nan),
            "res_nn_p25": np.where(urban, 7.5, np.nan),
            "removed_nonres_wall_m2": np.where(urban, 2000.0, 0.0),
        }, index=idx),
    }


@pytest.fixture
def region(tmp_path):
    with open(REPO / "configs" / "default.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    bbox = [106.80, -6.30, 106.95, -6.15]
    config["spatial"]["bbox"] = bbox
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

    assert list(matrix.columns[:4]) == FEATURE_DIMENSIONS_V2_CORE
    assert X.shape == (len(cells), 4) and np.isfinite(X).all()
    assert ((X >= 0) & (X <= 1)).all()
    # Rural or non-residential cells are excluded by pure physical Urban Built-Up Mask
    assert matrix["is_residential"].sum() == len(cells) // 2
    assert not matrix.loc[~matrix["is_residential"], "is_modelled"].any()
    assert matrix.loc[matrix["is_residential"], "is_modelled"].all()
    assert "population" not in raw.columns
    assert "amenities_15m" not in raw.columns
    assert qa["benchmarks_version"] == "v2"
    assert qa["residential_cells"] == len(cells) // 2
    assert "1" in {str(k) for k in qa["window_tier_shares_residential"]["s2"]}


def test_run_stage3_excludes_urban_smod_without_residential_buildings(region):
    config_path, root, cells = region
    # Zero out residential_building_count on the first urban cell while keeping SMOD=30
    bld_path = root / "data" / "interim" / "layers" / "buildings.parquet"
    bld = pd.read_parquet(bld_path)
    bld.iloc[0, bld.columns.get_loc("residential_building_count")] = 0
    write_table_with_provenance(bld, bld_path, {"synthetic": True})

    outputs = stage3.run_stage3(config_path, root, config_dir=REPO / "configs")
    matrix = pd.read_parquet(outputs["matrix"])
    assert not bool(matrix.iloc[0]["is_residential"])
    assert matrix["is_residential"].sum() == (len(cells) // 2) - 1


def test_cached_layer_rebuilds_when_grid_changes(region):
    config_path, root, cells = region
    config = stage3.load_region_config(config_path)
    run = stage3.RegionRun(config, root, cells[:-1], root / "data" / "interim" / "layers")
    calls = []

    def builder(r):
        calls.append(1)
        return pd.DataFrame({"smod_code": 30}, index=pd.Index(r.cells, name="h3_index")), {}

    out = stage3.cached_layer(run, "settlement_class", builder)
    assert calls == [1] and len(out) == len(cells) - 1


def test_run_stage3_computes_residential_building_morphology_from_footprints(region):
    import geopandas as gpd
    import h3
    import pyproj
    from shapely.geometry import box

    config_path, root, cells = region
    # Force build_buildings to execute from raw footprints + non-res zones
    (root / "data" / "interim" / "layers" / "buildings.parquet").unlink()

    # Ensure smod_code=30 on our test cells
    smod_path = root / "data" / "interim" / "layers" / "settlement_class.parquet"
    smod_df = pd.read_parquet(smod_path)
    cell_a, cell_b = cells[0], cells[1]
    smod_df["smod_code"] = 30
    write_table_with_provenance(smod_df, smod_path, {"synthetic": True})

    to_wgs = pyproj.Transformer.from_crs("EPSG:32748", "EPSG:4326", always_xy=True).transform
    to_utm = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32748", always_xy=True).transform

    def metric_poly(cx: float, cy: float, width: float, height: float):
        x0, y0 = to_wgs(cx - width / 2.0, cy - height / 2.0)
        x1, y1 = to_wgs(cx + width / 2.0, cy + height / 2.0)
        return box(x0, y0, x1, y1)

    lat_a, lon_a = h3.cell_to_latlng(cell_a)
    ax, ay = to_utm(lon_a, lat_a)
    lat_b, lon_b = h3.cell_to_latlng(cell_b)
    bx, by = to_utm(lon_b, lat_b)

    # Cell A: 4 residential buildings + 1 industrial building masked out by overlapping OSM zones
    # + 1 large warehouse (60x50=3000m2, 1 floor) outside OSM zones masked by size/height override!
    # Areas: 6x6=36m2 (<50 & <60), 6x6=36m2 (<50 & <60), 7x8=56m2 (<60 only), 10x10=100m2 (>=60)
    # Pairwise distances in Cell A: pair (0,1) at 6m apart; pair (2,3) at 14m apart; 120m between pairs
    # Expected NN distances = [6.0, 6.0, 14.0, 14.0] -> P25 = 6.0 m
    # Non-res outliers at (ax+200, ay) [overlapping OSM] & (ax-200, ay) [3000m2 warehouse] must be excluded!
    geoms = [
        metric_poly(ax, ay, 6.0, 6.0),
        metric_poly(ax + 6.0, ay, 6.0, 6.0),
        metric_poly(ax, ay + 120.0, 7.0, 8.0),
        metric_poly(ax + 14.0, ay + 120.0, 10.0, 10.0),
        metric_poly(ax + 200.0, ay, 80.0, 80.0),
        metric_poly(ax - 200.0, ay, 60.0, 50.0),
        # Cell B: single residential building (40m2) -> res_nn_p25 is NaN
        metric_poly(bx, by, 5.0, 8.0),
    ]
    b_gdf = gpd.GeoDataFrame(
        {
            "id": [f"b{i}" for i in range(7)],
            "height": [np.nan] * 7,
            "confidence": [0.95] * 7,
            "floor_count": [1] * 7,
            "geometry": geoms,
        },
        crs="EPSG:4326",
    )
    (root / "data" / "raw").mkdir(parents=True, exist_ok=True)
    b_gdf.to_parquet(root / "data" / "raw" / "buildings.parquet")

    # Overlapping OSM polygons at (ax+200, ay) must not double-count building_count!
    zone_poly = metric_poly(ax + 200.0, ay, 120.0, 120.0)
    z_gdf = gpd.GeoDataFrame({"landuse": ["industrial", "railway"], "geometry": [zone_poly, zone_poly]}, crs="EPSG:4326")
    z_gdf.to_parquet(root / "data" / "interim" / "osm_nonres_zones.parquet")

    outputs = stage3.run_stage3(config_path, root, config_dir=REPO / "configs")
    raw = pd.read_parquet(outputs["raw"])
    matrix = pd.read_parquet(outputs["matrix"])

    assert raw.loc[cell_a, "building_count"] == 6
    assert raw.loc[cell_a, "residential_building_count"] == 4
    assert raw.loc[cell_a, "res_share_lt50"] == pytest.approx(0.50, abs=1e-3)
    assert raw.loc[cell_a, "res_share_lt60"] == pytest.approx(0.75, abs=1e-3)
    assert raw.loc[cell_a, "res_nn_p25"] == pytest.approx(6.0, abs=0.2)

    assert raw.loc[cell_b, "residential_building_count"] == 1
    assert raw.loc[cell_b, "res_share_lt50"] == pytest.approx(1.0, abs=1e-3)
    assert np.isnan(raw.loc[cell_b, "res_nn_p25"])
    assert not bool(matrix.loc[cell_b, "is_modelled"])


def test_run_stage3_computes_k5_local_ring_and_city_median_dlst(region):
    import h3

    config_path, root, cells = region
    # Mark all cells as urban built-up (SMOD=30, res_bld=100) and impose a smooth regional W->E gradient
    # plus one sharp local hot spot (+4 K above its local neighborhood).
    smod_path = root / "data" / "interim" / "layers" / "settlement_class.parquet"
    bld_path = root / "data" / "interim" / "layers" / "buildings.parquet"
    ls_path = root / "data" / "interim" / "layers" / "landsat.parquet"

    smod = pd.read_parquet(smod_path)
    smod["smod_code"] = 30
    write_table_with_provenance(smod, smod_path, {"synthetic": True})

    bld = pd.read_parquet(bld_path)
    bld["residential_building_count"] = 100
    bld["res_share_lt50"] = 0.3
    bld["res_nn_p25"] = 8.0
    write_table_with_provenance(bld, bld_path, {"synthetic": True})

    lons = np.array([h3.cell_to_latlng(c)[1] for c in cells])
    # Smooth regional ramp across ~16 km: +0 K on west to +6 K on east
    lon_norm = (lons - lons.min()) / max(lons.max() - lons.min(), 1e-6)
    lst_k = 302.0 + 6.0 * lon_norm

    # Pick an interior cool western cell as a true local hot spot (+4 K over neighbors)
    hotspot_idx = int(np.argsort(lon_norm)[len(cells) // 4])
    hotspot_cell = cells[hotspot_idx]
    lst_k[hotspot_idx] += 4.0

    # Make east-most cell an isolated island (< min_ring_cells) by marking its ring non-urban
    east_idx = int(np.argmax(lon_norm))
    east_cell = cells[east_idx]
    for nbr in h3.grid_disk(east_cell, 5):
        if nbr != east_cell and nbr in bld.index:
            bld.loc[nbr, "residential_building_count"] = 0
    write_table_with_provenance(bld, bld_path, {"synthetic": True})

    ls = pd.read_parquet(ls_path)
    ls["lst_k"] = lst_k
    write_table_with_provenance(ls, ls_path, {"synthetic": True})

    outputs = stage3.run_stage3(config_path, root, config_dir=REPO / "configs")
    raw = pd.read_parquet(outputs["raw"])

    # Local k=5 urban ring detects the +4 K hotspot accurately despite its cool western background,
    # whereas citywide median understates it due to the warmer east.
    assert raw.loc[hotspot_cell, "dlst_local_ring_k5"] == pytest.approx(4.0, abs=0.4)
    assert raw.loc[hotspot_cell, "dlst_local_ring_k5"] > raw.loc[hotspot_cell, "dlst_city_median"] + 1.0
    # Isolated cell with fewer than min_ring_cells urban ring neighbors gets NaN (no cross-city leakage)
    assert np.isnan(raw.loc[east_cell, "dlst_local_ring_k5"])
    assert not np.isnan(raw.loc[east_cell, "dlst_city_median"])


def test_run_stage3_carries_optical_glcm_candidates_and_ghs_res_share(region):
    import geopandas as gpd

    config_path, root, cells = region
    ghs_path = root / "data" / "interim" / "layers" / "ghs_residential.parquet"
    ghs = pd.read_parquet(ghs_path)
    # Cell 0: 80% residential built-up; Cell 1: 100% non-residential -> 0.0; Cell 2: 0 total built -> NaN
    ghs.iloc[0] = [1.0e5, 2.0e4]
    ghs.iloc[1] = [5.0e4, 6.0e4]  # over-clipped nres > total should clamp at 0.0
    ghs.iloc[2] = [0.0, 0.0]
    write_table_with_provenance(ghs, ghs_path, {"synthetic": True})

    # Also simulate an urban cell (cells[1]) with missing/NaN GLCM texture
    s2_path = root / "data" / "interim" / "layers" / "sentinel2.parquet"
    s2 = pd.read_parquet(s2_path)
    s2.loc[cells[1], "s2_res_glcm_contrast"] = np.nan
    s2.loc[cells[1], "s2_res_glcm_homogeneity"] = np.nan
    write_table_with_provenance(s2, s2_path, {"synthetic": True})

    outputs = stage3.run_stage3(config_path, root, config_dir=REPO / "configs")
    raw = pd.read_parquet(outputs["raw"])
    geo = gpd.read_parquet(outputs["geo"])

    assert raw.loc[cells[0], "ghs_res_share"] == pytest.approx(0.80)
    assert raw.loc[cells[1], "ghs_res_share"] == pytest.approx(0.0)
    assert np.isnan(raw.loc[cells[2], "ghs_res_share"])
    assert "s2_res_glcm_contrast" in raw.columns and "s2_res_glcm_contrast" in geo.columns
    assert "s2_res_glcm_homogeneity" in raw.columns and "ghs_res_share" in geo.columns
    assert -1.0 <= float(geo.loc[cells[0], "ndvi"]) <= 1.0
    assert raw.loc[cells[0], "s2_res_glcm_contrast"] > 0.0
    assert np.isnan(raw.loc[cells[1], "s2_res_glcm_contrast"])  # NaN-safe on sparse/absent urban texture
    assert np.isnan(raw.loc[cells[-1], "s2_res_glcm_contrast"])  # rural cell masked to NaN
