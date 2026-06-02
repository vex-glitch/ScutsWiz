#!/usr/bin/python3
"""scwiz_make_txt — Execute Script: write shortcuts + shorthands directly to KeyCue.

Generates System-wide.kcustom in KeyCue's Custom Shortcuts folder — no import needed.
Reloads KeyCue automatically after writing.

Structure:
  ⌃⇧ group
  ⌃⌘⇧ - Keyboard Maestro
  ⌃⌥⌘ - Alfred
  ⌥⌘⇧
  ⌃⌥⌘⇧
  Shorthands
  System-wide omit block
"""

import sys
import os
import plistlib
import subprocess
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

KCUSTOM = (Path.home() / "Library/Application Support/KeyCue"
           / "Custom Shortcuts/System-wide.kcustom")

# F keys excluded
EXPORT_ORDER = ["⌃⇧", "⌃⌘⇧", "⌃⌥⌘", "⌥⌘⇧", "⌃⌥⌘⇧"]

IMPLICIT_HOME = {"⌃⌘⇧", "⌃⌥⌘"}

GROUP_HEADING = {
    "⌃⇧":   "⌃⇧",
    "⌃⌘⇧":  "⌃⌘⇧ - Keyboard Maestro",
    "⌃⌥⌘":  "⌃⌥⌘ - Alfred",
    "⌥⌘⇧":  "⌥⌘⇧",
    "⌃⌥⌘⇧": "⌃⌥⌘⇧",
}

# ── Helpers ────────────────────────────────────────────────────────────────

def heading(title):
    return {"heading": True, "title": title}

def item(title, keystring):
    return {"title": title, "keystring": keystring, "type": 1}

def omit(title):
    return {"title": title, "keystring": "✘", "type": 1}

# ── Build shortcuts entries ────────────────────────────────────────────────

shortcuts = []

rows = [r for r in core.read_ssot() if core.is_taken(r)]

group_rows = defaultdict(list)
for row in rows:
    try:
        g = core.get_group(row["keystroke"])
        group_rows[g].append(row)
    except ValueError:
        pass

sc_count = 0

for group in EXPORT_ORDER:
    group_taken = group_rows.get(group, [])
    if not group_taken:
        continue

    group_taken.sort(key=lambda r: (r.get("used_in", "").lower(), r.get("action", "").lower()))

    shortcuts.append(heading(GROUP_HEADING[group]))

    if group == "⌃⇧":
        shortcuts.append(item("ACT · HOME", "X"))
        for row in group_taken:
            action   = row.get("action", "").strip()
            home     = row.get("home", "").strip()
            ks       = row.get("keystroke", "").strip()
            label    = f"{action} · {home}" if home else action
            shortcuts.append(item(label, ks))
            sc_count += 1

    else:
        implicit = group in IMPLICIT_HOME
        hdr_title = "ACT · KEY" if implicit else "ACT · HOME · KEY"
        shortcuts.append(item(hdr_title, "KEY · LAY"))

        for row in group_taken:
            action   = row.get("action", "").strip()
            home     = row.get("home", "").strip()
            key      = row.get("key", "").strip()
            layer    = row.get("layer", "").strip()
            ks       = row.get("keystroke", "").strip()
            key_only = ks.split(" ", 1)[1] if " " in ks else ks
            meta     = " ".join(p for p in [key, layer] if p)

            if implicit:
                label = f"{action} · {key_only}"
            else:
                label = f"{action} · {home} · {key_only}" if home else f"{action} · {key_only}"

            shortcuts.append(item(label, meta))
            sc_count += 1

# ── Shorthands section ─────────────────────────────────────────────────────

sh_rows = core.read_shorthands()
sh_rows = [r for r in sh_rows if r.get("shorthand", "").strip()]
sh_rows.sort(key=lambda r: (r.get("used_in", "").lower(), r.get("action", "").lower()))

if sh_rows:
    shortcuts.append(heading("Shorthands"))
    shortcuts.append(item("IN - ACT · DESC", "KEY"))
    for row in sh_rows:
        action      = row.get("action", "").strip()
        shorthand   = row.get("shorthand", "").strip()
        used_in     = row.get("used_in", "").strip()
        description = row.get("description", "").strip()
        prefix = f"{used_in} - " if used_in else ""
        label  = f"{action} · {description}" if description else action
        shortcuts.append(item(f"{prefix}{label}", shorthand))

# ── Omit block ─────────────────────────────────────────────────────────────

shortcuts += [
    heading("Edit"),
    omit("Cut"), omit("Copy"), omit("Select All"), omit("Paste"),

    heading("Window"),
    omit("*"),

    heading("Spelling and Grammar"),
    omit("*"), omit("Check Document Now"),

    heading("*"),
    omit("Settings..."), omit("Zoom In"), omit("Zoom Out"),
    omit("Enter Full Screen"), omit("Start Dictation..."),
    omit("Emoji & Symbols"), omit("Close"),
    omit("Show Spelling and Grammar"),

    heading("File"),
    omit("Print..."), omit("Open..."), omit("Open File..."),

    heading("Expose and Spaces"),
    omit("*"),

    heading("Input Sources"),
    omit("*"),

    heading("Typinator"),
    omit("*"),

    heading("*"),
    omit("Spelling and Grammar"),

    heading("Help"),
    omit("*"),
]

# ── Write .kcustom (only if keycue_automation is enabled) ──────────────────

keycue_on = os.environ.get("keycue_automation", "0").strip() == "1"

if keycue_on:
    plist_data = {"name": "System-wide", "shortcuts": shortcuts}
    KCUSTOM.parent.mkdir(parents=True, exist_ok=True)
    with open(KCUSTOM, "wb") as f:
        plistlib.dump(plist_data, f, fmt=plistlib.FMT_XML)

    kc_running = subprocess.run(["pgrep", "-x", "KeyCue"], capture_output=True).returncode == 0
    if kc_running:
        subprocess.run(["osascript", "-e", 'tell application "KeyCue" to quit'],
                       capture_output=True)
        time.sleep(0.8)
        subprocess.run(["open", "-a", "KeyCue"], capture_output=True)

    print(f"✓ KeyCue updated  ({sc_count} shortcuts · {len(sh_rows)} shorthands)"
          + ("  · KeyCue reloaded" if kc_running else "  · KeyCue was not running"))
else:
    print(f"✓ Done  ({sc_count} shortcuts · {len(sh_rows)} shorthands)  · KeyCue skipped")
