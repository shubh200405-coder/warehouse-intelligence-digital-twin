# Project Audit

**Reviewed:** 13 November 2026

## Starting point

The existing project was a single-file Streamlit application with a seeded warehouse model, inventory CSV upload, Plotly charts, stock and ageing metrics, rack summaries, inbound/outbound analysis, exception rules and local exports.

No warehouse source files, database connection, Power BI report or separate frontend were present in the project directory. A reference PostgreSQL schema and Power BI starter files are included in this package; neither is connected to a live system.

## Current structure

| Path | Purpose |
|---|---|
| `app.py` | Streamlit application, demo data, CSV mapping, filters and analytics |
| `digital_twin.py` | Rack record preparation and HTML assembly |
| `static/` | Digital-twin HTML, CSS, floor-plan JavaScript and Three.js scene |
| `data/sample_inventory.csv` | Test inventory upload |
| `database/schema.sql` | Reference PostgreSQL schema |
| `powerbi/` | Data model, DAX measures and Power Query notes |
| `docs/` | Architecture, data dictionary, KPI definitions and usage notes |
| `tests/` | Automated data-model and digital-twin tests |

## Cleanup and reliability changes

- Removed section-divider and explanatory comments that repeated the code.
- Moved the digital-twin markup, styles and scripts into separate static assets.
- Kept business calculations in Python and presentation logic in the browser component.
- Added source-aware filter reset to prevent old selections from hiding records after a CSV or demo-source change.
- Used a composite warehouse/zone/rack key when building uploaded rack locations.
- Removed unused normalized inventory fields and an unused runtime dependency.
- Added sample-data and filter-state regression tests.
- Kept the original uploaded CSV read-only.

## Current limitations

The digital twin is a procedural visualization, not a surveyed warehouse layout. Three.js is loaded from a browser CDN. Inbound, outbound and movements are available in demo mode but are not inferred from an inventory-only CSV. PostgreSQL, external AI services, scheduled n8n workflows, IoT feeds and equipment control are not connected.
