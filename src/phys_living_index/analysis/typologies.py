"""
HDBSCAN density clustering on latent GAT embeddings (Z) to uncover organic neighborhood archetypes.

This module discovers unsupervised morphological and socioeconomic clusters across the
metropolitan landscape without imposing predefined administrative boundaries or arbitrary
k-means cluster counts.

By clustering directly within the low-dimensional latent space Z in R^(N x 2) learned by the
Spatial GAT Autoencoder, HDBSCAN groups settlements by continuous multidimensional similarity:
- Organic Typologies: Discovers natural settlement forms (e.g. Dense Core Kampungs,
  Disconnected Peri-Urban Sprawl, Planned Master Enclaves, Multi-Deprived Pockets).
- Noise Robustness: Cells assigned label -1 represent transitional edge cells, industrial
  facilities, or spatial outliers that do not conform to major settlement archetypes.
"""

from typing import Any

import hdbscan
import numpy as np


def discover_neighborhood_typologies(
    z_embeddings: np.ndarray,
    min_cluster_size: int = 25,
    min_samples: int = 10,
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Applies HDBSCAN density clustering to the 2D latent space embeddings (Z).

    Parameters
    ----------
    z_embeddings : np.ndarray
        Array of shape (N, 2) extracted from the SpatialGATAutoencoder bottleneck.
    min_cluster_size : int, optional
        Minimum number of spatial cells required to form an archetype cluster (default 25).
    min_samples : int, optional
        Number of samples in a neighborhood for a point to be considered a core point (default 10).

    Returns
    -------
    tuple[np.ndarray, dict[str, Any]]
        labels: Cluster assignment per cell (-1 designates noise / atypical cells).
        stats: Diagnostic dictionary containing cluster counts, noise ratios, and archetype sizes.
    """
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric="euclidean",
        prediction_data=True,
    )
    labels = clusterer.fit_predict(z_embeddings)

    unique_clusters = set(labels) - {-1}
    stats = {
        "num_clusters": len(unique_clusters),
        "noise_ratio": float(np.mean(labels == -1)),
        "cluster_sizes": {int(c): int(np.sum(labels == c)) for c in unique_clusters},
    }
    return labels, stats
