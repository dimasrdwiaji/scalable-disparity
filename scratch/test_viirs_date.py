import requests
from phys_living_index.data.credentials import load_earthdata_token
from phys_living_index.data.ingest_context import build_viirs_request_params

token = load_earthdata_token()
bbox = (106.35, -6.75, 107.65, -5.95)
cmr_url = "https://cmr.earthdata.nasa.gov/search/granules.json"
params = build_viirs_request_params(bbox)
headers = {"Authorization": f"Bearer {token}"}

resp = requests.get(cmr_url, params=params, headers=headers, timeout=30)
data = resp.json()
entries = data.get("feed", {}).get("entry", [])
print(f"Total VIIRS granules found: {len(entries)}")
if entries:
    for i, e in enumerate(entries[:5]):
        print(f"Granule {i}: title={e.get('title')}, time_start={e.get('time_start')}, time_end={e.get('time_end')}")
