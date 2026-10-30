"""
Ingest Overture Maps Foundation Places & Transportation from AWS S3 using DuckDB spatial.

Overture Maps Foundation (Linux Foundation, Amazon, Meta, Microsoft, TomTom) provides
globally standardized open geospatial themes partitioned into Cloud-Native GeoParquet
hosted on Amazon S3.

This module provides:
1. Pure query builders that construct partitioned S3 spatial SQL queries.
2. Thin I/O callers executing DuckDB queries over public S3 buckets with zero AWS credentials.
"""

from pathlib import Path

import duckdb

# Current stable Overture Maps release partition on AWS S3
DEFAULT_OVERTURE_RELEASE: str = "2026-10-21.0"


def get_duckdb_spatial_connection() -> duckdb.DuckDBPyConnection:
    """
    Initializes an in-memory DuckDB connection with spatial and HTTPFS extensions loaded.

    Configures S3 settings for the public Overture Maps bucket in us-west-2:
    - s3_region: 'us-west-2' (AWS region hosting Overture S3 buckets).
    - s3_url_style: 'path' (compatible with DuckDB HTTPFS S3 path syntax).

    Returns
    -------
    duckdb.DuckDBPyConnection
        Configured DuckDB connection handle ready for spatial Parquet queries.
    """
    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial;")
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("SET s3_region = 'us-west-2';")
    con.execute("SET s3_url_style = 'path';")
    con.execute("SET http_retries = 5;")
    con.execute("SET http_timeout = 60000;")
    return con


def build_overture_amenities_query(
    bbox: tuple[float, float, float, float],
    output_parquet: str | Path,
    release: str = DEFAULT_OVERTURE_RELEASE,
) -> str:
    """
    Constructs a DuckDB SQL query to extract essential amenities and green spaces from Overture.

    Extracts:
    - Overture Places: Primary essential destinations (education.school, healthcare.hospital,
      healthcare.clinic, commercial.supermarket_grocery).
    - Overture Base (Land Use): Public open recreation and green spaces (park, sports_pitch,
      recreation_ground).

    Parameters
    ----------
    bbox : tuple[float, float, float, float]
        Bounding box coordinates in WGS84: (min_lon, min_lat, max_lon, max_lat).
    output_parquet : str | Path
        Target filepath where extracted amenities will be saved as GeoParquet.
    release : str, optional
        Overture release date partition tag (e.g. '2026-10-21.0').

    Returns
    -------
    str
        DuckDB COPY ... TO SQL statement.
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    out_str = Path(output_parquet).as_posix()

    return f"""
    COPY (
        SELECT 
            id, 
            names.primary AS name, 
            coalesce(taxonomy.primary, basic_category) AS category,
            geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=places/type=place/*', hive_partitioning=true)
        WHERE bbox.xmin >= {min_lon} AND bbox.xmax <= {max_lon}
          AND bbox.ymin >= {min_lat} AND bbox.ymax <= {max_lat}
          AND (
              coalesce(taxonomy.primary, basic_category) IN (
                  'school', 'hospital', 'clinic', 'supermarket', 'grocery_store',
                  'education.school', 'healthcare.hospital', 'healthcare.clinic', 'commercial.supermarket_grocery'
              )
          )
        UNION ALL
        SELECT 
            id, 
            names.primary AS name, 
            subtype AS category,
            geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=base/type=land_use/*', hive_partitioning=true)
        WHERE bbox.xmin >= {min_lon} AND bbox.xmax <= {max_lon}
          AND bbox.ymin >= {min_lat} AND bbox.ymax <= {max_lat}
          AND subtype IN ('park', 'sports_pitch', 'recreation_ground')
    ) TO '{out_str}' (FORMAT PARQUET);
    """


def build_overture_transportation_query(
    bbox: tuple[float, float, float, float],
    output_parquet: str | Path,
    release: str = DEFAULT_OVERTURE_RELEASE,
) -> str:
    """
    Constructs a DuckDB SQL query to extract pedestrian-walkable road and path segments.

    Filters Overture Transportation segments:
    - Excludes railway corridors (subtype != 'rail') to focus on walkable paths and streets.
    - Captures pedestrian rights-of-way, sidewalks, local streets, and alleys.

    Parameters
    ----------
    bbox : tuple[float, float, float, float]
        Bounding box coordinates in WGS84: (min_lon, min_lat, max_lon, max_lat).
    output_parquet : str | Path
        Target filepath where extracted road segments will be saved as GeoParquet.
    release : str, optional
        Overture release date partition tag.

    Returns
    -------
    str
        DuckDB COPY ... TO SQL statement.
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    out_str = Path(output_parquet).as_posix()

    return f"""
    COPY (
        SELECT 
            id, 
            class, 
            subtype,
            geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=transportation/type=segment/*', hive_partitioning=true)
        WHERE bbox.xmin >= {min_lon} AND bbox.xmax <= {max_lon}
          AND bbox.ymin >= {min_lat} AND bbox.ymax <= {max_lat}
          AND (subtype IS NULL OR subtype != 'rail')
    ) TO '{out_str}' (FORMAT PARQUET);
    """


def fetch_overture_amenities(
    bbox: tuple[float, float, float, float],
    output_parquet: Path | str,
    release: str = DEFAULT_OVERTURE_RELEASE,
) -> Path:
    """
    Executes the Overture Places and Base land-use query and writes GeoParquet to disk.

    Thin I/O function that delegates to DuckDB spatial over S3.

    Parameters
    ----------
    bbox : tuple[float, float, float, float]
        Target spatial bounds (min_lon, min_lat, max_lon, max_lat).
    output_parquet : Path | str
        Destination path for output GeoParquet.
    release : str, optional
        Overture release partition tag.

    Returns
    -------
    Path
        Path to the verified output file.
    """
    output_parquet = Path(output_parquet)
    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    con = get_duckdb_spatial_connection()
    query = build_overture_amenities_query(bbox, output_parquet, release=release)

    try:
        con.execute(query)
    finally:
        con.close()

    assert output_parquet.exists() and output_parquet.stat().st_size > 0, "Overture amenities file was not written"
    return output_parquet


def fetch_overture_transportation(
    bbox: tuple[float, float, float, float],
    output_parquet: Path | str,
    release: str = DEFAULT_OVERTURE_RELEASE,
) -> Path:
    """
    Executes the Overture Transportation segment query and writes GeoParquet to disk.

    Thin I/O function that delegates to DuckDB spatial over S3.

    Parameters
    ----------
    bbox : tuple[float, float, float, float]
        Target spatial bounds (min_lon, min_lat, max_lon, max_lat).
    output_parquet : Path | str
        Destination path for output GeoParquet.
    release : str, optional
        Overture release partition tag.

    Returns
    -------
    Path
        Path to the verified output file.
    """
    output_parquet = Path(output_parquet)
    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    con = get_duckdb_spatial_connection()
    query = build_overture_transportation_query(bbox, output_parquet, release=release)

    try:
        con.execute(query)
    finally:
        con.close()

    assert output_parquet.exists() and output_parquet.stat().st_size > 0, "Overture transportation file was not written"
    return output_parquet
