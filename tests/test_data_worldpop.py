from pathlib import Path
import pytest
import rasterio
import numpy as np

from phys_living_index.data.ingest_context import (
    build_worldpop_request,
    fetch_worldpop,
)


def test_build_worldpop_request():
    bbox = (106.8, -6.3, 107.0, -6.1)
    req = build_worldpop_request(bbox, country_iso="IDN", year=2020)
    
    assert req["bbox"] == (106.8, -6.3, 107.0, -6.1)
    assert req["country_iso"] == "IDN"
    assert req["year"] == 2020
    assert "https://data.worldpop.org/GIS/Population/Individual_countries/IDN/idn_ppp_2020_UNadj.tif" in req["url"]


@pytest.mark.integration
def test_live_worldpop_small_sub_bbox(tmp_path):
    bbox = (106.82, -6.18, 106.85, -6.15)
    out_file = tmp_path / "worldpop_clipped.tif"
    
    res = fetch_worldpop(bbox, out_file)
    assert res.exists()
    
    with rasterio.open(res) as src:
        assert src.crs.to_epsg() == 4326
        data = src.read(1)
        assert data.shape[0] > 0
        assert data.shape[1] > 0
        valid = data[data >= 0]
        assert len(valid) > 0
        assert np.sum(valid) > 0
