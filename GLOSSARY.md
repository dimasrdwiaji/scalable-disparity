# Domain Glossary: Urban Physical Deprivation & Micro-Environmental Injustice

This glossary defines the standardized domain terms for the **revised Option A framework** (post-2026-11-10 audit and Workstream D [`options_memo.md`](docs/research/deep-dive-2026-11-10/options_memo.md)). Legacy/retired `PLSI` terms are listed at the bottom for traceability when inspecting older scripts.

---

### Spatial Grid & Geometry

* **H3 Resolution 8 (Res-8)**: Discrete Global Grid System hexagonal cell with an average area of $\approx 0.737\text{ km}^2$ and an edge length of $\approx 531\text{ m}$. Represents the primary spatial unit of analysis.
* **Urban Built-Up Mask**: Purely physical analysis mask combining `GHS-SMOD` urban settlement classes (`{21, 22, 23, 30}`) with $\ge 1$ residential building remaining after OpenStreetMap non-residential exclusions (zero `GHS-POP` or `WorldPop` population gate). Intra-urban thermal baselines and inequality metrics are evaluated strictly inside this mask.
* **Adjacency Graph ($A \in \mathbb{R}^{N \times N}$)**: Binary undirected topological graph where edge $A_{ij} = 1$ if hex cells $i$ and $j$ share a boundary on the H3 grid.
* **Spatial Blocking (CV)**: Spatially disjoint cross-validation folds used to prevent spatial autocorrelation leakage during threshold selection, boundary testing, and Stage 4 benchmarking.

---

### Built-Form & Morphology (Density-Orthogonal Core)

* **Residential Footprint Mask (`OSM` Non-Residential Filter)**: Spatial exclusion mask built from OpenStreetMap non-residential zones (`21,135` zones in the Jabodetabek screen) to remove factories, warehouses, ports, offices, and large commercial halls prior to computing residential morphology.
* **Small-Footprint Residential Buildings (`res_share_lt50`)**: Proportion of masked residential building footprints in a cell below the local small-structure threshold ($< 50\text{ m}^2$, with $< 60\text{ m}^2$ sensitivity check), capturing fine-grain informal subdivision independently of gross built-up density.
* **Interstitial Roof Spacing (`res_nn_p25`)**: 25th-percentile nearest-neighbor spacing (meters) among masked residential building footprints, measuring tight packing between roofs inside urban cores.
* **Residential Built Share (`ghs_res_share`)**: Proportion of built-up footprint/volume classified as residential (`GHSL`), used conditionally within urban cores to flag industrial, port, or rail encroachment around residential pockets.
* **Roof-Material Texture Candidate (`s2_res_glcm_*`)**: *Prospective Stage 3 candidate* — Gray-Level Co-occurrence Matrix texture derived from `10 m` Sentinel-2 imagery masked to residential footprints, under evaluation to test whether it detects heterogeneous/makeshift roof assemblages independently of macro-density.

---

### Intra-Urban Micro-Environment (Green & Thermal Baselines)

* **Vegetative Canopy (`NDVI`)**: Sentinel-2 Normalized Difference Vegetation Index ($\frac{\text{NIR} - \text{Red}}{\text{NIR} + \text{Red}}$) evaluated inside the urban mask to measure neighborhood canopy deficit relative to formal urban residential peers.
* **Intra-Urban Heat Anomaly (`ΔLST` / `dlst_intra`)**: Multi-year `100 m` Landsat 8/9 Tier-1 clear-sky land surface temperature minus the median LST of urban-masked peer cells inside a **local `k = 5` H3 focal ring ($\approx 2.6\text{ km}$ radius)** (with citywide urban-cluster median retained as a sensitivity comparison). Using urban peers removes coastal sea-breeze and terrain-slope offsets without `1 km` MODIS fallback.

---

### Composite Scoring, Inequality & Boundary Models

* **Urban Physical Deprivation Score**: Domain-validated synthesis of **Built Form** and **Micro-Environment** tested empirically across equal-weight domain averaging ($M_{z_i}$) and positive-offset Mazziotta–Pareto penalty aggregation ($\text{MPI}^+ = M_{z_i} + S_{z_i}^2 / M_{z_i}$) to test whether penalizing unbalanced deficits improves separation.
* **Hex-Grid Inequality Suite (`Gini`, `Lorenz`, `Spatial Palma Ratio`)**: Citywide inequality metrics computed **unweighted over equal-area urban-masked H3 cells** (`0.737 km²` each, inspired by `greenR`, with masked residential building count as an optional robustness check), always paired with known-group validation (`DKI Pergub 90`, stratified `Karawang`, and external hold-out city).
* **Spatial GAT Autoencoder (`GAT-AE`)**: Graph Attention Autoencoder over H3 geometric adjacency taking all `D = 4–6` individual vetted physical inputs directly (`in_channels = D`) into a `d = 2` latent bottleneck (never `d = D`), decomposed post-hoc into **Built-Form Friction** vs. **Micro-Environmental Friction**. Framed strictly as a **benchmarked hypothesis** against `Local Moran's I` (LISA) and pairwise Euclidean feature differences under spatially blocked CV.
* **Segregation Friction / Boundary Seams**: Sharp local feature discontinuities or elevated `GAT-AE` reconstruction errors ($\|x_i - \hat{x}_i\|^2$) evaluated against verified administrative/settlement borders (`Pergub 90` RW boundaries).

---

### Deprecated / Retired Terms (Do Not Use in Active Pipeline)

* **Living Space Ratio (`R_space` / UN-Habitat `9.0 m²`)**: Retired due to dasymetric circularity (`GHS-POP` vs. `GHS-BUILT-V` $R^2 = 0.976$) and null intra-urban discrimination (`DKI AUC = 0.5269, p = 0.210`).
* **Cumulative Walking Opportunities (`A_amenity`) & `osm_park400_2sfca`**: Retired from the deprivation score; general POI proximity inverts across dense *kampungs* vs. formal enclaves, and OSM parks were dropped per author decision due to secondary-city sparsity (`Karawang median = 0.0`).
* **Economic Energy Radiance (`E_night` / `VIIRS`)**: Retired; tracks macro urban intensity (`rho = 0.82`) and flips in secondary cities.
* **Air Purity (`PM25_inv`, `NO2_inv`), Water/Flood (`water_frequency`, `HAND`), `GLO-30` Slope, `plan_area_frac`, `Meta RWI`**: Retired or explicitly out of scope (coarse sensor resolution, DSM building-height bias, density collinearity, flood exclusion, and non-physical ML wealth proxy exclusion).
