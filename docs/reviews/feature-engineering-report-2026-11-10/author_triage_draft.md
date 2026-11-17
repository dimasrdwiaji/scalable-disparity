# Author triage (working draft, recorded during revision coaching)

Source: the author's own replies in the coaching session following the 2026-11-10 review. Item IDs refer to the Revision Roadmap in `editorial_decision_letter.md`. This is not the formal `author-adjudication/1.0` sidecar; it is the running record from which that sidecar can be produced. Nothing here is inferred: an item with no disposition has not been decided.

## Design decisions stated by the author

1. Each indicator should show whether a neighbourhood is better or worse than its neighbours, and by how much. A composite index is built afterwards.
2. All pipeline inputs must be globally open so the workflow transfers to other regions. Local data may be used for validation.
3. Meta RWI is not to be used at all, neither as an input nor for validation. Validation is against Kotaku.
4. VIIRS is not accepted as the socioeconomic indicator. (Screening note, not the author's: in Karawang VIIRS ranked Kotaku slum cells as brighter than other cells.)
5. The paper may claim physical living-environment disparity, with the composite built from separately validated dimensions.
6. Disparity scaling with density is acceptable; the density-independence test is not a pass/fail requirement.
7. The author would still like a socioeconomic indicator eventually. The slot stays open; no candidate is committed.

8. The per-person living-space indicator is dropped from the cell-level set.

9. Heat and slope stay as indicators. NDVI is named by the author as the environmental indicator. Flood is undecided: essential for Jabodetabek, unsure about other regions.

10. Keep the design as tight as possible. Flood is handled as an optional regional module outside the portable core (the author's wording: "if flood were to be unconvincing, remove it"). The same rule applies to the optional socioeconomy slot ("goes with the other as well"): it is dropped if it does not convince.

Not yet decided by the author: the direction of the accessibility indicator.

11. Response to the Devil's Advocate's strongest counter-argument (the features largely track built-up density): the author agrees it is not wrong, noting that many similar projects and rural-urban datasets follow the rural-urban divide, which follows density. The author is not yet sure how to make the work stand out and plans a much deeper dive into the topic and the available datasets before deciding.

## Dispositions

| Theme | Item | Disposition |
|---|---|---|
| A | R3 | will_address |
| A | R12 | will_address |
| A | R14 | will_address |
| A | R15 | will_address |
| A | S3 | will_address |
| A | S6 | will_address |
| B | R2 | will_address |
| B | R7 | will_address |
| B | R10 | will_address |
| B | S9 | will_address |
| B | S13 | will_address |
| C | R8 | will_address |
| C | S1 | will_address |
| D | R9 | will_address |
| D | R13 | will_address |
| D | R23 | will_address |
| D | R24 | will_address |
| D | R25 | will_address |
| D | R26 | will_address |
| D | R27 | will_address |
| D | S10 | will_address |
| D | S15 | will_address |
| E | R21 | will_address |
| E | R22 | will_address |
| E | S5 | will_address |
| E | S11 | will_address |
| E | S12 | will_address |
| E | S14 | will_address |
| F | R4 | will_address (on the basis that Susenas is only a coarse comparison because the data is too coarse, and Kotaku is the validation) |
| F | R17 | deferred (author undecided; "a much later part of the research") |
| F | R18 | deferred (author undecided; "a much later part of the research") |
| F | S8 | deferred (author undecided; "a much later part of the research") |
| G | R1 | will_address |
| G | R5 | will_address |
| G | R6 | will_address |
| G | R11 | will_address |
| G | S2 | will_address |
| G | S4 | will_address |
| G | S7 | will_address |
| G | S16 | will_address |
| G | S17 | will_address |
| H | R16 | will_address |
| H | R19 | will_address |
| H | R20 | will_address |
