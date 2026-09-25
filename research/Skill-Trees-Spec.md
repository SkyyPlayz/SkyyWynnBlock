# SkyWynn gathering skill trees: build spec (Mining, Foraging, Farming)

*Written 2026-09-23 by the skywynn-skill-research workflow (writer "trees"). Nothing here is built yet. Owner: Skyy (they/them).*
*Scope: one tree each for Mining, Foraging and Farming. Fishing's tree waits until Fishing comes off the shelf.*

**Evidence tags.** Every claim is tagged:
- **VERIFIED**: seen in a source I fetched, in HytaleServer.jar (reflect.py / bcfull.py / callers.py), in Assets.zip, in an installed mod, or in our own build scripts.
- **UNVERIFIED**: an inference, or something a research agent reported that I did not re-check.

In the hook columns:
- **SHIPPED** means the mechanism already runs in a SkyySkills jar we built.
- **ENGINE** means the engine method is VERIFIED in the jar but we have not used it yet.

Jar checked: `...\game\latest\Server\HytaleServer.jar`. Our code checked: `SkyySkills/build_skyyskills_0.3.2.py` (read only).

---

## 0. The short version (decisions for Skyy)

1. **One template, three trees.** Each tree has 12 nodes in 6 tiers, and the three trees share the same slot layout and cost curve. Hypixel reused one design for Heart of the Mountain and Heart of the Forest (section 2).
2. **Tiers open with the skill level only.** Tiers open at Mining 1 / 10 / 20 / 30 / 45 / 60 (the same levels for Foraging and Farming). No NPC, zone or mine is involved (design lock batch 2, item 8).
3. **Two currencies, both computed.**
   - **Tokens** (1 at level 1, then +1 every 5 levels, 21 at level 100) *unlock* nodes.
   - **Dust** (1 per 10 XP of that skill, forever, including XP past level 100) *levels* nodes.
   - Nothing is stored except the node levels, so there is nothing to dupe or lose, and a respec is exact.
   - The currency is called "Dust", not "Powder", because Wynn powders are gear items in SkyWynn.
4. **Respec is free and resets one whole tree.** It refunds everything spent in that tree. You click twice to confirm, and there is a 10-minute cooldown per tree.
5. **The code goes in a new mod, `SkyyTrees`.** SkyySkills gets a small, generic bridge patch: 5 bridge functions/maps, about 100 lines of patch script. Section 9 explains why.
6. **Every node has a VERIFIED hook.** Active abilities, crop-growth auras, auto-replant and real auto-smelt are marked **later** (section 7).
7. **Open for Skyy:**
   - XP pace: at today's XP rates, tiers 4-6 are very far away.
   - Economy numbers for coins, gems and bars.
   - The names.
   - All three are listed in section 15.

---

## 1. What the design lock says

- "HOTM-style trees unlock from that skill's levels, not from a location." (HANDOFF section 1, batch 2 item 8.) **VERIFIED**
- "A skill tree per gathering skill: YES (Mining, Foraging, Farming)." Fishing's tree waits with Fishing. (HANDOFF focus call; SkyySkills-Plan.md.) **VERIFIED**
- Level cap is 100 for every skill. The XP table is Hypixel's up to level 60, then +300k per level: level 30 = 8,022,425 XP, level 60 = 111,672,425, level 100 = 637,672,425. (`LEVELS` in build_skyyskills_0.3.2.py.) **VERIFIED**
- "Powders" is already taken: Wynn's five elements + powders replace SkyBlock runes (batch 2 item 5), and Smithing is leveled "by reforging and adding powders". **VERIFIED**. So the tree currency must not be called powder.

---

## 2. What the reference games do (summary, my own words)

| System | Unlock currency | Leveling currency | Tiers | Respec | Tag |
|---|---|---|---|---|---|
| Heart of the Mountain (SkyBlock Mining) | Tokens of the Mountain unlock perks | Mithril / Gemstone / Glacite powder level perks | 10 | Reset refunds all perk powder and tokens. Tier and Core of the Mountain are kept, and Core powder is not refunded. The reset cost was removed in July 2025 | VERIFIED (minecraft.wiki mirror) |
| Heart of the Forest (SkyBlock Foraging, 2025) | Tokens of the Forest | Forest Whispers, Desert Whispers | 8 | Same model: perk spend refunded; tier and "Center of the Forest" kept | VERIFIED (minecraft.wiki mirror) |
| The Garden (SkyBlock Farming) | none (no perk tree) | Copper buys per-crop Crop Upgrades (+5 Crop Fortune each, tiers I-IX) | Garden levels 1-15 | none described: the wiki never mentions resetting or refunding upgrades (UNVERIFIED that none exists) | VERIFIED except the respec column (minecraft.wiki mirror) |
| mcMMO | none | none | no tree. Most combat and gathering skills have one active "super ability" (Mining has a second one, Blast Mining); Acrobatics, Alchemy, Fishing and Repair have none, only passives. The gathering ones (Super Breaker, Tree Feller, Green Terra, Giga Drill Breaker) all unlock at level 5 on the default 1-100 scale (level 50 on the RetroMode 1-1000 scale), with a 240 s default cooldown and +1 s of duration every 5 levels | n/a | VERIFIED (mcMMO default config files on GitHub) |
| Wynncraft professions | none | none | new materials about every 10 levels, cap 132 | n/a | UNVERIFIED (research agent) |

**What we take from each:**
- **HOTM / HotF:** tokens choose, a second currency grinds, a full free reset keeps tier progress, and one template serves several skills.
- **Garden:** Farming's real SkyBlock progression is per-crop fortune. Our Farming tree turns that into crop-family "Mastery" nodes (S6, S7, S8, S10). This row is SkyBlock research. SkyWynn's dedicated Garden island is **parked** (2026-09-24); farming stays on the main islands. The node name "Garden Mastery" (S8) is a crop-family node, not a commitment to build that island.
- **mcMMO:** its signature gathering ability (Super Breaker, Tree Feller, Green Terra) becomes our tier-6 capstone. mcMMO hands it out early (level 5); we save it for tier 6 so it is the tree's big goal. The capstone is passive with a cooldown, because active ability keys are not verified (section 7).

---

## 3. Currency

### 3.1 Tokens (unlock currency), per tree, per profile

- `earned = level >= 1 ? tokensFirst + floor(level / tokensEvery) : 0`, with defaults `tokensFirst=1`, `tokensEvery=5`.
- That gives 1 at level 1, 2 at level 5, 3 at 10, 5 at 20, 7 at 30, 10 at 45, 13 at 60, 16 at 75 and 21 at 100.
- **Unlock costs:** a node in tiers 1-4 costs 1 token, tier 5 costs 2, and the tier-6 capstone costs 3. Unlocking all 12 nodes costs **16 tokens**, which you reach at **level 75**.
- Before level 75 you must choose. For example, at level 60 you have 13 tokens: all of tiers 1-5 costs 13, so you cannot also afford the capstone.
- For comparison, HOTM gives exactly 25 Tokens of the Mountain in total, from its tiers I-X and Core of the Mountain levels 1, 5, 7 and 10 (**VERIFIED**, wiki).
- Levels come from the existing bridge function `skill:fn:level`, which takes `apply(Object[]{UUID, "Mining"})` and returns an Integer for the active profile (build_skyyskills_0.3.2.py `SkillFn`). **VERIFIED**
- Level 1 of a node is what the token buys. Levels 2 and up cost Dust.

### 3.2 Dust (the "powder" layer): worth it now?

**Yes, but only in its simplest form: computed from XP, never stored, one kind per tree.**

- `earned = floor(total XP in that skill / xpPerDust) + debug.extraDust`, default `xpPerDust=10`.
- `spent` = the sum of the Dust costs of every node level bought in that tree.
- `available = earned - spent`. Only node levels are saved.

**Why now:**
- **It gives the HOTM feel.** Tokens are choices and Dust is the grind. Every block mined visibly fills the tree, not just the level bar.
- **It keeps going past level 100.** SkyySkills never caps XP: `SkillStore.bump` adds without a ceiling (**VERIFIED** in our code). Dust keeps coming after level 100, when tokens have stopped, so maxed players still have goals.
- **It is almost free to build.** It is one division plus a label on the page:
  - No new earning hooks.
  - No migration: players get Dust for XP they already earned.
  - No dupes, and nothing to lose on a crash.
  - Respec is exact: set the node levels to 0 and every Dust comes back.
- **It follows XP retunes on its own.** If Skyy changes xp.properties rates or the `multiplier=` line, Dust follows automatically.

**What is not worth it now:**
- HOTM's three era powders need zone-specific sources, which the design lock rules out.
- Dust from special sources (Exploration rewards, events) would need a stored `bonusDust` counter per tree. That is a later add-on and the formula already has room for it.
- **Never add a "+% Dust" node.** Because Dust is computed from lifetime XP, respeccing such a node would take Dust back retroactively.

**Name:** "Mining Dust", "Foraging Dust", "Farming Dust". No item id in Assets.zip contains "Dust" (**VERIFIED**, scan of Server/Item/Items). "Powder" collides with the Wynn powders (section 1).

### 3.3 Tokens and Dust by skill level (defaults, computed from the level table)

| Skill level | 1 | 5 | 10 | 15 | 20 | 25 | 30 | 35 | 40 | 45 | 50 | 60 | 75 | 90 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tokens | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 13 | 16 | 19 | 21 |
| Dust | 5 | 117 | 992 | 6,742 | 52,242 | 302,242 | 802,242 | 1,552,242 | 2,552,242 | 3,807,242 | 5,517,242 | 11,167,242 | 25,267,242 | 46,117,242 | 63,767,242 |

---

## 4. Gating and unlock rules

- **Tier gates** (skill level): I = 1, II = 10, III = 20, IV = 30, V = 45, VI = 60. Config key: `tier.levels=1,10,20,30,45,60`.
- **Path rule:** to unlock a node in tier *k* (k >= 2), you must own at least one node in tier *k-1*. This gives HOTM's "grow upward" feel without a graph. Tier I is exempt.
- **To unlock:** skill level >= the tier gate, the path rule is met, and you have enough tokens.
- **To level up:** you own the node, it is below max, and you have enough Dust for `B x n^3` (section 5).
- **Four node states on the page:**

| State | Rule | Card colour (background / text) |
|---|---|---|
| Locked | tier gate not reached, path rule not met, or not enough tokens (the detail panel says which) | #1c1414 / #b07a68 |
| Unlockable | all unlock rules met | #16301f / #9adf86 |
| Owned | level 1 up to max-1 (turned-off nodes show "(off)") | #10243d / #9cd8ff |
| Maxed | level = max | #3a3010 / #ffc300 |

- **On / off toggle:** every owned node can be switched off without losing its level. HOTM lets you toggle perks the same way. This matters for Spread, Vein Burst and Tree Feller. It is stored as `<Tree>.off=` (section 11).
- **XP pace warning.** With today's default xp.properties (stone 1 XP, oak log 6 XP, iron ore 8 XP; **VERIFIED**), level 30 needs about 8.0M XP, which is about 1.3M oak logs. So tiers 4-6 are long-term goals. If Skyy wants players to reach capstones sooner:
  - Raise the XP rates, and Dust scales with them automatically.
  - Or lower `tier.levels`.
  - Do not change the costs.

---

## 5. Shared cost template (the same for all three trees)

The Dust cost to go from level *n* to *n*+1 is **`B x n^3`**, for n = 1 .. max-1. The cube is on purpose: it matches the exponential XP table. At level 10, a player can have their tier-I nodes at level 4-5; at level 20, at level 11-12; at level 30, all of tier I is maxed. (Simulated with the default numbers.)

| Slot | Tier (gate) | Tokens | Max | B | Level 2 costs | Last level costs | Dust to max | Running total | Reached around skill level |
|---|---|---|---|---|---|---|---|---|---|
| S1 | I (1) | 1 | 25 | 5 | 5 | 69,120 | 450,000 | 450,000 | 27 |
| S2 | I (1) | 1 | 20 | 5 | 5 | 34,295 | 180,500 | 630,500 | 29 |
| S3 | I (1) | 1 | 15 | 5 | 5 | 13,720 | 55,125 | 685,625 | 30 |
| S4 | II (10) | 1 | 10 | 150 | 150 | 109,350 | 303,750 | 989,375 | 32 |
| S5 | II (10) | 1 | 10 | 150 | 150 | 109,350 | 303,750 | 1,293,125 | 34 |
| S6 | III (20) | 1 | 15 | 100 | 100 | 274,400 | 1,102,500 | 2,395,625 | 40 |
| S7 | III (20) | 1 | 10 | 500 | 500 | 364,500 | 1,012,500 | 3,408,125 | 44 |
| S8 | IV (30) | 1 | 10 | 1,000 | 1,000 | 729,000 | 2,025,000 | 5,433,125 | 50 |
| S9 | IV (30) | 1 | 10 | 1,000 | 1,000 | 729,000 | 2,025,000 | 7,458,125 | 55 |
| S10 | V (45) | 2 | 20 | 200 | 200 | 1,371,800 | 7,220,000 | 14,678,125 | 65 |
| S11 | V (45) | 2 | 10 | 4,000 | 4,000 | 2,916,000 | 8,100,000 | 22,778,125 | 73 |
| S12 | VI (60) | 3 | 5 | 150,000 | 150,000 | 9,600,000 | 15,000,000 | 37,778,125 | 85 |

Maxing a whole tree takes about 37.8M Dust, which a focused player reaches around skill level 85. That leaves goals between levels 60 and 100.

---

## 6. The three trees (12 nodes each)

**Groups used in the tables:**
- *Paid block / log / crop* = a break or F-harvest for which SkyySkills already paid that skill's XP. Player-placed blocks never count (SkyySkills' placed-block tracker; `ignorePlaced=true` is the default, **VERIFIED**).
- *ROCK* = block gather type Rocks, VolcanicRocks or Ore\*, plus any ORE block.
- *ORE* = block id starts with `Ore_`. Do not match on gather type Ore\* alone: `Ore_Mithril_Stone` has gather type Rocks, and the `_Cracked` ore variants carry their parent rock's type (Rocks, or Soils for `Ore_Thorium_Mud_Cracked`). **VERIFIED** in Assets.zip.
- *WOOD* = gather type Woods.
- *Log* = block id contains `_Trunk`.

Gather type strings are **VERIFIED** in Assets.zip as a block's own `BlockType.Gathering.Breaking.GatherType`: Rocks, Woods, Soils, SoftBlocks, VolcanicRocks, OreGold, OreIron, OreSilver, OreCopper, OreCobalt, OreThorium, OreAdamantite. OreMithril appears only in tool `Specs` (pickaxe power lists), never as a block's own type. No per-type counts are given, because the totals change with how you count (raw text hits, files, or parsed block entries with template parents).

Ore blocks are named `Ore_<Metal>_<Rock>` (for example `Ore_Iron_Stone`), so `<Metal>` is the second part of the id. The bare `Ore_<Metal>` ids (Ore_Gold, Ore_Iron, Ore_Adamantite, ...) have no BlockType: they are the ore items, used below only as icons. Onyxium and Prisma have ore items but no ore block, so Prospector (S11) never gives their bars. (**VERIFIED**, Assets.zip.)

**All item ids below are VERIFIED in Assets.zip:**
- Tools: Tool_Pickaxe_\*, Tool_Hatchet_\*, Tool_Hoe_\*, Tool_Sickle_\*.
- Gems: Rock_Gem_Diamond / Emerald / Ruby / Sapphire / Topaz.
- Bars: Ingredient_Bar_Copper / Iron / Silver / Gold / Cobalt / Thorium / Mithril / Adamantite / Onyxium / Prisma.
- Other: Ingredient_Tree_Sap, Ingredient_Life_Essence.
- Saplings: Plant_Sapling_\<Wood\> exists for every Wood_\<Wood\>_Trunk except Burnt and Fir.
- Seeds: Plant_Seeds_\<Crop\> exists for every Plant_Crop_\<Crop\>_Block except Berry, Berry_Wet, Berry_Winter and Wild_Grass (Seed Saver, S2, gives nothing for those).
- Every icon listed.

Hook codes are explained in 6.4. **Costs:** the Slot column is the row in section 5. Every S-number has the same token cost, `B` and Dust totals in all three trees: S1-S9 cost 1 token, S10-S11 cost 2, S12 costs 3, and level *n* to *n*+1 costs `B x n^3` Dust.

### 6.1 Mining

| Slot | Node (config id) | Icon | Max | Per level (total at max) | Hook |
|---|---|---|---|---|---|
| S1 | Mining Speed (MSpeed) | Tool_Pickaxe_Iron | 25 | +2% breaking power on ROCK blocks (+50%) | DMG |
| S2 | Mining Fortune (MFortune) | Ore_Gold | 20 | +1% double-drop chance on every paid Mining block (+20%) | DD |
| S3 | Mining Wisdom (MWisdom) | Ingredient_Crystal_Blue | 15 | +1% Mining XP (+15%) | XP |
| S4 | Miner Stamina (MStamina) | Tool_Pickaxe_Crude | 10 | +0.3 max Stamina (+3; vanilla max is 10) | STAT |
| S5 | Gem Finder (MGems) | Rock_Gem_Ruby | 10 | +0.02% chance per paid Mining block for 1 random gem from the 5 listed (0.2%) | ITEM |
| S6 | Rich Veins (MVeins) | Ore_Iron | 15 | +2% chance that a paid `Ore_` block gives its drops once more (+30%) | EXTRA |
| S7 | Pocket Change (MCoins) | Ingredient_Bar_Gold | 10 | +0.2% chance per paid Mining block for coins = your Mining level (2%) | COINS |
| S8 | Mining Spread (MSpread) | Rock_Stone | 10 | +3% chance to also break 1 touching block with the same id (30%) | BREAK |
| S9 | Tunnel Runner (MRunner) | Armor_Leather_Light_Legs | 10 | +1% move speed, flat layer, while holding a Tool_Pickaxe_ (+10%) | MOVE |
| S10 | Heavy Pick (MHeavy) | Tool_Pickaxe_Mithril | 20 | +2% breaking power on ORE blocks only; stacks with S1, so ores get x1.9 at max (+40%) | DMG |
| S11 | Prospector (MBars) | Ingredient_Bar_Iron | 10 | +1% chance per paid `Ore_<Metal>` block for 1 `Ingredient_Bar_<Metal>`, i.e. already smelted (10%) | ITEM |
| S12 | Vein Burst (MVein) | Ore_Adamantite | 5 | Breaking a paid `Ore_` block also breaks up to 4 + 2 x level touching blocks with the same id (6 up to 14). 40 s cooldown | BREAK |

### 6.2 Foraging

| Slot | Node (config id) | Icon | Max | Per level (total at max) | Hook |
|---|---|---|---|---|---|
| S1 | Chopping Speed (FSpeed) | Tool_Hatchet_Iron | 25 | +2% breaking power on WOOD blocks (+50%) | DMG |
| S2 | Foraging Fortune (FFortune) | Wood_Oak_Trunk | 20 | +1% double-drop chance on logs (+20%); SkyySkills only doubles logs (`doubleDropOnly=_Trunk`, VERIFIED) | DD |
| S3 | Foraging Wisdom (FWisdom) | Ingredient_Crystal_Green | 15 | +1% Foraging XP (+15%) | XP |
| S4 | Forest Vigor (FVigor) | Plant_Fruit_Apple | 10 | +1 max Health (+10) | STAT |
| S5 | Sap Tapper (FSap) | Ingredient_Tree_Sap | 10 | +1% chance per paid log for 1 Ingredient_Tree_Sap, which is a Fuel/Charcoal resource (10%) | ITEM |
| S6 | Replanter (FSapling) | Plant_Sapling_Oak | 15 | +1% chance per paid log for 1 sapling of that wood, `Wood_<W>_Trunk` to `Plant_Sapling_<W>` (15%) | ITEM |
| S7 | Pocket Change (FCoins) | Ingredient_Bar_Gold | 10 | +0.2% chance per paid log for coins = your Foraging level (2%) | COINS |
| S8 | Timber Spread (FSpread) | Wood_Birch_Trunk | 10 | +3% chance to also break 1 touching log with the same id (30%) | BREAK |
| S9 | Woodland Stride (FStride) | Armor_Leather_Light_Legs | 10 | +1% move speed while holding a Tool_Hatchet_ (+10%) | MOVE |
| S10 | Chopping Speed II (FSpeed2) | Tool_Hatchet_Mithril | 20 | +2% breaking power on WOOD blocks, stacks with S1 (+40%) | DMG |
| S11 | Fortune II (FFortune2) | Wood_Redwood_Trunk | 10 | +2% double-drop chance on logs (+20%) | DD |
| S12 | Tree Feller (FFeller) | Tool_Hatchet_Adamantite | 5 | Draft row (2026-09-23): up to 8 + 8 x level connected logs (16 up to 48), 30 s cooldown. Superseded: same-height breaking, then LOCKED 2026-09-25 in `research/Tree-Fall-Spec.md` (levels 1–6 = 1, 2, 4, 5, 6, 10 extra logs on that Y level; cooldown 3 s; level 6 spikes to 10 so a very large tree is not broken as a whole layer) | BREAK |

### 6.3 Farming

There is no breaking-power node here: crops are soft blocks that break in one hit. Farming's crop-family Masteries stand in for SkyBlock's Garden Crop Upgrades.

| Slot | Node (config id) | Icon | Max | Per level (total at max) | Hook |
|---|---|---|---|---|---|
| S1 | Farming Fortune (AFortune) | Plant_Crop_Pumpkin_Block | 25 | +1% double-drop chance on ripe crops, broken or F-harvested (+25%) | DD |
| S2 | Seed Saver (ASeeds) | Plant_Seeds_Wheat | 20 | +1% chance per paid crop for 1 matching `Plant_Seeds_<Crop>` (20%) | ITEM |
| S3 | Farming Wisdom (AWisdom) | Ingredient_Crystal_Yellow | 15 | +1% Farming XP (+15%) | XP |
| S4 | Hearty Harvest (AHearty) | Plant_Fruit_Berries_Red | 10 | +1 max Health (+10) | STAT |
| S5 | Essence Gatherer (AEssence) | Ingredient_Life_Essence | 10 | +0.5% chance per paid crop for 1 Ingredient_Life_Essence (5%) | ITEM |
| S6 | Grain Mastery (AGrain) | Plant_Crop_Wheat_Item | 15 | +2% extra-drop chance for Wheat, Rice, Corn, Cotton (+30%) | EXTRA |
| S7 | Root Mastery (ARoots) | Plant_Seeds_Carrot | 10 | +3% extra-drop chance for Carrot, Potato, Turnip, Onion (+30%) | EXTRA |
| S8 | Garden Mastery (AGarden) | Plant_Seeds_Tomato | 10 | +3% extra-drop chance for Tomato, Lettuce, Cauliflower, Chilli, Aubergine, Pumpkin (+30%) | EXTRA |
| S9 | Field Runner (ARunner) | Tool_Hoe_Iron | 10 | +1% move speed while holding a Tool_Hoe_ or Tool_Sickle_ (+10%) | MOVE |
| S10 | Herbalist (AHerbs) | Plant_Seeds_Health1 | 20 | +1.5% extra-drop chance for the Health1-3, Mana1-3 and Stamina1-3 crops (+30%). These are potion crops, so this ties in with Alchemy | EXTRA |
| S11 | Fortune II (AFortune2) | Plant_Crop_Wheat_Block | 10 | +2% double-drop chance on crops (+20%) | DD |
| S12 | Cornucopia (ACorn) | Ingredient_Life_Essence_Concentrated | 5 | +3% chance that a paid crop gives its drops two more times (15%) | EXTRA |

Crop families match on the crop item id prefix `Plant_Crop_<Crop>`, via `BlockType.getItem().getId()`. That prefix also covers the `_Eternal` variants. Every crop name here exists as `Plant_Crop_<Crop>_Block` in Assets.zip (**VERIFIED**).

**Double-drop totals at level 100.** SkyySkills gives 0.5% per level, so 50%. Adding the tree: Mining 50+20 = 70%, Foraging 50+20+20 = 90%, Farming 50+25+20 = 95%. All stay under SkyySkills' `perk.doubleDropMax=1.0` cap (**VERIFIED** default).

**Economy knobs** (Skyy's call; all live in trees.properties):
- Gem Finder: 0.2% per block at max.
- Pocket Change: 2% of blocks pay coins equal to your level.
- Prospector: 10% of ores give a bar.

### 6.4 Hook codes: what each one is and the evidence

| Code | What it does | Evidence | Status |
|---|---|---|---|
| **DMG** | `DamageBlockEvent.setDamage(getDamage() x (1 + bonus))` for the block's gather type. SkyyTrees `TreeDmgSys` = `EntityEventSystem` on `DamageBlockEvent`, query `Archetype.empty()` (the same query as SkyySkills `BreakSys`), and only when the entity has a `PlayerRef`. | The event class has `getDamage/setDamage/getBlockType/getItemInHand/getCurrentDamage`. `BlockHarvestUtils.damageSingleBlock`:<br>1. builds `new DamageBlockEvent(...)` after `BlockHealthChunk.getBlockHealth`;<br>2. calls `ComponentAccessor.invoke(Ref, event)` when the breaker ref is non-null;<br>3. returns if cancelled;<br>4. **re-reads `getDamage()`** into the local that `BlockHealthChunk.damageBlock(Instant, World, Vector3i, float)` uses.<br>The engine's own `TriggerVolumeRuleSystems$NoDestroyBlockDamage` is an `EntityEventSystem` on `DamageBlockEvent`. Gather type via `BlockType.getGathering().getBreaking().getGatherType()`. | ENGINE, VERIFIED (bytecode + reflect). **UNVERIFIED:** whether the client's crack animation looks odd when the server breaks the block sooner. "Speed" means more damage per hit, not faster swings (the research agent found no server-side swing rate; UNVERIFIED) |
| **DD** | SkyyTrees posts `dd.<skill>` into `skill:bonus:<uuid>`. SkyySkills adds it inside `Perks.chance`, which feeds both the break double drop and the F-harvest double drop. | `Perks.breakDouble` / `harvestDouble` / `chance` / `breakDrops` / `harvestDrops` / `give` exist and ship in 0.3.x. | SHIPPED path, VERIFIED. Needs the SkyySkills bridge patch (section 9.3) |
| **XP** | SkyyTrees posts `xp.<skill>`. SkyySkills multiplies gathering XP in `SkillXp.gain2`. | `SkillXp.gain` / `gain2` and `SkillCfg.MULT` are our code. | SHIPPED path, VERIFIED. Needs the patch |
| **STAT** | `EntityStatMap` `StaticModifier(MAX, ADDITIVE)` under SkyyTrees' own keys `skyytree_health` / `skyytree_stamina`, set once per second by `TreeTick`. | The same code as SkyySkills `Perks.mod` (keys `skyyskill_*`) and SkyyAccessories AccEffects. `DefaultEntityStatTypes` only has Health/Oxygen/Mana/Stamina/Ammo/SignatureEnergy, so a made-up "mining speed" stat is impossible; that is why speed goes through DMG. | SHIPPED pattern, VERIFIED |
| **ITEM** | On a paid gather, roll the chance, then `SimpleItemContainer.addOrDropItemStack(store, ref, inventory.getCombinedStorageHotbarBackpack(), new ItemStack(id, 1))`. The item lands in storage, or at your feet when full. | `ItemStack(String, int)` constructor (reflect). `Perks.give` in SkyySkills uses exactly this path. Item ids are in Assets.zip. The trigger is the new gather listener (patch). | SHIPPED path + ENGINE ctor, VERIFIED |
| **EXTRA** | On a paid gather, roll the chance, then give a **fresh** roll of the block's own drops from `skill:fn:drops`, i.e. SkyySkills `Perks.breakDrops` / `harvestDrops`. Those reproduce the engine through `BlockHarvestUtils.getDrops`. | Shipped in 0.3 double drops. The same exclusions apply automatically: tool-dependent drops, blocks with both Soft and Breaking drops, placed blocks. | SHIPPED, VERIFIED. Needs the patch |
| **COINS** | `coins:fn:add` with `apply(Object[]{UUID, Long})`. | SkyySkills level-up rewards already call it (`SkillStore.coinsAdd`). SkyyCoins 0.1.3+ publishes it, and 0.1.5 is per profile. | SHIPPED, VERIFIED |
| **MOVE** | SkyyTrees posts source `"trees.tools"` (layer `flat`, `speed` = the node for the tool in hand) into `move:<uuid>`. SkyySkills' and SkyyAccessories' MoveSync appliers already sum every source. Held item via `Player.getInventory().getItemInHand()`. | tools/skyymove.py protocol v1 ("every applier computes the same total from all sources"); `Inventory.getItemInHand()` (reflect). | SHIPPED protocol, VERIFIED. SkyyTrees only posts, so it needs SkyySkills 0.2+ or SkyyAccessories 0.3+ as the applier |
| **BREAK** | Collect the positions, then `BlockHarvestUtils.performBlockBreak(Ref player, ItemStack held, List<org.joml.Vector3i>, 4096, Store, chunkStore.getStore())`. This runs on the world thread inside the gather listener. | The static method exists (reflect). The engine's own `BreakBlockInteraction.interactWithBlock` calls it with `4096` (bytecode). For each position (it skips y outside 0-319 and unloaded chunk sections, and catches and logs a failure per block) it calls the 7-argument `performBlockBreak(Ref, ItemStack, Vector3i, int, Ref, ComponentAccessor, ComponentAccessor)`, which passes the player Ref on as the breaker to an 8-argument overload, which calls the 12-argument one. That one **builds a real `BreakBlockEvent`, invokes it on the player's Ref, stops if cancelled**, then runs `naturallyRemoveBlock` (normal drops). With no breaker Ref it fires `EnvironmentBreakBlockEvent` instead. The List overload returns how many blocks it broke (bytecode). So SkyyIslands protection, SkyySkills XP and double drops, and Collections all apply to every extra block. Positions a player placed are skipped via `skill:fn:placed` (patch). Reference mod: vein-mining-2.4.0 calls `Store.invoke(Ref, BreakBlockEvent)` + `World.setBlock` from a lambda made in its own BreakBlockEvent system (bytecode). | ENGINE, VERIFIED hook. **UNVERIFIED:** calling it with `Store` from a `world.execute` task (not a system), tool durability for the extra blocks, and what flag 4096 means. Prototype in the first build; if it fails, use the fallback in section 8.4 |

---

## 7. Later: nodes whose hook is not verified (not in the first build)

| Idea | Why later | What exists |
|---|---|---|
| Active pickaxe / axe / hoe abilities (Mining Speed Boost style) | `InteractionType.Ability1/2/3` exist (**VERIFIED**, reflect), but nobody has bound a custom server interaction to them end to end (**UNVERIFIED**) | One throwaway test item would settle it |
| Crop growth aura near the player | `FarmingBlock.setGrowthProgress / setLastTickGameTime / setCurrentStageSet` are public (**VERIFIED**). Whether nudging them actually advances the stage is **UNVERIFIED** | The engine's `FertilizeSoilInteraction` exists (**VERIFIED**) |
| Auto-replant for crops that break fully | The block placement + stage setting as one flow is **UNVERIFIED** | F-harvest crops already regrow in vanilla (SkyySkills 0.1 notes) |
| True auto-smelt (replace the ore drop) | Needs a cancel-and-rebuild of the break (**UNVERIFIED** flow) | Prospector (S11) gives a bonus bar instead |
| Quick Forge (faster Furnace tab) | Needs a SkyySacks change: SkyySacks would read `tree:fn:level`. Another workflow owns SkyySacks | The bridge function is in section 10 |
| Treasure chests (Great Explorer style) | Overlaps Exploration rewards (research/Exploration-Research.md) | - |
| Fishing tree | Fishing is shelved | Template slot S1-S12 is ready |
| Food / Cooking modifiers | Cooking is not a gathering skill, and research/Cooking-Skill-Spec.md is pending | `tree:fn:level` can feed it later |

---

## 8. Respec, abilities and safety rules

### 8.1 Respec
- **One tree at a time, free, full refund.** All node levels in that tree go to 0.
  - Tokens and Dust come back automatically, because both are computed.
  - Skill level and tiers are untouched (they come from the skill).
  - This is the HOTM / HotF model (section 2), minus the irreversible Core track, which we do not have.
- **Confirm:** the first click arms the button ("Click again to respec Mining", 10 s). The second click inside 10 s resets.
- **Cooldown:** `respec.cooldownMinutes=10` per tree. It stops spam and file churn, not choice.
- **Optional coin cost:** `respec.coins=0`, taken with `coins:fn:take` (VERIFIED SkyyCoins 0.1.3+). Default 0.
- **Negative balance:** if Skyy retunes costs and a player's spent Dust ends up above earned, the page shows the negative balance. Buying is blocked, effects keep working, and a respec is allowed at once, ignoring the cooldown.

### 8.2 Capstone and spread rules
- Only one extra-break action per player at a time.
- Positions broken by S8/S12 are remembered for 5 s. When those breaks come back through the gather listener, they still roll ITEM/EXTRA, but **never trigger another Spread/Vein/Feller** (no chains).
- Neighbours: 26-neighbourhood, same block id (Tree Feller: same `Wood_<W>_Trunk*` family). The origin tree must touch `Plant_Leaves_*`. Placed positions are skipped, and there is a hard cap on count and radius (6 blocks).
- `ability.disabledWorlds=` (comma list), for example to keep abilities out of the hub.
- Cooldowns are per player in memory. Chat line: "Vein Burst! +9 ore (ready again in 40 s)".

### 8.3 Feedback
- One aggregated chat line at most every 2 s: "Tree bonus: +1 Ruby, +1 Tree Sap (x3)".
- `/trees quiet` toggles it (stored in the player file).
- Double drops from the DD nodes keep SkyySkills' own "Double drop!" line, so there is one roll and one message.

### 8.4 BREAK fallback if `performBlockBreak` refuses the Store context
Copy vein-mining's pattern for each block:
1. Fire a synthetic `new BreakBlockEvent(held, pos, blockType)` with `Store.invoke(ref, ev)`.
2. If it was not cancelled, remove the block with `World.setBlock(x, y, z, "Empty", flags)`.
3. Give the drops from `skill:fn:drops`.

Both calls are **VERIFIED** in vein-mining's bytecode. The exact empty-block id and flags must be read from that bytecode before use (UNVERIFIED here).

---

## 9. Where the code lives

### 9.1 Options

| | A: inside SkyySkills | B: new SkyyTrees mod + small SkyySkills bridge patch |
|---|---|---|
| Build size | SkyySkills is already 3,115 lines / 184,667 bytes of build script (0.3.2, VERIFIED), jar 91,499 bytes. The trees add about 1,500 lines, so about 4,600. Every tree tweak recompiles and retests all of Skills | SkyyTrees about 1,500-1,900 lines on its own. The SkyySkills patch is about 100 lines |
| Parallel work | Alchemy, the Smithing row, Exploration and Cooking are all slated for SkyySkills right now. The same patch chain would give merge conflicts ("edit the patch, not this file", 0.3.2 docstring) | Independent. The SkyySkills patch is additive and generic, and can land after the current SkyySkills work |
| Failure blast radius | A load error takes XP down for everyone. SkyyIslands 0.4 failed to load completely over one system rule (HANDOFF) | A SkyyTrees load error only removes trees; skills keep working |
| One-registerSystem-per-class rule (VERIFIED: SkyyIslands 0.4 failed to load until GuardSystem was split into subclasses) | New classes needed anyway: a `DamageBlockEvent` system; the tick could reuse AcroSys | Two system classes: `TreeDmgSys` (one class for all three skills; never register it twice) and `TreeTick`. No BreakBlockEvent system, because the gather listener replaces it |
| Reuse of the perk code | Direct calls | Through bridge functions exposed by the patch (`skill:fn:drops`, `skill:fn:placed`, `skill:fn:xp`, the bonus map, the gather listener). The drop reproduction and placed tracker stay in one place |
| Standalone-mod rule (HANDOFF section 1) | fine | Loads alone with zero dependencies. Without SkyySkills it shows "Trees need SkyySkills" and does nothing |
| Page navigation | Internal page switch | `CommandManager.get().handleCommand(playerRef, "skills")` / `"trees mining"` (the SkyyMenu 0.1.x pattern, VERIFIED) |

### 9.2 Recommendation: **B (SkyyTrees 0.1 + the SkyySkills trees-bridge patch)**
It keeps the biggest, busiest build script from growing by half, isolates failures, and lets trees ship on their own schedule. The bridge pieces are generic, so later mods can use them too:
- Alchemy potions can add XP boosts through `skill:bonus`.
- Exploration or Collections can listen to `skill:on:gather`.

### 9.3 The SkyySkills patch (queued after the current SkyySkills work lands; new tools/ patch file, next free version)
1. **`skill:fn:xp`**: `Function apply(Object[]{UUID, String skill}) -> Long`, the total XP of the active profile (`SkillStore.data(u)[i]`).
2. **Bonus reader**: `skill:bonus:<uuid>` is a `ConcurrentHashMap<String source, Map<String, Number>>`, each entry immutable and replaced whole (move-protocol style).
   - Sum `xp.<skill>` over all sources and multiply gathering XP in `SkillXp.gain2` (rows 0-2 only), clamped 0..5.
   - Sum `dd.<skill>` and add it in `Perks.chance`. That needs the UUID, so add `chanceU(u, row, lvl)`. The result is still capped by `perk.doubleDropMax`.
3. **Gather listeners**: `skill:on:gather` is a `ConcurrentHashMap<String name, Function>`.
   - Called in `BreakTask.run` and `HarvestTask.run` right after `SkillXp.gain` + double drop, only for gathering rows.
   - Argument: `Object[]{PlayerRef, Integer row, BlockType, String world, Boolean harvest, Integer x, Integer y, Integer z}`.
   - Runs on the world thread, with a try/catch around each listener.
4. **`skill:fn:drops`**: `apply(Object[]{BlockType, Boolean harvest}) -> java.util.List` (a fresh roll from `Perks.breakDrops` / `harvestDrops`; null when it cannot be reproduced).
5. **`skill:fn:placed`**: `apply(Object[]{String world, Integer x, Integer y, Integer z}) -> Boolean`. This is a new synchronized `PlacedStore.contains` over `set(w)` / `key(x, y, z)`. The tracker is LRU-capped (VERIFIED), so very old placements can be forgotten; that is acceptable.
6. **UI**:
   - A "Tree" button on the Mining / Foraging / Farming rows of /skills and on their Stats page. It only appears when `tree:fn:level` is on the bridge, and runs `handleCommand(playerRef, "trees <skill>")`.
   - Stats page lines: "Skill tree: +X% double drops, +Y% XP" when the bonus is above 0.

---

## 10. Bridge keys

| Key | Type | Direction | Notes |
|---|---|---|---|
| `skill:fn:level` | Function (UUID, skill) -> Integer | SkyySkills -> SkyyTrees | exists today (VERIFIED). Gives tokens and tier gates |
| `skill:fn:xp` | Function (UUID, skill) -> Long | SkyySkills -> SkyyTrees | new (patch). Gives Dust |
| `skill:fn:drops` | Function (BlockType, Boolean) -> List | SkyySkills -> SkyyTrees | new (patch). EXTRA / BREAK fallback |
| `skill:fn:placed` | Function (world, x, y, z) -> Boolean | SkyySkills -> SkyyTrees | new (patch). BREAK safety |
| `skill:on:gather` | ConcurrentHashMap name -> Function | SkyyTrees registers `"trees"`; SkyySkills calls it | new (patch) |
| `skill:bonus:<uuid>` | ConcurrentHashMap source -> immutable Map (`xp.mining`, `dd.foraging`, ...) | SkyyTrees posts source `"trees"`; SkyySkills reads it | new (patch). UUID key = the active profile (contract rule 3) |
| `move:<uuid>` | movement protocol v1 | SkyyTrees posts `"trees.tools"` (flat) | existing protocol (VERIFIED) |
| `tree:<uuid>` | String, e.g. `"Mining:5/7,Foraging:0/3,Farming:2/4"` (nodes owned / tokens earned) | SkyyTrees -> HUD / menu later | new |
| `tree:fn:level` | Function (UUID, `"Mining.MSpeed"`) -> Integer (0 when turned off) | SkyyTrees -> any mod (later: SkyySacks Quick Forge, Cooking) | new. Its presence also tells SkyySkills to show the "Tree" button |
| `profile:fn:key`, `profile:epoch:<uuid>` | per tools/PROFILES-CONTRACT.md | SkyyProfiles -> SkyyTrees | read (VERIFIED contract) |
| `coins:fn:add`, `coins:fn:take` | SkyyCoins bridge | SkyyCoins -> SkyyTrees | Pocket Change, optional respec cost (VERIFIED) |

---

## 11. Storage per profile (tools/PROFILES-CONTRACT.md)

**Data folder:** `<world>/mods/Skyy_SkyyTrees/`, via `getDataDirectory().resolveSibling("Skyy_SkyyTrees")` (the stable-folder rule, HANDOFF section 2).

**Player file:** `players/<pkey>.properties`, where `pkey` is the contract helper. Profile 1 = `uuid.toString()`, profile N = `uuid-pN`. Written atomically (tmp file + move), dirty-flushed every 10 s, and also on respec and on shutdown.

```
name=Skyy
v=1
quiet=false
Mining.MSpeed=12
Mining.MFortune=5
Mining.MWisdom=1
Mining.off=MSpread
Mining.respecAt=1790000000000
Foraging.FSpeed=3
Farming.AFortune=2
```

- Only node levels, off flags, the respec time and quiet are stored. Tokens and Dust are always recomputed from `skill:fn:level` / `skill:fn:xp`, which are per profile, so they follow the active profile with no extra work.
- In-memory caches are keyed by the pkey String (contract rule 2).
- `skill:bonus:<uuid>`, `tree:<uuid>`, the `move` source and the `skyytree_*` modifiers are recomputed and republished when `TreeTick` sees `profile:epoch:<uuid>` change (contract rules 3-4).
- The inventory is never touched (rule 5).

**Config:** `trees.properties`, written with defaults on first run and reloaded by `/trees reload` (`requirePermission("skyytrees.admin")`, `setPermissionGroups(new String[0])`). Keys:
- `tier.levels`, `tokens.first`, `tokens.every`, `dust.xpPerDust`.
- `respec.cooldownMinutes`, `respec.coins`.
- `ability.disabledWorlds`, `feedbackMs`.
- For each node `<Tree>.<Id>.`: `max`, `per`, `B`, `tokens`, `enabled`, plus `items` / `crops` lists where a node uses them.
- `vein.cooldownSec`, `feller.cooldownSec`, `feller.needLeaves`.
- `debug.extraTokens=0` and `debug.extraDust=0`, for Skyy's testing only.

---

## 12. UI plan (inline page, SkyWynn style)

**Rules followed (HANDOFF section 2):**
- The page is built with `appendInline` only; no .ui files.
- No underscores in element ids.
- The root Group's Anchor holds only Width and Height.
- Top-bar and panel buttons (tabs, Back, Respec, Buy, Toggle) are `TextButton` + `TextButtonStyle`, as in HANDOFF section 2. Node cards are `Button` + `ButtonStyle` with `ItemIcon` and `Label` children (see Node card below). Both bind `EventData.of("a", payload)`, matched with `data.indexOf(payload + "\"")`. The trailing quote stops `trnode1` from matching `trnode10`.
- No page updates from MouseEntered / MouseExited.
- Click handlers call `rebuild()`, as `SkillsPage` already does (VERIFIED).
- `build(...)` is public.
- Text values are sanitised like `SkillsPage.safe` (`, : ; { } "`).

**Commands:**
- `/trees` (alias `/tree`) opens the last tree viewed, or Mining.
- `/trees mining|foraging|farming` is a usage variant with `withRequiredArg`, per the command rule on positional args.
- Both carry `setPermissionGroups(new String[]{"hytale:Adventurer"})`.
- `/trees quiet`.

**Layout (root `#SkyyTrRoot`, 1000 x 660):**

```
+--------------------------------------------------------------------------------------+
| [Mining] [Foraging] [Farming]        Mining 23 / 100    Tokens 2 of 5    Dust 48,210  |  #SkyyTrTab0-2 #SkyyTrLvl #SkyyTrTok #SkyyTrDust
|--------------------------------------------------------------------------------------|
| Tier VI  Mining 60 |  [Vein Burst      ]                    | DETAIL (#SkyyTrDet)     |
| Tier V   Mining 45 |  [Heavy Pick ][Prospector ]            |  icon  Mining Speed      |
| Tier IV  Mining 30 |  [Spread     ][Tunnel Run ]            |  Owned - level 12 / 25   |
| Tier III Mining 20 |  [Rich Veins ][Pocket Chg ]            |  Now: +24% breaking      |
| Tier II  Mining 10 |  [Stamina    ][Gem Finder ]            |  Next: +26%              |
| Tier I   Mining 1  |  [Speed      ][Fortune    ][Wisdom  ] |  Cost: 8,640 Dust        |
|                    |   (Tier I at the bottom, like HOTM)    |  Needs: -                |
|                    |                                        |  [ Level up - 8,640 ]    |  #SkyyTrBuy
|                    |                                        |  [ Turn off ]            |  #SkyyTrToggle
|--------------------------------------------------------------------------------------|
| [< Skills]   [Respec Mining]   feedback line                                          |  #SkyyTrBack #SkyyTrRespec #SkyyTrMsg
+--------------------------------------------------------------------------------------+
```

**Tier rows** are `Group #SkyyTrRow<t>` (Height 78, LayoutMode Left). Each holds:
- a tier Label (Width 130): green when the gate is reached, `#b07a68` when it is not;
- 1-3 node cards.

**Node card:** copy the proven SkyySacks bag-cell pattern. Every SkyySacks script since 0.2 builds `Button #SkyySCell<n>` with `ButtonStyle` + `ItemIcon` + `Label` and binds `Activating` (live 0.7.1, and built 0.7.2 at line 1197; VERIFIED); Skyy uses that page in game. HANDOFF section 2 only shows `TextButton`, so a note for later builders: `Button` is the deliberate choice for icon cells, not a slip. Do not "fix" node cards back to `TextButton`.

```java
b.appendInline("#SkyyTrRow" + t, "Button #SkyyTrN" + i + " { Anchor: (Width: 170, Height: 72); Style: ButtonStyle( Default: ( Background: " + bg + " ), Hovered: ( Background: " + hv + " ), Disabled: ( Background: #141414 ) ); ItemIcon { Anchor: (Width: 44, Height: 44, Left: 6, Top: 14); ItemId: \"" + icon + "\"; } Label { Anchor: (Left: 56, Top: 10, Width: 110, Height: 22); Text: \"" + name + "\"; Style: (FontSize: 11, RenderBold: true, TextColor: " + fg + "); } Label { Anchor: (Left: 56, Top: 40, Width: 110, Height: 18); Text: \"" + sub + "\"; Style: (FontSize: 11, TextColor: " + fg + "); } }");
ev.addEventBinding(CustomUIEventBindingType.Activating, "#SkyyTrN" + i, EventData.of("a", "trnode" + i));
```

`i` is the slot number, 1-12: S1 is `#SkyyTrN1` / `trnode1`, S12 is `#SkyyTrN12` / `trnode12`. TreeDefs, the cards and the events all use the slot number, with no +1/-1 conversion.

(In the build script's Python f-strings the braces are doubled.)

**The `sub` line depends on the state:**

| State | `sub` text |
|---|---|
| Locked | "Mining 30" / "Tier III first" / "Need 2 tokens" |
| Unlockable | "Unlock - 1 token" |
| Owned | "12 / 25", or "12 / 25 (off)" |
| Maxed | "MAX 25" |

The selected node uses its state's Hovered colour as its Default background. Colours are in section 4.

**Detail panel** (`#SkyyTrDet`, Width 320, Background #101d30): `ItemIcon #SkyyTrDetIcon`, then Labels `#SkyyTrDetName`, `#SkyyTrDetState`, `#SkyyTrDetNow`, `#SkyyTrDetNext`, `#SkyyTrDetCost`, `#SkyyTrDetNeed` and `#SkyyTrDetHow` (one line on what triggers it, e.g. "Rolls on every ore block that pays Mining XP").

**Buy button text:**
- "Unlock - 1 token"
- "Level up - 8,640 Dust"
- "Need Mining 30"
- "Need 3,400 more Dust"
- "MAX"

The server re-checks every rule on click, whatever the button says.

**Events:**

| Payload | Action |
|---|---|
| `trtab0-2` | switch tree; the selection resets to S1 |
| `trnode1-12` | select that slot's node (the number is the slot), then `rebuild()` |
| `trbuy` | validate, apply, mark dirty, republish the bonus, then `rebuild()` |
| `trtoggle` | switch the selected node on or off |
| `trrespec` | two-step confirm (section 8.1) |
| `trback` | `CommandManager.get().handleCommand(playerRef, "skills")` opens SkyySkills' /skills page (the SkyyMenu pattern, VERIFIED) |

**Styles:** copy SkyySkills `StatsPage`'s `TextButtonStyle` string and its `line(...)` label helper as they are (VERIFIED in 0.3.2).

### 12.1 Installed tree UIs worth copying (what exactly)
- **EndlessLeveling.jar, `com/airijko/endlessleveling/ui/ClassPathsUIPage`** (+ `$NodeStatus`, `$PathTierRow`; markup in `Common/UI/Custom/Pages/Classes/ClassPathNodeCard.ui` and `ClassPathTierRow.ui`).
  - **Copy:** the node-status model. It is a record of label + colour with four states, Active / Unlocked / Available / Locked, and `resolveNodeStatus(...)` decides the state per node (VERIFIED, constant pool). Also copy the page shape: tier rows of node cards, a detail panel (icon, name, coloured status line, requirements), and a legend.
  - **Copy:** the node card structure. It is a clickable Button with a 2 px outline, one background layer per state (only one visible), a 40x40 ItemIcon, and name and status labels (VERIFIED from the markup).
  - **Do not copy:** its .ui files or `append("Pages/...ui")`. Rebuild everything as inline strings (HANDOFF rule 2).
- **MMOSkillTree-1.6.0.jar, `com/ziggfreed/mmoskilltree/pages/skill/SkillTreePage`.**
  - **Copy:** the header (skill icon, name, level, XP bar, Prev/Next skill buttons; our tabs replace them), a tier list with a choices container per tier, and a Back button plus a Reset button whose background is greyed at runtime when a reset is not allowed (`#ResetButton.Style.Default.Background`, VERIFIED constant).
  - It also loads .ui files (append strings `Pages/SkillTreePage.ui`, `Pages/TierRow.ui`, `Pages/SkillTreeChoiceCard.ui`; in the jar they are `Common/UI/Custom/Pages/SkillTreePage.ui`, `.../TierRow.ui`, `.../SkillTreeChoiceCard.ui`), so copy the layout only (VERIFIED, constant pool + jar listing).
- **MMOSkillMasteryPack-2.0.0.zip, `Server/MMOSkillTree/MasteryGenerators/Gathering_Skill_Masteries.json`.** One generator stamps the same tiered node chain onto each gathering skill: tier, prerequisites, a skill-level gate, a cost, and a percent modifier (VERIFIED structure). That is the same idea as our one-template-three-trees table in trees.properties. Summarised, not copied.
- **Not useful:** RPGLeveling, LincerosLevelTools and ProficiencyLevels have no tree classes (research agent, UNVERIFIED). treeharvester-2026.02.19-1.1 targets an older engine API (`com.hypixel.hytale.math.vector.Vector3i`). The current jar uses `org.joml.Vector3i`: our `performBlockBreak` bytecode casts to it (VERIFIED).

---

## 13. SkyyTrees class list (for the builder)

`TreeDefs` (node table generated from Python) · `TreeCfg` (trees.properties) · `TreeStore` (per-pkey levels / off / respec, `pkey`, `bridge`) · `TreeCalc` (tokens, Dust, costs, states) · `TreeFx` (per-player cached effect vector, rebuilt on buy / respec / toggle / switch / reload; posts the `skill:bonus` and `tree:<uuid>` entries) · `TreeGather` (Function for `skill:on:gather`: ITEM / EXTRA / COINS / BREAK) · `TreeAbil` (flood fill, cooldowns, chain guard) · `TreeDmgSys` (EntityEventSystem, DamageBlockEvent) · `TreeTick` (EntityTickingSystem on players, once per second: epoch check, `skyytree_*` modifiers, move source) · `TreeFn` (`tree:fn:level`) · `TreePage` (CustomUIPage) · `TreesCmd` / `TreeQuietCmd` / `TreeReloadCmd` · `SkyyTreesPlugin`.

javassist rules from HANDOFF apply: no lambdas, generics, varargs, autoboxing, enhanced-for or inner classes, and methods go in dependency order.

---

## 14. Build order

1. **SkyySkills trees-bridge patch** (section 9.3), after the in-flight SkyySkills builds land. Build without deploying.
2. **SkyyTrees 0.1:**
   - currency, storage, page and commands;
   - all DMG, DD, XP, STAT, ITEM, EXTRA, COINS and MOVE nodes, plus Cornucopia;
   - S8 Spread with a BREAK prototype.
3. **SkyyTrees 0.2:** Vein Burst and Tree Feller on the BREAK path, or on the section 8.4 fallback if the prototype failed.
4. **Deploy SkyySkills and SkyyTrees together**, once Skyy OKs it (HANDOFF deploy rule). Then append an entry to HANDOFF section 6.

---

## 15. Open questions for Skyy

1. **XP pace.** At current XP rates, Mining 30 needs about 1.3M stone-equivalent. Do you want to raise gathering XP rates (the trees scale with them) or lower the tier gates (1/10/20/30/45/60)?
2. **Economy.** Are Pocket Change (2% of blocks pay your level in coins), Gem Finder (0.2%) and Prospector (10% bars) OK, or lower?
3. **Names.** Are "Dust" and "Tokens", and the node names, OK? (Kept short so they fit on the cards.)
4. **Respec.** Free with a 10 min cooldown, or charge coins?
5. **Command.** Add a `/hotm` alias for SkyBlock players? It would open the Mining tree.

---

## 16. In-game test checklist (for Skyy)

1. The server log shows "[SkyyTrees] 0.1 ready" and no load errors. Skills still award XP.
2. `/skills` → the Mining row has a "Tree" button → the Mining tree opens. "< Skills" takes you back.
3. The header shows your level, Tokens (1 + level/5) and Dust (your Mining XP / 10).
4. The four colours show up: tiers above your level say "Mining 30" in red; an unlockable node is green.
5. Unlock **Mining Speed**. Count the hits on one stone type before and after a few levels: fewer hits means it works. Tell me if the crack animation looks wrong.
6. **Fortune / Wisdom:** the Stats page shows the higher double-drop chance, and the "+XP" chat numbers go up by the %.
7. **Forest Vigor** (Foraging): max health goes up by 1 per level.
8. **Item nodes:** set `debug.extraDust=100000` and a high `per` in trees.properties, run `/trees reload`, then break logs and ore. You should get "Tree bonus: +1 Tree Sap" and similar, with items in your inventory.
9. **Tunnel Runner:** holding a pickaxe makes you faster; switching to a sword returns to normal within 2 s.
10. **Respec:** click twice → all nodes go to 0 and Tokens/Dust are full again; health and speed return to normal. A second respec says to wait.
11. **Turn off** a node → its effect stops, and its level is kept.
12. **Relog** → the tree is unchanged.
13. **After SkyyProfiles:** switch profile → a different tree; switch back → yours again.
14. **Spread / Tree Feller / Vein Burst** (use debug tokens):
    - A natural tree falls.
    - A log wall you placed does NOT.
    - Ore veins break.
    - A visitor on your island cannot use them (protection).
15. **Watch the server log** for "tree ... failed (logged once)" lines.

---

## Sources
- Heart of the Mountain: https://hypixelskyblock.minecraft.wiki/w/Heart_of_the_Mountain (fetched 2026-09-23; tokens unlock perks, powder levels them, 10 tiers, reset refunds and keeps tier/Core, reset cost removed July 2025). VERIFIED.
- Token of the Mountain: https://hypixelskyblock.minecraft.wiki/w/Token_of_the_Mountain (fetched 2026-09-23; itemised sources, 25 maximum). VERIFIED.
- Heart of the Forest: https://hypixelskyblock.minecraft.wiki/w/Heart_of_the_Forest (fetched; Foraging XII, 8 tiers, Tokens of the Forest, Forest/Desert Whispers, same reset model). VERIFIED.
- The Garden: https://hypixelskyblock.minecraft.wiki/w/The_Garden (fetched; 15 levels, Copper Crop Upgrades +5 Crop Fortune, tiers I-IX, 13 crops; nothing about resetting upgrades either way). VERIFIED.
- mcMMO default config, https://github.com/mcMMO-Dev/mcMMO (fetched 2026-09-23): `src/main/resources/skillranks.yml` (TreeFeller / SuperBreaker / GreenTerra / GigaDrillBreaker Rank_1 = 5 Standard, 50 RetroMode), `config.yml` (cooldowns 240 s), `advanced.yml` (`Ability.Length.IncreaseLevel` 5 Standard, 50 RetroMode), `SuperAbilityType.java` (which skills have a super ability). VERIFIED. The wiki pages (https://wiki.mcmmo.org/en/skills/mining, /woodcutting) render with JavaScript and could not be read.
- Wynncraft (https://wynncraft.wiki.gg/wiki/Professions): reported by the trees-games research agent. UNVERIFIED by me.
- Engine: HytaleServer.jar. Evidence:
  - reflect: DamageBlockEvent, BlockHarvestUtils, FarmingBlock, InteractionType, ItemStack, Inventory, Store, BlockBreakingDropType, ItemTool / ItemToolSpec, TriggerVolumeRuleSystems$NoDestroyBlockDamage;
  - bytecode: `BlockHarvestUtils.damageSingleBlock`, `performBlockBreak` (all overloads);
  - callers: `BreakBlockInteraction.interactWithBlock`.
- Assets: Assets.zip `Server/Item/Items/**` (gather types, item ids, crop / seed / sapling pairs).
- Installed mods (read only): EndlessLeveling.jar, MMOSkillTree-1.6.0.jar, MMOSkillMasteryPack-2.0.0.zip, vein-mining-2.4.0.jar.
- Our code: SkyySkills/build_skyyskills_0.3.2.py, SkyySacks/build_skyysacks_0.7.2.py (Button cells), SkyyMenu/build_skyymenu_0.1.2.py (handleCommand), SkyyCoins/build_skyycoins_0.1.3.py (coins:fn:take), tools/skyymove.py, tools/PROFILES-CONTRACT.md, HANDOFF.md.
