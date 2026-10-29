"""
Ablation study module for GAT Autoencoder latent bottleneck dimension d in {2, 3, 4, 8}.

Evaluates:
- Feature reconstruction Mean Squared Error (MSE).
- Topological graph link reconstruction loss (Binary Cross Entropy).
- HDBSCAN clustering quality (Silhouette Score and valid cluster counts).
"""

from typing import Any

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import silhouette_score

from ..analysis.typologies import discover_neighborhood_typologies
from .gnn_autoencoder import SpatialGATAutoencoder
from .train import train_gat_autoencoder


def run_bottleneck_ablation(
    x: torch.Tensor,
    edge_index: torch.Tensor,
    latent_dims: list[int] | None = None,
    epochs: int = 40,
    lr: float = 0.01,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """
    Runs multi-dimensional bottleneck ablation across candidate latent sizes.

    Parameters
    ----------
    x : torch.Tensor
        Feature matrix (N, in_channels).
    edge_index : torch.Tensor
        Topological graph edges (2, E).
    latent_dims : list[int] | None, optional
        List of latent dimensions to evaluate (default [2, 3, 4, 8]).
    epochs : int, default 40
        Number of epochs per run.
    lr : float, default 0.01
        Learning rate.
    seed : int, default 42
        Random seed for reproducibility.

    Returns
    -------
    list[dict[str, Any]]
        Ablation report comparing MSE, BCE, and cluster metrics per dimension.
    """
    if latent_dims is None:
        latent_dims = [2, 3, 4, 8]

    in_channels = x.shape[1]
    results: list[dict[str, Any]] = []

    pos_u, pos_v = edge_index[0], edge_index[1]

    for d in latent_dims:
        torch.manual_seed(seed)
        model = SpatialGATAutoencoder(
            in_channels=in_channels,
            hidden_dim=16,
            latent_dim=d,
        )

        _, z, x_hat = train_gat_autoencoder(
            model=model,
            x=x,
            edge_index=edge_index,
            epochs=epochs,
            lr=lr,
        )

        # 1. Feature reconstruction MSE
        mse = float(F.mse_loss(x_hat, x).item())

        # 2. Structure regularization BCE
        if edge_index.shape[1] > 0:
            pos_scores = torch.sum(z[pos_u] * z[pos_v], dim=1)
            bce = float(
                F.binary_cross_entropy_with_logits(
                    pos_scores, torch.ones_like(pos_scores)
                ).item()
            )
        else:
            bce = 0.0

        # 3. Latent space clustering quality
        z_np = z.detach().cpu().numpy()
        labels, stats = discover_neighborhood_typologies(
            z_np, min_cluster_size=max(5, len(x) // 10), min_samples=3
        )

        # Calculate silhouette score for non-noise points
        valid_mask = labels >= 0
        num_clusters = len(set(labels[valid_mask]))
        if num_clusters >= 2 and np.sum(valid_mask) > num_clusters:
            sil_score = float(silhouette_score(z_np[valid_mask], labels[valid_mask]))
        else:
            sil_score = float("nan")

        results.append({
            "latent_dim": d,
            "mse_recon": mse,
            "bce_struct": bce,
            "num_clusters": num_clusters,
            "noise_ratio": stats.get("noise_ratio", 0.0),
            "silhouette_score": sil_score,
        })

    return results
