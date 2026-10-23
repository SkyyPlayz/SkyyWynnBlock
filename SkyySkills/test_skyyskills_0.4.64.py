"""SkyySkills 0.4.64 - harness for COMBAT INTO CLASS, the SkyySkills part (tools/skills_0_4_64_patch.py). Build first:
    python tools/skills_0_4_64_patch.py && python SkyySkills/build_skyyskills_0.4.64.py
    python SkyySkills/test_skyyskills_0.4.64.py [--keep]
Deploys + rolls back TOGETHER with SkyyTrees 0.6.0, SkyyClasses 0.1.47, SkyyRebirth 0.5.2.
Phases (each a fresh child JVM: -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes, line endings kept, no new class / system / command; the "Class XP" labels, the
                 tree.rally row + its default-file block, tree:reads:SkyySkills lists Rally
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.4.63 -> 0.4.64: exactly the planned members (EXPECT)
  X     EXECUTED moveLegacy (the legacy Combat slot ADDED to a class slot that already has XP, the paid-level marker only into an empty
                 one, a non-class slot / no legacy XP = -1, twice = once), foldHistory (a verified copy, kept once), foldLog (one line with
                 the Undo), Rally (SkillV3.rally = tree.rally x rank, capped at its max rank, 0 without SkyyTrees; HpRegen.rateFor adds it
                 out of combat only; tree.rally read + clamped from the file)
  W     wiring   bytecode: Perks.migrate copies History BEFORE moveLegacy and logs after it
  LIVE  start twice on a scratch COPY of the live Skyy_SkyySkills (every one-time update + load): nothing of 0.4.64's own written; every
        player file's legacy Combat line named (all 0 on NewBetaTest = nothing to fold)
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): the fold's chat line at login (Perks.migrate needs a PlayerRef), the Rally regen on a live Health stat.
"""
import os, sys, subprocess, importlib.util, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "cls060", "sk")]


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T62 = _mod(os.path.join(HERE, "test_skyyskills_0.4.62.py"), "test_skyyskills_0_4_62")
T57, T48, T53 = T62.T57, T62.T48, T62.T53
jpath, _props = T62.jpath, T62._props
VERSION = "0.4.64"
PKG = "com.skyy.skills."
GEN = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyskills_0.4.63.py")
PATCH = os.path.join(TOOLS, "skills_0_4_64_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.63.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T62.LIVE_DIR
ADDED = []
EXPECT = {   # checked 2026-10-23 (the class compare vs 0.4.63 of the first harness run; CfgFile / CfgFn / CfgRows / CurveP9Mig / ManaGuard / SkillCfg /
            # SkyySkillsPlugin = the version text + the tree.rally row / default block; the rest = tools/skills_0_4_64_patch.py's changes)
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CurveP9Mig': ['~m run'],
    'HpRegen': ['+f RALLY', '~<clinit>', '~m rateFor', '~m read'],
    'ManaGuard': ['~m armReport2', '~m intReport', '~m packReport'],
    'Perks': ['~m migrate'],
    'SkillCfg': ['~m load'],
    'SkillStore': ['+f FOLDNX', '+m foldHistory', '+m foldHistory0', '+m foldLog', '~<clinit>', '~m moveLegacy'],   # fix round 2: + the 30 s retry gate
    'SkillV3': ['+f KEY_RALLY', '+f MAX_RALLY', '+m rally', '~m reads'],
    'SkyySkillsPlugin': ['~m setup'],
}


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyySkills 0.4.64') and g.count('VERSION = "0.4.64"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    for k in ("perHealth", "min", "max", "default", "role"):
        K.check(('("combat.%s", "Class XP' % k) in g and ('("combat.%s", "Combat XP' % k) not in g, "S the combat.%s row says Class XP (key unchanged)" % k)
    K.check(g.count('CFG_ROWS.append(("tree.rally", "Rally regen a rank"') == 1, "S the tree.rally Server Setup row")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def _fn(JImplements, JOverride, f):
    @JImplements("java.util.function.Function")
    class Fn(object):
        @JOverride
        def apply(self, a):
            return f(a)
    return Fn()


def run_x(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg, Sto, SD, SV3, HR = J("SkillCfg"), J("SkillStore"), J("SkillDefs"), J("SkillV3"), J("HpRegen")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    UUID, Int = JClass("java.util.UUID"), JClass("java.lang.Integer")
    N, C = int(SD.N), int(SD.COMBAT)
    CS = [int(x) for x in SD.CLASS_SLOT]
    names = [str(x) for x in SD.NAMES]
    K.check(len(CS) >= 2 and C not in CS, "X a legacy Combat slot (%d) apart from the class slots %s" % (C, CS))
    s1, s2 = CS[0], CS[1]

    def arr(vals):
        a = jpype.JArray(jpype.JLong)(2 * N)
        for i, v in vals.items():
            a[i] = v
        return a
    d = arr({C: 500, N + C: 3, s1: 1200, N + s1: 7})
    x = int(Sto.moveLegacy(d, s1))
    K.eq([x, int(d[s1]), int(d[N + s1]), int(d[C]), int(d[N + C])], [500, 1700, 7, 0, 0], "X moveLegacy: the old Combat XP is ADDED to a class slot with XP (its paid marker kept), Combat 0")
    K.eq(int(Sto.moveLegacy(d, s1)), -1, "X moveLegacy twice = once (-1: nothing left)")
    # fix round (critics A2 / B1): Combat paid levels 1-30, the class slot 1-3 - after the move only levels above 30 pay again
    ecum0 = SD.ECUM
    SD.ECUM = jpype.JArray(jpype.JLong)([100 * L_ * L_ for L_ in range(61)])   # a test class table (SkillCfg.load sets the real one in game)
    top = min(35, int(SD.levelOf(s1, 10 ** 15)))
    big = 1
    while int(SD.levelOf(s1, big)) < top:
        big = big * 2
    cm = top - 5
    d = arr({C: big, N + C: cm, s1: 50, N + s1: 3})
    Sto.moveLegacy(d, s1)
    lvn = int(SD.levelOf(s1, int(d[s1])))
    K.check(lvn >= top and cm > 3 and int(d[N + s1]) == cm, "FIX A2 a class slot with XP takes min(Combat's paid marker %d, the new level %d) - no coins twice: marker %d" % (cm, lvn, int(d[N + s1])))
    d = arr({C: 500, N + C: 40, s1: 50, N + s1: 1})
    Sto.moveLegacy(d, s1)
    lvn = int(SD.levelOf(s1, int(d[s1])))
    K.check(int(d[N + s1]) == max(1, min(40, lvn)), "FIX A2 the marker never goes above the new level (%d -> marker %d)" % (lvn, int(d[N + s1])))
    SD.ECUM = ecum0
    d = arr({C: 400, N + C: 2})
    K.eq([int(Sto.moveLegacy(d, s2)), int(d[s2]), int(d[N + s2])], [400, 400, 2], "X an empty class slot also takes the old paid-level marker (the 0.3 rule)")
    d = arr({C: 400})
    K.eq([int(Sto.moveLegacy(d, 0 if 0 not in CS else C)), int(d[C])], [-1, 400], "X a non-class slot: nothing moves")
    K.eq(int(Sto.moveLegacy(arr({s1: 9}), s1)), -1, "X no legacy XP: -1")
    # History + log
    hd = os.path.join(scratch, "x")
    os.makedirs(os.path.join(hd, "players"), exist_ok=True)
    Sto.DIR = jpath(os.path.join(hd, "players"))
    k = "00000000-0000-0000-0000-000000064001"
    f = os.path.join(hd, "players", k + ".properties")
    body = b"Combat=500\r\nWarrior=1200\r\n"
    open(f, "wb").write(body)
    K.check(bool(Sto.foldHistory(k)), "X foldHistory: copied")
    h = os.path.join(hd, "history", "combatfold", k + ".properties")
    K.check(os.path.isfile(h) and open(h, "rb").read() == body, "X history/combatfold = the file byte for byte")
    K.check(bool(Sto.foldHistory(k)) and open(h, "rb").read() == body and len(os.listdir(os.path.dirname(h))) == 1, "X a second call on the same file keeps the one copy")
    body2 = b"Combat=300\r\nWarrior=1700\r\n"
    open(f, "wb").write(body2)
    K.check(bool(Sto.foldHistory(k)) and open(h, "rb").read() == body2, "FIX A3 a changed file (after an Undo / a failed try) gets a FRESH copy")
    kept = [n for n in os.listdir(os.path.dirname(h)) if n.startswith(k + ".properties.")]
    K.check(len(kept) == 1 and open(os.path.join(os.path.dirname(h), kept[0]), "rb").read() == body, "FIX A3 the older copy is kept aside (%s)" % kept)
    K.check(bool(Sto.foldHistory("00000000-0000-0000-0000-000000064999")), "X no file = nothing to copy (true)")
    # fix round 2 (critics: a failing copy re-saved + warned every tick): after a failure the next try waits 30 s
    k3 = "00000000-0000-0000-0000-000000064003"
    open(os.path.join(hd, "players", k3 + ".properties"), "wb").write(b"Combat=50\r\n")
    hb = os.path.join(hd, "history", "combatfold", k3 + ".properties")
    os.makedirs(hb, exist_ok=True)   # a directory in the way = the copy fails
    import time as _t
    t0 = int(_t.time() * 1000)
    K.check(not bool(Sto.foldHistory(k3)), "FIX2 a directory in the way: the copy fails (waits)")
    nx = Sto.FOLDNX.get(k3)
    K.check(nx is not None and t0 + 29000 <= int(nx) <= int(_t.time() * 1000) + 30000, "FIX2 the next try is 30 s later (%s)" % nx)
    os.rmdir(hb)
    K.check(not bool(Sto.foldHistory(k3)) and not os.path.exists(hb), "FIX2 within the 30 s nothing is tried (no save, no warning) even once the way is clear")
    Sto.FOLDNX.put(k3, JClass("java.lang.Long")(0))
    K.check(bool(Sto.foldHistory(k3)) and os.path.isfile(hb) and Sto.FOLDNX.get(k3) is None, "FIX2 after the 30 s it copies (and forgets the wait)")
    Sto.foldLog(k, "legacy Combat XP 500 added to Warrior (1200 -> 1700)")
    lg = open(os.path.join(hd, "combatfold-changes.log"), encoding="utf-8").read()
    K.check(lg.count("\n") == 1 and ("\t" + k + "\tcombatfold\t") in lg and "Undo: stop the server, copy history/combatfold/" + k in lg, "X combatfold-changes.log: one tab-separated line with the Undo: %r" % lg[:160])
    # Rally
    u = UUID.fromString("00000000-0000-0000-0000-000000064002")
    br = Sto.bridge()
    K.eq([str(SV3.KEY_RALLY), int(SV3.MAX_RALLY), float(HR.RALLY)], ["Skill.Combat.b2.r4b", 3, 3.0], "X Rally: its key, 3 ranks, 3 % a rank")
    K.check("Skill.Combat.b2.r4b" in str(SV3.READS), "X tree:reads:SkyySkills lists Rally: %s" % SV3.READS)
    K.eq(float(SV3.rally(u)), 0.0, "X no SkyyTrees: no Rally")
    RK = {"r": 2}
    br.put("tree:fn:level", _fn(JImplements, JOverride, lambda a: Int(RK["r"]) if str(a[1]) == "Skill.Combat.b2.r4b" else Int(0)))
    K.eq(float(SV3.rally(u)), 6.0, "X Rally 2 = +6 %")
    RK["r"] = 9
    K.eq(float(SV3.rally(u)), 9.0, "X Rally capped at its 3 ranks")
    RK["r"] = 2
    br.put("skill:overall:" + str(u), Int(30))
    out_r, fight_r = float(HR.rateFor(u, False)), float(HR.rateFor(u, True))
    HR.RALLY = 0.0
    out_0, fight_0 = float(HR.rateFor(u, False)), float(HR.rateFor(u, True))
    HR.RALLY = 3.0
    K.check(fight_r == fight_0 and out_r > out_0 > 0.0, "X rateFor: Rally adds out of combat only (out %.4f vs %.4f, fight %.4f = %.4f)" % (out_r, out_0, fight_r, fight_0))
    # tree.rally from the file
    cf = os.path.join(hd, "xp.properties")
    gsrc = open(GEN, encoding="utf-8").read()
    K.check("tree.rally" in gsrc and 'clampD(@PKG@.SkillCfg.dbl(p, "tree.rally", 3.0), 3.0, 0.0, 50.0)' in gsrc, "X tree.rally read + clamped 0..50 (default 3)")
    K.save()


def run_w(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cn, mn):
        bos = BOS()
        for m in cp.get(PKG + cn).getDeclaredMethods():
            if str(m.getName()) == mn:
                IP(PS(bos)).print_(m)
        return str(bos.toString())
    m = code("Perks", "migrate")
    K.check("SkillStore.foldHistory" in m and "SkillStore.moveLegacy" in m and "SkillStore.foldLog" in m
            and m.index("SkillStore.foldHistory") < m.index("SkillStore.moveLegacy") < m.index("SkillStore.foldLog"), "W Perks.migrate: History copy, then the move, then the log line")
    K.check("SkillV3.rally" in code("HpRegen", "rateFor"), "W HpRegen.rateFor reads Rally")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    lc = os.path.join(os.path.dirname(home), "copy64")
    shutil.copytree(home, lc)
    L = T48.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Cfg, Sto, Hist, CLog, Rows, LF, C, M, SD = J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows"), J("LvFloor"), J("CurveP3Mig"), J("P3Mig"), J("SkillDefs")
    C9, M9 = J("CurveP9Mig"), J("P9Mig")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    xp = os.path.join(lc, "xp.properties")

    def start():
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
        r["load"] = str(Cfg.load())
        return r
    s0 = T53.snapd(lc)
    r1 = start()
    s1 = T53.snapd(lc)
    ch = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
    K.notes.append("LIVE start 1 changed: %s" % ch[:12])
    K.check(all(not c.startswith("players/") for c in ch) and "xp.properties" not in ch, "LIVE start 1 on the live copy: no player file, no xp.properties change (0.4.63 is live: its one-time updates are done): %s" % ch[:8])
    K.eq(float(J("HpRegen").RALLY), 3.0, "LIVE an old xp.properties without tree.rally reads the default 3")
    C_ = int(SD.COMBAT)
    pd = os.path.join(lc, "players")
    legacy = {}
    for fn in sorted(os.listdir(pd)):
        if fn.endswith(".properties"):
            pr = _props(open(os.path.join(pd, fn), "rb").read())
            legacy[fn[:-11]] = pr.get(str(SD.NAMES[C_]), "(none)")
    K.notes.append("LIVE legacy Combat lines: %s" % legacy)
    K.check(all(v in ("0", "(none)") for v in legacy.values()), "LIVE every live profile's legacy Combat XP is 0 (nothing to fold): %s" % legacy)
    r2 = start()
    s2 = T53.snapd(lc)
    K.check(s2 == s1, "LIVE start 2 changes nothing: %s" % sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k))[:8])
    K.save()


if __name__ == "__main__":
    phases = [("static", run_static), ("x", run_x), ("w", run_w), ("live", run_live)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
