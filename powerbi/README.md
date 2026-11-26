# Power BI

1. Get Data > Text/CSV: `data/incidents.csv`, `data/audits.csv`, `data/vendors.csv`.
2. Model: incidents[vendor_id] -> vendors[vendor_id]; audits[vendor_id] -> vendors[vendor_id].
3. Paste the measures from `measures.dax`.
4. Pages: (a) Exposure by process — bar chart of Expected Exposure, (b) Vendor scorecard table, (c) Audit reconciliation — discrepancy type donut + repeat-issue flag.
