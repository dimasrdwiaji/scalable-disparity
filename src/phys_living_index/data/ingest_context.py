"""
Ingest WorldPop, VIIRS Black Marble nighttime lights, and environmental raster layers (NDVI, LST, PM2.5).
"""

from typing import Tuple
from pathlib import Path


def fetch_worldpop(bbox: Tuple[float, float, float, float], output_tif: Path) -> Path:
    """Download unconstrained WorldPop 100m population counts clipped to bbox."""
    return output_tif


def fetch_environmental_layers(bbox: Tuple[float, float, float, float], output_dir: Path) -> Path:
    """Download Sentinel-2 NDVI, Landsat/MODIS LST, and Sentinel-5P/Open-Meteo PM2.5."""
    return output_dir
