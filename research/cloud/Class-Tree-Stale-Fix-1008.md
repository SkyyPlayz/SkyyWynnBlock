# Class tree stale nodes - fixed against the live SkyyTrees 0.3.3 (2026-10-08)

Cloud draft, 2026-10-08. Task: the stale nodes that research/cloud/Ability-Refresh-1007.md section 5 row 2 (and
research/cloud/Class-Ability-Spec-Draft.md "For the local session" row 8) listed for research/cloud/Class-Tree-Paths.md. Edited:
research/cloud/Class-Tree-Paths.md (rows + header + findings + change log) and research/cloud/Class-Tree-Build-Map.md (new section 9).
Live check (read-only): `SkyyTrees/build_skyytrees_0.3.3.py` (`CPATHS`, the node texts that shipped 2026-10-08 00:34) and
`SkyyArmory/build_skyyarmory_0.1.9.py` (`ArmoryTree.KEYS`, the nodes it applies).

## 1. Decisions followed (docs/answered/classes.md)

| Line | Decision | Used for |
|---|---|---|
| 2026-10-04 locks (class tree) | the class tree changes HOW an ability works; paths lock the other two; modifiers live in the ability tree | every replacement changes behaviour, none copies a modifier (except the L113 one Skyy asked for) |
| L113 (2026-10-07) | Mana Barrier = placed dome; "a Follow modifier / skill-tree upgrade makes the dome move with you" (Skyy: "there is an upgrade in the skill tree to make it follow you, correct?") | the missing Follow node -> Mage R3 Phase Step |
| L127-L128 | Enrage picks players 8 / party 16 ONCE at activation, not an aura; Flowing Form combo stacks, the 15-combo doubling is gone | W1 checked, W2 replacement picks once; E5 text |
| L133 | Warlord's Banner: every mob killed in its range extends it (1 / 3 / 5 s, cap 60 s) | W2 overlap |
| L136-L138 | Blood Frenzy per stack +1.5% damage, +1% attack speed, +0.5% move; allies half | B3 checked |
| L141 | Sacred Heal gains Echo (a second, weaker instant heal 1 s later in the same circle; 20-30% in research/cloud/Modifier-Pool-Spec.md) | LB2 overlap |

Task rule: node ids stay (saved files hold ids); a shipped node whose text changes is marked "(live 0.3.3 text differs - change in the
next SkyyTrees build)" and gets a row in research/cloud/Class-Tree-Build-Map.md section 9; overlapping nodes are replaced by a proposal
with a default, never deleted.

## 2. What the live build says

- Two of the six "stale" items were already fixed in research/cloud/Class-Tree-Paths.md on 2026-10-07 (commit 41827e7): the refresh read
  the older text. **W1 War Horn** has no "party radius +3" any more and **B3 Crimson Frenzy** has no "+2.5% (was +2%)"; both live texts match.
- All the nodes touched here are kind **K** (waiting for the class abilities, reader SkyyClasses). Waiting nodes cannot be bought, so **no
  player owns them** - changing their text needs no migration or refund.
- The 11 nodes that work now (SkyyTrees alone) and the 11 keys SkyyArmory 0.1.9 lists (`ArmoryTree.KEYS`: Mage T2 T3 PA1 PA2 PB1, Priest
  T1, Assassin T3 PC1-PC4) are untouched. (Side note: the deploy log says SkyyArmory reads 12 nodes incl. Monk Hard Knuckles; the KEYS
  string in the 0.1.9 script lists 11 - Class.Monk.PB1 is read in code but not in KEYS. Not part of this task; see section 5.)

## 3. Node table

Doc ids -> tree ids: Mage R3 = PA3, Priest LB2 = PA2, Berserker W1 = PA1, W2 = PA2, B3 = PB3, Monk E5 = PC5.

| Node | Was | Now | Live 0.3.3 shipped? | Build change needed |
|---|---|---|---|---|
| Mage R3 Phase Step (PA3) | blink 5 back, dome placed where you land; "moving it stays the Follow modifier"; dome 12 -> 10 s | **the Mana Barrier Follow tree upgrade** (L113): blink 5 back and the dome moves with you at full strength (modifier: 80-100%); the Follow modifier cannot also be equipped on Mana Barrier; dome 12 -> 10 s | yes, as waiting text "Mana Barrier: blink 5 blocks back, the dome lands where you land - dome 10 s" | yes - text only (Build-Map section 9) |
| Priest LB2 Radiant Pulse (PA2) | heal pulses again after 2 s at 50%; cooldown +3 s (= Echo, and stronger than Echo's 30% max) | **Guiding Light** (proposed): Sacred Heal can be aimed at an ally you look at within 20 blocks, the 9-block circle forms on them; cast 0.5 s slower | yes, waiting text "Sacred Heal pulses again after 2 s at 50% - cooldown +3 s" | yes - name + text |
| Berserker W2 Shared Fury (PA2) | allies' kills extend Enrage 1 s (max +5); cooldown +3 s (= the Banner's kill extension, one node before W3 Banner Bearer) | **rage swap** (proposed, name kept): the ally you look at when casting (within 16, picked once) gets your doubled buff, you get the ally buff; cooldown +3 s | yes, waiting text "Allies' kills extend Enrage 1 s each (max +5 s) - cooldown +3 s" | yes - text |
| Berserker W1 War Horn (PA1) | (old, pre-2026-10-07) party radius +3 | already: second call 3 s after activation for late arrivals, allies start at +15%; your peak -5 | yes, matches | no |
| Berserker B3 Crimson Frenzy (PB3) | (old) stacks +2.5% (was +2%) + heal 0.5% | already: each stack heals you 0.5% max Health, allies in the aura 0.25%; Mana + Stamina per attack +20% | yes, matches | no |
| Monk E5 Serenity (PC5) | trade-off "max combo 20 -> 18 (the old 15-combo doubling no longer exists)" | trade-off "max combo stacks 20 -> 18" (doubling remark removed) | yes, "max combo 18" matches | no (doc only) |

Balance (python3, from research/cloud/Class-Ability-Spec-Draft.md section 5 Enrage averages): rage swap moves the self average (16.7%
Lv 1 / 23.3% Lv 15) to one ally and the party average (8.3% / 13.0%) to the Berserker - the totals (25.0% / 36.3%) do not change. Guiding
Light changes where the heal lands, not how much (budget unchanged). Phase Step at full strength vs Follow 80-100%: at most +20% of one
dome, paid for by -2 s and losing a modifier slot.

## 4. Questions for Skyy

None of these is already in OPEN-QUESTIONS.md (the 2026-10-08 class tree lines there are about the 13 build-map defaults and builder choices).

| # | Question | Recommended default |
|---|---|---|
| 1 | Mana Barrier "Follow" in the skill tree: the Mage Riftwalker node **Phase Step** becomes the dome-follows-you upgrade (full strength, blocks the Follow modifier), and the Follow modifier stays for every other Mage? | [yes - Phase Step] |
| 2 | Priest **Radiant Pulse** copied Sacred Heal's new Echo. Replace it with **Guiding Light** (aim Sacred Heal at an ally within 20 blocks; cast 0.5 s slower)? | [yes - Guiding Light] |
| 3 | Berserker **Shared Fury** copied the Banner's "kills extend it". Change it to a **rage swap** (the ally you look at gets your doubled Enrage, you get theirs; cooldown +3 s)? | [yes - rage swap] |
| 4 | **War Horn**'s second call 3 s after Enrage starts picks up late arrivals - fine next to "picked once at activation" (it is a path choice, not an aura)? | [yes, keep] |

## 5. For the local session

| # | Item |
|---|---|
| 1 | research/cloud/Class-Tree-Build-Map.md section 9: three text changes in `CPATHS` (Mage PA3, Priest PA2 name + text, Berserker PA2) for the next SkyyTrees patch; ids / kind K / AP / gates unchanged, no migration (nobody owns waiting nodes). Wait for Skyy's answers or ship the defaults. |
| 2 | Ability builder (later): `Class.Mage.PA3` = dome follows at 100% + Follow modifier blocked on Mana Barrier (an exclusive rule like Floor + Duration+); `Class.Priest.PA2` = look-at target for Sacred Heal; `Class.Berserker.PA2` = swap self / ally Enrage values for one looked-at party member. **UNVERIFIED**: a placed dome entity that follows a player (already listed in research/cloud/Modifier-Pool-Spec.md section 7 row 7). |
| 3 | Check: the 2026-10-08 00:34 log line says SkyyArmory 0.1.9 reads 12 nodes incl. Monk Hard Knuckles, but `ArmoryTree.KEYS` in `SkyyArmory/build_skyyarmory_0.1.9.py` lists 11 (no `Class.Monk.PB1`), so Hard Knuckles may still show "Coming with SkyyArmory" in game (maybe on purpose: the power-hit filter was UNVERIFIED). |
| 4 | research/cloud/Ability-Refresh-1007.md section 5 row 2 and research/cloud/Class-Ability-Spec-Draft.md "For the local session" row 8 can be closed (this file). |
