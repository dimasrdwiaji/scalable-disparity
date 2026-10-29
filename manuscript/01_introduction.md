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

Rapid urbanization across the Global South has produced complex spatial configurations, where dense informal settlements (such as Latin American *favelas*, South Asian *bustees*, or Southeast Asian *kampungs*) frequently neighbor master-planned residential developments and commercial centers (Dovey et al., 2021; Kuffer et al., 2016). In large metropolitan regions such as Greater Jakarta (Jabodetabek), Indonesia—home to over 35 million residents—these adjacent neighborhoods exhibit measurable differences in dwelling volume, open green space, pedestrian connectivity, and environmental exposure. Tracking these micro-scale variations remains challenging for urban and regional planning authorities who need consistent, fine-grained spatial evidence.

## 1.1 The Challenge of Spatial Data Scarcity in Developing Regions
A central constraint in evaluating micro-scale urban disparities is the scarcity of spatial data in many low- and middle-income regions (Abascal et al., 2022). In contrast to high-income countries where fine-grained municipal property records, tax registries, and high-frequency census blocks are maintained, developing metropolises often depend on official censuses conducted at multi-year intervals and aggregated to coarse administrative boundaries (such as districts or regencies). Administrative aggregation introduces the Modifiable Areal Unit Problem (MAUP; Openshaw, 1984), obscuring local spatial variations that occur across contiguous streets and residential quarters (Reardon & O'Sullivan, 2004).

Crowdsourced spatial data, most notably OpenStreetMap (OSM), have been widely used to supplement public records. However, in many developing cities, volunteered geographic information exhibits spatial unevenness and attribute gaps (Barrington-Leigh & Millard-Ball, 2017). Commercial corridors and central business districts often have relatively dense contributions, whereas peripheral and informal residential areas frequently contain unclassified building footprints (e.g., tagged simply as `building=yes`) or incomplete point-of-interest (POI) records for basic services like healthcare and primary education.

## 1.2 Characteristics of Supervised Machine Learning Wealth Indices
Recent advances in Earth observation and machine learning have facilitated large-scale estimation of socioeconomic indicators (Burke et al., 2021; Chi et al., 2022; Jean et al., 2016). A prominent global resource is Meta’s Relative Wealth Index (RWI; Chi et al., 2022), which predicts household wealth at a 2.4 km grid resolution across 135 low- and middle-income countries using satellite imagery, mobile network connectivity, and topographic data calibrated against Demographic and Health Surveys (DHS).

While valuable for broad regional screening and humanitarian targeting, supervised wealth models have specific characteristics that warrant attention in urban spatial analysis:
1. **Relative Index Normalization**: RWI models are trained on within-country survey asset scores normalized to standard deviations from the national mean (mean zero, unit variance). Consequently, an RWI score reflects relative economic position within a specific country rather than an absolute measure of physical living conditions. A score of +1.0 in a predominantly rural country represents a different built environment than +1.0 in an urbanized economy, which limits standardized cross-border comparisons.
2. **Divergence Between Household Assets and the Physical Built Environment**: Household surveys typically record ownership of consumer durable assets, such as mobile phones, televisions, refrigerators, and personal vehicles (Rutstein & Johnson, 2004). In dense urban informal settlements, households may possess consumer durables while living in environments with limited living floor area (<9.0 m² per person), unpaved lanes, restricted drainage, and elevated particulate air pollution. Models trained on durable asset ownership can classify these areas as relatively well-off, reflecting household consumer goods rather than neighborhood physical living conditions.
3. **Data Access and Auditability**: Several high-resolution predictive models incorporate proprietary telecommunications or social platform connectivity data (Blumenstock et al., 2015). For public planning agencies, relying on closed data pipelines can complicate independent audits and long-term methodological replication.

## 1.3 Research Objectives and Questions
To complement existing survey-trained wealth indices, this study develops an unsupervised, cloud-native GeoAI framework that maps absolute physical living standards and identifies micro-scale spatial boundaries using open spatial datasets. We structure the inquiry around three research questions:
- **RQ1**: How can multi-source open remote sensing and open spatial geometries be integrated into an unsupervised, continuous Physical Living Standard Index that is comparable across administrative boundaries?
- **RQ2**: Can an unsupervised Graph Attention Autoencoder (GAT-AE) detect micro-scale spatial disparity and segregation boundaries without ground-truth training labels?
- **RQ3**: How do in-situ physical living standards diverge from satellite-predicted consumer asset wealth (Meta RWI) across dense urban residential morphologies?

## 1.4 Primary Contributions
This paper provides four main contributions:
1. **Derivation of the Physical Living Standard Index (PLSI)**: We formulate an interpretable index combining 10 physical dimensions (living floor area, built density, pedestrian amenity access, bare soil, nighttime radiance, vegetative canopy, thermal comfort, water drainage, and air quality). The indicators are anchored to recognized physical baselines, including UN-Habitat living space criteria (9.0 m² per person), WHO air quality guidelines, and 15-minute walking catchments.
2. **Unsupervised Disparity Detection via Graph Attention Autoencoders**: We deploy a Spatial GAT Autoencoder over a discrete global grid (Uber H3 Resolution 8, ~0.74 km²). By constraining latent dimensionality (d = 2) across geometric adjacency, the model establishes local continuity expectations, causing reconstruction error to increase where abrupt feature transitions occur. Attributed error decomposition separates socio-spatial discontinuities from biophysical land-cover edges.
3. **Open Data Integration Pipeline**: We demonstrate a reproducible pipeline combining Google Open Buildings v3 (2.5D heights), Overture Maps Foundation standardized point-of-interest data, and open satellite observations (Sentinel-2, Landsat, VIIRS), reducing dependence on proprietary datasets.
4. **Planning Relevance and Divergence Analysis**: We apply the Spatial Palma Ratio and a four-quadrant comparison framework (Asset Wealth vs. Physical Infrastructure) to provide urban and regional planners with an auditable tool for identifying infrastructure deficits in dense informal areas.

## 1.5 Structure of the Paper
The remainder of this article is organized as follows: Section 2 reviews relevant literature on remote sensing wealth estimation, 3D building morphology, pedestrian accessibility, and graph neural networks, concluding with the four-quadrant divergence framework. Section 3 outlines the study area and cloud data ingestion workflow. Section 4 presents the 10-dimensional feature engineering methodology and Spatial GAT-AE architecture. Section 5 discusses empirical results and validation benchmarks. Section 6 addresses planning implications and data limitations. Section 7 concludes with considerations for global transferability.

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
