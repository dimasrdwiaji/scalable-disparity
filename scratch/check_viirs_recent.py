import requests
from phys_living_index.data.credentials import load_earthdata_token

token = load_earthdata_token()
bbox = (106.35, -6.75, 107.65, -5.95)
cmr_url = "https://cmr.earthdata.nasa.gov/search/granules.json"
headers = {"Authorization": f"Bearer {token}"}

for yr in [2024, 2023, 2022, 2021]:
    params = {
        "short_name": "VNP46A2",
        "bounding_box": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
        "temporal": f"{yr}-06-01T00:00:00Z,{yr}-06-30T23:59:59Z",
        "page_size": 2,
    }
    resp = requests.get(cmr_url, params=params, headers=headers)
    data = resp.json()
    entries = data.get("feed", {}).get("entry", [])
    print(f"Year {yr} granules found: {len(entries)}")
    if entries:
        print(f"  Sample: {entries[0].get('title')} ({entries[0].get('time_start')})")
