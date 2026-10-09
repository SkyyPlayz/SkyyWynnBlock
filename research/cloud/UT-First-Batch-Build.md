# UT first batch (phase G2) - build spec: 10 Untiered items, 3 UT developer bows, the orange Mystery Bag

Cloud draft, 2026-10-09. Paper design for the local SkyyGear round; nothing built. Turns `research/cloud/Untiered-Mythic-Spec.md` section 1.3
(U1-U10) into exact ids, base items, fixed stats, trade-off lines and drop odds. Every number is a placeholder and a Server Setup row.
Builds ON phase G1 (SkyyGear 0.2.14 "rar01", running 2026-10-09 per `docs/log/2026-10.md` line 305: orange UT quality + orange bag,
Mythic bosses-only, per-rarity level caps, set check, market wall bridge, gear:fn:grant). G1 was not in the repo when this was written:
where G1 already named something (rarity id, bag id, cost row, bridge), **G1's name wins** - the names below are what G1 most likely used.

## 0. Decisions this follows (newest wins; not re-decided here)

| Source (line) | Skyy's words / the lock | Used here |
|---|---|---|
| `docs/answered/gear.md` 123 (2026-10-08) | "id like to use ROTMG style UT (un tiered.) the idea is, in its level category its good! but NOT always better ... (an example would be a staff with pierce, but less damage.)" | every item: one clear plus, one clear minus |
| `docs/answered/gear.md` 124 | "untiered orange, mythic for boss gear" | rarity `untiered`, orange |
| `docs/answered/gear.md` 126-127 | "UT weapons and armor are only mob drops and chest loot (bosses can drop them too.)" + "but you cant craft them." + "they can come from quests, but not shops." | section 3; no recipe, no shop |
| `docs/answered/gear.md` 128 | Untiered-Mythic-Spec section 7 "Yes to all" incl. "first UT batch kept", UT tiers = 6 zone bands, own-class lean x3 | U1-U10 kept as drafted; UT2 = Lv 15-29 |
| `docs/answered/gear.md` 129 (2026-10-08) | DEV BOWS: "what now? send me some info on these developer bows and prototypes. developer bows sound like cool specal items" | section 2 |
| `docs/answered/gear.md` 130 (2026-10-08) | DEV BOWS: "all of those bows sound really cool, id use them all as special / ut items." (default: Vampire / Bomb / Pull Mythic, Ricochet / Combat / Test Zoom UT; no leap) | section 2 |
| `docs/answered/gear.md` 131, 133 (2026-10-09) | Aegos bow "could be cool to add as a special item"; Arcane Power LifeVeil "a special spell book that heals instead of damaging is exactly the kind of thing a UT should do." | NOT in this batch (licence / permission pending) - later UT rows, same table |
| `docs/answered/gear.md` 137 (2026-10-09, newest) | UT drops -> "Orange mystery bag" (an 8th, orange bag; identify reveals the UT); caps "Mythic +2, UT +3, rest +6"; trading "Direct trade OK" (never on Bazaar / AH) | section 3; **replaces** the spec's "UT drops identified, no bag" (spec 1.4 / 5.3) and "tradable and AH-listed" (spec 1.1) |
| `docs/answered/economy.md` 89 | MARKET WALL -> "Mythic + UT + Sets" (never bought or sold on Bazaar / Auctions) | the orange bag is walled too (section 5) |
| `docs/answered/economy.md` 92 | roaming merchants: "never UT / Mythic" | already true: `SkyyMerchants/build_skyymerchants_0.1.py` lines 152-155 NEVER list holds all 6 dev bows |
| `docs/answered/gear.md` 121-122 | mystery bags one look per rarity; loot round defaults (6% mob roll, Unclaimed Luggage with coins, re-roll x5 max 3) | the orange bag reuses all of it |

## 0.1 How SkyyGear does it today (read-only, `SkyyGear/build_skyygear_0.2.13.py`, the SET pin)

| What | Where (lines) | What it means for UTs |
|---|---|---|
| Rarity table `RARITIES` (id, name, hex, frame, slot, drop particle), `LADDER = R_IDS[:6]` | 1262-1277 | G1 appends `untiered` (orange); UTs never in `ODDS_DEF` (1283) |
| `RARITY_DEF` mods / low / high %, `COST_I_DEF` identify (base, per level) | 1280, 1288 | UT identify row `untiered` (section 3.4) |
| `LVLUP_CAP_DEF = 6` (one cap) | 1686 | G1 makes it per rarity: UT +3 |
| Stat table `STATS` (key, label, slots w/s/a/e, unit, max @100 %, weight, live) | 1312-1359 | fixed lines use LIVE keys only: dmg, str, mp, cc, cd, lsteal, hpr, def, spd, stam |
| Gear document: `GearData.base` (v, kind, r, id, mods, src, at, gate), `mod(s, v)` = `{s, v}` with v the FINAL value | 7692-7710 | a UT doc = the same document + `ut` (table key) + `utv` |
| Modifier power by level `GearLevel.factor` = levelFloor 25 + 75 x min(L, 40) / 40 (%), `bounds` | 7821-7829, 8783-8794 | body-line numbers in section 1 use exactly this |
| Armor totals skip a stat whose slots lack `a` (Damage is `w` only) | 11778 | UT lines must bypass the slot filter (section 4 item 4) |
| Defense = damage x scale / (scale + Defense), **only when Defense > 0** | 15481-15487 | negative Defense does nothing -> U9 uses "damage taken +%" instead |
| Speed tiers Slow / Medium / Fast / Super Fast, swing factor 1.4 / 1.0 / 0.7 / 0.5, hit weight = factor (same DPS) | 2783-2789 (+ header 264-297) | U2 = fixed Slow tier |
| The 7 mystery bags: `BAG_ART`, `BAG_IDS = "Skyy_Unid_Bag_" + name`, ramp, item JSON (Quality, MaxStack 1, Variant hidden, Tags Unidentified), lang "<Rarity> Mystery Bag" | 3417-3473 | the orange bag = an 8th entry of the same lists (G1) |
| Bag document + make / rarity / roll / fromItem (`GearUnid`) | 12712-12786; header 89-150 | the orange bag adds `ut` (tier) and a UT pick at identify |
| Mob extra roll 6% inside `GearDeathMark`, chest extra 33% in `GearChestTag`, `gear:fn:box` for luggage (tier 1-4) | header 117-137; rows 3724-3752 | the three UT entry points (section 3.2) |
| Random bag pool filter (FAM_DEV, `_NPC`, `_Test`, Developer / Debug quality) | 1594, 3366-3376 | the 5 prototype bows ARE in today's random pool (only Test_Zoom is filtered) - section 2.3 removes all 6 |
| Prototype bow level rows (Shortbow_Bomb / Combat / Pull / Ricochet / Vampire = 10) | 1550-1554 | UT table overrides their level band |
| SkyyArmory 0.1.14: staff tap = quick shot (24 blocks, +15 %), wand taps pierce (`pierce.max` 0 = no cap), wand hold heal orb heals `orb.healPercent` % of the LANDED burst damage | `SkyyArmory/build_skyyarmory_0.1.14.py` 353-365, 391, 1168-1179; ids 1230, 1324-1325, 3104 | U1, U6, U7 hooks live in SkyyArmory |
| SkyyExploration 0.2.5 luggage: tiers 60/28/10/2, bags 0.5/1/1.5/2, each bag via `gear:fn:box` with the tier | `SkyyExploration/build_skyyexploration_0.2.5.py` 83-88, 1298, 1466-1467, 5095-5137 | no SkyyExploration change needed (the tier already reaches SkyyGear) |

## 1. The 10 UT2 items (Lv 15-29) - one table per item

Common to all ten (and the 3 UT bows):
- **Rarity** `untiered` (orange, G1). **Level** = the bag's identify level (uniform inside the bag's lo..hi, clamped to 15-29). **Level up** +3 (G1 cap).
- **Base stats** = the base item's own stats at that level through the live gear curves (weapon damage, armor Health / resistances).
- **Fixed lines** (no random modifiers, no modifier Reforge, never re-rolled by the stamp scan). Two kinds:
  - *body lines* = ordinary live stats at a fixed 70 % power (a Legendary roll's middle), so they grow with level like any roll:
    value = round(max x 70 % x factor(L) %), factor(L) = 25 + 75 x min(L, 40) / 40 (python3, values at Lv 15 / 22 / 29 below);
  - *trade-off lines* = constant numbers (never scale), shown as ONE orange tooltip line.
- **New id** = a copy of the base item's JSON made at build time (Recipe / salvage blocks REMOVED, `Variant` hidden from the creative list,
  own name + description lang lines, the base model with an orange-accent recolour of its texture as a PLACEHOLDER look - the bag's
  `BAG_ART` one-line swap pattern, `UT_ART`, until Quirk / local art). Nothing vanilla is committed. Id style keeps the family word so
  every reader (`GearData.isGear`, SkyyClasses weapon prefixes `Weapon_Staff_` / `Weapon_Wand_` / `Weapon_Bo_` ..., speed families, AH
  types) treats it as its base type: `Weapon_<Family>_UT_<Name>`, `Armor_UT_<Name>_<Slot>`.
- **Source** = the orange Mystery Bag only (section 3); chance per bag and per hour in section 3.3. Bosses / quests / elites later.

Body-line numbers (python3, `bounds` formula at 70 %):

| Stat (max @100 %) | Lv 15 | Lv 22 | Lv 29 |
|---|---|---|---|
| Strength (25), Magical Power (25), Defense (25) | 9 | 12 | 14 |
| Crit Chance % (15) | 6 | 7 | 8 |
| Crit Damage % (30) | 11 | 14 | 17 |
| Life Steal % (5) | 2 | 2 | 3 |
| Raw Health Regen (2) | 1 | 1 | 1 |

### U1 The Loophole (Mage staff)
| Field | Value |
|---|---|
| Id / base | `Weapon_Staff_UT_Loophole` / `Weapon_Staff_Iron` (SkyyArmory's own staff, so SkyyArmory builds this item) |
| Body lines | Magical Power 9 / 12 / 14, Crit Chance 6 / 7 / 8 % |
| Trade-off | Damage **-30 %** (all its damage); quick shots (tap) **pierce every enemy in a line** (no cap, reusing the wand pierce chain) |
| Tooltip line | "Quick shots pierce every enemy in a line. 30% less damage." |
| Engine | LOW: SkyyArmory's pierce code accepts this staff id (today wand taps only) |

### U2 The Paperweight (Warrior sword)
| Field | Value |
|---|---|
| Id / base | `Weapon_Sword_UT_Paperweight` / `Weapon_Sword_Iron` (SkyyGear builds it) |
| Body lines | Strength 9 / 12 / 14, Crit Damage 11 / 14 / 17 % |
| Trade-off | speed tier fixed **Slow** (swing time x1.4, hit weight x1.4 - same DPS as Medium) + Damage **+7 %** -> each hit x1.498 (+50 %), DPS x1.07, but 29 % fewer swings (python3: 1.4 x 1.07 = 1.498) |
| Tooltip line | "Hits 50% harder. Swings 40% slower." |
| Why not "two tiers slower" | only ONE tier sits below Medium (Slow); a second would need new swing assets. Question 4 |
| Engine | LOW: `spd` written as `S` at grant, never re-rolled |

### U3 Overtime (Berserker battleaxe)
| Field | Value |
|---|---|
| Id / base | `Weapon_Battleaxe_UT_Overtime` / `Weapon_Battleaxe_Iron` |
| Body lines | Strength 9 / 12 / 14, Life Steal 2 / 2 / 3 % |
| Trade-off | Damage **+30 % while your Health is under 50 %**; **-10 % max Health** while it is in your hand |
| Tooltip line | "30% more damage while under half Health. 10% less max Health while held." |
| Engine | LOW-MEDIUM: GearHit reads the attacker's Health; the max-Health part is a held-item modifier (the 0.2.12 GearHandSys add / remove pattern) |

### U4 The Pocket Knife (Assassin daggers)
| Field | Value |
|---|---|
| Id / base | `Weapon_Daggers_UT_PocketKnife` / `Weapon_Daggers_Iron` |
| Body lines | Crit Chance 6 / 7 / 8 %, Crit Damage 11 / 14 / 17 % |
| Trade-off | hits from **behind +50 %** (you stand inside the 120 degree cone behind the target's facing); hits from the **front -30 %** (the 120 degree cone in front); sides unchanged |
| Tooltip line | "Backstabs deal 50% more damage. Hits from the front deal 30% less." |
| Engine | LOW-MEDIUM: our own angle test on the damage event (target head / body yaw vs the attacker); UNVERIFIED which rotation component mobs keep |

### U5 Short Notice (Archer shortbow)
| Field | Value |
|---|---|
| Id / base | `Weapon_Shortbow_UT_ShortNotice` / `Weapon_Shortbow_Iron` |
| Body lines | Strength 9 / 12 / 14, Crit Chance 6 / 7 / 8 % |
| Trade-off | arrows fly **x2 speed, no drop** (gravity 0); they **vanish after 12 blocks**; Damage **-15 %** |
| Tooltip line | "Arrows fly twice as fast and flat, but vanish after 12 blocks. 15% less damage." |
| Engine | MEDIUM: a build-time copy of the bow's projectile config (speed x2, gravity 0, lifetime = 12 blocks / speed) referenced only by this id (UNVERIFIED that a per-item projectile copy works the way the speed tiers' interaction copies do) |

### U6 The Second Opinion (Priest wand)
| Field | Value |
|---|---|
| Id / base | `Weapon_Wand_UT_SecondOpinion` / `Weapon_Wand_Iron` (SkyyArmory builds it) |
| Body lines | Magical Power 9 / 12 / 14, Raw Health Regen 1 |
| Trade-off | the hold's **heal orb heals x1.5**; wand shots deal **-40 %** damage |
| Tooltip line | "Your heal orb heals 50% more. Wand shots deal 40% less damage." |
| Trap found | the heal orb heals a % of the LANDED burst damage (SkyyArmory 357-358), and the -40 % lands first: 1.5 x 0.6 = 0.9 = a WEAKER heal. SkyyArmory must heal from the damage before the UT cut: landed x 2.5 (python3: 1.5 / 0.6). The harness proves the heal = 1.5 x an Iron wand's at the same level |

### U7 The Turnstile (Monk Bo)
| Field | Value |
|---|---|
| Id / base | `Weapon_Bo_UT_Turnstile` / `Weapon_Bo_Iron` (SkyyArmory builds it) |
| Body lines | Strength 9 / 12 / 14, Crit Chance 6 / 7 / 8 % |
| Trade-off | every hit **knocks back x2**; Damage **-25 %** |
| Tooltip line | "Every hit knocks enemies back twice as far. 25% less damage." |
| Engine | LOW: the Bo's hit interactions copied with knockback force x2 for this id only (the gear `kb` stat is still "coming later", so not used) |

### U8 The Filing Cabinet (Heavy set, 4 pieces)
| Field | Value |
|---|---|
| Ids / bases | `Armor_UT_FilingCabinet_Head` / `_Chest` / `_Hands` / `_Legs` from `Armor_Iron_Head` / `_Chest` / `_Hands` / `_Legs` |
| Per piece | Defense 9 / 12 / 14 (body line); max Health **+6.25 %**; Damage **-3 %** (Head and Hands **-2 %**) |
| Full set (4/4) | max Health **+25 %**, Damage **-10 %**, Defense 36 / 48 / 56 |
| Tooltip line (each piece) | "Tank set: +6.25% max Health, 3% less damage dealt (whole set: +25% / -10%)." |
| Engine | LOW: lines per piece (a UT is not a Set - no 4/4 check; one piece already does something); Damage on armor needs the slot-filter bypass |

### U9 The Courier's Leathers (Light set, 4 pieces)
| Field | Value |
|---|---|
| Ids / bases | `Armor_UT_Courier_Head` / `_Chest` / `_Hands` / `_Legs` from `Armor_Leather_Medium_Head` / `_Chest` / `_Hands` / `_Legs` (**UNVERIFIED** ids - the repo only names the family row `Leather_Medium` (Lv 15); fallback `Armor_Leather_Light_*`, which the repo references) |
| Per piece | Crit Damage 11 / 14 / 17 % (body line); Speed **+4** (Hands +3; 1 Speed = +1 % walk speed, `speed.per`); Crit Chance **+1 %** (Chest +2 %); **+5 % damage taken** |
| Full set (4/4) | move speed **+15 %**, Crit Chance **+5 %**, damage taken **+20 %** |
| Tooltip line | "Runner's set: faster and sharper, but you take 5% more damage per piece." |
| Why not "-20 % Defense" | negative Defense is ignored by the live formula (line 15484, `def > 0`), and most players have little Defense to lose; "+20 % damage taken" is what the spec meant and always works |
| Engine | LOW: a new UT line `taken` applied in the same damage system as Defense |

### U10 The Intern's Robes (Cloth set, 4 pieces)
| Field | Value |
|---|---|
| Ids / bases | `Armor_UT_Intern_Head` / `_Chest` / `_Hands` / `_Legs` from `Armor_Cloth_Cotton_Head` / `_Chest` / `_Hands` / `_Legs` (Cotton = Lv 15, the repo names all four) |
| Per piece | Magical Power 9 / 12 / 14 (body line); Mana regen **+12.5 %**; max Health **-5 %** |
| Full set (4/4) | Mana regen **+50 %**, max Health **-20 %** |
| Tooltip line | "Spell-spam set: +12.5% Mana regen, 5% less max Health per piece." |
| Engine | LOW-MEDIUM: Mana regen belongs to SkyySkills - SkyyGear posts `regen.mana` (fraction) in its existing `skill:bonus:<uuid>` "gear" source (the 0.2.12 tool Fortune map); SkyySkills multiplies its regen by (1 + sum). One small SkyySkills change |

## 2. The 6 developer bows

| Vanilla id (repo refs) | Today | Role (gear.md 130 default) | This round |
|---|---|---|---|
| `Weapon_Shortbow_Ricochet` | Lv 10 row (0.2.13 line 1553); in the random bag pool | **UT** | UT2 row: its own id (no copy), rarity `untiered`, body Strength + Crit Chance, trade-off **Damage -20 %** next to its vanilla trick (arrows bounce - UNVERIFIED) |
| `Weapon_Shortbow_Combat` | Lv 10 row (1551); random pool | **UT** | same; trade-off -20 % (its fast charge 0.1-1.0 s per `research/Charged-Attack-Research.md` line 86 - behaviour UNVERIFIED) |
| `Weapon_Shortbow_Test_Zoom` | FAM_DEV, Developer quality, not in any pool (1594) | **UT** | same; trade-off -20 % (zoom scope - UNVERIFIED) |
| `Weapon_Shortbow_Vampire` | Lv 10 row (1554); random pool; CHG_EXCL (2424) | **Mythic** | out of random bags now; boss pool in B1 (suggest Burnt Skeleton Praetorian, undead) |
| `Weapon_Shortbow_Bomb` | Lv 10 row (1550); random pool; gear, not ammo (1409-1449) | **Mythic** | out of random bags now; B1 pool (suggest Trork Chieftain) |
| `Weapon_Shortbow_Pull` | Lv 10 row (1552); random pool | **Mythic** | out of random bags now; B1 pool (suggest The Broodmother) |

2.1 **Why no copy for the bows:** they already have their own models and tricks; a UT row on the vanilla id is enough (the UT document makes
it orange, fixed and walled). Old copies that random bags handed out since 0.2.11 stay what they are (e.g. a Rare Ricochet bow).
2.2 **Their trade-off text** is written after the local session reads the three JSON files (what the trick really is); -20 % damage is the
placeholder, so the bow is "good at its trick, weaker at plain shooting".
2.3 **Random pool:** all 6 ids join the build-side pool filter (next to FAM_DEV) so no Normal-Fabled bag ever becomes one again. Until B1
the 3 Mythic bows have no source but `/gear give` (admin) - question 3.
2.4 **Level:** Hytale and our rows put them at Lv 10 (UT1 band 1-14). UT1 does not exist yet, so default = UT2 (Lv 15-29) with the rest - question 2.

## 3. The orange Mystery Bag

### 3.1 The item
| Field | Value |
|---|---|
| Id | `Skyy_Unid_Bag_Untiered` (= `BAG_IDS` "Skyy_Unid_Bag_" + the new rarity name; made by G1 - use G1's id if it differs) |
| Name / look | "Untiered Mystery Bag" (the "<Rarity> Mystery Bag" lang line); quality = the Untiered quality (orange frame, name, drop glow); ramp orange placeholder until Quirk's 8th bag |
| Document (metadata "SkyyUnid", schema v2, as `GearUnid.make`) | `mys` = `"UT"` (no type shown - with ~1 UT per type, the type would give the item away), `r` = `untiered`, `ut` = tier (2), `lo` / `hi` = L-2..L+2 clamped to 15..29, `at` `-`, `src` / `ls` / `tier`, `t`, `n` (nonce), `id:false` |
| Tooltip | "Untiered Mystery Bag" (orange) / "Lv 20-24 - Untiered (tier UT2)" / "One Untiered weapon or armor piece - identify to see which." / "Cannot be used until identified." / "Identify: /identify - N coins" |
| Identify | the 0.2.11 path (fingerprint, coins FIRST, ONE in-place write, refund on failure): level uniform in lo..hi; item = weighted pick from the UT2 rows whose item exists on this server: weapon or armor by `ut.armorShare` (50 %), weapons with **own-class x3** (`ut.classLean`), each row `ut.weight.<key>` (1); then the UT document (via G1's `gear:fn:grant` core): rarity `untiered`, `lvl`, `ut` key, `utv`, fixed lines, `spd` where fixed, `box` = {mys, r, lo, hi, at, n:0} for re-rolls |
| Identify cost | row `cost.identify.untiered` **750 + 60 per level** (Lv 22 = 2,070; between Legendary 1,380 and Fabled 2,760 - python3) - placeholder; G1's row wins |
| Re-roll (x5 cost, max 3, live rule) | rarity stays `untiered`; a WEAPON re-rolls into another UT2 weapon (own-class lean again); an ARMOR piece re-rolls into another piece of the SAME armor type (= the other slots of the same UT set). Reforge level-ups are lost, as for every re-roll |
| Pays | Smithing identify XP at the Legendary row (placeholder; no XP on re-roll, live rule) |

### 3.2 How it drops (three entry points, all inside SkyyGear - no SkyyMobs or SkyyExploration change)
| Source | Rule | Row (default) |
|---|---|---|
| **Mobs** (GearDeathMark extra roll, 6 %) | when the 6 % roll hits AND the mob's level is inside a band that has UT rows (today 15-29): `ut.mob.share` of those bags are orange instead of a normal bag. Counts toward the 20 / hour cap; one roll per death (live) | `ut.mob.share` **2 %** (per kill 0.12 % = 1 in 833) |
| **Vanilla world chests** (GearChestTag, 33 % extra on a real fill) | same swap for the extra bag at the chest's zone level | `ut.chest.share` **2 %** |
| **Unclaimed Luggage** (`gear:fn:box`, which already gets the tier 1-4) | each bag a luggage gives is orange with the tier's chance (only if L is inside a UT band) | `ut.luggage.share` **1 / 2 / 4 / 8 %** (tiers I-IV; per claim 1.78 % = 1 in 56) |
| Vanilla gear that turns into a bag (`fromItem`) | never orange (it is a known vanilla item) | - |
| Bosses / elites / dungeon chests / quests | later rounds call `gear:fn:grant` or ask for an orange bag (B1, Elites, SkyyQuests) | - |

### 3.3 Odds per hour (python3; method: rate x share, summed)

Assumptions (Loot-Round-Revision 4-5): 120 levelled kills / hour (project average), 8 luggage claims / hour (the cap; ~0.77 bags each),
3 fresh vanilla chests / hour. Only while playing inside Lv 15-29.

| Set of shares | Mobs / h | Vanilla chests / h | Luggage / h | Orange bags / h | One bag every |
|---|---|---|---|---|---|
| Untiered-Mythic-Spec 1.4 numbers (1 % / 1 % / 0.5-1-3-8 %) | 0.072 | 0.010 | 0.096 | 0.178 | 5.6 h |
| **Default here** (2 % / 2 % / 1-2-4-8 %) | 0.144 | 0.020 | 0.142 | **0.306** | **3.3 h** |

What a bag holds (22 rows: 7 weapons + 3 UT bows + 12 armor pieces; armor 50 %, own-class weapons x3):

| You are | A specific own-class UT weapon per bag | ~hours of play for it (default) |
|---|---|---|
| Mage / Warrior / Berserker / Assassin / Priest / Monk (1 own UT weapon) | 12.5 % | ~26 h |
| Archer (4: Short Notice + 3 bows) | 8.3 % each, 33.3 % any | ~39 h for one specific bow |
| Armor | one specific piece 4.2 %, any piece of one set 16.7 % | a full set without re-rolls ~50 bags (~163 h); re-rolls (same armor type) and direct trade cut that a lot |

The set grind is the long pole - question 1.

## 4. What the round changes (by mod)

| Mod | Change |
|---|---|
| **SkyyGear** (next version after G1) | 1. UT table `UT_DEF` (key, id, base id, tier, lo, hi, armor type, body lines, trade-off lines, fixed spd, hooks, weight, lang) -> one Server Setup text row per UT `ut.line.<key>` (e.g. `dmg:-30;pierce:1`) + `ut.weight.<key>`; 2. builds the 4 vanilla-based weapons + 12 armor pieces (copied JSON, Recipe removed, Variant, `UT_ART` placeholder recolour, lang); 3. orange bag content + the three drop swaps + rows `part.ut`, `ut.mob.share`, `ut.chest.share`, `ut.luggage.share`, `ut.armorShare`, `ut.classLean`; 4. GearStats.totals adds the UT lines of every worn / held UT by its `ut` key with NO slot filter (armor Damage counts), never through `mods`; 5. new line kinds: `taken` (damage taken %, next to Defense), `lowHp` (U3), `back` / `front` (U4), `hpPct` (one max-Health MULTIPLICATIVE modifier `skyygear_ut_hp`, summed over worn + held UTs, GearHandSys add / remove), `regen.mana` (posted in skill:bonus "gear"); 6. GearLevel.band reads the UT table first (the level-up cap and "never above the band top" use 15-29); 7. the 6 dev bows out of the random pool; 8. `/gear ut` (admin list: the grid, which rows exist) and `/gear ut give <key> [level]`; 9. lazy heal: the stamp scan rewrites a UT's lines when `utv` differs from the table (a balance change reaches every copy; nothing re-rolls) |
| **SkyyArmory** (next version) | builds `Weapon_Staff_UT_Loophole`, `Weapon_Wand_UT_SecondOpinion`, `Weapon_Bo_UT_Turnstile` from its own Iron items and registers them in its id tables as Iron (Mana cost, blink, hop, heal orb, Monk moves); hooks: pierce on the Loophole's quick shots, heal from the pre-cut damage x1.5 on the Second Opinion, knockback x2 on the Turnstile's hit interactions |
| **SkyySkills** (small) | Mana regen x (1 + SkillBonus.sum(u, "regen.mana")); a missing key = 0 (older SkyyGear = no change) |
| SkyyClasses / SkyyExploration / SkyyMobs | no change (prefix rules, `gear:fn:box` tier and `mob:fn:level` already carry what is needed) |
| SkyyAuctions / SkyyBazaar | none if G1's market-wall bridge already covers rarity `untiered` AND the orange bag id; else add the bag (section 5) |

## 5. Dupe and loss safety

| Risk | Answer |
|---|---|
| Orange bag duplicated / split | same bag rules as the 7 live bags: MaxStack 1 + nonce, identify and re-roll are ONE in-place write in the same slot (the bag and the item never exist together), coins first, refund on failure |
| Extra drops from the swap | the UT share REPLACES a bag that was already rolled (mob / chest) - no extra roll, no extra entity; mob roll once per death, hourly cap 20 counts it |
| Luggage | per player, the claim is written before the give (live); the tier's share is applied per bag inside `gear:fn:box` |
| Crafting / recycling a UT | the copied JSON has no Recipe; the build asserts no recipe in Assets.zip, the SET jars or our own outputs makes a UT id, and no UT id has a sell / salvage value (the 0.2.11 coin-loop assert, extended) |
| Selling through the market | AH + Bazaar refuse rarity `untiered` documents AND `Skyy_Unid_Bag_Untiered` (an unopened bag must not dodge the wall); direct `/trade` and the Vault are fine (gear.md 137) |
| Permanent Health from `hpPct` | the modifier is never saved as a gain: removed on logout, profile swap (profile:busy), world switch and shutdown, recomputed on join (the GearHandSys / lock-modifier "checked once per join" pattern, 0.2.13 line 16360); taking a -Health piece off never kills (current Health is clamped, not lost) |
| Old random dev bows | untouched (their documents are Normal-Fabled); only new UT copies are orange |
| A missing partner | an Armory UT row whose item does not exist on this server is skipped at identify (never hands out an unknown id); without SkyySkills the robes' Mana line shows "(needs SkyySkills)" |
| Rollback | UT ids and the orange bag are unknown items in older jars: pin a FLOOR (main session) - "never roll SkyyGear / SkyyArmory below this round once UT items exist; first set `part.ut=false` and have players identify every orange bag". UT items themselves cannot be emptied first - treat a rollback as losing them |
| Admin give | `/gear ut give` logs to gear.log like `/gear box` |

## 6. Ready-to-paste task text for the local round

```
ROUND ut01 - UT first batch (phase G2). FULL ROUND (new items, drops, saved data, several mods). Launch with the skywynn-round workflow.
quotes (Skyy's own words): "id like to use ROTMG style UT (un tiered.) the idea is, in its level category its good! but NOT always better"
  / "untiered orange" / "UT weapons and armor are only mob drops and chest loot (bosses can drop them too.)" / "but you cant craft them."
  / "they can come from quests, but not shops." / "all of those bows sound really cool, id use them all as special / ut items."
  / 2026-10-09 popup: UT drops -> "Orange mystery bag"; trading -> "Direct trade OK".
Spec: research/cloud/UT-First-Batch-Build.md (all sections) on top of research/cloud/Untiered-Mythic-Spec.md 1.1-1.6.
Needs first: SkyyGear 0.2.14 (G1 rar01) deployed - reuse its rarity id, bag id, cost rows, gear:fn:grant, market wall.
Mods: SkyyGear (new patch from the SET pin), SkyyArmory (new patch: 3 UT items + 3 hooks), SkyySkills (regen.mana, small).
Files: tools/gear_<ver>_patch.py, tools/armory_<ver>_patch.py, tools/skills_<ver>_patch.py, their generated build_ / test_ scripts.
  NEVER edit SkyyGear-Plan.md / SkyyGear-Stat-Catalog.md or generated scripts.
Scope: section 1 (U1-U10 exactly as tabled), section 2 (3 UT bows on their own ids; all 6 dev bows out of the random pool),
  section 3 (orange bag content, 3 drop swaps, rows, re-roll rules), section 4 (all items), section 5 (all answers).
Harness must prove (bare JVM):
  - all 22 UT rows resolve to real items; no recipe / salvage / sell value for any UT id; copies hidden (Variant); lang present
  - 100,000 simulated Lv 20 kills: orange bags = 0.12 % +-0.03; Lv 10 and Lv 35 kills: 0; luggage tiers 1/2/4/8 % per bag
  - 10,000 identifies: armor ~50 %, own-class x3, level inside lo..hi and 15..29, rarity always untiered, fixed lines exact
  - re-roll: weapon -> another UT2 weapon, armor -> same armor type only, x5 cost, max 3, rarity never changes
  - totals: Paperweight per hit x1.498 / DPS x1.07 at Slow; Loophole -30; Overtime +30 only under half Health; Pocket Knife +50 / 0 / -30
    by cone; armor Damage lines count (slot filter bypassed); Courier +5 % damage taken per piece; hpPct sums worn + held and is gone
    after unequip / logout / profile swap; regen.mana posted (0.125 per robe piece)
  - Second Opinion heal = 1.5 x an Iron wand's heal at the same level (not 0.9)
  - market wall refuses an untiered document and Skyy_Unid_Bag_Untiered on the AH and the Bazaar
  - mutants that must FAIL: recipe kept on a copy; slot filter not bypassed; heal from landed damage; UT share added instead of swapped
Then: review -> fix -> cross-check (python tools/ci/crosscheck.py --jar <new jars> --baseline; python tools/ci/lint.py 0 fails)
  -> smoke test (every [Skyy...] ready line, no asset-validation failure, no SEVERE) -> pin + FLOOR in tools/deploy_set.py -> commit -> deploy.
What Skyy checks in game (TEST-CHECKLIST section):
  1. /gear ut give each item (admin): orange name, "UNTIERED" word, the one orange trade-off line, Lv 15-29, Requires <skill>.
  2. /gear box untiered (or G1's command): orange bag tooltip; identify it -> a UT; re-roll it once.
  3. Feel each trick: Loophole pierce in a crowd; Paperweight slow big hits; Overtime under half Health; Pocket Knife back vs front
     damage numbers; Short Notice flat fast arrows gone at 12 blocks; Second Opinion bigger heal orb; Turnstile knockback.
  4. Armor: Stats page shows max Health / Speed / Mana regen changes per piece; take a piece off -> back to normal.
  5. AH and Bazaar refuse a UT and the orange bag; /trade to a friend works.
  6. Reforge: level up stops at +3; the modifiers tab says the stats are fixed.
  7. Play Lv 15-29 for a while: an orange bag now and then (/gear loot counters).
```

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | UT drop rate: about one orange bag every 3 hours of play at Lv 15-29 (2 % of mob / chest bags, luggage 1-2-4-8 %). A full UT armor set is a long grind (~160 h solo without re-rolls; re-rolls stay inside the same armor set). OK, or more / fewer? | [about 1 every 3 h] |
| 2 | The 3 UT developer bows (Ricochet, Combat, Test Zoom): put them in this first batch at Lv 15-29, or wait for a Lv 1-14 (UT1) batch where Hytale had them (Lv 10)? | [this batch, Lv 15-29] |
| 3 | The 3 Mythic developer bows (Vampire, Bomb, Pull): out of random bags now and only from bosses once bosses exist (admin-only until then)? | [yes] |
| 4 | The Paperweight: our slowest swing tier is "Slow" (40 % slower, hits 50 % harder, a bit more damage overall). OK, or build a new "Very Slow" tier for the "two tiers slower" idea? | [Slow is fine] |
| 5 | UT armor works PER PIECE (each piece gives a quarter of the set's plus and minus), not only at 4/4 like a Set? | [per piece] |
| 6 | The Courier's Leathers: "-20% Defense" becomes "+20% damage taken" (negative Defense does nothing in our formula)? | [yes] |
| 7 | The orange bag hides the item type (only "weapon or armor" - one UT per type would give it away)? | [hide it] |
| 8 | Block the unopened orange bag from the AH / Bazaar too (else it dodges the market wall)? | [yes] |

## For the local session (UNVERIFIED)

- G1 (SkyyGear 0.2.14) names: rarity id `untiered`, quality id, `Skyy_Unid_Bag_Untiered`, `gear:fn:grant` arguments, the market-wall bridge and
  whether it covers bag ids, `cost.identify` row for untiered, per-rarity level-up rows. Adapt this file's names to G1's.
- Base ids: `Armor_Leather_Medium_Head/_Chest/_Hands/_Legs` (repo only has the `Leather_Medium` family row), `Armor_Cloth_Cotton_Hands`,
  `Armor_Iron_Legs`, `Weapon_Battleaxe_Iron` in Assets.zip; their ItemSoundSetId gives Heavy / Light / Cloth as expected.
- What `Weapon_Shortbow_Ricochet`, `_Combat`, `_Test_Zoom` really do (projectile / charge configs, ammo use) -> write their tooltip trick text;
  Test_Zoom's Developer quality has no side effect once our quality overrides the stack.
- A copied item JSON (new id) keeps working with its base's interactions; SkyyArmory's id checks accept the 3 new ids.
- Per-item projectile copy for Short Notice (speed, gravity 0, lifetime for 12 blocks).
- Bo hit interactions carry a knockback force that can be doubled in a per-id copy.
- Which rotation component a mob's facing lives in (Pocket Knife cones); players too (PvP).
- A max-Health MULTIPLICATIVE StaticModifier next to SkyySkills' and the armor lock modifiers (order, no stacking surprise).
- The weapon damage curve for an Iron-based copy at Lv 29 (above Iron's band 15-23): the curve reads the stored level, not the material band.
- Assumed play rates (120 kills, 8 luggage, 3 vanilla chests per hour) vs real `/gear loot` and `/exploreadmin stats` counters.
