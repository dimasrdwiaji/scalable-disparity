import duckdb

con = duckdb.connect()
con.install_extension("spatial")
con.load_extension("spatial")
con.install_extension("httpfs")
con.load_extension("httpfs")
con.execute("SET s3_region = 'us-west-2';")
con.execute("SET s3_url_style = 'path';")

bbox = (106.35, -6.75, 107.65, -5.95)
release = "2026-10-21.0"

query = f"""
    SELECT 
        coalesce(taxonomy.primary, basic_category) as cat,
        COUNT(*) as cnt
    FROM read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=places/type=place/*', hive_partitioning=true)
    WHERE bbox.xmin >= {bbox[0]} AND bbox.xmax <= {bbox[2]}
      AND bbox.ymin >= {bbox[1]} AND bbox.ymax <= {bbox[3]}
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 40
"""
df = con.execute(query).df()
print("Top 40 Place categories in Overture across Jabodetabek:")
print(df.to_string())
