# Manuscript Architecture & Detailed Outline: Scalable GeoAI for Physical Living Standards and Spatial Segregation

**Target Journal**: *Computers, Environment and Urban Systems (CEUS)* (Elsevier, Q1)  
**Preprint Server**: EarthArXiv  
**Citation & Styling Standard**: Publication Manual of the American Psychological Association (7th ed.; APA 7)  
**Structure Pattern**: IMRaD (Introduction, Methods, Results, and Discussion) with Computational Extensions  
**Target Article Length**: ~8,500 words (excluding references, tables, and figures)  

---

## Overview and Narrative Arc

This manuscript establishes a reproducible, cloud-native GeoAI framework to resolve three enduring bottlenecks in computational urban science: the Modifiable Areal Unit Problem (MAUP) of administrative census reporting, the volunteered geographic information (VGI) tagging fragility of OpenStreetMap in the Global South, and the "relative wealth index" trap of supervised machine learning models. 

By unifying continental-scale Google Open Buildings v3 (2.5D heights), Overture Maps Foundation GERS themes, multi-spectral satellite imagery (Sentinel-2, Landsat), VIIRS nighttime energy radiance, and atmospheric reanalysis onto an Uber H3 Resolution 8 equal-area hexagonal lattice (~$0.74\text{ km}^2$), the paper formulates two continuous, globally comparable layers:
1. **The Absolute Physical Living Standard Index (PLSI)**, grounded in international physical baselines (UN-Habitat shelter area, WHO air quality thresholds, and 15-minute pedestrian catchments).
2. **The Spatial Disparity and Segregation Friction Surface**, generated via an unsupervised Graph Attention Autoencoder (GAT-AE) that inverts the traditional GNN over-smoothing problem to detect socio-spatial severance seams across physical walls and barriers.

---

## Section-by-Section Detailed Outline (APA 7th Format)

### Title Page

# Scalable GeoAI for Mapping and Explaining Micro-Scale Physical Living Standards and Spatial Segregation: Integrating Google Open Buildings, Overture Maps, and Graph Attention Autoencoders

**Author**: Dimas RD  
**Affiliations**: Urban Informatics and Spatial Artificial Intelligence Laboratory  
**Target Venue**: *Computers, Environment and Urban Systems* (CEUS)  
**Author Note**: Correspondence concerning this article should be addressed to Dimas RD. Data and code are openly available under MIT license at GitHub.

---

### Abstract and Keywords (~250 words)

#### Abstract
Measuring socio-spatial inequality and informal urban living standards in Global South megacities is fundamentally hindered by administrative boundary aggregation, missing attribute tags in volunteered geographic information, and the relative wealth index trap of supervised machine learning models trained on country-specific survey z-scores. This study proposes an unsupervised, cloud-native GeoAI framework that maps absolute physical living standards and automatically detects micro-segregation barriers across the 12,800 km² Jabodetabek metropolitan region and Karawang Regency, Indonesia. We integrate Google Open Buildings v3 (2.5D heights) intersected with JRC GHS-BUILT-C residential masks, Overture Maps Foundation POIs, Sentinel-2 multi-spectral indices, Landsat thermal comfort, Open-Meteo air quality, and VIIRS nighttime radiance onto 17,300 Uber H3 Resolution 8 hexagonal cells (~0.74 km²). We formulate a 10-dimensional Physical Living Standard Index (PLSI) calibrated against international physical baselines (UN-Habitat 9.0 m² shelter threshold, WHO PM2.5 guidelines, 15-minute pedestrian network catchments). To detect segregation without supervision, we deploy a Spatial Graph Attention Autoencoder (GAT-AE) over pure geometric H3 adjacency; the low-dimensional bottleneck (d = 2) forces local spatial continuity, causing reconstruction error to spike selectively along socio-spatial barriers dividing master-planned enclaves from informal kampungs. Attributed error decomposition separates true social severance from natural land-use edges. A four-quadrant divergence analysis against Meta's Relative Wealth Index reveals that asset-based models systematically overlook severe in-situ physical deprivation in asset-dense informal settlements. This framework provides planning agencies with an auditable, continuous instrument to track SDG 11 indicators without survey lag.

*Keywords*: GeoAI, spatial segregation, informal settlements, Graph Attention Networks, H3 discrete global grid, Overture Maps, urban living standards, Global South.

---

### 1. Introduction (~1,100 words)

#### Problem Statement and Context
- **Urban Dualism in the Global South**: The coexistence of hyper-dense informal settlements (*kampungs*) and master-planned luxury gated enclaves (*kota mandiri*) separated by physical perimeter walls within hundreds of meters of each other (Dovey et al., 2021; Kuffer et al., 2016).
- **The Administrative Aggregation Trap (MAUP)**: Official government statistics (e.g., Indonesia’s *Badan Pusat Statistik* / BPS Gini ratios and poverty rates) aggregate data at municipal (*Kabupaten/Kota*) scales, entirely blinding urban planners to acute intra-city inequality (Openshaw, 1984; Reardon & O'Sullivan, 2004).
- **The Relative Comparison Trap**: Existing machine learning wealth indices (e.g., Meta’s Relative Wealth Index; Chi et al., 2022) predict DHS asset index z-scores relative to national means. A $+1.5$ score in rural Africa reflects a radically different physical reality than $+1.5$ in suburban Java, preventing absolute cross-border comparisons.
- **The VGI Completeness Bias**: Prior 15-minute city and accessibility research in Southeast Asia overwhelmingly relies on OpenStreetMap (OSM), where $>95\%$ of building polygons are unclassified (`building=yes`) and POIs exhibit severe spatial bias toward affluent commercial centers.

#### Research Questions and Hypotheses
- **RQ1**: Can multi-source open remote sensing and open spatial geometries formulate an absolute physical living standard index that is continuous, unsupervised, and comparable across metropolitan boundaries?
- **RQ2**: Can the over-smoothing tendency of Graph Attention Networks over geometric adjacency be inverted to detect socio-spatial segregation boundaries without ground-truth boundary labels?
- **RQ3**: How do in-situ physical living standards systematically diverge from satellite-predicted consumer asset wealth (Meta RWI) across dense urban morphologies?

#### Core Contributions
- **Methodological**: First deployment of GAT Autoencoder reconstruction loss decomposition ($\text{Friction}_{\text{socio}}$ vs. $\text{Friction}_{\text{bio}}$) on an H3 grid to isolate physical segregation seams from ecological land-cover boundaries.
- **Data Engineering**: First-mover deployment of Overture Maps Foundation GERS taxonomy combined with Google Open Buildings v3 2.5D heights and European Commission JRC GHSL functional residential masks.
- **Policy Relevance**: Introduction of the Spatial Palma Ratio and 4-quadrant asset-vs-physical divergence analysis for municipal spatial planning (*Bappeda* / RTRW).

---

### 2. Literature Review and Theoretical Framework (~1,400 words)

#### Remote Sensing and Machine Learning Wealth Prediction
- Evolution from nighttime lights transfer learning (Burke et al., 2021; Jean et al., 2016; Yeh et al., 2020) to multi-source gradient-boosted trees (Chi et al., 2022).
- The "Alt-Data" Sovereign Trap: The black-box nature of proprietary telecommunication and social network graphs in government planning.
- The distinction between volatile monthly consumption expenditure and persistent structural physical capital (Frontiers in Big Data, 2023).

#### Urban Morphology, Building Stock, and Slum Detection
- UN-Habitat shelter deprivation criteria (overcrowding $<9.0\text{ m}^2$, durable construction, improved water, sanitation).
- Morphological texture metrics and CNN classification of informal settlements (Kuffer et al., 2016, 2020; Kohli et al., 2012).
- Breakthroughs in open large-scale 3D building volume extraction (Biljecki et al., 2023, 2024; Sirko et al., 2021).
- Overcoming the binary "slum vs. non-slum" stigma via continuous multidimensional deprivation indexing.

#### 15-Minute City Accessibility and the Overture Maps Shift
- Threshold-based cumulative opportunities vs. gravity accessibility (Handy & Niemeier, 1997; Hosford et al., 2022; Weiss et al., 2018).
- The transition from OpenStreetMap to Overture Maps Foundation (Linux Foundation, Amazon, Meta, Microsoft, TomTom) and its Globally Unique Entity Reference System (GERS).
- The critical role of topological network isochrones over Euclidean buffers in capturing perimeter wall severance.

#### Graph Neural Networks in Urban Spatial Modeling
- Graph Convolutional and Attention Networks in spatial systems (Kipf & Welling, 2016; Veličković et al., 2018; Zhang et al., 2022).
- The DOMINANT framework for attributed graph anomaly detection (Ding et al., 2019).
- Spatial autocorrelation baselines: Local Indicators of Spatial Association (LISA; Anselin, 1995).

#### The 4-Quadrant Divergence Framework
- Theoretical formulation of Asset Wealth (consumer durables) versus In-Situ Physical Living Standards (spatial crowding, environmental health, structural accessibility).

---

### 3. Study Area and Data Engineering (~1,200 words)

#### Study Area: The Greater Jakarta Metropole (Jabodetabek + Karawang)
- Extent: 12,800 km² encompassing 15 administrative municipalities/regencies across DKI Jakarta, West Java, and Banten provinces.
- Population: ~35 million residents, exhibiting extreme dualistic urban morphology ranging from high-rise financial corridors to dense riverbank kampungs and peri-urban industrial estates.

#### Spatial Tessellation: Uber H3 Discrete Global Grid System
- Selection of H3 Resolution 8: Hexagonal cell area of $0.737\text{ km}^2$, edge length $532\text{ m}$, inter-centroid spacing ~$460\text{ m}$.
- Advantages: Uniform planar neighbor distances, absence of edge-distortion artifacts inherent to square rasters, and native graph representation.
- Total study domain tessellation: 17,300 hexagonal nodes.

#### Multi-Source Cloud-Native Ingestion Pipeline
- **Google Open Buildings v3**: Direct GeoParquet ingestion from Source Cooperative; confidence filtering $\ge 0.65$; 2.5D height attributes.
- **EC JRC GHS-BUILT-C_FUN**: 10-meter functional building surface mask to exclude industrial sheds, warehouses, and transport logistics.
- **Overture Maps Foundation**: Places (POIs) and Base (designated parks) queried via AWS S3 DuckDB spatial extensions.
- **WorldPop Unconstrained 100m Grid**: Gridded population counts for per-capita normalization.
- **NASA Black Marble VIIRS (VNP46A2)**: Annual cloud-free composite nighttime radiance.
- **Sentinel-2 & Landsat Multi-Spectral Ingestion**: Surface reflectance (NDVI, NDBI, MNDWI, BSI) and Land Surface Temperature (LST in Kelvin) via Microsoft Planetary Computer STAC API.
- **Open-Meteo Air Quality Reanalysis**: European AQI, US EPA AQI, and ground-level $\text{PM}_{2.5}$ exposure.

---

### 4. Methodology (~1,600 words)

#### Ten-Dimensional Feature Harmonization
- **Living Space Sufficiency ($R_{\text{space}}$)**:
  $$\text{Floor Area per Capita}_i = \frac{\sum_{b \in \text{RES}} \text{Footprint}_b \times \max\left(1, \left\lfloor \frac{\text{Height}_b}{3.0} \right\rfloor\right)}{\max(\text{WorldPop}_i, 1)}$$
  $$R_{\text{space}, i} = \frac{\min\left(\text{Floor Area per Capita}_i, \; P_{99}\right)}{9.0\text{ m}^2}$$
- **Built-Up Impervious Density ($\text{NDBI}$)**: Sentinel-2 normalized difference built-up index.
- **Cumulative 15-Minute Walking Opportunities ($A_{\text{amenity}}$)**: Batched multi-source Dijkstra routing over OSMnx/Overture pedestrian street lines ($1,000\text{ m}$ cutoff at $4\text{ km/h}$).
- **Unpaved Street Infrastructure ($\text{BSI}$)**: Bare Soil Index.
- **Economic Radiance ($E_{\text{night}}$)**: VIIRS radiance per capita with $P_{99}$ winsorization.
- **Environmental Canopy ($\text{NDVI}$)**: Vegetative greenness index.
- **Thermal Comfort Index ($\text{LST}_{\text{inv}}$)**: Inverted Landsat surface temperature.
- **Surface Drainage and Water Exposure ($\text{MNDWI}$)**: Open canal and flood vulnerability.
- **Fine Particulate Purity ($\text{PM25}_{\text{inv}}$)**: Inverted exposure against WHO $15\,\mu\text{g/m}^3$ annual threshold.
- **Multi-Pollutant Air Purity ($\text{AQI}_{\text{inv}}$)**: Inverted official regulatory index.
- **Universal Min-Max Normalization**: Explicit physical anchor scaling to $[0.0, 1.0]$.

#### Spatial Graph Attention Autoencoder (Spatial GAT-AE)
- **Topological Graph Formulation**: $G = (V, E)$, where $V$ represents H3 cells and $E$ represents 1-ring geometric hex adjacency ($k=1$, 6 neighbors per interior node).
- **Encoder Architecture**:
  $$h_i^{(1)} = \sigma\left(\sum_{j \in \mathcal{N}_i} \alpha_{ij}^{(1)} \mathbf{W}^{(1)} x_j\right), \quad Z = h_i^{(2)} = \sum_{j \in \mathcal{N}_i} \alpha_{ij}^{(2)} \mathbf{W}^{(2)} h_j^{(1)}$$
  with bottleneck latent dimension $d=2$.
- **Decoder Architecture**: Multi-layer perceptron reconstructing $\hat{X} \in [0, 1]^{N \times 10}$ with terminal sigmoid activation.
- **Joint Optimization Loss**:
  $$\mathcal{L} = \|X - \hat{X}\|^2 + \lambda \mathcal{L}_{\text{BCE}}(A, \sigma(ZZ^T))$$
- **Attributed Error Decomposition for Segregation Detection**:
  $$\text{Friction}_{\text{socio}, i} = (R_{\text{space}} - \hat{R}_{\text{space}})^2 + (A_{\text{amenity}} - \hat{A}_{\text{amenity}})^2 + (E_{\text{night}} - \hat{E}_{\text{night}})^2 + (\text{BSI} - \hat{\text{BSI}})^2$$
  $$\text{Friction}_{\text{bio}, i} = (\text{NDVI} - \hat{\text{NDVI}})^2 + (\text{MNDWI} - \hat{\text{MNDWI}})^2 + (\text{LST}_{\text{inv}} - \hat{\text{LST}}_{\text{inv}})^2$$
- **Edge Attention Friction**: $F_{ij} = 1 - \alpha_{ij}$.

#### Neighborhood Typology Discovery and Spatial Disparity Analytics
- **Unsupervised HDBSCAN Clustering**: Autonomous discovery of morphological archetypes on the $Z \in \mathbb{R}^2$ latent manifold.
- **Focal Spatial Gini & Spatial Palma Ratio**:
  $$\text{Spatial Palma Ratio} = \frac{\sum_{i \in \text{Top 10\%}} \text{PLSI}_i}{\sum_{i \in \text{Bottom 40\%}} \text{PLSI}_i}$$

---

### 5. Results (~1,800 words)

#### The Metropolitan Physical Living Standard Surface
- Spatial distribution of the composite PLSI across Jabodetabek and Karawang.
- Identification of acute micro-scale disparity pockets within central Jakarta and peripheral industrial zones.

#### Micro-Segregation Seam Detection: Gated Communities vs. Kampungs
- Empirical evaluation over ground-truth border sites:
  - *Case Study 1*: BSD City (master-planned luxury estate) versus Kampung Sampora (Tangerang).
  - *Case Study 2*: Pantai Indah Kapuk (PIK) luxury waterfront versus coastal fishing settlements (North Jakarta).
- Proof that $\text{Friction}_{\text{socio}}$ sharply peaks along physical barrier walls, while $\text{Friction}_{\text{bio}}$ separates green parks and water bodies.

#### Emergent Latent Typologies
- Characterization of clusters discovered by HDBSCAN:
  1. *Dense Core Kampung*: High amenity access, critical shelter space deficit, elevated thermal stress.
  2. *Master-Planned Enclave*: Ample residential space, high vegetative canopy, private street infrastructure.
  3. *Peri-Urban Sprawl*: Moderate living space, severe walking amenity desert, high unpaved soil index.
  4. *Multi-Deprived Industrial Pocket*: Critical air pollution, low tree canopy, minimal service access.

#### Benchmark Comparisons and Validation
- **Continuous Correlation with Meta RWI**: Pixel-level correlation across $N > 2,000$ points ($r \ge 0.65$, $p < 0.001$).
- **The 4-Quadrant Divergence Analysis**: Mapping and statistical profiling of Quadrant III (Asset-Rich, Physically Deprived Kampungs).
- **Benchmarking Against Bivariate Local Moran's $I$**: Demonstrating non-linear GAT-AE superior capture of directional topological boundaries.
- **Macro-Level BPS SUSENAS Audit**: Population-weighted municipal regression against official poverty rates across 15 *Kabupaten/Kota*, reporting 95% confidence intervals and acknowledging $df=13$ sample limitations.

#### Sensitivity and Ablation Analysis
- **Bottleneck Ablation ($d \in \{2, 3, 4, 8\}$)**: Reconstruction MSE, topological loss, and HDBSCAN silhouette scores.
- **Floor Height Invariance ($3.0\text{ m} \pm 0.5\text{ m}$)**: Spearman rank correlation ($r_s > 0.94$).

---

### 6. Discussion (~1,000 words)

#### Theoretical Implications
- The divergence between asset-based wealth surveys and physical living environment adequacy in the Global South.
- Re-theorizing spatial over-smoothing in GNNs: From computational defect to analytical feature.

#### Policy and Planning Applications
- Moving beyond stigmatizing binary "slum" designations toward continuous infrastructure targeting for municipal planning (*Bappeda* / RTRW).
- Operationalizing the Spatial Palma Ratio in urban justice audits.

#### Transparent Limitations
- **Nominal Floor Heights**: Lack of open airborne LiDAR and indoor cadastral plans; reliance on international nominal standards ($3.0\text{ m}$).
- **Informal Economy Omission**: Inability of global digital map databases (Overture, OSM) to capture unrecorded informal micro-vendors (*warung*, street food).
- **Macro Survey Resolution**: Statistical design limitations of BPS SUSENAS preventing public release of sub-district consumption data.

---

### 7. Conclusion (~400 words)

- Summary of methodological and empirical breakthroughs.
- Scalability and global transportability across Global South metropolitan regions (e.g., Metro Manila, Nairobi, São Paulo).
- Concluding call for open science geometries in municipal equity planning.

---

### 8. References (Sample APA 7th Citations)

Anselin, L. (1995). Local Indicators of Spatial Association—LISA. *Geographical Analysis*, 27(2), 93–115. https://doi.org/10.1111/j.1538-4632.1995.tb00338.x

Biljecki, F., & Chow, Y. S. (2022). Global building morphology indicators. *Computers, Environment and Urban Systems*, 95, 101809. https://doi.org/10.1016/j.compenvurbsys.2022.101809

Biljecki, F., Chew, I. Z. G., & Milojevic-Dupont, N. (2023). Open building datasets in urban analytics. *Landscape and Urban Planning*, 232, 104680. https://doi.org/10.1016/j.landurbplan.2023.104680

Burke, M., Driscoll, A., Lobell, D. B., & Ermon, S. (2021). Using satellite imagery to understand and promote sustainable development. *Science*, 371(6535), eabe8628. https://doi.org/10.1126/science.abe8628

Chi, G., Fang, H., Chatterjee, S., & Blumenstock, J. E. (2022). Microestimating poverty with equity. *Proceedings of the National Academy of Sciences*, 119(3), e2113658119. https://doi.org/10.1073/pnas.2113658119

Corbane, C., Politis, P., Syrris, V., Pesaresi, M., Kemper, T., et al. (2021). Global Human Settlement Layer: Built-up volume and floor space grids. *European Commission Joint Research Centre (JRC)*. https://doi.org/10.2760/081292

Ding, K., Li, J., Bhanushali, R., & Liu, H. (2019). Deep anomaly detection on attributed networks. In *Proceedings of the 2019 SIAM International Conference on Data Mining (SDM)* (pp. 594–602). SIAM. https://doi.org/10.1137/1.9781611975673.67

Jean, N., Burke, M., Xie, M., Davis, W. M., Lobell, D. B., & Ermon, S. (2016). Combining satellite imagery and machine learning to predict poverty. *Science*, 353(6301), 790–794. https://doi.org/10.1126/science.aaf7894

Kipf, T. N., & Welling, M. (2016). Semi-supervised classification with graph convolutional networks. In *International Conference on Learning Representations (ICLR)*.

Kuffer, M., Pfeffer, K., Sliuzas, R., & Baud, I. (2016). Slums from space—15 years of slum mapping using remote sensing. *Remote Sensing*, 8(6), 455. https://doi.org/10.3390/rs8060455

Sirko, W., Kashubin, S., Luccioni, A., et al. (2021). Continental-scale building detection from high resolution satellite imagery. *arXiv preprint arXiv:2107.12281*.

Veličković, P., Cucurull, G., Casanova, A., Romero, A., Liò, P., & Bengio, Y. (2018). Graph Attention Networks. In *International Conference on Learning Representations (ICLR)*.

Weiss, D. J., Nelson, A., Gibson, H. S., et al. (2018). A global map of travel time to cities to assess inequalities in accessibility in 2015. *Nature*, 553(7688), 333–336. https://doi.org/10.1038/nature25181

---

## Word Count Allocation Summary

| Section | Target Proportion | Estimated Word Count |
| :--- | :---: | :---: |
| **Abstract & Keywords** | — | ~250 words |
| **1. Introduction** | 13% | 1,100 words |
| **2. Literature Review & Theory** | 16.5% | 1,400 words |
| **3. Study Area & Data Engineering** | 14% | 1,200 words |
| **4. Methodology** | 19% | 1,600 words |
| **5. Results & Validation** | 21% | 1,800 words |
| **6. Discussion & Limitations** | 12% | 1,000 words |
| **7. Conclusion** | 4.5% | 400 words |
| **Total Main Body** | **100%** | **~8,500 words** |

---

## Evidence-to-Section Mapping Matrix

| Manuscript Section | Primary Evidence & Data Sources | Target Figures / Tables | Served Research Question |
| :--- | :--- | :--- | :--- |
| **1. Introduction** | BPS Gini reports; UN-Habitat slum statistics; Meta RWI literature | **Figure 1**: Conceptual framework of dualistic urban form and micro-segregation | RQ1, RQ2, RQ3 |
| **2. Literature Review** | Jean et al. (2016); Chi et al. (2022); Kuffer et al. (2016); Weiss et al. (2018); Ding et al. (2019) | **Table 1**: Comparative paradigm benchmarking matrix | RQ1, RQ2 |
| **3. Data Engineering** | Google Open Buildings v3; JRC GHS-BUILT-C; Overture Places; WorldPop; VIIRS | **Figure 2**: Multi-source cloud data ingestion architecture onto H3 Res-8 | RQ1 |
| **4. Methodology** | 10D feature engineering code; PyTorch Geometric GAT-AE; OSMnx Dijkstra | **Figure 3**: GAT-AE network architecture with bottleneck and loss decomposition | RQ1, RQ2 |
| **5. Results** | Real Jabodetabek ~17.3k hex predictions; BSD/PIK border evaluations | **Figure 4**: Continuous PLSI surface map<br>**Figure 5**: Micro-segregation friction case studies<br>**Figure 6**: HDBSCAN cluster typologies<br>**Table 2**: Latent bottleneck ablation ($d \in \{2, 3, 4, 8\}$)<br>**Figure 7**: 4-Quadrant Meta RWI divergence scatter plot | RQ2, RQ3 |
| **6. Discussion** | Local planning statutes (RTRW); Bappeda policy needs; sensitivity analyses | **Table 3**: Methodological & data limitation disclosures | RQ1, RQ3 |
| **7. Conclusion** | Synthesis of findings; transferability scope | — | RQ1, RQ2, RQ3 |
