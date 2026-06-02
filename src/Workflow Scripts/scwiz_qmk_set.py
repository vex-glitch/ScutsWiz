#!/usr/bin/python3
"""scwiz_qmk_set — Execute Script: pick and save QMK keymap path for the active keyboard.
Opens a native macOS file picker. No Alfred File Filter needed.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

path = sys.argv[1].strip() if len(sys.argv) > 1 else ""

if not path:
    print("ERROR: no path received", end="")
    sys.exit(1)

core.set_kb_config("qmk_path", path)
print(f"✓ QMK path set for {core.KEYBOARD_NAME}", end="")
