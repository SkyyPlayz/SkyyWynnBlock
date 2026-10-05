# Mob Levels: Research + Plan (2026-09-30)

Skyy's request (2026-09-30, verbatim): "lets setup a mob level system too! check into other hytale mods to see how this is usually
handled. (i want mob levels to be set by the biome. easiest is where you spawn. the blue forest and other bioms in zone 1 have slightly
harder/higher level mobs. and zone 2 is a pretty big step up. (id rate the biomes in each zone by how rare they are. the higher the rarity
the higher the difficulty.). (just look into the mob leveling for now and get a plan. we can build it later.)"

Research and plan only. Nothing is built. Every number in section 4 and 5 is a PLACEHOLDER until Skyy picks.

---

## 0. The short version

- **Other Hytale mods** all do the same basic thing: when a mob spawns, give it a level from where it is. The level raises its health and
  damage, and puts `[Lv. N]` on its nameplate. The best match for Skyy's idea is **MmoMobScaling** (installed here). It uses the zone and biome
  of the mob's spawn chunk. We can mirror its engine calls step by step. Section 1 has the others.
- **Hytale already ranks its own biomes.** Every Hytale zone is split into three **regions** (Tier 1 / 2 / 3). Vanilla spawn files already
  sort every biome's mob list into those three danger tiers. The **blue forest is Hytale's `Forest_Azure`**. Its mob environment is
  `Env_Zone1_Azure`. It only exists in Zone 1's outer region, "The Fens" (Zone1_Tier3). Vanilla already gives it Tier-3 mobs: the big
  skeleton groups, Tier-3 night void mobs and piranhas.
- **Rarity measure:** a biome is rare if (a) it sits in a far region of the zone, and (b) inside that region it takes up little ground. We
  can read (b) from worldgen: each biome's `Weight` and `SizeModifier`. The engine code proves that a smaller SizeModifier makes a biome's
  patches **bigger**. We cannot read (a) from the files. Region sizes need an in-game survey command (plan step 1.4).
- **Proposed plan:** a new standalone mod, working name **SkyyMobs**. On spawn it reads the mob's biome, gives it a level from a table Skyy
  picks, scales its health and damage, and writes `[Lv 12] Skeleton Fighter` on the nameplate. SkyySkills combat XP already pays by
  the mob's max health, so XP goes up with level for free. SkyyGear drops and a level-gap XP rule plug in later.
- **Zone 2 is a big step:** the draft bands are Zone 1 = Lv 1-12, Zone 2 = Lv 15-28, Zone 3 = Lv 30-42, Zone 4 = Lv 45-60. They line
  up with the class weapon skill levels that gate gear.

---

## 1. How other Hytale mods do it

### 1.1 Installed here (read only, to learn - nothing copied)

| Mod | Where the level comes from | What scales | How it shows | Notes |
|---|---|---|---|---|
| **MmoMobScaling 1.1.0** (Ziggfreed) | A "difficulty" per **zone** and per **biome** of the spawn chunk. Files `Difficulty/Zone1_Tier1.json` etc. Zone1: T1=1, T2=2, T3=3. Zone2: 5 / 8 / 10. Zone3: 12 / 15 / 18. Zone4: 25 / 28. Plus a `Biome` layer (example: Ocean1 = 12). Also distance escalation (after 15,000 blocks, +1 per 500 blocks) and an optional nearby-player power delta. | HP +8% per point, outgoing damage +1% per point, damage taken -0.2% per point (capped). A 12% base chance to roll a rarity (the Rare tier from difficulty 5: HP x1.4, damage x1.45, loot x1.2, XP x1.1) and affixes. | Rewrites the mob's display name to "Rare <name>". Adds a zone-difficulty HUD and a look-at "inspector" HUD. | **Closest to Skyy's idea.** Deterministic: seed = world seed + mob UUID + role, so a reloaded mob gets the same result. Runs once per spawn, no per-tick cost. Engine calls in appendix A. |
| **EndlessLeveling 12.5** (Airijko) | Modes: `DISTANCE` (1 level per 100 blocks from spawn), `PLAYER_BASED` (nearby players' level -5..+10), `MIXED`, `FIXED`, `TIERED`. Per-world overrides. | HP +5% per level, damage +3% per level, defence curve, random variance x0.8-1.25 on each. | Nameplate with level, name and health, refreshed every 20 ticks. | XP cut outside +-20 levels (x0.25 below, x0.05 above; config). Blacklists passive mobs by keyword. A "settled mob fast-exit" optimisation shows the periodic nameplate refresh costs real performance. |
| **RPGLeveling 0.3.13** (Zuxaw) | `ZoneLevelConfig.json`: zone -> LevelMin..LevelMax (defaults Zone 1 = 1-25, Zone 2 = 25-50, Zone 3 = 50-75, Zone 4 = 75-100). Inside a zone, a **stronger species (more base HP) gets a higher level** (HP floor/ceiling mapping), +-5 random. Biome remap list per zone. | `Max HP = Base x (1 + Level x HP%/Lvl)` (2.63x at Lv 50 on Normal). Damage the same way (1.5x at Lv 50). Extra damage and resistance when the mob out-levels you. | Nameplate `Name [Lvl. N]`, via `Nameplate.setText`. HUD zone name coloured by level match. Warning when you walk into a too-high zone. | XP from mob level; heavy penalty far from your level. |
| **endless-elite-mobs 4.8.1** | Random elite chance on top of EndlessLeveling. | Elite classes, abilities, rarity tiers. | Tint effects. | Needs EndlessLeveling. |
| **PJ-Difficulty 1.2.5** | One server-wide multiplier, fixed or rising over time. | Mob HP and damage multipliers. | UI page. | Not location based. |

### 1.2 Other mods on CurseForge (web)

- **LevelingCore** (AzureDoom): six modes. `SPAWN_ONLY`, `NEARBY_PLAYERS_MEAN` (40-block radius, default), `BIOME` (csv biome -> level),
  `ZONE`, `INSTANCE`, and `ENVIRONMENT`. **ENVIRONMENT reads the environment id from the chunk at the mob's position.** Level variance
  option, fixed-level overrides, level on the nameplate.
- **RPGMobs**: five tiers (Common to Legendary). Styles: Environment/zone-based (Zone 1 mostly low tiers, Zone 4 mostly T4-T5), distance,
  or random. Tiered nameplates with rank and family prefix (uses the NameplateBuilder library). Bigger model per tier.
- **HyRPG**: each mob **type** has a level range, random level inside it. XP = 20 + 5 x level. Nameplate `[Level]` or `MobName [Level]`.
- **Endless Leveling (CurseForge page)**: "Players gain XP only from mobs within +-10 levels."

### 1.3 What they have in common (the lessons)

1. **Pick the level once, at spawn, from where the mob spawns.** Every mod does this. Skyy's "easiest is where you spawn" is the standard.
2. **Make it deterministic** (seed from the mob's UUID), so a mob that unloads and reloads keeps its level without saving anything.
3. **Scale HP and damage by a small percent per level.** Common values: HP +5 to +8% per level, damage +1 to +3% per level.
4. **Skip passive mobs** (livestock, critters, fish): keyword blacklist, or "default attitude to players is Hostile".
5. **Nameplate = plain text with the level.** Updating it every tick (health bars) is the main performance cost. Set it once instead.
6. **XP by level with a level-gap penalty** (Wynncraft -3% per level of difference; EndlessLeveling a +-10 or +-20 window).

---

## 2. Wynncraft and Hypixel SkyBlock (comparison)

| | Wynncraft | Hypixel SkyBlock |
|---|---|---|
| Level source | Fixed per mob type, placed by area. Areas have a suggested level (Ragni = 1, its mobs Lv 3-10; Detlas Suburbs Lv 7-17). | Fixed per mob type and spawn spot (Graveyard Zombie Lv 1, Pack Spirit Lv 30, Golden Ghoul Lv 60 ... Nessie Lv 302). |
| Shows as | Name + level + health bar over the mob. **Nameplate colour = mob type** (red hostile, green passive, yellow neutral, blue defending). | `[Lv1] Graveyard Zombie` + current/max health. |
| Scales | HP and damage by level. | HP and damage climb steeply (Lv 1: 100 HP / 20 dmg; Lv 30: 6,000 / 300; Lv 60: 45,000 / 800). Combat XP and coins by level (Scavenger accessory: 0.5 coins per mob level). |
| XP | -3% XP per level of difference (a Lv 15 player earns best on Lv 12-18 mobs). | Higher level = more Combat XP and loot. |

Take-away for SkyWynn: our zones play the role of Wynn's areas. Our biomes play the role of the spots inside an area. Hypixel-style `[Lv N]`
in front of the name reads best on a short Hytale nameplate.

---

## 3. Hytale's world (from Assets.zip, read only)

### 3.1 How the world is cut up

- **Zones** come from the world mask (`Server/World/Default/Mask.json` + `Mask/Climate/*.json`). Temperate = Zone 1, Hot = Zone 2,
  Cold = Zone 3, and the volcanic islands = Zone 4. Oceans sit between them.
- **Each zone has three regions** (the climate "Children" Tier 1 / 2 / 3). Their centres sit at different points on the temperature and
  intensity maps. **Tier 1 is the zone's core near spawn. Tier 3 is the outer edge and far corners.** Zone 4 has Tier 4 and Tier 5.
- **Each region has its own biome list** (`Zones/<Region>/Tile.*.json`). Tile biomes are laid out as a jittered grid of cells. Each cell
  picks a biome by `Weight`, and the biome's `SizeModifier` grows or shrinks its cells. `Custom.*.json` biomes (rivers, lakes, mountains,
  Trork camps, Kweebec villages, plateaus, dunes) are painted over the tile biomes by noise.
- **Mobs spawn by "environment"**, not by biome name. Each biome names an environment, for example Forest_Azure -> `Env_Zone1_Azure`.
  Each file in `Server/NPC/Spawn/World/*` lists environments + mobs + weights.

Region display names (server.lang): Zone1_Spawn "First Gate of the Echo", Zone1_Tier1 "Drifting Plains", Zone1_Tier2 "Seedling Woods",
Zone1_Tier3 "The Fens"; Zone2_Tier1 "Golden Steppes", Zone2_Tier2 "Badlands", Zone2_Tier3 "Desolate Basin"; Zone3_Tier1 "Frostmarch
Tundra", Tier2 "Boreal Reach", Tier3 "The Everfrost"; Zone4_Tier4 "Cinder Wastes", Tier5 "Charred Woodlands". Zones: Emerald Wilds,
Howling Sands, Whisperfrost Frontiers, Devastated Lands, Oceans ("Crystalline Depths").

### 3.2 Rarity: the method

The engine uses the biome's `Weight` to pick which biome each grid cell gets. When it works out which cell a block belongs to, it multiplies
the distance to each cell point by that cell's biome `SizeModifier`, and the nearest point wins. Proof: bytecode of
`BiomePatternGeneratorJsonLoader$LoadedPointGeneratorDistanceFunction.distance2D`, appendix A. So **a smaller SizeModifier = bigger
patches** (0.6 beats 1.0).

- **Cells %** = the biome's weight share in its region (how many patches it gets).
- **Area %** = estimated ground share = weight / SizeModifier^2, normalised. It is an estimate. The exact curve depends on the
  distance function; weight / SizeModifier gives similar ranks.
- **Rarity score** (proposal) = region tier first (a Tier 3 biome is rarer across the zone than any Tier 1 biome), then smaller
  Area % = rarer inside the region.
- **Region sizes are not in the files.** They come from temperature and intensity noise. An admin survey command (plan 1.4) can
  sample worldgen on a big grid. It gives the true zone-wide share of every region and biome in a few seconds.

Vanilla's own danger tiers match this. The spawn files sort environments into Tier 1 / 2 / 3: `Wander_Zone1_Tier1..3` skeleton groups,
`Void/Tier1..3_Night` void mobs, `Fish_Tier1..3`.

### 3.3 Zone 1 - Emerald Wilds (every biome)

| Region (vanilla tier) | Tile biome | Cells % | Area % (est.) | Environment -> vanilla mob tier | Rarity in zone (1 = most common) |
|---|---|---|---|---|---|
| Zone1_Spawn (unique small zone placed near the world origin) | Plains_Spawn | 100 | 100 | Env_Zone1_Plains -> T1 | 1 |
| Tier1 Drifting Plains | Plains_Smooth | 52.5 | 37.4 | Env_Zone1_Plains -> T1 | 2 |
| Tier1 | Plains_Birch | 21.6 | 15.4 | Env_Zone1_Plains -> T1 | 3 |
| Tier1 | Forest_Birch (SizeMod 0.5) | 12.9 | 23.6 | Env_Zone1_Forests -> **T2** | 4 |
| Tier1 | Forest_Flower (SizeMod 0.5) | 12.9 | 23.6 | Env_Zone1_Forests -> **T2** | 4 |
| Tier2 Seedling Woods | Plains_Gorge | 40.0 | 46.7 | Env_Zone1_Plains -> T1 | 5 |
| Tier2 | Plains_Tallgrass | 20.0 | 23.4 | Env_Zone1_Plains -> T1 | 6 |
| Tier2 | Forest_Aspen | 20.0 | 15.0 | Env_Zone1_Forests -> T2 | 7 |
| Tier2 | Forest_Gully | 20.0 | 15.0 | Env_Zone1_Forests -> T2 | 7 |
| Tier3 The Fens | Plains_Gorge | 33.3 | 32.3 | Env_Zone1_Plains -> T1 | 8 |
| Tier3 | **Forest_Azure = the blue forest** (SizeMod 0.6) | 16.7 | 28.7 | **Env_Zone1_Azure -> T3** | 9 |
| Tier3 | Forest_Swamp (SizeMod 0.75) | 16.7 | 18.4 | Env_Zone1_Swamps -> T3 | 10 |
| Tier3 | Forest_Autumn | 16.7 | 10.3 | Env_Zone1_Autumn -> T2 | 11 |
| Tier3 | Forest_Moss | 16.7 | 10.3 | Env_Zone1_Swamps -> T3 | 11 |

Overlays inside Zone 1 (custom biomes): mountains in every region (`Mountain_Tier1..3`, Env_Zone1_Mountains -> T2 list: goats, grizzly,
hawks); rivers (inherit the parent's environment); lakes (`Lake` inside Azure -> Env_Zone1_Forests, `Lake_Swamp`/`Lake_Moss` -> swamps,
`Lake_Chalk`); Trork camps (Env_Zone1_Trork) and Kweebec villages (Env_Zone1_Kweebec) in Tier 1-3; shores and shallow ocean
(Env_Zone1_Shores).

**The blue forest.** `Tile.Forest_Azure.json`: Azure trees, cyan crystals, slate pillars, teal grass tint (#2F798A / #2F868A), `Plant_Crop_Mana3`
covers, environment `Env_Zone1_Azure` (parent Env_Zone1). It only generates in Zone1_Tier3. Vanilla spawns there: boar, bunny, forest birds,
**grizzly + spider (day)**, **Tier-3 skeleton groups** (Skeleton_Fighter 3-4, Skeleton_Mage 2-3, Skeleton_Burnt_Praetorian 3), **Tier-3 night
void** (Larva, Crawler, Eye, Spawn, Spectre), piranha / black piranha / pike.

**Strict rarity note for Skyy.** Inside The Fens, the blue forest has big patches (SizeModifier 0.6). By ground area, Autumn and Moss forests
are about 3x rarer than it. Skyy asked for the blue forest to be harder, so the draft puts it at the top of Zone 1 (section 4). Strict rarity
would put Autumn / Moss above it. Skyy decides (question 2).

Zone 1 mobs by environment (day unless noted; the Wander skeletons spawn all day; void mobs spawn at night, weighted by moon phase):

| Environment | Hostile / fighting mobs | Passive |
|---|---|---|
| Plains (T1) | Wolf_Black packs (day + night), Skeleton_Fighter 1-2 | chicken, cow, pig, sheep, horse, deer, rabbit, fox, mosshorn, tetrabird, frogs, birds, mouse; fish minnow / bluegill |
| Forests, Autumn, Mountains (T2) | Bear_Grizzly, Spider (forests); Bear_Grizzly (mountains); Skeleton_Fighter 2-3, Skeleton_Burnt_Praetorian 3 | boar, bunny, goat, birds, squirrel, duck; trout / catfish |
| Azure, Swamps (T3) | Snake_Marsh, Fen_Stalker (swamps, day + night); grizzly + spider (Azure); skeleton groups incl. mages + praetorians | mosshorn, wild pig, turkey, raven, frogs; piranha / pike |
| Shores | crab | tropical fish, lobster |
| Caves (beacons, by region tier) | goblins (scrapper, lobber, miner, hermit), rats, cave spiders, magma toads, Golem_Firesteel (T2-T3 volcanic), mineshaft skeletons | bats, molerats, silk larvae, magma snails |

Base health already climbs by species (role `MaxHealth`): Skeleton_Fighter 36, Skeleton_Mage 49, Spider 61, Fen_Stalker 74, Wolf_Black 103,
Bear_Grizzly 124, Skeleton_Burnt_Praetorian 226.

### 3.4 Zone 2 - Howling Sands (every biome)

| Region | Tile biome | Cells % | Area % (est.) | Environment -> vanilla tier | Rarity in zone |
|---|---|---|---|---|---|
| Tier1 Golden Steppes | Savannah_Forest (0.65) | 20 | 25.5 | Env_Zone2_Savanna -> T1 | 1 |
| Tier1 | Savannah_Plains (0.65) | 20 | 25.5 | Savanna -> T1 | 1 |
| Tier1 | Savannah_Boab (0.75) | 20 | 19.1 | Savanna -> T1 | 3 |
| Tier1 | Savannah_Rock (0.75) | 20 | 19.1 | Savanna -> T1 | 3 |
| Tier1 | Scrub_Bushland (1.0) | 20 | 10.8 | **Env_Zone2_Scrub -> T2** | 5 |
| Tier2 Badlands | Desert_Oasis / Desert_Rock / Desert_Springs (0.75) | 25 each | 28.1 each | Env_Zone2_Deserts -> T3 | 6 |
| Tier2 | Desert_Red (1.0) | 25 | 15.8 | Deserts -> T3 | 7 |
| Tier3 Desolate Basin | Desert_Barren | 50 | 50 | Deserts -> T3 | 8 |
| Tier3 | Desert_Mushroom | 50 | 50 | Deserts -> T3 | 8 |

Overlays: plateaus over every tile biome (Env_Zone2_Plateaus -> T2); a hidden oasis over the deserts (`Desert_Oasis_Hidden`,
Env_Zone2_Oasis -> T3); dunes; tar pits (Env_Zone2_Scrub); hot springs; mudflats and river (savanna); shores with coral, palm beaches.

Zone 2 mobs: Savanna (T1): hyena packs, sabertooth tiger, sand-skeleton guard / assassin. Scrub + Plateaus (T2): vulture, hyena, scorpion,
rattlesnake, Scarak_Seeker, sand skeletons 2-3. Deserts + Oasis (T3): sabertooth, Cactee, Scarak_Seeker, crocodile (oasis), sand
guard / assassin / mage groups of 3, Tier-3 night void. Caves: cobras, scorpions, Scarak louse, goblins, magma toads, Firesteel golems.
Zone 2 species are already tougher (sand skeletons 61 HP vs 36, hyena 103, sabertooth / scorpion 124, crocodile 145).

### 3.5 Zone 3, Zone 4, Oceans (short)

- **Zone 3 Whisperfrost Frontiers.** T1 Frostmarch Tundra: Forest_Redwood (area 39%, has Kweebec villages), Forest_Fir 29, Plains_Shire 16,
  Forest_Tundra 11, **Plains_Hotsprings 6 (rarest)**. T2 Boreal Reach: Forest_Cedar 56, Plains_Frozen 18, Forest_Cedar_Mixed 16,
  Plains_Tundra 10. T3 The Everfrost: Forest_Frozen 32, Forest_Frozen_Light 32, Plains_Frozen_Frost 36, plus the Outlander village
  (Outlander berserkers and hunters). Mobs: cobras, grizzly, white wolf packs, polar bear, snow leopard, frost skeletons (scout -> fighter ->
  soldier / mage / knight), undead pigs.
- **Zone 4 Devastated Lands** (cells = area, all SizeModifier 1). T4 Cinder Wastes: Wastes_Grasslands 28, Wastes_Geysers 23, Forest_Ghost 21,
  Desert_Dunes 14, Forest_Swamp 14 (+ ghost towns / villages, calderas, canyons). T5 Charred Woodlands: Desert_Ash 25, Wastes_Ash 25,
  Wastes_Lava 25 (volcano), Forest_Burned 12.5, Forest_Roots 12.5.
- **Oceans**: 13 tile biomes (cold / temperate / tropical x barren / kelp / reef / sandy + tropical tubes), weight 10 each; islands, trenches,
  sunken cities as overlays.

---

## 4. Proposed level plan (PLACEHOLDERS - Skyy picks)

**Scale:** Lv 1-60. It matches the SkyySkills class weapon skill (the gear level gate; Hypixel table to 60). Zone bands leave a gap at each
zone step, so "zone 2 is a pretty big step up":

| Zone | Band | Region -> sub-band |
|---|---|---|
| Zone 1 Emerald Wilds | **1-12** | Spawn 1-2 - Tier1 1-5 - Tier2 4-9 - Tier3 7-12 |
| Zone 2 Howling Sands | **15-28** | Tier1 15-19 - Tier2 19-24 - Tier3 24-28 |
| Zone 3 Whisperfrost | **30-42** | Tier1 30-34 - Tier2 34-38 - Tier3 38-42 |
| Zone 4 Devastated Lands | **45-60** | Tier4 45-52 - Tier5 52-60 |
| Oceans / shores | nearest zone region's band | - |

Biome bands inside Zone 1 and Zone 2 follow the rarity order from 3.3 / 3.4. Each mob rolls a level inside its biome band. The roll is
seeded by the mob's UUID, so it keeps its level after a reload.

| Zone 1 biome | Level | Zone 2 biome | Level |
|---|---|---|---|
| Plains_Spawn | 1-2 | Savannah_Forest / Savannah_Plains | 15-17 |
| Plains_Smooth | 1-3 | Savannah_Boab / Savannah_Rock | 16-18 |
| Plains_Birch | 2-4 | Scrub_Bushland | 17-19 |
| Forest_Birch / Forest_Flower | 3-5 | Plateaus (overlay, any region) | region band +1 |
| Plains_Gorge (Tier 2) | 4-6 | Desert_Oasis / Rock / Springs | 19-22 |
| Plains_Tallgrass | 5-7 | Desert_Red | 21-23 |
| Forest_Aspen / Forest_Gully | 6-8 | Hidden oasis (overlay) | 22-24 |
| Mountains (overlay) | region band top | Desert_Barren | 24-26 |
| Plains_Gorge (Tier 3) | 7-9 | Desert_Mushroom | 25-28 |
| Forest_Swamp | 8-10 | | |
| Forest_Autumn / Forest_Moss | 9-11 | | |
| **Forest_Azure (blue forest)** | **10-12** | | |

Optional twists (from other mods, each is a question for Skyy):
- **Species inside the band** (RPGLeveling): a stronger species rolls in the top half of the band (a Praetorian at the top, a Larva at the
  bottom).
- **Night void mobs**: same band as the biome, or +1 or +2 at night.
- **Flock leader** +1.

---

## 5. What scales (proposal, numbers open)

| Thing | Proposal | Where it comes from |
|---|---|---|
| Max health | x (1 + 0.06 x (Lv - 1)): Lv 12 = 1.66x, Lv 28 = 2.62x, Lv 60 = 4.54x (on top of the species' own base) | EndlessLeveling 5%, MmoMobScaling 8%, RPGLeveling ~3.3% |
| Damage dealt | x (1 + 0.03 x (Lv - 1)): Lv 12 = 1.33x, Lv 60 = 2.77x. Player armour and SkyyGear Defense still apply after it | EndlessLeveling 3% |
| Damage taken | off at first. Later: an under-levelled player deals less damage (RPGLeveling gap defence) | RPGLeveling |
| Combat XP | **free**: SkyySkills already pays NPC max health x 0.2 (clamped 1-500), so the health scaling raises XP. Later: Wynn-style level-gap penalty through a bridge key | SkyySkills 0.4.8 KillSys |
| Drops | later: an extra roll of the mob's own drop list at some chance per level; SkyyGear `odds.mob` shifted by level; coins per mob level (the SkyBlock Scavenger idea) | MmoMobScaling loot pulls, Hypixel |
| Elites / rarity | later, separate: a small chance for a "Rare" or "Elite" mob with a bigger multiplier (MmoMobScaling rarities, endless-elite-mobs) | - |

---

## 6. How the level shows

- **Nameplate text**, set once at spawn: `[Lv 12] Skeleton Fighter` (SkyBlock style, draft) or `Skeleton Fighter Lv. 12` (Wynn style).
  Vanilla hostile mobs have no nameplate at all (only merchants set display names). So this adds one, like the vanilla
  `/entity nameplate` command does.
- **Colour:** the Nameplate component only holds a plain String. Whether the client shows colour markup is **UNVERIFIED**. Test it with the
  vanilla `/entity nameplate <text>` command before building. A nameplate is the same for every viewer, so "red if the mob out-levels
  you" per player is not possible on it.
- **Health on the nameplate: no.** It needs a periodic nameplate refresh, which is EndlessLeveling's hot path and against our "no periodic
  updates" rule.
- The mob name comes from `server.lang` (`npcRoles.Skeleton_Fighter.name = Skeleton Fighter`). If the lookup fails, use the role id with
  spaces.
- Optional later: the zone / region name and its level band in the SkyyHud location line (SkyyExploration already reads the current zone).

---

## 7. Build plan (for later)

New standalone mod **SkyyMobs** (name TBD; zero dependencies; version first in the display name).

**Stage 1 - levels (SkyyMobs 0.1)**
1. `LevelHook` (HolderSystem on NPCEntity + EntityStatMap, AFTER RoleBuilderSystem and EntityStatsSystems$Setup; add reasons SPAWN and
   LOAD). Skip non-hostile NPCs (vanilla attitude + an exclude list). Work out the level key in this order:
   (a) the mob's **spawn environment** `NPCEntity.getEnvironment()` (world spawns; saved with the mob);
   (b) the environment of the block at the mob's **spawn point** (leash point) (caves, beacons, markers);
   (c) the classic-worldgen **region + tile biome** at the spawn point (`getZoneBiomeResultAt`);
   (d) the per-world default band.
   Then roll the level inside the band, with a seed from the world seed + mob UUID + role. Put the HP modifier on the mob (MULTIPLICATIVE
   on MAX, fixed key). Set the nameplate. Keep the level in memory by entity UUID (removed in `onEntityRemoved`).
   (a) and (b) matter because the island chain is hand-built on the server, and SkyyWorldGen uses World Gen 2. Neither has the classic
   zone lookup, but both have environments. Vanilla spawns and LevelingCore's ENVIRONMENT mode use them too.
2. `LevelDamage` (DamageEventSystem in the Filter group, BEFORE DamageSystems$ArmorDamageReduction): damage from a levelled mob x its
   damage multiplier. The same slot SkyyGear's GearHitSys uses.
3. Config: the band tables (region, biome and environment -> band), the HP and damage curves, the exclude list, and the nameplate format.
   All rows go in Server Setup through `tools/skyycfg.py`.
4. Commands: `/mobs` (player: the level band of the region you stand in). Admin sub-commands `/mobs survey` (samples worldgen over a large
   grid; prints each region's and biome's real zone-wide share, the missing rarity numbers) and `/mobs reload`.
5. Bridge (java.lang only): `mob:fn:level` = Function(Object[]{String world, UUID npc}) -> Integer (-1 if not levelled).

**Stage 2 - rewards:** SkyySkills reads `mob:fn:level` for the level-gap XP rule. SkyyGear shifts `odds.mob` by level. Bonus drop rolls and
coins per level.
**Stage 3:** elites / rarities, and per-island bands for the hand-built chain worlds (painted environments or admin areas).

Rules that apply when it is built: one registerSystem per class, world thread for components and stats, command permission groups,
javassist limits (the Supplier / Component classes must be top-level classes; no lambdas).

---

## 8. Questions for Skyy

1. **Scale and bands:** Lv 1-60 with Zone 1 = 1-12, Zone 2 = 15-28, Zone 3 = 30-42, Zone 4 = 45-60? Or bigger numbers (SkyBlock-style
   hundreds)?
2. **Blue forest vs strict rarity:** Forest_Azure at the top of Zone 1 (your call, draft), or the rarest ground first (Autumn / Moss above
   Azure)?
3. **Which mobs get levels:** hostile only (draft), or also neutral fighters (boar, Scarak, Feran)? Passive animals never?
4. **Numbers:** HP +6% and damage +3% per level (draft)? Should an under-levelled player also deal less damage?
5. **XP:** is "more HP = more XP" enough for now, or add a level-gap penalty (Wynn -3% per level of difference)?
6. **Drops:** more drops and better gear odds on higher levels (stage 2)?
7. **Night / void mobs:** same level as the biome, or a night bonus?
8. **Nameplate format:** `[Lv 12] Skeleton Fighter` or `Skeleton Fighter Lv. 12`? (Colour depends on the in-game test in section 6.)
9. **Level spread:** random inside the biome band (draft), or stronger species higher (RPGLeveling style)?
10. **Hand-built islands:** set levels by painted environments, or one band per island / area?
11. **Mod name:** SkyyMobs?

---

## Appendix A: engine facts (HytaleServer.jar release + installed mods, bytecode)

Checked with tools/dev/reflect.py, bc.py, bcfull.py, bcfull2.py, callers.py, cpstrings (constant pools). MmoMobScaling and ZiggfreedCommon
were dumped read-only with a javassist lister in scratch.

**Where the mob spawned**
- `NPCEntity.getEnvironment()` / `getSpawnConfiguration()`: `WorldSpawnJobSystems.preAddToWorld` sets them from
  `SpawnJobData.getEnvironmentIndex()` / `getSpawnConfigIndex()`. It is the TriConsumer that `NPCPlugin.spawnEntity` calls (offset 261)
  **before** `Store.addEntity(holder, AddReason)` (offset 272). So a HolderSystem `onEntityAdd` already sees the value. It is
  `Integer.MIN_VALUE` for NPCs that did not come from a world spawn job (`SpawnStatsCommand` checks for that). Flock members go through the
  same callback (`FlockPlugin.trySpawnFlock`). The NPCEntity codec has the key `"Env"`, so it is saved with the mob. VERIFIED (round-trip
  after a reload is UNVERIFIED).
- Environment id: `Environment.getAssetMap()` (IndexedLookupTableAssetMap) `.getAsset(index).getId()` -> e.g. `Env_Zone1_Azure`. The asset
  also has `getSpawnDensity()`. VERIFIED (reflection).
- Block environment at a position (engine recipe `EnvironmentCondition.eval0`): `world.getChunkStore().getChunkReference(
  ChunkUtil.indexChunkFromBlock(x, z))` -> `chunkStore.getStore().getComponent(ref, BlockChunk.getComponentType())` ->
  `BlockChunk.getEnvironment(Vector3d)` (3D, so caves get their cave environment). VERIFIED.
- Spawn point: `NPCPlugin.spawnEntity` calls `npc.saveLeashInformation(position, rotation)` (offset 46). The codec key `"LeashPos"`.
  `NPCEntity.getLeashPoint()`. The only other writers are `NPCSpawnCommand` and the role action `ActionSetLeashPosition` (a role can move it:
  caveat). VERIFIED.
- Worldgen zone / biome (engine recipe `NPCMemory$GatherMemoriesSystem.findLocationZoneName`):
  `world.getChunkStore().getGenerator()` instanceof `server.worldgen.chunk.ChunkGenerator` ->
  `getZoneBiomeResultAt((int) world.getWorldConfig().getSeed(), floor(x), floor(z))` ->
  `.getZoneResult().getZone().name()` (e.g. `Zone1_Tier3`) and `.getBiome().getName()`. It is cached (`ChunkGeneratorCache`). Void, Flat,
  instance and World Gen 2 worlds are not a ChunkGenerator, so there is no zone. MmoMobScaling does the same, queried at the chunk centre.
  VERIFIED.
- `BiomePatternGenerator.generateBiomeAt` returns the custom biome if one applies, else the tile biome (VERIFIED). That
  `ZoneBiomeResult.getBiome()` holds that value is UNVERIFIED. The tile biome underneath: `zone.biomePatternGenerator().getBiome(int, int,
  int)` exists (the argument order seed, x, z is UNVERIFIED). `ZoneGeneratorResult.getBorderDistance()` exists (distance to the region edge;
  it could grade levels deeper into a region).
- Biome size: `LoadedPointGeneratorDistanceFunction.distance2D(IIIDDDD)` returns `distanceFunction.distance2D(...) *
  sizeModifierProvider.get(seed, cellX, cellY)` = the cell biome's `TileBiome.getSizeModifier()`. `BiomePatternGenerator.getBiomeIndex` uses
  `IPointGenerator.nearest2D`. Weight: `ZoneBiomesJsonLoader` -> `TileBiome.getWeight()` -> IWeightedMap. VERIFIED. The area formula in 3.2
  is an estimate.

**Hooking the spawn (MmoMobScaling `MobScalingSpawnHook`, working mod)**
- `extends HolderSystem`; query `Archetype.of(NPCEntity.getComponentType(), EntityStatMap.getComponentType())`; dependencies
  `new SystemDependency(Order.AFTER, RoleBuilderSystem.class)` + `(Order.AFTER, EntityStatsSystems$Setup.class)`;
  `onEntityAdd(Holder, AddReason, Store)` (AddReason = SPAWN or LOAD) and `onEntityRemoved(Holder, RemoveReason, Store)`. World from
  `((EntityStore) store.getExternalData()).getWorld()`. Position from `holder.getComponent(TransformComponent.getComponentType())
  .getPosition()`. Seed: world seed mixed with `UUIDComponent.getUuid()` + role name hash + role index. VERIFIED (bytecode).
- Its per-mob data is a non-saved component: `getEntityStoreRegistry().registerComponent(Class, Supplier)` (ScaledMobComponent). No Skyy mod
  has registered a component yet, so javassist support is UNVERIFIED. The fallback is a static concurrent map by UUID.
- Hostile check (MmoMobScaling `MobClassifier`): `holder.getComponent(WorldSupport.getComponentType()).getDefaultPlayerAttitude() ==
  Attitude.HOSTILE` (Attitude: IGNORE, HOSTILE, NEUTRAL, FRIENDLY, REVERED). VERIFIED.

**Scaling max health** (ZiggfreedCommon `HealthUtil.scaleMaxHealth` / `reconcileOnMap`)
- `EntityStatMap m = holder.getComponent(EntityStatsModule.get().getEntityStatMapComponentType())`;
  `m.putModifier(DefaultEntityStatTypes.getHealth(), "<key>", new StaticModifier(Modifier$ModifierTarget.MAX,
  StaticModifier$CalculationType.MULTIPLICATIVE, mult))`; `m.maximizeStatValue(DefaultEntityStatTypes.getHealth())`. Reconcile =
  `getModifier` / `removeModifier` if the amount changed. A fixed key makes a re-apply on LOAD harmless. VERIFIED (bytecode + reflection).
  UNVERIFIED: whether to maximize on LOAD (it would heal a wounded mob on reload).

**Scaling mob damage** (MmoMobScaling `MobScalingDamageFilter`)
- `extends DamageEventSystem`; `getGroup()` = `DamageModule.get().getFilterDamageGroup()`; dependency `Order.BEFORE
  DamageSystems$ArmorDamageReduction`; `handle(int, ArchetypeChunk, Store, CommandBuffer, Damage)`: `damage.getSource()` instanceof
  `Damage$EntitySource` -> `getRef()` = the attacker -> the attacker's multiplier -> `damage.setAmount(damage.getAmount() * mult)`. SkyyGear
  0.1.1 GearHitSys / GearArmorSys sit in the same group (before / after armour). VERIFIED.

**Nameplate**
- `server.core.entity.nameplate.Nameplate` (Component, `getText` / `setText(String)`, BuilderCodec; synced by
  `NameplateSystems$EntityTrackerUpdate` via `consumeNetworkOutdated`). Engine recipe `DisplayNameSupport.setDisplayName(Holder, String,
  boolean)`: `holder.ensureAndGetComponent(Nameplate.getComponentType())` -> `setText(name)`. It also puts
  `PersistentDisplayName(Message)` + `DisplayNameComponent(Message)`. `/entity nameplate` does `store.ensureAndGetComponent(ref,
  Nameplate type).setText`. RPGLeveling does the same (`"[Lvl. N]"`). VERIFIED.
- The kill feed and death messages read `DisplayNameComponent` (`Damage$EntitySource.getDeathMessage`, `PlayerSystems$KillFeed*`).
  MmoMobScaling rewrites it with a decorated `Message`. Optional for us.
- Vanilla hostile roles set no `DisplayNames` (only merchants, quest master and tests), so they get no nameplate by default (files
  VERIFIED; in-game look UNVERIFIED). Colour markup in nameplate text: UNVERIFIED.
- Names: server.lang `npcRoles.<Role>.name`. The role's parameter holds `server.npcRoles.<Role>.name`. `I18nModule.get().getMessage(String,
  String)` exists (argument order UNVERIFIED; `getMessages(String)` returns a Map).

**Kills, XP, drops**
- Kill credit: `DeathComponent.getDeathInfo().getSource()` instanceof `Damage$EntitySource` -> `getRef()` -> PlayerRef (SkyySkills 0.4.8
  KillSys = `DeathSystems.OnDeathSystem.onComponentAdded`; MmoMobScaling `resolveKillerRef`). VERIFIED.
- SkyySkills combat XP = `EntityStatValue.getMax()` of health x `combat.perHealth` 0.2, clamped `combat.min` 1..`combat.max` 500,
  `combat.role.<Role>` overrides. So the HP modifier raises XP (that getMax includes the MAX modifier is implied by maximizeStatValue:
  UNVERIFIED). Zone 4 mobs may need `combat.max` raised.
- Vanilla drops (`NPCDamageSystems$DropDeathItems.tick`): `Role.getDropListId()` -> `ItemModule.get().getRandomItemDrops(id)` (List of
  ItemStack) -> `ItemComponent.generateItemDrops(accessor, list, position (+ offset), rotation)` -> `commandBuffer.addEntities(holders,
  AddReason.SPAWN)`. An extra roll = the same calls (MmoMobScaling `MobScalingLootDropSystem`: EntityTickingSystem on DeathComponent,
  AFTER `DeathSystems$TickCorpseRemoval`, BEFORE `DeathSystems$CorpseRemoval`). VERIFIED.
- SkyyGear 0.1.1 GearDeathMark / GearDropSys tag undocumented gear that spawns within 2 blocks of a dying NPC in the same tick as
  unidentified. Bonus drops spawned the same way should be tagged too (UNVERIFIED).

**Performance**
- The level work is once per NPC add (spawn or chunk load). The worldgen lookup is cached by the engine. The environment lookup is an
  array read. The damage filter is one map lookup per hit. There is no ticking system and no periodic nameplate update.

## Appendix B: data sources in Assets.zip

`Server/World/Default/Zones.json` (MaskMapping colours -> region folders), `Mask.json` + `Mask/Climate/{Temperate,Hot,Cold}.json` (zones and
tier points), `Zones/<Region>/Zone.json` (Discovery name, biome grid), `Tile.*.json` (Weight, SizeModifier, Environment), `Custom.*.json`
(BiomeMask, Priority, noise threshold), `Server/Environments/Zone*/Env_*.json` (SpawnDensity, parent), `Server/NPC/Spawn/World/*` +
`Beacons/*` (environment -> mobs), `Server/NPC/Roles/**` (MaxHealth, DropList, attitude), `Server/Languages/en-US/server.lang` (names).
Some Zone 4 files use comments / trailing commas (a lenient parse is needed).

## Sources

Installed mods (read only): MmoMobScaling-1.1.0.jar, ZiggfreedCommon-2.0.0.jar, EndlessLeveling.jar, RPGLeveling-0.3.13.jar,
endless-elite-mobs-4.8.1.jar, PJ-Difficulty-1.2.5.jar in `C:\Users\SkyLo\AppData\Roaming\Hytale\UserData\Mods`.

Web:
- https://www.curseforge.com/hytale/mods/rpg-leveling-and-stats
- https://docs.rpg-leveling.zuxaw.com/config-zones and https://docs.rpg-leveling.zuxaw.com/difficulty-scaling
- https://www.curseforge.com/hytale/mods/levelingcore and https://github.com/AzureDoom/LevelingCore/wiki/Mob-Leveling-Modes
- https://www.curseforge.com/hytale/mods/rpgmobs
- https://www.curseforge.com/hytale/mods/hyrpg
- https://www.curseforge.com/hytale/mods/endlessleveling
- https://www.curseforge.com/hytale/mods/endless-elite-mobs
- https://www.curseforge.com/hytale/mods/hydifficulty
- https://wynncraft.wiki.gg/wiki/Experience_Points, https://wynncraft.wiki.gg/wiki/Mobs,
  https://wynncraft.wiki.gg/wiki/Lists_of_mobs/Detlas_Suburbs, https://wynncraft.fandom.com/wiki/Lists_of_mobs/Ragni_Region,
  https://wynncraft.fandom.com/wiki/Mobs
- https://hypixelskyblock.minecraft.wiki/w/Mobs

Our own: HANDOFF.md, docs/plans/SkyWynn-Decisions.md (zone island chain, SkyyWorldGen), OPEN-QUESTIONS.md (2026-09-30 request),
research/Exploration-Research.md (zone discovery engine names), SkyySkills/build_skyyskills_0.4.8.py (KillSys), SkyyGear/build_skyygear_0.1.1.py
(GearDeathMark, GearHitSys).
