"""
Open-Meteo (CAMS global) air quality as a reference-year validation series.

Per ADR 0002 §5, Open-Meteo/CAMS is no longer a feature channel: its ~0.4° (~44 km) grid
carries no cell-level information, and a single `current` reading is not representative.
It is kept only to validate the satellite-derived PM2.5 and NO2 channels: hourly values for
the reference year are reduced to a per-location median.

The former Sentinel-2, Landsat, VIIRS VNP46A2 and WorldPop fetchers were removed. They took
a single scene and georeferenced it to the study bounding box, which misplaced every pixel.
Those channels are now built on Earth Engine (`gee_layers.py`) and aggregated per H3 cell.

Values stay in authentic units (μg/m³, AQI points). Failures raise; no placeholder values
are ever written.
"""

from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from shapely.geometry import Point

OPENMETEO_AIR_QUALITY_ENDPOINT = "https://air-quality-api.open-meteo.com/v1/air-quality"

# Open-Meteo Air Quality Variables (Pollen variables explicitly excluded)
OPENMETEO_AIR_QUALITY_VARIABLES: list[str] = [
    "pm2_5",
    "pm10",
    "carbon_monoxide",
    "carbon_dioxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
    "ammonia",
    "methane",
    "aerosol_optical_depth",
    "dust",
    "uv_index",
    "uv_index_clear_sky",
    "european_aqi",
    "european_aqi_pm2_5",
    "european_aqi_pm10",
    "european_aqi_no2",
    "european_aqi_o3",
    "european_aqi_so2",
    "us_aqi",
    "us_aqi_pm2_5",
    "us_aqi_pm10",
    "us_aqi_no2",
    "us_aqi_o3",
    "us_aqi_so2",
    "us_aqi_co",
]

# Variables needed to validate the PM2.5 and NO2 channels
OPENMETEO_VALIDATION_VARIABLES: list[str] = ["pm2_5", "nitrogen_dioxide", "ozone", "european_aqi"]


def generate_sampling_grid(
    bbox: tuple[float, float, float, float],
    step_deg: float = 0.25,
) -> list[tuple[float, float]]:
    """
    Generates regular grid points (lat, lon) spanning a bounding box.

    Parameters
    ----------
    bbox : tuple[float, float, float, float]
        WGS84 bounding box (min_lon, min_lat, max_lon, max_lat).
    step_deg : float, optional
        Grid spacing in degrees. The default 0.25° is finer than the CAMS ~0.4° grid,
        so every CAMS cell over the area is sampled at least once.

    Returns
    -------
    list[tuple[float, float]]
        List of (latitude, longitude) coordinate pairs.
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    lats = np.arange(min_lat, max_lat + step_deg / 2, step_deg)
    lons = np.arange(min_lon, max_lon + step_deg / 2, step_deg)
    return [(float(lat), float(lon)) for lat in lats for lon in lons]


def build_openmeteo_hourly_params(
    points: list[tuple[float, float]],
    start_date: str,
    end_date: str,
    variables: list[str] | None = None,
    max_batch_size: int = 10,
) -> list[dict[str, str]]:
    """
    Batches coordinate points into Open-Meteo multi-location hourly archive requests.

    Parameters
    ----------
    points : list[tuple[float, float]]
        Coordinate pairs (latitude, longitude).
    start_date, end_date : str
        Inclusive ISO dates, e.g. '2023-01-01' and '2023-12-31'.
    variables : list[str] | None, optional
        Hourly variables (default OPENMETEO_VALIDATION_VARIABLES).
    max_batch_size : int, optional
        Maximum coordinates per request (a year of hourly data is large; default 10).

    Returns
    -------
    list[dict[str, str]]
        URL parameter dictionaries ready for requests.get.
    """
    if variables is None:
        variables = OPENMETEO_VALIDATION_VARIABLES
    var_str = ",".join(variables)
    batches = []
    for i in range(0, len(points), max_batch_size):
        chunk = points[i : i + max_batch_size]
        batches.append({
            "latitude": ",".join(f"{p[0]:.4f}" for p in chunk),
            "longitude": ",".join(f"{p[1]:.4f}" for p in chunk),
            "hourly": var_str,
            "start_date": start_date,
            "end_date": end_date,
            "timezone": "UTC",
        })
    return batches


def summarize_hourly_median(
    items: list[dict[str, Any]],
    variables: list[str],
) -> pd.DataFrame:
    """
    Reduces Open-Meteo hourly responses to one row per location: median and valid-hour count.

    Parameters
    ----------
    items : list[dict[str, Any]]
        Parsed JSON responses (one per location) with an `hourly` block.
    variables : list[str]
        Hourly variables to summarize.

    Returns
    -------
    pd.DataFrame
        Columns latitude, longitude, `<var>_median` and `<var>_n_hours`.
    """
    rows = []
    for item in items:
        hourly = item.get("hourly")
        if hourly is None:
            raise ValueError("Open-Meteo response has no 'hourly' block")
        row: dict[str, Any] = {"latitude": item["latitude"], "longitude": item["longitude"]}
        for var in variables:
            values = np.asarray([np.nan if v is None else v for v in hourly.get(var, [])], dtype=float)
            valid = values[~np.isnan(values)]
            row[f"{var}_median"] = float(np.median(valid)) if valid.size else np.nan
            row[f"{var}_n_hours"] = int(valid.size)
        rows.append(row)
    return pd.DataFrame(rows)


def fetch_openmeteo_hourly_median(
    points: list[tuple[float, float]],
    start_date: str,
    end_date: str,
    output_parquet: str | Path,
    variables: list[str] | None = None,
    max_batch_size: int = 10,
    timeout_s: int = 120,
) -> Path:
    """
    Downloads hourly Open-Meteo air quality for the reference period and writes per-location
    medians as point GeoParquet. HTTP or parsing errors propagate.

    Parameters
    ----------
    points : list[tuple[float, float]]
        Coordinate pairs (latitude, longitude).
    start_date, end_date : str
        Inclusive ISO dates of the reference period.
    output_parquet : str | Path
        Destination GeoParquet path.
    variables : list[str] | None, optional
        Hourly variables (default OPENMETEO_VALIDATION_VARIABLES).
    max_batch_size : int, optional
        Coordinates per request.
    timeout_s : int, optional
        Request timeout in seconds.

    Returns
    -------
    Path
        Verified output GeoParquet path.
    """
    if variables is None:
        variables = OPENMETEO_VALIDATION_VARIABLES
    output_parquet = Path(output_parquet)
    output_parquet.parent.mkdir(parents=True, exist_ok=True)

    items: list[dict[str, Any]] = []
    for params in build_openmeteo_hourly_params(points, start_date, end_date, variables, max_batch_size):
        resp = requests.get(OPENMETEO_AIR_QUALITY_ENDPOINT, params=params, timeout=timeout_s)
        resp.raise_for_status()
        data = resp.json()
        items.extend(data if isinstance(data, list) else [data])

    df = summarize_hourly_median(items, variables)
    df["start_date"] = start_date
    df["end_date"] = end_date
    gdf = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df["longitude"], df["latitude"], strict=True)],
        crs="EPSG:4326",
    )
    gdf.to_parquet(output_parquet)
    return output_parquet
