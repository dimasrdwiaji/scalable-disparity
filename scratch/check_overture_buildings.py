import duckdb

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("INSTALL spatial; LOAD spatial;")
con.execute("SET s3_region = 'us-west-2';")
con.execute("SET s3_url_style = 'path';")

release = "2026-10-21.0"
bldg_url = f"s3://overturemaps-us-west-2/release/{release}/theme=buildings/type=building/*"

try:
    df_desc = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{bldg_url}', hive_partitioning=true) LIMIT 1;").df()
    print("Overture Buildings columns:")
    print(df_desc[["column_name", "column_type"]])
    
    # Query a small bbox in Jakarta
    bbox = (106.82, -6.18, 106.825, -6.175)
    sample_bldgs = con.execute(f"""
        SELECT id, height, num_floors, subtype, class, ST_AsText(geometry) AS geom
        FROM read_parquet('{bldg_url}', hive_partitioning=true)
        WHERE bbox.xmin >= {bbox[0]} AND bbox.xmax <= {bbox[2]}
          AND bbox.ymin >= {bbox[1]} AND bbox.ymax <= {bbox[3]}
        LIMIT 5;
    """).df()
    print("\nSample Overture Buildings:")
    print(sample_bldgs)
except Exception as e:
    print("Overture Buildings Error:", type(e), e)
