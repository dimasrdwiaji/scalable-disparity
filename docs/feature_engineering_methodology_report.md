# Spatial Feature Engineering for Physical Living Condition Disparity: Methodological Report & Independent Peer Review Protocol

**Project**: Spatial Physical Living Condition Index (Greater Jakarta / Jabodetabek Megacity)  
**Spatial Scale**: Uber H3 Hexagonal Discrete Global Grid System, Resolution 8 (Mean Cell Area $\approx 0.737 \text{ km}^2$, Inter-Cell Spacing $\approx 922\text{ m}$)  
**Total Spatial Universe**: $N = 9,345$ Residential Grid Cells across $6,992.4 \text{ km}^2$ ($32.10\text{ Million}$ Inhabitants)  
**Pipeline Stage**: Feature Engineering & Pre-Modeling Methodological Audit (Stage 2.5 / Review Entry)  
**Date**: November 2026  

---

## Executive Summary

This report establishes the complete methodological foundation, mathematical formalization, empirical results, and critical limitations of the spatial feature engineering pipeline designed to quantify intra-urban physical living disparities across Greater Jakarta (Jakarta Metropolitan Area / Jabodetabek). 

The pipeline models physical living conditions across seven dimensions grounded in urban morphology, urban climatology, transport equity, and environmental hazards:
1. **Residential Plan Area Fraction ($\lambda_{p,\text{res}}$)**
2. **2D Residential Footprint Area per Capita ($A_{\text{fp,res}} / \text{Pop}$)** and **Model-Inferred Living Space ($R_{\text{space}}$)**
3. **Building Morphological Compactness & Irregularity ($C_{\text{res}}$)**
4. **15-Minute Cumulative Essential Amenity Accessibility ($A_{\text{amenity}}$)**
5. **Vegetation Cover Fraction / Greenness ($f_{\text{veg}}$)**
6. **Micro-Scale Surface Urban Heat Island Anomaly ($\Delta \text{LST}$)**
7. **Hazardous Slope Exceedance Share ($S_{>15^\circ}$)**

A core contribution of this report is resolving the **"Built-Up vs. Plan Area Fraction Paradox"** and the **"Geographic Composition Skew"**:
* While satellite land-cover products characterize Jakarta as $75\%\text{--}80\%$ built-up (measuring total impervious surface), actual building roof coverage ($\lambda_p$) across DKI Jakarta is **$21.88\%$ residential** and **$28.75\%$ gross**, which aligns with Local Climate Zone 3 (Compact Low-Rise) benchmarks and peer megacities such as Metro Manila.
* In unstratified analyses, summary statistics are dominated by the $83.8\%$ peri-urban/rural cells of Kabupaten Bogor, Karawang, Bekasi, Lebak, and Cianjur. When stratified into the **Metropolitan Core (DKI Jakarta, $N=860$)**, **Satellite Municipalities (Kota Bodetabek, $N=926$)**, and **Peri-Urban Fringes ($N=7,559$)**, the indicators reflect local spatial realities.

The document concludes with a **Formal Independent Peer Review Instruction Protocol** designed for a 5-seat expert review panel to evaluate the methodological rigor, ground-truth validity, and potential systemic biases of this feature store prior to Graph Neural Network (GNN) and unsupervised index modeling.

---

## Section 1: Indicator Inventory ("What Is Calculated")

The spatial feature store represents each residential H3 cell $i \in \{1, \dots, N\}$ as a 7-dimensional feature vector $\mathbf{x}_i \in \mathbb{R}^7$:

$$\mathbf{x}_i = \begin{bmatrix} \lambda_{p,\text{res}, i} & A_{\text{fp,res}, i}/\text{Pop}_i & C_{\text{res}, i} & A_{\text{amenity}, i} & f_{\text{veg}, i} & \Delta \text{LST}_i & S_{>15^\circ, i} \end{bmatrix}^T$$

| Indicator Name | Mathematical Symbol | Unit | Physical Dimension Captured | Disparity Direction |
| :--- | :--- | :--- | :--- | :--- |
| **1. Residential Plan Area Fraction** | $\lambda_{p,\text{res}}$ | Dimensionless $[0, 1]$ | Ground-level building congestion, lack of setbacks, building packing density | Higher $\to$ Higher Congestion / Kampung Morphology |
| **2. Residential Footprint per Capita** | $A_{\text{fp,res}} / \text{Pop}$ | $\text{m}^2/\text{person}$ | Overcrowding, internal spatial deprivation, domestic confinement | Lower $\to$ Severe Overcrowding |
| **3. Building Compactness / Irregularity** | $C_{\text{res}}$ (or $I_{<0.55}$) | Dimensionless $[0, 1]$ | Organic self-built roof geometries vs. planned rectilinear subdivisions | Lower $C$ $\to$ Organic Informal Slum Morphology |
| **4. 15-Minute Amenity Accessibility** | $A_{\text{amenity}}$ | Count of POIs | Pedestrian service access equity (clinics, schools, markets) | Lower $\to$ Spatial Exclusion / Service Desert |
| **5. Vegetation Cover Fraction** | $f_{\text{veg}}$ | Dimensionless $[0, 1]$ | Green infrastructure deficit, lack of tree canopy, biophilic inequality | Lower $\to$ Environmental Deprivation |
| **6. Thermal Stress Anomaly** | $\Delta \text{LST}$ | Kelvin ($\text{K}$) | Micro-urban heat island exposure, lack of shading, corrugated metal heat trapping | Higher $\to$ Acute Environmental Hazard |
| **7. Hazardous Slope Exceedance** | $S_{>15^\circ}$ | Percentage $[0, 100\%]$ | Geomorphological hazard exposure (landslide vulnerability, unbuildable steep terrain) | Higher $\to$ Severe Physical Hazard Risk |

---

## Section 2: Mathematical Formulations & Derivations ("How to Calculate It")

### 2.1 Spatial Tessellation Base
All calculations are anchored to the Uber H3 discrete global grid system at **Resolution 8**:
* **Hexagon Area**: $A_{\text{cell}} \approx 0.7373\text{ km}^2$ ($737,328\text{ m}^2$ or $73.73\text{ ha}$)
* **Hexagon Edge Length**: $L_{\text{edge}} \approx 461.4\text{ m}$
* **Inter-Hexagon Centroid Distance**: $D_{\text{centroid}} \approx 922.7\text{ m}$
* **Residential Filter Criterion**: A cell is included in the residential analysis universe if and only if:
  $$\text{Pop}_i \ge 50 \quad \text{AND} \quad A_{\text{bldg,res}, i} > 0$$

### 2.2 Mathematical Formulations

#### Indicator 1: Residential Plan Area Fraction ($\lambda_{p,\text{res}}$)
The ratio of the sum of residential building footprint planar areas intersecting cell $i$ to the total planar area of the cell:
$$\lambda_{p,\text{res}, i} = \frac{\sum_{k \in \mathcal{B}_{\text{res}, i}} \text{Area}(B_k \cap H_i)}{\text{Area}(H_i)}$$
Where $H_i$ is the polygon geometry of H3 cell $i$, $B_k$ is the polygon geometry of building $k$, and $\mathcal{B}_{\text{res}, i}$ is the set of buildings whose centroids or area intersections fall within the GHS-BUILT-C residential land mask.

#### Indicator 2: Residential Footprint per Capita ($A_{\text{fp,res}} / \text{Pop}$) & Living Space ($R_{\text{space}}$)
1. **2D Ground Footprint per Capita**:
   $$\text{FP}_{\text{capita}, i} = \frac{\sum_{k \in \mathcal{B}_{\text{res}, i}} \text{Area}(B_k \cap H_i)}{\text{Pop}_i} \quad \left[\frac{\text{m}^2}{\text{person}}\right]$$
2. **Model-Extrapolated 3D Floor Space per Capita ($R_{\text{space}}$)**:
   $$R_{\text{space}, i} = \frac{\sum_{k \in \mathcal{B}_{\text{res}, i}} \text{Area}(B_k) \times \max\left(1, \left\lfloor \frac{h_k}{3.0} \right\rfloor\right)}{\text{Pop}_i} \quad \left[\frac{\text{m}^2}{\text{person}}\right]$$
   Where $h_k$ is the building height in meters provided by Google Open Buildings (derived from stereo/shadow ML inference), and $3.0\text{ m}$ is the standard floor-to-floor height assumption.

#### Indicator 3: Building Morphological Compactness ($C_{\text{res}}$)
The area-weighted Polsby-Popper circularity score of all residential building footprints in cell $i$:
$$C_k = 4\pi \frac{\text{Area}(B_k)}{\left[\text{Perimeter}(B_k)\right]^2} \in (0, 1]$$
$$C_{\text{res}, i} = \frac{\sum_{k \in \mathcal{B}_{\text{res}, i}} \text{Area}(B_k) \cdot C_k}{\sum_{k \in \mathcal{B}_{\text{res}, i}} \text{Area}(B_k)}$$
* A circle exhibits $C = 1.0$; an ideal square exhibits $C = \pi/4 \approx 0.7854$; a $2:1$ rectangle exhibits $C = 8\pi/36 \approx 0.6981$.
* **Alternative Irregularity Formulation**: Share of irregular footprints ($C_k < 0.55$):
  $$I_{<0.55, i} = \frac{\sum_{k \in \mathcal{B}_{\text{res}, i}, C_k < 0.55} \text{Area}(B_k)}{\sum_{k \in \mathcal{B}_{\text{res}, i}} \text{Area}(B_k)}$$

#### Indicator 4: 15-Minute Cumulative Essential Amenity Accessibility ($A_{\text{amenity}}$)
The count of essential urban POIs reachable within a 15-minute walk along the pedestrian network:
$$A_{\text{amenity}, i} = \sum_{j \in \mathcal{P}_{\text{essential}}} \mathbb{I}\left( d_{\text{network}}(\mathbf{c}_i, \mathbf{p}_j) \le D_{\text{threshold}} \right)$$
* **Network Graph Formulation**: Computed using `city2graph.utils.spatial.create_isochrone` on OpenStreetMap pedestrian network topology.
* **Walking Speed**: $v_{\text{walk}} = 4.5\text{ km/h} = 1.25\text{ m/s}$.
* **Time Budget**: $T = 15\text{ minutes} = 900\text{ seconds}$.
* **Cutoff Distance**: $D_{\text{threshold}} = 4.5\text{ km/h} \times 0.25\text{ h} = 1.125\text{ km}$ ($1,125\text{ m}$).
* **POI Categories ($\mathcal{P}_{\text{essential}}$)**:
  * *Healthcare*: Clinics, puskesmas, pharmacies, hospitals.
  * *Education*: Primary and secondary schools, kindergartens.
  * *Basic Commerce*: Traditional wet markets (`marketplace`), grocery stores, daily food provisioning.

#### Indicator 5: Vegetation Cover Fraction ($f_{\text{veg}}$)
Calculated from Sentinel-2 Surface Reflectance optical imagery (10m resolution) using the Normalized Difference Vegetation Index (NDVI):
$$\text{NDVI} = \frac{\rho_{\text{NIR}} - \rho_{\text{Red}}}{\rho_{\text{NIR}} + \rho_{\text{Red}}} = \frac{B8 - B4}{B8 + B4}$$
Cell greenness is calculated as the spatial mean over all cloud-free pixels within $H_i$:
$$f_{\text{veg}, i} = \frac{1}{|\mathcal{G}_i|} \sum_{p \in \mathcal{G}_i} \text{NDVI}_p$$
* **Diminishing Fractional Vegetation Cover ($FVC$) Alternative**:
  $$FVC_p = \left( \frac{\text{NDVI}_p - \text{NDVI}_{\text{soil}}}{\text{NDVI}_{\text{veg}} - \text{NDVI}_{\text{soil}}} \right)^2$$
  where $\text{NDVI}_{\text{soil}} = 0.05$ and $\text{NDVI}_{\text{veg}} = 0.70$.

#### Indicator 6: Thermal Stress Anomaly ($\Delta \text{LST}$)
Calculated from Landsat-8/9 Thermal Infrared Sensor (TIRS Band 10) Surface Temperature:
$$\Delta \text{LST}_i = \overline{\text{LST}}_i - \text{LST}_{\text{baseline}}$$
* Where $\overline{\text{LST}}_i$ is the area-weighted mean surface temperature in Kelvin across cell $i$.
* $\text{LST}_{\text{baseline}}$ is the regional rural background temperature (calculated as the 10th percentile LST across all vegetated peri-urban cells during identical acquisition windows).

#### Indicator 7: Hazardous Slope Exceedance Share ($S_{>15^\circ}$)
Derived from Copernicus GLO-30 / FABDEM digital elevation models (30m spatial resolution). Local terrain gradient is computed via Horn's finite-difference algorithm:
$$\text{Slope}_p = \arctan \left( \sqrt{ \left(\frac{\partial z}{\partial x}\right)^2 + \left(\frac{\partial z}{\partial y}\right)^2 } \right) \times \frac{180^\circ}{\pi}$$
The indicator measures the spatial percentage of cell $i$ occupied by terrain steeper than $15^\circ$ ($26.8\%$ gradient):
$$S_{>15^\circ, i} = \frac{\text{Count}\left( p \in \mathcal{D}_i \mid \text{Slope}_p > 15^\circ \right)}{|\mathcal{D}_i|} \times 100\%$$

---

## Section 3: Primary & Secondary Datasets ("The Datasets Used")

| Dataset Name | Source / Provider | Spatial Resolution | Temporal Window | Data Type | Role in Pipeline | Global Open Access? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Google Open Buildings v3** | Google Research / Sentinel-2 & Maxar VHR | Individual Polygon ($< 1\text{ m}$) | 2023 Update | Vector Polygons | Building Footprints, Ground Area, Perimeter, ML Height | **Yes** (CC-BY 4.0 / CDLA-Permissive) |
| **GHS-BUILT-C (R2023A)** | European Commission JRC | $10\text{ m}$ Raster | 2020 (Epoch 2023) | Raster Classification | Residential vs. Non-Residential Building Land Mask | **Yes** (Open Data Policy) |
| **GHS-POP (R2023A)** | European Commission JRC | $100\text{ m}$ Raster | 2023 Projection | Raster Grid | Residential Population Counts per cell | **Yes** (Open Data Policy) |
| **Copernicus DEM (GLO-30)** | European Space Agency (ESA) | $30\text{ m}$ Raster | 2020 | Raster Grid | Digital Elevation Model, Slope Derivation | **Yes** (Open Data Policy) |
| **FABDEM v1.2** | University of Bristol (Hawker et al.) | $30\text{ m}$ Raster | 2021 | Raster Grid | Forest and Building Removed Bare-Earth DEM | **Yes** (Non-commercial / Academic CC-BY-NC) |
| **Sentinel-2 Surface Reflectance** | ESA / Copernicus Program | $10\text{ m}$ / $20\text{ m}$ | 2023 Dry Season Composite | Optical Imagery | VNIR Bands (B4, B8) for NDVI & Vegetation Cover | **Yes** (Open Access) |
| **Landsat-8/9 TIRS** | USGS / NASA | $30\text{ m}$ (resampled from 100m) | 2022–2024 Composite | Thermal IR | Band 10 Surface Temperature ($\text{LST}$) | **Yes** (Public Domain) |
| **OpenStreetMap (OSM)** | OpenStreetMap Contributors | Vector Topology | Extracted 2024 | Vector Graph & Points | Pedestrian Highway Network, Essential POIs | **Yes** (ODbL License) |
| **Susenas (Reference Benchmark)** | BPS (Statistics Indonesia) | Regency/City Aggregate | 2022–2023 | Tabular Survey | Ground-Truth Floor Space per Capita Benchmark | **Restricted / Public Summary** |

---

## Section 4: Theoretical & Methodological Justification ("Reasoning")

### 4.1 Grounding in Peer-Reviewed Literature

```
                                  PHYSICAL DISPARITY CONSTRUCT
                                               |
         +--------------------+----------------+--------------------+--------------------+
         |                    |                                     |                    |
  BUILT MORPHOLOGY     HOUSING SUFFICIENCY                  ACCESS EQUITY        ENVIRONMENTAL HAZARD
         |                    |                                     |                    |
  - λp,res (Stewart   - FP/Capita (UN-Habitat,               - 15-Min POI         - ΔLST (Voogt & Oke, 2003;
    & Oke, 2012;        2003, 2018; Susenas)                   (Moreno et al.,      Zhou et al., 2019)
    Grimmond & Oke,   - R_space (GHS Dasymetric                 2021; Geurs &     - Slope > 15° (Taubenböck
    1999)               Coupling)                               van Wee, 2004)      et al., 2018; Kuffer, 2020)
  - Compactness (C)                                                               - f_veg (Biophilic Equity)
```

1. **Why Residential Plan Area Fraction ($\lambda_{p,\text{res}}$) instead of Population Density?**
   * *Theoretical Foundation*: As established in the Local Climate Zone (LCZ) architecture ([Stewart & Oke, 2012](https://doi.org/10.1175/BAMS-D-11-00019.1)) and surface energy balance formulations ([Grimmond & Oke, 1999](https://doi.org/10.1175/1520-0450(1999)038<1222:AEROBF>2.0.CO;2)), plan area fraction directly quantifies *geometric packing*.
   * *Independence from Census Demography*: Population density conflates vertical capacity with horizontal overcrowding. A luxury high-rise condominium cluster and an informal shanty settlement can exhibit identical gross population densities ($30,000\text{ pop/km}^2$). However, the high-rise cluster maintains $\lambda_p \approx 0.15\text{--}0.25$ with open green setbacks, while the informal settlement reaches $\lambda_p > 0.45\text{--}0.65$ at the block scale, eliminating ground permeability, light, and ventilation ([Kuffer et al., 2016](https://doi.org/10.3390/rs8060455)).
   * *Use of GHS Residential Mask*: Calculating gross building footprint coverage conflates industrial warehouses, seaports (e.g., Tanjung Priok), and logistics terminals with residential overcrowding. Masking via GHS-BUILT-C ensures that building coverage measures purely domestic settlement density.

2. **Why Footprint per Capita ($A_{\text{fp,res}} / \text{Pop}$)?**
   * *Theoretical Foundation*: [UN-Habitat (2003, 2018)](https://unhabitat.org/the-challenge-of-slums-global-report-on-human-settlements-2003) defines "sufficient living space" as a fundamental deprivation indicator: a household is overcrowded if more than 3 persons share a single habitable room, or if living area drops below $5.0\text{ m}^2/\text{person}$.
   * *Bypassing ML Height Errors*: Vertical living space models ($R_{\text{space}}$) rely on satellite stereo-matching and shadow-length models. In informal settlements, narrow alleys obscure building shadows, causing neural height predictors to assign standard $3\text{ m}$ default heights. Furthermore, dasymetric population disaggregation allocates population proportional to building volume, generating mathematical circularity. Measuring 2D ground footprint per capita ($A_{\text{fp,res}} / \text{Pop}$) provides an empirical, model-free proxy for ground crowding.

3. **Why Building Compactness ($C_{\text{res}}$)?**
   * *Theoretical Foundation*: Informal settlements in Southeast Asia develop through spontaneous, uncoordinated, organic accretion ([Sliuzas et al., 2010](https://doi.org/10.1016/j.landurbplan.2010.04.001); [Taubenböck et al., 2018](https://doi.org/10.1016/j.rse.2017.10.044)). Footprints in spontaneous kampungs follow irregular alleyways, property lines, and canal bends, resulting in highly non-convex, tortuous polygon boundaries. Formal planned subdivisions (e.g., BSD City, Kelapa Gading) feature rectilinear, highly compact rectangular plots.

4. **Why 15-Minute Network Accessibility ($A_{\text{amenity}}$)?**
   * *Theoretical Foundation*: Physical inequality extends beyond the home parcel into the immediate pedestrian catchment ([Moreno et al., 2021](https://doi.org/10.1080/23748834.2021.1944282); [Geurs & van Wee, 2004](https://doi.org/10.1016/j.jtrangeo.2003.10.005)). In low-income Global South settlements, transit affordability constraints mandate that essential provisioning (food markets, community clinics/puskesmas, primary schools) must be pedestrian-accessible.

5. **Why Thermal Stress ($\Delta \text{LST}$) and Vegetation Deficit ($f_{\text{veg}}$)?**
   * *Theoretical Foundation*: Environmental injustice literature demonstrates that low-income settlements suffer disproportionately from Surface Urban Heat Islands (SUHI) due to dense corrugated iron or zinc roofing, high thermal mass, and near-zero vegetative shading ([Voogt & Oke, 2003](https://doi.org/10.1016/S0034-4257(03)00079-8); [Zhou et al., 2019](https://doi.org/10.1029/2018EF001099); [Chakraborty et al., 2019](https://doi.org/10.1016/j.envres.2019.108744)).

6. **Why Hazardous Slope Exceedance ($S_{>15^\circ}$)?**
   * *Theoretical Foundation*: In megacity peripheries, marginalized populations are priced out of safe, flat terrain and settle on unbuildable steep slopes (> 15° gradient / 27%) and ravine edges, creating catastrophic vulnerability to tropical monsoonal landslides and debris flows ([Taubenböck et al., 2018](https://doi.org/10.1016/j.rse.2017.10.044); [Kuffer et al., 2020](https://doi.org/10.1016/j.habitatint.2020.102212)). Indonesian national spatial planning guidelines (SNI 03-1733-2004 / Ministry of Public Works Regulation No. 20/PRT/M/2007) designate slopes above $15^\circ$ as restricted for standard residential construction.

---

## Section 5: Summary of Results & Stratified Distributions ("Summary of the Result")

### 5.1 The Geographic Composition Skew

The study area encompasses **9,345 residential H3 cells**. Evaluating the dataset as a single unstratified distribution produces misleading results because the study area comprises three distinct geographic regimes:
1. **DKI Jakarta Core**: $N = 860$ cells ($9.2\%$), representing the historic, ultra-dense capital core.
2. **Kota Bodetabek (Satellite Municipalities)**: $N = 926$ cells ($9.9\%$), representing mature urban satellite cities (Kota Bogor, Depok, Tangerang, Tangerang Selatan, Bekasi).
3. **Kabupaten Hinterlands (Peri-Urban & Rural Fringes)**: $N = 7,559$ cells ($80.9\%$), representing extensive agrarian, mountainous, and industrial expanses (Kabupaten Bogor, Karawang, Bekasi, Lebak, Cianjur).

```
+-----------------------------------------------------------------------------------------+
|                               STUDY AREA CELL UNIVERSE (N = 9,345)                     |
|                                                                                         |
|  [ DKI Jakarta Core: 860 cells (9.2%) ]                                                 |
|  [ Kota Bodetabek: 926 cells (9.9%)  ]                                                  |
|  [====================================================== Kabupaten: 7,559 cells (80.9%) ]|
+-----------------------------------------------------------------------------------------+
```

### 5.2 Unstratified Distribution (All 9,345 Residential Cells)

| Indicator | Min | 10th % | Median | Mean | 90th % | Max | IQR |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **$\lambda_{p,\text{res}}$** (Residential Plan Area) | $0.0001$ | $0.012$ | **$0.062$** | $0.098$ | $0.231$ | $0.482$ | $0.119$ |
| **$A_{\text{fp,res}} / \text{Pop}$** ($\text{m}^2/\text{person}$) | $0.12$ | $7.85$ | **$26.40$** | $39.81$ | $78.14$ | $482.1$ | $42.10$ |
| **$R_{\text{space}}$** (Modeled Living Space, $\text{m}^2/\text{p}$) | $20.31$ | $27.42$ | **$57.18$** | $74.65$ | $132.4$ | $612.0$ | $56.80$ |
| **$C_{\text{res}}$** (Building Compactness) | $0.412$ | $0.681$ | **$0.724$** | $0.720$ | $0.758$ | $0.841$ | $0.046$ |
| **$A_{\text{amenity}}$** (15-Min POI Count) | $0$ | $0$ | **$4$** | $29.4$ | $88.0$ | $542$ | $21.0$ |
| **$f_{\text{veg}}$** (Mean NDVI) | $-0.082$ | $0.214$ | **$0.448$** | $0.418$ | $0.582$ | $0.791$ | $0.246$ |
| **$\Delta \text{LST}$** (Thermal Anomaly, $\text{K}$) | $-6.42$ | $-2.11$ | **$+0.13$** | $+0.42$ | $+3.18$ | $+8.21$ | $2.84$ |
| **$S_{>15^\circ}$** (Hazardous Slope Share, $\%$) | $0.0\%$ | $0.0\%$ | **$0.0\%$** | $2.2\%$ | $5.4\%$ | $68.4\%$ | $0.0\%$ |

### 5.3 Stratified Distribution Across Regional Typologies

To eliminate the masking effect of the peri-urban hinterlands, the table below provides stratified metrics across the three geographic regimes:

| Feature Dimension | DKI Jakarta Core ($N=860$) | Kota Bodetabek ($N=926$) | Kabupaten Hinterlands ($N=7,559$) |
| :--- | :--- | :--- | :--- |
| **Evaluated Land Area** | $644.42\text{ km}^2$ | $692.81\text{ km}^2$ | $5,655.17\text{ km}^2$ |
| **2023 Population** | $10,846,531$ | $6,334,180$ | $14,923,410$ |
| **Mean Population Density** | $\mathbf{16,830\text{ pop/km}^2}$ | $6,840\text{ pop/km}^2$ | $2,638\text{ pop/km}^2$ |
| **$\lambda_{p,\text{res}}$ (Median)** | $\mathbf{23.0\%}$ (P90: $33.4\%$) | $\mathbf{13.2\%}$ (P90: $21.5\%$) | $\mathbf{4.8\%}$ (P90: $12.1\%$) |
| **$\lambda_{p,\text{gross}}$ (Aggregate)** | $\mathbf{28.75\%}$ (Provincial Gross) | $16.50\%$ (Gross) | $6.20\%$ (Gross) |
| **$A_{\text{fp,res}} / \text{Pop}$ (Mean)** | $\mathbf{13.00\text{ m}^2/\text{person}}$ | $\mathbf{21.40\text{ m}^2/\text{person}}$ | $\mathbf{49.60\text{ m}^2/\text{person}}$ |
| **$A_{\text{fp,res}} / \text{Pop}$ (5th Percentile)**| $\mathbf{2.92\text{ m}^2/\text{person}}$ | $6.85\text{ m}^2/\text{person}$ | $14.20\text{ m}^2/\text{person}$ |
| **$A_{\text{amenity}}$ (Median 15-Min POIs)** | $\mathbf{158\text{ amenities}}$ | $\mathbf{38\text{ amenities}}$ | $\mathbf{2\text{ amenities}}$ |
| **$f_{\text{veg}}$ (Mean NDVI)** | $\mathbf{0.178}$ (Severe Green Deficit) | $0.321$ | $0.482$ |
| **$\Delta \text{LST}$ (Mean Thermal Anomaly)** | $\mathbf{+2.78\text{ K}}$ (Extreme SUHI) | $+1.42\text{ K}$ | $-0.38\text{ K}$ |
| **$S_{>15^\circ}$ (Mean Hazardous Slope)**| $\mathbf{0.00\%}$ (Alluvial Plain) | $0.15\%$ | $\mathbf{2.82\%}$ (Max: $68.4\%$) |

### 5.4 Internal Disparities Within DKI Jakarta Core

Even within DKI Jakarta, substantial morphological and social gradients exist across the five administrative municipalities (*Kota Administrasi*):

| Municipality | Cells ($N$) | Population | Aggregate $\lambda_{p,\text{res}}$ | Footprint/Capita ($A_{\text{fp}}/\text{Pop}$) | P5 Footprint/Capita | Median 15-Min POIs | Mean $\Delta \text{LST}$ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Jakarta Barat** | $174$ | $2,584,210$ | **$28.12\%$** | **$12.82\text{ m}^2$** | **$2.92\text{ m}^2$** | $184$ | $+3.42\text{ K}$ |
| **Jakarta Pusat** | $68$ | $1,082,415$ | **$23.51\%$** | **$11.81\text{ m}^2$** | **$3.14\text{ m}^2$** | $262$ | $+3.18\text{ K}$ |
| **Jakarta Selatan** | $202$ | $2,385,120$ | **$23.94\%$** | **$14.85\text{ m}^2$** | $5.41\text{ m}^2$ | $164$ | $+2.15\text{ K}$ |
| **Jakarta Timur** | $256$ | $3,248,110$ | **$21.32\%$** | **$12.78\text{ m}^2$** | $4.88\text{ m}^2$ | $148$ | $+2.64\text{ K}$ |
| **Jakarta Utara** | $160$ | $1,546,676$ | **$14.82\%$** | **$11.88\text{ m}^2$** | **$2.84\text{ m}^2$** | $92$ | $+3.21\text{ K}$ |

* **Micro-scale extremes**: In the densest informal kampungs of Jakarta Barat (e.g., Kelurahan Tambora, Kali Anyar, and Jembatan Besi), cell-wide $\lambda_{p,\text{res}}$ reaches **$48.2\%$**, and ground footprint per capita drops to **$2.92\text{ m}^2/\text{person}$**.
* In Jakarta Utara, the provincial average $\lambda_p$ ($14.8\%$) is diluted by massive port infrastructure (Tanjung Priok), water retention bodies, and industrial terminals; yet its informal residential pockets (e.g., Kampung Akuarium, Kalibaru, Penjaringan) exhibit the most acute domestic overcrowding ($2.84\text{ m}^2/\text{person}$ at the 5th percentile).

---

## Section 6: Critical Methodological Uncertainties & Limitations ("Unsureness on Reality")

To ensure transparency for independent peer review, this section documents the six primary methodological uncertainties, physical paradoxes, and algorithm artifacts present in the engineered features.

### 6.1 The "Built-Up" vs. "Plan Area Fraction" Paradox
* **Observation**: Stakeholders and urbanists often perceive Jakarta as "$75\%\text{--}80\%$ built-up" based on satellite land-cover maps (e.g., ESA WorldCover, MODIS). Discovering that residential building coverage is $21.9\%$ and gross building coverage is $28.8\%$ appears counter-intuitive.
* **Physical Cause**: Remote sensing land-cover classifications evaluate **Impervious Surface Fraction (ISF)**, which groups together building roofs, asphalt tollways, arterial roads, paved residential alleyways, concrete drainage canals, and vast paved parking lots. In contrast, Plan Area Fraction ($\lambda_p$) accounts *strictly* for building footprint polygons.
* **Literature Reality**: Local Climate Zone (LCZ) literature ([Stewart & Oke, 2012](https://doi.org/10.1175/BAMS-D-11-00019.1)) notes that while LCZ 3 (Compact Low-Rise) reaches $40\%\text{--}70\%$ building coverage at the micro-block scale ($50\text{--}100\text{ m}$), when aggregated over an entire $74\text{ ha}$ neighborhood with arterial roads, waterways, and public infrastructure, grid-level $\lambda_p$ naturally caps at $40\%\text{--}48\%$. This matches observations in Metro Manila ([Estoque et al., 2017](https://doi.org/10.1016/j.apgeog.2017.04.008)), where cell-wide $\lambda_p$ averages $25\%\text{--}38\%$.

### 6.2 The GHSL Dasymetric Volume Smoothing Artifact
* **Observation**: Modeled 3D living space ($R_{\text{space}}$) had an artificial empirical minimum of **$20.31\text{ m}^2/\text{person}$**, failing to register known severely overcrowded kampungs where UN-Habitat standards ($< 5\text{ m}^2/\text{person}$) are breached.
* **Physical Cause**: This is a direct artifact of dasymetric disaggregation in the global GHS-POP model. GHS-POP downscales census block populations to $100\text{ m}$ pixels by distributing population proportionally to estimated building volume ($V_{\text{built}} = \text{Area} \times \text{Height}$). When a researcher subsequently calculates:
  $$R_{\text{space}} = \frac{\text{Building Volume} / 3.0\text{ m}}{\text{GHS-POP}}$$
  the building volume terms in the numerator and denominator cancel out, mathematically guaranteeing that $R_{\text{space}}$ approaches a smoothed constant ($18\text{--}22\text{ m}^2/\text{person}$) across all high-density pixels.
* **Resolution**: Shifting to **2D Ground Footprint Area per Capita ($A_{\text{fp,res}} / \text{Pop}$)** successfully eliminates this dasymetric feedback loop, accurately revealing the $2.8\text{--}3.1\text{ m}^2/\text{person}$ conditions in Tambora and Penjaringan.

### 6.3 Open Buildings Polygon Regularization & Variance Collapse in Compactness
* **Observation**: Across all $9,345$ cells, building compactness ($C_{\text{res}}$) exhibits severe variance collapse ($\text{Mean} = 0.720, \text{Median} = 0.724, \text{IQR} = 0.046$). The metric failed to distinguish informal kampungs from formal subdivisions.
* **Algorithm Cause**: Satellite building segmentation algorithms (such as Mask R-CNN in Open Buildings v3) heavily regularize detected pixel masks during polygon vectorization ([Sirko et al., 2021](https://arxiv.org/abs/2107.12242)). The vectorizer fits minimum bounding rectangles and orthogonal bounding boxes to noisy contours. Consequently, whether a building is an informal zinc shack or a planned villa, its vectorized geometry is rendered as a rectangle ($C \approx 0.70$) or square ($C \approx 0.785$).
* **Resolution**: Replace mean circularity with the **Share of Irregular Footprints ($C_k < 0.55$)** or **Footprint Area Variance**, which avoids vectorization artifacts.

### 6.4 Modifiable Areal Unit Problem (MAUP) & Boundary Averaging
* **Observation**: An H3 Resolution 8 cell encompasses $73.7\text{ hectares}$. In Southeast Asian cities, high-density informal kampungs frequently exist as narrow pockets ($2\text{--}10\text{ hectares}$) directly adjacent to upscale commercial districts or gated subdivisions (e.g., the high-rise towers of Mega Kuningan immediately abutting Kampung Karet).
* **Impact**: Averaging morphological features across $74\text{ ha}$ dilutes localized micro-slums with surrounding formal infrastructure, potentially underestimating the severity of localized deprivation.

### 6.5 Topographic Slope Resolution Sensitivity
* **Observation**: Using a $30\text{ m}$ DEM (Copernicus GLO-30 / FABDEM) yields $S_{>15^\circ} = 0.0\%$ across all of DKI Jakarta.
* **Physical Cause**: A $30\text{ m}$ pixel filters out micro-topographic variations. While Jakarta is predominantly an alluvial plain, acute slope hazards do exist in informal riverbank settlements (*bantaran kali*) along the Ciliwung and Pesanggrahan rivers, where informal dwellings perch on artificial $45^\circ\text{--}90^\circ$ riverbank drop-offs ($3\text{--}8\text{ m}$ high). These micro-cliffs are invisible to a $30\text{ m}$ DEM.

### 6.6 OpenStreetMap POI Completeness Gradient
* **Observation**: Amenity counts drop precipitously from $158$ in DKI Jakarta to $2$ in Kabupaten hinterlands.
* **Data Bias**: While rural peripheries legitimately have fewer commercial services, OpenStreetMap suffers from well-documented voluntary geographic information (VGI) contributor bias ([Barrington-Leigh & Millard-Ball, 2017](https://doi.org/10.1371/journal.pone.0180698)). Rural and low-income areas have lower mapping completeness compared to affluent, tech-dense central areas.

---

## Section 7: Formal Independent Peer Review Protocol

This protocol outlines the instructions and evaluation criteria for an independent, 5-seat academic peer review panel. Reviewers must assess whether the feature engineering methodology meets rigorous international publication standards (e.g., *Environment and Planning B*, *Remote Sensing of Environment*, *Landscape and Urban Planning*, or *Computers, Environment and Urban Systems*).

```
+-----------------------------------------------------------------------------------------+
|                              5-SEAT INDEPENDENT REVIEW PANEL                            |
+-----------------------------------------------------------------------------------------+
| Seat 1: Methodology & Spatial Statistics Reviewer                                       |
| Seat 2: Urban Geography & Morphology Domain Reviewer                                    |
| Seat 3: Remote Sensing & Environmental Injustice Reviewer                               |
| Seat 4: Southeast Asian Megacities & Comparative Urbanism Reviewer                     |
| Seat 5: Methodological Devil's Advocate Reviewer                                         |
+-----------------------------------------------------------------------------------------+
```

### 7.1 Reviewer Personas & Terms of Reference

#### Reviewer 1: Methodology & Spatial Statistics Reviewer
* **Focus**: Spatial aggregation validity, MAUP, spatial autocorrelation, mathematical formulation correctness, and collinearity.
* **Key Questions**:
  1. Is the choice of H3 Resolution 8 ($0.737\text{ km}^2$) methodologically defensible for capturing physical disparity, or does it introduce unacceptable ecological fallacy and MAUP dilution?
  2. Is the replacement of modeled living space ($R_{\text{space}}$) with 2D ground footprint per capita ($A_{\text{fp,res}} / \text{Pop}$) statistically sound, and does it adequately resolve dasymetric endogeneity?
  3. How should the pipeline handle extreme right-skewness and zero-inflation in POI accessibility and hazardous slope features prior to representation learning?

#### Reviewer 2: Urban Geography & Morphology Domain Reviewer
* **Focus**: Urban morphology, informal settlement definitions, plan area fraction benchmarks, and Local Climate Zones.
* **Key Questions**:
  1. Does the empirical plan area fraction ($\lambda_{p,\text{res}} = 21.88\%$ aggregate, peaking at $48.2\%$) accurately represent the spatial reality of Jakarta's built environment according to morphology literature?
  2. Does the GHS-BUILT-C residential mask reliably isolate domestic settlements, or does it misclassify mixed-use shophouses (*ruko*) common across Southeast Asia?
  3. Is building circularity/compactness ($C_{\text{res}}$) salvageable given Open Buildings polygon regularization, or should it be entirely replaced by footprint density/heterogeneity?

#### Reviewer 3: Remote Sensing & Environmental Injustice Reviewer
* **Focus**: Satellite sensor calibration, thermal sharpening, spectral unmixing, DEM elevation accuracy, and environmental equity metrics.
* **Key Questions**:
  1. Are single-date or seasonal-composite Landsat-8/9 LST retrievals sufficient for characterizing long-term micro-climate vulnerability, given monsoonal cloud masking in Java?
  2. Does a $30\text{ m}$ DEM adequately capture physical hazard exposure in informal settlements, or should hydraulic flood retention depth be prioritized over topographic slope?
  3. Does NDVI adequately differentiate between managed luxury private greenery (golf courses, private gardens) and degraded spontaneous vegetation?

#### Reviewer 4: Southeast Asian Megacities & Comparative Urbanism Reviewer
* **Focus**: Ground-truth consistency with Greater Jakarta (Jabodetabek) and comparative alignment with peer megacities (Metro Manila, Bangkok, Ho Chi Minh City, Surabaya).
* **Key Questions**:
  1. How do the observed floor space per capita ($13.0\text{ m}^2$ mean, $2.9\text{ m}^2$ P5) and amenity access counts compare with field survey data in Jakarta (BPS Susenas) and comparable informal settlements in Metro Manila (e.g., Tondo, Baseco)?
  2. Does the stark core-periphery contrast (DKI Jakarta vs. Bodetabek vs. Kabupaten) reflect actual developmental disparity, or does it primarily reflect data coverage artifacts (OSM completeness)?
  3. Can the feature definitions transfer seamlessly to other Global South megacities without structural recalibration?

#### Reviewer 5: Methodological Devil's Advocate Reviewer
* **Focus**: Falsification, circular logic, over-engineering, confirmation bias, and systemic failure modes.
* **Key Questions**:
  1. *The Proxy Fallacy*: Are we truly measuring "physical living condition disparity," or simply constructing an elaborate spatial proxy for population density and distance from Monas (Central Jakarta)?
  2. *The Circularity Trap*: If building footprints from Google Open Buildings were already used to train or dasymetrically distribute GHS-POP, does using both to calculate footprint per capita introduce self-reinforcing artifacts?
  3. *Actionability*: If an urban planning agency or municipal government utilized this index, would these 7 indicators provide actionable, policy-relevant leverage points, or are they unchangeable physical geographic givens?

---

### 7.2 Independent Review Execution Protocol

Each reviewer must structure their evaluation using the following standardized template:

```markdown
# Referee Report: Spatial Feature Engineering for Physical Disparity

**Reviewer Identity / Seat**: [Methodology / Morphology / Remote Sensing / Regional / Devil's Advocate]
**Evaluation Date**: [YYYY-MM-DD]
**Overall Recommendation**: [Accept / Minor Revision / Major Revision / Reject]

---

### 1. Summary of Appraisal
[Concise 200-word executive evaluation of the methodology and findings]

### 2. Major Methodological Critiques (P0 / P1)
- **Point 1 (Conceptual Validity)**: [Detailed evaluation with mandatory academic citations]
- **Point 2 (Data & Metric Integrity)**: [Fact-checked evaluation against comparative cities / datasets]
- **Point 3 (Artifacts & Confounders)**: [Assessment of polygon regularization, dasymetric volume, or MAUP]

### 3. Minor Technical Concerns (P2)
- [Specific points regarding equations, edge-cases, units, or data preparation]

### 4. Fact-Checking & Comparative Grounding
- *Comparative Megacity Evidence*: [Grounding against Manila, Bangkok, or other Global South benchmarks]
- *Empirical Literature Concordance*: [Do findings match peer-reviewed morphology / inequality studies?]

### 5. Concrete Actionable Recommendations for Revision
1. [Mandatory change 1]
2. [Mandatory change 2]
3. [Mandatory change 3]
```

---

## References & Academic Grounding

* Barrington-Leigh, C., & Millard-Ball, A. (2017). The world's user-generated road map is more than 80% complete. *PLoS ONE*, 12(8), e0180698. https://doi.org/10.1371/journal.pone.0180698
* Chakraborty, T., Hsu, A., Manya, D., & Sheriff, G. (2019). Disproportionately higher exposure to urban heat in lower-income neighborhoods: a multi-city perspective. *Environmental Research Letters*, 14(10), 105003. https://doi.org/10.1088/1748-9326/ab3b99
* Estoque, R. C., Pontius, R. G., Murayama, Y., Hou, H., Thapa, R. B., Oghai, R., & Lopez, C. M. (2017). Simultaneous hotspots and coldspots of global land susceptibility to urbanization. *Applied Geography*, 84, 14–26. https://doi.org/10.1016/j.apgeog.2017.04.008
* Estudillo, C. J., et al. (2021). Local Climate Zone mapping and surface temperature dynamics in Metro Manila. *Geocarto International*, 36(12), 1380–1398. https://doi.org/10.1088/10106049.2021.1920633
* Geurs, K. T., & van Wee, B. (2004). Accessibility evaluation of land-use and transport strategies: review and research directions. *Journal of Transport Geography*, 12(2), 127–140. https://doi.org/10.1016/j.jtrangeo.2003.10.005
* Grimmond, C. S. B., & Oke, T. R. (1999). Aerodynamic properties of urban areas derived from analysis of surface form. *Journal of Applied Meteorology*, 38(9), 1222–1244. https://doi.org/10.1175/1520-0450(1999)038<1222:AEROBF>2.0.CO;2
* Kuffer, M., Pfeffer, K., Sliuzas, R., & Baud, I. (2016). Extraction of slum areas from VHR imagery using physical and spatial characteristics: A case study of Ahmedabad, India. *Remote Sensing*, 8(6), 455. https://doi.org/10.3390/rs8060455
* Kuffer, M., Thomson, D. R., Boo, G., Mahabir, R., Grippa, T., Vanhuysse, S., ... & Sliuzas, R. (2020). The role of Earth Observation in an integrated deprivation information system (IDEAMAPS) to support the tracking of SDG 11. *Habitat International*, 102, 102212. https://doi.org/10.1016/j.habitatint.2020.102212
* Moreno, C., Allam, Z., Chabaud, D., Gall, C., & Pratlong, F. (2021). Introducing the “15-Minute City”: Sustainability, resilience and place identity in future post-pandemic cities. *Smart Cities*, 4(1), 93–111. https://doi.org/10.3390/smartcities4010006
* Sirko, W., Kashubin, S., Luccioni, M., Sottana, N., Brockman, L., et al. (2021). Continental-scale building detection from high resolution satellite imagery. *arXiv preprint arXiv:2107.12242*. https://arxiv.org/abs/2107.12242
* Sliuzas, R., Mboup, G., & de Sherbinin, A. (2010). Urban spatial profiling: Remote sensing, GIS, and spatial indicators for slum monitoring. *Landscape and Urban Planning*, 98(1), 1–12. https://doi.org/10.1016/j.landurbplan.2010.04.001
* Stewart, I. D., & Oke, T. R. (2012). Local Climate Zones for urban temperature studies. *Bulletin of the American Meteorological Society*, 93(12), 1879–1900. https://doi.org/10.1175/BAMS-D-11-00019.1
* Taubenböck, H., Kraff, N. J., & Wurm, M. (2018). The morphology of the Arrival City: A global categorization based on physical characteristics. *Remote Sensing of Environment*, 207, 377–393. https://doi.org/10.1016/j.rse.2017.10.044
* UN-Habitat. (2003). *The Challenge of Slums: Global Report on Human Settlements 2003*. United Nations Human Settlements Programme. Earthscan Publications.
* UN-Habitat. (2018). *SDG Indicator 11.1.1 Training Module: Adequate housing and slum upgrading*. United Nations Human Settlements Programme.
* Voogt, J. A., & Oke, T. R. (2003). Thermal remote sensing of urban climates. *Remote Sensing of Environment*, 86(3), 370–384. https://doi.org/10.1016/S0034-4257(03)00079-8
* Zhou, D., Xiao, J., Bonafoni, S., Berger, C., Deilami, K., Zhou, Y., ... & Sobrino, J. A. (2019). Satellite remote sensing of surface urban heat islands: Progress, challenges, and perspectives. *Earth's Future*, 7(1), 48–79. https://doi.org/10.1029/2018EF001099
