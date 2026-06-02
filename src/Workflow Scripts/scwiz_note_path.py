#!/usr/bin/python3
"""scwiz_note_path — Execute Script: output path of the note file for the active keyboard."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

print(core.NOTE_PATH if core.NOTE_PATH and core.NOTE_PATH.exists() else "", end="")
