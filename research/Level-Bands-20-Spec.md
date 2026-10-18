# Level bands: 20 levels per zone, the Bronze Mining set, 15 Foraging + 15 Farming tiers (SPEC)

Where answers go: Skyy's answers -> `docs/answered/gear.md` (`python tools/qa_append.py gear ...`); open questions -> `OPEN-QUESTIONS.md`
(section 9 holds them with today's defaults). Builds follow section 7, one mod per builder. Index entry: `INDEX.md` research row.

## 0. Skyy's words (docs/answered/gear.md, last two lines, 2026-10-18)

1. BRONZE SET + 20 LEVELS PER ZONE (screenshot: Smithing > Mining armor, Copper 1-18 ... Adamantite 35-43, no Bronze): "where is bronze?
   bronze is the alloy of iron and copper. its already in the game. so we need to add the rescipy to smelt iron and copper together to make
   bronze, and add it to this list. also those levels dont add up at all. we have 3 tiers per zone. and im changing it so we have 20 levels
   per zone. so bronze gear would be like 15-23 thorium would start at 20. and dusk armor would end at like 43. (follow the same patern for
   all the new metals. ..."
2. APPROVED, on the table below: "perfect! make sure all the gear follows that. tools, weapons, armor. (combat gear. (make sure the Tiers
   listed in the items flavor text get updated too, to match the new order.) (this way it takes 5 rebirths to reach lvl 100 and get to the
   end of zone 5. ... we have 15 tiers of mining armor sets. we need to update foraging, and farming, to match (fishing can wait for an
   overhaul.) because of the armory mods style editor we made an armor design for like every tree type. so we should have the art to make
   the 15 tiers already. we just need to split each zone into 3 tiers of trees.) and for farming, are there 15 crops?"

This replaces the 2026-10-17 idea "end of zone 4 by lvl 50" (research/Zone-Tiers-Idea.md).

## 1. The band table (APPROVED by Skyy 2026-10-18)

Zone z starts at 20 x (z - 1) (Zone 1 at Lv 1); its three steps start at base, base + 8, base + 15 and end where the next step starts
(the alloy runs 3 levels into the next zone).

| Zone | Mob levels | T | Metal (step) | Band | Was (level.material / Mining armor list) |
|---|---|---|---|---|---|
| 1 | 1-20 | T1 | Copper (ore) - also Crude / Wood / Armor_Copper rows | **1-8** | 10-18 (Armor_Copper 1-18, Crude / Wood 1-13) |
| | | T2 | Iron (ore) | **8-15** | 15-23 |
| | | T3 | Bronze (alloy) | **15-23** | 15-23 (no Mining set) |
| 2 | 20-40 | T4 | Thorium | **20-28** | 20-28 |
| | | T5 | Lead | **28-35** | 22-30 / 22-27 |
| | | T6 | Dusk | **35-43** | 24-32 / 24-28 |
| 3 | 40-60 | T7 | Cobalt | **40-48** | 25-38 |
| | | T8 | Chromium | **48-55** | 28-40 / 28-34 |
| | | T9 | Azurvane | **55-63** | 31-41 / 31-38 |
| 4 | 60-80 | T10 | Adamantite | **60-68** | 35-43 |
| | | T11 | Slag | **68-75** | 37-45 / 37-42 |
| | | T12 | Cinder | **75-83** | 39-47 / 39-43 |
| 5 | 80-100 | T13 | Mithril | **80-88** | 40-49 |
| | | T14 | Titanium | **88-95** | 45-55 / 43-49 |
| | | T15 | Lumen | **95-103** | 50-60 / 46-49 |
| 6 (parked) | 100+ | T16 | Onyxium | **100-108** (same pattern; Q2) | 40-49 |

- ONE band per metal everywhere: tools, weapons, combat armor, the Mining sets (garmor.zoneBands = the same numbers), UT per zone.
- `tools/tier_tags.py` LEVEL_BANDS (start -> T): `((95,15),(88,14),(80,13),(75,12),(68,11),(60,10),(55,9),(48,8),(40,7),(35,6),(28,5),
  (20,4),(15,3),(8,2))`: Lv 1-7 T1, 8-14 T2, 15-19 T3, 20-27 T4 ... 95+ T15; Onyxium ids T16 (rule unchanged).
- Mob zone tops `20 40 60 80 100` (was `20 30 45 60 75`); Zone 1 mob levels do not change.
- Level caps: "5 rebirths to reach lvl 100" = first-run cap 50, +10 a rebirth (SkyyRebirth `caps.levels` 10). Today SkyySkills
  `levels.class.max` / `levels.max` default to 100 - the main session checks which cap a first-run player really has (Q8).

### 1.1 Non-metal combat families (the 59 level.material family rows): keep every tier tag, stretch the levels

Each 0.1.3 family start is mapped through the old -> new metal anchors (old 1 -> 1, 15 -> 8, 20 -> 20, 25 -> 40, 35 -> 60, 40 -> 80,
49 -> 100, straight lines between); width stays 8 (`level.bandWidth`). Checked: every family keeps the SAME T it shows today.

- Wool, Leather_Soft, Stone, Trork, Fishbone, Bone, Root, Stoneskin, Bamboo, Cane, Onion 3-10 (T1 Crude).
- Linen, Leather_Light, Scrap, Steel_Rusty, Steel_Flail_Rusty, Leaf, Kweebec, Cutlass, the 5 Shortbow_* rows 6-13 (T1 Copper).
- Cotton, Leather_Medium, Tribal 8-15 (T2).
- Silk, Leather_Heavy, Leather_Raven, Steel, Incandescent, Zombie, Katana, Nexus, Runic, Kunai, Grimoire, Wizard 20-27 (T4).
- Doomed, Void, Frost, Flame, Praetorian 40-47 (T7). Ancient, Steel_Ancient, Crystal, Cindercloth, Spellbook_Fire, Spellbook_Frost,
  Staff_Frost 50-57 (T8). Scarab, Spectral, Silversteel, Demon, Rekindle 60-67 (T10). Crystal_Flame, Crystal_Ice 80-87 (T13). Prisma 91-98 (T14).
- Starter rows (ST_BANDS): Armor_Leather_Soft / Armor_Cloth_Wool 1-12 -> 1-10; Weapon_Spellbook_Copper / Weapon_Crossbow_Copper 1-18 -> 1-8.
- `tools/tier_tags.py` LEVEL_CRUDE 10 -> 5 (so Lv 3 Stone still says "T1 Crude" and Lv 6 Scrap "T1 Copper", as today).

## 2. Every place a band lives today (SET pins, tools/deploy_set.py) and what it becomes

Line numbers = the pinned scripts; Gear 0.3.28 (building now) shifts Gear lines - grep the anchor text.

### 2.1 tools/tier_tags.py (shared; TT_VERSION "2" -> "3")
- `:130` LEVEL_BANDS -> section 1 (keep the old tuple as `LEVEL_BANDS_V2` for proofs / migrations). `:134` tier_for_level logic unchanged,
  docstrings `:33-35`, `:127-129`, `:135`. `:144` LEVEL_CRUDE 10 -> 5.
- NEW `METAL_BANDS = {metal: (min, cap)}` + `ZONE_TOPS = (20, 40, 60, 80, 100)` = THE table every build imports (Gear, Armory, Mobs,
  Bazaar, Auctions) - the next re-band is one edit.
- `:196-205` LOGS and `:207-215` CROPS -> the 15-step tree / crop ladders (sections 5 + 6).
- `:283-293` MINING_ARMOR rows unchanged (they take their ingot's T). Add the 10 new Foraging sets and 8 new Farming sets (section 5 / 6).
- `tools/test_tier_tags.py:169-179` -> the new numbers.
- WARNING: older build scripts assert today's LEVEL_BANDS (Gear 0.3.27 `:6635`, Armory `:702`, Bazaar `:6576`, Auctions `:2431`). Edit
  tier_tags.py only after Gear 0.3.28 is built, harnessed and pinned - as step 1 of the Gear 0.3.29 builder.

### 2.2 SkyyGear 0.3.27 (SkyyGear/build_skyygear_0.3.27.py) -> Gear 0.3.29
- `:2855` MATERIALS starts -> TT.METAL_BANDS (Crude / Wood 1, Copper 1, Iron 8, Bronze 15, Thorium 20, Cobalt 40, Adamantite 60,
  Mithril 80, Onyxium 100). `:2858` MATERIALS_010 stays (old migration).
- `:3014` VANILLA_TOP = 49 and every "never above 49" rule: `:3024` _mcap, `:3033` FAM_BANDS, `:3050` cap_of, `:6318`, help `:6904`, Java
  `GearCfg.VTOP` (`:9439`) / capOf -> the cap is the row limit; raise the level.material row limit 100 -> 200 (`:6901`).
- `:3019` _MNEXT + `:3027-3031` BANDS (the asserted table) -> TT.METAL_BANDS rows (Crude, Wood, Copper, Armor_Copper 1-8, Bronze, Iron,
  Thorium, Cobalt, Adamantite, Mithril, Onyxium).
- `:2923-2992` FAMILIES -> section 1.1 (width 8 kept).
- `:6632` G22_BANDS (`level.material.<M>_SkyWynn`) -> section 1 rows of the 8 zone metals.
- `:6293-6319` ZM_ROWS bands + ZM_BANDS_DEF `"22-27,24-28,28-34,31-38,37-42,39-43,43-49,46-49"` (= the screenshot) ->
  `"28-35,35-43,48-55,55-63,68-75,75-83,88-95,95-103"`.
- `:5029` MINE_TIERS / `:5041` MINE_ROWS / `:6304` ZM_LADDER: + Bronze (section 3).
- `:6166` GA2_BANDS_DEF `"1-18,15-23,20-28,25-38,35-43,40-49,40-49"` (Foraging / Farming / Fishing gathering armor bands, by tier) -> the
  15 metal bands by ladder T (sections 5 + 6). Fishing keeps its 5 sets but reads the new bands of its tiers (T1 / T2 / T4 / T7 / T10).
- `:6703-6711` G23 item band asserts (Bronze 15-23 stays; the rest read the new rows). `:7700` ST_BANDS -> section 1.1.
- `:4892-4894` UT_LO / UT_HI + `:7741-7746` UT_ALLOY / UT_BANDS (Z1 15-23, Z2 24-32, Z3 31-41, Z4 39-47, Z5 50-60) -> Bronze 15-23,
  Dusk 35-43, Azurvane 55-63, Cinder 75-83, Lumen 95-103; `:7763` / `:7782` the Armory UT rows; every `ut.<id>` row.
- `:45167` GearSigDrop.zoneOf (`<= 20 / 30 / 45`) -> TT.ZONE_TOPS (`<= 20 / 40 / 60 / 80`, else 5).
- `:21107-21118` GearView LB_LO / LB_T / LB_CRUDE (Java mirror of LEVEL_BANDS) follow TT; extend the proof to Lv 0-150.
- Lifelong tool rules read the live table (no code change, behaviour moves): `:18716` tool level = min(skill, tier band top) (a Copper tool
  now tops at 8, not 18); `:18838` / `:19807` tierWhy (tier-up needs the new tier's band start: Iron 8, Bronze 15, Thorium 20, Lead 28 ...
  Lumen 95). CHECK: Upgrade Points already spent when a tool's cap drops (Copper 18 -> 8) never go negative and never remove lines.
- Pack / Mythic rows (`:5009` PACK_ROWS, `:24192`) follow the rows.

### 2.3 Every item family that follows the bands (and its tag)
Ladder T NUMBERS do not change (Copper T1 ... Lumen T15, Onyxium T16); only levels move. So:
- Metal-word ids keep their tag word + number and get the new LEVEL band: lifelong pickaxe / hatchet / hoe / sickle / Harvester /
  watering can / shovel / multitool tiers (TOOL_METALS + G23 tools), every vanilla + Armory metal weapon (Sword, Axe, Battleaxe, Mace,
  Daggers, Longsword, Spear, Shortbow, Crossbow incl. the `_Wynn` gap crossbows, Staff, Wand / SoulCage, Spellbook, Kunai, Bo, Gauntlets,
  Wraps, GreatShield, Shield) incl. the 76 + 80 `<M>_SkyWynn` weapons, metal combat armor (vanilla Copper ... Onyxium, Bronze, Ornate
  Bronze, Armory recolours), the Mining sets (7 vanilla + 8 zone + Bronze).
- Non-metal ids: level from section 1.1, tag from level_tag - unchanged T by construction (1.1).
- Tags that DO change number = the gathering ladders (logs, crops, seeds, Enchanted logs / crops, Foraging / Farming armor): sections 5 + 6.
  Their lang keys belong to SkyyCollections (materials + Enchanted) and SkyyGear (armor) - both rebuild (`tools/ci/langdup.py` one writer).
- The armor-weight flavour text (`T3 Bronze Heavy`) is built from the same tag, so it follows.

### 2.4 SkyyArmory 0.1.34 -> Armory 0.1.35
- `:695-702` NM_BANDS + `:1658` BANDS -> import TT.METAL_BANDS. `:15043` zoneOfLevel (`<= 20 / 30 / 45`) -> TT.ZONE_TOPS.
- `:17947` bandStart reads Gear's live table; the Mana check (`:17911`) + BOOK ladder (`:3331`) re-prove at the new starts. No weapon
  number changes this round (the main session refreshes the Class Balance Workbench after the deploy).

### 2.5 SkyyMobs 0.1.10 -> Mobs 0.1.12 (0.1.11 is building now)
- `:870` BOSS_TOPS_DEF -> `"20 40 60 80 100"` (+ comments `:867`, `:1187`). `:1034-1035` ZONE_TOPS / ZONE_FLOORS -> {20, 40, 60, 80} /
  {1, 20, 40, 60}. `:1037` COLOR_ROWS 1 / 20 / 30 / 45 / 61 -> 1 / 20 / 40 / 60 / 81.
- `:960-1027` BIOME_ROWS, ENV_ROWS, ZONE_ROWS: zone map (old 1-20 / 20-30 / 30-45 / 45-60 / 60-75 -> 1-20 / 20-40 / 40-60 / 60-80 / 80-100,
  straight lines inside a zone, rounded). Zone 1 + goblin portals unchanged. E.g. Zone2_Tier1.* 20-24 -> 20-28, Zone2_Tier3.* 27-30 -> 34-40,
  Zone3_Tier1.* 30-34 -> 40-45, Zone3_Tier3.* 41-45 -> 55-60, Zone4_Tier4.* 45-50 -> 60-67, Zone4_Tier5.* 53-60 -> 71-80; the builder prints
  the full list. `levels.max` 100 stays; no `world.` rows are shipped.
- Balance: Zone 2-4 mobs get higher levels (more Health / damage / XP); 0.1.11's 35 % one-hit cap stays the safety.

### 2.6 SkyyBazaar 0.1.21 / SkyyAuctions 0.1.13 / SkyyCollections 0.2.27
- Bazaar `:6573-6588`, Auctions `:2429-2444`: LEVEL_BANDS copies + the assert `[0] == (50, 15)` -> (95, 15), `[-1] == (8, 2)`; proof 0-150.
  Both also bake the tier table (BZ_TIER_SPEC) -> rebuild for the new log / crop tiers ("sort by tier everywhere").
- Bazaar: the Bronze Mining recipes make Bronze armor craftable (its SET model `:160-176` leaves the TODO recipes out) - price it like the
  other crafted Mining sets (`market.gatheringSets`).
- Collections: the log / crop / seed / Enchanted lang tags (owner SkyyCollections) and any collection tier unlock that names a tree / crop
  tier -> rebuild after tier_tags (section 5 / 6).
- No band: SkyyQuests 0.4.1 (rewards ask Gear's live bands; doc line `:23` goes stale; tutorial goals Mining / Foraging / Farming 10 fit),
  SkyyWorldGen 0.7.4, Skills, Classes, Shards, Islands, Fishing, Pets, Merchants, Exploration (grep found none).

## 3. The Bronze Mining set

### 3.1 Vanilla facts (Assets.zip, read only)
- `Armor_Bronze_Head / Chest / Hands / Legs`: Parent `Armor_Iron_<slot>`, ItemLevel 25, Uncommon, ISS_Armor_Heavy, Iron's exact Health /
  resistance (9 / 17 / 7 / 13 HP; 5 / 9 / 4 / 7 %), durability 200 (Legs 250). Recipe 3 / 6 / 2 / 4 Bronze bars + Wood_Trunk + Light
  leather at bench id **"TODO"** (no bench has it: uncraftable today; Bazaar 0.1.21 + WorldGen 0.7.4 assert it).
- `Armor_Bronze_Ornate_*` (3 pieces, Rare, ItemLevel 28), same TODO bench - stay COMBAT drops (Q9).
- `Ingredient_Bar_Bronze` has no recipe of its own.

### 3.2 The smelt (Copper + Iron -> Bronze) already exists
`SkyyWorldGen/build_skyyworldgen_0.7.4.py:1551` WG_ALLOYS: 1 Copper Ingot + 1 Iron Ingot -> 1 Bronze Ingot, 24 s, bench `SkyyAlloy` = the
/craft Furnace, unlocked by **Furnace Charm T1** (equipped in Void Charms; T1 tier-up 32 Copper + 32 Iron ingots) - Skyy's own 2026-10-17
design ("T1 Copper+Iron -> Bronze"). Default: keep the gate and tell Skyy where it is (most likely no charm yet = "where is bronze"). Q6.

### 3.3 Gear 0.3.29: Bronze joins the Mining sets
- GearMine: Bronze = a new tier APPENDED at index 15 (saved indexes stay); ids = vanilla `Armor_Bronze_<Slot>` by EXACT id (like the 7
  vanilla sets, `:1237`); RANK / ZM_LADDER between Iron and Thorium; /smithing > Mining armor lists it there. Band level.material.Bronze 15-23.
- Mining lines (`garmor.mining.bronze`, `set.mining_bronze` rows): Fortune per piece (Head Chest Legs Hands) 0.2 0.4 0.2 0.2, Wisdom 0,
  lamp 2, full set `mfort+2 mpow+2.5` (full Fortune 3.0, between Iron 2.3 and Thorium 3.8).
- Recipe (Q5): standalone assets in `Server/Item/Recipes/SkyyGear/` (`:4141`), output `Armor_Bronze_<Slot>` = Iron's recipe with the Iron bar
  swapped 1:1: 9 / 16 / 7 / 13 Bronze Ingots + 4 / 7 / 3 / 6 Light Leather + 3 / 6 / 3 / 4 Linen scraps, Armor_Bench (Armor_<Slot>, tier 1),
  KnowledgeRequired false. The vanilla TODO recipe stays unreachable.
- Out of the bag pool (the Heavy bags keep Steel / Heavy Leather / Bronze_Ornate; update the `:5036` assert). Tag "T3 Bronze" (id word).

## 4. Saved data
- Item documents keep their STORED level (crafted / dropped gear, UT, Mythic, mining + gathering pieces); nothing rewrites them. Tag = the id's
  row (unchanged T for every metal / family item); gate = stored level (an old Iron sword at Lv 20 stays Lv 20; an old Lead mining piece at
  Lv 22 sits below Lead's new 28-35 band - easier to wear). Anvil Level up moves a piece into its new band (Q7).
- Lifelong tools: level live = min(skill, band top) - follows at once. Saved tier, lines, points stay (2.2 check).
- Old Bronze pieces already owned: mining armor BY ID from now (the 0.2.15 old-pieces rule).
- Gathering armor: the 20 Foraging + 28 Farming ids keep their ids and looks; only their tier numbers / bands / ladder slots change (5 + 6).
- No per-player file changes, no new saved fields.

### 4.1 Migrations (only lines still holding the OLD default; keep + log hand edits; verified History snapshot first; change-log line with Undo;
run-once marker; bytes + line endings kept - PROJECT-RULES 4)
- Gear `migrate0329` (Skyy_SkyyGear/config.properties): `level.material.*` rows still at their 0.3.28 default (11 metal, 8 `<M>_SkyWynn`,
  59 family, 4 starter rows), `garmor.zoneBands`, the gathering-armor band / ladder / stat rows (GA2), every `ut.<id>` still at its 0.3.27
  default; pure-addition block: `garmor.mining.bronze`, `set.mining_bronze`, the new Foraging / Farming set rows.
- Mobs `migrate0112`: `bosses.zoneTops`, every biome / env / zone row and colour row still at its 0.1.10 default.
- Armory, Bazaar, Auctions, Collections: no band rows -> none.
- Rollback: Gear 0.3.29 -> 0.3.28 is item-safe only after Undoing the migrate0329 rows (0.3.28 would clamp bands to 49). FLOOR comment in
  tools/deploy_set.py with the pin; Gear + Mobs + Armory + Collections + Bazaar + Auctions roll back together.

## 5. Foraging: 15 tree tiers (3 per zone)

Facts: 34 vanilla trunk ids (Assets.zip; the "33 logs" + Sadwillow / Ice). Today 5 tree tiers F1 Grove ... F5 Wastes (tier_tags LOGS at
T1 / T2 / T4 / T7 / T10) and 5 Foraging armor sets `Armor_Foraging_F1..F5_<Slot>` (looks Oak / Maple / Gumboab / Redwood / Sallow,
Gear `:6132`). The tree-armor art Skyy means is OURS: `art/gathering-armor/` = **26 approved per-tree 4-piece sets** (models, textures,
icons, Blockbench sources; manifest.json; README "one set per tree", approved 2026-10-08 / 10-09, not yet in game), drawn in 5 coolness
folders F1-F5. (No such designs exist in SkyyArmory or The Armory's files - grep found none; these are the ones.) Missing designs: Palm, Apple,
Amber, Windwillow, Wisteria_Wild, Sadwillow, Ice (Frostwood), Stormbark - none of them needs a set in this plan.

| Zone | T | Trees (trunk ids `Wood_<x>_Trunk`) | Armor set (art/gathering-armor design) | Hatchet at normal speed |
|---|---|---|---|---|
| 1 | T1 | Oak, Birch | **Oak** (F1, = today's Grove Bark F1 ids) | Copper |
| 1 | T2 | Beech, Ash, Aspen, Apple | **Beech** (F1) | Iron |
| 1 | T3 | Maple, Azure | **Maple** (F2, = today's Autumn Bark F2 ids) | Bronze |
| 2 | T4 | Dry, Palm | **Dry** (F3) | Thorium |
| 2 | T5 | Bottletree, Amber | **Bottletree** (F3) | Lead |
| 2 | T6 | Gumboab, Palo | **Gumboab** (F3, = today's Savanna Bark F3 ids) | Dusk |
| 3 | T7 | Fir, Cedar | **Fir** (F4) | Cobalt |
| 3 | T8 | Spiral, Poisoned, Windwillow | **Spiral** (F4) | Chromium |
| 3 | T9 | Redwood, Ice | **Redwood** (F4, = today's Northern Bark F4 ids) | Azurvane |
| 4 | T10 | Burnt, Sadwillow | **Burnt** (F5) | Adamantite |
| 4 | T11 | Petrified, Wisteria_Wild | **Petrified** (F5) | Slag |
| 4 | T12 | Sallow, Fire | **Sallow** (F5, = today's Wastes Bark F5 ids) | Cinder |
| 5 | T13 | Jungle, Bamboo | **Jungle** (F5) | Mithril |
| 5 | T14 | Banyan, Camphor, Fig_Blue | **Banyan** (F5) | Titanium |
| 5 | T15 | Crystal, Stormbark | **Crystalwood** (F5) | Lumen |

- Groups follow the zone biomes (Zone 1 Emerald Grove + Autumn / Azure forests, Zone 2 savanna / desert, Zone 3 Borea / north, Zone 4
  wastes / volcanic, Zone 5 jungle - Zone-Gathering-Spec "Zone N woods") and the Bazaar price tiers (economy.md) inside a zone. All 34 ids
  are placed once. Spare designs (Birch, Ash, Aspen, Azure, Palo, Cedar, Poisoned, Bamboo, BlueFig, Camphor, Fire) stay for later colourways.
- Art gap: the 26 designs escalate in 5 steps, so Zone 4 + Zone 5 share F5-level looks; the Zone 5 sets (Jungle, Banyan, Crystalwood)
  may want one more "cooler" pass (Q11). Every new set must be checked in game (none is yet).
- Gear: the 5 existing set ids stay (F1 = T1, F2 = T3, F3 = T6, F4 = T9, F5 = T12 - same looks, new tier slots); 10 new sets
  `Armor_Foraging_<Tree>_<Slot>` (the manifest's prefix: Beech, Dry, Bottletree, Fir, Spiral, Burnt, Petrified, Jungle, Banyan,
  Crystalwood = 40 pieces), our own art shipped as is (GA2_ART "art/gathering-armor"). Bands = the T's metal band. Stats: extend
  GA2_STAT_DEF over 15 tiers (interpolate between today's 5 points; the "four power sources" rule). Tier-up ladder = the Enchanted log of
  the next tier's key tree (round C1 made every collection's own Enchanted item).
- tier_tags LOGS -> 15 groups at T1..T15; Enchanted logs follow their base. Hatchet gate (gate.oreTiers-style "logs three up refused")
  reads the new log T - the 15-step hatchet ladder already exists (G23).

## 6. Farming: 15 crop tiers (3 per zone)

"are there 15 crops?" - 14 vanilla bench crops with seeds + Eternal seeds (Wheat, Lettuce, Carrot, Corn, Cauliflower, Turnip, Pumpkin,
Aubergine, Tomato, Chilli, Cotton, Rice, Potato, Onion). Other plants: Health / Mana / Stamina herbs 1-3 (9 plants with seeds, no Eternal),
Berry bushes (3 blocks, no seed), Mushrooms (`Plant_Seeds_Mushroom` exists), Apple (tree), Wild seeds; seeds with no crop item:
`Plant_Seeds_Sunflower`, `Plant_Seeds_Beans_Purple` (unfinished in vanilla).

| Zone | T | Crop | Bench pair today |
|---|---|---|---|
| 1 | T1 / T2 / T3 | Wheat / Lettuce / Carrot | P1, P1, P2 |
| 2 | T4 / T5 / T6 | Corn / Cauliflower / Turnip | P2, P3, P3 |
| 3 | T7 / T8 / T9 | Pumpkin / Aubergine / Tomato | P4, P4, P5 |
| 4 | T10 / T11 / T12 | Chilli / Cotton / Rice | P5, P6, P6 |
| 5 | T13 / T14 / T15 | Potato / Onion / **Mushroom** (default 15th) | P7, P7, - |

- 15th crop (Q12): default Mushroom - it already has a vanilla seed, a Farming collection and cave biomes (Zone 5 caves); no Eternal seed
  yet (add `Plant_Seeds_Mushroom_Eternal` of ours). Alternatives: our own Zone 5 crop (like our own ore per zone, needs art), or the herbs
  as a 3-step side ladder.
- Keeps the LOCKED Farmer's Workbench pair order; seeds / Eternal seeds = their crop's T. tier_tags CROPS -> T1..T15 (today pairs sit at
  T1 / T2 / T4 / T7 / T10 / T13 / T16). Zone-Gathering-Spec farm pairs per zone get re-split to these 3 crops per zone.
- Tools: hoe / sickle / Harvester have only Crude / Copper / Iron / Thorium (+ vanilla hoes); for 15 crop tiers the hoe + sickle get the
  15-step ladder like the pickaxe / hatchet did in G23 (new `<M>_SkyWynn` hoe + sickle ids, recoloured icons) - Q13, own round after this one.
- Farming armor art: 7 "Harvest" sets exist only as PLACEHOLDERS (`Armor_Farming_P1..P7_<Slot>`, vanilla Cloth_Cotton model recoloured:
  Wheat, Carrot, Cauliflower, Pumpkin, Chilli, Cotton, Onion; Gear `:6133`, GA2_ART "placeholder"). No real farming armor models exist
  (art/ has Foraging only). Default: keep the 7 ids at T1 Wheat, T3 Carrot, T5 Cauliflower, T7 Pumpkin, T10 Chilli, T11 Cotton, T14 Onion;
  add 8 placeholder recolours (Lettuce, Corn, Turnip, Aubergine, Tomato, Rice, Potato, Mushroom) now; Quirk draws 15 real crop sets later.

## 7. Build order (one mod per builder, after Gear 0.3.28 + Mobs 0.1.11 are pinned)

1. **SkyyGear 0.3.29** (Opus, full round): step 1 tools/tier_tags.py TT_VERSION 3 (METAL_BANDS, ZONE_TOPS, LEVEL_BANDS, LEVEL_CRUDE, LOGS,
   CROPS, gathering armor rows, test_tier_tags.py); then 2.2 + 3.3 + migrate0329 + the Foraging / Farming armor ladders (5 + 6).
2. **SkyyMobs 0.1.12** (Opus): 2.5 + migrate0112.
3. **SkyyArmory 0.1.35** (Opus): 2.4.
4. **SkyyCollections 0.2.28** (Opus): log / crop / seed / Enchanted tags + tier unlocks on the 15 ladders; Mushroom Eternal seed if Q12 = yes.
5. **SkyyBazaar 0.1.22** (Opus): 2.6 + Bronze armor pricing + new tier sort.
6. **SkyyAuctions 0.1.14** (lean): 2.6.
- Cross-check all six together, pin, deploy TOGETHER. Main session after: Class Balance Workbench + Progression Map refresh, TEST-CHECKLIST.
- Later rounds: 15-step hoe / sickle (Q13); Zone-Gathering-Spec farm / grove split; Fishing overhaul (waits, Skyy).
- Wynn elements move up one version: Gear elements = **0.3.30**, Mobs elements = 0.1.13.

## 8. Test in game
- /smithing > Mining armor: Copper 1-8, Iron 8-15, **Bronze 15-23**, Thorium 20-28 ... Lumen 95-103, Onyxium last.
- Furnace Charm T1 equipped -> /craft Furnace smelts Copper + Iron -> Bronze; craft a Bronze Mining piece at the Armor Bench.
- Hover a Maple log ("T3 Maple"), a Gumboab log ("T6"), a Turnip ("T6"); Foraging armor list shows 15 sets.
- Zone 2 desert mobs show Lv 30-40; a Zone 3 boss counts as Zone 3 (Mythic bag).

## 9. Questions for Skyy (popups, one at a time; defaults in brackets)
- Q2 Onyxium (Zone 6, parked) 100-108 and Lumen to 103 - the last levels need a rebirth-raised cap? [yes]
- Q3 Non-metal drop gear (Stone, Steel, Doomed, Scarab, Prisma, cloth, leather ...) keeps its tier tag, levels stretched to the new zones (1.1)? [yes]
- Q4 Mob zones: Zone 1 1-20 (unchanged), 2 20-40, 3 40-60, 4 60-80, 5 80-100? [yes]
- Q5 Bronze Mining set recipe = Iron's amounts with Bronze bars at the Armor Bench (vanilla's cheaper 3 / 6 / 2 / 4 is the other option)? [Iron's amounts]
- Q6 Bronze smelting stays behind Furnace Charm T1, or smelts without the charm? [keep the charm gate]
- Q7 Gear already made keeps its saved level; new drops use the new bands? [yes]
- Q8 First-run cap 50 (+10 a rebirth, 100 at rebirth 5) - set SkyySkills class / skill max to 50 if it is 100 today? [yes, in Server Setup]
- Q9 Ornate Bronze (3 pieces) stays a combat drop? [yes]
- Q10 The 15 tree groups + one armor set each (section 5 table)? [the table]
- Q11 Zone 5 tree sets (Jungle, Banyan, Crystalwood) get one more "cooler" art pass? [yes, Quirk, after the build]
- Q12 15th crop = Mushroom (with our own Eternal seed)? [Mushroom]
- Q13 Hoe + sickle get the full 15-metal ladder like pickaxe / hatchet (own round)? [yes, next]
- Q14 Farming armor: 8 more placeholder recolours now, real art later? [yes]
