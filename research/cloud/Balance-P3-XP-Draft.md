# Balance P3 XP curves - draft re-check (2026-10-23)

Verdict: the original task is MOSTLY OBSOLETE. P3 was built (research/Balance-P3-XP-Spec.md), and the P9 whole-run check found the leftover
XP gaps and fixed them (SkyySkills 0.4.62, deployed 2026-10-22 19:08, TEST-CHECKLIST 230). What is still useful: a status table, two small
leftovers, and what to confirm in game. No new curve is proposed.

## Decisions followed

- docs/answered/skills.md R1 LOCKED: class skill curve 50 x L + 0.25 x L^3 (now folded into the one P3 curve; "never below today at any level").
- docs/answered/skills.md 2026-10-04 / 10-05 LOCKED: Mining own level list (the cost rises, the XP per block never shrinks); Cooking "the easier
  to craft the less xp"; Flour way down.
- docs/answered/skills.md 2026-10-02 LOCKED: Cooking XP x0.5 ("cooking levels really fast"), kill XP gap rule.
- docs/answered/skills.md A:185-A:197 (balance goals): Zone hours 12 / 14 / 14, skills trail the class by 3-5 levels, Lv 50 first-run cap at
  ~33 h ("Middle: Lv 50 at ~33 h" -> levels.scale 120 %).
- docs/answered/project.md 2026-10-20 "RECOMMENDED ON ALL" and "DEFAULTS WHILE AWAY": open P3-P9 questions took the recommended default.
- docs/log/2026-10.md 2026-10-22 16:00: "DECISIONS P9: F1-F4 apply (Skills round), F5 Mana feel-test first, F6 ~36 h first run is fine."
- docs/log/2026-10.md 2026-10-18: level cap 50 first run, +10 a rebirth (100 at rebirth 5); keep levels on migration (P3 spec section 6).

## Are the original findings fixed?

| Original finding | Fixed by | Status now |
|---|---|---|
| Foraging curve too slow (Zone 1 needs 25k XP/h, had ~11k; 11 levels behind class at 30 h) | P3 XP per action (log 33 x tier factor); P9 F2: felled logs 70 % -> 100 %, Mining x1.25 -> x1 | Fixed on paper (P9 model: every skill 3-7 behind). NOT yet felt in game. |
| Cooking too slow | Never slow: 101k vs 85k needed. It was too FAST (Skyy's own tests) and was already cut | Fine. Watch only top pies (up to 2.07 x target, SkyyCooking 0.1.16 note). |
| Alchemy too slow | P3 alchemy.tierXp [1500, 7400, 18200, 33900, 54400]; model 60k vs 85k Zone 1, ok Zones 2-5 | Zone 1 still ~x0.83 (small). See leftover A. |
| Class XP too fast early | Not a real gap in the model: class Lv 20 at 12.5 h vs 12 h target, Lv 40 at 26.2 h vs 26 h. Early levels use the quick start (first 4 levels cheap) | Fixed / within +-15 %. Confirm by feel (Lv 2 in ~8 min). |
| Past-life XP discount (rebirth) | Built as a past-life XP BOOST (not a cheaper curve). P9 F4: 1.1, 1.52, 2.05, 3.35, 4.92 then 2.92 .. 3.67 | Done. Rebirth runs shrink ~15 % each (model ratios 1.00 / 0.99 / 1.01 / 1.00 / 1.00). |
| Level-up gap > 1 h | P9 F1 beast.xpFactor 1.5, F3 catchup.max 100 -> 20 | Model with fixes: 0.52 / 0.42 / 0.52 h. Live check 35 pass / 0 fail. |

## What is still open (vs targets)

| Gap | Target | Model (live P9) | Note |
|---|---|---|---|
| First run length | first rebirth 40-50 h | ~36 h with fixes (original unfixed: never by 60 h) | Skyy accepted ~36 h (P9 F6). Not a bug. |
| Zone 4 / Zone 5 first-time levels | 12-16 h / 15-20 h | 14.2 h / 16.7 h with F4 | Inside target. |
| Caster Mana dry time with half the stack | 20-30 s | 28-40 s | P9 F5: waits for Skyy's feel test. Not an XP item. |
| Cap stretch (hours 33 to 40+) | a level-up or gear upgrade each hour | even-player level-up gap p90 now ~0.5 h | Fine if the fixes hold in game. |

### Leftover A - research/balance/targets.md sections 1 / 1b / 2 look stale
Sections 1-2 still print the pre-P9 P3 numbers (for example "Foraging !! x0.51", "Farming !! x0.70"). Section 10 and research/Balance-P9-Check.md
hold the live numbers. Suggest: run `python tools/balance_model.py --p9 --check` (rewrites the file) so a reader is not misled. Needs the
repo only (no game files), but it REWRITES research/balance/targets.md, so this is a local-session job, not a cloud edit.

### Leftover B - Alchemy Zone 1 (levels 1-15) runs ~17 % under target
60k XP/h vs 85k needed. Everything after Zone 1 is ok. Proposal (small, one Server Setup row set, no code):

| Row | Today | Proposed | Effect (model, UNVERIFIED) |
|---|---|---|---|
| alchemy.tierXp tier 1 | 1500 | 1900 (+25 %) | Zone 1 ~75k XP/h (x0.88-0.95 with the real potion mix) |
| alchemy.tierXp tiers 2-5 | 7400 / 18200 / 33900 / 54400 | unchanged | Zones 2-5 stay ok |

Only do this if Skyy's Alchemy feel test says the first levels drag. Tier-1 potions are early; the one-time-migration rule applies (only rewrite
lines still on the old default; PROJECT-RULES section 4).

## Proposal table vs targets (no change to the curve)

| Item | Keep / change | Reason |
|---|---|---|
| One curve R(1100 x f(L) x s(L)) x levels.scale 120 % (Lv 20 = 69,780 XP, Lv 50 = 487,440) | Keep | Hits Zone 1-3 hours inside +-5 %. |
| XP per action ore 50 / log 33 / crop 38 / dish 800 x tier factor | Keep | P9 F2 already evened Mining and Foraging. |
| Catch-up +10 % a level past 5 behind, max +20 % | Keep (P9 F3) | Even player no more than 8 % slower than a focused one. |
| Past-life boost 1.1 .. 4.92, then 2.92 .. 3.67 | Keep (P9 F4) | Rebirth runs -15 % each. |
| Alchemy tier 1 XP +25 % | Optional, after a feel test | Leftover B. |
| Foraging felled logs 100 % | Keep, watch | If trees feel too generous, set fell.otherLogsPercent 85 (a row, no build). |

## Questions for Skyy

1. **Alchemy early levels:** do Alchemy levels 1-15 feel slow in your test? [Default: do nothing until you say so; if yes, raise tier-1 Alchemy XP +25 %.]
2. **Foraging pace:** after P9 (felled logs 100 %, Mining x1), does Foraging keep up with the class (3-7 levels behind)? [Default: yes, no change; if it still lags, raise the log base 33 -> 38.]
3. **Refresh the targets file:** OK to re-run `python tools/balance_model.py --p9 --check` so research/balance/targets.md sections 1 and 2 show the live numbers? [Default: yes, next local session.]

## For the local session (UNVERIFIED, needs the live set / game)

- UNVERIFIED: that SkyySkills 0.4.62 really holds beast.xpFactor 1.5, catchup.max 20, mining.xpMultiplier 1, fell.otherLogsPercent 100 in
  the live config (read Server Setup -> Skills; the P9 log says deployed).
- UNVERIFIED: the Alchemy Zone 1 number (60k) came from the model with GUESS time splits (Alchemy 4 % of play time), not a measured run.
- UNVERIFIED: actual pace in game: Foraging vs class at 10 / 20 / 30 h, quick-start Lv 2 time, the CurveP9Mig keep-levels result on
  existing profiles (TEST-CHECKLIST 230).
- Run `python tools/balance_model.py --p9 --check` and compare with Section 10 of research/balance/targets.md (35 pass / 0 fail expected).
