# ADR 0002: 2023 Reference Epoch, Representative Composites, and Area-Weighted Zonal Aggregation onto H3 Res-8

* **Status**: Accepted
* **Date**: 2026-11-02
* **Deciders**: Dimas RD
* **Partly supersedes**: ADR 0001 Amendment 1 (MNDWI as flood channel, AQI channel) and Amendment 2 item 1 (populated = `WorldPop > 0`)

---

## Context

The Stage 3 review (2026-11-02) found that the feature matrix was built from inputs that cannot support H3 Res-8 (~0.737 km²) analysis:

1. **Misregistered rasters.** Sentinel-2 indices and Landsat LST were taken from the *first* STAC search hit (one scene), decimated to 200 × 200 pixels, and georeferenced to the study bounding box with `from_bounds(bbox)`. One scene does not cover the bounding box, so every pixel sits at the wrong location.
2. **Point sampling instead of cell aggregation.** Every raster was read at the single pixel under the H3 centroid.
3. **Unrepresentative time.** VIIRS was one night (2023-12-31, New Year's Eve); Open-Meteo air quality was one `current` reading from 20 anchors with 8 distinct values (~40 km CAMS grid); the European AQI equals its ozone sub-index.
4. **Mixed epochs.** Population 2020, imagery from whatever scene came first, buildings and POIs from a 2026 Overture release.
5. **Loose residential mask.** `population >= 10` on a 1 km WorldPop pixel kept 88% of cells, including forest, paddy and 691 cells with no buildings.

## Decision

### 1. One reference epoch: calendar year 2023

All layers target 2023. Layers fall into three classes:

| Class | Rule |
|---|---|
| **Dynamic** (S2, Landsat, Dynamic World, VIIRS, S5P NO₂, PM2.5) | Computed exactly for 2023 (or a 2023 season, see §2). |
| **Fixed-epoch products** (GHS-POP, GHS-SMOD, GHS-BUILT-S, Open Buildings Temporal) | Use the 2023 layer if one exists; otherwise interpolate linearly between the bracketing epochs (GHS-POP 2020 → 2025). |
| **Snapshots** (OSM network, Overture POIs and footprints) | Use the snapshot closest to 2024-01-01 that the schema allows; otherwise the current snapshot. |

Every layer records its *effective* date range. Any layer that misses 2023 has its gap **quantified**, not just stated: built-up change per cell between GHS-BUILT-S 2020 and 2025 is reported as an upper bound on how much the physical stock moved.

### 2. Representative composites

Optical and thermal channels are **median composites of cloud-masked, clear-sky observations over the 2023 dry season (1 June – 30 September)**, not whole-year composites. In a whole-year composite, cloud persistence from November to March decides which months each pixel draws on. Paddy phenology (flooded → green → bare, 2–3 cycles a year) and wet-soil SWIR darkening then vary between cells for reasons unrelated to living conditions. A fixed dry-season window keeps cells in a comparable phenological and moisture state.

A composite counts as representative only if it passes all of the following, checked **per H3 cell** and recorded as QA columns:

| Check | Threshold | QA column |
|---|---|---|
| Clear observations per pixel (median across the cell's pixels) | Sentinel-2 ≥ 5; Landsat ≥ 3 | `<layer>_n_clear` |
| Cell area covered by a valid composite pixel | ≥ 80% | `<layer>_valid_frac` |
| Window tier used (see ladder) | Tier 1 preferred | `<layer>_tier` |
| Median acquisition day-of-year of contributing observations | Reported | `<layer>_median_doy` |

**Window ladder.** A cell that fails a tier moves to the next one. The tier is recorded, never hidden:

| Tier | Sentinel-2 | Landsat 8/9 |
|---|---|---|
| 1 | Jun–Sep 2023 | Jun–Sep 2023 |
| 2 | May–Oct 2023 | May–Oct 2023 |
| 3 | Jun–Sep 2023 + Jun–Sep 2024 | Jun–Sep 2022 + 2023 + 2024 |
| Fail | Cell marked `NaN` and excluded from training via mask | same |

**Study-area checks** (reported in the Stage 3 report):
- Share of populated cells per tier. If more than 10% need Tier 3, revisit the window before training.
- Seam check: no visible step across Sentinel-2 MGRS tile, orbit, or Landsat path/row boundaries (compare mean values in a 2-cell band either side of each boundary).
- Independent sanity check: Spearman correlation of the LST composite with MODIS MOD11A2 daytime LST (same window, 1 km), and of NDVI with Dynamic World tree + grass + crop probability. Investigate if ρ < 0.6.

**Water is the exception.** Flood and drainage exposure peaks in the wet season, so the water channel is the **2023 whole-year water frequency** from Dynamic World (share of clear observations classed as water), not dry-season MNDWI.

### 3. Area-weighted zonal aggregation

Every raster is aggregated onto the H3 Res-8 polygons with an **area-weighted reducer at the layer's native scale** (Google Earth Engine `reduceRegions`, which weights pixels by fractional overlap): mean for intensive quantities (indices, LST, radiance, concentrations), sum for extensive quantities (population). Centroid point sampling is removed.

Layers coarser than a Res-8 cell (VIIRS, S5P NO₂, PM2.5) are **not downscaled**. They are area-weighted onto cells and treated as neighbourhood or regional context, and the paper says so.

### 4. Processing platform: Google Earth Engine

Compositing, cloud masking and zonal reduction run on GEE. H3 polygons are uploaded once as a table asset and the reduced table is exported. Planetary Computer was rejected for this: compositing about 128 M pixels per band, per window tier, is heavy on a single machine, and GEE's `reduceRegions` gives area-weighted cell statistics directly.

### 5. Channel source changes

| Channel | Was | Now |
|---|---|---|
| Water | Single-scene MNDWI | Dynamic World 2023 water frequency |
| Multi-pollutant AQI | One-hour Open-Meteo European AQI (ozone-driven) | Sentinel-5P tropospheric NO₂, 2023 median |
| PM2.5 | One-hour Open-Meteo, IDW from 8 values | ACAG V6.GL satellite PM2.5, median of 2023 monthly means |
| LST | Single misregistered Landsat scene | Landsat 8/9 ST_B10 dry-season median at 30 m (option A; no downscaling) |
| Night lights | One VNP46A2 night (NYE 2023) | VIIRS VNL v2.2 annual 2023 (`median_masked`) |
| Population | WorldPop 1 km 2020, point sample | GHS-POP R2023A 100 m, interpolated to 2023, zonal sum |

Open-Meteo/CAMS is kept only as a 2023 hourly-median **validation** series, alongside ground stations. It is not a feature.

### 6. Residential cell mask

A cell is a **residential cell** if it has population density ≥ 300 persons/km² (the lowest settlement threshold in the GHSL Degree of Urbanisation, about 220 people per Res-8 cell) **and** at least one building footprint. Sensitivity is reported at 150, 300 and 1,500 persons/km². Non-residential cells stay in the graph for message passing but are excluded from loss and metrics. This replaces `population >= 10` and ADR 0001's `WorldPop > 0`.

The full list of native, as-ingested and target resolutions is in [`docs/input_data_resolution.md`](../input_data_resolution.md).

## Considered options

- **Whole-year composites.** Rejected for optical and thermal layers (reasons in §2). Kept for water frequency.
- **Random-forest LST downscaling from Sentinel-2 indices to 10 m.** Rejected. Landsat thermal is already 100 m native (~74 samples per cell), so downscaling buys nothing at Res-8. It would also predict LST from NDVI/NDBI/BSI, which are themselves model inputs, making the LST channel partly circular for the autoencoder.
- **Year-long median of Open-Meteo/CAMS for air quality.** Rejected as a feature. It fixes representativeness in time but not space: the ~40 km grid gives a smooth gradient with no cell-level information.
- **Keeping WorldPop 1 km.** Rejected. Its pixels (~0.86 km²) are larger than cells, so it double-counts (total came out at 46.5 M), and unconstrained allocation puts people in forest and paddy.

## Consequences

- **Positive**: every channel is correctly georeferenced, aggregated over the whole cell, and dated to one epoch, with per-cell QA showing how representative it is.
- **Negative**:
  - Depends on a GEE account and project; reduced tables must be exported and versioned so results stay reproducible offline.
  - Three channels (night lights, NO₂, PM2.5) remain coarser than a cell. Their cell-to-cell variation is mostly between neighbourhoods, not within them.
  - Cells that fail every window tier become `NaN` and are masked, so the residential cell count will change.
  - Feature names, the glossary, `configs/default.yaml` and the Stage 4 friction channel split (water and NO₂ channels) must be updated together.
