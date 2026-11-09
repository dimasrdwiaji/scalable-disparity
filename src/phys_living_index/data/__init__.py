"""
Data ingestion modules querying cloud-native geospatial data from AWS S3, Copernicus, and Google Earth Engine.
"""

import os
from contextlib import suppress

# Ensure PROJ_LIB / PROJ_DATA point to the active Python environment's database rather than conflicting external installs
with suppress(Exception):
    import pyproj.datadir

    _proj_dir = pyproj.datadir.get_data_dir()
    os.environ["PROJ_LIB"] = _proj_dir
    os.environ["PROJ_DATA"] = _proj_dir

from .credentials import load_earthdata_token, load_gee_project
from .ingest_buildings import (
    build_open_buildings_query,
    derive_floor_count,
    fetch_open_buildings_filtered,
    filter_by_confidence,
    intersect_residential_mask,
)
from .ingest_context import (
    OPENMETEO_AIR_QUALITY_VARIABLES,
    OPENMETEO_VALIDATION_VARIABLES,
    build_openmeteo_hourly_params,
    fetch_openmeteo_hourly_median,
    generate_sampling_grid,
    summarize_hourly_median,
)
from .ingest_overture import (
    build_overture_amenities_query,
    build_overture_transportation_query,
    fetch_overture_amenities,
    fetch_overture_transportation,
    get_duckdb_spatial_connection,
)

__all__ = [
    "OPENMETEO_AIR_QUALITY_VARIABLES",
    "OPENMETEO_VALIDATION_VARIABLES",
    "build_open_buildings_query",
    "build_openmeteo_hourly_params",
    "build_overture_amenities_query",
    "build_overture_transportation_query",
    "derive_floor_count",
    "fetch_open_buildings_filtered",
    "fetch_openmeteo_hourly_median",
    "fetch_overture_amenities",
    "fetch_overture_transportation",
    "filter_by_confidence",
    "generate_sampling_grid",
    "get_duckdb_spatial_connection",
    "intersect_residential_mask",
    "load_earthdata_token",
    "load_gee_project",
    "summarize_hourly_median",
]
