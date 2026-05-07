# Skill: Villa Analytics

Scan your PMS data and (optionally) your website analytics, then surface booking, occupancy, and revenue trends. Works for boutique hotels, villa rentals, and small multi-property setups.

> **Template note:** Replace `{{PMS_*}}`, `{{GA4_PROPERTY_ID}}`, `{{SHEET_ID_ANALYTICS}}` and `{{EMAIL_CLI}}` with the values for your setup. See the README for guidance.

## Trigger

User asks to "check analytics", "how's the property doing", "traffic report", "check ad performance", "occupancy report", or similar.

## Setup

- **PMS reports tool:** `{{PMS_REPORTS_TOOL}}`
- **PMS property ID:** `{{PMS_PROPERTY_ID}}`
- **GA4 property (optional):** `{{GA4_PROPERTY_ID}}`
- **Token (optional):** `{{GA4_TOKEN_PATH}}`
- **Output sheet (optional):** `{{SHEET_ID_ANALYTICS}}`

## Process

### 1. Pull PMS data

Default period: last 30 days plus the rolling next-90-day pace (adjust based on user request).

```python
from tools.pms_api import PMSAPI  # adapter around {{PMS_REPORTS_TOOL}}
api = PMSAPI()
pid = "{{PMS_PROPERTY_ID}}"

# Reservations confirmed/checked-in/checked-out in the last 30 days
recent = api.get_reservations(pid,
    checkInFrom='YYYY-MM-DD', checkInTo='YYYY-MM-DD',
    pageSize=100,
    status='confirmed,checked_in,checked_out,not_confirmed')

# Forward-looking pace
forward = api.get_reservations(pid,
    checkInFrom='YYYY-MM-DD', checkInTo='YYYY-MM-DD',
    pageSize=100,
    status='confirmed,checked_in,not_confirmed')
```

Key fields per reservation: `startDate`, `endDate`, `guestName`, `sourceName`, `balance`, `status`, `roomTypeID`, `total`.

### 2. Pull website analytics (optional)

If `{{GA4_PROPERTY_ID}}` is configured, load credentials and run reports:

```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
from google.oauth2.credentials import Credentials
import json, os

with open(os.path.expanduser("{{GA4_TOKEN_PATH}}")) as f:
    token_data = json.load(f)

creds = Credentials(
    token=token_data['token'],
    refresh_token=token_data['refresh_token'],
    token_uri=token_data['token_uri'],
    client_id=token_data['client_id'],
    client_secret=token_data['client_secret'],
    scopes=token_data.get('scopes', []),
)

client = BetaAnalyticsDataClient(credentials=creds)
PROPERTY = "{{GA4_PROPERTY_ID}}"
```

Run these reports (default: last 30 days):

**Overview** — sessions, users, new users, page views, avg session duration, engagement rate
**Traffic sources** — by `sessionSourceMedium` — where visitors come from
**Campaign performance** — by `sessionCampaignName` — Google Ads campaign results (sessions, bounce rate, avg duration)
**Top pages** — by `pagePath` — focus on the booking funnel (landing → availability → contact)
**Country breakdown** — by `country` — identify high-value vs junk traffic markets
**Device split** — by `deviceCategory` — mobile vs desktop vs tablet

### 3. Analyse and present

Present as scannable tables. Flag:

- **Occupancy** — by month / room type. Where are the gaps? What's the revenue at risk?
- **Booking source mix** — count by `sourceName`. Are you over-dependent on any single channel?
- **Average daily rate / RevPAR trend** — vs prior period.
- **High bounce rate on paid campaigns** (>50% is bad)
- **Suspicious country traffic** (high sessions, all new users, no engagement)
- **Funnel drop-offs** (landing → availability → contact conversion)
- **Pace vs same point last year** — are forward bookings ahead, flat, or behind?

### 4. Recommendations

Based on the data, suggest:

- Budget reallocation between channels
- Country / audience targeting changes
- Landing-page improvements
- Pricing or MLOS changes for soft weeks
- Outreach to partner agencies if a specific window is empty

### 5. (Optional) Log to sheet

If `{{SHEET_ID_ANALYTICS}}` is set, append a row with the headline metrics (date, occupancy %, ADR, sessions, bookings) so trends accumulate over time:

```bash
{{EMAIL_CLI}} sheets spreadsheets values append \
  --params '{"spreadsheetId": "{{SHEET_ID_ANALYTICS}}", "range": "Snapshots!A:Z", "valueInputOption": "USER_ENTERED"}' \
  --json '{"values": [[...]]}'
```

## Key Benchmarks

For paid traffic to a small-property booking site:

- Bounce rate should be <50%
- Avg session duration should be >90s
- Conversion rate should be >1% (once tracking is set up)

For occupancy, set your own targets per season — but a useful default for high season is >80% occupancy on premium room types.

## Guardrails

- Read-only — never modify PMS, GA4, or Google Ads settings.
- If the GA4 token is expired, credentials should auto-refresh; if that fails, re-run the OAuth flow for the user.
- Use a virtualenv (`.venv/bin/python3`) — not system python — for any Google API calls.
