#!/usr/bin/python3
"""ScutsWiz — central library. All TSV read/write/query/log operations."""

import csv
import json
import os
import string
import subprocess
from datetime import datetime
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
#
# Primary (new): base_path + keyboard_name Alfred variables
#   {base_path}/ScutsWiz/{keyboard_name}/{keyboard_name}_ssot.tsv   ← SSOT
#   {base_path}/ScutsWiz/{keyboard_name}/{keyboard_name}_tables/    ← MD tables
#   {base_path}/ScutsWiz/{keyboard_name}/Logs/                      ← change log
#   {base_path}/ScutsWiz/{keyboard_name}/{keyboard_name}_layout.png ← layout image
#   {base_path}/ScutsWiz/{keyboard_name}/{keyboard_name}_note.md    ← per-kb notes
#   {base_path}/ScutsWiz/shorthands/ScutsWiz_shorthands.tsv        ← global shorthands
#
# Fallback (legacy): individual ssot_path / md_path / shands_path variables

_base_env = os.environ.get("base_path", "").strip()
_kb_name  = os.environ.get("keyboard_name", "").strip()

if _base_env and _kb_name:
    KEYBOARD_NAME   = _kb_name
    SCUTSWIZ_DIR    = Path(_base_env) / "ScutsWiz"
    KB_DIR          = SCUTSWIZ_DIR / _kb_name
    SSOT            = KB_DIR / f"{_kb_name}_ssot.tsv"
    MD_DIR          = KB_DIR / f"{_kb_name}_tables"
    LOG_DIR         = KB_DIR / "Logs"
    LAYOUT_DIR      = KB_DIR / f"{_kb_name}_layout"
    LAYOUT_PATH     = LAYOUT_DIR / f"{_kb_name}_layout.png"
    NOTE_PATH       = KB_DIR / f"{_kb_name}_note.md"
    SHORTHANDS_DIR  = SCUTSWIZ_DIR / "shorthands"
    SHORTHANDS_SSOT = SHORTHANDS_DIR / "ScutsWiz_shorthands.tsv"
    TXT_DIR         = KB_DIR / f"{_kb_name}_keycue"   # legacy, unused

else:
    # ── Legacy fallback ────────────────────────────────────────────────────
    KEYBOARD_NAME   = ""
    _ssot_env       = os.environ.get("ssot_path", "").strip()
    if _ssot_env:
        SSOT    = Path(_ssot_env)
        BASE    = SSOT.parent.parent
    else:
        BASE    = Path("/Users/vex/Library/Mobile Documents/com~apple~CloudDocs"
                       "/💫 DarwOS/❌/01 Automation/Shortcuts")
        SSOT    = BASE / "ScutsWiz - SSOT/ScutsWiz_ssot.tsv"

    _wd             = os.environ.get("alfred_workflow_data", "").strip()
    LOG_DIR         = BASE / "ScutsWiz - Logs"
    SCUTSWIZ_DIR    = BASE
    KB_DIR          = BASE

    _md_env         = os.environ.get("md_path", "").strip()
    MD_DIR          = (Path(_md_env) if _md_env
                       else Path(_wd) / "Text Generations" / "Markdown" if _wd
                       else BASE / "ScutsWiz - MD")

    _txt_env        = os.environ.get("txt_path", "").strip()
    TXT_DIR         = (Path(_txt_env) if _txt_env
                       else Path(_wd) / "Text Generations" / "KeyCue" if _wd
                       else BASE / "ScutsWiz - TXT")

    _layout_env     = os.environ.get("layout_path", "").strip()
    LAYOUT_DIR      = Path(_layout_env).parent if _layout_env else None
    LAYOUT_PATH     = Path(_layout_env) if _layout_env else None

    _note_env       = os.environ.get("man_path", "").strip()
    NOTE_PATH       = Path(_note_env) if _note_env else None

    _shands_env     = os.environ.get("shands_path", "").strip()
    SHORTHANDS_DIR  = Path(_shands_env) if _shands_env else BASE / "ScutsWiz - Shorthands"
    SHORTHANDS_SSOT = SHORTHANDS_DIR / "ScutsWiz_shorthands.tsv"

# ── Slot universe ──────────────────────────────────────────────────────────

# F-key modifier combos in canonical display order
FKEY_MODS = [
    "", "⌃", "⌥", "⌘", "⇧",
    "⌃⌥", "⌃⌘", "⌃⇧", "⌥⌘", "⌥⇧", "⌘⇧",
    "⌃⌘⇧", "⌃⌥⇧", "⌃⌥⌘", "⌥⌘⇧",
    "⌃⌥⌘⇧",
]

MODIFIER_GROUPS = ["⌃⇧", "⌃⌘⇧", "⌃⌥⌘", "⌥⌘⇧", "⌃⌥⌘⇧"]

# Full key universe — must match the MD tables exactly
LETTERS = list(string.ascii_uppercase)
NUMBERS = [str(i) for i in range(10)]
NUMPAD  = [f"{i}n" for i in range(10)]
SYMBOLS = ["~", "`", "!", "@", "#", "%", "°", "^", "&", "*", "(", ")",
           "-", "_", "+", "=", "{", "}", "[", "]", "|", "\\", "/",
           ":", ";", '"', "'", "<", ">", ",", ".", "?"]
SPECIAL = ["␣", "↩", "⇥", "⇪", "⌫", "⌦",
           "insert", "home", "end", "pgup", "pgdn", "prtscr", "numlock",
           "↑", "↓", "←", "→"]
ALL_KEYS = LETTERS + NUMBERS + NUMPAD + SYMBOLS + SPECIAL

# Display names used in Alfred menus
GROUP_DISPLAY = {
    "Fkeys":    "F keys",
    "⌃⇧":     "⌃⇧",
    "⌃⌘⇧":    "⌃⌘⇧",
    "⌃⌥⌘":    "⌃⌥⌘",
    "⌥⌘⇧":    "⌥⌘⇧",
    "⌃⌥⌘⇧":   "⌃⌥⌘⇧",
}
ALL_GROUPS = ["Fkeys"] + MODIFIER_GROUPS


def get_slot_universe(group: str) -> list:
    if group == "Fkeys":
        slots = []
        for fn in range(1, 15):
            for mods in FKEY_MODS:
                slots.append(f"F{fn}" + (f" {mods}" if mods else ""))
        return slots
    if group in MODIFIER_GROUPS:
        return [f"{group} {key}" for key in ALL_KEYS]
    raise ValueError(f"Unknown group: {group!r}")


def get_group(keystroke: str) -> str:
    """Derive group from keystroke string."""
    ks = keystroke.strip()
    if ks[:1] == "F" and len(ks) > 1 and ks[1:2].isdigit():
        return "Fkeys"
    # Check longest prefix first to avoid ⌃⌥⌘ matching ⌃⌥⌘⇧
    for g in ["⌃⌥⌘⇧", "⌃⌘⇧", "⌃⌥⌘", "⌥⌘⇧", "⌃⇧"]:
        if ks.startswith(g + " "):
            return g
    raise ValueError(f"Cannot determine group for: {keystroke!r}")


# ── TSV operations ─────────────────────────────────────────────────────────

FIELDS = ["keystroke", "action", "home", "used_in", "description", "key", "layer", "modified_at"]


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def read_ssot() -> list:
    if not SSOT.exists():
        return []
    with open(SSOT, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_ssot(rows: list) -> None:
    SSOT.parent.mkdir(parents=True, exist_ok=True)
    with open(SSOT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, delimiter="\t",
                           extrasaction="ignore")
        w.writeheader()
        for row in rows:
            row.setdefault("home", "")
            row.setdefault("used_in", "")
            row.setdefault("key", "")
            row.setdefault("layer", "")
        w.writerows(rows)


def get_index() -> dict:
    """Return {keystroke: row} for fast lookup."""
    return {r["keystroke"]: r for r in read_ssot()}


# ── Slot state helpers ─────────────────────────────────────────────────────

def is_free(row_or_none) -> bool:
    """Free = not in TSV, or in TSV with empty action."""
    if row_or_none is None:
        return True
    return row_or_none.get("action", "") == ""


def is_unusable(row_or_none) -> bool:
    if row_or_none is None:
        return False
    return row_or_none.get("action", "") == "XXX"


def is_taken(row_or_none) -> bool:
    """Taken = in TSV, has action, and not unusable."""
    if row_or_none is None:
        return False
    a = row_or_none.get("action", "")
    return a != "" and a != "XXX"


# ── CRUD ──────────────────────────────────────────────────────────────────

def assign_slot(keystroke: str, action: str, home: str, used_in: str,
                description: str = "", key: str = "", layer: str = "") -> dict:
    rows = read_ssot()
    old = {}
    for row in rows:
        if row["keystroke"] == keystroke:
            old = dict(row)
            row.update(action=action, home=home, used_in=used_in,
                       description=description, modified_at=_now(),
                       key=key or row.get("key", ""),
                       layer=layer or row.get("layer", ""))
            break
    else:
        rows.append(dict(keystroke=keystroke, action=action, home=home,
                         used_in=used_in, description=description,
                         modified_at=_now(), key=key, layer=layer))
    write_ssot(rows)
    new = dict(keystroke=keystroke, action=action, home=home, used_in=used_in,
               description=description, key=key, layer=layer)
    log_change("assign", keystroke, old, new)
    return new


def update_keystroke(old_ks: str, new_ks: str) -> dict:
    rows = read_ssot()
    old = {}
    for row in rows:
        if row["keystroke"] == old_ks:
            old = dict(row)
            row["keystroke"] = new_ks
            row["modified_at"] = _now()
            break
    write_ssot(rows)
    new = {"keystroke": new_ks}
    log_change("change_key", old_ks, old, new)
    return new


def update_attributes(keystroke: str, action: str, home: str, used_in: str,
                      description: str = "", key: str = "", layer: str = "") -> dict:
    rows = read_ssot()
    old = {}
    for row in rows:
        if row["keystroke"] == keystroke:
            old = dict(row)
            row.update(action=action, home=home, used_in=used_in,
                       description=description, modified_at=_now(),
                       key=key or row.get("key", ""),
                       layer=layer or row.get("layer", ""))
            break
    write_ssot(rows)
    new = dict(keystroke=keystroke, action=action, home=home, used_in=used_in,
               description=description, key=key, layer=layer)
    log_change("change_attr", keystroke, old, new)
    return new


def delete_slot(keystroke: str) -> None:
    """Remove a row from the SSOT entirely, making the slot free again."""
    rows = read_ssot()
    old = {}
    new_rows = []
    for row in rows:
        if row["keystroke"] == keystroke:
            old = dict(row)
        else:
            new_rows.append(row)
    write_ssot(new_rows)
    log_change("delete", keystroke, old, {})


def clear_slot(keystroke: str) -> None:
    """⌃⏎ — wipe action/home/used_in/desc, keep keystroke row and key/layer metadata."""
    rows = read_ssot()
    old = {}
    for row in rows:
        if row["keystroke"] == keystroke:
            old = dict(row)
            row.update(action="", home="", used_in="", description="", modified_at=_now())
            # key and layer are hardware metadata — preserved on clear
            break
    write_ssot(rows)
    log_change("clear", keystroke, old,
               dict(keystroke=keystroke, action="", home="", used_in="", description=""))


def mark_unusable(keystroke: str) -> None:
    """⇧⏎ — stamp XXX into action/home/used_in/desc; preserve key/layer."""
    rows = read_ssot()
    old = {}
    for row in rows:
        if row["keystroke"] == keystroke:
            old = dict(row)
            row.update(action="XXX", home="XXX", used_in="XXX",
                       description="XXX", modified_at=_now())
            # key and layer are hardware metadata — preserved on unusable
            break
    else:
        rows.append(dict(keystroke=keystroke, action="XXX", home="XXX",
                         used_in="XXX", description="XXX",
                         modified_at=_now(), key="", layer=""))
    write_ssot(rows)
    log_change("unusable", keystroke, old,
               dict(action="XXX", home="XXX", used_in="XXX", description="XXX"))


# ── Stats ──────────────────────────────────────────────────────────────────

def group_stats(group: str) -> dict:
    universe = get_slot_universe(group)
    idx = get_index()
    total    = len(universe)
    unusable = sum(1 for ks in universe if is_unusable(idx.get(ks)))
    taken    = sum(1 for ks in universe if is_taken(idx.get(ks)))
    free     = total - taken - unusable
    pct      = round((taken / total) * 100) if total else 0
    return dict(total=total, taken=taken, free=free,
                unusable=unusable, percent=pct)


# ── Logging ────────────────────────────────────────────────────────────────

def _log_path() -> Path:
    return LOG_DIR / f"scutswiz_{datetime.now().strftime('%Y-%m-%d')}.log"


def log_change(operation: str, keystroke: str, old: dict, new: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    old_s = " | ".join(f"{k}={v}" for k, v in old.items() if k != "modified_at")
    new_s = " | ".join(f"{k}={v}" for k, v in new.items() if k != "modified_at")
    line  = f"{_now()}\t{operation}\t{keystroke}\tOLD: {old_s}\tNEW: {new_s}\n"
    with open(_log_path(), "a", encoding="utf-8") as f:
        f.write(line)
    _purge_old_logs()


def _purge_old_logs() -> None:
    """Keep only the 7 most recent daily log files."""
    if not LOG_DIR.exists():
        return
    logs = sorted(LOG_DIR.glob("scutswiz_*.log"), reverse=True)
    for stale in logs[7:]:
        stale.unlink(missing_ok=True)


def get_keystroke_history(keystroke: str) -> list:
    """Return all log entries for a specific keystroke, newest first."""
    if not LOG_DIR.exists():
        return []
    logs = sorted(LOG_DIR.glob("scutswiz_*.log"), reverse=True)
    entries = []
    for lf in logs:
        lines = open(lf, encoding="utf-8").readlines()
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) > 2 and parts[2] == keystroke:
                entries.append({
                    "timestamp": parts[0] if len(parts) > 0 else "",
                    "operation": parts[1] if len(parts) > 1 else "",
                    "keystroke": parts[2] if len(parts) > 2 else "",
                    "old":       parts[3] if len(parts) > 3 else "",
                    "new":       parts[4] if len(parts) > 4 else "",
                })
    return entries


def get_recent_changes(n: int = 10) -> list:
    """Return up to n log entries newest-first, across all log files."""
    if not LOG_DIR.exists():
        return []
    logs = sorted(LOG_DIR.glob("scutswiz_*.log"), reverse=True)
    entries = []
    for lf in logs:
        lines = open(lf, encoding="utf-8").readlines()
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            entries.append({
                "timestamp": parts[0] if len(parts) > 0 else "",
                "operation": parts[1] if len(parts) > 1 else "",
                "keystroke": parts[2] if len(parts) > 2 else "",
                "old":       parts[3] if len(parts) > 3 else "",
                "new":       parts[4] if len(parts) > 4 else "",
            })
            if len(entries) >= n:
                return entries
    return entries


# ── Alfred configuration (cross-keyword persistent state) ─────────────────

def _bundle_id() -> str:
    return os.environ.get("alfred_workflow_bundleid", "")


def set_alfred_config(key: str, value: str) -> None:
    """Persist a value in Alfred's workflow configuration (survives session close)."""
    env = {**os.environ, "_CFG_KEY": key, "_CFG_VAL": value, "_CFG_BID": _bundle_id()}
    subprocess.run(["osascript", "-l", "JavaScript", "-e", """
ObjC.import('stdlib');
Application('com.runningwithcrayons.Alfred').setConfiguration(
    $.getenv('_CFG_KEY'), {
        toValue:    $.getenv('_CFG_VAL'),
        inWorkflow: $.getenv('_CFG_BID'),
        exportable: true
    }
);
"""], env=env, capture_output=True)


def get_alfred_config(key: str, default: str = "") -> str:
    """Read a value Alfred exposes as an environment variable."""
    return os.environ.get(key, default).strip()


def remove_alfred_config(key: str) -> None:
    """Delete a key from Alfred's workflow configuration."""
    env = {**os.environ, "_CFG_KEY": key, "_CFG_BID": _bundle_id()}
    subprocess.run(["osascript", "-l", "JavaScript", "-e", """
ObjC.import('stdlib');
Application('com.runningwithcrayons.Alfred').removeConfiguration(
    $.getenv('_CFG_KEY'), { inWorkflow: $.getenv('_CFG_BID') }
);
"""], env=env, capture_output=True)


# ── Per-keyboard config ────────────────────────────────────────────────────

def get_kb_config(key: str, default: str = "") -> str:
    """Read a value from the active keyboard's config JSON."""
    config_path = KB_DIR / f"{KEYBOARD_NAME}_config.json"
    if not config_path.exists():
        return default
    try:
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
        return data.get(key, default)
    except (json.JSONDecodeError, OSError):
        return default


def set_kb_config(key: str, value: str) -> None:
    """Write a value to the active keyboard's config JSON."""
    config_path = KB_DIR / f"{KEYBOARD_NAME}_config.json"
    data = {}
    if config_path.exists():
        try:
            with open(config_path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    data[key] = value
    KB_DIR.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── Keyboard management ────────────────────────────────────────────────────

def list_keyboards() -> list:
    """Return sorted list of keyboard names (subfolders of ScutsWiz that contain an _ssot.tsv)."""
    if not SCUTSWIZ_DIR.exists():
        return []
    keyboards = []
    for d in sorted(SCUTSWIZ_DIR.iterdir()):
        if d.is_dir() and (d / f"{d.name}_ssot.tsv").exists():
            keyboards.append(d.name)
    return keyboards


def scaffold_keyboard(kb_name: str) -> Path:
    """Create folder structure for a new keyboard. Returns the keyboard directory."""
    base = os.environ.get("base_path", "").strip()
    if not base:
        raise ValueError("base_path variable not set — cannot scaffold keyboard")
    kb_dir = Path(base) / "ScutsWiz" / kb_name
    (kb_dir / f"{kb_name}_tables").mkdir(parents=True, exist_ok=True)
    (kb_dir / f"{kb_name}_layout").mkdir(parents=True, exist_ok=True)
    (kb_dir / "Logs").mkdir(parents=True, exist_ok=True)
    ssot = kb_dir / f"{kb_name}_ssot.tsv"
    if not ssot.exists():
        # Copy current keyboard's SSOT and clear key/layer — assignments carry over,
        # hardware mapping does not (user fills that in as they set up QMK)
        if SSOT.exists() and SSOT != ssot:
            rows = read_ssot()
            for row in rows:
                row["key"]   = ""
                row["layer"] = ""
            with open(ssot, "w", newline="", encoding="utf-8") as f:
                import csv as _csv
                w = _csv.DictWriter(f, fieldnames=FIELDS, delimiter="\t", extrasaction="ignore")
                w.writeheader()
                w.writerows(rows)
        else:
            with open(ssot, "w", encoding="utf-8") as f:
                f.write("\t".join(FIELDS) + "\n")

    note = kb_dir / f"{kb_name}_note.md"
    if not note.exists():
        note.write_text(f"# {kb_name}\n", encoding="utf-8")
    shorthands_dir = Path(base) / "ScutsWiz" / "shorthands"
    shorthands_dir.mkdir(parents=True, exist_ok=True)
    sh_ssot = shorthands_dir / "ScutsWiz_shorthands.tsv"
    if not sh_ssot.exists():
        with open(sh_ssot, "w", encoding="utf-8") as f:
            f.write("\t".join(SHORTHANDS_FIELDS) + "\n")
    return kb_dir


# ── Input parsing ──────────────────────────────────────────────────────────

def parse_assignment(text: str) -> tuple:
    """
    Parse 'Action - App' or 'Action - App - Description'.
    Returns (action, app, description). description may be empty.
    """
    parts = [p.strip() for p in text.split(" - ", 2)]
    action      = parts[0] if len(parts) > 0 else ""
    app         = parts[1] if len(parts) > 1 else ""
    description = parts[2] if len(parts) > 2 else ""
    return action, app, description


def parse_attributes(text: str) -> tuple:
    """
    Parse assignment text in either format:
      '{keystroke} - Action/Home/UsedIn/Description/Key/Layer'  (keyword input format)
      '{keystroke}/Action/Home/UsedIn/Description/Key/Layer'    (slash-only format)
    The keystroke prefix is stripped automatically in both cases.
    All fields after Action are optional; empty slots (e.g. //) are preserved as ''.
    Returns (action, home, used_in, description, key, layer).
    """
    if " - " in text:
        text = text.split(" - ", 1)[1]
    else:
        text = text.split("/", 1)[1] if "/" in text else text
    parts = [p.strip() for p in text.split("/", 5)]
    action      = parts[0] if len(parts) > 0 else ""
    home        = parts[1] if len(parts) > 1 else ""
    used_in     = parts[2] if len(parts) > 2 else ""
    description = parts[3] if len(parts) > 3 else ""
    key         = parts[4] if len(parts) > 4 else ""
    layer       = parts[5] if len(parts) > 5 else ""
    return action, home, used_in, description, key, layer


# ── Display helpers ────────────────────────────────────────────────────────

def format_entry(row: dict) -> str:
    """⌃⌥⌘ K :: Copy - BBEdit - Global palette"""
    parts = [row.get("action",""), row.get("home",""), row.get("used_in",""), row.get("description","")]
    parts = [p for p in parts if p and p != "XXX"]
    suffix = " - ".join(parts) if parts else "—"
    return f"{row['keystroke']} :: {suffix}"


# ── Shorthands ─────────────────────────────────────────────────────────────

SHORTHANDS_FIELDS = ["shorthand", "action", "used_in", "description", "modified_at"]


def read_shorthands() -> list:
    if not SHORTHANDS_SSOT.exists():
        return []
    with open(SHORTHANDS_SSOT, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_shorthands(rows: list) -> None:
    SHORTHANDS_SSOT.parent.mkdir(parents=True, exist_ok=True)
    with open(SHORTHANDS_SSOT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SHORTHANDS_FIELDS, delimiter="\t",
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def assign_shorthand(shorthand: str, action: str, used_in: str,
                     description: str = "") -> dict:
    """Upsert on (shorthand, used_in) — same shorthand may exist in different apps."""
    rows = read_shorthands()
    old  = {}
    for row in rows:
        if row["shorthand"] == shorthand and row.get("used_in", "") == used_in:
            old = dict(row)
            row.update(action=action, used_in=used_in,
                       description=description, modified_at=_now())
            break
    else:
        rows.append(dict(shorthand=shorthand, action=action, used_in=used_in,
                         description=description, modified_at=_now()))
    write_shorthands(rows)
    new = dict(shorthand=shorthand, action=action, used_in=used_in,
               description=description)
    _log_shorthand("assign", shorthand, old, new)
    return new


def shorthand_exists(shorthand: str, used_in: str) -> bool:
    """Return True if (shorthand, used_in) pair already exists in the SSOT."""
    return any(
        r["shorthand"] == shorthand and r.get("used_in", "") == used_in
        for r in read_shorthands()
    )


def delete_shorthand(shorthand: str, used_in: str = "") -> None:
    """Remove the (shorthand, used_in) row. If used_in is empty, removes all rows with that shorthand."""
    rows = read_shorthands()
    if used_in:
        old      = next((dict(r) for r in rows
                         if r["shorthand"] == shorthand and r.get("used_in", "") == used_in), {})
        new_rows = [r for r in rows
                    if not (r["shorthand"] == shorthand and r.get("used_in", "") == used_in)]
    else:
        old      = next((dict(r) for r in rows if r["shorthand"] == shorthand), {})
        new_rows = [r for r in rows if r["shorthand"] != shorthand]
    write_shorthands(new_rows)
    _log_shorthand("delete", shorthand, old, {})


def _log_shorthand(operation: str, shorthand: str, old: dict, new: dict) -> None:
    log_dir = SHORTHANDS_DIR / "Logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"scwiz_shorthands_{datetime.now().strftime('%Y-%m-%d')}.log"
    old_s = " | ".join(f"{k}={v}" for k, v in old.items() if k != "modified_at")
    new_s = " | ".join(f"{k}={v}" for k, v in new.items() if k != "modified_at")
    line  = f"{_now()}\t{operation}\t{shorthand}\tOLD: {old_s}\tNEW: {new_s}\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)
    # Keep only the 7 most recent daily log files
    logs = sorted(log_dir.glob("scwiz_shorthands_*.log"), reverse=True)
    for stale in logs[7:]:
        stale.unlink(missing_ok=True)


def get_recent_shorthand_changes(n: int = 20) -> list:
    log_dir = SHORTHANDS_DIR / "Logs"
    if not log_dir.exists():
        return []
    logs    = sorted(log_dir.glob("scwiz_shorthands_*.log"), reverse=True)
    entries = []
    for lf in logs:
        for line in reversed(open(lf, encoding="utf-8").readlines()):
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            entries.append({
                "timestamp": parts[0] if len(parts) > 0 else "",
                "operation": parts[1] if len(parts) > 1 else "",
                "shorthand": parts[2] if len(parts) > 2 else "",
                "old":       parts[3] if len(parts) > 3 else "",
                "new":       parts[4] if len(parts) > 4 else "",
            })
            if len(entries) >= n:
                return entries
    return entries


def parse_shorthand(text: str) -> tuple:
    """Parse 'shorthand/action/used_in/description'. All fields after shorthand optional."""
    parts = [p.strip() for p in text.split("/", 3)]
    shorthand   = parts[0] if len(parts) > 0 else ""
    action      = parts[1] if len(parts) > 1 else ""
    used_in     = parts[2] if len(parts) > 2 else ""
    description = parts[3] if len(parts) > 3 else ""
    return shorthand, action, used_in, description


# ── Alfred JSON output ─────────────────────────────────────────────────────

def alfred_json(items: list) -> str:
    return json.dumps({"skipknowledge": True, "items": items}, ensure_ascii=False)


def alfred_item(title, subtitle="", arg="", uid="", valid=True,
                icon=None, variables=None, mods=None) -> dict:
    item = {"title": title, "subtitle": subtitle,
            "arg": arg, "uid": uid or title, "valid": valid}
    if icon:
        item["icon"] = {"path": icon}
    if variables:
        item["variables"] = variables
    if mods:
        item["mods"] = mods
    return item
