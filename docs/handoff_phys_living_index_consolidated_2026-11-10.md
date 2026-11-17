# Consolidated handoff — phys_living_index: from Stage 3 audit to review panel to "what is this index actually for?"

Written 2026-11-10 for an agent with **no prior context**. This is the whole-project consolidation, not a task list. Read §0 first, then §9 (the follow-up the user wants), then dip into the rest as needed.

- **Repo:** `C:\Users\Dimas RD\Documents\projects\phys_living_index` (Windows; PowerShell primary, Git Bash available). Branch `feat/feateng-and-modelling`. At review time HEAD was `80f716b` ("revise disparity indicators") plus uncommitted edits. **Verify with `git status`; do not assume.** Commit/push only if the user asks.
- **Tooling:** `uv run <cmd>`; `uv run pytest -v` (integration tests skipped by default); `uv run ruff check .`. The project rules are in `CLAUDE.md` (ingestion keeps physical units; scaling to [0,1] only in `src/phys_living_index/features/`).
- **Secrets:** `.env` holds credentials (Earth Engine project, NASA Earthdata token, etc.). Never print or copy them.
- **The user's working style (matters):** wants the *significance and impact* of every choice explained, not just a list of choices; prefers a *tight* design over juggling unsuitable data; wants the workflow portable to any region (hence open data); answers coaching questions in their own words and expects you not to put words in their mouth.

---

## 0. Orientation: what to read, in order

1. `CLAUDE.md`, `GLOSSARY.md`
2. `docs/adr/0001-h3-gat-ae-unsupervised-disparity.md` (original design; status line lists what later ADRs supersede)
3. `docs/adr/0002-reference-epoch-representative-composites-zonal-aggregation.md`, `0003-universal-frozen-benchmarks-and-channel-weighting.md`, `0004-everyday-amenity-universe.md`
4. `docs/input_data_resolution.md` (native → ingested → target resolution per layer)
5. **The review package:** `docs/reviews/feature-engineering-report-2026-11-10/`
   - `editorial_decision_letter.md` — the decision, the 18-row "document fix or pipeline change?" table, consensus/disagreement analysis, the 27 must-fix (R1–R27) and 17 suggested (S1–S17) roadmap items with obligations, anchors and "required item details"
   - `referee_reports/seat1_methodology.md` … `seat5_devils_advocate.md` — five human-readable referee reports
   - `reviewer_cards/` — the machine-checked cards (anchored findings)
   - `repo_audit_evidence.md` — the evidence pack every reviewer was given (report-vs-repository comparison, recomputed tables, citation resolution)
   - `panel-provenance.json` — how the panel was actually executed
   - **`author_triage_draft.md`** — the user's decisions and per-item dispositions (the running record from coaching). **Read this before proposing anything.**
6. The report that was reviewed: `c:\Users\Dimas RD\.gemini\antigravity\brain\ecf500e3-2cd4-4343-a9ab-e2de20a84561\feature_engineering_disparity_report_and_review_protocol.md` (outside the repo). An apparent copy is the untracked `docs/feature_engineering_methodology_report.md`.
7. Older handoffs (context, partly superseded): `docs/handoff_phys_living_index_stage3_2026-11-03.md`, `docs/handoff_phys_living_index_stage3_2026-11-09.md`, `docs/handoff_phys_living_index_stage3.md` (the last has **wrong** claims about two bug fixes; ignore it).
8. Stage specs: `.scratch/stage-3-feature-engineering/spec.md` (+ `issues/03…14`), `.scratch/stage-4-modeling-disparity/`, `.scratch/stage-5-dual-validation/` (issues: 01 RWI 4-quadrant, 02 Kotaku validation, 03 orchestrator). Project plan docs: `docs/research_plan.md`, `docs/manuscript_outline.md`, `docs/literature_review_benchmarking.md`, `manuscript/01_introduction.md`, `manuscript/02_literature_review.md`, `latex/`.

---

## 1. Project overview

**Aim (user's words, condensed):** micro- or local-scale disparity can be observed through differences in living standard, which can be inferred from geospatial data. Each indicator should say whether a neighbourhood is better or worse than its neighbours and by how much; a composite index is built afterwards. The workflow must **transfer to any region of the world**, so inputs must be globally open. Local authoritative data may be used for *validation* but not as pipeline input.

**Study area / unit:** Jabodetabek + Karawang, bbox `[106.35, -6.75, 107.65, -5.95]`; Uber H3 resolution 8 cells (17,154; about 0.75 km² each near Jakarta). Residential cells (density ≥ 300 persons/km² and ≥ 1 building): 9,345. Cells with every channel valid (`is_modelled`): 8,375.

**Pipeline stages:** 1–2 ingestion → **3 feature engineering** (per-cell indicators, scaled with universal benchmarks) → 4 Graph Attention Autoencoder (GAT-AE, 2-D bottleneck; reconstruction error and attention weights as "segregation friction"; code exists, trained on an *older* 10-channel matrix) → 5 validation → 6 manuscript. The unsupervised design means the model needs no labels (ADR 0001).

**Where the project stands:** Stage 3 was remediated (GEE-based compositing, area-weighted zonal aggregation, frozen-benchmark scaling; ADRs 0002–0004, tickets 03–14), then revised by the user into a **7-channel** feature store (sessions not visible to the author of this handoff): plan area fraction, ground-footprint-per-capita/space sufficiency, compactness, 15-minute amenity count, NDVI, heat island intensity, terrain safety. Outputs: `data/interim/h3_features_raw.parquet` (62 columns), `data/interim/layers/*.parquet` (per-layer caches), `data/processed/feature_matrix_7d.{parquet,npy}`, `data/processed/stage3_qa.json`, `data/processed/graph_data.pt`, `data/processed/h3_hexagons.parquet`. The user then wrote a methodology report and asked for the independent review that this handoff consolidates.

**Code map:** `src/phys_living_index/pipeline/stage3.py` (orchestration), `features/{build_features,residential,isochrones,reference_sample,building_use}.py`, `data/{gee,gee_layers,ingest_acag,zonal_local,ingest_context,ingest_overture,ingest_buildings}.py`, `validation/{validate_kotaku,evaluate_rwi,audit_bps}.py`, `analysis/validate_living_space.py`, `models/`; configs `configs/default.yaml`, `configs/benchmarks/benchmarks_v0.yaml`, `benchmarks_v1.yaml`; scripts `scripts/{run_feature_engineering,run_ingestion,build_graph_dataset,build_reference_benchmarks}.py`.

---

## 2. The review panel (what was run, what it decided)

**Method:** the Academic Research Skills plugin (v3.24.1), skill `academic-paper-reviewer`, `full` mode: field analysis → four configured reviewer cards (Journal-Fit/regional, methodology, morphology/domain, remote sensing/environmental justice) plus a fixed Devil's Advocate; two-phase paper-blind then paper-visible review under a sprint contract; editorial synthesis with mechanical checkers (`check_phase_conformance.py`, `check_panel_synthesis.py` all passed). The user chose to include **repository checks**, so reviewers also received `repo_audit_evidence.md` and could open repo files read-only and write analysis scripts.

**Decision: Major Revision** (conditions F2, F3, F4, F5 fired; no fatal block declared). The Methodology reviewer attached a live condition: if the tables cannot be regenerated from one versioned run, its grade converts to fatal. Both Devil's Advocate CRITICAL findings were VALIDATED (C1, C2 below).

**Honest limits of the panel (do not oversell it):**
- All five seats are one model family and shared the same orchestrator-compiled audit pack. Agreement is not independent replication (`panel-provenance.json`: role-separated, context-separated, blind to peers, but not model-/provider-/human-distinct).
- Execution notes: seats were interrupted ~14 h mid-run and resumed; the provenance builder was run from a line-ending-normalised copy because Windows converted the plugin's contract file to CRLF (digest matches once LF).
- Advisory checks: reviewer-claim check marked 4 of 86 findings contradicted (the only substantive one: the report *does* cite a planning regulation for slope, so DA M4 "no indicator is tied to a planning instrument" is slightly too strong); suggested-reference check found all but one suggested reference in an index; acronym check is noise.

**What the panel found, in one paragraph each (details and anchors are in the letter):**
1. **The report does not describe the pipeline.** Dataset sources (Open Buildings vs Overture), the "GHS-BUILT-C" residential mask (absent; the pipeline uses OSM land-use zones plus size/rectangularity heuristics), FABDEM (absent; GLO-30 surface model only), walking speed/cutoff (4.5 km/h, 1,125 m vs 4 km/h, 1,000 m), compactness aggregation, ΔLST baseline (P10 vs median), residential rule (Pop ≥ 50 vs density ≥ 300), hexagon geometry (edge 461 m is wrong; ≈531 m) all differ. Many reported numbers do not reproduce (population 32.1 M vs 40.5 M; DKI mean ΔLST +2.78 K vs +10.9 K; strata counts/composition).
2. **Channel 1 is the circular quantity the report condemns.** The matrix's `space_sufficiency_ratio` = GHS built volume / 3 / GHS-POP / 9. It is saturated at its upper bound in about 74–76% of cells. The report's replacement, footprint per capita, is not a model-free measure either.
3. **The headline "2.8–3.1 m² per person" overcrowding in Tambora/Penjaringan is a filter artefact (DA C1).** The lowest-footprint DKI cells lost a median 99.5% of their footprint to the non-residential filter; cells around Tambora show about 8–15 m²; the 48.2% peak plan area is in Jakarta Utara, not Jakarta Barat.
4. **The dasymetric loop is not removed (DA C2).** Log GHS-POP on log residential GHS volume has R² 0.976. Footprint per capita factors into filter retention × footprint/volume × volume-per-person, and the last term (the only one carrying census information) contributes about −0.2% of variance overall (1.5% in DKI). It equals plan area ÷ density.
5. **The features largely track density.** Density + distance to Monas predict 59.1% of scaled-feature variance in spatially blocked CV; the leading principal component holds 70.1% (R² 0.83); within DKI the fit weakens (PC1 R² 0.53; heat R² 0.02).
6. **Channel-level problems:** compactness barely varies (98.9% of cells within 0.65–0.80) and its proposed replacement fails; slope uses a surface model (tall buildings read as terrain) and records uninhabited uplands; ΔLST background mixes uplands and 894 residential cells have no LST (concentrated in Jakarta Utara/Barat; Tier 3 flag true); flood/subsidence (dominant hazards) omitted; NDVI is misnamed as "cover fraction"; "essential" amenities are not what is counted (Overture everyday destinations, ADR 0004).
7. **Literature and framing:** LCZ 3 alignment and the "40–48% cap" contradicted/unsourced; the Metro Manila benchmark has no source; several DOIs fail or resolve to unrelated papers; thermal inequality asserted, not tested; settlement-level claims drawn from 74 ha cells.
8. **Validation:** Susenas listed as "ground truth" but no comparison reported; existing comparison is ambiguous (units few, DKI units share one value).
9. **No disparity function:** indicators point in conflicting directions (amenity vs plan area −0.80; an equal-weight composite is nearly flat across density deciles), so the composite is undefined.

Credits the panel gave: the compositing design, stratification, candid limitations section, DKI plan-area figures reproducing, plan area itself being a sound measure.

---

## 3. What we discussed after the review (chronological, with what each step established)

The coaching used the plugin's Phase 2.5 protocol (Socratic; the author's own words; no inferred work order). Everything below is *in addition to* the letter.

### 3.1 Why every living-space variant failed
The user tried footprint+height+population, then GHS volume, then plan area. The panel's finding: the weak link is the **population denominator**, not the numerator. GHS-POP is allocated within census units in proportion to built form, so within a unit "people per cell" is close to a rescaled copy of "buildings". Better heights or another built layer cannot fix this. (The allocation is inferred from the R² 0.976, and the GHSL method text could not be retrieved — verify before relying on it. Other global grids, e.g. WorldPop, Meta HRSL, are probably also built-layer-informed; untested.)

### 3.2 Synthetic simulation (invented data; illustrates logic only)
Two areas × four Jakarta-like cells with true residents; population allocated from volume with small noise (script in the session scratchpad, see §10). Results: **volume ÷ population** is almost exact *between* census units (36.3 vs 37.1; 13.3 vs 13.0 m²/person) and nearly flat *within* a unit (Gini 0.01 vs true 0.38). **Footprint ÷ population** inverted the ranking (luxury towers worst, kampung pocket best). A **plan-area-based score** (openness = 1 − λp/0.85; the "fabric score", which is only an informal label for plan area fraction) separated kampung from villas but could not distinguish a boarding-house cell from ordinary kampung (true 9.2 vs 11.6 m²/person) or luxury from public-rental towers (0.89 vs 0.88). **Takeaway:** per-person values are meaningful only at census-unit scale; neighbour-scale comparison from open global data supports a physical-fabric claim, not a crowding-of-people claim.

### 3.3 Plan area fraction ("building fabric" is not an academic term)
λp = residential building footprint ÷ whole cell area (numerator restricted to residential buildings; denominator is the full cell). Implementation: roof area minus eave correction (perimeter × 0.5 m, + π·0.25), buildings assigned to the cell of their centroid, non-residential buildings removed (OSM land-use zones; ≥ 2,500 m² and ≤ 3 floors; ≥ 1,000 m² with rectangularity ≥ 0.85 and ≤ 2 floors), clipped to [0,1] (`pipeline/stage3.py`, `features/residential.py`). It is a standard morphology measure (Stewart & Oke 2012 LCZ; Grimmond & Oke 1999; deprived-area mapping literature), but its specific thresholds and its link to living standard in informal settlements are unverified. In the audit pack it correlates **ρ = 0.87 with population density**.

### 3.4 The socioeconomic dimension: no good open input exists at this scale
The user wanted socioeconomic information as an input, but excluded **RWI entirely** (neither input nor validation: 2.4 km tiles, relative within country; note the Stage 5 ticket `.scratch/stage-5-dual-validation/issues/01-rwi-4quadrant-divergence.md` and `src/phys_living_index/validation/evaluate_rwi.py` still exist and now conflict with this decision) and distrusted VIIRS. Screens run on the user's data against the Kotaku slum polygons (**exploratory, one city, 60 positive cells; see §10 to reproduce**):
- **Karawang, 1,311 residential cells, 60 touching a Kotaku "SK Kumuh" polygon** (median polygon 3.8 ha). AUC for ranking slum cells with the assumed-deprived direction: density 0.72 (only in the high-density tercile), plan area 0.72, ΔLST 0.67, compactness 0.62, NDVI 0.60, slope share 0.54, **water frequency 0.39**, **amenities 0.30**, **VIIRS radiance (low = deprived) 0.20**. Flipped, slum cells were brighter than other cells about 80% of the time (median radiance 10.2 vs 2.8), and still so within density terciles (flipped AUC 0.87/0.80/0.67). Across all residential cells radiance correlates 0.82 with density (0.39 within DKI). Conclusion: VIIRS tracks urban intensity here; do not use it as a deprivation indicator (at most a context channel). Karawang is an industrial corridor, so part of this may be local.
- **Accessibility points the wrong way in Karawang:** slum cells had *more* amenities (median 6.5 vs 2.0). The amenity count rises with density; "more = better" is an assumption, not a fact.
- **Candidate proxies (directions fixed beforehand):** share of buildings < 30 m² AUC 0.60 and median footprint 0.59 (tercile AUCs 0.56–0.66; rank correlation with density ≈ 0) — the only candidates with a density-independent effect, modest, could be noise (8 candidates tried). Share of buildings ≥ 500 m² (0.38) and footprint spread (0.39) ran the wrong way. Formal-service share of POIs: coverage poor (421 of 1,311 cells have ≥ 3 POIs), AUC 0.45.
- **Flood proxy:** the existing Dynamic World water-frequency layer (`data/interim/layers/water.parquet`) does not separate Karawang slum cells and shows no relation to Kotaku's own waterlogging/drainage parameters among slum cells (ρ 0.12 / −0.07); plausibly confounded by rice paddies (untested). DKI median 0.006 — it barely registers where flooding is a major issue. The retired `water_frequency` channel is disclosed as retired in the roadmap (R9).
- **Kotaku data caveats:** Karawang polygons are small and usable; **Depok's are village-scale** (59% of residential cells touched once filtered to `rumah > 0`; 100% unfiltered) and discriminate nothing; DKI is a CSV of 445 RW names (`data/validation/dki_rw_kumuh_pergub90.csv`) — **I did not check whether geometry exists to map it to cells**.
- **GRDI (Global Gridded Relative Deprivation Index, NASA SEDAC/CIESIN, DOI 10.7927/3xxe-ap97, per a web search summary):** 30 arc-second (~1 km), 0–100 (higher = more deprived), six components each winsorized at 5% per tail and averaged: built-up ratio, child dependency ratio, infant mortality (CIESIN subnational v2.01, 2015), subnational HDI (Global Data Lab v4.0, 2018), VIIRS 2020 night lights, night-lights trend 2012–2020. **Unverified:** SEDAC page refused my connection; the Earthdata catalogue URL returned 404; I did not open the methodology PDF; I do not know BUILT's deprivation direction, the child-dependency source, coverage, or whether scaling is global or per country. Expectation (untested): within-city variation would come from built-up area and lights, i.e. the same failure mode as VIIRS and a double count of the built-form dimension; the infant-mortality/SHDI parts are administrative-unit constants, useful only as **regional context**. A test needs a NASA Earthdata login (the repo `.env` holds a token for VIIRS work) — **download requires the user's explicit approval (file name and size unknown).**

### 3.5 Resolution question (RWI at 2.4 km)
Larger H3 cells (res 7 ≈ 5 km²) would dilute the micro-scale aim, cut residential cells from ~9,300 to ~1,300 and fall below the N > 2,000 in the Stage 5 RWI ticket. Resolution 8 stays. The user then excluded RWI anyway.

### 3.6 The reframing the user accepted
The user said the planned dimensions are environmental (NDVI), accessibility (15-minute), built-up (plan area fraction) and socioeconomy; scaling with density is acceptable ("disparity may also scale with density"); they do not want to "juggle unsuitable data" to fill the socioeconomy side, and would rather keep the design tight, while still wishing for one socioeconomic indicator eventually. They **accepted** a claim of **physical living-environment disparity**, composite built from **separately validated dimensions**, with socioeconomy reserved as an optional slot and flood as an optional regional module — **each dropped if unconvincing**. Precedent offered from memory (verify): England's Index of Multiple Deprivation has a separate "living environment" domain.

### 3.7 Triage of the roadmap
All 44 items were walked through by theme (A–H). Result: **41 will_address, 3 deferred (R17 spatial dependence/blocked hold-out; R18 density-baseline reporting; S8 MAUP/resolution sensitivity — "a much later part of the research"), 0 declined.** R4 was accepted on the basis that Susenas is only a coarse comparison (data too coarse) and **Kotaku is the validation**. Per-person living-space indicator **dropped**; heat and slope **stay**. The deferred items are not one of the three formal dispositions; they must be resolved before a formal `author-adjudication/1.0` sidecar (schema under the plugin: `shared/contracts/revision/author_adjudication*.schema.json`) can be produced. Full table: `author_triage_draft.md`.

### 3.8 Devil's Advocate's strongest counter-argument and the user's reply
"The feature store mostly records how built-up a place is, several times over." **The user agreed it is not wrong**: many similar projects and rural–urban datasets follow the rural–urban divide, which follows density. They are **not yet sure how to make the work stand out** and want a much deeper dive into the topic and the available datasets. (The coaching protocol forbids the agent from proposing the contribution; keep it that way.)

---

## 4. How the findings cascade: each hole opens the next

Treat this as a dependency chain, not a to-do list. "Status" is what is known, not what is fixed.

1. **Report ≠ pipeline → nothing in the report can be trusted as written.** Tables do not regenerate; the Methodology reviewer's fatal condition applies. *Fix path:* freeze one tagged run (R2) before any modelling. Status: will_address; not started.
2. **Living space per person cannot be a neighbour-scale open-data indicator** (§3.1–3.2). The user dropped it. *Consequence:* the "crowding" story disappears; the built-form dimension now rests on **plan area alone**, which is a density measure (ρ 0.87) whose value depends on the **non-residential filter** (DA C1) and an undisclosed, grain-sensitive eave correction. If the filter is wrong the one remaining built-form indicator is wrong in exactly the dense places that matter.
3. **No socioeconomic input** (§3.4) → the claim must shrink to "physical living environment" → that is, by the user's own concession, **close to a density map** (§3.8). The novelty/standing-out problem is now the central open problem, and it determines what is worth building.
4. **Accessibility's direction is unknown** (§3.4: slum cells have more amenities) and amenities conflict with plan area/NDVI/heat in sign. *Consequence:* no defensible disparity function; the composite is undefined (R19). A single composite can hide neighbourhoods that are crowded *and* well-served.
5. **Environmental indicators have their own holes:** heat baseline mismatch and contaminated cells; LST missing for 894 residential cells (not random — north-coast Jakarta); NDVI cannot separate managed from spontaneous vegetation and is lowered by water; slope from a surface model and area-share-of-cell, not exposure of residents; hazards that matter (flood, subsidence) are not captured by any validated global layer.
6. **Validation is thin.** Kotaku: one usable city (60 positive cells), Depok too coarse, DKI geometry unverified; spatial dependence not handled (R17 deferred), so any AUC is optimistic; no second place for held-out validation. Screening channels on Karawang and validating on Karawang is circular — a held-out place is needed.
7. **"Universal frozen benchmarks" are not actually frozen.** `configs/benchmarks/benchmarks_v1.yaml` says `provisional: false` but its channels are identical to v0, there is no `reference_sample` block, and three channels still say `bound_source: provisional`. The portability claim of ADR 0003 (ticket 14) is unrealised, and 74.4% of residential cells clip at the upper bound of `space_sufficiency_ratio`.
8. **Stage 4 (the GNN) is premature.** The model code was trained on an older 10-channel matrix (`graph_data.pt` dated before the 7-channel revision may be stale); with weak, density-collinear, direction-ambiguous inputs the "segregation friction" it finds risks being a density-gradient detector. The review asked for the evaluation (baseline, blocked hold-out) to be defined *before* modelling.
9. **Literature support is unreliable:** wrong DOIs, unsourced benchmarks (Manila, LCZ cap), and the report's novelty claims ("resolving paradoxes") rest partly on those. The literature review files must be re-verified, not trusted.
10. **Net effect:** the engineering is sound (GEE harness, compositing ladder, provenance, tests), but the *scientific* case rests on (a) a density-correlated built-form indicator, (b) environment/accessibility indicators of undetermined direction, (c) one small validation site. The honest open question is no longer "fix the channels" but **"what can this index say that a density map cannot, and is that testable with open global data?"** — which is the deep dive.

---

## 5. What is still sound (keep, do not redo)

- The GEE zonal harness, representative-composite window ladder with per-cell QA, per-layer caching and provenance (`data/gee.py`, `gee_layers.py`, `pipeline/stage3.py`); 72+ offline tests and `ruff` were passing at the last full run in this thread (re-run).
- Plan area computation in DKI reproduces; Sentinel-2 NDVI matches Dynamic World vegetation probability (ρ 0.90); Landsat LST matches MODIS (ρ 0.88).
- Kotaku Karawang polygons and DKI RW list exist locally; a Kotaku validation module exists (`src/phys_living_index/validation/validate_kotaku.py`, ticket resolved).
- The universal-vs-regional configuration split (benchmarks vs region settings) is a good structure for the "global core + optional regional modules" design the user now wants.

---

## 6. Decisions the user has made (authoritative list: `author_triage_draft.md`)

Design: indicators compare a neighbourhood with its neighbours; composite later · inputs globally open, local data for validation only · **no RWI at all**; validation against Kotaku · VIIRS not accepted as the socioeconomic indicator · claim = physical living-environment disparity, dimensions validated separately · density-correlation acceptable · per-person indicator dropped · heat and slope stay · flood = optional regional module, dropped if unconvincing; same rule for the socioeconomy slot · wish for a socioeconomic indicator remains.

**Not decided:** the accessibility indicator's direction; whether/how flood enters; fate of R17/R18/S8; the paper's distinguishing contribution; which socioeconomy candidate (if any); whether DKI can serve as a held-out validation set.

**Coaching steps still open (ARS Phase 2.5):** the contribution-framing probe (questions only: "Ten years from now, what will citers say this paper established?", "Remove this paper from the literature — what is missing?", "If this paper succeeds, who would make different decisions as a result?" — the user has answered only indirectly), and implementation planning. The user has asked to **pause coaching until the deep dive is done**.

---

## 7. Open facts to verify (I could not)

- GRDI details (§3.4) and whether it adds anything beyond built-up/lights.
- Exact GHS-POP allocation method (the 0.976 R² is inferential).
- Whether DKI RW polygons exist with geometry; whether other cities have open slum/deprivation polygons.
- Hexagon size constants in `GLOSSARY.md` / `configs/default.yaml` (they also say edge 461 m; H3 gives ≈531 m).
- Whether `graph_data.pt` and Stage 4/5 outputs correspond to the 7-channel matrix.
- IMD "living environment" domain as precedent; Kuffer et al. 2021 (*Mapping the Morphology of Urban Deprivation*, Wiley, DOI 10.1002/9781119625865.ch14) and Taubenböck et al. 2018 (*Applied Geography* 92:150–167, DOI 10.1016/j.apgeog.2018.02.002) were found in Crossref lookups — still read them.

---

## 8. Repo-hygiene notes

- This thread added only documentation under `docs/reviews/…` (untracked) and earlier sessions added ADRs, tickets and code (largely uncommitted at various points). **Nothing from this thread was committed.**
- Windows quirks: PowerShell has no `&&`; native stderr shows as `NativeCommandError` even on success; pass `PYTHONIOENCODING=utf-8` when printing non-ASCII; `jsonschema`/`pyyaml` are not in the project env (the plugin checkers were run with `uv run --no-project --with jsonschema --with pyyaml`).
- Do not download datasets, send data to external services, or post anywhere without the user's explicit approval.

---

## 9. The follow-up: a much deeper dive

**Purpose.** Not "fix the channels" but decide what this work can claim that is *not* just density, and whether open global data can support it. The output informs roadmap item **R1** (research question and added value), the socioeconomy slot, the accessibility direction, the composite definition, and what Stage 4 should even test.

**Rules for the dive.** (a) Do not write or rank the paper's contribution — surface options and evidence, the user chooses. (b) Verify every citation against the primary source or Crossref; the existing literature files contain bad DOIs. (c) Separate *established*, *plausible*, and *unverified* in every claim. (d) Prefer reading primary sources and data documentation over summaries. (e) Report back before touching the pipeline.

**Workstream A — Literature map (verified).**
1. How do deprived-area / slum / urban-deprivation mapping studies from Earth Observation handle the density confound? Do they report accuracy beyond a density baseline? (IDEAMAPS line of work; Kuffer, Taubenböck, Sliuzas, Lilford; "Slums from Space"-type reviews.)
2. What do existing gridded deprivation or wealth indices (GRDI, Meta RWI, WorldPop/other wealth maps, DHS-based micro-estimates) validate, at what scale, and where do they fail inside cities?
3. Multi-domain deprivation frameworks with a *living environment* domain (IMD and analogues) — what do they include and how are domains validated?
4. Urban morphology / Local Climate Zones / building-grain metrics as deprivation proxies: effect sizes, scale dependence, transfer between cities.
5. Environmental-justice evidence linking vegetation/heat/hazard to income **in tropical Global South cities specifically** (the report's evidence was largely temperate or multi-city).
6. Accessibility measures (15-minute city, cumulative opportunities vs gravity/floating-catchment): which are validated against deprivation, and what happens in dense informal settlements? Directly addresses the Karawang sign flip.
7. Neighbour-contrast / spatial-discontinuity measures of inequality (local Moran, boundary detection, spatial Gini, focal Gini/Palma), and graph-based/autoencoder approaches: what do they add over local indicators, and how is the density gradient removed or controlled? (Stage 4 context.)
8. Validation designs for unsupervised physical indices: spatial cross-validation, known-group, held-out city.

**Workstream B — Dataset landscape.** Build a table (one row per candidate, columns: what it measures, native resolution, coverage, year(s), license/access, global/open?, how built — especially *whether it is itself derived from built-up or lights* —, known biases, evidence of association with deprivation, collinearity with density). Candidate classes to inventory (from recollection; verify each): GHSL family (BUILT-S/V/H/C, SMOD, POP), Meta HRSL, WorldPop, building footprint products (Overture, Google Open Buildings incl. temporal, Microsoft), heights (GHS-BUILT-H, Open Buildings 2.5D Temporal), OSM (road class/surface, footways/lanes, waterways, land use, POIs; completeness caveats), Overture Places, street-level imagery (e.g. Mapillary — check coverage/license), Dynamic World/ESA WorldCover, Sentinel-1 (texture/roof/structure), Sentinel-2 indices, Landsat/ECOSTRESS thermal, VIIRS/nightlights products, air quality (ACAG PM2.5, Sentinel-5P NO₂), DEMs (GLO-30, FABDEM, MERIT) and HAND/flood hazard layers, subsidence data (InSAR-based, check availability), travel-time/accessibility surfaces, and deprivation/wealth products (GRDI, RWI, DHS-derived). Include **validation resources worldwide** (open slum/informal settlement polygons, e.g. Kotaku in Indonesia; others to discover) because portability depends on them.

**Workstream C — Evidence generation (small pilots, run after A/B).** Use the same protocol as the Karawang screens but better: fix hypothesis directions in advance; test *within density bands*; report AUC with confidence intervals and the number of positives; **select on one site, validate on another**; account for spatial dependence (at least report Moran's I of residuals); record every candidate tried (multiple-comparison honesty). First check what other Kotaku/DKI geometry can be made available before running anything.

**Workstream D — Options memo for the user.** Not a recommendation of a contribution; an options table: for each plausible framing (e.g., what question it answers, what evidence supports it, what data it needs, what would falsify it, what it costs), plus the consequences for the roadmap and for the GNN stage. Include "what if nothing beats density" as an explicit, honest option.

**Deliverables.** (1) A sourced Markdown review (suggest `docs/research/deep-dive-<date>/`: `literature_map.md`, `dataset_inventory.md`, `pilot_screens.md`, `options_memo.md`, `references_verified.md`); (2) a short summary to the user; (3) updated `author_triage_draft.md` if decisions change. Stop and ask before changing code, configs or ADRs.

**Sequencing.** A and B first (can run in parallel), then C on the shortlisted candidates, then D. After D: resume coaching (contribution probe → implementation plan → formal adjudication sidecar), then ADR/glossary updates (e.g., "physical living-environment disparity", the optional-module design), then re-plan Stage 3 changes, then Stage 4/5.

**Stop criteria for the dive.** The user can name, for each dimension, either a validated indicator with a known direction or a decision to drop/defer it; and can state, in their own words, what the index shows that a density map does not (or decides to reposition the work).

---

## 10. Reproducing the screens (temporary session files; may be deleted)

Scripts used (all read-only on project data; run with `uv run python -I <script>` from the repo root):
- `C:\Users\DIMASR~1\AppData\Local\Temp\claude\373526ba80cba13d\e6a85533-4413-4c4d-be68-19362cec40d0\scratchpad\flood_screen.py` — water-frequency vs Kotaku Karawang
- `C:\Users\DIMASR~1\AppData\Local\Temp\claude\373526ba80cba13d\cb0aafb6-a98a-461f-9bf6-5a648ad958a9\scratchpad\viirs_kotaku.py` — VIIRS and indicator AUCs vs Kotaku (Depok filter `rumah > 0`)
- `…\cb0aafb6-…\scratchpad\screen_ses.py` — building-grain/POI-composition/NDVI/VIIRS screen (uses `review\work_domain\cell_morph.parquet`, produced by a reviewer from `data/raw/buildings.parquet` and `data/interim/osm_nonres_zones.parquet`)
- `…\cb0aafb6-…\scratchpad\coaching_sim.py` — synthetic living-space simulation; `…\scratchpad\scaling_impact.py` — earlier scaling-variance comparison
- Review work files: `…\cb0aafb6-…\scratchpad\review\` (contract, phase files, reviewer analysis scripts in `work_*`), mostly duplicated in the repo package.

If they are gone, re-create from §3.4: label a cell "slum" if any part of a Kotaku polygon (`data/validation/kotaku_sk_kumuh_karawang.geojson`) touches it; restrict to residential cells whose centroid is in Kabupaten Karawang (`data/interim/admin_boundaries_study_area.geojson`, `clean_name`); compute ROC-AUC with directions fixed in advance and again within density terciles.

---

## 11. Suggested skills (call via the Skill tool)

- `academic-research-skills:deep-research` — the primary vehicle for Workstream A/B (literature review / full modes; has source-verification agents). Pass the research questions from §9 verbatim.
- `mattpocock-skills:research` — lighter alternative that captures findings as Markdown in the repo from high-trust primary sources.
- `data:explore-data`, `data:statistical-analysis`, `data:validate-data` — for the pilot screens (Workstream C), including CIs, density-conditioned tests and QA of the evidence.
- `mattpocock-skills:grilling` — to stress-test the user's emerging contribution *with questions*, after the dive.
- `academic-research-skills:academic-paper` (modes: lit-review, citation-check, revision) and `academic-research-skills:academic-paper-reviewer` (re-review) — later, for rewriting the report and checking the revision against the roadmap.
- `mattpocock-skills:domain-modeling` — before editing `GLOSSARY.md` or ADRs (new terms, the global-core-plus-optional-modules design, superseding ADR 0003 benchmark wording).
- `mattpocock-skills:tdd`, `mattpocock-skills:diagnosing-bugs`, `mattpocock-skills:code-review` — for any pipeline change after the dive.
- `dataviz` / `data:create-viz` — maps and figures (S7) once indicators are settled.
