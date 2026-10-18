# Zone ores + alloys + Furnace Charm - build spec (round ores01)

Where things go: Skyy's answers to the questions at the end -> `docs/answered/gear.md` (tool `python tools/qa_append.py gear <file> --close "..."`);
build notes -> each mod's patch script docstring; results -> `docs/log/<YYYY-MM>.md`. Idea file this grew from: `research/Zone-Tiers-Idea.md`.
Written 2026-10-17 by a spec agent (no code, nothing built yet).

## 0. Decisions this spec follows (word for word)

- Skyy 2026-10-17: "Yes - start the zone ores + alloys + Furnace Charm round right after the current set deploys."
- gear.md 2026-10-17 FURNACE CHARM DESIGN: "regarding the furnace charm. Change: T1-T5 upgrades cost each zone's two metals and unlock that
  zone's alloy (T1 Copper+Iron -> Bronze, T2 Thorium+Lead -> Dusk, T3 Cobalt+Chromium -> Azurvane, T4 Adamantite+Slag -> Cinder, T5
  Mithril+Titanium -> Lumen). Keep your speed/fuel numbers and Eternal Flame at Charcoal tier 7. Collections for base metals only, no alloy
  collections."
  -> "your numbers" = smelt time -10/-20/-30/-40/-50%, fuel burned +15/+30/+45/+60/+75%; max tier -> Eternal Flame (no fuel).
- gear.md 2026-10-16 SMELTING ACCESSORY: "and lets make an accessory that increases how fast things smelt in the furnace. but also increases
  the fuel cost. (once max tire can be made into a variant gives infinite fuel. in the charcoal collection.)"
- Zone-Tiers-Idea.md (2026-10-17): "the metals you mine and their alloys will be used for mining sets, and upgrading tools. not combat gear.
  all combat gear is still drops only." / "Keep Silver/Gold for charms (Recommended)" / each zone = its vanilla metals + ONE new ore of ours,
  smelted into our OWN alloy / "copper and iron make bronze" / "Onyx and Nightveil are parked until there's a Zone 6." / "(dont change now.)"
  for the level re-band (so this round does NOT renumber the tier ladder).
- gear.md 2026-10-16 NO ENCHANTED ESSENCE OF LIFE (standing rule): before adding an item, use the vanilla one if it exists.
  -> Zone 1's alloy is VANILLA `Ingredient_Bar_Bronze` (it exists in Assets.zip with NO recipe today; only salvage of Ancient Steel / Bronze
  armor gives it). We add a recipe, not a new item.
- PROJECT-RULES 2 (check existing mods, no duplicates), 4 (tier tags, sort by tier, Server Setup, four power sources), LOCAL-RESUME.md
  locks (SkyyGear + SkyyMobs = Cobb).

## 1. Survey (PROJECT-RULES 2) - verdict: BUILD OUR OWN, nothing to pack

Skyy's Mods folder (read-only scan of every jar / zip, item ids + manifests, 2026-10-17) - all of these are DISABLED in NewBetaTest:

| Mod | Adds | Verdict |
|---|---|---|
| TerrariaToolsWeapons 0.5.0 (Markebarca) | `Ore_Lead`, `Ore_Lead_Stone`, `Ingredient_Bar_Lead`, Tin, Platinum, Hellstone, Crimtane + Lead tools / armor / anvil | **ID CLASH** with the obvious `Ore_Lead` names -> our ids get the `_SkyWynn` suffix (section 2). Terraria theme, combat gear - not a fit. |
| BelowEveryHeaven 1.6.1, Fullmetal Labyrinth 1.10.16, MGAspectro, NecromancerSpire | one themed ore + bar each, own world-gen assignments | Learn: one ore = raw item + host-rock block variants + a HytaleGenerator assignment. Not our metals. |
| CoalOre 2.0.9, OreGenLibrary | coal ore / an ore-gen helper | Coal would be a 2nd fuel source - out of scope; OreGenLibrary not needed (SkyyWorldGen already places veins). |
| PJ-HyperFurnaceLevels, enhanced-furnance (WanMine), PJ-IngotsAlchemy | furnace tiers / faster furnace / ingot transmute | DUPLICATE of our /craft Furnace + this charm - stay off. |
| Huge Stacks, Taintedroots, TheLostWorlds, Wyvern Welkin, EndgameAndQoL | vanilla ore ids in new host rocks / stack sizes | Not a fit (override vanilla ids). |

CurseForge (web search 2026-10-17, pages not opened - licences UNVERIFIED): **EvenMoreOres** (titanium etc.; page says Creative only, lead
"upcoming"), **Metallurgy 2** (tin -> bronze in an Alloyer), **SteelAge** (+ BronzeAge, CoalOre deps; Blast / Alloy Furnace), **Snitchy's
Foundry**, **HyProTech** (Alloy Smelter), **Bronze & Coal & Onyxium Crafting** (2 Copper + 1 Tin -> 3 Bronze). None has our zone metals, all
bring their OWN furnace block (a duplicate of the /craft Furnace) and their own names. Not packed.

What we LEARN / reuse: (a) the alloy = a 2-input Processing recipe (Metallurgy / SteelAge pattern) - Hytale's CraftingRecipe already takes
several inputs; (b) our own precedent `Ore_Onyxium_SkyWynn` in SkyyWorldGen 0.6+ (block JSON = vanilla ore recipe + vanilla texture by
path, veins in the `ZONES06["ores"]` table, inherited by Zones2) - the new ores copy it row for row; (c) vanilla standalone recipe files
(`Server/Item/Recipes/...`, the Salvage format: Input / PrimaryOutput / Output / BenchRequirement / TimeSeconds) - alloy recipes are
standalone files, so no vanilla item JSON is overridden.

Duplicate check vs our mods: SkyyAccessories already has the **Furnace bench accessory** `Skyy_Accessory_Furnace_T1/T2` (unlocks the /craft
Furnace; T2 = vanilla Furnace II tier speed). The Furnace Charm is a different thing (a boost charm, needs the bench accessory too) - both
stay; the charm's -% stacks multiplicatively on the bench tier. No pack mod (PACK.md) adds ores, alloys or furnaces.

## 2. New ores (Lead Z2, Chromium Z3, Slag Z4, Titanium Z5)

### 2.1 How vanilla does it (Assets.zip, checked)
- Raw item `Ore_Iron` (Categories Blocks.Ores, Tags Type Ore, MaxStack 25, model `Resources/Ores/Ore_Large.blockymodel` + texture
  `Resources/Ores/Ore_Textures/Iron.png`, icon `Icons/ItemsGenerated/Ore_Iron.png`).
- Ore BLOCKS per host rock `Ore_Iron_Stone / _Sandstone / _Shale / _Slate / _Basalt / _Volcanic`: BlockType CubeWithModel, the ore model
  over the host rock texture, `Gathering.Breaking.GatherType = "OreIron"`, drop list = 1 raw ore + 1 host cobble; Tags Family Iron;
  `Server/BlockTypeList/Ores.json` + `Server/Item/Block/Sets/Ores.json` (`"Ore*"` = every Ore_ block is in the Ores set - our blocks
  join it by their id prefix).
- Mining tier = the pickaxe's `Tool.Specs` power per GatherType (`OreThorium`, `OreCobalt`, `OreAdamantite` (+Quality 4), `OreMithril`).
- Bar `Ingredient_Bar_Iron`: Recipe Input Ore_Iron x1, BenchRequirement Processing "Furnace", TimeSeconds 14 (Copper 10, Thorium 18,
  Cobalt 18, Adamantite 20, Mithril 30), ResourceTypes Metal_Bars, model `Resources/Materials/Ingot.blockymodel` + `Ingot_Textures/<M>.png`.
- World gen: vanilla zone assignments (`HytaleGenerator/Assignments/Desert1_Thorium`, `Taiga1_Cobalt`, ...). Our zone islands are cut from
  the vanilla zones, so Zone 2 already has Thorium, Zone 3 Cobalt, Zone 4 Adamantite; Mithril + Onyxium come from SkyyWorldGen's own vein
  table (Zones 4 + 5).

### 2.2 Which of our mods places ores
Only **SkyyWorldGen** (`build_skyyworldgen_0.7.2.py` `ZONES06["ores"]` line ~1239, `Z7 = dict(Z6)` -> the same table runs in
`skywynn_zones2`; vein code `ores(...)` ~line 4549: 8x8x8 cells, jittered spheres, only inside `ore_hosts` rock, `ore_cover` 6 under
ground). SkyyIslands / SkyyExploration only name ore ids (kits / loot), they place no veins.

### 2.3 Ids (new; suffix `_SkyWynn` because TerrariaToolsWeapons owns `Ore_Lead*` / `Ingredient_Bar_Lead`, and to stay clear of future
vanilla ids - the Onyxium precedent). The `Ore_` / `Ingredient_Bar_` prefixes are kept on purpose: SkyySacks homes bags by prefix
(Mining `Ore_`, Smithing `Ingredient_Bar_`), SkyySkills pays Mining XP by prefix, SkyyGear's tier gate reads word 2 of an `Ore_` block id.

| Zone | Ore block (one per ore, host texture) | Raw ore item | Ingot | GatherType (= zone partner) | Mining XP | Smelt s |
|---|---|---|---|---|---|---|
| 2 | `Ore_Lead_Sandstone_SkyWynn` (Rock_Sandstone) | `Ore_Lead_SkyWynn` | `Ingredient_Bar_Lead_SkyWynn` | OreThorium | 18 | 18 |
| 3 | `Ore_Chromium_Shale_SkyWynn` (Rock_Shale) | `Ore_Chromium_SkyWynn` | `Ingredient_Bar_Chromium_SkyWynn` | OreCobalt | 15 | 18 |
| 4 | `Ore_Slag_Volcanic_SkyWynn` (Rock_Volcanic) | `Ore_Slag_SkyWynn` | `Ingredient_Bar_Slag_SkyWynn` | OreAdamantite (+Quality 4 like vanilla) | 30 | 20 |
| 5 | `Ore_Titanium_Basalt_SkyWynn` (Rock_Basalt) | `Ore_Titanium_SkyWynn` | `Ingredient_Bar_Titanium_SkyWynn` | OreMithril | 25 | 30 |

- Reusing the partner's GatherType = the vanilla pickaxes mine it exactly like the zone's vanilla metal; NO pickaxe file is overridden.
- Drops: 1 raw ore + 1 host cobble (vanilla pattern). Raw ore -> ingot 1:1 at the Furnace (recipe in the ingot JSON, like vanilla).
- Build checks (the Onyxium ones): every id absent from Assets.zip items + lang; every referenced model / texture / cobble exists.

### 2.4 Where they spawn (new rows in `ZONES06["ores"]`: block, y min, y max, vein chance per 8^3 cell, radius min/max, island index)
| Ore | y | chance | radius | island (0-based) |
|---|---|---|---|---|
| Lead | 20-110 | 0.020 | 1.3-2.4 | (1,) Zone 2 |
| Chromium | 16-100 | 0.018 | 1.3-2.4 | (2,) Zone 3 |
| Slag | 8-90 | 0.018 | 1.4-2.5 | (3,) Zone 4 |
| Titanium | 8-72 | 0.016 | 1.3-2.3 | (4,) Zone 5 |
Starting values (Mithril's 0.017 is the reference); one Server Setup row per ore: "Lead vein chance" etc. (World Gen section, live for new
chunks). NOTE: veins only appear in chunks generated AFTER the deploy (see Questions).

### 2.5 Tier gate + tags
- SkyyGear's tier gate (`LL_ORE`, catOf word 2) does not know Lead / Chromium / Slag / Titanium -> until a Gear round adds
  `("Lead", 3), ("Chromium", 4), ("Slag", 5), ("Titanium", 6)` they are gated only by vanilla pickaxe power (same as the partner ore).
  **SkyyGear is LOCKED to Cobb (LOCAL-RESUME.md)** -> that row waits for the lock release (follow-up round gear-ores, see section 6).
- Tier tags (`tools/tier_tags.py`, metal word at the zone partner's tier, `tag_text(t, word)`): Lead / Dusk = `T4 Lead` / `T4 Dusk`,
  Chromium / Azurvane T5, Slag / Cinder T6, Titanium / Lumen T7; vanilla Bronze is already T3 (TOOL_METALS). Ore, raw ore and ingot of a
  metal share its tag. Add an owner `SkyyWorldGen` to `OWNERS` (it writes these lang keys - `tools/ci/langdup.py` one writer per key).
  The planned 3-tiers-per-zone re-band renumbers these later in that ONE table (Skyy: "dont change now").

### 2.6 Textures / icons (vanilla-derived = generated at build time into the jar, never committed)
Recolour vanilla `Ore_Textures/<partner>.png` and `Ingot_Textures/<partner>.png` (PIL hue / value shift from a colour table in the build
script) for the 4 ores + 4 ingots + 4 alloy ingots, OR use the hand-drawn icons from the art list (section 5) when they exist (they are our
own art and may be committed). Lead = dull blue-grey, Chromium = mirror silver-cyan, Slag = rust-black with orange flecks, Titanium =
pale white-gold; Dusk = violet-bronze, Azurvane = deep azure, Cinder = ember red-black, Lumen = glowing white-gold (placeholder palette until
Quirk's / local art lands).

## 3. Alloys (Bronze / Dusk / Azurvane / Cinder / Lumen)

| Charm tier | Alloy item | Recipe (1 + 1 -> 1) | Smelt s | Smithing XP | Bazaar |
|---|---|---|---|---|---|
| T1 | `Ingredient_Bar_Bronze` (VANILLA) | Copper Ingot + Iron Ingot | 24 | 16 | keep 40 (fixed) |
| T2 | `Ingredient_Bar_Dusk_SkyWynn` | Thorium Ingot + Lead Ingot | 36 | 45 | AUTO |
| T3 | `Ingredient_Bar_Azurvane_SkyWynn` | Cobalt Ingot + Chromium Ingot | 36 | 38 | AUTO |
| T4 | `Ingredient_Bar_Cinder_SkyWynn` | Adamantite Ingot + Slag Ingot | 40 | 75 | AUTO |
| T5 | `Ingredient_Bar_Lumen_SkyWynn` | Mithril Ingot + Titanium Ingot | 60 | 63 | AUTO |
(time = sum of the two ingots' vanilla times; XP = (A + B) x 1.25 of the bars' SMITH_XP.)

- Recipes are STANDALONE files `Server/Item/Recipes/SkyWynn/Alloy_<Name>.json` (Salvage format) with `BenchRequirement Processing Id
  "SkyyAlloy"` - a bench id NO block has, so a placed vanilla furnace can never make them (= the /craft-only default, section 7).
- SkyySacks /craft Furnace (read: `ProcBench`, `unitMs(r, bench, tier)`, `burnOne`, `fuelMs`, `advance`, the queue code ~line 9960):
  the Furnace tab ALSO lists recipes whose bench id is `SkyyAlloy` and queues them in the player's **Furnace** ProcBench (its fuel, tier
  speed and output - `ProcBench.config("Furnace")`), sorted by tier then name. Locked rows: shown greyed with "Furnace Charm T<n> unlocks
  this" (the Omni-lock text pattern, `KnowSync.allowedOut`); a locked row never queues (checked again on the click).
- Lock = the player's equipped Furnace Charm tier >= the alloy's tier (bridge in 3.4). Charm removed later: queued alloy jobs finish
  (paid already); new ones refuse.
- Alloys get NO collection (Skyy). Charcoal from burning fuel keeps working as today.

## 4. Furnace Charm (SkyyAccessories, current pin 0.5.24 -> 0.5.25)

### 4.1 Item line
`Skyy_Charm_Furnace_T1 .. _T5` + `Skyy_Charm_Furnace_Eternal` ("Eternal Flame"). Lives in Void Charms like every accessory (crafted and
upgraded on the Void Charms CRAFT tab, one row = the next step only, gear.md 2026-10-16), Gathering sub tab. Tier tag: own ladder word
`Charm` (`ladder_tag(n, "Charm")` -> "T3 Charm - ..."; add "Charm" to `OWN_LADDERS`). Eternal Flame is tagged "T5 Charm" (it is T5 that needs no
fuel). Sort by tier.

| Tier | Smelt time | Fuel burned | Unlocks | Craft / tier-up cost (proposed; takes the tier below) |
|---|---|---|---|---|
| T1 | -10% | +15% | Bronze | 32 Copper Ingot + 32 Iron Ingot |
| T2 | -20% | +30% | Dusk | 64 Thorium Ingot + 64 Lead Ingot |
| T3 | -30% | +45% | Azurvane | 128 Cobalt Ingot + 128 Chromium Ingot |
| T4 | -40% | +60% | Cinder | 192 Adamantite Ingot + 192 Slag Ingot |
| T5 | -50% | +75% | Lumen | 256 Mithril Ingot + 256 Titanium Ingot |
| Eternal Flame | -50% | NO fuel | all 5 | T5 charm + 16 Enchanted Charcoal + 64 Lumen Ingot; needs Charcoal collection tier 7 |

- Effect (only the /craft Furnace, section 7): unit time = vanilla unit time x (1 - bench tier reduction) x (1 - charm %), fixed when the
  job is queued (ProcJob.unitMs, as today). Fuel: in `advance`, the fuel drained per processed ms = step x (1 + fuel %) (fuelMs runs out
  faster); Eternal Flame = `needsFuel` false for that player (no fuel used, and so no Charcoal byproduct). Tannery untouched.
- Four power sources: the charm is a Smithing / smelting charm, not a skill stat - no stacking rule applies; it gives NO Accessory Power
  (it is a utility charm like the bench accessories) - see Questions.
- Server Setup (`tools/skyycfg.py`, section "Void Charms"): `furnace.timePct` "10,20,30,40,50", `furnace.fuelPct` "15,30,45,60,75",
  `furnace.eternalTier` 7 (the Charcoal collection tier), `furnace.cost.T1..T5` + `furnace.cost.eternal` ("id:qty,id:qty"), `furnace.on`
  (live). Times shown in seconds where shown.

### 4.2 Bridge (plain java.lang, `skyy.bridge`)
- `acc:smelt:<uuid>` = `"<tier 0-5>|<timePct>|<fuelPct>|<eternal 0/1>"` (e.g. `"3|30|45|0"`; `"0|0|0|0"` / absent = none), republished
  with `acc:has` (on change, profile epoch, 5 s tick). SkyySacks reads it; absent (Accessories missing) = no bonus, every alloy locked.
- Eternal Flame unlock: Accessories asks `coll:fn:tier` for the Charcoal collection (>= `furnace.eternalTier`); SkyyCollections missing =
  Eternal Flame not craftable (log once).

## 5. Collections, Bazaar, Skills (listings)

- **SkyyCollections** (0.2.24 -> 0.2.25): 4 Mining collections like the vanilla metals (`add(...)` ~line 947): Lead (curve R, "lead veins in
  Zone 2 sandstone"), Chromium (R), Slag (E), Titanium (E) on the raw ore ids. NO alloy collections. NEW **Charcoal** collection (Smithing
  category, curve S - tier 7 = 5,000 Charcoal) credited through `coll:fn:add` with the new source `sacks:furnace` (accepted by code like
  `skills:felled` - no config migration). Every collection gets its own Enchanted item (economy.md 2026-10-16 "Own items now") -> 5 rows in
  `tools/skyyench.py`: Enchanted Lead / Chromium / Slag / Titanium Ingot (from ingots, 100:1) + Enchanted Charcoal. Tier rewards follow the
  partner metal's rows.
- **SkyySacks** (0.8.19 -> 0.8.20): Mining / Smithing bags take the new ids by prefix (verify); Enchanted homes via skyyench; every Furnace
  unit that pays Charcoal calls `coll:fn:add {UUID, "Ingredient_Charcoal", qty, "sacks:furnace", pkey}` when the charcoal lands in the
  output (once per unit, ledgered like `xpDone`).
- **SkyyBazaar** (0.1.19 -> 0.1.20): raw ores at the zone partner's price (Lead 48, Chromium 144, Slag 480, Titanium 1440); ingots +
  alloys AUTO (processed from inputs + premium; the 2-input alloy recipes must pass the existing loop guard ~line 2574 - Bronze stays 40,
  check Copper + Iron + premium < 40 is not a loop); Enchanted rows from skyyench.
- **SkyySkills** (0.4.48 -> next free after the Local Classes/Skills lock): Mining XP prefixes `Ore_Lead` 18, `Ore_Chromium` 15, `Ore_Slag`
  30, `Ore_Titanium` 25; SMITH_XP rows for the 4 ingots (= partner) + 5 alloys (table 3).

## 6. Art list (local Claude: metal items + ores; Quirk = armor only)

Icons (64 px, vanilla ItemsGenerated angle 22.5 / 45 / 22.5, skill `skywynn-art`): 4 raw ores, 4 ore blocks, 4 ingots, 4 alloy ingots
(Dusk, Azurvane, Cinder, Lumen; Bronze is vanilla), 5 Enchanted items (4 ingots + Charcoal, the Enchanted shine style), 6 Furnace Charm
icons (T1-T5 + Eternal Flame: a small furnace charm growing hotter, Eternal = white-gold flame). Block textures: 4 ore overlay textures
(Ore_Large model). Until drawn: build-time recolours (2.6).

## 7. Builder split (no two builders on one mod)

| Builder | Mod(s) / shared files | Work | Model |
|---|---|---|---|
| B1 | SkyyWorldGen 0.7.3 + `tools/tier_tags.py` | ALL new metal assets (one asset owner, the Onyxium precedent): 4 ore blocks, 4 raw ores, 4 ingots + their Furnace recipes, 4 alloy items, 5 `SkyyAlloy` recipe files (incl. vanilla Bronze), generated textures / icons, vein rows, Server Setup rows, tier tags (+ owner SkyyWorldGen, ladder word Charm) | Opus |
| B2 | SkyyAccessories 0.5.25 | Furnace Charm line, Void Charms CRAFT rows, `acc:smelt:<uuid>`, Eternal Flame via `coll:fn:tier`, Server Setup | Opus |
| B3 | SkyySacks 0.8.20 | `SkyyAlloy` rows in the Furnace tab + lock, charm time / fuel / Eternal in ProcBench, Charcoal `coll:fn:add` | Opus |
| B4 | SkyyCollections 0.2.25 + `tools/skyyench.py` | 4 ore collections + Charcoal collection, `sacks:furnace` source, 5 Enchanted rows | Opus |
| B5 | SkyyBazaar 0.1.20 + SkyySkills (next) | listings + XP rows (two small mods, one builder - after the Local Skills lock is released) | Sonnet ok |

B1 runs first only for the id list - the ids in this spec are FINAL, so B2-B5 start in parallel against them. One cross-check + smoke of
the whole set, deployed together (an ingot recipe in WorldGen references raw ores in WorldGen; Collections / Bazaar / Skills only name ids
at runtime and must build-check them against the B1 jar, not Assets.zip).
**Waits for the Cobb lock on SkyyGear + SkyyMobs (LOCAL-RESUME.md):** the tier-gate rows (2.5), mining sets and lifelong-tool tier-ups
paid in these metals / alloys (Zone-Tiers-Idea: "used for mining sets, and upgrading tools"), and any ore drop from mobs. Until then the
metals have uses: Furnace Charm tier-ups, alloys, Bazaar, collections. Round `gear-ores` queued after Cobb's PR merges.

## Questions for Skyy (default in [brackets])

1. Furnace Charm (OPEN-QUESTIONS gear): only the /craft Furnace, or the placed vanilla furnace too? [only /craft Furnace - the placed one
   has no per-player hook; alloys use their own bench id so a placed furnace cannot make them]
2. New ore veins only grow in land generated after the deploy - already-explored parts of the zone islands get none. OK? [yes - test in
   unexplored parts of each zone (or a fresh world); no world rewrite]
3. Alloy recipe: 1 ingot of each metal -> 1 alloy ingot? [yes, 1 + 1 -> 1, time = both smelts added]
4. Furnace Charm costs: 32 / 64 / 128 / 192 / 256 of each zone's two ingots per tier, Eternal Flame = 16 Enchanted Charcoal + 64 Lumen?
   [yes - editable in Server Setup]
5. The charm must be equipped in Void Charms for its speed / fuel AND for the alloy unlock? [yes - like the bench accessories]
6. Tier tags for the new metals: "T4 Lead", "T5 Chromium", "T6 Slag", "T7 Titanium" (same tier as the zone's vanilla metal) until the
   3-tiers-per-zone re-band? [yes]

## UNVERIFIED

- That SkyySacks' recipe scan picks up STANDALONE recipe files (`Server/Item/Recipes/...`) with an unknown Processing bench id
  (`SkyyAlloy`) - probe at build time (the Salvage recipes prove the format loads; the bench-less id needs an offline asset-load test).
- That a Processing recipe with a bench id no block uses passes asset validation without a WARN (smoke test).
- Ore textures as recolours look right on the CubeWithModel ore model (in-game screenshot).
- Vein chances (2.4) give a sensible amount per island - count with the generator's ORE_N stat after a test chunk run.
- Bazaar AUTO pricing of 2-input recipes (the pipeline was written for 1-input smelts) and its loop guard.
- CurseForge licences of the surveyed mods (pages not opened; none is packed, so nothing depends on them).
- Whether vanilla Bronze armor recipes become craftable once Bronze has a recipe (combat gear must stay drops only - B1 / cross-check
  confirm those recipes are already hidden or stay unreachable).

## 8. Added 2026-10-17 (Skyy: "Yes - add Electrum ... and the metals spec's spawn rules ... to this round before deploy.")
From Cobb's metals spec (sections 1, 3, 4; outside the repo), now part of this round:
- **Electrum** = 1 Gold bar + 1 Silver bar -> 1 Electrum bar (SkyyAlloy bench), a charm metal; unlocked at Furnace Charm T1 (the Bronze tier),
  before Zone 2. No ore, no collection.
- **Spawn rules:** each new ore mirrors its zone's vanilla base ore (same caves / mines, spawn spots, drop behaviour, weights), just slightly
  rarer. Base ore boost: Thorium, Cobalt, Adamantite and Mithril each slightly MORE common than vanilla; new ores mirror the ADJUSTED base.
  Lead mirrors adjusted Thorium (Z2), Chromium mirrors Cobalt (Z3), Slag mirrors Adamantite (Z4). Mithril (does not spawn in vanilla today)
  gets Adamantite's spawn spots + weights, in Zone 5, slightly rarer than Adamantite; Titanium mirrors that Mithril. Silver and Gold: find
  the zone where each spawns best and use that best rate in EVERY zone. The builder picks the "slightly rarer" factor from the vanilla
  weights and states it for Skyy's OK.
