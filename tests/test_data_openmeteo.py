import geopandas as gpd
import numpy as np
import pytest

from phys_living_index.data.ingest_context import (
    OPENMETEO_AIR_QUALITY_VARIABLES,
    build_openmeteo_hourly_params,
    fetch_openmeteo_hourly_median,
    generate_sampling_grid,
    summarize_hourly_median,
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


def test_build_openmeteo_hourly_params_batches_and_dates():
    points = [(round(0.1 * i, 3), round(0.1 * i, 3)) for i in range(25)]
    batches = build_openmeteo_hourly_params(points, "2023-01-01", "2023-12-31", max_batch_size=10)

    assert len(batches) == 3
    assert len(batches[0]["latitude"].split(",")) == 10
    assert len(batches[2]["latitude"].split(",")) == 5
    assert batches[0]["start_date"] == "2023-01-01"
    assert batches[0]["end_date"] == "2023-12-31"
    assert "current" not in batches[0]


def test_summarize_hourly_median_ignores_missing_hours():
    items = [{
        "latitude": -6.2,
        "longitude": 106.8,
        "hourly": {"pm2_5": [10.0, None, 30.0, 20.0], "nitrogen_dioxide": [None, None]},
    }]
    df = summarize_hourly_median(items, ["pm2_5", "nitrogen_dioxide"])

    assert df.loc[0, "pm2_5_median"] == pytest.approx(20.0)
    assert df.loc[0, "pm2_5_n_hours"] == 3
    assert np.isnan(df.loc[0, "nitrogen_dioxide_median"])
    assert df.loc[0, "nitrogen_dioxide_n_hours"] == 0


def test_summarize_hourly_median_raises_without_hourly_block():
    with pytest.raises(ValueError, match="hourly"):
        summarize_hourly_median([{"latitude": 0.0, "longitude": 0.0, "current": {}}], ["pm2_5"])


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
def test_live_openmeteo_hourly_median(tmp_path):
    out_parquet = tmp_path / "air_quality.parquet"

    res = fetch_openmeteo_hourly_median([(-6.17, 106.82)], "2023-06-01", "2023-06-07", out_parquet)
    assert res.exists()

    gdf = gpd.read_parquet(res)
    assert len(gdf) == 1
    assert gdf.loc[0, "pm2_5_n_hours"] > 0
