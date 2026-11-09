import time
import pandas as pd
import geopandas as gpd
import requests
from pathlib import Path
from shapely.geometry import Point

from phys_living_index.data.ingest_context import (
    OPENMETEO_AIR_QUALITY_VARIABLES,
    batch_locations,
    generate_sampling_grid,
)

bbox = (106.35, -6.75, 107.65, -5.95)
output_parquet = Path("data/raw/openmeteo_air_quality.parquet")

# 0.05 deg grid (~5.5km) captures full atmospheric variance without bursting Open-Meteo's rate limiter
points = generate_sampling_grid(bbox, step_deg=0.05)
batches = batch_locations(points, variables=OPENMETEO_AIR_QUALITY_VARIABLES, max_batch_size=50)
print(f"Generated {len(points)} grid points across {len(batches)} batches.")

session = requests.Session()
records = []
obs_time = None

for idx, b in enumerate(batches):
    print(f"Fetching batch {idx+1}/{len(batches)}...")
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    resp = session.get(url, params=b, timeout=20)
    if resp.status_code == 429:
        print("Hit 429, sleeping 5s...")
        time.sleep(5.0)
        resp = session.get(url, params=b, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    items = data if isinstance(data, list) else [data]
    for item in items:
        lat = item.get("latitude")
        lon = item.get("longitude")
        curr = item.get("current", {})
        if obs_time is None and curr.get("time"):
            obs_time = curr.get("time")
        rec = {"latitude": lat, "longitude": lon}
        for v in OPENMETEO_AIR_QUALITY_VARIABLES:
            rec[v] = curr.get(v)
        records.append(rec)
    time.sleep(0.5)

df = pd.DataFrame(records)
gdf = gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in zip(df["longitude"], df["latitude"])], crs="EPSG:4326")
gdf.to_parquet(output_parquet)
print(f"Successfully written {output_parquet}: {len(gdf)} points. Obs time: {obs_time}")
print("PM2.5 mean:", df["pm2_5"].mean(), "US AQI mean:", df["us_aqi"].mean())
