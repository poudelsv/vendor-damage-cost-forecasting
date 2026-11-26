"""Cost model: expected exposure = avg damage cost x incident frequency.
Preventable exposure: excess incidents above a 2-per-month baseline
(12 over the 6-month period) in recurring vendor+process groups,
at a 25% achievable-reduction assumption.
All inputs are SYNTHETIC."""
import csv, collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load():
    rows=list(csv.DictReader(open(ROOT/"data/incidents.csv")))
    for r in rows: r["damage_cost_usd"]=float(r["damage_cost_usd"])
    return rows
def main():
    rows=load()
    total=sum(r["damage_cost_usd"] for r in rows)
    by_proc=collections.defaultdict(list)
    for r in rows: by_proc[r["process"]].append(r["damage_cost_usd"])
    exposure=[]
    for proc,costs in sorted(by_proc.items()):
        n=len(costs); avg=sum(costs)/n
        # 6-month period -> annualised expected exposure = avg * monthly freq * 12
        exposure.append({"process":proc,"incidents":n,"avg_cost_usd":round(avg,2),
            "total_cost_usd":round(sum(costs),2),"monthly_frequency":round(n/6,2),
            "annualised_expected_exposure_usd":round(avg*(n/6)*12,2)})
    # preventable: recurring groups
    groups=collections.defaultdict(list)
    for r in rows: groups[(r["vendor_id"],r["process"])].append(r)
    preventable=0.0; detail=[]
    for (vid,proc),g in sorted(groups.items()):
        if len(g)>=13:  # above the 2/month baseline
            avg=sum(x["damage_cost_usd"] for x in g)/len(g)
            excess=(len(g)-12)*avg*0.25
            preventable+=excess
            detail.append({"vendor_id":vid,"process":proc,"incidents":len(g),"avg_cost_usd":round(avg,2),"preventable_exposure_usd":round(excess,2)})
    out={"total_incidents":len(rows),"total_damage_cost_usd":round(total,2),
         "preventable_exposure_usd":round(preventable,2),"exposure_by_process":exposure,
         "preventable_by_vendor_process":sorted(detail,key=lambda x:-x["preventable_exposure_usd"])}
    import json; (ROOT/"analysis").mkdir(exist_ok=True)
    (ROOT/"analysis/cost_model.json").write_text(json.dumps(out,indent=2))
    with open(ROOT/"analysis/exposure_by_process.csv","w",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=list(exposure[0].keys())); wr.writeheader(); wr.writerows(exposure)
    with open(ROOT/"analysis/preventable_exposure.csv","w",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=list(detail[0].keys())); wr.writeheader(); wr.writerows(detail)
    print(f"incidents={len(rows)} total=${total:,.2f} preventable=${preventable:,.2f}")
if __name__=="__main__": main()
