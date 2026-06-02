#!/usr/bin/python3
"""scwiz_sh_make_md — Execute Script: generate a markdown table for shorthands.

Columns: Shorthand | Action | Used In | Description
Sorted by shorthand alphabetically.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

rows = core.read_shorthands()
rows.sort(key=lambda r: r.get("shorthand", "").lower())

HEADER = "| Shorthand | Action | Used In | Description |\n"
SEP    = "| --- | --- | --- | --- |\n"

lines = [HEADER, SEP]

for row in rows:
    shorthand   = row.get("shorthand", "")
    action      = row.get("action", "")
    used_in     = row.get("used_in", "")
    description = row.get("description", "")
    lines.append(f"| {shorthand} | {action} | {used_in} | {description} |\n")

if len(lines) == 2:
    lines.append("|  |  |  |  |\n")

content = "".join(lines)

core.MD_DIR.mkdir(parents=True, exist_ok=True)
out_path = core.MD_DIR / "ScutsWiz_Shorthands.md"
out_path.write_text(content, encoding="utf-8")

print(f"✓ Generated {out_path.name}  ({len(rows)} shorthands)")
