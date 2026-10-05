"""SkyySkills 0.4.16 - bare-JVM harness for MINING'S OWN LEVEL LIST + LEADERBOARDS SKIP DELETED PROFILES (tools/skills_0_4_16_patch.py).
A focused harness: the new parts on the REAL classes of the 0.4.16 jar (HytaleServer.jar on the class path, -Xverify:all), the live save data
only ever READ and copied into the scratch folder; everything 0.4.15 already checked is guarded by the class compare (section F: only the
planned classes differ from the SET pin 0.4.15 beyond the version string) - run SkyySkills/test_skyyskills_0.4.15.py for the older sections.

    python SkyySkills/test_skyyskills_0.4.16.py [--jar <SkyySkills-0.4.16.jar>] [--prev <SkyySkills-0.4.15.jar>] [--dir <scratch>]
                                                [--live <Skyy_SkyySkills folder>] [--keep]

SECTIONS
  A   every class of the jar loads under -Xverify:all
  T   THE TABLES (real SkillDefs after a real SkillCfg.load of the fresh 0.4.16 default file): Mining's cumulative table = the Python model
      10 + 5L + 1.5L^2 (rounded half up) at every level boundary +-1 and 2,000 random totals (levelOf / intoLevel / needFor / progress /
      maxOf); every other non-class skill = the general list, every class skill = the class table (ECUM); the default file has the block
      once at its end and gather.boost.skills=Foraging,Farming; GatherPace: Mining unboosted (apply = the amount exactly), Foraging boosted
  L   SkillLv: the table loader on 12 line sets (any case, a class skill, Combat, unknown, a bad number, 0, 101 entries, two spellings,
      Foraging added, empty), one WARN per new problem, text(); the check= hook
  KC  the row through the REAL config kit (CfgPub / config:fn:SkyySkills): keys lists Mining; add a class skill / a bad list refused; add
      Foraging + remove Mining live (levels follow at once); Undo-style remove leaves Mining on the general list
  MG  SkillLvMig on file shapes: the live file (LF), CRLF, no final newline, an admin's gather value (kept + note), gather already new,
      no gather line, a continued gather value, an existing levels.skill line (marker only), the marker (nothing), a trailing backslash;
      exact bytes, History copy first, change-log lines, run twice = once
  M   START TWICE on the scratch copy of the live data (the plugin's setup order): start 1 = xp.properties migrated + own-levels.properties
      written with exactly the model's moves of every live profile, players/ untouched; start 2 changes nothing
  D   DELIVERY on the live copy: each live profile told once (OwnCurve.tick): coins:fn:add called exactly once per newly reached level (the
      model's list), the paid marker = the new level, XP unchanged on disk after the flush, a second tick nothing, a restart nothing; then
      Mining gains: no coins until a level above the marker
  DN  LEVEL DROPS (a steep list on a copy): the line says XP kept / nothing taken back; NO coins; marker unchanged; re-levelling pays nothing
      up to the old marker, then exactly once per new level; drop-through-gain4 path; SkyyCoins missing on a rise = owed, paid once later
  LB  LEADERBOARDS: SkillTop.all / rankOf with profile:fn:state answering pending / archived / active / inactive / null / PENDING / a Long /
      throwing, files on disk + profiles in memory; without SkyyProfiles = everyone (0.4.15's list)
  F   class compare 0.4.15 -> 0.4.16 (version string normalised): only the planned classes differ
"""
import os, sys, json, shutil, subprocess, zipfile, random, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.4.16", "0.4.15"
PKG = "com.skyy.skills."
MINING, FORAGING, FARMING, COMBAT, ACRO, DIVINITY, ARCHERY = 0, 1, 2, 3, 4, 15, 5
N = 16
MINING_PER = [(21 + 10 * L + 3 * L * L) // 2 for L in range(1, 101)]
SKL_MARK_ID = "Own level list per skill (SkyySkills 0.4.16)"
GOLD, GNEW = "Mining,Foraging,Farming", "Foraging,Farming"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "sk0416", "harness")))
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
    """the 0.4.15 harness module (its stand-in generator and JVM helpers) - imported, never run"""
    spec = importlib.util.spec_from_file_location("t0415", os.path.join(HERE, "test_skyyskills_0.4.15.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.SCRATCH = SCRATCH
    return m


def cum_of(per):
    c = [0]
    for x in per:
        c.append(c[-1] + x)
    return c


def level_in(cum, x):
    lv = 0
    while lv < len(cum) - 1 and x >= cum[lv + 1]:
        lv += 1
    return lv


def props(b):
    d = {}
    for ln in b.decode("latin-1").replace("\r\n", "\n").split("\n"):
        t = ln.strip()
        if t and not t.startswith("#") and "=" in t:
            d[t.split("=", 1)[0].strip()] = t.split("=", 1)[1].strip()
    return d


# ============================================================================================ child
def run_new(jar, out, fake, model_file):
    from jpype import JClass, JLong, JArray, JImplements, JOverride
    T = t15()
    res, path = T.common(jar, [fake])
    if res["load_fails"]:
        json.dump(res, open(out, "w"), indent=1)
        return
    D = res["data"]
    model = json.load(open(model_file))
    UUID, CHM = JClass("java.util.UUID"), JClass("java.util.concurrent.ConcurrentHashMap")
    Cfg, Xp, Store, Defs = JClass(PKG + "SkillCfg"), JClass(PKG + "SkillXp"), JClass(PKG + "SkillStore"), JClass(PKG + "SkillDefs")
    Lv, Own, LvMig, Top, Pace = JClass(PKG + "SkillLv"), JClass(PKG + "OwnCurve"), JClass(PKG + "SkillLvMig"), JClass(PKG + "SkillTop"), JClass(PKG + "GatherPace")
    Curve, Hist, CLog, Rows = JClass(PKG + "ClassCurve"), JClass(PKG + "CfgHist"), JClass(PKG + "CfgLog"), JClass(PKG + "CfgRows")
    Mig, HMig, DMig, CMig = JClass(PKG + "ManaMig"), JClass(PKG + "HealMig"), JClass(PKG + "DocMig"), JClass(PKG + "ClassManaMig")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Universe, Holder = JClass("com.hypixel.hytale.server.core.universe.Universe"), JClass("com.hypixel.hytale.component.Holder")
    FakeH, FakeW = JClass("skyytest.FakeHandler"), JClass("skyytest.FakeWorld")
    JBool, JLongC, JObj, JStr = JClass("java.lang.Boolean"), JClass("java.lang.Long"), JClass("java.lang.Object"), JClass("java.lang.String")
    Props = JClass("java.util.Properties")
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

    COINS = []
    COINS_ON = [True]

    @JImplements("java.util.function.Function")
    class Coins(object):
        @JOverride
        def apply(self, o):
            if not COINS_ON[0]:
                return None
            COINS.append([str(o[0]), int(o[1])])
            return JLongC(1000000 + sum(c[1] for c in COINS))

    ACTIVE = {}

    @JImplements("java.util.function.Function")
    class PKey(object):
        @JOverride
        def apply(self, o):
            k = ACTIVE.get(str(o))
            return k if k is not None else str(o)

    STATES = {}

    @JImplements("java.util.function.Function")
    class State(object):
        @JOverride
        def apply(self, o):
            v = STATES.get(str(o), "active")
            if v == "THROW":
                raise RuntimeError("state boom")
            if v == "LONG":
                return JLongC(5)
            return v

    bridge = Store.bridge()
    bridge.put("coins:fn:add", Coins())
    bridge.put("profile:fn:key", PKey())
    uni = U.allocateInstance(Universe.class_)
    PLAYERS, WORLDS = CHM(), CHM()
    setf(uni, Universe, "playersByUuid", PLAYERS)
    setf(uni, Universe, "players", PLAYERS.values())
    setf(uni, Universe, "worldsByUuid", WORLDS)
    setf(None, Universe, "instance", uni)
    world = U.allocateInstance(FakeW.class_)
    wuid = UUID(0x3016D, 1)
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

    def snap(d):
        return dict((os.path.relpath(os.path.join(r, fn), d).replace(os.sep, "/"), open(os.path.join(r, fn), "rb").read())
                    for r, ds, fs in os.walk(d) for fn in fs)

    def start(d):
        """the plugin's setup order: ManaMig -> HealMig -> DocMig -> ClassManaMig -> SkillLvMig (0.4.16) -> SkillCfg.load -> ClassCurve.start
        -> OwnCurve.start (0.4.16)"""
        Cfg.FILE = path(os.path.join(d, "xp.properties"))
        fresh_store(os.path.join(d, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        r = {"mana": [str(x) for x in Mig.run()], "heal": str(HMig.run()), "doc": str(DMig.run()), "cmig": str(CMig.run()), "lvmig": str(LvMig.run())}
        r["load"] = str(Cfg.load())
        r["curve"] = str(Curve.start(path(d)))
        r["own"] = str(Own.start(path(d)))
        r["ready"] = bool(Own.READY)
        r["pending"] = dict((str(k), str(v)) for k, v in Own.PENDING.items())
        r["done"] = dict((str(k), str(v)) for k, v in Own.DONE.items())
        r["slots"] = str(Own.SLOTS)
        return r

    def safe(name, fn_):
        try:
            D[name] = fn_()
        except Exception:
            import traceback
            D[name] = {"error": traceback.format_exc()[-3000:]}

    # ---------------------------------------------------------------- T: the tables
    def sec_T():
        R = {}
        work = os.path.join(SCRATCH, "t-cfg")
        os.makedirs(work, exist_ok=True)
        f = os.path.join(work, "xp.properties")
        R["load"] = load_cfg(work)
        R["defaults"] = open(f, "rb").read().decode("latin-1")
        R["block"] = str(LvMig.BLOCK)
        R["own0"] = [int(x) for x in Defs.own(MINING)]
        R["has"] = [bool(Defs.hasOwn(s)) for s in range(N)]
        R["cum"] = [int(x) for x in Defs.CUM]
        R["ecum"] = [int(x) for x in Defs.ECUM]
        R["max"] = [int(Defs.maxOf(s)) for s in range(N)]
        rnd = random.Random(416)
        mc = cum_of(MINING_PER)
        xs = sorted(set([0, 1] + [v + d for v in mc for d in (-1, 0, 1) if v + d >= 0] + [rnd.randrange(0, 700000) for _ in range(2000)] + [10 ** 12]))
        R["xs"] = xs
        R["mining"] = [[int(Defs.levelOf(MINING, JLong(x))), int(Defs.intoLevel(MINING, JLong(x))), int(Defs.needFor(MINING, JLong(x))), str(Defs.progress(MINING, JLong(x)))] for x in xs]
        R["general"] = [[int(Defs.levelOf(s, JLong(x))) for s in (FORAGING, FARMING, ACRO, 10, 11, 12, 13, COMBAT)] + [int(Defs.generalLevel(JLong(x)))] for x in xs[::9]]
        R["classes"] = [[int(Defs.levelOf(s, JLong(x))), int(Defs.levelIn(Defs.ECUM, JLong(x)))] for s in (5, 6, 15) for x in xs[::23]]
        R["pace"] = [bool(Pace.on(s)) for s in (MINING, FORAGING, FARMING)] + [str(Pace.TEXT)]
        u = UUID(0x7A, 1)
        fresh_store(os.path.join(SCRATCH, "t-players"))
        os.makedirs(os.path.join(SCRATCH, "t-players"), exist_ok=True)
        R["apply"] = [int(Pace.apply(u, MINING, JLong(10))) for _ in range(20)] + [int(Pace.apply(u, FORAGING, JLong(10)))]
        R["text"] = str(Lv.text())
        return R
    safe("T", sec_T)

    # ---------------------------------------------------------------- L: the loader + check hook
    def sec_L():
        R = {}
        Cfg.LOG = None
        cases = {
            "mining_case": {"levels.skill.mINing": "5,10,15"},
            "class": {"levels.skill.Divinity": "5,10", "levels.skill.Mining": "1,2,3"},
            "combat": {"levels.skill.Combat": "5"},
            "unknown": {"levels.skill.Fishing": "5"},
            "badnum": {"levels.skill.Mining": "5,x,7"},
            "zero": {"levels.skill.Mining": "5,0,7"},
            "toolong": {"levels.skill.Mining": ",".join(["1"] * 101)},
            "two": {"levels.skill.Mining": "1,2", "levels.skill.mining": "3,4,5"},
            "foraging": {"levels.skill.Foraging": "100,200", "levels.skill.Mining": "1,1,1,1"},
            "label": {"levels.skill.Exploration": "7", "levels.skill.Acrobatics": "8,9"},
            "empty": {},
            "huge": {"levels.skill.Mining": "1000000000000001"},
        }
        for name, kv in cases.items():
            p = Props()
            for k, v in kv.items():
                p.setProperty(k, v)
            p.setProperty("levels.skill.", "1")
            Lv.WARNED = ""
            Lv.read(p)
            R[name] = {"own": dict((str(s), [int(x) for x in Defs.own(s)]) for s in range(N) if Defs.hasOwn(s)), "text": str(Lv.text()), "warned": str(Lv.WARNED)}
        R["check"] = {k: (None if Lv.checkEntry(k, v) is None else str(Lv.checkEntry(k, v))) for k, v in (
            ("levels.skill[Mining]", "1,2,3"), ("levels.skill[mining]", "17,26"), ("levels.skill[Divinity]", "1,2"), ("levels.skill[Combat]", "1"),
            ("levels.skill[Fishing]", "1"), ("levels.skill[Mining]", "1,,2"), ("levels.skill[Mining]", ",".join(["5"] * 101)), ("levels.skill[Cooking]", "9"))}
        R["check_remove"] = Lv.checkEntry("levels.skill[Divinity]", None) is None
        return R
    safe("L", sec_L)

    # ---------------------------------------------------------------- MG: SkillLvMig on file shapes
    def sec_MG():
        R = {}
        live = open(LIVE, "rb").read()
        shapes = {
            "live": live,
            "crlf": live.replace(b"\n", b"\r\n"),
            "nofinal": live.rstrip(b"\n"),
            "admin": live.replace(b"gather.boost.skills=Mining,Foraging,Farming", b"gather.boost.skills=Mining,Farming"),
            "already": live.replace(b"gather.boost.skills=Mining,Foraging,Farming", b"gather.boost.skills=Foraging,Farming"),
            "nogather": live.replace(b"gather.boost.skills=Mining,Foraging,Farming\n", b""),
            "continued": live.replace(b"gather.boost.skills=Mining,Foraging,Farming", b"gather.boost.skills=Mining,\\\n    Foraging,Farming"),
            "haskey": live + b"levels.skill.Foraging=10,20\n",
            "marker": live + b"# ---------- " + SKL_MARK_ID.encode() + b" ----------\n",
            "backslash": live + b"multiplier.note=x\\",
            "dupold": live.replace(b"gather.boost.skills=Mining,Foraging,Farming", b"gather.boost.skills=Mining,Foraging,Farming\ngather.boost.skills=Farming"),
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
            r1 = str(LvMig.run())
            b1 = open(f, "rb").read()
            s1 = snap(d)
            r2 = str(LvMig.run())
            b2 = open(f, "rb").read()
            hist = [k for k in s1 if k.startswith("config-history/") and k.endswith(".bak")]
            R[name] = {"r1": r1, "r2": r2, "new": b1.decode("latin-1"), "same2": b1 == b2, "hist_old": any(s1[k] == data for k in hist), "n_hist": len(hist),
                       "log": s1.get("config-changes.log", b"").decode("utf-8")}
        return R
    safe("MG", sec_MG)

    # ---------------------------------------------------------------- M + D: the live copy
    def sec_MD():
        R = {}
        lc = os.path.join(SCRATCH, "live-copy")
        s0 = snap(lc)
        r1 = start(lc)
        s1 = snap(lc)
        r2 = start(lc)
        s2 = snap(lc)
        R["r1"], R["r2"] = r1, r2
        R["changed1"] = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
        R["changed2"] = sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k))
        R["record"] = s1.get("own-levels.properties", b"").decode("latin-1")
        R["xp1"] = s1["xp.properties"].decode("latin-1")
        R["pace"] = [bool(Pace.on(s)) for s in (MINING, FORAGING, FARMING)]
        # delivery: each live profile with a pending entry, as its player (profile key active)
        DEL = {}
        for k in sorted(r1["pending"]):
            us = k.split("-p")[0] if "-p" in k else k
            u = UUID.fromString(us)
            ACTIVE[us] = k
            pr = mkpr(u, "Live")
            f = os.path.join(lc, "players", k + ".properties")
            before = props(open(f, "rb").read())
            COINS[:] = []
            texts()
            Own.tick(pr, u)
            t1, c1 = texts(), list(COINS)
            paid = int(Store.dataK(k, u)[N + MINING])
            disk_now = props(open(f, "rb").read())          # review F1: before any flush - the marker must already be on disk
            Own.flush()
            after = props(open(f, "rb").read())
            COINS[:] = []
            Own.tick(pr, u)
            t2, c2 = texts(), list(COINS)
            DEL[k] = {"t1": t1, "c1": c1, "paid": paid, "disk_now": disk_now, "before": before, "after": after, "t2": t2, "c2": c2,
                      "level": int(Store.level(u, MINING))}
        R["deliver"] = DEL
        R["record2"] = open(os.path.join(lc, "own-levels.properties"), "rb").read().decode("latin-1")
        r3 = start(lc)
        R["r3"] = r3
        # later Mining gains on the richest profile: no coins until a level above the marker, then exactly once per level
        if DEL:
            k = max(DEL, key=lambda x: int(DEL[x]["before"].get("Mining", "0")))
            us = k.split("-p")[0] if "-p" in k else k
            u = UUID.fromString(us)
            ACTIVE[us] = k
            pr = mkpr(u, "Live")
            d = Store.dataK(k, u)
            x0, lv0 = int(d[MINING]), int(Store.level(u, MINING))
            mc = cum_of(MINING_PER)
            COINS[:] = []
            Xp.gain3(pr, MINING, mc[lv0 + 1] - x0 - 1, False, False)
            c_a = list(COINS)
            Xp.gain3(pr, MINING, 1, False, False)
            c_b = list(COINS)
            Xp.gain3(pr, MINING, 1, False, False)
            c_c = list(COINS)
            R["gain"] = {"key": k, "lv0": lv0, "c_a": c_a, "c_b": c_b, "c_c": c_c, "lv": int(Store.level(u, MINING)), "paid": int(d[N + MINING])}
        return R
    safe("MD", sec_MD)

    # ---------------------------------------------------------------- DN: level drops (a steep list) + gain4 path + SkyyCoins missing
    def sec_DN():
        R = {}
        dn = os.path.join(SCRATCH, "drop")
        shutil.copytree(os.path.join(SCRATCH, "live-copy-pristine"), dn)
        u = UUID(0xD0, 1)
        k = str(u)
        u2 = UUID(0xD0, 2)
        k2 = str(u2)
        u3 = UUID(0xD0, 3)
        k3 = str(u3)
        # 5,969 Mining XP, paid 8 (general level 8) -> on the steep list (1000 a level) level 5; u2: 1,787 paid 5 -> level 1 (paid 5);
        # u3: 9,925 paid 9 (general level 10 owed 10) -> steep 9 = a drop below the general level with an owed level
        open(os.path.join(dn, "players", k + ".properties"), "wb").write(b"name=Dropper\nMining=5969\nMining.paid=8\n")
        open(os.path.join(dn, "players", k2 + ".properties"), "wb").write(b"name=Dropper2\nMining=1787\nMining.paid=5\n")
        open(os.path.join(dn, "players", k3 + ".properties"), "wb").write(b"name=Dropper3\nMining=9925\nMining.paid=9\n")
        xf = os.path.join(dn, "xp.properties")
        txt = open(xf, "rb").read()
        open(xf, "wb").write(txt + b"\nlevels.skill.Mining=" + ",".join(["1000"] * 100).encode() + b"\n")
        r1 = start(dn)
        R["start"] = r1
        pr = mkpr(u, "Dropper")
        COINS[:] = []
        texts()
        Own.tick(pr, u)
        R["t1"], R["c1"] = texts(), list(COINS)
        d = Store.dataK(k, u)
        R["after"] = [int(d[MINING]), int(d[N + MINING]), int(Store.level(u, MINING))]
        Own.flush()
        R["disk"] = props(open(os.path.join(dn, "players", k + ".properties"), "rb").read())
        # re-level: 5 -> 8 pays nothing (paid 8), 9 pays 900 once
        COINS[:] = []
        seq = []
        for target in (6, 7, 8, 9, 10):
            need = target * 1000 - int(d[MINING])
            Xp.gain3(pr, MINING, need, False, False)
            seq.append([target, int(Store.level(u, MINING)), int(d[N + MINING]), list(COINS)])
        R["relevel"] = seq
        R["relevel_texts"] = texts()
        # u2 via the gain4 path first (the notice comes first inside gain4, then the award)
        pr2 = mkpr(u2, "Dropper2")
        COINS[:] = []
        Xp.gain3(pr2, MINING, 1, False, False)
        R["gain_path"] = {"t": texts(), "c": list(COINS), "lv": int(Store.level(u2, MINING)), "paid": int(Store.dataK(k2, u2)[N + MINING]),
                          "pending": k2 in [str(x) for x in Own.PENDING.keySet()]}
        # u3: drop to 9 with paid 9 = no 'pays no coins again' range beyond 9
        pr3 = mkpr(u3, "Dropper3")
        Own.tick(pr3, u3)
        R["u3"] = {"t": texts(), "paid": int(Store.dataK(k3, u3)[N + MINING]), "lv": int(Store.level(u3, MINING))}
        # a RISE with SkyyCoins missing: the line once, coins owed (marker unchanged), paid once at the next gain
        up = os.path.join(SCRATCH, "rise-nocoins")
        shutil.copytree(os.path.join(SCRATCH, "live-copy-pristine"), up)
        u4 = UUID(0xD0, 4)
        k4 = str(u4)
        open(os.path.join(up, "players", k4 + ".properties"), "wb").write(b"name=Riser\nMining=961\nMining.paid=4\n")
        start(up)
        pr4 = mkpr(u4, "Riser")
        COINS_ON[0] = False
        COINS[:] = []
        Own.tick(pr4, u4)
        t_a = texts()
        paid_a = int(Store.dataK(k4, u4)[N + MINING])
        COINS_ON[0] = True
        Own.tick(pr4, u4)
        t_b = texts()
        Xp.gain3(pr4, MINING, 1, False, False)
        t_c = texts()
        R["nocoins"] = {"t_a": t_a, "paid_a": paid_a, "t_b": t_b, "t_c": t_c, "coins": list(COINS), "paid": int(Store.dataK(k4, u4)[N + MINING]),
                        "lv": int(Store.level(u4, MINING))}
        return R
    safe("DN", sec_DN)

    # ---------------------------------------------------------------- KC: the row through the REAL config kit
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
        R["mig"] = str(LvMig.run())
        Cfg.load()
        CfgPub.start(Paths.get(kmods, JStrA([])), None)
        fn = bridge.get("config:fn:SkyySkills")

        def op(*a):
            r = fn.apply(OA(list(a)))
            return None if r is None else [None if x is None else str(x) for x in list(r)[:3]]

        def keys():
            ks = fn.apply(OA(["keys", "levels.skill", ""]))
            return [[str(x) for x in ks[0]], [str(x) for x in ks[2]]]
        R["keys1"] = keys()
        R["add_class"] = op("add", "levels.skill", "Divinity", "5,10", None, "console", "yes", "console")
        R["add_bad"] = op("add", "levels.skill", "Foraging", "5,-1", None, "console", "yes", "console")
        R["add_ok"] = op("add", "levels.skill", "Foraging", "100,200,300", None, "console", "yes", "console")
        CfgPub.flush()
        R["after_add"] = [keys(), bool(Defs.hasOwn(FORAGING)), int(Defs.levelOf(FORAGING, JLong(300))), int(Defs.maxOf(FORAGING))]
        R["rm"] = op("remove", "levels.skill", "Mining", None, "console", "yes", "console")
        CfgPub.flush()
        txt = open(kf, "rb").read().decode("latin-1")
        R["after_rm"] = [keys(), bool(Defs.hasOwn(MINING)), int(Defs.levelOf(MINING, JLong(9925))), "levels.skill.Mining=" in txt, SKL_MARK_ID in txt]
        lg = [str(x) for x in fn.apply(OA(["log", JClass("java.lang.Integer")(50)]))]
        R["log"] = [ln for ln in lg if "levels.skill" in ln or "gather.boost.skills" in ln]
        before2 = open(kf, "rb").read()
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        R["mig2"] = str(LvMig.run())
        R["same2"] = open(kf, "rb").read() == before2
        CfgPub.shutdown()
        return R
    safe("KC", sec_KC)

    # ---------------------------------------------------------------- LB: leaderboards
    def sec_LB():
        R = {}
        lb = os.path.join(SCRATCH, "lb-players")
        os.makedirs(lb, exist_ok=True)
        rows = [("aaaaaaaa-0000-0000-0000-000000000001", "Active", 900, "active"), ("aaaaaaaa-0000-0000-0000-000000000002", "Deleted", 800, "pending"),
                ("aaaaaaaa-0000-0000-0000-000000000003-p2", "Archived", 700, "archived"), ("aaaaaaaa-0000-0000-0000-000000000004", "Inactive", 600, "inactive"),
                ("aaaaaaaa-0000-0000-0000-000000000005", "NullState", 500, None), ("aaaaaaaa-0000-0000-0000-000000000006", "Upper", 400, "PENDING"),
                ("aaaaaaaa-0000-0000-0000-000000000007", "Thrower", 300, "THROW"), ("aaaaaaaa-0000-0000-0000-000000000008", "LongState", 200, "LONG"),
                ("aaaaaaaa-0000-0000-0000-000000000009", "Zero", 0, "active")]
        for k, nm, x, st in rows:
            open(os.path.join(lb, k + ".properties"), "wb").write(("name=%s\nMining=%d\n" % (nm, x)).encode())
            STATES[k] = st
        fresh_store(lb)
        # an in-memory profile (deleted while loaded) and an in-memory active one
        um, ua = UUID(0xBB, 1), UUID(0xBB, 2)
        dm = Store.dataK(str(um), um)
        dm[MINING] = 5000
        da = Store.dataK(str(ua), ua)
        da[MINING] = 100
        STATES[str(um)] = "pending"
        STATES[str(ua)] = "active"

        def board():
            for i in range(len(Top.CACHE)):
                Top.CACHE[i] = None
                Top.AT[i] = 0
            rs = Top.all(MINING)
            return [[str(r[0]), int(r[1]), str(r[2])] for r in rs]
        bridge.remove("profile:fn:state")
        R["without"] = board()
        bridge.put("profile:fn:state", State())
        R["with"] = board()
        rs = Top.all(MINING)
        R["rank_active"] = int(Top.rankOf(rs, UUID.fromString("aaaaaaaa-0000-0000-0000-000000000001")))
        R["rank_deleted"] = int(Top.rankOf(rs, UUID.fromString("aaaaaaaa-0000-0000-0000-000000000002")))
        R["rank_mem"] = int(Top.rankOf(rs, ua))
        bridge.put("profile:fn:state", "not a function")
        R["not_fn"] = len(board())
        bridge.remove("profile:fn:state")
        return R
    safe("LB", sec_LB)
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ parent
def mining_model(gen_per, coins_per, players_dir):
    """every live profile: Mining XP, paid marker, level on the general list (0.4.15) and on Mining's list (0.4.16), the coins 0.4.16 pays"""
    gc, mc = cum_of(gen_per), cum_of(MINING_PER)
    out = {}
    for fn in sorted(os.listdir(players_dir)):
        if not fn.endswith(".properties"):
            continue
        p = props(open(os.path.join(players_dir, fn), "rb").read())
        x = int(p.get("Mining", "0") or 0)
        paid = int(p.get("Mining.paid", "0") or 0)
        old, new = level_in(gc, x), level_in(mc, x)
        out[fn[:-11]] = {"name": p.get("name"), "xp": x, "paid": paid, "old": old, "new": new,
                         "coins": [coins_per * L for L in range(paid + 1, new + 1)], "moves": x > 0 and old != new}
    return out


def main():
    if "--mkfake" in sys.argv:
        return t15().run_mkfake(arg("--mkfake"))
    if "--new-run" in sys.argv:
        return run_new(arg("--new-run"), arg("--out"), arg("--fake"), arg("--model"))
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
    shutil.copytree(LIVE_DIR, os.path.join(SCRATCH, "live-copy-pristine"))
    lp = props(open(LIVE, "rb").read())
    gen_per = [int(x) for x in lp["levels"].split(",")]
    coins_per = int(lp.get("coinsPerLevel", "100"))
    check(lp.get("gather.boost.skills") == GOLD and not any(k.startswith("levels.skill.") for k in lp),
          "the live xp.properties is 0.4.15's (gather.boost.skills at the old default, no levels.skill line)")
    model = mining_model(gen_per, coins_per, os.path.join(LIVE_DIR, "players"))
    model_file = os.path.join(SCRATCH, "model.json")
    json.dump(model, open(model_file, "w"))
    me = os.path.abspath(__file__)
    fake = os.path.join(SCRATCH, "fake")
    p = subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(os.path.join(fake, "skyytest", "FakeHandler.class")), "the stand-in classes were generated")
    outp = os.path.join(SCRATCH, "run-new.json")
    p = subprocess.run([sys.executable, me, "--new-run", JAR, "--out", outp, "--fake", fake, "--model", model_file, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(outp), "child JVM ran")
    if FAILS:
        return finish()
    res = json.load(open(outp))
    check(not res["load_fails"] and res["loaded"] == res["classes"], "A: %d / %d classes load under -Xverify:all %s" % (res["loaded"], res["classes"], res["load_fails"][:3]))
    D = res["data"]
    for k in ("T", "L", "MG", "MD", "DN", "KC", "LB"):
        check(k in D and "error" not in D[k], "section %s ran: %s" % (k, (D.get(k) or {}).get("error")))
    if FAILS:
        return finish()
    mc = cum_of(MINING_PER)
    gcum = cum_of(gen_per)
    # ---------------------------------------------------------------- T
    T = D["T"]
    check(T["own0"] == mc, "T: Mining's own cumulative table = the model (10 + 5L + 1.5L^2): %s ..." % T["own0"][:6])
    check(T["has"] == [True] + [False] * 15, "T: only Mining has its own list by default: %s" % T["has"])
    bad = []
    for x, r in zip(T["xs"], T["mining"]):
        lv = level_in(mc, x)
        need = mc[lv + 1] - mc[lv] if lv < 100 else 0
        if r[:3] != [lv, x - mc[lv], need]:
            bad.append((x, r))
    check(not bad and T["max"][MINING] == 100, "T: Mining levelOf / intoLevel / needFor on %d totals = the model: %s" % (len(T["xs"]), bad[:3]))
    check(all(len(set(r)) == 1 for r in T["general"]), "T: Foraging / Farming / Acrobatics / Alchemy / Smithing / Cooking / Exploration / Combat = the general list")
    check(all(a == b for a, b in T["classes"]), "T: class skills level on ECUM (unchanged)")
    check(T["pace"] == [False, True, True, "Foraging,Farming"], "T: gathering pace: Mining off, Foraging + Farming on: %s" % T["pace"])
    check(T["apply"][:20] == [10] * 20 and T["apply"][20] == 30, "T: GatherPace.apply: Mining 10 -> 10 exactly (20 times), Foraging 10 -> 30 (x3 default): %s" % T["apply"])
    dft = T["defaults"]
    check(dft.endswith("\n" + T["block"]) and dft.count(SKL_MARK_ID) == 1 and "\ngather.boost.skills=Foraging,Farming\n" in dft
          and "\nlevels.skill.Mining=" + ",".join(map(str, MINING_PER)) + "\n" in dft and "Mining,Foraging,Farming\n" not in dft.replace("bridge.addxp.skills=Mining,Foraging,Farming", ""),
          "T: the fresh default file ends with the block (marker once, the Mining list), gather.boost.skills=Foraging,Farming")
    check(T["text"] == "Mining (100 levels)" and "own level lists Mining (100 levels)" in T["load"], "T: SkillLv.text / the load summary: %r" % T["text"])
    print("T. Mining's own table = 10 + 5L + 1.5L^2 on %d totals; others general, classes ECUM; pace Mining off; default file block" % len(T["xs"]))
    # ---------------------------------------------------------------- L
    Lr = D["L"]
    check(Lr["mining_case"]["own"] == {"0": [0, 5, 15, 30]} and Lr["mining_case"]["warned"].count("left out") == 1, "L: any case; the bare prefix line left out: %s" % Lr["mining_case"])
    check(Lr["class"]["own"] == {"0": [0, 1, 3, 6]} and "Divinity is not a skill" in Lr["class"]["warned"], "L: a class skill refused: %s" % Lr["class"])
    check(Lr["combat"]["own"] == {} and "Combat is not a skill" in Lr["combat"]["warned"], "L: legacy Combat refused")
    check(Lr["unknown"]["own"] == {} and Lr["badnum"]["own"] == {} and Lr["zero"]["own"] == {} and Lr["toolong"]["own"] == {} and Lr["huge"]["own"] == {}
          and "not a list" in Lr["badnum"]["warned"], "L: unknown / bad number / 0 / 101 entries / above 1e15 = left out (general list)")
    check(Lr["two"]["own"] == {"0": [0, 1, 3]} and "listed twice" in Lr["two"]["warned"], "L: two spellings: the first in sort order wins: %s" % Lr["two"])
    check(set(Lr["foraging"]["own"]) == {"0", "1"} and Lr["foraging"]["text"] == "Mining (4 levels), Foraging (2 levels)", "L: Foraging + Mining: %s" % Lr["foraging"]["text"])
    check(set(Lr["label"]["own"]) == {"4", "13"} and Lr["empty"]["own"] == {} and Lr["empty"]["text"] == "none", "L: Acrobatics / Exploration allowed; empty = none")
    ck = Lr["check"]
    check(ck["levels.skill[Mining]"] is not None and ck["levels.skill[mining]"] is None and ck["levels.skill[Cooking]"] is None
          and "Unknown skill Divinity" in ck["levels.skill[Divinity]"] and "Unknown skill Combat" in ck["levels.skill[Combat]"]
          and "Unknown skill Fishing" in ck["levels.skill[Fishing]"] and Lr["check_remove"],
          "L: check= hook: class / Combat / unknown refused, a removal always fine: %s" % ck)
    print("L. loader: 12 line sets, one WARN per problem; check= hook")
    # ---------------------------------------------------------------- MG
    MG = D["MG"]
    live = open(LIVE, "rb").read()
    blk = T["block"].encode("latin-1")
    head = blk[:blk.index(b"levels.skill.Mining=")]
    mlist = ",".join(map(str, MINING_PER))
    exp_live = live.replace(b"gather.boost.skills=" + GOLD.encode(), b"gather.boost.skills=" + GNEW.encode()) + b"\n" + blk
    check(MG["live"]["new"].encode("latin-1") == exp_live and MG["live"]["same2"] and MG["live"]["r2"] == "" and MG["live"]["hist_old"] and MG["live"]["n_hist"] == 1,
          "MG live: exactly the gather line changed + a blank line + the block; History holds the old bytes; run twice = once")
    lg = [ln.split("\t")[1:] for ln in MG["live"]["log"].strip().split("\n")]
    check(lg == [["SkyySkills 0.4.16", "-", "update", "gather.boost.skills", GOLD, GNEW, "ok"],
                 ["SkyySkills 0.4.16", "-", "update", "levels.skill[Mining]", "(none)", mlist, "ok"]], "MG live: two change-log lines: %s" % lg)
    check(MG["crlf"]["new"].encode("latin-1") == exp_live.replace(b"\n", b"\r\n") and MG["crlf"]["same2"], "MG crlf: CRLF kept, block in CRLF")
    check(MG["nofinal"]["new"].encode("latin-1") == live.rstrip(b"\n").replace(b"gather.boost.skills=" + GOLD.encode(), b"gather.boost.skills=" + GNEW.encode()) + b"\n\n" + blk,
          "MG no final newline: a newline + a blank line before the block")
    check(MG["admin"]["new"].encode("latin-1") == live.replace(b"gather.boost.skills=" + GOLD.encode(), b"gather.boost.skills=Mining,Farming") + b"\n" + blk
          and "kept (an admin's value) - Mining still gets the early gathering XP boost" in MG["admin"]["r1"] and "gather.boost.skills" not in MG["admin"]["log"],
          "MG admin: an admin's gather list kept (+ the note), the block added")
    check(MG["already"]["new"].encode("latin-1") == live.replace(b"gather.boost.skills=" + GOLD.encode(), b"gather.boost.skills=" + GNEW.encode()) + b"\n" + blk
          and "kept" not in MG["already"]["r1"], "MG already new: only the block")
    check(MG["nogather"]["new"].encode("latin-1") == live.replace(b"gather.boost.skills=Mining,Foraging,Farming\n", b"") + b"\n" + blk, "MG no gather line: only the block (SkillCfg.ensure14 adds the new default)")
    check(MG["continued"]["new"].encode("latin-1").startswith(live.replace(b"gather.boost.skills=" + GOLD.encode(), b"gather.boost.skills=Mining,\\\n    Foraging,Farming"))
          and "kept (an admin's value)" in MG["continued"]["r1"], "MG continued gather value: kept (+ note)")
    hk = live.replace(b"gather.boost.skills=" + GOLD.encode(), b"gather.boost.skills=" + GNEW.encode()) + b"levels.skill.Foraging=10,20\n" + b"\n" + head
    check(MG["haskey"]["new"].encode("latin-1") == hk and "levels.skill[Mining]" not in MG["haskey"]["log"], "MG an admin's levels.skill line: only the marker comments (no Mining entry)")
    check(MG["marker"]["r1"] == "" and MG["marker"]["new"].encode("latin-1") == live + b"# ---------- " + SKL_MARK_ID.encode() + b" ----------\n" and MG["marker"]["n_hist"] == 0,
          "MG marker present: nothing at all")
    bsl = live + b"multiplier.note=x\\"
    check((MG["backslash"]["r1"] == "" and MG["backslash"]["new"].encode("latin-1") == bsl) or
          MG["backslash"]["new"].encode("latin-1") == bsl.replace(b"gather.boost.skills=" + GOLD.encode(), b"gather.boost.skills=" + GNEW.encode()) + b"\n\n" + blk,
          "MG trailing backslash (no final newline): refused + untouched, or the block after a blank line (the Properties check passed): %r" % MG["backslash"]["r1"][:80])
    check(MG["dupold"]["new"].encode("latin-1") == live.replace(b"gather.boost.skills=" + GOLD.encode(), b"gather.boost.skills=" + GOLD.encode() + b"\ngather.boost.skills=Farming") + b"\n" + blk,
          "MG two gather lines, the last an admin's: nothing replaced (the effective value is kept)")
    print("MG. SkillLvMig on 11 file shapes")
    # ---------------------------------------------------------------- M + D
    MD = D["MD"]
    r1, r2 = MD["r1"], MD["r2"]
    want_pending = dict((k, "0:%d:%d" % (m["old"], m["new"])) for k, m in model.items() if m["moves"])
    check(r1["pending"] == want_pending and r1["ready"] and r1["slots"] == "Mining", "M: start 1 records exactly the model's moves: %s vs %s" % (r1["pending"], want_pending))
    check(MD["changed1"] and all(k in ("xp.properties", "own-levels.properties", "config-changes.log") or k.startswith("config-history/") for k in MD["changed1"])
          and "own-levels.properties" in MD["changed1"] and not any(k.startswith("players/") for k in MD["changed1"]),
          "M: start 1 changes only xp.properties, its History copy, the change log and own-levels.properties: %s" % MD["changed1"])
    check(MD["changed2"] == [] and r2["lvmig"] == "" and r2["pending"] == r1["pending"],
          "M: start 2 changes nothing: %s %r" % (MD["changed2"], r2["own"]))
    check(r1["heal"] == "" and r1["doc"] == "" and r1["cmig"] == "" and "updated for 0.4.16" in r1["lvmig"], "M: only SkillLvMig acts on the live 0.4.15 data")
    check(MD["pace"] == [False, True, True], "M: after the live start Mining is out of the gathering pace")
    DEL = MD["deliver"]
    for k, m in model.items():
        if not m["moves"]:
            continue
        dd = DEL.get(k, {})
        exp_c = [[k.split("-p")[0], c] for c in m["coins"]]
        check(dd.get("c1") == exp_c and dd.get("paid") == max(m["paid"], m["new"]) and dd.get("level") == m["new"],
              "D %s: coins:fn:add once per new level %s (got %s), marker %s" % (k, [c for c in m["coins"]], dd.get("c1"), dd.get("paid")))
        check(len(dd.get("t1", [])) >= 1 and any("Mining is now level %d (was %d)" % (m["new"], m["old"]) in t for t in dd["t1"]),
              "D %s: the notice line: %s" % (k, dd.get("t1")))
        check(dd.get("after", {}).get("Mining") == str(m["xp"]) and dd["after"].get("Mining.paid") == str(max(m["paid"], m["new"]))
              and all(dd["after"].get(x) == dd["before"].get(x) for x in dd["before"] if x not in ("Mining.paid",)),
              "D %s: on disk after the flush: XP unchanged, only the paid marker moved" % k)
        check(dd.get("disk_now", {}).get("Mining.paid") == str(max(m["paid"], m["new"])) and dd["disk_now"].get("Mining") == str(m["xp"]),
              "D %s: review F1 - the paid marker %s is on disk right after the deliver that paid (before any flush): %s"
              % (k, max(m["paid"], m["new"]), dd.get("disk_now", {}).get("Mining.paid")))
        check(dd.get("t2") == [] and dd.get("c2") == [], "D %s: a second tick does nothing" % k)
    check(MD["r3"]["pending"] == {} and set(MD["r3"]["done"]) == set(want_pending) and MD["r3"]["own"] == "", "D: restart: everyone done, nothing pending")
    g = MD.get("gain", {})
    check(g and g["c_a"] == [] and len(g["c_b"]) == 1 and g["c_b"][0][1] == coins_per * (g["lv0"] + 1) and g["c_c"] == g["c_b"] and g["paid"] == g["lv0"] + 1,
          "D: later Mining gains on %s: nothing until level %d, then %d coins once: %s" % (g.get("key"), g.get("lv0", 0) + 1, coins_per * (g.get("lv0", 0) + 1), g))
    print("M/D. live copy: %d profile(s) told; coins once per new level; XP unchanged on disk" % len(DEL))
    # ---------------------------------------------------------------- DN
    DN = D["DN"]
    check(DN["c1"] == [] and DN["after"] == [5969, 8, 5] and any("Mining is now level 5 (was 8) - your XP is kept and nothing is taken back; levels 6 to 8 were paid already" in t for t in DN["t1"]),
          "DN: a drop 8 -> 5: no coins, marker 8, XP 5969, the line: %s" % DN["t1"])
    check(DN["disk"].get("Mining") == "5969" and DN["disk"].get("Mining.paid") == "8", "DN: on disk XP + marker unchanged: %s" % DN["disk"])
    rl = DN["relevel"]
    check([r[1] for r in rl] == [6, 7, 8, 9, 10] and [r[2] for r in rl] == [8, 8, 8, 9, 10] and rl[2][3] == [] and rl[3][3] == [["00000000-0000-00d0-0000-000000000001", coins_per * 9]]
          and rl[4][3] == [["00000000-0000-00d0-0000-000000000001", coins_per * 9], ["00000000-0000-00d0-0000-000000000001", coins_per * 10]],
          "DN: re-levelling 6, 7, 8 pays nothing; 9 and 10 once each: %s" % rl)
    gp = DN["gain_path"]
    check(gp["c"] == [] and gp["lv"] == 1 and gp["paid"] == 5 and not gp["pending"] and any("Mining is now level 1 (was 5)" in t for t in gp["t"]),
          "DN: the gain4 path tells first (drop 5 -> 1), no coins: %s" % gp)
    check(DN["u3"]["paid"] == 9 and DN["u3"]["lv"] == 9 and any("is now level 9 (was 10)" in t and "nothing is taken back" in t and "pay no coins again" not in t and "pays no coins again" not in t for t in DN["u3"]["t"]),
          "DN: a drop to exactly the marker: no 'paid already' range: %s" % DN["u3"])
    nc = DN["nocoins"]
    check(nc["paid_a"] == 4 and any("is now level 10 (was 4)" in t for t in nc["t_a"]) and nc["t_b"] == [] and nc["paid"] == 10 and nc["lv"] == 10
          and [c[1] for c in nc["coins"]] == [coins_per * L for L in range(5, 11)] and any("could not be paid at the time" in t for t in nc["t_c"]),
          "DN: SkyyCoins missing on a rise: told once, coins owed, paid once (5..10) at the next gain: %s" % nc)
    print("DN. drops: no coins, marker kept, re-levelling pays only past the marker; owed coins paid once later")
    # ---------------------------------------------------------------- KC
    KC = D["KC"]
    check(KC["keys1"] == [["Mining"], [mlist]], "KC: the kit lists levels.skill = Mining: %s" % KC["keys1"][0])
    check(KC["add_class"][0] != "ok" and KC["add_bad"][0] != "ok" and KC["add_ok"][0] == "ok", "KC: a class skill / a bad list refused, Foraging added: %s %s %s" % (KC["add_class"], KC["add_bad"], KC["add_ok"]))
    check(KC["after_add"][1:] == [True, 2, 3] and "Foraging" in KC["after_add"][0][0], "KC: Foraging's list live after the save: %s" % KC["after_add"])
    check(KC["after_rm"][1:] == [False, level_in(gcum, 9925), False, True], "KC: Mining removed = the general list again, the marker stays: %s" % KC["after_rm"])
    check(KC["mig2"] == "" and KC["same2"], "KC: the next start's SkillLvMig leaves the admin's choice alone (marker)")
    print("KC. the row through the real kit: add / refuse / remove live")
    # ---------------------------------------------------------------- LB
    LB = D["LB"]
    names_w = [r[0] for r in LB["with"]]
    names_wo = [r[0] for r in LB["without"]]
    check(len(names_wo) == 11 and "Deleted" in names_wo and "Archived (profile 2)" in names_wo, "LB: without SkyyProfiles everyone is listed: %s" % names_wo)
    check("Deleted" not in names_w and "Archived (profile 2)" not in names_w and not any(r[2] == "00000000-0000-00bb-0000-000000000001" for r in LB["with"])
          and all(x in names_w for x in ("Active", "Inactive", "NullState", "Upper", "Thrower", "LongState", "Zero")) and len(LB["with"]) == 8,
          "LB: pending / archived (disk + memory) left out; active / inactive / null / PENDING / a Long / throwing shown: %s" % names_w)
    check(LB["rank_active"] == 1 and LB["rank_deleted"] == 0 and LB["rank_mem"] == 7, "LB: ranks skip the left-out profiles: %s %s %s" % (LB["rank_active"], LB["rank_deleted"], LB["rank_mem"]))
    check(LB["not_fn"] == 11, "LB: a non-Function bridge value = everyone")
    print("LB. leaderboards: %d of %d rows (pending / archived left out)" % (len(names_w), len(names_wo)))
    # ---------------------------------------------------------------- F: class compare
    za, zb = zipfile.ZipFile(PREV_JAR), zipfile.ZipFile(JAR)
    ca = dict((n, za.read(n)) for n in za.namelist() if n.endswith(".class"))
    cb = dict((n, zb.read(n)) for n in zb.namelist() if n.endswith(".class"))
    new_cls = sorted(n.split("/")[-1][:-6] for n in set(cb) - set(ca))
    gone_cls = sorted(set(ca) - set(cb))
    changed = sorted(n.split("/")[-1][:-6] for n in set(ca) & set(cb) if ca[n] != cb[n] and ca[n].replace(PREV_VERSION.encode(), VERSION.encode()) != cb[n])
    want_new = ["OwnCurve", "SkillLv", "SkillLvMig"]
    allowed = {"SkillDefs", "SkillCfg", "GatherPace", "SkillXp", "Perks", "SkillTop", "SkillTick", "SkyySkillsPlugin", "CfgRows", "CfgFile"}   # CfgFile: the kit's row arrays 196 -> 197
    check(new_cls == want_new and not gone_cls, "F: new classes %s (want %s), none gone %s" % (new_cls, want_new, gone_cls))
    check(set(changed) <= allowed and {"SkillDefs", "SkillCfg", "GatherPace", "SkillXp", "Perks", "SkillTop", "SkillTick", "SkyySkillsPlugin"} <= set(changed),
          "F: classes changed beyond the version string: %s (allowed %s)" % (changed, sorted(allowed)))
    others = [n for n in set(za.namelist()) | set(zb.namelist()) if not n.endswith(".class") and n != "manifest.json"]
    check(all(n in za.namelist() and n in zb.namelist() and za.read(n) == zb.read(n) for n in others), "F: every asset file byte-identical to 0.4.15")
    print("F. 0.4.15 -> 0.4.16: + %s; changed %s; %d unchanged classes" % (new_cls, changed, len(ca) - len(changed)))
    # ---------------------------------------------------------------- the live data is untouched
    live_after = dict((os.path.relpath(os.path.join(r, f), LIVE_DIR), os.path.getmtime(os.path.join(r, f))) for r, ds, fs in os.walk(LIVE_DIR) for f in fs)
    check(live_after == live_snap, "the live Skyy_SkyySkills folder was never written")
    # ---------------------------------------------------------------- report tables
    print("\nMINING TABLE (new 10 + 5L + 1.5L^2 vs old = the live general list):")
    print("  L   new cost  new total |   old cost   old total")
    for L in list(range(1, 21)) + [25, 30, 40, 50]:
        print("  %-3d %8d %10d | %10d %11d" % (L, MINING_PER[L - 1], mc[L], gen_per[L - 1], gcum[L]))
    print("  cumulative new / old: " + ", ".join("L%d %d / %d" % (L, mc[L], gcum[L]) for L in (5, 10, 20, 30, 50)))
    print("\nLIVE PROFILES (read only): Mining XP, paid marker, level 0.4.15 -> 0.4.16, coins paid at the notice")
    for k, m in model.items():
        print("  %-44s %-14s xp %6d paid %2d  level %2d -> %2d  coins %s" % (k, m["name"], m["xp"], m["paid"], m["old"], m["new"], sum(m["coins"])))
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
