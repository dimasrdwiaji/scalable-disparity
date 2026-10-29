# Scalable GeoAI for Measuring Micro-Scale Physical Living Standards and Spatial Disparities: Integrating Open Buildings, Standardized Point-of-Interest Data, and Graph Attention Autoencoders

**Author**: Dimas RD  
**Affiliation**: Urban Informatics and Spatial Artificial Intelligence Laboratory  
**Target Venue**: *ISPRS International Journal of Geo-Information* (IJGI) / *PLOS ONE* / EarthArXiv  
**Standard**: Publication Manual of the American Psychological Association (7th ed.; APA 7)  

---

### Abstract
Measuring socio-spatial disparities and physical living conditions in rapidly urbanizing regions of the Global South is constrained by spatial data scarcity, administrative boundary aggregation, and the relative normalization of survey-based wealth models. This study presents an unsupervised GeoAI framework that maps physical living standards and identifies micro-scale spatial discontinuities across the 12,800 km² Jabodetabek metropolitan region and Karawang Regency, Indonesia. We combine Google Open Buildings v3 (2.5D building heights) intersected with European Commission JRC GHS-BUILT-C residential masks, Overture Maps Foundation points of interest (POIs), Sentinel-2 multi-spectral indices, Landsat land surface temperature, Open-Meteo air quality reanalysis, and NASA VIIRS nighttime radiance onto 17,300 Uber H3 Resolution 8 hexagonal cells (~0.74 km²). We formulate a 10-dimensional Physical Living Standard Index (PLSI) calibrated against international shelter, environmental health, and pedestrian accessibility guidelines (UN-Habitat 9.0 m² living area baseline, WHO PM2.5 guidelines, and 15-minute walking catchments). To detect spatial boundaries without ground-truth training labels, we deploy a Spatial Graph Attention Autoencoder (GAT-AE) over hexagonal geometric adjacency. Constraining latent dimensionality (d = 2) encourages local spatial continuity, causing reconstruction error to increase where abrupt feature differences occur across physical and social boundaries dividing master-planned residential developments from dense informal settlements. Attributed error decomposition distinguishes socio-spatial boundaries from natural land-cover transitions. A four-quadrant comparison against Meta's Relative Wealth Index illustrates that asset-based measures can diverge from in-situ physical living conditions in dense, asset-holding informal neighborhoods. This framework provides urban and regional planners with an auditable, continuous instrument to evaluate physical living conditions without survey lag.

*Keywords*: GeoAI, spatial segregation, informal settlements, Graph Attention Networks, H3 discrete global grid, Overture Maps, urban living standards, Global South, urban planning.

---

# 1. Introduction

Rapid urbanization across the Global South has produced fragmented urban landscapes where dense informal settlements (such as Latin American *favelas*, South Asian *bustees*, or Southeast Asian *kampungs*) frequently neighbor master-planned residential enclaves and commercial centers (Dovey et al., 2021; Kuffer et al., 2016). In metropolitan regions such as Greater Jakarta (Jabodetabek), Indonesia—inhabited by over 35 million people—adjacent neighborhoods exhibit measurable disparities in residential volume, open green space, pedestrian connectivity, and environmental exposure. Tracking these micro-scale differences remains challenging for planning authorities who require consistent, fine-grained spatial evidence.

## 1.1 Spatial Data Scarcity in Developing Regions
Evaluating micro-scale disparities is constrained by the scarcity of fine-grained spatial data across many low- and middle-income regions (Abascal et al., 2022). Unlike high-income settings with detailed municipal property registries and frequent census updates, developing cities often rely on decennial censuses aggregated to coarse administrative boundaries. This administrative aggregation introduces the Modifiable Areal Unit Problem (MAUP; Openshaw, 1984), obscuring local variations across contiguous streets (Reardon & O'Sullivan, 2004). While crowdsourced spatial data—primarily OpenStreetMap (OSM)—partially address census gaps, volunteered geographic information displays spatial unevenness and attribute incompleteness in peripheral and informal areas (Barrington-Leigh & Millard-Ball, 2017).

## 1.2 Characteristics of Supervised Machine Learning Wealth Indices
Recent advances in Earth observation and machine learning have enabled large-scale estimation of socioeconomic indicators (Burke et al., 2021; Chi et al., 2022; Jean et al., 2016). Meta's Relative Wealth Index (RWI; Chi et al., 2022) provides a prominent example, predicting wealth at 2.4 km resolution across 135 countries using satellite imagery, mobile connectivity, and demographic surveys. 

While valuable for regional screening, supervised wealth models exhibit two notable characteristics in urban settings:
1. **Relative Metric Normalization**: Because training targets derive from within-country Demographic and Health Surveys (DHS) normalized to national z-scores, RWI reflects relative economic rank within a given country rather than an absolute physical living standard, complicating cross-border comparisons.
2. **Decoupling of Asset Ownership and Built Environment**: Survey asset indices measure consumer durable ownership (e.g., phones, appliances, vehicles; Rutstein & Johnson, 2004). In dense informal settlements, households may possess consumer electronics while experiencing pronounced floor-space constraints (<9.0 m² per person), unpaved alleys, open drainage canals, and elevated ambient air pollution. Asset-based models classify these areas as relatively affluent, capturing private consumer capital rather than neighborhood physical environmental conditions (Blumenstock et al., 2015).

## 1.3 Research Objectives and Contributions
This study introduces an unsupervised GeoAI framework that integrates open remote sensing and spatial geometry to map physical living standards and identify micro-scale spatial boundaries. We address three research questions:
- **RQ1**: How can multi-source open remote sensing and open spatial geometries formulate an unsupervised, continuous Physical Living Standard Index comparable across administrative boundaries?
- **RQ2**: Can an unsupervised Graph Attention Autoencoder (GAT-AE) detect micro-scale spatial disparity and segregation boundaries without ground-truth labels?
- **RQ3**: How do in-situ physical living standards diverge from satellite-predicted consumer asset wealth (Meta RWI) across dense urban residential morphologies?

We make four primary contributions:
1. **Formulation of the Physical Living Standard Index (PLSI)**: A continuous metric spanning 10 physical dimensions calibrated against international shelter (UN-Habitat 9.0 m² baseline), environmental health (WHO air quality), and 15-minute walking catchments.
2. **Unsupervised Boundary Detection via Spatial GAT-AE**: Repurposing network over-smoothing through a low-dimensional bottleneck ($d=2$) over hexagonal spatial adjacency (Uber H3 Res 8, ~0.74 km²) to highlight socio-spatial severance, accompanied by attributed error decomposition.
3. **Open Spatial Data Integration**: An open pipeline harmonizing Google Open Buildings v3 (2.5D heights), Overture Maps standardized points of interest, and open satellite observations (Sentinel-2, Landsat, VIIRS).
4. **Planning Utility**: Application of the Spatial Palma Ratio and a 4-quadrant divergence framework (Asset Wealth vs. Physical Living Standards) to support targeted municipal infrastructure investments.

The remainder of this paper is structured as follows: Section 2 reviews related literature and introduces the theoretical framework. Section 3 outlines the study area and data ingestion pipeline. Section 4 presents the feature engineering and Spatial GAT-AE architecture. Section 5 evaluates empirical results and validation benchmarks. Section 6 discusses planning implications and data limitations. Section 7 concludes with considerations for global transferability.

---

### Section 1 References

Abascal, E., Rothwell, R., Shonowo, A., et al. (2022). "Slum" severity index: A framework to assess spatial inequality in informal settlements. *Habitat International*, 123, 102554. https://doi.org/10.1016/j.habitatint.2022.102554

Barrington-Leigh, C., & Millard-Ball, A. (2017). The world's user-generated road map is more than 80% complete. *PLOS ONE*, 12(8), e0180698. https://doi.org/10.1371/journal.pone.0180698

Blumenstock, J., Cadamuro, G., & On, R. (2015). Predicting poverty and wealth from mobile phone metadata. *Science*, 350(6264), 1073–1077. https://doi.org/10.1126/science.aac4420

Burke, M., Driscoll, A., Lobell, D. B., & Ermon, S. (2021). Using satellite imagery to understand and promote sustainable development. *Science*, 371(6535), eabe8628. https://doi.org/10.1126/science.abe8628

Chi, G., Fang, H., Chatterjee, S., & Blumenstock, J. E. (2022). Microestimating poverty with equity. *Proceedings of the National Academy of Sciences*, 119(3), e2113658119. https://doi.org/10.1073/pnas.2113658119

Dovey, K., Pafka, E., & Ristic, M. (2021). *Mapping urbanities: Morphologies, flows, possibilities*. Routledge.

Jean, N., Burke, M., Xie, M., Davis, W. M., Lobell, D. B., & Ermon, S. (2016). Combining satellite imagery and machine learning to predict poverty. *Science*, 353(6301), 790–794. https://doi.org/10.1126/science.aaf7894

Kuffer, M., Pfeffer, K., Sliuzas, R., & Baud, I. (2016). Slums from space—15 years of slum mapping using remote sensing. *Remote Sensing*, 8(6), 455. https://doi.org/10.3390/rs8060455

Openshaw, S. (1984). *The Modifiable Areal Unit Problem*. Geo Books.

Reardon, S. F., & O'Sullivan, D. (2004). Measures of spatial segregation. *Sociological Methodology*, 34(1), 121–162. https://doi.org/10.1111/j.0081-1750.2004.00150.x

Rutstein, S. O., & Johnson, K. (2004). *The DHS wealth index* (DHS Comparative Reports No. 6). ORC Macro.
