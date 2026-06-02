#!/usr/bin/python3
"""scwiz_do_undo — Execute Script: undo the last change(s) within a 3-second window.

Reads the log newest-first, groups all entries whose timestamps fall within
WINDOW_SECONDS of the most recent entry, and reverses each one in order.
This means a multi-step operation (e.g. delete + assign from Change Keystroke)
is treated as a single undoable action.
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

WINDOW_SECONDS = 3


def parse_log_fields(s: str) -> dict:
    """Parse 'OLD: key=val | key=val ...' or 'NEW: ...' into a plain dict."""
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
            # Brand-new row was created — remove it
            core.delete_slot(ks)
        else:
            # Existing row was overwritten — restore old values
            core.assign_slot(ks,
                old.get("action", ""), old.get("home", ""), old.get("used_in", ""),
                description=old.get("description", ""),
                key=old.get("key", ""), layer=old.get("layer", ""))

    elif op == "delete":
        # Row was deleted — re-insert with old values
        core.assign_slot(ks,
            old.get("action", ""), old.get("home", ""), old.get("used_in", ""),
            description=old.get("description", ""),
            key=old.get("key", ""), layer=old.get("layer", ""))

    elif op == "change_key":
        # Keystroke was renamed old_ks → new_ks; rename it back
        new_ks = new.get("keystroke", "")
        if new_ks:
            core.update_keystroke(new_ks, ks)  # new_ks back to old ks

    elif op in ("change_attr", "clear", "unusable"):
        # Attributes were changed — restore old values
        if not old:
            core.delete_slot(ks)
        else:
            core.assign_slot(ks,
                old.get("action", ""), old.get("home", ""), old.get("used_in", ""),
                description=old.get("description", ""),
                key=old.get("key", ""), layer=old.get("layer", ""))


# ── Main ──────────────────────────────────────────────────────────────────────

entries = core.get_recent_changes(n=20)

if not entries:
    print("Nothing to undo")
    sys.exit(0)

anchor_ts = parse_ts(entries[0]["timestamp"])
if not anchor_ts:
    print("ERROR: cannot parse timestamp from log")
    sys.exit(1)

# Collect all entries within the time window
group = []
for entry in entries:
    ts = parse_ts(entry["timestamp"])
    if ts and abs((anchor_ts - ts).total_seconds()) <= WINDOW_SECONDS:
        group.append(entry)
    else:
        break  # log is newest-first; once outside the window we're done

# Reverse in order — newest first, so the last sub-action is undone first
for entry in group:
    reverse_entry(entry)

# Confirmation output for Post Notification
if len(group) == 1:
    print(f"✓ Undid {group[0]['operation']} → {group[0]['keystroke']}")
else:
    keystrokes = ", ".join(dict.fromkeys(e["keystroke"] for e in group))
    print(f"✓ Undid {len(group)} changes → {keystrokes}")
