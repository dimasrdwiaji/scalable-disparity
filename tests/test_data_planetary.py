import numpy as np
import pytest
import requests

from phys_living_index.data.ingest_context import (
    build_planetary_computer_stac_query,
    compute_bsi,
    compute_mndwi,
    compute_ndbi,
    compute_ndvi,
    extract_landsat_lst,
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


def test_compute_ndvi_true_range():
    # Dense vegetation: NIR high, Red low
    red = np.array([0.1, 0.4, 0.0])
    nir = np.array([0.5, 0.1, 0.0])

    ndvi = compute_ndvi(nir, red)

    # Check true remote sensing range [-1.0, 1.0]
    assert np.all(ndvi >= -1.0)
    assert np.all(ndvi <= 1.0)

    # Dense canopy (red=0.1, nir=0.5): (0.5 - 0.1) / (0.5 + 0.1) = 0.4 / 0.6 ≈ 0.667
    assert ndvi[0] == pytest.approx(0.4 / 0.6, abs=1e-3)
    # Water/asphalt (red=0.4, nir=0.1): (0.1 - 0.4) / (0.1 + 0.4) = -0.3 / 0.5 = -0.6
    assert ndvi[1] == pytest.approx(-0.6, abs=1e-3)


def test_compute_ndbi_builtup():
    # Built-up impervious surfaces: SWIR1 high, NIR lower
    swir1 = np.array([0.45, 0.10])
    nir = np.array([0.15, 0.50])

    ndbi = compute_ndbi(swir1, nir)

    assert np.all(ndbi >= -1.0)
    assert np.all(ndbi <= 1.0)
    # Concrete/roof pixel (swir1=0.45, nir=0.15): (0.45 - 0.15) / (0.45 + 0.15) = 0.3 / 0.6 = +0.5
    assert ndbi[0] == pytest.approx(0.5, abs=1e-3)
    # Dense vegetation pixel (swir1=0.10, nir=0.50): (0.10 - 0.50) / (0.10 + 0.50) = -0.4 / 0.6 ≈ -0.667
    assert ndbi[1] == pytest.approx(-0.4 / 0.6, abs=1e-3)


def test_compute_mndwi_water():
    # Surface water / drainage: Green high, SWIR1 strongly absorbed (very low)
    green = np.array([0.40, 0.10])
    swir1 = np.array([0.10, 0.40])

    mndwi = compute_mndwi(green, swir1)

    assert np.all(mndwi >= -1.0)
    assert np.all(mndwi <= 1.0)
    # Open water (green=0.4, swir1=0.1): (0.4 - 0.1) / (0.4 + 0.1) = 0.3 / 0.5 = +0.6
    assert mndwi[0] == pytest.approx(0.6, abs=1e-3)
    # Non-water (green=0.1, swir1=0.4): (0.1 - 0.4) / (0.1 + 0.4) = -0.6
    assert mndwi[1] == pytest.approx(-0.6, abs=1e-3)


def test_compute_bsi_bare_soil():
    # Bare soil / dirt road: SWIR1 and Red high; NIR and Blue lower
    swir1 = np.array([0.45])
    red = np.array([0.35])
    nir = np.array([0.20])
    blue = np.array([0.15])

    bsi = compute_bsi(swir1, red, nir, blue)

    assert np.all(bsi >= -1.0)
    assert np.all(bsi <= 1.0)
    # ((0.45 + 0.35) - (0.20 + 0.15)) / ((0.45 + 0.35) + (0.20 + 0.15)) = (0.80 - 0.35) / (0.80 + 0.35) = 0.45 / 1.15 ≈ 0.391
    assert bsi[0] == pytest.approx(0.45 / 1.15, abs=1e-3)


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
