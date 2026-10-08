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
