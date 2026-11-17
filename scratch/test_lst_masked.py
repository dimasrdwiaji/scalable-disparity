import rasterio
import numpy as np

with rasterio.open("data/raw/landsat_lst.tif") as src:
    arr = src.read(1)
    valid = arr[arr > 273.15]
    print(f"Total pixels: {arr.size}, Valid land pixels (> 0 C): {len(valid)} ({len(valid)/arr.size*100:.1f}%)")
    print(f"Valid LST min: {valid.min():.2f} K ({valid.min()-273.15:.2f} C)")
    print(f"Valid LST mean: {valid.mean():.2f} K ({valid.mean()-273.15:.2f} C)")
    print(f"Valid LST median: {np.median(valid):.2f} K ({np.median(valid)-273.15:.2f} C)")
    print(f"Valid LST max: {valid.max():.2f} K ({valid.max()-273.15:.2f} C)")
