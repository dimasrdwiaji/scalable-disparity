# Mapping Micro-Scale Intra-Urban Physical Deprivation, Environmental Inequality, and Spatial Boundaries in the Global South Using Open Earth Observation and Graph Attention

**Author**: Dimas RD

---

### Abstract
*[Placeholder: The abstract will be written after all empirical analyses, inequality evaluations, and spatial boundary benchmarks are completed.]*

*Keywords*: *[Placeholder: Keywords to be finalized after remaining sections are complete.]*

---

# 1. Introduction

Physical living conditions in growing cities rarely change smoothly across administrative districts. High-density informal settlements—often called *kampungs* in Indonesia—frequently border formal housing estates and commercial centers directly ([Kuffer et al., 2016](https://doi.org/10.3390/rs8060455); [Taubenböck et al., 2018](https://doi.org/10.1016/j.apgeog.2018.02.002)). Greater Jakarta (Jabodetabek) illustrates this proximity clearly. Gated residential developments and apartment blocks stand immediately adjacent to low-income *kampungs*, divided only by perimeter walls or arterial streets in central neighborhoods such as Menteng and Cikini as well as in suburban Tangerang ([Hidayati et al., 2020](https://doi.org/10.1080/17549175.2020.1814391); [Mardhotillah & Gamal, 2018](https://doi.org/10.14716/ijtech.v9i7.2519); [Wardhani, 2016](https://doi.org/10.18196/jgp.2016.0025)).

## 1.1 Detecting Intra-Urban Disparity with Open Data
Locating these block-scale differences supports slum upgrading, infrastructure planning, and heat mitigation ([Abascal et al., 2022a](https://doi.org/10.1016/j.compenvurbsys.2022.101770); [Chakraborty et al., 2019](https://doi.org/10.1088/1748-9326/ab3b99); [Hsu et al., 2021](https://doi.org/10.1038/s41467-021-22799-5); [Leonita et al., 2018](https://doi.org/10.3390/rs10101522)). When conditions are reported only as municipal or district averages, contrasting neighborhoods cancel each other out, hiding deprived pockets inside statistically affluent districts (Openshaw, 1984; [Reardon & O'Sullivan, 2004](https://doi.org/10.1111/j.0081-1750.2004.00150.x)). Spatial indicators mapped onto uniform hexagonal grids, paired with urban inequality summaries such as Gini or Palma ratios ([Mahajan, 2024](https://doi.org/10.1016/j.ecolind.2024.112108); [Rey & Smith, 2013](https://doi.org/10.1007/s12076-012-0086-z)), make both localized deficits and citywide dispersion visible.

Across much of the Global South, however, detailed municipal cadastres, sub-district housing registries, and commercial very-high-resolution imagery are incomplete, outdated, or restricted ([Herfort et al., 2023](https://doi.org/10.1038/s41467-023-39698-6); [Thomson et al., 2020](https://doi.org/10.3390/socsci9050080)). Monitoring tools therefore have to rely on globally open Earth observation and open vector datasets. Even open data require scrutiny before entering a model. Coarse atmospheric or thermal products blur street-level contrasts ([van Donkelaar et al., 2021](https://doi.org/10.1021/acs.est.1c05309); [Voogt & Oke, 2003](https://doi.org/10.1016/S0034-4257(03)00079-8)), population grids and nighttime lights tend to follow overall built density rather than local housing quality ([Gibson et al., 2021](https://doi.org/10.1016/j.jdeveco.2020.102602); [Pesaresi et al., 2024](https://doi.org/10.1080/17538947.2024.2390454)), and raw amenity counts can invert when central *kampungs* sit surrounded by busy commercial streets while wealthier gated estates sit farther away ([Hidayati et al., 2020](https://doi.org/10.1080/17549175.2020.1814391)).

## 1.2 Indicator Vetting and Analytical Scope
Because misleading inputs corrupt downstream inequality maps and clustering models alike, indicator selection cannot rely on data availability alone. This study treats literature-based **indicator vetting** as a core methodological step rather than background context. Candidate physical, environmental, and accessibility datasets are evaluated against four practical screening checks before modeling: whether pixel or polygon size captures individual city blocks, whether derived ratios avoid circular calculations against building-allocated population grids or overall urban density, whether farmland or non-residential land uses flip the direction of the signal, and whether crowdsourced tags leave out poorer or secondary-city neighborhoods ([Barrington-Leigh & Millard-Ball, 2017](https://doi.org/10.1371/journal.pone.0180698); [Herfort et al., 2023](https://doi.org/10.1038/s41467-023-39698-6); [Schiavina et al., 2023](https://doi.org/10.2760/098587)).

Section 2 conducts this full vetting review to establish which datasets warrant inclusion and what cutoffs or spatial masks they require, narrowing the scope to area-level built form and micro-environmental quality rather than consumer asset models such as Meta's Relative Wealth Index ([Chi et al., 2022](https://doi.org/10.1073/pnas.2113658119)), household crowding ratios, or service-proximity accessibility indices (which Section 2 excludes due to missing affordability data and proximity inversion in central *kampungs*). On an Uber H3 Resolution-8 grid (`~531 m` edge length) covering Mainland DKI Jakarta, Karawang, and an external hold-out city, the vetted feature pool covers two physical domains: residential built form (small-footprint residential buildings, nearest-neighbor building spacing, residential built-up share, and candidate Sentinel-2 roof-texture metrics) and intra-urban green-thermal conditions (Sentinel-2 canopy greenness and `100 m` Landsat thermal anomalies referenced against each city's urban extent). Each retained variable is first examined on its own to see how well it identifies informal areas and what side of disparity it explains, before combining validated domains so strength in one area cannot mask severe deficits in another ([Mazziotta & Pareto, 2016](https://doi.org/10.1007/s11205-015-0998-2); [OECD/EC-JRC, 2008](https://doi.org/10.1787/9789264043466-en)). We also compute urban-masked hexagonal inequality metrics and test whether an unsupervised Spatial Graph Attention Autoencoder (GAT-AE; [Salehi & Davulcu, 2020](https://doi.org/10.1109/ICTAI50040.2020.00154); [Veličković et al., 2018](https://doi.org/10.48550/arXiv.1710.10903)) with a two-dimensional bottleneck (`d = 2`) outperforms Local Indicators of Spatial Association (LISA; [Anselin, 1995](https://doi.org/10.1111/j.1538-4632.1995.tb00338.x)) and linear spatial gradients under spatially blocked cross-validation ([Roberts et al., 2017](https://doi.org/10.1111/ecog.02881)).

## 1.3 Research Questions
Three research questions structure the investigation:
1. **RQ1**: Which open physical and environmental indicators—and their associated global datasets—are suitable for identifying intra-urban deprivation once vetted for spatial resolution, density scaling, non-residential mixing, and proximity bias?
2. **RQ2**: How does each vetted indicator perform on its own—and when combined across physical domains without allowing surpluses to mask deficits—in identifying informal settlements, explaining different sides of neighborhood disparity, and describing citywide inequality?
3. **RQ3**: Does an unsupervised Spatial GAT-AE built on these vetted indicators isolate formal–informal neighborhood boundaries more accurately than classical spatial statistics under spatially blocked cross-validation, and how consistently does the method transfer across severity grades and an external city?

Section 2 answers RQ1 through the indicator-vetting literature review; Section 3 describes the study areas and open-data preparation; Section 4 details per-indicator validation, inequality metrics, and the GAT-AE benchmark; and Sections 5–7 present empirical results, limitations, and conclusions.

---

### Section 1 Verified References

Abascal, Á., Rothwell, N., Shonowo, A., Thomson, D. R., Elias, P., Elsey, H., Yeboah, G., & Kuffer, M. (2022a). "Domains of deprivation framework" for mapping slums, informal settlements, and other deprived areas in LMICs to improve urban planning and policy: A scoping review. *Computers, Environment and Urban Systems*, 93, 101770. [https://doi.org/10.1016/j.compenvurbsys.2022.101770](https://doi.org/10.1016/j.compenvurbsys.2022.101770)

Anselin, L. (1995). Local Indicators of Spatial Association—LISA. *Geographical Analysis*, 27(2), 93–115. [https://doi.org/10.1111/j.1538-4632.1995.tb00338.x](https://doi.org/10.1111/j.1538-4632.1995.tb00338.x)

Barrington-Leigh, C., & Millard-Ball, A. (2017). The world's user-generated road map is more than 80% complete. *PLOS ONE*, 12(8), e0180698. [https://doi.org/10.1371/journal.pone.0180698](https://doi.org/10.1371/journal.pone.0180698)

Chakraborty, T., Hsu, A., Manya, D., & Sheriff, G. (2019). Disproportionately higher exposure to urban heat in lower-income neighborhoods: A multi-city perspective. *Environmental Research Letters*, 14(10), 105003. [https://doi.org/10.1088/1748-9326/ab3b99](https://doi.org/10.1088/1748-9326/ab3b99)

Chi, G., Fang, H., Chatterjee, S., & Blumenstock, J. E. (2022). Microestimates of wealth for all low- and middle-income countries. *Proceedings of the National Academy of Sciences*, 119(3), e2113658119. [https://doi.org/10.1073/pnas.2113658119](https://doi.org/10.1073/pnas.2113658119)

Gibson, J., Olivia, S., Boe-Gibson, G., & Li, C. (2021). Which night lights data should we use in economics, and where? *Journal of Development Economics*, 149, 102602. [https://doi.org/10.1016/j.jdeveco.2020.102602](https://doi.org/10.1016/j.jdeveco.2020.102602)

Herfort, B., Lautenbach, S., Porto de Albuquerque, J., Anderson, J., & Zipf, A. (2023). A spatio-temporal analysis investigating completeness and inequalities of global urban building data in OpenStreetMap. *Nature Communications*, 14, 3985. [https://doi.org/10.1038/s41467-023-39698-6](https://doi.org/10.1038/s41467-023-39698-6)

Hidayati, I., Yamu, C., & Tan, W. (2020). Realised pedestrian accessibility of an informal settlement in Jakarta, Indonesia. *Journal of Urbanism: International Research on Placemaking and Urban Sustainability*. [https://doi.org/10.1080/17549175.2020.1814391](https://doi.org/10.1080/17549175.2020.1814391)

Hsu, A., Sheriff, G., Chakraborty, T., & Manya, D. (2021). Disproportionate exposure to urban heat island intensity across major US cities. *Nature Communications*, 12, 2721. [https://doi.org/10.1038/s41467-021-22799-5](https://doi.org/10.1038/s41467-021-22799-5)

Kuffer, M., Pfeffer, K., & Sliuzas, R. (2016). Slums from space—15 years of slum mapping using remote sensing. *Remote Sensing*, 8(6), 455. [https://doi.org/10.3390/rs8060455](https://doi.org/10.3390/rs8060455)

Leonita, G., Kuffer, M., Sliuzas, R. V., & Persello, C. (2018). Machine learning-based slum mapping in support of slum upgrading programs: The case of Bandung City, Indonesia. *Remote Sensing*, 10(10), 1522. [https://doi.org/10.3390/rs10101522](https://doi.org/10.3390/rs10101522)

Mahajan, S. (2024). greenR: An open-source framework for quantifying urban greenness. *Ecological Indicators*, 163, 112108. [https://doi.org/10.1016/j.ecolind.2024.112108](https://doi.org/10.1016/j.ecolind.2024.112108)

Mardhotillah, H., & Gamal, A. (2018). Segregation and gentrification of an informal settlement in a city center. *International Journal of Technology*, 9(7). [https://doi.org/10.14716/ijtech.v9i7.2519](https://doi.org/10.14716/ijtech.v9i7.2519)

Mazziotta, M., & Pareto, A. (2016). On a Generalized Non-compensatory Composite Index for Measuring Socio-economic Phenomena. *Social Indicators Research*, 127(3), 983–1003. [https://doi.org/10.1007/s11205-015-0998-2](https://doi.org/10.1007/s11205-015-0998-2)

OECD/EC-JRC (2008). *Handbook on Constructing Composite Indicators: Methodology and User Guide*. OECD Publishing. [https://doi.org/10.1787/9789264043466-en](https://doi.org/10.1787/9789264043466-en)

Openshaw, S. (1984). *The Modifiable Areal Unit Problem*. Geo Books.

Pesaresi, M., Schiavina, M., Politis, P., Freire, S., et al. (2024). Advances on the Global Human Settlement Layer by joint assessment of Earth Observation and population survey data. *International Journal of Digital Earth*, 17(1). [https://doi.org/10.1080/17538947.2024.2390454](https://doi.org/10.1080/17538947.2024.2390454)

Reardon, S. F., & O'Sullivan, D. (2004). Measures of spatial segregation. *Sociological Methodology*, 34(1), 121–162. [https://doi.org/10.1111/j.0081-1750.2004.00150.x](https://doi.org/10.1111/j.0081-1750.2004.00150.x)

Rey, S. J., & Smith, R. J. (2013). A spatial decomposition of the Gini coefficient. *Letters in Spatial and Resource Sciences*, 6(2), 55–82. [https://doi.org/10.1007/s12076-012-0086-z](https://doi.org/10.1007/s12076-012-0086-z)

Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J., Guillera-Arroita, G., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography*, 40(8), 913–929. [https://doi.org/10.1111/ecog.02881](https://doi.org/10.1111/ecog.02881)

Salehi, A., & Davulcu, H. (2020). Graph Attention Auto-Encoders (GATE). *IEEE International Conference on Tools with Artificial Intelligence (ICTAI)*. [https://doi.org/10.1109/ICTAI50040.2020.00154](https://doi.org/10.1109/ICTAI50040.2020.00154)

Schiavina, M., Melchiorri, M., Pesaresi, M., et al. (2023). *GHSL Data Package 2023*. EC-JRC. [https://doi.org/10.2760/098587](https://doi.org/10.2760/098587)

Taubenböck, H., Kraff, N. J., & Wurm, M. (2018). The morphology of the Arrival City – A global categorization based on literature surveys and remotely sensed data. *Applied Geography*, 92, 150–167. [https://doi.org/10.1016/j.apgeog.2018.02.002](https://doi.org/10.1016/j.apgeog.2018.02.002)

Thomson, D. R., Kuffer, M., Boo, G., Hati, B., Grippa, T., Elsey, H., Linard, C., & Kabaria, C. (2020). Need for an Integrated Deprived Area "Slum" Mapping System (IDEAMAPS) in Low- and Middle-Income Countries (LMICs). *Social Sciences*, 9(5), 80. [https://doi.org/10.3390/socsci9050080](https://doi.org/10.3390/socsci9050080)

van Donkelaar, A., Hammer, M. S., Bindle, L., Brauer, M., Brook, J. R., Garay, M. J., et al. (2021). Monthly global estimates of fine particulate matter and their uncertainty. *Environmental Science & Technology*, 55(22), 15287–15300. [https://doi.org/10.1021/acs.est.1c05309](https://doi.org/10.1021/acs.est.1c05309)

Veličković, P., Cucurull, G., Casanova, A., Romero, A., Liò, P., & Bengio, Y. (2018). Graph Attention Networks. *ICLR 2018* / *arXiv:1710.10903*. [https://doi.org/10.48550/arXiv.1710.10903](https://doi.org/10.48550/arXiv.1710.10903)

Voogt, J. A., & Oke, T. R. (2003). Thermal remote sensing of urban climates. *Remote Sensing of Environment*, 86(3), 370–384. [https://doi.org/10.1016/S0034-4257(03)00079-8](https://doi.org/10.1016/S0034-4257(03)00079-8)

Wardhani, I. S. (2016). The implications of gated society in Jakarta Metropolitan Region: A multiple-case study in Tangerang District, Banten, Indonesia. *Journal of Government and Politics*, 7(1), 128–152. [https://doi.org/10.18196/jgp.2016.0025](https://doi.org/10.18196/jgp.2016.0025)
