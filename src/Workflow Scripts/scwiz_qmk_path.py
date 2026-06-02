#!/usr/bin/python3
"""scwiz_qmk_path — Execute Script: output stored QMK keymap path for the active keyboard.
Outputs __not_set__ if no path has been configured yet.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

qmk_path = core.get_kb_config("qmk_path")
print(qmk_path if qmk_path else "__not_set__", end="")
