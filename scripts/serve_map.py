"""
Launch the interactive localhost web map for inspecting Stage 3 H3 inputs & outputs.

Usage:
    uv run python scripts/serve_map.py
    uv run python scripts/serve_map.py --port 8765 --rebuild --open
"""

import argparse
import logging
import os
import sys
import webbrowser
from http.server import ThreadingHTTPServer
from pathlib import Path

import pyproj

os.environ["PROJ_DATA"] = pyproj.datadir.get_data_dir()
os.environ["PROJ_LIB"] = pyproj.datadir.get_data_dir()

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "src"))

from phys_living_index.visualization.web_map import export_map_assets, make_map_handler  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Port to serve on (default: 8765)")
    parser.add_argument("--rebuild", action="store_true", help="Re-export GeoJSON map assets from parquet.")
    parser.add_argument("--open", action="store_true", help="Open the map URL in the default browser.")
    args = parser.parse_args()

    map_dir = repo_root / "data" / "processed" / "map"
    export_map_assets(repo_root, output_dir=map_dir, rebuild=args.rebuild)

    url = f"http://{args.host}:{args.port}/"
    server = ThreadingHTTPServer((args.host, args.port), make_map_handler(map_dir))
    logging.info("Serving Physical Living Index interactive map at %s (Ctrl+C to stop)", url)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Shutting down map server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
