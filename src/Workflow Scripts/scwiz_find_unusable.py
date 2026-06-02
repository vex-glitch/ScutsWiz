#!/usr/bin/python3
"""scwiz_find_unusable — Script Filter: list all unusable entries sorted by keystroke."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

query = sys.argv[1].strip().lower() if len(sys.argv) > 1 else ""

rows = [r for r in core.read_ssot() if core.is_unusable(r)]

# Sort alphabetically by keystroke
rows.sort(key=lambda r: r.get("keystroke", "").lower())

# Live filter
if query:
    rows = [r for r in rows if query in r.get("keystroke", "").lower()]

HINT  = "↩ Unassign  ⌘↩ Change Keystroke  ⌥↩ Change Attributes  ⇧↩ Mark Unusable  ⌃↩ Revert  ⌥⌘↩ Copy  ⇧⌘↩ Banner  ⌃⇧↩ Copy Keystroke"
items = []

for row in rows:
    ks  = row.get("keystroke", "")
    arg = f"{ks}/XXX/XXX/XXX/XXX/XXX/XXX"

    items.append(core.alfred_item(
        title    = f"{ks} - XXX/XXX/XXX/XXX/XXX/XXX",
        subtitle = HINT,
        arg      = arg,
        uid      = f"unusable_{ks}",
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
        title    = "No unusable entries" + (f" matching '{query}'" if query else ""),
        subtitle = "",
        valid    = False,
    ))

print(core.alfred_json(items))
