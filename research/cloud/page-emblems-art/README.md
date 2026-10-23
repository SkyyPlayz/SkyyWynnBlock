# Radial page emblems (Radial-Trees-Spec R4) - CONCEPT v1, cloud art 2026-10-22

**Status: DRAFT for Skyy's review.** Start here: `sheet.png` (each emblem at 2x and 1x, on a 1x mock of the map centre with its hubs,
and the approved Nexus for reference).

Why: SkyyTrees 0.5.0 + SkyyRebirth 0.5.0 radial pages show the SkyWynn crest placeholder (`tools/skyymap.py emblem_picture`) at the map
centre; spec Q8 default "new art; crest until it is approved" (Skyy 2026-10-20 "recommended on all"). The look (navy disc, heavy gold
rim with studs, bright symbol) follows the skill-tree centre Skyy liked on Hylterium (research/UI-Ideas.md 2026-10-22 SKILL TREE PAGE
LOOK) - described, never copied. First version; no older sheet.

| Page | Emblem | Trees it stands for |
|---|---|---|
| Gathering | pickaxe + hatchet (iron) behind a copper hoe + a bamboo fishing rod with a red bobber, handles fanned from one leather tie | Mining, Foraging, Farming, Fishing |
| Crafting | the anvil in front, a cooking pot with green stew + steam, a pink alchemy flask | Smithing, Cooking, Alchemy |
| Adventure | a steel sword across a treasure map (dotted path + X), a leather boot, a paw print | Combat, Exploration, Acrobatics, Beastmastery |
| Class | the 8 APPROVED class crests (`art/class-emblems/*_128.png`, read only, shrunk to 46 px @2x) in a ring round a gold 4-point star | the Class page / rail |
| Rebirth Nexus | **unchanged** - the approved 2026-10-13 Nexus (`research/cloud/icons-1013/icons/Skyy_Nexus_Of_The_Void.png`) | Rebirth |

Note the spec's table had older picks (Crafting "anvil + cauldron", Adventure "crossed swords + compass", Gathering "SkyWynn crest");
this round follows the newer task list (tools of all four / three / four trees, paw for Beastmastery).

## Files

| File | What |
|---|---|
| `emblems/<Page>@2x.png` | 192 x 192 RGBA (Gathering, Crafting, Adventure, Class) |
| `emblems/<Page>.png` | 96 x 96, the 1x copy (2 x 2 box filter) |
| `sheet.png` | review sheet 1700 x 1080 |
| `manifest.json` | path, size, bytes, sha256 per file |
| `make_emblems.py` | generator; `--check` = rebuild in memory and compare (SAME BYTES checked). Uses `research/cloud/ui-tiles-art/skyypaint.py` + `skyyitems.py` (pure Python, zlib only) |

Run: `python research/cloud/page-emblems-art/make_emblems.py` (a few seconds).

## Questions for Skyy (default in brackets)

1. Do the Gathering / Crafting / Adventure emblems read at map size (96 px)? [yes; if one is too busy, drop the smallest item (rod /
   flask / paw) first]
2. Class page: keep showing YOUR class's own crest in the centre once you have a class, and use the 8-crest ring only for "no class yet"
   and the left rail? [yes - that is what SkyyTrees 0.5.0 already does with `cemblem`]
3. Nexus: keep the approved art as is (128 px drawn doubled into the 140 px box), or redraw it natively at 256 px for twice the detail?
   [keep as is; a 256 px redraw only if it looks soft in game]

## For the local session

- Sizes: SkyyTrees map emblem box = 96 px (`skyymap.radial_layout(... emb=96)`, Radial-Trees-Spec 2.2: hubs 44 px at 84 px from C), so
  the shipped picture = 192 x 192 @2x. At 200 % zoom the box is 192 px = 1:1 with the @2x, still crisp.
- Where it plugs in: `tools/trees_0_5_0_patch.py` line ~225 ships ONE `tm_ship("Emblem", SMAP.emblem_picture())` ->
  `Common/UI/Custom/SkyyTrees/Map/Emblem@2x.png`. Next SkyyTrees round: ship one per page with names without underscores, e.g.
  `SkyyTrees/Map/EmblemGathering@2x.png`, `EmblemCrafting`, `EmblemAdventure`, `EmblemClass` (bytes from these PNGs, read as data -
  `SART.png_decode` / a copy step), and pick the page's emblem texture in the map markup instead of the one `Emblem`. Keep the crest as
  the fallback if a file is missing.
- Class page: the centre already shows the player's class crest (`TreePage.cemblem(ci)`); `EmblemClass` is for ci < 0 (no class) and the
  rail icon if wanted.
- SkyyRebirth 0.5.0: no change - `RM_EMB = 140`, `rm_black_hole()` keeps reading `Skyy_Nexus_Of_The_Void.png` (128 px, nearest x2).
- These PNGs are OUR art (no vanilla pixels) - committable. The Class emblem contains the approved class crests (also ours).
- UNVERIFIED: readability at 96 px in game (look check after the build). Please add this folder to `research/cloud/ART-INDEX.md` /
  `INDEX.md` (this session could not edit them) and record Skyy's answer with `python tools/qa_append.py ui <file> --no-question`.
