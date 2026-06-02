#!/usr/bin/python3
"""scwiz_what_key — Script Filter: what does this key do, across all modifier groups.
User types a key (e.g. A, F1, ↩) and sees every assigned shortcut that uses it.
Filters on the key portion of the keystroke only — not action, app, or description.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

query = sys.argv[1].strip().lower() if len(sys.argv) > 1 else ""

HINT = "↩ Unassign  ⌘↩ Change Keystroke  ⌥↩ Change Attributes  ⇧↩ Mark Unusable  ⌃↩ Revert  ⌥⌘↩ Copy  ⇧⌘↩ Banner"

def key_part(ks: str) -> str:
    """Extract just the key symbol from a keystroke string.
    '⌃⌘⇧ A'  → 'a'
    'F1 ⌃'   → 'f1'
    'F1'     → 'f1'
    """
    ks = ks.strip()
    if ks.startswith("F") and len(ks) > 1 and ks[1].isdigit():
        return ks.split()[0].lower()   # F-key: first token
    return ks.rsplit(" ", 1)[-1].lower()  # modifier group: last token

rows = [r for r in core.read_ssot() if core.is_taken(r)]

# Filter on key portion only
if query:
    rows = [r for r in rows if query in key_part(r.get("keystroke", ""))]

# Sort by key portion, then by full keystroke
rows.sort(key=lambda r: (key_part(r.get("keystroke", "")), r.get("keystroke", "")))

items = []

for row in rows:
    ks          = row.get("keystroke", "")
    action      = row.get("action", "")
    home        = row.get("home", "")
    used_in     = row.get("used_in", "")
    description = row.get("description", "")
    key         = row.get("key", "")
    layer       = row.get("layer", "")

    title      = f"{ks} - {action}/{home}/{used_in}/{description}/{key}/{layer}"
    arg        = f"{ks}/{action}/{home}/{used_in}/{description}/{key}/{layer}"
    banner_arg = core.format_entry(row)

    items.append(core.alfred_item(
        title    = title,
        subtitle = HINT,
        arg      = arg,
        uid      = f"whatkey_{ks}",
        valid    = True,
        mods     = {
            "cmd":       {"valid": True, "arg": arg,        "subtitle": "⌘↩  Change Keystroke"},
            "alt":       {"valid": True, "arg": arg,        "subtitle": "⌥↩  Change Attributes"},
            "shift":     {"valid": True, "arg": arg,        "subtitle": "⇧↩  Mark Unusable"},
            "ctrl":      {"valid": True, "arg": arg,        "subtitle": "⌃↩  Revert"},
            "cmd+alt":   {"valid": True, "arg": arg,        "subtitle": "⌥⌘↩  Copy to Clipboard"},
            "cmd+shift": {"valid": True, "arg": banner_arg, "subtitle": "⇧⌘↩  Display in Banner"},
        },
    ))

if not items:
    items.append(core.alfred_item(
        title    = "No shortcuts found" + (f" for key '{query}'" if query else ""),
        subtitle = "Type a key symbol to filter, e.g. A, F1, ↩",
        valid    = False,
    ))

print(core.alfred_json(items))
