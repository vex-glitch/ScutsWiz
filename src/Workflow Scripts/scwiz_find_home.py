#!/usr/bin/python3
"""scwiz_find_home — Script Filter: list unique home (origin) values alphabetically.
↩ → open shortcuts for that home.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

query = sys.argv[1].strip().lower() if len(sys.argv) > 1 else ""

rows = [r for r in core.read_ssot() if core.is_taken(r)]

# Build {home: count} dict
home_counts = {}
for row in rows:
    home = row.get("home", "").strip()
    if home:
        home_counts[home] = home_counts.get(home, 0) + 1

# Sort alphabetically
homes = sorted(home_counts.keys(), key=str.lower)

# Live filter
if query:
    homes = [h for h in homes if query in h.lower()]

items = []

for home in homes:
    count = home_counts[home]
    items.append(core.alfred_item(
        title     = home,
        subtitle  = f"{count} shortcut{'s' if count != 1 else ''}  —  ↩ browse",
        arg       = home,
        uid       = f"home_{home}",
        valid     = True,
        variables = {"sc_home": home},
    ))

if not items:
    items.append(core.alfred_item(
        title    = "No home entries found" + (f" matching '{query}'" if query else ""),
        subtitle = "Nothing has been assigned yet",
        valid    = False,
    ))

print(core.alfred_json(items))
