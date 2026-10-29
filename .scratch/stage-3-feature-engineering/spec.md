Status: ready-for-agent

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
