# Balance pass P8 - Rebirth: Void Particles, Nexus, keep buff, rebirths past 5, the skill trees (BUILD-READY spec, 2026-10-21)

Phase P8 of research/Balance-Pass-Spec.md section 8: "Rebirth: Void Particles, Nexus upgrades, keep buff, rebirths past 5 default, skill
trees for the skills (Skill-Trees-3 R3-R4)". Mods: SkyyRebirth, SkyySkills, SkyyTrees (+ SkyyClasses, SkyyMobs, SkyyPets for tree rows
whose effect those mods own). The rule from section 8: "rebirth speed-up is measured against the finished first run".
Skyy 2026-10-21: "keep going down the list. dont stop until the entire list is done" + "just go with the recommended on all of them. i need
to go to bed." + "run whatever you can in parallel to speed up the build". Spec only - nothing built, nothing committed. Where answers go:
docs/answered/skills.md (rebirth + tree lines); this file holds the plan (the main session adds it to INDEX.md under research/).
**Trees changes are based on SkyyTrees 0.4.5** (the P5 round building now: TreeMigP5, Rich Seams 2.5 a rank, the Mining Fortune budget).

**Goals used (Skyy's words):**
- "first rebirth after like 40-50 hours of gameplay. then each rebirth after that gets a little shorter" (docs/answered/skills.md:185) +
  Q3 "15% shorter each (Rec.)" (skills.md:187) + "Middle: Lv 50 at ~33 h" (skills.md:197).
- Level cap "Start 50, +10 each" -> 100 at rebirth 5 (skills.md:174); "allow rebirths past 5 so you can keep upgrading. but leave the lvl cap
  at 100 for now till we add more zones." (skills.md:193).
- Skill-Trees-3 answers (skills.md:193, research/Skill-Trees-3-Spec.md end): "Respec costs a Void Charm", "Yes, stronger" (VP ranks so each
  rebirth is ~15 % shorter), "Flat +0.25% each" (every unspent VP +0.25 % all XP, **no cap**; re-run the spend vs keep math), "One shared VP",
  "Coins, rising + 1 free/rebirth", "1 point after 25" (capstone), "Total points in tree", "2 branches x 4 rows" (light skills).
- Void Particles from total XP earned this run, past max level counts with a small bonus; nodes "start cheap ... quickly get expensive"
  (docs/answered/economy.md:154).
- No dev gates (economy.md:147: "turn it on ... dont gate anything for 'Other players'"); Beastmastery = a skill that "levels up from leveling
  pets" (skills.md:164); four power sources (PROJECT-RULES 4).

**Legend.** VERIFIED = read in code / live config (cited). DERIVED = the scratch model (tools/dev/scratch/p8spec/p8model.py on a copy of
tools/balance_model.py, deleted after; its functions are in Appendix A for the builder to port, section 7.7). PROPOSED = a default this spec
picks. UNVERIFIED = needs the game or a closer code read. W = checked on the web 2026-10-21, K = my knowledge, not checked.

---

## 0. For Skyy (plain words)

1. **Rebirth is already on and almost on target.** With today's numbers a player who spends Void Particles well gets each rebirth about
   6-9 % *faster* than "15 % shorter each" for rebirths 1-5. P8 lowers the past-life XP boost a little so the times land on the goal.
2. **Rebirths 6-8 were the big miss: 16-24 % too fast.** From rebirth 6 the cap stays 100, so there are no new levels to climb, and the full
   past-life boost made the run far too short. P8 gives the boost its own number for rebirths 6-10 (lower first, then rising again).
3. **The goal table, measured against the finished first run (45 h, class Lv 50 at ~33 h):** rebirth 1 = 38 h (class cap at 28 h),
   2 = 32.5 h, 3 = 27.6 h, 4 = 23.5 h, 5 = 20 h (Lv 100), 6 = 17 h, 7 = 14.4 h, 8 = 12.3 h, 9 = 10.4 h, 10 = 8.9 h (class cap at 6.5 h).
4. **A hidden cap was there:** class XP from rebirth (Insight + keep + Class Echo) stopped at +200 % in SkyySkills. So from rebirth 9 the
   keep buff did nothing more for your class. You said "no cap", so P8 lifts it to the same +500 % the skills already use.
5. **Past rebirth 10 runs keep getting shorter, just slower** (about 8-10 % a rebirth, because only the keep buff still grows). They flatten
   out at about 3.7 h to Lv 100 around rebirth 17 (the +500 % XP limit). A server owner can set a "fastest rebirth" ceiling in Server Setup
   (off by default).
6. **Spend or keep is a real choice:** the best mix hits the goal. Keeping everything is 4-13 % slower. Buying every cheap rank is 11-21 %
   slower. Never touching the Nexus still works.
7. **Unlimited rebirths for real:** your world still has "max 10 rebirths" saved from an old version. P8 switches it to unlimited, but only
   where it is still that old default.
8. **Skill trees (the rest of Skill-Trees-3 R3):** about 290 skill upgrades still say "coming soon". P8 wires them like the class trees were
   wired (R3a). Upgrades that cannot work in Hytale get the nearest working effect and honest text. Mining, Foraging and Combat come first.
   Then Beastmastery gets a real skill, which levels from pet XP. The useful and light trees come last. Active skills (Flurry, Shield Wall,
   Pollen Cloud ...) and capstones that need new systems stay "coming soon" for their own round.
9. **One thing for P9:** the tree XP upgrades you already have make run 1 about 4 h quicker than the model's 33 h. Both run 1 and every rebirth
   have them, so the rebirth ratios hold. P9 re-checks the 40-50 h first run.

---

## Research (short; W / K marked)

| Game | What it does | What we take |
|---|---|---|
| AdVenture Capitalist (W) | each Angel Investor gives +2 % profit while held; angel upgrades COST angels, which are gone for good; players spend only when the upgrade beats the lost bonus (the wiki's break-even rule) | our keep vs spend exactly: value per VP of a rank vs +0.25 % per held VP (section 2.2) |
| Cookie Clicker (W) | prestige level = +1 % CpS each, stacking additively, kept when you spend heavenly chips on the permanent tree | the opposite design (no dilemma); Skyy chose the AdCap kind ("balance how much you spend ... with how much you keep") |
| WoW Warband / heirloom catch-up (K) | big XP bonus only on content you have already done | the past-life boost (P3 section 5) only on levels below last run's cap |
| Diablo 3 seasons / Paragon (K) | each new run is much faster than the first; endless Paragon levels keep a small reward going after the cap | runs past rebirth 10 keep a small speed-up (the keep buff) instead of a hard stop |
| Incremental games in general (K) | each prestige layer is 10-20 % faster than the last, and a soft wall stops runs reaching zero | -15 % to rebirth 10, then the slower keep-only slope, then the existing +500 % limit as the wall |

Sources (W): https://adventure-capitalist.fandom.com/wiki/Angel_Upgrades , https://steamcommunity.com/app/346900/discussions/0/365172547955569702 ,
https://cookieclicker.wiki.gg/wiki/Prestige .

---

## Part 1 - Today (VERIFIED)

### 1.1 SkyyRebirth 0.4.1 (SkyyRebirth/build_skyyrebirth_0.4.1.py = REB; the VP system is 0.4.0, tools/rebirth_0_4_0_patch.py)

- **VP earned at rebirth n** (REB:44-48): `vp.base 20 + vp.perRebirth 10 x n + vp.perSkill 2 x (skills at cap, max 11) +
  floor(vp.overflow 12 x (sqrt(min(r, 16)) - 1))`, r = class run XP / XP to the class cap (r < 1 -> 0). Skills counted: Mining, Foraging,
  Farming (+ Ranching, Orchard pooled), Smithing, Alchemy, Fishing, Cooking.
- **Stored** per profile `Skyy_SkyyRebirth/players/<pkey>.properties`: `vp`, `vpSpent`, `vpEarned`, `node.<id>`, `v=4` (REB:41-43). VP <= 1e9.
- **Nexus (21 nodes, plain ladders, no row gate; REB:1404-1440, 611-620):** Void Insight +6/8/10/12/16 % all XP for 12/20/32/48/72 VP;
  Class Echo +4/5/7/9/11 % class XP for 4/6/10/16/24; Mining / Foraging / Combat / Beastmastery Echo +8/11/15/20/26 % for 4/6/10/16/24;
  6 Hand Echo nodes (Farming, Cooking, Alchemy, Fishing, Smithing, Acrobatics) on the Echo strengths/costs (they share one ladder -
  UNVERIFIED how exactly, section 7.8); Head Start +1 skill point a rank, 20/30/45 VP, 3 ranks; 8 Void-Forged tool nodes (+1 rebirth
  modifier level a rank, 4/6/10/16/24). **Everything costs 1,119 VP.** A node whose reader mod is missing shows "Coming with <Mod>".
- **Keep** (REB:60-62, 1576-1595): `nexus.keep` 0.25 % ALL XP per held VP, no cap. `allxp` = Insight + keep goes to every skill
  (`skill:bonus:<uuid>` source "rebirth", `xp.<skill>`) and to class XP through `rebirth:fn:stat "classxp"` (+ Class Echo).
- **Requirements** (REB:2500-2535): class level = class cap; rebirths < `rebirth.max` (**code default 0 = no limit since 0.3.6**, REB:123-126);
  not in combat; island or hub; no open Bazaar / AH orders (Continue closes them); unclaimed sale coins block.
- **Reset / kept** (REB:3982): skills (not Exploration), purse, bank, lifelong tools -> Crude, Mining armor -> Copper, every tree except
  Exploration (SkyyTrees `rebirth:part:trees`). Kept: Nexus ranks + VP, titles, cosmetics, class picks, the counter, pets' levels.
  `stat.perRebirth` 3 % all stats, `stat.cap` 30 (reached at rebirth 10).
- **Nexus respec:** costs `nexus.respecCharms` 1 Void Charm (lowest rarity first), refunds all spent VP; refused while a skill tree uses
  Head Start points (`tree:fn:headUsed` > 0).
- **Live world NewBetaTest** (read-only, `mods/Skyy_SkyyRebirth/config.properties`): `rebirth.on=true`, **`rebirth.max=10`** (the old 0.3.x
  default written into the file - so rebirths are still capped at 10 there), `caps.levels=10`, no `vp.*` / `nexus.*` lines (absent = code
  default), 0.3 leftovers `tree.*` / `dust.perNode` (dead keys). No `players/` folder yet: nobody has rebirthed on the test world.

### 1.2 SkyySkills 0.4.58 (= S58; the XP parts are from 0.4.57 / P3)

- Past-life boost `rebirth.pastLifeXp` = `1.2,1.45,1.8,2.25,2.8` (S58:5337, row S58:21674): XP into a rebirth-reset slot x entry n while
  that slot's level < the previous cap; past the list end = the last entry; rebirth 6+ = every level (prevCap = 100) (S58:13395-13414).
- Total: `P3Xp.mult` = skillMult x catch-up x past-life (S58:13429-13435), then `SkillBonus.boost` x (1 + b), b = tree + rebirth XP summed
  over sources, **clamped 0..5 (+500 %)** (S58:12236-12262).
- **Class XP rebirth part is clamped at +200 %**: `RbStat.fetch` z[3] = `clampPct(classxp)` with `MAXPCT = 200.0` (S58:8546, 8554-8557,
  11041-11050). MAXPCT is shared with the Health / Mana / Stamina % stats.
- Caps: `levels.runCap` 50, `levels.capMax` 100 -> 50/60/70/80/90/100, then 100 (S58:9390-9393, 9843). Catch-up on (+10 % a level past 5
  behind, <= +100 %).
- Live `xp.properties`: no `rebirth.pastLifeXp` line (= code default); `bridge.bonus.xpSkills=Mining,Foraging,Farming,Cooking`.

### 1.3 SkyyTrees 0.4.5 (= T45, building in the P5 round) + tools/trees_v3_data.py / trees_v3_effects.py

- 1 point a level (Combat = class level; Farming = the Farming average; **Beastmastery = 0 points until a Beastmastery skill exists**,
  T45:10312) + Head Start (`rebirth:fn:stat "headstart"`, <= 100). Row gate = total points in the tree; the built gate =
  `min(5 x (r - 1), hooked ranks in the rows below)` (TreeV3.GATES), so dead upgrades never block a row.
- **Free respec**: the first respec of a tree each run is free (`respec.<Tree>.free`), then `respec.perLevel` 100 x level x min(paid + 1,
  `respec.maxSteps` 5); a rebirth gives the free one back (`rbReset`, T45:10289-10350). = Skyy's "1 free per rebirth". Nothing to change.
- **Skill-tree upgrades live vs "coming soon"** (scratch count from the two tables; free row perks included): Mining 14 / 30, Foraging 11 /
  31, Combat 8 / 34, Beastmastery 0 / 40, Farming 9 / 31, Cooking 9 / 31, Alchemy 6 / 34, Fishing 5 / 12, Exploration 2 / 16, Acrobatics
  4 / 15, Smithing 5 / 14 -> **73 live, 288 coming soon.** All 8 class trees are fully wired (R3a).
- Tree XP rows already live: each skill's Wisdom row (+2 % a rank x 5 at row 5) + the "Pet <x>" rows (+2 % a rank x the pet's rarity bonus,
  <= x1.5) - up to ~+25 % XP per skill from about Lv 25 on; Combat Insight + Pet Fang the same for class XP.
- Budgets in trees_v3_effects.py: `TREE_FORT_MAX` 40 Fortune per skill (Mining is exactly 40.0 after P5), `ROW_FORT_MAX` 15.

### 1.4 What the model says about today (DERIVED, Appendix A, `--live`; greedy = the best spend/keep player; ratio = hours to the class
cap / target, target = run 1's 33.1 h x 0.85^n)

| Rebirth | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 12 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| greedy ratio | 0.94 | 0.93 | 0.92 | 0.91 | 0.91 | **0.76** | **0.80** | 0.84 | 0.93 | 1.09 | 1.51 | 2.47 |
| all-keep ratio | 1.03 | 1.04 | 1.03 | 1.01 | 1.00 | **0.82** | 0.86 | 0.90 | 0.95 | 1.09 | 1.51 | 2.47 |
| greedy h to class cap | 26.4 | 22.3 | 18.7 | 15.8 | 13.4 | 9.5 | 8.5 | 7.6 | 7.1 | 7.1 | 7.1 | 7.1 |

Why: (a) live VP income is higher than the P3 model assumed (48 / 58 / 68 / 77 / 87 VP for rebirths 1-5 vs the fixed 38-80 the P1/P3 tables
used - the overflow and 7 capped skills add ~10), so rebirths 1-5 run ~7 % fast; (b) rebirth 6 has no first-time levels (cap stays 100)
but keeps the full x2.8; (c) from rebirth 9 the class XP rebirth part hits the +200 % clamp, so class runs stop at 7.1 h whatever the keep is.
The P1/P3 tables 5b/5c in research/balance/targets.md use the fixed VP list - P8 replaces them (7.7).

---

## Part 2 - The rebirth curve (PROPOSED)

### 2.1 Targets (measured against the finished first run)

- Run 0 (first run): 45 h total, class Lv 50 at 33.1 h (the P3 model; levels.scale 120).
- **Rebirth n, n = 1..10: run = 45 h x 0.85^n, class cap at 33.1 h x 0.85^n.** Past rebirth 10: no hard target. Runs keep shrinking only by
  the keep buff (Skyy: no cap), down to the existing +500 % XP limit.

| Rebirth | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Cap | 60 | 70 | 80 | 90 | 100 | 100 | 100 | 100 | 100 | 100 |
| Whole run h | 38.3 | 32.5 | 27.6 | 23.5 | 20.0 | 17.0 | 14.4 | 12.3 | 10.4 | 8.9 |
| Class cap h | 28.2 | 23.9 | 20.4 | 17.3 | 14.7 | 12.5 | 10.6 | 9.0 | 7.7 | 6.5 |

### 2.2 The knobs and why only these move

- **Void Particle income: unchanged** (20 + 10 n + 2 / capped skill + overflow). It grows ~10 VP a rebirth (48 -> 145 at rebirth 10, DERIVED),
  so the keep buff and the Nexus get stronger every rebirth on their own.
- **Nexus ladders: unchanged** (Skyy picked "stronger" in 0.4.0). Spend vs keep, re-run as Skyy asked (answer 9), value of a rank in % all-XP
  per VP, time-weighted by the play split (balance_model SHARE: class 0.45, Mining 0.18, Foraging 0.15, Farming 0.10 ...), keep = 0.25:
  Insight 0.50 / 0.40 / 0.31 / 0.25 / 0.22; Class Echo 0.45 / 0.38 / 0.32 / 0.25 / 0.21; Mining Echo 0.36 / 0.33 / 0.27 / 0.23 / 0.20;
  Foraging Echo 0.30 / 0.28 / 0.23 ...; Hand (Farming) 0.20 ... So the best player buys **Insight 1-3, Class Echo 1-4, Mining Echo 1-3,
  Foraging Echo 1-2 (130 VP, done by rebirth 3)** and keeps everything else. The last ranks sit right at the keep value, which makes it a
  real choice: a Mining-focused player values Mining Echo ~2x higher and buys all of it. Tool and Head Start nodes are not XP. They are bought
  for gathering speed and points, and they count as "kept power".
- **Keep buff: unchanged, still no cap** (+0.25 % per held VP).
- **The class XP clamp: +200 % -> +500 %** (= the skills' limit; Skyy "no cap" - this hidden one cut the keep buff from rebirth 9 on).
- **The past-life boost list: retuned and extended to 10 entries** - the ONE pacing knob (it touches only replayed levels, P3 section 5).

### 2.3 New `rebirth.pastLifeXp` (PROPOSED; DERIVED by `tune_past()`, greedy player, then rounded)

`1.1,1.35,1.6,2,2.45,2.15,2.25,2.4,2.55,2.7` (today `1.2,1.45,1.8,2.25,2.8`; entry n = rebirth n; past the end = the last entry).
The dip at rebirth 6 is on purpose. Rebirth 5 still has 10 first-time levels (90-100, the dearest ones), rebirth 6 has none, and the keep
buff has grown by ~24 points. The Stats page shows the COMBINED rebirth XP (section 2.5), and that number does not drop (x4.9 at rebirth 5,
x4.8 at 6, then rising).

### 2.4 Proof (DERIVED; `p8model.py --noclamp --past <2.3>`; kept power = GUESS +6 % a rebirth, max +30 %)

| Rebirth | Cap | Past-life | Class x (VP bonus x kept) | VP total / spent / held | Keep | Class cap h | Target h | Ratio greedy | all-keep | buy-cheapest |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 60 | x1.10 | x1.31 | 48 / 46 / 2 | +0.5 % | 28.3 | 28.2 | **1.00** | 1.11 | 1.12 |
| 2 | 70 | x1.35 | x1.57 | 105 / 104 / 1 | +0.2 % | 23.7 | 23.9 | **0.99** | 1.10 | 1.11 |
| 3 | 80 | x1.60 | x1.88 | 172 / 130 / 42 | +10.5 % | 20.5 | 20.4 | **1.01** | 1.13 | 1.19 |
| 4 | 90 | x2.00 | x2.22 | 249 / 130 / 119 | +29.8 % | 17.2 | 17.3 | **1.00** | 1.10 | 1.15 |
| 5 | 100 | x2.45 | x2.60 | 335 / 130 / 205 | +51.2 % | 14.7 | 14.7 | **1.00** | 1.10 | 1.21 |
| 6 | 100 | x2.15 | x2.92 | 431 / 130 / 301 | +75.2 % | 12.4 | 12.5 | **0.99** | 1.08 | 1.18 |
| 7 | 100 | x2.25 | x3.26 | 537 / 130 / 407 | +101.8 % | 10.6 | 10.6 | **1.00** | 1.07 | 1.18 |
| 8 | 100 | x2.40 | x3.64 | 653 / 130 / 523 | +130.8 % | 8.9 | 9.0 | **0.99** | 1.06 | 1.15 |
| 9 | 100 | x2.55 | x4.05 | 779 / 130 / 649 | +162.2 % | 7.6 | 7.7 | **0.98** | 1.04 | 1.12 |
| 10 | 100 | x2.70 | x4.49 | 914 / 130 / 784 | +196.0 % | 6.4 | 6.5 | **0.99** | 1.04 | 1.11 |
| 12 | 100 | x2.70 | x5.46 | 1214 / 130 / 1084 | +271 % | 5.3 | (4.7) | - | - | - |
| 15 | 100 | x2.70 | x7.13 | 1727 / 130 / 1597 | +399 % | 4.1 | (2.9) | - | - | - |
| 17+ | 100 | x2.70 | x7.80 (limit) | 2097+ | +492 %+ | 3.7 | - | - | - | - |

- Every skill reaches the run's cap inside the run (Mining at cap at each run's end; catch-up on); 7 skills count for VP each run.
- **Too fast / too slow, where the stack bites (DERIVED):**
  - **Too fast (today):** rebirths 6-8 by 16-24 % (no new levels + full x2.8). Fixed by entries 6-8.
  - **Too slow (today):** rebirth 10+ class runs freeze at 7.1 h (the +200 % clamp). Fixed by the 500 % clamp.
  - **Past rebirth 10 (proposed):** runs shrink ~9 % a rebirth (keep only), slower than 15 %; class runs floor at 3.7 h from about
    rebirth 17, when the +500 % limit is hit. Skills hit the same limit a little later (their tree XP is in the same sum).
  - **Kept power is the big unknown.** With +0 % a rebirth (gear / shards / pets give nothing) the runs are 6-35 % too slow. With +10 % they
    are up to 9 % too fast for rebirths 2-4. Skyy's play-test sets it; the list is one Server Setup row.
  - **Pet echo / Beastmastery Echo** only touches pet XP (and the Beastmastery skill, Part 4). It is not in the class clock.
  - **Head Start** (+3 points at most) makes the tree XP rows come ~3 levels sooner. That is under 1 % of the run, not modelled.

### 2.5 Fastest-rebirth ceiling (PROPOSED, off by default)

New SkyySkills row `rebirth.xpMultMax` (decimal, 0 = off, 0-100). When > 0, in `SkillBonus.xpBonus` the REBIRTH part rb (source "rebirth" +
`RbStat.classXp`) is cut so that `pastLife x (1 + rb) <= xpMultMax` (rb' = xpMultMax / pastLife - 1, never below 0). The tree part of b is
not touched. The suggested value that freezes runs at rebirth 10 is **9.3** (DERIVED: 2.70 x 3.45). It goes in the row's help text, not the
default (Skyy: keep has no cap).
The Stats page line becomes "Rebirth XP x4.9 (past-life x2.45 below Lv 90, Void x2.0)". At the ceiling it adds "(at the server's fastest
rebirth)".

---

## Part 3 - Rebirths past 5, Void Particles, Nexus page, Head Start, respec

1. **Unlimited rebirths by default:** SkyyRebirth one-time migration `rebirth.max` `10` -> `0` only when the line is exactly `10` (the 0.3.x
   default); any other value is kept + one INFO line. The code default is 0 already (0.3.6). Row help: "0 = no limit".
2. **Caps:** unchanged (+10 a rebirth, clamp 100 in SkyySkills `levels.capMax`). Collection rank cap keeps +1 a rebirth with no clamp (ranks
   only give Enchanted items, skills.md:157) - Q6. `stat.perRebirth` 3 / `stat.cap` 30 = full at rebirth 10, the same point as the curve.
3. **VP income:** unchanged formula. The rebirth page hover on the Nexus shows the split ("This rebirth: 20 base + 60 rebirth 6 + 14 skills
   + 9 overflow = 103 VP") - UNVERIFIED whether 0.4.1 already shows it; if so, no change.
4. **Nexus page (SkyyRebirth 0.4.2):** the keep line also shows the class/skill limit ("Holding 784 VP: +196 % XP"); a node's hover shows
   "worth X % XP / VP vs keep 0.25" (Skill-Trees-3 6.5 "the dilemma shown") - UNVERIFIED if 0.4.0 has it; build only if missing.
   Dead Server Setup row `dust.first` (Dust is gone since Trees 0.4.0): hide the row (key still read, `rebirth:fn:dustmult` kept for old
   readers). Leave the dead `tree.*` / `dust.perNode` lines in the live file alone (no reader; rewriting them gains nothing).
5. **Head Start:** unchanged (3 ranks, +1 point each in every tree incl. class). 1 free tree respec per run: unchanged (VERIFIED 1.3).
6. **Nexus respec:** unchanged (1 Void Charm).
7. **Pets:** pet rebirths stay max 5 (`pets.rebirth.max`, Lv 100) - not part of "rebirths past 5" (that was the player's rebirth).

---

## Part 4 - The skill trees: finish Skill-Trees-3 R3 for the 11 skill trees (PROPOSED)

Same method as R3a did for the class trees (tools/trees_v3_data.py 4147-4176): every "(coming soon)" upgrade gets a hook, or else a NEW_TEXT
with the nearest server-side effect when the drafted mechanic cannot work in Hytale. A row stays "coming soon" only when it needs a system
that does not exist yet. ONE table (trees_v3_data.py: `hook` on the upgrade / trees_v3_effects.py `EFFECTS` rows for other appliers); one
skill per commit; the generator re-computes `TreeV3.GATES` (rows rise toward 0/5/10/15/20/25 as ranks get hooked).

### 4.1 Rules

- **Hook kinds SkyyTrees already applies** (T45 KINDS list): XP (skill:bonus xp.<skill>), DD, EXTRA / EXTRA2 (extra drop rolls), VEIN, FELLER,
  MOVE (flat move layer, SkyySkills / SkyyAccessories), HP / STA / MANA (own stat modifiers), COINS, SPREAD, SWING, RFALL, plus the `old`
  aliases (`Mining.MSpeed` = mining speed, `Mining.MGems` = gem drop ITEM). Prefer these: no applier rebuild.
- **Other appliers** (trees_v3_effects.py rows, THE CONTRACT): SkyyGear (bp / dmg / cc / cd), SkyyPets (pet rows), SkyyAccessories, SkyyCooking,
  plus NEW in P8: **SkyyClasses** for the Combat tree's conditional fight rows (codes `drAll`, `dmgLow`, `dmgBoss`, `kbRes` read by
  `Skill.Combat.b<n>.<id>` through `tree:fn:level`; inside P4's caps dmgCap 40 / drCap 35), **SkyyMobs** for the Spoils loot rows
  (`drop`, `coins`, `rare`, `bossRoll`, `dbl` on a kill by the player), **SkyyPets** for the Beastmastery tree (4.4).
- **Budgets per skill tree** (check() proves each, like TREE_FORT_MAX): Fortune incl. EXTRA chance (1 % extra roll = 1 Fortune) <= 40;
  **XP <= +30 %** (new `TREE_XP_MAX`; the rebirth model assumes ~25 %); move speed from one tree <= +10 %; max Health from one tree <= +10 %.
- **Stays coming soon (later rounds, named in the page text "coming with <system>"):** the skill ACTIVES and their modifier upgrades
  (Depth Charge, Pollen Cloud, Grapple Vine, Flurry, Shield Wall, Mark the Prey, Rally Cry, Pet Dig, Pet Harvest, Sweep Harvest; Q4),
  pure visuals (glints / glow / see-through-walls / tracks), durability rows (lifelong-tool durability UNVERIFIED), stack-size / sack rows,
  seasons / fey / geode / mushroom rows whose items or systems do not exist, and capstones that need a timer or a new drop (Heart of the
  Mountain, Core Tap, World Tree's Blessing, Heart of the Grove, Pathfinder's Mantle, Edge of the Legend, Unbreakable, Master Looter).
  Free row perks that stay soon cost nothing and never block a gate.

### 4.2 P8b - the essentials (Mining, Foraging, Combat): row-by-row (ranks x per rank = total; NEW_TEXT where the effect changed)

**Mining** (Fortune budget is full at 40.0 after P5 -> no new Fortune; XP 25 -> 29):
| Id | Name | Hook | Number / new text |
|---|---|---|---|
| b1 r2b | Burst Recovery | VEIN | "Burst Reach: +1 vein size/rank" (Vein Burst is passive, no cooldown) |
| b1 r2c | Chain Fortune | XP | "+2 % Mining XP/rank" (2) |
| b1 r3c | Steady Pick | old Mining.MSpeed kind | "+1 % mining speed/rank" (4) |
| b2 free | Stoneskin | RFALL | "-10 % fall damage" |
| b2 r2a | Rockhide | HP | "+2 % max Health/rank" (3) |
| b2 r2b | Echo Step | MOVE | "+2 % move speed/rank" (2) |
| b2 r4b | Hardened Edge | SkyyGear dmg | "+1.5 % damage/rank" (3) |
| b2 r5c | Blast Hammer | VEIN | "+2 vein size/rank" (2) |
| b3 r3b | Deep Bounty | COINS (as MCoins) | "2 % chance/rank an ore also pays coins" (3) |
| b3 r4a | Miner's Fortune | old Mining.MGems ITEM | "+1 % gem drop chance/rank" (3) |
| b3 r5b | Abyss Walker | MOVE | "+2 % move speed/rank" (3) (move total 4 + 6 = 10) |
Stay soon: Prospector's Eye, Vein Sense, Lantern Lore, Cave Stalker, Depth Charge + Bigger Bang + Safe Fuse, Seismic Pulse, Bottomless
Pockets, Durable Grip, Quick Repair, Emergency Pick, Lucky Strike, Tool Tempering, Cave Sense, Geode Cracker, Dust Sweep, Heart of the
Mountain, Core Tap.

**Foraging** (Fortune 37.5 -> 39.9; XP 25 -> 29.5):
| Id | Name | Hook | Number / new text |
|---|---|---|---|
| b1 r2b | Quick Fell | FELLER | "Timber reach: +1 log/rank" (3) (FELLER parameter meaning UNVERIFIED - builder reads the kind) |
| b1 r3b | Steady Rhythm | the Woodcutter speed row's kind | "+1 % chopping speed/rank" (4) |
| b1 r4a | Rare Grain | EXTRA | "+0.8 % chance a log drops once more/rank" (3) |
| b1 r5b | Forest Fortune | XP | "+1.5 % Foraging XP/rank" (3) |
| b3 r1a | Light Foot | MOVE | "+2 % move speed/rank" (3) |
| b3 r3b | Sturdy Hide | HP | "+2 % max Health/rank" (3) |
| b3 r3c | Wind Walker | RFALL | "-5 % fall damage/rank" (2) |
Stay soon: Timber Sense, Replanter, Splinter Shield, Echo Fell, Green Thumb, Forager's Pouch, Pollen Cloud + Wide Bloom + Lingering Spores,
Mushroom Hunter, Beast Trails, Wild Taste, Camouflage, Seasonal Bounty, Fey Bargain, Grapple Vine + Long Vine + Vine Recovery + Vine Swing,
Hawk Eye, Hardwood Axe, the 3 capstones.

**Combat** (points = class level; damage rows go through SkyyClasses UpFx = P4's 40 % tree-damage cap):
| Id | Name | Hook | Number / new text |
|---|---|---|---|
| b1 free | Combat Focus | SkyyGear dmg | "+3 % damage" (the 3-hit streak needs a streak system - nearest flat effect) |
| b1 r3a | Finisher | SkyyClasses dmgLow | "+4 % damage to enemies below 30 % Health/rank" (3) |
| b1 r3b | Momentum | MOVE | "+1 % move speed/rank" (4) |
| b1 r5a | Trophy Hunter | SkyyClasses dmgBoss | "+3 % damage to bosses and mini bosses/rank" (3) (mob:fn:info "rank", P4) |
| b2 r1a | Toughness | HP | "+2 % max Health/rank" (5) |
| b2 r1b | Iron Will | SkyyClasses kbRes | "+3 % knockback resistance/rank" (3) |
| b2 r3a | Thick Skin | SkyyClasses drAll | "+2 % damage reduction/rank" (4) (inside drCap 35) |
| b3 r1a | Scavenger | SkyyMobs drop | "+2 % mob drop chance/rank" (5) |
| b3 r1b | Coin Purse | SkyyMobs coins | "+3 % coins from kills/rank" (3) |
| b3 r3b | Rare Drop | SkyyMobs rare | "+1 % rare drop chance/rank" (3) (gear-bag rarity roll) |
| b3 r4a | Boss Hunter | SkyyMobs bossRoll | "+3 % boss loot roll/rank" (3) |
| b3 r5a | Lucky Kill | SkyyMobs dbl | "2 % chance/rank to double a mob's drops" (3) |
Stay soon: Flurry + Extra Strike + Flurry Recovery + Rending + Parry Reflex, Bloodlust, Shield Wall + Longer Wall + Quick Draw + Bastion +
Ward Pulse, Reprisal, Second Wind, Rally, Mark the Prey + Wide Mark + Lingering Mark, Treasure Sense, Salvage, the 3 capstones.
Loot rows never touch UT / Mythic rates (P5 targets 1-2 UT an hour, Mythic 1 per 5-10 boss kills): SkyyMobs applies drop / rare / bossRoll
before the UT and Mythic rolls, and its harness proves the rates stay inside the P5 bands with every row maxed.

### 4.3 P8b gates after wiring (DERIVED by the generator; table printed in the build log)
Mining, Foraging and Combat gain 29 / 21 / 40 hooked ranks, so most of their rows reach 0/5/10/15/20/25. **Ranks a player already owns in
a row whose gate rises stay owned and keep working until that tree's next respec** (the R1 grandfather rule; UNVERIFIED that Trees 0.4.5
already does this for SKILL trees - the builder checks `TreeV3.GATES` use on read; if not, add it: never take ranks away on read).

### 4.4 P8c - Beastmastery (Skyy skills.md:164 "a skill that levels up from leveling pets")
- **SkyySkills: new skill slot Beastmastery** (saved key `Beastmastery`, same P3 curve, resets on rebirth like the other skills, counts
  for VP as a capped skill (the 11 max stays)). XP = pet XP the player's pets gain x `beast.xpFactor` (PROPOSED 1.0; SkyyPets calls
  `skill:fn:addxp {UUID, "Beastmastery", amount}` after each pet XP grant, AFTER pet echo, so Beastmastery Echo also speeds the skill).
  Beastmastery is in `bridge.bonus.addxpSkills` (Insight / keep / Echo apply) and in `catchup.skills`. Pets keep their levels on rebirth.
  The skill levels again from new pet XP only (it never reads pet levels), so the rebirth reset is real.
- **SkyyTrees:** Beastmastery points = the Beastmastery level (the T45:10312 branch). The 40 rows go live: pet XP rows (+x % pet XP of a kind)
  -> SkyyPets applier effects `petxp.<kind>` (all / combat / mining / farming+foraging); "+x % all stats from <kind> pets" -> SkyyPets
  `petstat.<kind>` (inside the pets' 15 % power share: per-tree budget +15 % pet stats); Pack Speed / Alpha's Mark / Pack Instinct ->
  SkyyPets summon combat numbers; actives (Rally Cry, Pet Dig, Pet Harvest) + Glimmering Coat + Kinship (extra pet slot) stay soon.
- **Pets XP budget:** Beastmastery tree pet XP <= +30 % per pet kind (same TREE_XP_MAX); pet pace from P5 (Pets 0.4.8) is the target, so P8c
  re-checks P5's pet-level-per-hour table with the tree maxed and lowers pet XP rows if a pet levels > 30 % faster than P5's target.

### 4.5 P8d - useful + light trees (Farming, Cooking, Alchemy, Fishing, Exploration, Acrobatics, Smithing)
Same rules, one skill per commit, appliers SkyyCooking / SkyyExploration / SkyyFishing / SkyySkills (Alchemy, Smithing) as they already
read their keys. Fishing stays "nice to have" until its rework (A:187 Q4): only rows that use SkyyFishing's existing tree:fn:bonus kinds.
Exploration XP rows (Wanderer, Cartographer) -> SkyyExploration XP (Exploration never resets, so they are kept forever; XP <= +30 %).
The builder writes the row-by-row table into the patch header as 4.2 does (no new decisions: every effect is one of the 4.1 kinds or stays
soon).

---

## Part 5 - Rounds, versions, files (PROJECT-RULES 4: FULL rounds - saved config migrations, several mods)

| Round | Mods (version from the SET pin at build time) | Contents | Size |
|---|---|---|---|
| **P8a** rebirth numbers | SkyySkills next (0.4.59 if P6 has not bumped it), SkyyRebirth 0.4.2 | Part 2 + 3 | Full (migrations) |
| **P8b** essential trees | SkyyTrees 0.4.6 (from 0.4.5), SkyyClasses next (0.1.45), SkyyMobs next (0.1.15 or +1 after P5) | 4.2-4.3 | Full |
| **P8c** Beastmastery | SkyySkills +1, SkyyPets next (0.4.9 after P5's 0.4.8), SkyyTrees 0.4.7 | 4.4 | Full (new saved skill slot) |
| **P8d** useful + light trees | SkyyTrees 0.4.8, + SkyyCooking / SkyyExploration / SkyyFishing as rows need | 4.5 | Full, split per skill |

P8a and P8b can build in parallel (no shared file: Skills/Rebirth vs Trees/Classes/Mobs). P8c needs P8a's Skills pinned. P8d after P8b.
FLOOR comments (tools/deploy_set.py): P8a Skills + Rebirth pin + roll back together (Rebirth's page reads the new combined line via
`rebirth:fn:stat`; a rollback of Skills alone keeps the old list = 7-9 % fast runs, harmless); P8c: never roll Skills below P8c once a
Beastmastery XP line was saved (the older Skills drops the unknown key on save - same as Exploration's 0.4.1 rule).

### 5.1 Files and anchors per mod (new patch script each from the SET pin; never edit generated scripts)

| Mod | Changes | Anchors |
|---|---|---|
| SkyySkills (tools/skills_<ver>_patch.py) | `rebirth.pastLifeXp` default -> 2.3 (constant + row help); class XP clamp: `RbStat.fetch` z[3] uses a new `CLASSXP_MAX = 500.0` (not MAXPCT, which stays 200 for the stats); `rebirth.xpMultMax` row + field + the cut in `SkillBonus.xpBonus` (2.5); Stats line (2.5); migration PlMigP8 (5.3) | S58:5337, 8546-8557, 11041-11050, 12236-12245, 13404-13414, 13475-13478, 21674 |
| SkyyRebirth (tools/rebirth_0_4_2_patch.py from build_skyyrebirth_0.4.1.py) | migration RbMigP8 (`rebirth.max` 10 -> 0); `dust.first` row hidden; Nexus hover value line if missing (3.4); row help "0 = no limit" | REB:123-126, 646-699, 1576-1595, the page hover builder |
| SkyyTrees 0.4.6+ (tools/trees_0_4_6_patch.py from 0.4.5; data in tools/trees_v3_data.py + trees_v3_effects.py - the ONE tables) | hooks / NEW_TEXT of 4.2 (then 4.4 / 4.5); `TREE_XP_MAX` 0.30 + move / Health budgets in check(); gate table; grandfather check (4.3); Beastmastery points (4.4) | `TreeV3.GATES`, T45:10312, `check()`, READER_MODS (+ SkyyClasses, SkyyMobs) |
| SkyyClasses (tools/classes_<ver>_patch.py) | UpFx codes drAll / dmgLow / dmgBoss / kbRes read from `Skill.Combat.*` via tree:fn:level; `tree:reads:SkyyClasses` lists them | `UpFx.DMG_CAP`, the dr / kb codes (FX_CLASSES) |
| SkyyMobs (tools/mobs_<ver>_patch.py) | applier for 5 Spoils rows on player kills; `tree:reads:SkyyMobs`; rate proof vs P5 UT / Mythic | the drop roll, `mob:fn:info` |
| SkyyPets (P8c) | `skill:fn:addxp` Beastmastery after each pet XP grant; petxp / petstat rows | SkyyPets 4519-4554 (petecho), RB_READS |

### 5.2 Server Setup rows (tools/skyycfg.py, KEEP=10; Menu-Pattern pages)

| Mod -> page | Row (key) | Type / range | Default |
|---|---|---|---|
| Skills -> Levels | Past-life XP boost by rebirth (`rebirth.pastLifeXp`) | text, 1-20 entries, each 1-10 | `1.1,1.35,1.6,2,2.45,2.15,2.25,2.4,2.55,2.7` |
| Skills -> Levels | Fastest rebirth: most rebirth XP (`rebirth.xpMultMax`) | dec 0-100, 0 = off | 0 (help: "9.3 = runs stop shrinking at rebirth 10") |
| Skills -> Levels (P8c) | Beastmastery XP per pet XP (`beast.xpFactor`) | dec 0-10 | 1.0 |
| Rebirth -> Rebirth | Max rebirths per profile (`rebirth.max`) | int 0-1000 | 0 (help "0 = no limit") |
| Rebirth -> Rewards | Dust multiplier (`dust.first`) | - | row hidden (dead) |
| Trees / Classes / Mobs / Pets | one row per new EFFECTS row (per rank + ceiling, as R3b/R3c: `cfg_rows`) | dec | 4.2 numbers |

### 5.3 One-time migrations (PROJECT-RULES 4; clone `Mn52Mig` / `CurveP3Mig` (Skills), `vpMig` journal style (Rebirth))

- **SkyySkills PlMigP8** (`xp.properties`): `rebirth.pastLifeXp` rewritten ONLY when the line is exactly `1.2,1.45,1.8,2.25,2.8`; absent
  line = nothing written (the new code default applies; live NewBetaTest has no line); a hand-edited list is kept + one INFO line.
  `rebirth.xpMultMax=0` appended with its comment. Verified History snapshot first, one config-changes.log line per change (Undo in Server
  Setup -> Changes), bytes + line endings kept, a java.util.Properties check that only the planned keys differ, run-once marker
  `Balance P8 rebirth (SkyySkills <ver>)`, a fresh file carries the marker.
- **SkyyRebirth RbMigP8** (`config.properties`): `rebirth.max` `10` -> `0` only when exactly `10`; same kit; marker `Balance P8 rebirth
  (SkyyRebirth 0.4.2)`. Live: `rebirth.max=10` -> migrates.
- **Saved player data: none** (VP, ranks, tree ranks unchanged; P8c adds a new skill key, absent = 0 XP).
- LIVE check: copy the live `Skyy_SkyySkills/xp.properties` and `Skyy_SkyyRebirth/config.properties` to `tools/dev/scratch/p8a/` and run both
  migrations there in the harness (as Mn52Mig did).

### 5.4 Harness checks (each mod's bare-JVM test, -Xverify:all, then all P8 jars in one JVM)

1. Past-life: rebirth n = 1..12 returns the 2.3 list (11-12 = 2.7); prevCap 50/60/70/80/90/100/100...; Exploration never boosted.
2. Class XP rebirth part 300 % -> 300 % (no longer 200); Health / Mana % stats still clamp at 200.
3. `rebirth.xpMultMax` 9.3: past-life 2.7 x rb 3.0 -> rb' = 2.444; 0 = no cut; tree part never cut; NaN / negative ignored.
4. Rebirth: `rebirth.max` 0 -> a profile with 25 rebirths can rebirth; cap answers stay 100 from rebirth 5 (SkyySkills clamp).
5. Migrations on fresh / live copy / hand-edited / half-migrated files (marker last); Undo restores the exact old line.
6. Trees: check() proves every budget (Fortune 40, XP 30, move 10, Health 10 per tree); no "(coming soon)" upgrade has a hook; every hooked
   upgrade's reader lists its key; gates printed; a saved file with ranks above a new gate keeps them on read.
7. Mobs: 10,000 simulated kills with every Spoils row maxed: UT / Mythic per hour inside P5's bands.
8. Model (`balance_model.py --rebirth --check`): greedy ratio 0.95-1.05 for rebirths 1-10, all-keep <= 1.15, buy-cheapest <= 1.25.

### 5.5 In-game test steps (TEST-CHECKLIST after deploy)

1. `/skills` Stats page: "Rebirth XP x… (past-life x1.1 below Lv 50 ...)" on a rebirth-1 profile (admin test rebirth works while checks
   fail, economy.md:148).
2. `/rebirthadmin points 800` then `/rebirth`: keep line "+200 % XP"; class XP from a kill is about 3x the rebirth-0 amount x past-life
   (not capped at +200 %).
3. Server Setup -> Rebirth: Max rebirths = 0 (no limit); Changes lists the migrated line with Undo. Rebirth a test profile 6 times: the cap
   stays 100 at rebirth 6, rebirth 7 still allowed.
4. Server Setup -> Skills: set Fastest rebirth to 9.3 -> the Stats line says "(at the server's fastest rebirth)" on a rebirth-12 profile with
   lots of VP; set back to 0.
5. (P8b) Mining tree: Burst Reach / Blast Hammer make Vein Burst break more ore; Combat tree: Thick Skin lowers hits taken, Trophy Hunter
   shows on a boss; rows with old ranks above a new gate still work.
6. (P8c) Pets gain XP -> Beastmastery skill XP rises; the Beastmastery tree has points.

### 5.6 Model check (DERIVED - the numbers hit the targets)

| Target (source) | Model | OK |
|---|---|---|
| Rebirth n 15 % shorter, n = 1-10 (A:187 Q3), vs the finished first run | greedy 0.98-1.01 every rebirth | yes |
| Lazy play still works (T3 6.4 "skipping the Nexus never hurts badly") | all-keep 1.04-1.13 | yes |
| Spend vs keep is a real choice (A:193 answer 9) | the last ranks are worth 0.20-0.25 % / VP vs keep 0.25 | yes |
| Keep: +0.25 % / VP, no cap (A:193) | unchanged; the hidden +200 % class clamp lifted | yes |
| Rebirths unlimited, cap 100 (A:193) | rebirth.max 0; cap 100 from rebirth 5 | yes |
| 1 free respec per rebirth (A:193 answer 5) | VERIFIED live (Trees 0.4.5) | yes |
| Nexus respec costs a Void Charm (answer 7) | VERIFIED live | yes |
| First rebirth after 40-50 h (A:185) | 45 h run, class cap 33.1 h (P3) - ~29 h with today's tree XP rows (1.3) -> P9 | P9 |

### 5.7 balance_model.py (the P8 builder ports Appendix A AFTER the builder editing balance_model.py now has committed)

Port `rebirth_run` (= scratch `sim_run`), `vp_earned`, `rb_mults`, `rb_buy`, `rb_campaign`, `rb_tune_past`, `rb_table` into a new
`# ===== P8 REBIRTH` section. Replace `vp_plan` / tables 5b-5c (fixed VP_EARNED list) with `rb_campaign` (VP from the live formula), add
`--rebirth` (prints 2.4 + 1.4, writes "### 7. Rebirth (P8)" into research/balance/targets.md) and fold its rows into `--check`. Constants
to add: VP_BASE/PER/SKILL/OVER, INSIGHT / CLASS_ECHO / SKILL_ECHO ladders (REB:611-620), PAST_LIFE = 2.3, CLASS_RB_MAX 5.0 (was 2.0 in
live), XP_BONUS_MAX 5.0, KEPT_MAX 0.30. Class Balance Workbench: republish after P8a (rebirth numbers changed - memory rule).

### 5.8 UNVERIFIED

- Kept power per rebirth (+6 % GUESS): kept gear tiers, shards, pets, charms. The whole 2.3 list leans on it (2.4 sensitivity) - Skyy's
  play-test and the Server Setup row settle it.
- The play split (SHARE) and so the Echo values; a focused Miner values Mining Echo ~2x.
- Hand Echo's shared ladder (how the 6 nodes share the 5 Echo costs) and which Hand nodes show "Coming with" today (Fishing / Acrobatics
  readers) - read REB 1404-1440 + SkyySkills `tree:reads`.
- Whether the Nexus page already shows the VP split and the per-node "worth vs keep" line (3.3-3.4).
- FELLER / VEIN parameter meanings for the new rows; lifelong-tool durability (keeps those rows soon); Trees' grandfather-on-read for skill
  trees (4.3); SkyyClasses UpFx reading `Skill.Combat.*` keys; which drop roll SkyyMobs owns after P5.
- The tree XP rows' real spend order (the 29 h run-1 estimate in 1.3 assumes Pet Fang from Lv 10 and Combat Insight from Lv 25 with a
  Rare pet).

---

## Questions for Skyy (each with today's default in [brackets]; Skyy 2026-10-21 "just go with the recommended" -> every default is taken)

1. **Rebirth pace:** "15 % shorter each" through rebirth 10 (run 10 = ~9 h, class Lv 100 in ~6.5 h). After that runs keep shrinking only by
   the keep buff (~9 % a rebirth), down to ~3.7 h? [yes]
2. **Lift the hidden +200 % limit** on class XP from rebirth to the skills' +500 % (your "keep buff no cap")? [yes]
3. **Past-life boost** `1.1,1.35,1.6,2,2.45,2.15,2.25,2.4,2.55,2.7` (a bit lower than today; it dips at rebirth 6 because there are no new
   levels; the combined rebirth XP on the Stats page still rises)? [yes]
4. **Skill-tree active skills** (Flurry, Shield Wall, Vein-style actives, Pollen Cloud, Grapple Vine, Mark the Prey, pet actives): their own
   round after P9, and until then their upgrades stay "coming soon"? [yes, own round after P9]
5. **Upgrades that cannot work as drafted** (cooldowns on the passive Vein Burst, streak bonuses, "in caves" speed): give the nearest working
   effect with honest text (like the class trees)? [yes]
6. **Collection rank cap** keeps +1 every rebirth with no limit (ranks only give Enchanted items)? [yes]
7. **Beastmastery skill:** levels from the XP your pets gain (1 Beastmastery XP per pet XP), resets on rebirth like the other skills, and its
   points open the Beastmastery tree? [yes]
8. **Fastest-rebirth ceiling** as a Server Setup row, OFF by default (9.3 would stop runs shrinking at rebirth 10)? [yes, off]
9. **Unlimited rebirths on your test world:** switch the saved "max 10" to "no limit"? [yes]
10. **Combat tree loot rows** (Scavenger, Coin Purse, Rare Drop, Boss Hunter, Lucky Kill) live now, held so UT / Mythic rates stay on the
    P5 targets? [yes]

---

## Appendix A - the scratch model (tools/dev/scratch/p8spec/p8model.py, deleted after; port into balance_model.py, 5.7)

It imports balance_model (P3 curve `CURVES`, `xp_per_hour`, `catchup_mult`, `cum`, `SHARE`). Run: `--live` (today's ladders), `--noclamp`
(class clamp 5.0), `--past <list>`, `--kept <x>`, `--ceil <x>`, `--tune 10` (prints the 2.3 list: greedy, dt 0.05).

```python
VP_BASE, VP_PER, VP_SKILL, VP_OVER = 20, 10, 2, 12                     # REB:603-620
KEEP = 0.25                                                             # nexus.keep, % all XP per held VP
INSIGHT = ([12, 20, 32, 48, 72], [6, 8, 10, 12, 16]); CLASS_ECHO = ([4, 6, 10, 16, 24], [4, 5, 7, 9, 11])
SKILL_ECHO = ([4, 6, 10, 16, 24], [8, 11, 15, 20, 26])
CLASS_RB_MAX, XP_BONUS_MAX = 5.0, 5.0                                   # live class part 2.0 (S58:8546) -> P8 5.0; S58:12236 clamp 5
KEPT_PER_REBIRTH, KEPT_MAX = 0.06, 0.30                                 # GUESS
CAP1, STEP, CAPMAX, RUN1, SHRINK = 50, 10, 100, 45.0, 0.85
SKILLS = ["Class", "Mining", "Foraging", "Farming", "Cooking", "Alchemy", "Fishing"]
CEIL = None                                                             # rebirth.xpMultMax (None = off)

def arms():   # name, costs, % per rank, which XP streams it boosts
    return [("Insight", *INSIGHT, {s: 1.0 for s in SKILLS}), ("ClassEcho", *CLASS_ECHO, {"Class": 1.0}),
            ("MiningEcho", *SKILL_ECHO, {"Mining": 1.0}), ("ForagingEcho", *SKILL_ECHO, {"Foraging": 1.0}),
            ("HandFarming", *SKILL_ECHO, {"Farming": 1.0})]

def arm_value(pct, aff):   # % of all XP, time-weighted by SHARE
    return pct * sum(SHARE.get(s, 0) * f for s, f in aff.items())

def rebirth_run(cap, hours, mult, past_cap, past_mult, dt=0.02):
    """mult[s] = (1 + rebirth bonus, kept power); past-life on levels < past_cap; returns (h to class cap, levels at end, class XP earned)"""
    lv = {s: 0 for s in SHARE}; xp = {s: 0.0 for s in SHARE}; earned, t, t_cap = 0.0, 0.0, None
    while t < hours:
        for s, sh in SHARE.items():
            if sh <= 0: continue
            code, kept = mult.get(s, (1.0, 1.0))
            cm = code * (past_mult if lv[s] < past_cap else 1.0)
            if CEIL is not None: cm = min(cm, CEIL)
            gain = xp_per_hour(s, max(lv[s], 1), lv["Class"]) * sh * dt * cm * kept * catchup_mult(s, lv[s], lv["Class"])
            if s == "Class": earned += gain
            if lv[s] >= cap: continue
            xp[s] += gain
            while lv[s] < cap and xp[s] >= CURVES[s][lv[s]]:
                xp[s] -= CURVES[s][lv[s]]; lv[s] += 1
        t += dt
        if t_cap is None and lv["Class"] >= cap: t_cap = t
    return t_cap, lv, earned

def vp_earned(n, lv, cap, earned_class):   # REB:44-48
    capped = min(11, sum((3 if s == "Farming" else 1) for s in ("Mining", "Foraging", "Farming", "Cooking", "Alchemy", "Fishing")
                         if lv.get(s, 0) >= cap))
    r = earned_class / cum(CURVES["Class"], cap)
    over = math.floor(VP_OVER * (math.sqrt(min(r, 16)) - 1)) if r >= 1 else 0
    return VP_BASE + VP_PER * n + VP_SKILL * capped + over, capped, r

def rb_mults(ranks, held, n):
    kept = 1 + min(KEPT_MAX, KEPT_PER_REBIRTH * n)
    allb = sum(INSIGHT[1][:ranks["Insight"]]) / 100 + held * KEEP / 100
    out = {}
    for s in SKILLS:
        b = allb + sum(sum(p[:ranks[nm]]) / 100 for nm, c, p, aff in arms() if nm != "Insight" and s in aff)
        b = min(b, CLASS_RB_MAX if s == "Class" else XP_BONUS_MAX)
        out[s] = (1 + b, kept)
    return out

def rb_buy(ranks, bank, policy):   # greedy = buy while a rank beats keeping; keep = never; cheap = cheapest first
    while True:
        best = None
        for nm, cost, pct, aff in arms():
            r = ranks[nm]
            if r >= 5 or cost[r] > bank or policy == "keep": continue
            val = arm_value(pct[r], aff) / cost[r]
            if policy == "greedy" and val <= KEEP: continue
            key = val if policy == "greedy" else -cost[r]
            if best is None or key > best[0]: best = (key, nm, cost[r])
        if not best: return bank
        ranks[best[1]] += 1; bank -= best[2]

def rb_campaign(policy, past, nmax, dt=0.02):
    ranks = {a[0]: 0 for a in arms()}; bank = total = 0
    t0, lv, ec = rebirth_run(CAP1, RUN1, {}, 0, 1.0, dt)
    vp = vp_earned(1, lv, CAP1, ec)[0]; rows = [dict(n=0, t_cap=t0, target=t0)]
    for n in range(1, nmax + 1):
        bank += vp; total += vp; bank = rb_buy(ranks, bank, policy)
        cap, prev = min(CAPMAX, CAP1 + STEP * n), min(CAPMAX, CAP1 + STEP * (n - 1))
        pm = past[min(n, len(past)) - 1]; m = rb_mults(ranks, bank, n)
        target, run_target = t0 * SHRINK ** n, RUN1 * SHRINK ** n
        t, _lv, _ec = rebirth_run(cap, max(target * 1.8, 14.0), m, prev, pm, dt)
        _t, lv2, ec2 = rebirth_run(cap, run_target if t is None else max(run_target, t), m, prev, pm, dt)   # VP for the next rebirth
        vp = vp_earned(n + 1, lv2, cap, ec2)[0]
        rows.append(dict(n=n, cap=cap, past=pm, t_cap=t, target=target, total=total, held=bank, ranks=dict(ranks)))
    return rows

def rb_tune_past(nmax=10):   # bisection per entry: the greedy player's h to class cap = target
    past = [PAST_LIFE[0]]
    for n in range(1, nmax + 1):
        lo, hi = 1.0, 12.0
        for _ in range(22):
            mid = (lo + hi) / 2
            r = rb_campaign("greedy", past[:n - 1] + [mid] * 4, n, dt=0.05)[-1]
            lo, hi = (mid, hi) if (r["t_cap"] is None or r["t_cap"] > r["target"]) else (lo, mid)
        past = past[:n - 1] + [round(hi, 2)]
    return past
```
Tuned raw output (`--noclamp --tune 10`): `1.1, 1.33, 1.61, 1.99, 2.46, 2.14, 2.26, 2.39, 2.53, 2.69` (2.3 rounds it). Live-clamp tune for
comparison: `... 2.62, 3.1` at 9-10 (the +200 % clamp forces the boost up).
