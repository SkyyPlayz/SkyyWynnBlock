# Pack check: StructureV2 (+ joszza's DungeonBosses / River Bridges) and Souls like Bosses (2026-10-22)

Three pack candidates: (A) StructureV2 + joszza add-ons (sections 1-9), (B) joszza's DungeonBosses + River Bridges (sections 5-6),
(C) Souls like Bosses 1.3.7 by Bananaph0ne (section 10). Boss-family decision across all of them: section 10.5.

Read-only check (Sonnet). Sources: the jars in Skyy's Mods folder (copied to scratch, read, scratch deleted), CurseForge pages (WebFetch,
checked 2026-10-22), `PACK.md`, `tools/deploy_set.py`, NewBetaTest `config.json` (read only). Permission: `docs/answered/world.md` 2026-10-22
JOSZZA ANSWER ("Hi, sure, no problem. Everything is compatible. The merchant can be disabled in /sv2 admin or .json"). Nothing was built,
edited, deployed or sent.

Legend: VERIFIED = read in the jar / page. UNVERIFIED = needs the smoke test or an in-game look.

## 0. Short answer

- **StructureV2 0.1.7 = PACK it, merchant OFF.** Covered by joszza's reply (the ask named "OpenStructure + Dungeons and more Structures"; the
  StructureV2 page IS "Dungeons and more Structures", main file `StructureV2-0.1.7.jar`, 0.7).
- **StructureV2 alone has NO bosses.** The bosses (Bandit Boss, Astral Voidcaller, Ice Magus, Astral Sigil, boss rewards) are the separate
  mod **DungeonBosses 0.1.2** (`joszza:DungeonBosses`, CurseForge "Dungeons And More structure (boss)", 385 downloads, hard-requires
  StructureV2). Its page and manifest differ from the StructureV2 page, so the 10-22 reply (which named two other projects) does not clearly cover it.
- **River Bridges 0.1.1** (`joszza:RiverBridges`, 0.7, ARR, no modpack text) is a separate project, not covered by name.
- OpenStructures 0.1.4 (hub) is NOT needed: StructureV2 has its own engine; OpenStructures is an empty engine with no content ("Not a
  drop-in replacement for StructureV2 content"). Skip it (see 6).
- Today NewBetaTest has StructureV2, YUNG's, AncientConstructs, Marsi, MajorDungeons, Adathan, UltimateBossFight all `Enabled:false`; none of
  joszza's mods is in `PACK_THIRD_PARTY`.

## 1. What StructureV2 0.1.7 adds (VERIFIED from the jar)

Manifest `joszza:StructureV2`, `ServerVersion "*"`, no required deps (optional: joszza:Structure, Hytale:NPC, WorldEvents, Lootr). Main
`com.joszza.structurev2.StructureV2Plugin`. 195 asset files, ~140 own classes (385 classes counts the bundled Gson).

**Structures** - 33 spawn-rule files `Server/WorldGen/StructureV2/Prefabs/*.json` (+ 36 prefabs `Server/Prefabs/Structure/`). Placed by the mod's
own `ChunkPlacementListener` when a chunk is GENERATED - **new chunks only** (existing explored terrain is not changed; the OpenStructures page
says the same). Rules use `ZoneMask` (vanilla names `Zone1_*`..`Zone4_*`) + `BiomeMask` + `SpawnChance`, spacing, `MaxInstancesPerWorld`.

| Zone | Structures (rule id, biome, chance) |
|---|---|
| Zone 1 | Stonehenge (Plains, 0.99, max 48), plains_ruin1, plains_tavern, tavern_house (also Z3), goblin_base, Big_Tower_Goblin, Camp, kweebec_guard + camp2, magic_tower_plains (Ice Magus tower despite the name), windmill (on its own StructureV2_Wheat_Fields biome patch), minor_landmarks (angel statue, waterwell, small island), big_tree, **boss_island** (Forest, 0.35, max 20; Bandit Boss), sewer (Z1-2), big_miner (chance 0) |
| Zone 2 | feran_desert, feran_desert_big (Savanna / Scrub), dead_monster 1-3 (Z1-3 Desert / Savanna / Tundra) |
| Zone 3 | **ice_boss** (Glacier / Frozen / Tundra, 0.28, max 12; Astral Voidcaller crater), frozen_tower (Ice Magus), mineshaft (Tundra), merchant_camp_wagon (chance 0 = placed by the merchant event, Z1 + Z3) |
| Zone 4 | jungle_ruin1 (Wastes_Lava / Forest_Roots, 0.7, max 80) |
| Ocean (any zone except Zone4) | ship1, ship2, ruin_ship 1-2 (Sv2_Ship_* pirates), AirShip, AirShip1 (floating ships) |
| Off | flying_islands, island_angel_statue (chance 0) |

Also two biome tile files `Server/World/Default/Zones/Zone1_Tier1|Tier2/Custom.StructureV2_Wheat_Fields.json` (a rare wheat-field biome patch that
the windmill targets) - **the only worldgen asset; it does NOT override any vanilla world-gen file** (Settings.json etc. untouched), so no clash
with SkyyWorldGen's files by path. Overrides of vanilla ids (8): `Furniture_Goblin_Coffer` item + `Coffer_Goblin_Loot_Wave1-5` drop files (the goblin
coffer loot) and the vanilla `Undead/Skeleton` NPC group + attitude files. See 2.

**Which worlds:** every world with the vanilla V1 `ChunkGenerator` that has Zone1_ - Zone4_ zones (the listener calls
`ChunkGenerator` / `Zone` / `Biome` and reads the world seed). There is no world allow-list setting in `settings.json`. So: the vanilla
`default` world and any world SkyyWorldGen builds on the V1 painted-mask path (research/SkyyWorldGen-Plan.md Plan B) get structures; **Void
island worlds (SkyyIslands per-profile islands) have no ChunkGenerator, so nothing spawns there** (UNVERIFIED: confirm in the smoke test /
`/sv2 list`). Whether `skywynn_zones` (SkyyWorldGen 0.7.8) reports `Zone1_*` zone names is UNVERIFIED - if it uses the V2 HytaleGenerator,
the mod's zone/biome masks will not match and nothing places. Test: stand in a new zone chunk, `/sv2 entries`, `/sv2 spawn camp`.

**NPCs in StructureV2 (VERIFIED, 17 role files):** `Sv2_Bandit_Minion`(+ _Aggressive / _Defensive / _Mixed) camp / island raiders; `Sv2_Ship_Archer /
Cutthroat / Grenadier / Raider / Spearman` ship pirates; **`Sv2_Local_Trader`** (the traveling merchant; BarterShop `Sv2_Local_Trader`, spawn
`Sv2_Local_Trader`, WorldEvent `Sv2_Merchant_Camp_Event` + 4 stages). Bandit minion groups: `Sv2_BanditMinion`, `Sv2_Ship`.

**Items (VERIFIED):** `Sv2_Structure_Money` (a block-item "treasure pile", max stack 999, description "Boss coin. Spend at the traveling
merchant."), `Sv2_Weapon_Sword_Voidice` (parent `Weapon_Sword_Frost`, Quality Epic, ItemLevel 42, 15 physical base), `Sv2_Weapon_Staff_Voidice`
(poison bomb + frost orb + 3-shot signature), `Sv2_Ability_Voidice_IceWall` (ability item), `Sv2_Tool_Repair_Kit_Voidice` (restores ONLY
Voidice gear; custom interaction `StructureV2:VoidiceRepairKit`), `Furniture_Goblin_Coffer` (vanilla id overridden). No recipes, no armor.
**Loot tables:** `Drop_Sv2_Ice_Boss_Chest` (Astral Sigil + Structure Money 12-20 + choices; 24 % of the rare slot is one of the four Voidice
items, 6 % each), `Drop_Sv2_Ship`, `Drop_Sv2_Windmill_Farm`, `Drop_Sv2_Local_Trader` (empty), goblin coffer waves.

**Commands (VERIFIED):** `/sv2` (permission `structurev2.admin`; sub: `admin` panel, `reload`, `list [page] [world]`, `tp <i>`, `spawn <entry|prefab>`,
`entries`, `flush`, `clear` + `confirm`, `nearby [r]`, `validate`, `merchant` (`force`, `clear`), `boss ...`, `exportskin`, `devmode`, `discord`). `/sv2bosses`
belongs to DungeonBosses.

**Config files:** per world, in the plugin data dir `<world>/mods/<joszza_StructureV2>/` (exact folder name UNVERIFIED - no data exists in Skyy's
saves yet because it was never enabled; our `getDataDirectory` convention is `<world>/mods/Skyy_*`, the author's folder will be
`joszza_StructureV2` or similar): `settings.json` (written by `PluginSettings`; keys `worldgenEnabled`, `lazyBossIslandMaterializeRadius`,
`ambientFaunaSoftCap`, `defaults`, per-entry `overrides` {`enabled`, `chance`, `minBetween`, `minOther`, `ignoreOther`, `maxBiome`, `maxWorld`}, a
`merchant` block, a `boss` block, a `compat` block), `structurev2-spawns.json` (placed list), `structurev2-merchant-camp.json` (merchant session),
`merchant_shop.json` (copy of the bundled barter shop). **Merchant OFF key: `merchant.enabled = false`** (MerchantSettings fields: `enabled`,
`firstDelaySeconds` (default 3600), `cooldownMinSeconds / MaxSeconds`, `durationSeconds`, `maxSpawns`, `aetherhavenTownExclusion*`). Also settable in
`/sv2 admin` (Settings tab). Exact nesting UNVERIFIED until the file exists: after the first smoke run read it and set the key.
`merchant_camp_wagon` has chance 0, so with the merchant off no wagon camp and no trader ever place.

## 2. Duplicates / clashes

### 2.1 vs OUR mods

| Their thing | Ours | Clash? | Decision |
|---|---|---|---|
| Traveling merchant camp + `Sv2_Local_Trader` + barter shop | SkyyMerchants (one roaming merchant per zone, rumours, special-weapon shop) | Yes, duplicate | **Ours wins; theirs OFF** (`merchant.enabled false`; joszza confirmed the switch) |
| `Sv2_Structure_Money` (boss coin, only useful at their merchant) | SkyyCoins (the one currency) | Yes: a second currency | With merchant off it is dead weight in the boss chests. Do not trade it. See 3 |
| Voidice sword / staff / ice wall / repair kit | SkyyGear grades (UT / Mythic), SkyyArmory, lifelong tools (no repair) | Overlap in kind (more weapons) not id | Treat as plain pack weapons, see 3 |
| Repair kit | SkyyGear lifelong tools | Kit only works on Voidice gear and uses its own interaction | Harmless; keep as a boss-gear mechanic or hide |
| Bandit Boss (500 / 3 phases), Astral Voidcaller (2000 HP), Ice Magus mini boss (520 HP), minions, pirates | SkyyMobs levels + elite / boss ranks | No id clash; fixed HP numbers ignore our level curve | Rank rows (3) |
| Structure chests / ship loot (vanilla drops + Gold bars, sapphire) | SkyyExploration luggage + loot chests (per-profile chest loot rule: loot is per profile, chests not shared) | Their chests are normal world containers (one shared loot for all players, first come); Lootr optional would make it per-player | Install **Lootr** only if licence allows (not yet checked) - else treat as "world containers", fine for dungeon rewards; flagged below |
| Goblin coffer item + loot waves (vanilla ids overridden, 8 files) | none of ours | Overrides vanilla goblin coffer loot | Accept (only vanilla goblin camp coffers change) - but see 2.3 for load order |
| Boss island / ice crater / ice tower structures | SkyyWorldGen / SkyyZones | Different placement systems: theirs on new chunks via zone masks | Compatible if the zone world exposes `Zone*_` names (UNVERIFIED); SkyyZones' block-break gate / regen applies inside their prefabs (decide: structures inside zones are breakable? SkyyZones spec decides) |

### 2.2 vs the dungeon / structure mods in Skyy's Mods folder (all Enabled:false today)

| Mod | What | Overlap with StructureV2 + DungeonBosses | Best | Switch off |
|---|---|---|---|---|
| **StructureV2 + DungeonBosses** | overworld structures + 3 boss encounters, floating boss islands, merchant | - | **Best for open-world structures and bosses (pack)** | - |
| MajorDungeons 0.4.15 (MAJOR76, 0.7) | instanced dungeons, 120 NPCs, 178 items, own currency + merchants + mounts | own currency / merchants clash with SkyyCoins / SkyyMerchants; huge item set vs our gear rules | not packable (ARR, no permission) | stays OFF |
| AncientConstructs 1.2.3 (DanBagh) | construct boss + bench + charging station | ARR, none yet | stays OFF (learn) | OFF |
| YUNG's HyDungeons (0.1.1) | procedural instanced dungeon via portal | instanced, different shape from overworld structures | not duplicate of StructureV2 but overlaps our capstone dungeon spec | OFF (ARR, ask) |
| Marsi_Dungeon 0.4.0 | prefab-random dungeons, 458 items, 165 NPCs | big item set; manifest says server 2026.03.26 (old) | OFF | OFF |
| Adathan / UltimateBossFight / DungeonBosses' neighbours | extra bosses, portals | more boss rows | OFF | OFF |

Result: the pack needs only ONE structures-and-bosses family. StructureV2 + DungeonBosses (permission asked) is the one; none of the
others is enabled and none should be. No two enabled mods add the same structure or boss.

### 2.3 Vanilla overrides to know (VERIFIED against Assets.zip)

- StructureV2: 8 vanilla files (goblin coffer item + 5 loot-wave drop files + Undead Skeleton group + attitude).
- DungeonBosses: 29 vanilla files - 13 vanilla particle textures (Smoke, Glow, Ball6, EarthSpike ...), Skeleton_Frost_* roles (9 vanilla
  frost skeleton NPC roles: Archer, Archer_Patrol, Archmage, Fighter, Fighter_Patrol, Knight, Mage, Mage_Wander, Ranger) and the same Undead Skeleton
  group / attitude. So it **changes vanilla frost skeletons everywhere** (Zone 3 undead). Any of our mods that edits or levels `Skeleton_Frost_*`
  (SkyyMobs tables, `Skeleton_Elite` rows) must be re-checked after install. PROJECT-RULES 2: "Never ship a file overriding their item ids"
  is about THEM; here THEY override vanilla - it is theirs to ship, our rule is only that we do not edit it. Particle texture overrides can
  change other mods' visuals (smoke) - UNVERIFIED how visible.

## 3. How OUR code should treat each thing (and which mod changes)

| Thing | Treatment | Our mod / change |
|---|---|---|
| `Sv2_Structure_Money` | Coin pile block-item, stack 999. Merchant off = no use. **Convert to coins on pickup** is cleanest: a small SkyyCoins listener turns it into N coins (suggest 1 Structure Money = 1 coin x boss tier multiplier; default [10 coins]) and removes the stack; fallback (no code): add it to Bazaar / sell list as a low-value sellable. Do not block (Skyy loses loot silently) | SkyyCoins (pickup listener, SET bump) OR SkyyBazaar sell price row; decision for Skyy |
| `Sv2_Weapon_Sword_Voidice`, `Sv2_Weapon_Staff_Voidice` | Grade by id as plain pack weapons (like Armory / Crossbow packs): Sword = Warrior / Assassin melee rule, Staff = Mage staff rule; in SkyyGear they are **NOT Untiered and NOT Mythic** unless Skyy decides boss weapons count as Mythic ("boss gear" lock: Mythic = boss gear). Epic quality, ItemLevel 42 -> map level through the one SkyyGear level table; tier tag via `tools/tier_tags.py` | SkyyGear (id rows + tier tags, new SkyyGear version); SkyyClasses (staff rule) only if the staff is not already matched by id pattern |
| `Sv2_Ability_Voidice_IceWall` | An ability item: leave it alone, it needs no grade (it is not a gear slot). Check SkyyTrees / class ability slots do not treat unknown `Ability` items as weapons | none expected |
| `Sv2_Tool_Repair_Kit_Voidice` | Keep (only works on Voidice gear). Make sure SkyyGear lifelong-tool code ignores it (it is `Tool_Repair_Kit` parent, tag Tool) | SkyyGear check; no change if the repair-kit recipe code keys on vanilla ids |
| `Furniture_Goblin_Coffer` | vanilla container; fine | none |
| Bandit Boss / Astral Voidcaller / Ice Magus | Add rows in the SkyyMobs rank table: `Sv2_CompositeBoss_P1/P2/P3/Dormant` (one boss, 3 phase roles - treat all four as one Boss rank, level = zone of the boss island: Forest Z1 -> Lv 20ish band, decision), `Sv2_Astral` = Boss (Zone 3), `Sv2_Magic` + `Sv2_Magic_Decoy` = Mini boss, `Sv2_Bandit_Minion*` = normal / Elite, `Sv2_Ship_*` = normal. **Caution:** the boss changes phase by swapping the NPC role (P1 -> P2 -> P3): SkyyMobs must keep the level / health modifier across the role swap (UNVERIFIED; test) | SkyyMobs (rank rows + a phase-swap test); SkyyGear boss drops (their drop tables are fixed - our Mythic boss gear would need a separate drop hook) |
| Boss drop tables | They hold Structure Money, gold bars, sapphires, potions and the Voidice items. For SkyyWynn boss gear (Mythic) add our own drop through SkyyGear's boss-drop path; their tables stay | SkyyGear |
| Quests | optional: SkyyQuests "defeat the Bandit Boss island" objective by NPC role id | SkyyQuests (later) |

Version table (proposal, not built): SkyyGear 0.3.38 (Voidice id rows + tier tags + ignore repair kit), SkyyMobs next (rank rows, phase-swap
test), SkyyCoins next (Structure Money conversion) or SkyyBazaar sell row, deploy_set.py (PACK_THIRD_PARTY + config tuning). No change to
SkyyMerchants. SkyyWorldGen / SkyyZones only if the zone-world test shows the masks do not match (then a world-gen zone-name alias, or a
`defaults`/`overrides` tweak in `settings.json`).

## 4. Licence / credit text and exact deploy_set steps

Licence: **All Rights Reserved**, CurseForge shows no modpack sentence. joszza's written reply (2026-10-22, quoted above) is the permission
to include the structure mods in the SkyWynn pack. Keep the screenshot / quote in `docs/answered/world.md`. Rules we keep: install from the
author's CurseForge page, never bundled, never copy prefabs / models / textures / NPC files, never edit their item ids, merchant OFF.

PACK.md row (draft, one line like the others):
`| StructureV2 "Dungeons and more Structures" (joszza:StructureV2) | joszza | 0.1.7 | StructureV2-0.1.7.jar | Overworld structures in new chunks (camps, towers, mine, ships, boss islands) for the open zones (Skyy, 2026-10-22; joszza agreed in the CurseForge comments: "Hi, sure, no problem. Everything is compatible. The merchant can be disabled in /sv2 admin or .json"). Merchant camp OFF (duplicates SkyyMerchants); Sv2_Structure_Money converted by SkyyCoins; Voidice items graded by id; bosses: see DungeonBosses row. LICENCE: All Rights Reserved; permission = joszza's reply; credit "StructureV2 / Dungeons and more Structures by joszza" with link https://www.curseforge.com/hytale/mods/dungeons-and-more-structures in the pack description + server credits; never bundled; never edit its files. Overrides 8 vanilla files (goblin coffer loot + undead skeleton group). No dependencies. |`

Credit line for the server credits / pack description: `Structures and bosses by joszza (StructureV2, DungeonBosses, River Bridges) - https://www.curseforge.com/members/joszza/projects`.

deploy_set.py pack-config steps (the deploy script, not this check, does them; third-party keys):
1. Add `"joszza:StructureV2"` to `PACK_THIRD_PARTY` (pins it ON in the world config; today it is `Enabled:false`).
2. Add the config writer `tune_structurev2` in the style of `tune_perfect_parries` / BetterMap's allowedWorlds step: after the first run (file
   must exist) set in `<world>/mods/<StructureV2 data dir>/settings.json` `merchant.enabled=false` (missing-fields-only, keep hand edits, History
   snapshot first, change-log line). Until the file exists the merchant would spawn after `firstDelaySeconds` 3600 s - so on the first deploy ship
   the world with the settings file pre-seeded (create the data dir + a minimal `settings.json` `{"merchant":{"enabled":false}}`) OR deploy
   StructureV2 disabled in step 1 for one smoke run, read the file, then enable. Exact JSON nesting must be taken from the generated file (UNVERIFIED).
3. Smoke test (`python tools/smoke_test.py`): needs `[StructureV2] ...` ready line (the mod's name; expected text UNVERIFIED), no asset
   validation failure, no SEVERE; also run `/sv2 validate` in a V1-zone world.
4. Record: `python tools/record_deploy.py` + PACK.md row + log; Dungeons / merchant duplicate choice in PACK.md.
5. Install DungeonBosses only after step 1 works (hard dependency; `DungeonBosses` throws "StructureV2 not registered" otherwise).

Rollback: remove from PACK_THIRD_PARTY and the pack; `structurev2-spawns.json` keeps placed structures in the world (already placed
prefabs stay as blocks, boss NPCs become unknown roles) - treat like removing Better Mob Expansion (stop, clear boss islands first with `/sv2 clear`).

## 5. DungeonBosses 0.1.2 - "Dungeons And More structure AND BOSSES" (full check)

| Item | Result |
|---|---|
| Jar | `DungeonBosses-0.1.2.jar`, 11.6 MB in Skyy's Mods folder (so installed already); manifest `joszza:DungeonBosses` 0.1.2, requires `joszza:StructureV2` |
| CurseForge | "Dungeons And More structure (boss)", 385 downloads; page: game 0.7, latest file DungeonBosses-0.1.2.jar (2026-10-20), All Rights Reserved, no modpack text, "REQUIRES StructureV2" |
| Contents | 395 asset files; the boss code lives in package `com.joszza.structurev2.boss` + `com.joszza.dungeonbosses` (admin page, `/sv2bosses`); includes 72 byte-identical copies of StructureV2's own files (duplicates harmless) |
| NPCs | `Sv2_CompositeBoss_Dormant/P1/P2/P3` (Bandit Boss, 500 HP per phase, weapons Daggers_Mithril / Battleaxe_Onyxium / Mace_Mithril, 3 phases), `Sv2_Astral` (Astral Voidcaller, 2000 HP, ritual boss), `Sv2_Magic` / `Sv2_Magic_Decoy` (Ice Magus mini boss, 520 HP), Skeleton_Frost_* (9 vanilla roles overridden) |
| Items | `Sv2_Astral_Sigil` (key, consumed on summon), `Sv2_Astral_Brazier`, `Sv2_Trap` (trap plate), the 4 Voidice items (also in StructureV2 jar) |
| Loot | `Drop_Sv2_Bandit_Boss` (Structure Money 12-20 + Astral Sigil + gold / sapphire / potions), `Drop_Sv2_Astral` (money 8-14 + choices), `Drop_Sv2_Magic` (money, gold / silver / thorium bars, potions, poison bombs), Voidice gear only from the ice-boss crater chest (6 % each) |
| Structures it uses | `boss_island`, `ice_boss`, `frozen_tower`, `magic_tower_plains` (placed by StructureV2 rules) |
| Commands | `/sv2 boss ...` (spawn bandit phase 1-3, astral, god, islandRespawn, debug), `/sv2bosses admin` (boss settings: battle music, aggro grace, island respawn) |
| Worlds | same as StructureV2 (V1 chunk generator zones); arena "boss island" is "lazy" (materialises near players) - `lazyBossIslandMaterializeRadius` |
| Duplicates | bosses vs SkyyMobs (rank rows; fixed HP), Structure Money vs SkyyCoins, Sigil / Brazier no duplicate, frost skeleton override vs vanilla / SkyyMobs |
| Licence | ARR, no modpack text. **NOT clearly covered** by the 10-22 reply: the ask named "OpenStructure + Dungeons and more Structures". The comment thread is on the StructureV2 page; "Everything is compatible" may include the boss add-on but do not assume. -> **second ask (cheap)** |
| Verdict | **Worth a second ask, then pack** (best boss content on offer; no other pack mod adds these bosses). Until joszza answers keep it out of the pack (StructureV2 alone works without it; the structures that hold bosses (boss_island, ice_boss crater, towers) would be empty/inert shells - consider setting those overrides `enabled:false` if DungeonBosses is not installed) |

Note: the StructureV2 jar already contains the Voidice items and 4 bandit / ship NPC roles, so without DungeonBosses: ships and camps work,
bosses and the sigil gate do not.

## 6. River Bridges 0.1.1 (full check)

| Item | Result |
|---|---|
| Jar | `RiverBridges-0.1.1.jar` in Skyy's Mods folder; `joszza:RiverBridges`; optional dep `joszza:StructureV2`; website github.com/jesuisjoszi/River-Bridges |
| CurseForge | 0.7, latest RiverBridges-0.1.1.jar 2026-10-21, All Rights Reserved, no modpack text, 105 downloads |
| What | Natural wooden / stone bridges over rivers during world generation ("YUNG-inspired", from YUNG's Better Bridges idea): oak log span, stone deck, a large decorated bridge, damaged and fallen-tree variants (prefabs `bridge1`, `broken_bridge1` + variant ids from `bridges.json`, e.g. `kweebec_bridge`), and a rare archer guard `Rb_Bridge_Guard` (120 HP, bow, vanilla loot `Drop_Outlander_Marauder`, stays on the bridge) |
| How placed | `RiverCrossingScanner` / `BridgeChunkPlacement`: on chunk generation it finds river water (needs a river biome check `requireRiverBiome` / `isRiverPlainsBiome`, `getZoneBiomeResultAt`), spacing stored in `riverbridges-spawns.json`; config `Server/RiverBridges/bridges.json` (`enabled`, `spawnChance`, per-variant `chance`, `alternateChance`, `biomeMask`, `guardChance`) |
| Commands | `/rb list [page] [world]`, `/rb tp <i>`, `/rb find [radius]`, `/rb devmode` (permission `riverbridges.admin`) |
| Worlds | worlds with the vanilla ChunkGenerator + river biomes (Zone 1-3 rivers). No rivers = no bridges. Void island worlds: nothing. Skyy's solo islands cut from vanilla terrain are the ones that could get bridges (UNVERIFIED) |
| Duplicates | none with our mods (no bridge builder; guard NPC is one more outlander-like mob: needs a SkyyMobs normal-rank row `Rb_Bridge_Guard`). Not a duplicate of StructureV2 (no river bridges there); StructureV2 compat class `StructureV2BridgeCompat` stops them overlapping |
| Licence | ARR, no modpack text; NOT named in the 10-22 ask -> **second ask** |
| Verdict | **Worth a second ask, then pack.** Low risk, cosmetic, tiny (105 downloads); it fills the "rivers feel empty" gap; SkyyWorldGen islands would need rivers for it to show up. |

## 7. The other 11 joszza projects (checked via CurseForge pages 2026-10-22)

| Project | What | 0.7? | Licence | In StructureV2? | Dupes in our pack | Verdict |
|---|---|---|---|---|---|---|
| Dungeons and more Structures | = StructureV2 | 0.7 (+0.6, 0.5) | ARR | is the same | - | covered |
| **Dungeons And More structure (boss)** | = DungeonBosses | 0.7 | ARR | separate add-on (requires SV2) | SkyyMobs ranks | second ask (5) |
| **River Bridges** | bridges | 0.7 | ARR | separate | none | second ask (6) |
| Open Structure | worldgen hub: spawn / paste engine, admin UI, Java API; no content; 0.1.4 | 0.7 (+0.6) | ARR | engine only; SV2 has its own copy of it (SV2 predates it; OpenStructures scans legacy `Server/WorldGen/StructureV2` rule packs for migration) | duplicates SV2's engine | **skip** (not needed: SV2 works alone; running both could double-place the same legacy rule files - do NOT enable both). The 10-22 reply names it, so it is covered if a future joszza content pack needs it |
| More Bandit | roaming bandit camps with hideout + squad, night "hunt parties"; 0.1.1 | 0.7 | ARR | no (separate mod) | overlaps StructureV2 Camp + Bandit minions and SkyyMobs elites; hunt parties vs our zone threat design | skip (duplicate of StructureV2 bandit camps - "take the best one") |
| Hostile Doors | hostile NPCs open doors while chasing; admin menu; 0.1.0 | 0.7 | ARR | no | none; touches NPC AI of all mobs incl. SkyyMobs ones; denylist Kweebec / Feran_Civilian | optional, low value; ask only if Skyy wants it (default: skip; buildings are not a defence in our design) |
| Music Display | Spotify "now playing" HUD overlay; 0.1.8 | 0.7 | **MIT** | no | overlaps SkyyHud HUD; per-player Spotify login | **MIT = may be used without asking** but it is a personal-account feature, not server content; skip for the pack, mention as optional client-side. Never fold |
| Echo Relic (Beacon) | craft a 3-stage beacon fuelled with gold bars: Heal / Speed (stamina) / Mana regen aura, range grows with crystals; 1.0.0 | 0.7 (+0.6) | ARR | no | overlaps our Mana / stat design (potions, accessories, pets = four power sources; a free buff aura affects balance of Mana regen) | second ask only after Skyy decides a beacon fits (default: skip; check balance first) |
| hyChunks | chunk pre-generation tool; 0.1.2 | 0.7 (+0.6) | ARR | no | RechunK / world tools; server-owner tool, not pack content | skip (admin tool; owners may install themselves) |
| Shared Inventory | joke mod, all players share one inventory; 0.1.0 | 0.6 only | ARR | no | conflicts with profiles, bags, coins | **skip** (hard clash with SkyyProfiles / Sacks / Bank) |
| Structure Info - debug | `/` tool to scan + highlight nearby prefabs; 0.1.0 | 0.6 only | ARR | no | none | skip (debug tool for creators) |
| Lock Chest Better System | locks for chests, containers, benches; trusted players, passwords, lockpick minigame; 0.1.0 | 0.5 only (old) | ARR | no | overlaps SkyyIslands / SkyyGuilds protection, per-profile chests; would lock our island chests | skip (old version; our protection system is design-owned) |
| Table Games | poker + blackjack with stakes; "jszza-games-1.1.0" | Early Access (old) | ARR | no | own stakes currency vs SkyyCoins | skip (casino with its own money; a coins-based SkyyCasino idea would be our own) |
| Hot Air Ballon (prefab) | one hot-air-balloon prefab zip | 0.5 | ARR | partly: SV2 has AirShip prefabs | none | skip (ideas only; Skyy's mount rules: "take the best one" - mounts are pets/dragons) |

## 10. Souls like Bosses 1.3.7 (Bananaph0ne) - full check

Source: `Soulslike_Bosses-1_3_7.zip` in Skyy's Mods folder (read, scratch deleted) + CurseForge page `/hytale/mods/soulslike-bosses` (checked 2026-10-22).

### 10.1 Licence / version
Manifest `Bananaphone:Souls_Like_Bosses` 1.3.7, `ServerVersion ">=0.7.0 <0.8.0"`, asset pack only (no code, no dependencies). Page: main file
0.7, 1.3.7 dated 2026-10-21, licence field "All Rights Reserved" BUT the Permissions block says: modpacks allowed ("You're free to include
this mod in modpacks"), dependency use allowed, **no reupload, no paid / monetised packs or ad-link distribution**. => **Covered by the
page itself, no ask needed.** Rule for PACK.md: install from the author, never bundled; NonCommercial-type clause: if SkyWynn ever sells
ranks / perks, remove it or ask Bananaph0ne first (same flag as The Armory).

### 10.2 What it adds (VERIFIED)
- **Bosses (CurseForge names; roles `SLB_*` under `Server/NPC/Roles/Boss/`, all fixed HP, no level):**

| Boss | Role ids (HP) | How it is met |
|---|---|---|
| The Nightlord | `SLB_Nightlord` (2500) | Instance "Tree of the Nightlord": `PortalKey_Nightlord` (10 Plant_Fruit_Azure, Arcane Bench) + Portal Device; its entrance tree is also placed by worldgen in temperate / tropical OCEANS (modifier `SLB_Tree_Of_Night`) |
| Abyss Watchers | `SLB_Abyss_Watcher_Main` (2500) + Hostile / Support (500) | world boss in Zone 4 ash wastes / wasteland grassland (encounter + arena template) |
| Curse Plagued City (4 bosses) | `SLB_Gravedigger` (1125), `SLB_Gravedigger_Beast` (1125), `SLB_Bishop` / `_Aerial` (2000), `SLB_Rubeus_Beast` (1500) (+ `Rubeus_Human`, `Conductor` 2000 / 5000 disguise, werewolf / abomination / crawler "Mythic creature" NPCs) | portal dungeon (Void instance `Curse_Plagued_City`, 30 min limit): `PortalKey_Curse_Plagued_City` = 5 Wolf_Paw at the Arcane Bench, OR the world event "Curse Breach" (opens a portal, shown on the map) |
| Frenzied Bramblekin | `SLB_Frenzied_Bramblekin` (2500) | Zone 1 aspen / autumn forests (worldgen modifiers `SLB_Kweebec_Lager_Forest_*`); drops `Ancient_Calamity_Sealed_Place_Portal` |
| Goblin Ogre | `SLB_Goblin_Ogre_Boss` (1250) | Zone 1 plains (modifier `SLB_Goblin`), also instance Goblin King Lair via `PortalKey_Goblin_King_Lair` (5 Goblin_Ear) |
| Ancient Calamity (3 phases: Hooded Figure -> Unleashed Horror -> Ancient Calamity) | `SLB_Ancient_Calamity_P1/P2` (3000 each) + 100000-HP helper entities | sealed place "Roots of the World" (portal block item dropped by the Bramblekin; Seal Breaker needs Skeleton_Skull + 2 Eye_Of_Frenzy + 2 Goat_Horn; recipe note item) |
| Abandoned Kweebec Village / Catacombs of Carthus | instances with keys (5 Onion / 10 Fire Essence) | portal dungeons |
| Henchman, Rifle_Henchman | NPC roles (rifle = a GUN mob) | camp mobs inside dungeons |

- **Keys / portals:** 5 `PortalKey_*` items (Rare, ItemLevel 51, Arcane Bench recipes with vanilla items: Plant_Fruit_Azure, Onion, Fire Essence,
  Wolf_Paw, Goblin_Ear). Instance worlds are `WorldGen Void` with `Env_SLB` (`Server/Instances/*`, `Server/PortalTypes/*`) - they run anywhere, independent
  of our world generator.
- **Items (13 + ingredient items):** `Weapon_Sword_Darkmoon` (Epic, ItemLevel 50, has a recipe), `Weapon_Sword_Farron` (Uncommon 20),
  `Weapon_Cane_Conductor`, `Weapon_Spellbook_Bishop`, `Weapon_Staff_Frenzied` (Epic 50), `Weapon_Battleaxe_Ogre_Wood_Fence` (Epic 60),
  `Weapon_Gun_Blunderbuss_Gravedigger` (a GUN), `Ancient_Calamity_Sigil_Staff`, `Rune_Writhing_Flame`, ingredients `Goat_Horn / Goblin_Ear / Wolf_Paw /
  Skeleton_Skull / Eye_Of_Frenzy`, blocks `Ancient_Calamity_Amber_Block / Glowing_Grass / Glowing_Sallow_Trunk`, `Deco_Seedling_Head`,
  portal blocks. Boss drop tables (`Server/Drops/NPCs/Boss/*`) give the matching weapon + bars (e.g. Nightlord: Darkmoon sword + 5-10 Mithril bars).
- No commands (asset pack), no config file. Nothing is switched off by a setting except removing the mod.

### 10.3 Vanilla overrides - THE RISKS (VERIFIED by diff against Assets.zip; 74 vanilla files overridden, 21 JSON)
1. **`Server/GameplayConfigs/Default.json`** - adds the global "Curse Breach" world event to the universe gameplay config. This vanilla
   GAMEPLAY config is also touched by other mods/SkyyWorldGen? (check before enabling; if SkyyWorldGen or a Skyy mod ships a GameplayConfigs
   file the two overwrite each other - load order wins). The event is "Transient" and starts a map-marked portal at random.
2. **`Server/Entity/Stats/Health.json`** - changes the NPC health regen delay 15 -> 45 (and removes a comment): a GLOBAL NPC stat file. It would
   change regen for every mob including SkyyMobs-levelled ones and may clash with any Skyy mod that writes Health stat modifiers (SkyyClasses /
   SkyyMobs modify values, not this file; verify at the smoke test).
3. **Vanilla mob drop tables** (12): goblins (Duke, Lobber, Miner, Scrapper, Thief), black wolf, goat, skeleton variants (Skeleton, Fighter, Mage,
   Soldier, Burnt_Praetorian) - they gain the key ingredients (Goblin Ear, Wolf Paw, Goat Horn, Skeleton Skull). **Clash with our mob-drop rules**
   (SkyyGear UT / mob bag drops use these drop lists; PACK Armory drops use them too, research/Pack-Drops-Spec.md). Both mods overwrite
   the same files: whichever loads last wins. => Must be resolved before pack (see 10.4 "Skeleton_Elite").
4. `Portal_Device` item (adds the usable flag + `GameplayConfig: Portal`), `Rock_Ice` (friction 2 / drag 0 = non-slippery ice), `Gun_Shoot_Flintlock_Charging`,
   `NPC/Groups/Void.json`, `NPC/Groups/.../Goblin.json` and ~50 particle / texture / model files.
5. Worldgen: 6 `Server/WorldGen/Modifier/SLB_*.json` files that ADD biome prefabs into vanilla zone biomes by rule
   (`Zones.Zone1_Tier1.Tile.Plains_*`, `Zones.Oceans.Tile.Temperate_*` ...). They are modifiers on the vanilla `Default` world generator root
   and extend, not replace, vanilla world gen (no Settings.json override), so no file clash with SkyyWorldGen. Needs the V1 zone system - same
   caveat as StructureV2 (UNVERIFIED for `skywynn_zones`). Instance bosses (Curse City, Lair, Nightlord, Calamity) work in any world.

### 10.4 Fit with SkyyMobs ranks / SkyyGear rules
- **Rank:** every `SLB_*` boss role = **full boss** except where Skyy says otherwise (Bramblekin, Goblin Ogre, Ancient Calamity, Nightlord, Abyss
  Watchers, Gravedigger / Bishop / Rubeus / Conductor = full bosses; Henchman, Rifle_Henchman, Beast_* = normal / elite). Helper entities
  (100000 HP "Flame_Emitter", "Fake_Death", "Entombed", "Dying", "Transforming" roles) must be EXCLUDED from SkyyMobs levelling and drop rolls
  (they are invulnerable markers; a rank row for them would break the boss fight).
- **P4 fixed boss levels** (Balance-P4 spec: Chieftain 18 / Goblin Duke 38 / dragons 78 / 98; "bosses get fixed levels + one health pool"):
  assign by the zone/difficulty the boss lives in: Goblin Ogre (Z1 plains) ~Lv 20, Frenzied Bramblekin (Z1 forest) ~Lv 20-25, Nightlord
  (ocean instance, key at Azure fruit = Z1-2) ~Lv 38, Curse City (Wolf Paw, Z1-2) bosses ~Lv 38-45, Abyss Watchers (Zone 4) ~Lv 78, Ancient Calamity
  (needs the Bramblekin portal) ~Lv 98 final. Final numbers = Skyy / balance round. SkyyMobs applies one Health pool over the boss's phases;
  Ancient Calamity swaps roles between phases (P1 -> P2) like joszza's Bandit Boss: SkyyMobs must carry the level over a role swap (UNVERIFIED).
  All SLB HP values (1125-3000) are far below a Lv 78 boss, SkyyMobs' health scaling must overwrite them.
- **Drops:** boss drop tables are fixed (weapon + Mithril bars). Mythic only from full bosses (docs/answered/gear.md 10-16 / 10-22): add the SLB
  boss role ids to SkyyGear `bosses.roles` so they also roll Mythic Sigil / boss Mythic gear; their own weapons stay as plain pack weapons
  (Epic quality, ItemLevel 50-60, graded by id like Armory weapons, NOT UT / Mythic by themselves).
- **Crafting rule:** "No UT or mythic on crafted items" (10-22): `Weapon_Sword_Darkmoon` has a recipe - keep it a plain pack crafted item, never UT /
  Mythic; `PortalKey_*` recipes use vanilla items at the Arcane Bench (the Arcane Bench is vanilla). Key ingredients (Plant_Fruit_Azure,
  Plant_Crop_Onion_Item, Ingredient_Fire_Essence) are zone crops / mob drops: Onion is a Zone 5 crop in our design, so the Kweebec Village key
  is a late-game thing - OK, just document it.
- **Guns:** `Weapon_Gun_Blunderbuss_Gravedigger` + `Rifle_Henchman` conflict with Skyy's "No guns" (mobs.md 2026-10-09 "gun bandits -> No guns").
  The Blunderbuss is only a boss drop; decide: keep (boss-only), or exclude from the drop list (cannot edit their files). Default: leave it - the
  Gravedigger fight is built around it.
- **Weapons vs class rules:** Darkmoon / Farron = swords (Warrior / Assassin), Bishop Tome = Spellbook (Mage?), Cane / Didgeridoo staff -> check
  their tags (`Family: Axe`, odd) so SkyyClasses weapon-class mapping does not treat them as axes; Gravedigger Blunderbuss tag Gun.
- **Four power sources / gear:** nothing here is armor; no accessory / pet clashes.

### 10.5 Overlap with the other boss / dungeon mods - keep the best of each kind

| Kind | Candidates | Best | Why / what to switch off |
|---|---|---|---|
| Overworld mini/world boss + structure in open zones | DungeonBosses (Bandit Boss island Z1, Ice crater Astral Z3, Ice Magus towers) vs Souls like Bosses (Goblin Ogre, Bramblekin Z1, Abyss Watchers Z4, Nightlord ocean) | **both can stay** - different bosses in different places | No same-thing duplicate: Z1 has 3 world bosses from two mods; thin them via `settings.json` structure `enabled:false` for boss_island if Z1 is too crowded |
| Instanced portal dungeon | SLB Curse Plagued City / Kweebec Village / Catacombs / Lair, YUNG's HyDungeons, MajorDungeons, Marsi, Adathan | **Souls like Bosses** (modpack permission stated, 0.7, key flow with the vanilla Arcane Bench) | YUNG / MajorDungeons / Marsi / Adathan stay OFF (ARR, no permission, own currency / items) |
| Boss weapons | Voidice items (SV2), Darkmoon / Farron / Cane / Tome / Didgeridoo / Ogre Fence (SLB), Armory boss specials | all kept as drops (different weapon types: frost sword + staff vs sword / cane / tome / staff / axe) | Both swords: Voidice Blade (Epic 42) vs Darkmoon (Epic 50) - Skyy may want one sword per zone; dupe-rule asks "best version of each": keep both unless Skyy prefers fewer |
| Merchant / currency | SV2 merchant + Structure Money; SLB has none | ours (SkyyMerchants / SkyyCoins) | SV2 merchant OFF |
| Boss arena mechanics / boss bar | SV2 DungeonBosses boss bar + music, SLB encounter manager (`EncounterManager`) | SLB uses vanilla EncounterManager (the engine's boss UI); SV2 has its own | no clash; both fine |

Result: pack **StructureV2 (+ DungeonBosses + River Bridges after the second ask) AND Souls like Bosses**; no third boss/dungeon mod is
needed. The risk is not duplicates of bosses but the **shared vanilla-file overrides**: Skeleton_Frost_* + Undead/Skeleton group + goblin coffer
(SV2 / DungeonBosses) and goblin / wolf / skeleton drop tables + Health.json + GameplayConfigs/Default.json (SLB). The Undead `Skeleton`
group file is overridden by BOTH StructureV2 and DungeonBosses and SLB overrides skeleton drop files: check at the smoke test that the surviving
copies keep every mod working (SLB skeleton drops lost = no Skeleton_Skull for the Seal Breaker).

### 10.6 Our-mod changes for Souls like Bosses (proposal, not built)
SkyyMobs: rank rows for `SLB_*` (full boss) + exclusion list for helper entities; fixed boss levels (balance round). SkyyGear: add the boss
roles to `bosses.roles`; weapon id rows + tier tags (Darkmoon, Farron, Cane, Tome, Didgeridoo, Ogre Fence, Blunderbuss). PACK.md row +
credit "Souls like Bosses by Bananaph0ne - https://www.curseforge.com/hytale/mods/soulslike-bosses (modpack use allowed on its page; no reupload,
no paid packs)". `deploy_set.py`: add `"Bananaphone:Souls_Like_Bosses"` to `PACK_THIRD_PARTY`; smoke test for the vanilla-file overrides
above (Health.json, GameplayConfigs/Default.json, drops) - if the Health.json NPC regen change is unwanted it cannot be edited (their file);
choose accept or leave the mod off.

### 10.7 Verdict
**PACK it** (licence allows it; best instanced-dungeon + soulslike-boss content on offer), **with conditions**: (1) smoke test shows no
load-order damage from the vanilla overrides; (2) SkyyMobs rank rows + helper-entity exclusion built first; (3) SkyyGear boss roles/drop
rules added; (4) Skyy decides on the gun items. Until (2)+(3) are deployed keep it OFF so its bosses do not appear unlevelled.

## 8. Questions for Skyy (each with default)

1. **Add DungeonBosses (bosses) and River Bridges to the pack now, or only after joszza says yes?** [Wait for joszza: StructureV2 first,
   the two others after the reply - their licences are ARR and the 10-22 reply named other projects.]
2. **Structure Money: convert to coins on pickup (1 Structure Money = 10 coins) or sell it at the Bazaar?** [Convert to coins on pickup.]
3. **Voidice weapons: plain pack weapons (no UT, no Mythic), or Mythic boss gear?** [Plain pack weapons, boss tier in SkyyGear by id, no Mythic.]
4. **Bandit Boss island is Zone 1 forest (a boss at the very start): ok, or off until Zone 2+?** [Keep it on but only after the zone world is tested; if the boss is too hard at Lv 1-10 set `boss_island` `enabled:false` in settings.json.]

5. **Souls like Bosses: add it (modpack use allowed on its page) once SkyyMobs rank rows and the SkyyGear boss roles are ready?** [Yes, after those two rounds.]
6. **Gun items (Gravedigger Blunderbuss, Rifle Henchman) from Souls like Bosses: keep as boss-only, or skip the mod?** [Keep - boss-only drop.]
7. **Accept Souls like Bosses' global vanilla overrides (NPC regen delay 15 -> 45 s in Health.json, the Curse Breach world event, mob drops of goblins / wolves / skeletons)?** [Accept after the smoke test; the drop-table overlap with Armory / UT mob drops decides it.]

## 9. Follow-up message draft for Skyy to post to joszza (Skyy sends it; nobody else contacts joszza)

> Hi joszza, thanks again for the okay on StructureV2 - the merchant will be switched off in the pack, and everything is credited and linked
> to your CurseForge page (never re-uploaded). Two more of your mods fit our server pack really well: **DungeonBosses** (the bosses add-on for
> StructureV2) and **River Bridges**. May we list both in the SkyWynn modpack / server pack in the same way (credit + link, players install
> them from your pages, no files changed or re-uploaded)? Also: are the Voidice items and Astral Sigil okay to react to by id (we only grade /
> price them, we do not edit them)? Thank you!

(Only the two uncovered mods are asked. OpenStructure is covered by the 10-22 reply but not needed. Everything else on the author page is
skipped, so no ask.)

## UNVERIFIED (so the next session knows)

1. Exact plugin data-dir name and JSON nesting of the merchant key (file does not exist until the first run).
2. Whether `skywynn_zones` / SkyyWorldGen worlds report `Zone1_*` zone names so the masks match; whether Void island worlds are ignored.
3. Whether SkyyMobs keeps level / health across the boss role swap (P1 -> P2 -> P3).
4. Whether the vanilla Skeleton_Frost_* override (DungeonBosses) changes frost skeleton stats our Mob Curve assumes.
5. Whether the 13 overridden particle textures change other mods' visuals.
6. Lootr licence (optional, per-player containers).
7. Not played in game; not run in a smoke test (no game start allowed in this check).
