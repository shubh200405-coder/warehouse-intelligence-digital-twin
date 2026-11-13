# User Guide

## Start the application

Run `run_windows.bat`, or use the PowerShell commands in the main README. Open `http://localhost:8501` and keep the terminal open while working.

## Explore demo data

Start with **Demo dataset** in the sidebar. The demo includes three warehouses and linked inventory, rack, movement, inbound and outbound records. The header shows a Demo Data badge.

## Upload an inventory CSV

1. Select **Upload CSV** in the sidebar.
2. Choose a CSV file.
3. Check the suggested column mappings.
4. Map warehouse, SKU and quantity. Map optional fields when available.
5. Select **Apply mapping and load data**.

The original file is not changed. A single inventory CSV does not provide inbound, outbound or movement history, so those pages show unavailable data rather than generated records.

The included `data/sample_inventory.csv` can be used to test the upload flow.

## Use filters

Warehouse, region, category, SKU and zone filters affect inventory pages and rack details. The date range applies to dated operational records. **Reset all filters** restores the full scope for the current source. When the data source changes, selections from the previous source are cleared.

## Inspect the digital twin

Open **3D Digital Twin** to see the 2D plan and 3D scene together. Select a rack in either view to update the shared detail panel. Search by rack ID or SKU. The heatmap changes between occupancy, inventory value and stock status. Camera controls and forklift movement apply to the illustrative 3D scene only.

Open **2D Floor Plan** to use the 2D view without loading the Three.js module.

## Exports and automation

Use the download controls on the relevant pages to export CSV or JSON reports. The Automation Center generates local report files when a workflow is run. The optional n8n webhook sends a summary only after the user enters a URL and clicks the send button.

## Data quality

The Data Explorer shows source dimensions, missing values, duplicates, invalid quantities and sample rows. Review any data-quality warnings before using the metrics for operational decisions.
