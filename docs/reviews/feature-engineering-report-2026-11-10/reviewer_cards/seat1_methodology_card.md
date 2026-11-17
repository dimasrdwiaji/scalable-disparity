contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: block
trigger: "disclosure of parameters needed to recompute a central quantity"
block_class: repairable

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: block
trigger: "a central claim has no corresponding reported analysis"
block_class: repairable

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

Scope of the evidence. I read the manuscript as the claim and the repository as what it claims to describe. All re-analysis scripts are read-only and sit in `work_methodology/` (a1 to a5). Spatial weights are H3 first-ring contiguity on the 9,345 residential cells. Finer-scale results rebuild the pipeline's net residential footprint from `data/raw/buildings.parquet` by the same centroid assignment; the rebuild matches the pipeline at resolution 8 (r = 0.9994, median ratio 0.9997). Resolution 10 is reported with a caveat: centroid assignment lets single large buildings push a 1.5 ha cell above lambda = 1.

Why D1 is a repairable block and not fatal. My Phase 1 fatal clause covers central numbers that cannot be derived from the described procedure, and W2 to W4 come close to it. I hold it at repairable for one reason: the fatal clause also requires a defect that cannot be repaired, and here a coherent pipeline with dated outputs exists, so a report regenerated from one versioned run would repair the mismatch without new data collection. If the authors cannot regenerate the tables from a single versioned run, this judgement should convert to fatal.

Statistical reporting criterion (descriptive reporting of a spatial feature store): PARTLY_MEETS for distribution summaries, DOES_NOT_MEET for uncertainty, spatial dependence, missingness and sensitivity. The manuscript contains no hypothesis tests, so no p-values or degrees of freedom exist to audit. Evidence: W2, W3, W9, W12, W14, W15. The estimate is limited by the absence of any published run identifier linking tables to outputs.

### S1: Limitations are stated in the manuscript itself rather than left for reviewers to discover
**Evidence Anchor**: text: §6 "documents the six primary methodological uncertainties"
Section 6 names MAUP, OSM completeness, DEM resolution and polygon regularisation as open problems. That candour is useful even where the remedy claimed is not established.

### S2: Stratification addresses a real composition problem
**Evidence Anchor**: text: §5.1 "produces misleading results because the study area comprises three distinct geographic regimes"
Separating core, satellite and fringe cells is the correct response to a universe that is 80.9% fringe by count, and the rule reproduces the counts 860, 926 and 7,559.

### S3: Aggregate DKI plan area and footprint per capita agree arithmetically
**Evidence Anchor**: table: Table 5.3, DKI column, rows Evaluated Land Area, 2023 Population and A_fp,res/Pop
13.00 m² times 10,846,531 persons divided by 644.42 km² gives 21.88%, the headline residential value. The identity holds at the provincial level.

### W1: The feature vector specified in the report is not the one built, and channel 1 is the indicator the report declares circular
**Severity**: Critical
**Evidence Anchor**: equation: §1 feature vector x_i, element 2 (A_fp,res,i / Pop_i)
**Confidence**: 5 — direct reading of pipeline code and matrix columns
Section 1 defines element 2 as footprint per capita and §6.2 presents the shift as the resolution. In `feature_matrix_7d.parquet`, footprint per capita is not a channel. Channel 1 is `space_sufficiency_ratio`, built from GHS-BUILT-V residential volume / 3 / GHS-POP / 9 (`stage3.py:704-708`). That is exactly the quantity §6.2 says is mathematically guaranteed to be a smoothed constant. My re-analysis supports that diagnosis: the median is 57.17, 57.18, 57.19 and 55.79 m² across four density bands, the coefficient of variation is 0.19, and Moran's I is 0.95. The upper scaling bound of 54 m² lies below that near-constant level, so 74.4% of residential cells are clipped to 1.0. The channel entering representation learning is therefore close to a saturated constant that carries GHSL's allocation surface. Uncorrected, this invalidates any downstream statement about space sufficiency.

### W2: Reported population and stratum tables cannot be regenerated from the pipeline outputs
**Severity**: Critical
**Evidence Anchor**: table: Table 5.3, rows 2023 Population and Mean Population Density
**Confidence**: 5 — recomputation against dated outputs, weighed for staleness
Residential population is 32.10 M in the report and 40.48 M in the outputs; Kota is 6.33 M against 9.10 M; Kabupaten is 14.92 M against 20.53 M. Table 5.2 and Table 5.3 entries differ materially for FP per capita (mean 39.81 against 29.58), maximum amenity (542 against 1,352), Kota lambda median (13.2% against 18.8%) and municipal P5 values (Jakarta Timur 4.88 against 1.52; Utara 2.84 against 0.08). The Table 5.4 cell counts also differ (Utara 160 against 184). I weighed staleness: the outputs are dated 2026-11-09, and ΔLST, population and POI distributions cannot be reconciled by a single rule or vintage. The report names no run identifier that would bind any table to any output, so no central quantity can be recomputed as described.

### W3: Tables 5.2 and 5.3 contradict each other independently of the repository
**Severity**: Major
**Evidence Anchor**: table: Table 5.2 against Table 5.3, means of A_fp,res/Pop, f_veg and ΔLST
**Confidence**: 5 — arithmetic on reported values only
Cell-count weighting of the Table 5.3 stratum means with N = 860, 926 and 7,559 must return the Table 5.2 means. It gives 43.44 against 39.81 for footprint per capita, 0.438 against 0.418 for NDVI, and +0.09 K against +0.42 K for ΔLST. Separately, 6,334,180 / 692.81 = 9,143 persons/km², but the table prints 6,840; the other two strata reproduce. The Table 5.3 row labelled Mean for footprint per capita is also not a cell mean: 13.00 reproduces as the population-weighted aggregate of the Table 5.4 municipalities, whereas Table 5.2 reports a cell mean. In the Kabupaten stratum the two estimands differ by a factor of 1.76 in the outputs (33.24 against 18.84).

### W4: The ΔLST table cannot arise from the stated baseline, or from the implemented one
**Severity**: Major
**Evidence Anchor**: text: §2.2 "calculated as the 10th percentile LST across all vegetated peri-urban cells"
**Confidence**: 5 — logical implication plus recomputation
A 10th-percentile baseline over cool vegetated cells makes most residential anomalies positive and large. Table 5.2 instead reports a median of +0.13 K and P10 of −2.11 K, which would place half of all residential cells at or below the coolest decile of vegetated rural land. The implemented baseline is the median (305.45 K), giving a median anomaly of +5.85 K; the P10 of the same set is 299.01 K, which would give roughly +12.3 K. Neither reproduces the report. The reported minimum (−6.42 K) also hides a pipeline minimum of −36.48 K, which is implausible as a thermal anomaly and points to residual cloud or composite contamination.

### W5: Footprint per capita does not remove dasymetric dependence; it relocates it
**Severity**: Major
**Evidence Anchor**: text: §6.2 "successfully eliminates this dasymetric feedback loop"
**Confidence**: 4 — exact log identity on pipeline layers; allocation weights inferred from the data and the GHSL description
The denominator is still GHS-POP. In these data, rank correlation between population and GHS-BUILT-V residential volume is 0.985 and with GHS-BUILT-S it is 0.970, so population behaves as modelled volume times a near-constant. Exact decomposition: log(FP/Pop) = log(FP/S) − log(V/S) + log(V/Pop). The covariance shares of Var[log(FP/Pop)] are 67.9% for the Overture net footprint to GHS-S ratio, 32.4% for inverse GHS modelled height, and −0.2% for GHS volume per person (9,260 cells). Footprint per capita therefore varies because two building products disagree and because of GHSL's height model, not because of any demographic information. The cancellation is replaced by a ratio of two building datasets. Removing endogeneity requires a denominator independent of built-form covariates, such as kelurahan or desa census counts analysed at that support (Leyk et al., 2019, on fitness for use of gridded population).

### W6: Ground footprint per capita is neither model-free nor a measure of living space
**Severity**: Major
**Evidence Anchor**: text: §4.1 "provides an empirical, model-free proxy for ground crowding"
**Confidence**: 5 — algebraic identity and direct computation
Both terms are model outputs: an ML-derived conflated footprint layer and a dasymetric population grid. Further, FP/Pop = lambda × A / Pop identically (maximum relative error 3e−16 in the outputs), so the indicator is lambda divided by population density. Its log variance is accounted for almost entirely by log density (covariance share 1.00, lambda −0.00). This is a re-expression of inverse density, which §4.1 rejects as conflating vertical capacity with horizontal crowding. A high-rise with generous flats scores as severely overcrowded, which is the reverse of the stated polarity. Rank correlation with R_space is −0.03, so the two are not interchangeable measures of one construct.

### W7: The headline sub-5 m² conditions are largely an artefact of the non-residential filter
**Severity**: Major
**Evidence Anchor**: text: §6.2 "conditions in Tambora and Penjaringan"
**Confidence**: 4 — cell-level inspection; Tambora and Penjaringan located by approximate bounding boxes
Of 338 residential cells under 5 m² per person, the median cell had 97.5% of its footprint removed as non-residential, and those cells' median gross footprint is 38.4 m² per person; only 27 cells fall under 5 m² on gross footprint. Rank correlation of FP/cap with removed share is −0.60. In an approximate Tambora box (11 cells) FP/cap runs 5.76 to 14.98. In an approximate Penjaringan box (19 cells) the values under 5 are 0.00, 0.075 and 4.03, with 100%, 99.8% and 89.3% of footprint removed. No cell shows the claimed 2.8 to 3.1 m² by any defensible reading. Those figures are, in the report's own Table 5.4, municipal fifth percentiles, not Tambora or Penjaringan measurements. Cells with zero net footprint and non-trivial population should be treated as classification failures and not as extreme overcrowding.

### W8: R_space has two incompatible definitions and an impossible range
**Severity**: Major
**Evidence Anchor**: text: §6.2 "approaches a smoothed constant"
**Confidence**: 5 — internal comparison and recomputation
Section 2.2 defines R_space from footprint area times floors derived from building heights. Section 6.2 derives the artefact from GHS volume over GHS-POP. Only the second has a numerator sharing the dasymetric weight, so the cancellation argument does not apply to the §2.2 definition. The stated constant of 18 to 22 m² also conflicts with Table 5.2 (median 57.18, IQR 56.80) and with the outputs (median 57.18, IQR 8.19). The value 20.31 is the distribution minimum, not its centre.

### W9: MAUP is named but not tested
**Severity**: Major
**Evidence Anchor**: text: §6.4 "potentially underestimating the severity of localized deprivation"
**Confidence**: 5 — direct analysis
No result is shown at another resolution or zoning, although the data permit it. For lambda, 72.9% of variance among resolution 9 cells (10.5 ha) lies between resolution 8 parents (64% in a central Jakarta box), falling to 51.6% at resolution 10 (41.5% in the box; caveat in the scope note). Within-parent standard deviation is 0.049 at resolution 9. Of 515 resolution 9 cells with lambda at or above 0.40, 25.6% sit in parents under 0.30. Going coarser, the P5 of footprint per capita moves from 7.46 to 9.82 to 10.99 across resolutions 8, 7 and 6, and the zero share of slope falls from 59.9% to 36.2% to 19.9%. Rank correlations are comparatively stable (lambda and ΔLST 0.63, 0.65, 0.67). The verdict is that resolution 8 is defensible for neighbourhood-scale screening and for pairwise association, and it is not defensible for the 2 to 10 ha kampung pockets invoked in §6.4. Zoning effects (Fotheringham and Wong, 1991) need separate testing, for example with shifted H3 aggregation or census-unit overlays.

### W10: Cell-level statistics are read as statements about named settlements and residents
**Severity**: Major
**Evidence Anchor**: text: §5.4 "In the densest informal kampungs of Jakarta Barat"
**Confidence**: 4 — location check plus inference-level reasoning
The maximum lambda of 48.2% is at cell 888c12b6e5fffff in Jakarta Utara with FP/cap 26.39 m², whereas the report places it in Jakarta Barat and pairs it with 2.92 m². Maximum lambda and the low-footprint tail are different cells in different places, so a single kampung profile cannot be composed from them. Attaching 74 ha means to household deprivation standards is an ecological inference (Robinson, 1950), and no cross-level evidence is offered. Exposure context is likewise uncertain at this support (Kwan, 2012).

### W11: Zero-inflation and right skew are unaddressed in the report, and the pipeline treatment is partial
**Severity**: Major
**Evidence Anchor**: table: Table 5.2, rows A_amenity and S>15
**Confidence**: 5 — direct computation
Amenity has 21.4% exact zeros holding 4.4% of residents; none result from network snapping (no cell is beyond the cutoff). Skew is 4.84 raw and 0.57 after log1p. Slope has 59.9% exact zeros holding 73% of residents, skew 3.57, and no transform. Its scaled standard deviation is 0.103, with 59.9% of cells at exactly 1.0. Zeros in these two channels are of different kinds: amenity zeros combine real absence and data incompleteness, and slope zeros are a threshold artefact whose share depends on aggregation. Min-max scaling with a squared-error reconstruction leaves the model to spend capacity on a spike. A two-part representation should replace this: a presence indicator plus a conditional magnitude (Cragg, 1971), or a zero-inflated count likelihood for amenities (Lambert, 1992; decoder form in Lopez et al., 2018). Slope should be recomputed for built-up pixels only, as exposure, or be kept out of the embedding and used as a post hoc overlay. Slope correlates at +0.60 with NDVI and only −0.28 with lambda, so it currently encodes hilly vegetated land more than settlement hazard.

### W12: Spatial dependence is not quantified, and N = 9,345 cannot serve as the inferential sample
**Severity**: Major
**Evidence Anchor**: absence: §5 and §6 — expected Moran's I, effective sample size or a spatial validation design; checked §2.1, §5.2, §5.3, §5.4, §6.1 to §6.6 and §7.1
**Confidence**: 4 — permutation tests are exact to resolution; effective sizes are approximate
Global Moran's I on first-ring contiguity is 0.95 (R_space), 0.93 (density), 0.90 (amenity), 0.84 (lambda), 0.83 (ΔLST), 0.79 (NDVI), 0.63 (FP/cap), 0.49 (slope) and 0.38 (compactness); the maximum among 199 permutations is 0.03. Clifford, Richardson and Hémon (1989) effective sample sizes for channel pairs are 23 to 51 with lags to 120 km and 85 to 147 with lags to 10 km (Dutilleul, 1993, gives the related test). A catchment of 1,000 m on a lattice spaced about 937 m overlaps with its neighbours, so amenity autocorrelation is partly built in. Representation learning needs spatially blocked hold-out (Roberts et al., 2017; Ploton et al., 2020), and any later local cluster statistics need multiplicity control (Anselin, 1995).

### W13: The claimed independence from demography is contradicted by the correlation structure
**Severity**: Major
**Evidence Anchor**: text: §4.1 "Independence from Census Demography"
**Confidence**: 4 — computed on scaled and raw channels
Rank correlation of lambda with density is 0.87 and amenity with density is 0.82. The first principal component holds 52% of variance on the implemented scaled matrix and 56% on the stated vector. Variance inflation is not disqualifying (maximum 4.12 on the stated vector; adding log density yields 9.36 for density and 6.91 for lambda). The issue is thus one dominant density and urbanness factor and the absence of any reported collinearity evidence, not an inversion problem. Lambda, FP per capita and density have two degrees of freedom among three by identity (W6).

### W14: Normalisation, weighting and aggregation are unspecified and unexamined
**Severity**: Major
**Evidence Anchor**: absence: §2.2 and §5 — expected transforms, scaling bounds, weights and a robustness analysis for the composite inputs; checked §1, §2.1, §2.2, §4.1, §6 and §7.1
**Confidence**: 5 — manuscript search and config inspection
The manuscript stops at raw values, while the project's frozen benchmarks define what the model receives. In the outputs, 74.4% of channel 1 and 59.9% of terrain safety are clipped at the upper bound, compactness has a scaled standard deviation of 0.027, lambda occupies 0.433 to 1.0 under its 0.85 bound, and three bounds are still labelled provisional. These choices set each channel's influence and need a global sensitivity analysis (Saisana et al., 2005).

### W15: Missingness is undisclosed and is not random
**Severity**: Major
**Evidence Anchor**: absence: §5.2 to §5.4 — expected counts and a rule for cells with no LST or compactness; checked the header block, §2.1, §5.2, §5.3, §5.4 and §6
**Confidence**: 5 — direct computation
The modelled universe is 8,375, not 9,345: 894 residential cells (9.6%) have no LST. The rate is 34.2% in Jakarta Utara and 32.9% in Jakarta Barat. Excluded cells are denser (median 3,818 against 2,185 per km²) and have lower footprint per capita (16.4 against 25.3). Listwise exclusion therefore removes a portion of the population of interest and creates holes in the graph. The report's reported means do not state their denominator.

### W16: A named ground-truth benchmark has no reported comparison
**Severity**: Major
**Evidence Anchor**: text: §3 "Ground-Truth Floor Space per Capita Benchmark"
**Confidence**: 4 — manuscript search and project QA file
Susenas appears in the data table but in no result. The project QA holds a comparison for the modelled floor area: ratio mean 1.37, DKI municipalities 1.65 to 2.11, Spearman −0.21 over 16 units with DKI values repeated. Those units are few and not independent, so it is weak evidence either way, but its absence means no external validity is shown for the indicator central to the report.

### W17: The amenity definition is not the implemented one, and the origin is a single centroid
**Severity**: Major
**Evidence Anchor**: text: §2.2 "essential urban POIs reachable within a 15-minute walk"
**Confidence**: 5 — code, config and provenance inspection
The text gives OSM essentials at 1,125 m. The layer uses 1,000 m (provenance `cutoff_m`), Overture Places, and 173,820 points including restaurants, ATMs, banks and places of worship. A single centroid origin is up to about 530 m from a cell vertex, more than half of the walking budget, so within-cell access varies strongly on this indicator alone. Population-weighted origins from finer cells should replace it, and the essential subset should be reported separately.

### W18: Stated hexagon geometry is internally impossible
**Severity**: Minor
**Evidence Anchor**: text: §2.1 "Hexagon Edge Length"
**Confidence**: 5 — geometry
A regular hexagon of edge 461.4 m has area 0.553 km², not 0.7373 km². Centroid spacing is √3 times the edge (799 m), not two times the edge (922.7 m). The H3 average edge is 531.4 m.

### W19: The residential filter stated cannot yield the reported N
**Severity**: Minor
**Evidence Anchor**: equation: §2.1 residential filter Pop_i ≥ 50 AND A_bldg,res,i > 0
**Confidence**: 5 — recomputation
The stated rule selects 10,977 cells. The pipeline uses density at or above 300 per km² and building count at least 1, giving 9,345. Mask sensitivity (10,308; 9,345; 5,483) exists in the project and should be reported.

### W20: Vegetation is named and bounded as a cover fraction but computed as mean NDVI
**Severity**: Minor
**Evidence Anchor**: table: Section 1 indicator inventory, row 5 (Vegetation Cover Fraction)
**Confidence**: 5 — definition check
Mean NDVI has a negative range, stated in Table 5.2, so the unit [0, 1] and the name are wrong. The FVC alternative needs clipping to [0, 1] and is unused.

### W21: The fringe share is reported inconsistently
**Severity**: Minor
**Evidence Anchor**: text: Executive Summary "peri-urban/rural cells of Kabupaten Bogor"
**Confidence**: 5 — arithmetic
The Executive Summary uses 83.8%, §5.1 uses 80.9%, and 7,559 / 9,345 = 80.9%. The Kabupaten stratum also includes 870 cells outside the boundary file and 242 Kota Tangerang cells.

### W22: Plan area is defined by intersection but computed from eave-corrected centroid-assigned walls
**Severity**: Minor
**Evidence Anchor**: equation: §2.2 Indicator 1, numerator Area(B_k ∩ H_i)
**Confidence**: 5 — code inspection and computation
The eave correction removes about 17.4% of footprint area (wall to roof ratio 0.826) and is undisclosed. It does not vary strongly by density (0.806 to 0.826 at median), so I do not claim differential bias. It does change the benchmark comparison: on the stated definition, 21.88% would be about 26%.

### W23: Slope statement for DKI is contradicted, and the DEM is not bare earth
**Severity**: Minor
**Evidence Anchor**: text: §6.5 "across all of DKI Jakarta"
**Confidence**: 4 — outputs and asset identifier
The outputs show a DKI mean of 0.2% and maximum of 9.5%. The asset is GLO-30, a surface model, so positive values on the alluvial plain plausibly reflect buildings and canopy. FABDEM is absent from the code.

### W24: Municipal lambda and footprint per capita do not satisfy their identity
**Severity**: Minor
**Evidence Anchor**: table: Table 5.4, columns Aggregate lambda and Footprint/Capita
**Confidence**: 4 — arithmetic with mean cell area 0.7493 km²
Footprint per capita times population over cell area gives 25.4% for Barat (reported 28.12%) and 25.1% for Pusat (reported 23.51%), though the provincial total reconciles (S3).

### W25: The overcrowding threshold differs between text and benchmark file
**Severity**: Minor
**Evidence Anchor**: text: §4.1 "if living area drops below"
**Confidence**: 4 — manuscript and config; the source standard is left to the domain seat
The text uses 5 m² and `benchmarks_v1.yaml` uses 9 m². Either way the threshold refers to interior area, so comparing it with a roof-plan ratio is a category error.

## Arithmetic Receipts

### AR1
procedure_id: grim
evidence_anchor: table: Table 5.2, row A_amenity, column Mean
reported_inputs: mean 29.4; N 9,345 cells; integer count scale (Count of POIs); one decimal place
assumptions: unweighted cell mean over the Table 5.2 universe of 9,345 integer counts; granularity one count; precision as printed, one decimal
derivation: 29.4 times 9345 equals 274743 exactly, an integer total, so the mean is attainable and every rounding convention gives the same verdict
derived_value_or_range: 274743 divided by 9345 equals 29.4 exactly
rounding_interval: [29.35, 29.45)
nearest_achievable: 274742/9345 = 29.39989 and 274744/9345 = 29.40011
comparison_rule: reported mean is consistent if an integer total divided by N falls in the rounding interval; with N above 10 raised to the precision the procedure has almost no power to detect error
status: consistent
