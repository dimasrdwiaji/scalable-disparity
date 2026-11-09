import duckdb
con = duckdb.connect()
con.load_extension("spatial")
con.load_extension("h3")
res = con.execute("""
    SELECT 
        h3_cell_to_latlng(614953583411986431)[1] as lat,
        h3_cell_to_latlng(614953583411986431)[2] as lng
""").fetchall()
print(res)

