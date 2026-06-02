#!/usr/bin/python3
"""scwiz_find_key — Script Filter: list unique physical keys from the key column.
Connect to scwiz_find_key_layer via Replace.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

query = sys.argv[1].strip().lower() if len(sys.argv) > 1 else ""

rows = [r for r in core.read_ssot() if core.is_taken(r)]

key_counts = {}
for row in rows:
    k = row.get("key", "").strip()
    if k:
        key_counts[k] = key_counts.get(k, 0) + 1

keys = sorted(key_counts.keys(), key=str.lower)

if query:
    keys = [k for k in keys if query in k.lower()]

items = []

for k in keys:
    count = key_counts[k]
    items.append(core.alfred_item(
        title     = k,
        subtitle  = f"{count} shortcut{'s' if count != 1 else ''}  —  ↩ select layer",
        arg       = k,
        uid       = f"key_{k}",
        valid     = True,
        variables = {"sc_key": k},
    ))

if not items:
    items.append(core.alfred_item(
        title    = "No keys found" + (f" matching '{query}'" if query else ""),
        subtitle = "No shortcuts have a key assigned",
        valid    = False,
    ))

print(core.alfred_json(items))
