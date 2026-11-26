"""Daily automation: one run per day, one push at the end.

Each run picks N = randint(20, 60) (e.g. 30 one day, 56 another), generates
N small synthetic incident/audit batches under data/daily/YYYY-MM-DD/,
commits each batch separately with a meaningful message, then pushes ONCE.
Idempotent per day: if .daily_run_log.json already records today, exit 0
with no new commits. Fails safely (non-zero) if there is no git remote.
Run via cron ~09:00 America/Chicago — see CRON_SETUP.md.
All generated data is SYNTHETIC sample data, not real Delta records.
"""
import csv, json, random, subprocess, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / ".daily_run_log.json"
PROCESSES = ["Baggage Handling", "Ramp Loading", "Catering", "Fueling", "Pushback & Towing", "Aircraft Cleaning"]
BASE = {"Baggage Handling": 420, "Ramp Loading": 650, "Catering": 280, "Fueling": 900, "Pushback & Towing": 750, "Aircraft Cleaning": 180}

def sh(*args, check=True):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=check)

def main():
    today = date.today().isoformat()
    if LOG.exists():
        try:
            if json.loads(LOG.read_text()).get("last_run_date") == today:
                print(f"already ran today ({today}); nothing to do")
                return 0
        except json.JSONDecodeError:
            pass
    # fail safely without a remote — do not create empty local-only history
    remotes = sh("git", "remote", check=False).stdout.strip()
    if not remotes:
        print("ERROR: no git remote configured; refusing to run (see CRON_SETUP.md)", file=sys.stderr)
        return 1
    sh("git", "config", "user.name", "poudelsv")
    sh("git", "config", "user.email", "poudelsv@mail.uc.edu")
    sh("git", "config", "init.defaultBranch", "main")
    rng = random.Random()
    n = rng.randint(20, 60)
    day_dir = ROOT / "data" / "daily" / today
    day_dir.mkdir(parents=True, exist_ok=True)
    for i in range(1, n + 1):
        proc = rng.choice(PROCESSES)
        cost = max(80, min(1800, round(rng.gauss(BASE[proc], BASE[proc] * 0.35))))
        vendor = f"V-0{rng.randint(1, 6)}"
        batch = day_dir / f"batch_{i:02d}.csv"
        with open(batch, "w", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(["incident_date", "vendor_id", "process", "damage_cost_usd", "severity", "synthetic"])
            wr.writerow([today, vendor, proc, cost, "Minor" if cost < 400 else ("Major" if cost < 900 else "Severe"), "yes"])
        sh("git", "add", str(batch.relative_to(ROOT)))
        sh("git", "commit", "-m", f"data: synthetic daily batch {i}/{n} — {proc} ({vendor}, ${cost}) [{today}]")
    LOG.write_text(json.dumps({"last_run_date": today, "batches": n}, indent=2))
    sh("git", "add", ".daily_run_log.json")
    sh("git", "commit", "-m", f"chore: daily run log for {today} ({n} batches)")
    sh("git", "push", "origin", "main")
    print(f"done: {n} batch commits + run-log commit pushed once ({today})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
