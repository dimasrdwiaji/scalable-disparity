import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Condensed Section 1
sec1_content = """# Scalable GeoAI for Measuring Micro-Scale Physical Living Standards and Spatial Disparities: Integrating Open Buildings, Standardized Point-of-Interest Data, and Graph Attention Autoencoders

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
2. **Decoupling of Asset Ownership and Built Environment**: Survey asset indices measure consumer durable ownership (e.g., phones, appliances, vehicles; Rutstein & Johnson, 2004). In dense informal settlements, households may possess consumer electronics while experiencing severe floor-space constraints (<9.0 m² per person), unpaved alleys, open drainage canals, and elevated ambient air pollution. Asset-based models classify these areas as relatively affluent, capturing private consumer capital rather than neighborhood physical environmental conditions (Blumenstock et al., 2015).

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
"""

# Condensed Section 2
sec2_content = """# 2. Literature Review and Theoretical Framework

Evaluating urban living conditions across expanding metropolitan regions in the developing world draws on four complementary fields: remote sensing of socioeconomic indicators, 3D building morphology, pedestrian accessibility modeling, and graph neural networks for spatial anomaly detection. We synthesize these areas into a four-quadrant divergence framework that contrasts asset-based wealth with in-situ physical living standards.

## 2.1 Remote Sensing and Machine Learning for Socioeconomic Estimation
Satellite Earth observation has long supported socioeconomic monitoring. Nocturnal luminosity (DMSP and VIIRS) serves as an established proxy for regional economic activity and electrification (Henderson et al., 2012; Mellander et al., 2015), but encounters saturation in commercial cores and blooming across unpopulated surfaces (Zhao et al., 2019). To improve spatial resolution, transfer learning models use daytime multi-spectral imagery to predict nighttime radiance, learning visual features that correlate with local survey expenditures (Burke et al., 2021; Jean et al., 2016; Yeh et al., 2020). Meta’s Relative Wealth Index (RWI; Chi et al., 2022) scaled this approach to 135 countries at 2.4 km resolution by training gradient-boosted trees on satellite, mobility, and connectivity data against Demographic and Health Surveys (DHS). 

However, survey asset targets capture household durable goods ownership (Rutstein & Johnson, 2004). In dense urban settlements, asset accumulation can decouple from physical living conditions: households may own mobile devices and appliances while residing in overcrowded structures with unpaved access and open drainage canals.

## 2.2 Built-Environment Morphology and Living Space Sufficiency
Urban remote sensing has traditionally identified informal settlements through distinct morphological signatures: dense building configurations, organic street layouts, small footprints, and heterogeneous roofing (Kohli et al., 2012; Sliuzas et al., 2010). Early studies framed detection as binary "slum vs. formal" image classification (Kuffer et al., 2016, 2020; Wurm et al., 2019). While computationally effective, binary classifications obscure progressive consolidation (Dovey et al., 2020) and ignore the multidimensional continuum of living conditions (Abascal et al., 2022; Lilford et al., 2019).

To measure conditions continuously, UN-Habitat (2003, 2020) establishes five shelter deprivation criteria: durable construction, access to improved water, adequate sanitation, tenure security, and sufficient living area (<9.0 m² per person). Estimating floor area per capita historically proved difficult from 2D overhead imagery. Recent open planetary-scale building datasets, particularly Google Open Buildings v3 (Sirko et al., 2021) with 2.5D heights, now enable volumetric morphology estimation across the Global South (Biljecki et al., 2023, 2024). Intersecting building volumes with ambient population data (WorldPop; Tatem, 2017) and functional residential masks (JRC GHS-BUILT-C; Schiavina et al., 2022) enables continuous estimation of living floor area per capita across regional extents.

## 2.3 Pedestrian Accessibility and Open Spatial Data
Physical living standards also depend on spatial access to basic public amenities, including healthcare, education, retail, and green space (Geurs & van Wee, 2004; Handy & Niemeier, 1997). The "15-minute city" concept emphasizes reachable daily services within a 15-minute walk (Moreno et al., 2021). Cumulative opportunity thresholds (destinations within a fixed walking catchment at 4.0 km/h) offer intuitive, policy-relevant metrics compared to gravity models (Hosford et al., 2022; Weiss et al., 2018).

In fragmented cities, Euclidean buffer distances can substantially overestimate accessibility (Boeing, 2017). Rapid suburban expansion frequently situates enclosed master-planned developments beside informal settlements (Dovey et al., 2021; Firman, 2004). Perimeter walls and highway barriers require multi-kilometer pedestrian detours, making topological network routing essential. While OpenStreetMap enables open routing (Boeing, 2017), volunteer contributions remain uneven in peripheral areas (Barrington-Leigh & Millard-Ball, 2017). The Overture Maps Foundation (2023, 2024) addresses this gap by combining open registries and algorithmic extraction into a standardized Global Entity Reference System (GERS).

## 2.4 Graph Neural Networks and Spatial Anomaly Detection
Unsupervised disparity detection across continuous space requires structural learning methods beyond linear spatial autocorrelation statistics (Anselin, 1995; Reardon & O'Sullivan, 2004). Graph Neural Networks (GNNs), such as Graph Convolutional Networks (GCNs; Kipf & Welling, 2016) and Graph Attention Networks (GATs; Veličković et al., 2018), learn representations over non-Euclidean spatial graphs where hexagonal cells form nodes and geometric adjacency forms edges (Zhang et al., 2022).

Deep GNNs often encounter "over-smoothing," where repeated neighborhood message passing homogenizes node embeddings (Chen et al., 2020; Kipf & Welling, 2016). In unsupervised anomaly detection, this characteristic can be repurposed. By training a Graph Attention Autoencoder (GAT-AE) with a narrow bottleneck ($d=2$) over pure geometric adjacency, the model enforces local spatial continuity. Where an edge crosses an abrupt socio-spatial boundary, message passing aggregates conflicting feature distributions, resulting in elevated reconstruction errors at the interface. Drawing on attributed graph anomaly frameworks (DOMINANT; Ding et al., 2019), attributed error decomposition separates built-environment indicators from biophysical land-cover edges:
$$\\text{Reconstruction Error}_i = \\sum_{k=1}^M (x_{ik} - \\hat{x}_{ik})^2$$

## 2.5 Theoretical Synthesis: The 4-Quadrant Divergence Framework
We synthesize these domains into the **4-Quadrant Divergence Framework**, conceptualizing urban space along two axes: Consumer Asset Wealth (Meta RWI) and In-Situ Physical Living Standards (PLSI).

```
                  High Physical Living Standard (PLSI)
                                  ▲
                                  │
                 Quadrant III     │     Quadrant I
            (Subsidized Formal /  │ (Integrated Affluent /
             Well-Serviced Low-   │  Master-Planned Enclaves)
             Income Peripheries)  │
                                  │
◄─────────────────────────────────┼─────────────────────────────────►
Low Asset Wealth (Meta RWI)       │       High Asset Wealth (Meta RWI)
                                  │
                 Quadrant II      │     Quadrant IV
            (Unserviced Informal  │  (Asset-Dense, Infrastructure-
             Deprivation / Rural  │   Deprived Informal Settlements)
             Poverty)             │
                                  ▼
                   Low Physical Living Standard (PLSI)
```

- **Quadrant I (High Asset, High Physical)**: Formal residential communities with large dwelling areas, tree cover, and walkable amenities.
- **Quadrant II (Low Asset, Low Physical)**: Unplanned settlements and impoverished peri-urban areas lacking private assets and public services.
- **Quadrant III (Low Asset, High Physical)**: Subsidized public housing with modest household assets but planned dwelling volumes, drainage, and paved access.
- **Quadrant IV (High Asset, Low Physical)**: Established dense informal settlements where households hold durable goods (appliances, vehicles) but endure floor-space deprivation (<9.0 m²), open drainage, and elevated particulate air pollution.

Supervised models trained on survey asset indices often conflate Quadrant IV with Quadrant I, obscuring local infrastructure deficits. The unsupervised PLSI framework provides an empirical tool to evaluate both dimensions independently.

---

### Section 2 References

Abascal, E., Rothwell, R., Shonowo, A., et al. (2022). "Slum" severity index: A framework to assess spatial inequality in informal settlements. *Habitat International*, 123, 102554. https://doi.org/10.1016/j.habitatint.2022.102554

Anselin, L. (1995). Local indicators of spatial association—LISA. *Geographical Analysis*, 27(2), 93–115. https://doi.org/10.1111/j.1538-4632.1995.tb00338.x

Barrington-Leigh, C., & Millard-Ball, A. (2017). The world's user-generated road map is more than 80% complete. *PLOS ONE*, 12(8), e0180698. https://doi.org/10.1371/journal.pone.0180698

Biljecki, F., Chow, Y. S., & Stouffs, R. (2023). Quality of building height data in OpenStreetMap and its impact on urban analytics. *International Journal of Applied Earth Observation and Geoinformation*, 124, 103525. https://doi.org/10.1016/j.jag.2023.103525

Biljecki, F., Zhao, T., Liang, X., & Hou, Y. (2024). Global building height and volume estimation using open satellite and vector data. *ISPRS Journal of Photogrammetry and Remote Sensing*, 208, 112–132. https://doi.org/10.1016/j.isprsjprs.2024.01.012

Boeing, G. (2017). OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks. *Computers, Environment and Urban Systems*, 65, 126–139. https://doi.org/10.1016/j.compenvurbsys.2017.05.004

Burke, M., Driscoll, A., Lobell, D. B., & Ermon, S. (2021). Using satellite imagery to understand and promote sustainable development. *Science*, 371(6535), eabe8628. https://doi.org/10.1126/science.abe8628

Chen, D., Lin, Y., Li, W., Li, P., Zhou, J., & Sun, X. (2020). Measuring and relieving over-smoothing problem for graph neural networks from the topological view. *Proceedings of the AAAI Conference on Human Computation and Crowdsourcing*, 34(04), 3438–3445. https://doi.org/10.1609/aaai.v34i04.5747

Chi, G., Fang, H., Chatterjee, S., & Blumenstock, J. E. (2022). Microestimating poverty with equity. *Proceedings of the National Academy of Sciences*, 119(3), e2113658119. https://doi.org/10.1073/pnas.2113658119

Ding, K., Li, J., Bhanushali, R., & Liu, H. (2019). Deep anomaly detection on attributed networks. *Proceedings of the 2019 SIAM International Conference on Data Mining (SDM)*, 594–602. https://doi.org/10.1137/1.9781611975673.67

Dovey, K., van Oostrum, M., Chatterjee, I., & Titus, T. (2020). Towards a morphogenesis of informal settlements. *Habitat International*, 108, 102324. https://doi.org/10.1016/j.habitatint.2020.102324

Dovey, K., Pafka, E., & Ristic, M. (2021). *Mapping urbanities: Morphologies, flows, possibilities*. Routledge.

Firman, T. (2004). New town development in Jakarta Metropolitan Region: A perspective of spatial segregation. *Habitat International*, 28(3), 349–368. https://doi.org/10.1016/S0197-3975(03)00037-7

Geurs, K. T., & van Wee, B. (2004). Accessibility evaluation of land-use and transport strategies: Review and research directions. *Journal of Transport Geography*, 12(2), 127–140. https://doi.org/10.1016/j.jtrangeo.2003.10.005

Handy, S. L., & Niemeier, D. A. (1997). Measuring accessibility: An exploration of issues and alternatives. *Environment and Planning A: Economy and Space*, 29(7), 1175–1194. https://doi.org/10.1068/a291175

Henderson, J. V., Storeygard, A., & Weil, D. N. (2012). Measuring economic growth from outer space. *American Economic Review*, 102(2), 994–1028. https://doi.org/10.1257/aer.102.2.994

Hosford, K., Beairsto, J., & Winters, M. (2022). Is the 15-minute city within reach? Evaluating walking-scale accessibility in Canadian cities. *Transport Findings*, 32454. https://doi.org/10.32866/001c.32454

Jean, N., Burke, M., Xie, M., Davis, W. M., Lobell, D. B., & Ermon, S. (2016). Combining satellite imagery and machine learning to predict poverty. *Science*, 353(6301), 790–794. https://doi.org/10.1126/science.aaf7894

Kipf, T. N., & Welling, M. (2016). Semi-supervised classification with graph convolutional networks. *arXiv preprint arXiv:1609.02907*. https://arxiv.org/abs/1609.02907

Kohli, D., Sliuzas, R., Kerle, N., & Stein, A. (2012). An ontology of slums for image-based classification. *Computers, Environment and Urban Systems*, 36(2), 154–163. https://doi.org/10.1016/j.compenvurbsys.2011.11.001

Kuffer, M., Pfeffer, K., Sliuzas, R., & Baud, I. (2016). Slums from space—15 years of slum mapping using remote sensing. *Remote Sensing*, 8(6), 455. https://doi.org/10.3390/rs8060455

Kuffer, M., Thomson, D. R., Boo, G., Mahabir, R., Grippa, T., Vanhuysse, S., ... & Sliuzas, R. (2020). The role of Earth observation in an integrated deprivation information system for understanding who lives where in cities. *Computers, Environment and Urban Systems*, 80, 101429. https://doi.org/10.1016/j.compenvurbsys.2019.101429

Lilford, R. J., Oyebode, O., Satterthwaite, D., Melendez-Torres, G. J., Chen, Y. F., Mberu, B., ... & Watson, S. I. (2019). Improving the health and welfare of people who live in slums. *The Lancet*, 389(10068), 559–570. https://doi.org/10.1016/S0140-6736(16)31848-7

Mellander, C., Lobo, J., Stolarick, K., & Matheson, Z. (2015). Night-time light data: A good proxy measure for economic activity? *PLOS ONE*, 10(10), e0139779. https://doi.org/10.1371/journal.pone.0139779

Moreno, C., Allam, Z., Chabaud, D., Gall, C., & Pratlong, F. (2021). Introducing the "15-Minute City": Sustainability, resilience and place identity in future post-pandemic cities. *Smart Cities*, 4(1), 93–111. https://doi.org/10.3390/smartcities4010006

Overture Maps Foundation. (2023). *Overture Maps data release and schema documentation*. Linux Foundation. https://overturemaps.org

Overture Maps Foundation. (2024). *Global Entity Reference System (GERS) specification*. Linux Foundation. https://docs.overturemaps.org/gers/

Reardon, S. F., & O'Sullivan, D. (2004). Measures of spatial segregation. *Sociological Methodology*, 34(1), 121–162. https://doi.org/10.1111/j.0081-1750.2004.00150.x

Rutstein, S. O., & Johnson, K. (2004). *The DHS wealth index* (DHS Comparative Reports No. 6). ORC Macro.

Schiavina, M., Melchiorri, M., & Pesaresi, M. (2022). *GHSL Data Package 2022*. Publications Office of the European Union. https://doi.org/10.2760/19817

Sirko, W., Kashubin, S., Luccioni, M., Diertani, N., Gupta, M., Lee, C., ... & Chen, H. (2021). Continental-scale building detection from high resolution satellite imagery. *arXiv preprint arXiv:2107.12281*. https://arxiv.org/abs/2107.12281

Sliuzas, R., Mboup, G., & de Sherbinin, A. (2010). Slum indicators and spatial analysis. In *Proceedings of the 2010 IEEE International Geoscience and Remote Sensing Symposium* (pp. 3845–3848). IEEE. https://doi.org/10.1109/IGARSS.2010.5652579

Tatem, A. J. (2017). WorldPop, open data for global good. *Scientific Data*, 4(1), 170004. https://doi.org/10.1038/sdata.2017.4

United Nations Human Settlements Programme. (2003). *The challenge of slums: Global report on human settlements 2003*. Earthscan Publications.

United Nations Human Settlements Programme. (2020). *World cities report 2020: The value of sustainable urbanization*. UN-Habitat.

Veličković, P., Cucurull, G., Casanova, A., Romero, A., Liò, P., & Bengio, Y. (2018). Graph attention networks. *International Conference on Learning Representations (ICLR)*. https://arxiv.org/abs/1710.10903

Weiss, D. J., Nelson, A., Gibson, H. S., Temperley, W., Peedell, S., Lieber, A., ... & Gething, P. W. (2018). A global map of travel time to cities to assess inequalities in accessibility in 2015. *Nature*, 553(7688), 333–336. https://doi.org/10.1038/nature25181

Wurm, M., Stark, T., Zhu, X. X., Weigand, M., & Taubenböck, H. (2019). Semantic segmentation of slums in satellite images using transfer learning on fully convolutional neural networks. *ISPRS Journal of Photogrammetry and Remote Sensing*, 150, 59–69. https://doi.org/10.1016/j.isprsjprs.2019.02.006

Yeh, C., Perez, A., Driscoll, A., Azzari, G., Tang, Z., Lobell, D., Ermon, S., & Burke, M. (2020). Using publicly available satellite imagery and deep learning to understand economic well-being in Africa. *Nature Communications*, 11(1), 2583. https://doi.org/10.1038/s41467-020-16185-w

Zhang, C., Jing, W., & Yao, Y. (2022). A review of deep learning in spatial-temporal data analysis. *ISPRS International Journal of Geo-Information*, 11(7), 405. https://doi.org/10.3390/ijgi11070405

Zhao, M., Zhou, Y., Li, X., Zhou, C., Cheng, W., Li, M., & Huang, K. (2019). Building a series of consistent night-time light data (1992–2018) in Southeast Asia by integrating DMSP-OLS and NPP-VIIRS. *IEEE Transactions on Geoscience and Remote Sensing*, 58(3), 1843–1856. https://doi.org/10.1109/TGRS.2019.2949797
"""

paths = [
    ('c:/Users/Dimas RD/Documents/projects/phys_living_index/manuscript/01_introduction.md', sec1_content),
    ('c:/Users/Dimas RD/Documents/projects/wip/manuscript/01_introduction.md', sec1_content),
    ('c:/Users/Dimas RD/Documents/projects/phys_living_index/manuscript/02_literature_review.md', sec2_content),
    ('c:/Users/Dimas RD/Documents/projects/wip/manuscript/02_literature_review.md', sec2_content)
]

for p, content in paths:
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Wrote {p}")

# Report stats
for name, content in [('01_introduction.md', sec1_content), ('02_literature_review.md', sec2_content)]:
    parts = content.split('### Section')
    body = parts[0]
    refs = parts[1] if len(parts) > 1 else ''
    print(f"\n{name} Stats:")
    print(f"  Body words: {len(body.split())} (~{len(body.split())/450:.1f} pages at 450 words/page)")
    print(f"  Reference words: {len(refs.split())}")
    print(f"  Total words: {len(content.split())}")
