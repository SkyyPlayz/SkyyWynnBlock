# SkyWynn - ART RESUME (for the art agent)

You are the SkyWynn ART agent. You make finished, game-ready art (Blockbench models, textures, icons, animations) for Skyy's
Hytale server pack. Skyy (they/them) starts you and reviews your work. The main session (another Claude) wires finished art into the mods
and deploys - you never build mods or deploy.

## Read first (in this order)
1. `.claude/skills/skywynn-art/SKILL.md` - Skyy's art rules (detail level, real game things only, styles per family). Mandatory.
2. The Blockbench skills: `blockbench-use` first, then `blockbench-hytale` (Hytale formats, UV density, attachments, visibility keyframes),
   plus `blockbench-modeling` / `blockbench-texturing` / `blockbench-animation` as the job needs.
3. The item's section below, and the files it names.

## Blockbench on this PC
- Blockbench + the Hytale Models plugin + the Blockbench MCP plugin are installed. The MCP runs through the stdio bridge
  `tools/bb_mcp_stdio.py` (Avast breaks localhost HTTP) - Blockbench must be OPEN before your session starts, or the tools won't load.
- Hytale models are `.blockymodel` JSON + a PNG texture. Look at vanilla ones read-only in
  `C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\Assets.zip` (copy into `tools/dev/scratch/art-<item>/` to open;
  never edit the game files). A vanilla player model for fit checks is in `models-local/player/`.
- Save every Blockbench project as `models-local/blockbench-saves/<Item>.bbmodel`.

## Rules (the same for every item)
- Game files and `C:\Users\SkyLo\AppData\...\UserData` are READ-ONLY. Never start or close the game. Never deploy, never run
  `tools/deploy_set.py`, never edit mod build scripts or `tools/*_patch.py`.
- Never edit RESUME.md, HANDOFF.md, OPEN-QUESTIONS.md, TEST-CHECKLIST.md, PROJECT-RULES.md or docs/ - the main session owns them.
- The repo is PUBLIC: vanilla files or copies / recolours of vanilla art never go into git. Original art may be committed ONLY as a
  generator script in `tools/art/` (optional); the finished files themselves live in `models-local/` (git-ignored).
- Scratch only under `tools/dev/scratch/art-<item>/` and delete it when done.
- Git: you may commit and push ONLY `ART-RESUME.md` and new files in `tools/art/` (`git pull --rebase --autostash` first, `git add <those
  files>` - never `git add -A`). End commit messages with `Co-Authored-By: Claude <noreply@anthropic.com>`.
- Ask Skyy before any design choice that is theirs; give a recommended default.

## Where finished items go (every item)
Put everything in `models-local/art/<item>/`, laid out like the inside of a mod jar so the main session can copy it straight in:
```
models-local/art/<item>/
  Common/...            the .blockymodel, texture PNGs, icon PNG, .blockyanim files - at the paths named in the item's section
  sheet.png             one preview image Skyy can review: front / side / back, the icon, a frame from each animation
  manifest.json         every file: its path, size, what it is; animation names + lengths; the model's node names (for attachments / effects)
  README.md             what it is, how it was made, sizes, what is UNVERIFIED in game, open questions for Skyy (each with a default)
```
Then: (1) show Skyy `sheet.png` and ask for their OK, (2) in this file move the item to **Done** with the folder path and Skyy's answer
word for word, (3) commit + push ART-RESUME.md, (4) tell Skyy "ready for the main session to wire in". Then start the next item.

## NEXT ITEM

### 1. Pebble - the talking rock NPC (Zone 1 town + starter shards)
**Who:** Pebble is the guide of SkyWynn: a talking rock who has been "here four thousand years" (ticket #2, "been next" for 4,000 years),
gives terrible advice with total confidence, rounds every number up, cheerful and wrong. Stands in the Waiting Square in front of the Zone 1
temple; later walks you through the starter shards. Lines like "Pebble would be impressed. Pebble is a rock." Sources:
`research/cloud/Barks-Signs-Tips.md`, `research/cloud/Player-Guide-First-Hour.md`, `research/cloud/Zone-1-Town-Layout.md` (section 8).

**Why now:** the town build needs an NPC model for Pebble; vanilla has no rock creature (the only rock model is a tiny thrown rubble chunk,
`Rubble_Stone_Mossy`). Decision: `docs/answered/world.md` 2026-10-08 (Skyy said yes to the town plan incl. Pebble).

**What to make (game-ready):**
- A chunky Hytale-style mossy grey stone, about **knee to hip high on a player** (roughly 0.9-1.1 blocks), with a simple friendly face
  (eyes + a mouth line, maybe moss eyebrows), small stubby stone feet so it can waddle, moss + a tiny flower or sprout on top. Vanilla
  stone / moss palette (look at vanilla rock and moss block textures for colours - do not copy them).
- Pixel density at least vanilla creature level (Rabbit texture 160x160 is the reference; ideally 2x the detail of our old v1 sheets).
- Model: `Common/NPC/SkyyTowns/Pebble/Pebble.blockymodel` + `Pebble_Texture.png`.
- Icon: `Common/Icons/ModelsGenerated/Pebble.png` (128x128, like vanilla model icons).
- Animations (`.blockyanim`, in `Common/NPC/SkyyTowns/Pebble/Animations/Default/`, like vanilla
  `Common/NPC/Livestock/Rabbit/Animations/Default/Idle.blockyanim`): **Idle** (slow breathing wobble, blink), **Walk** (waddle on the stubby
  feet), **Talk** (mouth moves, little bounce), **Wave** (a pebble-arm or a hop - your call, keep it cute), plus **Hurt** / **Death** in
  `Animations/Damage/` if quick (a wince, a crumble-and-pop-back - it is a rock). Copy the vanilla Rabbit's folder layout and file naming.
- Keep the node names in the manifest (the main session hangs a nameplate / chat bubble on the head node).

**Ask Skyy (defaults in brackets):** size [knee-to-hip], face style [simple dot eyes + mouth line], extras on top [moss + one small sprout].

## Queue (after Pebble - check with Skyy before starting each)
2. **Accessory Bag icon** for the SkyWynn Menu tile + the Workbench "Accessories & Bags" tab: today both still show the vanilla bag. The new
   Accessory Bag model is in `models-local/art/bags/` (black leather satchel, gold handle + clasp, 5 small gems). Make a 64x64 icon in the
   same framing as vanilla item icons -> `models-local/art/accessory-bag-icon/Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png`.
3. **Hotbar ability item icons** - WAIT until the ability-input design is approved (`research/cloud/Ability-Input-Design.md`, being written).
4. **Light armor (paused by Skyy: "we can work on the armor more later")** - ask Skyy before touching it. Work files are in
   `models-local/light-armor/` and `models-local/blockbench-saves/`; approved looks in the skywynn-art skill section 3.

## Done
(nothing yet)
