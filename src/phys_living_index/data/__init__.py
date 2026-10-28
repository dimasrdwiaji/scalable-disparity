"""
Data ingestion modules querying cloud-native geospatial data from AWS S3, Copernicus, and Google Earth Engine.
"""

from .ingest_overture import (
    build_overture_amenities_query,
    build_overture_transportation_query,
    fetch_overture_amenities,
    fetch_overture_transportation,
)
from .ingest_buildings import (
    filter_by_confidence,
    derive_floor_count,
    intersect_residential_mask,
    fetch_open_buildings_filtered,
)
from .ingest_context import fetch_environmental_layers, fetch_worldpop

__all__ = [
    "build_overture_amenities_query",
    "build_overture_transportation_query",
    "fetch_overture_amenities",
    "fetch_overture_transportation",
    "filter_by_confidence",
    "derive_floor_count",
    "intersect_residential_mask",
    "fetch_open_buildings_filtered",
    "fetch_environmental_layers",
    "fetch_worldpop",
]
