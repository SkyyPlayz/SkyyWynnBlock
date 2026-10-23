# Wynn elements - spec review, rewritten for "what is still useful now" (cloud draft, 2026-10-23)

The original task (review `research/Wynn-Elements-Build-Spec.md` against `research/cloud/Element-System-Spec.md` before building) is
mostly OBSOLETE: elements shipped on 2026-10-23. This file keeps only what is still useful: spec vs shipped, open gaps, what is left.
Nothing here was checked against game files or built jars (cloud); shipped facts come from `docs/log/2026-10.md` and `RESUME.md`.

## Decisions followed

- `docs/answered/gear.md` 2026-10-18 ELEMENTS Q1-Q10 (Imbue out of combat; charms weak to powerful; pets carry elements, bonus only if the weapon has that element; Defence ON now; mob table +25 / -25 / boss -50; reactions later as tree nodes; plate shows the mob's OWN element; Poison like Wynn 50/10s, stacks, never staggers; elemental swords after elements ship; Powders spec next).
- `docs/answered/gear.md` 2026-10-18 ELEMENTS FIRST (before the big UT batch) and 2026-10-22 UT BANDS (move to zone end).
- `docs/answered/classes.md` 2026-10-17 IMBUE ALL 5 ELEMENTS and ELEMENT NAMES (Wynn names; Gravity = Earth).
- `docs/answered/gear.md` 2026-10-08 (elemental weapons shelved until our element system) - superseded by Q9 above, now done.
- `docs/answered/pets.md` 2026-10-18 DRAGON PET DESIGN and 2026-10-22 NESTKEEPER (element dragons allowed).

## 1. Spec vs shipped

| Spec step (`research/Wynn-Elements-Build-Spec.md` section 11) | Planned | Shipped | Status |
|---|---|---|---|
| B1 SkyyMobs element table + plates | 0.1.11 | 0.1.17 | DONE |
| B2 SkyyGear formula, Defence, Poison, popups | 0.3.27 | 0.3.39 (also UT bands migrate39) | DONE |
| B3 SkyyClasses Imbue names + DoT bridge | 0.1.39 | 0.1.46 | DONE |
| B4 SkyyPets pet elements | 0.4.4 | 0.4.10 | DONE |
| B5 SkyyAccessories element + Prism charms | 0.5.27 | 0.5.32 | DONE |
| B6 SkyyMenu charts | 0.3.40 | 0.3.45 (Elements / Strong-weak / Reactions charts) | DONE |
| Elemental swords (Q9) | not in spec | Gear 0.3.40 | DONE |
| Elemental dragons | not in spec | Pets 0.4.11 / 0.4.12, Mobs 0.1.18 | DONE (D1); riding D3 waits |

Version numbers moved because other rounds landed first; the build-order risk the spec flagged (wave 1 together, wave 2 later) turned out
moot: all six mods shipped in one round (elem1), smoke PASS 41 ready, 0 SEVERE.

## 2. Contradictions and gaps found

| # | Issue | Where | Suggested fix |
|---|---|---|---|
| G1 | The spec's own Questions Q1-Q10 (popup style, "49 Fire" word, ticks white, mob share 30 %, charm ladder, Poison max 20, plate suffix, charts location, Yeti override) have NO answer line in `docs/answered/gear.md` (only the earlier Wynn-Elements-Spec Q1-Q10 are recorded). The build used the bracket defaults silently. | `research/Wynn-Elements-Build-Spec.md` line 326 | Record "defaults used" in `docs/answered/gear.md` so no agent re-asks; ask Skyy only Q1 / Q7 / Q10 after the feel test. |
| G2 | Two spec files disagree on build size: `research/cloud/Element-System-Spec.md` section 12 plans small separate versions; the build spec merges to one 6-mod wave. The build spec wins (newest, shipped). | both | Mark `research/cloud/Element-System-Spec.md` "superseded by the build spec" at the top. |
| G3 | `research/cloud/Element-System-Spec.md` section 7 says reactions "NONE at launch"; Skyy Q6 says "later, as tree nodes". The shipped Menu has a Reactions CHART but no reaction mechanic. Consistent, but players may expect reactions to work. | Menu 0.3.45 | Label the chart "planned" until the tree nodes exist. |
| G4 | No element numbers appear in `research/balance/*.md` tables (grep of combat / targets / gear / xp: only Imbue and `ab.Elements.numbers`). The balance goals were never checked for mob element share 30 %, Defence scale 100, charm ladder 2/4/7/11/16 damage, Poison max 20. The build ran `--elem --p9 --check` 58 / 0 (a model check), but the numbers are not in the published balance tables. | `research/balance/targets.md` | Next balance run writes the `elem.*` rows into the tables (run `python tools/balance_model.py --elem --check`, local). |
| G5 | Poison: Skyy's example is 50 damage / 10 s on ONE item; spec caps a line at 20 (Q7 default), so 50/10 needs weapon + armor stacking. Skyy said it "all stacks", so consistent, but the gap to the quoted number is unchecked. | spec 3.5, Q7 | Keep 20; confirm the top-end stack reaches ~50 in the feel test. |
| G6 | Elemental swords are +8 % element / +20 % Poison flat, not tiered by zone (Z2-Z5 drops). The balance goals use tier-scaled numbers elsewhere. | Gear 0.3.40 log line | Check the four swords against the zone ladder in `research/balance/gear.md`. |
| G7 | Powders (Q10 "next spec") has no spec file and is only a later-list line in `RESUME.md`. | `RESUME.md` item 4 | Queue a Powders spec (planned, not yet written) (Sonnet draft) - see order below. |
| G8 | Tier tags: element charms and Prism charms are new tiered items; confirm they are in `tools/tier_tags.py` (rule: every tiered item). | PROJECT-RULES 4 | `python tools/ci/lint.py` already passed 0 fails, so likely fine; low risk. |

## 3. Remaining build order (what is actually left)

| Order | Item | Needs | Risk |
|---|---|---|---|
| 1 | Skyy feel test of TEST-CHECKLIST 233 + 234 (coloured numbers, plates, Poison, charms, swords) | Skyy | decides Q1 / Q2 / Q3 / Q8 defaults |
| 2 | Record G1 defaults in `docs/answered/gear.md` | docs only | none |
| 3 | a Powders spec (planned, not yet written) (Wynn-style gem slots with element powders) | cloud draft | must not clash with element charms (4 power sources rule) |
| 4 | UT design batch (12 armor sets + 32 weapons) now using elements | Powders + UT bands done | big; full round |
| 5 | Reactions as class-tree nodes (Wildfire, Shatter ...) | trees map (SkyyTrees 0.5.0) | ability-hit element path must tag causes first |
| 6 | Coloured Burn / Poison ticks (Q3) | probe P3 result | extra Damage path |

## Questions for Skyy

| # | Question | Recommended default |
|---|---|---|
| 1 | Keep the build spec's Q1-Q10 defaults as final (Wynn-style popups when they worked, word "Fire", mob share 30 %, Poison line max 20, plate suffix, charts under Skills, Yeti weak to Fire)? | Yes; change only after the feel test |
| 2 | Should the Reactions chart say "coming later" until reaction tree nodes exist? | Yes |
| 3 | Write the Powders spec next (before the UT batch)? | Yes, cloud Sonnet draft |

## For the local session (UNVERIFIED, needs game files / jars)

- Whether the shipped coloured per-element popups (probe P1) and the plate marker (suffix vs line above, P2) behaved as the spec assumed - read the 10-23 game logs (skill `skywynn-logs`).
- Whether Poison ticks flinch mobs (P3) and whether `classes:fn:dot` hits player victims (PvP).
- `python tools/balance_model.py --elem --check` output vs the numbers in section 2 G4/G5/G6; the sword stats against `research/balance/gear.md`.
- Element charms and Prism charms present in `tools/tier_tags.py`.
