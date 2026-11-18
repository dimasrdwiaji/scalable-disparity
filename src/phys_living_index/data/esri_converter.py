"""
Utilities for normalizing ArcGIS REST / WebMap Esri JSON geometries into standard WGS84 GeoJSON.
"""

from typing import Any

from pyproj import Transformer


def convert_esri_rings_to_geojson_polygon(
    rings: list[list[list[float]]],
    source_epsg: int = 3857,
    target_epsg: int = 4326,
) -> dict[str, Any]:
    """
    Transforms Esri JSON polygon rings into standard GeoJSON coordinates,
    reprojecting from source CRS (default Web Mercator EPSG:3857) to WGS84 (EPSG:4326).

    Args:
        rings: List of rings, where each ring is a list of [x, y] coordinates.
        source_epsg: Source EPSG code (default 3857).
        target_epsg: Target EPSG code (default 4326).

    Returns:
        GeoJSON geometry dict with type 'Polygon' and reprojected coordinates.
    """
    if source_epsg == target_epsg:
        return {
            "type": "Polygon",
            "coordinates": rings,
        }

    transformer = Transformer.from_crs(
        f"EPSG:{source_epsg}",
        f"EPSG:{target_epsg}",
        always_xy=True,
    )

    geojson_coordinates = []
    for ring in rings:
        reprojected_ring = [
            list(transformer.transform(pt[0], pt[1]))
            for pt in ring
        ]
        geojson_coordinates.append(reprojected_ring)

    return {
        "type": "Polygon",
        "coordinates": geojson_coordinates,
    }


def convert_esri_featureset_to_geojson(
    features: list[dict[str, Any]],
    source_epsg: int = 3857,
    target_epsg: int = 4326,
) -> dict[str, Any]:
    """
    Converts an ArcGIS REST feature set containing Esri geometries and attributes
    into a standard WGS84 GeoJSON FeatureCollection.

    Args:
        features: List of Esri feature dictionaries containing 'geometry' and 'attributes'.
        source_epsg: Source EPSG code (default 3857).
        target_epsg: Target EPSG code (default 4326).

    Returns:
        Standard GeoJSON FeatureCollection dictionary.
    """
    geojson_features = []
    for feat in features:
        geom = feat.get("geometry")
        attrs = feat.get("attributes") or feat.get("properties") or {}

        if geom and "rings" in geom:
            sr = geom.get("spatialReference", {})
            feat_epsg = sr.get("latestWkid") or sr.get("wkid") or source_epsg
            norm_geom = convert_esri_rings_to_geojson_polygon(
                rings=geom["rings"],
                source_epsg=feat_epsg,
                target_epsg=target_epsg,
            )
        else:
            norm_geom = geom

        geojson_features.append({
            "type": "Feature",
            "geometry": norm_geom,
            "properties": attrs,
        })

    return {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {"name": f"urn:ogc:def:crs:EPSG::{target_epsg}"},
        },
        "features": geojson_features,
    }
