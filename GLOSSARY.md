# Domain Glossary: Physical Living Standard & Spatial Disparity

This glossary defines standard domain terms used across the codebase, configuration files, and documentation. Avoid inventing synonyms for these established terms.

---

### Spatial Grid & Geometry

* **H3 Resolution 8 (Res-8)**: Discrete Global Grid System hexagonal cell with an average area of $\approx 0.737\text{ km}^2$ and an edge length of $\approx 461\text{ m}$. Represents the fundamental spatial unit of analysis.
* **Geometric Centroid**: The exact mathematical center of an H3 hexagonal cell, snapped to the nearest traversable pedestrian road edge for isochrone calculation.
* **Adjacency Graph ($A \in \mathbb{R}^{N \times N}$)**: Binary undirected topological graph where edge $A_{ij} = 1$ if hex cells $i$ and $j$ share a boundary on the H3 grid.

---

### Built Environment & Living Space

* **Living Space Ratio ($R_{\text{space}}$)**: The observed residential floor area per person divided by the UN-Habitat minimum shelter standard ($9.0\text{ m}^2$).
  $$R_{\text{space}} = \frac{\text{Observed Living Floor Area per Capita}}{9.0\text{ m}^2}$$
  Values $< 1.0$ indicate severe overcrowding / shelter deficit; values $\ge 1.0$ indicate space adequacy.
* **Residential Filter**: Spatial intersection mask from the EC JRC GHS-BUILT-C_FUN (Functional classification) used to isolate residential buildings and filter out industrial factories, warehouses, and commercial mega-structures from Google Open Buildings v3.
* **Building Height / Volume**: Estimated by Google Open Buildings 2.5D (height in meters). Floor count is approximated as $\max(1, \lfloor \text{height} / 3.0 \rfloor)$.

---

### Accessibility & Opportunities

* **Cumulative Walking Opportunities ($A_{\text{amenity}}$)**: Total count of essential destinations reachable via pedestrian road network within a 15-minute walk (1,000 meters at 4 km/h).
* **Overture Places**: Deduplicated, standardized POI categories from Overture Maps Foundation (`education.school`, `healthcare.hospital`, `healthcare.clinic`, `commercial.supermarket_grocery`).
* **Overture Base**: Designated open-space land-use polygons (`subtype: park`, `sports_pitch`, `recreation_ground`).
* **Perimeter Wall Severance**: Physical impedance where topological or gated community barriers create high network walking travel distance despite close Euclidean proximity.

---

### Environmental & Physical Context

* **Economic Energy Radiance ($E_{\text{night}}$)**: VIIRS Day/Night Band annual cloud-free nighttime radiance (nW/cm²/sr) normalized by population, reflecting active electrification and local commercial vitality.
* **Vegetative Canopy ($\text{NDVI}$)**: Normalized Difference Vegetation Index derived from Sentinel-2 cloud-free composite ($[-1, 1]$ mapped to $[0, 1]$).
* **Thermal Comfort ($\text{LST}_{\text{inv}}$)**: Inverted Land Surface Temperature (Landsat / Open-Meteo), where higher values indicate cooler microclimates and lower heat stress.
* **Air Purity ($\text{PM25}_{\text{inv}}$)**: Inverted annual $PM_{2.5}$ exposure benchmarked against the WHO guidelines ($15\,\mu\text{g/m}^3$).

---

### Model & Disparity Analytics

* **Physical Living Standard Index (PLSI)**: Multi-dimensional, universally benchmarked index ($0.0$ to $1.0$) synthesizing space sufficiency, cumulative amenities, energy, and environmental health.
* **Spatial GAT Autoencoder (GAT-AE)**: Graph Attention Autoencoder trained on pure geometric H3 adjacency with bottleneck dimension $d=2$.
* **Segregation Friction**: Node-level feature reconstruction error ($\|x_i - \hat{x}_i\|^2$). Because the autoencoder expects spatial continuity, reconstruction error spikes precisely across physical segregation seams (e.g. walls dividing kampungs from gated luxury estates).
* **Edge Friction ($1 - \alpha_{ij}$)**: Inverted learned attention weight from the GAT layer indicating where the model actively suppresses message passing between adjacent cells.
* **Spatial Palma Ratio**: The ratio of the living standard capital held by the richest 10% of the population to that held by the poorest 40%.
* **Neighborhood Archetypes**: Unsupervised clusters discovered via HDBSCAN on the latent representations ($Z$), categorizing settlements into organic typologies (*Dense Core Kampung*, *Disconnected Peri-Urban Sprawl*, *Planned Master Enclave*, *Multi-Deprived Pocket*).
