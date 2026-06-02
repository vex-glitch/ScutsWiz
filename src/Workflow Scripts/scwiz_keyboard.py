#!/usr/bin/python3
"""scwiz_keyboard — Script Filter: list keyboards, switch active, or create new.

Placeholder title:   Switch keyboard
Placeholder subtext: Select active keyboard  ·  Type new name to create one
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

query   = sys.argv[1].strip() if len(sys.argv) > 1 else ""
active  = core.KEYBOARD_NAME
q_lower = query.lower()

keyboards = core.list_keyboards()

items = []

# Existing keyboards — filtered by query
for kb in keyboards:
    if q_lower and q_lower not in kb.lower():
        continue
    is_active = kb == active
    title    = f"✓ {kb}" if is_active else kb
    subtitle = "Active keyboard" if is_active else "↩ Switch to this keyboard"
    items.append(core.alfred_item(
        title    = title,
        subtitle = subtitle,
        arg      = kb,
        uid      = f"kb_{kb}",
        valid    = not is_active,
    ))

# Create new — always visible; becomes actionable when query is a new name
if query and query not in keyboards:
    items.insert(0, core.alfred_item(
        title    = f"➕ Create keyboard: {query}",
        subtitle = "↩ Scaffold new keyboard and switch to it",
        arg      = f"__new__{query}",
        uid      = "kb_new",
        valid    = True,
    ))
else:
    items.append(core.alfred_item(
        title    = "➕ Create new keyboard",
        subtitle = "Type a name above to create and switch to it",
        arg      = "",
        uid      = "kb_new",
        valid    = False,
    ))

if not items:
    items.append(core.alfred_item(
        title    = "No keyboards found",
        subtitle = "Type a name to create your first keyboard",
        valid    = False,
    ))

print(core.alfred_json(items))
