import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

bib_content = r"""@article{Abascal2022,
  author    = {Abascal, Elena and Rothwell, Rachel and Shonowo, Ademola and others},
  title     = {{"Slum"} severity index: A framework to assess spatial inequality in informal settlements},
  journal   = {Habitat International},
  volume    = {123},
  pages     = {102554},
  year      = {2022},
  doi       = {10.1016/j.habitatint.2022.102554}
}

@article{Anselin1995,
  author    = {Anselin, Luc},
  title     = {Local indicators of spatial association---{LISA}},
  journal   = {Geographical Analysis},
  volume    = {27},
  number    = {2},
  pages     = {93--115},
  year      = {1995},
  doi       = {10.1111/j.1538-4632.1995.tb00338.x}
}

@article{BarringtonLeigh2017,
  author    = {Barrington-Leigh, Christopher and Millard-Ball, Adam},
  title     = {The world's user-generated road map is more than 80\% complete},
  journal   = {PLOS ONE},
  volume    = {12},
  number    = {8},
  pages     = {e0180698},
  year      = {2017},
  doi       = {10.1371/journal.pone.0180698}
}

@article{Biljecki2023,
  author    = {Biljecki, Filip and Chow, Yoong Shin and Stouffs, Rudi},
  title     = {Quality of building height data in {OpenStreetMap} and its impact on urban analytics},
  journal   = {International Journal of Applied Earth Observation and Geoinformation},
  volume    = {124},
  pages     = {103525},
  year      = {2023},
  doi       = {10.1016/j.jag.2023.103525}
}

@article{Biljecki2024,
  author    = {Biljecki, Filip and Zhao, Tianhong and Liang, Xiucheng and Hou, Yujun},
  title     = {Global building height and volume estimation using open satellite and vector data},
  journal   = {ISPRS Journal of Photogrammetry and Remote Sensing},
  volume    = {208},
  pages     = {112--132},
  year      = {2024},
  doi       = {10.1016/j.isprsjprs.2024.01.012}
}

@article{Blumenstock2015,
  author    = {Blumenstock, Joshua and Cadamuro, Gabriel and On, Robert},
  title     = {Predicting poverty and wealth from mobile phone metadata},
  journal   = {Science},
  volume    = {350},
  number    = {6264},
  pages     = {1073--1077},
  year      = {2015},
  doi       = {10.1126/science.aac4420}
}

@article{Boeing2017,
  author    = {Boeing, Geoff},
  title     = {{OSMnx}: New methods for acquiring, constructing, analyzing, and visualizing complex street networks},
  journal   = {Computers, Environment and Urban Systems},
  volume    = {65},
  pages     = {126--139},
  year      = {2017},
  doi       = {10.1016/j.compenvurbsys.2017.05.004}
}

@article{Burke2021,
  author    = {Burke, Marshall and Driscoll, Anne and Lobell, David B. and Ermon, Stefano},
  title     = {Using satellite imagery to understand and promote sustainable development},
  journal   = {Science},
  volume    = {371},
  number    = {6535},
  pages     = {eabe8628},
  year      = {2021},
  doi       = {10.1126/science.abe8628}
}

@inproceedings{Chen2020,
  author    = {Chen, Deli and Lin, Yankai and Li, Wei and Li, Peng and Zhou, Jie and Sun, Xu},
  title     = {Measuring and relieving over-smoothing problem for graph neural networks from the topological view},
  booktitle = {Proceedings of the AAAI Conference on Human Computation and Crowdsourcing},
  volume    = {34},
  number    = {04},
  pages     = {3438--3445},
  year      = {2020},
  doi       = {10.1609/aaai.v34i04.5747}
}

@article{Chi2022,
  author    = {Chi, Guanghua and Fang, Han and Chatterjee, Sourav and Blumenstock, Joshua E.},
  title     = {Microestimating poverty with equity},
  journal   = {Proceedings of the National Academy of Sciences},
  volume    = {119},
  number    = {3},
  pages     = {e2113658119},
  year      = {2022},
  doi       = {10.1073/pnas.2113658119}
}

@inproceedings{Ding2019,
  author    = {Ding, Kaize and Li, Jundong and Bhanushali, Rohit and Liu, Huan},
  title     = {Deep anomaly detection on attributed networks},
  booktitle = {Proceedings of the 2019 SIAM International Conference on Data Mining (SDM)},
  pages     = {594--602},
  year      = {2019},
  doi       = {10.1137/1.9781611975673.67}
}

@article{Dovey2020,
  author    = {Dovey, Kim and van Oostrum, Matthijs and Chatterjee, Ihsan and Titus, Tanzil},
  title     = {Towards a morphogenesis of informal settlements},
  journal   = {Habitat International},
  volume    = {108},
  pages     = {102324},
  year      = {2020},
  doi       = {10.1016/j.habitatint.2020.102324}
}

@book{Dovey2021,
  author    = {Dovey, Kim and Pafka, Elek and Ristic, Mirjana},
  title     = {Mapping Urbanities: Morphologies, Flows, Possibilities},
  publisher = {Routledge},
  year      = {2021}
}

@article{Firman2004,
  author    = {Firman, Tommy},
  title     = {New town development in {Jakarta Metropolitan Region}: A perspective of spatial segregation},
  journal   = {Habitat International},
  volume    = {28},
  number    = {3},
  pages     = {349--368},
  year      = {2004},
  doi       = {10.1016/S0197-3975(03)00037-7}
}

@article{Geurs2004,
  author    = {Geurs, Karst T. and van Wee, Bert},
  title     = {Accessibility evaluation of land-use and transport strategies: Review and research directions},
  journal   = {Journal of Transport Geography},
  volume    = {12},
  number    = {2},
  pages     = {127--140},
  year      = {2004},
  doi       = {10.1016/j.jtrangeo.2003.10.005}
}

@article{Handy1997,
  author    = {Handy, Susan L. and Niemeier, Deb A.},
  title     = {Measuring accessibility: An exploration of issues and alternatives},
  journal   = {Environment and Planning A: Economy and Space},
  volume    = {29},
  number    = {7},
  pages     = {1175--1194},
  year      = {1997},
  doi       = {10.1068/a291175}
}

@article{Henderson2012,
  author    = {Henderson, J. Vernon and Storeygard, Adam and Weil, David N.},
  title     = {Measuring economic growth from outer space},
  journal   = {American Economic Review},
  volume    = {102},
  number    = {2},
  pages     = {994--1028},
  year      = {2012},
  doi       = {10.1257/aer.102.2.994}
}

@article{Hosford2022,
  author    = {Hosford, Kate and Beairsto, Jared and Winters, Meghan},
  title     = {Is the 15-minute city within reach? {Evaluating} walking-scale accessibility in {Canadian} cities},
  journal   = {Transport Findings},
  pages     = {32454},
  year      = {2022},
  doi       = {10.32866/001c.32454}
}

@article{Jean2016,
  author    = {Jean, Neal and Burke, Marshall and Xie, Michael and Davis, W. Matthew and Lobell, David B. and Ermon, Stefano},
  title     = {Combining satellite imagery and machine learning to predict poverty},
  journal   = {Science},
  volume    = {353},
  number    = {6301},
  pages     = {790--794},
  year      = {2016},
  doi       = {10.1126/science.aaf7894}
}

@article{Kipf2016,
  author    = {Kipf, Thomas N. and Welling, Max},
  title     = {Semi-supervised classification with graph convolutional networks},
  journal   = {arXiv preprint arXiv:1609.02907},
  year      = {2016},
  url       = {https://arxiv.org/abs/1609.02907}
}

@article{Kohli2012,
  author    = {Kohli, Divyani and Sliuzas, Richard and Kerle, Norman and Stein, Alfred},
  title     = {An ontology of slums for image-based classification},
  journal   = {Computers, Environment and Urban Systems},
  volume    = {36},
  number    = {2},
  pages     = {154--163},
  year      = {2012},
  doi       = {10.1016/j.compenvurbsys.2011.11.001}
}

@article{Kuffer2016,
  author    = {Kuffer, Monika and Pfeffer, Karin and Sliuzas, Richard and Baud, Isa},
  title     = {Slums from space---15 years of slum mapping using remote sensing},
  journal   = {Remote Sensing},
  volume    = {8},
  number    = {6},
  pages     = {455},
  year      = {2016},
  doi       = {10.3390/rs8060455}
}

@article{Kuffer2020,
  author    = {Kuffer, Monika and Thomson, Dana R. and Boo, Gianluca and Mahabir, Ronita and Grippa, Ta{\"i}s and Vanhuysse, Sabine and others},
  title     = {The role of {Earth} observation in an integrated deprivation information system for understanding who lives where in cities},
  journal   = {Computers, Environment and Urban Systems},
  volume    = {80},
  pages     = {101429},
  year      = {2020},
  doi       = {10.1016/j.compenvurbsys.2019.101429}
}

@article{Lilford2019,
  author    = {Lilford, Richard J. and Oyebode, Oyinlola and Satterthwaite, David and Melendez-Torres, G. J. and Chen, Yen-Fu and Mberu, Blessing and others},
  title     = {Improving the health and welfare of people who live in slums},
  journal   = {The Lancet},
  volume    = {389},
  number    = {10068},
  pages     = {559--570},
  year      = {2019},
  doi       = {10.1016/S0140-6736(16)31848-7}
}

@article{Mellander2015,
  author    = {Mellander, Charlotta and Lobo, Jos{\'e} and Stolarick, Kevin and Matheson, Zara},
  title     = {Night-time light data: A good proxy measure for economic activity?},
  journal   = {PLOS ONE},
  volume    = {10},
  number    = {10},
  pages     = {e0139779},
  year      = {2015},
  doi       = {10.1371/journal.pone.0139779}
}

@article{Moreno2021,
  author    = {Moreno, Carlos and Allam, Zaheer and Chabaud, Didier and Gall, Catherine and Pratlong, Florent},
  title     = {Introducing the {"15-Minute City"}: Sustainability, resilience and place identity in future post-pandemic cities},
  journal   = {Smart Cities},
  volume    = {4},
  number    = {1},
  pages     = {93--111},
  year      = {2021},
  doi       = {10.3390/smartcities4010006}
}

@book{Openshaw1984,
  author    = {Openshaw, Stan},
  title     = {The Modifiable Areal Unit Problem},
  publisher = {Geo Books},
  year      = {1984}
}

@misc{Overture2023,
  author    = {{Overture Maps Foundation}},
  title     = {Overture Maps data release and schema documentation},
  publisher = {Linux Foundation},
  year      = {2023},
  url       = {https://overturemaps.org}
}

@misc{Overture2024,
  author    = {{Overture Maps Foundation}},
  title     = {Global Entity Reference System ({GERS}) specification},
  publisher = {Linux Foundation},
  year      = {2024},
  url       = {https://docs.overturemaps.org/gers/}
}

@article{Reardon2004,
  author    = {Reardon, Sean F. and O'Sullivan, David},
  title     = {Measures of spatial segregation},
  journal   = {Sociological Methodology},
  volume    = {34},
  number    = {1},
  pages     = {121--162},
  year      = {2004},
  doi       = {10.1111/j.0081-1750.2004.00150.x}
}

@techreport{Rutstein2004,
  author      = {Rutstein, Shea O. and Johnson, Kiersten},
  title       = {The {DHS} wealth index},
  institution = {ORC Macro},
  type        = {DHS Comparative Reports},
  number      = {6},
  year        = {2004}
}

@techreport{Schiavina2022,
  author      = {Schiavina, Marcello and Melchiorri, Michele and Pesaresi, Martino},
  title       = {{GHSL} Data Package 2022},
  institution = {Publications Office of the European Union},
  year        = {2022},
  doi         = {10.2760/19817}
}

@article{Sirko2021,
  author    = {Sirko, Wojciech and Kashubin, Sergii and Luccioni, Mateus and Diertani, Nicole and Gupta, Manvi and Lee, Christopher and others},
  title     = {Continental-scale building detection from high resolution satellite imagery},
  journal   = {arXiv preprint arXiv:2107.12281},
  year      = {2021},
  url       = {https://arxiv.org/abs/2107.12281}
}

@inproceedings{Sliuzas2010,
  author    = {Sliuzas, Richard and Mboup, Gora and de Sherbinin, Alex},
  title     = {Slum indicators and spatial analysis},
  booktitle = {Proceedings of the 2010 IEEE International Geoscience and Remote Sensing Symposium},
  pages     = {3845--3848},
  year      = {2010},
  doi       = {10.1109/IGARSS.2010.5652579}
}

@article{Tatem2017,
  author    = {Tatem, Andrew J.},
  title     = {{WorldPop}, open data for global good},
  journal   = {Scientific Data},
  volume    = {4},
  number    = {1},
  pages     = {170004},
  year      = {2017},
  doi       = {10.1038/sdata.2017.4}
}

@book{UNHabitat2003,
  author    = {{United Nations Human Settlements Programme}},
  title     = {The Challenge of Slums: Global Report on Human Settlements 2003},
  publisher = {Earthscan Publications},
  year      = {2003}
}

@book{UNHabitat2020,
  author    = {{United Nations Human Settlements Programme}},
  title     = {World Cities Report 2020: The Value of Sustainable Urbanization},
  publisher = {UN-Habitat},
  year      = {2020}
}

@inproceedings{Velickovic2018,
  author    = {Veli{\v{c}}kovi{\'c}, Petar and Cucurull, Guillem and Casanova, Arantxa and Romero, Adriana and Li{\`o}, Pietro and Bengio, Yoshua},
  title     = {Graph attention networks},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2018},
  url       = {https://arxiv.org/abs/1710.10903}
}

@article{Weiss2018,
  author    = {Weiss, Daniel J. and Nelson, Andy and Gibson, H. S. and Temperley, William and Peedell, Stephen and Lieber, Aaron and others},
  title     = {A global map of travel time to cities to assess inequalities in accessibility in 2015},
  journal   = {Nature},
  volume    = {553},
  number    = {7688},
  pages     = {333--336},
  year      = {2018},
  doi       = {10.1038/nature25181}
}

@article{Wurm2019,
  author    = {Wurm, Michael and Stark, Thomas and Zhu, Xiao Xiang and Weigand, Matthias and Taubenb{\"o}ck, Hannes},
  title     = {Semantic segmentation of slums in satellite images using transfer learning on fully convolutional neural networks},
  journal   = {ISPRS Journal of Photogrammetry and Remote Sensing},
  volume    = {150},
  pages     = {59--69},
  year      = {2019},
  doi       = {10.1016/j.isprsjprs.2019.02.006}
}

@article{Yeh2020,
  author    = {Yeh, Christopher and Perez, Anthony and Driscoll, Anne and Azzari, George and Tang, Zhongyi and Lobell, David and Ermon, Stefano and Burke, Marshall},
  title     = {Using publicly available satellite imagery and deep learning to understand economic well-being in {Africa}},
  journal   = {Nature Communications},
  volume    = {11},
  number    = {1},
  pages     = {2583},
  year      = {2020},
  doi       = {10.1038/s41467-020-16185-w}
}

@article{Zhang2022,
  author    = {Zhang, Chen and Jing, Wei and Yao, Yue},
  title     = {A review of deep learning in spatial-temporal data analysis},
  journal   = {ISPRS International Journal of Geo-Information},
  volume    = {11},
  number    = {7},
  pages     = {405},
  year      = {2022},
  doi       = {10.3390/ijgi11070405}
}

@article{Zhao2019,
  author    = {Zhao, Min and Zhou, Yuyu and Li, Xuecao and Zhou, Chenghu and Cheng, Weiming and Li, Manchun and Huang, Kangning},
  title     = {Building a series of consistent night-time light data (1992--2018) in {Southeast Asia} by integrating {DMSP-OLS} and {NPP-VIIRS}},
  journal   = {IEEE Transactions on Geoscience and Remote Sensing},
  volume    = {58},
  number    = {3},
  pages     = {1843--1856},
  year      = {2019},
  doi       = {10.1109/TGRS.2019.2949797}
}
"""

main_tex_content = r"""\documentclass[11pt,a4paper]{article}

% --- Core Packages ---
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{microtype}
\usepackage{hyperref}
\usepackage{natbib}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{xcolor}

% --- Hyperref Setup ---
\hypersetup{
    colorlinks=true,
    linkcolor=blue!70!black,
    citecolor=blue!70!black,
    urlcolor=teal!70!black
}

% --- Document Metadata ---
\title{\textbf{Scalable GeoAI for Measuring Micro-Scale Physical Living Standards and Spatial Disparities: Integrating Open Buildings, Standardized Point-of-Interest Data, and Graph Attention Autoencoders}}

\author{
    \textbf{Dimas RD} \\
    Urban Informatics and Spatial Artificial Intelligence Laboratory \\
    \texttt{Target: ISPRS IJGI / PLOS ONE / EarthArXiv}
}

\date{\today}

\begin{document}

\maketitle

\begin{abstract}
Measuring socio-spatial disparities and physical living conditions in rapidly urbanizing regions of the Global South is constrained by spatial data scarcity, administrative boundary aggregation, and the relative normalization of survey-based wealth models. This study presents an unsupervised GeoAI framework that maps physical living standards and identifies micro-scale spatial discontinuities across the 12,800 km$^2$ Jabodetabek metropolitan region and Karawang Regency, Indonesia. We combine Google Open Buildings v3 (2.5D building heights) intersected with European Commission JRC GHS-BUILT-C residential masks, Overture Maps Foundation points of interest (POIs), Sentinel-2 multi-spectral indices, Landsat land surface temperature, Open-Meteo air quality reanalysis, and NASA VIIRS nighttime radiance onto 17,300 Uber H3 Resolution 8 hexagonal cells ($\sim$0.74 km$^2$). We formulate a 10-dimensional Physical Living Standard Index (PLSI) calibrated against international shelter, environmental health, and pedestrian accessibility guidelines (UN-Habitat 9.0 m$^2$ living area baseline, WHO PM$_{2.5}$ guidelines, and 15-minute walking catchments). To detect spatial boundaries without ground-truth training labels, we deploy a Spatial Graph Attention Autoencoder (GAT-AE) over hexagonal geometric adjacency. Constraining latent dimensionality ($d = 2$) encourages local spatial continuity, causing reconstruction error to increase where abrupt feature differences occur across physical and social boundaries dividing master-planned residential developments from dense informal settlements. Attributed error decomposition distinguishes socio-spatial boundaries from natural land-cover transitions. A four-quadrant comparison against Meta's Relative Wealth Index illustrates that asset-based measures can diverge from in-situ physical living conditions in dense, asset-holding informal neighborhoods. This framework provides urban and regional planners with an auditable, continuous instrument to evaluate physical living conditions without survey lag.
\end{abstract}

\noindent\textbf{Keywords:} GeoAI, spatial segregation, informal settlements, Graph Attention Networks, H3 discrete global grid, Overture Maps, urban living standards, Global South, urban planning.

\vspace{1em}
\hrule
\vspace{1.5em}

% --- Sections ---
\input{sections/01_introduction}
\input{sections/02_literature_review}

% --- Bibliography ---
\newpage
\bibliographystyle{apalike}
\bibliography{references}

\end{document}
"""

sec1_tex_content = r"""\section{Introduction}

Rapid urbanization across the Global South has produced complex spatial configurations, where dense informal settlements (such as Latin American \textit{favelas}, South Asian \textit{bustees}, or Southeast Asian \textit{kampungs}) frequently neighbor master-planned residential developments and commercial centers \citep{Dovey2021, Kuffer2016}. In large metropolitan regions such as Greater Jakarta (Jabodetabek), Indonesia---home to over 35 million residents---these adjacent neighborhoods exhibit measurable differences in dwelling volume, open green space, pedestrian connectivity, and environmental exposure. Tracking these micro-scale variations remains challenging for urban and regional planning authorities who need consistent, fine-grained spatial evidence.

\subsection{The Challenge of Spatial Data Scarcity in Developing Regions}
A central constraint in evaluating micro-scale urban disparities is the scarcity of spatial data in many low- and middle-income regions \citep{Abascal2022}. In contrast to high-income countries where fine-grained municipal property records, tax registries, and high-frequency census blocks are maintained, developing metropolises often depend on official censuses conducted at multi-year intervals and aggregated to coarse administrative boundaries (such as districts or regencies). Administrative aggregation introduces the Modifiable Areal Unit Problem (MAUP; \citealt{Openshaw1984}), obscuring local spatial variations that occur across contiguous streets and residential quarters \citep{Reardon2004}.

Crowdsourced spatial data, most notably OpenStreetMap (OSM), have been widely used to supplement public records. However, in many developing cities, volunteered geographic information exhibits spatial unevenness and attribute gaps \citep{BarringtonLeigh2017}. Commercial corridors and central business districts often have relatively dense contributions, whereas peripheral and informal residential areas frequently contain unclassified building footprints (e.g., tagged simply as \texttt{building=yes}) or incomplete point-of-interest (POI) records for basic services like healthcare and primary education.

\subsection{Characteristics of Supervised Machine Learning Wealth Indices}
Recent advances in Earth observation and machine learning have facilitated large-scale estimation of socioeconomic indicators \citep{Burke2021, Chi2022, Jean2016}. A prominent global resource is Meta's Relative Wealth Index (RWI; \citealt{Chi2022}), which predicts household wealth at a 2.4~km grid resolution across 135 low- and middle-income countries using satellite imagery, mobile network connectivity, and topographic data calibrated against Demographic and Health Surveys (DHS).

While valuable for broad regional screening and humanitarian targeting, supervised wealth models have specific characteristics that warrant attention in urban spatial analysis:
\begin{enumerate}
    \item \textbf{Relative Index Normalization}: RWI models are trained on within-country survey asset scores normalized to standard deviations from the national mean (mean zero, unit variance). Consequently, an RWI score reflects relative economic position within a specific country rather than an absolute measure of physical living conditions. A score of $+1.0$ in a predominantly rural country represents a different built environment than $+1.0$ in an urbanized economy, which limits standardized cross-border comparisons.
    \item \textbf{Divergence Between Household Assets and the Physical Built Environment}: Household surveys typically record ownership of consumer durable assets, such as mobile phones, televisions, refrigerators, and personal vehicles \citep{Rutstein2004}. In dense urban informal settlements, households may possess consumer durables while living in environments with limited living floor area ($<9.0\text{ m}^2$ per person), unpaved lanes, restricted drainage, and elevated particulate air pollution. Models trained on durable asset ownership can classify these areas as relatively well-off, reflecting household consumer goods rather than neighborhood physical living conditions.
    \item \textbf{Data Access and Auditability}: Several high-resolution predictive models incorporate proprietary telecommunications or social platform connectivity data \citep{Blumenstock2015}. For public planning agencies, relying on closed data pipelines can complicate independent audits and long-term methodological replication.
\end{enumerate}

\subsection{Research Objectives and Questions}
To complement existing survey-trained wealth indices, this study develops an unsupervised, cloud-native GeoAI framework that maps absolute physical living standards and identifies micro-scale spatial boundaries using open spatial datasets. We structure the inquiry around three research questions:
\begin{itemize}
    \item \textbf{RQ1}: How can multi-source open remote sensing and open spatial geometries be integrated into an unsupervised, continuous Physical Living Standard Index that is comparable across administrative boundaries?
    \item \textbf{RQ2}: Can an unsupervised Graph Attention Autoencoder (GAT-AE) detect micro-scale spatial disparity and segregation boundaries without ground-truth training labels?
    \item \textbf{RQ3}: How do in-situ physical living standards diverge from satellite-predicted consumer asset wealth (Meta RWI) across dense urban residential morphologies?
\end{itemize}

\subsection{Primary Contributions}
This paper provides four main contributions:
\begin{enumerate}
    \item \textbf{Derivation of the Physical Living Standard Index (PLSI)}: We formulate an interpretable index combining 10 physical dimensions (living floor area, built density, pedestrian amenity access, bare soil, nighttime radiance, vegetative canopy, thermal comfort, water drainage, and air quality). The indicators are anchored to recognized physical baselines, including UN-Habitat living space criteria ($9.0\text{ m}^2$ per person), WHO air quality guidelines, and 15-minute walking catchments.
    \item \textbf{Unsupervised Disparity Detection via Graph Attention Autoencoders}: We deploy a Spatial GAT Autoencoder over a discrete global grid (Uber H3 Resolution 8, $\sim$0.74~km$^2$). By constraining latent dimensionality ($d = 2$) across geometric adjacency, the model establishes local continuity expectations, causing reconstruction error to increase where abrupt feature transitions occur. Attributed error decomposition separates socio-spatial discontinuities from biophysical land-cover edges.
    \item \textbf{Open Data Integration Pipeline}: We demonstrate a reproducible pipeline combining Google Open Buildings v3 (2.5D heights), Overture Maps Foundation standardized point-of-interest data, and open satellite observations (Sentinel-2, Landsat, VIIRS), reducing dependence on proprietary datasets.
    \item \textbf{Planning Relevance and Divergence Analysis}: We apply the Spatial Palma Ratio and a four-quadrant comparison framework (Asset Wealth vs. Physical Infrastructure) to provide urban and regional planners with an auditable tool for identifying infrastructure deficits in dense informal areas.
\end{enumerate}

\subsection{Structure of the Paper}
The remainder of this article is organized as follows: Section 2 reviews relevant literature on remote sensing wealth estimation, 3D building morphology, pedestrian accessibility, and graph neural networks, concluding with the four-quadrant divergence framework. Section 3 outlines the study area and cloud data ingestion workflow. Section 4 presents the 10-dimensional feature engineering methodology and Spatial GAT-AE architecture. Section 5 discusses empirical results and validation benchmarks. Section 6 addresses planning implications and data limitations. Section 7 concludes with considerations for global transferability.
"""

sec2_tex_content = r"""\section{Literature Review and Theoretical Framework}

Measuring socioeconomic conditions and living standards across rapidly expanding metropolitan regions in the developing world presents well-documented methodological challenges. This section reviews four related domains of research: (a) satellite remote sensing and machine learning models for socioeconomic estimation, (b) 3D building morphology and informal settlement characterization, (c) pedestrian accessibility and open spatial data infrastructures, and (d) graph neural networks for spatial anomaly detection. We conclude by synthesizing these insights into a theoretical four-quadrant divergence framework that contrasts asset-based wealth measures with in-situ physical living standards.

\subsection{Remote Sensing and Machine Learning for Socioeconomic Estimation}

Over the past decade, Earth observation and machine learning have expanded the scope of large-scale socioeconomic monitoring \citep{Burke2021, Jean2016}. Studies have demonstrated that nocturnal luminosity recorded by satellite sensors---such as the Defense Meteorological Satellite Program (DMSP) and the Visible Infrared Imaging Radiometer Suite (VIIRS)---correlates with gross regional product, electrification rates, and aggregated economic activity \citep{Henderson2012, Mellander2015}. However, nighttime radiance tends to saturate in dense commercial cores and bloom across unpopulated surfaces, which limits its ability to differentiate micro-scale residential differences \citep{Zhao2019}.

To address the spatial resolution constraints of nighttime lights, transfer learning frameworks were developed to extract visual features from daytime multi-spectral imagery. \citet{Jean2016} demonstrated that convolutional neural networks (CNNs) pretrained on ImageNet and fine-tuned to predict nighttime radiance from high-resolution daytime imagery could identify local economic clusters across five African nations, explaining up to 75\% of the variation in local survey expenditures. Subsequent studies extended this approach using multi-task deep learning architectures and multi-spectral sensors \citep{Burke2021, Yeh2020}, showing that visual features such as roof material, road paving, agricultural field patterns, and building density correlate with household survey outcomes.

A widely used global dataset is Meta's Relative Wealth Index (RWI; \citealt{Chi2022}). By combining high-resolution satellite imagery, topographic models, mobile telecommunication connectivity data, and user network connectivity graphs, \citet{Chi2022} trained gradient-boosted decision trees (XGBoost) against Demographic and Health Surveys (DHS) conducted across 135 low- and middle-income countries. RWI provides gridded wealth estimates at a 2.4~km resolution globally, supporting regional resource allocation and humanitarian assessments.

Alongside their utility, supervised satellite wealth models have specific structural characteristics that are relevant for metropolitan urban planning:
\begin{enumerate}
    \item \textbf{Relative Metric Normalization}: Because DHS surveys are conducted independently across different nations and survey waves, the target variable in supervised models is typically normalized as a within-country asset wealth score (a standardized z-score with mean zero and unit variance). Consequently, an RWI score of $+1.0$ reflects relative economic standing within a specific national distribution rather than an absolute level of material living conditions. An RWI value of $+1.0$ in a predominantly rural country reflects a different physical built environment than $+1.0$ in an urbanized economy, which complicates direct cross-border comparisons.
    \item \textbf{Decoupling of Asset Capital from Built Environmental Conditions}: Household surveys primarily measure ownership of consumer durable goods---such as smartphones, televisions, refrigerators, motorcycles, and cooking stoves \citep{Rutstein2004}. While durable asset ownership differentiates relative poverty in rural settings, it can decouple from physical living conditions in dense urban settlements. In established informal settlements across the Global South, families may accumulate consumer electronics and personal transport while residing in environments characterized by limited floor area ($<9.0\text{ m}^2$ per person), unpaved lanes, open drainage canals, and elevated ambient particulate air pollution. Models trained on durable asset ownership can classify these settlements as moderately affluent, capturing private consumer capital rather than neighborhood physical environmental conditions.
    \item \textbf{Accessibility and Auditability of Data}: Several high-resolution socioeconomic models incorporate proprietary data sources, such as mobile network call detail records (CDRs; \citealt{Blumenstock2015}) or commercial platform graphs. These proprietary sources are rarely accessible to municipal planning agencies, cannot be easily audited by external researchers, and raise data privacy considerations.
\end{enumerate}

\subsection{Built-Environment Morphology, 3D Building Geometry, and Informal Settlement Detection}

To evaluate physical urban living conditions, urban remote sensing has historically focused on mapping informal settlements and slums \citep{Kuffer2016}. Informal settlements represent spatial manifestations of rapid urbanization characterized by distinct morphological patterns: high building coverage, organic street configurations, small dwelling footprints, limited vegetative cover, and heterogeneous roofing materials \citep{Kohli2012, Sliuzas2010}.

Remote sensing approaches frequently framed informal settlement detection as a binary classification problem: labeling spatial units as either ``slum'' or ``formal'' using texture metrics (e.g., Gray-Level Co-occurrence Matrix; GLCM) or object-based image analysis (OBIA) applied to very high-resolution (VHR) aerial or commercial satellite imagery \citep{Kuffer2016, Wurm2019}. While effective for classification benchmarks, binary categorizations present two practical limitations. First, they simplify heterogeneous communities that experience progressive physical consolidation \citep{Dovey2020}. Second, binary labels mask the multidimensional continuum of living conditions: two settlements categorized as informal may have different access levels to piped water, road paving, and structural safety \citep{Abascal2022, Lilford2019}.

To evaluate living conditions continuously, research can draw upon established international shelter guidelines. The United Nations Human Settlements Programme \citep{UNHabitat2003, UNHabitat2020} defines shelter adequacy through five operational deprivation criteria: (1) durable housing construction, (2) sufficient living area (more than three persons sharing a single habitable room, operationalized as $<9.0\text{ m}^2$ of floor space per person), (3) access to improved water, (4) access to adequate sanitation, and (5) security of tenure.

Among these criteria, living space sufficiency ($<9.0\text{ m}^2$ per capita) is directly associated with residential density, domestic ventilation, and respiratory health, yet it is difficult to estimate from 2D overhead satellite imagery alone \citep{Lilford2019}. Two-dimensional rooftop footprints cannot differentiate between single-story structures and multi-story masonry dwellings.

Recent releases of open, large-scale building footprint datasets provide new opportunities to address vertical morphology. Google's Open Buildings v3 dataset \citep{Sirko2021} applied deep learning models to high-resolution satellite imagery to identify over 1.8 billion building footprints across Africa, Latin America, and South/Southeast Asia, including estimated structural heights derived from shadow and monocular depth cues. \citet{Biljecki2023, Biljecki2024} demonstrated that combining 2.5D building height estimates with functional building classifications enables scalable urban morphology modeling across cities in the Global South. By intersecting building volumes with gridded ambient population estimates (such as WorldPop; \citealt{Tatem2017}) and functional land-use masks from the European Commission Joint Research Centre (JRC GHS-BUILT-C; \citealt{Schiavina2022}), it becomes feasible to approximate living floor area per capita across regional extents.

\subsection{Pedestrian Accessibility, the 15-Minute City, and Open Spatial Data Systems}

Physical living standards are also shaped by spatial accessibility to basic public infrastructure, including primary healthcare facilities, schools, daily retail, and open green space \citep{Geurs2004, Handy1997}. The ``15-minute city'' concept \citep{Moreno2021} has gained traction as a planning framework, emphasizing that daily residential, educational, nutritional, and recreational needs should be reachable within a 15-minute walk or cycling trip.

In accessibility modeling, two primary methodologies are commonly applied: gravity-based models and cumulative opportunity thresholds \citep{Handy1997, Hosford2022}. Gravity models apply continuous distance-decay functions to represent diminishing interaction probability. Conversely, cumulative opportunity thresholds---measuring the number of destinations reachable within a fixed travel-time isochrone (e.g., 15 minutes of walking at 4.0~km/h, corresponding to $\sim$1,000 meters along a street network)---offer practical advantages for planning: they are interpretable for non-specialist decision makers and directly linked to human walking thresholds \citep{Hosford2022, Weiss2018}.

In fragmented metropolitan regions, calculating accessibility via Euclidean (``crow-flies'') buffer distances can substantially overestimate access \citep{Boeing2017}. Rapid suburbanization in developing cities has produced enclosed master-planned developments bordered by perimeter walls, located adjacent to unplanned informal settlements \citep{Dovey2021, Firman2004}. A public clinic or park may be physically close in Euclidean space, yet require a multi-kilometer detour around perimeter barriers and major transport corridors. Topological network routing over walkable street graphs is therefore necessary to reflect physical connectivity and barrier severance.

While OpenStreetMap (OSM) has enabled open network analysis \citep{Boeing2017}, volunteer-contributed data can exhibit geographic and thematic unevenness in developing countries \citep{BarringtonLeigh2017}. Commercial centers and higher-income districts are frequently mapped in greater detail than peri-urban fringes and informal settlements, which can omit basic amenities or leave building categories unassigned.

To improve the consistency of open geospatial datasets, the Overture Maps Foundation was established by the Linux Foundation in partnership with major technology providers \citep{Overture2023, Overture2024}. Overture integrates open spatial sources into a standardized taxonomy under the Global Entity Reference System (GERS). By combining open business registries, algorithmic road extraction, and community-contributed points of interest (POIs) under an open CDLA Permissive 2.0 license, Overture offers a standardized spatial layer for evaluating amenity access across regions where single-source volunteered geographic information is incomplete.

\subsection{Graph Neural Networks and Spatial Anomaly Detection}

Evaluating spatial disparity and segregation across regional extents without relying on subjective ground-truth boundary labeling requires unsupervised structural analysis methods.

Spatial segregation has traditionally been analyzed using global or local spatial autocorrelation statistics, including Moran's $I$ and Anselin's \citeyearpar{Anselin1995} Local Indicators of Spatial Association (LISA). In segregation literature, spatial dissimilarity metrics \citep{Reardon2004} assess whether population subgroups are evenly distributed across contiguous spatial units. However, classical spatial statistics operate under linear assumptions and can have difficulty capturing non-linear interactions across high-dimensional physical and environmental indicators (such as concurrent shifts in dwelling volume, tree canopy, bare soil exposure, and pedestrian travel times).

Graph Neural Networks (GNNs), including Graph Convolutional Networks (GCNs; \citealt{Kipf2016}) and Graph Attention Networks (GATs; \citealt{Velickovic2018}), provide frameworks for learning representations on non-Euclidean spatial structures \citep{Zhang2022}. Unlike conventional convolutional models that require regular pixel arrays, GNNs operate directly on topological graphs where spatial units (such as equal-area hexagonal cells) form nodes and spatial adjacency forms edges. GATs extend GCNs by computing attention coefficients $\alpha_{ij}$ between adjacent nodes, allowing the network to weight the relative influence of neighboring units based on feature relationships.

In node classification tasks, deep GNN architectures can encounter the ``over-smoothing'' effect, in which repeated neighborhood message passing causes representations across adjacent nodes to become increasingly similar \citep{Chen2020, Kipf2016}. In unsupervised spatial anomaly detection, this characteristic can be repurposed. By training a Graph Attention Autoencoder (GAT-AE) with a constrained low-dimensional bottleneck (e.g., latent dimension $d=2$) over a geometric spatial adjacency graph, the network is encouraged to preserve local spatial continuity: it expects adjacent geographic cells to exhibit similar physical living conditions.

When reconstructing the input feature vector, the autoencoder produces low reconstruction errors in areas characterized by spatial continuity. However, where an edge crosses an abrupt physical or socio-spatial boundary---such as a dividing wall between a planned residential development and a dense informal settlement---the message-passing mechanism aggregates disparate feature distributions. Consequently, the autoencoder yields elevated reconstruction errors along the boundary.

This formulation connects to attributed graph anomaly detection, notably the DOMINANT framework \citep{Ding2019}, which optimizes attribute and graph structure reconstruction to identify nodes whose features diverge from their structural neighborhood. Furthermore, because reconstruction error can be calculated per feature dimension, it supports \textbf{attributed error decomposition}:
\begin{equation}
\text{Reconstruction Error}_i = \sum_{k=1}^M (x_{ik} - \hat{x}_{ik})^2
\end{equation}
By isolating the reconstruction error of built-environment and socio-spatial indicators (living space, amenity accessibility, bare soil, and nighttime radiance) from biophysical land-cover transitions (such as agricultural boundaries or water bodies), attributed error decomposition helps distinguish human-made socio-spatial boundaries from natural environmental gradients.

\subsection{Theoretical Synthesis: The 4-Quadrant Divergence Framework}

Building upon the reviewed literature, we formulate the \textbf{4-Quadrant Divergence Framework} to describe the relationship between asset-based wealth metrics and in-situ physical living standards.

Conventional economic models often treat durable asset ownership and physical environmental quality as closely correlated. In rapidly growing metropolises across the Global South, however, land tenure arrangements, infrastructure delivery lags, and housing market segmentation can decouple these dimensions. We conceptualize urban space along two axes:
\begin{itemize}
    \item \textbf{Horizontal Axis: Consumer Asset Wealth} (measured via survey asset indices or satellite-predicted proxies such as Meta RWI), reflecting private ownership of consumer electronics, vehicles, and durable household goods.
    \item \textbf{Vertical Axis: In-Situ Physical Living Standard} (measured via our proposed 10-dimensional PLSI), reflecting living floor area, environmental quality, and walkable access to daily public infrastructure.
\end{itemize}

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

As depicted in Figure~\ref{fig:four_quadrant_framework}, this framework identifies four distinct conditions:
\begin{itemize}
    \item \textbf{Quadrant I: Integrated Affluent (High Asset, High Physical)}: Master-planned residential communities and formal residential districts characterized by higher household purchasing power, larger living areas per capita, paved road networks, tree canopy cover, and accessible 15-minute pedestrian amenity catchments.
    \item \textbf{Quadrant II: Unserviced Informal Deprivation (Low Asset, Low Physical)}: Unplanned squatter settlements, flood-prone margins, and impoverished peri-urban areas that lack both private household capital and public infrastructure.
    \item \textbf{Quadrant III: Subsidized Formal / Well-Serviced Peripheries (Low Asset, High Physical)}: Subsidized public housing developments or planned relocation areas where household monetary assets remain modest, but planning interventions ensure planned dwelling volumes, paved walkways, drainage, and waste management.
    \item \textbf{Quadrant IV: Asset-Dense, Infrastructure-Deprived Settlements (High Asset, Low Physical)}: Established, dense informal settlements located within central urban corridors. Households in these areas may possess private consumer durables (such as motorcycles and appliances) while facing limited living space ($<9.0\text{ m}^2$ per person), unpaved alleys, open drainage canals, and elevated exposure to particulate air pollution.
\end{itemize}

Supervised machine learning models trained on national survey asset scores tend to evaluate Quadrant IV primarily through its durable goods accumulation, which can obscure the need for neighborhood-level environmental and infrastructure improvements. By establishing an unsupervised physical living standard metric and comparing it with asset-based wealth estimates, this research provides a framework for analyzing both dimensions in urban spatial planning.
"""

# Targets
target_dirs = [
    'c:/Users/Dimas RD/Documents/projects/phys_living_index/latex',
    'c:/Users/Dimas RD/Documents/projects/wip/latex'
]

for td in target_dirs:
    os.makedirs(os.path.join(td, 'sections'), exist_ok=True)
    os.makedirs(os.path.join(td, 'figures'), exist_ok=True)
    os.makedirs(os.path.join(td, 'tables'), exist_ok=True)
    
    # Write references.bib
    with open(os.path.join(td, 'references.bib'), 'w', encoding='utf-8') as f:
        f.write(bib_content.strip() + '\n')
        
    # Write main.tex
    with open(os.path.join(td, 'main.tex'), 'w', encoding='utf-8') as f:
        f.write(main_tex_content.strip() + '\n')
        
    # Write sections
    with open(os.path.join(td, 'sections', '01_introduction.tex'), 'w', encoding='utf-8') as f:
        f.write(sec1_tex_content.strip() + '\n')
        
    with open(os.path.join(td, 'sections', '02_literature_review.tex'), 'w', encoding='utf-8') as f:
        f.write(sec2_tex_content.strip() + '\n')
        
    print(f"LaTeX environment successfully populated in: {td}")
