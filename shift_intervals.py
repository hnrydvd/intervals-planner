#!/usr/bin/env python3
"""Move workouts already in your intervals.icu calendar forward (or back) in time.

Matches on external_id prefix, changes only start_date_local (time of day is kept).

  export INTERVALS_API_KEY="..."  INTERVALS_ATHLETE_ID="i123456"
  python3 shift_intervals.py --prefix winter26- --weeks 1 --dry-run
  python3 shift_intervals.py --prefix winter26- --weeks 1
  python3 shift_intervals.py --prefix winter26- --days -3 --from 2026-11-09   # only on/after a date
  python3 shift_intervals.py --prefix winter26- --weeks 1 --plan my_plan.json # also write shifted JSON

Use --weeks or --days (or both); negative moves earlier.
--plan writes <plan>.shifted.json with the same shift applied, so that later runs of
update_intervals.py (which looks up events by the plan's dates) still find them.
"""
import argparse, base64, json, os, sys, urllib.request, urllib.error
from datetime import datetime, timedelta

BASE = "https://intervals.icu/api/v1"
ap = argparse.ArgumentParser()
ap.add_argument("--prefix", required=True, help="external_id prefix, e.g. winter26-")
ap.add_argument("--weeks", type=int, default=0)
ap.add_argument("--days", type=int, default=0)
ap.add_argument("--from", dest="from_date", help="only move events on/after YYYY-MM-DD")
ap.add_argument("--plan", help="plan JSON to also shift (writes a .shifted.json copy)")
ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()
delta = timedelta(weeks=a.weeks, days=a.days)
if not delta:
    sys.exit("Give --weeks and/or --days (non-zero).")

key, aid = os.environ.get("INTERVALS_API_KEY"), os.environ.get("INTERVALS_ATHLETE_ID")
if not (key and aid):
    sys.exit("Set INTERVALS_API_KEY and INTERVALS_ATHLETE_ID first.")

def call(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method,
        data=json.dumps(body).encode() if body is not None else None)
    req.add_header("Authorization", "Basic " + base64.b64encode(f"API_KEY:{key}".encode()).decode())
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0 (compatible; intervals-uploader/1.0)")  # avoids Cloudflare 1010
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:500]}")

shift = lambda s: (datetime.fromisoformat(s) + delta).strftime("%Y-%m-%dT%H:%M:%S")

oldest = a.from_date or "2000-01-01"
live = call("GET", f"/athlete/{aid}/events?oldest={oldest}&newest=2100-01-01")
todo = sorted((e for e in live if (e.get("external_id") or "").startswith(a.prefix)),
              key=lambda e: e["start_date_local"])
print(f"{len(todo)} workouts to move by {delta.days:+d} days")
for ev in todo:
    new = shift(ev["start_date_local"])
    print(("would move " if a.dry_run else "moving ") + f"{ev['start_date_local'][:10]} -> {new[:10]}  {ev['name']}")
    if not a.dry_run:
        call("PUT", f"/athlete/{aid}/events/{ev['id']}", {"start_date_local": new})

if a.plan:
    plan = json.load(open(a.plan))
    for e in plan:
        if e["external_id"].startswith(a.prefix) and (not a.from_date or e["start_date_local"][:10] >= a.from_date):
            e["start_date_local"] = shift(e["start_date_local"])
    out = a.plan.rsplit(".json", 1)[0] + ".shifted.json"
    if not a.dry_run:
        json.dump(plan, open(out, "w"), indent=2)
        print("Wrote", out)
print("Dry run only, nothing changed." if a.dry_run else "Done.")
