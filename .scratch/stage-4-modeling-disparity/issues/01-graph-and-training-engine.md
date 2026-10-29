# 01: Pure H3 Geometric Graph Construction & Batch Training Engine

**What to build:** Implement H3 geometric graph edge extraction (`build_h3_geometric_graph`) and the complete multi-epoch training pipeline (`train_gat_autoencoder`) in `src/phys_living_index/models/`.

**Status:** done

- [x] Pure H3 geometric adjacency graph edges built via `build_h3_geometric_graph` with no border pruning.
- [x] Multi-epoch `train_gat_autoencoder` minimizing dual MSE + link structure BCE regularization.
- [x] Unit tested with convergence assertions.
