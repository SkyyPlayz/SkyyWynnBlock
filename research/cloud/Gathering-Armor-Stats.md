# Gathering armor stats - Foraging (tree sets) + Farming (crop sets)

Cloud draft, 2026-10-09. Spec only: nothing built, nothing committed by this agent. Feeds the SkyyGear gathering-armor rounds that come after
the Mining armor round (Skyy 2026-10-09: "We we are making the vanilla armor the mining gear so I'd do that first by then Quirk should be done
with the foraging armor, and starting on the farm armor"). Every number is a placeholder and a Server Setup row (times in seconds).
Arithmetic: python3 with exact fractions (scratch only, method shown under each table).

Inputs read: `ART-RESUME.md` (item 14 + progress), `art/gathering-armor/README.md` + `art/gathering-armor/manifest.json`,
`research/cloud/gathering-armor-art/README.md`, `research/Gathering-Progression-Spec.md` (2.2, 2.3, 3.2-3.5, 4),
`research/cloud/Foraging-Armor-Design.md`, `research/cloud/Crop-Armor-Spec.md`, `research/cloud/Gathering-Armor-Mining-Farming.md`,
`research/cloud/Gathering-Numbers-Reconciled.md`, `research/cloud/Enchanted-Materials-Draft.md`, `research/cloud/Chain-Premium-Fix.md`,
`research/cloud/Untiered-Mythic-Spec.md` (3.2), `research/Recolor-Plan.md`, `research/cloud/Wardrobe-Spec.md`, read-only
`SkyyGear/build_skyygear_0.2.13.py` (newest in the repo; 0.2.14 = rarity G1 is building locally and is not in the repo yet) and
`SkyySkills/build_skyyskills_0.4.27.py`. `research/cloud/Mining-Armor-Spec.md` did not exist when this was finished (written in parallel);
section 5 says how to keep the two compatible.

## 0. Decisions this follows (not re-decided; newest wins)

| Where | Decision (short) | Used in |
|---|---|---|
| `docs/answered/gear.md:116` (2026-10-08 ARMOR SPLIT) | mining = vanilla metal sets; FARMING (crop sets) + FORAGING (bark plates) = our own | whole file |
| `docs/answered/gear.md:118` (2026-10-08 per tree) | 5 tree tiers F1-F5 from `research/Gathering-Progression-Spec.md` 2.2; every tree its own design in its colours, **same tier stats**; looks swapped Alteration-style; replaces the 7 wood-name tiers (Softwood..Goldenwood) | 1, 2, 6 |
| `docs/answered/gear.md:125` (2026-10-08 GATHERING SETS) | gathering armor wears the green **Set** label; full set (all 4) = a small bonus Fortune of its skill; higher tiers add a little speed / move speed | 3 |
| `docs/answered/gear.md:128` (popup batch 2) | the gathering set table of `research/cloud/Untiered-Mythic-Spec.md` 3.2 "as tabled" (Q13); look swaps via The Armory's table + our Wardrobe; **craft the key-log set then swap**; **one design per crop**; Alteration Kit cost | 3, 6 |
| `research/cloud/Untiered-Mythic-Spec.md` 3.2 (locked by the line above) | rarity `set`, `set` field = family + tier, no random rarity ladder, set bonus per row T1 +1 / T2 +1.5 / T3 +2.5 +5% speed (later) / T4 +4 +8% / T5 +5.5 +10% +5% move / T6 +7.5 +12% +8% move / T7 +10 +15% +10% move + the family special; armor Fortune cap 15 after the bonus; mixed tiers no bonus (all 4 the same set id) | 3 |
| `docs/answered/gear.md:120`, `:122` (WARDROBE) | our own SkyyWardrobe edits the look of a whole set; 500-coin set look edit (defaults all yes) | 6 |
| `docs/answered/gear.md:124` (RARITY NAMES) | Set = normal pieces until all 4 are worn, then a buff | 3 |
| `docs/answered/gear.md:65` (2026-10-05 FORAGING ARMOR) | Foraging Fortune + chopping speed (+ Foraging XP higher up), low Defense, **Tree Feller on the higher tiers** | 2, 3 |
| `docs/answered/gear.md:70`, `:71`, `:77`, `:84` | crop / food armor up the 7 Farming Bench pairs, the v2 look approved | 1, 2 |
| `docs/answered/gear.md:117` | recolour / look swaps keep rarity / level / modifiers / durability | 6 |
| `docs/answered/bags.md:59` | Enchanted ratio **always 100** | 4 |
| `docs/answered/bags.md:60` | launch with **18** Enchanted items (key logs Oak / Maple / Gumboab / Redwood / Sallow; key crops Wheat / Carrot / Cauliflower / Pumpkin / Tomato / Cotton / Potato), no Enchanted Blocks yet | 4 |
| `docs/answered/bags.md:63` | armor sets **cost about their unlock threshold** (was written as 6 / 3 / 1 Enchanted at ratio 160) | 4 (question 2) |
| `docs/answered/bags.md:66` | Enchanted items sell a bit above 100x base (premium, below any loop) | 4 |
| `docs/answered/economy.md:21`, `:79`, `:83` | log prices by tier (Oak 3, Maple 8, Gumboab 8, Redwood 20, Sallow 8 live); crops 2 / 6 / 16 / 40 in bench order; Tree Sap 12 | 4 |
| `docs/answered/skills.md:51` | Tree Feller table 1 / 2 / 4 / 5 / 6 / 10 extra logs, 3 s - reused, never a second system | 3 |
| `docs/answered/skills.md:71`, `:73` | hatchet swing bonuses only on wood; Heavy Hatchet is power, not swing | 2 |
| `docs/answered/skills.md:98` | the Foraging skill now gives Defense (not Health) | 2 (Defense stays low on the armor) |

Locked art status (ART-RESUME item 14, 2026-10-09): F1 Grove 5/5 approved (Oak, Birch, Beech, Ash, Aspen); F2 2/2 (Maple, Azure); F3 Gumboab +
Dry done, Bottletree + Palo held for a colour fix; F4 Fir, Cedar, Poisoned done, **Redwood** + Spiral held; F5 not started. Farming: concept
sheets approved (`research/cloud/gathering-armor-art/farming-sheet.png`, Wheat ... Onion), game-ready models not started.

## 1. Tiers, level bands and item ids

### 1.1 One row ladder for all three gathering families

The locked set table has rows T1-T7. Each family maps onto the row of the **same metal / zone**, so Mining, Foraging and Farming sets of one
zone give the same bonus (and the Mining spec can use the identical table):

| Row | Metal (Mining set) | Foraging tier (zone) | Farming pair | Band (SkyyGear `BANDS`, `SkyyGear/build_skyygear_0.2.13.py:1630-1633`) | Gate |
|---|---|---|---|---|---|
| T1 | Copper | **F1 Grove** (Zone 1) | **P1** Wheat / Lettuce | 1-18 (the `Armor_Copper` band) | skill 1 |
| T2 | Iron | **F2 Autumn + Azure** (Zone 1 Tier 3) | **P2** Carrot / Corn | 15-23 | 15 |
| T3 | Thorium | **F3 Savanna** (Zone 2) | **P3** Cauliflower / Turnip | 20-28 | 20 |
| T4 | Cobalt | **F4 Northern** (Zone 3) | **P4** Pumpkin / Aubergine | 25-38 | 25 |
| T5 | Adamantite | **F5 Wastes** (Zone 4) | **P5** Tomato / Chilli | 35-43 | 35 |
| T6 | Mithril | - (Orchard looks later) | **P6** Cotton / Rice | 40-49 | 40 |
| T7 | Onyxium | - | **P7** Potato / Onion | 40-49 (50+ later) | 40 |

- Gate skill: Foraging for the tree sets, Farming for the crop sets (`GATE_BY_KIND`, `SkyyGear/build_skyygear_0.2.13.py:1377`, already has
  `foraging` / `farming`). Crafted at your skill level clamped to the band ("crafted at your level").
- Why F(n) = T(n): the hatchet you use inside each tree tier is exactly that metal (F3 is chopped with the Thorium hatchet from Maple IV, F4
  Cobalt, F5 Adamantite then Mithril; `research/Gathering-Progression-Spec.md` 2.2 "Hatchet step"), and Zone 4's ore (Adamantite) is T5.
- Why P(n) = T(n): the set table's Farming column already runs Wheat-tier = T1 to the top crop = T7 (seven rows, seven pairs).
- Vanilla `Armor_Wood` is not part of this spec (stays vanilla; question 9).

### 1.2 Item ids (base = the crafted piece; looks = same stats, other model)

Base ids are **tier-coded** so a tree / crop word never sits in the id. Reason (VERIFIED in the script): SkyyGear finds an item's band by the
**first matching id word** (`LV_HEAD`, `SkyyGear/build_skyygear_0.2.13.py:1471`; tokens matched between underscores, `:1512`), and the family
words include **Cotton** (15), **Bamboo** (5) and **Onion** (5) (`FAMILIES`, `:1525` on). `Armor_Farming_Cotton_Chest` would get the cloth
Cotton band; a tier code cannot clash.

| What | Id pattern | Example | Count |
|---|---|---|---|
| Foraging base piece | `Armor_Foraging_F<n>_<Piece>` | `Armor_Foraging_F1_Head` (looks like Oak) | 5 tiers x 4 = 20 |
| Farming base piece | `Armor_Farming_P<n>_<Piece>` | `Armor_Farming_P1_Chest` (looks like Wheat) | 7 x 4 = 28 |
| Look of a base piece | `Skyy_Look_<BaseId>_<Look>` (the locked `research/Recolor-Plan.md` 4.3 pattern) | `Skyy_Look_Armor_Foraging_F1_Head_Birch`, `Skyy_Look_Armor_Farming_P1_Head_Lettuce` | Foraging 21 looks x 4 = 84; Farming 7 x 4 = 28 |
| Look family (ResourceType) | `Resource_Skyy_Forage_F<n>_<Piece>` / `Resource_Skyy_Farm_P<n>_<Piece>` | `Resource_Skyy_Forage_F1_Chest` | 20 + 28 = 48 |
| Set id (`set` field) | `forage_f<n>` / `farm_p<n>` | `forage_f1` | 12 |

Pieces: Head, Chest, Hands, Legs (vanilla armor slots; the art is drawn this way: `art/gathering-armor/manifest.json` "slots").
Total item ids at the end: 48 base + 112 looks = 160 (Recolor-Plan estimated 104 + 56 = 160: matches).

### 1.3 The looks per tier (crafted look in bold)

The crafted (base) look is the tier's **key** design ("craft the key-log set then swap", `docs/answered/gear.md:128`).

| Tier | Crafted look | Swap looks | Art (2026-10-09) | Display set name |
|---|---|---|---|---|
| F1 | **Oak** | Birch, Beech, Ash, Aspen | all 5 approved | Grove Bark |
| F2 | **Maple** | Azure | both approved | Autumn Bark |
| F3 | **Gumboab** | Dry, Bottletree, Palo | Gumboab + Dry done; Bottletree, Palo held (colour fix) | Savanna Bark |
| F4 | **Redwood** | Fir, Cedar, Poisoned, Spiral | Fir, Cedar, Poisoned done; **Redwood held** (colour fix) | Northern Bark |
| F5 | **Sallow** | Burnt, Petrified, Bamboo, Camphor, Banyan, Jungle, Blue Fig, Fire, Crystalwood | not started | Wastes Bark |
| P1 | **Wheat** | Lettuce | concept approved; models not started | Wheat Harvest |
| P2 | **Carrot** | Corn | concept | Carrot Harvest |
| P3 | **Cauliflower** | Turnip | concept | Cauliflower Harvest |
| P4 | **Pumpkin** | Aubergine | concept | Pumpkin Harvest |
| P5 | **Chilli** (as drawn) | Tomato | concept | Chilli Harvest |
| P6 | **Cotton** | Rice | concept | Cotton Harvest |
| P7 | **Onion** (as drawn) | Potato | concept | Onion Harvest |

- P5 / P7: the drawn sets are Chilli and Onion, but the pair's **key** crop (the Enchanted item, launch list `docs/answered/bags.md:60`) is
  Tomato / Potato. Default: the recipe uses the key crop's Enchanted item, the crafted look stays the drawn one (question 4).
- Display names per piece: "<Look> <vanilla piece word>", e.g. "Birch Bark Helmet", "Wheat Chestplate" (piece words read from the vanilla
  Iron set's language lines at build - UNVERIFIED).
- Icons: the art's own files (`Armor_Foraging_<Tree>_<Piece>.png`, `Armor_Farming_<Crop>_<Piece>.png`); the item JSON points at them, so the
  art never needs renaming.

## 2. Stats per piece

Shares of every set total: **Head 25% / Chest 35% / Legs 25% / Hands 15%** (the Mining + Crop drafts' split; the Foraging draft's 20 / 35 / 30 /
15 is dropped so all three families split the same way). All looks of one tier and slot carry identical numbers (family rule).

### 2.1 Foraging pieces (set totals; pieces pay their share)

| Tier | Foraging Fortune | Chopping Speed (swing, **later**) | Foraging Wisdom (XP) | Health (set, at band start) |
|---|---|---|---|---|
| F1 | 1 | +1% | - | 50% of vanilla Copper armor |
| F2 | 1.5 | +2% | - | 50% of Iron |
| F3 | 2.5 | +3% | - | 50% of Thorium |
| F4 | 4 | +4% | +2% | 50% of Cobalt |
| F5 | 5.5 | +6% | +4% | 50% of Adamantite |

### 2.2 Farming pieces (set totals)

| Tier | Farming Fortune | Farming Wisdom (XP) | Health (set, at band start) |
|---|---|---|---|
| P1 | 1 | - | 50% of Copper |
| P2 | 1.5 | - | 50% of Iron |
| P3 | 2.5 | - | 50% of Thorium |
| P4 | 4 | +2% | 50% of Cobalt |
| P5 | 5.5 | +4% | 50% of Adamantite |
| P6 | 7.5 | +6% | 50% of Mithril |
| P7 | 10 | +8% | 50% of Onyxium |

Per-piece Fortune (python3: total x 0.25 / 0.35 / 0.25 / 0.15): T1 0.25 / 0.35 / 0.25 / 0.15; T2 0.375 / 0.525 / 0.375 / 0.225; T3 0.625 /
0.875 / 0.625 / 0.375; T4 1.0 / 1.4 / 1.0 / 0.6; T5 1.375 / 1.925 / 1.375 / 0.825; T6 1.875 / 2.625 / 1.875 / 1.125; T7 2.5 / 3.5 / 2.5 / 1.5.

Rules:
- **Fortune unit** = the live tool unit: 1 Fortune = +1% chance of one extra drop (`SkyyGear/build_skyygear_0.2.13.py:53-59`). Wisdom = %
  extra gathering XP.
- **How it reaches the drops (LIVE path):** SkyyGear posts the worn armor as its own source `garmor` in `skill:bonus:<uuid>` with
  `dd.foraging` / `dd.farming` = Fortune / 100 and `xp.foraging` / `xp.farming` = Wisdom / 100 - the exact map shape the tool already posts as
  source `gear` (`SkyyGear/build_skyygear_0.2.13.py:77-80`) and SkyySkills reads on every award (`SkyySkills/build_skyyskills_0.4.27.py:764`,
  `:7979-7982`). Foraging Fortune counts on logs only (SkyySkills `perk.foraging.doubleDropOnly=_Trunk`), placed blocks never double.
- **While worn** (no held-tool check): logs / crops already filter by block. (The Crop draft's "only with a hoe or sickle held" is dropped so
  hand-harvesting counts - question 7.)
- **Caps:** `armor.fortune.cap` 15 (pieces + set bonus), `armor.wisdom.cap` 10, `armor.swing.cap` (question 6), all under SkyySkills'
  `perk.doubleDropMax`.
- **Chopping Speed is "(later)"**: hidden until a swing source for armor exists (the 2026-09-30 rule quoted in Untiered-Mythic 3.2). Today
  SkyyGear's tool line is Chopping **Power** (`SkyyGear/build_skyygear_0.2.13.py:45-52`, tooltip `:10595`); armor never touches power
  (`research/cloud/Gathering-Numbers-Reconciled.md` S7). Farming has no swing at all (hoes / sickles: Fortune only).
- **Health / Defense:** low on purpose. The item JSON's base Health = 50% of the same-slot vanilla metal piece of its row (read from Assets.zip
  at build, never committed; python3 on the Foraging draft's set totals: Copper 25 -> 12.5, Iron 46 -> 23, Thorium / Cobalt 61 -> 30.5,
  Adamantite / Mithril 68 -> 34). SkyyGear's armor Health curve H(L) (`base.hpCurve`, `:348-350`) scales it by item level like every armor.
  MaxDurability = the same vanilla piece's (UNVERIFIED numbers).
- **Under-level** (skill below the item level): no gathering lines and no set bonus (the tool rule `:62-65`: "works like a plain item").
- **Rarity = Set (green)**, always. Crafted pieces are stamped `set`, never rolled Normal..Fabled; the Smithing step-up never reaches Set
  (`LADDER = R_IDS[:6]`, `:1277`). SkyyGear's live `set` row gives 3 modifier slots (`RARITY_DEF`, `:1280-1281`): for gathering pieces they
  draw from a gathering pool **without Fortune** (Wisdom of the set's skill, Health, Defense), so the Fortune numbers above are the whole truth
  (question 8).

## 3. Full-set bonuses (the green Set label)

All 4 worn pieces must have the **same set id** (`forage_f1` ...). Looks share the set id, so Oak helm + Birch chest + Ash gloves + Aspen legs
IS a full Grove set. Under the locked rule there are no 2-piece bonuses (the drafts' Field Runner / 2-piece Green Thumb move into the full
set). The bonus Fortune is the locked T-row number; "(later)" lines stay hidden until their hook is live.

| Set | Row | Bonus Fortune (locked) | Speed (locked, later) | Move speed (locked) | Family special |
|---|---|---|---|---|---|
| Grove Bark (F1) | T1 | +1 Foraging Fortune | - | - | - |
| Autumn Bark (F2) | T2 | +1.5 | - | - | Tree Feller 1 (later) |
| Savanna Bark (F3) | T3 | +2.5 | +5% chopping | - | Tree Feller 2 (later) |
| Northern Bark (F4) | T4 | +4 | +8% chopping | - | Tree Feller 3 (later) |
| Wastes Bark (F5) | T5 | +5.5 | +10% chopping | +5% | Tree Feller 4 (later) |
| Wheat Harvest (P1) | T1 | +1 Farming Fortune | - | - | - |
| Carrot Harvest (P2) | T2 | +1.5 | - | - | - |
| Cauliflower Harvest (P3) | T3 | +2.5 | (harvest speed: no meaning, question 5) | - | - |
| Pumpkin Harvest (P4) | T4 | +4 | (question 5) | - | Sickle Range +1 (later) |
| Chilli Harvest (P5) | T5 | +5.5 | (question 5) | +5% | Sickle Range +1 (later) |
| Cotton Harvest (P6) | T6 | +7.5 | (question 5) | +8% | Sickle Range +1 (later), Green Thumb 25% (later) |
| Onion Harvest (P7) | T7 | +10 | (question 5) | +10% | Sickle Range +2 (later), Green Thumb 50% (later) |

Totals with the bonus (python3: pieces + bonus, then the 15 cap):

| Row | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
|---|---|---|---|---|---|---|---|
| Fortune, full set | 2 | 3 | 5 | 8 | 11 | 15 | 20 -> **15** |
| Chopping Speed, full set (Foraging) | 1 | 2 | 8 | 12 | 16 -> 12 at today's cap | - | - |

- **Tree Feller** (Skyy's "+treefeller on the higher tiers", `docs/answered/gear.md:65`): levels 1-4 as the Foraging draft's ladder moved onto
  F2-F5 (same table as the perk, 1 / 2 / 4 / 5 extra logs). Effective level = MAX of perk, axe and armor, one shared 3 s cooldown, Feller logs
  get Fortune at 50% and never re-trigger (`research/cloud/Gathering-Numbers-Reconciled.md` 1.3, F9). Needs SkyyTrees to read a `feller.armor`
  level from SkyyGear (the axe's version of this is not built either, `:72-74`). Until then the line is hidden.
- **Sickle Range** waits for the sickle range build (not in 0.2.12, `:74-75`); cap row `min(4, 1 + floor(Farming / 25))` unchanged.
- **Green Thumb** = a harvested crop is left one growth stage younger (UNVERIFIED engine hook, Crop draft 3).
- **Move speed** reuses the Speed line's live mechanism (SkyyAccessories Speed accessories) if SkyyGear can post to it; else hidden (UNVERIFIED).
- **T7 clip:** Onion Harvest reaches 20 and clips to 15, the same as Cotton (15). Its edge is move speed, Sickle Range 2 and Green Thumb 50%
  (question 3).
- Tooltip (Untiered-Mythic 3.1 format): `Set: Grove Bark (3/4) - +1 Foraging Fortune when all 4 are worn`, green (`#55FF55`, the live Set
  colour `SkyyGear/build_skyygear_0.2.13.py:1270`); the "(later)" lines are left out until live. The Stats page lists the active set bonus.

## 4. Recipes (Enchanted materials) and the cost check

### 4.1 The recipes

Cost rule (`docs/answered/bags.md:63`): a set costs **about its unlock threshold** in base material. Every armor unlocks at its key collection
tier **V** (the unlock grammar, `research/Gathering-Progression-Spec.md` 3.2: S curve V = 1,000; Oak is B curve, V = 1,000 too). At the
locked ratio 100 that is **10 Enchanted** = 1,000 base items. Piece split of 10 by 25 / 35 / 25 / 15 = 2.5 / 3.5 / 2.5 / 1.5 -> **Head 2 /
Chest 4 / Legs 3 / Hands 1**. Extras are cheap vanilla support items, never a second Enchanted kind (no previous-tier Enchanted: the collection
gate already stops skipping; question 2).

| Set | Unlock (collection tier V) | Enchanted per set (Head / Chest / Legs / Hands) | Extras per set (split the same way, rounded up on Chest) |
|---|---|---|---|
| Grove Bark (F1) | OakLog V | 10 `Skyy_Ench_Oak` (2 / 4 / 3 / 1) | 20 Plant Fiber |
| Autumn Bark (F2) | MapleLog V | 10 `Skyy_Ench_Maple` | 20 Plant Fiber |
| Savanna Bark (F3) | GumboabLog V | 10 `Skyy_Ench_Gumboab` | 20 Plant Fiber, 10 Tree Sap |
| Northern Bark (F4) | RedwoodLog V | 10 `Skyy_Ench_Redwood` | 20 Plant Fiber, 20 Tree Sap |
| Wastes Bark (F5) | SallowLog V | 10 `Skyy_Ench_Sallow` | 20 Plant Fiber, 30 Tree Sap |
| Wheat Harvest (P1) | Wheat V | 10 `Skyy_Ench_Wheat` | 20 Plant Fiber |
| Carrot Harvest (P2) | Carrot V | 10 `Skyy_Ench_Carrot` | 20 Plant Fiber |
| Cauliflower Harvest (P3) | Cauliflower V | 10 `Skyy_Ench_Cauliflower` | 20 Plant Fiber |
| Pumpkin Harvest (P4) | Pumpkin V | 10 `Skyy_Ench_Pumpkin` | 20 Plant Fiber, 4 cloth (Linen, UNVERIFIED id) |
| Chilli Harvest (P5) | Tomato V | 10 `Skyy_Ench_Tomato` | 20 Plant Fiber, 4 cloth (Cotton bolt, UNVERIFIED) |
| Cotton Harvest (P6) | Cotton V | 10 `Skyy_Ench_Cotton` | 20 Plant Fiber, 4 cloth (Cotton bolt, UNVERIFIED) |
| Onion Harvest (P7) | Potato V | 10 `Skyy_Ench_Potato` | 20 Plant Fiber, 4 cloth (Silk, UNVERIFIED) |

- Tree Sap = `Ingredient_Tree_Sap` (`docs/answered/economy.md:83`); Plant Fiber id, cloth ids and the bench: UNVERIFIED (read at build).
- Collections rows (SkyyCollections): append one `REC(<base id>)` token per piece on the key collection's tier V line (the live lines keep
  their bytes; `RW_ENTRIES` joins tokens, `research/Gathering-Progression-Spec.md` 3.2). Recipes `KnowledgeRequired: true`; no shop sells them
  (R3).
- **Dependency:** the 12 `Skyy_Ench_*` items are SkyyCollections / Sacks / Bazaar "phase A" (`research/Gathering-Progression-Spec.md` 4.1,
  6) - not built yet. Without them the armor rounds wait, or build with raw key items (100 per Enchanted; Chest = 400 logs) only if a probe
  shows a bench ingredient above one stack (100) works (UNVERIFIED, `research/cloud/Enchanted-Materials-Draft.md` 8.1).
- Salvage never returns Enchanted items; armor is never a Bazaar product (the live Bazaar refuses `Armor_*` ids - extend that assert to
  `Skyy_Look_*`).

### 4.2 Cost check vs Bazaar prices (python3)

Method: Enchanted mid price = 100 x base x 1.10 (the +10% Enchanted premium, `research/cloud/Chain-Premium-Fix.md` option A; the Block +4.5% step
is unused: no Blocks at launch). Instant buy = mid x 1.10, sell = mid x 0.90. Set bought = 10 Enchanted + extras at instant buy (Plant Fiber 1,
Tree Sap 12; cloth left out, price UNVERIFIED). "Raw value given up" = 1,000 base items sold raw at x 0.90.

| Set | Key base price | Enchanted mid / buy / sell | Set bought on the Bazaar | Raw value a gatherer gives up |
|---|---|---|---|---|
| F1 Grove | Oak 3 | 330 / 363 / 297 | 3,652 | 2,700 |
| F2 Autumn | Maple 8 | 880 / 968 / 792 | 9,702 | 7,200 |
| F3 Savanna | Gumboab 8 | 880 / 968 / 792 | 9,834 | 7,200 |
| F4 Northern | Redwood 20 | 2,200 / 2,420 / 1,980 | 24,486 | 18,000 |
| F5 Wastes | Sallow 8 | 880 / 968 / 792 | 10,098 | 7,200 |
| P1 Wheat | 2 | 220 / 242 / 198 | 2,442 | 1,800 |
| P2 Carrot | 2 | 220 / 242 / 198 | 2,442 | 1,800 |
| P3 Cauliflower | 6 | 660 / 726 / 594 | 7,282 | 5,400 |
| P4 Pumpkin | 6 | 660 / 726 / 594 | 7,282 + cloth | 5,400 |
| P5 Chilli (Tomato) | 16 | 1,760 / 1,936 / 1,584 | 19,382 + cloth | 14,400 |
| P6 Cotton | 16 | 1,760 / 1,936 / 1,584 | 19,382 + cloth | 14,400 |
| P7 Onion (Potato) | 40 | 4,400 / 4,840 / 3,960 | 48,422 + cloth | 36,000 |

- Loop check: buy 100 raw -> compress -> sell the Enchanted = 0.90 x 1.10 / 1.10 = **0.90** (a loss); armor cannot be sold on the Bazaar and
  salvage returns no Enchanted -> no exit. Crafting creates no coins.
- But **buying the materials does not skip the gate**: the recipe needs the player's own collection tier V (bought Enchanted never counts,
  `research/Gathering-Progression-Spec.md` 4.2).
- **Flag:** F5 (Sallow 8) costs less than F4 (Redwood 20), because the locked log prices do not follow zones (`research/Gathering-Progression-Spec.md`
  2.2 note). The 30 Tree Sap only adds 396 coins. Fine for a gathering set (the gate is the collection), but say so to Skyy (question 10).
- NPC sell-back of armor (if SkyyMerchants buys armor) must stay below the set's material sell value (UNVERIFIED: whether any NPC buys armor).

## 5. Compatibility with the Mining armor spec (written in parallel)

So `research/cloud/Mining-Armor-Spec.md` and this file give SkyyGear ONE set table:
- Same row table (T1-T7 = Copper..Onyxium), same bonus numbers (the locked 3.2 table), same Head 25 / Chest 35 / Legs 25 / Hands 15 split, same
  `armor.fortune.cap` 15 applied after the bonus, same mixed-tier rule (one set id).
- One set-table row per set: `set.<setId>=<family>,<row>,<display name>,<bonus Fortune>,<speed %>,<move %>,<special>` (format proposal; the
  local G1 build 0.2.14 defines the real one - adapt to it). Mining rows would be `mine_t1` ... with family `mining`.
- One bridge source for all worn gathering armor (`garmor`), keyed per skill (`dd.mining` / `dd.foraging` / `dd.farming`).
- If the Mining spec picks a different split, cap or row format, the Mining spec wins (it is built first) and this file follows.

## 6. Look swaps (change the look, keep the stats)

| Rule | Value |
|---|---|
| Family | one slot of one tier: `Resource_Skyy_Forage_F1_Chest` = { `Armor_Foraging_F1_Chest` (Oak), `Skyy_Look_..._Birch`, `_Beech`, `_Ash`, `_Aspen` } |
| Same stats | every member copies the base item's numbers + MaxDurability at build (build check: equal stats / durability per family) |
| What carries | rarity, level, modifiers, reforge, durability fraction (`research/Recolor-Plan.md` 1: the metadata document is cloned) |
| SkyyGear | `gear:base` map (look id -> base id) drives band, gate, stats, set id; a look id never re-rolls, never pays Smithing XP; `GearCraftSys` / `GearCraftPreSys` skip any `ArmoryAlteration` recipe (Recolor-Plan 2) |
| Where to swap | **SkyyWardrobe** (our own, `docs/answered/gear.md:120`, `:122`): Looks button, the whole stored set at once, **500 coins** per set change (`look.cost`); plus **The Armory's Alteration Table** when The Armory is ON (each look item carries a recipe: input = its family ResourceType x1, bench `ArmoryAlteration`, StructuralCrafting) - The Armory is OFF today (`tools/deploy_set.py:157` `PACK_DISABLED`, atlas overflow) |
| Until the Wardrobe ships | the look ids ship with the armor round (families from day one), but only the crafted look is obtainable; looks open with the Wardrobe |
| Never | a family across tiers or families; combat looks on gathering sets; per-tree recipes |
| Partial looks | a look a slot does not have is skipped ("Grove is now Birch (4 of 4 pieces)") |

Ship only approved art: held trees (Bottletree, Palo, Redwood, Spiral) and F5 join when Skyy approves them; Farming when Quirk's models land.
F4's crafted look is Redwood (held) - question 1.

## 7. SkyyGear build task text (ready to paste; one round per family)

> **SkyyGear 0.2.<next> - FORAGING ARMOR (Set label, tree looks).** Full round (new items in player hands, saved data via the item document,
> economy). Derive from the CURRENT SkyyGear SET pin with `tools/gear_0_2_<next>_patch.py`; build after the Mining armor round (same set
> table, same `garmor` source). Skyy's words: "lets still make the farming and gathering armor, but use vanilla for mining, and armory for
> combat gear." / "do a design per tree type in that set, so every hardwood gets its own design in that trees color" / "yes, gathering armor
> uses the set label, the full set gives a little bonus gathering fortune (mining foraging ect.) and the higher tiers can give a little more
> like mining /chopping speed, movement speed, ect." Spec: `research/cloud/Gathering-Armor-Stats.md` (sections 1-6).
> 1. ITEMS: base `Armor_Foraging_F<n>_<Head|Chest|Hands|Legs>` for every tier whose crafted look is approved (F1 Oak, F2 Maple, F3 Gumboab
>    now; F4 when Redwood v2 is approved; F5 later) + `Skyy_Look_<BaseId>_<Tree>` for every approved tree (F1 Birch, Beech, Ash, Aspen; F2
>    Azure; F3 Dry; F4 Fir, Cedar, Poisoned once F4 ships). Models / textures / icons from `art/gathering-armor/` (paths in its
>    `manifest.json`); item JSON generated by the build; base Health / MaxDurability = 50% / 100% of the same-slot vanilla metal piece of the
>    row (read from Assets.zip at build, nothing vanilla committed). Language lines "<Tree> Bark <piece word>".
> 2. FAMILIES: `Server/Item/ResourceTypes/Resource_Skyy_Forage_F<n>_<Piece>.json`; every member lists it; each look item gets the
>    `ArmoryAlteration` recipe (input = the family x1); build check: equal stats + MaxDurability per family. Publish `look:families` +
>    `look:base` on the bridge (Wardrobe-Spec 4.1). `gear:base` map: band / gate / stats / set id by base id (looked up BEFORE the id-word band
>    match). Skip `ArmoryAlteration` recipes in GearCraftSys + GearCraftPreSys.
> 3. LEVELS: bands F1 1-18, F2 15-23, F3 20-28, F4 25-38, F5 35-43 (explicit rows, never the id-word match); gate kind `foraging`; crafted
>    at the Foraging level clamped to the band; under-level = no gathering lines, no set bonus.
> 4. RARITY: always `set` (green); 3 modifier slots from a gathering pool WITHOUT Fortune (Foraging Wisdom, Health, Defense); Smithing craft
>    XP = the Normal craft XP (question 8).
> 5. STATS (per piece = set total x 25 / 35 / 25 / 15): Foraging Fortune 1 / 1.5 / 2.5 / 4 / 5.5; Foraging Wisdom F4 +2, F5 +4; Chopping
>    Speed 1 / 2 / 3 / 4 / 6 % hidden "(later)". Posted while worn as source `garmor` in `skill:bonus:<uuid>` (`dd.foraging` = Fortune / 100,
>    `xp.foraging` = Wisdom / 100), refreshed on equip change and at most every 1 s, removed on logout / `profile:busy` / shutdown.
> 6. SET: 4 pieces with the same set id -> + the locked row bonus (F1 +1, F2 +1.5, F3 +2.5, F4 +4, F5 +5.5 Foraging Fortune; F5 +5% move
>    speed if a move hook exists); speed and Tree Feller lines hidden "(later)"; clamp armor Fortune at `armor.fortune.cap` 15. Tooltip
>    `Set: Grove Bark (3/4) - +1 Foraging Fortune when all 4 are worn`.
> 7. RECIPES: section 4.1 (10 `Skyy_Ench_<KeyLog>` 2 / 4 / 3 / 1 + Plant Fiber + Tree Sap), bench + category read from the vanilla armor
>    bench (assert), `KnowledgeRequired`; SkyyCollections appends the REC tokens on <KeyLog> V (separate mod round, same SET). Needs the
>    Enchanted phase A items - STOP if `Skyy_Ench_Oak` is not in the SET.
> 8. SERVER SETUP (Gear -> Gathering armor, skyycfg, new keys only): `garmor.foraging.on`, band per tier, Fortune / Wisdom / speed per tier,
>    set bonus per tier, share split, `armor.fortune.cap` 15, `armor.wisdom.cap` 10, `armor.swing.cap`, `garmor.healthShare` 50.
> 9. HARNESS: every family equal stats; every base id resolves a band without the id-word match; a full mixed-look set counts as one set;
>    mixed tiers give no bonus; cap clamp; under-level gives nothing; no `Armor_Foraging_*` / `Skyy_Look_*` is a Bazaar product; salvage
>    output has no `Skyy_Ench_*`; the swap path keeps the item document byte-for-byte.
>
> **SkyyGear 0.2.<next> - FARMING ARMOR (crop sets).** Same round shape, when Quirk's crop models land. Items `Armor_Farming_P<n>_<Piece>`
> (P1 Wheat, P2 Carrot, P3 Cauliflower, P4 Pumpkin, P5 Chilli, P6 Cotton, P7 Onion looks) + `Skyy_Look_..._<OtherCrop>` (Lettuce, Corn,
> Turnip, Aubergine, Tomato, Rice, Potato) when drawn; families `Resource_Skyy_Farm_P<n>_<Piece>`; bands P1 1-18, P2 15-23, P3 20-28, P4
> 25-38, P5 35-43, P6 40-49, P7 40-49; gate `farming`; Farming Fortune 1 / 1.5 / 2.5 / 4 / 5.5 / 7.5 / 10, Farming Wisdom P4 +2 / P5 +4 / P6
> +6 / P7 +8 (`dd.farming`, `xp.farming`); set bonus +1 / +1.5 / +2.5 / +4 / +5.5 / +7.5 / +10 Farming Fortune, move speed P5 5 / P6 8 / P7
> 10 %; Sickle Range and Green Thumb hidden "(later)"; recipes section 4.1 (`Skyy_Ench_Tomato` for P5, `Skyy_Ench_Potato` for P7). Skyy's
> words: "but the farmer sets are going to be more like the wood ones. start with wheat armor, and work up through the food tiers making
> food armor, like in skyblock".

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | F4's crafted look is Redwood (the key log), and Redwood v2 is still held for a colour fix. Wait for it, or ship F4 with Fir as the crafted look? | [wait for Redwood v2; F1-F3 ship first] |
| 2 | Recipe size: the locked rule "cost about the unlock threshold" means 10 Enchanted (1,000 items) at ratio 100 - or keep the old literal 6 Enchanted (600)? And no previous-tier Enchanted in the recipe? | [10 Enchanted, no previous tier] |
| 3 | The top crop set (Onion, T7) reaches 20 Fortune and clips to the 15 cap, the same as Cotton. Keep the cap (Onion's edge = move speed, Sickle Range 2, Green Thumb 50%), or let a full set go to 20? | [keep cap 15] |
| 4 | P5 / P7: craft Chilli / Onion looks (as drawn) from Enchanted Tomato / Potato (the launch Enchanted list), with Tomato / Potato as swap looks later? | [yes] |
| 5 | Farming has no swing, so the set table's "harvest speed" means nothing. Give crop sets Sickle Range instead, or leave it empty? | [leave it; Sickle Range already on P4+] |
| 6 | Northern + Wastes chopping speed (pieces + set) is 12 / 16% but the armor swing cap is 12. Raise `armor.swing.cap` to 16 (the total stays under the +40% ceiling)? | [yes, 16] |
| 7 | Armor Fortune works while worn (hand-harvesting counts), not only with a hoe / sickle / hatchet held? | [while worn] |
| 8 | Set-rarity pieces roll 3 modifiers today: from a gathering pool WITHOUT Fortune (Wisdom, Health, Defense), and craft Smithing XP as a Normal piece (not Set's 4,000 base)? | [yes to both] |
| 9 | Vanilla Wood armor: stay plain vanilla, or give it a tiny Foraging Fortune (old tier 0)? | [plain vanilla] |
| 10 | F5 costs less than F4 on the Bazaar (Sallow 8 vs Redwood 20, locked log prices). Fine (the collection is the gate), or add more Tree Sap to F5? | [fine] |
| 11 | Set display names: "Grove Bark ... Wastes Bark" and "Wheat Harvest ... Onion Harvest"? | [yes] |

## For the local session (UNVERIFIED - needs Assets.zip / HytaleServer.jar / the game)

1. Vanilla armor bench id + its category list, and whether a "Gathering" category can be added (Workbench-tab style, `tools/skyywbtab.py`).
2. Vanilla metal piece Health / resist / MaxDurability per slot (Copper ... Onyxium) for the 50% base; vanilla piece words in the language file.
3. Plant Fiber, Linen / Cotton bolt / Silk item ids and their Bazaar prices (cloth left out of the cost check).
4. A bench recipe input above one stack (100), only needed if the armor round builds before the Enchanted items.
5. Our models on the player in game (`art/gathering-armor/README.md`: "NOT checked in game yet"), and the texture-atlas budget for ~160
   more armor textures + icons (The Armory was switched off for an atlas overflow, docs/log/2026-10.md 2026-10-09).
6. A live move-speed hook SkyyGear can post to (SkyyAccessories Speed line) - else the move-speed bonus stays hidden.
7. SkyyTrees reading an armor Tree Feller level (`feller.armor`), and a swing source for armor (Chopping Speed) - both "(later)".
8. Green Thumb (place a crop one stage younger) and Sickle Range hooks (Crop draft 3; sickle range build).
9. The 0.2.14 (rarity G1) set-table format: section 5's row proposal must be adapted to it; then merge with `research/cloud/Mining-Armor-Spec.md`.
10. Whether any NPC (SkyyMerchants) buys armor back, and at what price (section 4.2 last bullet).
