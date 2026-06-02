#!/usr/bin/python3
"""scwiz_history — Script Filter: full change history for one keystroke.

Reads scwiz_ks from the Alfred environment variable set by the previous node.
Shows every logged state newest-first. ↩ restores that state.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "ScutsWiz"))
import core

# Keystroke comes from the Alfred variable set by the preceding Arg and Vars node
keystroke = os.environ.get("scwiz_ks", "").strip()

if not keystroke:
    print(core.alfred_json([core.alfred_item(
        title    = "No keystroke selected",
        subtitle = "scwiz_ks variable is empty",
        valid    = False,
    )]))
    sys.exit(0)

OP_LABEL = {
    "assign":      "Assigned",
    "delete":      "Deleted",
    "change_key":  "Key changed",
    "change_attr": "Attributes changed",
    "clear":       "Cleared",
    "unusable":    "Marked unusable",
}

def parse_fields(s: str) -> dict:
    content = s.split(": ", 1)[1] if ": " in s else ""
    if not content.strip():
        return {}
    result = {}
    for part in content.split(" | "):
        if "=" in part:
            k, v = part.split("=", 1)
            result[k.strip()] = v.strip()
    return result

entries = core.get_keystroke_history(keystroke)
items   = []

for entry in entries:
    op        = entry["operation"]
    ts        = entry["timestamp"]
    old       = parse_fields(entry.get("old", ""))
    new       = parse_fields(entry.get("new", ""))

    # The "before" snapshot for this entry — what the row looked like before this op
    snap = old  # restoring means putting the row back to how it was before

    action      = snap.get("action", "")
    home        = snap.get("home", "")
    used_in     = snap.get("used_in", "")
    description = snap.get("description", "")
    key         = snap.get("key", "")
    layer       = snap.get("layer", "")

    # Build readable title
    op_label = OP_LABEL.get(op, op)
    if action and action != "XXX":
        state_str = f"{action}/{home}/{used_in}/{description}/{key}/{layer}"
    elif action == "XXX":
        state_str = "unusable"
    else:
        state_str = "(empty)"

    title    = f"{ts}  —  {op_label}"
    subtitle = f"Restore to: {keystroke}/{state_str}" if snap else "No previous state (created here)"

    # arg encodes the full state to restore: "ks/action/home/used_in/description/key/layer"
    arg   = f"{keystroke}/{action}/{home}/{used_in}/{description}/{key}/{layer}"
    valid = bool(snap)  # can't restore if there was no prior state

    items.append(core.alfred_item(
        title    = title,
        subtitle = subtitle,
        arg      = arg,
        uid      = f"hist_{keystroke}_{ts}",
        valid    = valid,
    ))

if not items:
    items.append(core.alfred_item(
        title    = f"No history found for {keystroke}",
        subtitle = "No log entries for this keystroke",
        valid    = False,
    ))

print(core.alfred_json(items))
