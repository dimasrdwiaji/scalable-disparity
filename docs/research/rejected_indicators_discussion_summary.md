# Why Plausible Urban-Deprivation Indicators Fail in Practice: Consolidated Screening Ledger (For Discussion Section)

**Project:** `phys_living_index` (Jabodetabek + Karawang, H3 Resolution 8)  
**Purpose:** Concise, discussion-ready summary of every candidate indicator tested and rejected across all project stages (original `10D → 7D → 4D` refinement, Stage 3 ADR 0005 audits, and exploratory morphology/imperviousness diagnostics), keeping the active core locked at **`D = 4`** (`res_share_lt50`, `res_nn_p25`, `vegetation_ndvi`, `dlst_local_ring_k5`).  
**Date:** 2026-11-19

---

## Part 1: Short Discussion Summary (4 Paragraphs)

When building a satellite-based physical living-space index, the temptation is to throw in every urban indicator that sounds reasonable on paper—building height, roof texture, nightlights, air pollution, walkable amenities, street alignment, and paved ground cover. Across three rounds of empirical testing in Greater Jakarta and Karawang (`9,252`–`9,641` urban H3 cells, benchmarked against Mainland DKI Jakarta's [Pergub 90/2018](#ref-pergub90) RW Kumuh registry and Karawang's [KOTAKU / Permen PUPR 14/2018](#ref-pupr2018) polygons), **15 plausible indicator families failed** to earn a spot alongside our four surviving dimensions. Crucially, they did not fail randomly; they broke down for five repeatable reasons: **sensor/resolution mismatch**, **pipeline circularity**, **density confounding**, **cross-city sign reversals**, and **hazard-vs-housing construct drift**.

First, several popular Earth Observation (EO) proxies simply run out of physical resolution—or pick up dataset artifacts—at the neighborhood scale (`~0.74 km²`). At `10 m` pixel size, Sentinel-2 roof texture (`GLCM`) blurs tightly packed `< 50 m²` *kampung* roofs into smooth gray patches instead of rough ones; Sentinel-5P air quality (`~5.5 km`) and `1 km` MODIS heat layers smear whole sub-districts together; Google Open Buildings' polygon smoothing turns irregular roofs into near-perfect rectangles (`median rectangularity = 0.9985`), wiping out shape-compactness variance; and `Open Buildings 2.5D` height estimates carry `2.2–7 m` errors in dense low-rise fabrics—wide enough to swallow the real gap between a 1-story *kampung* and a 2-story townhouse. Second, combining derived gridded datasets can accidentally create mathematical loops: dividing `GHS-BUILT-V` by `GHS-POP` to estimate living space per person (`R_space`) mostly recovers a flat sub-district constant (`R² = 0.976` circularity) because [GHS-POP (Schiavina et al., 2023)](#ref-schiavina2023) distributes census counts *using* built volume in the first place.

Third, many textbook urban indicators turned out to be **"where is the city?" detectors** rather than living-quality detectors. Nightlights (`VIIRS`), raw building coverage (`plan_area_frac` / `BCR`), `NDBI`, mixed non-residential share (`ghs_res_share`), and even local building orientation alignment all correlated heavily with gross density or urban–rural location, failing once dense Jakarta *kampungs* were compared against equally dense formal blocks right next door. Even more subtly, building orientation alignment flipped expectations in dense cores: sparse green villages looked "disordered," while wall-to-wall Jakarta *Berat* slums (such as Kalibaru at `1.53°` and Jembatan Besi at `2.33°`) were physically packed into neat parallel rows almost indistinguishable from planned suburban *perumahan*.

Fourth, the toughest failure mode—and the biggest warning for globally transferable indices—was **cross-region sign reversal**. Walkable amenity accessibility (`15-minute city` counts) scored cramped inner-city *kampungs* *higher* than leafy affluent suburbs because downtown slums sit closer to shops and main roads, while crowd-mapped OSM/Overture road layers suffer systematic volunteer-mapping bias against poorer areas ([Herfort et al., 2023](#ref-herfort2023)). Similarly, separating non-building paved surfaces (`ISF`) from building roofs ([Stewart & Oke, 2012](#ref-stewart2012)) broke on every global `10 m` product we tested: `GHS-BUILT-S` predicts roofs themselves (`30.3%` negative residuals), ESA WorldCover dilates over narrow alleys (`ρ = -0.741` with `NDVI`), and Google Dynamic World ([Brown et al., 2022](#ref-brown2022)) leaked softmax probability into `bare`/`water` in weathered coastal *Berat* slums—producing a negative slum correlation inside DKI (`AUC = 0.446`) that flipped completely positive in semi-rural Karawang (`AUC = 0.852`). Together, these negative results explain why keeping the model tight at **`D = 4`** (`0.7935` CV AUC on DKI *Berat/Sedang* slums) is stronger, cleaner, and far more honest than inflating the index with fragile proxies.

---

### Quick Failure-Category Map

| Failure Category | Rejected Indicators | Core Lesson |
| :--- | :--- | :--- |
| **A. Resolution & Sensor Mismatch** | 1. Sentinel-2 `10 m` GLCM Texture<br>2. Air Quality (`PM2.5`, `NO2`)<br>3. `1 km` MODIS & Citywide Thermal Baselines<br>4. 3D Building Height & Vertical Ratios | If the satellite pixel or error bar is coarser than the house/alley feature, the proxy either washes out or inverts. |
| **B. Circularity & Variance Collapse** | 5. Living Space Ratio (`R_space`: `GHS-BUILT-V / GHS-POP`)<br>6. Footprint Compactness & Rectangularity<br>7. Footprint Area Inequality (`res_area_gini`) | Derived grids can loop back on each other, and AI polygon regularization erases real geometric messiness. |
| **C. Density & Urban–Rural Confounding** | 8. VIIRS Nighttime Lights<br>9. Building Coverage (`plan_area_frac` / `BCR`)<br>10. Raw `NDBI` & `BSI`<br>11. Building Orientation Alignment & Entropy<br>12. Mixed Non-Residential Share (`ghs_res_share`) | What separates city from countryside often fails inside a dense city where slums and formal blocks share similar macro-density. |
| **D. Cross-Region Sign Reversals & Bias** | 13. Non-Building Imperviousness (`ISF`: WC, DW, GHSL)<br>14. Walkable Amenities & OSM Road/Alley Proxies | A proxy that points one way in a megacity core and the opposite way in a secondary regency breaks transferability. |
| **E. Construct Drift (Hazard ≠ Living Form)** | 15. Terrain Slope (`GLO-30`) & Flood/Water Frequency | Natural hazard exposure is geographically localized and does not measure indoor/neighborhood living-space deprivation. |

---

## Part 2: Standardized Per-Indicator Breakdown

Every rejected indicator below follows the exact same four-part template for direct comparison.

---

### Category A: Resolution & Sensor Mismatch

#### 1. Sentinel-2 `10 m` Roof Texture (`s2_res_glcm_contrast` & `s2_res_glcm_homogeneity`)
- **What it tried to measure:** Whether messy, tightly packed *kampung* roofs look visually rougher and more chaotic from space than tidy planned housing ([Kuffer et al., 2016](#ref-kuffer2016)).
- **What went wrong (the data):** Across all `852` Mainland DKI cells, `s2_res_glcm_homogeneity` was pure noise (`AUC = 0.507`, $p = 0.710$, `2/4` spatial folds). `s2_res_glcm_contrast` had weak separation (`AUC = 0.581`), failed fold consistency (`3/4`), and correlated *negatively* with building count (`ρ = -0.523`).
- **Why it failed:** Each Sentinel-2 pixel is `10 m × 10 m` (`100 m²`)—bigger than two `< 50 m²` *kampung* houses combined. Instead of looking "rough," sub-pixel *kampung* roofs average out into smooth uniform gray, while formal estates with setbacks, lawns, and larger roofs create sharper pixel-to-pixel contrast.
- **Takeaway for Discussion:** GLCM texture is a classic very-high-resolution (`< 1 m`) slum indicator ([Kuffer et al., 2016](#ref-kuffer2016)), but it does not survive downscaling to free `10 m` Sentinel-2 imagery.

#### 2. Air Quality Proxies (`PM2.5` & `NO2` — Sentinel-5P / ACAG / Open-Meteo)
- **What it tried to measure:** Unequal neighborhood exposure to air pollution and traffic/industrial fumes.
- **What went wrong (the data):** Native pixel grids (`~5.5 km` for Sentinel-5P `NO2`, `~0.1°–0.4°` for reanalysis) produced flat, heavily smoothed gradients across entire districts with almost no neighborhood-to-neighborhood contrast at H3 Resolution 8 (`~0.74 km²`).
- **Why it failed:** You cannot measure micro-scale intra-urban inequality (a *kampung* next to a gated *komplek* 500 m away) using an atmospheric sensor whose single pixel covers 30+ hexagons at once.
- **Takeaway for Discussion:** Regional air-pollution grids capture city-wide background risk, not block-level physical living disparity.

#### 3. Coarse Thermal Fallback (`1 km` MODIS) & Citywide / Raw Heat Baselines (`lst_k`, `dlst_city_median`)
- **What it tried to measure:** Micro-climatic urban heat stress inside crowded, unshaded neighborhoods.
- **What went wrong (the data):** In our earlier thermal cache, `25.3%` of Mainland DKI relied on `1 km` MODIS fallback (`lst_tier == 3`), depressing intra-urban thermal AUC from `0.677` (Landsat-only) to `0.592`. Meanwhile, subtracting a single citywide/rural median (`dlst_city_median`) shifted all of DKI up by `+5.08` to `+5.77 K` and flattened the Pergub 90 severity gradient (`KAT ρ = +0.015` vs. `+0.122` for our local `k = 5` ring baseline).
- **Why it failed:** `1 km` MODIS blurs over neighborhood hot spots, and a citywide rural baseline entangles macro-geography (cool southern Bogor hills vs. warm coastal North Jakarta) with neighborhood deprivation.
- **Takeaway for Discussion:** Thermal injustice only appears cleanly when using true `100 m` Landsat 8/9 multi-year composites referenced against each cell's own immediate urban neighborhood (`dlst_local_ring_k5`).

#### 4. 3D Building Height & Vertical Ratios (`ob_mean_floors`, `Open Buildings 2.5D`, `H/W`, `FAR`)
- **What it tried to measure:** Whether 2–3 story formal townhouses rise above 1-story *kampungs*, or whether narrow street canyons (`H/W`, [Stewart & Oke, 2012](#ref-stewart2012)) trap heat and block airflow.
- **What went wrong (the data):** In our `9.64M` cached footprints, `99.935%` had null `height` and `99.68%` defaulted to `1` floor. Overture's `ob_mean_floors` looked decent citywide (`AUC = 0.631`) only because of center-vs-suburb confounding—inside inner Jakarta it flipped sign (`Jakarta Pusat`: slums `2.04` vs. non-slums `2.71` floors). Literature validations of Sentinel-2-based `Open Buildings 2.5D` ([Sirko et al., 2023](#ref-sirko2023)) also report `2.2–7 m` MAE/RMSE with uneven overestimation in dense `0–10 m` low-rise fabrics.
- **Why it failed:** A `2–7 m` morphology-dependent error bar is as wide as the actual difference between a 1-story (`~3 m`) *kampung* and a 2-story (`~6 m`) townhouse. On top of that, dividing height by spacing (`H/W`) creates exact scale aliasing (`6 m / 3 m` townhouse = `3 m / 1.5 m` *kampung* = `2.0`) and mixes opposing causal directions (canyon heat stress vs. formal multi-story construction).
- **Takeaway for Discussion:** Until free, sub-meter 3D elevation data is globally available, adding noisy low-rise height proxies adds more uncertainty than signal.

---

### Category B: Mathematical Circularity & Variance Collapse

#### 5. Living Space Sufficiency Ratio (`space_sufficiency_ratio` / $R_{\text{space}}$ via `GHS-BUILT-V / GHS-POP`)
- **What it tried to measure:** Floor area per person against the UN-Habitat `9.0 m²/capita` crowding benchmark.
- **What went wrong (the data):** `76.35%` of modelled cells hit the upper clipping ceiling (`1.0`), the raw minimum was suspiciously stuck at `20.30 m²/person` across `152` identical cells (more than double the UN threshold and far above BPS Susenas Jakarta's `12.27 m²/person`), and DKI discrimination failed completely (`AUC = 0.5269`, $p = 0.210$).
- **Why it failed:** [GHS-POP R2023A (Schiavina et al., 2023)](#ref-schiavina2023) does not count people independently at `100 m`—it spreads coarse sub-district census totals across pixels proportionally to `GHS-BUILT-V` (`R² = 0.976` coupling). Dividing built volume by a population grid created *from* built volume cancels out the micro-scale signal and returns a flat sub-district constant.
- **Takeaway for Discussion:** Never divide a built-up layer by a dasymetric population grid (WorldPop or GHS-POP) to estimate crowding—you are just dividing a variable by a rescaled copy of itself.

#### 6. Building Footprint Compactness & Rectangularity (`building_compactness` / `res_mrr_rect_median`)
- **What it tried to measure:** Whether informal houses have messy, jagged, irregular polygon shapes compared to neat rectangular formal homes ([Biljecki & Chow, 2022](#ref-biljecki2022)).
- **What went wrong (the data):** Median cell compactness collapsed into a tiny band (`0.745–0.757`, `std = 0.013`), causing inverse-variance weights to explode (`5.51×`) and yielding near-zero real separation (`0.7447` vs `0.7471` in DKI). Across `8,715,990` residential footprints, median Minimum Rotated Rectangle (MRR) rectangularity was **`0.9985`**.
- **Why it failed:** Google Open Buildings ([Sirko et al., 2021](#ref-sirko2021)) regularizes predicted masks into clean 4-corner rectangles during post-processing. That smoothing erases the jagged roof geometry of real *kampungs* before we ever touch the polygons.
- **Takeaway for Discussion:** Shape-complexity metrics work on manual GIS/LiDAR footprints, but AI-regularized global building datasets flatten shape variance to near zero.

#### 7. Footprint Area Inequality (`res_area_gini`)
- **What it tried to measure:** Whether informal settlements mix tiny shacks and irregular compounds into higher within-neighborhood size inequality.
- **What went wrong (the data):** Unmasked `all_area_gini` looked strong (`AUC = 0.646`) only because warehouses/factories sat next to small homes (`ρ_dens = -0.571`). Once industrial sheds were masked out, `res_area_gini` dropped to `AUC = 0.593` and **inverted negatively** with DKI Pergub 90 severity (`ρ = -0.0991`).
- **Why it failed:** Dense *kampungs* are often *uniformly* small rather than unequal in footprint size, whereas mixed formal neighborhoods combine standard houses with larger mansions or corner plots.
- **Takeaway for Discussion:** Within-cell size inequality confuses mixed-use adjacency with residential deprivation; direct small-footprint prevalence (`res_share_lt50`) is far cleaner and sign-stable.

---

### Category C: Density & Urban–Rural Confounding

#### 8. VIIRS Nighttime Lights (`night_lights`)
- **What it tried to measure:** Economic vitality and formal public infrastructure (street lighting, commercial activity).
- **What went wrong (the data):** Correlated **`ρ = 0.82`** with gross urban density and flipped polarity across Karawang regimes.
- **Why it failed:** Bright commercial corridors, highways, and dense inner-city *kampungs* all glow brightly in `~500 m` VIIRS pixels (blooming/spillover), while quiet, tree-lined affluent suburbs look dimmer.
- **Takeaway for Discussion:** Nightlights work well for macro regional GDP, not for separating rich and poor blocks sitting 500 m apart inside a megacity.

#### 9. Residential Plan Area Fraction / Building Coverage (`residential_plan_area_fraction` / `BCR`)
- **What it tried to measure:** How tightly roofed-over a neighborhood is (`BSF`, [Stewart & Oke, 2012](#ref-stewart2012)).
- **What went wrong (the data):** Completely failed inside Mainland DKI (`AUC = 0.4798`, $p = 0.345$): DKI slums and non-slums had almost identical ground coverage (`0.228` vs `0.232`). At H3 Resolution 8, scale dilution also left `75%` of regional cells clustered above `0.84` when scaled against `0.85`.
- **Why it failed:** In a mature Asian megacity, a dense formal *ruko*/townhouse block covers roughly the same total share of ground as a *kampung*—they differ in **grain size** (`res_share_lt50`) and **tightest neighbor gap** (`res_nn_p25`), not total roof area.
- **Takeaway for Discussion:** Macro ground coverage saturates in dense urban cores; micro-grain and edge-spacing indicators are needed to look *inside* the density.

#### 10. Spectral Built-Up & Bare-Soil Indices (`NDBI`, `BSI`)
- **What it tried to measure:** General built-up intensity (`NDBI`) and exposed unpaved ground (`BSI`).
- **What went wrong (the data):** `NDBI` tracked gross density heavily (`ρ_dens = +0.664`) and correlated strongly and negatively with `NDVI`. Under `[−1, 1]` theoretical bounds, `BSI` variance collapsed to just `0.6%` of total model variance.
- **Why it failed:** Spectrally, `NDBI` and `BSI` mix clay-tile roofs, concrete, asphalt, and dry bare soil together—duplicating what `NDVI` already captures much more cleanly without bare-soil confusion.
- **Takeaway for Discussion:** Adding raw `NDBI`/`BSI` alongside `NDVI` mostly duplicates the green-vs-gray axis while injecting soil/roof material noise.

#### 11. Building Orientation Alignment & Entropy (`res_orient_knn5_mean`, `res_orient_entropy`, `res_H90/H180`, `res_disp4`)
- **What it tried to measure:** Whether houses follow an orderly rectilinear grid (planned *komplek*/townhouses) vs. organic scattered angles (*kampungs*), directly targeting [Permen PUPR 14/2018](#ref-pupr2018) Criterion 1.1 (*Ketidakteraturan Bangunan*) ([Fleischmann, 2019](#ref-fleischmann2019); [Boeing, 2019](#ref-boeing2019)).
- **What went wrong (the data):** Null in Mainland DKI (`res_orient_knn5_mean` `AUC = 0.493`, $p = 0.704$; `res_orient_entropy` `AUC = 0.526`, $p = 0.994$; `res_H90/disp4` `AUC = 0.529–0.537`, $p = 0.09–0.19$). Inside DKI's compact look-alike slice (`lt50 ≥ 0.35`, `nn ≤ 7.0 m`), it still failed (`AUC = 0.479`, $p = 0.679$) and slightly hurt 4D CV AUC (`0.6998 → 0.6985`). Across all `9,252` cells, it correlated **`-0.533`** with building count and **`+0.583`** with `NDVI`.
- **Why it failed:** Two opposing real-world mechanisms broke the linear rule: (1) sparse green rural villages look wildly "disordered" (`8.5°–44.5°`, with `n = 2` cells hitting `44.49°`) simply because isolated farmhouses don't share a grid; (2) wall-to-wall dense Jakarta *kampungs*—including gazetted *Berat* slums like **Kalibaru (`1.53°`)** and **Jembatan Besi (`2.33°`)**—get mechanically forced into parallel rows (`19.4%` of DKI *Berat/Sedang* cells sit `< 2.5°`).
- **Takeaway for Discussion:** Orientation alignment is a useful *post-hoc visual flag* for spotting mass-produced suburban *perumahan* (`44.1%` of compact Bodetabek cells sit `< 2.5°`), but it fails as a city-wide deprivation dimension because gridded inner-city slums look equally aligned.

#### 12. Mixed Non-Residential Built Share (`ghs_res_share`)
- **What it tried to measure:** Exposure of housing to mixed industrial, warehouse, port, and commercial zones.
- **What went wrong (the data):** Passed raw separation in DKI (`AUC = 0.659–0.686`), **but** failed Gate 2 collinearity (`ρ_cnt = +0.376`, `ρ_paf = +0.384`), flipped its density correlation regionally (`-0.564` vs `+0.388`), and showed almost no Pergub 90 severity ladder (`KAT ρ = -0.067` to `-0.074`).
- **Why it failed:** Many DKI slums sit near ports and factories (North/West Jakarta), creating a location correlation—but residential-vs-non-residential land-use mix is a **zoning context**, not a direct measure of housing physical quality, and behaves differently in suburban industrial corridors.
- **Takeaway for Discussion:** Keep land-use mix as a descriptive context layer rather than baking zoning into a physical living-space score.

---

### Category D: Cross-Region Sign Reversals & Mapping Bias

#### 13. Non-Building Imperviousness (`ISF`: WorldCover, Dynamic World, & GHSL minus `BCR`)
- **What it tried to measure:** The paved interstitial ground between buildings—car-width streets, driveways, parking (`ISF` vs `BSF`, [Stewart & Oke, 2012](#ref-stewart2012))—hypothesized to separate formal *komplek* (paved streets) from dense *kampungs* (wall-to-wall roofs, narrow *gang* alleys).
- **What went wrong (the data):** Every global EO product failed differently:
  - **`GHS-BUILT-S − BCR`:** `30.31%` negative residuals, median `0.009` ([Pesaresi & Politis, 2023](#ref-pesaresi2023) predicts building footprints themselves, not streets).
  - **ESA WorldCover (`isf_wc`):** Failed Gate 1 collinearity (`ρ = -0.741` with `NDVI`, `+0.917` with `BCR`), read *higher* in DKI *Berat* slums (`0.500` vs `0.468`), and lowered DKI CV AUC (`0.6998 → 0.6949`).
  - **Google Dynamic World (`isf_dw_prob`):** Monotonic inside DKI (`Berat = 0.159 → Non-Slum = 0.304`, $p = 6.94 \times 10^{-4}$; `AUC = 0.661` in DKI compact slice), **but completely flipped sign in Karawang** (`AUC_raw = 0.852` positive vs `0.446` negative in DKI), dropping zero-shot transfer AUC (`0.5869 → 0.5580`).
- **Why it failed:** At `10 m` resolution, WorldCover ([Zanaga et al., 2022](#ref-zanaga2022)) dilates hard `Built-up` labels right across `< 1.5 m` *kampung* alleys (`91.9%` built-up vs `40.6%` roofs). Meanwhile, Dynamic World ([Brown et al., 2022](#ref-brown2022)) outputs a **CNN softmax probability**, not a true area fraction: in weathered/coastal Jakarta *Berat* slums (Penjaringan, Kapuk, Kalibaru), probability leaked into `bare` (`0.099` vs `0.045`) and `water` (`0.154` vs `0.121`), pulling `isf_dw_prob` down in DKI while still tracking macro-urbanization upward in semi-rural Karawang.
- **Takeaway for Discussion:** Subtracting vector roof area from `10 m` global land-cover grids does not isolate paved streets cleanly—it mostly exposes raster dilation and classifier-probability quirks.

#### 14. Walkable Amenity Accessibility (`cumulative_amenities_15m`, `A_public`, `A_comm`) & OSM Road/Alley Proxies (`osm_walk_density`, `osm_gang_path_share`, `osm_park400_2sfca`)
- **What it tried to measure:** Everyday service access ("15-Minute City", [Moreno et al., 2021](#ref-moreno2021)), street connectivity, and pedestrian *gang* prevalence.
- **What went wrong (the data):** Both public and commercial amenity counts **inverted polarity** in DKI and Karawang (slums scored *higher* than affluent suburbs). `osm_gang_path_share` flipped direction across DKI density terciles (`0.415 → 0.592`, $p = 0.693$); `osm_park400_2sfca` collapsed to median `0.0` in Karawang; and cached Overture `clinic` / transit stops had `0` rows.
- **Why it failed:** In Global South megacities, informal *kampungs* cluster in dense, job-rich urban cores right next to shops, clinics, and roads, whereas wealthy gated suburbs trade walkability for private cars and space. Worse, OSM and Overture road/POI completeness is systematically higher in wealthier regions ([Herfort et al., 2023](#ref-herfort2023)), threatening global transferability.
- **Takeaway for Discussion:** Service accessibility is valuable as a *separate typology/context layer* (distinguishing service-rich inner *kampungs* from isolated peri-urban settlements), but should never be blended into a physical deprivation score.

---

### Category E: Construct Drift (Localized Natural Hazard ≠ Physical Living Form)

#### 15. Terrain Slope Safety (`terrain_safety_inv` / Copernicus DEM `GLO-30`) & Flood / Water Frequency (`water_frequency`, `HAND`)
- **What it tried to measure:** Exposure to steep landslide terrain (`> 15°`) and flood-prone low-lying land.
- **What went wrong (the data):** Almost the entire coastal Jakarta–Bekasi–Tangerang–Karawang urban plain scored a flat `1.0` on slope safety (zero intra-urban variance across DKI's worst slums), isolating only southern mountain foothills (Bogor/Cianjur).
- **Why it failed:** Slope and surface-water proximity measure **site-level natural hazard**, which is geographically specific (mountainous vs. coastal cities) rather than a universal measure of neighborhood housing quality—and a flat coastal slum can be severely deprived while a hillside villa can be wealthy.
- **Takeaway for Discussion:** Hazard layers belong in a separate climate-risk overlay so they can be crossed *against* physical deprivation (e.g., "deprived AND flood-prone") rather than muddying the housing-form index itself.

---

## References

- <a id="ref-biljecki2022"></a>Biljecki, F., & Chow, Y. S. (2022). Global Building Morphology Indicators. *Computers, Environment and Urban Systems*, 95, 101809. [https://doi.org/10.1016/j.compenvurbsys.2022.101809](https://doi.org/10.1016/j.compenvurbsys.2022.101809)
- <a id="ref-boeing2019"></a>Boeing, G. (2019). Urban spatial order: Street network orientation, configuration, and entropy. *Applied Network Science*, 4, 67. [https://doi.org/10.1007/s41109-019-0189-1](https://doi.org/10.1007/s41109-019-0189-1)
- <a id="ref-brown2022"></a>Brown, C. F., Brumby, S. P., Guzder-Williams, B., Birch, T., Hyde, S. B., Mazzariello, J., Czerwinski, W., Pasquarella, V. J., Haertel, R., Ilyushchenko, S., Schwehr, K., Weisse, M., Stolle, F., Hanson, C., Guinan, O., Moore, R., & Tait, A. M. (2022). Dynamic World, Near real-time global 10 m land use land cover mapping. *Scientific Data*, 9, 251. [https://doi.org/10.1038/s41597-022-01307-4](https://doi.org/10.1038/s41597-022-01307-4)
- <a id="ref-fleischmann2019"></a>Fleischmann, M. (2019). momepy: Urban Morphology Measuring Toolkit. *Journal of Open Source Software*, 4(43), 1807. [https://doi.org/10.21105/joss.01807](https://doi.org/10.21105/joss.01807)
- <a id="ref-pergub90"></a>Government of DKI Jakarta. (2018). *Peraturan Gubernur Provinsi Daerah Khusus Ibukota Jakarta Nomor 90 Tahun 2018 tentang Peningkatan Kualitas Permukiman dalam Rangka Penataan Kawasan Permukiman Terpadu* (Berita Daerah Provinsi DKI Jakarta Tahun 2018 Nomor 73003; later superseded by Pergub No. 33 Tahun 2024). JDIH Provinsi DKI Jakarta / JDIH BPK RI: [https://jdih.jakarta.go.id/](https://jdih.jakarta.go.id/) | [https://peraturan.bpk.go.id/](https://peraturan.bpk.go.id/)
- <a id="ref-herfort2023"></a>Herfort, B., Lautenbach, S., Porto de Albuquerque, J., Anderson, J., & Zipf, A. (2023). A spatio-temporal analysis investigating completeness and inequalities of global urban building data in OpenStreetMap. *Nature Communications*, 14, 3985. [https://doi.org/10.1038/s41467-023-39698-6](https://doi.org/10.1038/s41467-023-39698-6)
- <a id="ref-kuffer2016"></a>Kuffer, M., Pfeffer, K., & Sliuzas, R. (2016). Slums from space—15 years of slum mapping using remote sensing. *Remote Sensing*, 8(6), 455. [https://doi.org/10.3390/rs8060455](https://doi.org/10.3390/rs8060455)
- <a id="ref-pupr2018"></a>Ministry of Public Works and Housing of the Republic of Indonesia (Kementerian PUPR). (2018). *Peraturan Menteri PUPR Nomor 14/PRT/M/2018 tentang Pencegahan dan Peningkatan Kualitas Terhadap Perumahan Kumuh dan Permukiman Kumuh*. JDIH BPK RI: [https://peraturan.bpk.go.id/](https://peraturan.bpk.go.id/)
- <a id="ref-moreno2021"></a>Moreno, C., Allam, Z., Chabaud, D., Gall, C., & Pratlong, F. (2021). Introducing the "15-Minute City": Sustainability, resilience and place identity in future post-pandemic cities. *Smart Cities*, 4(1), 93–111. [https://doi.org/10.3390/smartcities4010006](https://doi.org/10.3390/smartcities4010006)
- <a id="ref-pesaresi2023"></a>Pesaresi, M., & Politis, P. (2023). *GHS-BUILT-S R2023A – GHS built-up surface grid, derived from Sentinel-2 composite and Landsat, multitemporal (1975–2030)*. European Commission, Joint Research Centre (JRC). [https://doi.org/10.2905/9F06F36F-4B11-47EC-ABB0-4F8B7B1D72EA](https://doi.org/10.2905/9F06F36F-4B11-47EC-ABB0-4F8B7B1D72EA)
- <a id="ref-schiavina2023"></a>Schiavina, M., Freire, S., Carioli, A., & MacManus, K. (2023). *GHS-POP R2023A – GHS population grid multitemporal (1975–2030)*. European Commission, Joint Research Centre (JRC). [https://doi.org/10.2905/2FF68A52-5B5B-4A22-8F40-C41DA8332CFE](https://doi.org/10.2905/2FF68A52-5B5B-4A22-8F40-C41DA8332CFE) *(Methodology: [Pesaresi et al., 2024](https://doi.org/10.1080/17538947.2024.2390454))*
- <a id="ref-sirko2021"></a>Sirko, W., Kashubin, S., Ritter, M., Annkah, A., Bouchareb, Y. S. E., Dauphin, Y., Keysers, D., Neumann, M., Cisse, M., & Quinn, J. (2021). Continental-scale building detection from high resolution satellite imagery. *arXiv preprint*. [https://doi.org/10.48550/arXiv.2107.12283](https://doi.org/10.48550/arXiv.2107.12283)
- <a id="ref-sirko2023"></a>Sirko, W., Brempong, E. A., Marcos, J. T. C., Annkah, A., Korme, A., Hassen, M. A., Sapkota, K., Shekel, T., Diack, A., Nevo, S., Hickey, J., & Quinn, J. (2023). High-resolution building and road detection from Sentinel-2 (Google Open Buildings 2.5D Temporal Dataset). Google Research. [https://sites.research.google/gr/open-buildings/temporal/](https://sites.research.google/gr/open-buildings/temporal/)
- <a id="ref-stewart2012"></a>Stewart, I. D., & Oke, T. R. (2012). Local Climate Zones for urban temperature studies. *Bulletin of the American Meteorological Society*, 93(12), 1879–1900. [https://doi.org/10.1175/BAMS-D-11-00019.1](https://doi.org/10.1175/BAMS-D-11-00019.1)
- <a id="ref-zanaga2022"></a>Zanaga, D., Van De Kerchove, R., Daems, D., De Keersmaecker, W., Brockmann, C., Kirches, G., Wevers, J., Cartus, O., Santoro, M., Fritz, S., Lesiv, M., Herold, M., Tsendbazar, N.-E., Xu, P., Ramoino, F., & Arino, O. (2022). *ESA WorldCover 10 m 2021 v200*. Zenodo. [https://doi.org/10.5281/zenodo.7254221](https://doi.org/10.5281/zenodo.7254221)
