# Loot round revision - boxes decided at identify, drop-only gear, more drops, vanishing loot chests

Cloud draft, 2026-10-06. Paper design; nothing built. Revises `research/Loot-Unid-Spec.md` (the "0.2.3 loot round" spec; the round is now
SkyyGear **0.2.6**, `RESUME.md` "Next" 3) and `research/cloud/Loot-Box-Design.md`. Every number is a placeholder and a Server Setup row (section 8).
Inputs read: `CLOUD-RESUME.md` task "Loot round revision"; `docs/answered/gear.md` (LOCKED 2026-10-02 drop boost + Wynncraft-style items, ANSWERED
2026-10-03 LOOT answers, LOCKED 2026-10-05 armor types, LOCKED 2026-10-06 LOOT); `research/Loot-Unid-Spec.md` sections 0-4, 7, 10-12;
`research/cloud/Loot-Box-Design.md`; `research/Exploration-Build-Spec.md` 2.2-2.3 (loot-chest capture, `PlacedByInteractionComponent` guard);
`research/Exploration-Research.md` (Wynncraft features); `HANDOFF.md` versions (SkyyExploration 0.2.3, SkyyMobs 0.1.3).

**Decisions followed (not re-decided):** LOCKED 2026-10-06 LOOT points (1)-(4); 2026-10-03 answers: class lean 50%, vanilla drops get the mob / zone
level, a LEVEL RANGE (not the exact level), rarity-coloured loot boxes, the extra chest piece only in NEW vanilla chests; LOCKED 2026-10-02: the extra
mob roll exists (rate now "a little higher"), about 1 in 3 new vanilla loot chests gets an extra piece (unchanged here); LOCKED 2026-10-05 armor types
(Heavy / Light / Cloth, soft rule); R3 (coins never skip a collection unlock). Loot-Box-Design option C / B (126 or 7 ids) is still open: this file works with either.

## 0. What Wynncraft does (WebSearch snippets only; wiki pages blocked)

| Fact | Source |
|---|---|
| Loot chests come in tiers I-IV; tier 1-2 marked by orange crit particles, tier 3-4 (deep in caves / obscure spots) by white particles | [Lootrunning (Historical)](https://wynncraft.wiki.gg/wiki/Lootrunning_(Historical)) snippet |
| Items in a chest are within 4 levels of the chest's level; unidentified items show a level range, the gear type, the chest level (armor: its material) | same snippet |
| Old rule: loot grew with time unopened (a fresh-opened chest had a few emeralds, hours-untouched ones far more) | same snippet (historical; current 2.x timer UNVERIFIED) |
| Each player gets their own copy of every chest | `research/Exploration-Research.md` l.38 (VERIFIED there) |
| The Identifier NPC identifies Unique and up for emeralds; price rises with item level and tier | [Identifier](https://wynncraft.wiki.gg/wiki/Identifier) snippet |
| Re-identify = put the item back in; **price x5 after each re-ID**; Corkian Augments steer a roll (max 2 per roll) | [forum post](https://forums.wynncraft.com/posts/1373034/), [Corkian Augment](https://wynncraft.wiki.gg/wiki/Corkian_Augment) snippets |
| Hytale prior art: "Loot Respawn System" refills world chests after a timer (8 h default), per-chest timers saved over restarts, **ignores player-placed storage**, cancels a refill if a player put items in | [CurseForge](https://www.curseforge.com/hytale/mods/loot-respawn-system) snippet (ideas only, no code) |

Not found in snippets (UNVERIFIED): today's Wynncraft respawn timer, whether chests spawn near players, whether re-ID changes the *item* or only its
stats. Skyy's lock ("I don't think it's set until you identify it, cause you can reroll and get a different looking weapon") is the rule here either way.

## 1. The box: what it stores, and identify (replaces Loot-Unid-Spec 1.4 + 2.1 step 3)

**Nothing secret is stored.** The item (and its exact level) does not exist until identify, so there is no sealed real id, no AES key, no `unid.key`,
no padding. A modded client sees only what the tooltip shows. **No seed either:** the repo and roll code are public, so a stored seed would leak the
result just like a sealed id. Identify rolls with SkyyGear's `SecureRandom` (`GearRoll.RNG`).

| Field (metadata `"SkyyGear"`, schema v2) | Meaning |
|---|---|
| `mys` | type key (`Weapon_Sword`, `Armor_Chest` ...), must match the box id |
| `r` | rarity, rolled at drop (shown on the box, box colour) |
| `lo`, `hi` | the shown level range: `L-2 .. L+2` around the source level L (mob / zone / chest), clamped to 1..`loot.levelTop` and to levels where the type has a candidate |
| `at` | armor only: Heavy / Light / Cloth, rolled at drop and shown ("Heavy Chestplate") so the class hint works; `-` for weapons |
| `src`, `ls`, `tier` | drop / chest / lootchest / admin; level source; loot-chest tier I-IV (for logs and the tooltip) |
| `q`, `t` (creation time), `id:false` | as before (q = the stack fallback, Loot-Unid-Spec 1.7; the old `at` time field is renamed `t`) |

**Identify (in-place swap, Loot-Unid-Spec 2.1 unchanged except step 3):** 3a level = uniform in `lo..hi` among levels with a candidate of `mys`
(and `at`); 3b item = weighted pick (section 3 pool weights) among candidates whose band holds that level; 3c a fresh identified document whose
`box` field keeps `{mys, r, lo, hi, at, n:0}` for re-rolls. Appraiser step-up still applies once, on this first identify only.
No candidate (pool changed by an update) = refused before coins move, logged (as today).

## 2. Re-identify (re-roll) - new

| Rule | Value |
|---|---|
| Who | only items with a `box` field (came from a box). Crafted gear, 0.2-style items and admin gear: no re-roll (Reforge is their tool) |
| What changes | item (same `mys` + `at`), level (inside `lo..hi`), modifiers - Wynncraft's "different looking weapon" |
| What never changes | rarity, type, armor type, range. No Appraiser step on a re-roll (no rarity fishing) |
| Cost | `cost.identify(r, hi)` x `unid.reroll.mult` ^ n (Wynncraft x5): 490 -> 2,450 -> 12,250 -> 61,250 for a Lv 41-45 Legendary |
| Limit | `unid.reroll.max` 3 re-rolls per item; `n` stored in `box` |
| Lost on re-roll | reforge level-ups and reforged modifiers (the page asks "Re-roll? This also clears its reforges" first) |
| Pays | no Smithing XP (coins never buy skill XP) |
| Where | the Identify page lists boxed items with a "Re-roll - N coins" button; same fingerprint check, coins first, refund on failure, one `setItemStackForSlot` |

**No coin loop (R3):** re-rolls only take coins; the result is a drop that could already have fallen (same pool, same range), never a recipe or
collection unlock, so coins skip nothing. The x5 ladder + cap make "fish for a look" a sink, not a farm. The local check: the NPC sell / salvage
value of any candidate must stay under the cheapest re-roll, else a re-roll could print coins (UNVERIFIED 3).

## 3. Drop-only vanilla gear joins the pool (ranking method; the list itself is LOCAL)

**Drop-only** = a gear id (Loot-Unid-Spec 1.1 rules: `Weapon_` family word or `Armor_` slot, minus Developer / Debug / Template / `*_NPC` / QA / Trooper)
that **no recipe in Assets.zip outputs** (any bench). The current pool (299 candidates) already holds many of them by band; this pass gives every
drop-only id a real level band instead of "band start" or none.

| Step | Ranking rule |
|---|---|
| 1 Power | weapons: primary-attack damage x attacks per second; armor: the piece's Health + resistance (SkyyGear's own armor numbers once the vanilla box is hidden) |
| 2 Ladder | compare with the CRAFTED ladder of the same type (sword vs Crude ... Onyxium swords; armor vs the same slot AND armor type: Heavy = metal sets, Light = leather, Cloth = tunics) |
| 3 Level | interpolate: power between crafted rungs A and B -> start = startA + (p - pA) / (pB - pA) x (startB - startA); band = start .. start + 8 (the metal-band width), clamped 1..49; above the top rung = 40-49 (re-ranked when Cindersteel+ ships) |
| 4 Source check | lowest vanilla drop list holding it: `Zone<N>_*_Tier<T>` -> that zone band split into tiers; no ladder (Kunai) = source rank only |
| 5 Disagree | power and source more than 10 levels apart -> use the mean, flag `check` for Skyy |
| 6 Override | `loot.pool.band` table row (id -> Min / Cap) wins over the computed band |

**Data format** (generated by the build from Assets.zip; only ids and computed levels, no vanilla stats or art committed - the local session places the
review copy per `INDEX.md`): tab-separated, one line per id:
`id  type  slot  armorType  source(craft|drop|both)  lo  hi  method(power|source|mean|override)  weight  flag`
Weight default 1 per id (`loot.dropOnlyWeight` multiplies drop-only ids, default 1).

## 4. Mob drop rate: 4% -> 6%

| Kills / hour | 4% (today) | **6% (proposed)** | 5% |
|---|---|---|---|
| 60 | 2.4 | 3.6 | 3.0 |
| 120 (project average) | 4.8 | **7.2** | 6.0 |
| 250 | 10 | 15 | 12.5 |

Why 6% (1 in ~17): "a little" = +50% boxes, still under 1 box per 8 kills; boxes now cost a re-roll-free identify sink of about 260-680 coins each
(Loot-Unid-Spec 3.6), so more boxes = more coin sink, not more coins. The hourly cap `loot.mob.capPerHour` stays 20 (333 kills an hour to reach it).
The loot chests (section 5) add up to about 6 boxes an hour on top, so a bigger mob jump would stack too much.

## 5. Our loot chests ("Unclaimed Luggage", tiers I-IV)

Lore: the Department of Arrivals keeps losing luggage; it lands on the surface near new arrivals and is collected again if nobody claims it.
**Host: SkyyExploration** (it already has the loot-chest registry `ChestReg`, open detection, chest XP); the boxes come from SkyyGear through a bridge
`gear:fn:box` (Object[]{type or null, lo, hi, rarity source, tier} -> ItemStack). Vanilla world chests keep the LOCKED 1-in-3 extra; these are separate.

### 5.1 Never touching player chests (three locks)
1. **Own block ids** `Skyy_LootChest_T1..T4`: a re-textured vanilla chest look, **no recipe, no item drop when broken, hidden from the creative list,
   unbreakable in Adventure**. Our code only ever places or removes blocks with this prefix.
2. **Registry** `Skyy_SkyyExploration/lootchests/<world>.tsv`: `x y z tier state(ACTIVE|LOOTED) placedAt lootedAt nonce`. A block is touched only when
   id prefix AND registry entry agree.
3. **Not a container:** the block has a Use interaction (no inventory), so no player can ever store items in it; the vanish can never delete a player's items.
   Clean-up: a `Skyy_LootChest_` block found on chunk load with no registry entry is removed, unless it has a `PlacedByInteractionComponent` (an admin
   placed it) - then it is left alone and logged.

### 5.2 Where they spawn (only in loaded chunks, never loads one)
Every `chests.spawnTick` (30 s), for each eligible player (Adventure, not flying, moved >= 32 blocks in the last 300 s = not AFK, in a zone world - never
SkyyIslands islands, the hub or dungeons): if fewer than `chests.perPlayer` (3) ACTIVE chests are within 64 blocks and the 128 x 128 area holds fewer than
`chests.perArea` (6), try up to 8 random columns 24-64 blocks away. A column is valid when: the top block is natural ground (grass, dirt, sand, snow,
gravel, stone list) with 2 air blocks above, not water / lava, no block entity within 8 blocks, no other loot chest within 32, not inside spawn
protection. Place the block, add the registry line, play a soft "thump" if a player is within 24.

### 5.3 Tier, content, loot and vanish

| Tier | Weight | Boxes (unid) | Rarity | Vanilla roll |
|---|---|---|---|---|
| I | 60 | 0-1 (50%) | Chest odds | 1 roll of `Zone<N>_Encounters_Tier1` |
| II | 28 | 1 | Chest odds | Tier2 list |
| III | 10 | 1-2 | Chest odds + `odds.levelShift` x 10 | Tier3 list |
| IV | 2 | 2 | Chest odds + shift x 20 | Tier3/4 list |

Level L = the zone level at the chest (`mob:fn:levelAt`, Loot-Unid-Spec 4.2 chain); boxes get `lo..hi` around L. Tier weights shift up with the
zone (Z4-Z5 x2 for III / IV). Average 0.77 boxes per chest. **No coins** in chests (no new faucet).
**Loot (per player, Wynncraft-style):** Use -> the loot goes straight into the player's inventory (overflow drops at their feet), chat summary.
Each player may loot a chest once. After the first loot the chest stays `chests.shareSeconds` (20) for nearby players, then **vanishes** (block -> air).
**Respawn:** the site waits `chests.respawnSeconds` (1800) then comes back full at the same spot if still valid and a player is within 64; new random
sites keep appearing too. **Despawn:** an unlooted chest with no player within 96 for `chests.despawnSeconds` (900) is removed (on chunk load if unloaded).

### 5.4 Anti-camping and limits
Per player: `chests.capPerHour` (8) loots per rolling hour; the same site once per `chests.siteCooldown` (3600) per player; AFK players spawn nothing.
Per area: `chests.perArea` (6) ACTIVE in 128 x 128. Per world: `chests.worldMax` (200). Party members share area caps, not loot caps.

### 5.5 Server load
One probe pass per eligible player per 30 s (max 8 heightmap reads in loaded chunks), registry in memory, saved on change every 10 s (atomic write),
cleanup only in the chunk-load hook. No per-tick work, no entity per chest (a block). Worst case 50 players = 400 column reads per 30 s.

## 6. What changed (diff)

| Topic | Loot-Unid-Spec (old) | Loot-Box-Design (old) | This revision |
|---|---|---|---|
| Real item | sealed id (AES-GCM, 64-byte pad, `unid.key`) | sealed id kept | **decided at identify**; no key, no seal, no seed |
| Level | exact level shown | range, real level hidden at a random offset | range `L-2..L+2`; level rolled at identify |
| Re-roll | none | none | re-roll item + level + mods, x5 cost, max 3, rarity fixed |
| Armor type on box | - | "Heavy armor" hint line | `at` rolled at drop, shown; re-roll keeps it |
| Pool | 299 candidates by material band | same | + every drop-only id ranked (power ladder + source check) |
| Mob rate | 4% (1 in 25) | - | **6%** (1 in ~17) |
| Chests | 33% extra in new vanilla chests | - | unchanged + our tier I-IV loot chests |
| Old mystery items | 18-id migration rules | 18 -> 126 swap | nothing shipped yet, so no migration of sealed items |

## 7. Build stages (full round: items, coins, saved data, two mods)

| Stage | Work |
|---|---|
| 0 local | Assets.zip scan: drop-only list + ranking TSV for Skyy; engine proofs (U1-U5) |
| A SkyyGear 0.2.6 | boxes v2 (no seal), identify roll, pool + drop-only, 6% rate, `gear:fn:box` bridge, box art (Loot-Box-Design) |
| B SkyyGear 0.2.6 | re-roll on the Identify page |
| C SkyyExploration next | `Skyy_LootChest_T1..T4` blocks, registry, spawner, Use loot, vanish / respawn / despawn, Exploration XP on loot |

## 8. Server Setup rows (times in seconds)

| Row | Default | Row | Default |
|---|---|---|---|
| `loot.mob.chance` | 6 % | `chests.enabled` | on |
| `unid.rangeHalf` | 2 (range 5 wide) | `chests.spawnTick` | 30 s |
| `unid.reroll.max` | 3 | `chests.perPlayer` / `perArea` / `worldMax` | 3 / 6 / 200 |
| `unid.reroll.mult` | 5 | `chests.ringMin` / `ringMax` | 24 / 64 blocks |
| `unid.showArmorType` | on | `chests.shareSeconds` | 20 s |
| `loot.dropOnlyWeight` | 1 | `chests.respawnSeconds` | 1800 s |
| `loot.pool.band` | empty table | `chests.despawnSeconds` | 900 s |
| `chests.tierWeights` | 60/28/10/2 | `chests.capPerHour` / `siteCooldown` | 8 / 3600 s |
| `chests.boxes` | 0.5/1/1.5/2 | `chests.afkSeconds` | 300 s |

## 9. Exploits

| Exploit | Answer |
|---|---|
| Modded client reads the box | nothing to read: the item does not exist yet |
| Identify-and-dump / AH sniping by contents | impossible; boxes are fair trades |
| Re-roll coin loop | x5 ladder, max 3, no XP; local check of sell / salvage values |
| Re-roll rarity fishing | rarity fixed, Appraiser only on first identify |
| Chest in a player base / deleting player items | natural-ground + no block entity within 8; our block is not a container; only our id is removed |
| Camping a site | per-player site cooldown, hourly cap, AFK rule |
| Alts / party farming | caps per account and per area; spawns need movement |
| Double loot | state LOOTED + per-player set written before the give, world thread only |

## For the local session (UNVERIFIED)
| # | Check |
|---|---|
| U1 | A plugin can place and remove a block in a loaded chunk from a system / `world.execute` without loading chunks |
| U2 | A custom block with a Use interaction and no container fires `UseBlockEvent` for our handler; unbreakable in Adventure |
| U3 | Sell / salvage value of every pool item (no re-roll coin loop) |
| U4 | Heightmap / top-block read API for a loaded column; natural-ground block list |
| U5 | `Zone<N>_Encounters_Tier1..4` drop lists all exist (tier count per zone) |
| U6 | The drop-only list and power numbers from Assets.zip (no recipe outputs the id) |
| U7 | `mob:fn:levelAt` is in SkyyMobs 0.1.3 or still to come |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Mob drop rate up to 6% (1 in 17)? | [6%] |
| 2 | Re-roll: x5 cost each time, max 3, keeps rarity, clears reforges? | [yes] |
| 3 | Show the armor type on armor boxes (Heavy / Light / Cloth)? | [yes] |
| 4 | Loot chests: each player gets their own loot, then it vanishes after 20 s? | [yes] |
| 5 | Looted chest comes back at the same spot (30 min) plus new random spots? | [both] |
| 6 | Name "Unclaimed Luggage" and lore? Coins in chests? | [the name; no coins] |
| 7 | Host the loot chests in SkyyExploration (chest XP too)? | [yes] |
