import duckdb, time

con = duckdb.connect()
con.load_extension("spatial")
con.load_extension("h3")
con.execute("SET geometry_always_xy = true;")

t0 = time.time()
# Let's count how many start/end points there are
query = """
    SELECT 
        COUNT(DISTINCT ST_PointN(geometry, 1)) as start_nodes,
        COUNT(DISTINCT ST_PointN(geometry, -1)) as end_nodes
    FROM read_parquet('data/raw/overture_transportation.parquet')
"""
res = con.execute(query).df()
print("Node counts in transportation:", res, f"time: {time.time()-t0:.2f}s")
