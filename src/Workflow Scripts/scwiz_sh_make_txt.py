#!/usr/bin/python3
"""scwiz_sh_make_txt — Execute Script: generate a KeyCue plain text import for shorthands.

Single section headed "Shorthands".
Each row prefixed with used_in shorthand: "TN - Action · Description\tshorthand"
Sorted by used_in alphabetically, then action alphabetically.
Only saved shorthands — no empty rows.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

rows = core.read_shorthands()
rows = [r for r in rows if r.get("shorthand", "").strip()]
rows.sort(key=lambda r: (r.get("used_in", "").lower(), r.get("action", "").lower()))

lines = ["Shorthands", "IN - ACT · DESC\tKEY"]

for row in rows:
    action      = row.get("action", "").strip()
    shorthand   = row.get("shorthand", "").strip()
    used_in     = row.get("used_in", "").strip()
    description = row.get("description", "").strip()

    prefix = f"{used_in} - " if used_in else ""
    label  = f"{action} · {description}" if description else action
    lines.append(f"{prefix}{label}\t{shorthand}")

content = "\n".join(lines) + "\n"

core.TXT_DIR.mkdir(parents=True, exist_ok=True)
out_path = core.TXT_DIR / "ScutsWiz_Shorthands.txt"
out_path.write_text(content, encoding="utf-8")

print(f"✓ Generated {out_path.name}  ({len(rows)} shorthands)")
