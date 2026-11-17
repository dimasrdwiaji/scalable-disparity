# Workstream A: Verified Academic Literature Map on Spatial Urban Deprivation

**Project**: Spatial Physical Living Condition Index (Jabodetabek / Greater Jakarta)  
**Deliverable**: Workstream A — Literature Review & Data Specification Mapping (Revision 2 — Incorporating User Feedback & Citation Verification)  
**Date**: 2026-11-11  
**Context**: Pre-modeling Deep Dive following Independent Review Panel, Stage 3 Triage, and Inline Feedback Lock  

> [!NOTE]
> **Classification Legend**: Claims are explicitly tagged as **`[Established]`** (demonstrated in peer-reviewed primary literature or directly observed in project screens), **`[Plausible]`** (mechanistically grounded hypothesis requiring empirical check in Workstream C), or **`[Unverified]`** (open empirical question to test in Workstream C before pipeline adoption).

---

## Executive Overview: Breaking Through the "Big Walls"

The independent review and Karawang Kotaku exploratory screens identified three critical failure modes in naive spatial disparity modeling:
1. **The Dasymetric Feedback Loop**: Living space per person ($\text{Volume} / \text{GHS-POP}$) collapses within census units because gridded population in `GHS-POP R2023A` is itself disaggregated using residential built volume ($R^2 = 0.976$ between `GHS-POP` and `GHS-BUILT-V` in Jabodetabek).
2. **The Density Confounder**: The leading principal component (`PC1`, $70.1\%$ variance) of the prior feature set tracks gross urban density and distance to Monas (density + distance to Monas explains $59.1\%$ variance).
3. **The Accessibility Sign-Flip**: Informal settlements exhibit *higher* cumulative walkable POI counts (`AUC = 0.30` in Karawang Kotaku screen; median `6.5` amenities in slum cells vs. `2.0` in formal cells) because survival/informal commerce co-locates in compact kampungs while formal suburban estates are car-oriented.

Each section below addresses one of the eight handoff research questions, incorporates all resolved author design constraints (dropping Setbacks, $\text{PM}_{2.5}/\text{NO}_2$, OSM Sidewalks, and excluding Flood Hazard from the universal global core; locking Intra-Urban Thermal Disparity over lapse-rate correction and splitting Accessibility into Public vs. Commercial channels), and points directly to Workstream B ([dataset_inventory.md](file:///C:/Users/Dimas%20RD/Documents/projects/phys_living_index/docs/research/deep-dive-2026-11-10/dataset_inventory.md)).

---

## Question 1: How Does Earth Observation Handle the Density Confounder in Slum/Deprivation Mapping?

### 1.1 Academic State of the Art
In systematic remote sensing reviews of informal settlements ([Kuffer et al., 2016](https://doi.org/10.3390/rs8060455); [Taubenböck et al., 2018](https://doi.org/10.1016/j.apgeog.2018.02.002); [Lilford et al., 2017](https://doi.org/10.1016/S0140-6736(16)31848-7)), gross building density ($\lambda_p$) is recognized as a necessary descriptor of built concentration but a **non-specific marker of deprivation**. Dense formal residential estates, mixed high-rise corridors, and informal settlements can all occupy high built-up fractions.

**Methodological strategies evaluated against Global South (Southeast Asian) urban realities**:
1. **`[Established]` Morphological Grain & Footprint Area Distribution**: Deprived settlements are characterized not simply by high coverage, but by **small, heterogeneous micro-scale footprint grains**.
   * *Global Literature Benchmark*: Across global "Arrival City" sites analyzed by [Taubenböck et al. (2018)](https://doi.org/10.1016/j.apgeog.2018.02.002), half of the sites exhibited median ground-floor building footprints below **$60\text{ m}^2$**, reaching extreme lower bounds such as **$7.7\text{ m}^2$** median footprint area in Manila informal settlements. Similarly, [Abascal et al. (2022b)](https://doi.org/10.1016/j.compenvurbsys.2022.101820) and [Jochem et al. (2021)](https://doi.org/10.1177/2399808320921208) show that building footprint area distributions and multi-scale spatial signatures distinguish residential neighborhood typologies independently of aggregate count density.
   * *Indonesian Housing Standard Context*: **SNI 03-1733-2004** (*Tata Cara Perencanaan Lingkungan Perumahan di Perkotaan*) and technical guidelines for *Rumah Sederhana Sehat* (**Kepmen Kimpraswil No. 403/KPTS/M/2002**) establish a minimum floor space benchmark of **$9\text{ m}^2/\text{person}$**, equating to **$36\text{ m}^2$** for a 4-person household (aligned with Type-36 basic housing, below typical formal Indonesian landed housing units). Structures whose *gross external footprint* falls below **$30\text{ m}^2$** fall below the basic family threshold even before deducting walls and circulation.
   * *Project Empirical Evidence*: In the Karawang Kotaku screen, the share of footprints $< 30\text{ m}^2$ exhibited near-zero correlation with gross density ($\rho \approx 0$) while maintaining `AUC = 0.60` for separating Kotaku slum polygons.
2. **`[Established vs. Unverified at Open Scale]` Structural Texture (VHR vs. Medium-Resolution Sentinel-2 / Sentinel-1)**: Classical texture/GLCM slum-mapping studies relied on **commercial very-high-resolution (VHR) sensors** where individual roofs span multiple pixels: e.g., [Wurm et al. (2017)](https://doi.org/10.1016/j.rse.2017.03.030) demonstrated SAR GLCM and polarimetric spatial features on **`~1 m` TerraSAR-X Spotlight data** in Mumbai, and [Leonita et al. (2018)](https://doi.org/10.3390/rs10101522) used **VHR optical GLCM** in Bandung ([Kuffer et al., 2016](https://doi.org/10.3390/rs8060455)).
   * *Open `10 m–20 m` Reality Check (`[Plausible]`)*: Neither free **`10 m` Sentinel-2** nor free **`~20 m × 22 m` native Sentinel-1 IW GRD** (resampled to `10 m` grid spacing) can resolve individual $25\text{--}40\text{ m}^2$ kampung roofs; both capture block-scale neighborhood heterogeneity rather than per-roof texture. Between the two, **`10 m` Sentinel-2 optical GLCM** offers crisper native resolution without multiplicative radar speckle or orbital-azimuth corner-reflector bias (and without InSAR phase complexity, since InSAR belongs to ground subsidence rather than amplitude texture). However, optical GLCM requires care: masking only to a `residential` land-use polygon leaves `tree-lawn-roof` contrast intact in leafy formal estates, while pixel-level `NDVI`/built masking creates sparse `NaN`-pair dropouts in low-coverage formal subdivisions. Whether either Sentinel-2 GLCM or Sentinel-1 `VH/VV` sub-pixel scattering improves density-stratified separation beyond `50 cm`-derived building polygons remains **`[Unverified]`**.
3. **Interstitial Setbacks — `[Dropped — Euro/US Gridded Planning Bias]`**: Measuring minimum building-to-building setbacks ($1.5\text{--}5\text{ m}$) reflects Western zoning codes. In Indonesian and wider Southeast Asian cities, formal commercial shophouses (*ruko*) and legal planned row-houses frequently exhibit zero side setbacks (wall-to-wall party walls). Setbacks are excluded from candidate feature engineering.
4. **`[Unverified]` Performance Strictly Conditioned on Density Strata**: Remote sensing slum classifiers routinely report citywide accuracy without stratifying by density bands. Whether morphological grain (`< 30 m²`, `< 50 m²`, Gini) and block-scale texture (`Sentinel-2` masked GLCM vs. optional `Sentinel-1 VH/VV`) separate slum from non-slum cells **within matched density terciles** remains an explicit test for Workstream C.

### 1.2 Data to Look For (Workstream B)
* **Vector Building Footprints**: Ground polygon area distributions (`< 30 m²`, `< 50 m²`, Footprint Area Gini) from *Google Open Buildings v3*, *Microsoft Global ML Building Footprints*, *Overture Maps Buildings*, and *OSM Buildings*.
* **Block-Scale Spectral/Texture & Optional SAR Material Probes**: *Copernicus Sentinel-2 L2A* (`10 m` masked optical GLCM + spectral bands) and, only as a secondary sub-pixel scattering check, *Copernicus Sentinel-1 GRD* (`VH/VV` amplitude cross-ratio).

---

## Question 2: Gridded Deprivation & Wealth Products (GRDI, RWI, WorldPop) Inside Cities

### 2.1 Academic State of the Art
1. **Meta Relative Wealth Index (RWI)** ([Chi et al., 2022](https://doi.org/10.1073/pnas.2113658119)):
   * **`[Established]` Scale & Connectivity Mismatch**: Mapped at $\sim 2.4\text{ km}$ tiles ($\approx 5.76\text{ km}^2$) using DHS/LSMS training data, Meta connectivity logs, road networks, and satellite inputs. Inside fragmented megacities, a single $2.4\text{ km}$ tile aggregates impoverished kampungs alongside adjacent high-income estates and commercial corridors, obscuring fine-grained deprivation boundaries (`~0.75 km²` H3 Res 8 scale) and risking cellular/connectivity spillover bias.
2. **Global Gridded Relative Deprivation Index (GRDI v1)** ([CIESIN / SEDAC, 2022](https://doi.org/10.7927/3XXE-AP97)):
   * **`[Established]` Component & Resolution Audit**: Mapped at $30\text{ arc-seconds}$ ($\approx 1\text{ km}$) over six components: Subnational HDI, Infant Mortality Rate, Child Dependency Ratio, Built-Up Area Ratio, VIIRS Nighttime Lights (VNL), and VNL Slope. Because demographic health inputs vary only at coarse administrative (province/regency) levels, **all sub-regency intra-urban variation inside GRDI v1 comes from built-up area and VIIRS nightlights**. In the Karawang Kotaku screen, VIIRS nightlights achieved `AUC = 0.20` (slum cells appeared brighter than formal/peri-urban cells), showing that GRDI inside a megacity conflates industrial/electrical corridor brightness with affluence.
3. **WorldPop Gridded Population & Poverty Surfaces** ([Stevens et al., 2015](https://doi.org/10.1371/journal.pone.0107042); [Steele et al., 2017](https://doi.org/10.1098/rsif.2016.0690)):
   * **`[Established]` Covariate & Dasymetric Leakage**: Top-down WorldPop constrained/unconstrained grids at $100\text{ m}$ rely on Random Forest weighting over geospatial covariates that include **VIIRS nighttime lights**, road networks, land cover, and built-settlement footprints. Consequently, WorldPop cannot act as a leak-free socioeconomic predictor at H3 Res 8.

### 2.2 Decision for Workstream B
* **Exclude RWI, GRDI v1, and WorldPop wealth/constrained NTL-weighted grids as internal model features.** Inventory GRDI v1, WorldPop, and Meta HRSL strictly to document their exact disaggregation and leakage mechanics, and keep census/BPS macro statistics (Regency HDI, poverty rate) solely as regional post-hoc context.

---

## Question 3: Multi-Domain Deprivation Frameworks (IMD & IDEAMAPS)

### 3.1 Academic State of the Art
1. **The Domains of Deprivation Framework / IDEAMAPS** ([Abascal et al., 2022a](https://doi.org/10.1016/j.compenvurbsys.2022.101770); [Kuffer et al., 2020](https://doi.org/10.3390/rs12060982); [Thomson et al., 2020](https://doi.org/10.3390/socsci9050080)):
   * **`[Established]` Multi-Scalar Domain Architecture**: [Abascal et al. (2022a)](https://doi.org/10.1016/j.compenvurbsys.2022.101770) synthesize 9 deprivation domains nested across three spatial scales:
     1. *Household Scale* (housing durability, internal overcrowding, tenure, in-home WATSAN — not directly observable from space);
     2. *Within-Area Scale* (physical fabric morphology, built environment hazards, local green/open space, unserviced condition — **directly observable via EO and vector footprints**);
     3. *Area-Connect Scale* (connectivity and access to schools, healthcare, transit, and civic infrastructure).
   * *Scope Implication*: Framing this project around **Within-Area physical morphology/environment** + **Area-Connect service accessibility** matches what global open data can rigorously measure without making unsupported household-wealth claims.
2. **The English Index of Multiple Deprivation (IMD)** ([MHCLG, 2019](https://www.gov.uk/government/statistics/english-indices-of-deprivation-2019)):
   * **`[Established]` Domain Separation & Non-Compensatory Ranking**: IMD separates **Living Environment** (9.3% weight: Indoor housing quality vs. Outdoor air quality and pedestrian traffic injuries) from Barriers to Housing/Services and Income/Employment, ranking each domain independently before exponential transformation so high values in one domain do not silently cancel severe deprivation in another.
   * **Operational Filter for Open Global Data at H3 Res 8 (~$0.75\text{ km}^2$)**:
     * **Air Quality ($\text{PM}_{2.5}$ / TROPOMI $\text{NO}_2$) — `[Dropped — Coarse Spatial Resolution]`**: Satellite-derived surface $\text{PM}_{2.5}$ (ACAG, [van Donkelaar et al., 2021](https://doi.org/10.1021/acs.est.1c05309)) sits at $0.01^\circ$ ($\approx 1\text{ km}$) smoothed from regional AOD/GEOS-Chem, and Sentinel-5P TROPOMI $\text{NO}_2$ sits at $5.5 \times 3.5\text{ km}$. Neither resolves intra-urban H3 Res 8 living disparities without severe ecological fallacy.
     * **OSM Pedestrian / Sidewalk Attributes (`sidewalk=no`, `highway=footway`) — `[Dropped — Completeness & Informal Fabric Bias]`**: Crowdsourced sidewalk tagging suffers extreme contributor skew and misses informal pedestrian kampung alleys (*gang*).

---

## Question 4: Urban Morphology, Building Grain, & Orientation Entropy

### 4.1 Academic State of the Art & Vector Mechanics
1. **Circular Orientation Entropy ($H_{\text{orient}}$)** ([Boeing, 2019](https://doi.org/10.1007/s41109-019-0189-1); [Abascal et al., 2022b](https://doi.org/10.1016/j.compenvurbsys.2022.101820)):
   * **`[Established]` Theoretical Mechanism**: Planned residential developments align along rectilinear or engineered curvilinear streets, concentrating building bearings into 1–2 dominant orthogonal modes (low entropy). Organic informal settlements grow incrementally along paths, terrain, and parcel edges, scattering azimuths across angles (high entropy).
   * **`[Established]` Exact Vector Calculation (No Moving-Window Raster Filter)**: Rather than passing a raster moving-window filter across imagery, $H_{\text{orient}}$ is computed **directly on the vector set of building polygons inside each H3 Res 8 cell**: extract each footprint's minimum rotated rectangle azimuth $\theta_b \in [0^\circ, 180^\circ)$ (collapsed modulo $180^\circ$ or $90^\circ$ axial symmetry, weighted optionally by footprint area, requiring a minimum polygon count $N \ge N_{\min}$ to avoid small-sample noise), bin into $B$ angular histogram bins (e.g., 18 or 36 bins), and compute normalized Shannon entropy $H_{\text{orient}} = -\sum_{k=1}^B p_k \ln p_k / \ln B$.
   * **Important Vectorization Caveat (`[Plausible]` Artifact Risk)**: Automated Mask-R-CNN or U-Net vectorization can merge adjacent slum roofs into single blobs or over-regularize corners ([Chamberlain et al., 2024](https://doi.org/10.1016/j.compenvurbsys.2024.102104)). Workstream C must explicitly test whether $H_{\text{orient}}$ retains signal in Google Open Buildings v3 vs. Overture/OSM footprints!
2. **Footprint Area Gini ($G_{\text{area}}$)**:
   * **`[Established]` Non-Parametric Within-Cell Computation**: For the vector collection of building footprint areas $\{A_1, A_2, \dots, A_K\}$ inside H3 cell $i$, the Gini coefficient is calculated directly over the ungrouped empirical areas:
     $$G_{\text{area}, i} = \frac{\sum_{a=1}^K \sum_{b=1}^K |A_a - A_b|}{2 K^2 \bar{A}}$$
     This measures structural size heterogeneity (uniform repetitive tract plots vs. mixed shacks/workshops/villas) directly within each H3 cell without imposing parametric normality ([Jochem et al., 2021](https://doi.org/10.1177/2399808320921208); [Rey & Smith, 2013](https://doi.org/10.1007/s12076-012-0086-z)). Magnitude separation in Jabodetabek is **`[Unverified]`** pending Workstream C empirical testing.
3. **Local Climate Zones (LCZ)** ([Stewart & Oke, 2012](https://doi.org/10.1175/BAMS-D-11-00019.1)):
   * **`[Established]` Structural Differentiation**: Distinguishes Compact Low-Rise (`LCZ 3`, $1\text{--}3$ stories, $\lambda_p = 40\text{--}70\%$, sparse trees) from Compact High-Rise (`LCZ 1`) and Open Low-Rise (`LCZ 6`).

### 4.2 Data to Look For (Workstream B)
* **High-Coverage Vector Building Polygons**: *Google Open Buildings v3*, *Microsoft Global ML Footprints*, *Overture Maps Buildings*, and *OSM Buildings* (checking polygon merge rates, minimum area cutoffs, and orientation fidelity across providers).

---

## Question 5: Environmental Justice in Tropical Global South Megacities

### 5.1 Thermal Disparity: Locked Intra-Urban Baseline Design
1. **Surface Urban Heat Island (SUHI) & Environmental Equity** ([Voogt & Oke, 2003](https://doi.org/10.1016/S0034-4257(03)00079-8); [Chakraborty & Lee, 2019](https://doi.org/10.1016/j.jag.2018.09.015); [Chakraborty et al., 2019](https://doi.org/10.1088/1748-9326/ab3b99); [Hsu et al., 2021](https://doi.org/10.1038/s41467-021-22799-5)):
   * **`[Established]` Regional Rural Baseline Confound**: Using non-urban/rural buffers across a wide topographic region (such as Jabodetabek spanning $0\text{ m}$ coastal plains to Bogor/Puncak mountain forests and irrigated Karawang paddies) conflates macro-elevation, orographic moisture, and agricultural irrigation cooling with urban heat inequality.
   * **`[Established]` Tropical Optical/Thermal Cloud Confound**: Persistent monsoonal cloud cover and ASTER GED emissivity climatology artifacts create spatial noise in single-date Landsat `ST_B10` scenes ([Chakraborty & Lee, 2019](https://doi.org/10.1016/j.jag.2018.09.015)). Dry-season median compositing with strict `QA_PIXEL` cloud/cirrus masking is required.
   * **`[Plausible]` Locked Author Preference — Intra-Urban Thermal Disparity ($\Delta \text{LST}_{\text{intra}}$) Within the Same Urban Temperature Envelope**: Rather than fitting a global regional elevation/lapse-rate regression across mountain forests and lowland cities, thermal environmental injustice is operationalized **strictly within the urban settlement envelope relative to local urban peers**:
     * Compare each urban cell against a **local intra-urban baseline** within its shared urban temperature envelope (e.g., $\Delta \text{LST}_{\text{intra}, i} = \text{LST}_i - \tilde{\text{LST}}_{\mathcal{N}_R(i) \cap \text{Urban}}$, subtracting the median or formal-green urban baseline within a local $R$-km multi-ring neighborhood inside built urban clusters such as `GHS-SMOD` Urban Centres/Clusters or elevation-matched urban envelopes).
     * *Why this avoids global lapse-rate assumptions*: Within a local $3\text{--}10\text{ km}$ urban temperature envelope (e.g., comparing coastal/central Jakarta kampungs against formal green residential estates like Menteng/Kemang, and separately comparing Bogor urban kampungs against Bogor formal green estates), macro-climate and regional mountain altitude are held constant naturally without imposing uncertain moist-tropical lapse-rate parameters. Workstream C will test local-ring radius sensitivity and correlation against density.

### 5.2 Vegetation Disparity (NDVI) & Multi-Dimensional Typologies
* **`[Established]` Multi-Dimensional Non-Monotonic Behavior**: Across tropical megacity extents, low NDVI inside dense urban cores identifies absence of shade trees and complete impervious paving ([Chakraborty et al., 2019](https://doi.org/10.1088/1748-9326/ab3b99)), whereas rural agricultural edges combine high NDVI with sparse services.
* **`[Plausible]` Typological Preservation**: As clarified in user feedback, high-NDVI/low-access rural settlements vs. low-NDVI/high-density urban kampungs vs. vegetated/formal residential estates reflect **distinct multi-dimensional living-environment profiles** rather than a failure of NDVI. NDVI should be evaluated as an independent environmental greenness dimension rather than forced into a single monotonic axis with rural poverty.

### 5.3 Flood & Terrain Hazards — `[Excluded from Universal Global Core -> Optional Regional Module]`
* **Rationale**: Jakarta's coastal alluvial plains suffer severe localized riverine/tidal flooding (*banjir rob* / *banjir kiriman*) and coastal land subsidence ([Tay et al., 2022](https://doi.org/10.1038/s41893-022-00947-z)), which plain slope ($S_{>15^\circ}$) misses. However, flood hazard mechanisms are highly region-specific globally (pluvial/coastal vs. flash mountain vs. arid cities without flooding). Per stage triage constraints, terrain/flood products (*MERIT-Hydro HAND*, *FABDEM*, *Sentinel-1 InSAR*) are inventoried in Workstream B strictly as an **Optional Regional Hazard Module**, excluded from the universal cross-city physical core.

---

## Question 6: Accessibility Measures & The Global South "Sign-Flip"

### 6.1 Academic State of the Art
* **`[Established]` Why Walkable POI Counts Flip Sign**: European chrono-urbanism (the "15-Minute City", [Moreno et al., 2021](https://doi.org/10.3390/smartcities4010006)) assumes wealthy neighborhoods are vibrant mixed-use centers. In Indonesian and many Global South cities, compact informal kampungs contain abundant micro-scale retail, food stalls (*warungs*), and informal repair shops, whereas high-income gated estates enforce single-use residential zoning designed around private automobiles. Collapsing all POIs produced `AUC = 0.30` (median `6.5` slum POIs vs. `2.0` formal POIs) in Karawang.

### 6.2 Locked Solution — Dual-Channel Accessibility Split
Rather than forcing one ambiguous direction onto accessibility, split POIs cleanly into two separate open channels to evaluate empirical separation independently:
1. **`A_public` (Formal Public & Social Infrastructure Access)**: Accredited schools, formal community clinics / *Puskesmas* / hospitals, fire/emergency facilities, and formal public transit stops/stations (`highway=bus_stop`, `railway=station`), measured via shortest walking network distance and/or congestion-aware coverage rather than raw total count.
2. **`A_commercial` (Everyday Sustenance & Commercial Retail Access)**: Food retail, markets, shops, cafes, and neighborhood services — interpreted alongside urban morphology to distinguish dense mixed-use kampungs from auto-dependent suburban gated estates.

---

## Question 7: Neighbor-Contrast, Spatial Discontinuity, & Graph Autoencoders (Stage 4)

### 7.1 Academic State of the Art
* **`[Established]` Relational Spatial Inequality**: Local Indicators of Spatial Association (LISA / Local Moran's $I$, [Anselin, 1995](https://doi.org/10.1111/j.1538-4632.1995.tb00338.x)) and spatial Gini decompositions ([Rey & Smith, 2013](https://doi.org/10.1007/s12076-012-0086-z)) capture local spatial boundary discontinuities (`High-Low` / `Low-High` friction edges where deprived kampungs abut wealthy estates).
* **`[Plausible]` Prerequisite for Meaningful Graph Learning**: Graph Attention Autoencoders (`GAT-AE`) can only detect socio-spatial boundary friction if node inputs $\mathbf{x}_i$ are **not dominated by a smooth urban density gradient** (which currently absorbs $70.1\%$ variance in `PC1`). Input features fed into Stage 4 must demonstrate genuine within-density discrimination or low density collinearity first.

---

## Question 8: Rigorous Validation Designs for Unsupervised Spatial Indices

### 8.1 Academic State of the Art
1. **`[Established]` Spatial Block Cross-Validation** ([Roberts et al., 2017](https://doi.org/10.1111/ecog.02881)): Random $k$-fold splits leak spatial autocorrelation. Validation and parameter checks require contiguous spatial blocks / held-out regency splits.
2. **`[Established]` Density-Stratified Known-Group Validation**: Evaluate candidate features using Mann-Whitney $U$, Cliff's $\delta$, and ROC-AUC **within matched density strata** (e.g., density terciles) against held-out confirmed boundaries (`Kotaku SK Kumuh`, `DKI Pergub 90/2018` priority RW subject to geometry verification, and formal planned estates) so models cannot score well merely by detecting city boundaries.
3. **`[Plausible]` Cross-City Out-of-Region Transferability**: Test frozen global-core definitions on external Indonesian metro areas (e.g., Bandung, Surabaya) and international open slum benchmarks (Rio de Janeiro IPP / IBGE, Cape Town, Nairobi).

---

## Summary: What Data Workstream B Must Inventory

| Target Physical Dimension | Status / Scope | Primary Open Data Candidates | Core Audit Question for Workstream B |
| :--- | :--- | :--- | :--- |
| **1. Building Morphology, Grain & $H_{\text{orient}}$** | Universal Core Candidate | *Google Open Buildings v3*, *Microsoft Footprints*, *Overture Buildings*, *OSM Buildings* | Coverage, polygon merge/simplification artifacts in slums, minimum area cutoff, license (`CC-BY-4.0` vs. `ODbL`). |
| **2. Block-Scale Optical Texture & Optional SAR Material** | Universal Core (`S2`) / Optional Check (`S1`) | *Sentinel-2 L2A* (`10 m` masked GLCM) vs. *Sentinel-1 GRD* (`VH/VV` amplitude, `~20 m` native) | Verify whether masked `10 m` Sentinel-2 GLCM avoids `tree-roof` / `NaN`-pair bias and whether coarse Sentinel-1 `VH/VV` adds anything non-redundant. |
| **3. Intra-Urban Thermal Anomaly ($\Delta\text{LST}_{\text{intra}}$)** | Universal Core Candidate | *Landsat 8/9 C2 L2 `ST_B10`*, *ECOSTRESS LSTE* | Cloud/ASTER-GED artifacts, local intra-urban envelope definition (`GHS-SMOD` urban mask). |
| **4. Urban Greenness / Canopy Deficit (NDVI)** | Universal Core Candidate | *Sentinel-2 Level-2A* (`B4`, `B8`, `SCL`) | Tropical cloud compositing, separation of rural paddy vs. urban kampung lack of shade. |
| **5. Dual Accessibility (`A_public` vs. `A_commercial`)** | Universal Core Candidate | *Overture Maps Places* (v2 taxonomy), *OSM POIs* & Street Network | Completeness bias across formal vs. kampung zones; schema breaking changes (`v2.0.0`). |
| **6. Gridded Built/Pop & Pre-Baked Indices (Audit)** | Rejection / Masking Audit | *GHSL R2023A*, *Meta HRSL*, *WorldPop*, *GRDI v1*, *Meta RWI* | Document exact NTL / built-up / volume leakage (`GHS-POP` $R^2=0.976$). Determine safe envelope masks (`GHS-SMOD`). |
| **7. Street-Level Imagery & Coarse Air Quality** | Rejected Audit | *Mapillary*, *ACAG $\text{PM}_{2.5}$*, *TROPOMI $\text{NO}_2$*, *OSM Sidewalks* | Confirm exact spatial resolution / kampung access omission limits. |
| **8. Regional Flood & Subsidence** | Optional Regional Module | *Copernicus GLO-30*, *FABDEM*, *MERIT-Hydro HAND*, *InSAR (DR-NTU)* | Document global availability vs. regional specificity. |
| **9. External Validation Geometries** | Validation Benchmark | *Kotaku*, *DKI Pergub 90*, *Rio IPP/IBGE*, *Cape Town*, *Map Kibera* | Verify license, coordinate geometry type (polygon vs. point), and non-circularity. |

---

## Verified References
See the complete primary-verified reference ledger in [references_verified.md](file:///C:/Users/Dimas%20RD/Documents/projects/phys_living_index/docs/research/deep-dive-2026-11-10/references_verified.md).
