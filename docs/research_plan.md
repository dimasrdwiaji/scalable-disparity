# Implementation Plan: Scalable GeoAI for Mapping and Explaining Micro-Scale Physical Living Standards and Spatial Disparity

## Goal Description

Existing measures of socioeconomic disparity (such as official national Gini coefficients or survey-based poverty rates) suffer from three critical bottlenecks:
1. **Administrative Aggregation Blindness**: National statistical agencies (e.g., Indonesia's *Badan Pusat Statistik* / BPS) aggregate data at provincial or municipal (*Kabupaten/Kota*) levels, completely masking intra-city micro-segregation where impoverished informal settlements (*kampungs*) and master-planned luxury estates coexist within hundreds of meters of each other.
2. **Volunteered Geographic Information (VGI) Tagging Fragility**: Standard open accessibility studies rely on raw OpenStreetMap (OSM) attribute tags (e.g., `operator:type=public`, `name~Puskesmas`), which suffer from severe contributor bias and missing data in the Global South.
3. **The Relative Comparison Trap**: Existing machine-learning wealth products (like Meta's Relative Wealth Index / RWI) are normalized as intra-country z-scores, preventing direct, absolute physical comparisons across borders (e.g., comparing rural Indonesia directly to urban Europe).

This project designs, simulates, and deploys a **reproducible, cloud-native GeoAI framework** that generates two globally comparable, continuous spatial surfaces across any bounding box:
* **Layer 1: The Absolute Physical Living Standard Index (PLSI)**: A continuous, universally benchmarked metric ($0.0$ to $1.0$) built on the **UN-Habitat $9.0\text{ m}^2$ minimum shelter standard**, **Overture Maps 15-minute cumulative amenity choice**, **environmental health (vegetation, heat, air quality)**, and **VIIRS nighttime energy radiance**.
* **Layer 2: The Spatial Disparity & Segregation Surface**: Derived through an **Unsupervised Graph Attention Autoencoder (GAT-AE)** on the Uber H3 grid (~460 m resolution), where the latent space discovers organic neighborhood typologies and the reconstruction error pinpoints micro-segregation friction borders.

---

## User Review Required

> [!IMPORTANT]
> **Settled Design Decisions (Post-Grilling Consensus):**
> 1. **Multi-Dimensional Feature Expansion**: To prevent the autoencoder from learning a trivial identity shortcut, the feature vector is expanded to 6 dimensions combining living space, cumulative amenities, nighttime energy, vegetative greenness (NDVI), thermal heat stress (LST), and air quality ($PM_{2.5}$).
> 2. **Universal Benchmark Normalization**: Raw features are scaled to $[0, 1]$ using international physiological and human settlement standards (UN-Habitat, WHO air quality, and saturation lighting baselines), ensuring cross-country comparability.
> 3. **Pure Geometric H3 Graph Topology**: H3 adjacency edges are retained across physical boundaries. This ensures the GNN expects spatial continuity so that its **reconstruction loss ($\|X - \hat{X}\|^2$) spikes precisely along gated community walls and severance barriers**, automatically detecting micro-segregation seams.
> 4. **Geometric Centroid Isochrone Routing**: 15-minute pedestrian catchments are calculated from the mathematical center of each H3 Res-8 cell snapped to Overture Transportation lines, ensuring uniform global scalability.
> 5. **Dual-Layer Validation Strategy**:
>    * *Global Grid Concordance*: Continuous spatial cross-correlation against Meta's Relative Wealth Index (RWI) at 2.4 km across Indonesia and international transfer regions (e.g., Metro Manila).
>    * *Official Government Audit*: Population-weighted zonal aggregation of H3 metrics into BPS administrative polygons, regressed against BPS SUSENAS poverty rates and municipal Gini ratios.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           1. CLOUD-NATIVE DATA INGESTION (AWS S3)                       │
│  • Google Open Buildings v3 (2.5D Heights & Polygons) ──> GeoParquet                    │
│  • EC JRC GHS-BUILT-C_FUN (10m Residential vs. Non-Residential Mask) ──> Cloud GeoTIFF  │
│  • Overture Maps Foundation (Places [POIs] & Base [Designated Parks]) ──> GeoParquet    │
│  • Overture Maps Transportation (Street Network Line Geometry) ──> GeoParquet            │
│  • WorldPop 100m Unconstrained Population Grid ──> Cloud GeoTIFF                         │
│  • NASA Black Marble VIIRS Annual Cloud-Free Radiance (VNP46A2) ──> Cloud GeoTIFF       │
│  • Sentinel-2 NDVI, Landsat LST, and Open-Meteo / Sentinel-5P PM2.5 ──> GeoTIFF / API   │
└────────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────▼────────────────────────────────────────────┐
│                    2. H3 DISCRETE GLOBAL GRID (Res 8: ~0.74 km², ~460m)                 │
│  X1: Space Sufficiency Ratio: R_space = (Observed Residential Area / Cap) / 9.0 m²      │
│  X2: Built-Up Density: Sentinel-2 NDBI (Roof packing & impervious surfaces)             │
│  X3: Cumulative Walk Amenities: Count of Schools, Clinics, Parks, Food (15-min walk)    │
│  X4: Unpaved Infrastructure: Sentinel-2 BSI (Bare soil & unpaved dirt roads)           │
│  X5: Economic Energy Radiance: VIIRS Radiance per Capita                                │
│  X6: Environmental Canopy: Sentinel-2 NDVI (-1.0 to 1.0)                                │
│  X7: Thermal Comfort Index: Inverted Landsat Land Surface Temperature (LST in K)         │
│  X8: Drainage & Water Exposure: Sentinel-2 MNDWI (Open drainage & flood risk)           │
│  X9: Fine Particulate Air Purity: Inverted PM2.5 Exposure against WHO Guidelines        │
│  X10: Multi-Pollutant Air Purity: Inverted Official European/US Air Quality Index (AQI) │
│  ==> Universal Min-Max Normalization to [0, 1] per Feature in Stage 3                   │
└────────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────▼────────────────────────────────────────────┐
│              3. UNSUPERVISED GRAPH AUTOENCODER (PyTorch Geometric on H3 Graph)           │
│  • Nodes: H3 Hex Cells (Feature matrix X in R^{N x 10})                                 │
│  • Edges: Pure H3 Geometric Adjacency (A in R^{N x N})                                   │
│  • Encoder: 2-layer Graph Attention Network (GAT) compressing X -> Z (Bottleneck d=2)   │
│  • Decoder: Reconstructs feature matrix X_hat and adjacency A_hat                       │
└────────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      ▼                                             ▼
┌───────────────────────────────────────────┐ ┌───────────────────────────────────────────┐
│     OUTPUT A: TYPOLOGY DISCOVERY          │ │   OUTPUT B: MICRO-SEGREGATION DETECTION   │
│  • HDBSCAN on Latent Embeddings (Z)       │ │ • High Reconstruction Error ||X - X_hat||²│
│  • Discovers Organic Neighborhood Types:  │ │ • Highlights sharp contrast seams where   │
│    - Dense Core Kampung (Crowded, Choices)│ │   slums and luxury gated estates collide  │
│    - Peri-Urban Sprawl (Space, Desert)    │ │   across physical walls and barriers      │
│    - Master-Planned Enclave (Space+Choice)│ └───────────────────────────────────────────┘
│    - Multi-Deprived Pocket (No Space/Ch.) │
└───────────────────────────────────────────┘
```

---

## Detailed Implementation Components

### Component 1: Cloud Data Engineering & Feature Ingestion (`src/data/`)

#### [NEW] `src/data/ingest_overture.py`
Queries Overture Maps GeoParquet directly from AWS S3 using DuckDB spatial without downloading raw OSM dumps:
```python
import duckdb

def fetch_overture_amenities(bbox: tuple, output_parquet: str):
    """
    Queries Overture Maps Places & Base themes directly from AWS S3.
    bbox: (min_lon, min_lat, max_lon, max_lat)
    """
    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial;")
    con.execute("INSTALL httpfs; LOAD httpfs;")
    
    query = f"""
    COPY (
        SELECT id, names.primary AS name, categories.main AS category, geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/2024-*/theme=places/type=place/*', hive_partitioning=true)
        WHERE bbox.xmin >= {bbox[0]} AND bbox.xmax <= {bbox[2]}
          AND bbox.ymin >= {bbox[1]} AND bbox.ymax <= {bbox[3]}
          AND categories.main IN (
              'education.school', 'healthcare.hospital', 
              'healthcare.clinic', 'commercial.supermarket_grocery'
          )
        UNION ALL
        SELECT id, names.primary AS name, subtype AS category, geometry
        FROM read_parquet('s3://overturemaps-us-west-2/release/2024-*/theme=base/type=land_use/*', hive_partitioning=true)
        WHERE bbox.xmin >= {bbox[0]} AND bbox.xmax <= {bbox[2]}
          AND bbox.ymin >= {bbox[1]} AND bbox.ymax <= {bbox[3]}
          AND subtype IN ('park', 'sports_pitch', 'recreation_ground')
    ) TO '{output_parquet}' (FORMAT PARQUET);
    """
    con.execute(query)
```

#### [NEW] `src/data/ingest_buildings.py`
Extracts Google Open Buildings v3 polygons and 2.5D heights, intersecting them with the European Commission's GHS-BUILT-C_FUN residential raster to eliminate factories, warehouses, and transport terminals.

---

### Component 2: H3 Feature Engineering & Normalization (`src/features/`)

#### [NEW] `src/features/build_features.py`
Harmonizes and standardizes features onto H3 Resolution 8 cells (~0.74 km²):
1. **Space Sufficiency Ratio ($R_{\text{space}}$)**:
   $$\text{Observed Living Floor Area per Capita}_i = \frac{\sum_{b \in \text{RES}} \text{Footprint}_b \times \max\left(1, \left\lfloor \frac{\text{Height}_b}{3.0} \right\rfloor\right)}{\max(\text{WorldPop}_i, 1)}$$
   $$R_{\text{space}, i} = \frac{\text{Observed Living Floor Area per Capita}_i}{9.0\text{ m}^2}$$
2. **Cumulative 15-Minute Walk Opportunities ($A_{\text{amenity}}$)**:
   * Build pedestrian network graph from Overture Transportation.
   * Compute walking network isochrone of $1,000\text{ m}$ (~15 min at $4\text{ km/h}$) from each geometric hex centroid.
   * Sum total reachable Overture schools, clinics, designated parks, and food markets (raw count reflecting choice abundance).
3. **Economic Energy Radiance ($E_{\text{night}}$)**:
   $$E_{\text{night}, i} = \frac{\text{Mean VIIRS Radiance}_i}{\max(\text{WorldPop}_i, 1)}$$
4. **Environmental Context**:
   * $\text{NDVI}_i$: Mean Sentinel-2 vegetative greenness index.
   * $\text{LST\_inv}_i$: Inverted Land Surface Temperature scaled against heat stress limits.
   * $\text{PM25\_inv}_i$: Inverted $PM_{2.5}$ concentration scaled against the WHO $15\,\mu\text{g/m}^3$ annual threshold.
5. **Universal Min-Max Scaling**: All 6 dimensions normalized to $[0.0, 1.0]$.

---

### Component 3: Graph Autoencoder Engine (`src/models/`)

#### [NEW] `src/models/gnn_autoencoder.py`
Builds the PyTorch Geometric Graph Attention Autoencoder with a strict bottleneck ($d=2$):
```python
import torch
import torch.nn as nn
from torch_geometric.nn import GATConv

class SpatialGATAutoencoder(nn.Module):
    def __init__(self, in_channels=6, hidden_dim=16, latent_dim=2):
        super().__init__()
        # Graph Encoder (Spatial message passing over H3 adjacency)
        self.conv1 = GATConv(in_channels, hidden_dim, heads=2, concat=True)
        self.conv2 = GATConv(hidden_dim * 2, latent_dim, heads=1, concat=False)
        
        # Decoder (Reconstructing feature matrix)
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, in_channels),
            nn.Sigmoid()  # Bound reconstructed features to [0, 1]
        )

    def encode(self, x, edge_index):
        x = torch.relu(self.conv1(x, edge_index))
        z = self.conv2(x, edge_index)
        return z

    def decode(self, z):
        return self.decoder(z)

    def forward(self, x, edge_index):
        z = self.encode(x, edge_index)
        x_hat = self.decode(z)
        return z, x_hat
```

* **Loss Formulation**:
  $$\mathcal{L} = \underbrace{\| X - \hat{X} \|^2}_{\text{Feature Reconstruction Loss}} + \lambda \underbrace{\mathcal{L}_{\text{BCE}}(A, \sigma(Z Z^T))}_{\text{Spatial Graph Adjacency Loss}}$$
* **Segregation Mapping Metric**:
  $$\text{Friction Score}_i = \| x_i - \hat{x}_i \|^2$$

---

### Component 4: Typology Discovery & Disparity Mapping (`src/analysis/`)

#### [NEW] `src/analysis/typologies.py`
Runs **HDBSCAN** on the latent representations ($Z$) to autonomously discover natural neighborhood archetypes without pre-specifying cluster counts.

#### [NEW] `src/analysis/disparity_metrics.py`
* **Local Focal Disparity Surface**: Computes the focal Gini coefficient of the latent living standard index within a $k=3$ H3 neighborhood ring (~3.5 km).
* **Regional Lorenz Curve & Gini**: Population-weighted Gini of the Physical Living Standard Index.

---

### Component 5: Dual-Layer Validation Engine (`src/validation/`)

#### [NEW] `src/validation/evaluate_rwi.py`
Calculates continuous pixel-to-pixel spatial Pearson and Spearman rank correlation between the unsupervised $\text{PLSI}$ and Meta's Relative Wealth Index at 2.4 km resolution across all evaluated regions.

#### [NEW] `src/validation/audit_bps.py`
Executes population-weighted zonal aggregation of H3 metrics into BPS *Kabupaten/Kota* boundaries and performs OLS regression against official BPS SUSENAS poverty rates and municipal Gini ratios:
$$\text{BPS Poverty Rate}_k = \beta_0 + \beta_1 \cdot \overline{\text{PLSI}}_k + \epsilon$$

---

## Verification Plan

### Automated Pipeline Tests
1. **Overture Ingestion Integrity**:
   * Verify DuckDB spatial query returns valid GeoParquet with nonzero rows and valid WGS84 coordinates.
2. **H3 Sufficiency Ratio Bounds**:
   * Unit test verifying that $R_{\text{space}} > 0$, properly masked for zero-population cells.
3. **GNN Convergence Test**:
   * 100-epoch training smoke test on a 500-hex sample to verify that reconstruction loss decreases monotonically ($\Delta \mathcal{L} < 0$).
4. **HDBSCAN Parameter Stability**:
   * Verify that HDBSCAN identifies $\ge 3$ distinct clusters and flags non-residential outliers as noise (`-1`).

### Empirical Validation Strategy
* **Spatial Alignment Verification**: Inspect the segregation friction map in QGIS / Kepler.gl over known border areas (e.g., the boundary wall between BSD City and Kampung Sampora) to confirm that the GNN reconstruction error spikes precisely along physical barriers.
* **BPS SUSENAS Benchmark**: Regress the aggregated municipal Physical Living Standard Index against official BPS poverty rates across the ~15 *Kabupaten/Kota* in the Jabodetabek + Karawang study area (the 14 Jabodetabek administrative units plus Karawang Regency), confirming Pearson $r \ge 0.65$ ($p < 0.001$). (Corrected from an earlier "25+" figure that didn't reconcile with any coherent Jabodetabek-branded area; see `.scratch/project-roadmap/map.md`.)
