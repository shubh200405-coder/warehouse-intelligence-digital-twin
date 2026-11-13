# Upgrade Notes

This package keeps the Streamlit application as the local entry point and separates the digital-twin presentation assets from Python data preparation.

Changes in this version:

- `digital_twin.py` now reads the HTML, CSS and JavaScript from `static/`.
- 2D rack selection and 3D rack selection continue to update one shared detail panel.
- The floor-plan-only view disables the Three.js module.
- Warehouse, zone and rack IDs are used together when identifying uploaded rack locations.
- Filters reset when the active data source changes.
- A sample inventory CSV and upload regression tests are included.
- Python dependencies were reduced to packages used by the local application. Test tooling is listed separately in `requirements-dev.txt`.

No database, hosted AI service, scheduled workflow, live IoT feed or production equipment integration has been added.


## UI polish

- Removed repetitive disclaimer banners, portfolio footer copy and long explanatory labels from the main interface.
- Kept a compact `DEMO DATA` source badge so the selected data source remains clear.
- Renamed the rules-based assistant page to `Insights & Recommendations`.
- Added Hinglish project and video walkthrough guides under `docs/`.
