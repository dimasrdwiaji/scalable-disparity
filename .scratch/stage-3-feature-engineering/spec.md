Status: complete (Revision 5 closed; 7-channel matrix regenerated and verified)

# Spec: Stage 3 — Feature Engineering & Pedestrian Isochrones

Source: `.scratch/project-roadmap/map.md` (Stage 3), `docs/research_plan.md`, `docs/adr/0001-h3-gat-ae-unsupervised-disparity.md`, and reviewer recommendation `REV-1` & `REV-3`.

## Problem Statement

While data ingestion modules for buildings, population, environmental layers, atmospheric metrics, and Overture POIs are now implemented, the raw data cannot yet be fed into the Graph Attention Autoencoder (GAT-AE). Specifically:
1. `src/phys_living_index/features/isochrones.py` is currently a placeholder stub that simply returns inputs without calculating actual network pedestrian accessibility.
2. In dense commercial Central Business Districts (CBDs) and non-residential hubs, residential floor area per capita ($R_{\text{space}}$) and nighttime lights per capita ($E_{\text{night}}$) can produce extreme outlier spikes due to near-zero population denominators, distorting normalized feature channels.
3. The 10-dimensional feature matrix $X \in \mathbb{R}^{N \times 10}$ on Uber H3 Resolution 8 cells (~0.74 km²) must be systematically constructed, winsorized at the 99th percentile ($P_{99}$), and bounded in $[0.0, 1.0]$ via domain-grounded physical benchmarks.

## Solution

Build out the full Stage 3 feature engineering pipeline:
1. Implement vectorized, batched pedestrian network routing in `src/phys_living_index/features/isochrones.py` using OSMnx to acquire walkable network geometry and `scipy.sparse.csgraph.dijkstra` for batched multi-source shortest paths within a 15-minute ($1,000\text{ m}$ at $4\text{ km/h}$) cutoff.
2. Calculate cumulative 15-minute walk access to formal public amenities ($A_{\text{amenity}}$: schools, clinics, parks, supermarkets) from H3 cell centroids snapped to the pedestrian graph.
3. Implement $P_{99}$ winsorization on $R_{\text{space}}$ and $E_{\text{night}}$ in `src/phys_living_index/features/build_features.py` before universal Min-Max normalization.
4. Harmonize all 10 feature channels onto the H3 Res-8 spatial grid into a clean $(N \times 10)$ numpy matrix ready for GAT-AE modeling.

## User Stories

1. As a spatial data scientist, I want `snap_points_to_network` to snap H3 geometric centroids to the nearest nodes or edges in the walkable street network, so that network routing originates from valid physical paths.
2. As a spatial data scientist, I want `compute_pedestrian_network_distance_matrix` to construct a sparse graph adjacency representation of the pedestrian street network and compute shortest path distances up to $1,000\text{ m}$ via `scipy.sparse.csgraph.dijkstra`, so that accessibility is computed rapidly across thousands of centroids.
3. As a researcher, I want `count_reachable_amenities` to sum all Overture POIs (schools, clinics, parks, food/groceries) within the $1,000\text{ m}$ pedestrian catchment for each H3 cell, so that $A_{\text{amenity}}$ reflects real walkable amenity choice.
4. As a machine learning engineer, I want $R_{\text{space}}$ and $E_{\text{night}}$ winsorized at their 99th percentiles ($P_{99}$) prior to Min-Max scaling, so that commercial CBD denominator artifacts do not collapse the variance across residential settlements.
5. As a researcher, I want $R_{\text{space}}$ calibrated against the UN-Habitat $9.0\text{ m}^2$ shelter threshold, such that a ratio of $1.0$ represents exact standard sufficiency.
6. As a machine learning engineer, I want `build_10d_feature_matrix` to assemble the full 10-dimensional array $X \in [0.0, 1.0]^{N \times 10}$ with all inverted hazard channels (heat, $\text{PM}_{2.5}$, multi-pollutant AQI) aligned so higher values indicate superior living standards.
7. As a test engineer, I want pure unit tests verifying Dijkstra distance calculations, winsorization clipping, and amenity counting without relying on live external network downloads.

## Implementation Decisions

- **Routing Engine**: Use `osmnx` for downloading/extracting undirected pedestrian networks and `scipy.sparse.csgraph.dijkstra` for multi-source distance calculations (as decided in wayfinder ticket 04).
- **Amenities Considered**: Formal public amenities from Overture: `education.school`, `healthcare.hospital`, `healthcare.clinic`, `commercial.supermarket_grocery`, and `base` park/leisure spaces.
- **Pure / Thin Seam**:
  - Pure functions: Graph creation from node/edge tables, sparse matrix distance computation, snapping coordinate mapping, amenity counting, $P_{99}$ winsorization, and 10D matrix normalization.
  - Thin execution: Network acquisition from OSMnx and file I/O.
- **Winsorization**: Configurable percentile (default 99.0%), clipping extreme outliers to the $P_{99}$ value before linear scaling to $[0.0, 1.0]$.
- **Inverted Scalers**: Inverted features ($\text{LST}_{\text{inv}}$, $\text{PM25}_{\text{inv}}$, $\text{AQI}_{\text{inv}}$) computed as $1.0 - \text{norm}(x)$ so that $1.0$ consistently indicates maximum environmental quality/comfort.

## Testing Decisions

- Test graph snapping and batched Dijkstra shortest paths on synthetic grid/linear graphs with known edge weights.
- Test amenity count aggregation against synthetic POI point distributions.
- Test $P_{99}$ winsorization on distributions containing deliberate extreme outlier spikes.
- Test that all columns of the output feature matrix $X$ are bounded strictly in $[0.0, 1.0]$ with no NaNs or Infs.

## Out of Scope

- Model training (GAT-AE) and typology clustering (HDBSCAN) — Stage 4.
- 4-Quadrant validation vs Meta RWI and BPS SUSENAS poverty regression — Stage 5.

---

## Revision 2 (2026-11-02): Data-Input Remediation

Source: Stage 3 review of `stage_3_feature_engineering_report.md` (Revision 3), [ADR 0002](../../docs/adr/0002-reference-epoch-representative-composites-zonal-aggregation.md), [`docs/input_data_resolution.md`](../../docs/input_data_resolution.md).

### Problem Statement

The Revision 3 feature matrix passes its shape, range and NaN checks, but its inputs cannot support Res-8 analysis:

1. **Misregistered rasters.** `scripts/run_ingestion.py` and `ingest_context.py` take one Sentinel-2 / Landsat scene (`features[0]`), decimate it to 200 × 200, and georeference it to the bounding box. Channels 2, 4, 6, 7 and 8 are spatially wrong.
2. **Centroid point sampling.** `sample_raster_at_points` reads one pixel per cell instead of aggregating over the cell.
3. **Unrepresentative time.** VIIRS is one night (2023-12-31); air quality is one `current` Open-Meteo reading from 8 distinct values; the AQI is ozone-driven.
4. **Mixed epochs.** Population 2020, imagery of unknown date, POIs and buildings 2026.
5. **Loose residential mask.** `population >= 10` on a 1 km WorldPop pixel keeps 88% of cells, including 691 with no buildings (scored R_space = 0, i.e. worst overcrowding).
6. **Scaling and weights.** Fixed [−1, 1] benchmarks compress the spectral channels to std 0.04–0.07; Stage 4 inverse-variance weights then inflate them (BSI 3.47 vs R_space 0.06).
7. **Skewed amenities.** 46% of residential cells are zero and ~40% of DKI core cells saturate at the 150 cap.
8. **Mixed orientation.** NDBI, BSI and MNDWI are not oriented "higher = better"; NDBI–BSI ρ = 0.82.
9. **Reproducibility.** OSM accessibility exists only in `scripts/build_osm_pedestrian_features.py`, which patches the interim table; `isochrones.py` is unused in production; ingestion silently writes constant fallback rasters on failure; `scripts/` is untracked.

### Solution

Follow ADR 0002: one 2023 reference epoch; representative dry-season median composites (whole-year for water) with per-cell QA and a window ladder; area-weighted zonal aggregation on Google Earth Engine; source swaps for water, NO₂, PM2.5, LST, night lights and population; a residential cell mask of ≥ 300 persons/km² plus ≥ 1 building. Then, per [ADR 0003](../../docs/adr/0003-universal-frozen-benchmarks-and-channel-weighting.md), scale every channel with universal benchmarks frozen from a global reference sample (never from the study area), keep per-region settings for measurement only, use uniform channel weights (inverse-variance as a sensitivity run), and regenerate the report and `graph_data.pt`.

### Tickets

| # | Ticket | Blocked by | Status |
|---|---|---|---|
| 03 | GEE H3 zonal harness and fail-loud ingestion | — | complete |
| 04 | Sentinel-2 dry-season composite (NDVI, NDBI, BSI) | 03 | complete |
| 05 | Landsat LST dry-season composite | 03 | complete |
| 06 | Dynamic World water frequency | 03 | complete |
| 07 | Population (GHS-POP 2023) and residential cell mask | 03, 10 | complete |
| 08 | VIIRS annual 2023 night-time radiance | 03 | complete |
| 09 | Air quality: ACAG PM2.5 and Sentinel-5P NO₂ | 03 | complete |
| 10 | Buildings epoch alignment and height fill | — | complete |
| 11 | Pedestrian accessibility consolidation and epoch snapshot | — | complete |
| 12 | Universal benchmark scaling, orientation and channel weights (ADR 0003) | 04–11, 14 | complete |
| 13 | Regenerate feature matrix, graph dataset and Stage 3 report | 12 | complete |
| 14 | Global reference sample and `benchmarks_v1` (ADR 0003) | 03–09, 11 | complete (v0 prov) |
| 15 | GHS residential built-surface masking for net living space | 10 | complete |
| 16 | Hierarchical building classification & Susenas calibration | 15 | complete |
| 17 | Ingest GHS-BUILT-V for 3D residential built volume per capita (BVPC_res) | 03 | complete |
| 18 | Residential plan area fraction (λp,res) on GHS residential mask | 10, 16 | complete |
| 19 | Building footprint compactness (4πA/P2) for morphological regularity | 10 | complete |
| 20 | Topographic slope hazardous exceedance share (Option A: slope > 15°) | 03 | in_progress |
| 21 | Retire Tier 3 channels and reconfigure benchmarks for lean feature set | 17–20 | complete |
| 22 | Rebuild Stage 3 feature matrix, QA report, and handoff to Stage 4 | 21 | in_progress |

### Out of Scope

- Retraining the GAT-AE and re-running Stage 4 analyses (they consume the output of ticket 13).
- LST downscaling below 100 m (rejected in ADR 0002).

---

## Revision 3 (2026-11-06): GHS Functional Residential Built-Surface Masking

Source: Evaluation of living space per capita distributions showing commercial/industrial floor space inflation.

### Problem Statement
Because OpenStreetMap and Overture building footprints in Indonesia lack functional classification tags (>99% generic `building=yes`), all building stock (office skyscrapers, shopping malls, factories, logistics warehouses, and schools) was aggregated into the residential floor mass. Dividing total unclassified built floor space by nighttime resident population inflated living floor space per capita to an unweighted cell median of ~45 m²/person (whereas Indonesian residential standards are ~9 to 15 m²/person).

### Solution
Follow ticket 15: Ingest `built_surface_nres` (non-residential built-up surface) alongside `built_surface` from EC JRC GHS-BUILT-S for epochs 2020 and 2025 via GEE zonal reduction. Derive the cell-level 2023 `residential_ratio`:
$$\text{residential\_ratio} = \max\left(0.0, \min\left(1.0, 1.0 - \frac{\text{built\_surface\_nres\_m2}}{\text{built\_surface\_total\_m2}}\right)\right)$$
Scale gross building floor area by `residential_ratio` to produce **Net Residential Floor Area**, recomputing $R_{\text{space}}$ and feature $X_1$ across all cells.


---

## Revision 4 (2026-11-06): Hierarchical Building Classification and Ground-Truth Susenas Calibration

Source: Ground-truth validation against BPS Susenas 2023 survey statistics demonstrating that commercial CBDs and industrial corridors retain 2.0x–2.7x overestimation due to roof overhangs and unclassified large non-residential structures.

### Problem Statement
Even after cell-level GHS 100 m built-surface masking, the population-weighted median living space remains at 28.0 m²/person (unweighted cell median 41.5 m²/person), compared to BPS Susenas 2023 survey targets of 12.3 m²/person for DKI Jakarta and 16.4 m²/person for West Java. Two primary physical factors drive this:
1. Footprint polygons trace the outer roof edges rather than foundation wall perimeters, imparting a +16% to +19% positive bias.
2. Buildings ≥ 500 m² account for 19.7% of total built floor area; many of these (warehouses, factories, mosques, schools, government compounds) are located within residential fabric where 100 m GHSL grid cells fail to isolate them.

### Solution (Ticket 16)
1. **Wall-line Geometry Inward Buffer**: Shrink building polygons inward by 0.5 m (`buildings.eave_offset_m: 0.5`), removing the roof overhang bias.
2. **Hierarchical Building Use Filtering**:
   - Rule 1: OSM non-residential landuse and amenity zones (covers 68.4% of buildings ≥ 2,500 m²).
   - Rule 2: Non-housing Overture place points inside footprint polygons.
   - Rule 3: GHS-BUILT-C 10 m majority functional class (21–25) for medium/large footprints.
   - Rule 4: Large-and-low geometric shape rule (footprints ≥ 2,500 m² with ≤ 3 floors; rectangular ≥ 1,000 m² with ≤ 2 floors).
   - Rule 5: Small home confirmation (< 200 m²).
   - Rule 6: Residual unclassified buildings scaled by rescaled GHS 100 m residential ratio.
3. **Susenas Ground-Truth Calibration**: Validate outputs against `data/external/susenas/bps_susenas_housing_2023.csv` to ensure regional convergence.

---

## Revision 5 (2026-11-09): Feature Architecture Redesign — Physical Morphological Disparity & Dimensionality Reduction

Source: Deep research on spatial disparity drivers, PRISMA 2020 systematic review, empirical collinearity analysis (Spearman rank matrix across 9,345 residential cells), and methodological decisions on assumption-light scalability.

### Problem Statement
1. **Collinearity & Redundancy**: Empirical correlation shows `bare_soil_bsi` is near-perfectly collinear with `builtup_ndbi` ($\rho = 0.966$) and inverted `vegetation_ndvi` ($\rho = -0.865$), double-counting impervious surfaces.
2. **Micro-Scale Artifacts & Confounders**:
   - `nighttime_energy_radiance` (VIIRS DNB) suffers from sensor blooming and commercial light spillover into adjacent deprived kampungs at H3 Res-8 ($\approx 460\text{ m}$).
   - `no2_inv` (Sentinel-5P, $3.5 \times 5.5\text{ km}$) and `air_purity_pm25_inv` (ACAG, $1.1\text{ km}$) operate at coarse regional resolutions that blur neighborhood boundaries, and $\text{NO}_2$ positively confounds with commercial activity and major traffic hubs.
   - `water_frequency` captures permanent open water bodies ($\rho = 0.024$ with living space sufficiency) rather than flash urban drainage ponding under dense roof cover.
3. **Brittle Heuristics in Vertical Floor Modeling**: Subdividing buildings by footprint cutoffs ($< 150\text{ m}^2$) or arbitrary roof pitch deductions lacks universal ground-truth justification outside local survey regions.

### Solution
Refactor the feature architecture into a lean, orthogonal 7-channel physical disparity index grounded in peer-reviewed literature:
1. **3D Structural Shelter Capacity**: Ingest European Commission JRC `GHS-BUILT-V R2023A` (`built_volume_total` minus `built_volume_nres`) to calculate **Residential Built-Up Volume Per Capita** ($\text{BVPC}_{\text{res}}, m^3/\text{person}$) and standardized floor area ($\text{Vol}_{\text{res}} / 3.0\text{ m}$), eliminating polygon floor-guessing and roof-pitch deductions (Ticket 17).
2. **Ground Structural Crowding**: Compute **Residential Plan Area Fraction** ($\lambda_{p,\text{res}} = \sum A_{\text{wall, res}} / A_{\text{cell}}$) on the GHS residential mask to capture 2D ground congestion directly (Ticket 18).
3. **Morphological Regularity**: Calculate **Building Footprint Compactness** ($C = 4\pi A / P^2$) from Open Buildings footprints to separate organic informal accretion ($C < 0.45$) from planned formal developments ($C > 0.65$) (Ticket 19).
4. **Environmental Amenity**: Retain **Vegetation Canopy Fraction** (`vegetation_ndvi`, Sentinel-2 10 m) capturing the urban ecological "luxury effect".
5. **Microclimatic Injustice**: Retain **Thermal Injustice** (`heat_island_intensity_inv`, Landsat-8/9 TIRS $\Delta\text{LST}$) capturing heat vulnerability.
6. **Infrastructural Opportunity**: Retain the existing **15-Minute Pedestrian Accessibility** (`cumulative_amenities_15m`, Overture POIs + OSM walkable network). Exclude street centrality/density metrics per user decision.
7. **Topographic Hazard Exposure**: Ingest 30 m DEM (FABDEM / Copernicus GLO-30) and compute **Hazardous Slope Exceedance Share** (Option A: share of 30 m pixels with slope $> 15^\circ$) inverted so higher values indicate safe buildable terrain (Ticket 20).
8. **Retire Tier 3 Channels**: Drop `bare_soil_bsi`, `nighttime_energy_radiance`, `air_purity_pm25_inv`, `no2_inv`, and `water_frequency` from the feature matrix and frozen benchmark definitions (Ticket 21).
9. **Rebuild & Validate**: Regenerate feature matrix, QA reports, and handoff to Stage 4 GAT-AE (Ticket 22).
