# 03: Latent Bottleneck Ablation Suite (REV-6)

**What to build:** Implement parameterized bottleneck ablation testing $d \in \{2, 3, 4, 8\}$ across reconstruction MSE, topological BCE, and HDBSCAN cluster silhouette score in `src/phys_living_index/models/ablation.py`.

**Status:** done

- [x] Multi-dimensional ablation function `run_bottleneck_ablation` testing candidate latent sizes.
- [x] Evaluates MSE reconstruction, structure BCE, and HDBSCAN cluster silhouette scores.
- [x] Unit tested across candidate latent dimensions.
