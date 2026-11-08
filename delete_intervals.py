#!/usr/bin/env python3
"""Bulk delete training blocks from your intervals.icu calendar.

Matches on external_id prefix, so workouts you added by hand are never touched.
Completed activities are separate from planned workouts and are not deleted.

  export INTERVALS_API_KEY="..."  INTERVALS_ATHLETE_ID="i123456"
  python3 delete_intervals.py --prefix winter26- --dry-run
  python3 delete_intervals.py --prefix winter26-
  python3 delete_intervals.py --prefix winter26- spring27-                # several blocks at once
  python3 delete_intervals.py --prefix winter26-W09                       # a single week
  python3 delete_intervals.py --prefix winter26- --from 2026-11-09        # only on/after a date

Lists what matches and asks for confirmation before deleting; --yes skips the prompt.
Deleting can't be undone, but upload_to_intervals.py can re-add workouts from the plan JSON.
"""
import argparse, base64, json, os, sys, urllib.request, urllib.error

BASE = "https://intervals.icu/api/v1"
ap = argparse.ArgumentParser()
ap.add_argument("--prefix", required=True, nargs="+", help="external_id prefix(es), e.g. winter26-")
ap.add_argument("--from", dest="from_date", help="only delete events on/after YYYY-MM-DD")
ap.add_argument("--yes", action="store_true", help="don't ask for confirmation")
ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()
if not all(p.strip() for p in a.prefix):
    sys.exit("--prefix can't be empty.")

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
            data = r.read()
            return json.loads(data) if data else None
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:500]}")

oldest = a.from_date or "2000-01-01"
live = call("GET", f"/athlete/{aid}/events?oldest={oldest}&newest=2100-01-01")
todo = sorted((e for e in live if (e.get("external_id") or "").startswith(tuple(a.prefix))),
              key=lambda e: e["start_date_local"])

print(f"{len(todo)} workouts match")
for ev in todo:
    print(("would delete " if a.dry_run else "") + f"{ev['start_date_local'][:10]}  {ev['external_id']}  {ev['name']}")
if a.dry_run:
    print("Dry run only, nothing changed.")
    sys.exit()
if not todo:
    sys.exit()

if not a.yes:
    try:
        answer = input(f"Permanently delete these {len(todo)} workouts? Type 'delete' to confirm: ")
    except EOFError:
        answer = ""
    if answer.strip() != "delete":
        sys.exit("Cancelled, nothing changed.")

deleted = 0
for i in range(0, len(todo), 40):
    batch = todo[i:i+40]
    call("PUT", f"/athlete/{aid}/events/bulk-delete", [{"id": e["id"]} for e in batch])
    deleted += len(batch)
    print(f"deleted {deleted}/{len(todo)}")
print("Done.")
