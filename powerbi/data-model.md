# Power BI Data Model

Use a star schema for a future Power BI model. Keep the fact tables at their native grain and filter them through conformed dimensions.

| Table | Grain |
|---|---|
| `FactInventorySnapshot` | One SKU at one location and snapshot date |
| `FactInventoryMovement` | One inventory movement event |
| `FactInboundReceipt` | One receipt line |
| `FactOutboundOrder` | One order line |
| `FactWarehouseAlert` | One alert event |
| `DimDate` | One calendar date |
| `DimWarehouse` | One warehouse |
| `DimProduct` | One SKU |
| `DimLocation` | One warehouse/zone/aisle/rack/bin location |
| `DimSupplier` | One supplier |

Create one-to-many relationships from dimensions to facts. Use role-playing date relationships for snapshot, movement, receipt and order dates. Avoid direct fact-to-fact relationships.

`measures.dax` contains starter measures. Validate table and column names against the final source model before using them.
