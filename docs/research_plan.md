# Implementation Plan: Mapping Micro-Scale Intra-Urban Physical Deprivation, Inequality & Spatial Boundaries (Option A)

> [!IMPORTANT]
> **Plan Revision Notice (2026-11-15):** This plan supersedes the pre-review 10D `PLSI` + `Meta RWI` + `BPS SUSENAS` plan following the Stage 3 editorial review (`major_revision`) and empirical screening in [pilot_screens.md](./research/deep-dive-2026-11-10/pilot_screens.md) and [options_memo.md](./research/deep-dive-2026-11-10/options_memo.md). `src/` and `configs/` updates will be implemented against this synchronized specification.

---

## 1. Goal & Revised Scientific Framing

Intra-urban physical deprivation in Global South megacities—such as Jakarta, where gated luxury estates and formal clusters stand directly beside dense informal *kampungs*—requires fine-grained detection using open global data because local cadastres and commercial imagery are scarce, incomplete, or closed-source. Off-the-shelf open proxies (`GHS-POP` floor space, `VIIRS` nightlights, coarse air/thermal grids, unmasked building coverage, and raw 15-minute POI counts) fail at neighborhood scale due to coarse resolution, density scaling, or proximity inversion.

This framework builds a **reproducible, open-data GeoAI pipeline** on H3 Resolution-8 hexes ($\approx 0.737\text{ km}^2$, $\approx 531\text{ m}$ edge) designed to:
1. **Evaluate each selected physical dimension individually (`RQ1`)**: Measure how effectively residential-masked building morphology (`res_share_lt50`, `res_nn_p25`, conditional `ghs_res_share`), prospective roof-material texture (`10 m` Sentinel-2 GLCM), urban canopy (`NDVI`), and multi-year `100 m` Landsat 8/9 **intra-urban surface heat** (`ΔLST`) separately detect informal deprivation and explain distinct facets of neighborhood disparity without collapsing into macro urban density (`PC1` reduced from `48.64%` to `29.93%` on `CAND_5D_CORE`).
2. **Quantify intra-urban inequality and profiles (`RQ2`)**: Combine separately validated Built-Form and Green-Thermal domains via non-compensatory aggregation paired with `greenR`-inspired H3 dispersion metrics (**Gini, Lorenz curves, Spatial Palma Ratio**) strictly within the urban mask (excluding `Overture`/`OSM` service proximity/accessibility indices completely due to missing affordability attributes and proximity inversion).
3. **Detect formal–informal boundaries and test transferability (`RQ3`)**: Benchmark an unsupervised `SpatialGATAutoencoder` ($d=2$) against classical spatial statistics (`Local Moran's I` / LISA and linear feature gradients) under spatially blocked cross-validation across `DKI Pergub 90`, density-stratified `Karawang`, and an external held-out city.

---

## 2. Retired & Out-of-Scope Elements

The following components from earlier drafts are **permanently excluded** from model inputs and validation:
* `R_space` / `UN-Habitat 9.0 m²` (`GHS-POP` vs. residential `GHS` volume $R^2 = 0.976$ circularity; `DKI AUC = 0.5269, p = 0.210`).
* `VIIRS` nighttime lights ($\rho = 0.82$ with density; inverted AUC `0.87/0.80/0.67` in Karawang).
* `PM2.5` / `NO2` / `Open-Meteo` (coarse `~5.5 km–0.4°` resolution cannot resolve neighborhood differences).
* `GLO-30` slope (reads formal high-rise canopy), `H90/H180` orientation entropy (`p = 0.186`), `res_comp_med`, `dead_end_share`, and unmasked `plan_area_frac` (`DKI AUC = 0.4798`).
* `osm_park400_2sfca` (dropped per author decision due to secondary-city OSM sparsity: `Karawang median = 0.0`).
* **Flood hazard** (`water_frequency`, `MNDWI`, `HAND`) dropped completely.
* `Meta RWI` (excluded from both inputs and validation) and `Depok Kotaku` (whole-municipality polygons `199.772 km²` vs. `199.511 km²`).

---

## 3. Pipeline Architecture & Module Plan

### Stage 1–2: Open Ingestion & Residential/Urban Masking (`src/data/`)
* **Buildings**: Extract open footprints (`Google-Microsoft Open Buildings` / `Vida`) and mask out non-residential areas using `OpenStreetMap` non-residential polygons (`21,135` zones in the Jabodetabek screen).
* **Urban Built Extent & Land-Use Share**: Extract `GHSL` residential share (`ghs_res_share`) and define the contiguous intra-urban built mask so rural/floodplain pixels are excluded from urban thermal baselines and inequality curves.
* **Optical & Thermal EO**:
  * `Sentinel-2`: Clear-sky `NDVI` + test extraction of `10 m` residential-masked GLCM texture for roof-material heterogeneity.
  * `Landsat 8/9` (`100 m` Tier-1): Build a **multi-year clear-sky seasonal composite** to lift Tier-1 thermal coverage well above the cached `55.8%` single-year DKI rate; **do not fall back to `1 km` MODIS Tier-3**, which degrades intra-urban heat discrimination (`0.7349 -> 0.5919`).
* **Context-Only VGI (`Overture` / `OSM`)**: Ingest POIs, transit stops, and road hierarchy strictly as a descriptive typology layer outside the deprivation model.

### Stage 3: Density-Orthogonal Feature Matrix & Composite (`src/features/`)
| Domain | Feature | Status | Target Role |
| :--- | :--- | :--- | :--- |
| Built Form | `res_share_lt50` (`< 50 m²` masked share) | **Core** | Primary micro-grain indicator |
| Built Form | `res_nn_p25` (25th-pct masked spacing) | **Core** | Interstitial packing indicator |
| Built Form | `ghs_res_share` (masked residential share) | **Conditional** | Industrial/port encroachment (urban core only) |
| Roof Texture | `s2_res_glcm_*` (`10 m` masked S2 GLCM) | **Candidate** | Must pass `c5` density-orthogonality screen |
| Micro-Env | `ndvi` (Sentinel-2 canopy) | **Core** | Urban vegetative deficit |
| Micro-Env | `dlst_intra` / `dlst_regency_urban` (`100 m` L8/9) | **Core** | Intra-urban thermal anomaly (urban baseline) |

* **Non-Compensatory Aggregation**: Validate Built-Form and Green-Thermal dimensions separately prior to composite aggregation using penalty-adjusted non-compensatory formulation (`Mazziotta–Pareto` style) so a surplus in one dimension cannot mask extreme deprivation in another.

### Stage 4: Benchmarked Spatial Boundary Modeling (`src/models/`)
* **Model**: PyTorch Geometric `SpatialGATAutoencoder` ($d = 2$ latent bottleneck, configurable `in_channels` matching the validated `~4–5D` orthogonal matrix) over pure H3 geometric adjacency.
* **Spurious-Baseline Safeguards & Go/No-Go Gate**:
  * Evaluate exclusively under **spatially blocked cross-validation** (`R17`).
  * Benchmark `GAT-AE` node reconstruction error ($\|x_i - \hat{x}_i\|^2$) and edge attention contrast ($1 - \alpha_{ij}$) directly against **univariate/bivariate `Local Moran's I` (LISA)** and **linear feature gradients** on verified `DKI Pergub 90` RW boundary seams.
  * **Stop/Go Rule**: Retain `GAT-AE` as a primary contribution only if it measurably outperforms classical spatial baselines; otherwise defer Stage 4 and foreground the de-confounded spatial morphology, typology, and inequality results.

### Stage 5: Inequality Analytics & Multi-Tier Validation (`src/analysis/`, `src/validation/`)
* **City-Wide Inequality (`greenR`-inspired)**: Compute H3 **Gini coefficient, Lorenz curves, and Spatial Palma Ratio** over the built-form, green-thermal, and composite deprivation surfaces strictly inside the urban built mask.
* **Context Typology Matrix**: Cross physical deprivation against descriptive `Overture`/`OSM` access context to separate *Inner-City Crowded Kampungs* from *Formal Enclaves* and *Peri-Urban Settlements*.
* **Known-Group & External Validation**:
  1. **Primary Intra-Urban Benchmark**: `DKI Jakarta Pergub 90` (`438` Mainland RWs: binary ROC-AUC, 5-municipality stratification, and `KAT 1–4` ordinal Spearman correlation).
  2. **Regime & MAUP Stress Test**: `Karawang Kotaku` stratified by density tercile (`T1` rural floodplain vs. `T3` dense core), documenting the `2.6 ha` RT vs. `~531 m` H3 scale gap.
  3. **External Out-of-Region City**: Evaluate generalization on at least one independent Indonesian or LMIC city outside Jabodetabek.

---

## 4. Verification & Key Limitations

1. **Automated Unit & Screen Checks**: Verify residential mask integrity, non-null Tier-1 L8 thermal coverage, density-orthogonality ceilings (`|rho|` and `PC1` variance share), blocked-CV non-leakage, and deterministic non-compensatory score bounds.
2. **Known Scope Limitations**: Global open physical features reliably target *dense urban morphological and micro-environmental deprivation*; they cannot capture household overcrowding (`GHS-POP` circularity), indoor housing quality, financial barriers to services, or rural floodplain poverty regimes where vegetative cover inverts.
