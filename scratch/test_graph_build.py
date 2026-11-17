import time
import numpy as np
import pandas as pd
import duckdb

t0 = time.time()
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
print(f"Edges read: {len(df_edges)} in {time.time()-t0:.2f}s")

# Let's map unique (x, y) coordinates
t1 = time.time()
pts1 = np.round(df_edges[["x1", "y1"]].to_numpy(), 6)
pts2 = np.round(df_edges[["x2", "y2"]].to_numpy(), 6)
all_pts = np.vstack([pts1, pts2])
unique_pts, inverse = np.unique(all_pts, axis=0, return_inverse=True)
n_edges = len(df_edges)
u = inverse[:n_edges]
v = inverse[n_edges:]
print(f"Unique nodes: {len(unique_pts)}, edges: {n_edges} in {time.time()-t1:.2f}s")
