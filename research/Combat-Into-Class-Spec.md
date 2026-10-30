# Combat into Class - one class tree per class, the Combat skill retired (spec, 2026-10-23)

Owner: Skyy (they/them). Status: SPEC (spec agent, 2026-10-23). Nothing built.
Where answers go: Skyy's answers to section 10 -> `docs/answered/classes.md` (word for word, `python tools/qa_append.py`); the build ->
the rounds in section 9; open items -> `OPEN-QUESTIONS.md` (main session). Supersedes the layout parts of
`research/Class-Tree-Clarity-Spec.md` (its fixes 1-4 are folded in here, section 6) and the queued "SkyyTrees 0.5.3 modifier cut".

Skyy's words (docs/answered/skills.md + classes.md, 2026-10-23):
- "i thought your calss was the combat skill, since when did we also have combat?" -> "Fold the Combat skill into the class: class level
  is your combat level, move the Combat tree's useful upgrades into the class trees, and retire the separate Combat skill (keep XP / no
  one loses progress)."
- "fold classes and combat into 1. that way you get a lot more upgrade options for the class"
- CLASS TREE LAYOUT: "keep the 3 trees, but since you only get 2 ability slots, put the A1 and both the A1 alt in one for the trees with a
  selection gate. so you unlock both alts at the same time, then have to pick which one you want. put A2 and A2 alt in another tree, and
  have the 3rd tree be more directly combat oriented. (with more upgrades geared towards doing damage with weapons instead of ability's.
  and some passive upgrades where the ability's are on the other trees. (the A1 and A2 trees still have some upgrades to increase weapon
  damage but are more geared towards the ability's and mana.) and of the class, have the row lockers be per tree, not all trees."
- MODIFIERS UNLOCK IN THE TREE: "but i do like how you had to unlock the modifiers for each ability, instead if them being tied to the
  ability's level." + popup "Unlock in tree, level by use".

Rules followed: PROJECT-RULES 4 (four power sources, one-time migrations: History copy, only untouched values, Undo, run-once marker,
bytes kept), `tools/PROFILES-CONTRACT.md` (one profile = one class, data per `<pkey>`), `tools/CONFIG-CONTRACT.md` (every new number =
a Server Setup row), `research/Menu-Pattern.md`, `research/Radial-Trees-Spec.md` (class page), Skill Trees 3 rules in
`tools/trees_v3_data.py` (1 point a rank, capstone 1 point, respec rules), Balance P4 caps (class tree `dmgCap 40`, `drCap 35`).

## 0. The short answer (what we found)

**There is no separate Combat XP today.** "Combat" in SkyySkills is a pseudo-skill that resolves to the player's class skill
(Archery / Swordsmanship / Sorcery / Fury / Divinity / Assassination / Zen / Battlemagic). Kills already pay class XP ONCE, into the
active profile's class slot (`Combat.<Class>` keys). The class level IS the combat level already. What makes it feel like two things:

1. the **Combat skill TREE** in SkyyTrees (Adventure page, `/tree combat`, saved keys `Skill.Combat.b<n>.<id>`), whose points are the class
   level AGAIN (so a Lv 30 player has 30 class points AND 30 Combat points);
2. the word "Combat" in labels (`/skills` row 3 fallback, Server Setup "Combat XP per max health", Accessories "unlocks at Combat 15",
   Gear's gate fallback "Combat", Rebirth's "Combat Echo" arm next to the Class arm, `/tree combat` help text);
3. a legacy SkyySkills slot `Combat` (slot 3) from before per-class XP - no longer earned. On Skyy's world NewBetaTest every profile
   file has `Combat=0` (4 files read from a scratch copy, 2026-10-23), and no SkyyTrees file holds any `Skill.Combat.*` rank.

So "keep XP / no one loses progress" needs **no XP conversion** on Skyy's world, and only a tiny safety migration elsewhere (4.3).
The real work is the TREE: one class tree per class with 3 branches (A1 line / A2 line / weapon combat), the Combat tree folded into
branch 3, per-branch row gates, modifiers as 1-point unlock nodes, and the clarity fixes.

## 1. Everything that reads or writes "Combat" today -> after the fold

Newest scripts = SET pins (`tools/deploy_set.py`) + READY candidates. Line numbers are in the named build script.

| Mod (script) | Today | After |
|---|---|---|
| **SkyySkills** `SkyySkills\build_skyyskills_0.4.63.py` | Kill XP `KillSys` (l.20065-20095) -> `MobXp.kill2` (l.20031): mob `xpBase x combat.perHealth 0.2`, clamp `combat.min 1` / `combat.max 0`, `x classSkill.xpMultiplier 3.0 x combat.levelCurve(L) x gap` into the CLASS slot only (`SkillClass.killSlot`, class weapon or ability only `combat.classWeaponOnly`); Combat Echo `P3Xp.echo`; party share `party.combatShare.*` (0.5, 48 blocks); no catch-up for class skills; curve = the general list (`levels.class.sameAsOthers`), P3 / P9 migrations, run cap 50 (+10 a rebirth); perks `perk.combat.healthPerLevel 0.1`, `perk.combat.damagePerLevel 0.002`; level coins `levelCoins`; Wisdom = `RbStat.classXp` + `SkillV3.classXp` (Combat Insight `Skill.Combat.b3.r5b` + every `xp.combat` source) clamped 0-5; `skill:fn:level {u,"Combat"}` = the class skill; `/skills` row 3 + `/skills top combat` = class slot; Overall Level counts "Class" once; saved `players/<pkey>.properties` keys `Combat` (legacy slot 3), `Combat.<Class>` (+ `.paid`); the Tree button finds the tree by its label in `tree:names`; Server Setup tab "combat" labels "Combat XP ...". | XP maths, keys, curve, caps, perks, party share, Wisdom: **unchanged** (they already are class XP). `skill:fn:level "Combat"` stays as an **alias** (Accessories / Quests / Gear fallback keep working). Labels: "Combat XP" -> "Class XP" in every Server Setup label / help (KEYS unchanged, so no setting migration). The `/skills` class row's Tree button opens `/tree class` (there is no "Combat" in `tree:names` any more). Legacy slot 3 folded into the class slot once (4.3). `tree:reads:SkyySkills` keeps `Skill.Combat.b3.r5b` (key unchanged, section 3.1). |
| **SkyyClasses** `SkyyClasses\build_skyyclasses_0.1.46.py` | Stores no class XP; reads the class level via `skill:fn:level {u, ClassDefs.SKILLS[ci]}`; ability levels by use (`abil.maxLevel 25`); modifiers unlock by ability level (`mods.unlock 2,4,6,8,10`, l.1876), level by use (`mods.steps 10,30,60,100`, l.1878), tree `mod` ranks add levels (clamp 5); 4 key rows `p1 p2 a1 a2` (l.442, default l.7668: p1 = A1 on Ability 2, p2 = A2 on Ability 3, a1 = A2-alt, a2 = picked A1-alt on the crouch rows); A1-alt pick only on the old /cast page (`Abil.setPick`); UpFx applies Combat Focus, Finisher, Trophy Hunter, Iron Will, Thick Skin from `Skill.Combat.*` inside `dmgCap 40` / `drCap 35`. | Modifiers **unlock in the tree** (`tree:fn:modOwned` answers again), level by use only (tree ranks never add levels); key rows fixed per branch (section 5); new verb `class:fn:abilDo alt <A|B>` (Clarity 4.2); UpFx keeps the Combat rows (keys unchanged) + 2 new codes `thorns`, `lowHeal` (3.3); one-time modifier migration (4.2). |
| **SkyyTrees** `SkyyTrees\build_skyytrees_0.5.1.py` (0.5.1 zoomfix in progress) + data `tools\trees_v3_data.py` / `tools\trees_v3_effects.py` | 19 trees; Combat = skill tree on the Adventure page (`V3_SKILL_ORDER`, `V3_NEW_PAGES`, `TREE_NAMES_EXTRA`), points = SkyySkills "Combat" = the class level, + Head Start; 70 live Combat ranks (P8b 39 + R3b 27 + R3c 4), 43 "coming soon"; class trees 3 branches, row gates on the TOTAL tree points 0/5/10/15/20/25 (0.5.2 adds "3 in the row above"); `/tree combat`. | **18 trees**: Combat leaves the Adventure page (Acrobatics / Exploration / Beastmastery = a 3-tree page) and joins every class tree as branch 3 (section 3). Class tree points = **2 x class level** (section 2). Per-branch row gates. Modifier unlock nodes. Ability nodes + PICK + panel fixes (section 6). `/tree combat` = alias of `/tree class`. One-time tree migration (4.1). |
| **SkyyRebirth** `SkyyRebirth\build_skyyrebirth_0.5.0.py` | Nexus arms: Class (Class Echo, `classxp`) AND Combat (Combat Echo `Combat.echo`, +8..+26 % kill XP, `nexus.skillEcho` 3rd number, reader `("SkyySkills","xp.combat")`); `/tree combat` page; Head Start +1 point a rank per tree; Combat has no VP share (`CAP_SKILLS`); rebirth needs the class at its cap. | Combat Echo **moves onto the Class arm** as its second node ("Kill Echo"; saved key `Combat.echo`, costs, `nexus.skillEcho` unchanged - no refund needed, no power change). Nexus = 10 arms. VP maths unchanged. Head Start: the class tree gets `2 x headstart` (it replaces two trees). |
| **SkyyGear** `SkyyGear\build_skyygear_0.3.41.py` | Gear gates: `GATE_BY_KIND` combat / equipment -> "class" (l.3417), `gateSkill` / `gateLabel` fall back to the literal "Combat" without SkyyClasses (l.18799-18819); stat `cwis` "Combat Wisdom" (l.3360); Combat tree rows Hone Edge, Weak Spot, Crit Mastery, Gear Resonance, Weapon Tempering read `Skill.Combat.b1.*` (trees_v3_effects). "Combat" Server Setup category + Smithing "Combat armor" = not the skill. | Fallback label "Combat" -> "Class level"; `cwis` label "Class Wisdom" (key unchanged). Tree rows unchanged (keys unchanged). Ride along in the queued Gear 0.3.42. |
| **SkyyAccessories** `SkyyAccessories\build_skyyaccessories_0.5.32.py` | `AccPower.level` = `skill:fn:level {u,"Combat"}` (l.4443-4469), Powers lock text "unlocks at Combat N" (`power.unlock 15`); Accessory Plates reads `Skill.Combat.b2.r4a`. | Text "unlocks at class level N" (alias keeps the read working). Plates unchanged. |
| **SkyyPets** `SkyyPets\build_skyypets_0.4.13.py` (0.4.14 tooltip next) | "Combat" = a PET TYPE (Wolf, Boar, ... Dog; l.901-920), pet XP share `skillMatch` "Combat" = every `Combat.<Class>` (l.828-839), poll rows (l.1015), Pet Fang reads `Skill.Combat.b3.r3a` (`xp.combat` + dmg). | No code change needed (pet type name kept - question 10.9). Pet Fang key unchanged. |
| **SkyyMobs** `SkyyMobs\build_skyymobs_0.1.18.py` | Gap uses `class:skill` + `skill:fn:level`; Spoils rows read `Skill.Combat.b3.*` (l.7365). | Unchanged (keys unchanged). `/mobs info` line text only if it says "Combat" (builder checks). |
| **SkyyMenu** `SkyyMenu\build_skyymenu_0.3.45.py` | Mod description / help "one tree for each skill (Mining, Foraging, Combat, ...)", "/tree combat" (l.931-932); Your Stats "Class Weapon Damage" reads `perk.combat.damagePerLevel`; notification tile "your old Combat XP moves to your class skill" (l.1148). | Help texts: drop Combat from the skill list, "/tree class" example. Rest unchanged. |
| **SkyyHud** `SkyyHud\build_skyyhud_0.3.35.py` | Skills widget class line = the class skill name (no literal Combat); Combat Indicator = in-combat state. | Unchanged. |
| **SkyyQuests** `SkyyQuests\build_skyyquests_0.4.3.py` | `gearLevel` = class skill, else "Combat" (l.4015-4030). | Unchanged (alias). |
| **SkyyGuilds** `SkyyGuilds\build_skyyguilds_0.1.13.py` | "combat" skipped in guild XP skills ("would count twice", l.5975). | Unchanged. |
| SkyyCollections / SkyyBazaar / SkyyArmory / SkyyProfiles / SkyyEssentials / SkyyCooking / SkyyExploration | "Combat" = a collection / sack category (Collections, Bazaar); Armory reads `perk.combat.manaPerLevel`; Profiles store only `p.<id>.class`. | Unchanged (not the skill). |
| **tools\balance_model.py** + `research\balance\*.md` | Class curve `CURVES "Class"`, `CLASS_MULT 3.0`, `PER_HEALTH 0.2`, `f_lv` level curve; P4 `P4_TREE dmgCap 40 / drCap 35`; tree budgets in `trees_v3_effects.check()` (per tree: XP 30 %, move 10 %, max Health 10 %, Fortune 40). | Add a P10 check (section 7): class tree AP = 2 x level, every combined tree reachable by Lv 100, the moved Combat rows' budgets carried into branch 3, new rows inside `dmgCap` / `drCap`. Label "Combat" -> "Class" in xp.md rows (docs only). |

## 2. Points, gates, reach

### 2.1 AP = 2 per class level (recommended)

Today a player gets the class level in points TWICE (class tree + Combat tree). One combined tree with **2 points a class level**
(+ `2 x Head Start`) keeps exactly the points everyone has today - nothing vanishes, nothing doubles. 1 point a level would halve the
tree budget and cut ~35 % of today's tree power (the four-sources balance would break).

| Class | Today's class ranks (of which modifier-level ranks) | New class part (non-modifier ranks + 1 per modifier) | + Combat part (3.2) | Combined | Full at Lv (2 AP) |
|---|---|---|---|---|---|
| Warrior | 106 (41) | 65 + 20 = 85 | 80 | 165 | 83 |
| Berserker | 104 (58) | 46 + 23 = 69 | 80 | 149 | 75 |
| Spellblade | 107 (57) | 50 + 22 = 72 | 80 | 152 | 76 |
| Monk | 107 (59) | 48 + 22 = 70 | 80 | 150 | 75 |
| Assassin | 93 (14) | 79 + 17 = 96 | 80 | 176 | 88 |
| Archer | 93 (29) | 64 + 22 = 86 | 80 | 166 | 83 |
| Mage | 93 (33) | 60 + 22 = 82 | 80 | 162 | 81 |
| Priest | 93 (23) | 70 + 23 = 93 | 80 | 173 | 87 |

(computed from `tools\trees_v3_data.py` + SkyyClasses `AB_MODS`, 2026-10-23.) Every combined tree is full by Lv 75-88 (Lv 100 = 200
AP), so a maxed player owns everything and ~25-50 AP stay free for later nodes. First run (cap Lv 50) = 100 AP = 57-67 % of the tree -
the same 100 points a Lv 50 player has today (50 + 50). Server Setup row `class.apPerLevel` (SkyyTrees, default 2, range 1-5).

### 2.2 Row gates PER BRANCH

A row of a class branch opens when ALL of:
1. **points spent in THAT branch** >= `5 x (row - 1)` (0 / 5 / 10 / 15 / 20 / 25) - row `class.gate.step` 5;
2. **3 points spent in the row directly above** in that branch (the 0.5.2 rule, row `class.gate.rowAbove` 3; free abilities / perks do not count);
3. **class level** >= `5 x (row - 1)` - row `class.gate.levelFloor` on / off (default ON, step 5 levels).

Why the level floor: with 2 AP a level and per-branch counting, a focused player would reach abilities about twice as early as today.
The floor keeps every ability at today's level (A1 Lv 1, A1-alts and A2 Lv 5, A2-alt Lv 20, capstones Lv 25) while the per-branch
points decide WHICH branch you push. The builder asserts: every row 1-5 of every branch holds >= 3 buyable ranks, and rows 1-5 of each
branch hold >= 25 ranks (else the capstone is unreachable).

Grandfathering: a row a player has open today (total-gate rule) that the new rule would close stays open until that tree's next respec
(the 0.4.1 `Class.<C>.gf` mechanism).

## 3. The new class tree (3 branches, every class)

| Branch | Holds | Ability keys (section 5) |
|---|---|---|
| **B1 - the A1 line** (class name of today's A1 branch, e.g. Priest "Devotion") | Row 1: A1 (free). Row 2 = **SELECTION GATE**: both A1-alts (A4a / A4b) unlock together, you PICK one (OR pair). The modifier unlock nodes of A1 and both alts, the upgrades that name A1 / its alts, Mana upgrades, a few weapon-damage nodes. Capstone: the A1-line capstone. | Ability 2 = A1, Crouch + Ability 2 = the picked A1-alt |
| **B2 - the A2 line** (e.g. Priest "Bulwark") | Row 2: A2 (free; row 2 so it opens at Lv 5 as today). Row 5: the A2-alt (A3 in `CLASS_LINES`, e.g. Guardian Spirit, Iron Chain, Explosive Arrow) - a selection-gate row too; with ONE A2-alt it simply unlocks (no OR). Modifier unlock nodes of A2 + A2-alt, their upgrades, Mana, a few weapon-damage nodes. Capstone: the A2-line capstone. | Ability 3 = A2, Crouch + Ability 3 = the A2-alt |
| **B3 - Weapon combat** (shared name "Weaponcraft", class colour darker) | The folded Combat tree (3.2) + the class's own weapon / defence / movement passives that name no ability (e.g. Warrior Iron Skin, Last Stand, Anchor; Assassin Backstab, Lethality; Archer Steady Draw, Eagle Eye). **Free passives at rows 1, 2 and 5** = the rows where B1 / B2 have abilities: r1 Combat Focus (+3 % damage), r2 + r5 the class's passive "free" nodes (Assassin Shadow Clone; otherwise a small class passive picked by the builder from the class's own passives, at 0 cost). Capstone: the class's weapon capstone if it has one, else Edge of the Legend (3.2). | none |

**Placement rule for today's class nodes** (the builder makes the table, R0, and prints it as `research/Class-Tree-v4-Table.md` for
Skyy to read): a node goes to the branch of the ability its hook / text names (A1, A4a, A4b -> B1; A2, A3 -> B2); "every ability" nodes
(Swift Prayer, Swift Casting cooldowns) and Mana nodes (Mana Well, Clarity, Attunement) -> B1 or B2, whichever has fewer ranks; a node
that names no ability (weapon damage, damage taken, max HP, move speed, Stamina) -> B3, except 2-4 weapon-damage ranks kept in each of B1
/ B2 (Skyy: "the A1 and A2 trees still have some upgrades to increase weapon damage"). Capstones: one per branch; a second
capstone-grade node in the same branch becomes a 1-rank row-5 node with the same effect (nothing lost). Rows may hold up to **6** ups
in class branches (today 3) - `check()` relaxed for class trees only; the radial generator decides node size (2.4 of the radial spec).

**Priest worked example** (today Devotion / Bulwark / Hallowed Ground): B1 Devotion = Sacred Heal (r1), Sanctuary OR Martyr's Grace (r2
gate), Sacred Heal Power / Echo / Renewal / Long Reach / Follow / Triage / Overheal / Benediction, Martyr's Grace Blood Covenant,
Sanctuary Duration / Power / Consecrate / Pilgrim / Follow / Chain / Sanctified Mana / Ward / Radiant Beacon / Efficiency, Clarity,
Swift Prayer, Miracle (capstone; Holy Land -> row-5 node) + the modifier unlocks of Sacred Heal (5), Sanctuary (4), Martyr's Grace (5).
B2 Bulwark = Shield Bubble (r2), Guardian Spirit (r5), the bubble / spirit upgrades, Undying Vigil (capstone) + modifier unlocks of
Shield Bubble (5), Guardian Spirit (4). B3 Weaponcraft = Smite, Steadfast, Bastion (+3 % max HP) + the Combat part. (B1 is the big one
for Priest; the builder balances by moving "every ability" / Mana nodes to B2.)

### 3.1 Saved keys never move (the key idea)

Every node carries an explicit saved key = its key TODAY, wherever it is drawn: the Combat nodes keep `Skill.Combat.b<n>.<id>`, a moved
class node keeps `Class.<C>.b<old n>.<old id>`, only NEW nodes get new keys (`Class.<C>.m.<Ability>.<Mod>` for modifier unlocks,
`Class.<C>.b3.n<k>` for anything else new). So:
- no saved-rank rewrite in SkyyTrees, and every applier (SkyyGear, SkyyAccessories, SkyyPets, SkyySkills, SkyyClasses, SkyyMobs) keeps
  reading the exact keys it reads today (`tree:fn:level`, `tree:reads:<mod>`) - none of them needs a code change for the move;
- a SkyyTrees rollback shows the old Combat tree with its ranks intact.
Data shape (`tools\trees_v3_data.py`): `up["key"]` (explicit), `branch["line"]` ("A1" / "A2" / "W"), `row["gate"]` per branch;
`TREES` drops the "Combat" tree entry after copying its nodes into each class's B3 (one source table `COMBAT_PART`, copied 8x).

### 3.2 The Combat part of B3 (same for all 8 classes)

Kept = all **70 live ranks** (unchanged numbers and appliers). Dropped = the "coming soon" nodes nobody can own (they were never
buyable): the three Combat ABILITIES Flurry / Shield Wall / Mark the Prey and their upgrades (Extra Strike, Flurry Recovery, Rending,
Parry Reflex, Bloodlust, Longer Wall, Quick Draw, Bastion, Ward Pulse, Wide Mark, Lingering Mark) - each class already has its own 5
abilities, and modifier-type nodes on abilities that do not exist break the class-tree rules; Salvage and Treasure Sense (no applier);
the capstones Edge of the Legend / Unbreakable / Master Looter (they name Flurry / Mark; Edge of the Legend is reworked as a fallback
capstone). Added = 3 small passives wired for the first time (their Combat keys are kept; nobody owns them).

| B3 row (per-branch gate) | Free | Combat-part nodes (key, max, effect, applier) |
|---|---|---|
| r1 (0) | Combat Focus +3 % damage (`Skill.Combat.b1.r1.free`, SkyyClasses) | Hone Edge 5 +2 % weapon dmg (`b1.r1a`, Gear) - Toughness 5 +0.5 % max HP (`b2.r1a`, Trees) - Scavenger 5 +2 % extra drop (`b3.r1a`, Mobs) - Coin Purse 3 (`b3.r1b`, Mobs) |
| r2 (5) | class passive (3) | Weak Spot 3 +2 % crit chance (`b1.r1b`, Gear) - Iron Will 3 +3 % KB res (`b2.r1b`, Classes) - Momentum 4 +1 % move (`b1.r3b`, Trees) - **Rally 3 NEW** +3 % Health regen out of combat (`b2.r4b`, SkyySkills `hpregen`) |
| r3 (10) | - | Finisher 3 +4 % vs <30 % HP (`b1.r3a`, Classes) - Thick Skin 4 +2 % DR (`b2.r3a`, Classes, inside drCap) - Pet Fang 5 (`b3.r3a`, Pets) - Rare Drop 3 (`b3.r3b`, Mobs) - **Reprisal 3 NEW** 3 % of melee damage taken reflected a rank (`b2.r3b`, Classes `thorns`, counted inside dmgCap) |
| r4 (15) | - | Crit Mastery 3 +3 % crit dmg (`b1.r4a`, Gear) - Gear Resonance 3 (`b1.r4b`, Gear) - Accessory Plates 3 (`b2.r4a`, Accessories) - Boss Hunter 3 (`b3.r4a`, Mobs) |
| r5 (20) | class passive (3) | Trophy Hunter 3 +3 % vs bosses (`b1.r5a`, Classes) - Weapon Tempering 4 (`b1.r5b`, Gear) - Lucky Kill 3 (`b3.r5a`, Mobs) - Battle Insight 5 +2 % class XP (was Combat Insight, `b3.r5b`, Skills) - **Second Wind 3 NEW** once a fight, heal 5 % max HP a rank when you drop below 20 % (`b2.r3c`, Classes `lowHeal`; "fight" = the `skill:fn:combat` window) |
| r6 (25) | - | the class's weapon capstone; fallback **Edge of the Legend** 1: +10 % damage to enemies below 30 % Health (Classes `dmgLow`, inside dmgCap) |

Combat part = 79 ranks + 1 capstone = 80, plus the class's own B3 passives. Names: Combat Insight -> **Battle Insight**, Combat Bulwark
branch name gone (Warrior and Priest already have a "Bulwark"). None of these is modifier-named; none multiplies (all add into
existing sums: UpFx `dmgCap 40`, `drCap 35`; SkyyGear dmg / cc / cd; Combat Health budget 13.75 % since 2026-10-27 = Toughness 2.5 + Plates 11.25, Skyy "Raise cap to 13.75%"; other trees stay 10 %).
Same-effect pairs inside one B3 (e.g. Assassin Power `dmgWeapon` vs Hone Edge; Priest Bastion vs Toughness) stay separate nodes with
different names (question 10.8).

## 4. One-time migrations (PROJECT-RULES 4; per profile file; History copy first, one write onto the lines read, change log = Undo, run-once marker, bytes + line endings kept)

### 4.1 SkyyTrees (`Skyy_SkyyTrees\players\<pkey>.properties`)

Because keys never move (3.1) the file needs almost nothing:
- ranks of a modifier-LEVEL node above its new max 1 are clamped on read (the existing T7 path `num(.., 0, UMAX)`); the freed points are
  simply unspent (no coins). The rank count before the clamp goes to 4.2 (modifier levels kept).
- `Class.<C>.gf` gets the rows the per-branch rule would close (grandfather, 2.2); `Class.<C>.mgf` = the modifier unlock nodes owned
  free (4.2) - one write.
- a free respec of the class tree for this run (`Class.<C>.foldRespec=1`): the layout changed, so everyone may re-plan once (row
  `class.foldRespec` on).
- the Combat tree's own respec counter / free-respec flag are dropped (the class tree's count rules), its Head Start use counts into the
  class tree (`tree:fn:headUsed` = the combined tree).
- marker `fold=done` in the file; History `history\fold\<stamp>\<pkey>.properties`; log `fold-changes.log` (Undo in Server Setup ->
  Changes = restore the History copy).

### 4.2 SkyyClasses (`Skyy_SkyyClasses\abilities\<pkey>.properties`)

- **Modifier levels kept**: for each (ability, modifier) take today's effective level `min(5, tree ranks + level from uses)`; if the uses
  alone give less, raise the use count to `mods.steps[level - 1]` (so the level stays and keeps growing by use). Only lines still holding
  the value it was worked out from (`AbilStore.setIf`).
- **Modifiers already usable stay usable**: every modifier that is unlocked today (ability level >= its `mods.unlock` step, or equipped)
  becomes a free-owned unlock node (`Class.<C>.mgf`, written by SkyyTrees from `class:fn:abilMods` field 2) - no points, kept until a
  respec of that branch (then 1 point each like any unlock). Nobody loses a slotted modifier.
- marker `abil.fold=done`, History `history\fold\`, `fold-changes.log`, one chat line naming what changed.
- Setting rows: `mods.unlock` keeps its value and is used only while `mods.treeUnlock` (new, default ON) is OFF. No config line is rewritten.

### 4.3 SkyySkills (`Skyy_SkyySkills\players\<pkey>.properties`)

Legacy slot `Combat` (slot 3): if `Combat > 0` and the profile has a class, add it to that profile's `Combat.<Class>` slot and set
`Combat=0` (kills before per-class XP never paid class XP, so adding is fair and cannot double count; `moveLegacy` did the same only while
every class slot was 0). Profile without a class: leave it. Level floors / run cap rules apply as for any XP (`SkillCap`, `LvFloor`).
History `history\combatfold\`, marker `combatfold.properties`, Undo log. On NewBetaTest this changes nothing (every `Combat=0`).

### 4.4 SkyyRebirth

No saved data changes: `Combat.echo` ranks stay, only drawn on the Class arm.

## 5. Ability keys - "you only get 2 ability slots" (mismatch report)

Today SkyyClasses has **4 key rows**: Ability 2, Ability 3, Crouch + Ability 2, Crouch + Ability 3 (`p1 p2 a1 a2`), default p1 = A1,
p2 = A2, a1 = A2-alt, a2 = the picked A1-alt, and any ability may be placed on any row. Skyy's "2 slots" matches if a slot = one key
with its crouch variant. Default design (question 10.2):
- **Slot 1 = Ability 2 key = branch 1**: Ability 2 = A1, Crouch + Ability 2 = the PICKED A1-alt.
- **Slot 2 = Ability 3 key = branch 2**: Ability 3 = A2, Crouch + Ability 3 = the A2-alt.
- No free placement any more (the Loadout's hold / place swap goes); the branch decides the key. Migration 4.2 moves each saved
  `p1 p2 a1 a2` onto this order once (History first). A passive A2-alt (Priest Guardian Spirit) needs no key: its crouch row stays empty.
- Equip slots for MODIFIERS: 2 per ability (rebirth 3-4), unchanged - shown as 2 slot tiles on the ability node's panel (6.2) and as 2
  small pips under the ability node on the map (filled = a modifier sits there).

## 6. Clarity fixes folded in (research/Class-Tree-Clarity-Spec.md 1-4)

1. **Ability nodes look like abilities** (Clarity 2): node kind `ability` in `tools\skyymap.py`, 52 px rounded square with the ability's
   rune icon (`SkyyAbility_<Class>_<Id>`, Guardian Spirit `SkyyClasses_Icon_GuardianSpirit`), label `ABILITY` / `ALT - IN USE` / `ALT - OR`.
2. **Equip from the panel** (Clarity 3): the ability node's panel shows its fixed key (section 5, no key buttons needed any more), its 2
   modifier slot tiles and its modifiers as tiles: **unlocked** (white, click = into the first empty slot), **locked** (grey, "unlock in
   the tree - 1 point", click = selects that unlock node on the map). Hint: `Modifiers unlock in the tree, then level by use.` Loadout
   view stays as the overview.
3. **The OR pick** (Clarity 4): the two A1-alts sit side by side at B1 row 2 (the selection gate) joined by the OR line; Primary
   button `Pick <alt>` -> `class:fn:abilDo alt <A|B>`; switching free out of combat, new alt starts on cooldown, 10 s between switches
   (rows `abil.altSwitch.wait` 10, `abil.altSwitch.cooldown` on).
4. **Overlap fix** (Clarity 5): `max_lines` on every wrapped fixed label of the map panel, the ability text in its own 5-line box,
   SkyyClasses DOES check, `tv3_fit` on free perk texts. (5.1 may already ship in SkyyTrees 0.5.2.)

**Radial page** (`research/Radial-Trees-Spec.md` 2.5 "Class" row): still 3 hubs, but sectors sized by need - B3 is the biggest
(~35-45 nodes), B1 / B2 ~20-30 each; ~75-90 nodes in all (Gathering fits 143 at 32 px), so node size probably 36 px (the generator
picks the largest of 44 / 40 / 36 / 32 that passes `skyymap.check` at 100 / 150 / 200 %). Ability nodes 52 px (shrink to 48 first).
The Adventure page becomes a 3-tree page (Acrobatics, Exploration, Beastmastery).

## 7. Four power sources - re-check (must pass before pinning)

- **Moves, never vanishes or doubles**: the 70 Combat ranks keep their numbers and appliers; the AP budget is identical (2.1); the
  points that bought modifier LEVELS buy nothing extra in power - modifier levels now come from use with the same cap 5 (4.2 keeps
  today's levels).
- **Branch 3 spans all four sources** as the Combat tree did: weapon (Hone Edge, Weapon Tempering, crit rows), armor (Gear Resonance),
  accessories (Accessory Plates), pets (Pet Fang).
- **New power only inside existing caps**: Reprisal + Edge of the Legend inside `dmgCap 40`; Second Wind / Rally are healing (no max HP);
  Combat Health budget 13.75 % (Skyy 2026-10-27; was 10 %), XP 30 % (Pet Fang 10 + Battle Insight 10 = 20), move 10 % (Momentum 4).
- Builder runs `python tools\trees_v3_effects.py` check(), `python tools\balance_model.py` (no flag = read only) and adds a `--p10`
  section: AP per class, full-tree level per class (table 2.1), per-branch capstone reach, the moved budgets. `--p9 --check` must stay
  35 / 0 (note: `--p9` REWRITES `research\balance\targets.md` - run it in the round, not in a spec).

## 8. Server Setup rows (new)

| Mod | Key | Type | Default | Range | Label |
|---|---|---|---|---|---|
| SkyyTrees | `class.apPerLevel` | int | 2 | 1-5 | Class tree points per level |
| SkyyTrees | `class.gate.step` | int | 5 | 1-20 | Class row gate (branch points) |
| SkyyTrees | `class.gate.rowAbove` | int | 3 | 0-10 | Points needed in the row above (shared with 0.5.2's row) |
| SkyyTrees | `class.gate.levelFloor` | bool | on | - | Rows also need class level 5 x (row - 1) |
| SkyyTrees | `class.foldRespec` | bool | on | - | One free class respec after the fold |
| SkyyClasses | `mods.treeUnlock` | bool | on | - | Modifiers unlock in the class tree |
| SkyyClasses | `abil.altSwitch.wait` / `.cooldown` | int s / bool | 10 / on | 0-600 | (Clarity 7) |
| SkyyClasses | `fx.thorns` / `fx.lowHeal` per rank | dec | 3 / 5 | 0-50 | Reprisal / Second Wind per rank |
| SkyySkills | `tree.rally` per rank | dec | 3 | 0-50 | Rally out-of-combat regen per rank |

Labels renamed (keys unchanged, no migration): SkyySkills "Combat XP ..." -> "Class XP ..."; Accessories `power.unlock` help "class level".

## 9. Build split, order, floors

Order: after SkyyTrees 0.5.1 (zoomfix) and 0.5.2 (Motherlode / row gates / harvest swing) are deployed. This round REPLACES the queued
Trees 0.5.3 (modifier cut) and 0.5.4 (clarity) - one class-tree rework, one migration.

| # | Builder (Opus unless noted) | Files | Notes |
|---|---|---|---|
| R0 | data (Fable or Opus) | `tools\trees_v3_data.py`, `tools\trees_v3_effects.py`, `tools\skyymap.py` (ability kind, OR edge) + kit test | `COMBAT_PART`, per-class 3-branch tables with explicit keys, check() rules (2.2, 3), prints `research\Class-Tree-v4-Table.md` |
| R1 | SkyyTrees **0.6.0** (patch `tools\trees_0_6_0_patch.py` from the 0.5.2 script) | radial class page, per-branch gates, 2 AP, Combat tree removed from Adventure, `/tree combat` alias, ability nodes / PICK / panel, migration 4.1 | hardest part |
| R2 | SkyyClasses **0.1.47** | tree modifier unlock (`tree:fn:modOwned`), fixed key rows, `abilDo alt`, `thorns` / `lowHeal`, migration 4.2, DOES check | needs R0 |
| R3 | SkyySkills **0.4.64** (lean, Sonnet review) | labels, Tree button -> /tree class, legacy fold 4.3, Rally `tree.rally` reader | |
| R4 | SkyyRebirth **0.5.2** (lean) | Combat Echo on the Class arm (10 arms), Head Start x2 to the class tree | needs R1 |
| R5 | labels ride along | SkyyGear 0.3.42 (gate label, `cwis`), SkyyAccessories 0.5.33 (Powers text), SkyyMenu 0.3.46 (help texts) | roll back alone |

Cross-check `python tools\ci\crosscheck.py --jar <new jars> --baseline`, `python tools\ci\lint.py`, smoke. Deploy R1-R4 TOGETHER.

**Rollback floor (new comment in tools\deploy_set.py):** SkyyTrees 0.6.0 + SkyyClasses 0.1.47 + SkyySkills 0.4.64 + SkyyRebirth 0.5.2 pin +
roll back TOGETHER. Rolling back: Trees 0.5.x shows the Combat tree again with its ranks (keys never moved) and reads modifier-level nodes
at rank 1 (the clamp is kept; their levels live in the raised use counts); `fold=done`, `Class.<C>.mgf`, `foldRespec` lines are ignored.
Classes 0.1.46 goes back to level unlocks (raised uses stay - harmless, levels capped at 5) and free key placement (the re-ordered
`p1 p2 a1 a2` stay valid). Before a rollback Undo the fold rows in Server Setup -> Changes (Trees `fold`, Classes `abil.fold`, Skills
`combatfold`). Never roll Trees below 0.4.0 (existing floor).

## 10. Questions for Skyy (default in [brackets])

1. Class tree points: 2 a class level (the class + Combat points you have today; every tree full by Lv 75-88)? [2 a level]
2. "2 ability slots" = 2 keys, each with its crouch alt: Ability 2 = A1 + picked A1-alt, Ability 3 = A2 + A2-alt, the branch decides the key? [yes]
3. Branch 2 has one A2-alt: its selection-gate row just unlocks it (no OR pick)? [yes]
4. Row gates per branch: 5 branch points a row + 3 in the row above + class level 5 a row (keeps abilities at today's levels)? [yes, level floor on]
5. Modifiers you can use today stay yours for free after the change (no points)? [yes, until that branch's next respec]
6. Combat's never-buildable parts (Flurry, Shield Wall, Mark the Prey and their upgrades, Salvage, Treasure Sense, 3 capstones) dropped; 3 new passives Rally / Reprisal / Second Wind added? [yes]
7. Combat Echo moves onto the Nexus Class arm (same node, same VP)? [yes]
8. Same-effect nodes in branch 3 (e.g. Assassin Power vs Hone Edge): keep both, different names? [keep both]
9. "Combat pets" (Wolf, Boar, Dog ...) keep that pet-type name? [keep]
10. One free class-tree respec for everyone after the update? [yes]

## 11. For the local session (UNVERIFIED)

- UNVERIFIED: the 4 key rows and their default order were read from SkyyClasses 0.1.46 comments (l.442, l.1173, l.7668), not run.
- UNVERIFIED: ~75-90 nodes + 52 px ability nodes pass `skyymap.check` on all 8 class pages (R0 must run it first).
- UNVERIFIED: B1 / B2 / B3 rank split per class (only the totals in 2.1 were computed; the builder's node table decides; Priest B1 may
  need Mana nodes moved to B2 to keep >= 25 ranks in each branch's rows 1-5).
- UNVERIFIED: the 3 new passives need appliers (SkyyClasses `thorns` / `lowHeal`, SkyySkills Rally regen) - no code exists yet; check for
  a duplicate cheat-death / thorns in pack mods (PROJECT-RULES 2 "no duplicates").
- Verified on a scratch copy of NewBetaTest (deleted): 4 SkyySkills profile files, all `Combat=0`; 4 SkyyTrees files, no `Skill.Combat.*`
  ranks (two still `v=2`, the treesV3 update runs on their next load).
- Main session: record the answers, add the floor comment, pin, and refresh the Class Balance Workbench (memory: balance chart) after R2.
