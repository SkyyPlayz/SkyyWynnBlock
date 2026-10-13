# Upgrade ladders + Dragon sets - every tier ladder on the Upgrade tab, costs, what carries, CONVERT, the Mythic Dragon set

Cloud draft, 2026-10-13. Paper design; nothing built. Every number is a placeholder and a Server Setup row (times in seconds).
Arithmetic: python3 (method under each table). Builds on the LIVE Upgrade tab (SkyyGear 0.2.22 / 0.2.23, read only) and on
`research/cloud/Mining-Armor-Spec.md`, `research/cloud/Gathering-Armor-Stats.md`, `research/cloud/Special-Tools-Spec.md`,
`research/cloud/UT-First-Batch-Build.md`, `research/cloud/Untiered-Mythic-Spec.md`, `research/cloud/Enchanted-Materials-Draft.md`
(+ `research/cloud/Chain-Premium-Fix.md`: Enchanted +10 %, Block +4.5 %). Coordinates with the queued GATHERING spec (RESUME wave 3 item 7:
lifelong tools, rarity upgrades, Upgrade Points) and SkyyGear 0.2.24 (one Anvil tab) - this file owns only the LADDERS and their COSTS.

## 0. Decisions this follows (`docs/answered/gear.md`, read whole; newest wins; nothing re-decided)

The /upgrade lines (2026-10-10), word for word where it matters:

| Line | Skyy's words | Used in |
|---|---|---|
| 155 | "2. an update page where it keeps the rarity sounds pretty cool, should we do that with the soul cages too?" -> put in your item + the next tier's materials (bars + essence), get the next tier with the SAME rarity and lines (re-levelled); built generic | 1, 2.6, 3 |
| 156 | picked ALL (gathering armor sets, tools, weapons, class weapons) + "some mythic sets too. (like, you make get a dragon armor set from the first dragon boss. then in the next zone, have a dragon mini boss for each element that drop upgrades for the dragon armor to Fire dragon armor, and so on.) (maybe also have things you can change the type. like for the dragon gear, we probably want cloth heavy and light variants. (So we can pick good armor sets from armory mod for the dragon sets, then make recolored variants fir the elements.)" -> every ladder + Mythic boss-drop upgrades + a CONVERT step; normal crafting of every tier stays | 2, 5, 6 |
| 157 | "we can probbly combind the upgrade into the reforge we already have." | 7 |
| 158 | "one command, one location. we could maybe even make a /smithing that have crafting, reforging and upgrading." | 7 |
| 160 | "wouldnt multitool work fine just folded into /upgrade?" -> a pickaxe / hatchet shows a second path "-> Multitool" | 2.2, 7 |
| 161 | "reforging and upgrading can probably be 1 tab" -> one Anvil tab (SkyyGear 0.2.24) | 7 |

Newer lines that change the ladders (these WIN over the task's "recipe minus the old item's share" default):

| Line | Skyy's words (short) | Effect here |
|---|---|---|
| 164 (2026-10-11) | tool level = your skill, capped by tier; "upgrade to Iron -> Lv 22, same rarity + points kept" | 3 (what carries) |
| 165 (2026-10-11) | "but we will make upgrading more difficult than crafting. (like it costs a enchanted iron ingot to upgrade copper to iron, and so on. )" | 2 (cost rule: never cheaper than a fresh craft) |
| 168-170 (2026-10-12) | LIFELONG TOOLS: spawn with a Common pickaxe + axe; "you can only upgrade your tool through the upgrader, you cant make a new one"; all gathering tools (hoe, sickle, rod too); multitool after rebirth 1 | 2.2 |
| 172 (2026-10-12) | "the shovel is weird, we can leave it out as a craft item" | shovel = no ladder |
| 175 (2026-10-12) | gathering armor "Yes, like the tools": level = skill, "tier up on the Upgrade tab with Enchanted materials, keep rarity + rolls" | 2.3, 2.4, question 1 |
| 176 (2026-10-12) | rarity-upgrade items = SIGILS (separate from tier upgrades) | 3 |
| 129 (2026-10-08) | Onyxium crossbow = "Upgrade of Mithril crossbow" | 2.5 |
| 137, 128 | Mythic = bosses only, level-up cap Mythic +2 / UT +3 / rest +6; UT never crafted | 2.7, 5 |
| 116, 125, 136 | Mining = vanilla metal sets (green Set label); Armory OFF until 0.7 | 2.3, 5 |
| 41 | durability OFF by default | 3 |

## 1. What the live code does (read only, `SkyyGear/build_skyygear_0.2.23.py`, the SET pin)

| Fact | Where |
|---|---|
| Ladder table = config row `upgrade.ladders`, rows "A>B>C" joined by ","; default = the Soul Cage row | `:4457-4458` (`UP_SOUL`), rows `:4736-4738` |
| Parser: one next tier per item ("an item in two ladders" refused), loops refused, a written cost `B(Id*N+Id2*M)` on the item it goes INTO | `:22494-22553` (`parse`), `:22465` (`parseCost`) |
| CONVERT kind reserved: a row with `~` is refused "converting an item's type is not built yet" | `:22503` |
| Cost = a written row cost, else the LIVE recipe whose output is the next item and whose inputs hold the old item x1 (its OTHER inputs = the cost) | `:22636-22693` (`fromRecipe`, `cost`) |
| Refused: Mythic / Set / Untiered (rarity > 4 or a `set` field), unidentified, stacks, no recipe, materials short, below band | `:22712-22739` (`check`) |
| New document = a CLONE of the old one: same rarity, lines, reforge name / count, speed tier; level = the next tier's craft level; each line x levelFactor(new) / levelFactor(old), never lower, capped at a fresh roll unless already above; bought level-ups (`lvU`, `lvl0`) and the bag origin (`box`) dropped; `kind` / `gate` = the next tier's | `:22751-22798` (`relevel`, `docI`) |
| Plain item (no document) = a normal craft roll of the next tier | `:22767` |
| Transaction: fingerprint re-check, UPGRADE-BEGIN flushed, materials out slot by slot (bags too, 0.2.23), new stack written into the item's OWN slot, other mods' keys carried (`GearData.carry`, Requip stamp kept), counts checked, every failure restored | `:22975` on (`upgrade`); header `:107-153`, 0.2.23 points 7-9 |
| No coins, no Smithing XP for an upgrade | header `:107-153` |
| Engine fact: a bench recipe never takes a stack with metadata, so rolled gear can never be a bench input (why the page exists) | header, 0.2.22 "WHY NOT THE BENCH" |
| Soul Cage recipes (SkyyArmory 0.1.21): cage N = cage N-1 x1 + that metal wand's bars + essence (Life 15, Life 15, Fire 15, Ice 15, Water 12, Lightning 12, Void 10, Concentrated Life 1) | `SkyyArmory/build_skyyarmory_0.1.21.py:4168-4179`, `:4330-4356` |
| Multitool merge (0.2.21) + Multitools ids `Tool_Hatchet_Pickaxe_Multitool_<Tier>` (Crude..Onyxium) | `:4351-4354`, `:21896-22100` |
| Tool tiers by id word Crude 0 / Wood 0 / Copper 1 ... Onyxium 7 | `:4347-4365` |

So the engine for "up" steps exists; this spec adds: more rows, a branching path, a "next item's own recipe" cost mode, a per-row
"special allowed" flag (Set / Mythic), a set-gated step, a row level for Mythic rows and the CONVERT kind.

## 2. The ladders and their per-step costs

### 2.0 The cost rule (one rule, three cases)

Skyy 2026-10-11 (line 165): upgrading is MORE difficult than crafting. So an upgrade never refunds anything and never costs less than
a fresh craft of the next tier. The old item is the price of keeping your rarity + lines.

| Case | Cost of one step | Why |
|---|---|---|
| A. The next tier has a normal recipe (weapons, Mining armor, Foraging / Farming armor) | the next item's OWN recipe in full (read live) + the old item | = a fresh craft + the old item: "harder than crafting", the minimum |
| B. Gathering gear (line 175 "with Enchanted materials") whose next recipe holds NO Enchanted item (Mining armor) | case A + **1 Enchanted ingot of the next metal per piece** | Skyy's Enchanted rule |
| C. No recipe exists (lifelong tools: crafting removed, line 169) | **1 Enchanted ingot of the next metal** (Skyy's example, "and so on") | Skyy's example literally |
| D. Already a ladder recipe (Soul Cages: cage + bars + essence) | unchanged (live) | line 155 "the next tier's materials (bars + essence)" |
| E. Mythic boss ladders (Dragon) | a written cost of boss-drop items (section 5) | line 156 |

The task's default ("next recipe minus the old item's share") is shown for comparison in 2.5 / 2.3; it is CHEAPER than a fresh craft, so
it breaks line 165 (question 2).

### 2.1 Enchanted ingot prices (python3)

Method: ratio 100 (`docs/answered/bags.md:59` "Always 100"); Enchanted mid = floor(100 x ORE base x 1.10) - priced from the raw ore, never
from bars (`research/cloud/Chain-Premium-Fix.md` C4: Enchanted from bars at bar value is a 1.08 loop); instant buy = floor(mid x 1.10),
sell = floor(mid x 0.90); ore bases `docs/answered/economy.md:20`. Enchanted Mithril is staged (with the 0.7 veins) and Onyxium is not on the
launch list (`research/cloud/enchanted-art/README.md`) - their steps stay refused ("not on this server") until the item exists.

| Metal | Ore base | Enchanted mid | Instant buy | Sell | Loop: buy 100 ore -> smelt -> compress -> sell |
|---|---|---|---|---|---|
| Copper | 5 | 550 | 605 | 495 | 0.99 (loss) |
| Iron | 16 | 1,760 | 1,936 | 1,584 | 0.93 |
| Thorium | 48 | 5,280 | 5,808 | 4,752 | 0.91 |
| Cobalt | 144 | 15,840 | 17,424 | 14,256 | 0.90 |
| Adamantite | 480 | 52,800 | 58,080 | 47,520 | 0.90 |
| Mithril | 1,440 | 158,400 | 174,240 | 142,560 | 0.90 |
| Onyxium | 3,712 | 408,320 | 449,152 | 367,488 | 0.90 |

(Copper's 0.99 is floor rounding of a 5-coin ore; still a loss. Buying 100 bars instead: 0.75-0.83.)

### 2.2 Tools + multitools (lifelong, case C)

Ladders (both ends = vanilla ids, build-asserted; Wood / Scrap / Steel / Bronze rungs are not on a lifelong ladder):

| Row | Ladder |
|---|---|
| Pickaxe | `Tool_Pickaxe_Crude > _Copper > _Iron > _Thorium > _Cobalt > _Adamantite > _Mithril > _Onyxium` |
| Hatchet | `Tool_Hatchet_Crude > _Copper > ... > _Onyxium` |
| Hoe | `Tool_Hoe_Crude > _Copper > _Iron > _Thorium` (vanilla stops at Thorium - question 9) |
| Sickle | `Tool_Sickle_Crude > _Copper > _Iron` (vanilla stops at Iron - question 9) |
| Multitool (after rebirth 1, line 170) | `Tool_Hatchet_Pickaxe_Multitool_Crude > _Copper > ... > _Onyxium` |
| Pickaxe / hatchet -> Multitool (line 160) | second path on the same tier: the other tool of the SAME tier is the material (the 0.2.21 merge rules: best rarity, merged lines); shown only after rebirth 1 |
| Fishing rod | `SkyyFishing_Rod_<Metal>` ladder in SkyyFishing (ids UNVERIFIED here; same cost rule) |
| Shovel | none (line 172: a plain craft item) |
| UT / Mythic special tools | none (UT: fixed band, never upgraded; Mythic: no tool ladder) |

Per step cost (python3: the 2.1 instant-buy column; running total = sum of the steps):

| Step | Pickaxe / hatchet / hoe / sickle / rod | Multitool (default x2: one pickaxe step + one hatchet step) | Running total, one tool |
|---|---|---|---|
| Crude -> Copper | 1 `Skyy_Ench_Copper` (605) | 2 (1,210) | 605 |
| Copper -> Iron | 1 `Skyy_Ench_Iron` (1,936) | 2 (3,872) | 2,541 |
| Iron -> Thorium | 1 `Skyy_Ench_Thorium` (5,808) | 2 (11,616) | 8,349 |
| Thorium -> Cobalt | 1 `Skyy_Ench_Cobalt` (17,424) | 2 (34,848) | 25,773 |
| Cobalt -> Adamantite | 1 `Skyy_Ench_Adamantite` (58,080) | 2 (116,160) | 83,853 |
| Adamantite -> Mithril | 1 `Skyy_Ench_Mithril` (174,240) | 2 (348,480) | 258,093 |
| Mithril -> Onyxium | 1 `Skyy_Ench_Onyxium` (449,152) | 2 (898,304) | 707,245 |

In gathering terms each step = 100 ore of the next metal (Mining 100 ore at Fortune 0) - about the next tier's first collection tiers.
Hoes / sickles / rods pay metal too (cross-skill rule line 164: "T2 tools need T2 materials"). Rebirth (line 169: back to Crude keeping
rarity) is the rebirth code's job: it writes the FIRST id of the row; the ladder table only tells it which that is.

### 2.3 Mining armor (vanilla metal sets, cases A + B)

Rows (the 28 ids of `research/cloud/Mining-Armor-Spec.md` 2.1): one row per slot, e.g.
`Armor_Copper_Head > Armor_Iron_Head > Armor_Thorium_Head > Armor_Cobalt_Head > Armor_Adamantite_Head > Armor_Mithril_Head > Armor_Onyxium_Head`.

Cost = the next piece's vanilla recipe (bars, read live) + 1 Enchanted ingot of the next metal. python3 with PLACEHOLDER bar counts
(Head 5 / Chest 8 / Legs 7 / Hands 4 = 24 per set; the real vanilla counts are UNVERIFIED) at bar instant buy (bar mid = floor(ore x 1.20)):

| Step (whole set) | Fresh craft of the next set | Default upgrade (recipe + 4 Enchanted) | x a fresh craft | Task default "minus the old share" (by value) |
|---|---|---|---|---|
| Copper -> Iron | 480 | 8,224 | 17.1 | 360 (saves 6 bars - cheaper than crafting) |
| Iron -> Thorium | 1,488 | 24,720 | 16.6 | 1,116 |
| Thorium -> Cobalt | 4,536 | 74,232 | 16.4 | 3,402 |
| Cobalt -> Adamantite | 15,192 | 247,512 | 16.3 | 11,394 |
| Adamantite -> Mithril | 45,600 | 742,560 | 16.3 | 34,200 |
| Mithril -> Onyxium | 117,576 | 1,914,184 | 16.3 | 83,283 |

Share method: old pieces' bar value / next bar value, floored (Copper 5 / Iron 16 = 0.31 of a bar each ...). The metals never share an
ingredient, so a per-ingredient "minus" would save nothing at all; only a value rule gives any discount.

Whether this ladder is worth having depends on question 1: today (0.2.15) Mining pieces are rarity Set with NO random lines, so an
upgrade keeps nothing a fresh craft lacks. Line 175 ("keep rarity + rolls") suggests gathering armor rolls rarity like tools (0.2.17);
then a Legendary Mining chest is worth ~17 crafts' cost to keep (python3: P(Legendary or better) = 5 %, i.e. 20 crafts expected).

### 2.4 Foraging tree sets + Farming crop sets (case A - the recipes already ARE Enchanted)

Rows by base id (`research/cloud/Gathering-Armor-Stats.md` 1.2): `Armor_Foraging_F1_<Piece> > F2 > F3 > F4 > F5` and
`Armor_Farming_P1_<Piece> > P2 > ... > P7` (4 rows each). Cost = the next piece's recipe = 2 / 4 / 3 / 1 Enchanted of the next key material
(Head / Chest / Legs / Hands) + its Plant Fiber / Tree Sap / cloth extras. python3, set totals at instant buy (Gathering-Armor-Stats 4.2
method; cloth left out, UNVERIFIED price):

| Step | Set step cost | Step | Set step cost |
|---|---|---|---|
| F1 Grove -> F2 Autumn (Maple) | 9,700 | P1 Wheat -> P2 Carrot | 2,440 |
| F2 -> F3 Savanna (Gumboab) | 9,830 | P2 -> P3 Cauliflower | 7,280 |
| F3 -> F4 Northern (Redwood) | 24,480 | P3 -> P4 Pumpkin | 7,280 + cloth |
| F4 -> F5 Wastes (Sallow) | 10,090 | P4 -> P5 Chilli (Tomato) | 19,380 + cloth |
| | | P5 -> P6 Cotton | 19,380 + cloth |
| | | P6 -> P7 Onion (Potato) | 48,420 + cloth |

Equal to a fresh craft + the old piece (line 165 satisfied without an extra surcharge). The collection gate still applies: the step is
refused until you could craft the next piece yourself (the same unlock the recipe needs; bought Enchanted never counts).
Looks: a look item (`Skyy_Look_<BaseId>_<Tree>`) upgrades through its base id (`gear:base`) and comes out as the next tier's CRAFTED look;
the page says so; re-pick the look in the Wardrobe (question 12).

### 2.5 Metal weapons + class weapons (case A)

Rows are GENERATED at build, never hand-typed: for every family prefix the build finds ids `<Family>_<Tier>` for Crude / Wood, Copper,
Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium in Assets.zip + the SET jars (SkyyArmory) and writes a row with every tier that exists
(a family with fewer than 2 tiers = no row). Families: vanilla swords, battleaxes, maces, daggers, spears, shortbows, crossbows (UNVERIFIED
id words), SkyyArmory `Weapon_Wand_`, `Weapon_Staff_`, `Weapon_Spellbook_`, `Weapon_Kunai_`, `Weapon_Bo_`, `Weapon_Fist_Gauntlets_`, the wraps
by their cloth column (`Weapon_Fist_Wraps_Linen > Cotton > Silk > Cindercloth > Shadoweave`), the crossbows incl. ours
(`Weapon_Crossbow_Copper_Wynn > ..._Iron > (pack tiers) > ..._Mithril > Weapon_Crossbow_Onyxium_Wynn`). Never: UT ids, Mythic ids, the
`_Wynn` + vanilla twins of one tier twice (the build asserts one id per tier per row).

Cost = the next item's own recipe in full. python3 (PLACEHOLDER 6 bars of the next metal; Copper wand / shortbow = 4 bars, known):

| Step | Fresh craft | Default upgrade | Task default (minus share) | + 1 Enchanted (question 2 option) | Expected cost to CRAFT a Rare+ / Legendary+ of that tier |
|---|---|---|---|---|---|
| Copper -> Iron | 120 | 120 + the old weapon | saves 1 bar | 2,056 | 800 / 2,400 |
| Iron -> Thorium | 372 | 372 + old | saves 2 bars | 6,180 | 2,480 / 7,440 |
| Thorium -> Cobalt | 1,134 | 1,134 + old | saves 2 | 18,558 | 7,560 / 22,680 |
| Cobalt -> Adamantite | 3,798 | 3,798 + old | saves 1 | 61,878 | 25,320 / 75,960 |
| Adamantite -> Mithril | 11,400 | 11,400 + old | saves 2 | 185,640 | 76,000 / 228,000 |
| Mithril -> Onyxium | 29,394 | 29,394 + old | saves 2 | 478,546 | 195,960 / 587,880 |

Method: craft odds Normal 60 / Unique 25 / Rare 10 / Legendary 4 / Fabled 1 (Smithing step-up ignored): Rare or better = 15 % -> 20/3
crafts expected, Legendary or better = 5 % -> 20 crafts. The default keeps an upgrade worth it for Rare+ items and pointless for Normal ones
(just craft fresh). With the +1 Enchanted surcharge (16-17 crafts' worth) it pays only for Legendary+.

Onyxium crossbow (line 129 "Upgrade of Mithril crossbow"): its recipe takes a Mithril crossbow, so a ROLLED Mithril crossbow can never be
used at the bench (engine fact) - the generated crossbow row reads that recipe live (case D, like the cages). UNVERIFIED: whether SkyyArmory
0.1.21 already ships that recipe shape (`SkyyArmory/build_skyyarmory_0.1.21.py:670`, `XBOWS`).

### 2.6 Soul Cages (case D, live)

`Weapon_Wand_SoulOrb > Weapon_Wand_SoulCage_Copper > _Iron > _Thorium > _Cobalt > _Adamantite > _Mithril > _Onyxium` (the default row).
Cost per step = that metal wand's bars (Copper 4 ... Onyxium 6; middle tiers = the vanilla shortbow counts, UNVERIFIED here) + essence Life 15,
Fire 15, Ice 15, Water 12, Lightning 12, Void 10, Concentrated Life 1 (= 100 Life). No change: a cage is only ever made from the cage before,
so the ladder IS the craft (line 165 already holds).

### 2.7 Never on a ladder

UT items (fixed band, line 146 / Untiered-Mythic 1.1), Mythic boss gear EXCEPT rows flagged in section 5, Set quest gear (quest Sets keep
their quest level), unidentified items and bags, shovels, Crude armor / robes (no next tier in their family), pack-mod items unless a row
names them (The Armory's own chains Antique Dragon -> Iron Dragon -> Cobalt Dragon, Rook -> Elite Rook, Scorpion -> Elite Scorpion are
recipe-read rows once The Armory is back - case D, runtime ids only, `research/Pack-Armor-Plan.md:98-102`).

### 2.8 Bazaar / coin loop check (python3 + structure)

| Path | Result |
|---|---|
| Buy ore / bars -> compress -> sell Enchanted | 0.90-0.99 (table 2.1): a loss |
| Buy materials -> upgrade -> sell the item | gear is not a Bazaar product (SkyyBazaar 0.1.7 trades only its product list; `market:veto` walls Mythic / UT / Set, `SkyyBazaar/build_skyybazaar_0.1.7.py:10-19`); the AH is player to player (no coins created) |
| Upgrade -> salvage | an upgraded item always carries a document, and a bench / salvage recipe never takes a stack with metadata (engine fact, 0.2.21); the multitool salvage cap stays (`:286-290`). UNVERIFIED that the Salvagebench uses the same matching (probe U-P7) |
| Upgrade refunds | none: every cost is >= 0 per material; the "minus" option, if ever picked, floors each material at 0 (never a negative = never a refund) |
| Upgrade -> Smithing XP | none (0.2.22: no XP) - no XP loop; question 11 |
| Convert A -> B -> A | costs both ways, changes no level / rolls: a coin sink, never a gain |

No loop exists by construction: the upgrade has no exit that pays more than its inputs.

## 3. What an upgrade keeps and what it re-rolls

| Part | Upgrade (tier up) | Convert (type change, section 6) |
|---|---|---|
| Rarity | KEPT (incl. a Sigil-raised rarity, line 176) | KEPT |
| Modifier lines | KEPT, values re-levelled x F(new) / F(old), never lower, capped at a fresh roll of the new level unless already above (live `relevel`) | KEPT as they are (same level); a line the new type cannot hold (question 10) is re-rolled once into an allowed line of the same rarity |
| Reforge name / count, weapon speed tier | KEPT | KEPT |
| Item LEVEL | RE-SET: the next tier's craft level (your skill moved into its band; lifelong tools / gathering armor: your skill capped by tier, line 164 / 175); Mythic rows: the row's level (section 5) | KEPT |
| Bought level-ups (`lvU`) | DROPPED (made at your level; the page warns) - Mythic rows too (the row level is above old + 2) | KEPT |
| Tool Upgrade Points (line 164, when they exist) | KEPT (a document field: the clone carries it) | - |
| Set membership | the NEXT item's set (by id for Mining / gathering sets; a gated row writes its new `set` id, section 5); the old `set` id is never carried | the target type's set id |
| Bag origin (`box`) | DROPPED | DROPPED |
| Other mods' keys (Requip stamp, loadout picks) | KEPT (`GearData.carry`, 0.2.23) | KEPT |
| Durability | full (durability OFF by default, line 41); if ON: the old fraction x the new max (Recolor-Plan rule) | same fraction |
| Plain item (no document) | the normal craft roll of the next tier (live) | refused (nothing to keep - craft it) |

## 4. Engine changes (SkyyGear, on top of 0.2.24)

| # | Change | Why |
|---|---|---|
| E1 | **Paths**: an item may have several next steps; the parser keeps one "up" per (from, to) and refuses only exact duplicates; the Anvil lists each path as its own button | Multitool path (line 160), Dragon elements (5 branches) |
| E2 | Cost mode `B(@)` = the next item's OWN recipe (lowest recipe id, output x1); paid through SkyySacks `sacks:fn:craftPay` / `craftRefund` (resource-type inputs like "any wood" work, as on the Craft tab); `B(@+Skyy_Ench_Iron*1)` = recipe + extras | case A / B (weapon and armor recipes do not contain the old item) |
| E3 | Row flag `!` after an id = this step may take a Set / Mythic document (today always refused); never UT | gathering Sets, Mythic Dragon |
| E4 | Set gate `B[set=dragon_base_heavy=>dragon_fire_heavy]`: the step only shows for documents with that `set`, and writes the new one; allows from == to (same id, new set) | Armory hands / legs have one colour (section 5) |
| E5 | Row level `B{L80}`: the new item level for a Mythic step (Mythic gear carries the boss level, not your skill; the wear gate stays) | Mythic rows have no craft band |
| E6 | CONVERT kind `A~B~C(cost)`: any member to any other member, same tier + slot only (build check: same slot word, same tier); never combined with "up" in one row | line 156 |
| E7 | Row generator at build for weapons (2.5) + Server Setup "Reset ladders to the pack default" button | 100+ rows nobody should type |

Config: `upgrade.ladders` grows past 2000 characters - raise the limit (the row says 2000, `:4738`) or split into `upgrade.ladders.<group>`
rows (tools, mining, foraging, farming, weapons, dragon) - the grouped rows are easier to edit (question 13).

## 5. The Mythic DRAGON set

### 5.1 Source and ladder

| Step | What | Where / level |
|---|---|---|
| D0 | **Dragon set** (base): Head / Chest / Hands / Legs in Heavy, Light and Cloth variants, rarity Mythic (purple), a full-set bonus (Mythic set rules, Untiered-Mythic 2.3) | the first dragon boss = **The Dragon, Zone 5** (Lv 70-75; replaces the "Drakonite Mythic set pieces" placeholder in Untiered-Mythic 2.4) - question 6 |
| D1 | **Fire / Water / Earth / Thunder / Air Dragon set**: an Upgrade path per element from each base piece | one **elemental drake mini-boss per element in the next zone** (the Lv 76-100 band beyond Zone 5; Zone-Bosses-Ideas "Beyond: Frost Dragon, Fire Dragon") drops that element's upgrade item |
| Convert | Heavy <-> Light <-> Cloth of the same element and slot | anywhere (Anvil) |

Elements = the five of `research/cloud/Element-System-Spec.md` 2 (shown names Fire, Water, Earth, Thunder, Air).

### 5.2 Upgrade items and drops

| Item (id) | Drops from | Rule |
|---|---|---|
| `Skyy_Drake_Heart_<Element>` ("Fire Drake Heart" ...) | that element's drake mini-boss | 1 per kill per eligible player (the Mythic 15 % damage credit), 2 in Challenge mode; the Appeals Desk respawn works (boss level x 25 coins / 60 s: 2,000-2,250 coins at Lv 80-90) |
| `Skyy_Dragon_Scale` (base) | The Dragon (Zone 5), 3 per kill per eligible player | the Convert cost |

Per piece step cost (written row cost): Head 2 / Chest 3 / Legs 2 / Hands 1 hearts = **8 per set** (python3: 8 kills, 4 in Challenge; 40
kills for all five elements of one type). Hearts are tradable materials but never Bazaar products (Mythic wall: listed in `market:veto`).

### 5.3 Looks (Armory ids at runtime only - all UNVERIFIED until The Armory loads on 0.7)

The Armory already ships colour variants, so NO recolouring of their files is needed (PACK.md: never copy / re-upload their art):

| Type | Armory base (Pack-Armor-Plan) | Base Dragon | Fire | Water | Earth | Thunder | Air |
|---|---|---|---|---|---|---|---|
| Heavy | Cobalt Dragon Set (`research/Pack-Armor-Plan.md:737`) | `...BlackPurple` chest / helm | `...BlackRed` | `...BlackCyan` | `...BlackGreen` | `...BlackYellow` | `...White` |
| Light | Antique Dragon Set (`:739`), re-typed Light by look | Purple helm / chest | Red | Cyan | Green | Yellow | White |
| Cloth | none in The Armory | question 7 | | | | | |

Hands / Legs exist in one colour (`CobaltDragonGauntletsBlack`, `CobaltDragonLeggingsBlack`; Antique `Guantlets` / `Leggings`), so those
steps are SET-GATED same-id steps (E4): the piece keeps its id, its `set` becomes `dragon_<element>_<type>`, its level the row level.
Every row is set-gated, so a plain Cobalt Dragon piece from the Zone 2 split set (Untiered-Mythic 2.4, Broodmother + Goblin Duke) never
shows a Dragon path (question 8). Fallback if The Armory stays broken on 0.7: our own ids built from VANILLA models recoloured at build
time (vanilla-derived art generated into the jar, never committed).

### 5.4 Stats (placeholders, Mythic rules)

| Set | Level | Full-set bonus (all 4, same set id) |
|---|---|---|
| Dragon (base) | the Dragon's level (70-75) | +150 Health, +5 % Defense (Heavy) / +5 % crit chance (Light) / +10 % max Mana (Cloth) |
| <Element> Dragon | the drake's level (row level, e.g. 80) | the base bonus + 10 % <element> damage + <element> Defence 10 (the Defence line goes live with the element system; hidden until then) |

Mythic level-up cap +2 stays; base stats x1.10 of a Fabled, 6 Mythic modifiers rolled at the drop (Untiered-Mythic 2.1); the upgrade keeps
them (section 3). Mixed types or elements = no bonus (one set id per element per type, question 10).

### 5.5 Convert cost

1 `Skyy_Dragon_Scale` per piece, both ways. Keeps everything (section 3); armor Health / resistance follow the new type automatically
(SkyyGear reads the type from the item). Rows: `<HeavyFire_Chest>~<LightFire_Chest>~<ClothFire_Chest>(Skyy_Dragon_Scale*1)!` x 4 slots x 6
(base + 5 elements).

## 6. CONVERT in general

Built generic (E6) but only Dragon rows ship. Rules: same tier, same slot; source and target both on the row; Mythic / Set need `!`; cost
>= 1 item (never free); refused for UT, unidentified and plain items. Later candidates (each a Skyy decision): Mythic boss sets that drop in
two types, The Armory's colour variants (but colour = a LOOK = the Wardrobe, not a convert).

## 7. The page (Anvil, SkyyGear 0.2.24) - layout

Right column under the item, one block per path (max 6 visible, scroll beyond):

```
[ item icon ]  Iron Pickaxe [Lv 22]  - Legendary
------------------------------------------------------------------
UPGRADE  -> Thorium Pickaxe [Lv 22]       1 Enchanted Thorium Ingot   0 / 1 (gold)   [ Upgrade ]
         -> Multitool (Iron)               Iron Hatchet (pick one)     -             [ Merge ]    (after rebirth 1)
CONVERT  (Dragon pieces only)  -> Light Fire Dragon Chestplate   1 Dragon Scale  3 / 1  [ Convert ]
Keeps: rarity, 4 lines (re-levelled), reforge "Sharp". Lost: 2 bought level-ups.
```

Every button greys with its reason (the live `check` texts); "Keeps / Lost" is the live `lossText` line.

## 8. Dupe / loss safety

| Risk | Answer |
|---|---|
| Base transaction | the live 0.2.22 / 0.2.23 one (fingerprint, UPGRADE-BEGIN flushed, materials out, the item's OWN slot rewritten, restore on failure, counts checked) - unchanged for every new row |
| `@` recipe costs via SkyySacks | order: plan -> UPGRADE-BEGIN (lists the recipe id + the measured before-counts, the 0.2.23 FIXER 2 evidence way) -> `craftPay` -> swap -> `craftCommit`; swap failure -> `craftRefund` + UPGRADE-FAILED; a crash between pay and swap can only LOSE the materials (logged), never copy |
| Branching paths | the click carries the path id + the item fingerprint + the page token; a stale page or a changed table snapshot (`tab()` is one immutable snapshot) refuses |
| Set-gated same-id step | the swap still writes a NEW stack into the same slot; the fingerprint includes the document, so a second click on the old fingerprint is refused (no double charge) |
| Mythic / Dragon items in Requip | fetched first (live 0.2.23 point 9); the Requip stamp is carried, loadout picks follow |
| Convert ping-pong | each way costs a Scale; the document never gains level / lines; logged CONVERT-BEGIN / DONE like an upgrade |
| Hearts / Scales | MaxStack normal, no document; mini-boss drops use the boss-loot path (per participant, written before the give); never sold by NPCs |
| Rebirth downgrade (tools / gathering armor to tier 1) | the rebirth round's own transaction; it reads the row's first id from the same snapshot |
| Rollback | old jars see upgraded items as ordinary gear documents (safe); set-gated Dragon pieces carry a `set` id old jars ignore. FLOOR only for new item ids (hearts, scales): never roll SkyyGear / SkyyMobs below the Dragon round once they exist |

## 9. Build phases + probes (all UNVERIFIED - need the game)

| Phase | Round | Contents | Needs |
|---|---|---|---|
| U0 | probes (local, no build) | P1-P8 below | - |
| U1 | SkyyGear after 0.2.24 (full round: items + saved data) | E1-E4, E6 engine, E7 weapon row generator, Mining armor rows, the crossbow row; Soul row unchanged | 0.2.24 Anvil |
| U2 | with the GATHERING / lifelong-tools round | tool + multitool + rod rows (written Enchanted costs); STOP if `Skyy_Ench_Copper` is not in the SET | Enchanted phase A items |
| U3 | with each gathering armor round | Foraging + Farming rows (case A) | those armor items |
| U4 | Dragon round (after Zone 5 + the next zone + The Armory on 0.7): SkyyMobs drake bosses + drops, SkyyGear Dragon rows + E5 + set table rows | Mythic boss stage, Element system |

| Probe | Question |
|---|---|
| P1 | The Armory ids on 0.7 (Cobalt / Antique Dragon colour variants still named as in `research/Pack-Armor-Plan.md:737-739`) |
| P2 | Vanilla bar counts per armor piece and per weapon family / tier (replace the 2.3 / 2.5 placeholders) |
| P3 | Which vanilla weapon / armor recipes use resource-type inputs; `sacks:fn:craftPay` by recipe id from inside an Anvil click |
| P4 | Hoes above Thorium / sickles above Iron: do they exist anywhere (pack mods)? else SkyyGear-built copies (question 9) |
| P5 | Dragon_Fire / Dragon_Frost roles as mini-bosses at a smaller scale + recolour per element at build time |
| P6 | `Skyy_Ench_*` items live (phase A) and their real ids |
| P7 | The Salvagebench refuses stacks with metadata like every bench (else an upgraded item could be salvaged - still capped, but check) |
| P8 | Anvil right column fits 2 paths + 1 convert row at 1100 x 880 with the vanilla tab look (`tools/skyyui.py`) |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Gathering armor (Mining / Foraging / Farming): should pieces roll a rarity + gathering lines like tools, so an upgrade keeps something (your "keep rarity + rolls")? The green "Set" bonus stays as a green block, like Mythic sets keep purple. | [yes, rarity like tools; the set bonus stays] |
| 2 | Weapon upgrade cost: the next weapon's recipe in full (the old weapon is the price - "harder than crafting"), or cheaper (recipe minus the old share), or + 1 Enchanted ingot on top? | [full next recipe, no Enchanted] |
| 3 | Tools: 1 Enchanted ingot of the next metal per step, Crude -> Copper too; hoes, sickles and rods pay metal like pickaxes? | [yes] |
| 4 | Multitool tier step = 2 Enchanted (a pickaxe step + a hatchet step) or 1 (a rebirth reward)? | [2] |
| 5 | Mining armor step = the next piece's recipe + 1 Enchanted ingot per piece (about 16x a fresh craft)? | [yes, only if 1 = yes; else no Mining ladder] |
| 6 | First dragon boss = The Dragon in Zone 5 (Lv 70-75) drops the base Dragon set; the 5 elemental drakes live in the next zone (Lv 76-100)? | [yes] |
| 7 | Dragon looks: Heavy = Armory Cobalt Dragon colours, Light = Armory Antique Dragon colours (no recolour needed). Cloth has no Armory dragon set - pick one, or vanilla cloth recoloured at build time? | [vanilla cloth recolour for now] |
| 8 | The Zone 2 split set already uses Cobalt Dragon (plain colours). Keep it and give the Zone 5 Dragon set the Black colour variants? | [yes] |
| 9 | Vanilla has no hoe above Thorium and no sickle above Iron. Make our own Cobalt+ hoes and Thorium+ sickles (recoloured vanilla at build)? | [yes] |
| 10 | Dragon: one set bonus per element AND type (mixing Heavy + Light = no bonus); convert re-rolls a line the new type cannot hold? | [yes / yes] |
| 11 | Upgrades pay Smithing XP? | [no, like now] |
| 12 | Upgrading a look item (Birch F1) gives the next tier's crafted look (Maple); first look change after an upgrade free in the Wardrobe? | [yes / yes] |
| 13 | Split the ladder table into groups in Server Setup (tools, mining, foraging, farming, weapons, dragon)? | [yes] |
| 14 | Drake Hearts per piece 2 / 3 / 2 / 1 (8 per set), 1 per kill (2 in Challenge)? | [yes] |

## For the local session

1. All of section 9's probes P1-P8 (UNVERIFIED: Armory ids on 0.7, vanilla bar counts, resource-type recipe inputs, hoe / sickle tiers,
   dragon roles, Enchanted ids, Salvagebench metadata rule, Anvil layout).
2. The vanilla weapon family id words (sword, battleaxe, mace, daggers, spear, shortbow, crossbow) for the E7 generator - read from
   Assets.zip at build, assert at least 2 tiers per row.
3. Whether SkyyArmory 0.1.21 already makes the Onyxium crossbow FROM a Mithril crossbow (line 129) - if yes, the row is recipe-read (case D).
4. `SkyyFishing_Rod_<Metal>` ids for the rod ladder (U2).
5. Merge with the GATHERING spec (RESUME wave 3 item 7): that spec owns Upgrade Points, Sigils and rebirth resets; this file owns the rows
   and costs. If it picks other step costs, its numbers win and section 2.2 follows.
6. Untiered-Mythic 2.4 "the Dragon Lv 70 = A3 + Drakonite Mythic set pieces" vs Dragon-Quest-Spec "dragon boss at 75": one level for the
   Zone 5 Dragon before U4.
