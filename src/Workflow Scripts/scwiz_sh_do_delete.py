#!/usr/bin/python3
"""scwiz_sh_do_delete — Execute Script: remove a shorthand from the SSOT TSV entirely.

Receives from Alfred:
  argv[1] — the arg from the find script, e.g. "shorthand/action/used_in/description"
             shorthand is everything before the first /

Deletes the row from the shorthands SSOT.
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

# Parse shorthand/action/used_in/description
shorthand, action, used_in, description = core.parse_shorthand(text)

if not shorthand:
    print(f"ERROR: could not parse shorthand from: {text!r}")
    sys.exit(1)

# Confirm the (shorthand, used_in) pair actually exists before deleting
rows = core.read_shorthands()
if not any(r.get("shorthand", "") == shorthand and r.get("used_in", "") == used_in
           for r in rows):
    app_label = f" in {used_in}" if used_in else ""
    print(f"ERROR: '{shorthand}'{app_label} not found in shorthands — nothing to delete")
    sys.exit(1)

core.delete_shorthand(shorthand, used_in)

rest = text.split("/", 1)[1] if "/" in text else ""
print(f"{shorthand} - {rest}")
