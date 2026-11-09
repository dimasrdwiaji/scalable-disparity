import pandas as pd
import numpy as np
import scipy.sparse as sp
from scipy.spatial import cKDTree
import duckdb

print("=" * 70)
print("DIAGNOSTIC 1: ROAD NETWORK GRAPH CONNECTED COMPONENTS")
print("=" * 70)

con = duckdb.connect()
con.install_extension("spatial")
con.load_extension("spatial")
con.execute("SET geometry_always_xy = true;")

transport_parquet = "data/raw/overture_transportation.parquet"
query_edges = f"""
    SELECT 
        ST_X(ST_PointN(geometry, 1)) as x1,
        ST_Y(ST_PointN(geometry, 1)) as y1,
        ST_X(ST_PointN(geometry, -1)) as x2,
        ST_Y(ST_PointN(geometry, -1)) as y2,
        ST_Length_Spheroid(geometry) as length_m
    FROM read_parquet('{transport_parquet}')
    WHERE ST_Length_Spheroid(geometry) > 0.0
"""
df_edges = con.execute(query_edges).df()
print(f"Extracted {len(df_edges):,} road edges.")

pts1 = np.round(df_edges[["x1", "y1"]].to_numpy(), 6)
pts2 = np.round(df_edges[["x2", "y2"]].to_numpy(), 6)
all_pts = np.vstack([pts1, pts2])
unique_pts, inverse = np.unique(all_pts, axis=0, return_inverse=True)
n_edges = len(df_edges)
u = inverse[:n_edges]
v = inverse[n_edges:]
weights = df_edges["length_m"].to_numpy(dtype=np.float64)

row_indices = np.concatenate([u, v])
col_indices = np.concatenate([v, u])
data = np.concatenate([weights, weights])
n_nodes = len(unique_pts)
adj = sp.csr_matrix((data, (row_indices, col_indices)), shape=(n_nodes, n_nodes))

n_comp, labels = sp.csgraph.connected_components(adj, directed=False)
unique_labels, comp_counts = np.unique(labels, return_counts=True)
sorted_comp = sorted(comp_counts, reverse=True)

print(f"Total graph nodes: {n_nodes:,}")
print(f"Connected components: {n_comp:,}")
print(f"Largest component size: {sorted_comp[0]:,} nodes ({sorted_comp[0]/n_nodes*100:.2f}%)")
print(f"Second largest component: {sorted_comp[1]:,} nodes")
print(f"Number of components with <= 10 nodes: {sum(1 for c in comp_counts if c <= 10):,}")

print("\n" + "=" * 70)
print("DIAGNOSTIC 2: CENTROID & POI SNAPPING TO LARGEST COMPONENT")
print("=" * 70)

# Check POIs
amenities_parquet = "data/raw/overture_amenities.parquet"
query_poi = f"""
    SELECT 
        ST_X(ST_Centroid(geometry)) as x,
        ST_Y(ST_Centroid(geometry)) as y
    FROM read_parquet('{amenities_parquet}')
"""
df_poi = con.execute(query_poi).df()
poi_coords = df_poi[["x", "y"]].to_numpy()
print(f"Total amenities loaded: {len(poi_coords):,}")

tree_all = cKDTree(unique_pts)
poi_dists_deg, poi_nodes = tree_all.query(poi_coords, k=1)
poi_comp = labels[poi_nodes]
in_largest_poi = (poi_comp == unique_labels[np.argmax(comp_counts)]).sum()
print(f"Amenities snapped to largest component: {in_largest_poi:,} ({in_largest_poi/len(poi_coords)*100:.2f}%)")
print(f"Amenities snapped to disconnected islands: {len(poi_coords) - in_largest_poi:,}")

# Check H3 hex cells
df_raw = pd.read_parquet("data/interim/h3_features_raw.parquet")
hex_coords = np.column_stack([df_raw["lon"].to_numpy(), df_raw["lat"].to_numpy()])
hex_dists_deg, hex_nodes = tree_all.query(hex_coords, k=1)
hex_comp = labels[hex_nodes]
in_largest_hex = (hex_comp == unique_labels[np.argmax(comp_counts)]).sum()
print(f"Hex cells snapped to largest component: {in_largest_hex:,} / {len(hex_coords):,} ({in_largest_hex/len(hex_coords)*100:.2f}%)")
print(f"Hex cells snapped to disconnected islands: {len(hex_coords) - in_largest_hex:,}")

# Check snapping distance in meters
hex_dists_m = hex_dists_deg * 111000.0
print(f"Centroid snapping distance (meters): Median={np.median(hex_dists_m):.1f}m, P75={np.percentile(hex_dists_m, 75):.1f}m, P90={np.percentile(hex_dists_m, 90):.1f}m, Max={np.max(hex_dists_m):.1f}m")
print(f"Hex cells with snap distance > 1000m: {(hex_dists_m > 1000.0).sum():,}")

print("\n" + "=" * 70)
print("DIAGNOSTIC 3: EUCLIDEAN 1000M BUFFER ACCESSIBILITY BENCHMARK")
print("=" * 70)

# Euclidean KDTree query: how many amenities are physically within 1,000m radius of each hex centroid?
# 1000m in degrees at lat -6.2 deg is ~ 1000 / 111,000 = 0.009009 deg
radius_deg = 1000.0 / 111000.0
poi_tree = cKDTree(poi_coords)
counts_euclidean = poi_tree.query_ball_point(hex_coords, r=radius_deg, return_length=True)

df_raw["amenities_euclidean_1000m"] = counts_euclidean
print("All 17,154 cells - Euclidean 1000m Amenities:")
print(pd.Series(counts_euclidean).describe())

pop_cells = df_raw[df_raw["is_populated"]]
print("\nPopulated 15,108 cells - Euclidean 1000m Amenities:")
print(pop_cells["amenities_euclidean_1000m"].describe())

print("\nNetwork Dijkstra vs Euclidean in Populated Cells:")
print(f"Network Dijkstra Mean: {pop_cells['cumulative_amenities_15m'].mean():.2f}, Median: {pop_cells['cumulative_amenities_15m'].median():.2f}, P75: {pop_cells['cumulative_amenities_15m'].quantile(0.75):.2f}, P90: {pop_cells['cumulative_amenities_15m'].quantile(0.90):.2f}, Max: {pop_cells['cumulative_amenities_15m'].max():.2f}")
print(f"Euclidean 1km Mean:    {pop_cells['amenities_euclidean_1000m'].mean():.2f}, Median: {pop_cells['amenities_euclidean_1000m'].median():.2f}, P75: {pop_cells['amenities_euclidean_1000m'].quantile(0.75):.2f}, P90: {pop_cells['amenities_euclidean_1000m'].quantile(0.90):.2f}, Max: {pop_cells['amenities_euclidean_1000m'].max():.2f}")
