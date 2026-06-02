#!/usr/bin/python3
"""scwiz_sh_undo — Execute Script: undo the last shorthand change(s) within a 3-second window.

Reads the shorthands log newest-first, groups all entries whose timestamps fall
within WINDOW_SECONDS of the most recent entry, and reverses each one.
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
    op        = entry["operation"]
    shorthand = entry["shorthand"]
    old       = parse_log_fields(entry.get("old", ""))

    if op == "assign":
        if not old:
            # Brand-new row was created — remove it
            core.delete_shorthand(shorthand)
        else:
            # Existing row was overwritten — restore old values
            core.assign_shorthand(shorthand,
                old.get("action", ""), old.get("used_in", ""),
                old.get("description", ""))

    elif op == "delete":
        # Row was deleted — re-insert with old values
        core.assign_shorthand(shorthand,
            old.get("action", ""), old.get("used_in", ""),
            old.get("description", ""))


# ── Main ──────────────────────────────────────────────────────────────────────

entries = core.get_recent_shorthand_changes(n=20)

if not entries:
    print("Nothing to undo")
    sys.exit(0)

anchor_ts = parse_ts(entries[0]["timestamp"])
if not anchor_ts:
    print("ERROR: cannot parse timestamp from log")
    sys.exit(1)

group = []
for entry in entries:
    ts = parse_ts(entry["timestamp"])
    if ts and abs((anchor_ts - ts).total_seconds()) <= WINDOW_SECONDS:
        group.append(entry)
    else:
        break

for entry in group:
    reverse_entry(entry)

if len(group) == 1:
    print(f"✓ Undid {group[0]['operation']} → {group[0]['shorthand']}")
else:
    shorthands = ", ".join(dict.fromkeys(e["shorthand"] for e in group))
    print(f"✓ Undid {len(group)} changes → {shorthands}")
