"""SkyySkills 0.4.12 - bare-JVM harness for the class skill curve + in-combat Mana regen round (tools/skills_0_4_12_patch.py):
class skills level on their own table (research/cloud/Class-Skill-Curve-Proposal.md section 5), every level comes from a per-slot lookup,
class level = max(general, class) up to the class max, the one-time class curve notice + its level-up rewards (ClassCurve), Mana refills
in combat at mana.regen.inCombat % of (vanilla + Mana Regen boosts) (ManaRegen), the skill:fn:manaregen registry.

    python SkyySkills/test_skyyskills_0.4.12.py [--jar <SkyySkills-0.4.12.jar>] [--old <SkyySkills-0.4.11.jar>] [--dir <scratch>]
                                                [--live <Skyy_SkyySkills folder>] [--keep]

Build first (python tools/skills_0_4_12_patch.py, then python SkyySkills/build_skyyskills_0.4.12.py). The old jar = the SET pin 0.4.11.
Child processes start fresh JVMs (the game's own JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + the jars; TEMP / TMP /
java.io.tmpdir in the scratch folder). The live world is READ ONLY: its Skyy_SkyySkills folder is copied into the scratch folder and only
that copy is ever written.
  A  every class of the 0.4.12 jar AND of the 0.4.11 jar loads and initializes under -Xverify:all
  T  the class table = the proposal's section 5 (parsed from the proposal file here) for levels 1-100, totals = its Total column, the
     general table = 0.4.11's; for every level boundary of both tables (+-1) and random totals: non-class slots level / intoLevel / needFor
     / progress = the 0.4.11 jar's global lookup, class slots = the proposal table's, maxOf 100 / 100
  G  the guard: class level = max(general, class) (a steeper class list), capped by the class max (levels.class 60 entries), the general
     list cut to 50 (class levels above 50 still on the class list), sameAsOthers = the general table exactly
  P  per-slot everywhere for a Priest with 67,425 Divinity XP (0.4.11 level 15, now 28) and 67,425 Mining XP (15 both): SkillStore.level,
     skill:fn:level (Divinity / Priest / Combat / Mining / Overall), skill:fn:xp (the total, unchanged), skill:<uuid>, skill:fn:overall,
     the /skills page, its Top 10 view, the Stats page, the Overall page, the +XP and [Party] chat lines, a real level up through
     SkillXp.gain (SKILL LEVEL UP Divinity 19 -> 20 +2,000 coins, next at 3.35k) and a Mining level up on the general table
  M  ClassCurve on scratch COPIES of the live data: (1) the live copy: first start scans every profile file, nobody rose (Skyy's class XP
     420 / 384 / 20 are the same level on both tables), the record is written, a second start changes nothing, the player files never
     change, xp.properties gains exactly the two appended blocks once; (2) an edited copy with risen profiles: one chat line each, the
     level-up coins of exactly the gained levels (paid markers), the Overall level up, the crossbow unlock line, the record (pending ->
     done, player file saved first), a second tick / a later award / a restart pay nothing again, the other profile told when it becomes
     active; (3) profile:busy waits; (4) an unwritable record: nobody told, the next start scans again; (5) SkyyCoins missing: the line
     once, the coins stay owed for the normal late payout
  R  Mana regen maths: ManaRegen.amount (out of combat = vanilla + rate x MR, in combat = F% of (rate x (1 + MR)), 0% = vanilla, max cap,
     no Mana, clamps, 6 s in combat at 50% = 15 Mana) and ManaRegen.rates / state on REAL engine conditions (AliveCondition,
     NoDamageTakenCondition 6 s, a charging stand-in) through REAL RegeneratingValue entries; mana.regen.inCombat load + clamps
  B  skill:fn:manaregen add / remove / get / sources / clear (java.lang types, bad arguments, clamps) feeding total(); the Server Setup
     action text
  C  the loader: the 0.4.12 default file = 0.4.11's + the version line, the levels comment and the two blocks; an old file gets both
     blocks once (LF and CRLF kept), an admin's levels.class.sameAsOthers is never overwritten, bad / short class lists
  K  the Server Setup rows: 180, the 0.4.11 keys in order + the 6 new ones after their neighbours; changed: the three general curve rows'
     label / help only; the class curve custom rows (get / set / read, cut + raise back exactly, scale 110 and back); kill / party /
     heal / grant XP = the 0.4.11 jar's
  F  class bytes 0.4.11 vs 0.4.12: + ClassCurve, ManaRegen, ManaRegenFn, ManaCmd; the changed classes are exactly the per-slot sites +
     hooks; KillSys, HealXp, BridgeXp, BridgeTask, HealMig, ManaMig, ManaGuard, the bridge Functions ... byte-identical or version only;
     manifest Version / Name / Description only; every non-class entry byte-identical
  X  the review fixes (each check fails on the first 0.4.12 jar): (R1) the Overall page with no counted skill is not the max layout
     ("Level 0 of 0", "No skill counts ...", one "Nothing - no skill counts" line) while a maxed player still gets "Max Overall Level
     reached"; (R3) AcroSys.tick calls ManaRegen.tick before the Acrobatics block, Brew.tick and Xbow.tick (bytecode order); (R4)
     ManaRegen.compact exact lines (vanilla 5/s, boosts, 0% in combat, unknown rate) and <= 110 characters with 12 sources / a 64-character
     source / +1000%, the Server Setup action uses it, /skills mana keeps the full text; (R5) the class curve size message reports the
     EFFECTIVE totals (150%: class skill 1 at 50 XP, not 75) and "not in use" while sameAsOthers is on; (R9) SkillKit.customSet /
     SkillKit.reload clear SkillStore.PUBLISHED and /skills reload calls republishAll (bytecode), and end to end skill:<uuid> goes from
     Divinity:28 to Divinity:20 at the next publishOnline after Class max level 20
Nothing is deployed. Default scratch folder: tools/dev/scratch/skills0412/harness (deleted at the end unless --keep; --dir must be a folder
INSIDE tools/dev/scratch/). Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.4.12", "0.4.11"
PKG = "com.skyy.skills."
CLASS_SLOTS = [5, 6, 7, 8, 9, 14, 15]
OTHER_SLOTS = [0, 1, 2, 3, 4, 10, 11, 12, 13]
ARCHERY, WARRIOR, DIVINITY, MINING, ALCHEMY, SMITHING, COOKING, EXPLORATION = 5, 6, 15, 0, 10, 11, 12, 13
HEALTHS = [-1.0, 2.0, 5.0, 7.0, 20.0, 37.0, 100.0, 250.0, 1000.0, 2500.0, 10000.0]
NEW_KEYS = ["levels.class", "levels.class.scale", "levels.class.max", "levels.class.sameAsOthers", "mana.regen.inCombat", "mana.regen.show"]


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skills0412", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyySkills-%s.jar" % OLD_VERSION)))
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


def proposal_table():
    md = open(os.path.join(ROOT, "research", "cloud", "Class-Skill-Curve-Proposal.md"), encoding="utf8").read()
    sec = md[md.index("## 5. Per-level table"):md.index("## 6.")]
    rows = []
    for ln in sec.splitlines():
        m = re.match(r"\|\s*(\d+)\s*\|\s*([\d,]+)\s*\|\s*([\d,]+)\s*\|\s*([\d,]+)\s*\|", ln)
        if m:
            rows.append(tuple(int(x.replace(",", "")) for x in m.groups()))
    return rows


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
    """skyytest.FakeHandler (PacketHandler: counts packets, keeps every chat text), FakeWorld (World.execute runs at once), FixedCondition
    (a Condition whose eval0 answers a field - the charging stand-in), FakeAcc (a ComponentAccessor answering getComponent with one
    DamageDataComponent and getArchetype with one Archetype)."""
    import jpype
    from jpype import JClass
    import skyybuild as B
    jpype.startJVM(B._jvm(), "-XX:-UsePerfData", classpath=[B.JAVASSIST], convertStrings=True)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    h = cp.makeClass("skyytest.FakeHandler")
    h.setSuperclass(cp.get("com.hypixel.hytale.server.core.io.PacketHandler"))
    h.addField(CtField.make("public static volatile int SENT = 0;", h))
    h.addField(CtField.make("public static final java.util.List TEXTS = java.util.Collections.synchronizedList(new java.util.ArrayList());", h))
    h.addMethod(CtNewMethod.make("""public void writeNoCache(com.hypixel.hytale.protocol.ToClientPacket p) {
  SENT = SENT + 1;
  if (p instanceof com.hypixel.hytale.protocol.packets.interface_.ServerMessage) {
    com.hypixel.hytale.protocol.FormattedMessage m = ((com.hypixel.hytale.protocol.packets.interface_.ServerMessage) p).message;
    TEXTS.add(m == null ? "" : String.valueOf(m.rawText));
  }
}""", h))
    h.writeFile(out_dir)
    w = cp.makeClass("skyytest.FakeWorld")
    w.setSuperclass(cp.get("com.hypixel.hytale.server.core.universe.world.World"))
    w.addField(CtField.make("public static volatile int RAN = 0;", w))
    w.addMethod(CtNewMethod.make("public void execute(java.lang.Runnable r) { RAN = RAN + 1; r.run(); }", w))
    w.writeFile(out_dir)
    c = cp.makeClass("skyytest.FixedCondition")
    c.setSuperclass(cp.get("com.hypixel.hytale.server.core.modules.entity.condition.Condition"))
    c.addField(CtField.make("public boolean v;", c))
    c.addConstructor(CtNewConstructor.make("public FixedCondition(boolean v) { super(false); this.v = v; }", c))
    c.addMethod(CtNewMethod.make("public boolean eval0(com.hypixel.hytale.component.ComponentAccessor a, com.hypixel.hytale.component.Ref r, java.time.Instant n) { return this.v; }", c))
    c.writeFile(out_dir)
    a = cp.makeClass("skyytest.FakeAcc")
    a.addInterface(cp.get("com.hypixel.hytale.component.ComponentAccessor"))
    a.addField(CtField.make("public com.hypixel.hytale.component.Component dd;", a))
    a.addField(CtField.make("public com.hypixel.hytale.component.Archetype arch;", a))
    a.addConstructor(CtNewConstructor.make("public FakeAcc() { }", a))
    a.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) { return this.dd; }", a))
    a.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Archetype getArchetype(com.hypixel.hytale.component.Ref r) { return this.arch; }", a))
    a.writeFile(out_dir)


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


def totals_to_test(cum_a, cum_b):
    """every level boundary of both tables, +-1, plus random totals up to past the end of the longer one"""
    xs = set([0, 1])
    for c in (cum_a, cum_b):
        for v in c:
            for d in (-1, 0, 1):
                if v + d >= 0:
                    xs.add(v + d)
    rnd = random.Random(412)
    top = max(cum_a[-1], cum_b[-1]) + 1000000
    for _ in range(1500):
        xs.add(rnd.randrange(0, top))
    return sorted(xs)


def common(jar, extra_cp):
    from jpype import JClass
    _jvm_start([jar] + extra_cp)
    res = load_all(jar)
    Paths, JStr, Arr = JClass("java.nio.file.Paths"), JClass("java.lang.String"), JClass("java.lang.reflect.Array")

    def path(p):
        return Paths.get(p, Arr.newInstance(JStr.class_, 0))
    return res, path


def defaults_part(D, Cfg, Rows, Bx, path, work):
    """numbers both jars must agree on: kill XP at the defaults, grants / gathering paid, rows, the default file"""
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
                 int(Bx.paid(u, ARCHERY, 100, True)), int(Bx.paid(u, DIVINITY, 10, False)), int(Bx.paidX(u, DIVINITY, 10, False, False))]
    D["rows"] = rows_of(Rows)


# ============================================================================================ child: the 0.4.11 jar (baseline numbers)
def run_old(jar, out, xs_file):
    from jpype import JClass, JLong
    res, path = common(jar, [])
    if not res["load_fails"]:
        D = res["data"]
        work = os.path.join(SCRATCH, "old")
        os.makedirs(work, exist_ok=True)
        defaults_part(D, JClass(PKG + "SkillCfg"), JClass(PKG + "CfgRows"), JClass(PKG + "BridgeXp"), path, work)
        Defs = JClass(PKG + "SkillDefs")
        Defs.setTable(Defs.DEFAULT_PER)
        D["per"] = [int(x) for x in Defs.DEFAULT_PER]
        D["cum"] = [int(x) for x in Defs.CUM]
        xs = json.load(open(xs_file))
        D["xs"] = [[int(Defs.levelOf(JLong(x))), int(Defs.intoLevel(JLong(x))), int(Defs.needFor(JLong(x))), str(Defs.progress(JLong(x)))] for x in xs]
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: the 0.4.12 jar
def run_new(jar, out, fake, xs_file):
    from jpype import JClass, JFloat, JLong, JImplements, JOverride, JArray, JObject
    res, path = common(jar, [fake])
    if res["load_fails"]:
        json.dump(res, open(out, "w"), indent=1)
        return
    D = res["data"]
    UUID, CHM, Props = JClass("java.util.UUID"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.Properties")
    Cfg, Xp, Store, Defs = JClass(PKG + "SkillCfg"), JClass(PKG + "SkillXp"), JClass(PKG + "SkillStore"), JClass(PKG + "SkillDefs")
    Bx, Rows, Kit, Curve = JClass(PKG + "BridgeXp"), JClass(PKG + "CfgRows"), JClass(PKG + "SkillKit"), JClass(PKG + "ClassCurve")
    Mana, ManaFn, Ovl, Px, Msg = JClass(PKG + "ManaRegen"), JClass(PKG + "ManaRegenFn"), JClass(PKG + "Overall"), JClass(PKG + "PartyXp"), JClass(PKG + "SkillMsg")
    SkillFn, XpFn, OvFn, Top = JClass(PKG + "SkillFn"), JClass(PKG + "SkillXpFn"), JClass(PKG + "OverallFn"), JClass(PKG + "SkillTop")
    SkillsPage, StatsPage, OverallPage = JClass(PKG + "SkillsPage"), JClass(PKG + "StatsPage"), JClass(PKG + "OverallPage")
    Hist, CLog, Mig, HMig, CfgFn = JClass(PKG + "CfgHist"), JClass(PKG + "CfgLog"), JClass(PKG + "ManaMig"), JClass(PKG + "HealMig"), JClass(PKG + "CfgFn")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Universe, Holder = JClass("com.hypixel.hytale.server.core.universe.Universe"), JClass("com.hypixel.hytale.component.Holder")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    FakeH, FakeW, Fixed, FakeAcc = JClass("skyytest.FakeHandler"), JClass("skyytest.FakeWorld"), JClass("skyytest.FixedCondition"), JClass("skyytest.FakeAcc")
    JDouble, JBool, JLongC, JObj, JInt = JClass("java.lang.Double"), JClass("java.lang.Boolean"), JClass("java.lang.Long"), JClass("java.lang.Object"), JClass("java.lang.Integer")
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

    @JImplements("java.util.function.Function")
    class Const(object):
        def __init__(self, v):
            self.v = v

        @JOverride
        def apply(self, o):
            return self.v

    COINS = []

    @JImplements("java.util.function.Function")
    class Coins(object):
        @JOverride
        def apply(self, o):
            COINS.append([str(o[0]), int(o[1])])
            return JLongC(1000000 + sum(c[1] for c in COINS))

    ACTIVE = {}

    @JImplements("java.util.function.Function")
    class PKey(object):
        @JOverride
        def apply(self, o):
            k = ACTIVE.get(str(o))
            return k if k is not None else str(o)

    bridge = Store.bridge()
    work = os.path.join(SCRATCH, "new")
    os.makedirs(work, exist_ok=True)
    defaults_part(D, Cfg, Rows, Bx, path, work)
    D["marker_heal"] = str(HMig.MG_MARK)
    D["curve_block"] = str(Cfg.CURVE_DEFAULTS)
    D["mreg_block"] = str(Cfg.MREG_DEFAULTS)

    # ---------------------------------------------------------------- T: the tables
    Defs.setTable(Defs.DEFAULT_PER)
    Defs.setClassTable(Defs.DEFAULT_CPER, False)
    T = {"cper": [int(x) for x in Defs.DEFAULT_CPER], "per": [int(x) for x in Defs.DEFAULT_PER], "ccum": [int(x) for x in Defs.CCUM],
         "cum": [int(x) for x in Defs.CUM], "ecum": [int(x) for x in Defs.ECUM], "maxes": [int(Defs.maxOf(s)) for s in range(16)],
         "cmax": int(Defs.CMAX), "max": int(Defs.MAX), "same": bool(Defs.SAME)}
    xs = json.load(open(xs_file))
    T["xs"] = {}
    for s in (MINING, 4, 3, COOKING, EXPLORATION, ARCHERY, DIVINITY, WARRIOR):
        T["xs"][str(s)] = [[int(Defs.levelOf(s, JLong(x))), int(Defs.intoLevel(s, JLong(x))), int(Defs.needFor(s, JLong(x))), str(Defs.progress(s, JLong(x)))] for x in xs]
    T["general"] = [int(Defs.generalLevel(JLong(x))) for x in xs]
    D["T"] = T

    # ---------------------------------------------------------------- G: the guard
    G = {}
    steep = [1000] * 100                                          # level 1 needs 1000 (general 50) ... level 100 = 100,000 total
    Defs.setClassTable(JArray(JLong)(steep), False)
    G["steep"] = [[int(Defs.levelOf(DIVINITY, JLong(x))), int(Defs.generalLevel(JLong(x))), int(Defs.levelIn(Defs.CCUM, JLong(x)))] for x in xs[::7]]
    G["steep_ecum"] = [int(x) for x in Defs.ECUM]
    Defs.setClassTable(JArray(JLong)([int(x) for x in Defs.DEFAULT_CPER][:60]), False)
    G["cut60"] = [int(Defs.maxOf(DIVINITY)), int(Defs.levelOf(DIVINITY, JLong(10 ** 12))), int(Defs.maxOf(MINING)), int(Defs.needFor(DIVINITY, JLong(10 ** 12))),
                  str(Defs.progress(DIVINITY, JLong(10 ** 12)))]
    Defs.setClassTable(Defs.DEFAULT_CPER, False)
    Defs.setTable(JArray(JLong)([int(x) for x in Defs.DEFAULT_PER][:50]))
    G["gen50"] = [int(Defs.maxOf(MINING)), int(Defs.maxOf(DIVINITY)), int(Defs.levelOf(DIVINITY, JLong(929090))), int(Defs.levelOf(MINING, JLong(10 ** 12))),
                  int(Defs.levelOf(DIVINITY, JLong(21540)))]
    Defs.setTable(Defs.DEFAULT_PER)
    Defs.setClassTable(Defs.DEFAULT_CPER, True)
    G["same"] = all(int(Defs.levelOf(s, JLong(x))) == int(Defs.generalLevel(JLong(x))) for s in CLASS_SLOTS for x in xs[::5]) and \
        [int(x) for x in Defs.ECUM] == [int(x) for x in Defs.CUM]
    Defs.setClassTable(Defs.DEFAULT_CPER, False)
    G["back"] = [int(x) for x in Defs.ECUM] == [int(x) for x in Defs.CCUM]
    D["G"] = G

    # ---------------------------------------------------------------- stand-ins: Universe, world, players
    uni = U.allocateInstance(Universe.class_)
    PLAYERS, WORLDS = CHM(), CHM()
    setf(uni, Universe, "playersByUuid", PLAYERS)
    setf(uni, Universe, "players", PLAYERS.values())
    setf(uni, Universe, "worldsByUuid", WORLDS)
    setf(None, Universe, "instance", uni)
    world = U.allocateInstance(FakeW.class_)
    wuid = UUID(0x3012D, 1)
    WORLDS.put(wuid, world)
    handler = U.allocateInstance(FakeH.class_)
    holder = U.allocateInstance(Holder.class_)
    TEXTS = getf(None, FakeH, "TEXTS")

    def mkpr(u, name):
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", u)
        setf(pr, PRef, "username", name)
        setf(pr, PRef, "packetHandler", handler)
        setf(pr, PRef, "worldUuid", wuid)
        setf(pr, PRef, "holder", holder)
        PLAYERS.put(u, pr)
        return pr

    def texts():
        out = [str(t) for t in TEXTS]
        TEXTS.clear()
        return out

    def fresh_store(players_dir):
        Store.DATA.clear()
        Store.DIRTY.clear()
        Store.QUIET.clear()
        Store.OWNER.clear()
        Store.PUBLISHED.clear()
        Store.DIR = path(players_dir)
        for i in range(len(Top.CACHE)):
            Top.CACHE[i] = None
            Top.AT[i] = 0

    def load_cfg(d, text=None):
        f = os.path.join(d, "xp.properties")
        if text is not None:
            os.makedirs(d, exist_ok=True)
            open(f, "wb").write(text)
        Cfg.FILE = path(f)
        return str(Cfg.load())

    def page_texts(pg):
        b, ev = UCB(), UEB()
        err = None
        try:
            pg.build(None, b, ev, None)
        except Exception as e:
            err = str(e)
        return err, [str(c.data) for c in b.getCommands() if c.data is not None]

    def has(lst, sub):
        return any(sub in x for x in lst)

    # ---------------------------------------------------------------- P: per-slot everywhere
    P = {}
    pdir = os.path.join(SCRATCH, "p-players")
    os.makedirs(pdir, exist_ok=True)
    load_cfg(os.path.join(SCRATCH, "p-cfg"), b"multiplier=1.0\n")
    uP = UUID(0x5117, 15)
    keyP = str(uP)
    open(os.path.join(pdir, keyP + ".properties"), "wb").write(
        ("name=Pria\nCombat.Priest=67425\nCombat.Priest.paid=15\nMining=67425\nMining.paid=15\nCombat.Archer=1000\nCombat.Archer.paid=4\n").encode("latin-1"))
    for k in ("u2", "u3"):
        pass
    open(os.path.join(pdir, "aaaaaaaa-0000-0000-0000-000000000001.properties"), "wb").write(b"name=Alex\nCombat.Priest=21540\nCombat.Priest.paid=20\n")
    fresh_store(pdir)
    prP = mkpr(uP, "Pria")
    bridge.put("class:" + keyP, "Priest")
    bridge.put("class:fn:allowed", Const(JBool.TRUE))
    bridge.put("coins:fn:add", Coins())
    P["level"] = [int(Store.level(uP, DIVINITY)), int(Store.level(uP, MINING)), int(Store.level(uP, ARCHERY))]
    sf, xf = SkillFn(), XpFn()
    P["fn_level"] = dict((n, int(sf.apply(JObj[:]([uP, n])))) for n in ("Divinity", "Priest", "Combat", "Mining", "Archery", "div"))
    P["fn_level"]["Overall"] = int(sf.apply(JObj[:]([uP, "Overall"])))
    P["fn_xp"] = [int(xf.apply(JObj[:]([uP, "Divinity"]))), int(xf.apply(JObj[:]([uP, "Mining"])))]
    P["levels"] = str(Store.levelsString(uP))
    ov = OvFn().apply(uP)
    P["overall"] = [int(ov[0]), int(ov[1]), int(ov[2])]
    P["ovmax"] = int(Ovl.maxLevel(uP))
    err, cmds = page_texts(SkillsPage(prP))
    P["skills_page"] = [err, has(cmds, "Divinity  28"), has(cmds, "Mining  15"), has(cmds, "XP to level 29"), has(cmds, "XP to level 16"),
                        has(cmds, "Overall Level ")]
    err, cmds = page_texts(StatsPage(prP, DIVINITY))
    P["stats_page"] = [err, has(cmds, "Divinity - level 28 of 100"), has(cmds, "XP to level 29")]
    err, cmds = page_texts(StatsPage(prP, MINING))
    P["stats_mining"] = [err, has(cmds, "Mining - level 15 of 100"), has(cmds, "XP to level 16")]
    sp = SkillsPage(prP)
    sp.view = DIVINITY
    err, cmds = page_texts(sp)
    P["top_page"] = [err, has(cmds, "Level 28"), has(cmds, "Level 20"), has(cmds, "Your rank #1 of 2 - level 28")]
    err, cmds = page_texts(OverallPage(prP))
    P["overall_page"] = [err, has(cmds, "Level %d of %d" % (P["overall"][0], P["ovmax"])), has(cmds, "Divinity 28 (your class)")]
    texts()
    Msg.PEND.clear()
    Msg.LAST.clear()
    Msg.note(prP, DIVINITY, 100)                      # the first note is due: sent at once
    P["msg"] = texts()
    Msg.note(prP, MINING, 1)                          # inside feedbackMs: pending, read back with take()
    P["msg_take"] = str(Msg.take(uP))
    Px.drop(uP)
    Px.add(uP, DIVINITY, 6, "Skyy")
    P["party"] = str(Px.take(uP))
    # a real level up on the class table: Alex 21,540 Divinity XP = 20 already; Pria to exactly 21,540 from 21,539
    Store.DATA.get(keyP)[DIVINITY] = 21539
    Store.DATA.get(keyP)[16 + DIVINITY] = 19
    COINS[:] = []
    texts()
    Xp.gain3(prP, DIVINITY, 1, False, False)
    P["levelup"] = {"texts": texts(), "coins": list(COINS), "paid": int(Store.DATA.get(keyP)[16 + DIVINITY]), "level": int(Store.level(uP, DIVINITY))}
    Store.DATA.get(keyP)[MINING] = 9924
    Store.DATA.get(keyP)[16 + MINING] = 9
    COINS[:] = []
    Xp.gain3(prP, MINING, 1, False, False)
    P["levelup_mining"] = {"texts": texts(), "coins": list(COINS)}
    D["P"] = P

    # ---------------------------------------------------------------- M: ClassCurve on scratch copies
    def snap(d):
        return dict((os.path.relpath(os.path.join(r, fn), d).replace(os.sep, "/"), open(os.path.join(r, fn), "rb").read())
                    for r, ds, fs in os.walk(d) for fn in fs)

    def start(d):
        """the plugin's setup order: ManaMig.run -> HealMig.run -> SkillCfg.load -> ClassCurve.start (+ the kit's history init)"""
        Cfg.FILE = path(os.path.join(d, "xp.properties"))
        fresh_store(os.path.join(d, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        mr = [str(x) for x in Mig.run()]
        hr = str(HMig.run())
        lt = str(Cfg.load())
        cr = str(Curve.start(path(d)))
        return {"mana": mr, "heal": hr, "load": lt, "curve": cr, "ready": bool(Curve.READY), "pending": dict((str(k), str(v)) for k, v in Curve.PENDING.items()),
                "done": dict((str(k), str(v)) for k, v in Curve.DONE.items())}

    M = {}
    bridge.remove("class:fn:allowed")
    lc = os.path.join(SCRATCH, "live-copy")
    s0 = snap(lc)
    r1 = start(lc)
    s1 = snap(lc)
    r2 = start(lc)
    s2 = snap(lc)
    M["live"] = {"r1": r1, "r2": r2, "changed1": sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k)),
                 "changed2": sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k)),
                 "players_same": all(s0[k] == s2.get(k) for k in s0 if k.startswith("players/")),
                 "xp_append": s1["xp.properties"] == s0["xp.properties"] + b"\n" + D["curve_block"].encode("latin-1") + b"\n" + D["mreg_block"].encode("latin-1"),
                 "record": s1.get("class-curve.properties", b"").decode("latin-1"), "n_players": len([k for k in s0 if k.startswith("players/")])}
    # (2) an edited copy: three risen profiles of one player (u2 profile 1 Priest 67,425 = 15 -> 28; profile 2 Archer 522,425 = 20 -> 51,
    # profile 3 Archer 1,000 = 4 -> 5 = the crossbow unlock level) + Skyy's real files
    ed = os.path.join(SCRATCH, "mig-edit")
    shutil.copytree(lc, ed)
    os.remove(os.path.join(ed, "class-curve.properties"))
    u2 = UUID(0xABC, 2)
    k1, k2, k3 = str(u2), str(u2) + "-p2", str(u2) + "-p3"
    open(os.path.join(ed, "players", k1 + ".properties"), "wb").write(b"name=Tester\nCombat.Priest=67425\nCombat.Priest.paid=15\nMining=67425\nMining.paid=15\n")
    open(os.path.join(ed, "players", k2 + ".properties"), "wb").write(b"name=Tester\nCombat.Archer=522425\nCombat.Archer.paid=20\n")
    open(os.path.join(ed, "players", k3 + ".properties"), "wb").write(b"name=Tester\nCombat.Archer=1000\nCombat.Archer.paid=4\n")
    pr2 = mkpr(u2, "Tester")
    bridge.put("profile:fn:key", PKey())
    bridge.put("class:fn:allowed", Const(JBool.TRUE))
    bridge.put("class:" + k1, "Priest")
    ACTIVE[k1] = k1
    e1 = start(ed)
    rec1 = open(os.path.join(ed, "class-curve.properties"), "rb").read().decode("latin-1")
    COINS[:] = []
    texts()
    Curve.tick(pr2, u2)
    t1 = texts()
    c1 = list(COINS)
    paid1 = int(Store.dataK(k1, u2)[16 + DIVINITY])
    disk_before = open(os.path.join(ed, "players", k1 + ".properties"), "rb").read().decode("latin-1")
    Curve.flush()
    disk_after = open(os.path.join(ed, "players", k1 + ".properties"), "rb").read().decode("latin-1")
    rec2 = open(os.path.join(ed, "class-curve.properties"), "rb").read().decode("latin-1")
    COINS[:] = []
    Curve.tick(pr2, u2)
    t2 = texts()
    c2 = list(COINS)
    Xp.gain3(pr2, DIVINITY, 5, False, False)          # a later small award: no level crossed, nothing more paid
    t3 = texts()
    c3 = list(COINS)
    M["edit1"] = {"start": e1, "rec1": rec1, "t1": t1, "c1": c1, "paid1": paid1, "disk_paid_before": "Combat.Priest.paid=28" in disk_before,
                  "disk_paid_after": "Combat.Priest.paid=28" in disk_after, "rec2": rec2, "t2": t2, "c2": c2, "t3": t3, "c3": c3}
    # restart (fresh statics from the file): k1 done; k2 / k3 still pending; k2 becomes active
    e2 = start(ed)
    ACTIVE[str(u2)] = k2
    bridge.put("class:" + str(u2), "Archer")
    COINS[:] = []
    texts()
    Curve.tick(pr2, u2)
    t4 = texts()
    c4 = list(COINS)
    Curve.flush()
    ACTIVE[str(u2)] = k3
    COINS[:] = []
    Curve.tick(pr2, u2)
    t5 = texts()
    c5 = list(COINS)
    Curve.flush()
    e3 = start(ed)
    ACTIVE[str(u2)] = k1
    bridge.put("class:" + str(u2), "Priest")
    COINS[:] = []
    for _ in range(3):
        Curve.tick(pr2, u2)
    t6 = texts()
    c6 = list(COINS)
    sE = snap(ed)
    M["edit2"] = {"start2": e2, "t4": t4, "c4": c4, "t5": t5, "c5": c5, "start3": e3, "t6": t6, "c6": c6,
                  "rec3": sE.get("class-curve.properties", b"").decode("latin-1"),
                  "disk": dict((k, sE["players/" + k + ".properties"].decode("latin-1")) for k in (k1, k2, k3))}
    # (3) profile:busy waits, then delivers
    bz = os.path.join(SCRATCH, "mig-busy")
    shutil.copytree(lc, bz)
    os.remove(os.path.join(bz, "class-curve.properties"))
    u3 = UUID(0xABC, 3)
    open(os.path.join(bz, "players", str(u3) + ".properties"), "wb").write(b"name=Busy\nCombat.Priest=67425\nCombat.Priest.paid=15\n")
    pr3 = mkpr(u3, "Busy")
    bridge.put("class:" + str(u3), "Priest")
    start(bz)
    bridge.put("profile:busy:" + str(u3), JBool.TRUE)
    texts()
    Curve.tick(pr3, u3)
    b1 = [texts(), str(u3) in [str(k) for k in Curve.PENDING.keySet()]]
    bridge.remove("profile:busy:" + str(u3))
    Curve.tick(pr3, u3)
    b2 = [texts(), str(u3) in [str(k) for k in Curve.PENDING.keySet()]]
    M["busy"] = {"while": b1, "after": b2}
    # (4) the record cannot be written (a FOLDER named class-curve.properties): nobody told, the next start scans again
    nw = os.path.join(SCRATCH, "mig-nowrite")
    shutil.copytree(lc, nw)
    os.remove(os.path.join(nw, "class-curve.properties"))
    open(os.path.join(nw, "players", str(u3) + ".properties"), "wb").write(b"name=Busy\nCombat.Priest=67425\nCombat.Priest.paid=15\n")
    os.makedirs(os.path.join(nw, "class-curve.properties.tmp", "x"))
    w1 = start(nw)
    texts()
    Curve.tick(pr3, u3)
    w_t = texts()
    w_rec = os.path.exists(os.path.join(nw, "class-curve.properties"))
    shutil.rmtree(os.path.join(nw, "class-curve.properties.tmp"))
    w2 = start(nw)
    M["nowrite"] = {"w1": w1, "t": w_t, "w2": w2, "rec": w_rec}
    # (5) SkyyCoins missing: the line once, the coins stay owed (paid marker unchanged) for the normal late payout
    nc = os.path.join(SCRATCH, "mig-nocoins")
    shutil.copytree(lc, nc)
    os.remove(os.path.join(nc, "class-curve.properties"))
    open(os.path.join(nc, "players", str(u3) + ".properties"), "wb").write(b"name=Busy\nCombat.Priest=67425\nCombat.Priest.paid=15\n")
    start(nc)
    bridge.remove("coins:fn:add")
    texts()
    Curve.tick(pr3, u3)
    n_t1 = texts()
    n_paid = int(Store.dataK(str(u3), u3)[16 + DIVINITY])
    bridge.put("coins:fn:add", Coins())
    COINS[:] = []
    Curve.tick(pr3, u3)
    n_t2 = texts()
    Xp.gain3(pr3, DIVINITY, 1, False, False)
    n_t3 = texts()
    M["nocoins"] = {"t1": n_t1, "paid": n_paid, "t2": n_t2, "t3": n_t3, "coins": list(COINS), "paid_after": int(Store.dataK(str(u3), u3)[16 + DIVINITY])}
    D["M"] = M

    # ---------------------------------------------------------------- R: Mana regen maths
    R = {}

    def amt(r, pct, f, secs, cur, mx):
        return round(float(Mana.amount(JArray(JFloat)(r), pct, f, JFloat(secs), JFloat(cur), JFloat(mx))), 5)
    R["amount"] = {
        "out0": amt([5, 5, 0], 0.0, 50, 1.0, 10, 30), "out20": amt([5, 5, 0], 20.0, 50, 1.0, 10, 30), "out20_pulse": amt([5, 5, 0], 20.0, 50, 0.2, 10, 30),
        "in0": amt([5, 0, 5], 0.0, 50, 1.0, 10, 30), "in0_pulse": amt([5, 0, 5], 0.0, 50, 0.2, 10, 30), "in20": amt([5, 0, 5], 20.0, 50, 1.0, 10, 30),
        "in_f0": amt([5, 0, 5], 20.0, 0, 1.0, 10, 30), "out_f0": amt([5, 5, 0], 20.0, 0, 1.0, 10, 30), "in_f100": amt([5, 0, 5], 0.0, 100, 1.0, 10, 30),
        "cap": amt([5, 0, 5], 0.0, 100, 1.0, 29.9, 30), "full": amt([5, 0, 5], 0.0, 50, 1.0, 30, 30), "nomana": amt([5, 0, 5], 50.0, 50, 1.0, 0, 0),
        "charging": amt([5, 0, 0], 50.0, 50, 1.0, 10, 30), "neg": amt([5, 5, 0], -40.0, 50, 1.0, 10, 30), "neg_in": amt([5, 0, 5], -40.0, 50, 1.0, 10, 30),
        "big": amt([5, 5, 0], 5000.0, 50, 1.0, 0, 10000), "nan": amt([5, 5, 0], float("nan"), 50, 1.0, 10, 30), "f150": amt([5, 0, 5], 0.0, 150, 1.0, 10, 30),
        "secs0": amt([5, 0, 5], 0.0, 50, 0.0, 10, 30)}
    tot = 0.0
    for _ in range(30):                                            # 6 s in combat in vanilla's 0.2 s pulses at 50%: 15 Mana
        tot += float(Mana.amount(JArray(JFloat)([5, 0, 5]), 0.0, 50, JFloat(0.2), JFloat(0.0 + tot), JFloat(100.0)))
    R["six_seconds"] = round(tot, 4)
    # the real engine conditions: EntityModule / DamageModule stand-ins so DamageDataComponent / DeathComponent component types resolve
    EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    DM = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageModule")
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    em, dm = U.allocateInstance(EM.class_), U.allocateInstance(DM.class_)
    ddType, deathType = U.allocateInstance(CT.class_), U.allocateInstance(CT.class_)
    R["stubs"] = []
    for cls, inst, want in ((EM, em, ("damageDataComponentType", ddType)), (DM, dm, ("deathComponentType", deathType))):
        sf_ = [f for f in cls.class_.getDeclaredFields() if JClass("java.lang.reflect.Modifier").isStatic(f.getModifiers()) and f.getType() == cls.class_]
        R["stubs"].append(len(sf_))
        for f in sf_:
            f.setAccessible(True)
            f.set(None, inst)
        setf(inst, cls, want[0], want[1])
    Arch = JClass("com.hypixel.hytale.component.Archetype")
    DDC = JClass("com.hypixel.hytale.server.core.entity.damage.DamageDataComponent")
    NDT = JClass("com.hypixel.hytale.server.core.modules.entity.condition.NoDamageTakenCondition")
    Alive = JClass("com.hypixel.hytale.server.core.modules.entity.condition.AliveCondition")
    RGN = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType$Regenerating")
    RGT = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType$Regenerating$RegenType")
    RGV = JClass("com.hypixel.hytale.server.core.modules.entitystats.RegeneratingValue")
    Cond = JClass("com.hypixel.hytale.server.core.modules.entity.condition.Condition")
    Instant, Duration = JClass("java.time.Instant"), JClass("java.time.Duration")
    nctor = NDT.class_.getDeclaredConstructor()
    nctor.setAccessible(True)
    nodmg = nctor.newInstance()
    setf(nodmg, NDT, "delay", Duration.ofSeconds(6))
    charging = Fixed(False)                                        # vanilla's Charging (inverse): passes while NOT charging

    def entry(amount, interval, rtype, conds):
        rg = RGN()
        setf(rg, RGN, "amount", JFloat(amount))
        setf(rg, RGN, "interval", JFloat(interval))
        setf(rg, RGN, "regenType", rtype)
        setf(rg, RGN, "conditions", None if conds is None else JArray(Cond)(conds))
        return RGV(rg)
    vanilla = entry(1.0, 0.2, RGT.ADDITIVE, [Alive(False), nodmg, charging])
    now = Instant.parse("2026-10-02T12:00:00Z")
    acc = FakeAcc()
    dd = DDC()
    acc.dd = dd
    acc.arch = Arch.empty()

    def rates(entries, hit_ago_ms, charge_ok=True, dead=False):
        dd.setLastDamageTime(now.minusMillis(hit_ago_ms))
        charging.v = charge_ok
        acc.arch = Arch.of(deathType) if dead else Arch.empty()
        try:
            return [round(float(x), 4) for x in Mana.rates(acc, None, now, JArray(RGV)(entries))]
        except Exception as e:
            return "error: %s" % e
    R["rates"] = {"out": rates([vanilla], 10000), "in": rates([vanilla], 2000), "edge6": rates([vanilla], 6000), "edge5999": rates([vanilla], 5999),
                  "in_charging": rates([vanilla], 2000, charge_ok=False), "out_charging": rates([vanilla], 10000, charge_ok=False),
                  "dead": rates([vanilla], 10000, dead=True), "dead_in": rates([vanilla], 2000, dead=True),
                  "pct_entry": rates([vanilla, entry(1.0, 0.5, RGT.PERCENTAGE, [])], 10000),
                  "zero_entry": rates([vanilla, entry(0.0, 0.2, RGT.ADDITIVE, [])], 10000),
                  "no_conds": rates([entry(2.0, 1.0, RGT.ADDITIVE, None)], 2000),
                  "two": rates([vanilla, entry(1.0, 1.0, RGT.ADDITIVE, [nodmg])], 2000)}

    def state(hit_ago_ms, charge_ok=True):
        dd.setLastDamageTime(now.minusMillis(hit_ago_ms))
        charging.v = charge_ok
        acc.arch = Arch.empty()
        return int(Mana.state(acc, None, now, vanilla.getRegenerating()))
    R["rates"]["state"] = [state(10000), state(2000), state(2000, False), state(10000, False)]
    # mana.regen.inCombat in the loader
    R["cfg"] = {}
    for name, line, in (("default", None), ("150", b"mana.regen.inCombat=150\n"), ("neg", b"mana.regen.inCombat=-5\n"),
                        ("abc", b"mana.regen.inCombat=abc\n"), ("zero", b"mana.regen.inCombat=0\n"), ("25", b"mana.regen.inCombat=25\n")):
        dd_ = os.path.join(SCRATCH, "r-cfg-" + name)
        load_cfg(dd_, b"multiplier=1.0\n" + (line or b""))
        R["cfg"][name] = int(Mana.IN_COMBAT)
    D["R"] = R

    # ---------------------------------------------------------------- B: skill:fn:manaregen
    Bq = {}
    fn = ManaFn()
    ub = UUID(0x8888, 1)
    Mana.SRC.clear()

    def call(*a):
        r = fn.apply(JObj[:](list(a)))
        if r is None:
            return None
        cn = str(r.getClass().getName())
        if cn == "java.lang.Double":
            return float(r.doubleValue())
        if cn == "java.lang.Integer":
            return int(r.intValue())
        if cn == "java.lang.Boolean":
            return "true" if r.booleanValue() else "false"
        if cn == "[Ljava.lang.String;":
            return [str(x) for x in r]
        return "?" + cn
    Bq["seq"] = [call("get", ub), call("add", ub, "SkyyGear", JDouble(15.0)), call("add", ub, "SkyyAccessories", JInt(5)), call("get", ub),
                 call("sources", ub), call("add", ub, "SkyyGear", JDouble(20.0)), call("get", ub), call("remove", ub, "SkyyGear"), call("get", ub),
                 call("remove", ub, "SkyyGear"), call("add", ub, "Arcane", JDouble(-30.0)), call("get", ub), call("add", ub, "Arcane", JDouble(0.0)),
                 call("sources", ub)]
    Bq["bad"] = [call("add", ub, "", JDouble(5.0)), call("add", ub, "x" * 65, JDouble(5.0)), call("add", ub, "nan", JDouble(float("nan"))),
                 call("add", "not-a-uuid", "src", JDouble(5.0)), call("add", ub, "src"), call("remove", ub), call("get", "nope"), call("frob", ub),
                 fn.apply("not an array") is None, call("sources", None)]
    Mana.SRC.clear()
    call("add", ub, "Big", JDouble(5000.0))
    Bq["clamp"] = [call("get", ub), call("sources", ub)]
    u4 = UUID(0x8888, 2)
    call("add", u4, "Big", JDouble(10.0))
    Bq["clear"] = [call("clear", "Big"), call("get", ub), call("get", u4), call("clear", JInt(3))]
    Mana.SRC.clear()
    call("add", ub, "SkyyGear", JDouble(20.0))
    Mana.IN_COMBAT = 50
    Bq["action"] = [str(x) for x in Mana.showAction(ub, "Skyy")]
    Bq["action_null"] = [str(x) for x in Mana.showAction(None, "console")]
    Bq["types"] = [str(fn.apply(JObj[:](["get", ub])).getClass().getName()), str(fn.apply(JObj[:](["add", ub, "a", JDouble(1.0)])).getClass().getName()),
                   str(fn.apply(JObj[:](["clear", "a"])).getClass().getName()), str(fn.apply(JObj[:](["sources", ub])).getClass().getName())]
    Bq["total_feeds"] = round(float(Mana.amount(JArray(JFloat)([5, 0, 5]), Mana.total(ub), 50, JFloat(1.0), JFloat(0.0), JFloat(30.0))), 4)
    Mana.SRC.clear()
    D["B"] = Bq

    # ---------------------------------------------------------------- C: the loader (blocks appended once, LF / CRLF, an admin's switch)
    C = {}
    cb_, mb_ = D["curve_block"].encode("latin-1"), D["mreg_block"].encode("latin-1")
    full = D["defaults"].encode("latin-1")
    base_old = full[:full.index(b"\n# ---------- Class skill levels (SkyySkills 0.4.12)") + 1]   # every pre-0.4.12 block, no 0.4.12 key
    assert b"levels.class=" not in base_old and b"levels.class.same" not in base_old and b"mana.regen" not in base_old
    cdir = os.path.join(SCRATCH, "c-lf")
    load_cfg(cdir, base_old)
    c1_ = open(os.path.join(cdir, "xp.properties"), "rb").read()
    load_cfg(cdir)
    c2_ = open(os.path.join(cdir, "xp.properties"), "rb").read()
    C["lf"] = {"exact": c1_ == base_old + b"\n" + cb_ + b"\n" + mb_, "again_same": c1_ == c2_, "no_cr": b"\r" not in c1_}
    cdir = os.path.join(SCRATCH, "c-crlf")
    load_cfg(cdir, base_old.replace(b"\n", b"\r\n"))
    c3_ = open(os.path.join(cdir, "xp.properties"), "rb").read()
    C["crlf"] = {"exact": c3_ == (base_old + b"\n" + cb_ + b"\n" + mb_).replace(b"\n", b"\r\n"), "all_crlf": c3_.count(b"\r\n") == c3_.count(b"\n")}
    cdir = os.path.join(SCRATCH, "c-admin")
    load_cfg(cdir, b"multiplier=1.0\nlevels.class.sameAsOthers=true\n")
    c4_ = open(os.path.join(cdir, "xp.properties"), "rb").read()
    load_cfg(cdir)
    C["admin"] = {"same_kept": c4_.count(b"levels.class.sameAsOthers=") == 1 and b"levels.class.sameAsOthers=true" in c4_,
                  "list_added": c4_.count(b"\nlevels.class=") == 1, "SAME": bool(Defs.SAME),
                  "class_eq_general": int(Defs.levelOf(DIVINITY, JLong(67425))) == int(Defs.generalLevel(JLong(67425)))}
    cdir = os.path.join(SCRATCH, "c-noeol")
    base_noeol = base_old.rstrip(b"\n")
    load_cfg(cdir, base_noeol)
    c5_ = open(os.path.join(cdir, "xp.properties"), "rb").read()
    C["noeol"] = c5_ == base_noeol + b"\n\n" + cb_ + b"\n" + mb_
    cdir = os.path.join(SCRATCH, "c-short")
    txt = load_cfg(cdir, b"multiplier=1.0\nlevels.class=10,20,30\nlevels.class.sameAsOthers=false\nmana.regen.inCombat=50\n")
    C["short"] = [int(Defs.CMAX), int(Defs.maxOf(DIVINITY)), int(Defs.levelOf(DIVINITY, JLong(60))), int(Defs.levelOf(DIVINITY, JLong(59))), "max level 3" in txt,
                  open(os.path.join(cdir, "xp.properties"), "rb").read().count(b"levels.class=") == 1]
    cdir = os.path.join(SCRATCH, "c-bad")
    txt = load_cfg(cdir, b"multiplier=1.0\nlevels.class=10,abc\nlevels.class.sameAsOthers=false\nmana.regen.inCombat=50\n")
    C["bad"] = [int(Defs.CMAX), [int(x) for x in Defs.CPER] == T["cper"], "1 bad line(s) skipped" in txt]
    f = os.path.join(SCRATCH, "c-fresh")
    load_cfg(f)
    C["fresh_text"] = str(Cfg.load())
    C["fresh"] = [int(Defs.CMAX), bool(Defs.SAME), int(Mana.IN_COMBAT), [int(x) for x in Defs.CPER] == T["cper"]]
    D["C"] = C

    # ---------------------------------------------------------------- K: the kit rows + the class curve custom rows
    K = {}
    K["get"] = [str(Kit.customGet("levels.class.max")), str(Kit.customGet("levels.class.scale")), str(Kit.customGet("levels.max")), str(Kit.customGet("levels.scale"))]
    r60 = Kit.customSet("levels.class.max", "60")
    K["cut60"] = [str(r60[0]), str(r60[1]), str(r60[2]), [str(x) for x in r60[3]][0], len(str(r60[3][1]).split(",")), int(Defs.CMAX), int(Defs.maxOf(DIVINITY)), int(Defs.MAX)]
    # the kit would write the line; emulate it for curListC (the kit's get) by setting CPER directly through the returned list
    r100 = Kit.customSet("levels.class.max", "100")
    K["raise100"] = [str(r100[0]), str(r100[1]), str(r100[2]), str(r100[3][1]) == ",".join(str(x) for x in T["cper"]), int(Defs.CMAX)]
    r110 = Kit.customSet("levels.class.scale", "110")
    K["scale110"] = [str(r110[0]), str(r110[1]), int(Defs.CPER[0]), str(r110[2])]
    rb = Kit.customSet("levels.class.scale", "100")
    K["scale100"] = [str(rb[0]), str(rb[1]), [int(x) for x in Defs.CPER] == T["cper"]]
    K["bad"] = [str(Kit.customSet("levels.class.max", "0")[0]), str(Kit.customSet("levels.class.max", "101")[0]), str(Kit.customSet("levels.class.scale", "5")[0]),
                str(Kit.customSet("levels.class.max", "x")[0])]
    rg = Kit.customSet("levels.max", "50")
    K["general50"] = [str(rg[0]), str(rg[3][0]), int(Defs.MAX), int(Defs.CMAX), int(Defs.maxOf(DIVINITY))]
    Kit.customSet("levels.max", "100")
    HM = JClass("java.util.HashMap")
    vals = HM()
    vals.put("levels.class", "10,20,30,40")
    vals.put("levels", "50,125")
    K["read"] = [str(Kit.customRead("levels.class.max", vals)), str(Kit.customRead("levels.class.scale", vals)), str(Kit.customRead("levels.max", vals)),
                 str(Kit.customRead("levels.class.max", None)), str(Kit.customRead("levels.class.scale", None))]
    K["check"] = [Kit.checkLevels("levels.class", "1,2,3") is None, Kit.checkLevels("levels.class", "0,5") is not None,
                  Kit.checkLevels("levels.class", ",".join(["5"] * 101)) is not None]
    Defs.setTable(Defs.DEFAULT_PER)
    Defs.setClassTable(Defs.DEFAULT_CPER, False)
    D["K"] = K

    # ---------------------------------------------------------------- X: the review fixes
    from jpype import JInt as PInt
    X = {}
    JStrA = JArray(JClass("java.lang.String"))
    OvCfg = JClass(PKG + "OverallCfg")
    slots0, cls0 = OvCfg.SLOTS, bool(OvCfg.CLASS)

    def page_all(pg):
        """page_texts + the appended markup (CustomUICommand.text: the static labels such as 'Max Overall Level reached')"""
        b, ev = UCB(), UEB()
        err = None
        try:
            pg.build(None, b, ev, None)
        except Exception as e:
            err = str(e)
        return err, [str(c.data) for c in b.getCommands() if c.data is not None] + [str(c.text) for c in b.getCommands() if c.text is not None]
    # R1: no counted skill (Overall.maxLevel 0) -> never the max layout; a maxed player still gets it
    Store.DATA.remove(keyP)
    OvCfg.SLOTS = JArray(PInt)([])
    OvCfg.CLASS = False
    err, cmds = page_all(OverallPage(prP))
    X["ov_none"] = {"err": err, "max": int(Ovl.maxLevel(uP)), "next": [str(x) for x in Ovl.nextLines(0, 0)],
                    "title": has(cmds, "Level 0 of 0"), "sub": has(cmds, "No skill counts toward the Overall Level on this server"),
                    "line": has(cmds, "Nothing - no skill counts toward the Overall Level"), "maxlay": has(cmds, "Max Overall Level reached"),
                    "the_highest": has(cmds, "the highest Overall Level")}
    OvCfg.SLOTS = JArray(PInt)([MINING])
    dmax = JArray(JLong)(32)
    dmax[MINING] = 10 ** 12
    dmax[16 + MINING] = 100
    Store.DATA.put(keyP, dmax)
    err, cmds = page_all(OverallPage(prP))
    X["ov_max"] = {"err": err, "max": int(Ovl.maxLevel(uP)), "title": has(cmds, "Level 100 of 100"), "maxlay": has(cmds, "Max Overall Level reached"),
                   "the_highest": has(cmds, "the highest Overall Level"), "next": [str(x) for x in Ovl.nextLines(100, 100)]}
    dmax[MINING] = 67425
    err, cmds = page_all(OverallPage(prP))
    X["ov_mid"] = {"err": err, "title": has(cmds, "Level 15 of 100"), "maxlay": has(cmds, "Max Overall Level reached"), "next_hd": has(cmds, "Overall Level 16 adds"),
                   "next": [str(x) for x in Ovl.nextLines(15, 100)]}
    OvCfg.SLOTS = slots0
    OvCfg.CLASS = cls0
    Store.DATA.remove(keyP)
    # R4: the compact Server Setup answer (pure), the action, the full /skills mana text
    try:                                                           # (a jar without ManaRegen.compact still runs on: those checks fail)
        X["compact"] = [str(Mana.compact(0.0, JStrA([]), JFloat(5.0), 50)), str(Mana.compact(20.0, JStrA(["SkyyGear=+20"]), JFloat(5.0), 50)),
                        str(Mana.compact(20.0, JStrA(["SkyyGear=+20"]), JFloat(5.0), 0)), str(Mana.compact(0.0, JStrA([]), JFloat(0.0), 50)),
                        str(Mana.compact(0.0, JStrA([]), JFloat(0.0), 0)), str(Mana.compact(0.0, None, JFloat(5.0), 100))]
        many = ["Source%02d=+%d" % (i, i) for i in range(12)]
        X["compact_many"] = str(Mana.compact(1000.0, JStrA(many), JFloat(5.0), 100))
        X["compact_long"] = str(Mana.compact(5.0, JStrA(["x" * 64 + "=+5"]), JFloat(5.0), 50))
        X["compact_odd"] = str(Mana.compact(333.333, JStrA(many), JFloat(3.3333), 55))
        X["compact_two"] = str(Mana.compact(45.0, JStrA(["SkyyAccessories=+25", "SkyyGear=+20"]), JFloat(5.0), 50))
        rnd = random.Random(4124)
        worst = 0
        for _ in range(400):
            k = rnd.randint(1, 99)
            src_ = ["".join(rnd.choice("abcXYZ") for _ in range(rnd.randint(1, 64))) + "=+" + str(rnd.randint(-1000, 1000)) for _ in range(k)]
            p_ = round(rnd.uniform(0, 1000), 3) if rnd.random() < 0.7 else rnd.choice([0.0, 1000.0, 999.999])
            worst = max(worst, len(str(Mana.compact(p_, JStrA(src_), JFloat(rnd.choice([5.0, 3.3333, 0.0, 7.777, 100.0])), rnd.randint(0, 100)))))
        X["compact_worst"] = worst
    except Exception as e:
        X.update({"compact": "error: %s" % e, "compact_many": "", "compact_long": "", "compact_odd": "", "compact_two": "", "compact_worst": 999})
    Mana.SRC.clear()
    for i in range(12):
        Mana.put(ub, "Source%02d" % i, float(i + 1))
    Mana.put(ub, "SkyyGear", 20.0)
    Mana.IN_COMBAT = 50
    X["vanilla_rate"] = float(Mana.vanillaRate())
    X["action"] = [str(x) for x in Mana.showAction(ub, "Skyy")]
    X["action_null"] = [str(x) for x in Mana.showAction(None, "console")]
    Mana.SRC.clear()
    Mana.put(ub, "SkyyGear", 20.0)
    X["action1"] = str(Mana.showAction(ub, "Skyy")[2])
    X["text1"] = str(Mana.text(ub))
    Mana.SRC.clear()
    # R5: the class curve size message = the EFFECTIVE class totals after the change
    Defs.setTable(Defs.DEFAULT_PER)
    Defs.setClassTable(Defs.DEFAULT_CPER, False)

    def eff(top):
        e = [int(x) for x in Defs.ECUM]
        return [str(Defs.fmt(JLong(e[i]))) for i in (1, 20, top) if i < len(e)]
    r = Kit.customSet("levels.class.scale", "150")
    X["scale150"] = {"r": [str(r[0]), str(r[1]), str(r[2])], "eff": eff(100), "ecum1": int(Defs.ECUM[1]), "ccum1": int(Defs.CCUM[1])}
    r = Kit.customSet("levels.class.scale", "100")
    X["scale100"] = {"r": [str(r[0]), str(r[1]), str(r[2])], "eff": eff(100), "same_list": [int(x) for x in Defs.CPER] == T["cper"]}
    Kit.customSet("levels.class.max", "10")
    r = Kit.customSet("levels.class.scale", "100")
    X["scale_max10"] = [str(r[0]), str(r[2])]
    Defs.setClassTable(Defs.DEFAULT_CPER, True)
    r = Kit.customSet("levels.class.scale", "120")
    X["scale_same"] = [str(r[0]), str(r[2]), bool(Defs.SAME)]
    Defs.setTable(Defs.DEFAULT_PER)
    Defs.setClassTable(Defs.DEFAULT_CPER, False)
    # R9: a live curve change forgets who is published; the next publishOnline republishes skill:<uuid>
    Store.PUBLISHED.clear()
    Store.PUBLISHED.put(uP, JBool.TRUE)
    Kit.customSet("levels.class.max", "60")
    X["pub_custom"] = bool(Store.PUBLISHED.isEmpty())
    Defs.setClassTable(Defs.DEFAULT_CPER, False)
    Store.PUBLISHED.put(uP, JBool.TRUE)
    Kit.reload()
    X["pub_reload"] = bool(Store.PUBLISHED.isEmpty())
    Defs.setTable(Defs.DEFAULT_PER)
    Defs.setClassTable(Defs.DEFAULT_CPER, False)
    dpub = JArray(JLong)(32)
    dpub[DIVINITY] = 67425
    dpub[16 + DIVINITY] = 28
    Store.DATA.put(keyP, dpub)
    bridge.put("class:" + keyP, "Priest")
    Store.PUBLISHED.clear()
    Store.publish(uP)
    e2e = [str(bridge.get("skill:" + keyP)), bool(Store.PUBLISHED.containsKey(uP))]
    Kit.customSet("levels.class.max", "20")
    e2e += [str(bridge.get("skill:" + keyP)), bool(Store.PUBLISHED.containsKey(uP)), int(Store.level(uP, DIVINITY))]
    Store.publishOnline()
    e2e += [str(bridge.get("skill:" + keyP)), bool(Store.PUBLISHED.containsKey(uP))]
    X["pub_e2e"] = e2e
    Store.DATA.remove(keyP)
    Defs.setTable(Defs.DEFAULT_PER)
    Defs.setClassTable(Defs.DEFAULT_CPER, False)
    D["X"] = X
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
                ln = str(IP.instructionString(it, it.next(), cpool)).replace(chr(13), "<CR>").replace(chr(10), "<LF>")
                ln = re.sub(r"#\d+ = ", "", ln).replace("ldc_w ", "ldc ")
                ln = re.sub(r"^(if\w*|goto|goto_w|jsr)\s+\d+", r"\1 N", ln)
                lines.append(ln)
            ms[k] = "\n".join(lines)
        fields = sorted("%s %s" % (f.getName(), f.getSignature()) for f in list(cc.getDeclaredFields()))
        return ms, fields

    zo, zn = zipfile.ZipFile(old), zipfile.ZipFile(new)
    res = {"diff": {}, "only_old": sorted(set(zo.namelist()) - set(zn.namelist())), "only_new": sorted(set(zn.namelist()) - set(zo.namelist())),
           "same": sorted(n for n in set(zo.namelist()) & set(zn.namelist()) if n.endswith(".class") and zo.read(n) == zn.read(n)), "calls": {}}
    for n in sorted(set(zo.namelist()) & set(zn.namelist())):
        if not n.endswith(".class") or zo.read(n) == zn.read(n):
            continue
        mo, fo = listing(ClassPool(False), zo.read(n))
        mn, fn = listing(ClassPool(False), zn.read(n))
        changed = sorted(k for k in set(mo) & set(mn) if mo[k] != mn[k])
        res["diff"][n] = {"changed": changed, "gone": sorted(set(mo) - set(mn)), "new": sorted(set(mn) - set(mo)),
                          "fields_gone": sorted(set(fo) - set(fn)), "fields_new": sorted(set(fn) - set(fo)),
                          "vo": [k for k in changed if version_only(mo[k], mn[k])]}
    # every SkillDefs level call in the new jar names its slot: no call to a (J)I / (J)J / (J)String lookup survives anywhere
    bad = []
    for n in zn.namelist():
        if not n.endswith(".class"):
            continue
        ms, _ = listing(ClassPool(False), zn.read(n))
        for k, v in ms.items():
            for ln in v.split("\n"):
                if "SkillDefs." in ln and re.search(r"SkillDefs\.(levelOf|intoLevel|needFor|progress)\(\(J\)", ln):
                    bad.append("%s %s: %s" % (n, k, ln.strip()))
    res["calls"]["global_lookups"] = bad
    mo, _ = listing(ClassPool(False), zo.read("com/skyy/skills/CfgFile.class"))
    mn, _ = listing(ClassPool(False), zn.read("com/skyy/skills/CfgFile.class"))
    a_, b_ = mo["<clinit>()V"].split(chr(10)), mn["<clinit>()V"].split(chr(10))
    res["calls"]["cfgfile_clinit"] = [[x, y] for x, y in zip(a_, b_) if x != y] if len(a_) == len(b_) else [["length", "%d %d" % (len(a_), len(b_))]]

    # X (review fixes): instruction positions of the calls that matter, in the NEW jar (-1 = no such call)
    def where(cls, prefix, pats):
        ms_, _ = listing(ClassPool(False), zn.read("com/skyy/skills/%s.class" % cls))
        ks = [k for k in ms_ if k.startswith(prefix)]
        if len(ks) != 1:
            return {"methods": ks}
        ls = ms_[ks[0]].split(chr(10))
        return dict((p, [i for i, ln in enumerate(ls) if p in ln]) for p in pats)
    res["calls"]["acrosys"] = where("AcroSys", "tick(", ["ManaRegen.tick", "Acro.state", "AcroCfg.ENABLED", "Acro.move", "Acro.falls", "Brew.tick", "Xbow.tick", "Perks.tick"])
    res["calls"]["kit_reload"] = where("SkillKit", "reload(", ["SkillCfg.load", "SkillStore.republishAll"])
    res["calls"]["kit_custom"] = where("SkillKit", "customSet(", ["SkillDefs.setTable", "SkillDefs.setClassTable", "SkillStore.republishAll", "SkillKit.classTotals"])
    res["calls"]["reload_cmd"] = where("ReloadCmd", "execute(", ["SkillCfg.load", "SkillStore.republishAll"])
    res["calls"]["republish_body"] = where("SkillStore", "republishAll(", ["monitorenter", "monitorexit", "invoke"])
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ parent
def main():
    if "--mkfake" in sys.argv:
        return run_mkfake(arg("--mkfake"))
    if "--old-run" in sys.argv:
        return run_old(arg("--old-run"), arg("--out"), arg("--xs"))
    if "--new-run" in sys.argv:
        return run_new(arg("--new-run"), arg("--out"), arg("--fake"), arg("--xs"))
    if "--bytecode" in sys.argv:
        return run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
    for j in (JAR, OLD_JAR):
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
    check(b"levels.class" not in livenow and b"mana.regen.inCombat" not in livenow and not os.path.exists(os.path.join(LIVE_DIR, "class-curve.properties")),
          "the live Skyy_SkyySkills is still 0.4.11's (no levels.class / mana.regen.inCombat / class-curve.properties)")
    prop = proposal_table()
    check([r[0] for r in prop] == list(range(1, 101)), "the proposal's section 5 table has levels 1-100")
    pcum = [0]
    for r in prop:
        pcum.append(pcum[-1] + r[1])
    gen = [50, 125, 200, 300, 500, 750, 1000, 1500, 2000, 3500, 5000, 7500, 10000, 15000, 20000, 30000, 50000, 75000, 100000, 200000,
           300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000, 1100000, 1200000, 1300000, 1400000, 1500000, 1600000,
           1700000, 1800000, 1900000, 2000000, 2100000, 2200000, 2300000, 2400000, 2500000, 2600000, 2750000, 2900000, 3100000,
           3400000, 3700000, 4000000] + [4300000 + 300000 * i for i in range(50)]
    gcum = [0]
    for x in gen:
        gcum.append(gcum[-1] + x)
    xs = totals_to_test(pcum, gcum)
    xs_file = os.path.join(SCRATCH, "xs.json")
    json.dump(xs, open(xs_file, "w"))
    me = os.path.abspath(__file__)
    fake = os.path.join(SCRATCH, "fake")
    p = subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(os.path.join(fake, "skyytest", "FakeAcc.class")), "the stand-in classes were generated")
    outs = {"old": os.path.join(SCRATCH, "run-old.json"), "new": os.path.join(SCRATCH, "run-new.json"), "bc": os.path.join(SCRATCH, "bytecode.json")}
    p = subprocess.run([sys.executable, me, "--old-run", OLD_JAR, "--out", outs["old"], "--xs", xs_file, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(outs["old"]), "child JVM for %s ran" % os.path.basename(OLD_JAR))
    p = subprocess.run([sys.executable, me, "--new-run", JAR, "--out", outs["new"], "--fake", fake, "--xs", xs_file, "--dir", SCRATCH], env=env)
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
    # ---------------------------------------------------------------- T
    T = D["T"]
    check(T["cper"] == [r[1] for r in prop], "T: SkillDefs.DEFAULT_CPER = the proposal's section 5 'XP for level' for levels 1-100")
    check(T["ccum"] == pcum and [pcum[i] for i in (10, 20, 30, 40, 60, 100)] == [3510, 21540, 77290, 209090, 929090, 6627590]
          and [pcum[i] for i in range(1, 101)] == [r[2] for r in prop], "T: class totals = the proposal's Total column (20 at 21,540, 40 at 209,090, 100 at 6,627,590)")
    check(T["per"] == O["per"] == gen and T["cum"] == O["cum"] == gcum and [gcum[i] for i in range(1, 101)] == [r[3] for r in prop],
          "T: the general table = 0.4.11's (= the proposal's Old total column)")
    check(all(pcum[i] <= gcum[i] for i in range(101)) and T["ecum"] == T["ccum"], "T: the class table is at or below the general one at every level; ECUM = the class table")
    check(T["maxes"] == [100] * 16 and T["cmax"] == 100 and T["max"] == 100 and not T["same"], "T: maxOf 100 for every slot, CMAX 100, sameAsOthers off")
    nbad = []
    for s in ("0", "4", "3", "12", "13"):
        for i, (a, b) in enumerate(zip(T["xs"][s], O["xs"])):
            if a != b:
                nbad.append((s, xs[i], a, b))
    check(not nbad, "T: non-class slots (Mining, Acrobatics, legacy Combat, Cooking, Exploration): level / into / need / progress = 0.4.11 for %d totals: %s" % (len(xs), nbad[:3]))

    def plevel(x):
        l = 0
        while l < 100 and x >= pcum[l + 1]:
            l += 1
        return l
    cbad = []
    for s in ("5", "15", "6"):
        for i, (lv, into, need, prog) in enumerate(T["xs"][s]):
            x = xs[i]
            L = plevel(x)
            wn = pcum[L + 1] - pcum[L] if L < 100 else 0
            if lv != L or into != x - pcum[L] or need != wn or (prog == "MAX") != (wn == 0):
                cbad.append((s, x, lv, into, need, L))
    check(not cbad, "T: class slots (Archery, Divinity, Swordsmanship) follow the proposal table for %d totals: %s" % (len(xs), cbad[:3]))
    check(T["general"] == [r[0] for r in O["xs"]], "T: SkillDefs.generalLevel = 0.4.11's global level for every total")
    rises = sum(1 for i in range(len(xs)) if T["xs"]["15"][i][0] > O["xs"][i][0])
    check(all(T["xs"]["15"][i][0] >= O["xs"][i][0] for i in range(len(xs))), "T: a class level is never below the 0.4.11 level for the same XP (%d of %d totals higher)" % (rises, len(xs)))
    print("T. class table = proposal (100 levels; 20 at 21,540 / 40 at 209,090 / 100 at 6,627,590), %d totals: other skills = 0.4.11, class skills = the table, never lower" % len(xs))
    # ---------------------------------------------------------------- G
    G = D["G"]
    check(all(a == max(b, c) for a, b, c in G["steep"]) and any(b > c for a, b, c in G["steep"]) and any(c > b for a, b, c in G["steep"]),
          "G: a steeper class list: class level = max(general, class) at every total (both sides win somewhere)")
    check(G["cut60"][:3] == [60, 60, 100] and G["cut60"][3] == 0 and G["cut60"][4] == "MAX", "G: class max 60 caps class levels at 60 (Mining stays 100): %s" % G["cut60"])
    check(G["gen50"] == [50, 100, 60, 50, 20], "G: the general list cut to 50: Mining max 50, Divinity still 100 (929,090 = 60, 21,540 = 20): %s" % G["gen50"])
    check(G["same"] and G["back"], "G: sameAsOthers = the general table exactly; switching it off restores the class table")
    print("G. guard: level = max(general, class) up to the class max; general cut to 50 keeps class 51-100; sameAsOthers = general")
    # ---------------------------------------------------------------- P
    P = D["P"]
    check(P["level"] == [28, 15, 5], "P: SkillStore.level: Divinity 67,425 = 28 (0.4.11: 15), Mining 67,425 = 15, Archery 1,000 = 5 (0.4.11: 4): %s" % P["level"])
    fl = P["fn_level"]
    check(fl["Divinity"] == 28 and fl["Priest"] == 28 and fl["Combat"] == 28 and fl["div"] == 28 and fl["Mining"] == 15 and fl["Archery"] == 5,
          "P: skill:fn:level Divinity / Priest / Combat (current class) / div = 28, Mining 15, Archery 5: %s" % fl)
    check(P["fn_xp"] == [67425, 67425], "P: skill:fn:xp answers the TOTAL XP, unchanged (SkyyGuilds / SkyyTrees): %s" % P["fn_xp"])
    check("Mining:15" in P["levels"] and "Divinity:28" in P["levels"] and "Archery:5" in P["levels"], "P: skill:<uuid> = %s" % P["levels"])
    # Overall: 8 listed skills (Mining 15 + 7 x 0) + the class skill 28 = 43 / 9 = 4 (4.7)
    check(P["overall"] == [4, 47, 9] and fl["Overall"] == 4 and P["ovmax"] == 100, "P: Overall Level from the class level 28: %s (max %d)" % (P["overall"], P["ovmax"]))
    check(P["skills_page"] == [None, True, True, True, True, True], "P: /skills rows: 'Divinity  28' + 'XP to level 29', 'Mining  15' + 'XP to level 16': %s" % P["skills_page"])
    check(P["stats_page"] == [None, True, True] and P["stats_mining"] == [None, True, True], "P: Stats page 'Divinity - level 28 of 100' / 'Mining - level 15 of 100': %s %s" % (P["stats_page"], P["stats_mining"]))
    check(P["top_page"] == [None, True, True, True], "P: Top 10 Divinity: Level 28 (Pria) / Level 20 (Alex 21,540), rank line level 28: %s" % P["top_page"])
    check(P["overall_page"] == [None, True, True], "P: Overall page 'Level 4 of 100' + 'Divinity 28 (your class)': %s" % P["overall_page"])
    # +100 Divinity XP at 67,425: class level 28 starts at 61,490, level 29 needs 7,550 -> 5,935 + 100 = 6,035 -> "6035/7550"
    check(P["msg"] == ["+100 Divinity XP (5935/7550)"] and P["msg_take"] == "+1 Mining XP (0/30.0k)",
          "P: the +XP chat lines use each slot's table (Divinity 67,425 = 5,935 into level 29's 7,550; Mining 67,425 = 0 / 30k): %s %s" % (P["msg"], P["msg_take"]))
    check(P["party"] == "[Party] +6 Divinity XP (5935/7550) from Skyy's kill", "P: [Party] line: %s" % P["party"])
    lu = P["levelup"]
    check(lu["texts"][:2] == ["SKILL LEVEL UP  Divinity 19 -> 20   +2000 coins", "  next: Divinity 21 at 0/3350 XP - /skills"] and lu["coins"] == [[str(lu["coins"][0][0]), 2000]]
          and lu["paid"] == 20 and lu["level"] == 20, "P: a real class level up (21,539 -> 21,540): SKILL LEVEL UP Divinity 19 -> 20 +2000 coins, next at 3,350: %s" % lu)
    lm = P["levelup_mining"]
    check(lm["texts"][:1] == ["SKILL LEVEL UP  Mining 9 -> 10   +1000 coins"] and [c[1] for c in lm["coins"]] == [1000], "P: Mining 9,924 -> 9,925 = level 10 on the general table: %s" % lm)
    print("P. per-slot: level / skill:fn:level / skill:<uuid> / Overall / pages / chat / level-up rewards all use Divinity 28 (0.4.11: 15), Mining 15")
    # ---------------------------------------------------------------- M
    M = D["M"]
    lv = M["live"]
    check(lv["r1"]["ready"] and lv["r1"]["pending"] == {} and "%d profile file(s) scanned, 0 with a higher class level" % lv["n_players"] in lv["r1"]["curve"],
          "M live: first start scans the %d profile files, nobody rose: %s" % (lv["n_players"], lv["r1"]["curve"]))
    check(lv["r1"]["heal"] == "", "M live: HealMig has nothing to do on the live data (its 0.4.11 marker is there): %r" % lv["r1"]["heal"])
    check(set(lv["changed1"]) == {"xp.properties", "class-curve.properties"} and lv["xp_append"] and lv["players_same"],
          "M live: start 1 changes only xp.properties (+ exactly the two blocks) and writes class-curve.properties; players untouched: %s" % lv["changed1"])
    check(lv["changed2"] == [] and lv["r2"]["ready"] and lv["r2"]["pending"] == {} and lv["r2"]["curve"] == "", "M live: start 2 changes nothing: %s" % lv["changed2"])
    check("\nscanned=" in lv["record"] and "\npending." not in lv["record"] and "\ndone." not in lv["record"] and lv["record"].count("\r") == 0,
          "M live: the record (scanned, no pending / done line): %r" % lv["record"][:300])
    e1 = M["edit1"]
    check(e1["start"]["pending"] and sorted(e1["start"]["pending"].values()) == sorted(["15:15:28", "5:20:51", "5:4:5"]),
          "M edit: the scan records exactly the 3 risen profiles (Divinity 15 -> 28, Archery 20 -> 51, Archery 4 -> 5): %s" % e1["start"]["pending"])
    check(e1["rec1"].count("\npending.") == 3 and "\ndone." not in e1["rec1"], "M edit: the record holds the 3 pending entries before anyone plays")
    want_c1 = sum(100 * L for L in range(16, 29))
    t1 = e1["t1"]
    check(len(t1) >= 1 and t1[0] == "[Skills] Class skill curve updated: Divinity is now level 28 (was 15) - +28.6k coins for levels 16 to 28",
          "M edit: ONE chat line: %s" % t1)
    check(sum(c[1] for c in e1["c1"]) == want_c1 == 28600 and len(e1["c1"]) == 13 and e1["paid1"] == 28,
          "M edit: the level-up coins of exactly levels 16-28 (13 payouts, 28,600) and the paid marker 28: %s" % e1["c1"][:3])
    check(any(t.startswith("OVERALL LEVEL UP") for t in t1[1:]), "M edit: the Overall level up from the class jump: %s" % t1[1:])
    check(not e1["disk_paid_before"] and e1["disk_paid_after"] and e1["rec2"].count("\ndone.") == 1 and e1["rec2"].count("\npending.") == 2,
          "M edit: flush saves the player file (paid 28 on disk) before the record moves the entry to done")
    check(e1["t2"] == [] and e1["c2"] == [] and e1["t3"] == [] and e1["c3"] == [], "M edit: a second tick and a later small award pay / say nothing more: %s %s" % (e1["t2"], e1["t3"]))
    e2 = M["edit2"]
    check(len(e2["start2"]["pending"]) == 2 and len(e2["start2"]["done"]) == 1, "M edit: restart: 2 still pending, 1 done: %s" % e2["start2"]["pending"])
    want_c4 = sum(100 * L for L in range(21, 52))
    check(e2["t4"][:1] == ["[Skills] Class skill curve updated: Archery is now level 51 (was 20) - +111.6k coins for levels 21 to 51"]
          and sum(c[1] for c in e2["c4"]) == want_c4 == 111600, "M edit: profile 2 told when it becomes active (111,600 coins): %s" % e2["t4"][:2])
    check(e2["t5"][:2] == ["[Skills] Class skill curve updated: Archery is now level 5 (was 4) - +500 coins for level 5", "  Unlocked: Crossbows stay loaded when you switch slots"]
          and [c[1] for c in e2["c5"]] == [500], "M edit: Archery 4 -> 5 = the crossbow unlock line too: %s" % e2["t5"][:3])
    check(e2["start3"]["pending"] == {} and len(e2["start3"]["done"]) == 3 and e2["t6"] == [] and e2["c6"] == [],
          "M edit: a third start: nothing pending, 3 done, nothing said or paid again")
    dk = e2["disk"]
    k1_, k2_, k3_ = sorted(dk, key=lambda k: (len(k), k))
    check("Combat.Priest.paid=28" in dk[k1_].splitlines() and "Combat.Archer.paid=51" in dk[k2_].splitlines() and "Combat.Archer.paid=5" in dk[k3_].splitlines(),
          "M edit: every told profile's paid marker is on disk (28 / 51 / 5)")
    check(e2["rec3"].count("\ndone.") == 3 and "\npending." not in e2["rec3"] and "Combat.Priest 15 -> 28 +28600 coins" in e2["rec3"], "M edit: the record ends with 3 done lines")
    bz = M["busy"]
    check(bz["while"] == [[], True] and bz["after"][1] is False and bz["after"][0][:1] and bz["after"][0][0].startswith("[Skills] Class skill curve updated: Divinity is now level 28"),
          "M busy: profile:busy waits, told right after: %s" % bz)
    nw = M["nowrite"]
    check(not nw["w1"]["ready"] and nw["w1"]["pending"] == {} and nw["t"] == [] and not nw["rec"] and nw["w2"]["ready"] and len(nw["w2"]["pending"]) == 1,
          "M unwritable record: nobody told; the next start scans again: %s / %s" % (nw["w1"], nw["w2"]["pending"]))
    nc = M["nocoins"]
    check(nc["t1"][:1] == ["[Skills] Class skill curve updated: Divinity is now level 28 (was 15)"] and sum(1 for x in nc["t1"] if "Class skill curve" in x) == 1
          and nc["paid"] == 15 and nc["t2"] == []
          and any("coins for earlier Divinity level ups" in t for t in nc["t3"]) and sum(c[1] for c in nc["coins"]) == 28600 and nc["paid_after"] == 28,
          "M no SkyyCoins: the line once (no coins), the levels stay owed and the next award pays them once: %s" % nc)
    print("M. ClassCurve: live copy %d files, nobody to tell, start twice = once; edited copy 3 profiles told once each (28,600 / 111,600 / 500 coins, unlock line)" % lv["n_players"])
    # ---------------------------------------------------------------- R
    R = D["R"]
    a = R["amount"]
    check(a["out0"] == 0.0 and a["out20"] == 1.0 and a["out20_pulse"] == 0.2, "R: out of combat SkyySkills adds only the boost part: 0 / +20%% = 1 a second (vanilla 5 + 1 = 6): %s" % a)
    check(a["in0"] == 2.5 and a["in0_pulse"] == 0.5 and a["in20"] == 3.0 and a["in_f100"] == 5.0, "R: in combat 50%% of (5 + boosts): 2.5 / 3.0 a second, 100%% = 5: %s" % a)
    check(a["in_f0"] == 0.0 and a["out_f0"] == 1.0, "R: in-combat 0% = vanilla (nothing in combat), out-of-combat boosts still run")
    check(a["cap"] == 0.1 and a["full"] == 0.0 and a["nomana"] == 0.0 and a["charging"] == 0.0 and a["secs0"] == 0.0, "R: max Mana cap / full / no Mana pool / charging = 0")
    check(a["neg"] == 0.0 and a["neg_in"] == 2.5 and a["big"] == 50.0 and a["nan"] == 0.0 and a["f150"] == 5.0, "R: a negative total counts 0, 5000% clamps to 1000%, NaN = 0, factor clamps to 100")
    check(R["six_seconds"] == 15.0, "R: 6 s in combat in 0.2 s pulses at 50%% = 15 Mana: %s" % R["six_seconds"])
    rr = R["rates"]
    check(R["stubs"] == [1, 1], "R: the EntityModule / DamageModule stand-ins took their instance field: %s" % R["stubs"])
    check(rr["out"] == [5.0, 5.0, 0.0] and rr["in"] == [5.0, 0.0, 5.0] and rr["edge6"] == [5.0, 5.0, 0.0] and rr["edge5999"] == [5.0, 0.0, 5.0],
          "R: real conditions: hit 10 s ago = out of combat, 2 s / 5.999 s = in combat, exactly 6 s = out (vanilla's >=): %s" % rr)
    check(rr["in_charging"] == [5.0, 0.0, 0.0] and rr["out_charging"] == [5.0, 0.0, 0.0] and rr["dead"] == [5.0, 0.0, 0.0] and rr["dead_in"] == [5.0, 0.0, 0.0],
          "R: charging (in or out of combat) and dead = no refill from SkyySkills either: %s" % rr)
    check(rr["pct_entry"] == [5.0, 5.0, 0.0] and rr["zero_entry"] == [5.0, 5.0, 0.0] and rr["no_conds"] == [2.0, 2.0, 0.0] and rr["two"] == [6.0, 0.0, 6.0] and rr["state"] == [0, 1, 2, 2],
          "R: Percentage / zero entries ignored, no conditions = running, two entries add up: %s" % rr)
    check(R["cfg"] == {"default": 50, "150": 100, "neg": 0, "abc": 50, "zero": 0, "25": 25}, "R: mana.regen.inCombat load + clamps: %s" % R["cfg"])
    print("R. Mana regen: out 0 / +20%% = +%s/s, in combat %s/s (+20%%: %s), 0%% = vanilla, cap, no Mana; real conditions in / out / charging / dead" % (a["out20"], a["in0"], a["in20"]))
    # ---------------------------------------------------------------- B
    Bq = D["B"]
    check(Bq["seq"] == [0.0, "true", "true", 20.0, ["SkyyAccessories=+5", "SkyyGear=+15"], "true", 25.0, "true", 5.0, "false", "true", 0.0, "true", ["SkyyAccessories=+5"]],
          "B: add / replace / remove / get / sources; a negative total counts 0; add 0 removes: %s" % Bq["seq"])
    check(Bq["bad"] == ["false", "false", "false", "false", "false", "false", 0.0, None, True, []], "B: bad arguments: %s" % Bq["bad"])
    check(Bq["clamp"] == [1000.0, ["Big=+1000"]] and Bq["clear"] == [2, 0.0, 0.0, 0], "B: one source clamps to 1000, the total too; clear removes a source everywhere: %s %s" % (Bq["clamp"], Bq["clear"]))
    check(Bq["types"] == ["java.lang.Double", "java.lang.Boolean", "java.lang.Integer", "[Ljava.lang.String;"], "B: java.lang return types: %s" % Bq["types"])
    check(Bq["action"][0] == "ok" and Bq["action"][2].startswith("Mana Regen +20% (SkyyGear=+20). ") and ("In combat 50% of the normal refill." in Bq["action"][2]
          or "in combat 3/s (50%)." in Bq["action"][2]) and len(Bq["action"][2]) <= 110 and Bq["action_null"][0] == "ok",
          "B: the Server Setup action (the compact one-line answer, review fix R4): %s" % Bq["action"])
    check(Bq["total_feeds"] == 3.0, "B: a registered +20%% feeds the in-combat refill (3 a second): %s" % Bq["total_feeds"])
    print("B. skill:fn:manaregen: add/remove/get/sources/clear, clamps, java.lang types; action: %r" % Bq["action"][2][:120])
    # ---------------------------------------------------------------- C
    C = D["C"]
    nd, od = D["defaults"], O["defaults"]
    want = od.replace("# SkyySkills %s - XP rules" % OLD_VERSION, "# SkyySkills %s - XP rules" % VERSION, 1)
    want = want.replace("# is the max level, at most 100)\n", "# is the max level, at most 100). Every skill but the class skills - they level on levels.class (Class skill levels, below).\n", 1)
    want = want + "\n" + D["curve_block"] + "\n" + D["mreg_block"]
    check(nd == want, "C: the 0.4.12 default file = 0.4.11's + version line + the levels comment + the two blocks at the end")
    check(C["lf"] == {"exact": True, "again_same": True, "no_cr": True}, "C: a 0.4.11-era LF file = itself + a blank line + the two blocks, once: %s" % C["lf"])
    check(C["crlf"] == {"exact": True, "all_crlf": True}, "C: the same file in CRLF: the blocks appended in CRLF, every byte before them kept: %s" % C["crlf"])
    check(C["admin"] == {"same_kept": True, "list_added": True, "SAME": True, "class_eq_general": True}, "C: an admin's sameAsOthers=true is kept (only the list appended): %s" % C["admin"])
    check(C["noeol"], "C: a file without a final newline gets one before the blank line")
    check(C["short"] == [3, 3, 3, 2, True, True], "C: a 3-entry class list = class max 3: %s" % C["short"])
    check(C["bad"] == [100, True, True], "C: a bad class list = the default class table + a bad line: %s" % C["bad"])
    check(C["fresh"] == [100, False, 50, True] and "class skills own table, max level 100, in-combat Mana regen 50%" in C["fresh_text"], "C: a fresh file: %s %s" % (C["fresh"], C["fresh_text"][-160:]))
    print("C. default file = 0.4.11 + version + levels comment + 2 blocks; old files get both blocks once (LF / CRLF kept); admin switch kept")
    # ---------------------------------------------------------------- K
    K = D["K"]
    ro, rn = O["rows"]["rows"], D["rows"]["rows"]
    ko, kn = [r[0] for r in ro], [r[0] for r in rn]
    check(len(rn) == 180 and [k for k in kn if k not in NEW_KEYS] == ko and all(k in kn for k in NEW_KEYS), "K: 180 rows = 0.4.11's 174 in order + %s" % NEW_KEYS)
    check(kn[kn.index("levels"):kn.index("levels") + 7] == ["levels", "levels.scale", "levels.max"] + NEW_KEYS[:4] and kn[kn.index("overall.chat") + 1:kn.index("overall.chat") + 3] == NEW_KEYS[4:],
          "K: the class rows right after the general curve rows, the Mana rows after overall.chat")
    od_ = dict((r[0], r) for r in ro)
    diff = sorted(r[0] for r in rn if r[0] in od_ and r != od_[r[0]])
    check(diff == ["levels", "levels.max", "levels.scale"], "K: only the three general curve rows changed: %s" % diff)
    nr = dict((r[0], r) for r in rn)
    for k in diff:
        ch = [i for i in range(11) if nr[k][i] != od_[k][i]]
        check(set(ch) <= {1, 10}, "K: %s: only label / help changed: %s" % (k, ch))
    check(nr["levels.class"][3:10] == ["text", ",".join(str(r[1]) for r in prop), "1", "2000", "", "", "live,danger,adv"] and nr["levels.class.scale"][3:10] == ["int", "100", "10", "1000", "step=5", "%", "live,danger"]
          and nr["levels.class.max"][3:10] == ["int", "100", "1", "100", "step=5", "", "live,danger"] and nr["levels.class.sameAsOthers"][3:10] == ["bool", "false", "", "", "", "", "live,danger"]
          and nr["mana.regen.inCombat"][3:10] == ["int", "50", "0", "100", "step=5", "%", "live"] and nr["mana.regen.show"][3] == "action",
          "K: the new rows' types / defaults / bounds / flags")
    check(all(len(r[1]) <= 40 and len(r[10]) <= 100 for r in rn), "K: labels <= 40, help <= 100")
    check(K["get"] == ["100", "100", "100", "100"], "K: customGet class max / scale / max / scale: %s" % K["get"])
    check(K["cut60"][:2] == ["ok", "60"] and K["cut60"][3:] == ["levels.class", 60, 60, 60, 100] and "Class max level: 60 (was 100)" in K["cut60"][2],
          "K: Class max level 60: the class list cut, the general max untouched: %s" % K["cut60"])
    check(K["raise100"][:2] == ["ok", "100"] and K["raise100"][3:] == [True, 100] and "back with the XP they had before the cut" in K["raise100"][2], "K: raised to 100: the exact class list back: %s" % K["raise100"])
    check(K["scale110"][:3] == ["ok", "110", 55] and K["scale100"] == ["ok", "100", True], "K: class curve size 110 -> level 1 = 55; 100 = the exact default: %s %s" % (K["scale110"], K["scale100"]))
    check(K["bad"] == ["bad", "bad", "bad", "bad"], "K: out-of-range / non-number class curve values refused: %s" % K["bad"])
    check(K["general50"] == ["ok", "levels", 50, 100, 100], "K: the general Max level 50 leaves the class table alone: %s" % K["general50"])
    check(K["read"] == ["4", str(round(100 * 100 / (50 + 100 + 160 + 220))), "2", "100", "100"], "K: customRead from a History copy: %s" % K["read"])
    check(K["check"] == [True, True, True], "K: checkLevels guards levels.class too")
    check(D["kill"] == O["kill"] and D["base"] == O["base"] and D["other"] == O["other"], "K: kill XP at the defaults = 0.4.11's: %s" % D["kill"])
    check(D["paid"] == O["paid"], "K: grants / crafting / heal XP paid = 0.4.11's: %s" % D["paid"])
    print("K. rows 180 (+%s); class curve rows cut / raise / scale / read; XP maths = 0.4.11" % ", ".join(NEW_KEYS))
    # ---------------------------------------------------------------- F
    diff = bc["diff"]
    beyond = dict((n.split("/")[-1][:-6], d) for n, d in diff.items() if set(d["changed"]) != set(d["vo"]) or d["new"] or d["gone"]
                  or d["fields_new"] or d["fields_gone"])
    vonly = sorted(n.split("/")[-1][:-6] for n in diff if n.split("/")[-1][:-6] not in beyond)
    want_beyond = {"SkillDefs", "SkillCfg", "SkillStore", "Overall", "SkillMsg", "PartyXp", "SkillXp", "Perks", "Acro", "AcroSys", "SkillsPage",
                   "StatsPage", "OverallPage", "TopCmd", "SkillKit", "SkillsCmd", "SkillTick", "SkyySkillsPlugin", "CfgRows", "CfgFile",
                   "ReloadCmd"}   # review fix R9: /skills reload calls SkillStore.republishAll
    check(set(beyond) == want_beyond, "F: classes changed beyond the version string: %s (unexpected %s, missing %s)" % (sorted(beyond), sorted(set(beyond) - want_beyond), sorted(want_beyond - set(beyond))))
    check(sorted(bc["only_new"]) == sorted("com/skyy/skills/%s.class" % c for c in ("ClassCurve", "ManaRegen", "ManaRegenFn", "ManaCmd")) and bc["only_old"] == [],
          "F: + ClassCurve, ManaRegen, ManaRegenFn, ManaCmd only: %s %s" % (bc["only_new"], bc["only_old"]))
    sd = beyond.get("SkillDefs", {})
    check(sorted(sd.get("gone", [])) == ["intoLevel(J)J", "levelOf(J)I", "needFor(J)J", "progress(J)Ljava/lang/String;"]
          and sorted(sd.get("new", [])) == sorted(["cumOf(I)[J", "generalLevel(J)I", "intoLevel(IJ)J", "levelIn([JJ)I", "levelOf(IJ)I", "maxOf(I)I", "needFor(IJ)J",
                                                  "progress(IJ)Ljava/lang/String;", "recalc()V", "setClassTable([JZ)V"]),
          "F: SkillDefs: the global lookups gone, the per-slot ones new: gone %s new %s" % (sd.get("gone"), sd.get("new")))
    check(bc["calls"]["global_lookups"] == [], "F: no (J) level lookup is called anywhere in the new jar: %s" % bc["calls"]["global_lookups"][:3])
    cf = beyond.get("CfgFile", {})
    check(cf.get("changed") == ["<clinit>()V"] and not cf.get("new") and not cf.get("gone") and bc["calls"]["cfgfile_clinit"] == [["sipush 174", "sipush 180"]] * 2,
          "F: CfgFile (kit): only its per-row arrays, sized 174 -> 180: %s" % bc["calls"]["cfgfile_clinit"])
    for c_ in ("Acro", "AcroSys", "SkillsCmd", "SkillTick", "TopCmd", "SkillMsg", "PartyXp"):
        d_ = beyond.get(c_, {})
        check(not d_.get("gone") and not d_.get("fields_gone") and not d_.get("fields_new") and len(d_.get("changed", [])) <= 2,
              "F: %s: only its hook / per-slot call changed: %s" % (c_, d_.get("changed")))
    for cls in ("KillSys", "HealXp", "BridgeXp", "BridgeTask", "HealMig", "ManaMig", "ManaGuard", "ManaCost", "SkillHealFn", "SkillAddFn", "SkillCraftFn",
                "SkillXpFn", "SkillFn", "OverallFn", "Xbow", "XbowCfg", "DivCfg", "OverallCfg", "BreakSys", "HarvestSys", "SkillClass", "CfgHist", "CfgLog", "SkillBonus"):
        check("com/skyy/skills/%s.class" % cls in bc["same"] or cls in vonly, "F: %s byte-identical (or the version string only)" % cls)
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    mo, mn = json.loads(zo.read("manifest.json")), json.loads(zn.read("manifest.json"))
    kd = sorted(k for k in set(mo) | set(mn) if mo.get(k) != mn.get(k))
    check(kd in (["Description", "Name", "Version"], ["Description", "Version"]), "F: manifest: only %s differ" % kd)
    nonclass = sorted(n for n in set(zo.namelist()) | set(zn.namelist()) if not n.endswith(".class") and n != "manifest.json"
                      and (n not in zo.namelist() or n not in zn.namelist() or zo.read(n) != zn.read(n)))
    check(nonclass == [], "F: every non-class entry byte-identical (the 40 spell overrides): %s" % nonclass[:5])
    print("F. class bytes: + ClassCurve, ManaRegen, ManaRegenFn, ManaCmd; changed beyond the version %d classes; version only %d; byte-identical %d"
          % (len(beyond), len(vonly), len([n for n in bc["same"]])))
    # ---------------------------------------------------------------- X: the review fixes
    X = D["X"]
    on = X["ov_none"]
    check(on["err"] is None and on["max"] == 0 and on["title"] and on["sub"] and on["line"] and not on["maxlay"] and not on["the_highest"]
          and on["next"] == ["Nothing - no skill counts toward the Overall Level"],
          "X R1: no counted skill: 'Level 0 of 0', 'No skill counts ...', one 'Nothing - no skill counts' line, NOT the max layout: %s" % on)
    om = X["ov_max"]
    check(om["err"] is None and om["max"] == 100 and om["title"] and om["maxlay"] and om["the_highest"] and om["next"] == [],
          "X R1: a maxed player (Mining 100 only) still gets 'Level 100 of 100' + 'Max Overall Level reached': %s" % om)
    oi = X["ov_mid"]
    check(oi["err"] is None and oi["title"] and not oi["maxlay"] and oi["next_hd"] and oi["next"] and not any("no skill counts" in x for x in oi["next"]),
          "X R1: Mining 15 only: 'Level 15 of 100' + 'Overall Level 16 adds' with its lines: %s" % oi)
    ac = bc["calls"]["acrosys"]
    check("methods" not in ac and len(ac["ManaRegen.tick"]) == 1 and all(len(ac[k]) >= 1 for k in ("Acro.state", "AcroCfg.ENABLED", "Acro.move", "Acro.falls", "Brew.tick", "Xbow.tick", "Perks.tick"))
          and ac["ManaRegen.tick"][0] < min(ac["Acro.state"][0], ac["AcroCfg.ENABLED"][0], ac["Acro.move"][0], ac["Acro.falls"][0], ac["Brew.tick"][0], ac["Xbow.tick"][0]),
          "X R3: AcroSys.tick calls ManaRegen.tick before Acro.state / the Acrobatics block / Brew.tick / Xbow.tick (instruction order): %s" % ac)
    cp = X["compact"]
    check(cp == ["Mana Regen +0% (no boosts). Refill 5/s, in combat 2.5/s (50%).", "Mana Regen +20% (SkyyGear=+20). Refill 6/s, in combat 3/s (50%).",
                 "Mana Regen +20% (SkyyGear=+20). Refill 6/s, in combat none (vanilla).", "Mana Regen +0% (no boosts). In combat 50% of the normal refill.",
                 "Mana Regen +0% (no boosts). In combat no refill (vanilla).", "Mana Regen +0% (no boosts). Refill 5/s, in combat 5/s (100%)."],
          "X R4: ManaRegen.compact lines (vanilla 5/s; +20%%; in-combat 0%%; rate unknown; null sources): %s" % cp)
    cm, cl, co, c2 = X["compact_many"], X["compact_long"], X["compact_odd"], X["compact_two"]
    check(cm == "Mana Regen +1000% (Source00=+0, Source01=+1, Source02=+2, +9 more). Refill 55/s, in combat 55/s (100%)."
          and cl == "Mana Regen +5% (1 source). Refill 5.25/s, in combat 2.625/s (50%)."
          and co == "Mana Regen +333.333% (Source00=+0, Source01=+1, +10 more). Refill 14.444/s, in combat 7.944/s (55%)."
          and c2 == "Mana Regen +45% (SkyyAccessories=+25, SkyyGear=+20). Refill 7.25/s, in combat 3.625/s (50%)." and X["compact_worst"] <= 110,
          "X R4: 12 sources at +1000%% (+9 more), one 64-character source (1 source), odd numbers, two that fit; 400 random lists: longest %d (<= 110): %r / %r / %r / %r"
          % (X["compact_worst"], cm, cl, co, c2))
    act, act1 = X["action"], X["action1"]
    vr = X["vanilla_rate"]
    tail = ("Refill %s/s" % ("%g" % (vr * 1.2))) if vr > 0 else "In combat 50% of the normal refill."
    check(act[0] == "ok" and len(act[2]) <= 110 and act[2].startswith("Mana Regen +98% (") and "+" in act[2] and "more)" in act[2]
          and act1.startswith("Mana Regen +20% (SkyyGear=+20). ") and tail in act1 and len(act1) <= 110
          and X["action_null"][0] == "ok" and X["action_null"][2].startswith("In game: your own. Mana Regen +0% (no boosts). ") and len(X["action_null"][2]) <= 110,
          "X R4: the Server Setup action answers the compact line (13 sources: %d characters; vanilla rate %s): %r / %r / %r" % (len(act[2]), vr, act[2], act1, X["action_null"][2]))
    check("Mana Regen boosts +20% (SkyyGear=+20)" in X["text1"] and "In combat: 50% of (vanilla + boosts)" in X["text1"] and "Never while charging." in X["text1"],
          "X R4: /skills mana keeps the full text: %r" % X["text1"])
    s150, s100 = X["scale150"], X["scale100"]
    check(s150["r"][:2] == ["ok", "150"] and s150["ecum1"] == 50 and s150["ccum1"] == 75 and "needs 75" not in s150["r"][2]
          and s150["r"][2] == "Class level curve size: 150%% - class skill 1 at %s XP, 20 at %s, 100 at %s in total. Saved (applies now)." % tuple(s150["eff"])
          and s150["eff"][0] == "50" and s150["eff"][1] == "32.3k",
          "X R5: Class level curve size 150%%: the EFFECTIVE totals (class skill 1 at 50 XP - capped by the other list - not the list's 75): %s" % s150)
    check(s100["r"] == ["ok", "100", "Class level curve size: 100% - class skill 1 at 50 XP, 20 at 21.5k, 100 at 6.62m in total. Saved (applies now)."] and s100["same_list"],
          "X R5: back to 100%%: %s" % s100)
    check(X["scale_max10"] == ["ok", "Class level curve size: 100% - class skill 1 at 50 XP, 10 at 3510 in total. Saved (applies now)."],
          "X R5: class max 10: no '20 at': %s" % X["scale_max10"])
    check(X["scale_same"] == ["ok", "Class level curve size: 120% - not in use while Class skills use the other list is on. Saved (applies now).", True],
          "X R5: sameAsOthers on: the class list is not in use: %s" % X["scale_same"])
    check(X["pub_custom"] and X["pub_reload"], "X R9: SkillKit.customSet (a curve row) and SkillKit.reload clear SkillStore.PUBLISHED: %s %s" % (X["pub_custom"], X["pub_reload"]))
    pe = X["pub_e2e"]
    check("Divinity:28" in pe[0] and pe[1] and "Divinity:28" in pe[2] and not pe[3] and pe[4] == 20 and "Divinity:20" in pe[5] and pe[6],
          "X R9: skill:<uuid> Divinity:28 -> Class max level 20 -> the next publishOnline republishes Divinity:20: %s" % pe)
    kr, kc, rc, rb = bc["calls"]["kit_reload"], bc["calls"]["kit_custom"], bc["calls"]["reload_cmd"], bc["calls"]["republish_body"]
    check(len(kr.get("SkillStore.republishAll", [])) == 1 and len(kr.get("SkillCfg.load", [])) == 1 and kr["SkillCfg.load"][0] < kr["SkillStore.republishAll"][0]
          and len(rc.get("SkillStore.republishAll", [])) == 1 and len(rc.get("SkillCfg.load", [])) == 1 and rc["SkillCfg.load"][0] < rc["SkillStore.republishAll"][0]
          and len(kc.get("SkillStore.republishAll", [])) == 1 and kc["SkillStore.republishAll"][0] > max(kc["SkillDefs.setTable"] + kc["SkillDefs.setClassTable"])
          and len(kc.get("SkillKit.classTotals", [])) == 1 and kc["SkillKit.classTotals"][0] > max(kc["SkillDefs.setClassTable"]),
          "X R9 / R5: republishAll after SkillCfg.load in SkillKit.reload and /skills reload, after the table set in customSet (classTotals too): %s %s %s" % (kr, rc, kc))
    check(len(rb.get("monitorenter", [])) == 1 and len(rb.get("invoke", [])) == 1, "X R9: republishAll = one call inside the PUB lock: %s" % rb)
    print("X. review fixes: Overall page without counted skills not max; Mana refill first in AcroSys.tick; compact action %d chars; effective class totals; skill:<uuid> republished"
          % len(act[2]))
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
