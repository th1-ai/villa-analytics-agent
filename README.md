# Villa Analytics Agent

A Claude Code skill for boutique-hotel and villa-rental operators. It scans your PMS data and surfaces booking, occupancy, and revenue trends — and (optionally) layers in website analytics so you can see the path from traffic to booking. Returns a scannable summary with concrete recommendations, not a 30-page dashboard.

Built on the **WAT framework** (Workflows, Agents, Tools): probabilistic AI handles reasoning, deterministic scripts handle execution.

> **About the name:** "villa-analytics" reflects the original use case (small villa + hotel hybrid). The skill works for any boutique property — single hotel, villa rental, or small multi-property operator.

---

## What it does

- **Pulls reservations** from your PMS — last 30 days plus the next 90 days of forward pace
- **Calculates the metrics that matter** — occupancy by room type, booking source mix, ADR, RevPAR, comparison with the prior period
- **Flags channel concentration** — warns if you're over-dependent on a single booking source
- **Optionally layers in GA4** — traffic by channel, campaign performance, funnel drop-offs, device/country split
- **Calls out junk traffic** — high sessions + zero engagement + suspicious country = likely bot
- **Recommends actions** — budget shifts, minimum-stay tweaks, partner-agency outreach for soft weeks. It recommends only; it never changes rates, budgets or settings.
- **Optionally logs snapshots** — appends one row of headline numbers to a Google Sheet so trends build up over time

The skill is read-only towards your PMS, GA4 and ad accounts. The snapshot row is the only thing it writes, and it shows you the row first.

---

## What you need

- [Claude Code](https://code.claude.com/docs/en/overview) installed
- **A PMS tool you supply** — a script or CLI that lists reservations from your PMS (dates, room type, source, status, total). This repo is a template: it contains the skill instructions, not the PMS integration. The examples use Cloudbeds, but any PMS with a reservation-list endpoint works.
- (Optional) A GA4 property and an OAuth token file for the GA4 Data API — only needed if you want website analytics in the report
- (Optional) A Google Sheet and a sheets CLI to log snapshots over time

---

## Quick start

1. **Clone the repo**:

   ```bash
   git clone https://github.com/th1-ai/villa-analytics-agent.git
   cd villa-analytics-agent
   ```

2. **Open Claude Code** from the project root:

   ```bash
   claude
   ```

3. **Let Claude set it up with you.** Paste this as your first message:

   > Read the README and `.claude/skills/villa-analytics/SKILL.md`, then set this skill up with me. Ask me for each placeholder value one at a time, tell me which ones are optional, and write my answers into the skill file. Do not guess any value.

   Prefer to do it by hand? See [Customising](#customising).

4. **(Optional) Copy the env template** if your own PMS or GA4 tools read credentials from `.env`:

   ```bash
   cp .env.example .env
   ```

   The skill does not read `.env`. It is there for your tools, so secrets stay out of the skill file and out of git.

5. **Ask for a report**:

   > "How is the property doing this month?"

   Claude Code picks up the `villa-analytics` skill automatically. You can also run it directly with `/villa-analytics`.

---

## Verify it works

1. In Claude Code, type `/` and check that `villa-analytics` is in the list. If it is not, you started `claude` outside the repo folder; restart it from the project root.
2. Ask "Give me an occupancy report for last month". The report must open with the exact dates and the number of reservations it read.
3. Check one number by hand against your PMS (for example, room nights sold last month). If they differ, tell Claude what the PMS shows; the usual causes are missing pages of results, cancelled bookings being counted, or taxes included in revenue.

### Troubleshooting

| Symptom | Fix |
|---|---|
| Claude says a setting has not been set up | A placeholder is still in the skill file. Run the setup prompt from the Quick start again, or fill it in by hand. |
| Claude cannot find or run the PMS tool | The path in the Configuration table must point to a script or CLI that exists on your machine. This repo does not ship one. |
| No occupancy or RevPAR in the report | The skill needs your room count per room type. Tell Claude, and let it save the answer to `notes.md`. |
| GA4 section is skipped | The GA4 property or token path is blank, or the token has expired and needs renewing. The PMS part still runs. |
| No "pace vs last year" line | Your PMS tool cannot return what was on the books a year ago. The skill leaves the line out instead of guessing. |

---

## File structure

```
villa-analytics-agent/
├── README.md                                        # This file
├── .env.example                                     # Credentials template for your own tools
├── .gitignore
├── LICENSE
└── .claude/
    └── skills/
        └── villa-analytics/
            ├── SKILL.md                             # The skill definition
            └── notes.md                             # Your standing notes (room counts, targets, exclusions)
```

---

## Customising

The skill file uses placeholders so it can be adapted to any PMS + analytics stack. Replace the following in [`.claude/skills/villa-analytics/SKILL.md`](.claude/skills/villa-analytics/SKILL.md) before the first run:

| Placeholder | What to put | Example |
|---|---|---|
| `{{PMS_REPORTS_TOOL}}` | Your script or CLI that lists reservations from your PMS | `tools/cloudbeds_api.py` |
| `{{PMS_PROPERTY_ID}}` | Property ID in your PMS | `123456789` |
| `{{GA4_PROPERTY_ID}}` | GA4 property ID (optional) | `properties/123456789` |
| `{{GA4_TOKEN_PATH}}` | Path to the OAuth token JSON (optional) | `~/.config/gws/analytics_token.json` |
| `{{SHEET_ID_ANALYTICS}}` | Google Sheet for snapshots (optional) | `1AbCdEf...` |
| `{{EMAIL_CLI}}` | Command-line tool that can append to Google Sheets (optional) | `gws` |

The example values are illustrations; yours will differ. For an optional item you do not use, leave the placeholder as it is and the skill skips that part.

You can use any text editor, or one `sed` pass:

```bash
# macOS. On Linux, use `sed -i` without the empty quotes.
sed -i '' \
  -e 's|{{PMS_REPORTS_TOOL}}|tools/cloudbeds_api.py|g' \
  -e 's|{{PMS_PROPERTY_ID}}|123456789|g' \
  -e 's|{{GA4_PROPERTY_ID}}|properties/123456789|g' \
  -e 's|{{GA4_TOKEN_PATH}}|~/.config/gws/analytics_token.json|g' \
  .claude/skills/villa-analytics/SKILL.md
```

The snapshot sheet needs a tab named `Snapshots`.

---

## How memory works

The skill keeps its standing notes in [`.claude/skills/villa-analytics/notes.md`](.claude/skills/villa-analytics/notes.md) and reads that file before each report. Use it for facts that stay true between reports: rooms per room type, season targets, what your PMS counts as revenue, or "campaign X always drives bot traffic — exclude it from the channel report". Add a line yourself, or tell Claude during a report and it will offer to add it.

---

## Related agents

This skill works well alongside:

- [`marketing-report-agent`](https://github.com/th1-ai/marketing-report-agent) — produces a 2-page Google Doc using the same data sources, formatted for monthly review
- [`dynamic-pricing-agent`](https://github.com/th1-ai/dynamic-pricing-agent) — proposes rate and minimum-stay changes for you to approve; a natural next step when this skill shows soft weeks
- [`morning-routine-agent`](https://github.com/th1-ai/morning-routine-agent) — the daily operational sweep; this skill is the deeper periodic review
- [`crm-pipeline-agent`](https://github.com/th1-ai/crm-pipeline-agent) — tracks the inquiry funnel that the analytics shows ending in a booking

The full set of 21 agents is at [th1.ai/agent-stack](https://th1.ai/agent-stack).

---

## License

MIT — see [LICENSE](LICENSE).
