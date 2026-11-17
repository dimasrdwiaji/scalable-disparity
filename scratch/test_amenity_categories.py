import duckdb

con = duckdb.connect()
con.load_extension("spatial")
df = con.execute("""
    SELECT category, COUNT(*) as cnt 
    FROM read_parquet('data/raw/overture_amenities.parquet') 
    GROUP BY 1 
    ORDER BY 2 DESC
""").df()
print(df)
