import pandas as pd
import numpy as np

df = pd.read_parquet("data/interim/h3_features_raw.parquet")
pop = df["population"]
floor = df["residential_floor_area_m2"]

# For cells with pop >= 10
pop_mask = pop >= 10.0
space_pop = np.where(pop_mask, floor / pop, 0.0)

print(f"Populated cells (pop >= 10): {pop_mask.sum()}")
valid_space = space_pop[pop_mask]
print("Percentiles of living space (m2/capita) in populated cells:")
for p in [1, 5, 10, 25, 50, 75, 90, 95, 98, 99, 99.5, 100]:
    print(f"P{p}: {np.percentile(valid_space, p):.2f} m2/capita (R_space = {np.percentile(valid_space, p)/9.0:.2f})")
