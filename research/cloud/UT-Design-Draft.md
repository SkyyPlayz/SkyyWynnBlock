# UT design draft - 12 armor sets + 32 weapons (Zones 2-5, plus the Zone 1 Spellblade)

Cloud draft, 2026-10-23. Paper design only. Nothing here is built, recorded as a decision, or a number the balance model has checked.
Every engine fact is **UNVERIFIED** (no game files here). Names are working names; Skyy picks.

## Decisions followed (all in `docs/answered/gear.md`, newest wins)

| Line | What Skyy locked | Used here |
|---|---|---|
| 123 / 124 (2026-10-08) | RotMG-style UT: good in its band, never strictly better; orange; Mythic = boss gear | every row is one upside + one real downside |
| 126-127 (2026-10-08) | UT = mob drops, loot chests, bosses, quests; never crafted, never in NPC shops | Source column; no recipe, no shop |
| 252-253 (2026-10-17) | UT and Mythic are per ZONE (not per tier), always the zone's top tier | one band per zone |
| 270 (2026-10-18) | per zone: 3 UT armor sets (Cloth, Light, Heavy) + 1 UT weapon per class | 3 sets x Zones 2-5 = 12; weapons below |
| 272 (2026-10-18) | the class's UT weapon alternates primary / alt: Z1 primary, Z2 alt, Z3 primary, Z4 alt, Z5 primary | weapon table types |
| 273 (2026-10-18) | UT = tradeoff (slow but huge hits; fewer damage but pierce; robes less Mana but HP / defence; heavy the opposite) | all trade-offs |
| 285 (2026-10-18) | UT = the zone's alloy tier, late in the zone; sources = elites, mini bosses, dungeons; Mythic = full bosses only | tier tag + source |
| 313 (2026-10-22) | UT tuned so every UT item is at least Fabled at its level (`utline.power` / per-item `utpow`) | no extra power budget in this file |
| 314 (2026-10-22) | UT bands move to the END of the zone | bands below |
| 319 (2026-10-22) | crafted items never UT / Mythic | no recipes, ever |
| 271 (2026-10-18) | the 5 Armory UTs ship as drafted (`research/UT-Lines-Draft.md` 2.1) | Hepta Axe fills a slot; no duplicate |
| 274 (2026-10-18) | elements built first; UTs use them | optional Element column (weapon only, SkyyGear-Plan lock 17) |

Also followed: `PROJECT-RULES.md` (tier tag first in the flavor text; four power sources; sort by tier; colour code in
`research/Vanilla-UI-Style-Guide.md` section 15; no dev gates - rows ship ON), `research/Menu-Pattern.md` (no new menu needed).

## 1. What exists already (not duplicated)

Built, Zone 1 (`research/cloud/UT-First-Batch-Build.md`): Filing Cabinet (Heavy, +Health / -damage), Courier's Leathers (Light, speed + crit /
+damage taken), Intern's Robes (Cloth, Mana regen / -Health); weapons Loophole (staff, pierce / -damage), Paperweight (sword, Slow), Overtime
(battleaxe, low-Health rage), Pocket Knife (daggers, backstab), Short Notice (shortbow, fast flat arrows / short), Second Opinion (wand, big heal),
Turnstile (Bo, double knockback); 3 prototype bows.
Approved, rows only (`research/UT-Lines-Draft.md`): Ghost Rook, Ghost Calvary, Battlegrounds, Ghost Sword (a second Warrior sword), Hepta Axe (Berserker battleaxe).
Open candidate adopted below as Z4 Cloth: the Auditor's set (`research/UT-Lines-Draft.md` section 3).
**Missing, so counted here:** Zone 1 Spellblade weapon (1), Zones 2-5 x 8 classes (32 slots) minus Hepta Axe (fills Berserker Z4) = **32 new weapons**.
Armor: 3 x 4 zones = **12 new sets** (48 pieces). Names, ids and motifs avoid every Z1 UT, every Mythic in `research/cloud/Own-Specials-Draft.md`, and the pack-mod ids.

## 2. Shared rules for every row

- **Source (all rows):** elite mobs, mini bosses and dungeon bosses of the set's zone, through the UT meter (elite 1 / mini boss 5 / dungeon boss 10
  points; 36 points = a sure UT; Gear 0.3.35) and the orange Mystery Bag; also zone quests and loot chests (incl. Unclaimed Luggage). Never crafted, bought,
  or on Bazaar / Auctions (market wall; direct player trade OK). Which mob feeds which set = Question 3.
- **Level band + tag (from `tools/tier_tags.py` METAL_BANDS, TT_VERSION 3; UT sits at the zone's alloy):**
  Z2 Dusk 35-43 `T6 Dusk` | Z3 Azurvane 55-63 `T9 Azurvane` | Z4 Cinder 75-83 `T12 Cinder` | Z5 Lumen 95-103 `T15 Lumen` (Z1 Bronze 15-23 `T3 Bronze`).
- **Tier-tag line text = tag first, then the set / item line:** `T6 Dusk - Night Shift: tough but low on Mana.` (format `tag_text(n, word)`: `"T%d %s"` + `" - "` + text).
  Every new UT id needs a row in `tools/tier_tags.py` ROWS, and `tools/ci/langdup.py` keeps one writer per lang key.
- **Power bands (not numbers):** body stat lines follow `utline.power` (every UT >= Fabled at its level, nothing to invent). The ONE upside and ONE
  downside use size classes: **S** = Filing Cabinet Head / Hands size, **M** = Filing Cabinet Chest / Legs size, **L** = twice M (only on weapons, as
  the whole point of the item). Rule of thumb: upside about one fifth to one third of the stat it bends; downside costs about half to two thirds of
  the upside's value in the situation where it hurts. Exact values come from `python tools/balance_model.py` (**needs the balance model**; do not
  copy any value from this file into `research/balance/targets.md`).
- **utfx keys used** (from `research/UT-Lines-Draft.md` 1): body `str mp cc cd lsteal hpr hprp def spd stam tdmg dmg`; tricks `lowhp back front taken hp
  mregen range pierce heal kb`; swing `slow|medium|fast|superfast`. Where a row needs more (e.g. a spear reach, a shield block) it says NEW ENGINE.
- **Four power sources:** a UT is weapon-or-gear only and must never need a pet / accessory to be usable, but each is built so a specific
  accessory / pet type *pairs* with it (column "Pairs with"). Weapon = about 35% of a build's power, armor about 30%, accessories 20%, pets 15%
  (`research/Balance-P5-Power-Spec.md`); a UT shifts that mix, it does not raise the total beyond "at least Fabled".
- **Sort by tier:** UTs list inside their zone's alloy tier, after the plain gear of that tier, then by name.

## 3. The 12 armor sets (4 pieces each; values are PER PIECE, the set total is 4x; Head / Hands about S, Chest / Legs about M)

Skyy's two anchor examples (gear.md 273) are Z2: Cloth = less Mana, lots of HP / defence; Heavy = the opposite (Mana for HP / defence).
Z1 already has Health-tank (Filing Cabinet), speed-crit (Courier), Mana-spam (Intern) - the new ones avoid repeating those pairs.

| # | Zone / tag | Category | Name (pieces) | Theme | Upside per piece | Downside per piece | Pairs with (accessory / pet) | Role in the four sources |
|---|---|---|---|---|---|---|---|---|
| A1 | Z2 `T6 Dusk` | Cloth | **Night Shift Robes** (Hood / Robe / Cuffs / Skirt) | tired mage on the late shift | max Health + , Defense + (M) | Mana regen - (M) | Health / Regen charms; a tank pet that taunts | Gear. Frees the Mage from armor Mana so accessories carry Mana |
| A2 | Z2 `T6 Dusk` | Light | **Mailroom Slickers** (Cap / Vest / Gloves / Pants) | quiet, fast, hits from behind | `back` + (S), Crit Chance + | `front` - (S) | Dagger / Kunai gear; Speed charm; a flanking pet | Gear. The armor version of the Pocket Knife |
| A3 | Z2 `T6 Dusk` | Heavy | **Server Room Plate** (Helm / Plate / Gauntlets / Greaves) | cold, humming, built for casters in plate | Mana + , Magical Power + (M) | max Health - (S), Defense - (S) | Mana-regen charms; a Mana pet | Gear. The opposite of A1 (Skyy 273): a Priest / Mage in heavy armor |
| A4 | Z3 `T9 Azurvane` | Cloth | **Whistleblower's Shroud** (Hood / Shroud / Wraps / Hem) | loud mage who stays far away | `range` + (M), Magical Power + | max Health - (M) | Defense / dodge charms; a pet that draws aggro | Gear. Kiting caster set; pairs with Mage staff or Archer-style range play |
| A5 | Z3 `T9 Azurvane` | Light | **Contractor's Kit** (Hard Hat / Vest / Gloves / Chaps) | pays for itself in blood | Life Steal + (M), Crit Chance + | Health Regen - (S), Defense - (S) | Life Steal and Regen charms; a heal-orb pet | Gear. Sustain through damage dealt, not through armor |
| A6 | Z3 `T9 Azurvane` | Heavy | **Fire Marshal's Plate** (Helm / Plate / Gauntlets / Greaves) | stands still, takes less, hits slower | `taken` - (M), `kb` resist | Speed - (M), Stamina - (S) | Speed charm; a pet that heals on a timer | Gear. Immovable tank; trade is movement |
| A7 | Z4 `T12 Cinder` | Cloth | **The Auditor's Set** (Hood / Robe / Cuffs / Skirt) | burst mage that runs dry | damage + (M) | Mana regen - (M) | Mana-on-kill charms; a Mana pet | Gear. Adopted from `research/UT-Lines-Draft.md` section 3 (Cindercloth base) |
| A8 | Z4 `T12 Cinder` | Light | **Night Watch Dusters** (Hat / Duster / Gloves / Boots) | patrols, never stops | Speed + (M), Stamina + (S) | damage - (S), `hp` - (S) | Speed / Stamina charms; a mount-style pet | Gear. Mobility set for gathering and travel as much as combat |
| A9 | Z4 `T12 Cinder` | Heavy | **Executive Plate** (Helm / Plate / Gauntlets / Greaves) | wins by being hit last | Defense + (M), Health Regen % + | Speed - (S), `taken` + when under half Health (`lowhp`) | Regen / Heal charms; a healer pet | Gear. Strong start, weak finish; pets and accessories cover the low-Health gap |
| A10 | Z5 `T15 Lumen` | Cloth | **Boardroom Mantle** (Cowl / Mantle / Sleeves / Train) | fights better the closer to death | `lowhp` damage + (M), Magical Power + | max Health - (M) | Life Steal / heal charms; a heal pet (not required) | Gear. Risky glass cannon; the Z5 counterpart of Overtime |
| A11 | Z5 `T15 Lumen` | Light | **Fire Exit Leathers** (Hood / Coat / Gloves / Boots) | escape artist | Speed + , Stamina + (M), dodge i-frame bonus (NEW ENGINE, optional) | Defense - (S), max Health - (S) | Dodge / Stamina charms; a Speed pet | Gear. Pure evasion; drops the gap to the Courier (damage taken) into a different axis |
| A12 | Z5 `T15 Lumen` | Heavy | **Corner Office Plate** (Helm / Plate / Gauntlets / Greaves) | huge Health, huge Mana tax | max Health + (M), Defense + (M), `taken` - (S) | Mana + regen - (M), Speed - (S) | Mana charms; a Mana pet; the Priest's Mana Steal | Gear. Z5 version of the Filing Cabinet idea, taxed in Mana instead of damage (so a Warrior is not punished) |

Flavor line pattern per piece (tag first, then the trade-off, colour coded per Style Guide section 15):
`T6 Dusk - Night Shift: +Health, +Defense, but slower Mana regen (set: x4).` Orange name, green upside, red downside.
Piece sets of one tier share a silhouette with the zone's alloy base armor, recoloured at build time (nothing vanilla-derived is committed);
base ids = the zone's combat armor of that category (**UNVERIFIED**, local session picks from Assets.zip).
Dedupe check: no two sets share a primary axis across the same zone, and no set repeats an existing Z1 pair (Health-tank, speed-crit, Mana-spam).

## 4. The 32 weapons (by class and weapon type; Z1 Spellblade first)

Types alternate primary -> alt (gear.md 272). Primary / alt per class from `research/classes/<Class>.md`: Archer shortbow / crossbow; Assassin
daggers / kunai; Berserker axes+battleaxes / maces+clubs; Mage staff / spellbook; Monk Bo / fist weapons; Priest wand / soul cage; Spellblade
2-handed sword / great shield; Warrior sword+longsword / spear. Z1 uses primary and is built (except the Spellblade).

Reading the tables: **Upside** and **Downside** are the single pair on the item; size is a class (S / M / L, see section 2). "Element" = optional flat element
line (weapon only, SkyyGear-Plan lock 17; ties the item to the Wynn elements) - drop it if Skyy would rather keep elements for Mythics.
"Role" = what the weapon does for the build (35% weapon source); the other three sources are named under "Pairs with".

### 4.1 Warrior (sword / spear) and Spellblade (2-handed sword / great shield)

| Zone / tag | Type | Name | Upside | Downside | Element | Role / pairs with |
|---|---|---|---|---|---|---|
| Z2 `T6 Dusk` | Spear | **The Sticky Note** | reach + (long poke, M) | damage - (M) | - | Safe-distance tank; Defense gear, a taunt pet |
| Z3 `T9 Azurvane` | Sword | **Red Tape** | each hit slows the enemy (M) | Slow swing tier | Water | Crowd control front-liner; Health gear, a heal pet |
| Z4 `T12 Cinder` | Spear | **The Reorg** | pierces a line of enemies (M) | damage - (M) | Fire | Group pull; Mana gear is wasted, so stack Defense |
| Z5 `T15 Lumen` | Sword | **Hostile Takeover** | damage + on low-Health enemies (execute, L) | damage - vs full-Health enemies (M) | - | Finisher; Life Steal accessories |
| Z1 `T3 Bronze` | 2h sword | **The Long Meeting** | wide arc hits 3+ enemies (M) | swing Slow, Momentum builds slower (M) | Air | New Z1 Spellblade slot; Mana gear |
| Z2 `T6 Dusk` | Great shield | **The Rubber Stamp** | blocks (reduces damage) for you (L) | no damage while raised (M) | Earth | Spellblade tank mode; Defense gear |
| Z3 `T9 Azurvane` | 2h sword | **Quarterly Review** | each Momentum stack adds damage (M) | Momentum decays faster (M) | Thunder | Spellblade DPS; Crit gear, Speed pet |
| Z4 `T12 Cinder` | Great shield | **The Firewall** | reflects a part of blocked damage (M) | Speed - while held (M) | Fire | Block-and-return; Health gear, a heal pet |
| Z5 `T15 Lumen` | 2h sword | **Final Notice** | sweeps hit all enemies in reach (L) | -damage per target beyond 3 (M) | - | Crowd clear; Mana accessories |

### 4.2 Archer, Assassin, Berserker

| Zone / tag | Type | Name | Upside | Downside | Element | Role / pairs with |
|---|---|---|---|---|---|---|
| Z2 `T6 Dusk` | Crossbow | **The Escalation** | damage + per held second of aim (L) | slow to reload (Slow tier) | - | Sniper; Crit charms, a scout pet |
| Z3 `T9 Azurvane` | Shortbow | **Reply All** | 3 arrows per shot (spread, M) | damage - per arrow (M) | Air | Close-range burst; Speed gear |
| Z4 `T12 Cinder` | Crossbow | **The Cc Line** | bolts pierce (M) | range - (S), damage - (M) | Thunder | Line clear; Mana-free, so Stamina gear |
| Z5 `T15 Lumen` | Shortbow | **Deadline** | damage + vs enemies at full Health (L) | damage - vs wounded (S) | - | Opener; Crit charms |
| Z2 `T6 Dusk` | Kunai | **The Paper Cut** | bleed (damage over time, M) | direct damage - (M) | - | Poison / bleed builds; Life Steal gear |
| Z3 `T9 Azurvane` | Daggers | **Hot Desking** | attacks teleport a short hop (NEW ENGINE, M) | damage - on first hit (S) | - | Mobile assassin; Speed gear, a dodge pet |
| Z4 `T12 Cinder` | Kunai | **The Resignation** | throw returns for a second hit (M) | Slow throw (M) | Water | Setup assassin; Crit gear |
| Z5 `T15 Lumen` | Daggers | **Two Weeks' Notice** | damage + while a mob has not seen you (back / stealth, L) | `front` - (L) | - | Pure backstab; stealth gear |
| Z2 `T6 Dusk` | Mace | **The Stapler** | heavy stun on hit (M) | Slow swing tier | Earth | Crowd control; Defense gear |
| Z3 `T9 Azurvane` | Battleaxe | **Overbooked** | damage + per enemy hit in a swing (M) | `taken` + (S) | Fire | Wave clear; Life Steal gear |
| Z4 `T12 Cinder` | Battleaxe | **Hepta Axe** (EXISTS) | hits 54% harder | `taken` + , Slow | - | See `research/UT-Lines-Draft.md` 2.1; band must move 45-59 -> 75-83 (Question 1) |
| Z5 `T15 Lumen` | Axe | **Hard Stop** | `lowhp` damage ++ and Life Steal (L) | max Health - (M) | - | Risk-reward bruiser; pairs with Regen charms |

### 4.3 Mage, Priest, Monk

| Zone / tag | Type | Name | Upside | Downside | Element | Role / pairs with |
|---|---|---|---|---|---|---|
| Z2 `T6 Dusk` | Spellbook | **The Style Guide** | spell range + , cheaper Mana (M) | damage - (M) | - | Efficient caster; Mana charms, a Mana pet |
| Z3 `T9 Azurvane` | Staff | **The Conference Call** | hits several targets (area, M) | damage - per target (M) | Water | Group damage; Mana gear |
| Z4 `T12 Cinder` | Spellbook | **The Fire Drill** | burst damage + (L) | Mana cost + (M) | Fire | Burst; Mana-on-kill accessories |
| Z5 `T15 Lumen` | Staff | **Off The Record** | bolts pierce and echo (M) | `taken` + while casting (S) | Thunder | Late-game caster; Defense gear |
| Z2 `T6 Dusk` | Soul cage | **The Lost & Found** | captures more Bindings (M) | Binding duration - (M) | - | Soul-cage Priest; Mana Steal gear |
| Z3 `T9 Azurvane` | Wand | **The Second Shift** | heals nearby allies (M) | wand shots - (M) | - | Healer; Regen gear, a heal pet |
| Z4 `T12 Cinder` | Soul cage | **The Retention Plan** | Bindings pull enemies (M) | Mana drain + (M) | Earth | Control Priest; Mana gear |
| Z5 `T15 Lumen` | Wand | **The Exit Interview** | big single-target damage (L) | cannot pierce, no heal bonus | Air | Priest damage build; Crit charms |
| Z2 `T6 Dusk` | Fist | **The Handshake** | combo speed + (M) | damage - per hit (S) | - | Fast Monk; Speed gear |
| Z3 `T9 Azurvane` | Bo | **The Coat Check** | extends combo window (M) | damage - first hit (S) | - | Flowing-form Monk; Stamina gear |
| Z4 `T12 Cinder` | Fist | **The Stress Ball** | each hit heals a little (M) | damage - (M) | - | Sustain Monk; Regen charms |
| Z5 `T15 Lumen` | Bo | **The Open Door** | knockback + and sweep (M) | damage - vs bosses (M) | Air | Space control; Defense gear |

Count check: 9 (section 4.1) + 12 + 12 = 33 rows, of which Hepta Axe already exists -> **32 new**.

## 5. Build order (for the local session; each its own lean round)

1. Rows-only items: the 12 armor sets and every weapon whose upside is already a utfx key (`swing=`, `dmg+/-`, `taken`, `back/front`, `lowhp`, `pierce`,
   `heal`, `hp`, `mregen`, `range`, `kb`): config + art-recolour only. Includes A1-A10, A12 and about 20 weapons.
2. Items that need new engine (marked NEW ENGINE or a mechanic with no key): Hot Desking (blink), The Rubber Stamp / The Firewall (great shield block
   and reflect), Escalation (aim-held damage), Reply All (3 arrows), Paper Cut (bleed), Red Tape (slow on hit). Each one a small SkyyArmory or SkyyGear round.
3. Doing all this at once is a **full round** (new items, drops, tier-tag table, balance model re-run), not a lean one.

## Questions for Skyy

1. Hepta Axe is a battleaxe at Z4, but Z4 should be the Berserker's ALT weapon (mace) by the 2026-10-18 alternation rule. Keep it as Z4's Berserker UT, or add a mace for Z4
   and move Hepta to Z5? **Default: keep Hepta at Z4 (it counts as the Z4 slot, band moved to Cinder 75-83); Z5 Hard Stop is an axe.**
2. Do the 12 new armor sets use new "office" names (all 12 above) or the zone's mob lore names? **Default: keep the office joke family, it matches the 10 Z1 UTs.**
3. Which elites / mini bosses / dungeons feed which set (one mob per set, or any elite in the zone)? **Default: any elite / mini boss / dungeon of the zone, weighted evenly (no per-set mob), until `tools/pack_drops.py` has the final mob list.**
4. Elements on UT weapons (Element column): ship now, or keep elements for Mythic bosses only? **Default: ship the single flat element listed (Wynn-style), none on armor.**
5. Do you want 2 UT per class in every zone later (you said you may want 2 tiers per zone)? **Default: no; stay at 1 per class per zone, 3 armor sets per zone.**
6. Is a new "great shield block" and "kunai return" okay as engine work now, or park those four weapons? **Default: park The Rubber Stamp, The Firewall, The Resignation and Hot Desking until the Spellblade / Assassin class rounds; ship the other 28.**

## For the local session (UNVERIFIED)

- Every ID, base item, class weapon type id, and art base needs Assets.zip: cloth / light / heavy base armor ids per zone, kunai / spear / mace / great shield / soul cage / spellbook ids, and whether Armory vs Gear builds each family.
- Which utfx keys really exist today vs only in the draft grammar: confirm `range`, `kb`, `hp`, `lowhp`, `mregen`, `taken`, `back`, `front` all work on ARMOR (the Auditor row and A1-A12 use them); `front` / `back` on armor is from `research/UT-Lines-Draft.md`, not yet shipped.
- Whether `lowhp` (damage under 50% Health) works on armor as well as on the Overtime battleaxe, and whether `kb` (knockback resist) is armor-capable (the Turnstile row says the gear `kb` stat is "coming later").
- Zone 1's current UT band is 15-29 in the first batch; METAL_BANDS now says Bronze 15-23 and the 2026-10-22 popup moves UT to zone end (Gear 0.3.39 `migrate39`). Confirm the 10 live Z1 UTs and the 5 Armory UTs landed in 15-23 (Hepta Axe row says 45-59 -> should be 75-83).
- All values (S / M / L) need `python tools/balance_model.py --p9 --check` before any row ships; none of these are in `research/balance/targets.md`. After the round: re-run `--p9 --check`, republish the Class Balance Workbench (memory: balance chart).
- Each new UT id needs a `tools/tier_tags.py` ROWS entry and a lang line; run `python tools/ci/langdup.py`. How the existing 10 UTs are tagged (T2 Iron vs T3 Bronze) was not verified.
- Whether the UT Mystery Bag (8th orange bag) can reveal an armor piece from a 3-category set (Cloth / Light / Heavy) given "armor bags hide the slot until identify" (Gear 0.3.36).
