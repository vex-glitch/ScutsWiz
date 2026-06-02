#!/usr/bin/python3
"""scwiz_kle — Execute Script: open active keyboard layout in KLE-NG.

Generates a #share= URL by LZString-compressing the layout JSON.
No server, no CORS, no localhost — just opens a URL.
"""

import sys
import os
import json
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

try:
    import lzstring
except ImportError:
    print("⚠️ Missing dependency — run: pip install lzstring", end="")
    sys.exit(1)

LAYOUT_DIR = core.LAYOUT_DIR
KB_NAME    = core.KEYBOARD_NAME

if not LAYOUT_DIR or not LAYOUT_DIR.exists():
    print(f"⚠️ Layout folder not found for {KB_NAME}", end="")
    sys.exit(1)

jsons = sorted(LAYOUT_DIR.glob("*.json"))
if not jsons:
    print(f"⚠️ No JSON file found in {LAYOUT_DIR.name}", end="")
    sys.exit(1)

json_file = jsons[0]

try:
    data = json.loads(json_file.read_text(encoding="utf-8"))
except Exception as e:
    print(f"⚠️ Could not read {json_file.name}: {e}", end="")
    sys.exit(1)

compressed = lzstring.LZString().compressToEncodedURIComponent(json.dumps(data))
url        = f"https://editor.keyboard-tools.xyz/#share={compressed}"

subprocess.run(["open", url], capture_output=True)
print(f"✓ {KB_NAME} layout opened in KLE-NG", end="")
