## Project Navigation & Standards

### Tooling & Automated Checks
- **Python Environment**: `uv run <cmd>`
- **Run Tests**: `uv run pytest -v` (live integration tests gated behind `@pytest.mark.integration` and skipped by default)
- **Lint & Types**: `uv run ruff check .` (enforces PEP 585/604 modern typing, isort, and NumPy 2.0+ rules)
- **Spatial / GDAL Safeguard**: `tests/conftest.py` and `src/phys_living_index/data/__init__.py` sanitize `PROJ_LIB` and `PROJ_DATA` to prevent external database collisions (e.g. host PostgreSQL).

### Architectural Boundaries
- **Raw Data Ingestion (`src/phys_living_index/data/`)**: Must preserve authentic physical and remote sensing units (spectral indices in $[-1.0, 1.0]$, temperature in Kelvin, air pollution in $\mu\text{g/m}^3$ and official AQI points). Never normalize or rescale to $[0, 1]$ within ingestion modules.
- **Feature Engineering (`src/phys_living_index/features/`)**: Universal Min-Max scaling to $[0, 1]$, inverted hazard scaling (heat, air pollution), and H3 hex aggregation belong exclusively here.

### Issue Tracker & Domain Docs
- **Issue Tracker**: Issues and specs live as local Markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`.
- **Domain Docs**: `GLOSSARY.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
