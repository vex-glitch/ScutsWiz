# ScutsWiz

**One workflow. Every shortcut. Every keyboard.**

![Alfred 5](https://img.shields.io/badge/Alfred-5-purple) ![macOS](https://img.shields.io/badge/macOS-compatible-blue) ![License: MIT](https://img.shields.io/badge/License-MIT-green)

---

## The Problem

If you use a custom keyboard with QMK, Keyboard Maestro, Alfred, and Typinator — your shortcuts live in four different places. You don't know what's free, what conflicts, or what a key does until you press it and something breaks. When a new keyboard arrives, you start from scratch.

ScutsWiz is a single-keyword Alfred workflow built around one idea: **a single source of truth for every shortcut you own**.

---

## The Philosophy

ScutsWiz treats your modifier key combinations as a **finite namespace** — like IP address space. There are exactly N possible ⌃⌥⌘ combinations. You own all of them. Some are assigned, some are free, some are unusable on your hardware. The goal is conscious ownership of the entire space.

This means:
- You assign shortcuts **intentionally**, not by habit
- Every assignment is documented — action, app, physical key, QMK layer
- Switching keyboards means updating the hardware mapping, not rebuilding from scratch
- Once a shortcut is consciously assigned, it is always retrievable and modifiable with a single keystroke

**ScutsWiz is for Systems t(h)inker(er)s.** You'll know if you are one as you continue reading.

The initial setup takes about an hour. After that the system lives with you forever — no more accidental conflicts, no more wondering *"something is triggering, where do I look? Keyboard Maestro? Alfred? System Settings?"* Open ScutsWiz, choose **What Does This Key Do**, pick the keystroke — and you know exactly where it lives, what it does, and how to change it.

> 📖 Full philosophy, design decisions, and the mental model behind ScutsWiz live in the [Wiki](https://github.com/vex-glitch/ScutsWiz/wiki).

---

## Overview

<!-- GIF: main list filter opening, scrolling through actions -->
> 🎬 *GIF: trigger ScutsWiz, scroll through the main action list*

Three pillars:

### 🗂 Track & Find
Find free slots. Know what every key does. Search your assigned shortcuts by app, action, or key position — with live filtering and modifier actions on every result.

<!-- GIF: next available → assign flow -->
> 🎬 *GIF: Next Available → find free slot → assign → KeyCue updates*

### 🔄 Stay in Sync
Every action that changes your shortcuts automatically regenerates your Markdown tables and updates KeyCue — no manual step required. The Generate Files action exists as a fallback, but in normal use everything stays current on its own.

<!-- GIF: Generate → KeyCue auto-reload -->
> 🎬 *GIF: Generate Files → KeyCue reloads with updated shortcuts*

### ⌨️ Keyboard-Aware
Each physical keyboard gets its own profile. Switch keyboards in one step. Assignments carry over — only the hardware key mapping resets for the new board.

<!-- GIF: Change Keyboard → scaffold → switch -->
> 🎬 *GIF: Change Keyboard → create Charybdis profile → switch*

---

## Getting Started

**Requirements:** Alfred 5 with Powerpack · macOS

**Install:** Download the workflow → open in Alfred

**Configure** (two required variables in Alfred preferences):

| Variable | What it is | Example |
|---|---|---|
| `base_path` | Folder where ScutsWiz stores its files | `~/Documents` |
| `keyboard_name` | Your current keyboard's name | `Charybdis` |

**Optional variables:**

| Variable | What it is |
|---|---|
| `code_editor` | App to open QMK keymap (app picker) |
| `app_md` | App to open Markdown tables |
| `app_SSOT` | App to open the SSOT file |
| `keycue_automation` | Enable direct KeyCue integration (checkbox) |

First run scaffolds your folder structure automatically. No further setup.

---

## Actions

<details>
<summary><strong>Find & Browse</strong></summary>

### Next Available
Browse free modifier+key combinations by group — ⌃⇧, ⌃⌘⇧, ⌃⌥⌘, ⌥⌘⇧, ⌃⌥⌘⇧, F Keys. See how full each group is at a glance. Assign directly from results.

### What Does This Key Do
Pick a modifier group → browse every slot in that group with its current assignment. Full reverse lookup.

### Find by Attribute
Filter assigned shortcuts by:
- **Home App** — which app handles the macro (KM, Alfred, etc.)
- **Used In App** — which app context it triggers in
- **Key Position** — physical key on the keyboard (by QMK layer position)
- **Action Name** — free-text search on the action description

All branches support live typing to filter, and every result carries the full set of [Universal Actions](#universal-actions).

</details>

<details>
<summary><strong>Keyboard Reference</strong></summary>

### CheatSheet
Displays your keyboard layout PNG in Alfred's image viewer. Switches automatically with your active keyboard profile.

### Layout Editor
Opens KLE-NG in your browser with your layout pre-loaded — no import dialog, no dragging files. The layout JSON is compressed directly into the URL using KLE-NG's own share format.

### QMK
Opens your keyboard's QMK keymap directory in your preferred code editor. First run prompts you to locate the folder once; stored per keyboard, never asked again.

### Note
Per-keyboard scratchpad for QMK notes, bugs, and to-dos. Opens in Alfred's Text View. Edit in place, ↩ saves back to disk.

</details>

<details>
<summary><strong>Shorthands</strong></summary>

A parallel tracking system for Typinator abbreviations — same SSOT pattern as shortcuts. Assign, find, act, undo.

**New** — add a shorthand (keyword, action, app, optional description)

**Find** — filter by app, keyword text, or action name. Every result supports assign, change, unassign.

**View** — open the shorthands file directly

**History** — last 10 modified shorthands with full context; act on any entry

**Undo** — 3-second undo window, same as shortcuts

Shorthands are **global** — shared across all keyboard profiles. The KeyCue export file includes both shortcuts and shorthands in one import.

</details>

<details>
<summary><strong>Generate & Sync Files</strong></summary>

Markdown tables and KeyCue are regenerated automatically after every assign, change, or delete action — you don't need to run Generate manually in normal use.

**Generate Files** is available as a fallback or to force a refresh:
- **MD Table (single group)** — regenerate the table for one modifier group
- **MD Tables (all groups)** — regenerate all tables at once
- **KeyCue** — force a full KeyCue refresh. Controlled by `keycue_automation` toggle.

### Navigate Files
Open, reveal in Finder, or act on your SSOT, Markdown tables, or layout files — all from Alfred.

</details>

<details>
<summary><strong>History & Undo</strong></summary>

Every assignment is logged with a timestamp. 

**Undo** — reverts the last change within a 3-second window

**History** — last 10 changes across all operations, live filterable. Act on any entry directly — unassign, re-assign, change attributes.

</details>

<details>
<summary><strong>Change Keyboard</strong></summary>

Switch between keyboard profiles or create a new one from Alfred.

On new keyboard creation:
- Folder structure scaffolded automatically (`_tables/`, `_layout/`, `Logs/`, `_note.md`)
- All existing assignments copied from current keyboard
- `key` and `layer` columns cleared — hardware mapping resets, everything else carries over
- Alfred variables updated in one step

> 📖 Full keyboard migration guide in the [Wiki](../../wiki).

</details>

<details>
<summary><strong>Docs</strong></summary>

Quick access to documentation for every tool ScutsWiz touches:
QMK · KLE-NG · KeyCue · VSCode · BBEdit · ScutsWiz GitHub

</details>

---

## Universal Actions

These modifier options appear on every result across all search and browse branches:

| Modifier | Action |
|---|---|
| ↩ | Assign / Unassign |
| ⌘↩ | Change Keystroke |
| ⌥↩ | Change Attributes |
| ⇧↩ | Mark Unusable |
| ⌃↩ | Revert |
| ⌥⌘↩ | Copy to Clipboard |
| ⇧⌘↩ | Display in Banner |
| ⌃⇧↩ | Copy Keystroke |

---

## File Structure

ScutsWiz stores everything in a folder of your choice:

```
{base_path}/ScutsWiz/
  shorthands/                     ← global, shared across keyboards
      ScutsWiz_shorthands.tsv
  {keyboard_name}/
      {keyboard_name}_ssot.tsv    ← the source of truth
      {keyboard_name}_tables/     ← generated Markdown tables
      {keyboard_name}_layout/     ← PNG, JSON files for KLE-NG
      {keyboard_name}_note.md     ← per-keyboard notes
      Logs/
```

---

## Wiki

> 📖 [ScutsWiz Wiki](https://github.com/vex-glitch/ScutsWiz/wiki) — full documentation

- [Philosophy & Mental Model](../../wiki)
- [The SSOT — fields, format, editing manually](../../wiki)
- [Keyboard Migration Guide](../../wiki)
- [Shorthands System](../../wiki)
- [KeyCue Integration](../../wiki)
- [KLE-NG Integration](../../wiki)
- [File Structure Reference](../../wiki)

---

## License

MIT
