from pathlib import Path
import pytest
import numpy as np
import requests

from phys_living_index.data.ingest_context import (
    build_planetary_computer_stac_query,
    compute_ndvi,
    extract_landsat_lst,
    fetch_planetary_computer_layers,
)


def test_build_planetary_computer_stac_query():
    bbox = (106.8, -6.3, 107.0, -6.1)
    date_range = ("2023-01-01", "2023-03-31")
    query = build_planetary_computer_stac_query(
        collection="sentinel-2-l2a",
        bbox=bbox,
        date_range=date_range,
        max_cloud_cover=15.0,
    )
    
    assert query["collections"] == ["sentinel-2-l2a"]
    assert query["bbox"] == [106.8, -6.3, 107.0, -6.1]
    assert query["datetime"] == "2023-01-01/2023-03-31"
    assert query["query"]["eo:cloud_cover"]["lt"] == 15.0


def test_compute_ndvi():
    # Dense vegetation: NIR high, Red low
    red = np.array([0.1, 0.4, 0.0])
    nir = np.array([0.5, 0.1, 0.0])
    
    scaled_ndvi = compute_ndvi(nir, red)
    
    # Check range is strictly in [0.0, 1.0] per GLOSSARY.md
    assert np.all(scaled_ndvi >= 0.0)
    assert np.all(scaled_ndvi <= 1.0)
    
    # Vegetation pixel (0.1, 0.5) has raw ndvi = 0.4/0.6 = 0.6667 -> rescaled = (0.6667+1)/2 = ~0.833
    assert scaled_ndvi[0] == pytest.approx((0.6666667 + 1.0) / 2.0, abs=1e-3)
    # Water/bare pixel (0.4, 0.1) has raw ndvi = -0.3/0.5 = -0.6 -> rescaled = (-0.6+1)/2 = 0.2
    assert scaled_ndvi[1] == pytest.approx((-0.6 + 1.0) / 2.0, abs=1e-3)


def test_extract_landsat_lst():
    # Landsat C2 Level-2 Surface Temperature DN formula: DN * 0.00341802 + 149.0
    dn = np.array([44180.0])
    lst_kelvin = extract_landsat_lst(dn)
    
    expected_kelvin = 44180.0 * 0.00341802 + 149.0  # ~300.008 K (~26.85 °C)
    assert lst_kelvin[0] == pytest.approx(expected_kelvin, abs=1e-2)
    assert lst_kelvin[0] > 250.0  # reasonable Kelvin bound


@pytest.mark.integration
def test_live_planetary_computer_stac_keyless():
    url = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
    bbox = (106.82, -6.18, 106.83, -6.17)
    payload = build_planetary_computer_stac_query("sentinel-2-l2a", bbox, max_cloud_cover=20.0)
    
    resp = requests.post(url, json=payload, timeout=20)
    assert resp.status_code == 200
    data = resp.json()
    assert "features" in data
    assert len(data["features"]) > 0
