"""Daily automation (GitHub API version): one run per day, random N batches.

Each run picks N = randint(20, 60) (e.g. 30 one day, 56 another), generates
N small synthetic incident batches under data/daily/YYYY-MM-DD/, and creates
one GitHub commit per batch via the Git Data API (helper
~/workspace/custom-connectors/custom.github/bin/github.py). No `git push`
is used: git push over https to github.com is not available from this VM
(only api.github.com is a registered host), so all remote writes go through
the API. Idempotent per day: if .daily_run_log.json already records today,
exit 0 with no new commits. All generated data is SYNTHETIC sample data,
not real Delta records.

Prerequisite: the repo poudelsv/vendor-damage-cost-forecasting must already
exist on GitHub (it could NOT be created via the API on 2026-11-25: the
registered token returned 403 "Resource not accessible by personal access
token" on POST /user/repos, so the repo must be created in the browser
first; see CRON_SETUP.md). After API commits, the local git HEAD diverges
from the remote HEAD (local history is the 5 initial commits; the remote
history is the API commits). That is expected: files on disk are the source
of truth locally, remote history is via the API. Do not `git push`/`git pull`
to reconcile; re-running this script bases each new commit on the live
remote HEAD fetched via the API.

Run via cron ~09:00 America/Chicago - see CRON_SETUP.md (cron NOT created yet).
Dry run (no files, no API calls): python3 scripts/daily_contribution_api.py --dry-run
"""
import csv
import json
import random
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / ".daily_run_log.json"
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.github/bin"))
import github as gh  # noqa: E402

OWNER = "poudelsv"
REPO = "vendor-damage-cost-forecasting"
BRANCH = "main"
PROCESSES = ["Baggage Handling", "Ramp Loading", "Catering", "Fueling",
             "Pushback & Towing", "Aircraft Cleaning"]
BASE = {"Baggage Handling": 420, "Ramp Loading": 650, "Catering": 280,
        "Fueling": 900, "Pushback & Towing": 750, "Aircraft Cleaning": 180}


def main():
    dry_run = "--dry-run" in sys.argv
    today = date.today().isoformat()
    if LOG.exists():
        try:
            if json.loads(LOG.read_text()).get("last_run_date") == today:
                print(f"already ran today ({today}); nothing to do")
                return 0
        except json.JSONDecodeError:
            pass
    rng = random.Random()
    n = rng.randint(20, 60)
    if dry_run:
        print(f"dry-run: would create {n} batch commits for {today} (no files, no API calls)")
        return 0
    status, repo = gh.get_repo(OWNER, REPO)
    if status != 200:
        print(f"ERROR: repo {OWNER}/{REPO} not accessible ({status}): {repo}. "
              "Create it on GitHub first (see CRON_SETUP.md); refusing to run.",
              file=sys.stderr)
        return 1
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
            wr.writerow([today, vendor, proc, cost,
                         "Minor" if cost < 400 else ("Major" if cost < 900 else "Severe"), "yes"])
        rel = str(batch.relative_to(ROOT))
        sha, _ = gh.commit_files(OWNER, REPO, BRANCH,
                                  f"data: synthetic daily batch {i}/{n} - {proc} ({vendor}, ${cost}) [{today}]",
                                  [(rel, str(batch))])
        print(f"batch {i}/{n}: commit {sha[:7]}")
    LOG.write_text(json.dumps({"last_run_date": today, "batches": n}, indent=2))
    sha, _ = gh.commit_files(OWNER, REPO, BRANCH,
                             f"chore: daily run log for {today} ({n} batches)",
                             [(".daily_run_log.json", str(LOG))])
    print(f"done: {n} batch commits + run-log commit {sha[:7]} via API ({today})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
