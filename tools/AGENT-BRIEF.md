# SkyWynn builder brief (read fully before working)

Project: SkyWynn, Skyy's public Hytale server mods (Hypixel SkyBlock + Wynncraft) as standalone "Skyy*" mods.
Folder: C:\Users\SkyLo\Desktop\Hytale mods WORK\SkyWynn PROJECT (git repo). Skyy uses they/them.

Read first: HANDOFF.md (the BUILDER / STATUS block at the top, sections 1-3, and the newest section-6 log lines - especially the
2026-09-28 line about generated scripts edited in commit ab75b6c), SkyWynn-Decisions.md 'Change notes (2026-09-25)', OPEN-QUESTIONS.md
(every "LOCKED 2026-09-25 (Skyy)" line is a decision to follow), tools/CONFIG-CONTRACT.md (admin settings kit tools/skyycfg.py -> SkyyMenu
Server Setup), research/Settings-Spec.md 1.2-1.3 (player switches), tools/PROFILES-CONTRACT.md. The LIVE set = tools/deploy_set.py SET.

## Toolchain
- No javac. Java lives in Python build scripts compiled by javassist via jpype (tools/skyybuild.py).
- Derive a new version from the CURRENT script of that mod (the SET pin). If the mod uses patch scripts (read the script header),
  write tools/<mod>_<ver>_patch.py that reads the previous GENERATED script and writes the new one; edit the patch, never the generated file.
- EXCEPTION: SkyySkills 0.4.5, SkyyTrees 0.2.3, SkyyClasses 0.1.6 and SkyyVault 0.1.2 generated scripts were edited by Skyy directly
  (commit ab75b6c). Never re-run their old patch scripts. The next version's patch reads the EDITED generated script as its source.
- javassist limits: no lambdas, generics, varargs, autoboxing, enhanced-for, inner classes, String switch, try-with-resources; methods
  before callers; a synchronized block holds one call; f-string braces doubled.
- Engine rules: ONE registerSystem per class; PlayerReadyEvent fires on every world switch; components / inventory / stats only on the
  world thread; count items before and after moves; give items storage-first unless a lock says otherwise.
- COMMAND RULES: every player command / subcommand / usage variant needs setPermissionGroups(new String[] { "hytale:Adventurer" }); an
  admin SUB-command under a player command needs requirePermission(...) AND setPermissionGroups(new String[0]) (lint rule perm_group_leaks).
- UI LOOK (Skyy 2026-09-28): every UI must look and feel as close to vanilla Hytale as possible - mirror the game's own UI styles
  (colours, fonts, frames, buttons, spacing) from Assets.zip instead of custom styling.
  USE THE SHARED KIT: tools/skyyui.py (`import skyyui as SUI`, call SUI.verify() at build time) - every colour, font, texture, sound,
  frame and button comes from it; read research/Vanilla-UI-Style-Guide.md first. Never hand-write styles; if the kit lacks a block, add it
  to the kit (+ tools/skyyui_test.py + the guide). Features marked trial/UNVERIFIED stay off until Skyy has seen them (skyyui.PROBED).
- UI RULES (HANDOFF section 2): inline pages only; no underscores in element ids; root anchor only Width/Height; TextButton + EventData;
  never periodic page updates; never close a page right before opening another; BIG readable pages (fit 1080 high); no UI on the vanilla
  inventory screen; NEVER put an ItemStack that may carry metadata into an ItemGridSlot (client disconnect) - use new ItemStack(id, qty).
- Cross-mod calls only through System.getProperties().get("skyy.bridge") with java.lang types.
- Engine inspection: tools/dev/reflect.py, cpgrep.py (run inside tools/dev), bc.py, bcfull.py, bcfull2.py, callers.py. Server jar and
  Assets.zip: C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest (read-only). Installed mods read-only in
  C:\Users\SkyLo\AppData\Roaming\Hytale\UserData\Mods.

## Hard rules
- NEVER pass --deploy. Never run tools/deploy_set.py except with --check.
- Never write inside C:\Users\SkyLo\AppData. Scratch only under tools/dev/scratch/<your-task>/ and delete it afterwards; point TEMP/TMP
  there for Java runs and use -XX:-UsePerfData.
- Delete ONLY your own scratch folder (the exact tools/dev/scratch/<your-task>/ you created). NEVER delete, empty or "clean" other
  folders under tools/dev/scratch/ - other agents run in parallel and their live work sits there (2026-10-02: a cleanup wiped
  several running agents' folders).
- Build with plain python (must end 'assembled ...jar'), then python tools/ci/lint.py (0 fails).
- Do not git commit. Edit ONLY the files your task names. Never edit HANDOFF.md, TEST-CHECKLIST.md, DESIGN-STATUS.md, OPEN-QUESTIONS.md,
  tools/deploy_set.py, SkyyGear-Plan.md or SkyyGear-Stat-Catalog.md (Skyy's design docs are read-only).
- Other builders work in parallel on other mods; do not touch their files.

## Return
Script/patch paths, the compile line, what you built, what you left out and why, UNVERIFIED items, and numbered in-game test steps.
