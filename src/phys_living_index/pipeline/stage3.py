"""
Stage 3 pipeline: raw inputs → per-cell raw features → universally scaled feature matrix.

One entry point (`run_stage3`) builds every channel for any region config (ADR 0002, 0003):
each layer is reduced onto the region's H3 Res-8 cells and cached as a parquet table with a
provenance record under `data/interim/layers/`, so reruns only rebuild missing layers.

Layers
------
Earth Engine: Sentinel-2 indices (tiered), Landsat LST (tiered), Dynamic World water frequency
and vegetation probability, JRC permanent water, GHS-POP / GHS-BUILT-S / GHS-SMOD, VIIRS
annual radiance, Sentinel-5P NO2, MODIS LST (sanity), Open Buildings Temporal floors.
Local: building footprints (DuckDB), ACAG PM2.5 (exactextract), OSM walk accessibility.
"""

import json
import logging
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import geopandas as gpd
import h3
import numpy as np
import pandas as pd
import requests
import yaml
from shapely.geometry import Polygon, box

from ..data.gee import read_provenance, reduce_image_over_cells, write_table_with_provenance
from ..features.build_features import (
    benchmark_path,
    build_feature_matrix,
    clipped_shares,
    combine_floor_area,
    complete_feature_mask,
    compute_heat_island_intensity,
    compute_living_space_ratio,
    compute_terrain_safety,
    fill_for_message_passing,
    heat_island_background_mask,
    load_benchmarks,
)
from ..features.residential import (
    built_surface_change_share,
    compute_residential_plan_area_fraction,
    mask_sensitivity,
    population_density,
    residential_mask,
)

logger = logging.getLogger(__name__)

LayerResult = tuple[pd.DataFrame, dict[str, Any]]


@dataclass
class RegionRun:
    """Everything a layer builder needs for one region."""

    config: dict[str, Any]
    root: Path
    cells: list[str]
    layer_dir: Path

    @property
    def bbox(self) -> list[float]:
        return list(self.config["spatial"]["bbox"])

    @property
    def crs(self) -> str:
        return self.config["spatial"]["utm_crs"]

    @property
    def year(self) -> int:
        return int(self.config["reference_epoch"]["year"])

    @property
    def batch_size(self) -> int:
        return int(self.config["compositing"]["gee_batch_size"])

    def path(self, relative: str) -> Path:
        return self.root / relative


def load_region_config(path: str | Path) -> dict[str, Any]:
    """Loads a per-region measurement settings file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_h3_grid(bbox: Sequence[float], resolution: int = 8) -> list[str]:
    """Sorted H3 cells whose centroids fall inside the bounding box."""
    return sorted(h3.geo_to_cells(box(*bbox).__geo_interface__, res=resolution))


def h3_polygons(cells: Sequence[str]) -> list[Polygon]:
    """Shapely polygons (lon, lat) for H3 cells."""
    return [Polygon([(lng, lat) for lat, lng in h3.cell_to_boundary(c)]) for c in cells]


# -----------------------------------------------------------------------------
# Layer cache
# -----------------------------------------------------------------------------


def cached_layer(run: RegionRun, name: str, builder: Callable[[RegionRun], LayerResult]) -> pd.DataFrame:
    """Returns a cached layer table, building and caching it (with provenance) when missing."""
    path = run.layer_dir / f"{name}.parquet"
    if path.exists():
        df = pd.read_parquet(path)
        if list(df.index) == run.cells:
            logger.info("Layer %s: cached.", name)
            return df
        logger.warning("Layer %s: cached cells differ from region grid; rebuilding.", name)
    logger.info("Layer %s: building...", name)
    t0 = time.time()
    df, provenance = builder(run)
    df = df.reindex(run.cells)
    df.index.name = "h3_index"
    provenance = {**provenance, "layer": name, "elapsed_s": round(time.time() - t0, 1)}
    write_table_with_provenance(df, path, provenance)
    return df


def layer_provenance(run: RegionRun, names: Sequence[str]) -> dict[str, Any]:
    """Provenance records of cached layers, for the QA report."""
    out = {}
    for name in names:
        path = run.layer_dir / f"{name}.parquet"
        if path.exists():
            out[name] = read_provenance(path)
    return out


# -----------------------------------------------------------------------------
# Earth Engine layers
# -----------------------------------------------------------------------------


def _tiers(raw: list[list[list[str]]]) -> list[list[tuple[str, str]]]:
    return [[(r[0], r[1]) for r in tier] for tier in raw]


def build_sentinel2(run: RegionRun) -> LayerResult:
    from ..data.gee_layers import S2_COLLECTION, reduce_tiered_composite, sentinel2_index_collection

    cfg = run.config["compositing"]["sentinel2"]
    table, tiers = reduce_tiered_composite(
        lambda ranges: sentinel2_index_collection(run.bbox, ranges, cfg["cs_cdf_threshold"]),
        ["ndvi", "ndbi", "bsi"],
        _tiers(cfg["tiers"]),
        run.cells,
        scale_m=cfg["scale_m"],
        min_clear=cfg["min_clear"],
        min_valid_frac=cfg["min_valid_frac"],
        crs=run.crs,
        batch_size=run.batch_size,
    )
    table = table.rename(columns={c: f"s2_{c}" for c in ["n_clear", "valid_frac", "median_doy", "tier"]})
    return table, {"asset": S2_COLLECTION, "cloud_mask": f"cs_cdf>={cfg['cs_cdf_threshold']}",
                   "scale_m": cfg["scale_m"], "crs": run.crs, "tiers": tiers}


def build_landsat(run: RegionRun) -> LayerResult:
    from ..data.gee_layers import (
        LANDSAT_COLLECTIONS,
        landsat_lst_collection,
        reduce_tiered_composite,
    )

    cfg = run.config["compositing"]["landsat"]
    table, tiers = reduce_tiered_composite(
        lambda ranges: landsat_lst_collection(run.bbox, ranges, cfg["max_st_uncertainty_k"]),
        ["lst"],
        _tiers(cfg["tiers"]),
        run.cells,
        scale_m=cfg["scale_m"],
        min_clear=cfg["min_clear"],
        min_valid_frac=cfg["min_valid_frac"],
        crs=run.crs,
        batch_size=run.batch_size,
    )
    table = table.rename(columns={"lst": "lst_k", **{c: f"lst_{c}" for c in ["n_clear", "valid_frac", "median_doy", "tier"]}})
    return table, {"asset": list(LANDSAT_COLLECTIONS), "band": "ST_B10", "scale_m": cfg["scale_m"],
                   "crs": run.crs, "tiers": tiers}


def build_water(run: RegionRun) -> LayerResult:
    from ..data.gee import compute_valid_fraction
    from ..data.gee_layers import (
        DYNAMIC_WORLD,
        JRC_SURFACE_WATER,
        dynamic_world_water_frequency,
        permanent_water,
    )

    cfg = run.config["compositing"]["water"]
    image, collection = dynamic_world_water_frequency(run.bbox, tuple(cfg["date_range"]), cfg["min_observations"])
    reduced = reduce_image_over_cells(
        image, run.cells, ["water_frequency", "water_n_obs"], scale=cfg["scale_m"],
        crs=run.crs, batch_size=run.batch_size,
    )
    perm = reduce_image_over_cells(
        permanent_water(cfg["permanent_min_occurrence"]), run.cells, ["permanent_water"], scale=30,
        extra_stats=(), crs=run.crs, batch_size=run.batch_size,
    )
    table = pd.DataFrame({
        "water_frequency": reduced["water_frequency_mean"],
        "water_n_obs": reduced["water_n_obs_mean"],
        "water_valid_frac": compute_valid_fraction(reduced["water_frequency_count"], cfg["scale_m"]),
        "permanent_water_share": perm["permanent_water_mean"],
    })
    return table, {"asset": [DYNAMIC_WORLD, JRC_SURFACE_WATER], "date_range": cfg["date_range"],
                   "image_count": int(collection.size().getInfo()), "scale_m": cfg["scale_m"]}


def build_vegetation_probability(run: RegionRun) -> LayerResult:
    from ..data.gee_layers import DYNAMIC_WORLD, dynamic_world_vegetation_probability

    tier1 = _tiers(run.config["compositing"]["sentinel2"]["tiers"])[0]
    image = dynamic_world_vegetation_probability(run.bbox, tier1)
    reduced = reduce_image_over_cells(
        image, run.cells, ["veg_probability"], scale=20, extra_stats=(), crs=run.crs, batch_size=run.batch_size,
    )
    return reduced.rename(columns={"veg_probability_mean": "veg_probability"}), {
        "asset": DYNAMIC_WORLD, "bands": "trees+grass+crops", "date_ranges": tier1, "scale_m": 20}


def build_population(run: RegionRun) -> LayerResult:
    from ..data.gee_layers import (
        GHS_BUILT_S,
        GHS_POP,
        ghs_built_surface,
        ghs_native_projection,
        ghs_population,
        interpolation_weight,
    )

    cfg = run.config["population"]
    low, high = cfg["ghs_epochs"]
    early, late = cfg["built_surface_epochs"]
    image = (
        ghs_population(run.year, low, high)
        .addBands(ghs_built_surface(early).rename("built_early"))
        .addBands(ghs_built_surface(late).rename("built_late"))
        .addBands(ghs_built_surface(early, non_residential=True).rename("built_nres_early"))
        .addBands(ghs_built_surface(late, non_residential=True).rename("built_nres_late"))
    )
    reduced = reduce_image_over_cells(
        image,
        run.cells,
        ["population", "built_early", "built_late", "built_nres_early", "built_nres_late"],
        scale=100,
        reducer="sum",
        extra_stats=(),
        crs=ghs_native_projection(),
        batch_size=run.batch_size,
    )
    weight = interpolation_weight(run.year, early, late)
    built_early = reduced["built_early_sum"].fillna(0.0)
    built_late = reduced["built_late_sum"].fillna(0.0)
    built_nres_early = reduced["built_nres_early_sum"].fillna(0.0)
    built_nres_late = reduced["built_nres_late_sum"].fillna(0.0)

    built_total_2023 = built_early * (1.0 - weight) + built_late * weight
    built_nres_2023 = built_nres_early * (1.0 - weight) + built_nres_late * weight

    # residential_ratio = (built_total - built_nres) / built_total, clamped to [0.0, 1.0]
    # Default to 1.0 where built_total == 0
    ratio = (built_total_2023 - built_nres_2023) / built_total_2023.where(built_total_2023 > 0)
    residential_ratio = ratio.fillna(1.0).clip(lower=0.0, upper=1.0)

    table = pd.DataFrame({
        "population": reduced["population_sum"].fillna(0.0),
        "built_surface_early_m2": built_early,
        "built_surface_late_m2": built_late,
        "built_surface_nres_early_m2": built_nres_early,
        "built_surface_nres_late_m2": built_nres_late,
        "built_surface_total_2023_m2": built_total_2023,
        "built_surface_nres_2023_m2": built_nres_2023,
        "residential_ratio": residential_ratio,
    })
    return table, {
        "asset": [GHS_POP, GHS_BUILT_S],
        "population_year": run.year,
        "population_epochs": [low, high],
        "built_epochs": [early, late],
        "scale_m": 100,
    }


def build_settlement_class(run: RegionRun) -> LayerResult:
    from ..data.gee_layers import GHS_SMOD, ghs_native_projection, ghs_settlement_class

    epoch = run.config["population"]["smod_epoch"]
    reduced = reduce_image_over_cells(
        ghs_settlement_class(epoch), run.cells, ["smod_code"], scale=1000, reducer="mode",
        extra_stats=(), crs=ghs_native_projection(), batch_size=run.batch_size,
    )
    return reduced.rename(columns={"smod_code_mode": "smod_code"}), {"asset": GHS_SMOD, "epoch": epoch}


def build_night_lights(run: RegionRun) -> LayerResult:
    from ..data.gee_layers import viirs_annual_radiance

    image, source = viirs_annual_radiance(run.year)
    scale = run.config["night_lights"]["scale_m"]
    reduced = reduce_image_over_cells(
        image, run.cells, ["radiance"], scale=scale, extra_stats=(), crs=run.crs, batch_size=run.batch_size,
    )
    return reduced.rename(columns={"radiance_mean": "radiance"}), {**source, "scale_m": scale}


def build_no2(run: RegionRun) -> LayerResult:
    from ..data.gee_layers import S5P_NO2, s5p_no2_median

    cfg = run.config["air_quality"]
    image, count = s5p_no2_median(run.bbox, tuple(cfg["no2_date_range"]))
    reduced = reduce_image_over_cells(
        image, run.cells, ["no2"], scale=cfg["no2_scale_m"], extra_stats=(), crs=run.crs, batch_size=run.batch_size,
    )
    return reduced.rename(columns={"no2_mean": "no2"}), {
        "asset": S5P_NO2, "band": "tropospheric_NO2_column_number_density",
        "date_range": cfg["no2_date_range"], "image_count": count, "statistic": "median"}


def build_modis_lst(run: RegionRun) -> LayerResult:
    from ..data.gee_layers import MODIS_LST, modis_day_lst

    tier1 = _tiers(run.config["compositing"]["landsat"]["tiers"])[0]
    reduced = reduce_image_over_cells(
        modis_day_lst(run.bbox, tier1), run.cells, ["modis_lst"], scale=1000, extra_stats=(),
        crs=run.crs, batch_size=run.batch_size,
    )
    return reduced.rename(columns={"modis_lst_mean": "modis_lst_k"}), {"asset": MODIS_LST, "date_ranges": tier1}


def build_open_buildings_floors(run: RegionRun) -> LayerResult:
    from ..data.gee_layers import OPEN_BUILDINGS_TEMPORAL, open_buildings_floor_bands

    cfg = run.config["buildings"]
    image = open_buildings_floor_bands(
        run.bbox,
        cfg["open_buildings_temporal_year"],
        cfg["ghsl_residential_floor_height_m"],
        cfg["ghsl_commercial_floor_height_m"],
        cfg["high_rise_threshold_m"],
    )
    reduced = reduce_image_over_cells(
        image, run.cells, ["presence", "presence_floors"], scale=cfg["open_buildings_scale_m"],
        reducer="sum", extra_stats=(), crs=run.crs, batch_size=max(run.batch_size // 4, 16),
    )
    presence = reduced["presence_sum"]
    mean_floors = reduced["presence_floors_sum"] / presence.where(presence > 0)
    return pd.DataFrame({"ob_mean_floors": mean_floors, "ob_presence_sum": presence}), {
        "asset": OPEN_BUILDINGS_TEMPORAL, "year": cfg["open_buildings_temporal_year"],
        "scale_m": cfg["open_buildings_scale_m"]}


def build_ghs_built_volume(run: RegionRun) -> LayerResult:
    """GHS-BUILT-V 3D residential built volume and floor area (m²) interpolated to reference year."""
    from ..data.gee_layers import (
        GHS_BUILT_V,
        ghs_built_volume,
        ghs_native_projection,
    )

    cfg = run.config["population"]
    low, high = cfg["ghs_epochs"]
    image = ghs_built_volume(run.year, low, high)
    reduced = reduce_image_over_cells(
        image,
        run.cells,
        ["built_volume_total", "built_volume_nres", "built_volume_res"],
        scale=100,
        reducer="sum",
        extra_stats=(),
        crs=ghs_native_projection(),
        batch_size=run.batch_size,
    )
    total_m3 = reduced["built_volume_total_sum"].fillna(0.0)
    nres_m3 = reduced["built_volume_nres_sum"].fillna(0.0)
    res_m3 = reduced["built_volume_res_sum"].fillna(0.0)
    ghs_floor_area = res_m3 / 3.0  # 3.0 m standard residential storey height

    table = pd.DataFrame({
        "built_volume_total_m3": total_m3,
        "built_volume_nres_m3": nres_m3,
        "built_volume_res_m3": res_m3,
        "ghs_floor_area_m2": ghs_floor_area,
    })
    return table, {
        "asset": GHS_BUILT_V,
        "year": run.year,
        "epochs": [low, high],
        "scale_m": 100,
    }


def build_topographic_hazard(run: RegionRun) -> LayerResult:
    """Copernicus GLO-30 30 m slope hazardous exceedance share (> 15°) and inverted terrain safety."""
    from ..data.gee_layers import COPERNICUS_DEM_GLO30, topographic_slope_exceedance

    hazard_cfg = run.config.get("topography", {})
    threshold_deg = float(hazard_cfg.get("slope_threshold_degrees", 15.0))
    scale_m = float(hazard_cfg.get("scale_m", 30.0))

    image = topographic_slope_exceedance(run.bbox, crs=run.crs, threshold_degrees=threshold_deg)
    reduced = reduce_image_over_cells(
        image,
        run.cells,
        ["slope_hazard_share"],
        scale=scale_m,
        extra_stats=(),
        crs=run.crs,
        batch_size=run.batch_size,
    )
    hazard_share = reduced["slope_hazard_share_mean"].fillna(0.0).clip(0.0, 1.0)
    safety = (1.0 - hazard_share).clip(0.0, 1.0)
    table = pd.DataFrame({
        "hazard_slope_share": hazard_share,
        "terrain_safety_inv": safety,
    })
    return table, {
        "asset": COPERNICUS_DEM_GLO30,
        "threshold_degrees": threshold_deg,
        "scale_m": scale_m,
    }


# -----------------------------------------------------------------------------
# Local layers
# -----------------------------------------------------------------------------


def ensure_osm_nonres_zones(run: RegionRun) -> Path:
    """Extracts non-residential landuse and amenity polygons from the OSM PBF extract."""
    target = run.path("data/interim/osm_nonres_zones.parquet")
    if target.exists():
        return target
    from pyrosm import OSM

    pbf = ensure_osm_extract(run)
    osm = OSM(pbf.as_posix(), bounding_box=run.bbox)
    lu = osm.get_landuse()
    nonres_lu = {
        "industrial", "commercial", "retail", "military", "railway", "religious", "education",
        "institutional", "port", "garages", "depot", "warehouse", "construction", "landfill", "quarry"
    }
    if lu is not None and not lu.empty:
        lu = lu[lu["landuse"].isin(nonres_lu)][["landuse", "geometry"]]
        lu = lu[lu.geom_type.isin(["Polygon", "MultiPolygon"])]
    else:
        lu = gpd.GeoDataFrame(columns=["landuse", "geometry"], crs="EPSG:4326")

    amen = osm.get_data_by_custom_criteria(
        custom_filter={
            "amenity": [
                "school", "university", "college", "hospital", "marketplace", "place_of_worship",
                "townhall", "police", "prison", "bus_station", "parking"
            ],
            "aeroway": True,
            "shop": ["mall", "supermarket", "department_store"],
        },
        filter_type="keep", keep_nodes=False, keep_ways=True, keep_relations=True
    )
    if amen is not None and not amen.empty:
        amen = amen[amen.geom_type.isin(["Polygon", "MultiPolygon"])]
        amen_col = amen.get("amenity", pd.Series(index=amen.index, dtype=str)).fillna("other").astype(str)
        amen["landuse"] = "amenity:" + amen_col
        amen = amen[["landuse", "geometry"]]
    else:
        amen = gpd.GeoDataFrame(columns=["landuse", "geometry"], crs="EPSG:4326")

    zones = pd.concat([lu, amen], ignore_index=True)
    zones = gpd.GeoDataFrame(zones, crs="EPSG:4326")
    target.parent.mkdir(parents=True, exist_ok=True)
    zones.to_parquet(target)
    return target


def build_buildings(run: RegionRun) -> LayerResult:
    """Per-cell building count, wall/roof footprint area, and hierarchical residential floor area."""
    import duckdb

    path = run.path("data/raw/buildings.parquet").as_posix()
    res = int(run.config["spatial"]["h3_resolution"])
    b_cfg = run.config.get("buildings", {})
    eave_m = float(b_cfg.get("eave_offset_m", 0.5))
    use_cfg = b_cfg.get("use_filter", {})
    comm_min = float(use_cfg.get("min_commercial_retail_size_m2", 200.0))
    large_low_min = float(use_cfg.get("large_low_min_m2", 2500.0))
    large_low_floors = float(use_cfg.get("large_low_max_floors", 3.0))
    rect_min = float(use_cfg.get("rect_warehouse_min_m2", 1000.0))
    rect_rect = float(use_cfg.get("rect_warehouse_min_rectangularity", 0.80))
    rect_floors = float(use_cfg.get("rect_warehouse_max_floors", 2.0))

    zones_path = ensure_osm_nonres_zones(run).as_posix()

    con = duckdb.connect()
    con.install_extension("spatial")
    con.load_extension("spatial")
    con.install_extension("h3", repository="community")
    con.load_extension("h3")
    con.execute("SET geometry_always_xy = true;")

    query = f"""
        WITH b_joined AS (
            SELECT
                printf('%x', h3_latlng_to_cell(ST_Y(ST_Centroid(b.geometry)), ST_X(ST_Centroid(b.geometry)), {res})) AS h3_index,
                ST_Area_Spheroid(b.geometry) as a_roof,
                GREATEST(0.0, ST_Area_Spheroid(b.geometry) - ST_Perimeter_Spheroid(b.geometry) * {eave_m} + 3.14159 * {eave_m * eave_m}) as a_wall,
                b.height,
                COALESCE(b.floor_count, 1) as floor_count,
                CASE
                    WHEN ST_Perimeter_Spheroid(b.geometry) > 0.0 THEN
                        LEAST(1.0, GREATEST(0.0, 4.0 * pi() * ST_Area_Spheroid(b.geometry) / (ST_Perimeter_Spheroid(b.geometry) * ST_Perimeter_Spheroid(b.geometry))))
                    ELSE NULL
                END as compactness,
                CASE
                    WHEN z.landuse IS NOT NULL AND (z.landuse NOT IN ('commercial', 'retail') OR ST_Area_Spheroid(b.geometry) >= {comm_min}) THEN 1
                    WHEN ST_Area_Spheroid(b.geometry) >= {large_low_min} AND COALESCE(b.floor_count, 1) <= {large_low_floors} THEN 1
                    WHEN ST_Area_Spheroid(b.geometry) >= {rect_min} AND (ST_Area(b.geometry) / NULLIF(ST_Area(ST_Envelope(b.geometry)), 0)) >= {rect_rect} AND COALESCE(b.floor_count, 1) <= {rect_floors} THEN 1
                    ELSE 0
                END as is_nonres
            FROM read_parquet('{path}') b
            LEFT JOIN (SELECT landuse, ST_SetCRS(geometry, 'OGC:CRS84') as geometry FROM read_parquet('{zones_path}')) z
            ON ST_Within(ST_Centroid(b.geometry), z.geometry)
        )
        SELECT
            h3_index,
            COUNT(*) AS building_count,
            SUM(a_roof) AS footprint_area_m2,
            SUM(a_wall) AS footprint_wall_m2,
            SUM(CASE WHEN is_nonres = 0 THEN a_wall ELSE 0 END) AS net_res_footprint_m2,
            SUM(CASE WHEN is_nonres = 0 AND height IS NOT NULL THEN a_wall * floor_count ELSE 0 END) AS explicit_floor_area_m2,
            SUM(CASE WHEN is_nonres = 0 AND height IS NULL THEN a_wall ELSE 0 END) AS unknown_height_footprint_m2,
            SUM(CASE WHEN is_nonres = 1 THEN a_wall ELSE 0 END) AS removed_nonres_wall_m2,
            SUM(CASE WHEN is_nonres = 0 THEN 1 ELSE 0 END) AS residential_building_count,
            SUM(CASE WHEN height IS NOT NULL THEN 1 ELSE 0 END) AS buildings_with_height,
            MEDIAN(CASE WHEN is_nonres = 0 THEN compactness ELSE NULL END) AS building_compactness
        FROM b_joined
        GROUP BY 1
    """
    df = con.execute(query).df().set_index("h3_index")
    con.close()
    df = df.reindex(run.cells)
    count_cols = [c for c in df.columns if c != "building_compactness"]
    df[count_cols] = df[count_cols].fillna(0.0)
    df["building_compactness"] = df["building_compactness"].astype(float)
    return df, {
        "source": "data/raw/buildings.parquet",
        "zones_source": zones_path,
        "eave_offset_m": eave_m,
        "assignment": "footprint centroid",
    }


def build_pm25(run: RegionRun) -> LayerResult:
    from ..data.ingest_acag import acag_median_geotiff, find_acag_monthly_files
    from ..data.zonal_local import zonal_stats_local

    files = find_acag_monthly_files(run.path(run.config["air_quality"]["acag_dir"]), run.year)
    tif = acag_median_geotiff(files, run.bbox, run.layer_dir / f"acag_pm25_{run.year}_median.tif")
    stats = zonal_stats_local(tif, run.cells, stats=("mean",), prefix="pm25")
    return stats.rename(columns={"pm25_mean": "pm25"}), {
        "source": "ACAG V6.GL.02.04", "files": [f.name for f in files], "statistic": "median of monthly means"}


def ensure_osm_extract(run: RegionRun) -> Path:
    """Downloads the dated Geofabrik extract named in the region config if not present."""
    url = run.config["accessibility"]["osm_extract_url"]
    target = run.path("data/raw/osm") / url.rsplit("/", 1)[-1]
    if target.exists():
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(target.suffix + ".part")
    logger.info("Downloading %s ...", url)
    with requests.get(url, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        with open(partial, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    partial.rename(target)
    return target


def load_amenity_points(run: RegionRun) -> gpd.GeoDataFrame:
    """Overture amenity points (representative points) with categories, in the region's UTM CRS."""
    import duckdb

    cfg = run.config["accessibility"]
    allowed = list(cfg["amenity_categories"]) + list(cfg.get("open_space_subtypes", []))
    path = run.path("data/raw/overture_amenities.parquet").as_posix()
    con = duckdb.connect()
    con.install_extension("spatial")
    con.load_extension("spatial")
    con.execute("SET geometry_always_xy = true;")
    df = con.execute(f"""
        SELECT category, ST_X(ST_PointOnSurface(geometry)) AS lon, ST_Y(ST_PointOnSurface(geometry)) AS lat
        FROM read_parquet('{path}')
    """).df()
    con.close()
    df = df[df["category"].isin(allowed)]
    gdf = gpd.GeoDataFrame(df[["category"]], geometry=gpd.points_from_xy(df["lon"], df["lat"]), crs="EPSG:4326")
    return gdf.to_crs(run.crs)


def build_accessibility(run: RegionRun) -> LayerResult:
    from ..features.isochrones import (
        calculate_pedestrian_cutoff_meters,
        compute_amenity_accessibility,
        load_osm_walk_network,
    )

    cfg = run.config["accessibility"]
    pbf = ensure_osm_extract(run)
    nodes, edges = load_osm_walk_network(pbf, run.bbox, run.crs)
    pois = load_amenity_points(run)
    centroids = [h3.cell_to_latlng(c) for c in run.cells]
    hex_gdf = gpd.GeoDataFrame(
        {"h3_index": run.cells},
        geometry=gpd.points_from_xy([lng for _, lng in centroids], [lat for lat, _ in centroids]),
        crs="EPSG:4326",
    ).to_crs(run.crs)
    cutoff = calculate_pedestrian_cutoff_meters(cfg["cutoff_minutes"], cfg["walking_speed_kmh"])
    table = compute_amenity_accessibility(
        hex_gdf, pois, nodes, edges, cutoff_meters=cutoff, batch_size=cfg["dijkstra_batch_size"],
    )
    return table, {"osm_extract": pbf.name, "nodes": len(nodes), "edges": len(edges), "pois": len(pois),
                   "cutoff_m": cutoff, "crs": run.crs}


GEE_LAYERS: dict[str, Callable[[RegionRun], LayerResult]] = {
    "sentinel2": build_sentinel2,
    "landsat": build_landsat,
    "water": build_water,
    "vegetation_probability": build_vegetation_probability,
    "population": build_population,
    "settlement_class": build_settlement_class,
    "night_lights": build_night_lights,
    "no2": build_no2,
    "modis_lst": build_modis_lst,
    "open_buildings_floors": build_open_buildings_floors,
    "ghs_built_volume": build_ghs_built_volume,
    "topographic_hazard": build_topographic_hazard,
}
LOCAL_LAYERS: dict[str, Callable[[RegionRun], LayerResult]] = {
    "buildings": build_buildings,
    "pm25": build_pm25,
    "accessibility": build_accessibility,
}


# -----------------------------------------------------------------------------
# Assembly
# -----------------------------------------------------------------------------


def assemble_raw_features(run: RegionRun, layers: dict[str, pd.DataFrame], benchmarks) -> pd.DataFrame:
    """Joins layers and derives the channel source columns, masks and heat island intensity."""
    raw = pd.concat([layers[name] for name in layers], axis=1)
    raw.index.name = "h3_index"

    raw["density_per_km2"] = population_density(raw["population"])
    raw["is_residential"] = residential_mask(
        raw["density_per_km2"], raw["building_count"],
        benchmarks.min_density_per_km2, benchmarks.min_building_count,
    )
    raw["gross_floor_area_m2"] = combine_floor_area(
        raw["explicit_floor_area_m2"], raw["unknown_height_footprint_m2"], raw["ob_mean_floors"]
    )

    # Rescaled GHS residential ratio applied to residual unclassified buildings
    if "built_surface_total_2023_m2" in raw.columns and "removed_nonres_wall_m2" in raw.columns:
        from ..features.building_use import compute_rescaled_ghs_ratio

        res_ratio = compute_rescaled_ghs_ratio(
            ghs_total_m2=raw["built_surface_total_2023_m2"],
            ghs_nres_m2=raw["built_surface_nres_2023_m2"],
            removed_nres_m2=raw["removed_nonres_wall_m2"],
            unclassified_m2=raw["unknown_height_footprint_m2"],
        )
    elif "residential_ratio" in raw.columns:
        res_ratio = raw["residential_ratio"]
    else:
        res_ratio = None

    raw["residential_ratio"] = res_ratio if res_ratio is not None else 1.0
    raw["floor_area_m2"] = combine_floor_area(
        raw["explicit_floor_area_m2"],
        raw["unknown_height_footprint_m2"],
        raw["ob_mean_floors"],
        residential_ratio=res_ratio,
    )
    raw["gross_space_sufficiency_ratio"] = compute_living_space_ratio(
        raw["gross_floor_area_m2"], raw["population"], benchmarks.un_habitat_min_m2
    )

    # If GHS-BUILT-V 3D residential volume is available, derive space sufficiency ratio directly (Ticket 17)
    if "built_volume_res_m3" in raw.columns:
        raw["ghs_floor_area_m2"] = raw["built_volume_res_m3"] / 3.0
        raw["space_sufficiency_ratio"] = compute_living_space_ratio(
            raw["ghs_floor_area_m2"], raw["population"], benchmarks.un_habitat_min_m2
        )
    elif "ghs_floor_area_m2" in raw.columns:
        raw["space_sufficiency_ratio"] = compute_living_space_ratio(
            raw["ghs_floor_area_m2"], raw["population"], benchmarks.un_habitat_min_m2
        )
    else:
        raw["space_sufficiency_ratio"] = compute_living_space_ratio(
            raw["floor_area_m2"], raw["population"], benchmarks.un_habitat_min_m2
        )

    # Residential Plan Area Fraction on GHS residential mask (Ticket 18)
    if "net_res_footprint_m2" in raw.columns:
        raw["residential_plan_area_fraction"] = compute_residential_plan_area_fraction(
            raw["net_res_footprint_m2"], raw.index, raw["is_residential"]
        )
    else:
        raw["residential_plan_area_fraction"] = np.nan

    # Building Compactness (Ticket 19)
    if "building_compactness" not in raw.columns:
        raw["building_compactness"] = np.nan

    # Topographic Slope Safety (Ticket 20)
    if "terrain_safety_inv" not in raw.columns:
        if "hazard_slope_share" in raw.columns:
            raw["terrain_safety_inv"] = compute_terrain_safety(raw["hazard_slope_share"])
        else:
            raw["terrain_safety_inv"] = 1.0

    hi_cfg = run.config["heat_island"]
    background = heat_island_background_mask(
        raw["is_residential"], raw["smod_code"], raw["veg_probability"],
        hi_cfg["background_smod_codes"], hi_cfg["min_veg_probability"],
    )
    raw["is_heat_background"] = background
    raw["heat_island_intensity_k"], background_lst = compute_heat_island_intensity(
        raw["lst_k"], background, hi_cfg["min_background_cells"]
    )
    raw.attrs["heat_background_lst_k"] = background_lst

    centroids = [h3.cell_to_latlng(c) for c in raw.index]
    raw["lat"] = [lat for lat, _ in centroids]
    raw["lon"] = [lng for _, lng in centroids]
    return raw


def _spearman(a: pd.Series, b: pd.Series) -> float | None:
    pair = pd.concat([a, b], axis=1).dropna()
    return float(pair.corr(method="spearman").iloc[0, 1]) if len(pair) > 2 else None


def quality_report(
    run: RegionRun,
    raw: pd.DataFrame,
    scaled: pd.DataFrame,
    benchmarks,
    is_modelled: pd.Series,
) -> dict[str, Any]:
    """Representativeness, coverage, sanity and epoch-gap checks for the Stage 3 report."""
    res = raw["is_residential"]
    accessibility_cfg = run.config["accessibility"]
    tier_shares = {
        prefix: raw.loc[res, f"{prefix}_tier"].value_counts(normalize=True).sort_index().to_dict()
        for prefix in ("s2", "lst")
    }
    report: dict[str, Any] = {
        "region": run.config["project"]["study_area"],
        "reference_year": run.year,
        "benchmarks_version": benchmarks.version,
        "benchmarks_provisional": benchmarks.provisional,
        "cells": len(raw),
        "residential_cells": int(res.sum()),
        "modelled_cells": int(is_modelled.sum()),
        "population_total": float(raw["population"].sum()),
        "window_tier_shares_residential": tier_shares,
        "tier3_share_flag": {k: float(v.get(3, 0.0)) > 0.10 for k, v in tier_shares.items()},
        "clip_shares": clipped_shares(raw, benchmarks, res).reset_index().to_dict(orient="records"),
        "mask_sensitivity": mask_sensitivity(
            raw["density_per_km2"], raw["building_count"], benchmarks.sensitivity_densities_per_km2,
            {"space_sufficiency_ratio": raw["space_sufficiency_ratio"], "amenities_15m": raw["amenities_15m"]},
        ).reset_index().to_dict(orient="records"),
        "epoch_gap_built_surface": built_surface_change_share(
            raw["built_surface_early_m2"], raw["built_surface_late_m2"], res
        ),
        "heat_island": {
            "background_cells": int(raw["is_heat_background"].sum()),
            "background_lst_k": raw.attrs.get("heat_background_lst_k"),
        },
        "sanity_spearman_residential": {
            "ndvi_vs_dw_veg_probability": _spearman(raw.loc[res, "ndvi"], raw.loc[res, "veg_probability"]),
            "landsat_lst_vs_modis_lst": _spearman(raw.loc[res, "lst_k"], raw.loc[res, "modis_lst_k"]),
        },
        "buildings": {
            "footprints_with_height_share": float(raw["buildings_with_height"].sum() / max(raw["building_count"].sum(), 1)),
            "cells_with_open_buildings_floors": int(raw["ob_mean_floors"].notna().sum()),
            "mean_residential_ratio": float(raw.loc[res, "residential_ratio"].mean()) if "residential_ratio" in raw.columns else 1.0,
            "total_wall_area_km2": float(raw["footprint_wall_m2"].sum() / 1e6) if "footprint_wall_m2" in raw.columns else None,
            "removed_nonres_wall_area_km2": float(raw["removed_nonres_wall_m2"].sum() / 1e6) if "removed_nonres_wall_m2" in raw.columns else None,
        },
        "accessibility": {
            "residential_cells_snap_over_limit": int(
                (raw.loc[res, "snap_distance_m"] > accessibility_cfg["max_snap_distance_m"]).sum()
            ),
            "max_snap_distance_m": accessibility_cfg["max_snap_distance_m"],
        },
        "missing_residential_values": scaled[res].isna().sum().to_dict(),
        "lst_range_k": [float(raw["lst_k"].min()), float(raw["lst_k"].max())],
        "layers": layer_provenance(run, [*GEE_LAYERS, *LOCAL_LAYERS]),
    }

    susenas_csv = run.path("data/external/susenas/bps_susenas_housing_2023.csv")
    admin_geojson = run.path("data/interim/admin_boundaries_study_area.geojson")
    if susenas_csv.exists() and admin_geojson.exists():
        from ..analysis.validate_living_space import evaluate_against_susenas

        try:
            eval_table = evaluate_against_susenas(raw, admin_geojson, susenas_csv)
            report["susenas_validation"] = eval_table.to_dict(orient="records")
        except Exception as e:
            logger.warning("Could not evaluate against Susenas: %s", e)
    report["spearman_residential_scaled"] = scaled[res].corr(method="spearman").round(3).to_dict()
    return report


def build_layers(
    config_path: str | Path,
    root: str | Path,
    names: Sequence[str],
    layer_dir: str | Path | None = None,
) -> dict[str, pd.DataFrame]:
    """Builds (or loads from cache) only the named layers, without assembling features."""
    root = Path(root)
    config = load_region_config(config_path)
    cells = generate_h3_grid(config["spatial"]["bbox"], config["spatial"]["h3_resolution"])
    run = RegionRun(config, root, cells, Path(layer_dir) if layer_dir else root / "data" / "interim" / "layers")
    builders = {**GEE_LAYERS, **LOCAL_LAYERS}
    unknown = [n for n in names if n not in builders]
    if unknown:
        raise KeyError(f"Unknown layers {unknown}; choose from {sorted(builders)}")
    if any(n in GEE_LAYERS and not (run.layer_dir / f"{n}.parquet").exists() for n in names):
        from ..data.gee import initialize_ee

        initialize_ee()
    return {n: cached_layer(run, n, builders[n]) for n in names}


def run_stage3(
    config_path: str | Path,
    root: str | Path,
    layer_dir: str | Path | None = None,
    config_dir: str | Path | None = None,
) -> dict[str, Path]:
    """
    Builds the Stage 3 outputs for one region config.

    Parameters
    ----------
    config_path : str | Path
        Per-region measurement settings.
    root : str | Path
        Region data root (reads data/raw, writes data/interim and data/processed).
    layer_dir : str | Path | None
        Layer cache directory (default root/data/interim/layers).
    config_dir : str | Path | None
        Directory holding `benchmarks/` (default: the region config's directory).

    Returns
    -------
    dict[str, Path]
        Paths of the raw table, scaled matrix (parquet, npy), GeoParquet and QA report.
    """
    root = Path(root)
    config = load_region_config(config_path)
    benchmarks = load_benchmarks(
        benchmark_path(config["benchmarks_version"], Path(config_dir) if config_dir else Path(config_path).parent)
    )
    if benchmarks.provisional:
        logger.warning("Benchmarks %s are PROVISIONAL; outputs are provisional (ticket 14).", benchmarks.version)

    cells = generate_h3_grid(config["spatial"]["bbox"], config["spatial"]["h3_resolution"])
    run = RegionRun(
        config=config,
        root=root,
        cells=cells,
        layer_dir=Path(layer_dir) if layer_dir else root / "data" / "interim" / "layers",
    )
    logger.info("Region %s: %d H3 cells.", config["project"]["study_area"], len(cells))

    needs_gee = any(not (run.layer_dir / f"{name}.parquet").exists() for name in GEE_LAYERS)
    if needs_gee:
        from ..data.gee import initialize_ee

        initialize_ee()

    layers = {name: cached_layer(run, name, fn) for name, fn in {**GEE_LAYERS, **LOCAL_LAYERS}.items()}
    raw = assemble_raw_features(run, layers, benchmarks)

    scaled = build_feature_matrix(raw, benchmarks)
    has_complete = complete_feature_mask(scaled)
    is_modelled = raw["is_residential"] & has_complete
    X = fill_for_message_passing(scaled, is_modelled)

    interim = root / "data" / "interim"
    processed = root / "data" / "processed"
    interim.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)

    raw_path = interim / "h3_features_raw.parquet"
    raw.to_parquet(raw_path)

    matrix = scaled.copy()
    matrix["is_residential"] = raw["is_residential"]
    matrix["has_complete_features"] = has_complete
    matrix["is_modelled"] = is_modelled
    n_dim = len(benchmarks.channels)
    matrix_path = processed / f"feature_matrix_{n_dim}d.parquet"
    matrix.to_parquet(matrix_path)
    matrix.to_parquet(processed / "feature_matrix_7d.parquet")
    matrix.to_parquet(processed / "feature_matrix_10d.parquet")
    npy_path = processed / f"feature_matrix_{n_dim}d.npy"
    np.save(npy_path, X)
    np.save(processed / "feature_matrix_7d.npy", X)
    np.save(processed / "feature_matrix_10d.npy", X)

    geo = gpd.GeoDataFrame(
        pd.concat([raw, scaled.add_suffix("_scaled")], axis=1),
        geometry=h3_polygons(cells),
        crs="EPSG:4326",
    )
    geo_path = processed / "h3_hexagons.parquet"
    geo.to_parquet(geo_path)

    qa_path = processed / "stage3_qa.json"
    with open(qa_path, "w", encoding="utf-8") as f:
        json.dump(quality_report(run, raw, scaled, benchmarks, is_modelled), f, indent=2, default=str)

    logger.info("Stage 3 done: %d residential, %d modelled cells.", int(raw["is_residential"].sum()), int(is_modelled.sum()))
    return {"raw": raw_path, "matrix": matrix_path, "npy": npy_path, "geo": geo_path, "qa": qa_path}
