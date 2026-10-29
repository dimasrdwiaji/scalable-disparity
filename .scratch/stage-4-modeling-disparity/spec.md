Status: in-progress

# Spec: Stage 4 — Model Training, Error Decomposition, Bottleneck Ablation & Disparity Metrics

Source: `.scratch/project-roadmap/map.md` (Stage 4), `docs/research_plan.md`, `docs/adr/0001-h3-gat-ae-unsupervised-disparity.md`, and reviewer recommendations `REV-4`, `REV-5`, `REV-6`.

## Problem Statement
Having engineered the 10-dimensional feature matrix $X \in [0.0, 1.0]^{N \times 10}$ and pedestrian accessibility metrics in Stage 3, Stage 4 turns this spatial matrix into unsupervised micro-segregation detection and neighborhood typology discovery. Specifically:
1. `src/phys_living_index/models/train.py` contains only an elementary placeholder `train_step`. It lacks a complete training loop with dual reconstruction/adjacency regularization losses, convergence monitoring, and embedding extraction.
2. Under reviewer recommendation `REV-5`, raw reconstruction error conflates natural unpopulated land-use edges (rivers, parks, industrial zones) with true socio-spatial inequality. We must implement DOMINANT-style error decomposition ($\text{Friction}_{\text{socio}}$ vs $\text{Friction}_{\text{bio}}$) and edge attention friction ($1 - \alpha_{ij}$).
3. Under reviewer recommendation `REV-6`, the choice of 2D latent bottleneck ($d=2$) must be rigorously ablated against $d \in \{2, 3, 4, 8\}$ across reconstruction MSE, topological BCE, and cluster silhouette scores.
4. Under reviewer recommendation `REV-4`, the deep non-linear GAT-AE must be benchmarked against standard linear spatial autocorrelation via Bivariate Local Moran's $I$ (LISA) using `esda`/`libpysal`, alongside local focal Gini/Palma inequality surfaces.

## Solution
1. Implement a complete training harness `train_gat_autoencoder` in `src/phys_living_index/models/train.py` and graph construction utilities in `src/phys_living_index/models/gnn_autoencoder.py`.
2. Implement attributed error decomposition in `SpatialGATAutoencoder` (`compute_attributed_friction`) and edge boundary friction extraction.
3. Build a reproducible ablation harness in `src/phys_living_index/models/ablation.py` benchmarking $d \in \{2, 3, 4, 8\}$.
4. Implement Bivariate Local Moran's $I$ and local focal moving-window inequality metrics in `src/phys_living_index/analysis/disparity_metrics.py`.

## User Stories
1. As a machine learning engineer, I want `build_h3_geometric_graph` to convert a set of H3 indices into pure topological adjacency edges without boundary pruning.
2. As a model trainer, I want `train_gat_autoencoder` to minimize both feature reconstruction MSE and latent structure regularization, returning learned latent embeddings $Z$ and reconstructed $\hat{X}$.
3. As an urban researcher, I want `compute_attributed_friction` to separate $\text{Friction}_{\text{socio}}$ from $\text{Friction}_{\text{bio}}$ so that socio-spatial segregation is distinguished from natural water/vegetation borders.
4. As a reviewer, I want an automated ablation suite evaluating $d \in \{2, 3, 4, 8\}$ to verify the stability and optimality of the 2D bottleneck.
5. As a spatial statistician, I want `compute_bivariate_local_moran` and focal inequality windows to benchmark GAT-AE against classical spatial autocorrelation.
