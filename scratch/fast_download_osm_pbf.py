import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
data_raw = repo_root / "data" / "raw"
data_raw.mkdir(parents=True, exist_ok=True)

target_path = data_raw / "java-latest.osm.pbf"
url = "https://download.geofabrik.de/asia/indonesia/java-latest.osm.pbf"

print(f"Target path: {target_path}", flush=True)

# 1. Get total file size
req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    total_size = int(resp.headers.get("Content-Length", 0))

print(f"Total file size: {total_size / (1024*1024):.2f} MB ({total_size:,} bytes)", flush=True)

num_workers = 8
chunk_size = (total_size + num_workers - 1) // num_workers
ranges = []
for i in range(num_workers):
    start = i * chunk_size
    end = min(start + chunk_size - 1, total_size - 1)
    if start <= end:
        ranges.append((i, start, end))

print(f"Downloading {len(ranges)} parts with {num_workers} parallel threads...", flush=True)

t0 = time.time()
completed_bytes = [0] * len(ranges)

def download_part(part_id, start_byte, end_byte):
    part_file = data_raw / f"java_part_{part_id}.tmp"
    req_part = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Range": f"bytes={start_byte}-{end_byte}",
        },
    )
    with urllib.request.urlopen(req_part, timeout=60) as response:
        written = 0
        target_len = end_byte - start_byte + 1
        with open(part_file, "wb") as out_f:
            while written < target_len:
                block = response.read(min(256 * 1024, target_len - written))
                if not block:
                    break
                out_f.write(block)
                written += len(block)
                completed_bytes[part_id] = written
    return part_id, part_file

with ThreadPoolExecutor(max_workers=num_workers) as executor:
    futures = [executor.submit(download_part, pid, s, e) for pid, s, e in ranges]
    
    while True:
        done_count = sum(1 for f in futures if f.done())
        curr_bytes = sum(completed_bytes)
        elapsed = time.time() - t0
        speed = (curr_bytes / (1024*1024)) / max(elapsed, 0.001)
        pct = curr_bytes / total_size * 100
        print(f"Progress: {curr_bytes / (1024*1024):.1f} / {total_size / (1024*1024):.1f} MB ({pct:.1f}%) at {speed:.1f} MB/s [{done_count}/{len(ranges)} parts]", flush=True)
        if done_count == len(ranges):
            break
        time.sleep(3.0)

# Concatenate all parts
print("\nAll parts downloaded! Concatenating parts into final file...", flush=True)
part_files = [f.result()[1] for f in futures]
with open(target_path, "wb") as out_f:
    for pf in part_files:
        with open(pf, "rb") as in_f:
            while True:
                buf = in_f.read(8 * 1024 * 1024)
                if not buf:
                    break
                out_f.write(buf)
        pf.unlink(missing_ok=True)

total_time = time.time() - t0
print(f"Download complete: {target_path.stat().st_size / (1024*1024):.2f} MB in {total_time:.1f}s ({total_size / (1024*1024) / total_time:.1f} MB/s)!", flush=True)
