import json
import threading
import urllib.request

import geopandas as gpd
import h3
import numpy as np
from shapely.geometry import Polygon, box

from phys_living_index.visualization.web_map import export_map_assets, make_map_handler


def _h3_poly(cell: str) -> Polygon:
    return Polygon([(lng, lat) for lat, lng in h3.cell_to_boundary(cell)])


def test_export_map_assets_sanitizes_nan_and_exports_layers(tmp_path):
    cells = sorted(h3.grid_disk(h3.latlng_to_cell(-6.20, 106.84, 8), 1))[:4]
    hex_gdf = gpd.GeoDataFrame(
        {
            "h3_index": cells,
            "is_residential": [True, True, False, True],
            "is_modelled": [True, False, False, True],
            "has_complete_features": [True, False, False, True],
            "smod_code": [30, 23, 12, 30],
            "res_share_lt50": [0.42, 0.31, np.nan, 0.55],
            "res_share_lt60": [0.51, 0.40, np.nan, 0.63],
            "res_nn_p25": [6.8, 7.5, np.nan, 6.2],
            "ndvi": [0.18, 0.25, 0.61, 0.14],
            "dlst_local_ring_k5": [1.25, np.nan, np.nan, 0.85],
            "dlst_city_median": [5.1, np.nan, np.nan, 4.8],
            "lst_k": [314.2, np.nan, 303.1, 313.8],
            "ghs_res_share": [0.92, 0.88, 1.0, 0.79],
            "residential_building_count": [1200, 300, 0, 1850],
            "building_count": [1250, 310, 0, 2100],
            "removed_nonres_wall_m2": [1000.0, 200.0, 0.0, 4500.0],
            "s2_tier": [1, 1, 1, 1],
            "lst_tier": [1, 0, 1, 2],
            "lat": [h3.cell_to_latlng(c)[0] for c in cells],
            "lon": [h3.cell_to_latlng(c)[1] for c in cells],
            "geometry": [_h3_poly(c) for c in cells],
        },
        crs="EPSG:4326",
    )
    (tmp_path / "data" / "processed").mkdir(parents=True)
    (tmp_path / "data" / "interim").mkdir(parents=True)
    (tmp_path / "data" / "validation").mkdir(parents=True)
    hex_gdf.to_parquet(tmp_path / "data" / "processed" / "h3_hexagons.parquet")

    # Minimal validation & admin boundaries
    adm = gpd.GeoDataFrame(
        {"clean_name": ["Jakarta Pusat"], "admin_level": ["5"], "geometry": [box(106.75, -6.30, 106.95, -6.10)]},
        crs="EPSG:4326",
    )
    adm.to_file(tmp_path / "data" / "interim" / "admin_boundaries_study_area.geojson", driver="GeoJSON")
    dki = gpd.GeoDataFrame(
        {
            "WILAYAH": ["JAKARTA PUSAT"],
            "KECAMATAN": ["MENTENG"],
            "KELURAHAN": ["PEGANGSAAN"],
            "RW": ["001"],
            "KAT_TEXT": ["Sedang"],
            "geometry": [_h3_poly(cells[0])],
        },
        crs="EPSG:4326",
    )
    dki.to_file(tmp_path / "data" / "validation" / "dki_rw_kumuh_pergub90.geojson", driver="GeoJSON")
    nonres = gpd.GeoDataFrame({"landuse": ["industrial"], "geometry": [_h3_poly(cells[3])]}, crs="EPSG:4326")
    nonres.to_parquet(tmp_path / "data" / "interim" / "osm_nonres_zones.parquet")

    outputs = export_map_assets(tmp_path, rebuild=True)
    assert "hexagons.geojson" in outputs
    assert "dki_slums.geojson" in outputs
    assert "osm_nonres_zones.geojson" in outputs

    raw_text = outputs["hexagons.geojson"].read_text(encoding="utf-8")
    assert "NaN" not in raw_text
    geo = json.loads(raw_text)
    assert len(geo["features"]) == 4
    props_by_id = {f["properties"]["h3_index"]: f["properties"] for f in geo["features"]}
    assert props_by_id[cells[0]]["dki_slum_status"] == "Official Slum"
    assert props_by_id[cells[0]]["dki_severity"] == "Sedang"
    assert props_by_id[cells[2]]["is_residential"] is False
    assert props_by_id[cells[2]]["res_share_lt50"] is None

    summary = json.loads(outputs["summary.json"].read_text(encoding="utf-8"))
    assert summary["total_cells"] == 4
    assert summary["urban_cells"] == 3
    assert summary["non_urban_cells"] == 1
    assert summary["modelled_cells"] == 2


def test_map_http_handler_serves_html_geojson_and_blocks_unknown(tmp_path):
    from http.server import ThreadingHTTPServer

    map_dir = tmp_path / "map"
    map_dir.mkdir()
    (map_dir / "hexagons.geojson").write_text('{"type":"FeatureCollection","features":[]}', encoding="utf-8")

    server = ThreadingHTTPServer(("127.0.0.1", 0), make_map_handler(map_dir))
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as resp:
            assert resp.status == 200
            html = resp.read().decode("utf-8")
            assert "OpenStreetMap" in html
            assert "Local Surface Heat Anomaly" in html
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/data/hexagons.geojson") as resp:
            assert resp.status == 200
            assert json.loads(resp.read().decode("utf-8"))["type"] == "FeatureCollection"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
