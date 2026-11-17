# ADR 0003: Universal Frozen Benchmarks, Per-Region Measurement Settings, and Unweighted Channels

* **Status**: Accepted
* **Date**: 2026-11-02
* **Deciders**: Dimas RD
* **Amends**: ADR 0001 (Negative consequence "Universal Min-Max to [0, 1]": kept, with new benchmark values); **supersedes** ADR 0001 Amendment 2 item 3 (P99 winsorization)

---

## Context

The workflow must transfer to other regions, and the **drivers and extent of disparity are expected to differ between regions**. Results are only comparable across regions if a scaled value means the same thing everywhere.

The Stage 3 review found:

1. **Benchmarks set to the theoretical range, not the realistic one.** NDBI, BSI and MNDWI were scaled over [−1, 1], a range settled land never covers. They were compressed to std 0.04–0.07.
2. **Scaling decides influence, not the model.** The GAT-AE learns neighbour attention (α_ij) and a feature projection that minimises the loss. With 10 channels squeezed into a 2-D bottleneck it keeps the highest-variance directions, much like PCA. Each channel's scaled variance therefore sets its share of the result. On the current data:

| Scheme | Living space | Amenities | LST | BSI | Other channels |
|---|---|---|---|---|---|
| Fixed [−1, 1]-style benchmarks, no weights | 40% | 24% | 17% | 0.6% | 1–8% each |
| Same + inverse-variance weights (current Stage 4) | 10% | 10% | 10% | 10% | 10% each |

3. **Inverse-variance weights make drivers identical everywhere.** They force every channel to equal influence in every region, the same as standardising each channel within the region. That rules out region-specific drivers by construction.
4. **Scaling to each study area's own percentiles brings back the relative-comparison trap.** ADR 0001 rejects this trap in the Meta Relative Wealth Index: a channel that barely varies in one region is stretched until its noise looks like a driver.

## Decision

### 1. Two kinds of configuration

| | **Universal scale settings** | **Per-region measurement settings** |
|---|---|---|
| Scope | Identical for every region; versioned (`benchmarks_v1`, `v2`, …) | Set per region |
| Contents | Channel benchmark bounds, transforms, orientation, residential density threshold | Bounding box, UTM zone, compositing window and ladder, cloud thresholds, amenity category mapping (local terms), walking speed |
| Rule | Never tuned to a study area. A revision creates a new version, and every region is rerun on it | Chosen so each channel's physical value is measured correctly in that place |

### 2. How benchmarks are set

Each channel is mapped to [0, 1] between a frozen lower and upper bound, then clipped. Bounds come from:

- **A standard, where one exists.** Example: UN-Habitat 9 m² for living space.
- **Otherwise, a global reference sample.** P1 and P99 over residential cells of a fixed, stratified set of cities from the GHS Urban Centre Database, covering world regions, Köppen climate classes and city sizes. Each city contributes the same number of randomly drawn residential cells, so no city dominates. The sample and its city list are frozen with the benchmark version.

| Channel | Transform | Lower bound | Upper bound | Orientation |
|---|---|---|---|---|
| Living space ratio | — | 0 m² per capita | 54 m² (6 × UN-Habitat 9 m²) | higher = better |
| Amenities (15-min walk) | `log1p(count)` | 0 | reference P99 | higher = better |
| NDBI | — | reference P1 | reference P99 | context (unoriented) |
| BSI | — | reference P1 | reference P99 | inverted (bare soil = worse) |
| Night-time radiance | `log1p` | reference P1 | reference P99 | higher = better |
| NDVI | — | reference P1 | reference P99 | context (unoriented) |
| **Heat island intensity** (replaces absolute LST) | ΔLST = cell LST − regional background LST, in K | reference P1 | reference P99 | inverted (hotter = worse) |
| Water frequency | — | 0 | 1 | context (unoriented) |
| PM2.5 | — | WHO annual guideline, 5 µg/m³ | reference P99 | inverted |
| NO₂ (tropospheric column) | — | reference P1 | reference P99 | inverted |

**Heat island intensity.** Absolute LST is climate-bound: one global range would place all cold-climate cities at the "comfortable" end. The channel therefore measures excess heat over the region's own background. The background is the median LST of non-residential cells (GHS-SMOD rural, density < 300/km²) dominated by tree or crop cover (Dynamic World) in the same composite. If a region has fewer than 50 such cells, the measurement settings must widen the background buffer and record it. Raw LST in Kelvin is kept at ingestion.

**Clipping replaces winsorization.** Values outside the frozen bounds are clipped. Per region, the share of residential cells clipped at each end is reported for every channel. Above 5% at either end, the region is flagged as outside the reference distribution. That is reported as a finding, **not** fixed by re-tuning that region's bounds.

### 3. Channel weights

- **Main run:** uniform channel weights. A channel's influence then reflects how much it actually varies in that region on the universal scale.
- **Sensitivity run:** inverse-variance weights, reported as a robustness check (overlap of the top-15% friction cells between the two runs).

### 4. Drivers are measured after training, not imposed before it

Region-specific drivers are reported as **per-channel shares of reconstruction error**, summed over hotspots and over the whole region, plus attributions (Integrated Gradients or KernelSHAP) on the encoder's latent coordinates and friction score. These attributions are comparable across regions only because the scale is universal. Each region trains its own model, so latent spaces are **not** compared directly between regions.

## Considered options

- **Benchmarks at the theoretical range, e.g. [−1, 1] (Stage 3 rev. 3).** Rejected: it compresses spectral channels to near-zero influence.
- **Inverse-variance weighting as the main run.** Rejected: it forces equal influence in every region and so cannot show region-specific drivers. Kept as the sensitivity run.
- **Per-region empirical scaling (P1–P99 of each study area).** Rejected: the relative-comparison trap ADR 0001 rejects for the Relative Wealth Index; extent and drivers stop being comparable.
- **Absolute LST with a global range.** Rejected: climate dominates the channel. Heat island intensity measures the built environment's contribution instead.

## Consequences

- **Positive**:
  - Scores, extent and driver attributions mean the same thing in every region.
  - Channels that do not vary in a region drop out on their own.
  - Adding a region needs only new measurement settings.
- **Negative**:
  - The reference sample must be built before final benchmarks exist: every channel computed for about 50–100 cities. Amenity routing is the most expensive part.
  - Until `benchmarks_v1` is frozen, any results are provisional.
  - A benchmark revision forces a rerun of every region.
  - Heat island intensity depends on the background definition, which needs a sensitivity check.
  - The configuration file splits in two: universal benchmarks and per-region settings.
  - `who_pm25_annual_threshold_ugm3: 15.0` in `configs/default.yaml` is the WHO **24-hour** guideline. The 2021 annual guideline is 5 µg/m³; correct it when ticket 12 is implemented.
