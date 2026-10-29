import geopandas as gpd
import pytest

from phys_living_index.data.ingest_context import (
    OPENMETEO_AIR_QUALITY_VARIABLES,
    batch_locations,
    fetch_openmeteo_air_quality,
    generate_sampling_grid,
)


def test_generate_sampling_grid():
    bbox = (106.80, -6.20, 106.82, -6.18)
    step = 0.005
    points = generate_sampling_grid(bbox, step_deg=step)

    assert len(points) > 0
    # Every point should be within bbox
    for lat, lon in points:
        assert -6.20 <= lat <= -6.18
        assert 106.80 <= lon <= 106.82


def test_batch_locations():
    points = [(round(0.1 * i, 3), round(0.1 * i, 3)) for i in range(125)]
    batches = batch_locations(points, max_batch_size=50)

    assert len(batches) == 3
    # Check first batch has 50 points
    lats = batches[0]["latitude"].split(",")
    lons = batches[0]["longitude"].split(",")
    assert len(lats) == 50
    assert len(lons) == 50
    # Check last batch has 25 points
    lats_last = batches[2]["latitude"].split(",")
    assert len(lats_last) == 25


def test_non_pollen_variable_list():
    # Primary fine particulates
    assert "pm2_5" in OPENMETEO_AIR_QUALITY_VARIABLES
    assert "pm10" in OPENMETEO_AIR_QUALITY_VARIABLES

    # Gaseous pollutants
    assert "carbon_monoxide" in OPENMETEO_AIR_QUALITY_VARIABLES
    assert "nitrogen_dioxide" in OPENMETEO_AIR_QUALITY_VARIABLES
    assert "sulphur_dioxide" in OPENMETEO_AIR_QUALITY_VARIABLES
    assert "ozone" in OPENMETEO_AIR_QUALITY_VARIABLES

    # Official regulatory composite indices
    assert "european_aqi" in OPENMETEO_AIR_QUALITY_VARIABLES
    assert "us_aqi" in OPENMETEO_AIR_QUALITY_VARIABLES

    # Confirm temperate European pollen variables are strictly excluded
    pollen_vars = [v for v in OPENMETEO_AIR_QUALITY_VARIABLES if "pollen" in v.lower()]
    assert len(pollen_vars) == 0


@pytest.mark.integration
def test_live_openmeteo_air_quality_integration(tmp_path):
    bbox = (106.82, -6.18, 106.83, -6.17)
    out_parquet = tmp_path / "air_quality.parquet"

    res = fetch_openmeteo_air_quality(bbox, out_parquet, step_deg=0.01)
    assert res.exists()

    gdf = gpd.read_parquet(res)
    assert len(gdf) > 0
    assert "pm2_5" in gdf.columns
    assert "us_aqi" in gdf.columns
    assert "european_aqi" in gdf.columns
    # Pollen must be absent
    assert not any("pollen" in col.lower() for col in gdf.columns)
