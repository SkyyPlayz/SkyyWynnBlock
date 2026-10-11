# Requip + /smithing hub - build spec (Wardrobe v2 + one Smithing page)

*Local spec 2026-10-11. Spec only: nothing built. Owner: Skyy (they/them). The Requip half ADOPTS the cloud spec
`research/cloud/Requip-Spec.md` (read it for the full Requip design); this file lists the fixes to it, then specifies the /smithing hub,
the bridges between SkyyWardrobe, SkyyGear and SkyySacks, and one combined build plan.*

## 0. Decisions this spec follows

All from `docs/answered/gear.md` (2026-10-10), Skyy's words:

| Line | Skyy said (word for word, trimmed with ...) | Means |
|---|---|---|
| 141 | "build the wardrobe/ loadout system too. (in the loadouts i want to be able to setup Armor, (hot bar if its not too hard.) Pets, and active abilities and their modifiers. ..." | a loadout = armor + hotbar + pet + summon + abilities |
| 153 | "... in fairy tail Erza has a magic call requip. ... im picturing an infinite storage space like a chess, you can dump all your gear into. and everything in there is selectable for the loadouts. (might be easier if we added an armor one, and items one for weapons and tools /potions and food. then also let it pull from the pocket dimension for blocks in the hot bar. (so they auto refill.)" | REQUIP: Armor space + Items space per profile; loadouts pick from them; block slots refill from the Pocket Dimension |
| 154 | "so you compile gear, then select what each kit uses from the pool. so your good weapon, you can select in every loadout, and swap out the armor, and tool in your hot bar for the job" | ONE pool; the same item in many loadouts |
| 155 | "2. an update page where it keeps the rarity sounds pretty cool, should we do that with the soul cages too?" | Upgrade keeps rarity + lines |
| 156 | "... maybe also have things you can change the type ..." | Upgrade covers every tier ladder; CONVERT later |
| 157 | "we can probbly combind the upgrade into the reforge we already have." | Upgrade is a tab of the Reforge page (SkyyGear 0.2.22) |
| 158 | "one command, one location.   we could maybe even make a /smithing that have crafting, reforging and upgrading. (and make it pull from and craft to that loadout storage i was talking about, make it work kinda like the bags we have, but for armor and weapons.) in the crafting, we could show the armor sorted into sets you click to open. (maybe use a bigger size than a item slot, and show the whole set like its on a player. (like a fancy set card showing off the set, maybe including set stats and bonuses. then you click them and it pulls up a page will all the items in a page where you can craft them. (we should give this, and the crafting thing a filter by class. so it only shows things your class can use" | /smithing = Craft + Reforge + Upgrade (+ Multitool); craft from + into Requip; SET CARDS; class filter |
| 151 | multitool "Merge the rolls (Recommended)" | /multitool merge page (SkyyGear 0.2.21) |

**Engine fact** (SkyyGear 0.2.21 header, verified on the engine's own crafting code): a bench recipe only takes an input stack whose
metadata equals the recipe input's (none). Every crafted / rolled gear item carries a SkyyGear document, so rolled gear is NEVER a
bench ingredient. That is why reforge, upgrade and merge live on our own pages, and why this hub does its own crafting.

Also followed: `tools/PROFILES-CONTRACT.md` (per-profile files under the profile key, `profile:busy`), `PROJECT-RULES.md` section 4
(one-time migrations, Ultracode for saved data / items / several mods), `research/Vanilla-UI-Style-Guide.md` + `tools/skyyui.py`
(pages at most 980 px high for 1080p, never a metadata ItemStack in an ItemGridSlot, rebuild only after a click).

## 1. Requip storage (adopted from the cloud spec, with fixes)

**In short** (details: `research/cloud/Requip-Spec.md` sections 3, 4, 8, 9):

| Topic | Rule |
|---|---|
| Spaces | per profile: **Armor** (anything that fits an armor spot) + **Items** (weapons, tools, multitools, potions, food) |
| Refused | blocks + materials (they belong in the Magic Bags), unidentified gear + mystery bags, bags / anything holding items, accessories, the menu item + vault arrows (`swap.keepIds`), unknown ids, `items.deny` |
| Units | gear = one entry each with a stable id (eid); potions / food = one entry per kind with a count |
| Size | "infinite" = paging: 45 per page (9 x 5), cap 1000 per space per profile (editable 50 - 10000), files of 100 entries |
| Sort / search | newest / rarity / level; a search box (id or name); the right panel filters to what fits the picked slot |
| Deposit | click an item in the "Your inventory" panel (our own non-draggable grid); shift-click the same if the click event carries shift (probe P3); **Deposit all gear** button (storage + backpack; hotbar only with `deposit.hotbar`) |
| Withdraw | **Take out** (to inventory, only where it fits whole; removes the stamp; picks of it show "removed") |
| Files | `Skyy_SkyyWardrobe/requip/<pkey>/` = `index.json` + `armor-000.json`... + `items-000.json`... + `loadouts.json` + `journal.json` + `orphans.json`; the SkyyWardrobe 0.1 lossless slot format (explicit fields + engine codec), atomic write + read back |
| Dupe-proofing | an entry is IN (stack in the file) or OUT (only a display copy, never turned back into an item); a write-ahead journal before any move; crash repair from the LIVE inventory; nothing is ever deleted (orphans) |

**Fixes to the cloud spec** (found while reading the code; the builder applies them):

| # | Fix | Why |
|---|---|---|
| F1 | SkyyGear **Upgrade** and **Multitool merge** build a brand-new ItemStack (`SkyyGear/build_skyygear_0.2.22.py`: GearUp `put(new ItemStack(to, 1), ...)`, GearMerge the same), so the `SkyyRequip` stamp is LOST there today. SkyyGear 0.2.23 must copy every metadata key that is not its own (`SkyyGear`, `SkyyGearView`, the item display) from the source onto the new stack: Upgrade = from the item; Merge = from the pickaxe, and the hatchet's eid is reported to Requip as used up (`wardrobe:fn:gone`). | the same entry must survive an upgrade / merge (task rule) |
| F2 | Reforge, level-up and identify write onto the SAME stack (`GearData.put(it, ...)`, which keeps other keys) - the stamp survives them. Probe P1 only has to check the engine-side cases (death drop, Vault, section moves). | narrows P1 |
| F3 | Drop the cloud spec 5.3 row "Reforged into a different item id (look change at The Armory table while worn)": a worn stamped / rolled piece can never be a bench input (engine fact), so The Armory table cannot change it. Look changes come from Requip Looks later (Wardrobe-Spec section 4). | engine fact |
| F4 | A stamped item that leaves Requip by Equip is never a bench ingredient while stamped. Fine for gear (rolled anyway). Kind entries (potions / food) are never stamped, so they still work in recipes. Take out strips the stamp, so a plain item that leaves Requip for good is a recipe input again. | engine fact |
| F5 | Migration: if a 0.1 journal (`loadouts/<pkey>.journal.json`) is still present, run the 0.1 repair FIRST (same code), then migrate. If the repair fails, that profile's Requip stays shut until `/requipadmin repair` - nothing is migrated half. | a crash just before the update must not be migrated as "stored" |
| F6 | Crafted gear goes INTO the pool through the normal Deposit transaction (section 4.6), never written straight to the file, so the crash rules stay one set. | one dupe model |

## 2. Loadouts = references into the pool

Adopted from `research/cloud/Requip-Spec.md` sections 5-7. The choices the task asked for:

| Question | Decision | Why |
|---|---|---|
| What is a reference? | the entry id (eid) of a pooled item, plus for items that left the pool a tiny metadata stamp `SkyyRequip = { e: "<eid>" }` | a slot index breaks the moment an item moves, is dropped or relocated; the stamp follows the item anywhere in the inventory |
| Why its own key and not a field inside the SkyyGear document? | Requip must also hold items with no SkyyGear document (pack armor before it is stamped, potions, food); the two mods stay independent (either can roll back alone) | SkyyGear keeps its document; it only promises to carry foreign keys (F1) |
| Same item in many loadouts | yes - ten picks, one item; it is IN the pool or OUT on you, never both; Equip moves an item already on you from slot A to slot B (no pool trip) | gear.md 154 |
| Reforge / upgrade / merge | same eid: reforge / level-up / identify keep the stamp (F2); upgrade / merge copy it (F1); a merged-away hatchet = "used up (merged)" | task rule |
| Item gone (dropped, traded, sold, in a chest) | the pick shows **NOT WITH YOU**, Equip skips that slot with a chat note; **Forget** clears it | cloud spec 5.3 |
| Equip | worn armor + hotbar of the picked slots go back into the spaces, the picks come out; ONE write-ahead transaction (journal first, every move read back, rollback in the same task, crash repair at the next join) | cloud spec 7 |
| Unpicked slot | **Keep** (what you wear stays); each slot also offers **Empty** | LOCKED partial-set rule (gear.md 122) |
| Pets + abilities | exactly as 0.1: `pets:fn:loadoutGet/Set`, `class:fn:loadoutGet/Set`, applied after the items | proven 0.1 bridge |

**Hotbar block slots (auto-refill)** - only from the Pocket Dimension, never from anywhere else:

| Rule | Value |
|---|---|
| Which slots | hotbar only, and only a slot the loadout picked as **Pocket block** (item id + target); never armor, never a slot holding gear |
| What | only items that have a Magic Bag home type (blocks + materials); never a stack with metadata |
| When | on Equip (taken from the bags at once), then every 2 s by SkyySacks' existing refill tick while that loadout is worn |
| How much | up to the target (default = the item's max stack, Server Setup `pocket.target`) |
| From where | ONLY the Magic Bags you carry (`sacks:fn:take`); never the Vault, never chests, never the rest of your inventory, never Requip |
| Leaving the loadout | the blocks go back into the bags (`sacks:fn:deposit`); what does not fit stays in the inventory (never dropped) |
| Needs | SkyySacks 0.7.17: refill an EMPTY reserved slot (today it only tops up stacks you used) - Requip publishes `requip:pocket:<uuid>` |

## 3. Migration from SkyyWardrobe 0.1

Adopted from `research/cloud/Requip-Spec.md` section 10 + fix F5:

1. Lazily, the first time 0.2 loads a profile key, on the player's world thread, journaled like a Deposit all.
2. A pending 0.1 journal is repaired first (F5).
3. Every stored stack of every 0.1 loadout -> a new pool entry; a 0.1 hotbar stack Requip refuses (a block, a bag) -> "Returned items"
   on the page (take out; never lost).
4. Each 0.1 loadout -> a Requip loadout, same number / name / pets / abilities, picks pointing at the new entries; empty spots = Keep.
5. The 0.1 EQUIPPED loadout (its gear is on you): never moved automatically - the page asks once "Put what you wear into Requip and pick
   it for <name>?" [Yes].
6. The 0.1 file is read-only and never changed or deleted. Run-once marker `migratedFrom01` in `index.json`; one MIGRATE log line.
7. Settings: 0.1 rows keep their values; `swap.hotbar` / `swap.strict` show as "(0.1, unused)"; new rows appended - no value rewritten,
   so the PROJECT-RULES 4 migration rule has nothing to change.

**Rollback floor** (`tools/deploy_set.py` note when pinned): once 0.2 has run, never roll SkyyWardrobe below 0.2 (0.1 cannot read
`requip/`; gear would be invisible, not lost - reinstall 0.2 to see it).

## 4. The /smithing hub (owned by SkyyGear)

### 4.1 One command, one page, four tabs

| Command | Opens |
|---|---|
| `/smithing` (alias `/smith`) | the hub on **Craft** |
| `/reforge` | the hub on **Reforge** (held item on the anvil, as today) |
| `/upgrade` | the hub on **Upgrade** (as 0.2.22) |
| `/multitool` | the hub on **Multitool** (the 0.2.21 two-pick page) |

- Player commands, `hytale:Adventurer` on the root and every variant. SkyyMenu: a **Smithing** tile (`gear:fn:smithing`).
- The page is the existing Reforge frame (1100 x 880, kit look). Title "Smithing"; the 0.2.22 tab row becomes
  **Craft | Reforge | Upgrade | Multitool** (Primary = active tab, Secondary the rest, 5 px apart; Upgrade / Multitool hidden while
  their switches are off, as today).
- Reforge, Upgrade and Multitool keep their 0.2.21 / 0.2.22 rules. Two changes:
  - **Materials from the bags too:** Upgrade (and any later material cost) takes from your inventory first, then your Magic Bags
    (`sacks:fn:take`, refund with `sacks:fn:put` on any failure, `sacks:fn:commit` after success) - the same order as `/craft` and benches.
  - **Requip items in the lists:** the left lists also show your IN Requip gear (tag "Requip"). Picking one **fetches** it into your
    inventory (`wardrobe:fn:fetch`: it becomes OUT, stamp kept, every loadout pick still points at it). A **Return to Requip** button
    (and Deposit all gear) puts it back. Needs a free inventory slot; else "Inventory full".

### 4.2 Craft tab - layout

```
+--------------------------------------------------------------------------------------------+
| SMITHING      [Craft] [Reforge] [Upgrade] [Multitool]                              [Close] |
+-----------------+--------------------------------------------------------------------------+
| Combat armor  > | +--------------+  +--------------+  +--------------+                      |
| Gathering armor | | Iron Plate   |  | Raven Leather|  | Silk Cloth   |   3 cards per row    |
| Weapons         | | Lv 20-27     |  | Lv 20-27     |  | Lv 20-27     |   2 rows per page    |
| Tools           | |    [Head]    |  |    [Head]    |  |    [Head]    |                      |
| Multitools      | | [Hands][Chest]|  | ...          |  | ...          |                      |
|                 | |    [Legs]    |  |              |  |              |                      |
| Class: Warrior  | | Health +48   |  |              |  |              |                      |
| [x] My class    | | Full set: -  |  |              |  |              |                      |
| [ ] Show all    | | 2/4 craftable|  |              |  |              |                      |
| Search [      ] | +--------------+  +--------------+  +--------------+                      |
|                 |                                   [< Page 1 / 3 >]                       |
+-----------------+--------------------------------------------------------------------------+
| Crafted gear goes to: Requip (Armor space 212 / 1000)       Materials: inventory, then bags |
+--------------------------------------------------------------------------------------------+
```

- Widths: left column 220 + gap 16 + card area 830 = 1066 (the frame's inner width 1100 - 34). Cards 266 x 300, 3 per row, gaps 16.
  Height: tab row 44 + 2 card rows (2 x 300 + 16) + pager + footer fits the 880 frame (the kit's `assert_page_size` proves it).
- **Set card** (bigger than a slot, like Skyy asked): name (bold, rarity-neutral), "Lv A-B - Heavy / Light / Cloth" (or "Mining /
  Foraging / Farming"), then the **figure**: 64 px icon cells arranged like a player - Head top centre; Hands left of Chest on the
  middle row; Legs bottom centre (no player model element is known in custom pages - Wardrobe-Spec probe E3; if a probe ever finds one,
  only the figure box changes). Icons are `new ItemStack(id, 1)` (metadata-free). Below: the set's base stats added up (Health,
  Resistance, mining lines), the full-set bonus text from SkyyGear's set table (`set.<id>` rows; mining sets' Fortune bonus), and a
  state word: "4/4 craftable", "2/4 craftable", "Locked - needs Armor Bench II accessory", "Mining 12 needed".
- **Weapons / Tools / Multitools**: one card per FAMILY (Swords, Maces, Bows, Staffs, Pickaxes ...) showing its tier ladder as small
  icons (up to 8 in two rows) + "Lv 1-49"; same click-through.
- Hover = SkyyGear's own tooltip lines (no page update from hover). Rebuild only after a click.

### 4.3 Piece page (click a card)

```
| < Back    IRON PLATE SET  (Heavy, Lv 20-27)                                                |
| [big figure 96 px icons]  | [Head]  Iron Helmet [Lv 20-27]   Iron Bar 6/6  Linen 2/4  [Craft] |
|  Set stats + full-set     | [Chest] Iron Chestplate          Iron Bar 10/8 ...        [Craft] |
|  bonus text               | [Hands] Iron Gauntlets           ...                      [Craft] |
|  Rolls a rarity: Normal   | [Legs]  Iron Greaves             ...                      [Craft] |
|  60% ... (your step-up)   |                                    [Craft every missing piece]  |
```

- One row per piece (or per tier for a weapon / tool family): icon, name + level band, every material with have / need (white =
  enough, gold = short; have = inventory + bags), the Craft button (greyed with the reason when not allowed).
- **Craft every missing piece**: crafts each piece of the set you can afford that is not already in your Requip / inventory, in one
  click (one transaction per piece; stops at the first refusal).
- Output: SkyyGear's normal craft roll (same odds + Smithing step-up as a bench craft), "crafted at your level", Smithing XP paid once
  per item exactly like a bench craft (the `/craft` path). After a craft: "Made: <name> (Rare) -> Requip".

### 4.4 Which recipes, and how the page stays consistent with benches

| Rule | Decision |
|---|---|
| Recipe source | the LIVE CraftingRecipe store (never a copy): every recipe whose primary output is a SkyyGear item (weapon, armor, tool, multitool) - vanilla, ours (SkyyGear / SkyyArmory recipe files) and pack mods - except table-only / timed Processing recipes and look (alteration) recipes. Re-read when the store size changes (the 0.2.22 ladder cache rule) |
| Bench requirement | **the same rule as SkyySacks `/craft`**: a recipe needing bench B at tier t is craftable here when you have B's bench accessory at tier >= t equipped in your Accessory Bag (Weapon Bench / Armor Bench / Workbench accessories T1-T3, or the Omni). Otherwise the row says "Needs Weapon Bench II accessory - or craft it at a Weapon Bench (tier 2)" |
| Knowledge | `KnowledgeRequired` recipes only when known / unlocked by collections (the `/craft` rule) |
| Level gate | SkyyGear's `craft.belowBand` and gate skill (multitools: Mining AND Foraging), exactly as at the bench |
| Time | instant, like `/craft` (crafting-bench recipes; timed Processing recipes are never offered) |
| Vanilla benches | unchanged; they keep crafting from inventory + bags and deliver into the inventory |

**Why this rule:** one portable-crafting rule for the whole pack. `/craft` already lets you craft bench recipes anywhere with the bench
accessory of that tier (Skyy's crafting layout lock in HANDOFF; `SkyySacks/build_skyysacks_0.7.16.py` `benchRecipes`). The hub is a
nicer face of the same thing for gear, so it must not become a free bench (that would make the Weapon / Armor Bench accessories
pointless) and must not be stricter than `/craft` (players would just use `/craft`). "Stand next to the bench" is not used: a custom
page cannot see benches reliably and it would be a second rule. To keep the rule in ONE place, SkyySacks answers it (`sacks:fn:craftList`,
section 5).

### 4.5 Class filter

| Item | Shown with "My class" on |
|---|---|
| Weapons | ids matching `class:weapons:<your class>` or `class:weapons:free` (SkyyClasses' live weapon prefixes) |
| Combat armor | sets of your class's armor TYPE: Warrior / Berserker = Heavy, Archer / Assassin / Monk = Light, Mage / Priest = Cloth (LOCKED armor types 2026-10-05; Server Setup row `smith.classArmor`, a class missing there = all types). Type = SkyyGear's armor type of the piece |
| Gathering armor, tools, multitools | always (every class gathers) |
| No class chosen / Show all | everything |

- "My class" is ON by default; **Show all** is a per-player switch remembered in SkyyGear's player switches.
- The vanilla bench screens cannot be filtered (client screens). SkyySacks `/craft` Smithing tab gets the same filter through
  `gear:fn:classShow` (section 5) in its 0.7.17 round - Skyy asked for "this, and the crafting thing".

### 4.6 Crafting into Requip - the transaction (world thread, one click)

1. Gates: profile settled (`profile:busy`, profile changed since the page), page token, recipe still allowed (`sacks:fn:craftList`),
   level gate. Room check: Requip accepts it (`wardrobe:fn:canDeposit`) OR a free inventory slot; neither = "No room", nothing moves.
2. Roll the item's document in memory (the bench craft roll).
3. `CRAFT-BEGIN` in `gear.log` (recipe, the rolled document, the material plan) flushed to disk.
4. Materials: `sacks:fn:craftPay` (inventory first, then bags - the `/craft` order; resource-type inputs handled by SkyySacks; never a
   stack with metadata). Paid less than asked = refund (`sacks:fn:craftRefund`) and refuse.
5. Deliver: the item is put into a free inventory slot (checked), then deposited into Requip by the NORMAL deposit
   (`wardrobe:fn:depositSlot`: Requip's own journal, read back, crash repair from the live inventory - fix F6). No free slot: deposited
   straight in with `wardrobe:fn:deposit`, whose journal step carries the material counts before the craft (inventory kinds + bag
   counts) as evidence; a crash repair that finds those materials back (the engine rolled the inventory back) removes the crafted entry
   (`CRAFT-UNDONE`), never keeps both.
6. Requip absent / off / full: the item stays in the inventory slot from step 5 ("Requip full - in your inventory").
7. Delivery failed completely = `sacks:fn:craftRefund` + `CRAFT-FAILED`; success = `sacks:fn:craftCommit`, Smithing XP paid,
   `CRAFT-DONE`. A crash between 4 and 5 can only lose the materials (listed in CRAFT-BEGIN for an admin), never copy an item.
8. Per-player busy flag + 1 s gap (as Reforge); a second click with the old token is refused.

Per-player switch "Crafted gear goes to: **Requip** / Inventory" (default Requip when SkyyWardrobe 0.2 is loaded).

## 5. Cross-mod bridges

All on `skyy.bridge`; arguments and answers are java.lang types plus the engine's own `ItemStack` / `BsonDocument` where an item must
pass (precedent: `gear:fn:roll`, `gear:fn:tradeable`) - never a class of our own mods. All functions run on the caller's world thread
only (else they answer null). Missing key = that feature greyed with a note.

**SkyyWardrobe 0.2 publishes**

| Key | Shape | Does |
|---|---|---|
| `wardrobe:fn:open` (+ `requip:fn:open`) | `apply(UUID) -> Boolean` | opens the Requip page (0.1 key kept) |
| `wardrobe:fn:canDeposit` | `apply(Object[]{UUID, String itemId, Integer count}) -> String` | null = it would be accepted; else the reason ("Armor space full (1000)", "not storable", "Requip shut") |
| `wardrobe:fn:depositSlot` | `apply(Object[]{UUID, String section, Integer slot}) -> String` | moves that inventory slot into the pool through the normal Deposit transaction; "eid:<hex>" / "kind:<hex>" or "refused:<reason>" |
| `wardrobe:fn:deposit` | `apply(Object[]{UUID, ItemStack, String source, String evidenceJson}) -> String` | a stack that is NOT in any inventory (a craft output) into the pool; journal step with the caller's evidence; same answers |
| `wardrobe:fn:list` | `apply(Object[]{UUID, String space}) -> Object[]` of `Object[]{String eid, String itemId, BsonDocument metadataCopy}` | IN entries for the hub lists (copies to read, never to give) |
| `wardrobe:fn:fetch` | `apply(Object[]{UUID, String eid}) -> String` | IN entry -> inventory, stamp kept, entry OUT; "ok" or the reason |
| `wardrobe:fn:gone` | `apply(Object[]{UUID, String eid, String why}) -> Boolean` | marks an OUT entry used up ("merged"); its picks show it |
| `requip:pocket:<uuid>` | `Map<Integer, String>` | reserved hotbar block slots of the worn loadout (SkyySacks refill) |
| `requip:stampKey` | `String` "SkyyRequip" | the stamp's metadata key (SkyyGear copies all foreign keys anyway) |

**SkyyGear 0.2.23 publishes** (new): `gear:fn:smithing` `apply(Object[]{UUID, String tab}) -> Boolean` (open the hub on a tab);
`gear:fn:classShow` `apply(Object[]{UUID, String itemId}) -> Boolean` (the class filter of 4.5, for `/craft`). It reads
`wardrobe:fn:*`, `sacks:fn:*`, `class:fn:get`, `class:weapons:*`, `acc:has:<uuid>` (through SkyySacks), `profile:*`.

**SkyySacks 0.7.17 publishes** (new; the cloud spec's two + the craft set)

| Key | Shape | Does |
|---|---|---|
| `sacks:fn:deposit` | `apply(Object[]{UUID, String itemId, Long qty}) -> Long accepted` | blocks back into the bags (bag caps respected) |
| (refill) | reads `requip:pocket:<uuid>` | the 2 s refill also fills reserved EMPTY slots up to the target |
| `sacks:fn:craftList` | `apply(Object[]{UUID, String group}) -> String[]` recipe ids | the `/craft` allow rule (bench accessory tier, knowledge, not table-only); group "smith" = gear outputs |
| `sacks:fn:craftHave` | `apply(Object[]{UUID, String recipeId}) -> Object[]{Long times, String[] inputs, Long[] have, Long[] need}` | have / need for the page (inventory + bags) |
| `sacks:fn:craftPay` | `apply(Object[]{UUID, String recipeId, Integer times}) -> Object[]{Long paid, String receipt}` | takes the inputs: inventory first, then bags; live-mirror rule; logged in `crafts.log` |
| `sacks:fn:craftRefund` | `apply(Object[]{UUID, String receipt}) -> Long` | puts a receipt's materials back, once, within 60 s |
| `sacks:fn:craftCommit` | `apply(Object[]{UUID, String receipt}) -> Boolean` | the craft happened: the receipt can never be refunded |

Existing and unchanged: `sacks:fn:count / all / take / put / commit` (Upgrade materials), `gear:fn:roll` (`/craft` gear rolls),
`pets:fn:loadoutGet/Set`, `class:fn:loadoutGet/Set`.

## 6. Build plan

| Round | Mod(s) | What | Size | Runs with |
|---|---|---|---|---|
| R0 | probe jar (local) | Requip probes P1 (engine side only, F2), P2, P3 (shift on SlotClicking), P7, P8 (~100 ItemGridSlots), P9; hub probe H1: 64 px item icons on a 266 x 300 card | lean probe + one Skyy test | first |
| R1 | **SkyyWardrobe 0.2 Requip** | spaces, entries, stamp, deposit / Deposit all gear / take out / forget / fetch, picker page, Equip transaction, crash repair, migration (+ F5), Server Setup, `/requip` (+ `/wardrobe /wd /loadout`), `/requipadmin`, every `wardrobe:fn:*` key of section 5 | **Ultracode** | parallel with R2 + R3 |
| R2 | **SkyySacks 0.7.17** | `sacks:fn:deposit`, reserved-slot refill, `sacks:fn:craftList / craftHave / craftPay / craftRefund / craftCommit`, class filter on the `/craft` Smithing tab via `gear:fn:classShow` | Full round (items, two mods' contract) | parallel with R1 + R3 |
| R3 | **SkyyGear 0.2.23 smithing hub** (on top of 0.2.22 once it is pinned) | `/smithing` + Craft tab (cards, piece page, class filter, craft transaction 4.6), tab row, Upgrade materials from bags, Requip items in the lists (fetch / return), foreign-key copy on Upgrade + Merge (F1), `gear:fn:smithing`, `gear:fn:classShow` | **Ultracode** (items, crafting, cross-mod) | parallel with R1 + R2, against the section 5 contracts |
| R4 | integration + **SkyyMenu** | the three jars in one JVM + offline smoke test; SkyyMenu: Wardrobe tile renamed "Requip", new Smithing tile; then pin R1-R4 together and deploy | Full (cross-check) / SkyyMenu lean | after R1-R3 |
| R5 | SkyyWardrobe 0.2.1 | Looks on pooled armor (`research/cloud/Wardrobe-Spec.md` section 4; needs `gear:base`) | Full round | later |

- R1, R2, R3 build in parallel because section 5 fixes the contracts; each harness uses fake bridges, R4 runs the real ones together.
  Order of deploy if one is late: R1 alone works (no crafting into it, no block refill); R3 alone works (crafts into the inventory);
  R2 alone changes nothing visible but the `/craft` filter.
- Each builder gets Skyy's quotes from section 0 (workflow `skywynn-round`, args `quotes`).

**Harness musts**

| Round | Must prove |
|---|---|
| R1 | format round trip (lossless, codec + explicit fields); a crash at EVERY Equip step (the 0.1 crash hooks) ends with every item exactly once; random-operation fuzz (deposit / equip / take out / fetch / forget / craft deposit / profile switch) with the invariant "each eid exists once across live + pool"; migration fixtures from scratch copies of real 0.1 files incl. a pending 0.1 journal (F5) and the equipped loadout; caps + file-split boundaries; unreadable / newer file keeps Requip shut; stamp survives SkyyGear reforge / level-up / identify / upgrade / merge (SkyyGear 0.2.23 jar in the same JVM) |
| R2 | refund only what a receipt took, once, within 60 s, never after commit; resource-type inputs; inventory-first then bags; never a metadata stack; refill never touches a slot not in `requip:pocket`, never a metadata stack, respects bag counts; deposit respects caps |
| R3 | page size assert (1100 x 880, <= 980 high); no metadata ItemStack in any ItemGridSlot of the built markup; craft transaction: room checked before materials, paid == crafted, refund on every failure path, XP paid once, nothing given on refusal; class filter matches SkyyClasses' live prefixes; recipe list equals the live recipes of Assets.zip + SkyyArmory / SkyyGear recipe files (no table-only ones); foreign keys copied on Upgrade + Merge |
| All | `python tools/ci/crosscheck.py --jar <new jars> --baseline`, `python tools/ci/lint.py` 0 fails, `python tools/smoke_test.py` PASS |

Rollback notes for `tools/deploy_set.py`: SkyyWardrobe floor 0.2 (section 3); SkyyGear 0.2.23 -> 0.2.22 safe (the hub goes; items are
ordinary gear; stamps are ignored keys); SkyySacks 0.7.17 -> 0.7.16 safe (Requip block slots stop refilling empty slots; hub crafting
greys out).

## 7. Questions for Skyy (each with a recommended default)

The cloud spec's 10 Requip questions (`research/cloud/Requip-Spec.md`, "Questions for Skyy") still stand with their defaults; ask them in
the same popup. New ones:

| # | Question | Default |
|---|---|---|
| 1 | Can the Smithing page craft without the bench accessory? | [No - same rule as `/craft`: the Weapon / Armor Bench accessory of that tier (or the Omni); benches work as always] |
| 2 | Where does gear crafted on the page go? | [Into Requip (armor -> Armor space, weapons / tools -> Items space); inventory if Requip is full or off; a per-player switch] |
| 3 | Materials: inventory first, then bags? | [Yes - the same order as `/craft` and benches] |
| 4 | Should Requip auto-collect gear you pick up, like the bags do with materials? | [No - Deposit all gear button + crafted gear goes straight in] |
| 5 | Class filter on by default? | [On when you have a class; "Show all" remembered per player; gathering armor + tools always shown] |
| 6 | A "Craft every missing piece" button on a set? | [Yes - each piece rolls its own rarity] |
| 7 | Reforge / Upgrade can take items straight from Requip (fetched into your inventory, loadouts keep pointing at them)? | [Yes] |
| 8 | Menu tiles: rename Wardrobe to "Requip" and add a "Smithing" tile? | [Yes, both] |
