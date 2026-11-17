import rasterio
from pathlib import Path
from phys_living_index.data.ingest_context import fetch_worldpop

bbox = (106.35, -6.75, 107.65, -5.95)
out_tif = Path("scratch/test_worldpop.tif")

print("Testing WorldPop full bbox download...")
fetch_worldpop(bbox, out_tif)

with rasterio.open(out_tif) as src:
    data = src.read(1)
    print("WorldPop shape:", data.shape)
    print("WorldPop min, max, sum:", data[data >= 0].min(), data[data >= 0].max(), data[data >= 0].sum())
