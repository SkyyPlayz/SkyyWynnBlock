# Booster accessories: spec

*Design, 2026-09-30, revised the same day after the design review and the feasibility review (see "Review notes" at the end).
Written for Skyy's request of 2026-09-30: booster accessories (+Strength, +% movement speed, +Stamina, +Health, +Mana and more) that
start basic and upgrade, Hypixel style, with many of them coming from mob drops and world loot chests later. Nothing was built,
committed or deployed. **Every number is a PLACEHOLDER** that Skyy can change in game (Server Setup). Inputs:
`research/Hypixel-Accessories-Research.md`, `research/Accessory-Pack-Inventory.md` (called "the inventory" below),
`SkyyAccessories-Plan.md`, `SkyyGear-Plan.md`, `SkyyGear-Stat-Catalog.md`, `OPEN-QUESTIONS.md`, `HANDOFF.md`, and the live build scripts.
Where a LOCKED line disagrees with this file, the lock wins. Section 8 lists every clash and how this file handles it.*

Tags: **VERIFIED** = read in a live build script or in Assets.zip on this PC. **INFERRED** = strongly implied, not proven.
**UNVERIFIED** = needs a test in the game.

---

## 0. In plain words

1. Four of Skyy's five boosters already exist as talismans: Health, Stamina, Mana and Speed (their internal keys are Vitality,
   Endurance, Intelligence and Speed). They are crafted at a Workbench today. This plan turns the 25 talismans into the first five
   **booster lines** (same items, same recipes, new names, new numbers) and adds **Strength** plus four more lines whose effects already
   work in the game.
2. **First build = 10 lines** in SkyyAccessories 0.5: Health, Stamina, Mana, Regeneration, Speed (the old talismans), Brawler
   (Strength), Runic (Magical Power), Stonehide (Defense), Razorfang (Crit Chance and Crit Damage together) and Feather (less fall
   damage, higher jumps).
3. Every line climbs tiers. At each step the **tier word** in the name (Charm, Band, Sigil, Emblem, Crest), the **rarity colour** and
   the number all go up. **Only your best item of a line counts.** Copies never stack. Different lines stack.
4. Rarities move to Skyy's **Wynn ladder** (Normal, Unique, Rare, Legendary, Fabled, Mythic), the same ladder as gear and Magic Bags.
5. Only stats that really work today are used. Stamina Regen, Attack Speed, Mana Regen, Mining Speed, oxygen, swim speed, coins and loot
   stats wait for later (section 4).
6. How you get them stays a placeholder: each tier carries source words (Craft, Drop, Chest, Combine, Boss) for the later loot pass.
   The old talisman recipes keep working, and the old lines also get Drop, Chest and Boss words so the loot pass has hooks. The new
   lines come only from an admin give command until the drop tables are built.
7. The bag grows past 9 slots (default 18, up to 60, with pages). 18 is a deliberate squeeze: the Omni plus all 10 lines fit, but
   11 bench accessories plus 10 lines (21) do not.
8. **On deploy, existing talismans change strength:** Health, Stamina and Mana get stronger (1.25x to 10x, depending on your pool),
   Speed stays the same, Regeneration gets weaker (about a third). See 1.6, Q5 and Q10.

---

## 1. Rules for every booster

### 1.1 What a booster is

- An accessory item that works only while it sits in the Accessory Bag (today's rule). Fixed numbers: no roll, no identify, no reforge.
  SkyyGear never treats these ids as gear (VERIFIED, inventory 3.1).
- A **line** (family) is one theme. Most lines have one main stat. Feather (fall damage and jump) and Razorfang (Crit Chance and Crit
  Damage, see 1.5) have two.
- Each item of a line is a **tier**. **Only the highest tier of a line counts**, for its stats and its Accessory Power. Equipping a
  higher tier swaps it in and hands the lower one back; an equal or lower tier is refused. This is already how the bag works
  (`AccDefs.groupOf` and `equipK`, VERIFIED), and a duplicate that slips in through `stashK` is harmless because `bestTiers` takes the
  maximum. So no stacking bug can appear later.
- **First build: one line per stat.** No two lines share a main stat, so Skyy's "only ONE accessory per kind/family counts (no stacking
  6 speed rings)" and "one per line" mean the same thing today. When later lines share a stat, Skyy picks the reading (Q8).
- No level requirement: accessories are not gear items (Q14).

### 1.2 Tiers, names and rarity

**Tier words, by position in the line:** T1 **Charm**, T2 **Band**, T3 **Sigil**, T4 **Emblem**, T5 **Crest**. The word always means
the step, never the rarity: Emblem is always the 4th item of its line (Legendary on the backbone lines and Feather, Fabled on the drop
lines), and Crest exists only on 5-tier lines. The colour tells you the rarity. Examples: "Health Charm" (Normal) up to "Health Crest"
(Fabled); "Brawler Charm" (Unique) up to "Brawler Emblem" (Fabled).

- None of these five is a Hypixel tier word (Hypixel's ladder is Talisman, Ring, Artifact, Relic, then Heirloom). Charm and Crest do
  appear inside a few one-off Hypixel item names; they are plain English words, not a copied ladder. An earlier draft used Relic and
  Heirloom, which are Hypixel's own ladder words, and Skyy has scrapped copy-paste Hypixel names before (locks 79 and 100). Q1 offers
  them only as the Hypixel-style fallback.
- This brings back tier words, which the 2026-09-23 layer note had replaced with rarity names, so it needs Skyy's yes (Q1).

| Line shape | Tiers | Rarities | Lines | Why |
|---|---|---|---|---|
| Backbone | 5 | Normal, Unique, Rare, Legendary, Fabled | Health, Stamina, Mana, Regeneration, Speed | these are the 25 talismans (5 rarities each), so nobody loses a tier |
| Drop line | 4 | Unique, Rare, Legendary, Fabled | Brawler, Runic, Stonehide, Razorfang | mob and chest finds start one step up (Hypixel starts a line at the rarity of its source) |
| Comfort line | 4 | Normal, Unique, Rare, Legendary | Feather | a cheap early helper that tops out lower |

- On booster lines, **Mythic** is kept free for later boss-only top tiers. (The crafted Omni becomes Mythic, like the Mythic Omni Bag;
  it is a bench accessory, not a booster line. SkyyGear makes no crafted Mythic gear, `craft.maxRarity` fabled.)
- **Set** is a gear-only rarity. No booster uses it.

### 1.3 Accessory Power (a build constant, not shown yet)

Locked: each accessory adds a flat +10 to +25 Accessory Power by rarity; the exact table is not set (SkyyGear-Plan locks 111-113).
Proposal, a placeholder that stays inside the locked range:

| Normal | Unique | Rare | Legendary | Fabled | Mythic |
|---|---|---|---|---|---|
| 10 | 13 | 16 | 19 | 22 | 25 |

- Each step is +3, so it is easy to guess. The top (Mythic, 25) is 2.5 times the bottom, as the lock implies. The old 3/5/8/12/16 draft
  in `SkyyAccessories-Plan.md` is obsolete.
- **No Accessory Power code exists yet** (inventory G6). In 0.5 the table is a **build constant** and a field in `acc:defs` (5.9). It
  is **not** a Server Setup row and not on any tooltip or page: Skyy's 2026-09-30 rule "if its not in the game yet, dont leave it in the
  list" rules out a setting or a number that does nothing (Q9).
- **The Omni double dip.** The Omni counts as every bench accessory at max tier, and the bag still lets bench accessories sit next to
  it (`groupOf` gives the Omni its own group). Rule for the future Accessory Power code: **while the Omni is in the bag, bench
  accessories add 0 Accessory Power** (the Omni already stands for all of them). Decide before any Accessory Power code (Q9).
- The Accessory Bag item itself adds no Accessory Power.

### 1.4 Allowed stats (they work today)

| Stat | Where it is applied | Status (inventory section 2) |
|---|---|---|
| Max Health (flat) | engine stat map, key `skyyacc_health` | LIVE (the Health talismans use it) |
| Max Stamina (flat) | engine stat map, key `skyyacc_stamina` | LIVE (the Stamina talismans use it) |
| Max Mana (% of your Mana, with a small flat floor, Q6) | engine stat map, key `skyyacc_mana` | LIVE (the Mana talismans use it) |
| Health healed every 2 s (% of max) | `addStatValue` timer | LIVE (Regeneration uses it) |
| Movement speed % | movement protocol, source `accessories.talismans`, % layer | LIVE (Speed uses it) |
| Jump height %, fall damage % | same movement source, fields `jump` and `fallDamage` | LIVE-READY (no accessory sends them yet) |
| Strength, Magical Power, Defense, Crit Chance, Crit Damage | SkyyGear, bridge `gear:extra:<uuid>` keys `str mp def cc cd` | LIVE-READY (nobody publishes it yet) |
| Life Steal; Wisdom and Fortune for Mining, Foraging, Farming | `gear:extra` key `lsteal`; `skill:bonus:<uuid>` keys `xp.<skill>`, `dd.<skill>` | LIVE-READY (wave 2, section 3) |

- **Combat stats on accessories.** SkyyGear 0.1's own slot table puts Defense on armor only and crits on weapons and armor only, and
  lock 125 keeps combat modifiers on combat gear. This file reads those as **gear** rules: accessories are not gear. Strength (catalog
  row) and Magical Power (lock 103) name accessories outright; lock 66 keeps Defense, Crit Chance, Crit Damage, Strength, Health and
  Speed as accessory enrichments, and lock 75 applies the same rulings to accessories. Section 8 lists this; Q11 asks Skyy to confirm.

**Kept out on purpose** (a build check fails if a booster uses one):

- Damage % (`dmg`): weapon only (lock 15). Flat element damage (`fEarth` and the rest): weapon only (lock 17). True Damage (`tdmg`):
  its placement is not set.
- `spd` through `gear:extra`: it would land in the flat layer next to armor. Speed uses the accessory % layer instead (Q4).
- Stamina Regen (`stam`): armor only unless Skyy says otherwise (lock 27, Q3).
- Every key SkyyGear marks "later" (Attack Speed, Ferocity, Thorns, Mana Regen and the rest). SkyyGear accepts them and silently does
  nothing, so a booster using one would lie (inventory 2.3 "Trap").

### 1.5 How the numbers were balanced

**Yardstick:** no tier should make gear pointless. A top-tier booster should be worth roughly half of the best single gear roll of the
same stat, and well under a full set of rolled gear.

- **Combat lines.** Tier values are about 12%, 24%, 36% and 48% of the SkyyGear full-power maximum for one modifier of that stat
  (Strength 25, Magical Power 25, Defense 25, Crit Chance 15, Crit Damage 30), rounded to an easy ramp: Strength, Magical Power and
  Defense +3/+6/+9/+12, Crit Chance +2/+4/+6/+8, Crit Damage +4/+8/+12/+16. So the top tier (Fabled) is:
  - about half of the best single gear roll;
  - at level 15 (Iron) a Legendary gear roll of Strength is 5.3 to 11.3 (45-95% of 25 at SkyyGear's 47.5% level factor), so Brawler
    +12 sits slightly above the best roll there; at level 20 (Thorium, 55%) the roll is 6.2 to 13.1 (SkyyGear levels: OPEN-QUESTIONS
    2026-09-30 lock; level factor `25 + 75 x level / 50`, VERIFIED in `GearLevel.factor`);
  - well under what a full set of rolled gear gives. The bag stays a real slice of power, but gear stays the main source.
- **What the top tier is worth alone** (no other gear, SkyyGear 0.1 formulas, VERIFIED: base Crit Chance 0, a crit is x2 x (1 + Crit
  Damage)):
  - Brawler +12 Strength = +12% damage on melee, arrows, thrown weapons and staff melee;
  - Runic +12 Magical Power = +12% on spell shots;
  - Stonehide +12 Defense = hits x 100/112, about 11% less damage taken;
  - Razorfang +8% Crit Chance and +16% Crit Damage = 1 + 0.08 x (2 x 1.16 - 1) = about +10.6% average damage.
- **Why the crits are one line.** Crit Damage alone does nothing without Crit Chance, and base Crit Chance is 0. As separate lines, a
  Crit Damage Emblem (+16) on top of a Crit Chance Emblem (+8%) added only about 2.6 points, and nothing at all on its own, so a
  Fabled boss drop would have been a trap. Paired, the line is worth about the same as Brawler for one slot. Q12 asks whether Skyy
  wants them split back into two lines.
- **Health, flat +5 per tier.** One skill-tree Health node gives +10 to +20 at max, and Overall Level 100 gives +50. The top tier
  (+25) is about 12% of a level-100 pool (about 200 Health).
- **Stamina, flat +2 to +6.** +2 is a fifth more stamina for a new player (10). +6 is about 17% of a level-100 pool (about 35), less
  than the Acrobatics stamina nodes (+8).
- **Mana, +5% to +25% of your Mana, never less than +1/+2/+3/+4/+5** (the floor). Lock 88 says dedicated mana accessories use % mana.
  But pools are tiny: a new player has 10 Mana and a Mage without armor 20, so 5% is +0.5 or +1, and even the top tier is only +2.5 or
  +5 while a wand cast costs 25. Stamina is flat for exactly this small-pool reason, and research pattern 14 says every accessory should
  do something you notice. The floor keeps the % rule and makes the line felt from T1; it matters only while pools are small (from 20
  Mana up, the % part is at least the floor at every tier). With a cloth armor set (60 to 100 Mana) the top tier gives +15 to +25, about one wand
  cast. The floor bends lock 88, so it needs Skyy's yes (Q6); setting the floor row to 0 gives "% only".
- **Speed, 2/4/6/8/10% (today's numbers, unchanged).** At Acrobatics 100 (x2.0) the top tier gives x2.20. That is +0.20 against +0.05
  for the best gear Speed roll (flat layer), so 4x the gear roll at Acrobatics 100 and 2x at Acrobatics 0, because the accessory %
  layer multiplies with Acrobatics. This breaks the half-of-gear yardstick; it is kept because it is the live talisman's shape and
  Skyy asked for "+% movement speed". Q4 offers the flat layer (top tier +0.10, 2x the gear roll at any Acrobatics level).
- **Regeneration, 0.2/0.4/0.6/0.8/1.0% of max Health every 2 s (lowered from 0.5/1/1.5/2/3).** Lock 20: Hytale has no natural regen,
  food and potions are the soft gate, and SkyBlock's "faster natural regen" stat is scrap. The best single gear Raw Health Regen roll
  is 2 per 2 s (2.4 with the Health Regen % line, VERIFIED in `build_skyygear_0.1.py`). Today's top talisman heals 3 per 2 s at 100
  Health and 6 at 200, in combat too, which beats the best gear roll by 1.25x to 2.5x. The new top tier heals 1 at 100 Health and 2 at
  200 (about 40% to 85% of the best gear roll), and stays under it up to about 240 Health. T1 heals 6 Health a minute at 100 Health:
  small, but visible in a game with no natural regen. Q10 offers the alternatives.
- **Feather:** Acrobatics 100 already gives -50% fall damage. The top Feather tier (-40%) brings that to x0.3 (flat and % layers
  multiply, VERIFIED in `tools/skyymove.py`). Jump +5% per tier (+20% at T4) is at most a fifth higher, far below the protocol's clamp
  (default + 20 blocks). The fall part needs SkyySkills; the jump part works without it (2.4).
- **Against Hypixel.** The ramps are as easy to guess (+3 per step, +2 per step), but each SkyWynn item is worth more, because a
  SkyWynn bag holds 18 to 60 items (not over 100) and each stat has one line.

### 1.6 Existing talismans: before and after (what changes on deploy)

Old = SkyyAccessories 0.4.5 (Common to Legendary, % of your pool). New = the 0.5 defaults (T1 to T5).

| Line | Pool | Old T1 ... T5 | New T1 ... T5 | Change |
|---|---|---|---|---|
| Health | 100 (new player) | +2, +4, +6, +8, +10 | +5, +10, +15, +20, +25 | 2.5x at every tier |
| Health | 200 (level 100) | +4, +8, +12, +16, +20 | same | 1.25x |
| Stamina | 10 (new player) | +0.2, +0.4, +0.6, +0.8, +1.0 | +2, +3, +4, +5, +6 | 10x at T1, 6x at T5 |
| Stamina | 35 (level 100) | +0.7, +1.4, +2.1, +2.8, +3.5 | same | 2.9x at T1, 1.7x at T5 |
| Mana | 10 (new player) | +0.2 ... +1.0 | +1 ... +5 (the floor) | 5x |
| Mana | 20 (Mage, no armor) | +0.4 ... +2.0 | +1 ... +5 | 2.5x |
| Mana | 100 (cloth armor) | +2 ... +10 | +5 ... +25 | 2.5x |
| Regeneration | any | 0.5, 1, 1.5, 2, 3% per 2 s | 0.2, 0.4, 0.6, 0.8, 1.0% | about 0.33x to 0.4x (weaker) |
| Speed | any | +2, +4, +6, +8, +10% | same | unchanged |

So **every Health, Stamina and Mana talisman gets stronger on deploy**, Speed stays, and Regeneration gets weaker. Skyy can accept the
jump or pick a gentler ramp (Q5), and keep or lower Regeneration (Q10). All numbers are one Server Setup row each.

---

## 2. First-build lines (SkyyAccessories 0.5)

### 2.1 Overview

| # | Family key (item ids) | Admin name (config, commands) | Line name (players see) | Main stat | Feed | Tiers | Status |
|---|---|---|---|---|---|---|---|
| 1 | Vitality | Health | Health | +max Health, flat | stat map `skyyacc_health` | 5 | FOLD (was % of Health) |
| 2 | Endurance | Stamina | Stamina | +max Stamina, flat | stat map `skyyacc_stamina` | 5 | FOLD (was % of Stamina) |
| 3 | Intelligence | Mana | Mana | +% max Mana, with a flat floor | stat map `skyyacc_mana` | 5 | FOLD (bigger numbers) |
| 4 | Regeneration | Regeneration | Regeneration | % of max Health healed every 2 s | `addStatValue` | 5 | FOLD (lower numbers) |
| 5 | Speed | Speed | Speed | +% movement speed | move, % layer | 5 | FOLD (unchanged) |
| 6 | Strength | Strength | Brawler | +Strength (melee, arrows, thrown weapons, staff melee) | `gear:extra` `str` | 4 | NEW |
| 7 | MagicPower | MagicPower | Runic | +Magical Power (spell shots only) | `gear:extra` `mp` | 4 | NEW |
| 8 | Defense | Defense | Stonehide | +Defense | `gear:extra` `def` | 4 | NEW |
| 9 | Crit | Crit | Razorfang | +Crit Chance % and +Crit Damage % | `gear:extra` `cc`, `cd` | 4 | NEW |
| 10 | Feather | Feather | Feather | less fall damage, higher jump | move, `fallDamage` + `jump` | 4 | NEW |

- **Three kinds of name.** The *family key* lives only in item ids, so no item id changes. The *admin name* is the stat word, used in
  config keys, `/accessories` commands and `acc:defs`; it never changes, even if a line is renamed. The *line name* is what players
  see; it lives only in the language file, so renaming is cheap (Q14).
- Vitality, Endurance and Intelligence never appear in player or admin text, which takes two scrapped stat names out of the game:
  "Vitality is scrap" (lock 20) and "No Intelligence ID" (lock 67). The commands still accept them as aliases (5.9).
- The drop-line names do not say the stat, so the **first tooltip line always names the stat** (5.7). Brawler is not melee-only: it
  also boosts arrows, thrown weapons and staff melee, and its tooltip says so. The names Hawkeye and Bulwark were dropped because the
  draft crystal table in `SkyyAccessories-Plan.md` section 2 uses them for the Archer and Warrior crystals.

### 2.2 Backbone lines (the 25 talismans, folded)

| Tier | Word | Rarity | AP | Source words | Health | Stamina | Mana (floor) | Regeneration | Speed |
|---|---|---|---|---|---|---|---|---|---|
| T1 | Charm | Normal | 10 | Craft | +5 | +2 | +5% (at least +1) | 0.2% / 2 s | +2% |
| T2 | Band | Unique | 13 | Craft, Drop | +10 | +3 | +10% (at least +2) | 0.4% / 2 s | +4% |
| T3 | Sigil | Rare | 16 | Craft, Chest | +15 | +4 | +15% (at least +3) | 0.6% / 2 s | +6% |
| T4 | Emblem | Legendary | 19 | Craft, Chest | +20 | +5 | +20% (at least +4) | 0.8% / 2 s | +8% |
| T5 | Crest | Fabled | 22 | Craft, Boss | +25 | +6 | +25% (at least +5) | 1.0% / 2 s | +10% |

- Ids stay exactly as they are: `Skyy_Talisman_<Key>_<Common|Uncommon|Rare|Epic|Legendary>` = T1 to T5 (for example
  `Skyy_Talisman_Vitality_Epic` is the Health Emblem, Legendary). The 15 older 0.2/0.3 ids (`_Talisman`, `_Ring`, `_Artifact`) keep
  counting as T2, T3 and T4 and still turn into the modern id when they pass through the bag (today's `modernOf`, VERIFIED).
- "Craft" = today's Workbench ladder (previous tier + materials), unchanged; every tier keeps its recipe. Drop, Chest and Boss are
  **extra** placeholder sources, so the later loot pass has hooks for Skyy's four named boosters too (Skyy: "many will be mob drops, and
  found in the random loot chests"). Collection-gated craft tiers (lock 64) are not wired in 0.5 (section 8).
- Mana is "% of your Mana": the percent of every other flat Mana source (base Mana, Overall Level, skills, trees, armor), as today, but
  never less than the floor.

### 2.3 Drop lines (new)

| Tier | Word | Rarity | AP | Brawler (Strength) | Runic (Magical Power) | Stonehide (Defense) | Razorfang (Crit Chance + Crit Damage) |
|---|---|---|---|---|---|---|---|
| T1 | Charm | Unique | 13 | +3 | +3 | +3 | +2% and +4% |
| T2 | Band | Rare | 16 | +6 | +6 | +6 | +4% and +8% |
| T3 | Sigil | Legendary | 19 | +9 | +9 | +9 | +6% and +12% |
| T4 | Emblem | Fabled | 22 | +12 | +12 | +12 | +8% and +16% |
| Source words per tier | | | | Drop, Combine, Craft, Boss | Chest, Combine, Craft, Boss | Drop, Combine, Craft, Boss | Chest, Combine, Craft, Boss |
| Top tier alone (1.5) | | | | +12% damage | +12% spell damage | about 11% less damage taken | about +10.6% average damage |

- Ids: `Skyy_Talisman_<Key>_T1` to `_T4` (section 5.3), for example `Skyy_Talisman_Strength_T3` is the Brawler Sigil and
  `Skyy_Talisman_Crit_T4` the Razorfang Emblem.
- What the stats do in SkyyGear 0.1 (VERIFIED, inventory 2.3): 1 Strength = +1% damage on melee, arrows, thrown weapons and staff melee;
  1 Magical Power = +1% on spell shots (wand, staff, spellbook); Defense cuts hits to `100 / (100 + Defense)`; nobody crits without gear
  or accessories (base Crit Chance is 0), a crit is x2 and Crit Damage raises that (+100 = x4); over 100% Crit Chance is overcrit.
- Offence stats only count with a gear weapon or bare hands (a held tool or block gives none), and never with a weapon above your level.
  Defense only counts against hits from a mob or player. SkyyGear's Server Setup switch "Gear stats in combat" (`part.stats`) must be
  on; the bag page says so when it is off (5.4).
- Source words (placeholders, for the later pass): **Drop** = a normal mob drop; **Chest** = a world loot chest; **Combine** = 4 copies
  of the tier below (turns duplicate drops into progress, Hypixel's Master Skull and Scarf's pattern); **Craft** = the tier below plus a
  drop from a harder mob; **Boss** = a boss drop.

### 2.4 Feather (new comfort line)

| Tier | Word | Rarity | AP | Fall damage | Jump height | Source words |
|---|---|---|---|---|---|---|
| T1 | Charm | Normal | 10 | -10% | +5% | Craft |
| T2 | Band | Unique | 13 | -20% | +10% | Craft |
| T3 | Sigil | Rare | 16 | -30% | +15% | Chest |
| T4 | Emblem | Legendary | 19 | -40% | +20% | Chest |

- Ids `Skyy_Talisman_Feather_T1` to `_T4`. Jump Height on accessories is allowed (lock 28). Hypixel has no jump accessory, so this one
  is a SkyWynn original.
- **Needs SkyySkills for the fall part.** Fall damage is applied only by SkyySkills (it owns `stat:owner:fallDamage`, VERIFIED).
  Without SkyySkills the fall part does nothing; the jump part still works, because SkyyAccessories writes jump through the movement
  protocol itself. The tooltip and the bag page say "fall damage needs SkyySkills" when it is missing, like the combat lines.
- Every tier now has a jump part, so T1 and T2 do something you notice even with a small fall bonus.
- INFERRED: the Acrobatics double jump uses the live `MovementSettings.jumpForce`, so Feather probably lifts the double jump by the same
  percent. Test step 6.

---

## 3. Wave 2 (the same engine, no new engine work; build right after 0.5 tests pass)

| Family key | Line name | Stats per tier | Tiers and rarity | Feed |
|---|---|---|---|---|
| Mining | Prospector | Mining Wisdom +3/+6/+9/+12% XP; Mining Fortune (double drops) T3 +3%, T4 +6% | 4, Normal to Legendary | `skill:bonus` `xp.mining`, `dd.mining` |
| Foraging | Woodsman | same numbers for Foraging (Fortune doubles logs only) | 4, Normal to Legendary | `xp.foraging`, `dd.foraging` |
| Farming | Harvester | same numbers for Farming | 4, Normal to Legendary | `xp.farming`, `dd.farming` |
| LifeSteal | Leech | **waits for Skyy's Life Steal shape**: the numbers are open and must not be invented (SkyyGear-Plan open item 9, catalog row) | 3, Rare to Fabled | `gear:extra` `lsteal` |

- Wisdom is sent as a fraction under one source name, `accessories.boosters` (0.03 = +3%). SkyySkills clamps the sum (XP 0 to 5,
  double drops 0 to 1, VERIFIED); `skill:bonus` is a per-source map, as SkyyTrees uses it with source `trees`.
- Before building, check the Fortune numbers against the skills' own double-drop perk (cap `perk.doubleDropMax` 1.0).
- Leech gets its numbers once Skyy sets the Life Steal shape; when it does, keep its top tier within the 48%-of-gear-max rule (1.5).
- Cooking Wisdom works the same way if Skyy wants a cooking line.

---

## 4. Later (needs new engine work, a missing system, or a Skyy call)

| Idea | Why it waits | What it needs |
|---|---|---|
| Mana Regen line | not wired (LATER). Vanilla already refills about 5 Mana a second, so a small trickle adds little while pools are 10 to 60 | the Regeneration timer pointed at Mana; worth it once pools or spell costs grow |
| Stamina Regen line | locked armor only (lock 27) | Skyy's say-so (Q3), then `gear:extra` `stam` works at once |
| Attack Speed, Ferocity | no mechanism (LATER) | the swing-speed system (`research/Swing-Speed-Spec.md`) and code-dealt extra hits |
| Mining Speed and Chopping Speed lines | SkyyTrees reads no outside source | a SkyyTrees patch that accepts outside bonuses |
| Breath (oxygen) and swim speed lines | locked as accessory effects (locks 61-62) but no Skyy code touches them; UNVERIFIED | engine checks of the Oxygen stat and swim settings |
| Dodge Chance, -% Spell Cost, Ability Damage, raw spell damage | no dodge-chance stat, no spell system | those systems |
| Combat Wisdom, XP Bonus, Loot Bonus, Loot Quality, Stealing, Trophy Hunter, coins | nothing reads them | readers in SkyySkills and the drop code |
| Mob-type protection and damage lines (undead, spiders, beasts, void) | no mob-family tags or damage hook | a mob family table and a SkyyGear hook |
| Day and night pair (Strength by night, Defense by day) | small new code that reads world time | a time check in the effect tick |
| Out-of-combat-only Regeneration (Q10 option) | no "last hit" timestamp in SkyyAccessories | a damage listener or a SkyyGear bridge key |
| Growing accessories (a kill counter or collection counter on the item) | needs item metadata and counters | metadata storage, like SkyyGear rolls |
| Mythic 5th tiers on the drop lines | no bosses or drop tables yet | boss drops |
| Accessory Power sum, powers (Balance and the rest), tuning, enrichments | not built (inventory G6) | SkyyAccessories 0.6 and later (Plan section 4); the Omni rule in 1.3 |
| Drop tables (mobs and chests), Combine recipes, collection gating of craft tiers (lock 64) | no Skyy mod adds mob or chest drops (inventory G7, G14) | a kill hook (SkyyCollections `CollKillSys` or SkyyGear `GearDeathMark` pattern) and a first-open chest roll (SkyyExploration pattern) calling `acc:fn:give` (5.9) |
| Bag slot unlocks (collections, skills, coins) | not built | Plan section 3, rebased (5.5) |
| Accessory stats in the HUD and stat screens | `gear:fn:stats` leaves `gear:extra` out on purpose | a SkyyGear total that includes it |
| More than one `gear:extra` writer | it is one string per player (inventory G4) | SkyyGear accepts a map of source to string, like `move:<uuid>` |
| An AH sub-category by booster stat | SkyyAuctions files every `Skyy_Talisman_*` under ACCESSORIES | an optional SkyyAuctions filter; the first tooltip line names the stat meanwhile |

---

## 5. How it fits the bag and the pack

### 5.1 The 25 talismans: fold them in (nothing is retired)

- They **become** the five backbone lines. Same item ids, same Workbench recipes, same one-per-family swap. What changes: the names
  (Health Charm and so on), the rarity look (5.2), the numbers (2.2, 1.6), and Health and Stamina become flat.
- **No item is rewritten.** Ids stay. Names, descriptions and the item quality come from the jar's item files, so every copy shows the
  new name at once. Only the stored quality index needs the restamp in 5.2.
- **Config migration**, one atomic write (tmp file + move) in `AccCfg.load(true)`, **before** `CfgPub.start` (the SkyyGuilds pattern).
  `AccCfg.writeDefaults` only seeds a missing file, and every 0.4.4+ server already has a `config.properties` with `slots=9` and
  `bonus.*` lines, so the new table entries would otherwise stay empty on every existing server (a kit table's row default must be
  empty; entries come only from file lines).
  - **When it runs:** only when the file has at least one `bonus.` line and no `boost.` line. After the write there are no `bonus.`
    lines left, so it never runs again, and a later deliberate `slots=9` stays 9. A file with neither kind of line just gets the missing
    `boost.` entries appended, and `slots` is left alone. A missing file gets the full 0.5 defaults from `writeDefaults`.
  - **Backup:** before writing, copy the old file once to `config.properties.pre-0.5.bak` (never overwrite an existing `.bak`). The
    kit's `config-history/` does **not** cover this write: the kit copies a file only at its own next save, and this migration runs
    before the kit starts.
  - `bonus.Intelligence`, `bonus.Regeneration`, `bonus.Speed`: an untouched 0.4.x default (`2,4,6,8,10`, `0.5,1,1.5,2,3`,
    `2,4,6,8,10`) gives way to the new default; an edited value is carried over to `boost.Mana.pct`, `boost.Regeneration.pct` or
    `boost.Speed.pct` as it is.
  - `bonus.Vitality`, `bonus.Endurance`: their unit changed (% to flat), so an edited value cannot carry over. It is dropped and
    **written to `config-changes.log`** with its old value, so the admin can redo it by hand.
  - `slots=9` becomes 18 in this one run. 9 was the hard maximum in 0.4.x, so a deliberate 9 cannot be told apart from the default;
    an admin who wants 9 sets it again once and it stays.
  - The old `bonus.` lines leave the file in the same write, and all `boost.` entries are appended (build defaults where nothing
    carried over).
  - Every changed, carried or dropped value gets one line in `config-changes.log` in the kit's format (who `migration-0.5`, via
    `migrate`) and one server INFO line.
- **One-time chat notice** (Server Setup switch, default on), with no scrapped names in it: "Your talismans are now booster
  accessories, with new names, rarity colours and numbers. Red is Health, yellow Stamina, blue Mana, green Regeneration, cyan Speed.
  /accessories shows your bonuses."
  - Sent only to players who already have a bag file (they used accessories before 0.5).
  - `PlayerReadyEvent` fires on every world switch and this mod has no event listener today, so 0.5 adds one listener and stores a
    per-player "notice seen" flag in a file (as SkyySacks does). The notice goes out once per player, ever.

### 5.2 Rarity: move accessories to the Wynn ladder

- **Six quality assets in the jar:** `Skyy_Acc_Normal`, `_Unique`, `_Rare`, `_Legendary`, `_Fabled`, `_Mythic`. Never a bare rarity
  word as an id (other mods in Skyy's folders ship `Mythic`; Bag-Restructure-Spec 1.4). Colours and frame art are the same as
  SkyyGear's `Skyy_Gear_*` table, and page colours come from the kit (`SUI.RARITY`, `SUI.RARITY_ORDER`). The field set must equal
  vanilla `Common.json` (the SkyyGear build check). QualityValue 1 to 6 stays below SkyyAuctions' "technical" limit of 8, so they stay
  tradeable, and SkyyAuctions' `qPretty` and filter already handle `Skyy_*` qualities (VERIFIED). SkyyAccessories ships its own set,
  because every Skyy mod must work alone.
- **Labels:** write each quality label under both `general.qualities.<id>` and `server.general.qualities.<id>`, as SkyySacks does
  (SkyyGear writes only the first).
- **Mapping** (SkyyGear's own migration map): Common to Normal, Uncommon to Unique, Rare to Rare, Epic to Legendary, Legendary to
  Fabled. Bench accessories follow it too (T1 Normal up to T5+ Fabled). The **Omni becomes Mythic**, like the Mythic Omni Bag (Q2).
  The **Accessory Bag item** (`Skyy_Accessory_Bag`) gets `Skyy_Acc_Unique`, which matches the ladder's second step.
- **Code: id words and display rarities are separate arrays.** 0.4.5 uses one `RARITY` array for id parsing (`tierOf`), id building
  (`modernOf`), names, lang, colours and error text. Under the Wynn ladder that breaks: "Legendary" is T5 in ids but a T4 rarity on
  screen, and Normal, Unique and Fabled are not id words, so `Skyy_Talisman_X_Legendary` would parse as T4 and `modernOf` would build
  wrong ids. 0.5 keeps an `ID_WORD` array (Common, Uncommon, Rare, Epic, Legendary) only for parsing and building ids, and a `DISPLAY`
  array (Normal to Mythic) plus a per-tier rarity index in the booster table for everything players see.
  `AccDefs.rarityOf` returns 1 to 6 (Normal to Mythic) from the booster table, because a drop line's T1 is Unique, not Normal.
- **Restamp.** Saved stacks keep the quality index they were saved with (VERIFIED, Bag-Restructure-Spec 1.4), so old stacks must be
  restamped with `withQuality` (the SkyySacks 0.7.7 pattern, spec 5.6):
  - It runs inside `AccEffects.tick`, which is on the world thread, every 5th run per player. It must **not** run in `AccTick`: that
    one is scheduled on `HytaleServer.SCHEDULED_EXECUTOR`, and inventory writes must be on the world thread.
  - Only when `AccStore.moveBlock(u) == null` (no bag move in progress for that player).
  - It covers every `Skyy_Talisman_*` and `Skyy_Accessory_*` stack in storage, hotbar and backpack whose index differs from its item's,
    **plus the bag item by name**, because `AccDefs.isAccessory` leaves `Skyy_Accessory_Bag` out.
  - The bag file stores ids only, so bag contents need nothing.
- **Known gaps** (the builder states them in the 0.5 notes):
  - The 2026-09-30 in-game probe (OPEN-QUESTIONS, "Seen in game") found that item slots with rarity backgrounds work on our pages,
    but rarity **frames** did not show. Expect the name colour and rarity label to show and the frame possibly not (UNVERIFIED, the same
    open test as SkyyGear and the bags). The rarity word is on the bag page either way.
  - Stacks outside a player's own inventory (SkyyVault, auction listings, trade windows, chests) keep the old look until they are
    taken out into an inventory, where the restamp catches them. Nothing is lost; only the look is stale.
  - Six new quality assets shift the index of every quality that loads after them. Other mods' saved stacks (for example Extended
    Backpacks' Mythic, SkyyVault items) may show a shifted look, as already happened when SkyyGear and SkyySacks added theirs. Test 1.
  - Rolling back to 0.4.5 leaves restamped stacks pointing at `Skyy_Acc_*` indexes that no longer exist (5.3).
- INFERRED: items that name a plugin quality load fine (SkyySacks 0.7.7 bags have used `Skyy_Bag_*` in their item files since
  2026-09-28).

### 5.3 Item ids and roll-back

- **New lines: `Skyy_Talisman_<Key>_T<n>`.** Old lines keep `Skyy_Talisman_<Key>_<Common..Legendary>` (5.1).
- Why the `Skyy_Talisman_` prefix: every current reader already treats it as a stat accessory. SkyyAuctions files it under
  ACCESSORIES, SkyyMenu counts it through `acc:tal`, and `AccDefs.familyOf` and `groupOf` already work for any key (VERIFIED).
- **Not `Skyy_Accessory_<Family>_<Tier>`** (the task's example): that prefix means "bench accessory". `AccDefs.benchOf` would turn
  the family into a fake bench id, publish it in `acc:has`, and SkyySacks would draw a fake `/craft` tab. 0.2 had exactly this bug.
- **Not the words Talisman, Ring or Artifact** at the end of an id: they are the 0.2/0.3 legacy tiers, and `modernOf` would turn
  `..._Ring` into `..._Rare` on equip, an id that does not exist.
- Parse order in 0.5: a `_T<digits>` tail first, then the `ID_WORD` rarity words, then the legacy words. Keys: CamelCase, no
  underscore, not ending in a rarity or legacy word.
- **Roll-back (corrected).** An earlier draft said going back to 0.4.5 loses no item. That was wrong: 0.4.5's `slotsK` reads only
  `slot0` to `slot8`, and `saveK` rewrites the whole bag file from that 9-slot array, so the next equip, unequip, `putK` or `stashK` on
  0.4.5 would delete slots 10 to 60 for good. So 0.5 does two things:
  - **Slots 0 to 8 stay in `bags/<pkey>.properties`** (the file 0.4.5 knows, same format), and **slots 9 to 59 go into
    `bags/<pkey>.more.properties`**, which 0.4.5 never reads or rewrites. After a roll-back the extra slots are hidden, not lost, and
    they come back with 0.5. 0.5 puts nothing else into the main file that 0.4.5 would drop on its rewrite.
  - **"Do not roll back below 0.5"** goes into the 0.5 deploy notes (the HANDOFF line whoever logs the deploy writes), as done for
    other mods. Reasons that the second file does not fix: restamped stacks point at `Skyy_Acc_*` quality indexes that 0.4.5 does not
    ship (stale look; UNVERIFIED whether an out-of-range index is safe), and new-line items in inventories are item ids 0.4.5 does not
    define (UNVERIFIED how the game treats them). A `slots=18` value is harmless on 0.4.5 (it clamps to 9 with a warning, VERIFIED).
    New-line items inside the bag are safe: 0.4.5 ignores a family it does not know (`familyIndex` returns -1).

### 5.4 How the stats reach the game (one generic effect tick, world thread, once a second per player)

The five hard-wired arrays (`VIT END INT REG SPD`) become **one booster table**: family key, admin name, line name, feed, stats, tier
ids, rarity per tier, numbers per tier, look per tier, source words per tier. The tick finds the best tier of each line in the bag (the
active profile's bag, `AccStore.pkey`), adds up each stat, and sends it.

**Javassist limits for the table (tested by the feasibility review with `tools/javassist.jar`):** `new float[][] {...}` and
`new String[][]` both fail to compile, and so do labeled `break` and `continue`. No live script uses `[][]`. Use flat 1-D arrays
(index = line x 6 + tier) or a text table parsed at class init, and loops without labels. 1-D arrays, `switch` on an int, `long` maths
and large initializers compile.

| Feed | Exact call | Rules |
|---|---|---|
| Health, Stamina (flat) | `putModifier(stat, "skyyacc_health" / "skyyacc_stamina", StaticModifier(MAX, ADDITIVE, amount))` | removed at 0 and when the mod is off. Never MULTIPLICATIVE (the engine adds every multiplicative amount into one factor) |
| Mana (% with floor) | same, key `skyyacc_mana`, amount = max(round(flatMax x pct) / 100, floor) | flatMax leaves out every `skyyacc_` key (it includes the SkyyGear armor lock, VERIFIED) |
| Regeneration | `addStatValue(Health, max x pct / 100)` every `regenEverySeconds` while 0 < Health < max | today's code; works in combat |
| Speed, jump, fall | `MoveSync.post(u, "accessories.talismans", "pct", speed, jump, fall)` then `sync` | one source for the whole bag (the existing name, so nothing else changes). Fractions: 0.10 = +10%, fall -0.40 = 40% less (the config stores the magnitude, the tick adds the minus). All zero removes the entry |
| Combat stats | `gear:extra:<uuid>` = one String, for example `"cc:4,cd:8,def:6,mp:3,str:9"` | whole numbers only (SkyyGear floors each part); one summed part per key; written only when the text changes; removed when empty, on leave, and republished on a profile switch (`profile:epoch`). Foreign text: see below |
| Wisdom, Fortune (wave 2) | `skill:bonus:<uuid>` map, source `accessories.boosters` = `{"xp.mining": 0.03, "dd.mining": 0.03}` | outer map created with `putIfAbsent`; the source's map is replaced whole when it changes |

- **Foreign `gear:extra` text.** We are the only writer until SkyyGear accepts a map. If the bridge holds text we did not write,
  overwrite it and log one WARN for that player. If the text changes again within 5 s after our overwrite (a second writer, even a test
  one), **stop writing for that player** until they relog or switch profile, and log one more WARN. Two writers never fight every
  second.
- **One try per publisher.** In 0.4.5 one `try` wraps the whole tick with one log-once flag, so a bug in new code would stop the speed
  sync and the stat modifiers too. 0.5 gives each publisher its own try and log-once flag: stat pools, Regeneration, movement,
  `gear:extra`, and the restamp.
- **No stale bridge keys.** `publishOnline` removes our `gear:extra:<uuid>` for every player who is no longer online, and `shutdown`
  removes it for every player we wrote (0.4.5 prunes only its local maps, so the key would outlive the player and the plugin).
- **SkyyGear present and switched on.** Detect SkyyGear by its bridge keys (`gear:gates` or a `gear:fn:*` function). Read its
  `part.stats` switch through `config:fn:SkyyGear` `get` (a legal `java.lang` bridge call). The bag page shows "Combat stats need
  SkyyGear" when it is missing and "SkyyGear's 'Gear stats in combat' is off" when the switch is off, instead of silently doing nothing.
  Feather's fall part shows "needs SkyySkills" the same way.
- **Equipping does not raise current Health or Stamina**, only the maximum; the bar fills by normal means. Do not "fix" this by adding
  the difference on equip: unequipping and re-equipping would then heal for free.
- All cross-mod calls go through `skyy.bridge` with `java.lang` types only.

### 5.5 Bag size and the bag page

- **Storage:** `CAP` 9 becomes 60, split over two files (5.3): `slot0` to `slot8` in `bags/<pkey>.properties`, `slot9` to `slot59` in
  `bags/<pkey>.more.properties` (both written tmp + move; old files simply have no second file, so no migration). `CAP` is storage
  only.
- **Slots:** the config row `slots` gets a default of **18** and a maximum of 60 (Q7). It still limits new equips only.
  - 18 is a deliberate squeeze, not an accident: the Omni (which stands for all 11 bench accessories) plus the 10 lines fit with 7
    spare, but 11 bench accessories plus 10 lines (21, or 22 with the Omni) do not, so players choose until unlocks exist.
  - `SkyyAccessories-Plan.md` section 3 (a draft) starts at 9 and adds +51 from collections (+12), skills (+20), coins (+16) and quests
    (+3), capped at 60. Starting at 18, those sources are **rebased to +42** so the cap stays 60 (for example coins +16 to +10 and
    collections +12 to +9); the exact split is set when unlocks are built.
- **Page:** the vanilla-kit window grows from 1210 x 780 to about **1210 x 950** (fits 1080 high). The BAG SLOTS well shows 9 rows per
  page (new constant `PAGE_ROWS = 9`) and the inventory list 6 rows per page, each with the kit's pager (the in-game probe of
  2026-09-30 showed the pager working). The Bonuses well lists up to 12 short lines in two columns (for example "+12 Strength",
  "+10% Speed", "-40% fall damage"), using the live config numbers.
  - `ACC_COLS_H` must be computed from `PAGE_ROWS`, not `CAP` (from `CAP = 60` the page would be far too tall). Update `fit()` and the
    test-harness asserts that expect `(1210, 780)`.
  - The bag item's description no longer prints `CAP` ("Holds up to 60"); it uses a neutral text ("Holds your accessories").
- Unlocking slots through collections, skills and coins stays for later (Plan section 3, rebased as above).

### 5.6 Looks (vanilla items by reference, one look per tier)

Each tier copies the **model** and **icon paths** of a vanilla item, as the talismans do today (`visual_of`, `icon_of`). Nothing is
copied into the jar. Every item named below was checked in Assets.zip (read only): every item exists, every ingredient has its own
model, and no two tiers share an icon (VERIFIED, both reviews re-checked all line-tier looks).

**Backbone lines:** model = the line's crystal fragment item for every tier (crystal clusters and gems are blocks, with no item model).
Icons: T1 crystal fragments, T2 small cluster, T3 medium cluster, T4 large cluster, T5 gem. So each tier now gets its own icon; today
T1-T2 share one icon and T3-T5 share another.

| Line | Colour (T1 `Ingredient_Crystal_<C>`, T2-T4 `Rock_Crystal_<C>_Small/Medium/Large`) | T5 icon |
|---|---|---|
| Health | Red | `Rock_Gem_Ruby` |
| Stamina | Yellow | `Rock_Gem_Topaz` |
| Mana | Blue | `Rock_Gem_Sapphire` |
| Regeneration | Green | `Rock_Gem_Emerald` |
| Speed | Cyan | `Rock_Gem_Zephyr` |

**New lines** (model and icon from the named item unless a model is given):

| Line | T1 | T2 | T3 | T4 |
|---|---|---|---|---|
| Brawler | `Ingredient_Bone_Fragment` | `Ingredient_Sinue_Cindersinue` | `Ingredient_Fire_Essence` | `Ingredient_Voidheart` |
| Runic | `Ingredient_Crystal_Purple` | icon `Rock_Crystal_Purple_Small` | icon `Rock_Crystal_Purple_Large` | icon `Rock_Gem_Voidstone` |
| Stonehide | `Ingredient_Crystal_White` | icon `Rock_Crystal_White_Small` | icon `Rock_Crystal_White_Large` | icon `Rock_Crystal_Iridescent_Large` |
| Razorfang | `Ingredient_Crystal_Pink` | icon `Rock_Crystal_Pink_Small` | icon `Rock_Crystal_Pink_Large` | icon `Rock_Crystal_Iridescent_Medium` |
| Feather | `Ingredient_Feathers_Light` | `Ingredient_Feathers_Blue` | `Ingredient_Ice_Essence` | `Ingredient_Motes_Light` |

- Crystal-line tiers without their own model use that line's crystal fragment model. The Diamond gem stays the Omni's icon only.
- Spares (checked, now unused after the crit lines were paired): `Ingredient_Feathers_Dark`, `Ingredient_Feathers_Red`,
  `Ingredient_Lightning_Essence`, `Rock_Crystal_Iridescent_Small`.
- Wave 2 suggestions (checked too): Prospector `Ingredient_Stud_Iron`, `Ingredient_Powder_Boom`, `Ingredient_Bar_Thorium`,
  `Ingredient_Bar_Onyxium`; Woodsman `Ingredient_Tree_Bark`, `Ingredient_Tree_Sap`, `Ingredient_Life_Essence`,
  `Ingredient_Life_Essence_Concentrated`; Harvester `Ingredient_Fibre`, `Ingredient_Life_Essence_Wheat`,
  `Ingredient_Life_Essence_Pumpkin`; Leech `Ingredient_Sac_Venom`, `Ingredient_Chitin_Sturdy`, `Ingredient_Void_Essence`.
- A booster can look like a stack of the ingredient it borrows (today's talismans look like crystals). The rarity colour, the name and
  `MaxStack 1` tell them apart. Our own art can replace any row later.

### 5.7 Tooltips (vanilla look)

- The name takes the quality colour and the rarity label on its own. The description uses vanilla item-text markup: line breaks,
  `<color is="#ffffff">` for the key number, `<i>` for a flavour line. VERIFIED in `Server/Languages/en-US/server.lang`: of the 331
  vanilla item descriptions (548 description keys in all), 143 use at least one of these (101 colour, 38 italic, 101 line breaks).
- In the language file a line break is the **two characters `\n`** on one line. A real newline would break the `"\n".join(lang)` file.
- Parts, in order: **the stat line first** (the line name alone does not say the stat), what it affects, any requirement, the
  one-per-line rule with the next tier's name, a flavour line. No mod names: players do not know "SkyyGear". Example, Brawler Band
  (shown with the line breaks rendered):

```
<color is="#ffffff">+6 Strength</color> while in your Accessory Bag.
More damage with melee, arrows, thrown weapons and staff melee.
Works with gear weapons or bare hands.
Only your best Brawler accessory counts. Next: Brawler Sigil.

<i>Scuffed wraps from a hundred fights.</i>
```

- Per-line requirement lines: Runic "Spell shots only (wand, staff, spellbook)."; Stonehide "Against hits from mobs and players.";
  Razorfang "+4% Crit Chance and +8% Crit Damage" on its stat line; Feather "Fall damage needs SkyySkills." is shown only on the bag page
  (tooltips are static).
- **Every player string is built from the line name plus the tier word**, never from the family key. In 0.4.5, `AccDefs.pretty`, the
  `why` refusal text, the legacy lang names and the bag description all print the family key plus "Talisman"; 0.5 replaces each one.
- Generated from the booster table, so text and numbers match the build defaults. A config change does not change item text (known
  limit G12). To keep that small, the "Next" part names the next tier without its number; the bag page and `/accessories lines` show
  the live numbers. Accessory Power stays off the tooltip until powers exist (Q9).

### 5.8 Server Setup rows (every number editable in game; kit `tools/skyycfg.py`)

| Key | Label | Category | Type | Default | Notes |
|---|---|---|---|---|---|
| `slots` | Accessory slots | Accessory Bag | int 1-60 | 18 | existing key, new max; live; lowering deletes nothing |
| `regenEverySeconds` | Regeneration heals every | Boosters | int, s | 2 | existing |
| `boost` | Booster numbers | Boosters | 1-column table (text), live, with a `check=` hook | row default empty (kit rule); the entries are written to the file by `writeDefaults` or the migration (5.1) | entry `<Admin name>.<stat>`, value = a comma list with one number per tier; a missing entry uses the build default |
| `line.Health` ... `line.Feather` | Health line, Stamina line, ... | Boosters | bool (10 scalar rows), live | on (see 6, staging) | off = the line stays in the bag, counts for nothing, and shows "switched off" |
| `combatToGear` | Send combat stats to SkyyGear | Boosters | bool, live | on (see 6, staging) | off = `gear:extra` is removed for everyone |
| `notice.boosters` | Tell players about the booster change | Accessory Bag | bool | on | the one-time chat line (5.1) |

- **`boost` entries** (the unit is in the entry name): `Health.flat`, `Stamina.flat`, `Mana.pct`, `Mana.floor`, `Regeneration.pct`,
  `Speed.pct`, `Strength.flat`, `MagicPower.flat`, `Defense.flat`, `Crit.chancePct`, `Crit.damagePct`, `Feather.fallPct`,
  `Feather.jumpPct`. Admin names, never Vitality, Endurance or Intelligence.
- **Why 10 bool rows, not a table of on/off:** no deployed table has a `bool` column, and SkyyMenu 0.3.3's table editor edits cells as
  typed text; scalar `bool` rows give real ON/OFF buttons.
- **No signs:** `AccCfg.num()` rejects a minus sign, so Feather's fall is stored as magnitudes (`10,20,30,40`) and the tick negates it;
  jump is `5,10,15,20`.
- **The `check=` hook** refuses a list whose count differs from the line's tier count, any negative or non-number, whole-number-only
  stats with a decimal (`Strength`, `MagicPower`, `Defense`, `Crit.*`, later `lsteal`: SkyyGear floors them, so a decimal would
  silently shrink), and values over a sane cap (100 for a percent, 1000 for a flat). Decimals are fine for Health, Stamina, Mana,
  Regeneration, Speed and Feather.
- **Help text is capped at 100 characters** (build-enforced), so one row cannot explain 13 units; the unit lives in the entry name.
  Example help: "One number per tier, comma list. The entry name gives the unit. Fall is written without a minus."
- **No Accessory Power row.** The AP table is a build constant until powers exist (1.3).
- The old `bonus` row goes away (migrated, 5.1). Rows marked live apply at once, like today's `bonus` row.

### 5.9 Hooks for getting them (acquisition stays a placeholder)

- **Commands** (two named admin sub-commands and one player sub-command, so no command has two usage variants):
  - `/accessories lines` (player): every line, its tiers, item ids, live numbers, and whether it is switched on.
    `setPermissionGroups(new String[] { "hytale:Adventurer" })`.
  - `/accessories give <player> <item id> [amount]` (admin).
  - `/accessories givetier <player> <name> <tier> [amount]` (admin). `<name>` takes the admin name (Health, Stamina, Mana, Strength,
    Crit, ...) and, as aliases, the old keys Vitality, Endurance and Intelligence. Usage and replies show the admin names only.
  - Each admin sub-command: `requirePermission("skyyaccessories.admin")` and `setPermissionGroups(new String[0])` (lint rule
    `perm_group_leaks`). `[amount]` is an optional argument, not a usage variant; if the command framework needs a variant for it,
    that variant gets the same two calls by hand, because the lint does not check variants.
  - Delivery runs on the **target player's world thread**; for a target in another world it hops with `world.execute`, as SkyyGear's
    `/gear migrate [player]` does (near line 6443 of `build_skyygear_0.1.py`). Storage first, the rest dropped at the player's feet
    (`addOrDropItemStack`), one item at a time (MaxStack 1, like today's `giveOne`), counting items before and after. The admin gets
    "Gave N" when it is done.
- **Bridge for the later loot pass:** `acc:fn:give` = Function(Object[] { UUID, String itemId, Integer amount }) returning an Integer
  (how many were given, counted before and after). **Call it on the target player's world thread** (a kill hook and a first-open chest
  roll already run there): `addOrDropItemStack` needs that player's store and ref. Called from any other thread, it hops with
  `world.execute`, returns 0 and logs one line. It only accepts ids from the booster table.
- **Bridge `acc:defs`:** one String listing every tier as `name:key:tier:itemId:rarity:ap:sources` (admin name, family key, tier
  number, id, display rarity, Accessory Power, source words joined by `+`, for example `Health:Vitality:4:Skyy_Talisman_Vitality_Epic:
  Legendary:19:Craft+Chest`). The loot pass builds its tables from the same source words (Drop, Chest, Combine, Craft, Boss) and finds
  hooks for all 45 items.
- New lines get **no recipe** in 0.5 (Skyy: "we will worry about how they are made/upgraded later"). Q13.

### 5.10 Which mod versions build it

| Mod | Version | Change |
|---|---|---|
| SkyyAccessories | **0.5** | everything in section 6. Patch `tools/acc_0_5_patch.py` reads the generated `SkyyAccessories/build_skyyaccessories_0.4.5.py` and writes `build_skyyaccessories_0.5.py` (edit the patch, never the generated file). The patch replaces roughly half of the 0.4.5 script: keep the `ACC PAGE BLOCK START/END` markers so a 0.5 test harness can exec the page block as `test_skyyaccessories_0.4.5.py` does |
| SkyyGear | 0.1 (live), no change | already reads `gear:extra` for Strength, Magical Power, Defense and crits, on every hit (VERIFIED) |
| SkyySkills | 0.4.7 (live), no change | applies fall damage from every movement source; reads `skill:bonus` for wave 2 |
| skyymove protocol | v1, no change | carries `jump` and `fallDamage` already |
| SkyyAuctions, SkyyMenu | no change needed | only these two read `acc:` keys (VERIFIED). Optional later: an AH filter by booster stat; SkyyMenu's "N talismans" could read "N boosters" |
| Wave 2 | SkyyAccessories 0.5.1 | table rows, items, looks and the `skill:bonus` publisher (Leech after Skyy's Life Steal shape); flip any stage-2 defaults left off (section 6) |

---

## 6. First-build list (the next pass builds this: SkyyAccessories 0.5)

1. One **booster table** in flat 1-D arrays (5.4) replacing the five hard-wired families, and one generic effect tick with one try per
   publisher.
2. **Wynn rarity** for every accessory: six `Skyy_Acc_*` quality assets with both label keys, the mapping (Omni Mythic, bag item
   Unique), separate `ID_WORD` and `DISPLAY` arrays, the world-thread restamp, `rarityOf` 1-6, kit colours (5.2).
3. **Fold the 25 talismans**: new names and numbers, flat Health and Stamina, Mana floor, lower Regeneration, config migration with
   `.bak` and log lines, one-time notice with its per-player flag file (5.1, 2.2).
4. **Five new lines, 20 items**: Brawler, Runic, Stonehide, Razorfang, Feather, with looks and tooltips (2.3, 2.4, 5.6, 5.7).
5. **Publishers**: `gear:extra` (only writer, whole numbers, allowlist, back-off rule, stale-key removal), the movement source (speed,
   jump, fall), the stat pools, Regeneration; SkyyGear presence and `part.stats` shown on the bag page (5.4).
6. **Bag**: 60 storage slots in two files, default 18, `PAGE_ROWS` paging for slots and inventory, the generic Bonuses well, window
   about 1210 x 950 (5.5).
7. **Commands and bridges**: `/accessories lines`, `give`, `givetier`, `acc:fn:give`, `acc:defs` (5.9).
8. **Server Setup rows** (5.8).

**Staging (one version carries a lot, so build it in two stages in the same patch):**
- **Stage 1:** the table, the fold, rarity and restamp, the bag, the config migration and rows, commands and bridges, the notice. This
  is where the risk to existing players sits, so it is built and checked first.
- **Stage 2:** the three feeds that have never run in the game: `gear:extra`, Feather's fall and jump. If stage 2 has not been tested in
  game before the deploy, ship it with `combatToGear` **off** and `line.Feather` **off** by default; Skyy switches them on in Server
  Setup for the first test, and 0.5.1 flips the defaults once it passes. New lines only come from the admin give, so a switched-off
  line affects no player.

**Build checks** (the script must fail on any of these):
- a booster uses a stat outside 1.4's allowlist, or a `gear:extra` key outside `str mp def cc cd lsteal`;
- any booster id starts with `Skyy_Accessory_` or ends in `_Talisman`, `_Ring` or `_Artifact`;
- a tier count does not match its number list; two tiers share an id or an icon;
- any of the 25 modern ids, the 15 legacy ids or the 20 new `_T<n>` ids fails to round-trip through `tierOf`, `familyOf` and
  `modernOf`, or the equip swap order differs from 0.4.5 for the old lines;
- a player string (lang, chat, page, refusal text) contains Vitality, Endurance, Intelligence or Talisman;
- a look path is missing in Assets.zip (today's `visual_of` and `icon_of` checks);
- a quality asset's field set differs from vanilla `Common.json`, or its QualityValue is 8 or more;
- the page does not fit at its new size (`fit()` and harness asserts updated from 1210 x 780);
- (the kit already fails on help text over 100 characters.)

**In-game tests** (the builder writes the full numbered steps):
1. Old talismans show the new names and Wynn colours; the restamp fixes stacks in storage, hotbar and backpack; the bag item shows
   Unique and the Omni Mythic. **A rolled gear item, a Magic Bag, an Extended Backpacks Mythic item and a SkyyVault item still look
   right** after the deploy (quality index shift). A talisman kept in the vault keeps its old look until taken out, then is restamped.
2. Config: a copied 0.4.5 `config.properties` migrates once (`config.properties.pre-0.5.bak` exists, `config-changes.log` has the
   lines, `slots` is 18, edited Mana/Regeneration/Speed numbers carried over). Restart: no second migration. Set `slots` to 9, restart:
   it stays 9.
3. `give` and `givetier` each new tier (also with the alias Vitality); equip T1, then T2 (T1 comes back); an equal tier is refused.
   Give to a player in another world.
4. `/gear` shows the "From other mods (gear:extra)" line with the right totals; a hit with and without Brawler; Razorfang with and
   without gear Crit Chance.
5. Health and Stamina maximums grow by the flat amount and the current value does not jump (expected); Mana grows by the percent, or
   by the floor on a small pool.
6. Speed with and without Acrobatics; fall from a set height with and without Feather; jump height at T4; the Acrobatics double jump
   with and without Feather (INFERRED to rise too).
7. Profile switch and relog: stats follow the active profile's bag; logout removes `gear:extra`; a server stop removes it too.
8. Server Setup: change `boost` `Strength.flat` and `slots`, see it apply at once; a refused entry (wrong count, a minus, a decimal
   Strength); switch a line off; `combatToGear` off; SkyyGear's `part.stats` off shows the note on the bag page.
9. The notice shows once for a player with a bag file, never again after a world switch or relog, and never for a brand-new player.
10. Bag page at 18 slots and at 60 (config), pagers, fits at 1080.
11. UNVERIFIED items to watch: plugin quality frames and colours; the first real `gear:extra` publisher; fall damage and jump from an
    accessory source (never sent before).

---

## 7. Open questions for Skyy (default in brackets)

1. **Tier words** Charm, Band, Sigil, Emblem, Crest in the names? This brings back tier words, which the 2026-09-23 note replaced with
   rarity names. [yes: the word shows the step, the Wynn colour shows the rarity; fallbacks: Relic and Heirloom for T4 and T5
   (Hypixel's own ladder words, like the names scrapped in locks 79 and 100), or today's "Rare Health Talisman" style]
2. **Wynn ladder for all accessories** (boosters, bench accessories, the Omni, the bag item)? [yes, with SkyyGear's mapping; the Omni
   becomes Mythic like the Mythic Omni Bag; the bag item Unique]
3. Does **"+ stamina" mean max Stamina** only, with Stamina Regen kept off accessories (lock 27)? [yes]
4. **Speed**: keep the accessory % layer (multiplies with Acrobatics), or lock 25's flat layer (adds)? The % top tier is 4x the best
   gear Speed roll at Acrobatics 100 (+0.20 against +0.05) and 2x at Acrobatics 0; flat would be 2x at any level. [keep %, with
   today's 2/4/6/8/10: it is what you asked for and what the live Speed talisman does]
5. **Health and Stamina flat** (+5 per tier Health, +2 to +6 Stamina) instead of % of your pool? **Every existing Health, Stamina and
   Mana talisman gets stronger on deploy** (1.6: Health 1.25x to 2.5x, Stamina 1.7x to 10x, Mana 2.5x to 5x). [yes, accept the jump;
   gentler option: Health +3/+6/+9/+12/+15 and Stamina +1 to +5]
6. **Mana**: % with a small flat floor (at least +1/+2/+3/+4/+5), so a new Mage feels it? This bends lock 88 (% mana on dedicated
   accessories) and **needs your yes**. [% with the floor; setting the floor row to 0 gives % only, where T1 to T3 do nothing you can
   feel until armor and levels raise the pool]
7. **Bag slots** until the unlock sources exist? [default 18, max 60, pages of 9; a 0.4.x config on 9 moves to 18 once. 18 is a
   deliberate squeeze (the Omni plus 10 lines fit; 11 benches plus 10 lines do not). The Plan section 3 unlock sources shrink from +51
   to +42 so the cap stays 60]
8. When a later line **shares a stat** with another line: one per stat, or one per line? [one per line; the first build has no overlap]
9. **Accessory Power** table 10/13/16/19/22/25: a build constant only, or shown before powers exist? Do bench accessories count? Does
   the Omni plus benches double count? [build constant, not shown, no setting until powers ship; bench accessories count (lock 112 says
   each accessory); while the Omni is in the bag, bench accessories add 0]
10. **Regeneration power**: today's top talisman (3% per 2 s) beats the best gear Raw Health Regen roll (2, or 2.4 with Health Regen %)
    by 1.25x to 2.5x. [lower to 0.2/0.4/0.6/0.8/1.0%, working in combat (top tier 40% to 85% of the best gear roll); other options:
    keep today's 0.5-3% but only out of combat (needs new code, section 4), or reshape it as the locked Raw Health Regen row]
11. **Combat stats on accessories**: confirm the reading that accessories are not gear, so locks 66 and 75 allow Defense, Crit
    Chance, Crit Damage, Strength, Health and Speed on them despite lock 125 and SkyyGear's gear slot table. [yes]
12. **Crit line**: one Razorfang line with both Crit Chance and Crit Damage, or two lines (Crit Damage alone does nothing without Crit
    Chance, and base Crit Chance is 0)? [one line]
13. New lines **only from the admin give** until the drop tables exist? [yes, no temporary recipes]
14. Small calls, one line: no **level requirement** on boosters; Feather **jump +20%** at the top is fine for the hand-built zones;
    **line names** Brawler, Runic, Stonehide, Razorfang, Feather (and Prospector, Woodsman, Harvester, Leech) are placeholders.
    [no; yes; placeholders, names live only in the language file]

---

## 8. Clashes with locked or earlier lines, and how this file handles them

| Clash | Source | Handling |
|---|---|---|
| The suggested `Skyy_Accessory_<Family>_<Tier>` ids | task text vs `AccDefs.benchOf`, SkyySacks `/craft` tabs | use `Skyy_Talisman_<Key>_T<n>` (5.3) |
| Tier words vs rarity names | 2026-09-23 layer note | Q1 |
| Hypixel's own tier words (Relic, Heirloom) | locks 79, 100 (copy-paste Hypixel names scrapped) | own words Emblem and Crest; Relic and Heirloom only as a fallback (1.2, Q1) |
| Accessories on vanilla rarities while gear and bags use Wynn | Decisions change note 5 (2026-09-25) | move to Wynn (5.2, Q2) |
| Defense, Crit Chance, Crit Damage as accessory main stats | SkyyGear 0.1 slot table (Defense armor only, crits weapon and armor), lock 125 (combat modifiers on combat gear) | read as gear-only rules; accessories are not gear, and locks 66 and 75 put Defense, Crit Chance, Crit Damage, Strength, Health and Speed on accessories (Strength catalog row and lock 103 name accessories outright) (1.4, Q11) |
| Flat Speed (lock 25) vs % Speed (layer model, live talisman, Skyy's "+% movement speed") | SkyyGear-Plan lock 25 | keep %, today's numbers; the power gap to gear is stated (1.5, Q4) |
| Stamina Regen on accessories | lock 27 | left out; max Stamina instead (Q3) |
| Health as % (live Vitality) vs flat Health on accessories | lock 19, lock 22 | flat (Q5) |
| +% Mana on tiny pools | lock 88, inventory C4 | % plus a flat floor, needs Skyy's yes (1.5, Q6) |
| Regeneration beats the best gear regen roll; SkyBlock natural regen is scrap | lock 20, catalog Raw Health Regen and Health Regen rows | numbers lowered below the best gear roll; shape kept for now (1.5, Q10) |
| Damage %, element damage | locks 15, 17 | not used (1.4) |
| "Vitality" and "Intelligence" in player and admin text | locks 20, 67 | display and admin names change; family keys stay in item ids only; build check (2.1, 6) |
| "Not in the game yet" | Skyy 2026-09-30 lock | stat allowlist and build check; Accessory Power a build constant, no setting, not shown (1.3) |
| Old Accessory Power draft 3/5/8/12/16 | Plan section 1 vs locks 111-113 | new table inside +10 to +25 (1.3) |
| Default 18 slots vs start 9 + 51 unlock slots, cap 60 | `SkyyAccessories-Plan.md` section 3 (draft) | start 18, unlock sources rebased to +42, the squeeze is intended (5.5, Q7) |
| Collection-gated craft tiers | lock 64 | not wired in 0.5: today's Workbench recipes stay ungated; the later acquisition pass adds the gate (2.2, section 4) |
| Life Steal numbers | SkyyGear-Plan open item 9 ("do not invent"), catalog row | Leech waits for Skyy's Life Steal shape (section 3) |
| `acc:pct` combat plan vs shipped `gear:extra` | Plan technical notes vs SkyyGear 0.1 | `gear:extra` (5.4) |
| Line names Hawkeye and Bulwark | draft crystal table, Plan section 2 (Archer and Warrior crystals) | dropped: crits paired into Razorfang, Defense line named Stonehide (2.1) |

---

## 9. Sources read

Skyy's design files (read only): `tools/AGENT-BRIEF.md`, `HANDOFF.md` (status block, movement layer rule, versions table, newest log
lines), `OPEN-QUESTIONS.md` (LOCKED lines, the 2026-09-30 SkyyGear level lock and the "Seen in game" probe line),
`SkyyAccessories-Plan.md` (sections 2, 3, 5), `SkyyGear-Plan.md` (locks 1-126, open item 9), `SkyyGear-Stat-Catalog.md` (placement
rows, regen and Life Steal rows, accessory sections), `SkyWynn-Decisions.md` (accessory change notes), `tools/CONFIG-CONTRACT.md`
(table rules, help cap, `config-history/` and `config-changes.log`). Research: `research/Hypixel-Accessories-Research.md` (sections 2
and 5), `research/Accessory-Pack-Inventory.md`, `research/SkyyGear-Stage1-Spec.md` (rarity ladder, migration map),
`research/Bag-Restructure-Spec.md` (quality index and restamp). Build scripts: `SkyyAccessories/build_skyyaccessories_0.4.5.py`,
`SkyyGear/build_skyygear_0.1.py` (modifier maxima, `hpr`/`hprp`, `GearLevel.factor`, `part.stats`, bridge keys),
`SkyySacks/build_skyysacks_0.7.7.py`, `SkyyAuctions/build_skyyauctions_0.1.2.py`, `SkyyMenu/build_skyymenu_0.3.3.py`,
`tools/skyymove.py`, `tools/skyyui.py`, `tools/deploy_set.py`. Assets.zip (read only): the item files for the look paths in 5.6 and the
item-text markup counts in `Server/Languages/en-US/server.lang`. The two reviews of 2026-09-30 (design and feasibility). No scratch
files were made.

---

## Review notes (2026-09-30)

Both reviews were applied in full; nothing was rejected outright. Where a fix differs from the reviewer's suggestion, the reason is here.

- **Design 2 (Regeneration):** lowered to 0.2-1.0% rather than the example 0.25-1.5%, so the top tier stays under the best gear regen
  roll up to about 240 Health (the example still beat it at 200). Out-of-combat-only is kept as the Q10 alternative, since it needs a
  combat timestamp this mod does not have.
- **Design 5 (Razorfang):** paired Crit Chance and Crit Damage into one line (the reviewer's "or pair them") instead of raising Crit
  Damage alone; a raised Crit Damage line still pays nothing without Crit Chance. Hawkeye is gone as a name.
- **Design 7 (tier words):** Emblem and Crest adopted as defaults. Charm and Crest do occur in a few one-off Hypixel item names; 1.2
  says so rather than claiming the words are unused.
- **Design 15 (names):** the stat goes on the first tooltip line; an AH sub-category by stat is left for a later SkyyAuctions change,
  because 0.5 keeps SkyyAuctions unchanged. Bulwark renamed Stonehide so neither crystal-table name is reused.
- **Design 16 (Speed):** took the reviewer's lower option, today's 2/4/6/8/10, so Speed talismans do not change on deploy.
- **Design 19 (Feather):** jump on every tier as an even ramp (+5/+10/+15/+20) rather than +5% on T1 and T2 only.
- **Design 22 (questions):** the five new questions were added (Q5, Q7, Q9, Q10, Q11, Q12 cover them); the old Q10, Q13 and Q14 were
  merged into Q14.
- **Feasibility 1 (roll-back):** did both suggested fixes, the second bag file and the "do not roll back below 0.5" note, because the
  quality indexes and new item ids are roll-back risks the second file does not cover.
- **Feasibility 5 (migration):** chose the atomic rewrite over scalar `boost` rows (13 comma lists fit one table better). The marker
  is "has `bonus.` lines and no `boost.` lines" instead of "new lines absent", so deleting a `boost.` entry later never re-runs the
  migration or bumps `slots` again.
- **Feasibility 12 (commands):** `/accessories lines` is a player command; `give` was split into `give` and `givetier`.
- **Feasibility 14 (counts):** recounted in Assets.zip: 331 item descriptions of 548 description keys; 101 use `<color is=` (the
  review said 102), 38 use `<i>`, 101 use `\n`, 143 use at least one.
- **Feasibility 15 (AP row):** removed; the AP table is a build constant and a field in `acc:defs`.
