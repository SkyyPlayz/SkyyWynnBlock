# Tree fall: felled-log crediting + Tree Feller rework (build spec)

*Written 2026-09-24 by the research workflow skywynn-tree-fall-research. Research only: no build script, mod folder, game file or other doc was changed; scratch files under tools/dev/scratch/ were deleted.*
*Targets (HANDOFF feedback round 2 queue): **SkyySkills 0.4.2** (on top of 0.4.1), **SkyyCollections 0.2.1** (on 0.2), **SkyyTrees 0.2.1** (on 0.2). Line numbers below are from `build_skyyskills_0.4.py`, `build_skyycollections_0.2.py` and `build_skyytrees_0.1.py`. Build through the `tools/*_patch.py` chain, not by editing generated scripts.*
*Skyy's report (2026-09-24): "right now i only get xp for the log i break, so i break 1 log and the whole tree falls, then i only get 6 xp per tree. not a great tradeoff." Data point: one felled birch dropped 20 logs; Collections counted 1 and Foraging paid for 1 (HANDOFF log 07:25 / 07:26).*

**Legend.** VERIFIED means one of these:
- seen in `HytaleServer.jar` bytecode (tools/dev: reflect, bc, bcfull, clinit, callers, cpgrep);
- seen in `Assets.zip` (read in memory);
- seen in our build scripts or in an installed mod's class file;
- seen in game by Skyy.

UNVERIFIED means design, inference, or not yet tested in game. `[SKYY?]` marks a choice or number for Skyy (they/them).

---

## 0. Verdict in plain words

1. **The engine's tree fall cannot be hooked as an event.** VERIFIED. When you cut the base, only that one block fires `BreakBlockEvent`, which is the event SkyySkills and SkyyCollections listen to. The rest of the tree is removed later by the block-physics system, one block at a time. That system fires no event and knows no player. That is why you get 6 XP (one trunk) per tree.
2. **The fix: take a snapshot of the tree at the moment you break it, then watch it fall.** Our break listener runs while the tree is still whole (VERIFIED order), so it records every natural log of that tree. A short watcher then checks those positions about 5 times a second. Each log that turns to air, and that nobody broke by hand, is paid to you as if you had broken it:
   - Foraging XP from the same table (6 per normal trunk);
   - a double-drop roll;
   - Collections count;
   - Sap Tapper, Replanter and Pocket Change rolls.

   The logs still drop on the ground as they do now.
3. **The vanilla rule behind thick trees, now VERIFIED in bytecode.** A trunk stands if it has a solid block right under it. It also stands if a sideways chain of up to 5 trunk blocks (8 for Maple) leads to a trunk that does. So:
   - A 1-wide tree falls from one cut.
   - A 2x2 or wider tree falls only when every trunk block of the layer you are cutting is gone.

   This is why Skyy's **Tree Feller rework** (break the other logs on the same Y level) is exactly the right ability now.
4. **Player-placed logs never pay, and vanilla never lets them fall.** VERIFIED. Placed logs and leaves are flagged "deco" by the engine, and the physics system skips deco blocks. We also skip anything in our placed-block tracker, and we only pay trees that touch natural leaves.
5. **Where it is built:**
   - **SkyySkills 0.4.2:** snapshot, watcher, XP, double drops, a "who felled this" bridge, and a new per-log listener map.
   - **SkyyCollections 0.2.1:** accepts one more `coll:fn:add` source. That is a config default only; Collections 0.2 already works if the source is added by hand.
   - **SkyyTrees 0.2.1:** Tree Feller becomes same-Y only (level 1 = 1 log beside it, max = the whole layer). Felled logs also roll the per-log Foraging nodes.

Expected result for Skyy's birch: about 20 x 6 = **120 Foraging XP** instead of 6, plus 1 XP per leaf if leaf XP stays on (section 2.7). **Birch Log collection +20** instead of +1. Both match the HANDOFF test expectation.

---

## 1. How Hytale fells a tree (VERIFIED)

### 1.1 The player's break (the only part that fires an event)

`BlockHarvestUtils.performBlockBreak(Vector3i, BlockType, ItemStack, int, String, String, int, Ref breaker, Ref, Ref, ComponentAccessor entityStore, ComponentAccessor chunkStore)` (bytecode read 2026-09-24):

1. If the block type is `BlockType.EMPTY`, return.
2. If there is a breaker `Ref`:
   - build `new BreakBlockEvent(item, pos, blockType)` and fire it on the breaker with `ComponentAccessor.invoke(ref, event)`;
   - if the event is cancelled: `BlockSection.invalidateBlock` (resend) and **return; the block is never removed**;
   - otherwise the target becomes `event.getTargetBlock()`.
3. If there is **no** breaker, `EnvironmentBreakBlockEvent` is broadcast instead. It is the else branch, not a second event after `BreakBlockEvent`.
4. Set the flags:
   - `2048` is added unless `BlockInteractionUtils.isNaturalAction` (Adventure mode);
   - **`256` is added unless `BlockInteractionUtils.isNoPhysics`**, which is Creative mode with `PlayerCreativeSettings.noPhysics()` on.
5. `naturallyRemoveBlock(...)` removes the block and spawns its drops, then `fireOnBreakInteraction(...)` runs.

**Consequence:** at the moment any `BreakBlockEvent` listener runs, the broken block and the whole tree above it are **still in the world**. Corrections to earlier notes:
- The earlier engine notes said `setBlock(EMPTY)` runs before the event. Bytecode says it runs after, inside `naturallyRemoveBlock`.
- The earlier notes said `EnvironmentBreakBlockEvent` follows every player break. It does not; it fires only when there is no breaker.

### 1.2 The support rules (JSON + engine semantics)

**Trunk:** `Server/Item/Items/Wood/Oak/Wood_Oak_Trunk.json` is the parent of every other `Wood_<W>_Trunk`. 129 child files override only `Gathering.Breaking`. Maple sets `MaxSupportDistance` to 8. The trunk's own fields:
- `"Support": {"Down": [{"FaceType": "Full", "AllowSupportPropagation": false}], "Horizontal": [{"TagId": "Type=Trunk", "Support": "Ignored"}]}`
- `"MaxSupportDistance": 5`
- `"IgnoreSupportWhenPlaced": true`
- `Gathering.Breaking` and `Gathering.Physics` both = `Wood_Oak_Trunk`

**Branch:** `Wood_Oak_Branch_Long` (Short and Corner are its children):
- Up / Down: a `Full` face (REQUIRED), or a `Branch` face (Ignored = distance only);
- `MaxSupportDistance: 6`;
- `IgnoreSupportWhenPlaced: true`;
- Breaking and Physics drop list `Wood_Branch` (0-2 sticks + 0-1 sap, or 1 stick).

**Leaves:** `Plant_Leaves_Oak` and every child:
- `BlockSides`: `Family=Leaves` Ignored, `Type=Trunk`, `Type=Branch`, `Branch` face;
- `MaxSupportDistance: 4`;
- `IgnoreSupportWhenPlaced: true`;
- Soft drop `Tree_Leaves` (fibre), Physics drop `Tree_Leaves_Physics` (fibre, weight 2).

The pack mod **Saplings From Trees** changes the Physics drop of Ash, Azure, Beech, Birch, Cedar, Dry and Oak leaves to `Tree_<W>_Leaves` (fibre or sapling). Its template keeps `IgnoreSupportWhenPlaced: true`.

**Engine semantics.** `BlockPhysicsUtil.testBlockPhysicsAtPosition`, plus the `RequiredBlockFaceSupport` constructors and `BlockPhysics` constants:
- An entry without `"Support"` is **REQUIRED**, and `AllowSupportPropagation` defaults to **true** (no-arg constructor: `support = REQUIRED`, `allowSupportPropagation = true`).
- A satisfied REQUIRED entry means the block is supported (return `-2`, SATISFIES_SUPPORT).
- An **Ignored** entry never supports by itself. When its neighbour matches and propagation is allowed, it feeds a distance: `min(neighbour support value) + 1`.
  - A deco neighbour (value 15) counts as distance 1.
  - If the result is at most `MaxSupportDistance`, the block stands with that distance.
  - Otherwise the result is `0` (DOESNT_SATISFY): the block is broken by physics.
- A block with no REQUIRED or DISALLOWED entry returns `-1` and is never tested again.

**So a trunk stands if:**
- a Full face is directly under it; or
- a sideways chain of at most 5 trunk-tagged blocks (8 for Maple) leads to a trunk that has one.

**Leaves** stand within 4 leaf steps of a trunk or branch. Branches stand on a Full face above or below, or on a chain of branch faces.

### 1.3 The cascade (no event, no player)

1. **The cycle.** `BlockPhysicsSystems$Ticking.tick` runs `BlockSection.forEachTicking`, then `lambda$tick$0`, then `applyBlockPhysics`. The lambda returns `IGNORED` straight away when:
   - `BlockPhysics.isDeco(x,y,z)` is true, or
   - the block id is 0 (empty).
2. **The outcome.** When `testBlockPhysics` returns 0, `BlockType.getSupportDropType()` decides:
   - BREAK: `naturallyRemoveBlockByPhysics(pos, bt, rot, 256, sectionRef, ...)`;
   - DESTROY: the same call with `2304`;
   - FALL: `FallingBlock.fallBlock`. No tree block declares `SupportDropType`; the earlier notes grepped all assets and found only 3 debug files.
3. **Drops.** `naturallyRemoveBlockByPhysics` picks the drops in this order, then calls `naturallyRemoveBlock` (flags `| 32`):
   - `Gathering.Physics` (quantity 1, ItemId, DropList);
   - else `Breaking` (Quantity, ItemId, DropList);
   - else `Soft`;
   - else `Harvest`.

   The drops spawn as item entities at the block. There is **no** `BreakBlockEvent`, `EnvironmentBreakBlockEvent` or `DamageBlockEvent` anywhere on this path, and no player, UUID or cause (see the earlier engine notes and the bytecode).
4. **Timing.** Every removal notifies its neighbours (flag 256), so the tree comes down one physics pass after another. It is not one atomic operation. UNVERIFIED, derived from the rule above and not measured:
   - A 1-wide trunk loses about one level per pass.
   - A thick trunk "counts up" the sideways distance for up to `MaxSupportDistance` passes per layer before that layer breaks. A tall 2x2 or 3x3 tree can take several seconds.
   - The watcher below is built for that; the in-game debug line measures it (test T14).
5. **Child woods drop their own log.** UNVERIFIED but safe. `Gathering` is `appendInherited` on `BlockType`, but `Physics` inside `BlockGathering` is plain `append`, so Birch has no Physics entry and falls back to its own `Breaking` (a birch log). This matches Skyy's 20 birch logs. Our code copies the engine's selection at runtime, so it never depends on this.

### 1.4 Placed blocks, creative, protection

- **Placed = deco.** `BlockPlaceUtils.tryPlaceBlock` calls `BlockPhysics.markDeco(...)` for a player placement when `!player.isOverrideBlockPlacementRestrictions()` and `BlockType.canBePlacedAsDeco()`. That method returns `IgnoreSupportWhenPlaced || Gathering.UseDefaultDropWhenPlaced`, and both fields are inherited. **Placed logs and leaves never fall** (the tick lambda skips deco) and drop themselves. VERIFIED in bytecode; test T4 confirms in game.
- **Creative with noPhysics on:** flag 256 is not set, so nothing falls. Creative pays nothing in SkyySkills anyway (`SkillXp.creative`).
- **Island protection:** SkyyIslands 0.4.4 `GuardDamage` / `GuardBreak` cancel `DamageBlockEvent` / `BreakBlockEvent` for non-members. A cancelled break returns before removal (1.1 step 2), so nothing falls and there is nothing to credit.

### 1.5 What our mods and the reference mods do today

Our mods (VERIFIED):
- **SkyySkills 0.4:** `BreakSys` (handler) defers `BreakTask` (world.execute). `BreakTask` does, in order: cancel check, `PlacedStore.remove`, XP from `SkillCfg.classifyBreak`, `Perks.breakDouble`, `SkillBonus.gather` (`skill:on:gather`). This runs only for the player's own `BreakBlockEvent`.
  - XP table (xp.properties defaults, lines 452-465): `_Trunk` / `_Trunk_Full` 6 (special woods 3-30), `Plant_Leaves_` 1, `_Branch_*` 1, `_Roots` 2.
- **SkyyCollections 0.2:** H1 `CollBreakSys` counts only `BreakBlockEvent` drops. Walk-over pickups never count.
- **SkyyTrees 0.1 Tree Feller:**
  - search: a 26-neighbour flood, 6 across, 32 up;
  - size: 8 + 8 x level logs;
  - gates: a leaves check and a 30 s cooldown;
  - it breaks through `BlockHarvestUtils.performBlockBreak`, so each extra log fires a real `BreakBlockEvent` and is paid by SkyySkills and Collections.

Reference mods (VERIFIED from class files):
- TreeHarvester (Serilum) breaks extra logs silently with `World.breakBlock` and fires no event.
- vein-mining 2.4.0 builds a real `BreakBlockEvent` per block. Its `isDecoBlock` reads `BlockPhysics` from the chunk section exactly as section 3.1 does.
- MMOSkillTree 1.6.0 has no tree-fall handling in its constant pools.

No installed mod credits the physics cascade.

---

## 2. Crediting design

### 2.1 Overview

| Step | Where | Thread | What |
|---|---|---|---|
| 1 Snapshot | `BreakSys.handle` (new code at the top) | world, synchronous, block still present | if the break can topple wood, record the natural tree positions above it |
| 2 Commit | `BreakTask.run`, **first thing** after the cancel check | world (world.execute) | discard if cancelled; else claim the positions and start a `FellWatch` |
| 3 Watch | `FellWatch` (HarvestTask hop pattern: `HytaleServer.SCHEDULED_EXECUTOR` every `fell.pollMs`, then `world.execute`) | world | a claimed position that became EMPTY is "felled" |
| 4 Credit | `FellCredit.one` | world | XP, double drop, Collections, per-log nodes, felledBy memory |

The snapshot is taken at step 1 because by the time `BreakTask` runs, a physics pass may already have removed the log above the cut. A search at step 2 could then lose its path up the tree.

### 2.2 Trigger (inside `BreakSys.handle`, cheap for non-tree blocks)

A snapshot is attempted when **all** of these hold:
- `fell.enabled`;
- the world is not in `fell.disabledWorlds`;
- the breaker is not in creative (`SkillXp.creative(st, r)`, which respects `creativeXp`);
- the broken block is one of these kinds:
  - **TRUNK:** id in the TreeWood list with suffix `_Trunk` or `_Trunk_Full`;
  - **BRANCH:** suffix `_Branch_Short`, `_Branch_Long` or `_Branch_Corner`;
  - **UNDER:** any block that has a TreeWood trunk directly above it (`fell.underTrunk=true`). Cutting the ground out from under a tree fells it too.

Breaking leaves or roots never triggers a snapshot.

**Tree ids.** `FellDefs.WOOD` / `FellDefs.LEAVES` are generated at build time from `Server/BlockTypeList/TreeWood.json` (183 ids, all `Wood_<W>_<Trunk|Trunk_Full|Branch_Short|Branch_Long|Branch_Corner|Roots>`) and `TreeLeaves.json` (44 `Plant_Leaves_*`). Both are VERIFIED. `family(id)` = the id without that suffix (e.g. `Wood_Wisteria_Wild`).

### 2.3 Snapshot rules

- **Coordinates.** `y0` = Y of the broken block.
- **Seed.**
  - TRUNK or BRANCH: the broken block.
  - UNDER: the trunk above it; its family is used.
- **Wood search.** Breadth-first search over the 26-neighbourhood. A cell is accepted only if:
  - its id is in `WOOD` with the same `family`;
  - it is **natural**: not in `PlacedStore` and not `BlockPhysics.isDeco`;
  - `|dx|, |dz| <= fell.radius` (8);
  - `y <= y0 + fell.height` (64);
  - its height fits its kind:
    - TRUNK / UNDER trigger: trunks need `y >= y0`; branches and roots need `y >= y0 - 1`;
    - BRANCH trigger: branches only (never walk into trunks or roots), `y >= y0 - 1`.
  - Cap: `fell.maxLogs` (256) accepted cells.
- **Claims and layer.** Every accepted cell becomes a **claim**, except:
  - the broken block itself;
  - trunks with `y == y0`. These go into the **layer** list: the other base logs of a thick tree. They only fall by being cut, so they are never claims.

  With UNDER, `y0` is the ground block's Y, so the seed trunk at `y0+1` is a claim.
- **Leaf search** (always done for the natural-tree test; claims only when `fell.leaves=true`):
  - from every accepted wood cell, the 26 neighbours whose id is in `LEAVES`, natural, `y >= y0 - 1`;
  - then a search through leaves up to 4 leaf steps (their `MaxSupportDistance`), cap `fell.maxLeaves` (384);
  - with `fell.leaves=false` the search stops at the first natural leaf.
- **Natural-tree test.** `leafSeen` = at least one natural leaf was found. With `fell.needLeaves=true`, a snapshot without it is dropped at commit. This stops a log wall or a placed-log tower from ever paying (defense in depth; see 1.4 and 4.1).
- **Read budget.** At most `fell.maxReads` (8000) block reads per snapshot. Cache the `BlockSection` and `BlockPhysics` per chunk section inside one snapshot (a tree spans 1-4 sections), so each read is an array lookup.
- **Stored per position:** the packed key (`PlacedStore.key`), the block index (`BlockSection.get`) and a leaf flag.

### 2.4 Claims, several players, reuse

These per-world maps are read and written on the world thread. Use `ConcurrentHashMap` so the bridge can read them from any thread.
- `CLAIMS`: key -> `FellWatch`;
- `LAYER`: key -> `FellWatch`;
- `FELLED`: an LRU of key -> `Object[]{UUID, pkey, Long at, String id}` (cap 8192, TTL `fell.memoryMs` 60 s).

**Handler (step 1)**, for the broken position `b`:
1. **`b` is claimed by a live watch `o`** (someone breaks a log that is already part of a falling tree):
   - remove the claim (this position is now a hand break and is paid by the normal path);
   - pass `o` to `BreakTask` so a **cancelled** break puts the claim back;
   - set `bInOther = !o.u.equals(u)`;
   - if `o.u.equals(u)`, call `o.touch()` and **skip the search**: the tree is already watched.
2. **`b` is in `LAYER` of a live watch of the same player** (the Tree Feller's extra base breaks, or cutting a 2x2 by hand): call `touch()` and skip the search.
3. **Otherwise:** search (2.3). Rate limit: `fell.maxSnapshotsPerSecond` (10) per player.

**Commit (step 2, not cancelled; `bInOther` is from step 1):**
1. Drop the snapshot if:
   - `needLeaves` and not `leafSeen`;
   - there are no claims;
   - the player already has `fell.maxWatchesPerPlayer` (4) live watches;
   - the server already has `fell.maxWatches` (64).
2. For each claim `k`, look at the current holder `h = CLAIMS.get(k)`. Take it (`CLAIMS.put(k, W)`) if:
   - `h` is null or no longer live; or
   - `h` belongs to the same player (the newest watch wins); or
   - `h` is another player's and `!bInOther`: this player cut a support outside the other player's falling part, e.g. the last base log of a partly cut 2x2, so their cut is the one that made those logs fall.

   Otherwise keep the other player's claim.
3. Put every layer key into `LAYER` -> `W`. Schedule the first poll.

**Rules for Skyy (plain):**
- A log that falls is paid to the player whose break took away its last support.
- A log someone breaks by hand is paid to them as a hand break, never also as felled.
- Nobody is paid twice for one log.

### 2.5 The watch (step 3)

For each unresolved claimed position, read `idx = BlockSection.get(x, y, z)` on the world thread. The read never loads a chunk; -1 means not loaded.

| Read | Meaning | Action |
|---|---|---|
| -1 | chunk not loaded | resolve, no credit ("lost") |
| same index as the snapshot | still standing | wait |
| 0 (empty; physics treats index 0 as nothing) | removed | resolve; `lastChange = now`; credit **only if** `CLAIMS.get(k) == this` (so not hand-broken, not taken over), then `CLAIMS.remove(k, this)` |
| any other index | replaced | resolve, no credit |

The watch ends when any of these is true:
- every position is resolved;
- `now - lastChange >= fell.quietMs` (3000; `lastChange` also moves on creation and on `touch()`);
- `now - created >= fell.maxWatchMs` (60000);
- the owner went offline.

On end:
- release this watch's remaining `CLAIMS` / `LAYER` entries (`remove(k, this)`);
- lower the player's watch count;
- optional chat summary (2.9);
- with `fell.debug`, one server-log line: player, world, claims, credited, hand, lost, other, duration in ms. It exists to measure the UNVERIFIED cascade timing.

### 2.6 What one felled position pays (step 4, `FellCredit.one`)

Preconditions, all checked at credit time:
- the owner is online (`Universe.get().getPlayer(u)` is valid);
- `SkillStore.pkey(u)` equals the snapshot's pkey (a profile switch mid-fall drops the credit, like `CraftTask`);
- no `profile:busy:<uuid>`;
- the owner is still in the tree's world;
- the owner is not in creative.

`bt = BlockType.getAssetMap().getAsset(idx)`. Then:

1. **XP.**
   - `rule = SkillCfg.classifyBreak(bt)`: the same table as a hand break, already scaled by the global multiplier.
   - If `rule != null && rule[2] == 1`: `xp = round(rule[1] x (leaf ? fell.leafXpFactor : fell.xpFactor))`, then `SkillXp.gain(pr, (int) rule[0], xp)`. This path applies the skill-tree bonus, so **Foraging Wisdom counts**, and it feeds the normal "+XP" chat aggregator.
2. **Double drop** (`fell.doubleDrops`): `Perks.breakDouble(pr, row, bt, world, true)`.
   - The level chance plus `dd.foraging` (Foraging Fortune I/II) apply, capped by `perk.doubleDropMax`.
   - `perk.foraging.doubleDropOnly=_Trunk` keeps it to trunks.
   - It uses the Breaking drops. For every tree wood these equal the Physics drops: VERIFIED for Oak and Branch_Long (Physics = Breaking), and the other woods have no Physics entry, so the engine uses Breaking too.
3. **Collections** (`fell.collections`): `FellDrops.roll(bt)` is the **engine's physics selection** (1.3 step 3: Physics, else Breaking, else Soft, else Harvest) followed by `BlockHarvestUtils.getDrops(bt, qty, itemId, dropListId)`. For every stack, call `coll:fn:add.apply(new Object[]{u, itemId, Long.valueOf(qty), "skills:felled", pkey})`. A refusal is dropped silently and counted in the debug line.
   - This is the same re-roll model that H1 uses for hand breaks.
   - Trunks drop their own log (deterministic), so the count is exact.
4. **Per-log nodes** (`fell.nodes`, only when `rule != null`): `SkillBonus.felled(pr, row, bt, world, x, y, z, pkey)` calls every Function in the new map `skill:on:felled` (2.8). Abilities never run from it.
5. **Memory:** `FELLED.put(k, {u, pkey, now, bt.getId()})` for `skill:fn:felledBy`.

A `rule == null` block (e.g. a wood set to `none`) still counts in Collections, like H1. It gets no XP, double drop or nodes, like `BreakTask`.

### 2.7 Leaves

- The XP table pays `Plant_Leaves_` 1 Foraging XP for a hand break. VERIFIED (line 453).
- Felled leaves pay the same table x `fell.leafXpFactor` (default **1.0**, per this task's rule "no XP unless the table pays for them").
- Set `fell.leaves=false` to stop crediting leaves at all. That also skips most of the snapshot reads, since leaves are the biggest part of a tree. `[SKYY?]`
- No double drop (`doubleDropOnly=_Trunk`) and no nodes: `TreeGather` only rolls on `_Trunk` ids.
- Collections: the Physics drop list is re-rolled, like H1 re-rolls leaf drop lists. That list is mostly nothing, sometimes fibre, and a sapling with Saplings From Trees. Only items in the collections registry count.
- Leaves can stay up when another tree's trunk supports them; the watch pays only those that really go.

### 2.8 Bridge additions (SkyySkills 0.4.2)

- **`skill:on:felled`**: a `ConcurrentHashMap` name -> Function, created with `putIfAbsent` in setup (like `skill:on:gather`).
  - Called on the world thread, once per credited position, after XP and the double drop.
  - Argument: `Object[]{PlayerRef, Integer row, BlockType, String world, Integer x, Integer y, Integer z, String pkey}`.
  - Every listener runs in its own try/catch, and a failure is logged once per listener (`SkillBonus.failed` pattern).
  - It is a **separate** map from `skill:on:gather`, so an old SkyyTrees (0.1 / 0.2) never sees felled logs and can never start an ability from one.
- **`skill:fn:felledBy`**: a Function, any thread.
  - Argument: `Object[]{String world, Integer x, Integer y, Integer z}`.
  - Returns `Object[]{UUID owner, String pkey, Long atMillis, String state}`: state is `"falling"` (claimed by a live watch; atMillis = snapshot time) or `"felled"` (in `FELLED`); otherwise null.
  - For other mods (pickups, minions, logs, quests). Remove it in shutdown.
- **Optional, recommended in the same build:** in `Perks.doubled`, also call `coll:fn:add` with the source `"skills:double"` for each double-drop stack. Collections 0.2 already accepts that source by default (line 270). A VERIFIED grep shows SkyySkills 0.4 never calls `coll:fn:add`, so double drops are not counted in Collections today, for hand breaks either. `[SKYY?]`

### 2.9 Chat

- XP arrives through `SkillXp.gain`, so the existing aggregated "+N Foraging XP" line (feedbackMs, `/skills quiet`) shows it as the tree comes down.
- With `fell.message=true`, one summary line when the watch ends and at least 1 log was credited: `Tree felled: 19 logs, 42 leaves (+156 Foraging XP)`. `/skills quiet` hides it.
- Later: gate the summary through the Settings registry (research/Settings-Spec.md).

### 2.10 What is deliberately NOT built

HANDOFF 07:25 floated "count walk-over pickups of world-dropped items". This spec replaces that with credit-at-fall, for four reasons:
1. There is no VERIFIED hook for ground pickups. Collections 0.2: "ground pickups never fire InteractivelyPickupItemEvent".
2. Telling thrown items apart from world drops needs item-entity data that is UNVERIFIED.
3. It would count hand-broken drops twice: H1 counts them at the break.
4. It would credit the picker, not the feller.

Credit-at-fall is exactly the H1 model. `skill:fn:felledBy` keeps a pickup design possible later.

---

## 3. Where each part is built

### 3.1 SkyySkills 0.4.2 (patch on 0.4.1)

**New classes.** Add them in dependency order, with no lambdas, generics, enhanced-for or inner classes (the javassist rules):
- `FellCfg`
- `FellDefs`
- `FellSnap`
- `FellWatch implements Runnable`
- `Fell` (maps and static helpers)
- `FellDrops`
- `FellCredit`
- `FelledByFn implements Function`
- `SkillBonus.felled` (a method on the existing class)

**Hook 1: `BreakSys` handler** (line ~3843). Insert after `w` is resolved and before `classifyBreak`:
```java
Object fs = null; Object unclaimed = null;
if (FellCfg.ENABLED && FellCfg.worldOk(w.getName()) && !SkillXp.creative(st, r)) {
  V3I t = e.getTargetBlock();
  if (t != null) {
    Object[] hc = Fell.onBreak(w.getName(), pr.getUuid(), t.x(), t.y(), t.z()); // {unclaimedWatch, Boolean inOther, Boolean reused}
    unclaimed = hc[0];
    if (!((Boolean) hc[2]).booleanValue())
      fs = Fell.snapshot(w, pr.getUuid(), SkillStore.pkey(pr.getUuid()), e.getBlockType(), t.x(), t.y(), t.z(), ((Boolean) hc[1]).booleanValue());
  }
}
```
- Pass `fs` and `unclaimed` to `BreakTask` (two new fields and a new constructor).
- The early `return` for `rule == null && !IGNORE_PLACED` must not skip a `BreakTask` while `fs != null || unclaimed != null`.
- Wrap all of this in its own try/catch that warns once. A snapshot failure must never stop the XP path.

**Hook 2: `BreakTask.run`** (line ~3637):
```java
if (this.ev.isCancelled()) { Fell.restore(this.world, this.ev, this.unclaimed); return; }
if (this.fs != null) Fell.commit((FellSnap) this.fs);   // BEFORE XP and SkillBonus.gather (the Tree Feller breaks inside gather)
... existing body unchanged ...
```

**Block reads.**
- `Fell.indexAt(World w, int x, int y, int z)`: the `SkillCfg.blockIdAt` read path, returning `sec.get(x, y, z)` or -1.
- `Fell.deco(...)`: `ChunkStore.getChunkSectionReferenceAtBlock(x, y, z)`, then `store.getComponent(sr, BlockPhysics.getComponentType())`, then `bp != null && bp.isDeco(x, y, z)`. `isDeco` masks the coordinates itself (`ChunkUtil.indexBlock`); VERIFIED.
- `Fell.natural(wn, x, y, z)` = `!PlacedStore.contains(wn, key) && !deco`.
- Reading chunk sections inside the event handler is UNVERIFIED in play. The engine reads the same sections in the same call right after the event (1.1), and `SkillCfg.blockIdAt` uses this path from world tasks today. Test T1 checks it.
- **Fallback if a handler read ever throws:** take the snapshot in `BreakTask` instead, and let the wood search step through up to 2 empty cells straight above the seed. A late snapshot can then still reach the rest of the tree.

**The watch** (sketch; the HarvestTask hop pattern, VERIFIED at lines 3693-3725):
```java
public void run() {
  if (this.hop) { this.hop = false; try { this.w.execute(this); } catch (Throwable t) { Fell.end(this); } return; }
  long now = System.currentTimeMillis();
  for (int i = 0; i < this.n; i++) {
    if (this.done[i]) continue;
    int cur = Fell.indexAt(this.w, this.x[i], this.y[i], this.z[i]);
    if (cur == this.idx[i]) continue;
    this.done[i] = true; this.left--; this.lastChange = now;
    if (cur != 0) continue;                                        // -1 not loaded / other block: no proof of a fall
    Long k = Long.valueOf(this.key[i]);
    if (Fell.claims(this.wn).get(k) != this) continue;            // hand-broken or taken over
    Fell.claims(this.wn).remove(k, this);
    FellCredit.one(this, i);
  }
  if (this.left <= 0 || now - this.lastChange >= FellCfg.QUIET_MS || now - this.created >= FellCfg.MAX_WATCH_MS || !Fell.online(this.u)) { Fell.end(this); return; }
  this.hop = true;
  HytaleServer.SCHEDULED_EXECUTOR.schedule(this, FellCfg.POLL_MS, java.util.concurrent.TimeUnit.MILLISECONDS);
}
```

**Config.** Add an `xp.properties` block, appended once to an existing file (`FellCfg.ensureDefaults`, the AlchCfg / SmithCfg / BridgeCfg pattern), and re-read by `/skills reload`:
```
# ---------- Felled trees (SkyySkills 0.4.2): every log that falls because you cut the tree pays like a hand-broken log ----------
fell.enabled=true
fell.xpFactor=1.0
fell.leaves=true
fell.leafXpFactor=1.0
fell.needLeaves=true
fell.underTrunk=true
fell.doubleDrops=true
fell.collections=true
fell.nodes=true
fell.message=true
fell.disabledWorlds=
fell.radius=8
fell.height=64
fell.maxLogs=256
fell.maxLeaves=384
fell.maxReads=8000
fell.maxSnapshotsPerSecond=10
fell.maxWatchesPerPlayer=4
fell.maxWatches=64
fell.pollMs=200
fell.quietMs=3000
fell.maxWatchMs=60000
fell.memoryMs=60000
fell.debug=false
```
Clamps:
- `pollMs`: 50-1000
- `quietMs`: 500-10000
- `radius`: 1-16
- `height`: 1-128
- `maxLogs`: 1-1024
- `maxLeaves`: 0-2048
- factors: 0-5

**Setup and shutdown.**
- In setup: `bridge().putIfAbsent("skill:on:felled", new ConcurrentHashMap())` and `bridge().put("skill:fn:felledBy", new FelledByFn())`.
- In shutdown: remove `skill:fn:felledBy` and end every live watch (release its claims). Leave the listener map in place, like `skill:on:gather`.

**Small related fix, recommended.** `PlaceTask` records every placed position, including saplings. When a sapling grows into a tree, the base trunk may sit on that recorded position (UNVERIFIED), and then the hand-broken base of a replanted tree pays 0.

Fix: skip recording when `ev.getItemInHand()` has an id starting with `Plant_Sapling_`. `PlaceBlockEvent.getItemInHand()` is VERIFIED. Saplings pay nothing when broken, so this opens no exploit. Apply the same change to SkyyCollections' H4. `[SKYY?]`

### 3.2 SkyyCollections 0.2.1 (patch on 0.2)

- `CollReg.loadConfig` (line ~854): after reading `bridge.add.sources`, add `skills:felled` unless `bridge.add.felled=false`. No file rewrite is needed; an existing `config.properties` gains the source automatically.
- Add the new default lines to `configText()`:
  - `# skills:felled = logs that fall when you cut a tree (SkyySkills 0.4.2)`
  - `bridge.add.sources=skills:double,skills:felled`
- Nothing else. The per-credit and per-minute caps and the profile check (`expectKey`) already apply (`CollFn` "add", `CollAddTask`, `creditOne`). VERIFIED at lines 2244-2270 and 1674+.
- Works with Collections 0.2 today if an admin adds `skills:felled` to `bridge.add.sources` by hand. VERIFIED from code.
- Also in this build, per HANDOFF: 'Tier -' -> 'No tier yet' (not part of this spec).

### 3.3 SkyyTrees 0.2.1 (patch on 0.2): the Tree Feller rework

**Node.** `("FFeller", "Tree Feller", "Tool_Hatchet_Adamantite", "FELLER", 5, per 1.0, base 0.0, ...)`:
- now text: `"Breaks %V more logs beside it on the same level"`;
- how text: `"On a log that pays Foraging XP - same Y level only; Hytale fells the tree once a whole layer is cut - cooldown %C s"`.

The level curve is **1, 2, 3, 4, then every log of that tree on that layer**:
- a 2x2 tree needs level 3;
- a 3x3 needs level 5.

`TreeFx.value` for `K_FELLER`:
```java
if (eff >= TreeCfg.MAX[i]) return (double) TreeCfg.FELLER_ALL; return TreeCfg.BASE[i] + per * (double) eff;
```
The page shows "every log on that level" at max (`%V` reads `FELLER_ALL` as "every").

**`TreeAbil.feller`** (line 1591):
1. `l = flatFlood(w, wn, x, y, z, fam, max, TreeCfg.RADIUS, pf)`. This is a breadth-first search on the same Y only:
   - neighbour order `(1,0) (-1,0) (0,1) (0,-1)` first, then the four diagonals, so level 1 takes the log directly beside the cut;
   - `|dx|, |dz| <= RADIUS`;
   - ids starting with `logFamily(id)` (`Wood_<W>_Trunk`, so Trunk and Trunk_Full);
   - not `recent`, not placed (`skill:fn:placed`);
   - cap `max`, at most 4000 reads.
2. If `l` is empty, return false (no cooldown).
3. If `FELLER_LEAVES`, run the existing `flood(w, wn, x, y, z, fam, true, 0, 256, RADIUS, FELLER_H, leaves, pf)` as a **read-only** natural-tree check. With `max=0` it breaks nothing and only sets `leaves[0]`. If no leaves, return false.
   - It stays valid here: a partial cut of a thick tree fells nothing, so the tree is still intact when TreeGather runs.
   - `feller.maxHeight` now means only "how high to look for leaves".
4. `n = breakList(...)`. This is unchanged: `performBlockBreak`, one real `BreakBlockEvent` per log.
5. Cooldown, then `"Tree Feller! +n logs on this level"`.

**Why this combines cleanly with crediting:**
- Every Feller log is a real hand break: XP, double drop and Collections H1 as today.
- In SkyySkills each of those breaks is a `LAYER` member of the first watch, so no new search runs.
- Once the layer is gone, the engine fells everything above, and the first watch credits those logs.
- There is no vertical reach any more, so no log is ever both broken by the Feller and felled.
- No chains: `recent` marks, plus felled logs arriving on `skill:on:felled`, which never runs abilities.

**Config (`trees.properties`).** Use the 0.2 `TreeCfg.has02` / append-once pattern:
- New: `feller.maxPerLayer=64` (clamp 1-256), stored as `TreeCfg.FELLER_ALL`.
- `feller.cooldownSec` default **5** (was 30) `[SKYY?]`. At 30 s a level-1 Feller is nearly useless.
- A one-time migration rewrites the old default lines when they are unchanged:
  - `Foraging.FFeller.per=8.0` -> `1.0`;
  - `Foraging.FFeller.base=8.0` -> `0.0`;
  - `feller.cooldownSec=30` -> `5`.

  Custom values are kept, with a server-log line warning that `per`/`base` now count logs on one level.

**Felled-log node rolls.**
- Register `"trees"` in `skill:on:felled`: `putIfAbsent` the map, and re-check every 5 s exactly like `skill:on:gather`.
- `TreeGather.felled(pr, row, bt, wn, x, y, z)`:
  - return if `TreeStore.busy(u)`, `row != 1`, or the id does not contain `_Trunk`;
  - roll `FSAP` (Sap Tapper), `FSAPLING` (Replanter) and `FCOINS` (Pocket Change) with the same code as `run`;
  - **never** Spread / Vein / Feller.
- `trees.properties` key `felled.nodes=true`.
- Foraging Wisdom and Fortune need nothing here: SkyySkills applies them (2.6).

**Spread.** Timber Spread is unchanged. If Spread breaks a log of a falling tree, it is a hand break and that log is unclaimed (2.4), so it is never paid twice.

### 3.4 Deploy pairing (every mix is safe)

| SkyySkills | SkyyTrees | SkyyCollections | Result |
|---|---|---|---|
| 0.4.2 | 0.2.1 | 0.2.1 | full design |
| 0.4.2 | 0.1 / 0.2 | any | felled XP, double drops and counts work; no per-log Sap / Replanter / Coins; the old vertical Feller's breaks are hand breaks and the rest is felled, with no double pay |
| 0.4.2 | any | 0.2 | no felled counts unless `skills:felled` is added to `bridge.add.sources` |
| 0.4 / 0.4.1 | 0.2.1 | any | the new Feller works; felled logs still unpaid (today's behaviour) |

---

## 4. Anti-exploit and performance

### 4.1 Exploits considered

| Attempt | Why it pays nothing extra |
|---|---|
| Place a log tower, break its base | Placed trunks are deco (1.4), so the engine never lets them fall. They are also skipped as placed or deco in the snapshot, and there are no natural leaves, so `needLeaves` fails. Test T4. |
| Stack placed logs on a natural stump or tree | They do not fall (deco) and they are never claims. |
| Grow, fell, replant loop (Replanter, Saplings From Trees) | This is the intended sky-island loop. Each natural log is removed once, so it pays once, and sapling growth time is the gate. Replanter rolls per felled trunk exactly as it does per hand-broken trunk. `[SKYY?]` if saplings become too plentiful: `fell.nodes` or the Replanter numbers. |
| Cut by hand and let it fall, to be paid twice | A hand break removes the claim before removal (2.4), so the watch skips that position. |
| Two players, one tree | One claim per position (2.4). The last-support rule decides; there is never a double payment. |
| Break protected island blocks as a visitor | Cancelled, so nothing is removed or falls, and the snapshot is discarded at commit. |
| Creative | No snapshot. Creative with noPhysics also fells nothing (1.1). |
| Profile switch mid-fall | pkey check at credit time; `coll:fn:add` `expectKey`. |
| Spam trunk-adjacent breaks to load the server | `maxSnapshotsPerSecond`, `maxReads`, `maxWatchesPerPlayer`, `maxWatches`, and reuse of a live watch. |
| Explosion or fire inside a live watch | A removal within the watch window is credited to the feller. That is minor and bounded by the tree. |
| TreeHarvester-style silent breaks (not in the pack) | Silent `World.breakBlock` removals inside a watch count as felled, which is correct: the player cut that tree. |

### 4.2 Performance budget

- **Snapshot:** at most 8000 section-cached reads, synchronous in the break path. A 20-log birch with about 60 leaves is roughly 2000 reads. UNVERIFIED cost; T14 logs it.
- **Watch:** at most 640 positions x 5 polls per second, usually over 1-5 s. A position is dropped from the loop once resolved.
- **Memory:** `FELLED` holds at most 8192 entries per world with a 60 s TTL. Claims live only as long as a watch.
- **Cheap for everything else:** a non-tree break costs one `blockIdAt(y+1)` (the UNDER test) and one `CLAIMS` lookup.

---

## 5. Test checklist (Skyy, in game; two accounts where marked)

**T1. Normal 1-wide tree (birch).** Break the base with no Tree Feller. Expect:
- the tree falls as before;
- about 20 x 6 = 120 Foraging XP, plus about 1 per leaf, shown in the "+XP" lines;
- Birch Log collection +20 (Skyy's data point: was +1);
- the server log shows no `fell` warning;
- with `fell.debug=true`, one line with credited / hand / lost counts and ms.

**T2. Double drops.** With Foraging level at least 10, some felled logs give "Double drop!" items into the inventory.

**T3. Nodes.** With Sap Tapper, Replanter and Pocket Change owned, they roll on felled trunks: "Tree bonus" lines appear.

**T4. Placed tower.** Place 5 birch logs in a column on grass, then break the bottom one. Expect: the other 4 stay floating (vanilla deco), and 0 XP for all of them.

**T5. Placed on natural.** Place 3 logs on top of a natural tree, then fell it. Expect: the natural logs pay; the placed ones float or stay and never pay.

**T6. 2x2 tree without the Feller.** Break 1 base log: nothing falls, 6 XP. Break the other 3 one at a time within a minute: the tree falls after the last one, and every log above is paid.

**T7. Tree Feller.**
- Level 1 on a 2x2: breaks 1 log beside the cut on the same Y, nothing falls.
- Level 3 on a 2x2: the whole layer is cut, the tree falls, everything is paid, and XP is not doubled for the layer logs.
- Level 5 on a 3x3 or wider tree: the whole layer is cut.
- Nothing is ever broken above or below the cut level.

**T8. Two accounts, A and B.**
- A cuts a 1-wide tree. While it falls, B breaks a log higher up: B gets that 1 log, A gets the rest.
- A cuts 3 base logs of a 2x2, then B cuts the last one: B gets the tree.

**T9. Island visitor (two accounts).** A visitor hits a tree on someone else's island: cancelled, nothing falls, no XP or counts.

**T10. Creative.** Creative with physics on (tree falls) and with noPhysics (nothing falls): 0 XP both times.

**T11. Profile switch.** Cut a tall tree and switch profile at once (`/profile`): no felled credit on the new profile.

**T12. Dirt under trunk.** Dig out the grass or dirt block under a 1-wide tree: the tree falls, all logs are paid (`fell.underTrunk`).

**T13. Replanted tree.** Plant a sapling, let it grow, and fell it. Expect: the logs above the base pay. Note whether the base log pays: it pays 0 until the `PlaceTask` sapling fix (3.1).

**T14. Timing and cost.** With `fell.debug=true`, fell a tall thick tree. Note the ms from the debug line, and that the server stays smooth. If the fall takes longer than `quietMs` between two removals, raise `fell.quietMs`.

**T15. Chunk edge.** Fell a tree standing across a chunk border: all logs are paid, or some are counted "lost" in the debug line, and nothing is paid twice.

**T16. Reload.** `/skills reload` after setting `fell.leaves=false`: leaves stop paying and logs still pay.

---

## 6. Open choices for Skyy

1. `fell.xpFactor` = 1.0: felled logs pay exactly like hand-broken ones. Lower it if trees become too fast a Foraging source. `[SKYY?]`
2. Leaf XP on felled trees: on at 1 XP each (the hand table) or off (`fell.leaves=false`, also cheaper on the server). `[SKYY?]`
3. Tree Feller level curve 1 / 2 / 3 / 4 / whole layer, and a 5 s cooldown (was 30 s). `[SKYY?]`
4. Shared-tree rule: the player who removes the last support gets the fall (2.4). `[SKYY?]`
5. Count double-drop items in Collections (`skills:double`, SkyySkills 0.4.2 one-liner, affects hand breaks too). `[SKYY?]`
6. The sapling placed-tracker fix (3.1) so the base log of a replanted tree pays. `[SKYY?]`

---

## 7. Sources

**`HytaleServer.jar` (bytecode read 2026-09-24):**
- `BlockHarvestUtils.performBlockBreak` (all overloads), `naturallyRemoveBlockByPhysics`, `getDrops` usage;
- `BlockInteractionUtils.isNoPhysics`, `isNaturalAction`;
- `BlockPhysicsSystems$Ticking.tick` and `lambda$tick$0`;
- `BlockPhysicsUtil.applyBlockPhysics`, `testBlockPhysicsAtPosition`, constants `IGNORE -1`, `SATISFIES_SUPPORT -2`, `WAITING_CHUNK -3`, `DOESNT_SATISFY 0`;
- `RequiredBlockFaceSupport` constructors (defaults REQUIRED / propagation true);
- `BlockPhysics.isDeco`, `get`, `IS_DECO_VALUE 15`;
- `BlockPlaceUtils.tryPlaceBlock` (`markDeco` condition), `BlockType.canBePlacedAsDeco`;
- `BlockType` codec (`Gathering`, `IgnoreSupportWhenPlaced` = `appendInherited`), `BlockGathering` codec (Physics / Breaking / Soft / Harvest / Tools = `append`, UseDefaultDropWhenPlaced = `appendInherited`);
- `PlaceBlockEvent` / `BreakBlockEvent` API; `ChunkStore.getChunkSectionReferenceAtBlock`.

**`Assets.zip`:**
- `Wood_Oak_Trunk`, `Wood_Birch_Trunk`, `Wood_Birch_Trunk_Full`, `Wood_Oak_Trunk_Full`, `Wood_Oak_Branch_Long` / `Short` / `Corner`, `Wood_Oak_Roots`, `Plant_Leaves_Oak`, `Plant_Leaves_Birch`;
- the 129 trunk files that override only Breaking; Maple `MaxSupportDistance 8`;
- `Server/BlockTypeList/TreeWood.json` (183), `TreeLeaves.json` (44);
- `Server/Drops/Wood/Tree_Leaves.json`, `Tree_Leaves_Physics.json`, `Wood_Branch.json`.

**Mods folder (read only):**
- `SaplingFromTrees-1.0.4.zip` (leaf overrides + template);
- `vein-mining-2.4.0.jar` `MiningManager.isDecoBlock`;
- `treeharvester` / `hybrid` and `MMOSkillTree-1.6.0.jar` constant pools.

**Our scripts:**
- `SkyySkills/build_skyyskills_0.4.py`: BreakSys 3843, BreakTask 3637, HarvestTask hop 3693-3725, PlacedStore 3497, classifyBreak 1582, blockIdAt 1558, `SkillBonus.gather` 2438, gain 2465, breakDouble 2888, XP table 452-465;
- `SkyyCollections/build_skyycollections_0.2.py`: docstring H1-H5, `bridge.add.sources` 270 / 854, `CollFn` add 2244, creditOne 1674;
- `SkyyTrees/build_skyytrees_0.1.py`: node table 306, `TreeFx.value` 1144, flood 1472, breakList 1531, feller 1591, TreeGather 1690+, config 372-374 / 626 / 710-714;
- `SkyyIslands/build_skyyislands_0.4.4.py` GuardDamage / GuardBreak;
- `tools/PROFILES-CONTRACT.md` pkey;
- `tools/trees_0_2_patch.py` (0.2 leaves the Foraging tree unchanged).

**In game (Skyy, 2026-09-24):** a tree falls when its base is cut; one birch = 20 logs dropped, 1 counted, 6 XP.
