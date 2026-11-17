import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Point

from phys_living_index.features.isochrones import (
    build_network_adjacency_matrix,
    calculate_pedestrian_cutoff_meters,
    compute_amenity_accessibility,
    compute_batched_dijkstra_distances,
    count_reachable_amenities,
    count_reachable_categories,
    project_coordinates,
    reachable_poi_mask,
    remaining_budget,
    snap_coordinates_to_nodes,
)


def test_calculate_pedestrian_cutoff_meters():
    # 15 minutes at 4.0 km/h: (4000 / 60) * 15 = 1000m
    cutoff_4kmh = calculate_pedestrian_cutoff_meters(walking_time_min=15.0, walking_speed_kmh=4.0)
    assert cutoff_4kmh == pytest.approx(1000.0)

    # 15 minutes at 4.8 km/h: (4800 / 60) * 15 = 1200m
    cutoff_fast = calculate_pedestrian_cutoff_meters(walking_time_min=15.0, walking_speed_kmh=4.8)
    assert cutoff_fast == pytest.approx(1200.0)

    # 10 minutes at 3.0 km/h: (3000 / 60) * 10 = 500m
    cutoff_slow = calculate_pedestrian_cutoff_meters(walking_time_min=10.0, walking_speed_kmh=3.0)
    assert cutoff_slow == pytest.approx(500.0)


def test_snap_coordinates_to_nodes():
    # 3 nodes: (0, 0), (1, 1), (5, 5)
    nodes_df = pd.DataFrame(
        {
            "node_id": [10, 20, 30],
            "x": [0.0, 1.0, 5.0],
            "y": [0.0, 1.0, 5.0],
        }
    )

    # Points to snap: (0.1, 0.1) -> node 10 (idx 0), (4.8, 5.1) -> node 30 (idx 2)
    coords = np.array([[0.1, 0.1], [4.8, 5.1]])
    node_indices, distances = snap_coordinates_to_nodes(coords, nodes_df)

    assert len(node_indices) == 2
    assert node_indices[0] == 0
    assert node_indices[1] == 2
    assert distances[0] < 0.2
    assert distances[1] < 0.3


def test_build_network_adjacency_and_dijkstra():
    # 4 nodes in a line: 0 --(300m)--> 1 --(400m)--> 2 --(500m)--> 3
    # Distances from node 0:
    # 0 -> 0m
    # 1 -> 300m
    # 2 -> 700m
    # 3 -> 1200m (exceeds 1000m cutoff)
    num_nodes = 4
    edges_df = pd.DataFrame(
        {
            "u": [0, 1, 2],
            "v": [1, 2, 3],
            "length_m": [300.0, 400.0, 500.0],
        }
    )

    adj_matrix = build_network_adjacency_matrix(num_nodes, edges_df, undirected=True)
    assert adj_matrix.shape == (4, 4)

    dist_matrix = compute_batched_dijkstra_distances(
        adj_matrix, source_indices=np.array([0]), cutoff_meters=1000.0
    )

    assert dist_matrix.shape == (1, 4)
    assert dist_matrix[0, 0] == pytest.approx(0.0)
    assert dist_matrix[0, 1] == pytest.approx(300.0)
    assert dist_matrix[0, 2] == pytest.approx(700.0)
    assert np.isinf(dist_matrix[0, 3])  # Filtered or set to inf past cutoff


def test_count_reachable_amenities():
    # Distance matrix for 2 hex origins to 4 nodes
    # hex 0 reaches nodes [0, 1] (<= 1000m)
    # hex 1 reaches nodes [2, 3] (<= 1000m)
    dist_matrix = np.array(
        [
            [100.0, 500.0, np.inf, np.inf],
            [np.inf, np.inf, 200.0, 800.0],
        ]
    )

    # 3 POIs mapped to network nodes:
    # POI A at node 1 (cat: school)
    # POI B at node 1 (cat: clinic)
    # POI C at node 2 (cat: park)
    poi_node_indices = np.array([1, 1, 2])

    counts = count_reachable_amenities(dist_matrix, poi_node_indices, cutoff_meters=1000.0)

    # hex 0 reaches node 1 (which has 2 POIs: A and B) -> count = 2
    # hex 1 reaches node 2 (which has 1 POI: C) -> count = 1
    assert len(counts) == 2
    assert counts[0] == 2
    assert counts[1] == 1


def test_remaining_budget_and_reachable_mask():
    budgets = remaining_budget(np.array([0.0, 300.0, 1200.0]), 1000.0)
    assert budgets.tolist() == [1000.0, 700.0, 0.0]

    dist = np.array([[0.0, 800.0], [0.0, 800.0], [0.0, 800.0]])
    reachable = reachable_poi_mask(dist, np.array([0, 1]), budgets)
    assert reachable.tolist() == [[True, True], [True, False], [True, False]]


def test_count_reachable_categories():
    reachable = np.array([[True, True, False], [False, False, True]])
    codes = np.array([0, 0, 1])
    assert count_reachable_categories(reachable, codes, 2).tolist() == [1, 1]


def test_project_coordinates_to_utm():
    x, y = project_coordinates(np.array([106.82, 106.83]), np.array([-6.17, -6.17]), "EPSG:32748")
    assert abs((x[1] - x[0]) - 1105.0) < 15.0  # 0.01° of longitude near 6°S


def _metric_fixture():
    # Line network in metres: nodes every 500 m along x
    nodes_df = pd.DataFrame({"x": [0.0, 500.0, 1000.0, 1500.0], "y": [0.0, 0.0, 0.0, 0.0]})
    edges_df = pd.DataFrame({"u": [0, 1, 2], "v": [1, 2, 3], "length_m": [500.0, 500.0, 500.0]})
    poi_gdf = gpd.GeoDataFrame({
        "category": ["school", "clinic", "school"],
        "geometry": [Point(10.0, 5.0), Point(990.0, 0.0), Point(1500.0, 0.0)],
    })
    return nodes_df, edges_df, poi_gdf


def test_compute_amenity_accessibility_applies_snap_budget():
    nodes_df, edges_df, poi_gdf = _metric_fixture()
    hex_gdf = gpd.GeoDataFrame({
        "h3_index": ["near", "offset", "far"],
        # 'offset' sits 200 m off node 0, so only 800 m of network budget remains
        "geometry": [Point(0.0, 0.0), Point(0.0, 200.0), Point(0.0, 1500.0)],
    })

    out = compute_amenity_accessibility(hex_gdf, poi_gdf, nodes_df, edges_df, cutoff_meters=1000.0, batch_size=2)

    assert out.loc["near", "amenities_15m"] == 2  # nodes 0 and 2 within 1000 m
    assert out.loc["near", "amenity_categories_15m"] == 2
    assert out.loc["offset", "amenities_15m"] == 1  # node 2 at 1000 m exceeds 800 m budget
    assert out.loc["offset", "snap_distance_m"] == pytest.approx(200.0)
    assert out.loc["far", "amenities_15m"] == 0  # snap distance > cutoff


def test_city2graph_isochrone_accessibility():
    from shapely.geometry import LineString

    from phys_living_index.features.isochrones import (
        compute_amenity_accessibility_city2graph,
        create_isochrone_city2graph,
    )

    nodes_gdf = gpd.GeoDataFrame({
        "id": [0, 1, 2],
        "geometry": [Point(0, 0), Point(500, 0), Point(1500, 0)],
    }, crs="EPSG:32748")

    edges_gdf = gpd.GeoDataFrame({
        "u": [0, 1],
        "v": [1, 2],
        "length_m": [500.0, 1000.0],
        "geometry": [LineString([(0, 0), (500, 0)]), LineString([(500, 0), (1500, 0)])],
    }, crs="EPSG:32748")

    center = Point(0, 0)
    iso = create_isochrone_city2graph(
        center_point=center,
        nodes_gdf=nodes_gdf,
        edges_gdf=edges_gdf,
        threshold=1000.0,
        edge_attr="length_m",
        method="buffer",
        buffer_distance=50.0,
    )
    assert len(iso) == 1
    assert iso.geometry.iloc[0].is_valid

    pois = gpd.GeoDataFrame({
        "category": ["school", "supermarket"],
        "geometry": [Point(400, 0), Point(1400, 0)],
    }, crs="EPSG:32748")

    hex_gdf = gpd.GeoDataFrame({
        "h3_index": ["cell_0"],
        "geometry": [Point(0, 0)],
    }, crs="EPSG:32748")

    res = compute_amenity_accessibility_city2graph(
        hex_gdf=hex_gdf,
        poi_gdf=pois,
        nodes_gdf=nodes_gdf,
        edges_gdf=edges_gdf,
        cutoff_meters=1000.0,
    )
    assert res.loc["cell_0", "amenities_15m"] == 1  # only school at 400m
    assert res.loc["cell_0", "amenity_categories_15m"] == 1
