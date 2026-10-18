# Per-player chest loot - survey (2026-10-18)

Skyy: "this one adds the per player loot to the chests i was talking about!" (ReLootChest) + "i want the normal vanilla chests to have per
player loot, that works on every profile, so you get to find and loot all the chests in the world again on every profile." + "we need to make
sure we update the loot tables so it drops our like gear unidentified and things like that." (docs/answered/project.md, last two lines).
Method: the three jars in Skyy's Mods folder were copied to scratch and read (manifest, class strings; no javap here, so no method bodies),
plus the CurseForge pages. Anything not read from code is marked UNVERIFIED.

## 1. The three mods

| | ReLootChest 1.0 | Lootr 0.3.12 | Loot4Everyone 1.3.9 |
|---|---|---|---|
| Author | Ender_Griefeur99 | Noobanidus (github.com/LootrMinecraft/LootrHytale) | MimStar (github.com/MimStar/Loot4Everyone-Hytale) |
| **Licence** | **All Rights Reserved** (CurseForge) - cannot pack or fold | **MIT** (CurseForge + Licence-Audit) | **MIT** (CurseForge) |
| ServerVersion | `*` | `>=0.6.2` | `0.6.0` (UNVERIFIED how the engine reads it; check the server log for a version warning). Other pack mods: mostly `*`, `>=0.7.0 <0.8.0`, `0.7.0` |
| Blocks | vanilla chests, no new blocks | **custom block** `Noobanidus_Lootr_LootChest` (own model + sparkles); worldgen chests are converted when their block entity is added, BlockSpawner picks are swapped before they spawn | vanilla chests stay vanilla; a chest is registered as a "loot chest" (template resource) |
| Saved per | player UUID, per chest position (JSON in `playerdata/`, contents + `lastLootMillis`) | player UUID set kept on the chest block (`PlayerContainers`) | `PlayerLoot` component on the player (UUID), per chest, plus a world-level template per chest |
| Map vs player-placed | `PlayerPlaced` flag set by a PlaceBlock system; flagged chests stay vanilla | only worldgen / spawner chests (or `/lootr custom x y z`); min capacity 2 | PlaceBlock listener keeps player-placed out; new chunks automatic, old chests via `/generatelc` |
| Later worldgen chests | yes (any unflagged chest) | yes for new chunks; **not retroactive** (page says so) | yes for new chunks; old via `/generatelc` |
| Refill / reset | none (once emptied it stays done) | none | **yes**: `/setautoresetlc` (days/hours/min/sec), `/resetlc` (one or all players) |
| Commands | none | `/lootr custom` (permission group typed `hyale:WorldEditor` - a typo in the jar, UNVERIFIED effect) | `/lootconfig` (UI page), `/generatelc`, `/editlc`, `/deletelc`, `/resetlc`, `/setautoresetlc`, `/setbreakrule`, `/setmessagerule`, `/setparticlerule`, `/setrandomrule`. No clash with any Skyy command (grepped builds) |
| Extras | "already looted" message | sparkles on unopened chests, break rules, config (Disable_Break, Minimum_Capacity, Disable_Conversion) | UI config page, random loot per player (re-rolls the droplist), discovery message/sound/particles, griefing protection, can build a chest from a droplist |
| Per PROFILE? | **No** (UUID only) | **No** (UUID only) | **No** (UUID only) |

None of the three has a profile key, a config for it, an API or an event we could hook for it. All three key by player UUID, so a new
profile would still see chests the same account already opened - the opposite of what Skyy wants. `profile:fn:key` (PROFILES-CONTRACT)
would have to be called inside their code.

## 2. How vanilla fills chests (Assets.zip read-only + our own research)

- World chests get a **drop list on the block entity** from BlockSpawner tables / prefabs. `StashPlugin$StashSystem` rolls that list into
  the container the moment the block entity is added to the chunk (`getRandomItemDrops(droplist)`, slots shuffled with a Random seeded
  from x,y,z), then clears the list (`StashGameplayConfig.isClearContainerDropList`, default true). It is **not** rolled at open time
  (research/Exploration-Build-Spec.md). Loot4Everyone overrides that stash config at world start (`StartWorldEventListener`).
- Droplist files: `Server/Drops/Prefabs/` has 64 files named `Zone<1-4>_<Encounters|Goblin|Kweebec|Trork|Undead|Outlander|Feran>_Tier<n>`
  plus `Portals_Goblin_Chest_*`, `Coffer_Goblin_Loot_Wave1-5`, `Portals_Hollows_Ancient_Chest`; `Server/Drops/Items/Container_*` (coffins,
  pots, wardrobes); `Server/Drops/Objectives/Trork_Camp_Chest`. A sample (Portals_Goblin_Chest_Tier2) is Scraps plus a 5 % weighted choice
  of a plain weapon id. Entries are plain item ids: **no metadata, so no level or rarity can be written in a droplist**.
- Our code already hooks this. SkyyGear `GearChestMark` (BEFORE) / `GearChestTag` (AFTER StashSystem) turn gear a fresh chest rolled into
  unidentified bags at the chest's zone level (`mob:fn:levelAt`, else the `Zone<N>` band of the list name) and add one extra bag
  (`loot.chest.chance` 33 %); the first open of prefab chests tags the rest. SkyyExploration `ChestReg` records every world loot chest
  (drop list present at add time = map chest; `PlacedByInteraction` = player-placed) and the first open **per profile** (XP; chest luck =
  one extra roll of the list into the opener's inventory). Neither runs on SkyyIslands worlds. SkyyQuests pays `gear:*` bag reward words.
  SkyyBazaar has no chest source (only ids/levels). The SkyyIslands starter chest is a one-off kit chest, not a world loot chest: it must
  stay out of any per-player system.

## 3. Clash with OUR chest loot

- Per-player copies **multiply our bags by design** (each profile rolls its own, bags included; 8 profiles = 8x). Intended ("find and loot
  all the chests again on every profile") but it is an economy change: flag to Skyy.
- A mod that copies the chest's CURRENT items (ReLootChest, Loot4 template) would copy stacks GearChestTag already turned into bags: the
  same item documents (same level/rarity) cloned for everyone. That is a duplication risk (PROJECT-RULES: full round). Re-rolling from the
  DROP LIST per profile is safe; copying item documents is not.
- Lootr's custom block changes the block id our `ChestReg` / `GearChestMark` expect (UNVERIFIED whether the drop list survives its
  conversion): first-open XP and the extra bag could silently stop. ReLootChest and Loot4 keep vanilla blocks: no such clash.
- Nothing of ours does per-player chests today, so no duplicate-mod issue inside our own set.

## 4. Recommendation

**Fold, do not pack.** ReLootChest cannot be redistributed (All Rights Reserved). Lootr and Loot4 are MIT but cannot key by profile, and
Lootr's custom block fights our chest hooks. Packing any one as-is gives the OPPOSITE of the must-have (same loot on every profile).
Once ours is in, none of the three stays in the pack / test set (no duplicates).

Build it in **SkyyExploration** (it already owns `ChestReg`, the map-vs-placed rule, first open per profile through `pkey`, chest luck and
the first-open window). Fresh code; ideas borrowed (MIT allows code too; credit in PACK.md):
- from **Loot4Everyone**: keep the vanilla block (no new item to dupe), the PlaceBlock "player-placed stays normal" check, reset timers +
  admin reset (Server Setup rows), message/particles for chests not yet opened;
- from **Lootr**: hook at block-entity add (we already do, BEFORE StashSystem), skip tiny containers, break rules (no contents dropped),
  unopened sparkles; its `/lootr custom` = our admin "make this a loot chest" (`/stash set`);
- from **ReLootChest**: the small shape - per-player map keyed by chest position, `PlayerPlaced` flag, one config line.
What we lose from the others: Loot4's UI page and ten commands (Server Setup replaces them), its random-per-player toggle (we re-roll from
the list anyway); Lootr's chest model and sparkles unless we add particles; ReLootChest nothing.

### How it works (proposal)
1. A world loot chest = a container that had a drop list at add time (ChestReg keeps the list name today).
2. First open by a profile (`pkey`): roll the registered drop list fresh, seeded by (pkey, world, x,y,z), run it through GearChestTag
   (bags at the chest's zone level + the 33 % extra bag), save the leftovers per profile in the existing `players/<pkey>` data. Later opens
   by that profile show its saved leftovers; a fully looted chest is empty for that profile only.
3. Another profile (even the same account) gets its own fresh roll. Refill timer optional (default off).
4. Never on island worlds, player-placed chests, or the SkyyIslands starter chest.
5. The shared physical container stays empty after the first fill, so no one sees the first opener's loot.
UNVERIFIED: opening a swapped container without client desync. ReLootChest does it with its own GUI session (`ReLootGuiService`,
`ReLootChestWindowTickSystem`), Loot4 with `OpenedContainerComponent` + `ContainerMonitoringSystem`: read those two when building.

## 5. Loot tables: our gear in chests

- **A (recommended): runtime, at the per-profile roll.** Droplists cannot carry levels or rarity, so unidentified bags must be created in
  code anyway. Reuse what exists: `gear:fn:box` / GearChestTag for bags (zone level from `mob:fn:levelAt`, tier from the list name's
  `Zone<N>_..._Tier<n>` and the tier ladder), `gear:fn:grant` for fixed items, Exploration's Unclaimed Luggage tiers. Odds stay in the
  existing `loot.chest.*` Server Setup rows (add per-zone rows if wanted).
- **B (optional): build-time asset overlay** of the Zone1-4 `*_Tier*` lists, generated INTO the jar from Assets.zip at build time (never
  committed, PROJECT-RULES 2), only for metadata-free items (materials, Enchanted ingredients, plain weapon ids that GearChestTag then
  bags). Cost: a vanilla patch can move those files, and Portals / Coffer lists also feed dungeons we do not want to double-buff.

## Questions for Skyy (defaults in brackets)
1. Fold per-profile chests into SkyyExploration and leave all three mods out of the pack / test set? [yes; remove ReLootChest, Lootr, Loot4Everyone from the Mods folder at the deploy]
2. Each profile gets a fresh roll including a fresh extra bag (8 profiles = 8x chest loot)? [yes, as asked]
3. Chests refill over time? [off; admin timer in Server Setup, default none]
4. Sparkles / sound for chests this profile has not opened yet? [sparkles on, like Lootr]
5. Chest contents: A only, or A plus the build-time overlay B for materials? [A only for now]
6. Chests opened before this ships count as unopened on every profile? [yes, everyone can loot them once more]
