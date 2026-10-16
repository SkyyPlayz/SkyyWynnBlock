# Accessory Power: spec (paper only)

Where this sits: `INDEX.md` -> `research/`. Skyy's words: `docs/answered/gear.md` 2026-10-16 (ACCESSORY POWER, ACCESSORY BAG AS A
GRID + POWER, GATHERING STAT SOURCES, ACCESSORY CRAFTING LIVES IN THE ACCESSORY BAG). Answers to section 8 go into
`docs/answered/gear.md` (`python tools/qa_append.py gear ...`). Build: SkyyAccessories 0.5.22, after accraft (0.5.21). Older locks used:
`SkyyGear-Plan.md` locks 12, 14, 80-113 (read-only), `research/Booster-Accessories-Spec.md` 1.3, `research/Accessory-Pack-Inventory.md`
2.3-2.6 + G4, `research/Collections-Tools-Redesign-Spec.md` 6 + its 2026-10-16 note.

## 0. In plain words

- Every accessory in your bag adds **Accessory Power (AP)** by its rarity: Normal 10 up to Mythic 25. Only the best one of each line counts.
- You **pick one Power** on the Accessory Bag page. Your total AP makes that Power stronger. There are **9 Powers from the start**:
  5 combat (Tank, Balance, Slayer, Lucky, Magical) and 4 gathering (Mining, Foraging, Farming, Fishing).
- The curve is soft: **double your AP and the Power gets about 1.5x stronger.** Big bags still matter, but nothing explodes.
- Switching is free (a 5 second wait between switches). New players start on **Balance**.
- The BAG tab becomes an **icon grid like the pets page** (all 60 slots at once). Equip from the inventory and Unequip stay.
- Drop-only accessories that can be upgraded show up in CRAFT **only while one is in your bag**; never as a from-scratch recipe.

## 1. Accessory Power per accessory

| Rarity | Normal | Unique | Rare | Legendary | Fabled | Mythic |
|---|---|---|---|---|---|---|
| AP | 10 | 13 | 16 | 19 | 22 | 25 |

(The table already sits in the 0.5.20 build as `ACC_AP`, a constant nothing reads. It becomes live and editable, section 6.)

Counting rules:
- **Only the best rarity of each line counts** (the live `bestTiers` rule): a second copy or a lower rarity of the same line adds 0.
- A line switched off in Server Setup adds 0 AP. Retired accessories (Alchemy, Cooking bench) add 0. The Accessory Bag item adds 0.
- **Bench accessories give AP like any other line** (recommended, Q2): their rarity is set by bench tier (I Normal, II Unique, III Rare,
  IV+ Legendary). They are the cheap early AP that makes a day-one bag feel good.
- **The Omni** is made FROM the 11 active top-tier bench accessories, so it must not cost you AP: the Omni gives the **sum of what those
  11 would give at their top rarity = 143 AP** (Workbench, Armor, Weapon Rare 16 each; Farming Legendary 19; Furnace, Tannery Unique 13
  each; Arcane, Furniture, Loom, Salvage, Campfire Normal 10 each). A bench accessory in the bag next to the Omni adds 0 (no double dip).
  The number is worked out from the bench table at build time, so a new bench line moves it by itself.
- Accessories in the inventory (not in the bag) give nothing, as today.

Where a bag stands (today's lines: 10 boosters + Lantern + 11 benches / Omni; the bag holds 18 slots to start, up to 60):

| Point | What the bag looks like | AP |
|---|---|---|
| Early (first hours) | 4 bench accessories tier I + 2 Normal boosters | ~60 |
| Mid | 18 slots full, mostly Unique / Rare | ~250 |
| Late (everything that exists today, maxed) | 10 boosters + Lantern Legendary, Omni | ~350 |
| Future full bag (reference only) | 60 slots, gathering lines, drop and boss finds, some Fabled / Mythic | ~1,200 |

## 2. The 9 Powers

**Multiplier** `M = (AP / 100) ^ 0.6` (both numbers are Server Setup rows). AP 60 = 0.74, 250 = 1.73, 350 = 2.12, 1,200 = 4.44.
Each Power lists its stats **at 100 AP**; your value = that x M, rounded (combat stats whole numbers, because SkyyGear floors
`gear:extra`). Only stats with working code are used (Skyy's rule: never a stat that does nothing yet).

### 2.1 Combat (locks 80-87: every starter gets a little Health + Defense; Power mana is flat mana)

| Power | Per 100 AP | Feel |
|---|---|---|
| **Tank** | Health 12, Defense 6 | Health and Defense only (lock 81) |
| **Balance** (default) | Health 5, Defense 3, Strength 3, Crit Chance 1, Crit Damage 3, Mana 2, Speed 1% | a bit of everything (lock 82) |
| **Slayer** | Health 2, Defense 1, Strength 7, Crit Damage 10 | hits hard, softer body (lock 83) |
| **Lucky** | Health 4, Defense 2, Crit Chance 5, Crit Damage 3 | crits often (lock 84) |
| **Magical** | Health 4, Defense 1, Magical Power 7, Mana 4 | spells (locks 86, 104) |

**Fast** (lock 85, Speed + Attack Speed) waits: Attack Speed has no code yet. It joins as a 6th Power when Attack Speed is live (Q1).
Mana Regen on Magical also waits (no code). The Combat 15 forms (Fortress, Harmony, Glass Cannon, Blitz, Arcane, and the one named
"Fortune") are a later round (Q5).

### 2.2 Gathering (Skyy: gear + accessories + pets all add Breaking Power / Speed / Fortune)

Units as the tools use them: Breaking Power % (fewer hits), Breaking Speed % (faster swings), Fortune (100 = one extra drop).

| Power | Breaking Power % | Breaking Speed % | Fortune | Why |
|---|---|---|---|---|
| **Mining** | 14 | 9 | 6 | ores need Power |
| **Foraging** | 9 | 14 | 6 | logs need speed |
| **Farming** | 3 | 10 | 9 | crops break in one hit; Fortune and sweep speed matter |
| **Fishing** | Fishing Speed 8% | Double Catch 2% | Treasure Chance 1% | the rod's own three stats (Q6) |

Each gathering Power works only for its own skill (Mining Power never helps Foraging).

### 2.3 What that gives at three points (plus the future bag)

| Power | Early, 60 AP (x0.74) | Mid, 250 AP (x1.73) | Late, 350 AP (x2.12) | Future, 1,200 AP (x4.44) |
|---|---|---|---|---|
| Tank | +9 HP, +4 Def | +21 HP, +10 Def | +25 HP, +13 Def | +53 HP, +27 Def |
| Balance | +4 HP, +2 Def, +2 Str, +1 CC, +2 CD, +1 Mana, +0.7% Spd | +9 HP, +5 Def, +5 Str, +2 CC, +5 CD, +3 Mana, +1.7% | +11 HP, +6 Def, +6 Str, +2 CC, +6 CD, +4 Mana, +2.1% | +22 HP, +13 Def, +13 Str, +4 CC, +13 CD, +9 Mana, +4.4% |
| Slayer | +1 HP, +1 Def, +5 Str, +7 CD | +3, +2, +12 Str, +17 CD | +4, +2, +15 Str, +21 CD | +9, +4, +31 Str, +44 CD |
| Lucky | +3 HP, +1 Def, +4 CC, +2 CD | +7, +3, +9 CC, +5 CD | +8, +4, +11 CC, +6 CD | +18, +9, +22 CC, +13 CD |
| Magical | +3 HP, +1 Def, +5 MP, +3 Mana | +7, +2, +12 MP, +7 Mana | +8, +2, +15 MP, +8 Mana | +18, +4, +31 MP, +18 Mana |
| Mining | BP +10%, BS +7%, Fortune 4 | +24%, +16%, 10 | +30%, +19%, 13 | +62%, +40%, 27 |
| Foraging | BP +7%, BS +10%, Fortune 4 | +16%, +24%, 10 | +19%, +30%, 13 | +40%, +62%, 27 |
| Farming | BP +2%, BS +7%, Fortune 7 | +5%, +17%, 16 | +6%, +21%, 19 | +13%, +44%, 40 |
| Fishing | Speed +6%, Double +1.5%, Treasure +0.7% | +14%, +3.5%, +1.7% | +17%, +4.2%, +2.1% | +36%, +8.9%, +4.4% |

How it fits the scale:
- **Combat:** late Slayer (+15 Strength) is a bit more than one Legendary Brawler (+12) and about half of one best gear roll set (gear
  maximum per modifier: Strength 25, Crit Damage 30, Defense 25). Gear stays the main source; the bag is a real second one.
- **Gathering:** maxed gear gives about +150% Power / +100% Speed / +60% Fortune; the tool at ~level 40 about +200% / +120% / +80%.
  Late Mining Power is ~20% of the gear numbers, the future bag ~40%. With the planned one-per-stat gathering accessory lines (round A1,
  e.g. a Legendary Breaking Power line ~+20%) accessories come to roughly a third of gear - "essential too", not an extra. Pets add on
  top (round P1). The four power sources stack, nothing replaces another.
- **Fishing** stays under SkyyFishing's own caps (Fishing Speed 100%, Double Catch 20%, Treasure 15%): Power counts toward the same cap.

## 3. Picking the Power

- **Where:** the Accessory Bag page. A strip on top of the BAG tab: `Accessory Power 352 - Power: Slayer [Change]`. Change (or a
  third tab **POWER** next to BAG / CRAFT) shows 9 buttons in two rows - Combat: Tank, Balance, Slayer, Lucky, Magical; Gathering:
  Mining, Foraging, Farming, Fishing - each with **its stats at your AP right now** (the table in 2.3, live). Click = pick; the picked one
  is highlighted (kit selected-button style).
- **Switching:** free, any time, **5 s wait** between switches (stops click spam re-posting stats; Server Setup row). No coins, no NPC.
  You can switch to Mining before a mining trip and back to Slayer for a fight.
- **New players and old profiles:** Balance (`SkyyGear-Plan.md`: "The default profile is Balance"). Nothing to migrate: no saved Power =
  Balance.
- **Per profile** (`tools/PROFILES-CONTRACT.md`): saved in its own file `Skyy_SkyyAccessories/power/<pkey>.properties` (`power=Slayer`,
  `switched=<ms>`), so a rollback to 0.5.21 just ignores it. Never written while `profile:busy`.
- **Loadouts** (lock 12: a loadout saves the Power): bridge `acc:fn:power` (get / set) for SkyyWardrobe; Wardrobe adds it in its next
  lean round.
- `/accessories power [name]` shows / picks it from chat too (player sub-command, `hytale:Adventurer`).

## 4. How the boosts reach the stats

SkyyAccessories already runs one effect tick per player per second on the world thread (`AccEffects.tick`, `AccGear`). The Power is
added there - no new tick.

| Stat | Door (all on `skyy.bridge`, java.lang types only) | Reader | Status |
|---|---|---|---|
| Strength, Magical Power, Defense, Crit Chance, Crit Damage | `gear:extra:<uuid>` String `"cc:8,cd:16,def:12,mp:12,str:12"` - the Power's numbers are ADDED to the booster lines' numbers in the same text | SkyyGear (live, every hit) | works today |
| Health | the existing `skyyacc_health` MAX modifier: Vitality flat + Power Health | engine stat map | works today |
| Mana (flat) | `skyyacc_mana`: the Mana line's % is worked out first, then the Power's flat Mana is added (so % never multiplies the Power) | engine stat map | works today |
| Speed % | movement source `accessories.talismans`, pct layer (Speed line + Power) | MoveSync | works today |
| Fortune (Mining / Foraging / Farming) | `skill:bonus:<uuid>` source **`accessories`**, key `dd.<skill>` = Fortune / 100 | SkyySkills `Perks.chanceU` (capped by `perk.doubleDropMax` until T1 lifts it) | works today |
| Breaking Power | same source, NEW key `bp.<skill>` = % / 100 | SkyyGear hit count (T1, Redesign spec 6.2: `x (1 + BP)`) - sums `bp.*` of every source except its own `gear` | new reader |
| Breaking Speed | same source, NEW key `swing.<skill>` = % / 100 | SkyyTrees: added to `gear:swing` + its node % before picking the swing bucket (spec 6.3) | new reader |
| Fishing Speed / Double Catch / Treasure | same source, NEW keys `fspd.fishing`, `dd.fishing`, `treasure.fishing` (fractions) | SkyyFishing: added to the rig stats before the caps | new reader |

**G4 (`gear:extra` is ONE string per player): no fix needed for this round.** SkyyAccessories is still its only writer, and the Power
goes into the same text, so nothing overwrites anything. SkyyGear already merges pets as a separate map (`pets:stats:<uuid>`). The day a
second mod must write combat stats, SkyyGear gets a `gear:extra:<uuid>` map form (source -> String, like `skill:bonus`) - not now.

**Gathering uses `skill:bonus` for all three stats** because it is already a source -> map shape (many writers, no overwrite). The
`accessories` source is replaced whole each time it changes, removed when empty, on `profile:busy` and when the player leaves (the
same rules as the `gear` and `pets` sources). SkyyPets today puts `swing.*` into `pets:stats`; round P1 moves it to `skill:bonus` so
SkyyTrees reads one place.

**Show only what works:** each new reader puts `skill:bonus:reads:bp`, `...:swing`, `...:fish` = Boolean TRUE on the bridge when it
starts. The POWER buttons and tooltips list a gathering stat only while its reader is there (Skyy: "if its not in the game yet, dont
leave it in the list"). Fortune works today, so Mining / Foraging / Farming are pickable from day one; Fishing shows once SkyyFishing reads.

Also published: `acc:power:<uuid>` = String `"Slayer|352"` (Power | AP) for SkyyHud / SkyyMenu stats / Wardrobe. `/gear` already prints
accessory combat stats on its "From other mods" line.

## 5. The Bag page

### 5.1 BAG tab = icon grid (reuse the pets page)

Reuse the SkyyPets 0.4.0 grid exactly: `SUI.item_grid(...)` with tooltips + well, filled by `SUI.java_grid_fill` (kit `tools/skyyui.py`;
grid slots built as `new ItemStack(id, 1)` - never a stack with metadata, HANDOFF UI rule).

```
 ACCESSORY BAG    [BAG] [CRAFT] [POWER]
 Accessory Power 352 - Power: Slayer [Change]        18 / 60 slots
 [All] [Combat] [Gathering] [Benches]
 +-------------------------------------------------+
 | 12 x 5 icon grid = all 60 bag slots, one page    |   slots past the server limit stay empty / dark
 +-------------------------------------------------+
 Selected: Legendary Brawler Accessory  +19 AP  [Unequip]
 In your inventory (click = select):  12 x 1 icon grid + kit pager      [Equip]
```

- **Hover** an icon: name in rarity colour, the tier tag line, its effects, `+19 Accessory Power`, and "Does not count - a better one
  of this line is in your bag" when it is a lower copy; drop-only lines add "Drop only - upgrade it in Craft" or "Drop only - cannot be
  upgraded".
- **Click** = select (pets pattern: "Click a pet:" then the action). Unequip / Equip use the live code paths (counted moves, the
  `acc:fn:bag` rules, one line only once). Sorted rarest first, then line name (sort-by-tier rule); filters match the CRAFT sub tabs.
- The old 9-row list, its pager and the "Bonuses" well go; the bonuses move into the hover text and the POWER view.

### 5.2 CRAFT tab rule for drop-only accessories

Each line gets a flag in the booster table: `craft` (normal), `drop-up` (drop only, upgradable), `drop` (drop only, never upgraded).
- `craft`: as accraft 0.5.21 (next step only; Normal / T1 when you own none).
- `drop-up`: **no row until one of that line is IN THE BAG** (inventory copies do not count - Skyy: "when you have one equipped"); then
  the row shows the next rarity with its upgrade cost and UPGRADE. Never a from-scratch recipe.
- `drop`: never in CRAFT.
- Recommended start (Q4): Brawler, Runic, Stonehide, Razorfang and Feather = `drop-up` (their first rarity drops; upgrades in the bag);
  later boss / Fabled / Mythic finds = `drop`. Their drop sources come with the loot pass (Inventory G7) - until then admin give only.

## 6. Build rounds, Server Setup, tier tags

### 6.1 Rounds (in order)

| # | Round | Mods | Size | What |
|---|---|---|---|---|
| 1 | accraft (running) | Accessories 0.5.21 | - | craft in the bag (base for this) |
| 2 | T1 (queued) | Gear 0.3.15 + Skills 0.4.46 | full | **add the `bp.<skill>` reader** to T1's new hit formula + `skill:bonus:reads:bp` (small, same code T1 already rewrites) |
| 3 | **AP1** | **Accessories 0.5.22** + Trees 0.3.20 (swing reader) + Fishing 0.1.9 (fish reader) | **full** (saved data, several mods, combat stats) | AP sum, Omni rule, 9 Powers, POWER view, BAG grid, CRAFT drop rule, all doors in section 4, Server Setup rows |
| 4 | lean | Wardrobe | lean | loadout saves the Power (`acc:fn:power`) |
| 5 | P1 / A1 | Pets, Accessories | per its spec | pets `swing.*` to `skill:bonus`; one-per-stat gathering accessory lines |

If T1 slips, AP1 can still ship: the gathering Powers then show Fortune only (section 4, "show only what works").
Harness checks for AP1: the AP sum with duplicates / lower copies / Omni + benches; M at 0, 60, 350, 1,200 AP; the `gear:extra` text equals
lines + Power; `skill:bonus` source removed on leave / busy / empty; the 5 s switch wait; a rollback to 0.5.21 leaves the bag files as
they were.

### 6.2 Server Setup rows (Server Setup > Accessories > Accessory Power; kit `tools/skyycfg.py`, `tools/CONFIG-CONTRACT.md`)

| Row | Default | Notes |
|---|---|---|
| Accessory Power on | on | off = no Power stats (AP still shown) |
| AP per rarity (Normal .. Mythic) | 10 / 13 / 16 / 19 / 22 / 25 | table row, 0-100 each |
| Bench accessories give AP | full | full / half / none |
| Power curve: AP for x1 / curve exponent | 100 / 0.6 | 1-1000 / 0.1-1.0 |
| Power multiplier guard | 20 | the most M can reach (a sanity cap) |
| Wait between Power switches | 5 s | 0-3600 s |
| Starting Power | Balance | one of the 9 |
| Powers (table: Power, stat, value per 100 AP, on/off) | section 2 | every number editable; off = the Power is hidden |

Readers: SkyyGear "Breaking Power from other mods" (on), SkyyTrees "Swing speed from other mods" (on), SkyyFishing "Fishing stats from
other mods" (on). Times in seconds.

### 6.3 Tier tags

No new tiered items in AP1. Tooltips keep their tag first (`T3 Talisman - ...`, `T2 Bench - ...`, own ladders in `tools/tier_tags.py`),
then the effects, then the new `+16 Accessory Power` line. The A1 gathering lines add their ids to `tools/tier_tags.py` when built.

## 7. Later (not in AP1)

Combat 15 Powers, tuning points (Hypixel: 1 per 10 AP), enrichments, Recombobulator-style rarity raises, Power stones, Fast (needs
Attack Speed), Mana Regen on Magical, a `gear:extra` map form (only when a second writer appears).

## 8. Questions for Skyy (default in [brackets])

1. **Which 5 combat Powers?** Fast needs Attack Speed, which does not work yet. [Tank, Balance, Slayer, Lucky, Magical now; Fast joins
   as the 6th when Attack Speed works]
2. **Do bench accessories give Accessory Power?** [Yes, by rarity like the rest; the Omni gives what the 11 benches it eats would give
   (143), and bench accessories next to it give 0]
3. **Switching Powers:** [free, any time from the bag page, 5 s wait between switches]
4. **Drop-only lines:** [Brawler, Runic, Stonehide, Razorfang, Feather drop at their first rarity and upgrade in the bag; later boss /
   Mythic finds cannot be upgraded]
5. **Combat 15 Powers** (Fortress, Harmony, Glass Cannon, Blitz, Arcane, "Fortune") - when, and the name clash with gathering Fortune?
   [a later round, unlocked at Combat 15; rename the combat "Fortune" Power to "Jackpot"]
6. **Fishing Power stats:** [Fishing Speed, Double Catch, Treasure Chance, inside the rod's own caps]
