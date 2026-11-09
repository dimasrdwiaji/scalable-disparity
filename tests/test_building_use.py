import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Point, Polygon, box

from phys_living_index.features.building_use import (
    classify_large_low_shape,
    classify_osm_zones,
    compute_isoperimetric_compactness,
    compute_rectangularity,
    compute_rescaled_ghs_ratio,
)


def test_compute_rectangularity():
    # Perfect rectangle: area == min rotated rectangle area -> rectangularity == 1.0
    rect = box(0, 0, 10, 20)
    assert compute_rectangularity(rect) == pytest.approx(1.0, abs=1e-3)

    # L-shaped polygon has lower rectangularity
    l_shape = Polygon([(0, 0), (10, 0), (10, 5), (5, 5), (5, 20), (0, 20)])
    # l_shape area = 50 + 75 = 125; min rotated rect (0,0 to 10,20) = 200 -> ratio = 125/200 = 0.625
    assert compute_rectangularity(l_shape) < 0.70


def test_compute_isoperimetric_compactness():
    # Square: area = 100, perimeter = 40 -> 4 * pi * 100 / 1600 = pi / 4 ~ 0.785
    sq_compact = compute_isoperimetric_compactness(100.0, 40.0)
    assert sq_compact == pytest.approx(np.pi / 4.0, abs=1e-3)

    # Elongated strip: area = 10, perimeter = 22 -> 4 * pi * 10 / 484 ~ 0.259
    strip_compact = compute_isoperimetric_compactness(10.0, 22.0)
    assert strip_compact < 0.30

    # Vectorized / Series support
    areas = pd.Series([100.0, 10.0, 0.0])
    perims = pd.Series([40.0, 22.0, 0.0])
    res = compute_isoperimetric_compactness(areas, perims)
    assert res.iloc[0] == pytest.approx(np.pi / 4.0, abs=1e-3)
    assert res.iloc[1] < 0.30
    assert res.iloc[2] == 0.0


def test_classify_osm_zones():
    # 3 buildings:
    # 1 in industrial zone (always non-res)
    # 1 in commercial zone, small (< 200m2 -> shophouse/residential kept)
    # 1 in commercial zone, large (>= 200m2 -> non-res)
    # 1 outside any zone
    bldgs = gpd.GeoDataFrame({
        "footprint_m2": [500.0, 100.0, 300.0, 80.0],
        "geometry": [Point(1, 1), Point(10, 10), Point(10, 11), Point(50, 50)],
    }, crs="EPSG:4326")

    zones = gpd.GeoDataFrame({
        "landuse": ["industrial", "commercial", "commercial"],
        "geometry": [
            box(0, 0, 2, 2),
            box(9, 9, 12, 12),
            box(9, 9, 12, 12),
        ],
    }, crs="EPSG:4326")

    flags = classify_osm_zones(bldgs, zones, commercial_min_size=200.0)
    assert bool(flags.iloc[0]) is True   # industrial -> non-res
    assert bool(flags.iloc[1]) is False  # commercial < 200m2 -> not flagged
    assert bool(flags.iloc[2]) is True   # commercial >= 200m2 -> flagged non-res
    assert bool(flags.iloc[3]) is False  # outside -> not flagged


def test_classify_large_low_shape():
    areas = pd.Series([3000.0, 3000.0, 1200.0, 1200.0, 100.0])
    floors = pd.Series([2.0, 8.0, 1.0, 1.0, 1.0])
    rect = pd.Series([0.9, 0.9, 0.9, 0.6, 0.9])

    flags = classify_large_low_shape(
        areas,
        floors,
        rect,
        large_low_min_m2=2500.0,
        large_low_max_floors=3,
        rect_min_m2=1000.0,
        rect_min_rect=0.85,
        rect_max_floors=2,
        high_rise_exemption=6,
    )
    assert bool(flags.iloc[0]) is True   # 3000m2, 2 floors -> non-res
    assert bool(flags.iloc[1]) is False  # 3000m2, 8 floors -> apartment exemption
    assert bool(flags.iloc[2]) is True   # 1200m2, rect 0.9, 1 floor -> warehouse
    assert bool(flags.iloc[3]) is False  # 1200m2, rect 0.6 (irregular kampung roof) -> not flagged
    assert bool(flags.iloc[4]) is False  # 100m2 -> normal house


def test_rescaled_ghs_ratio():
    # Case 1: GHS nres is 50,000 m2. Rules already removed 30,000 m2. Residual GHS nres is 20,000 m2.
    # Unclassified footprint is 100,000 m2.
    # Expected ratio = (100,000 - 20,000) / 100,000 = 0.80
    r1 = compute_rescaled_ghs_ratio(
        ghs_total_m2=pd.Series([120000.0]),
        ghs_nres_m2=pd.Series([50000.0]),
        removed_nres_m2=pd.Series([30000.0]),
        unclassified_m2=pd.Series([100000.0]),
    )
    assert r1.iloc[0] == pytest.approx(0.80)

    # Case 2: Rules already removed MORE than GHS nres (e.g. removed 60,000 m2 vs GHS 50,000 m2).
    # Residual nres is 0. Ratio should be 1.0 (no double-penalty on unclassified homes).
    r2 = compute_rescaled_ghs_ratio(
        ghs_total_m2=pd.Series([120000.0]),
        ghs_nres_m2=pd.Series([50000.0]),
        removed_nres_m2=pd.Series([60000.0]),
        unclassified_m2=pd.Series([60000.0]),
    )
    assert r2.iloc[0] == pytest.approx(1.0)
