import os
import pyproj

os.environ["PROJ_DATA"] = pyproj.datadir.get_data_dir()
os.environ["PROJ_LIB"] = pyproj.datadir.get_data_dir()

import contextily as ctx
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import box

fig, ax = plt.subplots(figsize=(6, 6))
gdf = gpd.GeoDataFrame(geometry=[box(106.8, -6.3, 106.9, -6.2)], crs="EPSG:4326")
gdf.plot(ax=ax, alpha=0.5, color="red")
ctx.add_basemap(ax, crs=gdf.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
plt.savefig("scratch/test_basemap.png")
print("Contextily basemap test successful!")
