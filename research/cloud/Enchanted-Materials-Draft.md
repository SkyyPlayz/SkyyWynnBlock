# Enchanted (compressed) materials - draft

Cloud draft, 2026-10-06. Skyy's direction (2026-10-05): "i want to use skyblocks enchanted iron and enchanted cobble (basically compressed materials) ... all the collection levels unlock things that progress you".
Builds on `SkyBlock-Gathering-Progression.md` (SkyBlock: 160 base = 1 Enchanted; Compactor at Cobblestone V, Super Compactor at Cobblestone X), `Gathering-Tiers-Draft.md` and `Collection-Unlocks-Draft.md`.
Money rules from `docs/log/2026-10.md` (SkyyBazaar 0.1.3 / 0.1.4: crafted items priced as inputs x ratio + a premium; an exact linear-program loop check over 2,252 recipes, tightest 0.9818 at premium 20%).
Item ids, bench names and the Bazaar's internals are UNVERIFIED (no game files).

## 0. The design in 8 lines

1. **Enchanted X = 160 X** (SkyBlock's ratio), crafted at a bench or by an accessory, for every **key material** of the three skills (about 40 items, section 2).
2. **Enchanted Block = 160 Enchanted X** (= 25,600 base), only for the materials where it matters (metals, key logs, key crops).
3. Enchanted items are **ingredients**: tools, armor sets, bags, Pocket Shard upgrades and accessories ask for them (section 4).
4. They count for collections **at their base amount**, and only when **obtained** (drop / Pocket Shard / loot), **never when crafted** (crafting only moves the items you already counted).
5. They are Bazaar products at `ratio x base x (1 + premium)` with a **small premium (10%)**: convenient, no buy -> craft -> sell loop, and almost no extra coin creation.
6. Trees and crops are **grouped** (one Enchanted per tree tier / crop group where possible) so there are not 33 + 14 variants.
7. Higher tiers compress **more slowly** by design: the Block is only worth it for the top tiers.
8. A **Compactor** (collection-unlocked) automates it, as in SkyBlock.

## 1. Which materials get an Enchanted form

### 1.1 Mining (key collections)
| Material | Enchanted form | Enchanted Block | Unlock (collection tier, see Collection-Unlocks) |
|---|---|---|---|
| Cobblestone (the S1 stone group: Sand, Rubble, Clay, Sandstone get **their own** Enchanted forms: Enchanted Sand, Enchanted Rubble, ...) | Enchanted Cobblestone | Enchanted Cobblestone Block | Cobblestone IV; block at VIII |
| Copper Ore | Enchanted Copper | Block | Copper V; Block IX |
| Iron Ore | Enchanted Iron | Block | Iron V; Block IX |
| Thorium Ore | Enchanted Thorium | Block | Thorium V; Block VIII |
| Cobalt Ore | Enchanted Cobalt | Block | Cobalt V; Block VIII |
| Adamantite Ore | Enchanted Adamantite | Block | Adamantite IV; Block VII |
| Mithril Ore | Enchanted Mithril | Block | Mithril IV; Block VII |
| Onyxium Ore (later) | Enchanted Onyxium | Block | later |
| Other stone groups (S2 / S3) | one Enchanted per group key stone: Enchanted Slate, Enchanted Basalt | none | their group's IV |
| Crystal Shards, Gemstones | no Enchanted forms (they are special, rare drops) | - | - |
| Silver, Gold | optional Enchanted Silver / Gold for jewelry (later) | - | - |

### 1.2 Foraging (grouped, not per log)
| Tree tier | Enchanted form | Made from | Block |
|---|---|---|---|
| F1 Common woods | **Enchanted Common Wood** (display name by key log: "Enchanted Oak Wood") | 160 logs of **any F1 species** | Enchanted Common Wood Block |
| F2 Uncommon woods | Enchanted Hardwood | 160 of any F2 species | Block |
| F3 Northern woods | Enchanted Redwood | 160 of any F3 species | Block |
| F4 Strange woods | Enchanted Azurewood | 160 of any F4 species | Block |
| F5 Elemental woods | Enchanted Crystalwood | 160 of any F5 species | Block |
| Plant Fiber | Enchanted Fiber (Rope) | 160 fiber | - |
| Tree Sap | Enchanted Sap (Resin) | 160 sap | - |
| Stick | Enchanted Stick | 160 | - |
A mixed recipe ("any species of the group") keeps the bag and bench simple and means 5 woods instead of 33; each log still counts toward **its own** collection (the Enchanted item remembers its mix only as a "share" by proportional counting: simplest rule = **each Enchanted Wood counts 160 toward the collection of the group's KEY log**; see section 5).

### 1.3 Farming (grouped by crop group)
| Crop | Enchanted form | Block |
|---|---|---|
| Wheat | Enchanted Wheat -> **Enchanted Hay Bale** (the block) | the Hay Bale |
| Carrot, Corn, Lettuce | Enchanted Carrot, Enchanted Corn, Enchanted Lettuce | none |
| Cauliflower, Turnip, Aubergine, Pumpkin (group B) | Enchanted Pumpkin (key), others per crop | Pumpkin Block |
| Chilli, Tomato, Cotton, Rice (group C) | Enchanted Tomato / Cotton / Rice | none |
| Potato, Onion (group D) | Enchanted Potato / Onion | none |
| Seeds | Seed pouch (stackable bag) - not Enchanted | - |
About 14 Enchanted crop items, 2 Blocks (Hay Bale, Pumpkin). Mushrooms, Cactus, berries and fruit have **no** Enchanted forms (they are food ingredients).

Totals: about 12 mining + 8 foraging + 14 farming = **about 34 Enchanted items + ~14 Blocks**.

## 2. Recipes and where you craft

| Option | How | Recommended |
|---|---|---|
| **A: bench recipes** | a normal bench recipe `160 X -> 1 Enchanted X` at the Workbench (the "Accessories & Bags" tab exists; add a "Compressing" tab) | **yes (start here)** |
| B: Compactor accessory | a collection-unlocked item in the bag / accessory slot that compresses on pickup (like SkyBlock's Personal Compactor): Compactor (blocks), Super Compactor (Enchanted), Personal Compactor (auto) | yes, tied to collections (Cobblestone V / X) |
| C: Pocket Shard upgrade | the shard compacts its own output (collected items are Enchanted) | yes (Pocket-Shards-Spec) |
| D: /craft | **no** (/craft is being removed: Pocket Dimension kit) | no |
**UNVERIFIED:** a bench recipe with a 160-item input must fit Hytale's recipe format (stack size is 64 or 100? and bench recipes may cap ingredient counts). If not, the fallback is the Compactor-only route (the Compactor accessory compresses on pickup, no bench recipe needed) or a two-step recipe (10 piles of 16 -> compressed pile, then compressed piles -> Enchanted). Check first.

## 3. Stack sizes, bags and bag handling
| Rule | Value |
|---|---|
| Enchanted stack size | **64** (display "x64"), so one slot holds 10,240 base items |
| Block stack size | 16 |
| Bags (SkyySacks) | each Enchanted item belongs to the **same category bag as its base** (a Mining bag holds Enchanted Iron; a Foraging bag Enchanted Wood). `SackDefs.catOf` gets a prefix rule `Skyy_Ench_*` -> the base's category (table built from the registry) |
| Bag capacity | Enchanted items count like any item: **1 slot = 64 items**; the point is that one slot now holds 160x more value |
| Auto-collect | bags pick Enchanted items up like their base item |
| Withdraw | taking Enchanted items out of a bag follows the live "withdrawn items stay out" rule |
| Pocket Dimension release (CurseForge mod) | Enchanted items belong to SkyyCollections / SkyWynn, **not** to the standalone Magic Bags mod |

## 4. What asks for them (the ladder)
Tier-up recipes use the **previous or current tier's** Enchanted item as an extra ingredient (SkyBlock: Jungle Axe = 3 Enchanted Jungle Wood):

| Recipe | Extra ingredient |
|---|---|
| Tier 2 tool (Iron pickaxe / hatchet / hoe) | 1 Enchanted of tier 1 (e.g. Enchanted Copper) |
| Tier 3 tool | 1 Enchanted of tier 2 |
| Tier 4 | 2 |
| Tier 5 | 2 |
| Tier 6 | 3 |
| Tier 7 | 4 |
| Gathering armor set (4 pieces) | 24 Enchanted of the tier's material + the vanilla armor ingredients (SkyBlock's Farm Armor needs 24 Enchanted Hay Bales) |
| Bag upgrades (Unique -> Rare ...) | 1 Enchanted of the bag's key material per step (on top of "previous bag") |
| Pocket Shard tiers | Tier VI+ uses Enchanted; Tier XI uses Enchanted Blocks |
| Accessories (Lantern, Haste) | 1 Enchanted of the accessory's key material |
| Compactors | SkyBlock: 32 Enchanted Cobblestone + 32 Enchanted Redstone (Hytale has no redstone) -> **32 Enchanted Cobblestone + 8 Enchanted Copper** |
Cost feel: 24 Enchanted = 3,840 base items (about 4-8 hours of focused gathering per armor set), 1 Enchanted tool part = 160 base (about 10 minutes).

## 5. Collection credit (the exact rule)
| Case | Credit |
|---|---|
| You craft Enchanted X from 160 X | **nothing new** (the 160 X already counted when you got them) |
| You obtain an Enchanted X from a drop, Pocket Shard compaction, reward or loot | **+160** to X's collection |
| You obtain an Enchanted Block | **+25,600** |
| Mixed-species Enchanted Wood (any of group F1) | **+160 to the group's key log collection** (Oak for F1, Maple F2, Redwood F3, Azure F4, Frostwood F5) |
| Withdrawing from a bag / buying on Bazaar / AH / NPC | nothing (existing rule) |
The "obtained, not crafted" rule is how SkyBlock avoids double counting while Enchanted items from minions still count.

## 6. Bazaar prices (the loop check)
The Bazaar prices a crafted product as `inputs x ratio + premium`. Instant buy `= base x factor x 1.10`, instant sell `= base x factor x 0.90`, factor clamped 0.25-4.0. A buy -> craft -> sell loop pays if
`sell(Enchanted) x 1 > buy(160 base)`, i.e. `0.90 x (1 + premium) x 160 > 1.10 x 160`, i.e. **premium > 22.2%**. At 20% the margin is 0.9818 (the live tightest); with the Bazaar's ~2% multi-player demand drift that is too tight.
**Proposal: premium 10% per compression step** (margin 0.90). It also keeps coin creation small: crafting 160 ore into an Enchanted item and selling it pays **10% more** than selling the ore (a Block 21%), the price of convenience.

| Material | base | Enchanted (160 base) | Enchanted Block (160 Enchanted) | block vs 25,600 base |
|---|---|---|---|---|
| Cobblestone / Sand / Fiber | 1 | 176 | 30,977 | 1.21x |
| Copper Ore | 5 | 881 | 155,056 | 1.21x |
| Iron Ore | 16 | 2,816 | 495,617 | 1.21x |
| Thorium Ore | 48 | 8,448 | 1,486,849 | 1.21x |
| Cobalt Ore | 144 | 25,345 | 4,460,720 | 1.21x |
| Adamantite Ore | 480 | 84,480 | 14,868,481 | 1.21x |
| Mithril Ore | 1,440 | 253,441 | 44,605,616 | 1.21x |
| Onyxium Ore | 3,712 | 653,312 | 114,982,913 | 1.21x |
| Common wood (F1) | 3 | 528 | 92,929 | 1.21x |
| Uncommon wood (F2) | 8 | 1,408 | 247,809 | 1.21x |
| Northern wood (F3) | 20 | 3,521 | 619,696 | 1.21x |
| Strange wood (F4) | 48 | 8,448 | 1,486,849 | 1.21x |
| Elemental wood (F5) | 128 | 22,528 | 3,964,929 | 1.21x |
| Crop A (Wheat, Carrot, Corn) | 2 | 352 | 61,953 | 1.21x |
| Crop B (Pumpkin ...) | 6 | 1,056 | 185,857 | 1.21x |
| Crop C (Tomato, Cotton, Rice) | 16 | 2,816 | 495,617 | 1.21x |
| Crop D (Potato, Onion) | 40 | 7,041 | 1,239,216 | 1.21x |
| Tree Sap | 4 | 704 | 123,905 | 1.21x |
(Base prices are the 2026-10-04 / 05 locks in docs/answered/economy.md.) The highest product, the Onyxium Block at 115M, is under the Bazaar's per-product ceiling (1e9).

### 6.1 Other money checks
| Risk | Check |
|---|---|
| Un-compress loops | there are **no** reverse recipes (Enchanted -> base) |
| Enchanted -> tool/armor -> salvage | tool/armor ingredients include Enchanted items; **salvage must not return Enchanted items** (the Bronze salvage loop in 0.1.3 was exactly this class of bug) |
| Cooking: crops -> food | food crafts use base crops only; no Enchanted in food |
| Bazaar quantity cap | the largest single trade is 100,000 items; Enchanted Blocks make big trades small (fine) |
| Shop sell-back | NPC sell-back (25% of base) applies to base items; Enchanted items sell at `160 x 0.25 x base` only up to the daily cap (NPC-Shops-Spec) |
| Auction House | Enchanted items may be listed (not "Bazaar items"); AH refuses Bazaar items by default - decide if Enchanted are exempt |

## 7. Server Setup rows (sketch)
`ench.enabled`, `ench.ratio` (160), `ench.blockRatio` (160), `ench.stack` (64), `ench.blockStack` (16), `ench.bazaarPremium` (10), per-material table (id, base item(s), Enchanted id, Block id, unlock tier), `ench.collectionRule` (obtained / crafted), `ench.compactor.*`.

## 8. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | Whether a bench recipe can take 160 of one ingredient (and 160 Enchanted for the Block) and how it handles a count above one stack. The fallback is the Compactor-only route. |
| 2 | New item ids + icons: ~34 Enchanted + ~14 Blocks. They can share one model with a tint (the "enchant glint" in vanilla?) - check the item glow / effect support. |
| 3 | `SackDefs.catOf` + `SkyyCollections` registries must learn the Enchanted ids (a generated table from this spec). |
| 4 | The Bazaar's per-product price ceiling and the multi-step premium maths (Bazaar auto-prices); rerun the LP loop check with the new recipes (2,252 + new ones). |
| 5 | Pocket Shard compaction upgrade and Compactor accessory as separate builds. |
| 6 | Whether "any species of group" recipes are possible (resource types), or whether there must be a recipe per log (then 5 Enchanted woods x species = too many; use resource types). |

## 9. Questions for Skyy
1. Premium per compression step: 10% (recommended), or 15-20% like ingots?
2. Enchanted Wood from **any species of the group** (5 woods), or one per species (33)? (Recommended: group.)
3. Do you want Enchanted Blocks for all materials, or only the top tiers? (Recommended: metals + key logs + wheat/pumpkin.)
