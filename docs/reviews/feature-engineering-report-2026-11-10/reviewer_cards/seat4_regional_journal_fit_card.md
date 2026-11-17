contract_role: eic

## Dimension Scores

### D1: methodology_rigor

score: not_assessed

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: not_assessed

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: block
trigger: "text and exhibits report conflicting values for the same quantity"

### D6: venue_fit_and_contribution

score: block
trigger: "A contribution is asserted but not demonstrated, for example no comparison with any established index or baseline method"
block_class: repairable

## Review Body

No target venue is bound (`criteria_binding_unavailable`). Fit is judged only against the general readership of urban analytics and urban remote sensing, and nothing below certifies alignment with a named outlet. Repository evidence is weighed as evidence about what the manuscript claims to describe. Scores cover only D5 and D6.

Overall signal: Major Revision. The contribution is repairable within the design, so the D6 block is repairable rather than fatal. The manuscript is not yet a research article.

### S1: Stratified reporting of a heterogeneous study area

**Evidence Anchor**: text: §5.1 "Evaluating the dataset as a single unstratified distribution produces misleading results"

Reporting by administrative tier is the right instinct for an extended metropolitan region. It keeps the agrarian and industrial periphery from dominating the summary statistics.

### S2: Globally available data stack as a transfer premise

**Evidence Anchor**: table: §3 dataset table, column "Global Open Access?"

Building an index on openly available global layers is a real attraction for data-poor Southeast Asian municipalities, and it is the strongest basis for a later comparative contribution.

### S3: Candid limitations section

**Evidence Anchor**: text: §6 "this section documents the six primary methodological uncertainties"

Naming the dasymetric, regularisation, areal-unit and volunteered-data problems is more open than most indicator papers. The defect lies in how they are resolved, not in their being raised.

### S4: Useful separation of building coverage from imperviousness

**Evidence Anchor**: text: §6.1 "accounts *strictly* for building footprint polygons"

The distinction is routinely blurred in policy discussion of Jakarta and is worth stating clearly, although it is a clarification and not a finding.

### W1: Contribution is asserted but not demonstrated

**Severity**: Critical
**Evidence Anchor**: text: Executive Summary "A core contribution of this report is resolving the"
**Confidence**: 4 — editorial judgement against the slum-mapping, deprivation-mapping and wealth-mapping literatures

The two named contributions are a definitional distinction and the act of stratifying. Stewart and Oke (2012) already separate building surface fraction from impervious surface fraction, and stratification is routine. No baseline is compared: not GHSL settlement classes, not the Relative Wealth Index (Chi et al., 2022), not the morphological slum literature (Taubenböck & Kraff, 2014; Wurm & Taubenböck, 2018), not IDEAMAPS (Thomson et al., 2020), and not Indonesian registers such as the BPS DKI RW Kumuh evaluations. The report stops before any index or model output, so there is no added information to assess and no decision or population outcome connected to the features. Remedy: state a research question, show what the feature set adds beyond population density and a named baseline, and validate against an independent deprivation outcome.

### W2: The manuscript does not describe the analysis held in the repository

**Severity**: Critical
**Evidence Anchor**: table: §3 Primary & Secondary Datasets, rows for Google Open Buildings v3, GHS-BUILT-C, FABDEM and OpenStreetMap
**Confidence**: 5 — repository audit, with ingestion and configuration files opened directly

I weighed whether this is only a stale draft. It cannot be treated so, because the differences are in the data sources and the outcome definition and not only in decimals. The repository uses Overture buildings and Overture Places rather than Google Open Buildings and OSM POIs, has no GHS-BUILT-C mask, has no FABDEM, uses a 1,000 m cutoff rather than 1,125 m, and keeps GHS-volume-based living space as the matrix channel that §6.2 says was replaced. Reported ΔLST for DKI is +2.78 K against +10.90 K recomputed, so even its magnitude cannot be interpreted. Whichever version is intended, a reader cannot tell what was done. Remedy: regenerate every exhibit from one frozen pipeline and rewrite §2, §3 and §5 from it.

### W3: The headline severe-crowding value is produced by the non-residential filter

**Severity**: Major
**Evidence Anchor**: text: §6.2 "accurately revealing the $2.8\text{--}3.1\text{ m}^2/\text{person}$ conditions in Tambora and Penjaringan"
**Confidence**: 5 — recomputed from `h3_features_raw.parquet` around named settlements

If λ of 48.2% and 2.92 m²/person describe one cell, as §5.4 implies, density would be about 165,000/km², or about 122,000 people in one cell. The largest cell population in the repository is 32,059. In the 11 cells around Tambora, net footprint per capita is 9.9 to 15.0 m². Kalibaru cells are 18.5 to 20.5 m², although §5.4 names Kalibaru among the most acute cases. The DKI tail is a classification effect: 68 DKI cells have net footprint below 5 m²/person, only 3 do before the filter, and those 68 had a median 93.6% of footprint removed, with median λ of 0.017 and median density of 9,705/km². DKI P5 is 2.89 net and 11.2 gross. Penjaringan's low cells (4.03 and 5.65 m²) had 89% and 80% removed and are 37.7 and 28.5 m² gross. Remedy: withdraw the settlement claims and validate the filter against mapped non-residential land.

### W4: Susenas is listed as ground truth but no comparison is reported, and the existing one does not validate

**Severity**: Major
**Evidence Anchor**: text: §3 "Ground-Truth Floor Space per Capita Benchmark"
**Confidence**: 4 — read `stage3_qa.json`, the benchmark CSV and the validation module; construct reasoning from survey practice

The manuscript gives no Susenas value. §7.1 also calls the 13.0 m² figure floor space, though it is ground footprint. DKI footprint per capita (12.97) is close to the Susenas figure (12.27), but that agreement is between different constructs and should not be read as validation. Footprint ignores storeys and survey area is reported dwelling floor area. The repository's modelled floor area runs 1.65 to 2.11 times Susenas in DKI municipalities and has a rank correlation of −0.21 across units. Across the 9 non-DKI units I compared, footprint per capita has a rank correlation of −0.08 with Susenas, with ratios of 0.73 to 1.29 across all 14 compared units. The benchmark column is also derived: it equals median dwelling area divided by mean household size in every row (largest difference 0.005). DKI is one provincial value repeated five times. The validation code maps the 181 km² "Tangerang" polygon, which is Kota Tangerang by area, to Kabupaten Tangerang. Remedy: report the comparison, separate footprint from floor area, use microdata or kabupaten-kota tabulations of per-capita area, and state the threshold mismatch.

### W5: The coverage artefact is named but never tested, and is diagnosed for the wrong dataset

**Severity**: Major
**Evidence Anchor**: text: §6.6 "Rural and low-income areas have lower mapping completeness"
**Confidence**: 4 — recomputed within density bins; attribution between real and coverage effects remains open

§6.6 cites a road-completeness paper (Barrington-Leigh & Millard-Ball, 2017) for a POI claim, and the POIs in the repository come from Overture Places, whose bias is commercial and platform listing rather than volunteer mapping. The contrast of 126 against 2 is largely density composition. Within density bins, DKI and Kabupaten medians are similar below 10,000/km² (4 v 3; 6 v 7; 25 v 16), while DKI retains a 2.4 to 2.9 fold excess at 10,000 to 25,000/km² (90.5 v 31; 154 v 63.5). Network snapping does not explain zeros (0.0 to 0.1% of cells over 500 m). The residual cannot be divided between real provision and digital visibility using anything in the manuscript. Overture's `sources` field is dropped at ingestion and confidence is hard-coded at 0.85, so source composition cannot be examined for buildings, where a similar gradient is plausible (Herfort et al., 2023). Remedy: validate against Podes, the Ministry of Health facility register and Dapodik school records by kecamatan or desa, and report completeness by stratum.

### W6: The Metro Manila benchmark has no verifiable source

**Severity**: Major
**Evidence Anchor**: text: §6.1 "This matches observations in Metro Manila"
**Confidence**: 5 — Crossref resolution from the audit; subject-matter reading of the cited title

The sole comparative figure rests on a DOI that resolves to an unrelated paper, and the cited title concerns global land susceptibility to urbanisation, which would not report block-scale plan area for Manila. No Bangkok, Ho Chi Minh City or Surabaya evidence appears, although peer alignment is stated in the Executive Summary. Remedy: compute λp with the same pipeline for at least one peer city or cite verifiable measurements.

### W7: Alignment with LCZ 3 is contradicted by the reported values

**Severity**: Major
**Evidence Anchor**: text: §6.1 "grid-level $\lambda_p$ naturally caps at"
**Confidence**: 4 — LCZ class ranges from Stewart and Oke (2012)

A gross DKI fraction of 28.75% lies outside the LCZ 3 building-surface range of 40 to 70% and inside the LCZ 6 open low-rise range of 20 to 40%. The aggregation cap of 40 to 48% is attributed to LCZ literature without a source and makes the claim hard to falsify. LCZ 7 (lightweight low-rise) is the class closest to the kampung descriptions and is not discussed. Remedy: map LCZ-comparable fractions at block scale, or drop the alignment claim.

### W8: Transferability is untested and several definitions are structurally Jakarta-specific

**Severity**: Major
**Evidence Anchor**: absence: Sections 1 to 6 — expected a second-city application or a reasoned transfer analysis of the feature definitions; checked Executive Summary, Section 4.1, Section 5, Section 6 and the dataset table
**Confidence**: 4 — comparative knowledge of Southeast Asian housing forms; arithmetic on footprint geometry

Definitions need structural recalibration. A formal 4 × 20 m Vietnamese tube house has C = 0.44, a 4 × 18 m ruko 0.47, so the §6.3 replacement (C below 0.55) labels planned narrow-plot housing as irregular. Footprint per capita misreads Bangkok and Ho Chi Minh City row housing of three to five storeys as crowding. Slope is close to null in deltaic Bangkok and Ho Chi Minh City. The residential filter depends on local OSM land-use coverage and on heuristics tuned for Indonesian warehouses. GHS-POP quality depends on census unit size (Leyk et al., 2019). Amenity vocabularies do not cross without change, as ADR 0004 itself concedes by making them per-region. Remedy: apply the unchanged pipeline to a peer city with reference data, separate universal from locally calibrated parameters, and report what breaks.

### W9: The core-periphery strata do not match their stated composition

**Severity**: Major
**Evidence Anchor**: text: §5.1 "representing mature urban satellite cities (Kota Bogor, Depok, Tangerang, Tangerang Selatan, Bekasi)"
**Confidence**: 5 — reproduced stratum membership from the boundary file

The reported counts are reproduced only when the 242 Kota Tangerang cells sit in the Kabupaten stratum. A further 870 cells (1.27 M people) lie outside every polygon, and Serang and Bandung Barat are included but unlisted. "Jabodetabek" here also includes Karawang and Lebak, which are outside the usual definition. The stratified contrast is the report's main empirical message, and the middle stratum is mis-specified. Remedy: define the study area and strata from official boundaries, with a sensitivity check.

### W10: Population denominators are not reconciled with official counts

**Severity**: Major
**Evidence Anchor**: table: §5.3 row "2023 Population"
**Confidence**: 3 — official figures taken from secondary web sources and should be confirmed against BPS tables

Report totals (Kota 6.33 M) differ from repository totals (9.10 M). The repository gives Kota Bekasi 3.30 M against a BPS-based figure of about 2.63 M, and Depok 2.90 M against about 2.17 M, while DKI is close to official counts. At the other extreme, peak cells around Tambora reach 36,000/km², whereas the whole kecamatan is reported near 49,800/km². GHS-POP may therefore both compress peaks and over-allocate to satellites, which moves every per-capita contrast across strata. Remedy: reconcile against kecamatan and desa census counts and show sensitivity to population source.

### W11: "Essential" amenities are not what is counted, and counts ignore demand

**Severity**: Major
**Evidence Anchor**: text: §2.2 "Clinics, puskesmas, pharmacies, hospitals"
**Confidence**: 5 — configuration and ADR 0004 read directly

ADR 0004 deliberately counts everyday destinations, including restaurants, cafes, ATMs and places of worship. The manuscript presents an essential-services measure and interprets low values as "Service Desert". Raw counts also ignore population competition, despite the availability literature (Luo & Qi, 2009). Published amenity counts for Tondo or Baseco do not exist in a comparable form, so the manuscript's comparison cannot be made without running the same procedure there. Remedy: report formal-service and everyday counts separately, add a per-capita or floating-catchment form, and run a matched Manila test.

### W12: Hazard dimension omits the region's dominant physical hazards

**Severity**: Major
**Evidence Anchor**: text: §1 "Geomorphological hazard exposure (landslide vulnerability, unbuildable steep terrain)"
**Confidence**: 4 — regional hazard literature

Flooding and land subsidence dominate physical risk for low-income north Jakarta (Abidin et al., 2011), and the same holds for riverine Metro Manila (Porio, 2011). A slope indicator that is effectively zero for most of the core cannot represent hazard disparity between core and periphery, and it biases the hazard channel toward the upland fringe. Remedy: add flood and subsidence layers or narrow the construct to slope hazard.

### W13: The document is a pre-modelling technical audit, not a research article

**Severity**: Major
**Evidence Anchor**: text: Header "Feature Engineering & Pre-Modeling Methodological Audit"
**Confidence**: 4 — editorial judgement from the document's structure

There is no research question, hypotheses or validation outcome, and a review protocol is embedded in the body as §7. Field-general reading: readers in urban analytics and planning expect a question and an evaluated result; the remote-sensing readership expects a new retrieval or validated measurement advance, which is not present. Remedy: remove §7, integrate this with the modelling stage or recast it as a validated data-descriptor paper.

### W14: Text and exhibits conflict on basic quantities

**Severity**: Major
**Evidence Anchor**: text: Executive Summary "$83.8\%$ peri-urban/rural cells"
**Confidence**: 5 — arithmetic on the manuscript's own numbers

The Executive Summary gives 83.8% and §5.1 gives 80.9% for the same share. The Kota density of 6,840/km² conflicts with the table's own population and area (9,143/km²). A cell of about 0.737 km² cannot have the reported 461.4 m edge, since a regular hexagon of that area has an edge near 532 m. §5.4 says footprint falls to 2.92 m² in Jakarta Barat while listing a lower 2.84 m² for Jakarta Utara. Remedy: rebuild all numbers from a single source and check text against tables.

### W15: Reference list is unreliable

**Severity**: Major
**Evidence Anchor**: text: References "Sliuzas, R., Mboup, G., & de Sherbinin, A. (2010)"
**Confidence**: 5 — Crossref results in the audit

At least nine cited DOIs fail or resolve to unrelated papers, and three cited works could not be found by title. These references carry the informal-settlement and comparative arguments, so the regional grounding cannot be relied on. Remedy: rebuild the bibliography from primary sources and read each work before citing it.

### W16: Informal-settlement labels outrun what the indicators can identify

**Severity**: Minor
**Evidence Anchor**: text: §1 "Lower $C$ $\to$ Organic Informal Slum Morphology"
**Confidence**: 4 — manuscript §6.3 and recomputed compactness spread

§6.3 concedes compactness does not distinguish kampungs from formal subdivisions, and yet the indicator table keeps the slum interpretation. Kampung should not be treated as a synonym for slum, as many kampungs are consolidated (Tunas & Peresthu, 2010). Remedy: describe the measure in morphological terms only.

### W17: Crowding threshold ignores the Indonesian standard

**Severity**: Minor
**Evidence Anchor**: text: §4.1 "living area drops below $5.0\text{ m}^2/\text{person}$"
**Confidence**: 4 — the repository's validation module uses 7.2 m²

The analysis uses 7.2 m²/capita in code and 5.0 m² in text. Neither applies directly to ground footprint per cell. Remedy: state one threshold and its scope.

### W18: No maps in a study of spatial disparity

**Severity**: Minor
**Evidence Anchor**: absence: Section 5 — expected at least one map of indicators or strata with legend and scale; checked all sections, the ASCII diagrams and the exhibits
**Confidence**: 5 — direct inspection

Remedy: add maps of each indicator, the strata, and the missing-data pattern.
