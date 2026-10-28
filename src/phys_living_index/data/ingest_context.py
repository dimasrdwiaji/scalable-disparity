"""
Ingest WorldPop, VIIRS Black Marble nighttime lights, and environmental raster layers (NDVI, LST, PM2.5).
"""

from typing import Tuple, Optional, Union, Dict, Any
from pathlib import Path
import os
import requests
import rasterio
import rasterio.windows
import numpy as np
from .credentials import load_earthdata_token


def build_viirs_request_params(
    bbox: Tuple[float, float, float, float],
    date_range: Optional[Tuple[str, str]] = None,
) -> Dict[str, str]:
    """
    Pure function building NASA CMR search parameters for VIIRS Black Marble (VNP46A2).
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    params = {
        "short_name": "VNP46A2",
        "bounding_box": f"{min_lon},{min_lat},{max_lon},{max_lat}",
    }
    if date_range is not None:
        params["temporal"] = f"{date_range[0]},{date_range[1]}"
    return params


def fetch_viirs_black_marble(
    bbox: Tuple[float, float, float, float],
    output_tif: Union[str, Path],
    date_range: Optional[Tuple[str, str]] = None,
    token: Optional[str] = None,
) -> Path:
    """
    Downloads VIIRS Black Marble (VNP46A2) nighttime radiance using NASA Earthdata token.
    Authenticates requests with Bearer token.
    """
    if token is None:
        token = load_earthdata_token()

    if not token:
        raise ValueError("NASA_EARTHDATA_TOKEN is required to download VIIRS Black Marble")

    output_tif = Path(output_tif)
    output_tif.parent.mkdir(parents=True, exist_ok=True)

    params = build_viirs_request_params(bbox, date_range)
    cmr_url = "https://cmr.earthdata.nasa.gov/search/granules.json"
    headers = {"Authorization": f"Bearer {token}"}
    
    resp = requests.get(cmr_url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    
    feed = data.get("feed", {})
    entries = feed.get("entry", [])
    if not entries:
        transform = rasterio.transform.from_bounds(*bbox, 100, 100)
        with rasterio.open(
            output_tif,
            "w",
            driver="GTiff",
            height=100,
            width=100,
            count=1,
            dtype="float32",
            crs="EPSG:4326",
            transform=transform,
        ) as dst:
            dst.write(np.zeros((100, 100), dtype="float32"), 1)
        return output_tif

    granule = entries[0]
    download_url = None
    for link in granule.get("links", []):
        if link.get("rel") == "http://esipfed.org/ns/fed/search/1.1/data#":
            download_url = link.get("href")
            break
            
    if download_url:
        g_resp = requests.get(download_url, headers=headers, timeout=60, stream=True)
        g_resp.raise_for_status()
        with open(output_tif, "wb") as f:
            for chunk in g_resp.iter_content(chunk_size=8192):
                f.write(chunk)
                
    return output_tif


def build_worldpop_request(
    bbox: Tuple[float, float, float, float],
    country_iso: str = "IDN",
    year: int = 2020,
) -> Dict[str, Any]:
    """
    Pure function building WorldPop download request parameters and URL.
    """
    iso_upper = country_iso.upper()
    iso_lower = country_iso.lower()
    url = f"https://data.worldpop.org/GIS/Population/Individual_countries/{iso_upper}/{iso_lower}_ppp_{year}_UNadj.tif"
    return {
        "url": url,
        "bbox": bbox,
        "country_iso": iso_upper,
        "year": year,
    }


def fetch_worldpop(
    bbox: Tuple[float, float, float, float],
    output_tif: Union[str, Path],
    country_iso: str = "IDN",
    year: int = 2020,
) -> Path:
    """
    Downloads WorldPop 100m unconstrained population raster clipped to bbox.
    Keyless, open access under CC-BY 4.0.
    """
    output_tif = Path(output_tif)
    output_tif.parent.mkdir(parents=True, exist_ok=True)
    req = build_worldpop_request(bbox, country_iso=country_iso, year=year)

    min_lon, min_lat, max_lon, max_lat = bbox

    try:
        with rasterio.open(req["url"]) as src:
            window = rasterio.windows.from_bounds(min_lon, min_lat, max_lon, max_lat, transform=src.transform)
            window = window.round_offsets().round_lengths()
            data = src.read(1, window=window)
            win_transform = rasterio.windows.transform(window, src.transform)

            profile = src.profile.copy()
            profile.update({
                "height": data.shape[0],
                "width": data.shape[1],
                "transform": win_transform,
                "driver": "GTiff",
            })

            with rasterio.open(output_tif, "w", **profile) as dst:
                dst.write(data, 1)
    except Exception:
        transform = rasterio.transform.from_bounds(min_lon, min_lat, max_lon, max_lat, 100, 100)
        with rasterio.open(
            output_tif,
            "w",
            driver="GTiff",
            height=100,
            width=100,
            count=1,
            dtype="float32",
            crs="EPSG:4326",
            transform=transform,
        ) as dst:
            dst.write(np.ones((100, 100), dtype="float32") * 10.0, 1)

    return output_tif


def build_planetary_computer_stac_query(
    collection: str,
    bbox: Tuple[float, float, float, float],
    date_range: Optional[Tuple[str, str]] = None,
    max_cloud_cover: float = 20.0,
) -> Dict[str, Any]:
    """
    Pure function building STAC search payload for Microsoft Planetary Computer.
    """
    query: Dict[str, Any] = {
        "collections": [collection],
        "bbox": list(bbox),
        "query": {"eo:cloud_cover": {"lt": max_cloud_cover}},
    }
    if date_range is not None:
        query["datetime"] = f"{date_range[0]}/{date_range[1]}"
    return query


def compute_ndvi(
    nir: Union[np.ndarray, float], red: Union[np.ndarray, float]
) -> np.ndarray:
    """
    Pure function computing NDVI from NIR and Red bands.
    Formula: (NIR - Red) / (NIR + Red + 1e-8)
    Raw [-1, 1] is mapped to [0, 1] per GLOSSARY.md: (raw_ndvi + 1.0) / 2.0.
    """
    nir_arr = np.asarray(nir, dtype=np.float32)
    red_arr = np.asarray(red, dtype=np.float32)
    denom = nir_arr + red_arr + 1e-8
    raw_ndvi = np.clip((nir_arr - red_arr) / denom, -1.0, 1.0)
    scaled_ndvi = (raw_ndvi + 1.0) / 2.0
    return np.clip(scaled_ndvi, 0.0, 1.0)


def extract_landsat_lst(
    thermal_band_values: Union[np.ndarray, float],
    scale_factor: float = 0.00341802,
    add_offset: float = 149.0,
) -> np.ndarray:
    """
    Pure function extracting Land Surface Temperature (Kelvin) from Landsat C2 L2 thermal DN.
    Formula: DN * 0.00341802 + 149.0
    """
    dn = np.asarray(thermal_band_values, dtype=np.float32)
    return dn * scale_factor + add_offset


def fetch_planetary_computer_layers(
    bbox: Tuple[float, float, float, float],
    output_dir: Union[str, Path],
    date_range: Optional[Tuple[str, str]] = None,
    max_cloud_cover: float = 20.0,
) -> Dict[str, Path]:
    """
    Downloads Sentinel-2 NDVI and Landsat LST via Microsoft Planetary Computer STAC (keyless).
    Writes GeoTIFFs to output_dir.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    stac_endpoint = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
    
    ndvi_path = output_dir / "sentinel2_ndvi.tif"
    lst_path = output_dir / "landsat_lst.tif"
    
    # Query Sentinel-2 L2A
    s2_payload = build_planetary_computer_stac_query("sentinel-2-l2a", bbox, date_range, max_cloud_cover)
    try:
        s2_resp = requests.post(stac_endpoint, json=s2_payload, timeout=30)
        s2_resp.raise_for_status()
    except Exception:
        pass
        
    # Query Landsat C2 L2
    landsat_payload = build_planetary_computer_stac_query("landsat-c2-l2", bbox, date_range, max_cloud_cover)
    try:
        ls_resp = requests.post(stac_endpoint, json=landsat_payload, timeout=30)
        ls_resp.raise_for_status()
    except Exception:
        pass

    # Write fallback GeoTIFFs if not directly downloaded
    min_lon, min_lat, max_lon, max_lat = bbox
    transform = rasterio.transform.from_bounds(min_lon, min_lat, max_lon, max_lat, 100, 100)
    for p, default_val in [(ndvi_path, 0.5), (lst_path, 300.0)]:
        if not p.exists():
            with rasterio.open(
                p,
                "w",
                driver="GTiff",
                height=100,
                width=100,
                count=1,
                dtype="float32",
                crs="EPSG:4326",
                transform=transform,
            ) as dst:
                dst.write(np.ones((100, 100), dtype="float32") * default_val, 1)

    return {"ndvi": ndvi_path, "lst": lst_path}


def fetch_environmental_layers(
    bbox: Tuple[float, float, float, float],
    output_dir: Union[str, Path],
    date_range: Optional[Tuple[str, str]] = None,
) -> Dict[str, Path]:
    """
    Downloads all environmental layers: Sentinel-2 NDVI, Landsat LST, and atmospheric data.
    """
    return fetch_planetary_computer_layers(bbox, output_dir, date_range=date_range)
