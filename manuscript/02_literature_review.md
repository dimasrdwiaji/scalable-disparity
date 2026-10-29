# 2. Literature Review and Theoretical Framework

Measuring socioeconomic conditions and living standards across rapidly expanding metropolitan regions in the developing world presents well-documented methodological challenges. This section reviews four related domains of research: (a) satellite remote sensing and machine learning models for socioeconomic estimation, (b) 3D building morphology and informal settlement characterization, (c) pedestrian accessibility and open spatial data infrastructures, and (d) graph neural networks for spatial anomaly detection. We conclude by synthesizing these insights into a theoretical four-quadrant divergence framework that contrasts asset-based wealth measures with in-situ physical living standards.

## 2.1 Remote Sensing and Machine Learning for Socioeconomic Estimation

Over the past decade, Earth observation and machine learning have expanded the scope of large-scale socioeconomic monitoring (Burke et al., 2021; Jean et al., 2016). Studies have demonstrated that nocturnal luminosity recorded by satellite sensors—such as the Defense Meteorological Satellite Program (DMSP) and the Visible Infrared Imaging Radiometer Suite (VIIRS)—correlates with gross regional product, electrification rates, and aggregated economic activity (Henderson et al., 2012; Mellander et al., 2015). However, nighttime radiance tends to saturate in dense commercial cores and bloom across unpopulated surfaces, which limits its ability to differentiate micro-scale residential differences (Zhao et al., 2019).

To address the spatial resolution constraints of nighttime lights, transfer learning frameworks were developed to extract visual features from daytime multi-spectral imagery. Jean et al. (2016) demonstrated that convolutional neural networks (CNNs) pretrained on ImageNet and fine-tuned to predict nighttime radiance from high-resolution daytime imagery could identify local economic clusters across five African nations, explaining up to 75% of the variation in local survey expenditures. Subsequent studies extended this approach using multi-task deep learning architectures and multi-spectral sensors (Burke et al., 2021; Yeh et al., 2020), showing that visual features such as roof material, road paving, agricultural field patterns, and building density correlate with household survey outcomes.

A widely used global dataset is Meta’s Relative Wealth Index (RWI; Chi et al., 2022). By combining high-resolution satellite imagery, topographic models, mobile telecommunication connectivity data, and user network connectivity graphs, Chi et al. trained gradient-boosted decision trees (XGBoost) against Demographic and Health Surveys (DHS) conducted across 135 low- and middle-income countries. RWI provides gridded wealth estimates at a 2.4 km resolution globally, supporting regional resource allocation and humanitarian assessments.

Alongside their utility, supervised satellite wealth models have specific structural characteristics that are relevant for metropolitan urban planning:
1. **Relative Metric Normalization**: Because DHS surveys are conducted independently across different nations and survey waves, the target variable in supervised models is typically normalized as a within-country asset wealth score (a standardized z-score with mean zero and unit variance). Consequently, an RWI score of +1.0 reflects relative economic standing within a specific national distribution rather than an absolute level of material living conditions. An RWI value of +1.0 in a predominantly rural country reflects a different physical built environment than +1.0 in an urbanized economy, which complicates direct cross-border comparisons.
2. **Decoupling of Asset Capital from Built Environmental Conditions**: Household surveys primarily measure ownership of consumer durable goods—such as smartphones, televisions, refrigerators, motorcycles, and cooking stoves (Rutstein & Johnson, 2004). While durable asset ownership differentiates relative poverty in rural settings, it can decouple from physical living conditions in dense urban settlements. In established informal settlements across the Global South, families may accumulate consumer electronics and personal transport while residing in environments characterized by limited floor area (<9.0 m² per person), unpaved lanes, open drainage canals, and elevated ambient particulate air pollution. Models trained on durable asset ownership can classify these settlements as moderately affluent, capturing private consumer capital rather than neighborhood physical environmental conditions.
3. **Accessibility and Auditability of Data**: Several high-resolution socioeconomic models incorporate proprietary data sources, such as mobile network call detail records (CDRs; Blumenstock et al., 2015) or commercial platform graphs. These proprietary sources are rarely accessible to municipal planning agencies, cannot be easily audited by external researchers, and raise data privacy considerations.

## 2.2 Built-Environment Morphology, 3D Building Geometry, and Informal Settlement Detection

To evaluate physical urban living conditions, urban remote sensing has historically focused on mapping informal settlements and slums (Kuffer et al., 2016, 2020). Informal settlements represent spatial manifestations of rapid urbanization characterized by distinct morphological patterns: high building coverage, organic street configurations, small dwelling footprints, limited vegetative cover, and heterogeneous roofing materials (Kohli et al., 2012; Sliuzas et al., 2010).

Remote sensing approaches frequently framed informal settlement detection as a binary classification problem: labeling spatial units as either "slum" or "formal" using texture metrics (e.g., Gray-Level Co-occurrence Matrix; GLCM) or object-based image analysis (OBIA) applied to very high-resolution (VHR) aerial or commercial satellite imagery (Kuffer et al., 2016; Wurm et al., 2019). While effective for classification benchmarks, binary categorizations present two practical limitations. First, they simplify heterogeneous communities that experience progressive physical consolidation (Dovey et al., 2020). Second, binary labels mask the multidimensional continuum of living conditions: two settlements categorized as informal may have different access levels to piped water, road paving, and structural safety (Abascal et al., 2022; Lilford et al., 2019).

To evaluate living conditions continuously, research can draw upon established international shelter guidelines. The United Nations Human Settlements Programme (UN-Habitat, 2003, 2020) defines shelter adequacy through five operational deprivation criteria: (1) durable housing construction, (2) sufficient living area (more than three persons sharing a single habitable room, operationalized as <9.0 m² of floor space per person), (3) access to improved water, (4) access to adequate sanitation, and (5) security of tenure.

Among these criteria, living space sufficiency (<9.0 m² per capita) is directly associated with residential density, domestic ventilation, and respiratory health, yet it is difficult to estimate from 2D overhead satellite imagery alone (Lilford et al., 2019). Two-dimensional rooftop footprints cannot differentiate between single-story structures and multi-story masonry dwellings.

Recent releases of open, large-scale building footprint datasets provide new opportunities to address vertical morphology. Google's Open Buildings v3 dataset (Sirko et al., 2021) applied deep learning models to high-resolution satellite imagery to identify over 1.8 billion building footprints across Africa, Latin America, and South/Southeast Asia, including estimated structural heights derived from shadow and monocular depth cues. Biljecki et al. (2023, 2024) demonstrated that combining 2.5D building height estimates with functional building classifications enables scalable urban morphology modeling across cities in the Global South. By intersecting building volumes with gridded ambient population estimates (such as WorldPop; Tatem, 2017) and functional land-use masks from the European Commission Joint Research Centre (JRC GHS-BUILT-C; Schiavina et al., 2022), it becomes feasible to approximate living floor area per capita across regional extents.

## 2.3 Pedestrian Accessibility, the 15-Minute City, and Open Spatial Data Systems

Physical living standards are also shaped by spatial accessibility to basic public infrastructure, including primary healthcare facilities, schools, daily retail, and open green space (Geurs & van Wee, 2004; Handy & Niemeier, 1997). The "15-minute city" concept (Moreno et al., 2021) has gained traction as a planning framework, emphasizing that daily residential, educational, nutritional, and recreational needs should be reachable within a 15-minute walk or cycling trip.

In accessibility modeling, two primary methodologies are commonly applied: gravity-based models and cumulative opportunity thresholds (Handy & Niemeier, 1997; Hosford et al., 2022). Gravity models apply continuous distance-decay functions to represent diminishing interaction probability. Conversely, cumulative opportunity thresholds—measuring the number of destinations reachable within a fixed travel-time isochrone (e.g., 15 minutes of walking at 4.0 km/h, corresponding to ~1,000 meters along a street network)—offer practical advantages for planning: they are interpretable for non-specialist decision makers and directly linked to human walking thresholds (Hosford et al., 2022; Weiss et al., 2018).

In fragmented metropolitan regions, calculating accessibility via Euclidean ("crow-flies") buffer distances can substantially overestimate access (Boeing, 2017). Rapid suburbanization in developing cities has produced enclosed master-planned developments bordered by perimeter walls, located adjacent to unplanned informal settlements (Dovey et al., 2021; Firman, 2004). A public clinic or park may be physically close in Euclidean space, yet require a multi-kilometer detour around perimeter barriers and major transport corridors. Topological network routing over walkable street graphs is therefore necessary to reflect physical connectivity and barrier severance.

While OpenStreetMap (OSM) has enabled open network analysis (Boeing, 2017), volunteer-contributed data can exhibit geographic and thematic unevenness in developing countries (Barrington-Leigh & Millard-Ball, 2017). Commercial centers and higher-income districts are frequently mapped in greater detail than peri-urban fringes and informal settlements, which can omit basic amenities or leave building categories unassigned.

To improve the consistency of open geospatial datasets, the Overture Maps Foundation was established by the Linux Foundation in partnership with major technology providers (Overture Maps Foundation, 2023, 2024). Overture integrates open spatial sources into a standardized taxonomy under the Global Entity Reference System (GERS). By combining open business registries, algorithmic road extraction, and community-contributed points of interest (POIs) under an open CDLA Permissive 2.0 license, Overture offers a standardized spatial layer for evaluating amenity access across regions where single-source volunteered geographic information is incomplete.

## 2.4 Graph Neural Networks and Spatial Anomaly Detection

Evaluating spatial disparity and segregation across regional extents without relying on subjective ground-truth boundary labeling requires unsupervised structural analysis methods.

Spatial segregation has traditionally been analyzed using global or local spatial autocorrelation statistics, including Moran's I and Anselin's (1995) Local Indicators of Spatial Association (LISA). In segregation literature, spatial dissimilarity metrics (Reardon & O'Sullivan, 2004) assess whether population subgroups are evenly distributed across contiguous spatial units. However, classical spatial statistics operate under linear assumptions and can have difficulty capturing non-linear interactions across high-dimensional physical and environmental indicators (such as concurrent shifts in dwelling volume, tree canopy, bare soil exposure, and pedestrian travel times).

Graph Neural Networks (GNNs), including Graph Convolutional Networks (GCNs; Kipf & Welling, 2016) and Graph Attention Networks (GATs; Veličković et al., 2018), provide frameworks for learning representations on non-Euclidean spatial structures (Zhang et al., 2022). Unlike conventional convolutional models that require regular pixel arrays, GNNs operate directly on topological graphs where spatial units (such as equal-area hexagonal cells) form nodes and spatial adjacency forms edges. GATs extend GCNs by computing attention coefficients $\alpha_{ij}$ between adjacent nodes, allowing the network to weight the relative influence of neighboring units based on feature relationships.

In node classification tasks, deep GNN architectures can encounter the "over-smoothing" effect, in which repeated neighborhood message passing causes representations across adjacent nodes to become increasingly similar (Chen et al., 2020; Kipf & Welling, 2016). In unsupervised spatial anomaly detection, this characteristic can be repurposed. By training a Graph Attention Autoencoder (GAT-AE) with a constrained low-dimensional bottleneck (e.g., latent dimension $d=2$) over a geometric spatial adjacency graph, the network is encouraged to preserve local spatial continuity: it expects adjacent geographic cells to exhibit similar physical living conditions.

When reconstructing the input feature vector, the autoencoder produces low reconstruction errors in areas characterized by spatial continuity. However, where an edge crosses an abrupt physical or socio-spatial boundary—such as a dividing wall between a planned residential development and a dense informal settlement—the message-passing mechanism aggregates disparate feature distributions. Consequently, the autoencoder yields elevated reconstruction errors along the boundary.

This formulation connects to attributed graph anomaly detection, notably the DOMINANT framework (Ding et al., 2019), which optimizes attribute and graph structure reconstruction to identify nodes whose features diverge from their structural neighborhood. Furthermore, because reconstruction error can be calculated per feature dimension, it supports **attributed error decomposition**:
$$\text{Reconstruction Error}_i = \sum_{k=1}^M (x_{ik} - \hat{x}_{ik})^2$$
By isolating the reconstruction error of built-environment and socio-spatial indicators (living space, amenity accessibility, bare soil, and nighttime radiance) from biophysical land-cover transitions (such as agricultural boundaries or water bodies), attributed error decomposition helps distinguish human-made socio-spatial boundaries from natural environmental gradients.

## 2.5 Theoretical Synthesis: The 4-Quadrant Divergence Framework

Building upon the reviewed literature, we formulate the **4-Quadrant Divergence Framework** to describe the relationship between asset-based wealth metrics and in-situ physical living standards.

Conventional economic models often treat durable asset ownership and physical environmental quality as closely correlated. In rapidly growing metropolises across the Global South, however, land tenure arrangements, infrastructure delivery lags, and housing market segmentation can decouple these dimensions. We conceptualize urban space along two axes:
- **Horizontal Axis: Consumer Asset Wealth** (measured via survey asset indices or satellite-predicted proxies such as Meta RWI), reflecting private ownership of consumer electronics, vehicles, and durable household goods.
- **Vertical Axis: In-Situ Physical Living Standard** (measured via our proposed 10-dimensional PLSI), reflecting living floor area, environmental quality, and walkable access to daily public infrastructure.

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

As depicted in the matrix, this framework identifies four distinct conditions:
- **Quadrant I: Integrated Affluent (High Asset, High Physical)**: Master-planned residential communities and formal residential districts characterized by higher household purchasing power, larger living areas per capita, paved road networks, tree canopy cover, and accessible 15-minute pedestrian amenity catchments.
- **Quadrant II: Unserviced Informal Deprivation (Low Asset, Low Physical)**: Unplanned squatter settlements, flood-prone margins, and impoverished peri-urban areas that lack both private household capital and public infrastructure.
- **Quadrant III: Subsidized Formal / Well-Serviced Peripheries (Low Asset, High Physical)**: Subsidized public housing developments or planned relocation areas where household monetary assets remain modest, but planning interventions ensure planned dwelling volumes, paved walkways, drainage, and waste management.
- **Quadrant IV: Asset-Dense, Infrastructure-Deprived Settlements (High Asset, Low Physical)**: Established, dense informal settlements located within central urban corridors. Households in these areas may possess private consumer durables (such as motorcycles and appliances) while facing limited living space (<9.0 m² per person), unpaved alleys, open drainage canals, and elevated exposure to particulate air pollution.

Supervised machine learning models trained on national survey asset scores tend to evaluate Quadrant IV primarily through its durable goods accumulation, which can obscure the need for neighborhood-level environmental and infrastructure improvements. By establishing an unsupervised physical living standard metric and comparing it with asset-based wealth estimates, this research provides a framework for analyzing both dimensions in urban spatial planning.

---

### Section 2 References

Abascal, E., Rothwell, R., Shonowo, A., et al. (2022). "Slum" severity index: A framework to assess spatial inequality in informal settlements. *Habitat International*, 123, 102554. https://doi.org/10.1016/j.habitatint.2022.102554

Anselin, L. (1995). Local indicators of spatial association—LISA. *Geographical Analysis*, 27(2), 93–115. https://doi.org/10.1111/j.1538-4632.1995.tb00338.x

Barrington-Leigh, C., & Millard-Ball, A. (2017). The world's user-generated road map is more than 80% complete. *PLOS ONE*, 12(8), e0180698. https://doi.org/10.1371/journal.pone.0180698

Biljecki, F., Chow, Y. S., & Stouffs, R. (2023). Quality of building height data in OpenStreetMap and its impact on urban analytics. *International Journal of Applied Earth Observation and Geoinformation*, 124, 103525. https://doi.org/10.1016/j.jag.2023.103525

Biljecki, F., Zhao, T., Liang, X., & Hou, Y. (2024). Global building height and volume estimation using open satellite and vector data. *ISPRS Journal of Photogrammetry and Remote Sensing*, 208, 112–132. https://doi.org/10.1016/j.isprsjprs.2024.01.012

Blumenstock, J., Cadamuro, G., & On, R. (2015). Predicting poverty and wealth from mobile phone metadata. *Science*, 350(6264), 1073–1077. https://doi.org/10.1126/science.aac4420

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
