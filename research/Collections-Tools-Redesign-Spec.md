# Collections rewards + tool upgrades redesign - build spec

Spec, 2026-10-16. Paper only, nothing built. Every number is a PLACEHOLDER and a Server Setup row (SkyWynn Menu -> Server Setup,
`tools/CONFIG-CONTRACT.md`; times in seconds) unless marked BUILD-TIME. Arithmetic checked in python (method given where it matters).
Builds on the live SET: SkyyCollections 0.2.20, SkyyGear 0.3.13 (farm01 is building 0.3.14 = Harvester for everyone), SkyySacks 0.8.12,
SkyySkills 0.4.44, SkyyTrees 0.3.18, SkyyBazaar 0.1.16, `tools/skyyench.py` (20 Enchanted items).
Replaces: `tools/skyyench.py` rule "No reverse recipe, ever" and `research/Gathering-Progression-Spec.md` 4.1 "Reverse recipe: none, ever"
(Skyy 2026-10-16 below); the 2026-10-06 lock "no Enchanted Blocks yet" (now asked for); the perk caps of SkyyGear 0.3.x `LL_PERKS`
(Speed 10, Fortune 10) and `tool.fortune.cap` 25.

## 0. Skyy's words this follows (word for word in `docs/answered/economy.md` + `skills.md`, 2026-10-16)

> COLLECTION REWARDS + TOOL UPGRADES REDESIGN (economy.md): "id like to make every collection give something more than just money, so we
> need to decide what recipes you unlock. (tools armor, enchanted versions of that item.) (we could do like skyblock does and compress
> further. 100 enchanted = 1 enchanted block (or similar variant that makes sense.) keep coins per collectiol nevel, but less than right
> now. and add the tool upgrade points. (remove the cap on the tools speed upgrade. like in the skill tree, lets have breaking power(amount
> of damage it does to the block. the higher it is the less hits.) and breaking/swing speed. (tool swings faster. needed to increase mining
> speed once a block breaks in 1 hit.) i wouldnt cap either. and id make the fortune caps really high too. (past 100% chance to drop
> double, it goes to a triple drop chance. so 200% is guaranteed 3 drops. no max %) when combining tools into multitools it takes the
> highest breaking power and breaking speed. and keeps the others where they are at. the multitool has all the modifiers from the hatchet
> and pickaxe. (farming tool works the same. though as we are scrapping the original tools, we just add the modifiers from both to the
> tool.)"

> ENCHANTED BACK + POCKET COMPACTOR (skills.md): "lets add a way to craft them back into the 100 normal items. so if i need copper but only
> have enchanted copper, i can craft it back to 100 copper. bonus points if you can make it automatic.) (and in the pocket dimension, i
> want an auto compactor you can unlock at rare or higher. (its an upgrade you have to buy once you unlock it. and its per pocket like the
> rarity.)"

> COLLECTION RANKS (skills.md): "show, announce, and give a few enchanted items." (rank amount x 2^k kept.)

Also followed (not re-decided): Enchanted ratio "Always 100" (2026-10-06); COINS NEVER SKIP COLLECTIONS OR BAGS (R3); lifelong tools -
upgrade only, never crafted (2026-10-12); upgrade costs the next tier's Enchanted material (2026-10-11); Enchanted Sticks in later
tool upgrades (2026-10-16); Harvester replaces hoe + sickle (2026-10-16, farm01); collections do not reset on rebirth; Fortune on all tiers.

## 0.1 Plain words (for Skyy)

- **Every collection tier now gives three things:** a smaller coin payout, **tool points** for that skill's lifelong tool, and **one
  unlock** (a recipe, a tool tier-up, an armor set, an accessory, an Enchanted item gift, the Enchanted recipe or the new Enchanted Block).
- **Enchanted Blocks:** 100 Enchanted = 1 Enchanted Block (a name that fits each item: Enchanted Hay Bale, Enchanted Iron Block ...).
- **Un-compress:** every Enchanted item crafts back into 100 of its base item (and a Block back into 100 Enchanted), anywhere, no bench.
  **Automatic:** when you craft in /craft or pocket crafting and you are short of Copper but hold Enchanted Copper (Void first, then
  inventory), it opens just enough of them for you.
- **Void Auto Compactor:** each Void category (Mining, Foraging, Farming ...) can buy its own Compactor once that category's bag is Rare or
  better. It turns every 100 base items you pick up into 1 Enchanted (and 100 Enchanted into a Block once you know the Block recipe).
- **Tools:** Breaking Power (fewer hits), Breaking Speed (faster swings, new) and Fortune have **no cap**; each level costs a little more
  than the last. Fortune past 100% rolls a third drop (200% = always 3 drops). Multitool / Harvester: keep the HIGHER Breaking Power and
  Breaking Speed, keep every other modifier of both tools.
- **Ranks** past the last tier give a few Enchanted items each.

## 1. Survey first (PROJECT-RULES 2)

| Mod (Skyy's Mods folder, read only) | Licence | What it does | Verdict |
|---|---|---|---|
| (no compactor mod exists) | - | nothing in the folder compacts or un-compresses | build our own |
| SalvageEverything 1.2.1 (CowMaster) | not found | data-only `Salvage_*` recipes at the salvager | learn: a reverse recipe is plain recipe JSON (our un-compress is too) |
| Dray's Leather+ | - | `Salvage_Leather_Light_From_Medium` - the only true "downgrade" recipe | learn (same idea, hand-written pair) |
| Multitools 1.2.9 (InkBlindCat) | MIT | pickaxe + hatchet items, already folded into SkyyGear | already ours - merge rule changes here |
| SimpleEnchantments 1.2.1 (MineAndCraft, Sorath) | not found in the jar | enchant tables, per-enchant ECS systems (Fortune, Durability...) | learn only; we already have Fortune + Power hooks. Licence check before any fold |
| LuckyMining 1.0.8 (Buuz135) | MIT | streak-based extra ore | learn (a fortune mechanic); nothing to take - our Fortune path exists |
| PJ-HyperPickaxes 1.3.7 | ARR | Fortune / vein / smelt in code | learn only |

Our own prior art reused: SkyyShards 0.4.1 Auto-Compactor I/II (per shard: `compactor.coins1/2`, `compactor.items1/2`, `coins:fn:take`,
100:1 from the ench table) is the model for the Void compactor purchase + step; SkyySkills 0.4.26 already rolls Fortune above 100% as
"whole part = guaranteed extra drops, rest = chance" (`perk.fortuneMax` 2.0) - exactly Skyy's 200% = 3 drops rule, it only needs the cap
lifted.

## 2. Engine facts this design rests on (VERIFIED unless marked)

| Fact | Source |
|---|---|
| Block health starts 1.0; each hit does the tool's `Tool.Specs[GatherType].Power`; hits = smallest n with n x Power >= 1. `DamageBlockEvent` fires before the damage and the engine re-reads `getDamage()` | `research/Tool-Levels-Spec.md` 2.1 (bytecode) |
| Vanilla pickaxe Rocks Power: Crude 0.25 (4 hits), Iron 0.5, Thorium 0.5; OreAdamantite Crude 0.05 / Iron 0.084 / Thorium 0.125 | Assets.zip `Server/Item/Items/Tool/Pickaxe/*.json` |
| SkyyGear multiplies Power in `GearToolHitSys` (DamageBlockEvent) = tool level curve (`tool.power.pickaxe` 1.0 at Lv 1 ... 2.2 at Lv 49) x rarity x the Speed perk (`lifelong.perkSpeed` 2% a level, max 10). Power is clamped at 100 | SkyyGear 0.3.13 `GearTool.stats` / `onDamage` |
| Swing: `Pickaxe_Attack` -> `Pickaxe_Mine` ~0.25 s of RunTimes (0.083 prepare + 0.083 hit + 0.084 pad); Primary default cooldown 0.35 s (`InteractionTypeUtils.getDefaultCooldown`). No swing-speed stat found (UNVERIFIED: not searched in the jar) | Assets.zip `Server/Item/Interactions/Weapons/Pickaxe/...`; `research/Swing-Speed-Spec.md` |
| SkyyTrees owns the pickaxe root override: 40 hidden effects `Skyy_Tree_Swing_Mine_01..40` pick a cooldown `0.35 / (1 + tier%)`, max +40% (0.25 s = the swing itself) | SkyyTrees 0.2.3+ / Swing-Speed-Spec |
| Fortune is posted by SkyyGear as `dd.<skill>` = Fortune / 100 into `skill:bonus:<uuid>`; SkyySkills rolls it: whole part = guaranteed extra drops, remainder = chance, capped by `perk.fortuneMax` (2.0, code clamp `Math.min(10.0, ...)`) | SkyySkills 0.4.26+ (line ~5560) |
| Tool points today: earned = skill level - 1 per skill (`GearLL.earned`), spent per perk; `LL_PERKS` order locked, saved by perk KEY | SkyyGear 0.3.13 |
| Void: 6 categories, rarity per category `rar.<Cat>` 0-3 (Normal, Unique, Rare, Legendary) + Omni; upgrade = `VoidStore.upgrade` (all-or-nothing, `VoidJob` save, `VOID-UPGRADE` log); unknown keys in `pd/<pkey>.properties` are kept by every version | SkyySacks 0.8.12 |
| Every Void change goes through `SackPool.add(k, id, n)`; intake paths (auto-pickup `PickGive.split`, `SweepTask.sweep`, `depositInv`) end in `noteIntake(k, ci, n)` | SkyySacks 0.8.12 |
| /craft + pocket crafting pay through `sacks:fn:craftPay` (Void first, then inventory, all-or-nothing, CRAFT-PAY / REFUND / COMMIT logs); bench crafting reads the Void through the BagMirror (36-slot mirror container, `wantedFor` / `rebuild`, `sync` books once) | SkyySacks 0.8.12 |
| Gathering armor recipes are open today (`KnowledgeRequired: false`); lifelong tool tier-ups have no collection gate | SkyyGear 0.3.13 |
| Bazaar prices an Enchanted item as a processed good from its recipe (100 x raw x (1 + premium)); quote band x1.10 buy / x0.90 sell | SkyyBazaar 0.1.16 |

## 3. Part A - Collections: every tier unlocks something

### 3.1 What every tier pays

| Part | Rule | Where |
|---|---|---|
| Coins | the new `tier.coins` table (3.2); Combat keeps `combat.coinMultiplier` 2 (no skill XP there) | collections.properties (row exists) |
| Skill XP | unchanged (`tier.xp` 500 III / 2,500 V / 10,000 VII, `tier.lastXp` 25,000) | unchanged |
| **Tool points** | `coll.toolPoints` (3.4) - DERIVED from reached tiers, never paid / saved | new bridge `coll:fn:toolPts` read by SkyyGear |
| **One unlock** | the tier grammar (3.3); a tier with nothing else gets an Enchanted gift (`item:<Ench>:<2 x tier>`, the 0.2.20 rule) | rewards.properties |

### 3.2 Coins - lower (row `tier.coins`, PLACEHOLDER: half of today)

| Tier | I | II | III | IV | V | VI | VII | VIII | IX | X | Sum B (10) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Now | 50 | 100 | 200 | 400 | 800 | 1,500 | 3,000 | 6,000 | 12,000 | 25,000 | 49,050 |
| **New** | 25 | 50 | 100 | 200 | 400 | 750 | 1,500 | 3,000 | 6,000 | 12,500 | 24,525 |

Already-paid tiers are never taken back (`_paid.<Id>` markers stay). One-time migration (section 8) rewrites only an untouched default line.

### 3.3 The tier grammar (one shape per curve; key collections)

Key collections = the ladder ones (Mining: Cobblestone, Copper, Iron, Thorium, Cobalt, Adamantite, Mithril; Foraging: Oak, Maple, Gumboab,
Redwood, Sallow, Azure; Farming: Wheat, Carrot, Cauliflower, Pumpkin, Tomato, Cotton, Potato). Built on `Gathering-Progression-Spec.md`
3.2-3.5 (rows marked live stay byte-for-byte).

| Tier | S (9) | R (8) | E (7) | B Cobblestone / Oak (10) |
|---|---|---|---|---|
| I | bag Normal on bag keys (live) / else Enchanted gift 2 | gift 2 | gift 2 | bag Normal (live) + gift 2 (live 0.2.20) |
| II | Enchanted gift 4 | gift 4 | **Enchanted recipe** | gift 4 |
| III | **Enchanted recipe** (live) + un-compress (always known, 4.1) | Enchanted recipe | **next tier TOOL TIER-UP** (gate) | Enchanted recipe (live) |
| IV | **next tier TOOL TIER-UP** (gate, 3.5) | tool tier-up | **gathering armor set** | Stone Brick (live) / Softwood armor |
| V | **gathering armor set** of this tier (+ bag Rare, live) | armor set | accessory Rare | bag Rare (live) + gift 10 |
| VI | accessory Rare (Prospector / Woodsman / Harvester talisman) / Unique Sigil (live on Wheat / Oak / Cobble) | accessory | **Enchanted Block recipe** | Sigil (live) |
| VII | **Enchanted Block recipe** (+ bag Legendary, live) | **Enchanted Block recipe** | capstone | **Enchanted Block recipe** + bag Legendary (live) |
| VIII | accessory Legendary | capstone | - | accessory Rare |
| IX | **capstone** (collection Fortune, Gathering-Progression 3.2) | - | - | accessory Legendary |
| X | - | - | - | capstone |

Non-key collections (other stones, sand, clay, other logs, other crops, fruit, mushrooms, Combat drops): their live rows stay (bricks at IV,
Shears / Crude Arrow, Lanterns on Tree Sap); every other tier gets the Enchanted gift of THEIR skill's tier-matched key item (a Shale
collection pays Enchanted Cobblestone; a Birch log pays Enchanted Oak; Combat pays coins x2 until Combat Enchanted items exist - question
3). The build GENERATES the full ~85-row table from this grammar (one function, asserted: every non-hidden collection, every tier, has
at least one non-coin token) and prints a review sheet for Skyy.

### 3.4 Tool points from collections (row `coll.toolPoints`, PLACEHOLDER)

- Key collection: **+1 point per tier reached**. Other collection of a gathering skill: **+1 at tiers III, VI, IX**.
- Points go to the SKILL of the collection's category (Mining -> pickaxe / multitool, Foraging -> hatchet / multitool, Farming -> Harvester;
  XP-routed collections (Ranching / Orchard / Fishing) give none until those skills have a lifelong tool; Combat none).
- DERIVED, never saved: SkyyGear earned = (skill level - 1) + `coll:fn:toolPts(pkey, skill)` (SkyyCollections counts reached tiers from the
  counts it already has). No payout, no marker, no dupe, rollback-safe; collections never reset, so these points survive rebirth.
- Totals at every tier (python, today's registry): Mining 58 key + 47 other = **105**; Foraging 54 + 82 = **136** (33 log collections);
  Farming 63 + 43 = **106**. Skill levels add 99. Foraging is higher - question 5.

### 3.5 Tool tier-up gate (the "tools" recipes)

Lifelong tools are never crafted, so the "tool recipe" a collection unlocks is the **right to tier up** the lifelong tool on the Anvil:
Thorium tier-up at Iron IV, Cobalt at Thorium IV, Adamantite at Cobalt IV, Mithril at Adamantite III (pickaxe); hatchets from the logs
(Gathering-Progression 3.4), Harvester from the crops (3.5). New reward token `tierup:<kind>:<Tier>`; SkyyCollections publishes the
profile's unlocked tier-ups on `coll:tierups` (pkey -> "pickaxe:Thorium,hatchet:Cobalt,..."); SkyyGear's Anvil shows a locked tier-up
as "Needs Iron collection IV (312 / 500)" (like the LOCKED RECIPES tab). Copper and Iron tier-ups stay open (Zone 1). No coin path (R3).

### 3.6 Armor recipes

The 68 gathering armor pieces get `KnowledgeRequired: true` and unlock at the tier in 3.3 (token `recipe:` as today; SkyyCollections'
known-recipe sync teaches them). Catch-up: at the first settle every profile is taught every armor recipe of tiers it already reached;
armor anyone already owns is never touched. (UNVERIFIED: the sync handles 68 more ids - it worked on ID.length for 20.)

### 3.7 Ranks past the last tier (Skyy: "show, announce, and give a few enchanted items")

- Rank k needs the last tier x `rebirth.rankFactor`^k (2, live). New: rank k pays **`rank.enchPerRank` x k Enchanted items (5 x k, cap 64)**
  of the collection's Enchanted item (non-key: its skill's tier-matched key item; Combat: coins = last-tier coins x k / 2). PLACEHOLDER.
- Marker `_paidrank.<Id>` (highest rank paid) on disk BEFORE the give; owed + retried while the inventory is full (the 0.2.13 item giver).
  Ranks already reached before this version are paid once at the first settle (catch-up, same marker).
- Example: Wheat last tier 20,000; rank 1 at 40,000 -> 5 Enchanted Wheat; rank 2 at 80,000 -> 10.

## 4. Part A2 + B - Enchanted Blocks and un-compress

### 4.1 Enchanted Blocks (second compression, ratio 100 BUILD-TIME)

100 Enchanted = 1 Block (= 10,000 base). Ids `Skyy_EnchBlock_<Key>`, quality `Skyy_Enchanted` (Value 4), stack 100, generated art (a
shiny cube of the Enchanted texture - skill `skywynn-art`, nothing vanilla committed). Table rows added to `tools/skyyench.py` (one
source: Collections ships, Sacks homes, Bazaar prices).

| Enchanted (20) | Block name (proposal) |
|---|---|
| Cobblestone | Enchanted Stone Block |
| Rubble | Enchanted Gravel Block |
| Copper / Iron / Thorium / Cobalt / Adamantite ingot | Enchanted <Metal> Block |
| Oak / Maple / Gumboab / Redwood / Sallow log | Enchanted <Wood> Heartwood |
| Wheat | Enchanted Hay Bale |
| Carrot | Enchanted Golden Carrot |
| Cauliflower / Tomato | Enchanted <Crop> Crate |
| Pumpkin | Enchanted Carved Pumpkin |
| Cotton | Enchanted Cotton Bale |
| Potato | Enchanted Baked Potato |
| Stick | Enchanted Stick Bundle |

Spent on (PLACEHOLDER, later rounds): lifelong tool tier-ups from Adamantite up (1 Block instead of 100 Enchanted), Legendary / Mythic
tool rarity upgrades, the top two gathering armor tiers, Legendary accessories, Void compactor cost (5.2). Bazaar: processed good from
its recipe like the Enchanted items (no new premium).

### 4.2 Manual un-compress (every Enchanted item -> 100 base; every Block -> 100 Enchanted)

| Field | Value |
|---|---|
| Recipe | `Skyy_Ench_<Key>` x1 -> base x100 (`OutputQuantity` 100 = one stack); `Skyy_EnchBlock_<Key>` x1 -> Enchanted x100. Generated from the same table |
| Where | Workbench "Compressing" tab AND pocket crafting (no bench) + /craft Crafting tab |
| Known | always (`KnowledgeRequired: false`) - anyone holding one (Bazaar, AH, gift) can open it |
| Output item | the table's base: ingots for metals, `Rock_Stone_Cobble`, `Rubble_Stone` (Enchanted Rubble accepts any rubble, gives plain stone rubble), the log, the crop, `Ingredient_Stick` |
| Collection credit | NONE (crafting is never a credit hook; the alias credit stays for GIVERS only) |
| Bazaar | the price builder must SKIP these reverse recipes when it derives prices (else base <- Enchanted <- base is a cycle); loop check: buy Enchanted 1.10 x 122 = 134 -> sell 100 base 0.90 x 100 = 90 = loss (premium 22%) - assert in the harness, both directions, Blocks too |
| `tools/skyyench.py` | the "No reverse recipe, ever" rule line is replaced by this (Skyy 2026-10-16) |

### 4.3 AUTOMATIC un-compress (Skyy: "bonus points if you can make it automatic")

Player switch `/settings -> Crafting -> Auto un-compress` (default ON). Opens Enchanted only - never a Block automatically (question 7).

| Path | Hook | How | Risk / phase |
|---|---|---|---|
| /craft (all tabs) + pocket crafting | `sacks:fn:craftPay` (SkyySacks, the one all-or-nothing payer) | before paying: for each input short by d, if the player holds `Skyy_Ench_<base>` (Void first, then inventory): open n = ceil(d / 100) in the pool (`SackPool.add(-n Ench)`, `+100n base`) inside the same rollback; leftover base stays in the Void (no room -> inventory -> else refuse "Not enough room to open Enchanted Copper"); log `CRAFT-UNPACK`; the craft list (`craftHave`) counts base + 100 x Enchanted so the CRAFT button lights | phase 1, safe (existing transaction) |
| Bench crafting (BagMirror) | `wantedFor` / `rebuild` + `sync` | mirror shows base as base + 100 x Enchanted (max 4 stacks); at `sync`, a consumption above the real base opens ceil(extra / 100) Enchanted and books the rest back - same single booking | phase 2, needs a probe (dupe risk; mirror counts must match exactly) |
| Inventory-only (no Void) | same as /craft | uses inventory Enchanted when the Void has none | phase 1 |

Never with a recipe whose OUTPUT is that Enchanted item (no open-then-recompress loop). Counts before and after (AGENT-BRIEF rule).

## 5. Part C - Void Auto Compactor (per category, Rare+, bought once)

### 5.1 Rules

| Rule | Value |
|---|---|
| Per | Void category (Mining, Foraging, Farming, Fishing, Combat, Smithing) - "per pocket like the rarity" |
| Unlock | that category's rarity Rare or higher (`rar.<Cat>` >= 2) or Omni; below it the row shows "Reach Rare to unlock" |
| Buy | once per category per profile; cost row `pd.compactor.cost.<Cat>` PLACEHOLDER = **25,000 coins + 32 Enchanted of the category's first key item** (Mining: Enchanted Cobblestone, Foraging: Enchanted Oak, Farming: Enchanted Wheat); `coins:fn:take` first (the SkyyShards call), items Void-first, all-or-nothing + refund (`VoidStore.upgrade` pattern); never coins only (R3 - the rarity gate is the real gate) |
| Categories with no Enchanted item yet (Fishing, Combat, Smithing) | row hidden ("Nothing to compact yet") until the table has items for them |
| What it compacts | every base item of that category with a `tools/skyyench.py` row whose Enchanted RECIPE the profile knows (collection tier); then Enchanted -> Block when the Block recipe is known |
| When | on every positive intake (after `noteIntake`: auto-pickup, Sweep, Deposit, Deposit all, shard Collect into the Void); while base >= 100 + keep: base -100, Enchanted +1 (one `SackPool.add` pair under `BagMirror.beforeTake / afterTake`); not on a timer |
| Per item | toggles on the Void page (On / Off per item, default On) + "keep" amount per item (default 0, PLACEHOLDER) |
| Space | 1 Enchanted = 1 space (Bags-v2 Q5) - compacting frees 99 |
| Credit | none (the base already counted when gathered) |
| Interplay | auto un-compress opens only what the craft needs; leftover < 100 never re-compacts at once; the compactor never runs inside a craft transaction |

### 5.2 Saved data (SkyySacks `pd/<pkey>.properties`, unknown keys kept by every version)

`comp.<Cat>=1` (bought), `compOff.<Cat>=<id,id>` (switched off), `compKeep.<id>=<n>`. Purchase logged `VOID-COMPACTOR` (crafts.log);
each step `VOID-COMPACT <id> -100 / +1` (rate-limited summary per minute). Rollback: an older SkyySacks ignores the keys, the Enchanted
items stay where they are; the coins are not refunded (admin note in the rollback floor comment).

## 6. Part D - Tool upgrades

### 6.1 The lines (SkyyGear `LL_PERKS`; order is locked -> the new line is APPENDED; saved by key)

| Line (key) | Effect per level | Max | Cost of level n | Tools |
|---|---|---|---|---|
| **Breaking Power** (`spd`, renamed from "Speed"; same meaning) | +5% Power (`lifelong.perkSpeed` 2 -> 5, PLACEHOLDER) | **none** (was 10) | `1 + floor((n-1) / lifelong.costStep)`, costStep 10 | pickaxe, hatchet, multitool, Harvester (new: farm tools get it - crops with hits) |
| **Breaking Speed** (`swing`, NEW) | +3% swing speed (`lifelong.perkSwing` 3) | none | same curve | pickaxe, hatchet, multitool, Harvester |
| **Fortune** (`fort`) | +2 Fortune (`lifelong.perkFortune` 1 -> 2) | **none** (was 10) | same curve | all gathering tools + pole |
| Wisdom, Vein Mine, Tree Feller, Steady Line, can perks | unchanged | unchanged | unchanged | unchanged |

Cost curve (python): levels 10 / 20 / 30 / 40 / 50 / 60 cost 10 / 30 / 60 / 100 / 150 / 210 points total; 100 points buys level 40, 200
buys 58. Caps removed: `tool.fortune.cap` 25 -> 0 = none; the Power clamp 100 -> none (a sanity guard `tool.power.max` 1000 stays as a
row); SkyySkills `perk.fortuneMax` 2.0 -> 0 = none and the code clamp `Math.min(10.0, ...)` goes (a guard `perk.fortuneGuard` 100 extra
drops stays). Extra drops past 1 are given as ONE stack of n x the drop (not n loops). `collections.doubleDrops=false` stays (extra drops
never count for collections).

### 6.2 Breaking Power -> hits (fewer hits)

Hits = ceil(1 / (vanilla Power x Gear multiplier x (1 + BP%))). Example (python): Thorium pickaxe Lv 49 (x2.2) on Adamantite ore
(0.125): BP 0 = 4 hits, BP level 2 (+10%) = 3, level 4 (+20%) = 2, level 12 (+60%) = 1. Once a block breaks in 1 hit more Power does
nothing - that is where Breaking Speed takes over (Skyy's words). The tier gate (`gate.nextFactor` 0.4) still multiplies after.

### 6.3 Breaking Speed -> swing interval

Interval = 0.35 s / (1 + swing%) (swing% = Gear line + SkyyTrees Mining / Chopping Speed nodes, summed). +40% = 0.25 s (4 / s), +100% =
0.175 s (5.7 / s), +200% = 0.117 s (8.6 / s), +400% = 0.07 s (14.3 / s).

- **One writer:** SkyyTrees already owns the pickaxe root override and its 40 swing effects. SkyyGear publishes `gear:swing:<uuid>`
  (Double %, the held tool's line); SkyyTrees adds it to its own node % and picks the bucket. Buckets become GENERATED: 5% steps to
  `swing.maxPercent` (default 1000 = 200 effects, row; "no cap" in practice = the engine tick).
- **Past +40%** the swing animation itself (0.25 s of RunTimes) is the floor: SkyyTrees ships re-timed copies of `Pickaxe_Mine` (each
  RunTime / (1 + s)) per bucket, chosen by the same EffectCondition. **UNVERIFIED (probe P1):** that the client plays a re-timed swing
  smoothly and the server accepts a hit every 0.07 s; the hatchet, Harvester (sickle) and multitool roots are overridden the same way
  (UNVERIFIED which of those SkyyTrees already overrides).

### 6.4 Multitool and Harvester merge (replaces the 0.2.21 "within caps" merge for lifelong tools)

| Part | Rule |
|---|---|
| Breaking Power, Breaking Speed (perk levels AND rolled power lines `mpow` / `cpow`) | the HIGHER of the two tools; the lower tool's spent points on that line are REFUNDED to its skill's free points (nothing lost) |
| Every other perk (Fortune per skill, Wisdom per skill, Vein Mine, Tree Feller) | kept as it is on its own tool - the multitool carries the pickaxe's AND the hatchet's (Mining Fortune and Foraging Fortune are separate lines) |
| Rolled modifier lines | all of both kept (no "max lines" trim, no cap clamp for the uncapped stats) |
| Rarity | the best of the two (live rule) |
| Paying later | a shared line (Power, Speed) can be paid from either skill's free points (Mining first, then Foraging; the page says which) |
| Harvester (hoe + sickle, farm01 0.3.14) | same rule ("we just add the modifiers from both"): higher Power / Speed, every other line of both. If farm01's one-time merge used the old "within caps" rule, the 0.3.15 round re-merges once from its saved pre-merge copy (marker) - checked when farm01 lands |

## 7. Build rounds (biggest player-facing first, Skyy: "start building the queued answers, biggest player-facing ones first")

| Round | Mods | What | Size |
|---|---|---|---|
| T1 tools | SkyyGear 0.3.15 + SkyySkills 0.4.45 | 6.1, 6.2, 6.4 (uncapped lines, cost curve, the Swing line stored + shown, merge rule, refunds), Fortune uncap + bulk extra drops, reads `coll:fn:toolPts` when present | full (economy + saved points) |
| T2 swing | probe P1 first, then SkyyTrees 0.3.19 (+ Gear bridge) | 6.3 generated buckets + re-timed swings | full + probe |
| C1 collections | SkyyCollections 0.2.21 + SkyyGear (tier-up gate read) | 3.2 coins migration, 3.3 generated grammar (+ review sheet), 3.4 `coll:fn:toolPts`, 3.5 `tierup:` + `coll:tierups`, 3.6 armor knowledge + catch-up, 3.7 rank rewards | full (saved data, migration) |
| V1 compactor | SkyySacks 0.8.13 | section 5 | full (items could be lost / duped) |
| E1 blocks + un-compress | SkyyCollections + SkyySacks (homes) + SkyyBazaar (prices, loop check) + `tools/skyyench.py` + art | 4.1, 4.2 | full |
| E2 auto un-compress | SkyySacks | 4.3 phase 1 (craftPay), then phase 2 (BagMirror, probe) | full |
| later | all | Enchanted items for every collection (question 3), Combat / Fishing compactors | spec first |

T1 and C1 can run in parallel (different mods; C1's bridge is optional for T1). V1 needs nothing else. E1 before E2.

## 8. Saved data + migrations

- **collections.properties `tier.coins`:** one-time, only the line still exactly `50,100,...,25000` -> the new line; hand-edited kept +
  logged; verified History copy first; change-log row with Undo; run-once marker; bytes + line endings kept (PROJECT-RULES 4).
- **rewards.properties:** new tokens appended to keys under the CollToolMig machinery (untouched default lines only, marker `RW_MARK5`);
  `tierup:` / rank tokens are new keys -> an old version logs "unknown token" and skips them (rollback-safe).
- **Profile collection files:** `_paidrank.<Id>`, catch-up marker for armor knowledge; old versions keep unknown meta lines.
- **SkyyGear lifelong data:** perk levels saved by key -> raising the max needs no migration; the new `swing` key is ignored by older
  versions (points shown as spent there: rollback note "reset tool points after a rollback below 0.3.15"). `lifelong.perkSpeed` 2 -> 5 and
  `perkFortune` 1 -> 2: one-time row migrations (untouched defaults only) - a BUFF to existing tools, no refund needed.
- **SkyySacks:** section 5.2 keys only.
- **SkyySkills:** `perk.fortuneMax` 2.0 -> 0 (none): one-time, untouched default only.

## 9. UNVERIFIED (probe or build-time check)

1. Re-timed `Pickaxe_Mine` copies play smoothly on the client and the server accepts hits every ~0.07 s (P1). Which tool roots SkyyTrees
   already overrides (hatchet / sickle / multitool).
2. A hard engine floor on swing interval (server tick) - sets the practical `swing.maxPercent`.
3. BagMirror auto un-compress books exactly once (phase 2 probe, count before / after).
4. The known-recipe sync copes with 68 armor ids + 20 Block recipes + 40 reverse recipes.
5. Crafted output (un-compress) never reaches a collection credit path (expected: crafting is not a hook - assert in the harness).
6. `coins:fn:take` argument shape for the compactor purchase (copy SkyyShards 0.4.1 ~line 3384).
7. Vanilla block / model fitting each Enchanted Block (hay bale, crate) - else a generated cube.
8. How SkyyGear 0.3.x handles earned < spent after a rebirth (collection points soften it; check before T1).

## 10. Questions for Skyy (today's default in [brackets])

1. Coins per collection tier: half of today (25 ... 12,500)? [yes, half]
2. Tool points per collection tier: +1 per tier on key collections, +1 at III / VI / IX on the others? [yes]
3. Should EVERY collection (Sand, Clay, Bone, Hide, other logs / crops) get its own Enchanted item, or do non-key collections pay their
   skill's key Enchanted item as gifts? [gifts now; own Enchanted items later in a separate round]
4. Enchanted Block names (Hay Bale, Heartwood, Golden Carrot, Baked Potato ...) as in 4.1? [yes]
5. Foraging gets more collection points (33 log collections, 136 vs ~105). Even them out (cap 110 per skill)? [no cap]
6. Breaking Power +5% / Breaking Speed +3% / Fortune +2 per level, each level costing 1 more point every 10 levels? [yes]
7. Auto un-compress: open Enchanted items only, never Enchanted Blocks? [Enchanted only]
8. Void Compactor price: 25,000 coins + 32 Enchanted of the category's first key item, once per category? [yes]
9. Compactor "keep" amount per item: 0 (compact everything, auto un-compress covers crafting)? [0]
10. Tool tier-ups from Thorium up need the collection tier (Iron IV for Thorium ...); Copper / Iron stay open? [yes]
11. Gathering armor recipes become collection unlocks (taught at once to everyone already past the tier)? [yes]
12. Rank rewards: 5 x rank Enchanted items (cap 64)? [yes]
13. Multitool merge: refund the lower tool's Breaking Power / Speed points? [yes, refund]
