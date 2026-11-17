import rasterio
import traceback

url = "https://data.worldpop.org/GIS/Population/Individual_countries/IDN/idn_ppp_2020_UNadj.tif"
print(f"Testing direct rasterio open on {url}...")
try:
    with rasterio.open(url) as src:
        print("Rasterio opened successfully!")
        print("CRS:", src.crs)
        print("Bounds:", src.bounds)
        print("Shape:", src.shape)
        window = rasterio.windows.from_bounds(106.35, -6.75, 107.65, -5.95, transform=src.transform)
        print("Window:", window)
        window = window.round_offsets().round_lengths()
        data = src.read(1, window=window)
        print("Read window shape:", data.shape)
        print("Data min, max, sum:", data[data >= 0].min(), data[data >= 0].max(), data[data >= 0].sum())
except Exception as e:
    print("Error opening worldpop:", type(e), e)
    traceback.print_exc()
