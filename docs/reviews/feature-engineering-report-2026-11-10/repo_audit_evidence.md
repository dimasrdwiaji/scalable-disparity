# Repository Audit Evidence Pack (orchestrator-produced; not a reviewer output)

Compiled by recomputing the report's tables from the repository's current outputs on 2026-11-09. Repo: `C:\Users\Dimas RD\Documents\projects\phys_living_index`, HEAD `80f716b` plus uncommitted edits. Outputs dated 2026-11-09: `data/interim/h3_features_raw.parquet`, `data/processed/feature_matrix_7d.parquet`, `data/processed/stage3_qa.json`.
Treat every line as a fact to be weighed. A mismatch may be a stale report, a stale output, or a real error; the pack does not say which. Reviewers may open repository files read-only to check anything here. Stratification reproduced by point-in-polygon of cell centroids in `data/interim/admin_boundaries_study_area.geojson`, with "DKI" = names containing Jakarta (excluding none; 1 Kepulauan Seribu cell falls in DKI), "Kota" = Kota Bekasi + Kota Depok + South Tangerang City + Kota Bogor, "Kab" = everything else. That rule reproduces the report's N exactly (860 / 926 / 7,559).

## A. Definition and pipeline: report text vs. code/config

| Item | Report says | Repository does | Location |
|---|---|---|---|
| Residential filter | Pop >= 50 AND residential building area > 0 (§2.1) | density >= 300 persons/km² AND building_count >= 1. Min population among the 9,345 cells is 221.8 | `benchmarks_v1.yaml` residential block; `stage3.py:669` |
| Feature vector element 2 | Footprint per capita A_fp,res/Pop (§1, §6.2 "Resolution: shifting to 2D ground footprint") | Channel 1 of the 7-D matrix is `space_sufficiency_ratio` = GHS-BUILT-V residential volume / 3.0 / GHS-POP / 9. Footprint per capita is NOT a matrix channel | `stage3.py:704-708`; `benchmarks_v1.yaml` channels; columns of `feature_matrix_7d.parquet` |
| R_space derivation | Footprint × floor(h/3) from Google heights (§2.2) | The channel uses GHS-BUILT-V volume / 3 (see above) | `stage3.py:705` |
| Compactness aggregation | Area-weighted mean Polsby-Popper (§2.2) | Unweighted MEDIAN of building Polsby-Popper | `stage3.py:544` |
| Irregular-share "Resolution" (§6.3) | Replace mean circularity with I<0.55 or area variance | Not implemented; channel 3 is still compactness | `benchmarks_v1.yaml` |
| Building footprints | Google Open Buildings v3 | Overture Maps buildings theme (conflated sources) | `scripts/run_ingestion.py:83` |
| Footprint geometry | Area(B_k ∩ H_i) | Building assigned wholly to the cell of its centroid; area is an eave-corrected "wall" area: area − perimeter×0.5 m + π·0.25. Eave correction is undisclosed | `stage3.py:513-515`; `configs/default.yaml` eave_offset_m |
| Residential mask | GHS-BUILT-C 10 m residential land mask (§2.2, §3, §4.1) | No GHS-BUILT-C in the pipeline. Non-residential removed by OSM land-use zones plus geometric heuristics (>=2,500 m² & <=3 floors; >=1,000 m² & rectangularity >=0.85 & <=2 floors); GHS-BUILT-S NRES ratio is used for floor area only | `stage3.py:518-528, 678-697` |
| Heights | "Google Open Buildings (stereo/shadow ML)" | Only 0.066% of footprints have an explicit height (`stage3_qa.json` buildings) | QA |
| Walk speed / cutoff | 4.5 km/h, 1,125 m (§2.2) | 4.0 km/h, 15 min = 1,000 m | `configs/default.yaml:104-105`; `accessibility.parquet` provenance cutoff_m = 1000 |
| Routing method | `city2graph.utils.spatial.create_isochrone` | Batched SciPy Dijkstra; cached layer dated 2026-11-02 is what feeds the matrix (raw amenities_15m == layer: True). A city2graph function exists in `isochrones.py` but `stage3.py:631` calls `compute_amenity_accessibility` | `stage3.py:614-634` |
| POI source and set | OSM; "essential": healthcare, education, basic commerce (§2.2, §3) | Overture Places 2026-10-21 + base land-use; 173,820 POIs incl. restaurants, cafes, ATMs, banks, government offices, all places of worship, parks | `configs/default.yaml` amenity_categories; ADR 0004 |
| ΔLST baseline | 10th percentile LST across vegetated peri-urban cells (§2.2) | Median LST of non-residential, GHS-SMOD rural, veg-probability>=0.5 cells = 305.45 K (P10 of the same set = 299.01 K) | `build_features.py:331`; `stage3_qa.json` heat_island |
| DEM | Copernicus GLO-30 / FABDEM (§2.2, §3, §6.5) | Copernicus GLO-30 only (`COPERNICUS/DEM/GLO30_2024_1`), a surface model. FABDEM absent from code | `gee_layers.py:43, 457` |
| Landsat window | 2022–2024 composite (§3) | Tiered: Jun–Sep 2023 first, wider windows on failure, final tier 2022–2024 | `configs/default.yaml` |
| Modelled universe | N = 9,345 throughout | `is_modelled` = 8,375. 970 residential cells excluded: 894 LST failure (tier 0), 85 no compactness (overlap possible) | `feature_matrix_7d.parquet`, QA |
| f_veg | "Vegetation Cover Fraction", dimensionless [0,1], lower = deprivation | Mean NDVI, min −0.241 among residential; benchmark orientation is `context` (no direction) | QA; `benchmarks_v1.yaml` |
| Benchmark status | not discussed | `benchmarks_v1.yaml` has `provisional: false`, but its channels are identical to v0, it has no `reference_sample` block, and three channels still say `bound_source: provisional`. ADR 0003 requires a global reference sample (ticket 14) | `configs/benchmarks/` |
| Clipping | not discussed | `space_sufficiency_ratio`: 74.4% of residential cells exceed upper bound 6.0 (flag `outside_reference: true`); modelled median scaled value = 1.0. Lambda upper bound 0.85 vs observed max 0.482, so inverted scaled range is 0.433–1.0 | QA clip_shares; matrix describe |
| Hex geometry | Edge 461.4 m; centroid distance 922.7 m | `h3.average_hexagon_edge_length(8,'m')` = 531.4 m; a regular hexagon of 0.737 km² has edge ≈ 532.6 m. Neighbour centroid spacing near Jakarta 936.6 m (√3·edge ≈ 920) | h3 v4 library |

## B. Reported numbers vs. recomputed

### Universe
| Quantity | Report | Recomputed |
|---|---|---|
| Residential cells | 9,345 | 9,345 |
| Residential area km² | 6,992.4 | 6,963.98 |
| Residential population | 32.10 M | 40.48 M (QA all-cell total 40.73 M) |
| DKI pop | 10,846,531 | 10,846,220 |
| Kota pop | 6,334,180 | 9,097,882 |
| Kab pop | 14,923,410 | 20,532,840 |
| Kota density /km² | 6,840 | 13,171 (note: report's own 6,334,180 / 692.81 = 9,143) |
| Kab density /km² | 2,638 | 3,647 |
| DKI density /km² | 16,830 | 16,865 |

### Table 5.2 (all residential cells; Min / P10 / Median / Mean / P90 / Max / IQR)
| Indicator | Report | Recomputed |
|---|---|---|
| lambda_p,res | .0001 / .012 / .062 / .098 / .231 / .482 / .119 | 0 / .0181 / .0619 / .0941 / .2256 / .4817 / .1049 |
| FP per capita | .12 / 7.85 / 26.40 / 39.81 / 78.14 / 482.1 / 42.10 | 0 / 10.83 / 24.21 / 29.58 / 55.50 / 313.5 / 26.85 |
| R_space (GHS volume/3/pop) | 20.31 / 27.42 / 57.18 / 74.65 / 132.4 / 612 / 56.80 | min 20.30, median 57.18, mean 55.36, Q1 50.26, Q3 58.45, max 77.94 |
| C_res | .412 / .681 / .724 / .720 / .758 / .841 / .046 | .5448 / .7363 / .7513 / .7493 / .7617 / .7854 / .0123 (98.9% of cells in 0.65–0.80) |
| Amenity | 0 / 0 / 4 / 29.4 / 88 / 542 / 21 | 0 / 0 / 4 / 31.17 / 94 / 1,352 / 24; 21.4% of cells are zero |
| NDVI | −.082 / .214 / .448 / .418 / .582 / .791 / .246 | −.241 / .2138 / .415 / .412 / .6036 / .7792 / .2138 |
| ΔLST K (n = 8,451) | −6.42 / −2.11 / +.13 / +.42 / +3.18 / +8.21 / 2.84 | −36.48 / +1.47 / +5.85 / +6.24 / +11.61 / +25.09 / 5.89 |
| Slope share % | 0 / 0 / 0 / 2.2 / 5.4 / 68.4 / 0 | 0 / 0 / 0 / 3.95 / 13.21 / 83.63 / 1.22; 59.9% of cells exactly zero |

### Table 5.3 (DKI | Kota | Kab)
| Indicator | Report | Recomputed |
|---|---|---|
| lambda median | 23.0 | 13.2 | 4.8 % | 23.0 | 18.8 | 5.0 % |
| lambda P90 | 33.4 | 21.5 | 12.1 % | 33.4 | 27.7 | 15.1 % |
| gross lambda aggregate | 28.75 | 16.5 | 6.2 % | 28.8 | 21.0 | 8.6 % |
| FP/cap mean | 13.00 | 21.40 | 49.60 | 13.14 | 14.98 | 33.24 (population-weighted aggregates: 12.97 | 14.11 | 18.84) |
| FP/cap P5 | 2.92 | 6.85 | 14.20 | 2.89 | 9.58 | 8.17 |
| Amenity median | 158 | 38 | 2 | 126 | 58 | 2 |
| NDVI mean | .178 | .321 | .482 | .210 | .303 | .448 |
| ΔLST mean K | +2.78 | +1.42 | −.38 | +10.90 | +9.79 | +5.28 |
| Slope mean % | 0.00 | .15 | 2.82 (max 68.4) | 0.2 | 0.6 | 4.8 (DKI max 9.5; Kab max 83.6) |

### Table 5.4 (DKI municipalities; report → recomputed)
| Municipality | N | Pop | Agg lambda % | FP/cap agg | FP/cap P5 | Median POI | ΔLST |
|---|---|---|---|---|---|---|---|
| Barat | 174→167 | 2.584M→2.698M | 28.12→27.7 | 12.82→12.82 | 2.92→8.17 | 184→123 | +3.42→+11.09 |
| Pusat | 68→64 | 1.082M→0.940M | 23.51→23.2 | 11.81→11.81 | 3.14→4.61 | 262→351 | +3.18→+11.26 |
| Selatan | 202→196 | 2.385M→2.330M | 23.94→23.6 | 14.85→14.85 | 5.41→7.70 | 164→171 | +2.15→+10.82 |
| Timur | 256→249 | 3.248M→3.062M | 21.32→21.0 | 12.78→12.78 | 4.88→1.52 | 148→106 | +2.64→+11.61 |
| Utara | 160→184 | 1.547M→1.817M | 14.82→15.5 | 11.88→11.72 | 2.84→0.08 | 92→54 | +3.21→+9.24 |

## C. Claims about extremes and geography
- Maximum lambda 0.4817 is at cell 888c12b6e5fffff (−6.120, 106.905), admin Jakarta Utara, FP/cap 26.39 m². Report §5.4 places 48.2% in Jakarta Barat kampungs (Tambora, Kali Anyar, Jembatan Besi). Highest Jakarta Barat lambda is 0.451.
- The low tail of FP/cap is dominated by the non-residential filter: 338 residential cells have FP/cap < 5, and 93.7% of the footprint in those cells was removed as non-residential. The 12 lowest cells have net footprint exactly 0 with 100% of footprint removed (e.g. 888c107a2bfffff in Jakarta Timur: population 1,837, 154,561 m² removed; 888c1040cdfffff in Kab. Bekasi: population 7,532, 236,116 m² removed). 27 of 860 DKI cells have FP/cap < 1. Share of footprint removed: DKI 23.9%, all residential 19.4%.
- Kabupaten stratum in the report's N = 7,559 contains 870 cells outside every polygon in the admin file (pop 1.27 M; 845 have lon > 107.2, i.e. eastern part of the box outside the admin file), plus 242 cells of "Tangerang" (the Kota Tangerang polygon, distinct from "Kabupaten Tangerang"), although §5.1 lists Tangerang as a Kota Bodetabek unit. Cells also fall in Serang (121), Bandung Barat (77), Kab. Sukabumi (3), which §5.1 does not list.
- Executive Summary says 83.8% peri-urban/rural; §5.1 says 80.9%.

## D. Missingness (LST)
- 894 of 9,345 residential cells (9.6%) have no LST after all tiers. Rate by unit: Jakarta Utara 34.2%, Jakarta Barat 32.9%, Kab. Tangerang 25.2%, Bandung Barat 23.4%, Tangerang 17.4%, South Tangerang 14.3%, Karawang 10.9%, Kab. Bekasi 8.6%. Modelled share by stratum: DKI 721/860 (83.8%), Kota 882/926 (95.2%), Kab 6,772/7,559 (89.6%).
- `stage3_qa.json`: residential LST tier shares tier 1 74.8%, tier 2 2.8%, tier 3 12.8%, tier 0 9.6%; `tier3_share_flag.lst = true` (ADR 0002 says revisit the window before training if Tier 3 > 10%). Sentinel-2 is tier 1 for 100%.
- LST all-cell range 258.0–330.5 K; residential min 268.97 K; ΔLST < −10 K in 2 residential cells.
- Sanity Spearman (residential): NDVI vs Dynamic World veg probability 0.90; Landsat vs MODIS LST 0.88.
- Epoch gap: 20.8% of residential cells change built surface > 10% between GHS-BUILT-S 2020 and 2025 (median 2.0%).
- Mask sensitivity: residential cells 10,308 (150/km²), 9,345 (300), 5,483 (1,500).

## E. Correlation structure (Spearman, residential cells)
| | lambda | FP/cap | C_res | Amenity | NDVI | ΔLST | Slope | Density | Dist. to Monas |
|---|---|---|---|---|---|---|---|---|---|
| lambda | 1 | −.44 | −.39 | .79 | −.57 | .63 | −.28 | .87 | −.52 |
| FP/cap | | 1 | .31 | −.59 | .65 | −.63 | .30 | −.78 | .51 |
| C_res | | | 1 | −.38 | .36 | −.41 | .15 | −.42 | .29 |
| Amenity | | | | 1 | −.64 | .65 | −.32 | .82 | −.56 |
| NDVI | | | | | 1 | −.76 | .60 | −.72 | .65 |
| ΔLST | | | | | | 1 | −.49 | .74 | −.64 |
| Slope | | | | | | | 1 | −.34 | .41 |
| Density | | | | | | | | 1 | −.61 |

Net residential footprint vs population ρ = .874; population vs GHS-BUILT-S ρ = .969.

## F. Susenas comparison already in `stage3_qa.json` (not presented in the report)
Modelled population-weighted median floor area per capita vs. Susenas 2023 median, 16 units with a match (DKI municipalities all share the provincial value 12.27 m²): ratio mean 1.37, min 0.92, max 2.11; DKI municipalities 1.65–2.11. Spearman across the 16 units −0.21 (units are not independent because DKI values repeat). Share at or below 7.2 m²/capita: modelled DKI municipalities 0–11.2% vs. Susenas 22%. This comparison uses the pipeline's modelled floor area, not footprint per capita.

## G. Citation resolution (Crossref API, 2026-11-09)
| Cited in report | Result |
|---|---|
| Kuffer et al. 2016, "Extraction of slum areas from VHR imagery ... Ahmedabad", Remote Sensing 8(6) 455, 10.3390/rs8060455 | DOI resolves to Kuffer, Pfeffer, Sliuzas, "Slums from Space—15 Years of Slum Mapping Using Remote Sensing". Title and author list in report are wrong |
| Taubenböck et al. 2018, RSE 207, 377–393, 10.1016/j.rse.2017.10.044 | DOI resolves to an unrelated soil-moisture paper (Wang et al.). The Arrival City paper is Applied Geography 92, 150–167, 10.1016/j.apgeog.2018.02.002 |
| Sliuzas, Mboup, de Sherbinin 2010, Landscape and Urban Planning 98(1), 10.1016/j.landurbplan.2010.04.001 | DOI resolves to an unrelated corrigendum on ecological networks in Turkey. No matching paper found by title search |
| Estoque et al. 2017, Applied Geography 84, 14–26, 10.1016/j.apgeog.2017.04.008 | DOI resolves to an unrelated river-management paper (Marçal et al.). No matching paper found by title search |
| Estudillo et al. 2021, Geocarto Int., 10.1080/10106049.2021.1920633 | DOI resolves to an unrelated cotton evapotranspiration paper. No matching paper found by title search |
| Zhou et al. 2019, Earth's Future 7(1), 10.1029/2018EF001099 | DOI not found. The paper exists as Remote Sensing 11(1), 48, 10.3390/rs11010048 |
| Kuffer et al. 2020, Habitat International 102, 102212 (IDEAMAPS) | DOI not found. Closest real paper: Remote Sensing 12(6), 982, 10.3390/rs12060982 |
| Grimmond & Oke 1999, 38(9), 1222–1244, ...<1222:AEROBF>... | DOI not found. Crossref: J. Applied Meteorology 38, 1262–1292, ...<1262:apouad>... |
| Moreno et al. 2021 inline link 10.1080/23748834.2021.1944282 | Inline DOI not found; reference-list DOI 10.3390/smartcities4010006 is correct |
| Chakraborty et al. 2019 inline link 10.1016/j.envres.2019.108744 | Inline DOI resolves to an unrelated paper (Li et al.); reference-list DOI 10.1088/1748-9326/ab3b99 is correct |
| Stewart & Oke 2012; Geurs & van Wee 2004; Voogt & Oke 2003; Barrington-Leigh & Millard-Ball 2017 | Resolve correctly |
| Sirko et al. 2021 arXiv:2107.12242 | Not on Crossref (arXiv preprint); not checked further |
| SNI 03-1733-2004; PermenPU 20/PRT/M/2007; UN-Habitat 2003/2018 | Not machine-checkable here |
