#!/usr/bin/python3
"""scwiz_sh_recent — Script Filter: last 10 modified shorthands.

⏎       → Unassign
⌘⏎      → Change Shorthand
⌥⏎      → Change Attributes
⌘⇧      → Banner
⌥⌘      → Copy
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

query = sys.argv[1].strip().lower() if len(sys.argv) > 1 else ""

rows = core.read_shorthands()
rows = [r for r in rows if r.get("modified_at", "").strip()]
rows.sort(key=lambda r: r.get("modified_at", ""), reverse=True)
rows = rows[:10]

HINT = "⏎ Unassign  ·  ⌘⏎ Change Shorthand  ·  ⌥⏎ Change Attributes  ·  ⌘⇧ Banner  ·  ⌥⌘ Copy"

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

    parts = [p for p in [action, used_in, description] if p]
    title = "  ·  ".join([shorthand] + parts)
    arg   = f"{shorthand}/{action}/{used_in}/{description}"

    items.append(core.alfred_item(
        title    = title,
        subtitle = HINT,
        arg      = arg,
        uid      = f"shrecent_{shorthand}",
        valid    = True,
    ))

if not items:
    items.append(core.alfred_item(
        title    = "No recent shorthands" + (f" matching '{query}'" if query else ""),
        subtitle = "Nothing has been saved yet",
        valid    = False,
    ))

print(core.alfred_json(items))
