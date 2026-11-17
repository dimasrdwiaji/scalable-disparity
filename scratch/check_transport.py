import duckdb

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("INSTALL spatial; LOAD spatial;")
con.execute("SET s3_region = 'us-west-2';")
con.execute("SET s3_url_style = 'path';")

release = "2026-10-21.0"
trans_url = f"s3://overturemaps-us-west-2/release/{release}/theme=transportation/type=segment/*"

try:
    df_desc = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{trans_url}', hive_partitioning=true) LIMIT 1;").df()
    print("Overture Transportation columns:")
    print(df_desc[["column_name", "column_type"]])
    
    bbox = (106.82, -6.18, 106.825, -6.175)
    sample_trans = con.execute(f"""
        SELECT id, class, subtype, ST_AsText(geometry) AS geom
        FROM read_parquet('{trans_url}', hive_partitioning=true)
        WHERE bbox.xmin >= {bbox[0]} AND bbox.xmax <= {bbox[2]}
          AND bbox.ymin >= {bbox[1]} AND bbox.ymax <= {bbox[3]}
          AND (subtype IS NULL OR subtype != 'rail')
        LIMIT 5;
    """).df()
    print("\nSample Transportation segments:")
    print(sample_trans)
except Exception as e:
    print("Overture Transportation Error:", type(e), e)
