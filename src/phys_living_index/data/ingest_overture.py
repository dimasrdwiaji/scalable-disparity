"""
Ingest Overture Maps Foundation Places & Transportation directly from AWS S3 using DuckDB spatial.
"""

from typing import Tuple, Union, Optional
import duckdb
from pathlib import Path

DEFAULT_OVERTURE_RELEASE = "2026-10-21.0"


def get_duckdb_spatial_connection() -> duckdb.DuckDBPyConnection:
    """Initialize a DuckDB connection with spatial and httpfs extensions."""
    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial;")
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("SET s3_region = 'us-west-2';")
    con.execute("SET s3_url_style = 'path';")
    return con


def build_overture_amenities_query(
    bbox: Tuple[float, float, float, float],
    output_parquet: Union[str, Path],
    release: str = DEFAULT_OVERTURE_RELEASE,
) -> str:
    """
    Pure query builder constructing the DuckDB SQL statement to query Overture Places
    and Base themes from AWS S3.
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    out_str = Path(output_parquet).as_posix()

    return f"""
    COPY (
        SELECT 
            id, 
            names.primary AS name, 
            categories.main AS category,
            ST_GeomFromWkb(geometry) AS geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=places/type=place/*', hive_partitioning=true)
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
        FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=base/type=land_use/*', hive_partitioning=true)
        WHERE bbox.xmin >= {min_lon} AND bbox.xmax <= {max_lon}
          AND bbox.ymin >= {min_lat} AND bbox.ymax <= {max_lat}
          AND subtype IN ('park', 'sports_pitch', 'recreation_ground')
    ) TO '{out_str}' (FORMAT PARQUET);
    """


def build_overture_transportation_query(
    bbox: Tuple[float, float, float, float],
    output_parquet: Union[str, Path],
    release: str = DEFAULT_OVERTURE_RELEASE,
) -> str:
    """
    Pure query builder constructing the DuckDB SQL statement to query Overture Transportation
    pedestrian-walkable segments from AWS S3.
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    out_str = Path(output_parquet).as_posix()

    return f"""
    COPY (
        SELECT 
            id, 
            class, 
            subtype,
            ST_GeomFromWkb(geometry) AS geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=transportation/type=segment/*', hive_partitioning=true)
        WHERE bbox.xmin >= {min_lon} AND bbox.xmax <= {max_lon}
          AND bbox.ymin >= {min_lat} AND bbox.ymax <= {max_lat}
          AND (subtype IS NULL OR subtype != 'rail')
    ) TO '{out_str}' (FORMAT PARQUET);
    """


def fetch_overture_amenities(
    bbox: Tuple[float, float, float, float],
    output_parquet: Path,
    release: str = DEFAULT_OVERTURE_RELEASE,
) -> Path:
    """
    Queries Overture Maps Places & Base themes directly from AWS S3 over the bounding box.
    Thin I/O function executing the query via DuckDB spatial.
    """
    output_parquet = Path(output_parquet)
    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    con = get_duckdb_spatial_connection()
    query = build_overture_amenities_query(bbox, output_parquet, release=release)
    con.execute(query)
    con.close()
    return output_parquet


def fetch_overture_transportation(
    bbox: Tuple[float, float, float, float],
    output_parquet: Path,
    release: str = DEFAULT_OVERTURE_RELEASE,
) -> Path:
    """
    Queries Overture Maps Transportation (pedestrian-walkable lines) from AWS S3.
    Thin I/O function executing the query via DuckDB spatial.
    """
    output_parquet = Path(output_parquet)
    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    con = get_duckdb_spatial_connection()
    query = build_overture_transportation_query(bbox, output_parquet, release=release)
    con.execute(query)
    con.close()
    return output_parquet
