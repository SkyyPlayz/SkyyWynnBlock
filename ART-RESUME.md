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

### 13. Zone 1 town props - the Waiting Room + Waiting Square set (Blockbench, full models)
**Why:** Skyy approved the Zone 1 town plan (docs/answered/world.md 2026-10-08: "keep v2, its hub enough" + yes to every town question).
The town is "the Department of Arrivals": a vanilla temple turned into a cosmic waiting room. Its story props are ours to make (the
buildings are vanilla prefabs). Read `research/cloud/Zone-1-Town-Layout.md` (sections 4, 7, 9), `research/cloud/Story-Script-Draft.md`
(section 2: the Waiting Room, the Board) and `research/cloud/Barks-Signs-Tips.md` (the tone: cheerful bureaucracy, numbers always a bit
wrong). Vanilla temple stone + wood palette so they sit in the temple hall.
**Make (each = model + texture + 64x64 icon, block-sized props like vanilla furniture; look at vanilla `Common/Blocks/...` furniture
models in Assets.zip for scale and file layout), in `art/town-props/Common/...`:**
1. **The Board** - the big glowing "NOW SERVING #3" board (wall-mounted, ~3 blocks wide). Paint the frame and a glowing panel; leave the
   number area plain (the server shows the text as a floating name), plus an "off" / flicker texture variant for Void hiccups.
2. **Ticket machine** - a "PLEASE TAKE A NUMBER" pedestal dispenser (~1 x 2 blocks), with a ticket sticking out.
3. **Waiting bench row** - a long stone + wood bench for the hall (3 blocks long), matching the temple.
4. **Warp Pad** - a flat stone ring set in the paving (5 x 5), with a faint glowing rune inlay (glow texture / emissive if the format allows).
5. **Door Home** - a standing stone arch with a shimmering portal plane (the shard arch players use to go to their island), ~3 x 4 blocks.
6. **Town map sign** - a wooden stand with a painted map of the town ("You Are Here. The Temple Was Here First."), ~2 x 2 blocks; paint
   a simplified version of `research/cloud/Zone-1-Town-Map.png` (our own map, OK to use).
One `sheet.png` with all six + names, manifest with sizes and node names. Original pixels only.
**Ask Skyy (defaults in brackets):** Board colour [amber glow on dark stone], machine style [brass + stone], arch portal colour [the void
purple of the bag swirl].

## Queue (check with Skyy before starting each)
6. **Monk claws** (Blockbench, full items): Wolverine-style long blades from the knuckles on a black LEATHER glove (skywynn-art skill,
   section 3: "CLAWS = Wolverine-style long blades from the knuckles on a black LEATHER glove"), one per metal tier Copper ... Onyxium
   in the shared metal tier colours. Skyy chose "wraps + gauntlets only" for now, so ASK Skyy before starting. Model like the vanilla
   fist / dagger items (look at Assets.zip `Common/Items/Weapons/...`), icon 64x64 per tier.
7. **Pets** (Blockbench, full models): 15 launch pets in Hytale chunky voxel style (research/cloud/Pets-Spec.md + research/cloud/pet-art/
   README.md for the list and the approved v2 look). The pet system is not built yet - ASK Skyy before starting.
9. **Light armor (tier sets)** - NEW DIRECTION 2026-10-08 (docs/answered/gear.md): most armor will come from installed armor mods (e.g. The Armory) as mob drops, so our own armor sets are low priority - ask Skyy before any more armor work. Paused by Skyy ("we can work on the armor more later"); ask Skyy before touching it. Approved looks
   are in the skywynn-art skill, section 3. A separate candidate dark-leather design is in Done (#3).

## Done
### 8. Hotbar ability item icons (2026-10-08)
- Folder: `art/hotbar-items/` - 37 icons (64x64) under `Common/Icons/ItemsGenerated/`: 35 mirror items
  `SkyyClasses_AbilityItem_<Class>_<Ability>.png` (the approved ability glyph on a square class-rimmed tablet with visible thickness,
  so it never reads as the round HUD icon) + 2 utility items `SkyyClasses_AbilityItem_Loadout.png` / `..._Hints.png` (neutral steel
  rim, gold studs). `sheet.png`, `manifest.json`, `README.md`. Scripts: `tools/art/make_hotbar_items.py`, `make_hotbar_sheet.py`,
  `validate_hotbar_items.py` (glyphs reuse the `make_ability_icons.py` painters).
- Spec: `research/cloud/Ability-Input-Design.md` section 2. Item ids / paths are PROPOSED (SkyyClasses phase I2 not built); the
  OPEN-QUESTIONS "keys only" item is still the main session's call.
- Skyy's answers, word for word: "Start the hotbar icons" / "Yes, the hotbar icons look good, commit them"
- Not yet seen in game.

### 12. Class ability icons - Archer (2026-10-08)
- Folder: `art/ability-icons/Common/Icons/Abilities/Archer/` - PinningShot, RapidFire, ExplosiveArrow, ArrowRain, HuntersNet (64x64).
  Shared sheet/manifest/README/scripts updated + `sheet-archer.png`. Leaf-green rim (`#8fd67a`), dark forest field (`#24381c` -> `#091108`).
  Arrow detail pass (v2), as Skyy asked: lit oak shafts with a grain hint + dark nock, barbed steel broadheads with a lit bevel on an
  iron socket, two separate vanes (red with a cream bar + cream cock feather), red thread wrap; Arrow Rain now shows 4 bigger arrows.
  Hunter's Net unchanged (no arrow).
- Skyy's answers, word for word: "If you can, give the arrows a bit more detail." / "Yes, the Archer icons look good, commit them"
- Not yet seen in game. All 7 classes now have ability icons (35 icons).

### 11. Class ability icons - Berserker (2026-10-08)
- Folder: `art/ability-icons/Common/Icons/Abilities/Berserker/` - Enrage, Whirlwind, Earthsplitter, BloodFrenzy, WarlordsBanner (64x64).
  Shared sheet/manifest/README/scripts updated + `sheet-berserker.png`. Blood-red rim (`#d9443f`), dark oxblood field (`#42161e` -> `#120609`).
- Skyy's answer, word for word: "Yes, the Berserker icons look good, commit them"
- Not yet seen in game.

### 10. Class ability icons - Warrior (2026-10-08)
- Folder: `art/ability-icons/Common/Icons/Abilities/Warrior/` - RallyingGuard, ShieldShockwave, IronChain, BulwarkStance, Unbreakable (64x64).
  Shared sheet/manifest/README/scripts updated + `sheet-warrior.png`. Amber-gold rim (`#e0b060`), dark gunmetal field (`#2a3a44` -> `#0b1216`).
- Skyy's answer, word for word: "Yes, the Warrior icons look good, commit them"
- Not yet seen in game.

### 7. Class ability icons - Assassin (2026-10-08)
- Folder: `art/ability-icons/Common/Icons/Abilities/Assassin/` - CloakFirstStrike, Toxin, GodKiller, ShadowClone, VanishingAct (64x64).
  Shared manifest/README/scripts updated + `sheet-assassin.png`. Cloak + First Strike and Shadow Clone: hood v2 (Assassin's-Creed-style
  beak hood + dark grey-violet face mask), as Skyy asked.
- Skyy's answers, word for word: "The hood looks a little weird, do an assassins creed style hood, with a face mask" / "Yes, the Assassin
  hood looks good, commit them"
- Not yet seen in game.

### 5. Class ability icons - Monk (2026-10-08)
- Folder: `art/ability-icons/Common/Icons/Abilities/Monk/` - FlowingForm, PalmStrike, CycloneKick, HundredFists, StillWater (64x64).
  Shared sheet/manifest/README/scripts updated. Cyclone Kick: upright soft brown shoe (Skyy asked for shoes + vertical foot).
- Skyy's answers, word for word: "They all look great, except the cyclone kick. The foot looks weird" / "Either wrap the foot or give his shoes don't leave it bare" / "Use shoes instead, make the foot vertical like the first image" / "Yes, the shoe looks good, commit the Monk icons"
- Not yet seen in game.

### 4. Class ability icons - Mage + Priest (2026-10-08)
- Folder: `art/ability-icons/` - 10 icons under `Common/Icons/Abilities/Mage/` and `.../Priest/` (64x64), `sheet.png`,
  `manifest.json`, `README.md`. Scripts: `tools/art/make_ability_icons.py`, `make_ability_sheet.py`, `validate_ability_icons.py`.
- Mage: Meteor, ManaBarrier, FrostNova, Starfall, ArcaneBeam. Priest: SacredHeal, ShieldBubble, GuardianSpirit, Sanctuary, MartyrsGrace.
- Frame: round dark frame with class-colour rim; dark class-tinted background (defaults from ART-RESUME).
- Skyy's answer, word for word: "The ability icons look great, commit them"
- Not yet seen in game. Remaining classes (Monk, Assassin, Warrior, Berserker, Archer) are Next / Queue — one class per commit.

### 3. Dark Leather light armor - candidate design (2026-10-08)
- Folder: `art/dark-leather-armor/` - Head/Chest/Hands/Legs `.blockymodel` + textures under
  `Common/Items/Armors/SkyyDarkLeather/`, icons `Common/Icons/ItemsGenerated/Armor_SkyyDarkLeather_*.png` (64x64),
  `source/*.bbmodel`, `sheet.png`, `manifest.json`, `README.md`. Scripts: `tools/art/make_dark_leather.py` and related `dl_*.py`.
- Dark charcoal leather, navy tabard, brown straps, amber trim. Half-plate chest with ONE LEFT wrapping pauldron. Slim leather
  half-helm (crest, V brow + amber gem, swept fins, grille visor). 45 boxes / 540 tris. Loads in Blockbench + Hytale plugin; NOT in game.
- Skyy's answers, word for word: "It looks great! But it's supposed to be light armor, so I try to slim it up and scale it down,
  especially the shoulder pads and the helmet, try to make them slim" / "Looks great! If just try to make the shoulder pad wrap
  around the shoulder a little bit if you can" / "Yes commit it as a new possible light armor design"
- This is a **new possible** light armor look, not a wire-in of the existing tier light armor. Main session decides how/whether to use it.

### 2. Accessory Bag menu icon (2026-10-08)
- Folder: `art/accessory-bag-icon/` - icon `Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png` (64x64), `sheet.png`,
  `manifest.json`, `README.md`. Generator scripts: `tools/art/make_accessory_bag_icon.py`, `make_accessory_bag_sheet.py`.
- Gems left to right (Option B): Health red #d23a3a, Stamina yellow #d6a800, Mana blue #2f6fe0, Regeneration green #2fb34f,
  Speed cyan #4ac0cc (cyan = approved Speed accessory wing colour, `tools/art/make_accessory_icons.py`).
- Skyy's answers, word for word: "Use Option B gem colors" / "Make it a little brighter with a more leather look (still black leather,
  just lighter" / "Yes, the bag icon looks good, commit it"
- For the main session: the in-game bag model (`ACC_GEMS` in `tools/art/make_bags.py`) still uses red, blue, yellow, green, violet, so it
  no longer matches this icon - recommend updating it to the Option B order. The Workbench tab can use the same PNG at
  `Icons/CraftingCategories/<Mod>/AccessoriesBags.png` (per `skyywbtab.py`). Not yet seen in game.

### 1. Pebble - the talking rock NPC (2026-10-08)
- Folder: `art/pebble/` (model, 256x192 texture, 128x128 icon, Idle/Walk/Talk/Wave + Damage/Hurt/Death animations,
  `source/Pebble.bbmodel`, `sheet.png`, `manifest.json`, `README.md`). Generator scripts: `tools/art/` (make_pebble.py etc.).
- About 0.99 blocks tall to the sprout tip, 25 nodes; hang the nameplate / chat bubble on the `Head` node (see manifest + README).
- Loads in Blockbench 5.2.1 + Hytale Models 0.10.0; NOT yet tested in game (see README "UNVERIFIED").
- Skyy's answer, word for word: "Pebble looks great, keep it as is"
- Defaults kept: knee-to-hip size, dot eyes + mouth line, moss brows + faint blush, tiny pebble arms, moss + one sprout,
  invulnerable recommended (Death kept as a spare gag), requested `Pebble/Pebble.blockymodel` path kept.
