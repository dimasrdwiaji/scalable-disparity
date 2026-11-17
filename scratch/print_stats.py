import pandas as pd
import numpy as np

df_raw = pd.read_parquet("data/interim/h3_features_raw.parquet")
df_proc = pd.read_parquet("data/processed/feature_matrix_10d.parquet")

print("=== RAW INTERIM FEATURES SUMMARY (N = 17,154) ===")
stats_raw = df_raw[[
    "space_sufficiency_ratio",
    "builtup_ndbi",
    "cumulative_amenities_15m",
    "bare_soil_bsi",
    "nighttime_energy_radiance",
    "vegetation_ndvi",
    "thermal_comfort_lst_inv",
    "water_mndwi",
    "air_purity_pm25_inv",
    "multi_pollutant_aqi_inv",
]].describe(percentiles=[0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]).T
print(stats_raw[["mean", "std", "min", "25%", "50%", "75%", "99%", "max"]].to_string())

print("\n=== STANDARDIZED 10D FEATURES SUMMARY (N = 17,154, Range [0.0, 1.0]) ===")
stats_proc = df_proc.describe(percentiles=[0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]).T
print(stats_proc[["mean", "std", "min", "25%", "50%", "75%", "99%", "max"]].to_string())

print("\n=== TOP PAIRWISE CORRELATIONS ===")
corr = df_proc.corr()
pairs = []
for i in range(len(corr.columns)):
    for j in range(i+1, len(corr.columns)):
        pairs.append((corr.columns[i], corr.columns[j], corr.iloc[i, j]))
pairs.sort(key=lambda x: abs(x[2]), reverse=True)
for c1, c2, r in pairs[:10]:
    print(f"{c1} vs {c2}: r = {r:+.3f}")
