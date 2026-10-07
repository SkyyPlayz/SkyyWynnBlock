---
name: skywynn-art
description: Rules for making SkyWynn concept art and icons (armor sets, weapons, tools, accessories, pets, Enchanted materials, emblems, maps) the way Skyy approved them. Use before drawing or redrawing ANY SkyWynn art sheet or icon, local or cloud.
---

# SkyWynn art - how Skyy wants it (from Skyy's reviews, docs/answered/gear.md + pets.md + world.md, 2026-10-05/06)

Read the newest lines for your subject first: `grep -n "art review\|references\|LIGHT ARMOR\|MINING\|ENCHANTED\|PETS" docs/answered/gear.md docs/answered/pets.md docs/answered/world.md`.
The newest line wins. Skyy's word-for-word answers live there; never re-decide a LOCKED line.

## 1. Detail and size
- At LEAST vanilla Hytale density, ideally **2x-4x the detail** of the v1 cloud sheets (Skyy: "seems a little Pixley").
- Vanilla reference sizes (Assets.zip): armor model textures Mithril Chest 192x64, Head 160x64, Legs 128x64, Hands 64x64; item icons 64x64;
  creature texture (Rabbit) 160x160, model icons 128x128.
- Concept sheets: front + back per tier, a label + level band under each, the tier's metal swatch; keep the generator script next to the sheet
  (`make_*.py`, deterministic: two runs = same bytes).

## 2. Real game things only
- **Use what the game actually has.** Check every item id against Assets.zip (cloud: ask the local session, mark UNVERIFIED). Skyy:
  "make sure you are going off of what the game actually has, not just making up whatever looks good."
- Enchanted materials = a **shiny copy of the vanilla resource**: metals compress from INGOTS (not ore), stone = Cobblestone + Rubble (all
  rubble kinds count as Rubble), logs ARE blocks (one Enchanted log per log, no separate "log block"). Ratio 100.
- Junk / filler items = existing vanilla items (sticks, fibre, rubble, shells ...), no invented junk unless it has a real use.
- Our items never reuse a pack mod's id (More Crossbow Tiers, Frah's Crossbow Tiers ...) - pick ids like `..._Wynn` and check.

## 3. Style per family (approved looks)
- **Metal tier colours** (shared by every family): Copper copper, Iron grey, Thorium green, Cobalt blue, Adamantite red, Mithril pale cyan
  (vanilla Mithril helmet WINGS), Onyxium purple / gold (crown + horns). Each tier echoes the vanilla metal armor / helmet of that tier.
- **Light armor**: black leather + metal trim per tier (approved). HELMETS: hard metal helms, NEVER a cloth hood (Skyy disliked the hood,
  esp. the back); Corinthian / sallet / closed / Spartan / horned / winged / crowned per tier; contrasting trim metal. Masks = a later idea, not on helmets.
- **Heavy** tier 1 = heavy leather; **Cloth** tier 1 = Crude Robe (green, crystal shards) - both approved.
- **Mining armor**: HALF PLATE build (rounded embossed pauldrons, segmented breastplate, plated arms + gauntlets, crossed straps + buckled belts),
  the WHOLE armor in the tier's metal colour, NO skirt / tabard, keeps the v2 helmets + the working lamp; starts at Copper.
- **Foraging armor**: bark plates + sap veins (approved); Goldenwood helmet = Mithril-style wings.
- **Farming armor**: crop-themed v2 (approved).
- **Weapons**: wood handle + metal head + leaf crystals (wands, staffs); soul cage floats over the palm and slowly spins; CLAWS = Wolverine-style
  long blades from the knuckles on a black LEATHER glove (3D reference: a skeletal metal glove, blades extend from the knuckles).
- **Accessory icons**: one object per line, rarity = growing gem + metal (approved); Stamina icon = a LIGHTNING BOLT like the vanilla Stamina symbol.
- **Pets**: Hytale-style chunky voxel models (v2 approved); the dragon icon looks like the Dragon Nestkeeper dragons - an ORIGINAL drawing in
  that style until Aures allows using their model.
- **Class emblems**: approved; Monk = wrapped fist (not claws), colour Saffron #f08a30; soul-cage emblem uses the v2 soul cage.
- **Zone 1 town**: organic, SkyBlock-Hub-like roads around the vanilla temple at the centre right behind spawn.

## 4. References and copyright
- Skyy's reference pictures are other people's art: they stay LOCAL in `research/refs/` (git-ignored) and are DESCRIBED in words in
  docs/answered/ - never commit, trace or copy them; cloud sessions work from the written description.
- Vanilla textures: never commit them; recolours of vanilla art are GENERATED at build time into the jar (tools/skyyart.py).

## 5. Hand-off
- Output in `research/cloud/<family>-art/` (cloud) with a README: what changed vs the previous version, the old sheet kept as `*-v<N>.png`,
  open questions for Skyy (each with a default), and "For the local session" (every UNVERIFIED id / size).
- Show Skyy the SHEET (one image per family), then record the answer word for word (`python tools/qa_append.py gear <file> --no-question`).
