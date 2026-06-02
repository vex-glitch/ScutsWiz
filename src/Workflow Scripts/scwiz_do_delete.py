#!/usr/bin/python3
"""scwiz_do_delete — Execute Script: remove an entry from the SSOT TSV entirely.

Receives from Alfred:
  argv[1] — the LastSelection variable, e.g. "⌃⌘⇧ A/Run/App/Des/y/L"
             keystroke is everything before the first /

Deletes the row from the SSOT, making the slot free again.
Prints a one-line confirmation for a downstream Post Notification node.
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

# Keystroke is everything before the first /
# e.g. "⌃⌘⇧ A/Run/App/Des/y/L"  →  "⌃⌘⇧ A"
keystroke = text.split("/", 1)[0].strip()

if not keystroke:
    print(f"ERROR: could not parse keystroke from: {text!r}")
    sys.exit(1)

# Confirm the entry actually exists before deleting
idx = core.get_index()
if keystroke not in idx:
    print(f"ERROR: {keystroke} not found in SSOT — nothing to delete")
    sys.exit(1)

core.delete_slot(keystroke)

# Reformat "⌃⌘⇧ A/Run/App/Des/y/L" → "⌃⌘⇧ A - Run/App/Des/y/L"
rest = text.split("/", 1)[1] if "/" in text else ""
print(f"{keystroke} - {rest}")
