#!/usr/bin/python3
"""scwiz_do_assign — Execute Script: write an assignment to the SSOT TSV.

Receives from Alfred:
  argv[1]        — full keyword text, e.g. "F5 ⌃⇧ - Activate Google/KM//Y/Extend"
  env scwiz_ks   — the keystroke, set by the slot-picker Script Filter

Writes the assignment to the SSOT and prints a one-line result for a
downstream Post Notification or Large Type node.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

text = sys.argv[1].strip() if len(sys.argv) > 1 else ""

if not text:
    print("ERROR: no input text received")
    sys.exit(1)

# Keystroke is everything before the first ' - ' or the first '/'
# e.g. "F1 ⌘ - Activate Google/KM//Y/Default"  →  "F1 ⌘"
# e.g. "F5 ⌃⇧/Test/AA/BB/e/1"                  →  "F5 ⌃⇧"
if " - " in text:
    keystroke = text.split(" - ", 1)[0].strip()
elif "/" in text:
    keystroke = text.split("/", 1)[0].strip()
else:
    print(f"ERROR: cannot parse keystroke from: {text!r}")
    sys.exit(1)

action, home, used_in, description, key, layer = core.parse_attributes(text)

core.assign_slot(keystroke, action, home, used_in,
                 description=description, key=key, layer=layer)

# Build a compact confirmation string for notification/large type
parts = [action]
if home:        parts.append(home)
if used_in:     parts.append(used_in)
if description: parts.append(description)
summary = " · ".join(parts)
extra   = []
if key:   extra.append(f"key={key}")
if layer: extra.append(f"layer={layer}")
if extra: summary += f"  ({', '.join(extra)})"

print(f"✓ {keystroke}  →  {summary}")
