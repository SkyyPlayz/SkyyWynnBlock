# SkyWynn gathering tiers - draft (Mining, Foraging, Farming)

Cloud draft, 2026-10-06. Repo data only (no game files): `docs/answered/economy.md` (metal / wood / crop tiers), `docs/answered/gear.md` (Foraging armor ladder, tool levels, armor types),
`research/Tool-Levels-Spec.md` (breaking Quality gates), `SkyyCollections/build_skyycollections_0.2.6.py` (the 159 collections), the zone bands (Zone 1 1-20, Zone 2 20-30, Zone 3 30-45, Zone 4 45-60),
and `research/cloud/SkyBlock-Gathering-Progression.md` (SkyBlock model). Anything that needs Assets.zip is **UNVERIFIED** and listed in section 7.
Skyy's direction (2026-10-05): *SkyBlock-style ladder; tier the materials first (Hytale kind of does this already), then tie recipes to collection levels; group trees so Zone 1 does not have 6 tree tiers; Enchanted (compressed) materials.*

## 0. What a tier is (the rule for every skill)

A **gathering tier = one material family + the tool that can harvest it + the armor set that boosts it + an access rule + a compressed form**. All five columns appear in every table below.

| Part | Meaning |
|---|---|
| Materials | the blocks / items that belong to the tier (and so to its collections) |
| Tool tier | the lowest gathering tool that can break them (Tool-Levels-Spec: breaking Quality) |
| Armor tier | the gathering armor set for that tier (Foraging armor is LOCKED; Mining / Farming armor = later ideas) |
| Access | the zone / biome where it grows + the skill level (SkyBlock "access" gate) |
| Compressed | its Enchanted form (details in `Enchanted-Materials-Draft.md`) |
| Collection gate | which collection tier unlocks the **next** tier's tool/armor recipe (details in `Collection-Unlocks-Draft.md`) |

Seven tiers is the natural number: the **seven vanilla metals** (Copper, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium), the **seven Farming Bench tiers (T1-T7)**, and the **seven foraging wood tiers** of the Farmer's Workbench
(Softwood -> Lightwood -> Hardwood -> Drywood -> Darkwood -> Redwood -> Goldenwood), each Foraging armor design echoing one metal (LOCKED 2026-10-05). So every skill gets the same 7-step spine, mapped to the same level bands:

| Tier | Gear band | Zone it opens | Metal (Mining) | Wood (Foraging) | Crop group (Farming) |
|---|---|---|---|---|---|
| T1 | 1-18 (Crude / Wood / Copper) | Zone 1 | Copper | Softwood | crops group A |
| T2 | 15-23 | Zone 1 upper | Iron | Lightwood | crops group B |
| T3 | 20-28 | Zone 2 | Thorium | Hardwood | crops group C |
| T4 | 25-38 | Zone 2 -> 3 | Cobalt | Drywood | crops group D |
| T5 | 35-43 | Zone 3 | Adamantite | Darkwood | eternal seeds I |
| T6 | 40-49 | Zone 3 -> 4 | Mithril | Redwood | eternal seeds II |
| T7 | 50+ (later, own tiers) | Zone 4 / 5 | Onyxium | Goldenwood | eternal seeds III |
(The metals column is exact: it follows the SkyyGear bands already live. The wood and crop columns are my proposals; section 7 lists the checks.)

## 1. MINING

### 1.1 Facts from the repo
- 14 stone-like collections already exist (Cobblestone, Sandstone, Shale, Slate, Basalt, Volcanic, Marble, Quartzite, Limestone, Ice, Salt, Sand, Rubble, Clay) and 8 metals (Copper, Iron, Silver, Gold, Thorium, Cobalt, Adamantite, Mithril) + hidden Onyxium + Crystal + Gemstone.
- **Quality gates:** Adamantite ore needs a pickaxe of Quality 4 (**Thorium or better**); Mithril ore is Rocks Quality 5 (**Adamantite or better**) (Tool-Levels-Spec 3, section 831). So vanilla already gates metals by pickaxe tier - the tiers below follow that.
- Silver and Gold are outside the tool ladder (economy.md) and stay decorative / economy items.
- Bazaar prices climb x2 per tier (Copper 5, Iron 16, Thorium 48, Cobalt 144, Adamantite 480, Mithril 1,440, Onyxium 3,712).

### 1.2 Mining tiers (metals)
| Tier | Ore | Where (zone / host rock) | Pickaxe needed | Gathering armor (later idea) | Compressed | Gate |
|---|---|---|---|---|---|---|
| T1 | **Copper Ore** (+ Stone, Sand, Clay, Rubble) | Zone 1 veins, Cobblestone everywhere | Crude / Wood / Copper pickaxe | Mining armor T1 (Copper-trimmed) | Enchanted Copper | start; Copper collection I-III |
| T2 | **Iron Ore** | Zone 1 upper rings | Copper pickaxe | T2 (Iron) | Enchanted Iron | Copper collection IV+ |
| T3 | **Thorium Ore** | Zone 2 (mud, sandstone) | Iron pickaxe | T3 | Enchanted Thorium | Iron collection IV+ |
| T4 | **Cobalt Ore** | Zone 2-3 (shale, slate) | Thorium pickaxe | T4 | Enchanted Cobalt | Thorium collection IV+ |
| T5 | **Adamantite Ore** | Zone 3 (magma) | Quality 4 = Thorium or better; Cobalt pickaxe recommended | T5 | Enchanted Adamantite | Cobalt collection IV+ |
| T6 | **Mithril Ore** | Zone 3-4 | Quality 5 = Adamantite or better | T6 | Enchanted Mithril | Adamantite collection IV+ |
| T7 | **Onyxium Ore** | none known yet (hidden collection) | Mithril pickaxe | T7 | Enchanted Onyxium | later |

### 1.3 Mining - the stone / bulk families (a parallel mini-ladder)
Stone has many families and no metal gate; group them into **3 bulk tiers** so we do not have 14 stone tiers:
| Bulk tier | Collections (existing) | Zone | Use |
|---|---|---|---|
| **S1 Common stone** | Cobblestone, Sand, Rubble, Clay, Sandstone | Zone 1 | building, cobble compactors, early smelting |
| **S2 Rock** | Shale, Slate, Limestone, Marble, Quartzite, Salt | Zone 2-3 | mid-game building, Enchanted Cobblestone variants |
| **S3 Volcanic / frozen** | Basalt, Volcanic Rock, Ice | Zone 3-4 | late building, fuel, special recipes |
| Specials (not tiered) | Crystal Shards, Gemstones | Zone 2+ | magic items (Collections: E curve) |

### 1.4 Level and skill access
Mining level opens the zones (SkyBlock "access"): none needed for Zone 1; **Mining 10 for T2**, **Mining 20 for T3/T4**, **Mining 30 for T5**, **Mining 40 for T6** are suggested (the tool levels already require "Mining N" to use a level-N tool - LOCKED 2026-10-02). A tier's pickaxe can only be *crafted* when the previous tier's collection is at tier IV, so tool level and collection both gate.

## 2. FORAGING (the grouped-tree ladder)

### 2.1 Facts from the repo
- 33 log types, one collection each, plus Plant Fiber, Stick, Tree Sap. Bazaar price tiers (LOCKED 2026-10-04) already group them: **T1 common** (Oak, Birch, Ash, Aspen, Beech, Cedar, Dry, Fir, Jungle, Palm 3; Bamboo, Burnt 2), **T2** (Apple, Banyan, Bottletree, Camphor, Blue Fig, Gumboab, Maple, Palo, Poisoned, Sallow, Spiral, Windwillow, Wild Wisteria 4), **T3** (Amber, Redwood 5), **T4** (Azure, Petrified 6), **T5** (Crystalwood, Fire, Frostwood, Stormbark 8).
- Foraging armor is LOCKED: tier 1 = vanilla **Wood armor**, then the Farmer's Workbench ladder **Softwood -> Lightwood -> Hardwood -> Drywood -> Darkwood -> Redwood -> Goldenwood** (7 tiers), each echoing Copper -> Onyxium; stats Foraging Fortune + chopping speed (+ Foraging XP higher up), low Defense, Tree Feller on higher tiers; axes also get Tree Feller.
- Tool gate: hatchet = Foraging level; logs are always multi-hit (Tool-Levels-Spec 5).

### 2.2 Proposal: **5 tree tiers, not 33** (and only 2 in Zone 1)
Group the 33 log types by the **5 Bazaar price tiers** (already agreed) and attach the **7 wood-ladder names** as the armor/recipe tiers:

| Tree tier | Logs (grouped; from the Bazaar tiers) | Zone | Hatchet needed | Armor tier it unlocks | Compressed |
|---|---|---|---|---|---|
| **F1 Common woods** | Oak, Birch, Ash, Aspen, Beech, Bamboo, Burnt, Dry, Palm, Jungle (the T1 list minus Cedar, Fir) | Zone 1 (rim and middle) | Crude / Wood / Copper | **Wood armor** (vanilla, T1) -> **Softwood** | Enchanted Oak (as the "common wood" form) |
| **F2 Uncommon woods** | Apple, Maple, Blue Fig, Camphor, Banyan, Bottletree, Gumboab, Palo, Sallow, Spiral, Windwillow, Wild Wisteria, Poisoned | Zone 1 upper + Zone 2 | Copper / Iron | **Lightwood**, then **Hardwood** | Enchanted Maple |
| **F3 Northern woods** | Cedar, Fir, Redwood, Amber | Zone 3 | Iron / Thorium | **Drywood**? (see 7.2) / **Darkwood** | Enchanted Redwood |
| **F4 Strange woods** | Azure, Petrified | Zone 1 blue forest (Azure) + Zone 3-4 | Thorium / Cobalt | **Darkwood** / **Redwood** | Enchanted Azure |
| **F5 Elemental woods** | Crystalwood, Fire, Frostwood, Stormbark | Zone 3-4 | Adamantite / Mithril | **Redwood** -> **Goldenwood** | Enchanted Crystalwood |
Fiber / Stick / Tree Sap are **support materials**, not tiers: Tree Sap's collection gates the Lantern (LOCKED 2026-10-05).

Why 5 and why only F1 + a little F2 in Zone 1: Zone 1 gets **one common group** (F1) plus the blue-forest wood (Azure, F4) as the "special" - so the player faces 1-2 tree tiers there, not 6.
The 7 armor names are *recipes*, unlocked by **collection tiers of the group's key log** (see Collection-Unlocks-Draft), so several armor tiers can come from one tree tier; the armor name sets the **look** (echoes a metal), the tree tier sets the **ingredient**.

### 2.3 Foraging tool / armor ladder
| Step | Hatchet | Armor (gathering) | Unlocked by |
|---|---|---|---|
| 1 | Crude hatchet (NPC shop) | Wood armor (vanilla) | start |
| 2 | Copper hatchet | Softwood | Oak collection III-IV |
| 3 | Iron hatchet | Lightwood | Birch / Maple collection IV |
| 4 | Thorium hatchet | Hardwood | F2 key log V |
| 5 | Cobalt hatchet | Drywood | F3 key log IV |
| 6 | Adamantite hatchet | Darkwood | F4 key log IV |
| 7 | Mithril hatchet | Redwood | F5 key log IV |
| 8 | Onyxium hatchet (later) | Goldenwood | later |
(8 rows because the vanilla Wood armor is tier 1 and the 7 bench woods come after it; if the bench ladder already includes the Wood armor as "Softwood" it collapses to 7 - see section 7.)

## 3. FARMING (the vanilla Farming Bench path)

### 3.1 Facts from the repo
- Crops follow the **vanilla Farming Bench order** (LOCKED 2026-10-05): Wheat / Carrot / Lettuce / Corn = 2; Cauliflower / Turnip / Aubergine / Pumpkin = 6; Chilli / Tomato / Cotton / Rice = 16; Potato / Onion = 40 (Bazaar). Seeds climb x2 per tier; **eternal seeds** climb x4 (50 / 200 / 800 / 3,200).
- 14 crops + Wild Berries, Apple, Wild Fruit, Mushroom (19 kinds), Cactus, Seeds, Essence of Life, Petals, and 4 raw meats are the Farming collections.
- Hoe and sickle are Farming-gated tools (LOCKED), Fortune only (no swing speed); Farming Bench accessories exist T1-T7.

### 3.2 Farming tiers
Crops are planted, so **zones do not gate them**; the gate is the **seed recipe** (collection) and the **bench tier**.
| Tier | Crops (vanilla Farming Bench order) | Seeds | Hoe / sickle | Armor (later idea) | Compressed | Gate |
|---|---|---|---|---|---|---|
| **A** | Wheat, Carrot, Lettuce, Corn | wild seeds (drop from grass, from breaking ripe crops) | Crude / Copper hoe | Farming armor T1 | Enchanted Wheat / Carrot | start; Wheat collection I |
| **B** | Cauliflower, Turnip, Aubergine, Pumpkin | seeds via collection recipe | Iron hoe | T2 | Enchanted Pumpkin | Wheat collection IV, Carrot IV |
| **C** | Chilli, Tomato, Cotton, Rice | seeds via collection | Thorium / Cobalt hoe | T3 | Enchanted Tomato / Cotton | Corn V, Pumpkin IV |
| **D** | Potato, Onion | seeds via collection | Adamantite hoe | T4 | Enchanted Potato | Cotton IV, Rice IV |
| **Eternal I-III** | the eternal seed variants of the crops above | craftable (collection-gated) | Mithril / Onyxium hoe | T5-T7 | Enchanted Eternal Crop | the corresponding crop collection high tiers |
Livestock and fruit (Raw Chicken / Beef / Pork / Wildmeat, Apples, Berries) are **side collections** feeding Cooking (SkyyCooking) rather than tiers.

## 4. Cross-skill alignment table
| Level band | Zone | Mining ore | Tree tier | Crop group | Armor (all three gathering sets) |
|---|---|---|---|---|---|
| 1-10 | 1 | Copper + stone S1 | F1 | A | Wood / T1 |
| 10-20 | 1 | Iron | F1 + F2 | A, B | T2 |
| 20-30 | 2 | Thorium, Cobalt (start) | F2, F3 | B, C | T3-T4 |
| 30-45 | 3 | Cobalt, Adamantite, Mithril (start) | F3, F4, F5 | C, D | T5-T6 |
| 45-60 | 4 | Mithril | F5 | D, eternal | T6-T7 |

## 5. Collections that become tier keys (existing registry ids)
| Skill | Tier key collections |
|---|---|
| Mining | Cobblestone (+ the S1 group), Copper, Iron, Thorium, Cobalt, Adamantite, Mithril |
| Foraging | Oak (F1), Birch (F1), Maple (F2), Redwood (F3), Azure (F4), Frostwood or Crystalwood (F5); Tree Sap (Lantern) |
| Farming | Wheat, Carrot, Corn, Pumpkin, Tomato, Cotton, Rice, Potato (+ Seeds) |

## 6. Level pacing sketch
Using the live curves (Mining x2 early boost, class curve flattened): a tier's collection IV (about 1,000 of its base item) takes about 1-2 hours of focused gathering at the tier's level; a tier's **V-VI** (compressors, armor) takes 4-8 hours. So a **full 7-tier ladder is a 60-100 hour project** for each skill, in line with SkyBlock's pacing (tier numbers are Skyy's to set in the Collection-Unlocks draft).

## 7. UNVERIFIED / for the local session
| # | Check |
|---|---|
| 1 | The wood categories: which of the 33 log types the Farmer's Workbench counts as Softwood / Lightwood / Hardwood / Drywood / Darkwood / Redwood / Goldenwood (look at the `Bench_Farming` recipes and the `Wood_*` resource types in Assets.zip). My groups in 2.2 use the Bazaar price tiers instead; reconcile them with the real categories. |
| 2 | Whether the vanilla Wood armor is itself the "Softwood" step (then the ladder is 7, not 8). |
| 3 | Real breaking Quality for each ore (Copper, Iron, Thorium, Cobalt) and the Quality of every pickaxe / hatchet / hoe material, to confirm the tool-tier column. |
| 4 | Where each tree grows (biome / zone) and where each ore spawns, using the zone biome files; my zone assignments are inferred from names and the Mob-Levels refit. |
| 5 | The vanilla Farming Bench tier of each crop (Skyy locked "vanilla order"); the crop groups A-D copy the Bazaar's price order, check them against the bench recipes. |
| 6 | Whether Silver and Gold need a tier (the economy lock leaves them out of the tool ladder). |
| 7 | The hoe tiers: which hoe materials vanilla has (Crude, Copper, Iron, ...). |

## 8. Questions for Skyy
1. Are 5 tree tiers (F1-F5) right, with only F1 (+ the special Azure wood) in Zone 1? Or fewer (4)?
2. Should the gathering *armor* ladder for Mining and Farming ship together with Foraging armor, or one skill at a time (Foraging first, as locked)?
3. Do you want Silver / Gold as an optional "luxury" tier (jewelry, accessories) outside the tool ladder?
