# Spellbook Ladder (Copper to Onyxium, then 5 new tiers)

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: `research/classes/Mage.md` (Spellbooks), `docs/answered/classes.md` (lines 42-43, the Levitate lock), `docs/answered/gear.md` (lines 12, 43: recipes mirror vanilla weapons, simple Workbench recipes), `research/SkyyArmory-Spec.md` (1.1 ids, 5.1 recipes, 15.2 staff ladder, 15.4 Mana pools), `research/cloud/SkyyArmory-Roadmap.md` (sections 2, 4, 6, Q3), `research/cloud/Weapon-Speed-Tiers.md`, `research/Magic-Traversal-Spec.md` (section 8). Every number is a placeholder and a Server Setup row (times in seconds). Arithmetic checked in python3.

## 0. Decisions followed (LOCKED, not re-decided)

| Lock | Source | Used here |
|---|---|---|
| Spellbook attack = the book's spell; charged = LEVITATE: float up ~8 blocks, hover ~3 s drifting the way you look, land with no fall damage | `docs/answered/classes.md:43`, `research/classes/Mage.md` | Section 2 (spell) and 3 (Levitate). The locked 8 blocks / 3 s is the **Copper** rung; later metals only extend it |
| Mage = staffs + spellbooks; Priest = wands + Soul Orb | `docs/answered/classes.md:42` | Class gate in section 7 |
| Recipes match vanilla weapons: same bench and same metals as that material's other vanilla weapons; simple Workbench recipes for wands, spellbooks and staffs by material | `docs/answered/gear.md:12`, `:43` | Section 6 |
| Traversals cost Mana and Stamina; magical ones 2 parts Mana : 1 part Stamina (10 + 5, 20 + 10) | `docs/answered/classes.md:96`, `research/Magic-Traversal-Spec.md` section 8 | Section 3 |
| Staff cost = 2 x wand; damage multiple `1.25 x (C / 10) - 0.25`; base orb 50 (recommended, S1); all casters launch the same `Skeleton_Mage_Corruption_Orb` | `research/SkyyArmory-Spec.md` 15.2 | The staff is the yardstick (section 2) |
| Metal bands Copper 10-18 ... Onyxium 40-49; new tiers Cindersteel 50-59, Amberite 58-67, Drakonite 66-75, Voidglass 76-88, Aetherium 86-100 | `docs/answered/gear.md:43`, Roadmap section 2 | Both ladders |
| Spellbooks keep a flatter cost ladder, capped at 40% of the pool at band start, and make up power with AREA | Roadmap section 6 | Section 2 |

## 1. Look (art)

- **Base = a leather book**, like Light armor and the wands keep their base: the same brown leather cover and page block on every tier. Only the metal changes.
- **Metal parts:** four corner caps, a spine band, a clasp and a small cover plate with the tier's emblem. Copper is warm orange, Iron grey, Thorium pale green-grey, Cobalt blue, Adamantite deep red-bronze, Mithril silver-blue, Onyxium black with violet lines (the vanilla colour of each metal).
- **New tiers:** Cindersteel dark steel with orange seam lines on the clasp; Amberite gold-brown with a fossil inlay in the plate; Drakonite green-black scale plate with a tiny wing; Voidglass translucent violet plate; Aetherium pale silver-blue with floating rune dots (glow layer).
- Art path: recolour the vanilla `Weapon_Spellbook_*` model and texture per metal with the kit `tools/skyyart.py` (UNVERIFIED: model names). Icon = the closed book; in hand it opens at the burst.

## 2. The spell: Page Burst (a lobbed orb that bursts)

**What it is.** Tap fires a glowing page-orb in a short arc. It bursts where it hits a mob or the ground, or at its max range, into a sphere of **radius R**. Every hostile inside takes the full per-target damage, up to a **targets cap** (nearest to the centre first). No edge falloff by default. Players and allies take nothing (PvP rules as for the staff). Range 20 blocks; a row.

**Why this shape.** Wide-and-short beats a cone for a lobbed spell, needs no aiming at one mob, and the burst point is easy to read (a ring decal for 0.3 s). It is the group tool next to the staff's single-target orb. Teleport is the staff's traversal; the book's is Levitate.

**The rule that sets every number.** Compare per Mana against the staff of the same metal (damage per Mana is the same for quick and charged staff shots: `50 x mult / C`).

- Book cost `B` = 30% of the Mage **fighter** pool at the band start, rounded to 5 (pool = 30 + 10 x level + 0.2 x floor(level / 9), the 15.4 rule; Mithril 430.8 matches 15.4). So a book is about **3.3 casts per full pool** and never above the 40% cap.
- Per-target damage = `k x (staff damage per Mana) x B`, with **k = 0.40** (row `book.k`).
- One target: 0.40 of the staff's damage per Mana (loses). Two: 0.80 (loses). Three: **1.20** (wins). Five: 2.00. So the book only wins at **3+ targets**, by construction, at every tier.

| Tier (band) | Pool at start | Book cost B (share) | Staff charged Mana | B / staff | Staff dmg / Mana | Book dmg per target | Radius R | Targets cap | Dmg per Mana at 1 / 2 / 3 / cap targets (staff = 1.00) |
|---|---|---|---|---|---|---|---|---|---|
| Copper (10-18) | 130.2 | 40 (30.7%) | 20 | 2.00 | 5.63 | 90 | 3.00 | 4 | 0.40 / 0.80 / 1.20 / 1.60 |
| Iron (15-23) | 180.2 | 55 (30.5%) | 30 | 1.83 | 5.83 | 128 | 3.25 | 4 | 0.40 / 0.80 / 1.20 / 1.60 |
| Thorium (20-28) | 230.4 | 70 (30.4%) | 50 | 1.40 | 6.00 | 168 | 3.50 | 5 | 0.40 / 0.80 / 1.20 / 2.00 |
| Cobalt (25-38) | 280.4 | 85 (30.3%) | 80 | 1.06 | 6.09 | 207 | 4.00 | 5 | 0.40 / 0.80 / 1.20 / 2.00 |
| Adamantite (35-43) | 380.6 | 115 (30.2%) | 120 | 0.96 | 6.15 | 283 | 4.25 | 6 | 0.40 / 0.80 / 1.20 / 2.40 |
| Mithril (40-49) | 430.8 | 130 (30.2%) | 170 | 0.76 | 6.18 | 321 | 4.50 | 6 | 0.40 / 0.80 / 1.20 / 2.40 |
| Onyxium (40-49) | 430.8 | 130 (30.2%) | 170 | 0.76 | 6.18 | 321 | 4.50 | 6 | same as Mithril |
| *Cindersteel (50-59)* | 531.0 | 160 (30.1%) | 210 | 0.76 | 6.19 | 396 | 5.00 | 7 | 0.40 / 0.80 / 1.20 / 2.80 |
| *Amberite (58-67)* | 611.2 | 185 (30.3%) | 240 | 0.77 | 6.20 | 459 | 5.25 | 7 | 0.40 / 0.80 / 1.20 / 2.80 |
| *Drakonite (66-75)* | 691.4 | 205 (29.6%) | 270 | 0.76 | 6.21 | 509 | 5.50 | 8 | 0.40 / 0.80 / 1.20 / 3.20 |
| *Voidglass (76-88)* | 791.6 | 235 (29.7%) | 310 | 0.76 | 6.21 | 584 | 5.75 | 8 | 0.40 / 0.80 / 1.20 / 3.20 |
| *Aetherium (86-100)* | 891.8 | 270 (30.3%) | 350 | 0.77 | 6.22 | 671 | 6.00 | 10 | 0.40 / 0.80 / 1.20 / 4.00 |

Notes on the table:
- Damage is the **base-50, before-level** figure like `research/SkyyArmory-Spec.md` 15.2; SkyyGear's level damage multiplies book and staff the same way, so the ratios hold at every level.
- Staff Mana for the new tiers = the Roadmap section 6 column (210 / 240 / 270 / 310 / 350). Mithril and Onyxium match, as for the staffs. Staff columns re-run 2026-10-06 on those costs (python3): staff damage multiples 26.0 / 29.75 / 33.5 / 38.5 / 43.5, staff damage per Mana 6.19 / 6.20 / 6.20 / 6.21 / 6.21, B / staff 0.76 / 0.77 / 0.76 / 0.76 / 0.77; book damage per target, radius, caps and the 1 / 2 / 3 / cap ratios do not move (they depend on B, not on the staff cost).
- The cost ladder is **flatter than 2 x staff**: Copper is exactly 2 x (the live 20 vs 10 ratio), but by Mithril the book is 0.76 x the staff, and 2 x would have been 340 (79% of the pool; the Roadmap said it would not fit).
- The Roadmap section 6 pool column once used 5 Mana per level (the Priest rate, 280 at Lv 50). That is fixed: it now uses the Mage rate (10 per level, 531 at Lv 50), so the staff charged share is 39.5% and the book share about 30% (Q2).
- Cadence: the tap is the spell, no quick/charged split. Medium speed (0.50 s between casts), so Mana, not the timer, limits a Mage to about 3 casts, then regen (5/s, 2.5/s in combat).
- Wood: the live vanilla books (20 Mana, orb 25) stay as they are for now (the same call as Spec RS5); no Wood rung is proposed.

**Weapon speed (`research/cloud/Weapon-Speed-Tiers.md` section 3):** the spellbook is **Medium** (w = 1.0), so the table needs no weighting. The staff is **Slow** (w = 1.4): with `speed.manaScale` on, its cost and damage are both x1.4, so damage per Mana (all that this ladder compares) does not change. Absolute staff Mana in the table is the w = 1 figure.

## 3. Levitate (the charged move; hold)

Hold = the charge, as for staff and wand. Release: you rise to the height, hover while drifting the way you look, then float down; **no fall damage** until the end of the hover plus 3 s (a row). Cost is one payment at the start: **Mana = 2 x Stamina** (the locked ratio; vanilla Stamina Max is 10, so Stamina is capped at 10). A cast that cannot lift you (a ceiling within 2 blocks) costs nothing, as for the blink. Crouching ends the hover early (row `lev.crouchLands`, default on).

| Tier | Height (blocks) | Hover (s) | Drift speed (x walk) | Mana | Stamina | Mana per second of hover |
|---|---|---|---|---|---|---|
| Copper | 8 | 3.0 | 0.8 | 10 | 5 | 3.3 |
| Iron | 8 | 3.0 | 0.8 | 10 | 5 | 3.3 |
| Thorium | 9 | 3.5 | 0.9 | 12 | 6 | 3.4 |
| Cobalt | 10 | 4.0 | 1.0 | 14 | 7 | 3.5 |
| Adamantite | 11 | 4.5 | 1.0 | 16 | 8 | 3.6 |
| Mithril / Onyxium | 12 | 5.0 | 1.1 | 18 | 9 | 3.6 |
| *Cindersteel* | 13 | 5.5 | 1.1 | 20 | 10 | 3.6 |
| *Amberite* | 14 | 6.0 | 1.2 | 20 | 10 | 3.3 |
| *Drakonite* | 15 | 6.5 | 1.2 | 20 | 10 | 3.1 |
| *Voidglass* | 16 | 7.0 | 1.2 | 20 | 10 | 2.9 |
| *Aetherium* | 17 | 8.0 | 1.3 | 20 | 10 | 2.5 |

- Mana is a small part of the pool (10 of 130 at Copper = 7.7%; 20 of 531 at Cindersteel = 3.8%). **Stamina is the real limit**: at Lv 50 and up it takes the whole bar, so Levitate is one move per Stamina refill. That is intended (a traversal, not a flight mode).
- Horizontal reach = hover x drift x walk speed. Walk speed is not a number we know here (UNVERIFIED), so the rows are in "x walk".
- Mage kit synergy (not designed here): Levitate over a pit or trap is the escape; the staff's teleport is the dash.

## 4. Items and ids (SkyyArmory 1.1 id rules)

| Item id | Name | Quality / ItemLevel (that metal's vanilla Sword) | SkyyGear band by the metal word |
|---|---|---|---|
| `Weapon_Spellbook_Copper` | Copper Spellbook | Common / 10 | 10-18 |
| `Weapon_Spellbook_Iron` | Iron Spellbook | Uncommon / 20 | 15-23 |
| `Weapon_Spellbook_Thorium` | Thorium Spellbook | Rare / 30 | 20-28 |
| `Weapon_Spellbook_Cobalt` | Cobalt Spellbook | Rare / 35 | 25-38 |
| `Weapon_Spellbook_Adamantite` | Adamantite Spellbook | Rare / 40 | 35-43 |
| `Weapon_Spellbook_Mithril` | Mithril Spellbook | Epic / 50 | 40-49 |
| `Weapon_Spellbook_Onyxium` | Onyxium Spellbook | Epic / 50 | 40-49 |
| `Weapon_Spellbook_Cindersteel` ... `_Aetherium` (5 later) | Cindersteel Spellbook ... | band quality set with the tier | 50-59 ... 86-100 |

- **No "skyy" in any item id** (`GearData.skyyItem` would stop it being gear). The prefix `Weapon_Spellbook_` is vanilla's, so SkyyGear's spell list and band lookup (metal word from the left) pick them up the same way as the wands.
- Asset ids (interactions, projectiles, the burst, Levitate) are not items and keep the pack prefix: `SkyyArmory_Spellbook_Burst_<Metal>`, `SkyyArmory_Spellbook_Levitate_<Metal>`, `SkyyArmory_Spellbook_Primary_<Metal>` (the item's `Primary`).
- `Tags` `Family: ["Spellbook"]`, `MaxStack` unset (1), copied from the vanilla Spellbook item at build time. Description: `Tap: Page Burst, 40 Mana, hits up to 4 within 3 blocks. Hold: Levitate, 10 Mana + 5 Stamina.` through the lang fallback key.
- Build check: if a Hytale update adds a vanilla `Weapon_Spellbook_<metal>`, stop (as for wands).

## 5. Damage and Mana plumbing

- The burst reuses the carrier orb (Damage 25 as the carrier only; the real damage comes from the burst, set to the per-target figure x SkyyGear level damage). Mana is spent at cast, as for the staff.
- The area scan and the cap are done by a small server hook (like the Meteor ability: nearest first, hostile only). The burst point comes from the orb's hit / miss event.
- SkyyGear's "Charged Attack Damage" line (a spell gets +15% of the roll) applies to **Levitate: no** (no damage); the burst is a tap, so it counts as a normal spell hit.
- Flat per-hit gear lines (True Damage, flat element) apply per target; with w = 1 they scale as for any Medium weapon. A burst hitting 6 targets gets 6 flats, which only adds to its group role (accepted; Q5).

## 6. Recipes (Workbench = the Weapon Bench, as for wands and staffs)

R1 says match vanilla weapons. Wands and staffs mirror **that metal's shortbow** (`research/SkyyArmory-Spec.md` 5.1: one tab for every caster); the book does the same so the Mage finds staff and book side by side. Inputs below are copied from the spec's shortbow table (VERIFIED there); the build reads them again every time.

| Book | Mirrors | Bench / tab / tier | Time | Inputs |
|---|---|---|---|---|
| Copper | Weapon_Shortbow_Copper | Weapon_Bench / Bow / - | 3 s | Copper Bar x4, Wood Trunk x4, Fibre x6 |
| Iron | Weapon_Shortbow_Iron | same / - | 3.5 s | Iron Bar x6, Light Leather x2, Linen Scrap x3 |
| Thorium | Weapon_Shortbow_Thorium | same / 2 | 4 s | Thorium Bar x8, Medium Leather x2, Linen Scrap x3 |
| Cobalt | Weapon_Shortbow_Cobalt | same / 2 | 4 s | Cobalt Bar x10, Heavy Leather x2, Shadoweave Scrap x3 |
| Adamantite | Weapon_Shortbow_Adamantite | same / 3 | 4.5 s | Adamantite Bar x11, Heavy Leather x3, Cindercloth Scrap x3 |
| Mithril | Weapon_Shortbow_Mithril | same / 3 | 5 s | Mithril Bar x6, Storm Leather x2, Voidheart x1 |
| Onyxium | none in vanilla | same / 3 | 5 s | the Mithril recipe with Onyxium Bar x6 (the same fallback as the Onyxium wand and staff) |

- Leather is in every recipe, which fits the "leather book + metal parts" look. Only the shortbow's unrelated Wood / Fibre lines at Copper are odd for a book; accepted, one rule beats a custom one.
- **New tiers (later):** Smithy, collection-gated (R3: coins never skip a collection unlock). Placeholder: tier Bar x6 + the zone leather x2 + the zone core x1 (Ember Core, fossil, dragon scale), recipe level = your class level clamped to the band. Voidglass and Aetherium are **drops only** (Roadmap section 2), so no recipe for those two.
- **Economy check (Bazaar buy = base x 1.10, sell = base x 0.90, spread 22.2%):** the crafted book is never valued above its inputs plus the spread, so a craft-and-sell loop does not pay; the Mage must keep this when the new recipes get prices. Books are bound-by-level like all gear.

## 7. Class gate and other mods

- SkyyClasses today treats the prefix `Weapon_Spellbook_` as a **Priest** weapon (spec section 6, `C:254`). The Mage lock reverses that. The new books are **Mage-only**; existing Priest-only handling (the heal cap, the hit-block popup) must drop the spellbook prefix (UNVERIFIED, see below). Priest keeps the wand and Soul Orb.
- Spellbook hits never heal.

## 8. Server Setup rows (Armory > Spellbooks; times in seconds)

| Row | Default | Meaning |
|---|---|---|
| `book.enabled` | on | whole book ladder |
| `book.k` | 0.40 | per-target damage vs the staff's damage per Mana (0.34-0.49 keeps "wins at 3+") |
| `book.costShare` | 30 | % of the Mage fighter pool a cast costs at band start |
| `book.cost.<metal>` (12 rows) | table in section 2 | Mana per Page Burst |
| `book.radius.<metal>` / `book.targets.<metal>` | table in section 2 | burst radius (blocks) / most targets hit |
| `book.range` | 20 | blocks the orb flies |
| `book.edgeFalloff` | 0 | % less damage at the edge (0 = flat) |
| `lev.height.<metal>` / `lev.hover.<metal>` | table in section 3 | blocks / seconds |
| `lev.drift.<metal>` | table in section 3 | x walk speed |
| `lev.mana.<metal>` / `lev.stamina.<metal>` | table in section 3 | cost; Mana is always shown as 2 x Stamina |
| `lev.safeAfter` | 3 | seconds with no fall damage after the hover |
| `lev.crouchLands` | on | crouch ends the hover |
| `book.recipe.<metal>` | the shortbow's | reads like the wand recipe rows |

## For the local session (UNVERIFIED)

1. **The burst hook:** can an orb's hit / miss event spawn a custom area scan (as `ArmorySpawnSys` already spawns quick orbs)? Fallback: an instant burst at the look point (ray to `book.range`).
2. **Levitate:** vertical velocity and a hover that holds Y: the engine's movement / velocity components, how to cancel fall damage for `lev.safeAfter` seconds, the real walk speed for the "x walk" column.
3. **Model and texture** names of the vanilla spellbooks, and whether a vanilla `Weapon_Spellbook_<metal>` item already exists (the build stop).
4. **Mage pool for 50+:** the 15.4 Mage row (10 per level) is a proposal for SkyySkills 0.4.15 and extrapolated above Lv 49; the book Mana column follows it.
5. **SkyyClasses `C:254`** and the SkyyGear `SPELL_PREFIXES` (`G:831`): which code treats `Weapon_Spellbook_` as a Priest weapon and what moves to Mage.
6. Whether `speed.manaScale` multiplying the staff's cost by 1.4 breaks the 40%-of-pool cap at high tiers (staff Mana x1.4 at Lv 50 is 308 of 531 = 58%).
7. Real Stamina max and regen (10, 1 per second?) used for the Levitate cost; recipe tab for the Weapon Bench (shortbow tab) is VERIFIED only in the wand spec.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Is Page Burst (a lobbed orb that bursts in a sphere, a group tool that loses to the staff on one target) the right feel for the book? | yes |
| 2 | Should the book Mana follow the Mage pool (10 per level, 531 at Lv 50) or the Roadmap's 5 per level (280)? | Mage pool; costs scale to 30% |
| 3 | Is "wins from 3 targets" right (k = 0.40), or 2 targets (k about 0.55)? | 3 targets |
| 4 | Staff speed Slow multiplies its Mana by 1.4 (the section 2 table holds w = 1). Keep that, or make speed damage-only for casters? | keep (`speed.manaScale`) |
| 5 | Flat per-hit gear lines count per target in a burst: fine, or once per cast? | per target |
| 6 | Levitate scales up with metal (8 blocks, 3 s at Copper to 17 blocks, 8 s at Aetherium) or stays 8 / 3 at every tier? | scales up |
| 7 | Recipe: copy the shortbow (leather in every one) or a custom "leather + bars" recipe (fewer Wood / Fibre)? | shortbow copy |
| 8 | Onyxium book gets the Mithril recipe with Onyxium bars (Skyy's wand answer)? | yes |
| 9 | Do you want a Wood book rung (live book 20 Mana stays) or leave the live book as the Wood tier? | leave as is |
