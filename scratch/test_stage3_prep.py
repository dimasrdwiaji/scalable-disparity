import duckdb
from pathlib import Path

raw_dir = Path("data/raw")
con = duckdb.connect()
con.load_extension("spatial")
try:
    con.load_extension("h3")
except Exception:
    con.execute("FORCE INSTALL h3 FROM community;")
    con.load_extension("h3")

p_buildings = (raw_dir / "buildings.parquet").as_posix()
print("Buildings schema:")
df_b = con.execute(f"DESCRIBE SELECT * FROM '{p_buildings}'").df()
print(df_b)

print("\nBuildings sample:")
df_sample = con.execute(f"SELECT * FROM '{p_buildings}' LIMIT 3").df()
print(df_sample)

p_amenities = (raw_dir / "overture_amenities.parquet").as_posix()
print("\nAmenities schema:")
print(con.execute(f"DESCRIBE SELECT * FROM '{p_amenities}'").df())

p_trans = (raw_dir / "overture_transportation.parquet").as_posix()
print("\nTransportation schema:")
print(con.execute(f"DESCRIBE SELECT * FROM '{p_trans}'").df())
print("\nTransportation sample:")
print(con.execute(f"SELECT * FROM '{p_trans}' LIMIT 3").df())
