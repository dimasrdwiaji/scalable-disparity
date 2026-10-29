# ADR 0001: Unsupervised Graph Attention Autoencoder on Geometric H3 Adjacency for Spatial Disparity Mapping

* **Status**: Accepted (Amended October 2026)
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
   When an affluent enclave and an informal kampung share an H3 boundary, their feature vector exhibits a step-function jump. The decoder fails to reconstruct this abrupt discontinuity, causing the reconstruction error ($\|X - \hat{X}\|^2$) to spike precisely along the segregation wall.
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

---

## Amendment (October 2026): 10-Dimensional Feature Expansion & Global Standards

1. **Feature Vector Expansion from 6D to 10D**:
   To capture the multidimensional nature of living standard disparity without collinear redundancy:
   - Added Built-up Roof Density ($\text{NDBI}$) to differentiate informal corrugated metal/asbestos roof texture from planned concrete roofing.
   - Added Bare Soil & Unpaved Infrastructure ($\text{BSI}$) to measure missing civic street paving in peri-urban zones.
   - Added Surface Water & Flood Vulnerability ($\text{MNDWI}$) to capture open wastewater drainage and low-elevation flood accumulation.
   - Added Multi-Pollutant Air Purity ($\text{AQI}_{\text{inv}}$) using official European/US AQI regulatory standards, supplementing fine particulate exposure ($\text{PM}_{2.5}$).
2. **Preservation of Authentic Units in Ingestion**:
   Raw raster and vector data in `ingest_context.py` remain in their canonical scientific units (spectral indices in $[-1.0, 1.0]$, LST in Kelvin, pollutants in $\mu\text{g/m}^3$ and AQI points). Scaling to $[0, 1]$ occurs exclusively in `build_features.py` during Stage 3.
3. **Global Floor-Count Derivation**:
   Building floor heights are grounded in international benchmarks (**EC JRC GHSL**; Biljecki & Chow, 2022) with $3.0\text{ m}$ for residential and $3.6\text{ m}$ for commercial structures, ensuring international portability.


---

## Amendment 2 (October 2026): Post-Peer-Review Hardening — Error Decomposition & Ablation

1. **Attributed Reconstruction Error Decomposition (DOMINANT Framework)**:
   To prevent unpopulated ecological and industrial boundaries (e.g., mangroves, golf courses, airport perimeters) from falsely registering as social inequality, total attribute reconstruction loss is decomposed additively into Socioeconomic Deprivation Friction ($\text{Friction}_{\text{socio}}$: living space, walking amenities, night radiance, bare soil) and Biophysical Contrast ($\text{Friction}_{\text{bio}}$: greenness, water, land surface temperature). True segregation boundaries require $\text{Friction}_{\text{socio}} \ge P_{85}$ across populated residential cells (`WorldPop > 0`).
2. **Latent Bottleneck Ablation ($d \in \{2, 3, 4, 8\}$)**:
   While $d=2$ is retained for direct, non-distorted Cartesian visualization and HDBSCAN clustering, the model architecture is benchmarked against higher latent capacities ($d \in \{3, 4, 8\}$) to evaluate reconstruction fidelity and prove the bottleneck does not induce catastrophic oversmoothing.
3. **Robust Denominator Winsorization**:
   To prevent high-density commercial corridors with small census population counts from creating explosive outliers in $R_{\text{space}}$, 99th percentile ($P_{99}$) winsorization is enforced prior to universal Min-Max normalization.
4. **Benchmarking Against Linear Spatial Autocorrelation**:
   The non-linear GAT self-attention edge friction ($1 - \alpha_{ij}$) is formally benchmarked against Bivariate Local Moran's $I$ (LISA) to demonstrate the necessity of deep geometric learning over isotropic linear spatial lags.
