# Shard Clicker + one page per skill - idea (2026-11-14)

Where this goes: `research/` (INDEX.md "research"). Skyy's words: `docs/answered/world.md` (2026-11-14 "SHARDS -> MENU CLICKER").
Status: IDEA, waiting on Skyy's picks. Replaces the visitable shard islands (research/Gathering-Shards-Spec.md, Shard-Islands-Ideas.md)
once built. Related: research/Inventory-Screen-Plan.md (12 tabs), research/ui-theme-art/ (Upgrade page = the first "one page per category").

## Skyy's idea in short
- One page per skill (from the Skills column): tools + armor at the top (Requip button), stats with that set, the skill tree, and the
  skill's mascot (farm ghost for Farming) whose card opens the shard mini-game.
- The mini-game is a clicker on one top-down island: click the tree / node; hits and drops use your real tool (breaking power, Fortune),
  less XP than the world. Upgrades: node size (drops), node count, spirit totem (auto-collect speed / amount), weather totem (= irrigation),
  island size (adds another base-level spirit pole), decorations (looks), next-tier island (next wood type, a bridge to click; zoom out to pick).

## How it can work in Hytale's custom UI (what is possible)
- A custom page cannot draw freely, but it can stack OUR pictures: island base per size step, trees / totems / spirits in fixed spots,
  decorations as overlays. Upgrading swaps pictures. Art is ours, built into the jar (no vanilla pixels in git).
- Every click is one message to the server and back (fast on a local world). A click shows a short shake / "+3 Oak Log" pop.
- Spirits "work" on a timer (one page update every ~1-2 s, not per frame) - cheap and smooth enough.
- Drops go into the shard's storage grid (round shard1: chest-like grid, no stack limit), then Collect -> inventory / Void.
- Offline: spirits keep collecting at the current offline rate (today 30-35 % for 10-12 h) - no change to the economy rules.

## Suggestions to make it better (defaults in [brackets])
1. Same loop for every gathering skill, one mascot each: Foraging tree, Mining rock / ore node, Farming crop plot, Fishing pond (click to
   reel), Combat training dummy (spirits fight -> mob drops). [Foraging first, then Farming, Mining, Fishing, Combat]
2. Keep the world the best place to level: clicks give 25 % of world XP, spirits give 0 XP; the clicker is the best IDLE material source.
   Click cap ~8 counted clicks / s so auto-clickers don't win. [25 % / 0 % / 8 per s]
3. Short upgrade list per island (6 tracks): Node size, Node count, Spirit totem (speed + amount), Weather totem (regrow speed), Island
   size (adds a pole + node spots), Decorations (looks + a tiny bonus at max). Costs = coins + that skill's Enchanted materials (a sink).
4. Lucky moments to keep clicking fun: a golden tree / rich vein now and then (x5 drops, 15 s), a "spirit treat" boost from the mascot.
5. Islands unlock by tier like the world (T1 Oak -> T2 Beech -> ...) and need the same skill level / collection as the world tier.
6. Today's shard islands: existing islands + totems turn into clicker levels on first open (nothing lost; stored items move to storage).
7. The skill page merges Skills + Upgrade + Requip + Shards for that skill, so the top "Upgrade" tab can become "go to this skill's
   page". [Upgrade tab stays until the skill pages exist]

## Combat = town defense (Skyy 2026-11-14, docs/answered/world.md)
- A little town defended by spirit warriors; upgrade the warriors (strength, kill speed, move speed).
- Upgrade the town to attract more monsters and more kinds: zone 1 easiest first (rats -> wolves + skeletons -> bears + big skeletons +
  trolls ...); at max every kind attacks at once and all their loot is collected.
- Unlocking zone 2 gives a zone 2 town / island farmed the same way.
- ZONE LOCKS on every shard: zone 2 content (e.g. Thorium) only after zone 2 is unlocked.
- Each of the first four skills has its own game: Foraging (tree clicker), Mining (rock / ore node), Farming (crop plots), Combat (town
  defense). Others later.

## Mining = quarry (Skyy 2026-11-14, docs/answered/world.md)
- A big quarry; one island per ZONE (not per ore). Zone 1: Copper, Iron with an upgrade. Silver + Gold on every island, more common with
  upgrades, following vanilla's spread (Silver most common in zone 3).
- Upgrades: miner spirits + quarry (mine speed), chance of something good per block mined. Every block also gives the zone's stone types.

## Farming + Foraging = island clusters per zone (Skyy 2026-11-14)
- Farming: one island per crop; Foraging: one per wood - grouped in a cluster per ZONE (zone 2 crops / woods in a separate zone 2
  cluster that opens with zone 2). The zoomed-out map shows the clusters.

## Steps
1. Art round: the Farming skill page + the Foraging clicker island (small / grown / zoomed out) as mockups for Skyy.
2. Probe: click speed and picture swaps in a test page (SkyyUiProbe), element count.
3. Spec + build Foraging first (SkyyShards), then the other skills; the skill page with the new inventory screen phases.
