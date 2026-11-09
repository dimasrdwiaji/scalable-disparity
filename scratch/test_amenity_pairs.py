import duckdb, time

con = duckdb.connect()
con.load_extension("spatial")
con.load_extension("h3")
con.execute("SET geometry_always_xy = true;")

t0 = time.time()
# Let's see: for 17,154 H3 hexes and 21,460 amenities
# Generate H3 centroids
query = """
    WITH hexes AS (
        SELECT 
            h3_cell,
            printf('%x', h3_cell) as h3_index,
            ST_Point(h3_cell_to_latlng(h3_cell)[2], h3_cell_to_latlng(h3_cell)[1])::POINT_2D as pt
        FROM (
            SELECT unnest(h3_polygon_wkt_to_cells('POLYGON((106.35 -6.75, 107.65 -6.75, 107.65 -5.95, 106.35 -5.95, 106.35 -6.75))', 8)) as h3_cell
        )
    )
    SELECT 
        COUNT(*) as total_pairs,
        COUNT(DISTINCT h3_index) as hexes_with_amenity
    FROM hexes h
    JOIN read_parquet('data/raw/overture_amenities.parquet') a
      ON ST_DWithin_Spheroid(h.pt, ST_Point(ST_X(ST_Centroid(a.geometry)), ST_Y(ST_Centroid(a.geometry)))::POINT_2D, 1000.0)
"""
res = con.execute(query).df()
print("Candidate pairs within 1000m:", res, f"time: {time.time()-t0:.2f}s")
