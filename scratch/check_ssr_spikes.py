import pandas as pd
import numpy as np

df_raw = pd.read_parquet("data/interim/h3_features_raw.parquet")
ssr = df_raw["space_sufficiency_ratio"]

print("Total cells:", len(ssr))
print("Cells with ssr == 0:", (ssr == 0).sum(), f"({(ssr == 0).sum()/len(ssr)*100:.1f}%)")
print("Cells with ssr < 1.0 (crowded / substandard):", ((ssr > 0) & (ssr < 1.0)).sum(), f"({((ssr > 0) & (ssr < 1.0)).sum()/len(ssr)*100:.1f}%)")
print("Cells with 1.0 <= ssr < 5.0 (adequate to affluent):", ((ssr >= 1.0) & (ssr < 5.0)).sum(), f"({((ssr >= 1.0) & (ssr < 5.0)).sum()/len(ssr)*100:.1f}%)")
print("Cells with ssr >= 5.0 (clipped to 1.0):", (ssr >= 5.0).sum(), f"({(ssr >= 5.0).sum()/len(ssr)*100:.1f}%)")
