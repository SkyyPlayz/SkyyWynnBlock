# 🪨 Using the project in Obsidian

Set up 2026-10-05. The repo comes with its Obsidian settings, so it works the same on every PC.

&nbsp;

## 1. Open it (one time)

- Obsidian → **Open folder as vault** → pick `C:\Users\SkyLo\Desktop\Hytale mods WORK\SkyWynn PROJECT`.

- That folder IS the vault. Nothing moves, so every path in the docs and tools stays right.

- If Obsidian asks: **Trust author and enable plugins** is not needed - the vault uses no community plugins.

- The empty `Hytale Projects` folder can be deleted, or kept for notes that are not SkyWynn.

Why not put the project inside `Hytale Projects`? Moving the folder changes the paths that RESUME, the tools and Claude's local
memory use, and Obsidian warns against symlinks / junctions. If you still want one vault for several projects later, the local
Claude session can move the folder and fix every path in one round.

&nbsp;

## 2. What is already set up

- **Bookmarks** (left sidebar, bookmark icon): Resume, Index, Open questions, Test next, Handoff, Project rules, Classes,
  Answered questions, this month's log - in reading order.

- **Easy-read style:** Atkinson Hyperlegible font, big text (20), wide line + letter spacing, short lines, no italics.
  Switch it off or on: Settings → Appearance → CSS snippets → `skywynn-easy-read`.

- **Links:** normal markdown links `[Resume](RESUME.md)`, not `[[wiki links]]`. They work in Obsidian, on GitHub and for the AI.
  New links are relative paths, and Obsidian fixes them when you rename or move a file.

- **Hidden from search + graph** (still in the folder): `docs/archive/`, the generated class pages `research/classes/html/`,
  `tools/dev/`, `build_classes/`, `backups/`, the stray `PROJECT/` folder.

- **Diagrams:** the class map diagrams (mermaid) draw themselves in reading view.

&nbsp;

## 3. Good habits

- Search everything: **Ctrl+Shift+F**. One line in `docs/answered/` or `docs/log/` = one whole fact.

- Jump to any file: **Ctrl+O** and type part of the name.

- See what links to a note: the **Backlinks** panel (right sidebar).

- The class pages for reading: open `research/classes/html/index.html` in a browser (big cards).
  Edit the class `.md` in Obsidian, then ask Claude to run `python tools/class_pages.py` (or run it yourself).

- **Don't edit by hand:** `SkyyGear-Plan.md` and `SkyyGear-Stat-Catalog.md` stay exactly as Skyy wrote them (Claude never edits
  them; you can). Generated files (`research/classes/html/`) are rebuilt by the tool.

- Your window layout (Obsidian's workspace files) is never pushed to GitHub. The shared settings above are.

&nbsp;

## 4. Plugins

- **None needed.** The built-in ones the vault uses are already on: search, quick switcher, bookmarks, backlinks, outline, graph,
  canvas, page preview, file recovery.

- **Optional - Homepage** (community plugin): opens `RESUME.md` every time you open the vault.

- **Optional - Obsidian Git** (community plugin): a "Pull" button to get the newest files. Turn its **auto-commit and auto-push OFF** -
  the Claude sessions commit and push, and automatic commits would clash with them.

- Skip the rest (Dataview, themes, ...): every extra plugin is one more thing that can break or rewrite files.
