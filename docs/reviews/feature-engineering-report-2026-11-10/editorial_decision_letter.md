# Editorial Decision Package

## Calibration Resolution

`calibration_status: NOT_CALIBRATED`

No profile artifact binds this panel, so this package carries no measured error profile.

## Mechanical Audit Lines

```text
dimension_verdicts: [D1=block, D2=block, D3=block, D4=block, D5=block, D6=block]
fired_conditions: [F2, F3, F4, F5]
da_critical_adjudications: [C1=VALIDATED, C2=VALIDATED]
editorial_decision=major_revision
```

---

# Part 1: Editorial Decision Letter

## Manuscript Information

- **Title**: Spatial Feature Engineering for Physical Living Condition Disparity: Methodological Report & Independent Peer Review Protocol
- **Manuscript ID**: None assigned (`stage3-feature-report-round-1`)
- **Decision Date**: 2026-11-10
- **Review Round**: Round 1
- **Target venue**: None bound (`criteria_binding_unavailable`). This letter makes no venue-fit claim.

Dear Author,

Your report was reviewed through five role-separated seats. Seat labels in this letter are EIC (journal-fit), MET (methodology), DOM (domain), PER (cross-disciplinary, remote sensing) and DA (Devil's Advocate). Findings are cited by seat and card ID, for example `MET W4`. `R<n>` and `S<n>` refer only to roadmap items.

## Review Panel Provenance (#540/#740)

- **Typed artifact**: `panel-provenance.json` (review directory)
- **Artifact SHA-256**: `e24492795c4a768ee6e2f150301a28cee0c1ede2f90e676486ec121dc79cb5e7`
- **Panel ID**: `stage3-feature-report-round-1`
- **Normalized manifest SHA-256**: `ef66cff63bf52ffa3bbb87495ecf10034d8b9dce2af6c64b15fec72aaf2e2526`
- **Execution topology SHA-256**: `516f3584a18ace3a1553d7cb8e708f2d119f6b0fabac1bbd1976cb4d19f14a65`
- **Fresh-context scope**: `within_panel_attempt_only` (does not compare retries or prior rounds)

| Seat | Role ID | Actor type | Context ID | Peer outputs visible | Model family | Provider | Human reviewer ID |
|---|---|---|---|---|---|---|---|
| EIC | eic | model | invocation-ab85c1eb4ba5876a5 | false | claude-opus | anthropic | null |
| R1 | methodology | model | invocation-a018f4d868d414c23 | false | claude-opus | anthropic | null |
| R2 | domain | model | invocation-a4d9e7f9f4ac35b8c | false | claude-opus | anthropic | null |
| R3 | perspective | model | invocation-a8d4654777cdc3c32 | false | claude-opus | anthropic | null |
| DA | da | model | invocation-aedd24bdf78d7d914 | false | claude-opus | anthropic | null |

| Provenance axis | Status |
|---|---|
| Role-separated | true |
| Within-panel invocation-context separation | true |
| Blind to peer outputs | true |
| Model-family distinct | false |
| Provider distinct | false |
| Human-reviewer distinct | false |

- **Binary independence claim**: Not computed. Role diversity proves only role separation. This panel should not be described as independent.
- **Correlated-error disclosure**: All model-executed review seats used one model family; role separation does not remove correlated-error risk.
- **Shared-input disclosure**: All reviewers were given the same orchestrator-compiled repository audit pack (`repo_audit.md`). It is a shared input and a further source of correlated error. Agreement between seats on a figure taken from that pack is not independent confirmation of that figure.
- **Execution notes**: The provenance builder ran from a scratch copy because Windows had converted the plugin's contract file to CRLF. With LF endings its SHA-256 equals the pinned contract digest, so the contract content is unchanged. Panel seats were interrupted for about 14 hours mid-run and resumed in the same context.
- **Synthesizer verification**: The two DA CRITICAL findings were rechecked read-only against the feature store by this synthesizer, which is also model-executed. That check reduces arithmetic risk only. It does not reduce correlated-error risk on interpretation.

## Decision: Major Revision

The decision is mechanical. No condition was softened.

**Role-scoped matrix** (only assessed eligible seats)

| Dimension | Priority | Eligible assessed seats | Verdict |
|---|---|---|---|
| D1 methodology_rigor | mandatory | MET: block (repairable) | block |
| D2 domain_accuracy | mandatory | DOM: block (repairable) | block |
| D3 argumentative_coherence | mandatory | DA: block (repairable); MET: block (repairable) | block |
| D4 cross_disciplinary_relevance | high | PER: block | block |
| D5 writing_and_structure | normal | EIC: block | block |
| D6 venue_fit_and_contribution | mandatory | EIC: block (repairable) | block |

**Failure conditions**

| Condition | Severity | Quantifier | Evaluation | Fired |
|---|---|---|---|---|
| F1 any mandatory fatal block | 95 | any | No seat declared `fatal` on D1, D2, D3 or D6 | false |
| F2 any mandatory scores block | 90 | any | D1, D2, D3 and D6 each have at least one block | true |
| F3 two or more mandatory warn or worse | 70 | majority | D1 (n=1) true; D2 (n=1) true; D3 (n=2, both seats) true; D6 (n=1) true; count 4 | true |
| F4 any high-priority scores block | 60 | any | D4 block | true |
| F5 any dimension warn or worse | 40 | any | All six | true |
| F0 every dimension passes | 10 | all | None pass | false |

Precedence: F2 has the highest severity among fired conditions, and its action is major revision.

**Limits on this decision.** All four mandatory blocks are declared repairable, so F1 did not fire. MET attaches a condition to its D1 grade: "If the authors cannot regenerate the tables from a single versioned run, this judgement should convert to fatal." That condition is live for the next round. D6 is graded on contribution only, because no venue was bound.

## Blocking Issues (3 shown, immutable source order)

All six dimensions block, so this table is the shortest route into the problem and not the full list. The contribution block on D6 (R1), the literature block on D2 (R5, R6, R11) and the thermal-framing block on D4 (R23, R25) also stand.

| Transport ref | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| R2 | The report does not describe the analysis in the repository, and its tables cannot be regenerated from the outputs | EIC W2; MET W2; PER W5; DA M7 | table: §3 Primary & Secondary Datasets, rows for Google Open Buildings v3, GHS-BUILT-C, FABDEM and OpenStreetMap | R2 |
| R3 | The headline severe-crowding result is produced by the non-residential filter | EIC W3; MET W7; DOM W5, W6; DA C1 | text: §6.2 "accurately revealing the $2.8\text{--}3.1\text{ m}^2/\text{person}$ conditions in Tambora and Penjaringan" | R3 |
| R12 | Channel 1 of the matrix is the quantity the report declares circular, and it is nearly constant | MET W1, W8; EIC W2; DA M3 | equation: §1 feature vector x_i, element 2 (A_fp,res,i / Pop_i) | R12 |

## The Central Editorial Question: Document Fix or Pipeline Change?

The short answer is that rewriting the report to match the code is not enough, and changing the code to match the report is not enough either. The clearest case is the crowding channel. If you document the code, you carry forward a channel that MET W1 and DA M3 show is close to a saturated constant. If you implement the report, you adopt footprint per capita, which DA C1 and C2 show is driven at cell scale by the filter and by building-product disagreement. Both routes lead to a new specification.

"Intended truth" below is stated only where a card establishes it. Elsewhere it is **unknown**, and only you can settle it.

| # | Item | Report vs repository | Remedy class | Intended truth | Timing | Source |
|---|---|---|---|---|---|---|
| 1 | Crowding channel | Footprint per capita vs `space_sufficiency_ratio` from GHS volume | **Pipeline must change** in either direction | Unknown (DA M3) | Before modelling | MET W1, W8; EIC W2; DA M3, C2 |
| 2 | Residential mask | GHS-BUILT-C vs OSM land-use zones plus geometric rules | **Pipeline must change.** DOM W4 finds a swap to GHS-BUILT-C would not settle mixed use. The filter needs validation and a partial weight | Unknown | Before modelling | DOM W4, W5; EIC W2, W3; MET W7; DA C1 |
| 3 | DEM | GLO-30 / FABDEM vs GLO-30 surface model only | **Pipeline must change.** Bare-earth DEM is the stated minimum | Unknown | Before modelling | PER W9; MET W23; EIC W2 |
| 4 | ΔLST baseline | P10 of vegetated cells vs median of rural vegetated cells, and neither reproduces the reported table | **Pipeline must change.** A lowland, elevation-matched reference is requested whichever statistic was intended. Contaminated cells also need treatment | Unknown | Before modelling | MET W4; PER W4, W5 |
| 5 | Modelled universe | 9,345 vs 8,375 modelled | **Pipeline must change or be stress-tested.** Disclosure alone leaves holes in the graph on the north coast | Both numbers are real; the report omits the second | Before modelling | MET W15; PER W3; DA M11 |
| 6 | Compactness | Area-weighted mean vs unweighted median; the §6.3 replacement is not implemented | **Pipeline must change**: drop the channel. Do not implement the §6.3 replacement as written (DOM W7; EIC W8) | Unknown for the statistic; moot if dropped | Before modelling | DOM W7; EIC W8; DA M9 |
| 7 | Amenity set | OSM "essential" vs Overture Places everyday destinations | **Document and pipeline.** Rename the measure, and add an essential subset and better origins | Repository is intended (ADR 0004, per EIC W11) | Before modelling for the channel definition | EIC W11; MET W17 |
| 8 | Landsat window | "2022–2024 Composite" vs a tier ladder with 74.8% of cells on Jun–Sep 2023 | **Document, and a pipeline decision.** The repository's Tier 3 flag is true, and ADR 0002 says to revisit before training | Repository design is intended (ADR 0002, per PER W2) | Before modelling | PER W2 |
| 9 | Reported tables and population | 32.10 M vs 40.48 M; ΔLST +2.78 vs +10.90 K, and others | **Document fix by regeneration** from one tagged run, provided the outputs are the truth. MET weighed staleness and found no single rule or vintage reconciles them | Unknown | Freeze before modelling; rewrite after | MET W2; EIC W2; PER W5; DA M7 |
| 10 | Strata | Kota Tangerang listed in the Kota stratum but counted in Kabupaten; 870 cells outside every polygon | **Document and code.** Redefine strata from official boundaries, and correct the Kota Tangerang mapping in the validation code | Unknown | Before modelling | EIC W4, W9; MET W21 |
| 11 | Vegetation channel | "Cover fraction" on [0,1] vs mean NDVI; lower = deprivation vs orientation `context` | **Document** for the name. **Pipeline** for the missing water mask. The direction must be decided | Unknown for direction | Before modelling for direction and water mask | MET W20; PER W11, W12 |
| 12 | Plan area geometry | Polygon intersection vs centroid assignment with undisclosed eave correction | **Document at minimum.** Keep or remove the eave deduction by explicit decision (see Disagreement 1) | Unknown; report is silent | Before modelling | MET W22; DOM W3, W13 |
| 13 | Building source | Google Open Buildings v3 vs Overture | **Document fix.** Retaining the dropped `sources` field is a pipeline improvement needed to examine source composition | Unknown | Write-up; field retention before modelling if pursued | EIC W2, W5; DOM W9 |
| 14 | Walking cutoff | 1,125 m vs 1,000 m | **Document fix** unless 1,125 m was intended, in which case rerun | Unknown | Settle before modelling | EIC W2; MET W17 |
| 15 | Residential rule | Pop >= 50 vs density >= 300 and building count >= 1 | **Document fix**, with the existing mask sensitivity reported | Unknown | Write-up | MET W19 |
| 16 | Slope algorithm | Horn vs `ee.Terrain.slope` on a reprojected DEM | **Document fix**, subject to the stair-step check PER raises | Unknown | Write-up | PER W14 |
| 17 | Thresholds | 5 m² vs 7.2 m² vs 9 m², applied to ground footprint | **Document fix.** State one threshold and stop applying it to footprint | Unknown | Write-up | EIC W17; MET W25; DOM W5; DA M10 |
| 18 | Hexagon geometry, GHS epochs, DKI slope statement | Internal or factual errors | **Document only** | Report is wrong as written | Write-up | MET W18, W23; EIC W14; DOM W12; PER W9 |

## What Must Be Done Before Graph Neural Network Modelling

These items change what the model receives or how it is evaluated. A representation trained before they are settled would have to be retrained.

- **Freeze the input**: one tagged pipeline run with a run identifier (R2).
- **Re-specify crowding**: resolve channel 1 and the footprint-per-capita alternative together (R12, R14), including the non-residential filter (R3, R21).
- **Handle the gaps**: 894 cells have no LST and the graph has holes in Jakarta Utara and Barat (R20). Settle the composite and tier question (R24) and the thermal baseline and contaminated cells (R13).
- **Fix or remove weak channels**: compactness (R22), slope source and form (R26, R27), amenity definition (R8), hazard construct (R9).
- **Set the numerical treatment**: zero inflation and skew (R16), scaling bounds and clipping (R19), and vegetation direction and water mask (S10).
- **Define the evaluation in advance**: a disparity function (R19), a density baseline the model must beat (R18), spatially blocked hold-out (R17), and a validation target (R4). Strata definitions feed these comparisons (R7).

These items concern the write-up and can follow modelling, but they must be complete before any submission: the contribution statement (R1), the Manila and LCZ claims (R5, R6), arithmetic (R10), references (R11), settlement-level statements (R15), thermal and inequality framing (R23, R25), and the suggested items not listed above.

## DA CRITICAL Adjudications

**C1: VALIDATED.** *DA's argument*: the 2.8 to 3.1 m² per person result is produced by the non-residential filter and not by crowding. *Corroboration*: EIC W3, MET W7, DOM W5 and W6, each with its own recomputation. PER did not address it. *Verification against the feature store*: confirmed. DKI P5 of net footprint per capita is 2.89 m². Using the 860 DKI cells, 43 cells sit at or below P5, with a median 99.5% of footprint removed, median gross 28.0 m² and median net 0.15 m². One is in Jakarta Barat and 24 are in Jakarta Utara. DA's 44 cells, 25.9 m² and 0.21 m² reproduce exactly when one further Jakarta-tagged cell is included (861 cells), so the difference is a stratum-membership detail. For DKI cells with under 20% removed I get 514 cells and P5 of 10.6 m² (DA: 515 and 10.5). Of DKI cells below 5 m², 95.6% lost over half their footprint, and 0.35% of DKI cells are below 5 m² before filtering. With an approximate Tambora point and 1.5 km radius I get 10 cells at 9.9 to 15.0 m²; DA's 9 cells run 7.9 to 15.0 m². Either way no value is near 2.9. The single Penjaringan-area cell at 2.72 m² was not independently rechecked. *Limit*: the settlement locations are radius approximations, as DA states. *Required author response*: R3.

**C2: VALIDATED.** *DA's argument*: moving to 2D footprint does not eliminate the dasymetric loop, and the measure is not model-free. *Corroboration*: MET W5 and W6, by a different decomposition; DOM W5 on "model-free". EIC and PER did not address it. *Verification*: confirmed on 9,260 cells. Log GHS-POP on log residential GHS volume gives R² 0.976. Covariance shares of log footprint per capita are 59.3% for the filter term, 40.9% for footprint over volume, and −0.2% for volume per person; within DKI the filter term is 103.9% and volume per person 1.4% (DA: 1.5%). Footprint per capita equals plan area over density to rounding. *Limits*: the GHSL allocation is inferred from the data and the report's own statement, since DA could not retrieve the method text and MET also infers it. Calling volume per person "the only term carrying census information" is DA's interpretation. The demonstrated coupling does not depend on that interpretation, and it does not depend on whether Google footprints trained GHSL, which DA could not confirm. *Bound on the finding*: DA itself credits footprint mass as informative at census-unit scale; see Disagreement 3. *Required author response*: R14.

## Consensus Analysis

Counts are over the four non-DA seats. "Silent" is neither agreement nor dissent. Because the four seats share a model family and an audit pack, a consensus label records agreement among roles and is not independent replication.

### [CONSENSUS-4]

- **SC-1**: The report's specification does not match the repository. EIC W2; MET W1, W17, W19; DOM W4, W7; PER W9, W14.

### [CONSENSUS-3]

- **SC-2**: Reported tables cannot be regenerated from the outputs. EIC W2, MET W2, PER W5. DOM silent. DOM S2 records that the DKI plan-area figures do reproduce.
- **SC-4**: The low footprint tail and the named-settlement crowding figures are a filter artefact. EIC W3, MET W7, DOM W5/W6. PER silent. DA C1.
- **SC-13**: Reported ΔLST magnitudes and baseline cannot be interpreted. EIC W2, MET W4, PER W4/W5. DOM silent.
- **SC-14**: The DEM is a surface model, and FABDEM is absent from the code. EIC W2, MET W23, PER W9. DOM silent.
- **SC-18**: 74 ha cell values cannot carry statements about named settlements or residents. MET W10, DOM W6, PER W6/W15. EIC silent.
- **SC-19**: A living-area threshold is misapplied to ground footprint. EIC W17, MET W25, DOM W5. PER silent. DA M10.

### Corroborated Findings (2 of 4, no conflict)

| Sub-claim | Finding | Seats | Silent | DA |
|---|---|---|---|---|
| SC-3 | Channel 1 is the condemned quantity | MET W1, EIC W2 | DOM, PER | M3 |
| SC-5 | Footprint per capita keeps dasymetric dependence and is not model-free | MET W5/W6, DOM W5 | EIC, PER | C2 |
| SC-6 | Susenas is named as ground truth with no comparison | EIC W4, MET W16 | DOM, PER | M6 |
| SC-7 | LCZ 3 alignment and the 40–48% cap are unsupported | EIC W7, DOM W1 | MET, PER | M8 |
| SC-8 | Manila benchmark has no verifiable source | EIC W6, DOM W2 | MET, PER | M8 |
| SC-9 | The reference list is unreliable | EIC W15, DOM W2/W8–W10 | MET, PER | M12 |
| SC-10 | Compactness fails, and its stated replacement also fails | DOM W7, EIC W8 | MET, PER | M9 |
| SC-11 | The stated residential mask is absent | EIC W2, DOM W4 | MET, PER | none |
| SC-12 | LST missingness is undisclosed and non-random | MET W15, PER W3 | EIC, DOM | M11 |
| SC-15 | Flood and subsidence are omitted | EIC W12, PER W8 | MET, DOM | none |
| SC-17 | "Essential" amenities are not what is counted | EIC W11, MET W17 | DOM, PER | minor note |
| SC-20 | Report numbers conflict internally | EIC W14, MET W3/W18/W21/W24 | DOM, PER | M7 |
| SC-21 | Strata do not match their stated composition | EIC W9, MET W21 | DOM, PER | none |
| SC-22 | Independence from density is untested | MET W13, EIC W1 | DOM, PER | M1 |
| SC-23 | NDVI is misnamed and cannot bear the green-deficit reading | MET W20, PER W11/W12 | EIC, DOM | none |

### Single-Reviewer Findings

Retained on their own evidence and not labelled consensus: SC-25 contribution (EIC W1); SC-26 zero inflation (MET W11); SC-27 spatial dependence (MET W12); SC-28 scaling and aggregation (MET W14, with DA M2); SC-29 LST read as heat exposure (PER W1); SC-30 composite and tiers (PER W2); SC-31 inequality untested (PER W6); SC-32 POI coverage (EIC W5); SC-33 transferability (EIC W8); SC-34 population reconciliation (EIC W10); SC-35 article form (EIC W13); SC-36 labels (EIC W16); SC-37 maps (EIC W18); SC-38 MAUP (MET W9); SC-39 universe rule (MET W19); SC-40 tortuosity premise (DOM W8); SC-41 factual corrections (DOM W9–W12); SC-42 plausibility check (DOM W13); SC-43 thermal and slope details (PER W7, W13–W15); SC-44 harms of labels (PER W16). SC-29 and SC-31 carry the D4 block alone. DA M4 (actionability) has no non-DA counterpart.

### Points of Disagreement

The EIC card did not arbitrate these conflicts. The resolutions below are the synthesizer's, made on the evidence in the cards.

**Disagreement 1 [SPLIT, SC-24]: Is the eave correction neutral?**
- **MET W22**: wall-to-roof ratio barely varies with density (0.806 to 0.826), so "I do not claim differential bias".
- **DOM W3**: "The deduction is not neutral". The ratio ranges from 0.75 to 0.96 across DKI cells and rises with median building size (Spearman 0.45).
- **Type**: Existence.
- **Editor's Resolution**: Both stand, because they test different axes. The deduction is approximately neutral across density and not neutral across building grain. Disclose it, and make an explicit decision on whether to keep it before modelling. Roadmap S11.
- **Rationale**: Evidence and expertise. Grain is the morphological axis at issue, and it is DOM's domain.

**Disagreement 2 [SPLIT, SC-16]: Where does slope belong?**
- **PER W9, W10**: a bare-earth DEM is the minimum, and terrain should be intersected with buildings or population. Flood takes priority as a hazard (W8).
- **MET W11**: recompute for built-up pixels, "or be kept out of the embedding and used as a post hoc overlay". DA M5 also says to treat slope as context.
- **EIC W12**: add flood and subsidence layers, or narrow the construct to slope hazard.
- **Type**: Direction.
- **Editor's Resolution**: The current channel cannot be carried forward; all positions agree on that. The cards do not settle whether a corrected slope stays in the embedding. That is left to the author, who must state the choice and the reason before modelling. Roadmap R26, R27, R9.
- **Rationale**: Author autonomy on an unresolved design question, with a required explanation.

**Disagreement 3 [unresolved dissent]: Does footprint per capita carry valid signal at census-unit scale?**
- **DA (credit in review body)**: 0.74 to 1.26 of the Susenas median, Spearman 0.56 over 16 units and 0.39 over the 10 non-DKI units; "Footprint mass is informative at census-unit scale."
- **EIC W4**: across 9 non-DKI units Spearman is −0.08, ratios run 0.73 to 1.29 over 14 units, and agreement is "between different constructs and should not be read as validation".
- **MET W16**: units are few and not independent, so this is "weak evidence either way" (stated for modelled floor area).
- **Type**: Existence.
- **Editor's Resolution**: **Unresolved.** The two calculations use different unit sets and the cards do not reconcile them. No claim of unit-level validity should be made until the author publishes one comparison with its unit list. Roadmap R4.
- **Rationale**: Unresolved-dissent principle. This synthesis does not choose between them.

**Disagreement 4 [severity]: How severe is the filter artefact?**
- **DA C1** grades it Critical. **EIC W3, MET W7, DOM W5** grade it Major.
- **Editor's Resolution**: Grades are transported unchanged. The disagreement does not affect the decision: C1 is validated and F2 fires independently.

**Figure reconciliations (no substantive conflict)**
- *PC1 share*: DA reports 70.1% and MET W13 reports 52%. Both reproduce on the 8,375 modelled cells: 70.1% from the covariance matrix of scaled channels and 51.8% from the correlation matrix. They answer different questions. A variance-seeking encoder on the scaled matrix faces the 70.1% figure.
- *Excluded cells*: MET W15 finds excluded cells denser overall (median 3,818 vs 2,185 per km²); DA M11 finds no density difference inside DKI. These are different scopes.
- *Footprint-per-capita decompositions*: MET W5, MET W6 and DA C2 factor the same quantity differently, and the identities coexist. They do not compete.

## Decision Rationale

F2 fires on four mandatory dimensions, and the contract's action is major revision. The fired action stands as computed.

The seats converge on one problem. EIC W2 finds the manuscript does not describe the repository's analysis, and all four non-DA seats contribute specific mismatches (SC-1). MET W2 shows the tables cannot be regenerated. Those are not only reporting defects. MET W1 and DA M3 show that the matrix channel for crowding is the quantity §6.2 rejects, while DA C1 and C2, corroborated by EIC W3, MET W5–W7 and DOM W5, show that the proposed replacement fails at cell scale. Neither document nor code offers a sound specification of the report's most prominent indicator.

Literature support is also weak where the report claims its contribution. DOM W1 and EIC W7 find the LCZ alignment contradicted by the published ranges, and EIC W15 and DA M12 find key references unverifiable. PER W1 and W6 find surface temperature presented as heat exposure and injustice without a stated link.

Rejection is not indicated. No seat declared a fatal block. MET explains that a coherent pipeline with dated outputs exists, and DOM finds plan area itself sound and DKI values reproducible (S2). Candid limitations, stratification and the careful compositing design are credited by the seats (EIC S1, S3; MET S1, S2; PER S4). A lesser decision is unavailable under the contract, and would not fit a report whose main channel must be re-specified. MET's conditional conversion to fatal applies if a single versioned run cannot be produced.

---

# Part 2: Revision Roadmap

Rows use immutable source order: fixed seat order EIC, MET, DOM, PER, DA, then finding ordinal of the driving finding. `R<n>` is a transport reference and not a work rank. Severity and Confidence are transported from the driving finding, with other grades noted. Timing is added for this report: **P** means before modelling and **W** means write-up.

The closed `revision-roadmap/1.0` JSON is not emitted here. No block manifest is bound, so `proposed_targets[]` cannot be populated without invention.

## Required Revisions (Must Fix)

| Transport ref | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Obligation class | Cost scope | Bounded consequence | Timing |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | State a research question and show added value over density and a named baseline | SC-25 | Critical | text: Executive Summary "A core contribution of this report is resolving the" | 4 — editorial judgement | EIC W1 | must_fix | new_data: outcome and baseline comparison | acceptance_criterion_unmet: claim, core contribution | W |
| R2 | Regenerate every exhibit from one frozen, tagged run and rewrite §2, §3, §5 from it | SC-1, SC-2 | Critical | table: §3 Primary & Secondary Datasets, rows for Google Open Buildings v3, GHS-BUILT-C, FABDEM and OpenStreetMap | 5 — repository audit | EIC W2; MET W2; PER W5; DA M7 | must_fix | re_analysis: §2, §3, §5 | method_reproducibility_unresolved: manuscript | P (freeze), W (rewrite) |
| R3 | Withdraw the settlement crowding claims; validate the filter; report with and without it; flag cells where it removes most footprint | SC-4 | Major (DA C1 Critical) | text: §6.2 "accurately revealing the $2.8\text{--}3.1\text{ m}^2/\text{person}$ conditions in Tambora and Penjaringan" | 5 — recomputed | EIC W3; MET W7; DOM W5, W6; DA C1 | must_fix | re_analysis: non-residential filter | claim_scope_unsupported: claim, §6.2 | P |
| R4 | Report the Susenas comparison, separating footprint from floor area, including failures; add known-group validation | SC-6 | Major | text: §3 "Ground-Truth Floor Space per Capita Benchmark" | 4 — QA file and validation module | EIC W4; MET W16; DA M6 | must_fix | re_analysis: Susenas units | evidence_gap_remains: claim, ground-truth benchmark | P (define), W (report) |
| R5 | Remove the Manila benchmark or compute it with the same pipeline | SC-8 | Major | text: §6.1 "This matches observations in Metro Manila" | 5 — Crossref | EIC W6; DOM W2; DA M8 | must_fix | section: §6.1, Executive Summary | claim_scope_unsupported: claim, peer alignment | W |
| R6 | Withdraw the LCZ 3 alignment and the 40–48% cap, or derive it at LCZ-appropriate scale; discuss LCZ 6 and LCZ 7 | SC-7 | Major (DOM W1 Critical) | text: §6.1 "grid-level $\lambda_p$ naturally caps at" | 4 — LCZ class ranges | EIC W7; DOM W1; DA M8 | must_fix | section: §6.1, Executive Summary | claim_scope_unsupported: claim, LCZ alignment | W |
| R7 | Define study area and strata from official boundaries, with a sensitivity check; correct stated composition | SC-21 | Major | text: §5.1 "representing mature urban satellite cities (Kota Bogor, Depok, Tangerang, Tangerang Selatan, Bekasi)" | 5 — reproduced | EIC W9; MET W21 | must_fix | re_analysis: strata | interpretive_ambiguity_remains: table, Table 5.3 | P |
| R8 | Report formal-service and everyday counts separately; add a demand-sensitive form; replace the single centroid origin | SC-17 | Major | text: §2.2 "Clinics, puskesmas, pharmacies, hospitals" | 5 — config and ADR read | EIC W11; MET W17 | must_fix | re_analysis: amenity channel | claim_scope_unsupported: dataset, amenity channel | P |
| R9 | Add flood and subsidence layers from suitable sources, or narrow the construct to slope hazard | SC-15 | Major | text: §1 "Geomorphological hazard exposure (landslide vulnerability, unbuildable steep terrain)" | 4 — hazard literature | EIC W12; PER W8 | must_fix | new_data: hazard layers | claim_scope_unsupported: dataset, hazard dimension | P |
| R10 | Correct internal contradictions in text and tables | SC-20 | Major | text: Executive Summary "$83.8\%$ peri-urban/rural cells" | 5 — arithmetic | EIC W14; MET W3, W18, W21, W24 | must_fix | section: Executive Summary, §2.1, §5 | editorial_conformance_unmet: manuscript | W |
| R11 | Rebuild the bibliography from primary sources and remove claims whose support cannot be found | SC-9 | Major | text: References "Sliuzas, R., Mboup, G., & de Sherbinin, A. (2010)" | 5 — Crossref | EIC W15; DOM W2, W8–W10; DA M12 | must_fix | section: References | reader_traceability_reduced: manuscript | W |
| R12 | Resolve channel 1: state the true channel and replace the saturated quantity with a justified crowding measure; reconcile the two R_space definitions | SC-3 | Critical | equation: §1 feature vector x_i, element 2 (A_fp,res,i / Pop_i) | 5 — code and matrix | MET W1, W8; EIC W2; DA M3 | must_fix | re_analysis: channel 1 | acceptance_criterion_unmet: dataset, feature matrix | P |
| R13 | Specify one thermal baseline; use a lowland, elevation-matched reference with sensitivity analysis; remove contaminated cells | SC-13 | Major | text: §2.2 "calculated as the 10th percentile LST across all vegetated peri-urban cells" | 5 — logical implication and recomputation | MET W4; PER W4, W5 | must_fix | re_analysis: heat channel | method_reproducibility_unresolved: table, ΔLST rows | P |
| R14 | Retract "eliminates" and "model-free"; use a population denominator not allocated by built layers, or restrict inference to census-unit scale | SC-5 | Major (DA C2 Critical) | text: §6.2 "successfully eliminates this dasymetric feedback loop" | 4 — log identity on pipeline layers | MET W5, W6; DOM W5; DA C2 | must_fix | re_analysis: footprint per capita | claim_scope_unsupported: claim, dasymetric resolution | P |
| R15 | Stop attaching cell statistics to named settlements or households; relocate the 48.2% claim; address ecological inference | SC-18 | Major | text: §5.4 "In the densest informal kampungs of Jakarta Barat" | 4 — location check | MET W10; DOM W6; PER W6, W15 | must_fix | section: §5.4, §6.2 | claim_scope_unsupported: claim, §5.4 | W |
| R16 | Replace min-max on spike channels with a two-part or zero-inflated treatment; give slope and amenity zeros separate handling | SC-26 | Major | table: Table 5.2, rows A_amenity and S>15 | 5 — direct computation | MET W11 | must_fix | re_analysis: amenity and slope channels | acceptance_criterion_unmet: dataset, channel scaling | P |
| R17 | Quantify spatial dependence and adopt spatially blocked hold-out | SC-27 | Major | absence: §5 and §6 — expected Moran's I, effective sample size or a spatial validation design; checked §2.1, §5.2, §5.3, §5.4, §6.1 to §6.6 and §7.1 | 4 — permutation tests | MET W12 | must_fix | re_analysis: validation design | evidence_gap_remains: manuscript | P |
| R18 | Report variance explained by density and distance by channel and stratum; define a density baseline the model must beat | SC-22 | Major | text: §4.1 "Independence from Census Demography" | 4 — computed | MET W13; EIC W1; DA M1 | must_fix | re_analysis: density baseline | claim_scope_unsupported: claim, §4.1 | P |
| R19 | Publish scaling bounds and clipping; resolve provisional bounds; define a disparity function with sensitivity to weights and directions | SC-28 | Major | absence: §2.2 and §5 — expected transforms, scaling bounds, weights and a robustness analysis for the composite inputs; checked §1, §2.1, §2.2, §4.1, §6 and §7.1 | 5 — manuscript search and config | MET W14; DA M2 | must_fix | re_analysis: scaling and composite | method_reproducibility_unresolved: dataset, benchmarks | P |
| R20 | Report the modelled universe and coverage by unit; diagnose the mask; address gaps with imputation or a broader composite, with sensitivity | SC-12 | Major | absence: §5.2 to §5.4 — expected counts and a rule for cells with no LST or compactness; checked the header block, §2.1, §5.2, §5.3, §5.4 and §6 | 5 — direct computation | MET W15; PER W3; DA M11 | must_fix | re_analysis: LST coverage | evidence_gap_remains: dataset, modelled universe | P |
| R21 | Describe the actual mask; replace binary treatment of mixed use with a validated partial weight | SC-11 | Major | text: §4.1 "Masking via GHS-BUILT-C ensures that building coverage measures purely domestic settlement density." | 4 — code read | DOM W4; EIC W2 | must_fix | re_analysis: residential mask | claim_scope_unsupported: dataset, residential mask | P |
| R22 | Drop compactness as a channel; validate a replacement against known groups | SC-10 | Major | text: §6.3 "which avoids vectorization artifacts" | 5 — derivation and recomputation | DOM W7; EIC W8; DA M9 | must_fix | re_analysis: channel 3 | acceptance_criterion_unmet: dataset, channel 3 | P |
| R23 | Rename the channel as dry-season clear-sky surface temperature anomaly; state the linking assumption; validate or drop "thermal stress" | SC-29 | Major | text: §1 indicator table "Micro-urban heat island exposure, lack of shading, corrugated metal heat trapping" | 5 — thermal RS literature | PER W1 | must_fix | section: §1, §4.1, §5.3 | claim_scope_unsupported: claim, thermal exposure | W |
| R24 | Describe the composite accurately; harmonise tiers; revisit the window under ADR 0002 because the Tier 3 flag is true | SC-30 | Major | text: §3 dataset table, Landsat row "2022–2024 Composite" | 4 — compositing practice | PER W2 | must_fix | re_analysis: LST composite | interpretive_ambiguity_remains: dataset, LST composite | P |
| R25 | Test the thermal-inequality claim with socioeconomic data, or withdraw the injustice framing | SC-31 | Major | text: §4.1 item 5 "low-income settlements suffer disproportionately from Surface Urban Heat Islands (SUHI)" | 4 — EJ method | PER W6 | must_fix | new_data: socioeconomic linkage | claim_scope_unsupported: claim, §4.1 | W |
| R26 | Use a bare-earth DEM and correct the DKI slope statement | SC-14 | Major | text: §6.5 "yields $S_{>15^\circ} = 0.0\%$ across all of DKI Jakarta" | 4 — DEM characteristics | PER W9; MET W23; EIC W2 | must_fix | re_analysis: slope source | method_reproducibility_unresolved: dataset, slope channel | P |
| R27 | Measure slope at dwellings or decide to treat it as post hoc context, with the reason stated | SC-16 | Major | text: §2.2 Indicator 7 "The indicator measures the spatial percentage of cell $i$ occupied by terrain steeper than" | 4 — recomputed | PER W10; MET W11; EIC W12; DA M5 | must_fix | re_analysis: slope channel | interpretive_ambiguity_remains: dataset, slope channel | P |

### Required Item Details

**R1: Contribution**
- **Problem**: The named contributions are a definitional distinction and stratification, with no baseline comparison or outcome.
- **Source**: EIC W1.
- **Requirement**: State a research question and show what the feature set adds beyond density and a named baseline.
- **Acceptance criteria**: The report states one research question and reports a comparison against density and at least one named baseline on an independent outcome.

**R2: One reproducible run**
- **Problem**: Data sources, parameters and tables do not correspond to the repository.
- **Source**: EIC W2; MET W2; PER W5; DA M7.
- **Requirement**: Tag one run, publish its identifier, and regenerate all exhibits from it. State whether report or code was the intended specification for each row of the mismatch table.
- **Acceptance criteria**: Every table recomputes from the named run identifier, and failure to achieve this triggers MET's conditional conversion of D1 to fatal.

**R3: Crowding tail**
- **Problem**: The sub-5 m² tail and the Tambora and Penjaringan figures come from the filter.
- **Source**: EIC W3; MET W7; DOM W5, W6; DA C1.
- **Requirement**: Withdraw the claims, validate the filter against mapped land use, report with and without it, and treat zero-net-footprint cells as classification failures.
- **Acceptance criteria**: Footprint statistics appear with and without the filter, the claims are withdrawn or shown by actual boundary, and flagged cells are counted.

**R4: External validation**
- **Problem**: Susenas is called ground truth, but no comparison appears.
- **Source**: EIC W4; MET W16; DA M6.
- **Requirement**: Present the comparison with its unit list and failures, separate footprint from floor area, use finer tabulations where possible, and add known-group validation. Correct the Kota Tangerang mapping.
- **Acceptance criteria**: One comparison table lists every unit and construct, and it resolves the conflicting Spearman values in Disagreement 3.

**R5: Manila benchmark**
- **Problem**: The sole comparative figure has no verifiable source.
- **Source**: EIC W6; DOM W2; DA M8.
- **Requirement**: Compute the measure for a peer city with the same pipeline or remove the claim.
- **Acceptance criteria**: Each comparative figure traces to a verified source or a reported computation.

**R6: LCZ claim**
- **Problem**: DKI fractions fall outside the LCZ 3 range, and the cap is unsourced.
- **Source**: EIC W7; DOM W1; DA M8.
- **Requirement**: Withdraw the alignment or compute at appropriate scale, and discuss LCZ 6 and LCZ 7.
- **Acceptance criteria**: The report no longer claims LCZ 3 alignment unless published class ranges support it at the stated scale.

**R7: Strata**
- **Problem**: Reported strata differ from their stated composition.
- **Source**: EIC W9; MET W21.
- **Requirement**: Define strata from official boundaries, resolve the 870 unassigned cells, and add a sensitivity check.
- **Acceptance criteria**: Stratum membership is listed by administrative unit and reproduces the reported counts.

**R8: Amenity channel**
- **Problem**: The measure counts everyday destinations and ignores demand.
- **Source**: EIC W11; MET W17.
- **Requirement**: Separate formal-service and everyday counts, add a per-capita or floating-catchment form, and use population-weighted origins.
- **Acceptance criteria**: The channel definition, POI set and cutoff in the report match the run, and separate counts are reported.

**R9: Hazard construct**
- **Problem**: Flood and subsidence dominate hazard here and are absent.
- **Source**: EIC W12; PER W8.
- **Requirement**: Add suitable flood and subsidence layers, or narrow the construct, and disclose the retirement of `water_frequency`.
- **Acceptance criteria**: The hazard dimension's stated scope matches the layers used, and the retired signal is disclosed.

**R10: Internal arithmetic**
- **Problem**: Text and tables conflict.
- **Source**: EIC W14; MET W3, W18, W21, W24.
- **Requirement**: Rebuild all numbers from one source and check text against tables.
- **Acceptance criteria**: Stratum means reweight to global means, and the density, geometry and fringe-share figures are arithmetically consistent.

**R11: References**
- **Problem**: Several DOIs fail or resolve to unrelated papers.
- **Source**: EIC W15; DOM W2, W8–W10; DA M12.
- **Requirement**: Verify every entry and remove unsupported claims.
- **Acceptance criteria**: Every citation resolves to the cited work, and each attributed claim has been checked against its source.

**R12: Channel 1**
- **Problem**: The matrix keeps the quantity §6.2 condemns, saturated at the upper bound.
- **Source**: MET W1, W8; EIC W2; DA M3.
- **Requirement**: State the true channel and replace or justify it, considering R14.
- **Acceptance criteria**: The report's feature vector equals the matrix columns, and the channel is not dominated by clipping at its bound.

**R13: Thermal baseline**
- **Problem**: Neither the stated nor the implemented baseline reproduces the reported table, and the background mixes uplands.
- **Source**: MET W4; PER W4, W5.
- **Requirement**: Specify one baseline, use a lowland reference, show sensitivity, and treat implausible cells.
- **Acceptance criteria**: Reported ΔLST values recompute from the stated baseline, and contaminated cells are excluded or flagged.

**R14: Dasymetric dependence**
- **Problem**: The denominator is still GHS-POP, and the indicator re-expresses inverse density.
- **Source**: MET W5, W6; DOM W5; DA C2.
- **Requirement**: Retract the claims and use an independent denominator, or restrict inference to census-unit scale.
- **Acceptance criteria**: "Eliminates" and "model-free" are gone, and the crowding measure uses an independent denominator or claims only census-unit scale.

**R15: Settlement claims**
- **Problem**: Cell statistics are read as settlement and household conditions.
- **Source**: MET W10; DOM W6; PER W6, W15.
- **Requirement**: Remove composed settlement profiles and correct the location of maxima.
- **Acceptance criteria**: No statement attributes a 74 ha statistic to a named kampung without settlement-boundary evidence.

**R16: Zero inflation**
- **Problem**: Amenity and slope have large spikes under min-max scaling.
- **Source**: MET W11.
- **Requirement**: Adopt a two-part or zero-inflated treatment.
- **Acceptance criteria**: The chosen treatment is specified per channel and the distinct meaning of zeros is stated.

**R17: Spatial dependence**
- **Problem**: Autocorrelation is unquantified.
- **Source**: MET W12.
- **Requirement**: Report dependence and use spatially blocked hold-out.
- **Acceptance criteria**: Moran's I and effective sample size are reported and the modelling plan uses blocked hold-out.

**R18: Density dominance**
- **Problem**: Channels share a dominant density factor, and independence is untested.
- **Source**: MET W13; EIC W1; DA M1.
- **Requirement**: Report variance explained, overall and by stratum, and fix a density baseline.
- **Acceptance criteria**: The report presents channel-level variance explained by density and distance in blocked validation.

**R19: Scaling and disparity function**
- **Problem**: Bounds, clipping and aggregation are unreported and undefined.
- **Source**: MET W14; DA M2.
- **Requirement**: Publish transforms and bounds, resolve provisional ones, and define the disparity function with sensitivity.
- **Acceptance criteria**: Each channel's bounds and clip share are published and results are shown under alternative weightings and directions.

**R20: Missingness**
- **Problem**: LST gaps fall on the north coast, and N is misreported.
- **Source**: MET W15; PER W3; DA M11.
- **Requirement**: State the modelled universe, report coverage by unit, diagnose the mask, and treat the gap.
- **Acceptance criteria**: Coverage by unit is published and results include a sensitivity to the treatment of missing LST.

**R21: Residential mask**
- **Problem**: The stated mask is absent, and no binary mask handles mixed use.
- **Source**: DOM W4; EIC W2.
- **Requirement**: Describe the real mask and validate a partial weight on a labelled sample.
- **Acceptance criteria**: The mask text matches the run and reports validation against a labelled sample.

**R22: Compactness**
- **Problem**: The channel does not discriminate, and the stated replacement flags narrow formal plots.
- **Source**: DOM W7; EIC W8; DA M9.
- **Requirement**: Remove it, and validate any replacement. DOM's candidate is median footprint area.
- **Acceptance criteria**: The channel is removed or replaced, and any replacement is shown to separate known groups.

**R23: Thermal framing**
- **Problem**: Skin temperature is presented as human heat exposure.
- **Source**: PER W1.
- **Requirement**: Rename, state the link, and validate or drop the language.
- **Acceptance criteria**: "Thermal stress" and "acute hazard" are removed unless validated against air temperature or a heat-stress index.

**R24: Composite**
- **Problem**: The composite is effectively one dry season, and tiers are not interchangeable.
- **Source**: PER W2.
- **Requirement**: Describe it accurately, harmonise tiers, and apply ADR 0002.
- **Acceptance criteria**: Window shares are reported and the Tier 3 flag is resolved under ADR 0002 before training.

**R25: Inequality claim**
- **Problem**: Thermal inequality is asserted but not tested.
- **Source**: PER W6.
- **Requirement**: Test with socioeconomic data and a stated measure, or withdraw it.
- **Acceptance criteria**: A disparity statistic is reported or the injustice framing is absent from the report.

**R26: DEM**
- **Problem**: GLO-30 is a surface model, and non-zero slope tracks tall buildings.
- **Source**: PER W9; MET W23; EIC W2.
- **Requirement**: Use a bare-earth DEM and correct §6.5.
- **Acceptance criteria**: The slope channel derives from a named bare-earth DEM, and the DKI statement matches the outputs.

**R27: Slope form**
- **Problem**: The channel records uninhabited upland terrain.
- **Source**: PER W10; MET W11; EIC W12; DA M5.
- **Requirement**: Intersect with dwellings or move to post hoc context, and state the reason (Disagreement 2).
- **Acceptance criteria**: The report states where slope enters the model and why, with slope measured at dwellings if it stays in the embedding.

## Suggested Revisions (Should Fix)

| Transport ref | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Obligation class | Cost scope | Bounded consequence | Timing |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | Validate POIs against Podes, facility and school registers; correct the §6.6 diagnosis for Overture | SC-32 | Major | text: §6.6 "Rural and low-income areas have lower mapping completeness" | 4 — within-bin recomputation | EIC W5 | should_fix | new_data: registers | evidence_gap_remains: section, §6.6 | P |
| S2 | Apply the pipeline to a peer city, or limit transfer claims and separate universal from local parameters | SC-33 | Major | absence: Sections 1 to 6 — expected a second-city application or a reasoned transfer analysis of the feature definitions; checked Executive Summary, Section 4.1, Section 5, Section 6 and the dataset table | 4 — comparative knowledge | EIC W8 | should_fix | new_data: peer city | claim_scope_unsupported: claim, transfer | W |
| S3 | Reconcile population with kecamatan and desa counts, with sensitivity to population source | SC-34 | Major | table: §5.3 row "2023 Population" | 3 — secondary web sources | EIC W10 | should_fix | re_analysis: denominators | evidence_gap_remains: table, Table 5.3 | P |
| S4 | Remove §7 and integrate with modelling, or recast as a validated data descriptor | SC-35 | Major | text: Header "Feature Engineering & Pre-Modeling Methodological Audit" | 4 — editorial judgement | EIC W13 | should_fix | section: §7, structure | editorial_conformance_unmet: manuscript | W |
| S5 | Describe compactness in morphological terms only | SC-36 | Minor | text: §1 "Lower $C$ $\to$ Organic Informal Slum Morphology" | 4 — §6.3 and recomputation | EIC W16 | should_fix | sentence: §1 table | claim_scope_unsupported: table, indicator inventory | W |
| S6 | State one threshold and its scope, and stop applying living-area standards to ground footprint | SC-19 | Minor (DA M10 Major) | text: §4.1 "living area drops below $5.0\text{ m}^2/\text{person}$" | 4 — validation module uses 7.2 m² | EIC W17; MET W25; DOM W5; DA M10 | should_fix | sentence: §4.1, §6.2 | claim_scope_unsupported: claim, overcrowding threshold | W |
| S7 | Add maps of each indicator, strata and missing data | SC-37 | Minor | absence: Section 5 — expected at least one map of indicators or strata with legend and scale; checked all sections, the ASCII diagrams and the exhibits | 5 — direct inspection | EIC W18 | should_fix | section: §5 | reader_traceability_reduced: manuscript | W |
| S8 | Report results at other resolutions and zonings; scope resolution 8 to neighbourhood screening | SC-38 | Major | text: §6.4 "potentially underestimating the severity of localized deprivation" | 5 — direct analysis | MET W9 | should_fix | re_analysis: MAUP | evidence_gap_remains: section, §6.4 | P |
| S9 | State the residential rule actually used and report mask sensitivity | SC-39 | Minor | equation: §2.1 residential filter Pop_i ≥ 50 AND A_bldg,res,i > 0 | 5 — recomputation | MET W19 | should_fix | sentence: §2.1 | reporting_requirement_unmet: section, §2.1 | W |
| S10 | Rename the vegetation channel, add a water mask, settle direction, and add canopy, land-use and access layers | SC-23 | Minor (PER W11 Major) | table: Section 1 indicator inventory, row 5 (Vegetation Cover Fraction) | 5 — definition check | MET W20; PER W11, W12 | should_fix | re_analysis: vegetation channel | interpretive_ambiguity_remains: dataset, vegetation channel | P |
| S11 | Disclose the eave correction and centroid assignment; keep or remove the deduction by explicit decision | SC-24 | Minor (DOM W3 Major) | equation: §2.2 Indicator 1, numerator Area(B_k ∩ H_i) | 5 — code inspection | MET W22; DOM W3 | should_fix | section: §2.2 | reporting_requirement_unmet: section, §2.2 | P |
| S12 | Support or remove the premise that informal footprints are tortuous | SC-40 | Major | text: §4.1 "resulting in highly non-convex, tortuous polygon boundaries" | 4 — literature, two DOIs | DOM W8 | should_fix | section: §4.1 | claim_scope_unsupported: claim, §4.1 | W |
| S13 | Correct the regularisation attribution, the 0.45–0.65 range, the land-cover versus impervious statement and the GHS epochs | SC-41 | Minor | text: §6.3 "such as Mask R-CNN in Open Buildings v3" | 4 — automated extraction | DOM W9–W12 | should_fix | sentence: §3, §4.1, §6.1, §6.3 | editorial_conformance_unmet: manuscript | W |
| S14 | Add a physical-plausibility check on plan area fraction | SC-42 | Minor | absence: §2.2 and §5 — expected a check that cell plan area fractions are physically possible; checked the plan area equation, Table 5.2, Table 5.3 and §6.1 | 5 — direct recomputation | DOM W13 | should_fix | re_analysis: QA | evidence_gap_remains: dataset, plan area | P |
| S15 | Correct roof physics, quote the regulatory clause, state the slope algorithm, and drop "micro-scale" | SC-43 | Minor | text: §4.1 item 5 "dense corrugated iron or zinc roofing, high thermal mass" | 4 — radiometry | PER W7, W13–W15 | should_fix | sentence: §2.2, §4.1, Executive Summary | editorial_conformance_unmet: manuscript | W |
| S16 | State permitted users, scale of use and misuse risks of hazard and deprivation labels | SC-44 | Minor | absence: §4 to §6 — expected discussion of users, scale of use and harms of hazard or deprivation labels for kampung residents; checked §4.1, §5.4, §6.1 to §6.6, and the §7.1 question list | 3 — outside core expertise | PER W16 | consider | section: limitations | reporting_requirement_unmet: manuscript | W |
| S17 | Classify channels as modifiable, partly modifiable or fixed context, and separate fixed context from the disparity score | — | Major | absence: Sections 1 to 7 of the report — expected a mapping from each indicator to a planning instrument, responsible agency, and responsiveness to intervention; checked Executive Summary, Section 4 justifications, Section 6 limitations, Section 7 protocol | 4 — full-text check | DA M4 | should_fix | section: new actionability section | evidence_gap_remains: claim, policy relevance | W |

## Source-Traceability Checklist

Source order. This is not a suggested work order; author triage is collected separately.

- [ ] R1 — obligation `must_fix`: contribution and baseline
- [ ] R2 — obligation `must_fix`: one frozen run, regenerated exhibits
- [ ] R3 — obligation `must_fix`: non-residential filter and crowding claims
- [ ] R4 — obligation `must_fix`: Susenas comparison and validation
- [ ] R5 — obligation `must_fix`: Manila benchmark
- [ ] R6 — obligation `must_fix`: LCZ claim
- [ ] R7 — obligation `must_fix`: strata
- [ ] R8 — obligation `must_fix`: amenity channel
- [ ] R9 — obligation `must_fix`: hazard construct
- [ ] R10 — obligation `must_fix`: internal arithmetic
- [ ] R11 — obligation `must_fix`: references
- [ ] R12 — obligation `must_fix`: channel 1
- [ ] R13 — obligation `must_fix`: thermal baseline
- [ ] R14 — obligation `must_fix`: dasymetric dependence
- [ ] R15 — obligation `must_fix`: settlement claims
- [ ] R16 — obligation `must_fix`: zero inflation
- [ ] R17 — obligation `must_fix`: spatial dependence
- [ ] R18 — obligation `must_fix`: density dominance
- [ ] R19 — obligation `must_fix`: scaling and disparity function
- [ ] R20 — obligation `must_fix`: missingness
- [ ] R21 — obligation `must_fix`: residential mask
- [ ] R22 — obligation `must_fix`: compactness
- [ ] R23 — obligation `must_fix`: thermal framing
- [ ] R24 — obligation `must_fix`: composite and tiers
- [ ] R25 — obligation `must_fix`: inequality claim
- [ ] R26 — obligation `must_fix`: DEM
- [ ] R27 — obligation `must_fix`: slope form
- [ ] S1 — obligation `should_fix`: POI coverage
- [ ] S2 — obligation `should_fix`: transferability
- [ ] S3 — obligation `should_fix`: population reconciliation
- [ ] S4 — obligation `should_fix`: document form
- [ ] S5 — obligation `should_fix`: morphological labels
- [ ] S6 — obligation `should_fix`: threshold
- [ ] S7 — obligation `should_fix`: maps
- [ ] S8 — obligation `should_fix`: MAUP
- [ ] S9 — obligation `should_fix`: residential rule
- [ ] S10 — obligation `should_fix`: vegetation channel
- [ ] S11 — obligation `should_fix`: eave correction
- [ ] S12 — obligation `should_fix`: tortuosity premise
- [ ] S13 — obligation `should_fix`: factual corrections
- [ ] S14 — obligation `should_fix`: plausibility check
- [ ] S15 — obligation `should_fix`: thermal and slope details
- [ ] S16 — obligation `consider`: harms of labels
- [ ] S17 — obligation `should_fix`: actionability

## Journal-Supplied Deadline

- **Exact deadline from source letter**: `NOT PROVIDED`

## Response Letter Instructions

Please respond to every item using `templates/revision_response_template.md`, with the adopted change or the reason for not adopting it, and mark changes in the revised report. For each row of the mismatch table, state whether the report or the code was the intended specification.

## Closing

We encourage you to consider the reviewers' comments carefully and to submit a substantially revised report. The revised report will undergo another round of review. We suggest that the before-modelling items be settled first, so that the Graph Neural Network is trained on a feature store the report describes.

Sincerely,
Editorial Synthesizer

---

# Part 3: Reviewer Report Summary (Appendix)

Recommendation enums are given only where the Phase 2 card states one. Confidence is per finding and is shown in the roadmap.

| Seat | Stated signal | Scores | Key point |
|---|---|---|---|
| EIC | Overall signal: Major Revision | D5 block; D6 block (repairable) | Contribution is asserted and not demonstrated, and the manuscript does not describe the analysis in the repository (W1, W2) |
| MET | No recommendation enum on the card | D1 block (repairable, conditional); D3 block (repairable) | The built feature vector is not the reported one, and channel 1 is the indicator the report calls circular (W1) |
| DOM | No recommendation enum on the card | D2 block (repairable) | The LCZ 3 alignment and aggregation cap are not in the source and are contradicted by its table (W1) |
| PER | No recommendation enum on the card | D4 block | Surface temperature is read as human heat exposure with no stated link or validation (W1) |
| DA | N/A — findings only | D3 block (repairable) | The flagship crowding result is a filter artefact, and the dasymetric loop is not removed (C1, C2) |

---

## Attachment: Suggested-Reference Check (advisory, #1001)

Suggested-reference check (script output, not a reviewer finding; #1001)
Seats read: R2, R3 (complete).

| Seat | # | Reference | Result |
|---|---|---|---|
| R2 | 1 | Stewart, I. D. et al. (2012) "Local Climate Zones for Urban Temperature Studies" doi:10.1175/BAMS-D-11-00019.1 | Found in an index |
| R2 | 2 | Taubenböck, H. et al. (2014) "The physical face of slums: a structural comparison of slums in Mumbai, India, based on remotely sensed data" doi:10.1007/s10901-013-9333-x | Found in an index |
| R2 | 3 | Taubenböck, H. et al. (2018) "The morphology of the Arrival City - A global categorization based on literature surveys and remotely sensed data" doi:10.1016/j.apgeog.2018.02.002 | Found in an index |
| R2 | 4 | Funo, S. et al. (2002) "Typology of Kampung Houses and Their Transformation Process" doi:10.3130/jaabe.1.2\_193 | Found in an index |
| R2 | 5 | Tipple, G. (2005) "The Place of Home-based Enterprises in the Informal Sector" doi:10.1080/00420980500060178 | DOI or arXiv ID not found, and no title match |
| R2 | 6 | Kusno, A. (2013) "The Shophouse and the Chinese (in After the New Order)" doi:10.21313/hawaii/9780824837457.003.0002 | Found in an index |
| R2 | 7 | Fleischmann, M. (2019) "momepy: Urban Morphology Measuring Toolkit" doi:10.21105/joss.01807 | Found in an index |
| R2 | 8 | Biljecki, F. et al. (2022) "Global Building Morphology Indicators" doi:10.1016/j.compenvurbsys.2022.101809 | Found in an index |
| R2 | 9 | Demuzere, M. et al. (2022) "A global map of local climate zones to support earth system modelling and urban-scale environmental science" doi:10.5194/essd-14-3835-2022 | Found in an index |
| R2 | 10 | Estoque, R. C. et al. (2017) "Effects of landscape composition and pattern on land surface temperature: An urban heat island study in the megacities of Southeast Asia" doi:10.1016/j.scitotenv.2016.10.195 | Found in an index |
| R2 | 11 | Sirko, W. et al. (2021) "Continental-Scale Building Detection from High Resolution Satellite Imagery" arXiv:2107.12283 | Found in an index |
| R3 | 1 | Venter, Z. S. (2021) "Crowdsourced air temperatures contrast satellite measures of the urban heat island and its mechanisms" doi:10.1126/sciadv.abb9569 | Found in an index |
| R3 | 2 | Chakraborty, T. (2022) "Lower Urban Humidity Moderates Outdoor Heat Stress" doi:10.1029/2022AV000729 | Found in an index |
| R3 | 3 | Ramsay, E. E. (2021) "Chronic heat stress in tropical urban informal settlements" doi:10.1016/j.isci.2021.103248 | Found in an index |
| R3 | 4 | Kuras, E. R. (2017) "Opportunities and Challenges for Personal Heat Exposure Research" doi:10.1289/ehp556 | Found in an index |
| R3 | 5 | Weng, Q. (2014) "Modeling annual parameters of clear-sky land surface temperature variations and evaluating the impact of cloud cover using time series of Landsat TIR data" doi:10.1016/j.rse.2013.09.002 | Found in an index |
| R3 | 6 | Bechtel, B. (2015) "A New Global Climatology of Annual Land Surface Temperature" doi:10.3390/rs70302850 | Found in an index |
| R3 | 7 | Malakar, N. K. (2018) "An Operational Land Surface Temperature Product for Landsat Thermal Data: Methodology and Validation" doi:10.1109/tgrs.2018.2824828 | Found in an index |
| R3 | 8 | Laraby, K. G. (2018) "Uncertainty estimation method and Landsat 7 global validation for the Landsat surface temperature product" doi:10.1016/j.rse.2018.06.026 | Found in an index |
| R3 | 9 | Estoque, R. C. (2017) "Effects of landscape composition and pattern on land surface temperature: An urban heat island study in the megacities of Southeast Asia" doi:10.1016/j.scitotenv.2016.10.195 | Found in an index |
| R3 | 10 | Harlan, S. L. (2006) "Neighborhood microclimates and vulnerability to heat stress" doi:10.1016/j.socscimed.2006.07.030 | Found in an index |
| R3 | 11 | Abidin, H. Z. (2011) "Land subsidence of Jakarta (Indonesia) and its relation with urban development" doi:10.1007/s11069-011-9866-9 | Found in an index |
| R3 | 12 | Budiyono, Y. (2015) "Flood risk assessment for delta mega-cities: a case study of Jakarta" doi:10.1007/s11069-014-1327-9 | Found in an index |
| R3 | 13 | Padawangi, R. (2015) "Water, Water Everywhere: Toward Participatory Solutions to Chronic Urban Flooding in Jakarta" doi:10.5509/2015883517 | Found in an index |
| R3 | 14 | Hawker, L. (2022) "A 30 m global map of elevation with forests and buildings removed" doi:10.1088/1748-9326/ac4d4f | Found in an index |
| R3 | 15 | Huete, A. (2002) "Overview of the radiometric and biophysical performance of the MODIS vegetation indices" doi:10.1016/s0034-4257(02)00096-2 | Found in an index |
| R3 | 16 | Carlson, T. N. (1997) "On the relation between NDVI, fractional vegetation cover, and leaf area index" doi:10.1016/s0034-4257(97)00104-1 | Found in an index |
| R3 | 17 | Hope, D. (2003) "Socioeconomics drive urban plant diversity" doi:10.1073/pnas.1537557100 | Found in an index |
| R3 | 18 | Schwarz, K. (2015) "Trees Grow on Money: Urban Tree Canopy Cover and Environmental Justice" doi:10.1371/journal.pone.0122051 | Found in an index |
| R3 | 19 | Wolch, J. R. (2014) "Urban green space, public health, and environmental justice: The challenge of making cities just green enough" doi:10.1016/j.landurbplan.2014.01.017 | Found in an index |

"Found" means an index holds a record with this DOI or arXiv ID and title, or with this title. It does not show that the work supports the recommendation, or that the authors and year are right.

---

## Attachment: Reviewer Claim Check (advisory, #1002)

The judge answered 86 of 86 findings from 5 reviewers: it marked 4 as contradicted, and 53 cannot be checked from the manuscript alone.

The judge marked these findings as contradicted by the manuscript. The script checked only the words of each quote: that they occur in the manuscript, or, for words the finding quotes, that they do not. The judge gave the locations, and the script did not check them. Read each quote to decide:
- Journal-Fit Reviewer · W7: Alignment with LCZ 3 is contradicted by the reported values
  > “Local Climate Zone (LCZ) literature (\[Stewart &amp; Oke, 2012\](https://doi.org/10.1175/BAMS-D-11-00019.1)) notes that while LCZ 3 (Compact Low-Rise) reaches $40\\%\\text{--}70\\%$ building coverage at the micro-block scale” (Section 6.1, Literature Reality)
- Reviewer 1 · W15: Missingness is undisclosed and is not random
  > “5.2 Unstratified Distribution (All 9,345 Residential Cells)” (Section 5.2 heading)
- Devil's Advocate · M8: The headline alignment is not supported. DKI coverage of 21.88 to 28.75% lies below the LCZ 3 range of 40 to 70% in Stewart and Oke (2012) and within the LCZ 6 open low-rise range of 20 to 40%. The stated 40 to 48% aggregation cap has no source and matches the study's own 48.2% maximum. The Manila source does not resolve to any matching paper. Some dilution at 74 ha is plausible, but it is not shown.
  > “Local Climate Zone (LCZ) literature (\[Stewart &amp; Oke, 2012\](https://doi.org/10.1175/BAMS-D-11-00019.1)) notes that while LCZ 3 (Compact Low-Rise) reaches $40\\%\\text{--}70\\%$ building coverage at the micro-block scale” (Section 6.1, Literature Reality)
- Devil's Advocate · M4: Actionability is never addressed. No indicator is tied to a planning instrument, agency, or responsiveness to intervention. Slope is fixed, compactness carries no lever, reducing plan area conflicts with proximity, and the 74 ha cell is not a planning unit.
  > “Indonesian national spatial planning guidelines (SNI 03-1733-2004 / Ministry of Public Works Regulation No. 20/PRT/M/2007) designate slopes above $15^\\circ$ as restricted for standard residential construction.” (Section 4.1, item 6)

The author decides what to do with each row. This check does not change the decision, the consensus counts, or the Revision Roadmap. The judge is the session model; as this judge, the #1002 contrast test passed Claude Opus 5.5 and Claude Fable 5.1 (gpt-6-astra and Gemini 4 Argon passed it in part one, through other transports); other models are untested.

---

## Attachment: Acronym Check (advisory, #849)

### Acronym check (advisory; no reply needed)
Coverage: body (partial)
Not in this input: English abstract, Chinese abstract.

| Scope | Line | Rule | Acronym | Uses |
|---|---|---|---|---|
| Body | 25 | Not defined | DKI | 7 |
| Body | 65 | Not defined | BUILT | 3 |
| Body | 65 | Not defined | GHS | 7 |
| Body | 72 | Not defined | ML | 2 |
| Body | 83 | Not defined | POI | 3 |
| Body | 104 | Not defined | TIRS | 1 |
| Body | 107 | Not defined | LST | 2 |
| Body | 110 | Not defined | FABDEM | 2 |
| Body | 110 | Not defined | GLO | 2 |
| Body | 152 | Not defined | AEROBF | 1 |
| Body | 152 | Not defined | CO | 1 |
| Body | 161 | Not defined | BSD | 1 |
| Body | 170 | Not defined | PRT | 1 |
| Body | 170 | Not defined | SNI | 1 |
| Body | 246 | Not defined | ESA | 1 |
| Body | 246 | Not defined | MODIS | 1 |
| Body | 248 | Defined again | LCZ | 3 |
| Body | 252 | Not defined | POP | 3 |
| Body | 259 | Not defined | CNN | 1 |
| Body | 267 | Not defined | DEM | 4 |
| Body | 295 | Not defined | MAUP | 2 |
| Body | 318 | Not defined | BPS | 1 |
| Body | 319 | Not defined | OSM | 1 |
| Body | 369 | Not defined | ONE | 1 |
| Body | 369 | Not defined | PLoS | 1 |
| Body | 375 | Not defined | VHR | 1 |
| Body | 376 | Not defined | SDG | 2 |
| Body | 379 | Not defined | GIS | 1 |
