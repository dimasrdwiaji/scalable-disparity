import h3
import pytest
import torch

from phys_living_index.models.gnn_autoencoder import (
    SpatialGATAutoencoder,
    build_h3_geometric_graph,
)
from phys_living_index.models.train import train_gat_autoencoder


def test_gat_autoencoder_forward_shape():
    num_nodes = 50
    in_channels = 10
    latent_dim = 2

    model = SpatialGATAutoencoder(in_channels=in_channels, hidden_dim=16, latent_dim=latent_dim)
    x = torch.rand((num_nodes, in_channels))

    src = torch.arange(num_nodes)
    dst = (src + 1) % num_nodes
    edge_index = torch.stack([torch.cat([src, dst]), torch.cat([dst, src])], dim=0)

    z, x_hat, (edge_out, alpha) = model(x, edge_index)

    assert z.shape == (num_nodes, latent_dim)
    assert x_hat.shape == (num_nodes, in_channels)
    assert edge_out.shape[0] == 2
    assert alpha.shape[0] == edge_out.shape[1]
    assert torch.all(x_hat >= 0.0)
    assert torch.all(x_hat <= 1.0)

    friction = model.compute_reconstruction_friction(x, x_hat)
    assert friction.shape == (num_nodes,)
    assert torch.all(friction >= 0.0)


def test_build_h3_geometric_graph():
    # Pick a real H3 Res-8 index and get its 1-ring neighbors (7 hexes total)
    center_hex = h3.latlng_to_cell(-6.2, 106.8, 8)
    hex_ring = list(h3.grid_disk(center_hex, 1))
    assert len(hex_ring) == 7

    edge_index, hex_to_idx = build_h3_geometric_graph(hex_ring)
    assert edge_index.shape[0] == 2
    assert edge_index.shape[1] > 0
    assert len(hex_to_idx) == 7
    # Center hex has 6 neighbors in the disk -> 6 outgoing + 6 incoming = 12 directed edges with center
    center_idx = hex_to_idx[center_hex]
    assert (edge_index[0] == center_idx).sum().item() == 6


def test_train_gat_autoencoder_convergence():
    torch.manual_seed(42)
    num_nodes = 40
    in_channels = 10
    latent_dim = 2

    # Ring graph edges
    src = torch.arange(num_nodes)
    dst = (src + 1) % num_nodes
    edge_index = torch.stack([torch.cat([src, dst]), torch.cat([dst, src])], dim=0)

    # Smooth synthetic feature matrix
    x = torch.rand((num_nodes, in_channels))

    model = SpatialGATAutoencoder(in_channels=in_channels, hidden_dim=16, latent_dim=latent_dim)

    history, z_final, x_hat_final = train_gat_autoencoder(
        model=model,
        x=x,
        edge_index=edge_index,
        epochs=30,
        lr=0.01,
        loss_weights={"reconstruction": 1.0, "structure": 0.1},
    )

    assert len(history) == 30
    assert history[-1]["total_loss"] < history[0]["total_loss"]
    assert z_final.shape == (num_nodes, latent_dim)
    assert x_hat_final.shape == (num_nodes, in_channels)


def test_attributed_error_decomposition_and_edge_friction():
    num_nodes = 20
    in_channels = 10
    model = SpatialGATAutoencoder(in_channels=in_channels, hidden_dim=16, latent_dim=2)

    x = torch.rand((num_nodes, in_channels))
    x_hat = torch.rand((num_nodes, in_channels))

    decomp = model.compute_attributed_friction(x, x_hat)
    assert "friction_total" in decomp
    assert "friction_socio" in decomp
    assert "friction_bio" in decomp

    # Check additive decomposition
    total_reconstructed = decomp["friction_socio"] + decomp["friction_bio"]
    assert torch.allclose(decomp["friction_total"], total_reconstructed, atol=1e-5)

    # Check edge friction
    edge_index = torch.tensor([[0, 1], [1, 0]], dtype=torch.long)
    alpha = torch.tensor([[0.8, 0.6], [0.1, 0.3]], dtype=torch.float32)  # 2 heads
    _, edge_fric = model.compute_edge_boundary_friction(edge_index, alpha)
    assert edge_fric.shape == (2,)
    assert edge_fric[0].item() == pytest.approx(1.0 - 0.7)  # mean(0.8, 0.6) = 0.7 -> fric = 0.3
    assert edge_fric[1].item() == pytest.approx(1.0 - 0.2)  # mean(0.1, 0.3) = 0.2 -> fric = 0.8
