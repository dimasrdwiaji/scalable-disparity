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


def test_compute_amenity_accessibility_integration_mock():
    # Synthetic GeoDataFrames
    # Hex centroids: 2 hexes
    hex_gdf = gpd.GeoDataFrame(
        {
            "h3_index": ["8828308281fffff", "8828308283fffff"],
            "geometry": [Point(106.82, -6.17), Point(106.83, -6.17)],
        },
        crs="EPSG:4326",
    )

    # POIs: 2 points
    poi_gdf = gpd.GeoDataFrame(
        {
            "id": ["p1", "p2"],
            "category": ["education.school", "healthcare.clinic"],
            "geometry": [Point(106.821, -6.171), Point(106.829, -6.171)],
        },
        crs="EPSG:4326",
    )

    # Network nodes and edges
    nodes_df = pd.DataFrame(
        {
            "node_id": [1, 2, 3],
            "x": [106.82, 106.825, 106.83],
            "y": [-6.17, -6.17, -6.17],
        }
    )
    edges_df = pd.DataFrame(
        {
            "u": [0, 1],
            "v": [1, 2],
            "length_m": [500.0, 500.0],
        }
    )

    accessibility = compute_amenity_accessibility(
        hex_gdf=hex_gdf,
        poi_gdf=poi_gdf,
        nodes_df=nodes_df,
        edges_df=edges_df,
        cutoff_meters=1000.0,
    )

    assert isinstance(accessibility, pd.Series)
    assert len(accessibility) == 2
    assert "8828308281fffff" in accessibility.index
    assert np.all(accessibility.values >= 0)
