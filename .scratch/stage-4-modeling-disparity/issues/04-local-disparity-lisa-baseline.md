# 04: Local Spatial Disparity & Bivariate LISA Baseline (REV-4)

**What to build:** Implement local moving-window Focal Gini / Spatial Palma metrics and Bivariate Local Moran's I (LISA) in `src/phys_living_index/analysis/disparity_metrics.py`.

**Status:** done

- [x] Local focal moving-window Gini and Palma surfaces within k-ring radius via `compute_focal_disparity_surface`.
- [x] Bivariate Local Moran's I (LISA) spatial outlier baseline computed via `esda`/`libpysal`.
- [x] Unit tested on synthetic spatial grids and step functions.
