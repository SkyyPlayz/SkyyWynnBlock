"""Harness for SkyyIslands 0.5.20 (beta bugs round 1 + the island pond; tools/islands_0_5_20_patch.py).
Build first: python tools/islands_0_5_20_patch.py && python SkyyIslands/build_skyyislands_0.5.20.py

    python SkyyIslands/test_skyyislands_0.5.20.py [--jar <jar>] [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; stand-in IsleApi = a Python JProxy, real IslandStore files in scratch, -Xverify:all):
  A / C / AA  verify, compare 0.5.19 -> 0.5.20 (exactly the planned members; IslandJoin new; non-class: manifest + the layout data), audit
  CFG   the 3 new config lines + rows (islands.deathKeep, camp.clearWhenDone, pond.enabled), a 0.5.19 file = the defaults and is not
        rewritten, islands.respawnKeep's value untouched (login only now), /island reset clears pond.placed
  RESP  bug 1: died on the own island and still there = 4 (NO goHome = no second teleport); the generated goHome returns 4 for the same
        world before any Teleport; bug 2: a death in the hub / Zone 1 / Zone 2 -> the island trip (0.5.19 kept the zone respawn = the
        ruins), a shard death keeps its respawn, islands.deathKeep edits, a bed where they died still wins, the login keep list unchanged;
        4 retries 1 / 2 / 3 / 4 s apart, then a WARN + the chat line (a parked login trip: no chat line, the login routing);
        the bed trip: bedSpot (raw spot free -> raw; on the bed -> the engine's ring; a wall in the ring -> the next cell; not loaded ->
        null; all blocked -> one up), IsleTask 13 -> 14 on the player's world -> IsleApi.teleport with the spot
  TIME  bug 9: onJoin hands the hub's reading to an island / shard / ZONE world being joined (never the hub, other worlds, a stale or
        paused reading, sync off); joinSync jumps forward only when > 10 game minutes behind, never backwards / in a bed skip;
        timeAll with nobody to sync still reads the hub's clock every 10 s; timeHub stores the reading; bytecode: timeWorlds takes
        skywynn_z worlds, setup registers IslandJoin for AddPlayerToWorldEvent
  CLEAR bug 19: camp done -> the tracked camp mobs + camp-role NPCs near the camp removed (a cow stays); not done -> nothing; the boss
        removed only once boss.done and not needed (repaired portal); a broken portal with no shard keeps it; 10 s pace; setting off
  POND  bare Python on the build's layout (0.5.19 vs 0.5.20 differ only in the pond cells; water enclosed; 2-3 deep; flush; off the
        spawn / bed / chest / plot / cave / bridge; the 0.5.19 JAR's own layout = S3_L_OLD and the 0.5.20 jar's = S3_L) + pondOnce
        EXECUTED: an old natural island -> dug + floored + planted + 46 water, pond.placed=1, never again; a new island -> water only;
        a player's block -> skip (nothing changed, pond.placed=skip); a cell not loaded -> later; a dug hole (air) -> wait, never filled;
        setting off; an island file with pond.placed=1; the 10 s pace
  LIVE  a scratch COPY of the live Skyy_SkyyIslands: config load = the new defaults, the file not rewritten; every island file reads,
        none has pond.placed yet; no file of the copy changed
Not testable without the game (UNVERIFIED): the respawn invulnerability really gone, the arrival clock order, the water on a live chunk,
the watering can / fishing in the pond, the camp mobs vanishing in front of a player.
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import soundpass_kit as SK

VERSION = "0.5.20"
OLD = "0.5.19"
PKG = "com.skyy.islands."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "isl520", "h")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyIslands")
ADDED = ["IslandJoin"]
EXPECT = {
    "IslandCfg": ["+f DEATH_KEEP", "+f CAMP_CLEAR", "+f POND_ON", "~<clinit>", "~m load"],
    "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "CfgFile": ["~<clinit>"],
    "IslandStore": ["~m setWorldName0"],
    "IsleApi": ["+m remove", "+m setWater", "+m teleport", "+m canWater", "+m fluid"],
    "IsleEng": ["+m remove", "+m water0", "+m setWater", "+m canWater", "+m fluid", "+m teleport", "~m goHome", "~m timeWorlds"],
    "IsleState": ["+f pondDone", "+f pondAt", "+f clearAt", "+f pondWaits", "+f pondFails"],
    "IsleTask": ["+f x", "+f y", "+f z", "+f bx", "+f by", "+f bz", "~m run"],
    "IsleLife": ["+f SNAP_MS", "+f SNAP_AT", "+f SNAP_F", "+f JOIN_MIN", "+f SNAP_TTL", "+f SNAP_GAP", "+f JOINS", "+f RETRIES", "+f CLEARED",
                 "+f PONDS", "+f WATER", "+f POND_C", "+f POND_OLD", "+f POND_NEW", "+f POND_W", "+f POND_WI", "+f POND_RUNS", "+f POND_PRE", "+f POND_SLOW", "~<clinit>",
                 "+m pondState", "+m pondSave", "+m pondStopped", "+m notHome",
                 "+m clearRoles", "+m clearTick", "+m pondOnce", "~m tickWorld", "+m deathKeep", "~m respawn", "~m respawnRetry",
                 "+m gaveUp", "+m respawnLog", "+m airish", "+m freeAt", "+m bedSpot", "+m bedTrip", "+m bedLand", "~m timeHub",
                 "~m timeAll", "+m timeKind", "+m onJoin", "+m joinSync"],
    "SkyyIslandsPlugin": ["~m setup"],
    "StarterIsles": ["~<clinit>", "~m decode", "~m fill"],   # the layout's run / block counts (constants) - the pond
    "FillTask": ["~m run"],
}
KO = "00000000-0000-4000-8000-0000000b0520"   # owner of the respawn / clear islands
KP = "00000000-0000-4000-8000-0000000c0520"   # owner of the pond islands
W, WP, WC = "skyy-island-resp", "skyy-island-pond", "skyy-island-camp"
HUB = "skywynn_zones"


def run_compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """the kit's compare; its non-class check replaced: only the manifest and the island layout data may change"""
    HK._kit_compare(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    d["fails"] = [f for f in d["fails"] if not f.startswith("C: non-class entries changed")]
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    na = set(n_ for n_ in za.namelist() if not n_.endswith(".class"))
    nb = set(n_ for n_ in zb.namelist() if not n_.endswith(".class"))
    changed = sorted(n_ for n_ in na & nb if za.read(n_) != zb.read(n_))
    if na != nb or changed != ["manifest.json"]:
        d["fails"].append("C: non-class entries: added %s removed %s changed %s" % (sorted(nb - na), sorted(na - nb), changed))
    d["ok"] += 1
    json.dump(d, open(out, "w"), indent=1)


HK._kit_compare = HK.run_compare
HK.run_compare = run_compare


def layout_of(v):
    os.environ["S3_ONLY"] = "1"
    sp = importlib.util.spec_from_file_location("build_skyyislands_%s_s3" % v.replace(".", "_"), os.path.join(HERE, "build_skyyislands_%s.py" % v))
    m = importlib.util.module_from_spec(sp)
    try:
        sp.loader.exec_module(m)
    except ImportError as e:
        assert "S3_ONLY" in str(e), e
    finally:
        del os.environ["S3_ONLY"]
    return m


def stand_in(iface, impl):
    """a JImplements stand-in for every abstract method of iface: impl's methods where it has them, else a neutral answer"""
    from jpype import JClass, JImplements, JOverride, JLong, JInt
    neutral = {"boolean": False, "int": JInt(0), "long": JLong(0), "void": None}
    body = {}
    for mm in JClass(iface).class_.getMethods():
        n, rt = str(mm.getName()), str(mm.getReturnType().getName())
        if hasattr(impl, n):
            body[n] = JOverride((lambda f: lambda self, *a: f(*a))(getattr(impl, n)))
        else:
            body[n] = JOverride((lambda v: lambda self, *a: v)(neutral.get(rt)))
    return JImplements(iface)(type("Stand", (object,), body))()


class Env(object):
    """the JVM + the real IslandStore on scratch island files"""

    def __init__(self, scratch, jar, sub):
        from jpype import JClass, isJVMStarted
        if not isJVMStarted():
            HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
        JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
        P = lambda n: JClass(PKG + n)
        self.P = P
        self.St, self.Cfg, self.Life, self.Task, self.Rows = P("IslandStore"), P("IslandCfg"), P("IsleLife"), P("IsleTask"), P("CfgRows")
        self.Paths, self.UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
        self.home = os.path.join(scratch, sub, "Skyy_SkyyIslands")
        shutil.rmtree(os.path.join(scratch, sub), ignore_errors=True)
        self.isl = os.path.join(self.home, "islands")
        os.makedirs(self.isl, exist_ok=True)
        self.St.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyIslands")
        self.Cfg.FILE = self.Paths.get(os.path.join(self.home, "config.properties"))
        self.Cfg.load("")

    def files(self, d):
        for k, props in d.items():
            with open(os.path.join(self.isl, k + ".properties"), "w", encoding="utf-8") as f:
                f.write("".join("%s=%s\n" % kv for kv in props.items()))
        self.St.DIR = self.Paths.get(self.isl)
        self.St.IO = None
        self.St.STOPPING = False
        self.St.SETTINGS.clear()
        self.St.loadIslandWorlds()

    def prop(self, k, key):
        for l in open(os.path.join(self.isl, k + ".properties"), encoding="utf-8").read().splitlines():
            if l.startswith(key + "="):
                return l.split("=", 1)[1]
        return None


# ================================================================================================ CFG
def run_cfg(out, jar, scratch, _home):
    K = HK.Child(out)
    E = Env(scratch, jar, "cfg")
    Cfg = E.Cfg
    cf = os.path.join(E.home, "config.properties")
    txt = open(cf, encoding="utf-8").read()
    lines = txt.splitlines()
    for l in ("islands.deathKeep=skyy-shard-", "camp.clearWhenDone=true", "pond.enabled=true", "islands.respawnKeep=skyy-shard-,skywynn_z"):
        K.check(l in lines, "CFG a fresh config.properties lists %s" % l)
    K.eq((str(Cfg.DEATH_KEEP), bool(Cfg.CAMP_CLEAR), bool(Cfg.POND_ON), str(Cfg.RESPAWN_KEEP)), ("skyy-shard-", True, True, "skyy-shard-,skywynn_z"),
         "CFG defaults (respawnKeep's value unchanged)")
    old = "\n".join(l for l in lines if not l.startswith(("islands.deathKeep", "camp.clearWhenDone", "pond.enabled")) and "0.5.20" not in l) + "\n"
    open(cf, "w", encoding="utf-8").write(old)
    Cfg.DEATH_KEEP, Cfg.CAMP_CLEAR, Cfg.POND_ON = "x", False, False
    Cfg.load("")
    K.eq((str(Cfg.DEATH_KEEP), bool(Cfg.CAMP_CLEAR), bool(Cfg.POND_ON)), ("skyy-shard-", True, True), "CFG a 0.5.19 file without the lines = the defaults")
    K.eq(open(cf, encoding="utf-8").read(), old, "CFG the 0.5.19 file is not rewritten (no migration)")
    open(cf, "w", encoding="utf-8").write(old + "islands.deathKeep=skyy-shard-,skywynn_z\ncamp.clearWhenDone=FALSE\npond.enabled=false\n")
    Cfg.load("")
    K.eq((str(Cfg.DEATH_KEEP), bool(Cfg.CAMP_CLEAR), bool(Cfg.POND_ON)), ("skyy-shard-,skywynn_z", False, False), "CFG hand edits read")
    open(cf, "w", encoding="utf-8").write(txt)
    Cfg.load("")
    rows = SK.kit_rows(E.Rows)
    want = {"islands.deathKeep": ("Death worlds that keep their respawn", "hub", "text", "skyy-shard-"),
            "camp.clearWhenDone": ("Clear the camp when the quest is done", "isles", "bool", "true"),
            "pond.enabled": ("Island 1 pond", "isles", "bool", "true"),
            "islands.respawnKeep": ("Worlds you log back in to", "hub", "text", "skyy-shard-,skywynn_z")}
    for k, v in want.items():
        r = rows.get(k)
        K.check(r is not None and tuple(r[1:5]) == v and "live" in r[9] and len(r[10]) <= 100, "ROW %s = %s (live, help <= 100): %s" % (k, v, r and r[1:11]))
    K.check("zone" in rows["islands.syncTime"][10], "ROW Island time = hub time says zone worlds too: %s" % rows["islands.syncTime"][10])
    gen = open(os.path.join(HERE, "build_skyyislands_%s.py" % VERSION), encoding="utf-8").read()
    K.check('p.remove("pond.placed");' in gen, "CFG /island reset clears pond.placed (a reset island has the pond in its layout)")
    K.save()


# ================================================================================================ RESP
def run_resp(out, jar, scratch, _home):
    from jpype import JClass, JString, JArray, JObject, JInt
    K = HK.Child(out)
    E = Env(scratch, jar, "resp")
    St, Cfg, Life, Task, UUID = E.St, E.Cfg, E.Life, E.Task, E.UUID
    uO = UUID.fromString(KO)
    E.files({KO: {"v": "5", "world": W, "isles": "3"}})
    K.check(str(St.ownerOf(W)) == KO and str(St.homeKey(uO)) == KO, "SETUP the island file: %s -> %s" % (KO[:8], W))
    A = {"where": {}, "online": set(), "later": [], "exec": [], "login": [], "home": [], "say": [], "tp": [], "beds": set(), "blocks": {}, "unl": set()}

    class Api(object):
        def later(self, r, ms):
            A["later"].append((r, int(ms)))
            return True

        def worldOf(self, u):
            w = A["where"].get(str(u))
            return None if w is None else JString(w)

        def online(self, u):
            return str(u) in A["online"]

        def exec(self, wn, r):
            A["exec"].append((str(wn), r))
            return A.get("execok", True)

        def fluid(self, wn, x, y, z):
            return JInt(A["fluid"].get((int(x), int(y), int(z)), 0))

        def players(self, wn):
            return JArray(JObject)([JArray(JObject)([UUID.fromString(k), JObject(0.5, "java.lang.Double"), JObject(129.0, "java.lang.Double"),
                                                     JObject(0.5, "java.lang.Double")]) for k, w in A["where"].items() if w == str(wn)])

        def loginRoute(self, u):
            A["login"].append(str(u))

        def hubWorld(self):
            return JString(HUB)

        def hasBed(self, u, wn):
            return str(wn) in A["beds"]

        def goHome(self, wn, u, hk, hw):
            A["home"].append((str(wn), str(hw)))
            return JInt(1)

        def toHub(self, wn, u):
            return True

        def name(self, u):
            return JString("Ava")

        def say(self, u, text, color):
            A["say"].append(str(text))

        def block(self, wn, x, y, z):
            p = (int(x), int(y), int(z))
            if p in A["unl"]:
                return None
            return JString(A["blocks"].get(p, ""))

        def teleport(self, fw, u, tw, x, y, z):
            A["tp"].append((str(fw), str(tw), float(x), float(y), float(z)))
            return JInt(A.get("tpr", 1))
    A["fluid"] = {}
    Life.API = stand_in(PKG + "IsleApi", Api())
    Cfg.RESPAWN_HOME = True

    def clear():
        for k in ("later", "exec", "login", "home", "say", "tp"):
            A[k][:] = []
    A["online"].add(KO)
    # ---- bug 1: died on the own island and still there -> 4, no goHome (no second teleport)
    A["where"][KO] = W
    r = int(Life.respawn(JString(W), uO, JString(W)))
    K.check(r == 4 and not A["home"], "RESP bug 1: died on the own island, the engine respawned them there -> 4, goHome NOT called (no second teleport)")
    gen = open(os.path.join(HERE, "build_skyyislands_%s.py" % VERSION), encoding="utf-8").read()
    gh = gen[gen.index("public int goHome(String wn"):]
    gh = gh[:gh.index('}""")')]
    K.check(gh.index("if (w2 != null && w2 == from) return 4;") < gh.index("addComponent"), "RESP bug 1: IsleEng.goHome returns 4 for the same world before any Teleport")
    K.check("w2 == from" not in gh.split("return 4;", 1)[1] and "return -2" not in gh, "RESP review: goHome's dead same-world branches (2-block check, -2) are gone")
    rs = gen[gen.index("public static int respawn(String wn"):]
    K.check("g == -2" not in rs[:rs.index('}""")')], "RESP review: respawn() no longer waits for goHome's -2")
    # ---- bug 2: deaths in the hub / zones go home
    for dw in (HUB, "skywynn_zones2", "default"):
        clear()
        A["where"][KO] = dw
        r = int(Life.respawn(JString(dw), uO, JString(dw)))
        K.check(r == 1 and A["home"] == [(dw, W)], "RESP bug 2: died in %s -> the island trip (route 1, goHome to %s): %s %s" % (dw, W, r, A["home"]))
    clear()
    A["where"][KO] = "skyy-shard-" + KO
    K.check(int(Life.respawn(JString("skyy-shard-" + KO), uO, JString("skyy-shard-" + KO))) == 0 and not A["home"], "RESP a shard death keeps the shard's respawn")
    K.check(bool(Life.keepWorld(JString(HUB))) and not bool(Life.deathKeep(JString(HUB))), "RESP logins in the zones still stay (respawnKeep), deaths there go home")
    Cfg.DEATH_KEEP = "skyy-shard-,skywynn_z"
    clear()
    A["where"][KO] = HUB
    K.check(int(Life.respawn(JString(HUB), uO, JString(HUB))) == 0 and not A["home"], "RESP Server Setup deathKeep + skywynn_z -> zone deaths keep the zone again (A/B)")
    Cfg.DEATH_KEEP = "skyy-shard-"
    A["beds"].add(HUB)
    clear()
    K.check(int(Life.respawn(JString(HUB), uO, JString(HUB))) == 0 and not A["home"], "RESP a bed set where they died still wins (unchanged)")
    A["beds"].clear()
    # ---- retries: 1 / 2 / 3 / 4 s, then give up loudly
    A["where"][KO] = "nowhere"
    delays = []
    t = Task(4, JString("other"), uO)
    t.a = JString(HUB)
    for k in range(5):
        clear()
        t.fl = k
        t.run()
        delays.append(A["later"][0][1] if A["later"] else None)
    K.eq(delays, [1000, 2000, 3000, 4000, None], "RESP bug 2: not in that world yet -> tried again 1 / 2 / 3 / 4 s later (0.5.19: once)")
    K.check(len(A["say"]) == 1 and "/island" in A["say"][0] and not A["login"], "RESP after the 4th retry: the chat line '%s'" % (A["say"] and A["say"][0]))
    clear()
    t.fl, t.login = 4, True
    t.run()
    K.check(not A["say"] and A["login"] == [KO], "RESP a parked login trip that gives up: no chat line, the login routing runs")
    t.login = False
    clear()
    del A["where"][KO]
    t5 = Task(5, JString(HUB), uO)
    t5.fl = 2
    t5.run()
    K.check(len(A["later"]) == 1 and A["later"][0][1] == 3000 and int(A["later"][0][0].fl) == 3, "RESP mode 5 between worlds: the retry carries on (3 s, try 3)")
    clear()
    t5.fl = 4
    t5.run()
    K.check(not A["later"] and len(A["say"]) == 1, "RESP mode 5 still between worlds after 4 retries: gives up with the chat line")
    # ---- the bed trip: bedSpot (the engine's rule) + modes 13 -> 14
    bl = A["blocks"]
    for x in range(-4, 9):
        for z in range(-4, 9):
            bl[(x, 128, z)] = "Soil_Grass"
    for c in ((2, 129, 2), (3, 129, 2), (2, 129, 3), (3, 129, 3), (2, 129, 4), (3, 129, 4)):
        bl[c] = "Furniture_Human_Ruins_Bed"
    s = Life.bedSpot(JString(W), 6.5, 129.0, 6.5, 6, 129, 6)
    K.eq([float(v) for v in s], [6.5, 129.0, 6.5], "BED the respawn spot free (feet + head air, grass under) -> exactly there")
    s = Life.bedSpot(JString(W), 2.5, 129.56, 2.5, 2, 129, 2)
    K.eq([float(v) for v in s], [1.5, 129.0, 1.5], "BED on the bed's own cell -> the first free ring cell (1,129,1) beside it (engine rule)")
    bl[(1, 129, 1)] = "Rock_Stone_Brick"
    s = Life.bedSpot(JString(W), 2.5, 129.56, 2.5, 2, 129, 2)
    K.eq([float(v) for v in s], [1.5, 129.0, 2.5], "BED a wall beside the bed -> the next ring cell (bug 2: 'had to move the bed')")
    bl[(1, 129, 2)] = "Plant_Grass_Lush_Short"
    s = Life.bedSpot(JString(W), 2.5, 129.56, 2.5, 2, 129, 2)
    K.eq([float(v) for v in s], [1.5, 129.0, 2.5], "BED a grass tuft is no wall")
    A["fluid"][(1, 129, 2)] = 7
    s = Life.bedSpot(JString(W), 2.5, 129.56, 2.5, 2, 129, 2)
    K.eq([float(v) for v in s], [1.5, 129.0, 3.5], "BED review: water at the feet is no landing spot -> the next ring cell")
    A["fluid"].clear()
    A["fluid"][(1, 130, 2)] = 7
    s = Life.bedSpot(JString(W), 2.5, 129.56, 2.5, 2, 129, 2)
    K.eq([float(v) for v in s], [1.5, 129.0, 3.5], "BED review: water at the head is no landing spot either")
    A["fluid"].clear()
    A["unl"].add((2, 130, 2))
    K.check(Life.bedSpot(JString(W), 2.5, 129.56, 2.5, 2, 129, 2) is None, "BED a cell not loaded -> null (the raw spot one up)")
    A["unl"].clear()
    saved = dict(bl)
    for x in range(-1, 6):
        for z in range(-1, 6):
            for y in (129, 130, 131):
                bl.setdefault((x, y, z), "Rock_Stone")
    s = Life.bedSpot(JString(W), 2.5, 129.56, 2.5, 2, 129, 2)
    K.eq([round(float(v), 2) for v in s], [2.5, 130.56, 2.5], "BED no free cell at all -> the raw position one block up")
    bl.clear()
    bl.update(saved)
    clear()
    t13 = Task(13, JString(W), uO)
    t13.a, t13.x, t13.y, t13.z, t13.bx, t13.by, t13.bz = JString(HUB), 2.5, 129.56, 2.5, 2, 129, 2
    t13.run()
    K.check(len(A["exec"]) == 1 and A["exec"][0][0] == HUB and int(A["exec"][0][1].mode) == 14 and str(A["exec"][0][1].ks[0]) == W
            and (float(A["exec"][0][1].x), float(A["exec"][0][1].y), float(A["exec"][0][1].z)) == (1.5, 129.0, 2.5),
            "BED IsleTask 13 (the island's thread) -> 14 on the player's world with the checked spot")
    A["exec"][0][1].run()
    K.eq(A["tp"], [(HUB, W, 1.5, 129.0, 2.5)], "BED IsleTask 14 -> IsleApi.teleport(player's world, island, the spot)")
    clear()
    A["tpr"] = 0
    A["exec"][0:0] = []
    t14 = Task(14, JString(HUB), uO)
    t14.ks, t14.x, t14.y, t14.z = [JString(W)], 1.5, 129.0, 2.5
    t14.run()
    K.check(len(A["say"]) == 1 and "/island" in A["say"][0], "BED review: the teleport could not deliver (not there / still dead) -> the chat line")
    A["tpr"] = -1
    clear()
    t14.run()
    K.check(len(A["say"]) == 1, "BED review: the teleport failed (-1) -> WARN + the chat line")
    A["tpr"] = 1
    A["execok"] = False
    clear()
    t13.run()
    K.check(len(A["say"]) == 1 and len(A["exec"]) == 1, "BED review: the player's world gone (exec refused) -> WARN + the chat line")
    A["execok"] = True
    K.check("@PKG@.IsleTask bt = new @PKG@.IsleTask(13, home, u);" in gh and "if (exec(home, bt)) return 1;" in gh, "BED goHome hands a bed trip to the island's thread")
    Life.API = None
    K.save()


# ================================================================================================ TIME
def run_time(out, jar, scratch, _home):
    from jpype import JClass, JString, JLong, JInt
    K = HK.Child(out)
    E = Env(scratch, jar, "time")
    Cfg, Life, Task = E.Cfg, E.Life, E.Task
    A = {"exec": [], "gt": {}, "fl": {}, "set": [], "tw": set()}
    NOW = [10000000]

    class Api(object):
        def now(self):
            return JLong(NOW[0])

        def hubWorld(self):
            return JString(HUB)

        def exec(self, wn, r):
            A["exec"].append((str(wn), r))
            return True

        def gameTime(self, wn):
            return JLong(A["gt"].get(str(wn), -9223372036854775808))

        def timeFlags(self, wn):
            return JInt(A["fl"].get(str(wn), 0))

        def setGameTime(self, wn, ms):
            A["set"].append((str(wn), int(ms)))
            return True

        def timeWorlds(self):
            s = JClass("java.util.HashSet")()
            for w in A["tw"]:
                s.add(JString(w))
            return s
    Life.API = stand_in(PKG + "IsleApi", Api())
    Cfg.SYNC_TIME = True
    H = 5 * 86400000 + 6 * 3600000
    Life.SNAP_MS, Life.SNAP_F, Life.SNAP_AT = H, 0, NOW[0] - 5000
    for wn, want in (("skyy-island-x", 1), ("skyy-shard-x", 1), ("skywynn_zones2", 1), (HUB, 0), ("default", 0)):
        A["exec"][:] = []
        r = int(Life.onJoin(JString(wn), NOW[0]))
        ok = r == want and (want == 0 and not A["exec"] or want == 1 and A["exec"][0][0] == wn and int(A["exec"][0][1].mode) == 15 and int(A["exec"][0][1].ms) == H)
        K.check(ok, "TIME onJoin %s -> %s (IsleTask 15 with the hub's reading on that world's thread)" % (wn, "the arrival jump" if want else "nothing"))
    for why, setup in (("stale (70 s old)", lambda: setattr(Life, "SNAP_AT", NOW[0] - 70000)), ("the hub paused", lambda: setattr(Life, "SNAP_F", 1)),
                       ("sync off", lambda: setattr(Cfg, "SYNC_TIME", False)), ("no reading yet", lambda: setattr(Life, "SNAP_AT", 0))):
        Life.SNAP_MS, Life.SNAP_F, Life.SNAP_AT = H, 0, NOW[0] - 5000
        Cfg.SYNC_TIME = True
        setup()
        A["exec"][:] = []
        K.check(int(Life.onJoin(JString("skyy-island-x"), NOW[0])) == 0 and not A["exec"], "TIME onJoin with the reading %s -> nothing" % why)
    Cfg.SYNC_TIME = True
    for d, want, why in ((-20 * 60000, True, "20 game minutes behind -> forward to the hub"), (-5 * 60000, False, "5 minutes behind -> left to the sync"),
                         (3 * 3600000, False, "ahead -> never backwards")):
        A["set"][:] = []
        A["gt"]["skyy-island-x"] = H + d
        A["fl"]["skyy-island-x"] = 0
        r = int(Life.joinSync(JString("skyy-island-x"), H))
        K.check((r == 1 and A["set"] == [("skyy-island-x", H)]) if want else (r == 0 and not A["set"]), "TIME joinSync %s" % why)
    A["set"][:] = []
    A["gt"]["skyy-island-x"] = H - 3600000
    A["fl"]["skyy-island-x"] = 2
    K.check(int(Life.joinSync(JString("skyy-island-x"), H)) == 0 and not A["set"], "TIME joinSync in a bed skip -> left alone")
    # timeAll with nobody to sync: the hub's clock read every 10 s
    A["exec"][:] = []
    Life.HUBQ = 0
    Life.SNAP_AT = NOW[0] - 20000
    Life.timeAll(NOW[0])
    K.check(len(A["exec"]) == 1 and A["exec"][0][0] == HUB and int(A["exec"][0][1].mode) == 12 and len(A["exec"][0][1].ks) == 0,
            "TIME timeAll with no island to sync still reads the hub's clock (IsleTask 12, no worlds)")
    A["exec"][:] = []
    Life.timeAll(NOW[0] + 3000)
    K.check(not A["exec"], "TIME ... not again within 10 s")
    A["gt"][HUB] = H + 777
    A["fl"][HUB] = 0
    NOW[0] += 1000
    Life.timeHub(JString(HUB), None)
    K.check(int(Life.SNAP_MS) == H + 777 and int(Life.SNAP_AT) == NOW[0] and int(Life.HUBQ) == 0, "TIME timeHub stores the hub's reading (the hub's thread)")
    # bytecode: zones in timeWorlds, the listener registered
    pool = JClass("javassist.ClassPool")(True)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cn, mn):
        bos = BOS()
        for mm in pool.get(PKG + cn).getDeclaredMethods():
            if str(mm.getName()) == mn:
                IP(PS(bos)).print_(mm)
        return str(bos.toString())
    K.check('"skywynn_z"' in code("IsleEng", "timeWorlds"), "TIME IsleEng.timeWorlds takes skywynn_z (zone) worlds")
    su = code("SkyyIslandsPlugin", "setup")
    K.check("AddPlayerToWorldEvent" in su and "IslandJoin" in su, "TIME setup registers IslandJoin for AddPlayerToWorldEvent")
    K.check("IsleLife.onJoin" in code("IslandJoin", "accept"), "TIME IslandJoin.accept -> IsleLife.onJoin")
    Life.API = None
    K.save()


# ================================================================================================ CLEAR
def run_clear(out, jar, scratch, _home):
    from jpype import JClass, JString, JLong, JInt
    K = HK.Child(out)
    E = Env(scratch, jar, "clear")
    St, Cfg, Life = E.St, E.Cfg, E.Life
    E.files({KO: {"v": "5", "world": WC, "isles": "3", "camp.done": "1"}})
    camp, boss = [float(v) for v in Life.CAMP], [float(v) for v in Life.BOSS]
    A = {"rm": [], "near": {}, "shard": 0}

    class Api(object):
        def now(self):
            return JLong(1)

        def remove(self, wn, uuid):
            A["rm"].append(str(uuid))
            return True

        def npcs(self, wn, x, y, z, r):
            l = JClass("java.util.ArrayList")()
            for (cx, cz), ents in A["near"].items():
                if abs(float(x) - cx) < 1 and abs(float(z) - cz) < 1:
                    for e in ents:
                        l.add(JClass("java.lang.Object")[:]([JString(e[0]), JString(e[1])]))
            return l

        def count(self, wn, u, item):
            return JLong(A["shard"])

        def questDone(self, owner, task):
            return JInt(0)
    Life.API = stand_in(PKG + "IsleApi", Api())
    A["near"][(camp[0], camp[2])] = [("c3", "Skeleton_Fighter"), ("cow", "Cow")]
    A["near"][(boss[0], boss[2])] = [("b1", "Golem_Crystal_Earth")]
    mem = JClass("java.util.ArrayList")()
    Cfg.CAMP_CLEAR, Cfg.CAMP_STOP, Cfg.BOSS_STOP = True, True, True
    st = Life.state(JString(WC))
    st.camp.add(JString("c1"))
    st.camp.add(JString("c2"))
    n = int(Life.clearTick(JString(WC), st, mem, 100000))
    K.check(n == 2 and sorted(A["rm"]) == ["c1", "c2"] and st.camp.size() == 0,
            "CLEAR camp done -> the TRACKED skeletons removed; an untracked same-role skeleton (another mod's / a pet) and the cow stay: %s" % A["rm"])
    A["rm"][:] = []
    K.check(int(Life.clearTick(JString(WC), st, mem, 105000)) == 0 and not A["rm"], "CLEAR at most every 10 s")
    E.files({KO: {"v": "5", "world": WC, "isles": "3", "camp.done": "1", "boss.done": "1"}})
    st.clearAt = 0
    st.bossDone = False
    st.boss = JString("b0")
    A["rm"][:] = []
    Life.clearTick(JString(WC), st, mem, 200000)
    K.check("b1" not in A["rm"] and "b0" not in A["rm"], "CLEAR boss.done but the portal broken and nobody holds a Hub Shard -> the Shardkeeper stays (needed)")
    E.files({KO: {"v": "5", "world": WC, "isles": "3", "camp.done": "1", "boss.done": "1", "portal": "1"}})
    st.clearAt = 0
    A["rm"][:] = []
    Life.clearTick(JString(WC), st, mem, 300000)
    K.check(A["rm"] == ["b0"] and st.boss is None, "CLEAR boss done + portal repaired -> the tracked Shardkeeper removed, an untracked Golem_Crystal_Earth (a pet golem) kept: %s" % A["rm"])
    E.files({KO: {"v": "5", "world": WC, "isles": "3", "camp.done": "1"}})
    st4 = Life.state(JString(WC))
    st4.clearAt = 0
    st4.campDone = True
    st4.camp.add(JString("c9"))
    Cfg.CAMP_ON = False
    A["rm"][:] = []
    Life.clearTick(JString(WC), st4, mem, 500000)
    K.check(not A["rm"], "CLEAR review: camp.enabled off -> no sweep")
    Cfg.CAMP_ON = True
    st4.camp.clear()
    E.files({KO: {"v": "5", "world": WC, "isles": "3"}})
    st3 = Life.state(JString(WC))
    st3.campDone, st3.bossDone, st3.clearAt = False, False, 0
    st3.questAt = 299000
    st3.bossAt = 299000
    A["rm"][:] = []
    Life.clearTick(JString(WC), st3, mem, 300000)
    K.check(not A["rm"], "CLEAR camp / boss not done -> nothing removed")
    Cfg.CAMP_CLEAR = False
    st.clearAt = 0
    A["rm"][:] = []
    K.check(int(Life.clearTick(JString(WC), st, mem, 400000)) == 0 and not A["rm"], "CLEAR the setting off -> nothing (0.5.19)")
    Cfg.CAMP_CLEAR = True
    gen = open(os.path.join(HERE, "build_skyyislands_%s.py" % VERSION), encoding="utf-8").read()
    tw = gen[gen.index("public static int tickWorld(String wn)"):]
    K.check(tw.index("clearTick(") < tw.index("campTick(") and "pondOnce(" in tw, "CLEAR tickWorld runs clearTick (before campTick) and pondOnce")
    Life.API = None
    K.save()


# ================================================================================================ POND
def run_pond(out, jar, scratch, _home):
    from jpype import JClass, JString, JLong
    K = HK.Child(out)
    m = layout_of(VERSION)
    m19 = layout_of(OLD)
    L, LO, cells, water, cols = m.S3_L, m.S3_L_OLD, m.S3_POND_CELLS, m.S3_POND_WATER, m.S3_POND_COLS
    K.eq(LO, m19.S3_L, "LAYOUT S3_L_OLD = the 0.5.19 build's layout exactly")
    diff = set(k for k in set(L) | set(LO) if L.get(k) != LO.get(k))
    K.check(diff <= set(c[:3] for c in cells) and len(cells) == 179 and len(water) == 46 and len(cols) == 19,
            "LAYOUT only pond cells differ (%d changed of %d checked; 46 water; 19 columns)" % (len(diff), len(cells)))
    ws = set(water)
    K.check(all(p not in L for p in ws), "LAYOUT the water cells are empty in the block layout (fluids are placed by pondOnce)")
    leak = [(p, q) for p in ws for q in ((p[0] + 1, p[1], p[2]), (p[0] - 1, p[1], p[2]), (p[0], p[1], p[2] + 1), (p[0], p[1], p[2] - 1), (p[0], p[1] - 1, p[2]))
            if q not in ws and (q not in L or L[q].startswith("Plant_"))]
    K.check(not leak, "LAYOUT every water cell has water or a solid block on 4 sides and below: %s" % leak[:3])
    depth = dict(((x, z), len([1 for (a, y, b) in ws if (a, b) == (x, z)])) for (x, z) in cols)
    K.check(set(depth.values()) == {2, 3} and min(depth.values()) >= 2 and all((x, 128, z) in ws for x, z in cols),
            "LAYOUT 2-3 deep everywhere (SkyyFishing fish.minDepth 2), the water line flush at y 128: %s" % sorted(set(depth.values())))
    K.check(all(depth[(x, z)] >= 2 for x in (2, 3, 4) for z in (8, 9, 10)), "LAYOUT a 3 x 3 block of fishable water (fish 3 wide)")
    K.check(all((x, 129, z) not in L and (x, 130, z) not in L for x, z in cols), "LAYOUT nothing over the water")
    near = lambda p, q, r: abs(p[0] - q[0]) <= r and abs(p[1] - q[1]) <= r
    K.check(not [c for c in cols if near(c, (8, 8), 2)], "LAYOUT 2 blocks of grass between the spawn (8.5, 8.5) and the pond")
    K.check(not [c for c in cols if c in [(b[0], b[2]) for b in m.S3_BED_CELLS] or near(c, (4, 4), 1) or (11 <= c[0] <= 13 and 2 <= c[1] <= 5)
                 or c in m.S3_CAVE_FRONT or c[0] >= 9], "LAYOUT off the bed, chest, plot, cave front and the east path to island 2")
    plants = [c for c in cells if c[4].startswith("Plant_")]
    K.check(len(plants) == 4 and all(c[3] == "" and LO.get((c[0], 128, c[2])) == "Soil_Grass" for c in plants), "LAYOUT 3 reeds + a fern on free rim grass")
    # the jars' own layout data
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    S, Life, St, Cfg = P("StarterIsles"), P("IsleLife"), P("IslandStore"), P("IslandCfg")
    runs = list(S.decode())
    pal = [str(x) for x in S.PAL] if hasattr(S, "PAL") else None
    dec = {}
    if pal is not None:
        for i in range(0, len(runs), 5):
            for k in range(runs[i + 4]):
                dec[(runs[i + 1] + k, runs[i + 2], runs[i + 3])] = pal[runs[i]]
        K.eq(dec, L, "JAR StarterIsles in the 0.5.20 jar decodes to the build's new layout")
    else:
        K.notes.append("StarterIsles.PAL not found - decode compared by size only")
        K.check(sum(runs[i + 4] for i in range(0, len(runs), 5)) == len(L), "JAR StarterIsles block count = the new layout")
    K.eq([(int(Life.POND_C[i * 3]), int(Life.POND_C[i * 3 + 1]), int(Life.POND_C[i * 3 + 2]), str(Life.POND_OLD[i]), str(Life.POND_NEW[i])) for i in range(len(Life.POND_OLD))],
         [tuple(c) for c in cells], "JAR IsleLife.POND_C / OLD / NEW = the build's cells")
    K.eq([tuple(int(Life.POND_W[i + j]) for j in range(3)) for i in range(0, len(Life.POND_W), 3)], [tuple(w) for w in water], "JAR IsleLife.POND_W = the water cells")
    # ---- pondOnce EXECUTED
    E = Env(scratch, jar, "pond")
    keys = {}
    for i, why in enumerate(("old", "new", "player", "unloaded", "hole", "off", "done", "pit", "dry", "midset", "midwater", "cap")):
        keys[why] = "00000000-0000-4000-8000-00000c0520%02d" % i
    E.files(dict((k, {"v": "5", "world": "skyy-island-pond-" + why, "isles": "3"}) for why, k in keys.items()))
    A = {"w": {}, "water": {}, "set": 0, "reads": 0, "unl": set(), "fail": set(), "wfail": set(), "canw": True}

    class Api(object):
        def block(self, wn, x, y, z):
            A["reads"] += 1
            p = (int(x), int(y), int(z))
            if p in A["unl"]:
                return None
            return JString(A["w"][str(wn)].get(p, ""))

        def setBlock(self, wn, x, y, z, bid):
            p = (int(x), int(y), int(z))
            if p in A["fail"] and not str(bid):
                return False
            A["set"] += 1
            if str(bid):
                A["w"][str(wn)][p] = str(bid)
            else:
                A["w"][str(wn)].pop(p, None)
            return True

        def setWater(self, wn, x, y, z):
            if (int(x), int(y), int(z)) in A["wfail"]:
                return False
            A["water"].setdefault(str(wn), set()).add((int(x), int(y), int(z)))
            return True

        def canWater(self, wn, x, y, z):
            return A["canw"]

        def save(self, r):
            r.run()
            return True
    Life.API = stand_in(PKG + "IsleApi", Api())
    Cfg.POND_ON = True
    pc = [c[:3] for c in cells]

    def world(why, base):
        wn = "skyy-island-pond-" + why
        A["w"][wn] = dict(base)
        return wn, Life.state(JString(wn))

    def run(why, wn, st, now=1000000):
        A["set"] = 0
        return int(Life.pondOnce(JString(wn), JString(keys[why]), st, now))
    wn, st = world("old", LO)
    r = run("old", wn, st)
    got = A["w"][wn]
    K.check(r == 1 and all(got.get(c[:3], "") == c[4] for c in cells) and A["water"].get(wn) == ws and E.prop(keys["old"], "pond.placed") == "1",
            "POND an existing natural island -> dug, floored, planted (%d blocks) + %d water, pond.placed=1" % (A["set"], len(A["water"].get(wn, ()))))
    K.check(A["set"] == sum(1 for c in cells if c[3] != c[4]), "POND exactly the cells that differ were set (%d)" % A["set"])
    K.check(run("old", wn, st, 2000000) == 0 and A["set"] == 0, "POND never again (memory)")
    st_b = Life.state(JString(wn + "-again"))
    E.St.SETTINGS.clear()
    K.check(int(Life.pondOnce(JString(wn), JString(keys["old"]), st_b, 3000000)) == 0 and A["set"] == 0, "POND never again (pond.placed=1 in the island file)")
    wn, st = world("new", L)
    r = run("new", wn, st)
    K.check(r == 1 and A["set"] == 0 and A["water"].get(wn) == ws, "POND a new / reset island (the layout's basin) -> water only, no block changed")
    wn, st = world("player", LO)
    f = [c for c in cells if c[3] == "Soil_Dirt" and c[4] == "Soil_Clay"][0]
    A["w"][wn][f[:3]] = "Wood_Oak_Planks"
    r = run("player", wn, st)
    K.check(r == 0 and A["set"] == 0 and wn not in A["water"] and E.prop(keys["player"], "pond.placed") == "skip" and bool(st.pondDone),
            "POND a player's block in the spot -> skipped for good, nothing changed (pond.placed=skip)")
    wn, st = world("unloaded", LO)
    A["unl"] = set([pc[50]])
    r = run("unloaded", wn, st)
    K.check(r == 0 and A["set"] == 0 and wn not in A["water"] and E.prop(keys["unloaded"], "pond.placed") is None and not bool(st.pondDone),
            "POND a cell not loaded -> nothing yet (no verdict)")
    A["unl"] = set()
    A["reads"] = 0
    K.check(run("unloaded", wn, st, 1005000) == 0 and A["reads"] == 0, "POND looked at again only after 10 s")
    K.check(run("unloaded", wn, st, 1011000) == 1 and A["water"].get(wn) == ws, "POND ... then placed once loaded")
    wn, st = world("hole", LO)
    rim = [c for c in cells if c[3] == c[4] and c[3] in ("Soil_Dirt", "Soil_Grass")][0]
    del A["w"][wn][rim[:3]]
    r = run("hole", wn, st)
    K.check(r == 0 and A["set"] == 0 and wn not in A["water"] and E.prop(keys["hole"], "pond.placed") is None and not bool(st.pondDone),
            "POND a hole dug in the spot (air where ground should be) -> wait, never filled, never drained into")
    A["reads"] = 0
    K.check(run("hole", wn, st, 1010000) == 0 and A["reads"] == 0, "POND review: a hole backs off (no look 10 s later) ...")
    K.check(run("hole", wn, st, 1020000) == 0 and A["reads"] > 0 and A["set"] == 0, "POND ... looks again after 20 s, still nothing changed")
    # review: a player's own pit at exactly the pond's water cells (the floor still the old ground) = wait, never filled
    wn, st = world("pit", LO)
    for wc in water:
        A["w"][wn].pop(tuple(wc), None)
    r = run("pit", wn, st)
    K.check(r == 0 and A["set"] == 0 and wn not in A["water"] and E.prop(keys["pit"], "pond.placed") is None and not bool(st.pondDone),
            "POND review: a player's pit at the exact water cells (no inprogress marker, old floor) -> NOT taken as ours, nothing filled")
    # review: the water dry run fails BEFORE anything is dug -> nothing changed, looked at again, gives up after 5 looks
    wn, st = world("dry", LO)
    A["canw"] = False
    t0 = 1000000
    for k in range(5):
        run("dry", wn, st, t0 + k * 11000)
    K.check(A["w"][wn] == LO and wn not in A["water"] and E.prop(keys["dry"], "pond.placed") == "gaveup" and bool(st.pondDone),
            "POND review: the water cannot be placed -> nothing dug, ever; after 5 looks pond.placed=gaveup (logged)")
    A["canw"] = True
    # review: a dig fails mid-run -> inprogress kept, the next look finishes it (no half pit left for good)
    wn, st = world("midset", LO)
    A["fail"] = set([tuple(water[0])])
    r = run("midset", wn, st)
    K.check(r == 0 and E.prop(keys["midset"], "pond.placed") == "inprogress.1" and not bool(st.pondDone), "POND review: a dig fails mid-run -> pond.placed=inprogress.1 (ours to finish)")
    A["fail"] = set()
    r = run("midset", wn, st, 1011000)
    got = A["w"][wn]
    K.check(r == 1 and all(got.get(c[:3], "") == c[4] for c in cells) and A["water"].get(wn) == ws and E.prop(keys["midset"], "pond.placed") == "1",
            "POND review: ... resumed on the next look (inprogress = air in the dug cells is ours) -> the whole pond, pond.placed=1")
    # review: a water fill fails right after its dig -> that block is put back, the next look finishes
    wn, st = world("midwater", LO)
    wc0 = tuple(water[-1])
    A["wfail"] = set([wc0])
    r = run("midwater", wn, st)
    K.check(r == 0 and A["w"][wn].get(wc0) == LO.get(wc0) and E.prop(keys["midwater"], "pond.placed") == "inprogress.1",
            "POND review: a failed fill puts its dug block back (no dry hole), inprogress kept")
    A["wfail"] = set()
    K.check(run("midwater", wn, st, 1011000) == 1 and A["water"].get(wn) == ws, "POND review: ... and the next look finishes it")
    # review: a run that keeps stopping gives up (logged) after 3 runs, nothing more changed
    E.files({keys["cap"]: {"v": "5", "world": "skyy-island-pond-cap", "isles": "3", "pond.placed": "inprogress.3"}})
    wn, st = world("cap", LO)
    K.check(run("cap", wn, st) == 0 and A["set"] == 0 and E.prop(keys["cap"], "pond.placed") == "gaveup" and bool(st.pondDone),
            "POND review: inprogress.3 -> gaveup (logged), nothing more changed")
    wn, st = world("off", LO)
    Cfg.POND_ON = False
    K.check(run("off", wn, st) == 0 and A["reads"] >= 0 and A["set"] == 0 and wn not in A["water"], "POND the setting off -> nothing")
    Cfg.POND_ON = True
    E.files({keys["done"]: {"v": "5", "world": "skyy-island-pond-done", "isles": "3", "pond.placed": "1"}})
    wn, st = world("done", LO)
    K.check(run("done", wn, st) == 0 and A["set"] == 0 and wn not in A["water"], "POND an island file with pond.placed=1 -> nothing")
    Life.API = None
    K.save()


# ================================================================================================ LIVE
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    h0 = HK.tree_hash(home)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    St, Cfg = P("IslandStore"), P("IslandCfg")
    Paths = JClass("java.nio.file.Paths")
    St.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyIslands")
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    Cfg.load("")
    K.eq((str(Cfg.DEATH_KEEP), bool(Cfg.CAMP_CLEAR), bool(Cfg.POND_ON)), ("skyy-shard-", True, True), "LIVE the live config (no new lines) = the new defaults")
    K.check(str(Cfg.RESPAWN_KEEP) == "skyy-shard-,skywynn_z" and bool(Cfg.SYNC_TIME), "LIVE respawnKeep / syncTime as the live file says")
    St.DIR = Paths.get(os.path.join(home, "islands"))
    St.IO = None
    St.STOPPING = False
    St.loadIslandWorlds()
    d = os.path.join(home, "islands")
    owners = [f[:-11] for f in sorted(os.listdir(d)) if f.endswith(".properties")]
    three = 0
    for k in owners:
        s = St.settings(k)
        K.check(s is not None and not bool(s.bad), "LIVE island file %s reads" % k[:12])
        if s.raw is not None and str(s.raw.getProperty("isles", "")) == "3":
            three += 1
        K.check(s.raw is None or s.raw.getProperty("pond.placed") is None, "LIVE %s: no pond yet (gets it on the next visit if the spot is untouched)" % k[:12])
    K.notes.append("live: %d island files, %d with 3 islands" % (len(owners), three))
    K.check(HK.tree_hash(home) == h0, "LIVE no file of the copy changed (load writes nothing)")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("cfg", run_cfg), ("resp", run_resp), ("time", run_time), ("clear", run_clear), ("pond", run_pond), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyIslands"))
