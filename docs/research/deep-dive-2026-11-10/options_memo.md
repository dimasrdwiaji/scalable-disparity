# Workstream D: Options Memo & Revised Research Specification (Option A)

**Date:** 2026-11-15  
**Status:** Settled direction (`Option A`), ready to guide downstream doc sync and Stage 3–5 experiments.  
**Predecessors:** [literature_map.md](./literature_map.md) | [dataset_inventory.md](./dataset_inventory.md) | [pilot_screens.md](./pilot_screens.md) | [literature_review_blueprint.md](./literature_review_blueprint.md)

---

## 1. Locked Strategic Decisions

1. **Construct:** Reframe from *"10-dimensional Physical Living Standard Index (`PLSI`)"* to **Density-Orthogonal Urban Physical Deprivation & Micro-Environmental Injustice** (strictly within the urban built-up extent).
2. **Eliminated Modules (Do Not Re-Introduce):**
   - `R_space` / `UN-Habitat 9.0 m²` (`GHS-POP` vs. `GHS-BUILT-V` `R² = 0.976` circularity; `DKI AUC = 0.5269, p = 0.210`).
   - `VIIRS` nightlights (`rho = 0.82` with density; flipped Karawang AUC `0.87/0.80/0.67`).
   - `PM2.5` / `NO2` / `Open-Meteo` (`Sentinel-5P ~5.5 km` / `0.1–0.4°` too coarse).
   - `GLO-30` slope, `H90/H180`, `res_comp_med`, `dead_end_share`, `plan_area_frac` (`AUC = 0.4798`), and `Meta RWI` (excluded from both inputs and validation).
   - `osm_park400_2sfca` (dropped by author; secondary-city `Karawang median = 0.0`) and **flood hazard / `HAND` / `water_frequency` (dropped completely)**.
   - `Depok Kotaku` baseline (whole-municipality polygons `199.772 km²` vs. city `199.511 km²`).
3. **Role of Service Accessibility (`Overture` / `OSM`):** Removed from the deprivation score; retained strictly as a **descriptive context/typology layer** distinguishing inner-city *kampungs* (service-proximate yet physically/thermally stressed) from formal enclaves and peri-urban settlements.

---

## 2. Candidate Feature Stack (H3 Res-8, `~531 m` edge)

| Domain | Feature | Status | Verified DKI Mainland Screen (`pilot_screens.md`) | Engineering Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **Built Form** | `res_share_lt50` (masked `< 50 m²` share) | **Core** | `AUC = 0.6667 (+)`, `rho_dens = -0.1910`; `KAT rho = +0.2342` | Keep OSM non-res mask (`21,135` zones) |
| **Built Form** | `res_nn_p25` (masked 25th-pct spacing) | **Core** | `AUC_mag = 0.6825 (-)`, `rho_dens = -0.0879`; `Karawang T3 = 0.715` | Keep |
| **Built Form** | `ghs_res_share` (residential built share) | **Conditional** | `strat AUC = 0.6895 (-)` in DKI; flips density sign regionally (`-0.564` vs `+0.388`) | Gate strictly inside urban mask / regime check |
| **Built Form (Roof Texture)** | `s2_res_glcm_*` (`10 m` Sentinel-2 masked GLCM) | **Candidate** | Unscreened (`200×200` thumbnails cached only) | Run full-grid extraction + `c5` density-orthogonality screen |
| **Micro-Environment** | `ndvi` (Sentinel-2 canopy) | **Core** | `AUC_mag = 0.6732 (-)` (`strat = 0.7059`), all 5 DKI municipalities | Mask to intra-urban built extent |
| **Micro-Environment** | `dlst_intra` / `dlst_regency_urban` (`100 m` L8/9) | **Core (Needs Fix)** | `AUC = 0.6765` / `0.7349` on Tier-1 (`n=406`); `KAT rho = +0.2022` | **Mandatory:** Multi-year L8/L9 clear-sky compositing to raise Tier-1 coverage above cached `55.8%` (drop `1 km` MODIS Tier-3 fallback) |

---

## 3. Aggregation, Inequality, & `GAT-AE` Decision Rules

- **Non-Compensatory Scoring:** Validate Built-Form and Green-Thermal domains separately before combining via penalty-adjusted / non-compensatory aggregation ([Mazziotta & Pareto, 2016](https://doi.org/10.1007/s11205-015-0998-2)).
- **Urban Inequality Layer (`greenR`-inspired):** Compute **Gini, Lorenz curves, and Spatial Palma Ratio** over H3 cells strictly within the urban built mask, paired with known-group validation.
- **Stage 4 `GAT-AE` (`d=2`) Go/No-Go Gate:**
  - Train only on the orthogonalized `~4–5D` feature set under **spatially blocked CV (`R17`)**.
  - **Pass criterion:** `GAT-AE` boundary/reconstruction signals must outperform simpler baselines (**`Local Moran's I` / LISA** and **linear feature gradients**) on verified `DKI Pergub 90` RW boundaries. If it fails to beat those baselines, **defer/drop Stage 4** and publish the interpretable spatial morphology + inequality framework.

---

## 4. Validation Design

1. **Primary Benchmark:** `DKI Jakarta Pergub 90` (`438` Mainland RWs: binary discrimination + `KAT 1–4` ordinal Spearman correlation + 5-municipality stratification).
2. **Regime Stress Test:** `Karawang Kotaku` stratified by density tercile (`T1` rural floodplain vs. `T3` dense core), explicitly documenting the `2.6 ha` RT vs. `~531 m` H3 MAUP caveat.
3. **External Hold-Out City:** Add at least **one out-of-region Indonesian or LMIC city** with independent labels before claiming cross-city generalization.

---

## 5. Immediate Next Checklist (Before Editing `src/` or `configs/`)

1. Synchronize framing across [README.md](../../../README.md), [GLOSSARY.md](../../../GLOSSARY.md) (fixing stale `461 m` hex edge -> `~531 m`), [docs/research_plan.md](../../research_plan.md), and [manuscript/01_introduction.md](../../../manuscript/01_introduction.md).
2. Run multi-year `100 m` Landsat 8/9 Tier-1 compositing and `10 m` masked Sentinel-2 GLCM pilot screen (`c5`).
3. Lock external hold-out city dataset and run Stage 4 `GAT-AE` vs. `Local Moran's I` blocked-CV benchmark.
