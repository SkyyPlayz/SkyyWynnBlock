"""SkyySkills 0.4.10 - bare-JVM harness for the class skill XP multiplier round (tools/skills_0_4_10_patch.py): ONE new Server Setup row
classSkill.xpMultiplier (default 3) multiplies every XP gain into a class skill through SkillCfg.classXp - kills (KillSys, after combat.max),
the party share (a fraction of that same kill XP), Priest heal XP on others and on yourself and class skill grants (BridgeXp.paid inside
BridgeXp.offer, after divinity.healXpMaxPerMinute, before bridge.maxXpPerMinute); gathering and the other skills unchanged.

    python SkyySkills/test_skyyskills_0.4.10.py [--jar <SkyySkills-0.4.10.jar>] [--old <SkyySkills-0.4.9.jar>] [--guilds <SkyyGuilds jar>]
                                                [--dir <scratch>] [--live <Skyy_SkyySkills folder>] [--keep]

Build first (python tools/skills_0_4_10_patch.py, then python SkyySkills/build_skyyskills_0.4.10.py). The old jar = the SET pin 0.4.9, the
Guilds jar = the SET pin of SkyyGuilds (0.1.4). Child processes start fresh JVMs (the game's own JRE, -Xverify:all, -XX:-UsePerfData,
HytaleServer.jar + the mod jar(s); TEMP / TMP / java.io.tmpdir in the scratch folder). The live world is READ ONLY: its Skyy_SkyySkills
folder is copied into the scratch folder and only that copy is ever written.
  A  every class of the 0.4.10 jar AND of the 0.4.9 jar loads and initializes under -Xverify:all
  C  the row through the real loader (SkillCfg.load on scratch files): fresh file (default block, x3), the clamps (0..100; NaN, -1 -> 0;
     250 -> 100; unparsable -> 3), a file without the key gets the block appended ONCE (a second load writes nothing), the load text
     ("class skill XP x3" = the ready line's xp rules and the /skills reload reply); the 0.4.10 default file = the 0.4.9 one + the block
  K  XP per kill: SkillCfg.combatXp (unchanged, = the 0.4.9 jar's numbers for every health) then SkillCfg.classXp, for 10 mob healths + a
     combat.role override, at x1 / x3 / x0 (and x2.5: the fraction by chance, mean 2.5; x1.1 on 10 = 11 exactly), with the xp multiplier at
     2 too; every class slot multiplied, every other slot unchanged; REAL awards through SkillXp.gain (a stand-in packet handler takes the
     chat lines): 10 kills of a 100 HP mob = +200 / +600 / +0 Archery
  P  the party share: PartyXp.amount(kill XP, 0.5) of the multiplied kill XP (10 at x1, 30 at x3 for a 100 HP mob; odd XP by chance),
     written through gain4 into the member's own class skill exactly as given (no second multiply)
  H  Priest heal XP END TO END through the bridge functions SkyyClasses calls (skill:fn:healxp on others and with the trailing TRUE =
     self) -> HealXp.offer -> BridgeXp.offer -> BridgeXp.paid -> BridgeTask (a stand-in Universe + World that runs the task at once) ->
     gain3: 50 HP on others = 10 / 30 / 0 Divinity XP, 40 HP on yourself = 10 / 30 / 0; a class skill grant (skill:fn:addxp with
     Archery listed in bridge.addxp.skills) 100 -> 300; a non-Priest gets nothing
  X  the caps: combat.max / combat.min / combat.role sit BEFORE the multiplier (2,500 HP: 500 -> 1,500; 2 HP: 1 -> 3; role 100 -> 300;
     combat.max 50 -> 150); divinity.healXpMaxPerMinute counts the BASE heal XP (1,500 HP on others in a minute = 300 base = the cap,
     paid 900 at x3; the next heal is refused); bridge.maxXpPerMinute counts the PAID XP (cap 1,000: a 400 base heal = 1,200 paid is
     refused at x3 and paid at x1)
  G  gathering unchanged: Mining / Foraging / Farming rules, the xp multiplier (scaled), BridgeXp.paid for Mining / Alchemy / Smithing /
     Cooking / Exploration grants and a real Mining award are the same at x1 and x3
  U  SkyyGuilds (the live SET jar) counting the members' skill XP through SkySkills' real skill:fn:xp: XpTask.check credits 10 % of the
     XP actually gained (x1: 200 Archery -> 20 guild XP; x3: 600 -> 60; Mining 80 -> 8 both), never more than xpMaxPerCheck
  S  texts: StatsPage.how of a class skill (". Class skill XP x3 on this server"; x1 = the 0.4.9 text; x0 "is off"), the Divinity heal
     line (x1 = the 0.4.9 text, x3 the effective rates 0.6 / 0.75 / max 900), how() of the other skills unchanged
  R  the Server Setup rows: 0.4.10 = 0.4.9 + classSkill.xpMultiplier (first Combat row, dec 0-100, default 3.0, unit x, live, reload)
     + the help texts of multiplier, combat.max and divinity.healXpMaxPerMinute; nothing else
  L  START TWICE ON A SCRATCH COPY OF THE LIVE DATA (setup order ManaMig.run -> SkillCfg.load -> kit history -> ManaMig.keepCopy): the
     first start appends exactly the class skill XP block to xp.properties (nothing else in it changes, the Properties gain only
     classSkill.xpMultiplier=3.0), the second start writes nothing; config-history / players / placed stay byte-identical; x3 both times
  F  class bytes 0.4.9 vs 0.4.10: only SkillCfg (field + 4 methods + load + the default text), KillSys (onComponentAdded), BridgeXp (paid
     new, offer), StatsPage (how), DivCfg (statsLine) and the kit's CfgRows (rows / help) + CfgFile (its default-file lines) change beyond the version;
     KillSys passes the ONE multiplied local to SkillXp.gain and PartyXp.share; BridgeXp.offer gives paid()'s result to allow(); SkillXp,
     HealXp, PartyXp and everything else byte-identical (or version only); manifest: Version / Name / Description only
  T  the pacing table: kills to reach class skill 10 / 15 / 25 / 40 at x1 and x3 (research/Mob-Levels-Plan.md section 7 kill XP per zone)
Nothing is deployed. Default scratch folder: tools/dev/scratch/skills0410/harness (deleted at the end unless --keep; --dir must be a folder
INSIDE tools/dev/scratch/). Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.4.10", "0.4.9"
PKG = "com.skyy.skills."
GPKG = "com.skyy.guilds."
SCRIPT = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
HEALTHS = [-1.0, 2.0, 5.0, 7.0, 20.0, 37.0, 100.0, 250.0, 1000.0, 2500.0, 10000.0]
ROLE = "Skyy_Test_Boss"
CLASS_SLOTS = [5, 6, 7, 8, 9, 14, 15]
OTHER_SLOTS = [0, 1, 2, 3, 4, 10, 11, 12, 13]
ARCHERY, DIVINITY, MINING, ALCHEMY, SMITHING, COOKING, EXPLORATION, FURY = 5, 15, 0, 10, 11, 12, 13, 14


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


def _guilds_pin():
    t = open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8").read()
    m = re.search(r'\("SkyyGuilds", "([0-9.]+)"\)', t[t.index("SET = ["):])
    return m.group(1) if m else "0.1.4"


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skills0410", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyySkills-%s.jar" % OLD_VERSION)))
GUILDS_JAR = os.path.abspath(arg("--guilds", os.path.join(ROOT, "SkyyGuilds", "SkyyGuilds-%s.jar" % _guilds_pin())))
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
    """skyytest.FakeHandler extends PacketHandler (writeNoCache counts the packets: PlayerRef.sendMessage works on an Unsafe-allocated
    PlayerRef) and skyytest.FakeWorld extends World (execute runs the task at once on the calling thread = 'the world thread'). Neither
    gets a constructor: both are allocated with Unsafe, like the PlayerRef / Universe stand-ins."""
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


# ============================================================================================ child: the 0.4.9 jar (baseline numbers)
def run_old(jar, out):
    import jpype
    from jpype import JClass, JFloat
    _jvm_start([jar])
    res = load_all(jar)
    if res["load_fails"]:
        json.dump(res, open(out, "w"), indent=1)
        return
    D = res["data"]
    Paths, JStr, Arr = JClass("java.nio.file.Paths"), JClass("java.lang.String"), JClass("java.lang.reflect.Array")
    Cfg, Dv, Sp, Rows = JClass(PKG + "SkillCfg"), JClass(PKG + "DivCfg"), JClass(PKG + "StatsPage"), JClass(PKG + "CfgRows")
    work = os.path.join(SCRATCH, "old")
    os.makedirs(work, exist_ok=True)
    f = os.path.join(work, "xp.properties")
    Cfg.FILE = Paths.get(f, Arr.newInstance(JStr.class_, 0))
    D["load"] = str(Cfg.load())
    D["defaults"] = open(f, "rb").read().decode("latin-1")
    D["kill"] = [int(Cfg.combatXp(None, JFloat(h))) for h in HEALTHS]
    D["statsLine"] = str(Dv.statsLine())
    D["how"] = dict((str(s), str(Sp.how(s))) for s in CLASS_SLOTS + OTHER_SLOTS)
    D["resolve"] = dict((i, [int(x) for x in Cfg.resolve(i)]) for i in ("Ore_Iron", "Rock_Stone", "Plant_Crop_Wheat_Block", "Wood_Oak_Trunk"))
    D["rows"] = rows_of(Rows)
    json.dump(res, open(out, "w"), indent=1)


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
    binds = {}
    for c in ("BK", "BF", "BFK", "BCLS", "BNAME", "BCHECK", "BAFTER", "BCONF"):
        try:
            binds[c] = [str(x) for x in getattr(Rows, c)]
        except Exception:
            pass
    return {"rows": [list(r) for r in zip(*arrs)], "binds": binds, "cats": [str(x) for x in Rows.CAT_IDS]}


# ============================================================================================ child: the 0.4.10 jar (+ SkyyGuilds)
def run_new(jar, out, fake, guilds):
    import jpype
    from jpype import JClass, JFloat, JImplements, JOverride
    _jvm_start([jar, fake, guilds])
    res = load_all(jar)
    if res["load_fails"]:
        json.dump(res, open(out, "w"), indent=1)
        return
    D = res["data"]
    Paths, JStr, Arr = JClass("java.nio.file.Paths"), JClass("java.lang.String"), JClass("java.lang.reflect.Array")
    Props, UUID, System = JClass("java.util.Properties"), JClass("java.util.UUID"), JClass("java.lang.System")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    Cfg, Defs, Xp, Store = JClass(PKG + "SkillCfg"), JClass(PKG + "SkillDefs"), JClass(PKG + "SkillXp"), JClass(PKG + "SkillStore")
    Bx, Bc, Hx, Px = JClass(PKG + "BridgeXp"), JClass(PKG + "BridgeCfg"), JClass(PKG + "HealXp"), JClass(PKG + "PartyXp")
    Dv, Sp, Rows, Mig, Hist = JClass(PKG + "DivCfg"), JClass(PKG + "StatsPage"), JClass(PKG + "CfgRows"), JClass(PKG + "ManaMig"), JClass(PKG + "CfgHist")
    XpFn, AddFn, HealFn = JClass(PKG + "SkillXpFn"), JClass(PKG + "SkillAddFn"), JClass(PKG + "SkillHealFn")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Universe, Holder = JClass("com.hypixel.hytale.server.core.universe.Universe"), JClass("com.hypixel.hytale.component.Holder")
    FakeH, FakeW = JClass("skyytest.FakeHandler"), JClass("skyytest.FakeWorld")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def path(p):
        return Paths.get(p, Arr.newInstance(JStr.class_, 0))

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    def getf(obj, cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f.get(obj)

    def props(d):
        p = Props()
        for k, v in d.items():
            p.setProperty(k, v)
        return p

    bridge = Store.bridge()
    work = os.path.join(SCRATCH, "new")
    os.makedirs(work, exist_ok=True)
    Store.DIR = path(os.path.join(work, "players"))
    # the stand-in Universe (Unsafe-allocated, the SkyyGuilds harness pattern) with one FakeWorld: getPlayer / getWorld / execute work
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

    def mkpr(n, name, online=True):
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", UUID(0x5117, n))
        setf(pr, PRef, "username", name)
        setf(pr, PRef, "packetHandler", handler)
        setf(pr, PRef, "worldUuid", wuid)
        setf(pr, PRef, "holder", holder)
        if online:
            PLAYERS.put(UUID(0x5117, n), pr)
        return pr

    def xp_of(u, slot):
        return int(Store.data(u)[slot])

    # ---------------------------------------------------------------- C: the row through the real loader
    def cfg_file(name, text):
        d = os.path.join(work, "cfg-" + name)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        f = os.path.join(d, "xp.properties")
        if text is not None:
            open(f, "wb").write(text)
        Cfg.FILE = path(f)
        return f

    C = {}
    f = cfg_file("fresh", None)
    t1 = str(Cfg.load())
    fresh = open(f, "rb").read()
    C["fresh"] = {"mult": float(Cfg.CLASS_MULT), "text": t1, "file": fresh.decode("latin-1"), "classDefaults": str(Cfg.CLASS_DEFAULTS)}
    t2 = str(Cfg.load())
    C["fresh"]["again_same"] = open(f, "rb").read() == fresh
    LINE = b"classSkill.xpMultiplier=3.0\n"
    C["values"] = {}
    for v in ("1", "1.0", "0", "2.5", "100", "250", "-1", "NaN", "abc", " 3 ", "1e1"):
        cfg_file("v", fresh.replace(LINE, ("classSkill.xpMultiplier=%s\n" % v).encode("latin-1")))
        Cfg.load()
        C["values"][v] = float(Cfg.CLASS_MULT)
    # a file without the key: the minimal 0.4.5-style file and the fresh file with the key's block removed
    blk = (b"\n" + str(Cfg.CLASS_DEFAULTS).encode("latin-1"))
    nokey = fresh.replace(blk, b"")
    C["strip_ok"] = nokey != fresh and b"classSkill.xpMultiplier" not in nokey
    f = cfg_file("nokey", nokey)
    Cfg.load()
    a1 = open(f, "rb").read()
    m1 = float(Cfg.CLASS_MULT)
    Cfg.load()
    a2 = open(f, "rb").read()
    C["nokey"] = {"appended": a1 == nokey + blk, "again_same": a2 == a1, "mult": [m1, float(Cfg.CLASS_MULT)], "count": a2.count(b"\nclassSkill.xpMultiplier=")}
    f = cfg_file("old", b"# a SkyySkills 0.4.5 file\nmultiplier=1.0\n")
    Cfg.load()
    o1 = open(f, "rb").read()
    Cfg.load()
    o2 = open(f, "rb").read()
    C["old"] = {"count": o1.count(b"\nclassSkill.xpMultiplier=3.0\n"), "again_same": o1 == o2, "mult": float(Cfg.CLASS_MULT)}
    D["C"] = C

    def at(mult, extra=b"", name="m"):
        """load the fresh default file with classSkill.xpMultiplier=mult (+ extra lines) through the real loader"""
        txt = fresh.replace(LINE, ("classSkill.xpMultiplier=%s\n" % mult).encode("latin-1")) + extra
        cfg_file(name, txt)
        return str(Cfg.load())

    # ---------------------------------------------------------------- K: XP per kill
    K = {}
    role_line = ("combat.role.%s=100\n" % ROLE).encode("latin-1")
    for m in ("1", "3", "0"):
        txt = at(m, role_line)
        K[m] = {"text": txt, "mult": float(Cfg.CLASS_MULT),
                "base": [int(Cfg.combatXp(None, JFloat(h))) for h in HEALTHS],
                "kill": dict((str(s), [int(Cfg.classXp(s, Cfg.combatXp(None, JFloat(h)))) for h in HEALTHS]) for s in CLASS_SLOTS),
                "role": [int(Cfg.combatXp(ROLE, JFloat(50.0))), int(Cfg.classXp(ARCHERY, Cfg.combatXp(ROLE, JFloat(50.0))))],
                "other": dict((str(s), [int(Cfg.classXp(s, x)) for x in (1, 7, 20, 500)]) for s in OTHER_SLOTS),
                "zero": [int(Cfg.classXp(ARCHERY, 0)), int(Cfg.classXp(ARCHERY, -5))]}
    at("3", b"combat.max=50\n", "max50")
    K["max50"] = [int(Cfg.classXp(ARCHERY, Cfg.combatXp(None, JFloat(h)))) for h in HEALTHS]
    at("3", b"multiplier=2.0\n", "mult2")      # the later multiplier= line wins (Properties: last one)
    K["mult2"] = {"MULT": float(Cfg.MULT), "kill100": int(Cfg.classXp(ARCHERY, Cfg.combatXp(None, JFloat(100.0)))),
                  "base100": int(Cfg.combatXp(None, JFloat(100.0))), "mining8": int(Cfg.classXp(MINING, Cfg.scaled(8)))}
    at("2.5")
    v25 = [int(Cfg.classXp(ARCHERY, 1)) for _ in range(20000)]
    K["x25"] = {"set": sorted(set(v25)), "mean": sum(v25) / float(len(v25)), "two": sorted(set(int(Cfg.classXp(ARCHERY, 2)) for _ in range(200))),
                "big": int(Cfg.classXp(ARCHERY, 1000)), "text": str(Cfg.classText())}
    at("1.1")
    K["x11"] = sorted(set(int(Cfg.classXp(ARCHERY, 10)) for _ in range(2000)))
    at("100")
    K["x100"] = [int(Cfg.classXp(ARCHERY, 500)), int(Cfg.classXp(ARCHERY, 90000000000000000))]
    # real awards through SkillXp.gain (the KillSys call), 10 kills of a 100 HP mob per multiplier
    skyy = mkpr(1, "Skyy")
    u1 = UUID(0x5117, 1)
    bridge.put("class:" + str(u1), "Archer")
    aw = {}
    for m in ("1", "3", "0"):
        at(m)
        before, sent0 = xp_of(u1, ARCHERY), int(FakeH.SENT)
        for _ in range(10):
            Xp.gain(skyy, ARCHERY, Cfg.classXp(ARCHERY, Cfg.combatXp(None, JFloat(100.0))))
        aw[m] = {"delta": xp_of(u1, ARCHERY) - before, "sent": int(FakeH.SENT) - sent0}
    K["awards"] = aw
    D["K"] = K

    # ---------------------------------------------------------------- P: the party share
    P = {}
    mate = mkpr(2, "Mate")
    u2 = UUID(0x5117, 2)
    bridge.put("class:" + str(u2), "Priest")
    for m in ("1", "3"):
        at(m)
        cx = int(Cfg.classXp(ARCHERY, Cfg.combatXp(None, JFloat(100.0))))
        amt = int(Px.amount(cx, 0.5))
        before = xp_of(u2, DIVINITY)
        Xp.gain4(mate, DIVINITY, amt, False, False, "Skyy")
        odd = int(Cfg.classXp(ARCHERY, Cfg.combatXp(None, JFloat(37.0))))
        oddv = [int(Px.amount(odd, 0.5)) for _ in range(20000)]
        P[m] = {"cx": cx, "share": amt, "delta": xp_of(u2, DIVINITY) - before, "odd": odd, "odd_set": sorted(set(oddv)),
                "odd_mean": sum(oddv) / float(len(oddv)), "frac": float(JClass(PKG + "PartyCfg").FRACTION)}
    D["P"] = P

    # ---------------------------------------------------------------- H + X: heal XP end to end, the caps
    H = {}
    priest = mkpr(3, "Pria")
    u3 = UUID(0x5117, 3)
    bridge.put("class:" + str(u3), "Priest")
    hfn, afn = HealFn(), AddFn()
    hwin = getf(None, Hx, "HWIN")
    bwin = getf(None, Bx, "WIN")
    JLong, JDouble, JBool = JClass("java.lang.Long"), JClass("java.lang.Double"), JClass("java.lang.Boolean")

    def heal(hp, self_=False, u=u3):
        a = [u, JDouble(hp), "classes:heal", None]
        if self_:
            a.append(JBool.TRUE)
        before = xp_of(u, DIVINITY)
        r = hfn.apply(JClass("java.lang.Object")[:](a))
        return [bool(r), xp_of(u, DIVINITY) - before]

    for m in ("1", "3", "0"):
        at(m)
        hwin.clear()
        bwin.clear()
        ran0 = int(FakeW.RAN)
        H[m] = {"others50": heal(50.0), "self40": heal(40.0, True), "ran": int(FakeW.RAN) - ran0,
                "paid10": int(Bx.paid(u3, DIVINITY, 10, False)), "paid10grant": int(Bx.paid(u3, DIVINITY, 10, True))}
    # a non-Priest heals: refused, nothing paid
    at("3")
    hwin.clear()
    H["archer"] = heal(50.0, False, u1)
    # the heal cap counts the BASE heal XP: 1,500 HP on others in one window = 300 base = the cap (paid 900 at x3), the next heal refused
    hwin.clear()
    bwin.clear()
    capr = [heal(500.0), heal(500.0), heal(500.0), heal(5.0)]
    H["cap"] = {"runs": capr, "window": [int(x) for x in hwin.get(u3)], "cap": int(Dv.MAX_MIN)}
    at("1")
    hwin.clear()
    bwin.clear()
    H["cap_x1"] = [heal(500.0), heal(500.0), heal(500.0), heal(5.0)]
    # bridge.maxXpPerMinute counts the PAID XP: cap 1,000 -> a 400 base heal (2,000 HP) pays 1,200 at x3 = refused; at x1 400 = paid
    at("3", b"bridge.maxXpPerMinute=1000\ndivinity.healXpMaxPerMinute=0\n", "bcap")
    hwin.clear()
    bwin.clear()
    H["bcap_x3"] = {"per_min": int(Bc.PER_MIN), "heal": heal(2000.0), "win": [int(x) for x in bwin.get(u3)] if bwin.get(u3) is not None else None,
                    "small": heal(1500.0)}
    at("1", b"bridge.maxXpPerMinute=1000\ndivinity.healXpMaxPerMinute=0\n", "bcap1")
    hwin.clear()
    bwin.clear()
    H["bcap_x1"] = {"heal": heal(2000.0), "win": [int(x) for x in bwin.get(u3)] if bwin.get(u3) is not None else None}
    # a class skill grant through skill:fn:addxp (an admin listed Archery in bridge.addxp.skills) and a Mining grant (SkyyCollections)
    G = {}
    for m in ("1", "3"):
        at(m, b"bridge.addxp.skills=Mining,Foraging,Farming,Alchemy,Smithing,Cooking,Archery\n", "grant")
        bwin.clear()
        b5, b0 = xp_of(u1, ARCHERY), xp_of(u1, MINING)
        r5 = bool(afn.apply(JClass("java.lang.Object")[:]([u1, "Archery", JLong(100), "test:grant", None])))
        r0 = bool(afn.apply(JClass("java.lang.Object")[:]([u1, "Mining", JLong(500), "collections:tier", None])))
        G["grant" + m] = {"archery": [r5, xp_of(u1, ARCHERY) - b5], "mining": [r0, xp_of(u1, MINING) - b0], "slot": int(Bx.grantSlot("Archery"))}
    at("3")
    G["default_list_archery"] = int(Bx.grantSlot("Archery"))
    D["H"] = H

    # ---------------------------------------------------------------- G: gathering and the other skills unchanged
    for m in ("1", "3"):
        at(m)
        b0 = xp_of(u1, MINING)
        Xp.gain(skyy, MINING, Cfg.scaled(8))
        G[m] = {"scaled": [int(Cfg.scaled(x)) for x in (1, 8, 40)],
                "paid": [int(Bx.paid(u1, MINING, 500, True)), int(Bx.paid(u1, ALCHEMY, 40, False)), int(Bx.paid(u1, SMITHING, 12, False)),
                         int(Bx.paid(u1, COOKING, 30, True)), int(Bx.paid(u1, EXPLORATION, 25, True)), int(Bx.paid(u1, 4, 9, True))],
                "resolve": dict((i, [int(x) for x in Cfg.resolve(i)]) for i in ("Ore_Iron", "Rock_Stone", "Plant_Crop_Wheat_Block", "Wood_Oak_Trunk")),
                "mining_award": xp_of(u1, MINING) - b0}
    D["G"] = G

    # ---------------------------------------------------------------- U: SkyyGuilds counts the real skill XP
    Gu = {}
    try:
        GS, GC, XT = JClass(GPKG + "GuildStore"), JClass(GPKG + "GCfg"), JClass(GPKG + "XpTask")
        gd = os.path.join(work, "guilds")
        os.makedirs(os.path.join(gd, "guilds"), exist_ok=True)
        GS.DIR = path(gd)
        GS.GDIR = path(os.path.join(gd, "guilds"))
        GC.FILE = path(os.path.join(gd, "config.properties"))
        for mp in (GS.GUILDS, GS.BYNAME, GS.BYPLAYER, GS.INVITES, GS.CONFIRM, XT.BASE, XT.FRAC):
            mp.clear()
        GS.SEASON, GS.NEXT_ID, GS.DAY, GS.DAY_READ = 3, 7, 1234, int(System.currentTimeMillis())
        GC.SHARE, GC.MAX_DELTA, GC.LEVEL_FALLBACK, GC.LOG_KEEP, GC.MAX_MEMBERS = 10, 10000000, 25, 200, 25
        GC.MAX_BANK, GC.INVITE_SECONDS, GC.ONLINE_MSG, GC.BASE, GC.STEP = 1000000000000, 300, False, 100, 150
        GC.DEF_LIM_ADMIN, GC.DEF_LIM_MEMBER = -1, 0
        GC.parseSkills(props({"xpSkills": str(GC.DEF_SKILLS)}))
        g = JClass(GPKG + "Guild")()
        g.id, g.name, g.tag, g.created, g.xp, g.bank = "g1", "Xp Guild", "XP", int(System.currentTimeMillis()) - 86400000, 0, 0
        g.limAdmin, g.limMember = -1, 0
        mm = JClass(GPKG + "GMember")()
        mm.uuid, mm.uid, mm.name, mm.rank, mm.joined, mm.contrib = str(u1), u1, "Skyy", 2, int(System.currentTimeMillis()) - 1000000, 0
        g.members.put(mm.uuid, mm)
        GS.BYPLAYER.put(mm.uuid, "g1")
        GS.GUILDS.put("g1", g)
        GS.BYNAME.put("xp guild", "g1")
        bridge.put("skill:fn:xp", XpFn())
        Gu["skills"] = [str(x) for x in GC.SKILLS]
        Gu["baseline"] = int(XT.check(u1))
        steps = []
        for m in ("1", "3"):
            at(m)
            a0 = xp_of(u1, ARCHERY)
            for _ in range(10):
                Xp.gain(skyy, ARCHERY, Cfg.classXp(ARCHERY, Cfg.combatXp(None, JFloat(100.0))))
            gained = xp_of(u1, ARCHERY) - a0
            fnv = int(XpFn().apply(JClass("java.lang.Object")[:]([u1, "Archery"])))
            steps.append([m, gained, int(XT.check(u1)), fnv == xp_of(u1, ARCHERY)])
            Xp.gain(skyy, MINING, Cfg.scaled(80))
            steps.append([m + "mining", 80, int(XT.check(u1)), True])
        Gu["steps"] = steps
        Gu["guild_xp"] = int(GS.GUILDS.get("g1").xp)
        Gu["max_delta"] = int(GC.MAX_DELTA)
    except Exception as e:
        Gu["error"] = repr(e)
    D["U"] = Gu

    # ---------------------------------------------------------------- S: texts
    S = {}
    for m in ("1", "3", "0"):
        at(m)
        S[m] = {"how": dict((str(s), str(Sp.how(s))) for s in CLASS_SLOTS + OTHER_SLOTS), "statsLine": str(Dv.statsLine()),
                "classText": str(Cfg.classText()), "classHow": str(Cfg.classHow())}
    D["S"] = S

    # ---------------------------------------------------------------- R: rows
    D["rows"] = rows_of(Rows)

    # ---------------------------------------------------------------- L: start twice on a scratch COPY of the live data
    lc = os.path.join(SCRATCH, "live-copy")

    def snap(d):
        return dict((os.path.relpath(os.path.join(r, fn), d).replace(os.sep, "/"), open(os.path.join(r, fn), "rb").read())
                    for r, ds, fs in os.walk(d) for fn in fs)
    s0 = snap(lc)
    runs, snaps = [], []
    for k in range(2):
        Cfg.FILE = path(os.path.join(lc, "xp.properties"))
        Hist.DIR = None
        r = [str(x) for x in Mig.run()]
        lt = str(Cfg.load())
        Rows.HOME = path(lc)
        Hist.init()
        kc = str(Mig.keepCopy())
        runs.append([r, kc, float(Cfg.CLASS_MULT), "class skill XP x3" in lt])
        snaps.append(snap(lc))
    s1, s2 = snaps
    ch1 = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
    ch2 = sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k))
    x0, x1 = s0.get("xp.properties", b""), s1.get("xp.properties", b"")
    p0, p1 = Props(), Props()
    p0.load(JClass("java.io.ByteArrayInputStream")(x0))
    p1.load(JClass("java.io.ByteArrayInputStream")(x1))
    k0 = dict((str(k), str(p0.getProperty(k))) for k in p0.stringPropertyNames())
    k1 = dict((str(k), str(p1.getProperty(k))) for k in p1.stringPropertyNames())
    D["L"] = {"runs": runs, "changed1": ch1, "changed2": ch2, "appended": x1 == x0 + blk, "crlf": x0.count(b"\r\n"),
              "newkeys": sorted(set(k1) - set(k0)), "gone": sorted(set(k0) - set(k1)),
              "diffvals": sorted(k for k in k0 if k in k1 and k0[k] != k1[k]), "newval": k1.get("classSkill.xpMultiplier"),
              "n": len(s0), "players": len([k for k in s0 if k.startswith("players/")]), "hist": len([k for k in s0 if k.startswith("config-history/")])}

    # ---------------------------------------------------------------- T: the level table the pacing numbers use
    D["CUM"] = [int(x) for x in Defs.CUM]
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: bytecode compare
def version_only(a, b):
    la, lb = a.split(chr(10)), b.split(chr(10))
    return len(la) == len(lb) and all(x == y or x.replace(OLD_VERSION, VERSION, 1) == y for x, y in zip(la, lb))


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
                ln = str(IP.instructionString(it, it.next(), cpool))
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
        if not n.endswith(".class"):
            continue
        a, b = zo.read(n), zn.read(n)
        if a == b:
            continue
        mo, fo = listing(ClassPool(False), a)
        mn, fn = listing(ClassPool(False), b)
        changed = sorted(k for k in set(mo) & set(mn) if mo[k] != mn[k])
        res["diff"][n] = {"changed": changed, "gone": sorted(set(mo) - set(mn)), "new": sorted(set(mn) - set(mo)),
                          "fields_gone": sorted(set(fo) - set(fn)), "fields_new": sorted(set(fn) - set(fo)),
                          "vo": [k for k in changed if version_only(mo[k], mn[k])]}
    for cls, meth in (("KillSys", "onComponentAdded"), ("BridgeXp", "offer"), ("BridgeXp", "paid")):
        ms, _ = listing(ClassPool(False), zn.read("com/skyy/skills/%s.class" % cls))
        for k, v in ms.items():
            if k.startswith(meth + "("):
                res["flows"]["%s.%s" % (cls, meth)] = v
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ parent
def flow_local(lines, call):
    """the local slot a long returned by `call` is stored in (lstore N right after it), else None"""
    for i, ln in enumerate(lines):
        if call in ln and i + 1 < len(lines):
            m = re.match(r"lstore(?:_| )(\d+)", lines[i + 1].strip())
            return m.group(1) if m else None
    return None


def loaded_before(lines, call, slot):
    """True when the instruction just before every long argument push of `call` ... simplified: an lload of `slot` occurs between the
    previous invoke and this call"""
    for i, ln in enumerate(lines):
        if call in ln:
            j = i - 1
            seen = False
            while j >= 0 and "invoke" not in lines[j]:
                if re.match(r"lload(?:_| )%s$" % slot, lines[j].strip()):
                    seen = True
                j -= 1
            return seen
    return False


def main():
    if "--mkfake" in sys.argv:
        run_mkfake(arg("--mkfake"))
        return
    if "--old-run" in sys.argv:
        run_old(arg("--old-run"), arg("--out"))
        return
    if "--new-run" in sys.argv:
        run_new(arg("--new-run"), arg("--out"), arg("--fake"), arg("--guilds"))
        return
    if "--bytecode" in sys.argv:
        run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
        return
    for j in (JAR, OLD_JAR, GUILDS_JAR):
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
    check(b"classSkill.xpMultiplier" not in livenow, "L: the live xp.properties has no classSkill.xpMultiplier yet (a 0.4.9 file)")
    me = os.path.abspath(__file__)
    fake = os.path.join(SCRATCH, "fake")
    p = subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(os.path.join(fake, "skyytest", "FakeHandler.class"))
          and os.path.isfile(os.path.join(fake, "skyytest", "FakeWorld.class")), "the stand-in packet handler / world classes were generated")
    outs = {"old": os.path.join(SCRATCH, "run-old.json"), "new": os.path.join(SCRATCH, "run-new.json"), "bc": os.path.join(SCRATCH, "bytecode.json")}
    p = subprocess.run([sys.executable, me, "--old-run", OLD_JAR, "--out", outs["old"], "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(outs["old"]), "child JVM for %s ran" % os.path.basename(OLD_JAR))
    p = subprocess.run([sys.executable, me, "--new-run", JAR, "--out", outs["new"], "--dir", SCRATCH, "--fake", fake, "--guilds", GUILDS_JAR], env=env)
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
    block = C["fresh"]["classDefaults"]
    check(C["fresh"]["mult"] == 3.0 and "class skill XP x3" in C["fresh"]["text"] and C["fresh"]["again_same"],
          "C: a fresh file: x3, the load text says 'class skill XP x3', a second load writes nothing")
    check(C["fresh"]["file"].count("\nclassSkill.xpMultiplier=3.0\n") == 1 and C["fresh"]["file"].endswith("\n\n" + block),
          "C: the fresh default file carries the class skill XP block once, at its end")
    od = O["defaults"]
    check(C["fresh"]["file"] == od.replace("# SkyySkills %s - XP rules" % OLD_VERSION, "# SkyySkills %s - XP rules" % VERSION, 1) + "\n" + block,
          "C: the 0.4.10 default file = the 0.4.9 default file (version line) + a blank line + the class skill XP block")
    want = {"1": 1.0, "1.0": 1.0, "0": 0.0, "2.5": 2.5, "100": 100.0, "250": 100.0, "-1": 0.0, "NaN": 0.0, "abc": 3.0, " 3 ": 3.0, "1e1": 10.0}
    check(C["values"] == want, "C: loader values / clamps: %s" % C["values"])
    check(C["strip_ok"] and C["nokey"]["appended"] and C["nokey"]["again_same"] and C["nokey"]["mult"] == [3.0, 3.0] and C["nokey"]["count"] == 1,
          "C: a file without the key gets exactly the block appended once (x3 at once and after): %s" % C["nokey"])
    check(C["old"]["count"] == 1 and C["old"]["again_same"] and C["old"]["mult"] == 3.0, "C: a 0.4.5-style file: the block once, then stable: %s" % C["old"])
    print("C. classSkill.xpMultiplier: fresh x%s, clamps %s, appended once to a file without it" % (C["fresh"]["mult"], C["values"]))
    # ---------------------------------------------------------------- K
    K = D["K"]
    check(K["1"]["base"] == O["kill"] and K["3"]["base"] == O["kill"] and K["0"]["base"] == O["kill"],
          "K: combatXp per health is the 0.4.9 jar's at every multiplier: %s" % O["kill"])
    for m, f in (("1", 1), ("3", 3), ("0", 0)):
        check(all(K[m]["kill"][str(s)] == [x * f for x in O["kill"]] for s in CLASS_SLOTS),
              "K x%s: every class slot pays %d x the 0.4.9 kill XP: %s" % (m, f, K[m]["kill"][str(ARCHERY)]))
        check(all(K[m]["other"][str(s)] == [1, 7, 20, 500] for s in OTHER_SLOTS), "K x%s: every non-class slot unchanged" % m)
        check(K[m]["role"] == [100, 100 * f] and K[m]["zero"] == [0, 0], "K x%s: combat.role 100 -> %d; 0 / negative -> 0: %s" % (m, 100 * f, K[m]["role"]))
        check(K[m]["mult"] == float(m) and ("class skill XP x%s" % m) in K[m]["text"], "K x%s: the load text names it" % m)
    check(K["x25"]["set"] == [2, 3] and abs(K["x25"]["mean"] - 2.5) < 0.03 and K["x25"]["two"] == [5] and K["x25"]["big"] == 2500
          and K["x25"]["text"] == "x2.5", "K x2.5: 1 XP -> 2 or 3 (mean %.3f), 2 -> 5, 1000 -> 2500" % K["x25"]["mean"])
    check(K["x11"] == [11], "K x1.1: 10 XP -> exactly 11 (never 12): %s" % K["x11"])
    check(K["x100"] == [50000, 9000000000000000], "K x100: 500 -> 50,000; a huge number saturates: %s" % K["x100"])
    check(K["mult2"] == {"MULT": 2.0, "kill100": 120, "base100": 40, "mining8": 16}, "K: with multiplier=2 a 100 HP kill = 20 x 2 x 3 = 120, Mining 8 x 2 = 16: %s" % K["mult2"])
    aw = K["awards"]
    check(aw["1"]["delta"] == 200 and aw["3"]["delta"] == 600 and aw["0"]["delta"] == 0,
          "K: REAL awards (SkillXp.gain) of 10 kills of a 100 HP mob: +200 / +600 / +0 Archery: %s" % aw)
    check(aw["1"]["sent"] > 0 and aw["3"]["sent"] > 0 and aw["0"]["sent"] == 0, "K: chat lines went out through the player's packet handler (none at x0)")
    rows_k = ["%7s HP: %4d / %4d / %d" % (("unknown" if h < 0 else "%g" % h), a, b, c)
              for h, a, b, c in zip(HEALTHS, K["1"]["kill"][str(ARCHERY)], K["3"]["kill"][str(ARCHERY)], K["0"]["kill"][str(ARCHERY)])]
    print("K. XP per kill x1 / x3 / x0 (combat.perHealth 0.2, min 1, max 500, default 5):\n   " + "\n   ".join(rows_k)
          + "\n   combat.role 100: %s / %s / %s" % (K["1"]["role"][1], K["3"]["role"][1], K["0"]["role"][1]))
    # ---------------------------------------------------------------- P
    P = D["P"]
    check(P["1"]["cx"] == 20 and P["1"]["share"] == 10 and P["1"]["delta"] == 10 and P["3"]["cx"] == 60 and P["3"]["share"] == 30
          and P["3"]["delta"] == 30, "P: party share of a 100 HP kill = half the MULTIPLIED kill XP: x1 10, x3 30, written as given: %s" % P)
    check(P["3"]["odd"] == 21 and P["3"]["odd_set"] == [10, 11] and abs(P["3"]["odd_mean"] - 10.5) < 0.05 and P["1"]["odd"] == 7
          and P["1"]["odd_set"] == [3, 4], "P: an odd kill XP (37 HP: 7 / 21) shares 3-4 / 10-11 by chance (mean %.3f)" % P["3"]["odd_mean"])
    print("P. party share (fraction %s) of a 100 HP kill: x1 %d of %d, x3 %d of %d" % (P["3"]["frac"], P["1"]["share"], P["1"]["cx"], P["3"]["share"], P["3"]["cx"]))
    # ---------------------------------------------------------------- H
    H = D["H"]
    for m, f in (("1", 1), ("3", 3), ("0", 0)):
        check(H[m]["others50"] == [True, 10 * f] and H[m]["self40"] == [True, 10 * f],
              "H x%s: skill:fn:healxp 50 HP on others / 40 HP on yourself -> +%d Divinity XP each, end to end: %s %s" % (m, 10 * f, H[m]["others50"], H[m]["self40"]))
        check(H[m]["ran"] == (2 if f else 0) and H[m]["paid10"] == 10 * f and H[m]["paid10grant"] == 10 * f,
              "H x%s: the bridge task ran on the (stand-in) world thread; BridgeXp.paid(10) = %d" % (m, 10 * f))
    check(H["archer"] == [False, 0], "H: a non-Priest's heal is refused, nothing paid: %s" % H["archer"])
    print("H. heal XP end to end: 50 HP on others / 40 HP on yourself = %s / %s / %s Divinity XP at x1 / x3 / x0"
          % (H["1"]["others50"][1], H["3"]["others50"][1], H["0"]["others50"][1]))
    # ---------------------------------------------------------------- X
    check(K["3"]["kill"][str(ARCHERY)][HEALTHS.index(2500.0)] == 1500 and K["3"]["kill"][str(ARCHERY)][HEALTHS.index(10000.0)] == 1500
          and K["1"]["kill"][str(ARCHERY)][HEALTHS.index(10000.0)] == 500, "X: combat.max 500 sits before the multiplier: 2,500 / 10,000 HP pay 1,500 at x3")
    check(K["3"]["kill"][str(ARCHERY)][HEALTHS.index(2.0)] == 3 and K["3"]["kill"][str(ARCHERY)][0] == 15, "X: combat.min 1 -> 3, combat.default 5 -> 15 at x3")
    check(K["max50"] == [min(50, x) * 3 for x in O["kill"]], "X: combat.max=50 -> at most 150 a kill at x3: %s" % K["max50"])
    cap = H["cap"]
    check(cap["cap"] == 300 and [r[1] for r in cap["runs"]] == [300, 300, 300, 0] and [r[0] for r in cap["runs"]] == [True, True, True, False]
          and cap["window"][1] == 300, "X: divinity.healXpMaxPerMinute counts BASE heal XP: 3 x 500 HP = 300 base = the cap, paid 900 at x3, the next heal refused: %s" % cap)
    check([r[1] for r in H["cap_x1"]] == [100, 100, 100, 0], "X: the same minute at x1 pays 300: %s" % H["cap_x1"])
    b3, b1 = H["bcap_x3"], H["bcap_x1"]
    check(b3["per_min"] == 1000 and b3["heal"] == [False, 0] and b3["small"] == [True, 900] and b1["heal"] == [True, 400],
          "X: bridge.maxXpPerMinute counts PAID XP: cap 1,000 - a 400 base heal = 1,200 paid at x3 refused, 300 base = 900 paid; x1 400 paid: %s %s" % (b3, b1))
    print("X. caps: combat.max before the multiplier (2,500 HP = 1,500 at x3); heal cap 300 BASE a minute = 900 paid at x3; bridge.maxXpPerMinute counts the paid XP")
    # ---------------------------------------------------------------- G
    G = D["G"]
    check(G["1"] == {k: v for k, v in G["3"].items()} and G["1"]["scaled"] == [1, 8, 40] and G["1"]["paid"] == [500, 40, 12, 30, 25, 9]
          and G["1"]["mining_award"] == 8, "G: gathering / Alchemy / Smithing / Cooking / Exploration / Acrobatics identical at x1 and x3: %s" % G["1"])
    check(G["1"]["resolve"] == O["resolve"], "G: block rules = the 0.4.9 jar's: %s" % O["resolve"])
    check(G["grant1"]["archery"] == [True, 100] and G["grant3"]["archery"] == [True, 300] and G["grant1"]["mining"] == [True, 500]
          and G["grant3"]["mining"] == [True, 500] and G["grant3"]["slot"] == ARCHERY and G["default_list_archery"] == -1,
          "G: skill:fn:addxp into a listed class skill 100 -> 100 / 300; a Mining grant 500 both times; Archery not grantable by default: %s" % G)
    print("G. gathering unchanged: Mining grant 500, Alchemy 40, Smithing 12, Cooking 30, Exploration 25, Acrobatics 9, a real Mining award +8 at x1 and x3")
    # ---------------------------------------------------------------- U
    Gu = D["U"]
    check("error" not in Gu, "U: SkyyGuilds ran: %s" % Gu.get("error"))
    if "error" not in Gu:
        st = Gu["steps"]
        check(Gu["baseline"] == 0 and st[0][:3] == ["1", 200, 20] and st[1][2] == 8 and st[2][:3] == ["3", 600, 60] and st[3][2] == 8
              and all(s[3] for s in st) and Gu["guild_xp"] == 96 and "Archery" in Gu["skills"] and Gu["max_delta"] == 10000000,
              "U: SkyyGuilds credits 10 %% of the XP actually gained: x1 200 -> 20, x3 600 -> 60, Mining 80 -> 8: %s" % st)
        print("U. SkyyGuilds %s: guild XP = 10%% of real skill XP (x1 200 Archery -> %d, x3 600 -> %d, Mining 80 -> %d); xpMaxPerCheck %d skill XP per 10 s"
              % (os.path.basename(GUILDS_JAR), st[0][2], st[2][2], st[1][2], Gu["max_delta"]))
    # ---------------------------------------------------------------- S
    S = D["S"]
    for s in CLASS_SLOTS:
        o = O["how"][str(s)]
        check(S["1"]["how"][str(s)] == o and S["3"]["how"][str(s)] == o + ". Class skill XP x3 on this server"
              and S["0"]["how"][str(s)] == o + ". Class skill XP is off on this server", "S: how(%d) x1 = 0.4.9, x3 / x0 add the line: %s" % (s, S["3"]["how"][str(s)]))
    for s in OTHER_SLOTS:
        check(S["1"]["how"][str(s)] == S["3"]["how"][str(s)] == S["0"]["how"][str(s)] == O["how"][str(s)], "S: how(%d) unchanged" % s)
    check(S["1"]["statsLine"] == O["statsLine"], "S: Divinity heal line at x1 = 0.4.9: %s" % O["statsLine"])
    check(S["3"]["statsLine"] == "Healing pays 0.6 Divinity XP per HP on others, 0.75 on yourself (class skill XP x3, max 900 a minute)",
          "S: Divinity heal line at x3: %s" % S["3"]["statsLine"])
    check(S["0"]["statsLine"] == "Healing pays no Divinity XP on this server (class skill XP x0)", "S: x0: %s" % S["0"]["statsLine"])
    print("S. Stats: %r ; %r" % (S["3"]["how"][str(ARCHERY)], S["3"]["statsLine"]))
    # ---------------------------------------------------------------- R
    ro, rn = O["rows"], D["rows"]
    ko, kn = [r[0] for r in ro["rows"]], [r[0] for r in rn["rows"]]
    check(len(kn) == len(ko) + 1 and [k for k in kn if k != "classSkill.xpMultiplier"] == ko, "R: one row more, every other key in the same order")
    nr = rn["rows"][kn.index("classSkill.xpMultiplier")]
    check(nr == ["classSkill.xpMultiplier", "Class skill XP multiplier", "combat", "dec", "3.0", "0", "100", "", "x", "live",
                 "Class skill XP from kills, party shares and Priest heals times this, on top of the XP multiplier."], "R: the new row: %s" % nr)
    check([r[0] for r in rn["rows"] if r[2] == "combat"][0] == "classSkill.xpMultiplier", "R: it is the first row of the Combat tab")
    od_ = dict((r[0], r) for r in ro["rows"])
    diff = sorted(r[0] for r in rn["rows"] if r[0] in od_ and r != od_[r[0]])
    check(diff == ["combat.max", "divinity.healXpMaxPerMinute", "multiplier"], "R: only these rows' texts changed: %s" % diff)
    check(all([x for i, x in enumerate(rn["rows"][kn.index(k)]) if i != 10] == [x for i, x in enumerate(od_[k]) if i != 10] for k in diff),
          "R: ... and only their help (index 10)")
    bo, bn = ro["binds"], rn["binds"]
    ix = kn.index("classSkill.xpMultiplier")
    check(all([v for i, v in enumerate(bn[c]) if i != ix] == bo[c] for c in bo) and bn["BK"][ix] == bn["BK"][kn.index("combat.perHealth")]
          and bn["BFK"][ix] == "classSkill.xpMultiplier", "R: the bindings are 0.4.9's + the new row's (reload, file key classSkill.xpMultiplier)")
    print("R. rows %d -> %d: + classSkill.xpMultiplier (Combat, first); help text of %s" % (len(ko), len(kn), ", ".join(diff)))
    # ---------------------------------------------------------------- L
    L = D["L"]
    check(L["runs"][0][2] == 3.0 and L["runs"][1][2] == 3.0 and L["runs"][0][3] and L["runs"][1][3] and L["runs"][0][0] == L["runs"][1][0],
          "L: x3 on both starts, the load text says so, ManaMig finds nothing twice: %s" % L["runs"])
    check(L["changed1"] == ["xp.properties"] and L["appended"] and L["newkeys"] == ["classSkill.xpMultiplier"] and L["gone"] == []
          and L["diffvals"] == [] and L["newval"] == "3.0", "L: the first start only appends the class skill XP block (only the new key): %s" % L)
    check(L["changed2"] == [], "L: the second start writes nothing: %s" % L["changed2"])
    print("L. live copy (%d files, %d players, %d history): start 1 appends only classSkill.xpMultiplier=3.0, start 2 writes nothing"
          % (L["n"], L["players"], L["hist"]))
    # ---------------------------------------------------------------- F
    diff = bc["diff"]
    beyond = dict((n.split("/")[-1][:-6], d) for n, d in diff.items() if set(d["changed"]) != set(d["vo"]) or d["new"] or d["gone"]
                  or d["fields_new"] or d["fields_gone"])
    vonly = sorted(n.split("/")[-1][:-6] for n, d in diff.items() if n.split("/")[-1][:-6] not in beyond)
    want_cls = {"SkillCfg", "KillSys", "BridgeXp", "StatsPage", "DivCfg", "CfgRows", "CfgFile"}
    check(set(beyond) == want_cls, "F: classes changed beyond the version string: %s" % sorted(beyond))
    cf = beyond.get("CfgFile", {})
    check(cf.get("changed") == ["<clinit>()V"] and not cf.get("new") and not cf.get("gone") and not cf.get("fields_new"),
          "F: CfgFile: only its static default-file lines (<clinit>: the version line + the class skill XP block): %s" % cf)
    cr = beyond.get("CfgRows", {})
    check(set(cr.get("changed", [])) - set(cr.get("vo", [])) <= {"<clinit>()V"} and not cr.get("new") and not cr.get("fields_new"),
          "F: CfgRows: only its static row arrays (<clinit>): %s" % cr)
    sc = beyond.get("SkillCfg", {})
    check(sorted(sc.get("new", [])) == sorted(["classHow()Ljava/lang/String;", "classText()Ljava/lang/String;", "classXp(IJ)J",
                                              "ensureClass(Ljava/util/Properties;)V"]) and sc.get("gone") == []
          and sorted(sc.get("fields_new", [])) == ["CLASS_DEFAULTS Ljava/lang/String;", "CLASS_MULT D"]
          and set(sc.get("changed", [])) - set(sc.get("vo", [])) <= {"load()Ljava/lang/String;", "<clinit>()V"},
          "F: SkillCfg: + CLASS_MULT / CLASS_DEFAULTS, + ensureClass / classXp / classText / classHow, load (+ the default text): %s" % sc)
    ks = beyond.get("KillSys", {})
    check([k for k in ks.get("changed", []) if k not in ks.get("vo", [])] == ["onComponentAdded(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Component;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;)V"]
          and not ks.get("new") and not ks.get("fields_new"), "F: KillSys: only onComponentAdded: %s" % ks)
    bx = beyond.get("BridgeXp", {})
    check(bx.get("new") == ["paid(Ljava/util/UUID;IJZ)J"] and [k for k in bx.get("changed", []) if k not in bx.get("vo", [])] == [
        "offer(Ljava/util/UUID;IJLjava/lang/String;Ljava/lang/String;Lcom/hypixel/hytale/server/core/asset/type/item/config/CraftingRecipe;IZ)J"],
          "F: BridgeXp: + paid, offer changed: %s" % bx)
    for cls, meth in (("StatsPage", "how(I)Ljava/lang/String;"), ("DivCfg", "statsLine()Ljava/lang/String;")):
        d = beyond.get(cls, {})
        check([k for k in d.get("changed", []) if k not in d.get("vo", [])] == [meth] and not d.get("new") and not d.get("fields_new"),
              "F: %s: only %s: %s" % (cls, meth, d))
    for cls in ("SkillXp", "HealXp", "PartyXp", "BridgeTask", "SkillXpFn", "SkillAddFn", "SkillHealFn", "BreakSys", "HarvestSys", "CraftTask", "SmeltTask",
                "ManaMig", "ManaGuard", "ManaCost", "Overall", "OverallCfg", "SkillsPage", "OverallPage", "SkillStore", "SkillClass", "Perks", "Acro"):
        n = "com/skyy/skills/%s.class" % cls
        check(n in bc["same"] or cls in vonly, "F: %s byte-identical (or the version string only)" % cls)
    check(not bc["only_old"] and not bc["only_new"], "F: the same entries in both jars: %s %s" % (bc["only_old"], bc["only_new"]))
    fl = bc["flows"]
    kl = fl.get("KillSys.onComponentAdded", "").split("\n")
    loc = flow_local(kl, "SkillCfg.classXp(")
    ci = [i for i, ln in enumerate(kl) if "SkillCfg.combatXp" in ln]
    xi = [i for i, ln in enumerate(kl) if "SkillCfg.classXp" in ln]
    check(len(ci) == 1 and len(xi) == 1 and ci[0] < xi[0] and loc is not None and loaded_before(kl, "SkillXp.gain(", loc)
          and loaded_before(kl, "PartyXp.share(", loc), "F: KillSys: combatXp -> classXp -> ONE local (%s) that SkillXp.gain and PartyXp.share both get" % loc)
    ol = fl.get("BridgeXp.offer", "").split("\n")
    pl = flow_local(ol, "BridgeXp.paid(")
    check(pl is not None and loaded_before(ol, "BridgeXp.allow(", pl) and not any(("SkillCfg.scaled" in ln or "SkillCfg.classXp" in ln or "SkillBonus.boost" in ln) for ln in ol),
          "F: BridgeXp.offer: paid() -> ONE local (%s) that allow() and the BridgeTask get; no multiplier of its own" % pl)
    pa = fl.get("BridgeXp.paid", "")
    check(pa.index("SkillCfg.scaled") < pa.index("SkillCfg.classXp") < pa.index("SkillBonus.boost"), "F: BridgeXp.paid: xp multiplier -> class skill XP multiplier -> tree bonus")
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    mo = json.loads(zo.read("manifest.json"))
    mn = json.loads(zn.read("manifest.json"))
    kd = sorted(k for k in set(mo) | set(mn) if mo.get(k) != mn.get(k))
    check(kd == ["Description", "Name", "Version"] or kd == ["Description", "Version"], "F: manifest: only %s differ" % kd)
    check("Class skills earn 3x XP by default" in mn.get("Description", ""), "F: the manifest description names the multiplier")
    nonclass = sorted(n for n in set(zo.namelist()) | set(zn.namelist()) if not n.endswith(".class") and n != "manifest.json"
                      and (n not in zo.namelist() or n not in zn.namelist() or zo.read(n) != zn.read(n)))
    check(nonclass == [], "F: every non-class entry (the 40 generated spell overrides ...) byte-identical: %s" % nonclass[:5])
    print("F. class bytes: changed beyond the version %s; version only %s; KillSys local %s; offer local %s" % (
        ", ".join(sorted(beyond)), ", ".join(vonly), loc, pl))
    # ---------------------------------------------------------------- T: the pacing table
    cum = D["CUM"]
    zones = [(0, 10, 15), (10, 15, 35), (15, 25, 35), (25, 40, 50)]   # (from, to, typical kill XP) - research/Mob-Levels-Plan.md section 7
    print("T. kills to reach a class skill level (typical kill XP per zone from research/Mob-Levels-Plan.md 7: Zone 1 15, Zone 2 35, Zone 3 50):")
    print("   level   cumulative XP      x1 kills      x3 kills    (100 HP mobs only: x1 / x3)")
    tot1 = tot3 = 0
    for a, b, kx in zones:
        seg = cum[b] - cum[a]
        tot1 += int(math.ceil(seg / float(kx)))
        tot3 += int(math.ceil(seg / float(kx * 3)))
        print("   %5d %15s %13s %13s    %s / %s" % (b, "{:,}".format(cum[b]), "{:,}".format(tot1), "{:,}".format(tot3),
                                                    "{:,}".format(int(math.ceil(cum[b] / 20.0))), "{:,}".format(int(math.ceil(cum[b] / 60.0)))))
    check(cum[25] == 3022425 and cum[10] == 9925, "T: the level table is the Hypixel curve (skill 25 = 3,022,425 XP)")
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
