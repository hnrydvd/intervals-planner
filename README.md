# 12-Week Indoor Cycling + Easy Running Base Block for intervals.icu

An example 12-week winter base plan for cyclists who want to ride indoors on weekdays, do long rides on weekends, and rebuild an easy running base alongside. The plan is delivered as ready-to-import intervals.icu workouts, plus scripts to load them into your calendar.

- 84 workouts over 12 weeks (48 rides, 36 runs)
- Roughly 5.5 to 9.3 hours of riding and 65 to 150 minutes of running per week
- Bike intensity is prescribed as a percentage of FTP, run intensity as a percentage of max heart rate, so it scales to any athlete
- The first run is 20 minutes; running volume builds gradually, with deload weeks at 4, 8 and 12

## Repository contents

| File | Purpose |
|---|---|
| `intervals_plan_12wk.json` | All 84 workouts (dates, names, workout text, IDs). Source of truth for the scripts. |
| `upload_to_intervals.py` | Adds the workouts to your intervals.icu calendar via the API. Skips ones already there. |
| `update_intervals.py` | Rewrites descriptions of workouts already in your calendar when the JSON changes. |
| `plan_overview.csv` | One row per session (date, day, type, name, minutes) for a quick overview. |

## Weekly structure

| Day | Session |
|---|---|
| Mon | Easy run |
| Tue | Indoor sweet spot |
| Wed | Easy run (longest of the week) |
| Thu | Indoor tempo, then threshold, then short VO2 |
| Fri | Easy run (short, the day before the long ride) |
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

SS = sweet spot. Tuesday and Thursday sessions include warmup, rest and cooldown, so some run longer than the headline durations suggest. Peak weeks are about 9.3 hours of riding plus 2 to 2.5 hours of running.

## Intensity reference

| Work | Target |
|---|---|
| Z2 / endurance rides | 62% FTP, HR roughly at or below 75% of max |
| Sweet spot | 90% FTP |
| Tempo | 82% FTP |
| Threshold | 98% FTP |
| VO2 intervals | 110% FTP |
| Easy runs | 50-73% of max HR, conversational effort; let HR lead, not pace |

This block is base only: no strides, tempo or race-pace running. Run/walk is fine in weeks 1-3 if calves or shins complain.

## Requirements

- An [intervals.icu](https://intervals.icu) account
- Python 3 (the scripts use only the standard library, nothing to install)
- Your **FTP** set under Ride settings, and your **max HR** set under Run settings, so percentage targets calculate correctly

## Usage

### Upload to your calendar

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

Each workout has an `external_id`, so re-running the upload skips workouts that are already in your calendar rather than duplicating them.

Treat your API key like a password: don't commit it or put it in a file in the repo.

### Changing the start date

Dates are fixed in `intervals_plan_12wk.json` (week 1 starts Monday, Oct 26, 2026). To start on a different Monday, shift every `start_date_local` value by the same whole number of weeks before uploading. For example, to move the plan forward by 7 days:

```python
import json, datetime as dt
shift = dt.timedelta(days=7)
events = json.load(open("intervals_plan_12wk.json"))
for e in events:
    d = dt.datetime.fromisoformat(e["start_date_local"]) + shift
    e["start_date_local"] = d.isoformat()
json.dump(events, open("intervals_plan_12wk.json", "w"), indent=1)
```

Keep the shift a multiple of 7 so the weekly structure stays on the right days.

### Editing the plan after upload

`upload_to_intervals.py` will not change workouts already in your calendar, because it skips matching IDs. To change them:

1. Edit the `description` text in `intervals_plan_12wk.json`.
2. Preview and apply only the affected workouts:
   ```
   python3 update_intervals.py --match -run --dry-run
   python3 update_intervals.py --match -run
   ```

`--match` filters on the workout ID (`-run`, `-ss`, `-thu`, `-sat-long`, `-sun-z2`). Omit it to update every workout whose text differs. The update overwrites matched descriptions, including any edits you made by hand in intervals.icu.

### Workout IDs

IDs follow `winter26-W{week}-{day}-{type}`, for example `winter26-W07-tue-ss` or `winter26-W03-fri-run`.

## Workout text syntax

Workouts use the intervals.icu text format. Steps start with `-`, repeats are an `Nx` header line, and ramps use `ramp lo-hi%`:

```
Warmup
- 12m ramp 50-75%

Sweet spot 2x
- 20m 90%
- 5m 55%

Cooldown
- 5m 50%
```

Run steps use heart rate, e.g. `- 25m 50-73% HR`. A single value like `73% HR` is read as a target rather than a ceiling, so keep a range.

## Notes

- This plan is a general template, not personalised coaching. Adjust volume and intensity to your own fitness, schedule and recovery.
- If the total load is too much, shorten the Sunday ride first and leave the runs alone.
