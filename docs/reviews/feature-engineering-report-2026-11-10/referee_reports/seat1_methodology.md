# Referee Report: Spatial Feature Engineering for Physical Disparity
**Reviewer Identity / Seat**: Methodology & Spatial Statistics
**Evaluation Date**: 2026-11-09
**Overall Recommendation**: Major Revision
---
### 1. Summary of Appraisal
The report sets out a clear seven-indicator feature store on H3 resolution 8 and is candid about many limitations. Its statistical foundation is not yet adequate. The report and the pipeline have diverged: the vector specified is not the vector built, and channel 1 is still the volume-based living-space ratio that §6.2 declares circular. Population, ΔLST and stratum tables cannot be regenerated from the outputs, and Tables 5.2 and 5.3 contradict each other on the report's own numbers. I do not accept the claim that footprint per capita resolves dasymetric endogeneity. The denominator remains GHS-POP, and an exact decomposition shows that indicator variance comes from disagreement between building products and from modelled height, with no demographic contribution. The sub-5 m² tail is largely a product of the non-residential filter. Resolution 8 is defensible for neighbourhood-scale screening but not for kampung-level claims, and no scale or zoning test is reported. Spatial dependence is strong (Moran's I up to 0.95; effective sample sizes in the tens to low hundreds) and unaddressed. Missing LST is concentrated in dense northern Jakarta. All of this appears repairable by regenerating the report from one versioned run, substituting or dropping the living-space channel, and adding the sensitivity work below.

### 2. Major Methodological Critiques (P0 / P1)
- **Point 1 (Conceptual Validity)**: *§7.1 Q2. Is replacing R_space with 2D footprint per capita statistically sound, and does it resolve dasymetric endogeneity?* No on both counts as written, with one part of the diagnosis correct.
  - The diagnosis holds for the GHS-volume ratio: its median is about 57 m² in every density band (57.17, 57.18, 57.19, 55.79), CV 0.19, Moran's I 0.95. The stated constant of 18 to 22 m² is wrong, and §2.2 gives a different formula to which the cancellation does not apply.
  - The replacement keeps GHS-POP in the denominator. Population correlates at 0.985 with residential built volume. Using log(FP/Pop) = log(FP/S) − log(V/S) + log(V/Pop), the covariance shares are 67.9%, 32.4% and −0.2%. The variation is a ratio of two building products plus inverse GHSL height, and contains no independent population signal.
  - The indicator is lambda divided by population density by identity, so it is inverse density in another form. Tall housing is scored as overcrowded. "Model-free" is incorrect because both terms are model outputs.
  - Most importantly, it is not in the feature matrix. Channel 1 remains the volume ratio, with 74.4% of cells clipped at 1.0 because the 54 m² bound sits under its near-constant level.
- **Point 2 (Data & Metric Integrity)**: The numbers do not support the text.
  - Population is 32.10 M reported and 40.48 M in the outputs. ΔLST medians are +0.13 K reported and +5.85 K in the outputs, and the reported distribution is not attainable under either a P10 or a median baseline.
  - Stratum means do not average to the overall means: footprint per capita 43.44 against 39.81, NDVI 0.438 against 0.418, ΔLST +0.09 against +0.42 K. Kota density should be 9,143, not 6,840.
  - The modelled universe is 8,375 cells, not 9,345. The 9.6% missing LST reaches 34.2% in Jakarta Utara and 32.9% in Jakarta Barat, and excluded cells are denser, so it is not ignorable (W15).
  - The amenity layer uses 1,000 m rather than 1,125 m and a broader Overture POI set than the "essential" OSM set described. Susenas is called ground truth, but no comparison is shown.
- **Point 3 (Artifacts & Confounders)**: *§7.1 Q1. Is H3 resolution 8 defensible, or does it introduce unacceptable ecological fallacy and MAUP dilution?* It is conditionally defensible, for a narrower claim than the one made.
  - From rebuilt fine-scale footprints, 72.9% of lambda variance among resolution 9 cells (10.5 ha) lies between resolution 8 parents, and 51.6% at resolution 10 (about 1.5 ha; centroid assignment makes this noisy). In central Jakarta the figures are 64% and 41.5%. Rank correlations among channels are stable from resolution 8 to 6 (lambda and ΔLST 0.63, 0.65, 0.67).
  - Dilution is real at the scale the report cares about: 25.6% of resolution 9 cells with lambda at or above 0.40 sit in parents under 0.30. Extremes also move, with the footprint per capita P5 going 7.46, 9.82, 10.99 at resolutions 8, 7, 6.
  - Use resolution 8 as a neighbourhood screening unit, with within-cell dispersion from resolution 9 as an added descriptor. Do not use it to assert conditions in 2 to 10 ha kampungs (Fotheringham and Wong, 1991; Robinson, 1950; Kwan, 2012). The maximum-lambda cell is in Jakarta Utara, not Barat, and has 26.39 m² per person, so the narrative profile in §5.4 joins facts from different places.
  - The 2.8 to 3.1 m² figures are not measured at Tambora or Penjaringan. They are municipal fifth percentiles, and 338 cells under 5 m² have a median of 97.5% of footprint removed as non-residential (median gross 38.4 m²). Cells with 0.00 and 0.075 m² per person in Penjaringan are filter failures.

*§7.1 Q3. How should the pipeline handle extreme right-skew and zero-inflation in POI accessibility and slope before representation learning?* Treat them as two different zero processes, not with one transform.
  - Amenity (21.4% zeros, 4.4% of residents; skew 4.84 raw, 0.57 after log1p): keep log1p, add a presence channel, and consider a hurdle or zero-inflated count reconstruction term (Cragg, 1971; Lambert, 1992; Lopez et al., 2018). Separate true zeros from coverage zeros using an external completeness signal. Replace the single centroid origin with population-weighted origins from finer cells.
  - Slope (59.9% zeros holding 73% of residents; 36.2% and 19.9% zeros at resolutions 7 and 6, so the spike is scale-dependent): do not pass as a min-max share. Recompute on built-up pixels with a bare-earth DEM as exposure, then either use presence plus a magnitude conditional on presence, or remove from the embedding and overlay after modelling.
  - Assess reconstruction separately on zero and non-zero cells. Report influence by channel, since scaled variance governs it.

### 3. Minor Technical Concerns (P2)
- Hexagon geometry: edge 461.4 m implies 0.553 km², and centroid spacing is √3 times the edge. H3 average edge is 531.4 m.
- The stated Pop ≥ 50 filter gives 10,977 cells, not 9,345.
- "Vegetation Cover Fraction [0, 1]" is mean NDVI, which is negative in places.
- Fringe share is stated as 83.8% and 80.9%.
- An undisclosed eave correction removes about 17.4% of area (roof to wall ratio 0.826). It is not strongly density-dependent, but 21.88% would be about 26% on the stated definition.
- §6.5 says slope is zero across DKI, while outputs show a maximum of 9.5%, and GLO-30 is a surface model.
- Table 5.4 aggregates do not satisfy lambda = FP × Pop / Area for Barat and Pusat, although the provincial total does.
- The text threshold of 5 m² and the benchmark of 9 m² differ, and both are interior-area standards being applied to a roof-plan ratio.
- The GRIM check on the amenity mean is consistent but has negligible power at this N.

### 4. Fact-Checking & Comparative Grounding
- *Comparative Megacity Evidence*: I offer no independent comparative benchmark. The Metro Manila comparison in §6.1 rests on citations that the citation audit could not resolve to matching works, so it should be treated as unsupported until replaced. This is for the domain and regional seats to assess in detail.
- *Empirical Literature Concordance*: Strong positive spatial dependence and a dominant urbanisation factor are as expected for gridded urban indicators; the first component carries 52% to 56% of variance and the largest VIF on the stated vector is 4.12, so collinearity is one common factor and not an inversion hazard. Lambda correlates 0.87 with density, which undercuts §4.1's claim of independence from demography. Clifford-Richardson effective sizes of 23 to 147, depending on lag range, show that N = 9,345 is not the inferential sample (Clifford et al., 1989; Dutilleul, 1993). The effect of population-grid fitness on derived indicators is documented in Leyk et al. (2019). Sensitivity practice for composite inputs is set out in Saisana et al. (2005), and blocked validation in Roberts et al. (2017) and Ploton et al. (2020). Several report citations have wrong or broken DOIs per the repository audit and need checking.

### 5. Concrete Actionable Recommendations for Revision
1. Regenerate every table, equation and dataset description from one versioned run, with a run identifier, and reconcile all stated definitions with code (P0).
2. Decide the living-space channel. Remove the volume ratio as a living-space measure. Either adopt a census-based denominator at its native support for footprint or floor-area indicators or relabel the channel as a built-form ratio and stop claiming that dasymetric endogeneity is resolved (P0).
3. Screen out filter failures: treat zero or heavily filtered net footprint as missing. Report results on gross and net footprint, and validate against Susenas with honest treatment of unit dependence (P1).
4. Report sensitivity for resolutions 7, 8 and 9, zoning shifts, and a dispersion descriptor (for example resolution 9 lambda variance within resolution 8), and limit all claims to the supported scale (P1).
5. Report Moran's I, effective sample sizes and collinearity, and use spatially blocked validation and multiplicity-controlled local statistics (P1).
6. Adopt the two-part handling for amenity and slope, and specify transforms, bounds, weights and a global sensitivity analysis (P1).
7. Disclose missingness, justify the handling of LST gaps with a stated mechanism, and compare results with imputed and excluded cells (P1).
8. Report population-weighted estimates next to cell means and state each table's estimand (P1).
