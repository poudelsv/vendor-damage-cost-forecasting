-- 1. Expected exposure by process: avg cost x frequency
SELECT process, COUNT(*) AS incidents, ROUND(AVG(damage_cost_usd),2) AS avg_cost,
  ROUND(SUM(damage_cost_usd),2) AS total_cost,
  ROUND(AVG(damage_cost_usd)*COUNT(*)/6*12,2) AS annualised_expected_exposure
FROM incidents GROUP BY process ORDER BY annualised_expected_exposure DESC;
-- 2. Reconciliation discrepancies (vendor vs leader)
SELECT vendor_id, process, COUNT(*) AS discrepant_audits
FROM audits WHERE discrepancy_type <> 'match' GROUP BY vendor_id, process ORDER BY 3 DESC;
-- 3. Repeat operational issues vs one-off reporting discrepancies
SELECT repeat_operational_issue, discrepancy_type, COUNT(*) FROM audits GROUP BY 1,2;
-- 4. Monthly trend
SELECT substr(incident_date,1,7) AS month, COUNT(*) AS incidents, ROUND(SUM(damage_cost_usd),2) AS cost
FROM incidents GROUP BY month ORDER BY month;
-- 5. Vendor scorecard
SELECT vendor_id, COUNT(*) AS incidents, ROUND(AVG(damage_cost_usd),2) AS avg_cost, ROUND(SUM(damage_cost_usd),2) AS total_cost
FROM incidents GROUP BY vendor_id ORDER BY total_cost DESC;
