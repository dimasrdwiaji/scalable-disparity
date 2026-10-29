# 01: Pedestrian Network Isochrones & Amenity Reachability

**What to build:** Implement batched pedestrian accessibility routing in `src/phys_living_index/features/isochrones.py`. Given an undirected pedestrian network (from OSMnx) and POI points (from Overture), snap H3 centroids and POIs to the nearest network nodes, construct a sparse adjacency matrix, compute shortest paths via `scipy.sparse.csgraph.dijkstra` with a $1,000\text{ m}$ cutoff, and calculate the cumulative reachable amenity count ($A_{\text{amenity}}$) per H3 cell.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] A pure snapping function maps arbitrary (lon, lat) coordinates to the nearest network node indices, unit-tested on synthetic coordinates and node fixtures.
- [ ] A pure graph builder converts node coordinates and edge line strings (with length in meters) into a `scipy.sparse.csr_matrix` adjacency representation.
- [ ] A vectorized Dijkstra function computes shortest-path distances from origin node indices to all network nodes, capping results at `cutoff_meters` (default 1000m).
- [ ] An amenity-counting function tallies reachable POI counts per H3 origin cell.
- [ ] Thin wrapper function `compute_amenity_accessibility` coordinates loading, graph construction, routing, and returns a `pd.Series` indexed by H3 ID.
