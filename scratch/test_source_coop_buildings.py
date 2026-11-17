import duckdb
import geopandas as gpd
from shapely import wkt
from phys_living_index.data.ingest_buildings import derive_floor_count, filter_by_confidence

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("INSTALL spatial; LOAD spatial;")
con.execute("SET s3_region = 'us-west-2';")
con.execute("SET s3_url_style = 'path';")

bbox = (106.82, -6.18, 106.825, -6.175)
source_url = "s3://us-west-2.opendata.source.coop/vida/google-microsoft-osm-open-buildings/geoparquet/by_country_s2/country_iso=IDN/*.parquet"

query = f"""
SELECT 
    CAST(boundary_id AS VARCHAR) AS id, 
    NULL::DOUBLE AS height, 
    confidence, 
    ST_AsText(geometry) AS wkt_geom
FROM read_parquet('{source_url}')
WHERE bbox.xmin >= {bbox[0]} AND bbox.xmax <= {bbox[2]}
  AND bbox.ymin >= {bbox[1]} AND bbox.ymax <= {bbox[3]}
  AND confidence >= 0.65;
"""
df = con.execute(query).df()
print("Extracted buildings from Source Cooperative:", len(df))
if not df.empty:
    df["geometry"] = df["wkt_geom"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df.drop(columns=["wkt_geom"]), geometry="geometry", crs="EPSG:4326")
    gdf["floor_count"] = derive_floor_count(gdf)
    cols = ["id", "geometry", "height", "confidence", "floor_count"]
    gdf = gdf[cols]
    print(gdf.head(3))
