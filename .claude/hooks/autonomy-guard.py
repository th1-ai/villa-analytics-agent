#!/usr/bin/env python3
"""PreToolUse guard for scheduled runs of the villa-analytics skill.

Reads the hook JSON from stdin and AUTONOMY.md from the project root.
Exit 0 = no decision (normal permission rules apply). Exit 2 = block; the
reason on stderr is shown to Claude.

Rules, for Bash calls only:
  1. AUTONOMY.md at Level PAUSED or Level 0: block every command. A missing
     file, no Level line, two Level lines or an unknown value count as PAUSED.
  2. A spreadsheet write (append/update/clear/batchUpdate) below Level 3: block.
  3. A spreadsheet write at Level 3: allow one per calendar day, then block.
"""
import datetime
import json
import os
import re
import sys

SHEET_WRITE = re.compile(
    r"sheets?\b.*\b(append|update|batchupdate|clear|delete)\b", re.IGNORECASE | re.DOTALL
)


def block(reason):
    print("autonomy-guard: " + reason, file=sys.stderr)
    sys.exit(2)


def read_level(root):
    """Return 0-3, or None for PAUSED.

    AUTONOMY.md has exactly one line "Level: <value>". A missing file, a missing
    line, more than one line or an unknown value all count as PAUSED.
    """
    try:
        with open(os.path.join(root, "AUTONOMY.md"), encoding="utf-8") as fh:
            values = re.findall(r"^Level:[ \t]*(\S*)[ \t]*$", fh.read(), re.MULTILINE)
    except OSError:
        return None
    if len(values) == 1 and values[0] in ("0", "1", "2", "3"):
        return int(values[0])
    return None


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        block("could not read the hook input, so the call is refused.")
    if event.get("tool_name") != "Bash":
        sys.exit(0)
    command = (event.get("tool_input") or {}).get("command") or ""
    root = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()

    level = read_level(root)
    if level is None or level == 0:
        block(
            "AUTONOMY.md is PAUSED (or has no valid Level line) or at Level 0. "
            "Scheduled runs are stopped. Do not retry; end the run."
        )
    if not SHEET_WRITE.search(command):
        sys.exit(0)
    if level < 3:
        block(
            "a spreadsheet write needs Level 3 and AUTONOMY.md says Level %d. "
            "Put the row in the report as a proposal instead." % level
        )
    state = os.path.join(root, "runs", ".snapshot-days")
    today = datetime.date.today().isoformat()
    try:
        with open(state, encoding="utf-8") as fh:
            done = fh.read().split()
    except OSError:
        done = []
    if today in done:
        block("the daily limit of 1 snapshot write is used for %s. Do not retry." % today)
    try:
        os.makedirs(os.path.dirname(state), exist_ok=True)
        with open(state, "a", encoding="utf-8") as fh:
            fh.write(today + "\n")
    except OSError:
        block("could not record the snapshot write in runs/.snapshot-days, so it is refused.")
    sys.exit(0)


if __name__ == "__main__":
    main()
