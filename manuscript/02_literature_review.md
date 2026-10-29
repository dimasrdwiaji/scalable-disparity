# 2. Literature Review and Theoretical Framework

Measuring socioeconomic conditions and living standards across rapidly expanding metropolitan regions in the developing world has long presented a fundamental methodological challenge. This section reviews four converging domains of research: (a) satellite remote sensing and machine learning models for socioeconomic estimation, (b) 3D building morphology and informal settlement characterization, (c) pedestrian accessibility and open spatial data infrastructures, and (d) graph neural networks for spatial anomaly detection. We conclude by synthesizing these insights into a theoretical four-quadrant divergence framework that contrasts asset-based wealth measures with in-situ physical living standards.

## 2.1 Remote Sensing and Machine Learning for Socioeconomic Estimation

Over the past decade, the integration of satellite Earth observation and machine learning has transformed large-scale socioeconomic monitoring (Burke et al., 2021; Jean et al., 2016). Early pioneering studies established that nocturnal luminosity recorded by satellite sensors—such as the Defense Meteorological Satellite Program (DMSP) and the Visible Infrared Imaging Radiometer Suite (VIIRS)—serves as a robust proxy for gross regional product, electrification, and aggregated economic activity (Henderson et al., 2012; Mellander et al., 2015). However, nighttime radiance encounters severe saturation in dense urban cores and blooms across unpopulated surfaces, rendering it inadequate for resolving micro-scale residential inequalities (Zhao et al., 2019).

To overcome the resolution limits of nighttime lights, transfer learning frameworks were developed to extract visual feature representations from daytime multi-spectral imagery. Jean et al. (2016) demonstrated that convolutional neural networks (CNNs) pretrained on ImageNet and fine-tuned to predict nighttime radiance from high-resolution daytime imagery could effectively identify local economic clusters across five African nations, explaining up to 75% of the variation in local survey expenditures. Subsequent studies extended this paradigm using multi-task deep learning architectures and multi-spectral sensors (Burke et al., 2021; Yeh et al., 2020), demonstrating that features such as roof material, road paving, agricultural field patterns, and building footprints correlate strongly with national household survey outcomes.

A major milestone in global socioeconomic mapping was achieved by Meta’s Relative Wealth Index (RWI; Chi et al., 2022). By ingesting high-resolution satellite imagery, topographic models, mobile telecommunication connectivity data, and Facebook user network connectivity graphs, Chi et al. trained gradient-boosted decision trees (XGBoost) against Demographic and Health Surveys (DHS) conducted across 135 low- and middle-income countries. RWI provides gridded poverty estimates at a micro-resolution of 2.4 km globally, representing an invaluable public asset for humanitarian logistics, disaster response, and broad regional resource targeting.

Despite these advancements, supervised satellite wealth models present three critical structural limitations when applied to metropolitan urban planning:
1. **The Relative Normalization Trap**: Because DHS surveys are conducted independently across different countries and survey waves, the dependent variable in supervised models is typically normalized as a within-country asset wealth score (a standardized z-score with mean zero and unit variance). Consequently, an RWI score of +1.0 reflects relative economic standing within that specific nation's distribution, rather than an absolute level of human welfare. An RWI value of +1.0 in rural East Africa corresponds to a fundamentally different physical built environment than +1.0 in urban Southeast Asia, preventing standardized, cross-border comparative evaluations.
2. **The Asset-vs-Physical Decoupling**: Household surveys primarily measure ownership of consumer durable goods—such as smartphones, televisions, refrigerators, motorcycles, and cooking stoves (Rutstein & Johnson, 2004). While durable asset ownership effectively differentiates absolute poverty in rural agrarian settings, it breaks down in dense urban settlements. In informal urban kampungs across Southeast Asia, low-income families frequently accumulate modern consumer electronics and motorized transport, yet inhabit precarious living spaces characterized by extreme room crowding (<5 m² per person), lack of ventilation, unpaved alleyways, open drainage canals, and hazardous air pollution exposure. Supervised asset models systematically misclassify these physically deprived settlements as moderately affluent because their training targets capture consumer capital rather than the in-situ physical environment.
3. **The Proprietary Data Sovereign Barrier**: Many recent high-accuracy socioeconomic models depend on proprietary, non-reproducible data feeds, such as mobile network call detail records (CDRs; Blumenstock et al., 2015) or closed social media advertising graphs. These data streams are inaccessible to public municipal planning agencies, lack long-term institutional guarantees, raise pressing civil privacy concerns, and cannot be audited independently by external researchers.

## 2.2 Built-Environment Morphology, 3D Building Geometry, and Informal Settlement Detection

To capture the physical reality of urban living conditions, urban remote sensing has historically focused on mapping informal settlements and slums (Kuffer et al., 2016). Slums and informal kampungs represent spatial manifestations of urban poverty characterized by distinct morphological patterns: high building density, organic and irregular street layouts, small dwelling footprints, lack of open green space, and heterogeneous, low-cost roofing materials (Kohli et al., 2012; Sliuzas et al., 2010).

Historically, remote sensing approaches framed slum detection as a binary classification problem: labeling discrete spatial units as either "slum" or "formal" using texture metrics (e.g., Gray-Level Co-occurrence Matrix; GLCM) or object-based image analysis (OBIA) applied to very high-resolution (VHR) aerial or commercial satellite imagery (Kuffer et al., 2016; Wurm et al., 2019). While computationally successful, binary classifications suffer from severe limitations. First, they stigmatize complex, evolving communities that exhibit vibrant informal economies and gradual physical consolidation (Dovey et al., 2020). Second, binary labels conceal the multidimensional continuum of deprivation: two neighborhoods classified as "slums" may experience drastically different living conditions, with one possessing reliable piped water and public transport, while the other faces severe structural collapse hazards and zero sanitation infrastructure (Abascal et al., 2022; Lilford et al., 2019).

To move beyond binary classifications, research must align with internationally recognized shelter standards. The United Nations Human Settlements Programme (UN-Habitat, 2003, 2020) defines an informal or inadequate settlement through five operational deprivation dimensions: (1) lack of durable housing construction, (2) insufficient living area (more than three persons sharing a single habitable room, operationalized as <9.0 m² of floor space per person), (3) lack of access to improved water, (4) lack of access to adequate sanitation, and (5) lack of security of tenure.

Among these dimensions, living space sufficiency (<9.0 m² per capita) represents the most direct determinant of infectious disease transmission, mental well-being, and domestic fire hazards, yet it has remained virtually impossible to measure from traditional 2D overhead satellite imagery (Lilford et al., 2019). Two-dimensional rooftop footprints cannot distinguish between a single-story corrugated tin shack and a three-story multi-family masonry dwelling.

Recent breakthroughs in planetary-scale building footprint extraction have begun to resolve this vertical blind spot. Google's Open Buildings v3 dataset (Sirko et al., 2021) deployed deep learning models over 50 cm satellite imagery to detect over 1.8 billion building footprints across Africa, Latin America, and Southeast Asia, providing individual building boundary polygons alongside estimated structural heights derived from shadow analysis and stereoscopic monocular depth estimation. Biljecki et al. (2023, 2024) demonstrated that combining large-scale 2.5D building height estimates with functional building filters provides unprecedented capabilities for volumetric urban morphology modeling, allowing researchers to estimate usable floor area at scale across cities in the Global South. By intersecting these building volumes with gridded ambient population datasets (such as WorldPop; Tatem, 2017) and functional land-use masks from the European Commission Joint Research Centre (JRC GHS-BUILT-C; Schiavina et al., 2022), it becomes feasible to compute continuous, physical living floor area per capita across entire metropolitan territories.

## 2.3 Pedestrian Accessibility, the 15-Minute City, and Open Spatial Data Systems

Physical living standards are not confined to the private dwelling; they depend fundamentally on the spatial accessibility of essential public amenities, including primary healthcare facilities, public schools, markets, and recreational green spaces (Geurs & van Wee, 2004; Handy & Niemeier, 1997). The "15-minute city" concept (Moreno et al., 2021) has gained widespread prominence as an urban planning paradigm, positing that all urban dwellers should be able to fulfill daily residential, educational, nutritional, and leisure needs within a short 15-minute pedestrian walk or cycling trip from their doorstep.

In urban accessibility modeling, two primary methodologies dominate: gravity-based models and cumulative opportunity thresholds (Handy & Niemeier, 1997; Hosford et al., 2022). Gravity models apply distance-decay functions to represent diminishing interaction probability with increasing distance. However, cumulative opportunity thresholds—counting the total number of essential destinations reachable within a fixed travel-time isochrone (e.g., 15 minutes of pedestrian walking at 4.0 km/h, corresponding to ~1,000 meters along a walkable network)—offer substantial advantages for public policy: they are intuitive, easy to communicate to community stakeholders, and directly tied to human physical walking capabilities (Hosford et al., 2022; Weiss et al., 2018).

Crucially, in the fragmented morphologies of Global South megacities, calculating accessibility via simple Euclidean ("crow-flies") buffer rings yields fundamentally misleading results (Boeing, 2017). Rapid suburbanization in Southeast Asia has produced extensive gated communities (*kota mandiri*) enclosed by towering boundary walls and private security checkpoints, immediately adjacent to un-serviced informal kampungs (Dovey et al., 2021; Firman, 2004). A modern hospital or public park may be located only 300 meters from an informal settlement in Euclidean space, yet require a 3-kilometer detour around perimeter walls and tollway barriers to access. Topological network routing over pedestrian graphs is therefore essential to detect physical severance and micro-segregation.

Historically, academic research on urban pedestrian networks has relied almost exclusively on OpenStreetMap (OSM; Boeing, 2017). While OSM has democratized global mapping, its reliance on volunteer contributions creates severe completeness and socio-demographic biases in developing countries (Barrington-Leigh & Millard-Ball, 2017). Commercial centers and affluent districts are densely mapped, whereas peri-urban settlements and peripheral kampungs frequently lack basic amenity tags or display generic classifications (such as unclassified building polygons).

To address these shortcomings, the Overture Maps Foundation was launched in late 2022 by the Linux Foundation in partnership with Amazon Web Services, Meta, Microsoft, and TomTom (Overture Maps Foundation, 2023, 2024). Overture unifies heterogeneous spatial data sources into a validated, schema-standardized spatial taxonomy based on the Global Entity Reference System (GERS). By merging multi-source business registries, algorithmic road network extraction, and verified points of interest (POIs) under an open CDLA Permissive 2.0 license, Overture provides a robust open infrastructure for mapping essential social infrastructure (healthcare, education, markets, green parks) across regions where single-source VGI remains incomplete.

## 2.4 Graph Neural Networks and Spatial Anomaly Detection

To detect socio-spatial segregation and urban disparity across large metropolitan areas without relying on expensive, subjective ground-truth boundary surveys, spatial data science requires unsupervised structural learning techniques.

Spatial segregation has traditionally been quantified using global or local spatial autocorrelation statistics, most notably Moran's I and Anselin's (1995) Local Indicators of Spatial Association (LISA). In the context of segregation studies, spatial dissimilarity indices (Reardon & O'Sullivan, 2004) evaluate whether different socioeconomic groups are evenly distributed across contiguous spatial units. However, classical spatial statistics operate under linear spatial lag assumptions and struggle to capture high-dimensional non-linear interactions across heterogeneous physical environmental features (e.g., simultaneous discontinuities in building height, tree canopy, street dust, and pedestrian travel time).

In recent years, Graph Neural Networks (GNNs), such as Graph Convolutional Networks (GCNs; Kipf & Welling, 2016) and Graph Attention Networks (GATs; Veličković et al., 2018), have emerged as powerful architectures for learning continuous representations over non-Euclidean spatial networks (Zhang et al., 2022). Unlike standard convolutional networks that require regular 2D pixel grids, GNNs operate directly on topological graphs where spatial entities (such as equal-area hexagonal cells) constitute nodes, and spatial contiguity relations form edges. GATs enhance GCNs by computing dynamic attention coefficients $\alpha_{ij}$ between neighboring nodes, allowing the network to weight the relative influence of adjacent spatial units adaptively based on their feature similarity.

In standard node classification tasks, deep GNNs frequently suffer from the "over-smoothing" problem, where repeated neighborhood message-passing causes the representations of adjacent nodes to converge toward uniform values (Chen et al., 2020; Kipf & Welling, 2016). In the context of unsupervised spatial segregation detection, however, this over-smoothing tendency can be creatively leveraged rather than avoided. By training a Graph Attention Autoencoder (GAT-AE) with a narrow low-dimensional bottleneck (e.g., latent dimension $d=2$) over a pure geometric spatial adjacency graph, the network is constrained to enforce local spatial continuity: it expects adjacent geographic cells to exhibit similar physical living conditions.

When the autoencoder attempts to reconstruct the original high-dimensional feature vector, it succeeds in homogeneous areas (whether uniformly affluent or uniformly deprived), yielding low reconstruction errors. However, when an edge crosses an abrupt socio-spatial boundary—such as a security wall separating a luxury golf estate from a hyper-dense informal kampung—the local message-passing mechanism is forced to average across contradictory feature distributions. As a result, the autoencoder cannot satisfy both nodes simultaneously, causing reconstruction error to spike sharply at the interface.

This phenomenon draws direct inspiration from attributed graph anomaly detection frameworks, particularly DOMINANT (Ding et al., 2019). DOMINANT demonstrates that jointly optimizing feature reconstruction and graph structure reconstruction enables unsupervised detection of anomalous nodes whose attributes conflict sharply with their structural neighborhood. Furthermore, because the reconstruction error in an autoencoder is computed element-wise across each feature dimension, it enables **attributed error decomposition**:
$$\text{Reconstruction Error}_i = \sum_{k=1}^M (x_{ik} - \hat{x}_{ik})^2$$
By isolating the error contributions of built-environment and socioeconomic features (such as living space, amenity accessibility, bare soil, and nighttime radiance) from purely biophysical land-cover transitions (such as agricultural crop cycles or water bodies), attributed decomposition allows researchers to distinguish genuine human socio-spatial severance from natural environmental boundaries.

## 2.5 Theoretical Synthesis: The 4-Quadrant Divergence Framework

Building upon the preceding literature, we formulate the **4-Quadrant Divergence Framework** to conceptualize the structural disconnect between asset-based wealth metrics and in-situ physical living standards.

Traditional economic welfare models assume that household consumption assets and physical environmental quality co-vary linearly. In rapidly growing Global South cities, however, land tenure informalities, infrastructure deficits, and speculative real estate dynamics decouple these two domains. We conceptualize urban space along two orthogonal axes:
- **Horizontal Axis: Consumer Asset Wealth** (measured via survey asset indices or satellite-predicted proxies such as Meta RWI), reflecting private ownership of consumer electronics, vehicles, and durable goods.
- **Vertical Axis: In-Situ Physical Living Standard** (measured via our proposed 10-dimensional PLSI), reflecting spatial shelter adequacy, clean environmental exposure, and walkable public infrastructure access.

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
            (Severe Structural    │  (The Urban Kampung Trap:
             Deprivation / Rural  │   Asset-Dense yet Severely
             Poverty)             │   Physically Deprived)
                                  ▼
                   Low Physical Living Standard (PLSI)
```

As illustrated in the conceptual matrix, this framework identifies four distinct urban conditions:
- **Quadrant I: Integrated Affluent (High Asset, High Physical)**: Master-planned gated estates (*kota mandiri*) and high-end residential towers characterized by high household purchasing power, generous private living space (>30 m² per capita), paved road networks, high tree canopy cover, and comprehensive 15-minute pedestrian amenity catchments.
- **Quadrant II: Severe Structural Deprivation (Low Asset, Low Physical)**: Unconsolidated squatter settlements, flood-prone riverbanks, and impoverished rural-urban transition zones that lack both private economic capital and basic municipal infrastructure.
- **Quadrant III: Subsidized Formal / Well-Serviced Peripheries (Low Asset, High Physical)**: Public social housing developments (*rusunawa*) or planned relocation sites where household monetary assets remain modest, but public planning interventions ensure adequate per-capita living volumes, paved pedestrian paths, stormwater drainage, and municipal waste collection.
- **Quadrant IV: The Urban Kampung Trap (High Asset, Low Physical)**: Established, hyper-dense informal settlements located within central metropolitan areas. Here, multi-generational families possess significant personal disposable income—owning multiple motorcycles, air conditioners, and smartphones—yet endure extreme spatial crowding (<5 m² per capita), acute open sewage exposure, unpaved alleyways, and hazardous levels of fine particulate matter ($\text{PM}_{2.5}$).

Supervised machine learning models trained on national survey asset scores systematically conflate Quadrant IV with Quadrant I, treating high-density urban kampungs as moderately wealthy areas while obscuring their urgent need for environmental and structural infrastructure upgrades. By establishing an unsupervised, physical living standard metric and contrasting it directly against asset-based wealth estimates, this research resolves this critical blind spot in urban planning and spatial inequality research.

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

United Nations Human Settlements Programme (UN-Habitat). (2003). *The challenge of slums: Global report on human settlements 2003*. Earthscan Publications.

United Nations Human Settlements Programme (UN-Habitat). (2020). *World cities report 2020: The value of sustainable urbanization*. UN-Habitat.

Veličković, P., Cucurull, G., Casanova, A., Romero, A., Liò, P., & Bengio, Y. (2018). Graph attention networks. *International Conference on Learning Representations (ICLR)*. https://arxiv.org/abs/1710.10903

Weiss, D. J., Nelson, A., Gibson, H. S., Temperley, W., Peedell, S., Lieber, A., ... & Gething, P. W. (2018). A global map of travel time to cities to assess inequalities in accessibility in 2015. *Nature*, 553(7688), 333–336. https://doi.org/10.1038/nature25181

Wurm, M., Stark, T., Zhu, X. X., Weigand, M., & Taubenböck, H. (2019). Semantic segmentation of slums in satellite images using transfer learning on fully convolutional neural networks. *ISPRS Journal of Photogrammetry and Remote Sensing*, 150, 59–69. https://doi.org/10.1016/j.isprsjprs.2019.02.006

Yeh, C., Perez, A., Driscoll, A., Azzari, G., Tang, Z., Lobell, D., Ermon, S., & Burke, M. (2020). Using publicly available satellite imagery and deep learning to understand economic well-being in Africa. *Nature Communications*, 11(1), 2583. https://doi.org/10.1038/s41467-020-16185-w

Zhang, C., Jing, W., & Yao, Y. (2022). A review of deep learning in spatial-temporal data analysis. *ISPRS International Journal of Geo-Information*, 11(7), 405. https://doi.org/10.3390/ijgi11070405

Zhao, M., Zhou, Y., Li, X., Zhou, C., Cheng, W., Li, M., & Huang, K. (2019). Building a series of consistent night-time light data (1992–2018) in Southeast Asia by integrating DMSP-OLS and NPP-VIIRS. *IEEE Transactions on Geoscience and Remote Sensing*, 58(3), 1843–1856. https://doi.org/10.1109/TGRS.2019.2949797
