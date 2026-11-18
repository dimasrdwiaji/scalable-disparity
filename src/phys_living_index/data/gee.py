"""
Thin Google Earth Engine seam: area-weighted zonal statistics of any ee.Image over H3 cells.

Every raster channel is aggregated onto H3 Res-8 polygons with `reduceRegions`, which weights
each pixel by its fractional overlap with the cell (ADR 0002 §3). Centroid point sampling is
not used. Cells are sent in batches as client-side features, so no table asset upload is needed;
a batch that fails (e.g. a computation timeout) is split in half and retried.

Pure helpers (feature building, result parsing, valid-area fraction, provenance) carry no
Earth Engine dependency and are unit-tested offline.
"""

import json
import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import h3
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .credentials import load_gee_project

logger = logging.getLogger(__name__)

PROVENANCE_METADATA_KEY = b"phys_living_index.provenance"
SUPPORTED_REDUCERS = ("mean", "sum", "median", "mode")


def h3_cell_features(cells: Sequence[str]) -> list[dict[str, Any]]:
    """
    Builds GeoJSON polygon features for H3 cells, each carrying its `h3_index` property.

    Parameters
    ----------
    cells : Sequence[str]
        H3 cell indices.

    Returns
    -------
    list[dict[str, Any]]
        GeoJSON Feature dictionaries in (lon, lat) order with closed rings.
    """
    features = []
    for cell in cells:
        ring = [[lng, lat] for lat, lng in h3.cell_to_boundary(cell)]
        ring.append(ring[0])
        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [ring]},
            "properties": {"h3_index": cell},
        })
    return features


def batch_cells(cells: Sequence[str], batch_size: int) -> list[list[str]]:
    """Splits cells into consecutive batches of at most `batch_size`."""
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")
    return [list(cells[i : i + batch_size]) for i in range(0, len(cells), batch_size)]


def parse_reduce_regions(
    features: list[dict[str, Any]],
    bands: Sequence[str],
    stats: Sequence[str],
) -> pd.DataFrame:
    """
    Parses `reduceRegions` output features into a table indexed by `h3_index`.

    Earth Engine names combined-reducer outputs `<band>_<stat>` for multi-band images but
    just `<stat>` for single-band images; both forms are accepted. Columns are always
    named `<band>_<stat>`. Missing values (fully masked cells) become NaN.

    Parameters
    ----------
    features : list[dict[str, Any]]
        Features as returned by `FeatureCollection.getInfo()["features"]`.
    bands : Sequence[str]
        Image band names that were reduced.
    stats : Sequence[str]
        Reducer output names (e.g. 'mean', 'count').

    Returns
    -------
    pd.DataFrame
        One row per cell, one column per band and statistic.
    """
    rows = []
    for feat in features:
        props = feat.get("properties", {})
        row: dict[str, Any] = {"h3_index": props["h3_index"]}
        for band in bands:
            for stat in stats:
                key = f"{band}_{stat}"
                if key in props:
                    value = props[key]
                elif len(bands) == 1 and stat in props:
                    value = props[stat]
                elif len(stats) == 1 and band in props:
                    value = props[band]
                else:
                    value = None
                row[key] = np.nan if value is None else float(value)
        rows.append(row)
    columns = ["h3_index"] + [f"{b}_{s}" for b in bands for s in stats]
    return pd.DataFrame(rows, columns=columns).set_index("h3_index")


def compute_valid_fraction(
    pixel_count: pd.Series,
    scale_m: float,
) -> pd.Series:
    """
    Approximates the share of each cell's area covered by valid (unmasked) pixels.

    Parameters
    ----------
    pixel_count : pd.Series
        Count of valid pixels per cell, indexed by H3 cell id.
    scale_m : float
        Pixel size in metres at which the reduction ran.

    Returns
    -------
    pd.Series
        Valid-area fraction in [0, 1].
    """
    cell_area = np.array([h3.cell_area(c, unit="m^2") for c in pixel_count.index])
    frac = pixel_count.fillna(0.0).to_numpy() * scale_m**2 / cell_area
    return pd.Series(np.clip(frac, 0.0, 1.0), index=pixel_count.index)


def write_table_with_provenance(
    df: pd.DataFrame,
    output_path: str | Path,
    provenance: dict[str, Any],
) -> Path:
    """
    Writes a parquet table with a JSON provenance record stored in the schema metadata.

    Parameters
    ----------
    df : pd.DataFrame
        Table to write.
    output_path : str | Path
        Destination parquet file.
    provenance : dict[str, Any]
        Asset IDs, date ranges, scale, CRS, scene counts, window tiers, etc.

    Returns
    -------
    Path
        The written file path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pandas(df)
    metadata = dict(table.schema.metadata or {})
    metadata[PROVENANCE_METADATA_KEY] = json.dumps(provenance, default=str).encode()
    pq.write_table(table.replace_schema_metadata(metadata), output_path)
    return output_path


def read_provenance(path: str | Path) -> dict[str, Any]:
    """Reads the provenance record written by `write_table_with_provenance`."""
    metadata = pq.read_schema(path).metadata or {}
    raw = metadata.get(PROVENANCE_METADATA_KEY)
    return json.loads(raw) if raw else {}


def initialize_ee(project: str | None = None) -> None:
    """
    Initializes Earth Engine, raising a clear error when credentials are missing or expired.

    Parameters
    ----------
    project : str | None, optional
        Cloud project ID. Defaults to EE_PROJECT, then to the credentials' stored project.
    """
    import ee

    project = project or load_gee_project()
    try:
        ee.Initialize(project=project)
    except Exception as exc:  # noqa: BLE001 - re-raised with an actionable message
        raise RuntimeError(
            "Earth Engine initialization failed. Re-run `uv run earthengine authenticate` "
            "and make sure EE_PROJECT (or the credentials' project) is registered for Earth Engine."
        ) from exc


def _build_reducer(reducer: str, extra_stats: Sequence[str]) -> Any:
    import ee

    factories = {
        "mean": ee.Reducer.mean,
        "sum": ee.Reducer.sum,
        "median": ee.Reducer.median,
        "mode": ee.Reducer.mode,
        "count": ee.Reducer.count,
    }
    if reducer not in SUPPORTED_REDUCERS:
        raise ValueError(f"Unsupported reducer {reducer!r}; choose from {SUPPORTED_REDUCERS}")
    combined = factories[reducer]()
    for stat in extra_stats:
        combined = combined.combine(factories[stat](), sharedInputs=True)
    return combined


def _reduce_batch(
    image: Any,
    cells: list[str],
    reducer: Any,
    scale: float,
    crs: Any,
    tile_scale: int,
) -> list[dict[str, Any]]:
    import ee

    fc = ee.FeatureCollection(h3_cell_features(cells))
    kwargs: dict[str, Any] = {"collection": fc, "reducer": reducer, "scale": scale, "tileScale": tile_scale}
    if crs is not None:
        kwargs["crs"] = crs
    return image.reduceRegions(**kwargs).getInfo()["features"]


def reduce_image_over_cells(
    image: Any,
    cells: Sequence[str],
    bands: Sequence[str],
    scale: float,
    reducer: str = "mean",
    extra_stats: Sequence[str] = ("count",),
    crs: Any = "EPSG:32748",
    batch_size: int = 250,
    tile_scale: int = 4,
    min_batch_size: int = 8,
) -> pd.DataFrame:
    """
    Area-weighted zonal statistics of an ee.Image over H3 cells.

    Use `reducer='mean'` for intensive quantities (indices, LST, radiance, concentrations)
    and `reducer='sum'` for extensive quantities (population).

    Parameters
    ----------
    image : ee.Image
        Image whose bands are named `bands`.
    cells : Sequence[str]
        H3 cell indices.
    bands : Sequence[str]
        Band names to report.
    scale : float
        Reduction scale in metres (the layer's native scale).
    reducer : str, default 'mean'
        Primary statistic.
    extra_stats : Sequence[str], default ('count',)
        Additional statistics sharing the inputs (e.g. 'count' for valid-pixel counts).
    crs : str | ee.Projection | None, default 'EPSG:32748'
        Reduction CRS. Pass the image's own projection for extensive counts.
    batch_size : int, default 250
        Cells per request.
    tile_scale : int, default 4
        Earth Engine tileScale (higher uses less memory per tile).
    min_batch_size : int, default 8
        Smallest batch to retry before giving up.

    Returns
    -------
    pd.DataFrame
        Columns `<band>_<stat>` indexed by `h3_index`, in the order of `cells`.
    """
    import ee

    stats = [reducer, *extra_stats]
    ee_reducer = _build_reducer(reducer, extra_stats)
    image = image.select(list(bands))

    pending = batch_cells(cells, batch_size)
    frames = []
    while pending:
        batch = pending.pop(0)
        try:
            features = _reduce_batch(image, batch, ee_reducer, scale, crs, tile_scale)
        except ee.EEException as exc:
            if len(batch) <= min_batch_size:
                raise RuntimeError(f"reduceRegions failed for {len(batch)} cells: {exc}") from exc
            half = len(batch) // 2
            logger.warning("Batch of %d cells failed (%s); splitting.", len(batch), exc)
            pending[:0] = [batch[:half], batch[half:]]
            continue
        frames.append(parse_reduce_regions(features, bands, stats))
        logger.info("Reduced %d / %d cells.", sum(len(f) for f in frames), len(cells))

    return pd.concat(frames).reindex(list(cells))
