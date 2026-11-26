# Daily automation — setup

Status 2026-11-26: BLOCKED on repo creation. The repo
`poudelsv/vendor-damage-cost-forecasting` does not exist yet on GitHub.
`POST /user/repos` via the registered token returned 403
"Resource not accessible by personal access token", so the repo cannot be
created from this VM. Create it in the browser first (github.com, new
repository, name `vendor-damage-cost-forecasting`, public, do not add a
README/gitignore/license there), then run the push below. Do NOT create the
cron until the push is verified.

## 1. Push the project (once, after the repo exists in the browser)

```bash
python3 ~/workspace/custom-connectors/custom.github/bin/github.py push \
  --owner poudelsv --repo vendor-damage-cost-forecasting \
  --path ~/workspace/projects/vendor-damage-cost-forecasting \
  --message "feat: Vendor Damage Cost Forecasting and Safety Audit Reconciliation (synthetic replication)"
```

This pushes every tracked file (except .git/, __pycache__, *.db/sqlite,
.daily_run_log.json, data/daily/) as one Git Data API commit. Verify with:

```bash
python3 ~/workspace/custom-connectors/custom.github/bin/github.py get-repo --owner poudelsv --repo vendor-damage-cost-forecasting
```

## 2. Daily cron, ~09:00 America/Chicago (create only after step 1 works)

```bash
crontab -e
# add:
0 9 * * * cd $HOME/workspace/projects/vendor-damage-cost-forecasting && /usr/bin/python3 scripts/daily_contribution_api.py >> logs/daily.log 2>&1
```

- Use `scripts/daily_contribution_api.py`, NOT `scripts/daily_contribution.py`.
  The old script uses `git push` to github.com, which does not work from this
  VM (only api.github.com is a registered host). The API script creates one
  commit per batch through the GitHub REST API instead.
- Each run picks N = randint(20, 60), writes N batch files under
  `data/daily/YYYY-MM-DD/`, creates one API commit per batch, then one
  run-log commit. Dry-run (no files, no API calls):
  `python3 scripts/daily_contribution_api.py --dry-run` (verified 2026-11-26:
  "would create 26 batch commits").
- Idempotent per day: a second run on the same day exits without new commits
  (see `.daily_run_log.json`, which is itself pushed as the final commit).
- Git identity used: `poudelsv` / `poudelsv@mail.uc.edu`, branch `main`.
- After API commits, local git HEAD diverges from remote HEAD (local history
  is the 5 initial commits; remote history is the API commits). That is
  expected. Do not `git push` or `git pull` to reconcile; each daily run
  bases its commits on the live remote HEAD fetched via the API.
- The script fails safely (non-zero, logged) if the repo does not exist.
