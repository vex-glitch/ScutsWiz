#!/usr/bin/python3
"""scwiz_layout_path — Execute Script: output path of the layout PNG for the active keyboard.
Finds the first PNG in the keyboard's layout folder.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

pngs = sorted(core.LAYOUT_DIR.glob("*.png")) if core.LAYOUT_DIR else []
print(pngs[0] if pngs else "", end="")
