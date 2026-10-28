# ADR 0001: Unsupervised Graph Attention Autoencoder on Geometric H3 Adjacency for Spatial Disparity Mapping

* **Status**: Accepted
* **Date**: October 2026
* **Deciders**: Dimas RD

---

## Context and Problem Statement

Measuring socio-spatial segregation and living standard disparity at the intra-metropolitan scale is bottlenecked by:
1. Administrative aggregation (BPS municipal-level Gini statistics mask micro-scale inequality).
2. The lack of ground-truth survey labels at sub-kilometer resolution (surveys like SUSENAS are sparse and anonymized with jitter).
3. The relative comparison trap of existing models (e.g., Meta's Relative Wealth Index relies on within-country relative z-scores).

We require an unsupervised machine learning architecture that:
- Does not depend on ground-truth training labels.
- Preserves continuous spatial topology.
- Detects sharp micro-segregation boundaries (such as 3-meter concrete walls between master-planned estates and informal kampungs).

## Considered Options

1. **Supervised Regression / CNNs on Satellite Imagery** (e.g., Jean et al. 2016, Chi et al. 2022).
2. **Network-Pruned Spatial GNN**: Pruning H3 graph edges that lack road crossings before message passing.
3. **Graph Attention Autoencoder (GAT-AE) with Pure Geometric H3 Adjacency & Reconstruction Friction** (Selected).

## Decision Outcome

Chosen option: **Option 3: GAT-AE on Pure Geometric H3 Adjacency**.

### Rationale:
1. **Reversing the GNN Over-Smoothing Dilemma**:
   Standard Graph Neural Networks smooth representations across neighbors. By retaining *pure geometric H3 adjacency* across physical boundaries (walls, rivers) and enforcing a strict bottleneck ($d=2$), the autoencoder is forced to learn a low-dimensional manifold expecting spatial continuity.
2. **Reconstruction Loss as Segregation Friction**:
   When an affluent enclave and an informal kampung share an H3 boundary, their 6-dimensional feature vector exhibits a step-function jump. The decoder fails to reconstruct this abrupt discontinuity, causing the reconstruction error ($\|X - \hat{X}\|^2$) to spike precisely along the segregation wall.
3. **Dual Boundary Corroboration**:
   Extracting the GAT layer's learned attention coefficients ($\alpha_{ij}$) provides edge-level corroboration: where $\alpha_{ij} \to 0$, the network explicitly detects dissimilar neighbors.

## Consequences

* **Positive**:
  - Unsupervised: Zero dependence on survey labels for training.
  - Objective: Friction boundaries are mathematically derived from multi-dimensional physical features.
  - Portability: Applicable to any city worldwide using standard open data (Overture Maps, Google Open Buildings, Sentinel, VIIRS).
* **Negative**:
  - Requires careful normalization (Universal Min-Max to $[0, 1]$) to prevent high-magnitude features from dominating the reconstruction error.
  - Requires bottleneck latent space ($d \le 2$) to prevent trivial identity mapping shortcuts.
