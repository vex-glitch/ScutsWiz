#!/usr/bin/python3
"""scwiz_docs — Script Filter: open documentation links for tools used in ScutsWiz."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

query = sys.argv[1].strip().lower() if len(sys.argv) > 1 else ""

DOCS = [
    ("QMK Docs",        "Keyboard firmware documentation",          "https://docs.qmk.fm/"),
    ("KLE",             "Keyboard Layout Editor — layout editor",    "https://editor.keyboard-tools.xyz/"),
    ("KeyCue",          "KeyCue product page and support",           "https://www.ergonis.com/keycue/"),
    ("VSCode Docs",     "Visual Studio Code documentation",          "https://code.visualstudio.com/docs"),
    ("BBEdit",          "BBEdit product page and documentation",     "https://www.barebones.com/products/bbedit/"),
    ("ScutsWiz GitHub", "Workflow source — coming soon",             ""),
]

items = []
for title, subtitle, url in DOCS:
    if query and query not in title.lower() and query not in subtitle.lower():
        continue
    items.append(core.alfred_item(
        title    = title,
        subtitle = subtitle,
        arg      = url,
        uid      = f"docs_{title}",
        valid    = bool(url),
    ))

print(core.alfred_json(items))
