import pandas as pd

df_raw = pd.read_parquet("data/interim/h3_features_raw.parquet")
high_space = df_raw[df_raw["living_space_per_capita_m2"] > 100]

print(f"Number of cells with living space > 100 m2/capita: {len(high_space)}")
print("\nSample of cells with living space > 100 m2/capita:")
print(high_space[["lat", "lon", "population", "building_count", "residential_floor_area_m2", "living_space_per_capita_m2"]].head(15))

print("\nSummary of population in cells with living space > 100 m2/capita:")
print(high_space["population"].describe())
