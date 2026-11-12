# runs/

The `villa-analytics` skill keeps its memory here. Everything in this folder except this file is ignored by git, because it holds your property's figures.

| File | Written at | What it is |
|---|---|---|
| `LOG.md` | Level 1 and up | One entry per scheduled run, newest last. The latest run summary is the last entry; other agents read that entry, not a separate file. The skill reads the last entries before it acts, so it does not repeat work. |
| `handoff/villa-analytics-agent.md` | Level 2 and up | The latest figures for sibling agents. Replaced on each run. |
| `.snapshot-days` | Level 3 | Written by the guard hook: the days on which a snapshot row was allowed. |

## `LOG.md` entry format

```markdown
## 2026-01-05T07:00:12+01:00
- Level: 1 (scheduled)
- Checked: PMS 2025-12-06 to 2026-01-04 (212 reservations, all pages), pace to 2026-04-04, GA4 skipped (not configured)
- Headline: occupancy 71%, ADR 240, RevPAR 170 (room revenue excl. tax)
- Actions taken: none
- Actions proposed: snapshot row [2026-01-05, 30d, 71%, 240, 170, -, 212]
- Errors: none
- Needs you: March pace 38% against a 60% target
```

"Actions taken" lists each write with an id you can check, for example the sheet range the row landed in. A shadow run writes `shadow: would append ...` there. A stopped run is one line, for example `- Level: PAUSED (scheduled), skipped: AUTONOMY.md has no valid Level line`.

## `handoff/villa-analytics-agent.md` format

```markdown
# Handoff: villa-analytics-agent
Generated: 2026-01-05T07:00:12+01:00 by villa-analytics (Level 2)
Period: 2025-12-06 to 2026-01-04. Revenue = room revenue excl. tax.

## Headline
| Metric | This period | Prior period |
|---|---|---|
| Occupancy | 71% | 66% |

## Soft weeks (next 90 days)
| Week starting | Room type | Occupancy on the books | Room nights unsold | Target |
|---|---|---|---|---|
| 2026-03-02 | Garden Room | 21% | 22 | 60% |

## Source mix
| Source | Room nights | Revenue |
|---|---|---|
```

Aggregates only. No guest names or contact details. The figures above are invented examples.
