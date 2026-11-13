from __future__ import annotations

import hashlib
import io
import json
import re
import urllib.request
from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from digital_twin import build_digital_twin_html

st.set_page_config(
    page_title="Warehouse Intelligence | Control Tower",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

PALETTE = {
    "bg": "#08111f",
    "panel": "#111d2e",
    "panel_2": "#15243a",
    "line": "#263750",
    "text": "#eef4ff",
    "muted": "#8ea2bd",
    "blue": "#4ea1ff",
    "teal": "#2dd4bf",
    "green": "#35c48b",
    "amber": "#f5b942",
    "red": "#f36b74",
    "purple": "#a78bfa",
}

st.markdown(
    """
    <style>
      html, body, [class*="css"] { font-family: 'DM Sans', 'Segoe UI', sans-serif; }
      .stApp { background: radial-gradient(circle at 80% 0%, #14263e 0%, #091321 43%, #07101c 100%); color: #eef4ff; }
      [data-testid="stSidebar"] { background: #0b1727; border-right: 1px solid #23344b; }
      [data-testid="stSidebar"] * { color: #dce8f8; }
      .block-container { padding-top: 1.35rem; padding-bottom: 2rem; max-width: 1600px; }
      h1, h2, h3 { font-family: 'Manrope', sans-serif !important; letter-spacing: -0.035em; }
      h1 { font-weight: 800 !important; }
      h2, h3 { color: #edf4ff; }
      [data-testid="stMetric"] { background: #111e30; border: 1px solid #243750; padding: 14px 16px; border-radius: 14px; }
      [data-testid="stMetricLabel"] { color: #9db0c9 !important; }
      [data-testid="stMetricValue"] { color: #f3f7ff !important; }
      div[data-testid="stDataFrame"] { border: 1px solid #263750; border-radius: 12px; overflow: hidden; }
      .hero { padding: 1.25rem 1.45rem; border: 1px solid #29415f; border-radius: 18px; background: linear-gradient(120deg, rgba(22,44,70,.96), rgba(13,28,46,.96)); margin-bottom: 1.15rem; }
      .eyebrow { color: #69b2ff; font-size: .72rem; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; }
      .hero-title { font-family: 'Manrope', sans-serif; color: #f5f8ff; font-size: 1.9rem; line-height: 1.1; font-weight: 800; margin: .35rem 0 .45rem; }
      .hero-sub { color: #a9bbd2; font-size: .92rem; }
      .pill { display:inline-block; padding: .28rem .58rem; border-radius: 99px; border: 1px solid #34516f; background:#102841; color:#9dd0ff; font-size:.68rem; font-weight:700; letter-spacing:.07em; }
      .pill-demo { border-color:#765d2a; color:#ffd27b; background:#332817; }
      .section-kicker { color:#78baff; text-transform:uppercase; letter-spacing:.13em; font-size:.68rem; font-weight:700; margin-bottom:.15rem; }
      .section-title { font-family:'Manrope',sans-serif; font-size:1.16rem; color:#f0f5ff; font-weight:700; margin-bottom:.65rem; }
      .insight { padding: .85rem 1rem; background:#101e30; border:1px solid #263b55; border-left:3px solid #4ea1ff; border-radius:11px; margin:.35rem 0; color:#d9e6f7; }
      .muted { color:#8ea2bd; }
      .small-note { color:#91a5c0; font-size:.76rem; }
      .stButton>button, .stDownloadButton>button { border-radius:9px; border:1px solid #365374; background:#173656; color:#edf6ff; font-weight:600; }
      .stButton>button:hover, .stDownloadButton>button:hover { border-color:#67b5ff; color:#fff; background:#1d456e; }
      [data-baseweb="select"] > div, [data-baseweb="input"] > div { background:#101e30; border-color:#2c4059; }
      hr { border-color:#23364e; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def make_demo_data() -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(42)
    today = pd.Timestamp.today().normalize()

    wh_seed = [
        ("WH-DEL", "North Hub", "Delhi", "North", "Regional Distribution"),
        ("WH-MUM", "West Hub", "Mumbai", "West", "Fulfilment Centre"),
        ("WH-BLR", "South Hub", "Bengaluru", "South", "Regional Distribution"),
    ]
    categories = ["Electronics", "Home & Kitchen", "Apparel", "Grocery", "Personal Care", "Sports", "Toys", "Office Supplies"]
    product_rows = []
    for i in range(1, 161):
        cat = categories[(i - 1) % len(categories)]
        cost = float(rng.integers(80, 6500)) + float(rng.integers(0, 99)) / 100
        product_rows.append({
            "sku_id": f"SKU-{i:04d}",
            "product_name": f"{cat.split()[0]} Product {i:03d}",
            "category": cat,
            "unit_cost": round(cost, 2),
            "unit_price": round(cost * float(rng.uniform(1.15, 1.85)), 2),
        })
    products = pd.DataFrame(product_rows)

    warehouse_rows, zone_rows, rack_rows = [], [], []
    zone_names = ["RECEIVING", "BULK", "PICK-FACE", "SECURE", "DISPATCH"]
    for wh_id, wh_name, city, region, wh_type in wh_seed:
        wh_rack_capacity = 0
        for zi, zone in enumerate(zone_names, start=1):
            zone_id = f"{wh_id}-Z{zi:02d}"
            zone_rows.append({"zone_id": zone_id, "warehouse_id": wh_id, "zone_name": zone, "zone_type": zone})
            for ri in range(1, 9):
                rack_id = f"{wh_id}-R{zi:02d}{ri:02d}"
                cap = int(rng.integers(300, 451))
                wh_rack_capacity += cap
                rack_rows.append({
                    "rack_id": rack_id, "warehouse_id": wh_id, "zone_id": zone_id,
                    "rack_name": f"Rack {zi:02d}-{ri:02d}", "capacity_units": cap,
                })
        warehouse_rows.append({
            "warehouse_id": wh_id, "warehouse_name": wh_name, "city": city,
            "region": region, "total_capacity_units": wh_rack_capacity, "warehouse_type": wh_type,
        })
    warehouses = pd.DataFrame(warehouse_rows)
    zones = pd.DataFrame(zone_rows)
    racks = pd.DataFrame(rack_rows)

    inv_rows = []
    sku_ids = products["sku_id"].to_numpy()
    for rack in racks.to_dict("records"):
        target = int(rack["capacity_units"] * float(rng.uniform(0.32, 0.94)))
        weights = rng.dirichlet(np.ones(5) * 2.2)
        quantities = np.maximum(1, np.floor(weights * target).astype(int))
        for j, qty in enumerate(quantities):
            sku = str(rng.choice(sku_ids))
            last_days = int(rng.choice([rng.integers(0, 31), rng.integers(31, 61), rng.integers(61, 91), rng.integers(91, 181)], p=[.44, .27, .16, .13]))
            reorder = int(rng.integers(24, 72))
            safety = int(rng.integers(10, max(11, reorder - 4)))
            inv_rows.append({
                "inventory_id": f"INV-{len(inv_rows)+1:05d}",
                "warehouse_id": rack["warehouse_id"], "zone_id": rack["zone_id"],
                "rack_id": rack["rack_id"], "sku_id": sku,
                "quantity_on_hand": int(qty), "reorder_level": reorder,
                "safety_stock": safety, "last_movement_date": today - pd.Timedelta(days=last_days),
                "lot_status": str(rng.choice(["AVAILABLE", "AVAILABLE", "QUALITY HOLD", "RESERVED"], p=[.68, .16, .08, .08])),
            })
    inventory = pd.DataFrame(inv_rows).merge(products, on="sku_id", how="left")

    movement_types = ["RECEIPT", "PICK", "TRANSFER_IN", "TRANSFER_OUT", "ADJUSTMENT"]
    movement_rows = []
    for i in range(1, 1801):
        item = inventory.iloc[int(rng.integers(0, len(inventory)))]
        days_ago = int(rng.integers(0, 366))
        movement_rows.append({
            "movement_id": f"MOV-{i:05d}", "movement_date": today - pd.Timedelta(days=days_ago),
            "warehouse_id": item["warehouse_id"], "sku_id": item["sku_id"], "rack_id": item["rack_id"],
            "movement_type": str(rng.choice(movement_types, p=[.24, .38, .13, .17, .08])),
            "quantity": int(rng.integers(1, 91)), "reference_id": f"REF-{int(rng.integers(10000, 99999))}",
        })
    movements = pd.DataFrame(movement_rows)

    supplier_names = ["Apex Components", "BluePeak Trading", "Crestline Supply", "Delta Wholesale", "Evergreen Imports", "Frontier Distributors", "Global Source Co.", "Horizon Goods"]
    inbound_rows = []
    for i in range(1, 321):
        wh = wh_seed[int(rng.integers(0, 3))][0]
        expected = today - pd.Timedelta(days=int(rng.integers(0, 150)))
        status = str(rng.choice(["RECEIVED", "PARTIAL", "PENDING"], p=[.70, .18, .12]))
        delay = int(rng.integers(-2, 8)) if status != "PENDING" else None
        received_date = (expected + pd.Timedelta(days=delay)) if delay is not None else pd.NaT
        units_exp = int(rng.integers(80, 1600))
        units_rec = (
            int(units_exp * rng.uniform(.94, 1.04))
            if status == "RECEIVED"
            else int(units_exp * rng.uniform(.25, .82))
            if status == "PARTIAL"
            else 0
        )
        inbound_rows.append({
            "receipt_id": f"RCV-{i:05d}", "warehouse_id": wh,
            "supplier_name": str(rng.choice(supplier_names)), "expected_date": expected,
            "received_date": received_date, "units_expected": units_exp, "units_received": units_rec,
            "inspection_status": str(rng.choice(["PASSED", "PENDING", "FAILED"], p=[.78, .17, .05])),
            "receipt_status": status,
        })
    inbound = pd.DataFrame(inbound_rows)

    outbound_rows = []
    regions = ["North", "South", "East", "West", "Central"]
    for i in range(1, 451):
        wh = wh_seed[int(rng.integers(0, 3))][0]
        order_date = today - pd.Timedelta(days=int(rng.integers(0, 150)))
        status = str(rng.choice(["DISPATCHED", "PICKING", "PENDING", "CANCELLED"], p=[.72, .11, .12, .05]))
        units_ordered = int(rng.integers(5, 420))
        if status == "DISPATCHED":
            units_dispatched = int(units_ordered * rng.uniform(.94, 1.0))
            units_picked = units_dispatched
            dispatch_date = order_date + pd.Timedelta(days=int(rng.integers(0, 6)))
        elif status == "PICKING":
            units_picked = int(units_ordered * rng.uniform(.2, .85))
            units_dispatched = 0
            dispatch_date = pd.NaT
        else:
            units_picked = 0
            units_dispatched = 0
            dispatch_date = pd.NaT
        outbound_rows.append({
            "order_id": f"ORD-{i:05d}", "warehouse_id": wh, "order_date": order_date,
            "dispatch_date": dispatch_date, "customer_region": str(rng.choice(regions)),
            "units_ordered": units_ordered, "units_picked": units_picked,
            "units_dispatched": units_dispatched, "order_status": status,
            "picking_duration_minutes": round(float(rng.uniform(8, 145)), 1) if status in ["DISPATCHED", "PICKING"] else np.nan,
        })
    outbound = pd.DataFrame(outbound_rows)

    return {
        "warehouses": warehouses, "zones": zones, "racks": racks,
        "products": products, "inventory": inventory,
        "movements": movements, "inbound": inbound, "outbound": outbound,
    }

FIELD_CONFIG = {
    "warehouse_id": ("Warehouse / location", ["warehouse_id", "warehouse", "location", "warehouse_name", "site", "facility"]),
    "sku_id": ("SKU / product ID", ["sku_id", "sku", "product_id", "item_id", "product_code", "item_code"]),
    "quantity_on_hand": ("Quantity / stock", ["quantity_on_hand", "quantity", "stock", "qty", "on_hand", "available_qty"]),
    "unit_cost": ("Unit cost (optional)", ["unit_cost", "cost", "cost_per_unit", "purchase_price", "unitpricecost"]),
    "inventory_value_input": ("Inventory value (optional)", ["inventory_value", "stock_value", "total_value", "value"]),
    "category": ("Category (optional)", ["category", "product_category", "item_category", "product_group"]),
    "rack_id": ("Rack / bin (optional)", ["rack_id", "rack", "bin", "bin_location", "storage_location"]),
    "zone_id": ("Zone (optional)", ["zone_id", "zone", "area"]),
    "last_movement_date": ("Last movement date (optional)", ["last_movement_date", "last_moved", "lastmovement", "movement_date", "last_transaction_date"]),
    "product_name": ("Product name (optional)", ["product_name", "product", "item_name", "description", "sku_name"]),
    "reorder_level": ("Reorder level (optional)", ["reorder_level", "reorder_point", "minimum_stock", "min_stock"]),
    "safety_stock": ("Safety stock (optional)", ["safety_stock", "safety_qty", "buffer_stock"]),
    "rack_capacity": ("Rack capacity (optional)", ["rack_capacity", "capacity_units", "bin_capacity"]),
    "warehouse_capacity": ("Warehouse capacity (optional)", ["warehouse_capacity", "total_capacity_units", "storage_capacity"]),
}


def _norm_col(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def _suggest_column(columns: list[str], aliases: list[str]) -> str:
    lookup = {_norm_col(c): c for c in columns}
    for alias in aliases:
        if _norm_col(alias) in lookup:
            return lookup[_norm_col(alias)]
    for col in columns:
        n = _norm_col(col)
        if any(_norm_col(a) in n or n in _norm_col(a) for a in aliases if len(_norm_col(a)) > 3):
            return col
    return "— Not mapped —"


def build_uploaded_model(raw: pd.DataFrame, mapping: dict[str, str]) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    selected = {std: raw[col].copy() for std, col in mapping.items() if col != "— Not mapped —" and col in raw.columns}
    if not all(k in selected for k in ["warehouse_id", "sku_id", "quantity_on_hand"]):
        raise ValueError("Map Warehouse / location, SKU / product ID, and Quantity / stock before loading.")

    inv = pd.DataFrame(index=raw.index)
    inv["inventory_id"] = [f"UPLOAD-{i+1:06d}" for i in range(len(raw))]
    inv["warehouse_id"] = selected["warehouse_id"].astype("string").fillna("Unknown").str.strip()
    inv["sku_id"] = selected["sku_id"].astype("string").fillna("Unknown").str.strip()
    qty_raw = selected["quantity_on_hand"]
    inv["quantity_on_hand"] = pd.to_numeric(qty_raw, errors="coerce")
    invalid_qty = int((qty_raw.notna() & inv["quantity_on_hand"].isna()).sum())
    missing_qty = int(inv["quantity_on_hand"].isna().sum())
    inv["quantity_on_hand"] = inv["quantity_on_hand"].fillna(0)
    numeric_defaults = {
        "unit_cost": np.nan,
        "reorder_level": np.nan,
        "safety_stock": np.nan,
        "rack_capacity": np.nan,
        "warehouse_capacity": np.nan,
    }
    for col, default in numeric_defaults.items():
        inv[col] = pd.to_numeric(selected[col], errors="coerce") if col in selected else default
    for col in ["category", "rack_id", "zone_id", "product_name"]:
        inv[col] = selected[col].astype("string").fillna("Unknown").str.strip() if col in selected else "Unknown"
    inv["last_movement_date"] = (
        pd.to_datetime(selected["last_movement_date"], errors="coerce")
        if "last_movement_date" in selected
        else pd.NaT
    )
    source_value = (
        pd.to_numeric(selected["inventory_value_input"], errors="coerce")
        if "inventory_value_input" in selected
        else pd.Series(np.nan, index=raw.index)
    )
    calculated_value = inv["quantity_on_hand"] * inv["unit_cost"]
    inv["inventory_value"] = source_value.fillna(calculated_value)

    wh = inv[["warehouse_id", "warehouse_capacity"]].drop_duplicates("warehouse_id").copy()
    wh["warehouse_name"] = wh["warehouse_id"]
    wh["city"] = "Not provided"
    wh["region"] = "Not provided"
    wh["total_capacity_units"] = wh["warehouse_capacity"]
    wh["warehouse_type"] = "Uploaded inventory"
    warehouses = wh[["warehouse_id", "warehouse_name", "city", "region", "total_capacity_units", "warehouse_type"]]

    products = inv[["sku_id", "product_name", "category", "unit_cost"]].drop_duplicates("sku_id").copy()
    products["unit_price"] = np.nan
    zones = inv[["zone_id", "warehouse_id"]].drop_duplicates().copy()
    zones["zone_name"] = zones["zone_id"]
    zones["zone_type"] = "Uploaded"
    racks = inv[["rack_id", "warehouse_id", "zone_id", "rack_capacity"]].drop_duplicates(
        ["warehouse_id", "zone_id", "rack_id"]
    ).copy()
    racks = racks[racks["rack_id"].astype(str).ne("Unknown")]
    racks["rack_name"] = racks["rack_id"]
    racks = racks.rename(columns={"rack_capacity": "capacity_units"})
    if racks["capacity_units"].isna().all():
        racks = pd.DataFrame(columns=["rack_id", "warehouse_id", "zone_id", "rack_name", "capacity_units"])

    quality = {
        "rows": int(len(raw)), "columns": int(len(raw.columns)),
        "missing_cells": int(raw.isna().sum().sum()),
        "duplicate_rows": int(raw.duplicated().sum()),
        "invalid_quantity_values": invalid_qty, "missing_quantity_values": missing_qty,
        "unmapped_columns": [c for c in raw.columns if c not in mapping.values()],
    }
    model = {
        "warehouses": warehouses, "zones": zones, "racks": racks,
        "products": products, "inventory": inv,
        "movements": pd.DataFrame(), "inbound": pd.DataFrame(), "outbound": pd.DataFrame(),
    }
    return model, quality


def money(value: Any) -> str:
    return "—" if pd.isna(value) else f"₹{float(value):,.0f}"


def number(value: Any) -> str:
    return "—" if pd.isna(value) else f"{float(value):,.0f}"


def pct(value: Any) -> str:
    return "—" if pd.isna(value) else f"{float(value):.1f}%"


def dark_chart(fig: go.Figure, height: int = 330) -> go.Figure:
    fig.update_layout(
        template="plotly_dark", height=height, paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(family="DM Sans", color="#c7d5e8", size=11),
        margin=dict(l=18, r=18, t=30, b=18), legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.12),
        hoverlabel=dict(bgcolor="#14243a", bordercolor="#365374", font_color="#eef4ff"),
    )
    fig.update_xaxes(gridcolor="#24364c", zerolinecolor="#24364c", linecolor="#30445d")
    fig.update_yaxes(gridcolor="#24364c", zerolinecolor="#24364c", linecolor="#30445d")
    return fig


def section(title: str, kicker: str | None = None) -> None:
    if kicker:
        st.markdown(f'<div class="section-kicker">{kicker}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def metric_row(items: list[tuple[str, str, str | None]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value, help_text) in zip(cols, items):
        with col:
            st.metric(label, value, help=help_text)


def add_inventory_fields(inv: pd.DataFrame) -> pd.DataFrame:
    out = inv.copy()
    if "inventory_value" not in out.columns:
        if "unit_cost" in out.columns:
            out["inventory_value"] = out["quantity_on_hand"] * out["unit_cost"]
        else:
            out["inventory_value"] = np.nan
    elif "unit_cost" in out.columns:
        out["inventory_value"] = out["inventory_value"].where(out["inventory_value"].notna(), out["quantity_on_hand"] * out["unit_cost"])
    if "last_movement_date" in out.columns:
        out["last_movement_date"] = pd.to_datetime(out["last_movement_date"], errors="coerce")
        out["days_since_movement"] = (pd.Timestamp.today().normalize() - out["last_movement_date"]).dt.days
    else:
        out["days_since_movement"] = np.nan
    defaults = {
        "reorder_level": np.nan,
        "safety_stock": np.nan,
        "category": "Unknown",
        "product_name": out["sku_id"].astype(str),
        "zone_id": "Unknown",
        "rack_id": "Unknown",
        "warehouse_id": "Unknown",
    }
    for column, value in defaults.items():
        if column not in out:
            out[column] = value
    out["stock_status"] = np.select(
        [out["quantity_on_hand"].le(0), out["safety_stock"].notna() & out["quantity_on_hand"].lt(out["safety_stock"]),
         out["reorder_level"].notna() & out["quantity_on_hand"].le(out["reorder_level"]),
         out["reorder_level"].notna()],
        ["Out of Stock", "Critical", "Low Stock", "Healthy"], default="Not assessed",
    )
    return out


def rack_summary(model: dict[str, pd.DataFrame], inv: pd.DataFrame | None = None) -> pd.DataFrame:
    racks = model.get("racks", pd.DataFrame()).copy()
    if racks.empty or "capacity_units" not in racks.columns:
        return pd.DataFrame()
    source = inv if inv is not None else add_inventory_fields(model["inventory"])
    if source.empty:
        return pd.DataFrame()
    if "warehouse_id" in source.columns:
        racks = racks[racks["warehouse_id"].astype(str).isin(source["warehouse_id"].astype(str).unique())]
    if "zone_id" in source.columns:
        racks = racks[racks["zone_id"].astype(str).isin(source["zone_id"].astype(str).unique())]
    if racks.empty:
        return pd.DataFrame()
    occ = source.groupby(["warehouse_id", "zone_id", "rack_id"], dropna=False)["quantity_on_hand"].sum().reset_index(name="occupied_units")
    result = racks.merge(occ, on=["warehouse_id", "zone_id", "rack_id"], how="left")
    result["occupied_units"] = result["occupied_units"].fillna(0)
    result["available_units"] = (result["capacity_units"] - result["occupied_units"]).clip(lower=0)
    result["utilization_pct"] = np.where(result["capacity_units"].gt(0), result["occupied_units"] / result["capacity_units"] * 100, np.nan)
    result["rack_status"] = np.select(
        [result["occupied_units"].eq(0), result["utilization_pct"].ge(95), result["utilization_pct"].ge(85)],
        ["Empty", "Critical", "High"], default="Healthy",
    )
    return result


def build_alerts(
    inv: pd.DataFrame,
    racks: pd.DataFrame,
    inbound: pd.DataFrame,
    outbound: pd.DataFrame,
    pending_days: int = 3,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    today = pd.Timestamp.today().normalize()
    for r in inv.itertuples(index=False):
        status = getattr(r, "stock_status", "Not assessed")
        if status in ("Out of Stock", "Critical", "Low Stock"):
            severity = "Critical" if status in ("Out of Stock", "Critical") else "High"
            rows.append({"alert_type": status, "warehouse_id": r.warehouse_id, "related_item": r.sku_id,
                         "severity": severity, "alert_date": today, "explanation": f"{r.sku_id} has {r.quantity_on_hand:,.0f} units against reorder level {r.reorder_level if pd.notna(r.reorder_level) else 'not provided'}.",
                         "recommended_next_step": "Review replenishment and confirm open purchase orders.", "status": "Open"})
        age = getattr(r, "days_since_movement", np.nan)
        if pd.notna(age) and age > 90:
            rows.append({"alert_type": "Ageing inventory", "warehouse_id": r.warehouse_id, "related_item": r.sku_id,
                         "severity": "Medium" if age <= 150 else "High", "alert_date": today, "explanation": f"No movement recorded for {int(age)} days.",
                         "recommended_next_step": "Validate demand, consider transfer or markdown, and review replenishment.", "status": "Open"})
    if not racks.empty:
        for r in racks.loc[racks["utilization_pct"].ge(90)].itertuples(index=False):
            rows.append({"alert_type": "Rack over 90%", "warehouse_id": r.warehouse_id, "related_item": r.rack_id,
                         "severity": "High" if r.utilization_pct >= 97 else "Medium", "alert_date": today,
                         "explanation": f"Rack utilization is {r.utilization_pct:.1f}%.",
                         "recommended_next_step": "Review slotting and move suitable stock to available locations.", "status": "Open"})
    if not inbound.empty:
        temp = inbound.copy()
        temp["expected_date"] = pd.to_datetime(temp["expected_date"], errors="coerce")
        temp["received_date"] = pd.to_datetime(temp["received_date"], errors="coerce")
        delayed = temp[
            (temp["received_date"].isna() & temp["expected_date"].lt(today))
            | (temp["received_date"].notna() & temp["received_date"].gt(temp["expected_date"]))
        ]
        for r in delayed.itertuples(index=False):
            delay = (today - r.expected_date).days if pd.isna(r.received_date) else (r.received_date - r.expected_date).days
            rows.append({"alert_type": "Inbound delay", "warehouse_id": r.warehouse_id, "related_item": r.receipt_id,
                         "severity": "High" if delay > 5 else "Medium", "alert_date": r.expected_date,
                         "explanation": f"Receipt {r.receipt_id} is delayed by approximately {max(0, int(delay))} days.",
                         "recommended_next_step": "Contact supplier and update the receiving schedule.", "status": "Open"})
    if not outbound.empty:
        temp = outbound.copy()
        temp["order_date"] = pd.to_datetime(temp["order_date"], errors="coerce")
        stale = temp[(temp["order_status"].isin(["PENDING", "PICKING"])) & temp["order_date"].lt(today - pd.Timedelta(days=pending_days))]
        for r in stale.itertuples(index=False):
            age = (today - r.order_date).days
            rows.append({"alert_type": "Pending outbound order", "warehouse_id": r.warehouse_id, "related_item": r.order_id,
                         "severity": "High" if age > pending_days + 3 else "Medium", "alert_date": r.order_date,
                         "explanation": f"Order {r.order_id} remains {r.order_status.lower()} for {age} days.",
                         "recommended_next_step": "Check picking availability and resolve dispatch blockers.", "status": "Open"})
    return pd.DataFrame(rows, columns=["alert_type", "warehouse_id", "related_item", "severity", "alert_date", "explanation", "recommended_next_step", "status"])

FILTER_STATE_KEYS = ("flt_wh", "flt_region", "flt_cat", "flt_sku", "flt_zone", "flt_dates")


def reset_filters_for_source(session_state: Any, source_key: str) -> None:
    if session_state.get("_filter_source") == source_key:
        return
    for key in FILTER_STATE_KEYS:
        session_state.pop(key, None)
    session_state["_filter_source"] = source_key


def apply_filters(
    model: dict[str, pd.DataFrame], inv: pd.DataFrame
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, Any]]:
    warehouses = model["warehouses"].copy()
    warehouse_options = sorted(inv["warehouse_id"].dropna().astype(str).unique().tolist())
    region_map = {}
    if not warehouses.empty and {"warehouse_id", "region"}.issubset(warehouses.columns):
        region_map = warehouses.set_index("warehouse_id")["region"].to_dict()
    inv_regions = sorted({str(region_map.get(w, "Not provided")) for w in warehouse_options})

    st.sidebar.markdown("### Global filters")
    wh_selected = st.sidebar.multiselect("Warehouse", warehouse_options, default=warehouse_options, key="flt_wh")
    region_selected = st.sidebar.multiselect("Region", inv_regions, default=inv_regions, key="flt_region")
    cat_options = sorted(inv["category"].dropna().astype(str).unique().tolist())
    cat_selected = st.sidebar.multiselect("Product category", cat_options, default=cat_options, key="flt_cat")
    sku_options = sorted(inv["sku_id"].dropna().astype(str).unique().tolist())
    sku_selected = st.sidebar.multiselect("SKU", sku_options, default=sku_options, key="flt_sku")
    zone_options = sorted(inv["zone_id"].dropna().astype(str).unique().tolist())
    zone_selected = st.sidebar.multiselect("Zone", zone_options, default=zone_options, key="flt_zone")
    today = pd.Timestamp.today().date()
    date_range = st.sidebar.date_input("Operational date range", value=(today - timedelta(days=90), today), key="flt_dates")
    if st.sidebar.button("Reset all filters", use_container_width=True):
        for key in FILTER_STATE_KEYS:
            st.session_state.pop(key, None)
        st.rerun()

    filtered_inv = inv.copy()
    if wh_selected:
        filtered_inv = filtered_inv[filtered_inv["warehouse_id"].astype(str).isin(wh_selected)]
    if region_selected:
        regions = filtered_inv["warehouse_id"].map(region_map).fillna("Not provided").astype(str)
        filtered_inv = filtered_inv[regions.isin(region_selected)]
    if cat_selected:
        filtered_inv = filtered_inv[filtered_inv["category"].astype(str).isin(cat_selected)]
    if sku_selected:
        filtered_inv = filtered_inv[filtered_inv["sku_id"].astype(str).isin(sku_selected)]
    if zone_selected:
        filtered_inv = filtered_inv[filtered_inv["zone_id"].astype(str).isin(zone_selected)]
    if not all((wh_selected, region_selected, cat_selected, sku_selected, zone_selected)):
        filtered_inv = filtered_inv.iloc[0:0]

    start_date, end_date = (
        date_range
        if isinstance(date_range, (tuple, list)) and len(date_range) == 2
        else (today - timedelta(days=90), today)
    )
    date_start, date_end = pd.Timestamp(start_date), pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    ops = {}
    for name in ["movements", "inbound", "outbound"]:
        df = model.get(name, pd.DataFrame()).copy()
        if not df.empty:
            date_col = {"movements": "movement_date", "inbound": "expected_date", "outbound": "order_date"}[name]
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df = df[df[date_col].between(date_start, date_end)]
            if wh_selected:
                df = df[df["warehouse_id"].astype(str).isin(wh_selected)]
            if region_selected and region_map:
                regions = df["warehouse_id"].map(region_map).fillna("Not provided").astype(str)
                df = df[regions.isin(region_selected)]
            if not wh_selected or not region_selected:
                df = df.iloc[0:0]
        ops[name] = df
    return filtered_inv, ops


def sku_summary(inv: pd.DataFrame) -> pd.DataFrame:
    if inv.empty: return pd.DataFrame()
    agg = inv.groupby("sku_id", dropna=False).agg(
        product_name=("product_name", "first"), category=("category", "first"),
        quantity_on_hand=("quantity_on_hand", "sum"), inventory_value=("inventory_value", lambda s: s.sum(min_count=1)),
        reorder_level=("reorder_level", lambda s: s.sum(min_count=1)), safety_stock=("safety_stock", lambda s: s.sum(min_count=1)),
        days_since_movement=("days_since_movement", "max"),
    ).reset_index()
    agg = agg.sort_values("inventory_value", ascending=False, na_position="last").reset_index(drop=True)
    total_val = agg["inventory_value"].sum(min_count=1)
    if pd.notna(total_val) and total_val > 0:
        agg["value_share_pct"] = agg["inventory_value"].fillna(0) / total_val * 100
        agg["cumulative_value_pct"] = agg["value_share_pct"].cumsum()
        agg["ABC_class_calc"] = np.select([agg["cumulative_value_pct"].le(80), agg["cumulative_value_pct"].le(95)], ["A", "B"], default="C")
    else:
        agg["value_share_pct"] = np.nan
        agg["cumulative_value_pct"] = np.nan
        agg["ABC_class_calc"] = "Not available"
    return agg


def warehouse_summary(inv: pd.DataFrame, model: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if inv.empty: return pd.DataFrame()
    out = inv.groupby("warehouse_id").agg(inventory_units=("quantity_on_hand", "sum"), inventory_value=("inventory_value", lambda s: s.sum(min_count=1)), active_skus=("sku_id", "nunique")).reset_index()
    wh = model["warehouses"].copy()
    if not wh.empty:
        out = out.merge(wh, on="warehouse_id", how="left")
    rack = rack_summary(model, inv)
    if not rack.empty:
        cap = rack.groupby("warehouse_id").agg(occupied_units=("occupied_units", "sum"), capacity_units=("capacity_units", "sum")).reset_index()
        cap["capacity_utilization_pct"] = np.where(cap["capacity_units"].gt(0), cap["occupied_units"] / cap["capacity_units"] * 100, np.nan)
        out = out.merge(cap[["warehouse_id", "capacity_units", "capacity_utilization_pct"]], on="warehouse_id", how="left")
    elif "total_capacity_units" in out.columns and out["total_capacity_units"].notna().any():
        out["capacity_utilization_pct"] = np.where(out["total_capacity_units"].gt(0), out["inventory_units"] / out["total_capacity_units"] * 100, np.nan)
    else:
        out["capacity_utilization_pct"] = np.nan
    if "warehouse_name" not in out: out["warehouse_name"] = out["warehouse_id"]
    return out


def show_csv_download(label: str, df: pd.DataFrame, filename: str, key: str) -> None:
    st.download_button(label, df.to_csv(index=False).encode("utf-8-sig"), file_name=filename, mime="text/csv", key=key, use_container_width=True)


def chart_empty(message: str = "Not available in uploaded data") -> None:
    st.info(message)

st.sidebar.markdown(
    "<div class='eyebrow'>OPERATIONS ANALYTICS</div>"
    "<h2 style='margin:.2rem 0 0;'>WAREHOUSE<br>INTELLIGENCE</h2>"
    "<div class='small-note'>Inventory · Operations · Spatial Analytics</div>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")
source_mode = st.sidebar.radio("Data source", ["Demo dataset", "Upload CSV"], index=0, key="data_source_mode")
quality_info: dict[str, Any] | None = None

if source_mode == "Demo dataset":
    model = make_demo_data()
    st.session_state.pop("upload_model", None)
    st.session_state.pop("upload_quality", None)
else:
    uploaded = st.sidebar.file_uploader("Upload inventory CSV", type=["csv"], help="Single inventory CSV. Your original file is not changed.")
    model = None
    if uploaded is not None:
        try:
            raw_csv = pd.read_csv(io.BytesIO(uploaded.getvalue()))
            st.sidebar.caption(f"File loaded: {len(raw_csv):,} rows × {len(raw_csv.columns)} columns")
            with st.sidebar.expander("Map columns", expanded=True):
                mapping = {}
                cols = list(raw_csv.columns)
                left, right = st.columns(2)
                for i, (std, (label, aliases)) in enumerate(FIELD_CONFIG.items()):
                    container = left if i % 2 == 0 else right
                    suggestion = _suggest_column(cols, aliases)
                    default_index = (["— Not mapped —"] + cols).index(suggestion)
                    with container:
                        mapping[std] = st.selectbox(label, ["— Not mapped —"] + cols, index=default_index, key=f"mapping_{std}")
                st.caption("Required: warehouse/location, SKU/product ID and quantity/stock. Other fields are optional.")
                if st.button("Apply mapping and load data", key="apply_mapping", use_container_width=True):
                    try:
                        mapped_model, quality_info = build_uploaded_model(raw_csv, mapping)
                        st.session_state["upload_model"] = mapped_model
                        st.session_state["upload_quality"] = quality_info
                        st.session_state["upload_filename"] = uploaded.name
                        st.session_state["upload_signature"] = hashlib.sha256(uploaded.getvalue()).hexdigest()
                        st.success("Inventory CSV mapped and loaded.")
                    except Exception as exc:
                        st.error(str(exc))
            model = st.session_state.get("upload_model")
            quality_info = st.session_state.get("upload_quality")
        except Exception as exc:
            st.sidebar.error(f"Could not read CSV: {exc}")
    else:
        model = st.session_state.get("upload_model")
        quality_info = st.session_state.get("upload_quality")
    if model is None:
        st.warning("Upload an inventory CSV and apply the column mapping. Until then, switch to Demo dataset to explore the working application.")
        st.stop()

is_demo = source_mode == "Demo dataset"
source_key = (
    "demo"
    if is_demo
    else f"upload:{st.session_state.get('upload_signature', st.session_state.get('upload_filename', 'inventory'))}"
)
reset_filters_for_source(st.session_state, source_key)
inv_all = add_inventory_fields(model["inventory"])

source_label = "DEMO DATA" if is_demo else f"CSV · {st.session_state.get('upload_filename', 'inventory.csv')}"
st.markdown(
    f"<div class='hero'><div class='eyebrow'>WAREHOUSE INTELLIGENCE <span style='color:#617995'>/</span> OPERATIONS CONTROL TOWER</div>"
    f"<div class='hero-title'>See every zone. Understand every movement. Control every operation.</div>"
    f"<div class='hero-sub'>Digital Twin &amp; Operational Analytics Command Center&nbsp;&nbsp; <span class='pill {'pill-demo' if is_demo else ''}'>{source_label}</span></div>"
    f"<div class='small-note' style='margin-top:.65rem'>Updated {datetime.now().strftime('%d %b %Y · %H:%M')}</div></div>",
    unsafe_allow_html=True,
)

inv, ops = apply_filters(model, inv_all)
inv = add_inventory_fields(inv)
skus = sku_summary(inv)
wh_summary = warehouse_summary(inv, model)
racks_filtered = rack_summary(model, inv)
alerts = build_alerts(inv, racks_filtered, ops.get("inbound", pd.DataFrame()), ops.get("outbound", pd.DataFrame()))

pages = ["Command Center", "3D Digital Twin", "2D Floor Plan", "Inventory Intelligence", "Rack & Bin Explorer", "Warehouse Map", "Inbound Operations", "Outbound Operations", "Workforce & Equipment", "Space Optimization", "Risk & Exceptions", "Insights & Recommendations", "Automation Center", "Data Explorer", "Settings"]
page = st.sidebar.radio("Workspace", pages, key="workspace_page")
st.sidebar.markdown("---")
st.sidebar.caption("Warehouse Operations Control Tower")

inventory_units = inv["quantity_on_hand"].sum() if not inv.empty else 0
inventory_value = inv["inventory_value"].sum(min_count=1) if not inv.empty else np.nan
active_skus = inv["sku_id"].nunique() if not inv.empty else 0
low_stock = inv.loc[inv["stock_status"].isin(["Critical", "Low Stock", "Out of Stock"]), "sku_id"].nunique() if not inv.empty else 0
out_of_stock = inv.loc[inv["stock_status"].eq("Out of Stock"), "sku_id"].nunique() if not inv.empty else 0
dead_value = inv.loc[inv["days_since_movement"].gt(90), "inventory_value"].sum(min_count=1) if not inv.empty else np.nan
capacity_util = np.nan
if not racks_filtered.empty:
    cap_total = racks_filtered["capacity_units"].sum()
    capacity_util = racks_filtered["occupied_units"].sum() / cap_total * 100 if cap_total else np.nan
elif not wh_summary.empty and wh_summary["capacity_utilization_pct"].notna().any():
    capacity_util = np.average(wh_summary["capacity_utilization_pct"].dropna(), weights=wh_summary.loc[wh_summary["capacity_utilization_pct"].notna(), "total_capacity_units"] if "total_capacity_units" in wh_summary else None)

if page == "Command Center":
    section("Executive overview", "01 / COMMAND VIEW")
    st.caption("Current inventory snapshot follows the selected warehouse, region, category, SKU and zone filters. The date filter applies to operational trends and receipt/order analysis.")
    metric_row([
        ("Total inventory units", number(inventory_units), "Sum of quantity on hand in the filtered inventory snapshot."),
        ("Inventory value", money(inventory_value), "Quantity × unit cost, or source-provided inventory value."),
        ("Active SKUs", number(active_skus), "Distinct SKUs in the filtered inventory."),
        ("Capacity utilization", pct(capacity_util), "Calculated only when capacity data is available."),
        ("Low-stock SKUs", number(low_stock), "Distinct SKUs below their reorder level, including critical stock."),
        ("Dead / non-moving value", money(dead_value), "Value for inventory with no movement recorded for more than 90 days."),
    ])
    if inv.empty: st.warning("No inventory records match the current filters. Reset filters or select a different scope.")
    c1, c2 = st.columns([1.12, .88])
    with c1:
        section("Inventory value by warehouse", "VALUE DISTRIBUTION")
        if not wh_summary.empty and wh_summary["inventory_value"].notna().any():
            fig = px.bar(wh_summary, x="warehouse_name", y="inventory_value", color="warehouse_name", text_auto=".2s")
            fig.update_layout(showlegend=False, yaxis_title="Inventory value (₹)", xaxis_title="")
            st.plotly_chart(dark_chart(fig, 310), use_container_width=True)
        else: chart_empty("Inventory value requires unit cost or a source-provided inventory value column.")
    with c2:
        section("Inventory units by category", "STOCK MIX")
        if not inv.empty:
            cat = inv.groupby("category", dropna=False)["quantity_on_hand"].sum().reset_index().sort_values("quantity_on_hand", ascending=False)
            fig = px.pie(cat, names="category", values="quantity_on_hand", hole=.62)
            fig.update_traces(textposition="inside", textinfo="percent")
            st.plotly_chart(dark_chart(fig, 310), use_container_width=True)
        else: chart_empty()

    c3, c4 = st.columns(2)
    with c3:
        section("Daily inbound vs outbound", "OPERATIONAL FLOW")
        inbound, outbound = ops["inbound"], ops["outbound"]
        if not inbound.empty or not outbound.empty:
            i_daily = inbound.groupby("expected_date")["units_received"].sum().rename("Inbound received") if not inbound.empty else pd.Series(dtype=float)
            o_daily = outbound.groupby("order_date")["units_dispatched"].sum().rename("Outbound dispatched") if not outbound.empty else pd.Series(dtype=float)
            daily = pd.concat([i_daily, o_daily], axis=1).fillna(0).rename_axis("date").reset_index()
            daily = daily.melt(id_vars="date", var_name="flow", value_name="units")
            fig = px.line(daily, x="date", y="units", color="flow", markers=False)
            st.plotly_chart(dark_chart(fig, 300), use_container_width=True)
        else: chart_empty("Inbound and outbound operational datasets are not available for this source.")
    with c4:
        section("Inventory ageing", "DAYS SINCE LAST MOVEMENT")
        if inv["days_since_movement"].notna().any():
            age = inv.dropna(subset=["days_since_movement"]).copy()
            age["age_bucket"] = pd.cut(age["days_since_movement"], bins=[-1, 30, 60, 90, np.inf], labels=["0–30 days", "31–60 days", "61–90 days", "90+ days"])
            age_df = age.groupby("age_bucket", observed=False)["quantity_on_hand"].sum().reset_index()
            fig = px.bar(age_df, x="age_bucket", y="quantity_on_hand", color="age_bucket")
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Units")
            st.plotly_chart(dark_chart(fig, 300), use_container_width=True)
        else: chart_empty("Last movement date is not available in the uploaded data.")

    c5, c6 = st.columns(2)
    with c5:
        section("Top 10 SKUs by inventory value", "VALUE CONCENTRATION")
        if not skus.empty and skus["inventory_value"].notna().any():
            top = skus.head(10).sort_values("inventory_value")
            fig = px.bar(top, x="inventory_value", y="sku_id", orientation="h", hover_data=["product_name", "category"])
            fig.update_layout(xaxis_title="Inventory value (₹)", yaxis_title="")
            st.plotly_chart(dark_chart(fig, 330), use_container_width=True)
        else: chart_empty("Inventory value is unavailable.")
    with c6:
        section("Warehouse capacity comparison", "SPACE UTILIZATION")
        if not wh_summary.empty and wh_summary["capacity_utilization_pct"].notna().any():
            fig = px.bar(wh_summary, x="warehouse_name", y="capacity_utilization_pct", color="capacity_utilization_pct", range_y=[0, 105], text=wh_summary["capacity_utilization_pct"].round(1).astype(str) + "%")
            fig.update_layout(showlegend=False, yaxis_title="Utilization %", xaxis_title="")
            st.plotly_chart(dark_chart(fig, 330), use_container_width=True)
        else: chart_empty("Capacity is not available. Map rack capacity or warehouse capacity in the uploaded CSV.")

    section("Calculated business summary", "SIGNALS FROM CURRENT FILTERS")
    summary_cols = st.columns(4)
    with summary_cols[0]:
        if not wh_summary.empty:
            best = wh_summary.sort_values("inventory_value", ascending=False).iloc[0]
            st.markdown(f"<div class='insight'><b>Highest inventory value</b><br>{best['warehouse_name']}<br><span class='small-note'>{money(best['inventory_value'])}</span></div>", unsafe_allow_html=True)
        else: st.markdown("<div class='insight'>Highest inventory-value warehouse<br><span class='small-note'>Not available</span></div>", unsafe_allow_html=True)
    with summary_cols[1]:
        cap_ok = wh_summary.dropna(subset=["capacity_utilization_pct"]) if not wh_summary.empty else pd.DataFrame()
        if not cap_ok.empty:
            best = cap_ok.sort_values("capacity_utilization_pct", ascending=False).iloc[0]
            text = f"{best['warehouse_name']} · {pct(best['capacity_utilization_pct'])}"
        else: text = "Not available in source data"
        st.markdown(f"<div class='insight'><b>Highest capacity utilization</b><br><span class='small-note'>{text}</span></div>", unsafe_allow_html=True)
    with summary_cols[2]:
        st.markdown(f"<div class='insight'><b>Low-stock SKUs</b><br><span class='small-note'>{low_stock:,} distinct SKU(s)</span></div>", unsafe_allow_html=True)
    with summary_cols[3]:
        if not inv.empty and inv["inventory_value"].notna().any():
            best_cat = inv.groupby("category")["inventory_value"].sum().sort_values(ascending=False)
            st.markdown(f"<div class='insight'><b>Largest inventory category</b><br>{best_cat.index[0]}<br><span class='small-note'>{money(best_cat.iloc[0])}</span></div>", unsafe_allow_html=True)
        else: st.markdown("<div class='insight'>Largest inventory category<br><span class='small-note'>Value not available</span></div>", unsafe_allow_html=True)

elif page in ("3D Digital Twin", "2D Floor Plan"):
    title = "Interactive 3D warehouse digital twin" if page == "3D Digital Twin" else "Interactive 2D warehouse floor plan"
    section(title, "02 / SPATIAL OPERATIONS")
    st.caption("Select a rack in either view to inspect its capacity, utilization and SKU details.")
    twin_warehouses = sorted(racks_filtered["warehouse_id"].astype(str).unique().tolist()) if not racks_filtered.empty else []
    if not twin_warehouses:
        st.warning("A mapped rack layout is not available for this source. Use Demo dataset, or upload rack/bin, zone and rack capacity fields.")
    else:
        selected_twin_wh = st.selectbox("Warehouse for spatial view", twin_warehouses, key="twin_warehouse")
        twin_racks = racks_filtered[racks_filtered["warehouse_id"].astype(str).eq(selected_twin_wh)].copy().reset_index(drop=True)
        twin_inventory = inv[inv["warehouse_id"].astype(str).eq(selected_twin_wh)].copy()
        wh_info = model["warehouses"]
        if not wh_info.empty and "warehouse_id" in wh_info:
            wh_match = wh_info[wh_info["warehouse_id"].astype(str).eq(selected_twin_wh)]
            twin_name = str(wh_match.iloc[0].get("warehouse_name", selected_twin_wh)) if not wh_match.empty else selected_twin_wh
        else:
            twin_name = selected_twin_wh
        html = build_digital_twin_html(twin_racks, twin_inventory, twin_name, view_mode="2d" if page == "2D Floor Plan" else "both")
        components.html(html, height=1080 if page == "2D Floor Plan" else 1450, scrolling=True)

elif page == "Rack & Bin Explorer":
    section("Rack & bin explorer", "03 / LOCATION DRILL-DOWN")
    if racks_filtered.empty:
        st.info("Add rack ID and rack capacity columns to the CSV to enable location-level analysis.")
    else:
        left, right = st.columns(2)
        rack_wh_options = sorted(racks_filtered["warehouse_id"].astype(str).unique().tolist())
        chosen_wh = left.selectbox("Warehouse", rack_wh_options, key="explorer_wh")
        wh_racks = racks_filtered[racks_filtered["warehouse_id"].astype(str).eq(chosen_wh)].copy()
        chosen_zone_options = ["All zones"] + sorted(wh_racks["zone_id"].astype(str).unique().tolist())
        chosen_zone = right.selectbox("Zone", chosen_zone_options, key="explorer_zone")
        if chosen_zone != "All zones":
            wh_racks = wh_racks[wh_racks["zone_id"].astype(str).eq(chosen_zone)]
        selected_rack_id = st.selectbox("Rack", wh_racks["rack_id"].astype(str).tolist(), key="explorer_rack")
        selected_rack_row = wh_racks[wh_racks["rack_id"].astype(str).eq(selected_rack_id)].iloc[0]
        rack_lines = inv[inv["rack_id"].astype(str).eq(selected_rack_id)].copy()
        rack_value = rack_lines["inventory_value"].sum(min_count=1)
        metric_row([
            ("Location path", f"{chosen_wh} / {chosen_zone if chosen_zone != 'All zones' else selected_rack_row['zone_id']} / {selected_rack_id}", None),
            ("Capacity", number(selected_rack_row["capacity_units"]), None),
            ("Occupied units", number(selected_rack_row["occupied_units"]), None),
            ("Available units", number(selected_rack_row["available_units"]), None),
            ("Utilization", pct(selected_rack_row["utilization_pct"]), None),
            ("Inventory value", money(rack_value), None),
        ])
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"<div class='insight'><b>Location status</b><br>{selected_rack_row['rack_status']}<br><span class='small-note'>{rack_lines['sku_id'].nunique()} SKU(s) · {rack_lines['stock_status'].isin(['Critical','Low Stock','Out of Stock']).sum()} stock-risk line(s)</span></div>", unsafe_allow_html=True)
            st.caption("Rack-level details are shown here. Add shelf or bin columns when available.")
        with c2:
            st.markdown("**SKU-level location contents**")
            cols = [c for c in ["sku_id", "product_name", "category", "quantity_on_hand", "unit_cost", "inventory_value", "last_movement_date", "stock_status"] if c in rack_lines.columns]
            st.dataframe(rack_lines[cols], use_container_width=True, hide_index=True)
        st.markdown("**Warehouse location ranking**")
        st.dataframe(wh_racks.sort_values("utilization_pct", ascending=False), use_container_width=True, hide_index=True)
        show_csv_download("Export rack contents", rack_lines, f"{selected_rack_id}_contents.csv", "rack_contents_export")

elif page == "Inventory Intelligence":
    section("Inventory intelligence", "02 / STOCK HEALTH & VALUE")
    slow_count = inv.loc[inv["days_since_movement"].gt(60), "sku_id"].nunique() if not inv.empty else 0
    metric_row([
        ("Total SKUs", number(active_skus), None), ("Total stock units", number(inventory_units), None),
        ("Inventory value", money(inventory_value), None), ("Low-stock count", number(low_stock), None),
        ("Out-of-stock count", number(out_of_stock), None), ("Slow-moving SKUs", number(slow_count), "More than 60 days since last movement."),
    ])
    if not inv.empty:
        c1, c2 = st.columns(2)
        with c1:
            section("ABC value classification", "CONVENTIONAL CONFIGURABLE 80 / 15 / 5 METHOD")
            if not skus.empty and skus["inventory_value"].notna().any():
                abc = skus.groupby("ABC_class_calc")["sku_id"].count().reindex(["A", "B", "C"], fill_value=0).reset_index(name="sku_count")
                fig = px.pie(abc, names="ABC_class_calc", values="sku_count", hole=.58)
                fig.update_layout(legend_title="Class")
                st.plotly_chart(dark_chart(fig, 300), use_container_width=True)
            else: chart_empty("ABC classification needs inventory value.")
        with c2:
            section("Inventory ageing buckets", "DAYS SINCE LAST MOVEMENT")
            age = inv.dropna(subset=["days_since_movement"]).copy()
            if not age.empty:
                age["age_bucket"] = pd.cut(age["days_since_movement"], [-1, 30, 60, 90, np.inf], labels=["0–30", "31–60", "61–90", "90+"])
                age_df = age.groupby("age_bucket", observed=False).agg(units=("quantity_on_hand", "sum"), value=("inventory_value", "sum")).reset_index()
                fig = px.bar(age_df, x="age_bucket", y="units", color="age_bucket", hover_data=["value"])
                fig.update_layout(showlegend=False, xaxis_title="Days", yaxis_title="Units")
                st.plotly_chart(dark_chart(fig, 300), use_container_width=True)
            else: chart_empty("Last movement date is not available.")
        c3, c4 = st.columns(2)
        with c3:
            section("Category-wise inventory value", "PORTFOLIO MIX")
            if inv["inventory_value"].notna().any():
                cat = inv.groupby("category")["inventory_value"].sum().sort_values(ascending=False).reset_index()
                fig = px.bar(cat, x="category", y="inventory_value", color="category")
                fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Value (₹)")
                st.plotly_chart(dark_chart(fig, 300), use_container_width=True)
            else: chart_empty("Inventory value is unavailable.")
        with c4:
            section("Stock quantity vs reorder level", "REPLENISHMENT WATCH")
            stock_compare = inv.groupby("sku_id").agg(quantity=("quantity_on_hand", "sum"), reorder=("reorder_level", lambda s: s.sum(min_count=1))).reset_index().dropna(subset=["reorder"])
            if not stock_compare.empty:
                stock_compare = stock_compare.sort_values("quantity").head(18)
                fig = go.Figure()
                fig.add_trace(go.Bar(x=stock_compare["sku_id"], y=stock_compare["quantity"], name="On hand", marker_color=PALETTE["blue"]))
                fig.add_trace(go.Scatter(x=stock_compare["sku_id"], y=stock_compare["reorder"], name="Reorder level", mode="markers", marker=dict(color=PALETTE["amber"], size=9)))
                fig.update_layout(barmode="group", xaxis_title="", yaxis_title="Units")
                st.plotly_chart(dark_chart(fig, 300), use_container_width=True)
            else: chart_empty("Reorder levels are not available in this upload.")

        section("SKU inventory register", "FILTERED DETAIL")
        table_cols = [c for c in ["sku_id", "product_name", "warehouse_id", "category", "quantity_on_hand", "reorder_level", "unit_cost", "inventory_value", "last_movement_date", "days_since_movement", "stock_status"] if c in inv.columns]
        table = inv[table_cols].copy().sort_values("inventory_value", ascending=False, na_position="last")
        st.dataframe(table, use_container_width=True, hide_index=True, height=390)
        show_csv_download("Download filtered inventory", table, "filtered_inventory.csv", "dl_inv")
    else: st.info("No inventory records match the current filter selection.")
    st.caption("ABC method: SKUs are sorted by inventory value; class A covers cumulative value through 80%, B the next 15% through 95%, and C the remainder. This is a conventional configurable method, not a universal standard.")

elif page == "Warehouse Map":
    section("Warehouse map · digital twin lite", "03 / STORAGE FOOTPRINT")
    st.caption("Rack layout by zone, with occupancy and inventory details.")
    if racks_filtered.empty:
        st.info("Rack-level capacity is not available. For an uploaded CSV, map Rack / bin and Rack capacity to enable this view.")
    else:
        wh_choices = sorted(racks_filtered["warehouse_id"].dropna().astype(str).unique().tolist())
        selected_wh = st.selectbox("Select warehouse", wh_choices, key="map_wh")
        rack_wh = racks_filtered[racks_filtered["warehouse_id"].astype(str).eq(selected_wh)].copy()
        rack_wh = rack_wh.sort_values(["zone_id", "rack_id"]).reset_index(drop=True)
        rack_wh["x"] = np.arange(len(rack_wh)) % 10
        rack_wh["y"] = -(np.arange(len(rack_wh)) // 10)
        selected_rack = st.selectbox("Select rack for detail", rack_wh["rack_id"].tolist(), key=f"map_rack_{selected_wh}")
        colors = {"Empty": "#64748b", "Healthy": PALETTE["green"], "High": PALETTE["amber"], "Critical": PALETTE["red"]}
        rack_wh["color"] = rack_wh.apply(lambda r: PALETTE["blue"] if r["rack_id"] == selected_rack else colors.get(r["rack_status"], "#64748b"), axis=1)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=rack_wh["x"], y=rack_wh["y"], mode="markers+text",
            marker=dict(size=28, color=rack_wh["color"], line=dict(color="#dbeafe", width=1), symbol="square"),
            text=rack_wh["rack_id"].str.split("-").str[-1], textposition="middle center",
            textfont=dict(size=9, color="#06111f"),
            customdata=rack_wh[["rack_id", "zone_id", "occupied_units", "capacity_units", "utilization_pct", "rack_status"]],
            hovertemplate="Rack %{customdata[0]}<br>Zone %{customdata[1]}<br>Occupied %{customdata[2]:,.0f}<br>Capacity %{customdata[3]:,.0f}<br>Utilization %{customdata[4]:.1f}%<br>Status %{customdata[5]}<extra></extra>"
        ))
        fig.update_layout(showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False), height=480, margin=dict(l=10,r=10,t=20,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,23,39,.55)")
        fig.update_xaxes(range=[-.8, 9.8])
        fig.update_yaxes(scaleanchor="x", scaleratio=1)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("<span class='pill'>BLUE · SELECTED</span> &nbsp; <span style='color:#35c48b'>●</span> Healthy &nbsp; <span style='color:#f5b942'>●</span> High &nbsp; <span style='color:#f36b74'>●</span> Critical &nbsp; <span style='color:#64748b'>●</span> Empty", unsafe_allow_html=True)
        picked = rack_wh[rack_wh["rack_id"].eq(selected_rack)].iloc[0]
        rack_inv = inv[(inv["warehouse_id"].astype(str).eq(selected_wh)) & (inv["rack_id"].astype(str).eq(selected_rack))]
        products_stored = ", ".join(rack_inv["sku_id"].astype(str).unique().tolist()[:8]) or "None"
        rack_value = rack_inv["inventory_value"].sum(min_count=1)
        metric_row([
            ("Rack ID", str(picked["rack_id"]), None), ("Zone", str(picked["zone_id"]), None),
            ("Capacity", number(picked["capacity_units"]), None), ("Occupied", number(picked["occupied_units"]), None),
            ("Available", number(picked["available_units"]), None), ("Occupancy", pct(picked["utilization_pct"]), None),
        ])
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"<div class='insight'><b>Rack status</b><br>{picked['rack_status']}<br><span class='small-note'>Inventory value: {money(rack_value)}</span></div><div class='insight'><b>Products stored</b><br><span class='small-note'>{products_stored}</span></div>", unsafe_allow_html=True)
        with c2:
            section("Rack-level inventory", "SELECTED LOCATION")
            st.dataframe(rack_inv[[c for c in ["sku_id", "product_name", "category", "quantity_on_hand", "unit_cost", "inventory_value", "stock_status"] if c in rack_inv.columns]], use_container_width=True, hide_index=True)
        section("Rack register", "WAREHOUSE LAYOUT DATA")
        st.dataframe(rack_wh[["rack_id", "zone_id", "capacity_units", "occupied_units", "available_units", "utilization_pct", "rack_status"]], use_container_width=True, hide_index=True, height=300)

elif page == "Inbound Operations":
    section("Inbound operations", "04 / RECEIVING PERFORMANCE")
    inbound = ops["inbound"].copy()
    if inbound.empty:
        st.info("Not available in uploaded data. This module requires an Inbound CSV or the demo dataset.")
    else:
        inbound["expected_date"] = pd.to_datetime(inbound["expected_date"], errors="coerce")
        inbound["received_date"] = pd.to_datetime(inbound["received_date"], errors="coerce")
        expected_units = inbound["units_expected"].sum()
        received_units = inbound["units_received"].sum()
        completion = received_units / expected_units * 100 if expected_units else np.nan
        pending = inbound["receipt_status"].isin(["PENDING", "PARTIAL"]).sum()
        delay = (inbound.loc[inbound["received_date"].notna(), "received_date"] - inbound.loc[inbound["received_date"].notna(), "expected_date"]).dt.days
        avg_delay = delay.mean() if not delay.empty else np.nan
        metric_row([("Total receipts", number(len(inbound)), None), ("Units expected", number(expected_units), None), ("Units received", number(received_units), None), ("Receiving completion", pct(completion), None), ("Pending / partial", number(pending), None), ("Avg. receiving delay", f"{avg_delay:.1f} days" if pd.notna(avg_delay) else "—", None)])
        c1, c2 = st.columns(2)
        with c1:
            section("Expected vs received", "SUPPLIER RECEIPTS")
            by_supplier = inbound.groupby("supplier_name")[ ["units_expected", "units_received"] ].sum().reset_index().sort_values("units_expected", ascending=False).head(10)
            fig = px.bar(by_supplier, x="supplier_name", y=["units_expected", "units_received"], barmode="group")
            fig.update_layout(xaxis_title="", yaxis_title="Units", legend_title="")
            st.plotly_chart(dark_chart(fig, 320), use_container_width=True)
        with c2:
            section("Receipt status", "WORK QUEUE")
            status = inbound["receipt_status"].value_counts().rename_axis("status").reset_index(name="receipts")
            fig = px.pie(status, names="status", values="receipts", hole=.58)
            st.plotly_chart(dark_chart(fig, 320), use_container_width=True)
        c3, c4 = st.columns(2)
        with c3:
            section("Daily inbound received", "TREND")
            trend = inbound.groupby("expected_date")["units_received"].sum().reset_index()
            fig = px.area(trend, x="expected_date", y="units_received")
            fig.update_layout(xaxis_title="", yaxis_title="Units received")
            st.plotly_chart(dark_chart(fig, 280), use_container_width=True)
        with c4:
            section("Inspection status", "QUALITY GATE")
            q = inbound["inspection_status"].value_counts().rename_axis("inspection_status").reset_index(name="receipts")
            fig = px.bar(q, x="inspection_status", y="receipts", color="inspection_status")
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Receipts")
            st.plotly_chart(dark_chart(fig, 280), use_container_width=True)
        section("Inbound receipt register", "FILTERED DETAIL")
        st.dataframe(inbound[["receipt_id", "supplier_name", "warehouse_id", "expected_date", "received_date", "units_expected", "units_received", "receipt_status", "inspection_status"]], use_container_width=True, hide_index=True, height=340)
        show_csv_download("Download inbound register", inbound, "inbound_register.csv", "dl_inbound")

elif page == "Outbound Operations":
    section("Outbound operations", "05 / ORDER FULFILMENT")
    outbound = ops["outbound"].copy()
    if outbound.empty:
        st.info("Not available in uploaded data. This module requires an Outbound CSV or the demo dataset.")
        st.caption("OTIF is not reported because promised delivery dates and actual delivery dates are not part of the current data model.")
    else:
        total_orders = len(outbound)
        dispatched = outbound["order_status"].eq("DISPATCHED").sum()
        pending = outbound["order_status"].isin(["PENDING", "PICKING"]).sum()
        ordered = outbound["units_ordered"].sum()
        dispatched_units = outbound["units_dispatched"].sum()
        fulfilment = dispatched_units / ordered * 100 if ordered else np.nan
        avg_pick = outbound["picking_duration_minutes"].mean()
        metric_row([("Total orders", number(total_orders), None), ("Orders dispatched", number(dispatched), None), ("Pending orders", number(pending), None), ("Units ordered", number(ordered), None), ("Units dispatched", number(dispatched_units), None), ("Fulfilment rate", pct(fulfilment), None)])
        st.metric("Average picking duration", f"{avg_pick:.1f} min" if pd.notna(avg_pick) else "—")
        c1, c2 = st.columns(2)
        with c1:
            section("Orders by status", "ORDER WORKFLOW")
            status = outbound["order_status"].value_counts().rename_axis("status").reset_index(name="orders")
            fig = px.pie(status, names="status", values="orders", hole=.58)
            st.plotly_chart(dark_chart(fig, 300), use_container_width=True)
        with c2:
            section("Ordered vs dispatched units", "VOLUME")
            wh_order = outbound.groupby("warehouse_id")[["units_ordered", "units_dispatched"]].sum().reset_index()
            fig = px.bar(wh_order, x="warehouse_id", y=["units_ordered", "units_dispatched"], barmode="group")
            fig.update_layout(xaxis_title="", yaxis_title="Units", legend_title="")
            st.plotly_chart(dark_chart(fig, 300), use_container_width=True)
        c3, c4 = st.columns(2)
        with c3:
            section("Daily dispatch trend", "DISPATCHED UNITS")
            dispatch = outbound.dropna(subset=["dispatch_date"]).groupby("dispatch_date")["units_dispatched"].sum().reset_index()
            if not dispatch.empty:
                fig = px.line(dispatch, x="dispatch_date", y="units_dispatched", markers=True)
                st.plotly_chart(dark_chart(fig, 280), use_container_width=True)
            else: chart_empty("No dispatch dates are available in this filter range.")
        with c4:
            section("Picking duration distribution", "PROCESS TIME")
            pick = outbound.dropna(subset=["picking_duration_minutes"])
            if not pick.empty:
                fig = px.histogram(pick, x="picking_duration_minutes", nbins=18)
                fig.update_layout(xaxis_title="Minutes", yaxis_title="Orders")
                st.plotly_chart(dark_chart(fig, 280), use_container_width=True)
            else: chart_empty("Picking duration is not available.")
        section("Outbound order register", "FILTERED DETAIL")
        st.dataframe(outbound[["order_id", "warehouse_id", "order_date", "dispatch_date", "units_ordered", "units_picked", "units_dispatched", "order_status", "picking_duration_minutes"]], use_container_width=True, hide_index=True, height=340)
        show_csv_download("Download outbound register", outbound, "outbound_register.csv", "dl_outbound")
        st.caption("OTIF requires promised and actual delivery dates.")

elif page == "Workforce & Equipment":
    section("Workforce & equipment", "08 / OPERATIONS")
    st.caption("Choose a workflow to view equipment movement and task activity.")
    scenario = st.selectbox("Simulation scenario", ["Receiving to storage", "Replenishment transfer", "Picking to dispatch"], key="equipment_scenario")
    speed = st.select_slider("Simulation speed", options=["0.5×", "1×", "2×", "4×"], value="1×", key="equipment_speed")
    st.session_state.setdefault("equipment_running", False)
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("▶ Play simulation", use_container_width=True, key="equipment_play"):
            st.session_state["equipment_running"] = True
    with c2:
        if st.button("Ⅱ Pause", use_container_width=True, key="equipment_pause"):
            st.session_state["equipment_running"] = False
    with c3:
        st.metric("Scenario state", "RUNNING" if st.session_state["equipment_running"] else "PAUSED")
    equipment = pd.DataFrame([
        {"equipment_id":"FLT-01","type":"Forklift","zone":"RECEIVING → BULK","status":"Active" if st.session_state["equipment_running"] else "Idle","utilization_pct":68,"scenario":scenario},
        {"equipment_id":"FLT-02","type":"Forklift","zone":"PICK-FACE → PACKING","status":"Active" if st.session_state["equipment_running"] and scenario == "Picking to dispatch" else "Standby","utilization_pct":54,"scenario":scenario},
        {"equipment_id":"AGV-01","type":"AGV","zone":"BULK → DISPATCH","status":"Active" if st.session_state["equipment_running"] and scenario == "Replenishment transfer" else "Standby","utilization_pct":37,"scenario":scenario},
    ])
    metric_row([("Equipment", "3", None), ("Scenario", scenario, None), ("Playback speed", speed, None), ("Task state", "Running" if st.session_state["equipment_running"] else "Paused", None)])
    st.dataframe(equipment, use_container_width=True, hide_index=True)
    events = pd.DataFrame([
        {"event_time":"00:00","equipment_id":"FLT-01","from":"Receiving dock","to":"Bulk zone","movement":"Put-away","status":"In progress" if st.session_state["equipment_running"] else "Paused"},
        {"event_time":"00:18","equipment_id":"AGV-01","from":"Bulk zone","to":"Dispatch staging","movement":"Pallet transfer","status":"Queued"},
        {"event_time":"00:34","equipment_id":"FLT-02","from":"Pick-face","to":"Packing","movement":"Picked pallet","status":"Queued"},
    ])
    st.markdown("**Activity timeline**")
    st.dataframe(events, use_container_width=True, hide_index=True)
    st.caption("Playback controls update the demonstration state and event labels. The standalone digital-twin scene also provides a procedural forklift animation when its 3D renderer is available.")

elif page == "Space Optimization":
    section("Space optimization", "09 / CAPACITY INTELLIGENCE")
    if racks_filtered.empty:
        st.info("Space optimization requires mapped rack capacity. Upload rack/bin and capacity columns to enable this analysis.")
    else:
        threshold = st.slider("High-utilization threshold", 70, 99, 85, key="space_threshold")
        rack_space = racks_filtered.copy()
        total_cap = rack_space["capacity_units"].sum()
        occupied = rack_space["occupied_units"].sum()
        empty_count = int(rack_space["rack_status"].eq("Empty").sum())
        high_count = int(rack_space["utilization_pct"].ge(threshold).sum())
        metric_row([("Total capacity", number(total_cap), None), ("Occupied units", number(occupied), None), ("Available units", number(max(0, total_cap-occupied)), None), ("Utilization", pct(occupied/total_cap*100 if total_cap else np.nan), None), ("Empty racks", number(empty_count), None), (f"Racks ≥ {threshold}%", number(high_count), None)])
        c1, c2 = st.columns(2)
        with c1:
            section("Rack utilization ranking", "CAPACITY HEATMAP INPUT")
            fig = px.bar(rack_space.sort_values("utilization_pct", ascending=False).head(20), x="rack_id", y="utilization_pct", color="utilization_pct", range_y=[0, 110], hover_data=["warehouse_id", "zone_id", "rack_status"])
            fig.update_layout(xaxis_title="Rack", yaxis_title="Utilization %")
            st.plotly_chart(dark_chart(fig, 330), use_container_width=True)
        with c2:
            section("Utilization distribution", "RACK COUNT")
            fig = px.histogram(rack_space, x="utilization_pct", nbins=12)
            fig.update_layout(xaxis_title="Utilization %", yaxis_title="Racks")
            st.plotly_chart(dark_chart(fig, 330), use_container_width=True)
        high = rack_space[rack_space["utilization_pct"].ge(threshold)].copy()
        spare = rack_space[rack_space["utilization_pct"].lt(50) & rack_space["available_units"].gt(0)].copy()
        st.markdown("**Candidate review queue**")
        if not high.empty and not spare.empty:
            candidates = high[["rack_id", "warehouse_id", "zone_id", "occupied_units", "capacity_units", "utilization_pct"]].head(10).copy()
            candidates["candidate_spare_racks"] = ", ".join(spare.sort_values("utilization_pct")["rack_id"].astype(str).head(3).tolist())
            candidates["review_note"] = "Validate SKU compatibility, handling rules and travel distance before any move."
            st.dataframe(candidates, use_container_width=True, hide_index=True)
        else:
            st.info("No high-pressure / low-utilization candidate pair was found in the current filtered data. No relocation is proposed.")
        st.caption("Relocation candidates are analytical prompts only. No stock movement is executed or recorded.")

elif page == "Risk & Exceptions":
    section("Risk & exception center", "06 / PRIORITIZED ACTION QUEUE")
    pending_days = st.slider("Pending outbound threshold (days)", 1, 14, 3, key="risk_pending_days")
    alerts = build_alerts(inv, racks_filtered, ops.get("inbound", pd.DataFrame()), ops.get("outbound", pd.DataFrame()), pending_days)
    if alerts.empty:
        st.success("No rule-based exceptions were generated from the current filtered dataset.")
    else:
        metric_row([
            ("Open exceptions", number(len(alerts)), None),
            ("Critical", number(alerts["severity"].eq("Critical").sum()), None),
            ("High", number(alerts["severity"].eq("High").sum()), None),
            ("Medium", number(alerts["severity"].eq("Medium").sum()), None),
        ])
        a1, a2, a3 = st.columns(3)
        severities = ["Critical", "High", "Medium", "Low"]
        selected_sev = a1.multiselect("Severity", severities, default=severities, key="risk_sev")
        types = sorted(alerts["alert_type"].unique().tolist())
        selected_types = a2.multiselect("Alert type", types, default=types, key="risk_type")
        statuses = sorted(alerts["status"].unique().tolist())
        selected_status = a3.multiselect("Status", statuses, default=statuses, key="risk_status")
        filtered_alerts = alerts[alerts["severity"].isin(selected_sev) & alerts["alert_type"].isin(selected_types) & alerts["status"].isin(selected_status)]
        color_map = {"Critical": "#f36b74", "High": "#f59e0b", "Medium": "#60a5fa", "Low": "#94a3b8"}
        fig = px.bar(filtered_alerts["severity"].value_counts().reindex(severities, fill_value=0).rename_axis("severity").reset_index(name="count"), x="severity", y="count", color="severity", color_discrete_map=color_map)
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Exceptions")
        st.plotly_chart(dark_chart(fig, 240), use_container_width=True)
        st.dataframe(filtered_alerts.sort_values("severity", key=lambda s: s.map({"Critical": 0, "High": 1, "Medium": 2, "Low": 3})), use_container_width=True, hide_index=True, height=390)
        show_csv_download("Download alert register", filtered_alerts, "warehouse_alert_register.csv", "dl_alerts")
    st.markdown("---")
    section("In-app automation demo", "GENERATE & EXPORT")
    st.caption("These actions run only when clicked. No email, webhook or external workflow is implied.")
    a, b = st.columns(2)
    with a:
        if st.button("Generate current alert snapshot", use_container_width=True):
            st.session_state["last_alert_snapshot"] = {"timestamp": datetime.now().isoformat(timespec="seconds"), "count": int(len(alerts))}
        snapshot = st.session_state.get("last_alert_snapshot")
        if snapshot:
            st.success(f"Snapshot recorded at {snapshot['timestamp']} · {snapshot['count']} alert(s)")
    with b:
        if st.button("Build daily warehouse summary", use_container_width=True):
            wh_for_report = warehouse_summary(inv, model)
            report = {
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "data_mode": "DEMO DATA" if is_demo else "UPLOADED CSV",
                "inventory_units": int(inventory_units), "inventory_value": None if pd.isna(inventory_value) else float(inventory_value),
                "active_skus": int(active_skus), "low_stock_skus": int(low_stock), "alerts": int(len(alerts)),
                "warehouses": wh_for_report.to_dict(orient="records"),
            }
            st.session_state["daily_report"] = report
        report = st.session_state.get("daily_report")
        if report:
            st.success(f"Report generated at {report['generated_at']}")
            st.download_button("Download daily summary JSON", json.dumps(report, indent=2, default=str), file_name="daily_warehouse_summary.json", mime="application/json", use_container_width=True)
    with st.expander("Optional n8n webhook (manual send only)"):
        webhook = st.text_input("Webhook URL", type="password", placeholder="https://…", key="n8n_webhook")
        if st.button("Send test alert payload", key="send_webhook"):
            if not webhook.strip():
                st.error("Enter a webhook URL first.")
            else:
                payload = {"event": "warehouse_alert_snapshot", "generated_at": datetime.now().isoformat(timespec="seconds"), "alert_count": int(len(alerts)), "severity_counts": alerts["severity"].value_counts().to_dict() if not alerts.empty else {}, "data_mode": "demo" if is_demo else "uploaded_csv"}
                try:
                    req = urllib.request.Request(webhook.strip(), data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
                    with urllib.request.urlopen(req, timeout=8) as response:
                        st.success(f"Webhook responded with HTTP {response.status}.")
                except Exception as exc:
                    st.error(f"Webhook request failed: {exc}")

elif page == "Insights & Recommendations":
    section("Warehouse insights", "07 / DECISION SUPPORT")
    st.caption("Insights are based on current inventory, warehouse capacity and movement metrics.")
    insights = []
    if not wh_summary.empty:
        top_val = wh_summary.sort_values("inventory_value", ascending=False, na_position="last").iloc[0]
        if pd.notna(top_val["inventory_value"]): insights.append(f"**Value concentration:** {top_val['warehouse_name']} holds the highest inventory value in the current filter ({money(top_val['inventory_value'])}).")
        cap = wh_summary.dropna(subset=["capacity_utilization_pct"])
        if not cap.empty:
            top_cap = cap.sort_values("capacity_utilization_pct", ascending=False).iloc[0]
            insights.append(f"**Space pressure:** {top_cap['warehouse_name']} has the highest calculated capacity utilization at {pct(top_cap['capacity_utilization_pct'])}.")
    if low_stock:
        insights.append(f"**Replenishment focus:** {low_stock:,} distinct SKU(s) are at or below reorder level. Prioritize critical and out-of-stock lines first.")
    if pd.notna(dead_value) and dead_value > 0:
        insights.append(f"**Ageing exposure:** {money(dead_value)} of inventory value has no movement recorded for more than 90 days. Validate whether demand has shifted before replenishing these items.")
    if not racks_filtered.empty and racks_filtered["utilization_pct"].ge(90).any():
        count = int(racks_filtered["utilization_pct"].ge(90).sum())
        insights.append(f"**Storage constraint:** {count} rack(s) are at or above 90% occupancy. Review slotting and relocation opportunities.")
    if not ops["inbound"].empty:
        idf = ops["inbound"]
        pending_in = int(idf["receipt_status"].isin(["PENDING", "PARTIAL"]).sum())
        insights.append(f"**Receiving queue:** {pending_in} receipt(s) are pending or partial in the selected date window.")
    if not ops["outbound"].empty:
        odf = ops["outbound"]
        pending_out = int(odf["order_status"].isin(["PENDING", "PICKING"]).sum())
        insights.append(f"**Fulfilment queue:** {pending_out} order(s) remain pending or in picking in the selected date window.")
    if not insights: insights.append("The current dataset does not contain enough fields to generate operational recommendations. Add cost, movement date, reorder, capacity or operational data to unlock more insights.")
    for text in insights: st.markdown(f"<div class='insight'>{text}</div>", unsafe_allow_html=True)
    section("Ask using the current data", "SUGGESTED QUESTIONS")
    questions = ["Which warehouse has the highest inventory value?", "Which SKUs are below reorder level?", "Which products have not moved for 90 days?", "Which racks have the highest utilization?", "What are the biggest warehouse risks?", "Summarize current warehouse performance."]
    for q in questions:
        with st.expander(q):
            if "highest inventory value" in q.lower():
                if not wh_summary.empty and wh_summary["inventory_value"].notna().any():
                    r = wh_summary.sort_values("inventory_value", ascending=False).iloc[0]
                    st.write(f"{r['warehouse_name']} — {money(r['inventory_value'])}.")
                else: chart_empty("Inventory value is unavailable.")
            elif "below reorder" in q.lower():
                low = inv[inv["stock_status"].isin(["Critical", "Low Stock", "Out of Stock"])][["sku_id", "warehouse_id", "quantity_on_hand", "reorder_level", "stock_status"]]
                st.dataframe(low.head(50), use_container_width=True, hide_index=True)
            elif "90 days" in q.lower():
                old = inv[inv["days_since_movement"].gt(90)][["sku_id", "warehouse_id", "quantity_on_hand", "days_since_movement", "inventory_value"]]
                st.dataframe(old.head(50), use_container_width=True, hide_index=True)
            elif "racks" in q.lower():
                if not racks_filtered.empty: st.dataframe(racks_filtered.sort_values("utilization_pct", ascending=False).head(20), use_container_width=True, hide_index=True)
                else: chart_empty("Rack capacity is not available.")
            elif "risks" in q.lower():
                st.dataframe(alerts.head(50), use_container_width=True, hide_index=True) if not alerts.empty else st.write("No exceptions were generated from available fields.")
            else:
                st.write(f"Current filtered inventory: {number(inventory_units)} units across {number(active_skus)} SKUs; inventory value {money(inventory_value)}; {number(low_stock)} SKU(s) require stock attention; {number(len(alerts))} rule-based exceptions.")
    with st.expander("Connect an LLM assistant"):
        st.info("The current insights are generated from warehouse metrics and business rules. An external LLM can be connected later through environment variables or Streamlit secrets.")

elif page == "Automation Center":
    section("Automation center", "12 / APPROVAL-GATED WORKFLOWS")
    st.caption("Choose a workflow to generate a report or alert from the current data.")
    st.session_state.setdefault("automation_log", [])
    action = st.selectbox("Workflow", ["Generate low-stock alert snapshot", "Generate ageing inventory report", "Generate overcapacity report", "Build daily warehouse summary"], key="automation_action")
    if st.button("Run selected workflow", type="primary", key="run_automation"):
        now = datetime.now().isoformat(timespec="seconds")
        if action == "Generate low-stock alert snapshot":
            result_df = inv[inv["stock_status"].isin(["Critical", "Low Stock", "Out of Stock"])].copy()
            filename = "low_stock_alerts.csv"
        elif action == "Generate ageing inventory report":
            result_df = inv[inv["days_since_movement"].gt(90)].copy()
            filename = "ageing_inventory.csv"
        elif action == "Generate overcapacity report":
            result_df = racks_filtered[racks_filtered["utilization_pct"].ge(90)].copy()
            filename = "overcapacity_racks.csv"
        else:
            result_df = warehouse_summary(inv, model)
            filename = "daily_warehouse_summary.csv"
        st.session_state["automation_last_result"] = {"timestamp": now, "workflow": action, "rows": int(len(result_df)), "filename": filename, "csv": result_df.to_csv(index=False)}
        st.session_state["automation_log"].insert(0, {"timestamp": now, "workflow": action, "status": "Completed locally", "records": int(len(result_df)), "data_mode": "DEMO DATA" if is_demo else "UPLOADED CSV"})
    latest = st.session_state.get("automation_last_result")
    if latest:
        st.success(f"{latest['workflow']} generated {latest['rows']:,} row(s) at {latest['timestamp']}.")
        st.download_button("Download workflow output", latest["csv"].encode("utf-8-sig"), file_name=latest["filename"], mime="text/csv", use_container_width=True)
    st.markdown("**Workflow execution log**")
    if st.session_state["automation_log"]:
        st.dataframe(pd.DataFrame(st.session_state["automation_log"]), use_container_width=True, hide_index=True)
    else:
        st.info("No workflow has been run in this session.")
    with st.expander("Webhook integration"):
        webhook = st.text_input("Webhook URL", type="password", key="automation_webhook_url", placeholder="https://…")
        if st.button("Send current summary to webhook", key="automation_webhook_send"):
            if not webhook.strip():
                st.error("Enter a webhook URL first.")
            else:
                payload = {"event":"warehouse_summary_manual", "generated_at":datetime.now().isoformat(timespec="seconds"), "inventory_units":int(inventory_units), "inventory_value":None if pd.isna(inventory_value) else float(inventory_value), "low_stock_skus":int(low_stock), "open_exceptions":int(len(alerts)), "data_mode":"demo" if is_demo else "uploaded_csv"}
                try:
                    req = urllib.request.Request(webhook.strip(), data=json.dumps(payload).encode("utf-8"), headers={"Content-Type":"application/json"}, method="POST")
                    with urllib.request.urlopen(req, timeout=8) as response:
                        st.success(f"Webhook responded with HTTP {response.status}.")
                except Exception as exc:
                    st.error(f"Webhook request failed: {exc}")

elif page == "Settings":
    section("Settings", "14 / CONFIGURATION")
    metric_row([("Active source", "DEMO" if is_demo else "CSV UPLOAD", None), ("Inventory rows", number(len(inv_all)), None), ("Warehouses in scope", number(inv["warehouse_id"].nunique()), None), ("Last refresh", datetime.now().strftime("%H:%M:%S"), None)])
    st.markdown("**Data source**")
    st.write("Demo dataset" if is_demo else f"Uploaded file: {st.session_state.get('upload_filename', 'inventory.csv')}")
    st.markdown("**Available integrations**")
    st.write("- Insights: built-in warehouse rules")
    st.write("- Database: PostgreSQL reference schema in `database/schema.sql`")
    st.write("- Automation: manual webhook option in Automation Center")
    st.write("- Power BI: model notes and DAX measures in `powerbi/`")
    st.markdown("**KPI definitions**")
    with st.expander("View key KPI formulas"):
        st.markdown("""- Inventory value = quantity on hand × unit cost (or source-provided inventory value).
- Capacity utilization = occupied units ÷ capacity × 100.
- Low stock = distinct SKU at/below reorder level.
- Ageing = days since last movement, not purchase age.
- Receiving completion = units received ÷ units expected × 100.
- Fulfilment = units dispatched ÷ units ordered × 100.""")

elif page == "Data Explorer":
    section("Data explorer", "08 / DATA & QUALITY")
    st.markdown(f"<div class='insight'><b>Active data source</b><br>{'Demo dataset' if is_demo else 'Uploaded CSV'}<br><span class='small-note'>{'Built-in sample data' if is_demo else st.session_state.get('upload_filename', 'inventory.csv')}</span></div>", unsafe_allow_html=True)
    if quality_info:
        metric_row([("Source rows", number(quality_info["rows"]), None), ("Source columns", number(quality_info["columns"]), None), ("Missing cells", number(quality_info["missing_cells"]), None), ("Duplicate rows", number(quality_info["duplicate_rows"]), None)])
        st.write(f"Invalid quantity values: **{quality_info['invalid_quantity_values']}** · Missing quantity values treated as zero for calculations: **{quality_info['missing_quantity_values']}**")
        if quality_info["unmapped_columns"]: st.caption("Unmapped source columns (retained in the original upload, not used by this MVP): " + ", ".join(map(str, quality_info["unmapped_columns"])))
    else:
        metric_row([("Inventory records", number(len(model["inventory"])), None), ("Product records", number(len(model["products"])), None), ("Rack records", number(len(model["racks"])), None), ("Movement records", number(len(model["movements"])), None)])
    if not is_demo:
        st.info("This file contains inventory data. Add receipt, order or movement files to enable the related operational analysis.")
    tabs = st.tabs(["Inventory sample", "Column profile", "Data quality", "Downloads"])
    with tabs[0]:
        st.dataframe(inv_all.head(100), use_container_width=True, hide_index=True, height=400)
    with tabs[1]:
        profile = pd.DataFrame({"column": inv_all.columns, "dtype": [str(inv_all[c].dtype) for c in inv_all.columns], "missing": [int(inv_all[c].isna().sum()) for c in inv_all.columns], "unique": [int(inv_all[c].nunique(dropna=True)) for c in inv_all.columns]})
        st.dataframe(profile, use_container_width=True, hide_index=True)
    with tabs[2]:
        if quality_info:
            issues = []
            if quality_info["missing_cells"]: issues.append(f"{quality_info['missing_cells']} missing source cells detected.")
            if quality_info["duplicate_rows"]: issues.append(f"{quality_info['duplicate_rows']} duplicate row(s) detected in the original CSV.")
            if quality_info["invalid_quantity_values"]: issues.append(f"{quality_info['invalid_quantity_values']} non-numeric quantity value(s) were converted to zero for calculations.")
            if quality_info["missing_quantity_values"]: issues.append(f"{quality_info['missing_quantity_values']} quantity value(s) were missing and set to zero for calculations.")
            if inv_all["unit_cost"].isna().all() and inv_all["inventory_value"].isna().all(): issues.append("Inventory valuation is unavailable: map Unit cost or Inventory value.")
            if inv_all["last_movement_date"].isna().all(): issues.append("Ageing analysis is unavailable: map Last movement date.")
            if inv_all["reorder_level"].isna().all(): issues.append("Stock status / low-stock analysis is unavailable: map Reorder level.")
            if not model["racks"].empty and model["racks"]["capacity_units"].isna().all(): issues.append("Rack capacity is unavailable.")
            if issues:
                for issue in issues: st.warning(issue)
            else: st.success("No major mapping or quality issues were detected by the MVP checks.")
        else:
            st.success("Demo dataset generated with internally linked warehouse, zone, rack, product, inventory and operations records.")
        invalid_negative = int(inv_all["quantity_on_hand"].lt(0).sum())
        if invalid_negative: st.error(f"Negative stock quantities: {invalid_negative} row(s). Review before using operationally.")
        else: st.success("No negative stock quantities detected.")
    with tabs[3]:
        sku_export = sku_summary(inv)
        wh_export = warehouse_summary(inv, model)
        c1, c2 = st.columns(2)
        with c1:
            show_csv_download("Filtered inventory CSV", inv, "filtered_inventory.csv", "expl_inv")
            show_csv_download("SKU summary CSV", sku_export, "sku_summary.csv", "expl_sku")
        with c2:
            show_csv_download("Warehouse summary CSV", wh_export, "warehouse_summary.csv", "expl_wh")
            show_csv_download("Alert register CSV", alerts, "alert_register.csv", "expl_alerts")


