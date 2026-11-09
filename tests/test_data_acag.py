import h3
import numpy as np
import pytest
import rasterio
import xarray as xr

from phys_living_index.data.ingest_acag import (
    acag_median_geotiff,
    detect_pm25_variable,
    find_acag_monthly_files,
)
from phys_living_index.data.zonal_local import zonal_stats_local


def _write_month(directory, yyyymm, value, ascending_lat=True):
    lats = np.arange(-6.995, -5.0, 0.01)
    if not ascending_lat:
        lats = lats[::-1]
    lons = np.arange(106.005, 108.0, 0.01)
    data = np.full((lats.size, lons.size), value, dtype=np.float32)
    ds = xr.Dataset({"GWRPM25": (("lat", "lon"), data)}, coords={"lat": lats, "lon": lons})
    path = directory / f"V6GL02.04.CNNPM25.GL.{yyyymm}-{yyyymm}.nc"
    ds.to_netcdf(path)
    return path


def test_find_acag_monthly_files_filters_year_and_annual(tmp_path):
    for m, v in [("202302", 30.0), ("202301", 10.0), ("202201", 99.0)]:
        _write_month(tmp_path, m, v)
    (tmp_path / "V6GL02.04.CNNPM25.GL.202301-202312.nc").write_text("annual")

    files = find_acag_monthly_files(tmp_path, 2023)
    assert [f.name[-16:-10] for f in files] == ["202301", "202302"]

    with pytest.raises(FileNotFoundError):
        find_acag_monthly_files(tmp_path, 2021)


def test_detect_pm25_variable():
    ds = xr.Dataset(
        {"PM25": (("lat", "lon"), np.zeros((2, 2))), "area": (("x",), np.zeros(3))},
        coords={"lat": [0.0, 1.0], "lon": [0.0, 1.0]},
    )
    assert detect_pm25_variable(ds) == "PM25"


@pytest.mark.parametrize("ascending_lat", [True, False])
def test_acag_median_geotiff_and_zonal_mean(tmp_path, ascending_lat):
    files = [
        _write_month(tmp_path, f"2023{m:02d}", v, ascending_lat)
        for m, v in [(1, 10.0), (2, 40.0), (3, 20.0)]
    ]
    out = acag_median_geotiff(files, (106.6, -6.4, 107.0, -6.0), tmp_path / "pm25.tif")

    with rasterio.open(out) as src:
        arr = src.read(1)
        assert np.allclose(arr, 20.0)
        left, bottom, right, top = src.bounds
        assert left == pytest.approx(106.6, abs=0.011) and top == pytest.approx(-6.0, abs=0.011)
        assert src.transform.e < 0  # north-up

    cells = [h3.latlng_to_cell(-6.2, 106.8, 8)]
    stats = zonal_stats_local(out, cells, prefix="pm25")
    assert stats.loc[cells[0], "pm25_mean"] == pytest.approx(20.0)
