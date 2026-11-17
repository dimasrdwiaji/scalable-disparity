import geopandas as gpd
import duckdb
from shapely.geometry import Point
from city2graph.utils.spatial import create_isochrone

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

nodes_gdf = gpd.read_parquet("data/interim/osm_walk_nodes.parquet")
edges_gdf = gpd.read_parquet("data/interim/osm_walk_edges.parquet")

# Test on the zero-cell in Cisarua: lat=-6.6358, lon=106.8822
lat_zero, lon_zero = -6.6358, 106.8822
center_zero = gpd.GeoSeries([Point(lon_zero, lat_zero)], crs="EPSG:4326").to_crs("EPSG:32748").iloc[0]

# Filter network around Cisarua
mask_cis = (
    (nodes_gdf["lon"] >= lon_zero - 0.05) & (nodes_gdf["lon"] <= lon_zero + 0.05) &
    (nodes_gdf["lat"] >= lat_zero - 0.05) & (nodes_gdf["lat"] <= lat_zero + 0.05)
)
cis_node_ids = set(nodes_gdf.loc[mask_cis, "id"])
edges_cis = edges_gdf[edges_gdf["u"].isin(cis_node_ids) & edges_gdf["v"].isin(cis_node_ids)].copy()
nodes_cis = nodes_gdf[nodes_gdf["id"].isin(cis_node_ids)].copy()

nodes_cis_utm = nodes_cis.to_crs("EPSG:32748")
edges_cis_utm = edges_cis.to_crs("EPSG:32748")
edges_cis_utm["length_m"] = edges_cis_utm["length"]

print(f"Cisarua local network: {len(nodes_cis_utm)} nodes, {len(edges_cis_utm)} edges.")

# Euclidean check first
euclid_1000 = center_zero.buffer(1000.0)
amenities_euclid = pois_gdf[pois_gdf.geometry.within(euclid_1000)]
print(f"Euclidean 1,000m circle amenity count around Cisarua cell: {len(amenities_euclid)}")
if len(amenities_euclid) > 0:
    print(amenities_euclid["category"].value_counts())

# Isochrone check
iso_cis = create_isochrone(
    nodes=nodes_cis_utm,
    edges=edges_cis_utm,
    center_point=center_zero,
    threshold=1000.0,
    edge_attr="length_m",
    method="buffer",
    buffer_distance=50.0,
)

amenities_iso = pois_gdf[pois_gdf.geometry.within(iso_cis.geometry.iloc[0])]
print(f"city2graph 15-minute isochrone amenity count: {len(amenities_iso)}")
