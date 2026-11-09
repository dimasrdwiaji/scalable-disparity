import tempfile
import numpy as np
import rasterio
import requests
from pathlib import Path
from phys_living_index.data.credentials import load_earthdata_token

token = load_earthdata_token()
bbox = (106.35, -6.75, 107.65, -5.95)
url = "https://data.laadsdaac.earthdatacloud.nasa.gov/prod-lads/VNP46A2/VNP46A2.A2023365.h28v09.002.2025143180512.h5"
output_tif = Path("data/raw/viirs_black_marble.tif")

print("Downloading VIIRS H5 file (19.2 MB)...")
headers = {"Authorization": f"Bearer {token}"}
r = requests.get(url, headers=headers, stream=True)
r.raise_for_status()

with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as tmp:
    tmp_path = Path(tmp.name)
    for chunk in r.iter_content(chunk_size=65536):
        tmp.write(chunk)

print(f"Downloaded to {tmp_path}. Opening with rasterio...")
try:
    with rasterio.open(tmp_path) as src:
        print("Subdatasets available:")
        for s in src.subdatasets:
            print(" ", s)
        target = next((s for s in src.subdatasets if "Gap_Filled_DNB_BRDF-Corrected_NTL" in s), src.subdatasets[0])
        print("Reading target:", target)
        with rasterio.open(target) as sub_src:
            arr = sub_src.read(1).astype(np.float32)
            # VIIRS VNP46A2 scale factor is 0.1, fill value is 65535
            arr[arr > 65500] = 0.0
            arr[arr < 0] = 0.0
            arr = arr * 0.1  # Convert to nW/cm2/sr
            print(f"Array shape: {arr.shape}, min: {arr.min()}, max: {arr.max()}, mean: {arr.mean():.2f}")
            
            # Tile h28v09 covers lon 100 to 110, lat -10 to 0 (approx 2400x2400 pixels at 500m)
            # Save raster
            h, w = arr.shape
            # Nominal Sinusoidal/Geographic bounds for tile h28v09
            # In VNP46A2, each tile is 10 deg x 10 deg: h28 is 100 to 110 deg E, v09 is 0 to 10 deg S (-10 to 0)
            tile_min_lon, tile_max_lon = 100.0, 110.0
            tile_min_lat, tile_max_lat = -10.0, 0.0
            
            # Calculate pixel indices for our bbox [106.35, -6.75, 107.65, -5.95]
            px_start = int((bbox[0] - tile_min_lon) / (tile_max_lon - tile_min_lon) * w)
            px_end = int((bbox[2] - tile_min_lon) / (tile_max_lon - tile_min_lon) * w)
            py_start = int((tile_max_lat - bbox[3]) / (tile_max_lat - tile_min_lat) * h)
            py_end = int((tile_max_lat - bbox[1]) / (tile_max_lat - tile_min_lat) * h)
            
            clipped = arr[py_start:py_end, px_start:px_end]
            print(f"Clipped Jabodetabek shape: {clipped.shape}, min: {clipped.min()}, max: {clipped.max()}, mean: {clipped.mean():.2f}")
            
            ch, cw = clipped.shape
            transform = rasterio.transform.from_bounds(bbox[0], bbox[1], bbox[2], bbox[3], cw, ch)
            with rasterio.open(
                output_tif,
                "w",
                driver="GTiff",
                height=ch,
                width=cw,
                count=1,
                dtype="float32",
                crs="EPSG:4326",
                transform=transform,
            ) as dst:
                dst.write(clipped, 1)
            print("Successfully written", output_tif, "Size:", output_tif.stat().st_size)
finally:
    if tmp_path.exists():
        tmp_path.unlink()
