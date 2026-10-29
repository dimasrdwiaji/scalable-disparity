# Scalable GeoAI for Mapping and Explaining Micro-Scale Physical Living Standards and Spatial Segregation: Integrating Google Open Buildings, Overture Maps, and Graph Attention Autoencoders

**Author**: Dimas RD  
**Affiliation**: Urban Informatics and Spatial Artificial Intelligence Laboratory  
**Target Venue**: *ISPRS International Journal of Geo-Information* (IJGI) / *PLOS ONE* / EarthArXiv  
**Standard**: Publication Manual of the American Psychological Association (7th ed.; APA 7)  

---

### Abstract
Measuring socio-spatial inequality and living conditions in Global South megacities is fundamentally hindered by pervasive geographic data scarcity, the incompleteness of crowdsourced spatial data in peripheral areas, administrative boundary aggregation, and the relative wealth index trap of supervised machine learning models trained on national survey asset scores. This study proposes an unsupervised, cloud-native GeoAI framework that maps absolute physical living standards and identifies micro-scale segregation barriers across the 12,800 km² Jabodetabek metropolitan region and Karawang Regency, Indonesia. We integrate Google Open Buildings v3 (2.5D heights) intersected with European Commission JRC GHS-BUILT-C residential masks, Overture Maps Foundation points of interest (POIs), Sentinel-2 multi-spectral indices, Landsat land surface temperature, Open-Meteo air quality reanalysis, and NASA VIIRS nighttime radiance onto 17,300 Uber H3 Resolution 8 hexagonal cells (~0.74 km²). We formulate a 10-dimensional Physical Living Standard Index (PLSI) calibrated against international human settlement and health baselines (UN-Habitat 9.0 m² shelter area, WHO PM2.5 standards, and 15-minute pedestrian network catchments). To detect segregation without survey training labels, we deploy a Spatial Graph Attention Autoencoder (GAT-AE) over pure geometric H3 adjacency. The bottleneck representation (d = 2) enforces local spatial continuity expectations, causing reconstruction error to spike selectively along abrupt socio-spatial boundaries separating luxury master-planned enclaves from informal kampungs. Attributed error decomposition separates true social severance from natural ecological land-cover transitions. A four-quadrant divergence analysis against Meta's Relative Wealth Index demonstrates that asset-based models systematically underestimate physical deprivation in asset-dense informal settlements. This framework provides urban and regional planning authorities with an auditable, continuous instrument to track physical living standards and spatial inequality without survey latency.

*Keywords*: GeoAI, spatial segregation, informal settlements, Graph Attention Networks, H3 discrete global grid, Overture Maps, urban living standards, Global South, urban planning.

---

# 1. Introduction

Rapid urbanization across Southeast Asia and the broader Global South has generated pronounced spatial dualism, where hyper-dense informal settlements (*kampungs*) and master-planned luxury enclaves (*kota mandiri*) frequently sit immediately adjacent to each other, separated only by concrete perimeter walls or transport corridors (Dovey et al., 2021; Kuffer et al., 2016). In metropolitan regions like Greater Jakarta (Jabodetabek), Indonesia—home to over 35 million residents—these stark physical contrasts reflect deep disparities in shelter quality, public health exposure, and basic infrastructure access. Yet, despite the spatial prominence of this divide, public authorities and urban planners struggle to measure, monitor, and address these inequalities with actionable geographic precision.

## 1.1 The Challenge of Spatial Data Poverty in Developing Regions
The fundamental obstacle to tracking micro-scale urban disparity lies in systemic data scarcity (Abascal et al., 2022). In developed economies, urban research relies heavily on comprehensive municipal property databases, fine-grained census block summaries, and high-density cadastral mapping. In contrast, metropolitan regions across the Global South exist in an environment of acute geospatial data poverty. Official government censuses and socio-economic surveys are conducted infrequently—often at 5- to 10-year intervals—and are aggregated at coarse administrative levels (such as municipal *Kabupaten/Kota* boundaries). This administrative aggregation creates a severe Modifiable Areal Unit Problem (MAUP; Openshaw, 1984), completely averaging out the extreme micro-scale inequality that exists between neighboring streets (Reardon & O'Sullivan, 2004).

To bypass census limitations, researchers have increasingly turned to volunteered geographic information (VGI), predominantly OpenStreetMap (OSM). However, in developing cities, VGI exhibits severe geographical coverage voids and tagging incompleteness (Barrington-Leigh & Millard-Ball, 2017). In Indonesia, for instance, over 95% of building polygons in OSM remain unclassified (tagged simply as `building=yes`), and points of interest (POIs) such as clinics, schools, and grocery stores are heavily skewed toward affluent central commercial districts, while peri-urban and informal settlements remain largely unmapped.

## 1.2 The Limitations of Supervised Machine Learning Wealth Indices
Concurrently, computer vision and machine learning models trained on satellite imagery (e.g., Burke et al., 2021; Chi et al., 2022; Jean et al., 2016) have emerged as popular tools for estimating socioeconomic indicators. Most notably, Meta’s Relative Wealth Index (RWI; Chi et al., 2022) estimates wealth at a 2.4 km resolution across 135 low- and middle-income countries by training gradient-boosted trees on Demographic and Health Surveys (DHS) asset indices.

While valuable for broad regional screening, these approaches suffer from two core limitations when applied to urban spatial planning:
1. **The Relative Comparison Trap**: RWI calculates an asset wealth score relative to a country's national mean (as a normalized z-score). Consequently, a score of $+1.0$ in rural sub-Saharan Africa represents a completely different physical living standard than $+1.0$ in urban Java, preventing direct, absolute comparisons across international borders or even across urban-rural divides.
2. **The Asset-vs-Physical Decouple**: DHS surveys measure household ownership of consumer durable assets (e.g., mobile phones, televisions, refrigerators, motorcycles). In dense urban kampungs, many households own smartphones and consumer appliances, earning moderate or high asset scores, yet live in precarious conditions characterized by severe room overcrowding ($<5\text{ m}^2$ per person), unpaved alleys, open sewage canals, and hazardous particulate air pollution. Supervised asset models systematically miss this in-situ physical environmental deprivation.

## 1.3 Research Objectives and Questions
To overcome these limitations, this paper develops a transparent, reproducible, and unsupervised GeoAI framework that maps absolute physical living standards and autonomously pinpoints micro-segregation barriers using globally available, open spatial data. We frame this investigation around three primary research questions:
- **RQ1**: Can multi-source open remote sensing and open spatial geometries formulate an absolute physical living standard index that is continuous, unsupervised, and comparable across metropolitan boundaries?
- **RQ2**: Can an unsupervised Graph Attention Autoencoder (GAT-AE) detect micro-scale spatial disparity and segregation boundaries without ground-truth labels?
- **RQ3**: How do in-situ physical living standards systematically diverge from satellite-predicted consumer asset wealth (Meta RWI) across dense urban morphologies?

## 1.4 Primary Contributions
This paper makes four concrete contributions to spatial data science and urban planning:
1. **Formulation of the Physical Living Standard Index (PLSI)**: We propose a continuous, multidimensional metric composed of 10 physical indicators (living floor area, built density, pedestrian amenity access, bare soil, nighttime radiance, vegetative canopy, thermal comfort, water drainage, and air quality). Crucially, the index is calibrated against international physical baselines (the UN-Habitat $9.0\text{ m}^2$ shelter threshold, WHO air quality standards, and 15-minute walking catchments), enabling absolute cross-border comparability.
2. **Unsupervised Segregation Detection via Graph Attention Autoencoders**: We deploy a Spatial GAT Autoencoder over an equal-area hexagonal grid (Uber H3 Resolution 8, ~$0.74\text{ km}^2$). By enforcing local spatial continuity through a low-dimensional bottleneck ($d=2$), the model forces reconstruction error to spike where sharp feature discontinuities occur across physical barriers. We implement an attributed error decomposition ($\text{Friction}_{\text{socio}}$ vs. $\text{Friction}_{\text{bio}}$) to separate true socio-spatial barriers from natural land-cover transitions.
3. **Open Data Harmonization Architecture**: We establish a cloud-native pipeline combining Google Open Buildings v3 (2.5D heights), Overture Maps Foundation standardized entity themes, and multi-sensor satellite imagery (Sentinel-2, Landsat, VIIRS), eliminating reliance on closed proprietary data.
4. **Urban and Regional Planning Utility**: We operationalize the Spatial Palma Ratio and a 4-quadrant divergence framework (Asset Wealth vs. Physical Infrastructure), providing planning agencies with an interpretable, audit-ready tool to target infrastructure interventions.

## 1.5 Structure of the Paper
The remainder of this article is organized as follows: Section 2 reviews related literature and formulates the theoretical framework. Section 3 describes the Greater Jakarta study area and cloud data ingestion pipeline. Section 4 presents the 10-dimensional feature engineering methodology and the Spatial GAT-AE architecture. Section 5 reports empirical results, segregation case studies, and validation benchmarks. Section 6 discusses planning implications and transparent data limitations. Section 7 concludes with a roadmap for global transferability.

---

### Section 1 References

Abascal, E., Rothwell, R., Shonowo, A., et al. (2022). "Slum" severity index: A framework to assess spatial inequality in informal settlements. *Habitat International*, 123, 102554. https://doi.org/10.1016/j.habitatint.2022.102554

Barrington-Leigh, C., & Millard-Ball, A. (2017). The world's user-generated road map is more than 80% complete. *PLOS ONE*, 12(8), e0180698. https://doi.org/10.1371/journal.pone.0180698

Burke, M., Driscoll, A., Lobell, D. B., & Ermon, S. (2021). Using satellite imagery to understand and promote sustainable development. *Science*, 371(6535), eabe8628. https://doi.org/10.1126/science.abe8628

Chi, G., Fang, H., Chatterjee, S., & Blumenstock, J. E. (2022). Microestimating poverty with equity. *Proceedings of the National Academy of Sciences*, 119(3), e2113658119. https://doi.org/10.1073/pnas.2113658119

Dovey, K., van Oostrum, M., Chatterjee, I., & Titus, T. (2021). Towards a morphogenesis of informal settlements. *Habitat International*, 108, 102324. https://doi.org/10.1016/j.habitatint.2020.102324

Jean, N., Burke, M., Xie, M., Davis, W. M., Lobell, D. B., & Ermon, S. (2016). Combining satellite imagery and machine learning to predict poverty. *Science*, 353(6301), 790–794. https://doi.org/10.1126/science.aaf7894

Kuffer, M., Pfeffer, K., Sliuzas, R., & Baud, I. (2016). Slums from space—15 years of slum mapping using remote sensing. *Remote Sensing*, 8(6), 455. https://doi.org/10.3390/rs8060455

Openshaw, S. (1984). *The Modifiable Areal Unit Problem*. Geo Books.

Reardon, S. F., & O'Sullivan, D. (2004). Measures of spatial segregation. *Sociological Methodology*, 34(1), 121–162. https://doi.org/10.1111/j.0081-1750.2004.00150.x
