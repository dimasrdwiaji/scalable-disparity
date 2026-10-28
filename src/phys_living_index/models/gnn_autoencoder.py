"""
Spatial Graph Attention Autoencoder (SpatialGATAutoencoder) with strict bottleneck (d=2).
"""

from typing import Tuple
import torch
import torch.nn as nn
from torch_geometric.nn import GATConv


class SpatialGATAutoencoder(nn.Module):
    """
    Graph Attention Autoencoder for spatial living standard representation.
    
    Trained on pure geometric H3 adjacency.
    Reconstruction error ||X - X_hat||² serves as the Segregation Friction Map.
    """
    def __init__(self, in_channels: int = 6, hidden_dim: int = 16, latent_dim: int = 2, heads: int = 2):
        super().__init__()
        # Encoder: 2-layer Graph Attention Network with attention extraction
        self.conv1 = GATConv(in_channels, hidden_dim, heads=heads, concat=True)
        self.conv2 = GATConv(hidden_dim * heads, latent_dim, heads=1, concat=False)
        
        # Decoder: MLP reconstructing 6D features bounded to [0, 1]
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, in_channels),
            nn.Sigmoid(),
        )

    def encode(self, x: torch.Tensor, edge_index: torch.Tensor) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """Encodes node features into latent space and returns edge attention weights."""
        x, (edge_index_out, alpha1) = self.conv1(x, edge_index, return_attention_weights=True)
        x = torch.relu(x)
        z, (_, alpha2) = self.conv2(x, edge_index, return_attention_weights=True)
        return z, (edge_index_out, alpha1)

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decodes latent representations back to feature space."""
        return self.decoder(z)

    def forward(
        self, x: torch.Tensor, edge_index: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """
        Forward pass.
        
        Returns:
            z: Latent embeddings (N, 2)
            x_hat: Reconstructed features (N, 6)
            attentions: Learned attention coefficients on edges
        """
        z, attentions = self.encode(x, edge_index)
        x_hat = self.decode(z)
        return z, x_hat, attentions

    def compute_reconstruction_friction(self, x: torch.Tensor, x_hat: torch.Tensor) -> torch.Tensor:
        """Computes node-level reconstruction error ||x - x_hat||²."""
        return torch.sum((x - x_hat) ** 2, dim=1)
