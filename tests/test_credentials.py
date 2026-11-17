from pathlib import Path

import pytest

from phys_living_index.data.credentials import load_earthdata_token, load_gee_project


def test_load_earthdata_token_from_env_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("NASA_EARTHDATA_TOKEN=mock_token_abc_123\n")

    token = load_earthdata_token(env_path=env_file)
    assert token == "mock_token_abc_123"


def test_load_earthdata_token_from_environ(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("NASA_EARTHDATA_TOKEN", "mock_env_token_xyz")
    token = load_earthdata_token()
    assert token == "mock_env_token_xyz"


def test_load_gee_project_from_environ(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("EE_PROJECT", "mock-ee-project")
    assert load_gee_project() == "mock-ee-project"
