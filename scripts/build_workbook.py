"""Build excel/Vendor_Damage_Cost_Forecasting.xlsx from analysis outputs (openpyxl)."""
import csv, json
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font
ROOT=Path(__file__).resolve().parents[1]
wb=Workbook(); ws=wb.active; ws.title="Exposure by Process"
ws.append(["Process","Incidents","Avg cost (USD)","Total cost (USD)","Monthly freq","Annualised expected exposure (USD)"])
for r in csv.DictReader(open(ROOT/"analysis/exposure_by_process.csv")):
    ws.append([r["process"],int(r["incidents"]),float(r["avg_cost_usd"]),float(r["total_cost_usd"]),float(r["monthly_frequency"]),float(r["annualised_expected_exposure_usd"])])
for c in ws[1]: c.font=Font(bold=True)
ws2=wb.create_sheet("Vendor Scorecards")
ws2.append(["Vendor","Incidents","Total cost (USD)","Avg cost (USD)","Audits","Discrepancy rate %","Score /100"])
for r in csv.DictReader(open(ROOT/"analysis/vendor_scorecards.csv")):
    ws2.append([r["vendor_id"],int(r["incidents"]),float(r["total_cost_usd"]),float(r["avg_cost_usd"]),int(r["audits"]),float(r["discrepancy_rate_pct"]),float(r["score_0_100"])])
for c in ws2[1]: c.font=Font(bold=True)
ws3=wb.create_sheet("Preventable Exposure")
ws3.append(["Vendor","Process","Incidents","Avg cost (USD)","Preventable exposure (USD)"])
for r in csv.DictReader(open(ROOT/"analysis/preventable_exposure.csv")):
    ws3.append([r["vendor_id"],r["process"],int(r["incidents"]),float(r["avg_cost_usd"]),float(r["preventable_exposure_usd"])])
for c in ws3[1]: c.font=Font(bold=True)
model=json.load(open(ROOT/"analysis/cost_model.json"))
ws3.append([]); ws3.append(["TOTAL PREVENTABLE EXPOSURE (USD)",model["preventable_exposure_usd"]])
wb.save(ROOT/"excel/Vendor_Damage_Cost_Forecasting.xlsx"); print("workbook written")
