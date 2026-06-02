#!/usr/bin/python3
"""scwiz_find_home_sc — Script Filter: list shortcuts for a selected home (origin).
Receives home name via Replace from scwiz_find_home (sys.argv[1] = home).
On subsequent keystrokes, argv[1] is the live query; home is read from a temp file.
Results sorted by action alphabetically.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

_tmpdir    = Path(os.environ.get("TMPDIR", "/tmp"))
STATE_FILE = _tmpdir / "scwiz_home_sc.txt"

argv1 = sys.argv[1].strip() if len(sys.argv) > 1 else ""

rows      = core.read_ssot()
all_homes = {r.get("home", "").strip() for r in rows if core.is_taken(r)}

if argv1 in all_homes:
    # Initial load via Replace — argv1 IS the home name
    home  = argv1
    query = ""
    STATE_FILE.write_text(home, encoding="utf-8")
else:
    # User is typing — read saved home, strip Alfred's prepended prefix to get actual query
    home  = STATE_FILE.read_text(encoding="utf-8").strip() if STATE_FILE.exists() else ""
    raw   = argv1.lower()
    query = raw[len(home):].strip() if home and raw.startswith(home.lower()) else raw

HINT = "↩ Unassign  ⌘↩ Change Keystroke  ⌥↩ Change Attributes  ⇧↩ Mark Unusable  ⌃↩ Revert  ⌥⌘↩ Copy  ⇧⌘↩ Banner  ⌃⇧↩ Copy Keystroke"

if not home:
    print(core.alfred_json([core.alfred_item(
        title    = "No home selected",
        subtitle = "Select a home from the previous list",
        valid    = False,
    )]))
    sys.exit(0)

taken = [r for r in rows if core.is_taken(r) and r.get("home", "").strip() == home]
taken.sort(key=lambda r: r.get("action", "").lower())

items = []

for row in taken:
    ks          = row.get("keystroke", "")
    action      = row.get("action", "")
    home_       = row.get("home", "")
    used_in     = row.get("used_in", "")
    description = row.get("description", "")
    key         = row.get("key", "")
    layer       = row.get("layer", "")

    if query:
        haystack = " ".join([ks, action, home_, used_in, description, key, layer]).lower()
        if query not in haystack:
            continue

    title = f"{ks} - {action}/{home_}/{used_in}/{description}/{key}/{layer}"
    arg   = f"{ks}/{action}/{home_}/{used_in}/{description}/{key}/{layer}"

    items.append(core.alfred_item(
        title    = title,
        subtitle = HINT,
        arg      = arg,
        uid      = f"homesc_{ks}",
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
        title    = f"No shortcuts for home '{home}'" + (f" matching '{query}'" if query else ""),
        subtitle = "",
        valid    = False,
    ))

print(core.alfred_json(items))
