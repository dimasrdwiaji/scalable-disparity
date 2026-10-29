import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
import rasterio
from shapely.geometry import box

from phys_living_index.data.ingest_buildings import (
    build_open_buildings_query,
    derive_floor_count,
    fetch_open_buildings_filtered,
    filter_by_confidence,
    intersect_residential_mask,
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


def test_derive_floor_count_height_only():
    # Heights tested with GHSL standard: 3.0m for < 35m, 3.6m for >= 35m
    heights = pd.Series([0.0, 1.5, 2.9, 3.0, 5.9, 6.0, 9.1, 30.0, 36.0, 72.0])
    floors = derive_floor_count(heights)
    # 0m -> 1, 1.5m -> 1, 2.9m -> 1, 3m -> 1, 5.9m -> 1, 6m -> 2, 9.1m -> 3, 30m -> 10,
    # 36m (>=35m, 36/3.6) -> 10, 72m (72/3.6) -> 20
    expected = [1, 1, 1, 1, 1, 2, 3, 10, 10, 20]
    assert list(floors) == expected


def test_derive_floor_count_explicit_attributes():
    # When explicit floor attributes exist, they must take precedence over height
    df = pd.DataFrame({
        "id": ["b1", "b2", "b3"],
        "height": [10.0, 15.0, 30.0],
        "num_floors": [4, 6, np.nan],  # b1 has 4 floors, b2 has 6 floors, b3 missing
    })
    floors = derive_floor_count(df)
    # b1: explicit 4; b2: explicit 6; b3: derived from height 30/3 = 10
    assert list(floors) == [4, 6, 10]


def test_derive_floor_count_subtype_stratification():
    # Test commercial vs residential international GHSL benchmarks
    df = pd.DataFrame({
        "id": ["res1", "comm1"],
        "height": [18.0, 18.0],
        "subtype": ["residential", "commercial"],
    })
    floors = derive_floor_count(df)
    # res1: 18 / 3.0 = 6 floors
    # comm1: 18 / 3.6 = 5 floors
    assert list(floors) == [6, 5]


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
    assert {"id", "geometry", "height", "confidence", "floor_count"}.issubset(gdf.columns)
    assert np.all(gdf["confidence"] >= 0.65)
    assert np.all(gdf["floor_count"] >= 1)
