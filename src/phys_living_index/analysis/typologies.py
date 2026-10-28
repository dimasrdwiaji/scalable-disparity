"""
HDBSCAN clustering on latent GAT embeddings (Z) to uncover organic neighborhood archetypes.
"""

from typing import Tuple, Dict, Any
import numpy as np
import hdbscan


def discover_neighborhood_typologies(
    z_embeddings: np.ndarray,
    min_cluster_size: int = 25,
    min_samples: int = 10,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Runs HDBSCAN on the 2D latent bottleneck representations.
    
    Returns:
        cluster_labels: Array of cluster assignments (-1 represents noise / non-residential outliers).
        cluster_stats: Dictionary containing cluster metrics and archetype profiles.
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
