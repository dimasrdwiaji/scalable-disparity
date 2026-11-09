import rasterio
import numpy as np

with rasterio.open("data/raw/landsat_lst.tif") as src:
    arr = src.read(1)
    print("Percentiles of landsat_lst:")
    for p in [0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100]:
        print(f"P{p}: {np.percentile(arr, p):.2f} K ({np.percentile(arr, p) - 273.15:.2f} C)")
