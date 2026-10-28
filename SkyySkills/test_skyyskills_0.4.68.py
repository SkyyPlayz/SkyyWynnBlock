"""SkyySkills 0.4.68 - harness for "low-tier crop falloff" (tools/skills_0_4_68_patch.py; round farmxp). Build first:
    python tools/skills_0_4_68_patch.py && python SkyySkills/build_skyyskills_0.4.68.py
    python SkyySkills/test_skyyskills_0.4.68.py [--keep]
Phases (each a fresh child JVM: -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes, line endings kept, 0 classes / systems / commands added, VERSION, the 3 call sites,
                 the 6 Server Setup rows right after the tool-tier row, the fresh default file (the LT block at the end)
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.4.67 -> 0.4.68: exactly the planned members (EXPECT)
  X     EXECUTED Sickle.readLow (defaults, custom, clamps, bad lists), FarmTier.lowTier / cropTier / bandMult / lowMult / lowAt (Wheat at
                 Lv 10 / 25 / 40, right-tier crops at Lv 40 unchanged, the 8+ band, herbs / Orchard / other ids never lowered, the exact
                 average of a fraction), a Harvester sweep of many crops, FarmTier.low (the game path: the player's real Farming level from
                 SkillStore), enabled false = the 0.4.67 numbers, statsLine / lowText
  X67   the 0.4.67 X phase re-run on the 0.4.68 jar (FellCfg + ForXpMig unchanged)
  LIVE  start twice on a scratch COPY of the live Skyy_SkyySkills (NewBetaTest, 0.4.67): no file changes at all (no one-time update),
                 SkillCfg.load reads the code defaults (on, 4 / 0.5, 8 / 0.25); then the file with farming.lowTier.enabled=false -> off
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): the three award sites themselves on a real sweep / break / F-harvest (each one changed line calls
FarmTier.low, executed here).
"""
import os, sys, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "skills068", "sk")]


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T67 = _mod(os.path.join(HERE, "test_skyyskills_0.4.67.py"), "test_skyyskills_0_4_67")
T48, T53 = T67.T48, T67.T53
jpath = T67.jpath
VERSION = "0.4.68"
PKG = "com.skyy.skills."
GEN = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyskills_0.4.67.py")
PATCH = os.path.join(TOOLS, "skills_0_4_68_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.67.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T67.LIVE_DIR
ADDED = []
EXPECT = {   # checked 2026-10-27 (the class compare vs 0.4.67 of the first harness run): Sickle (the keys) + FarmTier (the rule) + the 3 award
    # sites (Sickle.award, BreakTask, HarvestTask) + the Stats line = THE change; the rest = the default-file text (CfgFile), the 6 rows (CfgRows)
    # and the version / ready-line text (CfgFn, CurveP9Mig, ManaGuard, SkillCfg.load, setup) - the same set 0.4.67 changed for its version
    'BreakTask': ['~m run'],
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CurveP9Mig': ['~m run'],
    'FarmTier': ['+f LOWERED', '+m bandMult', '+m cropName', '+m cropTier', '+m low', '+m lowAt', '+m lowMult', '+m lowText', '+m lowTier', '+m statsLine', '~<clinit>'],
    'HarvestTask': ['~m run'],
    'ManaGuard': ['~m armReport2', '~m intReport', '~m packReport'],
    'Sickle': ['+f LOW_G1', '+f LOW_G2', '+f LOW_LV', '+f LOW_LV_DEF', '+f LOW_LV_TEXT', '+f LOW_M1', '+f LOW_M2', '+f LOW_NAMES', '+f LOW_ON', '+f LOW_WARNED',
               '+m checkLowLevels', '+m lowGapOf', '+m lowLevels', '+m lowMultOf', '+m readLow', '~<clinit>', '~m award', '~m read'],
    'SkillCfg': ['~m load'],
    'SkyySkillsPlugin': ['~m setup'],
    'StatsPage': ['~m lines0'],
}
LADDER = ["Wheat", "Lettuce", "Carrot", "Corn", "Cauliflower", "Turnip", "Pumpkin", "Aubergine", "Tomato", "Chilli", "Cotton", "Rice", "Potato", "Onion", "Mushroom"]
P3_CROP = [40, 80, 135, 185, 280, 380, 460, 605, 750, 860, 1050, 1250, 1400, 1600, 1850]
LEVELS = [1, 8, 15, 20, 28, 35, 40, 48, 55, 60, 68, 75, 80, 88, 95]
LT_KEYS = ["farming.lowTier.enabled", "farming.lowTier.levels", "farming.lowTier.gap1", "farming.lowTier.mult1", "farming.lowTier.gap2", "farming.lowTier.mult2"]


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyySkills 0.4.68') and g.count('VERSION = "0.4.68"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(")
            and g.count("makeClass(") == o.count("makeClass("), "S no new command / system / class")
    K.check(g.count("{PKG}.FarmTier.low(") == 2 and g.count("@PKG@.FarmTier.low(") == 1, "S the 3 award sites call FarmTier.low (break, F-harvest; sweep)")
    K.check("amt = @PKG@.FarmTier.low(u, (String) info[2], amt);" in g and "{PKG}.FarmTier.low(this.u, this.ripe, this.amount)" in g
            and "bamt = {PKG}.FarmTier.low(this.u, lbt == null ? null : lbt.getId(), bamt);" in g, "S sweep per crop, F-harvest, break")
    K.check(g.index("amt = @PKG@.FarmTier.low(u, (String) info[2], amt);") < g.index("if (amt > 0L) @PKG@.SkillXp.gain(pr, @PKG@.Farm3.route(@PKG@.SkillDefs.FARMING, (String) info[2]), amt);"),
            "S the sweep lowers BEFORE SkillXp.gain (pace, Wisdom, pet share, Beastmastery follow)")
    K.check('assert [_r[0] for _r in CFG_ROWS][_ix68:_ix68 + 7] == ["farming.tierUpXpFactor"] + [_k for _k, _v in LT_KEYS]' in g, "S the 6 rows sit right after the tool-tier row (build-time assert)")
    K.check("DEFAULTS.endswith(LT_BLOCK)" in g and "DEFAULTS_067.endswith(FX_BLOCK)" in g, "S the LT block ends the fresh file")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_x(out, jar, scratch, _home):
    from jpype import JInt, JLong, JDouble, JClass
    K = HK.Child(out)
    J = T67._cls(jar)
    S, FT, Cfg, Sto, F3 = J("Sickle"), J("FarmTier"), J("SkillCfg"), J("SkillStore"), J("Farm3")
    P = T67._P
    try:
        # ---- the fresh default file carries the 6 keys
        d68 = T67._plain(str(Cfg.DEFAULTS))
        K.check([d68.get(k) for k in LT_KEYS] == ["true", ",".join(str(x) for x in LEVELS), "4", "0.5", "8", "0.25"], "X fresh file: %s" % [d68.get(k) for k in LT_KEYS])
        # ---- readLow
        S.read(P({}))
        K.check(bool(S.LOW_ON) and list(S.LOW_LV) == LEVELS and int(S.LOW_G1) == 4 and float(S.LOW_M1) == 0.5 and int(S.LOW_G2) == 8 and float(S.LOW_M2) == 0.25,
                "X readLow: code defaults on, P3 bands, 4 / 0.5, 8 / 0.25")
        S.read(P({"farming.lowTier.gap1": "3", "farming.lowTier.mult1": "0.6", "farming.lowTier.gap2": "-2", "farming.lowTier.mult2": "7", "farming.lowTier.levels": "1, 10, 30"}))
        K.check(int(S.LOW_G1) == 3 and abs(float(S.LOW_M1) - 0.6) < 1e-12 and int(S.LOW_G2) == 0 and float(S.LOW_M2) == 1.0 and list(S.LOW_LV) == [1, 10, 30],
                "X readLow: custom + clamps (gap -2 -> 0, mult 7 -> 1)")
        S.read(P({"farming.lowTier.levels": "5,3", "farming.lowTier.mult1": "abc", "farming.lowTier.gap1": "x"}))
        K.check(list(S.LOW_LV) == LEVELS and float(S.LOW_M1) == 0.5 and int(S.LOW_G1) == 4, "X readLow: a falling list / bad numbers -> the defaults")
        K.check(S.checkLowLevels("k", "1,8,15") is None and S.checkLowLevels("k", "8,1") is not None and S.checkLowLevels("k", "") is not None
                and S.checkLowLevels("k", "0,5") is not None and S.checkLowLevels("k", "1,a") is not None, "X checkLowLevels refuses bad lists")
        S.read(P({}))
        # ---- tiers
        K.eq([int(FT.lowTier(JInt(l))) for l in (0, 1, 7, 8, 14, 15, 20, 27, 28, 34, 35, 39, 40, 47, 48, 55, 95, 120)],
             [1, 1, 1, 2, 2, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 9, 15, 15], "X lowTier: the P3 bands")
        K.eq([int(FT.cropTier("Plant_Crop_%s_Block" % c)) for c in LADDER], list(range(1, 16)), "X cropTier: the ladder Wheat T1 .. Mushroom T15")
        K.check(int(FT.cropTier("*Plant_Crop_Wheat_Block_State_Definitions_StageFinal")) == 1 and int(FT.cropTier("Plant_Crop_Corn")) == 4,
                "X cropTier: a state id (leading *) and the bare id")
        K.check(all(int(FT.cropTier(x)) == 0 for x in ("Plant_Crop_Health1_Block", "Plant_Crop_Apple_Block", "Plant_Crop_Berry_Block", "Plant_Crop_Wheatgrass",
                                                       "Plant_Crop_", "Ore_Iron", None, "Wood_Oak_Trunk")), "X cropTier: herbs / orchard / look-alikes / others = 0")
        m = lambda lv, c: float(FT.lowMult(JInt(lv), "Plant_Crop_%s_Block" % c))
        # the asked numbers: Wheat at Lv 10 / 25 / 40, right-tier at Lv 40
        K.eq([m(10, "Wheat"), m(25, "Wheat"), m(28, "Wheat"), m(40, "Wheat"), m(55, "Wheat")], [1.0, 1.0, 0.5, 0.5, 0.25], "X Wheat at Lv 10 / 25 / 28 / 40 / 55")
        K.eq([m(34, "Lettuce"), m(35, "Lettuce"), m(38, "Lettuce"), m(43, "Lettuce"), m(60, "Lettuce")], [1.0, 0.5, 0.5, 0.5, 0.25], "X Lettuce at Lv 34 / 35 / 38 / 43 / 60")
        K.eq([m(40, c) for c in ("Carrot", "Corn", "Cauliflower", "Turnip", "Pumpkin", "Aubergine")], [0.5, 1.0, 1.0, 1.0, 1.0, 1.0],
             "X Lv 40 (T7): Carrot (4 below) x0.5, Corn..Pumpkin (right tier) and above x1")
        K.check(all(m(lv, c) == 1.0 for lv in range(1, 28) for c in LADDER), "X Zone 1 and Farming Lv 1-27: every crop x1 (unchanged)")
        K.check(all(m(lv, c) == 1.0 for lv in range(15, 36) for i, c in enumerate(LADDER) if int(FT.lowTier(JInt(lv))) - (i + 1) <= 3),
                "X Zone 2: right-tier crops (0-3 tiers below) always x1")
        # lowAt: amounts, fractions with the exact average
        K.eq(int(FT.lowAt(JInt(40), "Plant_Crop_Wheat_Block", JLong(40), JDouble(0.0))), 20, "X lowAt: Wheat 40 XP at Lv 40 -> 20")
        K.eq(int(FT.lowAt(JInt(10), "Plant_Crop_Wheat_Block", JLong(40), JDouble(0.0))), 40, "X lowAt: Wheat at Lv 10 -> 40 (unchanged)")
        K.eq(int(FT.lowAt(JInt(25), "Plant_Crop_Wheat_Block", JLong(40), JDouble(0.0))), 40, "X lowAt: Wheat at Lv 25 -> 40 (unchanged)")
        K.eq(int(FT.lowAt(JInt(40), "Plant_Crop_Pumpkin_Block", JLong(460), JDouble(0.0))), 460, "X lowAt: Pumpkin (right tier) at Lv 40 -> 460 (unchanged)")
        K.eq(int(FT.lowAt(JInt(60), "Plant_Crop_Wheat_Block", JLong(40), JDouble(0.0))), 10, "X lowAt: Wheat at Lv 60 (9 below) -> 10")
        K.check(int(FT.lowAt(JInt(40), "Plant_Crop_Carrot_Block", JLong(135), JDouble(0.4))) == 68 and int(FT.lowAt(JInt(40), "Plant_Crop_Carrot_Block", JLong(135), JDouble(0.6))) == 67,
                "X lowAt: 135 x0.5 = 67.5 -> 68 when r < 0.5, else 67")
        n = 2000
        tot = sum(int(FT.lowAt(JInt(40), "Plant_Crop_Carrot_Block", JLong(135), JDouble((i + 0.5) / n))) for i in range(n))
        K.check(tot == 135 * n // 2, "X lowAt: the exact average (%d of %d)" % (tot, 135 * n // 2))
        K.eq(int(FT.lowAt(JInt(90), "Plant_Crop_Health1_Block", JLong(80), JDouble(0.0))), 80, "X lowAt: a herb is never lowered")
        # a Harvester sweep at Lv 40: 30 Wheat + 30 Lettuce (each crop its own award) vs Lv 25 and the right-tier sweep
        def sweep(lv, crops):
            return sum(int(FT.lowAt(JInt(lv), "Plant_Crop_%s_Block" % c, JLong(P3_CROP[LADDER.index(c)]), JDouble(0.5))) for c in crops)
        sw = ["Wheat"] * 30 + ["Lettuce"] * 30
        K.eq([sweep(25, sw), sweep(38, sw), sweep(40, sw)], [3600, 1800, 1800], "X Harvester sweep of 30 Wheat + 30 Lettuce: Lv 25 3600, Lv 38 / 40 1800 (x0.5)")
        K.eq(sweep(40, ["Pumpkin"] * 30 + ["Turnip"] * 30), 30 * 460 + 30 * 380, "X a right-tier sweep at Lv 40 pays full")
        # the game path: the player's real Farming level (SkillStore) + the Orchard guard
        xd = os.path.join(scratch, "xgame")
        os.makedirs(os.path.join(xd, "players"), exist_ok=True)
        open(os.path.join(xd, "xp.properties"), "wb").write(str(Cfg.DEFAULTS).encode("latin-1"))
        Cfg.FILE = jpath(os.path.join(xd, "xp.properties"))
        Sto.DIR = jpath(os.path.join(xd, "players"))
        Sto.DATA.clear()
        Cfg.load()
        u = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-000000068001")
        d = Sto.data(u)
        far = int(J("SkillDefs").FARMING)
        for xp in range(0, 400001, 500):
            d[far] = xp
            if int(Sto.level(u, JInt(far))) == 40:
                break
        lv = int(Sto.level(u, JInt(far)))
        K.check(lv == 40, "X (setup: player at Farming Lv %d with %d XP)" % (lv, int(d[far])))
        got = [int(FT.low(u, "Plant_Crop_Wheat_Block", JLong(40))) for _ in range(20)]
        K.check(all(x == 20 for x in got), "X low (game path): Wheat at the player's Lv 40 -> 20")
        K.eq(int(FT.low(u, "Plant_Crop_Pumpkin_Block", JLong(460))), 460, "X low: Pumpkin at Lv 40 -> 460")
        d[far] = 0
        K.eq(int(FT.low(u, "Plant_Crop_Wheat_Block", JLong(40))), 40, "X low: Wheat at Lv %d -> 40" % int(Sto.level(u, JInt(far))))
        d[far] = 400000
        F3.read(P({"orchard.ids": "Plant_Crop_Wheat"}))
        K.check(int(F3.route(JInt(far), "Plant_Crop_Wheat_Block")) != far and int(FT.low(u, "Plant_Crop_Wheat_Block", JLong(40))) == 40,
                "X low: a crop an admin routed to Orchard (orchard.ids) is never lowered (Lv %d)" % int(Sto.level(u, JInt(far))))
        Cfg.load()
        K.check(int(F3.route(JInt(far), "Plant_Crop_Wheat_Block")) == far, "X (orchard.ids back to the default)")
        # enabled false = the 0.4.67 numbers
        S.read(P({"farming.lowTier.enabled": "false"}))
        K.check(all(int(FT.lowAt(JInt(lv), "Plant_Crop_%s_Block" % c, JLong(x), JDouble(0.0))) == x for lv in (10, 40, 99) for c, x in zip(LADDER, P3_CROP)),
                "X enabled false: every crop at every level pays its 0.4.67 XP")
        K.eq(int(FT.low(u, "Plant_Crop_Wheat_Block", JLong(40))), 40, "X enabled false: the game path too")
        K.check(FT.statsLine(JInt(40)) is None and str(FT.lowText()) == "off", "X enabled false: no Stats line, ready line 'off'")
        S.read(P({"farming.lowTier.gap1": "0", "farming.lowTier.gap2": "0"}))
        K.eq(int(FT.lowAt(JInt(99), "Plant_Crop_Wheat_Block", JLong(40), JDouble(0.0))), 40, "X both gaps 0 = nothing lowered")
        # texts
        S.read(P({}))
        t10, t40, t60 = str(FT.statsLine(JInt(10))), str(FT.statsLine(JInt(40))), str(FT.statsLine(JInt(60)))
        K.check("T2" in t10 and "every crop pays full XP" in t10, "X statsLine Lv 10: %s" % t10)
        K.check(t40 == "Your Farming tier: T7 - less XP for Wheat (T1) to Carrot (T3) x0.5", "X statsLine Lv 40: %s" % t40)
        K.check(t60 == "Your Farming tier: T10 - less XP for Wheat (T1) to Lettuce (T2) x0.25, Carrot (T3) to Turnip (T6) x0.5", "X statsLine Lv 60: %s" % t60)
        K.notes.append("lowText: %s" % str(FT.lowText()))
        K.check("4+ tiers below x0.5" in str(FT.lowText()) and "8+ x0.25" in str(FT.lowText()), "X lowText")
    except Exception as e:
        import traceback
        traceback.print_exc()
        K.check(False, "X: run crashed: %s" % str(e)[:400])
    K.save()


def run_x67(out, jar, scratch, home):
    T67.run_x(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    J = T67._cls(jar)
    xp = os.path.join(home, "xp.properties")
    t0 = open(xp, "rb").read().decode("latin-1")
    K.check(T67.MARK_ID in t0 and "farming.lowTier" not in t0, "LIVE the live file is the 0.4.67 one (Foraging marker, no lowTier lines)")
    s0 = T53.snapd(home)
    r1 = T67._start(J, home)
    s1 = T53.snapd(home)
    ch = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
    K.check(ch == [], "LIVE start 1: nothing written (no one-time update): %s" % ch[:8])
    S, FT = J("Sickle"), J("FarmTier")
    K.check(bool(S.LOW_ON) and int(S.LOW_G1) == 4 and float(S.LOW_M1) == 0.5 and int(S.LOW_G2) == 8 and float(S.LOW_M2) == 0.25 and list(S.LOW_LV) == LEVELS,
            "LIVE SkillCfg.load: the code defaults (the file has no lowTier lines)")
    K.eq(int(FT.lowAt(40, "Plant_Crop_Wheat_Block", 40, 0.0)), 20, "LIVE Wheat at Lv 40 -> 20 on the live settings")
    r2 = T67._start(J, home)
    K.check(T53.snapd(home) == s1, "LIVE start 2 changes nothing")
    open(xp, "ab").write(("farming.lowTier.enabled=false" + ("\r\n" if "\r\n" in t0 else "\n")).encode("latin-1"))
    J("SkillCfg").load()
    K.check(not bool(S.LOW_ON) and int(FT.lowAt(40, "Plant_Crop_Wheat_Block", 40, 0.0)) == 40, "LIVE farming.lowTier.enabled=false in the file -> off (0.4.67 numbers)")
    K.save()


if __name__ == "__main__":
    phases = [("static", run_static), ("x", run_x), ("x67", run_x67), ("live", run_live)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
