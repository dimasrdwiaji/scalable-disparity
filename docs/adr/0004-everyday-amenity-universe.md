# ADR 0004: Everyday Amenity Universe for 15-Minute Walk Accessibility

* **Status**: Accepted
* **Date**: 2026-11-02
* **Deciders**: Dimas RD
* **Departs from**: Stage 3 spec (formal amenities only: schools, clinics, hospitals, supermarkets, parks)

The 15-minute walk channel counts **everyday destinations**: daily retail and markets (warung, kiosks, convenience stores, pasar), food stalls and restaurants, pharmacies, clinics and hospitals, banks/ATMs, post and government offices, schools, places of worship, and parks/sports grounds. It does not count formal public services alone. In kampung-dominated cities most daily needs are met by small informal outlets, and a formal-only list scored most of Jabodetabek as having no access. The category list is a **per-region measurement setting** (`accessibility.amenity_categories`, Overture taxonomy) so other regions can map their own local vocabulary. The channel is scaled with `log1p`, so the jump from 0 to 5 destinations weighs more than 200 to 400 (diminishing returns). Reachable **category diversity** is kept as an auxiliary column for the report.

## Consequences

- The channel measures dense everyday opportunity, which correlates with night-time radiance and built-up density more than a formal-services count would. The Stage 3 report shows this correlation.
- Rural scores depend on Overture and OSM completeness. Cells more than 500 m from the walk network are flagged rather than silently scored 0.
