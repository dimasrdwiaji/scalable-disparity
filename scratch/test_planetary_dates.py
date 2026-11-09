import requests
from phys_living_index.data.ingest_context import build_planetary_computer_stac_query

stac_endpoint = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
bbox = (106.35, -6.75, 107.65, -5.95)

# Sentinel-2
s2_payload = build_planetary_computer_stac_query("sentinel-2-l2a", bbox, max_cloud_cover=20.0)
s2_resp = requests.post(stac_endpoint, json=s2_payload, timeout=30).json()
s2_features = s2_resp.get("features", [])
print(f"Sentinel-2 items found: {len(s2_features)}")
for i, f in enumerate(s2_features[:3]):
    props = f.get("properties", {})
    print(f"S2 item {i}: id={f.get('id')}, datetime={props.get('datetime')}, cloud_cover={props.get('eo:cloud_cover')}")

# Landsat
ls_payload = build_planetary_computer_stac_query("landsat-c2-l2", bbox, max_cloud_cover=20.0)
ls_resp = requests.post(stac_endpoint, json=ls_payload, timeout=30).json()
ls_features = ls_resp.get("features", [])
print(f"\nLandsat items found: {len(ls_features)}")
for i, f in enumerate(ls_features[:3]):
    props = f.get("properties", {})
    print(f"Landsat item {i}: id={f.get('id')}, datetime={props.get('datetime')}, cloud_cover={props.get('eo:cloud_cover')}")
