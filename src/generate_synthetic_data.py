"""Generate SYNTHETIC sample data. NOT real Delta internal data.
Seeded (42) so outputs are reproducible. Anonymised vendors V-01..V-06,
processes are generic ramp/handling categories."""
import csv, random
from pathlib import Path
random.seed(42)
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/"data"; DATA.mkdir(exist_ok=True)
VENDORS=[("V-01","Baggage Handling"),("V-02","Ramp Loading"),("V-03","Catering"),
("V-04","Fueling"),("V-05","Pushback & Towing"),("V-06","Aircraft Cleaning")]
PROCESSES=["Baggage Handling","Ramp Loading","Catering","Fueling","Pushback & Towing","Aircraft Cleaning"]
BASE={"Baggage Handling":420,"Ramp Loading":650,"Catering":280,"Fueling":900,"Pushback & Towing":750,"Aircraft Cleaning":180}
DMG={"Baggage Handling":["belt loader strike","container damage","cart collision"],
"Ramp Loading":["cargo door strike","loader impact","pallet drop"],
"Catering":["truck contact","lift damage","galley door strike"],
"Fueling":["hose coupling damage","panel strike","spill cleanup"],
"Pushback & Towing":["towbar damage","nose-gear strike","wingtip contact"],
"Aircraft Cleaning":["lavatory panel damage","cabin fixture damage","exterior strike"]}
def main():
    with open(DATA/"vendors.csv","w",newline="") as f:
        wr=csv.writer(f); wr.writerow(["vendor_id","vendor_name","primary_process","contract_start","stations"])
        for vid,proc in VENDORS:
            wr.writerow([vid,f"Vendor {vid[-2:]} (anonymised)",proc,"2024-01-01",random.randint(2,6)])
    incidents=[]; costs=[]
    iid=1000
    for i in range(142):
        vid,proc=random.choice(VENDORS)
        # skew: make V-02 Ramp and V-01 Baggage the repeat offenders
        if random.random()<0.25: vid,proc="V-02","Ramp Loading"
        if random.random()<0.15: vid,proc="V-01","Baggage Handling"
        cost=round(random.gauss(BASE[proc],BASE[proc]*0.35))
        cost=max(80,min(1800,cost))
        month=random.randint(1,6); day=random.randint(1,28)
        sev="Minor" if cost<400 else ("Major" if cost<900 else "Severe")
        incidents.append([f"INC-{iid}",f"2025-{month:02d}-{day:02d}",vid,proc,random.choice(DMG[proc]),cost,sev])
        parts=round(cost*0.55); labour=round(cost*0.30); down=max(0,cost-parts-labour)
        costs.append([f"INC-{iid}",parts,labour,down,cost]); iid+=1
    with open(DATA/"incidents.csv","w",newline="") as f:
        wr=csv.writer(f); wr.writerow(["incident_id","incident_date","vendor_id","process","damage_type","damage_cost_usd","severity"]); wr.writerows(incidents)
    with open(DATA/"damage_costs.csv","w",newline="") as f:
        wr=csv.writer(f); wr.writerow(["incident_id","parts_usd","labour_usd","downtime_usd","total_usd"]); wr.writerows(costs)
    audits=[]
    for a in range(48):
        vid,proc=random.choice(VENDORS)
        v_find=random.randint(0,4); l_find=v_find+random.choice([-1,0,0,0,1,2])
        l_find=max(0,l_find)
        disc="match" if v_find==l_find else ("underreported" if l_find>v_find else "overreported")
        # repeat-operational flag for recurring combos
        repeat="Yes" if (vid in ("V-01","V-02") and proc in ("Baggage Handling","Ramp Loading") and random.random()<0.6) else "No"
        audits.append([f"AUD-{2000+a}",f"2025-{random.randint(1,6):02d}-{random.randint(1,28):02d}",vid,proc,v_find,l_find,disc,repeat])
    with open(DATA/"audits.csv","w",newline="") as f:
        wr=csv.writer(f); wr.writerow(["audit_id","audit_date","vendor_id","process","vendor_reported_findings","leader_findings","discrepancy_type","repeat_operational_issue"]); wr.writerows(audits)
    print(f"generated {len(incidents)} incidents, {len(audits)} audits")
if __name__=="__main__": main()
