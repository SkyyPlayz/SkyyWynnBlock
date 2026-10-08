# SkyWynn - ART RESUME (for the art agent)

You are the SkyWynn ART agent. You make finished, game-ready art (Blockbench models, textures, icons, animations) for Skyy's
Hytale server pack, on YOUR OWN machine with your own Blockbench. Skyy (they/them) owns the project and reviews your work. Skyy's main
session (another Claude, on Skyy's PC) pulls your finished art from this repo, wires it into the mods and deploys - you never build mods
or deploy.

## Read first (in this order)
1. `.claude/skills/skywynn-art/SKILL.md` (in this repo) - Skyy's art rules: detail level, real game things only, styles per family. Mandatory.
2. The item's section below and the files it names.
3. If your Claude has the Blockbench MCP skills (`blockbench-use`, `blockbench-hytale`, `blockbench-modeling`, `blockbench-texturing`,
   `blockbench-animation`), load them before working. They come from github.com/jasonjgardner/blockbench-mcp-project (`skills/`).

## Tools you need (on your machine)
- Blockbench with the **Hytale Models** plugin (File > Plugins), for the `.blockymodel` / `.blockyanim` formats.
- Optional: the Blockbench MCP plugin so Claude can drive Blockbench.
- A Hytale install, to LOOK at vanilla models for scale, style and file layout: they are inside the game's `Assets.zip`
  (`Common/NPC/...`, `Common/Items/...`, `Common/Icons/...`). Read-only - never copy vanilla files into the repo.

## Rules (the same for every item)
- The repo is PUBLIC. Everything you commit must be ORIGINAL work: no vanilla Hytale files, no copies, edits or recolours of vanilla
  models / textures, nothing from other mods or other people's art. Looking at vanilla for scale and style is fine; tracing is not.
- You may commit ONLY: your item folder under `art/`, `ART-RESUME.md`, and (optional) a generator script in `tools/art/`.
  Never edit mod build scripts, `tools/*_patch.py`, `tools/deploy_set.py`, RESUME.md, HANDOFF.md, OPEN-QUESTIONS.md, TEST-CHECKLIST.md,
  PROJECT-RULES.md or anything in `docs/` - Skyy's main session owns those.
- Git: `git pull --rebase --autostash` before you push; stage files by name (`git add art/<item> ART-RESUME.md`), never `git add -A`.
  Commit with a GitHub noreply email, never a personal address. End commit messages with `Co-Authored-By: Claude <noreply@anthropic.com>`.
- Ask Skyy before any design choice that is theirs; give a recommended default.

## Where finished items go (every item)
Put everything in `art/<item>/` in this repo, laid out like the inside of a mod jar so the main session can copy it straight in:
```
art/<item>/
  Common/...            the .blockymodel, texture PNGs, icon PNG, .blockyanim files - at the paths named in the item's section
  source/<Item>.bbmodel your Blockbench project (so it can be edited later)
  sheet.png             one preview image Skyy can review: front / side / back, the icon, a frame from each animation
  manifest.json         every file: its path, size, what it is; animation names + lengths; the model's node names (for attachments / effects)
  README.md             what it is, sizes, how to edit it, what is UNVERIFIED in game, open questions for Skyy (each with a default)
```
Then: (1) show Skyy `sheet.png` and ask for their OK, (2) in this file move the item to **Done** with its folder and Skyy's answer word
for word, (3) commit + push, (4) tell Skyy "ready for the main session to wire in". Then start the next item.

## NEXT ITEM

### 2. Accessory Bag menu icon
Next in the queue below - check with Skyy before starting.

## Queue (after Pebble - check with Skyy before starting each)
2. **Accessory Bag menu icon** (64x64): the SkyWynn Menu tile and the Workbench "Accessories & Bags" tab still show the vanilla bag. The new
   Accessory Bag is a black leather satchel with a gold handle + small gold clasp and 5 tiny gems in a row (the 5 accessory-line
   colours). Ask Skyy for a screenshot of it in game, then draw an ORIGINAL 64x64 icon in vanilla item-icon framing ->
   `art/accessory-bag-icon/Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png`.
3. **Hotbar ability item icons** - WAIT until Skyy approves the ability-input design (`research/cloud/Ability-Input-Design.md`).
4. **Light armor** - paused by Skyy ("we can work on the armor more later"); ask Skyy before touching it. Approved looks are in the
   skywynn-art skill, section 3.

## Done
### 1. Pebble - the talking rock NPC (2026-10-08)
- Folder: `art/pebble/` (model, 256x192 texture, 128x128 icon, Idle/Walk/Talk/Wave + Damage/Hurt/Death animations,
  `source/Pebble.bbmodel`, `sheet.png`, `manifest.json`, `README.md`). Generator scripts: `tools/art/` (make_pebble.py etc.).
- About 0.99 blocks tall to the sprout tip, 25 nodes; hang the nameplate / chat bubble on the `Head` node (see manifest + README).
- Loads in Blockbench 5.2.1 + Hytale Models 0.10.0; NOT yet tested in game (see README "UNVERIFIED").
- Skyy's answer, word for word: "Pebble looks great, keep it as is"
- Defaults kept: knee-to-hip size, dot eyes + mouth line, moss brows + faint blush, tiny pebble arms, moss + one sprout,
  invulnerable recommended (Death kept as a spare gag), requested `Pebble/Pebble.blockymodel` path kept.
