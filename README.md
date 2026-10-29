# 12-Week Winter Base Block for intervals.icu

Indoor cycling on weekdays, long rides on weekends, plus a gradual return to easy running.
84 workouts, Mon Oct 26, 2026 to Sun Jan 17, 2027.

## Files

| File | Purpose |
|---|---|
| `intervals_plan_12wk.json` | All 84 workouts (dates, names, workout text, IDs). Source of truth for the scripts. |
| `upload_to_intervals.py` | Adds the workouts to your intervals.icu calendar via the API. Skips ones already there. |
| `update_intervals.py` | Rewrites descriptions of workouts already in your calendar when the JSON changes. |
| `plan_overview.csv` | One row per session (date, day, type, name, minutes) for a quick sanity check. |

## Weekly structure

| Day | Session |
|---|---|
| Mon | Easy run |
| Tue | Indoor sweet spot |
| Wed | Easy run (longest of the week) |
| Thu | Indoor tempo, then threshold, then short VO2 |
| Fri | Easy run (short, day before the long ride) |
| Sat | Long ride: mostly Z2 with sweet spot blocks late |
| Sun | Long steady Z2 ride |

Weeks 4, 8 and 12 are deloads.

### Progression

| Wk | Tue | Thu | Sat | Sun | Runs Mon/Wed/Fri (min) |
|---|---|---|---|---|---|
| 1 | 2x20 SS | 3x10 tempo | 2:30 | 2:00 | 20/25/20 |
| 2 | 2x25 SS | 4x10 tempo | 2:45 | 2:00 | 25/30/25 |
| 3 | 3x20 SS | 3x15 tempo | 3:00 | 2:15 | 30/35/30 |
| 4 | 2x20 SS | easy spin | 2:00 | 1:30 | 25/30/25 |
| 5 | 2x30 SS | 3x10 threshold | 3:00 | 2:15 | 30/40/30 |
| 6 | 2x35 SS | 4x10 threshold | 3:15 | 2:30 | 35/45/30 |
| 7 | 3x25 SS | 5x10 threshold | 3:30 | 2:30 | 35/50/35 |
| 8 | 2x20 SS | easy spin | 2:15 | 1:30 | 30/40/30 |
| 9 | 2x40 SS | 5x5 VO2 | 3:15 | 2:30 | 40/55/35 |
| 10 | 3x30 SS | 5x5 VO2 | 3:30 | 2:30 | 40/60/40 |
| 11 | 1x90 SS | 6x5 VO2 | 3:30 | 2:30 | 45/65/40 |
| 12 | 2x20 SS | easy spin | 2:15 | 1:30 | 35/45/35 |

Tuesday and Thursday sessions include warmup, rest and cooldown, so some run longer than the
bike-hours estimate in the original plan (peak weeks are about 9.3 h of riding).

## Before you import

Set these in intervals.icu so the workouts calculate correctly:

- **FTP: 244 W** (Ride settings). Bike steps are %FTP: sweet spot 90%, tempo 82%, threshold 98%, VO2 110%, Z2 62%.
- **Max HR: ~202 bpm** (Run settings). Runs are written as `50-73% HR`, a ceiling of about 148 bpm.

## Upload to your calendar

1. In intervals.icu, open **Settings > Developer Settings** and copy your API key and athlete ID (looks like `i123456`).
2. Set environment variables:
   ```
   export INTERVALS_API_KEY="your_api_key"
   export INTERVALS_ATHLETE_ID="i123456"
   ```
3. Preview, then upload:
   ```
   python3 upload_to_intervals.py --dry-run
   python3 upload_to_intervals.py
   ```
4. Open your calendar at Oct 26 and check week 1 before trusting the rest.

The scripts use only the Python standard library (no installs).

## Editing the plan after upload

Re-running `upload_to_intervals.py` will not change workouts already in your calendar, because it skips matching IDs. To change them:

1. Edit the `description` text in `intervals_plan_12wk.json`.
2. Preview and apply only the affected workouts:
   ```
   python3 update_intervals.py --match -run --dry-run
   python3 update_intervals.py --match -run
   ```
   `--match` filters on the workout ID (`-run`, `-ss`, `-thu`, `-sat-long`, `-sun-z2`). Omit it to update every workout whose text differs.

`update_intervals.py` overwrites matched descriptions, including any edits you made by hand in intervals.icu.

### Workout ID format

`winter26-W{week}-{day}-{type}`, for example `winter26-W07-tue-ss` or `winter26-W03-fri-run`.

### Workout text syntax

Steps start with `-`, repeats are a `Nx` header line, ramps use `ramp lo-hi%`:

```
Warmup
- 12m ramp 50-75%

Sweet spot 2x
- 20m 90%
- 5m 55%

Cooldown
- 5m 50%
```

Run steps use heart rate, e.g. `- 25m 50-73% HR`. A single value like `73% HR` is read as a target, not a ceiling, so keep a range.

## Pacing guide

- **Z2 rides:** about 62% FTP (~150 W), HR at or below about 140 bpm.
- **Easy runs:** about 10:45-11:30/mi, HR at or below about 148 bpm. Let HR lead; run/walk in weeks 1-3 if calves or shins complain.
- **No run intensity** (strides, tempo, race pace) in this block. It is base only.
- If total load becomes too much, shorten the Sunday ride first and leave the runs alone.
