# SkyyGear 0.2 "Wynn-style item levels": build spec

> **Skyy's decisions 2026-10-02 win over this draft:** OPEN-QUESTIONS.md, section "Q&A with Skyy 2026-10-02", rounds 1 (magic weapon recipes match vanilla weapons).

*Written 2026-10-01 from Skyy's request of the same day and its same-day follow-up (OPEN-QUESTIONS.md:50-57), docs/plans/SkyWynn-Decisions.md change
notes 2026-09-25 #5 and #6, the SkyyGear 0.1.3 code (B = `SkyyGear/build_skyygear_0.1.3.py`), Assets.zip (read only) and
research/Mob-Levels-Plan.md. Reviewed the same day by a critic + editor pass: section 12 lists every correction.
Nothing here is built yet. Skyy's docs SkyyGear-Plan.md and SkyyGear-Stat-Catalog.md were only read.*

**Legend.** LOCKED = Skyy decided it (source named). VERIFIED = seen in a live script or Assets.zip. INFERRED = likely but not proven
(stage 0 checks it). **PLACEHOLDER** = a number Skyy has not picked. Every placeholder is a Server Setup row (section 9).

---

## 0. Plain words (for Skyy)

- **Your side question is already ruled (LOCKED, Decisions 2026-09-25 #6).** A gear requirement is never your overall or average level.
  It checks the skill that matches the gear: combat gear checks your class weapon skill (Priest = Divinity, Mage = Sorcery, Archer =
  Archery, Warrior = Swordsmanship, Berserker = Fury). Mining gear checks Mining, foraging gear checks Foraging and farming gear checks
  Farming. So "priest level 4" = **Divinity 4**. (SkyyGear-Plan.md line 298 still lists this as open. That line is out of date. It is
  your doc, so it was not edited.)
- **New in 0.2:** every weapon and armor piece carries **its own level**, like in Wynncraft. Two Wood Wands can be Lv 1 and Lv 4.
- **That one number does two jobs:**
  - It sets the item's base stats: damage for weapons, health and resistance for armor.
  - It is the use requirement: a Lv 4 wand needs Divinity 4.
- **Your example works:** a Wood Wand at Lv 1 hits 6-8 (that is exactly what vanilla's wand swing does), and at Lv 4 it hits 10-13.
- **Crafting:** what you craft comes out at **your class skill level** (your Divinity level if you are a Priest), so you can always use
  what you make. It stays inside the material's level range. **The ranges overlap like Wynncraft** (your same-day note). Defaults:
  Wood / Crude Lv 1-13, Copper 10-18, Bronze / Iron 15-23, Thorium 20-28, Cobalt 25-38, Adamantite 35-43, Mithril / Onyxium 40-49.
  A level 80 player crafting Copper gets Lv 18, the Copper cap, because Iron starts at 15. (Your example said "about 22" and "iron starts
  about 20". The 2026-09-30 table is LOCKED with Iron at 15, so the defaults follow it. Question 2.)
- **Same level, about the same stats in every material.** The better material starts with a little more of its own base stat
  (default +0.3% per level its range starts at: Copper +3%, Iron +4.5%, Mithril +12%).
- **Chests and mob drops** roll a level from the zone they are in, and they still drop unidentified.
- **Heads-up, pacing (needs your call, question 1).** Reaching a gear level means reaching that class skill level, and the skill curve
  is steep: skill 15 = 67,000 XP, 20 = 522,000, 25 = 3.0 million, 40 = 25.5 million. At today's kill XP (about 45 per Zone 1 kill and
  105 per Zone 2 kill, with the x3 class skill multiplier of SkyySkills 0.4.10), and if all of it came from kills like that, that is
  about 640 Zone 2 kills for skill 15, 5,000 for skill 20 and 29,000 for skill 25. So most players will sit around Lv 10-18 for a long time. Gear you **craft** is safe, because it is made at your level.
  **Gear you find** in Zone 2 and above (Lv 15-40) would be unwearable, so that part (stage 4) waits for your pacing decision.
- **Priests cannot craft wands** (LOCKED 2026-09-25: wait for custom weapons). Their only wand is the kit's Lv 1 Wood Wand, and a Lv 4
  wand can only be a found item. Your Lv 1 / Lv 4 wand example is therefore about found gear for Priests.
- **Tools** get a level and a material range now. Reforging tools needs the gathering stats (Mining Fortune ...) to be live first,
  because "coming later" stats never roll (LOCKED 2026-09-30). That is a later stage (section 10).
- **Every number below can be changed in Server Setup.**

---

## 1. The model

| Rule | Detail |
|---|---|
| Level lives on the stack | Stored as `lvl` in the item's SkyyGear document. 0.1.3 already **reads** it first (`GearLevel.level`, B:4138-4167, the read is B:4141) and only the admin `/gear level` writes it (B:9797-9802). 0.2 starts writing it on craft and on found gear. A document with `lvl` also reads correctly in 0.1.3, so a rollback is safe. |
| Range | Lv 0-100 (`clamp`, B:4132). Level 0 stays valid for old and admin-set items. Real gear is Lv 1-49 until our own Zone 4 gear exists (section 2). |
| Base stats come from the level | Weapons: damage. Armor: Health plus Physical / Projectile resistance. Formulas are in section 3. |
| Requirement = the same level | Checked against the gate skill (LOCKED): combat and equipment check the class skill, mining gear Mining, foraging gear Foraging, farming gear Farming. The check function is unchanged except for the floor below (`GearGate.check`, B:4274). |
| Gate floor | Skills start at 0 (SkyySkills). For gear, **a skill below `level.gateFloor` (1) counts as that floor in every gate state**. Without this a new Priest (Divinity 0) could not use the kit's Lv 1 wand, and a classless player (or a server set to `level.noSkills=block` without SkyySkills) would be blocked from every Lv 1 item, because `check` passes only `need <= 0` in those states (B:4285). |
| Rarity | Unchanged. Rarity sets how many modifiers an item gets and how strong they are. Level sets the base stats and the modifier power factor (section 6). |
| Tools | They store and show a level, and their gate still shows "coming later" (B:5236). Tool power stays vanilla until the gathering gear design exists (section 10, Later). |
| Equipment | Level and gate only (kind `equipment`, class gate). It has no base stat to scale, and its stats come from modifiers. |
| Shields | **Not gear.** `Weapon_Shield_` is in the default `gear.exclude` (B:649), so a shield has no level and no gate. The Warrior kit's Wood Shield stays outside this system. |

---

## 2. Material level bands (they overlap)

The first number of each band is Skyy's 0.1.3 table value (LOCKED 2026-09-30). Wood / Crude moves from 0 to 1, because Wynn levels start
at 1 and your example starts at Lv 1. The cap is the **next material's start + 3**: the overlap you asked for (Wynncraft pattern:
leather 1-18, chain from about 15).

**Metals**

| Material | 0.1.3 level | **0.2 band** | Zone it fits (Mob-Levels-Plan 4.1) |
|---|---|---|---|
| Crude, Wood | 0 | **1-13** | Zone 1 (1-10) and the gap to Copper |
| Copper | 10 | **10-18** | end of Zone 1, gap 11-14, Zone 2 start |
| Bronze, Iron | 15 | **15-23** | Zone 2 start and middle |
| Thorium | 20 | **20-28** | Zone 2 middle and end, gap 26-29 |
| Cobalt | 25 | **25-38** | Zone 2 end, gap 26-29, Zone 3 (30-40) |
| Adamantite | 35 | **35-43** | Zone 3 middle and end, gap 41-44 |
| Mithril, Onyxium | 40 | **40-49** | Zone 3 end, gap 41-44, Zone 4 start (45) |
| Copper ARMOR (entry `Armor_Copper`) | 1 (Skyy 2026-10-01) | **1-18** | LOCKED 2026-10-01: "lower copper armors minimum level to 1, since there is no lower tier armor". Copper weapons and tools keep 10-18. Works in 0.1.3 already as a Server Setup row (`Armor_Copper=1`); 0.2 ships it as a default band. |

**The 59 other family rows.** The band runs from the table value to that value + 7 (`level.bandWidth` 8 = a 5-level step plus the
3-level overlap), never above 49.

| Band | Families (from B:771 onward) |
|---|---|
| 5-12 | Wool, Leather_Soft, Stone, Trork, Fishbone, Bone, Root, Stoneskin, Bamboo, Cane, Onion |
| 10-17 | Linen, Leather_Light, Scrap, Steel_Rusty, Steel_Flail_Rusty, Leaf, Kweebec, Cutlass, Shortbow_Bomb/Combat/Pull/Ricochet/Vampire |
| 15-22 | Cotton, Leather_Medium, Tribal |
| 20-27 | Silk, Leather_Heavy, Leather_Raven, Steel, Incandescent, Zombie, Katana, Nexus, Runic, Kunai, Grimoire, Wizard |
| 25-32 | Doomed, Void, Frost, Flame, Praetorian |
| 30-37 | Cindercloth, Ancient, Steel_Ancient, Crystal, Spellbook_Fire, Spellbook_Frost, Staff_Frost |
| 35-42 | Scarab, Spectral, Silversteel, Demon, Rekindle |
| 40-47 | Crystal_Flame, Crystal_Ice |
| 45-49 | Prisma |

**Tools** use the same table by their material word (a Copper pickaxe is Copper 10-18). An item with a per-item level row
(`level.item.<id>`) has no range: it is always exactly that level.

**When a level falls outside the band**

| Case | Result |
|---|---|
| Crafter's level is above the band | The item is made at the band's cap. Chat: "Copper gear caps at Lv 18 - use Iron for higher." |
| Crafter's level is below the band | Default: made at the band's start, so you grow into it. Chat: "Made at Lv 10 - you need Divinity 10 to use it." (`craft.belowBand` min; block = refuse.) |
| A found item's rolled level is outside the band | It is moved into the band. An Iron sword is never below 15, and a Wood sword in Zone 3 stays at 13. |
| Admin `/gear level <n>` | Any level 0-100, bands ignored (works as today, B:9795-9803). |
| A band is changed in Server Setup | Items already stamped keep their level. Items with no stamp follow the table live (as in 0.1.3). The admin command `/gear relevel` re-stamps the items a player holds. Vault, AH and bag contents are not touched. |
| Lv 50-60 (Zone 4) | No vanilla material reaches it. Our own gear fills it later (same note as Mob-Levels-Plan). |

---

## 3. Base stats from the level

### 3.1 The level curve F(L) (PLACEHOLDER, row `base.curve`)

F is a multiplier on the Lv 1 value. It is a straight line between these points: **1:1.0, 4:1.6, 10:2.0, 40:3.0, 100:5.0**.

| Lv | 1 | 4 | 5 | 9 | 10 | 15 | 20 | 25 | 30 | 35 | 40 | 49 | 60 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F | 1.00 | 1.60 | 1.67 | 1.93 | 2.00 | 2.17 | 2.33 | 2.50 | 2.67 | 2.83 | 3.00 | 3.30 | 3.67 | 5.00 |

- Lv 1 to 4 follows Skyy's example: +20% of the Lv 1 value per level.
- From Lv 10 on it adds 3.3% of the Lv 1 value per level (one straight line to Lv 100).
- **At Lv 40, F = 3.0 = vanilla's own Mithril vs Crude ratio** (sword 18 / 6, shortbow 37 / 12, spear 12 / 4, mace 56 / 19). The first
  draft had 3.5, which put Lv 40 gear about 17% above vanilla Mithril. It also gave a level-matched player 1.4x the damage against
  mobs of the same level, while Mob-Levels-Plan section 15 #1 assumed gear adds only 1.5-2.5x power by Zone 3-4. With 3.0 the
  player-to-mob ratio is 1.17 at Lv 40 and 1.47 at Lv 10 (mob health x(1 + 0.04 x (L - 1))).
- **Material bonus (Skyy's follow-up: the better material "starts with a little more of its own base stat").** Weapon damage and armor
  Health get a further factor (1 + `base.matBonus` % x the band's start level), default 0.3 per start level: Wood +0.3%, Copper +3%,
  Iron +4.5%, Thorium +6%, Cobalt +7.5%, Adamantite +10.5%, Mithril +12%, Prisma +13.5%. PLACEHOLDER. Resistance gets no bonus.

### 3.2 Weapons

**One base item per family, and the material only picks the band.** Each weapon family uses the vanilla Crude or Wood item as its Lv 1
base. Every material of that family deals the same damage at the same level (plus the small material bonus). So a Lv 12 Copper sword
equals a Lv 12 Wood-band sword. This also fixes vanilla staffs, which deal 5 / 25 whatever their material (VERIFIED: the plain staves, wands
and spellbooks all swing and cast the same in every material; only the Crystal staves have spells of their own).

All numbers below are read from Assets.zip (VERIFIED 2026-10-01).

| Family (kit item) | Lv 1 swings or shots (vanilla) | Other steps at Lv 1 (vanilla) |
|---|---|---|
| Wand (Priest kit, Weapon_Wand_Wood) | **6 and 8** (Sword_Swing_Left / Right_Fast) | cast orb 25 (projectile `Skeleton_Mage_Corruption_Orb`, the same for every wand, staff and spellbook) |
| Staff (Mage kit, Weapon_Staff_Wood) | 5 and 5 (Spear swings) | orb 25 |
| Sword (Warrior kit, Weapon_Sword_Crude) | 6 / 6 / 11 (combo order) | thrust 16, Vortexstrike 12 spin / 35 stab |
| Shortbow (Archer kit, Weapon_Shortbow_Crude) | draw strength 0-4: 4 / 6 / 8 / 10 / 12 (headshot at full draw 16) | Volley 9 + 6 (the signature step adds a flat Physical 6) |
| Battleaxe (Berserker kit) | 11 / 14 / 23 | downstrike 18, whirlwind 9 |
| Daggers | swings 3 / 3, stabs 5 / 7 | pounce 20 / 25 |
| Longsword / Axe / Mace / Club / Spear | 8x3 / 8, 8 / 19x3 / 4, 4 / stab 4 | charged 24 / 16 / 26 (slam 59) / none (a Crude club has no charged step) / thrown 10 |
| Spellbook | none | orb 25 |
| Crossbow (only Iron exists) | standard bolt 10 | combo 27, big arrow 78. Its base is Iron's values divided by F(15) and Iron's bonus, so an Iron crossbow at Lv 15 deals exactly vanilla |

**Per-hit damage.** One rule for every step (swing, charged, signature, thrown, bow draw, orb):

> hit = the engine's own amount x **K** x F(L) x (1 + `base.matBonus` x band start) x a random 100 +/- `base.spread` %

- **K** = the family base item's largest primary-attack entry / this item's largest entry. A Copper sword is first scaled down to
  Crude size. Vanilla steps scale evenly inside one item (Sword Crude -> Mithril: swings x3.09, thrust x3.19), so one number per
  item is enough. Crude and Wood items, orbs and items without a damage breakdown have K = 1. It comes from the same engine data
  `damageText` already reads (`getBasicDamageBreakdown`, B:5141-5157), cached per item id.
- `base.spread` default **0**: hits keep Hytale's own steps (a wand alternates 6 and 8), so Skyy's "6-8" is exactly the listed range.
  Set 10 for a random +/-10% on every hit (it keeps the average).
- Because it is one multiplier on whatever the engine already computed, charge %, combo order and the Charged / Signature class
  behaviour stay as they are, and no per-step lookup is needed.
- Odd items (Crystal staves, Frost, Flame, Praetorian, Scarab ...) keep their special shape. `base.item.<id>` scales any single item.

### 3.3 Worked table (round half up; material bonus not included)

| Lv | **Wood Wand** (swings / orb) | **Staff** (swing / orb) | **Sword** (swings / thrust) | **Shortbow** (full draw / headshot) | **Chestplate** (Health / resist) |
|---|---|---|---|---|---|
| 1 | **6-8** / 25 | 5 / 25 | 6-11 / 16 | 12 / 16 | 9 / 6.5% |
| 4 | **10-13** / 40 | 8 / 40 | 10-18 / 26 | 19 / 26 | 14 / 7.3% |
| 10 | 12-16 / 50 | 10 / 50 | 12-22 / 32 | 24 / 32 | 18 / 9.1% |
| 20 | 14-19 / 58 | 12 / 58 | 14-26 / 37 | 28 / 37 | 21 / 11.0% |
| 40 | 18-24 / 75 | 15 / 75 | 18-33 / 48 | 36 / 48 | 27 / 14.3% |

- **Skyy's example:** Lv 1 = 6-8 exactly as in vanilla. Lv 4 = 10-13, against "like 10-12". An exact 10-12 can't come from one
  multiplier, because 6 needs x1.67 and 8 needs x1.5.

**Against vanilla, at the level each material's band starts** (sword = average of the three combo swings, shortbow = full draw,
armor = a full four-piece set; the material bonus is included):

| Material (Lv) | Sword vanilla -> 0.2 | Shortbow vanilla -> 0.2 | Armor set vanilla -> 0.2 (Health / resist) |
|---|---|---|---|
| Copper (10) | 10.0 -> 15.8 (+58%) | 15 -> 24.7 (+65%) | 25 HP, 18% -> 52 HP, 25% (+106%) |
| Iron (15) | 12.7 -> 17.4 (+37%) | 19 -> 27.2 (+43%) | 46 HP, 25% -> 57 HP, 28% (+23%) |
| Thorium (20) | 15.3 -> 19.0 (+24%) | 23 -> 29.7 (+29%) | 61 HP, 32% -> 62 HP, 31% (+1%) |
| Cobalt (25) | 15.3 -> 20.6 (+34%) | 23 -> 32.2 (+40%) | 61 HP, 32% -> 67 HP, 33% (+10%) |
| Adamantite (35) | 18.7 -> 24.0 (+29%) | 29 -> 37.6 (+30%) | 68 HP, 40% -> 78 HP, 37% (+15%) |
| Mithril (40) | 23.3 -> 25.8 (+10%) | 37 -> 40.3 (+9%) | 68 HP, 40% -> 84 HP, 40% (+24%) |

- So 0.2 hits harder than vanilla at the same material: **about +60% at Copper, +25-40% in the middle, about +10% at Mithril**. Mobs
  keep vanilla health until SkyyMobs (risk R1).
- Vanilla Copper armor is the weakest set in the game (25 HP; Wool, Leather, Iron and Bronze sets are 46 HP), so Copper doubles
  while the rest land within about +25%. Lv 1-7 armor (25-43 HP) is below vanilla Wool and Leather (46 HP) on purpose: you grow into it.
- **Known outliers (risk R10).** Vanilla Axe, Longsword and Club scale 9-19x from Crude to Onyxium, against about 3x for every other
  family, so the single curve leaves them far under vanilla above Lv 15-20: Axe +7% at Lv 15, -40% at Lv 25, -64% at Lv 40; Longsword
  +13% / -35% / -62%; Club -47% at Lv 15 and -82% at Lv 40 (its Crude item is a 4-damage outlier with no charged step). Sword, Shortbow,
  Spear, Mace and Battleaxe stay within +5% to +70% of vanilla everywhere, and Daggers within -16% to +36%. Fix after the stage 2 test with a per-family curve
  (`base.curve.<Family>`), not by bending F for everyone. It only matters above Lv 20, which players do not reach yet (section 0).

### 3.4 Armor

| Stat | Lv 1 base (vanilla Copper row, VERIFIED) | Scales with |
|---|---|---|
| Health | Head 5, Chest 9, Legs 7, Hands 4 (there is no Feet slot) | F(L) x (1 + material bonus) |
| Physical = Projectile resistance | Head 3.6%, Chest 6.48%, Legs 5.04%, Hands 2.88% | R(L) = 1:1.0, 10:1.4, 20:1.7, 40:2.2, 100:3.0 (`base.resCurve`). Lv 40 matches vanilla Mithril (about 40% for a set) |
| Extra lines (Thorium poison resist, Cindercloth fire, Silk / Cindercloth / Onyxium mana) | Vanilla, not scaled in 0.2 | - |

- Full set at Lv 40 (no material bonus): +75 Health and about 40% resistance. Vanilla Mithril is +68 and about 40%.

### 3.5 How it plugs into Hytale's damage pipeline

1. `GearHitSys` (Filter group, before armor, B:7512-7627) already knows the weapon stack: the hand stack for melee, and for projectiles
   the `GearShot` launch snapshot (`rec.main`, B:7531), so the level is read from the stack. **No new field on `GearShot` is needed.**
   Arrows go through a damage step but with a plain `EntitySource`, and the weapon comes from `GearShotTrack.pick`. Orbs and thrown
   spears come with a `ProjectileSource` and `GearShotTrack.find`.
2. **New first step in the weapon branch** (its own switch `part.base`; it must not sit inside the `part.stats` branch at B:7592, or
   turning stats off would turn base damage off): `d.setAmount(d.getAmount() x m)` with m from section 3.2.
3. Then the existing chain runs unchanged: Damage % -> Strength / Magical Power -> Charged Attack Damage -> crit -> `setAmount`
   (B:7609).
4. `base.mode=off` = vanilla damage (the live rollback). An item whose level cannot be read gets m = F(1) = 1 and one log line.
5. **Armor Health:** per worn SkyyGear piece the delta is (per-stack Health - the asset's native Health). The negative part (a
   per-stack value below the native one, and every inactive piece, which is cancelled completely as today) goes through the existing
   lock `skyygear_lock_` (`GearFx.locks`, B:7337), which only cancels and waits for the engine's own armor modifier before it
   raises (`plan`, B:7285). **The lock is cancel-only** (it writes `-next`, B:7364), so it cannot carry a positive delta. The positive
   part (Copper-row 9 Health at Lv 10 is 18, so +9) is a plain `StaticModifier(MAX, ADDITIVE, +x)` under a new key
   `skyygear_base_<Health id>`; adding max Health needs no sync wait (INFERRED, stage 3 test). This is a second modifier key, not a
   reuse of the first one.
6. **Armor resistance:** `GearArmorSys` (B:7641-7652) corrects the engine's result by `act / full`, both read from the engine's map.
   0.2 computes `act` with our own copy of the formula (`GearArmor.reduce`, B:6998) plus a per-cause multiplier delta for Physical and
   Projectile = the sum of (per-stack - asset) over the active SkyyGear pieces. No new engine objects, and `full` stays the engine's.
   It needs `ordered && ARMOR_NATIVE`, the same condition as today's inactive-armor fix. If ordering is unavailable the per-stack
   resistance silently does not apply, so log it once.
7. Mob weapons and non-gear damage are untouched, because they have no SkyyGear document.

---

## 4. Crafting: "all items crafted are crafted at your level" (LOCKED, Skyy 2026-10-01)

| Rule | Detail |
|---|---|
| Which level | **Your level in the skill that gates what you wear**: the class skill (`GearGate.gateSkill(u, "class")`, B:4230) for every combat weapon, armor and equipment piece. This is the literal reading of the request, it needs no weapon-to-skill table, and it cannot drift from SkyyClasses. A Warrior crafting a sword uses Swordsmanship. A Warrior crafting a Priest's item uses Swordsmanship too. |
| Tool | Mining / Foraging / Farming (pickaxe and shovel / hatchet / hoe and sickle, as `TOOL_FAMILIES`, B:638). |
| Clamp | Into the material band (section 2). With the gate floor, a fresh Divinity 0 Priest crafts at Lv 1. |
| Without SkyySkills / no class picked | Band start. Without SkyyClasses the pseudo-skill "Combat" is used (as the gate does today). |
| Rarity | Unchanged. The Smithing rarity chance (B:4869-4890) still picks the rarity. **Smithing never raises the level.** |
| Wands, spellbooks | No recipes today (LOCKED 2026-09-25), so nothing is crafted. The rule applies the day they get recipes. |
| Creative mode | Not rolled (`GearCraftSys` skips it), as today. |

**One change point.** Both craft paths end in `GearRoll.craftDoc(id, u)` (B:4991), and `craftDoc` already receives the crafter:

| Path | Today | 0.2 |
|---|---|---|
| SkyySacks `/craft` | `gear:fn:roll({crafter UUID, itemId, count, "craft", recipeId})` (Sacks 0.7.9:3432-3465), mode 8 (B:6367-6385) | **No Sacks change.** Mode 8 calls `craftDoc` once per item (every item its own document and roll), up to 64. All of them get the same level, because crafter and item id are the same. An optional `"lvl"` key is accepted and clamped. |
| Vanilla bench | `GearCraftSys` (B:6532) -> `GearCraftTask` -> `rollIn` -> `craftDoc(id, u)` (B:6501) | Same stamp. |

**Order matters.** `newDoc` rolls the modifiers with `GearLevel.level(id, d)` (B:4986), so `lvl` must be put into the document **before**
`rollMods`. Add an `lvl` parameter to `newDoc` / `craftDoc` / `unidDoc`; do not stamp afterwards, or the modifiers roll at the table
level.

**Exploit and edge cases (checked)**

| Case | Result |
|---|---|
| Crafting at a high level with cheap materials | The band cap stops it: Wood / Crude tops out at Lv 13, Copper at 18. Non-metal families have the same caps. Only the matching material reaches a higher level. |
| Cheap material at the cap is as good as an expensive one at the same level | Intended ("same level = about the same stats"). The material bonus (up to +12%) is the reason to pay more. |
| Crafting for a friend or an alt | The item is made at the crafter's level. The user still needs that skill level. No exploit, but a market limit (R6). |
| Kit farming (new profiles, `/class kit`) | Kit items are unstamped, so they read as the band start (Lv 1). Never the owner's level. The kit stays once per profile (LOCKED 2026-10-01). |
| Buying low-level gear as a high-level player | Nothing to exploit. Low level = low base and low modifier power. The level shows in the AH text (`rollsLine` already prints "Lv N", B:5480-5485). |
| Level boost by class change or alt | The class is locked per profile, and each profile has its own skills. Skill levels are re-read within one second (`GearTick` refresh). |
| Reforge or identify to change a level | They never change `lvl`. Cost uses the stored level, as today. |
| Salvage loops | Vanilla salvage returns materials, not levels. No loop. |

---

## 5. Found gear (chests and mob drops)

*This whole section is stage 4 and waits for the pacing decision (question 1).*

| Source | Level |
|---|---|
| World chests (`unidDoc(id, 2, "chest")`, `GearStamp` 1-3, `GearTag`, the 0.1.3 first-open tag, SkyyExploration chest luck) | Rolled evenly inside the **zone band at the looting player's position**, then moved into the material band. The loot window only knows the player (`lootStack(s, u, where)`, B:6049), so the player's position is the lookup point. The loot-table path (`GearTag.CHEST`) has the chest ref but needs no separate rule. |
| Mob drops (`unidDoc(id, 1, "drop")`) | The same lookup at the death position (`GearTag.MARKS` holds world + x / y / z). Later, once `mob:fn:level` exists and the dying mob's UUID is passed to the mark: the mob's level +/- `loot.mobSpread`, then moved into the material band. |
| Zone band lookup | 1. `mob:fn:band(world, x, z)` when SkyyMobs stage 2 is present: one zone table for mobs and loot, and SkyyGear keeps no copy of Mob-Levels-Plan section 2. 2. `loot.level.world.<world>`: the hand-built zone islands are separate worlds, so this is the main route for the real server. 3. Otherwise the material band's start. |
| Identify | Unchanged: still unidentified. The exact level and requirement already show before identify (`lines`, B:5295). The identify cost uses the stored level. |
| Your own level | Not used by default. `loot.aboveYou` (default off) can cap found gear at your skill + N: a lever for the pacing problem. The band start still wins, so a Mithril sword is never below 40. |

The rarity shift of Mob-Levels-Plan section 5 reads `mob:fn:level` as well, but it is a separate row (`odds.levelShift`).

---

## 6. Modifiers / identifications

- **Keep the 0.1.3 power rule** (LOCKED 2026-09-30, `stat.levelFull` 40): power % = 25 + 75 x min(level, 40) / 40 (`factor`,
  B:4170-4178). It now reads the **stack's** level, so a Lv 13 Wood-band item rolls at 49% power. Before, every Wood item was level 0
  and rolled at 25%.
- Above Lv 40 modifiers stay at full power. Base stats keep growing through F(L).
- Reforge, identify and the `migrate clampToLevel` path read the stored level (or the table level when there is no stamp). **The 0.2
  migration never runs `clampToLevel`**, so existing rolls are not cut.

---

## 7. Requirement UX

**Tooltip** (per-stack `ItemDisplayMetadata`, B:5397-5446; the render signature already includes the level, B:5371):

```
Wood Wand                         <- rarity colour
Lv 4 - Requires Divinity 4        <- grey when met; red + "(you: 2)" when not
Priest weapon                     <- red "Priest weapon - you are a Warrior" when wrong class
Damage 10-13 per hit              <- per stack: the vanilla steps x m
Charged 36-44                     <- only if a breakdown entry's label can be read (stage 0 check c)
...modifiers / "Unidentified - identify for N coins"
```

- 0.1.3's `damageText` takes the min and max over **all** breakdown entries, charged ones included (a Crude sword shows 6-16).
  Splitting "Damage" from "Charged" needs the entry label. If that accessor does not exist, show one combined range, scaled by m.
- Armor shows `Health +14   Resist 7.3%`. Under-level armor keeps its line: "Gives no stats until Divinity 20" (B:5313).
- Gathering gear shows "Lv 12 - Requires Mining 12 (coming later)".

**When your level is too low** (unchanged from 0.1.3, apart from the floor):
- **Weapon:** the hit deals 0 and has no knockback. A popup says "<item> needs Divinity 4 - you are 2" (B:6626-6646), throttled to
  1.5 s, and `gear.blockedPopup` turns it off (B:7577-7582, B:4298-4313).
- **Armor:** the piece gives no SkyyGear stats, and its per-stack Health and resistance are removed too (B:7023-7048, B:7336). A chat
  warning appears if `gear.armorWarn` is on.

**Wrong class:** SkyyClasses `class:fn:allowed` blocks the item, and SkyyGear stays out (B:6614). The tooltip shows the class line.

**Admin:** `/gear read` also prints the base stats ("Lv 4 - Divinity - 10-13 / orb 40"). `/gear level` and the new `/gear relevel`
are both admin only.

---

## 8. Migration, kits and other mods

| Item | 0.2 behaviour |
|---|---|
| Existing gear (no `lvl`) | **Not rewritten.** An item with no stamp keeps reading its level from the table, now the band's start: Copper stays 10, Iron 15, and Crude / Wood read 1 instead of 0. Rolls, rarity and identify state are untouched. A stamp appears only when a document is created or rewritten anyway (craft, found gear, identify, reforge, admin). This avoids a mass rewrite of every stack and keeps `gear:fn:sig` and the tooltip signature steady. |
| Admin-set `lvl` | Kept as is. |
| Base damage of existing gear | Switches to section 3 straight away (stage 2). A Copper sword goes from 8-14 to about 13-24. Announce it in the patch notes. |
| Class kits (SkyyClasses 0.1.10) | Plain kit items stay unstamped and read as the band start (Lv 1). The gate floor lets a skill-0 player use them. **No SkyyClasses change.** |
| Config file | A one-time update (the marker pattern of `migrate013`: a marker line, edited rows kept) rewrites `level.material.*` rows that still hold their 0.1.3 default single number into the new band defaults. A row Skyy edited keeps its single number, which now means N to N + `level.bandWidth` - 1. The `level.material` table gets a **Max** column (kit multi-column table `int\|int;type;Level\|Cap`; a missing Max = the width rule). |
| Config changes later | They no longer re-level stamped items. Use `/gear relevel` for that. |
| Stacking | Spears and spellbooks with different levels don't stack. Harmless, because gear stacks are already split. |
| `gear:fn:level` | Returns the stored level, else the table level. Same API. |
| `gear:fn:sig` | **Includes the level** (B:5489-5492), so the AH shows "rolls differ" for a Lv 4 and a Lv 9 wand. The AH calls it live on both sides (SkyyAuctions 0.1.2:1778), so the changed value breaks nothing. |
| `gear:fn:describe` / `rollsLine` | `rollsLine` already includes "Lv N" (B:5480-5485). Add the per-stack damage line to `describe` so the AH tooltip shows it. |
| `gear:fn:roll` | Mode 8 stamps the crafter's level. An optional `"lvl"` key is accepted (clamped). |
| `gear:fn:unid` | Mode 9 takes an optional world + position so the zone lookup can run. Without one it uses the band start. |
| New keys | `gear:fn:craftLevel` (stage 5, optional). `gear:gates` and `gear:tiers` are unchanged. |
| SkyyAuctions 0.1.2 | Works unchanged: its "Normal - Lv N" text reads `gear:fn:level`. Sorting or filtering by level is a later Auctions update. |
| SkyySacks 0.7.9 / SkyyAccessories 0.5.1 / SkyyMenu / SkyyHud / SkyyExploration | No change needed. |
| SkyyClasses Priest heal | Heals 25% of the damage a Priest hit did, **capped at 10 HP per hit and 10 HP per second** (LOCKED 2026-09-25), so higher-level wands heal more only until the cap. Orb hits reach it at about Lv 4 (25 x 1.6 = 40 damage, 25% = 10 HP). No tuning needed. |

---

## 9. Server Setup rows (all editable, page "levels"; live reload like the 0.1.3 rows)

| Row | Default | Meaning |
|---|---|---|
| `part.levels` | true | Master switch. false = 0.1.3 behaviour: nothing is stamped, table start levels only. |
| `level.material.<word>` | `Copper=10\|18` ... (section 2) | Table with Min and Cap columns. A single number still works: N to N + `level.bandWidth` - 1. |
| `level.item.<id>` | (empty) | An exact level for one item (no range). Existing row. |
| `level.bandWidth` | 8 | Band size for rows that give one number (a 5-level step plus a 3-level overlap). |
| `level.gateFloor` | 1 | Player skill below this counts as this for gear, in every gate state. |
| `craft.levelFrom` | gate | gate = the crafter's gate skill; band = always the band start (the 0.1.3 behaviour for crafting). |
| `craft.belowBand` | min | min = make it at the band's start; block = refuse the craft. |
| `craft.weaponSkill` | (empty) | Optional `prefix:Skill` list. Empty = every combat craft uses the class skill. Fill it only to make a weapon type use its own skill. |
| `loot.level.world.<world>` | (empty) | A band for a named world (zone islands, hub, dungeons). Stage 4. |
| `loot.mobSpread` | 5 | +/- levels around the mob level (once `mob:fn:level` exists). |
| `loot.aboveYou` | 0 | Found gear is never above your gate skill + N. 0 = off. |
| `base.mode` | shape | shape = the multiplier of section 3.2; off = vanilla damage. |
| `base.curve` | `1:1.0,4:1.6,10:2.0,40:3.0,100:5.0` | F(L) for damage and armor Health. |
| `base.curve.<Family>` | (empty) | A per-family F(L). For the outliers of risk R10. |
| `base.resCurve` | `1:1.0,10:1.4,20:1.7,40:2.2,100:3.0` | R(L) for armor resistance. |
| `base.matBonus` | 0.3 | % bonus per level a material's band starts at (damage and Health). |
| `base.spread` | 0 | +/- % random on every hit. 0 = vanilla steps. |
| `base.family.<Family>` | the Crude / Wood item (Crossbow: Iron) | The Lv 1 base item of each weapon family. |
| `base.item.<itemId>` | 1.0 | Multiplier for one item. |
| `base.armor.<slot>` | Head 5,3.6 / Chest 9,6.48 / Legs 7,5.04 / Hands 4,2.88 | Lv 1 Health and resistance per slot. |
| `base.armorOn` | true | Per-stack armor stats (stage 3). Off = vanilla armor values. |
| (unchanged) `stat.levelFloor` 25, `stat.levelFull` 40, identify / reforge cost rows, `level.noSkills`, `level.armorNative`, `level.vanilla`, `level.default` | | |

---

## 10. Build stages (smallest first) and risks

| Stage | What ships | Size |
|---|---|---|
| 0 - checks (no player change) | (a) Build time: K is computable for every vanilla gear id (the build walks Assets.zip like the 0.1.3 checks). (b) In game: does the client draw its own vanilla damage block next to our per-stack text (R2)? (c) Is a breakdown entry's label readable, to split the "Damage" and "Charged" lines? | S |
| 1 - stored level + requirement | Bands and the config update, `lvl` in `newDoc` / `craftDoc` / `unidDoc` before `rollMods` (B:4986-4993), crafting at your level, gate floor, tooltip "Lv N - Requires X N", `gear:fn:sig` with level, `/gear relevel`, Server Setup rows. **Damage stays vanilla.** Safe on its own: you can always use what you craft. | M |
| 2 - weapon base damage | `base.mode` shape in `GearHitSys` (own switch `part.base`), the per-stack "Damage x-y" tooltip line. | M |
| 3 - armor base stats | Per-stack Health delta through the lock plumbing, per-stack resistance in `GearArmorSys`. | M-L |
| 4 - found gear levels | Zone lookup for chests and drops (`mob:fn:band` or world rows), `gear:fn:unid` position, `loot.aboveYou`. **Blocked by question 1.** | M |
| 5 - other mods | AH level sort / filter (SkyyAuctions), "Crafts at Lv N" preview via `gear:fn:craftLevel` (SkyySacks), `mob:fn:level` once SkyyMobs ships. | S each |
| Later | A lower-level craft picker (Wynncraft allows crafting at or below your level; useful for friends and the market). Tool power and **tool reforging** (needs the gathering stats Mining Fortune etc. to be live, because "coming later" stats never roll). Per-family curves (R10). An optional Wynn-style uniform light-hit roll. An "ascend" path that raises a favourite item's level. | - |

**Risks**

| # | Risk | Mitigation |
|---|---|---|
| R1 | 0.2 gear hits harder than vanilla at the same material (+58% sword and +106% armor Health at Copper, about +10% sword at Mithril), while mobs keep vanilla health until SkyyMobs. At the same level a player ends up 1.2-1.5x stronger per hit and about 1.7x tankier than at Lv 1 against mobs of that level (Mob-Levels-Plan 4% health and 2% damage per level). | `base.curve` and `scale.hp` are live. Ship stage 1 first and tune before stage 2. If it is too easy, raise `scale.hp` or flatten the curve. |
| R2 | The client may draw its own vanilla damage block, so the tooltip would show two lines (UNVERIFIED). | Stage 0 check (b). Fall back to hiding the vanilla line, or accept it. |
| R3 | A step has no readable weapon: an arrow with no launch record. | `GearShotTrack` record; without one the hit is not scaled and logged once. |
| R4 | Existing gear damage changes overnight (Copper sword 8-14 -> about 13-24). | Patch note. `base.mode=off` rolls it back live. |
| R5 | Cross-class craft levels. | None needed: the default uses the class skill, so there is no weapon-to-skill table to drift from SkyyClasses. |
| R6 | A Lv 40 item is useless to a Divinity 5 friend, which hurts trading. | The "Later" lower-level craft picker, plus low-zone farming. |
| R7 | The Priest heal scales with base damage. | Capped at 10 HP per hit by the live placeholder, so it saturates early. Nothing to do. |
| R8 | Odd items with big steps (Crystal_Red Fireball 60 x F) get strong. | `base.item.<id>` per-item multiplier. |
| R9 | A uniform min-max light-hit roll (if added later) raises light DPS over vanilla's combo order: Sword +11%, Battleaxe +6%, Wand 0%. | That is why shape mode (vanilla steps) is the default. |
| R10 | Axe, Longsword and Club fall far under vanilla above Lv 15-20 (section 3.3). | `base.curve.<Family>` per-family curves after the stage 2 test. Matters only above Lv 20. |
| R11 | **Pacing.** Class skill 25 needs about 3.0 million XP and 40 needs 25.5 million. Gear found above about Lv 18 is unwearable. | Question 1. Stages 1-3 are safe (crafted at your level). Stage 4 waits. Until then leave the Zone 2+ rows of `loot.level.world` empty, or set `loot.aboveYou`. |
| R12 | A Priest has no way to get a wand above Lv 1 before custom weapons (no recipes, almost no drops). | Known dependency, not a bug of this spec. Found Priest gear or custom Priest weapons must carry it. |

---

## 11. Questions for Skyy (each has a recommended default)

**ANSWERED 2026-10-01 by Skyy: all four recommended defaults** (1 flatten the class skill curve, 2 keep the table + 3 overlap,
3 keep 1-49 / own tiers later, 4 add wand / spellbook / staff recipes now). The questions stay below for reference.

1. **Skill pacing (blocks stage 4; Mob-Levels-Plan question 7 asks the same).** Skill 15 = 67,000 XP, 20 = 522,000, 25 = 3.0 million,
   40 = 25.5 million. How should players reach class skill levels 20-40: a shorter class-skill curve, a level XP bonus (XP x (1 +
   0.05 x (L - 1)) in the Mob plan), or more XP per mob? **Default: decide it with Mob-Levels-Plan question 7 and a playtest. Until
   then ship stages 0-3 and keep found gear above about Lv 18 off.**
2. **Band caps.** Your note said Copper's cap is about 22 and Iron starts about 20. The 2026-09-30 table is LOCKED with Iron at 15,
   so the defaults use "next material's start + 3" (Copper 10-18, Iron 15-23, Cobalt 25-38 ...). Keep that, or move Iron's start
   to about 20 and widen the overlap? **Default: keep the locked table and the +3 overlap.** (One Server Setup row per material.)

3. **Levels above 49 (added by the main session).** Skills go to **100** (the skill page says "level 3 of 100") and your example used
   a level 80 player, but vanilla materials end around Lv 40-49 (Mithril / Onyxium, Prisma 45). Stretch the vanilla materials across
   1-100 (bigger bands), or keep them at 1-49 and fill 50-100 with our own gear later? **Default: keep 1-49 now; our own tiers fill
   50-100 later** (stretching makes every band ~2x wider and the climb even slower, see question 1).
4. **Priest and Mage crafting (added by the main session).** Wands, spellbooks and staffs have no recipes (LOCKED 2026-09-25: wait for
   custom weapons), so a Priest can never craft a better wand at their level. Add vanilla-style recipes for them now (Wood / Copper /
   Iron ... wands and spellbooks at the Workbench), or keep waiting? **Default: add simple recipes now so "crafted at your level" works
   for every class.**

**Decided by default, no question (change the row if you disagree):** crafting below a material's start makes it at the start
(`craft.belowBand`); a craft uses the crafter's class skill for every weapon and armor (`craft.weaponSkill`); hits keep Hytale's own
steps and do not roll between min and max (`base.spread`, "Later"); found gear ignores your level (`loot.aboveYou` 0); a lower-level
craft option comes after 0.2; Wood and Crude start at Lv 1 instead of 0.

---

## 12. Review log (critic + editor pass, 2026-10-01)

**Conflicts with Skyy's words or locked decisions, fixed**
- Same-day follow-up (OPEN-QUESTIONS.md:52-57) was missing: the bands did not overlap, and "the better material starts with a little
  more of its own base stat" was missing (the draft said every material deals exactly the same damage). Section 2 and 3.1 redone.
  Tool reforging was also missing: now a stated dependency on the gathering stats ("coming later" stats never roll, LOCKED 2026-09-30).
- The 0.1.3 table stays the source of each band's start (LOCKED 2026-09-30). Crude / Wood 0 -> 1 is an adjustment, disclosed.
- Shields were described as gear with a level and gate. They are excluded from gear by default (B:649).
- "Wynncraft rule" for mob-drop level +/- 5 and "Wynncraft caps loot by your level" were unverified claims. Removed.

**Wrong code facts, fixed**
- `lvl` was cited at B:2374. It is read at B:4141 and written only by the admin command (B:9797-9802).
- Range is 0-100, not 1-100 (B:4132, B:9795-9803).
- A craft of up to 64 "gives the whole stack one level": mode 8 makes one document per item (B:6367-6385).
- `GearShot` "now also stores the level": it already holds the launch stack (`rec.main`).
- Arrows were called legacy projectiles without a sequence. Only orbs and thrown spears are; arrows use a damage step with a plain
  `EntitySource` and `GearShotTrack.pick`.
- The chest-open path was assumed to know the chest position. The loot window only knows the player UUID.
- `gear:fn:sig` and `rollsLine`: `rollsLine` already prints "Lv N". The sig change is harmless for the AH (live on both sides).
- Shortbow rows were wrong. "Quick shot 15 = 9 + 6" is the Signature Volley, and "full draw 22 = 16 + 6" adds a flat 6 to the headshot
  that is not there. The real Crude draws are 4 / 6 / 8 / 10 / 12 (headshot 16). The claim "bows are about +50% because of a flat Physical 6"
  was wrong: bows track swords (+65% vs +58% at Copper). The Daggers pounce is 20 / 25 (not 20 / 30). The staff light hit is a single 5.
- Priest heal "scales with base damage": it is capped at 10 HP per hit (LOCKED 2026-09-25).
- The "tooltip shows exact level before identify" is not new: `lines` already shows it (B:5295).
- Classless players: `check` passes only `need <= 0` (B:4285), so Lv 1 Wood items needed the floor in every gate state.

**Infeasible or over-built steps, replaced**
- Wynn-style uniform light-hit roll in `hitAmount` needed per-step `Class` + `BaseDamage` reads (BaseDamage read UNVERIFIED), and it
  raises DPS over vanilla's combo order. Replaced by one multiplier (shape), which also covers arrows, orbs and thrown spears.
- "The native Health is cancelled with the existing lock and a per-stack modifier is added" was too loose: the lock is cancel-only
  (B:7364). Now a delta split in two: the lock for the negative part, one new additive key for the positive part (section 3.5 item 5).
  Per-stack resistance uses our own copy of the formula, not new engine objects.
- A duplicate zone lookup inside SkyyGear replaced by `mob:fn:band` + world rows (the real zone islands are separate worlds).
- Mass migration stamp replaced by "unstamped items read the table" (no rewrite of every stack).
- `craft.weaponSkill` table replaced by the crafter's class skill (no drift, no question).
- `stat.pctFloor`, `base.light.<Family>`, `base.singleSpread` removed (not asked for, or only needed by the range mode).

**Balance fixed**
- F(40) 3.5 -> 3.0, F(100) 6.5 -> 5.0 (section 3.1). Full tables against vanilla added (section 3.3), including the Axe / Longsword /
  Club outliers and Copper armor.
- Pacing added as a blocking dependency with the XP table (section 0, R11, question 1).

**Questions removed as not needed:** damage curve slope, crafting below a band, cross-class crafting, normal-hit roll, lower-level
crafting option, found gear above your level. **Kept:** pacing, band caps.
