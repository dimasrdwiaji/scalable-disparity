from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box, Polygon, Point
import rasterio
import pytest

from phys_living_index.data.ingest_buildings import (
    build_open_buildings_query,
    filter_by_confidence,
    derive_floor_count,
    intersect_residential_mask,
    fetch_open_buildings_filtered,
)


def test_build_open_buildings_query():
    bbox = (106.8, -6.2, 106.9, -6.1)
    query = build_open_buildings_query(bbox=bbox, min_confidence=0.70)
    assert isinstance(query, str)
    assert "bbox.xmin >= 106.8" in query
    assert "bbox.ymin >= -6.2" in query
    assert "bbox.xmax <= 106.9" in query
    assert "bbox.ymax <= -6.1" in query
    assert "confidence >= 0.7" in query
    assert "ST_AsText(geometry)" in query


def test_filter_by_confidence():
    geoms = [box(0, 0, 1, 1), box(1, 1, 2, 2), box(2, 2, 3, 3), box(3, 3, 4, 4)]
    gdf = gpd.GeoDataFrame(
        {
            "id": ["b1", "b2", "b3", "b4"],
            "confidence": [0.50, 0.649, 0.650, 0.850],
            "height": [3.0, 6.0, 9.0, 12.0],
        },
        geometry=geoms,
        crs="EPSG:4326",
    )
    filtered = filter_by_confidence(gdf, min_confidence=0.65)
    assert len(filtered) == 2
    assert list(filtered["id"]) == ["b3", "b4"]
    assert np.all(filtered["confidence"] >= 0.65)


def test_derive_floor_count():
    heights = pd.Series([0.0, 1.5, 2.9, 3.0, 5.9, 6.0, 9.1, 30.0])
    floors = derive_floor_count(heights, floor_height=3.0)
    expected = [1, 1, 1, 1, 1, 2, 3, 10]
    assert list(floors) == expected


def test_intersect_residential_mask():
    # Building 1 is inside residential zone, Building 2 is outside
    b1 = box(0.1, 0.1, 0.5, 0.5)
    b2 = box(10.0, 10.0, 11.0, 11.0)
    buildings = gpd.GeoDataFrame(
        {"id": ["res_bldg", "ind_bldg"], "height": [5.0, 15.0]},
        geometry=[b1, b2],
        crs="EPSG:4326",
    )
    # Residential mask covering [0, 0, 1, 1]
    res_mask = gpd.GeoDataFrame(
        {"class": ["residential"]},
        geometry=[box(0, 0, 1, 1)],
        crs="EPSG:4326",
    )
    masked = intersect_residential_mask(buildings, res_mask)
    assert len(masked) == 1
    assert masked.iloc[0]["id"] == "res_bldg"


def test_intersect_residential_raster_mask(tmp_path):
    # Test GeoTIFF raster mask handling
    mask_tif = tmp_path / "ghs_built_c.tif"
    transform = rasterio.transform.from_bounds(0.0, 0.0, 2.0, 2.0, 2, 2)
    # 2x2 grid: upper-left is 1 (residential), rest is 0 (non-residential)
    # Note: in raster coords, row 0 is top (lat 1-2), row 1 is bottom (lat 0-1)
    data = np.array([[1, 0], [0, 0]], dtype=np.uint8)
    with rasterio.open(
        mask_tif, "w", driver="GTiff", height=2, width=2, count=1, dtype="uint8", crs="EPSG:4326", transform=transform
    ) as dst:
        dst.write(data, 1)

    b1 = box(0.1, 1.1, 0.5, 1.5)  # in residential pixel (0.0-1.0, 1.0-2.0)
    b2 = box(1.1, 0.1, 1.5, 0.5)  # in non-residential pixel
    buildings = gpd.GeoDataFrame(
        {"id": ["b1", "b2"], "height": [3.0, 6.0]},
        geometry=[b1, b2],
        crs="EPSG:4326",
    )
    masked = intersect_residential_mask(buildings, mask_tif)
    assert len(masked) == 1
    assert masked.iloc[0]["id"] == "b1"


@pytest.mark.integration
def test_live_open_buildings_small_sub_bbox(tmp_path):
    # Small test bbox in Central Jakarta
    bbox = (106.82, -6.18, 106.825, -6.175)
    out_file = tmp_path / "buildings.parquet"
    res = fetch_open_buildings_filtered(bbox, output_parquet=out_file, min_confidence=0.65)
    
    assert res.exists()
    gdf = gpd.read_parquet(res)
    assert len(gdf) > 0
    assert set(["id", "geometry", "height", "confidence", "floor_count"]).issubset(gdf.columns)
    assert np.all(gdf["confidence"] >= 0.65)
    assert np.all(gdf["floor_count"] >= 1)
