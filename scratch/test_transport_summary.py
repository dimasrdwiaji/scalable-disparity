import duckdb

con = duckdb.connect()
con.load_extension("spatial")
df = con.execute("""
    SELECT 
        ST_GeometryType(geometry) as geom_type,
        class,
        subtype,
        COUNT(*) as cnt
    FROM read_parquet('data/raw/overture_transportation.parquet')
    GROUP BY 1, 2, 3
    ORDER BY 4 DESC
    LIMIT 10
""").df()
print(df)
