#!/usr/bin/python3
"""scwiz_make_md — Execute Script: regenerate a markdown table from the SSOT TSV.

argv[1] — group name: "Fkeys", "⌃⌘⇧", "⌃⌥⌘", "⌥⌘⇧", "⌃⌥⌘⇧", "Everything", or "All"

  All       — generates every individual group file + Everything in one pass
  Everything — generates one combined file with all groups
  <group>   — generates the single file for that modifier group

Writes the full slot universe (free and assigned) as a markdown table
to the corresponding MD file. Empty slots get empty cells.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

group = sys.argv[1].strip() if len(sys.argv) > 1 else "All"

HEADER = "| Trigger | Action | Home | Used In | Description | Key | Layer |\n"
SEP    = "| --- | --- | --- | --- | --- | --- | --- |\n"


def row_line(ks: str, row: dict) -> str:
    if row and core.is_unusable(row):
        return f"| {ks} | XXX | XXX | XXX | XXX | XXX | XXX |\n"
    if row and core.is_taken(row):
        return (f"| {ks} | {row.get('action','')} | {row.get('home','')} | "
                f"{row.get('used_in','')} | {row.get('description','')} | "
                f"{row.get('key','')} | {row.get('layer','')} |\n")
    return f"| {ks} |  |  |  |  |  |  |\n"


def build_table(group_name: str, idx: dict) -> str:
    universe = core.get_slot_universe(group_name)
    lines    = [HEADER, SEP]

    if group_name == "Fkeys":
        # Empty table row between each F-key's modifier block (every 16 rows)
        EMPTY_ROW = "|  |  |  |  |  |  |  |\n"
        for i, ks in enumerate(universe):
            if i > 0 and i % len(core.FKEY_MODS) == 0:
                lines.append(EMPTY_ROW)
            lines.append(row_line(ks, idx.get(ks)))
    else:
        for ks in universe:
            lines.append(row_line(ks, idx.get(ks)))

    return "".join(lines)


def write_md(filename: str, content: str) -> Path:
    path = core.MD_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


idx = core.get_index()

if group == "All":
    generated = []
    for g in core.ALL_GROUPS:
        content  = build_table(g, idx)
        filename = f"ScutsWiz_{g}.md"
        write_md(filename, content)
        generated.append(filename)
    parts = [build_table(g, idx) for g in core.ALL_GROUPS]
    write_md("ScutsWiz_Everything.md", "\n".join(parts))
    generated.append("ScutsWiz_Everything.md")
    print(f"✓ Generated {len(generated)} files: {', '.join(generated)}")

elif group == "Everything":
    parts    = [build_table(g, idx) for g in core.ALL_GROUPS]
    content  = "\n".join(parts)
    path     = write_md("ScutsWiz_Everything.md", content)
    print(f"✓ Generated {path.name}")

elif group in core.ALL_GROUPS:
    content  = build_table(group, idx)
    filename = f"ScutsWiz_{group}.md"
    path     = write_md(filename, content)
    print(f"✓ Generated {path.name}")

else:
    print(f"ERROR: unknown group '{group}'")
    sys.exit(1)
