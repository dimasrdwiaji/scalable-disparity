from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from phys_living_index.features.build_features import (
    benchmark_path,
    load_benchmarks,
    parse_benchmarks,
)
from phys_living_index.features.reference_sample import (
    city_clip_shares,
    dated_extract_url,
    driest_consecutive_months,
    pool_city_cells,
    reference_bounds,
    select_reference_cities,
    size_class,
    smallest_containing_extract,
    utm_epsg,
    window_tiers,
    write_benchmark_version,
)

CONFIG_DIR = Path(__file__).resolve().parent.parent / "configs"


def test_size_class_bins():
    out = size_class(pd.Series([50_000, 500_000, 2_000_000, 30_000_000]))
    assert out.tolist() == ["small", "medium", "large", "megacity"]


def test_select_reference_cities_is_stratified_and_seeded():
    centres = pd.DataFrame({
        "name": [f"c{i}" for i in range(12)],
        "world_region": ["Asia"] * 6 + ["Africa"] * 6,
        "climate_class": ["A"] * 12,
        "size_class": ["large"] * 12,
    })
    a = select_reference_cities(centres, n_per_stratum=2, seed=7)
    b = select_reference_cities(centres, n_per_stratum=2, seed=7)

    assert len(a) == 4
    assert a.groupby("world_region").size().tolist() == [2, 2]
    pd.testing.assert_frame_equal(a, b)


def test_pool_city_cells_caps_each_city():
    big = pd.DataFrame({"is_residential": [True] * 100, "x": np.arange(100)})
    small = pd.DataFrame({"is_residential": [True, True, False], "x": [1, 2, 3]})
    pooled = pool_city_cells({"big": big, "small": small}, cells_per_city=10, seed=1)

    assert pooled.groupby("city").size().to_dict() == {"big": 10, "small": 2}


def test_reference_bounds_skips_standard_channels_and_uses_transform():
    benchmarks = load_benchmarks(benchmark_path("v0", CONFIG_DIR))
    n = 1000
    rng = np.random.default_rng(0)
    pooled = pd.DataFrame({
        "space_sufficiency_ratio": rng.uniform(0, 5, n),
        "residential_plan_area_fraction": rng.uniform(0.1, 0.7, n),
        "building_compactness": rng.uniform(0.4, 0.8, n),
        "amenities_15m": rng.integers(0, 1000, n).astype(float),
        "ndvi": rng.uniform(0, 0.7, n),
        "heat_island_intensity_k": rng.uniform(-2, 10, n),
        "terrain_safety_inv": rng.uniform(0.5, 1.0, n),
    })
    bounds = reference_bounds(pooled, benchmarks)

    assert "space_sufficiency_ratio" not in bounds and "residential_plan_area_fraction" not in bounds
    assert bounds["cumulative_amenities_15m"]["upper"] == pytest.approx(
        np.percentile(np.log1p(pooled["amenities_15m"]), 99)
    )


def test_write_benchmark_version_keeps_standard_lower(tmp_path):
    with open(benchmark_path("v0", CONFIG_DIR), encoding="utf-8") as f:
        base = yaml.safe_load(f)
    bounds = {
        "vegetation_ndvi": {"lower": -0.05, "upper": 0.75, "n": 10},
        "space_sufficiency_ratio": {"lower": 1.0, "upper": 8.0, "n": 10},
    }
    path = write_benchmark_version(base, bounds, "v1", {"seed": 1}, tmp_path / "benchmarks_v1.yaml")

    with open(path, encoding="utf-8") as f:
        written = parse_benchmarks(yaml.safe_load(f))
    by_name = {c.name: c for c in written.channels}
    assert written.version == "v1" and not written.provisional
    assert by_name["vegetation_ndvi"].lower == -0.05
    assert by_name["space_sufficiency_ratio"].lower == 0.0  # Standard lower bound kept
    assert by_name["space_sufficiency_ratio"].upper == 8.0


def test_city_clip_shares():
    benchmarks = load_benchmarks(benchmark_path("v0", CONFIG_DIR))
    pooled = pd.DataFrame({c.source: [0.0, 0.0] for c in benchmarks.channels})
    pooled["residential_plan_area_fraction"] = [0.95, 0.2]
    pooled["city"] = ["a", "a"]
    shares = city_clip_shares(pooled, benchmarks).set_index("channel")
    assert shares.loc["residential_plan_area_fraction", "share_outside"] == 0.5


def test_smallest_containing_extract_and_dated_url():
    def feat(name, bounds, url):
        x0, y0, x1, y1 = bounds
        ring = [[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]
        return {"geometry": {"type": "Polygon", "coordinates": [ring]},
                "properties": {"id": name, "urls": {"pbf": url}}}

    index = [
        feat("asia", (60, -20, 150, 60), "https://x/asia-latest.osm.pbf"),
        feat("java", (105, -9, 115, -5), "https://x/asia/indonesia/java-latest.osm.pbf"),
        feat("sumatra", (95, -6, 106, 6), "https://x/sumatra-latest.osm.pbf"),
    ]
    best = smallest_containing_extract(index, (106.35, -6.75, 107.65, -5.95))
    assert best["id"] == "java"
    assert dated_extract_url(best["urls"]["pbf"], "2024-01-01").endswith("java-240101.osm.pbf")

    with pytest.raises(LookupError):
        smallest_containing_extract(index, (0, 0, 1, 1))


def test_utm_epsg():
    assert utm_epsg(106.8, -6.2) == "EPSG:32748"
    assert utm_epsg(-0.1, 51.5) == "EPSG:32630"


def test_driest_consecutive_months_wraps_year():
    precip = [10, 12, 50, 80, 90, 100, 100, 90, 80, 50, 20, 5]
    assert driest_consecutive_months(precip, 4) == [11, 12, 1, 2]


def test_window_tiers_from_driest_months():
    tiers = window_tiers(2023, [6, 7, 8, 9])
    assert tiers[0] == [["2023-06-01", "2023-10-01"]]
    assert tiers[1] == [["2023-05-01", "2023-11-01"]]
    assert tiers[2] == [["2023-06-01", "2023-10-01"], ["2024-06-01", "2024-10-01"]]

    wrapped = window_tiers(2023, [11, 12, 1, 2])
    assert wrapped[0] == [["2023-11-01", "2024-03-01"]]
