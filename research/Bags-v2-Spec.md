# Bags v2 - build spec (one Pocket Dimension, storage levels, rarity upgrades)

*Local spec 2026-10-10. Spec only: nothing built. Owner: Skyy (they/them). Base: SkyySacks 0.7.16 (the SET pin) plus SkyySacks 0.7.17,
which another round is building right now (`research/Requip-Smithing-Spec.md` section 5). SkyyCollections 0.2.8 (the SET pin).
All numbers marked PLACEHOLDER are Server Setup rows: Skyy or an owner can change them in game.*

**In plain words:** you get ONE bag, the Pocket Dimension. It has a storage page per category (Mining, Foraging, Farming, Fishing,
Combat, Smithing). Each category has a **level** that rises on its own as you collect more items of that kind, and a **rarity** you
raise with an **Upgrade** button that costs items. Space = level x rarity multiplier, counted as a total number of items per category.
Old bags turn into the starting rarity, everything inside them stays, and nothing is lost.

## 0. Decisions this spec follows

From `docs/answered/bags.md`, word for word (trimmed with ...). The 2026-10-10 lines are the newest and win over everything older.

| Line (status, date) | Skyy said | Means here |
|---|---|---|
| REQUEST 2026-10-10 (Bags v2) | "still have it upgrade from collection, but its based on the total number of items in that category you have collected. (one pocket dimension bag. and each storage type level up and upgrades automatically with your collection level.) then have an upgrade button, where it costs so many items from each collection to upgrade the rarity, which increases a storage multiplier. so its Storage level x rarity multiplier.) this way your storage constantly goes up as you use it. and you can upgrade it." | the whole design: sections 1-3 |
| LOCKED 2026-10-10 (popups) | old crafted bags "Convert + refund (Recommended)" (each bag's rarity becomes its category's starting rarity, contents move into the Pocket Dimension, nothing lost) | section 4 |
| LOCKED 2026-10-10 (popups) | capacity "Item limit per category (Recommended)" (e.g. Mining Lv 14 x Rare 2.0 = 2,800 items across all mining materials) | 100 items per level (section 2), Rare = x2.0 |
| LOCKED 2026-10-10 (popups) | Omni "Becomes 'Omni' rarity (Recommended)" (top rarity for every category, unlocked by all categories at Legendary, biggest multiplier) | section 2.3 |
| R3 LOCKED 2026-10-02 | "COINS NEVER SKIP COLLECTIONS OR BAGS" | each rarity step also needs a storage LEVEL (earned only by collecting), so Bazaar-bought items alone can never buy a rarity |
| R2 LOCKED 2026-10-02 | "bags keep collecting from the MAIN inventory only" | pickup unchanged |
| R3 LOCKED 2026-10-02 | "auto-collect LEAVES ALONE THE AMOUNT YOU TOOK" | kept counts unchanged |
| R4 LOCKED 2026-10-02 | "STACK AUTO-REFILL from bags with a player setting ... HOTBAR ONLY / FULL INVENTORY / OFF" | refill unchanged (default Hotbar only) |
| LOCKED 2026-10-03 (general rule) | "if it goes in the bag, it goes in a matching section in the bizzar." | the new Fishing category gets a Bazaar Fishing section (section 5) |
| LOCKED 2026-09-30 | "id keep cooked food out" | cooked food stays out (switch bags.cookedFood, default off) |
| LOCKED 2026-10-01 | "Charcoal goes in the Smithing bag" | Charcoal = Smithing |
| VERIFIED 2026-10-03 | "the crafting in benches from your sack works perfectly even in multiplayer." | the bench link stays as it is |
| REQUEST 2026-10-07 + LOCKED 2026-10-08 | "i want the pocket dimension to be a bag in the hot bar icon ..."; "mouth stays open while you hold it." | the one bag keeps the 0.7.14 / 0.7.16 look, hold pose and swirl |

**Replaced by Bags v2 (older lines, newer line wins):** R4 "carrying 2-3 bags of the same type ADDS their space together"; popup batch 4
"carried bags of one type -> Keep unlimited"; 2026-10-08 "bags stay separate types (NOT all Omni-style)"; the bag recipe ladders
(Normal I / Unique III / Rare V / Legendary VII, Mining from Cobblestone, fiber T1 recipes, Omni hidden until all Legendary). There
are no bag recipes any more. The rarity, the emblem colours and the Omni idea live on as the category rarity.

## 1. Categories

### 1.1 What goes where (today's bag lists, one table)

Today's `SackDefs.homeOf` stays the one rule; v2 changes only two rows (marked).

| Category | Items (id families) | Change vs 0.7.16 |
|---|---|---|
| **Mining** | `Ore_*`, `Rubble_*`, `Rock_*` (cobbles, ice, salt, gem blocks), `Soil_*` (sand, clay, dirt) | **+ `Ingredient_Crystal_*`** (the Crystal collection; today it stays in the inventory) |
| **Foraging** | `Wood_*` (logs, planks), Stick, Plant Fiber, Tree Bark, Tree Sap | - |
| **Farming** | `Plant_*` (crops, seeds, fruit, mushrooms, cactus, petals), raw meat `Food_*_Raw`, `Food_Egg*`, Essence of Life, Poop. Cooked food stays out | fish leave (next row) |
| **Fishing** (new) | `Fish_*`, `Food_Fish_Raw` + Uncommon / Rare / Epic / Legendary | **moved from Farming**. SkyyFishing whole fish (`SkyyFishing_Fish_*`, weight metadata, stack 1) never go in: an item with metadata never pools |
| **Combat** | Bone, Chitin, Venom / other sacs, Feathers, Voidheart, Boom Powder, every `Ingredient_*_Essence` | - |
| **Smithing** | bars / ingots, leather, hides, cloth bolts, fabric scraps, leather strap, iron stud, Charcoal | - |
| (later) Enchanted | `Skyy_Ench_<Key>` -> the base item's category, from `tools/skyyench.py` (Gathering-Progression-Spec F13) | when the Enchanted round ships |

Build assert: every item of every visible SkyyCollections collection has a category (so "you collected it" always means "it fits").

### 1.2 The Pocket Dimension = ONE bag, ONE page

- One item, `Skyy_Sack_Pocket` (the `Skyy_Sack_` prefix keeps it blocked from /trade, the Auction House and Merchants and out of
  SkyyGear). It looks like today's pouch with the violet swirl and sparkles. The mouth stays open while held, with the 0.7.16 hold pose.
- **The storage belongs to the profile, not to the item.** The item is only the opener (use it, or `/pd`, `/sacks`, `/bags`). Losing,
  dropping or storing the item can never lose items. `/pd` gives a new one when you have none.
- One page: a tab per category (section 3). The `/craft` tab and the Furnace / Tannery queues stay where they are.

## 2. Storage level, rarity, capacity, upgrades

### 2.1 Storage level (automatic)

- **Total** of a category = every item of that category's collections you have collected (SkyyCollections counts, per profile).
  Mining / Foraging / Farming / Combat / Fishing = that SkyyCollections category. **Smithing** has no collection category, so it
  adds up the hide and fabric-scrap collections (Light / Medium / Heavy Hide, Linen, Wool, Shadoweave, Cindercloth) and the metal ore
  collections (Copper to Mithril) (question 4).
- **Level = 1 + floor( sqrt( total / step ) )**, capped at the max level. `step` is per category, because Mining and Farming items
  come in far bigger numbers than fish or combat drops.
- **Never goes down:** the best level ever reached is saved per profile per category; shown level = max(saved, computed). A collection
  reset, a changed `step` or SkyyCollections missing for a while never lowers it.
- Without SkyyCollections: SkyySacks counts its own intake per category (items it ever stored) as the total.

Items collected to REACH a level (step: Mining 25, Foraging 20, Farming 25, Combat 8, Smithing 10, Fishing 2 - all PLACEHOLDER):

| Level | Mining | Foraging | Farming | Combat | Smithing | Fishing |
|---|---|---|---|---|---|---|
| 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5 | 400 | 320 | 400 | 128 | 160 | 32 |
| 10 | 2,025 | 1,620 | 2,025 | 648 | 810 | 162 |
| 14 | 4,225 | 3,380 | 4,225 | 1,352 | 1,690 | 338 |
| 25 | 14,400 | 11,520 | 14,400 | 4,608 | 5,760 | 1,152 |
| 50 | 60,025 | 48,020 | 60,025 | 19,208 | 24,010 | 4,802 |
| 100 | 245,025 | 196,020 | 245,025 | 78,408 | 98,010 | 19,602 |
| 200 | 990,025 | 792,020 | 990,025 | 316,808 | 396,010 | 79,202 |
| 250 (max) | 1,550,025 | 1,240,020 | 1,550,025 | 496,008 | 620,010 | 124,002 |

Each next level needs a few more items than the last (about 2 x step x level), and every level always adds space. Early levels come
within minutes, later ones keep coming with normal play. That is the "constantly goes up" Skyy asked for.

### 2.2 Capacity = item limit per category

**Capacity = level x 100 x rarity multiplier** (100 = PLACEHOLDER "items per level"). It is ONE total for all items of the category
(Skyy's example: Mining Lv 14 x Rare 2.0 = 2,800 items across all mining materials).

| Rarity (ladder) | Multiplier | Lv 1 | Lv 10 | Lv 14 | Lv 25 | Lv 50 | Lv 100 | Lv 250 |
|---|---|---|---|---|---|---|---|---|
| Normal (start) | x1.0 | 100 | 1,000 | 1,400 | 2,500 | 5,000 | 10,000 | 25,000 |
| Unique | x1.5 | 150 | 1,500 | 2,100 | 3,750 | 7,500 | 15,000 | 37,500 |
| Rare | x2.0 | 200 | 2,000 | 2,800 | 5,000 | 10,000 | 20,000 | 50,000 |
| Legendary | x3.0 | 300 | 3,000 | 4,200 | 7,500 | 15,000 | 30,000 | 75,000 |
| **Omni** (every category) | x5.0 | 500 | 5,000 | 7,000 | 12,500 | 25,000 | 50,000 | 125,000 |

- Names and colours are today's bag ladder (Normal #ffffff, Unique #ffff55, Rare #ff55ff, Legendary #55ffff, Omni = the Mythic
  #cc66cc). "Common" in talk = Normal.
- **At the limit:** pickup and Deposit all stop taking items of that category (the rest stays in your inventory). Taking items out
  always works. Lowering a setting never deletes anything: it only stops intake.

### 2.3 Rarity upgrades (the Upgrade button)

A step needs (a) the storage **level gate** of that category and (b) the **items** below, paid from the Pocket Dimension first, then
the inventory, in one all-or-nothing click. The level gate is what keeps coins from skipping it (R3): items can be bought, levels cannot.
The cost uses the category's ladder collections (the Gathering-Progression tiers), not every small collection (question 3).

| Step | Level gate | Mining | Foraging | Farming | Combat | Smithing | Fishing |
|---|---|---|---|---|---|---|---|
| Normal -> Unique | Lv 10 | 500 Cobblestone, 250 Copper Ore, 100 Iron Ore | 500 Oak Log, 500 Plant Fiber, 100 Tree Sap | 500 Wheat, 250 Lettuce, 100 Essence of Life | 250 Bone Fragments, 100 Feathers | 200 Light Hide, 100 Linen Scraps, 100 Wool Scraps | 100 Raw Fish |
| Unique -> Rare | Lv 25 | 2,000 Cobblestone, 1,000 Copper Ore, 1,000 Iron Ore, 250 Thorium Ore | 2,000 Oak, 1,000 Maple, 500 Gumboab, 250 Tree Sap | 2,000 Wheat, 1,000 Carrot, 500 Cauliflower, 250 Essence of Life | 1,000 Bone, 500 Feathers, 100 Venom Sac, 100 Sturdy Chitin | 750 Light Hide, 500 Medium Hide, 250 Linen, 100 Shadoweave Scraps | 500 Raw Fish, 20 Rare Raw Fish |
| Rare -> Legendary | Lv 50 | 5,000 Cobblestone, 2,500 Iron Ore, 1,000 Thorium, 500 Cobalt, 100 Adamantite | 5,000 Oak, 2,000 Maple, 1,000 Gumboab, 1,000 Redwood, 500 Sallow, 500 Tree Sap | 5,000 Wheat, 2,000 Carrot, 1,000 Pumpkin, 1,000 Tomato, 500 Cotton, 500 Essence of Life | 2,500 Bone, 1,000 Feathers, 250 Venom Sac, 250 Chitin, 100 Essence of the Void, 10 Voidheart | 2,000 Light Hide, 1,000 Medium Hide, 250 Heavy Hide, 250 Shadoweave, 100 Cindercloth | 1,500 Raw Fish, 100 Rare, 10 Epic Raw Fish |
| -> Omni | all six categories Legendary | automatic, no cost (question 2) | | | | | |

All costs and gates are PLACEHOLDER rows. Why this feels steady: each step's cost is roughly a fifth to a sixth of what you had to
collect to reach its gate, so by the time the button lights up you have usually already gathered most of it. Every step is also a
big jump in space (x1.5 -> x2 -> x3 -> x5) on top of the level growth.

### 2.4 Server Setup rows (SkyWynn Menu -> Server Setup -> "Bags and Crafting", all live)

| Key | Default | Range | Note |
|---|---|---|---|
| `pd.perLevel` | 100 | 1 - 100,000 | items per storage level |
| `pd.maxLevel` | 250 | 1 - 10,000 | |
| `pd.step.<Category>` (6 rows) | 25 / 20 / 25 / 8 / 10 / 2 | 1 - 1,000,000 | items for the level curve |
| `pd.mult.<Rarity>` (5 rows) | 1.0 / 1.5 / 2.0 / 3.0 / 5.0 | 0.1 - 100 | must not go down along the ladder (asks first, like today's tier order check) |
| `pd.gate.<Rarity>` (3 rows) | 10 / 25 / 50 | 1 - max level | |
| `pd.cost.<Category>.<Rarity>` (18 rows, advanced) | the table above | text `itemId:qty,...` | unknown ids are refused at save |
| `pd.omniAuto` | on | on / off | off = Omni needs an admin grant (no cost table) |
| existing `bags.cookedFood`, `bags.refill`, `bags.refillDefault`, `bags.pocketCraft`, `bags.benchChests`, Furnace / Tannery rows | unchanged | | |
| retired `bag.small / medium / rare / large / omni`, `bags.freeRecipes` | kept in the file, no longer read (no rewrite) | | |

## 3. UX

### 3.1 Pocket Dimension page (vanilla kit, at most 980 px high)

| Area | Shows |
|---|---|
| Left column | 6 category tabs (Mining, Foraging, Farming, Fishing, Combat, Smithing): icon + name in its rarity colour + "Lv 14" + a thin fill bar |
| Header of the open tab | "Mining - Lv 14 - Rare (x2.0)". Storage bar: "2,140 / 2,800 items". Level bar: "4,100 / 4,225 collected to Lv 15 (+200 space)" |
| Upgrade box | "Upgrade to Legendary (x3.0): space 2,800 -> 4,200". Gate line "Needs Mining Lv 50 (you: 14)". Cost rows: item icon + "have / need" (green when enough, red when not). UPGRADE button greyed until all are met; click -> confirm ("Pay these items?") -> done + sound. At Legendary: "Omni: get all six categories to Legendary (4 / 6)" |
| Grid | today's 36-cell grid with paging, click to take, Pick up all, Deposit all (per tab) |
| Footer | Stack refill setting (Hotbar only / Full inventory / Off), the `/craft` tab, Furnace / Tannery |
| Over the limit | an amber line: "Over the limit (25,300 / 15,000) - nothing new goes in until you take some out" |

### 3.2 Pickup routing

Every 2 s the sweep looks at the MAIN inventory only (R2), takes each item to its category (1.1) if the profile is settled
(`settledKey`, `profile:busy`) and the category is under its limit, takes only what fits (the rest stays), and respects kept counts (R3)
and the cooked-food switch. No bag needs to be carried.

### 3.3 Kept features (must behave exactly as today unless listed)

| Feature | v2 rule |
|---|---|
| Auto-pickup, kept counts, Deposit all | unchanged; "carry a bag of that type" becomes "always" |
| Stack refill (Hotbar only / Full / Off) | unchanged, plus 0.7.17's reserved empty hotbar slots for Requip (`requip:pocket:<uuid>`) |
| Crafting from bags: benches, inventory crafting, `/craft` | unchanged; the mirror offers every category (no longer only carried bag types) |
| `/craft` class filter (`gear:fn:classShow`, 0.7.17) | unchanged |
| Bazaar sell from bags, SkyyFishing / SkyyWardrobe takes | `sacks:fn:count / all / take / put / commit` unchanged in shape; "bag carried" gate gone |
| Requip deposit + craft bridges (0.7.17) | `sacks:fn:deposit` respects the category limit (answers what it accepted); `craftList / craftHave / craftPay / craftRefund / craftCommit` unchanged |
| Furnace / Tannery queues, Campfire tab | unchanged |

## 4. Migration (Convert + refund)

### 4.1 What really moves

Nothing in storage moves: since 0.7.2 the bag contents already live in the profile's pool file (`pools/<pkey>.properties`, item ->
count). Bags were only keys and limits. So migration only has to (a) turn bag ITEMS into a starting rarity and (b) remove those items safely.

### 4.2 Rules

| Case | Result |
|---|---|
| A profile's first v2 login | every category starts at Normal, level from its totals; the pool is untouched; a `/pd` item is given (a claim if the inventory is full) |
| A legacy bag in the inventory (hotbar, storage, backpack) | the category's rarity = max(current, that bag's rarity) - **best bag wins**: Normal / Unique / Rare / Legendary = the old Small / Medium / Rare / Large ids. The bag is removed |
| Farming bag | also sets the new Fishing category (fish lived in Farming) |
| Mythic Omni Bag | Omni rarity in every category |
| Extra bags (a second bag of a type, or one below the rarity you already have) | **refund** its full crafting chain into the Pocket Dimension: Normal = 20 Plant Fiber + 4 Sticks; Unique = that + 6 Linen Scraps; Rare = + 6 Shadoweave Scraps; Legendary = + 6 Cindercloth Scraps; an extra Omni = 5 Legendary chains. Refunds may go over the limit (never refused) |
| Legacy bags in chests, the Vault, on the ground, or in another profile's inventory | converted ON SIGHT the moment they enter an inventory of a settled profile (join, the 2 s sweep, after a profile switch). The 21 old item ids stay defined (no unknown items anywhere), without recipes, tooltip "Old Magic Bag - turns into Pocket Dimension rarity when you pick it up" |
| Over the new limit | allowed. Everything stays visible and takeable; intake of that category waits until the total is below the limit. Never deleted |

### 4.3 Safety (Ultracode level: saved data + items)

- Per profile file `Skyy_SkyySacks/pd/<pkey>.properties` (rarity per category, best level per category, `omni`, `v2.first=<time>`
  marker = run-once). Tmp + fsync + atomic rename, like the pool.
- **History snapshot first:** before a profile's first v2 change, copy its pool + processing files to
  `Skyy_SkyySacks/history/<pkey>-<time>/` and read the copy back (verified) - no snapshot, no migration (retry next login, WARN once).
- **Journal** `pd/<pkey>.journal` (append, fsync), per bag: `intent` -> rarity saved (idempotent: max) -> bag removed through the
  exact-slot transaction -> `removed` -> refund booked as **pending** -> after 30 s (three engine player-save ticks, the SkyyProfiles
  marker rule) the refund goes into the pool -> `done`. A crash rolls the inventory back, so the bag comes back and converts again;
  the pending refund of a crashed run is dropped, so a bag is never refunded twice and never lost. A rarity can only go up, so a
  repeat is harmless.
- Respects `profile:busy` and `settledKey` (never during a switch or crash recovery). World thread only.
- KnowSync forgets its own 21 managed bag recipe ids once (it never touches other entries).
- One INFO log line + one chat line per profile: "Your Magic Bags became Pocket Dimension rarity: Mining Rare, ... Nothing was lost."

### 4.4 Rollback floor

Once a server runs v2, bags have been removed, and SkyySacks 0.7.x needs a carried bag to reach a pool. **Never roll back below
SkyySacks 0.8.0** (add to the `tools/deploy_set.py` floors). Emergency only: `/pdadmin legacybags <player>` gives back the bags the
journal removed for the active profile (admin, logged); the pool was never touched.

## 5. Cross-mod

| Mod | Change | Keys |
|---|---|---|
| **SkyyCollections 0.2.9** | new `coll:fn:catTotal` `apply(Object[]{UUID, String category}) -> Long` (sum of that category's collections for the active profile; null = unknown). SkyySacks falls back to summing `coll:fn:count` over `coll:list` (`id:Category,...`) when it is missing. Bag reward rows: while `sacks:v2` is TRUE, `Skyy_Sack_*` reward tokens are not shown, not counted in Locked / Unlocked recipes and teach nothing (the file is NOT rewritten - no migration). `sacks:freebags` no longer read | new: `coll:fn:catTotal`. Unchanged: `coll:fn:count / tier / add / where`, `coll:list`, `coll:recipes:<uuid>` |
| **SkyySacks 0.8.0** | publishes v2 state | new: `sacks:v2` (Boolean TRUE), `sacks:fn:pd` `apply(UUID) -> Object[]` of `Object[]{String cat, Integer level, String rarity, Long cap, Long stored}` (Menu / HUD / later Storage hub), `sacks:fn:catOf` `apply(String itemId) -> String` (the 1.1 rule). Unchanged shape: `sacks:fn:count / all / take / put / commit`, 0.7.17's `sacks:fn:deposit / craftList / craftHave / craftPay / craftRefund / craftCommit`. Retired: `sacks:freebags` (no longer written) |
| **SkyyBazaar 0.1.8** | new **Fishing** section (Skyy's "matching section" rule); fish move out of Farming; Crystals get Mining products if any are missing (the build guard over `SackDefs.catOf` must pass); bag gate gone on its side automatically | reads `sacks:fn:*` as today |
| **SkyyMenu (next)** | Pocket Dimension tile text: "One bag for everything. Each category's space grows as you collect; upgrade its rarity for more. Command: /pd (or /sacks, /bags)" | `cmdc:sacks` unchanged |
| SkyyEssentials, SkyyAuctions, SkyyMerchants, SkyyGear | nothing: `Skyy_Sack_*` already covers the new item | - |
| SkyyFishing, SkyyWardrobe | nothing (bridge shapes unchanged); later optional `fish:fn:landed` so landed fish count toward the Fishing level | - |
| SkyyAccessories | optional later: rename the Workbench tab "Accessories & Bags" -> "Accessories" (no bag recipes left) | - |

## 6. Build plan

| Round | Mods | Kind | Content |
|---|---|---|---|
| **W. Wait** | - | - | SkyySacks 0.7.17 must be built, reviewed and **pinned in the SET** first: 0.8.0 is derived from it (`tools/sacks_0_8_0_patch.py`) and must keep its deposit / reserved-slot refill / craft bridges / class filter |
| 0 (can start now) | SkyyCollections 0.2.9 | lean | `coll:fn:catTotal` + hide `Skyy_Sack_*` rows while `sacks:v2`; harmless without SkyySacks 0.8 |
| **1** | SkyySacks 0.8.0 + SkyyBazaar 0.1.8 (+ Collections 0.2.9 if not yet live) | **Ultracode** (saved data, items, several mods) | categories + Fishing, levels, rarity, item limits, Upgrade, the new page, `Skyy_Sack_Pocket`, migration + journal, Server Setup rows, bridges; deploy together |
| 2 | SkyyMenu tile text (+ balance chart / docs) | lean | after round 1 is live |

**Harness musts (round 1):**

- **Conservation (no dupe, no loss):** items in inventory + pool before = after, for: sweep at / near / over the limit, partial fit,
  Deposit all, withdraw, Pick up all, refill (incl. reserved slots), `sacks:fn:take / put / commit / deposit`, `craftPay / Refund /
  Commit`, bench + pocket crafting, the Furnace / Tannery, and the Upgrade (all-or-nothing; a double click in one tick charges once;
  pool + inventory split payments).
- **Migration:** every bag id x rarity; several bags of one type (best wins + refunds); the Omni; bags in hotbar / storage / backpack;
  full inventory for the `/pd` item; a crash injected after each journal step plus the engine rollback = exactly one rarity and at
  most one refund, never zero bags and zero credit; profile switch and `profile:busy` mid-run; a bag carried into another profile;
  History snapshot verified before the first write; run-once.
- **Limits:** over-limit never deletes; lowering any row never deletes; level never drops (counts lowered, Collections missing,
  `step` raised); Omni appears exactly when all six are Legendary.
- **Bridges:** old shapes answer as before (Bazaar 0.1.7 and SkyyFishing 0.1.2 jars run unchanged against 0.8.0); `sacks:v2` read by
  Collections; Bazaar build guard green with Fishing.
- `-Xverify:all`, `python tools/ci/lint.py` 0 fails, `python tools/ci/crosscheck.py --jar <new jars> --baseline`, page layout checks
  (`tools/skyyui.py`), the rollback floor added to `tools/deploy_set.py`.

## 7. Questions for Skyy (recommended default first)

| # | Question | Recommended default |
|---|---|---|
| 1 | Do you have to carry the Pocket Dimension item for pickup to work, or is it only the opener (storage works anyway)? | **Opener only** - nothing can be lost by dropping it; everyone has it from the start, `/pd` gives a new one |
| 2 | Omni: automatic once all six categories are Legendary, or one last paid upgrade? | **Automatic** (the six Legendary upgrades already cost a lot; the old Omni also just took the Legendary bags) |
| 3 | Upgrade cost: items from the category's ladder collections (table 2.3), or literally from EVERY collection of the category (Mining has ~25, some hidden until Hytale 0.7)? | **Ladder collections** |
| 4 | Smithing level counts hides + fabric scraps + metal ores collected? | **Yes** (Smithing has no collection category of its own) |
| 5 | An Enchanted item (when they ship) uses 1 space or 100? | **1** - compressing is the reward, like SkyBlock |
| 6 | Numbers: 100 items per level, multipliers x1 / x1.5 / x2 / x3 / x5, gates Lv 10 / 25 / 50, the cost table | **Ship as placeholders** (all Server Setup rows); Fishing numbers re-checked once SkyyFishing feeds the Fishing total |
