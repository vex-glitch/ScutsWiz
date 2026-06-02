#!/usr/bin/python3
"""scwiz_next_cocs — Script Filter: free ⌃⌥⌘⇧ slots in MD-table order.
Alfred passes the typed query as argv[1] for live filtering.
↩  → open assign flow for this slot
⌘↩ → copy keystroke to clipboard
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

GROUP = "⌃⌥⌘⇧"

query = sys.argv[1].strip().upper() if len(sys.argv) > 1 else ""

idx      = core.get_index()
universe = core.get_slot_universe(GROUP)
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
        uid      = f"cocs_{ks}",
        valid    = True,
    ))

if not items:
    items.append(core.alfred_item(
        title    = "No free ⌃⌥⌘⇧ slots" + (f" matching '{query}'" if query else ""),
        subtitle  = "All ⌃⌥⌘⇧ combinations are taken or unusable",
        valid    = False,
    ))

print(core.alfred_json(items))
