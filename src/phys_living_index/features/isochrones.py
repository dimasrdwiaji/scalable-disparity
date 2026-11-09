"""
Pedestrian network routing and 15-minute walkable amenity accessibility.

Implements batched pedestrian routing over a walkable street network:
- Projecting coordinates to a metric CRS (e.g. UTM) so snap distances are in metres.
- Snapping H3 centroids and POIs to nearest network nodes via cKDTree.
- Constructing sparse CSR adjacency matrices representing street graph geometry.
- Vectorized shortest paths via scipy.sparse.csgraph.dijkstra, keeping only distances at
  POI nodes per batch.
- Remaining-budget rule: the walk from the centroid to its nearest node is deducted from
  the 15-minute distance budget.
- Reachable amenity count and reachable category diversity per cell.
"""

from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree


def project_coordinates(
    lon: np.ndarray,
    lat: np.ndarray,
    crs: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Projects WGS84 (lon, lat) to a metric CRS, returning (x, y) in metres."""
    transformer = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    x, y = transformer.transform(np.asarray(lon), np.asarray(lat))
    return np.asarray(x), np.asarray(y)


def snap_coordinates_to_nodes(
    coords: np.ndarray,
    nodes_df: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Snaps 2D coordinates to nearest network nodes.

    Parameters
    ----------
    coords : np.ndarray
        Array of shape (N, 2) containing point coordinates (same CRS as nodes).
    nodes_df : pd.DataFrame
        DataFrame of network nodes containing 'x' and 'y' columns.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        - Nearest node index in `nodes_df` for each input coordinate (shape N).
        - Planar distance to nearest node (shape N), in the CRS units.
    """
    node_coords = nodes_df[["x", "y"]].to_numpy()
    tree = cKDTree(node_coords)
    distances, indices = tree.query(coords, k=1)
    return np.asarray(indices), np.asarray(distances)


def build_network_adjacency_matrix(
    num_nodes: int,
    edges_df: pd.DataFrame,
    undirected: bool = True,
) -> csr_matrix:
    """
    Constructs a scipy sparse CSR adjacency matrix from network edges.

    Parameters
    ----------
    num_nodes : int
        Total number of nodes in the network graph.
    edges_df : pd.DataFrame
        DataFrame of edges with columns 'u', 'v', and 'length_m'.
    undirected : bool, default True
        Whether the graph is undirected (pedestrian paths are bi-directional).

    Returns
    -------
    csr_matrix
        Sparse adjacency matrix where weights represent distance in meters.
    """
    u = edges_df["u"].to_numpy(dtype=np.int32)
    v = edges_df["v"].to_numpy(dtype=np.int32)
    weights = edges_df["length_m"].to_numpy(dtype=np.float64)

    if undirected:
        row_indices = np.concatenate([u, v])
        col_indices = np.concatenate([v, u])
        data = np.concatenate([weights, weights])
    else:
        row_indices = u
        col_indices = v
        data = weights

    return csr_matrix((data, (row_indices, col_indices)), shape=(num_nodes, num_nodes))


def compute_batched_dijkstra_distances(
    adj_matrix: csr_matrix,
    source_indices: np.ndarray,
    cutoff_meters: float = 1000.0,
) -> np.ndarray:
    """
    Computes shortest-path network distances from source nodes to all graph nodes.

    Parameters
    ----------
    adj_matrix : csr_matrix
        Sparse graph adjacency matrix with distances in meters.
    source_indices : np.ndarray
        1D array of origin node indices.
    cutoff_meters : float, default 1000.0
        Maximum walking distance cutoff in meters (~15 minutes at 4 km/h).

    Returns
    -------
    np.ndarray
        Array of shape (len(source_indices), num_nodes) with shortest path distances.
        Distances exceeding cutoff_meters are set to np.inf.
    """
    dist_matrix = dijkstra(
        csgraph=adj_matrix,
        directed=False,
        indices=source_indices,
        limit=cutoff_meters,
    )
    dist_matrix[dist_matrix > cutoff_meters] = np.inf
    return dist_matrix


def count_reachable_amenities(
    dist_matrix: np.ndarray,
    poi_node_indices: np.ndarray,
    cutoff_meters: float | np.ndarray = 1000.0,
) -> np.ndarray:
    """
    Counts reachable amenities within walking distance for each origin.

    Parameters
    ----------
    dist_matrix : np.ndarray
        Shortest-path distance matrix of shape (num_sources, num_nodes).
    poi_node_indices : np.ndarray
        Array of network node indices where POIs are located.
    cutoff_meters : float | np.ndarray, default 1000.0
        Cutoff distance, or a per-origin remaining budget of shape (num_sources,).

    Returns
    -------
    np.ndarray
        Integer array of shape (num_sources,) representing count of reachable POIs.
    """
    if len(poi_node_indices) == 0:
        return np.zeros(dist_matrix.shape[0], dtype=np.int64)
    return np.sum(reachable_poi_mask(dist_matrix, poi_node_indices, cutoff_meters), axis=1, dtype=np.int64)


def reachable_poi_mask(
    dist_matrix: np.ndarray,
    poi_node_indices: np.ndarray,
    budget_meters: float | np.ndarray,
) -> np.ndarray:
    """Boolean (num_sources, num_pois) mask of POIs within each origin's distance budget."""
    budget = np.asarray(budget_meters, dtype=np.float64)
    if budget.ndim == 1:
        budget = budget[:, np.newaxis]
    return dist_matrix[:, poi_node_indices] <= budget


def count_reachable_categories(
    reachable: np.ndarray,
    poi_category_codes: np.ndarray,
    n_categories: int,
) -> np.ndarray:
    """Number of distinct POI categories reachable from each origin."""
    onehot = csr_matrix(
        (np.ones(len(poi_category_codes)), (np.arange(len(poi_category_codes)), poi_category_codes)),
        shape=(len(poi_category_codes), n_categories),
    )
    per_category = csr_matrix(reachable.astype(np.float64)) @ onehot
    return np.asarray((per_category > 0).sum(axis=1)).ravel().astype(np.int64)


def remaining_budget(snap_distance_m: np.ndarray, cutoff_meters: float) -> np.ndarray:
    """Network distance budget left after walking from the centroid to its nearest node (>= 0)."""
    return np.maximum(cutoff_meters - np.asarray(snap_distance_m, dtype=np.float64), 0.0)


def calculate_pedestrian_cutoff_meters(
    walking_time_min: float = 15.0,
    walking_speed_kmh: float = 4.0,
) -> float:
    """
    Computes pedestrian network distance cutoff in meters.

    Formula:
        cutoff = (walking_speed_kmh * 1000 / 60) * walking_time_min

    Parameters
    ----------
    walking_time_min : float, default 15.0
        Walk duration threshold in minutes.
    walking_speed_kmh : float, default 4.0
        Average pedestrian travel speed in km/h. Standard baseline:
        - 4.0 km/h (~1.11 m/s) accounts for pedestrian crossing delays,
          congested urban sidewalks, and tropical climatic conditions.
        - 4.8 km/h (~1.33 m/s) represents brisk uninterrupted walking.

    Returns
    -------
    float
        Distance threshold in meters (e.g. 1000.0 m for 15 min at 4.0 km/h).
    """
    speed_meters_per_minute = (walking_speed_kmh * 1000.0) / 60.0
    return float(speed_meters_per_minute * walking_time_min)


def _point_coords(gdf: gpd.GeoDataFrame) -> np.ndarray:
    geoms = gdf.geometry
    if not (geoms.geom_type == "Point").all():
        geoms = geoms.representative_point()
    return np.column_stack([geoms.x, geoms.y])


def compute_amenity_accessibility(
    hex_gdf: gpd.GeoDataFrame,
    poi_gdf: gpd.GeoDataFrame,
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    cutoff_meters: float | None = None,
    walking_time_min: float = 15.0,
    walking_speed_kmh: float = 4.0,
    batch_size: int = 64,
    category_col: str | None = "category",
    engine: str = "vectorized",
) -> pd.DataFrame:
    """
    15-minute walkable amenity count, category diversity and snap distance per H3 cell.

    All inputs must share one metric CRS (e.g. UTM) so snap distances are in metres; use
    `project_coordinates` / `GeoDataFrame.to_crs` beforehand. Each origin's network budget is
    the cutoff minus its snap distance; origins farther than the cutoff reach nothing.

    Parameters
    ----------
    hex_gdf : gpd.GeoDataFrame
        H3 cells with 'geometry' (centroid points or polygons) and 'h3_index'.
    poi_gdf : gpd.GeoDataFrame
        POIs (points or polygons, which use a representative point).
    nodes_df : pd.DataFrame
        Network graph nodes with 'x' and 'y'.
    edges_df : pd.DataFrame
        Network graph edges with 'u', 'v', 'length_m' (node positions in `nodes_df`).
    cutoff_meters : float | None, optional
        Distance budget; derived from walking time and speed when None.
    walking_time_min, walking_speed_kmh : float
        Used when `cutoff_meters` is None.
    batch_size : int, default 64
        Origins per Dijkstra batch (memory ~ batch_size × nodes × 8 bytes).
    category_col : str | None, default 'category'
        POI category column for diversity; None skips diversity.
    engine : str, default 'vectorized'
        Routing engine: 'vectorized' (batched csgraph Dijkstra) or 'city2graph' (city2graph isochrones).

    Returns
    -------
    pd.DataFrame
        `amenities_15m`, `amenity_categories_15m` and `snap_distance_m`, indexed by 'h3_index'.
    """
    if cutoff_meters is None:
        cutoff_meters = calculate_pedestrian_cutoff_meters(walking_time_min, walking_speed_kmh)

    if engine == "city2graph":
        return compute_amenity_accessibility_city2graph(
            hex_gdf=hex_gdf,
            poi_gdf=poi_gdf,
            nodes_gdf=nodes_df if isinstance(nodes_df, gpd.GeoDataFrame) else gpd.GeoDataFrame(
                nodes_df, geometry=gpd.points_from_xy(nodes_df["x"], nodes_df["y"]), crs=hex_gdf.crs
            ),
            edges_gdf=edges_df if isinstance(edges_df, gpd.GeoDataFrame) else None,
            cutoff_meters=cutoff_meters,
            category_col=category_col,
        )

    adj_matrix = build_network_adjacency_matrix(len(nodes_df), edges_df, undirected=True)

    hex_geoms = hex_gdf.geometry
    hex_points = hex_geoms if (hex_geoms.geom_type == "Point").all() else hex_geoms.centroid
    hex_coords = np.column_stack([hex_points.x, hex_points.y])
    poi_coords = _point_coords(poi_gdf)

    hex_node_indices, snap_m = snap_coordinates_to_nodes(hex_coords, nodes_df)
    poi_node_indices, _ = snap_coordinates_to_nodes(poi_coords, nodes_df)
    budgets = remaining_budget(snap_m, cutoff_meters)

    if category_col is not None and category_col in poi_gdf.columns:
        codes, uniques = pd.factorize(poi_gdf[category_col].fillna("unknown"))
        n_categories = len(uniques)
    else:
        codes, n_categories = None, 0

    counts = np.zeros(len(hex_node_indices), dtype=np.int64)
    diversity = np.zeros(len(hex_node_indices), dtype=np.int64)
    for start in range(0, len(hex_node_indices), batch_size):
        end = min(start + batch_size, len(hex_node_indices))
        dist = compute_batched_dijkstra_distances(adj_matrix, hex_node_indices[start:end], cutoff_meters)
        reachable = reachable_poi_mask(dist, poi_node_indices, budgets[start:end])
        del dist
        reachable[budgets[start:end] <= 0] = False
        counts[start:end] = reachable.sum(axis=1)
        if codes is not None:
            diversity[start:end] = count_reachable_categories(reachable, codes, n_categories)

    return pd.DataFrame(
        {"amenities_15m": counts, "amenity_categories_15m": diversity, "snap_distance_m": snap_m},
        index=pd.Index(hex_gdf["h3_index"], name="h3_index"),
    )


def create_isochrone_city2graph(
    center_point: Any,
    nodes_gdf: gpd.GeoDataFrame,
    edges_gdf: gpd.GeoDataFrame,
    threshold: float = 1000.0,
    edge_attr: str = "length_m",
    method: str = "buffer",
    buffer_distance: float = 50.0,
) -> gpd.GeoDataFrame:
    """
    Computes a walking isochrone polygon using city2graph.utils.spatial.create_isochrone.

    Parameters
    ----------
    center_point : Any
        Origin point (shapely Point, GeoSeries, or GeoDataFrame) in a metric CRS.
    nodes_gdf : gpd.GeoDataFrame
        Street network nodes with Point geometry.
    edges_gdf : gpd.GeoDataFrame
        Street network edges with LineString geometry and traversal weight column.
    threshold : float, default 1000.0
        Walking cutoff in metres (15 minutes at 4 km/h = 1000m).
    edge_attr : str, default 'length_m'
        Traversed edge length column.
    method : str, default 'buffer'
        Polygon generation method ('buffer', 'concave_hull_alpha', 'convex_hull').
    buffer_distance : float, default 50.0
        Buffer distance in metres around reachable network edges.

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame with reachable isochrone polygon geometry.
    """
    from city2graph.utils.spatial import create_isochrone

    return create_isochrone(
        nodes=nodes_gdf,
        edges=edges_gdf,
        center_point=center_point,
        threshold=threshold,
        edge_attr=edge_attr,
        method=method,
        buffer_distance=buffer_distance,
    )


def compute_amenity_accessibility_city2graph(
    hex_gdf: gpd.GeoDataFrame,
    poi_gdf: gpd.GeoDataFrame,
    nodes_gdf: gpd.GeoDataFrame,
    edges_gdf: gpd.GeoDataFrame | None = None,
    cutoff_meters: float = 1000.0,
    category_col: str | None = "category",
    method: str = "buffer",
    buffer_distance: float = 50.0,
) -> pd.DataFrame:
    """
    Computes 15-minute walking amenity counts and category diversity using city2graph isochrones.

    Parameters
    ----------
    hex_gdf : gpd.GeoDataFrame
        H3 cells with 'geometry' and 'h3_index' in metric CRS.
    poi_gdf : gpd.GeoDataFrame
        POIs with 'geometry' and optional `category_col` in metric CRS.
    nodes_gdf : gpd.GeoDataFrame
        Network nodes GeoDataFrame.
    edges_gdf : gpd.GeoDataFrame | None, optional
        Network edges GeoDataFrame.
    cutoff_meters : float, default 1000.0
        Pedestrian cutoff distance in metres.
    category_col : str | None, default 'category'
        Category column for computing diversity.
    method : str, default 'buffer'
        Isochrone boundary method.
    buffer_distance : float, default 50.0
        Buffer distance in metres.

    Returns
    -------
    pd.DataFrame
        Table with 'amenities_15m', 'amenity_categories_15m', and 'snap_distance_m'.
    """
    from city2graph.utils.spatial import create_isochrone

    hex_geoms = hex_gdf.geometry
    hex_points = hex_geoms if (hex_geoms.geom_type == "Point").all() else hex_geoms.centroid
    hex_coords = np.column_stack([hex_points.x, hex_points.y])

    # Snap distance for reporting
    nodes_xy = pd.DataFrame({"x": nodes_gdf.geometry.x, "y": nodes_gdf.geometry.y})
    _, snap_m = snap_coordinates_to_nodes(hex_coords, nodes_xy)

    counts = np.zeros(len(hex_gdf), dtype=np.int64)
    diversity = np.zeros(len(hex_gdf), dtype=np.int64)

    poi_pts = poi_gdf.copy()
    if not (poi_pts.geometry.geom_type == "Point").all():
        poi_pts["geometry"] = poi_pts.geometry.representative_point()

    for idx, (_, row) in enumerate(hex_gdf.iterrows()):
        pt = row.geometry if row.geometry.geom_type == "Point" else row.geometry.centroid
        iso = create_isochrone(
            nodes=nodes_gdf,
            edges=edges_gdf,
            center_point=pt,
            threshold=cutoff_meters,
            edge_attr="length_m" if (edges_gdf is not None and "length_m" in edges_gdf.columns) else "length",
            method=method,
            buffer_distance=buffer_distance,
        )
        if len(iso) > 0 and not iso.geometry.iloc[0].is_empty:
            geom = iso.geometry.iloc[0]
            inside = poi_pts[poi_pts.geometry.within(geom)]
            counts[idx] = len(inside)
            if category_col is not None and category_col in inside.columns:
                diversity[idx] = inside[category_col].nunique()

    return pd.DataFrame(
        {"amenities_15m": counts, "amenity_categories_15m": diversity, "snap_distance_m": snap_m},
        index=pd.Index(hex_gdf["h3_index"], name="h3_index"),
    )


def load_osm_walk_network(
    pbf_path: str | Path,
    bbox: list[float],
    crs: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extracts the OSM walking network inside `bbox` with pyrosm and projects it to `crs`.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        nodes (x, y in `crs` metres; row position = node index) and edges (u, v, length_m).
    """
    from pyrosm import OSM

    osm = OSM(Path(pbf_path).as_posix(), bounding_box=list(bbox))
    nodes_gdf, edges_gdf = osm.get_network(network_type="walking", nodes=True)

    node_ids = nodes_gdf["id"].to_numpy()
    x, y = project_coordinates(nodes_gdf["lon"].to_numpy(), nodes_gdf["lat"].to_numpy(), crs)
    nodes = pd.DataFrame({"osm_id": node_ids, "x": x, "y": y})

    index_of = pd.Series(np.arange(len(node_ids)), index=node_ids)
    valid = edges_gdf["u"].isin(index_of.index) & edges_gdf["v"].isin(index_of.index)
    edges = pd.DataFrame({
        "u": index_of.loc[edges_gdf.loc[valid, "u"]].to_numpy(),
        "v": index_of.loc[edges_gdf.loc[valid, "v"]].to_numpy(),
        "length_m": edges_gdf.loc[valid, "length"].to_numpy(dtype=np.float64),
    })
    return nodes, edges
