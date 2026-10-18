"""Derive SkyySkills/build_skyyskills_0.4.53.py from the GENERATED SkyySkills 0.4.52 (build_skyyskills_0.4.52.py = the tools/deploy_set.py SET
pin; 0.4.52 came from 0.4.51 by tools/skills_0_4_52_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with
0.4.52 (nothing else changed); 0.4.52 stays untouched, its line endings are kept (tools/soundpass_gen.Patch).
Run:  python tools/skills_0_4_53_patch.py   then   python SkyySkills/build_skyyskills_0.4.53.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.53.py

Skyy's words (docs/answered/skills.md, gear.md, docs/log/2026-10.md):
  NO XP CAPS 2026-10-18: "is there a cap on acrobatics xp gain? or any other xp gain? if so remove all caps"
  FORTUNE MATH, NO CAP 2026-10-18: "so the way it works is, there isnt a cap on any of the fortunes. 100%= guaranteed double drop. 150%= 50%
    triple drop. and so on. so 300%= guaranteed 4 drops"
  LEVEL CAP PER REBIRTH 2026-10-18 (popup): ""5 rebirths to reach lvl 100": how should the level cap grow per rebirth?" -> "Start 50, +10 each"
  ALLOY SMITHING XP (log 2026-10-18 11:15): alloys pay 0 Smithing XP (RecipeXp.classify only bench Furnace; alloys use SkyyAlloy)
  FARMING TOO SLOW 2026-10-18: "and farming still levels really slow" (+ beta notes "Farming too slow, Foraging too fast")
ROLLBACK to 0.4.52: NOT plain - 0.4.52 reads the migrated 0 values as their OLD meaning: acro.fallXpMax=0 / acro.fallMaxXpPerMinute=0 = NO fall
  XP, perk.doubleDropMax=0 = no level-perk / accessory / pet Fortune, bridge.maxXpPerCall=0 = every grant of 1+ XP refused (read as 1),
  acro.jumpCooldownMs / dodgeCooldownMs 0 = 200 / 100 ms. Undo the 0.4.53 lines in Server Setup -> Changes (or restore the config-history copy
  "before the 0.4.53 no XP caps update") BEFORE rolling back. levels.skill.Farming stays (0.4.52 reads it: Farming keeps its own list - remove
  it in Server Setup -> Levels -> Own XP list per skill to go back to the general list; levels never drop below the paid marker's coins).
  level-floors.properties is ignored by 0.4.52 (the level cap goes back to the table: 100). No player file is changed by 0.4.53.
"""
import os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

# ---- 1. NO XP CAPS: (key, old default(s) '|' separated, new default)
NC_KEYS = [("acro.jumpCooldownMs", "800", "0"), ("acro.fallXpMax", "2000|2000.0", "0"), ("acro.fallMaxXpPerMinute", "3000|3000.0", "0"),
           ("acro.dodgeCooldownMs", "400", "0"), ("combat.max", "500", "0"), ("divinity.healXpMaxPerMinute", "900", "0"),
           ("bridge.maxXpPerCall", "500000", "0"), ("bridge.maxXpPerMinute", "3000000", "0"),
           ("acro.perfectDodge.maxXpPerMinute", "1000000", "0"), ("ranching.maxXpPerMinute", "1000000", "0"),
           # 2. FORTUNE NO CAP
           ("perk.doubleDropMax", "1.0|1|1.00", "0")]
assert len(set(_k for _k, _o, _n in NC_KEYS)) == len(NC_KEYS) == 11

# ---- 5. FARMING LEVEL LIST (the model: tools/skills_0_4_53_patch.py RATES; research note in the docstring NOTE below)
MINE_PER_MIN = 30 * (0.85 * 1 + 0.15 * 6.5) * 1.25     # 30 blocks a minute, 15 % Copper / Iron ore (6.5), mining.xpMultiplier 1.25 = 68.44
FARM_PER_MIN = 20 * 4.0                                 # 20 ripe crops a minute sustained (hoe, replanting), wheat / carrot / potato 4 XP = 80
FOR_PER_MIN = 2 * (6 + 9 * 6 * 0.7 + 100 * 1)          # 2 felled trees a minute: the chopped log 6 + 9 logs x 6 x 70 % + 100 leaves x 1 = 287.6
K_FARM = FARM_PER_MIN / MINE_PER_MIN


def pace(L):   # the gathering pace (gather.boost.early 3 to level 10, easing to late 1.5 at level 20) - Farming keeps it
    return 3.0 if L <= 10 else (1.5 if L >= 20 else 3.0 - 1.5 * (L - 10) / 10.0)


def mining(L):  # Mining's own list (0.4.16, Skyy): 10 + 5L + 1.5L^2 rounded half up
    return (21 + 10 * L + 3 * L * L) // 2


FARM_PER = [max(1, int(mining(L) * K_FARM * pace(L - 1) + 0.5)) for L in range(1, 101)]
FARM_PER[0] = 50   # review fix: level 1 = the general list's 50 (60 would drop a 50-59 XP player from Lv 1 to 0 - Skyy's never-lower rule)
assert FARM_PER[:6] == [50, 91, 137, 189, 256, 330] and all(FARM_PER[i] < FARM_PER[i + 1] or i in range(9, 20) for i in range(99)), FARM_PER[:25]
GEN = [50, 125, 200, 300, 500, 750, 1000, 1500, 2000, 3500, 5000, 7500, 10000, 15000, 20000, 30000, 50000, 75000, 100000, 200000, 300000, 400000,
       500000, 600000, 700000, 800000, 900000, 1000000, 1100000, 1200000, 1300000]
_cf, _cg = 0, 0
for _i in range(100):   # the new list never asks more XP than the general list for ANY level (no level ever drops)
    _cf += FARM_PER[_i]
    _cg += (GEN[_i] if _i < len(GEN) else 10 ** 9)
    assert _cf <= _cg, (_i + 1, _cf, _cg)
RATES = []
for _L in (5, 15, 30):
    _m = MINE_PER_MIN * 60
    _fo = FOR_PER_MIN * pace(_L) * 60
    _fa = FARM_PER_MIN * pace(_L) * 60
    RATES.append((_L, _m / mining(_L + 1), _fo / GEN[_L], _fa / GEN[_L], _fa / FARM_PER[_L]))
for _L, _mi, _fo, _fa0, _fa1 in RATES:   # Farming's levels per hour = Mining's (within 2 %) at every checked level
    assert abs(_fa1 / _mi - 1.0) < 0.02, (_L, _mi, _fa1)
FARM_LIST = ",".join(str(_x) for _x in FARM_PER)
RATE_TXT = "\n".join("     Lv %2d   Mining %6.2f   Foraging %7.3f (unchanged)   Farming %7.4f -> %6.2f levels an hour" % _r for _r in RATES)

NOTE = '''0.4.53 (2026-10-18) = NO XP CAPS + FORTUNE NO CAP + LEVEL CAP 50 (+10 A REBIRTH) + ALLOY SMITHING XP + FARMING LEVEL LIST.
  1. NO XP CAPS (Skyy 2026-10-18 docs/answered/skills.md: "is there a cap on acrobatics xp gain? or any other xp gain? if so remove all caps"):
     every XP gain cap is 0 = no cap now, and 0 means no cap everywhere:
       acro.fallXpMax 2000 -> 0 (was: 0 = no fall XP), acro.fallMaxXpPerMinute 3000 -> 0 (was: 0 = no fall XP), acro.jumpCooldownMs 800 -> 0
       (XP-only: a paid jump needs a fresh jump edge + acro.jumpMinMove 2 blocks of your own movement - unchanged; floor 200 -> 0),
       acro.dodgeCooldownMs 400 -> 0 (XP-only since 0.4.23: the roll + its push never waited for it; acro.dodgeMinMove still gates a paid roll;
       floor 100 -> 0), combat.max 500 -> 0 (no per-kill maximum; combat.min stays), divinity.healXpMaxPerMinute 900 -> 0, bridge.maxXpPerCall
       500000 -> 0 (was at least 1), bridge.maxXpPerMinute 3000000 -> 0, acro.perfectDodge.maxXpPerMinute 1000000 -> 0,
       ranching.maxXpPerMinute 1000000 -> 0 (acro.maxXpPerMinute was 0 already). Any value above 0 is still a cap an admin can set.
     KEPT on purpose (not XP-gain caps): harvestCooldownMs 5000 (one F-harvest of one block pays once - a crop regrows slower than that; an
       anti double-pay guard), acro.jumpMinMove / acro.dodgeMinMove (no XP for jumping / rolling in place), acro.teleportBlocks / maxSpeed (a
       teleport pays no move XP), combat.gap.max 3.5 (Skyy's 2026-10-02 KILL XP lock "gap rule max +250%%" - a bonus ceiling, not a gain cap;
       question for Skyy), farming.tierUpXpFactor 0.5 (Skyy's tool tier rule), the Wisdom x6 ceiling, the SkyyMobs XP factor <= 100, the
       10000-units-per-craft and 1000000-XP-per-furnace-take overflow guards.
  2. FORTUNE NO CAP (gear.md 2026-10-18 FORTUNE MATH, NO CAP: "there isnt a cap on any of the fortunes. 100%%= guaranteed double drop. 150%%=
     50%% triple drop"): perk.doubleDropMax 1.0 -> 0 = no cap (row max 1 -> 1000; any value above 0 still caps the level perk + accessories +
     pets + armor part, below 1 also tool Fortune - 0.4.48's rule). extras = floor(F) + (r < F mod 1); perk.fortuneGuard 100 stays the stop.
  3. LEVEL CAP 50 + 10 A REBIRTH (popup 2026-10-18 LEVEL CAP PER REBIRTH: "Start 50, +10 each"): new row levels.runCap (Levels, default 50,
     0-100, 0 = off = the table max; a fresh file has levels.runCap=50, an older file no line = 50): every skill and class skill but Exploration caps at
     min(levels.runCap, its table max) + SkyyRebirth's raise (rebirth:fn:cap is now asked with this base; SkyyRebirth 0.3.5 caps.levels 10 x
     rebirths) - 50 / 60 / 70 / 80 / 90 / 100 at rebirth 0 - 5, then 100 (new row levels.capMax 100, 0 = no clamp; Skyy "leave the lvl
     cap at 100 for now till we add more zones"; rebirths past 5 still run). Exploration keeps its
     table (SkyyRebirth never raises or resets it). XP keeps counting past the cap (unchanged). The capped level is used everywhere the
     level counts: perks, Fortune, Mana per class level, class power, Mana regen per class level, the Overall Level (+ the Farming average),
     /skills + Stats ("level 50 of 50" -> MAX), skill:fn:level / run (SkyyRebirth's "class at max level" = the cap), the curve notices.
     The leaderboards keep ranking by XP (their level column = the table level, unchanged). SkillDefs.levelCap / capMax honour a cap BELOW
     the table (0.4.35 assumed cap >= table).
     NEVER LOWERED: LvFloor - once (no Skyy_SkyySkills/level-floors.properties yet), right after SkillCfg.load, every players/*.properties is
     read (read only) and each skill level above 50 (above levels.runCap if lower) is kept as that profile's floor
     <pkey>/<saved skill name>=<level>,<total XP then>,<rb.lastTx then>; the cap of that profile + skill is never below its floor while its
     XP is at least that total and no rebirth ran since (a rebirth ends the floor for good). Farming's floor is its GENERAL-list level when this start added Farming's own list
     (the level the player really had). The file is written atomically, never rewritten (delete it = scanned again at the next start).
  4. ALLOY SMITHING XP (log 2026-10-18 11:15): RecipeXp.classify also pays Smithing for bench "SkyyAlloy" (SkyySacks' /craft Furnace alloy rows
     through skill:fn:craftxp) - ONCE per smelt at the 0.4.49 table value (Bronze 16, Dusk 45, Azurvane 38, Cinder 75, Lumen 63, Electrum 28),
     NOT times the output count (SkyyWorldGen 0.7.5 gives 2 bars a smelt; the Furnace keeps x output count). Enchanted alloys (no table row)
     pay smithing.smeltDefault once a smelt (follow-up: their own rows).
  5. FARMING LEVEL LIST (Skyy 2026-10-18 "and farming still levels really slow"): Farming gets its OWN level list (levels.skill.Farming, the
     0.4.16 Mining mechanism): XP for level L = Mining's (10 + 5L + 1.5L^2) x %.3f (Farming's XP a minute / Mining's with starting tools) x
     the gathering pace at level L - 1 (Farming keeps the pace), so Farming levels as fast as Mining. Level 10 at %d XP, 20 at %d, 50 at %d,
     100 at %d (the general list: 50 at 55.2 million, 100 at 637.7 million). Levels an hour with starting tools (model: Mining 30 blocks a minute, 15 %% Copper /
     Iron ore, x1.25; Foraging 2 felled trees a minute, 10 logs + 100 leaves; Farming 20 ripe crops a minute at 4 XP; the pace):
%s
     Foraging is 1.6x Mining at Lv 5 only and far BELOW it from Lv 10 on (the general list) - not lowered; an own Foraging list is a question
     for Skyy. Saved XP never changes; OwnCurve tells each profile once and pays the new levels' coins (0.4.16 rules, up to the level cap).
  6. MIGRATIONS (PROJECT-RULES 4): Nc53Mig (a clone of Mn52Mig, + several old spellings per key) ONCE on an EXISTING xp.properties (setup,
     after Mn52Mig, before SkillCfg.load): each of the 11 keys in item 1 + 2 whose LAST entry is a one-line entry holding exactly an old default
     -> 0; an admin's own value kept (INFO); no line = nothing; marker; config-history copy first; one change-log line per change (Undo);
     bytes + line endings kept. Fa53Mig (a clone of Zo49Mig) ONCE: appends levels.skill.Farming in a marked block when the file has no such
     line (an admin's own Farming list is kept); History first. A fresh file carries both markers + the Farming list.
  No new command / system / bridge key. New file level-floors.properties (written once). CHECKED: SkyySkills/test_skyyskills_0.4.53.py.
  ROLLBACK: see tools/skills_0_4_53_patch.py (Undo the 0.4.53 lines first - 0.4.52 reads 0 as "none" for the fall XP lines and the double drop).
''' % (K_FARM, sum(FARM_PER[:10]), sum(FARM_PER[:20]), sum(FARM_PER[:50]), sum(FARM_PER), RATE_TXT)

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.52.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.53.py"))
assert P.has('VERSION = "0.4.52"') and P.has("Mn52Mig") and not P.has("Nc53Mig") and not P.has("LvFloor"), "not the generated SkyySkills 0.4.52 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

# ================================================================================================ docstring + version
P.rep('''"""SkyySkills 0.4.52 - build script (derived from the generated 0.4.51 by tools/skills_0_4_52_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.53 - build script (derived from the generated 0.4.52 by tools/skills_0_4_53_patch.py - edit the patch, not this file;
''' + NOTE + '''0.4.52 was derived from the generated 0.4.51 by tools/skills_0_4_52_patch.py;
''')
P.rep('VERSION = "0.4.52"', 'VERSION = "0.4.53"')

# ================================================================================================ 1. NO XP CAPS - Acrobatics
P.rep('''ACRO_L.append("acro.jumpCooldownMs=800")''', '''ACRO_L.append("acro.jumpCooldownMs=0")   # 0.4.53 (Skyy "remove all caps"): was 800 (XP-only)''')
P.rep('''                 "# at most acro.fallXpMax; all fall XP together at most acro.fallMaxXpPerMinute in any 60 seconds (0 = no fall XP), a cap",''',
      '''                 "# at most acro.fallXpMax; all fall XP together at most acro.fallMaxXpPerMinute in any 60 seconds (0 = no cap, both), a cap",''')
P.rep('''FALL_DMG_DEF, FALL_MAX_DEF, FALL_PM_DEF = "10", "2000", "3000"''',
      '''FALL_DMG_DEF, FALL_MAX_DEF, FALL_PM_DEF = "10", "0", "0"   # 0.4.53 (Skyy "remove all caps"): 2000 / 3000 -> 0 = no cap''')
P.rep('''ACRO_L.append("acro.dodgeCooldownMs=400")''', '''ACRO_L.append("acro.dodgeCooldownMs=0")   # 0.4.53 (Skyy "remove all caps"): was 400 (XP-only)''')
P.rep('''"long JUMP_CD = 800L"''', '''"long JUMP_CD = 0L"''')
P.rep('''"double FALL_MAX = 2000.0", "double FALL_PER_MIN = 3000.0"''', '''"double FALL_MAX = 0.0", "double FALL_PER_MIN = 0.0"''')
P.rep('''"long DODGE_CD = 400L"''', '''"long DODGE_CD = 0L"''')
P.rep('''  JUMP_CD = Math.max(200L, {PKG}.SkillCfg.lng(p, "acro.jumpCooldownMs", 800L));''',
      '''  JUMP_CD = Math.max(0L, {PKG}.SkillCfg.lng(p, "acro.jumpCooldownMs", 0L));   // 0.4.53: 0 = every jump (the edge + jumpMinMove still gate)''')
P.rep('''  FALL_MAX = nn({PKG}.SkillCfg.dbl(p, "acro.fallXpMax", 2000.0));
  FALL_PER_MIN = nn({PKG}.SkillCfg.dbl(p, "acro.fallMaxXpPerMinute", 3000.0));''',
      '''  FALL_MAX = nn({PKG}.SkillCfg.dbl(p, "acro.fallXpMax", 0.0));   // 0.4.53: 0 = no cap (was: 0 = no fall XP)
  FALL_PER_MIN = nn({PKG}.SkillCfg.dbl(p, "acro.fallMaxXpPerMinute", 0.0));   // 0.4.53: 0 = no cap (was: 0 = no fall XP)''')
P.rep('''  DODGE_CD = Math.max(100L, {PKG}.SkillCfg.lng(p, "acro.dodgeCooldownMs", 400L));''',
      '''  DODGE_CD = Math.max(0L, {PKG}.SkillCfg.lng(p, "acro.dodgeCooldownMs", 0L));   // 0.4.53: 0 = every roll (dodgeMinMove still gates)''')
P.rep('''      double x = s[16] * {PKG}.AcroCfg.FALL_DMG_XP;
      if (x > {PKG}.AcroCfg.FALL_MAX) x = {PKG}.AcroCfg.FALL_MAX;''', '''      double x = s[16] * {PKG}.AcroCfg.FALL_DMG_XP;
      if ({PKG}.AcroCfg.FALL_MAX > 0.0 && x > {PKG}.AcroCfg.FALL_MAX) x = {PKG}.AcroCfg.FALL_MAX;   // 0.4.53: 0 = no cap''')
P.rep('''      double x = s[289] * {PKG}.AcroCfg.FALL_DMG_XP * (1.0 + {PKG}.AcroCfg.ROLL);
      if (x > {PKG}.AcroCfg.FALL_MAX) x = {PKG}.AcroCfg.FALL_MAX;''', '''      double x = s[289] * {PKG}.AcroCfg.FALL_DMG_XP * (1.0 + {PKG}.AcroCfg.ROLL);
      if ({PKG}.AcroCfg.FALL_MAX > 0.0 && x > {PKG}.AcroCfg.FALL_MAX) x = {PKG}.AcroCfg.FALL_MAX;   // 0.4.53: 0 = no cap''')
P.rep('''  double room = {PKG}.AcroCfg.FALL_PER_MIN - ringSum(s, sec, 153, 217);''',
      '''  if ({PKG}.AcroCfg.FALL_PER_MIN <= 0.0) {{   // 0.4.53: 0 = no cap (was: 0 = no fall XP)
    if (whole < 1.0) return 0.0;
    ringAdd(s, sec, whole, 153, 217);
    return whole;
  }}
  double room = {PKG}.AcroCfg.FALL_PER_MIN - ringSum(s, sec, 153, 217);''')
P.rep('''    ("acro.jumpCooldownMs", "Paid jump cooldown", "acrobatics", "int", "800", "200", "600000", "", "ms", "live,adv", "", "reload"),''',
      '''    ("acro.jumpCooldownMs", "Paid jump cooldown", "acrobatics", "int", "0", "0", "600000", "", "ms", "live,adv",
     "0 = every jump pays (after moving). Only XP: never delays a jump.", "reload"),''')
P.rep('''    ("acro.fallXpMax", "Most XP per landing", "acrobatics", "dec", "2000", "0", "1000000000", "", "", "live", "", "reload"),
    ("acro.fallMaxXpPerMinute", "Fall XP per minute cap", "acrobatics", "dec", "3000", "0", "1000000000", "", "", "live",
     "All fall XP in any 60 seconds (0 = no fall XP). Its own cap.", "reload"),''',
      '''    ("acro.fallXpMax", "Most XP per landing", "acrobatics", "dec", "0", "0", "1000000000", "", "", "live", "0 = no cap.", "reload"),
    ("acro.fallMaxXpPerMinute", "Fall XP per minute cap", "acrobatics", "dec", "0", "0", "1000000000", "", "", "live",
     "All fall XP in any 60 seconds (0 = no cap). Its own cap.", "reload"),''')
P.rep('''    ("acro.dodgeCooldownMs", "Paid dodge cooldown", "acrobatics", "int", "400", "100", "600000", "", "ms", "live,adv",
     "Only how often a roll pays XP. Never delays the roll or its push (0.4.23).", "reload"),''',
      '''    ("acro.dodgeCooldownMs", "Paid dodge cooldown", "acrobatics", "int", "0", "0", "600000", "", "ms", "live,adv",
     "Only how often a roll pays XP (0 = every roll after moving). Never delays the roll or its push.", "reload"),''')

# ================================================================================================ 1. combat.max
P.rep('''L.append("combat.max=500")''', '''L.append("combat.max=0")   # 0.4.53 (Skyy "remove all caps"): was 500; 0 = no maximum''')
P.rep('''cfg.addField(CtField.make("public static volatile long C_MAX = 500L;", cfg))''', '''cfg.addField(CtField.make("public static volatile long C_MAX = 0L;", cfg))   # 0.4.53: 0 = no maximum''')
P.rep('''    C_MAX = lng(p, "combat.max", 500L);''', '''    C_MAX = lng(p, "combat.max", 0L);   // 0.4.53: 0 = no maximum (was 500)''')
P.rep('''  if (x > C_MAX) x = C_MAX;
  return scaled(x);''', '''  if (C_MAX > 0L && x > C_MAX) x = C_MAX;   // 0.4.53: 0 = no maximum
  return scaled(x);''')
P.rep('''  if (x > (double) @PKG@.SkillCfg.C_MAX) x = (double) @PKG@.SkillCfg.C_MAX;''',
      '''  if (@PKG@.SkillCfg.C_MAX > 0L && x > (double) @PKG@.SkillCfg.C_MAX) x = (double) @PKG@.SkillCfg.C_MAX;   // 0.4.53: 0 = no maximum''')
P.rep('''    ("combat.max", "Combat XP maximum", "combat", "int", "500", "0", "1000000000", "", "", "live",
     "Most class XP one kill pays before the class skill XP multiplier (an NPC role's own XP beats it).", "reload"),''',
      '''    ("combat.max", "Combat XP maximum", "combat", "int", "0", "0", "1000000000", "", "", "live",
     "Most class XP one kill pays before the class XP multiplier (0 = no maximum; role XP beats it).", "reload"),''')

# ================================================================================================ 1. heal XP per minute
P.rep('''HEAL_PER_HP_DEF, HEAL_SELF_DEF, HEAL_MAX_DEF = "1", "1.25", "900"
assert (float(HEAL_PER_HP_DEF), float(HEAL_SELF_DEF), int(HEAL_MAX_DEF)) == (1.0, 1.25, 900)''',
      '''HEAL_PER_HP_DEF, HEAL_SELF_DEF, HEAL_MAX_DEF = "1", "1.25", "0"   # 0.4.53 (Skyy "remove all caps"): the minute cap 900 -> 0 = no limit
assert (float(HEAL_PER_HP_DEF), float(HEAL_SELF_DEF), int(HEAL_MAX_DEF)) == (1.0, 1.25, 0)''')
P.rep('''assert (HEAL_PER_HP_DEF, HEAL_MAX_DEF, HEAL_SELF_DEF) == ("1", "900", "1.25")''', '''assert (HEAL_PER_HP_DEF, HEAL_MAX_DEF, HEAL_SELF_DEF) == ("1", "0", "1.25")   # 0.4.53: 900 -> 0''')
P.rep('''for decl in ("boolean ON = true", "double PER_HP = 1.0", "long MAX_MIN = 900L", "double PER_HP_SELF = 1.25"):''',
      '''for decl in ("boolean ON = true", "double PER_HP = 1.0", "long MAX_MIN = 0L", "double PER_HP_SELF = 1.25"):   # 0.4.53: MAX_MIN 900 -> 0''')
P.rep('''  long m = {PKG}.SkillCfg.lng(p, "divinity.healXpMaxPerMinute", 900L);''', '''  long m = {PKG}.SkillCfg.lng(p, "divinity.healXpMaxPerMinute", 0L);   // 0.4.53: 0 = no limit (was 900)''')

# ================================================================================================ 1. perfect dodge + ranching per minute
P.rep('''PD_ON_DEF, PD_WIN_DEF, PD_CTR_DEF, PD_MULT_DEF, PD_XP_DEF, PD_PM_DEF = "true", "100", "750", "1.25", "5", "1000000"''',
      '''PD_ON_DEF, PD_WIN_DEF, PD_CTR_DEF, PD_MULT_DEF, PD_XP_DEF, PD_PM_DEF = "true", "100", "750", "1.25", "5", "0"   # 0.4.53: PD_PM_DEF 1000000 -> 0 = no cap''')
P.rep('''RANCH_PM_DEF = "1000000"''', '''RANCH_PM_DEF = "0"   # 0.4.53 (Skyy "remove all caps"): 1000000 -> 0 = no cap''')
P.rep('''"long XP = 5L", "long MAX_PM = 1000000L"):''', '''"long XP = 5L", "long MAX_PM = 0L"):   # 0.4.53: MAX_PM 1000000 -> 0''')
P.rep('''  MAX_PM = clampL(@PKG@.SkillCfg.lng(p, "acro.perfectDodge.maxXpPerMinute", 1000000L), 0L, 1000000000L);''',
      '''  MAX_PM = clampL(@PKG@.SkillCfg.lng(p, "acro.perfectDodge.maxXpPerMinute", 0L), 0L, 1000000000L);   // 0.4.53: 0 = no cap (was 1000000)''')
P.rep('''  long pm = @PKG@.SkillCfg.lng(p, "ranching.maxXpPerMinute", 1000000L);''', '''  long pm = @PKG@.SkillCfg.lng(p, "ranching.maxXpPerMinute", 0L);   // 0.4.53: 0 = no cap (was 1000000)''')
P.rep('''assert DEFAULTS.count(PD44_MARK_ID) == 1 and _dp.get("acro.perfectDodge.windowMs") == "100" and _dp.get("ranching.maxXpPerMinute") == "1000000"''',
      '''assert DEFAULTS.count(PD44_MARK_ID) == 1 and _dp.get("acro.perfectDodge.windowMs") == "100" and _dp.get("ranching.maxXpPerMinute") == "0"   # 0.4.53''')
P.rep('''assert ("\\n" + DEFAULTS).count("\\nacro.perfectDodge.windowMs=100\\n") == 1 and ("\\n" + DEFAULTS).count("\\nranching.maxXpPerMinute=1000000\\n") == 1''',
      '''assert ("\\n" + DEFAULTS).count("\\nacro.perfectDodge.windowMs=100\\n") == 1 and ("\\n" + DEFAULTS).count("\\nranching.maxXpPerMinute=0\\n") == 1   # 0.4.53: Nc53Mig moves 1000000 -> 0''')

# ================================================================================================ 1. bridge caps
P.rep('''BRIDGE_L.append("bridge.maxXpPerCall=500000")
BRIDGE_L.append("bridge.maxXpPerMinute=3000000")''', '''BRIDGE_L.append("bridge.maxXpPerCall=0")   # 0.4.53 (Skyy "remove all caps"): 500000 -> 0 = no cap
BRIDGE_L.append("bridge.maxXpPerMinute=0")   # 0.4.53: 3000000 -> 0 = no cap''')
P.rep('''"long PER_CALL = 500000L", "long PER_MIN = 3000000L",''', '''"long PER_CALL = Long.MAX_VALUE", "long PER_MIN = 0L",   # 0.4.53: no caps''')
P.rep('''  long c = {PKG}.SkillCfg.lng(p, "bridge.maxXpPerCall", 500000L);
  PER_CALL = c < 1L ? 1L : c;
  long m = {PKG}.SkillCfg.lng(p, "bridge.maxXpPerMinute", 3000000L);''', '''  long c = {PKG}.SkillCfg.lng(p, "bridge.maxXpPerCall", 0L);
  PER_CALL = c <= 0L ? Long.MAX_VALUE : c;   // 0.4.53: 0 = no cap (was at least 1)
  long m = {PKG}.SkillCfg.lng(p, "bridge.maxXpPerMinute", 0L);   // 0.4.53: 0 = no cap (was 3000000)''')
P.rep('''    ("bridge.maxXpPerCall", "Largest XP grant per call", "general", "int", "500000", "1", "1000000000000", "", "", "live,adv",
     "A guard against a broken mod: one grant from another mod asks for at most this much.", "reload"),
    ("bridge.maxXpPerMinute", "Granted XP per player per minute", "general", "int", "3000000", "0", "1000000000000000", "", "", "live,adv",''',
      '''    ("bridge.maxXpPerCall", "Largest XP grant per call", "general", "int", "0", "0", "1000000000000", "", "", "live,adv",
     "One grant from another mod asks for at most this much (0 = no cap).", "reload"),
    ("bridge.maxXpPerMinute", "Granted XP per player per minute", "general", "int", "0", "0", "1000000000000000", "", "", "live,adv",''')

# ================================================================================================ 2. FORTUNE NO CAP
P.rep('''PERK_L.append("perk.doubleDropMax=1.0")''', '''PERK_L.append("perk.doubleDropMax=0")   # 0.4.53 (Skyy "there isnt a cap on any of the fortunes"): 1.0 -> 0 = no cap''')
P.rep('''"double DD_MAX = 1.0"''', '''"double DD_MAX = 0.0"''')
P.rep('''  DD_MAX = Math.min(1.0, rate(p, "perk.doubleDropMax", 1.0));''',
      '''  DD_MAX = rate(p, "perk.doubleDropMax", 0.0);   // 0.4.53: 0 = no cap (the default; was 1.0 and never above 1)''')
P.rep('''  return c > {PKG}.PerkCfg.DD_MAX ? {PKG}.PerkCfg.DD_MAX : c;''',
      '''  return ({PKG}.PerkCfg.DD_MAX > 0.0 && c > {PKG}.PerkCfg.DD_MAX) ? {PKG}.PerkCfg.DD_MAX : c;   // 0.4.53: 0 = no cap''')
P.rep('''  if (c > {PKG}.PerkCfg.DD_MAX) c = {PKG}.PerkCfg.DD_MAX;''', '''  if ({PKG}.PerkCfg.DD_MAX > 0.0 && c > {PKG}.PerkCfg.DD_MAX) c = {PKG}.PerkCfg.DD_MAX;   // 0.4.53: 0 = no cap''')
P.rep('''  if (base > @PKG@.PerkCfg.DD_MAX) base = @PKG@.PerkCfg.DD_MAX;''', '''  if (@PKG@.PerkCfg.DD_MAX > 0.0 && base > @PKG@.PerkCfg.DD_MAX) base = @PKG@.PerkCfg.DD_MAX;   // 0.4.53: 0 = no cap''')
P.rep('''  if (@PKG@.PerkCfg.DD_MAX < 1.0 || @PKG@.PerkCfg.FORT_MAX > 0.0) {   // 0.4.48: perk.fortuneMax 0 (the default) = no cap
    double cap = @PKG@.PerkCfg.DD_MAX < 1.0 ? @PKG@.PerkCfg.DD_MAX : @PKG@.PerkCfg.FORT_MAX;''',
      '''  boolean hard = @PKG@.PerkCfg.DD_MAX > 0.0 && @PKG@.PerkCfg.DD_MAX < 1.0;   // 0.4.53: an admin's doubleDropMax below 1 (0 = no cap)
  if (hard || @PKG@.PerkCfg.FORT_MAX > 0.0) {   // 0.4.48: perk.fortuneMax 0 (the default) = no cap
    double cap = hard ? @PKG@.PerkCfg.DD_MAX : @PKG@.PerkCfg.FORT_MAX;''')
P.rep('''    ("perk.doubleDropMax", "Double drop chance cap", "perks", "dec", "1.0", "0", "1", "", "", "live",
     "Double-drop chance cap (1 = 100%), tree Fortune included. Below 1 it caps tool Fortune too.", "reload"),''',
      '''    ("perk.doubleDropMax", "Double drop chance cap", "perks", "dec", "0", "0", "1000", "", "", "live",
     "0 = no cap. Else the level-perk Fortune cap (1 = 100%). Below 1 it caps tool Fortune too.", "reload"),''')

# ================================================================================================ 3. LEVEL CAP: SkillDefs
P.rep('''defs.addField(CtField.make("public static final int CAP_EXTRA_MAX = 1000;", defs))''',
      '''defs.addField(CtField.make("public static final int CAP_EXTRA_MAX = 1000;", defs))
# 0.4.53 (Skyy 2026-10-18 "Start 50, +10 each"): levels.runCap - the first-run level cap of every rebirth-reset slot (0 = off = the table max)
defs.addField(CtField.make("public static volatile int RUN_CAP = 50;", defs))
# 0.4.53 (Skyy 2026-10-18 "allow rebirths past 5 so you can keep upgrading. but leave the lvl cap at 100 for now till we add more zones."):
# levels.capMax - the highest level cap any rebirth reaches (0 = no clamp)
defs.addField(CtField.make("public static volatile int CAP_MAX = 100;", defs))''')
P.rep('''public static int capMax(int s, int cap) {
  int m = maxOf(s);
  return cap > m ? cap : m;
}''', '''public static int capMax(int s, int cap) {
  int m = maxOf(s);
  if (cap > 0 && cap < m) return cap;   // 0.4.53: a cap below the table (levels.runCap) is the max
  return cap > m ? cap : m;
}''')
P.rep('''  int l = levelIn(c, total);
  if (cap <= max || l < max) return l;''', '''  int l = levelIn(c, total);
  if (cap > 0 && cap < max) return l < cap ? l : cap;   // 0.4.53: a cap below the table (levels.runCap): the level stops there
  if (cap <= max || l < max) return l;''')
P.rep('''    C_DEFAULT = lng(p, "combat.default", 5L);''', '''    C_DEFAULT = lng(p, "combat.default", 5L);
    long rc53 = lng(p, "levels.runCap", 50L);   // 0.4.53: the first-run level cap (0 = off = the table max)
    {PKG}.SkillDefs.RUN_CAP = rc53 < 0L ? 0 : (rc53 > 100L ? 100 : (int) rc53);
    long cm53 = lng(p, "levels.capMax", 100L);   // 0.4.53: the clamp of every rebirth-raised cap (0 = none)
    {PKG}.SkillDefs.CAP_MAX = cm53 < 0L ? 0 : (cm53 > 1000L ? 1000 : (int) cm53);''')

# ================================================================================================ 3. LvFloor (fields + the pure lookup) + SkillCap
LVF_HEAD = '''# ================= 0.4.53 LvFloor: levels a player already had above the first-run cap are never lowered =================
# MAP = "<pkey>/<slot>" -> long[]{ level, total XP at the scan }, TX = pkey -> its rb.lastTx at the scan: the cap of that profile + slot is
# at least the level while the slot's XP is at least that total AND no rebirth ran since (SkillStore.RBTX still the scanned one). Filled once from level-floors.properties (LvFloor.start).
lvf = pool.makeClass(PKG + ".LvFloor")
for _d53 in ("public static final java.util.concurrent.ConcurrentHashMap MAP = new java.util.concurrent.ConcurrentHashMap();",
             "public static java.nio.file.Path FILE;", "public static volatile boolean NEW_FARM = false;",
             'public static final String NAME = "level-floors.properties";', "public static volatile int SCANNED = -1;",
             "public static final java.util.concurrent.ConcurrentHashMap TX = new java.util.concurrent.ConcurrentHashMap();"):
    lvf.addField(CtField.make(_d53, lvf))
lvf.addMethod(CtNewMethod.make(J14(r"""
public static int floorOf(String k, int s, long total) {
  if (k == null || s < 0 || MAP.isEmpty()) return 0;
  Object o = MAP.get(k + "/" + s);
  if (!(o instanceof long[])) return 0;
  long[] f = (long[]) o;
  if (total < f[1]) return 0;
  Object t = TX.get(k);   // the profile's last rebirth at the scan ("" = none): a rebirth since then ends the floor for good
  Object c = @PKG@.SkillStore.RBTX.get(k);
  String cur = c instanceof String ? (String) c : "";
  if (t instanceof String && !((String) t).equals(cur)) return 0;
  return (int) f[0];
}"""), lvf))
'''
P.rep('''scap = pool.makeClass(PKG + ".SkillCap")
''', LVF_HEAD + '''scap = pool.makeClass(PKG + ".SkillCap")
''')
# fetch asks SkyyRebirth with the first-run base (runBase), not the table max
P.rep('''    if (!@PKG@.SkillDefs.rebirthResets(s)) continue;
    int base = @PKG@.SkillDefs.maxOf(s);''', '''    if (!@PKG@.SkillDefs.rebirthResets(s)) continue;
    int base = runBase(s);   // 0.4.53: the first-run cap (levels.runCap), SkyyRebirth adds caps.levels x rebirths''')
P.rep('''scap.addMethod(CtNewMethod.make(J14(r"""
public static int[] fetch(java.util.function.Function f, String k) {''', '''# 0.4.53: the first-run cap of slot s: min(levels.runCap, its table max) for every rebirth-reset slot; Exploration / runCap 0 = the table max
scap.addMethod(CtNewMethod.make(J14(r"""
public static int runBase(int s) {
  int m = @PKG@.SkillDefs.maxOf(s);
  int c = @PKG@.SkillDefs.RUN_CAP;
  if (c <= 0 || !@PKG@.SkillDefs.rebirthResets(s)) return m;
  return c < m ? c : m;
}"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static int[] fetch(java.util.function.Function f, String k) {''')
P.rep('''public static int cap(String k, int s) {
  if (s < 0 || s >= @PKG@.SkillDefs.N) return 0;
  return @PKG@.SkillDefs.maxOf(s) + extra(k, s);
}"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static int level(String k, int s, long total) {
  if (s < 0 || s >= @PKG@.SkillDefs.N) return 0;
  return @PKG@.SkillDefs.levelCap(s, total, cap(k, s));
}"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static long need(String k, int s, long total) {
  return @PKG@.SkillDefs.needCap(s, total, cap(k, s));
}"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static long into(String k, int s, long total) {
  return @PKG@.SkillDefs.intoCap(s, total, cap(k, s));
}"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static String progress(String k, int s, long total) {
  return @PKG@.SkillDefs.progressCap(s, total, cap(k, s));
}"""), scap))''', '''public static int capT(String k, int s, long total) {
  if (s < 0 || s >= @PKG@.SkillDefs.N) return 0;
  int c = runBase(s) + extra(k, s);   // 0.4.53: the first-run cap + SkyyRebirth's raise (0.4.35: the table max + the raise)
  int cm = @PKG@.SkillDefs.CAP_MAX;   // 0.4.53 (Skyy "leave the lvl cap at 100 for now"): levels.capMax clamps it (0 = no clamp)
  if (cm > 0 && @PKG@.SkillDefs.rebirthResets(s) && c > cm) c = cm;
  int f = @PKG@.LvFloor.floorOf(k, s, total);   // 0.4.53: a level the profile already had is never lowered
  return f > c ? f : c;
}"""), scap))
# 0.4.53: the loaded XP of profile k (-1 = not loaded: no floor) - for the callers that ask the cap without a total
scap.addMethod(CtNewMethod.make(J14(r"""
public static long totalOf(String k, int s) {
  if (k == null || s < 0) return -1L;
  Object o = @PKG@.SkillStore.DATA.get(k);
  if (!(o instanceof long[])) return -1L;
  long[] d = (long[]) o;
  return s < d.length ? d[s] : -1L;   // SkillStore.rd is compiled later; a long read of a live array
}"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static int cap(String k, int s) {
  if (s < 0 || s >= @PKG@.SkillDefs.N) return 0;
  return capT(k, s, totalOf(k, s));
}"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static int level(String k, int s, long total) {
  if (s < 0 || s >= @PKG@.SkillDefs.N) return 0;
  return @PKG@.SkillDefs.levelCap(s, total, capT(k, s, total));
}"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static long need(String k, int s, long total) {
  return @PKG@.SkillDefs.needCap(s, total, capT(k, s, total));
}"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static long into(String k, int s, long total) {
  return @PKG@.SkillDefs.intoCap(s, total, capT(k, s, total));
}"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static String progress(String k, int s, long total) {
  return @PKG@.SkillDefs.progressCap(s, total, capT(k, s, total));
}"""), scap))
# 0.4.53: the TABLE level, never above the profile's cap - for the places that counted the table level (Overall, Mana per class level, class
# power, Mana regen per class level, the Farming average, the curve notices): equal to 0.4.52 while the cap is at or above the table
scap.addMethod(CtNewMethod.make(J14(r"""
public static int lvK(String k, int s, long total) {
  if (s < 0 || s >= @PKG@.SkillDefs.N) return 0;
  int t = @PKG@.SkillDefs.levelOf(s, total);
  int c = level(k, s, total);
  return c < t ? c : t;
}"""), scap))
# the profile key of a LOADED data array (identity); not loaded = the table level (0.4.52 exactly - never lower than before)
scap.addMethod(CtNewMethod.make(J14(r"""
public static int lvD(long[] d, int s, long total) {
  if (d == null || s < 0 || s >= @PKG@.SkillDefs.N) return 0;
  java.util.Iterator it = @PKG@.SkillStore.DATA.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object v = e.getValue();
    Object dd = d;
    if (v == dd) return lvK((String) e.getKey(), s, total);
  }
  return @PKG@.SkillDefs.levelOf(s, total);
}"""), scap))
# Farm3.lvIn (compiled before SkillCap) gets its capped body now
fm3.getDeclaredMethod("lvIn").setBody(J14(r"""{
  if ($1 == null || $2 < 0 || $2 >= $1.length) return 0;
  return @PKG@.SkillCap.lvD($1, $2, $1[$2]);   // 0.4.53: capped (levels.runCap)
}"""))''')
# skill:fn:run + the rebirth preview: the cap of the total they read (a not-loaded profile's floor too)
P.rep('''    long total = @PKG@.SkillStore.rd(d, s);
    int cap = @PKG@.SkillCap.cap(k, s);
    return new Object[]''', '''    long total = @PKG@.SkillStore.rd(d, s);
    int cap = @PKG@.SkillCap.capT(k, s, total);   // 0.4.53: + the floor of this total
    return new Object[]''')
P.rep('''    long total = @PKG@.SkillStore.rd(d, s);
    int cap = @PKG@.SkillCap.cap(k, s);
    p.setProperty("arm."''', '''    long total = @PKG@.SkillStore.rd(d, s);
    int cap = @PKG@.SkillCap.capT(k, s, total);   // 0.4.53
    p.setProperty("arm."''')
P.rep('''    int c2 = @PKG@.SkillCap.cap(k, s2);''', '''    int c2 = @PKG@.SkillCap.capT(k, s2, t2);   // 0.4.53''')
# the table-level readers -> capped
P.rep('''    sum += (s == {PKG}.SkillDefs.FARMING && {PKG}.Farm3.AVG) ? {PKG}.Farm3.avgOf(d) : {PKG}.SkillDefs.levelOf(s, d[s]);   // 0.4.37''',
      '''    sum += (s == {PKG}.SkillDefs.FARMING && {PKG}.Farm3.AVG) ? {PKG}.Farm3.avgOf(d) : {PKG}.SkillCap.lvD(d, s, d[s]);   // 0.4.37; 0.4.53: capped''')
P.rep('''      if (cs >= 0) {{ sum += {PKG}.SkillDefs.levelOf(cs, d[cs]); n++; }}''', '''      if (cs >= 0) {{ sum += {PKG}.SkillCap.lvD(d, cs, d[cs]); n++; }}   // 0.4.53: capped''')
P.rep('''    else sb.append({PKG}.SkillDefs.LABELS[s]).append(" ").append({PKG}.SkillDefs.levelOf(s, d[s]));''',
      '''    else sb.append({PKG}.SkillDefs.LABELS[s]).append(" ").append({PKG}.SkillCap.lvD(d, s, d[s]));   // 0.4.53: capped''')
P.rep('''      if (cs >= 0) part = {PKG}.SkillClass.skillName(u, cs) + " " + {PKG}.SkillDefs.levelOf(cs, d[cs]) + " (your class)";''',
      '''      if (cs >= 0) part = {PKG}.SkillClass.skillName(u, cs) + " " + {PKG}.SkillCap.lvD(d, cs, d[cs]) + " (your class)";   // 0.4.53: capped''')
P.rep('''  if (s < 0 || s >= @PKG@.SkillDefs.N || s >= d.length) return 0.0f;
  int lv = @PKG@.SkillDefs.levelOf(s, d[s]);''', '''  if (s < 0 || s >= @PKG@.SkillDefs.N || s >= d.length) return 0.0f;
  int lv = @PKG@.SkillCap.lvD(d, s, d[s]);   // 0.4.53: capped''')
P.rep('''  if (s < 0 || s >= @PKG@.SkillDefs.N || s >= d.length) return 0;
  return @PKG@.SkillDefs.levelOf(s, d[s]);
}"""), cpw))''', '''  if (s < 0 || s >= @PKG@.SkillDefs.N || s >= d.length) return 0;
  return @PKG@.SkillCap.lvD(d, s, d[s]);   // 0.4.53: capped
}"""), cpw))''')
P.rep('''    long[] d = (long[]) @PKG@.SkillStore.DATA.get(@PKG@.SkillStore.pkey(u));
    if (d == null || s >= d.length) return 0.0;
    return boost(7, @PKG@.SkillDefs.CLASSES[@PKG@.SkillDefs.classIdx(s)], @PKG@.SkillDefs.levelOf(s, @PKG@.SkillStore.rd(d, s)));''',
      '''    String pk = @PKG@.SkillStore.pkey(u);
    long[] d = (long[]) @PKG@.SkillStore.DATA.get(pk);
    if (d == null || s >= d.length) return 0.0;
    return boost(7, @PKG@.SkillDefs.CLASSES[@PKG@.SkillDefs.classIdx(s)], @PKG@.SkillCap.lvK(pk, s, @PKG@.SkillStore.rd(d, s)));   // 0.4.53: capped''')
P.rep('''    long[] d = (long[]) @PKG@.SkillStore.DATA.get(@PKG@.SkillStore.pkey(u));
    if (d == null || s >= d.length) return 0.0;
    int over = @PKG@.SkillDefs.levelOf(s, @PKG@.SkillStore.rd(d, s)) - FROM_LEVEL;''',
      '''    String pk = @PKG@.SkillStore.pkey(u);
    long[] d = (long[]) @PKG@.SkillStore.DATA.get(pk);
    if (d == null || s >= d.length) return 0.0;
    int over = @PKG@.SkillCap.lvK(pk, s, @PKG@.SkillStore.rd(d, s)) - FROM_LEVEL;   // 0.4.53: capped''')
P.rep('''      int lv = {PKG}.SkillDefs.levelOf(s, {PKG}.SkillStore.rd(d, s));''', '''      int lv = {PKG}.SkillCap.lvK(k, s, {PKG}.SkillStore.rd(d, s));   // 0.4.53: capped''')
P.rep('''      int lv = @PKG@.SkillDefs.levelOf(s, @PKG@.SkillStore.rd(d, s));''', '''      int lv = @PKG@.SkillCap.lvK(k, s, @PKG@.SkillStore.rd(d, s));   // 0.4.53: capped''')
# the row (no file line until an admin changes it: a missing line = 50)
P.rep('''     "A listed skill levels on its own list (level 1 first). XP is kept; new levels pay coins once.", "reload;check=SkillLv.checkEntry"),''',
      '''     "A listed skill levels on its own list (level 1 first). XP is kept; new levels pay coins once.", "reload;check=SkillLv.checkEntry"),
    # 0.4.53 (Skyy 2026-10-18 LEVEL CAP PER REBIRTH "Start 50, +10 each"): the first-run cap; SkyyRebirth adds caps.levels per rebirth
    ("levels.runCap", "Level cap before rebirths", "levels", "int", "50", "0", "100", "step=5", "", "live,danger",
     "First-run skill + class level cap; each rebirth adds +10. 0 = list max. Not Exploration.",
     "reload"),
    # 0.4.53 (Skyy 2026-10-18 "allow rebirths past 5 ... leave the lvl cap at 100 for now till we add more zones"): the clamp
    ("levels.capMax", "Highest level cap", "levels", "int", "100", "0", "1000", "step=10", "", "live,danger",
     "No rebirth raises a skill or class level cap above this (0 = no clamp). XP keeps counting.", "reload"),''')

# ================================================================================================ 4. ALLOY SMITHING XP
P.rep('''    if (b.equalsIgnoreCase("Furnace")) {{
      if (!{PKG}.SmithCfg.ENABLED) return null;''', '''    if (b.equalsIgnoreCase("Furnace") || b.equalsIgnoreCase("SkyyAlloy")) {{   // 0.4.53: + SkyyWorldGen's alloy smelts (SkyySacks' /craft Furnace)
      if (!{PKG}.SmithCfg.ENABLED) return null;''')
P.rep('''      long xp = per * (long) Math.max(1, po.getQuantity());''',
      '''      long xp = b.equalsIgnoreCase("SkyyAlloy") ? per : per * (long) Math.max(1, po.getQuantity());   // 0.4.53: an alloy pays once a smelt (2 bars out)''')

# ================================================================================================ 6. Nc53Mig + Fa53Mig: defaults, markers, classes
NC53_MARK_ID = "SkyySkills 0.4.53 no XP caps"
NC53_MARK = "# SkyySkills 0.4.53 no XP caps: every XP cap and the double drop cap 0 means no cap (old defaults moved to 0 once)."
FA53_MARK_ID = "SkyySkills 0.4.53 Farming level list"
FA53_HEAD = ["# ---------- Farming own level list (0.4.53) ----------",
             "# " + FA53_MARK_ID + " (Skyy 2026-10-18: farming levels really slow): Farming levels on its own list like Mining.",
             "# XP per level is Mining's x 1.169 x the gathering pace, so Farming levels about as fast as Mining. Saved XP never changes.",
             "# Server Setup -> Levels -> Own XP list per skill edits or removes it."]
for _x in [NC53_MARK] + FA53_HEAD:
    assert "=" not in _x and _x.startswith("# "), _x
    assert len(_x) <= 140 and all(ord(_ch) < 128 for _ch in _x), _x
P.rep('''L.append(MN52_MARK)   # 0.4.52: Mn52Mig's run-once marker - only a FRESH file has it (no block an older migration appends carries it)
DEFAULTS = "\\n".join(L) + "\\n"
''', '''L.append(MN52_MARK)   # 0.4.52: Mn52Mig's run-once marker - only a FRESH file has it (no block an older migration appends carries it)
NC53_MARK_ID = "''' + NC53_MARK_ID + '''"
NC53_MARK = "''' + NC53_MARK + '''"
NC53_KEYS = ''' + repr(NC_KEYS) + '''
FA53_MARK_ID = "''' + FA53_MARK_ID + '''"
FA53_HEAD = ''' + repr(FA53_HEAD) + '''
FARM_LIST = "''' + FARM_LIST + '''"   # 0.4.53: Farming's own level list (tools/skills_0_4_53_patch.py: Mining's x 1.169 x the gathering pace)
L.append(NC53_MARK)   # 0.4.53: Nc53Mig's run-once marker (a fresh file only)
RC53_L = ["# Level cap before rebirths (SkyySkills 0.4.53, Skyy: Start 50, +10 each): every skill and class skill but Exploration caps here on",
          "# the first run; each rebirth adds SkyyRebirth's caps.levels (+10). 0 means the list max. Levels you already had stay.",
          "levels.runCap=50",
          "# levels.capMax: the highest cap any rebirth reaches (Skyy: 100 for now, till more zones). 0 means no clamp.",
          "levels.capMax=100"]   # a missing line (an older file) reads the same 50 / 100
L.extend(RC53_L)
L.append("")
L.extend(FA53_HEAD)   # 0.4.53: Fa53Mig's block - a fresh file carries it (marker + the list); an old file gets the same block once
L.append("levels.skill.Farming=" + FARM_LIST)
DEFAULTS = "\\n".join(L) + "\\n"
''')
P.rep('''assert DEFAULTS.count(MN52_MARK_ID) == 1 and all(("\\n" + DEFAULTS).count("\\n%s=%s\\n" % (_k, _n)) == 1 for _k, _o, _n in MN52_KEYS)   # 0.4.52
''', '''assert DEFAULTS.count(MN52_MARK_ID) == 1 and all(("\\n" + DEFAULTS).count("\\n%s=%s\\n" % (_k, _n)) == 1 for _k, _o, _n in MN52_KEYS)   # 0.4.52
assert DEFAULTS.count(NC53_MARK_ID) == 1 and all(("\\n" + DEFAULTS).count("\\n%s=%s\\n" % (_k, _n)) == 1 for _k, _o, _n in NC53_KEYS)   # 0.4.53
assert DEFAULTS.count(FA53_MARK_ID) == 1 and ("\\n" + DEFAULTS).count("\\nlevels.skill.Farming=") == 1   # 0.4.53
''')
P.rep('''"\\n" + G43_DEFAULTS + "\\n" + G44_DEFAULTS + "\\n" + MN52_MARK + "\\n")   # 0.4.52: + the Mn52Mig marker;''',
      '''"\\n" + G43_DEFAULTS + "\\n" + G44_DEFAULTS + "\\n" + MN52_MARK + "\\n" + NC53_MARK + "\\n" + "\\n".join(RC53_L) + "\\n\\n" + "\\n".join(FA53_HEAD) + "\\nlevels.skill.Farming=" + FARM_LIST + "\\n")   # 0.4.53: + Nc53 marker + Fa53 block; 0.4.52: + the Mn52Mig marker;''')
P.rep('''assert _dp.get("levels.skill.Mining") == ",".join(str(_x) for _x in MINING_PER) and sorted(_k for _k in _dp if _k.startswith("levels.skill.")) == SKL_KEYS''',
      '''assert _dp.get("levels.skill.Mining") == ",".join(str(_x) for _x in MINING_PER) and sorted(_k for _k in _dp if _k.startswith("levels.skill.")) == sorted(SKL_KEYS + ["levels.skill.Farming"])   # 0.4.53: + Farming (Fa53 block)
assert _dp.get("levels.skill.Farming") == FARM_LIST and len(FARM_LIST.split(",")) == 100   # 0.4.53''')
P.rep('''mn52 = pool.makeClass(PKG + ".Mn52Mig")        # 0.4.52: the one-time less-Mana update (class Mana per level + regen) of an existing xp.properties
''', '''mn52 = pool.makeClass(PKG + ".Mn52Mig")        # 0.4.52: the one-time less-Mana update (class Mana per level + regen) of an existing xp.properties
nc53 = pool.makeClass(PKG + ".Nc53Mig")        # 0.4.53: the one-time no-XP-caps update (11 old cap defaults -> 0) of an existing xp.properties
fa53 = pool.makeClass(PKG + ".Fa53Mig")        # 0.4.53: the one-time Farming level list block appended to an existing xp.properties
''')

# ---- Nc53Mig = Mn52Mig's code with several old spellings per key ('|')
_a = P.s.index('mn52.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(MN52_MARK_ID), mn52))')
_e = P.s.index('could not update xp.properties for 0.4.52', _a)
_e = P.s.index('}"""), mn52))\n', _e) + len('}"""), mn52))\n')
CL = P.s[_a:_e]


def _sub(t, o, n):
    assert t.count(o) >= 1, o
    return t.replace(o, n)


def _jarr(xs):
    return "new String[] { " + ", ".join('"%s"' % x for x in xs) + " }"


CL = _sub(CL, "json.dumps(MN52_MARK_ID)", "json.dumps(NC53_MARK_ID)")
CL = _sub(CL, "json.dumps(MN52_MARK)", "json.dumps(NC53_MARK)")
CL = re.sub(r"mn52\.addField\(CtField\.make\('public static final String\[\] KEYS = new String\[\] \{[^\n]*\n",
            lambda m: "mn52.addField(CtField.make('public static final String[] KEYS = %s;', mn52))\n" % _jarr([k for k, o, n in NC_KEYS]), CL, count=1)
CL = re.sub(r"mn52\.addField\(CtField\.make\('public static final String\[\] OLDS = new String\[\] \{[^\n]*\n",
            lambda m: "mn52.addField(CtField.make('public static final String[] OLDS = %s;', mn52))\n" % _jarr([o for k, o, n in NC_KEYS]), CL, count=1)
CL = re.sub(r"mn52\.addField\(CtField\.make\('public static final String\[\] NEWS = new String\[\] \{[^\n]*\n",
            lambda m: "mn52.addField(CtField.make('public static final String[] NEWS = %s;', mn52))\n" % _jarr([n for k, o, n in NC_KEYS]), CL, count=1)
assert CL.count("OLDS = new String[] { \"800\"") == 1 and CL.count('"perk.doubleDropMax" }') == 1, CL[:900]
CL = _sub(CL, "for _k, _o, _n in MN52_KEYS)", "for _k, _o, _n in NC53_KEYS)")
CL = _sub(CL, '''public static int idx(String k) {
  if (k == null) return -1;
  for (int i = 0; i < KEYS.length; i++) if (KEYS[i].equals(k)) return i;
  return -1;
}"""), mn52))''', '''public static int idx(String k) {
  if (k == null) return -1;
  for (int i = 0; i < KEYS.length; i++) if (KEYS[i].equals(k)) return i;
  return -1;
}"""), mn52))
# 0.4.53: OLDS[i] may list several spellings of the old default ("1.0|1") - exact text, trimmed
mn52.addMethod(CtNewMethod.make(J14(r"""
public static boolean oldHit(int i, String v) {
  if (v == null || i < 0 || i >= OLDS.length) return false;
  String[] o = OLDS[i].split("\\\\|");
  for (int j = 0; j < o.length; j++) if (o[j].equals(v)) return true;
  return false;
}"""), mn52))''')
CL = _sub(CL, "mig[i] = eff[i] != null && !multi[i] && eff[i].equals(OLDS[i]);", "mig[i] = eff[i] != null && !multi[i] && oldHit(i, eff[i]);")
CL = _sub(CL, "if (mig[i]) { rows.add(KEYS[i]); rows.add(OLDS[i]); rows.add(NEWS[i]); }", "if (mig[i]) { rows.add(KEYS[i]); rows.add(eff[i]); rows.add(NEWS[i]); }")
CL = _sub(CL, "@PKG@.CfgFile.value(l, k).trim().equals(OLDS[x2])", "oldHit(x2, @PKG@.CfgFile.value(l, k).trim())")
CL = _sub(CL, '"SkyySkills 0.4.52"', '"SkyySkills 0.4.53"')
CL = _sub(CL, "0.4.52 (less Mana; the file", "0.4.53 (no XP caps; the file")
CL = _sub(CL, "0.4.52 (less Mana)", "0.4.53 (no XP caps)")
CL = _sub(CL, "the 0.4.52 default is", "the 0.4.53 default is")
CL = _sub(CL, "before the 0.4.52 less Mana update", "before the 0.4.53 no XP caps update")
CL = _sub(CL, "updated for 0.4.52:", "updated for 0.4.53:")
CL = _sub(CL, "0.4.52 marker added", "0.4.53 marker added")
# review fix: an existing 0 on the four keys where 0 used to mean OFF (no fall XP / no perk Fortune / every grant refused) gets an INFO line
CL = _sub(CL, '''mn52.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.53";', mn52))''',
          '''mn52.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.53";', mn52))
mn52.addField(CtField.make('public static final String ZERO_NOTE = ",acro.fallXpMax,acro.fallMaxXpPerMinute,bridge.maxXpPerCall,perk.doubleDropMax,";', mn52))''')
CL = _sub(CL, ''' kept (an admin's value) - the 0.4.53 default is " + NEWS[i]);
''', ''' kept (an admin's value) - the 0.4.53 default is " + NEWS[i]);
    else if (eff[i] != null && !multi[i] && ZERO_NOTE.indexOf("," + KEYS[i] + ",") >= 0) kept.append(kept.length() > 0 ? "; " : "").append(KEYS[i] + "=0 kept - since 0.4.53 0 means NO CAP (it used to mean none / off); set a number to cap it");
''')
CL = CL.replace("mn52", "nc53")
assert "0.4.52" not in CL and "mn52" not in CL and "MN52" not in CL and "Mana" not in CL and "mana." not in CL, [l for l in CL.splitlines() if "52" in l or "ana" in l][:5]

# ---- Fa53Mig = Zo49Mig's code (block append of the lines a file lacks), one key; sets LvFloor.NEW_FARM when it added the line
_a = P.s.index('zo49.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(ZO_MARK_ID), zo49))')
_m = P.s.index('# pure text step. null = nothing to do; else { new text, String[] added keys }', _a)
_e = P.s.index('could not update xp.properties for 0.4.49', _m)
_e = P.s.index('}"""), zo49))\n', _e) + len('}"""), zo49))\n')
CL2 = '''fa53.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(FA53_MARK_ID), fa53))
fa53.addField(CtField.make("public static final String HEAD = %s;" % json.dumps("\\n".join(FA53_HEAD) + "\\n"), fa53))
fa53.addField(CtField.make('public static final String[] KEYS = new String[] { "levels.skill.Farming" };', fa53))
fa53.addField(CtField.make("public static final String[] VALS = new String[] { %s };" % json.dumps(FARM_LIST), fa53))
fa53.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.53";', fa53))
assert ("\\n" + DEFAULTS).count("\\nlevels.skill.Farming=" + FARM_LIST + "\\n") == 1 and DEFAULTS.count("\\n".join(FA53_HEAD)) == 1
''' + P.s[_m:_e]
CL2 = _sub(CL2, "zone ores + alloys XP", "Farming level list")
CL2 = _sub(CL2, "before the 0.4.49 zone ores XP update", "before the 0.4.53 Farming level list update")
CL2 = _sub(CL2, "(Mining XP for the zone ores, Smithing XP for their ingots and the alloys)", "(Farming's own level list levels.skill.Farming)")
CL2 = _sub(CL2, '''    @PKG@.CfgRows.atomicWrite(f, data);
''', '''    @PKG@.CfgRows.atomicWrite(f, data);
    if (added.length > 0) @PKG@.LvFloor.NEW_FARM = true;   // LvFloor (this start) keeps Farming's GENERAL-list level as the floor
''')
CL2 = CL2.replace("0.4.49", "0.4.53").replace("zo49", "fa53")
assert "zo49" not in CL2 and "0.4.49" not in CL2 and "zone" not in CL2 and "Mining XP" not in CL2, [l for l in CL2.splitlines() if "zone" in l or "49" in l][:5]

# ---- LvFloor I/O (after the migrations: CfgRows.atomicWrite exists)
LVF_IO = '''
# ---- LvFloor I/O (0.4.53): start(base) right after SkillCfg.load - read level-floors.properties, or (no file) scan every players/*.properties
# ONCE (read only) and write it: each rebirth-reset slot whose level is above min(levels.runCap, 50) (0 = 50). Farming: its GENERAL-list level
# when Fa53Mig added Farming's own list this start. A failure = WARN, no file (the next start scans again). Never rewritten.
lvf.addMethod(CtNewMethod.make(J14(r"""
public static int read(java.nio.file.Path f) throws Exception {
  java.util.Properties p = new java.util.Properties();
  java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
  try { p.load(in); } finally { in.close(); }
  int n = 0;
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    int sl = k.lastIndexOf('/');
    if (sl <= 0) continue;
    int s = @PKG@.SkillDefs.indexOf(k.substring(sl + 1));
    if (s < 0 || !@PKG@.SkillDefs.NAMES[s].equals(k.substring(sl + 1))) continue;
    String[] v = p.getProperty(k).trim().split(",", 3);
    if (v.length < 2) continue;
    try {
      long lv = Long.parseLong(v[0].trim());
      long tot = Long.parseLong(v[1].trim());
      if (lv < 1L || lv > 100000L || tot < 0L) continue;
      MAP.put(k.substring(0, sl) + "/" + s, new long[] { lv, tot });
      TX.put(k.substring(0, sl), v.length > 2 ? v[2].trim() : "");
      n++;
    } catch (Throwable t) { }
  }
  return n;
}"""), lvf))
lvf.addMethod(CtNewMethod.make(J14(r"""
public static String scanText() throws Exception {
  int rc = @PKG@.SkillDefs.RUN_CAP;
  int min = (rc > 0 && rc < 50) ? rc : 50;
  StringBuilder sb = new StringBuilder();
  sb.append("# SkyySkills 0.4.53 level floors (Skyy 2026-10-18: levels never lowered by the level cap) - written once, do not edit\\n");
  sb.append("# <profile key>/<skill>=<level>,<XP then>,<last rebirth then>: the cap stays at least that level (that XP or more, no rebirth since)\\n");
  java.nio.file.Path dir = @PKG@.SkillStore.DIR;
  if (dir == null || !java.nio.file.Files.isDirectory(dir, new java.nio.file.LinkOption[0])) return sb.toString();
  java.io.File[] fs = dir.toFile().listFiles();
  if (fs == null) throw new java.io.IOException("cannot list " + dir);
  java.util.Arrays.sort(fs);
  int files = 0;
  for (int i = 0; i < fs.length; i++) {
    String nm = fs[i].getName();
    if (!fs[i].isFile() || !nm.endsWith(".properties")) continue;
    String pk = nm.substring(0, nm.length() - 11);
    if (pk.length() == 0 || pk.indexOf('/') >= 0 || pk.indexOf('=') >= 0 || pk.indexOf(':') >= 0) continue;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = new java.io.FileInputStream(fs[i]);
    try { p.load(in); } finally { in.close(); }
    files++;
    String tx = String.valueOf(p.getProperty("rb.lastTx", "")).trim();
    if (tx.indexOf(',') >= 0 || tx.indexOf(92) >= 0) tx = "?";   // never in a real txid; "?" = never matches (no floor)
    for (int s = 0; s < @PKG@.SkillDefs.N; s++) {
      if (!@PKG@.SkillDefs.rebirthResets(s)) continue;
      long x = 0L;
      try { x = Long.parseLong(String.valueOf(p.getProperty(@PKG@.SkillDefs.NAMES[s], "0")).trim()); } catch (Throwable t) { x = 0L; }
      if (x <= 0L) continue;
      int lv = (s == @PKG@.SkillDefs.FARMING && NEW_FARM) ? @PKG@.SkillDefs.generalLevel(x) : @PKG@.SkillDefs.levelOf(s, x);
      if (lv <= min) continue;
      sb.append(pk).append('/').append(@PKG@.SkillDefs.NAMES[s]).append('=').append(lv).append(',').append(x).append(',').append(tx).append('\\n');
    }
  }
  SCANNED = files;
  return sb.toString();
}"""), lvf))
lvf.addMethod(CtNewMethod.make(J14(r"""
public static synchronized String start(java.nio.file.Path base) {
  MAP.clear();
  TX.clear();
  SCANNED = -1;
  try {
    FILE = base.resolve(NAME);
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return "level floors: " + read(FILE) + " kept level(s) read";
    String t = scanText();
    @PKG@.CfgRows.atomicWrite(FILE, t.getBytes("ISO-8859-1"));
    int n = read(FILE);
    String msg = "level floors (0.4.53, levels never lowered by the level cap " + @PKG@.SkillDefs.RUN_CAP + "): scanned " + SCANNED + " profile file(s), " + n + " level(s) above the cap kept in " + NAME;
    @PKG@.SkillCfg.info(msg);
    return msg;
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("level floors: could not scan / write " + NAME + " (levels above the cap may show capped until the next start scans again): " + t);
    return "";
  }
}"""), lvf))
'''
NC_JAVA = """
# ---- Nc53Mig (0.4.53, PROJECT-RULES section 4; a clone of Mn52Mig's reviewed machinery + several old spellings per key): ONCE on an EXISTING
# xp.properties, setup() right after Mn52Mig.run, BEFORE SkillCfg.load. The 11 XP / double drop caps: when a key's LAST entry is a one-line
# entry holding exactly an old default (OLDS, '|' separated) -> 0; any other value kept (INFO; a line already at 0 is not reported); no line =
# nothing. The marker at the end; config-history copy first; one config-changes.log line per change (Undo); Properties check; atomicWrite.
""" + CL + """
# ---- Fa53Mig (0.4.53; a clone of Zo49Mig's reviewed block-append machinery): ONCE on an EXISTING xp.properties, setup() right after
# Nc53Mig.run, BEFORE SkillCfg.load: ONE block (the marker head + levels.skill.Farming) appended after the last line in the file's own line
# ending when the file has no levels.skill.Farming line (an admin's own one is kept); no existing line changes (Properties check);
# config-history copy first; atomicWrite; one INFO line. A failure = WARN, file untouched, retried next start.
""" + CL2 + LVF_IO
P.rep('''
# ================= SkillIO.run (0.4.32 C): the SkyySkills-IO jobs''', NC_JAVA + '''
# ================= SkillIO.run (0.4.32 C): the SkyySkills-IO jobs''')
P.rep('''  {PKG}.Mn52Mig.run();        // 0.4.52: untouched class Mana per level + Mana regen defaults -> the lower 0.4.52 ones, once; History first
  String rules = {PKG}.SkillCfg.load();
''', '''  {PKG}.Mn52Mig.run();        // 0.4.52: untouched class Mana per level + Mana regen defaults -> the lower 0.4.52 ones, once; History first
  {PKG}.Nc53Mig.run();        // 0.4.53: untouched XP caps + perk.doubleDropMax -> 0 (no cap), once; History first
  {PKG}.Fa53Mig.run();        // 0.4.53: Farming's own level list into an existing xp.properties, once; History first
  String rules = {PKG}.SkillCfg.load();
  {PKG}.LvFloor.start(base);  // 0.4.53: levels above the first-run cap that players already have - recorded once, never lowered
''')
P.rep('''          rbcm, snd39, rbs39, pd44, fm48, zo49, fl50, mn52, ob50,''', '''          rbcm, snd39, rbs39, pd44, fm48, zo49, fl50, mn52, nc53, fa53, lvf, ob50,''')
P.rep('''assert len(CFG_ROWS) == 275, ("''', '''assert len(CFG_ROWS) == 277, ("0.4.53: + levels.runCap, levels.capMax; ''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
print("wrote SkyySkills/build_skyyskills_0.4.53.py (%d changes)" % len(P.changes))
for _r in RATES:
    print("rates Lv %2d: Mining %.2f, Foraging %.3f, Farming %.4f -> %.2f levels an hour" % _r)
