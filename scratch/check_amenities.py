import duckdb
import yaml

con = duckdb.connect()
df_raw_cat = con.execute("SELECT category, count(1) as cnt FROM read_parquet('data/raw/overture_amenities.parquet') GROUP BY 1 ORDER BY 2 DESC").df()
print("Total POIs in overture_amenities.parquet:", df_raw_cat["cnt"].sum())
print(df_raw_cat.head(25))

with open("configs/default.yaml") as f:
    cfg = yaml.safe_load(f)
allowed = set(cfg["accessibility"]["amenity_categories"])
print(f"\nAllowed categories count: {len(allowed)}")
matched = df_raw_cat[df_raw_cat["category"].isin(allowed)]
print("Matched POIs count:", matched["cnt"].sum())
unmatched = df_raw_cat[~df_raw_cat["category"].isin(allowed)]
print("Unmatched POIs count:", unmatched["cnt"].sum())
print("\nTop unmatched categories:")
print(unmatched.head(25))
