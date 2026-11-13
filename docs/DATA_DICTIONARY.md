# Data Dictionary

The inventory CSV is normalized to the following fields. Optional fields remain unavailable when they are not mapped from the source.

| Field | Description | Source / derivation |
|---|---|---|
| `inventory_id` | Row identifier | Generated upload row ID or demo ID |
| `warehouse_id` | Warehouse or site key | Required source field |
| `sku_id` | Product identifier | Required source field |
| `quantity_on_hand` | Current stock quantity | Required numeric source field |
| `unit_cost` | Cost per unit | Optional source field |
| `inventory_value` | Total stock value | Source value, otherwise quantity × unit cost |
| `product_name` | Product description | Optional source field; SKU used as fallback |
| `category` | Product category | Optional source field |
| `zone_id` | Storage zone key | Optional source field |
| `rack_id` | Rack or bin key | Optional source field |
| `rack_capacity` | Capacity of the location | Optional source field |
| `warehouse_capacity` | Capacity of the warehouse | Optional source field |
| `reorder_level` | Reorder threshold | Optional source field |
| `safety_stock` | Safety stock threshold | Optional source field |
| `last_movement_date` | Last recorded movement date | Optional source date |
| `days_since_movement` | Days since last movement | Calculated from the movement date |
| `stock_status` | Current stock status | Calculated from quantity, safety stock and reorder level |

The demo model also contains warehouse, zone, rack, product, movement, inbound, outbound and alert records. Operational history is not generated from an inventory-only upload.
