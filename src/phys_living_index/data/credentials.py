"""
Shared credential loader reading API keys and tokens from .env or environment variables.
"""

import os
from pathlib import Path
from typing import Optional, Union
from dotenv import load_dotenv


def load_earthdata_token(env_path: Optional[Union[str, Path]] = None) -> Optional[str]:
    """
    Loads NASA_EARTHDATA_TOKEN from the specified .env file or system environment.
    Never logs or prints the token value.
    """
    if env_path is not None:
        load_dotenv(dotenv_path=Path(env_path))
    else:
        load_dotenv()
    return os.environ.get("NASA_EARTHDATA_TOKEN")


def load_bps_webapi_key(env_path: Optional[Union[str, Path]] = None) -> Optional[str]:
    """
    Loads BPS_WEBAPI_KEY from the specified .env file or system environment.
    """
    if env_path is not None:
        load_dotenv(dotenv_path=Path(env_path))
    else:
        load_dotenv()
    return os.environ.get("BPS_WEBAPI_KEY")
