import rasterio
from pathlib import Path
import numpy as np

raw_dir = Path("data/raw")
rasters = [
    "worldpop.tif",
    "viirs_black_marble.tif",
    "sentinel2_ndvi.tif",
    "sentinel2_ndbi.tif",
    "sentinel2_mndwi.tif",
    "sentinel2_bsi.tif",
    "landsat_lst.tif"
]

for r in rasters:
    p = raw_dir / r
    with rasterio.open(p) as src:
        arr = src.read(1)
        valid = arr[arr != src.nodata] if src.nodata is not None else arr
        valid = valid[~np.isnan(valid)]
        print(f"{r}: shape={src.shape}, crs={src.crs}, res={src.res}, bounds={src.bounds}, min={valid.min():.2f}, mean={valid.mean():.2f}, max={valid.max():.2f}, total_sum={valid.sum():.2f}")
