# Villa Analytics Agent

A Claude Code skill for boutique-hotel and villa-rental operators. It scans your PMS data and surfaces booking, occupancy, and revenue trends — and (optionally) layers in website analytics so you can see the path from traffic to booking. Returns a scannable summary with concrete recommendations, not a 30-page dashboard.

Built on the **WAT framework** (Workflows, Agents, Tools): probabilistic AI handles reasoning, deterministic scripts handle execution.

> **About the name:** "villa-analytics" reflects the original use case (small villa + hotel hybrid). The skill works for any boutique property — single hotel, villa rental, or small multi-property operator.

---

## What it does

- **Pulls reservations** from your PMS — last 30 days plus forward pace
- **Calculates the metrics that matter** — occupancy by room type, booking source mix, ADR, RevPAR, pace vs prior period
- **Flags channel concentration** — warns if you're over-dependent on a single OTA
- **Optionally layers in GA4** — traffic by channel, campaign performance, funnel drop-offs, device/country split
- **Calls out junk traffic** — high sessions + zero engagement + suspicious country = likely bot
- **Recommends actions** — budget shifts, MLOS tweaks, partner-agency outreach for soft weeks
- **Optionally logs snapshots** — appends headline numbers to a Google Sheet so trends build up over time

---

## What you need

- [Claude Code](https://claude.ai/code) installed
- A PMS with API access — the agent calls a reservations-list endpoint and reads guest/source/room data. The reference setup uses Cloudbeds, but any PMS with similar endpoints works.
- (Optional) A GA4 property and an OAuth token file — only needed if you want website analytics in the report
- (Optional) A Google Sheet to log snapshots over time

---

## Quick start

1. **Clone the repo** into a Claude Code project:

   ```bash
   git clone https://github.com/th1-ai/villa-analytics-agent.git
   cd villa-analytics-agent
   ```

2. **Copy the env template** and fill it in:

   ```bash
   cp .env.example .env
   ```

3. **Edit [`.claude/skills/villa-analytics/SKILL.md`](.claude/skills/villa-analytics/SKILL.md)** — replace placeholders described in [Customising](#customising) with your tooling.

4. **Open in Claude Code** from the project root:

   ```bash
   claude
   ```

5. **Invoke the skill**:

   > "How is the property doing this month?"

   Claude Code will pick up the `villa-analytics` skill automatically.

---

## File structure

```
villa-analytics-agent/
├── README.md                                        # This file
├── .env.example                                     # PMS auth, GA4, sheet IDs
├── .gitignore
├── LICENSE
└── .claude/
    └── skills/
        └── villa-analytics/
            └── SKILL.md                             # The skill definition
```

---

## Customising

The skill file uses placeholders so it can be adapted to any PMS + analytics stack. Replace the following before first run:

| Placeholder | What to put | Example |
|---|---|---|
| `{{PMS_LOOKUP_TOOL}}` | Script that looks up reservations | `tools/lookup_guest.py` |
| `{{PMS_REPORTS_TOOL}}` | Script/library wrapping your PMS API | `tools/cloudbeds_api.py` |
| `{{PMS_PROPERTY_ID}}` | Property ID in your PMS | `123456789` |
| `{{GA4_PROPERTY_ID}}` | GA4 property ID (optional) | `properties/123456789` |
| `{{GA4_TOKEN_PATH}}` | Path to OAuth token JSON (optional) | `~/.config/gws/analytics_token.json` |
| `{{SHEET_ID_ANALYTICS}}` | Google Sheet for snapshots (optional) | `1AbCdEf...` |
| `{{EMAIL_CLI}}` | Command-line wrapper for sheets | `gws` |

Reference example tool paths from a Cloudbeds-based reference setup: `tools/cloudbeds_api.py`. Yours will differ.

You can do this with any text editor or with one `sed` pass:

```bash
sed -i '' \
  -e 's|{{PMS_REPORTS_TOOL}}|tools/cloudbeds_api.py|g' \
  -e 's|{{PMS_PROPERTY_ID}}|123456789|g' \
  -e 's|{{GA4_PROPERTY_ID}}|properties/123456789|g' \
  .claude/skills/villa-analytics/SKILL.md
```

---

## How memory works

This is a skill-only repo, so there's no per-skill memory folder by default. If you want persistent learnings (e.g. "campaign X always drives bot traffic — exclude it from the channel report"), add a `.claude/agent-memory/villa-analytics/` folder and write short notes there — Claude Code will pick them up automatically.

---

## Related agents

This skill works well alongside:

- [`marketing-report-agent`](https://github.com/th1-ai/marketing-report-agent) — produces a 2-page Google Doc using the same data sources, formatted for monthly review
- [`dynamic-pricing-agent`](https://github.com/th1-ai/dynamic-pricing-agent) — uses the occupancy/pace numbers this skill surfaces to recommend rate and MLOS changes
- [`morning-routine-agent`](https://github.com/th1-ai/morning-routine-agent) — pulls a daily snapshot using a subset of these metrics
- [`crm-pipeline-agent`](https://github.com/th1-ai/crm-pipeline-agent) — tracks the inquiry funnel that the analytics shows ending in a booking

---

## License

MIT — see [LICENSE](LICENSE).
