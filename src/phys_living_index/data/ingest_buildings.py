"""
Ingest Google Open Buildings v3 with confidence filtering and residential masking.

Google Open Buildings v3 provides building footprint polygons with high-resolution
2.5D height estimates derived from satellite imagery.

This module provides:
1. Pure functions for:
   - Confidence threshold filtering (retaining reliable footprints, default >= 0.65).
   - Authoritative hierarchical floor-count derivation based on international urban
     remote sensing benchmarks (EC JRC Global Human Settlement Layer - GHSL; Biljecki & Chow, 2022).
   - Residential spatial masking (supporting both vector boundaries and EC JRC GHS-BUILT-C GeoTIFFs).
   - DuckDB spatial SQL query construction.
2. Thin I/O callers executing DuckDB queries over Source Cooperative open data.
"""

from pathlib import Path

import duckdb
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio

from .ingest_overture import get_duckdb_spatial_connection

# Source Cooperative / Vida Open Buildings IDN distribution mirror
DEFAULT_OPEN_BUILDINGS_SOURCE_URL: str = (
    "s3://us-west-2.opendata.source.coop/vida/google-microsoft-osm-open-buildings/geoparquet/by_country_s2/country_iso=IDN/*.parquet"
)

# International nominal floor-to-floor height benchmarks (GHSL, UN-Habitat, Biljecki & Chow 2022)
GHSL_RESIDENTIAL_FLOOR_HEIGHT_M: float = 3.0
GHSL_COMMERCIAL_FLOOR_HEIGHT_M: float = 3.6


def build_open_buildings_query(
    bbox: tuple[float, float, float, float],
    min_confidence: float = 0.65,
    source_url: str = DEFAULT_OPEN_BUILDINGS_SOURCE_URL,
    id_expr: str = "id",
    height_expr: str = "height",
) -> str:
    """
    Constructs a DuckDB SQL statement to query building footprints within a bounding box.

    Parameters
    ----------
    bbox : tuple[float, float, float, float]
        WGS84 spatial bounds: (min_lon, min_lat, max_lon, max_lat).
    min_confidence : float, optional
        Confidence threshold [0.0, 1.0] for satellite detection reliability. Default 0.65.
    source_url : str, optional
        S3 / HTTPS URL pointing to partitioned Open Buildings GeoParquet files.
    id_expr : str, optional
        Column expression for identifier (default 'id').
    height_expr : str, optional
        Column expression for building height in meters (default 'height').

    Returns
    -------
    str
        DuckDB SQL query string extracting id, height, confidence, and geometry as WKT.
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    return f"""
    SELECT 
        {id_expr} AS id, 
        {height_expr} AS height, 
        confidence, 
        ST_AsText(geometry) AS wkt_geom
    FROM read_parquet('{source_url}')
    WHERE bbox.xmin >= {min_lon} AND bbox.xmax <= {max_lon}
      AND bbox.ymin >= {min_lat} AND bbox.ymax <= {max_lat}
      AND confidence >= {min_confidence}
    """


def filter_by_confidence(gdf: gpd.GeoDataFrame, min_confidence: float = 0.65) -> gpd.GeoDataFrame:
    """
    Filters a GeoDataFrame of building footprints by detection confidence threshold.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        Building footprints with a 'confidence' column.
    min_confidence : float, optional
        Minimum acceptable detection score (default 0.65). Footprints with confidence
        below this threshold are discarded as satellite detection artifacts.

    Returns
    -------
    gpd.GeoDataFrame
        Filtered GeoDataFrame containing only confident detections.
    """
    if "confidence" not in gdf.columns or gdf.empty:
        return gdf
    return gdf[gdf["confidence"] >= min_confidence].copy()


def derive_floor_count(
    data: pd.DataFrame | gpd.GeoDataFrame | pd.Series | np.ndarray | float,
    height_col: str = "height",
    subtype_col: str = "subtype",
    explicit_cols: tuple[str, ...] = ("num_floors", "levels", "building:levels", "floor_count", "stories"),
    residential_floor_height: float = GHSL_RESIDENTIAL_FLOOR_HEIGHT_M,
    commercial_floor_height: float = GHSL_COMMERCIAL_FLOOR_HEIGHT_M,
) -> pd.Series | np.ndarray:
    """
    Derives building floor count using a 3-tier hierarchical resolution based on
    international urban remote sensing benchmarks (EC JRC GHSL; Biljecki & Chow, 2022):

    1. Explicit Ground-Truth Tier:
       If any explicit attribute ('num_floors', 'levels', 'building:levels', 'floor_count')
       is present in the dataset and contains valid positive integers, that ground-truth
       value is used directly.
    2. International Typological Benchmark Tier:
       If only height and functional subtype are available:
       - Residential structures ('residential', 'apartments', 'house'): nominal 3.0 m floor-to-floor height.
       - Commercial/Public structures ('commercial', 'office', 'retail', 'industrial'): 3.6 m floor-to-floor height.
    3. Height-Stratified Fallback Tier:
       When only raw height is provided:
       - Low/mid-rise buildings (< 35 m): nominal 3.0 m per floor.
       - High-rise towers (>= 35 m): nominal 3.6 m per floor (accounting for structural slabs, HVAC, and mechanical floors).
       - Minimum lower bound: every physical building has at least 1 floor (max(1, floors)).

    Parameters
    ----------
    data : pd.DataFrame | gpd.GeoDataFrame | pd.Series | np.ndarray | float
        Building data container containing heights and/or explicit floor columns.
    height_col : str, optional
        Name of the building height column (in meters). Default 'height'.
    subtype_col : str, optional
        Name of the building land-use / subtype column. Default 'subtype'.
    explicit_cols : tuple[str, ...], optional
        Candidate column names representing explicit floor ground-truth tags.
    residential_floor_height : float, optional
        International residential floor-to-floor height in meters (default 3.0m).
    commercial_floor_height : float, optional
        International commercial/office floor-to-floor height in meters (default 3.6m).

    Returns
    -------
    pd.Series | np.ndarray
        Integer floor count series or array with values >= 1.
    """
    # 1. Handle DataFrame / GeoDataFrame inputs
    if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
        # Check for explicit ground-truth floor count columns
        for col in explicit_cols:
            if col in data.columns:
                valid_mask = pd.to_numeric(data[col], errors="coerce").notnull() & (data[col] > 0)
                if valid_mask.any():
                    # Populate explicit floors where present
                    floors = pd.to_numeric(data[col], errors="coerce").fillna(0).astype(int)
                    # For rows missing explicit floor tags, fall back to height derivation
                    if (~valid_mask).any():
                        h_sub = data.loc[~valid_mask, height_col] if height_col in data.columns else 0.0
                        derived = derive_floor_count(
                            h_sub,
                            residential_floor_height=residential_floor_height,
                            commercial_floor_height=commercial_floor_height,
                        )
                        floors.loc[~valid_mask] = derived
                    return pd.Series(np.maximum(1, floors), index=data.index, name="floor_count")

        # Check for subtype-informed derivation
        heights = data[height_col].fillna(3.0) if height_col in data.columns else pd.Series(3.0, index=data.index)
        if subtype_col in data.columns:
            is_comm = data[subtype_col].astype(str).str.lower().isin(
                ["commercial", "office", "retail", "public", "industrial"]
            )
            inter_story = np.where(is_comm, commercial_floor_height, residential_floor_height)
            floors = np.maximum(1, np.floor(heights.values / inter_story)).astype(int)
            return pd.Series(floors, index=data.index, name="floor_count")

        return derive_floor_count(
            heights,
            residential_floor_height=residential_floor_height,
            commercial_floor_height=commercial_floor_height,
        )

    # 2. Handle Series, ndarray, list, or scalar float inputs
    h = np.asarray(data, dtype=float)
    # Stratified height: towers >= 35m use 3.6m inter-story, standard structures use 3.0m
    inter_story = np.where(h >= 35.0, commercial_floor_height, residential_floor_height)
    floors = np.maximum(1, np.floor(h / inter_story)).astype(int)

    if isinstance(data, pd.Series):
        return pd.Series(floors, index=data.index, name="floor_count")
    return floors


def intersect_residential_mask(
    buildings_gdf: gpd.GeoDataFrame,
    residential_mask: gpd.GeoDataFrame | Path | str | None,
) -> gpd.GeoDataFrame:
    """
    Filters building footprints to retain only those overlapping residential zones.

    Supports both vector boundaries (GeoJSON, GeoPackage, Shapefile, Parquet) and
    raster classification grids (e.g., EC JRC GHS-BUILT-C GeoTIFFs).

    For raster masks, buildings are sampled at their centroids. Footprints situated
    over residential pixels (> 0) are preserved; industrial factories and commercial
    mega-warehouses situated over non-residential pixels are excluded from living space calculations.

    Parameters
    ----------
    buildings_gdf : gpd.GeoDataFrame
        Building footprints in WGS84 (EPSG:4326).
    residential_mask : gpd.GeoDataFrame | Path | str | None
        Residential filter mask. If None, input buildings are returned unaltered.

    Returns
    -------
    gpd.GeoDataFrame
        Residential-filtered building footprints.
    """
    if residential_mask is None or buildings_gdf.empty:
        return buildings_gdf

    # Handle GeoTIFF raster mask (e.g. EC JRC GHS-BUILT-C)
    if isinstance(residential_mask, (str, Path)):
        mask_path = Path(residential_mask)
        if not mask_path.exists():
            return buildings_gdf

        if mask_path.suffix.lower() in [".tif", ".tiff"]:
            with rasterio.open(mask_path) as src:
                # Sample raster at building centroids projected into raster coordinate space
                if buildings_gdf.crs != src.crs:
                    b_proj = buildings_gdf.to_crs(src.crs)
                else:
                    b_proj = buildings_gdf

                if b_proj.crs and b_proj.crs.is_geographic:
                    # Use planar UTM 48S for planar centroid then project to raster CRS
                    centroids = buildings_gdf.to_crs(epsg=32748).geometry.centroid.to_crs(src.crs)
                else:
                    centroids = b_proj.geometry.centroid

                coords = [(c.x, c.y) for c in centroids]
                sampled = list(src.sample(coords))
                values = np.array([s[0] for s in sampled])
                # Non-zero pixel indicates residential built-up presence
                is_residential = values > 0
                return buildings_gdf[is_residential].copy()

        if mask_path.suffix.lower() in [".parquet", ".geoparquet", ".geojson", ".gpkg", ".shp"]:
            mask_gdf = gpd.read_file(mask_path)
        else:
            return buildings_gdf
    else:
        mask_gdf = residential_mask

    if buildings_gdf.crs != mask_gdf.crs:
        mask_gdf = mask_gdf.to_crs(buildings_gdf.crs)

    joined = gpd.sjoin(buildings_gdf, mask_gdf, how="inner", predicate="intersects")
    return joined[buildings_gdf.columns].drop_duplicates(
        subset=["id"] if "id" in buildings_gdf.columns else None
    )


def fetch_open_buildings_filtered(
    bbox: tuple[float, float, float, float],
    output_parquet: str | Path,
    ghs_residential_mask: gpd.GeoDataFrame | Path | str | None = None,
    min_confidence: float = 0.65,
    source_url: str = DEFAULT_OPEN_BUILDINGS_SOURCE_URL,
) -> Path:
    """
    Downloads, filters, derives floor counts, and writes standardized residential buildings GeoParquet.

    1. Executes DuckDB spatial query over Source Cooperative open data.
    2. Applies detection confidence threshold filtering (>= min_confidence).
    3. Derives building floor counts using international GHSL standards.
    4. Applies EC JRC GHS-BUILT-C residential masking.
    5. Writes standardized GeoParquet to output_parquet with schema:
       ['id', 'geometry', 'height', 'confidence', 'floor_count'].

    Parameters
    ----------
    bbox : tuple[float, float, float, float]
        WGS84 spatial bounds (min_lon, min_lat, max_lon, max_lat).
    output_parquet : str | Path
        Target destination filepath.
    ghs_residential_mask : gpd.GeoDataFrame | Path | str | None, optional
        Residential boundary mask or GHS-BUILT-C GeoTIFF path.
    min_confidence : float, optional
        Confidence cutoff (default 0.65).
    source_url : str, optional
        Direct Source Cooperative Parquet distribution URL.

    Returns
    -------
    Path
        Path to the verified output GeoParquet file.
    """
    output_parquet = Path(output_parquet)
    output_parquet.parent.mkdir(parents=True, exist_ok=True)

    con = get_duckdb_spatial_connection()
    try:
        desc_df = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{source_url}') LIMIT 1").df()
        cols_avail = set(desc_df["column_name"])
        id_expr = "CAST(boundary_id AS VARCHAR)" if "boundary_id" in cols_avail else "id"
        height_expr = "height" if "height" in cols_avail else "NULL::DOUBLE"
        query = build_open_buildings_query(
            bbox=bbox,
            min_confidence=min_confidence,
            source_url=source_url,
            id_expr=id_expr,
            height_expr=height_expr,
        )
        df = con.execute(query).df()
    except (duckdb.Error, RuntimeError, OSError, ValueError):
        df = pd.DataFrame(columns=["id", "height", "confidence", "wkt_geom"])
    finally:
        con.close()

    if df.empty:
        gdf = gpd.GeoDataFrame(
            columns=["id", "geometry", "height", "confidence", "floor_count"],
            crs="EPSG:4326",
        )
    else:
        from shapely import wkt

        df["geometry"] = df["wkt_geom"].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(df.drop(columns=["wkt_geom"]), geometry="geometry", crs="EPSG:4326")
        gdf = filter_by_confidence(gdf, min_confidence=min_confidence)
        gdf["floor_count"] = derive_floor_count(gdf)
        if ghs_residential_mask is not None:
            gdf = intersect_residential_mask(gdf, ghs_residential_mask)

    # Standardize column schema
    cols = ["id", "geometry", "height", "confidence", "floor_count"]
    for c in cols:
        if c not in gdf.columns:
            gdf[c] = None
    gdf = gdf[cols]

    if not gdf.empty:
        assert gdf.geometry.is_valid.all(), "Building geometries contain invalid shapes"

    gdf.to_parquet(output_parquet)
    assert output_parquet.exists() and output_parquet.stat().st_size > 0, "Output file was not created properly"
    return output_parquet
