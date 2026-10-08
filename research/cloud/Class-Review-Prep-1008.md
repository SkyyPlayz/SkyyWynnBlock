# Class review prep - Archer, Warrior, Mage, Assassin (cloud draft 2026-10-08)

Skyy will "go over the other classes later" (the 2026-10-07 class review covered Berserker, Monk and Priest in full). This page is the prep so that
review is a set of quick yes / no answers. Paper only: nothing is built, no numbers are decided, every number is a placeholder.

## Decisions this follows

| Source | Lines | What it fixes |
|---|---|---|
| docs/answered/classes.md | 111 | Meteor gains **Echo** (Skyy: "i was just looking at the mage class A1- alt Starfall and noticed the modifier, echo.  that should be available on the metro too.") |
| docs/answered/classes.md | 112-114 | Mana Barrier: at least 12 s, drains Mana instead of Health, placed dome + Follow, see-through look |
| docs/answered/classes.md | 115-117 | Assassin dagger charged = **Shadow Step** (replaces Pounce); NO void protection on any traversal (newest, wins) |
| docs/answered/classes.md | 118 | God Killer gains Echo (Skyy: "for the assassin, id give god killer the echo modification") |
| docs/answered/classes.md | 131 | Warrior shield traversal SHELVED unless a new shield weapon type is added |
| docs/answered/classes.md | 148 | Make the Monk and Assassin classes playable (weapons work for them) - build round |
| docs/answered/classes.md | 95 (2026-10-05) | Bows, crossbows, swords, spears stay VANILLA for now ("they stay vanilla FOR NOW. they will change later.") |
| research/classes/README.md | pool block | Echo is one of the 17 shared modifiers: "repeats once after 1 s at reduced strength · each level: stronger echo" |

**Which classes were reviewed on 2026-10-07** (checked line by line in docs/answered/classes.md, lines 111-148):

| Class | 2026-10-07 lines | Status |
|---|---|---|
| Priest | 140-147 | fully reviewed (Binding, Sacred Heal Echo, Sanctuary, Martyr's Grace, Shield Bubble, Guardian Spirit) |
| Berserker | 125-139 | fully reviewed (traversals, Enrage, Blood Frenzy, Banner, Whirlwind Echo) |
| Monk | 119-124, 128 | fully reviewed (fists, Palm Strike Echo, Still Water Echo, Flowing Form) |
| **Mage** | 111-114 | **partly**: only Meteor Echo and Mana Barrier. Starfall, Arcane Beam, Frost Nova and the staff / spellbook traversals were NOT looked at |
| **Assassin** | 115-118 | **partly**: only Shadow Step and God Killer Echo. Cloak, the A1-alt pair, Toxin and the kunai were NOT looked at |
| **Warrior** | 131 only | **not reviewed** (one shelved idea, no ability line) |
| **Archer** | none | **not reviewed** |

No other class had zero lines, so Berserker is NOT added. Mage and Assassin are included here because their reviews were only partial.

## 1. Summary (one screen)

| | Archer | Warrior | Mage | Assassin |
|---|---|---|---|---|
| Roles | crowd control + focus marker | tank + crowd control | burst damage + survival | priority killer + debuffer |
| Abilities (locked / proposed) | 3 locked, 2 proposed | 2 locked, 3 proposed | 2 locked, 3 proposed | 3 locked, 2 proposed |
| Echo today | none | none | Meteor (new), Starfall | God Killer (new) |
| Best Echo candidates | Explosive Arrow, Arrow Rain | Shield Shockwave, Rallying Guard | Frost Nova, (Mana Barrier: rule) | Toxin, Shadow Clone |
| Mobility | none (vanilla bow / crossbow) | sword Thrust dash, spear throw (vanilla) | **strong**: staff teleport, spellbook Levitate | **strong**: kunai teleport + Shadow Step (not built) |
| Defence | none (roots are the defence) | **strong** | Mana Barrier only | Cloak, Shadow Clone / smoke |
| Biggest gap | no mobility and no defence at all | no mobility (shield idea shelved), low damage | no heal / sustain; one defensive tool | AoE: single-target only |
| Open picks | A1-alt: Arrow Rain or Hunter's Net | A1-alt: Bulwark or Unbreakable; taunt engine check | A1-alt: Starfall or Arcane Beam | A1-alt: Shadow Clone or Vanishing Act |
| Review depth on 10-07 | none | none | partial | partial |

Echo in this project (important for every section below): Skyy added Echo to Meteor, God Killer, Palm Strike, Still Water, Whirlwind, Sacred Heal, Martyr's Grace,
Shield Bubble and Warlord's Banner on 2026-10-07. In every case the line reads the same way: the effect **happens once more, weaker, about 1 s later, and each Echo
level makes the repeat stronger**. Examples: Meteor = "a second, weaker meteor on the same spot 1 s later" (docs/answered/classes.md:111); God Killer = "the empowered
strike repeats once 1 s later at reduced strength" (118); Banner = the buff "lingers briefly at reduced strength after the banner ends" (132). Two Skyy twists: Still Water's Echo
brings back the counter-hits for ~3 s while you can move (124), and the Modifier Pool Spec rule "cannot echo an echo; echoes cost nothing; strength 30 / 40 / 50 / 60 / 70%"
(research/cloud/Modifier-Pool-Spec.md:39) is the working default for all of them. That spec line also says Echo is NOT for channels, stances or cloak - but Skyy gave it to the Still Water
stance, so that exclusion is stale (see Questions, Q2).

&nbsp;

## 2. Archer - crowd control + focus marker

Source: research/classes/Archer.md (abilities lines 78-160), numbers from research/cloud/Class-Ability-Spec-Draft.md (rows 54-58). Cost = Mana; the Archer has only ~10 base Mana (Spec Draft:33-35 and finding 1 at :176).

| Ability | What it does | Modifiers (4, equip 2) | Cost / CD | Status | Source |
|---|---|---|---|---|---|
| A1 Pinning Shot | piercing arrow, 30 blocks; Rooted ~2 s + Marked 6 s (+15% damage taken from everyone) | Pierce, Split, Duration+, Power+ | 10 / 12 s | locked | research/classes/Archer.md:78; Spec Draft:54 |
| A1-alt A Arrow Rain | 6-block rain 3 s, Slowed; still inside after 2 s = Rooted 1.5 s + Marked | Radius+, Duration+, Lingering, Power+ | 16 / 20 s | proposed | research/classes/Archer.md:98; Spec Draft:55 |
| A1-alt B Hunter's Net | net bursts into 4-block root zone 3 s; all caught Marked 8 s | Radius+, Duration+, Pull, Split | 14 / 18 s | proposed | research/classes/Archer.md:114; Spec Draft:56 |
| A2 Rapid Fire | 15 arrows in 3 s, each about half a shot | Ricochet, Pierce, Duration+, Slow | 14 / 20 s | locked | research/classes/Archer.md:130; Spec Draft:57 |
| A2-alt Explosive Arrow | next charged shot 2x damage in a 4-block blast | Radius+, Split, Lingering, Knockback+ | 12 / 14 s | locked | research/classes/Archer.md:146; Spec Draft:58 |
| Weapons | shortbow + crossbow: vanilla attack and charged, no traversal (ideas for later: Grapple Arrow, Dodge Roll) | - | - | locked vanilla | research/classes/Archer.md:52-70 |

**Echo candidates** (Echo is not offered by any Archer ability today):

| Ability | What Echo would mean | Verdict |
|---|---|---|
| Explosive Arrow | a second, weaker blast on the same spot 1 s later (same idea as Meteor) | **best fit** - it is the Archer's Meteor |
| Arrow Rain | a second shower right after, like Starfall's Echo | good, only if Arrow Rain wins the A/B pick |
| Pinning Shot | a second arrow at the same target 1 s later: re-applies the Mark, no second root | ok, but Root + Echo + Pierce could chain-lock; keep root once |
| Hunter's Net | a second, smaller net | weak (root zone already lasts 3 s) |
| Rapid Fire | - | no: it is a 3 s burst (channel-like), Echo rules exclude channels |

**Gaps**
- **Mobility: none.** Bow and crossbow are vanilla for now (Skyy 2026-10-05). The class tree gives only +4% move speed (research/cloud/Class-Tree-Paths.md, Archer T4).
- **Defence: none.** Roots and nets are soft defence only; no shield, heal, dodge or cloak.
- **Overlaps:** Mark (+15% damage taken) overlaps the Assassin's First Strike / Death Mark idea; roots overlap the Warrior's stuns; Explosive Arrow AoE overlaps Mage Meteor (Archer's is tied to a charged shot, so cheaper).
- **Power check:** Rapid Fire is the highest martial share (45% of weapon DPS at max, Spec Draft:133); Pinning Shot + Rapid Fire = 65% (limit 80%).
- **Low Mana:** ~10 base Mana, so 12-16 Mana abilities need the "+2 Mana per class level" row (Spec Draft:33-35) or Stamina costs.

**3 suggestions**

| # | Suggestion | Recommended default | Yes / no |
|---|---|---|---|
| A1 | Give Explosive Arrow Echo (second, weaker blast on the same spot 1 s later). It takes the slot of **Lingering** (both repeat damage) [or becomes a 5th choice - see Q1]. | **Yes**, replaces Lingering | |
| A2 | Lock the A1-alt as **Hunter's Net** (Arrow Rain dropped). The Archer's job is crowd control; Rapid Fire + Explosive Arrow already cover damage, and Net brings Pull (the only Archer Pull). | **Yes**, Hunter's Net | |
| A3 | Write down the later traversal plan so it is not forgotten: shortbow = Grapple Arrow, crossbow = Dodge Roll (both already ideas in the class file). Still vanilla until Skyy says build. | **Yes**, record only | |

&nbsp;

## 3. Warrior - tank + crowd control

Source: research/classes/Warrior.md (abilities 76-164), numbers research/cloud/Class-Ability-Spec-Draft.md (rows 45-49).

| Ability | What it does | Modifiers (4, equip 2) | Cost / CD | Status | Source |
|---|---|---|---|---|---|
| A1 Rallying Guard | you + party within 6 blocks take 20% less damage 6 s; mobs within 8 blocks turn on you 4 s | Duration+, Radius+, Power+, Ward | 12 / 24 s | locked | research/classes/Warrior.md:76; Spec Draft:45 |
| A1-alt A Bulwark Stance | 8 s: 50% less front damage, front projectiles blocked, you move 30% slower; allies behind take 25% less | Duration+, Power+, Knockback+, Ward | 14 / 28 s | proposed | research/classes/Warrior.md:96; Spec Draft:46 |
| A1-alt B Unbreakable | taunt 8 blocks; 5 s cannot drop below 1 HP; heal 20% of damage taken | Duration+, Radius+, Leech, Power+ | 16 / 40 s | proposed | research/classes/Warrior.md:114; Spec Draft:47 |
| A2 Shield Shockwave | 6-block cone, stun ~1.5 s, one weapon hit | Radius+, Knockback+, Slow, Power+ | 10 / 12 s | locked | research/classes/Warrior.md:132; Spec Draft:48 |
| A2-alt Iron Chain | chain 15 blocks, drags first enemy to you, stun 1 s | Pull, Chain, Slow, Power+ | 12 / 14 s | proposed | research/classes/Warrior.md:148; Spec Draft:49 |
| Weapons | swords: vanilla combo + Thrust dash (needs Stamina); longswords: stab, no movement; spears: stab + spear throw. Shield traversal SHELVED (classes.md:131) | - | - | locked vanilla | research/classes/Warrior.md:50-68 |

**Echo candidates** (none today):

| Ability | What Echo would mean | Verdict |
|---|---|---|
| Shield Shockwave | a second, weaker cone 1 s later (damage + a short stun; the 1.5 s stun is not repeated at full length) | **best fit** - direct copy of the Palm Strike Echo (classes.md:123) |
| Rallying Guard | the damage reduction lingers briefly at reduced strength after it ends, same idea as the Banner Echo (classes.md:132); the taunt is NOT echoed | good, fits "tank protects the party" |
| Iron Chain | a second, weaker pull | no: dragging twice is clumsy |
| Bulwark Stance / Unbreakable | - | no: stances; Unbreakable echo would be a second "cannot die" window (too strong) |

**Gaps**
- **Mobility: only vanilla.** Sword Thrust dash and spear throw. Skyy said on 2026-10-07 that he wants "a traversal per weapon" for the Berserker (classes.md:125); the Warrior has no such line. The shield idea is shelved.
- **Damage is low** (Shield Shockwave 16%, Iron Chain 8% of weapon DPS at max, Spec Draft:130-131) - fine for a tank but the Warrior has no damage-per-Mana story of its own.
- **Overlaps:** Rallying Guard party reduction overlaps Priest Shield Bubble and the Berserker Banner defence; Unbreakable (cannot die) overlaps Priest Guardian Spirit (a save); Shield Shockwave stun overlaps Monk Palm Strike; Iron Chain Pull overlaps Hunter's Net Pull.
- **Engine check still open:** can a mod make mobs target the Warrior (taunt)? If not, Rallying Guard uses a stun (research/classes/Warrior.md:224). Both A1-alts and Iron Chain lean on taunt.
- No self-heal in the base kit (only Leech modifier and tree Juggernaut path).

**3 suggestions**

| # | Suggestion | Recommended default | Yes / no |
|---|---|---|---|
| W1 | Give Shield Shockwave Echo (second, weaker cone 1 s later, damage + short stun). It replaces **Slow** in the list (Slow also comes from Iron Chain) [or 5th choice - Q1]. | **Yes**, replaces Slow | |
| W2 | Give Rallying Guard Echo = the damage reduction lingers ~3 s at reduced strength after it ends; taunt not repeated. | **Yes**, replaces Ward | |
| W3 | Lock the A1-alt as **Bulwark Stance** (Unbreakable dropped): Bulwark is unique (front block, allies behind) and drives the Guardian tree path; Unbreakable overlaps the Priest's Guardian Spirit. | **Yes**, Bulwark | |

&nbsp;

## 4. Mage - burst damage (glass cannon)

Source: research/classes/Mage.md (abilities 87-175), numbers research/cloud/Class-Ability-Spec-Draft.md (rows 63-67). Mana: 30 + 10 per Sorcery level (Spec Draft:29).

| Ability | What it does | Modifiers | Cost / CD | Status | Source |
|---|---|---|---|---|---|
| A1 Meteor | spot up to 25 blocks; after 1 s a 4-block meteor, ~3x a charged staff shot | Radius+, Power+, Lingering, Split, **Echo** (new 10-07) | 30 Mana / 14 s | locked | research/classes/Mage.md:87; Spec Draft:63 |
| A1-alt A Starfall | 3 s, 12 stars over a 6-block area, each ~40% of a Meteor | Duration+, Radius+, **Echo**, Power+ | 36 / 18 s | proposed | research/classes/Mage.md:109; Spec Draft:64 |
| A1-alt B Arcane Beam | channel a 20-block beam up to 3 s, damage ramps 1x to 3x | Pierce, Duration+, Power+, Slow | 30 / 18 s | proposed | research/classes/Mage.md:125; Spec Draft:65 |
| A2 Mana Barrier | placed dome, 12 s, damage drains Mana (1 Mana per 2 HP) instead of Health; see-through look; ends at 0 Mana | Duration+, Power+, Ward, Knockback+, Follow | 20 / 30 s | locked (10-07) | research/classes/Mage.md:143; Spec Draft:66 |
| A2-alt Frost Nova | freeze enemies in 5 blocks 2 s (a hit breaks it after 1 s), then Chill 3 s | Radius+, Duration+, Slow, Power+ | 24 / 22 s | proposed | research/classes/Mage.md:163; Spec Draft:67 |
| Staff (charged) | TELEPORT 10 blocks the way you look + light trail that hurts enemies; no void protection | - | Mana : Stamina 2 : 1 (Spec Draft section 1.1) | locked | research/classes/Mage.md:55-71 |
| Spellbook (charged) | LEVITATE up ~8 blocks, hover ~3 s, no fall damage | - | same | locked | research/classes/Mage.md:73-79 |

Note: Meteor lists 5 modifiers and Mana Barrier lists 5 in research/classes/Mage.md (lines 38, 41), but the written rule is "each ability offers 4, you equip 2" - see Q1.

**Echo candidates**

| Ability | What Echo would mean | Verdict |
|---|---|---|
| Meteor | second weaker meteor on the same spot 1 s later (LOCKED) | done |
| Starfall | already lists Echo "a second, weaker shower right after" (research/classes/Mage.md:121) - wording differs from the rest (see M2) | done, needs one wording |
| Frost Nova | a second weaker pulse 1 s later that only **Chills** (no second freeze) | good |
| Mana Barrier | dome lingers briefly at reduced strength after it ends | possible, but Echo rules exclude stances (Q2); it already has Follow and Knockback+ |
| Arcane Beam | - | no: a channel (rules exclude it) |
| Staff teleport | a second, free blink back to the start | not an ability modifier; closer to tree node R2 "Rift Echo" (research/cloud/Class-Tree-Paths.md, Mage Path A) - the name clashes with the Echo modifier |

**Gaps**
- **Mobility is strong** (teleport + Levitate) and the tree adds more; no gap.
- **Defence / sustain is thin:** Mana Barrier is the only defensive tool, no heal and no Leech on any Mage ability; "Survival" is the second role. "Without the healing from priest, you die really easy" (docs/answered/classes.md:29, 2026-10-03 test).
- **Overlaps:** Meteor / Starfall / Explosive Arrow (Archer) are all ground AoE burst; Frost Nova freeze overlaps Warrior Shockwave and Monk stuns; the Mage teleport overlaps the Assassin's kunai teleport and Shadow Step (same fantasy, different weapon - fine).
- **Open since the class file:** "Mage A2-alt (Frost Nova proposed)" and "A1-alt pair" (research/classes/Mage.md:38-40).

**3 suggestions**

| # | Suggestion | Recommended default | Yes / no |
|---|---|---|---|
| M1 | Give Frost Nova Echo: a second weaker pulse 1 s later that only Chills (no second freeze, so no permanent lock). | **Yes**, replaces Power+ | |
| M2 | Use ONE Echo wording for all: "repeats once 1 s after the ability ends". Starfall's "a second, weaker shower right after" becomes the same. | **Yes** | |
| M3 | Lock the A1-alt as **Starfall** (Arcane Beam dropped): Skyy already looked at Starfall and wanted Echo from it; Beam is a channel, harder to build (Spec Draft:218, engine check). | **Yes**, Starfall | |

&nbsp;

## 5. Assassin - priority killer + debuffer

Source: research/classes/Assassin.md (abilities 77-169), numbers research/cloud/Class-Ability-Spec-Draft.md (rows 103-107), research/Shadow-Step-Spec.md.

| Ability | What it does | Modifiers (4, equip 2) | Cost / CD | Status | Source |
|---|---|---|---|---|---|
| A1 Cloak + First Strike | invisible ~8 s (breaks on attack); next hit +100% crit chance (crit cap 150%, triple crit above 200%) | Duration+, Efficiency, Power+, Haste | 14 / 30 s | locked | research/classes/Assassin.md:77; Spec Draft:103 |
| A1-alt A Shadow Clone | cloak + decoy mobs attack 5 s; bursts when it ends | Duration+, Power+, Split, Knockback+ | 20 / 35 s | proposed | research/classes/Assassin.md:99; Spec Draft:104 |
| A1-alt B Vanishing Act | instant 3 s cloak + 4-block smoke; enemies lose track 2 s and are slowed | Radius+, Duration+, Slow, Efficiency | 16 / 28 s | proposed | research/classes/Assassin.md:117; Spec Draft:105 |
| A2 Toxin | thrown vial, 4-block poison cloud 5 s: Poisoned + Weakened (-15% damage dealt) | Radius+, Duration+, Lingering, Chain | 12 / 16 s | locked | research/classes/Assassin.md:135; Spec Draft:106 |
| A2-alt God Killer | next hit on a boss / mini-boss 2x, 3x from behind; stacks with First Strike | Power+, Duration+, Efficiency, Haste, **Echo** (new 10-07) | 14 / 45 s | locked | research/classes/Assassin.md:151; Spec Draft:107 |
| Daggers (charged) | **Shadow Step** replaces Pounce: vanish, fading shadow, appear behind the mob nearest your aim (24 blocks), next hit = guaranteed backstab + 10% (placeholder); no mob = step 18 blocks; no void protection | - | Stamina 4, CD 6 s Crude to 4 s Onyxium (all placeholders); NOT BUILT | locked (10-07) | research/classes/Assassin.md:57; research/Shadow-Step-Spec.md:30-32 |
| Kunai (charged) | throw + teleport to where it lands (~20 blocks); hold right-click to return within ~8 s with AoE knockback | - | not set in the class file | locked | research/classes/Assassin.md:59-69 |

Stale text found: the research/classes/Assassin.md map still says daggers "Charged: Pounce - vanilla traversal" (research/classes/Assassin.md:23) although line 57 says Shadow Step replaces it. No change made here (not my file); listed for the local session.

**Echo candidates**

| Ability | What Echo would mean | Verdict |
|---|---|---|
| God Killer | empowered strike repeats once 1 s later (LOCKED) | done |
| Toxin | a second, weaker poison cloud 1 s after the first | **best fit** - zones can echo (Modifier-Pool-Spec.md:39) |
| Shadow Clone | a second, smaller burst when the first ends | good, only if it wins the A/B pick |
| Vanishing Act | a second, smaller smoke puff | ok, only if it wins the A/B pick |
| Cloak + First Strike | - | no: Echo rules exclude cloaks, and a second +100% crit chance would break the crit cap |

**Gaps**
- **Mobility is strong** (kunai teleport + Shadow Step, once built). Two teleports on one class is on purpose (different weapons), but keep their roles apart: Shadow Step = close in on a target, kunai = reposition / escape.
- **Defence:** Cloak and the A1-alt (decoy or smoke) are the only defensive tools; no heal, no shield.
- **No AoE damage:** Toxin and Shadow Clone are the only multi-target tools; fine for a single-target killer but leaves the Assassin weak against packs.
- **Overlaps:** teleport with Mage; Weaken (-15% damage dealt) with Berserker / Warrior defensive buffs; Mark-like setup (First Strike, Death Mark tree node) with the Archer's Mark.
- **Engine checks still open (UNVERIFIED):** can a mod pick a mob's target (Shadow Clone and Vanishing Act both need it - research/classes/Assassin.md:107); the whole Shadow Step list (research/Shadow-Step-Spec.md section 5).
- **Not playable yet** - classes.md:148 says build the Assassin class (daggers / kunai), so nothing here can be tested in game before that round.

**3 suggestions**

| # | Suggestion | Recommended default | Yes / no |
|---|---|---|---|
| S1 | Give Toxin Echo (a second, weaker poison cloud 1 s later, same spot). It replaces **Lingering** (both extend damage on the ground). | **Yes**, replaces Lingering | |
| S2 | Lock the A1-alt as **Vanishing Act** (Shadow Clone dropped): cheaper to build (no clone entity), fits "cloak, strike, leave" and the debuffer role (Slow in smoke). Both still need the mob-target engine check. | **Yes**, Vanishing Act | |
| S3 | Accept Shadow Step's two open defaults: "small bonus" = +10% on the guaranteed backstab; the guaranteed-backstab window = 3 s (research/Shadow-Step-Spec.md:30, 64). | **Yes**, +10% and 3 s | |

&nbsp;

## Questions for Skyy

| # | Question | Recommended default |
|---|---|---|
| Q1 | You added Echo to Meteor and God Killer, which now list **5** modifiers. Does Echo become a **5th** choice (an ability offers 5, you still equip 2), or does it **replace** one of the old four? | [replace one, keeping "offers 4": the suggestions above name which one] |
| Q2 | The Modifier Pool Spec says Echo is not for channels, stances or cloaks, but you gave it to Still Water (a stance). Drop that exclusion for stances (keep it for channels and cloak)? | [yes, drop it for stances; keep channels and cloak out] |
| Q3 | Archer, Warrior, Mage, Assassin A1-alt picks (suggestions A2, W3, M3, S2 above): Hunter's Net, Bulwark Stance, Starfall, Vanishing Act? | [all four as written] |
| Q4 | Echo on the five suggested abilities (Explosive Arrow, Shield Shockwave, Rallying Guard, Frost Nova, Toxin)? | [yes to all five] |
| Q5 | Warrior traversal: your "traversal per weapon" idea (2026-10-07, Berserker) - should the Warrior also get one per weapon later (spear = Spear Leap; sword keeps the vanilla Thrust dash)? Still vanilla for now either way. | [yes, record Spear Leap as the later plan] |
| Q6 | Physical classes (Archer, Warrior, Assassin) have ~10 Mana: add "+2 Mana per class level" so their 12-16 Mana abilities work? (Spec Draft:33-35 and :222, still open) | [yes] |
| Q7 | Mage "survival" gap: add a Leech modifier to Meteor / Starfall (hits heal you a little) so the glass cannon has some sustain? | [no for now - test the Priest pairing first; decide after a play session] |

## For the local session

| # | Item | Why / what to check |
|---|---|---|
| 1 | Taunt: can a mod make mobs target a player? (Warrior Rallying Guard / Unbreakable / Iron Chain; Assassin Shadow Clone / Vanishing Act) | UNVERIFIED, needs HytaleServer.jar (research/classes/Warrior.md:224, research/classes/Assassin.md:107) |
| 2 | Echo implementation per kind: "happens once more after 1 s at 30-70% strength, costs nothing, cannot echo an echo" | UNVERIFIED engine support (research/cloud/Modifier-Pool-Spec.md section 7 row 1 says Echo needs our own composition) |
| 3 | research/cloud/Modifier-Pool-Spec.md section 4 is stale: it says only Starfall and Hundred Fists offer Echo (2 abilities) - now Meteor, God Killer, Palm Strike, Still Water, Whirlwind, Sacred Heal, Martyr's Grace, Shield Bubble and Banner too; the "4 per ability" count (140 slots) is also off. Needs a refresh once Q1 is answered. | cloud file, safe to edit later |
| 4 | research/cloud/Class-Ability-Spec-Draft.md section 2 rows for Meteor, God Killer, Palm Strike etc. do not mention Echo yet | cloud file, safe to edit later |
| 5 | research/classes/Assassin.md:23 map still says daggers' charged = Pounce | stale vs line 57; fix with `python tools/class_pages.py` flow when the Assassin build round starts |
| 6 | Name clash: tree node "Rift Echo" (Mage Path A R2) vs the Echo modifier; same for any future "Echo" tree names | rename the node (suggest "Rift Chain") when research/cloud/Class-Tree-Paths.md is next edited (it is read-only for me tonight) |
| 7 | Shadow Step build (not started): replace the dagger charged interaction, cone target pick, teleport + yaw to the target's back, forced backstab flag, fading shadow | all UNVERIFIED (research/Shadow-Step-Spec.md section 5) |
| 8 | Assassin and Monk class slots must exist before any Assassin test (docs/answered/classes.md:148) | build round |
| 9 | docs_check result for this file (run in this session) | see the report to the main session |
