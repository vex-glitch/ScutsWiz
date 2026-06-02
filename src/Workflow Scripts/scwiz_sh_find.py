#!/usr/bin/python3
"""scwiz_sh_find — Script Filter: search shorthands across all fields.
↩ → edit   ⌃↩ → delete   ⌥⌘↩ → copy shorthand to clipboard
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

query = sys.argv[1].strip().lower() if len(sys.argv) > 1 else ""

rows = core.read_shorthands()
rows.sort(key=lambda r: r.get("shorthand", "").lower())

HINT = "↩ Edit  ·  ⌃↩ Delete  ·  ⌥⌘↩ Copy"

items = []

for row in rows:
    shorthand   = row.get("shorthand", "")
    action      = row.get("action", "")
    used_in     = row.get("used_in", "")
    description = row.get("description", "")

    if query:
        haystack = " ".join([shorthand, action, used_in, description]).lower()
        if query not in haystack:
            continue

    parts    = [p for p in [action, used_in, description] if p]
    subtitle = "  ·  ".join(parts) if parts else ""
    arg      = f"{shorthand}/{action}/{used_in}/{description}"

    items.append(core.alfred_item(
        title    = shorthand,
        subtitle = (subtitle + "  —  " if subtitle else "") + HINT,
        arg      = arg,
        uid      = f"shfind_{shorthand}",
        valid    = True,
        mods     = {
            "ctrl":    {"valid": True, "arg": arg, "subtitle": "⌃↩  Delete shorthand"},
            "cmd+alt": {"valid": True, "arg": arg, "subtitle": "⌥⌘↩  Copy to Clipboard"},
        },
    ))

if not items:
    items.append(core.alfred_item(
        title    = "No shorthands found" + (f" matching '{query}'" if query else ""),
        subtitle = "Nothing has been saved yet",
        valid    = False,
    ))

print(core.alfred_json(items))
