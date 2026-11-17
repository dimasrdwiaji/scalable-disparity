# Handoff — phys_living_index, Stage 3 remediation (live data run in progress)

Written 2026-11-03 for an agent with **no prior context**. Read this whole file, then the "Read first" list, before touching anything.

- **Repo:** `C:\Users\Dimas RD\Documents\projects\phys_living_index` (Windows; PowerShell is the primary shell, Git Bash also available).
- **Branch:** `feat/feateng-and-modelling`. **Nothing from this work is committed.** A few `tests/` deletions/renames are staged (from `git rm`/`git mv`); everything else is unstaged or untracked. Commit/push only when the user asks.
- **Tooling:** `uv run <cmd>`, `uv run pytest -v` (integration tests skipped by default via `-m 'not integration'`), `uv run ruff check .`. Current state: **72 passed, ruff clean** (verified 2026-11-03).

---

## 1. What the project is (one paragraph)

An unsupervised GeoAI index of *physical living standards* for Jabodetabek + Karawang (bbox `[106.35, -6.75, 107.65, -5.95]`) on **H3 resolution 8** cells (17,154 cells, ~0.737 km² each). Ten channels per cell (living space, built-up, 15-min walk amenities, bare soil, night lights, vegetation, heat, water, PM2.5, NO₂) feed a **Graph Attention Autoencoder** (2-D bottleneck) whose reconstruction error marks segregation boundaries ("friction"). Pipeline stages: 1–2 ingestion, **3 feature engineering (current)**, 4 modelling/disparity (code already exists, commit `ff7632a`), 5 validation, 6 manuscript. The user wants the workflow to be **portable to other regions**, where drivers and extent of disparity will differ.

## 2. Read first (in this order)

1. `CLAUDE.md` — tooling and the architectural boundary: ingestion keeps authentic physical units; all scaling to [0,1] happens only in `src/phys_living_index/features/`.
2. `GLOSSARY.md` — updated this session (Residential Cell, Reference Epoch, Representative Composite, Window Tier, Universal Benchmark, Reference Sample, Measurement Setting, Context Channel, Heat Island Intensity, Water Frequency, Traffic Combustion Exposure/NO₂). Use these terms.
3. ADRs in `docs/adr/`:
   - `0001-h3-gat-ae-unsupervised-disparity.md` (original design; status line lists what is superseded)
   - `0002-reference-epoch-representative-composites-zonal-aggregation.md` — 2023 epoch, dry-season representative composites with per-cell window ladder, area-weighted zonal aggregation on GEE, channel source swaps, residential mask
   - `0003-universal-frozen-benchmarks-and-channel-weighting.md` — frozen universal benchmarks (never per-area), per-region measurement settings, heat island intensity, uniform weights (inverse-variance = sensitivity run), drivers measured post-training
   - `0004-everyday-amenity-universe.md` — expanded amenity list (warung, kiosks, worship, etc.)
4. `docs/input_data_resolution.md` — native → as-ingested → target resolution and aggregation rule per channel.
5. `.scratch/stage-3-feature-engineering/spec.md` — read the **"Revision 2"** section at the bottom (problem list + ticket table).
6. Tickets `.scratch/stage-3-feature-engineering/issues/03…14-*.md` — each has a `## Comments` block with implementation notes and **deviations**. Acceptance checkboxes are still unticked on purpose; tick only after the live run verifies them. Issue-tracker conventions: `docs/agents/issue-tracker.md`.
7. Original report under review (outside repo): `c:\Users\Dimas RD\.gemini\antigravity\brain\ecf500e3-2cd4-4343-a9ab-e2de20a84561\stage_3_feature_engineering_report.md`.
8. Next stage: `.scratch/stage-4-modeling-disparity/spec.md` (+ its issues). Stage 4 code is generic (takes `mask` and `channel_weights`); socio channels = indices 0–4, bio = 5–9, which the new channel order preserves.
9. `docs/handoff_phys_living_index_stage3.md` — an **earlier in-repo handoff** from a previous session. Mostly accurate, **but its "Bugs fixed" section is wrong about the code** (see §5). It is untracked; ask the user whether to keep or delete it.

## 3. How we got here (context the docs don't spell out)

- The user asked for a review of their Stage 3 report. The review found the inputs unusable: Sentinel-2 and Landsat were **one scene each, decimated to 200×200 and georeferenced to the whole bbox** (every pixel misplaced); every raster was **centroid point-sampled**; VIIRS was a single night (2023-12-31, New Year's Eve); air quality was one Open-Meteo `current` reading (20 anchors, 8 distinct values, AQI = ozone sub-index); WorldPop 1 km double-counted (46.5 M); the mask `pop >= 10` kept 88% of cells, incl. 691 with no buildings scored as worst overcrowding; inverse-variance weights gave BSI 3.47 vs living space 0.06.
- User decisions, in order: use **Google Earth Engine**; one **2023** reference epoch (document and quantify gaps); **dry-season (Jun–Sep) median** composites made representative per cell, whole-year for water; **LST option A** (Landsat 30 m, no random-forest downscaling — it would be circular with NDVI/NDBI inputs); prefers **median** statistics.
- On scaling, the user first thought the GAT-AE "learns variable weights like SHAP". Explained: attention weights are over neighbours; with a 2-D bottleneck the model keeps high-variance directions (PCA-like), so scaling sets each channel's influence. Because the goal is cross-region comparability, we chose **universal frozen benchmarks** (standards where they exist, else P1/P99 of a global reference sample, versioned; never tuned to a study area). The user then raised that tighter bounds might be Jakarta-specific → resolved by deriving them from a **global** sample, not the study area. "Keep 2" = keep **uniform weights (main) and inverse-variance (sensitivity)**.
- **User preference:** explain the significance and impact of choices (with numbers where possible), not just list choices. Be concise and concrete.

## 4. What is implemented (code + offline tests)

Do not re-derive — read the files:
- `src/phys_living_index/data/gee.py` — `reduce_image_over_cells` (client-side cell batches, auto-split on failure), parsing, valid-area fraction, parquet provenance (`write_table_with_provenance` / `read_provenance`), `initialize_ee` (uses `EE_PROJECT` from `.env`).
- `src/phys_living_index/data/gee_layers.py` — all Earth Engine image builders, window ladder (`reduce_tiered_composite`, `select_window_tier`), ERA5 dry-season helper.
- `src/phys_living_index/data/ingest_acag.py`, `data/zonal_local.py` (exactextract), `data/ingest_context.py` (Open-Meteo 2023 hourly-median **validation only**), `data/credentials.py`.
- `src/phys_living_index/features/build_features.py` (benchmark loading/scaling, clip shares, heat island, living space, floor-area fill), `features/residential.py`, `features/isochrones.py`, `features/reference_sample.py`.
- `src/phys_living_index/pipeline/stage3.py` — per-layer cache `data/interim/layers/<layer>.parquet`, `build_layers`, `run_stage3`, writes `data/processed/stage3_qa.json`.
- Configs: `configs/default.yaml` (region measurement settings), `configs/benchmarks/benchmarks_v0.yaml` (**provisional** bounds).
- Scripts: `scripts/run_feature_engineering.py` (`--only-layers`, `--rebuild`), `scripts/run_ingestion.py` (`--root`, `--only`), `scripts/build_graph_dataset.py`, `scripts/build_reference_benchmarks.py` (select/prepare/run/pool), `scripts/plot_feature_diagnostics.py` (renamed columns, untested).

## 5. ⚠️ Critical: two bug fixes are NOT in the code

The previous session reports fixing these and rebuilt the `population` layer with the fixes (current cache: **40.73 M people, 9,346 cells ≥ 300/km²**, verified). But on 2026-11-03 the source does **not** contain either fix — the edits were lost. **Re-apply both (test-first) before building any more layers**, otherwise `open_buildings_floors` will be all-NaN and any population rebuild will be wrong:

1. `data/gee.py::parse_reduce_regions` — when a **single, uncombined** reducer (e.g. `sum` with `extra_stats=()`) runs on a **multi-band** image, Earth Engine names outputs by **band** (`population`), not `population_sum`. Current code only accepts `<band>_<stat>` or (single band) `<stat>`. Add: if `len(stats) == 1` and `band in props`, use `props[band]`. Add a unit test in `tests/test_gee.py`. Affects `population` (multi-band sum) and `open_buildings_floors` (multi-band sum).
2. `data/gee_layers.py::ghs_population` — GHS-POP has negative no-data (≈ −200 over sea) that gets summed into cells. Clamp each epoch image with `.max(0)` before interpolating.

After fixing, rebuild `population` (`--rebuild population`) and confirm ~40.73 M again.

## 6. Live-run state (verified 2026-11-03)

Earth Engine is authenticated; `EE_PROJECT` is set in `.env` (don't print or copy it). OSM dated extract `data/raw/osm/java-240101.osm.pbf` (833 MB) downloaded.

Cached layers in `data/interim/layers/` (all 17,154 rows):

| Layer | Key facts |
|---|---|
| buildings | 14,541 cells with footprints; only 6,291 of 9.64 M footprints have a height |
| accessibility | OSM 2024-01-01: 3.97 M nodes, 4.20 M edges, 173,820 POIs; all-cell median 0, P99 270, max 1,352; 22% of cells snap > 500 m (mostly sea/forest — re-check on residential cells) |
| night_lights | VIIRS VNL v2.2 annual 2023; median 2.2, max 108 nW/cm²/sr |
| population | 40.73 M total (built with the fixes in §5) |
| settlement_class | GHS-SMOD 2025 mode |
| no2 | S5P 2023 median of 5,077 images |
| modis_lst | 2,381 NaN (sea) |
| vegetation_probability | DW trees+grass+crops, Jun–Sep 2023 |
| water | 1,321 NaN (< 10 obs); 155 DW images |
| landsat | tiers {1: 12,420, 2: 491, 3: 2,130, 0 (failed): 2,113}; **LST min 258 K is implausible** |

**Still to build:** `sentinel2` (interrupted mid-Tier 1; 98 scenes), `open_buildings_floors` (needs fix §5.1 first), `pm25` (needs ACAG files).

Background jobs die when a session ends — the last two did. Run long builds in the background **and** expect to resume (the per-layer cache makes reruns cheap).

## 7. Next steps (in order)

1. Re-apply the two fixes in §5 with tests; rebuild `population`; verify.
2. Build remaining EE layers (background, ~10–30 min):
   `uv run python scripts/run_feature_engineering.py --only-layers sentinel2 open_buildings_floors`
3. Investigate Landsat: 258 K minimum and 2,113 tier-0 cells. Check how many are **residential** cells once the mask exists; likely residual cloud/cloud-edge or water. Options: stricter `ST_QA` limit, dilate cloud mask, exclude permanent water. Compare against MODIS (ADR 0002 sanity check, ρ ≥ 0.6).
4. When the user has placed ACAG files in `data/raw/acag/`, verify the NetCDF variable via `detect_pm25_variable`, then run the full pipeline: `uv run python scripts/run_feature_engineering.py`, then `uv run python scripts/build_graph_dataset.py` (**it has no `--help`; running it builds/overwrites `graph_data.pt`**).
5. Review `data/processed/stage3_qa.json`: tier shares (flag Tier 3 > 10%), clip shares (> 5% = outside reference), mask sensitivity, epoch gap, sanity correlations, residential snap-distance flags. Population total vs BPS 2023 kab/kota totals (ticket 07).
6. Redundancy check (|ρ| > 0.8 pairs, e.g. NDBI–BSI) → keep/merge decision appended to ADR 0003 (ticket 12) — discuss with the user.
7. Rewrite the Stage 3 report (ticket 13) from the QA outputs. Label everything **provisional** until `benchmarks_v1` exists. Apply the review's wording fixes (rural share is of cells not area; no "perfectly matching" claims; discuss network vs buffer gap).
8. Tick ticket checkboxes only for verified items; update ticket `Status` lines.

## 8. Blocked on the user

- **ACAG PM2.5:** the 12 monthly 2023 files of V6.GL.02.04 at 0.01° (Box links only: https://sites.wustl.edu/acag/datasets/surface-pm2-5/) into `data/raw/acag/`. The folder does not exist yet. `run_stage3` stops at `pm25` without them.
- **Ticket 14 (benchmarks_v1):** a GHS Urban Centre Database table with columns `name, country, world_region, climate_class, population, min_lon, min_lat, max_lon, max_lat`. Running 50–100 cities is heavy (OSM extract + routing per city) — agree scale with the user before starting.
- Whether to keep `docs/handoff_phys_living_index_stage3.md` in the repo.

## 9. Pitfalls

- PowerShell: no `&&`; native stderr lines show as `NativeCommandError` noise even on success — check exit codes/output, not the red text. Multi-file bash heredocs have failed here; prefer the Write tool.
- Never write placeholder/fallback values when a download fails (ADR 0002); raise instead.
- Don't compute scaling bounds from the study area (ADR 0003); bounds come only from `configs/benchmarks/`.
- H3 grid must stay identical: `pipeline.stage3.generate_h3_grid` (uses `h3.geo_to_cells`) reproduces the original 17,154 cells — keep it.
- Don't commit or push unless asked.

## 10. Suggested skills (call via the Skill tool)

- `mattpocock-skills:tdd` — re-apply the §5 fixes test-first; any further pipeline fixes.
- `mattpocock-skills:diagnosing-bugs` — Landsat 258 K / tier-0 investigation; any layer whose numbers look wrong.
- `data:validate-data` and `data:statistical-analysis` — checking layer distributions and `stage3_qa.json` before the report rewrite.
- `mattpocock-skills:domain-modeling` — before editing ADRs/GLOSSARY (redundancy decision, any new terms).
- `mattpocock-skills:code-review` — review the branch against tickets 03–14 before the user commits.
- `data:create-viz` / `dataviz` — when regenerating Stage 3 figures (`scripts/plot_feature_diagnostics.py`).
