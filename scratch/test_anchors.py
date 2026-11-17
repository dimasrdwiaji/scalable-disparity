import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path
from phys_living_index.data.ingest_context import OPENMETEO_AIR_QUALITY_VARIABLES

anchors = [
    (-6.175, 106.828, "Jakarta Pusat"),
    (-6.121, 106.774, "Jakarta Utara"),
    (-6.167, 106.763, "Jakarta Barat"),
    (-6.261, 106.810, "Jakarta Selatan"),
    (-6.225, 106.900, "Jakarta Timur"),
    (-6.178, 106.631, "Kota Tangerang"),
    (-6.288, 106.717, "Tangerang Selatan"),
    (-6.326, 106.450, "Tigaraksa / Kab Tangerang"),
    (-6.402, 106.794, "Kota Depok"),
    (-6.597, 106.799, "Kota Bogor"),
    (-6.480, 106.850, "Cibinong / Kab Bogor"),
    (-6.238, 106.975, "Kota Bekasi"),
    (-6.268, 107.150, "Cikarang / Kab Bekasi Industrial"),
    (-6.150, 107.050, "Babelan / Kab Bekasi North"),
    (-6.305, 107.300, "Karawang Kota"),
    (-6.365, 107.280, "Telukjambe / KIIC Karawang"),
    (-6.200, 107.450, "Rengasdengklok / Karawang Agrarian"),
    (-6.450, 107.400, "Cikampek / Karawang Hub"),
    (-6.650, 107.050, "Puncak / Bogor Highland"),
    (-6.000, 106.700, "Teluk Jakarta / Coastal"),
]

var_str = ",".join(OPENMETEO_AIR_QUALITY_VARIABLES)
lats = ",".join(f"{a[0]}" for a in anchors)
lons = ",".join(f"{a[1]}" for a in anchors)
url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lats}&longitude={lons}&current={var_str}"

r = requests.get(url, timeout=30)
print("Status:", r.status_code)
if r.status_code == 200:
    data = r.json()
    records = []
    for a, d in zip(anchors, data):
        c = d.get("current", {})
        rec = {"region": a[2], "latitude": a[0], "longitude": a[1]}
        for v in OPENMETEO_AIR_QUALITY_VARIABLES:
            rec[v] = c.get(v)
        records.append(rec)
    df = pd.DataFrame(records)
    print(df[["region", "latitude", "longitude", "pm2_5", "us_aqi", "european_aqi"]].to_string())
    
    out_p = Path("data/raw/openmeteo_air_quality.parquet")
    gdf = gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in zip(df["longitude"], df["latitude"])], crs="EPSG:4326")
    gdf.to_parquet(out_p)
    print(f"Successfully saved {len(gdf)} anchor points to {out_p} ({out_p.stat().st_size} bytes)")
