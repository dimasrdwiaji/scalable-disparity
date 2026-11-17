# Literature Review Blueprint (Option A — Revised Study)

**Date:** 2026-11-15  
**Review Form:** Targeted, claim-auditing two-part thematic synthesis (`lit-review` mode)  
**Evidence Labels:** `[Established]` | `[Conditional]` | `[Contradicted]`  
**Citation Ledger:** All citations below are verified in [references_verified.md](./references_verified.md).

---

## Section 2.0 Geographic & Conceptual Framing (Variable-Selection Justification)
- **Urban Fragmentation Context:** In Global South megacities such as Jakarta, luxury residential clusters and high-rise developments sit directly beside dense informal *kampungs* ([Mardhotillah & Gamal, 2018](https://doi.org/10.14716/ijtech.v9i7.2519); [Wardhani, 2016](https://doi.org/10.18196/jgp.2016.0025); [Hidayati et al., 2020](https://doi.org/10.1080/17549175.2020.1814391)), motivating automated open-data detection of intra-urban physical deprivation and neighborhood boundaries.
- **Role of Section 2 in the Paper:** Rather than treating density confounding as the paper's sole theme, Section 2 provides the **scholarly justification for indicator selection**—explaining why commonly used open proxies mislead at neighborhood scale (Part 1) and why each chosen physical/micro-environmental dimension isolates a distinct facet of built and environmental disparity (Part 2).
- **Core Argument:** Separate *area-level physical built/environmental deprivation* from income, household crowding, and generic service proximity ([Thomson et al., 2020](https://doi.org/10.3390/socsci9050080); [Abascal et al., 2022a](https://doi.org/10.1016/j.compenvurbsys.2022.101770); [MHCLG, 2019](https://www.gov.uk/government/statistics/english-indices-of-deprivation-2019)).
- **Global South vs. Global North Contrast:** In Southeast Asian megacities such as Jakarta, *kampungs* sit inside dense, mixed-use cores with high pedestrian proximity to amenities ([Hidayati et al., 2020](https://doi.org/10.1080/17549175.2020.1814391)), inverting Global North "service desert" assumptions behind 15-minute-city counts ([Moreno et al., 2021](https://doi.org/10.3390/smartcities4010006)).

---

## Part 1: Why Macro-Density & Naive Open Proxies Mislead Deprivation Mapping

### 2.1 "Density ≠ Inequality": Three Confounding Mechanisms
1. **Construct Conflation (`[Established]`):** High structural density coexists with both planned high-rise/compact districts and informal *kampungs* ([Taubenböck et al., 2018](https://doi.org/10.1016/j.apgeog.2018.02.002); [Abascal et al., 2022a](https://doi.org/10.1016/j.compenvurbsys.2022.101770); [Lilford et al., 2017](https://doi.org/10.1016/S0140-6736(16)31848-7)).
2. **Dasymetric & Scale Circularity (`[Conditional — Thinner Direct Audit Literature]`):** `GHS-POP` / `WorldPop` disaggregate census totals using building volume and RS covariates ([Stevens et al., 2015](https://doi.org/10.1371/journal.pone.0107042); [Schiavina et al., 2023](https://doi.org/10.2760/098587); [Pesaresi et al., 2024](https://doi.org/10.1080/17538947.2024.2390454)). *Gap note:* Explicit empirical audits proving intra-urban circularity when dividing `GHS-POP` by `GHS-BUILT` inside deprivation indices are sparse in published literature, making our Jabodetabek screen a direct contribution.
3. **Regime & Ecological Inversion (`[Established]`):** `NDVI`, `LST`, `VIIRS`, and `POI` density invert sign across urban cores vs. rural/floodplain regimes ([Stewart & Oke, 2012](https://doi.org/10.1175/BAMS-D-11-00019.1); [Chakraborty & Lee, 2019](https://doi.org/10.1016/j.jag.2018.09.015); [Gibson et al., 2021](https://doi.org/10.1016/j.jdeveco.2020.102602)).

### 2.2 Five Technical Proxy Failure Classes (+ `Meta RWI` Boundary)
- **(a) Dasymetric Living-Space Ratio (`GHS-POP` / `R_space` / `9.0 m²`) — `[Contradicted]`:** Reconstructs building-volume scaling rather than household crowding ([Schiavina et al., 2023](https://doi.org/10.2760/098587); [Pesaresi et al., 2024](https://doi.org/10.1080/17538947.2024.2390454)).
- **(b) Nighttime Lights (`VIIRS`) — `[Contradicted Intra-Urban]`:** Blooming/overflow and core saturation obscure dark informal pockets inside bright cities and track urban intensity ([Gibson et al., 2021](https://doi.org/10.1016/j.jdeveco.2020.102602); [JSTARS, 2018](https://doi.org/10.1109/JSTARS.2018.2830336); [RS, 2017](https://doi.org/10.3390/rs9020197)).
- **(c) Coarse Atmospheric, Thermal & DSM Products (`Sentinel-5P`, `MODIS 1 km`, `GLO-30`) — `[Contradicted for Neighborhood Scale]`:** Coarse `PM2.5` (`~1–5 km`) ([van Donkelaar et al., 2021](https://doi.org/10.1021/acs.est.1c05309)), `1 km` thermal smearing ([Voogt & Oke, 2003](https://doi.org/10.1016/S0034-4257(03)00079-8)), and DSM building-height-as-slope confounding ([Hawker et al., 2022](https://doi.org/10.1088/1748-9326/ac4d4f)).
- **(d) Open VGI / POI Accessibility (`OSM` & `Overture`) — `[Contradicted as Deprivation Score]`:** VGI completeness varies across wealth and city tiers ([Barrington-Leigh & Millard-Ball, 2017](https://doi.org/10.1371/journal.pone.0180698); [Herfort et al., 2023](https://doi.org/10.1038/s41467-023-39698-6); [Overture Schema](https://docs.overturemaps.org)), while proximity without affordability/quality leaves *kampung* residents as "captive pedestrians" ([Hidayati et al., 2020](https://doi.org/10.1080/17549175.2020.1814391)). *(`OSM` parks excluded.)*
- **(e) Unmasked Building Coverage (`plan_area_frac`) — `[Conditional]`:** Mixes industrial/commercial footprints with housing ([Jochem et al., 2021](https://doi.org/10.1177/2399808320921208); [Chamberlain et al., 2024](https://doi.org/10.1016/j.compenvurbsys.2024.102104); [Sirko et al., 2021](https://arxiv.org/abs/2107.12283)).
- **Scope Boundary (`Meta RWI`):** Excluded ([Chi et al., 2022](https://doi.org/10.1073/pnas.2113658119)) because it predicts survey asset wealth from connectivity/device signals rather than direct physical living conditions.

---

## Part 2: Density-Orthogonal Alternatives, Inequality, & Boundary GeoAI

### 2.3 Residential-Masked Micro-Morphology & Roof-Material Contrast
- **Micro-Morphology (`[Established]`):** Masked small footprint grain (`< 50 m²`), tight nearest-neighbor spacing, and non-residential separation discriminate informal settlements inside dense cores ([Kuffer et al., 2016](https://doi.org/10.3390/rs8060455); [Taubenböck et al., 2018](https://doi.org/10.1016/j.apgeog.2018.02.002); [Leonita et al., 2018](https://doi.org/10.3390/rs10101522); [Jochem & Tatem, 2021](https://doi.org/10.1371/journal.pone.0247535); [Abascal et al., 2022b](https://doi.org/10.1016/j.compenvurbsys.2022.101820)).
- **Roof-Material Heterogeneity (`[Established]`):** Makeshift/contrasting roof materials (corrugated metal, asbestos, mixed patching vs. uniform formal tile/concrete) are a well-established deprivation signal ([Kuffer et al., 2016](https://doi.org/10.3390/rs8060455); [Kuffer et al., 2016b](https://doi.org/10.1109/JSTARS.2016.2538563); [Wurm et al., 2017](https://doi.org/10.1016/j.rse.2017.03.030)).
- **`10 m` Sentinel-2 GLCM Detectability (`[Conditional — Prospective Candidate]`):** `10 m` pixels cannot isolate single small roofs, but GLCM neighborhood texture captures aggregate roof/alley heterogeneity ([Wurm et al., 2017b](https://doi.org/10.1109/JURSE.2017.7924586); [de Mattos et al., 2021](https://doi.org/10.48550/arXiv.2106.11395); [Wurm et al., 2019](https://doi.org/10.1016/j.isprsjprs.2019.06.006)) without `SAR` foreshortening ambiguity. Remains a candidate pending density-orthogonality screening.

### 2.4 Intra-Urban Micro-Environment (Green & Thermal Baselines)
- **Intra-Urban Normalization (`[Established]`):** `NDVI` and `ΔLST` must be evaluated against the city's urban built envelope ([Stewart & Oke, 2012](https://doi.org/10.1175/BAMS-D-11-00019.1); [Chakraborty & Lee, 2019](https://doi.org/10.1016/j.jag.2018.09.015); [Chakraborty et al., 2019](https://doi.org/10.1088/1748-9326/ab3b99); [Hsu et al., 2021](https://doi.org/10.1038/s41467-021-22799-5)).
- **Landsat `100 m` vs. MODIS `1 km` (`[Established]`):** Neighborhood thermal disparity requires `100 m` Landsat 8/9 multi-year compositing rather than `1 km` MODIS fallback ([Voogt & Oke, 2003](https://doi.org/10.1016/S0034-4257(03)00079-8); [Land, 2022](https://doi.org/10.3390/land11050711)). *(Flood hazard / `HAND` dropped completely.)*

### 2.5 Non-Compensatory Composites & Hex-Grid Inequality
- **Non-Compensatory Aggregation (`[Established]`):** Domain-first validation + penalty-adjusted non-compensatory aggregation ([OECD/EC-JRC, 2008](https://doi.org/10.1787/9789264043466-en); [Mazziotta & Pareto, 2016](https://doi.org/10.1007/s11205-015-0998-2)).
- **`greenR`-Inspired H3 Inequality (`[Established]`):** `Gini`, `Lorenz`, `Spatial Palma Ratio`, and `GSSI` ([Mahajan, 2024](https://doi.org/10.1016/j.ecolind.2024.112108); [Rey & Smith, 2013](https://doi.org/10.1007/s12076-012-0086-z)) inside the urban mask measure dispersion, requiring known-group validation (`Pergub 90` / `Kotaku`) to confirm *who* bears the deficit.

### 2.6 Spatial Boundary Detection (`GAT-AE` vs. Spatial Baselines)
- **Testable Hypothesis (`[Conditional — Thinner Comparative Benchmark Literature]`):** `GAT` / `GATE` ([Veličković et al., 2018](https://doi.org/10.48550/arXiv.1710.10903); [Salehi & Davulcu, 2020](https://doi.org/10.1109/ICTAI50040.2020.00154); [HGAurban, 2025](https://doi.org/10.1145/3746252.3761383)) must be benchmarked against `Local Moran's I` ([Anselin, 1995](https://doi.org/10.1111/j.1538-4632.1995.tb00338.x)) and spatial gradients under spatially blocked CV ([Roberts et al., 2017](https://doi.org/10.1111/ecog.02881)).

---

## Section 2.7 Synthesis Bridge: Proxy Validity Matrix
*(See verified Proxy Validity Matrix in `lit-review` output; maps `Rejected`, `Context-Only Typology`, `Surviving Core`, `Candidate`, and `Stage 5 / Benchmark` variables into Stage 3–5 implementation in [options_memo.md](./options_memo.md).)*
