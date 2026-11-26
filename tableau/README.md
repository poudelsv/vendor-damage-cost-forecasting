# Tableau

1. Connect to `data/incidents.csv`, `data/audits.csv`, `data/vendors.csv` (join on vendor_id).
2. Calculated fields:
   - `Expected Exposure` = `AVG([Damage Cost Usd]) * COUNT([Incident Id]) / 6 * 12`
   - `Discrepancy Flag` = `[Discrepancy Type] != "match"`
   - `Repeat Issue` = `[Repeat Operational Issue] = "Yes"`
3. Dashboards: Exposure by Process (bar), Vendor Scorecard (table), Audit Reconciliation (discrepancy vs repeat-issue crosstab).
