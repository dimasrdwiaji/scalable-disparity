"""
Data ingestion modules querying cloud-native geospatial data from AWS S3, Copernicus, and Google Earth Engine.
"""

import os

# Ensure PROJ_LIB / PROJ_DATA point to the active Python environment's database rather than conflicting external installs
try:
    import pyproj.datadir
    _proj_dir = pyproj.datadir.get_data_dir()
    os.environ["PROJ_LIB"] = _proj_dir
    os.environ["PROJ_DATA"] = _proj_dir
except Exception:
    pass

from .ingest_overture import (
    build_overture_amenities_query,
    build_overture_transportation_query,
    fetch_overture_amenities,
    fetch_overture_transportation,
)
from .ingest_buildings import (
    build_open_buildings_query,
    filter_by_confidence,
    derive_floor_count,
    intersect_residential_mask,
    fetch_open_buildings_filtered,
)
from .ingest_context import (
    build_viirs_request_params,
    fetch_viirs_black_marble,
    build_worldpop_request,
    fetch_worldpop,
    build_planetary_computer_stac_query,
    compute_ndvi,
    extract_landsat_lst,
    fetch_planetary_computer_layers,
    OPENMETEO_AIR_QUALITY_VARIABLES,
    generate_sampling_grid,
    batch_locations,
    fetch_openmeteo_air_quality,
    fetch_environmental_layers,
)
from .credentials import load_earthdata_token

__all__ = [
    "build_overture_amenities_query",
    "build_overture_transportation_query",
    "fetch_overture_amenities",
    "fetch_overture_transportation",
    "build_open_buildings_query",
    "filter_by_confidence",
    "derive_floor_count",
    "intersect_residential_mask",
    "fetch_open_buildings_filtered",
    "build_viirs_request_params",
    "fetch_viirs_black_marble",
    "build_worldpop_request",
    "fetch_worldpop",
    "build_planetary_computer_stac_query",
    "compute_ndvi",
    "extract_landsat_lst",
    "fetch_planetary_computer_layers",
    "OPENMETEO_AIR_QUALITY_VARIABLES",
    "generate_sampling_grid",
    "batch_locations",
    "fetch_openmeteo_air_quality",
    "fetch_environmental_layers",
    "load_earthdata_token",
]
