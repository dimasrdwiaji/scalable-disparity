import os
import sys
import time
import urllib.request
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
data_raw = repo_root / "data" / "raw"
data_raw.mkdir(parents=True, exist_ok=True)

target_path = data_raw / "java-latest.osm.pbf"
url = "https://download.geofabrik.de/asia/indonesia/java-latest.osm.pbf"

print(f"Target path: {target_path}", flush=True)
print(f"Downloading from: {url}", flush=True)

# Check if file already exists with full size (~857 MB = 899,095,496 bytes)
if target_path.exists() and target_path.stat().st_size > 800 * 1024 * 1024:
    print(f"File already exists and is complete: {target_path.stat().st_size / (1024*1024):.2f} MB. Skipping download.", flush=True)
    sys.exit(0)

# Streaming download with progress report every 50 MB or 10 seconds
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (GeoAI Research Pipeline)"})
t0 = time.time()
last_report_time = t0
downloaded_bytes = 0

with urllib.request.urlopen(req) as response:
    total_size = int(response.headers.get("Content-Length", 0))
    print(f"Total size: {total_size / (1024*1024):.2f} MB", flush=True)
    
    chunk_size = 1024 * 1024 # 1 MB chunks
    temp_path = target_path.with_suffix(".pbf.part")
    
    with open(temp_path, "wb") as f:
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            downloaded_bytes += len(chunk)
            
            now = time.time()
            if now - last_report_time >= 5.0:
                elapsed = now - t0
                speed_mb = (downloaded_bytes / (1024*1024)) / max(elapsed, 0.001)
                pct = (downloaded_bytes / total_size * 100) if total_size > 0 else 0
                print(f"Downloaded {downloaded_bytes / (1024*1024):.1f} / {total_size / (1024*1024):.1f} MB ({pct:.1f}%) at {speed_mb:.1f} MB/s", flush=True)
                last_report_time = now

# Rename part to final
temp_path.replace(target_path)
total_time = time.time() - t0
print(f"Download complete: {target_path.stat().st_size / (1024*1024):.2f} MB in {total_time:.1f} seconds (average {(downloaded_bytes / (1024*1024)) / total_time:.1f} MB/s).", flush=True)
