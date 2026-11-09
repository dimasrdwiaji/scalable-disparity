import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

sec1_tex_content = r"""\section{Introduction}

Rapid urbanization across the Global South has produced fragmented urban landscapes where dense informal settlements (such as Latin American \textit{favelas}, South Asian \textit{bustees}, or Southeast Asian \textit{kampungs}) frequently neighbor master-planned residential enclaves and commercial centers \citep{Dovey2021, Kuffer2016}. In metropolitan regions such as Greater Jakarta (Jabodetabek), Indonesia---inhabited by over 35 million people---adjacent neighborhoods exhibit measurable disparities in residential volume, open green space, pedestrian connectivity, and environmental exposure. Tracking these micro-scale differences remains challenging for planning authorities who require consistent, fine-grained spatial evidence.

\subsection{Spatial Data Scarcity in Developing Regions}
Evaluating micro-scale disparities is constrained by the scarcity of fine-grained spatial data across many low- and middle-income regions \citep{Abascal2022}. Unlike high-income settings with detailed municipal property registries and frequent census updates, developing cities often rely on decennial censuses aggregated to coarse administrative boundaries. This administrative aggregation introduces the Modifiable Areal Unit Problem (MAUP; \citealt{Openshaw1984}), obscuring local variations across contiguous streets \citep{Reardon2004}. While crowdsourced spatial data---primarily OpenStreetMap (OSM)---partially address census gaps, volunteered geographic information displays spatial unevenness and attribute incompleteness in peripheral and informal areas \citep{BarringtonLeigh2017}.

\subsection{Characteristics of Supervised Machine Learning Wealth Indices}
Recent advances in Earth observation and machine learning have enabled large-scale estimation of socioeconomic indicators \citep{Burke2021, Chi2022, Jean2016}. Meta's Relative Wealth Index (RWI; \citealt{Chi2022}) provides a prominent example, predicting wealth at 2.4~km resolution across 135 countries using satellite imagery, mobile connectivity, and demographic surveys. 

While valuable for regional screening, supervised wealth models exhibit two notable characteristics in urban settings:
\begin{enumerate}
    \item \textbf{Relative Metric Normalization}: Because training targets derive from within-country Demographic and Health Surveys (DHS) normalized to national z-scores, RWI reflects relative economic rank within a given country rather than an absolute physical living standard, complicating cross-border comparisons.
    \item \textbf{Decoupling of Asset Ownership and Built Environment}: Survey asset indices measure consumer durable ownership (e.g., phones, appliances, vehicles; \citealt{Rutstein2004}). In dense informal settlements, households may possess consumer electronics while experiencing pronounced floor-space constraints ($<9.0\text{ m}^2$ per person), unpaved alleys, open drainage canals, and elevated ambient air pollution. Asset-based models classify these areas as relatively affluent, capturing private consumer capital rather than neighborhood physical environmental conditions \citep{Blumenstock2015}.
\end{enumerate}

\subsection{Research Objectives and Contributions}
This study introduces an unsupervised GeoAI framework that integrates open remote sensing and spatial geometry to map physical living standards and identify micro-scale spatial boundaries. We address three research questions:
\begin{itemize}
    \item \textbf{RQ1}: How can multi-source open remote sensing and open spatial geometries formulate an unsupervised, continuous Physical Living Standard Index comparable across administrative boundaries?
    \item \textbf{RQ2}: Can an unsupervised Graph Attention Autoencoder (GAT-AE) detect micro-scale spatial disparity and segregation boundaries without ground-truth labels?
    \item \textbf{RQ3}: How do in-situ physical living standards diverge from satellite-predicted consumer asset wealth (Meta RWI) across dense urban residential morphologies?
\end{itemize}

We make four primary contributions:
\begin{enumerate}
    \item \textbf{Formulation of the Physical Living Standard Index (PLSI)}: A continuous metric spanning 10 physical dimensions calibrated against international shelter (UN-Habitat $9.0\text{ m}^2$ baseline), environmental health (WHO air quality), and 15-minute walking catchments.
    \item \textbf{Unsupervised Boundary Detection via Spatial GAT-AE}: Repurposing network over-smoothing through a low-dimensional bottleneck ($d=2$) over hexagonal spatial adjacency (Uber H3 Res 8, $\sim$0.74~km$^2$) to highlight socio-spatial severance, accompanied by attributed error decomposition.
    \item \textbf{Open Spatial Data Integration}: An open pipeline harmonizing Google Open Buildings v3 (2.5D heights), Overture Maps standardized points of interest, and open satellite observations (Sentinel-2, Landsat, VIIRS).
    \item \textbf{Planning Utility}: Application of the Spatial Palma Ratio and a 4-quadrant divergence framework (Asset Wealth vs. Physical Living Standards) to support targeted municipal infrastructure investments.
\end{enumerate}

The remainder of this paper is structured as follows: Section 2 reviews related literature and introduces the theoretical framework. Section 3 outlines the study area and data ingestion pipeline. Section 4 presents the feature engineering and Spatial GAT-AE architecture. Section 5 evaluates empirical results and validation benchmarks. Section 6 discusses planning implications and data limitations. Section 7 concludes with considerations for global transferability.
"""

sec2_tex_content = r"""\section{Literature Review and Theoretical Framework}

Evaluating urban living conditions across expanding metropolitan regions in the developing world draws on four complementary fields: remote sensing of socioeconomic indicators, 3D building morphology, pedestrian accessibility modeling, and graph neural networks for spatial anomaly detection. We synthesize these areas into a four-quadrant divergence framework that contrasts asset-based wealth with in-situ physical living standards.

\subsection{Remote Sensing and Machine Learning for Socioeconomic Estimation}
Satellite Earth observation has long supported socioeconomic monitoring. Nocturnal luminosity (DMSP and VIIRS) serves as an established proxy for regional economic activity and electrification \citep{Henderson2012, Mellander2015}, but encounters saturation in commercial cores and blooming across unpopulated surfaces \citep{Zhao2019}. To improve spatial resolution, transfer learning models use daytime multi-spectral imagery to predict nighttime radiance, learning visual features that correlate with local survey expenditures \citep{Burke2021, Jean2016, Yeh2020}. Meta's Relative Wealth Index (RWI; \citealt{Chi2022}) scaled this approach to 135 countries at 2.4~km resolution by training gradient-boosted trees on satellite, mobility, and connectivity data against Demographic and Health Surveys (DHS). 

However, survey asset targets capture household durable goods ownership \citep{Rutstein2004}. In dense urban settlements, asset accumulation can decouple from physical living conditions: households may own mobile devices and appliances while residing in overcrowded structures with unpaved access and open drainage canals.

\subsection{Built-Environment Morphology and Living Space Sufficiency}
Urban remote sensing has traditionally identified informal settlements through distinct morphological signatures: dense building configurations, organic street layouts, small footprints, and heterogeneous roofing \citep{Kohli2012, Sliuzas2010}. Early studies framed detection as binary ``slum vs. formal'' image classification \citep{Kuffer2016, Kuffer2020, Wurm2019}. While computationally effective, binary classifications obscure progressive consolidation \citep{Dovey2020} and ignore the multidimensional continuum of living conditions \citep{Abascal2022, Lilford2019}.

To measure conditions continuously, UN-Habitat \citep{UNHabitat2003, UNHabitat2020} establishes five shelter deprivation criteria: durable construction, access to improved water, adequate sanitation, tenure security, and sufficient living area ($<9.0\text{ m}^2$ per person). Estimating floor area per capita historically proved difficult from 2D overhead imagery. Recent open planetary-scale building datasets, particularly Google Open Buildings v3 \citep{Sirko2021} with 2.5D heights, now enable volumetric morphology estimation across the Global South \citep{Biljecki2023, Biljecki2024}. Intersecting building volumes with ambient population data (WorldPop; \citealt{Tatem2017}) and functional residential masks (JRC GHS-BUILT-C; \citealt{Schiavina2022}) enables continuous estimation of living floor area per capita across regional extents.

\subsection{Pedestrian Accessibility and Open Spatial Data}
Physical living standards also depend on spatial access to basic public amenities, including healthcare, education, retail, and green space \citep{Geurs2004, Handy1997}. The ``15-minute city'' concept emphasizes reachable daily services within a 15-minute walk \citep{Moreno2021}. Cumulative opportunity thresholds (destinations within a fixed walking catchment at 4.0~km/h) offer intuitive, policy-relevant metrics compared to gravity models \citep{Hosford2022, Weiss2018}.

In fragmented cities, Euclidean buffer distances can substantially overestimate accessibility \citep{Boeing2017}. Rapid suburban expansion frequently situates enclosed master-planned developments beside informal settlements \citep{Dovey2021, Firman2004}. Perimeter walls and highway barriers require multi-kilometer pedestrian detours, making topological network routing essential. While OpenStreetMap enables open routing \citep{Boeing2017}, volunteer contributions remain uneven in peripheral areas \citep{BarringtonLeigh2017}. The Overture Maps Foundation \citep{Overture2023, Overture2024} addresses this gap by combining open registries and algorithmic extraction into a standardized Global Entity Reference System (GERS).

\subsection{Graph Neural Networks and Spatial Anomaly Detection}
Unsupervised disparity detection across continuous space requires structural learning methods beyond linear spatial autocorrelation statistics \citep{Anselin1995, Reardon2004}. Graph Neural Networks (GNNs), such as Graph Convolutional Networks (GCNs; \citealt{Kipf2016}) and Graph Attention Networks (GATs; \citealt{Velickovic2018}), learn representations over non-Euclidean spatial graphs where hexagonal cells form nodes and geometric adjacency forms edges \citep{Zhang2022}.

Deep GNNs often encounter ``over-smoothing,'' where repeated neighborhood message passing homogenizes node embeddings \citep{Chen2020, Kipf2016}. In unsupervised anomaly detection, this characteristic can be repurposed. By training a Graph Attention Autoencoder (GAT-AE) with a narrow bottleneck ($d=2$) over pure geometric adjacency, the model enforces local spatial continuity. Where an edge crosses an abrupt socio-spatial boundary, message passing aggregates conflicting feature distributions, resulting in elevated reconstruction errors at the interface. Drawing on attributed graph anomaly frameworks (DOMINANT; \citealt{Ding2019}), attributed error decomposition separates built-environment indicators from biophysical land-cover edges:
\begin{equation}
\text{Reconstruction Error}_i = \sum_{k=1}^M (x_{ik} - \hat{x}_{ik})^2
\end{equation}

\subsection{Theoretical Synthesis: The 4-Quadrant Divergence Framework}
We synthesize these domains into the \textbf{4-Quadrant Divergence Framework}, conceptualizing urban space along two axes: Consumer Asset Wealth (Meta RWI) and In-Situ Physical Living Standards (PLSI).

\begin{figure}[htbp]
\centering
\begin{verbatim}
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
\end{verbatim}
\caption{The 4-Quadrant Divergence Framework contrasting asset-based wealth with in-situ physical living standards.}
\label{fig:four_quadrant_framework}
\end{figure}

\begin{itemize}
    \item \textbf{Quadrant I (High Asset, High Physical)}: Formal residential communities with large dwelling areas, tree cover, and walkable amenities.
    \item \textbf{Quadrant II (Low Asset, Low Physical)}: Unplanned settlements and impoverished peri-urban areas lacking private assets and public services.
    \item \textbf{Quadrant III (Low Asset, High Physical)}: Subsidized public housing with modest household assets but planned dwelling volumes, drainage, and paved access.
    \item \textbf{Quadrant IV (High Asset, Low Physical)}: Established dense informal settlements where households hold durable goods (appliances, vehicles) but endure floor-space deprivation ($<9.0\text{ m}^2$), open drainage, and elevated particulate air pollution.
\end{itemize}

Supervised models trained on survey asset indices often conflate Quadrant IV with Quadrant I, obscuring local infrastructure deficits. The unsupervised PLSI framework provides an empirical tool to evaluate both dimensions independently.
"""

target_dirs = [
    'c:/Users/Dimas RD/Documents/projects/phys_living_index/latex',
    'c:/Users/Dimas RD/Documents/projects/wip/latex'
]

for td in target_dirs:
    with open(os.path.join(td, 'sections', '01_introduction.tex'), 'w', encoding='utf-8') as f:
        f.write(sec1_tex_content.strip() + '\n')
    with open(os.path.join(td, 'sections', '02_literature_review.tex'), 'w', encoding='utf-8') as f:
        f.write(sec2_tex_content.strip() + '\n')
    print(f"Updated LaTeX sections in: {td}")
