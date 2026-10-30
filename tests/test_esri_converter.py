"""
Unit tests for ArcGIS REST Esri JSON geometry conversion to GeoJSON.
"""

import pytest

from phys_living_index.data.esri_converter import (
    convert_esri_featureset_to_geojson,
    convert_esri_rings_to_geojson_polygon,
)


def test_convert_esri_rings_to_geojson_polygon():
    # Synthetic Web Mercator coordinates near Jakarta (106.8° E, -6.2° S)
    rings = [
        [
            [11888931.0, -691880.0],
            [11890000.0, -691880.0],
            [11890000.0, -690000.0],
            [11888931.0, -690000.0],
            [11888931.0, -691880.0],
        ]
    ]

    geom = convert_esri_rings_to_geojson_polygon(rings, source_epsg=3857, target_epsg=4326)

    assert geom["type"] == "Polygon"
    assert len(geom["coordinates"]) == 1
    coords = geom["coordinates"][0]
    assert len(coords) == 5

    # Check longitude and latitude range in WGS84
    for lon, lat in coords:
        assert 106.0 <= lon <= 107.0
        assert -7.0 <= lat <= -6.0


def test_convert_esri_featureset_to_geojson():
    features = [
        {
            "geometry": {
                "rings": [
                    [
                        [11888931.0, -691880.0],
                        [11890000.0, -691880.0],
                        [11890000.0, -690000.0],
                        [11888931.0, -690000.0],
                        [11888931.0, -691880.0],
                    ]
                ],
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            },
            "attributes": {"FID": 1, "Nama": "Kampung Test", "k1_a_p": 50.0},
        }
    ]

    fc = convert_esri_featureset_to_geojson(features)

    assert fc["type"] == "FeatureCollection"
    assert len(fc["features"]) == 1
    f0 = fc["features"][0]
    assert f0["type"] == "Feature"
    assert f0["geometry"]["type"] == "Polygon"
    assert f0["properties"]["Nama"] == "Kampung Test"
    assert f0["properties"]["k1_a_p"] == 50.0
    assert pytest.approx(f0["geometry"]["coordinates"][0][0][0], 1e-2) == 106.8
