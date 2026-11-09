"""
Stage 3: Feature Engineering & Spatial Harmonization onto Uber H3 Resolution 8 cells.

Single entry point (ticket 13). Builds every channel for the region config, caching each
layer under data/interim/layers/ so reruns only rebuild missing layers, then scales with the
universal benchmarks (ADR 0003) and writes:
- data/interim/h3_features_raw.parquet   raw physical values, masks, QA columns
- data/processed/feature_matrix_10d.parquet  scaled channels (NaN kept) + masks
- data/processed/feature_matrix_10d.npy      scaled channels, NaN filled for message passing
- data/processed/h3_hexagons.parquet         GeoParquet for GIS
- data/processed/stage3_qa.json              representativeness and sanity checks

Usage:
    uv run python scripts/run_feature_engineering.py [--config configs/default.yaml]
    uv run python scripts/run_feature_engineering.py --rebuild sentinel2 landsat
"""

import argparse
import logging
import os
import sys
from pathlib import Path

import pyproj

# Ensure PROJ uses the python venv bundle rather than external PostGIS proj.db
os.environ["PROJ_DATA"] = pyproj.datadir.get_data_dir()
os.environ["PROJ_LIB"] = pyproj.datadir.get_data_dir()

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "src"))

from phys_living_index.pipeline.stage3 import build_layers, run_stage3  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", default=str(repo_root / "configs" / "default.yaml"))
    parser.add_argument("--rebuild", nargs="*", default=[], help="Layer names whose cache to discard first.")
    parser.add_argument("--only-layers", nargs="*", default=None, help="Build only these layers, then stop.")
    args = parser.parse_args()

    layer_dir = repo_root / "data" / "interim" / "layers"
    for name in args.rebuild:
        (layer_dir / f"{name}.parquet").unlink(missing_ok=True)

    if args.only_layers is not None:
        build_layers(args.config, repo_root, args.only_layers, layer_dir=layer_dir)
        return

    outputs = run_stage3(args.config, repo_root, layer_dir=layer_dir)
    for key, path in outputs.items():
        logging.info("%s -> %s", key, path)


if __name__ == "__main__":
    main()
