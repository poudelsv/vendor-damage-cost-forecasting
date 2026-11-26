"""Vendor scorecards: incident rate, avg cost, discrepancy rate, exposure."""
import csv, collections, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    inc=list(csv.DictReader(open(ROOT/"data/incidents.csv")))
    aud=list(csv.DictReader(open(ROOT/"data/audits.csv")))
    cards=[]
    for vid in sorted({r["vendor_id"] for r in inc}):
        gi=[r for r in inc if r["vendor_id"]==vid]; ga=[r for r in aud if r["vendor_id"]==vid]
        cost=sum(float(r["damage_cost_usd"]) for r in gi)
        disc=sum(1 for r in ga if r["discrepancy_type"]!="match")/max(1,len(ga))
        score=round(max(0,100 - disc*30 - min(30,cost/2000) - len(gi)*0.5),1)
        cards.append({"vendor_id":vid,"incidents":len(gi),"total_cost_usd":round(cost,2),
            "avg_cost_usd":round(cost/max(1,len(gi)),2),"audits":len(ga),
            "discrepancy_rate_pct":round(disc*100,1),"score_0_100":score})
    cards.sort(key=lambda x:-x["total_cost_usd"])
    (ROOT/"analysis/vendor_scorecards.json").write_text(json.dumps(cards,indent=2))
    with open(ROOT/"analysis/vendor_scorecards.csv","w",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=list(cards[0].keys())); wr.writeheader(); wr.writerows(cards)
    print(f"scorecards: {len(cards)} vendors")
if __name__=="__main__": main()
