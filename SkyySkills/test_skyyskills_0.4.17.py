"""SkyySkills 0.4.17 - bare-JVM harness for THE MOB CURVE'S SKYYSKILLS PART (tools/skills_0_4_17_patch.py; research/Mob-Curve-Spec.md 2.4,
4.2, 6.3, 6.4, 7.4). The new parts on the REAL classes of the 0.4.17 jar (HytaleServer.jar on the class path, -Xverify:all); the live save
data only ever READ and copied into the scratch folder. Everything 0.4.16 already checked is guarded by the class compare (section F: only
the planned classes differ from the SET pin 0.4.16 beyond the version string) - run SkyySkills/test_skyyskills_0.4.16.py for the older parts.
SkyyMobs 0.1.4's mob:fn:info is a stand-in Function implementing the spec 7.3 contract exactly (the real one is built in parallel).

    python SkyySkills/test_skyyskills_0.4.17.py [--jar <SkyySkills-0.4.17.jar>] [--prev <SkyySkills-0.4.16.jar>] [--dir <scratch>]
                                                [--live <Skyy_SkyySkills folder>] [--keep]

SECTIONS
  A   every class of the jar loads under -Xverify:all
  C   the fresh 0.4.17 default file (real SkillCfg.load): the KXP block once at the end; MobXp.LEVEL, the 16 default points, curve(L) = the
      Python model at levels -5..110; ManaRegen 7 / 20; the 4 new rows + the relabelled rows; the load summary
  CV  the curve loader on 10 line sets (bad entries, 05 + 5, bounds, empty -> default + WARN once) + combatXp.xpFrom parsing + the check= hook
  X   the maths: lvBase on every vanilla levelled base (max(base, 50)) x levels 1-60 x Hard / Easy / Normal shares = the Python model
      (bit-exact); vs 0.4.16's Hard XP (the integer chain): within 1.2 % of its exact product everywhere, worst vs the rounded chain
      reported; payD's chance rounding (floor / ceil only, mean); the spec 4.3 table rows
  K   MobXp.kill2 end to end on a stand-in store (the killer + 6 party members on their own class skills, the real PartyXp.share3 / one3):
      level mode Hard / Easy, gap on / part off, a custom curve, health mode, no mob:fn:info (= 0.4.16 path), info null / throwing /
      malformed (= classXp, no level factor), a role override (on / part off), the first-kill line with "(Lv 1 health B)"
  R   Mana regen per class level: ManaRegen.total / sources / compact / the bridge (skill:fn:manaregen) at class level 0..100, with a
      registered boost, the MAX_PCT clamp, no class, an offline profile (no file read); the REAL ManaRegen.tick out of / in combat
  MG  KillXpMig on 13 file shapes: the live file, CRLF, no final newline, a hand-set levelBonus 0.1, the part off, an admin's
      combat.xpFrom=health, an admin's curve entry, an admin's mana.regen.perLevel, everything present, the marker, a trailing backslash,
      an empty file, a broken file; exact bytes, History copy first, one change-log line, run twice = once
  M   START TWICE on the scratch copy of the live data (the plugin's setup order): start 1 = xp.properties gets the block (+ History + 1 log
      line), players/ untouched; start 2 changes nothing
  KC  the rows through the REAL config kit (config:fn:SkyySkills): keys / tset / add / remove on combat.levelCurve (refusals), the choice row
      (label typed), mana.regen.perLevel live, the change log holds the update line
  F   class compare 0.4.16 -> 0.4.17 (version string normalised): only the planned classes differ; KillSys calls kill2, not kill
  AU  the engine-access audit (every bytecode reference looked up with the JVM's own access rules; control refused)
"""
import os, sys, json, math, shutil, subprocess, zipfile, random, importlib.util
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.4.17", "0.4.16"
PKG = "com.skyy.skills."
MINING, DIVINITY, ARCHERY, WARRIOR = 0, 15, 5, 6
N = 16
KXP_MARK_ID = "SkyySkills 0.4.17 kill XP by level"
KXP_LEVELS = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]
# max(base, 50) of every vanilla levelled role (SkyyMobs levels list x Assets.zip role health; research/Mob-Curve-Spec.md numbers 1.4)
XP_BASES = [50, 54, 60, 61, 74, 81, 88, 92, 103, 107, 118, 124, 126, 145, 158, 160, 193, 224, 226, 249, 283, 341, 400]


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "mc-skills", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyySkills-%s.jar" % PREV_VERSION)))
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


def t15():
    """the 0.4.15 harness module (its stand-in generator, JVM helpers, regen stand-ins and the access audit) - imported, never run"""
    spec = importlib.util.spec_from_file_location("t0415", os.path.join(HERE, "test_skyyskills_0.4.15.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.SCRATCH = SCRATCH
    return m


# ============================================================================================ the Python model (spec 4.2)
def kxp_fmt(f):
    c = int(math.floor(f * 100.0 + 0.5))
    c = 10 if c < 10 else (100000 if c > 100000 else c)
    return format(Decimal(c).scaleb(-2).normalize(), "f")


def kxp_curve(b):
    return [(L, kxp_fmt((1.0 + 0.08 * (L - 1)) * (1.0 + b * (L - 1)))) for L in KXP_LEVELS]


DEF_PTS = [(float(L), float(v)) for L, v in kxp_curve(0.05)]


def ev(pts, x):
    """SkyyGear's GearBase.eval in Python (same operations, same order)"""
    ls, vs = [p[0] for p in pts], [p[1] for p in pts]
    n = len(ls)
    if n == 0:
        return 1.0
    if x <= ls[0]:
        return vs[0]
    if x >= ls[n - 1]:
        return vs[n - 1]
    for i in range(1, n):
        if x <= ls[i]:
            return vs[i - 1] + (vs[i] - vs[i - 1]) * (x - ls[i - 1]) / (ls[i] - ls[i - 1])
    return vs[n - 1]


def lvbase_py(xb, L, xm, per=0.2, cmin=1, cmax=500, mult=1.5, pts=None):
    x = xb * per
    if x != x or x < 0.0:
        x = 0.0
    if x < float(cmin):
        x = float(cmin)
    if x > float(cmax):
        x = float(cmax)
    if not (mult > 0.0) or not (xm > 0.0):
        return 0.0
    v = x * mult * ev(pts or DEF_PTS, float(L)) * xm
    return v if v > 0.0 else 0.0


def gap_py(L, S, free=5, above=0.05, mx=3.5, below=0.05, mn=0.1, on=True):
    if not on or L < 1:
        return 1.0
    d = L - (S if S >= 0 else 0)
    if d > free:
        return min(mx, 1.0 + above * (d - free))
    if d < -free:
        return max(mn, 1.0 - below * (-d - free))
    return 1.0


def jround(x):
    return int(math.floor(x + 0.5))


def old_hard_xp(xb, L, mult=1.5, cm=3.0):
    """0.4.16 on SkyyMobs 0.1.3 Hard: maxHp = max(base, 50) x (1 + 0.08 (L-1)) (float), combatXp = scaled(clamp(round(maxHp x 0.2))),
    x class mult x (1 + 0.05 (L-1)); exact = the same without the two integer roundings"""
    import struct
    mh = struct.unpack("f", struct.pack("f", xb * (1.0 + 0.08 * (L - 1))))[0]
    raw = min(max(jround(mh * 0.2), 1), 500)
    sc = raw if mult == 1.0 else jround(raw * mult)
    return sc * cm * (1.0 + 0.05 * (L - 1)), mh * 0.2 * mult * cm * (1.0 + 0.05 * (L - 1))


def props(b):
    d = {}
    for ln in b.decode("latin-1").replace("\r\n", "\n").split("\n"):
        t = ln.strip()
        if t and not t.startswith("#") and "=" in t:
            d[t.split("=", 1)[0].strip()] = t.split("=", 1)[1].strip()
    return d


# ============================================================================================ child
def run_new(jar, out, fake):
    from jpype import JClass, JLong, JInt, JFloat, JDouble, JArray, JImplements, JOverride
    T = t15()
    res, path = T.common(jar, [fake])
    if res["load_fails"]:
        json.dump(res, open(out, "w"), indent=1)
        return
    D = res["data"]
    UUID, CHM, Props = JClass("java.util.UUID"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.Properties")
    Cfg, Xp, Store, Defs = JClass(PKG + "SkillCfg"), JClass(PKG + "SkillXp"), JClass(PKG + "SkillStore"), JClass(PKG + "SkillDefs")
    MobXp, Px, Mana, ManaFn, KMig = JClass(PKG + "MobXp"), JClass(PKG + "PartyXp"), JClass(PKG + "ManaRegen"), JClass(PKG + "ManaRegenFn"), JClass(PKG + "KillXpMig")
    Hist, CLog, Rows = JClass(PKG + "CfgHist"), JClass(PKG + "CfgLog"), JClass(PKG + "CfgRows")
    Mig, HMig, DMig, CMig, LvMig = JClass(PKG + "ManaMig"), JClass(PKG + "HealMig"), JClass(PKG + "DocMig"), JClass(PKG + "ClassManaMig"), JClass(PKG + "SkillLvMig")
    Curve, Own = JClass(PKG + "ClassCurve"), JClass(PKG + "OwnCurve")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Universe, Holder = JClass("com.hypixel.hytale.server.core.universe.Universe"), JClass("com.hypixel.hytale.component.Holder")
    FakeH, FakeW = JClass("skyytest.FakeHandler"), JClass("skyytest.FakeWorld")
    JBool, JLongC, JObj, JStr, JIntC, JDoubleC = (JClass("java.lang.Boolean"), JClass("java.lang.Long"), JClass("java.lang.Object"), JClass("java.lang.String"),
                                                  JClass("java.lang.Integer"), JClass("java.lang.Double"))
    HL = JClass("com.hypixel.hytale.logger.HytaleLogger")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def findf(c, name):
        while c is not None:
            for f in c.getDeclaredFields():
                if str(f.getName()) == name:
                    f.setAccessible(True)
                    return f
            c = c.getSuperclass()
        raise RuntimeError("no field " + name)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    def setany(obj, name, val):
        findf(obj.getClass(), name).set(obj, val)

    def alloc(cls):
        return U.allocateInstance(cls.class_)

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

    bridge = Store.bridge()
    Cfg.LOG = HL.get("SkyySkills")          # its INFO / WARN lines go to this child's stdout (the parent reads them)
    uni = alloc(Universe)
    PLAYERS, WORLDS = CHM(), CHM()
    setf(uni, Universe, "playersByUuid", PLAYERS)
    setf(uni, Universe, "players", PLAYERS.values())
    setf(uni, Universe, "worldsByUuid", WORLDS)
    setf(None, Universe, "instance", uni)
    wuid = UUID(0x3017D, 1)
    WORLDS.put(wuid, alloc(FakeW))
    handler, holder = alloc(FakeH), alloc(Holder)
    TEXTS = getf(None, FakeH, "TEXTS")

    def mkpr(u, name):
        pr = alloc(PRef)
        setf(pr, PRef, "uuid", u)
        setf(pr, PRef, "username", name)
        setf(pr, PRef, "packetHandler", handler)
        setf(pr, PRef, "worldUuid", wuid)
        setf(pr, PRef, "holder", holder)
        PLAYERS.put(u, pr)
        return pr

    def texts():
        o = [str(t) for t in TEXTS]
        TEXTS.clear()
        return o

    def fresh_store(players_dir):
        Store.DATA.clear()
        Store.DIRTY.clear()
        Store.QUIET.clear()
        Store.OWNER.clear()
        Store.PUBLISHED.clear()
        Store.DIR = path(players_dir)

    def load_cfg(d, text=None):
        f = os.path.join(d, "xp.properties")
        os.makedirs(d, exist_ok=True)
        if text is not None:
            open(f, "wb").write(text)
        elif os.path.exists(f):
            os.remove(f)
        Cfg.FILE = path(f)
        return str(Cfg.load())

    def snap(d):
        return dict((os.path.relpath(os.path.join(r, fn), d).replace(os.sep, "/"), open(os.path.join(r, fn), "rb").read())
                    for r, ds, fs in os.walk(d) for fn in fs)

    def cfg15(name):
        """the fresh 0.4.17 default file with Skyy's multiplier 1.5 (16 curve points from the file)"""
        d0 = os.path.join(SCRATCH, "c-cfg", "xp.properties")
        t0 = open(d0, "rb").read()
        assert t0.count(b"\nmultiplier=1.0\n") == 1
        return load_cfg(os.path.join(SCRATCH, name), t0.replace(b"\nmultiplier=1.0\n", b"\nmultiplier=1.5\n"))

    def safe(name, fn_):
        try:
            D[name] = fn_()
        except Exception:
            import traceback
            D[name] = {"error": traceback.format_exc()[-3000:]}
        print("[harness] section %s done" % name, flush=True)

    def mark(t):
        print("[harness-mark] " + t, flush=True)

    # ---------------------------------------------------------------- C: the fresh default file + rows
    def sec_C():
        R = {}
        work = os.path.join(SCRATCH, "c-cfg")
        R["load"] = load_cfg(work)
        R["defaults"] = open(os.path.join(work, "xp.properties"), "rb").read().decode("latin-1")
        R["block"] = str(KMig.HEAD) + str(KMig.FROM_TXT) + str(KMig.CURVE_HEAD) + str(KMig.curveLines(0.05)) + str(KMig.MANA_HEAD)
        R["consts"] = [str(KMig.MARK_ID), str(KMig.PER_DEF), str(KMig.FL_DEF), [int(x) for x in KMig.LEVELS]]
        R["mode"] = [bool(MobXp.LEVEL), int(MobXp.CURVE_N), str(MobXp.CURVE_WARNED), bool(MobXp.ON)]
        R["curve"] = [[L, float(MobXp.curve(L))] for L in range(-5, 111)]
        R["mana"] = [float(Mana.PER_LEVEL), int(Mana.FROM_LEVEL), int(Mana.IN_COMBAT)]
        R["text"] = str(MobXp.text())
        cols = ("KEYS", "LABELS", "CATS", "TYPES", "DEFS", "MINS", "MAXS", "OPTS", "UNITS", "FLAGS", "HELPS")
        arrs = [[str(x) for x in getattr(Rows, c)] for c in cols]
        rows = [list(r) for r in zip(*arrs)]
        R["rows"] = dict((r[0], r) for r in rows if r[0] in ("combat.xpFrom", "combat.levelCurve", "mana.regen.perLevel", "mana.regen.fromLevel",
                                                             "combat.levelBonus", "combat.levelXp.enabled", "combat.perHealth"))
        R["order"] = [r[0] for r in rows]
        R["n_rows"] = len(rows)
        R["fmt"] = dict((repr(x), str(KMig.fmt(x))) for x in (1.0, 1.584, 3.604, 10.0, 0.0, 0.004, 99999.0, 1.005, 2.675, 53.074, 0.105))
        R["lines01"] = str(KMig.curveLines(0.1))
        R["lines0"] = str(KMig.curveLines(0.0))
        return R
    safe("C", sec_C)

    # ---------------------------------------------------------------- CV: the curve loader, combat.xpFrom, the check= hook
    def sec_CV():
        R = {}
        cases = {
            "good": {"combat.levelCurve.1": "1", "combat.levelCurve.40": "10"},
            "bad": {"combat.levelCurve.abc": "2", "combat.levelCurve.101": "2", "combat.levelCurve.-1": "2", "combat.levelCurve.10": "0.05",
                    "combat.levelCurve.20": "2000", "combat.levelCurve.30": "x", "combat.levelCurve.0": "2", "combat.levelCurve.50": "4"},
            "dup": {"combat.levelCurve.05": "3", "combat.levelCurve.5": "9", "combat.levelCurve.10": "5"},
            "one": {"combat.levelCurve.20": "4"},
            "empty": {},
            "allbad": {"combat.levelCurve.x": "1"},
            "spaces": {"combat.levelCurve. 7": " 2.5 ", "combat.levelCurve.0007": "3"},
        }
        for name, kv in cases.items():
            p = Props()
            for k, v in kv.items():
                p.setProperty(k, v)
            MobXp.CURVE_WARNED = ""
            MobXp.LEVEL = True
            mark("CV " + name)
            MobXp.readCurve(p)
            w1 = str(MobXp.CURVE_WARNED)
            MobXp.readCurve(p)                       # the same problems again: no second WARN (the parent counts the lines)
            pts = MobXp.CURVE
            R[name] = {"n": int(MobXp.CURVE_N), "warned": w1, "null": pts is None,
                       "pts": None if pts is None else [[float(x) for x in pts[0]], [float(x) for x in pts[1]]],
                       "at": [float(MobXp.curve(L)) for L in (0, 1, 3, 5, 7, 10, 20, 40, 60, 100, 200)]}
        mark("CV end")
        xf = {}
        for v in (None, "level", "health", "HEALTH", " Health ", "lvl", ""):
            p = Props()
            if v is not None:
                p.setProperty("combat.xpFrom", v)
            mark("XF %r" % v)
            MobXp.read(p)
            xf[repr(v)] = bool(MobXp.LEVEL)
        mark("XF end")
        R["xpFrom"] = xf
        MobXp.read(Props())
        ck = {}
        for key, val in (("combat.levelCurve[40]", "14"), ("combat.levelCurve[0]", "1"), ("combat.levelCurve[100]", "60"), ("combat.levelCurve[101]", "2"),
                         ("combat.levelCurve[abc]", "2"), ("combat.levelCurve[4.5]", "2"), ("combat.levelCurve[-3]", "2"), ("combat.levelCurve[40]", "0.05"),
                         ("combat.levelCurve[40]", "1001"), ("combat.levelCurve[40]", "abc"), ("combat.levelCurve[1000]", "2")):
            r = MobXp.checkCurvePoint(key, val)
            ck[key + "=" + val] = None if r is None else str(r)
        p = Props()
        p.setProperty("combat.levelCurve.20", "4")
        MobXp.readCurve(p)
        ck["remove_last"] = str(MobXp.checkCurvePoint("combat.levelCurve[20]", None))
        p.setProperty("combat.levelCurve.40", "8")
        MobXp.readCurve(p)
        ck["remove_one_of_two"] = MobXp.checkCurvePoint("combat.levelCurve[20]", None) is None
        R["check"] = ck
        MobXp.readCurve(Props())
        return R
    safe("CV", sec_CV)

    # ---------------------------------------------------------------- X: the maths
    def sec_X():
        R = {}
        cfg15("x-cfg")
        MobXp.CURVE_WARNED = ""
        R["consts"] = [float(Cfg.MULT), float(Cfg.CLASS_MULT), float(Cfg.C_PER_HP), int(Cfg.C_MIN), int(Cfg.C_MAX), int(MobXp.CURVE_N)]
        grid = []
        for xb in XP_BASES + [1.0, 4.9, 2600.0, 3000.0]:
            for L in range(1, 61):
                for xm in (1.0, 0.70, 0.62, 0.85, 0.81):
                    grid.append([xb, L, xm, float(MobXp.lvBase(float(xb), L, xm))])
        R["grid"] = grid
        R["edge"] = [float(MobXp.lvBase(103.0, 20, 0.0)), float(MobXp.lvBase(103.0, 20, -1.0)), float(MobXp.lvBase(0.0, 20, 1.0)),
                     float(MobXp.lvBase(float("nan"), 20, 1.0))]
        Cfg.C_MIN, Cfg.C_MAX = 50, 10                                # an inverted pair pays the max (0.4.16 order)
        R["inverted"] = float(MobXp.lvBase(103.0, 1, 1.0))
        Cfg.C_MIN, Cfg.C_MAX = 1, 500
        Cfg.MULT = 0.0
        R["mult0"] = float(MobXp.lvBase(103.0, 20, 1.0))
        Cfg.MULT = 1.5
        # payD: the chance rounding
        rnd = []
        for base, f in ((151.7, 3.0), (20.6, 1.0), (10.0, 1.1), (0.3, 1.0)):
            vals = [int(MobXp.payD(DIVINITY, base, f)) for _ in range(20000)]
            rnd.append([base, f, sorted(set(vals)), sum(vals) / len(vals)])
        R["payD"] = rnd
        R["payD_edge"] = [int(MobXp.payD(DIVINITY, 0.0, 1.0)), int(MobXp.payD(DIVINITY, 10.0, 0.0)), int(MobXp.payD(DIVINITY, float("inf"), 1.0)),
                          int(MobXp.payD(DIVINITY, 10.0, float("nan"))), int(MobXp.payD(MINING, 10.0, 1.0)), int(MobXp.payD(DIVINITY, 1e16, 3.0)),
                          int(MobXp.payD(DIVINITY, 10.0 / 3.0, 3.0))]
        return R
    safe("X", sec_X)

    # ---------------------------------------------------------------- K: kill2 end to end
    def sec_K():
        R = {}
        cfg15("k-cfg")
        ENV = T.regen_env()
        EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
        em = EMc.get()
        CT = JClass("com.hypixel.hytale.component.ComponentType")
        TY = {}
        for fname in ("playerComponentType", "uuidComponentType", "transformComponentType"):
            TY[fname] = alloc(CT)
            setany(em, fname, TY[fname])
        TY["playerRef"] = alloc(CT)
        setany(uni, "playerRefComponentType", TY["playerRef"])
        TY["stats"] = ENV["statsType"]
        EST = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
        WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
        PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
        GM = JClass("com.hypixel.hytale.protocol.GameMode")
        ESMc, ESVc = ENV["ESM"], ENV["ESV"]
        Ref = JClass("com.hypixel.hytale.component.Ref")
        AtomicRef = JClass("java.util.concurrent.atomic.AtomicReference")
        TRC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
        UUC = JClass("com.hypixel.hytale.server.core.entity.UUIDComponent")
        MapStore = JClass("skyytest.MapStore")
        IHM, AL = JClass("java.util.IdentityHashMap"), JClass("java.util.ArrayList")

        def world(name):
            w = alloc(FakeW)
            setf(w, WLD, "name", name)
            es = alloc(EST)
            setf(es, EST, "world", w)
            return w, es

        def health(mx):
            esm = alloc(ESMc)
            hv = alloc(ESVc)
            for nm, v in (("id", "Health"), ("index", JInt(0)), ("value", JFloat(mx)), ("min", JFloat(0.0)), ("max", JFloat(mx))):
                setany(hv, nm, v)
            setany(esm, "values", JArray(ESVc)([hv]))
            return esm

        def player(mode="Adventure"):
            p = alloc(PLA)
            setany(p, "gameMode", getattr(GM, mode))
            setany(p, "waitingForClientReady", AtomicRef())
            setany(p, "currentFallDistance", JDouble(0.0))
            return p

        def put(store, ref, typ, comp):
            m = store.comps.get(ref)
            if m is None:
                m = IHM()
                store.comps.put(ref, m)
            m.put(typ, comp)

        def mkstore(es):
            st = alloc(MapStore)
            st.comps = IHM()
            st.ext = es
            st.events = AL()
            return st
        wK, esK = world("default")
        stK = mkstore(esK)
        npc = Ref(stK, 7)
        un = UUID(0x317, 33)
        put(stK, npc, TY["uuidComponentType"], UUC(un))
        CALLS = []
        INFO = {"v": None, "throw": False}

        @JImplements("java.util.function.Function")
        class Info(object):
            @JOverride
            def apply(self, o):
                CALLS.append([str(o[0]), str(o[1])])
                if INFO["throw"]:
                    raise RuntimeError("info boom")
                return INFO["v"]

        def info(level, base, xb, hp, dmg, xm):
            return JArray(JObj)([JIntC.valueOf(JInt(level)), JDoubleC.valueOf(float(base)), JDoubleC.valueOf(float(xb)), JDoubleC.valueOf(float(hp)),
                                 JDoubleC.valueOf(float(dmg)), JDoubleC.valueOf(float(xm))])
        bridge.put("class:fn:allowed", Const(JBool.TRUE))

        def member(n, cls_, slot, lvl, pos, mode="Adventure"):
            u = UUID(0x9A47, n)
            pr = mkpr(u, "M%d" % n)
            r = Ref(stK, 100 + n)
            setany(pr, "entity", r)
            put(stK, r, TY["playerComponentType"], player(mode))
            tc = TRC()
            tc.getPosition().set(float(pos[0]), float(pos[1]), float(pos[2]))
            put(stK, r, TY["transformComponentType"], tc)
            put(stK, r, TY["stats"], health(100.0))
            bridge.put("class:" + str(u), cls_)
            return {"u": u, "pr": pr, "r": r, "slot": slot, "lvl": lvl, "cls": cls_}
        fresh_store(os.path.join(SCRATCH, "k-players"))
        os.makedirs(os.path.join(SCRATCH, "k-players"), exist_ok=True)
        killer = member(0, "Priest", DIVINITY, 20, (0, 64, 0))
        mlist = [member(1, "Archer", ARCHERY, 1, (10, 64, 0)), member(2, "Warrior", WARRIOR, 30, (0, 64, 20)), member(3, "Priest", DIVINITY, 40, (30, 70, 30)),
                 member(4, "Archer", ARCHERY, 60, (-20, 64, -20)), member(5, "Archer", ARCHERY, 1, (60, 64, 0)), member(6, "Warrior", WARRIOR, 1, (5, 64, 5), "Creative")]
        ids_ = JArray(JStr)([str(killer["u"])] + [str(m["u"]) for m in mlist])
        bridge.put("party:fn:members", Const(ids_))

        def setlvl(m, lvl):
            d = Store.data(m["u"])
            cum = [int(x) for x in Defs.cumOf(m["slot"])]
            d[m["slot"]] = cum[lvl]
            d[N + m["slot"]] = lvl
            m["lvl"] = lvl

        def xp_of(m):
            return int(Store.data(m["u"])[m["slot"]])

        def reset_all():
            for m in [killer] + mlist:
                setlvl(m, m["lvl"])

        def run(name, runs=300, role=None, maxhp=359.36):
            reset_all()
            levels = [int(Store.level(m["u"], m["slot"])) for m in [killer] + mlist]
            kc, gains = [], [[] for _ in mlist]
            for _ in range(runs):
                reset_all()
                before = [xp_of(m) for m in mlist]
                k0 = xp_of(killer)
                cx = int(MobXp.kill2(killer["pr"], killer["r"], stK, DIVINITY, role, JFloat(maxhp), npc))
                kc.append([cx, xp_of(killer) - k0])
                for i, m in enumerate(mlist):
                    gains[i].append(xp_of(m) - before[i])
            R[name] = {"levels": levels, "killer": kc, "gains": gains}
            texts()
        # level mode, Hard share, killer Divinity 20 vs a Lv 20 wolf class (spec test step 7: ~455 with x1.5)
        bridge.remove("mob:fn:level")
        bridge.put("mob:fn:info", Info())
        INFO["v"] = info(20, 103.0, 103.0, 4.91, 1.76, 1.0)
        run("lv_hard")
        R["calls"] = CALLS[:1]
        INFO["v"] = info(20, 103.0, 103.0, 3.4, 1.4, 0.6944)
        run("lv_easy")
        # the gap: the killer at Divinity 5 vs the Lv 20 mob (d 15 -> x1.5); the part off -> no gap, the curve stays
        INFO["v"] = info(20, 103.0, 103.0, 4.91, 1.76, 1.0)
        killer["lvl"] = 5
        run("lv_gap")
        MobXp.ON = False
        run("lv_partoff")
        MobXp.ON = True
        killer["lvl"] = 20
        # a custom curve (an admin's table): Lv 20 x10
        p = Props()
        p.setProperty("combat.levelCurve.1", "1")
        p.setProperty("combat.levelCurve.20", "10")
        MobXp.readCurve(p)
        run("lv_custom", runs=100)
        MobXp.readCurve(Props())
        # health mode with mob:fn:info present: 0.4.16 exactly (mob:fn:level answers 33)
        bridge.put("mob:fn:level", Const(JIntC.valueOf(JInt(33))))
        MobXp.LEVEL = False
        n0 = len(CALLS)
        run("health_mode")
        R["health_calls"] = len(CALLS) - n0
        MobXp.LEVEL = True
        # no mob:fn:info (SkyyMobs 0.1.3): 0.4.16 exactly
        bridge.remove("mob:fn:info")
        run("no_info_fn")
        bridge.put("mob:fn:info", Info())
        # info answers null / throws / malformed: classXp(the health-mode base), no level factor (mob:fn:level's 33 is NOT used)
        INFO["v"] = None
        run("info_null")
        INFO["throw"] = True
        f0 = bool(MobXp.INFO_FAILED_ONCE)
        mark("K info throw")
        run("info_throw", runs=50)
        R["info_throw_flag"] = [f0, bool(MobXp.INFO_FAILED_ONCE)]
        INFO["throw"] = False
        mal = {}
        for nm, v in (("short", JArray(JObj)([JIntC.valueOf(JInt(20)), JDoubleC.valueOf(103.0)])), ("level0", info(0, 103, 103, 1, 1, 1)),
                      ("xb0", info(20, 103, 0, 1, 1, 1)), ("string", "20"), ("nan_xm", info(20, 103, 103, 4.91, 1.76, float("nan"))),
                      ("neg_xm", info(20, 103, 103, 4.91, 1.76, -2.0)), ("big_xm", info(20, 103, 103, 4.91, 1.76, 500.0)),
                      ("five", JArray(JObj)([JIntC.valueOf(JInt(20)), JDoubleC.valueOf(103.0), JDoubleC.valueOf(103.0), JDoubleC.valueOf(4.91), JDoubleC.valueOf(1.76)])),
                      ("long_level", JArray(JObj)([JLongC.valueOf(JLong(20)), JDoubleC.valueOf(103.0), JIntC.valueOf(JInt(103))])),
                      ("inf_xb", info(20, 103, float("inf"), 1, 1, 1))):
            INFO["v"] = v
            d0 = MobXp.infoOf(stK, npc)
            mal[nm] = None if d0 is None else [float(x) for x in d0]
        R["malformed"] = mal
        R["info_nulls"] = [MobXp.infoOf(None, npc) is None, MobXp.infoOf(stK, None) is None]
        npc2 = Ref(stK, 8)                                         # no UUIDComponent
        INFO["v"] = info(20, 103, 103, 1, 1, 1)
        R["info_no_uuidc"] = MobXp.infoOf(stK, npc2) is None
        # a role override: 0.4.16's maths (scaled(50) = 75 x 3 x levelFactor(20) x gap) - never the curve; part off = classXp
        rl = Props()
        rl.setProperty("multiplier", "1.5")
        rl.setProperty("combat.role.Skeleton_Test", "50")
        load_cfg(os.path.join(SCRATCH, "k-cfg2"), b"multiplier=1.5\ncombat.role.Skeleton_Test=50\n")
        INFO["v"] = info(20, 103.0, 103.0, 4.91, 1.76, 1.0)
        run("role", role="Skeleton_Test")
        MobXp.ON = False
        run("role_off", role="Skeleton_Test")
        MobXp.ON = True
        # the first kill of a role: the log line gains "(Lv 1 health 103)" (the parent reads it from this child's stdout)
        Cfg.SEEN_ROLES.clear()
        mark("K first kill")
        run("first_kill", runs=2, role="Wolf_Black", maxhp=505.73)
        INFO["v"] = None
        Cfg.SEEN_ROLES.clear()
        mark("K first kill null")
        run("first_kill_null", runs=1, role="Wolf_White", maxhp=505.73)
        mark("K end")
        INFO["v"] = info(20, 103.0, 103.0, 4.91, 1.76, 1.0)
        R["text_lv"] = str(MobXp.text())
        MobXp.LEVEL = False
        R["text_hp"] = str(MobXp.text())
        MobXp.LEVEL = True
        R["fraction"] = float(JClass(PKG + "PartyCfg").FRACTION)
        # the old signatures still work (one2 / share2 delegate with lvb -1)
        reset_all()
        b0 = [xp_of(m) for m in mlist]
        Px.share2(killer["pr"], killer["r"], stK, JLong(108), DIVINITY, JLong(36), -1)
        R["old_share2"] = [xp_of(m) - b for m, b in zip(mlist, b0)]
        bridge.remove("party:fn:members")
        bridge.remove("mob:fn:info")
        bridge.remove("mob:fn:level")
        return R
    safe("K", sec_K)

    # ---------------------------------------------------------------- R: Mana regen per class level
    def sec_R():
        R = {}
        load_cfg(os.path.join(SCRATCH, "r-cfg"))
        fresh_store(os.path.join(SCRATCH, "r-players"))
        os.makedirs(os.path.join(SCRATCH, "r-players"), exist_ok=True)
        u = UUID(0x4E6E, 1)
        bridge.put("class:" + str(u), "Priest")
        d = Store.data(u)
        cum = [int(x) for x in Defs.cumOf(DIVINITY)]
        tab = []
        for lv in (0, 1, 19, 20, 21, 25, 30, 40, 49, 60, 100):
            d[DIVINITY] = cum[lv]
            tab.append([lv, int(Store.level(u, DIVINITY)), float(Mana.classPct(u)), float(Mana.total(u))])
        R["table"] = tab
        d[DIVINITY] = cum[30]
        Mana.SRC.clear()
        R["no_src"] = [float(Mana.total(u)), [str(x) for x in Mana.sources(u)]]
        Mana.put(u, "Test", 20.0)
        R["with_src"] = [float(Mana.total(u)), [str(x) for x in Mana.sources(u)]]
        R["compact"] = str(Mana.compact(Mana.total(u), Mana.sources(u), JFloat(5.0), 50))
        R["show"] = [str(x) for x in Mana.showAction(u, "Skyy")]
        R["text"] = str(Mana.text(u))
        fn = ManaFn()
        R["bridge"] = [float(fn.apply(JArray(JObj)(["get", u]))), [str(x) for x in fn.apply(JArray(JObj)(["sources", u]))]]
        Mana.remove(u, "Test")
        Mana.PER_LEVEL = 100.0
        d[DIVINITY] = cum[100]
        R["clamp"] = [float(Mana.classPct(u)), float(Mana.total(u))]
        Mana.PER_LEVEL = 0.0
        R["off"] = [float(Mana.classPct(u)), float(Mana.total(u)), [str(x) for x in Mana.sources(u)]]
        Mana.PER_LEVEL, Mana.FROM_LEVEL = 7.0, 20
        d[DIVINITY] = cum[30]
        R["fromlevel"] = []
        for fl in (0, 25, 30, 100):
            Mana.FROM_LEVEL = fl
            R["fromlevel"].append([fl, float(Mana.classPct(u))])
        Mana.FROM_LEVEL = 20
        bridge.remove("class:" + str(u))
        R["no_class"] = [float(Mana.classPct(u)), float(Mana.total(u))]
        bridge.put("class:" + str(u), "Warrior")             # another class: its OWN class skill (Swordsmanship, level 0 here)
        R["other_class"] = float(Mana.classPct(u))
        bridge.put("class:" + str(u), "Priest")
        # an offline profile with a file on disk: never read from here (DATA stays without it)
        u2 = UUID(0x4E6E, 2)
        open(os.path.join(SCRATCH, "r-players", str(u2) + ".properties"), "wb").write(b"name=Off\nDivinity=99999999\n")
        bridge.put("class:" + str(u2), "Priest")
        R["offline"] = [float(Mana.classPct(u2)), bool(Store.DATA.containsKey(str(u2)))]
        R["null"] = [float(Mana.classPct(None)), float(Mana.total(None))]
        # the REAL ManaRegen.tick (the 0.4.15 stand-ins): 30 ticks of 1/30 s out of combat, then 30 in combat; SkyySkills' own additions
        ENV = T.regen_env()
        from jpype import JFloat as JF
        Instant = ENV["Instant"]
        ChronoUnit = JClass("java.time.temporal.ChronoUnit")
        tr, store, cb, fsm, mv, dd2 = ENV["tr"], ENV["store"], ENV["cb"], ENV["fsm"], ENV["mv"], ENV["dd2"]
        ESV = ENV["ESV"]

        def second(lv, hit):
            d[DIVINITY] = cum[lv]
            Mana.CLK.clear()
            Mana.SRC.clear()
            Mana.IN_COMBAT = 50
            dd2.setLastDamageTime(Instant.MIN)
            ENV["charging"].v = True
            setf(mv, ESV, "value", JF(2.0))
            setf(mv, ESV, "max", JF(1000.0))
            dt = JF(1.0 / 30.0)
            nanos = JLong(int(float(dt) * 1.0e9))
            tot = 0.0
            for t in range(31):
                tr.add(nanos, ChronoUnit.NANOS)
                if hit:
                    dd2.setLastDamageTime(tr.getNow())
                c0 = int(fsm.calls)
                Mana.tick(u, store, cb, None, dt)
                if int(fsm.calls) != c0:
                    tot += float(fsm.last)
                    setf(mv, ESV, "value", JF(min(1000.0, float(mv.get()) + float(fsm.last))))
            return round(tot, 4)
        R["tick"] = dict(("%d_%s" % (lv, "in" if hit else "out"), second(lv, hit)) for lv in (20, 30, 40) for hit in (False, True))
        R["tick_warn"] = bool(Mana.FAILED_ONCE)
        return R
    safe("R", sec_R)

    # ---------------------------------------------------------------- MG: KillXpMig on file shapes
    def sec_MG():
        R = {}
        live = open(LIVE, "rb").read()
        shapes = {
            "live": live,
            "crlf": live.replace(b"\n", b"\r\n"),
            "nofinal": live.rstrip(b"\n"),
            "bonus01": live.replace(b"combat.levelBonus=0.05", b"combat.levelBonus=0.1"),
            "partoff": live.replace(b"combat.levelXp.enabled=true", b"combat.levelXp.enabled=false"),
            "admin_from": live + b"combat.xpFrom=health\n",
            "admin_curve": live + b"combat.levelCurve.10=3\n",
            "admin_per": live + b"mana.regen.perLevel=5\n",
            "all": live + b"combat.xpFrom=level\ncombat.levelCurve.1=1\nmana.regen.perLevel=7\nmana.regen.fromLevel=20\n",
            "marker": live + b"# ---------- " + KXP_MARK_ID.encode() + b" ----------\n",
            "backslash": live + b"multiplier.note=x\\",
            "empty": b"",
            "nobonus": b"multiplier=1.0\n",
        }
        for name, data in shapes.items():
            d = os.path.join(SCRATCH, "mg-" + name)
            os.makedirs(d, exist_ok=True)
            f = os.path.join(d, "xp.properties")
            open(f, "wb").write(data)
            Cfg.FILE = path(f)
            Hist.DIR = None
            Rows.HOME = None
            CLog.FILE = None
            CLog.Q.clear()
            r1 = str(KMig.run())
            b1 = open(f, "rb").read()
            s1 = snap(d)
            r2 = str(KMig.run())
            b2 = open(f, "rb").read()
            hist = [k for k in s1 if k.startswith("config-history/") and k.endswith(".bak")]
            R[name] = {"r1": r1, "r2": r2, "new": b1.decode("latin-1"), "same2": b1 == b2, "hist_old": any(s1[k] == data for k in hist), "n_hist": len(hist),
                       "log": s1.get("config-changes.log", b"").decode("utf-8")}
        return R
    safe("MG", sec_MG)

    # ---------------------------------------------------------------- M: start twice on the live copy
    def start(d):
        Cfg.FILE = path(os.path.join(d, "xp.properties"))
        fresh_store(os.path.join(d, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        r = {"mana": [str(x) for x in Mig.run()], "heal": str(HMig.run()), "doc": str(DMig.run()), "cmig": str(CMig.run()), "lvmig": str(LvMig.run()),
             "kxmig": str(KMig.run())}
        r["load"] = str(Cfg.load())
        r["curve"] = str(Curve.start(path(d)))
        r["own"] = str(Own.start(path(d)))
        r["mode"] = [bool(MobXp.LEVEL), int(MobXp.CURVE_N), float(MobXp.curve(20)), float(MobXp.curve(40)), float(Mana.PER_LEVEL), int(Mana.FROM_LEVEL),
                     float(Cfg.MULT), float(Cfg.CLASS_MULT)]
        return r

    def sec_M():
        R = {}
        lc = os.path.join(SCRATCH, "live-copy")
        s0 = snap(lc)
        R["r1"] = start(lc)
        s1 = snap(lc)
        R["r2"] = start(lc)
        s2 = snap(lc)
        R["changed1"] = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
        R["changed2"] = sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k))
        R["xp0"] = s0["xp.properties"].decode("latin-1")
        R["xp1"] = s1["xp.properties"].decode("latin-1")
        R["log_new"] = s1.get("config-changes.log", b"").decode("utf-8")[len(s0.get("config-changes.log", b"").decode("utf-8")):]
        R["hist_new"] = [k for k in s1 if k.startswith("config-history/") and k not in s0]
        R["hist_old"] = any(s1[k] == s0["xp.properties"] for k in R["hist_new"])
        R["n_bak"] = sum(1 for k in s1 if k.startswith("config-history/") and k.endswith(".bak"))
        return R
    safe("M", sec_M)

    # ---------------------------------------------------------------- KC: the rows through the real config kit
    def sec_KC():
        R = {}
        CfgPub = JClass(PKG + "CfgPub")
        OA = JArray(JObj)
        Paths, JStrA = JClass("java.nio.file.Paths"), JArray(JStr)
        kmods = os.path.join(SCRATCH, "kc")
        khome = os.path.join(kmods, "Skyy_SkyySkills")
        os.makedirs(os.path.join(khome, "players"), exist_ok=True)
        kf = os.path.join(khome, "xp.properties")
        open(kf, "wb").write(open(LIVE, "rb").read())
        Cfg.FILE = path(kf)
        fresh_store(os.path.join(khome, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        R["mig"] = str(KMig.run())
        Cfg.load()
        CfgPub.start(Paths.get(kmods, JStrA([])), None)
        fn = bridge.get("config:fn:SkyySkills")

        def op(*a):
            r = fn.apply(OA(list(a)))
            return None if r is None else [None if x is None else str(x) for x in list(r)[:3]]

        def keys():
            ks = fn.apply(OA(["keys", "combat.levelCurve", ""]))
            return [[str(x) for x in ks[0]], [str(x) for x in ks[2]]]
        R["keys1"] = keys()
        R["get_from"] = str(fn.apply(OA(["get", "combat.xpFrom"])))
        R["tset40"] = op("tset", "combat.levelCurve", "40", "14", None, "console", "yes", "console")
        CfgPub.flush()
        R["after_tset"] = [float(MobXp.curve(40)), float(MobXp.curve(42)), "combat.levelCurve.40=14" in open(kf, "rb").read().decode("latin-1")]
        R["add101"] = op("add", "combat.levelCurve", "101", "2", None, "console", "yes", "console")
        R["addabc"] = op("add", "combat.levelCurve", "abc", "2", None, "console", "yes", "console")
        R["addlow"] = op("add", "combat.levelCurve", "55", "0.05", None, "console", "yes", "console")
        R["add55"] = op("add", "combat.levelCurve", "55", "20", None, "console", "yes", "console")
        CfgPub.flush()
        R["after_add"] = [float(MobXp.curve(55)), int(MobXp.CURVE_N)]
        R["rm55"] = op("remove", "combat.levelCurve", "55", None, "console", "yes", "console")
        CfgPub.flush()
        R["after_rm"] = [float(MobXp.curve(55)), int(MobXp.CURVE_N)]
        R["set_health"] = op("set", "combat.xpFrom", "Mob health", None, "console", "yes", "console")
        CfgPub.flush()
        R["after_health"] = [bool(MobXp.LEVEL), "combat.xpFrom=health" in open(kf, "rb").read().decode("latin-1")]
        R["set_bad"] = op("set", "combat.xpFrom", "sometimes", None, "console", "yes", "console")
        R["undo"] = op("set", "combat.xpFrom", "level", None, "console", "yes", "console")
        CfgPub.flush()
        R["after_undo"] = bool(MobXp.LEVEL)
        R["set_per"] = op("set", "mana.regen.perLevel", "10", None, "console", "yes", "console")
        R["set_from"] = op("set", "mana.regen.fromLevel", "25", None, "console", "yes", "console")
        R["set_per_bad"] = op("set", "mana.regen.perLevel", "150", None, "console", "yes", "console")
        CfgPub.flush()
        R["after_mana"] = [float(Mana.PER_LEVEL), int(Mana.FROM_LEVEL)]
        lg = [str(x) for x in fn.apply(OA(["log", JIntC(50)]))]
        R["log"] = [ln for ln in lg if "combat.xpFrom" in ln or "combat.levelCurve" in ln or "mana.regen" in ln]
        CfgPub.shutdown()
        return R
    safe("KC", sec_KC)
    json.dump(res, open(out, "w"), indent=1)


def run_audit(jar, fake, out):
    T = t15()
    return T.run_audit(jar, fake, out)


# ============================================================================================ parent
def within(vals, x, tol_mean):
    lo, hi = math.floor(x + 1e-9), math.ceil(x - 1e-9)
    ok_range = all(lo <= v <= hi for v in vals)
    mean = sum(vals) / float(len(vals)) if vals else 0.0
    ok_mean = abs(mean - x) <= max(tol_mean * x, 0.5)
    return ok_range and ok_mean, mean


def main():
    if "--mkfake" in sys.argv:
        return t15().run_mkfake(arg("--mkfake"))
    if "--new-run" in sys.argv:
        return run_new(arg("--new-run"), arg("--out"), arg("--fake"))
    if "--audit" in sys.argv:
        return run_audit(arg("--audit"), arg("--fake"), arg("--out"))
    for j in (JAR, PREV_JAR):
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
    live_snap = dict((os.path.relpath(os.path.join(r, f), LIVE_DIR), os.path.getmtime(os.path.join(r, f))) for r, ds, fs in os.walk(LIVE_DIR) for f in fs)
    shutil.copytree(LIVE_DIR, os.path.join(SCRATCH, "live-copy"))
    lp = props(open(LIVE, "rb").read())
    check(not any(k.startswith("combat.levelCurve") or k in ("combat.xpFrom", "mana.regen.perLevel", "mana.regen.fromLevel") for k in lp)
          and KXP_MARK_ID not in open(LIVE, "rb").read().decode("latin-1") and "levels.skill.Mining" in lp,
          "the live xp.properties is 0.4.16's (no 0.4.17 line, the 0.4.16 Mining list present)")
    me = os.path.abspath(__file__)
    fake = os.path.join(SCRATCH, "fake")
    p = subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(os.path.join(fake, "skyytest", "FakeHandler.class")), "the stand-in classes were generated")
    outp = os.path.join(SCRATCH, "run-new.json")
    logp = os.path.join(SCRATCH, "run-new.log")
    with open(logp, "wb") as lf:
        p = subprocess.run([sys.executable, me, "--new-run", JAR, "--out", outp, "--fake", fake, "--dir", SCRATCH], env=env, stdout=lf, stderr=subprocess.STDOUT)
    check(p.returncode == 0 and os.path.isfile(outp), "child JVM ran (log %s)" % logp)
    auo = os.path.join(SCRATCH, "audit.json")
    pa = subprocess.run([sys.executable, me, "--audit", JAR, "--fake", fake, "--out", auo, "--dir", SCRATCH], env=env, capture_output=True)
    check(pa.returncode == 0 and os.path.isfile(auo), "engine-access audit child ran: %s" % pa.stderr[-500:])
    if FAILS:
        return finish()
    res = json.load(open(outp))
    LOG = open(logp, "rb").read().decode("utf-8", "replace")
    check(not res["load_fails"] and res["loaded"] == res["classes"], "A: %d / %d classes load under -Xverify:all %s" % (res["loaded"], res["classes"], res["load_fails"][:3]))
    D = res["data"]
    for k in ("C", "CV", "X", "K", "R", "MG", "M", "KC"):
        check(k in D and "error" not in D[k], "section %s ran: %s" % (k, (D.get(k) or {}).get("error")))
    if FAILS:
        return finish()

    def logpart(a, b):
        i = LOG.find("[harness-mark] " + a)
        j = LOG.find("[harness-mark] " + b, i + 1)
        return LOG[i:j] if i >= 0 and j > i else ""
    # ---------------------------------------------------------------- C
    C = D["C"]
    kdef = kxp_curve(0.05)
    block = C["block"] + "mana.regen.perLevel=7\nmana.regen.fromLevel=20\n"
    check(C["defaults"].endswith("\n\n" + block) and C["defaults"].count(KXP_MARK_ID) == 1,
          "C: the fresh default file ends with the KXP block (blank line before it, the marker once) = KillXpMig's own parts")
    check(all(("\ncombat.levelCurve.%d=%s\n" % (L, v)) in C["defaults"] for L, v in kdef) and "\ncombat.xpFrom=level\n" in C["defaults"],
          "C: the default file holds the 16 model points (1, 1.58, 2.49 ... 53.07) and combat.xpFrom=level")
    check(C["consts"] == [KXP_MARK_ID, "7", "20", KXP_LEVELS], "C: KillXpMig constants: %s" % C["consts"])
    check(C["mode"][:3] == [True, 16, ""] and C["mode"][3], "C: after the load: Mob level mode, 16 points from the file, no WARN, part on: %s" % C["mode"])
    bad = [(L, v) for L, v in C["curve"] if v != ev(DEF_PTS, float(L))]
    check(not bad, "C: MobXp.curve(L) = the Python model bit for bit at levels -5..110: %s" % bad[:4])
    check(C["mana"] == [7.0, 20, 50], "C: ManaRegen PER_LEVEL 7 / FROM_LEVEL 20 (in combat 50 %%): %s" % C["mana"])
    rw = C["rows"]
    check(rw["combat.xpFrom"][1:9] == ["Kill XP comes from", "combat", "choice", "level", "", "", "level|Mob level,health|Mob health", ""]
          and rw["combat.levelCurve"][1:9] == ["Kill XP level curve", "combat", "table", "", "0.1", "1000", "dec;none;Factor", ""]
          and rw["mana.regen.perLevel"][1:9] == ["Mana regen per class level", "overall", "dec", "7", "0", "100", "", "%"]
          and rw["mana.regen.fromLevel"][1:9] == ["Mana regen growth starts at", "overall", "int", "20", "0", "100", "", ""]
          and rw["combat.levelBonus"][1] == "Health mode: XP per mob level" and rw["combat.levelBonus"][10].startswith("Mob health mode only")
          and rw["combat.levelXp.enabled"][10].startswith("Mob level mode: the level gap XP rows") and "Lv 1 health" in rw["combat.perHealth"][10],
          "C: the 4 new rows + the relabelled rows (spec 6.3): %s" % json.dumps(rw)[:400])
    o = C["order"]
    check(o[o.index("combat.gap.min") + 1:o.index("combat.gap.min") + 3] == ["combat.xpFrom", "combat.levelCurve"]
          and o[o.index("mana.regen.inCombat") + 1:o.index("mana.regen.inCombat") + 3] == ["mana.regen.perLevel", "mana.regen.fromLevel"] and C["n_rows"] == 201,
          "C: row places (after the gap rows / after in-combat regen), 201 rows")
    check("Mana regen +7% per class level above 20" in C["load"] and "kill XP from the mob level (Lv 1 health x the level curve: Lv 20 x4.91, Lv 40 x12.15, 16 points x the difficulty share" in C["load"],
          "C: the load summary names both: %s" % C["load"][-400:])
    fm = C["fmt"]
    check(fm["1.0"] == "1" and fm["1.584"] == "1.58" and fm["3.604"] == "3.6" and fm["10.0"] == "10" and fm["0.0"] == "0.1" and fm["99999.0"] == "1000"
          and all(fm[k] == kxp_fmt(float(k)) for k in fm), "C: KillXpMig.fmt = the Python formatter (incl. the 0.1 / 1000 clamps): %s" % fm)
    check(C["lines01"] == "".join("combat.levelCurve.%d=%s\n" % (L, v) for L, v in kxp_curve(0.1))
          and C["lines0"] == "".join("combat.levelCurve.%d=%s\n" % (L, v) for L, v in kxp_curve(0.0)),
          "C: Java curveLines(0.1) / (0) = the Python generator (a hand-set bonus / the part off)")
    print("C. default file block, 16 points = model, rows, Mana 7 / 20, load summary")
    # ---------------------------------------------------------------- CV
    CV = D["CV"]
    check(CV["good"]["n"] == 2 and CV["good"]["pts"] == [[1.0, 40.0], [1.0, 10.0]] and CV["good"]["warned"] == ""
          and CV["good"]["at"][:3] == [1.0, 1.0, 1.0 + 9.0 * 2 / 39] and CV["good"]["at"][-1] == 10.0, "CV good: 2 points, straight line, flat outside: %s" % CV["good"])
    w = CV["bad"]["warned"]
    check(CV["bad"]["n"] == 2 and CV["bad"]["pts"] == [[0.0, 50.0], [2.0, 4.0]] and all(x in w for x in ("abc is not a mob level", "101 is not a mob level",
          "-1 is not a mob level", "level 10: not a factor", "level 20: not a factor", "level 30: not a factor")),
          "CV bad: only levels 0 and 50 kept, each problem named: %s / %s" % (CV["bad"]["pts"], w))
    check(CV["dup"]["n"] == 2 and CV["dup"]["pts"] == [[5.0, 10.0], [3.0, 5.0]] and "level 5 is listed twice (5 left out)" in CV["dup"]["warned"],
          "CV 05 + 5: the first in sort order (05) wins: %s" % CV["dup"])
    check(CV["one"]["n"] == 1 and all(v == 4.0 for v in CV["one"]["at"]), "CV one point: flat everywhere")
    check(CV["empty"]["n"] == 0 and CV["empty"]["null"] and "no usable entry" in CV["empty"]["warned"] and CV["empty"]["at"][6] == 4.91
          and CV["allbad"]["n"] == 0 and CV["allbad"]["null"] and CV["allbad"]["at"][7] == 12.15,
          "CV empty / all bad: the default curve + one WARN: %s" % CV["empty"]["warned"])
    check(CV["spaces"]["n"] == 1 and CV["spaces"]["pts"] == [[7.0], [2.5]] and "0007 is not a mob level" in CV["spaces"]["warned"], "CV ' 7' (trimmed) / '0007' (4 digits refused): %s" % CV["spaces"])
    for nm in ("bad", "dup", "allbad", "spaces"):   # the logger's lines are not ordered with print(): count them whole ("empty"'s text is also every later empty load's)
        w_ = "Kill XP level curve: " + CV[nm]["warned"][len("Kill XP level curve: "):]
        n_ = sum(1 for ln_ in LOG.splitlines() if ln_.endswith(w_))
        check(n_ == 1, "CV %s: the WARN once for two identical loads (%d)" % (nm, n_))
    check(CV["xpFrom"] == {"None": True, "'level'": True, "'health'": False, "'HEALTH'": False, "' Health '": False, "'lvl'": True, "''": True}
          and LOG.count("combat.xpFrom=lvl is not level or health - using level") == 1 and LOG.count("combat.xpFrom= is not level or health - using level") == 1,
          "CV combat.xpFrom parsing (+ one WARN each for 'lvl' and ''): %s" % CV["xpFrom"])
    ck = CV["check"]
    check(ck["combat.levelCurve[40]=14"] is None and ck["combat.levelCurve[0]=1"] is None and ck["combat.levelCurve[100]=60"] is None
          and all("whole number 0 to 100" in (ck[k] or "") for k in ("combat.levelCurve[101]=2", "combat.levelCurve[abc]=2", "combat.levelCurve[4.5]=2",
                                                                   "combat.levelCurve[-3]=2", "combat.levelCurve[1000]=2"))
          and all("0.1 to 1000" in (ck[k] or "") for k in ("combat.levelCurve[40]=0.05", "combat.levelCurve[40]=1001", "combat.levelCurve[40]=abc"))
          and "Keep at least one point" in ck["remove_last"] and ck["remove_one_of_two"], "CV check= hook: %s" % ck)
    print("CV. curve loader (bad / duplicate / empty -> default + one WARN), combat.xpFrom, check= hook")
    # ---------------------------------------------------------------- X
    X = D["X"]
    check(X["consts"] == [1.5, 3.0, 0.2, 1, 500, 16], "X: the file's multiplier 1.5, class mult 3, perHealth 0.2, min 1, max 500, 16 points: %s" % X["consts"])
    bad = [g for g in X["grid"] if g[3] != lvbase_py(g[0], g[1], g[2])]
    check(not bad, "X: lvBase = the Python model bit for bit on %d cases: %s" % (len(X["grid"]), bad[:3]))
    worst_exact, worst_round = (0.0, None), (0.0, None)
    for xb in XP_BASES:
        for L in range(1, 61):
            new = lvbase_py(xb, L, 1.0) * 3.0
            rounded, exact = old_hard_xp(xb, L)
            e1, e2 = abs(new / exact - 1.0), abs(new / rounded - 1.0)
            if e1 > worst_exact[0]:
                worst_exact = (e1, (xb, L, round(exact, 2), round(new, 2)))
            if e2 > worst_round[0]:
                worst_round = (e2, (xb, L, round(rounded, 2), round(new, 2)))
    check(worst_exact[0] <= 0.012, "X: Hard level mode vs 0.4.16's exact Hard XP product (x1.5): worst %.2f%% at %s (the curve's interpolation)" % (worst_exact[0] * 100, worst_exact[1]))
    check(worst_round[0] <= 0.051, "X: vs 0.4.16's integer-rounded chain: worst %.2f%% at %s (0.4.16 rounded max health x 0.2 and x1.5 to whole numbers)" % (worst_round[0] * 100, worst_round[1]))
    hi10 = max(abs(lvbase_py(xb, L, 1.0) * 3.0 / old_hard_xp(xb, L)[0] - 1.0) for xb in XP_BASES for L in range(20, 61))
    check(hi10 <= 0.021, "X: from Lv 20 within 2.1%% of 0.4.16 for every vanilla base (%.2f%%)" % (hi10 * 100))
    spec43 = {(1, 103): 62, (10, 103): 154, (20, 103): 303, (33, 103): 573, (40, 103): 751, (60, 103): 1396, (20, 226): 666, (40, 226): 1648,
              (60, 226): 3063, (20, 50): 147, (49, 103): 1018}
    got43 = dict((k, round(lvbase_py(k[1], k[0], 1.0, mult=1.0) * 3.0)) for k in spec43)
    check(all(abs(got43[k] - v) <= 1 for k, v in spec43.items()), "X: spec 4.3 'new' column (x1.0) within 1 XP: %s" % got43)
    check(X["edge"] == [0.0, 0.0, 1.0 * 1.5 * 4.91, 1.0 * 1.5 * 4.91] and X["inverted"] == 10.0 * 1.5 and X["mult0"] == 0.0,
          "X: xpMult 0 / negative = 0 XP; xpBase 0 / NaN -> combat.min; an inverted min / max pays the max; multiplier 0 = 0: %s %s %s" % (X["edge"], X["inverted"], X["mult0"]))
    for base, f, vals, mean in X["payD"]:
        x = base * 3.0 * f
        check(set(vals) <= set([math.floor(x), math.ceil(x)]),
              "X payD(%s x 3 x %s = %.4f): only floor / ceil: %s" % (base, f, x, vals))
        check(abs(mean - x) < 0.02 + 0.01 * x ** 0.5, "X payD mean %.4f vs %.4f" % (mean, x))
    check(X["payD_edge"] == [0, 0, 0, 0, 10, 9000000000000000, 30], "X payD edges (0, NaN, inf, a non-class slot x1, the cap, 10/3 x 3 x 3 = 30 exactly): %s" % X["payD_edge"])
    print("X. lvBase = model on %d cases; vs 0.4.16 Hard: exact product worst %.2f%%, rounded chain worst %.2f%% (%s), from Lv 20 %.2f%%"
          % (len(X["grid"]), worst_exact[0] * 100, worst_round[0] * 100, worst_round[1], hi10 * 100))
    # ---------------------------------------------------------------- K
    K = D["K"]
    fr = K["fraction"]
    check(K["calls"] == [["default", "00000000-0000-0317-0000-000000000021"]], "K: mob:fn:info gets {world name, the UUIDComponent uuid}: %s" % K["calls"])

    def kcase(name, x_killer, member_x, tol=0.03):
        kc = K[name]
        vals = [c[0] for c in kc["killer"]]
        ok, mean = within(vals, x_killer, tol)
        check(ok and all(c[0] == c[1] for c in kc["killer"]), "K %s: killer pays %.3f (floor / ceil, mean %.3f; = the XP gained)" % (name, x_killer, mean))
        for i, mx in enumerate(member_x):
            g = kc["gains"][i]
            if mx is None:
                check(all(v == 0 for v in g), "K %s member %d: nothing (out of range / creative): %s" % (name, i + 1, sorted(set(g))[:5]))
                continue
            lo, hi = math.floor(math.floor(mx / fr + 1e-9) * fr + 1e-9), math.ceil(math.ceil(mx / fr - 1e-9) * fr - 1e-9)
            mean = sum(g) / float(len(g))
            check(all(lo <= v <= hi for v in g) and abs(mean - mx) <= max(0.06 * mx, 0.6),
                  "K %s member %d: %.3f (range %d-%d, mean %.3f, got %s)" % (name, i + 1, mx, lo, hi, mean, sorted(set(g))[:6]))
        return kc
    LVL = [1, 30, 40, 60]
    lb_hard = lvbase_py(103.0, 20, 1.0)
    kcase("lv_hard", lb_hard * 3.0, [lb_hard * 3.0 * gap_py(20, s) * fr for s in LVL] + [None, None])
    check(abs(lb_hard * 3.0 - 455.157) < 0.001, "K: spec test step 7 - a Lv 20 wolf-class kill at Divinity 20 pays %.2f (~455 with x1.5)" % (lb_hard * 3.0))
    lb_easy = lvbase_py(103.0, 20, 0.6944)
    kcase("lv_easy", lb_easy * 3.0, [lb_easy * 3.0 * gap_py(20, s) * fr for s in LVL] + [None, None])
    kcase("lv_gap", lb_hard * 3.0 * 1.5, [lb_hard * 3.0 * gap_py(20, s) * fr for s in LVL] + [None, None])
    kcase("lv_partoff", lb_hard * 3.0, [lb_hard * 3.0 * fr for s in LVL] + [None, None])
    lb_c = lvbase_py(103.0, 20, 1.0, pts=[(1.0, 1.0), (20.0, 10.0)])
    kcase("lv_custom", lb_c * 3.0, [lb_c * 3.0 * gap_py(20, s) * fr for s in LVL] + [None, None], tol=0.04)
    import struct
    mh = struct.unpack("f", struct.pack("f", 359.36))[0]
    base_old = jround(jround(mh * 0.2) * 1.5)                       # combatXp(null, 359.36f) = scaled(round(71.87)) = round(72 x 1.5) = 108
    x_old = base_old * 3.0 * (1.0 + 0.05 * 32) * gap_py(33, 20)
    kcase("health_mode", x_old, [base_old * 3.0 * (1.0 + 0.05 * 32) * gap_py(33, s) * fr for s in LVL] + [None, None])
    check(K["health_calls"] == 0, "K: health mode never asks mob:fn:info (%d calls)" % K["health_calls"])
    kcase("no_info_fn", x_old, [base_old * 3.0 * (1.0 + 0.05 * 32) * gap_py(33, s) * fr for s in LVL] + [None, None])
    kcase("info_null", base_old * 3.0, [base_old * 3.0 * fr for s in LVL] + [None, None])
    kcase("info_throw", base_old * 3.0, [base_old * 3.0 * fr for s in LVL] + [None, None], tol=0.06)
    check(K["info_throw_flag"] == [False, True] and LOG.count("mob info lookup (mob:fn:info) failed (logged once") == 1,
          "K: a throwing mob:fn:info = no level, WARN once: %s" % K["info_throw_flag"])
    m = K["malformed"]
    check(m["short"] is None and m["level0"] is None and m["xb0"] is None and m["string"] is None and m["inf_xb"] is None
          and m["nan_xm"] == [20.0, 103.0, 1.0] and m["neg_xm"] == [20.0, 103.0, 0.0] and m["big_xm"] == [20.0, 103.0, 100.0]
          and m["five"] == [20.0, 103.0, 1.0] and m["long_level"] == [20.0, 103.0, 1.0], "K: malformed answers: %s" % m)
    check(K["info_nulls"] == [True, True] and K["info_no_uuidc"], "K: no store / no ref / no UUIDComponent = null")
    kcase("role", 75 * 3.0 * (1.0 + 0.05 * 19), [75 * 3.0 * (1.0 + 0.05 * 19) * gap_py(20, s) * fr for s in LVL] + [None, None])
    kcase("role_off", 75 * 3.0, [75 * 3.0 * fr for s in LVL] + [None, None])
    fk = fk2 = LOG
    check(fk.count("combat: first kill of NPC role Wolf_Black (max health 505.73) (Lv 1 health 103) - override with combat.role.Wolf_Black=<xp>") == 1,
          "K: the first-kill line gains '(Lv 1 health 103)', once: %r" % fk[-300:])
    check(fk2.count("combat: first kill of NPC role Wolf_White (max health 505.73) - override with combat.role.Wolf_White=<xp>") == 1,
          "K: no info answer -> the 0.4.16 first-kill line: %r" % fk2[-300:])
    check(K["text_lv"].startswith("from the mob level (Lv 1 health x the level curve: Lv 20 x4.91, Lv 40 x12.15 default x the difficulty share")
          and "; gap more than 5 levels above" in K["text_lv"] and K["text_hp"].startswith("from mob health, on (+5% a mob level"), "K: MobXp.text: %s | %s" % (K["text_lv"], K["text_hp"]))
    check(all(abs(v - round(108 * fr)) <= 1 for v in K["old_share2"][:4]) and K["old_share2"][4:] == [0, 0], "K: the old share2 signature = 0.4.16: %s" % K["old_share2"])
    print("K. kill2: level mode Hard %.1f / Easy / gap / part off / custom curve; health mode + no mob:fn:info = 0.4.16; info null / throw / malformed = classXp; role override" % (lb_hard * 3))
    # ---------------------------------------------------------------- R
    Rr = D["R"]
    exp = {0: 0.0, 1: 0.0, 19: 0.0, 20: 0.0, 21: 7.0, 25: 35.0, 30: 70.0, 40: 140.0, 49: 203.0, 60: 280.0, 100: 560.0}
    check(all(r[1] == r[0] and abs(r[2] - exp[r[0]]) < 1e-9 and abs(r[3] - exp[r[0]]) < 1e-9 for r in Rr["table"]),
          "R: class level 0..100 -> +0 up to 20, +7 a level after (30 = +70, 40 = +140, 49 = +203): %s" % Rr["table"])
    check(Rr["no_src"] == [70.0, ["class level=+70"]] and Rr["with_src"] == [90.0, ["Test=+20", "class level=+70"]],
          "R: the perk is one more source, listed as 'class level': %s %s" % (Rr["no_src"], Rr["with_src"]))
    check(Rr["compact"].startswith("Mana Regen +90% (Test=+20, class level=+70). Refill 9.5/s, in combat 4.75/s (50%).") and "Mana Regen +90%" in Rr["show"][2]
          and Rr["bridge"] == [90.0, ["Test=+20", "class level=+70"]] and "class level=+70" in Rr["text"], "R: compact / show / text / bridge: %s | %s" % (Rr["compact"], Rr["bridge"]))
    check(Rr["clamp"] == [8000.0, 1000.0] and Rr["off"] == [0.0, 0.0, []], "R: MAX_PCT clamp 1000; perLevel 0 = off: %s %s" % (Rr["clamp"], Rr["off"]))
    check(Rr["fromlevel"] == [[0, 210.0], [25, 35.0], [30, 0.0], [100, 0.0]], "R: fromLevel moves the start: %s" % Rr["fromlevel"])
    check(Rr["no_class"] == [0.0, 0.0] and Rr["other_class"] == 0.0 and Rr["offline"] == [0.0, False] and Rr["null"] == [0.0, 0.0],
          "R: no class / another class's skill / an offline profile (no file read, DATA untouched) / null = 0: %s %s %s" % (Rr["no_class"], Rr["offline"], Rr["null"]))
    tk = Rr["tick"]
    want = {"20_out": 0.0, "20_in": 2.5, "30_out": 3.5, "30_in": 4.25, "40_out": 7.0, "40_in": 6.0}
    check(all(abs(tk[k] - v) <= 0.2 for k, v in want.items()) and not Rr["tick_warn"],
          "R: the REAL ManaRegen.tick adds per second (vanilla 5/s itself): class 20 out 0 / in 2.5, 30 out 3.5 / in 4.25, 40 out 7 / in 6: %s" % tk)
    print("R. Mana regen +7%% a class level above 20: %s" % tk)
    # ---------------------------------------------------------------- MG
    MG = D["MG"]
    live = open(LIVE, "rb").read()
    full = block.encode("latin-1")

    def blk(b=0.05, frm=True, curve=True, per=True, fl=True):
        t = C["block"].split("combat.xpFrom=level\n")[0]                # HEAD + FROM comments
        head = t.split("# KILL XP COMES FROM")[0]
        out = head
        if frm:
            out += t[len(head):] + "combat.xpFrom=level\n"
        if curve:
            ch = C["block"][C["block"].index("# KILL XP LEVEL CURVE"):C["block"].index("combat.levelCurve.1=")]
            out += ch + "".join("combat.levelCurve.%d=%s\n" % (L, v) for L, v in kxp_curve(b))
        if per or fl:
            out += C["block"][C["block"].index("# MANA REGEN PER CLASS LEVEL"):]
            out += ("mana.regen.perLevel=7\n" if per else "") + ("mana.regen.fromLevel=20\n" if fl else "")
        return out.encode("latin-1")
    check(blk() == full, "MG: the model block = the default-file block")

    def mg(name, exp_bytes, log_rows, msg_has=()):
        r = MG[name]
        got = r["new"].encode("latin-1")
        lg = [ln.split("\t")[1:] for ln in r["log"].strip().split("\n") if ln.strip()]
        ok = got == exp_bytes and r["same2"] and r["r2"] == "" and lg == log_rows and all(x in r["r1"] for x in msg_has)
        if exp_bytes != (shapes_in.get(name)):
            ok = ok and r["hist_old"] and r["n_hist"] == 1
        check(ok, "MG %s: bytes %s, run twice = once %s, log %s, history %s/%d, msg %r" % (name, got == exp_bytes, r["same2"] and r["r2"] == "", lg,
                                                                                          r["hist_old"], r["n_hist"], r["r1"][:160]))
    one_log = [["SkyySkills 0.4.17", "-", "update", "combat.xpFrom", "health", "level", "ok"]]
    shapes_in = {"marker": live + b"# ---------- " + KXP_MARK_ID.encode() + b" ----------\n"}
    mg("live", live + b"\n" + full, one_log, ("combat.xpFrom=level", "16 points from level bonus 0.05: Lv 20 x4.91, Lv 40 x12.15", "mana.regen.perLevel=7, mana.regen.fromLevel=20"))
    mg("crlf", (live + b"\n" + full).replace(b"\n", b"\r\n"), one_log)
    mg("nofinal", live.rstrip(b"\n") + b"\n\n" + full, one_log)
    mg("bonus01", live.replace(b"combat.levelBonus=0.05", b"combat.levelBonus=0.1") + b"\n" + blk(b=0.1), one_log, ("level bonus 0.1",))
    mg("partoff", live.replace(b"combat.levelXp.enabled=true", b"combat.levelXp.enabled=false") + b"\n" + blk(b=0.0), one_log, ("level bonus 0:",))
    mg("admin_from", live + b"combat.xpFrom=health\n" + b"\n" + blk(frm=False), [])
    mg("admin_curve", live + b"combat.levelCurve.10=3\n" + b"\n" + blk(curve=False), one_log)
    mg("admin_per", live + b"mana.regen.perLevel=5\n" + b"\n" + blk(per=False), one_log)
    mg("all", live + b"combat.xpFrom=level\ncombat.levelCurve.1=1\nmana.regen.perLevel=7\nmana.regen.fromLevel=20\n" + b"\n" + blk(frm=False, curve=False, per=False, fl=False),
       [], ("marker added",))
    check(MG["marker"]["r1"] == "" and MG["marker"]["new"].encode("latin-1") == shapes_in["marker"] and MG["marker"]["n_hist"] == 0 and MG["marker"]["log"] == "",
          "MG marker present: nothing at all")
    bsl = live + b"multiplier.note=x\\"
    check((MG["backslash"]["r1"] == "" and MG["backslash"]["new"].encode("latin-1") == bsl) or MG["backslash"]["new"].encode("latin-1") == bsl + b"\n\n" + full,
          "MG trailing backslash: refused + untouched, or the block after a blank line: %r" % MG["backslash"]["r1"][:80])
    check(MG["empty"]["new"].encode("latin-1") == b"\n" + full and MG["empty"]["same2"], "MG empty file: the block (after one newline): %r" % MG["empty"]["new"][:40])
    check(MG["nobonus"]["new"].encode("latin-1") == b"multiplier=1.0\n\n" + full and MG["nobonus"]["same2"], "MG a file without the 0.4.14 rows: the default bonus 0.05 curve")
    print("MG. KillXpMig on 13 file shapes (exact bytes, History first, one log line, run twice = once)")
    # ---------------------------------------------------------------- M
    M = D["M"]
    r1, r2 = M["r1"], M["r2"]
    check(M["xp1"].encode("latin-1") == M["xp0"].encode("latin-1") + b"\n" + full, "M: start 1 appends exactly the block to the live copy (nothing else changes)")
    pruned = [k for k in M["changed1"] if k.startswith("config-history/") and k.endswith(".bak") and k not in M["hist_new"]]
    check(all(k in ("xp.properties", "config-changes.log", "config-history/index.log") or k in M["hist_new"] or k in pruned for k in M["changed1"])
          and len(M["hist_new"]) == 1 and M["hist_old"] and M["n_bak"] <= 10 and not any(k.startswith("players/") for k in M["changed1"]),
          "M: start 1 changes only xp.properties, one new History copy (the old bytes; the kit keeps %d, pruned %s) and the log: %s" % (M["n_bak"], pruned, M["changed1"]))
    check([ln.split("\t")[1:] for ln in M["log_new"].strip().split("\n")] == one_log, "M: one change-log line: %r" % M["log_new"])
    check(M["changed2"] == [] and r2["kxmig"] == "" and r1["lvmig"] == "" and r1["cmig"] == "" and r1["heal"] == "" and r1["doc"] == ""
          and "updated for 0.4.17" in r1["kxmig"], "M: only KillXpMig acts on the live 0.4.16 data; start 2 changes nothing: %s" % M["changed2"])
    check(r1["mode"] == [True, 16, 4.91, 12.15, 7.0, 20, 1.5, 3.0] and r2["mode"] == r1["mode"], "M: after the live start: level mode, 16 points, Mana 7 / 20, x1.5, x3: %s" % r1["mode"])
    print("M. live copy: start 1 = the block + History + 1 log line; start 2 = nothing")
    # ---------------------------------------------------------------- KC
    KC = D["KC"]
    check(KC["mig"].startswith("xp.properties updated for 0.4.17") and sorted(KC["keys1"][0]) == sorted(str(L) for L in KXP_LEVELS)
          and dict(zip(KC["keys1"][0], KC["keys1"][1])) == dict((str(L), v) for L, v in kdef), "KC: the kit lists the 16 points: %s" % KC["keys1"])
    check(KC["get_from"] == "level", "KC: get combat.xpFrom = level")
    check(KC["tset40"][0] == "ok" and KC["after_tset"][0] == 14.0 and abs(KC["after_tset"][1] - (14.0 + (14.46 - 14.0) * 2.0 / 5.0)) < 1e-9 and KC["after_tset"][2],
          "KC: tset 40 -> 14 live (Lv 45 interpolates): %s %s" % (KC["tset40"], KC["after_tset"]))
    check(KC["add101"][0] != "ok" and KC["addabc"][0] != "ok" and KC["addlow"][0] != "ok" and KC["add55"][0] == "ok" and KC["after_add"] == [20.0, 17],
          "KC: 101 / abc / 0.05 refused, 55 = 20 added live: %s %s %s %s %s" % (KC["add101"], KC["addabc"], KC["addlow"], KC["add55"], KC["after_add"]))
    check(KC["rm55"][0] == "ok" and KC["after_rm"][1] == 16 and abs(KC["after_rm"][0] - (16.97 + (22.59 - 16.97) * 0.5)) < 1e-9, "KC: remove 55 live: %s" % KC["after_rm"])
    check(KC["set_health"][0] == "ok" and KC["set_health"][1] == "health" and KC["after_health"] == [False, True] and KC["set_bad"][0] != "ok"
          and KC["undo"][0] == "ok" and KC["after_undo"], "KC: the choice row (label 'Mob health' typed) live; a bad value refused; set back: %s %s" % (KC["set_health"], KC["set_bad"]))
    check(KC["set_per"][0] == "ok" and KC["set_from"][0] == "ok" and KC["set_per_bad"][0] != "ok" and KC["after_mana"] == [10.0, 25],
          "KC: mana.regen.perLevel 10 / fromLevel 25 live; 150 refused: %s" % KC["after_mana"])
    check(any("\tcombat.xpFrom\thealth\tlevel\tok" in ln and "update" in ln for ln in KC["log"]) and any("combat.levelCurve[40]" in ln for ln in KC["log"]),
          "KC: the change log holds the update line (Undo) and the table edit: %s" % KC["log"][:6])
    print("KC. the rows through the real kit: table tset / add / remove + refusals, the choice row, Mana rows, the log")
    # ---------------------------------------------------------------- F: class compare
    za, zb = zipfile.ZipFile(PREV_JAR), zipfile.ZipFile(JAR)
    ca = dict((n, za.read(n)) for n in za.namelist() if n.endswith(".class"))
    cb = dict((n, zb.read(n)) for n in zb.namelist() if n.endswith(".class"))
    new_cls = sorted(n.split("/")[-1][:-6] for n in set(cb) - set(ca))
    gone_cls = sorted(set(ca) - set(cb))
    changed = sorted(n.split("/")[-1][:-6] for n in set(ca) & set(cb) if ca[n] != cb[n] and ca[n].replace(PREV_VERSION.encode(), VERSION.encode()) != cb[n])
    must = {"MobXp", "PartyXp", "ManaRegen", "SkillCfg", "KillSys", "SkyySkillsPlugin"}
    allowed = must | {"CfgRows", "CfgFile"}                         # the kit's row arrays (197 -> 201 rows)
    check(new_cls == ["KillXpMig"] and not gone_cls, "F: new classes %s, none gone %s" % (new_cls, gone_cls))
    check(set(changed) <= allowed and must <= set(changed), "F: classes changed beyond the version string: %s (allowed %s)" % (changed, sorted(allowed)))
    ks = [cb[n] for n in cb if n.endswith("/KillSys.class")][0]
    check(b"\x00\x05kill2" in ks and b"\x00\x04kill" not in ks.replace(b"\x00\x05kill2", b""), "F: KillSys calls MobXp.kill2, no longer MobXp.kill")
    others = [n for n in set(za.namelist()) | set(zb.namelist()) if not n.endswith(".class") and n != "manifest.json"]
    check(all(n in za.namelist() and n in zb.namelist() and za.read(n) == zb.read(n) for n in others), "F: every asset file byte-identical to 0.4.16")
    print("F. 0.4.16 -> 0.4.17: + %s; changed %s; %d unchanged classes" % (new_cls, changed, len(ca) - len(changed)))
    # ---------------------------------------------------------------- AU: the engine-access audit
    au = json.load(open(auo))
    check(au["refused"] == [] and au["control"] and au["refs"] > 1000, "AU: %d references in %d classes, refused %s; control refused: %s" % (
        au["refs"], au["classes"], au["refused"][:3], bool(au["control"])))
    print("AU. engine-access audit: %d references, %d refused (control refused: %s)" % (au["refs"], len(au["refused"]), bool(au["control"])))
    # ---------------------------------------------------------------- the live data is untouched
    live_after = dict((os.path.relpath(os.path.join(r, f), LIVE_DIR), os.path.getmtime(os.path.join(r, f))) for r, ds, fs in os.walk(LIVE_DIR) for f in fs)
    check(live_after == live_snap, "the live Skyy_SkyySkills folder was never written")
    # ---------------------------------------------------------------- report
    print("\nKILL XP, same-level kill, Hard, Skyy's x1.5 and class x3 (0.4.16 rounded chain -> 0.4.17 level mode):")
    for xb in (50, 103, 226, 400):
        print("  Lv 1 health %3d: " % xb + ", ".join("Lv %d %.0f -> %.0f" % (L, old_hard_xp(xb, L)[0], lvbase_py(xb, L, 1.0) * 3.0) for L in (1, 10, 20, 33, 40, 49, 60)))
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
