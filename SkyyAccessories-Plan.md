# SKYYACCESSORIES — ACCESSORY POWER + BAG SLOTS (proposal)
*Drafted 2026-09-23. Based on Hypixel SkyBlock's Accessory Power (formerly "Magical Power"), adapted to our layer model. Anything marked **[SKYY?]** needs your call.*

**Lock (2026-09-23 batch 2):** the accessory bag and magical power are **core**, not a later-game system. They ship with the core loop (`SkyWynn-Master-Plan.md` P1, `SkyWynn-Decisions.md` 5.10). The numbers below are still a draft. Gear also has rarity and stats on every item, and a reforge swaps bonuses (rows 5.1, 5.3–5.5); that layer is core too, and it is not this bag.

**Lock (2026-09-24, Decisions change note 8, `SkyyGear-Plan.md` lock 14):** each accessory gives its own buff and also adds accessory power. Total power feeds one selectable buff. More power means a stronger buff. Locked examples: **Warrior** (strength as a damage modifier, plus a small amount of crit chance, crit damage, health, and defence) and **Elementalist** (all elemental damage types, and all elemental resistance). More options are TBD. A loadout saves the selected buff, along with armor and the Equipment bar (necklace, cloak, ring, belt — working name Equipment, name not final). That bar is not this bag. The crystal table, the ln curve, tuning, AP-by-rarity, and the slot prices below stay a draft. They are not the locked buff list or the locked numbers.

**Lock (2026-09-25, change notes 17–19, `SkyyGear-Plan.md` locks 63–76):** most accessories are crafted. Some come from mobs or chests. Leveling a collection unlocks the next accessory craft tier. Crafting the next rarity needs the previous rarity as an ingredient. That craft ladder is the lock. The bag-slot prices in section 3 stay a draft. Enrichments: keep Speed, Crit Damage, Crit Chance, Strength, Defense, Health, and Attack Speed. Intelligence Enrichment is **Mana % enrichment**. No Intelligence ID. Sea Creature Chance is later, with fishing. Magic Find Enrichment is scrap. Ferocity Enrichment was pending at this note. The Hypixel starter lean was replaced later the same day (change note 20).

**Lock (2026-09-25, change note 20, `SkyyGear-Plan.md` locks 77–90):** Ferocity stays. It can roll on combat gear and accessories. Enchant cap 300. Total cap 600. Ferocity Enrichment is still pending. Do not scrap the Ferocity stat. Hypixel starter names are scrap: Fortuitous, Pretty, Protected, Simple, Warrior. Custom starters: Tank, Balance, Slayer, Lucky, Fast, Magical. Every starter grants a little Health and Defense. Tank adds Health and Defense only. Balance is an even boost, including flat mana. Slayer has more Strength and Crit Damage, and less Health and Defense. Lucky has high Crit Chance. Fast has high Speed and Attack Speed. Magical has normal Health, less Defense, flat mana, and mana regen. Accessory powers use flat mana. Dedicated mana accessories use +% mana. Gear modifier rulings apply to accessories and Equipment the same way. No Power was scrapped later (change note 24). The default profile is Balance. Stone powers are not locked. Wiki numbers are research. They are not our numbers. Combat 15 names were replaced later the same day (change note 21).

**Lock (2026-09-25, change note 21, `SkyyGear-Plan.md` locks 91–101):** Combat-gated powers mirror the starter themes. They are more extreme. They use buffs and debuffs. Amounts still scale with total Accessory Power. **Glass Cannon** is Keep. It is the Combat 15 form of Slayer: −Health, −Defense, much more Strength and Crit Damage, solid Crit Chance. The other five were drafts at this note. Confirmed later the same day (change note 22). Do not copy Hypixel names Commando, Disciplined, Inspired, Ominous, or Prepared. Stone powers stay pending. No Power was scrapped later (change note 24). The default profile is Balance.

**Lock (2026-09-25, change note 22, `SkyyGear-Plan.md` locks 102–110):** Magical Power is a spell-damage stat. Strength boosts a melee or hit. A Mage can melee with a staff and also cast. Staff melee uses Strength. Spells use Magical Power. It rolls on weapons, armor, Equipment, and accessories. It is not the bag's Accessory Power score. Hypixel's older name for that score was also Magical Power. Do not mix them. Starter Magical adds flat mana, mana regen, and Magical Power. Combat 15 Keep: Fortress (large Health and Defense; a Speed or Strength debuff is optional), Harmony (larger even spread of Health, Defense, Speed, Strength, flat mana, Crit Chance, and Crit Damage; Magical Power is not in that spread), Fortune (much higher Crit Chance, good Crit Damage, slight Strength, −Health, −Defense), Blitz (high Speed and Attack Speed, −Health, −Defense), Arcane (more Magical Power, −Defense, −Strength, flat mana and mana regen). Whether Magical Power joins enrichments or tuning is open.

**Lock (2026-09-25, change note 23, `SkyyGear-Plan.md` locks 111–115):** SkyBlock-style Accessory Power. Each accessory has its own buffs and also adds flat Accessory Power by rarity, from +10 to +25. The exact table is not set. The 3/5/8/12/16 table below is the old draft, not this lock. Total Accessory Power is the sum across equipped accessories. The selected profile (Tank, Balance, Slayer, and the Combat 15 ladder) scales from that total. No Power was scrapped later the same day (change note 24). The default profile is Balance.

**Lock (2026-09-25, change note 24, `SkyyGear-Plan.md` locks 116–118):** No Power is scrap. There is no selectable empty profile. The default profile is Balance. Players can switch to Tank, Slayer, Lucky, Fast, or Magical. They can also switch to the Combat 15 ladder when unlocked: Fortress, Harmony, Glass Cannon, Fortune, Blitz, Arcane.

## 1. Accessory Power (AP)

The numbers in this section are the old draft. Change note 23 is the lock: flat +10 to +25 by rarity, exact table not set, total is the sum of equipped accessories.

Each accessory in the bag gives AP by rarity; only the best item per family counts (the bag already hands back lower tiers). That best-per-family line is part of this draft, not change note 23.

| Rarity | Common | Uncommon | Rare | Epic | Legendary |
|---|---|---|---|---|---|
| AP | 3 | 5 | 8 | 12 | 16 |

- Talisman families run Common to Legendary, as you decided.
- Bench accessories: T1 Common, T2 Uncommon, T3 Rare, T4 Epic, T5 and up Legendary.
- AP is a visible score: bag page header, `/acc power`, later a HUD widget.

## 2. How power turns into stats (percent layer)
AP gives no stats itself. It feeds two things, both in the accessory percent layer:
**final = (default + skills + armor) x (1 + talisman % + crystal % + tuning %)**

**Power Crystal.** Pick one, swap for free. Its stats "at x1.0" are multiplied by the **Power Multiplier M = ln(1 + AP / 100)**: fast early, flat later, never caps (Hypixel's curve shape, easier to tune).

| Crystal | For | Stats at x1.0 |
|---|---|---|
| Balanced | everyone (starter) | Health 5%, Damage 3%, Defense 3%, Speed 1% |
| Hawkeye | Archer | Damage 8%, Crit Chance 3%, Speed 3% |
| Bulwark | Warrior | Health 10%, Defense 10%, Damage 4% |
| Shadowstep | Assassin | Crit Damage 15%, Speed 4%, Health -3% |
| Bloodrage | Shaman (later) — may point back at Berserker, pending | Damage 12%, Health 5%, Defense -4% |
| Arcane | Mage | Mana 15%, Ability Damage 6% |

Negative stats follow your gear trade-off rule. Balanced is unlocked from the start; your class crystal unlocks at class skill 10. Later: "Stone" upgrades for 9 of a rare boss drop (like Hypixel's Stone Powers).

Class crystals follow the class roster in `SkyyClasses-Plan.md` (Warrior, Archer, Mage, Assassin, Shaman, plus Berserker once that class is no longer pending). Bloodrage's class column was drafted as Berserker. The 2026-09-23 roster lock pointed it at Shaman, a later class. **2026-09-24:** Berserker is back on the roster, status PENDING (the owner wants it; details and timing wait on a talk with the builder). Bloodrage **may point back at Berserker**, pending that talk. Until then the table still shows Shaman, and the numbers are still a draft. Do not retune Bloodrage in this pass.

**Tuning points.** 1 point per 10 AP, spent in `/acc tune`, free reset. Per point: Health or Defense +0.25%, Damage +0.15%, Crit Chance +0.1%, Stamina or Mana +0.5%, Speed +0.1% (max +5% speed from tuning).

**Worked example: a Warrior with the Bulwark crystal, all tuning points in Health**

| Bag | Contents | AP | M | Crystal gives | Tuning |
|---|---|---|---|---|---|
| 9 slots (start) | 3 Common, 4 Uncommon, 2 Rare | 45 | 0.37 | Health +3.7%, Def +3.7%, Dmg +1.5% | 4 pts = Health +1% |
| 27 slots (mid) | 5 Uncommon, 12 Rare, 8 Epic, 2 Legendary | 249 | 1.25 | Health +12.5%, Def +12.5%, Dmg +5% | 24 pts = Health +6% |
| 60 slots (max) | 15 Rare, 25 Epic, 20 Legendary | 740 | 2.13 | Health +21.3%, Def +21.3%, Dmg +8.5% | 74 pts = Health +18.5% |

Health at max bag: 100 default HP, +60 flat from skills and armor, and a Legendary Vitality talisman at +10% gives 160 x (1 + 0.10 + 0.213 + 0.185) = **240 HP**.

Health, Stamina, Mana and Speed can go live now; Damage, Defense and Crit are published for the future combat mod to apply.

## 3. Bag slot progression
Start **9** (today's bag), **max 60**, all sources stack:

| Source | Slots | How you earn them |
|---|---|---|
| Collections (SkyyCollections) | +12 | +1 per 5 collection tiers reached (all collections combined) |
| Skills (SkyySkills) | +20 | +1 at level 25/50/75/100 in Mining, Foraging, Farming, Acrobatics and your class skill |
| Coins (SkyyCoins) | +16 | buy 2 slots at a time for 25k, 50k, 100k, 200k, 400k, 800k, 1.6M, 3.2M coins (6.4M total) |
| Quests (later) | +3 | reward from a quest line |

Unlocks are permanent (switching class never removes slots). Note: only **18 families exist today** (13 bench + 5 talisman), so slots past ~18 stay empty until we add more families.

**How locked slots look.** After your unlocked slots comes one row of dark grey "LOCKED" cells, each showing its next requirement ("Mining 25", "Buy 25k"). Under the grid, an **Unlock progress** panel: "Collections 23/60 tiers - next slot at 25", "Skills 3/20 milestones", and a "Buy 2 slots - 25,000" button (click twice to confirm, like Bazaar Sell inventory). No hover info (hover updates crash the client).

## 4. Build plan
0.3 is already the movement-protocol build, so this starts at 0.4:
- **0.4 - slots + AP:** rarity on every accessory (Quality field), AP + multiplier on the bag page, unlocks from the three live sources, locked cells, Buy button, bridge keys. Needs SkyyCollections 0.1.4 to publish total tiers.
- **0.5 - crystals + tuning:** crystal picker and tuning pages, % modifiers for Health/Stamina/Mana, speed via the movement protocol, combat stats published.
- **0.6+ - later:** enrichments (Legendary only, one small % stat per item, in item metadata like SkyyRolls), a rarity-upgrade item (Recombobulator), Stone crystals, tuning templates, quest slots, HUD AP widget, leaderboard.

## 5. Open questions for Skyy
1. **[SKYY?]** Keep Hypixel's AP values of 3/5/8/12/16?
2. **[SKYY?]** Should bench accessories give AP?
3. **[SKYY?]** Class-locked crystals, or free choice with a bonus for your own class?
4. **[SKYY?]** 60-slot max, these sources, these coin prices?
5. **[SKYY?]** Today's talismans give FLAT Health, Stamina and Mana, but the layer model says accessories give %. Convert them in 0.4 along with the rarity change?
6. **[SKYY?]** Should the Arcane (Mage) crystal ship in 0.5?

---
## Technical notes
- **Storage:** `bags/<uuid>.properties` gains `slotsUnlocked=` (highest ever, so items never get trapped), `slotsBought=`, `crystal=`, `tune.<Stat>=`; `slot9..slot59` once unlocked. Recomputed on page open and the 5 s tick.
- **Bridge writes:** `acc:power:<uuid>` Integer; `acc:slots:<uuid>` "unlocked/60"; `acc:crystal:<uuid>` id; `acc:pct:<uuid>` Map stat->Double (the whole accessory percent layer); `acc:fn:power` Function(UUID)->Integer. `acc:has`, `acc:tal` and `acc:fn:has` are unchanged.
- **Bridge reads (all optional):** `coll:tiers:<uuid>` (new), `skill:<uuid>` (exists), `class:<uuid>` (SkyyClasses), `coins:fn:take` (exists; refuse the purchase if it is missing or returns false).
- **Stat application:**
  - Health/Stamina/Mana: `StaticModifier(MAX, MULTIPLICATIVE)` keys `skyyacc_*_pct` (TerrariaAddons pattern). Verify it applies after ADDITIVE; if not, compute the % and post ADDITIVE.
  - Speed widens the existing `move:<uuid>` pct source to talismans + crystal + tuning.
  - Damage, Defense and Crit get one applier each, elected with `stat:owner:<stat>` (the fallDamage pattern).

## Change (Skyy, 2026-09-23 late): alchemy and cooking are table-only
Alchemy and Cooking are skills now, so their bench accessories go: no Alchemy Bench or Cooking Bench accessory, no Alchemy tab and no cooking recipes in /craft. You brew and cook at the real tables, and those tables draw ingredients from your sacks (the SkyySacks bag link already feeds every vanilla bench window). The Omni accessory stops counting them. Accessories already owned stay as items but do nothing (no recipe). Smelting in the furnace (vanilla Furnace and the SkyySacks Furnace tab) gives Smithing XP.

## Change (Skyy, 2026-09-24): the Campfire accessory is BACK
Quick inventory cooking through the /craft Campfire tab: 50% Cooking XP and 75% of the Cooking skill's bonus (an emergency cook).
The Alchemy Bench and Cooking Bench accessories stay retired (table only). SkyyAccessories 0.4.3 + SkyySacks 0.7.4 + SkyyCooking 0.1.1.
