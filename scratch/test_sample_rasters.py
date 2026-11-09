import h3
import rasterio
import numpy as np
import pandas as pd
from shapely.geometry import box

# Generate 17,154 H3 res-8 hexes
b = box(106.35, -6.75, 107.65, -5.95)
hex_list = list(h3.geo_to_cells(b.__geo_interface__, res=8) if hasattr(h3, 'geo_to_cells') else h3.polygon_to_cells(h3.Polygon(b.exterior.coords), 8))
hex_list.sort()

# Centroids
coords = [h3.cell_to_latlng(h) if hasattr(h3, 'cell_to_latlng') else h3.h3_to_geo(h) for h in hex_list]
lats, lons = zip(*coords)

pts = list(zip(lons, lats))

with rasterio.open("data/raw/worldpop.tif") as src:
    pop_samples = [val[0] for val in src.sample(pts)]
    pop_arr = np.array(pop_samples)
    pop_arr = np.where(pop_arr < 0, 0.0, pop_arr)
    print("WorldPop sample summary (masked nodata):")
    print(f"Total sampled: {pop_arr.sum():.2f}")
    print(f"Min: {pop_arr.min():.2f}, Median: {np.median(pop_arr):.2f}, Mean: {pop_arr.mean():.2f}, Max: {pop_arr.max():.2f}")
    print(f"Cells with > 0 pop: {(pop_arr > 0).sum()} / {len(pop_arr)}")
