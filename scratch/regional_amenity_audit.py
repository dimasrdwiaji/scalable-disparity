import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import duckdb

print("=" * 75)
print("REGIONAL AMENITY ACCESSIBILITY AUDIT ACROSS ALL 17,154 CELLS")
print("=" * 75)

# Load POIs
con = duckdb.connect()
con.install_extension("spatial")
con.load_extension("spatial")
con.execute("SET geometry_always_xy = true;")

amenities_parquet = "data/raw/overture_amenities.parquet"
df_poi = con.execute(f"SELECT ST_X(ST_Centroid(geometry)) as x, ST_Y(ST_Centroid(geometry)) as y FROM read_parquet('{amenities_parquet}')").df()
poi_coords = df_poi[["x", "y"]].to_numpy()
poi_tree = cKDTree(poi_coords)
print(f"Loaded {len(poi_coords):,} total Overture amenities.")

# Load H3 features
df_raw = pd.read_parquet("data/interim/h3_features_raw.parquet")
hex_xy = np.column_stack([df_raw["lon"].to_numpy(), df_raw["lat"].to_numpy()])

# Compute Euclidean 1000m and 750m counts for ALL 17,154 cells
print("Computing 1,000m and 750m radial KDTree query across all 17,154 cells...")
deg_1000m = 1000.0 / 111000.0
deg_750m = 750.0 / 111000.0

counts_1000m = np.array(poi_tree.query_ball_point(hex_xy, r=deg_1000m, return_length=True))
counts_750m = np.array(poi_tree.query_ball_point(hex_xy, r=deg_750m, return_length=True))

df_raw["amenities_euc_1000m"] = counts_1000m
df_raw["amenities_euc_750m"] = counts_750m

# Regional comparison on ALL 17,154 cells
print("\n" + "-" * 75)
print("ALL 17,154 CELLS (Including unpopulated sea/wetland/forest):")
print("-" * 75)
comp_all = pd.DataFrame({
    "Old Dijkstra (Current)": df_raw["cumulative_amenities_15m"],
    "Circuity-Adj 750m Buffer": df_raw["amenities_euc_750m"],
    "Euclidean 1000m Buffer": df_raw["amenities_euc_1000m"],
})
print(comp_all.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]).round(1).to_string())

# Regional comparison on POPULATED 15,108 residential cells
print("\n" + "-" * 75)
print("POPULATED 15,108 CELLS (pop >= 10.0 residents):")
print("-" * 75)
pop_df = df_raw[df_raw["is_populated"]]
comp_pop = pd.DataFrame({
    "Old Dijkstra (Current)": pop_df["cumulative_amenities_15m"],
    "Circuity-Adj 750m Buffer": pop_df["amenities_euc_750m"],
    "Euclidean 1000m Buffer": pop_df["amenities_euc_1000m"],
})
print(comp_pop.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]).round(1).to_string())

# Comparison in Core Urban Jabodetabek (DKI Jakarta + Bodetabek Urban Core)
# DKI Jakarta approximate bbox: [106.68, -6.37, 106.98, -6.08]
dki_mask = (df_raw["lon"] >= 106.68) & (df_raw["lon"] <= 106.98) & (df_raw["lat"] >= -6.37) & (df_raw["lat"] <= -6.08) & df_raw["is_populated"]
dki_df = df_raw[dki_mask]
print("\n" + "-" * 75)
print(f"DKI JAKARTA URBAN CORE (N = {len(dki_df):,} populated cells):")
print("-" * 75)
comp_dki = pd.DataFrame({
    "Old Dijkstra (Current)": dki_df["cumulative_amenities_15m"],
    "Circuity-Adj 750m Buffer": dki_df["amenities_euc_750m"],
    "Euclidean 1000m Buffer": dki_df["amenities_euc_1000m"],
})
print(comp_dki.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]).round(1).to_string())
