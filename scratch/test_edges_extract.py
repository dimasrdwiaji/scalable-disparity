import duckdb
import time

con = duckdb.connect()
con.load_extension("spatial")
con.execute("SET geometry_always_xy = true;")

t0 = time.time()
# Query start and end coordinates with edge length in meters
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
print(f"Extracted {len(df_edges)} edges in {time.time()-t0:.2f} seconds!")
print(df_edges.head())
