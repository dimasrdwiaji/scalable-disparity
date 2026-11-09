import duckdb

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("INSTALL spatial; LOAD spatial;")
con.execute("SET s3_region = 'us-west-2';")
con.execute("SET s3_url_style = 'path';")
con.execute("SET allow_asterisks_in_http_paths = true;")

print("--- Testing Open Buildings with allow_asterisks_in_http_paths ---")
url = "https://data.source.coop/vida/google-microsoft-open-buildings/geoparquet/by_country_s2/country_iso=IDN/*"
try:
    df_desc = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{url}') LIMIT 1;").df()
    print("Open Buildings columns:")
    print(df_desc[["column_name", "column_type"]])
    
    bbox = (106.82, -6.18, 106.825, -6.175)
    query = f"""
    SELECT id, height, confidence, ST_AsText(geometry) AS wkt_geom
    FROM read_parquet('{url}')
    WHERE bbox.xmin >= {bbox[0]} AND bbox.xmax <= {bbox[2]}
      AND bbox.ymin >= {bbox[1]} AND bbox.ymax <= {bbox[3]}
      AND confidence >= 0.65
    LIMIT 5;
    """
    df_q = con.execute(query).df()
    print("Sample query result (rows):", len(df_q))
    if len(df_q) > 0:
        print(df_q.head(2))
except Exception as e:
    print("Open Buildings Error:", type(e), e)

print("\n--- Inspecting Overture Places categories/taxonomy ---")
release = "2026-10-21.0"
ov_url = f"s3://overturemaps-us-west-2/release/{release}/theme=places/type=place/*"
try:
    sample_places = con.execute(f"""
        SELECT id, names.primary AS name, basic_category, taxonomy, ST_AsText(geometry) AS geom
        FROM read_parquet('{ov_url}', hive_partitioning=true)
        WHERE bbox.xmin >= 106.82 AND bbox.xmax <= 106.83
          AND bbox.ymin >= -6.18 AND bbox.ymax <= -6.17
        LIMIT 10;
    """).df()
    print(sample_places)
except Exception as e:
    print("Overture sample error:", type(e), e)

print("\n--- Inspecting Overture Base (land_use) ---")
base_url = f"s3://overturemaps-us-west-2/release/{release}/theme=base/type=land_use/*"
try:
    df_base = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{base_url}', hive_partitioning=true) LIMIT 1;").df()
    print(df_base[["column_name", "column_type"]])
except Exception as e:
    print("Overture Base error:", type(e), e)
