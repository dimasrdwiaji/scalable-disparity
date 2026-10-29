import torch

from phys_living_index.models.gnn_autoencoder import SpatialGATAutoencoder


def test_gat_autoencoder_forward_shape():
    num_nodes = 50
    # Test with 10D expanded feature vector
    in_channels = 10
    latent_dim = 2

    model = SpatialGATAutoencoder(in_channels=in_channels, hidden_dim=16, latent_dim=latent_dim)

    # Random feature matrix (normalized between 0 and 1)
    x = torch.rand((num_nodes, in_channels))

    # Ring graph edges representing H3 topological adjacency
    src = torch.arange(num_nodes)
    dst = (src + 1) % num_nodes
    edge_index = torch.stack([torch.cat([src, dst]), torch.cat([dst, src])], dim=0)

    z, x_hat, (edge_out, alpha) = model(x, edge_index)

    assert z.shape == (num_nodes, latent_dim)
    assert x_hat.shape == (num_nodes, in_channels)
    assert edge_out.shape[0] == 2
    assert alpha.shape[0] == edge_out.shape[1]

    # Reconstructed features bounded by Sigmoid to [0, 1]
    assert torch.all(x_hat >= 0.0)
    assert torch.all(x_hat <= 1.0)

    # Test reconstruction friction
    friction = model.compute_reconstruction_friction(x, x_hat)
    assert friction.shape == (num_nodes,)
    assert torch.all(friction >= 0.0)
