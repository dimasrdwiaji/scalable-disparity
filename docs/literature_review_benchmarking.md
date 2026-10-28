# Literature Review & Benchmarking Analysis: Scalable GeoAI for Micro-Scale Living Standards & Spatial Segregation

**Author:** Dimas RD  
**Framework:** Scalable GeoAI for Physical Living Standards (PLSI) & Spatial Segregation  
**Target Manuscript:** EarthArXiv / *Computers, Environment and Urban Systems (CEUS)*  
**Date:** October 2026  

---

## Executive Summary

This document conducts a rigorous comparative literature review benchmarking our proposed GeoAI framework against existing scientific literature across four major paradigms:
1. **Remote Sensing & ML Poverty/Wealth Mapping** (Jean et al., *Science* 2016; Chi et al., *PNAS* 2022 / Meta RWI; Burke et al., *Science* 2021).
2. **Urban Morphology, Slum Detection, and Building Stock Analysis** (UN-Habitat; Kuffer et al., *CEUS* 2016, 2020; Biljecki et al., 2023, 2024; Google Open Buildings v3).
3. **Urban Accessibility, 15-Minute Cities, & Open Map Data** (Weiss et al., *Nature* 2018, *Nature Medicine* 2020; Handy & Niemeier 1997; Overture Maps Foundation 2023–2025).
4. **Graph Neural Networks (GNNs) & Spatial Segregation Analytics** (Kipf & Welling 2016; Zhang et al., *CEUS* 2022; Reardon & O'Sullivan 2004; Massey & Denton 1988).

We identify **four major critical gaps in current literature**, demonstrate how our research fills them with high-novelty contributions, and outline **concrete methodological enhancements** adopted from recent cutting-edge publications.

---

## 1. Comparative Analysis Against Existing Paradigms

| Dimension | Existing Literature Approach | Limitations of Existing Work | Our Proposed GeoAI Framework |
| :--- | :--- | :--- | :--- |
| **Socioeconomic Wealth Mapping** | **Supervised ML on Satellite & Alt-Data**<br>• Jean et al. (2016, *Science*), Yeh et al. (2020, *Nat. Commun.*): CNNs on daytime imagery pre-trained on nighttime lights.<br>• Chi et al. (2022, *PNAS*) / Meta RWI: Gradient boosted trees combining satellite + Facebook de-identified connectivity data. | • **Relative z-score trap**: Trained on DHS asset indices; measures relative rank *within* a country, preventing absolute cross-border physical comparisons.<br>• **Coarse spatial resolution**: 2.4 km grid (Meta RWI) or survey cluster centroids (jittered by 2–5 km for privacy), completely blinding models to micro-segregation.<br>• **Proprietary black-box inputs**: Telecommunication and Facebook social graphs cannot be audited or verified by local planning agencies (*Bappeda*). | • **Unsupervised & Physics-Grounded**: Zero survey supervision. Direct calibration against international physical thresholds (UN-Habitat 9 m² shelter baseline, WHO air quality, 15-min walk thresholds).<br>• **Micro-Scale (~460 m / 0.74 km²)**: Continuous Uber H3 Res-8 hexagons across the whole metropolitan extent.<br>• **100% Open & Auditable**: Open Buildings, Overture Maps, Sentinel-2, VIIRS. |
| **Slum & Deprivation Detection** | **Binary / Multi-class Remote Sensing**<br>• Kuffer et al. (2016, *CEUS*; 2020, *Remote Sens.*): Texture metrics (GLCM) and deep CNNs classifying "slum vs. non-slum".<br>• GHSL (Pesaresi et al., JRC): Built-up surface and degree of urbanization grids. | • **Binary classification stigma**: Labels entire neighborhoods as "slum", ignoring the nuanced spectrum of deprivation in dualistic cities.<br>• **Prohibitive VHR image costs**: Relies on commercial imagery (WorldView, Pleiades at $15–$25/km²), making metropolitan-scale tracking cost-prohibitive. | • **Continuous Multi-Dimensional Index**: Measures a continuous 0.0–1.0 spectrum of physical adequacy without stigmatizing binary labels.<br>• **Global Open AI Geometry**: Uses free Google Open Buildings v3 (2.5D heights) intersected with JRC GHS-BUILT-C residential masks. |
| **Urban Accessibility & 15-Minute Cities** | **Global Friction Surfaces & OSM Networks**<br>• Weiss et al. (2018, *Nature*; 2020, *Nat. Med.*): Global travel time to cities and healthcare at 1 km.<br>• Logan et al. (2022): Evaluating 15-minute city access in US/European cities using OpenStreetMap. | • **VGI completeness bias in Global South**: In Indonesia, >95% of OSM buildings are tagged `building=yes`; public vs. private facility tags are sparse and unverified.<br>• **Euclidean buffer fallacies**: Studies often use straight-line radii, missing physical barriers and gated perimeter walls. | • **Overture Maps Foundation (Places & Base)**: Leverages deduplicated commercial + open POIs, standardizing categories across healthcare, education, retail, and designated parks.<br>• **Network Isochrones**: 15-minute walking catchments over true pedestrian network lines, accounting for physical perimeter walls. |
| **Socio-Spatial Segregation Analysis** | **Areal Aggregation Indices**<br>• Massey & Denton (1988), Reardon & O'Sullivan (2004): Spatial Dissimilarity and Spatial Information Theory based on census demographic tables.<br>• Zhang et al. (2022, *CEUS*): GNNs for urban functional zone embeddings. | • **Administrative boundary dependence**: Suffers from the Modifiable Areal Unit Problem (MAUP) and boundary gerrymandering.<br>• **Oversmoothing in GNNs**: Standard GNN message-passing averages node features across neighbors, actively blurring sharp inequality boundaries. | • **GAT-AE Reconstruction Friction**: Retaining geometric adjacency forces the Graph Attention Autoencoder to expect continuity. **Reconstruction error ($\|X - \hat{X}\|^2$) spikes precisely at segregation seams** (e.g., gated wall vs. kampung).<br>• **HDBSCAN Latent Discovery**: Unsupervised discovery of neighborhood archetypes without arbitrary $K$. |

---

## 2. In-Depth Literature Benchmarking

### 2.1 The Remote Sensing Wealth Prediction Paradigm
Pioneering work by **Jean et al. (2016)** (*Science*) established the benchmark for estimating consumption expenditure and wealth from space by transfer-learning CNNs from nighttime lights (VIIRS) to daytime optical imagery. This was expanded globally by **Chi et al. (2022)** (*PNAS*) to release Meta's Relative Wealth Index (RWI) across 135 low- and middle-income countries.

#### Why our research has a distinct contribution:
1. **The Relative vs. Absolute Paradox**: RWI calculates an asset wealth score relative to the national average. Thus, a value of $+1.5$ in rural Malawi represents a radically different physical reality than $+1.5$ in suburban Java. Our framework formulates the **Physical Living Standard Index (PLSI)** grounded in immutable physical benchmarks (floor space in m², walking minutes, thermal Kelvin, $\mu\text{g/m}^3$), enabling true cross-border and rural-urban parity.
2. **The "Alt-Data" Sovereign Trap**: Recent evaluations of RWI in Indonesia (Frontiers / PubMed Central, 2023) highlighted that while RWI correlates with census asset indicators, local planning agencies (*Bappeda*) cannot audit the underlying proprietary mobile connectivity metrics from Meta. Our framework uses exclusively transparent, verifiable public scientific sensors and open geometries.

### 2.2 Built-Environment Morphology & Slum Deprivation
UN-Habitat defines housing deprivation based on five shelter indicators: lack of durable housing, overcrowding (insufficient living area), lack of safe water, lack of sanitation, and insecure tenure. In the geospatial literature, **Kuffer et al. (2016, 2020)** pioneered the automated identification of deprived urban areas using spatial textures and morphological irregularity. Concurrently, **Biljecki et al. (2023, 2024)** demonstrated the utility of large-scale open building footprints (Google Open Buildings, Microsoft) for estimating 3D building volume and density indicators.

#### Why our research has a distinct contribution:
1. **Solving the Density-Wealth Confounding Problem**: Prior studies frequently misclassified high-density urban kampungs as "dense formal cores" or vice versa because raw building footprint density is ambiguous (a Manhattan high-rise and a Kowloon tenement are both tall and dense). By coupling **Google Open Buildings 2.5D heights** with **WorldPop gridded population** and masking by the **EC JRC GHS-BUILT-C** functional residential layer, we isolate **true residential living floor area per person ($R_{\text{space}}$)** and benchmark it directly against the UN-Habitat $9.0\text{ m}^2$ standard.
2. **Continuous Surface vs. Stigmatizing Binary Flags**: Instead of labeling an area as a binary "slum", our multidimensional index treats living standards as a continuous multivariate spectrum, capturing areas that may have adequate housing space but extreme amenity deprivation.

### 2.3 OpenStreetMap vs. Overture Maps in Global South Accessibility
Accessibility literature has rapidly evolved from classic gravity models (Handy & Niemeier, 1997; Geurs & van Wee, 2004) to threshold-based cumulative opportunities (15-minute city metrics; Hosford et al., 2022). However, nearly all published studies in the Global South rely on OpenStreetMap.

#### Why our research has a distinct contribution:
1. **Overcoming VGI Bias**: In Southeast Asia, OSM building attributes are $>95\%$ unclassified (`building=yes`), and volunteer POIs suffer from severe spatial bias toward affluent, digitalized commercial districts.
2. **First-Mover Deployment of Overture Maps Foundation**: Overture Maps (established by Linux Foundation, Amazon, Meta, Microsoft, and TomTom) fuses and deduplicates global POI datasets into a clean, hierarchical taxonomy (GERS). Utilizing Overture Places and Base themes represents a significant data-engineering advancement over fragile OSM volunteer tag parsing.

### 2.4 Graph Neural Networks & Spatial Segregation
In urban computing, Graph Convolutional Networks (GCNs) and Graph Attention Networks (GATs) (Kipf & Welling 2016; Veličković et al. 2018) are predominantly deployed for supervised tasks: predicting traffic speeds, classifying urban functional zones (Zhang et al., *CEUS* 2022), or predicting house prices.

#### Our Primary Methodological Novelty:
* **The "Reconstruction Loss as Segregation Friction" Mechanism**: Standard GNN literature views spatial over-smoothing as a problem to be mitigated. In our framework, **we turn spatial message passing into a feature**:
  * We construct the graph $G = (V, E)$ using pure geometric H3 adjacency.
  * Message passing over $E$ enforces local spatial continuity expectations in the latent representation $Z$.
  * Where a physical segregation barrier exists (e.g., a gated community wall dividing a kampung from luxury villas), the feature values of adjacent nodes exhibit a step-function jump.
  * Because the autoencoder bottleneck ($d=2$) prevents memorization, the decoder **fails to reconstruct this sharp boundary**.
  * Consequently, the reconstruction error $\|x_i - \hat{x}_i\|^2$ **automatically spikes along segregation boundaries**, providing an unsupervised, mathematically derived map of spatial severance!
* To our knowledge, using GAT autoencoder reconstruction error on an H3 grid as an objective indicator of socio-spatial segregation boundaries has **never been published in urban remote sensing or spatial AI literature**.

---

## 3. Actionable Enhancements Adopted from Literature

### Enhancement 1: Extract GAT Edge Attention Coefficients ($\alpha_{ij}$) as Direct Boundary Friction
* **Source**: Veličković et al. (2018) *Graph Attention Networks*; CEUS spatial GNN literature.
* **Mechanism**: During GAT encoding, the attention mechanism calculates an explicit weight $\alpha_{ij} \in [0, 1]$ representing how much node $i$ attends to neighbor $j$:
  $$\alpha_{ij} = \frac{\exp\left(\text{LeakyReLU}\left(\mathbf{a}^T [\mathbf{W}h_i \,\|\, \mathbf{W}h_j]\right)\right)}{\sum_{k \in \mathcal{N}_i} \exp\left(\text{LeakyReLU}\left(\mathbf{a}^T [\mathbf{W}h_i \,\|\, \mathbf{W}h_k]\right)\right)}$$
* **Integration**: Where $\alpha_{ij} \to 0$, the neural network has explicitly decided that neighbor $j$ is dissimilar and should be ignored. We extract $1 - \alpha_{ij}$ as an explicit **Edge Boundary Friction** layer, corroborating the node-level reconstruction loss.

### Enhancement 2: Add the Spatial Palma Ratio to Disparity Metrics
* **Source**: Palma (2011); Cobham et al. (2016); standard urban inequality literature.
* **Mechanism**: While the Gini coefficient is sensitive to middle-class distribution shifts, the Palma Ratio directly contrasts the extremes:
  $$\text{Spatial Palma Ratio} = \frac{\text{Sum of PLSI in Top 10\% Population}}{\text{Sum of PLSI in Bottom 40\% Population}}$$
* **Integration**: Added to `src/analysis/disparity_metrics.py` alongside Gini for reporting to policy audiences (*World Bank, UN*).

### Enhancement 3: Quality & Confidence Filtering on Google Open Buildings
* **Source**: Sirko et al. (2021) *Continental-scale building detection from high-resolution satellite imagery*; Biljecki et al. (2023).
* **Mechanism**: Google Open Buildings assigns each polygon a detection confidence score between $0.5$ and $1.0$.
* **Integration**: In `src/data/ingest_buildings.py`, filter out building polygons with confidence $< 0.65$ to eliminate false-positive satellite artifacts.

### Enhancement 4: Spatial Autocorrelation & Local Moran's $I$ Baseline Comparison
* **Source**: Anselin (1995) *Local Indicators of Spatial Association (LISA)*.
* **Mechanism**: Compute bivariate Local Moran's $I$ (High-Low and Low-High spatial outliers) as a formal quantitative baseline.
* **Integration**: Proving that the GAT-AE captures non-linear multidimensional barriers that linear LISA misses will be a major highlight of the preprint.

### Enhancement 5: Clear Articulation of the Wealth-vs-Income Decouple
* **Source**: Frontiers in Big Data (2023) / NIH study on SUSENAS & RWI in Indonesia.
* **Mechanism**: Satellite-derived indices capture long-term structural physical capital, achieving higher concordance with asset registries (Meta RWI, DHS) than with volatile monthly cash expenditures (SUSENAS consumption).
* **Integration**: Grounded in the manuscript discussion.

---
*End of Literature Review & Benchmarking Analysis.*
