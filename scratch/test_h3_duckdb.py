import duckdb
con = duckdb.connect()
con.load_extension("spatial")
con.load_extension("h3")
con.execute("SET geometry_always_xy = true;")

res = con.execute("""
    SELECT 
        h3_latlng_to_cell(-6.2, 106.8, 8) as h3_int,
        printf('%x', h3_latlng_to_cell(-6.2, 106.8, 8)) as h3_hex
""").df()
print(res)
