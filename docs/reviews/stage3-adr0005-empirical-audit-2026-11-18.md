# Stage 3 Empirical Audit & Supervisor Review (ADR 0005, Tickets 01–05)

**Date:** 2026-11-18  
**Branch / Commits Audited:** `main` (`8d5286c` for Tickets 01–04; `2bfed31` for Ticket 05)  
**Scope:** Real-data verification across Mainland DKI Jakarta (`admin_boundaries_study_area.geojson`), Bodetabek, and Karawang Regency (`17,154` H3 Resolution-8 cells; `9,641` urban-masked cells post-`b_dedup`), plus live Earth Engine diagnostics on Mainland DKI (`854` urban cells).

---

## 1. Executive Summary

Evaluating Stage 3 (Tickets 01–05) against real Jabodetabek + Karawang data confirms that the four core `ADR 0005` indicators (**`res_share_lt50`**, **`res_nn_p25`**, **`ndvi`**, and **`dlst_local_ring_k5`**) behave coherently within Mainland DKI Jakarta and cleanly capture regional urban–rural structural differences. However, the audit also uncovered **two critical methodological findings** before Stage 4 execution:

1. **Jurisdiction-Boundary Confounding Changed Candidate Screening:** Testing `DKI Pergub 90` against a rectangular bounding box (`dki.total_bounds`, `1,843` cells spilling into Tangerang, Depok, and Bekasi) allowed `ghs_res_share` to falsely pass Gate 2 (`rho = +0.105` $\to$ `promoted = True`). When properly scoped strictly to **Mainland DKI Jakarta** (`n = 852`), **all three candidate features fail 3-gate screening** (`s2_res_glcm_contrast` `AUC = 0.581`, `rho_bld = -0.523`, `3/4` folds; `s2_res_glcm_homogeneity` `AUC = 0.507`, `p = 0.710`; `ghs_res_share` `rho_paf = +0.384`, `KAT_rho = -0.074`). Active modeling should lock cleanly at **`D = 4`**.
2. **Coarse `OSM industrial` Masking Excluded 8 Valid DKI *Kampungs*:** Eight Pergub 90 slum hexes (`>= 10%` overlap) — including two **`Berat`** (Severe) cells in Penjaringan RW 017 (`187` and `88` buildings) and dense *kampung* pockets in Sunter Jaya (`450` buildings), Rawa Terate (`268`), Kalibaru (`185`), and Cilincing (`134`, `76.9% < 100 m²`, median `39.7 m²`) — were zeroed out to `residential_building_count = 0` solely because `OSM landuse=industrial` removes all enclosed buildings regardless of footprint size.

---

## 2. Detailed Empirical Findings

### 2.1 Masking & Jurisdictional Scope (`Ticket 01` & `Ticket 05`)

- **Regional Mask Coverage (`17,154` total H3 Res-8 cells):**
  - Legacy `population >= 300` mask: `9,345` cells (`54.5%`).
  - `urban_built_up_mask` (`GHS-SMOD {21, 22, 23, 30}` $\land$ `residential_building_count >= 1`): `9,650` cells pre-`b_dedup`, **`9,641` cells** (`56.2%`) after overlapping-OSM deduplication (`b_dedup`) and confidence filtering (`>= 0.65`).
  - Pre-`b_dedup` shift vs. `pop >= 300`: dropped `688` mostly rural `SMOD {11, 12, 13}` sprawl cells and `85` zero-residential-building cells; excluded `134` non-residential urban `SMOD` industrial/vacant cells; gained `993` suburban built cells (median `68` residential buildings, median `133.7 persons/km²`).
- **Validation Label Coverage:**
  - **Karawang Kotaku (`>= 10%` overlap):** `14/14` (`100%`) covered (`5` excluded cells had only `0.05%–8.1%` rural edge slivers in `SMOD {11, 12}`).
  - **DKI Pergub 90 (`>= 10%` overlap):** `363/370` (`98.1%`) covered pre-`b_dedup`; `8` mainland DKI slum hexes excluded post-`b_dedup`, **all 8** flagged solely by `OSM` `industrial` zones (`Penjaringan RW 017` `[Berat]`, `Sunter Jaya RW 011`, `Rawa Terate RW 001`, `Kalibaru RW 010`, `Cilincing RW 008`, `Koja RW 007`).

### 2.2 `Small-Footprint Residential Buildings` (`Ticket 02`, Post-`b_dedup`)

Across `9,641` urban-masked cells (`data/raw/buildings.parquet` + `osm_nonres_zones.parquet`):

| Metric | Valid `n` | Mean | `P05` | `P25` | Median | `P75` | `P95` | Min / Max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `res_share_lt50` | `9,641` | `0.3603` | `0.199` | `0.280` | `0.335` | `0.405` | `0.621` | `0.000` / `1.000` |
| `res_share_lt60` | `9,641` | `0.4456` | `0.266` | `0.359` | `0.421` | `0.505` | `0.713` | `0.000` / `1.000` |
| `res_nn_p25` (m) | `9,615` (`26` NaN) | `9.458` | `5.847` | `7.343` | `8.104` | `8.798` | `10.518` | `2.401` / `825.501` |
| `residential_building_count` | `9,641` | `938.0` | `46.0` | `279.0` | `607.0` | `1,355.0` | `2,819.0` | `1.0` / `6,628.0` |

- **Deduplication Fix Impact (`b_dedup`):** Before deduplicating overlapping `OSM` polygon joins in SQL, `res_nn_p25` had an artificial `0.000 m` minimum from duplicated building rows; post-`b_dedup`, minimum spacing rose cleanly to **`2.401 m`**.
- **Extreme Tails (`~1%`):** High-share outliers (`res_share_lt50 >= 0.95`) and `> 25 m` spacing outliers (`1.03%`) occur almost exclusively in sparse peri-urban cells (`median 4–5` residential footprints).

### 2.3 Intra-DKI Mainland vs. Multi-Regional Contrasts (`Tickets 02–05`)

Evaluating indicators strictly inside Mainland DKI Jakarta (`n = 851–853`; `350` slum, `503` non-slum; `728` cached thermal):

| Indicator | DKI Slum vs. Non-Slum Med | `AUC` | `PR-AUC` | `rho_paf` | `rho_cnt` | `KAT_rho` *(Ordinal)* |
|---|---:|---:|---:|---:|---:|---:|
| `res_share_lt50` | `0.353` vs. `0.288` | `0.652 (+)` | `0.561` | `-0.220` | `+0.184` | **`+0.208`** |
| `res_share_lt60` | `0.445` vs. `0.375` | `0.652 (+)` | `0.551` | `-0.188` | `+0.241` | **`+0.221`** |
| `res_nn_p25` | `6.868` vs. `7.364 m` | `0.651 (-)` | `0.560` | `-0.141` | `-0.467` | **`-0.191`** |
| `ndvi` | `0.181` vs. `0.216` | `0.623 (-)` | `0.516` | `-0.454` | `-0.433` | `-0.131` |
| `dlst_local_ring_k5` *(2023 cache)* | `+0.214` vs. `-0.188 K` | `0.566 (+)` | `0.478` | `+0.499` | `+0.518` | **`+0.122`** |
| *`dlst_city_median` (sensitivity)* | `+5.766` vs. `+5.082 K` | `0.574 (+)` | `0.477` | `+0.547` | `+0.605` | `+0.015` |

**Sub-Regional Medians Across Urban-Masked Cells (`n = 9,641`):**

| Regime | `res_share_lt50` | `res_nn_p25` (m) | `ndvi` | `dlst_local_ring_k5` (K) | `ghs_res_share` | `plan_area_frac` | `res_bld_cnt` |
|---|---:|---:|---:|---:|---:|---:|---:|
| `DKI_Slum` | `0.353` | `6.868` | `0.181` | `+0.214` | `0.867` | `0.228` | `2,119` |
| `DKI_NonSlum` | `0.288` | `7.364` | `0.216` | `-0.188` | `0.935` | `0.232` | `2,171` |
| `Bodetabek_Core` | `0.341` | `7.712` | `0.362` | `+0.068` | `1.000` | `0.081` | `881` |
| `Bogor` | `0.337` | `8.267` | `0.512` | `-0.121` | `1.000` | `0.059` | `581` |
| `Karawang` | `0.332` | `8.531` | `0.411` | `-0.026` | `1.000` | `0.034` | `349` |

- **Key Physical Takeaway:** In DKI, slums and formal blocks share almost identical macro ground coverage (`plan_area_frac = 0.228 vs 0.232`) and building counts (`2,119 vs 2,171`), differing in micro-grain (`res_share_lt50`, `res_nn_p25`) and green/thermal stress. In Bogor/Karawang, `res_share_lt50` is similarly elevated (`0.33–0.34`), **but** accompanied by wide spacing (`8.3–8.5 m`), high greenery (`ndvi = 0.41–0.51`), low coverage (`0.03–0.06`), and cool local rings (`-0.03 to -0.12 K`). Feeding all four ungrouped channels into `GAT-AE` is therefore essential to prevent rural/peri-urban small cottages from conflating with dense urban *kampungs*.

### 2.4 Thermal Compositing Diagnosis (`Ticket 03`)

- Old cached 2023 `30 m` `landsat.parquet` (`n = 9,650` urban) had `919` (`9.5%`) `tier=0` NaNs and `3` `< 290 K` cold cloud-leak outliers producing a `-53.83 K` `dlst_local_ring_k5` tail.
- Live GEE testing of `100 m` multi-year (`2021–2025`, `Jun–Oct`) over `854` DKI Mainland cells eliminated all `< 290 K` cloud leaks (`min = 304.09 K`, `max = 328.47 K`), yielding `771/854` (`90.3%`) strict pass. Of the `83` failing cells, **`68` failed solely `n_clear < 3`** (`valid_frac` `P10 = 0.988`, `P05 = 0.904`), proving seasonal cloud duration—not spatial pixel fraction—was the bottleneck.
- Expanding the dry-season window slightly to **`May–Nov` (`2021–2025`)** increased strict pass rate to **`794/854` (`93.0%`)**, with **`853/854` (`99.9%`)** holding valid thermal pixels.
- Meanwhile, `dlst_city_median` artificially shifts all of DKI to `+5.08 to +5.77 K` (due to cooler Bogor hinterlands) and loses severity gradient (`KAT_rho = +0.015` vs `+0.122` for `dlst_local_ring_k5`).

### 2.5 Full DKI Mainland Candidate Screening (`Tickets 04–05`, Live GEE `n = 852`)

- An initial `250`-cell H3-ordered sample inflated `s2_res_glcm_contrast` to `AUC = 0.852` (`rho = -0.290`) by contrasting northern coastal blocks against southern estates. Across all `852` DKI Mainland cells:
  - `s2_res_glcm_contrast`: `AUC = 0.581 (+)`, `p = 5.17e-5`, `rho = -0.523` (`residential_building_count`) / `-0.342` (`plan_area_frac`), `3/4` spatial folds $\to$ **`promoted = False`**. At `10 m` resolution (`100 m²` pixels), sub-pixel `< 50 m²` *kampung* roofs average into uniform gray textures (`rho < 0` with count), whereas setbacks and warehouses drive contrast.
  - `s2_res_glcm_homogeneity`: `AUC = 0.507 (+)`, `p = 0.710`, `2/4` folds $\to$ **`promoted = False`**.
  - `ghs_res_share`: `AUC = 0.659 (-)`, `p = 2.61e-15`, `rho = +0.378` (`count`) / **`+0.384` (`plan_area_frac`)**, `4/4` folds, `KAT_rho = -0.074` $\to$ **`promoted = False`**.

---

## 3. Recommendations Prior to Stage 4 (`Tickets 06–09`)

1. **Lock Active Model Channels at `D = 4` & Remove `10 m` GLCM Reduction from `build_sentinel2`:** Keep `[res_share_lt50, res_nn_p25, vegetation_ndvi, dlst_local_ring_k5]`. Retaining `10 m` GLCM fails Gate 2/3 empirically on DKI Mainland and slows full-region Earth Engine exports; report `ghs_res_share` (and the negative GLCM finding) analytically in text/screening tables rather than feeding either into `GAT-AE` (`Stage 4`).
2. **Enforce Provincial Boundary Masking on City-Specific Evaluation (`run_stage5` / Candidate Screen):** Always clip `DKI Pergub 90` benchmarking and candidate screening to Mainland DKI polygons (`admin_boundaries_study_area.geojson`) rather than `dki.total_bounds` to eliminate unsurveyed Bodetabek leakage.
3. **Add a Cluster-Guarded Small-Home Exemption Inside `OSM industrial` Zones (`build_buildings`):** If an `OSM industrial` polygon inside an H3 cell contains a dense small-house cluster (e.g., `>= 10` footprints `< 100 m²`), retain `< 100 m²` footprints as residential while continuing to exclude `>= 200 m²` industrial halls—rescuing mixed port/factory-belt *kampungs* (`Penjaringan RW 017 [Berat]`, `Cilincing RW 008`, `Sunter Jaya RW 011`, `Rawa Terate RW 001`, `Kalibaru RW 010`) without admitting isolated factory sheds.
4. **Widen Landsat Tier 3 Window to `May–Nov` (`2021–2025`) & Refresh Local Caches Before Stage 4:** Updates `compositing.landsat.tiers[2]` in `configs/default.yaml` to cover `May–Nov` (`93.0%` strict pass, `99.9%` non-null) and refreshes `data/interim/layers/{buildings,landsat,sentinel2}.parquet` cleanly with zero `< 290 K` cloud leaks.


---

## 4. Post-Fix Verification & Rerun Audit (2026-11-18)

Following implementation of all four recommendations (plus an extra `min_lst_k = 290.0 K` pixel filter discovered when the initial regional `May–Nov` rebuild surfaced a corrupt `150.0 K` `LC08_122064_20240706` frame over coastal Tarumajaya, Bekasi yielding `-49.7 K` anomalies), all Stage 3 caches (`sentinel2`, `landsat`, `ghs_residential`, `buildings`) and derived matrices were rebuilt across all `17,154` regional H3 cells and re-audited.

### 4.1 Code & Test Verification
- **Lint (`uv run ruff check src/ tests/`):** `All checks passed!`
- **Test Suite (`uv run pytest -v`):** **`110 passed, 3 deselected, 2 warnings`** (added 4 unit tests covering `industrial_cluster_min_count` exemption vs isolated factory sheds, `build_sentinel2` GLCM skip + `v2` `D = 4` lock, `landsat_lst_collection` `min_lst_k` forwarding, and `scope_gdf_to_jurisdiction` / `compute_h3_kotaku_spatial_overlap(..., jurisdiction_gdf=...)` boundary masking).

### 4.2 Rebuilt Cache Health & Coverage (`17,154` total $\to$ `9,718` urban $\to$ `9,252` modelled)
- **Active Matrix:** Locked at **`D = 4`** (`[res_share_lt50, res_nn_p25, vegetation_ndvi, dlst_local_ring_k5]`), `promoted_channels = []`, `outside_reference_channels = []` (`clip_flag_share` `< 0.9%` on every bound across all 4 channels).
- **Industrial-Cluster Exemption (`>= 10` footprints `< 100 m²`):** Rescued mixed port/factory-belt *kampungs*, raising urban-masked coverage from `9,641` to **`9,718`** cells and Mainland DKI `Pergub 90` coverage (`>= 10%` overlap) to **`355 / 356` (`99.7%`)** — rescuing `Penjaringan RW 017 [Berat]`, `Sunter Jaya RW 011`, `Rawa Terate RW 001`, `Kalibaru RW 010`, and `Cilincing RW 008`, leaving only `1` port-edge sliver (`Koja RW 007`, `15` total buildings). Karawang `Kotaku` coverage remains **`14 / 14` (`100%`)**.
- **Thermal Recovery & Cloud-Leak Elimination (`min_lst_k = 290.0 K`, `May–Nov` `2021–2025` Tier 3):**
  - Urban-masked `lst_k` (`n = 9,275`, `95.4%` valid): **`min = 297.031 K`**, `P05 = 305.393 K`, `median = 311.223 K`, `max = 328.466 K` (**zero `< 290 K` artifacts**).
  - `dlst_local_ring_k5` (`n = 9,267`): **`min = -9.374 K`**, `P05 = -3.165 K`, `median = -0.055 K`, `P95 = +3.386 K`, `max = +13.989 K`.
  - Tier breakdown on urban cells (`lst`): **Tier 1 (`79.5%`), Tier 2 (`13.7%`), Tier 3 (`2.3%`, `tier3_share_flag = False`), `tier = 0` missing (`4.6%`)**; Sentinel-2 `ndvi` achieved **`100.0%` Tier 1** (`0` missing).

### 4.3 Post-Fix Empirical Metrics & Readiness for Stage 4 (`Tickets 06–09`)
- **Mainland DKI Standalone Performance (`n = 860` urban cells; `355` slum, `505` non-slum; `800` thermal):**
  - `res_share_lt50`: `AUC = 0.663`, `PR = 0.572`, `rho_cnt = +0.088`, `KAT_rho = +0.187` (`0.362` vs `0.292`).
  - `res_nn_p25`: `AUC = 0.640`, `PR = 0.552`, `rho_cnt = -0.486`, `KAT_rho = -0.190` (`6.907 m` vs `7.352 m`).
  - `ndvi`: `AUC = 0.625`, `PR = 0.521`, `rho_cnt = -0.414`, `KAT_rho = -0.186` (`0.179` vs `0.214`).
  - `dlst_local_ring_k5`: `AUC = 0.551`, `PR = 0.460`, `rho_cnt = +0.559`, `KAT_rho = +0.096` (`+0.178 K` vs `-0.168 K`; `dlst_city_median` remains confounded at `+5.610 / +5.067 K` with `KAT_rho = -0.033`).
  - `ghs_res_share` (candidate audit): `AUC = 0.660 (-)`, `rho_cnt = +0.376` (`Gate 2 False`), `KAT_rho = -0.067` $\to$ `promoted = False`.
- **Inter-Channel Independence (`n = 9,252` scaled urban cells):** Max pairwise `|Spearman rho|` across the 4 active channels is **`0.456`** (`res_nn_p25` vs `vegetation_ndvi`), confirming low redundancy ahead of Stage 4 `SpatialGATAutoencoder` (`4 -> 2`) modeling.
- **Verdict:** **Stage 3 approved (`GO`)** to advance to Stage 4–5 implementation (`Tickets 06–09`).
