#!/usr/bin/python3
"""scwiz_find_key_sc — Script Filter: list all shortcuts for the selected key.
Receives key via Replace from scwiz_find_key (sys.argv[1] = key).
On subsequent keystrokes, argv[1] is the live query; key is read from a temp file.
Shows all layers combined, sorted by layer then action alphabetically.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

_tmpdir    = Path(os.environ.get("TMPDIR", "/tmp"))
STATE_FILE = _tmpdir / "scwiz_key_sc.txt"

argv1 = sys.argv[1].strip() if len(sys.argv) > 1 else ""

rows     = core.read_ssot()
all_keys = {r.get("key", "").strip() for r in rows if core.is_taken(r)}

if argv1 in all_keys:
    # Initial load via Replace — argv1 IS the key value
    key   = argv1
    query = ""
    STATE_FILE.write_text(key, encoding="utf-8")
else:
    # User is typing — read saved key, strip Alfred's prepended prefix to get actual query
    key   = STATE_FILE.read_text(encoding="utf-8").strip() if STATE_FILE.exists() else ""
    raw   = argv1.lower()
    query = raw[len(key):].strip() if key and raw.startswith(key.lower()) else raw

HINT = "↩ Unassign  ⌘↩ Change Keystroke  ⌥↩ Change Attributes  ⇧↩ Mark Unusable  ⌃↩ Revert  ⌥⌘↩ Copy  ⇧⌘↩ Banner  ⌃⇧↩ Copy Keystroke"

if not key:
    print(core.alfred_json([core.alfred_item(
        title    = "No key received",
        subtitle = "Select a key from the previous list",
        valid    = False,
    )]))
    sys.exit(0)

taken = [r for r in rows if core.is_taken(r) and r.get("key", "").strip() == key]
taken.sort(key=lambda r: (r.get("layer", "").lower(), r.get("action", "").lower()))

items = []

for row in taken:
    ks          = row.get("keystroke", "")
    action      = row.get("action", "")
    home        = row.get("home", "")
    used_in     = row.get("used_in", "")
    description = row.get("description", "")
    key_        = row.get("key", "")
    layer_      = row.get("layer", "")

    if query:
        haystack = " ".join([ks, action, home, used_in, description, key_, layer_]).lower()
        if query not in haystack:
            continue

    title = f"{ks} - {action}/{home}/{used_in}/{description}/{key_}/{layer_}"
    arg   = f"{ks}/{action}/{home}/{used_in}/{description}/{key_}/{layer_}"

    items.append(core.alfred_item(
        title    = title,
        subtitle = HINT,
        arg      = arg,
        uid      = f"keysc_{ks}",
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
        title    = f"No shortcuts for key '{key}'" + (f" matching '{query}'" if query else ""),
        subtitle = "",
        valid    = False,
    ))

print(core.alfred_json(items))
