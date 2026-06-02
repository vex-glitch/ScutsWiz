#!/usr/bin/python3
"""scwiz_next_fk — Script Filter: free F-key slots in MD-table order.
Alfred passes the typed query as argv[1] for live filtering.
↩  → copy keystroke to clipboard
⌘↩ → open assign flow for this slot
"""

import sys
import os

# core.py lives in ScutsWiz/, one level up from Workflow Scripts/
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

query = sys.argv[1].strip().upper() if len(sys.argv) > 1 else ""

idx      = core.get_index()
universe = core.get_slot_universe("Fkeys")
items    = []

for ks in universe:
    row = idx.get(ks)

    # Skip taken and unusable — show only free slots
    if core.is_taken(row) or core.is_unusable(row):
        continue

    # Live text filter
    if query and query not in ks.upper():
        continue

    items.append(core.alfred_item(
        title    = ks,
        subtitle = "Free  —  ↩ Assign  ·  ⌥⌘↩ Copy  ·  ⇧↩ Mark Unusable",
        arg      = ks,
        uid      = f"fk_{ks}",
        valid    = True,
    ))

if not items:
    items.append(core.alfred_item(
        title    = "No free F-key slots" + (f" matching '{query}'" if query else ""),
        subtitle  = "All F-key combinations are taken or unusable",
        valid    = False,
    ))

print(core.alfred_json(items))
