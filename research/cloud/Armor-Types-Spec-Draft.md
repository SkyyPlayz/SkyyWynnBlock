# Armor Types - Heavy / Light / Cloth (spec draft)

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: `docs/answered/gear.md` (the 2026-10-05 armor lines quoted below),
`research/Mob-Curve-Spec.md` (sections 1.3, 2.2, 2.3, 2.7, 5.1-5.2, 6.2), `research/Gear-Levels-Wynn-Spec.md` (sections 3.1, 3.4, 3.5, 7),
`research/cloud/Crude-Armor-Design.md`, `research/cloud/Foraging-Armor-Design.md`, `research/cloud/Weapon-Speed-Tiers.md` (section 7),
`research/SkyyGear-Stage1-Spec.md` (stat keys `cc`, `cd`, `def`, `spd`, `as`), `research/Accessory-Pack-Inventory.md` 2.2, `tools/skyymove.py` (header).
Every number is a placeholder and a Server Setup row (section 9). All arithmetic python-checked (scratch model, deleted).

## 0. Decisions this follows (LOCKED, `docs/answered/gear.md`, 2026-10-05 - not re-decided here)

| Lock | Words (short) |
|---|---|
| ARMOR TYPES | "Anyone can wear any armor; only your class's type gives its bonus stats. Every family covers levels 1-49 through its own tier ladder." |
| LIGHT ARMOR | "first tire is leather armor. then it can be upgraded to copper ... keeps the leather look and adds metal on it" (Leather -> Copper -> ... -> Mithril / Onyxium); metal tiers are our designs, art proof first |
| HEAVY ARMOR | "heavy leather armor set as the first tire below copper ... we will use vanilla armor as heavy armor for now" (`Armor_Leather_Heavy`, then vanilla metal sets) |
| CLOTH | Crude Robe = `Ingredient_Fibre` + `Ingredient_Crystal_Green`, then vanilla tunics Wool -> Linen -> Cotton -> Silk -> Cindercloth |
| ARMOR TYPE STATS (Split) | trade-offs for ANYONE: Heavy slower, most Defense + Health; Light a little faster, medium Defense; Cloth Health + Mana, fastest, least Defense. Class bonus ONLY on-type: Heavy + crit damage (Warrior / Berserker); Light + attack speed + crit chance (Archer / Assassin / Monk); Cloth + Mana regen on higher tiers (Mage / Priest). "Replaces the stat lists in the first armor-types line." |
| Armor box | "HIDE the vanilla armor box ... SkyyGear shows and applies all armor Health / resistance; rides the mob curve build." |
| Wood armor | "remove wood armor from the cloth section ... first tire of foraging armor" |
| Vanilla numbers (NOTE) | Linen Tunic `Armor_Cloth_Linen_Chest` +17 Health, 9% projectile / physical resist; Silk the same + 22 Mana; "SkyyGear sets every Cloth tier's stats from its item level" |

Reading used here: **"Defense" = the armor's Physical / Projectile resistance** (the tooltip's `Resist` line). The rolled `def` stat
(`x 100 / (100 + def)`) is separate and unchanged. The NOTE line said the Cloth bonus (max Mana, regen, spell power) applies to every
cloth tier; the later Split lock replaced the stat lists, so here max Mana is a Cloth trade-off for anyone and the on-type bonus is
Mana regen from the higher tiers (question 4).

## 1. Tier ladders (bands = the metal bands; ids UNVERIFIED unless quoted from a lock)

| Tier | Heavy (Warrior, Berserker) | Light (Archer, Assassin, Monk) | Cloth (Mage, Priest) | Band |
|---|---|---|---|---|
| 1 | Heavy Leather `Armor_Leather_Heavy_*` | Leather `Armor_Leather_Light_*` (Soft / Medium / Raven also Light, same band - Q10) | Crude Robe (new, `Armor_Cloth_Crude_*`?) | 1-13 |
| 2 | Copper `Armor_Copper_*` | Light Copper (new) | Wool `Armor_Cloth_Wool_*`? | 10-18 (Copper armor live 1-18, Q9) |
| 3 | Iron | Light Iron (new) | Linen `Armor_Cloth_Linen_*` (Chest id from Skyy's screenshot) | 15-23 |
| 4 | Thorium | Light Thorium (new) | Cotton | 20-28 |
| 5 | Cobalt | Light Cobalt (new) | Silk | 25-38 |
| 6 | Adamantite | Light Adamantite (new) | Cindercloth (covers 35-49, Q6) | 35-43 |
| 7 | Mithril / Onyxium | Light Mithril / Light Onyxium (new) | (Cindercloth) | 40-49 |
| side | Bronze -> tier 3 band, Steel (`Armor_Steel_Ancient_*`) -> tier 4 band (Q11) | - | - | |

Recipe ideas:
- **Heavy:** vanilla recipes as they are (Heavy Leather and every metal set).
- **Light:** tier 1 = vanilla leather recipe. Each upgrade = the previous Light piece + that metal's bars (half the vanilla metal piece's
  bar count, rounded up) + 2 leather, at the bench that makes the metal armor - the wand rule (wood handle + metal tip). The old piece
  is consumed; the new one keeps rarity + rolled modifiers and is stamped at your class level inside the new band (Q7). No salvage
  path returns more than went in.
- **Cloth:** Crude Robe at the Workbench: Hood 6 Fibre + 1 Crystal, Robe 12 + 1, Trousers 9 + 1, Wraps 4 + 1 (31 Fibre, 4 Crystal - Q14).
  Tunics keep vanilla recipes.

## 2. Health and Defense per level (per piece, then summed)

Per piece, with slot base Health h = Head 5 / Chest 9 / Legs 7 / Hands 4 and slot resist r = 3.6 / 6.48 / 5.04 / 2.88 %
(`base.armor.<slot>`), H(L) = `base.hpCurve`, R(L) = `base.resCurve`, bonus = the band-start material bonus (Gear spec 3.1):

- **Health = h x H(L) x bonus x typeHP**  - Heavy 100 %, Light 90 %, Cloth 90 %
- **Resist = r x R(L) x typeRes**  - Heavy 100 %, Light 80 %, Cloth 60 %
- **Heavy = today's metal numbers exactly**, so the mob curve (built on metal armor, Mob-Curve 2.3) needs no change.

Full set, best tier at the level, same assumptions as Mob-Curve 5.1 (Hard, wolf class 27 bite, 3.0 s cycle, no gear stats):

| Lv | mob HP / bite before armor | Heavy HP / resist | Light HP / resist | Cloth HP / resist / Mana | bites to die H / L / C (raw) | seconds to die H / L / C | Mage -15 % in Cloth |
|---|---|---|---|---|---|---|---|
| 1 | 103 / 27 | +25 / 18.0 % | +22 / 14.4 % | +22 / 10.8 % / +15 | 6 / 6 / 6 (5.65 / 5.30 / 5.09) | 18 / 18 / 18 | 5 |
| 10 | 177 / 37 | +50 / 25.2 % | +45 / 20.2 % | +45 / 15.1 % / +30 | 6 / 6 / 5 (5.61 / 5.08 / 4.78) | 18 / 18 / 15 | 5 |
| 20 | 260 / 48 | +62 / 30.6 % | +56 / 24.5 % | +56 / 18.4 % / +35 | 6 / 5 / 5 (5.12 / 4.53 / 4.19) | 18 / 15 / 15 | 4 |
| 30 | 577 / 82 | +145 / 35.1 % | +131 / 28.1 % | +131 / 21.1 % / +40 | 5 / 5 / 4 (4.82 / 4.11 / 3.74) | 15 / 15 / 12 | 4 |
| 40 | 1358 / 134 | +269 / 39.6 % | +242 / 31.7 % | +242 / 23.8 % / +45 | 5 / 4 / 4 (4.74 / 3.90 / 3.49) | 15 / 12 / 12 | 3 |
| 49 | 2526 / 208 | +437 / 41.8 % | +393 / 33.4 % | +393 / 25.1 % / +50 | 5 / 4 / 4 (4.56 / 3.68 / 3.27) | 15 / 12 / 12 | 3 |

(max HP = 100 + armor + the small skill part from Mob-Curve 2.3; bites = ceil(max HP / (bite x (1 - resist))).)

**Time to kill at the same level** does not depend on armor Health; only the class bonus moves it (section 4). Mob-Curve 5.2's +0 rows
stay: Warrior 14 / 12 / 14 / 16 (Lv 33) / 17 swings at Lv 1 / 10 / 20 / 33 / 49, Mage and Priest 1-2 shots from Lv 10.

Checks against the mob curve:
- Heavy is byte-for-byte today's - the Mob-Curve rule "same level = today's Hard" holds for metal wearers.
- Light loses about 1 bite at Lv 20+ (-12 to -19 % raw), Cloth about 1-1.5 (-10 to -28 %). Nobody drops below 3 same-level bites.
- Casters kill a same-level mob in 1.7-2.0 s (1-2 shots) against 9-12 s to die in Cloth - the race is still won by a wide margin.
- The weak spot: a Lv 40+ Mage at -15 % in Cloth dies in 3 bites. Mob-Curve 2.7's Mage survival tool (6-8 % max Health back per
  charged cast) is now a must for the class round, not a nice-to-have.
- Vanilla check: our Lv 15 Linen chest = 18 Health / 6.0 % (vanilla 17 / 9 %) - close on Health, lower on resist as Cloth should be.

## 3. Movement speed trade-off (anyone)

| Full set | Speed | Per piece (Head / Chest / Legs / Hands = 20 / 36 / 28 / 16 % of the set) |
|---|---|---|
| Heavy | -5 % | -1.0 / -1.8 / -1.4 / -0.8 |
| Light | +4 % | +0.8 / +1.44 / +1.12 / +0.64 |
| Cloth | +8 % | +1.6 / +2.88 / +2.24 / +1.28 |

- Flat, not level-scaled. Posted by SkyyGear in its existing `gear.armor` source on the **flat layer** (Skyy 2026-09-23: skills + armor
  = flat, accessories = percent on top): factor = clamp((1 + Acrobatics + armor spd + type) x (1 + accessories), 0.3, 5).
- **Cap:** the armor-type part is clamped to -10 % ... +10 % (row), on top of the protocol's 0.3-5 clamp.
- Stacking, python-checked (Heavy / none / Light / Cloth): Acrobatics 0: 0.95 / 1.00 / 1.04 / 1.08; Acrobatics +50 % with a +10 % Speed
  accessory: 1.595 / 1.65 / 1.694 / 1.738. Cloth vs Heavy = +13.7 % at Acro 0, +9 % at Acro 50, +6.7 % at Acro 100.

## 4. Class bonus (only when your class matches the type; per matching piece, by the same 20 / 36 / 28 / 16 split)

| Tier | 1 | 2 | 3 | 4 | 5 | 6 | 7 (Mithril / Onyxium) |
|---|---|---|---|---|---|---|---|
| Heavy: Crit Damage % (`cd`) | 5 | 8 | 12 | 15 | 18 | 22 | 26 |
| Light: Crit Chance % (`cc`) | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| Light: Attack Speed % (`as`, HIDDEN) | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| Cloth: Mana Regen % (Crude, Wool, Linen, Cotton, Silk, Cindercloth) | 0 | 0 | 0 | 10 | 20 | 30 | - |

Effect on same-level kill time (python-checked; assumes 10 % crit chance from gear, crit = x2 x (1 + cd)): Heavy -0.9 % (Lv 1) to
-4.5 % (Lv 40+); Light -1.8 % to -6.8 %, and -3.7 % to -13.7 % once Attack Speed is live. Cloth Mana regen adds to SkyySkills'
`ManaRegen.total` (in-combat 2.5 / s; Mob-Curve's +7 % per class level above 20 stacks additively). Heavy is the smallest kill
bonus because it already has the most Health and Defense. Other classes see the line grey: "Warrior / Berserker: Crit Damage +8 %".

## 5. Mixed sets

Everything is **per piece**: each piece gives its own type's Health, resist, speed and Mana share, and its class bonus share only if
it matches your class. No set bonus, no "majority type" rule (Q13). Example (Lv 20, Archer): Light chest + Light legs + Heavy head +
Heavy hands = speed +1.44 +1.12 -1.0 -0.8 = +0.76 %; crit chance (5 x 0.64) = +3.2 %; Health and resist add piece by piece.

## 6. Wood / Foraging armor

No armor type: no speed change, no class bonus (`research/cloud/Foraging-Armor-Design.md` already says it never competes for the class
bonus). Proposed change to that draft: Health and resist = **50 % of the Heavy formula at the item's level** (rows `type.none.hp` /
`type.none.res`) instead of fixed vanilla-based numbers, so it follows the new H(L). Lv 1 Wood: +12 HP / 9 %; Lv 40 Redwood: +134 HP /
19.8 % (2-3 same-level bites - a gathering set, by design). Its Fortune / chopping speed / Tree Feller stay as that draft says.

## 7. Attack Speed status

`as` is a **later** stat (SkyyGear-Stage1-Spec): it needs the per-family swing override from `research/Swing-Speed-Spec.md`, which the
weapon speed tiers also need (`research/cloud/Weapon-Speed-Tiers.md` section 7). Until that ships: Light's Attack Speed is stored in
the type table, **not applied, not in tooltips, not on the Stats page** (no grey "coming later" line - "never advertise a stat that
does nothing"). Row `type.light.asLive` (off) turns it on in the same build that makes `as` live; the 150 % cap applies to the total.

## 8. Build plan

| Step | What | Round |
|---|---|---|
| A | Art proof: `tools/skyyart.py` preview sheet per Light metal tier (black leather + metal accents; above Copper echo the vanilla set) for Skyy to pick | local, no agents |
| B | SkyyGear, riding the mob-curve SkyyGear version (with the armor-box hide): type map (item prefix -> type), typeHP / typeRes multipliers, speed post, Cloth max Mana, class bonus (`cc`, `cd` live; Mana regen through a `skyy.bridge` source for SkyySkills), tooltip type line + grey class line, Stats page values | full round (every armor piece, cross-mod, several mods) |
| C | New items: Crude Robe (4 pieces) + Light Copper ... Onyxium (assets generated at build time from vanilla leather models, never committed), upgrade recipes, Bronze / Steel classification | full round (items that could be lost in an upgrade) |
| D | Attack Speed on (`type.light.asLive`) together with the weapon speed mechanism | with the weapon-speed round |

Harness checks: every Heavy piece's Health / resist identical to the curve build without types; the section 2 table re-derived from
the jar; per-piece sums for a mixed set; class mismatch = no bonus; unknown armor = type None (no change); speed post never outside
the cap; Light `as` value never reaches a stat map while `asLive` is off. Until step C, Light covers only Lv 1-13 (Archers wear Heavy or
Cloth above that) - say so in the TEST-CHECKLIST section.

## 9. Server Setup rows (Gear -> new tab "Armor types", config kit)

| Key | Label | Type | Default | Range |
|---|---|---|---|---|
| part.armorTypes | Armor types | bool | true | |
| type.map | Armor type by item | table `choice;none;Type` (Heavy / Light / Cloth / None), key = item id or `Prefix*` | section 1 | |
| type.classes | Classes per type | table `text;none;Classes` | Heavy: Warrior, Berserker; Light: Archer, Assassin, Monk; Cloth: Mage, Priest | |
| type.heavy.hp / .light.hp / .cloth.hp / .none.hp | <Type> Health | int % | 100 / 90 / 90 / 50 | 10-300 |
| type.heavy.res / .light.res / .cloth.res / .none.res | <Type> Resist | int % | 100 / 80 / 60 / 50 | 10-300 |
| type.heavy.spd / .light.spd / .cloth.spd | <Type> speed, full set | dec % | -5 / 4 / 8 | -50-50 |
| type.spdCap | Armor type speed at most | dec % | 10 | 0-50 |
| type.cloth.mana | Cloth Mana at Lv 1 | int | 15 (x spell curve S(L)) | 0-500 |
| type.heavy.cd / type.light.cc / type.light.as / type.cloth.regen | <bonus> per tier | table `dec;none;Value`, key = tier 1-7 | section 4 | 0-100 |
| type.light.asLive | Light Attack Speed live | bool | false | |
| type.greyLine | Show other classes' bonus grey | bool | true | |

## For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | Item ids: `Armor_Leather_Heavy_*`, `Armor_Leather_Light/Soft/Medium/Raven_*`, `Armor_Cloth_Wool/Linen/Cotton/Silk/Cindercloth_*`, `Armor_Bronze_*`, `Armor_Steel_Ancient_*`, Onyxium; whether each cloth tier has all 4 slots |
| 2 | `Ingredient_Crystal_Green` drop rate from `Drop_Golem_Crystal_Earth`, and that this golem is Skyy's "temple guardian" |
| 3 | Vanilla armor speed: do Heavy Leather / metal sets already carry a movement modifier the hide must cancel? |
| 4 | `spd` decimals and negative values through `gear.armor` (flat layer) in `tools/skyymove.py` appliers |
| 5 | How SkyyGear reads the player's class (beyond `GearGate.gateSkill(u, "class")`) and a SkyySkills bridge source for Mana regen |
| 6 | Max Mana from armor: a `StaticModifier` on the Mana stat like the Health one (vanilla Silk proves armor can) |
| 7 | Bench names for the Light upgrade recipes; vanilla metal piece bar counts |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Heavy = today's metal armor numbers; Light 90 % Health / 80 % Defense; Cloth 90 % Health / 60 % Defense? | [yes] |
| 2 | Speed full set: Heavy -5 %, Light +4 %, Cloth +8 %, never past +-10 %? | [yes] |
| 3 | Class bonus per tier as in section 4 (Heavy crit damage 5-26 %, Light crit chance 2-8 %)? | [yes] |
| 4 | Cloth Mana regen from Cotton up (+10 / 20 / 30 %); max Mana for anyone in Cloth? | [yes, yes] |
| 5 | Light Attack Speed fully hidden until it works, nothing in its place? | [yes] |
| 6 | Cindercloth covers Lv 35-49 (no 7th cloth tier until the Lv 50+ tiers)? | [yes] |
| 7 | A Light upgrade keeps rarity + rolled modifiers and restamps the level at yours? | [yes] |
| 8 | Drop the separate Crude armor set (`research/cloud/Crude-Armor-Design.md`) - each type's tier 1 replaces it? | [yes] |
| 9 | Copper armor band back to 10-18 now Heavy Leather sits below it? | [keep 1-18 (your 2026-10-01 lock) until you say] |
| 10 | Soft / Medium / Raven leather count as Light tier 1? | [yes] |
| 11 | Bronze = Heavy at the Iron band, Ancient Steel = Heavy at the Thorium band? | [yes] |
| 12 | Foraging armor Health / Defense = 50 % of Heavy at its level, no speed change? | [yes] |
| 13 | Mixed sets per piece, no full-set bonus? | [yes] |
| 14 | Crude Robe = 31 Fibre + 4 green crystals (1 per piece)? | [yes] |
