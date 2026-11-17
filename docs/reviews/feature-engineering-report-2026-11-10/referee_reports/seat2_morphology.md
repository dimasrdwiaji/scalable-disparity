# Referee Report: Spatial Feature Engineering for Physical Disparity
**Reviewer Identity / Seat**: Urban Geography & Morphology
**Evaluation Date**: 2026-11-09
**Overall Recommendation**: Major Revision
---
### 1. Summary of Appraisal

The report asks the right morphological question: how much of a megacity's "built-up" land is actually roof. Plan area fraction is a sensible core indicator, and the DKI values reproduce exactly from the feature store. The benchmarking built around it does not hold. Stewart & Oke's LCZ 3 range is a local-scale value of 40-70%, and it contains neither a "micro-block" qualifier nor a 40-48% aggregate cap. The report's 21.88% and 28.75% fall in the range of open low-rise (LCZ 6), not compact low-rise. The Manila comparison cites a paper I could not find. The headline figure also differs from plan area fraction as the literature defines it: DKI coverage is 34.4% on roof area, close to the 36.3% from GHS-BUILT-S, before an undisclosed eave deduction and a land-use filter reduce it. The GHS-BUILT-C mask described in the text is not in the pipeline. The filter actually used retains most ruko while deleting tens of thousands of house-sized buildings, and it generates much of the extreme crowding tail. Building compactness cannot be salvaged, and the proposed irregular-share fix measures elongation. All of this can be repaired without abandoning the concept, but the benchmark claims must be withdrawn or re-derived before the indicator set is modelled.

### 2. Major Methodological Critiques (P0 / P1)

- **Point 1 (Conceptual Validity)**: *P0.* The claimed agreement with LCZ 3 is the report's stated core contribution, and it misreads the source. As reproduced with attribution in Abougendia et al. (2020, Table 1), Stewart & Oke (2012) define LCZs as regions spanning hundreds of metres to several kilometres, with building surface fraction of 40-70% for LCZ 3, 20-40% for LCZ 6 and 60-90% for LCZ 7. I read that reproduction and Stewart's (2011) datasheets for LCZ 3, 6 and 7, which give the same ranges. The journal page refused automated access, so I did not read the paper's body text, and my statement about what it omits is limited to its table and the datasheets. The 74 ha hexagon is at the LCZ scale, so nothing in the scheme lowers the range on aggregation. Only 2.3% of DKI cells reach 40% on the residential metric. On roof area, 31.2% exceed 40% and 8.4% exceed 48%, with a plausible maximum of 63.2%, so the "natural cap" is contradicted by the project's own data. LCZ 7, whose datasheet names informal and squatter settlements as its function, is not discussed. Separately, the premise that informal footprints are tortuous is unsupported. The morphological-slum literature stresses small size, high density, low height and irregular arrangement (Taubenböck & Kraff 2014; Taubenböck et al. 2018). Kampung irregularity sits at parcel and alley scale (Funo et al. 2002). I confirmed those three records on Crossref but describe them from prior knowledge, without re-reading them for this review.

- **Point 2 (Data & Metric Integrity)**: *P1.* **Seat 2, Question 1: Does 21.88%, peaking at 48.2%, accurately represent Jakarta?** Not as stated. 21.88% is a correct output of the code but it is coverage after a 0.5 m eave deduction and a land-use filter. The sequence for DKI is 34.4% roof area, 28.75% wall-line and 21.88% net, against 36.3% for GHS-BUILT-S (cell Spearman 0.83). The "gross" 28.75% has therefore already lost about a sixth, and the eave deduction falls hardest on small-grain fabric. The 48.2% is a filtered 74 ha average located in Jakarta Utara, not in the Jakarta Barat kampungs named in §5.4. Jakarta's building coverage on a standard definition is about 34-36%, mostly in the open low-rise range with a substantial compact minority at this scale. Cells mapped to Tambora, Kali Anyar and Jembatan Besi give 14.9, 13.6 and 9.9 m² per person, not 2.92.

  **Seat 2, Question 2: Does the GHS-BUILT-C mask isolate domestic settlement or misclassify ruko?** The mask is not in the pipeline, so the published numbers do not depend on it. The filter actually used keeps buildings under 200 m² in OSM commercial or retail zones, and most strip frontage is not zoned. At least 14,602 retained DKI footprints (0.8% by count, 2.05% by area) contain a commercial place point, and 95.1% of those are outside any commercial or retail zone. This is a lower bound because place data are incomplete and point locations are imprecise. So ruko are mostly counted as housing. The opposite error also occurs: every building in non-commercial zones is removed, deleting 51,744 buildings under 200 m² in DKI, including 24,173 in industrial and 11,996 in military polygons. Adopting GHS-BUILT-C would not resolve this, because a single dominant label per 10 m pixel cannot represent a building with trade below and dwelling above. The "purely domestic" claim should be withdrawn.

- **Point 3 (Artifacts & Confounders)**: *P1.* **Seat 2, Question 3: Can compactness be salvaged, or should it be replaced by footprint density or heterogeneity?** It should be dropped. In DKI, 93.8% of retained polygons are quadrilaterals and the DKI median cell compactness has a standard deviation of 0.015. In my contrast of 9 kampung and 8 planned cells, medians were 0.740 and 0.743 with overlapping ranges. The proposed share below 0.55 does not avoid the artefact: a rectangle falls below 0.55 at an aspect ratio of about 3.4, so it flags narrow terraces and ruko rows, and 62% of the flagged DKI footprints are plain quadrilaterals. Footprint count density is not a good replacement either, since its Spearman with plan area fraction is 0.96. Median footprint area is the best candidate available in the data: Spearman 0.04 with plan area fraction and -0.02 with population density, with a kampung median of 57 m² against 117 m² for planned cells. That contrast is illustrative only, with hand-picked cells and no ground truth. Merged roofs bias grain upward in the densest fabric, so validation is required. Area heterogeneity separated the groups poorly and should be secondary. Inter-building gaps and block structure are closer to the construct. The filter also shapes the crowding tail: 338 cells have footprint per capita below 5 m², with 89% of their roof area removed by the zone rule, and 85 populated cells have zero net footprint.

### 3. Minor Technical Concerns (P2)

- The regularisation mechanism is misattributed. Sirko et al. use a U-Net, cover Africa only and produce no heights; the paper does not describe rectangle fitting. The cited arXiv number resolves to an astrophysics paper (correct: 2107.12283). The polygons here are from Overture, and source attribution is not retained in the project's file.
- ESA WorldCover and MODIS give categorical classes, not impervious surface fraction. The 75-80% figure has no source.
- The Table in §3 lists GHS-BUILT-C as "2020 (Epoch 2023)". The product is a 2018 layer. GHS-POP 2023 is an interpolation of the 2020 and 2025 epochs.
- The block-scale informal range of 0.45-0.65 is attached to a reference whose title and authors are wrong. I could not access the full text, so its presence there is unverified. The high-rise range has no source.
- Whole-building centroid assignment differs from the stated intersection and permits impossible values: cell 888c12b68dfffff has a gross roof fraction of 1.18 against 0.46 in GHS-BUILT-S.
- The compactness statistics describe an area-weighted mean, whereas the code uses an unweighted median (IQR 0.012, not 0.046).

### 4. Fact-Checking & Comparative Grounding

- *Comparative Megacity Evidence*: I found no published cell-wide plan area fraction for Metro Manila. The cited Estoque et al. (2017) DOI resolves to an unrelated paper and no paper with that title was found. The real Estoque, Murayama & Myint (2017) concerns land-surface temperature. Estudillo et al. (2021) also resolves to an unrelated paper and is never cited in the text. The Manila agreement should be removed unless a checkable source is found, or computed directly with one footprint product and one definition across Jakarta, Manila and Bangkok.

- *Empirical Literature Concordance*: The Stewart & Oke claims fail as set out in Point 1. Taubenböck et al. (2018) is real but is in *Applied Geography*, and the cited DOI is unrelated. Sliuzas et al. (2010) could not be found. The roof-based DKI coverage agrees well with GHS-BUILT-S, which is the most reassuring empirical result available and is not in the report.

### 5. Concrete Actionable Recommendations for Revision

1. Withdraw the LCZ 3 alignment and the 40-48% cap. Report building surface fraction on a roof-area basis for all buildings, and compare it with the published ranges for LCZ 3, 6 and 7, or with an LCZ map (Demuzere et al. 2022).
2. Remove the Manila benchmark, or replace it with a sourced or directly computed comparison. Correct every reference that fails to resolve.
3. Disclose the eave deduction and justify it, or remove it from the plan area fraction. Keep residential and gross fractions clearly separate.
4. Rewrite the mask description to match the pipeline. Validate the filter against a labelled sample of ruko, kampung and estate buildings, restrict zone removal so that house-sized buildings are not deleted wholesale, and report sensitivity. Treat ruko as mixed use with a partial weight.
5. Retire building compactness and the irregular share. Test median footprint area and arrangement measures against a very-high-resolution reference that includes merged-roof cases.
6. Remove or re-derive the Tambora, Penjaringan and Jakarta Barat claims. Use finer nested cells for any statement about kampung pockets, and stop comparing footprint per person with a floor-area standard.
7. Add a plausibility check that rejects plan area fractions above 1 and uses land area as the denominator.

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
