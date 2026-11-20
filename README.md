
# Warehouse Intelligence
### Digital Twin & Warehouse Operations Analytics

<p align="center">
  <strong>See every zone. Understand every movement. Control every operation.</strong>
</p>

---
https://warehouse-intelligence-digital-twin-4fkxsabngic8dnlnmcikkp.streamlit.app/

## Overview

Warehouse Intelligence is an interactive warehouse operations and inventory analytics application built to help warehouse managers monitor inventory, analyze storage capacity, identify operational risks, and explore warehouse layouts through interactive 2D and 3D visualizations.

The application combines data analytics, inventory intelligence, warehouse visualization, and operational monitoring in one platform.

It supports both sample datasets and user-uploaded CSV files, allowing users to explore warehouse performance through an interactive dashboard.

## Key Features

### 1. Executive Command Center
- Total inventory units and inventory value
- Active SKU monitoring
- Warehouse capacity utilization
- Low-stock and out-of-stock monitoring
- Inventory value analysis
- Warehouse performance overview

### 2. Inventory Intelligence
- ABC inventory classification
- Inventory ageing analysis
- Slow-moving and non-moving stock identification
- Reorder-level monitoring
- Safety-stock analysis
- SKU-level inventory valuation
- Category-wise inventory analysis

### 3. Interactive 2D Warehouse Floor Plan
- Warehouse zone visualization
- Rack-level selection
- Storage occupancy indicators
- Rack-level inventory details
- Search and location highlighting

### 4. 3D Warehouse Digital Twin
- Interactive 3D warehouse environment
- Camera rotation, zoom and navigation
- Rack selection and highlighting
- Warehouse structure visualization
- Rack-level information panel
- Synchronized 2D and 3D selection

### 5. Rack & Bin Explorer
- Warehouse-to-rack hierarchy
- Rack capacity and occupancy
- SKU-level storage information
- Inventory value by location
- Stock status and ageing details

### 6. Inbound & Outbound Operations
- Inbound receipt monitoring
- Expected vs. received units
- Outbound order analysis
- Dispatch performance
- Fulfilment metrics

### 7. Risk & Exception Management
- Low-stock alerts
- Out-of-stock identification
- Slow-moving inventory alerts
- Storage capacity warnings
- Operational exception monitoring

### 8. Space Optimization
- Warehouse capacity analysis
- Zone-wise utilization
- Rack occupancy comparison
- Available storage capacity
- Underutilized and overcrowded locations

### 9. Workforce & Equipment
- Equipment activity visualization
- Forklift movement scenarios
- Operational simulation
- Equipment activity monitoring

### 10. Insights & Recommendations
- Rule-based warehouse insights
- Inventory health recommendations
- Stock and capacity risk identification
- Data-driven operational suggestions

### 11. Data Explorer
- CSV upload and column mapping
- Data quality checks
- Missing-value analysis
- Duplicate record identification
- Downloadable reports

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Web application |
| Pandas | Data processing and analysis |
| NumPy | Numerical calculations |
| Plotly | Interactive analytics and charts |
| HTML5 | Interface structure |
| CSS3 | UI styling |
| JavaScript | Frontend interactions |
| Three.js | 3D warehouse visualization |
| SQL | Database design |
| Power BI | Business intelligence integration |
| DAX | Analytical measures |
| Pytest | Application testing |

---

## Project Architecture

```text
Data Sources
    |
    ├── Sample Warehouse Dataset
    |
    └── Uploaded CSV Files
            |
            v
    Data Processing Layer
       Python / Pandas
            |
            v
      Analytics Engine
       KPI Calculations
       Inventory Analysis
       Risk Detection
            |
            v
     Warehouse Intelligence
            |
     ├── Executive Dashboard
     ├── Inventory Intelligence
     ├── 2D Floor Plan
     ├── 3D Digital Twin
     ├── Operations Analytics
     ├── Risk Management
     └── Insights & Reports
```

---

## Repository Structure

```text
warehouse-intelligence-digital-twin/
│
├── app.py
├── digital_twin.py
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── run_windows.bat
├── .gitignore
├── .env.example
│
├── .streamlit/
│   └── config.toml
│
├── data/
│   └── sample_inventory.csv
│
├── static/
│   ├── digital_twin.html
│   ├── digital_twin.css
│   ├── floorplan.js
│   └── three_scene.js
│
├── database/
│   └── schema.sql
│
├── docs/
│   ├── screenshots/
│   ├── ARCHITECTURE.md
│   ├── DATA_DICTIONARY.md
│   ├── KPI_DEFINITIONS.md
│   └── USER_GUIDE.md
│
├── powerbi/
│   ├── measures.dax
│   ├── data-model.md
│   └── power-query-notes.md
│
└── tests/
```

---

## Installation & Setup

### Prerequisites

- Python 3.10 or later
- Git
- Visual Studio Code (recommended)
- Internet connection for installing dependencies and loading the 3D visualization

### 1. Clone the Repository

```bash
git clone https://github.com/shubh200405-coder/warehouse-intelligence-digital-twin.git
```

### 2. Navigate to the Project

```bash
cd warehouse-intelligence-digital-twin
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python -m streamlit run app.py
```

### 7. Open in Browser

```text
http://localhost:8501
```

---

## Working with CSV Data

The application supports CSV-based inventory analysis.

The inventory dataset can include fields such as:

| Column | Description |
|---|---|
| warehouse | Warehouse identifier |
| sku | Product identifier |
| quantity | Available stock quantity |
| category | Product category |
| unit_cost | Cost per unit |
| zone | Warehouse storage zone |
| rack | Rack identifier |
| reorder_level | Stock reorder threshold |
| safety_stock | Minimum safety stock |
| last_movement_date | Last inventory movement date |
| capacity_units | Rack storage capacity |

Users can upload their own inventory CSV and map the uploaded columns to the application's standard fields.

The availability of individual analytics depends on the columns provided.

---

## Key KPI Definitions

| KPI | Calculation |
|---|---|
| Inventory Value | Quantity × Unit Cost |
| Total Inventory Units | Sum of Quantity on Hand |
| Capacity Utilization | Occupied Units / Total Capacity × 100 |
| Low Stock SKUs | Distinct SKUs at or below reorder level |
| Out-of-Stock SKUs | Distinct SKUs with zero or negative stock |
| Inventory Ageing | Days Since Last Movement |
| Dead Stock Value | Value of inventory with no movement beyond the configured threshold |
| Receiving Completion | Received Units / Expected Units × 100 |
| Fulfilment Rate | Dispatched Units / Ordered Units × 100 |

All calculations depend on the availability and quality of the underlying data.

---

## Screenshots

Screenshots of the application will be available in:

```text
docs/screenshots/
```

Planned screenshots:

| Screenshot | Description |
|---|---|
| command-center.png | Executive dashboard |
| inventory-intelligence.png | Inventory analytics |
| 2d-floor-plan.png | Interactive warehouse floor plan |
| 3d-digital-twin.png | 3D warehouse visualization |
| risk-center.png | Warehouse alerts |
| data-explorer.png | CSV upload and data analysis |

---

## Data & Integration Notes

- The included sample dataset is synthetic.
- Uploaded CSV files are analyzed according to their available columns.
- Equipment movements are simulated scenarios, not live equipment tracking.
- The 3D warehouse is a visualization model, not a connection to physical warehouse infrastructure.
- Insights are generated through rule-based calculations.
- External AI services and workflow automation require separate configuration.
- PostgreSQL integration is a potential extension and should not be assumed to be active.

---

## Future Enhancements

- PostgreSQL database integration
- FastAPI-based analytics services
- Advanced warehouse location optimization
- Live warehouse data integration
- AI-powered warehouse assistant
- n8n workflow automation
- Advanced inventory forecasting
- Equipment telemetry integration
- Enhanced 3D warehouse models
- Power BI reporting integration

---

## Author

**Shubh Srivastava**

Data Analytics | Python | SQL | Power BI | Business Intelligence

- **GitHub:** [shubh200405-coder](https://github.com/shubh200405-coder)
- **LinkedIn:** [Shubh Srivastava](https://www.linkedin.com/in/shubh-srivastava0520/)
- **Email:** [shubh200405@gmail.com](mailto:shubh200405@gmail.com)

---

## License

This project is intended for educational, portfolio, and demonstration purposes.

---

<p align="center">
  <strong>Warehouse Intelligence</strong><br>
  Turning Warehouse Data into Operational Insights.
</p>
