# 3. Study Area and Data Preparation

## 3.1 Study Domain and Spatial Grid
The primary investigation covers Greater Jakarta (*Jabodetabek*) and the neighboring industrial corridor of Karawang Regency in West Java, Indonesia, bounded by `[106.35°E, -6.75°S]` and `[107.65°E, -5.95°S]` ($\approx 12,800\text{ km}^2$; Figure 1) and projected to UTM Zone 48S (`EPSG:32748`) for metric operations. Rather than treating the entire `12,800 km²` bounding box as a single uniform validation pool, sub-regions serve distinct analytical roles:

- **Primary urban core (Mainland DKI Jakarta):** Evaluates block-scale discrimination and severity grading across dense central *kampungs* (such as neighborhoods bordering Menteng and Cikini; [Hidayati et al., 2020](https://doi.org/10.1080/17549175.2020.1814391); [Mardhotillah & Gamal, 2018](https://doi.org/10.14716/ijtech.v9i7.2519)) and planned formal housing estates. Official slum boundaries from Governor Regulation (Pergub) No. 90/2018 cover `438` mainland neighborhood units (*Rukun Warga*, RW; `~107 km²`) with four severity categories (*Kategori* 1–4), yielding `355` slum and `373` non-slum hexagonal cells in pilot mainland screening.
- **Secondary urban–rural transition (Karawang Regency):** Stress-tests how indicators behave outside dense megacity cores across industrial corridors and irrigated rice plains ([Wardhani, 2016](https://doi.org/10.18196/jgp.2016.0025)). Government *Kotaku* records delineate `100` small neighborhood pockets (*Rukun Tetangga*, RT; `2.83 km²`, median polygon area `2.6 ha`), stratified into low-, medium-, and high-density terciles to separate urban-core behavior from vegetated floodplain settlements and quantify unit-size mismatch against larger hexagonal cells.
- **Excluded baseline and external hold-out city:** Municipal *Kotaku* polygons in Depok (`199.772 km²` against a `199.511 km²` city boundary) span entire administrative districts rather than specific slum pockets and are excluded. To test transferability outside Jabodetabek without local overfitting, an independent external hold-out city in Indonesia or another low- or middle-income region is slated for Stage 5 evaluation.

![Figure 1: Regional setting across Greater Jakarta (Jabodetabek) and Karawang Regency](../latex/figures/study_area_map.png)
*Figure 1. Regional setting across Greater Jakarta (Jabodetabek) and Karawang Regency (~12,800 km²), showing provincial and municipal boundaries across DKI Jakarta, Banten, and West Java along with major ports, commercial cores, and upland terrain.*

To avoid administrative boundary distortions (Openshaw, 1984), spatial layers are harmonized onto an Uber H3 Resolution-8 discrete global grid ([Sahr et al., 2003](https://doi.org/10.1559/152304003100011090)), where each hexagonal cell spans $\approx 0.737\text{ km}^2$ (`73.73 ha`) with an edge length of $\approx 531\text{ m}$. Urban-mask filtering via the Global Human Settlement Layer (GHSL) confines intra-urban temperature baselines and inequality metrics strictly to contiguous built urban areas.

## 3.2 Vetted Open Dataset Inventory
Following Section 2's vetting criteria, only global open datasets that avoid coarse block smearing, circular population ratios, nightlight saturation, and service-proximity inversion enter the pipeline (Table 1). Disqualified layers—including `GHS-POP`, VIIRS nightlights, Sentinel-5P and `PM2.5` atmospheric grids, `1 km` MODIS fallbacks, `GLO-30` terrain slopes, flood layers, Overture/OSM service counts, and Meta's Relative Wealth Index—are excluded.

| Group | Dataset | Source | Resolution | Role in Revised Pipeline |
| :--- | :--- | :--- | :--- | :--- |
| Spatial Grid | Uber H3 (Res 8) | Uber H3 | `0.737 km²` / `~531 m` edge | Equal-area spatial units and 6-neighbor adjacency graph for baselines and GAT-AE. |
| Built Footprints | Open Buildings (Google / Vida) | [Sirko et al. (2021)](https://arxiv.org/abs/2107.12283) | Sub-meter footprints | Small-footprint residential buildings (`< 50–60 m²`) and nearest-neighbor spacing. |
| Land-Use Mask | OpenStreetMap (2024-01-01) | Geofabrik / OSM | Vector polygons | Masks `21,135` non-residential zones (factories, ports, malls, offices) prior to built-form metrics. |
| Urban Envelope | EC JRC GHSL (`BUILT` / `SMOD`) | [Pesaresi et al. (2024)](https://doi.org/10.1080/17538947.2024.2390454) | `10–100 m` / `1 km` | Urban extent mask for baselines and inequality; conditional residential share (`ghs_res_share`). |
| Optical Imagery | Copernicus Sentinel-2 L2A | ESA / GEE | `10 m` VNIR | Cloud Score+ dry-season NDVI and prospective residential-masked `10 m` GLCM roof texture. |
| Surface Heat | Landsat 8/9 C2 L2 (`ST_B10`) | USGS / GEE | `100 m` native (`30 m` grid) | Intra-urban surface temperature anomaly (`ΔLST`); multi-year compositing pending. |
| Ground Truth | DKI Pergub 90 & Karawang Kotaku | DKI / PUPR | RW / RT polygons | Validation labels only (`438` DKI RWs `KAT 1–4`; `100` stratified Karawang RTs); never model inputs. |

## 3.3 Masking, Compositing, and Feature Preparation Protocol
Open layers are prepared across three standardized steps prior to Section 4's individual indicator evaluations, noting explicitly where updated Stage 3 extraction runs remain scheduled:

1. **Non-residential filtering and building spacing:** All footprints intersecting the `21,135` OSM non-residential zones are removed before computing small-footprint residential building share (`< 50 m²`, paired with `< 60 m²` sensitivity checks) and 25th-percentile nearest-neighbor roof distance (`res_nn_p25`). Because the cached building-footprint extract carries a uniform `0.85` confidence value, confidence-cutoff sweeps are noted as a data-extract limitation rather than simulated.
2. **Multi-year Landsat compositing without coarse thermal fallback:** In preliminary 2023 single-season extraction over Mainland DKI Jakarta, strict clear-sky `100 m` Landsat 8/9 (Tier-1) observations covered only `55.8%` of mainland cells, while `25.3%` fell back to `1 km` MODIS (Tier-3) and `14.6%` remained missing. Because `1 km` MODIS fallback smears neighborhood heat contrasts, the preparation protocol removes Tier-3 MODIS entirely and switches to multi-year dry-season clear-sky Landsat 8/9 compositing (scheduled in Stage 3) referenced against each city's urban built baseline ([Chakraborty & Lee, 2019](https://doi.org/10.1016/j.jag.2018.09.015); [Stewart & Oke, 2012](https://doi.org/10.1175/BAMS-D-11-00019.1)).
3. **Candidate Sentinel-2 texture and final variable pool:** Currently cached imagery stores only preview `200×200` thumbnails; Stage 3 execution will extract full-grid `10 m` Sentinel-2 GLCM texture restricted to residential zones and screen it against macro-density alongside the core variables below:

| Physical Domain | Variable Name | Status | Operational Definition |
| :--- | :--- | :--- | :--- |
| Built Form | `res_share_lt50` | **Core** | Share of masked residential footprints `< 50 m²` (`< 60 m²` sensitivity check). |
| Built Form | `res_nn_p25` | **Core** | 25th-percentile nearest-neighbor distance (m) across masked residential roofs. |
| Built Form | `ghs_res_share` | **Conditional** | Residential share of built-up surface inside the urban extent (flags industrial encroachment). |
| Roof Texture | `s2_res_glcm_*` | **Candidate** | Residential-masked `10 m` Sentinel-2 GLCM contrast/entropy (pending full extraction and screen). |
| Micro-Environment | `ndvi` | **Core** | Urban-masked Sentinel-2 dry-season canopy greenness. |
| Micro-Environment | `dlst_intra` | **Core** | Multi-year `100 m` Landsat 8/9 LST minus urban built baseline (K; Tier-1 only). |
