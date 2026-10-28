# Project Handoff: Scalable GeoAI for Physical Living Standards & Micro-Scale Spatial Disparity

**Date:** October 28, 2026  
**Target:** Next AI Agent / Research Pair Programmer  
**Location:** `%TEMP%\HANDOFF_GEOAI_SPATIAL_DISPARITY.md`  

---

## 1. Project Background & Context

* **User**: MSc graduate from ITC, University of Twente (specialized in Geo-informatics / spatial optimization). Background in multimodal accessibility (GTC, waiting time penalties, 2SFCA competition) in Greater Jakarta.
* **Goal**: Build and validate an end-to-end, cloud-native **GeoAI framework** producing:
  1. A publication-grade preprint manuscript for submission to *EarthArXiv* / *Computers, Environment and Urban Systems (CEUS)*.
  2. An open-source, cloud-native portfolio piece demonstrating advanced spatial data science (DuckDB Spatial, GeoParquet, PyTorch Geometric, Uber H3) for top PhD applications (ITC Twente, TU Delft, NUS) and international policy organizations (UN-Habitat, World Bank).
* **Core Problem Solved**:
  - Administrative Gini/poverty blindness (BPS municipal aggregations mask sub-kilometer kampung/luxury segregation).
  - VGI tagging fragility (in Indonesia, >95% of OSM buildings are tagged `building=yes`; volunteer POIs have heavy digital bias).
  - The relative comparison trap (Meta RWI uses intra-country relative z-scores, preventing absolute physical comparisons across countries).

---

## 2. Settled Methodology & Key Artifacts

All core design decisions have been settled through iterative grilling and literature benchmarking. **Do not redesign these core components**; reference the existing artifacts:

1. **Formal Implementation Plan**:
   - Path: [`research_plan_spatial_disparity_geoai.md`](file:///C:/Users/Dimas%20RD/.gemini/antigravity/brain/ecf500e3-2cd4-4343-a9ab-e2de20a84561/research_plan_spatial_disparity_geoai.md)
   - Contains: System architecture, mathematical formulations ($R_{\text{space}}$, cumulative walking accessibility, universal scaling, GAT-AE architecture, HDBSCAN clustering, BPS zonal aggregation).
2. **Literature Review & Benchmarking Analysis**:
   - Path: [`literature_review_benchmarking.md`](file:///c:/Users/Dimas%20RD/Documents/projects/wip/docs/literature_review_benchmarking.md)
   - Contains: Detailed comparison against Meta RWI (Chi et al. 2022 *PNAS*), Jean et al. (2016 *Science*), Kuffer et al. (*CEUS*), Biljecki et al. (2023, 2024), Weiss et al. (*Nature* 2018), and 5 literature-adopted enhancements.
3. **Executive Presentation Slide**:
   - Path: [`research_framework_slide.png`](file:///c:/Users/Dimas%20RD/Documents/projects/wip/research_framework_slide.png) (and artifact copy [`geoai_research_framework_slide_1792263231578.jpg`](file:///C:/Users/Dimas%20RD/.gemini/antigravity/brain/ecf500e3-2cd4-4343-a9ab-e2de20a84561/geoai_research_framework_slide_1792263231578.jpg)).

### Core Methodological Guardrails:
* **Grid**: Continuous Uber H3 Resolution 8 (~460 m edge length, ~0.74 km²) without artificial urban-rural masking.
* **Feature Vector ($X \in \mathbb{R}^{N \times 6}$)**:
  1. $R_{\text{space}}$: Observed residential floor area per capita divided by UN-Habitat $9.0\text{ m}^2$ minimum shelter threshold.
  2. $A_{\text{amenity}}$: 15-minute cumulative pedestrian walking reach (Overture Places & Base).
  3. $E_{\text{night}}$: VIIRS nighttime energy radiance per capita.
  4. $\text{NDVI}$: Sentinel-2 vegetative greenness.
  5. $\text{LST}_{\text{inv}}$: Inverted Landsat / Open-Meteo Land Surface Temperature.
  6. $\text{PM25}_{\text{inv}}$: Inverted $PM_{2.5}$ air pollution against WHO guidelines.
* **GAT Autoencoder Bottleneck ($d=2$) & Segregation Friction**:
  - Graph is constructed using pure geometric H3 adjacency.
  - Reconstruction loss ($\|X - \hat{X}\|^2$) spikes precisely at gated community walls and severance boundaries.
  - HDBSCAN on latent space $Z$ uncovers organic neighborhood typologies.
* **Dual Validation**:
  - Global: Continuous grid correlation against Meta RWI (2.4 km).
  - Local: Population-weighted zonal aggregation into BPS administrative units regressed against official BPS SUSENAS poverty/Gini rates.

---

## 3. Environment & Tools Status

* **OS**: Windows 11. Shell: PowerShell.
* **Workspace**: `c:\Users\Dimas RD\Documents\projects\wip`
* **Python Tooling**: `uv` package manager is installed and verified at `C:\Users\Dimas RD\.local\bin\uv.exe`.
  - In PowerShell commands, use: `$env:PATH = "$HOME\.local\bin;" + $env:PATH; uv run ...`

---

## 4. Immediate Next Steps for Next Session

1. **Repository Scaffolding**:
   - Initialize `pyproject.toml` using `uv` with required dependencies: `duckdb`, `geopandas`, `h3`, `pyarrow`, `torch`, `torch-geometric`, `hdbscan`, `scikit-learn`, `requests`, `fsspec`.
   - Create directories: `src/data/`, `src/features/`, `src/models/`, `src/analysis/`, `src/validation/`, `tests/`, `configs/`.
2. **Implement Cloud-Native Ingestion (`src/data/`)**:
   - `ingest_overture.py`: DuckDB spatial script to query Overture Places (`education.school`, `healthcare.hospital`, `healthcare.clinic`, `commercial.supermarket_grocery`) and Base (`park`, `sports_pitch`) from AWS S3 over the Jabodetabek bounding box.
   - `ingest_buildings.py`: Ingestion & clipping of Google Open Buildings v3 (confidence $\ge 0.65$) masked by JRC GHS-BUILT-C residential raster.
3. **Feature Engineering (`src/features/build_features.py`)**:
   - Build H3 Res-8 hexagonal feature matrix and compute 15-min pedestrian isochrones.

---

## 5. Suggested Skills for Next Agent

When taking over, call the Skill tool for:
- **`codebase-design`**: Guide deep modular design for the data ingestion and model inference pipeline.
- **`tdd`**: Write unit and integration tests (e.g. verifying DuckDB spatial queries, H3 sufficiency bounds, and GAT convergence) test-first.
- **`research`**: If looking up specific cloud endpoints (e.g. Overture S3 partitions or Copernicus open access hubs).
- **`pr`**: When formatting initial commits and pull request summaries.
