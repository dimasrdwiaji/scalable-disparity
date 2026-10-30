import torch

from phys_living_index.models.ablation import run_bottleneck_ablation


def test_run_bottleneck_ablation_dimensions():
    num_nodes = 50
    in_channels = 10

    # Ring graph edges
    src = torch.arange(num_nodes)
    dst = (src + 1) % num_nodes
    edge_index = torch.stack([torch.cat([src, dst]), torch.cat([dst, src])], dim=0)

    # Synthetic multi-cluster features
    cluster1 = torch.normal(0.2, 0.05, size=(25, in_channels))
    cluster2 = torch.normal(0.8, 0.05, size=(25, in_channels))
    x = torch.cat([cluster1, cluster2], dim=0).clamp(0.0, 1.0)

    results = run_bottleneck_ablation(
        x=x,
        edge_index=edge_index,
        latent_dims=[2, 4],
        epochs=15,
        lr=0.02,
        seed=42,
    )

    assert len(results) == 2
    assert results[0]["latent_dim"] == 2
    assert results[1]["latent_dim"] == 4

    for r in results:
        assert "mse_recon" in r
        assert "bce_struct" in r
        assert "num_clusters" in r
        assert r["mse_recon"] > 0.0
