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
    mask: torch.Tensor | None = None,
    channel_weights: torch.Tensor | None = None,
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
    mask : torch.Tensor | None, optional
        Populated node mask (N,).
    channel_weights : torch.Tensor | None, optional
        Weights per channel (in_channels,).
    seed : int, default 42
        Random seed for reproducibility.

    Returns
    -------
    list[dict[str, Any]]
        Ablation report comparing MSE, Dirichlet structure loss, and cluster metrics per dimension.
    """
    if latent_dims is None:
        latent_dims = [2, 3, 4, 8]

    in_channels = x.shape[1]
    results: list[dict[str, Any]] = []

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
            mask=mask,
            channel_weights=channel_weights,
        )

        # 1. Feature reconstruction MSE
        if mask is not None:
            mse = float(F.mse_loss(x_hat[mask], x[mask]).item())
        else:
            mse = float(F.mse_loss(x_hat, x).item())

        # 2. Dirichlet smoothness regularization
        if edge_index.shape[1] > 0:
            diff = z[edge_index[0]] - z[edge_index[1]]
            struct_loss = float(torch.mean(torch.sum(diff ** 2, dim=1)).item())
        else:
            struct_loss = 0.0

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
            "struct_loss": struct_loss,
            "bce_struct": struct_loss,  # alias for backward compatibility
            "num_clusters": num_clusters,
            "noise_ratio": stats.get("noise_ratio", 0.0),
            "silhouette_score": sil_score,
        })

    return results
