import duckdb

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("INSTALL spatial; LOAD spatial;")
con.execute("SET s3_region = 'us-west-2';")
con.execute("SET s3_url_style = 'path';")

release = "2026-10-21.0"
bldg_url = f"s3://overturemaps-us-west-2/release/{release}/theme=buildings/type=building/*"

# Query a 0.05 x 0.05 deg area (~5.5km x 5.5km) in Central/South Jakarta
bbox = (106.80, -6.25, 106.85, -6.20)
query = f"""
SELECT 
    COUNT(*) AS total_buildings,
    COUNT(height) AS with_height,
    COUNT(num_floors) AS with_floors,
    AVG(height) AS avg_height,
    MAX(height) AS max_height
FROM read_parquet('{bldg_url}', hive_partitioning=true)
WHERE bbox.xmin >= {bbox[0]} AND bbox.xmax <= {bbox[2]}
  AND bbox.ymin >= {bbox[1]} AND bbox.ymax <= {bbox[3]};
"""
res = con.execute(query).df()
print("Overture Buildings coverage test in South Jakarta:")
print(res)
