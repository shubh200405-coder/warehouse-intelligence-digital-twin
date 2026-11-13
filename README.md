# Warehouse Intelligence

**Warehouse operations analytics and digital twin**

Warehouse Intelligence is a local Streamlit application for exploring inventory, warehouse capacity and operational exceptions. It includes a 2D floor plan and a procedural Three.js view that share rack selection and display inventory details from the active dataset.

The app includes a built-in demo dataset and supports uploaded inventory CSV files. The warehouse layout and equipment movement are visual models used to explore the operational data.

## Features

- Executive KPIs, warehouse summaries and Plotly charts.
- Inventory status, ageing and ABC classification.
- CSV upload with automatic column suggestions and manual mapping.
- Interactive 2D floor plan and 3D warehouse scene.
- Rack selection shared between the 2D and 3D views.
- Rack-level capacity, utilization, SKU and inventory-value details.
- Inbound, outbound and exception analysis when the selected source contains those records.
- Simulated equipment activity, local report generation and optional manual webhook testing.
- CSV exports, a sample inventory file, automated tests and Power BI starter assets.

## Requirements

- Windows 10 or 11
- Python 3.10 or later
- Internet access for the first dependency installation and the Three.js browser modules
- A modern browser with WebGL enabled for the 3D scene

The 2D floor plan does not require WebGL. Three.js is loaded from `esm.sh`; the 3D scene requires an internet connection when opened.

## Run on Windows

1. Extract this folder to a location where you have write access.
2. Install Python and enable **Add Python to PATH** in the installer.
3. Double-click `run_windows.bat`.
4. Open `http://localhost:8501` in your browser.

The launcher creates `.venv` when needed, installs the requirements and starts Streamlit through `python -m streamlit`. Keep the terminal open while using the application. Press `Ctrl+C` in that terminal to stop it.

### PowerShell

Run these commands from the project folder:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If `.venv` already exists, skip the first command.

## Load the sample CSV

A test file is included at `data/sample_inventory.csv`.

1. Start the app and select **Upload CSV** in the sidebar.
2. Choose `data/sample_inventory.csv`.
3. Review the suggested mappings. The required fields are warehouse, SKU and quantity.
4. Click **Apply mapping and load data**.
5. Check the Command Center, Inventory Intelligence, Rack & Bin Explorer and Digital Twin pages.

The sample contains 144 inventory rows, three warehouses and 36 rack locations. It includes zero-stock, low-stock and ageing cases for validation. It is a sample dataset for testing the upload and analytics workflow.

## Use your own data

A single inventory CSV must contain at least:

| Field | Required | Example column names |
|---|---|---|
| Warehouse or location | Yes | `warehouse_id`, `warehouse`, `location` |
| SKU or product ID | Yes | `sku_id`, `sku`, `product_id` |
| Quantity on hand | Yes | `quantity_on_hand`, `quantity`, `stock` |
| Unit cost or inventory value | No | `unit_cost`, `inventory_value` |
| Category and product name | No | `category`, `product_name` |
| Rack and zone | No | `rack_id`, `zone_id` |
| Last movement date | No | `last_movement_date` |
| Reorder and safety stock | No | `reorder_level`, `safety_stock` |
| Rack or warehouse capacity | No | `rack_capacity`, `warehouse_capacity` |

Original CSV files are read but not modified. The mapping step creates a normalized in-memory model. If a field is unavailable, the affected KPI or view is shown as unavailable rather than inferred.

When switching between demo data and a newly uploaded CSV, the app clears selections that belonged to the previous source. Use **Reset all filters** to restore the current source's full scope at any time.

## Project structure

```text
warehouse-intelligence/
├── app.py
├── digital_twin.py
├── static/
│   ├── digital_twin.html
│   ├── digital_twin.css
│   ├── floorplan.js
│   └── three_scene.js
├── data/
│   └── sample_inventory.csv
├── database/
│   └── schema.sql
├── docs/
├── powerbi/
├── tests/
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
└── run_windows.bat
```

`app.py` contains the Streamlit pages, demo data, CSV mapping and analytics. `digital_twin.py` prepares rack records and combines the static HTML, CSS and JavaScript assets.

- `docs/GITHUB_PUBLISH_GUIDE.md` — repository setup and Streamlit deployment.

## Tests

Install the development dependencies and run the tests from the project folder:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

The tests cover demo data relationships, uploaded CSV mapping, rack metrics, filter-state reset and digital-twin content generation.

## KPI definitions

- **Inventory value:** quantity on hand × unit cost, or the source-provided inventory value.
- **Capacity utilization:** occupied units ÷ capacity units × 100.
- **Low stock:** distinct SKUs at or below reorder level.
- **Out of stock:** quantity on hand less than or equal to zero.
- **Ageing:** days since the last recorded movement, not assumed purchase age.
- **Non-moving value:** inventory value where no movement is recorded for more than 90 days.
- **Receiving completion:** received units ÷ expected units × 100.
- **Fulfilment:** dispatched units ÷ ordered units × 100.
- **ABC classification:** SKUs sorted by value; A through 80% cumulative value, B through 95%, C for the remainder.

Turnover, DIO, XYZ, picking accuracy and OTIF require additional source fields and are not calculated from an inventory-only CSV.

## Integrations and limitations

- **PostgreSQL:** `database/schema.sql` is a reference schema. The app does not connect to or modify a database.
- **AI:** insights are calculated locally using business rules. No Claude or OpenAI API is called.
- **n8n:** the Automation Center offers an optional manual webhook test. No scheduled workflow is configured.
- **Power BI:** `powerbi/` contains a model outline, starter DAX measures and Power Query notes. No PBIX file is included.
- **Digital twin:** the warehouse structure is procedural and illustrative. It is not a verified CAD drawing, live sensor feed or equipment controller.
- **Operations data:** inbound, outbound and movement analytics are available in demo mode. They are not inferred from an inventory-only upload.

## Documentation

- `docs/PROJECT_AUDIT.md` — repository review and current scope.
- `docs/ARCHITECTURE.md` — application flow and component boundaries.
- `docs/DATA_DICTIONARY.md` — normalized fields.
- `docs/KPI_DEFINITIONS.md` — formulas and data requirements.
- `docs/USER_GUIDE.md` — common workflows.
- `docs/UPGRADE_NOTES.md` — changes in this project version.
- `docs/PROJECT_EXPLANATION_HINGLISH.md` — end-to-end project walkthrough in Hinglish.
- `docs/VIDEO_OVERVIEW_SCRIPT_HINGLISH.md` — a natural script for a short project demo video.

## GitHub summary

Interactive warehouse analytics application with inventory intelligence, rack-level drill-down, synchronized 2D/3D visualization, exception monitoring and simulated equipment activity.

## Deploy on Streamlit Community Cloud

This repository is structured for deployment from its root directory. The Streamlit entry point is `app.py`, and Python dependencies are declared in the root `requirements.txt`.

1. Push this project to a GitHub repository.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
3. Select **Create app** and choose this repository.
4. Set the branch to `main` and the main file path to `app.py`.
5. Choose an available app subdomain and select **Deploy**.

The app needs the files in `static/` and `data/` to remain in the repository. The 3D scene loads its Three.js modules from a browser CDN, so the 3D view requires an internet connection.

Do not commit `.env`, `.streamlit/secrets.toml`, API keys, passwords, customer data, or private warehouse exports. The included `data/sample_inventory.csv` is synthetic test data and is safe to use as the public demo file. Configure any future credentials through the hosting platform's secrets settings.

After deployment, pushing commits to the selected GitHub branch triggers an app update.
