import duckdb

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("INSTALL spatial; LOAD spatial;")
con.execute("SET s3_region = 'us-west-2';")
con.execute("SET s3_url_style = 'path';")

release = "2026-10-21.0"
ov_url = f"s3://overturemaps-us-west-2/release/{release}/theme=places/type=place/*"

query = f"""
SELECT names.primary AS name, basic_category, taxonomy.primary AS tax_primary
FROM read_parquet('{ov_url}', hive_partitioning=true)
WHERE bbox.xmin >= 106.8 AND bbox.xmax <= 106.9
  AND bbox.ymin >= -6.3 AND bbox.ymax <= -6.1
  AND (
    basic_category IN ('school', 'hospital', 'clinic', 'supermarket', 'grocery_store')
    OR taxonomy.primary IN ('school', 'hospital', 'clinic', 'supermarket', 'grocery_store')
  )
LIMIT 15;
"""
df = con.execute(query).df()
print(df.to_string())
