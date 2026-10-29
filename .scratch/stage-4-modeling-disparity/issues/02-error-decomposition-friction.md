# 02: Attributed Error Decomposition & Boundary Friction Mapping (REV-5)

**What to build:** Implement DOMINANT-style error decomposition in `SpatialGATAutoencoder` separating total reconstruction friction into `Friction_socio` and `Friction_bio`, and extract edge boundary friction `(1 - alpha_ij)`.

**Status:** done

- [x] DOMINANT additive error decomposition `compute_attributed_friction` separating socio and bio dimensions.
- [x] Edge boundary friction `compute_edge_boundary_friction` extracting `1 - alpha_ij`.
- [x] Unit tested for exact additive recovery and multi-head attention averaging.
