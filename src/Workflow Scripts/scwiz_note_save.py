#!/usr/bin/python3
"""scwiz_note_save — Execute Script: write Text View content back to the keyboard note file.

Receives:
  argv[1]        — text content from Text View
  note_path env  — file path set by preceding Args and Vars node
"""

import sys
import os
from pathlib import Path

content = sys.argv[1] if len(sys.argv) > 1 else ""
path    = os.environ.get("note_path", "").strip()

if not path:
    print("ERROR: note_path variable not set", end="")
    sys.exit(1)

Path(path).write_text(content, encoding="utf-8")
print(f"✓ Note saved", end="")
