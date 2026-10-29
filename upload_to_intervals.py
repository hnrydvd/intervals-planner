#!/usr/bin/env python3
"""Push the 12-week plan into your intervals.icu calendar.

Setup (intervals.icu > Settings > Developer Settings):
  export INTERVALS_API_KEY="your_api_key"
  export INTERVALS_ATHLETE_ID="i123456"      # your athlete id (shown next to the API key)

Run a preview first:   python3 upload_to_intervals.py --dry-run
Then upload:           python3 upload_to_intervals.py

Events carry an external_id (winter26-...), so workouts already in your
calendar from an earlier run of this script are skipped, not duplicated.
"""
import base64, json, os, sys, urllib.request, urllib.error

BASE = "https://intervals.icu/api/v1"
here = os.path.dirname(os.path.abspath(__file__))
events = json.load(open(os.path.join(here, "intervals_plan_12wk.json")))
dry = "--dry-run" in sys.argv

key = os.environ.get("INTERVALS_API_KEY")
aid = os.environ.get("INTERVALS_ATHLETE_ID")
if not dry and not (key and aid):
    sys.exit("Set INTERVALS_API_KEY and INTERVALS_ATHLETE_ID first (or use --dry-run).")

def call(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method,
        data=json.dumps(body).encode() if body is not None else None)
    token = base64.b64encode(f"API_KEY:{key}".encode()).decode()
    req.add_header("Authorization", "Basic " + token)
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0 (compatible; intervals-uploader/1.0)")
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:500]}")

first, last = events[0]["start_date_local"][:10], events[-1]["start_date_local"][:10]
print(f"{len(events)} workouts, {first} to {last}")
if dry:
    for e in events[:14]:
        print(e["start_date_local"][:16], e["type"].ljust(5), e["name"])
    print("... (dry run, nothing sent)")
    sys.exit()

existing = call("GET", f"/athlete/{aid}/events?oldest={first}&newest={last}")
have = {e.get("external_id") for e in existing if e.get("external_id")}
new = [e for e in events if e["external_id"] not in have]
print(f"{len(events)-len(new)} already present, uploading {len(new)}")
for i in range(0, len(new), 40):
    call("POST", f"/athlete/{aid}/events/bulk", new[i:i+40])
print("Done. Check your calendar from", first)