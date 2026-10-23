# Balance targets refresh notes - what is stale in `research/balance/targets.md`

Cloud draft, 2026-10-23. Paper only; the model was NOT run and `research/balance/targets.md` was not changed (it is generated: never hand-edit).
Read: `research/balance/targets.md` (all 554 lines), `tools/balance_model.py` (docstring, the P9 LIVE constants at lines ~118-165, the section writers,
`__main__` flag branches around lines 3225-3305), `research/Balance-P9-Check.md`, `RESUME.md`, `docs/log/2026-10.md` (10-22 P8 / P9 lines), `docs/answered/skills.md`
(2026-10-22 P9 FIXES line). Where the model was run and which section it writes decides everything below.

## Decisions followed (word for word in `docs/answered/`)

| Date | Skyy's words (short) | Used for |
|---|---|---|
| 2026-10-22 (`skills.md`) | P9 FIXES: "Apply all 3 (Recommended)"; first run "~36 h is fine (Recommended)" | live numbers the refresh must show (fixes F1 - F4 are LIVE in SkyySkills 0.4.62) |
| 2026-10-22 | DECISIONS P9: F1-F4 apply, F5 Mana feel-test first, F6 ~36 h fine | the one goal that may still read "waiting" is F5 (casters dry 28-40 s) |
| 2026-10-20 (A:197) | "Middle: Lv 50 at ~33 h" -> levels.scale 120 % | the fixed yardstick; do not change |
| 2026-10-18 / 10-21 | coins x10 targets 100k / 5M / 100M | section 3 yardstick, unchanged |

## 1. How the file is built (so the refresh is done in the right order)

| Command | Writes | Notes |
|---|---|---|
| `python tools/balance_model.py --md` | the WHOLE file: header + Assumptions + sections 1-5c + "Fixed targets" + "Top 10 gaps" + "Answered" + section 6 (P4) + section 7 (P5) + section 8 (P6) | OVERWRITES the file: **sections 9 (P7) and 10 (P9) are NOT in this writer** (code: `body + p4_md() + p5_md() + p6_md()`), so they vanish until their flags are run again |
| `--combat`/`--power`/`--gather`/`--econ`/`--p9 --md` | only their own section (6 / 7 / 8 / 9 / 10; each replaces or appends its own `### N.` block) | line endings kept |
| `--p9 --check`, `--p9 --fixes`, `--elem` | nothing | read-only; `--elem` = Wynn elements ON (58 / 0 per the 10-23 log) |

So "re-run `--p9`" alone refreshes ONLY section 10. The older sections 1-5 need `--md`; the right full order is below (section 5).

## 2. Section by section: what is stale and why

Current live state used as the yardstick: SkyySkills 0.4.62 (P9 fixes: `beast.xpFactor` 1.5, `mining.xpMultiplier` 1, `fell.otherLogsPercent` 100, `catchup.max` 20 %,
levels x1.5 for Lv 61-80 and x1.9 for Lv 81-100, `rebirth.pastLifeXp` 1.1 / 1.52 / 2.05 / 3.35 / 4.92 / 2.92 ... 3.67), P7 coin curve + prices, P8 trees, Wynn elements (Gear 0.3.39).

| Section | Written by | Pre-P9? | What is stale | What the re-run must change |
|---|---|---|---|---|
| Header + Assumptions | `--md` | yes | says "Run 1 ... P3 numbers"; the Assumptions list "Catch-up 10 % a level past 5 behind, <= +100 %" and the past-life list "[1.1, 1.35, 1.6, 2, 2.45]" are P3-era; the `tools/balance_model.py` module docstring still says "levels.scale 130 %" while the code and Skyy's answer are 120 | catch-up max 20 %; past-life list = the live 10-value list; Mining/felled-log notes; docstring 130 -> 120 (small code fix in the next model edit - not part of the doc) |
| 1 Class level vs hours | `--md` | yes (P3 curve) | levels 61-100 use the P3 list (no x1.5 / x1.9); Zones 4 / 5 "rebirth runs (cap)" rows | Zone 4 / 5 hour targets still ~12-16 / 15-20; model rows must show 14.2 / 16.7 h (P9 with fixes) instead of 9.4 / 8.7 |
| 1b Level at hour | `--md` | yes | skill columns come from the old split; Mining no longer runs ahead (x1.25 gone), Foraging no longer 10+ behind (logs 100 %) | the Foraging / Farming columns rise; Mining trails by 3-5 again |
| 1c Kinds of player | `--md` | yes | catch-up on / off rows were built for +100 %; at 20 % the on / off gap shrinks (fighter-first no longer ~20 % faster) | rows converge: "on" ~ "off" within ~8 % |
| 2 XP per hour needed | `--md` | yes | the Foraging "!! x0.51 / 0.63 / 0.77 / 0.76" and Farming "!! x0.70" gaps are pre-fix; Zones 4-5 XP/h use cheaper P3 levels | gaps fall (Foraging felled logs x1.37 vs 0.73); Zones 4-5 "XP/h needed" rises with the x1.5 / x1.9 levels |
| 3 Coins | `--md` | partly | "Today at zone end" Zone 3 = 1.8M is the ONE number that disagrees with the P7 / P9 check (sim 1.7M at Lv 50 vs 2.9M for 80-87 % of the target; x1.01 at zone end) - Economy-Sinks-Survey already flagged it | after the refresh the Zone 3 row should agree with section 10's "Coin targets x10 ... x1.03 / 1.04 / 1.01 / 1.01 / 0.99" |
| 4 Drops, collections | `--md` | yes | collection tier II / V times predate Collections 0.2.31 (shorter S / B / R / E curves, 10-22); the line "Longest stretch without any level-up: 1.56 h !!" is pre-fix | tier times shift; the longest-stretch row should read <= 1 h (fighter) / the P9 p90 numbers |
| 5a Void Particle arms | `--md` | no (PROPOSED strengths) | unchanged unless T3 arms changed | check the 5a ranks vs the live rebirth tree (P8d) |
| 5b / 5c Rebirths 1-5 | `--md` | yes | 5c "Past-life boost [1.1, 1.35, 1.6, 2.0, 2.45]" and its hours are the old list; live is 1.1 / 1.52 / 2.05 / 3.35 / 4.92 (rebirth 1-5) | new boost values and shorter / longer "with boost" hours; the "-15 % each" target should still pass (P9 row: 1.00 / 0.99 / 1.01 / 1.00 / 1.00) |
| Fixed targets / Top 10 gaps / Answered | `--md` | yes | the Top 10 list is the P3 gap list; most of its entries are fixed | list shrinks to the real remaining gaps (expect: Fishing, Mana feel test) |
| 6 Combat (P4) | `--combat` (writer p4) | after P4 (10-21), before elements | rows built before Wynn elements (10-23 `--elem`); not touched by the secret dragons | re-run once so hit/TTK rows match Gear 0.3.39; element rows are in `--elem`, not in this section |
| 7 Power sources (P5) | `--power` | after P5 / P8 | pet rows list the 39 roster kinds + 5 dragons; the P8b mobs / P8d trees changes and the secret dragons (Secret-Dragons-Spec) add rows; "UT / Mythic meters" shifted by Mobs 0.1.15 (Spoils rows) | re-run after every pets / mobs / gear power change |
| 8 Gathering + crafting (P6) | `--gather` | after P6b (10-22) | 0.3.36 tier-up / armor costs are in; Heartwood left for P9; Fortune stacking rows | re-run only if P6 numbers changed since 10-22 (none known) |
| 9 Economy (P7) | `--econ` | after P7 / P7b | LIVE as of 10-22; death 5 %, merchants; no Wardrobe / Tab rows (see `research/cloud/Wardrobe-Coin-Prices.md`) | add a cosmetic-share line when Wardrobe prices ship |
| **10 Whole first run (P9)** | `--p9 --md` | **written BEFORE the fixes** | the table and the goal rows still show the 10-22 pre-fix state: "Run done h: 60.0 / 28.8 / 60.0", Beastmastery 43-45, "never by 60 h", 9 failing rows (F1 - F6), and the line "Live numbers (P9 LIVE corrections: Mining XP x1.25, felled logs 70 % = x0.73 a log ...)". Since SkyySkills 0.4.62 the model constants are `MINING_XP_X = 1.0`, `FELL_OTHER_PCT = 100.0` (model lines ~155-156) | the biggest change: run done ~36 h (even), Beastmastery reaches 50, Zone 4 / 5 hours up, goals 35 pass / 0 fail (RESUME and the 10-22 log say `--p9 --check` 35 / 0; the caster-Mana row F5 stays a "waiting for the feel test" case); the header sentence must list the NEW live corrections (beast 1.5, catch-up 20 %, levels x1.5 / x1.9, past-life list) |

UNVERIFIED (not run here): whether `--md` already runs with the LIVE corrections (module flag `LIVE = "--p3" not in sys.argv` suggests yes, the file header says "always the P3
numbers"); the exact rows that move. The first run after the refresh decides; compare before / after with `git diff`.

## 3. What the `--p9` re-run must change (checklist)

1. Table "Whole first run": even player done ~36 h (not 60), gatherer-first done by ~60 h (not "never"), fighter-first ~29 h; Beastmastery at cap / done 50 / 50.
2. Goal rows: F1 (level-up gap), F2 (skills trail 3-5), F3 (even easier), F4 (Zone 4 / 5 hours), the Beastmastery pace row all flip to yes; F6 (first rebirth 40-50 h) is the accepted "~36 h is fine" - the row should read as accepted, not as a failure (a model change: move it to the "report, Skyy's choice" group like F7).
3. Zone 4 / Zone 5 first-time hours: 9.4 / 8.7 -> 14.2 / 16.7.
4. Header text: replace the stale P9 LIVE list with the current one (mining x1, logs 100 %, beast 1.5, catch-up 20 %, levels x1.5 / x1.9, past-life 10 values).
5. Totals line: `--p9 --check` exits 0 with 35 goals (or 36 if the elements goal block is added); `--elem --p9 --check` 58 / 0 stays a separate read-only check.

## 4. Questions for Skyy (defaults)

| # | Question | Default |
|---|---|---|
| 1 | Refresh `research/balance/targets.md` now (a local lean job: run the commands in section 5, commit the diff)? | [yes, no Skyy input needed] |
| 2 | Show the accepted "~36 h first run" as OK instead of a failing goal F6? | [yes, it was accepted 10-22] |
| 3 | Add the Wynn element rows (`--elem`) to targets.md as their own section 11 so they stop being a console-only check? | [yes] |

## 5. For the local session (UNVERIFIED - needs Python + the repo; no game files)

Run from the repo root, one at a time (each flag overwrites its own section; `--md` overwrites the whole file):

```
python tools/balance_model.py --md
python tools/balance_model.py --combat
python tools/balance_model.py --power
python tools/balance_model.py --gather
python tools/balance_model.py --econ
python tools/balance_model.py --p9 --md
python tools/balance_model.py --p9 --check
python tools/balance_model.py --elem --p9 --check
git diff --stat research/balance/targets.md
```

| # | Check |
|---|---|
| 1 | `--md` keeps the file's line endings (the writer uses `\n`; other section writers keep CRLF if present - mixed endings are intended, `.gitattributes` keeps bytes; do not convert) |
| 2 | `--md` drops sections 9 / 10 (they are re-added by `--econ` / `--p9 --md`; the section order may change - appended sections go to the end) - check the order afterwards |
| 3 | Whether `--combat` / `--power` / `--gather` flags are the exact names (the module docstring lists `--power --gather --econ --p9`; the `--combat` branch is at line ~3272) |
| 4 | After the refresh run `python tools/docs_check.py` (OK) and update `research/balance/README.md` / `INDEX.md` if the section list changed |
| 5 | Fix the module docstring "levels.scale 130 %" -> 120 % in the next edit of `tools/balance_model.py` (not a docs-only change; cloud sessions never edit build scripts) |
| 6 | After the secret dragons (Secret-Dragons-Spec) and the Wardrobe prices, re-run `--power` and `--econ` once more |
