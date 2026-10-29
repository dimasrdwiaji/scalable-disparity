"""
Shared credential loader reading API keys and access tokens from .env or system environment.

This module provides a secure, centralized entry point for loading external authentication
tokens (e.g., NASA Earthdata Login). It strictly avoids logging, printing, or leaking
secrets, ensuring tokens remain isolated in memory.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


def _init_env(env_path: Path | str | None = None) -> None:
    """
    Initializes environment variables from a .env file if specified or available.

    Parameters
    ----------
    env_path : Path | str | None, optional
        Explicit path to the target .env file. If None, dotenv automatically searches
        for a .env file in the current working directory and parent trees.
    """
    if env_path is not None:
        load_dotenv(dotenv_path=Path(env_path))
    else:
        load_dotenv()


def load_earthdata_token(env_path: Path | str | None = None) -> str | None:
    """
    Retrieves the NASA Earthdata bearer token from .env or the system environment.

    Used by VIIRS Black Marble (VNP46A2) nighttime lights ingestion to query
    NASA Common Metadata Repository (CMR) and download HDF5 granules.

    Parameters
    ----------
    env_path : Path | str | None, optional
        Optional explicit path to the .env file.

    Returns
    -------
    str | None
        The NASA_EARTHDATA_TOKEN string if configured, or None if missing.
    """
    _init_env(env_path)
    return os.environ.get("NASA_EARTHDATA_TOKEN")
