import pandas as pd
import numpy as np

df_raw = pd.read_parquet("data/interim/h3_features_raw.parquet")
df_proc = pd.read_parquet("data/processed/feature_matrix_10d.parquet")

total_n = len(df_raw)
pop_mask = df_raw["is_populated"]
n_pop = int(pop_mask.sum())
pct_pop = n_pop / total_n * 100

print(f"Total H3 Res-8 cells: {total_n:,}")
print(f"Populated cells (pop >= 10): {n_pop:,} ({pct_pop:.1f}%)")
print(f"Unpopulated cells (pop < 10): {total_n - n_pop:,} ({100 - pct_pop:.1f}%)")

pop_raw = df_raw[pop_mask]
pop_proc = df_proc[pop_mask]

print("\n" + "=" * 60)
print("1. AMENITY ACCESSIBILITY (15-min Walking Network)")
print("=" * 60)
amen = pop_raw["cumulative_amenities_15m"]
print(f"Raw Amenities Count: Mean={amen.mean():.1f}, Median={amen.median():.0f}")
print(f"Quantiles: Min={amen.min():.0f}, P10={amen.quantile(0.10):.0f}, P25={amen.quantile(0.25):.0f}, P50={amen.quantile(0.50):.0f}, P75={amen.quantile(0.75):.0f}, P90={amen.quantile(0.90):.0f}, P95={amen.quantile(0.95):.0f}, P99={amen.quantile(0.99):.0f}, Max={amen.max():.0f}")

amen_norm = pop_proc["cumulative_amenities_15m"]
print(f"Normalized A_amenity [0, 1]: Mean={amen_norm.mean():.4f}, Median={amen_norm.median():.4f}, P75={amen_norm.quantile(0.75):.4f}, P90={amen_norm.quantile(0.90):.4f}, P99={amen_norm.quantile(0.99):.4f}, Max={amen_norm.max():.4f}")

print("\n" + "=" * 60)
print("2. LIVING SPACE PER CAPITA & SPACE SUFFICIENCY (R_space)")
print("=" * 60)
sp = pop_raw["living_space_per_capita_m2"]
print(f"Living Space (m2/capita): Mean={sp.mean():.2f}, Median={sp.median():.2f}")
print(f"Quantiles (m2/capita): Min={sp.min():.2f}, P10={sp.quantile(0.10):.2f}, P25={sp.quantile(0.25):.2f}, P50={sp.quantile(0.50):.2f}, P75={sp.quantile(0.75):.2f}, P90={sp.quantile(0.90):.2f}, P95={sp.quantile(0.95):.2f}, P99={sp.quantile(0.99):.2f}, Max={sp.max():.2f}")

rsp = pop_raw["space_sufficiency_ratio"]
print(f"R_space (sp / 9.0m2): Mean={rsp.mean():.2f}, Median={rsp.median():.2f}, P25={rsp.quantile(0.25):.2f}, P75={rsp.quantile(0.75):.2f}, P90={rsp.quantile(0.90):.2f}, P99={rsp.quantile(0.99):.2f}, Max={rsp.max():.2f}")
rsp_norm = pop_proc["space_sufficiency_ratio"]
print(f"Normalized R_space [0, 1]: Mean={rsp_norm.mean():.4f}, Median={rsp_norm.median():.4f}, P25={rsp_norm.quantile(0.25):.4f}, P75={rsp_norm.quantile(0.75):.4f}, P90={rsp_norm.quantile(0.90):.4f}, Max={rsp_norm.max():.4f}")

at_cap = (sp >= 54.0).sum()
print(f"Cells at luxury cap (>= 54.0 m2): {at_cap} ({at_cap / n_pop * 100:.2f}%)")

print("\n" + "=" * 60)
print("3. NIGHTTIME ENERGY RADIANCE (VIIRS Luminosity)")
print("=" * 60)
viirs = pop_raw["nighttime_energy_radiance"]
print(f"Raw Radiance (nW/cm2/sr): Mean={viirs.mean():.2f}, Median={viirs.median():.2f}")
print(f"Quantiles: Min={viirs.min():.2f}, P10={viirs.quantile(0.10):.2f}, P25={viirs.quantile(0.25):.2f}, P50={viirs.quantile(0.50):.2f}, P75={viirs.quantile(0.75):.2f}, P90={viirs.quantile(0.90):.2f}, P99={viirs.quantile(0.99):.2f}, Max={viirs.max():.2f}")
viirs_norm = pop_proc["nighttime_energy_radiance"]
print(f"Normalized VIIRS [0, 1]: Mean={viirs_norm.mean():.4f}, Median={viirs_norm.median():.4f}, P90={viirs_norm.quantile(0.90):.4f}, P99={viirs_norm.quantile(0.99):.4f}")

FEATURE_COLS = [
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
]

print("\n" + "=" * 60)
print("4. ALL 10 DIMENSIONS SUMMARY (Populated Cells N=15,108)")
print("=" * 60)
summary_df = pd.DataFrame(index=FEATURE_COLS, columns=["Mean", "Std", "Min", "P25", "Median", "P75", "P90", "P99", "Max"])
for c in FEATURE_COLS:
    v = pop_proc[c].astype(float)
    summary_df.loc[c] = [
        f"{v.mean():.3f}",
        f"{v.std():.3f}",
        f"{v.min():.3f}",
        f"{v.quantile(0.25):.3f}",
        f"{v.median():.3f}",
        f"{v.quantile(0.75):.3f}",
        f"{v.quantile(0.90):.3f}",
        f"{v.quantile(0.99):.3f}",
        f"{v.max():.3f}",
    ]
print(summary_df.to_string())

print("\n" + "=" * 60)
print("5. KEY CORRELATIONS (Pearson r on Populated Cells)")
print("=" * 60)
corr = pop_proc[FEATURE_COLS].corr()
for pair in [
    ("cumulative_amenities_15m", "air_purity_pm25_inv"),
    ("cumulative_amenities_15m", "nighttime_energy_radiance"),
    ("cumulative_amenities_15m", "builtup_ndbi"),
    ("cumulative_amenities_15m", "space_sufficiency_ratio"),
    ("space_sufficiency_ratio", "builtup_ndbi"),
    ("space_sufficiency_ratio", "vegetation_ndvi"),
    ("nighttime_energy_radiance", "air_purity_pm25_inv"),
    ("vegetation_ndvi", "thermal_comfort_lst_inv"),
    ("vegetation_ndvi", "builtup_ndbi"),
]:
    r_val = corr.loc[pair[0], pair[1]]
    print(f"r({pair[0]}, {pair[1]}) = {r_val:.3f}")

