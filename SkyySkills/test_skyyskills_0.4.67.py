"""SkyySkills 0.4.67 - harness for "Foraging XP by wood tier + less for big trees" (tools/skills_0_4_67_patch.py; round forxp). Build first:
    python tools/skills_0_4_67_patch.py && python SkyySkills/build_skyyskills_0.4.67.py
    python SkyySkills/test_skyyskills_0.4.67.py [--keep]
Phases (each a fresh child JVM: -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes, line endings kept, + exactly 1 class / 0 systems / 0 commands, VERSION, the rows,
                 the fresh default file (the tier rows, the leaf factor, the FX block + marker)
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.4.66 -> 0.4.67: exactly the planned members (EXPECT) + the new class (ADDED)
  X     EXECUTED FellCfg.read (defaults, custom, clamps, 0 = off), FellCfg.share (the curve), FellCfg.creditR (logs x xpFactor x
                 otherLogsPercent x share, leaves x leafXpFactor paid as random whole XP with the exact average, the FELLED counter,
                 0 = nothing), FellCfg.credit (the game path), FellCfg.text; ForXpMig.plan on a 0.4.66 file (every planned line, nothing
                 else; an admin's own row kept + named; CRLF kept; the block lines only if absent; the marker = never again)
  LIVE  start twice on a scratch COPY of the live Skyy_SkyySkills (NewBetaTest, 0.4.66): start 1 = every 0.4.66 migration + ForXpMig:
                 xp.properties changes ONLY the planned lines (+ the block), CRLF / bytes kept elsewhere, config-history copy + one
                 config-changes.log row per change, no player file touched; SkillCfg.load then reads Maple 12 / Oak 4 / leaves 0.1 / big
                 trees 30 + 2 (classifyBreak on the real Wood_Maple_Trunk block type); start 2 changes nothing
  LIVE2 a scratch COPY with the Maple row hand-edited by an admin (Foraging:99) and a pending P3 file: kept / refused as PROJECT-RULES 4 says
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): FellCredit.one itself on a real falling tree (its one changed line calls FellCfg.credit, executed here);
the real falling order of a tree's logs (which logs get the shrinking share - the total is the same for one wood).
"""
import os, sys, subprocess, importlib.util, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "forxp", "sk")]


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T66 = _mod(os.path.join(HERE, "test_skyyskills_0.4.66.py"), "test_skyyskills_0_4_66")
T64 = T66.T64
T48, T53, T57 = T64.T48, T64.T53, T64.T57
jpath = T64.jpath
VERSION = "0.4.67"
PKG = "com.skyy.skills."
GEN = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyskills_0.4.66.py")
PATCH = os.path.join(TOOLS, "skills_0_4_67_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.66.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T66.LIVE_DIR
ADDED = ["ForXpMig"]
EXPECT = {   # checked 2026-10-25 (the class compare vs 0.4.66 of the first harness run): FellCfg + FellCredit.one + setup = THE change; the rest = the
    # default-file text (CfgFile, FellCfg.ensureDefaults), the 2 rows (CfgRows) and the version text
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CurveP9Mig': ['~m run'],
    'FellCfg': ['+f BIG_FALLOFF', '+f BIG_FROM', '+m credit', '+m creditR', '+m share', '~<clinit>', '~m ensureDefaults', '~m read', '~m text'],
    'FellCredit': ['~m one'],
    'ManaGuard': ['~m armReport2', '~m intReport', '~m packReport'],
    'SkillCfg': ['~m load'],
    'SkyySkillsPlugin': ['~m setup'],
}
P3_LOG = [35, 70, 120, 160, 245, 330, 400, 525, 650, 745, 915, 1050, 1200, 1400, 1600]
FX_LOG = [4, 7, 12, 22, 34, 46, 56, 74, 91, 142, 174, 200, 372, 434, 496]   # fixer: 10 % T1-T3, 14 % T4-T9, 19 % T10-T12, 31 % T13-T15 of P3_LOG
MARK_ID = "Foraging XP by tier (SkyySkills 0.4.67)"


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyySkills 0.4.67') and g.count('VERSION = "0.4.67"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem("), "S no new command, no new system")
    K.check(g.count("makeClass(") == o.count("makeClass(") + 1 and g.count('pool.makeClass(PKG + ".ForXpMig")') == 1, "S exactly 1 new class (ForXpMig)")
    for i, k in enumerate(("fell.bigTreeFrom", "fell.bigTreeFalloff")):
        K.check(g.count('CFG_ROWS.insert(_ix67 + %d, ("%s",' % (i + 1, k)) == 1, "S Server Setup row %s right after Felled leaf XP (fix 4)" % k)
    K.check('assert [_r[0] for _r in CFG_ROWS][_ix67:_ix67 + 3] == ["fell.leafXpFactor", "fell.bigTreeFrom", "fell.bigTreeFalloff"]' in g
            and "(full logs / k)" not in g and "each extra log after that pays less" in g, "S fix 4: the rows sit next to the leaf row (build-time assert) in plain words")
    K.check("FX_PCT = [10] * 3 + [14] * 6 + [19] * 3 + [31] * 3" in g and all(a < b for a, b in zip(FX_LOG, FX_LOG[1:]))
            and FX_LOG == [max(1, (x * p + 50) // 100) for x, p in zip(P3_LOG, [10] * 3 + [14] * 6 + [19] * 3 + [31] * 3)], "S fix 2: the per-tier taper, higher tier pays more")
    K.check('("fell.leafXpFactor", "Felled leaf XP", "gathering", "dec", "0.1",' in g, "S the leaf row default 0.1")
    K.check(g.count("{PKG}.ForXpMig.run();") == 1 and g.index("{PKG}.ForXpMig.run();") > g.index("{PKG}.P9Mig.run();") and
            g.index("{PKG}.ForXpMig.run();") < g.index("String rules = {PKG}.SkillCfg.load();"), "S setup: ForXpMig after the P9 updates, before SkillCfg.load")
    K.check(g.count("{PKG}.FellCfg.credit(rule[1], W.leaf[i], W.cLogs + 2)") == 1 and "Math.round((double) rule[1] * fct)" not in g, "S FellCredit.one pays through FellCfg.credit")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def _cls(jar):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR], verify=True)
    L = T48.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    J("SkillCfg").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    return J


def _P(d):
    from jpype import JClass
    p = JClass("java.util.Properties")()
    for k, v in d.items():
        p.setProperty(k, v)
    return p


def _plain(txt):
    out = {}
    for ln in txt.replace("\r\n", "\n").split("\n"):
        t = ln.strip()
        if t and not t.startswith("#") and "=" in t:
            out[t.split("=", 1)[0].strip()] = t.split("=", 1)[1].strip()
    return out


def run_x(out, jar, scratch, _home):
    from jpype import JInt, JLong, JDouble, JBoolean
    K = HK.Child(out)
    J = _cls(jar)
    FC, XE, FM, Cfg = J("FellCfg"), J("XpEven"), J("ForXpMig"), J("SkillCfg")
    try:
        # ---- FellCfg.read: code defaults, custom values, clamps
        FC.read(_P({}))
        K.check(int(FC.BIG_FROM) == 30 and abs(float(FC.BIG_FALLOFF) - 2.0) < 1e-12 and abs(float(FC.LEAF_XP_FACTOR) - 0.1) < 1e-12, "X read: code defaults 30 / 2 / leaves 0.1")
        FC.read(_P({"fell.bigTreeFrom": "50", "fell.bigTreeFalloff": "1.5", "fell.leafXpFactor": "0.5"}))
        K.check(int(FC.BIG_FROM) == 50 and abs(float(FC.BIG_FALLOFF) - 1.5) < 1e-12 and abs(float(FC.LEAF_XP_FACTOR) - 0.5) < 1e-12, "X read: custom values")
        FC.read(_P({"fell.bigTreeFrom": "-3", "fell.bigTreeFalloff": "9"}))
        K.check(int(FC.BIG_FROM) == 0 and abs(float(FC.BIG_FALLOFF) - 4.0) < 1e-12, "X read: clamps 0..1024 / 0..4")
        FC.read(_P({"fell.bigTreeFrom": "5000", "fell.bigTreeFalloff": "abc"}))
        K.check(int(FC.BIG_FROM) == 1024 and abs(float(FC.BIG_FALLOFF) - 2.0) < 1e-12, "X read: 5000 -> 1024, a bad number -> the default 2")
        # ---- share
        FC.read(_P({}))
        K.check(float(FC.share(JInt(1))) == 1.0 and float(FC.share(JInt(30))) == 1.0, "X share: logs 1-30 pay in full")
        K.check(abs(float(FC.share(JInt(60))) - 0.25) < 1e-12 and abs(float(FC.share(JInt(300))) - 0.01) < 1e-12, "X share: log 60 = 25 %, log 300 = 1 %")
        tot = sum(float(FC.share(JInt(k))) for k in range(1, 251))
        K.check(55.0 < tot < 57.0, "X share: a 250-log Maple pays %.1f logs' worth (model ~56)" % tot)
        tot2 = sum(float(FC.share(JInt(k))) for k in range(1, 3001))
        K.check(tot2 < 60.0, "X share: a 3000-log giant stays under 60 logs' worth (%.1f)" % tot2)
        FC.read(_P({"fell.bigTreeFrom": "0"}))
        K.check(float(FC.share(JInt(500))) == 1.0, "X share: fell.bigTreeFrom 0 = every log full")
        FC.read(_P({"fell.bigTreeFalloff": "0"}))
        K.check(float(FC.share(JInt(500))) == 1.0, "X share: fell.bigTreeFalloff 0 = every log full")
        FC.read(_P({"fell.bigTreeFalloff": "1"}))
        K.check(abs(float(FC.share(JInt(60))) - 0.5) < 1e-12, "X share: falloff 1 = gentler (log 60 = 50 %)")
        # ---- creditR: logs (xpFactor x otherLogsPercent x share), leaves (x leafXpFactor, random whole XP)
        FC.read(_P({}))
        XE.read(_P({}))
        K.check(abs(float(XE.FELL_PCT) - 100.0) < 1e-12, "X (fell.otherLogsPercent default 100)")
        f0 = int(XE.FELLED.get())
        K.eq(int(FC.creditR(JLong(12), JBoolean(False), JInt(2), JDouble(0.99))), 12, "X creditR: a Maple log (12) inside the first 30 pays 12")
        K.check(int(XE.FELLED.get()) == f0 + 1, "X creditR: a felled log counts in XpEven.FELLED (as fellLog did)")
        K.eq(int(FC.creditR(JLong(12), JBoolean(False), JInt(60), JDouble(0.99))), 3, "X creditR: log 60 pays 12 x 25 % = 3")
        K.check(int(FC.creditR(JLong(12), JBoolean(False), JInt(120), JDouble(0.70))) == 1 and int(FC.creditR(JLong(12), JBoolean(False), JInt(120), JDouble(0.80))) == 0,
                "X creditR: log 120 pays 12 x 6.25 % = 0.75 -> 1 XP when r < 0.75, else 0 (the exact average)")
        n = 20000
        got = sum(int(FC.creditR(JLong(1), JBoolean(True), JInt(5), JDouble((i + 0.5) / n))) for i in range(n))
        K.check(got == n // 10, "X creditR: a leaf (1 XP) x 0.1 pays 1 XP for every 10 leaves on average (%d of %d)" % (got, n))
        K.eq(int(FC.creditR(JLong(1), JBoolean(True), JInt(5000), JDouble(0.05))), 1, "X creditR: leaves never get the big-tree share")
        FC.read(_P({"fell.leafXpFactor": "1.0"}))
        K.check(all(int(FC.creditR(JLong(1), JBoolean(True), JInt(2), JDouble(r))) == 1 for r in (0.0, 0.5, 0.999)), "X creditR: leaf factor 1.0 = 1 XP each (the old Math.round result)")
        FC.read(_P({"fell.leafXpFactor": "0"}))
        K.eq(int(FC.creditR(JLong(1), JBoolean(True), JInt(2), JDouble(0.0))), 0, "X creditR: leaf factor 0 = nothing")
        FC.read(_P({"fell.xpFactor": "0"}))
        f1 = int(XE.FELLED.get())
        K.check(int(FC.creditR(JLong(12), JBoolean(False), JInt(2), JDouble(0.0))) == 0 and int(XE.FELLED.get()) == f1, "X creditR: fell.xpFactor 0 = nothing, not counted")
        FC.read(_P({}))
        K.eq(int(FC.creditR(JLong(0), JBoolean(False), JInt(2), JDouble(0.0))), 0, "X creditR: a 0 XP row pays nothing")
        XE.read(_P({"fell.otherLogsPercent": "50"}))
        K.eq(int(FC.creditR(JLong(12), JBoolean(False), JInt(2), JDouble(0.99))), 6, "X creditR: fell.otherLogsPercent 50 still applies (12 x 50 %)")
        XE.read(_P({}))
        FC.read(_P({"fell.xpFactor": "2.0"}))
        K.eq(int(FC.creditR(JLong(12), JBoolean(False), JInt(60), JDouble(0.99))), 6, "X creditR: fell.xpFactor 2 x share 25 % = 12 x 2 x 0.25")
        FC.read(_P({}))
        tree = sum(int(FC.creditR(JLong(12), JBoolean(False), JInt(k + 1), JDouble(0.5))) for k in range(1, 298))
        K.check(600 <= tree + 12 <= 700, "X a big Maple's 298 logs (12 XP each, the chopped one at 12) pay %d XP in all (model ~670 + leaves)" % (tree + 12))
        r = [int(FC.credit(JLong(12), JBoolean(False), JInt(2))) for _ in range(50)]
        K.check(all(x == 12 for x in r), "X credit (the game path, ThreadLocalRandom): a whole share pays exactly 12")
        rl = [int(FC.credit(JLong(1), JBoolean(True), JInt(2))) for _ in range(4000)]
        K.check(all(x in (0, 1) for x in rl) and 250 < sum(rl) < 550, "X credit: leaves pay 0 or 1, ~10 %% (%d of 4000)" % sum(rl))
        FC.ENABLED = True
        FC.BROKEN = False
        t = str(FC.text())
        K.check("leaves x0.1" in t and "big trees: 30 logs full, then (30 / log)^2.0" in t, "X text: %s" % t)
        FC.read(_P({"fell.bigTreeFrom": "0"}))
        K.check("every log full" in str(FC.text()), "X text: big trees off")
        FC.read(_P({}))

        # ---- ForXpMig.plan on a 0.4.66 file (the 0.4.66 jar's fresh default file = SkillCfg.DEFAULTS of the OLD jar)
        from jpype import JClass
        LO = T48.loader_for(OLD_JAR)
        d66 = str(JClass(PKG + "SkillCfg", loader=LO).DEFAULTS)
        d67 = str(Cfg.DEFAULTS)
        K.check(FM.plan(d67) is None and MARK_ID in d67, "X plan: the 0.4.67 fresh file carries the marker = nothing to do")
        pl = FM.plan(d66)
        K.check(pl is not None, "X plan: a 0.4.66 file gets an update")
        new = str(pl[0])
        a0, a1 = _plain(d66), _plain(new)
        moved = sorted(k for k in set(a0) | set(a1) if a0.get(k) != a1.get(k))
        want = {}
        for k, v in a0.items():
            if k.startswith("block.Wood_") and (k.endswith("_Trunk") or k.endswith("_Trunk_Full")) and v.startswith("Foraging:"):
                x = int(v.split(":")[1])
                if x in P3_LOG:
                    want[k] = "Foraging:%d" % FX_LOG[P3_LOG.index(x)]
        want.update({"suffix._Trunk": "Foraging:4", "suffix._Trunk_Full": "Foraging:4", "fell.leafXpFactor": "0.1", "fell.bigTreeFrom": "30", "fell.bigTreeFalloff": "2"})
        K.check(moved == sorted(want) and all(a1[k] == v for k, v in want.items()), "X plan: exactly the planned lines move (%d): %s" % (len(moved), [k for k in moved if k not in want][:5]))
        K.check(a1.get("block.Wood_Maple_Trunk") == "Foraging:12" and a1.get("block.Wood_Oak_Trunk") == "Foraging:4" and a1.get("block.Wood_Crystal_Trunk") == "Foraging:496"
                and a1.get("block.Wood_Bamboo_Trunk") == "Foraging:372", "X plan: Maple 12, Oak 4, Crystal (T15) 496, Bamboo (T13) 372 (fix 2 taper)")
        K.check(len(list(pl[1])) == 3 * len(want), "X plan: one change-log row per changed / added line (%d)" % (len(list(pl[1])) // 3))
        K.check(new.count(MARK_ID) == 1 and FM.plan(new) is None, "X plan: the marker once, a second plan = nothing")
        ad = d66.replace("block.Wood_Maple_Trunk=Foraging:120", "block.Wood_Maple_Trunk=Foraging:99")
        pa = FM.plan(ad)
        K.check(_plain(str(pa[0])).get("block.Wood_Maple_Trunk") == "Foraging:99" and "block.Wood_Maple_Trunk=Foraging:99 kept" in str(pa[3])
                and _plain(str(pa[0])).get("block.Wood_Azure_Trunk") == "Foraging:12", "X plan: an admin's Maple 99 is kept + named; Azure still moves: %s" % str(pa[3])[:120])
        cr = d66.replace(chr(10), chr(13) + chr(10))
        pc = str(FM.plan(cr)[0])
        K.check(pc.count(chr(10)) == pc.count(chr(13) + chr(10)) and _plain(pc) == a1, "X plan: a CRLF file stays CRLF, same values")
        hb = d66 + "fell.bigTreeFrom=10" + chr(10)
        ph = FM.plan(hb)
        K.check(_plain(str(ph[0])).get("fell.bigTreeFrom") == "10" and str(ph[0]).count("fell.bigTreeFrom=") == 1, "X plan: an existing fell.bigTreeFrom line is kept, not added twice")
        K.check(FM.plan(None) is None, "X plan: null text = nothing")
    except Exception as e:
        import traceback
        traceback.print_exc()
        K.check(False, "X: run crashed: %s" % str(e)[:400])
    K.save()


def _start(J, lc):
    """the setup() order of the one-time updates (T64.run_live) + ForXpMig, then SkillCfg.load"""
    Cfg, Sto, Hist, CLog, Rows, LF, C, M = J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows"), J("LvFloor"), J("CurveP3Mig"), J("P3Mig")
    C9, M9 = J("CurveP9Mig"), J("P9Mig")
    xp = os.path.join(lc, "xp.properties")
    Cfg.FILE = jpath(xp)
    Sto.DATA.clear()
    Sto.DIR = jpath(os.path.join(lc, "players"))
    Hist.DIR = None
    Rows.HOME = None
    CLog.FILE = None
    CLog.Q.clear()
    LF.NEW_FARM = False
    r = dict((nm, str(J(nm).run())) for nm in T57.MIGS)
    ok = bool(C.run(jpath(lc)))
    r["P3Mig"] = str(M.run()) if ok else ""
    if ok:
        C.after(jpath(lc))
    for nm in ("P4Mig", "PlMigP8", "BmMigP8c", "SkMigP7"):
        r[nm] = str(J(nm).run())
    ok9 = bool(C9.run(jpath(lc)))
    r["P9Mig"] = str(M9.run()) if ok9 else ""
    if ok9:
        C9.after(jpath(lc))
    r["ForXpMig"] = str(J("ForXpMig").run())
    r["load"] = str(Cfg.load())
    return r


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    J = _cls(jar)
    lc = home
    xp = os.path.join(lc, "xp.properties")
    b0 = open(xp, "rb").read()
    t0 = b0.decode("latin-1")
    K.check(MARK_ID not in t0 and "block.Wood_Maple_Trunk=Foraging:120" in t0 and "fell.leafXpFactor=1.0" in t0, "LIVE the live file is the 0.4.66 one (Maple 120, leaves 1.0, no marker)")
    s0 = T53.snapd(lc)
    r1 = _start(J, lc)
    s1 = T53.snapd(lc)
    ch = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
    K.notes.append("LIVE start 1 changed: %s" % ch[:12])
    K.notes.append("LIVE ForXpMig: %s" % r1["ForXpMig"][:300])
    K.check(all(not c.startswith("players/") for c in ch), "LIVE start 1: no player file touched")
    K.check("xp.properties" in ch and any(c.startswith("config-history/") for c in ch) and "config-changes.log" in ch, "LIVE start 1: xp.properties updated, config-history copy, change-log rows: %s" % ch[:8])
    b1 = open(xp, "rb").read()
    t1 = b1.decode("latin-1")
    a0, a1 = _plain(t0), _plain(t1)
    moved = sorted(k for k in set(a0) | set(a1) if a0.get(k) != a1.get(k))
    K.check(all(k.startswith("block.Wood_") or k in ("suffix._Trunk", "suffix._Trunk_Full", "fell.leafXpFactor", "fell.bigTreeFrom", "fell.bigTreeFalloff") for k in moved)
            and len(moved) >= 60, "LIVE start 1: only the Foraging lines moved (%d): %s" % (len(moved), [k for k in moved if not k.startswith("block.Wood_")]))
    K.check(a1["block.Wood_Maple_Trunk"] == "Foraging:12" and a1["block.Wood_Oak_Trunk"] == "Foraging:4" and a1["fell.leafXpFactor"] == "0.1"
            and a1["fell.bigTreeFrom"] == "30" and a1["fell.bigTreeFalloff"] == "2", "LIVE start 1: Maple 12, Oak 4, leaves 0.1, big trees 30 / 2")
    crlf0 = b"\r\n" in b0
    K.check((b"\r\n" in b1) == crlf0 and t1.count(MARK_ID) == 1, "LIVE start 1: the file's own line ending kept (CRLF %s), the marker once" % crlf0)
    l0, l1 = t0.split("\n"), t1.split("\n")
    keep = [ln for ln in l0 if not any(ln.startswith(k + "=") for k in moved)]
    keep1 = [ln for ln in l1[:len(l0)] if not any(ln.startswith(k + "=") for k in moved)]
    K.check(keep == keep1, "LIVE start 1: every other line byte-identical and in place")
    hist = [c for c in ch if c.startswith("config-history/") and c in s1]   # (KEEP=10: the kit prunes the oldest copy)
    K.check(any(s1[c] == b0 for c in hist), "LIVE start 1: the config-history copy is the old file byte for byte")
    log = s1.get("config-changes.log", b"").decode("latin-1")
    K.check(log.count("SkyySkills 0.4.67") >= len(moved) and "block[Wood_Maple_Trunk]" in log, "LIVE start 1: one change-log row per change (%d lines name 0.4.67)" % log.count("SkyySkills 0.4.67"))
    FC = J("FellCfg")
    K.check(int(FC.BIG_FROM) == 30 and abs(float(FC.BIG_FALLOFF) - 2.0) < 1e-12 and abs(float(FC.LEAF_XP_FACTOR) - 0.1) < 1e-12, "LIVE SkillCfg.load reads big trees 30 / 2, leaves 0.1")
    r2 = _start(J, lc)
    s2 = T53.snapd(lc)
    K.check(s2 == s1, "LIVE start 2 changes nothing: %s" % sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k))[:8])
    K.check(r2["ForXpMig"] == "", "LIVE start 2: ForXpMig does nothing (marker)")
    K.save()


def run_live2(out, jar, scratch, home):
    K = HK.Child(out)
    J = _cls(jar)
    xp = os.path.join(home, "xp.properties")
    t0 = open(xp, "rb").read().decode("latin-1")
    t0 = t0.replace("block.Wood_Maple_Trunk=Foraging:120", "block.Wood_Maple_Trunk=Foraging:99")
    open(xp, "wb").write(t0.encode("latin-1"))
    r = _start(J, home)
    t1 = open(xp, "rb").read().decode("latin-1")
    a1 = _plain(t1)
    K.check(a1["block.Wood_Maple_Trunk"] == "Foraging:99" and a1["block.Wood_Maple_Trunk_Full"] == "Foraging:12" and a1["block.Wood_Oak_Trunk"] == "Foraging:4",
            "LIVE2 an admin's Maple 99 is kept; the untouched rows move")
    K.check("block.Wood_Maple_Trunk=Foraging:99 kept" in r["ForXpMig"], "LIVE2 the kept value is named in the log line: %s" % r["ForXpMig"][-200:])
    # a file whose Balance P3 update has not landed: ForXpMig refuses and leaves the file alone (retried next start)
    FM, Cfg, M3 = J("ForXpMig"), J("SkillCfg"), J("P3Mig")
    p3mark = str(M3.MARK_ID)
    old = t0.replace(p3mark, "removed marker")
    K.check(M3.plan(old) is not None and FM.plan(old) is not None, "LIVE2 (setup: with the P3 marker removed P3Mig has work again, ForXpMig too)")
    fake = os.path.join(home, "pending.properties")
    open(fake, "wb").write(old.encode("latin-1"))
    Cfg.FILE = jpath(fake)
    before = open(fake, "rb").read()
    res = str(FM.run())
    K.check(res == "" and open(fake, "rb").read() == before, "LIVE2 a file whose Balance P3 update has not landed is left alone")
    Cfg.FILE = jpath(xp)
    K.save()


if __name__ == "__main__":
    phases = [("static", run_static), ("x", run_x), ("live", run_live), ("live2", run_live2)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
