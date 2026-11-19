# 3. Study Area and Data Preparation

## 3.1 Study Domain and Spatial Grid
The primary study domain spans Greater Jakarta (*Jabodetabek*) and Karawang Regency in West Java, Indonesia, bounded by `106.35°E–107.65°E` and `6.75°S–5.95°S` ($\approx 12,800\text{ km}^2$; Figure 1) and projected to UTM Zone 48S (`EPSG:32748`) for metric calculations. Sub-regions serve three distinct roles:

- **Primary urban core (Mainland DKI Jakarta):** Evaluates block-scale discrimination and severity grading across dense central *kampungs* (such as neighborhoods near Menteng and Cikini; [Hidayati et al., 2020](https://doi.org/10.1080/17549175.2020.1814391); [Mardhotillah & Gamal, 2018](https://doi.org/10.14716/ijtech.v9i7.2519)) and planned formal estates. Official Governor Regulation (Pergub) No. 90/2018 records delineate `438` mainland neighborhood units (*Rukun Warga*, RW; `~107 km²`) across four severity tiers (*Kategori* 1–4).
- **Secondary urban–rural transition (Karawang Regency):** Stress-tests indicator behavior outside megacity cores across industrial corridors and irrigated rice plains ([Wardhani, 2016](https://doi.org/10.18196/jgp.2016.0025)). Government *Kotaku* records delineate `100` small neighborhood pockets (*Rukun Tetangga*, RT; `2.83 km²`, median `2.6 ha`), stratified into density terciles to assess floodplain settlements and scale mismatch inside larger hexagons.
- **Excluded baseline and external hold-out city:** Municipal *Kotaku* polygons in Depok (`199.772 km²` against a `199.511 km²` city boundary) cover the entire municipality rather than localized pockets and are excluded. An independent external hold-out city tests geographic transferability without local retuning.

![Figure 1: Regional setting across Greater Jakarta (Jabodetabek) and Karawang Regency](../latex/figures/study_area_map.png)
*Figure 1. Regional setting across Greater Jakarta (Jabodetabek) and Karawang Regency (~12,800 km²), showing provincial and municipal boundaries across DKI Jakarta, Banten, and West Java along with major ports, commercial cores, and upland terrain.*

To avoid administrative boundary distortions (Openshaw, 1984), spatial layers are aggregated onto an Uber H3 Resolution-8 grid ([Sahr et al., 2003](https://doi.org/10.1559/152304003100011090)), where each hexagon spans $\approx 0.737\text{ km}^2$ (`73.73 ha`; edge length $\approx 531\text{ m}$). Confined urban-extent masks intersect GHSL Settlement Model (`GHS-SMOD`) urban classes (`{21, 22, 23, 30}`) with cells containing at least one non-industrial residential footprint, restricting baselines and inequality metrics to built-up neighborhoods without relying on `GHS-POP`.

## 3.2 Vetted Open Dataset Inventory
Following Section 2's vetting criteria, only global open datasets that avoid coarse block smearing, circular population ratios, nightlight saturation, and service-proximity inversion enter the pipeline (Table 1). Disqualified layers—including `GHS-POP`, VIIRS nightlights, Sentinel-5P and `PM2.5` atmospheric grids, `1 km` MODIS fallbacks, `GLO-30` terrain slopes, flood layers, Overture/OSM service counts, and Meta's Relative Wealth Index—are excluded.

| Group | Dataset | Source | Resolution | Role in Revised Pipeline |
| :--- | :--- | :--- | :--- | :--- |
| Spatial Grid | Uber H3 (Res 8) | Uber H3 | `0.737 km²` / `~531 m` edge | Equal-area spatial units and 6-neighbor adjacency graph for baselines and GAT-AE. |
| Built Footprints | Open Buildings (Google / Vida) | [Sirko et al. (2021)](https://arxiv.org/abs/2107.12283) | Sub-meter footprints | Small-footprint residential buildings (`< 50–60 m²`) and nearest-neighbor spacing. |
| Land-Use Mask | OpenStreetMap (2024-01-01) | Geofabrik / OSM | Vector polygons | Masks `21,135` non-residential zones (factories, ports, malls, offices) prior to built-form metrics. |
| Urban Envelope | EC JRC GHSL (`BUILT` / `SMOD`) | [Pesaresi et al. (2024)](https://doi.org/10.1080/17538947.2024.2390454) | `10–100 m` / `1 km` | Urban extent mask for baselines and inequality; conditional residential share (`ghs_res_share`). |
| Optical Imagery | Copernicus Sentinel-2 L2A | ESA / GEE | `10 m` VNIR | Cloud Score+ dry-season NDVI and candidate residential-masked `10 m` GLCM roof texture. |
| Surface Heat | Landsat 8/9 C2 L2 (`ST_B10`) | USGS / GEE | `100 m` native (`30 m` grid) | Multi-year dry-season intra-urban surface heat anomaly (`ΔLST`); no `1 km` MODIS fallback. |
| Ground Truth | DKI Pergub 90 & Karawang Kotaku | DKI / PUPR | RW / RT polygons | Validation labels only (`438` DKI RWs `KAT 1–4`; `100` stratified Karawang RTs); never model inputs. |

## 3.3 Masking, Compositing, and Feature Preparation Protocol
Open layers pass through three standardized steps before single-indicator screening:

1. **Non-residential filtering and building geometry:** Footprints intersecting the `21,135` OSM non-residential zones are removed before computing small-footprint share (`< 50 m²`, paired with a `< 60 m²` sensitivity check) and 25th-percentile nearest-neighbor centroid spacing (`res_nn_p25`). Because this building-footprint extract assigns a uniform `0.85` confidence score across polygons, confidence-threshold sensitivity sweeps cannot be run on it.
2. **Multi-year 100 m thermal compositing and local baseline:** Single-season cloud masking over humid tropical cities leaves substantial thermal gaps; in preliminary 2023 dry-season extraction over Mainland DKI Jakarta, clear-sky `100 m` Landsat 8/9 observations covered `55.8%` of cells while `25.3%` fell back to `1 km` MODIS and `14.6%` remained missing. To prevent `1 km` thermal smearing, we drop MODIS fallback completely and widen clear-sky Landsat 8/9 dry-season compositing progressively across `2023`, `2022–2024`, and `2021–2025` windows ([Voogt & Oke, 2003](https://doi.org/10.1016/S0034-4257(03)00079-8)). Intra-urban surface heat anomaly (`dlst_local_ring_k5`) subtracts the median temperature of urban-masked neighbors within a `k = 5` hexagonal ring (`~2.6 km`), pairing with a citywide urban-median baseline for sensitivity ([Chakraborty & Lee, 2019](https://doi.org/10.1016/j.jag.2018.09.015); [Stewart & Oke, 2012](https://doi.org/10.1175/BAMS-D-11-00019.1)).
3. **Candidate roof-texture screening pool:** Full-resolution `10 m` Sentinel-2 Cloud Score+ dry-season composites supply urban canopy greenness (`ndvi`) alongside residential-masked GLCM contrast and homogeneity (`s2_res_glcm_*`, `3×3` window). Both texture metrics and `ghs_res_share` enter the candidate pool to be screened empirically against macro-density and official settlement records alongside the four core indicators below:

| Physical Domain | Variable Name | Status | Operational Definition |
| :--- | :--- | :--- | :--- |
| Built Form | `res_share_lt50` | **Core** | Share of masked residential footprints `< 50 m²` (`< 60 m²` sensitivity check). |
| Built Form | `res_nn_p25` | **Core** | 25th-percentile nearest-neighbor centroid distance (`m`) across masked residential roofs. |
| Built Form | `ghs_res_share` | **Conditional** | Residential share of built-up surface inside the urban extent (flags industrial encroachment). |
| Roof Texture | `s2_res_glcm_*` | **Candidate** | Residential-masked `10 m` Sentinel-2 GLCM contrast and homogeneity (`3×3` window; screened before selection). |
| Micro-Environment | `ndvi` | **Core** | Urban-masked `10 m` Sentinel-2 dry-season canopy greenness. |
| Micro-Environment | `dlst_local_ring_k5` | **Core** | Multi-year `100 m` Landsat 8/9 LST minus `k = 5` urban-ring median (`K`; citywide median sensitivity). |
