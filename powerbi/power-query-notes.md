# Power Query Notes

1. Import raw extracts as staging queries and preserve them unchanged.
2. Create referenced queries for transformed tables.
3. Trim identifiers and standardize column names and data types.
4. Convert quantity and cost fields to numeric types; review conversion errors instead of silently replacing them.
5. Parse dates using an explicit locale.
6. Check dimension-key uniqueness and identify orphan foreign keys.
7. Create and mark a dedicated date table.
8. Keep inventory snapshots separate from movement and order events.
9. Document snapshot timestamps and event semantics before calculating turnover or fulfilment metrics.

These notes describe a proposed Power BI workflow. They have not been applied to a PBIX file.
