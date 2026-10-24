# Sapling fix - SkyyTrees 0.6.3 (queued after bm1 / Trees 0.6.2)

Skyy 2026-10-24: "trees arnt really dropping saplings right now". Root cause found by the sapling builder (docs/log/2026-10.md 2026-10-24).
Build from the SET pin of SkyyTrees once 0.6.2 lands; full verify (harness executes each path, lint, crosscheck).

## Root cause
1. Vanilla never drops saplings from trees (Assets.zip Server/Drops/Wood/Tree_Leaves.json = 50 % Fibre; Tree_Leaves_Physics.json = 2 % Fibre;
   Plant_Sapling_Oak is crafted only).
2. The pack mod Saplings From Trees 1.0.4 (Helios) made fallen leaves drop saplings (~2.5 % per fallen leaf, 7 woods). It is off since 0.7
   ("Skipped disabled pack: Helios:Saplings From Trees"); Skyy 2026-10-12 (docs/answered/project.md:58) said rebuild it ourselves - never done.
3. Our replacement (SkyyTrees 0.3.11, still in 0.6.1) is one 10 % roll per felled tree (TreeReplant.note2, build_skyytrees_0.6.1.py ~9642,
   trees.saplingDropPct=10) + Replanter perk 1 %/level/log (~9338) + a stump replant. Leaves are never rolled.
   Log 2026-10-24 16:04-16:05: ~15-20 trees felled -> 1 sapling, 1 replant.

## Fix
A. Leaves drop saplings: in TreeFelledFn.apply / TreeReplant.note (~9644-9690). SkyySkills already passes every felled leaf to skill:on:felled
   (build_skyyskills_0.4.64.py:19327). Block id "Plant_Leaves_*" -> its sapling, roll trees.leafSaplingPct; respect TreeReplant.allowed()
   (replantWhere), skip while TreeStore.busy, deliver with TreeGather.giveItem; one "Tree bonus" line per tree (no chat spam).
   Leaf -> sapling map built at BUILD time from Assets.zip (majority sapling per Plant_Sapling_* last Farming-stage prefab; fallback name
   match). Asserts: Oak -> Oak, Fir -> Spruce, Fir_Snow -> Spruce_Frozen. Also Goldentree -> Amber, Bottle -> Gumboab, Palm_Arid -> Palm.
   No sapling: Burnt, Dead, Bramble, Autumn, Snow, Fir_Red, Rhododendron, *_Floor leaves.
   New Server Setup row Trees -> Abilities "Sapling chance per fallen leaf" (trees.leafSaplingPct, 0-100 %, decimals, default 2.5);
   missing line = default, nothing rewritten. Keep the 10 % per-tree roll + Replanter (they stack).
B. Replant reliability:
   1. TreeReplantTask.near (~9506): anchor to the FIRST log's x/z, radius 3 (today a moving anchor + restarting timer merges nearby trees).
   2. TreeReplant.plant (~9605): if the block under the lowest felled log is a same-family trunk (stump), plant on the first soil cell with
      air above among the 8 cells around it at stump height (default taken; overrides an old builder note "mid-trunk cut = no sapling").
   3. Skipped-replant counter with reason (stump / not soil / blocked / unloaded) in the info line.

## In-game test (after deploy)
1. Cut 5 Oak / Birch at the bottom log: about 1 sapling per tree ("Tree bonus" line; inventory or the Void if saplings-to-Void is on).
2. Wait 5 s after each: a sapling is planted on each stump spot.
3. Cut 2 trees at eye level (stump left): a sapling is still planted next to the stump.
4. Cut 3 close trees one after another: each gets its own replant.
5. Server Setup -> Trees -> Abilities: "Sapling chance per fallen leaf" = 0 -> only the rare 10 % per-tree drop is left.
