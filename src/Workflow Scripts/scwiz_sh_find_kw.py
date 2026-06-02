#!/usr/bin/python3
"""scwiz_sh_find_kw — Script Filter: search shorthands by keyword/abbreviation text.
Filters on the shorthand field only.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

HINT = "⏎ Unassign  ·  ⌘⏎ Change Shorthand  ·  ⌥⏎ Change Attributes  ·  ⌘⇧ Banner  ·  ⌥⌘ Copy"

query = sys.argv[1].strip().lower() if len(sys.argv) > 1 else ""

rows = core.read_shorthands()
rows.sort(key=lambda r: r.get("shorthand", "").lower())

items = []

for row in rows:
    shorthand   = row.get("shorthand", "")
    action      = row.get("action", "")
    used_in     = row.get("used_in", "")
    description = row.get("description", "")

    if query and query not in shorthand.lower():
        continue

    parts = [p for p in [action, used_in, description] if p]
    title = "  ·  ".join([shorthand] + parts)
    arg   = f"{shorthand}/{action}/{used_in}/{description}"

    items.append(core.alfred_item(
        title    = title,
        subtitle = HINT,
        arg      = arg,
        uid      = f"shkw_{shorthand}",
        valid    = True,
    ))

if not items:
    items.append(core.alfred_item(
        title    = "No shorthands found" + (f" matching '{query}'" if query else ""),
        subtitle = "Nothing has been saved yet",
        valid    = False,
    ))

print(core.alfred_json(items))
