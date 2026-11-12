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
- **Can run on its own** — on a schedule, at the autonomy level you set in [`AUTONOMY.md`](AUTONOMY.md). It keeps a run log, tells you only what needs you, and leaves a summary file for sibling agents. See [Run it on its own](#run-it-on-its-own).

The skill is read-only towards your PMS, GA4 and ad accounts at every level. The snapshot row is the only thing it writes outside this folder. When you ask for a report yourself, it shows you the row first; on a schedule it appends the row by itself only at Level 3.

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
| A scheduled run says a command was blocked or denied | Expected below the level that allows it; the report names the level. If your PMS tool is denied, the `allow` rule in `.claude/settings.scheduled.json` does not match how the tool is run. |
| A scheduled run stops at once | `AUTONOMY.md` says `Level: 0` or `Level: PAUSED`, or it is missing or has no valid `Level:` line (that counts as PAUSED). |
| No "pace vs last year" line | Your PMS tool cannot return what was on the books a year ago. The skill leaves the line out instead of guessing. |

---

## File structure

```
villa-analytics-agent/
├── README.md                                        # This file
├── AUTONOMY.md                                      # The autonomy level and limits. You edit it; the skill obeys it
├── .env.example                                     # Credentials template for your own tools
├── .gitignore
├── LICENSE
├── runs/
│   ├── README.md                                    # Format of the run log and the handoff file
│   └── .gitkeep                                     # LOG.md and handoff/ appear here; git ignores them
└── .claude/
    ├── settings.example.json                        # Example permissions and hook for scheduled runs
    ├── hooks/
    │   └── autonomy-guard.py                        # Blocks scheduled writes that AUTONOMY.md does not allow
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

`{{PMS_REPORTS_TOOL}}` and `{{EMAIL_CLI}}` also appear in [`.claude/settings.example.json`](.claude/settings.example.json). You fill those in on your own copy of that file; see [Run it on its own](#run-it-on-its-own).

---

## Run it on its own

Out of the box the skill runs when you ask. You can also let it run on a schedule. [`AUTONOMY.md`](AUTONOMY.md) sets how much it does by itself:

| Level | What a scheduled run does |
|---|---|
| PAUSED | Nothing. It logs why and stops. A missing file or an invalid `Level:` line counts as PAUSED. |
| 0 | Nothing. Scheduled runs stop at the start. |
| 1 (default) | Reads the PMS and GA4, prints the report, adds an entry to `runs/LOG.md`. |
| 2 | Also writes `runs/handoff/villa-analytics-agent.md` and proposes the snapshot row for your approval. |
| 3 | Also appends the snapshot row to your sheet: 1 row per day, append only, not when a check failed. |

No level lets it write to the PMS, change a rate or a budget, or contact anyone. The full action table, the guard rails and the list of what interrupts you are in `AUTONOMY.md`.

### 1. Make your settings file for scheduled runs

```bash
cp .claude/settings.example.json .claude/settings.scheduled.json
```

Open `.claude/settings.scheduled.json` and replace the two placeholders in the `allow` list. A rule must match the command the way Claude runs it. If your PMS tool is run as `python3 tools/cloudbeds_api.py ...`, the rule is `Bash(python3 tools/cloudbeds_api.py *)`. If you have no snapshot sheet, delete the two `sheets` lines. Leave no `{{...}}` in the file: in our test, a run with a placeholder still in it was refused the write to its own run log. If you use GA4, add one `Bash(...)` rule for your GA4 command; without one, a scheduled run skips the website section.

What the file does:

- **allow:** your PMS tool, the snapshot append command and the read-back of the row, and edits under `runs/`. Nothing else is pre-approved.
- **deny:** reading `.env`, editing `AUTONOMY.md` or anything under `.claude/` (the agent cannot raise its own level), `rm`, `curl`, `wget`, `git push`, and web access. Deny rules match the command text; they are a seat belt, not a sandbox.
- **hook:** [`autonomy-guard.py`](.claude/hooks/autonomy-guard.py) runs before every shell command. It blocks all commands when `AUTONOMY.md` is at `Level: PAUSED` or `Level: 0` (a missing file, a missing or repeated `Level:` line and an unknown value count as PAUSED), blocks a spreadsheet write below Level 3, and allows 1 spreadsheet write per day at Level 3. It needs `python3`.

The file is loaded only by the command below, so cloning this repo or working in it by hand is not affected.

### 2. Run it once by hand

```bash
cd /path/to/villa-analytics-agent
claude -p "/villa-analytics This is a scheduled run. Follow AUTONOMY.md." \
  --settings .claude/settings.scheduled.json \
  --permission-mode dontAsk \
  --max-turns 40 \
  < /dev/null > runs/last-run.txt
```

`-p` runs Claude Code without a chat window. `--permission-mode dontAsk` refuses everything your settings file does not allow, instead of waiting for an answer nobody will give. `--max-turns` stops a run that goes in circles. Read `runs/last-run.txt` and `runs/LOG.md`. The report must open with "Needs you".

### 3. Put it on a schedule

Example for cron on macOS or Linux (`crontab -e`), every Monday at 07:00. Use the full path that `which claude` prints, because cron has a short `PATH`:

```cron
0 7 * * 1 cd /path/to/villa-analytics-agent && /full/path/to/claude -p "/villa-analytics This is a scheduled run. Follow AUTONOMY.md." --settings .claude/settings.scheduled.json --permission-mode dontAsk --max-turns 40 < /dev/null > runs/last-run.txt 2>&1
```

This is an example. The command and the hook were tested by hand; your cron, your login and your tools were not. After the first scheduled run, check that `runs/last-run.txt` holds a report and not a login error. Weekly is enough for this report; daily is the most the guard rails expect. Claude Code also has its own scheduling options; see [the scheduling docs](https://code.claude.com/docs/en/scheduled-tasks).

A personal Pro or Max plan's limits assume ordinary individual use under Anthropic's Usage Policy, so for heavy or business-critical schedules use an API key or a team plan.

### 4. Move up one level at a time

1. Run at the current level for 2 weeks (at least 3 runs).
2. Read `runs/LOG.md`. Check one figure per run against your PMS, and check that every "Needs you" item was real.
3. Change the one `Level:` line in `AUTONOMY.md`. The first 3 runs at the new level are shadow runs: they log what they would do and do not do it.

To stop everything, change the line to `Level: PAUSED` (or `Level: 0`).

### Where the output goes

| File | For whom |
|---|---|
| `runs/last-run.txt` | You: the full text of the last report. |
| `runs/LOG.md` | You and [`morning-routine-agent`](https://github.com/th1-ai/morning-routine-agent): one entry per run, with "Needs you". The latest run summary is the last entry. |
| `runs/handoff/villa-analytics-agent.md` (Level 2+) | [`dynamic-pricing-agent`](https://github.com/th1-ai/dynamic-pricing-agent) (soft weeks) and [`marketing-report-agent`](https://github.com/th1-ai/marketing-report-agent) (headline, source mix). Point those agents at this file; they do not find it by themselves. |

Formats are in [`runs/README.md`](runs/README.md).

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
