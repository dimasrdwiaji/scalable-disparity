import h3
import pandas as pd
import numpy as np
from shapely.geometry import box
from scipy.spatial.distance import cdist

b = box(106.35, -6.75, 107.65, -5.95)
hex_list = list(h3.geo_to_cells(b.__geo_interface__, res=8) if hasattr(h3, 'geo_to_cells') else h3.polygon_to_cells(h3.Polygon(b.exterior.coords), 8))
hex_list.sort()
coords = [h3.cell_to_latlng(h) if hasattr(h3, 'cell_to_latlng') else h3.h3_to_geo(h) for h in hex_list]
lats, lons = zip(*coords)
hex_coords = np.column_stack([lons, lats])

df_aq = pd.read_parquet("data/raw/openmeteo_air_quality.parquet")
anchor_coords = df_aq[["longitude", "latitude"]].to_numpy()

dists = cdist(hex_coords, anchor_coords)
weights = 1.0 / (dists**2 + 1e-6)
weights /= weights.sum(axis=1, keepdims=True)

pm25_interp = weights @ df_aq["pm2_5"].to_numpy()
aqi_interp = weights @ df_aq["european_aqi"].to_numpy()

print(f"PM2.5 interpolated: min={pm25_interp.min():.2f}, mean={pm25_interp.mean():.2f}, max={pm25_interp.max():.2f}")
print(f"European AQI interpolated: min={aqi_interp.min():.2f}, mean={aqi_interp.mean():.2f}, max={aqi_interp.max():.2f}")
