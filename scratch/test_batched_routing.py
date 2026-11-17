import time
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree
import duckdb
import h3
from shapely.geometry import box

print("Setting up graph and POIs...")
con = duckdb.connect()
con.load_extension("spatial")
con.execute("SET geometry_always_xy = true;")

# 1. Road edges
query_edges = """
    SELECT 
        ST_X(ST_PointN(geometry, 1)) as x1,
        ST_Y(ST_PointN(geometry, 1)) as y1,
        ST_X(ST_PointN(geometry, -1)) as x2,
        ST_Y(ST_PointN(geometry, -1)) as y2,
        ST_Length_Spheroid(geometry) as length_m
    FROM read_parquet('data/raw/overture_transportation.parquet')
    WHERE ST_Length_Spheroid(geometry) > 0.0
"""
df_edges = con.execute(query_edges).df()
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
N_nodes = len(unique_pts)
adj = csr_matrix((data, (row_indices, col_indices)), shape=(N_nodes, N_nodes))

# 2. Amenities
query_poi = """
    SELECT 
        ST_X(ST_Centroid(geometry)) as x,
        ST_Y(ST_Centroid(geometry)) as y
    FROM read_parquet('data/raw/overture_amenities.parquet')
"""
df_poi = con.execute(query_poi).df()
poi_coords = df_poi[["x", "y"]].to_numpy()

# Snap POIs to nearest network nodes
tree = cKDTree(unique_pts)
_, poi_node_indices = tree.query(poi_coords, k=1)
print(f"POIs snapped: {len(poi_node_indices)} POIs to {len(np.unique(poi_node_indices))} distinct nodes")

# 3. Test on 1,000 sources
b = box(106.35, -6.75, 107.65, -5.95)
hex_list = list(h3.geo_to_cells(b.__geo_interface__, res=8) if hasattr(h3, 'geo_to_cells') else h3.polygon_to_cells(h3.Polygon(b.exterior.coords), 8))
hex_list.sort()
coords = [h3.cell_to_latlng(h) if hasattr(h3, 'cell_to_latlng') else h3.h3_to_geo(h) for h in hex_list]
lats, lons = zip(*coords)
hex_coords = np.column_stack([lons, lats])
_, hex_node_indices = tree.query(hex_coords, k=1)

print(f"Testing batched Dijkstra on 1,000 hex origins...")
t0 = time.time()
counts = []
batch_size = 250
for i in range(0, 1000, batch_size):
    batch = hex_node_indices[i:i+batch_size]
    # Dijkstra with limit=1000.0 meters
    dists = dijkstra(adj, directed=False, indices=batch, limit=1000.0)
    # Extract distances to POI nodes
    poi_dists = dists[:, poi_node_indices]
    reachable = (poi_dists <= 1000.0).sum(axis=1)
    counts.extend(reachable)

t1 = time.time()
print(f"1,000 hex origins processed in {t1-t0:.2f}s! ({ (t1-t0)/1000 * 1000:.2f} ms/hex)")
print(f"Reachable amenities min: {min(counts)}, mean: {np.mean(counts):.2f}, max: {max(counts)}")
