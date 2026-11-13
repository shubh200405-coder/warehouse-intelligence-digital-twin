# KPI Definitions

| KPI | Calculation | Data required |
|---|---|---|
| Inventory units | Sum of quantity on hand | Quantity |
| Inventory value | Sum of quantity × unit cost, or source inventory value | Quantity and cost or value |
| Active SKUs | Distinct SKU count | SKU |
| Capacity utilization | Occupied units ÷ capacity × 100 | Quantity, rack or warehouse capacity |
| Low-stock SKUs | Distinct SKUs at or below reorder level | SKU and reorder level |
| Out-of-stock SKUs | Distinct SKUs with quantity ≤ 0 | SKU and quantity |
| Non-moving value | Inventory value with no movement for more than 90 days | Value and last movement date |
| Receiving completion | Received units ÷ expected units × 100 | Inbound receipt quantities |
| Fulfilment rate | Dispatched units ÷ ordered units × 100 | Outbound order quantities |

Ageing is based on **days since last movement**, not purchase age. The ABC calculation sorts SKU inventory value descending and assigns A through 80% cumulative value, B through 95%, and C to the remainder. This is a configurable convention.

Inventory turnover, days inventory outstanding, XYZ classification, picking accuracy and OTIF are not calculated unless the required cost, demand, error or delivery data exists.
