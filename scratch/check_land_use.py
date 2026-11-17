import duckdb

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("INSTALL spatial; LOAD spatial;")
con.execute("SET s3_region = 'us-west-2';")
con.execute("SET s3_url_style = 'path';")

release = "2026-10-21.0"
base_url = f"s3://overturemaps-us-west-2/release/{release}/theme=base/type=land_use/*"

query = f"""
SELECT id, names.primary AS name, subtype, class, ST_AsText(geometry) AS geom
FROM read_parquet('{base_url}', hive_partitioning=true)
WHERE bbox.xmin >= 106.8 AND bbox.xmax <= 106.9
  AND bbox.ymin >= -6.3 AND bbox.ymax <= -6.1
  AND subtype IN ('park', 'sports_pitch', 'recreation_ground')
LIMIT 5;
"""
df = con.execute(query).df()
print(df)
