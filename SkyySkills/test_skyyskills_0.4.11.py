"""SkyySkills 0.4.11 - bare-JVM harness for the Priest heal XP round (tools/skills_0_4_11_patch.py): the three heal rows are the FINAL heal
XP (divinity.healXpPerHp 1, divinity.healXpPerHpSelf 1.25, divinity.healXpMaxPerMinute 900) - healing no longer goes through the class
skill XP multiplier (HealXp.offer -> BridgeXp.offerX(..., cls false)); kills, party shares and grants keep it. One-time HealMig update of
an existing xp.properties.

    python SkyySkills/test_skyyskills_0.4.11.py [--jar <SkyySkills-0.4.11.jar>] [--old <SkyySkills-0.4.10.jar>] [--classes <SkyyClasses jar>]
                                                [--dir <scratch>] [--live <Skyy_SkyySkills folder>] [--keep]

Build first (python tools/skills_0_4_11_patch.py, then python SkyySkills/build_skyyskills_0.4.11.py). The old jar = the SET pin 0.4.10, the
Classes jar = the SET pin of SkyyClasses (0.1.10, the skill:fn:healxp caller). Child processes start fresh JVMs (the game's own JRE,
-Xverify:all, -XX:-UsePerfData, HytaleServer.jar + the jars; TEMP / TMP / java.io.tmpdir in the scratch folder). The live world is READ
ONLY: its Skyy_SkyySkills folder is copied into the scratch folder and only that copy is ever written.
  A  every class of the 0.4.11 jar AND of the 0.4.10 jar loads and initializes under -Xverify:all
  C  the real loader: a fresh file = 1 / 1.25 / 900 (code = file = row defaults), the marker once above the Divinity block, the 0.4.11
     default file = the 0.4.10 one with exactly the version line, the marker, the 3 heal values and the rewritten comment lines changed;
     missing heal lines -> the code defaults 1 / 1.25 / 900; the blocks appended to an old file carry 1 / 1.25 / 900
  H  heal XP END TO END from the real SkyyClasses 0.1.10 jar (HealTask.xp / xpSelf = its skill:fn:healxp calls) -> SkillHealFn ->
     HealXp.offer -> BridgeXp.offerX -> BridgeTask (stand-in world runs it at once) -> gain3, at the defaults (class skill XP x3):
     50 HP on others = +50, 40 HP on yourself = +50, 3 HP = +3, 4 HP self = +5; fractions by chance averaged (1 HP self = 1 or 2, mean
     1.25; 2.5 HP on others = 2 or 3, mean 2.5); a non-Priest gets nothing
  M  the class skill XP multiplier at x1 / x5 / x0: heal XP stays 50 / 50 (and the cap 900), the Stats line stays the same; kill XP
     follows it (a 100 HP kill 20 / 100 / 0, 10 real kills +200 / +1000 / +0); a class skill grant (paid, cls true) still multiplied
  X  the cap counts FINAL heal XP: 3 x 300 HP on others = 900, the next heal refused; 720 HP on yourself = 900; others + self share it;
     the general XP multiplier 2 comes after the cap (50 HP = 100, a capped minute 1,800, the Stats line shows it); bridge.maxXpPerMinute
     still counts the paid XP
  K  kill XP / party share / grants / gathering = the 0.4.10 jar's at the defaults (x3): every health, combat.role, real awards
  S  texts: the Stats line "Healing pays 1 Divinity XP per HP on others, 1.25 on yourself (max 900 a minute)", the ready-line text,
     StatsPage.how() of every skill = 0.4.10's
  R  the Server Setup rows: same 174 keys in the same order; only the 3 heal rows (defaults 1 / 1.25 / 900, help, the others label)
     and classSkill.xpMultiplier's help changed
  L  HealMig on scratch COPIES of the live data: (1) start twice in the plugin's order (ManaMig.run -> HealMig.run -> SkillCfg.load -> kit
     history -> ManaMig.keepCopy): start 1 rewrites exactly the untouched 0.2 / 0.25 / 300 lines + the old default comment lines + the
     marker, History version = the old bytes, 3 config-changes.log lines (Undo), DivCfg 1 / 1.25 / 900; start 2 writes nothing;
     (2) an EDITED copy (healXpPerHp=0.3, CRLF, a non-ASCII byte): 0.3 kept and logged, the others updated, CRLF and every other byte
     kept, 2 log lines, again = nothing; (3) a file without heal lines: only the marker; (4) config-history unwritable: untouched
  F  class bytes 0.4.10 vs 0.4.11: + HealMig; BridgeXp (+ paidX / offerX; paid / offer delegate), HealXp (offer -> offerX cls false),
     DivCfg (defaults, read, ensureSelf text, statsLine), SkillCfg (<clinit>: the class skill XP block text), the kit's CfgRows / CfgFile
     (<clinit>), the plugin (setup: HealMig.run) change beyond the version; KillSys, SkillXp, PartyXp, SkillHealFn (the SkyyClasses
     contract), SkillAddFn, ManaMig ... byte-identical or version only; manifest Version / Name / Description only
Nothing is deployed. Default scratch folder: tools/dev/scratch/skills0411/harness (deleted at the end unless --keep; --dir must be a folder
INSIDE tools/dev/scratch/). Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.4.11", "0.4.10"
PKG = "com.skyy.skills."
HEALTHS = [-1.0, 2.0, 5.0, 7.0, 20.0, 37.0, 100.0, 250.0, 1000.0, 2500.0, 10000.0]
ROLE = "Skyy_Test_Boss"
CLASS_SLOTS = [5, 6, 7, 8, 9, 14, 15]
OTHER_SLOTS = [0, 1, 2, 3, 4, 10, 11, 12, 13]
ARCHERY, DIVINITY, MINING, ALCHEMY, SMITHING, COOKING, EXPLORATION = 5, 15, 0, 10, 11, 12, 13
STATS = "Healing pays 1 Divinity XP per HP on others, 1.25 on yourself (max 900 a minute)"
HEAL_KEYS = ["divinity.healXpPerHp", "divinity.healXpPerHpSelf", "divinity.healXpMaxPerMinute"]


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


def _pin(mod, dflt):
    t = open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8").read()
    m = re.search(r'\("%s", "([0-9.]+)"\)' % mod, t[t.index("SET = ["):])
    return m.group(1) if m else dflt


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skills0411", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyySkills-%s.jar" % OLD_VERSION)))
CLASSES_JAR = os.path.abspath(arg("--classes", os.path.join(ROOT, "SkyyClasses", "SkyyClasses-%s.jar" % _pin("SkyyClasses", "0.1.10"))))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySkills")))
LIVE = os.path.join(LIVE_DIR, "xp.properties")
KEEP = "--keep" in sys.argv
FAILS, OKS, GUARD_OK = [], [0], [False]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def _jvm_start(cp, verify=True):
    import jpype
    import skyybuild as B
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    opts = (["-Xverify:all"] if verify else []) + ["-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp]
    jpype.startJVM(jvm, *opts, classpath=[B.SERVER_JAR] + list(cp), convertStrings=True)
    return B


# ============================================================================================ child: the javassist stand-ins
def run_mkfake(out_dir):
    """skyytest.FakeHandler extends PacketHandler (writeNoCache counts packets) and skyytest.FakeWorld extends World (execute runs the
    task at once on the calling thread = 'the world thread'); both Unsafe-allocated (the 0.4.10 harness stand-ins)."""
    import jpype
    from jpype import JClass
    import skyybuild as B
    jpype.startJVM(B._jvm(), "-XX:-UsePerfData", classpath=[B.JAVASSIST], convertStrings=True)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    CtField, CtNewMethod = JClass("javassist.CtField"), JClass("javassist.CtNewMethod")
    h = cp.makeClass("skyytest.FakeHandler")
    h.setSuperclass(cp.get("com.hypixel.hytale.server.core.io.PacketHandler"))
    h.addField(CtField.make("public static volatile int SENT = 0;", h))
    h.addMethod(CtNewMethod.make("public void writeNoCache(com.hypixel.hytale.protocol.ToClientPacket p) { SENT = SENT + 1; }", h))
    h.writeFile(out_dir)
    w = cp.makeClass("skyytest.FakeWorld")
    w.setSuperclass(cp.get("com.hypixel.hytale.server.core.universe.world.World"))
    w.addField(CtField.make("public static volatile int RAN = 0;", w))
    w.addMethod(CtNewMethod.make("public void execute(java.lang.Runnable r) { RAN = RAN + 1; r.run(); }", w))
    w.writeFile(out_dir)


def load_all(jar):
    from jpype import JClass
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    loaded, fails = 0, []
    for n in names:
        try:
            Cls.forName(n, True, loader)
            loaded += 1
        except Exception as e:
            fails.append("%s: %s" % (n, e))
    return {"jar": jar, "classes": len(names), "loaded": loaded, "load_fails": fails, "data": {}}


def rows_of(Rows):
    cols = ("KEYS", "LABELS", "CATS", "TYPES", "DEFS", "MINS", "MAXS", "OPTS", "UNITS", "FLAGS", "HELPS")
    arrs = [[str(x) for x in getattr(Rows, c)] for c in cols]
    return {"rows": [list(r) for r in zip(*arrs)]}


def common(jar, extra_cp):
    """JVM + the jar's classes; returns (res, ns) with helpers shared by the old and the new run"""
    from jpype import JClass
    _jvm_start([jar] + extra_cp)
    res = load_all(jar)
    Paths, JStr, Arr = JClass("java.nio.file.Paths"), JClass("java.lang.String"), JClass("java.lang.reflect.Array")

    def path(p):
        return Paths.get(p, Arr.newInstance(JStr.class_, 0))
    return res, path


def defaults_part(D, Cfg, Dv, Sp, Rows, Bx, path, work):
    """numbers both jars must agree on (or the harness compares): kill XP at the defaults, grants / gathering paid, how(), rows"""
    from jpype import JClass, JFloat
    UUID = JClass("java.util.UUID")
    f = os.path.join(work, "xp.properties")
    if os.path.exists(f):
        os.remove(f)
    Cfg.FILE = path(f)
    D["load"] = str(Cfg.load())
    D["defaults"] = open(f, "rb").read().decode("latin-1")
    D["kill"] = [int(Cfg.classXp(ARCHERY, Cfg.combatXp(None, JFloat(h)))) for h in HEALTHS]
    D["base"] = [int(Cfg.combatXp(None, JFloat(h))) for h in HEALTHS]
    D["other"] = dict((str(s), [int(Cfg.classXp(s, x)) for x in (1, 7, 20, 500)]) for s in OTHER_SLOTS)
    u = UUID(0x5117, 99)
    D["paid"] = [int(Bx.paid(u, MINING, 500, True)), int(Bx.paid(u, ALCHEMY, 40, False)), int(Bx.paid(u, SMITHING, 12, False)),
                 int(Bx.paid(u, COOKING, 30, True)), int(Bx.paid(u, EXPLORATION, 25, True)), int(Bx.paid(u, 4, 9, True)),
                 int(Bx.paid(u, ARCHERY, 100, True)), int(Bx.paid(u, DIVINITY, 10, False))]
    D["scaled"] = [int(Cfg.scaled(x)) for x in (1, 8, 40)]
    D["resolve"] = dict((i, [int(x) for x in Cfg.resolve(i)]) for i in ("Ore_Iron", "Rock_Stone", "Plant_Crop_Wheat_Block", "Wood_Oak_Trunk"))
    D["how"] = dict((str(s), str(Sp.how(s))) for s in CLASS_SLOTS + OTHER_SLOTS)
    D["statsLine"] = str(Dv.statsLine())
    D["divText"] = str(Dv.text())
    D["div"] = [float(Dv.PER_HP), float(Dv.PER_HP_SELF), int(Dv.MAX_MIN)]
    D["rows"] = rows_of(Rows)
    D["divDefaults"] = [str(Dv.DEFAULTS), str(Dv.SELF_DEFAULTS), str(Cfg.CLASS_DEFAULTS)]


# ============================================================================================ child: the 0.4.10 jar (baseline numbers)
def run_old(jar, out):
    from jpype import JClass
    res, path = common(jar, [])
    if not res["load_fails"]:
        work = os.path.join(SCRATCH, "old")
        os.makedirs(work, exist_ok=True)
        defaults_part(res["data"], JClass(PKG + "SkillCfg"), JClass(PKG + "DivCfg"), JClass(PKG + "StatsPage"), JClass(PKG + "CfgRows"),
                      JClass(PKG + "BridgeXp"), path, work)
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: the 0.4.11 jar (+ SkyyClasses)
def run_new(jar, out, fake, classes):
    from jpype import JClass, JFloat
    res, path = common(jar, [fake, classes])
    if res["load_fails"]:
        json.dump(res, open(out, "w"), indent=1)
        return
    D = res["data"]
    UUID, CHM, Props = JClass("java.util.UUID"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.Properties")
    Cfg, Xp, Store = JClass(PKG + "SkillCfg"), JClass(PKG + "SkillXp"), JClass(PKG + "SkillStore")
    Bx, Bc, Hx, Px = JClass(PKG + "BridgeXp"), JClass(PKG + "BridgeCfg"), JClass(PKG + "HealXp"), JClass(PKG + "PartyXp")
    Dv, Sp, Rows, Mig, Hist = JClass(PKG + "DivCfg"), JClass(PKG + "StatsPage"), JClass(PKG + "CfgRows"), JClass(PKG + "ManaMig"), JClass(PKG + "CfgHist")
    HMig, CLog = JClass(PKG + "HealMig"), JClass(PKG + "CfgLog")
    HealFn, AddFn = JClass(PKG + "SkillHealFn"), JClass(PKG + "SkillAddFn")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Universe, Holder = JClass("com.hypixel.hytale.server.core.universe.Universe"), JClass("com.hypixel.hytale.component.Holder")
    FakeH, FakeW = JClass("skyytest.FakeHandler"), JClass("skyytest.FakeWorld")
    JDouble, JBool, JLong, JObj = JClass("java.lang.Double"), JClass("java.lang.Boolean"), JClass("java.lang.Long"), JClass("java.lang.Object")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    def getf(obj, cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f.get(obj)

    bridge = Store.bridge()
    work = os.path.join(SCRATCH, "new")
    os.makedirs(work, exist_ok=True)
    defaults_part(D, Cfg, Dv, Sp, Rows, Bx, path, work)
    D["marker"] = str(HMig.MG_MARK)
    D["docpairs"] = [[str(a), str(b)] for a, b in zip(HMig.DOC_OLD, HMig.DOC_NEW)]
    Store.DIR = path(os.path.join(work, "players"))
    uni = U.allocateInstance(Universe.class_)
    PLAYERS, WORLDS = CHM(), CHM()
    setf(uni, Universe, "playersByUuid", PLAYERS)
    setf(uni, Universe, "players", PLAYERS.values())
    setf(uni, Universe, "worldsByUuid", WORLDS)
    setf(None, Universe, "instance", uni)
    world = U.allocateInstance(FakeW.class_)
    wuid = UUID(0x3011D, 1)
    WORLDS.put(wuid, world)
    handler = U.allocateInstance(FakeH.class_)
    holder = U.allocateInstance(Holder.class_)

    def mkpr(n, name):
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", UUID(0x5117, n))
        setf(pr, PRef, "username", name)
        setf(pr, PRef, "packetHandler", handler)
        setf(pr, PRef, "worldUuid", wuid)
        setf(pr, PRef, "holder", holder)
        PLAYERS.put(UUID(0x5117, n), pr)
        return pr

    def xp_of(u, slot):
        return int(Store.data(u)[slot])

    def cfg_file(name, text):
        d = os.path.join(work, "cfg-" + name)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        f = os.path.join(d, "xp.properties")
        if text is not None:
            open(f, "wb").write(text)
        Cfg.FILE = path(f)
        return f

    # ---------------------------------------------------------------- C: the loader
    C = {}
    f = cfg_file("fresh", None)
    C["text"] = str(Cfg.load())
    fresh = open(f, "rb").read()
    C["div"] = [float(Dv.PER_HP), float(Dv.PER_HP_SELF), int(Dv.MAX_MIN)]
    Cfg.load()
    C["again_same"] = open(f, "rb").read() == fresh
    nokeys = b"".join(ln for ln in fresh.splitlines(True) if not any(ln.startswith(k.encode() + b"=") for k in HEAL_KEYS))
    cfg_file("nokeys", nokeys)
    Cfg.load()
    C["nokeys"] = [float(Dv.PER_HP), float(Dv.PER_HP_SELF), int(Dv.MAX_MIN), nokeys.count(b"divinity.healXpPerHp=")]
    f = cfg_file("old", b"# a SkyySkills 0.4.3 file\nmultiplier=1.0\n")
    Cfg.load()
    o1 = open(f, "rb").read().decode("latin-1")
    C["old"] = [float(Dv.PER_HP), float(Dv.PER_HP_SELF), int(Dv.MAX_MIN), o1.count("\ndivinity.healXpPerHp=1\n"),
                o1.count("\ndivinity.healXpPerHpSelf=1.25\n"), o1.count("\ndivinity.healXpMaxPerMinute=900\n"), str(HMig.MG_MARK) in o1]
    D["C"] = C
    LINE = b"classSkill.xpMultiplier=3.0\n"

    def at(mult, extra=b"", name="m"):
        cfg_file(name, fresh.replace(LINE, ("classSkill.xpMultiplier=%s\n" % mult).encode("latin-1")) + extra)
        return str(Cfg.load())

    # ---------------------------------------------------------------- players
    skyy = mkpr(1, "Skyy")
    u1 = UUID(0x5117, 1)
    bridge.put("class:" + str(u1), "Archer")
    mkpr(3, "Pria")
    u3 = UUID(0x5117, 3)
    bridge.put("class:" + str(u3), "Priest")
    hfn = HealFn()
    bridge.put("skill:fn:healxp", hfn)
    hwin, bwin = getf(None, Hx, "HWIN"), getf(None, Bx, "WIN")
    HT = None
    try:
        HT = JClass("com.skyy.classes.HealTask")
        D["classes_err"] = None
    except Exception as e:
        D["classes_err"] = repr(e)

    def heal(hp, self_=False, u=u3, via_classes=True):
        """SkyyClasses 0.1.10's own call (HealTask.xp / xpSelf -> skill:fn:healxp), else SkillHealFn with the same arguments"""
        before = xp_of(u, DIVINITY)
        if via_classes and HT is not None:
            if self_:
                HT.xpSelf(u, float(hp))
            else:
                HT.xp(u, float(hp))
            ok = None
        else:
            a = [u, JDouble(hp), "classes:heal:self" if self_ else "classes:heal", str(u)]
            if self_:
                a.append(JBool.TRUE)
            ok = bool(hfn.apply(JObj[:](a)))
        return [ok, xp_of(u, DIVINITY) - before]

    def fresh_windows():
        hwin.clear()
        bwin.clear()

    # ---------------------------------------------------------------- H: heal XP end to end at the defaults
    H = {}
    at("3")
    fresh_windows()
    ran0 = int(FakeW.RAN)
    H["classes"] = {"others50": heal(50), "self40": heal(40, True), "others3": heal(3), "self4": heal(4, True), "ran": int(FakeW.RAN) - ran0}
    fresh_windows()
    H["direct"] = {"others50": heal(50, via_classes=False), "self40": heal(40, True, via_classes=False)}
    seq = []
    for i in range(2000):
        if i % 400 == 0:
            fresh_windows()
        seq.append(heal(1, True)[1])
    H["self1"] = {"set": sorted(set(seq)), "mean": sum(seq) / float(len(seq))}
    seq = []
    for i in range(2000):
        if i % 200 == 0:
            fresh_windows()
        seq.append(heal(2.5)[1])
    H["others25"] = {"set": sorted(set(seq)), "mean": sum(seq) / float(len(seq))}
    seq = []
    for i in range(500):
        if i % 400 == 0:
            fresh_windows()
        seq.append(heal(1)[1])
    H["others1"] = sorted(set(seq))
    am = [int(Hx.amount(1.0, 1.25)) for _ in range(40000)]
    H["amount"] = {"set": sorted(set(am)), "mean": sum(am) / float(len(am)), "x8": int(Hx.amount(8.0, 1.25)), "x7": int(Hx.amount(7.0, 1.0))}
    H["paid"] = [int(Bx.paidX(u3, DIVINITY, 10, False, False)), int(Bx.paid(u3, DIVINITY, 10, False))]
    fresh_windows()
    H["archer"] = heal(50, False, u1, via_classes=False)
    D["H"] = H

    # ---------------------------------------------------------------- M: the class skill XP multiplier x1 / x5 / x0
    M = {}
    for m in ("1", "5", "0"):
        txt = at(m)
        fresh_windows()
        k0 = xp_of(u1, ARCHERY)
        for _ in range(10):
            Xp.gain(skyy, ARCHERY, Cfg.classXp(ARCHERY, Cfg.combatXp(None, JFloat(100.0))))
        r = {"text_ok": ("class skill XP x%s" % m) in txt, "others50": heal(50), "self40": heal(40, True),
             "kill100": int(Cfg.classXp(ARCHERY, Cfg.combatXp(None, JFloat(100.0)))), "kills10": xp_of(u1, ARCHERY) - k0,
             "paid": [int(Bx.paidX(u3, DIVINITY, 10, False, False)), int(Bx.paid(u3, DIVINITY, 10, False))],
             "statsLine": str(Dv.statsLine()), "how15": str(Sp.how(DIVINITY))}
        fresh_windows()
        r["cap"] = [heal(300)[1], heal(300)[1], heal(300)[1], heal(5)[1]]
        M[m] = r
    D["M"] = M

    # ---------------------------------------------------------------- X: the cap (final heal XP), the general multiplier, the bridge cap
    X = {}
    at("3")
    fresh_windows()
    X["others"] = [heal(300, via_classes=False), heal(300, via_classes=False), heal(300, via_classes=False), heal(5, via_classes=False)]
    X["window"] = [int(x) for x in hwin.get(u3)]
    fresh_windows()
    X["self"] = [heal(720, True, via_classes=False), heal(1, True, via_classes=False)]
    fresh_windows()
    X["mixed"] = [heal(400, via_classes=False), heal(400, True, via_classes=False), heal(1, via_classes=False)]
    X["cap"] = int(Dv.MAX_MIN)
    at("3", b"multiplier=2.0\n", "mult2")
    fresh_windows()
    X["mult2"] = {"others50": heal(50), "statsLine": str(Dv.statsLine()), "kill100": int(Cfg.classXp(ARCHERY, Cfg.combatXp(None, JFloat(100.0))))}
    fresh_windows()
    X["mult2"]["cap"] = [heal(300)[1], heal(300)[1], heal(300)[1], heal(5)[1]]
    at("3", b"multiplier=0\n", "mult0")
    X["mult0"] = str(Dv.statsLine())
    at("3", b"bridge.maxXpPerMinute=1000\ndivinity.healXpMaxPerMinute=0\n", "bcap")
    fresh_windows()
    X["bcap"] = {"per_min": int(Bc.PER_MIN), "big": heal(1200, via_classes=False), "fits": heal(900, via_classes=False), "statsLine": str(Dv.statsLine())}
    at("3", b"divinity.healXp.enabled=false\n", "off")
    fresh_windows()
    X["off"] = [heal(50, via_classes=False), str(Dv.statsLine())]
    D["X"] = X

    # ---------------------------------------------------------------- K: kills / party / grants at the defaults through real awards
    K = {}
    at("3")
    k0 = xp_of(u1, ARCHERY)
    for _ in range(10):
        Xp.gain(skyy, ARCHERY, Cfg.classXp(ARCHERY, Cfg.combatXp(None, JFloat(100.0))))
    K["kills10"] = xp_of(u1, ARCHERY) - k0
    K["role"] = None
    at("3", ("combat.role.%s=100\n" % ROLE).encode("latin-1"), "role")
    K["role"] = int(Cfg.classXp(ARCHERY, Cfg.combatXp(ROLE, JFloat(50.0))))
    at("3")
    K["share"] = int(Px.amount(Cfg.classXp(ARCHERY, Cfg.combatXp(None, JFloat(100.0))), 0.5))
    at("3", b"bridge.addxp.skills=Mining,Foraging,Farming,Alchemy,Smithing,Cooking,Archery\n", "grant")
    bwin.clear()
    b5 = xp_of(u1, ARCHERY)
    ok = bool(AddFn().apply(JObj[:]([u1, "Archery", JLong(100), "test:grant", None])))
    K["grant"] = [ok, xp_of(u1, ARCHERY) - b5]
    D["K"] = K

    # ---------------------------------------------------------------- L: HealMig on scratch copies
    def snap(d):
        return dict((os.path.relpath(os.path.join(r, fn), d).replace(os.sep, "/"), open(os.path.join(r, fn), "rb").read())
                    for r, ds, fs in os.walk(d) for fn in fs)

    def props(b):
        p = Props()
        p.load(JClass("java.io.ByteArrayInputStream")(b))
        return dict((str(k), str(p.getProperty(k))) for k in p.stringPropertyNames())

    def start(d):
        """the plugin's setup order (CfgPub.start replaced by the kit history init it does)"""
        Cfg.FILE = path(os.path.join(d, "xp.properties"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        mr = [str(x) for x in Mig.run()]
        hr = str(HMig.run())
        lt = str(Cfg.load())
        Rows.HOME = path(d)
        Hist.init()
        CLog.init()
        kc = str(Mig.keepCopy())
        return {"mana": mr, "heal": hr, "keep": kc, "div": [float(Dv.PER_HP), float(Dv.PER_HP_SELF), int(Dv.MAX_MIN)], "stats": str(Dv.statsLine()),
                "text_ok": "class skill XP x3" in lt}

    def diff_lines(a, b):
        la, lb = a.split(b"\n"), b.split(b"\n")
        import difflib
        sm = difflib.SequenceMatcher(None, la, lb, autojunk=False)
        out = []
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op != "equal":
                out.append([op, [x.decode("latin-1") for x in la[i1:i2]], [x.decode("latin-1") for x in lb[j1:j2]]])
        return out

    L = {}
    lc = os.path.join(SCRATCH, "live-copy")
    s0 = snap(lc)
    r1 = start(lc)
    s1 = snap(lc)
    r2 = start(lc)
    s2 = snap(lc)
    x0, x1 = s0["xp.properties"], s1["xp.properties"]
    p0, p1 = props(x0), props(x1)
    newbak = sorted(k for k in s1 if k.startswith("config-history/") and k.endswith(".bak") and k not in s0)
    L["live"] = {"r1": r1, "r2": r2, "changed1": sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k)),
                 "changed2": sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k)),
                 "propdiff": sorted([k, p0.get(k), p1.get(k)] for k in set(p0) | set(p1) if p0.get(k) != p1.get(k)),
                 "diff": diff_lines(x0, x1), "newbak": newbak, "bak_is_old": len(newbak) == 1 and s1[newbak[0]] == x0,
                 "index_tail": s1.get("config-history/index.log", b"").decode("utf-8").strip().split("\n")[-1],
                 "log": s1.get("config-changes.log", b"").decode("utf-8").strip().split("\n"),
                 "lf_only": x0.count(b"\r") == 0 and x1.count(b"\r") == 0,
                 "players_same": all(s0[k] == s2.get(k) for k in s0 if k.startswith("players/") or k.startswith("placed/")),
                 "n": len(s0), "players": len([k for k in s0 if k.startswith("players/")])}
    # (2) an EDITED copy: healXpPerHp=0.3 by hand, CRLF, a non-ASCII byte in a comment; empty history
    ed = os.path.join(SCRATCH, "mig-edit")
    os.makedirs(ed)
    e0 = x0.replace(b"\ndivinity.healXpPerHp=0.2\n", b"\ndivinity.healXpPerHp=0.3\n")
    e0 = (b"# caf\xe9 - an admin's note\n" + e0).replace(b"\n", b"\r\n")
    open(os.path.join(ed, "xp.properties"), "wb").write(e0)
    Cfg.FILE = path(os.path.join(ed, "xp.properties"))
    Rows.HOME, Hist.DIR, CLog.FILE = None, None, None
    er1 = str(HMig.run())
    t0 = snap(ed)
    e1 = t0["xp.properties"]
    er2 = str(HMig.run())
    t1 = snap(ed)
    pe0, pe1 = props(e0), props(e1)
    L["edit"] = {"r1": er1, "r2": er2, "same2": t0 == t1, "crlf": e1.count(b"\r\n") == e1.count(b"\n") and e1.count(b"\r") == e1.count(b"\n"),
                 "e9": e1.startswith(b"# caf\xe9 - an admin's note\r\n"),
                 "propdiff": sorted([k, pe0.get(k), pe1.get(k)] for k in set(pe0) | set(pe1) if pe0.get(k) != pe1.get(k)),
                 "diff": diff_lines(e0, e1), "log": t0.get("config-changes.log", b"").decode("utf-8").strip().split("\n"),
                 "bak": [k for k in t0 if k.endswith(".bak")], "bak_is_old": any(t0[k] == e0 for k in t0 if k.endswith(".bak"))}
    # (3) a file without heal lines (pre-0.4.4): only the marker, at the top; the loader then appends the 0.4.11 blocks
    nd = os.path.join(SCRATCH, "mig-nokeys")
    os.makedirs(nd)
    n0 = b"# a SkyySkills 0.4.3 file\nmultiplier=1.0\n"
    open(os.path.join(nd, "xp.properties"), "wb").write(n0)
    Cfg.FILE = path(os.path.join(nd, "xp.properties"))
    Rows.HOME, Hist.DIR, CLog.FILE = None, None, None
    nr1 = str(HMig.run())
    n1 = open(os.path.join(nd, "xp.properties"), "rb").read()
    Cfg.load()
    n2 = open(os.path.join(nd, "xp.properties"), "rb").read()
    nr2 = str(HMig.run())
    L["nokeys"] = {"r1": nr1, "r2": nr2, "marker_top": n1 == (str(HMig.MG_MARK) + "\n").encode("latin-1") + n0,
                   "after_load": [float(Dv.PER_HP), float(Dv.PER_HP_SELF), int(Dv.MAX_MIN)], "again_same": open(os.path.join(nd, "xp.properties"), "rb").read() == n2,
                   "log": os.path.exists(os.path.join(nd, "config-changes.log"))}
    # (4) config-history cannot be written (a FILE named config-history): WARN, nothing written, the next start retries
    bd = os.path.join(SCRATCH, "mig-nohist")
    os.makedirs(bd)
    open(os.path.join(bd, "xp.properties"), "wb").write(x0)
    open(os.path.join(bd, "config-history"), "wb").write(b"not a folder")
    Cfg.FILE = path(os.path.join(bd, "xp.properties"))
    Rows.HOME, Hist.DIR, CLog.FILE = None, None, None
    br = str(HMig.run())
    L["nohist"] = {"r": br, "untouched": open(os.path.join(bd, "xp.properties"), "rb").read() == x0,
                   "nolog": not os.path.exists(os.path.join(bd, "config-changes.log"))}
    # the pure text step on a CRLF copy of the live file: same changes as the LF run, every line still CRLF
    tc = HMig.mgUpdate(x0.decode("latin-1").replace("\n", "\r\n"))
    L["crlf_text"] = str(tc[0]).encode("latin-1") == x1.replace(b"\n", b"\r\n")
    D["L"] = L
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: bytecode compare
def version_only(a, b):
    la, lb = a.split(chr(10)), b.split(chr(10))
    return len(la) == len(lb) and all(x == y or x.replace(OLD_VERSION, VERSION, 1) == y for x, y in zip(la, lb))


def strings_only(a, b):
    """the same instructions; only string constants (ldc) differ - an inlined static final text (a default block, a help text)"""
    la, lb = a.split(chr(10)), b.split(chr(10))
    const = re.compile(r"(ldc|ldc2_w|[dfil]const_\w+|bipush|sipush) ")
    return len(la) == len(lb) and all(x == y or (const.match(x + " ") and const.match(y + " ")) for x, y in zip(la, lb))


def run_bytecode(old, new, out):
    import skyybuild as B
    from jpype import JClass
    _jvm_start([B.JAVASSIST], verify=False)
    ClassPool, BAIS = JClass("javassist.ClassPool"), JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def listing(pool, data):
        cc = pool.makeClass(BAIS(data))
        ms = {}
        behaviors = list(cc.getDeclaredBehaviors())
        if cc.getClassInitializer() is not None:
            behaviors.append(cc.getClassInitializer())
        for mm in behaviors:
            k = "%s%s" % (mm.getName(), mm.getSignature())
            if mm.getMethodInfo().getCodeAttribute() is None:
                ms[k] = ""
                continue
            it = mm.getMethodInfo().getCodeAttribute().iterator()
            cpool = mm.getMethodInfo().getConstPool()
            lines = []
            while it.hasNext():
                ln = str(IP.instructionString(it, it.next(), cpool)).replace(chr(13), "<CR>").replace(chr(10), "<LF>")   # one instruction = one line
                ln = re.sub(r"#\d+ = ", "", ln).replace("ldc_w ", "ldc ")
                ln = re.sub(r"^(if\w*|goto|goto_w|jsr)\s+\d+", r"\1 N", ln)
                lines.append(ln)
            ms[k] = "\n".join(lines)
        fields = sorted("%s %s" % (f.getName(), f.getSignature()) for f in list(cc.getDeclaredFields()))
        return ms, fields

    zo, zn = zipfile.ZipFile(old), zipfile.ZipFile(new)
    res = {"diff": {}, "flows": {}, "only_old": sorted(set(zo.namelist()) - set(zn.namelist())),
           "only_new": sorted(set(zn.namelist()) - set(zo.namelist())),
           "same": sorted(n for n in set(zo.namelist()) & set(zn.namelist()) if n.endswith(".class") and zo.read(n) == zn.read(n))}
    for n in sorted(set(zo.namelist()) & set(zn.namelist())):
        if not n.endswith(".class") or zo.read(n) == zn.read(n):
            continue
        mo, fo = listing(ClassPool(False), zo.read(n))
        mn, fn = listing(ClassPool(False), zn.read(n))
        changed = sorted(k for k in set(mo) & set(mn) if mo[k] != mn[k])
        res["diff"][n] = {"changed": changed, "gone": sorted(set(mo) - set(mn)), "new": sorted(set(mn) - set(mo)),
                          "fields_gone": sorted(set(fo) - set(fn)), "fields_new": sorted(set(fn) - set(fo)),
                          "vo": [k for k in changed if version_only(mo[k], mn[k])],
                          "so": [k for k in changed if strings_only(mo[k], mn[k])],
                          "dl": dict((k, [[x[:90], y[:90]] for x, y in zip(mo[k].split(chr(10)), mn[k].split(chr(10))) if x != y][:6]
                                     + [len(mo[k].split(chr(10))), len(mn[k].split(chr(10)))]) for k in changed)}
    for cls, meth in (("HealXp", "offer"), ("BridgeXp", "offer"), ("BridgeXp", "offerX"), ("BridgeXp", "paid"), ("BridgeXp", "paidX")):
        ms, _ = listing(ClassPool(False), zn.read("com/skyy/skills/%s.class" % cls))
        for k, v in ms.items():
            if k.startswith(meth + "("):
                res["flows"]["%s.%s %s" % (cls, meth, k[len(meth):])] = v
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ parent
def main():
    if "--mkfake" in sys.argv:
        return run_mkfake(arg("--mkfake"))
    if "--old-run" in sys.argv:
        return run_old(arg("--old-run"), arg("--out"))
    if "--new-run" in sys.argv:
        return run_new(arg("--new-run"), arg("--out"), arg("--fake"), arg("--classes"))
    if "--bytecode" in sys.argv:
        return run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
    for j in (JAR, OLD_JAR, CLASSES_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    if not os.path.isfile(LIVE):
        sys.exit("the live xp.properties is not at %s (pass --live <folder>; it is only ever read and copied)" % LIVE)
    scratch_root = os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower().rstrip("/")
    here = SCRATCH.replace("\\", "/").lower().rstrip("/")
    if here == scratch_root or not here.startswith(scratch_root + "/"):
        sys.exit("--dir must be a folder INSIDE tools/dev/scratch/ (the whole folder is deleted afterwards), not %s" % SCRATCH)
    GUARD_OK[0] = True
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    shutil.copytree(LIVE_DIR, os.path.join(SCRATCH, "live-copy"))
    livenow = open(LIVE, "rb").read()
    check(b"\ndivinity.healXpPerHp=0.2\n" in livenow and b"\ndivinity.healXpPerHpSelf=0.25\n" in livenow
          and b"\ndivinity.healXpMaxPerMinute=300\n" in livenow and b"0.4.11 heal XP update" not in livenow,
          "L: the live xp.properties still has the 0.4.10 heal defaults 0.2 / 0.25 / 300 and no marker")
    me = os.path.abspath(__file__)
    fake = os.path.join(SCRATCH, "fake")
    p = subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(os.path.join(fake, "skyytest", "FakeWorld.class")), "the stand-in classes were generated")
    outs = {"old": os.path.join(SCRATCH, "run-old.json"), "new": os.path.join(SCRATCH, "run-new.json"), "bc": os.path.join(SCRATCH, "bytecode.json")}
    p = subprocess.run([sys.executable, me, "--old-run", OLD_JAR, "--out", outs["old"], "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(outs["old"]), "child JVM for %s ran" % os.path.basename(OLD_JAR))
    p = subprocess.run([sys.executable, me, "--new-run", JAR, "--out", outs["new"], "--dir", SCRATCH, "--fake", fake, "--classes", CLASSES_JAR], env=env)
    check(p.returncode == 0 and os.path.isfile(outs["new"]), "child JVM for %s ran" % os.path.basename(JAR))
    p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", outs["bc"], "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(outs["bc"]), "bytecode child ran")
    if FAILS:
        return finish()
    new, old, bc = json.load(open(outs["new"])), json.load(open(outs["old"])), json.load(open(outs["bc"]))
    # ---------------------------------------------------------------- A
    for r in (new, old):
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A: %s: %d / %d classes load under -Xverify:all %s"
              % (os.path.basename(r["jar"]), r["loaded"], r["classes"], r["load_fails"][:3]))
    print("A. -Xverify:all: %s %d / %d, %s %d / %d classes" % (os.path.basename(new["jar"]), new["loaded"], new["classes"],
                                                             os.path.basename(old["jar"]), old["loaded"], old["classes"]))
    if FAILS:
        return finish()
    D, O = new["data"], old["data"]
    # ---------------------------------------------------------------- C
    C = D["C"]
    check(C["div"] == [1.0, 1.25, 900] and D["div"] == [1.0, 1.25, 900] and O["div"] == [0.2, 0.25, 300] and C["again_same"],
          "C: a fresh file loads 1 / 1.25 / 900 (0.4.10: 0.2 / 0.25 / 300); a second load writes nothing")
    nd, od = D["defaults"], O["defaults"]
    check(nd.count("\ndivinity.healXpPerHp=1\n") == 1 and nd.count("\ndivinity.healXpPerHpSelf=1.25\n") == 1
          and nd.count("\ndivinity.healXpMaxPerMinute=900\n") == 1 and nd.count(D["marker"]) == 1
          and "\n\n" + D["marker"] + "\n# ---------- Divinity (SkyySkills 0.4.4)" in nd, "C: the default file: 1 / 1.25 / 900 and the marker once, above the Divinity block")
    want = od.replace("# SkyySkills %s - XP rules" % OLD_VERSION, "# SkyySkills %s - XP rules" % VERSION, 1)
    want = want.replace("\ndivinity.healXpPerHp=0.2\n", "\ndivinity.healXpPerHp=1\n").replace("\ndivinity.healXpPerHpSelf=0.25\n", "\ndivinity.healXpPerHpSelf=1.25\n")
    want = want.replace("\ndivinity.healXpMaxPerMinute=300\n", "\ndivinity.healXpMaxPerMinute=900\n")
    want = want.replace("\n# ---------- Divinity (SkyySkills 0.4.4)", "\n" + D["marker"] + "\n# ---------- Divinity (SkyySkills 0.4.4)", 1)
    for a, b in D["docpairs"]:
        check(want.count("\n" + a + "\n") == 1, "C: the 0.4.10 default file has the old comment line once: %s" % a)
        want = want.replace("\n" + a + "\n", "\n" + b + "\n")
    check(nd == want, "C: the 0.4.11 default file = the 0.4.10 one + version line, marker, 3 heal values and %d rewritten comment lines" % len(D["docpairs"]))
    check(C["nokeys"] == [1.0, 1.25, 900, 0], "C: no heal lines in the file -> the code defaults 1 / 1.25 / 900: %s" % C["nokeys"])
    check(C["old"] == [1.0, 1.25, 900, 1, 1, 1, False], "C: an old file gets the Divinity blocks appended with 1 / 1.25 / 900 (no marker in them): %s" % C["old"])
    dd = D["divDefaults"]
    check("divinity.healXpPerHp=1\n" in dd[0] and "divinity.healXpMaxPerMinute=900\n" in dd[0] and "divinity.healXpPerHpSelf=1.25\n" in dd[1]
          and "Priest heal XP is NOT multiplied" in dd[2] and "Priest heal XP (on others" not in dd[2], "C: the appended blocks (DivCfg / class skill XP) carry the new numbers and texts")
    print("C. defaults 1 / 1.25 / 900 (file = code = rows), marker above the Divinity block, %d comment lines rewritten" % len(D["docpairs"]))
    # ---------------------------------------------------------------- H
    H = D["H"]
    check(D["classes_err"] is None, "H: SkyyClasses %s HealTask loaded: %s" % (os.path.basename(CLASSES_JAR), D["classes_err"]))
    hc = H["classes"]
    check(hc["others50"][1] == 50 and hc["self40"][1] == 50 and hc["others3"][1] == 3 and hc["self4"][1] == 5 and hc["ran"] == 4,
          "H: through SkyyClasses' own skill:fn:healxp calls at the defaults (class skill XP x3): 50 HP others +50, 40 HP self +50, 3 HP +3, 4 HP self +5: %s" % hc)
    check(H["direct"] == {"others50": [True, 50], "self40": [True, 50]}, "H: SkillHealFn accepts the same calls (TRUE) and pays the same: %s" % H["direct"])
    check(H["self1"]["set"] == [1, 2] and abs(H["self1"]["mean"] - 1.25) < 0.05, "H: 1 HP on yourself = 1 or 2 XP, mean %.3f (1.25)" % H["self1"]["mean"])
    check(H["others25"]["set"] == [2, 3] and abs(H["others25"]["mean"] - 2.5) < 0.05, "H: 2.5 HP on others = 2 or 3 XP, mean %.3f (2.5)" % H["others25"]["mean"])
    check(H["others1"] == [1], "H: 1 HP on others = exactly 1 XP every time: %s" % H["others1"])
    check(H["amount"]["set"] == [1, 2] and abs(H["amount"]["mean"] - 1.25) < 0.01 and H["amount"]["x8"] == 10 and H["amount"]["x7"] == 7,
          "H: HealXp.amount(1 HP, 1.25) mean %.4f over 40,000; 8 HP x 1.25 = 10; 7 x 1 = 7" % H["amount"]["mean"])
    check(H["paid"] == [10, 30], "H: BridgeXp.paidX(10, cls false) = 10 (heal), paid(10) = 30 (a class skill grant keeps x3): %s" % H["paid"])
    check(H["archer"] == [False, 0], "H: a non-Priest's heal is refused, nothing paid: %s" % H["archer"])
    print("H. heal XP end to end (SkyyClasses HealTask -> skill:fn:healxp): 50 HP others +%d, 40 HP self +%d; 1 HP self mean %.3f, 2.5 HP others mean %.3f"
          % (hc["others50"][1], hc["self40"][1], H["self1"]["mean"], H["others25"]["mean"]))
    # ---------------------------------------------------------------- M
    M = D["M"]
    for m, f in (("1", 1), ("5", 5), ("0", 0)):
        r = M[m]
        check(r["others50"][1] == 50 and r["self40"][1] == 50 and r["cap"] == [300, 300, 300, 0] and r["statsLine"] == STATS and r["paid"] == [10, 10 * f],
              "M x%s: heal XP unchanged (50 / 50, cap 900, Stats line), grants x%d: %s" % (m, f, r))
        check(r["kill100"] == 20 * f and r["kills10"] == 200 * f and r["text_ok"], "M x%s: a 100 HP kill pays %d, 10 real kills +%d" % (m, 20 * f, 200 * f))
        check(r["how15"] == O["how"][str(DIVINITY)].replace(". Class skill XP x3 on this server", "") + ({"1": "", "5": ". Class skill XP x5 on this server",
              "0": ". Class skill XP is off on this server"}[m]), "M x%s: the Divinity how-to line names the kill multiplier: %s" % (m, r["how15"]))
    print("M. class skill XP x1 / x5 / x0: heal 50 HP others = %d / %d / %d, cap 900 each; kill 100 HP = %d / %d / %d"
          % (M["1"]["others50"][1], M["5"]["others50"][1], M["0"]["others50"][1], M["1"]["kill100"], M["5"]["kill100"], M["0"]["kill100"]))
    # ---------------------------------------------------------------- X
    X = D["X"]
    check(X["cap"] == 900 and X["others"] == [[True, 300], [True, 300], [True, 300], [False, 0]] and X["window"][1] == 900,
          "X: the cap counts FINAL heal XP: 3 x 300 HP others = 900, the next heal refused: %s" % X["others"])
    check(X["self"] == [[True, 900], [False, 0]] and X["mixed"] == [[True, 400], [True, 500], [False, 0]],
          "X: 720 HP on yourself = 900 = the cap; others + self share one cap: %s %s" % (X["self"], X["mixed"]))
    m2 = X["mult2"]
    check(m2["others50"][1] == 100 and m2["cap"] == [600, 600, 600, 0] and m2["kill100"] == 120
          and m2["statsLine"] == "Healing pays 2 Divinity XP per HP on others, 2.5 on yourself (XP multiplier x2, max 1800 a minute)",
          "X: the general XP multiplier 2 comes after the cap (50 HP = 100, a capped minute 1,800, shown on the Stats line): %s" % m2)
    check(X["mult0"] == "Healing pays no Divinity XP on this server (XP multiplier x0)", "X: XP multiplier 0: %s" % X["mult0"])
    b = X["bcap"]
    check(b["per_min"] == 1000 and b["big"] == [False, 0] and b["fits"] == [True, 900]
          and b["statsLine"] == "Healing pays 1 Divinity XP per HP on others, 1.25 on yourself", "X: bridge.maxXpPerMinute 1,000 still counts the paid XP; cap 0 = no max shown: %s" % b)
    check(X["off"] == [[False, 0], "Divinity XP from healing is off on this server"], "X: the part switch off: %s" % X["off"])
    print("X. cap 900 FINAL heal XP a minute (others, self, both); XP multiplier 2 -> 100 per 50 HP, 1,800 a minute")
    # ---------------------------------------------------------------- K
    K = D["K"]
    check(D["kill"] == O["kill"] and D["base"] == O["base"] and D["other"] == O["other"], "K: kill XP at the defaults = the 0.4.10 jar's for every health: %s" % D["kill"])
    check(D["paid"][:7] == O["paid"][:7] and D["scaled"] == O["scaled"] and D["resolve"] == O["resolve"],
          "K: grants / crafting / gathering paid = 0.4.10's (Mining, Alchemy, Smithing, Cooking, Exploration, Acrobatics, an Archery grant): %s" % D["paid"])
    check(D["paid"][7] == O["paid"][7] == 30, "K: BridgeXp.paid (the cls-true path) into Divinity is still x3 like 0.4.10: %s %s" % (D["paid"][7], O["paid"][7]))
    check(K["kills10"] == 600 and K["role"] == 300 and K["share"] == 30 and K["grant"] == [True, 300],
          "K: 10 real kills of a 100 HP mob +600, combat.role 100 -> 300, party share 30, an Archery grant 100 -> 300: %s" % K)
    print("K. kill XP unchanged (x3): %s" % D["kill"])
    # ---------------------------------------------------------------- S
    check(D["statsLine"] == STATS, "S: the Stats line at the defaults: %s" % D["statsLine"])
    check(O["statsLine"] == "Healing pays 0.6 Divinity XP per HP on others, 0.75 on yourself (class skill XP x3, max 900 a minute)", "S: (0.4.10 said: %s)" % O["statsLine"])
    check(D["divText"] == "on (1 XP per HP healed on others, 1.25 on yourself, up to 900 a minute)", "S: the ready-line text: %s" % D["divText"])
    check(D["how"] == O["how"], "S: StatsPage.how() of every skill = 0.4.10's")
    print("S. Stats: %r (0.4.10: %r)" % (D["statsLine"], O["statsLine"]))
    # ---------------------------------------------------------------- R
    ro, rn = O["rows"]["rows"], D["rows"]["rows"]
    check([r[0] for r in rn] == [r[0] for r in ro] and len(rn) == 174, "R: the same 174 keys in the same order")
    od_ = dict((r[0], r) for r in ro)
    diff = sorted(r[0] for r in rn if r != od_[r[0]])
    check(diff == ["classSkill.xpMultiplier"] + HEAL_KEYS[:1] + [HEAL_KEYS[2], HEAL_KEYS[1]] or diff == sorted(["classSkill.xpMultiplier"] + HEAL_KEYS),
          "R: only classSkill.xpMultiplier and the 3 heal rows changed: %s" % diff)
    nr = dict((r[0], r) for r in rn)
    check([nr[k][4] for k in HEAL_KEYS] == ["1", "1.25", "900"], "R: heal row defaults 1 / 1.25 / 900: %s" % [nr[k][4] for k in HEAL_KEYS])
    check(all("Not multiplied by class skill XP" in nr[k][10] for k in HEAL_KEYS) and "Not Priest heals" in nr["classSkill.xpMultiplier"][10],
          "R: the help says healing is not multiplied")
    for k in diff:
        ch = [i for i in range(11) if nr[k][i] != od_[k][i]]
        check(set(ch) <= {1, 4, 10} and (1 not in ch or k == "divinity.healXpPerHp"), "R: %s: only label (healXpPerHp) / default / help changed: %s" % (k, ch))
    for k in ["classSkill.xpMultiplier"] + HEAL_KEYS:
        print("R. %-28s %-36s default %-5s help %r" % (k, nr[k][1], nr[k][4], nr[k][10]))
    # ---------------------------------------------------------------- L
    L = D["L"]
    lv = L["live"]
    check("divinity.healXpPerHp 0.2 -> 1, divinity.healXpPerHpSelf 0.25 -> 1.25, divinity.healXpMaxPerMinute 300 -> 900" in lv["r1"]["heal"]
          and lv["r1"]["div"] == [1.0, 1.25, 900] and lv["r1"]["stats"] == STATS and lv["r1"]["text_ok"], "L live: start 1 updates the 3 untouched lines: %s" % lv["r1"])
    check(lv["r2"]["heal"] == "" and lv["r2"]["div"] == [1.0, 1.25, 900] and lv["changed2"] == [], "L live: start 2 writes nothing: %s %s" % (lv["r2"]["heal"], lv["changed2"]))
    check(lv["propdiff"] == [[HEAL_KEYS[0], "0.2", "1"], [HEAL_KEYS[2], "300", "900"], [HEAL_KEYS[1], "0.25", "1.25"]] or
          sorted(lv["propdiff"]) == sorted([[HEAL_KEYS[0], "0.2", "1"], [HEAL_KEYS[1], "0.25", "1.25"], [HEAL_KEYS[2], "300", "900"]]),
          "L live: the Properties differ in exactly the 3 heal keys: %s" % lv["propdiff"])
    ins = [d for d in lv["diff"] if d[0] == "insert"]
    reps = [d for d in lv["diff"] if d[0] == "replace"]
    oldl = [x for d in reps for x in d[1]]
    newl = [x for d in reps for x in d[2]]
    wantold = set("%s=%s" % (k, v) for k, v in zip(HEAL_KEYS, ("0.2", "0.25", "300"))) | set(a for a, b in D["docpairs"])
    check(len(ins) == 1 and ins[0][2] == [D["marker"]] and all(d[0] in ("insert", "replace") for d in lv["diff"]) and len(oldl) == len(newl)
          and set(oldl) <= wantold and all(x in [b for a, b in D["docpairs"]] + ["%s=%s" % (k, v) for k, v in zip(HEAL_KEYS, ("1", "1.25", "900"))] for x in newl),
          "L live: only the marker is inserted, only heal value lines and old default comment lines are replaced (1:1): %s" % lv["diff"])
    x1 = [d for d in lv["diff"] if d[0] == "insert"]
    check(lv["bak_is_old"] and "SkyySkills 0.4.11" in lv["index_tail"] and "before the 0.4.11 heal XP update" in lv["index_tail"],
          "L live: History holds the old file (%s): %s" % (lv["newbak"], lv["index_tail"]))
    lg = [ln.split("\t") for ln in lv["log"]]
    check(len(lg) == 3 and all(ln[1:4] == ["SkyySkills 0.4.11", "-", "update"] and ln[7] == "ok" for ln in lg)
          and sorted(ln[4:7] for ln in lg) == sorted([[HEAL_KEYS[0], "0.2", "1"], [HEAL_KEYS[1], "0.25", "1.25"], [HEAL_KEYS[2], "300", "900"]]),
          "L live: one config-changes.log line per key (Server Setup -> Changes -> Undo): %s" % lv["log"])
    check(set(lv["changed1"]) == {"xp.properties", "config-history/index.log", "config-changes.log"} | set(lv["newbak"]) and lv["players_same"] and lv["lf_only"],
          "L live: start 1 touches only xp.properties, its History copy + index and config-changes.log; players / placed untouched: %s" % lv["changed1"])
    ed = L["edit"]
    check(HEAL_KEYS[0] + "=0.3 kept (an admin's value)" in ed["r1"] and "divinity.healXpPerHpSelf 0.25 -> 1.25, divinity.healXpMaxPerMinute 300 -> 900" in ed["r1"]
          and "divinity.healXpPerHp 0.2" not in ed["r1"], "L edit: 0.3 kept and logged, the untouched two updated: %s" % ed["r1"])
    check(sorted(ed["propdiff"]) == sorted([[HEAL_KEYS[1], "0.25", "1.25"], [HEAL_KEYS[2], "300", "900"]]) and ed["crlf"] and ed["e9"] and ed["bak_is_old"],
          "L edit: only the 2 keys changed, every line still CRLF, the 0xE9 byte kept, History = the old bytes: %s" % ed["propdiff"])
    check(len(ed["log"]) == 2 and ed["r2"] == "" and ed["same2"], "L edit: 2 change-log lines; a second run writes nothing: %s" % ed["log"])
    nk = L["nokeys"]
    check(nk["marker_top"] and "no divinity heal XP line still had its 0.4.10 default" in nk["r1"] and nk["after_load"] == [1.0, 1.25, 900]
          and nk["r2"] == "" and not nk["log"], "L no heal lines: only the marker at the top, the loader appends 1 / 1.25 / 900, then nothing: %s" % nk)
    check(L["nohist"]["r"] == "" and L["nohist"]["untouched"] and L["nohist"]["nolog"], "L history unwritable: WARN, file untouched, no log: %s" % L["nohist"])
    check(L["crlf_text"], "L: the text step on a CRLF copy of the live file = the LF result with CRLF")
    print("L. live copy (%d files, %d players): start 1 -> %d lines replaced + marker, History + 3 Undo lines; start 2 nothing; edited 0.3 kept; CRLF kept"
          % (lv["n"], lv["players"], len(oldl)))
    # ---------------------------------------------------------------- F
    diff = bc["diff"]
    beyond = dict((n.split("/")[-1][:-6], d) for n, d in diff.items() if set(d["changed"]) != set(d["vo"]) or d["new"] or d["gone"]
                  or d["fields_new"] or d["fields_gone"])
    vonly = sorted(n.split("/")[-1][:-6] for n in diff if n.split("/")[-1][:-6] not in beyond)
    check(set(beyond) == {"BridgeXp", "HealXp", "DivCfg", "SkillCfg", "CfgRows", "SkyySkillsPlugin"},
          "F: classes changed beyond the version string: %s" % sorted(beyond))
    check(bc["only_new"] == ["com/skyy/skills/HealMig.class"] and bc["only_old"] == [], "F: + HealMig only: %s %s" % (bc["only_new"], bc["only_old"]))

    def real(c):
        d = beyond.get(c, {})
        return sorted(k for k in d.get("changed", []) if k not in d.get("vo", []))
    bx = beyond.get("BridgeXp", {})
    check(sorted(bx.get("new", [])) == ["offerX(Ljava/util/UUID;IJLjava/lang/String;Ljava/lang/String;Lcom/hypixel/hytale/server/core/asset/type/item/config/CraftingRecipe;IZZ)J",
                                        "paidX(Ljava/util/UUID;IJZZ)J"] and not bx.get("gone") and not bx.get("fields_new"),
          "F: BridgeXp: + paidX / offerX: %s" % bx.get("new"))
    check(real("HealXp") == ["offer(Ljava/util/UUID;DLjava/lang/String;Ljava/lang/String;Z)Z"] and not beyond.get("HealXp", {}).get("new"), "F: HealXp: only offer: %s" % real("HealXp"))
    so = lambda c: set(beyond.get(c, {}).get("so", []))
    check(real("DivCfg") == ["<clinit>()V", "ensureDefaults(Ljava/util/Properties;)V", "ensureSelf(Ljava/util/Properties;)V", "read(Ljava/util/Properties;)V",
                             "statsLine()Ljava/lang/String;"] and {"ensureDefaults(Ljava/util/Properties;)V", "ensureSelf(Ljava/util/Properties;)V", "read(Ljava/util/Properties;)V"} <= so("DivCfg")
          and not beyond.get("DivCfg", {}).get("new") and not beyond.get("DivCfg", {}).get("fields_new"),
          "F: DivCfg: field defaults (<clinit>), statsLine; read / ensureDefaults / ensureSelf only their constants (the default numbers + the inlined block): %s" % real("DivCfg"))
    check(real("SkillCfg") == ["ensureClass(Ljava/util/Properties;)V", "load()Ljava/lang/String;"] and set(real("SkillCfg")) <= so("SkillCfg")
          and not beyond.get("SkillCfg", {}).get("new"), "F: SkillCfg: only the inlined default texts (load = the default file, ensureClass = the class skill XP block): %s" % real("SkillCfg"))
    check(real("CfgRows") == ["<clinit>()V"] and not beyond.get("CfgRows", {}).get("new"), "F: CfgRows: only its static row arrays (<clinit>): %s" % real("CfgRows"))
    check(real("SkyySkillsPlugin") == ["setup()V"], "F: the plugin: only setup (HealMig.run): %s" % real("SkyySkillsPlugin"))
    for cls in ("KillSys", "SkillXp", "PartyXp", "BridgeTask", "SkillHealFn", "SkillAddFn", "SkillCraftFn", "SkillXpFn", "BreakSys", "HarvestSys",
                "ManaMig", "ManaGuard", "ManaCost", "Overall", "OverallCfg", "SkillsPage", "StatsPage", "OverallPage", "SkillStore", "SkillClass", "CfgHist", "CfgLog",
                "CfgFile"):
        check("com/skyy/skills/%s.class" % cls in bc["same"] or cls in vonly, "F: %s byte-identical (or the version string only)" % cls)
    fl = bc["flows"]
    ho = [v for k, v in fl.items() if k.startswith("HealXp.offer ")][0]
    check("BridgeXp.offerX(" in ho and "BridgeXp.offer(" not in ho, "F: HealXp.offer calls BridgeXp.offerX, not offer")
    hl = ho.split("\n")
    i = [n for n, ln in enumerate(hl) if "BridgeXp.offerX(" in ln][0]
    check(hl[i - 1].strip() == "iconst_0" and hl[i - 2].strip() == "iconst_0", "F: HealXp.offer passes grant false, cls false: %s" % hl[i - 3:i + 1])
    po = [v for k, v in fl.items() if k.startswith("BridgeXp.paid (")][0].split("\n")
    oo = [v for k, v in fl.items() if k.startswith("BridgeXp.offer (")][0].split("\n")
    check(any("BridgeXp.paidX(" in ln for ln in po) and po[[n for n, ln in enumerate(po) if "paidX(" in ln][0] - 1].strip() == "iconst_1"
          and len(po) <= 9, "F: BridgeXp.paid = paidX(..., true): %s" % po)
    check(any("BridgeXp.offerX(" in ln for ln in oo) and oo[[n for n, ln in enumerate(oo) if "offerX(" in ln][0] - 1].strip() == "iconst_1"
          and len(oo) <= 14, "F: BridgeXp.offer = offerX(..., true): %s" % oo)
    px = [v for k, v in fl.items() if k.startswith("BridgeXp.paidX (")][0]
    check(px.index("SkillCfg.scaled") < px.index("SkillCfg.classXp") < px.index("SkillBonus.boost"), "F: paidX: xp multiplier -> (cls) class skill XP -> tree bonus")
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    mo, mn = json.loads(zo.read("manifest.json")), json.loads(zn.read("manifest.json"))
    kd = sorted(k for k in set(mo) | set(mn) if mo.get(k) != mn.get(k))
    check(kd in (["Description", "Name", "Version"], ["Description", "Version"]), "F: manifest: only %s differ" % kd)
    check("1 per HP on others, 1.25 on yourself, up to 900 a minute" in mn.get("Description", ""), "F: the manifest names the heal XP")
    nonclass = sorted(n for n in set(zo.namelist()) | set(zn.namelist()) if not n.endswith(".class") and n != "manifest.json"
                      and (n not in zo.namelist() or n not in zn.namelist() or zo.read(n) != zn.read(n)))
    check(nonclass == [], "F: every non-class entry byte-identical: %s" % nonclass[:5])
    print("F. class bytes: + HealMig; changed beyond the version %s; version only %d classes" % (", ".join(sorted(beyond)), len(vonly)))
    return finish()


def finish():
    if not KEEP and GUARD_OK[0]:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("SkyySkills %s harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
