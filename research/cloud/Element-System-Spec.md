# Element System - spec draft

Cloud draft, 2026-10-09. Nothing built. Unblocks the Spellblade's **A2 Elemental Imbue** and the shelved Armory **Elemental swords**
(`research/classes/Spellblade.md` section "Elements", lines 203-222). Builds ON SkyyGear's live element lines; it does not redesign them.
Numbers are PLACEHOLDERS (all editable in Server Setup). Maths done with python3 (method shown next to each result).

## 0. Decisions this follows (never re-decided here)

| Source | Line(s) | What it fixes |
|---|---|---|
| `docs/answered/classes.md` | 172 (LOCKED 2026-10-08, popup batch 1) | Spellblade page defaults "Yes to all": **elements Fire / Water / Earth / Wind / Lightning + Poison status**; this also accepted page Question 7 (`research/classes/Spellblade.md` 545: the five with the statuses tabled, Poison = a status, Gravity sword = Earth) |
| `docs/answered/classes.md` | 167 | Spellblade = primarily elemental, owns the element system's application + the Armory Elemental swords; some NON-elemental AoE debuffs too |
| `docs/answered/classes.md` | 52, 54 | class-tree nodes may make an ability elemental: **pick ONE of the 5 elements** (Priest bubble example); choose-one paths |
| `docs/answered/gear.md` | 119 | the 4 Armory Elemental swords (Flame / Gravity / Ice / Poison) are SHELVED until tied to our element system |
| `docs/answered/gear.md` | 112 | Armory specials = BOSS DROPS; we add our own so no class has far more weapons |
| `SkyyGear-Plan.md` (read only) | lock 17, lines 60-67 | flat Earth / Thunder / Water / Fire / Air are **weapon-only**; element damage is applied on its own, then cut or raised by the target's **element affinity** and **elemental defence** (Wynncraft model); single-element defence = armor only; all-element % = class trees only |
| `SkyyGear-Plan.md` (read only) | 303 | **Powders** (Wynn's five) stay locked; slots / tiers / drops still open - not in this spec |
| `docs/plans/SkyWynn-Decisions.md` | 30, 71-74, 322 (row 5.8) | Wynn's five on gear; "not a swap to Hytale's set" |
| `research/Hytale-Runes-Research.md` | 53-54, 204-206, 296-299 | VERIFIED: the engine's five elements Fire / Water / Earth / Wind / Lightning = Wynn's Fire / Water / Earth / Air / Thunder; `ReactionDamageSystem` exists, vanilla uses no reactions |
| `research/Crit-Indicator-Research.md` | 148-150, 205 | VERIFIED: a damage cause's `DamageTextColor` reaches only a damaged PLAYER's indicator, never the attacker's numbers; changing a hit's cause breaks SkyyGear family checks |

## 1. In one table

| Part | v1 (launch) | Later |
|---|---|---|
| Elements | the five, one name each (section 2) | - |
| Gear | SkyyGear's live flat lines, now kept **per element** instead of one sum | element Defence lines go live; powders |
| Mobs | per-family **Weak +25% / Resist -25%** to element damage (bosses of their own element -50%) | mobs that deal element damage |
| Statuses | one per element, applied by **abilities only** (Imbue, Elemental Bubble, Frost Nova ...) - gear lines never | class-tree nodes deepen them |
| Reactions | **none** | 2 candidates (section 7) |
| Numbers on screen | one white number as today (element part inside it) | coloured element numbers via the crit style-swap |

## 2. The five elements

The same five everywhere; the engine id is internal. **Player-facing name: the gear's live Wynn names** (Fire, Water, Earth, Thunder,
Air) - they are already on every tooltip and the Stats page; the Spellblade page's Wind / Lightning become Air / Thunder in text
(Question 1).

| Element (shown) | Engine damage cause (internal) | Status (section 5) | Colour | Armory Elemental sword | Essence (`research/cloud/Soul-Orb-Spec.md` 14-27) |
|---|---|---|---|---|---|
| 🔥 **Fire** | `Fire` | **Burn** | `#FF6A3D` | Flame | Fire essence |
| 💧 **Water** | `Water` | **Chill -> Freeze** | `#4FA8FF` | Ice | Ice essence |
| 🪨 **Earth** | `Earth` | **Stagger** | `#C0905A` | Gravity (Q7 accepted: Earth, pull-down flavour) | (green crystal, Earth Crystal Golem drop - UNVERIFIED as essence) |
| ⚡ **Thunder** | `Lightning` | **Shock** | `#FFD84D` | - | Lightning essence |
| 🌪️ **Air** | `Wind` | **Gust** | `#A5EDE0` | - | Wind / Zephyr essence (UNVERIFIED item) |
| (status only) **Poison** | none (vanilla Poison effect) | **Poison** | `#7ED957` | Poison | - |

Essences are only the crafting flavour link (Elemental sword reforge, future powders); they add no rule here.

## 3. What SkyyGear already does (VERIFIED in `SkyyGear/build_skyygear_0.2.11.py`, the SET pin, read only)

| What | Where (lines) | Fact |
|---|---|---|
| The lines | 1242-1249 | `fEarth` "Earth Damage", `fThunder`, `fWater`, `fFire`, `fAir` (max 6 at 100%, weight 4); `rThunder` "Raw Thunder Damage", `rWater` (max 6, weight 3); `rElem` "Raw Elemental Damage" (max 3, weight 3, suffix "(each element)", 9987). Weapons only (slot `w`). LIVE. |
| Defence lines | 1265-1269 | `dEarth` ... `dAir` "X Defence", armor only, max 10, **live = 0 (coming later, never rolls while pool.later is off)** |
| Roll value | 8446-8457, 7501-7509, 1199-1200, 1399 | value = max x rarity % (Normal 30-60 ... Mythic 60-130) x level factor (25% at Lv 0 -> 100% at Lv 40, `stat.levelFull` 40), Java-rounded, at least 1 |
| One sum | 13055-13062 `GearHit.elemSum` | Earth + Thunder + Water + Fire + Air + Raw Thunder + Raw Water + **5 x Raw Elemental** = ONE integer; the element identity is lost here |
| Carried | 13063-13067 `GearHit.info` slot [5]; stored per Damage by `GearHitSys` 14675-14775 | only for a PLAYER attacker's weapon hit (`u != null`); ability hits with `EntitySource(caster)` also pass here (`research/cloud/Class-Ability-Engine-Spec.md` 327) |
| Weapon speed | 10482-10487 `GearSpeed.scaleInfo` | the sum x the swing weight w, stochastically rounded (mean exact) |
| Applied | 14808-14818 `GearTrueSys` (Filter, after `GearArmorSys`) | `+ True Damage + element sum` AFTER armor and Defense: never cut by Defence, never doubled by crits; a comment there already says "affinities are a later stage" = this spec |

Roll ranges today (python3: `max(1, round(max x pct/100 x factor/100))` over the live tables):

| Item level | Normal | Unique | Rare | Legendary | Fabled | Mythic |
|---|---|---|---|---|---|---|
| Fire Damage (max 6) Lv 1 | 1 | 1 | 1 | 1-2 | 1-2 | 1-2 |
| Lv 20 | 1-2 | 1-3 | 2-3 | 2-4 | 2-4 | 2-5 |
| Lv 40+ | 2-4 | 2-4 | 2-5 | 3-6 | 3-7 | 4-8 |
| Raw Elemental (max 3, x5) Lv 40+ | 1-2 | 1-2 | 1-2 | 1-3 | 2-3 | 2-4 |

So gear elements are small flat extras; the element system's weight comes from abilities (Imbue = +30% of the hit). No retune proposed.

## 4. The change on the gear side (small)

1. `elemSum` becomes **`elemSplit` = int[5]** (Fire, Water, Earth, Thunder, Air):
   Fire = fFire + rElem; Water = fWater + rWater + rElem; Earth = fEarth + rElem; Thunder = fThunder + rThunder + rElem; Air = fAir + rElem.
   The five add up to exactly today's sum (Raw Elemental still counts 5 times), so with no mob modifier nothing changes.
2. `GearHit.info` keeps slot [5] (the sum) for old readers and adds slot [6] = the int[5]; `scaleInfo` weights each of the five.
3. `GearTrueSys` adds `sum over e of round(part_e x (1 + mod_e / 100))`, where `mod_e` = the victim's Weak / Resist value for e
   (section 6; players and unknown mobs = 0). Still after armor, still never crit.
4. **Imbue** (section 8): when the attacker has an active Imbue (read from the bridge), the hit gets `+ imbuePct% of the pre-armor hit`
   as that element into the same int[5] - so mob resistances apply to it the same way, and the existing pipeline carries it.
5. Switch `elem.on` (default true): off = exactly 0.2.11 (one sum, no modifiers, no Imbue part).

No new Damage objects and no cause change (`research/Crit-Indicator-Research.md` 205: a cause change breaks SkyyGear's family checks).

## 5. Statuses (one per element; the Spellblade table, accepted in classes.md 172)

"H" on the Spellblade page = the hit that applied the status; here written as **% of the applying hit**. Statuses come from
**abilities only** (gear element lines never apply them - no proc spam, simple to read).

| Status | Effect (placeholder) | Stacks | Boss rule (crowd control halved, Spellblade page 228) |
|---|---|---|---|
| **Burn** (Fire) | 10% of the hit per second for 4 s, Fire damage | up to 3 (each its own 4 s) | full damage |
| **Chill** (Water) | -15% move + attack speed, 3 s | 3 Chills within 3 s = **Freeze** 1.5 s (a hit after 1 s breaks it) | slow 7.5%; Freeze 0.75 s; breakout rules apply |
| **Stagger** (Earth) | every 3rd Earth hit: stagger 0.4 s + **-10% defence 4 s** | the defence cut does not stack (refresh) | stagger 0.2 s; defence cut full |
| **Shock** (Thunder) | the hit jumps to 1 enemy within 3 blocks at 40%; shocked enemies take **+5% from everyone** 3 s | jump never chains further | full (it is damage + a debuff) |
| **Gust** (Air) | heavy hit: knock-up 0.5 s; every hit: +1 block knockback | - | **bosses immune** (the Pull rule, `research/cloud/Modifier-Pool-Spec.md` 38) |
| **Poison** (status only) | 8% of the hit per second for 6 s, plain damage (no element, no resist) | Assassin rules (`research/classes/Assassin.md`) | full |

Status damage (Burn ticks) counts as its element (so Resist cuts it); a resisted element still applies its status (only the damage
part changes - one rule). Example, python3 with a 100-damage hit and Imbue +30%:

| Target | Imbue part | Whole hit | vs neutral | Burn, 3 stacks over 4 s |
|---|---|---|---|---|
| Neutral | 30 | 130 | - | 120 |
| Weak (+25%) | 37.5 | 137.5 | +5.8% | 150 |
| Resist (-25%) | 22.5 | 122.5 | -5.8% | 90 |
| Boss of its own element (-50%) | 15 | 115 | -11.5% | 60 |

So picking the right element is worth about 6-12% on the hit and 25% on Burn - noticeable, never a wall (no mob is immune:
SkyyMobs' own "no mob is ever immune" rule, `SkyyMobs/build_skyymobs_0.1.5.py` 660).

## 6. Mob resistances

**SkyyMobs has NO resistance data today** (grep of `SkyyMobs/build_skyymobs_0.1.5.py`: only the level / curve / gap tables; the
vanilla role list is read from Assets.zip at build time). New table, matched on the NPC role id (longest match wins; no match = neutral).
Rule: each family has at most ONE Resist and ONE Weak; theme = it resists its own element and is weak to the one that "beats" it.

| Zone | Family (match, role ids UNVERIFIED unless seen in SkyyMobs) | Resist (-25%) | Weak (+25%) | Why |
|---|---|---|---|---|
| 1 Emerald Wilds | Trork, Goblin, Feran, Kweebec (hostile), wolves, bears, boars | - | - | beasts / folk: neutral |
| 1 | Skeleton (`Skeleton_Fighter` seen), Zombie | - | Fire | undead burn |
| 1 | Burnt Skeleton / Praetorian | Fire | Water | burnt |
| 1 | Earthen / Crystal Earth Golem | Earth | Air | stone, worn by wind |
| 1 | Fen Stalker, swamp toads | Water | Thunder | wet |
| 2 Howling Sands | Scarak (`Scarak_Fighter`, `Scarak_Louse` seen), Cactee (seen) | Earth | Water | sand / chitin |
| 2 | Sandswept Golem | Earth | Water | sand |
| 2 | sand skeletons | - | Fire | undead |
| 3 Whisperfrost | Yeti, Frost Golem, frost skeletons | Water | **Fire** | ice melts (theme beats the wheel) |
| 3 | Outlanders | - | - | folk |
| 4 Devastated Lands | Firesteel / Fire / Ember Golem (`Golem_Firesteel` seen), Emberwulf | Fire | Water | fire beings |
| 4 / 5 | Raptor, Cave Rex, Triceratops | - | - | beasts |
| 5 | Pterodactyl (and any flyer) | Air | Thunder | flyers |
| any | Void (`Spectre_Void`, `Crawler_Void` seen, Void Eye) | Thunder | Fire | void eats storms, fears light |
| any | Piranha (seen), sharks | Water | Thunder | aquatic |
| bosses | Dragon_Fire (seen) / Dragon_Frost | own element **-50%** | Water / Fire | boss of an element |

Server Setup table `elem.mobs` (SkyyMobs -> Mobs -> Element resistances), columns **Match | Resist | Weak** (element names or "-");
a server owner adds rows for other mods' mobs by role id (runtime only, PACK.md safe).

## 7. Reactions - recommend NONE at launch

The engine has `ReactionDamageSystem` (VERIFIED, unused by vanilla). Keep v1 readable: five statuses are already a lot. Later (a
class-tree layer, Spellblade page 216), at most two, both Spellblade + Mage team-ups:

| Reaction (later) | Trigger | Effect |
|---|---|---|
| Wildfire | Air hit on a Burning enemy | Burn spreads to enemies within 3 blocks (1 stack) |
| Shatter | Thunder hit on a Frozen enemy | ends Freeze, +50% of that hit as Water damage |

## 8. Which classes use which element

| Class | Element use | Source |
|---|---|---|
| ⚔️🔮 **Spellblade** | all five: **Imbue** (+30% of every arc / bash / crescent as the element for 12 s + its status); **attunement** picked out of combat, default **Fire**, Tempest path unlocks a second; an Elemental sword overrides it (Flame = Fire, Ice = Water, Gravity = Earth, **Poison sword = Poison status, no element** - Question 5); Breach / Rift / Shattering carry the element only while imbued | `research/classes/Spellblade.md` 161-222, 307-330 |
| 🔮 **Mage** | Frost Nova = **Water** (its Freeze + Chill ARE the Water status); Meteor / Lingering burn = **Fire** (Question 6); element otherwise set in the class tree (Plan lock 17, line 66) | `research/classes/Mage.md` 86-176 |
| ✨ **Priest** | Aegis A2 **Elemental Bubble**: pick 1 of 5 (no change without respec) | `research/cloud/Class-Tree-Paths.md` 22, 169, 172 |
| 🏹 **Archer** | Stormbow B2 burning patch = **Fire** (Burn) | `research/cloud/Class-Tree-Paths.md` 99 |
| 🗡️ **Assassin** | **Poison** (status, no element) | `research/classes/Assassin.md` 139-149 |
| 🛡️ Warrior, 🪓 Berserker, 🥋 Monk | none (physical; "Earthsplitter" / "Earthshaker" are names, not Earth) | class pages |
| Everyone | flat element lines on any weapon (SkyyGear, live) | section 3 |

## 9. How it shows

| Where | v1 |
|---|---|
| Gear tooltip | the existing lines keep their text; each element line's NAME in its element colour if the tooltip path takes a colour (UNVERIFIED) |
| Stats page (`research/cloud/Stats-Page-Spec.md` 69) | one row per element with its total, coloured; Raw Elemental shown inside each |
| Damage numbers | one white number (element part included), as today. Later: the crit style-swap (`research/Crit-Indicator-Research.md` row 1, already live for crits in SkyyGear 0.2.2) with one style per element |
| Status on a mob | the vanilla effect visuals where they exist (Frost chill / freeze, Poison - VERIFIED assets in Runes research 55; a Burn effect UNVERIFIED) + a short ASCII popup ("BURN", "FROZEN") via the marker popup (row 2 of that table) - ASCII only, the font has no symbols |
| Mob plate | optional tag "Weak: Fire" (Question 4, default off - learn it by playing) |
| Spellblade shield rune | glows in the element colour (page 183) |

Colours (python3 WCAG contrast vs the vanilla row `#101925` / a lighter panel `#1e2a3a`; body text `#96a9be` = 7.3 / 6.0 for scale):
Fire `#FF6A3D` 6.2 / 5.1 - Water `#4FA8FF` 7.1 / 5.8 - Earth `#C0905A` 6.2 / 5.1 - Thunder `#FFD84D` 12.8 / 10.5 - Air `#A5EDE0`
13.3 / 10.9 - Poison `#7ED957` 10.1 / 8.3. All above 4.5. Picked to avoid the rarity colours (`research/Vanilla-UI-Style-Guide.md`
192-193: Unique `#FFFF55`, Legendary `#55FFFF`, Fabled `#FF5555`, Set `#55FF55`) - so NOT Wynn's own red / aqua / yellow / green.

## 10. Server Setup rows (times in seconds)

| Mod | Key | Label | Type | Default | Range | Unit |
|---|---|---|---|---|---|---|
| SkyyGear | elem.on | Element system on | bool | true | - | - |
| SkyyGear | elem.weak | Damage bonus vs a weak mob | int | 25 | 0-100 | % |
| SkyyGear | elem.resist | Damage cut vs a resisting mob | int | 25 | 0-90 | % |
| SkyyGear | elem.bossResist | Boss vs its own element | int | 50 | 0-90 | % |
| SkyyMobs | elem.mobs | Element resistances | table Match\|Resist\|Weak | section 6 | - | - |
| SkyyClasses | imbue.pct / imbue.time | Imbue element damage / duration | int / dec | 30 / 12 | 0-200 / 1-60 | % / s |
| SkyyClasses | burn.pct / burn.time / burn.stacks | Burn per second / time / max stacks | int / dec / int | 10 / 4 / 3 | 0-100 / 1-20 / 1-10 | % / s / - |
| SkyyClasses | chill.slow / chill.time / freeze.at / freeze.time | Chill slow / time / Chills to freeze / Freeze time | int / dec / int / dec | 15 / 3 / 3 / 1.5 | 0-60 / 1-10 / 1-10 / 0.5-5 | % / s / - / s |
| SkyyClasses | stagger.every / stagger.time / stagger.def / stagger.defTime | Earth stagger | int / dec / int / dec | 3 / 0.4 / 10 / 4 | 1-10 / 0-2 / 0-50 / 1-20 | - / s / % / s |
| SkyyClasses | shock.pct / shock.range / shock.vuln / shock.time | Thunder shock | int / dec / int / dec | 40 / 3 / 5 / 3 | 0-100 / 1-10 / 0-25 / 1-10 | % / blocks / % / s |
| SkyyClasses | gust.knockUp / gust.kb | Air gust | dec / dec | 0.5 / 1 | 0-2 / 0-5 | s / blocks |
| SkyyClasses | poison.pct / poison.time | Poison | int / dec | 8 / 6 | 0-50 / 1-20 | % / s |
| SkyyClasses | elem.bossCc | Boss crowd-control strength | int | 50 | 0-100 | % |

## 11. Where the code lives (cross-mod only through `skyy.bridge`, plain java.lang types)

| Piece | Mod | Bridge |
|---|---|---|
| Per-element split, modifiers, Imbue part on the hit | SkyyGear (owns the lines and `GearTrueSys`) | reads `mob:fn:elem` and `classes:fn:imbue` |
| Resistance table | SkyyMobs (mob data) | new `mob:fn:elem(String roleId, Integer element)` -> Integer % (+25 / -25 / -50 / 0); SkyyGear caches per role; missing = 0 |
| Imbue state, attunement, statuses (tick, stacks, boss halving, popups) | SkyyClasses (ability engine) | new `classes:fn:imbue(String uuid)` -> String "Fire;30" or null; statuses applied in its own inspect hook (where the stunlock tracker already sits) |
| Elemental swords | SkyyGear (guaranteed element line by item id at identify) + loot list as boss specials | runtime ids only - never override The Armory's files (PACK.md) |

## 12. Build plan (small versions; use the next free version at build time)

| Step | Mods | Round | What |
|---|---|---|---|
| 0 | - | local probes | section 13 |
| 1 | SkyyGear 0.2.12 + SkyyMobs 0.1.6 | **full** (damage maths, 2 mods) | split + `elem.*` rows + `elem.mobs` + `mob:fn:elem`; Stats page colours (SkyyMenu only if it draws the rows). With `elem.on` and an empty table the damage equals 0.2.11 (harness: same totals on 1,000 random rolls) |
| 2 | SkyyClasses (the Spellblade build, after the ability engine) + SkyyGear | full (with that round) | Imbue + attunement + the six statuses + `classes:fn:imbue`; Frost Nova reuses Chill / Freeze |
| 3 | SkyyGear (+ loot list) | lean | unshelve the 4 Elemental swords as Spellblade boss specials with their element line (Skyy OK first - gear.md 119) |
| Later | SkyyGear, SkyyMobs | full | element Defence lines live + mobs that deal element damage; coloured numbers; reactions; powders |

## 13. Engine probes (all UNVERIFIED)

| # | Question | Why |
|---|---|---|
| E1 | Does the hit of an ability using `EntitySource(caster)` reach `GearHitSys` as a weapon hit (so it gets the flat lines)? And can a status tick be marked so it does NOT (else every Burn tick would add the weapon's element lines)? | double-counting |
| E2 | A vanilla Burn / on-fire EntityEffect: id, damage, visuals; can we apply it with our own damage (or only its visuals)? | Burn look |
| E3 | Vanilla Frost chill / freeze / slow effects (Runes research 55): apply to NPCs from code, durations editable, slow on NPC move + attack speed? | Chill / Freeze |
| E4 | NPC stagger: does a short effect / knockback interrupt an NPC attack (same as engine spec probe P8)? | Stagger, Gust |
| E5 | The real role ids for the section 6 families (Earth golem, frost skeleton, Burnt Praetorian, Yeti, Emberwulf, Fen Stalker, Void Eye, Pterodactyl, Dragon_Frost) | table rows |
| E6 | Can SkyyGear item tooltips colour part of a line (the rarity name path)? | tooltip colours |
| E7 | Do any vanilla mobs already deal Fire / Elemental-cause damage to players (golems, dragons, lava)? | later Defence stage |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | One name per element everywhere: the gear's live Wynn names **Fire, Water, Earth, Thunder, Air** (Spellblade text changes Wind -> Air, Lightning -> Thunder)? | **[yes, Wynn names]** |
| 2 | Mob resistances: each family Resist -25% to one element, Weak +25% to one; bosses -50% to their own; never immune (section 6 table)? | **[yes]** |
| 3 | Reactions: none at launch; Wildfire + Shatter later as Spellblade / Mage class-tree nodes? | **[none now]** |
| 4 | Show "Weak: Fire" on mob name plates? | **[no - learn by playing; a Bestiary later]** |
| 5 | Poison Elemental sword: Imbue applies Poison (no element damage, the +30% as plain damage)? | **[yes]** |
| 6 | Mage: Frost Nova = Water and Meteor = Fire (they use the shared statuses)? | **[yes]** |
| 7 | Gear element lines stay damage-only (statuses only from abilities)? | **[yes]** |
| 8 | Element colours: Fire orange-red, Water blue, Earth clay brown, Thunder amber, Air pale mint, Poison green (section 9)? | **[yes]** |

## For the local session

- Probes E1-E7 (need HytaleServer.jar / Assets.zip). E1 is the blocker for statuses: a status tick must never pick up weapon stats.
- Fill the real role ids into the section 6 table (`elem.mobs` defaults) from the vanilla role list SkyyMobs already reads.
- Step 1 is a damage change: full round + `python tools/ci/crosscheck.py` with the old/new SkyyGear; the harness must prove the five
  parts sum to 0.2.11's `elemSum` on random rolls with an empty `elem.mobs` table.
- Unshelving the Elemental swords (step 3) needs Skyy's OK (gear.md 119) and only runtime ids of The Armory's items.
