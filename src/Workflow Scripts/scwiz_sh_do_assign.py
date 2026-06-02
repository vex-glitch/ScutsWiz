#!/usr/bin/python3
"""scwiz_sh_do_assign — Execute Script: save a shorthand to the shorthands SSOT.
Receives: shorthand/action/used_in/description via argv[1].
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

text = sys.argv[1].strip() if len(sys.argv) > 1 else ""

if not text:
    print("ERROR: no input received")
    sys.exit(1)

shorthand, action, used_in, description = core.parse_shorthand(text)

if not shorthand:
    print("ERROR: shorthand value is empty")
    sys.exit(1)

if core.shorthand_exists(shorthand, used_in):
    existing  = next(
        r for r in core.read_shorthands()
        if r["shorthand"] == shorthand and r.get("used_in", "") == used_in
    )
    parts     = [p for p in [existing.get("action",""), existing.get("used_in",""), existing.get("description","")] if p]
    detail    = f"{shorthand} - " + "  ·  ".join(parts) if parts else shorthand
    print(f"⚠️ This shorthand already exists, try again\n{detail}")
    sys.exit(1)

core.assign_shorthand(shorthand, action, used_in, description)
print(f"✓ Saved  {shorthand}  →  {action}/{used_in}" + (f"/{description}" if description else ""))
