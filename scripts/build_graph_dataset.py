"""
Serializes the H3 spatial graph and 10-dimensional feature matrix into a PyTorch Geometric
Data object for Stage 4 GAT-AE modeling.

Per ADR 0003 §3, the main run uses uniform channel weights; inverse-variance weights over the
modelled cells are stored alongside as `channel_weights_inverse_variance` for the Stage 4
sensitivity run. The training mask is `is_modelled` (residential cells with every channel
valid); other cells stay in the graph for message passing only.
"""

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch_geometric.data import Data

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "src"))

from phys_living_index.models.gnn_autoencoder import build_h3_geometric_graph  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("build_graph_dataset")

processed_dir = repo_root / "data" / "processed"


def inverse_variance_weights(x: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Inverse per-channel variance over masked cells, normalized to mean 1 (sensitivity run)."""
    raw = 1.0 / (np.var(x[mask], axis=0) + 1e-4)
    return raw / raw.mean()


def build_and_save_pyg_dataset(
    processed_dir: Path = processed_dir,
    output_path: Path | None = None,
) -> Data:
    """
    Loads the scaled feature matrix, builds the H3 adjacency graph, and serializes the PyG Data.
    """
    if output_path is None:
        output_path = processed_dir / "graph_data.pt"

    pq_path = processed_dir / "feature_matrix_7d.parquet"
    npy_file = processed_dir / "feature_matrix_7d.npy"
    if not pq_path.exists():
        pq_path = processed_dir / "feature_matrix_10d.parquet"
        npy_file = processed_dir / "feature_matrix_10d.npy"

    df = pd.read_parquet(pq_path)
    x_np = np.load(npy_file).astype(np.float32)

    dim_cols = [c for c in df.columns if c not in ("is_residential", "has_complete_features", "is_modelled")]
    if x_np.shape != (len(df), len(dim_cols)):
        raise ValueError(f"Matrix shape {x_np.shape} does not match table ({len(df)}, {len(dim_cols)})")
    if not np.isfinite(x_np).all():
        raise ValueError("Feature matrix contains NaN or Inf")

    hex_ids = df.index.astype(str).tolist()
    edge_index, _ = build_h3_geometric_graph(hex_ids)
    logger.info("Graph: %d nodes, %d directed edges, %d features.", len(hex_ids), edge_index.shape[1], len(dim_cols))

    is_modelled = df["is_modelled"].to_numpy(dtype=bool).copy()
    is_residential = df["is_residential"].to_numpy(dtype=bool).copy()
    uniform = np.ones(len(dim_cols), dtype=np.float32)
    inv_var = inverse_variance_weights(x_np, is_modelled).astype(np.float32)
    for name, w in zip(dim_cols, inv_var, strict=True):
        logger.info("  %-28s inverse-variance weight (sensitivity run) = %5.2f", name, w)

    data = Data(
        x=torch.from_numpy(x_np),
        edge_index=edge_index,
        is_modelled=torch.from_numpy(is_modelled),
        is_residential=torch.from_numpy(is_residential),
        channel_weights=torch.from_numpy(uniform),
        channel_weights_inverse_variance=torch.from_numpy(inv_var),
        feature_names=list(dim_cols),
        h3_indices=hex_ids,
    )
    torch.save(data, output_path)
    logger.info("Saved %s (%d modelled of %d cells).", output_path, int(is_modelled.sum()), len(hex_ids))
    return data


if __name__ == "__main__":
    build_and_save_pyg_dataset()
