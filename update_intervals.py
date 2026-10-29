#!/usr/bin/env python3
"""Update workouts already in your intervals.icu calendar from intervals_plan_12wk.json.

Matches on external_id (winter26-...) and rewrites the description of any
workout whose text differs from the JSON. Everything else is left alone.

  export INTERVALS_API_KEY="..."  INTERVALS_ATHLETE_ID="i123456"
  python3 update_intervals.py --match -run --dry-run   # preview, runs only
  python3 update_intervals.py --match -run             # apply

Leave off --match to update every workout whose text differs.
Note: this overwrites any edits you made by hand to those descriptions.
"""
import base64, json, os, sys, urllib.request, urllib.error
BASE = "https://intervals.icu/api/v1"
here = os.path.dirname(os.path.abspath(__file__))
plan = {e["external_id"]: e for e in json.load(open(os.path.join(here, "intervals_plan_12wk.json")))}
dry = "--dry-run" in sys.argv
match = sys.argv[sys.argv.index("--match")+1] if "--match" in sys.argv else ""
key, aid = os.environ.get("INTERVALS_API_KEY"), os.environ.get("INTERVALS_ATHLETE_ID")
if not (key and aid): sys.exit("Set INTERVALS_API_KEY and INTERVALS_ATHLETE_ID first.")

def call(method, path, body=None):
    req = urllib.request.Request(BASE+path, method=method, data=json.dumps(body).encode() if body is not None else None)
    req.add_header("Authorization", "Basic "+base64.b64encode(f"API_KEY:{key}".encode()).decode())
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0 (compatible; intervals-uploader/1.0)")
    try:
        with urllib.request.urlopen(req) as r: return json.load(r)
    except urllib.error.HTTPError as e: sys.exit(f"HTTP {e.code}: {e.read().decode()[:500]}")

dates = sorted(e["start_date_local"][:10] for e in plan.values())
live = call("GET", f"/athlete/{aid}/events?oldest={dates[0]}&newest={dates[-1]}")
todo = [(ev, plan[ev["external_id"]]) for ev in live
        if ev.get("external_id") in plan and match in ev["external_id"]
        and (ev.get("description") or "").strip() != plan[ev["external_id"]]["description"].strip()]
print(f"{len(todo)} workouts need updating")
for ev, new in todo:
    print(("would update " if dry else "updating ") + new["start_date_local"][:10], new["name"])
    if not dry: call("PUT", f"/athlete/{aid}/events/{ev['id']}", {"description": new["description"]})
print("Done." if not dry else "Dry run only, nothing changed.")