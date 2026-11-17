import h3
import rasterio
import numpy as np
from shapely.geometry import box
from scipy.interpolate import NearestNDInterpolator

b = box(106.35, -6.75, 107.65, -5.95)
hex_list = list(h3.geo_to_cells(b.__geo_interface__, res=8) if hasattr(h3, 'geo_to_cells') else h3.polygon_to_cells(h3.Polygon(b.exterior.coords), 8))
hex_list.sort()
coords = [h3.cell_to_latlng(h) if hasattr(h3, 'cell_to_latlng') else h3.h3_to_geo(h) for h in hex_list]
lats, lons = zip(*coords)
pts = list(zip(lons, lats))

with rasterio.open("data/raw/landsat_lst.tif") as src:
    lst_vals = np.array([v[0] for v in src.sample(pts)])

valid_mask = lst_vals >= 280.0
print(f"Total H3 cells: {len(lst_vals)}")
print(f"Cells with valid terrestrial LST (>= 280 K): {valid_mask.sum()} ({valid_mask.sum()/len(lst_vals)*100:.1f}%)")
print(f"Cells with ocean/fill nodata (< 280 K): {(~valid_mask).sum()}")

# Nearest-neighbor interpolation from valid cells
coords_xy = np.column_stack([lons, lats])
valid_coords = coords_xy[valid_mask]
valid_values = lst_vals[valid_mask]

interp = NearestNDInterpolator(valid_coords, valid_values)
lst_filled = lst_vals.copy()
lst_filled[~valid_mask] = interp(coords_xy[~valid_mask])

print(f"Filled LST min: {lst_filled.min():.2f} K ({lst_filled.min()-273.15:.2f} C)")
print(f"Filled LST mean: {lst_filled.mean():.2f} K ({lst_filled.mean()-273.15:.2f} C)")
print(f"Filled LST max: {lst_filled.max():.2f} K ({lst_filled.max()-273.15:.2f} C)")
