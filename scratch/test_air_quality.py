import pandas as pd
import geopandas as gpd

df = pd.read_parquet("data/raw/openmeteo_air_quality.parquet")
print("Open-Meteo Air Quality columns:")
print(df.columns.tolist())
print("\nShape:", df.shape)
print("\nSample records:")
print(df[["latitude", "longitude", "pm2_5", "pm10", "european_aqi", "us_aqi"]].head(10))
print("\nSummary stats:")
print(df[["pm2_5", "pm10", "european_aqi", "us_aqi"]].describe())
