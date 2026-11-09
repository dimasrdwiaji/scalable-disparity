"""
Scales physical living standard indicators on H3 Resolution 8 cells into the feature matrix X.

Implements ADR 0003:
1. Universal frozen benchmarks: every channel is mapped to [0, 1] between bounds read from a
   versioned benchmark file (configs/benchmarks/benchmarks_<version>.yaml). Bounds are never
   computed from the study area, so a scaled value means the same thing in every region.
2. Transforms before scaling: `log1p` for heavy-tailed counts (amenities, radiance).
3. Orientation: `positive` channels keep their direction, `inverted` hazard channels
   (bare soil, excess heat, PM2.5, NO2) become 1 - x so higher is better, and `context`
   channels (built-up, vegetation, water) carry no better/worse direction.
4. Clipping at the frozen bounds replaces P99 winsorization; the share of residential cells
   clipped at each bound is reported, and a region above `clip_flag_share` is flagged as
   outside the reference distribution, never re-tuned.

Raw inputs keep authentic physical units (CLAUDE.md); scaling happens only here.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

TRANSFORMS = ("none", "log1p")
ORIENTATIONS = ("positive", "inverted", "context")
FRICTION_GROUPS = ("socio", "bio")

# The lean, orthogonal 7-channel physical disparity feature dimensions (Revision 5)
FEATURE_DIMENSIONS_7D: list[str] = [
    "space_sufficiency_ratio",        # 1. Living Space Sufficiency Ratio (3D JRC GHS-BUILT-V) [socio]
    "residential_plan_area_fraction", # 2. Residential Plan Area Fraction (Ground Crowding on GHS Mask) [socio]
    "building_compactness",           # 3. Building Footprint Compactness (Morphological Regularity) [socio]
    "cumulative_amenities_15m",       # 4. 15-Minute Walking Accessibility (Overture/OSM) [socio]
    "vegetation_ndvi",                # 5. Vegetation Luxury Effect (Sentinel-2 NDVI) [bio]
    "heat_island_intensity_inv",      # 6. Inverted Surface Urban Heat Island (Landsat ΔLST) [bio]
    "terrain_safety_inv",             # 7. Topographic Slope Safety (Copernicus DEM 30m) [bio]
]
FEATURE_DIMENSIONS = FEATURE_DIMENSIONS_7D

# The legacy 10 canonical feature channels for backwards compatibility
FEATURE_DIMENSIONS_10D: list[str] = [
    "space_sufficiency_ratio",    # 1. Living Space Ratio
    "builtup_ndbi",               # 2. Built-up Density (NDBI)
    "cumulative_amenities_15m",   # 3. 15-Minute Walking Opportunities
    "bare_soil_bsi",              # 4. Bare Soil / Dirt Roads (BSI)
    "nighttime_energy_radiance",  # 5. Night-time Radiance
    "vegetation_ndvi",            # 6. Vegetation (NDVI)
    "heat_island_intensity_inv",  # 7. Inverted Heat Island Intensity (ΔLST)
    "water_frequency",            # 8. Surface Water Frequency
    "air_purity_pm25_inv",        # 9. Inverted Fine Particulates (PM2.5)
    "no2_inv",                    # 10. Inverted Tropospheric NO2
]


@dataclass(frozen=True)
class ChannelBenchmark:
    """Universal scaling rule for one feature channel."""

    name: str
    source: str
    transform: str
    lower: float
    upper: float
    orientation: str
    friction_group: str
    bound_source: str

    def __post_init__(self) -> None:
        if self.transform not in TRANSFORMS:
            raise ValueError(f"{self.name}: unknown transform {self.transform!r}")
        if self.orientation not in ORIENTATIONS:
            raise ValueError(f"{self.name}: unknown orientation {self.orientation!r}")
        if self.friction_group not in FRICTION_GROUPS:
            raise ValueError(f"{self.name}: unknown friction group {self.friction_group!r}")
        if not self.upper > self.lower:
            raise ValueError(f"{self.name}: upper bound must exceed lower bound")


@dataclass(frozen=True)
class BenchmarkSet:
    """A versioned set of universal benchmarks (ADR 0003)."""

    version: str
    provisional: bool
    channels: tuple[ChannelBenchmark, ...]
    min_density_per_km2: float
    min_building_count: int
    sensitivity_densities_per_km2: tuple[float, ...]
    un_habitat_min_m2: float
    clip_flag_share: float

    @property
    def names(self) -> list[str]:
        return [c.name for c in self.channels]

    def group_indices(self, group: str) -> list[int]:
        """Column indices of channels in a Stage 4 friction group ('socio' or 'bio')."""
        return [i for i, c in enumerate(self.channels) if c.friction_group == group]


def benchmark_path(version: str, config_dir: str | Path) -> Path:
    """Path of the benchmark file for a version, e.g. configs/benchmarks/benchmarks_v0.yaml."""
    return Path(config_dir) / "benchmarks" / f"benchmarks_{version}.yaml"


def parse_benchmarks(raw: dict[str, Any]) -> BenchmarkSet:
    """Validates a parsed benchmark YAML document into a BenchmarkSet."""
    channels = tuple(ChannelBenchmark(**c) for c in raw["channels"])
    names = [c.name for c in channels]
    if len(set(names)) != len(names):
        raise ValueError("Duplicate channel names in benchmark file")
    residential = raw["residential"]
    return BenchmarkSet(
        version=str(raw["version"]),
        provisional=bool(raw.get("provisional", False)),
        channels=channels,
        min_density_per_km2=float(residential["min_density_per_km2"]),
        min_building_count=int(residential["min_building_count"]),
        sensitivity_densities_per_km2=tuple(float(d) for d in residential["sensitivity_densities_per_km2"]),
        un_habitat_min_m2=float(raw["living_space"]["un_habitat_min_m2"]),
        clip_flag_share=float(raw["clip_flag_share"]),
    )


def load_benchmarks(path: str | Path) -> BenchmarkSet:
    """Loads and validates a universal benchmark file."""
    with open(path, encoding="utf-8") as f:
        return parse_benchmarks(yaml.safe_load(f))


def apply_transform(values: np.ndarray, transform: str) -> np.ndarray:
    """Applies a channel transform; NaN stays NaN."""
    values = np.asarray(values, dtype=np.float64)
    if transform == "none":
        return values
    if transform == "log1p":
        return np.log1p(np.clip(values, 0.0, None))
    raise ValueError(f"Unknown transform {transform!r}")


def scale_channel(values: np.ndarray, bench: ChannelBenchmark) -> np.ndarray:
    """
    Transforms, clips to the frozen bounds, scales to [0, 1] and orients one channel.
    NaN (no valid observation) is preserved.
    """
    x = apply_transform(values, bench.transform)
    scaled = (np.clip(x, bench.lower, bench.upper) - bench.lower) / (bench.upper - bench.lower)
    if bench.orientation == "inverted":
        scaled = 1.0 - scaled
    return scaled


def build_feature_matrix(raw_df: pd.DataFrame, benchmarks: BenchmarkSet) -> pd.DataFrame:
    """
    Scales every channel of the raw feature table with the universal benchmarks.

    Parameters
    ----------
    raw_df : pd.DataFrame
        Raw physical values indexed by H3 cell; must contain each channel's `source` column.
    benchmarks : BenchmarkSet
        Universal benchmark version.

    Returns
    -------
    pd.DataFrame
        Scaled channels in benchmark order, values in [0, 1] or NaN.
    """
    missing = [c.source for c in benchmarks.channels if c.source not in raw_df.columns]
    if missing:
        raise KeyError(f"Raw feature table lacks source columns: {missing}")
    scaled = {c.name: scale_channel(raw_df[c.source].to_numpy(), c) for c in benchmarks.channels}
    return pd.DataFrame(scaled, index=raw_df.index)


def clipped_shares(
    raw_df: pd.DataFrame,
    benchmarks: BenchmarkSet,
    mask: pd.Series | np.ndarray,
) -> pd.DataFrame:
    """
    Share of masked (residential) cells clipped at each frozen bound, per channel.

    A channel whose share at either bound exceeds `clip_flag_share` is flagged: the region
    lies outside the reference distribution for that channel.
    """
    mask = np.asarray(mask, dtype=bool)
    rows = []
    for c in benchmarks.channels:
        x = apply_transform(raw_df[c.source].to_numpy(), c.transform)[mask]
        x = x[~np.isnan(x)]
        n = max(x.size, 1)
        below = float(np.sum(x < c.lower)) / n
        above = float(np.sum(x > c.upper)) / n
        rows.append({
            "channel": c.name,
            "n_valid": int(x.size),
            "share_below_lower": below,
            "share_above_upper": above,
            "outside_reference": max(below, above) > benchmarks.clip_flag_share,
        })
    return pd.DataFrame(rows).set_index("channel")


def complete_feature_mask(scaled_df: pd.DataFrame) -> pd.Series:
    """Cells with a valid value in every channel."""
    return scaled_df.notna().all(axis=1)


def fill_for_message_passing(
    scaled_df: pd.DataFrame,
    reference_mask: pd.Series | np.ndarray,
) -> np.ndarray:
    """
    Fills NaN with the per-channel median over reference (residential, complete) cells.

    Filled cells are excluded from the loss and metrics by the training mask; the fill only
    keeps message passing defined across the full H3 graph.
    """
    reference_mask = np.asarray(reference_mask, dtype=bool)
    medians = scaled_df[reference_mask].median()
    filled = scaled_df.fillna(medians).fillna(0.0)
    return filled.to_numpy(dtype=np.float32)


def combine_floor_area(
    explicit_floor_area_m2: pd.Series,
    unknown_height_footprint_m2: pd.Series,
    mean_floors: pd.Series,
    residential_ratio: pd.Series | None = None,
) -> pd.Series:
    """
    Total floor area per cell: footprints with a known height use their own floor count;
    footprints without one take the cell's presence-weighted mean floors from Open Buildings
    2.5D Temporal (1 floor where that layer has no buildings).

    If residential_ratio is provided (e.g. from GHS-BUILT-S non-residential surface masking),
    gross floor area is multiplied by the residential fraction in [0, 1] to remove commercial,
    industrial, and institutional built stock.
    """
    floors = mean_floors.reindex(explicit_floor_area_m2.index).fillna(1.0).clip(lower=1.0)
    unknown = unknown_height_footprint_m2.reindex(explicit_floor_area_m2.index).fillna(0.0)
    gross = explicit_floor_area_m2.fillna(0.0) + unknown * floors
    if residential_ratio is not None:
        ratio = residential_ratio.reindex(explicit_floor_area_m2.index).fillna(1.0).clip(lower=0.0, upper=1.0)
        return gross * ratio
    return gross


def compute_ghs_residential_floor_area(
    built_volume_total_m3: pd.Series,
    built_volume_nres_m3: pd.Series,
    floor_height_m: float = 3.0,
) -> pd.Series:
    """
    Computes residential floor area (m²) from GHS-BUILT-V 3D volume grids:
    floor_area_res = max(0, built_volume_total - built_volume_nres) / floor_height_m.
    Standard storey height is 3.0 m (Biljecki & Chow, 2022; European Commission JRC).
    """
    total = built_volume_total_m3.fillna(0.0)
    nres = built_volume_nres_m3.fillna(0.0)
    vol_res = (total - nres).clip(lower=0.0)
    return vol_res / floor_height_m


def compute_terrain_safety(hazard_slope_share: pd.Series) -> pd.Series:
    """
    Computes terrain safety indicator:
    Inverted share of cell area with slope exceeding hazardous threshold (> 15°):
    terrain_safety = (1.0 - hazard_slope_share).clip(lower=0.0, upper=1.0)
    Higher values indicate safer, non-hazardous, buildable flat terrain.
    """
    return (1.0 - hazard_slope_share.fillna(0.0)).clip(lower=0.0, upper=1.0)


def compute_living_space_ratio(
    floor_area_m2: pd.Series,
    population: pd.Series,
    un_habitat_min_m2: float = 9.0,
) -> pd.Series:
    """
    Living Space Ratio R_space = (residential floor area / population) / 9.0 m².

    Cells without population are NaN (undefined), not 0, so missing buildings or people
    can never be read as severe overcrowding. Capping happens at scaling via the frozen
    upper bound.
    """
    pop = population.reindex(floor_area_m2.index)
    per_capita = floor_area_m2 / pop.where(pop > 0)
    return per_capita / un_habitat_min_m2


def heat_island_background_mask(
    is_residential: pd.Series,
    smod_code: pd.Series,
    veg_probability: pd.Series,
    background_smod_codes: list[int],
    min_veg_probability: float,
) -> pd.Series:
    """Non-residential rural cells dominated by tree/grass/crop cover: the regional LST background."""
    return (
        ~is_residential.astype(bool)
        & smod_code.isin(background_smod_codes)
        & (veg_probability >= min_veg_probability)
    )


def compute_heat_island_intensity(
    lst_k: pd.Series,
    background_mask: pd.Series,
    min_background_cells: int = 50,
) -> tuple[pd.Series, float]:
    """
    Heat island intensity ΔLST = cell LST - median LST of the regional background (K).

    Raises
    ------
    ValueError
        If fewer than `min_background_cells` background cells have a valid LST; widen the
        region's background definition in its measurement settings.
    """
    background = lst_k[background_mask.astype(bool)].dropna()
    if len(background) < min_background_cells:
        raise ValueError(
            f"Only {len(background)} heat-island background cells (< {min_background_cells}); "
            "widen the region's heat_island background settings."
        )
    background_lst = float(background.median())
    return lst_k - background_lst, background_lst


def assemble_h3_features(
    h3_hexes: list[str],
    data_sources: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Assembles indicator columns into a unified H3 Resolution 8 table.

    Parameters
    ----------
    h3_hexes : list[str]
        List of target H3 cell indices.
    data_sources : dict[str, Any] | None, optional
        Column name to pd.Series (aligned by H3 index), array/list (positional), or scalar.

    Returns
    -------
    pd.DataFrame
        H3 feature table indexed by H3 cell ID.
    """
    df = pd.DataFrame(index=h3_hexes)
    df.index.name = "h3_index"
    if data_sources is not None:
        for col, vals in data_sources.items():
            if isinstance(vals, pd.Series):
                df[col] = vals.reindex(h3_hexes).to_numpy()
            elif isinstance(vals, (np.ndarray, list)):
                if len(vals) != len(h3_hexes):
                    raise ValueError(f"{col}: expected {len(h3_hexes)} values, got {len(vals)}")
                df[col] = vals
            else:
                df[col] = vals
    return df
