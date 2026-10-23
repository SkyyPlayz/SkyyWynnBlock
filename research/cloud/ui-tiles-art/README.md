# SkyWynn Menu picture tiles - phase 1 (the 8 Home tiles) - CONCEPT v1, cloud art 2026-10-22

**Status: DRAFT for Skyy's review.** Start here: `sheet.png` (all 8 at 2x and 1x with the label bar mock, plus the default Home grid at 1x).

Why: Skyy 2026-10-22 on Hylterium's illustrated hub tiles: "i like the pictures they have on this menu." (research/UI-Ideas.md
"MENU TILE PICTURES"; spec research/UI-Queue-Spec.md item 8; reference `research/refs/menu-hub-hylterium.webp` stays local and was only
looked at for the LOOK - busy close-up scene, bright colours, depth, sparkles, blue label bar, gold frame. Nothing traced or copied.)
Rules followed: `.claude/skills/skywynn-art/SKILL.md` (real game things, our approved family looks, deterministic generator).

This is the first version - no older sheet to keep (`*-v<N>.png` starts with the next redraw).

## What each picture shows (all our own drawings of real game things)

| File stem | Label | Shortcut key | Default Home slot | Scene |
|---|---|---|---|---|
| `tab_world_teleport` | Teleport | `tab:world:teleport` | 12 (centre) | a grass sky island with a stone-brick arch holding a swirling cyan / violet shard portal, small far islands |
| `hub_character` | Character | `hub:character` | 7 | an adventurer in black leather + copper trim (our approved T1 light armor look) on grass blocks, ringed by 6 skill badges: pickaxe (Mining), sword (Combat), wheat (Farming), fish (Fishing), hatchet (Foraging), flask (Alchemy) |
| `hub_storage` | Storage | `hub:storage` | 11 | a round iron bank vault door with a gold wheel, a wooden chest (iron bands, gold lock), the Pocket Dimension pouch with violet sparkles (bags.md: violet = SkyySack_PortalSparkle), coins |
| `hub_market` | Market | `hub:market` | 17 | a Bazaar stall: striped awning, coin sign, crates of wheat / apples / carrots / fish, gold coin stacks |
| `hub_smithing` | Crafting | `hub:smithing` | 13 | the anvil with a glowing ingot + hammer and sparks, a workbench with a flask and ingots, tools on the wall, a cooking pot, a finished sword |
| `hub_world` | World | `hub:world` | none (see Q2) | three floating islands (oak + blossom trees, a waterfall) and a gold compass rose |
| `hub_social` | Social | `hub:social` | 6 | three players waving on a grassy hill, a heart chat bubble, a party star |
| `hub_settings` | Settings | `hub:settings` | 8 | steel / gold / copper gears on a blueprint grid + an **ALT** key cap (the SkyWynn Menu key since 2026-10-22) |

## Files

| File | What |
|---|---|
| `tiles/<stem>@2x.png` | 232 x 232 RGBA, the picture (soft 3 px corners at 1x); bottom 44 px (22 at 1x) is meant to sit under the label bar |
| `tiles/<stem>.png` | 116 x 116, the 1x copy (2 x 2 box filter) |
| `sheet.png` | review sheet, 2136 x 1250 |
| `manifest.json` | every file: path, size, bytes, sha256, + the tile list (stem, label, key, Home slot) |
| `make_tiles.py` | the generator; `--check` rebuilds in memory and compares with the manifest (SAME BYTES checked) |
| `skyypaint.py`, `skyyitems.py` | the shared pure-Python painter (zlib only, no Pillow - Pillow is not installed locally) + the item glyphs; `research/cloud/page-emblems-art/make_emblems.py` imports them too |

Run: `python research/cloud/ui-tiles-art/make_tiles.py` (~8 s). No vanilla file, other mod or reference picture is read.

## Questions for Skyy (default in brackets)

1. Do these 8 scenes say what each area is, and is the look right (chunky voxel scenes, bright, busy like the reference)? [yes - build
   phase 2 (31 hub tabs + My Island / Hub / Spawn) in the same look after your OK]
2. World is not on the default Home since SkyyMenu 0.3.30 (the Teleport centre opens the same page). Keep its picture for players who pin
   it? [yes, keep it; default Home unchanged]
3. Settings shows an "ALT" key cap (the menu key). Keep the word even for players who rebound Walk? [yes - same as the hotbar hint rule
   "ALT - Menu"; else a plain gear-only picture]
4. Character wears our T1 light armor (black leather + copper). Show the player's class colour instead? [no - one fixed picture; the
   pictures are static per build]

## For the local session

- Ship as OUR art (committable, not vanilla-derived): copy `tiles/<stem>@2x.png` into the SkyyMenu jar at
  `Common/UI/Custom/SkyyMenu/Tiles/<stem>@2x.png`; markup references `SkyyMenu/Tiles/<stem>.png` (no `@2x`, the client loads the @2x - the
  proven Group Background path, UI-Queue-Spec 8). The 1x files are only for previews / the sheet; ship them only if a build needs 1x.
- File names = the shortcut key with `:` -> `_` (like `TAB_ART` / `SkyyHubTabs/<hub>_<tab>@2x.png`). `hub:smithing` keeps its key, its
  label is "Crafting" (HUB_TITLE31).
- Sizes: slot 120 x 120 (`SLOT30`), picture 116 x 116 at 2 px inset, label bar 22 px at the bottom (kit blue `#4274a5` at 0.9, label 15
  bold white), 2 px gold edge `#E8A93B` on hover / selected. The bar / text / edge are page elements, NOT baked into the PNG (the sheet only
  mocks them). Tiles without a picture keep today's `MENU_ICON_OF` icon.
- Slot numbers on the sheet = SkyyMenu 0.3.44 `BUILTIN_HOME` (5 x 5 numbering `row * 5 + col`): 12 Teleport, 7 Character, 11 Storage,
  13 Crafting, 17 Market, 6 Social, 8 Settings.
- Size budget: 8 x ~37-89 KB @2x = ~466 KB.
- UNVERIFIED: the in-game crispness at 120 px on the sky theme (probe T1, UI-Queue-Spec 11) - a look check after the jar build.
- The spec named the folder `research/cloud/menu-tiles-art/`; this task wrote `research/cloud/ui-tiles-art/` - please point
  `research/cloud/ART-INDEX.md` / `INDEX.md` here (this session could not edit them).
- After Skyy answers: record the words with `python tools/qa_append.py ui <file> --no-question` (skywynn-art hand-off).
