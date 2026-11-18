"""
Area-weighted zonal statistics of a local GeoTIFF over H3 cells (exactextract).

Used for rasters that are not on Earth Engine (e.g. ACAG PM2.5). Each pixel is weighted by
its exact fractional overlap with the cell polygon, matching the GEE `reduceRegions` path.
"""

from collections.abc import Sequence
from pathlib import Path

import geopandas as gpd
import h3
import pandas as pd
from shapely.geometry import Polygon


def h3_cells_geodataframe(cells: Sequence[str]) -> gpd.GeoDataFrame:
    """H3 cell polygons as a WGS84 GeoDataFrame with an `h3_index` column."""
    polygons = [Polygon([(lng, lat) for lat, lng in h3.cell_to_boundary(c)]) for c in cells]
    return gpd.GeoDataFrame({"h3_index": list(cells)}, geometry=polygons, crs="EPSG:4326")


def zonal_stats_local(
    raster_path: str | Path,
    cells: Sequence[str],
    stats: Sequence[str] = ("mean", "count"),
    prefix: str = "",
) -> pd.DataFrame:
    """
    Area-weighted zonal statistics of a single-band GeoTIFF over H3 cells.

    Parameters
    ----------
    raster_path : str | Path
        Single-band GeoTIFF in any CRS (cells are reprojected to match).
    cells : Sequence[str]
        H3 cell indices.
    stats : Sequence[str], default ('mean', 'count')
        exactextract operations; 'count' is the coverage-weighted valid-pixel count.
    prefix : str, optional
        Column prefix, producing `<prefix>_<stat>`.

    Returns
    -------
    pd.DataFrame
        One column per statistic, indexed by `h3_index` in the order of `cells`.
    """
    from exactextract import exact_extract

    gdf = h3_cells_geodataframe(cells)
    result = exact_extract(
        str(raster_path),
        gdf,
        list(stats),
        include_cols=["h3_index"],
        output="pandas",
    )
    result = result.set_index("h3_index")
    if prefix:
        result = result.rename(columns={s: f"{prefix}_{s}" for s in stats})
    return result.reindex(list(cells))
