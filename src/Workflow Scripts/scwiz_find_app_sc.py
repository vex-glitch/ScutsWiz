#!/usr/bin/python3
"""scwiz_find_app_sc — Script Filter: list shortcuts for a selected app (used_in).
Receives the app name via Replace from scwiz_find_app (sys.argv[1] = used_in).
On subsequent keystrokes, argv[1] is the live query; used_in is read from a temp file.
Results sorted by action alphabetically.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

_tmpdir    = Path(os.environ.get("TMPDIR", "/tmp"))
STATE_FILE = _tmpdir / "scwiz_app_sc.txt"

argv1 = sys.argv[1].strip() if len(sys.argv) > 1 else ""

rows       = core.read_ssot()
all_apps   = {r.get("used_in", "").strip() for r in rows if core.is_taken(r)}

if argv1 in all_apps:
    # Initial load via Replace — argv1 IS the used_in value
    used_in = argv1
    query   = ""
    STATE_FILE.write_text(used_in, encoding="utf-8")
else:
    # User is typing — read saved used_in, strip Alfred's prepended prefix to get actual query
    used_in = STATE_FILE.read_text(encoding="utf-8").strip() if STATE_FILE.exists() else ""
    raw     = argv1.lower()
    query   = raw[len(used_in):].strip() if used_in and raw.startswith(used_in.lower()) else raw

HINT = "↩ Unassign  ⌘↩ Change Keystroke  ⌥↩ Change Attributes  ⇧↩ Mark Unusable  ⌃↩ Revert  ⌥⌘↩ Copy  ⇧⌘↩ Banner  ⌃⇧↩ Copy Keystroke"

if not used_in:
    print(core.alfred_json([core.alfred_item(
        title    = "No app selected",
        subtitle = "Select an app from the previous list",
        valid    = False,
    )]))
    sys.exit(0)

taken = [r for r in rows if core.is_taken(r) and r.get("used_in", "").strip() == used_in]
taken.sort(key=lambda r: r.get("action", "").lower())

items = []

for row in taken:
    ks          = row.get("keystroke", "")
    action      = row.get("action", "")
    home        = row.get("home", "")
    used_in_    = row.get("used_in", "")
    description = row.get("description", "")
    key         = row.get("key", "")
    layer       = row.get("layer", "")

    if query:
        haystack = " ".join([ks, action, home, used_in_, description, key, layer]).lower()
        if query not in haystack:
            continue

    title = f"{ks} - {action}/{home}/{used_in_}/{description}/{key}/{layer}"
    arg   = f"{ks}/{action}/{home}/{used_in_}/{description}/{key}/{layer}"

    items.append(core.alfred_item(
        title    = title,
        subtitle = HINT,
        arg      = arg,
        uid      = f"appsc_{ks}",
        valid    = True,
        mods     = {
            "cmd":     {"valid": True, "arg": arg, "subtitle": "⌘↩  Change Keystroke"},
            "alt":     {"valid": True, "arg": arg, "subtitle": "⌥↩  Change Attributes"},
            "shift":   {"valid": True, "arg": arg, "subtitle": "⇧↩  Mark Unusable"},
            "ctrl":    {"valid": True, "arg": arg, "subtitle": "⌃↩  Revert"},
            "cmd+alt": {"valid": True, "arg": arg, "subtitle": "⌥⌘↩  Copy to Clipboard"},
        },
    ))

if not items:
    items.append(core.alfred_item(
        title    = f"No shortcuts for '{used_in}'" + (f" matching '{query}'" if query else ""),
        subtitle = "",
        valid    = False,
    ))

print(core.alfred_json(items))
