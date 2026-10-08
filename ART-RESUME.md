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

### 1. Pebble - the talking rock NPC (Zone 1 town + starter shards)
**Who:** Pebble is the guide of SkyWynn: a talking rock who has been "here four thousand years" (ticket #2, "been next" for 4,000 years),
gives terrible advice with total confidence, rounds every number up, cheerful and wrong. Stands in the Waiting Square in front of the Zone 1
temple; later walks new players through the starter shards. Lines like "Pebble would be impressed. Pebble is a rock." Background:
`research/cloud/Barks-Signs-Tips.md`, `research/cloud/Player-Guide-First-Hour.md`, `research/cloud/Zone-1-Town-Layout.md` (section 8).

**Why now:** the Zone 1 town build needs an NPC model for Pebble, and vanilla Hytale has no rock creature.

**What to make (game-ready):**
- A chunky Hytale-style mossy grey stone, about **knee to hip high on a player** (roughly 0.9-1.1 blocks), with a simple friendly face
  (eyes + a mouth line, maybe moss eyebrows), small stubby stone feet so it can waddle, moss + a tiny sprout on top. Stone / moss colours
  in the vanilla palette (match the look, paint your own pixels).
- Pixel density at least vanilla creature level (the vanilla Rabbit uses a 160x160 texture; more detail is welcome).
- Model + texture: `Common/NPC/SkyyTowns/Pebble/Pebble.blockymodel` + `Common/NPC/SkyyTowns/Pebble/Pebble_Texture.png`.
- Icon: `Common/Icons/ModelsGenerated/Pebble.png` (128x128, like vanilla model icons).
- Animations: `Common/NPC/SkyyTowns/Pebble/Animations/Default/` **Idle** (slow breathing wobble, blink), **Walk** (waddle on the stubby feet),
  **Talk** (mouth moves, little bounce), **Wave** (a pebble-arm or a hop - your call, keep it cute); if quick, `Animations/Damage/`
  **Hurt** (a wince) + **Death** (crumble, then pop back - it is a rock). Use the same folder layout and naming as vanilla creatures
  (e.g. the Rabbit: `Common/NPC/Livestock/Rabbit/Animations/Default/Idle.blockyanim`).
- List the node names in the manifest (the main session hangs a nameplate / chat bubble on the head node).

**Ask Skyy (defaults in brackets):** size [knee-to-hip], face style [simple dot eyes + mouth line], extras on top [moss + one small sprout].

## Queue (after Pebble - check with Skyy before starting each)
2. **Accessory Bag menu icon** (64x64): the SkyWynn Menu tile and the Workbench "Accessories & Bags" tab still show the vanilla bag. The new
   Accessory Bag is a black leather satchel with a gold handle + small gold clasp and 5 tiny gems in a row (the 5 accessory-line
   colours). Ask Skyy for a screenshot of it in game, then draw an ORIGINAL 64x64 icon in vanilla item-icon framing ->
   `art/accessory-bag-icon/Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png`.
3. **Hotbar ability item icons** - WAIT until Skyy approves the ability-input design (`research/cloud/Ability-Input-Design.md`).
4. **Light armor** - paused by Skyy ("we can work on the armor more later"); ask Skyy before touching it. Approved looks are in the
   skywynn-art skill, section 3.

## Done
(nothing yet)
