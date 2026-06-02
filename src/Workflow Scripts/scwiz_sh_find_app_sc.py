#!/usr/bin/python3
"""scwiz_sh_find_app_sc — Script Filter: list shorthands for a selected app (used_in).
Receives app via Replace from scwiz_sh_find_app. Uses temp file to persist
used_in across keystrokes so the user can type to filter results.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

HINT = "⏎ Unassign  ·  ⌘⏎ Change Shorthand  ·  ⌥⏎ Change Attributes  ·  ⌘⇧ Banner  ·  ⌥⌘ Copy"

_tmpdir    = Path(os.environ.get("TMPDIR", "/tmp"))
STATE_FILE = _tmpdir / "scwiz_sh_app_sc.txt"

argv1 = sys.argv[1].strip() if len(sys.argv) > 1 else ""

rows    = core.read_shorthands()
all_apps = {r.get("used_in", "").strip() for r in rows if r.get("used_in", "").strip()}

if argv1 in all_apps:
    used_in = argv1
    query   = ""
    STATE_FILE.write_text(used_in, encoding="utf-8")
else:
    used_in = STATE_FILE.read_text(encoding="utf-8").strip() if STATE_FILE.exists() else ""
    raw     = argv1.lower()
    query   = raw[len(used_in):].strip() if used_in and raw.startswith(used_in.lower()) else raw

if not used_in:
    print(core.alfred_json([core.alfred_item(
        title    = "No app selected",
        subtitle = "Select an app from the previous list",
        valid    = False,
    )]))
    sys.exit(0)

taken = [r for r in rows if r.get("used_in", "").strip() == used_in]
taken.sort(key=lambda r: r.get("action", "").lower())

items = []

for row in taken:
    shorthand   = row.get("shorthand", "")
    action      = row.get("action", "")
    used_in_    = row.get("used_in", "")
    description = row.get("description", "")

    if query:
        haystack = " ".join([shorthand, action, used_in_, description]).lower()
        if query not in haystack:
            continue

    parts = [p for p in [action, used_in_, description] if p]
    title = "  ·  ".join([shorthand] + parts)
    arg   = f"{shorthand}/{action}/{used_in_}/{description}"

    items.append(core.alfred_item(
        title    = title,
        subtitle = HINT,
        arg      = arg,
        uid      = f"shappsc_{shorthand}",
        valid    = True,
    ))

if not items:
    items.append(core.alfred_item(
        title    = f"No shorthands for '{used_in}'" + (f" matching '{query}'" if query else ""),
        subtitle = "",
        valid    = False,
    ))

print(core.alfred_json(items))
