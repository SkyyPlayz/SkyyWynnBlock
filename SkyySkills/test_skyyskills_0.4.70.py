"""SkyySkills 0.4.70 - harness for HOW TO LEVEL + SHARD XP CANNOT OUTRUN THE CLASS + THE BOOT CHECK WINDOW (tools/skills_0_4_70_patch.py). Build first:
    python tools/skills_0_4_70_patch.py && python SkyySkills/build_skyyskills_0.4.70.py
    python SkyySkills/test_skyyskills_0.4.70.py [--keep]
Phases (each a fresh child JVM: -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes, 0.4.69's patch still regenerates 0.4.69, line endings kept, 2 classes / 0 systems / 0 commands added,
                 the offerX call after paidY and before the per-minute cap, the row line before the row markup, the Stats slot, the 4 + 1 rows, PACK_MAX 18
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.4.69 -> 0.4.70: exactly the planned members (EXPECT)
  SH    EXECUTED ShardLead on a real SkillStore: every band, band edges, custom / clamped settings, enabled off, no class (highest class level, 0 if none),
                 absent class mod, unknown class, a class still following a profile switch, levels not loaded, non-shard sources, the fraction's average;
                 THE REAL PATH: skill:fn:addxp -> BridgeXp.offerX on a stand-in Universe / PlayerRef / World: the BridgeTask queued carries the lowered award
  HL    EXECUTED SkillHelp: every skill's line present on every list row + class row, under 60 characters; defaults, empty, 300 characters, a line that
                 cannot fit, non-ASCII, both column widths, MAX LEVEL / no-class texts; every default line against the real engine-free fit
  PK    EXECUTED ManaGuard.packStep: 17 tries log nothing while a WARN is remembered, try 18 logs each WARN once; a full answer stops at once
  LIVE  start twice on a scratch COPY of the live Skyy_SkyySkills: no file changes at all, code defaults read, a shardxp / help line in the file is read
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): how the rows look at 1080 on a real client; the real SkyyShards Collect / Sell chat line.
"""
import os, sys, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "sk070", "sk")]
_cmp0 = HK.run_compare
_eq00 = HK.Child.eq


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T69 = _mod(os.path.join(HERE, "test_skyyskills_0.4.69.py"), "test_skyyskills_0_4_69")
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T67 = T69.T67
T53 = T69.T68.T53
VERSION = "0.4.70"
PKG = "com.skyy.skills."
GEN = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyskills_0.4.69.py")
PATCH = os.path.join(TOOLS, "skills_0_4_70_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.69.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T69.LIVE_DIR
ADDED = ["ShardLead", "SkillHelp"]
EXPECT = {   # THE changes: BridgeXp.offerX, SkillsPage.build, StatsPage.build, SkillCfg.load, ManaGuard.PACK_MAX (inlined into packStep); the rest = the default file, rows, version texts
    'BridgeXp': ['~m offerX'],
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CurveP9Mig': ['~m run'],
    'ManaGuard': ['~m armReport2', '~m intReport', '~m packReport', '~m packStep'],
    'SkillCfg': ['~m load'],
    'SkillsPage': ['~m build'],
    'SkyySkillsPlugin': ['~m setup'],
    'StatsPage': ['~m build'],
}
HELP = {"Mining": "mine rock", "Foraging": "chop trees", "Farming": "ripe crops", "Fishing": "catch fish", "Ranching": "tame, crate or milk", "Orchard": "apples and berries",
        "Alchemy": "brew potions", "Smithing": "Furnace", "Cooking": "Cooking Bench", "Acrobatics": "run, jump, dodge", "Exploration": "loot chests", "Beastmastery": "pet in a slot",
        "Combat": "once you have a class", "Archery": "bows", "Swordsmanship": "swords", "Assassination": "daggers", "Zen": "bo staves", "Sorcery": "staves", "Fury": "axes", "Divinity": "heal",
        "Battlemagic": "longswords"}


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read().replace("\r\n", "\n")
    o = open(GEN_OLD, encoding="utf8", newline="").read().replace("\r\n", "\n")
    K.check(g.startswith('"""SkyySkills 0.4.70') and g.count('VERSION = "0.4.70"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(")
            and g.count("makeClass(") == o.count("makeClass(") + 2, "S 2 new classes, no new command / system")
    ox = g[g.index("public static long offerX("):g.index("public static long offer(java.util.UUID")]
    K.check(ox.count("ShardLead.apply(") == 1 and ox.index("paidY(") < ox.index("ShardLead.apply(") < ox.index("if (!allow(u, amt))"), "S offerX: after paidY, before the per-minute cap, once")
    K.check("if (grant) amt = {PKG}.ShardLead.apply(u, slot, amt, source);" in ox, "S offerX: only skill:fn:addxp grants")
    K.check("if (!PACK_DONE" in g and g.count("PACK_MAX = 18;") == 1 and "PACK_MAX = 6;" not in g, "S PACK_MAX 18")
    bld = g[g.index("SK_BUILD_SRC = f"):g.index("for _piece in (SK_SHELL_JAVA")]
    K.check(bld.count("SkillHelp.row(prog, sl, tw)") == 1 and bld.index("SkillHelp.row(prog, sl, tw)") < bld.index("{SK_ROW_JAVA}"), "S the row line is built before the row markup")
    K.check("{ST_HELP_JAVA}" in g and "st_help()" in g, "S Stats note slot")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "skills_0_4_69_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn ^ on), sorted("com/skyy/skills/%s.class" % c for c in ADDED), "S the jar adds exactly the 2 classes")
    K.eq(sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


def _load(J, scratch, name):
    Cfg = J("SkillCfg")
    d = os.path.join(scratch, name)
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, "xp.properties")
    open(f, "w", encoding="latin-1", newline="\n").write(str(Cfg.DEFAULTS))
    Cfg.FILE = T67.jpath(f)
    Cfg.load()
    return f


def _xp_for(SD, slot, L):
    from jpype import JInt, JLong
    lo, hi = 0, 2000000000000
    while lo < hi:
        m = (lo + hi) // 2
        if int(SD.levelOf(JInt(slot), JLong(m))) >= L:
            hi = m
        else:
            lo = m + 1
    return lo


def run_sh(out, jar, scratch, _home):
    from jpype import JInt, JLong, JDouble, JClass, JArray, JString
    K = HK.Child(out)
    J = T67._cls(jar)
    SD, ST, LD, P3, BX = J("SkillDefs"), J("SkillStore"), J("ShardLead"), J("P3Xp"), J("BridgeXp")
    P, SHC = T67._P, "shard:mining"
    _load(J, scratch, "sh")
    br = ST.bridge()
    N, MIN, ARCH, MAGE = int(SD.N), int(SD.MINING), int(SD.indexOf("Archer")), int(SD.indexOf("Mage"))
    K.check(bool(LD.ON) and int(LD.LEAD) == 5 and int(LD.LEAD_PCT) == 50 and int(LD.FAR_PCT) == 10, "SH the fresh file: on, 5, 50, 10")
    d = JArray(JClass("long"))(2 * N)
    u = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-000000070000")
    k = str(u)
    ST.DATA.put(k, d)
    fn = J("SkillAddFn")()
    br.put("class:fn:allowed", fn)   # a Function = SkyyClasses is loaded
    br.put("class:" + k, "Archer")
    d[ARCH] = _xp_for(SD, ARCH, 30)
    A = lambda amt=1000, src=SHC, r=0.0, sl=MIN: int(LD.applyR(u, JInt(sl), JLong(amt), JString(src) if src is not None else None, JDouble(r)))

    def mining(L):
        d[MIN] = _xp_for(SD, MIN, L)
        K.eq(int(P3.lvl(u, JInt(MIN))), L, "SH Mining level %d in the store" % L)

    for L, want, why in ((1, 1000, "below"), (29, 1000, "just below"), (30, 1000, "equal to the class"), (31, 500, "lead 1"), (35, 500, "lead 5 (band edge)"), (36, 100, "lead 6"), (45, 100, "far")):
        mining(L)
        K.eq(A(), want, "SH class 30, Mining %d (%s) -> %d of 1000" % (L, why, want))
    # the fraction: whole XP, exact average
    mining(36)
    K.eq([A(3, r=0.0), A(3, r=0.5), A(3, r=0.95), A(9, r=0.05), A(9, r=0.95)], [1, 0, 0, 1, 0], "SH 3 XP x 10 %: 0 or 1 by the random number (0.3 -> paid below 0.3); 9 x 10 %")
    mining(31)
    K.eq(A(1001, r=0.0), 501, "SH 1001 x 50 %, r 0 -> 501 (the .5 paid)")
    K.eq(A(1001, r=0.9), 500, "SH 1001 x 50 %, r 0.9 -> 500")
    t = sum(int(LD.apply(u, JInt(MIN), JLong(3), JString(SHC))) for _ in range(4000))
    K.check(5600 <= t <= 6400, "SH apply: 4000 awards of 3 XP x 50 %% average 1.5 each: %d" % t)
    # other sources unchanged
    mining(45)
    for s in ("collections", "shard", "SHARD:mining", "sacks:craft", "", None):
        K.eq(A(src=s), 1000, "SH source %r unchanged" % s)
    K.eq(A(src="shard:farming"), 100, "SH any shard: source counts (shard:farming)")
    # no class chosen: the highest class level on the profile, 0 if none
    br.remove("class:" + k)
    K.eq(A(), 100, "SH no class chosen, highest class Archery 30, Mining 45 -> x0.1")
    d[MAGE] = _xp_for(SD, MAGE, 44)
    K.eq(int(LD.classLv(u)), 44, "SH no class: classLv = the highest class level (Sorcery 44)")
    K.eq(A(), 500, "SH no class, highest 44, Mining 45 -> x0.5")
    d[ARCH] = 0
    d[MAGE] = 0
    K.eq(int(LD.classLv(u)), 0, "SH no class and no class XP: classLv 0")
    K.eq(A(), 100, "SH no class level at all: Mining 45 -> x0.1")
    mining(3)
    K.eq(A(), 500, "SH no class level at all: Mining 3 -> x0.5")
    d[MIN] = 0
    K.eq(A(), 1000, "SH level 0 against class 0 -> x1")
    d[ARCH] = _xp_for(SD, ARCH, 30)
    br.put("class:" + k, "Archer")
    mining(45)
    # settings
    LD.read(P({"shardxp.leadLevels": "2", "shardxp.leadPct": "25", "shardxp.farPct": "0"}))
    mining(32)
    K.eq(A(), 250, "SH custom: lead 2 at 25 %")
    mining(33)
    K.eq(A(), 0, "SH custom: far 0 % pays nothing (accepted by the caller)")
    LD.read(P({"shardxp.leadLevels": "-3", "shardxp.leadPct": "500", "shardxp.farPct": "-1"}))
    K.check(int(LD.LEAD) == 0 and int(LD.LEAD_PCT) == 100 and int(LD.FAR_PCT) == 0, "SH clamps: lead 0, 100 %, 0 %")
    LD.read(P({"shardxp.leadLevels": "x", "shardxp.leadPct": "y", "shardxp.farPct": "z"}))
    K.check(int(LD.LEAD) == 5 and int(LD.LEAD_PCT) == 50 and int(LD.FAR_PCT) == 10, "SH bad numbers -> the defaults")
    LD.read(P({"shardxp.enabled": "false"}))
    K.check(not bool(LD.ON), "SH read: enabled false")
    mining(45)
    K.eq(A(), 1000, "SH enabled off -> x1")
    LD.read(P({}))
    K.check(bool(LD.ON), "SH missing line = default on")
    K.eq(A(), 100, "SH on again")
    # fail open
    LD.WARNED.clear()
    br.put("class:" + k, "Gardener")
    K.eq([A(), A()], [1000, 1000], "SH unknown class -> x1")
    K.eq(int(LD.WARNED.size()), 1, "SH unknown class logged once")
    br.put("class:" + k, "Archer")
    br.remove("class:fn:allowed")
    K.eq([A(), A()], [1000, 1000], "SH absent class mod -> x1")
    K.eq(int(LD.WARNED.size()), 2, "SH absent class mod logged once")
    br.put("class:fn:allowed", fn)
    br.put("profile:class:" + k, "Mage")
    K.eq(A(), 1000, "SH class still following a profile switch -> x1")
    br.remove("profile:class:" + k)
    J("SkillClass").resync(u)
    u2 = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-000000070001")
    K.eq(int(LD.applyR(u2, JInt(MIN), JLong(1000), JString(SHC), JDouble(0.0))), 1000, "SH levels not loaded -> x1")
    K.eq(int(LD.applyR(None, JInt(MIN), JLong(1000), JString(SHC), JDouble(0.0))), 1000, "SH no player -> unchanged")
    K.eq(int(LD.applyR(u, JInt(99), JLong(1000), JString(SHC), JDouble(0.0))), 1000, "SH a bad slot -> unchanged, no throw")
    K.eq(A(0), 0, "SH 0 XP -> 0")

    # ---- THE REAL PATH: skill:fn:addxp -> SkillAddFn -> BridgeXp.offerX -> a BridgeTask on the world's queue (a stand-in Universe, PlayerRef, World)
    Unsafe = JClass("sun.misc.Unsafe")
    f = Unsafe.class_.getDeclaredField("theUnsafe")
    f.setAccessible(True)
    un = f.get(None)
    UNI, PR, WLD = (JClass("com.hypixel.hytale.server.core.universe." + n) for n in ("Universe", "PlayerRef", "world.World"))
    HM = JClass("java.util.HashMap")

    def setf(cls, obj, name, val):
        fld = cls.class_.getDeclaredField(name)
        fld.setAccessible(True)
        fld.set(obj, val)

    uni, pr, w = un.allocateInstance(UNI.class_), un.allocateInstance(PR.class_), un.allocateInstance(WLD.class_)
    q = JClass("java.util.ArrayDeque")()
    wid = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000700aa")
    setf(WLD, w, "acceptingTasks", JClass("java.util.concurrent.atomic.AtomicBoolean")(True))
    setf(WLD, w, "taskQueue", q)
    setf(PR, pr, "holder", un.allocateInstance(JClass("com.hypixel.hytale.component.Holder").class_))
    setf(PR, pr, "worldUuid", wid)
    pl, wl = HM(), HM()
    pl.put(u, pr)
    wl.put(wid, w)
    setf(UNI, uni, "playersByUuid", pl)
    setf(UNI, uni, "worldsByUuid", wl)
    setf(UNI, None, "instance", uni)
    Long = JClass("java.lang.Long")
    OA = JArray(JClass("java.lang.Object"))

    def award(skill, n, src):
        q.clear()
        r = fn.apply(OA([u, JString(skill), Long(n), JString(src)]))
        t = q.pollFirst()
        return bool(r), (None if t is None else (int(J("BridgeTask").class_.getField("amt").getLong(t)), str(J("BridgeTask").class_.getField("source").get(t))))

    br.put("class:" + k, "Archer")
    mining(45)
    base = int(BX.paidY(u, JInt(MIN), JLong(1000), True, True, False))
    K.check(base > 0, "PATH paidY for 1000 base: %d" % base)
    ok, t = award("Mining", 1000, SHC)
    K.check(ok and t is not None and t[1] == SHC and abs(t[0] - base * 0.1) <= 1, "PATH Mining 45 / class 30: skill:fn:addxp queues x0.1 of paidY (%d): %s" % (base, t))
    ok, t = award("Mining", 1000, "collections")
    K.check(ok and t is not None and abs(t[0] - base) <= 1, "PATH a non-shard source: the full paidY: %s" % (t,))
    mining(31)
    base = int(BX.paidY(u, JInt(MIN), JLong(1000), True, True, False))
    ok, t = award("Mining", 1000, SHC)
    K.check(ok and t is not None and abs(t[0] - base * 0.5) <= 1, "PATH Mining 31 / class 30: x0.5 of paidY (%d): %s" % (base, t))
    mining(30)
    base = int(BX.paidY(u, JInt(MIN), JLong(1000), True, True, False))
    ok, t = award("Mining", 1000, SHC)
    K.check(ok and t is not None and abs(t[0] - base) <= 1, "PATH Mining 30 / class 30: x1 (%d): %s" % (base, t))
    br.put("class:" + k, "Gardener")
    ok, t = award("Mining", 1000, SHC)
    K.check(ok and t is not None, "PATH an unknown class never fails the bridge call: %s" % (t,))
    br.put("class:" + k, "Archer")
    LD.ON = False
    mining(45)
    base = int(BX.paidY(u, JInt(MIN), JLong(1000), True, True, False))
    ok, t = award("Mining", 1000, SHC)
    K.check(ok and t is not None and abs(t[0] - base) <= 1, "PATH enabled off: the full paidY: %s" % (t,))
    LD.ON = True
    LD.FAR_PCT = 0
    ok, t = award("Mining", 1000, SHC)
    K.check(ok and t is None, "PATH 0 % pays nothing, the caller still gets TRUE (its owed XP clears)")
    K.check(fn.apply(OA([u, JString("Mining")])) == JClass("java.lang.Boolean").FALSE, "PATH a malformed call -> FALSE, no throw")
    setf(UNI, None, "instance", None)
    K.save()


def run_hl(out, jar, scratch, _home):
    from jpype import JInt, JString, JClass
    K = HK.Child(out)
    J = T67._cls(jar)
    SD, H, Cfg = J("SkillDefs"), J("SkillHelp"), J("SkillCfg")
    P = T67._P
    f = _load(J, scratch, "hl")
    N = int(SD.N)
    labels = [str(x) for x in SD.LABELS]
    K.eq(sorted(labels), sorted(HELP), "HL the harness knows every skill (21)")
    for s in range(N):
        t = str(H.line(JInt(s)))
        K.check(t and len(t) <= 60 and HELP[labels[s]] in t, "HL %s: %r" % (labels[s], t))
    rows = [int(x) for x in SD.ROW_SLOTS]
    K.eq(sorted(set(rows)), sorted(rows), "HL 13 distinct list rows")
    W = (1272, 1368)
    prog = "706 / 750 XP to level 2"
    r = str(H.row(JString(prog), JInt(int(SD.indexOf("Ranching"))), JInt(1272)))
    K.eq(r, prog + "  -  pick up eggs, wool, meat; tame, crate or milk animals", "HL the Ranching row reads like the task's example")
    for tw in W:
        for s in rows + [int(x) for x in SD.CLASS_SLOT]:
            for p in (prog, "MAX LEVEL - 12.3m XP", "999.9m / 999.9m XP to level 100"):
                out_ = str(H.row(JString(p), JInt(s), JInt(tw)))
                K.check(out_ == p + str(H.SEP) + str(H.line(JInt(s))), "HL %s at %d: the whole line" % (labels[s], tw))
                K.check(int(H.width(JString(out_))) <= tw - 8, "HL %s at %d: fits" % (labels[s], tw))
    # no-class row: the longest XP text there is
    nc = "Old Combat XP (level 12) moves to the first class you choose"
    out_ = str(H.row(JString(nc), JInt(int(SD.COMBAT)), JInt(1272)))
    K.check(out_.startswith(nc + str(H.SEP)) and int(H.width(JString(out_))) <= 1264, "HL the no-class row fits: %r" % out_)
    # fixer: the no-class Combat row and the legacy Stats note do not repeat their own "/class" advice; Beastmastery says what to do; every default line stays short
    cl = str(H.line(JInt(int(SD.COMBAT))))
    K.check("/class" not in cl and "choose" not in cl.lower(), "FIX Combat's line does not repeat the row title / Stats sub-line: %r" % cl)
    for pc in (nc, "Your combat skill is your class skill"):
        K.eq(str(H.row(JString(pc), JInt(int(SD.COMBAT)), JInt(1272))), pc + str(H.SEP) + "defeat monsters once you have a class", "FIX the no-class Combat row reads once: %r" % pc)
    K.eq(str(H.line(JInt(int(SD.indexOf("Beastmastery"))))), "put a pet in a slot, then earn XP in its skill", "FIX the Beastmastery line is plain")
    # fixer: the Server Setup rows say it plainly (no "lead rate" jargon)
    CR = J("CfgRows")
    lb = dict((k_, str(CR.LABELS[int(CR.index(k_))])) for k_ in ("shardxp.leadLevels", "shardxp.leadPct", "shardxp.farPct"))
    K.eq(lb, {"shardxp.leadLevels": "Shard XP: levels just above your class", "shardxp.leadPct": "Shard XP just above your class", "shardxp.farPct": "Shard XP far above your class"}, "FIX plain Server Setup labels")
    K.check(not any("lead rate" in str(CR.HELPS[int(CR.index(k_))]) or "rate beyond" in v_ for k_, v_ in lb.items()), "FIX no 'lead rate' left in the row help")
    # empty row hides
    H.read(P({"help.Mining": ""}))
    K.eq(str(H.line(JInt(int(SD.MINING)))), "", "HL empty row: no line")
    K.eq(str(H.row(JString(prog), JInt(int(SD.MINING)), JInt(1272))), prog, "HL empty row: the XP text alone")
    K.check("chop trees" in str(H.line(JInt(int(SD.FORAGING)))), "HL a missing line = the default")
    # long: cut to MAX on read, and a wide line is cut to fit
    H.read(P({"help.Mining": "W" * 300, "help.Farming": "  spaced out  "}))
    t = str(H.line(JInt(int(SD.MINING))))
    K.eq(len(t), int(H.MAX), "HL 300 characters: kept to MAX 80")
    K.eq(str(H.line(JInt(int(SD.FARMING)))), "spaced out", "HL trimmed")
    p = "999.9m / 999.9m XP to level 100"
    out_ = str(H.row(JString(p), JInt(int(SD.MINING)), JInt(1272)))
    K.check(out_.endswith("...") and out_.startswith(p + str(H.SEP) + "WW") and int(H.width(JString(out_))) <= 1264, "HL a very wide line is cut with ... and fits: width %d" % int(H.width(JString(out_))))
    K.check(int(H.width(JString(out_))) > 1100, "HL the cut uses the room (%d px)" % int(H.width(JString(out_))))
    # no room at all
    K.eq(str(H.fit(JString(p), JString("something"), JInt(100))), p, "HL no room: the XP text alone")
    K.eq(str(H.fit(JString(p), None, JInt(1272))), p, "HL null line")
    # non-ASCII counts as the widest
    K.check(int(H.width(JString("é"))) >= max(int(x) for x in H.W), "HL non-ASCII = at least the widest ASCII width")
    # bounds
    K.eq(str(H.line(JInt(-1))), "", "HL slot -1")
    K.eq(str(H.line(JInt(N))), "", "HL slot N")
    # the file path: an edited line reloads through SkillCfg.load
    open(f, "a", encoding="latin-1", newline="\n").write("help.Fishing=\nhelp.Orchard=my orchard line\n")
    Cfg.load()
    K.check(str(H.line(JInt(int(SD.FISHING)))) == "" and str(H.line(JInt(int(SD.ORCHARD)))) == "my orchard line", "HL SkillCfg.load reads the file (empty hides, custom text)")
    # ---- the Server Setup table, through the kit's own table path (what the in-game page runs): lists every skill, set, empty, remove, too long, not a skill
    Paths, HL = JClass("java.nio.file.Paths"), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    mods = os.path.join(scratch, "hlm")
    d = os.path.join(mods, "Skyy_SkyySkills")
    os.makedirs(d, exist_ok=True)
    f2 = os.path.join(d, "xp.properties")
    t0 = str(Cfg.DEFAULTS).replace("help.Mining=", "#").replace("help.Foraging=", "#")   # a file without those two lines: they still list, as defaults
    open(f2, "w", encoding="latin-1", newline="\n").write(t0)
    Cfg.FILE = T67.jpath(f2)
    Cfg.load()
    Fn, CP, Rows = J("CfgFn"), J("CfgPub"), J("CfgRows")
    CP.start(Paths.get(mods), HL)
    i = int(Rows.index("help"))
    K.check(i >= 0 and bool(Rows.isTable(JInt(i))), "HL the Server Setup row 'help' is a table")
    ks = [str(x) for x in Fn.entryKeys(JInt(i))]
    K.eq(sorted(ks), sorted(HELP), "HL the table lists every skill, even with no file line")
    K.eq(str(Fn.entryValue(JInt(i), "Mining")), str(H.DEF[int(SD.MINING)]), "HL a missing line shows the default")
    TC = lambda e, v, m=0: str(list(Fn.tableChange(JInt(i), JString(e), JString(v) if v is not None else None, JInt(m), None, JString("harness"), JString("yes"), JString("console")))[0])
    K.eq(TC("Mining", "dig for it"), "ok", "HL table: set a line")
    K.eq(TC("Fishing", ""), "ok", "HL table: an empty line")
    K.eq(TC("Orchard", "x" * 81), "bad", "HL table: 81 characters refused")
    K.eq(TC("Gardening", "nope"), "bad", "HL table: not a skill refused")
    CP.shutdown()
    t = open(f2, encoding="latin-1").read()
    K.check("help.Mining=dig for it" in t and "help.Fishing=\n" in t.replace("\r\n", "\n"), "HL the kit wrote the two lines into xp.properties")
    Cfg.load()
    K.check(str(H.line(JInt(int(SD.MINING)))) == "dig for it" and str(H.line(JInt(int(SD.FISHING)))) == "", "HL a restart reads them (text, empty hides)")
    CP.start(Paths.get(mods), HL)
    K.eq(TC("Mining", None, 2), "ok", "HL table: Remove")
    CP.shutdown()
    Cfg.load()
    K.eq(str(H.line(JInt(int(SD.MINING)))), str(H.DEF[int(SD.MINING)]), "HL Remove puts the default back")
    K.save()


def run_pk(out, jar, scratch, _home):
    from jpype import JArray, JString, JClass
    K = HK.Child(out)
    J = T67._cls(jar)
    MG, Cfg = J("ManaGuard"), J("SkillCfg")
    SA = JArray(JString)
    K.eq(int(MG.PACK_MAX), 18, "PK PACK_MAX 18")
    W, I = SA(["warn", "not active"]), SA(["info", "active"])
    def rd():
        MG.PACK_DONE = False
        MG.PACK_TRIES = 0
        for n in ("ITEMS_DONE", "INT_DONE", "MANA_DONE", "ARM_DONE"):
            setattr(MG, n, False)
        for n in ("PACK_PEND", "INT_PEND", "MANA_PEND", "ARM_PEND", "PACK_LAST", "INT_LAST", "MANA_LAST", "ARM_LAST"):
            setattr(MG, n, "")
    rd()
    for t in range(1, 18):
        MG.packStep(W, W, W, W)
        K.check(not bool(MG.PACK_DONE) and str(MG.MANA_LAST) == "", "PK try %d of 18: still waiting, nothing logged" % t)
    MG.packStep(W, W, W, W)
    K.check(bool(MG.PACK_DONE) and str(MG.MANA_LAST) == "not active" and str(MG.PACK_LAST) == "not active" and str(MG.ARM_LAST) == "not active" and str(MG.INT_LAST) == "not active", "PK try 18: the WARNs land, then done")
    rd()
    for t in range(1, 8):
        MG.packStep(W, W, W, W)
    MG.packStep(I, I, I, I)
    K.check(bool(MG.PACK_DONE) and int(MG.PACK_TRIES) == 8 and str(MG.MANA_LAST) == "active", "PK a full answer at try 8 stops at once (assets finished loading)")
    rd()
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JInt
    K = HK.Child(out)
    J = T67._cls(jar)
    xp = os.path.join(home, "xp.properties")
    t0 = open(xp, "rb").read().decode("latin-1")
    K.check("shardxp." not in t0 and "\nhelp." not in t0, "LIVE the live file has no 0.4.70 lines yet")
    s0 = T53.snapd(home)
    T67._start(J, home)
    s1 = T53.snapd(home)
    K.eq(sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k)), [], "LIVE start 1: nothing written (no one-time update)")
    LD, H, SD = J("ShardLead"), J("SkillHelp"), J("SkillDefs")
    K.check(bool(LD.ON) and int(LD.LEAD) == 5 and int(LD.LEAD_PCT) == 50 and int(LD.FAR_PCT) == 10, "LIVE code defaults (the file has no shardxp lines)")
    K.check(all(str(H.line(JInt(s))) for s in range(int(SD.N))), "LIVE every how-to line shows from the code defaults")
    T67._start(J, home)
    K.check(T53.snapd(home) == s1, "LIVE start 2 changes nothing")
    open(xp, "ab").write(("shardxp.enabled=false" + ("\r\n" if "\r\n" in t0 else "\n") + "help.Mining=" + ("\r\n" if "\r\n" in t0 else "\n")).encode("latin-1"))
    J("SkillCfg").load()
    K.check(not bool(LD.ON) and str(H.line(JInt(int(SD.MINING)))) == "", "LIVE the file's shardxp.enabled=false / empty help.Mining are read")
    K.save()


if __name__ == "__main__":
    phases = [("static", run_static), ("sh", run_sh), ("hl", run_hl), ("pk", run_pk), ("live", run_live)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
