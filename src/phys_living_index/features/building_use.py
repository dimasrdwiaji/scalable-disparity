"""
Hierarchical building-level functional use classification and residential floor area filtering.

Addresses overestimation of residential floor area by identifying commercial, industrial,
and institutional buildings from OSM land use/amenity zones, POI intersections, GHS-BUILT-C,
and geometric shape signatures.
"""


import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry.base import BaseGeometry


def compute_rectangularity(geometry: BaseGeometry) -> float:
    """
    Computes the rectangularity index (area / minimum rotated rectangle area) in [0.0, 1.0].
    """
    if geometry is None or geometry.is_empty:
        return 0.0
    area = geometry.area
    if area <= 0.0:
        return 0.0
    min_rect = geometry.minimum_rotated_rectangle
    rect_area = min_rect.area
    if rect_area <= 0.0:
        return 0.0
    return float(min(1.0, max(0.0, area / rect_area)))


def compute_isoperimetric_compactness(
    area: float | pd.Series,
    perimeter: float | pd.Series,
) -> float | pd.Series:
    """
    Computes isoperimetric compactness: 4 * pi * area / (perimeter ** 2), bounded in [0.0, 1.0].

    - Circular shape: compactness = 1.0
    - Square shape: compactness = pi / 4 ~ 0.785
    - High regularity (formal planned subdivisions): compactness >= 0.65 - 0.85
    - Organic informal accretion (kampungs, slums): compactness <= 0.40 - 0.45
    """
    if isinstance(area, pd.Series):
        perim_sq = perimeter ** 2
        with np.errstate(divide="ignore", invalid="ignore"):
            c = (4.0 * np.pi * area) / perim_sq.where(perim_sq > 0)
        return c.fillna(0.0).clip(lower=0.0, upper=1.0)

    if perimeter <= 0.0 or area <= 0.0:
        return 0.0
    val = (4.0 * np.pi * area) / (perimeter ** 2)
    return float(min(1.0, max(0.0, val)))


def classify_osm_zones(
    buildings_gdf: gpd.GeoDataFrame,
    osm_zones_gdf: gpd.GeoDataFrame,
    commercial_min_size: float = 200.0,
    area_col: str = "footprint_m2",
) -> pd.Series:
    """
    Identifies non-residential buildings located inside OSM land-use and amenity zones.

    - Industrial, educational, religious, health, government, infrastructure, and transport
      zones apply to buildings of any size.
    - Commercial and retail zones apply only to footprints >= `commercial_min_size` to preserve
      residential dwelling upper floors in mixed shophouse (ruko) corridors.
    """
    if osm_zones_gdf.empty or buildings_gdf.empty:
        return pd.Series(False, index=buildings_gdf.index)

    joined = gpd.sjoin(
        buildings_gdf[["geometry", area_col]],
        osm_zones_gdf[["geometry", "landuse"]],
        predicate="within",
        how="left",
    )
    # Deduplicate in case a building falls on the boundary of multiple zones
    joined = joined[~joined.index.duplicated(keep="first")]

    in_zone = joined["landuse"].notna()
    is_comm = joined["landuse"].isin(["commercial", "retail", "amenity:marketplace"])
    large_enough = joined[area_col] >= commercial_min_size

    flag = in_zone & (~is_comm | large_enough)
    return flag.reindex(buildings_gdf.index).fillna(False)


def classify_poi_intersection(
    footprints_gdf: gpd.GeoDataFrame,
    nonres_pois_gdf: gpd.GeoDataFrame,
    min_size: float = 150.0,
    area_col: str = "footprint_m2",
) -> pd.Series:
    """
    Flags buildings that contain a verified non-residential POI (school, office, hospital, etc.)
    and have a footprint >= `min_size`.
    """
    if nonres_pois_gdf.empty or footprints_gdf.empty:
        return pd.Series(False, index=footprints_gdf.index)

    joined = gpd.sjoin(
        footprints_gdf[["geometry", area_col]],
        nonres_pois_gdf[["geometry"]],
        predicate="contains",
        how="left",
    )
    joined = joined[~joined.index.duplicated(keep="first")]
    has_poi = joined["index_right"].notna()
    large_enough = joined[area_col] >= min_size

    return (has_poi & large_enough).reindex(footprints_gdf.index).fillna(False)


def classify_large_low_shape(
    areas: pd.Series,
    floors: pd.Series,
    rectangularities: pd.Series,
    large_low_min_m2: float = 2500.0,
    large_low_max_floors: float = 3.0,
    rect_min_m2: float = 1000.0,
    rect_min_rect: float = 0.85,
    rect_max_floors: float = 2.0,
    high_rise_exemption: float = 6.0,
) -> pd.Series:
    """
    Flags large horizontal footprints characteristic of logistics warehouses, manufacturing plants,
    and hypermarkets, while exempting high-rise residential apartment towers.
    """
    exempt = floors >= high_rise_exemption

    is_large_low = (areas >= large_low_min_m2) & (floors <= large_low_max_floors)
    is_rect_warehouse = (areas >= rect_min_m2) & (rectangularities >= rect_min_rect) & (floors <= rect_max_floors)

    return (~exempt) & (is_large_low | is_rect_warehouse)


def combine_hierarchical_rules(
    is_osm_nonres: pd.Series,
    is_poi_nonres: pd.Series,
    is_shape_nonres: pd.Series,
    is_small_home: pd.Series,
) -> tuple[pd.Series, pd.Series]:
    """
    Combines hierarchical rules where the first rule that triggers determines the classification.

    Priority:
    1. Rule 1: OSM non-residential zone -> non_residential
    2. Rule 2: Non-residential POI inside polygon -> non_residential
    3. Rule 3: Large-and-low / rectangular warehouse shape -> non_residential
    4. Rule 4: Small home confirmation (< 200 m2) -> residential
    5. Default -> unclassified (subject to residual GHS scaling)

    Returns
    -------
    tuple[pd.Series, pd.Series]
        (use_class, rule_name)
    """
    idx = is_osm_nonres.index
    use_class = pd.Series("unclassified", index=idx, dtype="object")
    rule_name = pd.Series("none", index=idx, dtype="object")

    # Rule 4: Small home
    small_mask = is_small_home & (use_class == "unclassified")
    use_class[small_mask] = "residential"
    rule_name[small_mask] = "small_home"

    # Rule 3: Large-and-low
    shape_mask = is_shape_nonres
    use_class[shape_mask] = "non_residential"
    rule_name[shape_mask] = "large_low_shape"

    # Rule 2: POI inside
    poi_mask = is_poi_nonres
    use_class[poi_mask] = "non_residential"
    rule_name[poi_mask] = "poi_contained"

    # Rule 1: OSM zone (highest precedence)
    osm_mask = is_osm_nonres
    use_class[osm_mask] = "non_residential"
    rule_name[osm_mask] = "osm_nonres_zone"

    return use_class, rule_name


def compute_rescaled_ghs_ratio(
    ghs_total_m2: pd.Series,
    ghs_nres_m2: pd.Series,
    removed_nres_m2: pd.Series,
    unclassified_m2: pd.Series,
) -> pd.Series:
    """
    Rescales GHS 100 m residential ratio so that non-residential stock already excised
    by building-level rules is not subtracted a second time.

    r* = 1.0 - (max(0, ghs_nres - removed_nres) / unclassified_m2)
    clamped to [0.0, 1.0].
    """
    residual_nres = (ghs_nres_m2 - removed_nres_m2).clip(lower=0.0)
    unclass = unclassified_m2.where(unclassified_m2 > 0)
    ratio = 1.0 - (residual_nres / unclass)
    return ratio.fillna(1.0).clip(lower=0.0, upper=1.0)
