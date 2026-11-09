import osmnx as ox
import networkx as nx
import geopandas as gpd
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import duckdb

print("Testing OSMnx walking network download on BSD City / Sampora case study area...")
# Bounding box for BSD / Sampora: [106.60, -6.34, 106.68, -6.27]
north, south, east, west = -6.27, -6.34, 106.68, 106.60

# Download OSM walking network
G_walk = ox.graph_from_bbox(bbox=(north, south, east, west), network_type="walk")
print(f"OSM Walking Graph downloaded: {len(G_walk.nodes):,} nodes, {len(G_walk.edges):,} edges.")

# Inspect edge types
edge_data = ox.graph_to_gdfs(G_walk, nodes=False)
print("Top highway types in OSM walk graph:")
print(edge_data["highway"].value_counts().head(10))

# Load our amenities in this bbox
con = duckdb.connect()
con.install_extension("spatial")
con.load_extension("spatial")
con.execute("SET geometry_always_xy = true;")

query_poi = f"""
    SELECT 
        ST_X(ST_Centroid(geometry)) as x,
        ST_Y(ST_Centroid(geometry)) as y
    FROM read_parquet('data/raw/overture_amenities.parquet')
    WHERE ST_X(geometry) >= {west} AND ST_X(geometry) <= {east}
      AND ST_Y(geometry) >= {south} AND ST_Y(geometry) <= {north}
"""
df_poi_sub = con.execute(query_poi).df()
print(f"Amenities in BSD/Sampora bbox: {len(df_poi_sub):,}")
