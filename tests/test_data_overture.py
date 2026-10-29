from pathlib import Path

import pytest

from phys_living_index.data.ingest_overture import (
    build_overture_amenities_query,
    build_overture_transportation_query,
    fetch_overture_amenities,
)


def test_build_overture_amenities_query():
    bbox = (106.8, -6.2, 106.9, -6.1)
    out_path = Path("/tmp/amenities.parquet")
    query = build_overture_amenities_query(bbox, out_path)

    assert isinstance(query, str)
    assert "theme=places/type=place" in query
    assert "theme=base/type=land_use" in query
    assert "bbox.xmin >= 106.8" in query
    assert "bbox.ymin >= -6.2" in query
    assert "bbox.xmax <= 106.9" in query
    assert "bbox.ymax <= -6.1" in query
    assert "'education.school'" in query
    assert "'healthcare.hospital'" in query
    assert "'healthcare.clinic'" in query
    assert "'commercial.supermarket_grocery'" in query
    assert "'park'" in query
    assert "amenities.parquet" in query


def test_build_overture_transportation_query():
    bbox = (106.8, -6.2, 106.9, -6.1)
    out_path = Path("/tmp/transport.parquet")
    query = build_overture_transportation_query(bbox, out_path)

    assert isinstance(query, str)
    assert "theme=transportation/type=segment" in query
    assert "bbox.xmin >= 106.8" in query
    assert "bbox.ymin >= -6.2" in query
    assert "bbox.xmax <= 106.9" in query
    assert "bbox.ymax <= -6.1" in query
    assert "subtype != 'rail'" in query
    assert "transport.parquet" in query


@pytest.mark.integration
def test_live_overture_amenities_small_sub_bbox(tmp_path):
    # Small sub-bbox near Central Jakarta (Monas area)
    bbox = (106.82, -6.18, 106.83, -6.17)
    out_file = tmp_path / "monas_amenities.parquet"
    
    result_path = fetch_overture_amenities(bbox, out_file)
    assert result_path.exists()
    
    import duckdb
    con = duckdb.connect()
    count = con.execute(f"SELECT COUNT(*) FROM read_parquet('{result_path.as_posix()}')").fetchone()[0]
    con.close()
    assert count > 0  # valid execution with nonzero rows
