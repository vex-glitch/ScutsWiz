#!/usr/bin/python3
"""scwiz_do_restore — Execute Script: revert a keystroke to its previous state.

Receives from Alfred:
  argv[1] — current row, e.g. "F1/Revert/Claude/Script/S/1"
             keystroke is everything before the first /

Finds the most recent log entry for that keystroke, uses its timestamp as the
anchor, then collects all log entries within 3 seconds of it (same window logic
as undo) and reverses them all. This correctly handles both:
  - Change Attributes: only the one keystroke in the window
  - Change Keystroke:  old keystroke (delete) + new keystroke (assign) both in window
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

WINDOW_SECONDS = 3


def parse_log_fields(s: str) -> dict:
    content = s.split(": ", 1)[1] if ": " in s else ""
    if not content.strip():
        return {}
    result = {}
    for part in content.split(" | "):
        if "=" in part:
            k, v = part.split("=", 1)
            result[k.strip()] = v.strip()
    return result


def parse_ts(s: str):
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None


def reverse_entry(entry: dict) -> None:
    op  = entry["operation"]
    ks  = entry["keystroke"]
    old = parse_log_fields(entry.get("old", ""))
    new = parse_log_fields(entry.get("new", ""))

    if op == "assign":
        if not old:
            core.delete_slot(ks)
        else:
            core.assign_slot(ks,
                old.get("action", ""), old.get("home", ""), old.get("used_in", ""),
                description=old.get("description", ""),
                key=old.get("key", ""), layer=old.get("layer", ""))

    elif op == "delete":
        core.assign_slot(ks,
            old.get("action", ""), old.get("home", ""), old.get("used_in", ""),
            description=old.get("description", ""),
            key=old.get("key", ""), layer=old.get("layer", ""))

    elif op == "change_key":
        new_ks = new.get("keystroke", "")
        if new_ks:
            core.update_keystroke(new_ks, ks)

    elif op in ("change_attr", "clear", "unusable"):
        if not old:
            core.delete_slot(ks)
        else:
            core.assign_slot(ks,
                old.get("action", ""), old.get("home", ""), old.get("used_in", ""),
                description=old.get("description", ""),
                key=old.get("key", ""), layer=old.get("layer", ""))


# ── Main ──────────────────────────────────────────────────────────────────────

text = sys.argv[1].strip() if len(sys.argv) > 1 else ""

if not text:
    print("ERROR: no input received")
    sys.exit(1)

# Keystroke is everything before the first /
keystroke = text.split("/", 1)[0].strip()

if not keystroke:
    print(f"ERROR: cannot parse keystroke from: {text!r}")
    sys.exit(1)

# Find the most recent log entry for this keystroke to use as the time anchor
history = core.get_keystroke_history(keystroke)

if not history:
    print(f"ERROR: no log history found for {keystroke}")
    sys.exit(1)

anchor_ts = parse_ts(history[0]["timestamp"])

if not anchor_ts:
    print("ERROR: cannot parse timestamp from log")
    sys.exit(1)

# Collect all log entries (any keystroke) within the time window of the anchor
all_entries = core.get_recent_changes(n=50)
group = [e for e in all_entries
         if (ts := parse_ts(e["timestamp"])) and
         abs((anchor_ts - ts).total_seconds()) <= WINDOW_SECONDS]

if not group:
    print(f"ERROR: no log entries found near {anchor_ts}")
    sys.exit(1)

# Reverse all entries in the group
for entry in group:
    reverse_entry(entry)

if len(group) == 1:
    print(f"✓ Reverted {group[0]['keystroke']}")
else:
    keystrokes = ", ".join(dict.fromkeys(e["keystroke"] for e in group))
    print(f"✓ Reverted {len(group)} changes ({keystrokes})")
