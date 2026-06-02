#!/usr/bin/python3
"""scwiz_find_app — Script Filter: list unique apps alphabetically.
↩ → open shortcuts for that app.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

query = sys.argv[1].strip().lower() if len(sys.argv) > 1 else ""

rows = [r for r in core.read_ssot() if core.is_taken(r)]

# Build {used_in: count} dict
app_counts = {}
for row in rows:
    used_in = row.get("used_in", "").strip()
    if used_in:
        app_counts[used_in] = app_counts.get(used_in, 0) + 1

# Sort alphabetically
apps = sorted(app_counts.keys(), key=str.lower)

# Live filter
if query:
    apps = [a for a in apps if query in a.lower()]

items = []

for used_in in apps:
    count = app_counts[used_in]
    items.append(core.alfred_item(
        title     = used_in,
        subtitle  = f"{count} shortcut{'s' if count != 1 else ''}  —  ↩ browse",
        arg       = used_in,
        uid       = f"app_{used_in}",
        valid     = True,
        variables = {"sc_used_in": used_in},
    ))

if not items:
    items.append(core.alfred_item(
        title    = "No apps found" + (f" matching '{query}'" if query else ""),
        subtitle = "Nothing has been assigned yet",
        valid    = False,
    ))

print(core.alfred_json(items))
