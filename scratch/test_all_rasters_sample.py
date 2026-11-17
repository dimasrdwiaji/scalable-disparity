import h3
import rasterio
import numpy as np
import pandas as pd
from shapely.geometry import box

b = box(106.35, -6.75, 107.65, -5.95)
hex_list = list(h3.geo_to_cells(b.__geo_interface__, res=8) if hasattr(h3, 'geo_to_cells') else h3.polygon_to_cells(h3.Polygon(b.exterior.coords), 8))
hex_list.sort()
coords = [h3.cell_to_latlng(h) if hasattr(h3, 'cell_to_latlng') else h3.h3_to_geo(h) for h in hex_list]
lats, lons = zip(*coords)
pts = list(zip(lons, lats))

rasters = [
    ("worldpop", "data/raw/worldpop.tif"),
    ("viirs", "data/raw/viirs_black_marble.tif"),
    ("ndvi", "data/raw/sentinel2_ndvi.tif"),
    ("ndbi", "data/raw/sentinel2_ndbi.tif"),
    ("mndwi", "data/raw/sentinel2_mndwi.tif"),
    ("bsi", "data/raw/sentinel2_bsi.tif"),
    ("lst", "data/raw/landsat_lst.tif"),
]

data = {"h3_index": hex_list, "lat": lats, "lon": lons}
for name, path in rasters:
    with rasterio.open(path) as src:
        vals = np.array([v[0] for v in src.sample(pts)])
        print(f"Sampled {name}: min={vals.min():.2f}, mean={vals.mean():.2f}, max={vals.max():.2f}, nodata={src.nodata}")
        data[name] = vals

df = pd.DataFrame(data)
print("\nSample DataFrame:")
print(df.head())
print("\nMissing or NaN counts:")
print(df.isna().sum())
