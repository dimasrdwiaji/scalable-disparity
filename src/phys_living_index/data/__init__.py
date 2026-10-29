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

from .credentials import load_earthdata_token
from .ingest_buildings import (
    build_open_buildings_query,
    derive_floor_count,
    fetch_open_buildings_filtered,
    filter_by_confidence,
    intersect_residential_mask,
)
from .ingest_context import (
    OPENMETEO_AIR_QUALITY_VARIABLES,
    batch_locations,
    build_planetary_computer_stac_query,
    build_viirs_request_params,
    build_worldpop_request,
    compute_bsi,
    compute_mndwi,
    compute_ndbi,
    compute_ndvi,
    extract_landsat_lst,
    fetch_environmental_layers,
    fetch_openmeteo_air_quality,
    fetch_planetary_computer_layers,
    fetch_viirs_black_marble,
    fetch_worldpop,
    generate_sampling_grid,
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
    "batch_locations",
    "build_open_buildings_query",
    "build_overture_amenities_query",
    "build_overture_transportation_query",
    "build_planetary_computer_stac_query",
    "build_viirs_request_params",
    "build_worldpop_request",
    "compute_bsi",
    "compute_mndwi",
    "compute_ndbi",
    "compute_ndvi",
    "derive_floor_count",
    "extract_landsat_lst",
    "fetch_environmental_layers",
    "fetch_open_buildings_filtered",
    "fetch_openmeteo_air_quality",
    "fetch_overture_amenities",
    "fetch_overture_transportation",
    "fetch_planetary_computer_layers",
    "fetch_viirs_black_marble",
    "fetch_worldpop",
    "filter_by_confidence",
    "generate_sampling_grid",
    "get_duckdb_spatial_connection",
    "intersect_residential_mask",
    "load_earthdata_token",
]
