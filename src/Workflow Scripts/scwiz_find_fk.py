#!/usr/bin/python3
"""scwiz_find_fk — Script Filter: search assigned F-key shortcuts."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

query = sys.argv[1].strip().lower() if len(sys.argv) > 1 else ""

idx      = core.get_index()
universe = core.get_slot_universe("Fkeys")
items    = []

HINT = "↩ Unassign  ⌘↩ Change Keystroke  ⌥↩ Change Attributes  ⇧↩ Mark Unusable  ⌃↩ Revert  ⌥⌘↩ Copy  ⇧⌘↩ Banner  ⌃⇧↩ Copy Keystroke"

for ks in universe:
    row = idx.get(ks)

    if not core.is_taken(row):
        continue

    action      = row.get("action", "")
    home        = row.get("home", "")
    used_in     = row.get("used_in", "")
    description = row.get("description", "")
    key         = row.get("key", "")
    layer       = row.get("layer", "")

    if query:
        haystack = " ".join([ks, action, home, used_in, description, key, layer]).lower()
        if query not in haystack:
            continue

    title = f"{ks} - {action}/{home}/{used_in}/{description}/{key}/{layer}"
    arg   = f"{ks}/{action}/{home}/{used_in}/{description}/{key}/{layer}"

    items.append(core.alfred_item(
        title    = title,
        subtitle = HINT,
        arg      = arg,
        uid      = f"findfk_{ks}",
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
        title    = "No assigned F-key shortcuts" + (f" matching '{query}'" if query else ""),
        subtitle = "Nothing has been assigned yet",
        valid    = False,
    ))

print(core.alfred_json(items))
