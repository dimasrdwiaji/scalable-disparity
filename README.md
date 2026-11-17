# Mapping Micro-Scale Intra-Urban Physical Deprivation, Inequality & Spatial Boundaries (GeoAI Framework)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A reproducible, open-data **GeoAI framework** for detecting micro-scale intra-urban physical deprivation, environmental inequality, and formal–informal settlement boundaries in Global South cities where fine-grained municipal cadastres and commercial imagery are scarce or closed-source.

> [!NOTE]
> **Project Revision Status (2026-11-15):** Following the November 10 editorial audit (`editorial_decision=major_revision`) and empirical deep dive (`docs/research/deep-dive-2026-11-10/`), the project follows the **Option A** specification in [options_memo.md](file:///c:/Users/Dimas%20RD/Documents/projects/phys_living_index/docs/research/deep-dive-2026-11-10/options_memo.md). Legacy `src/` and `configs/` modules remain scheduled for Stage 3–5 updates to match this specification.

---

## 🎯 Overview

Across Global South megacities such as DKI Jakarta, master-planned luxury developments and gated clusters routinely stand directly beside dense informal *kampungs*. Detecting these fine-scale disparities and boundaries is essential for equitable infrastructure targeting and heat mitigation, yet local registries and commercial high-resolution data are often incomplete or closed-source—requiring open global Earth observation and spatial geometry. At the same time, off-the-shelf open proxies (`GHS-POP` per-capita floor space, `VIIRS` nightlights, coarse air/thermal grids, unmasked building coverage, and raw POI counts) frequently break down at neighborhood scale due to coarse resolution, scaling with gross urban density, or service-proximity inversion in mixed-use cores.

The revised **Option A** design addresses this through three integrated stages:
* **Per-Dimension Physical & Environmental Evaluation**: Uses residential-masked building grain (`res_share_lt50`), nearest-neighbor spacing (`res_nn_p25`), conditional residential share (`ghs_res_share`), prospective `10 m` Sentinel-2 GLCM roof-material texture, Sentinel-2 canopy (`NDVI`), and multi-year `100 m` Landsat 8/9 **intra-urban heat anomaly** (`ΔLST`), assessing how each variable independently explains distinct facets of neighborhood disparity.
* **Non-Compensatory Inequality & Excluded Accessibility**: Aggregates separately validated Built-Form and Green-Thermal dimensions cleanly, quantifies city-wide dispersion via urban-masked H3 **Gini, Lorenz curves, and Spatial Palma Ratio**, and excludes cumulative/gravity service accessibility (`Overture`/`OSM` POIs), `OSM` parks, flood hazard, and `Meta RWI` (Section 2 vets accessibility out because slums physically sit near services while open POI data lack financial affordability/quality attributes; `OSM` is retained strictly for non-residential polygon masking).
* **Benchmarked Spatial Boundary Detection (`GAT-AE`)**: Evaluates an unsupervised `SpatialGATAutoencoder` ($d=2$) on the H3 Res-8 grid (`~531 m` edge) directly against classical spatial statistics (`Local Moran's I` / feature gradients) under spatially blocked cross-validation.

---

## 🏗️ System Architecture (Revised Option A)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    1. OPEN GLOBAL DATA INGESTION (Intra-Urban Extent)                   │
│  • Open Building Footprints (Google / Vida) ──> Masked via 21,135 OSM Non-Res Zones     │
│  • EC JRC GHSL (ghs_res_share) ──> Urban Mask & Residential/Industrial Separation       │
│  • Sentinel-2 10m (NDVI + Candidate Masked GLCM Roof Texture)                           │
│  • Multi-Year Landsat 8/9 Tier-1 (100m Clear-Sky Composite LST; No 1km MODIS Fallback)  │
│  • Overture Maps / OSM (Context-Only Typology Layer; Excluded from Deprivation Score)   │
└────────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────▼────────────────────────────────────────────┐
│               2. H3 RES-8 FEATURE MATRIX (~0.74 km², ~531 m Edge Length)                │
│  [Core Built Form]     res_share_lt50 (<50 m² share) | res_nn_p25 (packing) | [res_share]│
│  [Core Micro-Env]      Sentinel-2 NDVI | Intra-Urban Landsat 8/9 ΔLST Anomaly           │
│  [Prospective Cand.]   Masked 10m Sentinel-2 GLCM (pending c5 density-orthogonality)    │
│  ==> Domain-First Validation & Non-Compensatory Aggregation (Mazziotta–Pareto Style)    │
└────────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      ▼                                             ▼
┌───────────────────────────────────────────┐ ┌───────────────────────────────────────────┐
│  3. INEQUALITY, TYPOLOGY & VALIDATION     │ │ 4. BENCHMARKED BOUNDARY MODEL (STAGE 4)   │
│  • H3 Gini, Lorenz, Spatial Palma Ratio   │ │ • GAT-AE (d=2) on orthogonalized matrix   │
│    (strictly inside urban built mask)     │ │ • Tested under spatially blocked CV       │
│  • Context-Only Typology (Access x Stress)│ │ • Must beat Local Moran's I / gradients   │
│  • Labels (Val Only): DKI Pergub 90       │ │   on verified RW boundaries (else defer)  │
│    (KAT 1–4), Stratified Karawang, Ext.   │ └───────────────────────────────────────────┘
└───────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
phys_living_index/
├── configs/
│   └── default.yaml                      # Spatial bounds, feature & model config (pending sync)
├── data/                                 # Raw, interim, and processed H3 tables (git-ignored)
├── docs/
│   ├── adr/                              # Architecture Decision Records
│   ├── research/deep-dive-2026-11-10/    # Literature map, dataset audit, screens & Option A memo
│   ├── reviews/                          # Stage 3 editorial review package & author triage
│   └── research_plan.md                  # Synchronized Option A implementation plan
├── manuscript/
│   └── 01_introduction.md                # Revised introduction aligned with Option A
├── src/
│   ├── data/                             # Open EO / building / VGI extraction
│   ├── features/                         # H3 Res-8 aggregation & domain normalization
│   ├── models/                           # SpatialGATAutoencoder & spatial baselines
│   ├── analysis/                         # Gini / Lorenz / Palma inequality & typologies
│   └── validation/                       # Known-group & ordinal validation (Pergub 90 / Kotaku)
├── tests/                                # Pytest automated test suite
├── GLOSSARY.md                           # Updated domain terminology (retired terms noted)
└── README.md
```

---

## 🚀 Quickstart & Setup

This repository uses [`uv`](https://docs.astral.sh/uv/) for Python dependency management.

```powershell
cd "c:\Users\Dimas RD\Documents\projects\phys_living_index"
uv venv
uv pip install -e ".[dev]"
uv run pytest -v
```

### Key Documentation & Research Records
* **Workstream D Options Memo (Settled Spec)**: [options_memo.md](file:///c:/Users/Dimas%20RD/Documents/projects/phys_living_index/docs/research/deep-dive-2026-11-10/options_memo.md)
* **Literature Review Blueprint**: [literature_review_blueprint.md](file:///c:/Users/Dimas%20RD/Documents/projects/phys_living_index/docs/research/deep-dive-2026-11-10/literature_review_blueprint.md)
* **Verified Citation Ledger**: [references_verified.md](file:///c:/Users/Dimas%20RD/Documents/projects/phys_living_index/docs/research/deep-dive-2026-11-10/references_verified.md)
* **Pilot Feature Screens**: [pilot_screens.md](file:///c:/Users/Dimas%20RD/Documents/projects/phys_living_index/docs/research/deep-dive-2026-11-10/pilot_screens.md)
* **Research Implementation Plan**: [docs/research_plan.md](file:///c:/Users/Dimas%20RD/Documents/projects/phys_living_index/docs/research_plan.md)
* **Domain Vocabulary**: [GLOSSARY.md](file:///c:/Users/Dimas%20RD/Documents/projects/phys_living_index/GLOSSARY.md)
