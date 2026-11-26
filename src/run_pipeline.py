"""Run the full pipeline end-to-end: generate -> ingest (sqlite fallback) -> cost model -> reconcile -> scorecards -> Excel workbook."""
import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(mod):
    subprocess.run([sys.executable,"-m",mod],cwd=ROOT,check=True)
if __name__=="__main__":
    for m in ["src.generate_synthetic_data","src.ingest","src.cost_model","src.reconcile","src.scorecards"]:
        run(m)
    subprocess.run([sys.executable,"scripts/build_workbook.py"],cwd=ROOT,check=True)
    print("pipeline complete — see analysis/")
