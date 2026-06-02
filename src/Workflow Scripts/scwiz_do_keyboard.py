#!/usr/bin/python3
"""scwiz_do_keyboard — Execute Script: switch active keyboard or scaffold a new one.

Receives from Alfred:
  argv[1] — keyboard name, or "__new__{name}" for a new keyboard
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

text = sys.argv[1].strip() if len(sys.argv) > 1 else ""

if not text:
    print("ERROR: no keyboard name received")
    sys.exit(1)

is_new  = text.startswith("__new__")
kb_name = text[len("__new__"):] if is_new else text

if not kb_name:
    print("ERROR: keyboard name is empty")
    sys.exit(1)

if is_new:
    kb_dir = core.scaffold_keyboard(kb_name)
    core.set_alfred_config("keyboard_name", kb_name)
    print(f"✓ Created {kb_name}  —  now active")
else:
    core.set_alfred_config("keyboard_name", kb_name)
    print(f"✓ Switched to {kb_name}")
