"""
Training pipeline for the SpatialGATAutoencoder on H3 Adjacency Graphs.
"""

import torch
import torch.nn.functional as F

from .gnn_autoencoder import SpatialGATAutoencoder


def train_step(
    model: SpatialGATAutoencoder,
    optimizer: torch.optim.Optimizer,
    x: torch.Tensor,
    edge_index: torch.Tensor,
    loss_weights: dict[str, float] | None = None,
) -> dict[str, float]:
    """
    Executes a single optimization step minimizing feature reconstruction error
    and graph structure regularization.

    Parameters
    ----------
    model : SpatialGATAutoencoder
        The autoencoder model.
    optimizer : torch.optim.Optimizer
        PyTorch optimizer.
    x : torch.Tensor
        Feature matrix (N, in_channels).
    edge_index : torch.Tensor
        Topological graph edges (2, E).
    loss_weights : dict[str, float] | None, optional
        Weights for reconstruction and structure loss.

    Returns
    -------
    dict[str, float]
        Dictionary of loss terms for this step.
    """
    if loss_weights is None:
        loss_weights = {"reconstruction": 1.0, "structure": 0.05}

    model.train()
    optimizer.zero_grad()

    z, x_hat, _ = model(x, edge_index)

    # 1. Feature reconstruction loss (MSE)
    loss_recon = F.mse_loss(x_hat, x)

    # 2. Graph topological link structure regularization
    # Sample positive edge inner products to be close to 1
    if edge_index.shape[1] > 0:
        pos_u, pos_v = edge_index[0], edge_index[1]
        pos_scores = torch.sum(z[pos_u] * z[pos_v], dim=1)
        loss_struct = F.binary_cross_entropy_with_logits(
            pos_scores, torch.ones_like(pos_scores)
        )
    else:
        loss_struct = torch.tensor(0.0, device=x.device)

    total_loss = (
        loss_weights.get("reconstruction", 1.0) * loss_recon
        + loss_weights.get("structure", 0.05) * loss_struct
    )

    total_loss.backward()
    optimizer.step()

    return {
        "total_loss": float(total_loss.item()),
        "recon_loss": float(loss_recon.item()),
        "struct_loss": float(loss_struct.item()),
    }


def train_gat_autoencoder(
    model: SpatialGATAutoencoder,
    x: torch.Tensor,
    edge_index: torch.Tensor,
    epochs: int = 50,
    lr: float = 0.01,
    weight_decay: float = 1e-4,
    loss_weights: dict[str, float] | None = None,
    verbose: bool = False,
) -> tuple[list[dict[str, float]], torch.Tensor, torch.Tensor]:
    """
    Trains the SpatialGATAutoencoder over multiple epochs and extracts final embeddings.

    Parameters
    ----------
    model : SpatialGATAutoencoder
        Model to train.
    x : torch.Tensor
        Node feature matrix (N, in_channels).
    edge_index : torch.Tensor
        Graph edges (2, E).
    epochs : int, default 50
        Number of training epochs.
    lr : float, default 0.01
        Learning rate.
    weight_decay : float, default 1e-4
        L2 weight decay.
    loss_weights : dict[str, float] | None, optional
        Loss weighting dictionary.
    verbose : bool, default False
        Whether to print loss during training.

    Returns
    -------
    tuple[list[dict[str, float]], torch.Tensor, torch.Tensor]
        - history: List of loss metrics per epoch.
        - z_final: Final latent embeddings (N, latent_dim).
        - x_hat_final: Final reconstructed features (N, in_channels).
    """
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    history: list[dict[str, float]] = []

    for epoch in range(epochs):
        step_metrics = train_step(model, optimizer, x, edge_index, loss_weights=loss_weights)
        history.append(step_metrics)
        if verbose and (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1:03d} | Total Loss: {step_metrics['total_loss']:.4f}")

    model.eval()
    with torch.no_grad():
        z_final, x_hat_final, _ = model(x, edge_index)

    return history, z_final, x_hat_final
