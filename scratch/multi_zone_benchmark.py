import sys
sys.stdout.reconfigure(line_buffering=True)

import osmnx as ox
import networkx as nx
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse.csgraph import dijkstra
import scipy.sparse as sp
import duckdb

print("=" * 80, flush=True)
print("MULTI-ZONE BENCHMARK: OLD DIJKSTRA vs FIXED SEGMENT OVERTURE vs OSMNX vs EUCLIDEAN", flush=True)
print("=" * 80, flush=True)

con = duckdb.connect()
con.install_extension("spatial")
con.load_extension("spatial")
con.execute("SET geometry_always_xy = true;")

amenities_parquet = "data/raw/overture_amenities.parquet"
transport_parquet = "data/raw/overture_transportation.parquet"
df_raw = pd.read_parquet("data/interim/h3_features_raw.parquet")

zones = {
    "Central Jakarta Core (Menteng / Johar Baru)": (106.83, -6.20, 106.86, -6.17),
    "South Jakarta Mixed Dense (Tebet / Manggarai)": (106.84, -6.24, 106.87, -6.21),
    "Bekasi Municipality Center (Bekasi Barat)": (106.98, -6.25, 107.01, -6.22),
    "Karawang Industrial Urban Center": (107.28, -6.32, 107.31, -6.29),
}

all_zone_results = []

for z_name, (w, s, e, n) in zones.items():
    print(f"\nProcessing {z_name}...", flush=True)
    buf_deg = 1200.0 / 111000.0
    w_buf, s_buf, e_buf, n_buf = w - buf_deg, s - buf_deg, e + buf_deg, n + buf_deg

    # 1. Fixed Segment Overture
    q_seg = f"""
        WITH lines AS (
            SELECT id, geometry, ST_NPoints(geometry) as n_pts
            FROM read_parquet('{transport_parquet}')
            WHERE ST_X(ST_Centroid(geometry)) >= {w_buf} AND ST_X(ST_Centroid(geometry)) <= {e_buf}
              AND ST_Y(ST_Centroid(geometry)) >= {s_buf} AND ST_Y(ST_Centroid(geometry)) <= {n_buf}
        ),
        points AS (
            SELECT id, unnest(generate_series(1, n_pts - 1))::INTEGER as idx, geometry
            FROM lines
        ),
        raw_pts AS (
            SELECT 
                ST_X(ST_PointN(geometry, idx)) as x1,
                ST_Y(ST_PointN(geometry, idx)) as y1,
                ST_X(ST_PointN(geometry, (idx + 1)::INTEGER)) as x2,
                ST_Y(ST_PointN(geometry, (idx + 1)::INTEGER)) as y2
            FROM points
        )
        SELECT 
            x1, y1, x2, y2,
            ST_Distance_Spheroid(ST_Point(x1, y1), ST_Point(x2, y2)) as length_m
        FROM raw_pts
        WHERE length_m > 0.0
    """
    df_seg = con.execute(q_seg).df()
    
    p1 = np.round(df_seg[["x1", "y1"]].to_numpy(), 6)
    p2 = np.round(df_seg[["x2", "y2"]].to_numpy(), 6)
    all_pts = np.vstack([p1, p2])
    unique_pts, inv = np.unique(all_pts, axis=0, return_inverse=True)
    m = len(df_seg)
    u = inv[:m]
    v = inv[m:]
    w_arr = df_seg["length_m"].to_numpy(dtype=np.float64)
    adj = sp.csr_matrix((np.concatenate([w_arr, w_arr]), (np.concatenate([u, v]), np.concatenate([v, u]))), shape=(len(unique_pts), len(unique_pts)))
    tree_nodes = cKDTree(unique_pts)

    # 2. POIs in buffer
    q_poi = f"""
        SELECT 
            ST_X(ST_Centroid(geometry)) as x,
            ST_Y(ST_Centroid(geometry)) as y
        FROM read_parquet('{amenities_parquet}')
        WHERE ST_X(ST_Centroid(geometry)) >= {w_buf} AND ST_X(ST_Centroid(geometry)) <= {e_buf}
          AND ST_Y(ST_Centroid(geometry)) >= {s_buf} AND ST_Y(ST_Centroid(geometry)) <= {n_buf}
    """
    df_poi_sub = con.execute(q_poi).df()
    poi_coords = df_poi_sub[["x", "y"]].to_numpy()
    _, poi_node_idx = tree_nodes.query(poi_coords, k=1)

    # 3. Hex cells
    zone_hexes = df_raw[(df_raw["lon"] >= w) & (df_raw["lon"] <= e) & (df_raw["lat"] >= s) & (df_raw["lat"] <= n)].copy()
    hex_xy = np.column_stack([zone_hexes["lon"].to_numpy(), zone_hexes["lat"].to_numpy()])
    _, hex_node_idx = tree_nodes.query(hex_xy, k=1)

    # Dijkstra on Fixed Overture
    dist_mat = dijkstra(adj, directed=False, indices=hex_node_idx, limit=1000.0)
    poi_dists = dist_mat[:, poi_node_idx]
    fixed_seg_counts = np.sum(poi_dists <= 1000.0, axis=1)

    # Old stored Dijkstra
    old_counts = zone_hexes["cumulative_amenities_15m"].to_numpy()

    # Euclidean
    poi_tree = cKDTree(poi_coords)
    euc_750m = np.array(poi_tree.query_ball_point(hex_xy, r=750.0/111000.0, return_length=True))
    euc_1000m = np.array(poi_tree.query_ball_point(hex_xy, r=1000.0/111000.0, return_length=True))

    # OSMnx
    print(f"  Downloading OSMnx walk graph for {z_name}...", flush=True)
    G_walk = ox.graph_from_bbox(bbox=(w_buf, s_buf, e_buf, n_buf), network_type="walk")
    osm_poi_nodes = ox.nearest_nodes(G_walk, X=poi_coords[:, 0], Y=poi_coords[:, 1])
    node_cnts = {}
    for p in osm_poi_nodes:
        node_cnts[p] = node_cnts.get(p, 0) + 1
    osm_hex_nodes = ox.nearest_nodes(G_walk, X=hex_xy[:, 0], Y=hex_xy[:, 1])

    osmnx_counts = []
    for hn in osm_hex_nodes:
        reachable = nx.single_source_dijkstra_path_length(G_walk, hn, cutoff=1000.0, weight="length")
        osmnx_counts.append(sum(node_cnts.get(rn, 0) for rn in reachable))
    osmnx_counts = np.array(osmnx_counts)

    res_df = pd.DataFrame({
        "Zone": z_name,
        "Hex_ID": zone_hexes.index,
        "Old_Dijkstra": old_counts,
        "Fixed_Overture_Dijkstra": fixed_seg_counts,
        "OSMnx_Pedestrian": osmnx_counts,
        "Euclidean_750m": euc_750m,
        "Euclidean_1000m": euc_1000m,
    })
    all_zone_results.append(res_df)

final_df = pd.concat(all_zone_results, ignore_index=True)

print("\n" + "=" * 80, flush=True)
print("MULTI-ZONE BENCHMARK SUMMARY TABLE (MEAN VALUES ACROSS ALL 4 ZONES)", flush=True)
print("=" * 80, flush=True)
summary_table = final_df.groupby("Zone")[["Old_Dijkstra", "Fixed_Overture_Dijkstra", "OSMnx_Pedestrian", "Euclidean_750m", "Euclidean_1000m"]].mean().round(1)
print(summary_table.to_string(), flush=True)

print("\nMEDIAN VALUES ACROSS ALL 4 ZONES:", flush=True)
summary_median = final_df.groupby("Zone")[["Old_Dijkstra", "Fixed_Overture_Dijkstra", "OSMnx_Pedestrian", "Euclidean_750m", "Euclidean_1000m"]].median().round(1)
print(summary_median.to_string(), flush=True)
