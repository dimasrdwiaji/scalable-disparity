contract_role: domain

## Dimension Scores

### D1: methodology_rigor

score: not_assessed

### D2: domain_accuracy

score: block
block_class: repairable
trigger: "a key cited source attributed a finding, class definition or threshold it does not contain"

The report's named core contribution attaches to Stewart & Oke (2012) a scale-dependent ceiling and a micro-block scale that the source does not contain, and places the result in a class whose published range the result does not reach. The Manila benchmark rests on a reference that does not exist as cited. The block is repairable, not fatal: plan area fraction itself is a sound indicator, the pipeline's roof-based coverage agrees closely with an independent product (DKI 34.4% against 36.3% for GHS-BUILT-S), and the benchmark claims can be withdrawn or re-derived without re-specifying the concept.

### D3: argumentative_coherence

score: not_assessed

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: not_assessed

### D6: venue_fit_and_contribution

score: not_assessed

## Review Body

Scope of checks. I read the Local Climate Zone (LCZ) property table as reproduced with attribution in Abougendia et al. (2020, WIT Transactions, Table 1), and the key and the LCZ 1, 2, 3, 6 and 7 sheets of Stewart's (2011) zone datasheets. The publisher's page for Stewart & Oke (2012) refused automated access, so I did not read the journal's body text; statements about what that paper omits are limited to its table and the datasheets. I consulted Sirko et al. (arXiv 2107.12283) through an automated extraction of an HTML full-text rendering, not by reading it line by line. I could not open the full text of Kuffer et al. (2016). For Taubenböck & Kraff (2014), Taubenböck et al. (2018), Funo et al. (2002), Tipple (2005) and Kusno (2013), Crossref confirms the records, but I describe their content from prior knowledge and did not re-read them here. I recomputed morphology from `data/raw/buildings.parquet` and the 2026-11-09 feature store with read-only scripts in `work_domain`. Stratum figures below are for the 860 DKI cells, whose assignment reproduces the report's N.

Answers to the report's three Seat 2 questions are given in W1, W3 and W6 (question 1), W4 and W5 (question 2), and W7 and W8 (question 3).

### S1: Plan area and impervious cover are correctly separated in principle

**Evidence Anchor**: text: §6.1 "accounts *strictly* for building footprint polygons"
Treating building cover and paved cover as distinct quantities matches the LCZ scheme, which tabulates building surface fraction and impervious surface fraction separately. Readers who equate "built-up" with roof cover need this correction.

### S2: The DKI residential fraction is reproducible

**Evidence Anchor**: table: Table 5.3, row for the median residential plan area fraction, DKI column
The DKI median of 23.0%, P90 of 33.4% and aggregate of 21.88% reproduce exactly from the feature store. The quantity is computed as the code defines it; my objections concern what it is called and what it is compared with.

### S3: The compactness failure is reported openly

**Evidence Anchor**: text: §6.3 "The metric failed to distinguish informal kampungs from formal subdivisions."
An indicator that does not work is disclosed rather than buried. My recomputation agrees with the direction of this statement and shows the collapse is more severe than reported.

### W1: The LCZ 3 alignment and the 40-48% cap are not in the cited source and are contradicted by its table

**Severity**: Critical
**Evidence Anchor**: text: §6.1 "notes that while LCZ 3 (Compact Low-Rise) reaches"
**Confidence**: 4 - ranges read in an attributed table and the datasheets; journal body text not read; values recomputed from project data

The report says Stewart & Oke give 40-70% at a "micro-block scale" of 50-100 m and that aggregation to 74 ha "naturally caps" lambda at 40-48%. As reproduced, the LCZ definition is regions that "span hundreds of meters to several kilometres in horizontal scale". The 40-70% range for LCZ 3 is therefore a local-scale value, the same order of scale as a 74 ha hexagon, not a micro-block value that shrinks on aggregation. I found no 40-48% aggregate cap in the table or in the datasheets I read, and no scale qualifier on the 40-70% range there.

By the published ranges, the report's own numbers do not align with LCZ 3. LCZ 3 is 40-70% building surface fraction, LCZ 6 (open low-rise) is 20-40% and LCZ 7 (lightweight low-rise) is 60-90%. An aggregate of 21.88% or 28.75% sits in the LCZ 6 range. Only 2.3% of DKI cells reach 40% on the residential metric, and 60.8% fall in 20-40%. LCZ 7, whose datasheet names informal settlements and squatter settlements as its function, is never mentioned. Building fraction alone does not assign an LCZ, so the defensible statement is weaker in both directions: the numbers are compatible with mostly open low-rise cover at this scale, with a compact minority.

The cap is also contradicted by the project's data. On the unfiltered roof-area basis, 31.2% of DKI cells exceed 40% and 8.4% exceed 48%, with a plausible maximum of 63.2%. The 48.2% peak is a result of the deductions described in W3, not a natural ceiling. The report calls this reconciliation a core contribution, so the error is at the centre of its claim.

### W2: The Metro Manila benchmark has no identifiable source

**Severity**: Major
**Evidence Anchor**: text: §6.1 "This matches observations in Metro Manila"
**Confidence**: 5 - Crossref record checked; title search run; real Estoque paper identified

The cell-wide 25-38% range is attributed to Estoque et al. (2017). The DOI resolves to an unrelated river-management paper and no paper with the cited title was found. The real Southeast Asian megacity paper by Estoque, Murayama and Myint (2017, Science of the Total Environment) studies land-surface temperature against landscape composition, and I would not expect it to report building plan area fraction. The second Manila entry, Estudillo et al. (2021), also resolves to an unrelated paper and is never cited in the text. I found no published cell-wide plan area fraction for Metro Manila in my searches, so the peer-megacity agreement in the Executive Summary has no evidential basis as written.

### W3: The reported lambda is not plan area fraction as the cited literature defines it

**Severity**: Major
**Evidence Anchor**: text: §2.2 "The ratio of the sum of residential building footprint planar areas intersecting cell"
**Confidence**: 5 - direct recomputation from building polygons and code

The LCZ scheme defines building surface fraction as the proportion of ground surface with building cover. The pipeline instead deducts an undisclosed 0.5 m eave strip and then a land-use filter. For DKI the sequence is 34.4% on roof area, 28.75% after the eave deduction, and 21.88% after the filter. GHS-BUILT-S, an independent product, gives 36.3% for the same cells, with a cell-level Spearman of 0.83 against roof area. The figure the report calls "gross" is therefore already reduced by about one sixth.

The deduction is not neutral. Wall-to-roof ratio ranges from 0.75 to 0.96 across DKI cells and rises with median building size (Spearman 0.45), so small-grain fabric loses proportionally more. It also strips the exterior perimeter of a merged terrace but not its party walls. An indicator meant to measure kampung packing is thus attenuated most where packing is finest.

Comparing a residential-only figure with LCZ ranges, which cover all buildings, is also unlike with unlike. Question 1 answer: 21.88% is a correct arithmetic output but not an accurate statement of Jakarta's building coverage, which is near 34-36% on a standard definition. The 48.2% is a filtered cell-average and neither a peak building coverage nor a kampung-scale value.

### W4: The GHS-BUILT-C residential mask is not in the pipeline, and no such mask could deliver "purely domestic" cover

**Severity**: Major
**Evidence Anchor**: text: §4.1 "Masking via GHS-BUILT-C ensures that building coverage measures purely domestic settlement density."
**Confidence**: 4 - code read directly; mixed-use estimate is a lower bound from point data

GHS-BUILT-C is absent from the code. Non-residential removal uses OSM land-use polygons and size and shape rules. Question 2 therefore cannot be answered as posed for the published numbers.

For the mask actually used, ruko are largely retained. A building in an OSM commercial or retail zone is kept when under 200 m², and most strip frontage has no such zone. Of the DKI footprints kept as residential, 14,602 (0.8% by count, 2.05% by area) contain a commercial Overture place point, and 95.1% of those lie outside any commercial or retail zone. This is a lower bound because place data are incomplete and many points sit on the street rather than the roof. The filter's removal share correlates with the GHS non-residential share across cells (Spearman 0.76) but exceeds it in DKI (23.9% against 14.7%).

A swap to GHS-BUILT-C would not settle the matter. The product assigns one dominant function per 10 m pixel from a 2018 composite, while a ruko is vertically mixed by design, with trade below and dwelling above (on the shophouse in Indonesia, see Kusno 2013), and kampung housing commonly contains home-based enterprise (Funo et al. 2002; Tipple 2005). Mixed use needs a partial weight validated against a labelled sample, not a binary mask.

### W5: The land-use filter removes house-sized buildings and manufactures the extreme crowding tail

**Severity**: Major
**Evidence Anchor**: text: §4.1 "provides an empirical, model-free proxy for ground crowding"
**Confidence**: 4 - recomputed from project data; zone labels not field-checked

Footprint per capita depends on GHS-POP and on the filter, so it is not model-free. In non-commercial OSM zones every building is removed regardless of size. In DKI that deletes 51,744 buildings under 200 m² (3.87 km²), including 24,173 in `industrial` zones and 11,996 in `military` zones, and the median building in an industrial zone is 71 m², almost the same as the 69 m² median of DKI buildings outside any zone. Military and workers' housing inside such polygons is residential.

The filter is uneven. In my hand-picked contrast, kampung cells lost a median 6% of footprint and planned-estate cells 52%, reflecting where OSM land-use is mapped. Penjaringan, the location the report highlights, lost 80%. Across all residential cells, 338 have footprint per capita below 5 m², 89% of roof area in those cells was removed by the zone rule, and 85 cells have net footprint of exactly zero while still being populated. The sub-5 m² tail is largely a filter effect, not observed overcrowding. Ground footprint per person is also not living area, and comparing it with a floor-area standard ignores storeys.

### W6: The kampung narrative for the extremes is contradicted by the data

**Severity**: Major
**Evidence Anchor**: text: §5.4 "In the densest informal kampungs of Jakarta Barat"
**Confidence**: 5 - cell-level recomputation; place-to-cell mapping approximate

The 48.2% maximum is in Jakarta Utara at (-6.120, 106.905), where footprint per capita is 26.4 m². Jakarta Barat's maximum is 45.1%. The cells I mapped to the named places give 14.9 m² for Tambora, 13.6 m² for Kali Anyar and 9.9 m² for Jembatan Besi, against the 2.92 m² the report states. The Jakarta Barat fifth percentile recomputes to 8.17 m². The claim in §6.2 that footprint per capita reveals 2.8-3.1 m² in Tambora and Penjaringan is not supported; the single Penjaringan cell at 5.65 m² had 80% of its footprint removed. These are cell averages over 74 ha, so they cannot show conditions in a 2-10 ha kampung pocket in either direction.

### W7: Irregular share below 0.55 is not a remedy for regularisation

**Severity**: Major
**Evidence Anchor**: text: §6.3 "which avoids vectorization artifacts"
**Confidence**: 5 - analytic derivation plus building-level recomputation

For a rectangle of aspect ratio r, Polsby-Popper is pi*r/(1+r)^2, which falls below 0.55 at r of about 3.4. The threshold therefore measures elongation, and it flags narrow terrace and ruko rows. Of the 81,363 retained DKI footprints below 0.55, 62% by count are plain quadrilaterals. In the same data 93.8% of retained DKI polygons are quadrilaterals, so regularisation is real and strong, and it acts on the input to any shape metric, not only on the mean.

Question 3 answer: building-level compactness is not salvageable and should be dropped as a channel. It should not be replaced by footprint count density, whose Spearman with the plan area fraction is 0.96, and 0.84 with population density, so it would duplicate an existing channel. Median footprint area is the better candidate: its Spearman is 0.04 with plan area fraction and -0.02 with population density, and in my contrast it nearly separated the two groups (kampung median 57 m², planned 117 m²; 9 and 8 hand-picked cells, illustrative only). Area coefficient of variation separated them poorly and I would treat it as secondary. Merged conjoined roofs bias grain upward in the densest fabric, so any replacement needs validation against a very-high-resolution sample. Arrangement measures (gaps, alley width, block structure; see momepy, Fleischmann 2019) are closer to the construct.

The reported statistics also do not describe the code. The pipeline uses an unweighted median with an IQR of 0.012, not an area-weighted mean with an IQR of 0.046.

### W8: The premise that informal footprints are geometrically tortuous lacks support

**Severity**: Major
**Evidence Anchor**: text: §4.1 "resulting in highly non-convex, tortuous polygon boundaries"
**Confidence**: 4 - morphological-slum literature known; two cited records checked by DOI

The citations offered do not carry this claim. Sliuzas et al. (2010) could not be found, and the Taubenböck DOI points to a soil-moisture paper. The real Arrival City paper (Taubenböck et al. 2018, Applied Geography) and the earlier Mumbai work (Taubenböck & Kraff 2014) characterise morphological slums chiefly through small building size, high density, low height and irregular arrangement. Those are properties of grain and pattern. The LCZ datasheets locate informality the same way: LCZ 3 buildings are tightly packed "often without discernable alignment", and LCZ 7 has a "compact (often formless) arrangement". Kampung houses are mostly rectilinear rooms on irregular plots, and the irregularity lies at parcel and alley scale (Funo et al. 2002). The data agree: kampung and planned contrast cells have median compactness 0.740 and 0.743, with overlapping ranges. The direction assigned to the indicator in §1 therefore lacks a demonstrated basis.

### W9: The regularisation mechanism is misattributed

**Severity**: Minor
**Evidence Anchor**: text: §6.3 "such as Mask R-CNN in Open Buildings v3"
**Confidence**: 4 - automated extraction of the paper's full-text rendering; abstract confirmed separately

Sirko et al. use a U-Net, cover Africa only, produce no heights, and describe a contouring step that gives angular shapes. They do not describe fitting minimum bounding rectangles; round shapes vectorised as rectangles appear as an error type. The arXiv number cited resolves to an astrophysics paper; the correct one is 2107.12283. The polygons here come from the conflated Overture layer, whose sources are not retained in the project's file, so per-source shape effects cannot be assessed. The observed regularisation stands, which is why this is Minor.

### W10: The 0.45-0.65 informal settlement range is unverified and scale-mismatched

**Severity**: Minor
**Evidence Anchor**: text: §4.1 "the informal settlement reaches"
**Confidence**: 3 - bibliographic record checked; full text not accessible to me

The cited DOI is the review "Slums from Space", with a different title and author list from the reference entry. I could not access its full text and do not assert the range is absent. The range is explicitly block-scale, whereas the indicator is measured over 74 ha. The high-rise range of 0.15-0.25 has no source.

### W11: Categorical land-cover classes are not impervious surface fraction

**Severity**: Minor
**Evidence Anchor**: text: §6.1 "Remote sensing land-cover classifications evaluate"
**Confidence**: 4 - established product definitions

ESA WorldCover and MODIS assign a categorical built-up class per pixel. The share of pixels in that class is not an impervious fraction, and it is partly a resolution effect. The 75-80% figure also carries no source. The contrast with roof cover is valid but it is not a paradox, and the mechanism should be stated correctly.

### W12: GHS epochs in the data table do not exist as stated

**Severity**: Minor
**Evidence Anchor**: text: §3 "2020 (Epoch 2023)"
**Confidence**: 5 - Earth Engine catalogue and project configuration checked

GHS-BUILT-C R2023A is a 2018 product. GHS-POP R2023A has five-yearly epochs; the configuration interpolates 2020 and 2025 to 2023, which is a derived estimate and not a released projection.

### W13: No physical-plausibility check on plan area fraction

**Severity**: Minor
**Evidence Anchor**: absence: §2.2 and §5 — expected a check that cell plan area fractions are physically possible; checked the plan area equation, Table 5.2, Table 5.3 and §6.1
**Confidence**: 5 - direct recomputation

Whole-building centroid assignment, in place of the stated intersection, allows values above 1. Cell 888c12b68dfffff has a gross roof fraction of 1.18, against 0.46 in GHS-BUILT-S, which suggests a very large or erroneous polygon. Cell area also includes water, which lowers Jakarta Utara values.

### Missing Key References

The works below are those this review relies on. Each was confirmed on Crossref, except Sirko et al., which was confirmed on arXiv.

~~~yaml suggested-references
- title: "Local Climate Zones for Urban Temperature Studies"
  authors: ["Stewart, I. D.", "Oke, T. R."]
  year: "2012"
  doi: "10.1175/BAMS-D-11-00019.1"
  arxiv_id: null
- title: "The physical face of slums: a structural comparison of slums in Mumbai, India, based on remotely sensed data"
  authors: ["Taubenböck, H.", "Kraff, N. J."]
  year: "2014"
  doi: "10.1007/s10901-013-9333-x"
  arxiv_id: null
- title: "The morphology of the Arrival City - A global categorization based on literature surveys and remotely sensed data"
  authors: ["Taubenböck, H.", "Kraff, N. J.", "Wurm, M."]
  year: "2018"
  doi: "10.1016/j.apgeog.2018.02.002"
  arxiv_id: null
- title: "Typology of Kampung Houses and Their Transformation Process"
  authors: ["Funo, S.", "Yamamoto, N.", "Silas, J."]
  year: "2002"
  doi: "10.3130/jaabe.1.2_193"
  arxiv_id: null
- title: "The Place of Home-based Enterprises in the Informal Sector"
  authors: ["Tipple, G."]
  year: "2005"
  doi: "10.1080/00420980500060178"
  arxiv_id: null
- title: "The Shophouse and the Chinese (in After the New Order)"
  authors: ["Kusno, A."]
  year: "2013"
  doi: "10.21313/hawaii/9780824837457.003.0002"
  arxiv_id: null
- title: "momepy: Urban Morphology Measuring Toolkit"
  authors: ["Fleischmann, M."]
  year: "2019"
  doi: "10.21105/joss.01807"
  arxiv_id: null
- title: "Global Building Morphology Indicators"
  authors: ["Biljecki, F.", "Chow, A."]
  year: "2022"
  doi: "10.1016/j.compenvurbsys.2022.101809"
  arxiv_id: null
- title: "A global map of local climate zones to support earth system modelling and urban-scale environmental science"
  authors: ["Demuzere, M.", "Kittner, J.", "Martilli, A.", "Mills, G."]
  year: "2022"
  doi: "10.5194/essd-14-3835-2022"
  arxiv_id: null
- title: "Effects of landscape composition and pattern on land surface temperature: An urban heat island study in the megacities of Southeast Asia"
  authors: ["Estoque, R. C.", "Murayama, Y.", "Myint, S. W."]
  year: "2017"
  doi: "10.1016/j.scitotenv.2016.10.195"
  arxiv_id: null
- title: "Continental-Scale Building Detection from High Resolution Satellite Imagery"
  authors: ["Sirko, W.", "Kashubin, S.", "Ritter, M."]
  year: "2021"
  doi: null
  arxiv_id: "2107.12283"
~~~
