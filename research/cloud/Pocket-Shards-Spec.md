# Pocket Shards - spec draft (SkyWynn's minions)

> **Skyy's decisions 2026-10-02 win over this draft:** OPEN-QUESTIONS.md, section "Q&A with Skyy 2026-10-02", rounds 7.

Cloud draft, 2026-10-02. Paper design only; nothing built. Builds on `docs/plans/SkyyMinions-Plan.md` (the Pocket Shards section) and
`research/Isles-of-the-Void-Lore.md`. Every game-engine fact is UNVERIFIED unless said otherwise - see "For the local session".

## 0. Research note (what I could and could not check)

The Hypixel wiki hosts were blocked for page fetches in this cloud session, so I only had search snippets. The table below says which
SkyBlock facts are confirmed by those snippets and which come from my memory (treat as approximate; **the shape matters, not the exact numbers**).

| SkyBlock fact | Source |
|---|---|
| Tiers I to XI (a few minions have a 12th tier); higher tier = faster and more storage | search snippet, [Hypixel SkyBlock wiki mirror](https://hypixelskyblock.minecraft.wiki/w/Cobblestone_Minion) |
| Start with 5 placed minions; more slots from crafting UNIQUE minions (also from tiers and profile upgrades) | snippet ([minion slots guide](https://www.minecraftiplist.com/blog/unlocking-all-31-minion-slots-in-hypixel-skyblock-a-comprehensive-guide/)) |
| Cobblestone minion: T1 delay 14 s, storage 64; T2 delay 14 s, storage 192 | snippet (Cobblestone Minion page) |
| Fuel examples: Coal 30 min +5%, Block of Coal 5 h +5%, Enchanted Bread 12 h +5%, Enchanted Coal 1 day +10%, Enchanted Charcoal 1.5 days +20% | snippet ([Minion Fuel table](https://hypixelskyblock.minecraft.wiki/w/Minion_Fuel/Table)) |
| Compactor: items to block form. Super Compactor 3000: to enchanted form. Auto Smelter: smelts output. Diamond Spreader: now and then +1 diamond, no speed cost. Minion Expander: +1 range, +5% speed (stacks twice). Flycatcher: +20% speed. Budget Hopper: sells when storage is full for 50% of price | snippet ([Minion Upgrades](https://hypixelskyblock.minecraft.wiki/w/Minion_Upgrades)) |
| Cobblestone delay by tier 14 / 14 / 12 / 12 / 10 / 10 / 9 / 9 / 8 / 8 / 7 s; storage 1 / 3 / 3 / 6 / 6 / 9 / 9 / 12 / 12 / 15 / 15 stacks of 64 | memory, **UNVERIFIED** (first two storage values match the snippet) |
| Slot ladder: 5 slots at start, then +1 at roughly 5 / 15 / 30 / 50 / 75 / 100 ... unique minions crafted, 26 unique-craft slots at the top | memory, **UNVERIFIED** |
| A SkyBlock minion does not give skill XP; its items DO count for collections | existing SkyWynn lock (Decisions 3.7) |

## 1. What a Pocket Shard is (recap of the locks)

- One block. A tiny shard floats inside it. It does **not** touch the world around it (no 5x5 area).
- One resource per type, tiers I-XI, fuel, upgrades, collections credit, slots by crafting unique types, works offline, helpful not mandatory.
- Lives on the personal island (SkyyIslands), per profile (PROFILES-CONTRACT: each profile has its own shards and slots).
- Not Hytale Companions (row 9.10 answered for now).

## 2. Pocket Shard types (launch list)

SkyBlock has ~300 minion types. We start small and tie each type to a **collection** (SkyyCollections) and a **skill**, so
unlocking a type means you have already gathered that item yourself. Item ids are UNVERIFIED; names use the SkyyCollections naming.

| Group | Pocket Shard | Makes | Unlock (collection tier I = first craft recipe) | Notes |
|---|---|---|---|---|
| Mining | Cobblestone | Cobblestone | Cobblestone I | the starter shard; first one comes from the starter shard chain (lore) |
| Mining | Copper | Copper Ore | Copper ore I | |
| Mining | Iron | Iron Ore | Iron ore I | |
| Mining | Thorium | Thorium Ore | Thorium ore I | |
| Mining | Cobalt | Cobalt Ore | Cobalt ore I | |
| Mining | Adamantite | Adamantite Ore | Adamantite ore I | gated by gear level |
| Mining | Mithril | Mithril Ore | Mithril ore I | top vanilla tier; later our own tiers |
| Mining | Coal / Charcoal | Coal (if the item exists) | Coal I | also the cheap fuel source - check item |
| Mining | Sand / Gravel / Clay | the block | collection I | cheap bulk |
| Foraging | Oak, Birch, Ash, Spruce ... | the log (one shard per wood type; launch with the 6 most common, add rest later) | that log's collection I | 33 log types exist; do the common ones first |
| Foraging | Stick, Plant Fibre | the item | collection I | |
| Foraging | Sapling (per tree) | saplings | | matches Saplings From Trees pack mod idea |
| Farming | Wheat, Carrot, Potato, Pumpkin, Melon, Berry ... | the crop item (as it drops, not planted) | crop collection I | simulates harvest; needs no farmland |
| Combat | Bone, Hide, Feather, Chitin, Sac ... | the mob drop | drop's collection I | "Zombie Pocket Shard" style names in the plan become item-named (Bone Pocket Shard); mob drops are SkyyCollections' Combat category |
| Smithing / Cooking | none at launch | | | their output needs player skill; revisit later |
| Fishing | none | | | Fishing is hidden in collections for now |

Launch size suggestion: **about 30 types** (8 mining, 8 foraging, 8 farming, 6 combat) - enough to fill 20+ slots of unique-crafting
without writing 300 recipes. Types are data rows (a `shards.types` table), not code, so adding one is a config line (like the Collections registry).

## 3. Tiers I-XI

### 3.1 Speed
Each type has a **base delay** (seconds per item at tier I). A tier multiplies it. Use SkyBlock's own ratio ladder (from the Cobblestone column,
memory, UNVERIFIED but it is just a smooth curve; any smooth curve works):

| Tier | I | II | III | IV | V | VI | VII | VIII | IX | X | XI |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Delay factor | 1.00 | 1.00 | 0.86 | 0.86 | 0.71 | 0.71 | 0.64 | 0.64 | 0.57 | 0.57 | 0.50 |
| Storage (stacks) | 1 | 3 | 3 | 6 | 6 | 9 | 9 | 12 | 12 | 15 | 15 |

Base delays by group (proposal, **placeholder**, all editable rows): bulk (cobblestone, sand, logs) 14 s; ores 20-40 s by rarity
(Copper 22, Iron 26, Thorium 30, Cobalt 34, Adamantite 40, Mithril 46); crops 20-30 s; mob drops 28-40 s. A SkyBlock minion's real
rate is HALF of its listed delay in practice for block-breakers (it also has to place); Pocket Shards simulate one step, so the delay is the real rate.

### 3.2 Crafting cost per tier
Pattern (SkyBlock-like, ours): T1 = 80 of the base item (plus a Shard Core, see 3.3). T2-T5 cost more of the base item (x2, x3, x4, x5 of 80 - bulk
steps); T6-T11 switch to **compressed** items (ex. blocks / bars / planks) so a tier stays reachable without a thousand loose items, T11 also needs
a rare drop from a zone guardian. All numbers rows in Server Setup.

| Step | Cost shape |
|---|---|
| T1 | 80 base item + 1 Shard Core |
| T2 | 4 stacks (about 160 base item) + the T1 shard |
| T3-T5 | rising multiples of base item + previous shard |
| T6-T10 | compressed forms of the item (blocks, bars) + previous shard |
| T11 | big compressed stack + 1 Void Fragment (zone 3-4 guardian drop) + previous shard |

The previous-tier shard is consumed (tiers are upgraded in a crafting step, the shard keeps its upgrades and contents, like SkyBlock).

### 3.3 The Shard Core
A new craftable item (a Cracked Shard Core from the starter chain mini boss, later crafted from Void Fragments) that is the one-time
price of every type's T1. It ties the system into the story and gives a sink for the rare drop. Name is a working name.

## 4. Fuel

One fuel slot. Fuel burns while the shard works; offline time counts too (fuel lasts as long as real time, same as storage accounting).

| Fuel | Duration | Speed | Made from |
|---|---|---|---|
| Charcoal / Coal | 30 min | +5% | burn from logs (vanilla) - item ids UNVERIFIED |
| Coal Block | 5 h | +5% | |
| Enchanted-style compressed coal ("Compressed Charcoal") | 24 h | +10% | Smithing/Alchemy station |
| Void Oil | 36 h | +20% | Alchemy; a Void Fragment in the recipe |
| Void Core (rare) | permanent while fuelled by the player | +25% | zone boss drop, one per shard |

Rows: one `shards.fuel.<id>` entry (duration seconds, percent). Admin can add fuel types.

## 5. Upgrade slots (3 slots per shard)

SkyBlock minions have 2 upgrade slots, 1 fuel slot, 1 shipping slot. Ours: **fuel (1), upgrade (2), output (1)**.

| Upgrade | Effect | Unlock | SkyBlock model |
|---|---|---|---|
| Compactor | outputs turn into their block form when you have enough | Cobblestone collection tier V (SkyBlock gates it the same) | Compactor |
| Super Compactor | compress into the next form too | late collection | Super Compactor 3000 |
| Auto-Smelter | smelts output (ores to ingots) using our Smithing recipes | Smithing level / collection | Auto Smelter |
| Storage Expander | +3 stacks, up to two | Mining collection | Small Storage |
| Void Lens | +20% speed | craftable from Void Fragment | Flycatcher |
| Tide Charm | +5% speed, can stack twice | craftable | Minion Expander (range is meaningless for us, so only the speed) |
| Gem Spreader | now and then +1 of a rare drop (gem / essence) | late | Diamond Spreader |
| Auto-Sell Hopper | sells full storage to the nearest NPC buyer at 50% of the NPC sell price | late, **capped** (below) | Budget Hopper |

Auto-Sell inflation guard (Decisions 3.5 "watch inflation on public"): sell price 50% of NPC value, a daily cap on coins per profile
(updated 2026-10-06: auto-sell has **no cap of its own**; it pays 50% and counts toward the ONE shared NPC sell-back cap `shops.dailySellCap`, 20,000 a day in Zone 1 x1.5 per zone, see NPC-Shops-Spec.md section 3; the old separate `shards.autosell.dailyCoins` 50,000 row is dropped - Economy-Audit.md C9, F9) and the sold items still count for collections but pay **no** skill XP and **no** extra
tree bonus. Admin switch to turn auto-sell off.

## 6. Slots

- **Start with 5 placeable Pocket Shards per profile** (SkyBlock: 5).
- **More slots by crafting unique types** (types, not tiers): suggested ladder, scaled for our ~30 launch types:

| Unique types crafted | 0 | 5 | 10 | 15 | 20 | 25 | 30 |
|---|---|---|---|---|---|---|---|
| Slots | 5 | 6 | 8 | 10 | 12 | 14 | 16 |

SkyBlock's ladder is slower and has 300 types to go through. Ours must be reachable with 30 types; rows editable.
- A second source later (the island's size tier, SkyyIslands): +1 slot per island size step. Not at launch.
- Slots and shards are per profile; deleting a profile deletes its shards (follows PROFILES-CONTRACT).

## 7. Collections, skills and economy

| Rule | Value |
|---|---|
| Items made count for the matching collection | yes (existing lock). Bazaar-bought never count. Items from a shard count when you COLLECT them (take them out), not when produced, so an unattended shard cannot silently finish a tier - and tiers must be earned by the owner, not a co-op member |
| Skill XP from shard output | **none** (SkyBlock gives none; keeps real play valuable) |
| Class / combat shards and kill XP | none; they make drops only |
| Bonus drop effects (double drop perk, skill tree) | do not apply |
| Output cannot be sold at more than NPC prices | auto-sell only via the hopper above |
| Not mandatory | no quest or zone unlock needs a Pocket Shard |

## 8. Offline time, storage rules

- A shard stores `lastRun`. On load (island visit, chunk load, server start) it computes `elapsed = min(now - lastRun, maxOffline)` and adds
  `floor(elapsed / delay)` items, capped by storage and fuel time left. `maxOffline` default 3 days (row), so abandoned shards do not pile up forever.
- Fuel burns during `elapsed` too; the speed bonus is applied to the fuel-covered time only.
- When storage is full it stops; the visible shard dims (visual cue, a block state).
- Opening the block (F) shows a vanilla-style window with: items grid, fuel slot, 2 upgrade slots, tier and rate lines, "Collect all". UI follows the
  vanilla kit (`tools/skyyui.py`).

## 9. Server Setup rows (config kit)

`shards.enabled`, `shards.baseSlots` (5), the slot ladder, `shards.types` (table: id, group, item, base delay, collection key, unlock tier),
`shards.tier.delayFactor` / `shards.tier.storage` lists, `shards.maxOffline` (seconds shown as hours/days), fuel table, upgrade rows (effect %),
autosell switch + percent (the daily cap is the shared `shops.dailySellCap`, updated 2026-10-06). All times in seconds.

## 10. Story fit (suggested)

- The first Cobblestone shard is a gift/quest reward from the "talking rock guide" ("a shard of me" joke) or the bounty from the starter shard chain mini boss.
- Shard cores are "leftover paperwork" from the clerk; Void Fragments from guardians. Names are working names.

## 11. For the local session (UNVERIFIED engine questions)

| # | Question |
|---|---|
| 1 | Can a mod register a custom block with a block entity that holds an inventory and survives save/load (Hytale "container"/"bench" block entities)? Check the vanilla Workbench/Chest block classes and how SkyySacks/others store data. |
| 2 | A custom block model with a floating inner shard (static model vs animated; does a model support a looping idle animation?). Fallback: static glowing block texture. |
| 3 | Is there a tick/timer hook for placed blocks, and can we avoid per-block ticking by computing on load only (as in section 8)? Prefer lazy accounting (no tick at all) + a 1 s HUD refresh only while a window is open. |
| 4 | Max stack size per item in Hytale (I used 64 for the storage unit). |
| 5 | Exact item ids for coal/charcoal, sand, clay, crops and mob drops (use the SkyyCollections registry as the source of truth). |
| 6 | How profile switching/deleting should hide or remove placed shard blocks on the island (follow SkyyIslands per-profile world). |
| 7 | The bridge key for crediting collections from a shard (`coll:fn:...`) - must credit on collect, owner only. |
| 8 | Whether the Companion tech (Chapter 2) later could host the visual shard; not needed now. |

## 12. Questions for Skyy

1. Launch list size: about 30 types OK, or start with 12? (Recommended: 12 first - Cobblestone, Copper, Iron, Oak, Birch, Wheat, Carrot, Pumpkin, Bone, Hide, Feather, Charcoal - then grow.)
2. Should a shard's items count for collections when produced or when collected? (Recommended: when collected.)
3. Auto-sell at launch or later? (Recommended: later, once Economy exists; ship the daily cap with it.)
