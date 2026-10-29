from pathlib import Path

import pytest

from phys_living_index.data.credentials import load_earthdata_token
from phys_living_index.data.ingest_context import (
    build_viirs_request_params,
    fetch_viirs_black_marble,
)


def test_load_earthdata_token_from_env_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("NASA_EARTHDATA_TOKEN=mock_token_abc_123\n")

    token = load_earthdata_token(env_path=env_file)
    assert token == "mock_token_abc_123"


def test_load_earthdata_token_from_environ(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("NASA_EARTHDATA_TOKEN", "mock_env_token_xyz")
    token = load_earthdata_token()
    assert token == "mock_env_token_xyz"


def test_build_viirs_request_params():
    bbox = (106.8, -6.3, 107.0, -6.1)
    date_range = ("2023-01-01T00:00:00Z", "2023-01-31T23:59:59Z")

    params = build_viirs_request_params(bbox, date_range)

    assert params["short_name"] == "VNP46A2"
    assert params["bounding_box"] == "106.8,-6.3,107.0,-6.1"
    assert params["temporal"] == "2023-01-01T00:00:00Z,2023-01-31T23:59:59Z"


def test_viirs_raises_when_no_token(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setattr("phys_living_index.data.ingest_context.load_earthdata_token", lambda: None)
    out_file = tmp_path / "viirs.tif"

    with pytest.raises(ValueError, match="NASA_EARTHDATA_TOKEN is required"):
        fetch_viirs_black_marble(
            bbox=(106.8, -6.3, 107.0, -6.1),
            output_tif=out_file,
            token=None,
        )


@pytest.mark.integration
def test_live_viirs_download_with_token(tmp_path: Path):
    token = load_earthdata_token()
    if not token:
        pytest.skip("NASA_EARTHDATA_TOKEN not set in environment or .env")

    bbox = (106.82, -6.18, 106.83, -6.17)
    out_file = tmp_path / "live_viirs.tif"

    res = fetch_viirs_black_marble(bbox=bbox, output_tif=out_file, token=token)
    assert res.exists()
