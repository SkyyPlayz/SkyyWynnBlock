# SkyyMinions — plan

> **Skyy's decisions 2026-10-02 win over this draft:** OPEN-QUESTIONS.md, section "Q&A with Skyy 2026-10-02", rounds 7.
*Design lock 2026-09-23 night. See `SkyWynn-Master-Plan.md` Part 2B and 2E (P2), and `SkyWynn-Decisions.md` rows 3.3–3.7.*

## Where they live

Minions live on the **private island** (`SkyyIslands-Plan.md`). That island is the progression home and the free building space. Minions are one of the progression systems there, next to upgrades, co-op, and size tiers.

## How required they are

Helpful, **not mandatory**. They are AFK help for materials you have already reached. You can finish the island chain, quests, and the capstone dungeon without placing one.

They do not gate zone unlocks, class skills, or collections. Skipping them is slower, not blocked.

## What we already decided to take

Unchanged by the call, still the minion design:

- Offline generators with tiers
- Upgrades: fuel, storage, compactor
- Hoppers that auto-sell — watch inflation on a public server
- Slots earned by crafting unique minions
- Minion items count toward collections; bazaar-bought items never do

The Garden is **parked** (row 3.8, 2026-09-24): it is not where farming happens for now. Farming stays on the private island and the zone islands. Minions are not a stand-in for the Garden, and they are still not required.

## Pocket Shards (Skyy 2026-10-01 - the themed form of minions)

Skyy: "something similar to the skyblock minions, but keeping it in theme ... a mini shard, or a pocket shard. (a little block you place
with its own mini shard inside, that collects the resource. (same concept as the minions, similar upgrades, BUT it only takes 1 block
instead of a big area, and it fits the theme.)" Story: research/Isles-of-the-Void-Lore.md.

- **One block.** You place a Pocket Shard block; a tiny floating shard is visible inside it (a custom block model - an orb or frame with a
  mini island). It never breaks or places blocks in the world: it simulates the work, so it needs no 5x5 area.
- **One resource per type** (an Oak Pocket Shard, a Copper Pocket Shard, a Wheat Pocket Shard, a Zombie Pocket Shard, ...), the
  SkyBlock minion list as the starting point.
- **Same concept as minions:** tiers (SkyBlock uses I-XI; faster and more storage per tier), fuel, upgrades (compactor, auto-smelter,
  storage), items count toward Collections (Bazaar-bought never do - existing lock), more slots by crafting unique Pocket Shards
  (existing lock), auto-sell later (watch inflation).
- **Works offline:** it counts the time since it last ran (chunk load / island visit) and adds what it would have made, up to its storage.
- Still helpful, **not mandatory** (lock above). Lives on your personal island.
- Row 9.10 (minions vs Hytale's Chapter-2 Companions): answered for now - Pocket Shards are our own block system, not built on
  Hytale's Companions (our pets are a separate system too: research/Pets-Idea.md).
- Engine research needed before a plan: a custom block with a block entity + inventory, a custom model, and offline time accounting.

## What this plan does not decide

Row 9.10 is still open: whether minions stay a custom system or eventually ride Chapter 2 Companions. Until that row is locked, minions mean island resource automation, and companions mean vanilla homestead chores. This doc does not pick new minion types or tier counts beyond the phase note in the master plan (first minion types in P2).
