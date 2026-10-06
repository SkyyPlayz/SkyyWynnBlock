# Booster accessories: spec

*Design, 2026-09-30. Revised the same day after the design review and the feasibility review, then revised again to Skyy's decisions
(OPEN-QUESTIONS.md, LOCKED 2026-09-30; see "Revision to Skyy's decisions" at the end). Written for Skyy's request of 2026-09-30:
booster accessories (+Strength, +% movement speed, +Stamina, +Health, +Mana and more) that start basic and upgrade, Hypixel style, with
many of them coming from mob drops and world loot chests later. Nothing was built, committed or deployed. **Every number is a
PLACEHOLDER** that Skyy can change in game (Server Setup). Inputs: `research/Hypixel-Accessories-Research.md`,
`research/Accessory-Pack-Inventory.md` (called "the inventory" below), `docs/plans/SkyyAccessories-Plan.md`, `SkyyGear-Plan.md`,
`SkyyGear-Stat-Catalog.md`, `OPEN-QUESTIONS.md`, `HANDOFF.md`, the live build scripts and the engine jar. Where a LOCKED line disagrees
with this file, the lock wins. Section 8 lists every clash and how this file handles it.*

Tags: **VERIFIED** = read in a live build script, in Assets.zip or in HytaleServer.jar bytecode on this PC. **INFERRED** = strongly
implied, not proven. **UNVERIFIED** = needs a test in the game.

**Skyy's decisions (LOCKED 2026-09-30), which this file follows:**
1. No tier words: "they are all accessories. but they come in the same rarity tiers as weapons and armor". A booster line upgrades
   Normal -> Unique -> Rare -> Legendary and stops at Legendary. "mythic and fable are rare finds/drops you cant craft" (a few special
   ones later, not in this build).
2. Bag: 18 slots to start, up to 60.
3. The 25 talismans fold into the new lines with the new numbers.
4. "+stamina" = max Stamina AND Stamina Regen (this lifts the old "Stamina Regen armor only" rule for accessories).
5. How they are obtained and upgraded comes later (mob drops, loot chests). Admin give command for now.
6. A stat that does nothing yet must never be on a booster.

---

## 0. In plain words

1. Four of Skyy's five boosters already exist as talismans: Health, Stamina, Mana and Speed (their internal keys are Vitality,
   Endurance, Intelligence and Speed), plus Regeneration. They are crafted at a Workbench today. They **fold** into the first five
   **booster lines** (same items, same recipes up to Legendary, new names, new numbers). Five more lines follow: Brawler (Strength),
   Runic (Magical Power), Stonehide (Defense), Razorfang (Crit Chance and Crit Damage together) and Feather (less fall damage, higher
   jumps). All ten use effects that already work in the game.
2. **Each line is one accessory** with one name, "<Line> Accessory" (Health Accessory, Brawler Accessory), in **four rarities: Normal,
   Unique, Rare, Legendary**, the same rarity tiers as weapons and armor. The item name starts with its rarity, like the Magic Bags
   ("Rare Health Accessory", like "Rare Mining Bag"). There are no tier words.
3. **Only your best accessory of a line counts.** Copies never stack. Different lines stack. A line stops at Legendary.
4. **Fabled and Mythic accessories are rare finds** that nobody can craft or upgrade into. None are in this build (section 4.1).
5. **Stamina = max Stamina and Stamina Regen.** SkyyAccessories adds the regen itself: your Stamina refills faster whenever it is
   refilling anyway, and never while you sprint (5.4.1). Every stat on a booster works in the game.
6. How you get them stays a placeholder: each rarity carries source words (Craft, Drop, Chest, Combine, Boss) for the later loot pass.
   The old talisman recipes keep working up to Legendary; the new lines come only from an admin give command for now.
7. The bag grows past 9 slots: 18 by default, up to 60, with pages.
8. **Two builds.** Part 1 (SkyyAccessories 0.5) folds the five old lines, moves every accessory to the gear rarities, grows the bag and
   adds the commands. Part 2 (0.5.1) adds the five new lines and the feeds they need (section 6).
9. **On deploy, existing talismans change strength:** Health, Stamina and Mana get stronger (1.2x to 7.5x, depending on your pool),
   Speed gets a little stronger on the lower rarities, Regeneration gets weaker. The old Epic and Legendary talismans both become
   Legendary. See 1.6.

---

## 1. Rules for every booster

### 1.1 What a booster is

- An accessory item that works only while it sits in the Accessory Bag (today's rule). Fixed numbers: no roll, no identify, no reforge.
  SkyyGear never treats these ids as gear (VERIFIED, inventory 3.1).
- A **line** (family) is one theme and one accessory name. Most lines have one main stat. Stamina (max and regen), Feather (fall damage
  and jump) and Razorfang (Crit Chance and Crit Damage, see 1.5) have two.
- Each item of a line is one **rarity** (code tier 1 to 4 = Normal to Legendary; players only ever see the rarity). **Only the highest
  rarity of a line counts**, for its stats and its Accessory Power. Equipping a higher rarity swaps it in and hands the lower one back;
  an equal or lower rarity is refused. This is already how the bag works (`AccDefs.groupOf` and `equipK`, VERIFIED), and a duplicate that
  slips in through `stashK` is harmless because `bestTiers` takes the maximum. So no stacking bug can appear later.
- **One line per stat.** No two lines share a main stat, so Skyy's "only ONE accessory per kind/family counts (no stacking 6 speed
  rings)" and "one per line" mean the same thing today. When later lines share a stat, Skyy picks the reading (Q8).
- No level requirement: accessories are not gear items (Q14).

### 1.2 Names and rarity (Skyy 2026-09-30)

| Code tier | Rarity (Wynn colour, VERIFIED in SkyyGear's ladder) | Accessory Power | Name example |
|---|---|---|---|
| 1 | Normal (white `#FFFFFF`) | 10 | Normal Health Accessory |
| 2 | Unique (yellow `#FFFF55`) | 13 | Unique Health Accessory |
| 3 | Rare (pink `#FF55FF`) | 16 | Rare Health Accessory |
| 4 | Legendary (aqua `#55FFFF`) | 19 | Legendary Health Accessory |

- **Every line has these four rarities and no others.** The old draft's shapes (5-step backbone lines, drop lines starting at Unique,
  a Fabled top step) are gone.
- **Name = "<Rarity> <Line> Accessory".** The rarity word is not a tier word: it is the rarity itself, the same four words gear and Magic
  Bags use. It sits at the front for three reasons: the in-game probe of 2026-09-30 showed rarity **frames** do not render on our items
  (only the name colour and the rarity label do), so the word carries the rarity in lists, chat and the AH; Skyy's Magic Bags already
  read "Rare Mining Bag" (VERIFIED, `build_skyysacks_0.7.8.py`); and this mod already names its items "<X> Accessory" (Campfire
  Accessory, Omni Accessory, VERIFIED). Q14 lets Skyy drop the front word if the colour and label are enough.
- **Crafted accessories stop at Legendary.** Bench accessories: tier I Normal, II Unique, III Rare, IV and up Legendary (the Farming
  accessory's IV to VII are all Legendary). The **Omni** is crafted, so it is Legendary, not Mythic (Skyy: Mythic cannot be crafted).
  The **Accessory Bag item** stays Unique.
- **Fabled and Mythic** are rare finds only (section 4.1). **Set** is a gear-only rarity. No 0.5 item uses any of the three.

### 1.3 Accessory Power (a build constant, not shown yet)

Locked: each accessory adds a flat +10 to +25 Accessory Power by rarity; the exact table is not set (SkyyGear-Plan locks 111-113).
Proposal, a placeholder that stays inside the locked range:

| Normal | Unique | Rare | Legendary | Fabled | Mythic |
|---|---|---|---|---|---|
| 10 | 13 | 16 | 19 | 22 | 25 |

- Each step is +3, so it is easy to guess. Fabled and Mythic are reserved for the later rare finds (4.1); the top (Mythic, 25) is 2.5
  times the bottom, as the lock implies. The old 3/5/8/12/16 draft in `docs/plans/SkyyAccessories-Plan.md` is obsolete.
- **No Accessory Power code exists yet** (inventory G6). In 0.5 the table is a **build constant** and a field in `acc:defs` (5.9). It
  is **not** a Server Setup row and not on any tooltip or page: Skyy's 2026-09-30 rule "if its not in the game yet, dont leave it in the
  list" rules out a setting or a number that does nothing (Q9).
- **The Omni double dip.** The Omni (now Legendary, 19) counts as every bench accessory at max tier, and the bag still lets bench
  accessories sit next to it (`groupOf` gives the Omni its own group). Rule for the future Accessory Power code: **while the Omni is in
  the bag, bench accessories add 0 Accessory Power** (the Omni already stands for all of them). Decide before any Accessory Power code (Q9).
- The Accessory Bag item itself adds no Accessory Power.

### 1.4 Allowed stats (every one has working code)

| Stat | Where it is applied | Status | Part |
|---|---|---|---|
| Max Health (flat) | engine stat map, key `skyyacc_health` | LIVE (the Health talismans use it) | 1 |
| Max Stamina (flat) | engine stat map, key `skyyacc_stamina` | LIVE (the Stamina talismans use it) | 1 |
| Stamina Regen % (vanilla refill runs faster) | SkyyAccessories' own top-up: `addStatValue(Stamina)` on the world thread while vanilla's own stamina regen runs (5.4.1) | NEW code; every engine call VERIFIED in bytecode and compile-tested; the feel is UNVERIFIED | 1 |
| Max Mana (% of your Mana, with a small flat floor, Q6) | engine stat map, key `skyyacc_mana` | LIVE (the Mana talismans use it) | 1 |
| Health healed every 2 s (% of max) | `addStatValue` timer | LIVE (Regeneration uses it) | 1 |
| Movement speed % | movement protocol, source `accessories.talismans`, % layer | LIVE (Speed uses it) | 1 |
| Jump height %, fall damage % | same movement source, fields `jump` and `fallDamage` | LIVE-READY (no accessory sends them yet) | 2 |
| Strength, Magical Power, Defense, Crit Chance, Crit Damage | SkyyGear, bridge `gear:extra:<uuid>` keys `str mp def cc cd` | LIVE-READY (nobody publishes it yet) | 2 |
| Life Steal; Wisdom and Fortune for Mining, Foraging, Farming | `gear:extra` key `lsteal`; `skill:bonus:<uuid>` keys `xp.<skill>`, `dd.<skill>` | LIVE-READY (wave 2, section 3) | wave 2 |

- **Stamina Regen on accessories** is Skyy's decision 4 (it lifts lock 27, "Stamina Regen armor only", for accessories only). It is
  applied by SkyyAccessories, **not** sent to SkyyGear as `gear:extra` `stam`: 5.4.1 says why and proves the engine side.
- **Combat stats on accessories.** SkyyGear 0.1's own slot table puts Defense on armor only and crits on weapons and armor only, and
  lock 125 keeps combat modifiers on combat gear. This file reads those as **gear** rules: accessories are not gear. Strength (catalog
  row) and Magical Power (lock 103) name accessories outright; lock 66 keeps Defense, Crit Chance, Crit Damage, Strength, Health and
  Speed as accessory enrichments, and lock 75 applies the same rulings to accessories. Section 8 lists this; Q11 asks Skyy to confirm.

**Kept out on purpose** (a build check fails if a booster uses one; Skyy's decision 6):

- Damage % (`dmg`): weapon only (lock 15). Flat element damage (`fEarth` and the rest): weapon only (lock 17). True Damage (`tdmg`):
  its placement is not set.
- `spd` through `gear:extra`: it would land in the flat layer next to armor. Speed uses the accessory % layer instead (Q4).
- `stam` through `gear:extra`: not used; the Stamina line applies its own regen (5.4.1), so the two never add up by accident.
- Every key SkyyGear marks "later" (Attack Speed, Ferocity, Thorns, Mana Regen and the rest). SkyyGear accepts them and silently does
  nothing, so a booster using one would lie (inventory 2.3 "Trap").

### 1.5 How the numbers were balanced

**Yardstick:** no rarity should make gear pointless. A Legendary booster should be worth roughly half of the best single gear roll of
the same stat, and well under a full set of rolled gear.

**The 4-step rescale (how the old 5-step numbers became 4).** One rule for every line: **rarity step n of 4 gets n/4 of the Legendary
number** (Normal a quarter, Unique half, Rare three quarters, Legendary all of it).
- **Legendary keeps the top number** the 5-step draft gave its top tier. That top was the number measured against the yardstick, and
  Legendary is now the top a player can reach, so no line's ceiling moves: Speed stays at 10%, Regeneration at 1.0%, Stamina at +6.
- **Health and Mana tops go from 25 to 24**, so every step is a whole number (6/12/18/24). The Mana floor becomes quarter steps of 4
  (at least +1/+2/+3/+4).
- The old middle step (T4 of 5) is simply gone; the old T1 to T3 numbers rise slightly because a quarter step is bigger than a fifth.
- **The drop lines and Feather were already four quarter steps** (+3/+6/+9/+12, +2/+4/+6/+8, +4/+8/+12/+16, 10/20/30/40, 5/10/15/20),
  so their numbers stay. Only their rarities change: the drop lines move from Unique..Fabled to Normal..Legendary.
- The new Stamina Regen part follows the same rule: +5/+10/+15/+20%.

**Per line:**

- **Combat lines (part 2).** Step values are about 12%, 24%, 36% and 48% of the SkyyGear full-power maximum for one modifier of that
  stat (Strength 25, Magical Power 25, Defense 25, Crit Chance 15, Crit Damage 30), rounded to an easy ramp: Strength, Magical Power and
  Defense +3/+6/+9/+12, Crit Chance +2/+4/+6/+8, Crit Damage +4/+8/+12/+16. So the Legendary step is:
  - about half of the best single gear roll;
  - at level 15 (Iron) a Legendary gear roll of Strength is 5.3 to 11.3 (45-95% of 25 at SkyyGear 0.1's 47.5% level factor), so
    Brawler +12 sits slightly above the best roll there; at level 20 (Thorium, 55%) the roll is 6.2 to 13.1 (SkyyGear levels:
    OPEN-QUESTIONS 2026-09-30 lock; level factor `25 + 75 x level / 50`, VERIFIED in `GearLevel.factor`). SkyyGear 0.1.1 (built,
    not live) sets full power at level 40 (`stat.levelFull` 40, VERIFIED), which lifts the level-15 roll to 6.0 to 12.6, so Brawler
    +12 then sits just under the best roll;
  - well under what a full set of rolled gear gives. The bag stays a real slice of power, but gear stays the main source.
- **What the Legendary step is worth alone** (no other gear, SkyyGear 0.1 formulas, VERIFIED: base Crit Chance 0, a crit is x2 x (1 +
  Crit Damage)):
  - Brawler +12 Strength = +12% damage on melee, arrows, thrown weapons and staff melee;
  - Runic +12 Magical Power = +12% on spell shots;
  - Stonehide +12 Defense = hits x 100/112, about 11% less damage taken;
  - Razorfang +8% Crit Chance and +16% Crit Damage = 1 + 0.08 x (2 x 1.16 - 1) = about +10.6% average damage.
- **Why the crits are one line.** Crit Damage alone does nothing without Crit Chance, and base Crit Chance is 0. As separate lines, a
  Legendary Crit Damage accessory (+16) on top of a Legendary Crit Chance accessory (+8%) added only about 2.6 points, and nothing at all
  on its own, so it would have been a trap. Paired, the line is worth about the same as Brawler for one slot. Q12 asks whether Skyy
  wants them split back into two lines.
- **Health, flat +6 per step.** One skill-tree Health node gives +10 to +20 at max, and Overall Level 100 gives +50. The Legendary step
  (+24) is about 12% of a level-100 pool (about 200 Health).
- **Stamina, flat +1.5/+3/+4.5/+6, plus Stamina Regen +5/+10/+15/+20%.**
  - Max: +1.5 is 15% more stamina for a new player (10). +6 is about 17% of a level-100 pool (about 35), less than the Acrobatics
    stamina nodes (+8). Decimals are fine: the pool is a float and the check hook allows decimals for Stamina.
  - Regen: vanilla refills 0.3 Stamina every 0.1 s = **3 per second**, only while you are not sprinting, gliding or blocking, and only
    after the short pause that follows an empty bar (`Server/Entity/Stats/Stamina.json`, VERIFIED). Legendary +20% = +0.6 per second
    while refilling: a full 16-Stamina bar (10 + 6) refills in about 4.4 s instead of 5.3 s. Never while sprinting.
  - Against gear: SkyyGear's Stamina Regen roll (`stam`, max 2 per 2 s at full power, VERIFIED) adds +1 per second **all the time**,
    sprinting included. Legendary gives 60% of that roll's refill speed and nothing during a sprint, so it is worth about half of the
    best roll: on the yardstick.
- **Mana, +6/+12/+18/+24% of your Mana, never less than +1/+2/+3/+4** (the floor). Lock 88 says dedicated mana accessories use % mana.
  Pools today (SkyySkills 0.4.7, live): 10 Mana without a caster class, Mage and Priest 20, and a wand cast costs 25. SkyySkills 0.4.8
  (built, not live; Skyy 2026-09-30) starts Mage and Priest at 30 and divides spell costs by 5 (wand 5, staff 10, spellbook 20,
  VERIFIED in its header). The % part beats the floor from about 17 Mana up at every step, so under 0.4.8 the floor only matters for
  players without a caster class. At 30 Mana the steps give +1.8/+3.6/+5.4/+7.2 (Legendary: about 1.4 wand casts under 0.4.8); with a
  cloth armor set (60 to 100 Mana) Legendary gives +14 to +24. The floor bends lock 88, so it needs Skyy's yes (Q6); setting the floor
  row to 0 gives "% only".
- **Speed, +2.5/+5/+7.5/+10%.** At Acrobatics 100 (x2.0) Legendary gives x2.20. That is +0.20 against +0.05 for the best gear Speed
  roll (flat layer), so 4x the gear roll at Acrobatics 100 and 2x at Acrobatics 0, because the accessory % layer multiplies with
  Acrobatics. This breaks the half-of-gear yardstick; the top is kept because it is the live talisman's top and Skyy asked for "+% movement
  speed". Q4 offers the flat layer (Legendary +0.10, 2x the gear roll at any Acrobatics level).
- **Regeneration, 0.25/0.5/0.75/1.0% of max Health every 2 s** (was 0.5/1/1.5/2/3 in 0.4.5; Skyy accepted "Regeneration weaker").
  Lock 20: Hytale has no natural regen, food and potions are the soft gate, and SkyBlock's "faster natural regen" stat is scrap. The
  best single gear Raw Health Regen roll is 2 per 2 s (2.4 with the Health Regen % line, VERIFIED in `build_skyygear_0.1.py`). The old
  top talisman healed 3 per 2 s at 100 Health and 6 at 200, in combat too, 1.25x to 2.5x the best gear roll. Legendary now heals 1 at
  100 Health and 2 at 200 (about 40% to 85% of the best gear roll) and stays under it up to about 240 Health. Normal heals 7.5 Health a
  minute at 100 Health: small, but visible in a game with no natural regen.
- **Feather (part 2):** Acrobatics 100 already gives -50% fall damage. The Legendary step (-40%) brings that to x0.3 (flat and % layers
  multiply, VERIFIED in `tools/skyymove.py`). Jump +5% per step (+20% at Legendary) is at most a fifth higher, far below the protocol's
  clamp (default + 20 blocks). The fall part needs SkyySkills; the jump part works without it (2.4).
- **Against Hypixel.** The ramps are as easy to guess (+3 per step, +2 per step), but each SkyWynn item is worth more, because a SkyWynn
  bag holds 18 to 60 items (not over 100) and each stat has one line.

### 1.6 Existing talismans: before and after (what changes on the part 1 deploy)

Old = SkyyAccessories 0.4.5 (five ids per line, % of your pool). New = the 0.5 defaults. The ids do not change; `_Epic` and `_Legendary`
both become Legendary (2.2).

| Line | Pool | Old: `_Common`, `_Uncommon`, `_Rare`, `_Epic`, `_Legendary` | New: Normal, Unique, Rare, Legendary, Legendary | Change |
|---|---|---|---|---|
| Health | 100 (new player) | +2, +4, +6, +8, +10 | +6, +12, +18, +24, +24 | 3x; the old `_Legendary` 2.4x |
| Health | 200 (level 100) | +4, +8, +12, +16, +20 | same | 1.5x; the old `_Legendary` 1.2x |
| Stamina (max) | 10 (new player) | +0.2, +0.4, +0.6, +0.8, +1.0 | +1.5, +3, +4.5, +6, +6 | 7.5x; the old `_Legendary` 6x |
| Stamina (max) | 35 (level 100) | +0.7, +1.4, +2.1, +2.8, +3.5 | same | about 2.1x; the old `_Legendary` 1.7x |
| Stamina (regen) | any | none | +5, +10, +15, +20, +20% refill speed | new |
| Mana | 10 (no caster class) | +0.2 ... +1.0 | +1, +2, +3, +4, +4 (the floor) | 5x; the old `_Legendary` 4x |
| Mana | 20 (Mage or Priest, 0.4.7) | +0.4 ... +2.0 | +1.2, +2.4, +3.6, +4.8, +4.8 | 3x; the old `_Legendary` 2.4x |
| Mana | 30 (Mage or Priest, 0.4.8) | +0.6 ... +3.0 | +1.8, +3.6, +5.4, +7.2, +7.2 | 3x; the old `_Legendary` 2.4x |
| Mana | 100 (cloth armor) | +2 ... +10 | +6, +12, +18, +24, +24 | 3x; the old `_Legendary` 2.4x |
| Regeneration | any | 0.5, 1, 1.5, 2, 3% per 2 s | 0.25, 0.5, 0.75, 1.0, 1.0% | 0.5x; the old `_Legendary` about 0.33x (weaker) |
| Speed | any | +2, +4, +6, +8, +10% | +2.5, +5, +7.5, +10, +10% | 1.25x; the old `_Legendary` unchanged |

So **every Health, Stamina and Mana talisman gets stronger on deploy** (Skyy's lock names this), Speed gets a little stronger except at
the top, and Regeneration gets weaker (also in the lock). No talisman of the four other lines loses anything. All numbers are one Server
Setup entry each.

---

## 2. The lines

### 2.1 Overview

| # | Family key (item ids) | Admin name (config, commands) | Line name | Item name (Rare example) | Main stat | Feed | Part | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | Vitality | Health | Health | Rare Health Accessory | +max Health, flat | stat map `skyyacc_health` | 1 | FOLD (was % of Health) |
| 2 | Endurance | Stamina | Stamina | Rare Stamina Accessory | +max Stamina, flat, and +% Stamina Regen | stat map `skyyacc_stamina` + regen top-up (5.4.1) | 1 | FOLD (was % of Stamina) + NEW regen part |
| 3 | Intelligence | Mana | Mana | Rare Mana Accessory | +% max Mana, with a flat floor | stat map `skyyacc_mana` | 1 | FOLD (bigger numbers) |
| 4 | Regeneration | Regeneration | Regeneration | Rare Regeneration Accessory | % of max Health healed every 2 s | `addStatValue` | 1 | FOLD (lower numbers) |
| 5 | Speed | Speed | Speed | Rare Speed Accessory | +% movement speed | move, % layer | 1 | FOLD (top unchanged) |
| 6 | Strength | Strength | Brawler | Rare Brawler Accessory | +Strength (melee, arrows, thrown weapons, staff melee) | `gear:extra` `str` | 2 | NEW |
| 7 | MagicPower | MagicPower | Runic | Rare Runic Accessory | +Magical Power (spell shots only) | `gear:extra` `mp` | 2 | NEW |
| 8 | Defense | Defense | Stonehide | Rare Stonehide Accessory | +Defense | `gear:extra` `def` | 2 | NEW |
| 9 | Crit | Crit | Razorfang | Rare Razorfang Accessory | +Crit Chance % and +Crit Damage % | `gear:extra` `cc`, `cd` | 2 | NEW |
| 10 | Feather | Feather | Feather | Rare Feather Accessory | less fall damage, higher jump | move, `fallDamage` + `jump` | 2 | NEW |

- **Three kinds of name.** The *family key* lives only in item ids, so no item id changes. The *admin name* is the stat word, used in
  config keys, `/accessories` commands and `acc:defs`; it never changes, even if a line is renamed. The *line name* is what players
  see, inside "<Rarity> <Line> Accessory"; it lives only in the language file, so renaming is cheap (Q14).
- Vitality, Endurance and Intelligence never appear in player or admin text, which takes two scrapped stat names out of the game:
  "Vitality is scrap" (lock 20) and "No Intelligence ID" (lock 67). The commands still accept them as aliases (5.9).
- The drop-line names do not say the stat, so the **first tooltip line always names the stat** (5.7). Brawler is not melee-only: it
  also boosts arrows, thrown weapons and staff melee, and its tooltip says so. The names Hawkeye and Bulwark were dropped because the
  draft crystal table in `docs/plans/SkyyAccessories-Plan.md` section 2 uses them for the Archer and Warrior crystals.

### 2.2 The five folded lines (the 25 talismans; part 1)

| Rarity | Item id | AP | Source words | Health | Stamina (max, regen) | Mana (floor) | Regeneration | Speed |
|---|---|---|---|---|---|---|---|---|
| Normal | `_Common` | 10 | Craft | +6 | +1.5, +5% | +6% (at least +1) | 0.25% / 2 s | +2.5% |
| Unique | `_Uncommon` | 13 | Craft, Drop | +12 | +3, +10% | +12% (at least +2) | 0.5% / 2 s | +5% |
| Rare | `_Rare` | 16 | Craft, Chest | +18 | +4.5, +15% | +18% (at least +3) | 0.75% / 2 s | +7.5% |
| Legendary | `_Epic` (and the legacy `_Legendary`) | 19 | Craft, Boss | +24 | +6, +20% | +24% (at least +4) | 1.0% / 2 s | +10% |

- **Ids stay exactly as they are:** `Skyy_Talisman_<Key>_<Common|Uncommon|Rare|Epic>` = Normal to Legendary (for example
  `Skyy_Talisman_Vitality_Epic` is the Legendary Health Accessory).
- **The old fifth id, `Skyy_Talisman_<Key>_Legendary`, folds into Legendary.** It becomes a **legacy id**, handled exactly like the 15
  older 0.2/0.3 ids (`_Talisman`, `_Ring`, `_Artifact`, which keep counting as Unique, Rare and Legendary): its item asset stays so every
  owned copy still loads, it has **no recipe**, it counts as Legendary with the same numbers, and it turns into the `_Epic` id when it
  passes through the bag (today's `modernOf`, VERIFIED). It shows the same name and look as the `_Epic` item ("Legendary Health
  Accessory"), because it is the same accessory; players never see ids. `_Epic` and `_Legendary` tie, so the bag refuses one while the
  other is equipped.
- **Why `_Epic` carries Legendary and not `_Legendary`:** the Workbench ladder `_Common` -> `_Uncommon` -> `_Rare` -> `_Epic` then
  stays exactly as it is, and only one recipe goes away (the old `_Epic` -> `_Legendary` step). Keeping `_Legendary` instead would mean
  rewriting its recipe to start from `_Rare` and retiring `_Epic`, which gives Epic owners a free step or takes one away. Players who
  crafted the old fifth step keep the top rarity and lose no strength (1.6); only the materials of that last step bought nothing extra.
- **Recipes: the Workbench ladder keeps working up to Legendary** (removing it would take away a way players already use). Legendary is
  now reached at the old fourth step's cost (Thorium tier), a placeholder until the acquisition pass (Skyy's decision 5). Drop, Chest
  and Boss are **extra** placeholder sources, so the later loot pass has hooks for these lines too (Skyy: "many will be mob drops, and
  found in the random loot chests"). Collection-gated craft tiers (lock 64) are not wired in 0.5 (section 8).
- Mana is "% of your Mana": the percent of every other flat Mana source (base Mana, Overall Level, skills, trees, armor), as today, but
  never less than the floor.
- Stamina's two parts work alone: the max part through the stat map, the regen part through SkyyAccessories' own top-up. Neither needs
  SkyyGear.

### 2.3 Drop lines (new; part 2)

| Rarity | AP | Brawler (Strength) | Runic (Magical Power) | Stonehide (Defense) | Razorfang (Crit Chance + Crit Damage) |
|---|---|---|---|---|---|
| Normal | 10 | +3 | +3 | +3 | +2% and +4% |
| Unique | 13 | +6 | +6 | +6 | +4% and +8% |
| Rare | 16 | +9 | +9 | +9 | +6% and +12% |
| Legendary | 19 | +12 | +12 | +12 | +8% and +16% |
| Source words, Normal to Legendary | | Drop, Combine, Craft, Boss | Chest, Combine, Craft, Boss | Drop, Combine, Craft, Boss | Chest, Combine, Craft, Boss |
| Legendary alone (1.5) | | +12% damage | +12% spell damage | about 11% less damage taken | about +10.6% average damage |

- Ids: `Skyy_Talisman_<Key>_T1` to `_T4` = Normal to Legendary (section 5.3), for example `Skyy_Talisman_Strength_T3` is the Rare
  Brawler Accessory and `Skyy_Talisman_Crit_T4` the Legendary Razorfang Accessory.
- What the stats do in SkyyGear 0.1 (VERIFIED, inventory 2.3): 1 Strength = +1% damage on melee, arrows, thrown weapons and staff melee;
  1 Magical Power = +1% on spell shots (wand, staff, spellbook); Defense cuts hits to `100 / (100 + Defense)`; nobody crits without gear
  or accessories (base Crit Chance is 0), a crit is x2 and Crit Damage raises that (+100 = x4); over 100% Crit Chance is overcrit.
- Offence stats only count with a gear weapon or bare hands (a held tool or block gives none), and never with a weapon above your level.
  Defense only counts against hits from a mob or player. SkyyGear's Server Setup switch "Gear stats in combat" (`part.stats`) must be
  on; the bag page says so when it is off (5.4).
- Source words (placeholders, for the later pass): **Drop** = a normal mob drop; **Chest** = a world loot chest; **Combine** = 4 copies
  of the rarity below (turns duplicate drops into progress, Hypixel's Master Skull and Scarf's pattern); **Craft** = the rarity below plus
  a drop from a harder mob; **Boss** = a boss drop. None of them ever makes a Fabled or Mythic item (4.1).

### 2.4 Feather (new comfort line; part 2)

| Rarity | AP | Fall damage | Jump height | Source words |
|---|---|---|---|---|
| Normal | 10 | -10% | +5% | Craft |
| Unique | 13 | -20% | +10% | Craft |
| Rare | 16 | -30% | +15% | Chest |
| Legendary | 19 | -40% | +20% | Chest |

- Ids `Skyy_Talisman_Feather_T1` to `_T4`. Jump Height on accessories is allowed (lock 28). Hypixel has no jump accessory, so this one
  is a SkyWynn original.
- **Needs SkyySkills for the fall part.** Fall damage is applied only by SkyySkills (it owns `stat:owner:fallDamage`, VERIFIED).
  Without SkyySkills the fall part does nothing; the jump part still works, because SkyyAccessories writes jump through the movement
  protocol itself. The bag page says "fall damage needs SkyySkills" when it is missing, like the combat lines.
- Every rarity has a jump part, so Normal and Unique do something you notice even with a small fall bonus.
- INFERRED: the Acrobatics double jump uses the live `MovementSettings.jumpForce`, so Feather probably lifts the double jump by the same
  percent. Part 2 test step 3.

---

## 3. Wave 2 (the same engine, no new engine work; SkyyAccessories 0.5.2, after part 2 passes)

| Family key | Line name | Stats per rarity | Rarities | Feed |
|---|---|---|---|---|
| Mining | Prospector | Mining Wisdom +3/+6/+9/+12% XP; Mining Fortune (double drops) Rare +3%, Legendary +6% | Normal to Legendary | `skill:bonus` `xp.mining`, `dd.mining` |
| Foraging | Woodsman | same numbers for Foraging (Fortune doubles logs only) | Normal to Legendary | `xp.foraging`, `dd.foraging` |
| Farming | Harvester | same numbers for Farming | Normal to Legendary | `xp.farming`, `dd.farming` |
| LifeSteal | Leech | **waits for Skyy's Life Steal shape**: the numbers are open and must not be invented (SkyyGear-Plan open item 9, catalog row) | Normal to Legendary | `gear:extra` `lsteal` |

- Wisdom is sent as a fraction under one source name, `accessories.boosters` (0.03 = +3%). SkyySkills clamps the sum (XP 0 to 5,
  double drops 0 to 1, VERIFIED); `skill:bonus` is a per-source map, as SkyyTrees uses it with source `trees`.
- Checked 2026-10-06: Rare +3 / Legendary +6 stays; accessory Fortune cap 10 (`accessories.fortune.cap`); no swing line (see `research/cloud/Gathering-Numbers-Reconciled.md`).
- Leech gets its numbers once Skyy sets the Life Steal shape; when it does, keep its Legendary step within the 48%-of-gear-max rule (1.5).
  (The old draft ran Leech from Rare to Fabled; Skyy's lock puts every line on Normal to Legendary.)
- Cooking Wisdom works the same way if Skyy wants a cooking line.

---

## 4. Later

### 4.1 Later: rare finds (Fabled and Mythic)

- **Skyy (LOCKED 2026-09-30):** "mythic and fable are rare finds/drops you cant craft". A booster line upgrades Normal -> Unique -> Rare
  -> Legendary and stops there. **Fabled and Mythic accessories are never crafted, never an upgrade result (no Craft, no Combine, no
  Workbench), and never a step of a line.** A few special ones come later; **none are in this build.**
- **When:** with the drop tables (mob kill hook and first-open chest roll, 4.2), because a rare find needs a place to drop from. Each
  special accessory is designed then (name, effect, drop source), one at a time, with Skyy.
- **Suggested shape (for that later pass, not decided):** each rare find gets its **own family key**, so it is its own line of one and
  the one-per-line rule stays simple; its stats follow the same allowlist (1.4), so it never carries a stat that does nothing.
- **What 0.5 prepares so they slot in with no migration:**
  - The six quality assets `Skyy_Acc_Normal` to `Skyy_Acc_Mythic` all ship in part 1 (5.2), Fabled and Mythic unused. Adding quality
    assets shifts the index of every quality that loads after them (5.2 known gaps), so shipping all six now means one shift instead of
    two. No list shows the unused two: SkyyAuctions builds its rarity filter from the gear ladder plus vanilla quality names and skips
    every quality id starting with `Skyy_` (VERIFIED, `tierList` in `build_skyyauctions_0.1.2.py`).
  - Accessory Power 22 (Fabled) and 25 (Mythic) are reserved in the build constant (1.3).
  - The `DISPLAY` rarity array has all six names; the booster table and every recipe stop at Legendary (build check, section 6).
  - `acc:defs` and `acc:fn:give` carry the rarity as text, so a later rare find needs no bridge change.

### 4.2 Waits for engine work, a missing system or a Skyy call

| Idea | Why it waits | What it needs |
|---|---|---|
| Mana Regen line | not wired (LATER). Vanilla already refills about 5 Mana a second (`Mana.json`: 1 every 0.2 s, VERIFIED), so a small trickle adds little while pools are 10 to 60 | the Stamina Regen top-up (5.4.1) pointed at Mana's regen entries; worth it once pools or spell costs grow |
| Attack Speed, Ferocity | no mechanism (LATER) | the swing-speed system (`research/Swing-Speed-Spec.md`) and code-dealt extra hits |
| Mining Speed and Chopping Speed lines | SkyyTrees reads no outside source | a SkyyTrees patch that accepts outside bonuses |
| Breath (oxygen) and swim speed lines | locked as accessory effects (locks 61-62) but no Skyy code touches them; UNVERIFIED | engine checks of the Oxygen stat and swim settings |
| Dodge Chance, -% Spell Cost, Ability Damage, raw spell damage | no dodge-chance stat, no spell system | those systems |
| Combat Wisdom, XP Bonus, Loot Bonus, Loot Quality, Stealing, Trophy Hunter, coins | nothing reads them | readers in SkyySkills and the drop code |
| Mob-type protection and damage lines (undead, spiders, beasts, void) | no mob-family tags or damage hook | a mob family table and a SkyyGear hook |
| Day and night pair (Strength by night, Defense by day) | small new code that reads world time | a time check in the effect tick |
| Out-of-combat-only Regeneration | no "last hit" timestamp in SkyyAccessories | a damage listener or a SkyyGear bridge key |
| Growing accessories (a kill counter or collection counter on the item) | needs item metadata and counters | metadata storage, like SkyyGear rolls |
| Fabled and Mythic rare finds | Skyy: later, not in this build | section 4.1 and the drop tables below |
| Accessory Power sum, powers (Balance and the rest), tuning, enrichments | not built (inventory G6) | SkyyAccessories 0.6 and later (Plan section 4); the Omni rule in 1.3 |
| Drop tables (mobs and chests), Combine recipes, collection gating of craft tiers (lock 64) | no Skyy mod adds mob or chest drops (inventory G7, G14); Skyy's decision 5 | a kill hook (SkyyCollections `CollKillSys` or SkyyGear `GearDeathMark` pattern) and a first-open chest roll (SkyyExploration pattern) calling `acc:fn:give` (5.9) |
| Bag slot unlocks (collections, skills, coins) | not built | Plan section 3, rebased (5.5) |
| Accessory stats in the HUD and stat screens | `gear:fn:stats` leaves `gear:extra` out on purpose | a SkyyGear total that includes it |
| More than one `gear:extra` writer | it is one string per player (inventory G4) | SkyyGear accepts a map of source to string, like `move:<uuid>` |
| An AH sub-category by booster stat | SkyyAuctions files every `Skyy_Talisman_*` under ACCESSORIES | an optional SkyyAuctions filter; the first tooltip line names the stat meanwhile |

---

## 5. How it fits the bag and the pack

### 5.1 The 25 talismans: fold them in (confirmed by Skyy; nothing is lost)

- They **become** the five folded lines. Same item ids, the same Workbench recipes up to Legendary, same one-per-family swap. What
  changes: the names ("<Rarity> Health Accessory" and so on), the rarity look (5.2), the numbers (2.2, 1.6), Health and Stamina become
  flat, Stamina gains its regen part, and the old `_Legendary` id becomes a legacy id that counts as Legendary (2.2).
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
    `2,4,6,8,10`) gives way to the new default. An **edited** five-number list is carried over to `boost.Mana.pct`,
    `boost.Regeneration.pct` or `boost.Speed.pct` as **its 1st, 2nd, 3rd and 5th numbers** (the admin's top stays the top, the same rule
    as the rescale in 1.5); the dropped 4th number is written to `config-changes.log`. A list that is not five numbers is dropped and
    logged.
  - `bonus.Vitality`, `bonus.Endurance`: their unit changed (% to flat), so an edited value cannot carry over. It is dropped and
    **written to `config-changes.log`** with its old value, so the admin can redo it by hand. `boost.Stamina.regenPct` is new and always
    gets the build default.
  - `slots=9` becomes 18 in this one run (Skyy's decision 2). 9 was the hard maximum in 0.4.x, so a deliberate 9 cannot be told apart
    from the default; an admin who wants 9 sets it again once and it stays.
  - The old `bonus.` lines leave the file in the same write, and all part 1 `boost.` entries are appended (build defaults where nothing
    carried over). Part 2 appends its own entries on its first start when they are missing (no `slots` change, no removal).
  - Every changed, carried or dropped value gets one line in `config-changes.log` in the kit's format (who `migration-0.5`, via
    `migrate`) and one server INFO line.
- **One-time chat notice** (Server Setup switch, default on), with no scrapped names in it: "Your talismans are now accessories: Health,
  Stamina, Mana, Regeneration and Speed Accessory, in the gear rarities Normal, Unique, Rare and Legendary, with new numbers. Stamina
  now also refills faster. /accessories lines shows every line."
  - Sent only to players who already have a bag file (they used accessories before 0.5).
  - `PlayerReadyEvent` fires on every world switch and this mod has no event listener today, so 0.5 adds one listener and stores a
    per-player "notice seen" flag in a file (as SkyySacks does). The notice goes out once per player, ever.

### 5.2 Rarity: move accessories to the gear ladder (Skyy: "the same rarity tiers as weapons and armor")

- **Six quality assets in the jar:** `Skyy_Acc_Normal`, `_Unique`, `_Rare`, `_Legendary`, `_Fabled`, `_Mythic` (the last two unused
  until the rare finds, 4.1). Never a bare rarity word as an id (other mods in Skyy's folders ship `Mythic`; Bag-Restructure-Spec 1.4).
  Colours and frame art are the same as SkyyGear's `Skyy_Gear_*` table, and page colours come from the kit (`SUI.RARITY`,
  `SUI.RARITY_ORDER`). The field set must equal vanilla `Common.json` (the SkyyGear build check). QualityValue 1 to 6 stays below
  SkyyAuctions' "technical" limit of 8, so they stay tradeable, and SkyyAuctions' `qPretty` already handles `Skyy_*` qualities
  (VERIFIED). SkyyAccessories ships its own set, because every Skyy mod must work alone.
- **Labels:** write each quality label under both `general.qualities.<id>` and `server.general.qualities.<id>`, as SkyySacks does
  (SkyyGear writes only the first).
- **Mapping:**
  - Folded lines (ids): `_Common` Normal, `_Uncommon` Unique, `_Rare` Rare, `_Epic` Legendary, legacy `_Legendary` Legendary. Legacy
    `_Talisman` Unique, `_Ring` Rare, `_Artifact` Legendary.
  - New lines: `_T1` to `_T4` = Normal to Legendary.
  - Bench accessories: I Normal, II Unique, III Rare, IV and up Legendary (crafted accessories stop at Legendary; 0.4.5's `QUAL` went up
    to vanilla Legendary at T5+, VERIFIED).
  - The **Omni: Legendary** (it is crafted, so not Mythic). The **Accessory Bag item** (`Skyy_Accessory_Bag`): Unique.
- **Code: id words and display rarities are separate arrays.** 0.4.5 uses one `RARITY` array for id parsing (`tierOf`), id building
  (`modernOf`), names, lang, colours and error text. Under the gear ladder that breaks: the word "Epic" in an id now means Legendary on
  screen, and "Legendary" in an id is a legacy word. 0.5 keeps:
  - an `ID_WORD` array (Common, Uncommon, Rare, Epic = tiers 1 to 4) only for parsing and building ids;
  - the legacy words Talisman, Ring, Artifact **and Legendary**, parsed to tiers 2, 3, 4 and 4, and rebuilt by `modernOf` into the
    `ID_WORD` id of that tier (`_Legendary` -> `_Epic`);
  - a `DISPLAY` array (Normal, Unique, Rare, Legendary, Fabled, Mythic) plus a per-tier rarity index in the booster table for everything
    players see. `AccDefs.rarityOf` returns 1 to 4 for every 0.5 item (5 and 6 reserved for 4.1).
- **Restamp.** Saved stacks keep the quality index they were saved with (VERIFIED, Bag-Restructure-Spec 1.4), so old stacks must be
  restamped with `withQuality` (the SkyySacks 0.7.7 pattern, spec 5.6):
  - It runs inside `AccEffects.tick`, which is on the world thread, every 5th run per player. It must **not** run in `AccTick`: that
    one is scheduled on `HytaleServer.SCHEDULED_EXECUTOR`, and inventory writes must be on the world thread.
  - Only when `AccStore.moveBlock(u) == null` (no bag move in progress for that player).
  - It covers every `Skyy_Talisman_*` and `Skyy_Accessory_*` stack in storage, hotbar and backpack whose index differs from its item's,
    **plus the bag item by name**, because `AccDefs.isAccessory` leaves `Skyy_Accessory_Bag` out. It changes the quality only, never the
    id or the count (count before and after, as every inventory write does).
  - The bag file stores ids only, so bag contents need nothing.
- **Known gaps** (the builder states them in the 0.5 notes):
  - The 2026-09-30 in-game probe (OPEN-QUESTIONS, "Seen in game") found that item slots with rarity backgrounds work on our pages,
    but rarity **frames** did not show. Expect the name colour and rarity label to show and the frame possibly not (UNVERIFIED, the same
    open test as SkyyGear and the bags). The rarity word is in the item name and on the bag page either way (1.2).
  - Stacks outside a player's own inventory (SkyyVault, auction listings, trade windows, chests) keep the old look until they are
    taken out into an inventory, where the restamp catches them. Nothing is lost; only the look is stale.
  - Six new quality assets shift the index of every quality that loads after them. Other mods' saved stacks (for example Extended
    Backpacks' Mythic, SkyyVault items) may show a shifted look, as already happened when SkyyGear and SkyySacks added theirs. Part 1
    test 1.
  - Rolling back to 0.4.5 leaves restamped stacks pointing at `Skyy_Acc_*` indexes that no longer exist (5.3).
- INFERRED: items that name a plugin quality load fine (SkyySacks 0.7.7 bags have used `Skyy_Bag_*` in their item files since
  2026-09-28).

### 5.3 Item ids and roll-back

- **New lines (part 2): `Skyy_Talisman_<Key>_T<n>`**, n = 1 to 4. Folded lines keep `Skyy_Talisman_<Key>_<Common..Epic>` plus their
  legacy ids (5.1, 2.2).
- Why the `Skyy_Talisman_` prefix: every current reader already treats it as a stat accessory. SkyyAuctions files it under
  ACCESSORIES, SkyyMenu counts it through `acc:tal`, and `AccDefs.familyOf` and `groupOf` already work for any key (VERIFIED). The word
  "Talisman" never reaches a player: ids are hidden, and the build check keeps it out of every player string.
- **Not `Skyy_Accessory_<Family>_<Tier>`**: that prefix means "bench accessory". `AccDefs.benchOf` would turn the family into a fake
  bench id, publish it in `acc:has`, and SkyySacks would draw a fake `/craft` tab. 0.2 had exactly this bug.
- **Not the words Talisman, Ring, Artifact or Legendary** at the end of a new id: they are legacy words, and `modernOf` would rebuild
  them into another id.
- Parse order in 0.5: a `_T<digits>` tail first, then the `ID_WORD` words, then the legacy words. Keys: CamelCase, no underscore, not
  ending in an id word or legacy word.
- **Roll-back.** 0.4.5's `slotsK` reads only `slot0` to `slot8`, and `saveK` rewrites the whole bag file from that 9-slot array, so the
  next equip, unequip, `putK` or `stashK` on 0.4.5 would delete slots 10 to 60 for good. So 0.5 does two things:
  - **Slots 0 to 8 stay in `bags/<pkey>.properties`** (the file 0.4.5 knows, same format), and **slots 9 to 59 go into
    `bags/<pkey>.more.properties`**, which 0.4.5 never reads or rewrites. After a roll-back the extra slots are hidden, not lost, and
    they come back with 0.5. 0.5 puts nothing else into the main file that 0.4.5 would drop on its rewrite.
  - **"Do not roll back below 0.5"** goes into the 0.5 deploy notes (the HANDOFF line whoever logs the deploy writes), as done for
    other mods. Reasons that the second file does not fix: restamped stacks point at `Skyy_Acc_*` quality indexes that 0.4.5 does not
    ship (stale look; UNVERIFIED whether an out-of-range index is safe), and part 2's new-line items in inventories are item ids 0.4.5
    does not define (UNVERIFIED how the game treats them). A `slots=18` value is harmless on 0.4.5 (it clamps to 9 with a warning,
    VERIFIED). New-line items inside the bag are safe: 0.4.5 ignores a family it does not know (`familyIndex` returns -1). A `_Legendary`
    talisman that 0.5 rebuilt into `_Epic` is a normal 0.4.5 item (its old Epic).

### 5.4 How the stats reach the game (one generic effect tick, world thread, once a second per player)

The five hard-wired arrays (`VIT END INT REG SPD`) become **one booster table**: family key, admin name, line name, feed, stats, tier
ids, rarity per tier, numbers per tier, look per tier, source words per tier. The tick finds the best rarity of each line in the bag (the
active profile's bag, `AccStore.pkey`), adds up each stat, and sends it.

**Javassist limits for the table (tested by the feasibility review with `tools/javassist.jar`):** `new float[][] {...}` and
`new String[][]` both fail to compile, and so do labeled `break` and `continue`. No live script uses `[][]`. Use flat 1-D arrays
(index = line x 4 + tier) or a text table parsed at class init, and loops without labels. 1-D arrays, `switch` on an int, `long` maths
and large initializers compile.

| Feed | Exact call | Rules | Part |
|---|---|---|---|
| Health, Stamina max (flat) | `putModifier(stat, "skyyacc_health" / "skyyacc_stamina", StaticModifier(MAX, ADDITIVE, amount))` | removed at 0 and when the line or mod is off. Never MULTIPLICATIVE (the engine adds every multiplicative amount into one factor) | 1 |
| Stamina Regen (%) | `addStatValue(Stamina, rate x pct / 100 x seconds)` while vanilla's own positive stamina regen entry passes its conditions | 5.4.1 | 1 |
| Mana (% with floor) | same as Health, key `skyyacc_mana`, amount = max(round(flatMax x pct) / 100, floor) | flatMax leaves out every `skyyacc_` key (it includes the SkyyGear armor lock, VERIFIED) | 1 |
| Regeneration | `addStatValue(Health, max x pct / 100)` every `regenEverySeconds` while 0 < Health < max | today's code; works in combat | 1 |
| Speed, jump, fall | `MoveSync.post(u, "accessories.talismans", "pct", speed, jump, fall)` then `sync` | one source for the whole bag (the existing name, so nothing else changes). Fractions: 0.10 = +10%, fall -0.40 = 40% less (the config stores the magnitude, the tick adds the minus). All zero removes the entry. Part 1 sends jump and fall as 0 | 1 (speed), 2 (jump, fall) |
| Combat stats | `gear:extra:<uuid>` = one String, for example `"cc:4,cd:8,def:6,mp:3,str:9"` | whole numbers only (SkyyGear floors each part); one summed part per key; written only when the text changes; removed when empty, on leave, and republished on a profile switch (`profile:epoch`). Foreign text: see below | 2 |
| Wisdom, Fortune (wave 2) | `skill:bonus:<uuid>` map, source `accessories.boosters` = `{"xp.mining": 0.03, "dd.mining": 0.03}` | outer map created with `putIfAbsent`; the source's map is replaced whole when it changes | wave 2 |

- **Foreign `gear:extra` text (part 2).** We are the only writer until SkyyGear accepts a map. If the bridge holds text we did not
  write, overwrite it and log one WARN for that player. If the text changes again within 5 s after our overwrite (a second writer, even
  a test one), **stop writing for that player** until they relog or switch profile, and log one more WARN. Two writers never fight
  every second.
- **One try per publisher.** In 0.4.5 one `try` wraps the whole tick with one log-once flag, so a bug in new code would stop the speed
  sync and the stat modifiers too. 0.5 gives each publisher its own try and log-once flag: stat pools, Stamina Regen, Regeneration,
  movement, the restamp, and in part 2 `gear:extra`.
- **No stale bridge keys (part 2).** `publishOnline` removes our `gear:extra:<uuid>` for every player who is no longer online, and
  `shutdown` removes it for every player we wrote (0.4.5 prunes only its local maps, so the key would outlive the player and the plugin).
- **SkyyGear present and switched on (part 2).** Detect SkyyGear by its bridge keys (`gear:gates` or a `gear:fn:*` function). Read its
  `part.stats` switch through `config:fn:SkyyGear` `get` (a legal `java.lang` bridge call). The bag page shows "Combat stats need
  SkyyGear" when it is missing and "SkyyGear's 'Gear stats in combat' is off" when the switch is off, instead of silently doing nothing.
  Feather's fall part shows "needs SkyySkills" the same way.
- **Equipping does not raise current Health or Stamina**, only the maximum; the bar fills by normal means. Do not "fix" this by adding
  the difference on equip: unequipping and re-equipping would then heal for free.
- All cross-mod calls go through `skyy.bridge` with `java.lang` types only.

### 5.4.1 Stamina Regen: what is live today, how SkyyAccessories applies it, and the engine proof

**Is Stamina Regen a live effect today? Only inside SkyyGear.** (All VERIFIED by reading the scripts.)
- SkyyGear 0.1 (live), 0.1.1 and 0.1.2 (built): `stam` "Stamina Regen" is a LIVE stat (the last of the 21 live keys, max 2 at full
  power, armor only). `GearFx.second` (world thread, once a second) adds the summed `stam` of the worn armor **plus `gear:extra`** to
  current Stamina every `regen.periodMs` (2000 ms) as a flat amount, capped at max, skipped for a dead player, only while `part.stats`
  is on. It runs no matter what the player is doing, sprinting included.
- SkyySkills 0.4.7 (live) and 0.4.8, SkyyTrees 0.2.5: no Stamina Regen. They only add max Stamina (Second Wind, Marathon, Endurance,
  Miner Stamina) and SkyySkills sets the vanilla `StaminaRegenDelay` stat after a double jump (a regen pause, 0.3 s by default).

**Why the Stamina line does not send `stam` through `gear:extra`:**
1. It would need SkyyGear with `part.stats` on. The Stamina line is a folded line that works alone today; it must keep doing so.
2. SkyyGear floors each `gear:extra` part to a whole number per 2 s. A 4-step ramp under the yardstick (Legendary about half of the 2 per
   2 s roll = 1 per 2 s) would floor Normal to Rare to 0 or 1.
3. SkyyGear's regen also runs while sprinting. Vanilla sprinting drains 0.1 Stamina every 0.1 s = 1 per second (`Stamina.json`,
   VERIFIED), and 2 per 2 s is exactly 1 per second, so it cancels sprint cost: it is a sprint extender, not a faster refill.

**Why not "EntityStatMap regen modifiers": a per-player regen modifier does not exist in the engine.** (VERIFIED in HytaleServer.jar
bytecode.)
- `EntityStatMap.putModifier(int, String, Modifier)` stores a `Modifier` whose `ModifierTarget` can only be `MIN` or `MAX` (the enum has
  exactly those two), and `EntityStatValue.computeModifiers` applies them to the stat's min and max only. That is how the max-Stamina
  part works; it cannot touch regen.
- Regen multipliers exist only as `RegeneratingModifier` objects inside assets: `EntityStatType$Regenerating.getModifiers()` (the
  `Stamina.json` stat type, shared by every entity; `RegeneratingValue.regenerate` multiplies the amount by each modifier whose
  conditions hold) and `ItemArmor.getRegeneratingValues()` (extra regen entries on **worn armor** items, which
  `EntityStatsSystems$Regenerate.tick` adds for each armor slot). Changing the stat type would change every player and needs a copy of
  vanilla `Stamina.json` (never copy vanilla files into git, and another pack overriding it would clash); accessories in the bag are not
  worn armor.

**How SkyyAccessories applies it (part 1, inside `AccEffects.tick`, the `EntityTickingSystem` on Player that already runs the
Regeneration heal on the world thread):**
1. The clock: `now = ((TimeResource) store.getResource(TimeResource.getResourceType())).getNow()`, exactly how the engine's own
   `EntityStatsSystems$Regenerate.tick` gets the time it hands to regen conditions.
2. The rate vanilla is refilling at right now: take the Stamina value `v = m.get(DefaultEntityStatTypes.getStamina())` and loop over
   `v.getRegeneratingValues()`. For each `rg = rv[i].getRegenerating()` with `rg.getRegenType() == RegenType.ADDITIVE`,
   `rg.getAmount() > 0` and `rg.getInterval() > 0`, if `Condition.allConditionsMet(cb, ref, now, rg)` is true, add
   `rg.getAmount() / rg.getInterval()` to the rate. In vanilla that is one of the two positive entries (normal and overdrawn, which
   exclude each other), 0.3 / 0.1 s = 3 per second. The Creative entry is PERCENTAGE and is skipped; the sprint and glide drains are
   negative and are skipped.
3. The top-up: `amount = rate x pct / 100 x seconds`, where `seconds` is the time since the last top-up on the 1 s effect clock (clamped
   to 0..2 s, like SkyyGear's regen clock). Skip when Health <= 0 or Stamina >= max; cap at max; then `m.addStatValue(stamina, amount)`.
   The engine's own regen ends in the same `EntityStatMap.addStatValue(int, float)` call.
4. Never call `RegeneratingValue.shouldRegenerate` or `regenerate`: they advance the engine's per-entity regen timer
   (`remainingUntilRegen`). `Condition.allConditionsMet` is `public static` and is exactly the check `shouldRegenerate` makes after its
   timer step; the engine passes the CommandBuffer as the accessor, as step 2 does. The conditions only read components: Sprinting and
   Gliding read `MovementStatesComponent`, Wielding reads `DamageDataComponent.getCurrentWielding()`, Stat reads the stat value.
5. Its own try and log-once flag (5.4). Line switch off, the mod off, or `Stamina.regenPct` all 0 = nothing runs.

**Proof, 2026-09-30:** every class and method above was read in HytaleServer.jar bytecode (`RegeneratingValue`,
`EntityStatType$Regenerating` and its `RegenType` enum ADDITIVE and PERCENTAGE, `RegeneratingModifier`, `Condition`,
`Modifier$ModifierTarget`, `EntityStatValue`, `EntityStatMap`, `TimeResource`, `EntityStatsSystems$Regenerate`, the Sprinting, Gliding,
Wielding and Stat conditions), and a method with exactly steps 1 to 3 compiled with `tools/javassist.jar` against HytaleServer.jar (in
memory only; the scratch folder was deleted). Part 1's build adds `B.probe` checks for each engine call so an engine update fails the
build instead of the tick.

**What it means in play:** the bonus flows exactly when vanilla's refill flows. It stops while sprinting, gliding or blocking (Wielding
is INFERRED to be the block/guard interaction), during the pause after an empty bar and during SkyySkills' double-jump pause, so it
never makes sprinting free. If a pack changes the regen numbers in `Stamina.json`, the bonus stays a percent of whatever the regen is.
It adds to SkyyGear's Stamina Regen (a different mechanism), and the two never double-count because the line sends no `stam`.

**Known limit:** the conditions are sampled once a second, so a second that is half sprint and half refill gets the whole second's
bonus or none: at most 0.6 Stamina at Legendary, and it averages out. If the in-game test shows it feels uneven, the refinement is to
count condition-met time on every engine tick and pay it out on the 1 s clock (no other change). UNVERIFIED in game: the feel, and that
the conditions answer the same from our system as from the engine's (they read the same components).

**Side note for SkyyGear (outside this spec, not changed here):** one full-power `stam` roll (2 per 2 s) equals the vanilla sprint
drain, so it makes sprinting free, and several armor pieces can each roll it. Worth a look in SkyyGear's own balance pass.

### 5.5 Bag size and the bag page

- **Storage:** `CAP` 9 becomes 60, split over two files (5.3): `slot0` to `slot8` in `bags/<pkey>.properties`, `slot9` to `slot59` in
  `bags/<pkey>.more.properties` (both written tmp + move; old files simply have no second file, so no migration). `CAP` is storage
  only.
- **Slots (Skyy's decision 2):** the config row `slots` gets a default of **18** and a maximum of **60**. It still limits new equips
  only.
  - 18 means players choose: the Omni (which stands for all 11 bench accessories) plus the 10 lines fit with 7 spare, but 11 bench
    accessories plus 10 lines (21, or 22 with the Omni) do not, until unlocks exist.
  - `docs/plans/SkyyAccessories-Plan.md` section 3 (a draft) starts at 9 and adds +51 from collections (+12), skills (+20), coins (+16) and quests
    (+3), capped at 60. Starting at 18, those sources are **rebased to +42** so the cap stays 60 (for example coins +16 to +10 and
    collections +12 to +9); the exact split is set when unlocks are built.
- **Page:** the vanilla-kit window grows from 1210 x 780 to about **1210 x 950** (fits 1080 high). The BAG SLOTS well shows 9 rows per
  page (new constant `PAGE_ROWS = 9`) and the inventory list 6 rows per page, each with the kit's pager (the in-game probe of
  2026-09-30 showed the pager working). Each row shows the name and the rarity word in the rarity colour (today's 18 px name + 15 px
  rarity line). The Bonuses well lists up to 12 short lines in two columns (for example "+12 Strength", "+10% Speed", "+20% Stamina
  Regen", "-40% fall damage"), using the live config numbers.
  - `ACC_COLS_H` must be computed from `PAGE_ROWS`, not `CAP` (from `CAP = 60` the page would be far too tall). Update `fit()` and the
    test-harness asserts that expect `(1210, 780)`.
  - The bag item's description no longer prints `CAP` ("Holds up to 60"); it uses a neutral text ("Holds your accessories").
- Unlocking slots through collections, skills and coins stays for later (Plan section 3, rebased as above).

### 5.6 Looks (vanilla items by reference, one look per rarity)

Each rarity copies the **model** and **icon paths** of a vanilla item, as the talismans do today (`visual_of`, `icon_of`). Nothing is
copied into the jar. Every item named below was checked in Assets.zip (read only): every item exists, every ingredient has its own
model, and no two rarities of a line share an icon (VERIFIED, both reviews re-checked all looks).

**Folded lines:** model = the line's crystal fragment item for every rarity (crystal clusters and gems are blocks, with no item model).
Icons: Normal crystal fragments, Unique small cluster, Rare large cluster, Legendary gem. So each rarity gets its own icon; today
Common-Uncommon share one icon and Rare-Legendary share another. The legacy ids use the look of the rarity they count as (the legacy
`_Legendary` looks exactly like `_Epic`).

| Line | Colour (Normal `Ingredient_Crystal_<C>`, Unique `Rock_Crystal_<C>_Small`, Rare `Rock_Crystal_<C>_Large`) | Legendary icon |
|---|---|---|
| Health | Red | `Rock_Gem_Ruby` |
| Stamina | Yellow | `Rock_Gem_Topaz` |
| Mana | Blue | `Rock_Gem_Sapphire` |
| Regeneration | Green | `Rock_Gem_Emerald` |
| Speed | Cyan | `Rock_Gem_Zephyr` |

**New lines (part 2)** (model and icon from the named item unless a model is given):

| Line | Normal | Unique | Rare | Legendary |
|---|---|---|---|---|
| Brawler | `Ingredient_Bone_Fragment` | `Ingredient_Sinue_Cindersinue` | `Ingredient_Fire_Essence` | `Ingredient_Voidheart` |
| Runic | `Ingredient_Crystal_Purple` | icon `Rock_Crystal_Purple_Small` | icon `Rock_Crystal_Purple_Large` | icon `Rock_Gem_Voidstone` |
| Stonehide | `Ingredient_Crystal_White` | icon `Rock_Crystal_White_Small` | icon `Rock_Crystal_White_Large` | icon `Rock_Crystal_Iridescent_Large` |
| Razorfang | `Ingredient_Crystal_Pink` | icon `Rock_Crystal_Pink_Small` | icon `Rock_Crystal_Pink_Large` | icon `Rock_Crystal_Iridescent_Medium` |
| Feather | `Ingredient_Feathers_Light` | `Ingredient_Feathers_Blue` | `Ingredient_Ice_Essence` | `Ingredient_Motes_Light` |

- Crystal-line rarities without their own model use that line's crystal fragment model. The Diamond gem stays the Omni's icon only.
- Spares (checked, unused): `Rock_Crystal_<C>_Medium` for the five folded colours (the old T3 icon), `Ingredient_Feathers_Dark`,
  `Ingredient_Feathers_Red`, `Ingredient_Lightning_Essence`, `Rock_Crystal_Iridescent_Small`.
- Wave 2 suggestions (checked too): Prospector `Ingredient_Stud_Iron`, `Ingredient_Powder_Boom`, `Ingredient_Bar_Thorium`,
  `Ingredient_Bar_Onyxium`; Woodsman `Ingredient_Tree_Bark`, `Ingredient_Tree_Sap`, `Ingredient_Life_Essence`,
  `Ingredient_Life_Essence_Concentrated`; Harvester `Ingredient_Fibre`, `Ingredient_Life_Essence_Wheat`,
  `Ingredient_Life_Essence_Pumpkin`; Leech `Ingredient_Sac_Venom`, `Ingredient_Chitin_Sturdy`, `Ingredient_Void_Essence`.
- An accessory can look like a stack of the ingredient it borrows (today's talismans look like crystals). The rarity colour, the name and
  `MaxStack 1` tell them apart. Our own art can replace any row later.

### 5.7 Tooltips (vanilla look)

- The name takes the quality colour, and the quality adds its rarity label. The description uses vanilla item-text markup: line breaks,
  `<color is="#ffffff">` for the key number, `<i>` for a flavour line. VERIFIED in `Server/Languages/en-US/server.lang`: of the 331
  vanilla item descriptions (548 description keys in all), 143 use at least one of these (101 colour, 38 italic, 101 line breaks).
- In the language file a line break is the **two characters `\n`** on one line. A real newline would break the `"\n".join(lang)` file.
- Parts, in order: **the stat line first** (the line name alone does not say the stat), what it affects, any requirement, the
  one-per-line rule with the next rarity's name (or "the top rarity" at Legendary), a flavour line. No mod names: players do not know
  "SkyyGear". Examples (shown with the line breaks rendered):

```
Unique Brawler Accessory
<color is="#ffffff">+6 Strength</color> while in your Accessory Bag.
More damage with melee, arrows, thrown weapons and staff melee.
Works with gear weapons or bare hands.
Only your best Brawler Accessory counts. Next: Rare Brawler Accessory.

<i>Scuffed wraps from a hundred fights.</i>
```

```
Legendary Stamina Accessory
<color is="#ffffff">+6 max Stamina</color> and <color is="#ffffff">+20% Stamina Regen</color> while in your Accessory Bag.
Your Stamina refills 20% faster whenever it refills (not while you sprint, glide or block).
Only your best Stamina Accessory counts. Legendary is the top rarity.
```

- Per-line requirement lines: Runic "Spell shots only (wand, staff, spellbook)."; Stonehide "Against hits from mobs and players.";
  Razorfang "+4% Crit Chance and +8% Crit Damage" on its stat line; Feather "Fall damage needs SkyySkills." is shown only on the bag page
  (tooltips are static).
- **Every player string is built from the rarity, the line name and "Accessory"**, never from the family key. In 0.4.5,
  `AccDefs.pretty`, the `why` refusal text, the legacy lang names and the bag description all print the family key plus "Talisman"; 0.5
  replaces each one.
- Generated from the booster table, so text and numbers match the build defaults. A config change does not change item text (known
  limit G12). To keep that small, the "Next" part names the next rarity without its number; the bag page and `/accessories lines` show
  the live numbers. Accessory Power stays off the tooltip until powers exist (Q9).

### 5.8 Server Setup rows (every number editable in game; kit `tools/skyycfg.py`)

| Key | Label | Category | Type | Default | Notes | Part |
|---|---|---|---|---|---|---|
| `slots` | Accessory slots | Accessory Bag | int 1-60 | 18 | existing key, new max; live; lowering deletes nothing | 1 |
| `regenEverySeconds` | Regeneration heals every | Boosters | int, s | 2 | existing | 1 |
| `boost` | Booster numbers | Boosters | 1-column table (text), live, with a `check=` hook | row default empty (kit rule); the entries are written to the file by `writeDefaults` or the migration (5.1) | entry `<Admin name>.<stat>`, value = a comma list with one number per rarity (4); a missing entry uses the build default | 1 (part 2 adds entries) |
| `line.Health` ... `line.Speed` | Health line, Stamina line, ... | Boosters | bool (5 scalar rows), live | on | off = the line stays in the bag, counts for nothing, and shows "switched off" | 1 |
| `line.Strength`, `line.MagicPower`, `line.Defense`, `line.Crit`, `line.Feather` | Brawler line, ... | Boosters | bool (5 scalar rows), live | on | as above | 2 |
| `combatToGear` | Send combat stats to SkyyGear | Boosters | bool, live | on | off = `gear:extra` is removed for everyone | 2 |
| `notice.boosters` | Tell players about the accessory change | Accessory Bag | bool | on | the one-time chat line (5.1) | 1 |

- **`boost` entries** (the unit is in the entry name). Part 1: `Health.flat`, `Stamina.flat`, `Stamina.regenPct`, `Mana.pct`,
  `Mana.floor`, `Regeneration.pct`, `Speed.pct`. Part 2: `Strength.flat`, `MagicPower.flat`, `Defense.flat`, `Crit.chancePct`,
  `Crit.damagePct`, `Feather.fallPct`, `Feather.jumpPct`. Admin names, never Vitality, Endurance or Intelligence.
- **Defaults on, switches as kill switches.** Skyy's decision 6 says a booster stat must never do nothing, so no line ships switched off.
  The switches let an admin stop a line that misbehaves; the bag page then says "switched off" for it.
- **Why scalar bool rows, not a table of on/off:** no deployed table has a `bool` column, and SkyyMenu 0.3.3's table editor edits cells as
  typed text; scalar `bool` rows give real ON/OFF buttons.
- **No signs:** `AccCfg.num()` rejects a minus sign, so Feather's fall is stored as magnitudes (`10,20,30,40`) and the tick negates it;
  jump is `5,10,15,20`.
- **The `check=` hook** refuses a list that is not exactly 4 numbers, any negative or non-number, whole-number-only stats with a decimal
  (`Strength`, `MagicPower`, `Defense`, `Crit.*`, later `lsteal`: SkyyGear floors them, so a decimal would silently shrink), and values
  over a sane cap (100 for a percent, 1000 for a flat). Decimals are fine for Health, Stamina (both entries), Mana, Regeneration, Speed
  and Feather.
- **Help text is capped at 100 characters** (build-enforced), so one row cannot explain 14 units; the unit lives in the entry name.
  Example help: "Four numbers, Normal to Legendary. The entry name gives the unit. Fall is written without a minus."
- **No Accessory Power row.** The AP table is a build constant until powers exist (1.3).
- The old `bonus` row goes away (migrated, 5.1). Rows marked live apply at once, like today's `bonus` row.

### 5.9 Hooks for getting them (acquisition stays a placeholder; Skyy's decision 5)

- **Commands** (two named admin sub-commands and one player sub-command, so no command has two usage variants):
  - `/accessories lines` (player): every line, its rarities, item ids, live numbers, and whether it is switched on.
    `setPermissionGroups(new String[] { "hytale:Adventurer" })`.
  - `/accessories give <player> <item id> [amount]` (admin).
  - `/accessories givetier <player> <name> <rarity> [amount]` (admin). `<name>` takes the admin name (Health, Stamina, Mana, Strength,
    Crit, ...) and, as aliases, the old keys Vitality, Endurance and Intelligence. `<rarity>` takes Normal, Unique, Rare, Legendary or
    1 to 4. Usage and replies show the admin names and rarity words only.
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
  `world.execute`, returns 0 and logs one line. It only accepts ids from the booster table (never a legacy id).
- **Bridge `acc:defs`:** one String listing every rarity of every line as `name:key:tier:itemId:rarity:ap:sources` (admin name, family
  key, tier number, id, display rarity, Accessory Power, source words joined by `+`, for example `Health:Vitality:4:Skyy_Talisman_
  Vitality_Epic:Legendary:19:Craft+Boss`). The loot pass builds its tables from the same source words (Drop, Chest, Combine, Craft,
  Boss) and finds hooks for all 40 items (20 after part 1).
- The commands and bridges read the booster table, so part 2 adds rows and nothing else.
- New lines get **no recipe** (Skyy: "we will worry about how they are made/upgraded later").

### 5.10 Which mod versions build it

| Mod | Version | Change |
|---|---|---|
| SkyyAccessories | **0.5 = part 1** | section 6, part 1. Patch `tools/acc_0_5_patch.py` reads the generated `SkyyAccessories/build_skyyaccessories_0.4.5.py` and writes `build_skyyaccessories_0.5.py` (edit the patch, never the generated file). The patch replaces roughly half of the 0.4.5 script: keep the `ACC PAGE BLOCK START/END` markers so a 0.5 test harness can exec the page block as `test_skyyaccessories_0.4.5.py` does |
| SkyyAccessories | **0.5.1 = part 2** | section 6, part 2. Patch `tools/acc_0_5_1_patch.py` reads the generated 0.5 script |
| SkyyAccessories | 0.5.2 = wave 2 | section 3: table rows, items, looks and the `skill:bonus` publisher (Leech after Skyy's Life Steal shape) |
| SkyyGear | 0.1 (live), no change | already reads `gear:extra` for Strength, Magical Power, Defense and crits, on every hit (VERIFIED) |
| SkyySkills | 0.4.7 (live), no change | applies fall damage from every movement source; reads `skill:bonus` for wave 2 |
| skyymove protocol | v1, no change | carries `jump` and `fallDamage` already |
| SkyyAuctions, SkyyMenu | no change needed | only these two read `acc:` keys (VERIFIED). Optional later: an AH filter by booster stat; SkyyMenu's "N talismans" could read "N accessories" |

---

## 6. The build, in two parts

### 6.1 Part 1: SkyyAccessories 0.5 (everything that touches existing players)

1. One **booster table** in flat 1-D arrays (5.4) holding the five folded lines, replacing the five hard-wired families, and one
   generic effect tick with one try per publisher.
2. **Gear rarity** for every accessory: six `Skyy_Acc_*` quality assets with both label keys, the mapping (bench IV and up Legendary,
   Omni Legendary, bag item Unique), separate `ID_WORD` and `DISPLAY` arrays with `Legendary` as a legacy id word, the world-thread
   restamp, `rarityOf` 1-4, kit colours (5.2).
3. **Fold the 25 talismans**: names "<Rarity> <Line> Accessory", the 4-step numbers, flat Health and Stamina, Mana floor, lower
   Regeneration, the `_Legendary` ids as legacy ids (no recipe, count as Legendary, rebuilt into `_Epic`), config migration with `.bak`
   and log lines, one-time notice with its per-player flag file (5.1, 2.2).
4. **Stamina Regen** top-up (5.4.1), with `B.probe` checks for its engine calls.
5. **Bag**: 60 storage slots in two files, default 18, `PAGE_ROWS` paging for slots and inventory, the generic Bonuses well, window
   about 1210 x 950 (5.5).
6. **Commands and bridges**: `/accessories lines`, `give`, `givetier`, `acc:fn:give`, `acc:defs` (5.9), all driven by the table.
7. **Server Setup rows**: `slots`, `regenEverySeconds`, `boost` with the 7 part 1 entries, the 5 part 1 line switches,
   `notice.boosters` (5.8).

**Part 1 build checks** (the script must fail on any of these):
- a booster uses a stat outside 1.4's allowlist;
- a line does not have exactly 4 rarities Normal to Legendary, a number list is not 4 long, two rarities share an id or an icon, or any
  item with a recipe (booster, bench accessory, Omni) has a quality above Legendary;
- any of the 20 modern ids, the 15 old legacy ids or the 5 `_Legendary` legacy ids fails to round-trip through `tierOf`, `familyOf` and
  `modernOf` (`_Legendary` -> `_Epic`), or the equip swap order differs from 0.4.5 for the old lines other than the new `_Epic` /
  `_Legendary` tie;
- a booster's name is not exactly "<Rarity> <Line> Accessory", or any player string (lang, chat, page, refusal text) contains
  Vitality, Endurance, Intelligence or Talisman;
- a look path is missing in Assets.zip (today's `visual_of` and `icon_of` checks);
- a quality asset's field set differs from vanilla `Common.json`, or its QualityValue is 8 or more;
- an engine call of the Stamina Regen top-up is missing (`B.probe`);
- the page does not fit at its new size (`fit()` and harness asserts updated from 1210 x 780);
- (the kit already fails on help text over 100 characters.)

**Part 1 in-game tests** (the builder writes the full numbered steps):
1. Old talismans show the new names and gear colours; the restamp fixes stacks in storage, hotbar and backpack; the bag item shows
   Unique, the Omni Legendary, Farming accessory IV to VII Legendary. **A rolled gear item, a Magic Bag, an Extended Backpacks Mythic
   item and a SkyyVault item still look right** after the deploy (quality index shift). A talisman kept in the vault keeps its old look
   until taken out, then is restamped.
2. An old `_Legendary` talisman: counts as Legendary, has no recipe, comes back as the `_Epic` item after equip and unequip, and ties with
   an `_Epic` (the second one is refused). The Workbench still upgrades Rare to Legendary (the `_Epic` recipe).
3. Config: a copied 0.4.5 `config.properties` migrates once (`config.properties.pre-0.5.bak` exists, `config-changes.log` has the
   lines, `slots` is 18, an edited Mana/Regeneration/Speed list carried over as its 1st, 2nd, 3rd and 5th numbers). Restart: no second
   migration. Set `slots` to 9, restart: it stays 9.
4. `give` and `givetier` each rarity (also with the alias Vitality and with a rarity word); equip Normal, then Unique (Normal comes
   back); an equal rarity is refused. Give to a player in another world.
5. Health and Stamina maximums grow by the flat amount and the current value does not jump (expected); Mana grows by the percent, or by
   the floor on a small pool.
6. Stamina Regen: empty the bar by sprinting, then time the refill with and without a Legendary Stamina Accessory (a 16-Stamina bar:
   about 5.3 s against 4.4 s). While sprinting the bar drains at the same speed with or without it. While blocking, no refill either way.
   After a SkyySkills double jump the short pause still happens. Set `Stamina.regenPct` to `0,0,0,0`: the refill is back to vanilla.
7. Speed with and without Acrobatics.
8. Profile switch and relog: stats follow the active profile's bag.
9. Server Setup: change `boost` `Health.flat` and `slots`, see it apply at once; a refused entry (wrong count, a minus); switch a line
   off (the page shows "switched off").
10. The notice shows once for a player with a bag file, never again after a world switch or relog, and never for a brand-new player.
11. Bag page at 18 slots and at 60 (config), pagers, fits at 1080.
12. UNVERIFIED items to watch: plugin quality frames and colours; the Stamina Regen feel (the once-a-second sample, 5.4.1).

### 6.2 Part 2: SkyyAccessories 0.5.1 (the five new lines and the feeds that never ran in game)

1. **Five new lines, 20 items**: Brawler, Runic, Stonehide, Razorfang, Feather, as booster table rows, with looks and tooltips (2.3, 2.4,
   5.6, 5.7). No recipes; admin give only.
2. **`gear:extra` publisher**: only writer, whole numbers, allowlist `str mp def cc cd` (`lsteal` joins in wave 2), back-off rule,
   stale-key removal, republish on a profile switch (5.4).
3. **Feather through the movement source**: the existing `accessories.talismans` post now also carries `jump` and `fallDamage`.
4. **Notes on the bag page**: SkyyGear missing, its `part.stats` off, SkyySkills missing for Feather's fall part (5.4).
5. **Server Setup**: the 7 part 2 `boost` entries (appended on first start when missing), the 5 line switches, `combatToGear` (5.8).
   All on by default (Skyy's decision 6); new items reach players only through the admin give until the loot pass.

**Part 2 build checks:** every part 1 check, extended to the 20 `_T<n>` ids; a `gear:extra` key outside `str mp def cc cd`; any new id
that starts with `Skyy_Accessory_` or ends in `_Talisman`, `_Ring`, `_Artifact` or `_Legendary`.

**Part 2 in-game tests:**
1. `give` and `givetier` each new rarity; equip Normal, then Unique; an equal rarity is refused.
2. `/gear` shows the "From other mods (gear:extra)" line with the right totals; a hit with and without Brawler; Razorfang with and
   without gear Crit Chance.
3. Fall from a set height with and without Feather; jump height at Legendary; the Acrobatics double jump with and without Feather
   (INFERRED to rise too).
4. Logout removes `gear:extra`; a server stop removes it too; a profile switch republishes it.
5. `combatToGear` off; a line switched off; SkyyGear's `part.stats` off shows the note on the bag page.
6. UNVERIFIED items to watch: the first real `gear:extra` publisher; fall damage and jump from an accessory source (never sent before).

---

## 7. Open questions for Skyy (default in brackets)

**Answered by Skyy on 2026-09-30 (now built into this file):** tier words (none: one name per line, gear rarities), the gear ladder for
all accessories (yes; crafted ones stop at Legendary, so the Omni is Legendary), "+stamina" (max Stamina and Stamina Regen), flat Health
and Stamina with every Health, Stamina and Mana talisman stronger on deploy (yes, fold with the new numbers), bag slots (18, up to 60),
Regeneration weaker (yes), new lines from the admin give only until the drop tables exist (yes), Fabled and Mythic (rare finds, later).

Still open:

4. **Speed**: keep the accessory % layer (multiplies with Acrobatics), or lock 25's flat layer (adds)? The % Legendary is 4x the best
   gear Speed roll at Acrobatics 100 (+0.20 against +0.05) and 2x at Acrobatics 0; flat would be 2x at any level. [keep %, with
   +2.5/+5/+7.5/+10: it is what you asked for and the live Speed talisman's top]
6. **Mana**: % with a small flat floor (at least +1/+2/+3/+4), so a player with a tiny pool feels it? This bends lock 88 (% mana on
   dedicated accessories) and **needs your yes**. Under SkyySkills 0.4.8 (Mage and Priest start at 30) the floor only matters below
   about 17 Mana, so only for players without a caster class. [% with the floor; setting the floor row to 0 gives % only]
8. When a later line **shares a stat** with another line: one per stat, or one per line? [one per line; the first build has no overlap]
9. **Accessory Power** table 10/13/16/19 (22/25 reserved for rare finds): a build constant only, or shown before powers exist? Do bench
   accessories count? Does the Omni plus benches double count? [build constant, not shown, no setting until powers ship; bench
   accessories count (lock 112 says each accessory); while the Omni is in the bag, bench accessories add 0]
11. **Combat stats on accessories**: confirm the reading that accessories are not gear, so locks 66 and 75 allow Defense, Crit
    Chance, Crit Damage, Strength, Health and Speed on them despite lock 125 and SkyyGear's gear slot table. [yes]
12. **Crit line**: one Razorfang line with both Crit Chance and Crit Damage, or two lines (Crit Damage alone does nothing without Crit
    Chance, and base Crit Chance is 0)? [one line]
14. Small calls, one line: no **level requirement** on boosters; Feather **jump +20%** at Legendary is fine for the hand-built zones;
    **line names** Brawler, Runic, Stonehide, Razorfang, Feather (and Prospector, Woodsman, Harvester, Leech) are placeholders; the
    **rarity word at the front of the name** ("Rare Health Accessory", like "Rare Mining Bag"). [no; yes; placeholders, names live only
    in the language file; yes, because rarity frames do not render]

(Numbers kept from the earlier draft so HANDOFF and review notes still match.)

---

## 8. Clashes with locked or earlier lines, and how this file handles them

| Clash | Source | Handling |
|---|---|---|
| The suggested `Skyy_Accessory_<Family>_<Tier>` ids | task text vs `AccDefs.benchOf`, SkyySacks `/craft` tabs | use `Skyy_Talisman_<Key>_T<n>` (5.3) |
| Tier words (Charm, Band, Sigil, Emblem, Crest) in the earlier draft | Skyy 2026-09-30: "they are all accessories" | dropped: one name per line, "<Rarity> <Line> Accessory" (1.2) |
| Five talisman ids, four rarities | the 0.4.5 talisman ladder vs Skyy's Normal to Legendary | `_Epic` carries Legendary; `_Legendary` becomes a legacy id counting as Legendary, no recipe (2.2) |
| The earlier draft's Fabled top step and Unique-to-Fabled drop lines | Skyy 2026-09-30: lines stop at Legendary; Fabled and Mythic are rare finds | every line Normal to Legendary; numbers rescaled so Legendary keeps the top (1.5); Fabled and Mythic in 4.1 |
| A Mythic Omni (earlier draft, like the Mythic Omni Bag) | Skyy 2026-09-30: Mythic cannot be crafted | the crafted Omni is Legendary; bench IV and up Legendary (1.2, 5.2) |
| Accessories on vanilla rarities while gear and bags use Wynn | Decisions change note 5 (2026-09-25), Skyy 2026-09-30 | move to the gear ladder (5.2) |
| Stamina Regen on accessories | lock 27, catalog "Sprint Regen" row (armor only) | lifted for accessories by Skyy 2026-09-30; applied by SkyyAccessories itself, not `gear:extra` `stam` (5.4.1) |
| SkyyGear's Stamina Regen also runs while sprinting | SkyyGear 0.1 `GearFx.second` | the accessory regen follows vanilla's conditions instead; SkyyGear side note in 5.4.1 |
| Defense, Crit Chance, Crit Damage as accessory main stats | SkyyGear 0.1 slot table (Defense armor only, crits weapon and armor), lock 125 (combat modifiers on combat gear) | read as gear-only rules; accessories are not gear, and locks 66 and 75 put Defense, Crit Chance, Crit Damage, Strength, Health and Speed on accessories (Strength catalog row and lock 103 name accessories outright) (1.4, Q11) |
| Flat Speed (lock 25) vs % Speed (layer model, live talisman, Skyy's "+% movement speed") | SkyyGear-Plan lock 25 | keep %, top unchanged at 10%; the power gap to gear is stated (1.5, Q4) |
| Speed "unchanged on deploy" (earlier draft) | the 4-step rescale | lower rarities rise 1.25x, the top stays 10%; no Speed talisman gets weaker (1.6) |
| Health as % (live Vitality) vs flat Health on accessories | lock 19, lock 22 | flat (Skyy: fold with the new numbers) |
| +% Mana on tiny pools | lock 88, inventory C4 | % plus a flat floor, needs Skyy's yes (1.5, Q6) |
| Regeneration beats the best gear regen roll; SkyBlock natural regen is scrap | lock 20, catalog Raw Health Regen and Health Regen rows | numbers lowered below the best gear roll (Skyy: "Regeneration weaker") (1.5) |
| Damage %, element damage | locks 15, 17 | not used (1.4) |
| "Vitality" and "Intelligence" in player and admin text | locks 20, 67 | display and admin names change; family keys stay in item ids only; build check (2.1, 6) |
| "Not in the game yet" / "stats that do nothing must never be on a booster" | Skyy 2026-09-30 locks | stat allowlist and build check; no line ships switched off; Accessory Power a build constant, no setting, not shown (1.3, 1.4, 5.8) |
| Old Accessory Power draft 3/5/8/12/16 | Plan section 1 vs locks 111-113 | new table inside +10 to +25 (1.3) |
| Default 18 slots vs start 9 + 51 unlock slots, cap 60 | `docs/plans/SkyyAccessories-Plan.md` section 3 (draft) | Skyy: 18 to 60; unlock sources rebased to +42 (5.5) |
| Collection-gated craft tiers | lock 64 | not wired in 0.5: today's Workbench recipes stay ungated; the later acquisition pass adds the gate (2.2, 4.2) |
| Life Steal numbers | SkyyGear-Plan open item 9 ("do not invent"), catalog row | Leech waits for Skyy's Life Steal shape (section 3) |
| `acc:pct` combat plan vs shipped `gear:extra` | Plan technical notes vs SkyyGear 0.1 | `gear:extra` (5.4) |
| Line names Hawkeye and Bulwark | draft crystal table, Plan section 2 (Archer and Warrior crystals) | dropped: crits paired into Razorfang, Defense line named Stonehide (2.1) |

---

## 9. Sources read

Skyy's design files (read only): `tools/AGENT-BRIEF.md`, `HANDOFF.md` (status block, movement layer rule, versions table, newest log
lines), `OPEN-QUESTIONS.md` (LOCKED lines, including the 2026-09-30 booster lock, the SkyyGear level lock, the SkyySkills 0.4.8 Mana line
and the "Seen in game" probe line), `docs/plans/SkyyAccessories-Plan.md` (sections 2, 3, 5), `SkyyGear-Plan.md` (locks 1-126, open item 9),
`SkyyGear-Stat-Catalog.md` (placement rows, regen, Sprint Regen and Life Steal rows, accessory sections), `docs/plans/SkyWynn-Decisions.md`
(accessory change notes), `tools/CONFIG-CONTRACT.md` (table rules, help cap, `config-history/` and `config-changes.log`). Research:
`research/Hypixel-Accessories-Research.md` (sections 2 and 5), `research/Accessory-Pack-Inventory.md`, `research/SkyyGear-Stage1-Spec.md`
(rarity ladder, migration map), `research/Bag-Restructure-Spec.md` (quality index and restamp). Build scripts:
`SkyyAccessories/build_skyyaccessories_0.4.5.py` (talisman and bench tables, `QUAL`, recipes, `AccEffects.tick`),
`SkyyGear/build_skyygear_0.1.py`, `_0.1.1.py`, `_0.1.2.py` (stat table incl. `stam`, `GearFx.second` regen, `gear:extra` parsing and
`totalsInv`, modifier maxima, `hpr`/`hprp`, `GearLevel.factor`, `stat.levelFull`, `part.stats`, bridge keys),
`SkyySkills/build_skyyskills_0.4.7.py` and `_0.4.8.py` (double-jump regen pause, Mana base and spell costs),
`SkyyTrees/build_skyytrees_0.2.5.py` (Stamina nodes), `SkyySacks/build_skyysacks_0.7.7.py` and `_0.7.8.py` (bag names),
`SkyyAuctions/build_skyyauctions_0.1.2.py` (`qPretty`, `tierList`, `category`), `SkyyMenu/build_skyymenu_0.3.3.py`, `tools/skyymove.py`,
`tools/skyyui.py`, `tools/skyybuild.py`, `tools/deploy_set.py` (SET pins, read only). Assets.zip (read only): the item files for the look
paths in 5.6, `Server/Entity/Stats/Stamina.json`, `StaminaRegenDelay.json`, `Health.json`, `Mana.json`, and the item-text markup counts
in `Server/Languages/en-US/server.lang`. HytaleServer.jar (read only, bytecode): the classes listed under "Proof" in 5.4.1. A compile
test of the Stamina Regen top-up ran with `tools/javassist.jar` in `tools/dev/scratch/booster-spec/` (TEMP and TMP pointed there,
`-XX:-UsePerfData`); the folder was deleted afterwards. The two reviews of 2026-09-30 (design and feasibility).

---

## Revision to Skyy's decisions (2026-09-30)

What changed from the reviewed draft, and why:

- **Tier words dropped** (decision 1): Charm, Band, Sigil, Emblem and Crest are gone everywhere. Each line is one accessory, named
  "<Rarity> <Line> Accessory"; the rarity word stays in front because rarity frames do not render and the Magic Bags already work this way.
- **Four rarities, Normal to Legendary, for every line** (decision 1). The 5-step numbers were rescaled with one rule, step n = n/4 of
  the Legendary number, keeping the old top at Legendary; Health and Mana tops 25 -> 24 for whole steps. The drop lines and Feather kept
  their numbers (already quarter steps) and moved down to Normal..Legendary.
- **The fifth talisman id folds into Legendary**: `_Epic` carries Legendary, `_Legendary` becomes a legacy id with no recipe (2.2); the
  config migration carries edited five-number lists as their 1st, 2nd, 3rd and 5th numbers (5.1).
- **Crafted accessories stop at Legendary**: bench accessories IV and up and the Omni are Legendary (the earlier draft had a Mythic Omni
  and Fabled bench tops).
- **Fabled and Mythic** moved to section 4.1 "Later: rare finds". Their quality assets still ship in part 1 (one index shift) and stay
  unused.
- **Stamina = max Stamina and Stamina Regen** (decision 4). Checked: Stamina Regen is live only inside SkyyGear (`stam`), as a flat
  amount every 2 s that also runs while sprinting; SkyySkills and SkyyTrees have none. The engine has no per-player regen modifier
  (EntityStatMap modifiers target only MIN and MAX; regen modifiers live in shared assets and worn armor). So SkyyAccessories tops up
  Stamina itself on the world thread, only while vanilla's own regen conditions pass (`Condition.allConditionsMet`), proven in bytecode
  and by a javassist compile test (5.4.1). Numbers +5/+10/+15/+20%.
- **Bag 18 -> 60** and **the fold** confirmed (decisions 2, 3); **admin give only** (decision 5); **no stat that does nothing and no line
  switched off by default** (decision 6).
- **Build split into two parts**: part 1 (0.5) = everything that touches existing players, including the Stamina Regen; part 2 (0.5.1)
  = the five new lines with the `gear:extra` and Feather feeds. Wave 2 moves to 0.5.2.
- **Resolved questions** Q1, Q2, Q3, Q5, Q7, Q10 and Q13 left section 7; Q6 notes SkyySkills 0.4.8's Mana change; Q14 adds the rarity
  word in the name.

## Review notes (2026-09-30, earlier draft)

Both reviews were applied in full; nothing was rejected outright. Where a fix differs from the reviewer's suggestion, the reason is here.
(Items about tier words, Fabled tops and the Mythic Omni are superseded by the revision above.)

- **Design 2 (Regeneration):** lowered below the best gear regen roll rather than the example 0.25-1.5%, so the top stays under the best
  gear roll up to about 240 Health (the example still beat it at 200). Out-of-combat-only stays in section 4.2, since it needs a combat
  timestamp this mod does not have.
- **Design 5 (Razorfang):** paired Crit Chance and Crit Damage into one line (the reviewer's "or pair them") instead of raising Crit
  Damage alone; a raised Crit Damage line still pays nothing without Crit Chance. Hawkeye is gone as a name.
- **Design 7 (tier words):** superseded: Skyy chose no tier words.
- **Design 15 (names):** the stat goes on the first tooltip line; an AH sub-category by stat is left for a later SkyyAuctions change,
  because 0.5 keeps SkyyAuctions unchanged. Bulwark renamed Stonehide so neither crystal-table name is reused.
- **Design 16 (Speed):** took the reviewer's lower option (today's top, 10%); the 4-step rescale now lifts the lower rarities slightly.
- **Design 19 (Feather):** jump on every rarity as an even ramp (+5/+10/+15/+20) rather than +5% on the first two only.
- **Design 22 (questions):** the five new questions were added; the old Q10, Q13 and Q14 were merged into Q14.
- **Feasibility 1 (roll-back):** did both suggested fixes, the second bag file and the "do not roll back below 0.5" note, because the
  quality indexes and new item ids are roll-back risks the second file does not cover.
- **Feasibility 5 (migration):** chose the atomic rewrite over scalar `boost` rows (14 comma lists fit one table better). The marker
  is "has `bonus.` lines and no `boost.` lines" instead of "new lines absent", so deleting a `boost.` entry later never re-runs the
  migration or bumps `slots` again.
- **Feasibility 12 (commands):** `/accessories lines` is a player command; `give` was split into `give` and `givetier`.
- **Feasibility 14 (counts):** recounted in Assets.zip: 331 item descriptions of 548 description keys; 101 use `<color is=` (the
  review said 102), 38 use `<i>`, 101 use `\n`, 143 use at least one.
- **Feasibility 15 (AP row):** removed; the AP table is a build constant and a field in `acc:defs`.
