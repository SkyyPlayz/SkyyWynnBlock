# OUTBOX - cloud session -> local session

The local session's `cloud-link` mod polls this file on `origin/main` every 3 minutes and wakes the local session with every NEW block.
Cloud sessions: to answer the local session (a question, "done", a blocker), APPEND one block and push to main:

```
## <YYYY-MM-DD HH:MM> <short title>
<what you did / found / need, plain text, a few lines; name files by path>
```

Never edit or delete older blocks (their titles are how the mod knows what is new). Keep each block short; details go in the files.

## 2026-10-08 03:50 OUTBOX test
Cloud session got the new two-way channel message and will report done / blocked here from now on.

## 2026-10-08 03:58 Cloud list started
Working the CLOUD-RESUME list now: ability refresh, engine spec, Monk probe plan, class review prep, consistency pass + questions digest, and the 3 art tasks, all running in parallel. Class-Tree-Paths.md and Class-Tree-Build-Map.md are not touched. One OUTBOX block per finished task.

## 2026-10-08 04:04 Class review prep
Done: research/cloud/Class-Review-Prep-1008.md - Archer, Warrior, Mage, Assassin (Mage + Assassin were only partly reviewed 2026-10-07), abilities + modifiers, Echo candidates, gaps, 3 yes/no suggestions each.
Top questions: Meteor / God Killer Echo = 5th modifier or replace one [replace one]; drop the 'no Echo on stances' rule (Still Water) [yes]; A1-alt picks Hunter's Net / Bulwark Stance / Starfall / Vanishing Act [all four].
Stale for local: research/classes/Assassin.md:23 still says Pounce (now Shadow Step).

## 2026-10-08 04:04 Consistency pass 2026-10-07
Done: research/cloud/Consistency-Pass-1007.md. Fixed stale cloud lines: Zone 4-5 ore prices marked 'proposed 4,300 / 9,300 / 23,000', kunai void rule dropped (floorCheck 12 -> 0, no void protection), Monk colour Q closed (Saffron), Sushi seaweed, Sanctuary locked numbers in the old draft.
Open: does 'no void protection' also cover the dragon catching you over void (research/cloud/Dragon-Quest-Spec.md:82) and the Knockback+ void check (research/cloud/Modifier-Pool-Spec.md:35)?

## 2026-10-08 04:04 Questions digest 2026-10-07
Done: research/cloud/Questions-Digest-1007.md - 40 open questions not in the 1006 digest, top 10 = build blockers (Mana for physical classes, ability cap 15 / 14 points, tree size, Shadow Step +10%, Block +4.5%, Ember 4,300, Amberite 9,300 / Drakonite 23,000, Bazaar buy floor 0.9, ore regrow, fishing grade). Skyy can answer by row numbers.

## 2026-10-08 04:05 Enchanted v2 (rest)
Done: research/cloud/enchanted-art/enchanted-sheet-v2.png now 43 icons (+14: Onyxium / Silver / Gold ingots, Sand, Clay, Sandstone / Slate / Basalt cobble, Birch / Ash / Azure / Crystal logs, Fibre, Hay Bundle). 13 v1 icons left out on purpose (metal + wood blocks, Pumpkin Block) - README section 7.1.
Questions: Enchanted forms for Sand / Clay / stone cobbles [no, only Cobblestone + Rubble]; Hay Bundle as a 2nd Wheat step [not at launch]. All 14 base ids UNVERIFIED.

## 2026-10-08 04:06 Class emblems v2 (other 5)
Done: research/cloud/class-art/class-sheet.png - Warrior (sword + spear), Berserker (battleaxe + mace), Archer (recurve bow + arrow), Assassin (kunai + dagger), Mage (crystal staff + spellbook) at the Monk / Priest v2 detail; Monk + Priest bytes unchanged.
Questions: Archer bow only [yes]; locked = grey emblem [yes]; Mage crystal violet [yes]. Weak spots: Berserker axe busy at 64 px, kunai hides the dagger grip.

## 2026-10-08 04:08 Fishing UI mockup v2
Done: research/cloud/Fishing-UI-Mockup.png (v1 kept as research/cloud/Fishing-UI-Mockup-v1.png), generator research/cloud/fishing-ui/make_fishing_ui_v2.py, notes in research/cloud/Fishing-UI-Mockup.md v2 section. Shows the fight screen, minigame HUD bar (5 states), catch cards, Bench Rig tab and a new Pond Fish collection page; colours / sizes from tools/skyyui.py.
Questions: pack rarity ladder for fish [yes]; catch card 3 s + one chat line [yes]; species grid on the collection page now [yes].

## 2026-10-08 04:10 Class ability spec refresh
Done: research/cloud/Class-Ability-Spec-Draft.md + research/cloud/Modifier-Pool-Spec.md now follow every classes.md 2026-10-07 line (L111-L148); change list research/cloud/Ability-Refresh-1007.md. Floor = 18th modifier, Echo on 11 abilities, Follow on Mana Barrier, stunlock breakout section 2.8.
Budget fix PROPOSED: Echo 20-30% (was 30-70%) or Meteor / Palm Strike / Whirlwind break the caps. Questions: Echo 30% at L5 [yes]; Banner cooldown from the fall [yes]; Blood Frenzy per-swing cost [yes].
Local: research/classes/README.md pool needs --sync-pool (no Floor, 'offers 4'); research/cloud/Class-Tree-Paths.md stale nodes listed in the refresh file (E5, B3, LB2, W1, W2, no Mana Barrier Follow node).

## 2026-10-08 04:11 Class ability ENGINE spec
Done: research/cloud/Class-Ability-Engine-Spec.md - cast pipeline, 9 ability kinds, cooldowns in memory, Mana / Stamina rules, modifiers + Echo as data, zones / toggles / passives / chains, Server Setup rows, HUD (vanilla ability HUD or SkyyHud widget), 8-step build plan (E0 probe mod first). SkyyClasses 0.1.13 has no ability code yet; hooks cited by line.
Questions: 0.7 rune keys as main cast input + /cast backup [yes]; block vanilla runes for class players [yes]; Guardian Spirit cooldown shared across Priests [yes]. 15 engine probes (P1-P15) for the local session.

## 2026-10-08 04:18 Monk moves probe plan
Done: research/cloud/Monk-Probe-Plan.md - 13 probes as /mprobe commands (what each measures, pass / fail, fallback), 12-step in-game test script for Skyy. Draft probe jar SkyyMonkProbe/build_skyymonkprobe_0.1.py + test script come in a [cloud] pull request (UNTESTED, never pin before your build + review).
New APIs: holding / dragging mobs in mid-air (probes 7-8), slow effect id, self-sourced fall damage, melee damage cause. Findings: vault '7 blocks in 0.8 s' lands ~1.06 s; SkyySkills RollSys can pay roll XP on a Plunge landing (breaks 'no Acrobatics XP').
Questions: crouch as the free air jump [yes]; short slow if mobs can't hang [yes]; keep only -15% fall damage if slow-fall stutters [yes].

## 2026-10-08 04:19 Cloud list done
All 10 tasks from tonight's CLOUD-RESUME are done and pushed (one OUTBOX block each above). Draft probe jar: https://github.com/SkyyPlayz/SkyyWynnBlock/pull/11 - UNTESTED, left open for you to build + review before merging.
Refilled CLOUD-RESUME with 3: Ability engine probe plan (E0), Echo options page, Class tree stale nodes (waits until you say research/cloud/Class-Tree-Paths.md is free).

## 2026-10-08 04:25 PR 11 review round
Copilot reviewed https://github.com/SkyyPlayz/SkyyWynnBlock/pull/11: 2 fixes pushed (a64674e: plain rise speed used apex time and flew 2x; manifest IncludesAssetPack false + harness check). Left open on purpose: 'enemy() hits any NPC with stats (merchants, pets)' - same filter as live SkyyArmory 0.1.7 ArmoryTrav.kind; if the probes catch merchants/pets, fix it in a shared filter for Armory + Monk. Your call.

## 2026-10-08 06:35 Class tree stale nodes started
Got it - starting the Class tree stale nodes fix against live SkyyTrees 0.3.3 / SkyyArmory 0.1.9 (node ids kept; shipped text changes listed for your next SkyyTrees build). Echo options page running in parallel. Thanks for taking PR 11.

## 2026-10-08 06:38 Echo options for Skyy
Done: research/cloud/Echo-Options.md (one page). A = Echo 20-30% for all (every budget passes) [default]; B = per-ability caps (4 damage abilities 20-30%, heals / God Killer keep 30-70%); C = keep 30-70% but Echo costs more Mana / cooldown (Meteor 30 -> 37.4 Mana, Whirlwind 14 -> 16.9 s). Starfall breaks like Meteor; Hundred Fists breaks the Monk pair rule at 70%. Numbers use the draft model, UNVERIFIED vs real SkyyGear damage.

## 2026-10-08 06:41 Class tree stale nodes
Done: research/cloud/Class-Tree-Stale-Fix-1008.md + edits in research/cloud/Class-Tree-Paths.md and research/cloud/Class-Tree-Build-Map.md (new section 9 = text changes for the next SkyyTrees build; ids kept, no migration). W1 War Horn + B3 Crimson Frenzy already match live 0.3.3. Proposed: Mage PA3 Phase Step = Mana Barrier Follow upgrade; Priest PA2 Radiant Pulse -> Guiding Light (aim Sacred Heal at an ally); Berserker PA2 Shared Fury -> rage swap; Monk E5 text only.
CHECK (verified): SkyyArmory/build_skyyarmory_0.1.9.py line 6264 ArmoryTree.KEYS lists 11 nodes and leaves out Class.Monk.PB1 (Hard Knuckles), but line 9963 reads it - the tree page may still say 'Coming with SkyyArmory' for Hard Knuckles while it works (or the reverse is intended).
