import duckdb
import numpy as np
import scipy.sparse as sp

con = duckdb.connect()
con.install_extension("spatial")
con.load_extension("spatial")
con.execute("SET geometry_always_xy = true;")

w, s, e, n = 106.63, -6.32, 106.67, -6.29
transport_parquet = "data/raw/overture_transportation.parquet"

# Query 1: What our old query did (only PointN 1 and PointN -1)
q_old = f"""
    SELECT 
        ST_X(ST_PointN(geometry, 1)) as x1,
        ST_Y(ST_PointN(geometry, 1)) as y1,
        ST_X(ST_PointN(geometry, -1)) as x2,
        ST_Y(ST_PointN(geometry, -1)) as y2,
        ST_Length_Spheroid(geometry) as length_m
    FROM read_parquet('{transport_parquet}')
    WHERE ST_X(ST_Centroid(geometry)) >= {w} AND ST_X(ST_Centroid(geometry)) <= {e}
      AND ST_Y(ST_Centroid(geometry)) >= {s} AND ST_Y(ST_Centroid(geometry)) <= {n}
"""
df_old = con.execute(q_old).df()

# Query 2: Segment-level extraction (all consecutive vertices along each linestring!)
q_segments = f"""
    WITH lines AS (
        SELECT id, geometry, ST_NPoints(geometry) as n_pts
        FROM read_parquet('{transport_parquet}')
        WHERE ST_X(ST_Centroid(geometry)) >= {w} AND ST_X(ST_Centroid(geometry)) <= {e}
          AND ST_Y(ST_Centroid(geometry)) >= {s} AND ST_Y(ST_Centroid(geometry)) <= {n}
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
"""
df_seg = con.execute(q_segments).df()

print(f"Old approach (endpoint only): {len(df_old):,} edges")
print(f"Segment approach (consecutive vertices): {len(df_seg):,} edges")

def count_components(df_e):
    p1 = np.round(df_e[["x1", "y1"]].to_numpy(), 6)
    p2 = np.round(df_e[["x2", "y2"]].to_numpy(), 6)
    pts = np.vstack([p1, p2])
    unique_pts, inv = np.unique(pts, axis=0, return_inverse=True)
    m = len(df_e)
    u = inv[:m]
    v = inv[m:]
    w_arr = df_e["length_m"].to_numpy(dtype=np.float64)
    adj = sp.csr_matrix((np.concatenate([w_arr, w_arr]), (np.concatenate([u, v]), np.concatenate([v, u]))), shape=(len(unique_pts), len(unique_pts)))
    n_c, l_c = sp.csgraph.connected_components(adj, directed=False)
    _, counts = np.unique(l_c, return_counts=True)
    return len(unique_pts), n_c, sorted(counts, reverse=True)[0]

nodes_old, comp_old, max_old = count_components(df_old)
nodes_seg, comp_seg, max_seg = count_components(df_seg)

print(f"\nOld (Endpoint only): {nodes_old:,} nodes, {comp_old:,} components. Largest component = {max_old:,} nodes ({max_old/nodes_old*100:.1f}%)")
print(f"Segment-level:       {nodes_seg:,} nodes, {comp_seg:,} components. Largest component = {max_seg:,} nodes ({max_seg/nodes_seg*100:.1f}%)")
