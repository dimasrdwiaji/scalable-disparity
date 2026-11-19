"""
Builds compact GeoJSON/JSON payloads from Stage 3 outputs and serves an interactive
MapLibre GL JS web map on localhost for visual inspection of inputs and results.
"""

import json
import logging
import math
from functools import partial
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd

from ..validation.validate_kotaku import (
    MAINLAND_DKI_MUNICIPALITIES,
    compute_h3_kotaku_spatial_overlap,
)

logger = logging.getLogger(__name__)

TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "map.html"

HEX_EXPORT_COLUMNS: tuple[str, ...] = (
    "is_residential",
    "is_modelled",
    "has_complete_features",
    "smod_code",
    "res_share_lt50",
    "res_share_lt60",
    "res_nn_p25",
    "ndvi",
    "dlst_local_ring_k5",
    "dlst_city_median",
    "lst_k",
    "ghs_res_share",
    "residential_building_count",
    "building_count",
    "removed_nonres_wall_m2",
    "s2_tier",
    "lst_tier",
    "res_share_lt50_scaled",
    "res_nn_p25_scaled",
    "vegetation_ndvi_scaled",
    "dlst_local_ring_k5_scaled",
)

ALLOWED_DATA_FILES: frozenset[str] = frozenset({
    "hexagons.geojson",
    "dki_slums.geojson",
    "karawang_slums.geojson",
    "admin_boundaries.geojson",
    "osm_nonres_zones.geojson",
    "summary.json",
})


def _sanitize_value(value: Any, decimals: int = 4) -> Any:
    """Converts pandas/numpy scalars and NaN/Inf values into strict JSON-safe primitives."""
    if value is None:
        return None
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        fval = float(value)
        if not math.isfinite(fval):
            return None
        return round(fval, decimals)
    if pd.isna(value):
        return None
    return str(value)


def _round_coords(coords: Any, precision: int = 5) -> Any:
    """Recursively rounds GeoJSON coordinate tuples to reduce payload size."""
    if isinstance(coords, (list, tuple)):
        if coords and isinstance(coords[0], (int, float)):
            return [round(float(coords[0]), precision), round(float(coords[1]), precision)]
        return [_round_coords(c, precision) for c in coords]
    return coords


def _gdf_to_compact_geojson(
    gdf: gpd.GeoDataFrame,
    prop_cols: list[str],
    coord_precision: int = 5,
    simplify_tolerance_m: float | None = None,
) -> dict[str, Any]:
    """Serializes a GeoDataFrame to a strict, compact GeoJSON FeatureCollection."""
    if len(gdf) == 0:
        return {"type": "FeatureCollection", "features": []}

    work = gdf.copy()
    if work.crs is not None and work.crs.to_epsg() != 4326:
        work = work.to_crs(epsg=4326)

    if simplify_tolerance_m is not None and simplify_tolerance_m > 0:
        metric_crs = "EPSG:32748"
        simplified = work.geometry.to_crs(metric_crs).simplify(simplify_tolerance_m, preserve_topology=True)
        work = work.set_geometry(simplified.to_crs(epsg=4326))

    keep_cols = [c for c in prop_cols if c in work.columns]
    features: list[dict[str, Any]] = []
    for _, row in work.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        geo_iface = geom.__geo_interface__
        geo_iface = {
            "type": geo_iface["type"],
            "coordinates": _round_coords(geo_iface["coordinates"], coord_precision),
        }
        props = {col: _sanitize_value(row[col]) for col in keep_cols}
        features.append({"type": "Feature", "geometry": geo_iface, "properties": props})

    return {"type": "FeatureCollection", "features": features}


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, allow_nan=False, separators=(",", ":")), encoding="utf-8")
    return path


def _attach_validation_labels(
    hex_gdf: gpd.GeoDataFrame,
    root: Path,
) -> gpd.GeoDataFrame:
    """Attaches official Mainland DKI Pergub 90 and Karawang Kotaku overlap attributes to H3 cells."""
    out = hex_gdf.copy()
    adm_path = root / "data" / "interim" / "admin_boundaries_study_area.geojson"
    dki_path = root / "data" / "validation" / "dki_rw_kumuh_pergub90.geojson"
    krw_path = root / "data" / "validation" / "kotaku_sk_kumuh_karawang.geojson"

    adm = gpd.read_file(adm_path) if adm_path.exists() else None

    if dki_path.exists():
        dki = gpd.read_file(dki_path)
        dki_ov = compute_h3_kotaku_spatial_overlap(
            out[["h3_index", "geometry"]],
            dki,
            overlap_threshold=0.10,
            jurisdiction_gdf=adm,
            include_names=MAINLAND_DKI_MUNICIPALITIES if adm is not None else None,
        ).set_index("h3_index")
        out["dki_slum_status"] = out["h3_index"].map(
            dki_ov["is_slum"].map({1.0: "Official Slum", 0.0: "Formal / Non-Slum"})
        )
        out["dki_severity"] = out["h3_index"].map(dki_ov["KAT_TEXT"]) if "KAT_TEXT" in dki_ov.columns else None
        out["dki_kelurahan"] = out["h3_index"].map(dki_ov["KELURAHAN"]) if "KELURAHAN" in dki_ov.columns else None
        out["dki_rw"] = out["h3_index"].map(dki_ov["RW"]) if "RW" in dki_ov.columns else None

    if krw_path.exists():
        krw = gpd.read_file(krw_path)
        krw_ov = compute_h3_kotaku_spatial_overlap(
            out[["h3_index", "geometry"]],
            krw,
            overlap_threshold=0.10,
            jurisdiction_gdf=adm,
            include_names=["Kabupaten Karawang"] if adm is not None else None,
        ).set_index("h3_index")
        out["karawang_slum_status"] = out["h3_index"].map(
            krw_ov["is_slum"].map({1.0: "Kotaku Slum", 0.0: "Non-Slum"})
        )

    return out


def export_map_assets(
    root: str | Path,
    output_dir: str | Path | None = None,
    rebuild: bool = False,
) -> dict[str, Path]:
    """
    Exports compact GeoJSON layers and QA summary metadata for the localhost web map.

    Parameters
    ----------
    root : str | Path
        Project/data root containing `data/processed/h3_hexagons.parquet`.
    output_dir : str | Path | None
        Destination directory (defaults to `<root>/data/processed/map`).
    rebuild : bool
        If False and all primary assets already exist, returns cached paths immediately.
    """
    root = Path(root)
    map_dir = Path(output_dir) if output_dir else root / "data" / "processed" / "map"
    map_dir.mkdir(parents=True, exist_ok=True)

    hex_out = map_dir / "hexagons.geojson"
    summary_out = map_dir / "summary.json"
    if not rebuild and hex_out.exists() and summary_out.exists():
        logger.info("Using cached web map assets in %s", map_dir)
        return {name: map_dir / name for name in ALLOWED_DATA_FILES if (map_dir / name).exists()}

    hex_parquet = root / "data" / "processed" / "h3_hexagons.parquet"
    if not hex_parquet.exists():
        raise FileNotFoundError(f"Missing Stage 3 GeoParquet: {hex_parquet}")

    hex_gdf = gpd.read_parquet(hex_parquet)
    if hex_gdf.index.name == "h3_index" and "h3_index" not in hex_gdf.columns:
        hex_gdf = hex_gdf.reset_index()
    elif "h3_index" not in hex_gdf.columns:
        hex_gdf = hex_gdf.assign(h3_index=hex_gdf.index.astype(str))

    hex_gdf = _attach_validation_labels(hex_gdf, root)
    hex_cols = [
        "h3_index",
        *HEX_EXPORT_COLUMNS,
        "dki_slum_status",
        "dki_severity",
        "dki_kelurahan",
        "dki_rw",
        "karawang_slum_status",
    ]
    _write_json(hex_out, _gdf_to_compact_geojson(hex_gdf, hex_cols, coord_precision=5))

    outputs: dict[str, Path] = {"hexagons.geojson": hex_out}

    dki_path = root / "data" / "validation" / "dki_rw_kumuh_pergub90.geojson"
    if dki_path.exists():
        dki_gdf = gpd.read_file(dki_path)
        _write_json(
            map_dir / "dki_slums.geojson",
            _gdf_to_compact_geojson(dki_gdf, ["WILAYAH", "KECAMATAN", "KELURAHAN", "RW", "KAT_TEXT"], 5),
        )
        outputs["dki_slums.geojson"] = map_dir / "dki_slums.geojson"

    krw_path = root / "data" / "validation" / "kotaku_sk_kumuh_karawang.geojson"
    if krw_path.exists():
        krw_gdf = gpd.read_file(krw_path)
        krw_cols = [c for c in ("Kecamatan", "Kelurahan", "RT", "Tipologi", "Luas_Ha") if c in krw_gdf.columns]
        _write_json(map_dir / "karawang_slums.geojson", _gdf_to_compact_geojson(krw_gdf, krw_cols, 5))
        outputs["karawang_slums.geojson"] = map_dir / "karawang_slums.geojson"

    adm_path = root / "data" / "interim" / "admin_boundaries_study_area.geojson"
    if adm_path.exists():
        adm_gdf = gpd.read_file(adm_path)
        _write_json(
            map_dir / "admin_boundaries.geojson",
            _gdf_to_compact_geojson(adm_gdf, ["clean_name", "admin_level"], 5, simplify_tolerance_m=40.0),
        )
        outputs["admin_boundaries.geojson"] = map_dir / "admin_boundaries.geojson"

    nonres_path = root / "data" / "interim" / "osm_nonres_zones.parquet"
    if nonres_path.exists():
        nonres_gdf = gpd.read_parquet(nonres_path)
        _write_json(
            map_dir / "osm_nonres_zones.geojson",
            _gdf_to_compact_geojson(nonres_gdf, ["landuse"], 5, simplify_tolerance_m=15.0),
        )
        outputs["osm_nonres_zones.geojson"] = map_dir / "osm_nonres_zones.geojson"

    qa_path = root / "data" / "processed" / "stage3_qa.json"
    qa_data = json.loads(qa_path.read_text(encoding="utf-8")) if qa_path.exists() else {}
    summary = {
        "total_cells": int(len(hex_gdf)),
        "urban_cells": int(hex_gdf["is_residential"].sum()) if "is_residential" in hex_gdf.columns else 0,
        "non_urban_cells": int((~hex_gdf["is_residential"]).sum()) if "is_residential" in hex_gdf.columns else 0,
        "modelled_cells": int(hex_gdf["is_modelled"].sum()) if "is_modelled" in hex_gdf.columns else 0,
        "active_dimensions": qa_data.get("active_dimensions", 4),
        "center_lon": float(hex_gdf["lon"].median()) if "lon" in hex_gdf.columns else 106.85,
        "center_lat": float(hex_gdf["lat"].median()) if "lat" in hex_gdf.columns else -6.25,
        "available_layers": sorted(outputs.keys()),
    }
    _write_json(summary_out, summary)
    outputs["summary.json"] = summary_out
    logger.info("Exported %d web map assets to %s", len(outputs), map_dir)
    return outputs


class _MapRequestHandler(BaseHTTPRequestHandler):
    """Serves the single-page web map and exported GeoJSON/JSON assets."""

    def __init__(self, *args: Any, map_dir: Path, template_path: Path, **kwargs: Any) -> None:
        self.map_dir = map_dir
        self.template_path = template_path
        super().__init__(*args, **kwargs)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        logger.debug("HTTP %s - %s", self.address_string(), format % args)

    def do_GET(self) -> None:
        route = self.path.split("?", 1)[0]
        if route in ("/", "/index.html"):
            if not self.template_path.exists():
                self.send_error(HTTPStatus.NOT_FOUND, "Map template not found")
                return
            body = self.template_path.read_bytes()
            self._send_bytes(body, "text/html; charset=utf-8")
            return

        if route.startswith("/data/"):
            filename = route[len("/data/") :]
            if filename not in ALLOWED_DATA_FILES:
                self.send_error(HTTPStatus.NOT_FOUND, "Unknown map asset")
                return
            target = self.map_dir / filename
            if not target.exists():
                self.send_error(HTTPStatus.NOT_FOUND, f"Missing map asset: {filename}")
                return
            self._send_bytes(target.read_bytes(), "application/json; charset=utf-8")
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def _send_bytes(self, body: bytes, content_type: str) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)


def make_map_handler(
    map_dir: str | Path,
    template_path: str | Path | None = None,
) -> type[BaseHTTPRequestHandler]:
    """Returns a request handler class bound to `map_dir` and `template_path`."""
    resolved_dir = Path(map_dir).resolve()
    resolved_tpl = Path(template_path).resolve() if template_path else TEMPLATE_PATH
    return partial(_MapRequestHandler, map_dir=resolved_dir, template_path=resolved_tpl)  # type: ignore[return-value]
