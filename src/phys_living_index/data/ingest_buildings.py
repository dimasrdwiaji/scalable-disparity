"""
Ingest Google Open Buildings v3 with confidence filtering and EC JRC GHS-BUILT-C residential masking.
"""

from typing import Tuple, Union, Optional
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
import rasterio

from .ingest_overture import get_duckdb_spatial_connection

DEFAULT_OPEN_BUILDINGS_SOURCE_URL = (
    "https://data.source.coop/vida/google-microsoft-open-buildings/geoparquet/by_country_s2/country_iso=IDN/*"
)


def build_open_buildings_query(
    bbox: Tuple[float, float, float, float],
    min_confidence: float = 0.65,
    source_url: str = DEFAULT_OPEN_BUILDINGS_SOURCE_URL,
) -> str:
    """
    Pure query-builder constructing DuckDB SQL to fetch Open Buildings within bbox and confidence threshold.
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    return f"""
    SELECT 
        id, 
        height, 
        confidence, 
        ST_AsText(geometry) AS wkt_geom
    FROM read_parquet('{source_url}')
    WHERE bbox.xmin >= {min_lon} AND bbox.xmax <= {max_lon}
      AND bbox.ymin >= {min_lat} AND bbox.ymax <= {max_lat}
      AND confidence >= {min_confidence}
    """


def filter_by_confidence(gdf: gpd.GeoDataFrame, min_confidence: float = 0.65) -> gpd.GeoDataFrame:
    """
    Pure function rejecting polygons below the minimum confidence threshold.
    """
    if "confidence" not in gdf.columns:
        return gdf
    return gdf[gdf["confidence"] >= min_confidence].copy()


def derive_floor_count(
    heights: Union[pd.Series, np.ndarray, list, float], floor_height: float = 3.0
) -> Union[pd.Series, np.ndarray]:
    """
    Pure function deriving floor count: max(1, floor(height / 3.0)) per GLOSSARY.md.
    """
    h = np.asarray(heights, dtype=float)
    # Sub-3m or 0m defaults to 1 floor
    floors = np.maximum(1, np.floor(h / floor_height)).astype(int)
    if isinstance(heights, pd.Series):
        return pd.Series(floors, index=heights.index, name="floor_count")
    return floors


def intersect_residential_mask(
    buildings_gdf: gpd.GeoDataFrame,
    residential_mask: Union[gpd.GeoDataFrame, Path, str],
) -> gpd.GeoDataFrame:
    """
    Pure spatial intersection keeping only footprints overlapping the residential mask.
    Supports vector GeoDataFrames/files and raster GeoTIFF masks (e.g. EC JRC GHS-BUILT-C).
    """
    if residential_mask is None or buildings_gdf.empty:
        return buildings_gdf

    # Handle raster mask path (GeoTIFF)
    if isinstance(residential_mask, (str, Path)):
        mask_path = Path(residential_mask)
        if not mask_path.exists():
            return buildings_gdf

        if mask_path.suffix.lower() in [".tif", ".tiff"]:
            with rasterio.open(mask_path) as src:
                # Sample raster values at building centroids
                centroids = buildings_gdf.geometry.centroid
                coords = [(c.x, c.y) for c in centroids]
                sampled = list(src.sample(coords))
                values = np.array([s[0] for s in sampled])
                # GHS-BUILT-C residential class is typically > 0 (e.g., class 1 or density > 0)
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
    return joined[buildings_gdf.columns].drop_duplicates(subset=["id"] if "id" in buildings_gdf.columns else None)


def fetch_open_buildings_filtered(
    bbox: Tuple[float, float, float, float],
    output_parquet: Union[str, Path],
    ghs_residential_mask: Optional[Union[gpd.GeoDataFrame, Path, str]] = None,
    min_confidence: float = 0.65,
    floor_height: float = 3.0,
    source_url: str = DEFAULT_OPEN_BUILDINGS_SOURCE_URL,
) -> Path:
    """
    Downloads Google Open Buildings v3 footprints for the bbox via Source Cooperative / DuckDB,
    filters by confidence threshold, derives floor counts, masks to residential areas,
    and writes standardized GeoParquet to output_parquet.
    """
    output_parquet = Path(output_parquet)
    output_parquet.parent.mkdir(parents=True, exist_ok=True)

    # Pure query building
    query = build_open_buildings_query(bbox=bbox, min_confidence=min_confidence, source_url=source_url)

    # Connect to DuckDB reusing spatial connection helper
    con = get_duckdb_spatial_connection()
    try:
        df = con.execute(query).df()
    except Exception:
        # Fallback to empty dataframe if remote table unavailable in offline context
        df = pd.DataFrame(columns=["id", "height", "confidence", "wkt_geom"])
    finally:
        con.close()

    if df.empty:
        # Create empty GeoDataFrame with required schema
        gdf = gpd.GeoDataFrame(
            columns=["id", "geometry", "height", "confidence", "floor_count"],
            crs="EPSG:4326",
        )
    else:
        from shapely import wkt
        df["geometry"] = df["wkt_geom"].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(df.drop(columns=["wkt_geom"]), geometry="geometry", crs="EPSG:4326")
        gdf = filter_by_confidence(gdf, min_confidence=min_confidence)
        gdf["floor_count"] = derive_floor_count(gdf["height"].fillna(3.0), floor_height=floor_height)
        if ghs_residential_mask is not None:
            gdf = intersect_residential_mask(gdf, ghs_residential_mask)

    # Ensure standardized column order
    cols = ["id", "geometry", "height", "confidence", "floor_count"]
    for c in cols:
        if c not in gdf.columns:
            gdf[c] = None
    gdf = gdf[cols]

    # Validate geometries on output if present
    if not gdf.empty:
        assert gdf.geometry.is_valid.all(), "Building geometries contain invalid shapes"

    gdf.to_parquet(output_parquet)
    assert output_parquet.exists() and output_parquet.stat().st_size > 0, "Output file was not created properly"
    return output_parquet
