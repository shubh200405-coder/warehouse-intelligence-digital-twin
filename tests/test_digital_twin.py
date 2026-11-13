from pathlib import Path

import pandas as pd

from digital_twin import build_digital_twin_html, prepare_twin_records


def sample_data():
    racks = pd.DataFrame(
        [
            {
                "rack_id": "WH-A-R001",
                "warehouse_id": "WH-A",
                "zone_id": "BULK",
                "rack_name": "Rack 1",
                "capacity_units": 100,
                "occupied_units": 72,
                "available_units": 28,
                "utilization_pct": 72.0,
                "rack_status": "Healthy",
            },
            {
                "rack_id": "WH-A-R002",
                "warehouse_id": "WH-A",
                "zone_id": "PICK",
                "rack_name": "Rack 2",
                "capacity_units": 100,
                "occupied_units": 96,
                "available_units": 4,
                "utilization_pct": 96.0,
                "rack_status": "Critical",
            },
        ]
    )
    inventory = pd.DataFrame(
        [
            {
                "rack_id": "WH-A-R001",
                "warehouse_id": "WH-A",
                "zone_id": "BULK",
                "sku_id": "SKU-001",
                "product_name": "Demo Box",
                "category": "Demo",
                "quantity_on_hand": 72,
                "unit_cost": 10,
                "inventory_value": 720,
                "days_since_movement": 8,
                "stock_status": "Healthy",
                "last_movement_date": pd.Timestamp("2026-11-04"),
            },
            {
                "rack_id": "WH-A-R002",
                "warehouse_id": "WH-A",
                "zone_id": "PICK",
                "sku_id": "SKU-002",
                "product_name": "Demo Cable",
                "category": "Electronics",
                "quantity_on_hand": 96,
                "unit_cost": 5,
                "inventory_value": 480,
                "days_since_movement": 101,
                "stock_status": "Low Stock",
                "last_movement_date": pd.Timestamp("2026-08-03"),
            },
        ]
    )
    return racks, inventory


def test_twin_records_use_source_values():
    racks, inventory = sample_data()
    records = prepare_twin_records(racks, inventory)

    assert len(records) == 2
    assert records[0]["rack_id"] == "WH-A-R001"
    assert records[0]["inventory_value"] == 720
    assert records[1]["sku_rows"][0]["sku_id"] == "SKU-002"


def test_2d_and_3d_views_share_selection_and_rack_data():
    racks, inventory = sample_data()
    html = build_digital_twin_html(racks, inventory, "Demo Warehouse")

    assert 'id="floorSvg"' in html
    assert "threeMount" in html
    assert "selectRackFrom3D" in html
    assert "focusThreeRack" in html
    assert "Play forklift" in html
    assert "WAREHOUSE MODEL" in html
    assert "WH-A-R001" in html
    assert "2 racks in current filtered scope" in html


def test_floor_plan_mode_disables_the_3d_module():
    racks, inventory = sample_data()
    html = build_digital_twin_html(racks, inventory, "Demo Warehouse", view_mode="2d")

    assert 'id="sceneCard" style="display:none"' in html
    assert '<script type="text/plain">' in html


def test_twin_is_not_built_without_location_data():
    html = build_digital_twin_html(pd.DataFrame(), pd.DataFrame(), "Uploaded data")

    assert "Warehouse layout unavailable" in html
    assert "Add rack ID, zone and capacity columns" in html


def test_app_ui_uses_concise_product_copy():
    app_source = (Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8")
    twin_template = (Path(__file__).resolve().parents[1] / "static" / "digital_twin.html").read_text(encoding="utf-8")

    assert "Portfolio Project" not in app_source
    assert "DATA MODE CLEARLY DISCLOSED" not in app_source
    assert "SIMULATED DIGITAL TWIN —" not in app_source
    assert "NOT LIVE IOT" not in twin_template
    assert "WAREHOUSE MODEL" in twin_template
