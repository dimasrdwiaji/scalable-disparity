# Input Data Resolution: Native → As Ingested → Target on H3 Res-8

Companion to [ADR 0002](adr/0002-reference-epoch-representative-composites-zonal-aggregation.md). Analysis unit: **H3 Res-8 cell, mean area ≈ 0.737 km²** (equivalent square ≈ 858 m side).

"Native px / cell" is the number of native pixels in one cell. Above 1, the layer is finer than the cell and is **aggregated** (zonal statistic). Below 1, the layer is coarser than the cell and is **assigned** by area weighting. It is never downscaled.

Reference epoch: **2023**. Dry-season window: **1 Jun – 30 Sep 2023**, with the window ladder in ADR 0002 §2.

## Feature channels

| # | Channel | Source (target) | Native resolution | Native px / cell | As ingested now (Stage 3 rev. 3) | Target time window | Cell aggregation strategy |
|---|---|---|---|---|---|---|---|
| 1 | Living space ratio — floor area | Overture buildings (footprints) + Open Buildings 2.5D Temporal 2023 (height where Overture lacks it) | Vector footprints; heights at 4 m effective | n/a (vector) | Overture 2026-10-21 footprints, mostly fallback floor counts | Footprints: nearest-2024 snapshot; heights: 2023 | Sum of footprint area × floors per cell (footprint centroid in cell) |
| 1 | Living space ratio — population | GHS-POP R2023A | 100 m (3 arcsec, Mollweide) | ~74 | WorldPop 2020, 1 km (0.0083°), **centroid point sample** (~0.86 km² pixel; total 46.5 M) | 2023, linear interpolation of 2020 and 2025 epochs | Area-weighted **sum** |
| 2 | Built-up density (NDBI) | Sentinel-2 L2A harmonized (B8, B11) | 10 m / 20 m (B11) | ~7,370 / ~1,840 | One scene, decimated to 200 × 200 over bbox (~720 × 440 m), **misregistered**, centroid sample | Dry-season median, cloud-masked (Cloud Score+) | Area-weighted mean at 20 m |
| 3 | 15-min walk amenities | OSM walk network + Overture places | Vector | n/a | OSM `java-latest` (2026) + Overture 2026-10-21 | Nearest-2024 snapshot | Network Dijkstra from the snapped centroid, 1,000 m budget minus snap distance |
| 4 | Bare soil (BSI) | Sentinel-2 L2A harmonized (B2, B4, B8, B11) | 10 m / 20 m | ~7,370 / ~1,840 | As NDBI (misregistered) | Dry-season median | Area-weighted mean at 20 m |
| 5 | Night-time radiance | VIIRS VNL v2.2 annual (`median_masked`) | 15 arcsec (~463 m) | ~3.5 | VNP46A2 **single night 2023-12-31**, centroid sample | 2023 annual | Area-weighted mean |
| 6 | Vegetation (NDVI) | Sentinel-2 L2A harmonized (B4, B8) | 10 m | ~7,370 | As NDBI (misregistered) | Dry-season median | Area-weighted mean at 10 m |
| 7 | Thermal comfort (LST) | Landsat 8/9 C2 L2 `ST_B10` | 100 m native thermal, delivered at 30 m | ~74 native / ~820 delivered | One scene, decimated to 200 × 200 over bbox, **misregistered**, centroid sample | Dry-season median, QA_PIXEL-masked | Area-weighted mean at 30 m (no downscaling) |
| 8 | Water frequency (replaces MNDWI) | Dynamic World V1 `label == water` | 10 m | ~7,370 | Single-scene MNDWI (misregistered) | **Whole year 2023** (flood exposure peaks in the wet season) | Per-pixel share of clear observations classed water → area-weighted mean |
| 9 | PM2.5 | ACAG V6.GL satellite PM2.5 (monthly) | 0.01° (~1.1 km) | ~0.6 | Open-Meteo `current`, 20 anchors / 8 distinct values (CAMS ~0.4°, ~44 km), IDW | 2023, **median of 12 monthly means** | Area-weighted assignment (context, coarser than cell) |
| 10 | NO₂ (replaces AQI) | Sentinel-5P TROPOMI OFFL L3 tropospheric NO₂ | 3.5 × 5.5 km native; GEE L3 grid ~1.1 km | ~0.04 native | Open-Meteo `current` European AQI (= ozone sub-index) | 2023, median of daily | Area-weighted assignment (context, coarser than cell) |

## Masks, QA and validation layers (not features)

| Layer | Source | Native resolution | Native px / cell | Time | Use |
|---|---|---|---|---|---|
| Residential cell mask | GHS-POP (density) + building count | 100 m + vector | ~74 | 2023 | ≥ 300 persons/km² **and** ≥ 1 building; sensitivity 150 / 300 / 1,500 |
| Settlement class | GHS-SMOD R2023A | 1 km | ~0.74 | 2020/2025 (nearest to 2023) | Sub-region strata for reporting (replaces hand-drawn regions) |
| Epoch-gap check | GHS-BUILT-S R2023A | 100 m | ~74 | 2020 vs 2025 | Quantify built-stock change across the gap |
| LST sanity check | MODIS MOD11A2 daytime LST | 1 km | ~0.74 | Dry season 2023 | Spearman vs Landsat composite |
| NDVI sanity check | Dynamic World tree + grass + crop probability | 10 m | ~7,370 | Dry season 2023 | Spearman vs NDVI composite |
| Air-quality validation | Open-Meteo/CAMS hourly; Jakarta SPKU / OpenAQ stations | ~0.4° / points | ≪ 1 | 2023 | Hourly median; checks against PM2.5 and NO₂, not features |

## Rules

1. **Aggregate at native scale.** Reduce each raster at its native `scale` in EPSG:32748 (UTM 48S), never on a resampled copy.
2. **Mean for intensive, sum for extensive.** Indices, LST, radiance and concentrations take the area-weighted mean; population takes the area-weighted sum.
3. **Coarse layers are context.** Channels with fewer than 1 native pixel per cell (5 partially, 9, 10) carry neighbourhood or regional variation, not within-cell variation. The methods section says so.
4. **Authentic units at ingestion** (CLAUDE.md): reflectance indices in [−1, 1], LST in K, radiance in nW/cm²/sr, PM2.5 in µg/m³, NO₂ in mol/m², water frequency in [0, 1]. Scaling happens only in `features/`.
5. **Record provenance.** Every exported table records the asset ID, date range, window tier and scene count.
