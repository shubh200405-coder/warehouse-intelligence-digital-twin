import ast
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_DIR / "app.py"


def load_data_functions():
    tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
    function_names = {
        "make_demo_data",
        "_norm_col",
        "_suggest_column",
        "build_uploaded_model",
        "add_inventory_fields",
        "rack_summary",
        "sku_summary",
        "build_alerts",
        "reset_filters_for_source",
    }
    nodes = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in function_names:
            node.decorator_list = []
            nodes.append(node)
        elif isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "FILTER_STATE_KEYS"
            for target in node.targets
        ):
            nodes.append(node)

    namespace = {"np": np, "pd": pd, "re": re, "Any": Any}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(APP_PATH), "exec"), namespace)
    return namespace


def test_demo_model_has_consistent_record_counts_and_keys():
    model = load_data_functions()["make_demo_data"]()

    assert len(model["warehouses"]) == 3
    assert len(model["zones"]) == 15
    assert len(model["racks"]) == 120
    assert len(model["products"]) == 160
    assert len(model["inventory"]) == 600
    assert len(model["movements"]) == 1800
    assert len(model["inbound"]) == 320
    assert len(model["outbound"]) == 450
    assert set(model["inventory"]["rack_id"]).issubset(model["racks"]["rack_id"])
    assert set(model["inventory"]["sku_id"]).issubset(model["products"]["sku_id"])


def test_rack_utilization_and_alerts_use_inventory_data():
    functions = load_data_functions()
    model = functions["make_demo_data"]()
    inventory = functions["add_inventory_fields"](model["inventory"])
    racks = functions["rack_summary"](model, inventory)
    alerts = functions["build_alerts"](inventory, racks, model["inbound"], model["outbound"])

    assert len(racks) == 120
    assert (racks["capacity_units"] > 0).all()
    assert racks["utilization_pct"].ge(0).all()
    assert {"severity", "alert_type", "related_item"}.issubset(alerts.columns)


def test_uploaded_sample_csv_maps_and_builds_rack_metrics():
    functions = load_data_functions()
    raw = pd.read_csv(PROJECT_DIR / "data" / "sample_inventory.csv")
    mapping = {
        "warehouse_id": "warehouse_id",
        "sku_id": "sku_id",
        "quantity_on_hand": "quantity_on_hand",
        "unit_cost": "unit_cost",
        "inventory_value_input": "inventory_value",
        "category": "category",
        "rack_id": "rack_id",
        "zone_id": "zone_id",
        "last_movement_date": "last_movement_date",
        "product_name": "product_name",
        "reorder_level": "reorder_level",
        "safety_stock": "safety_stock",
        "rack_capacity": "rack_capacity",
        "warehouse_capacity": "warehouse_capacity",
    }

    model, quality = functions["build_uploaded_model"](raw, mapping)
    inventory = functions["add_inventory_fields"](model["inventory"])
    racks = functions["rack_summary"](model, inventory)

    assert len(inventory) == 144
    assert inventory["warehouse_id"].nunique() == 3
    assert inventory["sku_id"].nunique() > 1
    assert len(racks) == 36
    assert inventory["inventory_value"].sum() > 0
    assert racks["capacity_units"].notna().all()
    assert quality["invalid_quantity_values"] == 0
    assert model["inbound"].empty and model["outbound"].empty


def test_filters_reset_only_when_the_source_changes():
    reset_filters = load_data_functions()["reset_filters_for_source"]
    state = {
        "flt_wh": ["WH-OLD"],
        "flt_sku": ["SKU-OLD"],
        "main_page": "Inventory Intelligence",
    }

    reset_filters(state, "upload:first.csv")
    assert "flt_wh" not in state
    assert "flt_sku" not in state
    assert state["main_page"] == "Inventory Intelligence"

    state["flt_wh"] = ["WH-A"]
    reset_filters(state, "upload:first.csv")
    assert state["flt_wh"] == ["WH-A"]

    reset_filters(state, "upload:second.csv")
    assert "flt_wh" not in state
