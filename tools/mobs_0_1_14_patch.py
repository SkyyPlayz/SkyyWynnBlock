"""Derive SkyyMobs/build_skyymobs_0.1.14.py from the GENERATED 0.1.13 (build_skyymobs_0.1.13.py = the tools/deploy_set.py SET pin, made by
tools/mobs_0_1_13_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with 0.1.13
(tools/soundpass_gen.Patch); line endings kept.
Run:  python tools/mobs_0_1_14_patch.py   then   python SkyyMobs/build_skyymobs_0.1.14.py   then   python SkyyMobs/test_skyymobs_0.1.14.py
Edit THIS file, never the generated script (never --deploy).

0.1.14 (2026-10-20) = BALANCE PASS P4, the SkyyMobs part (research/Balance-P4-Combat-Spec.md Part 1 + 6.1-6.4; FULL round with SkyyGear 0.3.34,
  SkyySkills 0.4.58, SkyyClasses 0.1.44, SkyyArmory 0.1.42, SkyyTrees 0.4.4 - deploy and roll back TOGETHER). Skyy (2026-10-20 popup):
  "Combat bug ... Fix it?" -> "Fix it to the targets (Recommended)" + "keep going down the list. dont stop until the entire list is done";
  every other spec question takes its recommended default (docs/answered/classes.md 2026-10-20 P4 line).
  1. THE LEVEL CURVE ON THE P4 RULE (spec 1.2 / 1.4; tools/balance_model.py P4_TABLES = the spec's exact numbers, checked against the RULE
     there: health to 0.01, damage within 2.5 %): 21 points per table (Lv 1, 5, 10 ... 100) instead of 11; Lv 1-20 Normal health = 0.1.13's
     exactly; past Lv 20 Health x (F x material bonus x class perk)(L) / (the same at 20), damage x the player's EHP(L) / EHP(20), so a
     same-level fight takes the same hits at every level (0.1.13: 2-4x too fast from Zone 2 on, the gear curve was not re-banded). Easy = x0.6
     / x0.6, Normal x1.0 / x1.1, Hard x1.6 / x1.8 of the Normal line; Custom = a copy of Normal (0.1.13: of Hard).
  2. Health floor (strength.floor) 50 -> 70: trash takes ~4-5 hits with an expected kit (spec 1.2).
  3. Level gap (spec 1.6, "+5 hard, +10 a wall"): gap.free 5 -> 3, gap.dealtStep 2.5 -> 5 %, gap.takenStep 1.5 -> 3 %; dealtMin 40 / takenMax
     1.5 kept. (+5 levels about x1.8 as hard, +10 x4.3-4.8.)
  4. RANKS (spec 1.7, new Server Setup tab Mobs -> Ranks, 10 rows, all live): elites (rank.elite.roles "*_Elite*, *Captain*, *Champion*,
     *Alpha*, *Brute*" + any band-levelled mob rolls elite rank.elite.chance 3 % with rank.elite.levels +3 - the roll is fixed per mob UUID, so
     a reload keeps it) x3 Health / x1.5 damage; mini bosses (rank.mini.roles, empty, + mob:fn:setLevel's optional 5th argument "mini") x10 /
     x2; full bosses (the Boss roles row) get rank.boss.base 4500 Health before the level curve (their own base replaced, so every boss lasts
     about the same) and x2 damage. The rank goes after the level curve and before the level gap; One hit at most (35 %) stays last. The
     nameplate says "Elite" / "Mini Boss" in front of the name. Fixed level by role (scale.role) gets a 3rd column Damage x (old 2-column
     lines work). Defaults (exact ids - the kit refuses * entries): Trork_Chieftain Lv 18, the 4 Goblin_Duke phases Lv 38, Dragon_Frost Lv 78,
     Dragon_Fire Lv 98 (x1 / x1). The built-in list gains the elite skeletons (Skeleton_Elite, Skeleton_Elite_Phase_2: band level + rank);
     Never level these (levels.exclude) loses the four vanilla boss / elite patterns (Goblin_Duke*, Trork_Chieftain, Dragon_*,
     Skeleton_Elite*) - *_Boss* stays (it guards other mods' bosses, review F1).
  5. mob:fn:info: hpMult and dmgMult include the rank + the role's Damage x; xpMult = min(1, health share) x min(rank Health x, 10) (bosses
     at most x10 of a same-level kill); a 7th entry String rank ("", "elite", "mini", "boss"). The health share keeps 0.1.13's kill XP: the
     reference is the P4 Normal default divided by 0.1.12's Normal / Hard share (P3's numbers stay; Hard = 1, Easy x0.6).
  6. ONE-TIME UPDATE MobMigP4 (PROJECT-RULES 4; MobMig12's reviewed edit / curveEdit text steps copied, MobMig.mgKit / mgSaved, MobMig12.same
     / fileIdx): ONCE on an existing config.properties, setup() right after MobMig12, BEFORE MobCfg.load. A key whose LAST entry is a one-line
     entry holding exactly its 0.1.13 default moves (strength.floor 50, gap.free 5, gap.dealtStep 2.5, gap.takenStep 1.5, levels.exclude);
     an admin's own value is kept (INFO); a curve table moves WHOLE only while every point is its 0.1.13 default; the old Fixed level by role
     comment line -> the 3-column one; then ONE block at the end in the file's own line ending: the default scale.role rows the file has no
     line for, the rank.* rows it lacks, the run-once marker. A verified config-history copy first, one config-changes.log line per change
     (Undo in Server Setup -> Changes), a java.util.Properties check (only the planned keys differ), atomicWrite; a fresh file carries the
     marker. Skyy's NewBetaTest: every curve table, floor 50, the gap rows and levels.exclude are untouched -> all move.
SAVED DATA: none besides that one config update. Mobs already spawned keep their level; the new tables reach them at once (live
re-apply, Health share kept). One new class MobMigP4; no new command, system or bridge key (asserted).
ROLLBACK 0.1.14 -> 0.1.13: only TOGETHER with SkyyGear 0.3.33 (the old gear curves) - 0.1.13 reads the migrated rows as admin values (21-point
tables, floor 70, the gap rows, the boss rows): Undo them in Server Setup -> Changes first, or restore config-history/... (the copy MobMigP4 made).
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.13.py"), os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.14.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.1.13"') and P.s.startswith('"""SkyyMobs 0.1.13 - build script'), "build_skyymobs_0.1.13.py is not the SET pin 0.1.13"
assert "0.1.14" not in P.s
SYS0, CMD0, PUT0, CLS0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count("bridge().put("), P.s.count("makeClass(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.14 (2026-10-20)"):].rstrip() + "\n\n"

# ================================================================================================================ header + version
P.rep('''"""SkyyMobs 0.1.13 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_13_patch.py from the SET pin 0.1.12 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.13.py -> SkyyMobs/SkyyMobs-0.1.13.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.13.py   (--static: the text checks only)

''', '''"""SkyyMobs 0.1.14 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_14_patch.py from the SET pin 0.1.13 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.14.py -> SkyyMobs/SkyyMobs-0.1.14.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.14.py

''' + NOTE + '''0.1.13 (the base, everything below is still true unless 0.1.14 above says otherwise):
''')
P.rep('VERSION = "0.1.13"', 'VERSION = "0.1.14"')

# ================================================================================================================ 2. the floor 50 -> 70
P.rep('''assert floor_hp(36, 6.0, 1) == 50.0 and floor_hp(74, 6.0, 1) == 74.0, "Lv 1: a 36-HP mob is lifted to 50, a 74-HP mob keeps 74"
''', '''assert floor_hp(36, 6.0, 1) == 50.0 and floor_hp(74, 6.0, 1) == 74.0, "Lv 1: a 36-HP mob is lifted to 50, a 74-HP mob keeps 74"
# 0.1.14 (Balance P4 1.2): strength.floor 50 -> 70 (trash = 4-5 hits with an expected kit); the checks above keep 0.1.2's 50
FLOOR_013 = FLOOR_DEF
FLOOR_DEF = 70
assert floor_hp(36, 6.0, 1, floor=FLOOR_DEF) == 70.0 and floor_hp(74, 6.0, 1, floor=FLOOR_DEF) == 74.0 and FLOOR_013 == 50
''')

# ================================================================================================================ 3. the level gap
P.rep('''GAP_DEF = {"free": 5, "dealtStep": 2.5, "dealtMin": 40.0, "takenStep": 1.5, "takenMax": 1.5}''',
      '''GAP_DEF_013 = {"free": 5, "dealtStep": 2.5, "dealtMin": 40.0, "takenStep": 1.5, "takenMax": 1.5}   # 0.1.4 - 0.1.13 (what MobMigP4 moves)
# 0.1.14 (Balance P4 1.6, "+5 hard, +10 a wall"): free 3, -5 % your damage / +3 % its damage a level past it; floor 40 % / cap x1.5 kept
GAP_DEF = {"free": 3, "dealtStep": 5.0, "dealtMin": 40.0, "takenStep": 3.0, "takenMax": 1.5}''')

# ================================================================================================================ 4. scale.role: 3 columns
P.rep('''ROLE_DOC = ("# Fixed level by role (Server Setup -> Mobs -> Which mobs): lines scale.role.<role id> with <level>,<health x> - that mob always "
            "gets this level (beats Never level these), health x on top; level 0 is off. None by default.")''',
      '''ROLE_DOC_013 = ("# Fixed level by role (Server Setup -> Mobs -> Which mobs): lines scale.role.<role id> with <level>,<health x> - that mob always "
                "gets this level (beats Never level these), health x on top; level 0 is off. None by default.")
# 0.1.14 (Balance P4 1.7): a 3rd column Damage x; the vanilla bosses get rows by default (MobMigP4 swaps the exact old comment line)
ROLE_DOC = ("# Fixed level by role (Server Setup -> Mobs -> Which mobs): lines scale.role.<role id> with <level>,<health x>,<damage x> - that "
            "mob always gets this level (beats Never level these), health x and damage x on top; level 0 is off.")''')

# ================================================================================================================ 1. the P4 tables
P.rep('''assert CURVES[("hp", "hard")][-1] == (100, 35.07) and CURVES[("dmg", "hard")][-1] == (100, 10.19), (CURVES[("hp", "hard")][-1], CURVES[("dmg", "hard")][-1])
''', '''assert CURVES[("hp", "hard")][-1] == (100, 35.07) and CURVES[("dmg", "hard")][-1] == (100, 10.19), (CURVES[("hp", "hard")][-1], CURVES[("dmg", "hard")][-1])
# 0.1.14 (Balance P4, research/Balance-P4-Combat-Spec.md 1.2 / 1.4): THE RULE - tools/balance_model.py P4_TABLES are the spec's exact numbers,
# checked there against the RULE (p4_table_problems: health to 0.01, damage within 2.5 %); Custom = a copy of Normal. CURVES_012 = the
# 0.1.12 / 0.1.13 tables (MobMigP4 moves a file's table only while it is exactly that; MobMig12's own constants keep using them).
import balance_model as BM
CURVES_012 = CURVES
CURVE_DEF_TEXT_012 = CURVE_DEF_TEXT
assert not BM.p4_table_problems(), BM.p4_table_problems()
CURVES = dict(((_k, _d), BM.p4_table(_k, _d)) for _k, _d in CURVE_IDX)
CURVE_DEF_TEXT = [",".join("%d:%s" % (a, num(b)) for a, b in CURVES[kd]) for kd in CURVE_IDX]
for _kd, _p in CURVES.items():
    assert [a for a, _b in _p] == BM.P4_LEVELS and all(_p[i][1] < _p[i + 1][1] for i in range(len(_p) - 1)), _kd
    assert all(0.1 <= _b <= 1000 for _a, _b in _p), _kd
for _k in CURVE_KINDS:
    assert CURVES[(_k, "custom")] == CURVES[(_k, "normal")], "0.1.14: Custom = a copy of Normal (spec 1.4)"
    for _i in range(len(BM.P4_LEVELS)):
        assert CURVES[(_k, "easy")][_i][1] <= CURVES[(_k, "normal")][_i][1] <= CURVES[(_k, "hard")][_i][1]
for _L in range(1, 21):          # Lv 1-20: the Normal health line is 0.1.13's (Zone 1 unchanged)
    assert abs(curve_eval(CURVES[("hp", "normal")], _L) - curve_eval(CURVES_012[("hp", "normal")], _L)) <= 0.0051, _L
    assert abs(curve_eval(CURVES[("dmg", "normal")], _L) - 1.1 * curve_eval(CURVES_012[("dmg", "normal")], _L)) <= 0.0051, _L
for _L in range(1, 101):
    assert curve_eval(CURVES[("hp", "normal")], _L) < curve_eval(CURVES[("hp", "normal")], _L + 1) or _L == 100
# the kill XP share reference (MobCfg.hardRef in curve shape): the P4 Normal default / 0.1.12's Normal-to-Hard share -> Normal pays 0.1.13's
P4_SHARE_N, P4_SHARE_H = CURVE_DEF_TEXT_012[CURVE_IDX.index(("hp", "normal"))], CURVE_DEF_TEXT_012[CURVE_IDX.index(("hp", "hard"))]
P4_REF_N = CURVE_DEF_TEXT[CURVE_IDX.index(("hp", "normal"))]
print("0.1.14 Level curve (Balance P4): 21 points a table; Normal Lv 20 / 40 / 60 / 80 / 100 health x%s / x%s / x%s / x%s / x%s (0.1.13 x%s / x%s / x%s / x%s / x%s)"
      % tuple([num(curve_eval(CURVES[("hp", "normal")], _L)) for _L in (20, 40, 60, 80, 100)] + [num(round(curve_eval(CURVES_012[("hp", "normal")], _L), 2)) for _L in (20, 40, 60, 80, 100)]))
''')
# MobMig12's constants keep the 0.1.12 tables (its K_NEW = the stretch)
P.rep('''    _nm = dict((a, num(b)) for a, b in CURVES[_kd])''', '''    _nm = dict((a, num(b)) for a, b in CURVES_012[_kd])   # 0.1.14: MobMig12 keeps moving 0.1.11 -> 0.1.12 (MobMigP4 then -> P4)''')
P.rep('''    MG12_K.append((_pf, "|".join("%d=%s" % (a, num(b)) for a, b in CURVES_011[_kd]), "|".join("%d=%s" % (a, num(b)) for a, b in CURVES[_kd]),
                   "|".join("%s%d=%s" % (_pf, a, num(b)) for a, b in CURVES[_kd]), "|".join(_lg)))''',
      '''    MG12_K.append((_pf, "|".join("%d=%s" % (a, num(b)) for a, b in CURVES_011[_kd]), "|".join("%d=%s" % (a, num(b)) for a, b in CURVES_012[_kd]),
                   "|".join("%s%d=%s" % (_pf, a, num(b)) for a, b in CURVES_012[_kd]), "|".join(_lg)))''')

# ================================================================================================================ 4. elites built in, the exclude row
P.rep('''assert len(LEVELLED) == 280, "0.1.6: the built-in list on the 0.7.0 Assets.zip is 280 roles (293 - 13 NOT_BUILTIN), got %d" % len(LEVELLED)
''', '''assert len(LEVELLED) == 280, "0.1.6: the built-in list on the 0.7.0 Assets.zip is 280 roles (293 - 13 NOT_BUILTIN), got %d" % len(LEVELLED)
# 0.1.14 (Balance P4 1.7): the elite skeletons get a band level (+ their Elite rank); Never level these loses the four vanilla boss / elite
# patterns (bosses get their level from Fixed level by role now); *_Boss* stays - it is the guard for OTHER mods' bosses (review F1)
P4_ELITES = sorted(_n for _n in FIGHTERS if matches(["Skeleton_Elite*"], _n) and not _n.startswith("Template_"))
assert P4_ELITES == ["Skeleton_Elite", "Skeleton_Elite_Phase_2"], P4_ELITES
LEVELLED = sorted(set(LEVELLED) | set(P4_ELITES))
LEVELLED_TEXT = ",".join(LEVELLED)
_lev_low = set(n.lower() for n in LEVELLED)
EXCLUDE_013 = EXCLUDE_DEF
EXCLUDE_DEF = ",".join(["Test_*", "Tamed_*", "Temple_*", "*_Merchant*", "Risen_*"] + GUARDS)
_excl = EXCLUDE_DEF.split(",")
assert EXCLUDE_013 == "Test_*,Tamed_*,Temple_*,*_Merchant*,Risen_*,Goblin_Duke*,Trork_Chieftain,Dragon_*,Skeleton_Elite*,*_Mount*,*_Pet*,*_Boss*,*NPC*,*_Hub*,*Blacksmith*,*Trader*"
assert "*_Boss*" in _excl and not [p for p in BOSSES if p in _excl], EXCLUDE_DEF
assert len(LEVELLED) == 282 and levelled("Skeleton_Elite") and not levelled("Trork_Chieftain") and not levelled("Goblin_Duke") and not levelled("Dragon_Fire")
for _o in OTHER_MOD_ROLES:
    assert not levelled(_o) and not levelled(_o, OLD_PREFIXES), "0.1.14: another mod's mount / pet / NPC / boss would get a level: " + _o
# the vanilla bosses' Fixed level rows (spec 1.7: zone tops Lv 20 / 40 / 80 / 100 minus 2; exact ids - the kit refuses * entries)
P4_BOSS_LEVELS = [("Trork_Chieftain", 18), ("Goblin_Duke", 38), ("Goblin_Duke_Phase_2", 38), ("Goblin_Duke_Phase_3_Fast", 38),
                  ("Goblin_Duke_Phase_3_Slow", 38), ("Dragon_Frost", 78), ("Dragon_Fire", 98)]
assert all(_r in ROLES for _r, _l in P4_BOSS_LEVELS) and all(matches(BOSS_PATS, _r) for _r, _l in P4_BOSS_LEVELS), "0.1.14: a boss row names no vanilla boss"
P4_ROLE_ROWS = [("scale.role." + _r, "%d,1,1" % _l) for _r, _l in P4_BOSS_LEVELS]
# the Ranks rows (spec 1.7): (key, default, Server Setup label, type, min, max, unit, help)
P4_ELITE_DEF = "*_Elite*, *Captain*, *Champion*, *Alpha*, *Brute*"
P4_RANK_ROWS = [
    ("rank.elite.roles", P4_ELITE_DEF, "Elite roles", "text", "", "2000", "", "Role ids or Prefix* / *Part* patterns that are always elites."),
    ("rank.elite.hp", "3", "Elite Health x", "dec", "1", "100", "x", "An elite's Health x this on top of its level (Skyy: 3x)."),
    ("rank.elite.dmg", "1.5", "Elite damage x", "dec", "1", "100", "x", "An elite's hits x this on top of its level (Skyy: 1.5x)."),
    ("rank.elite.chance", "3", "Elite chance", "dec", "0", "100", "%", "Any band-levelled mob is an elite this often (fixed per mob). 0 = only the roles."),
    ("rank.elite.levels", "3", "Elite extra levels", "int", "0", "20", "", "A rolled elite spawns this many levels above its band roll."),
    ("rank.mini.roles", "", "Mini boss roles", "text", "", "2000", "", "Role ids or patterns that are mini bosses (other mods can ask for one too)."),
    ("rank.mini.hp", "10", "Mini boss Health x", "dec", "1", "100", "x", "A mini boss's Health x this on top of its level (Skyy: 10x)."),
    ("rank.mini.dmg", "2", "Mini boss damage x", "dec", "1", "100", "x", "A mini boss's hits x this on top of its level (Skyy: 2x)."),
    ("rank.boss.base", "4500", "Boss Health before levels", "int", "1", "1000000", "", "Every Boss roles mob gets this base Health (x the level curve), about 3.5 min solo."),
    ("rank.boss.dmg", "2", "Boss damage x", "dec", "1", "100", "x", "A full boss's hits x this on top of its level."),
]
P4_RANK_DOC = ["# Ranks (SkyyMobs 0.1.14, Balance P4): elites / mini bosses get Health x and damage x on top of their level; a full boss (Boss roles)",
               "# gets rank.boss.base Health before the level curve. In game: Server Setup > Mobs > Ranks."]
''')

# ================================================================================================================ the fresh default file
P.rep('''    ROLE_DOC,           # 0.1.4: scale.role (Fixed level by role) - no entries by default; MobMig14 puts this line after levels.max
''', '''    ROLE_DOC,           # 0.1.4: scale.role (Fixed level by role) - no entries by default; MobMig14 puts this line after levels.max
] + ["%s=%s" % _kv for _kv in P4_ROLE_ROWS] + [      # 0.1.14: the vanilla bosses' rows (MobMigP4 appends the missing ones to an old file)
''')
P.rep('''    MG12_MARK,          # 0.1.12: the fresh file carries MobMig12's run-once marker (never migrated)
]
CFG_TEXT = "\\n".join(CFG_LINES) + "\\n"''', '''    MG12_MARK,          # 0.1.12: the fresh file carries MobMig12's run-once marker (never migrated)
] + P4_RANK_DOC + ["%s=%s" % (_r[0], _r[1]) for _r in P4_RANK_ROWS] + [MGP4_MARK]   # 0.1.14: the Ranks rows + MobMigP4's run-once marker
CFG_TEXT = "\\n".join(CFG_LINES) + "\\n"''')
P.rep('''assert CFG_TEXT.index("levels.max=100\\n" + ROLE_DOC + "\\n") > 0 and sum(1 for ln in CFG_LINES if ln.startswith("curve.")) == 88   # 0.1.12: 8 x 11 points''',
      '''assert CFG_TEXT.index("levels.max=100\\n" + ROLE_DOC + "\\n") > 0 and sum(1 for ln in CFG_LINES if ln.startswith("curve.")) == 168   # 0.1.14: 8 x 21 points
assert CFG_TEXT.count(MGP4_MARK_ID) == 1 and "\\nstrength.floor=70\\n" in CFG_TEXT and "\\ngap.free=3\\n" in CFG_TEXT and "\\nscale.role.Dragon_Fire=98,1,1\\n" in CFG_TEXT''')
# the marker (defined with the other 0.1.12 markers, before the default file)
P.rep('''MG12_MARK_ID = "SkyyMobs 0.1.12 level bands update"''', '''MG12_MARK_ID = "SkyyMobs 0.1.12 level bands update"
# 0.1.14: MobMigP4's run-once marker (fresh file + every updated file), History title, change-log name
MGP4_MARK_ID = "Balance P4 combat (SkyyMobs 0.1.14)"
MGP4_MARK = "# %s (2026-10-20): Level curve on the P4 rule, floor 70, level gap 3 / 5 / 3, ranks, boss levels - research/Balance-P4-Combat-Spec.md" % MGP4_MARK_ID
MGP4_WHO = "SkyyMobs 0.1.14"
MGP4_WHAT = "before the 0.1.14 Balance P4 combat update"
assert "=" not in MGP4_MARK and all(32 <= ord(_c) < 127 for _c in MGP4_MARK) and '"' not in MGP4_MARK and "@" not in MGP4_MARK''')

# ================================================================================================================ MobInfo + MobCfg fields
P.rep('''          "public volatile double base;", "public volatile double rx;"):
    F(mi, f)
C(mi, "public MobInfo() { this.base = -1.0; this.rx = 1.0; }")''', '''          "public volatile double base;", "public volatile double rx;",
          # 0.1.14 (Balance P4 1.7): the damage x on its hits (role Damage x x rank damage), the rank (0 none, 1 elite, 2 mini boss, 3 boss)
          # and whether the level came from a band roll (only those may roll elite)
          "public volatile double dx;", "public volatile int rank;", "public volatile boolean rolled;"):
    F(mi, f)
C(mi, "public MobInfo() { this.base = -1.0; this.rx = 1.0; this.dx = 1.0; this.rank = 0; this.rolled = false; }")''')
P.rep('''          "public static volatile String[] P_BOSS;", "public static volatile int[] BOSS_TOP;"):
    F(cfg, f)''', '''          "public static volatile String[] P_BOSS;", "public static volatile int[] BOSS_TOP;"):
    F(cfg, f)
# 0.1.14 (Balance P4 1.7): the Ranks rows + what derive makes of them; RANKFIX = mob UUID -> Integer rank another mod asked for
# (mob:fn:setLevel's 5th argument; dropped when the mob dies); the kill XP reference (hardRef, curve shape)
for f in ("public static volatile String RANK_ELITE_ROLES = %s;" % jstr(P4_ELITE_DEF), "public static volatile double RANK_ELITE_HP = 3.0;",
          "public static volatile double RANK_ELITE_DMG = 1.5;", "public static volatile double RANK_ELITE_CHANCE = 3.0;",
          "public static volatile int RANK_ELITE_LEVELS = 3;", 'public static volatile String RANK_MINI_ROLES = "";',
          "public static volatile double RANK_MINI_HP = 10.0;", "public static volatile double RANK_MINI_DMG = 2.0;",
          "public static volatile int RANK_BOSS_BASE = 4500;", "public static volatile double RANK_BOSS_DMG = 2.0;",
          "public static volatile String[] P_ELITE;", "public static volatile String[] P_MINI;",
          "public static final java.util.concurrent.ConcurrentHashMap RANKFIX = new java.util.concurrent.ConcurrentHashMap();",
          "public static final String SHARE_N = %s;" % jstr(P4_SHARE_N), "public static final String SHARE_H = %s;" % jstr(P4_SHARE_H),
          "public static final String REF_N = %s;" % jstr(P4_REF_N), "public static volatile Object[] REF_PTS;"):
    F(cfg, f)''')

# ================================================================================================================ the Server Setup rows
P.rep('''    ("scale.role", "Fixed level by role", "levels", "table", "", "0", "1000", "int|dec;none;Level|Health x", "", "live,danger",
     "Bosses / special mobs: always this level (beats Never level these), Health x on top. 0 = off.",''',
      '''    ("scale.role", "Fixed level by role", "levels", "table", "", "0", "1000", "int|dec|dec;none;Level|Health x|Damage x", "", "live,danger",
     "Bosses / special mobs: always this level (beats Never level these), Health x + damage x on top.",''')
P.rep('''assert [c for c, _l in CFG_CATS] == ["levels", "strength", "curve", "gap", "bands", "plate"], "0.1.4 = 0.1.3's tabs + Level curve + Level gap"
''', '''assert [c for c, _l in CFG_CATS] == ["levels", "strength", "curve", "gap", "bands", "plate"], "0.1.4 = 0.1.3's tabs + Level curve + Level gap"
# 0.1.14 (Balance P4 1.7): the Ranks tab right after Level gap, its 10 rows (every edit re-applies the loaded mobs' Health through derive)
CFG_CATS.insert(CFG_CATS.index(("gap", "Level gap")) + 1, ("rank", "Ranks"))
_RF = {"rank.elite.roles": "RANK_ELITE_ROLES", "rank.elite.hp": "RANK_ELITE_HP", "rank.elite.dmg": "RANK_ELITE_DMG", "rank.elite.chance": "RANK_ELITE_CHANCE",
       "rank.elite.levels": "RANK_ELITE_LEVELS", "rank.mini.roles": "RANK_MINI_ROLES", "rank.mini.hp": "RANK_MINI_HP", "rank.mini.dmg": "RANK_MINI_DMG",
       "rank.boss.base": "RANK_BOSS_BASE", "rank.boss.dmg": "RANK_BOSS_DMG"}
CFG_ROWS += [(_k, _lab, "rank", _ty, _d, _lo, _hi, "", _u, "live" if _ty != "text" else "live", _h, "field:MobCfg.%s;after=MobCfg.derive" % _RF[_k])
             for _k, _d, _lab, _ty, _lo, _hi, _u, _h in P4_RANK_ROWS]
_bad4 = ["%s help %d" % (r[0], len(r[10])) for r in CFG_ROWS if len(r[10]) > 100] + ["%s label %d" % (r[0], len(r[1])) for r in CFG_ROWS if len(r[1]) > 40]
assert not _bad4, _bad4
for _r in CFG_ROWS:
    if _r[0].startswith("rank."):
        assert _dp.get(_r[0]) == _r[4], "0.1.14: default file and row default differ: " + _r[0]
assert [c for c, _l in CFG_CATS] == ["levels", "strength", "curve", "gap", "rank", "bands", "plate"]
''')
P.rep('''_entries = {"bands.biome": len(BIOME_ROWS), "bands.env": len(ENV_ROWS), "bands.world": 0, "bands.zone": len(ZONE_ROWS),
            "plate.colors": len(COLOR_ROWS), "scale.role": 0}''', '''_entries = {"bands.biome": len(BIOME_ROWS), "bands.env": len(ENV_ROWS), "bands.world": 0, "bands.zone": len(ZONE_ROWS),
            "plate.colors": len(COLOR_ROWS), "scale.role": len(P4_ROLE_ROWS)}''')
# the 0.1 / 0.1.4 negative controls measure with the 0.1.4 tab list (the Ranks tab does not change what they test)
P.rep('''_old_bad, _old = menu_fit(_old_rows, [("levels", "Who gets levels")] + CFG_CATS[1:], CFG_TITLE, "0.1", CFG_NOTE, [CFG_FILE, BANDS_FILE], _entries)''',
      '''_old_bad, _old = menu_fit([r for r in _old_rows if not r[0].startswith("rank.")], [("levels", "Who gets levels")] + [c for c in CFG_CATS[1:] if c[0] != "rank"], CFG_TITLE, "0.1", CFG_NOTE, [CFG_FILE, BANDS_FILE], _entries)''')

# ================================================================================================================ MobCfg: roles 3rd column, ranks, apply, derive
P.rep('''  java.util.ArrayList raw = new java.util.ArrayList();
  int[] lv = new int[ks.length];
  double[] hx = new double[ks.length];
  int n = 0;''', '''  java.util.ArrayList raw = new java.util.ArrayList();
  int[] lv = new int[ks.length];
  double[] hx = new double[ks.length];
  double[] dxx = new double[ks.length];   // 0.1.14: the 3rd column Damage x (default 1)
  int n = 0;''')
P.rep('''      double x = (parts.length > 1 && parts[1].trim().length() > 0) ? Double.parseDouble(parts[1].trim()) : 1.0;
      if (e.length() == 0 || l < 0 || l > 100 || Double.isNaN(x) || x < 0.1 || x > 100.0) throw new IllegalArgumentException("out of range");
      if (l == 0) continue;
      raw.add(e); lv[n] = l; hx[n] = x; n++;
      sig.append(e.toLowerCase()).append('=').append(l).append(',').append(x).append(';');''',
      '''      double x = (parts.length > 1 && parts[1].trim().length() > 0) ? Double.parseDouble(parts[1].trim()) : 1.0;
      double dx = (parts.length > 2 && parts[2].trim().length() > 0) ? Double.parseDouble(parts[2].trim()) : 1.0;
      if (e.length() == 0 || l < 0 || l > 100 || Double.isNaN(x) || x < 0.1 || x > 100.0 || Double.isNaN(dx) || dx < 0.1 || dx > 100.0) throw new IllegalArgumentException("out of range");
      if (l == 0) continue;
      raw.add(e); lv[n] = l; hx[n] = x; dxx[n] = dx; n++;
      sig.append(e.toLowerCase()).append('=').append(l).append(',').append(x).append(';');''')
P.rep('''      @PKG@.MobLog.warnOnce("role:" + ks[i] + "=" + v, "scale.role: skipped the line " + ks[i] + "=" + v + " (needs <level 0-100>,<health x 0.1-100>)");
    }
  }
  String[] r = new String[n], lo = new String[n];
  int[] rl = new int[n];
  double[] rx = new double[n];
  for (int i = 0; i < n; i++) { r[i] = (String) raw.get(i); lo[i] = r[i].toLowerCase(); rl[i] = lv[i]; rx[i] = hx[i]; }
  ROLES_TAB = new Object[] { r, lo, rl, rx };''', '''      @PKG@.MobLog.warnOnce("role:" + ks[i] + "=" + v, "scale.role: skipped the line " + ks[i] + "=" + v + " (needs <level 0-100>,<health x 0.1-100>[,<damage x 0.1-100>])");
    }
  }
  String[] r = new String[n], lo = new String[n];
  int[] rl = new int[n];
  double[] rx = new double[n];
  double[] rd = new double[n];
  for (int i = 0; i < n; i++) { r[i] = (String) raw.get(i); lo[i] = r[i].toLowerCase(); rl[i] = lv[i]; rx[i] = hx[i]; rd[i] = dxx[i]; }
  ROLES_TAB = new Object[] { r, lo, rl, rx, rd };''')
P.rep('''M(cfg, r"""
public static String roleKey(String role) {''', '''# 0.1.14: the scale.role Damage x (3rd column; 1 = none or an old 2-column line)
M(cfg, r"""
public static double roleDx(String role) {
  int i = roleIdx(role);
  Object[] t = ROLES_TAB;
  if (i < 0 || t == null || t.length < 5) return 1.0;
  return ((double[]) t[4])[i];
}""")
M(cfg, r"""
public static String roleKey(String role) {''')
P.rep('''  String sig = CURVE_ON ? "curve|" + diffIdx() + "|" + ptsText(curveOf(diffIdx())) + "|" + HP_FLOOR + "|" + ROLE_SIG
                        : "linear|" + HP_STEP + "|" + HP_CAP + "|" + HP_FLOOR + "|" + ROLE_SIG;''',
      '''  P_ELITE = @PKG@.MobGlob.list(RANK_ELITE_ROLES);   // 0.1.14: the Ranks rows (before the signature: an edit re-applies the loaded mobs)
  P_MINI = @PKG@.MobGlob.list(RANK_MINI_ROLES);
  String rsig = "|rank|" + RANK_ELITE_ROLES + "|" + RANK_ELITE_HP + "|" + RANK_ELITE_CHANCE + "|" + RANK_MINI_ROLES + "|" + RANK_MINI_HP + "|" + RANK_BOSS_BASE + "|" + BOSS_ROLES;
  String sig = CURVE_ON ? "curve|" + diffIdx() + "|" + ptsText(curveOf(diffIdx())) + "|" + HP_FLOOR + "|" + ROLE_SIG + rsig
                        : "linear|" + HP_STEP + "|" + HP_CAP + "|" + HP_FLOOR + "|" + ROLE_SIG + rsig;''')
P.rep('''  BOSS_TOPS = c.getProperty("bosses.zoneTops", BOSS_TOPS_DEF).trim();
  bosses(null);''', '''  BOSS_TOPS = c.getProperty("bosses.zoneTops", BOSS_TOPS_DEF).trim();
  bosses(null);
  RANK_ELITE_ROLES = c.getProperty("rank.elite.roles", @RKELITE@).trim();   // 0.1.14: the Ranks rows (a file without a line = its default)
  RANK_ELITE_HP = dec(c.getProperty("rank.elite.hp"), 3.0, 1.0, 100.0);
  RANK_ELITE_DMG = dec(c.getProperty("rank.elite.dmg"), 1.5, 1.0, 100.0);
  RANK_ELITE_CHANCE = dec(c.getProperty("rank.elite.chance"), 3.0, 0.0, 100.0);
  RANK_ELITE_LEVELS = intOf(c.getProperty("rank.elite.levels"), 3, 0, 20);
  RANK_MINI_ROLES = c.getProperty("rank.mini.roles", "").trim();
  RANK_MINI_HP = dec(c.getProperty("rank.mini.hp"), 10.0, 1.0, 100.0);
  RANK_MINI_DMG = dec(c.getProperty("rank.mini.dmg"), 2.0, 1.0, 100.0);
  RANK_BOSS_BASE = intOf(c.getProperty("rank.boss.base"), 4500, 1, 1000000);
  RANK_BOSS_DMG = dec(c.getProperty("rank.boss.dmg"), 2.0, 1.0, 100.0);''')
P.rep('''T["HITCAP"] = str(HITCAP_DEF)   # 0.1.11''', '''T["HITCAP"] = str(HITCAP_DEF)   # 0.1.11
T["RKELITE"] = '"' + P4_ELITE_DEF + '"'   # 0.1.14 (plain ASCII, no quotes / backslashes: asserted)
assert all(32 <= ord(_c) < 127 for _c in P4_ELITE_DEF) and chr(34) not in P4_ELITE_DEF and chr(92) not in P4_ELITE_DEF''')
# the rank maths (after capHit; MobCfg methods only - MobLevel's come later)
P.rep('''# 0.1.2: the floor factor max(1, floor / base) (1 when the floor is off or the base unknown) and the health amount = the 0.1.1 level''',
      '''# 0.1.14 (Balance P4 1.7): the elite roll, fixed per mob UUID (SplitMix64 like MobLevel.roll, its own salt): a reload keeps it
M(cfg, r"""
public static long mix64(long z) {
  z = (z ^ (z >>> 30)) * -4658895280553007687L;
  z = (z ^ (z >>> 27)) * -7723592293110705685L;
  return z ^ (z >>> 31);
}""")
M(cfg, r"""
public static boolean eliteRoll(java.util.UUID u) {
  double c = RANK_ELITE_CHANCE;
  if (u == null || !(c > 0.0)) return false;
  long h = mix64(u.getMostSignificantBits() ^ 6022176624127591935L);
  h = mix64(h ^ u.getLeastSignificantBits());
  return (double) Long.remainderUnsigned(h, 10000L) < c * 100.0;
}""")
# fix2 (critic: clear-all dropped live mobs' ranks): RANKFIX holds at most 2000; a full map drops one arbitrary entry (dead mobs leave
# through MobLevel.forget(unload=false), so a full map only means leaks)
M(cfg, r"""
public static void rankPut(java.util.UUID u, int rk) {
  if (u == null || rk <= 0) return;
  if (!RANKFIX.containsKey(u) && RANKFIX.size() >= 2000) {
    java.util.Iterator it = RANKFIX.keySet().iterator();
    if (it.hasNext()) { it.next(); it.remove(); }
  }
  RANKFIX.put(u, Integer.valueOf(rk));
}""")
# the rank of a mob: another mod's ask (RANKFIX) > a full boss (Boss roles) > Mini boss roles > Elite roles > the elite roll (band-levelled only)
M(cfg, r"""
public static int rankOf(String role, java.util.UUID u, boolean rolled) {
  if (u != null) {
    Object f = RANKFIX.get(u);
    if (f instanceof Integer) return ((Integer) f).intValue();
  }
  if (role == null) return 0;
  if (isBoss(role)) return 3;
  if (@PKG@.MobGlob.any(P_MINI, role)) return 2;
  if (@PKG@.MobGlob.any(P_ELITE, role)) return 1;
  if (rolled && eliteRoll(u)) return 1;
  return 0;
}""")
M(cfg, r"""
public static String rankWord(int r) {
  if (r == 1) return "elite";
  if (r == 2) return "mini";
  if (r == 3) return "boss";
  return "";
}""")
# the Health x of a rank on a mob of this base Health (a boss: its base replaced by rank.boss.base, the floor counted like hpAmount)
M(cfg, r"""
public static double rankHp(int r, double base) {
  if (r == 1) return RANK_ELITE_HP;
  if (r == 2) return RANK_MINI_HP;
  if (r == 3) {
    if (!(base > 0.0)) return 1.0;
    int f = HP_FLOOR;
    double b = (f > 0 && (double) f > base) ? (double) f : base;
    return (double) RANK_BOSS_BASE / b;
  }
  return 1.0;
}""")
M(cfg, r"""
public static double rankDmg(int r) {
  if (r == 1) return RANK_ELITE_DMG;
  if (r == 2) return RANK_MINI_DMG;
  if (r == 3) return RANK_BOSS_DMG;
  return 1.0;
}""")
# { Health x (scale.role x rank, 0.01-100000), damage x (scale.role Damage x x rank), rank } of a mob
M(cfg, r"""
public static double[] factors(String role, java.util.UUID u, double base, boolean rolled) {
  int r = rankOf(role, u, rolled);
  double hx = roleX(role) * rankHp(r, base);
  if (!(hx >= 0.01)) hx = 0.01;
  if (hx > 100000.0) hx = 100000.0;
  return new double[] { hx, roleDx(role) * rankDmg(r), (double) r };
}""")
# the kill XP reference in curve shape: the P4 Normal default / 0.1.12's Normal-to-Hard health share (so Normal pays 0.1.13's share)
M(cfg, r"""
public static double refCurve(double x) {
  Object[] p = REF_PTS;
  if (p == null) { p = new Object[] { parsePts(REF_N), parsePts(SHARE_N), parsePts(SHARE_H) }; REF_PTS = p; }
  double sn = eval((Object[]) p[1], x), sh = eval((Object[]) p[2], x);
  double share = sh > 0.0 ? sn / sh : 1.0;
  if (!(share > 0.0)) share = 1.0;
  return eval((Object[]) p[0], x) / share;
}""")
# 0.1.2: the floor factor max(1, floor / base) (1 when the floor is off or the base unknown) and the health amount = the 0.1.1 level''')
P.rep('''  if (CURVE_ON) {
    double c = eval(curveOf(2), (double) level);
    if (!(c >= 0.1)) c = 0.1;
    return (double) (float) c;
  }''', '''  if (CURVE_ON) {
    double c = refCurve((double) level);   // 0.1.14: the P4 Normal default / 0.1.12's share (was the Hard table: P3's kill XP stays)
    if (!(c >= 0.1)) c = 0.1;
    return (double) (float) c;
  }''')

# ================================================================================================================ MobLevel: apply, onAdd, forget, refresh
P.rep('''  int hi = @DST@.getHealth();
  double rx = @PKG@.MobCfg.roleX(role);
  setMult(m, hi, level, full, @PKG@.MobCfg.HEAL_ON_LOAD, rx);
  String name = nameFor(u, role, tkeyOf(npc));''', '''  int hi = @DST@.getHealth();
  boolean rolled = step != null && !step.equals("role") && !step.equals("set") && @PKG@.MobCfg.roleLevel(role) <= 0;   // 0.1.14
  double[] fx = @PKG@.MobCfg.factors(role, u, baseOf(m, hi), rolled);   // 0.1.14: scale.role x the rank (a boss: rank.boss.base)
  double rx = fx[0];
  setMult(m, hi, level, full, @PKG@.MobCfg.HEAL_ON_LOAD, rx);
  String name = nameFor(u, role, tkeyOf(npc));
  int rk = (int) fx[2];
  if (rk == 1) name = "Elite " + name;            // 0.1.14: the rank on the plate
  else if (rk == 2) name = "Mini Boss " + name;''')
P.rep('''  i.base = baseOf(m, hi); i.rx = rx;
  if (w != null) i.wref = new java.lang.ref.WeakReference(w);''', '''  i.base = baseOf(m, hi); i.rx = rx; i.dx = fx[1]; i.rank = rk; i.rolled = rolled;
  if (w != null) i.wref = new java.lang.ref.WeakReference(w);''')
P.rep('''    level = levelFor(res, seed, u, role);
    if (level <= 0) return;
    step = (String) res[3];''', '''    level = levelFor(res, seed, u, role);
    if (level <= 0) return;
    step = (String) res[3];
    if (@PKG@.MobCfg.rankOf(role, u, true) == 1 && !@PKG@.MobGlob.any(@PKG@.MobCfg.P_ELITE, role) && @PKG@.MobCfg.eliteRoll(u)) {   // 0.1.14: a rolled elite
      level = level + @PKG@.MobCfg.RANK_ELITE_LEVELS;
      if (level > @PKG@.MobCfg.MAX_LEVEL) level = @PKG@.MobCfg.MAX_LEVEL;
    }''')
P.rep('''  if (!unload) NAMEFIX.remove(u);   // 0.1.9: the mob died / was removed - its given name goes too (an unload keeps it)''',
      '''  if (!unload) { NAMEFIX.remove(u); @PKG@.MobCfg.RANKFIX.remove(u); }   // 0.1.9: the mob died / was removed - its given name goes too (an unload keeps it); 0.1.14: + its asked rank''')
P.rep('''      double rx = @PKG@.MobCfg.roleX(i.role);
      if (refreshOne(m, hi, i.level, rx)) n++;
      i.rx = rx;
      if (m != null) i.base = baseOf(m, hi);''', '''      double[] fx = @PKG@.MobCfg.factors(i.role, i.uuid, m == null ? -1.0 : baseOf(m, hi), i.rolled);   // 0.1.14: + the rank
      double rx = fx[0];
      if (refreshOne(m, hi, i.level, rx)) n++;
      i.rx = rx;
      i.dx = fx[1];
      i.rank = (int) fx[2];
      if (m != null) i.base = baseOf(m, hi);''')

# ================================================================================================================ LevelDamage + mob:fn:info + setLevel
P.rep('''    boolean lvd = i != null && i.level > 1;''', '''    boolean lvd = i != null && (i.level > 1 || (i.dx > 0.0 && i.dx != 1.0));   // fix2: a Lv 1 ranked / role mob still deals its Damage x (dmgMult(1) = 1)''')

P.rep('''    float mult = @PKG@.MobCfg.dmgMult(i.level);
    if (vp == null) {
      if (mult != 1.0f) d.setAmount(d.getAmount() * mult);
      return;
    }''', '''    float mult = (float) ((double) @PKG@.MobCfg.dmgMult(i.level) * (i.dx > 0.0 ? i.dx : 1.0));   // 0.1.14: x the rank / role Damage x (before the gap)
    if (vp == null) {
      if (mult != 1.0f) d.setAmount(d.getAmount() * mult);
      return;
    }''')
P.rep('''    double xm = hard > 0.0 ? hm / hard : 1.0;
    if (xm > 1.0) xm = 1.0;
    return new Object[] { Integer.valueOf(level), Double.valueOf(base), Double.valueOf(xb), Double.valueOf(hm * rx),
                          Double.valueOf((double) @PKG@.MobCfg.dmgMult(level)), Double.valueOf(xm) };''', '''    double xm = hard > 0.0 ? hm / hard : 1.0;
    if (xm > 1.0) xm = 1.0;
    if (m.rank > 0) {   // 0.1.14: a ranked mob pays x its rank Health (at most x10 of a same-level kill)
      double rp = rx / @PKG@.MobCfg.roleX(m.role);
      if (!(rp > 1.0)) rp = 1.0;
      xm = xm * (rp > 10.0 ? 10.0 : rp);
    }
    double dx = m.dx > 0.0 ? m.dx : 1.0;
    return new Object[] { Integer.valueOf(level), Double.valueOf(base), Double.valueOf(xb), Double.valueOf(hm * rx),
                          Double.valueOf((double) @PKG@.MobCfg.dmgMult(level) * dx), Double.valueOf(xm), @PKG@.MobCfg.rankWord(m.rank) };''')
P.rep('''    if (name != null) {
      if (@PKG@.MobLevel.NAMEFIX.size() >= 2000) @PKG@.MobLevel.NAMEFIX.clear();
      @PKG@.MobLevel.NAMEFIX.put(u, name);
    }''', '''    if (name != null) {
      if (@PKG@.MobLevel.NAMEFIX.size() >= 2000) @PKG@.MobLevel.NAMEFIX.clear();
      @PKG@.MobLevel.NAMEFIX.put(u, name);
    }
    int rk = rankArg(a);   // 0.1.14 (Balance P4 1.7): an optional 5th argument "elite" / "mini" / "boss" (SkyyIslands' Shardkeeper = "mini")
    if (rk > 0) {
      @PKG@.MobCfg.rankPut(u, rk);   // fix2: a full map drops ONE stale entry, never every live mob's rank
    }''')
P.rep('''M(sfn, r"""
public static int levelArg(Object o) {''', '''M(sfn, r"""
public static int rankArg(Object[] a) {
  if (a.length < 5 || !(a[4] instanceof String)) return 0;
  String r = ((String) a[4]).trim().toLowerCase();
  if (r.equals("elite")) return 1;
  if (r.equals("mini")) return 2;
  if (r.equals("boss")) return 3;
  return 0;
}""")
M(sfn, r"""
public static int levelArg(Object o) {''')
P.rep('''# Object[]{ String world, UUID npc, Number level [, String name] } -> Boolean (TRUE = levelled, exactly /mobs set). Never throws.''',
      '''# Object[]{ String world, UUID npc, Number level [, String name [, String rank "elite" | "mini" | "boss"]] } -> Boolean (TRUE = levelled,
# exactly /mobs set). Never throws. 0.1.14: the 5th argument (a name may be null) gives the mob that rank (Health x / damage x of Ranks).''')
P.rep('''public static String checkScaleRole(String key, String value) {
  if (value == null) return null;
  String[] p = value.split("\\\\|");
  try {
    int l = Integer.parseInt(p[0].trim());
    if (l < 0 || l > 100) return "Level must be from 0 to 100 (0 = off).";
    if (p.length > 1 && p[1].trim().length() > 0) {
      double x = Double.parseDouble(p[1].trim());
      if (Double.isNaN(x) || x < 0.1 || x > 100.0) return "Health x must be from 0.1 to 100.";
    }
  } catch (Throwable t) { return "Type a whole level (0-100) and a Health x (0.1-100)."; }
  return null;
}''', '''public static String checkScaleRole(String key, String value) {
  if (value == null) return null;
  String[] p = value.split("\\\\|");
  try {
    int l = Integer.parseInt(p[0].trim());
    if (l < 0 || l > 100) return "Level must be from 0 to 100 (0 = off).";
    if (p.length > 1 && p[1].trim().length() > 0) {
      double x = Double.parseDouble(p[1].trim());
      if (Double.isNaN(x) || x < 0.1 || x > 100.0) return "Health x must be from 0.1 to 100.";
    }
    if (p.length > 2 && p[2].trim().length() > 0) {   // 0.1.14: the Damage x column
      double y = Double.parseDouble(p[2].trim());
      if (Double.isNaN(y) || y < 0.1 || y > 100.0) return "Damage x must be from 0.1 to 100.";
    }
  } catch (Throwable t) { return "Type a whole level (0-100), a Health x and a Damage x (0.1-100)."; }
  return null;
}''')

# ================================================================================================================ 6. MobMigP4
P.rep('''m12 = pool.makeClass(PKG + ".MobMig12")    # 0.1.12: the one-time 20-levels-per-zone update of config.properties + bands.properties''',
      '''m12 = pool.makeClass(PKG + ".MobMig12")    # 0.1.12: the one-time 20-levels-per-zone update of config.properties + bands.properties
mp4 = pool.makeClass(PKG + ".MobMigP4")    # 0.1.14: the one-time Balance P4 combat update of config.properties''')
P.rep('''ALL = [lg, gb, bd, mi, cfg, lv, hk, dm, dmu, fn, ps, sc, pt, rf, mh, mc, mm, gp, gd, gdu, ifn, m14, lat, mcr, crs, cfn, sfn, bfn, m11, m12]''',
      '''ALL = [lg, gb, bd, mi, cfg, lv, hk, dm, dmu, fn, ps, sc, pt, rf, mh, mc, mm, gp, gd, gdu, ifn, m14, lat, mcr, crs, cfn, sfn, bfn, m11, m12, mp4]''')


def _m12_method(name):
    """the Java source of one MobMig12 method (the reviewed text step), copied for MobMigP4"""
    a = P.s.index('M(m12, r"""\npublic static ' + name)
    b = P.s.index('""")', a)
    return P.s[a + len('M(m12, r"""'):b]


_IDX, _EDIT, _SAME, _CURVE = _m12_method("int idx("), _m12_method("Object[] edit("), _m12_method("boolean sameMap("), _m12_method("Object[] curveEdit(")
assert _EDIT.count(" - the 0.1.12 default is ") == 1 and _CURVE.count(" - the 0.1.12 default stretches it to Lv 100: ") == 1
_EDIT = _EDIT.replace(" - the 0.1.12 default is ", " - the 0.1.14 (Balance P4) default is ")
_CURVE = _CURVE.replace(" - the 0.1.12 default stretches it to Lv 100: ", " - the 0.1.14 (Balance P4) default is ")
MIGP4 = r'''
# ---------------------------------------------------------------- MobMigP4 (0.1.14): the one-time Balance P4 combat update of config.properties
# PROJECT-RULES 4 (MobMig12's reviewed text steps edit / curveEdit / sameMap / idx, copied with this class's constants): a key whose LAST entry
# is a one-line entry holding exactly its 0.1.13 default moves (value text only); an admin's own value is kept (INFO); a curve table moves
# WHOLE only while every point is its 0.1.13 default; the exact old Fixed level by role comment -> the 3-column one; then ONE block at the end
# (the file's own line ending): the default scale.role rows the file has no line for (any case), the rank.* rows it lacks, the run-once
# marker. A verified config-history copy first (MobMig.mgKit / mgSaved), one config-changes.log line per change (Undo in Server Setup ->
# Changes), a java.util.Properties check (MobMig12.same: only the planned keys differ), atomicWrite. setup(): after MobMig12, BEFORE MobCfg.load.
def _p4_rows():
    c = [("strength.floor", str(FLOOR_013), str(FLOOR_DEF)), ("levels.exclude", EXCLUDE_013, EXCLUDE_DEF)]
    for _k in ("free", "dealtStep", "takenStep"):
        c.append(("gap." + _k, num(GAP_DEF_013[_k]) if _k != "free" else str(GAP_DEF_013[_k]), num(GAP_DEF[_k]) if _k != "free" else str(GAP_DEF[_k])))
    for _k in ("dealtMin", "takenMax"):
        assert GAP_DEF_013[_k] == GAP_DEF[_k]
    k = []
    for _kd in CURVE_IDX:
        _pf = "curve.%s.%s." % _kd
        _om = dict((a, num(b)) for a, b in CURVES_012[_kd])
        _nm = dict((a, num(b)) for a, b in CURVES[_kd])
        _lg = ["%s[%d];%s;%s" % (_pf[:-1], _L, _om.get(_L, "(none)"), _nm.get(_L, "(none)")) for _L in sorted(set(_om) | set(_nm)) if _om.get(_L) != _nm.get(_L)]
        k.append((_pf, "|".join("%d=%s" % (a, num(b)) for a, b in CURVES_012[_kd]), "|".join("%d=%s" % (a, num(b)) for a, b in CURVES[_kd]),
                  "|".join("%s%d=%s" % (_pf, a, num(b)) for a, b in CURVES[_kd]), "|".join(_lg)))
    return c, k


MGP4_C, MGP4_K = _p4_rows()
assert [r[0] for r in MGP4_C] == ["strength.floor", "levels.exclude", "gap.free", "gap.dealtStep", "gap.takenStep"] and MGP4_C[0][1:] == ("50", "70")
assert [r[1:] for r in MGP4_C[2:]] == [("5", "3"), ("2.5", "5"), ("1.5", "3")], MGP4_C
assert len(MGP4_K) == 8 and all(_r[1] != _r[2] for _r in MGP4_K)
for _d in ("public static final String[] C_KEY = %s;" % _jarr([t[0] for t in MGP4_C]),
           "public static final String[] C_OLD = %s;" % _jarr([t[1] for t in MGP4_C]),
           "public static final String[] C_NEW = %s;" % _jarr([t[2] for t in MGP4_C]),
           "public static final String[] C_NONE = %s;" % _jarr(["" for t in MGP4_C]),
           "public static final String[] C_DOLD = %s;" % _jarr([ROLE_DOC_013]),
           "public static final String[] C_DNEW = %s;" % _jarr([ROLE_DOC]),
           "public static final String[] K_PFX = %s;" % _jarr([t[0] for t in MGP4_K]),
           "public static final String[] K_OLD = %s;" % _jarr([t[1] for t in MGP4_K]),
           "public static final String[] K_NEW = %s;" % _jarr([t[2] for t in MGP4_K]),
           "public static final String[] K_LINES = %s;" % _jarr([t[3] for t in MGP4_K]),
           "public static final String[] K_LOG = %s;" % _jarr([t[4] for t in MGP4_K]),
           "public static final String[] R_KEY = %s;" % _jarr([t[0] for t in P4_ROLE_ROWS]),
           "public static final String[] R_VAL = %s;" % _jarr([t[1] for t in P4_ROLE_ROWS]),
           "public static final String[] A_KEY = %s;" % _jarr([t[0] for t in P4_RANK_ROWS]),
           "public static final String[] A_VAL = %s;" % _jarr([t[1] for t in P4_RANK_ROWS]),
           "public static final String[] A_DOC = %s;" % _jarr(P4_RANK_DOC),
           "public static final String MARK = %s;" % jstr(MGP4_MARK),
           "public static final String MARK_ID = %s;" % jstr(MGP4_MARK_ID),
           "public static final String WHO = %s;" % jstr(MGP4_WHO),
           "public static final String WHAT = %s;" % jstr(MGP4_WHAT)):
    F(mp4, _d)
M(mp4, r"""''' + _IDX + r'''""")
M(mp4, r"""''' + _EDIT + r'''""")
M(mp4, r"""''' + _SAME + r'''""")
M(mp4, r"""''' + _CURVE + r'''""")
# the run-once marker in a comment line (null = not there)
M(mp4, r"""
public static boolean marked(String text) {
  String[] raw = text.split("\n", -1);
  for (int i = 0; i < raw.length; i++) {
    String s = raw[i];
    if (s.endsWith("\r")) s = s.substring(0, s.length() - 1);
    if (@PKG@.CfgFile.isComment(s) && s.indexOf(MARK_ID) >= 0) return true;
  }
  return false;
}""")
# the appended block: { new text, String[] logs (key, old, new)*, String[] props (key, value)* }
M(mp4, r"""
public static Object[] append(String text) {
  java.util.Properties p = new java.util.Properties();
  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { }
  java.util.HashSet low = new java.util.HashSet();
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) low.add(((String) it.next()).toLowerCase());
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  String nl = cr + "\n";
  java.util.ArrayList logs = new java.util.ArrayList();
  java.util.ArrayList props = new java.util.ArrayList();
  StringBuilder blk = new StringBuilder();
  for (int i = 0; i < R_KEY.length; i++) {
    if (low.contains(R_KEY[i].toLowerCase())) continue;
    blk.append(R_KEY[i]).append('=').append(R_VAL[i]).append(nl);
    logs.add("scale.role[" + R_KEY[i].substring(11) + "]"); logs.add("(none)"); logs.add(R_VAL[i].replace(',', '|'));
    props.add(R_KEY[i]); props.add(R_VAL[i]);
  }
  boolean any = false;
  StringBuilder rk = new StringBuilder();
  for (int i = 0; i < A_KEY.length; i++) {
    if (p.getProperty(A_KEY[i]) != null) continue;
    any = true;
    rk.append(A_KEY[i]).append('=').append(A_VAL[i]).append(nl);
    logs.add(A_KEY[i]); logs.add("(none)"); logs.add(A_VAL[i]);
    props.add(A_KEY[i]); props.add(A_VAL[i]);
  }
  if (any) { for (int i = A_DOC.length - 1; i >= 0; i--) rk.insert(0, A_DOC[i] + nl); }
  String pre = (text.length() == 0 || text.endsWith("\n")) ? "" : nl;
  String last = text.endsWith("\n") ? text.substring(0, text.length() - 1) : text;
  if (last.endsWith("\r")) last = last.substring(0, last.length() - 1);
  int bs = 0;
  for (int i = last.length() - 1; i >= 0 && last.charAt(i) == '\\'; i--) bs++;
  if (bs % 2 == 1) pre = pre + nl;
  String body = text + pre + blk.toString() + rk.toString() + MARK + nl;
  return new Object[] { body, (String[]) logs.toArray(new String[0]), (String[]) props.toArray(new String[0]) };
}""")
M(mp4, r"""
public static String[] cat(String[] a, String[] b) {
  String[] r = new String[a.length + b.length];
  for (int i = 0; i < a.length; i++) r[i] = a[i];
  for (int i = 0; i < b.length; i++) r[a.length + i] = b[i];
  return r;
}""")
# the pure text step: null = the marker is there; else { new text, Integer moved keys, String[] kept, String[] logs, String[] props, Integer tables }
M(mp4, r"""
public static Object[] plan(String text) {
  if (text == null || marked(text)) return null;
  Object[] a = edit(text, C_KEY, C_OLD, C_NEW, C_NONE, C_KEY, C_OLD, C_NEW, C_NONE, C_DOLD, C_DNEW, null);
  Object[] b = curveEdit((String) a[0]);
  Object[] c = append((String) b[0]);
  return new Object[] { c[0], Integer.valueOf(((Integer) a[1]).intValue() + ((Integer) b[1]).intValue()), cat((String[]) a[2], (String[]) b[2]),
    cat(cat((String[]) a[3], (String[]) b[3]), (String[]) c[1]), cat(cat((String[]) a[4], (String[]) b[4]), (String[]) c[2]), b[1] };
}""")
M(mp4, r"""
public static String mgLog(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}""")
M(mp4, r"""
public static void logAll(String[] rows) {
  for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(mgLog(rows[i], rows[i + 1], rows[i + 2]));
  if (rows.length > 0) @PKG@.CfgLog.flush();
}""")
M(mp4, r"""
public static synchronized String run(java.nio.file.Path dir) {
  if (dir == null) return "";
  java.nio.file.Path f = dir.resolve("config.properties");
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = plan(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] nb = ((String) r[0]).getBytes("ISO-8859-1");
    if (!@PKG@.MobMig12.same(old, nb, (String[]) r[4])) {
      @PKG@.MobLog.warn("config.properties NOT updated for 0.1.14 (Balance P4 combat): the update would change more than its lines (the file is used as it is; the next start tries again)");
      return "";
    }
    int fc = @PKG@.MobMig12.fileIdx("/config.properties");
    if (fc < 0) return "";
    @PKG@.MobMig.mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fc, old, @PKG@.CfgHist.stamp(), WHO, WHAT);
    if (!@PKG@.MobMig.mgSaved(fc, old)) {
      @PKG@.MobLog.warn("config.properties NOT updated for 0.1.14 (Balance P4 combat): the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, nb);
    logAll((String[]) r[3]);
    String msg = "config.properties updated for 0.1.14 (Balance P4 combat): " + ((Integer) r[1]).intValue() + " settings moved (" + ((Integer) r[5]).intValue()
      + " of them Level curve tables, 21 points each; floor 70, level gap 3 / 5 / 3; boss levels + Ranks rows added; the old file is in config-history; Server Setup -> Changes can undo each line)";
    @PKG@.MobLog.info(msg);
    StringBuilder all = new StringBuilder(msg);
    String[] k1 = (String[]) r[2];
    for (int i = 0; i < k1.length; i++) { @PKG@.MobLog.info(k1[i]); all.append('\n').append(k1[i]); }
    return all.toString();
  } catch (Throwable t) {
    @PKG@.MobLog.warn("could not update config.properties for 0.1.14 (Balance P4 combat; the file is used as it is): " + t);
    return "";
  }
}""")
'''
P.rep('''# ---------------------------------------------------------------- MobCmds: the command bodies (world thread: AbstractPlayerCommand runs there)''',
      MIGP4.lstrip("\n") + '''
# ---------------------------------------------------------------- MobCmds: the command bodies (world thread: AbstractPlayerCommand runs there)''')
P.rep('''  String mg12 = @PKG@.MobMig12.run(dir);   // 0.1.12: 20 levels per zone - untouched zone tops / band rows / colour rows (once; History first; Undo in Server Setup)
  if (mg12.length() > 0) mg = mg.length() > 0 ? mg + "\\n" + mg12 : mg12;''', '''  String mg12 = @PKG@.MobMig12.run(dir);   // 0.1.12: 20 levels per zone - untouched zone tops / band rows / colour rows (once; History first; Undo in Server Setup)
  if (mg12.length() > 0) mg = mg.length() > 0 ? mg + "\\n" + mg12 : mg12;
  String mgp4 = @PKG@.MobMigP4.run(dir);   // 0.1.14: Balance P4 combat - untouched curve tables / floor / gap / exclude rows + boss + Ranks rows (once; History first; Undo)
  if (mgp4.length() > 0) mg = mg.length() > 0 ? mg + "\\n" + mgp4 : mgp4;''')
P.rep('''                 "(Zone 1 Lv 1-20, Zone 2 20-40, Zone 3 40-60, Zone 4 60-80, Zone 5 80-100), more health and damage per level with a difficulty "
                 "setting and a health floor, the Level curve (Wynncraft style) and a BRUTAL level gap, a [Lv 9] nameplate,''',
      '''                 "(Zone 1 Lv 1-20, Zone 2 20-40, Zone 3 40-60, Zone 4 60-80, Zone 5 80-100), more health and damage per level with a difficulty "
                 "setting and a health floor, the Level curve (Wynncraft style) and a BRUTAL level gap, elites / mini bosses / bosses (Ranks), a [Lv 9] nameplate,''')

# ================================================================================================================ guards
assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count("bridge().put(") == PUT0
assert P.s.count("makeClass(") == CLS0 + 1, "exactly one new class (MobMigP4)"
P.finish()
