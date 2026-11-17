# ADR 0005: Pure Physical Urban Mask, Local Urban Ring Thermal Baseline, Empirical Composite Test, and Benchmarked GAT-AE

* **Status**: Accepted (2026-11-16)
* **Amends / Supersedes**: Supersedes the `WorldPop > 0` / `GHS-POP` mask and `10`-channel `Friction_socio` / `Friction_bio` split in [ADR 0001](0001-h3-gat-ae-unsupervised-disparity.md), and supersedes the rural vegetated $\Delta\text{LST}$ background and retired proxy channels in [ADR 0003](0003-universal-frozen-benchmarks-and-channel-weighting.md).

## Context and Decision

Empirical proxy vetting and Jabodetabek pilot screens showed that population-grid ratios (`R_space`), nightlights (`VIIRS`), coarse air/thermal layers, and `Overture`/`OSM` service-proximity indices conflate built density or invert across central *kampungs*. In addition, subtracting a rural vegetated or single citywide thermal baseline leaves sea-breeze and terrain gradients entangled with neighborhood heat stress.

We adopt four structural rules for Stage 3–5 implementation and Section 4 methodology:

1. **Pure physical urban mask**: Cells enter the intra-urban model and inequality suite strictly via `GHS-SMOD` urban settlement classes (`{21, 22, 23, 30}`) plus $\ge 1$ residential building remaining after removing OSM non-residential zones—with no `GHS-POP` or `WorldPop` cutoff.
2. **Local `k = 5` ($\approx 2.6\text{ km}$) urban-ring thermal baseline**: $\Delta\text{LST}_i$ is computed as cell LST minus the median multi-year `100 m` Landsat 8/9 Tier-1 LST of neighboring urban-masked cells within a `k = 5` H3 ring (`Chakraborty2019a` citywide urban-cluster median retained strictly as a sensitivity check).
3. **Individual screening + empirical non-compensatory test**: Candidates (`s2_res_glcm_*`, conditional `ghs_res_share`) must clear separation, low coverage correlation ($|\rho| < 0.35$), and blocked-fold consistency before promotion. Arithmetic domain averaging ($M_{z_i}$) and positive-offset Mazziotta–Pareto penalty aggregation ($\text{MPI}^+$) are tested empirically head-to-head rather than locking in $\text{MPI}^+$ prior to evidence; hexagonal `Gini`, `Lorenz`, and `Spatial Palma Ratio` run unweighted over equal-area urban cells (`building count` optional robustness check).
4. **`GAT-AE` (`D -> d=2`) benchmarked over blocked spatial folds**: Feed all `D = 4–6` individual vetted variables directly into `SpatialGATAutoencoder` (`latent_dim = 2`, never `d = D`; `d = 3` ablation only if $D \ge 5$), decompose output errors post-hoc into Built-Form Friction vs. Micro-Environmental Friction, and test boundary detection strictly against `Local Moran's I` (LISA) and pairwise Euclidean feature differences on spatially blocked folds.

## Consequences

* Eliminates all population-grid and accessibility leakage from urban masking, thermal baselines, inequality weights, and boundary detection.
* Forces `GAT-AE` to justify its complexity empirically against linear spatial statistics rather than assuming improvement by construction.
