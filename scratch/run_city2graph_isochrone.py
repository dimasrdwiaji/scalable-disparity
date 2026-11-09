import geopandas as gpd
import pandas as pd
import duckdb
from shapely.geometry import Point
import city2graph
from city2graph.utils.spatial import create_isochrone

# 1. Load POIs
con = duckdb.connect()
con.install_extension('spatial')
con.load_extension('spatial')
df_pois = con.execute("""
    SELECT category, ST_X(ST_Centroid(geometry)) as lon, ST_Y(ST_Centroid(geometry)) as lat
    FROM read_parquet('data/raw/overture_amenities.parquet')
""").df()
con.close()

pois_gdf = gpd.GeoDataFrame(
    df_pois,
    geometry=gpd.points_from_xy(df_pois['lon'], df_pois['lat']),
    crs="EPSG:4326"
).to_crs("EPSG:32748")

print(f"Loaded {len(pois_gdf)} POIs.")

# 2. Load OSM network nodes and edges
nodes_gdf = gpd.read_parquet("data/interim/osm_walk_nodes.parquet")
edges_gdf = gpd.read_parquet("data/interim/osm_walk_edges.parquet")

# Filter network to a bounding box around BSD and Monas to keep NetworkX graph fast
print("Filtering network around BSD City & Monas...")
# BSD BBox: [106.60, -6.35, 106.70, -6.25]
mask_bsd = (
    (nodes_gdf["lon"] >= 106.60) & (nodes_gdf["lon"] <= 106.70) &
    (nodes_gdf["lat"] >= -6.35) & (nodes_gdf["lat"] <= -6.25)
)
bsd_node_ids = set(nodes_gdf.loc[mask_bsd, "id"])

edges_bsd = edges_gdf[edges_gdf["u"].isin(bsd_node_ids) & edges_gdf["v"].isin(bsd_node_ids)].copy()
nodes_bsd = nodes_gdf[nodes_gdf["id"].isin(bsd_node_ids)].copy()

nodes_bsd_utm = nodes_bsd.to_crs("EPSG:32748")
edges_bsd_utm = edges_bsd.to_crs("EPSG:32748")
edges_bsd_utm["length_m"] = edges_bsd_utm["length"]

print(f"BSD network: {len(nodes_bsd_utm)} nodes, {len(edges_bsd_utm)} edges.")

# 3. BSD Center Point
# BSD Green Office Park / The Breeze: -6.302, 106.652
center_bsd = gpd.GeoSeries([Point(106.652, -6.302)], crs="EPSG:4326").to_crs("EPSG:32748").iloc[0]

# Generate 15-minute isochrone (1000 meters)
print("Generating 15-minute walking isochrone via city2graph (cutoff = 1000m)...")
isochrone_gdf = create_isochrone(
    nodes=nodes_bsd_utm,
    edges=edges_bsd_utm,
    center_point=center_bsd,
    threshold=1000.0,
    edge_attr="length_m",
    method="buffer",
    buffer_distance=50.0,
)

print("Isochrone generated!")
print("Isochrone CRS:", isochrone_gdf.crs)
print("Isochrone Area (km2):", isochrone_gdf.geometry.area.sum() / 1e6)

# 4. Count amenities in isochrone
amenities_in_iso = pois_gdf[pois_gdf.geometry.within(isochrone_gdf.geometry.iloc[0])]
print(f"\n>>> city2graph 15-minute walk isochrone amenity count: {len(amenities_in_iso)}")
print("Categories sample in isochrone:\n", amenities_in_iso["category"].value_counts().head(10))

# Euclidean 1000m buffer comparison
euclid_1000 = center_bsd.buffer(1000.0)
amenities_euclid = pois_gdf[pois_gdf.geometry.within(euclid_1000)]
print(f"\n>>> Euclidean 1,000m circle amenity count: {len(amenities_euclid)}")
