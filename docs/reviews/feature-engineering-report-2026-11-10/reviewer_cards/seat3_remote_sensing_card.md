contract_role: perspective

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: block
trigger: "a physical, sensor-derived or area-level quantity is presented as human exposure, wellbeing, deprivation or injustice with no stated linking assumption, no validation or citation supporting that link, and no limitation on it"

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

I read this report as a thermal and optical remote-sensing scientist who works on exposure inequality. I am an outsider to urban morphology and defer to other seats on it. My question is whether each link holds from radiance, to retrieved variable, to lived exposure, to a statement about inequality.

The block on D4 rests on the thermal channel. Radiometric skin temperature from a clear-sky mid-morning overpass is named a "Thermal Stress Anomaly", given the direction "Acute Environmental Hazard", and justified through environmental-injustice literature. The report states no linking assumption, offers no validation against air temperature or a heat-stress measure, and lists no thermal limitation among the six uncertainties in Section 6. The defect can be repaired by reframing and validation, so I grade the findings below as Major and not Critical. Slope and NDVI show the same pattern at lower stakes: each is named after the construct it is hoped to represent.

Repository checks below were run read-only on `h3_features_raw.parquet` (residential cells) and the code at HEAD. Report-versus-repository differences count as findings only where they change what a reader may conclude.

Answers to the three Seat 3 questions. (1) No: neither a single date nor one dry-season composite characterises long-term micro-climate vulnerability; the product supports a statement about relative dry-season, clear-sky, mid-morning surface temperature only. (2) No: a 30 m surface model does not capture hazard in informal settlements, and flood exposure should take priority over slope in this delta, but flood depth cannot be derived credibly from the same 30 m global elevation data. (3) No: NDVI measures green photosynthetic signal, not ownership, management, access or ecological condition.

### W1: Land surface temperature is read as human heat exposure
**Severity**: Major
**Evidence Anchor**: text: §1 indicator table "Micro-urban heat island exposure, lack of shading, corrugated metal heat trapping"
**Confidence**: 5, thermal remote sensing and heat-exposure literature

Landsat ST_B10 is a directional radiometric skin temperature, seen from above at about 10:00 local time. In a kampung it is dominated by roofs. It does not measure the air temperature, humidity, radiant load, wind or indoor conditions that determine heat stress. Voogt and Oke (2003), which the report cites, draws this distinction. Venter et al. (2021) show that satellite and crowdsourced air-temperature views of the urban heat island differ in magnitude and mechanism, and Chakraborty et al. (2022) show that urban humidity deficits offset part of the outdoor heat-stress signal. Indoor conditions matter directly here: Ramsay et al. (2021) document chronic indoor heat stress in tropical informal settlements, and Kuras et al. (2017) set out why area measures differ from personal exposure. The fix is to rename the channel as dry-season clear-sky surface temperature anomaly, state the linking assumption, and validate against station or sensor air temperature and a humid-heat index in a subset of neighbourhoods. Absent that validation, the words "thermal stress" and "acute hazard" should go.

### W2: The composite cannot carry a long-term vulnerability claim, and the stated window misdescribes it
**Severity**: Major
**Evidence Anchor**: text: §3 dataset table, Landsat row "2022–2024 Composite"
**Confidence**: 4, Landsat compositing practice; tier offsets are observational

The repository does better than a single date: QA_PIXEL and ST_QA masks, a median composite, and a per-cell window ladder. But the product is essentially one season. 74.8% of residential cells use June to September 2023 only, with median acquisition around day 229, and 12.8% pool 2022 to 2024. The report's "2022–2024 Composite" therefore misdescribes most cells. The 2023 dry season was an El Niño season in Java, so it is a poor sole reference for long-term conditions, and for vegetated and agricultural backgrounds especially. The composite also samples only cloud-free mornings. It excludes the humid wet season, the afternoon peak and night-time heat retention, which are central to vulnerability in dense housing.

Tiers are not interchangeable. Comparing Landsat minus MODIS within 0.1-degree bins that contain more than one tier, Tier 2 sits about +1.9 K and Tier 3 about -1.2 K, against +0.2 K for Tier 1. These offsets are confounded with the conditions that push a cell to a wider tier, but they are as large as the 2.4 K spread between DKI municipal means in the current outputs (+9.24 to +11.61 K). Pixels are accepted with ST_QA uncertainty up to 3 K, also the same order as that spread. Landsat-MODIS agreement of Spearman 0.88 falls to 0.61 inside DKI, so the headline sanity check is carried by the urban-rural gradient. The repository's own flag `tier3_share_flag.lst` is true, and ADR 0002 says to revisit the window before training in that case. A long-term claim needs a multi-year stack with an annual-cycle model (Weng and Fu, 2014; Bechtel, 2015), tier harmonisation, and a diurnal source such as ECOSTRESS.

### W3: LST coverage fails where the report's most deprived case studies sit
**Severity**: Major
**Evidence Anchor**: absence: §5.3 and §5.4 tables — expected LST coverage and window-tier shares by municipality; checked §3 dataset table, §5.2 to §5.4 tables, §6 limitations
**Confidence**: 5, directly recomputed from repository QA columns

The report presents N = 9,345 and a mean ΔLST for every Jakarta municipality as though coverage were complete. In the outputs, 894 residential cells (9.6%) have no LST. Failure is 34.2% in Jakarta Utara and 32.9% in Jakarta Barat, against 1.0 to 1.6% in Jakarta Selatan and Timur. Inside DKI it is 28.9% north of latitude -6.2 and 0.7% south of it. Only 19.0% of Jakarta Utara cells use the primary window, and 41.3% use Tier 3. About 1.53 million of 4.51 million residents in Utara and Barat are in cells with no thermal value. Near the report's own named places, using my approximate coordinates and a 1 km radius, two of three cells around Kampung Akuarium and two of four around Jembatan Besi fail.

Failing cells split about evenly between too few clear observations (502) and too little valid area (510), with 118 failing both, and the outputs do not separate the ST_QA limit from cloud as the cause. MODIS medians for failing and retained DKI cells are nearly equal (309.90 and 310.07 K), so I find no evidence that the excluded cells are hotter at 1 km. The problem is coverage: the seven-channel model drops those cells altogether, and the north coast loses a third of its cells. The authors should report coverage by unit, diagnose which mask removes the pixels, relax or model the gap, and run sensitivity analysis on the ST_QA limit.

### W4: The heat-island background is an upland forest reference, so ΔLST is not an urban heat island intensity
**Severity**: Major
**Evidence Anchor**: text: §2.2 Indicator 6 "the regional rural background temperature (calculated as the 10th percentile LST across all vegetated peri-urban cells"
**Confidence**: 4, surface heat island methods; slope share is my proxy for elevation

The implemented baseline is the median LST of non-residential, GHS-SMOD rural, vegetated cells (305.45 K), not the stated 10th percentile (299.01 K for the same set). The difference is 6.4 K. The background also mixes climates: 75% of its cells have at least 5% of their area steeper than 15 degrees. Flat background cells (under 1% steep, n = 598) have a median of 308.25 K, and cells at least 10% steep (n = 2,420) a median of 304.09 K. An upland forest reference inflates every lowland value by several kelvin through elevation and land cover. A single scalar leaves cell ranks unchanged, but it changes the magnitudes the report interprets, and it interacts with fixed benchmark bounds of -5 and +15 K. The authors should use a lowland, elevation-matched rural reference, or correct for elevation, and show sensitivity to the choice.

### W5: The reported thermal magnitudes do not correspond to the implemented pipeline
**Severity**: Major
**Evidence Anchor**: table: §5.3 stratified distribution table, ΔLST mean row
**Confidence**: 5, recomputed and cross-checked against the audit pack

The report gives +2.78, +1.42 and -0.38 K for DKI, Kota and Kabupaten. The current outputs give +10.90, +9.79 and +5.28 K. The sign for Kabupaten changes, and only 3.9% of residential cells are negative in the outputs, whereas the report's median is +0.13 K. Applying the stated 10th-percentile baseline would raise the values further, so the report's definition does not explain its numbers either. Whatever the cause, "Extreme SUHI" cannot be evaluated from a table that the pipeline does not produce. The two coldest residential cells (268.97 and 288.72 K, both Tier 3 in Kabupaten Bekasi, against MODIS near 306 K) also indicate residual cloud contamination that survives the masks.

### W6: Thermal inequality is asserted from cited literature and not tested here
**Severity**: Major
**Evidence Anchor**: text: §4.1 item 5 "low-income settlements suffer disproportionately from Surface Urban Heat Islands (SUHI)"
**Confidence**: 4, environmental-justice method; the correlations are recomputed but use proxies

The feature store contains no income or wealth measure, no population subgroup, and no disparity statistic for heat. Only Chakraborty et al. (2019) of the three citations addresses income, and it does so with surface temperature in other cities. Within DKI, ΔLST rises with plan area fraction (Spearman 0.54) and density (0.44) and falls with NDVI (-0.49), but it does not track crowding: the correlation with net footprint per capita is +0.18, the opposite of the claimed direction, and with modelled space sufficiency -0.08. The strong all-cell correlation (-0.63 with footprint per capita) reflects the urban-rural gradient. ΔLST is also averaged over every pixel in a 74 ha cell, including roads, industry and water, and assigned to residents, which is an ecological inference. The authors should either test the claim with Susenas or Podes-linked socioeconomic data and a stated disparity measure, computed on residential pixels, or withdraw the injustice framing and describe a built-form correlate of surface temperature.

### W7: The roof physics in the justification is inconsistent, and it matters to the retrieval
**Severity**: Minor
**Evidence Anchor**: text: §4.1 item 5 "dense corrugated iron or zinc roofing, high thermal mass"
**Confidence**: 4, thermal radiometry

Thin corrugated sheet has low thermal mass; it heats and cools rapidly, which is a different mechanism from concrete or masonry storage. Bare metal also has low and variable broadband emissivity. The Collection 2 surface temperature algorithm uses ASTER-based emissivity and reanalysis-based atmospheric correction (Malakar et al., 2018; Laraby and Schott, 2018), which do not represent this roof stock, so retrieved temperature over metal roofs may be biased. Native TIRS resolution of 100 m also cannot separate roof materials. Roofing composition is not measured anywhere in the pipeline.

### W8: Slope is the wrong primary physical hazard for this delta, and the flood signal was silently retired
**Severity**: Major
**Evidence Anchor**: text: §4.1 item 6 "marginalized populations are priced out of safe, flat terrain and settle on unbuildable steep slopes"
**Confidence**: 4, Jakarta hazard literature and repository specification

This mechanism is imported from hillside-settlement cities. In Jakarta the dominant physical hazards for low-income residents are riverine and pluvial flooding, tidal inundation and subsidence (Abidin et al., 2011; Budiyono et al., 2015; Padawangi and Douglass, 2015), and the upland south also hosts high-amenity villa development. The slope channel is zero for 78.6% of DKI cells and 59.9% of all cells, so it gives no hazard information in the part of the region where the report locates its concerns. Its population-weighted mean is 0.98% against 3.95% unweighted.

The repository once carried `water_frequency`, a Dynamic World flood proxy. It was retired in Ticket 21, partly on the ground that it captures open water and has a correlation of 0.024 with living space sufficiency. The report does not disclose this. Independence from another channel is not a reason to remove a hazard. Limited validity as a flood measure is a reason, but that calls for replacing it. Flood should take priority, but not as depth from a global 30 m model: FABDEM vertical error in built-up areas is about a metre (Hawker et al., 2022), comparable to common flood depths, and subsidence quickly dates any static elevation in north Jakarta. Practical routes are BPBD inundation records at RW level, InaRISK hazard layers, Sentinel-1 flood frequency, and hydrodynamic modelling on a higher-resolution terrain model such as DEMNAS or LiDAR. The term "hydraulic flood retention depth" also needs definition.

### W9: GLO-30 is a surface model, so non-zero slope in flat Jakarta tracks tall buildings
**Severity**: Major
**Evidence Anchor**: text: §6.5 "yields $S_{>15^\circ} = 0.0\%$ across all of DKI Jakarta"
**Confidence**: 4, DEM characteristics; floors are themselves modelled

The report names GLO-30 and FABDEM, but the code uses GLO-30 only, which is a surface model that includes buildings and canopy. The statement of 0.0% across DKI is not what the outputs show: 184 of 860 DKI cells are non-zero, with a maximum of 9.5%. A 15-degree slope across a 30 m pixel needs a rise of about 8 m, which a building edge easily produces. The share of non-zero cells climbs to 48.8% in the top quintile of Open Buildings mean floors, against 11.6 to 20.4% in the lower quintiles, and the steepest DKI cells include high-rise areas with mean floors of 5.2 and 7.7. On an alluvial plain the channel is partly labelling high-rise districts as terrain hazard, which runs against the intended meaning. FABDEM or another bare-earth model is the minimum correction.

### W10: Slope is an area share of the cell, not exposure of residents
**Severity**: Major
**Evidence Anchor**: text: §2.2 Indicator 7 "The indicator measures the spatial percentage of cell $i$ occupied by terrain steeper than"
**Confidence**: 4, recomputed; pixel-level overlay not run

Steep ground in a cell need not be where people live. The 1,579 cells with at least 5% steep area hold only 2.0 million of 40.5 million residents, with median density of 746 per km² against 3,390 elsewhere. The channel therefore mostly records uninhabited upland terrain within a hexagon, and it correlates positively with NDVI (0.60) and distance from Monas (0.41). A hazard-exposure measure should intersect steep or unstable terrain with building footprints or population at pixel scale, and landslide susceptibility also depends on lithology, drainage and rainfall.

### W11: NDVI cannot separate managed private greenery from degraded spontaneous vegetation
**Severity**: Major
**Evidence Anchor**: text: §1 indicator table "Green infrastructure deficit, lack of tree canopy, biophilic inequality"
**Confidence**: 4, optical remote sensing and urban greening literature

NDVI responds to green leaf area and is nearly saturated over dense canopy and irrigated turf (Huete et al., 2002). Golf turf, a private garden, roadside shrubs, weedy vacant land and paddy can have similar values, and NDVI says nothing about tenure, management, public access, species or condition. It also cannot support "lack of tree canopy", because it does not separate trees from grass and crops. The repository specification calls the channel the "luxury effect", a relationship documented with socioeconomic data (Hope et al., 2003; Schwarz et al., 2015) that this study does not have. Presence is also not benefit (Wolch et al., 2014). The direction is unresolved: the report states lower means deprivation, whereas the benchmark sets orientation to `context`. Across all cells NDVI is mainly rurality (Spearman with density -0.72), and a dry-season composite captures an arbitrary paddy stage; the Karawang interquartile range is 0.35 to 0.47. At minimum, the authors should label the channel as greenness, and add a tree-canopy product, a land-use and access layer that separates private or gated green from public green, and a test against tenure or wealth.

### W12: NDVI cell means are lowered by water and the channel is misnamed
**Severity**: Minor
**Evidence Anchor**: text: §2.2 Indicator 5 "Cell greenness is calculated as the spatial mean over all cloud-free pixels within"
**Confidence**: 5, recomputed

No water mask is applied. 29 residential cells have negative mean NDVI, and the 102 cells below 0.1 have a median whole-year water frequency of 0.38. Those are water-affected cells, not green deficits. The report calls the channel a "Vegetation Cover Fraction" on [0, 1], but it is mean NDVI with a recomputed minimum of -0.241. The FVC alternative in §2.2 is not implemented in the repository.

### W13: The planning threshold needs a checked source and unit
**Severity**: Minor
**Evidence Anchor**: text: §4.1 item 6 "designate slopes above $15^\circ$ as restricted for standard residential construction"
**Confidence**: 3, secondary Indonesian sources only; I did not read the regulations themselves

Indonesian studies I located cite settlement and landslide criteria in percent gradient (for example 0 to 25% from Permen PU 41/PRT/M/2007, and 20 to 40% and above 40% typologies from Permen PU 22/PRT/M/2007). I could not confirm a 15-degree limit in the cited SNI or Permen PU 20/2007. 15 degrees is 26.8%, so a percent-degree confusion would matter. The authors should quote the clause.

### W14: The slope algorithm stated is not the one used
**Severity**: Minor
**Evidence Anchor**: text: §2.2 Indicator 7 "Local terrain gradient is computed via Horn's finite-difference algorithm"
**Confidence**: 4, Earth Engine documentation as I recall it and repository code

The code calls `ee.Terrain.slope`, documented as using 4-connected neighbours, on a DEM forced through `reproject` at 30 m. That is not Horn's eight-neighbour estimator, and reprojection without an explicit resampling method can add stair-step gradients near a 15-degree threshold.

### W15: "Micro-scale" overstates the thermal support
**Severity**: Minor
**Evidence Anchor**: text: Executive Summary "Micro-Scale Surface Urban Heat Island Anomaly"
**Confidence**: 5, sensor specification

TIRS is about 100 m native, delivered at 30 m, and the result is averaged over 74 ha. This is neighbourhood-scale. It cannot see alleys, shade or individual roofs, and the terms "micro-scale" and "micro-climate" should be dropped.

### W16: Hazard labels carry an unexamined risk for residents
**Severity**: Minor
**Evidence Anchor**: absence: §4 to §6 — expected discussion of users, scale of use and harms of hazard or deprivation labels for kampung residents; checked §4.1, §5.4, §6.1 to §6.6, and the §7.1 question list
**Confidence**: 3, outside my core expertise; informed by Jakarta flood-governance writing

Riverbank kampungs are named in §6.5 as hazard sites, and in Jakarta river-normalisation programmes have involved evictions. A coarse index that calls a place hazardous or deprived can be used to justify displacement without residents having a voice in it. The report should say who may use each layer, at what scale, and what it must not be used for, and should involve community or BPBD knowledge in validation (Padawangi and Douglass, 2015).

### S1: Candour about micro-topography
**Evidence Anchor**: text: §6.5 "These micro-cliffs are invisible to a $30\text{ m}$ DEM."

The authors recognise that riverbank drop-offs fall below DEM resolution, and this is the right starting point for the hazard discussion.

### S2: Stratification avoids a misleading pooled reading
**Evidence Anchor**: text: §5.1 "Evaluating the dataset as a single unstratified distribution produces misleading results"

Separating the core, satellite cities and hinterland is essential for reading thermal and vegetation gradients, and it exposes the urban-rural structure of these channels.

### S3: Limitations are documented openly
**Evidence Anchor**: text: §6 "this section documents the six primary methodological uncertainties"

A dedicated uncertainty section is uncommon and useful, though it needs to extend to the thermal and vegetation channels.

### S4: The implemented compositing design is careful
**Evidence Anchor**: dataset: repository `stage3_qa.json` window_tier_shares_residential and tier3_share_flag, with `lst_tier`, `lst_n_clear` and `lst_valid_frac` columns in `h3_features_raw.parquet`

Per-cell representativeness checks, recorded tiers, QA masking and an independent MODIS comparison are stronger than the report conveys and should be described in it.

### Cross-Disciplinary Reading Recommendations
Venter et al. (2021), Chakraborty et al. (2022), Ramsay et al. (2021) and Kuras et al. (2017) on surface versus experienced heat; Weng and Fu (2014) and Bechtel (2015) on cloud gaps and annual cycles; Malakar et al. (2018) and Laraby and Schott (2018) on the Landsat product; Estoque et al. (2017) on Southeast Asian megacity LST; Harlan et al. (2006) on neighbourhood microclimates; Abidin et al. (2011), Budiyono et al. (2015), Padawangi and Douglass (2015) and Hawker et al. (2022) on Jakarta flood context and elevation; Huete et al. (2002), Carlson and Ripley (1997), Hope et al. (2003), Schwarz et al. (2015) and Wolch et al. (2014) on vegetation indices and green equity.

~~~yaml suggested-references
- title: "Crowdsourced air temperatures contrast satellite measures of the urban heat island and its mechanisms"
  authors: ["Venter, Z. S."]
  year: "2021"
  doi: "10.1126/sciadv.abb9569"
  arxiv_id: null
- title: "Lower Urban Humidity Moderates Outdoor Heat Stress"
  authors: ["Chakraborty, T."]
  year: "2022"
  doi: "10.1029/2022AV000729"
  arxiv_id: null
- title: "Chronic heat stress in tropical urban informal settlements"
  authors: ["Ramsay, E. E."]
  year: "2021"
  doi: "10.1016/j.isci.2021.103248"
  arxiv_id: null
- title: "Opportunities and Challenges for Personal Heat Exposure Research"
  authors: ["Kuras, E. R."]
  year: "2017"
  doi: "10.1289/ehp556"
  arxiv_id: null
- title: "Modeling annual parameters of clear-sky land surface temperature variations and evaluating the impact of cloud cover using time series of Landsat TIR data"
  authors: ["Weng, Q."]
  year: "2014"
  doi: "10.1016/j.rse.2013.09.002"
  arxiv_id: null
- title: "A New Global Climatology of Annual Land Surface Temperature"
  authors: ["Bechtel, B."]
  year: "2015"
  doi: "10.3390/rs70302850"
  arxiv_id: null
- title: "An Operational Land Surface Temperature Product for Landsat Thermal Data: Methodology and Validation"
  authors: ["Malakar, N. K."]
  year: "2018"
  doi: "10.1109/tgrs.2018.2824828"
  arxiv_id: null
- title: "Uncertainty estimation method and Landsat 7 global validation for the Landsat surface temperature product"
  authors: ["Laraby, K. G."]
  year: "2018"
  doi: "10.1016/j.rse.2018.06.026"
  arxiv_id: null
- title: "Effects of landscape composition and pattern on land surface temperature: An urban heat island study in the megacities of Southeast Asia"
  authors: ["Estoque, R. C."]
  year: "2017"
  doi: "10.1016/j.scitotenv.2016.10.195"
  arxiv_id: null
- title: "Neighborhood microclimates and vulnerability to heat stress"
  authors: ["Harlan, S. L."]
  year: "2006"
  doi: "10.1016/j.socscimed.2006.07.030"
  arxiv_id: null
- title: "Land subsidence of Jakarta (Indonesia) and its relation with urban development"
  authors: ["Abidin, H. Z."]
  year: "2011"
  doi: "10.1007/s11069-011-9866-9"
  arxiv_id: null
- title: "Flood risk assessment for delta mega-cities: a case study of Jakarta"
  authors: ["Budiyono, Y."]
  year: "2015"
  doi: "10.1007/s11069-014-1327-9"
  arxiv_id: null
- title: "Water, Water Everywhere: Toward Participatory Solutions to Chronic Urban Flooding in Jakarta"
  authors: ["Padawangi, R."]
  year: "2015"
  doi: "10.5509/2015883517"
  arxiv_id: null
- title: "A 30 m global map of elevation with forests and buildings removed"
  authors: ["Hawker, L."]
  year: "2022"
  doi: "10.1088/1748-9326/ac4d4f"
  arxiv_id: null
- title: "Overview of the radiometric and biophysical performance of the MODIS vegetation indices"
  authors: ["Huete, A."]
  year: "2002"
  doi: "10.1016/s0034-4257(02)00096-2"
  arxiv_id: null
- title: "On the relation between NDVI, fractional vegetation cover, and leaf area index"
  authors: ["Carlson, T. N."]
  year: "1997"
  doi: "10.1016/s0034-4257(97)00104-1"
  arxiv_id: null
- title: "Socioeconomics drive urban plant diversity"
  authors: ["Hope, D."]
  year: "2003"
  doi: "10.1073/pnas.1537557100"
  arxiv_id: null
- title: "Trees Grow on Money: Urban Tree Canopy Cover and Environmental Justice"
  authors: ["Schwarz, K."]
  year: "2015"
  doi: "10.1371/journal.pone.0122051"
  arxiv_id: null
- title: "Urban green space, public health, and environmental justice: The challenge of making cities just green enough"
  authors: ["Wolch, J. R."]
  year: "2014"
  doi: "10.1016/j.landurbplan.2014.01.017"
  arxiv_id: null
~~~
