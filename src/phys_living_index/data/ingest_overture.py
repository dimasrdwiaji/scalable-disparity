"""
Ingest Overture Maps Foundation Places & Transportation directly from AWS S3 using DuckDB spatial.
"""

from typing import Tuple
import duckdb
import geopandas as gpd
from pathlib import Path


def get_duckdb_spatial_connection() -> duckdb.DuckDBPyConnection:
    """Initialize a DuckDB connection with spatial and httpfs extensions."""
    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial;")
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("SET s3_region='us-west-2';")
    return con


def fetch_overture_amenities(bbox: Tuple[float, float, float, float], output_parquet: Path) -> Path:
    """
    Queries Overture Maps Places & Base themes directly from AWS S3 over the bounding box.
    
    Args:
        bbox: (min_lon, min_lat, max_lon, max_lat)
        output_parquet: Destination file path for GeoParquet output.
        
    Returns:
        Path to the saved GeoParquet file.
    """
    con = get_duckdb_spatial_connection()
    min_lon, min_lat, max_lon, max_lat = bbox

    query = f"""
    COPY (
        SELECT 
            id, 
            names.primary AS name, 
            categories.main AS category,
            ST_GeomFromWkb(geometry) AS geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/2024-*/theme=places/type=place/*', hive_partitioning=true)
        WHERE bbox.xmin >= {min_lon} AND bbox.xmax <= {max_lon}
          AND bbox.ymin >= {min_lat} AND bbox.ymax <= {max_lat}
          AND categories.main IN (
              'education.school', 'healthcare.hospital', 
              'healthcare.clinic', 'commercial.supermarket_grocery'
          )
        UNION ALL
        SELECT 
            id, 
            names.primary AS name, 
            subtype AS category,
            ST_GeomFromWkb(geometry) AS geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/2024-*/theme=base/type=land_use/*', hive_partitioning=true)
        WHERE bbox.xmin >= {min_lon} AND bbox.xmax <= {max_lon}
          AND bbox.ymin >= {min_lat} AND bbox.ymax <= {max_lat}
          AND subtype IN ('park', 'sports_pitch', 'recreation_ground')
    ) TO '{output_parquet.as_posix()}' (FORMAT PARQUET);
    """
    con.execute(query)
    con.close()
    return output_parquet


def fetch_overture_transportation(bbox: Tuple[float, float, float, float], output_parquet: Path) -> Path:
    """
    Queries Overture Maps Transportation (pedestrian-walkable lines) from AWS S3.
    """
    con = get_duckdb_spatial_connection()
    min_lon, min_lat, max_lon, max_lat = bbox

    query = f"""
    COPY (
        SELECT 
            id, 
            class, 
            subtype,
            ST_GeomFromWkb(geometry) AS geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/2024-*/theme=transportation/type=segment/*', hive_partitioning=true)
        WHERE bbox.xmin >= {min_lon} AND bbox.xmax <= {max_lon}
          AND bbox.ymin >= {min_lat} AND bbox.ymax <= {max_lat}
          AND (subtype IS NULL OR subtype != 'rail')
    ) TO '{output_parquet.as_posix()}' (FORMAT PARQUET);
    """
    con.execute(query)
    con.close()
    return output_parquet
