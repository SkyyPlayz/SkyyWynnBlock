# Mob spawns + mob variety (spec, 2026-10-27)

Where this goes: research/ (specs). Answers to the open questions at the end go to `docs/answered/mobs.md` (`python tools/qa_append.py
mobs <file> --close "..."`); the build rounds named in section 6 go to RESUME "Next". Engine facts here were read from the 0.7.x
server jar (javassist, tools/dev/) and Assets.zip (read-only, scratch copy deleted). UNVERIFIED = needs the PROBE list (section 7).

## 0. Goal (Skyy's words, docs/answered/mobs.md 2026-10-27)

> "can you increase mob spawn rates, especially for the skeletons in the over world. but it would be great fi we could also get more
> mob variety especially for normal regular monsters to fight everywhere. wynn craft does this by giving more difficult versions armor
> an stuff."

So: (A) more mobs in the overworld (the zones world `skywynn_zones2`), skeletons first; (B) more kinds of normal monsters everywhere,
the Wynncraft way - tougher versions of the same mob (armour, better weapon, a name word), not only new bodies.

Not in scope: island worlds (SkyyIslands, environment `Env_Default_Void` = no world spawns; the camp skeletons are placed by code),
Combat Shard islands (SkyyShards has its own spawner + rows), dungeons / bosses (StructureV2, DungeonBosses, Souls like Bosses).

## 1. How vanilla spawning works (engine facts)

- **Spawn tables** = `Server/NPC/Spawn/World/<Zone>/*.json` (`WorldNPCSpawn`): a list of environments, NPCs with `Weight`, `Flock`
  size, `SpawnBlockSet`, `DayTimeRange`, `LightRanges`, `MoonPhaseWeightModifiers` (0-2 per moon phase). Each NPC + environment pair may
  appear in ONE file only (engine SEVERE "Combination NPC %s with Environment %s defined before in configuration %s" - the second is
  dropped). Beacons (`Spawn/Beacons`, caves / mineshafts) and markers (`Spawn/Markers`, prefab camps, respawn `P1D` = once a game day)
  are separate spawners.
- **Density** = the environment's `SpawnDensity` (`Server/Environments/...`, inherited from the parent env). The engine
  (`WorldEnvironmentSpawnData.adjustSegmentCount / setDensity`): expected NPCs of an environment = (block columns of that env in loaded
  chunks) x density / 1024 = **density NPCs per loaded 32 x 32 chunk** of that environment. Each NPC entry gets expected x weight /
  sum of weights of every entry in that env (`updateExpectedNPCs`). So weight = share, density = total.
- Zone 1 densities: `Env_Zone1` 0.5 (Plains inherits it), Forests / Autumn / Swamps 0.9, Mountains 0.3, Caves 0.5, Goblin caves 3,
  Deeproot 2. Zone 2: 0.2-0.5. Zone 3: 0.3-0.9.
- **World cap** `GameplayConfig.MaxEnvironmentalNPCSpawns` ("The absolute maximum number of environmental NPC spawns. < 0 for
  infinite"), read in `WorldSpawningSystem.tick`; vanilla Default.json does not set it (default value UNVERIFIED, P7).
- **Live hooks** (public): `WorldEnvironmentSpawnData.setDensity(double, Store)` (per world, per env; recalculates every chunk),
  `SpawningPlugin.getEnvironmentDensity`, `WorldSpawnData` resource (`SpawningPlugin.getWorldSpawnDataResourceType`). Weights live in
  `RoleSpawnParameters` (no setter). `WorldSpawnManager.updateSpawnParameters` re-reads the env density on an asset reload, so a live
  density must be re-applied after one. Admin readout exists: vanilla `/spawn stats` (`SpawnStatsCommand`, syntax P1).
- **NPC equipment**: a role has `Weapons` / `OffHand` (vanilla uses them everywhere) and an `Armor` list (only vanilla TEST roles,
  e.g. `Test_Combat_Knight`: Armor_Iron_Head / Chest / Hands / Legs). The LOOK comes from the model: skeleton models have `Parent:
  Skeleton` (-> `Player`) and `DefaultAttachments` / `RandomAttachmentSets`; vanilla `Showcase_Skeleton_Tank` already wears
  `Items/Armors/Copper/Head.blockymodel` + `Items/Armors/Iron/Legs.blockymodel` + an iron battleaxe = **player armour models on a
  skeleton work as attachments** (vanilla-proven shape; client draw P5).

## 2. Why the overworld feels empty (numbers)

Vanilla gives skeletons their own small "Wander" files and lets animals / critters / fish share the same environments:

| Env (Zone 1) | density / chunk | daytime weight sum | skeleton weight | skeleton share | skeletons per chunk |
|---|---|---|---|---|---|
| Plains (meadow rims) | 0.5 | 129 | 4 (Fighter 3 + Wander 1) | **3 %** | ~0.015 (1 per ~65 chunks) |
| Forests / Autumn | 0.9 | 91 | 7 (+ Burnt Praetorian 2) | 8 % | ~0.07 |
| Mountains | 0.3 | 72 | 7 | 10 % | ~0.03 |
| Azure | 0.9 (Forests line) | 111 | 12 (Fighter, Mage, Praetorian) | 11 % | ~0.10 |
| Swamps | 0.9 | 157 | 12 | 8 % | ~0.07 |

(Weight sums count every WorldNPCSpawn entry of the env except the night-only Void files; fish entries count because they share the
env. Night adds Void Larva / Crawler / Eye at weight 40-75 per env, which dilutes skeletons further. Whether entries outside their
DayTimeRange drop out of the sum: P4.) Hostile share of the whole Zone 1 day table is ~10-20 %; the rest are critters, animals and
fish. On top: our world is floating islands over void (fewer land columns per loaded chunk than vanilla land), SkyyZones removes
natural hostile spawns in towns + safe regions, and the vanilla Zone 1 skeleton roster in the world tables is only Skeleton_Fighter
(+ Mage + Burnt Praetorian in the harder biomes). Knight, Soldier, Archer, Ranger, Scout, Archmage, Elite exist but spawn only from
prefab camp markers once a game day.

## 3. What already exists (vanilla -> pack -> ours)

### 3.1 Vanilla variants (use first)
- Skeletons, 5 families x up to 9 roles (MaxHealth / weapon): plain Skeleton_Fighter 70 (random weapon), Scout 61 (crude bow),
  Archer 60 (rusty iron bow), Ranger 49 (crossbow), Mage 49 (wand), Archmage 88 (staff), Soldier 100 (rusty axe, chest plate),
  Knight 130 (rusty steel sword + shield, helm + chest), Elite 350 (giant longsword; boss-like); Sand (Z2: Guard, Assassin, Mage,
  Archer, Ranger, Scout, Soldier, Archmage), Frost (Z3: Fighter, Soldier, Knight, Mage, Archer, Ranger, Scout, Archmage), Burnt (Z4:
  Soldier, Knight, Lancer, Praetorian 226, Archer, Gunner, Alchemist, Wizard), Incandescent (Z4: Fighter, Footman, Mage, Head).
  Each has `_Wander` / `_Patrol` copies. Models already show a ladder: Fighter 3 attachments (tunic, boots) -> Soldier + chest plate
  -> Knight + helmet = vanilla's own "armoured versions".
- Other hostile families: Goblins (Scrapper 36, Thief 30, Miner 140, Lobber 80, Guardian 90, Burner 160, Glutton 700), Trorks (61 each,
  Chieftain 124), Outlanders (Z3: Berserker / Marauder / Priest / Sorcerer 103, Brute 124, Hunter / Stalker 61), Scarak (Z2), Zombies
  (Zombie 90, Frost 81, Sand 49, Burnt 126), Wraith 193, Ghoul 193, crystal Golems (one per element: Earth / Flame / Frost / Sand /
  Thunder = elem1's element bodies).
- Armour models for the look (Common/Items/Armors): Copper, Iron, Bronze, Bronze_Ornate, Steel, Thorium, Cobalt, Adamantite, Mithril,
  Onyxium, Prisma, Leather_*, Trork_Warrior, Orbis_Knight ... = one vanilla set per tier step of tools/tier_tags.py LADDER.

### 3.2 Pack mods + Skyy's Mods folder
| Mod | State | What it adds to spawning | Verdict |
|---|---|---|---|
| Better Mob Expansion 3.5 (Frah, GPLv3) | in PACK.md but **PACK_DISABLED** since 0.7.0 (boot failure: BME_Bomb_Damage) | own spawn files (new ids, no vanilla override): BME_Elite_Skeleton (+ Frost / Sand) weight 4 in Z1 Plains / Forests / Mountains, Hellscourge Trork, Kamikaze goblin, crocodiles, leopards ... ~30 | separate re-test (smoke with it on); if it boots, it is extra bodies, not our variant ladder - keep it as "more kinds", our ladder stays ours. Never copy its files (GPL). |
| NoCube Undead Warriors 0.1.0 | off | OVERRIDES vanilla Wander_Zone1_Tier1 / Tier2 (adds NoCube_Undead_Warrior, random weapon, 100 HP) | clashes with A2 (same two files) - stays off; ours wins. Learned: overriding the Wander files is how mods do it. |
| StructureV2 + DungeonBosses + River Bridges (joszza) | on | camp markers, 33 spawn rules (own files), DungeonBosses overrides 9 vanilla Skeleton_Frost_* roles | no clash if our files never repeat an NPC + env pair and our variants are NEW role ids (build asserts both). |
| Souls like Bosses | on | bosses; overrides 74 vanilla files (some drops) | not touched. |
| Aures Rare Monsters | off (pets.md 2026-10-22: Nestkeeper only) | 54 rare variants | stays off (decision stands). |
| Endless Elite Mobs, MmoMobScaling, PJ-Difficulty | off | mob scaling | skip - SkyyMobs does levels / ranks (Mod-Survey-0.7 clash list). |
| Spawn Manager + Assets (MIT) | off | per-mob on/off by patched copies, restart, no zones | skip (Mods-Folder-Survey: our own files do it); learned: patched copies of the vanilla files. |
| Forgotten Creatures, PJ Blood Moon / Mob Events, InvasionX, Slime Mobs! | off | hidden vanilla creatures / events / slimes | later, own checks (Slime Mobs! is in the Augments queue). |

CurseForge (quick survey 2026-10-27, licences not checked): IncreaseNPCSpawns (up to 3x all spawns, passive too), SpawnControl (live
density + weight), Not Enough Skeletons (more skeleton spawns), RPGMobs (elite NPCs with stats + equipment; author warns removing it
can leave broken elites), Elites (abandoned; elite Archer / Archmage / Fighter / Knight / Mage / Soldier). Verdict: **learn, not
pack** - a flat spawn multiplier raises animals too and has no zones / Server Setup; elite mods duplicate SkyyMobs ranks. Learn
from SpawnControl (live density + weight edits = the P2 / P3 hooks) and RPGMobs (equipment on elites, the leftover-entity warning).

### 3.3 Ours (must not clash)
- **SkyyMobs 0.1.20** (SET pin): level from the spawn point's biome / env band (20 levels a zone), the P4 level curve, elites (3 %
  roll per UUID, +3 levels, x3 Health / x1.5 damage; *_Elite* / *Captain* ... always), mini bosses / bosses, elements (elem1: `elem.mobs`
  table, Frost = Water, Burnt = Fire, Sand = Earth ...; the plate shows the element), nameplate `[Lv 9] Elite Name` (plate colours are
  an UNVERIFIED client feature, `plate.colorOn` OFF), Spoils drops, kill credit, `mob:fn:info` (hpMult / dmgMult / xpMult / rank) read by
  SkyySkills (kill XP), SkyyGear (gear rolls), SkyyClasses. It has NO spawn control today.
- **SkyyZones 0.3.2**: no natural hostile spawns in town / safe regions (`zones:fn:noSpawn`; a natural spawn = environment set).
- **SkyyWorldGen 0.7.11**: zones world built from vanilla Env_ZoneN_* environments (so vanilla tables + SkyyMobs bands apply); its
  "spawn remap" is crops only.
- **SkyyShards / SkyyIslands**: own code spawns (NPCPlugin.spawnNPC), untouched.

## 4. Proposal A - spawn rates (skeletons first)

Three levers, cheapest first. Weights move the SHARE (more monsters, fewer critters, same NPC count = no performance cost); density
moves the TOTAL (more of everything in that env).

**A1 Hostile weights (build time, the skeleton fix).** SkyyMobs ships its own copies of the vanilla `Wander_ZoneN_TierN` files
(generated from Assets.zip at build, never committed - PROJECT-RULES 2), plus one new file per zone for the vanilla roles vanilla
leaves to camps. Default: every skeleton weight x3, Zone 1 lists gain Soldier, Knight, Archer, Scout (Tier 1-2) and Ranger, Archmage
(Tier 3); Z2 Sand, Z3 Frost, Z4 Burnt / Incandescent the same way. Plains skeleton share 3 % -> ~10 %, Forests 8 % -> ~22 %.
Other hostile families (Trork, Goblin surface camps, Outlander, Zombie, Scarak) x1.5 where they already spawn - no new places.
**A2 Density per zone (live).** Server Setup > Mobs > Spawns: `spawn.density.z1` .. `z5` (% of vanilla, default 125, 0-300), one
optional table `spawn.density.env` (Env id = %), applied with `setDensity` per world on start + after an asset reload, only to
Env_ZoneN_* environments in worlds listed in `spawn.worlds` (default the zones world + the vanilla default world; never island /
instance worlds). Caves keep 100 % (beacons; the volcanic caves are already "really hard"). **A3 Per-family rows (live)** -
`spawn.family.<Skeleton|Trork|Goblin|Outlander|Zombie|Scarak|Void>` (%): if P3 passes (the weight field can be changed live +
`recalculateWeight`), they scale A1's weights live; if it fails they still apply after a restart (the build cannot rewrite the jar, so
SkyyMobs would need its own top-up spawner - only if Skyy wants live family control; not in the default plan).

Result with defaults (A1 x3 + A2 125 %): Zone 1 plains skeletons ~0.015 -> ~0.06 a chunk (~4x), forests ~0.07 -> ~0.25 (~3.5x);
total NPCs +25 %. Day and night both (skeletons are 0-24 in vanilla; Skyy R5: no night bonus).

Performance: NPC count = density x loaded chunks; the weight change adds none. +25 % density = +25 % NPC AI in the loaded area of each
player; the spawner itself is vanilla (no new tick). Watch server tick after deploy (the open "shared scheduler stalls" item in RESUME:
do not deploy A2 above 125 % until that is read). An admin readout `/mobs spawns` (env, density %, expected / actual, skeleton share;
admin only, requirePermission + setPermissionGroups(new String[0])) reads WorldSpawnData - no world change.

## 5. Proposal B - variety the Wynncraft way

Wynncraft fills a zone with the same family in several strengths (e.g. "Skeleton", "Armoured Skeleton", "Skeleton Veteran"),
each visibly geared, each worth more. Ours, vanilla first:

**B1 Vanilla roster first.** A1 already puts Soldier (chest plate) and Knight (helm + chest + shield) into the world tables: that is
vanilla's own armoured ladder at no build cost.

**B2 Tier variants (new role ids, our assets).** For each common family role (Skeleton Fighter / Soldier / Archer / Scout, the Sand /
Frost / Burnt equivalents, Trork Warrior / Hunter / Guard, Goblin Scrapper / Miner, Outlander Marauder / Berserker, Zombie), generated
at build:
- `Skyy_<Role>_Armored` and `Skyy_<Role>_Veteran`: a copy of the vanilla role (or a Variant of it - P5) with a new model = the vanilla
  model + vanilla armour attachments of the zone's metal (tools/tier_tags.py LADDER: Z1 Copper -> Iron -> Bronze, Z2 Thorium ->
  Steel/Cobalt, Z3 Cobalt -> Adamantite, Z4 Mithril, Z5 Onyxium / Prisma; Veteran = full set + shield / better vanilla weapon).
  Health / damage come from SkyyMobs ranks (below), NOT from an armour stat (Skyy R5 2026-10-01 "no mob armour" - one damage rule, the
  P4 curve stays the single source; the role `Armor` list is left empty).
- Spawned by our A1 files: within the zone's Tier 1 / 2 / 3 lists (easy / middle / hard biomes) Plain : Armored : Veteran =
  70 : 25 : 5 (Tier 1), 55 : 35 : 10 (Tier 2), 40 : 40 : 20 (Tier 3). Rows `variant.mix.t1..t3`.
- New SkyyMobs ranks (Server Setup > Mobs > Ranks): **Armored** x1.4 Health / x1.15 damage / +1 level, **Veteran** x1.9 Health /
  x1.3 damage / +2 levels; the existing Elite roll (3 %) still goes on top of any of them. Rank word in front of the name:
  `[Lv 12] Armored Skeleton Soldier`, `[Lv 14] Veteran Trork Hunter`; element word as elem1.
- **Rarity colour on the nameplate** (PROJECT-RULES 4): plain = Normal white, Armored = Unique `#FFFF55`, Veteran = Rare `#FF55FF`,
  Elite = Legendary `#55FFFF`, Mini boss = Fabled `#FF5555`, Boss = Mythic `#CC66CC` (SUI.RARITY). The plate colour is still an
  UNVERIFIED client feature (P6); until it passes the rank WORD carries it and `/mobs inspect` shows the colour name.

**B3 Element variants (elem1).** Per zone a small share of the variant mix uses the zone's element (Augments-Spec Z2-Z5 Thunder /
Water / Fire / Air; Z1 = Earth from the Golem_Crystal_Earth body) - an `elem.mobs` entry per variant id (`Skyy_*_Armored_Fire` is NOT
needed: the element is a SkyyMobs table entry, the body stays). Default: 10 % of Armored / Veteran spawns get the zone element (row
`variant.elemPct`), shown on the plate as today. Ties into Augments A3 ("drops + element mobs") - share the table, one round.

**B4 Drops / XP.** Kill XP already follows `mob:fn:info` (xpMult = min(1, health share) x min(rank Health x, 10)): Armored pays ~x1.4,
Veteran ~x1.9 - no new XP code. Spoils: rank rows `rank.armored.spoils` +25 %, `rank.veteran.spoils` +50 % on the existing Spoils
chances; SkyyGear's gear roll reads the rank string - Armored / Veteran count as normal kills for the Elite-only gear roll (no new
gear rule; Mythic stays boss-only). The vanilla armour a variant wears never drops (economy: the set prices are SkyyGear's).

**B5 Balance vs research/balance/targets.md (read only).** Combat table: trash 4.4 hits (expected kit), tough 12.5. Armored x1.4 =
~6 hits, Veteran x1.9 = ~8.4 hits (between trash and tough - the "harder version" without becoming a wall). Default mix average HP
x1.25 (Tier 2) at the same level; XP follows HP so XP per minute of fighting is unchanged. The model's 150 kills/h is a GUESS: if
Skyy's empty world runs below it, more spawns bring the real pace up TO the model, not past it; the risk is less walking between
fights -> faster class pace. Check after deploy: one 20-minute Zone 1 session, kills per hour from the SkyySkills log line vs 150
(> 200 = lower A2 to 100 % first, then A1's x3 to x2). Four power sources unchanged (variants are sized against the expected kit =
weapon + gear + accessories + pets). Do not run balance_model.py --md / --combat for this; a later model tweak only adds the
variant mix to the kill-XP assumption.

## 6. Build rounds (SkyyMobs mainly)

| Round | Mods | Size | What |
|---|---|---|---|
| **spawn1** | SkyyMobs 0.1.21 | Full (new admin command, several pack mods' files checked) | A1 weight files (+ B1 vanilla roster), A2 density rows + `setDensity` hook, A3 rows (live if P3), `/mobs spawns`; build asserts: no NPC + env pair already in Assets / any SET jar / pack jar except the vanilla files we replace, every id is a vanilla role |
| **variety1** | SkyyMobs 0.1.22 (+ SkyyGear only if its rank reader needs the two new words; SkyySkills / SkyyClasses read hpMult, no change) | Full (new ranks feed XP + loot) | B2 role + model assets, ranks Armored / Veteran, plates + rarity words, B4 Spoils rows; tier_tags table untouched (mobs have no item tier) |
| **variety2** | SkyyMobs (+ Augments A3) | with Augments A3 | B3 element share |

Saved data / rollback:
- spawn1: no saved data; new config keys only (missing line = default, no migration). Rollback alone to 0.1.20 = vanilla weights +
  densities back at the next start; extra mobs already spawned despawn normally.
- variety1: variant role ids are saved in chunks with the mobs. Rolling back to a jar without them = "Reloading nonexistent role"
  WARNs (seen with BME after it was switched off: harmless, they vanish). Before a rollback: `variant.on` OFF, then `/mobs strip
  variants` (new admin sub-command: removes loaded Skyy_*_Armored / _Veteran mobs) or wait a game day. Floor note in deploy_set.py.
- Load order: our replacement Wander files must win over vanilla (P4). NoCube Undead Warriors stays off (same files).

## 7. PROBE list (engine first, one short probe each, on a scratch copy)

1. `/spawn stats` syntax + baseline expected / actual per env in the zones world (Zone 1 envs), skeleton count in 128 blocks.
2. `setDensity` live on the WorldSpawnData resource: expected NPCs move, stays until an asset reload, re-apply works.
3. Live weight: can `RoleSpawnParameters` weight be changed (reflection on the final field) + `recalculateWeight` take it? (A3 live.)
4. A jar asset at `Server/NPC/Spawn/World/Zone1/Wander_Zone1_Tier1.json` replaces vanilla's (no "defined before" SEVERE); entries
   outside their DayTimeRange leave the weight sum.
5. Variant role: `Type: Variant` with `Reference` = a concrete vanilla role (Skeleton_Fighter) vs a full copy; a model with
   `Items/Armors/<Set>/*.blockymodel` attachments draws on a skeleton (Showcase_Skeleton_Tank shape) and on a Trork / Goblin (non-Player
   skeleton models - may not fit; then skeletons + Outlanders only).
6. Nameplate colour (`/mobs platetest`, which markup the client draws) - the rarity colour rule.
7. `MaxEnvironmentalNPCSpawns` default and server tick time with +25 % / +50 % density on one player's loaded area.
8. SkyyZones noSpawn still removes the new spawns in towns (natural spawn = environment set - expected yes).
9. (optional) Better Mob Expansion 3.5 boots on 0.7.x (smoke with it on) - then Skyy decides whether to re-enable it.

## 8. OPEN QUESTIONS for Skyy (defaults in brackets)

1. How many more mobs? [Skeletons about 4x, other monsters about 1.5x, animals unchanged; a Server Setup row per zone to change it.]
2. Armour on mobs - you locked "no mob armour" on 2026-10-01. Armoured versions now? [Yes: armour you can SEE (vanilla sets of that
   zone's metal) + more Health / damage through the level system, no separate armour stat.]
3. The ladder and names: [three steps - normal, "Armored", "Veteran" (+ elites on top as today); mix 70/25/5 in easy biomes up to
   40/40/20 in the hardest; nameplate rarity colours white / yellow / pink, elites cyan.]
4. Rewards for the tougher versions: [XP follows their Health (x1.4 / x1.9, automatic); drop chances +25 % / +50 %; the armour they
   wear never drops.]
