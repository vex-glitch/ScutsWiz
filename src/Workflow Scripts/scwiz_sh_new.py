#!/usr/bin/python3
"""scwiz_sh_new — Script Filter: enter a new shorthand.
Type: shorthand/action/used_in/description
↩ → save shorthand
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

query = sys.argv[1].strip() if len(sys.argv) > 1 else ""

HINT = "↩ Save  ·  ⌃↩ Delete  ·  ⌥⌘↩ Copy"

items = []

if query:
    shorthand, action, used_in, description = core.parse_shorthand(query)

    if shorthand:
        arg   = f"{shorthand}/{action}/{used_in}/{description}"
        parts = [p for p in [action, used_in, description] if p]
        subtitle_preview = "  ·  ".join(parts) if parts else "Type: shorthand/action/used_in/description"

        items.append(core.alfred_item(
            title    = shorthand,
            subtitle = subtitle_preview + "  —  ↩ Save",
            arg      = arg,
            uid      = f"shnew_{shorthand}",
            valid    = True,
        ))

if not items:
    items.append(core.alfred_item(
        title    = "Type a shorthand",
        subtitle = "Format: shorthand/action/used_in/description",
        valid    = False,
    ))

print(core.alfred_json(items))
