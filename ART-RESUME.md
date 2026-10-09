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

### 14. Gathering armor - FORAGING (bark plates) + FARMING (crop sets), full game-ready models
**Why:** Skyy 2026-10-08 (docs/answered/gear.md, ARMOR SPLIT): "lets still make the farming and gathering armor, but use vanilla for
mining, and armory for combat gear." Mining = vanilla metal armor, combat = The Armory pack, so these two families are the only armor we
make ourselves. The LOOKS are approved: read every gear.md line about FORAGING / FARMING armor (2026-10-05 / 06; newest wins), the concept
sheets + READMEs in `research/cloud/foraging-armor/` and `research/cloud/gathering-armor-art/` (farming = crop sets), and the specs
`research/cloud/Foraging-Armor-Design.md` (section 2 tier table) and `research/cloud/Crop-Armor-Spec.md` (section 1 the seven sets).
**Order:** Foraging first, lowest tier first, one tier per commit, show Skyy each tier's sheet:
- Foraging (Skyy 2026-10-08: "do a design per tree type in that set, so every hardwood gets its own design in that trees color"):
  one 4-piece design PER TREE TYPE, in that tree's wood + leaf colours, grouped by the 5 tree tiers (research/Gathering-Progression-Spec.md 2.2):
  F1 Grove: Oak, Birch, Beech, Ash, Aspen | F2 Autumn + Azure: Maple, Azure | F3 Savanna: Gumboab, Dry, Bottletree, Palo |
  F4 Northern: Redwood, Fir, Cedar, Poisoned, Spiral | F5 Wastes: Sallow, Burnt, Petrified, Bamboo, Camphor, Banyan, Jungle, Blue Fig, Fire, Crystalwood.
  Same bark-plate family look (approved concept), each tree its own variation; trees of one tier share stats and players swap looks at an
  alteration station later. Start with F1 Oak (key log), then the rest of F1, one tree per commit; show Skyy each sheet. Paths use the
  tree name: `SkyyForaging/<Tier>/<Tree>/<Piece>.blockymodel`, icons `Armor_Foraging_<Tree>_<Piece>.png`. Orchard trees: later.
- Farming: Wheat, Carrot, Cauliflower, Pumpkin, Chilli, Cotton, Onion ("more like the wood ones ... food armor, like in skyblock").
**Make, per tier:** 4 pieces - Head, Chest, Hands, Legs - exactly like a vanilla armor set (look at vanilla Iron in Assets.zip:
`Common/Items/Armors/Iron/{Head,Chest,Hands,Legs}.blockymodel` + `<Piece>_Texture.png`, icons `Common/Icons/ItemsGenerated/Armor_Iron_<Piece>.png`;
fit them on the vanilla player model). Our paths: `art/gathering-armor/Common/Items/Armors/SkyyForaging/<Tier>/<Piece>.blockymodel` +
`<Piece>_Texture.png`, icons `Common/Icons/ItemsGenerated/Armor_Foraging_<Tier>_<Piece>.png` (Farming: `SkyyFarming/` and
`Armor_Farming_<Crop>_<Piece>`). At least vanilla texture density (vanilla armor textures: Chest 192x64, Head 160x64, Legs 128x64,
Hands 64x64), original pixels only. Per tier a `sheet-<tier>.png` (front / side / back on the player, the 4 icons); one shared
`manifest.json` + `README.md` + `source/*.bbmodel`.
**Ask Skyy (defaults):** keep the concept looks as approved [yes]; helmet in every tier [yes].

## Queue (check with Skyy before starting each)
16. **Chibi pets - start with the SKELETON** (Skyy 2026-10-08: "add the pet chibi list to quirks queue start with the skeleton, and well go
   from there."). Pets are every neutral mob + many enemies; at launch each pet is the vanilla mob model shrunk, and you make CHIBI versions
   of the favourites (docs/answered/pets.md 2026-10-08: "i want all the pets of them to be similar just a little smaller and cuter ... like
   a skeleton pet would be about fox size"). Chibi = clearly the same creature (same colours, key features), bigger head, shorter stubbier
   body / legs, big eyes or eye sockets, cute not scary. Size: about a vanilla Fox (look at `Common/NPC/Beast/Fox` and the vanilla Skeleton
   in `Common/NPC/Undead/Skeleton` in Assets.zip - match its look, paint your own pixels). Make: model + texture + 128x128 icon + animations
   Idle, Walk, Run, Sit (pets sit while you stand still), Happy (a little hop / spin when fed or petted), Hurt - same folder layout + names as a
   vanilla creature (`Animations/Default/`). Paths `art/pets/<Creature>/Common/NPC/SkyyPets/<Creature>/<Creature>.blockymodel`, icon
   `Common/Icons/ModelsGenerated/SkyyPet_<Creature>.png`. One sheet, then show Skyy. The full favourites list (top 15) comes from
   `research/Pets-Roster.md` (being written) - after the Skeleton, ask Skyy which is next.
15. **Mystery bags - unidentified loot, ONE per rarity (7)** (Skyy 2026-10-08: "make the mystery bags unidentified items come in before you
   identify them. we just need 1 per rarity."). A dropped / looted unidentified weapon or armor piece shows as a closed loot bag until the
   player identifies it (Wynncraft style: level + rarity shown, type hidden). Rarities + colours (placeholders from
   research/cloud/Loot-Box-Design.md, ask Skyy to confirm): Normal white, Unique yellow, Rare magenta, Legendary cyan, Fabled red, Mythic
   purple, Set green - richer bags for higher rarities (more trim, a gem, a glow / sparkle on Mythic). Keep them clearly different from
   our Pocket Dimension bags (black pouch + portal swirl) - e.g. a tied cloth sack with a wax seal / tag in the rarity
   colour. Make: model + texture + 64x64 icon per rarity, a dropped look, `art/mystery-bags/Common/Items/SkyyGear/MysteryBag/<Rarity>.blockymodel`,
   icons `Common/Icons/ItemsGenerated/SkyyGear_MysteryBag_<Rarity>.png`, one sheet. Ask Skyy which to do first: this or the gathering armor.
13. **Zone 1 town props** (was NEXT; moved behind the gathering armor 2026-10-08) - - the Waiting Room + Waiting Square set (Blockbench, full models)
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
9. **Armor** - DECIDED 2026-10-08 (docs/answered/gear.md): our own Light armor is DROPPED (combat armor = The Armory pack), MINING armor = vanilla metal sets (no art needed). Still OURS: FARMING (crop sets) + FORAGING (bark plates) armor - approved concept designs in research/cloud/gathering-armor-art/ + foraging-armor/; ask Skyy before starting them as full Blockbench items.

- **Known issue - Pebble mirrored UVs (fix pending Skyy's OK):** found while making the pets. Blockbench 5.2.1 + Hytale Models 0.10.0 read a
  mirrored face's `offset.x` as the RIGHT edge of its texture region. The committed Pebble (`art/pebble/`) likely has the mirrored
  right-side parts' offsets wrong (R-Foot, R-Arm, R-Brow, Sprout-Leaf-R use the same offset as their L twin), so those faces may sample
  the wrong pixels / show seams. Not fixed - waiting for Skyy. The pets generator already writes mirrored offsets the right way.

## Done
### 7. Pets - 15 launch pets (2026-10-08)
- Folder: `art/pets/` - per pet `Common/NPC/SkyyPets/<Pet>/Models/<Pet>.blockymodel` + `<Pet>_Texture.png` and
  `Animations/Default/{Idle,Walk,Run|Fly}.blockyanim`; icons `Common/Icons/ModelsGenerated/SkyyPets_<Pet>.png` (128) and
  `Common/Icons/ItemsGenerated/SkyyPets_Pet_<Pet>.png` (64); `source/<Pet>.bbmodel`, `sheet.png`, `manifest.json`, `README.md`.
  Pets: Rabbit, Chicken, Goat, Warthog, Bear, Turkey, Wolf, Boar, Hawk, Ram, Skrill (original "stormwing"), Tusker, Mouflon, Horse, Camel.
  Scripts: `tools/art/make_pets.py`, `pets_models.py`, `pets_anims.py`, `pets_common.py`, `pets_render.py`, `make_pets_previews.py`,
  `make_pets_manifest.py`, `validate_pets.py`, `bb_validate_pets.js`.
- Look: cute Hytale chunky voxel (big friendly eyes, soft shapes, painted light). v2 redid the 4 rideables after Skyy's review: Horse on
  vanilla-horse proportions (long neck + head, mane, feathered cuffs, hooves), two-hump Camel, a tough war Ram (spiral horns, heavy brow,
  steel chest plate), a clearly wild Mouflon (red coat, white belly, crescent horns, Priest tack). Original art; vanilla only looked at.
- Ids are PROPOSED (pet system not built): item `SkyyPets_Pet_<Pet>`, model / NPC `SkyyPets_<Pet>`, name key `skyypets.pet.<pet>.name`;
  nameplate on `Head`, rider seat on `Saddle`. Loads clean in Blockbench 5.2.1 + Hytale Models 0.10.0 (no validator issues, all
  45 animations bind).
- Skyy's answers, word for word: "keep the kinda hytale style, and make the pets cute." / "Numbers 10 13 14 and 15 look a little weird.
  Check the hytale horses skins, and make it look more like them. The Ram looks dorky. It needs to look a little more tough and
  aggressive, and also a little more like an actual ram. The camel just looks a little weird and I'm not even sure what the other
  creature is" / "Yes, the pets look good, commit them"
- Not yet seen in game. UNVERIFIED: NPC/asset JSON, anim slot names, mount seat, 0.6x -> 1.0x level scaling (see README).

### 6. Monk claws - 7 metal tiers (2026-10-08)
- Folder: `art/monk-claws/` - `Common/Items/Weapons/Fist/SkyyArmory_Claws_<Tier>.blockymodel` + `_Texture.png` (64x128) and icons
  `Common/Icons/ItemsGenerated/SkyyArmory_Fist_Claws_<Tier>.png` (64x64) for Copper, Iron, Thorium, Cobalt, Adamantite, Mithril,
  Onyxium; optional equip animation `Common/Items/Weapons/Animations/SkyyArmory_Claws/SkyyArmory_Claws_Extend.blockyanim` (0.4 s, holds),
  `source/*.bbmodel`, `sheet.png`, `manifest.json`, `README.md`. Scripts: `tools/art/make_monk_claws.py`, `make_monk_claws_sheet.py`,
  `mc_render.py`, `bb_validate_claws.js`. Same ids / paths as the local `models-local/art/fists` claws, so they replace those.
- Redesign (original, own palettes): black leather fist glove under a metal skeletal frame (carpal plate with a saffron Monk diamond,
  4 finger bones, knuckle caps, finger segments), 3 long curved stepped blades from between the knuckles (middle one longest), studded
  wrist cuff + wound leather strap + saffron cord. Mithril gold trim, Onyxium black-violet. 44 boxes / 528 tris. Skyy's reference
  picture stays local (not committed). Loads clean in Blockbench 5.2.1 + Hytale Models 0.10.0 (Validator: no errors / warnings).
- Skyy's answers, word for word: "Monk claws next, but they need a redesign to look like this (with claws out. Ignore the collapse
  stages, unless you want to animate them popping out when you equip them.)" / "Yes, the Monk claws look good, commit them"
- Not yet seen in game. UNVERIFIED: equip-animation trigger, IconProperties, left-hand mirroring (see README).

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
