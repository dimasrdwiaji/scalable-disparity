import pytest
import torch
from phys_living_index.models.gnn_autoencoder import SpatialGATAutoencoder


def test_gat_autoencoder_forward_shape():
    num_nodes = 50
    in_channels = 6
    latent_dim = 2
    
    model = SpatialGATAutoencoder(in_channels=in_channels, hidden_dim=16, latent_dim=latent_dim)
    
    # Random feature matrix (normalized between 0 and 1)
    x = torch.rand((num_nodes, in_channels))
    
    # Ring graph edges
    src = torch.arange(num_nodes)
    dst = (src + 1) % num_nodes
    edge_index = torch.stack([torch.cat([src, dst]), torch.cat([dst, src])], dim=0)
    
    z, x_hat, attentions = model(x, edge_index)
    
    assert z.shape == (num_nodes, latent_dim)
    assert x_hat.shape == (num_nodes, in_channels)
    # Output bounded by Sigmoid
    assert torch.all(x_hat >= 0.0)
    assert torch.all(x_hat <= 1.0)
    
    # Test reconstruction friction
    friction = model.compute_reconstruction_friction(x, x_hat)
    assert friction.shape == (num_nodes,)
    assert torch.all(friction >= 0.0)
