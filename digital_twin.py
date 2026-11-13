from __future__ import annotations

import html
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd

STATIC_DIR = Path(__file__).parent / "static"


def _as_number(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    return number if math.isfinite(number) else None


def _as_text(value: Any, fallback: str = "—") -> str:
    return fallback if value is None or pd.isna(value) else str(value)


def prepare_twin_records(racks: pd.DataFrame, inventory: pd.DataFrame) -> list[dict[str, Any]]:
    if racks is None or racks.empty or inventory is None or inventory.empty:
        return []
    if "rack_id" not in inventory.columns:
        return []

    records = []
    for index, rack in racks.reset_index(drop=True).iterrows():
        rack_id = _as_text(rack.get("rack_id"), "")
        if not rack_id:
            continue

        lines = inventory[inventory["rack_id"].astype(str).eq(rack_id)]
        sku_rows = [
            {
                "sku_id": _as_text(row.get("sku_id")),
                "product_name": _as_text(row.get("product_name")),
                "category": _as_text(row.get("category")),
                "quantity": _as_number(row.get("quantity_on_hand")) or 0,
                "inventory_value": _as_number(row.get("inventory_value")),
                "days_since_movement": _as_number(row.get("days_since_movement")),
                "stock_status": _as_text(row.get("stock_status"), "Not assessed"),
            }
            for row in lines.head(24).to_dict("records")
        ]
        ages = pd.to_numeric(lines.get("days_since_movement", pd.Series(dtype=float)), errors="coerce")
        low_stock = lines.get("stock_status", pd.Series(dtype=str)).isin(
            ["Critical", "Low Stock", "Out of Stock"]
        )

        records.append(
            {
                "rack_id": rack_id,
                "warehouse_id": _as_text(rack.get("warehouse_id")),
                "zone_id": _as_text(rack.get("zone_id")),
                "rack_name": _as_text(rack.get("rack_name"), rack_id),
                "capacity_units": _as_number(rack.get("capacity_units")) or 0,
                "occupied_units": _as_number(rack.get("occupied_units")) or 0,
                "available_units": _as_number(rack.get("available_units")) or 0,
                "utilization_pct": _as_number(rack.get("utilization_pct")) or 0,
                "rack_status": _as_text(rack.get("rack_status"), "Not assessed"),
                "inventory_value": _as_number(
                    lines.get("inventory_value", pd.Series(dtype=float)).sum(min_count=1)
                ),
                "sku_count": int(lines["sku_id"].nunique()) if "sku_id" in lines else 0,
                "oldest_stock_days": _as_number(ages.max()) if not ages.empty else None,
                "low_stock_sku_count": int(low_stock.sum()),
                "sku_rows": sku_rows,
                "layout_index": int(index),
            }
        )

    return records


def build_digital_twin_html(
    racks: pd.DataFrame,
    inventory: pd.DataFrame,
    warehouse_name: str,
    view_mode: str = "both",
) -> str:
    records = prepare_twin_records(racks, inventory)
    if not records:
        return """<div style="font-family:Segoe UI,sans-serif;background:#0a1422;color:#dce8f7;padding:24px;border:1px solid #263b55;border-radius:14px">
        <h3 style="margin-top:0">Warehouse layout unavailable</h3>
        <p>Add rack ID, zone and capacity columns to the inventory file to enable this view.</p>
        <p style="color:#9cb0ca">You can also switch to the built-in demo dataset.</p></div>"""

    rack_data = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
    rack_data = rack_data.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")

    template = (STATIC_DIR / "digital_twin.html").read_text(encoding="utf-8")
    css = (STATIC_DIR / "digital_twin.css").read_text(encoding="utf-8")
    floorplan_script = (STATIC_DIR / "floorplan.js").read_text(encoding="utf-8")
    three_script = (STATIC_DIR / "three_scene.js").read_text(encoding="utf-8")

    is_2d = view_mode == "2d"
    three_script_type = "text/plain" if is_2d else "module"
    scene_style = 'style="display:none"' if is_2d else ""
    view_class = "single-view" if is_2d else ""
    three_script_tag = f'<script type="{three_script_type}">\n{three_script}\n</script>'

    replacements = {
        "__DIGITAL_TWIN_CSS__": css,
        "__WAREHOUSE_NAME__": html.escape(str(warehouse_name)),
        "__RACK_DATA__": rack_data,
        "__FLOORPLAN_SCRIPT__": floorplan_script,
        "__THREE_SCRIPT__": three_script_tag,
        "__VIEW_CLASS__": view_class,
        "__SCENE_STYLE__": scene_style,
        "__RACK_COUNT__": f"{len(records):,}",
    }
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)

    return template
