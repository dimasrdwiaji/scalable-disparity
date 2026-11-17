# Workstream C: Empirical Pilot Screens & Validation Hygiene Report

**Project**: Spatial Physical Living Condition Index (Jabodetabek / Greater Jakarta)  
**Deliverable**: Workstream C — Density-Stratified Empirical Screens, MAUP Audit & Cross-Dimensional Collinearity Diagnostics  
**Date**: 2026-11-11  
**Depends On**: [literature_map.md](file:///C:/Users/Dimas%20RD/Documents/projects/phys_living_index/docs/research/deep-dive-2026-11-10/literature_map.md) | [dataset_inventory.md](file:///C:/Users/Dimas%20RD/Documents/projects/phys_living_index/docs/research/deep-dive-2026-11-10/dataset_inventory.md) | [references_verified.md](file:///C:/Users/Dimas%20RD/Documents/projects/phys_living_index/docs/research/deep-dive-2026-11-10/references_verified.md)

> [!NOTE]
> **Purpose & Epistemic Standard**: All empirical tests in this document operate strictly on cached local project files (without pipeline modifications in `src/` or `configs/`, and without external API downloads). Every candidate signal identified in Workstreams A & B is evaluated for: (1) **within-density-tercile discrimination** against non-circular slum decrees (`dki_rw_kumuh_pergub90`, `kotaku_sk_kumuh_karawang`), (2) **ordinal severity scaling** (`KAT_NUM` 1–4 in DKI; Kotaku `k1_a_p` in Karawang), (3) **MAUP / spatial-support sensitivity**, and (4) **cross-dimensional orthogonality** across all `9,345` residential H3 Res 8 cells. Findings are tagged **`[Established]`** (consistent across density terciles and sensitivity checks), **`[Observed Caveat]`** (significant signal with structural regime/coverage conditionality), **`[Rejected]`** (null or collinear empirically), or **`[Unverified Offline]`** (blocked by missing local cache fields/rasters).

---

## Executive Summary of Empirical Screens

1. **Validation Suite Re-Baselining**:
   * **`[Established]` DKI Pergub 90/2018 (`n = 445` RWs, `438` Mainland)**: Valid intra-urban severity and binary benchmark (`355` primary positive cells at $\ge 10\%$ overlap vs. `373` zero-overlap residential controls; balanced across density terciles).
   * **`[Rejected as Slum Mask]` Depok Kotaku (`kotaku_sk_kumuh_depok.geojson`)**: Total mapped polygon area (`199.772 km²`) equals the entire Kota Depok municipal boundary (`199.511 km²`). These are full-*kelurahan* administrative tracts (`median = 301.0 ha`), not intra-kelurahan physical slum outlines; `rumah > 0` in only `21/63` units (`33.3%`).
   * **`[Observed Caveat]` Karawang Kotaku (`n = 100` RTs, `total = 2.830 km²`)**: Pools two structurally opposing slum typologies—cramped urban cores (`Karawang Barat`, `Cikampek`, `Rengasdengklok`; median footprint $62.2\text{--}63.2\text{ m}^2$) and rural river-floodplain villages (`Teluk Jambe Barat` `k4_p = 100`, `72.7 m²`; `Klari` `83.9 m²`)—creating within-tercile polarity reversals when unstratified. Furthermore, `2.6 ha` RT polygons compared against $100\text{--}750\text{ m}$ (`~170 ha`, `~65×` larger) rings introduce severe MAUP extent bias into distribution entropy and Gini.
2. **Five Validated Orthogonal Physical Signals**:
   * Across DKI Mainland density terciles (`strat_mean_dir_auc`) and Pergub 90 `KAT 1 -> 4` severity grading, only five locally measurable dimensions consistently separate deprived from non-deprived settlements independent of gross building coverage (`residential_plan_area_fraction` itself fails in DKI at `AUC = 0.4798, p = 0.345`):
     1. **Vegetative Shade Deficit (`ndvi`)**: `AUC_mag = 0.6732` (`strat = 0.7059`, lower in all 5 Kotamadya).
     2. **Micro-Scale Structural Packing (`res_nn_p25`)**: 25th-percentile nearest-neighbor residential roof spacing, `AUC_mag = 0.6825` (`strat = 0.6839`), **`rho_dens = -0.0879`**, `KAT wmean rho = -0.2244`.
     3. **Micro-Footprint Grain (`res_share_lt50` / `lt60`)**: `res_share_lt50` `AUC = 0.6667` (`strat = 0.6669`), strongest ordinal RW severity gradient (`share_lt60 rho = +0.2355, p = 6.20e-7`; `share_lt50 rho = +0.2342`), near-zero global density correlation (`ALL_RES rho = -0.101`).
     4. **Landsat-8 Tier-1 Intra-Urban Thermal Disparity (`dlst_regency_urban` / `dlst_intra_s21_k5`)**: Conditional on excluding `1 km` MODIS Tier-3 (`25.3%`) and cloud gaps (`14.6%`) inside DKI (`n = 406`), `dlst_regency_urban` jumps to `AUC = 0.7349` (`strat = 0.7481`, `+0.950 K vs -0.610 K`) and `dlst_intra_s21_k5` rises from `0.5919` (mixed-tier) to `0.6765` (`strat = 0.6739`), remaining positive across all 5 Kotamadya and scaling with RW severity (`rho = +0.2022, p = 5.3e-4` vs. raw `lst_k p = 0.285`).
     5. **Mixed Non-Residential Exposure (`ghs_res_share`)**: `AUC_mag = 0.6855` (`strat = 0.6895`) in DKI, reflecting Pergub 90 RW clustering along mixed industrial/rail/port belts—flagged with a land-use vs. housing-quality distinction.
   * Replacing the Original 7D baseline with the **5-Axis Candidate Core** drops leading `PC1` variance collapse from **`48.64%`** (`n = 8,375`) to **`29.93%`** (`n = 8,333`), distributing variance cleanly across four components (`29.9%, 22.3%, 19.8%, 17.3%, 10.6%`).
3. **Empirically Rejected Hypotheses & Offline Cache Gaps**:
   * **Rejected**: `residential_plan_area_fraction` (DKI `AUC = 0.4798`), `space_sufficiency_ratio` (`0.5269`), vector orientation entropy/disorder (`res_H90_all / res_H180_all / res_disp4_all`: DKI `AUC = 0.528–0.537, p = 0.09–0.19`; `KAT p = 0.29–0.52`), residential `area_gini` (weakened once industrial sheds masked and *inverts negatively* with RW severity `-0.0991`), and **Dual-Channel Accessibility (`A_public` vs `A_comm`)** (sign reversal persists in *both* channels in DKI and Karawang).
   * **Unverified Offline**: Google Open Buildings confidence cutoffs (`100%` of cached `9,643,124` footprints share `confidence == 0.85`), footprint height distribution (`99.68%` have `floor_count == 1` and `99.935%` null `height`), true transit stops / Overture `clinic` (`0` cached rows), and `10 m` Sentinel-2 masked GLCM / Sentinel-1 `VH/VV` (no full-resolution GeoTIFFs cached locally).

---

## 1. Validation Geometry & Local Data Hygiene Audit

Before scoring candidate features, all validation layers (`data/validation/`) and cached input tables were audited in projected UTM Zone 48S (`EPSG:32748`) and exact H3 Resolution 8 geometry (`17,154` study cells: `9,345` `is_residential`, `7,809` non-residential; `smod_code` counts: `{30: 5548, 21: 3635, 11: 3132, 10: 2129, 12: 1992, 23: 413, 22: 188, 13: 117}`).

### 1.1 Validation Polygons & Disqualification Audit

| Benchmark File | Jurisdiction & Scope | Polygon Count & Area (`EPSG:32748`) | Spatial Overlay on H3 Res 8 Grid | Audit Verdict & Guardrails |
| :--- | :--- | :--- | :--- | :--- |
| **`dki_rw_kumuh_pergub90.geojson`** ([`.csv`](file:///C:/Users/Dimas%20RD/Documents/projects/phys_living_index/data/validation/dki_rw_kumuh_pergub90.csv)) | DKI Jakarta (`874` Mainland H3 cells: `860` res, `867` `smod>=21`; excludes Kep. Seribu) | `445` valid RW polygons (`438` Mainland, `7` Kep. Seribu); `1.389–545.110 ha` (`med = 11.035 ha`, `total = 106.998 km²`). `KAT_NUM`: `{1: 129, 2: 202, 3: 99, 4: 15}` (`Mainland: {1: 126, 2: 198, 3: 99, 4: 15}`). | Mainland overlap: `>=0.01%: 487` (`486` res); `>=1%: 456`; `>=5%: 405`; **`>=10%: 356` (`355` res primary pos)**; `>=25%: 218` (all res); `>=50%: 89`; `0%: 386` (**`373` res primary neg**). Buffer `0 < share < 10%`: `131` excluded. | **`[Established]` Primary Intra-Urban Benchmark**: Polygons are RW-scale administrative slum zones (not centroids) spanning all 5 municipalities and carrying 4-tier ordinal severity (`KAT_NUM` 1–4). |
| **`kotaku_sk_kumuh_karawang.geojson`** ([`.csv`](file:///C:/Users/Dimas%20RD/Documents/projects/phys_living_index/data/validation/kotaku_sk_kumuh_karawang.csv)) | Kab. Karawang (`2,609` cells; `1,311` res; `1,451` `smod>=21`; `449` `smod==30`) | `100` RT polygons (`2` invalid geometries repaired via `make_valid()`); `0.546–7.316 ha` (`med = 2.599 ha`, `total = 2.830 km²`) across `8` Kecamatan / `27` Kelurahan. | `share > 0: 64` (`60` res; `59/64` in `smod>=21`: `{30: 43, 21: 14, 23: 2, 12: 3, 11: 2}`); `>=1%: 53`; `>=5%: 28`; `>=10%: 14`; `>=25%: 1`. Urban `smod>=21` res: **`56` pos vs. `1,120` neg** (`1,082` with `res_n_bldg>=20`). | **`[Observed Caveat]` Mixed Dual-Regime Micro-Polygons**: Sub-H3 (`2.6 ha` vs `~75 ha` H3 cell); requires BOTH `smod>=21` urban matching AND matched-area polygon tests (`Section 3`) to control floodplain vs. town split & MAUP. |
| **`kotaku_sk_kumuh_depok.geojson`** ([`.csv`](file:///C:/Users/Dimas%20RD/Documents/projects/phys_living_index/data/validation/kotaku_sk_kumuh_depok.csv)) | Kota Depok (`admin_boundaries`: `199.511 km²`) | `63` polygons across `62` unique `Desa` / `11` `Kecamatan`; `83.585–712.684 ha` (`med = 301.018 ha`), **total area `199.772 km²`**. | Entire city area covered (`100.1%` of municipal extent); `rumah > 0` in only `21/63` polygons (`33.3%`, `median = 0.0`, total `966` houses -> overlaps `96` H3 cells vs. `176` `rumah == 0` cells). | **`[Rejected]` Disqualified as Sub-Kelurahan Physical Mask**: Polygons represent full administrative *kelurahan* bounds rather than delineated slum pockets; unusable as local H3 spatial ground truth. |

* **Auxiliary Pipeline Audit Finding (`Tangerang` Name Disambiguation)**: [`validate_living_space.py`](file:///C:/Users/Dimas%20RD/Documents/projects/phys_living_index/src/phys_living_index/analysis/validate_living_space.py) matches regency names via naive substring/token rules susceptible to conflating *Kota Tangerang* and *Kabupaten Tangerang*; Workstream C strictly disambiguates `regency_std` labels against `admin_boundaries_study_area.geojson` (`20` municipal polygons).

### 1.2 Cached Local Input Telemetry & Unscreenable Blind Spots

Auditing raw/interim pipeline artifacts ([`ingest_buildings.py`](file:///C:/Users/Dimas%20RD/Documents/projects/phys_living_index/src/phys_living_index/data/ingest_buildings.py), [`ingest_overture.py`](file:///C:/Users/Dimas%20RD/Documents/projects/phys_living_index/src/phys_living_index/data/ingest_overture.py), [`stage3_qa.json`](file:///C:/Users/Dimas%20RD/Documents/projects/phys_living_index/data/processed/stage3_qa.json), `buildings.parquet`, `overture_amenities.parquet`, `osm_walk_edges.parquet`) uncovered four hard constraints on what offline validation can and cannot test:

1. **Vector Footprint Confidence & Height Censorship (`buildings.parquet`)**:
   * Total footprints cached: `9,643,124` (`9,635,394` falling inside study H3 cells; `14,541` H3 cells populated; `9,188 / 9,345` residential cells have `>= 20` residential footprints after masking `21,135` `osm_nonres_zones.parquet` polygons).
   * **`[Unverified Offline]` Zero Confidence Variance**: **`100.0%` (`9,643,124 / 9,643,124`)** of cached footprints in Vida `google-microsoft-open-buildings` carry `confidence == 0.85` identically. Sensitivity testing of Google Open Buildings confidence cutoffs (`0.65` vs. `0.70` vs. `0.75`) cannot run without re-pulling native v3 shards.
   * **Minimal Vertical Attribute Fill**: `height` is non-null in only **`6,291` rows (`0.065%`; `height_frac > 0` in only `319 / 9,345` residential cells)**, and `floor_count == 1` across **`9,612,514` rows (`99.68%`)** (Overture attributes inherited selectively into `ob_mean_floors` in `stage3_l3`).
2. **LST Multi-Tier Heterogeneity vs. Clean Sentinel-2 Coverage**:
   * Optical `s2_tier == 1` coverage is effectively complete (`874 / 874 = 100%` in DKI Mainland; `1,311 / 1,311 = 100%` in `Karawang_res`; `9,345 / 9,345 = 100%` across `ALL_RES`).
   * Thermal **`lst_tier` suffers severe Tier-3/missingness degradation in Jakarta**: across `DKI_Mainland (n = 874)`, only **`488` (`55.8%`)** carry `100 m` Landsat 8/9 (`lst_tier == 1`), **`37` (`4.2%`)** carry Tier-2, **`221` (`25.3%`)** fall back to **`1 km` MODIS (`lst_tier == 3`)**, and **`128` (`14.6%`)** are completely missing (`lst_tier == 0`, `NA`). Across `Karawang_res (n = 1,311)`: `{1: 1008 (76.9%), 0: 143 (10.9%), 3: 122 (9.3%), 2: 38 (2.9%)}`. Across `ALL_RES (n = 9,345)`: `{1: 6992 (74.8%), 3: 1200 (12.8%), 0: 894 (9.6%), 2: 259 (2.8%)}`.
3. **Missing Full-Resolution Sentinel-2 / Sentinel-1 GeoTIFFs**:
   * Cached rasters in `data/raw/*.tif` are `200×200` preview thumbnails; zero `10 m` Sentinel-2 BOA stacks or Sentinel-1 IW GRD rasters exist locally. Masked `10 m` optical GLCM and Sentinel-1 `VH/VV` texture cannot be screened offline.
4. **Overture Places Schema v2 / Category Completeness (`overture_amenities.parquet`)**:
   * Cached table holds `173,820` POIs across **`32` unique categories** (`A_public = 49,962`, `A_comm = 105,238`, `A_relig = 18,620`). Despite ingestion query configuration, **`clinic` returned `0` rows** (`HEALTH_CATS` only holds `hospital` and `pharmacy`), and **no public transit stops** (`bus_stop`, `rail_station`, `TransJakarta` shelters) were ingested.

---

## 2. DKI Jakarta Mainland — Density-Stratified Screen & Severity Gradient

Primary binary labels restrict strictly to **Mainland Jakarta residential cells** (`dki_slum_share >= 0.10`, `n = 355` vs. `dki_slum_share == 0.0`, `n = 373`; intermediate overlap `0 < share < 10%`, `n = 131` excluded as boundary buffer; evaluated also at `>= 25%`, `n = 218` vs. `373`). Density terciles split evenly across `residential_plan_area_fraction`: `T1_low [0.0000, 0.1839]` (`122/121`), `T2_mid [0.1841, 0.2688]` (`116/126`), `T3_high [0.2688, 0.4817]` (`117/126`).

### 2.1 Candidate Feature Performance Within & Across Density Terciles

| Feature | Axis / Source | `auc_raw` | `auc_mag` (`dir`) | Med (Pos vs. Neg) | `rho_dens` | `auc_T1` | `auc_T2` | `auc_T3` | `strat_mean_dir_auc` | `p`-val (MWU) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`ndvi`** | S2 Canopy Deficit | `0.3268` | **`0.6732 (-)`** | `0.1798` vs `0.2277` | `-0.4152` | `0.2677` | `0.2410` | `0.3736` | **`0.7059`** *(0.7165†)* | `6.23e-16` | **`[Established]`** |
| **`ghs_res_share`** | GHSL Non-Res Share | `0.3145` | **`0.6855 (-)`** | `0.8638` vs `0.9440` | `+0.3828` | `0.2762` | `0.2731` | `0.3822` | **`0.6895`** *(0.7036†)* | — | **`[Observed Caveat]`** |
| **`res_nn_p25`** | Res Footprint NN 25th | `0.3175` | **`0.6825 (-)`** | `6.854` vs `7.458 m` | **`-0.0879`** | `0.3135` | `0.2852` | `0.3495` | **`0.6839`** *(0.7011†)* | `3.20e-17` | **`[Established]`** |
| `all_nn_p25` | Unmasked NN 25th | `0.3323` | `0.6677 (-)` | — | `-0.2173` | `0.3363` | `0.2954` | `0.3504` | `0.6726` | — | Superseded by `res_` |
| `all_share_lt50` | Unmasked Grain `<50m²` | `0.6682` | `0.6682 (+)` | — | `-0.2025` | `0.6622` | `0.6562` | `0.6848` | `0.6677` | — | Superseded by `res_` |
| **`res_share_lt50`** | Res Grain **`< 50 m²`** | `0.6667` | **`0.6667 (+)`** | `35.05%` vs `28.10%` | **`-0.1910`** | `0.6520` | `0.6631` | `0.6855` | **`0.6669`** *(0.6820†)* | `1.28e-14` | **`[Established]`** |
| **`res_share_lt60`** | Res Grain `< 60 m²` | `0.6658` | **`0.6658 (+)`** | — | **`-0.1688`** | `0.6560` | `0.6598` | `0.6794` | **`0.6651`** *(0.6831†)* | — | **`[Established]`** |
| `all_area_gini` | Unmasked Gini | `0.6457` | `0.6457 (+)` | — | `-0.5711` | `0.6330` | `0.6967` | `0.6675` | `0.6658` | — | **Industrial confound** |
| `res_area_q25` | Res Area 25th pct | `0.3393` | `0.6607 (-)` | — | `+0.1791` | `0.3585` | `0.3399` | `0.3217` | `0.6600` | — | Co-varies w/ `<50m²` |
| **`dlst_regency_urban`** | Urban Anomaly (mixed) | `0.6501` | `0.6501 (+)` | *(see §2.3 L8)* | `+0.4842` | `0.6832` | `0.6581` | `0.6411` | `0.6608` | — | **`[Observed Caveat]`** |
| `res_area_med` | Res Median Area (`m²`) | `0.3421` | `0.6579 (-)` | `65.83` vs `75.71 m²` | `+0.1481` | `0.3396` | `0.3529` | `0.3382` | `0.6564` | — | Alternate size summary |
| `ndbi` | S2 Built Index | `0.6050` | `0.6050 (+)` | — | **`+0.6640`** | `0.6570` | `0.6847` | `0.6020` | `0.6479` | — | High density $\rho$ |
| `res_share_lt30` | Res Grain `< 30 m²` | `0.6161` | `0.6161 (+)` | `14.00%` vs `12.06%` | `-0.264` | `0.583` | `0.616` | `0.661` | `0.6198` *(0.6353†)* | `8.04e-8` | Weaker than `<50/60` |
| `ob_mean_floors` | Overture/Vida Height | `0.6309` | `0.6309 (+)` | `1.785` vs `1.587` | `-0.463` | `0.623` | `0.663` | `0.618` | — | `1.00e-9` | **Kotamadya confound** |
| `osm_walk_density` | Street Density (`km/km²`) | `0.6093` | `0.6093 (+)` | `22.13` vs `19.79` | `+0.471` | `0.669` | `0.672` | `0.560` | `0.6338` | `3.34e-7` | **High density $\rho$** |
| `res_area_gini` | Res Masked Gini (`>=20`) | `0.5930` | `0.5930 (+)` | `0.4208` vs `0.4032` | `-0.163` | `0.536` | `0.618` | `0.633` | `0.5956` | `1.93e-5` | Drops vs `all_`; inverts RW |
| `res_comp_med` | Res Compactness Med | `0.4181` | `0.5819 (-)` | `0.7447` vs `0.7471` | `-0.059` | `0.451` | `0.368` | `0.424` | `—` *(0.586††)* | `1.54e-4` | Near-zero median delta |
| **`res_disp4_all`** | **Orientation Disorder** | `0.5370` | **`0.5370 (+)`** | `0.2431` vs `0.2221` | `-0.123` | `0.512` | `0.578` | `0.526` | `0.5387` | **`0.090`** | **`[Rejected]` Null in DKI** |
| **`res_H90_all`** | **Orientation Entropy 90°** | `0.5288` | **`0.5288 (+)`** | `0.6886` vs `0.6741` | `-0.066` | `0.499` | `0.556` | `0.538` | `0.529–0.539` | **`0.186`** | **`[Rejected]` Null in DKI** |
| **`space_sufficiency`** | **Baseline GHSL/Pop** | `0.5269` | **`0.5269 (+)`** | `6.917` vs `6.198` | `-0.066` | `0.548` | `0.430` | `0.594` | `—` | **`0.210`** | **`[Rejected]` (74.4% clip)** |
| **`osm_gang_path_share`** | **OSM Living/Path Share** | `0.4915` | `0.5085 (-)` | `0.3011` vs `0.3097` | `+0.321` | `0.415` | `0.482` | `0.592` | — | **`0.693`** | **`[Rejected]` Flip across T1-T3** |
| **`res_plan_area_frac`** | **Baseline Plan Area Frac** | `0.4798` | **`0.5202 (-)`** | `0.2267` vs `0.2288` | `+1.000` | `0.448` | `0.510` | `0.443` | `0.5331` | **`0.345`** | **`[Rejected]` Baseline fail** |

*†Sensitivity values in parentheses denote `>= 25%` overlap threshold (`n = 218` pos vs. `373` neg): `ndvi 0.7165`, `ghs_res_share 0.7036`, `res_nn_p25 0.7011 (rho_dens = -0.0349)`, `res_share_lt60 0.6831`, `res_share_lt50 0.6820`, `res_share_lt30 0.6353`. ††`res_comp_med` / `building_compactness` range `0.5857–0.5861` across compactness specs.*

### 2.2 Intra-Kotamadya Robustness Check (Eliminating City-Core Location Confounding)

| Municipality | Evaluated `n` (Pos / Neg) | `ndvi` Med (Pos vs. Neg) | `res_nn_p25` (m) (Pos vs. Neg) | `res_share_lt50` (Pos vs. Neg) | `ob_mean_floors` (Pos vs. Neg) | L8 `dlst_intra_s21_l8_k5` (`n` Pos/Neg) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Jakarta Barat** | `74 / 66` | `0.157` vs `0.180` (`-`) | `6.97` vs `7.37` (`-`) | `0.311` vs `0.238` (`+`) | `1.75` vs `1.53` (`+`) | `+0.108` vs `+0.029 K` (`19/34`) |
| **Jakarta Pusat** | `36 / 17` | `0.134` vs `0.224` (`-`) | `6.66` vs `8.11` (`-`) | `0.384` vs `0.277` (`+`) | **`2.04` vs `2.71` (`-`)** | `+0.158` vs `-0.735 K` (`18/14`) |
| **Jakarta Selatan** | `73 / 91` | `0.239` vs `0.263` (`-`) | `7.48` vs `7.81` (`-`) | `0.305` vs `0.286` (`+`) | `1.65` vs `1.44` (`+`) | `+0.101` vs `-0.297 K` (`46/78`) |
| **Jakarta Timur** | `80 / 134` | `0.201` vs `0.243` (`-`) | `6.56` vs `7.17` (`-`) | `0.368` vs `0.311` (`+`) | `1.65` vs `1.60` (`+`) | `+0.594` vs `-0.253 K` (`54/113`) |
| **Jakarta Utara** | `92 / 65` | `0.153` vs `0.180` (`-`) | `6.61` vs `7.51` (`-`) | `0.386` vs `0.230` (`+`) | **`2.02` vs `2.11` (`-`)** | `+1.288` vs `+0.087 K` (`15/15`) |

* **`[Established]` True Within-Borough Invariance vs. `ob_mean_floors` Artifact**: Across *all five* DKI municipalities individually, Pergub 90 cells consistently have lower `ndvi`, tighter `res_nn_p25`, higher `res_share_lt50`, and warmer L8 intra-urban heat anomalies (`dlst_intra_s21_l8_k5`). Conversely, **`ob_mean_floors`** owes its pooled `0.6309` AUC largely to center-vs.-suburb composition (`Pusat`/`Utara` have larger slum share and taller 2+ floor cores where non-slums remain taller `2.71 > 2.04`), reversing polarity inside inner Jakarta.

### 2.3 Landsat-8 Tier-1 vs. MODIS-Contaminated Intra-Urban Thermal Disparity (`n = 406` vs. `621`)

Restricted strictly to H3 cells holding true `100 m` Landsat 8/9 thermal retrievals (`lst_tier == 1`, `pos = 152, neg = 254`), intra-urban heat disparities sharpen substantially relative to mixed-tier composites (`n = 621`):

| Thermal Variant (`lst_tier == 1`, `n = 406`) | `auc` | Med (Pos vs. Neg) | `auc_T1` | `auc_T2` | `auc_T3` | `mean_T` | `p`-val (MWU) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`dlst_regency_urban`** ($T - \text{med}_{\text{reg, smod}\ge 21}$) | **`0.7349`** | **`+0.950` vs `-0.610 K`** | `0.770` | `0.780` | `0.695` | **`0.7481`** | `2.30e-15` |
| `lst_k` / `heat_island_intensity_k` *(constant offset)* | `0.7109` | `317.700` vs `316.210 K` | `0.716` | `0.758` | `0.676` | `0.7165` | `1.13e-12` |
| **`dlst_intra_s21_k8`** (`k=8` disk, `smod>=21` peers) | **`0.6880`** | `+0.930` vs `-0.202 K` | `0.717` | `0.690` | `0.648` | **`0.6850`** | `2.25e-10` |
| **`dlst_intra_s21_k5`** (`k=5` disk, `smod>=21` peers) | **`0.6765`** | **`+0.710` vs `-0.173 K`** | `0.711` | `0.657` | `0.653` | **`0.6739`** | `2.63e-09` |
| `dlst_intra_s21_k3` (`k=3` disk, `smod>=21` peers) | `0.6513` | `+0.489` vs `-0.149 K` | `0.677` | `0.625` | `0.636` | `0.6459` | `3.34e-07` |
| `dlst_intra_s21_l8_k5` *(`n=405`, strictly L8 peers)* | `0.6451` | `+0.413` vs `-0.270 K` | `0.689` | `0.596` | `0.633` | `0.6394` | `1.00e-06` |
| *Mixed-tier `dlst_intra_s21_k5` comparison (`n=621`)* | `0.5919` | `+0.235` vs `-0.323 K` | `0.591` | `0.581` | `0.598` | `0.5900` | `7.73e-05` |

* **`[Observed Caveat]` The Thermal Fidelity–Coverage Dilemma**: `1 km` MODIS Tier-3 (`25.3%` in DKI) smears urban microclimates across `~1 km` pixels, cutting `dlst_intra_s21_k5` AUC from `0.6765` to `0.5919`. Yet restricting strictly to cached Tier-1 leaves **`44.2%` of DKI Mainland missing thermal values**—requiring a wider multi-year Landsat 8+9 `ST_B10` compositing pull in GEE if thermal justice enters the final production core.

### 2.4 Pergub 90 Ordinal Severity Scaling (`KAT_NUM` 1->4 Across `438` Mainland RWs & Overlapping H3 Cells)

* **Direct Polygon-Level Morphometrics (`n = 438` Mainland RWs: `K1=126`, `K2=198`, `K3=99`, `K4=15`)**:
  * **`share_lt60`**: **`rho = +0.2355 (p = 6.20e-7)`** — monotonic median rise `0.4942 (K1) -> 0.5310 (K2) -> 0.5684 (K3) -> 0.5856 (K4)`.
  * **`share_lt50`**: **`rho = +0.2342 (p = 7.15e-7)`** — medians `0.3868 -> 0.4224 -> 0.4772 -> 0.4414`.
  * **`area_med`**: **`rho = -0.2279 (p = 1.44e-6)`** — medians `60.62 -> 57.08 -> 52.30 -> 53.41 m²`.
  * **`area_gini`**: **`rho = -0.0991 (p = 0.0382)`** — **inverts negatively** (`0.4422 -> 0.4252 -> 0.4146 -> 0.3575`) because `Berat` (`KAT 4`) slums consist of homogeneously small dwellings whereas milder `Sangat Ringan` (`KAT 1`) RWs span mixed land uses.
  * **Orientation (`disp4_all`, `H90_all`, `H180_all`)**: Null (`rho = -0.0507, -0.0306, -0.0309`; `p = 0.290–0.524`; `K4` `disp4 = 0.0904`, `H90 = 0.5258`, lowest disorder in severe tightly packed settlements).
* **H3 Cell-Level Severity (`dki_kat_wmean` / `dki_kat_max` on `dki_slum_share >= 10%`)**:
  * `res_nn_p25`: `rho_wmean = -0.2244` (`rho_max = -0.2796`); `res_share_lt50`: `+0.2216`; `ndvi`: `rho_wmean = -0.1628` (`rho_max = -0.2627`).
  * **`dlst_intra_s21_k5` vs. raw `lst_k`**: Intra-urban `k=5` anomaly scales monotonically with Pergub 90 severity (**`rho = +0.2022, p = 5.3e-4`**) whereas raw `lst_k` turns non-significant (**`rho = +0.0629, p = 0.285`**), empirically validating Workstream A/B's choice of intra-urban thermal anomaly over raw temperature.

---

## 3. Kabupaten Karawang — Dual-Regime Phenomenon & MAUP Diagnostics

### 3.1 Karawang Urban-Matched Screen (`smod >= 21`, `pos = 56`, `neg = 1,120`) & Tercile Regime Split

Density terciles across `Karawang Urban` (`T1_low [0.0000, 0.0296]`, `pos=7/385`; `T2_mid [0.0297, 0.0598]`, `pos=14/378`; `T3_high [0.0599, 0.2523]`, `pos=35/357`) expose why unstratified pooling or naive tercile magnitude averaging (`strat_mean_dir_auc`) can seriously mislead:

| Feature (Karawang Urban) | `auc_raw` | `dir` | Med (Pos vs. Neg) | `rho_dens` | `auc_T1` (`pos=7`) | `auc_T2` (`pos=14`) | `auc_T3` (`pos=35`) | Interpretation & Regime Diagnostics |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`radiance`** (VIIRS) | `0.7855` | `+` | — | `+0.3960` | `0.7748` | `0.8057` | `0.7323` | `strat = 0.7709` (township-center / street-lighting correlation) |
| **`osm_gang_path_share`** | **`0.7912`** | `+` | `0.1834` vs `0.0000` | `+0.3310` | `0.6815` | `0.7871` | **`0.7854`** | `strat = 0.7514`; strong *gang* mapping in Karawang towns vs. DKI null |
| `osm_walk_density` | `0.7536` | `+` | — | `+0.6869` | `0.6597` | `0.6551` | `0.7361` | `strat = 0.6837` (closely tracks density) |
| **`res_nn_p25`** | `0.2744` | **`-`** | `7.54–8.23` vs `8.27–8.68`* | `-0.2884` | `0.4317` | `0.3010` | **`0.2852`** | `auc_mag = 0.7256`, `strat = 0.6607` (`T3` equals DKI `0.715`) |
| `residential_plan_area_frac` | `0.7287` | `+` | `0.0995` vs `0.0404` | `+1.0000` | `0.6275` | `0.5667` | `0.7136` | Town vs. peri-urban density proxy in Karawang |
| **`res_share_lt50`** | `0.6165` | `+` | `0.365` vs `0.320` | **`-0.073`** | `0.564` | `0.567` | **`0.671`** | **Converges on DKI inside dense urban core `T3` (`0.671`)** |
| **`res_share_lt30`** | `0.6078` | `+` | `0.176` vs `0.158` | **`-0.065`** | `0.632` | `0.524` | **`0.656`** | Near-zero density correlation; stronger `T3` |
| `res_area_gini` | `0.6603` | `+` | `0.431` vs `0.390` | `+0.336` | `0.703` | `0.545` | `0.588` | Driven by `T1` flood-village farmyard shed variance |
| `res_disp4_all` / `H90_all` | `0.626 / 0.642` | `+` | `0.261 / 0.735` vs `0.194 / 0.679` | `+0.196 / +0.240` | `0.674 / 0.676` | `0.518 / 0.553` | `0.604 / 0.606` | Moderate positive in Karawang unlike DKI null |
| **`ndvi`** *(Polarity Flip!)* | `0.4069` | **`-/+`** | `0.372` vs `0.413` | `-0.106` | **`0.674` (+)** | `0.538` (+) | **`0.320` (`0.680 -`)** | **`T1` flood-villages are greener (`0.486 vs 0.406`); `T3` cores deprived (`0.350 vs 0.394`)** |
| **`dlst_intra_s21_k5`** *(Trap!)* | `0.4650` | **`-/+`** | — | `+0.3835` | **`0.1840` (-)** | **`0.2329` (-)** | **`0.4935`** | **Cautionary Artifact**: `strat_mean_dir_auc` hits `0.6965` only because `-` signs invert `T1/T2` `-2.03 K` wet-floodplain cooling; raw `lst_k` in `T3` is `315.08 vs 311.95 K` (`AUC_T3 = 0.7353`)! |

*\*`T1/T2/T3` medians for `res_nn_p25` (Pos vs. Neg): `T1 8.23 vs 8.68 m`, `T2 7.93 vs 8.52 m`, `T3 7.54 vs 8.27 m` (`all_nn_p25` citywide `7.88 vs 8.46 m`). For `T3` raw `lst_k`, dense urban slums are substantially hotter (`315.08 vs 311.95 K`, `AUC_T3 = 0.7353`), whereas `T1` flood-plain villages are cooler (`308.24 vs 309.37 K`, `dlst_s21_k5 = -2.029 vs -0.354 K`).*

### 3.2 Structural Explanation: Karawang Kotaku Polygons by Kecamatan (`n = 100` RTs)

| Kecamatan | Median Buildings (`all_n_bldg`) | Median Footprint (`m²`) | `all_share_lt30` | `all_share_lt50` | `all_area_gini` | `all_H90_all` | Field `k1_a_p` (Irreg.) | Field `k4_p` (Drainage/Flood) | Regime Profile |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Rengasdengklok** | `81.0` | **`62.205`** | `0.130` | **`0.357`** | `0.302` | `0.639` | `0.000` | `100.0` | Old market town core (small footprints) |
| **Cikampek** | `84.0` | **`62.757`** | `0.135` | **`0.321`** | `0.347` | `0.648` | `50.000` | `100.0` | Dense rail/township core |
| **Karawang Barat** | `91.0` | **`63.214`** | `0.130` | **`0.322`** | `0.319` | `0.536` | `34.300` | `100.0` | Urban regency seat |
| **Teluk Jambe Barat** | **`155.0`** | `72.673` | `0.152` | `0.268` | `0.370` | `0.583` | `26.600` | **`100.0`** | **Riverine floodplain villages** (*Karang Ligar*, etc.) |
| **Karawang Timur** | `90.5` | `73.901` | `0.129` | `0.272` | `0.369` | `0.528` | `8.962` | `100.0` | Transitional township |
| **Teluk Jambe Timur** | `130.0` | `78.849` | `0.131` | `0.254` | `0.372` | `0.637` | `50.000` | `100.0` | Mixed industrial-periurban edge |
| **Klari** | `89.0` | `83.912` | `0.139` | `0.268` | `0.387` | `0.584` | `50.000` | `0.0` | Rural/peri-urban larger lots |
| **Kota Baru** | `79.0` | `84.580` | `0.085` | `0.205` | `0.354` | `0.614` | `50.000` | `100.0` | Rural/exurban cottages |

### 3.3 Polygon MAUP Audit: `170 ha` Ring Bias vs. Equal-Area `~2.6 ha` Controls (`n_slum = 100, n_ctrl = 59`)

Comparing micro-polygons (`median = 2.6 ha`) directly against `100–750 m` annular rings (`~170 ha`, `~65×` area) creates extreme artificial statistical separation on dispersion and entropy metrics because larger geographic windows automatically sample more diverse parcels, road axes, and factory sheds (`c5_krw_polygon_vs_ring` vs. `c6` shifted equal-area `500 m` circle controls):

| Polygon Feature | Slum RT vs. `~170 ha` Ring (`auc_mag dir`) | `med_slum` vs `med_ring` (`win_rate`) | Equal-Area `~2.6 ha` Shifted Control (`n=100 vs 59`) | Equal-Area `med_slum` vs `med_ctrl` | MAUP Diagnosis |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `all_n_bldg` | — | — | **`AUC = 0.736 (+)`** | **`96.0` vs `64.0`** | **True structural crowding density per `2.6 ha`** |
| `res_H180_all` / `all_H180_all` | `0.9344–0.9346 (-)` | `0.650` vs `0.842` (`0.03`) | — | — | **Pure MAUP ring-size artifact** (`65×` area inflation) |
| **`all_H90_all`** | `0.9126 (-)` | `0.592` vs `0.812` (`0.05`) | **`AUC = 0.625 (+)`** *(Flipped!)* | **`0.5922` vs `0.5251`** | Unequal ring flips sign; equal-area restores hypothesis |
| **`all_disp4_all`** | `0.8522 (-)` | `0.129` vs `0.376` (`0.10`) | **`AUC = 0.583 (+)`** *(Flipped!)* | **`0.1287` vs `0.0981`** | Weak-moderate positive in Karawang; zero in DKI |
| **`all_area_gini`** | `0.8838 (-)` | `0.350` vs `0.449` (`0.07`) | `AUC = 0.303 (-)` | `0.3495` vs `0.4046` | Non-slum controls include larger agro/commercial sheds |
| `all_share_lt50` | — | — | `AUC = 0.316 (-)` | `0.2806` vs `0.3469` | Rural flood-plain Kotaku cottages (`73–85 m²`) bias pooled RT `<50m²` below urban peer controls |

---

## 4. OSM Masking, Dual-Channel Accessibility & Street Network Morphology

### 4.1 Impact of Masking OSM Non-Residential Land Uses (`21,135` Polygons)

Filtering `buildings.parquet` against `osm_nonres_zones.parquet` before H3 aggregation consistently improves specificity in Jakarta without harming recall:
* **Nearest-Neighbor Roof Packing**: `res_nn_p25` outperforms unmasked `all_nn_p25` (`strat_mean 0.6839 vs 0.6726`) while halving correlation with gross building density (`rho_dens = -0.0879` vs `-0.2173`).
* **Exposing False Gini Signals**: Unmasked `all_area_gini` achieves `AUC = 0.6457` (`strat = 0.6658`) alongside severe negative density correlation (`rho_dens = -0.5711`) because industrial warehouses next to residential zones inflate polygon-area inequality. Masking non-residential polygons drops `res_area_gini` to **`0.5930`** (`strat = 0.5956`, `rho_dens = -0.163`)—confirming most apparent Gini signal was industrial land-use mixing rather than intra-slum housing inequality.

### 4.2 Dual-Channel Walk Accessibility Audit (`A_public` vs. `A_commercial` vs. `A_religious`)

Using regional clipped OSM walk graphs (`DKI_Mainland: 1,253,215 nodes, 116,620 POIs`; `Karawang_ResUrban: 861,668 nodes, 15,760 POIs`) and partitioning `173,820` Overture Places cleanly into **`A_public`** (`49,962`: schools/edu, hospital/pharmacy [note `0` `clinic` rows], civic offices, parks), **`A_commercial`** (`105,238`: food/retail/banks/malls), and **`A_religious`** (`18,620`), Dijkstra network routing (`limit = 2,500 m`) reveals:

| Accessibility Feature | DKI Mainland `auc_raw` | DKI Med (Pos vs. Neg) | DKI `rho_dens` | Karawang Urban `auc_raw` | KRW Med (Pos vs. Neg) | KRW `rho_dens` | Audit Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`a_public_15m`** | `0.5570` (`+`) | **`38.0` vs `30.0`** (`p=7.8e-3`) | `+0.531` | `0.6571` (`+`) | **`3.0` vs `1.0`** | `+0.644` | **`[Rejected]` Sign-flip persists in `A_public`** |
| **`a_comm_15m`** | `0.5598` (`+`) | **`89.0` vs `65.0`** (`p=5.3e-3`) | `+0.529` | `0.7018` (`+`) | **`3.5` vs `1.0`** | `+0.629` | **`[Rejected]` Sign-flip persists in `A_comm`** |
| **`a_relig_15m`** | `0.6038` (`+`) | **`15.0` vs `11.0`** (`p=1.2e-6`) | `+0.581` | `0.6888` (`+`) | **`1.5` vs `0.0`** | `+0.548` | Surrogate dense-kampung *musholla* density |
| `dist_nearest_public_m` | `0.494` (`-`) | `180.6` vs `190.2 m` | — | `0.3714` (`-`) | `513.5` vs `788.2 m` | `-0.583` | Slums closer (or equal in DKI) to mapped POIs |
| `dist_nearest_health_m` | — | `429.3` vs `467.3 m` | — | `0.2636` (`-`) | **`1080.0` vs `2349.7 m`** | `-0.511` | **Missing Overture `clinic` leaves only town pharmacies/hospitals** |
| `dist_nearest_park_m` | `0.5416` (`+`) | `986.5` vs `848.6 m` (`p=0.052`) | `-0.288` | `0.4203` (`-`) | `2600` vs `2600 m` (cap) | `-0.249` | Weak expected sign in DKI only (`<0.55`) |
| `a_public_share_15m` / `_25m` | `0.4642` (`15m`) | `0.302` vs `0.318` (`p=0.099`) | `-0.110` | `0.3590` (`25m`) | `0.394` vs `0.500` (`strat=0.632`) | `-0.153` | Only weak composition lean; poor universal reliability |

* **`[Established]` Hypothesis Falsified**: Dividing Overture POIs into `A_public` vs. `A_commercial` does **not** isolate service-desert deprivation in Indonesian cities. Both Jakarta slums and urban Karawang Kotaku blocks sit closer to dense mixed-use neighborhoods holding *more* walkable schools, pharmacies, shops, and mosques than formal perimeter housing estates. **Critical Gap (`[Unverified Offline]`)**: Overture cached `0` `clinic` (*Puskesmas/Klinik*) records and `0` public transit stops (`TransJakarta`/`KRL`/commuter feeders); true public *transit* & primary-clinic deficits remain untested until OSM civic/transit POIs are ingested.

### 4.3 OSM Walk Street Morphology (`4,330,694` Edges)

* **`osm_gang_path_share`**: Strong discriminator in **Karawang Urban** (`AUC = 0.7912`, median `0.1834` vs `0.0000`, `strat = 0.7514`, `T3 = 0.7854`), yet completely **null in DKI Mainland** (`AUC = 0.4915, p = 0.693`, switching polarity `T1 = 0.415 -> T2 = 0.482 -> T3 = 0.592`). High contributor/hotspot tagging heterogeneity prevents `gang` share from serving as an uncalibrated global indicator.
* **`osm_walk_density_km_km2`**: Tracks urban concentration (`rho_dens = +0.471` DKI, `+0.687` KRW). **`osm_dead_end_share`**: Weakly *lower* in DKI slums (`0.0682 vs 0.0778`, `AUC = 0.4157`), opposite standard US cul-de-sac/grid hypotheses because DKI planned *cluster* subdivisions use gated cul-de-sacs whereas inner-city kampungs form porous multi-alley warrens.

---

## 5. Cross-Dimensional Orthogonality & PCA Variance Decomposition (`ALL_RES`)

### 5.1 Multi-Region vs. DKI Spearman Correlation Structure (`n = 9,345` vs. `860` Res Cells)

| Variable | `plan_area_frac` (`ALL` / `DKI`) | `density_km2` (`ALL` / `DKI`) | `res_nn_p25` (`ALL` / `DKI`) | `res_share_lt50` (`ALL` / `DKI`) | `ndvi` (`ALL` / `DKI`) | `dlst_s21_k5` (`ALL` / `DKI`) | `dlst_reg_urb` (`ALL` / `DKI`) | `ghs_res_share` (`ALL` / `DKI`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`res_nn_p25`** | `-0.454` / **`-0.123`** | `-0.462` / `-0.080` | `1.000` | `-0.457` / `-0.629` | `+0.475` / `+0.367` | `-0.126` / `-0.200` | `-0.240` / `-0.260` | `+0.278` / `+0.092` |
| **`res_share_lt50`** | **`-0.101`** / **`-0.187`** | **`-0.041`** / `-0.120` | `-0.457` / `-0.629` | `1.000` | **`-0.053`** / `-0.081` | **`-0.009`** / `+0.098` | **`+0.065`** / `+0.162` | **`+0.005`** / `-0.039` |
| **`ndvi`** | `-0.571` / `-0.439` | `-0.715` / `-0.441` | `+0.475` / `+0.367` | `-0.053` / `-0.081` | `1.000` | `-0.293` / `-0.523` | `-0.408` / `-0.548` | `+0.604` / `+0.300` |
| **`dlst_intra_s21_k5`** | `+0.292` / `+0.502` | `+0.305` / `+0.333` | `-0.126` / `-0.200` | `-0.009` / `+0.098` | `-0.293` / `-0.523` | `1.000` | `+0.667` / `+0.870` | `-0.125` / `+0.043` |
| **`dlst_regency_urban`** | `+0.347` / `+0.496` | `+0.409` / `+0.355` | `-0.240` / `-0.260` | `+0.065` / `+0.162` | `-0.408` / `-0.548` | `+0.667` / `+0.870` | `1.000` | `-0.265` / `-0.046` |
| **`ghs_res_share`** | **`-0.364` / `+0.388`** | **`-0.564` / `+0.145`** | `+0.278` / `+0.092` | `+0.005` / `-0.039` | `+0.604` / `+0.300` | `-0.125` / `+0.043` | `-0.265` / `-0.046` | `1.000` |

* **Key Orthogonality Findings**:
  1. `res_share_lt50` is **strictly orthogonal** to macro-urban density (`rho = -0.041`), vegetative greenness (`-0.053`), intra-urban heat (`-0.009`), and `ghs_res_share` (`+0.005`), directly isolating architectural micro-grain.
  2. `res_nn_p25` separates closely related nearest-neighbor spacing (`rho = -0.123` with density inside Jakarta) and exhibits only moderate overlap with `< 50 m²` micro-grain (`rho = -0.457` regionally / `-0.629` in DKI) and canopy (`+0.475`).
  3. **`ghs_res_share` Exhibits Cross-Scale Polarity Flip**: Regionally (`ALL_RES`), lower `ghs_res_share` reflects dense mixed commercial cores (`rho = -0.564` with density); inside DKI Mainland, formal master-planned subdivisions sit near `0.94+` while Pergub 90 RWs sit near `0.86` along industrial/port/rail corridors (`rho = +0.388` with residential plan area fraction).

### 5.2 PCA Eigenvalue Collapse Comparison (`StandardScaler` Over `ALL_RES`)

| Candidate Set | Included Indicators | Complete Cases (`n`) | Explained Variance Ratios (`PC1 .. PCk`) | Diagnosis |
| :--- | :--- | :---: | :--- | :--- |
| **Original 7D Baseline** | `res_plan_area_frac, net_m2_per_capita, building_compactness, ndvi, heat_island_intensity_k, amenities_15m, population` | `8,375` | **[`0.4864`, `0.1407`, `0.1338`, `0.1069`, `0.0593`, `0.0373`, `0.0355`]** | Severe `PC1` urban-density domination (**`48.64%`**); 3 tail axes `<6%`. |
| **`CAND_5D_CORE`** | `res_nn_p25, res_share_lt50, ndvi, dlst_intra_s21_k5, ghs_res_share` | `8,333` | **[`0.2993`, `0.2232`, `0.1984`, `0.1733`, `0.1058`]** | Balanced multi-dimensional variance: top 4 axes each carry **`17.3%–29.9%`**. |
| `CAND_8D_comp` | `CAND_5D_CORE` + `res_area_gini, res_disp4_all, res_comp_med` | `8,301` | `[0.2504, 0.1727, 0.1501, 0.1202, 0.1078, 0.0990, 0.0639, 0.0359]` | Added morphology shapes largely weakly correlated with slums in DKI. |
| `CAND_8D_hgt` | `CAND_5D_CORE` + `res_area_gini, res_disp4_all, ghs_res_eff_height_m` | `8,301` | `[0.2949, 0.1744, 0.1489, 0.1202, 0.1087, 0.0811, 0.0389, 0.0329]` | GHSL effective height absorbs `PC1` variance (`29.49%`) via core-density link. |
| `CAND_8D_gang` | `CAND_5D_CORE` + `osm_gang_path_share, res_disp4_all, ghs_res_eff_height_m` | `8,298` | `[0.3167, 0.1671, 0.1302, 0.1264, 0.1125, 0.0689, 0.0452, 0.0329]` | `osm_gang_path_share` + height re-inflate `PC1` to `31.67%`. |

---

## 6. Summary Decision Scorecard & Workstream D Handoff

| Category | Indicator / Signal | Cross-Region Synthesis & Decision Role for Workstream D (`options_memo.md`) |
| :--- | :--- | :--- |
| **Surviving Core Axes** *(High Priority)* | **`res_share_lt50` / `res_share_lt60`**, **`res_nn_p25`**, **`ndvi`** | Passed **every** screen: orthogonal or near-orthogonal to `plan_area_frac`, significant across all 3 density terciles in DKI (`strat AUC = 0.665–0.706`), consistent across all 5 Jakarta municipalities, monotonic against Pergub 90 `KAT 1–4`, and validated inside dense `T3` Karawang cores (`AUC 0.671–0.715`). |
| **Conditional Thermal Axis** *(Needs Tier-1 GEE Fix)* | **`dlst_intra_s21_k5` / `k8` / `dlst_regency_urban`** *(strictly `lst_tier == 1`)* | Strong intra-urban thermal disparity (`AUC 0.677–0.735`) + RW severity correlation (`p = 5.3e-4`) once `1 km` MODIS Tier-3 is removed; degraded (`44.2%` DKI non-Tier-1 gap) in cached local snapshot and requires urban-mask conditioning (`smod >= 21`) to avoid cooling wet flood-plain farming villages. |
| **Conditional Land-Use Exposure** *(Needs Framing Care)* | **`ghs_res_share`** | Strong DKI tercile survivor (`strat AUC = 0.690`), isolating industrial/port/rail encroachment; **cannot** stand alone as an internal housing quality metric due to regional-vs.-intra-city correlation inversion (`-0.564` vs `+0.388`). |
| **Regime-Dependent / Conditional** | `osm_gang_path_share`, `res_area_gini`, `res_disp4_all`, `ob_mean_floors` | Active in Karawang (`gang AUC 0.791`, `H90` equal-area `0.625`) but null or reversed inside Jakarta (`gang p = 0.69`, `disp4 p = 0.09`, `area_gini KAT -0.099`, `floors` inverted inside Pusat/Utara). Do **not** include blindly in a universal global core without regime/bias controls. |
| **Empirically Rejected** | `residential_plan_area_fraction`, `space_sufficiency_ratio`, **`A_public` / `A_commercial` (Overture 15m/25m)**, `osm_dead_end_share`, `res_comp_med` | Baseline density & Volume/Pop collapse (`AUC 0.48–0.53` in DKI), dual-channel POI splitting fails to overturn urban core co-location bias, and `dead_end_share` / `comp_med` fail direction or effect-size thresholds. |
| **Unscreened Offline Gaps** *(Targeted Checks Possible in Workstream D Options)* | **Google OB confidence sensitivity (`0.65/0.70/0.75`)**, **`10 m` Sentinel-2 masked GLCM** & **`Sentinel-1 VH/VV`**, **OSM `Puskesmas`/clinic & transit stops**, **Regional Flood (`HAND/InSAR`) ablation** | Cached tables (`confidence == 0.85`, `200×200` preview TIFs, `0` Overture `clinic`/transit rows) prevented offline ablation. Workstream D (`options_memo.md`) will weigh: (Option A) fast zero-external-pull refactor around the orthogonal **5D Core** (fixing MODIS Tier-3 gap via L8 backfill if authorized), vs. (Option B) lightweight GEE + OSM public-transit/clinic pull to test `10 m` masked S2 GLCM, OB confidence stability, and transit deserts before locking the production schema. |
