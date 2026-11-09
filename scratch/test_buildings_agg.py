import duckdb, time

con = duckdb.connect()
con.load_extension("spatial")
con.load_extension("h3")
con.execute("SET geometry_always_xy = true;")

t0 = time.time()
query = """
    SELECT 
        printf('%x', h3_latlng_to_cell(ST_Y(ST_Centroid(geometry)), ST_X(ST_Centroid(geometry)), 8)) AS h3_index,
        COUNT(*) AS building_count,
        SUM(ST_Area_Spheroid(geometry) * floor_count) AS total_floor_area,
        SUM(ST_Area_Spheroid(geometry)) AS footprint_area
    FROM read_parquet('data/raw/buildings.parquet')
    GROUP BY 1
"""
df_buildings_h3 = con.execute(query).df()
t1 = time.time()
print(f"Aggregated {len(df_buildings_h3)} H3 cells with buildings in {t1 - t0:.2f} seconds!")
print(df_buildings_h3.head())
print(df_buildings_h3.describe())
