# Starter shard chain - paper layout

Cloud draft, 2026-10-03. Paper design only; no prefab, no world edit. Matches the 12 quests in `research/cloud/Story-Script-Draft.md` and the lock **R8 (2026-10-02): the first gap has a broken bridge you repair; the later gaps you
build across with your own blocks**. Engine facts used: a chunk is 32 blocks (VERIFIED, `docs/plans/SkyyIslands-Plan.md`); the island template box defaults to 3 x 3 chunks (96 x 96 blocks), y 96-191 (LOCKED 2026-09-25);
the island world is a copied template, so extra shards live in the same world (lore note). Everything about spawns, protection and coordinates beyond that is a proposal.

## 0. At a glance

| Shard | Role | Size (radius) | Centre (x, y, z) | Quests | Mobs |
|---|---|---|---|---|---|
| **1 - Home shard** | Wake-up, gather, craft, farm, collections | 30 (about 60 wide) | (0, 140, 0) | 1-7 | none (safe) |
| **2 - Crude shard** | Crude armor, first fight | 14 (about 28 wide) | (56, 138, 0) | 8-9 | 9 weak hostile mobs |
| **3 - Toll shard** | Bridge camp, mini boss, the portal frame | 18 (about 36 wide) | (102, 142, 0) | 10-12 | 5 mobs + Warden Gumbo |

Gaps (edge to edge): **shard 1 -> 2 = 12 blocks (the broken bridge you repair)**; **shard 2 -> 3 = 14 blocks (you build it)**. Total length about 150 blocks along x (5 chunks): chunks (-1..4, -1..0) in the template.

## 1. The map (not to scale)

```
 y 140                                                 y 138               y 142
 ┌──────────── SHARD 1 ───────────┐                 ┌─ SHARD 2 ─┐          ┌──── SHARD 3 ────┐
 │  trees   pond      cave        │ ═ broken ═ gap ═│ bushes    │ ··build·· │ camp   toll hut  │
 │  ■■■     ~~~    ▲▲▲ (stone,    │   bridge  12    │  rocks    │   gap 14  │  ▲ portal frame  │
 │  Pebble   farm  ▲▲▲  copper)   │                 │  mobs ×9  │           │  mobs ×5 + Gumbo │
 │  chest  work-bench spot        │                 │  craft    │           │                  │
 └────────────────────────────────┘                 └───────────┘          └──────────────────┘
        (spawn, safe)                                    checkpoint A            checkpoint B
```
Below every shard the rock tapers into a cone about 14 blocks thick (a floating-island look); anything under y 96 is the Void (fall = respawn).

## 2. Shard 1 - Home shard (quests 1-7)

Bigger and more interesting than today's plain starter island (lore: "a few trees, a small cave with stone and copper").

| Feature | Position (relative to centre) | Details | Used by |
|---|---|---|---|
| **Spawn / Pebble's rock** | (0, 0) | grassy mound; Pebble sits here; the starter chest (existing kit) next to it | Q1 |
| Trees | NW quarter, 10-12 trees: 5 oak, 4 birch, 2 ash (a mix, because Collections tracks each log type) | at least 60 logs available, leaves drop Plant Fibre | Q2, armor recipe |
| Bushes | scattered, about 20 bushes | Plant Fibre and Sticks (about 15 fibre, 10 sticks), plus fibre from leaves | armor, rope |
| **Pond** | SW, 6 x 6, 2 deep | water for crops and a bucket | Q5 |
| **Farm patch** | S, flat 7 x 7 soil next to the pond | enough for 5 wheat, with 5 starter seeds from Pebble | Q5 |
| **Cave** | NE edge, entrance 3 x 3, tunnel 12 long, one room 7 x 7 | 40+ stone/cobble blocks, **8 copper ore** in a visible vein, 2 coal veins (fuel for the Smithing intro); torch brackets | Q4 |
| Rocks / rubble | 6 boulders around the east side | 15-20 Stone Rubble | armor recipe |
| **Workbench spot** | beside the chest | a marked flat area ("table goes here" sign) | Q3 |
| **Bridge landing (east edge)** | (30, 0) | the **broken bridge**: posts and a few planks stop 4 blocks out; the rest of the 12 blocks are missing | Q7 |
| Safe edges | rim | low fence of rock so nobody falls by accident; the Void below still respawns you | |
| Beds / respawn | a bed at the chest | respawn point for shard 1 | all |

Resources available vs needs (so the player never gets stuck):

| Need | Quest | Available |
|---|---|---|
| 10 logs | Q2 | 60+ |
| Workbench recipe (logs, sticks, fibre per vanilla) | Q3 | enough (UNVERIFIED recipe cost) |
| 20 cobble, 5 copper | Q4 | 40+ cobble, 8 copper |
| 5 wheat (needs seeds, soil, water, growth time) | Q5 | 5 seeds from Pebble, farm patch, pond |
| Bridge repair: about 24 planks + 8 sticks (or logs/stone) | Q7 | planks from the 60 logs |
| Crude armor set: 31 fibre, 11 sticks, 10 rubble, 2 logs | Q8 | fibre and sticks on shards 1 and 2, rubble on both |
| Bridge 2: about 3 wide x 14 long = 42 blocks (stone or planks) | Q10 | cobble from the cave + logs |

**Wheat growth time** is an UNVERIFIED risk (crops ripen over real time). Q5 is meant to run while the player does Q4/Q6; if growth is too slow, ship a starter "fast growth" patch or give the wheat in the chest (config row).

## 3. Shard 2 - Crude shard (quests 8-9)

| Feature | Details |
|---|---|
| **Landing** | the repaired bridge ends at a stone arch; a **checkpoint A** banner (respawn point after the player has crossed) |
| Craft corner | a ruined workbench-with-roof "Crude Smithy" (the Workbench from Q3 can be placed here too); 6 bushes and 8 rocks nearby for fibre and rubble |
| Crude armor Q8 | the player can craft the set right here from what is on the shard + what they carry |
| Mobs (Q9) | 9 weak hostiles in three groups of three (e.g. Skeleton_Fighter or vanilla Zone 1 spawn-start mobs), Lv 1-3 (`bands.islands` 1-3) |
| Fight area | a flat 14 x 14 arena ring with two low rock walls to hide behind |
| Edge | 12-gap west to shard 1 (repaired), 14-gap east to shard 3 (unbuilt) |

## 4. Shard 3 - Toll shard (quests 10-12)

| Feature | Details |
|---|---|
| **Landing** | the player builds across the 14-block gap (width 3 is enough); a small stone dock on shard 3's near edge |
| **Camp** | 5 Trork camp mobs around a fire (Trork Warriors Lv 3-5) guard the way; a tent and barrels (loot: a few coins, fibre) |
| **Toll hut** | a wooden booth with a lowered gate on the far side; **Warden Gumbo** (a Trork Warrior with boss scaling) stands in front. Level 6, health about x6 (placeholder; Mob-Levels `scale.role`) |
| **Portal frame** | a stone ring ("the one with the sad face") behind the hut, dead and dark until the Portal Shard is placed |
| Arena | 18-radius ring, two pillars, a ramp; no fall-off hazard for the fight (fence on three sides) |
| Reward | the Portal Shard drops from Gumbo; **checkpoint B** at the dock |
| Exit | portal opens to the Zone 1 temple (first warp unlocked) |
| Afterwards | the portal stays; the player can return to shard 1 any time; shards 2-3 remain as normal island areas |

## 5. Void, respawn and safety

| Rule | Value |
|---|---|
| Falling into the Void | respawn at the last checkpoint (shard 1 bed by default; checkpoint A after crossing, B after the dock). The lore text says "respawn on your starting shard" - keep that as the default, with checkpoints a **setting** (`starter.checkpoints`) |
| Fall damage | none on shard edges (fence); the Void respawn takes you without penalty on the starter island |
| Death | respawn at the checkpoint; the 10-25% coin loss still applies by default (starter coins are only 10,000; consider turning it off for the first chain - setting) |
| Mobs on shard 2/3 | despawn when the player leaves; respawn on return (until Gumbo is defeated; then camp mobs stay dead for a while) |
| Co-op / visitors | visitors can walk across; Gumbo's Portal Shard drops per profile (quest flag), not per visitor |

## 6. What is repairable vs buildable (the R8 lock)

| Gap | What the player does |
|---|---|
| 1 -> 2 (12 blocks) | **Repair**: ropes and planks - craft/gather "Bridge Repair Kit" items (about 24 planks, 8 sticks, 6 fibre) and place them on the marked broken sections (the posts show where). Teaches placing blocks without free building |
| 2 -> 3 (14 blocks) | **Build**: free building with your own stone/wood; teaches the building tools, uses the cobblestone from the cave |
| Later in the game | any further gaps (zone islands use portals, not bridges) |

Story script change: Quest 7 should read **"Bridge Repair"** (fix the broken bridge; Pebble: "That used to be a bridge. It had opinions.") and Quest 10 is the build one. I patched `Story-Script-Draft.md` accordingly.

## 7. Existing profiles and the `/island reset` rule

- Existing profiles skip the starter chain (a profile flag). Their island is unchanged.
- New profiles get the chain's island template (a **new template version**: `Server/Instances/SkyyIsland` extended with shards 2-3 and the repaired-bridge assets). Old template islands never change.
- `/island reset` (24 h cooldown, 3 confirms - LOCKED) rebuilds the personal island from the template: **it must not re-run the chain**, and must keep shards 2-3 intact if the profile finished the chain (decide: reset only shard 1's building area).
- Island size upgrades (3x3 -> 9x9) apply to shard 1's build box; shards 2-3 stay protected.

## 8. Build plan (for the local session)

| Step | Work |
|---|---|
| 1 | Add the chunks for shards 2-3 to the island template; generate with the existing prefab/placement code (`PrefabUtil.paste`) or hand-build once and copy |
| 2 | Place spawn markers/mob spawns for shards 2-3 (or script-spawn on entry) |
| 3 | Protect shards 2-3 (no breaking except the bridge sections) |
| 4 | Place the quest NPCs (Pebble, Gumbo) once the quest system exists; until then a sign/hologram |
| 5 | Checkpoints: either beds/banners with a respawn hook (SkyyIslands respawn code) |

## 9. For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | The template box (3x3 chunks) vs shards 2-3 outside it: how SkyyIslands limits building and what `bands.islands` does outside the box. |
| 2 | Hostile spawning on a copied island world: do vanilla environment spawns work on a hand-made island? (WorldGen plan stage 0 test 2 asks the same.) Fallback: script-spawn. |
| 3 | Respawn points: how to set a per-profile checkpoint (bed rules, `Player.setSpawn`?). |
| 4 | Wheat growth time and whether a seed item exists in the starter chest. |
| 5 | The vanilla Workbench recipe costs and whether armor recipes can sit on it (Crude armor design). |
| 6 | World height: y 96-191 box with the Void under y 96; confirm the Void respawn height setting. |
| 7 | A broken-bridge prefab (posts, half planks) and a Trork camp prefab exist in vanilla (Trork camps do) - reuse by reference, never commit. |

## 10. Questions for Skyy

1. Should shard 1 respawn after a Void fall always happen at the home shard (lore) or at the last checkpoint (my default)?
2. Is a 12-block repair and a 14-block build the right difficulty, or smaller gaps (6 and 10)?
3. Should the 10-25% death coin loss be off during the starter chain (new players have 10,000 coins)?
