-- Reference PostgreSQL schema only. This file is NOT executed by the app.
-- Review and back up any target database before applying a schema.
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id TEXT PRIMARY KEY,
    warehouse_name TEXT NOT NULL,
    city TEXT,
    region TEXT,
    total_capacity_units NUMERIC(18,2),
    warehouse_type TEXT
);
CREATE TABLE IF NOT EXISTS zones (
    zone_id TEXT PRIMARY KEY,
    warehouse_id TEXT NOT NULL REFERENCES warehouses(warehouse_id),
    zone_name TEXT NOT NULL,
    zone_type TEXT
);
CREATE TABLE IF NOT EXISTS racks (
    rack_id TEXT PRIMARY KEY,
    warehouse_id TEXT NOT NULL REFERENCES warehouses(warehouse_id),
    zone_id TEXT REFERENCES zones(zone_id),
    rack_name TEXT,
    capacity_units NUMERIC(18,2) CHECK (capacity_units IS NULL OR capacity_units >= 0)
);
CREATE INDEX IF NOT EXISTS ix_racks_wh_zone ON racks(warehouse_id, zone_id);
CREATE TABLE IF NOT EXISTS products (
    sku_id TEXT PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    unit_cost NUMERIC(18,2),
    unit_price NUMERIC(18,2)
);
CREATE TABLE IF NOT EXISTS inventory_snapshot (
    inventory_id TEXT PRIMARY KEY,
    snapshot_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    warehouse_id TEXT NOT NULL REFERENCES warehouses(warehouse_id),
    zone_id TEXT REFERENCES zones(zone_id),
    rack_id TEXT REFERENCES racks(rack_id),
    sku_id TEXT NOT NULL REFERENCES products(sku_id),
    quantity_on_hand NUMERIC(18,2) NOT NULL,
    reorder_level NUMERIC(18,2),
    safety_stock NUMERIC(18,2),
    last_movement_date DATE,
    lot_status TEXT
);
CREATE INDEX IF NOT EXISTS ix_inventory_wh_sku ON inventory_snapshot(warehouse_id, sku_id);
CREATE INDEX IF NOT EXISTS ix_inventory_rack ON inventory_snapshot(rack_id);
CREATE TABLE IF NOT EXISTS inventory_movements (
    movement_id TEXT PRIMARY KEY,
    movement_date TIMESTAMPTZ NOT NULL,
    warehouse_id TEXT NOT NULL REFERENCES warehouses(warehouse_id),
    sku_id TEXT NOT NULL REFERENCES products(sku_id),
    rack_id TEXT REFERENCES racks(rack_id),
    movement_type TEXT NOT NULL,
    quantity NUMERIC(18,2) NOT NULL,
    reference_id TEXT
);
CREATE INDEX IF NOT EXISTS ix_movements_wh_date ON inventory_movements(warehouse_id, movement_date);
CREATE TABLE IF NOT EXISTS inbound_receipts (
    receipt_id TEXT PRIMARY KEY,
    warehouse_id TEXT NOT NULL REFERENCES warehouses(warehouse_id),
    supplier_name TEXT,
    expected_date DATE,
    received_date DATE,
    units_expected NUMERIC(18,2),
    units_received NUMERIC(18,2),
    inspection_status TEXT,
    receipt_status TEXT
);
CREATE TABLE IF NOT EXISTS outbound_orders (
    order_id TEXT PRIMARY KEY,
    warehouse_id TEXT NOT NULL REFERENCES warehouses(warehouse_id),
    order_date DATE,
    dispatch_date DATE,
    customer_region TEXT,
    units_ordered NUMERIC(18,2),
    units_picked NUMERIC(18,2),
    units_dispatched NUMERIC(18,2),
    order_status TEXT,
    picking_duration_minutes NUMERIC(10,2)
);
CREATE TABLE IF NOT EXISTS warehouse_alerts (
    alert_id BIGSERIAL PRIMARY KEY,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    warehouse_id TEXT REFERENCES warehouses(warehouse_id),
    related_item TEXT,
    event_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    explanation TEXT,
    recommended_action TEXT,
    status TEXT NOT NULL DEFAULT 'Open',
    resolution_note TEXT
);
CREATE INDEX IF NOT EXISTS ix_alerts_status_severity ON warehouse_alerts(status, severity);
