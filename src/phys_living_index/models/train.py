"""
Training pipeline for the SpatialGATAutoencoder on H3 Adjacency Graphs.
"""

import torch

from .gnn_autoencoder import SpatialGATAutoencoder


def train_step(
    model: SpatialGATAutoencoder,
    optimizer: torch.optim.Optimizer,
    x: torch.Tensor,
    edge_index: torch.Tensor,
    loss_weights: dict[str, float] | None = None,
    mask: torch.Tensor | None = None,
    channel_weights: torch.Tensor | None = None,
) -> dict[str, float]:
    """
    Executes a single optimization step minimizing feature reconstruction error
    and graph Dirichlet smoothness regularization.

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
        Weights for reconstruction and structure loss. Default: {'reconstruction': 1.0, 'structure': 0.1}.
    mask : torch.Tensor | None, optional
        Boolean tensor of shape (N,) indicating active/populated nodes to compute reconstruction loss on.
        If None, all nodes are included.
    channel_weights : torch.Tensor | None, optional
        Tensor of shape (in_channels,) weighting reconstruction loss across channels
        (e.g., inverse channel variance for standardized scaling).

    Returns
    -------
    dict[str, float]
        Dictionary of loss terms for this step.
    """
    if loss_weights is None:
        loss_weights = {"reconstruction": 1.0, "structure": 0.1}

    model.train()
    optimizer.zero_grad()

    z, x_hat, _ = model(x, edge_index)

    # 1. Feature reconstruction loss (optionally masked and channel-standardized)
    if mask is not None:
        target_x = x[mask]
        pred_x = x_hat[mask]
    else:
        target_x = x
        pred_x = x_hat

    sq_err = (pred_x - target_x) ** 2
    if channel_weights is not None:
        loss_recon = torch.mean(channel_weights * sq_err)
    else:
        loss_recon = torch.mean(sq_err)

    # 2. Graph topological Dirichlet smoothness regularization:
    # L_struct = (1 / |E|) * sum_{(u,v) in E} ||z_u - z_v||_2^2
    # Formalizes Tobler's First Law of Geography without unbounded link drift.
    if edge_index.shape[1] > 0:
        diff = z[edge_index[0]] - z[edge_index[1]]
        loss_struct = torch.mean(torch.sum(diff ** 2, dim=1))
    else:
        loss_struct = torch.tensor(0.0, device=x.device)

    total_loss = (
        loss_weights.get("reconstruction", 1.0) * loss_recon
        + loss_weights.get("structure", 0.1) * loss_struct
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
    mask: torch.Tensor | None = None,
    channel_weights: torch.Tensor | None = None,
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
    mask : torch.Tensor | None, optional
        Boolean tensor of shape (N,) indicating populated nodes to supervise.
    channel_weights : torch.Tensor | None, optional
        Tensor of shape (in_channels,) weighting reconstruction loss.
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
        step_metrics = train_step(
            model=model,
            optimizer=optimizer,
            x=x,
            edge_index=edge_index,
            loss_weights=loss_weights,
            mask=mask,
            channel_weights=channel_weights,
        )
        history.append(step_metrics)
        if verbose and (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1:03d} | Total Loss: {step_metrics['total_loss']:.4f}")

    model.eval()
    with torch.no_grad():
        z_final, x_hat_final, _ = model(x, edge_index)

    return history, z_final, x_hat_final
