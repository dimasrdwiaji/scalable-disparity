"""
Training script for the SpatialGATAutoencoder on H3 Adjacency Graphs.
"""

from typing import Dict, Any
import torch
import torch.nn.functional as F
from .gnn_autoencoder import SpatialGATAutoencoder


def train_step(
    model: SpatialGATAutoencoder,
    optimizer: torch.optim.Optimizer,
    x: torch.Tensor,
    edge_index: torch.Tensor,
    loss_weights: Dict[str, float],
) -> float:
    """Executes a single optimization step."""
    model.train()
    optimizer.zero_grad()
    
    z, x_hat, _ = model(x, edge_index)
    
    # Feature reconstruction loss
    loss_recon = F.mse_loss(x_hat, x)
    
    # Graph structure regularization (inner product decoder)
    adj_recon = torch.sigmoid(torch.mm(z, z.t()))
    # Simplified adjacency loss sample
    loss = loss_weights.get("reconstruction", 1.0) * loss_recon
    
    loss.backward()
    optimizer.step()
    return loss.item()
