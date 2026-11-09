import sys
sys.stdout.reconfigure(line_buffering=True)

import osmnx as ox
import networkx as nx
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import duckdb

print("=" * 70, flush=True)
print("MULTI-TOOL ISOCHRONE COMPARISON (OSMnx vs Overture Dijkstra vs Euclidean)", flush=True)
print("=" * 70, flush=True)

con = duckdb.connect()
con.install_extension("spatial")
con.load_extension("spatial")
con.execute("SET geometry_always_xy = true;")

# 1. Load POIs
amenities_parquet = "data/raw/overture_amenities.parquet"
df_poi = con.execute(f"SELECT ST_X(ST_Centroid(geometry)) as x, ST_Y(ST_Centroid(geometry)) as y FROM read_parquet('{amenities_parquet}')").df()
poi_coords = df_poi[["x", "y"]].to_numpy()
poi_tree = cKDTree(poi_coords)
print(f"Loaded {len(poi_coords):,} amenities.", flush=True)

# 2. Load H3 features
df_raw = pd.read_parquet("data/interim/h3_features_raw.parquet")

# Test Zone: BSD City / Kampung Sampora
# Bounding box: [106.63, -6.32, 106.67, -6.29]
w, s, e, n = 106.63, -6.32, 106.67, -6.29
zone_hexes = df_raw[(df_raw["lon"] >= w) & (df_raw["lon"] <= e) & (df_raw["lat"] >= s) & (df_raw["lat"] <= n)].copy()
print(f"Target Zone: BSD City / Kampung Sampora ({len(zone_hexes)} H3 Res-8 cells)", flush=True)

# Tool 1: Current Stored Overture Dijkstra
cur_dijkstra = zone_hexes["cumulative_amenities_15m"].to_numpy()

# Tool 4: Euclidean 1000m & 750m (Circuity-adjusted)
hex_xy = np.column_stack([zone_hexes["lon"].to_numpy(), zone_hexes["lat"].to_numpy()])
euc_1000m = np.array(poi_tree.query_ball_point(hex_xy, r=1000.0/111000.0, return_length=True))
euc_750m = np.array(poi_tree.query_ball_point(hex_xy, r=750.0/111000.0, return_length=True))

# Tool 2: OSMnx Walk Network
print("Downloading OpenStreetMap walking network via OSMnx...", flush=True)
buf_deg = 1200.0 / 111000.0
G_walk = ox.graph_from_bbox(bbox=(w - buf_deg, s - buf_deg, e + buf_deg, n + buf_deg), network_type="walk")
print(f"OSM Walk Graph: {len(G_walk.nodes):,} nodes, {len(G_walk.edges):,} edges.", flush=True)

# Check highway types in OSM
edges_gdf = ox.graph_to_gdfs(G_walk, nodes=False)
print("OSM Highway types in zone:\n", edges_gdf["highway"].value_counts().head(8).to_string(), flush=True)

# Snap POIs to OSM graph
poi_mask = (poi_coords[:, 0] >= w - buf_deg) & (poi_coords[:, 0] <= e + buf_deg) & (poi_coords[:, 1] >= s - buf_deg) & (poi_coords[:, 1] <= n + buf_deg)
sub_poi_coords = poi_coords[poi_mask]
print(f"Amenities in expanded zone: {len(sub_poi_coords):,}", flush=True)

poi_nodes = ox.nearest_nodes(G_walk, X=sub_poi_coords[:, 0], Y=sub_poi_coords[:, 1])
node_poi_counts = {}
for p in poi_nodes:
    node_poi_counts[p] = node_poi_counts.get(p, 0) + 1

hex_nodes = ox.nearest_nodes(G_walk, X=hex_xy[:, 0], Y=hex_xy[:, 1])
print("Routing 15-minute (1000m) pedestrian isochrones via OSMnx / NetworkX Dijkstra...", flush=True)
osmnx_counts = []
for hn in hex_nodes:
    reachable_nodes = nx.single_source_dijkstra_path_length(G_walk, hn, cutoff=1000.0, weight="length")
    cnt = sum(node_poi_counts.get(rn, 0) for rn in reachable_nodes)
    osmnx_counts.append(cnt)
osmnx_counts = np.array(osmnx_counts)

# Summary Comparison Table
comp_df = pd.DataFrame({
    "Current (Overture Dijkstra)": cur_dijkstra,
    "OSMnx (OSM Pedestrian Graph)": osmnx_counts,
    "Euclidean 750m (Circuity Adj)": euc_750m,
    "Euclidean 1000m (Geometric Upper)": euc_1000m,
}, index=zone_hexes.index)

print("\n" + "=" * 70, flush=True)
print("COMPARISON RESULTS: BSD CITY / KAMPUNG SAMPORA ENCLAVE (N = 18 cells)", flush=True)
print("=" * 70, flush=True)
print(comp_df.describe().round(1).to_string(), flush=True)

print("\nPer-Cell Breakdown (First 10 cells):", flush=True)
print(comp_df.head(10).to_string(), flush=True)
