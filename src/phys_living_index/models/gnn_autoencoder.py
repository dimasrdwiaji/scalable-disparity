"""
Spatial Graph Attention Autoencoder (SpatialGATAutoencoder) with bottleneck dimension d=2.

This module implements the core unsupervised deep learning model for spatial disparity mapping:
1. Pure Geometric H3 Adjacency:
   The graph topology is defined strictly by hexagonal edge sharing on the H3 grid (A_ij = 1).
   Physical segregation boundaries (e.g., 3-meter concrete perimeter walls separating
   master-planned enclaves from informal kampungs) are NOT pruned from the graph.
2. Low-Dimensional Latent Bottleneck (d = 2):
   By forcing the autoencoder through a strict 2-dimensional bottleneck, the model learns
   a smooth manifold expecting spatial continuity across neighboring hexagons.
3. Segregation Friction as Reconstruction Error:
   Where abrupt physical segregation occurs, neighboring cells exhibit sharp step-function
   jumps across their feature vectors. Because the smooth decoder cannot reconstruct these
   discontinuities, the node-level reconstruction error ||x_i - x_hat_i||² spikes precisely
   along the physical segregation wall.
4. Edge Attention Corroboration:
   The learned graph attention coefficients alpha_ij provide dual edge-level corroboration:
   where the model suppresses message passing between adjacent cells (alpha_ij -> 0),
   the edge friction (1 - alpha_ij) confirms an unbridgeable socio-spatial boundary.
"""

import torch
from torch import nn
from torch_geometric.nn import GATConv


class SpatialGATAutoencoder(nn.Module):
    """
    Graph Attention Autoencoder for unsupervised spatial living standard disparity detection.

    Attributes
    ----------
    in_channels : int
        Number of input feature dimensions (e.g. 6 for canonical, 10 for expanded).
    hidden_dim : int
        Dimension of the intermediate graph convolutional layer.
    latent_dim : int
        Bottleneck latent dimension (default d=2 for 2D neighborhood topology discovery).
    heads : int
        Number of multi-head attention mechanisms in the first GAT layer.
    """

    def __init__(
        self,
        in_channels: int = 10,
        hidden_dim: int = 16,
        latent_dim: int = 2,
        heads: int = 2,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim

        # Encoder: 2-layer Graph Attention Network extracting edge attention weights
        self.conv1 = GATConv(in_channels, hidden_dim, heads=heads, concat=True)
        self.conv2 = GATConv(hidden_dim * heads, latent_dim, heads=1, concat=False)

        # Decoder: Multi-Layer Perceptron reconstructing feature space bounded to [0.0, 1.0]
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, in_channels),
            nn.Sigmoid(),
        )

    def encode(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> tuple[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
        """
        Encodes node features into the 2D latent space and captures learned attention weights.

        Parameters
        ----------
        x : torch.Tensor
            Normalized node feature matrix of shape (N, in_channels).
        edge_index : torch.Tensor
            Graph edge index tensor of shape (2, E) representing H3 topological adjacency.

        Returns
        -------
        tuple[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]
            z: Latent embeddings (N, latent_dim).
            (edge_index_out, alpha1): Attention weights from the first GAT layer.
        """
        x, (edge_index_out, alpha1) = self.conv1(x, edge_index, return_attention_weights=True)
        x = torch.relu(x)
        z, _ = self.conv2(x, edge_index, return_attention_weights=True)
        return z, (edge_index_out, alpha1)

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """
        Decodes 2D latent embeddings back to the normalized feature space.

        Parameters
        ----------
        z : torch.Tensor
            Latent bottleneck tensor of shape (N, latent_dim).

        Returns
        -------
        torch.Tensor
            Reconstructed feature matrix x_hat of shape (N, in_channels) in [0.0, 1.0].
        """
        return self.decoder(z)

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
        """
        Executes the full forward pass through encoder and decoder.

        Parameters
        ----------
        x : torch.Tensor
            Input feature matrix of shape (N, in_channels).
        edge_index : torch.Tensor
            H3 adjacency graph edges of shape (2, E).

        Returns
        -------
        tuple[torch.Tensor, torch.Tensor, tuple[torch.Tensor, torch.Tensor]]
            z: Latent bottleneck embeddings (N, latent_dim).
            x_hat: Reconstructed feature matrix (N, in_channels).
            attentions: Edge index and multi-head attention coefficients (edge_index, alpha).
        """
        z, attentions = self.encode(x, edge_index)
        x_hat = self.decode(z)
        return z, x_hat, attentions

    def compute_reconstruction_friction(
        self,
        x: torch.Tensor,
        x_hat: torch.Tensor,
    ) -> torch.Tensor:
        """
        Computes node-level Segregation Friction as squared reconstruction error ||x - x_hat||².

        Parameters
        ----------
        x : torch.Tensor
            Ground-truth normalized features of shape (N, in_channels).
        x_hat : torch.Tensor
            Autoencoder reconstructed features of shape (N, in_channels).

        Returns
        -------
        torch.Tensor
            Per-node reconstruction friction scalar of shape (N,).
        """
        return torch.sum((x - x_hat) ** 2, dim=1)
