"""
ACAG V6.GL satellite-derived surface PM2.5 (Washington University in St. Louis).

The product (V6.GL.02.04, 1998-2023, 0.01° monthly and annual, NetCDF, μg/m³) is distributed
through Box share links only (https://sites.wustl.edu/acag/datasets/surface-pm2-5/), so the
monthly files must be downloaded manually into a local directory. This module finds the
reference year's monthly files, crops them to the study area, and writes the per-pixel median
of the monthly means as a GeoTIFF (ADR 0002 §5). Cell values are then an area-weighted mean
(`zonal_local.zonal_stats_local`).
"""

import re
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import rasterio
import rasterio.transform

# e.g. V6GL02.04.CNNPM25.GL.202301-202301.nc  (start-end as YYYYMM)
_MONTH_SPAN = re.compile(r"(?P<start>\d{6})-(?P<end>\d{6})")


def find_acag_monthly_files(directory: str | Path, year: int) -> list[Path]:
    """
    Finds single-month ACAG NetCDF files for `year` (name contains `YYYYMM-YYYYMM` with
    equal start and end), sorted by month.

    Raises
    ------
    FileNotFoundError
        If no monthly file for the year is present.
    """
    directory = Path(directory)
    found: dict[str, Path] = {}
    for path in directory.glob("*.nc"):
        match = _MONTH_SPAN.search(path.name)
        if match and match["start"] == match["end"] and match["start"].startswith(str(year)):
            found[match["start"]] = path
    if not found:
        raise FileNotFoundError(
            f"No ACAG monthly NetCDF files for {year} in {directory}. Download the V6.GL.02.04 "
            "0.01° monthly files from https://sites.wustl.edu/acag/datasets/surface-pm2-5/."
        )
    return [found[k] for k in sorted(found)]


def detect_pm25_variable(dataset) -> str:
    """Returns the name of the single 2-D latitude/longitude data variable in an ACAG file."""
    candidates = [
        name for name, var in dataset.data_vars.items()
        if var.ndim == 2 and {d.lower()[:3] for d in var.dims} == {"lat", "lon"}
    ]
    if len(candidates) != 1:
        raise ValueError(f"Expected one 2-D lat/lon variable, found {candidates}")
    return candidates[0]


def _crop(dataset, bbox: Sequence[float]):
    lat_name = next(d for d in dataset.dims if d.lower().startswith("lat"))
    lon_name = next(d for d in dataset.dims if d.lower().startswith("lon"))
    min_lon, min_lat, max_lon, max_lat = bbox
    lats = dataset[lat_name].values
    lat_slice = slice(max_lat, min_lat) if lats[0] > lats[-1] else slice(min_lat, max_lat)
    return dataset.sel({lat_name: lat_slice, lon_name: slice(min_lon, max_lon)}), lat_name, lon_name


def acag_median_geotiff(
    monthly_files: Sequence[str | Path],
    bbox: Sequence[float],
    output_tif: str | Path,
) -> Path:
    """
    Writes the per-pixel median of monthly ACAG PM2.5 means (μg/m³) over `bbox` as GeoTIFF.

    Pixels with no valid month are written as NaN.
    """
    import xarray as xr

    stack = []
    lats = lons = None
    for path in monthly_files:
        with xr.open_dataset(path) as ds:
            cropped, lat_name, lon_name = _crop(ds, bbox)
            var = detect_pm25_variable(cropped)
            arr = cropped[var].transpose(lat_name, lon_name).values.astype(np.float32)
            if lats is None:
                lats, lons = cropped[lat_name].values, cropped[lon_name].values
            stack.append(arr)

    data = np.stack(stack)
    data[data < 0] = np.nan
    with np.errstate(all="ignore"):
        median = np.nanmedian(data, axis=0).astype(np.float32)
    if lats[0] < lats[-1]:  # GeoTIFF rows run north to south
        median, lats = median[::-1], lats[::-1]

    res_lon = float(abs(lons[1] - lons[0]))
    res_lat = float(abs(lats[1] - lats[0]))
    transform = rasterio.transform.from_origin(
        float(lons[0]) - res_lon / 2, float(lats[0]) + res_lat / 2, res_lon, res_lat
    )
    output_tif = Path(output_tif)
    output_tif.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        output_tif, "w", driver="GTiff", height=median.shape[0], width=median.shape[1], count=1,
        dtype="float32", crs="EPSG:4326", transform=transform, nodata=np.nan,
    ) as dst:
        dst.write(median, 1)
    return output_tif
