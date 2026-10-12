# Shard Islands + farming totems (idea) - Skyy 2026-10-11

Skyy's words are in `docs/answered/skills.md` (2026-10-11 SHARD ISLANDS and FARMING TOTEM IDEAS). This REPLACES the "Pocket Shard =
minion block" idea in `research/cloud/Pocket-Shards-Spec.md` (that spec must be revised before anything is built). Not designed yet.

## Shards = mini islands (our version of minions + the SkyBlock Garden)

- A **shard** placed on your island is a **portal** to a private mini island you can only reach through it.
- **Farming shard:** starts with ONE small wheat island and ONE T1 **Harvest Spirit** totem. The farm is bigger than the spirit's range,
  so you can go in and farm by hand until you upgrade.
- **All plants in a shard are eternal** (no replanting); upgrades cost **Eternal Seeds** (+ other items).
- **Upgrade the island** to make it bigger: 3 levels at launch.
- **Buy a new island** inside the shard for a new crop, upgrade it with that crop + other items, then automate it the same way.
- **Craft + upgrade totems** to automate and improve each island.
- The overworld still has farming, mining and tree gathering, but **developing your shards is the ONLY way to get automation** - minions
  become their own minigame.

## Shards 2 (same day)

- **Mining and Foraging get their own shards too** (plus Farming, Ranching, Orchard).
- **Collections + skill XP are gained when you COLLECT** from the shard, so each shard has its **own menu**:
  - **Collect** what it produced;
  - **shard upgrades**: auto-compactor (like SkyBlock), time compressor (time runs faster in the shard = more per minute);
  - **Islands**: add islands and upgrade them.
- **Protected:** no building or breaking blocks in a shard - you can only farm / gather and place / remove totems.
- **Layout = fixed slots around a hub:** a small hub island (portal + menu) with fixed slots around it; any island in any slot; one
  pre-made bridge per slot that appears when the slot is filled; each island grows in place (3 sizes per slot). No order lock.
- **The same shard menu opens from the portal on your main island** (right-click, like a vanilla portal's menu) - our own custom
  design, and it needs a really cool one (Sky Window kit).

## Three farming skills, one tree

- **Farming, Ranching and Orchard** each get their **own shard and their own skill**.
- Your **Farming level = the average of the 3**; they share ONE Farming skill tree.
- They must be balanced so each has a clear progression path, and they help each other (plan this together).

## Totem poles (all wanted)

| Totem | Does |
|---|---|
| Rain | waters crops in its area (handheld Rain Totem: click = rain, costs Mana) |
| Fertilizer | growth boost; stronger per tier |
| Blessing of the Sun | sunlight / growth boost |
| Fairy Grove | tiny fairies - drifting dots of light that light up the garden and help it grow faster |
| Season Ward | crops keep growing out of season (Dynamic Seasons winter), no freezing |
| Scarecrow / Guardian | keeps crop-eating mobs and birds out, no trampling |
| Pollinator (bees) | chance for rare crop mutations / variants |
| Harvest Spirit | auto-harvests ripe crops into a linked chest / Void bag (the shard's starting totem) |
| Harvest Moon | extra crops at night, plus an EXTREMELY low chance of an Enchanted crop (boosted by a Moon Blade modifier on scythes) |
| Compost | turns weeds, rotten food and spare drops into fertilizer |
| Herd / Ranch | animals: faster breeding, more wool / eggs / milk |
| Mushroom / Shade | shade crops + mushrooms grow at any light |

Rules locked the same day: Totem Poles need no fuel (optional booster fuel slot), tier up on the Anvil Upgrade tab with Enchanted materials,
plus 2 minion-style upgrade slots. Base model: MoreTotems' Water Totem (MIT, credit nagatwin).

Engine question for the spec: a private instanced island per player per shard (Hytale instances / per-player worlds), and how many can a
server hold. Related: `research/Gathering-Progression-Spec.md`, `research/cloud/Pocket-Shards-Spec.md`, `research/cloud/Starter-Shards-Plan-2.md`.
