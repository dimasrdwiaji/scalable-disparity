# 02: 10D Feature Harmonization, P99 Winsorization & Matrix Assembly

**What to build:** Implement $P_{99}$ winsorization and 10D feature matrix assembly in `src/phys_living_index/features/build_features.py`. Ensure living floor space per capita ($R_{\text{space}}$) and nighttime lights per capita ($E_{\text{night}}$) are winsorized at $P_{99}$ before scaling to prevent commercial CBD denominator artifacts (`REV-1`), apply universal Min-Max benchmarks, invert hazard indicators, and output a validated numpy array $X \in [0.0, 1.0]^{N \times 10}$.

**Blocked by:** 01 (needs reachable amenities output from isochrone calculation)

**Status:** ready-for-agent

- [ ] A pure winsorization function clips values above a given percentile (default 99th percentile), unit-tested on synthetic distributions with extreme outlier spikes.
- [ ] `compute_living_space_ratio` incorporates $P_{99}$ winsorization before division by UN-Habitat $9.0\text{ m}^2$ threshold.
- [ ] An energy radiance per capita function incorporates $P_{99}$ winsorization.
- [ ] Inverted scalers transform heat, $\text{PM}_{2.5}$, and multi-pollutant AQI into positive living standard channels bounded in $[0.0, 1.0]$.
- [ ] `build_10d_feature_matrix` assembles all 10 standardized columns for all H3 cells into an $(N \times 10)$ array, asserting valid ranges, no NaNs, and correct shape.
