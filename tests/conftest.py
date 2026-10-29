import os
from contextlib import suppress

# Fix PROJ_LIB / PROJ_DATA when external programs (e.g. PostgreSQL) override environment variables
with suppress(Exception):
    import pyproj.datadir

    proj_dir = pyproj.datadir.get_data_dir()
    os.environ["PROJ_LIB"] = proj_dir
    os.environ["PROJ_DATA"] = proj_dir
