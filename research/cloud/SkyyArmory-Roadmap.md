# SkyyArmory roadmap - next items per class and our own Lv 50-100 tiers

Cloud draft, 2026-10-06. Paper plan; nothing built. Inputs read: `research/SkyyArmory-Spec.md` (0.1 metal wands + section 15 staffs), `research/classes/*.md`, `docs/answered/gear.md` (armor types, Heavy/Light/Cloth locks), `research/Gear-Levels-Wynn-Spec.md`, `research/cloud/` Monk-Kit, Soul-Orb, Mob-Levels-Refit, Capstone-Dungeon, Zone-Bosses, Crude-Armor. Web research (search snippets only; wiki hosts are blocked): [Hytale weapons (Prima Games)](https://primagames.com/tips/all-weapons-and-how-to-craft-them-in-hytale), [Hytale armor (G-Portal)](https://www.g-portal.com/wiki/en/hytale-armor/), [Wynncraft Class](https://wynncraft.wiki.gg/wiki/Class), [Wynncraft Relic weapons](https://wynncraft.wiki.gg/wiki/Relic_Weapons). All names and numbers are **proposals** for Skyy. Facts that need the game files are marked UNVERIFIED.

## 0. Where we are (from the repo)

| Piece | State |
|---|---|
| SkyyArmory 0.1 | **wands**: Copper, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium, art style B (wood handle + metal head), spec'd in full; Mana 5/10/15/25/40/60/85 for the charged shot |
| Staffs | spec'd in section 15 (cost = 2 x the wand, damage multiple `1.25 x (C/10) - 0.25`, base orb 50) |
| Priest Soul Orb | spec'd (`research/cloud/Soul-Orb-Spec.md`, 8 tiers) |
| Monk Bo staff + fists | spec'd (`research/cloud/Monk-Kit-Spec.md`) |
| Everything else | vanilla weapons for now (Warrior sword/longsword/spear, Archer shortbow/crossbow, Berserker axe/battleaxe/mace/club, Assassin dagger); kunai is new |
| Armor | three types locked (Heavy = plate, Light = leather + metal accents, Cloth = robes); all ladders stop at **Lv 49** (vanilla's top: Mithril, Onyxium). Search snippets say **Onyxium has a full gear set in the game files but is not obtainable**, Mithril armor is creative-only (UNVERIFIED) |
| Bands | Wood/Crude 1-13, Copper 10-18, Iron 15-23, Thorium 20-28, Cobalt 25-38, Adamantite 35-43, Mithril/Onyxium 40-49 (LOCKED) |

The gap: **nothing exists for Lv 50-100**, and Zone 4 (Lv 45-60), Zone 5 (Lv 60-75), the dragon (75) and the capstone (76-100) need gear (Zone-Bosses, Capstone: "our own Lv 50-100 tiers drop here").

## 1. Wynncraft lessons (what to copy)

| Wynncraft | Our use |
|---|---|
| Four weapon types by class (bow, spear, wand, dagger) plus relic | we already have 2 weapon types per class; each type keeps **its own pace** (attack speed) and traversal |
| Item tiers Normal / Unique / Rare / Legendary / Fabled / Mythic / Set | already our rarity ladder (SkyyGear) |
| High-level gear is found, mostly **dropped**, not bought | Zone 4-5 tiers craftable, capstone tiers **drop only** |
| Level-gated, level-bound ranges that overlap | our bands overlap the same way |

## 2. The new tier ladder (Lv 50-100)

Five new tiers, one per step of the zones. Names are working names in our own voice (none copy Hypixel or Wynncraft gear names). Bands overlap by about 8 levels like the vanilla ones.

| # | Tier | Zone / source | Band | How you get it | Look and theme |
|---|---|---|---|---|---|
| T8 | **Cindersteel** | Zone 4 Devastated Lands (ember ore + Ember Core from the guardian) | **50-59** | craft (Smithy; collection-gated) | dark steel with glowing orange seams |
| T9 | **Amberite** | Zone 5 dinosaur caves (amber + fossil, cave ore) | **58-67** | craft (collection-gated), drops from Zone 5 elites | warm gold-brown, fossil inlays |
| T10 | **Drakonite** | Zone 5 deep + the dragon (dragon scale) | **66-75** | craft from dragon scales (a boss gate), also drops | green-black scales, a tiny wing motif |
| T11 | **Voidglass** | capstone floors 1-4 | **76-88** | **drops only** (unidentified gear from the Final Audit), optionally craftable from "Voidglass Shards" later | translucent violet glass over dark metal |
| T12 | **Aetherium** | capstone floors 5-7 | **86-100** | **drops only**; the **Set** rarity pieces (green, 3-piece bonuses) are Aetherium and Voidglass | pale silver-blue, floating runes |

Rules:

- **Crafting level = your class level**, like today (SkyyGear), clamped to the band. Drops roll inside the band.
- Rarity weights, reforges, identify, the level gate: all SkyyGear, no new engine (the level range is 0-100 already, VERIFIED in `GearLevel.clamp` per Gear-Levels-Wynn-Spec).
- **Tiers use a common stat identity** so the pool is not a pile of random numbers (section 5).
- Tools (pickaxe, axe, hoe): same names, Lv 50+ later (Tool-Levels-Spec R13).

## 3. Which models to reuse (UNVERIFIED until the game files are read)

| Tier | Weapons | Armor |
|---|---|---|
| T8 Cindersteel | **recolour of the vanilla Onyxium model per type** (its full set exists in the files, not obtainable), new texture (kit `tools/skyyart.py`) | recolour vanilla Onyxium plate, Light = leather with Cindersteel accents, Cloth = Cinderweave robe (new) |
| T9 Amberite | recolour the Mithril model | same pattern |
| T10 Drakonite | Onyxium model + a scale texture | same pattern |
| T11-T12 | the same models with glass/rune textures (a small additive overlay for glow) | same pattern |

Rule (PROJECT-RULES 2): **generate every texture at build time from vanilla files, never commit vanilla or vanilla-derived assets** (the wand art kit already does this). A recolour never needs a new model, so each tier costs textures + ids + recipes, not modelling.

**Wand/staff style rule (locked):** wooden handle + metal head, so a Priest/Mage's weapon keeps the wood look at every tier; the heads are `Metal` colours from the table above.

## 4. Per class: what to build next

Order inside a class = the order of the build list in section 6. "Vanilla" means the vanilla weapon already has all 7 metals up to Onyxium.

| Class | Weapons (types) | Now | Next to build | Lv 50-100 version |
|---|---|---|---|---|
| **Priest** | Wand, Soul Orb | wands spec'd, orb spec'd | 1. Wands 0.1 (live next) 2. Soul Orb ladder (8 tiers incl. Wood/Cobalt cage) | Wand and Orb at T8-T12 |
| **Mage** | Staff, Spellbook (updated 2026-10-06: spellbooks are a **Mage** weapon, but SkyyClasses gates the `Weapon_Spellbook_` prefix as **Priest** today - the books need the class gate moved to Mage and the Priest heal-cap / hit-block handling to drop the prefix, UNVERIFIED; see Spellbook-Ladder.md section 7) | staffs spec'd | 1. Staffs 2. **Spellbooks**: no metals exist; a book is **leather + metal clasp/cover** (same "keep the base, add metal" idea as Light armor); 7 books Copper to Onyxium | Staff + Spellbook at T8-T12; Spellbook cost = 2 x staff in Mana (the spec's spellbook 20, so x4 of the wand) |
| **Archer** | Shortbow, Crossbow | vanilla | 1. **Crossbow ladder check**: vanilla has crossbows? (UNVERIFIED which metals) 2. add a **quiver/holster** accessory slot later (updated 2026-10-06: the locked "holstered crossbow reloads in 30 s" is a tree node at Archery Lv 75, not an accessory - Archer-Bolts-Holster.md; "extra bolts" = magazine 6 -> 10) | Shortbow, Crossbow at T8-T12 |
| **Warrior** | Sword (+longsword), Spear | vanilla | 1. nothing new at Lv 1-49 2. **Spear Leap** traversal (idea) | Sword, Longsword, Spear at T8-T12 |
| **Berserker** | Axe, Battleaxe, Mace, Club | vanilla | 1. nothing new at Lv 1-49 2. Leap Slam / Bull Rush (ideas) | Axe, Battleaxe, Mace at T8-T12 (Club stays crude) |
| **Monk** | Bo staff, Fists (wraps/gauntlets/claws) | spec'd (Monk-Kit) | 1. **Bo staff ladder** (Wood to Onyxium) 2. **Fist family** (cloth wraps, leather-and-metal gauntlets, claws) | Bo staff, Gauntlets, Claws at T8-T12 |
| **Assassin** | Dagger, **Kunai** | kunai new | 1. Kunai ladder (thrown, stack of 1; the metal ladder mirrors daggers) 2. Smoke Roll (idea) | Dagger + Kunai at T8-T12 |

**Counts (to size the work):** 19 weapon types (wand, orb, staff, spellbook, bow, crossbow, sword, longsword, spear, axe, battleaxe, mace, club, bo staff, wraps, gauntlet, claw, dagger, kunai) x 5 new tiers = **95 weapon items** if every type gets every tier. Armor: 3 types x 4 pieces x 5 tiers = **60 pieces**. That is too much for one release, so the build is staged (section 6).

## 5. Stat identity (Wynncraft-inspired, our own)

Each **tier** has a small signature so tiers feel different, not just bigger. The signature is a **bias in the modifier pool** (SkyyGear stat catalog), never a new engine feature.

| Tier | Signature (mod weights x1.5) | Element link |
|---|---|---|
| Cindersteel | Strength, Fire damage, Health regen | Fire |
| Amberite | Defense, Health, Earth damage | Earth |
| Drakonite | Crit Damage, Strength, Speed | Air (wings) |
| Voidglass | Mana (max, regen), Magical Power, Thunder damage | Thunder |
| Aetherium | all five of the above at x1.2, plus rare Major IDs | all |

Each **armor type** keeps its locked identity: Heavy = most Defense/Health + crit damage, Light = speed, attack speed, crit chance, Cloth = Health, Mana, even more speed, Mana regen on high tiers (all per `docs/answered/gear.md`).

**Weapon pace:** superseded by `research/cloud/Weapon-Speed-Tiers.md` (checked 2026-10-06: pointer is present and current) (Skyy's four tiers Slow / Medium / Fast / Super Fast, same DPS, per-hit weight from the real attack interval; it replaces the x1.6 / x1.0 / x0.6 placeholders that were here).

## 6. Magic weapons: extending the Mana ladder (the one math job here)

Skyy's rule (SkyyArmory section 15): staff cost = 2 x wand; damage multiple `1.25 x (C / 10) - 0.25` for staff cost C. (updated 2026-10-06: the pools now come from `research/SkyyArmory-Spec.md` 15.4, not the old "30 + 5 per level" guess.) Fighter pool at a band start = `30 + r x L + 0.2 x floor(L / 9)` with **r = 5 for the Priest (wand)** and **r = 10 for the Mage (staff)**; 15.4 prints 230.8 / 430.8 at Lv 40 and 531 at Lv 50 (Lv 50+ is the same rule carried up, UNVERIFIED above Lv 49). Rule for the 5 new tiers: **keep casts per full pool at the Mithril rung's figure** (wand 2.7, staff 2.5), i.e. the charged share of the pool stays at Mithril's (wand 36.8%, staff 39.5%, the 15.4 caps of 37% / 40%), rounded to 5.

| Tier | Level (band start) | Wand charged Mana | Staff charged Mana | Priest pool | Mage pool | Wand share / casts per pool | Staff share / casts per pool | Staff damage multiple |
|---|---|---|---|---|---|---|---|---|
| Copper | 10 | 10 | 20 | 80.2 | 130.2 | 12.5% / 8.0 | 15.4% / 6.5 | 2.25 |
| Iron | 15 | 15 | 30 | 105.2 | 180.2 | 14.3% / 7.0 | 16.6% / 6.0 | 3.5 |
| Thorium | 20 | 25 | 50 | 130.4 | 230.4 | 19.2% / 5.2 | 21.7% / 4.6 | 6.0 |
| Cobalt | 25 | 40 | 80 | 155.4 | 280.4 | 25.7% / 3.9 | 28.5% / 3.5 | 9.75 |
| Adamantite | 35 | 60 | 120 | 205.6 | 380.6 | 29.2% / 3.4 | 31.5% / 3.2 | 14.75 |
| Mithril / Onyxium (today) | 40 | 85 | 170 | 230.8 | 430.8 | 36.8% / 2.7 | 39.5% / 2.5 | 21.0 |
| **Cindersteel** | 50 | **105** | **210** | 281.0 | 531.0 | 37.4% / 2.7 | 39.5% / 2.5 | 26.0 |
| **Amberite** | 58 | **120** | **240** | 321.2 | 611.2 | 37.4% / 2.7 | 39.3% / 2.5 | 29.75 |
| **Drakonite** | 66 | **135** | **270** | 361.4 | 691.4 | 37.4% / 2.7 | 39.1% / 2.6 | 33.5 |
| **Voidglass** | 76 | **155** | **310** | 411.6 | 791.6 | 37.7% / 2.7 | 39.2% / 2.6 | 38.5 |
| **Aetherium** | 86 | **175** | **350** | 461.8 | 891.8 | 37.9% / 2.6 | 39.2% / 2.5 | 43.5 |

The first 7 rungs are **LOCKED and unchanged**, and they stay sane under the real pools: shares climb 12.5% to 36.8% (wand) and 15.4% to 39.5% (staff), never over the 37% / 40% caps; casts per pool fall 8 to 2.7 (wand) and 6.5 to 2.5 (staff). Quick shot stays C / 5.

**Change from the first draft:** the old table (wand 110 / 125 / 140 / 160 / 180, staff 220 / 250 / 280 / 320 / 360) was built on a Priest-rate pool used for both classes. Against the real Mage pool its staff share was 41.4% / 40.9% / 40.5% / 40.4% / 40.4%, just over the 40% cap, and 5 Mana per rung too dear for the wand. The new costs are 5 / 5 / 5 / 5 / 5 lower, so the share at every new rung sits at Mithril's. The staff damage multiple drops a little with them (27.3 / 31.0 / 34.8 / 39.8 / 44.8 become 26.0 / 29.75 / 33.5 / 38.5 / 43.5); damage per Mana is unchanged (6.2 per Mana at base 50).

**Speed-tier scaling** (`research/cloud/Weapon-Speed-Tiers.md` section 5: cost = base x w, damage = base x w, so damage per Mana is unchanged). The wand is Medium (w 1.0): the table is exact. The staff is Slow (w 1.4), so with `speed.manaScale` on its real charged cost is the staff column x 1.4:

| Rung | Staff column | Slow staff cost (x 1.4) | Share of Mage pool | Casts per pool |
|---|---|---|---|---|
| Copper | 20 | 28 | 22% | 4.6 |
| Adamantite | 120 | 168 | 44% | 2.3 |
| Mithril | 170 | 238 | 55% | 1.8 |
| Cindersteel | 210 | 294 | 55% | 1.8 |
| Aetherium | 350 | 490 | 55% | 1.8 |

Notes: the steady share keeps the spell economy the same shape at every rung, Slow or not (Slow staff: about 1.8 casts per pool, the cost of a heavy hit; a Fast w 0.7 staff would give about 3.6). The 40% cap is for the w = 1 column; with Slow the staff passes it from Cobalt up already (Mithril 55% today), so that is a Slow-staff property, not a new-tier problem (Q6). `research/cloud/Spellbook-Ladder.md` is Medium (w 1.0), costs 30% of the Mage pool (book 160 / 185 / 205 / 235 / 270, unchanged by this table) and uses the 15.4 Mage row already; only its "Staff charged Mana" column and "B / staff" ratio still read 220 / 250 / 280 / 320 / 360 and become 210 / 240 / 270 / 310 / 350 (ratios 0.76 / 0.77 / 0.76 / 0.76 / 0.77), and its note on the 5-per-level pool can go. Spellbook charged Mana = 2 x staff would exceed the pool, so books keep a flatter cost ladder and make up the difference with **area** (Q3).


## 7. Build stages (the main session decides rounds; weapons are items + recipes + assets, usually a **lean round** each, a **full round** when it touches several mods)

| Stage | Contents | Needs |
|---|---|---|
| A | Wands 0.1 (7 metals) | designed |
| B | Staffs | SkyyArmory section 15 |
| C | **Spellbooks** (7 metals) | design (Q3) |
| D | Soul Orb 8 tiers | Soul-Orb-Spec |
| E | Monk: Bo staff + fists | Monk-Kit-Spec |
| F | Kunai ladder | Assassin kunai traversal |
| G | **T8 Cindersteel** for the **main weapon of each class** (wand, staff, shortbow, sword, axe, bo staff, dagger = 7 items) + 3 armor sets (12 pieces) = **19 assets**, with Zone 4 ore, Smithy recipes, collection gates | mob curve to Lv 60, Zone 4 world gen |
| H | T8 for the remaining weapon types | G |
| I | T9 Amberite + T10 Drakonite (Zone 5; dragon scale craft) | Zone 5, dragon quest |
| J | T11-T12 + the **Set** rarity pieces (capstone drops) | capstone dungeon |
| K | Lv 50+ tools and the gathering armor extension | Tool-Levels-Spec, Collection-Unlocks |

Each stage deploys alone, and no stage needs another to **exist** (item ids stay stable).

## 8. Server Setup rows (sketch)

`armory.tier.<name>.enabled`, `armory.tier.<name>.levelMin/Max` (the bands), `armory.mana.<weapon>.<tier>` (charged cost; quick = /5), `armory.pace.*` (updated 2026-10-06: replaced by the `speed.*` rows of Weapon-Speed-Tiers.md section 8: four tiers slow / medium / fast / superfast, not three), `armory.craft.collectionGate` (on). All times in seconds.

## For the local session (UNVERIFIED)

- The vanilla item ids of the Onyxium/Mithril sets (weapons and armor) and whether recolouring them as assets is allowed (files stay in Assets.zip; textures are generated at build time).
- Which vanilla crossbow/longsword/club metals exist.
- Whether SkyyGear's level range and stat curve are sound above Lv 49 (the Mob-Curve spec covers up to Lv 60).
- The real Mana pool rule above 40 (the 15.4 rows are a proposal for SkyySkills 0.4.15 and carried up to Lv 86 here); whether the cost path takes fractional Mana (Slow x 1.4 gives tenths).
- Whether a recoloured Onyxium set would clash with a future vanilla release that makes Onyxium obtainable (the build check in SkyyArmory 1.1 already stops on an id clash).

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Do the five names (Cindersteel, Amberite, Drakonite, Voidglass, Aetherium) work, or do you want your own? | yes |
| 2 | Capstone tiers (Voidglass, Aetherium) drop only, or also craftable from shards? | drop only at launch |
| 3 | Spellbooks: leather + metal clasp ladder (7 metals), area-based power instead of raw Mana? | yes |
| 4 | First wave (stage G): only the main weapon per class plus 3 armor sets? | yes |
| 5 | Weapon pace: see `research/cloud/Weapon-Speed-Tiers.md` questions | - |
| 6 | New-tier Mana 105 / 120 / 135 / 155 / 175 (wand) and double (staff) instead of the first draft 110 ... 180? A Slow staff then costs 55% of the Mage pool per charged shot (x 1.4): keep, or make speed damage-only for casters? | new costs; keep `speed.manaScale` |
