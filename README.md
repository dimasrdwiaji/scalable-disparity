# Physical Living Standard Index (PLSI) & Micro-Scale Spatial Disparity

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A reproducible, cloud-native **GeoAI framework** for mapping and explaining micro-scale physical living standards and spatial segregation in the Global South without reliance on administrative census aggregates or fragile volunteered geographic tags.

---

## 🎯 Overview

Existing measures of socioeconomic disparity (such as official Gini coefficients or survey poverty rates) suffer from three critical bottlenecks:
1. **Administrative Aggregation Blindness**: National statistical agencies (e.g., Indonesia's *Badan Pusat Statistik* / BPS) aggregate data at municipal (*Kabupaten/Kota*) levels, completely masking intra-city micro-segregation where impoverished informal settlements (*kampungs*) and master-planned luxury estates coexist within hundreds of meters of each other.
2. **Volunteered Geographic Information (VGI) Tagging Fragility**: Standard open accessibility studies rely on raw OpenStreetMap (OSM) attribute tags (`building=yes`, missing `operator:type=public`), which suffer from severe volunteer bias and missing data in the Global South.
3. **The Relative Comparison Trap**: Existing machine-learning wealth products (e.g., Meta's Relative Wealth Index / RWI) are normalized as intra-country relative z-scores, preventing direct absolute physical comparisons across borders.

This framework generates two globally comparable, continuous spatial surfaces across any bounding box:
* **Layer 1: The Absolute Physical Living Standard Index (PLSI)**: A continuous, universally benchmarked metric ($0.0$ to $1.0$) built on the **UN-Habitat $9.0\text{ m}^2$ minimum shelter standard**, **Overture Maps 15-minute cumulative amenity choice**, **environmental health (vegetation, heat, air quality)**, and **VIIRS nighttime energy radiance**.
* **Layer 2: The Spatial Disparity & Segregation Surface**: Derived through an **Unsupervised Graph Attention Autoencoder (GAT-AE)** on the Uber H3 grid (~460 m resolution), where the latent space discovers organic neighborhood typologies and the reconstruction error pinpoints micro-segregation friction borders.

---

## 🏗️ System Architecture

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
│  X2: Cumulative Walk Amenities: Count of Schools, Clinics, Parks, Food (15-min walk)    │
│  X3: Economic Energy Radiance: VIIRS Radiance per Capita                                │
│  X4: Environmental Canopy: Sentinel-2 NDVI (0 to 1)                                     │
│  X5: Thermal Comfort Index: Inverted Landsat/Open-Meteo Land Surface Temperature (LST)  │
│  X6: Air Purity Index: Inverted PM2.5 Exposure against WHO Guidelines                   │
│  ==> Universal Min-Max Normalization to [0, 1] per Feature                              │
└────────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────▼────────────────────────────────────────────┐
│              3. UNSUPERVISED GRAPH AUTOENCODER (PyTorch Geometric on H3 Graph)           │
│  • Nodes: H3 Hex Cells (Feature matrix X in R^{N x 6})                                  │
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

## 📁 Repository Structure

```
phys_living_index/
├── assets/
│   ├── figures/             # Diagram slides and publication-grade maps
│   └── diagrams/            # Architecture excalidraw schematics
├── configs/
│   └── default.yaml         # Spatial bounds, feature parameters, model hyperparams
├── data/
│   ├── raw/                 # Downloaded raw partitions (git-ignored)
│   ├── interim/             # Intermediate H3 intersections (git-ignored)
│   └── processed/           # Final feature matrices & model outputs (git-ignored)
├── docs/
│   ├── adr/                 # Architecture Decision Records (ADRs)
│   ├── research_plan.md     # Full scientific methodology and mathematical plan
│   ├── literature_review_benchmarking.md # Primary literature review and comparison
│   └── handoff.md           # Agent handoff notes
├── src/
│   ├── data/                # Cloud-native S3 / DuckDB data extraction
│   ├── features/            # 15-min isochrones, H3 binning, universal scaling
│   ├── models/              # PyTorch Geometric SpatialGATAutoencoder & training
│   ├── analysis/            # Spatial Gini, Palma Ratio, HDBSCAN typologies
│   └── validation/          # Meta RWI correlation & BPS SUSENAS zonal audit
├── tests/                   # Pytest automated test suite
├── GLOSSARY.md              # Domain terminology reference
├── pyproject.toml           # Project dependencies managed via uv
└── README.md
```

---

## 🚀 Quickstart & Setup

This repository uses [`uv`](https://docs.astral.sh/uv/) for fast, reproducible Python dependency management.

### 1. Install `uv` & Dependencies

```powershell
# Clone or navigate to the directory
cd "c:\Users\Dimas RD\Documents\projects\phys_living_index"

# Create virtual environment and sync dependencies
uv venv
uv pip install -e ".[dev]"
```

### 2. Run Test Suite

```powershell
uv run pytest
```

### 3. Key Documentation & References
* **Research Implementation Plan**: [docs/research_plan.md](file:///c:/Users/Dimas%20RD/Documents/projects/phys_living_index/docs/research_plan.md)
* **Literature Review & Benchmarking**: [docs/literature_review_benchmarking.md](file:///c:/Users/Dimas%20RD/Documents/projects/phys_living_index/docs/literature_review_benchmarking.md)
* **Architecture Decision Records**: [docs/adr/0001-h3-gat-ae-unsupervised-disparity.md](file:///c:/Users/Dimas%20RD/Documents/projects/phys_living_index/docs/adr/0001-h3-gat-ae-unsupervised-disparity.md)
* **Domain Vocabulary**: [GLOSSARY.md](file:///c:/Users/Dimas%20RD/Documents/projects/phys_living_index/GLOSSARY.md)
