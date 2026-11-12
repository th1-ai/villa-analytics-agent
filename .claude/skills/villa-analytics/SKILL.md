---
name: villa-analytics
description: Read-only performance report for a boutique hotel or villa rental. Pulls reservations from the PMS (and GA4 website analytics if configured), then reports occupancy, ADR, RevPAR, booking source mix, forward pace and traffic quality, with a short list of recommendations. Use when the operator asks to check analytics, how the property is doing, for an occupancy, pace, revenue or channel-mix report, or for a website traffic or ad performance report.
---

# Villa Analytics

Scan PMS data and (optionally) website analytics, then surface booking, occupancy and revenue trends as a short, scannable report. Works for boutique hotels, villa rentals and small multi-property setups.

## Configuration

| Setting | Value |
|---|---|
| PMS reports tool | `{{PMS_REPORTS_TOOL}}` |
| PMS property ID | `{{PMS_PROPERTY_ID}}` |
| GA4 property (optional) | `{{GA4_PROPERTY_ID}}` |
| GA4 OAuth token file (optional) | `{{GA4_TOKEN_PATH}}` |
| Snapshot sheet (optional) | `{{SHEET_ID_ANALYTICS}}` |
| Sheets CLI (optional) | `{{EMAIL_CLI}}` |

**Before anything else:** if a value above still shows double curly braces, it has not been set up.

- A required value (PMS reports tool, PMS property ID) is missing: stop, tell the operator which one, and offer to fill it in with them. Do not run a report on guessed values.
- An optional value is missing or blank: skip that part of the report and say in one line that it was skipped.

The PMS tool, the GA4 access and the sheets CLI are supplied by the operator. This skill does not ship them. If a tool is missing or errors, report the exact error and stop; do not fall back to estimated numbers.

## Standing notes

If [notes.md](notes.md) has entries, read them first and apply them (room counts, season targets, campaigns to exclude, known data quirks). When the operator gives you a lasting fact or correction during a report, offer to add it there.

## Process

### 1. Fix the period

Default: the last 30 days, plus the next 90 days for forward pace. Use the operator's period if they give one. State the exact dates at the top of the report, and use the same length for the comparison period.

### 2. Pull PMS data

Read `{{PMS_REPORTS_TOOL}}` (or its `--help`) to learn how it is called, then pull reservations for property `{{PMS_PROPERTY_ID}}`:

- **Past period:** confirmed, checked-in and checked-out reservations with at least one night inside the period.
- **Forward pace:** confirmed and in-house reservations with at least one night in the next 90 days.
- **Comparison:** the prior period of the same length. For "pace vs the same point last year", you need what was on the books on that date a year ago; most PMS exports cannot give this. If yours cannot, say so and leave the line out.

Fields needed per reservation: arrival date, departure date, room type, booking source, status, total, and the date the booking was made if available.

Rules that keep the numbers right:

- **Fetch every page.** A single page of results silently undercounts. Keep paging until the tool returns no more rows, and state the reservation count in the report.
- **Count nights, not arrivals.** A stay that starts before the period still fills nights inside it. Filter by stay overlap; if the tool only filters by arrival date, widen the window and trim the nights yourself.
- **Leave out cancelled and no-show reservations.** Show unconfirmed or tentative bookings as a separate line, not inside occupancy.
- **Say what "revenue" means.** PMS totals differ on taxes, fees and extras. Use one definition throughout and name it.

### 3. Compute the metrics

- **Occupancy** = room nights sold / room nights available, by month and by room type.
- **ADR** = room revenue / room nights sold.
- **RevPAR** = room revenue / room nights available.
- **Source mix** = share of room nights and of revenue by booking source.
- **Pace** = room nights and revenue on the books for the next 90 days, by month or week.

Occupancy and RevPAR need the number of rooms available per room type, less any out-of-service nights. Take it from the PMS tool or from `notes.md`. If neither has it, ask the operator once and offer to save the answer. Do not infer room count from the reservations.

### 4. Pull website analytics (optional)

Only if a GA4 property and token file are configured. Run GA4 Data API reports for the same period, using whatever GA4 tool the operator has. If there is none, this Python sketch shows the shape (needs the `google-analytics-data` package in a virtualenv, not system Python):

```python
import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.oauth2.credentials import Credentials

creds = Credentials.from_authorized_user_file(os.path.expanduser("{{GA4_TOKEN_PATH}}"))
client = BetaAnalyticsDataClient(credentials=creds)
PROPERTY = "{{GA4_PROPERTY_ID}}"  # format: properties/<numeric id>
```

Reports to run:

| Report | Dimension | Why |
|---|---|---|
| Overview | none | sessions, users, new users, views, average session duration, engagement rate |
| Traffic sources | `sessionSourceMedium` | where visitors come from |
| Campaigns | `sessionCampaignName` | paid campaign quality (sessions, bounce rate, duration) |
| Top pages | `pagePath` | the booking funnel: landing, availability, contact or booking |
| Countries | `country` | real markets vs junk traffic |
| Devices | `deviceCategory` | mobile vs desktop vs tablet |

If the token is expired and does not refresh, stop the GA4 part, tell the operator the token at `{{GA4_TOKEN_PATH}}` needs renewing, and deliver the PMS part of the report. Never print the contents of the token file.

### 5. Analyse

Flag what the data shows; skip a line if there is nothing to say.

- **Occupancy gaps** by month and room type, with the room nights unsold.
- **Channel concentration:** one source carrying most of the room nights or revenue.
- **ADR and RevPAR** against the prior period.
- **Pace:** forward months that look soft against the operator's targets or last year, if known.
- **Paid campaigns with a high bounce rate** (see benchmarks).
- **Suspicious country traffic:** many sessions, nearly all new users, almost no engagement.
- **Funnel drop-offs** between landing, availability and contact or booking pages.

With few rooms, small numbers swing wildly. When a figure rests on only a handful of bookings or sessions, say so instead of calling it a trend.

### 6. Report

Reply in this order, using tables for the numbers:

1. **Headline:** 2 to 3 sentences on how the property is doing.
2. **Period and data:** exact dates, reservation count, revenue definition, and anything skipped or unavailable.
3. **Occupancy, ADR, RevPAR** by month and room type, with the prior period alongside.
4. **Source mix.**
5. **Forward pace.**
6. **Website** (only if GA4 was pulled).
7. **Flags.**
8. **Recommendations:** 3 to 5 at most. Each one names the number it rests on. Typical areas: budget shifts between channels, country or audience targeting, landing-page fixes, rate or minimum-stay changes for soft weeks, partner outreach for an empty window.

Aggregates only. Do not put guest names or contact details in the report; nobody needs them to read a trend, and reports get forwarded.

### 7. Log a snapshot (optional)

Only if a snapshot sheet and a sheets CLI are configured. Show the operator the row first (date, period, occupancy %, ADR, RevPAR, sessions, bookings), then append it. With the Google Workspace CLI the call looks like this; adapt it to your own CLI:

```bash
{{EMAIL_CLI}} sheets spreadsheets values append \
  --params '{"spreadsheetId": "{{SHEET_ID_ANALYTICS}}", "range": "Snapshots!A:Z", "valueInputOption": "USER_ENTERED"}' \
  --json '{"values": [["<date>", "<period>", "<occupancy>", "<adr>", "<revpar>", "<sessions>", "<bookings>"]]}'
```

Append one row per run. Never edit or delete existing rows.

## Benchmarks

Rules of thumb, not targets. The operator's own targets in `notes.md` win.

- Paid traffic to a small-property booking site: bounce rate under 50%, average session duration over 90 seconds, conversion rate over 1% (only if conversion tracking is set up; if it is not, say so and do not estimate one).
- High season: over 80% occupancy on premium room types.

## Guardrails

- **Read-only.** Never change anything in the PMS, GA4 or an ads account. The only write this skill makes is the snapshot row in step 7, plus `notes.md` when the operator agrees.
- **Recommend, do not act.** Rate, minimum-stay and budget changes are suggestions for the operator. Do not apply them, and do not contact guests, partners or agencies.
- **No invented numbers.** Every figure comes from a tool result in this session. If data is missing, partial or looks wrong (for example occupancy above 100%), say so and show what you have.
- **Keep secrets out.** Do not read `.env` or token files into the conversation or the report.
