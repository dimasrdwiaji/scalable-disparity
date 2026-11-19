"""
Earth Engine image builders for every raster channel, plus representative-composite tiering.

Implements ADR 0002:
- Sentinel-2 (NDVI, NDBI, BSI) and Landsat 8/9 LST as cloud-masked median composites over a
  seasonal window, with a per-cell window ladder (Tier 1 narrowest) and QA columns
  (clear observations, valid-area fraction, median acquisition day-of-year).
- Dynamic World whole-year water frequency, JRC permanent water.
- VIIRS VNL v2.2 annual radiance, Sentinel-5P tropospheric NO2.
- GHS-POP (interpolated to the reference year), GHS-SMOD, GHS-BUILT-S.
- MODIS daytime LST and Dynamic World vegetation probability (sanity checks).
- Open Buildings 2.5D Temporal floors (height fill for footprints without heights).

All values stay in authentic physical units: indices in [-1, 1], LST in Kelvin, radiance in
nW/cm²/sr, NO2 in mol/m², frequencies in [0, 1]. Scaling happens only in `features/`.
"""

import logging
from collections.abc import Callable, Sequence
from typing import Any

import numpy as np
import pandas as pd

from .gee import compute_valid_fraction, reduce_image_over_cells

logger = logging.getLogger(__name__)

DateRange = tuple[str, str]

S2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"
CLOUD_SCORE_PLUS = "GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED"
LANDSAT_COLLECTIONS = ("LANDSAT/LC08/C02/T1_L2", "LANDSAT/LC09/C02/T1_L2")
DYNAMIC_WORLD = "GOOGLE/DYNAMICWORLD/V1"
JRC_SURFACE_WATER = "JRC/GSW1_4/GlobalSurfaceWater"
VIIRS_ANNUAL = "NOAA/VIIRS/DNB/ANNUAL_V22"
VIIRS_MONTHLY = "NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG"
S5P_NO2 = "COPERNICUS/S5P/OFFL/L3_NO2"
GHS_POP = "JRC/GHSL/P2023A/GHS_POP"
GHS_SMOD = "JRC/GHSL/P2023A/GHS_SMOD_V2-0"
GHS_BUILT_S = "JRC/GHSL/P2023A/GHS_BUILT_S"
GHS_BUILT_V = "JRC/GHSL/P2023A/GHS_BUILT_V"
COPERNICUS_DEM_GLO30 = "COPERNICUS/DEM/GLO30_2024_1"
MODIS_LST = "MODIS/061/MOD11A2"
OPEN_BUILDINGS_TEMPORAL = "GOOGLE/Research/open-buildings-temporal/v1"

# Landsat Collection 2 Level-2 surface temperature scaling (USGS)
LANDSAT_ST_SCALE = 0.00341802
LANDSAT_ST_OFFSET = 149.0
# QA_PIXEL bits: 0 fill, 1 dilated cloud, 2 cirrus, 3 cloud, 4 cloud shadow
LANDSAT_QA_REJECT_BITS = (1 << 0) | (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4)
DYNAMIC_WORLD_WATER_LABEL = 0


# -----------------------------------------------------------------------------
# Window ladder (pure)
# -----------------------------------------------------------------------------


def tier_passes(
    n_clear: pd.Series,
    valid_frac: pd.Series,
    min_clear: float,
    min_valid_frac: float,
) -> pd.Series:
    """Cells whose composite is representative: enough clear observations and valid area."""
    return (n_clear.fillna(0.0) >= min_clear) & (valid_frac.fillna(0.0) >= min_valid_frac)


def select_window_tier(
    tier_tables: Sequence[pd.DataFrame],
    value_cols: Sequence[str],
    min_clear: float,
    min_valid_frac: float,
) -> pd.DataFrame:
    """
    Picks, per cell, the narrowest window tier whose composite is representative.

    Each tier table has `value_cols` plus `n_clear`, `valid_frac` and `median_doy`, indexed
    by H3 cell. Tiers are ordered narrowest first. A cell that fails every tier gets NaN
    values and tier 0.

    Parameters
    ----------
    tier_tables : Sequence[pd.DataFrame]
        Per-tier reduction tables (a later tier may cover only the cells still failing).
    value_cols : Sequence[str]
        Channel value columns to carry through.
    min_clear : float
        Minimum median clear observations per pixel.
    min_valid_frac : float
        Minimum share of the cell area with a valid composite pixel.

    Returns
    -------
    pd.DataFrame
        `value_cols`, `n_clear`, `valid_frac`, `median_doy` and `tier` per cell.
    """
    if not tier_tables:
        raise ValueError("At least one tier table is required")
    cells = tier_tables[0].index
    qa_cols = ["n_clear", "valid_frac", "median_doy"]
    out = pd.DataFrame(np.nan, index=cells, columns=[*value_cols, *qa_cols])
    out["tier"] = 0
    remaining = pd.Series(True, index=cells)

    for tier_number, table in enumerate(tier_tables, start=1):
        table = table.reindex(cells)
        passes = tier_passes(table["n_clear"], table["valid_frac"], min_clear, min_valid_frac)
        take = remaining & passes
        out.loc[take, [*value_cols, *qa_cols]] = table.loc[take, [*value_cols, *qa_cols]].to_numpy()
        out.loc[take, "tier"] = tier_number
        remaining &= ~take

    # Failed cells keep the widest tier's QA so the report can show why they failed
    last = tier_tables[-1].reindex(cells)
    out.loc[remaining, qa_cols] = last.loc[remaining, qa_cols].to_numpy()
    out["tier"] = out["tier"].astype(int)
    return out


def tier_table_from_reduction(
    reduced: pd.DataFrame,
    value_bands: Sequence[str],
    scale_m: float,
) -> pd.DataFrame:
    """
    Converts a `reduce_image_over_cells` result for a QA composite into a tier table.

    Expects `<band>_mean` and `<band>_count` for value bands and `n_clear_median`,
    `median_doy_median` for the QA bands.
    """
    table = pd.DataFrame(index=reduced.index)
    for band in value_bands:
        table[band] = reduced[f"{band}_mean"]
    table["n_clear"] = reduced["n_clear_median"]
    table["median_doy"] = reduced["median_doy_median"]
    table["valid_frac"] = compute_valid_fraction(reduced[f"{value_bands[0]}_count"], scale_m)
    return table


# -----------------------------------------------------------------------------
# Collection builders (Earth Engine)
# -----------------------------------------------------------------------------


def _region(bbox: Sequence[float]) -> Any:
    import ee

    return ee.Geometry.Rectangle(list(bbox), proj="EPSG:4326", geodesic=False)


def _with_doy(image: Any, mask: Any) -> Any:
    import ee

    doy = ee.Image.constant(image.date().getRelative("day", "year").add(1)).toInt16()
    return doy.updateMask(mask).rename("doy")


def _merge_date_ranges(builder: Callable[[DateRange], Any], date_ranges: Sequence[DateRange]) -> Any:
    collection = builder(date_ranges[0])
    for date_range in date_ranges[1:]:
        collection = collection.merge(builder(date_range))
    return collection


def sentinel2_index_collection(
    bbox: Sequence[float],
    date_ranges: Sequence[DateRange],
    cs_cdf_threshold: float = 0.60,
) -> Any:
    """
    Per-observation NDVI, NDBI and BSI from cloud-masked Sentinel-2 L2A (harmonized).

    Clear pixels are those with Cloud Score+ `cs_cdf >= cs_cdf_threshold`. Indices are
    computed per observation, before compositing.
    """
    import ee

    region = _region(bbox)
    cloud_score = ee.ImageCollection(CLOUD_SCORE_PLUS)

    def build(date_range: DateRange) -> Any:
        return (
            ee.ImageCollection(S2_COLLECTION)
            .filterBounds(region)
            .filterDate(*date_range)
            .linkCollection(cloud_score, ["cs_cdf"])
        )

    def to_indices(img: Any) -> Any:
        clear = img.select("cs_cdf").gte(cs_cdf_threshold)
        ndvi = img.normalizedDifference(["B8", "B4"]).rename("ndvi")
        ndbi = img.normalizedDifference(["B11", "B8"]).rename("ndbi")
        bsi = img.expression(
            "((s + r) - (n + b)) / ((s + r) + (n + b))",
            {"s": img.select("B11"), "r": img.select("B4"), "n": img.select("B8"), "b": img.select("B2")},
        ).rename("bsi")
        nir_gray = img.select("B8").unitScale(0, 5000).multiply(63).round().clamp(0, 63).toUint8().rename("nir_gray")
        return (
            ee.Image.cat([ndvi, ndbi, bsi, nir_gray]).updateMask(clear)
            .addBands(_with_doy(img, clear))
            .copyProperties(img, ["system:time_start"])
        )

    return _merge_date_ranges(build, date_ranges).map(to_indices)


def sentinel2_residential_glcm_image(
    bbox: Sequence[float],
    date_ranges: Sequence[DateRange],
    year: int = 2023,
    epoch_low: int = 2020,
    epoch_high: int = 2025,
    cs_cdf_threshold: float = 0.60,
    glcm_size: int = 3,
    ndvi_max: float = 0.35,
) -> Any:
    """
    10 m Sentinel-2 GLCM texture (`s2_res_glcm_contrast`, `s2_res_glcm_homogeneity`) masked
    strictly to residential built-up pixels (`ghs_res > 0` and `ndvi < ndvi_max`).
    """
    collection = sentinel2_index_collection(bbox, date_ranges, cs_cdf_threshold)
    ndvi_med = collection.select("ndvi").median()
    gray = collection.select("nir_gray").median().round().toUint8().rename("gray")
    glcm = gray.glcmTexture(size=glcm_size)
    ghs = ghs_residential_built_bands(year, epoch_low, epoch_high)
    res_built = ghs.select("ghs_built_total").subtract(ghs.select("ghs_built_nres")).gt(0)
    mask = res_built.And(ndvi_med.lt(ndvi_max))
    contrast = glcm.select("gray_contrast").rename("s2_res_glcm_contrast").updateMask(mask)
    homogeneity = glcm.select("gray_idm").rename("s2_res_glcm_homogeneity").updateMask(mask)
    return contrast.addBands(homogeneity)


def ghs_residential_built_bands(
    year: int,
    epoch_low: int = 2020,
    epoch_high: int = 2025,
) -> Any:
    """GHS-BUILT-S total and non-residential built surface (m² per 100 m pixel) interpolated to `year`."""
    import ee

    weight = interpolation_weight(year, epoch_low, epoch_high)
    low_tot = ee.Image(f"{GHS_BUILT_S}/{epoch_low}").select("built_surface").max(0)
    high_tot = ee.Image(f"{GHS_BUILT_S}/{epoch_high}").select("built_surface").max(0)
    total = low_tot.multiply(1.0 - weight).add(high_tot.multiply(weight)).rename("ghs_built_total")

    low_nres = ee.Image(f"{GHS_BUILT_S}/{epoch_low}").select("built_surface_nres").max(0)
    high_nres = ee.Image(f"{GHS_BUILT_S}/{epoch_high}").select("built_surface_nres").max(0)
    nres = low_nres.multiply(1.0 - weight).add(high_nres.multiply(weight)).rename("ghs_built_nres")
    return total.addBands(nres)


def landsat_lst_collection(
    bbox: Sequence[float],
    date_ranges: Sequence[DateRange],
    max_st_uncertainty_k: float = 3.0,
    min_lst_k: float | None = 273.15,
) -> Any:
    """
    Per-observation Landsat 8/9 surface temperature (K) with QA_PIXEL and ST_QA masking.

    LST = ST_B10 × 0.00341802 + 149.0. Fill, dilated cloud, cirrus, cloud and shadow are
    removed, as are pixels whose ST_QA uncertainty exceeds `max_st_uncertainty_k` or whose
    brightness-inverted surface temperature drops below `min_lst_k` (e.g. corrupt ~150 K
    TIRS scan-line/fill artifacts or unmasked cloud tops).
    """
    import ee

    region = _region(bbox)

    def build(date_range: DateRange) -> Any:
        merged = ee.ImageCollection(LANDSAT_COLLECTIONS[0]).filterBounds(region).filterDate(*date_range)
        for coll_id in LANDSAT_COLLECTIONS[1:]:
            merged = merged.merge(
                ee.ImageCollection(coll_id).filterBounds(region).filterDate(*date_range)
            )
        return merged

    def to_lst(img: Any) -> Any:
        clear = img.select("QA_PIXEL").bitwiseAnd(LANDSAT_QA_REJECT_BITS).eq(0)
        certain = img.select("ST_QA").multiply(0.01).lte(max_st_uncertainty_k)
        lst = img.select("ST_B10").multiply(LANDSAT_ST_SCALE).add(LANDSAT_ST_OFFSET).rename("lst")
        ok = clear.And(certain)
        if min_lst_k is not None:
            ok = ok.And(lst.gte(min_lst_k))
        return lst.updateMask(ok).addBands(_with_doy(img, ok)).copyProperties(img, ["system:time_start"])

    return _merge_date_ranges(build, date_ranges).map(to_lst)


def composite_with_qa(collection: Any, value_bands: Sequence[str]) -> Any:
    """
    Median composite of `value_bands` plus QA bands `n_clear` (clear observations per pixel)
    and `median_doy` (median acquisition day-of-year of contributing observations).
    """
    median = collection.select(list(value_bands)).median()
    n_clear = collection.select(value_bands[0]).count().rename("n_clear")
    median_doy = collection.select("doy").median().rename("median_doy")
    return median.addBands(n_clear).addBands(median_doy)


def reduce_tiered_composite(
    collection_builder: Callable[[Sequence[DateRange]], Any],
    value_bands: Sequence[str],
    tiers: Sequence[Sequence[DateRange]],
    cells: Sequence[str],
    scale_m: float,
    min_clear: float,
    min_valid_frac: float,
    crs: str = "EPSG:32748",
    batch_size: int = 250,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """
    Runs the window ladder: reduces Tier 1 for all cells, then each wider tier only for the
    cells still failing, and selects the narrowest representative tier per cell.

    Returns
    -------
    tuple[pd.DataFrame, list[dict[str, Any]]]
        The tier-selected table and a provenance record per tier (date ranges, scene count,
        cells attempted).
    """
    remaining = list(cells)
    tier_tables: list[pd.DataFrame] = []
    provenance: list[dict[str, Any]] = []

    for tier_number, date_ranges in enumerate(tiers, start=1):
        collection = collection_builder(date_ranges)
        scene_count = int(collection.size().getInfo())
        provenance.append({
            "tier": tier_number,
            "date_ranges": [list(r) for r in date_ranges],
            "scene_count": scene_count,
            "cells_attempted": len(remaining),
        })
        logger.info("Tier %d: %d scenes, %d cells.", tier_number, scene_count, len(remaining))
        if not remaining:
            tier_tables.append(pd.DataFrame(columns=[*value_bands, "n_clear", "valid_frac", "median_doy"]))
            continue

        image = composite_with_qa(collection, value_bands)
        reduced = reduce_image_over_cells(
            image,
            remaining,
            bands=[*value_bands, "n_clear", "median_doy"],
            scale=scale_m,
            reducer="mean",
            extra_stats=("median", "count"),
            crs=crs,
            batch_size=batch_size,
        )
        table = tier_table_from_reduction(reduced, value_bands, scale_m)
        tier_tables.append(table)
        passes = tier_passes(table["n_clear"], table["valid_frac"], min_clear, min_valid_frac)
        remaining = list(table.index[~passes])

    full_index = pd.Index(list(cells), name="h3_index")
    tier_tables = [t.reindex(full_index) for t in tier_tables]
    return select_window_tier(tier_tables, value_bands, min_clear, min_valid_frac), provenance


def dynamic_world_water_frequency(
    bbox: Sequence[float],
    date_range: DateRange,
    min_observations: int = 10,
) -> tuple[Any, Any]:
    """
    Per-pixel share of observations classed as water (Dynamic World label 0) over a window,
    masked where fewer than `min_observations` exist.

    Returns
    -------
    tuple[ee.Image, ee.ImageCollection]
        Image with bands `water_frequency` and `water_n_obs`, and the source collection.
    """
    import ee

    collection = ee.ImageCollection(DYNAMIC_WORLD).filterBounds(_region(bbox)).filterDate(*date_range)
    labels = collection.select("label")
    n_obs = labels.count().rename("water_n_obs")
    water = labels.map(lambda img: img.eq(DYNAMIC_WORLD_WATER_LABEL)).sum()
    frequency = water.divide(n_obs).rename("water_frequency")
    valid = n_obs.gte(min_observations)
    return frequency.updateMask(valid).addBands(n_obs.updateMask(valid)), collection


def dynamic_world_vegetation_probability(bbox: Sequence[float], date_ranges: Sequence[DateRange]) -> Any:
    """Median Dynamic World tree + grass + crop probability (`veg_probability`) over windows."""
    import ee

    region = _region(bbox)

    def build(date_range: DateRange) -> Any:
        return ee.ImageCollection(DYNAMIC_WORLD).filterBounds(region).filterDate(*date_range)

    collection = _merge_date_ranges(build, date_ranges)
    veg = collection.map(lambda img: img.select("trees").add(img.select("grass")).add(img.select("crops")))
    return veg.median().rename("veg_probability")


def permanent_water(min_occurrence: float = 90.0) -> Any:
    """Binary JRC Global Surface Water mask (`permanent_water`) where occurrence >= min_occurrence."""
    import ee

    occurrence = ee.Image(JRC_SURFACE_WATER).select("occurrence")
    return occurrence.gte(min_occurrence).unmask(0).rename("permanent_water")


def viirs_annual_radiance(year: int) -> tuple[Any, dict[str, Any]]:
    """
    VIIRS VNL v2.2 annual `median_masked` radiance for `year` (nW/cm²/sr), falling back to the
    median of that year's monthly VCMSLCFG `avg_rad` composites when the annual is missing.
    Negative values are clipped to 0.
    """
    import ee

    start, end = f"{year}-01-01", f"{year + 1}-01-01"
    annual = ee.ImageCollection(VIIRS_ANNUAL).filterDate(start, end)
    if int(annual.size().getInfo()) > 0:
        image = annual.first().select("median_masked")
        source = {"asset": VIIRS_ANNUAL, "band": "median_masked", "year": year}
    else:
        monthly = ee.ImageCollection(VIIRS_MONTHLY).filterDate(start, end)
        image = monthly.select("avg_rad").median()
        source = {"asset": VIIRS_MONTHLY, "band": "avg_rad", "year": year,
                  "months": int(monthly.size().getInfo()), "fallback": True}
    return image.max(0).rename("radiance"), source


def s5p_no2_median(bbox: Sequence[float], date_range: DateRange) -> tuple[Any, int]:
    """Median Sentinel-5P OFFL L3 tropospheric NO2 column (mol/m²) and its image count."""
    import ee

    collection = (
        ee.ImageCollection(S5P_NO2)
        .filterBounds(_region(bbox))
        .filterDate(*date_range)
        .select("tropospheric_NO2_column_number_density")
    )
    return collection.median().rename("no2"), int(collection.size().getInfo())


def interpolation_weight(year: int, epoch_low: int, epoch_high: int) -> float:
    """Linear weight of the upper epoch for interpolating to `year` (0 at epoch_low, 1 at epoch_high)."""
    if not epoch_low <= year <= epoch_high or epoch_low == epoch_high:
        raise ValueError(f"{year} is not within [{epoch_low}, {epoch_high}]")
    return (year - epoch_low) / (epoch_high - epoch_low)


def ghs_population(year: int, epoch_low: int = 2020, epoch_high: int = 2025) -> Any:
    """GHS-POP R2023A 100 m population count linearly interpolated to `year` (`population`)."""
    import ee

    weight = interpolation_weight(year, epoch_low, epoch_high)
    low = ee.Image(f"{GHS_POP}/{epoch_low}").select("population_count").max(0)
    high = ee.Image(f"{GHS_POP}/{epoch_high}").select("population_count").max(0)
    return low.multiply(1 - weight).add(high.multiply(weight)).rename("population")


def ghs_native_projection() -> Any:
    """Native projection (Mollweide, 100 m) of GHS R2023A layers, for extensive reductions."""
    import ee

    return ee.Image(f"{GHS_POP}/2020").projection()


def ghs_settlement_class(epoch: int) -> Any:
    """GHS-SMOD settlement model class (`smod_code`) for an epoch."""
    import ee

    return ee.Image(f"{GHS_SMOD}/{epoch}").select("smod_code")


def ghs_built_surface(epoch: int, non_residential: bool = False) -> Any:
    """GHS-BUILT-S built-up surface (m² per 100 m pixel) for an epoch.
    Selects 'built_surface_nres' if non_residential is True, else 'built_surface'.
    """
    import ee

    band = "built_surface_nres" if non_residential else "built_surface"
    return ee.Image(f"{GHS_BUILT_S}/{epoch}").select(band)


def ghs_built_volume(year: int, epoch_low: int = 2020, epoch_high: int = 2025) -> Any:
    """GHS-BUILT-V R2023A 100 m built-up volume (m³) linearly interpolated to `year`.

    Returns an ee.Image with bands:
    - 'built_volume_total': total built-up volume (m³)
    - 'built_volume_nres': non-residential built-up volume (m³)
    - 'built_volume_res': net residential built-up volume max(0, total - nres) (m³)
    """
    import ee

    weight = interpolation_weight(year, epoch_low, epoch_high)
    low_total = ee.Image(f"{GHS_BUILT_V}/{epoch_low}").select("built_volume_total").max(0)
    high_total = ee.Image(f"{GHS_BUILT_V}/{epoch_high}").select("built_volume_total").max(0)
    total = low_total.multiply(1.0 - weight).add(high_total.multiply(weight)).rename("built_volume_total")

    low_nres = ee.Image(f"{GHS_BUILT_V}/{epoch_low}").select("built_volume_nres").max(0)
    high_nres = ee.Image(f"{GHS_BUILT_V}/{epoch_high}").select("built_volume_nres").max(0)
    nres = low_nres.multiply(1.0 - weight).add(high_nres.multiply(weight)).rename("built_volume_nres")

    res = total.subtract(nres).max(0).rename("built_volume_res")
    return total.addBands(nres).addBands(res)


def topographic_slope_exceedance(
    bbox: Sequence[float],
    crs: str = "EPSG:3857",
    threshold_degrees: float = 15.0,
) -> Any:
    """Copernicus GLO-30 30 m DEM slope exceedance mask (> threshold_degrees).

    Reprojects DEM to `crs` at 30 m so terrain slope is computed in meters rather than degrees.
    Returns an ee.Image with band 'slope_hazard_share' (1 where slope > threshold, else 0).
    Reducing with mean over an H3 cell computes the area share of hazardous slope.
    """
    import ee

    region = _region(bbox)
    dem = (
        ee.ImageCollection(COPERNICUS_DEM_GLO30)
        .filterBounds(region)
        .select("DEM")
        .mosaic()
        .reproject(crs=crs, scale=30)
    )
    slope = ee.Terrain.slope(dem)
    return slope.gt(threshold_degrees).rename("slope_hazard_share")


def modis_day_lst(bbox: Sequence[float], date_ranges: Sequence[DateRange]) -> Any:
    """Mean MODIS MOD11A2 daytime LST (K, `modis_lst`) over the windows (sanity check)."""
    import ee

    region = _region(bbox)

    def build(date_range: DateRange) -> Any:
        return ee.ImageCollection(MODIS_LST).filterBounds(region).filterDate(*date_range)

    collection = _merge_date_ranges(build, date_ranges)
    return collection.select("LST_Day_1km").mean().multiply(0.02).rename("modis_lst")


ERA5_LAND_MONTHLY = "ECMWF/ERA5_LAND/MONTHLY_AGGR"


def monthly_precipitation_climatology(
    bbox: Sequence[float],
    start_year: int,
    end_year: int,
) -> list[float]:
    """
    Mean ERA5-Land total precipitation (m) per calendar month over the bbox, averaged over
    [start_year, end_year]. Used to derive each reference city's dry-season window.
    """
    import ee

    region = _region(bbox)
    collection = ee.ImageCollection(ERA5_LAND_MONTHLY).filterDate(f"{start_year}-01-01", f"{end_year + 1}-01-01")
    values = []
    for month in range(1, 13):
        image = collection.filter(ee.Filter.calendarRange(month, month, "month")).select("total_precipitation_sum").mean()
        stat = image.reduceRegion(ee.Reducer.mean(), region, scale=11132, bestEffort=True).getInfo()
        values.append(float(stat.get("total_precipitation_sum") or np.nan))
    return values


def open_buildings_floor_bands(
    bbox: Sequence[float],
    year: int,
    residential_floor_height_m: float = 3.0,
    commercial_floor_height_m: float = 3.6,
    high_rise_threshold_m: float = 35.0,
) -> Any:
    """
    Open Buildings 2.5D Temporal bands for presence-weighted mean floors per cell.

    Floors follow the GLOSSARY hierarchy: floor(h / 3.0) below `high_rise_threshold_m`,
    floor(h / 3.6) above, minimum 1. Returns bands `presence` and `presence_floors`
    (presence × floors); reduce both with `sum` and divide to get mean floors per cell.
    """
    import ee

    collection = (
        ee.ImageCollection(OPEN_BUILDINGS_TEMPORAL)
        .filterBounds(_region(bbox))
        .filterDate(f"{year}-01-01", f"{year + 1}-01-01")
    )
    mosaic = collection.mosaic()
    height = mosaic.select("building_height")
    presence = mosaic.select("building_presence").rename("presence")
    floors = (
        height.divide(residential_floor_height_m)
        .where(height.gte(high_rise_threshold_m), height.divide(commercial_floor_height_m))
        .floor()
        .max(1)
    )
    return presence.addBands(presence.multiply(floors).rename("presence_floors"))
