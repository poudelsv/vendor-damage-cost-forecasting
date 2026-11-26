"""Reconcile vendor submissions vs safety-leader audits.
Flags: match / underreported / overreported; separates reporting
discrepancies from repeat operational issues."""
import csv, collections, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    rows=list(csv.DictReader(open(ROOT/"data/audits.csv")))
    counts=collections.Counter(r["discrepancy_type"] for r in rows)
    repeat=sum(1 for r in rows if r["repeat_operational_issue"]=="Yes")
    under=[r for r in rows if r["discrepancy_type"]=="underreported"]
    by_vendor=collections.Counter(r["vendor_id"] for r in under)
    out={"total_audits":len(rows),"discrepancy_counts":dict(counts),
         "discrepancy_rate_pct":round(100*(len(rows)-counts.get("match",0))/len(rows),1),
         "repeat_operational_audits":repeat,
         "underreported_by_vendor":dict(by_vendor)}
    (ROOT/"analysis/reconciliation.json").write_text(json.dumps(out,indent=2))
    with open(ROOT/"analysis/audit_discrepancies.csv","w",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0].keys())); wr.writeheader()
        wr.writerows([r for r in rows if r["discrepancy_type"]!="match"])
    print(out)
if __name__=="__main__": main()
