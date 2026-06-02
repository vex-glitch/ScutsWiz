#!/usr/bin/python3
"""scwiz_recent — Script Filter: last 10 modified entries in the SSOT TSV.
Rows are sorted by modified_at descending (most recent first).

↩       → Unassign
⌘↩      → Change Keystroke
⌥↩      → Change Attributes
⌥⌘↩     → Mark Unusable
⌃↩      → Copy to Clipboard
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

query = sys.argv[1].strip().lower() if len(sys.argv) > 1 else ""

rows = core.read_ssot()

# Keep only rows that have been touched (have a modified_at timestamp)
rows = [r for r in rows if r.get("modified_at", "").strip()]

# Sort newest first
rows.sort(key=lambda r: r.get("modified_at", ""), reverse=True)

# Take top 10
rows = rows[:10]

HINT = "↩ Unassign  ⌘↩ Change Keystroke  ⌥↩ Change Attributes  ⇧↩ Mark Unusable  ⌃↩ Revert  ⌥⌘↩ Copy  ⇧⌘↩ Banner"

items = []

for row in rows:
    ks          = row.get("keystroke", "")
    action      = row.get("action", "")
    home        = row.get("home", "")
    used_in     = row.get("used_in", "")
    description = row.get("description", "")
    key         = row.get("key", "")
    layer       = row.get("layer", "")

    # Live text filter across all visible fields
    if query:
        haystack = " ".join([ks, action, home, used_in, description, key, layer]).lower()
        if query not in haystack:
            continue

    # Title: "F1 ⌘ - Working/Alfred//S/1"  (unusable shown plainly)
    if action == "XXX":
        title = f"{ks} - unusable"
    else:
        title = f"{ks} - {action}/{home}/{used_in}/{description}/{key}/{layer}"

    # arg carries the full row for all downstream actions
    arg = f"{ks}/{action}/{home}/{used_in}/{description}/{key}/{layer}"

    items.append(core.alfred_item(
        title    = title,
        subtitle = HINT,
        arg      = arg,
        uid      = f"recent_{ks}",
        valid    = True,
        mods     = {
            "cmd":     {"valid": True, "arg": arg, "subtitle": "⌘↩  Change Keystroke"},
            "alt":     {"valid": True, "arg": arg, "subtitle": "⌥↩  Change Attributes"},
            "shift":   {"valid": True, "arg": arg, "subtitle": "⇧↩  Mark Unusable"},
            "ctrl":    {"valid": True, "arg": arg, "subtitle": "⌃↩  Revert"},
            "cmd+alt": {"valid": True, "arg": arg, "subtitle": "⌥⌘↩  Copy to Clipboard"},
        },
    ))

if not items:
    items.append(core.alfred_item(
        title    = "No recent changes" + (f" matching '{query}'" if query else ""),
        subtitle = "Nothing has been assigned yet",
        valid    = False,
    ))

print(core.alfred_json(items))
