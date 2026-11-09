import time
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
import duckdb

con = duckdb.connect()
con.load_extension("spatial")
con.execute("SET geometry_always_xy = true;")

query = """
    SELECT 
        ST_X(ST_PointN(geometry, 1)) as x1,
        ST_Y(ST_PointN(geometry, 1)) as y1,
        ST_X(ST_PointN(geometry, -1)) as x2,
        ST_Y(ST_PointN(geometry, -1)) as y2,
        ST_Length_Spheroid(geometry) as length_m
    FROM read_parquet('data/raw/overture_transportation.parquet')
    WHERE ST_Length_Spheroid(geometry) > 0.0
"""
df_edges = con.execute(query).df()

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
N = len(unique_pts)
adj = csr_matrix((data, (row_indices, col_indices)), shape=(N, N))

print("Adjacency built. Shape:", adj.shape, "NNZ:", adj.nnz)

# Test running dijkstra for 10 sources with limit=1000.0
t0 = time.time()
sample_sources = np.random.choice(N, size=10, replace=False)
dist = dijkstra(adj, directed=False, indices=sample_sources, limit=1000.0)
t1 = time.time()
print(f"Dijkstra for 10 sources took {t1-t0:.4f}s ({ (t1-t0)/10 * 1000:.2f} ms/source)")
print(f"Memory of dist matrix: {dist.nbytes / 1024 / 1024:.2f} MB")
