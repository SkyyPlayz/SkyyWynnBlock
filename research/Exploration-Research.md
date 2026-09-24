# Exploration skill: research and options

*For Skyy. Written 2026-09-23. This is research plus options, not a decision: **Skyy picks the rewards.***

Tags: **VERIFIED** = seen in a source, the game jar, the game assets or our code. **UNVERIFIED** = reported but not confirmed, or sources disagree.
Hytale feasibility tags: **VERIFIED hook** (the engine piece exists and we know how to use it) / **needs a test** (the pieces exist, but we haven't proven them in game) / **not possible**.

**In one breath:** SkyBlock has no Exploration skill. It pays for exploring with scattered side systems (Fairy Souls, warps, coin hunts). Wynncraft treats exploring as its biggest XP source (Discoveries plus Caves). Hytale already has a built-in "you discovered a zone" banner we can listen to. It only works on generated worlds, though, so SkyWynn's hand-built island chain will need its own list of discovery spots.

---

## 1. What Hypixel SkyBlock gives for exploring

| Feature | What you do | What you get | Tag |
|---|---|---|---|
| Fairy Souls | Find 289 hidden souls spread over every island. Hand them in 5 at a time to Tia the Fairy | +10 SkyBlock XP per batch of 5, plus a permanent backpack slot at 17 set batches. They used to give stats. That ended when SkyBlock Levels came in | VERIFIED |
| Area achievements (e.g. "Explorer") | Discover every area of the main island, or reach certain secret spots | Achievement points only (cosmetic lobby unlocks). No power | VERIFIED |
| Fast travel / Travel Scrolls | Use a scroll item, or for some places just visit once (Crystal Hollows unlocks on the first visit) | A permanent warp in the Fast Travel menu and `/warp` | VERIFIED |
| Spider's Den Relics | Find 28 relics in one zone. The Archaeologist gives you a compass that points to the nearest one | 10,000 coins each, +30,000 for all of them. A "rare relics" side quest was removed | VERIFIED |
| Rift Enigma Souls | Collect orbs in the Rift dimension. Hand them in 4 at a time | Every batch upgrades one cloak (+2 Speed, +4 Mana Regen) and gives Motes (the Rift's currency) | VERIFIED; total count UNVERIFIED (one page says 40, another source says 52) |
| Crystal Hollows / Glacite Mineshafts | Explore random mining caves, bring 5 crystals to the center, loot corpses in mineshafts | A big loot bundle, mining-tree XP and powder. Rare drops have a pity meter | VERIFIED (exact drop odds UNVERIFIED) |
| Hoppity's Hunt (seasonal) | Find eggs that spawn at fixed spots on every island | Collectible rabbits that boost the event's economy | VERIFIED |
| Museum | Donate gear you found | Small permanent SkyBlock XP per first donation | VERIFIED (milestone bonus numbers UNVERIFIED) |
| Bestiary | Kill every mob type | Health, SkyBlock XP, combat XP | VERIFIED. This is really Hunting, which is shelved |

**Takeaway:** in SkyBlock, only Fairy Souls feed the main level XP, and that caps at a small total. A player once suggested an Exploration skill on the forums, but no staff replied and it was never planned (VERIFIED).

## 2. What Wynncraft gives for exploring

| Feature | What you do | What you get | Tag |
|---|---|---|---|
| Territorial Discoveries | Walk into one of 400+ territories | One-time XP (about 0.78M total) | VERIFIED |
| World Discoveries | Walk into one of 200+ named landmarks. A banner pops on screen | One-time XP, from 10 up to 4,000,000 depending on the area's level (about 8.4M total) | VERIFIED |
| Secret Discoveries | Solve a puzzle, a parkour route or a hidden lever, sometimes while carrying a quest item. Level-gated | The biggest pot: about 38.9M XP total | VERIFIED |
| Discovery XP rule | - | XP-boost gear does **not** increase discovery XP, on purpose | VERIFIED |
| Content Book | An item that lists everything you've found or finished, per level bracket | A completion checklist | VERIFIED |
| Caves (100+) | Clear a cave from start to end | End chest (top tiers), first-clear XP, emeralds, sometimes a unique item. About 36.5M cave XP total | VERIFIED |
| Loot chests, tiers I-IV | Find chests. Harder to reach means a higher tier | Gear, emeralds. Accessories only come from the top two tiers. Each player gets their own copy of every chest | VERIFIED (the "best after 2-3 hours unopened" timing is UNVERIFIED) |
| Mini-quest posts | Find a post somewhere in the world, gather or slay | XP, emeralds, profession XP | VERIFIED |
| World Events | A random event starts in the region you're in | XP, loot, keys, runes | VERIFIED |
| Lootrun camps | Unlock them by clearing a region's caves and quests | A repeatable endgame loot loop | VERIFIED |
| Fast travel | Quests unlock tunnels, airships and boats. Teleport scrolls are bought | Convenience | VERIFIED (whether a scroll needs a prior visit is UNVERIFIED) |

**Takeaway:** Discoveries add up to about 48M XP, the largest single XP source in Wynncraft. Caves add about 36.5M more. Wynncraft has no separate achievements system.

## 3. What Hytale lets us detect

I re-checked the key points in the jar and assets myself.

| Signal | Plain words | Feasibility |
|---|---|---|
| Entering a named zone | Hytale already shows a "zone discovered" banner and remembers it once per player. We can listen for that moment. The catch: it reads the world generator's zone map. The default world has only 5 names (Emerald Wilds, Howling Sands, Whisperfrost Frontiers, Devastated Lands, Oceans), split into about 28 regions. A hand-built island world just reports "Void" | VERIFIED hook (only useful on generated worlds) |
| Entering OUR named spot | We keep a list of spots (a point plus a radius, or a box) per island. The per-second player check SkyySkills already runs tells us who is standing where | VERIFIED hook (the pieces are proven; the spot list is new) |
| Show a Wynn-style banner and sound | The engine function behind the zone banner is one we can call ourselves | VERIFIED hook |
| First arrival on an island | Island configs can carry their own discovery banner (the Forgotten Temple uses one). The engine remembers it once per island world per player | needs a test (each private island gets a new world id, so this only suits shared chain islands) |
| Biome changed | The engine updates your current biome every second. There is no event for it, so we'd check it ourselves | VERIFIED hook |
| Near a structure or dungeon | Search tools exist for generated worlds, but you have to ask them. Nothing tells you "you're near one" | needs a test (hand-placed spots are simpler) |
| Opening a chest the first time | The "used a block" event SkyySkills already listens to fires on chests. Chests a player placed are tagged, so we can tell them apart from world chests. There is no clean "opened" event. The installed Lootr mod shows how per-player chest loot works | needs a test |
| Chunks explored (map coverage %) | The installed BetterMap mod already tracks each player's explored chunks. That's a pattern we can copy | needs a test |
| Map markers revealed | The engine keeps a "revealed markers" list per player | needs a test (our map isn't built yet) |
| Hytale Memories | A real lore-card collectible, but it only covers NPCs in one vanilla dungeon | VERIFIED, too narrow to build on |
| Respawn point / warp / teleporter set | All exist as engine pieces | VERIFIED hook (minor XP only) |
| "Container opened" event, biome-discovery event, bestiary, "near a POI" push | Not in the engine | not possible (we work around them as above) |

**Two design facts from this:**
1. **Profiles:** Hytale's own "discovered" list is per account, not per profile. Profiles are full saves, so Exploration must keep its own per-profile record, like every other mod (profile contract).
2. **Hand-built chain:** since the islands are built by hand, discoveries become a **hand-authored list**, which is exactly how Wynncraft does it. The builders place the spots.

## 4. Options for SkyWynn's Exploration skill

★ = suggested starter set. **Skyy picks; none of this is decided.**
Effort: S = a day or two, M = about a week with testing, L = a big project or blocked by another system.

### (a) Ways to EARN Exploration XP

| # | Option | From | How it fits SkyWynn | Feasibility | Effort |
|---|---|---|---|---|---|
| A1 ★ | **Discovery spots**: named landmarks on every island, plus a few in the hub. A banner, a sound and one-time XP that scales with the island's tier | Wynn (World Discoveries) | Gives each chain island a reason to cross the whole thing, not just rush the exit. The hub gets starter spots so new players learn the system | VERIFIED hook | M (admin command to place spots; builders author the list) |
| A2 ★ | **Secret discoveries**: hidden spots behind parkour, levers or puzzles. Bigger XP | Wynn (Secret Discoveries) | Pairs with Acrobatics (jump bonus opens routes). Rewards knowing an island well | VERIFIED hook (same system as A1) | M (mostly building work) |
| A3 | **First arrival on island N**: a large one-time XP payout | Wynn / new | Matches "finish one island before the next unlocks" | needs a test; the chain isn't built yet | S once the chain exists |
| A4 | **World chests found**: first open of each world-placed chest gives XP | Wynn loot chests | Chests on islands become exploration targets. Lootr shows the per-player loot pattern | needs a test | M |
| A5 | **Map coverage**: small XP per new chunk walked, capped per island | new (BetterMap pattern) | Rewards wandering. No XP while `/fly` is on | needs a test | M |
| A6 | **Engine zone discovery** on any generated world (a resource world, say) | Hytale | Only matters if SkyWynn ever has a generated wilderness | VERIFIED hook | S |
| A7 | **First clear of a story dungeon or cave** | Wynn (caves) | Story-beat dungeons sit on the chain | blocked: SkyyDungeons is plan-only | L |

### (b) Per-level rewards

| # | Option | From | How it fits | Feasibility | Effort |
|---|---|---|---|---|---|
| B1 ★ | **Coins per level**, same as the other skills | SkyBlock / our SkyySkills | Consistent with the live skills | VERIFIED (live pattern) | S |
| B2 | **Chest luck**: a small chance per level of an extra roll from world chests | Wynn (Loot Quality) | Makes A4 better as you level | needs a test (depends on A4) | M |
| B3 | **Finder sense**: higher levels show nearby undiscovered spots as a compass or HUD hint | SkyBlock (relic compass) | Uses the SkyyHud widget system; later the map | needs a test | M |
| B4 | **Small stat trickle** (e.g. +Health every 10 levels) | SkyBlock skill rewards | SkyyAccessories already adds max health this way | VERIFIED pattern | S |
| B5 | **Its own small skill tree** | our gathering trees | Only if Skyy wants trees beyond the gathering skills | open | L |

### (c) Milestone / collection rewards (fairy-soul style)

| # | Option | From | How it fits | Feasibility | Effort |
|---|---|---|---|---|---|
| C1 ★ | **Hidden collectibles** ("Echo Shards" is the Master Plan's placeholder name). Hand them in 5 at a time to an NPC in the hub. Each batch gives something permanent: Magic Bag capacity, an accessory bag slot or a small stat | SkyBlock (Fairy Souls) + Master Plan row 7.11 | Sends players back to the hub (the social point). Spread over the hub and every island | needs a test (a clickable block + the proven block-use event) | M |
| C2 | **Island completion %**: a per-island checklist (spots, secrets, chests, shards). 100% gives a title, cosmetic or coins | Wynn (Content Book) | Cheap add-on to A1 and C1; could be a `/explore` page | needs a test | S-M |
| C3 | **Zone hunt with a finder compass**: one island gets its own coin hunt | SkyBlock (Relics) | A themed side activity for one island | needs a test | M |
| C4 | **Seasonal egg hunt** | SkyBlock (Hoppity) | Events, later | needs a test | L |
| C5 | **Museum** of found items | SkyBlock | Probably belongs to Collections, later | open | L |

### (d) Unlocks (warps, travel, cosmetics)

| # | Option | From | How it fits | Feasibility | Effort |
|---|---|---|---|---|---|
| D1 ★ | **Warp unlocked on first arrival**: reaching an island's warp point adds it to your warp list from the hub | SkyBlock (auto-unlock on visit) + Wynn (earned fast travel) | Perfect for hub + chain: the hub becomes the travel point to every island you've reached. Vanilla `/warp` is global, not per player, so we'd need a per-profile unlock list (vanilla-first rule: reuse vanilla warp points, add only the lock) | needs a test | M |
| D2 | **Travel scroll items** that unlock a warp (e.g. secret islands) | SkyBlock | An add-on to D1; tradable on the Bazaar | needs a test | S after D1 |
| D3 | **Titles and cosmetics** ("Wayfarer of Emerald Wilds") at milestones | new | Needs a small title or chat-tag system | needs a test | S-M |
| D4 | **Lootrun-style camp** unlocked by 100% on an island | Wynn | A repeatable endgame loop per island | open | L, later |
| D5 | **Map reveal**: POI icons appear on SkyWynn's map after discovery | Wynn map / SkyBlock waypoints | The map isn't built; design for it now | needs a test | L, later |

**Suggested starter set (Skyy picks):** A1 + A2 (discovery spots and secrets, one system), C1 (collectibles), D1 (warps on arrival), B1 (coins per level). C2 is a cheap extra once A1 and C1 exist.

**A warning for any pick:** discoveries are one-time and run out. With a level-100 cap, Exploration needs either enough spots per island or some repeatable sources (A4 chests, A5 coverage, events). Otherwise players hit a wall where there is nothing left to find.

## 5. Questions for Skyy

1. **Per profile or account-wide?** Profiles are full saves, so the default is that a new class starts exploring from zero. Should shards or warps carry over?
2. **One-time only, or repeatable too?** This decides how reachable level 100 is.
3. **Should Exploration XP ignore XP boosts** (the Wynncraft rule)?
4. **What should collectibles pay?** Bag capacity, accessory slots, stats or coins?
5. **Warps:** free on the first visit, or do they cost coins or a scroll?
6. **A name** for the collectible ("Echo Shards" is a placeholder).
7. **Does Exploration get its own skill tree**, or only the gathering skills?
8. **Should `/fly` or teleports block Exploration XP?**

---

## Appendix: engine names (for the builder, not for Skyy)

Checked with `tools/dev/reflect.py`, `bc.py`, `bcfull.py`, `callers.py` and `cpgrep.py` against the release `HytaleServer.jar` and `Assets.zip`.

- Zone discovery: `server.core.event.events.ecs.DiscoverZoneEvent` (+ `$Display`, cancellable; it hides the banner). Fired from `WorldMapTracker.onZoneDiscovered`, only when `discoverZone(World, regionName)` returns true. That call checks and adds to `PlayerConfigData.getDiscoveredZones()`: one set per player, not per world, keyed by the zone folder name (e.g. `Zone1_Tier1`). Fired **before** the display check, so zones with `Display:false` (shores, shallow seas) also fire it. VERIFIED.
- Zone data comes from `server.worldgen.BiomeDataSystem` via `ChunkGenerator.getZoneBiomeResultAt`. The world must use the classic worldgen generator. Zone names live in `Assets.zip` `Server/World/Default/Zones/*/Zone.json` ("Discovery" block); the `Void` and `Flat` worlds have no zone name. VERIFIED.
- Current zone and biome: `Player.getWorldMapTracker().getCurrentZone()` / `getCurrentBiomeName()`, updated at `UPDATE_SPEED` 1.0. VERIFIED.
- Banner: `server.core.util.EventTitleUtil.showEventTitleToPlayer(PlayerRef, Message, Message, boolean[, String icon, float, float, float])`, plus `SoundUtil.playSoundEvent2d`. VERIFIED.
- Instance discovery: `builtin.instances.event.DiscoverInstanceEvent` (+ `$Display`). Fired by `InstancesPlugin.onPlayerReady` → `showInstanceDiscovery`, gated by `PlayerConfigData.getDiscoveredInstances()` (world UUID) unless `AlwaysDisplay`. The config goes in `Server/Instances/<name>/config.json` "Discovery" (TitleKey, SubtitleKey, Icon, Major, ...); see `Forgotten_Temple`, `Defaults/CreativeHub`. VERIFIED.
- Block use: `UseBlockEvent$Post`, subscribed via `EntityEventSystem`, as in SkyySkills 0.3.1. Placed-by tag: `server.core.modules.interaction.components.PlacedByInteractionComponent.getWhoPlacedUuid()`. Containers: `ItemContainerBlock` (`getDroplist()`). VERIFIED.
- Map markers: `server.core.universe.world.worldmap.markers.DiscoverableMapMarkers.isRevealed/reveal/hide(Player, String)`. VERIFIED.
- POI search: `builtin.locate.PrefabPatternSearchUtil`, `CaveDungeonSearchUtil`, `SpiralSearchUtil` (pull only). VERIFIED (from research notes).
- Memories: `builtin.adventure.memories.*` (`PlayerMemories`, `MemoriesPlugin`). VERIFIED (research notes).
- Warps and respawn: `builtin.teleport.Warp`, `builtin.adventure.teleporter.component.Teleporter`, `RespawnEvent`, `PlayerRespawnPointData`. VERIFIED (research notes).
- Mods to copy from (read-only): BetterMap 1.3.8 `dev.ninesliced.exploration.ExploredChunksTracker` (per-player explored chunks: `markChunkExplored`, `getExploredCount`); Lootr 0.3.12 (per-player world chests); ZiggfreedCommon `ZoneLocator` (reads the current zone). VERIFIED by reflection.

## Sources

SkyBlock (community mirror; official wiki pages were not reachable during research):
- https://hypixelskyblock.minecraft.wiki/w/Fairy_Souls
- https://hypixelskyblock.minecraft.wiki/w/Achievements
- https://hypixelskyblock.minecraft.wiki/w/Travel_Scrolls
- https://hypixelskyblock.minecraft.wiki/w/Relics
- https://hypixelskyblock.minecraft.wiki/w/Enigma_Souls
- https://hypixelskyblock.minecraft.wiki/w/Crystal_Nucleus
- https://hypixelskyblock.minecraft.wiki/w/Commissions
- https://hypixelskyblock.minecraft.wiki/w/Museum
- https://hypixelskyblock.minecraft.wiki/w/Bestiary
- https://hypixelskyblock.minecraft.wiki/w/SkyBlock_Levels/Tasks
- https://hypixel-skyblock.fandom.com/wiki/Glacite_Mineshafts
- https://wiki.hypixel.net/Hoppity's_Hunt
- https://hypixel.net/threads/new-skill-idea-exploration.6085811/

Wynncraft:
- https://wynncraft.wiki.gg/wiki/Experience_Points
- https://wynncraft.wiki.gg/wiki/World_Discoveries
- https://wynncraft.wiki.gg/wiki/Secret_Discoveries
- https://wynncraft.wiki.gg/wiki/Territorial_Discoveries
- https://wynncraft.wiki.gg/wiki/Content_Book
- https://wynncraft.wiki.gg/wiki/Caves
- https://wynncraft.wiki.gg/wiki/Loot
- https://wynncraft.wiki.gg/wiki/Lootrunning
- https://wynncraft.wiki.gg/wiki/Mini-Quest
- https://wynncraft.wiki.gg/wiki/World_Events
- https://wynncraft.wiki.gg/wiki/Fast_Travel
- https://wynncraft.wiki.gg/wiki/Version_2.0.3

Our own:
- HANDOFF.md sections 1 and 3, SkyySkills-Plan.md, SkyWynn-Master-Plan.md (row "Exploration collectibles"), SkyWynn-Decisions.md (rows 2.12, 7.11), SkyyIslands-Plan.md.
