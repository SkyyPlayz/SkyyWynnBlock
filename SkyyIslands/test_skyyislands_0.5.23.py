"""Harness for SkyyIslands 0.5.23 (bug 4 part 1: a death that goes home respawns straight onto the island; tools/islands_0_5_23_patch.py).
Build first: python tools/islands_0_5_23_patch.py && python SkyyIslands/build_skyyislands_0.5.23.py

    python SkyyIslands/test_skyyislands_0.5.23.py [--jar <jar>] [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; stand-in IsleApi = a Python JProxy, real IslandStore files in scratch, -Xverify:all):
  A / C / AA  verify, compare 0.5.22 -> 0.5.23 (exactly the planned members + the new IsleRespawnEvt; only the manifest changes), audit
  EARLY IsleLife.early on the RespawnEvent: a zone death (no bed there) with the island loaded -> the vanilla respawn cancelled + ONE
        earlyTrip; a second click cancelled without a second trip; a stale one (> 10 s) starts again; landDead: done (counted, EARLY
        cleared) / failed while dead (-> revive, the one-shot BYPASS lets the vanilla respawn through once) / not dead (nothing);
        bedLand with the dead flag = the respawn (never the plain teleport); every 0.5.22 rule untouched: a death on the island, a bed
        where they died, islands.deathKeep, no island (hub route), island not loaded (earlyTrip 0), the setting off -> 0 (vanilla)
  IDS / BOSS / TIME / CLEAR  the 0.5.22 phases again (regression)
  LIVE  a scratch COPY of the live Skyy_SkyyIslands: every island file reads; nothing changed
Not testable without the game (UNVERIFIED): the client going straight from the death screen to the island (one JoinWorld), the death page
closing on our removal (vanilla ClearRespawnUI), the ECS order vs vanilla's PlayerLives hook (we read PlayerLives ourselves).
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.5.23"
OLD = "0.5.22"
PKG = "com.skyy.islands."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "i523", "h")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyIslands")
ADDED = ["IsleRespawnEvt"]
EXPECT = {
    "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "IslandCfg": ["~m load"],   # the config kit's version text only
    "IsleApi": ["+m earlyTrip", "+m respawnTo", "+m revive"],
    "IsleEng": ["+m earlyTrip", "+m respawnTo", "+m revive"],
    "IsleTask": ["+f dead", "~m run"],
    "IsleLife": ["+f EARLY", "+f BYPASS", "+f EARLYN", "+f EARLY_TTL", "+f EARLY_WAIT", "+f EARLY_OLD", "+f DONE", "+f EARLY_NET", "~<clinit>", "~m respawn", "+m revive", "+m landDead", "+m early", "~m bedTrip",
                 "~m bedLand", "~m respawnLog"],
    "SkyyIslandsPlugin": ["~m setup"],
}
KO = "00000000-0000-4000-8000-0000000b0522"
WC = "skyy-island-camp22"
U = ["00000000-0000-4000-8000-00000000c%03d" % i for i in range(10)]


def run_compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """the kit's compare; its non-class check: only the manifest may change"""
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
        self.St, self.Cfg, self.Life = P("IslandStore"), P("IslandCfg"), P("IsleLife")
        self.Paths = JClass("java.nio.file.Paths")
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


class Api(object):
    """the stand-in engine: A['alive'] = live ids, A['loaded'] = ids whose chunk is loaded (remove works), A['near'] = npcs()"""

    def __init__(self, A):
        self.A = A

    def now(self):
        from jpype import JLong
        return JLong(1)

    def remove(self, wn, uuid):
        u = str(uuid)
        self.A["tried"].append(u)
        if u in self.A["loaded"] and u in self.A["alive"]:
            self.A["rm"].append(u)
            self.A["alive"].discard(u)
            return True
        return False

    def alive(self, wn, uuid):
        return uuid is not None and str(uuid) in self.A["alive"]

    def npcs(self, wn, x, y, z, r):
        from jpype import JClass, JString
        l = JClass("java.util.ArrayList")()
        for (cx, cz), ents in self.A["near"].items():
            if abs(float(x) - cx) < 1 and abs(float(z) - cz) < 1:
                for e in ents:
                    l.add(JClass("java.lang.Object")[:]([JString(e[0]), JString(e[1])]))
        return l

    def count(self, wn, u, item):
        from jpype import JLong
        return JLong(self.A["shard"])

    def questDone(self, owner, task):
        from jpype import JInt
        return JInt(0)

    def save(self, t):
        self.A["saved"].append((str(t.a), [str(k) for k in t.ks], [None if v is None else str(v) for v in t.vs]))
        return True

    def level(self, wn, uuid, lvl, name):
        self.A["named"].append(str(uuid))
        return True

    def petOwned(self, uuid):
        return str(uuid) in self.A["pets"]

    def roleOk(self, role):
        return True

    def spawn(self, wn, role, x, y, z, yaw):
        from jpype import JString
        u = self.A["next"].pop(0)
        self.A["alive"].add(u)
        self.A["loaded"].add(u)
        self.A["spawned"].append(u)
        return JString(u)


def fresh_A():
    return {"rm": [], "tried": [], "alive": set(), "loaded": set(), "near": {}, "shard": 0, "saved": [], "named": [], "pets": set(),
            "next": [], "spawned": []}


def member(x, z):
    from jpype import JClass, JDouble
    mem = JClass("java.util.ArrayList")()
    mem.add(JClass("java.lang.Object")[:]([JClass("java.util.UUID").fromString(KO), JClass("java.lang.Double")(x),
                                           JClass("java.lang.Double")(130.0), JClass("java.lang.Double")(z)]))
    return mem


# ================================================================================================ IDS
def run_ids(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    E = Env(scratch, jar, "ids")
    Cfg, Life, IS = E.Cfg, E.Life, E.P("IsleState")
    camp, boss = [float(v) for v in Life.CAMP], [float(v) for v in Life.BOSS]
    Cfg.CAMP_CLEAR, Cfg.CAMP_STOP, Cfg.BOSS_STOP, Cfg.CAMP_ON, Cfg.BOSS_ON = True, True, True, True, True
    A = fresh_A()
    Life.API = stand_in(PKG + "IsleApi", Api(A))
    # --- load: good ids join, junk skipped; boss.id = ours
    E.files({KO: {"v": "5", "world": WC, "isles": "3", "camp.ids": "%s, junk,%s,," % (U[1], U[2]), "boss.id": U[5]}})
    st = IS(JString(WC))
    Life.loadIds(JString(WC), st, JString(KO))
    K.eq(sorted(str(x) for x in st.camp.toArray()), [U[1], U[2]], "IDS loadIds: the saved camp ids join (junk skipped)")
    K.check(str(st.boss) == U[5] and bool(st.bossMine), "IDS loadIds: the saved boss.id = OUR Shardkeeper")
    st.camp.clear()
    Life.loadIds(JString(WC), st, JString(KO))
    K.check(st.camp.size() == 0, "IDS loadIds runs once per world per run")
    st.camp.add(JString(U[1]))
    st.camp.add(JString(U[2]))
    Life.saveIds(JString(KO), st)
    K.eq(A["saved"], [], "IDS saveIds: nothing changed -> no write")
    st.camp.add(JString(U[3]))
    Life.saveIds(JString(KO), st)
    K.eq(A["saved"], [(KO, ["camp.ids", "boss.id"], [",".join(sorted([U[1], U[2], U[3]])), U[5]])], "IDS saveIds: a new camp id -> one write (sorted)")
    Life.saveIds(JString(KO), st)
    K.eq(len(A["saved"]), 1, "IDS saveIds: written only once per change")
    st.camp.clear()
    st.boss = None
    Life.saveIds(JString(KO), st)
    K.eq(A["saved"][-1], (KO, ["camp.ids", "boss.id"], [None, None]), "IDS saveIds: none left -> both keys removed")
    # --- after a "restart": the camp + boss done, the saved ids are swept
    E.files({KO: {"v": "5", "world": WC, "isles": "3", "camp.done": "1", "boss.done": "1", "portal": "1",
                  "camp.ids": "%s,%s,%s" % (U[1], U[2], U[3]), "boss.id": U[5]}})
    A = fresh_A()
    Life.API = stand_in(PKG + "IsleApi", Api(A))
    A["alive"].update([U[1], U[2], U[3], U[5], U[7]])
    A["loaded"].update([U[1], U[2], U[5], U[7]])          # U[3] is in a chunk that is not loaded
    A["near"][(camp[0], camp[2])] = [(U[7], "Skeleton_Fighter")]   # an untracked same-role skeleton (another mod's / pre-0.5.22)
    st = IS(JString(WC))
    Life.loadIds(JString(WC), st, JString(KO))
    far = member(boss[0] + 500, boss[2] + 500)
    n = int(Life.clearTick(JString(WC), st, far, 100000))
    K.check(n == 3 and sorted(A["rm"]) == sorted([U[1], U[2], U[5]]), "IDS after a restart: the saved camp ids + the saved Shardkeeper removed: %s" % A["rm"])
    K.check(U[7] not in A["tried"], "IDS an untracked same-role skeleton is never removed")
    K.eq([str(x) for x in st.camp.toArray()], [U[3]], "IDS a failed removal while nobody is near (not loaded) is KEPT")
    K.check(st.boss is None and not bool(st.bossMine), "IDS the removed Shardkeeper is forgotten")
    st.clearAt = 0
    A["loaded"].add(U[3])
    n = int(Life.clearTick(JString(WC), st, far, 200000))
    K.check(n == 1 and A["rm"][-1] == U[3] and st.camp.size() == 0, "IDS ... removed on a later pass once its chunk is loaded")
    st.camp.add(JString(U[8]))                            # gone for good (died while unloaded)
    st.clearAt = 0
    Life.clearTick(JString(WC), st, member(camp[0], camp[2]), 300000)
    K.check(st.camp.size() == 0, "IDS a failed removal with a member near (loaded = really gone) is forgotten")
    Life.saveIds(JString(KO), st)
    K.eq(A["saved"][-1][2], [None, None], "IDS after the sweep the island file keys are removed")
    # --- review guard: campAlive keeps a saved id that is not alive while nobody is near (not loaded); forgets it when near
    rl = JClass("java.lang.String")[:]([JString("Skeleton_Fighter")])
    st.camp.add(JString(U[9]))
    Life.campAlive(JString(WC), st, rl, False)
    K.check(st.camp.contains(JString(U[9])), "IDS campAlive: a saved id not alive while nobody is near (not loaded) is KEPT")
    Life.campAlive(JString(WC), st, rl, True)
    K.check(not st.camp.contains(JString(U[9])), "IDS campAlive: ... forgotten when a member is near (loaded = really gone)")
    gen0 = open(os.path.join(HERE, "build_skyyislands_%s.py" % VERSION), encoding="utf-8").read()
    K.check("campAlive(wn, st, rl, anyNear(mem, CAMP[0], CAMP[2], LOADED_R))" in gen0, "IDS campTick passes the near rule to campAlive")
    # --- /island reset clears the keys (the generated setWorldName0)
    gen = open(os.path.join(HERE, "build_skyyislands_%s.py" % VERSION), encoding="utf-8").read()
    sw = gen[gen.index("p.remove(\"pond.placed\");"):][:200]
    K.check('p.remove("camp.ids"); p.remove("boss.id");' in sw, "IDS /island reset removes camp.ids + boss.id")
    tw = gen[gen.index("public static int tickWorld(String wn)"):]
    tw = tw[:tw.index('}""")')]
    K.check(tw.index("three(wn") < tw.index("loadIds(") < tw.index("a.players(wn)") and tw.index("bossTick(") < tw.index("saveIds(owner, st)"),
            "IDS tickWorld: loadIds after the 3-island check, saveIds after the camp / boss ticks")
    Life.API = None
    K.save()


# ================================================================================================ BOSS
def run_boss(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    E = Env(scratch, jar, "boss")
    Cfg, Life, IS = E.Cfg, E.Life, E.P("IsleState")
    boss = [float(v) for v in Life.BOSS]
    Cfg.CAMP_CLEAR, Cfg.BOSS_STOP, Cfg.BOSS_ON = True, True, True
    E.files({KO: {"v": "5", "world": WC, "isles": "3"}})
    A = fresh_A()
    Life.API = stand_in(PKG + "IsleApi", Api(A))
    near = member(boss[0], boss[2])
    # a pet golem in the arena: skipped -> our boss spawns
    A["alive"].add(U[0])
    A["near"][(boss[0], boss[2])] = [(U[0], "Golem_Crystal_Earth")]
    A["pets"].add(U[0])
    A["next"] = [U[4]]
    st = IS(JString(WC))
    st.idsLoaded = True
    st.idsSaved = "|"
    r = int(Life.bossTick(JString(WC), st, near, 100000))
    K.check(r == 1 and str(st.boss) == U[4] and bool(st.bossMine) and U[0] not in A["named"],
            "BOSS a pet golem in the arena is skipped (not renamed); OUR Shardkeeper wakes and is bossMine")
    # a foreign same-role NPC (not a pet): blocks a second spawn, never renamed, never removed
    st2 = IS(JString(WC))
    A["pets"].clear()
    A["named"][:] = []
    A["next"] = [U[6]]
    r = int(Life.bossTick(JString(WC), st2, near, 100000))
    K.check(r == 0 and str(st2.boss) == U[0] and not bool(st2.bossMine) and not A["named"] and not A["spawned"][1:],
            "BOSS a foreign Golem_Crystal_Earth: tracked as blocking, NOT renamed, no second spawn")
    E.files({KO: {"v": "5", "world": WC, "isles": "3", "boss.done": "1", "portal": "1"}})
    st2.clearAt = 0
    A["rm"][:] = []
    Life.clearTick(JString(WC), st2, near, 200000)
    K.check(U[0] not in A["tried"] and str(st2.boss) == U[0], "BOSS the foreign one is never removed by the sweep")
    # our saved boss after a restart: renamed once
    st3 = IS(JString(WC))
    st3.boss = JString(U[4])
    st3.bossMine = True
    A["named"][:] = []
    Life.bossTick(JString(WC), st3, near, 300000)
    Life.bossTick(JString(WC), st3, near, 301000)
    K.eq(A["named"], [U[4]], "BOSS our Shardkeeper (saved boss.id) gets its name once after a restart")
    st3.clearAt = 0
    Life.clearTick(JString(WC), st3, near, 400000)
    K.check(U[4] in A["rm"] and st3.boss is None, "BOSS ... and is cleared once the quest is done")
    Life.API = None
    K.save()


# ================================================================================================ CLEAR (0.5.20 behaviour kept)
def run_clear(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    E = Env(scratch, jar, "clear")
    Cfg, Life = E.Cfg, E.Life
    E.files({KO: {"v": "5", "world": WC, "isles": "3", "camp.done": "1"}})
    camp, boss = [float(v) for v in Life.CAMP], [float(v) for v in Life.BOSS]
    A = fresh_A()
    Life.API = stand_in(PKG + "IsleApi", Api(A))
    A["alive"].update(["c1", "c2", "c3", "b0", "b1"])
    A["loaded"].update(["c1", "c2", "c3", "b0", "b1"])
    A["near"][(camp[0], camp[2])] = [("c3", "Skeleton_Fighter"), ("cow", "Cow")]
    A["near"][(boss[0], boss[2])] = [("b1", "Golem_Crystal_Earth")]
    mem = member(camp[0], camp[2])
    Cfg.CAMP_CLEAR, Cfg.CAMP_STOP, Cfg.BOSS_STOP, Cfg.CAMP_ON, Cfg.BOSS_ON = True, True, True, True, True
    st = Life.state(JString(WC))
    st.camp.add(JString("c1"))
    st.camp.add(JString("c2"))
    n = int(Life.clearTick(JString(WC), st, mem, 100000))
    K.check(n == 2 and sorted(A["rm"]) == ["c1", "c2"] and st.camp.size() == 0, "CLEAR camp done -> only the TRACKED skeletons removed: %s" % A["rm"])
    A["rm"][:] = []
    K.check(int(Life.clearTick(JString(WC), st, mem, 105000)) == 0 and not A["rm"], "CLEAR at most every 10 s")
    E.files({KO: {"v": "5", "world": WC, "isles": "3", "camp.done": "1", "boss.done": "1"}})
    st.clearAt = 0
    st.bossDone = False
    st.boss = JString("b0")
    st.bossMine = True
    Life.clearTick(JString(WC), st, mem, 200000)
    K.check("b0" not in A["rm"], "CLEAR boss.done but the portal broken and nobody holds a Hub Shard -> the Shardkeeper stays (needed)")
    E.files({KO: {"v": "5", "world": WC, "isles": "3", "camp.done": "1", "boss.done": "1", "portal": "1"}})
    st.clearAt = 0
    Life.clearTick(JString(WC), st, mem, 300000)
    K.check(A["rm"] == ["b0"] and st.boss is None and "b1" not in A["tried"], "CLEAR boss done + portal repaired -> our Shardkeeper removed, b1 kept")
    st.camp.add(JString("c9"))
    Cfg.CAMP_CLEAR = False
    st.clearAt = 0
    A["rm"][:] = []
    K.check(int(Life.clearTick(JString(WC), st, mem, 400000)) == 0 and not A["rm"], "CLEAR the setting off -> nothing")
    Cfg.CAMP_CLEAR = True
    Life.API = None
    K.save()


# ================================================================================================ TIME (bug 9)
def run_time(out, jar, scratch, _home):
    from jpype import JString, JLong, JInt
    K = HK.Child(out)
    E = Env(scratch, jar, "time")
    Cfg, Life = E.Cfg, E.Life
    WI, WS, HUB = "skyy-island-time22", "skyy-shard-00000000-0000-4000-8000-000000000022", "skywynn_zones"
    E.files({KO: {"v": "5", "world": WI, "isles": "3", "time.held": "1"}})
    HOUR, DAY, MIN = 3600000, 86400000, 60000
    T = {HUB: 100 * DAY + 20 * HOUR}
    F = {}
    A = {"set": [], "pause": [], "exec": []}

    class TApi(object):
        def now(self):
            return JLong(1000)

        def hubWorld(self):
            return JString(HUB)

        def gameTime(self, wn):
            return JLong(T.get(str(wn), -2 ** 63))

        def timeFlags(self, wn):
            return JInt(F.get(str(wn), 0))

        def setGameTime(self, wn, ms):
            A["set"].append((str(wn), int(ms)))
            T[str(wn)] = int(ms)
            return True

        def setTimePaused(self, wn, p):
            A["pause"].append((str(wn), bool(p)))
            F[str(wn)] = (F.get(str(wn), 0) & ~1) | (1 if p else 0)
            return True

        def exec(self, wn, r):
            A["exec"].append((str(wn), int(r.mode), int(r.ms), None if r.a is None else str(r.a)))
            return True

        def save(self, t):
            return True
    Life.API = stand_in(PKG + "IsleApi", TApi())
    Cfg.SYNC_TIME = True
    clr = lambda: [A[k].__delitem__(slice(None)) for k in A]
    sync = lambda wn: int(Life.syncTime(JString(wn), JLong(T[HUB]), JInt(F.get(HUB, 0))))
    tick = lambda m=4: [T.__setitem__(k, T[k] + m * MIN) for k in list(T)]
    # 1. an island AHEAD (0.5.21 held it paused): forward to the hub's next same time of day + un-paused, no hold
    T[WI] = T[HUB] + 3 * HOUR
    F[WI] = 1
    Life.HELD.put(JString(WI), True)
    r = sync(WI)
    K.check(A["set"] == [(WI, T[HUB] + DAY)] and (WI, False) in A["pause"] and r == 3,
            "TIME ahead 3 h -> forward 21 h to the hub's same time of day (never back) and un-paused (0.5.21 held it): %s %s r=%d" % (A["set"], A["pause"], r))
    K.check(not Life.HELD.containsKey(JString(WI)), "TIME ... no longer held")
    # 2. our own write is never taken for a change
    clr(); tick()
    K.check(sync(WI) == 0 and not A["set"] and not A["exec"], "TIME the next sync after our own jump: nothing (no loop)")
    # 3. /time set forward 6 h on the island -> handed to the hub, not undone
    clr(); tick(); T[WI] += 6 * HOUR
    iw = T[WI]
    r = sync(WI)
    K.check(r == 4 and A["exec"] == [(HUB, 16, 6 * HOUR, WI)] and not A["set"] and T[WI] == iw,
            "TIME /time set +6 h on the island -> IsleTask 16 to the HUB (+6 h), the island is NOT undone: r=%d %s" % (r, A["exec"]))
    h0 = T[HUB]
    K.check(int(Life.hubShift(JString(HUB), JLong(6 * HOUR), JString(WI))) == 1 and T[HUB] == h0 + 6 * HOUR, "TIME hubShift: the hub + 6 h")
    clr(); tick()
    K.check(sync(WI) == 0 and not A["set"] and not A["exec"] and (T[WI] - T[HUB]) % DAY == 0, "TIME ... then the island = the hub's time of day, nothing more")
    # 4. /time set BACK 6 h on the island -> the hub goes FORWARD 18 h (the next same time of day)
    clr(); tick(); T[WI] -= 6 * HOUR
    r = sync(WI)
    K.check(r == 4 and A["exec"] == [(HUB, 16, 18 * HOUR, WI)], "TIME a time set back 6 h -> the hub forward 18 h: %s" % A["exec"])
    Life.hubShift(JString(HUB), JLong(18 * HOUR), JString(WI))
    clr(); tick(); sync(WI)
    K.check(not A["exec"] and (T[WI] - T[HUB]) % DAY == 0 and T[WI] >= T[HUB], "TIME ... and every clock agrees afterwards (never back)")
    # 5. a change in the HUB (an admin there) is never copied - the island follows
    clr(); tick(); T[HUB] += 5 * HOUR
    r = sync(WI)
    K.check(not A["exec"] and r == 1 and A["set"] == [(WI, T[HUB])], "TIME a hub change -> no hand-over, the island follows: %s %s" % (A["exec"], A["set"]))
    # 6. a bed skip on the island: left alone while running, then the skip reaches the hub
    clr(); tick(); F[WI] = 2; T[WI] += 3 * HOUR
    K.check(sync(WI) == 0 and not A["set"] and not A["exec"], "TIME a bed skip in progress: left alone")
    tick(); F[WI] = 0; T[WI] += 7 * HOUR
    r = sync(WI)
    K.check(r == 4 and len(A["exec"]) == 1 and A["exec"][0][1] == 16 and A["exec"][0][2] == 10 * HOUR, "TIME the finished bed skip (+10 h) -> the hub: %s" % A["exec"])
    Life.hubShift(JString(HUB), JLong(10 * HOUR), JString(WI))
    F[HUB] = 2
    K.check(int(Life.hubShift(JString(HUB), JLong(HOUR), JString(WI))) == 0, "TIME hubShift during the hub's own bed skip: nothing")
    F[HUB] = 0
    # 7. the arrival jump: an ahead world forward to the hub's same time of day; its record forgotten (never a hand-over after)
    clr(); tick(); T[WI] = T[HUB] + 3 * HOUR
    K.check(int(Life.joinSync(JString(WI), JLong(T[HUB]))) == 1 and T[WI] == T[HUB] + DAY - 0 * HOUR - 0 and not Life.TIME_REC.containsKey(JString(WI)),
            "TIME joinSync: ahead 3 h -> forward 21 h, record forgotten")
    clr(); tick()
    K.check(sync(WI) == 0 and not A["exec"], "TIME ... the next sync: no hand-over")
    T[WI] = T[HUB] - 2 * HOUR
    K.check(int(Life.joinSync(JString(WI), JLong(T[HUB]))) == 1 and T[WI] == T[HUB], "TIME joinSync: behind -> the hub's time (0.5.20)")
    # 8. a shard world ahead: forward too, never paused
    clr(); T[WS] = T[HUB] + 2 * HOUR
    sync(WS)
    K.check(A["set"] == [(WS, T[HUB] + DAY)] and not A["pause"], "TIME a shard world ahead -> forward to the same time of day, no pause")
    # 10. review guard: the hub frozen (its clock does not move) + the island ticking -> no forward day jump every sync, held instead
    clr(); F[WI] = 0; T[WI] = T[HUB] + 2 * HOUR
    sync(WI)                                   # first sync (no record yet): one forward jump
    n0 = len(A["set"])
    for _ in range(4):
        T[WI] += 4 * MIN                       # the island ticks, the hub does not
        if F.get(WI, 0) & 1:
            T[WI] -= 4 * MIN                   # a paused island does not tick
        sync(WI)
    K.check(len(A["set"]) == n0 == 1 and F.get(WI, 0) & 1 and not A["exec"],
            "TIME hub frozen + island ticking -> no repeated forward jumps (one at the start), the island held (paused), no hand-over: %s %s" % (A["set"], A["pause"]))
    clr(); tick(); tick()                      # the hub moves again
    sync(WI)
    K.check(not (F.get(WI, 0) & 1) and len(A["set"]) <= 1 and (T[WI] - T[HUB]) % DAY == 0 and T[WI] >= T[HUB],
            "TIME ... the hub moves again -> un-paused, matched to the hub's time of day: %s" % A["set"])
    # 11. review: a hand-over the hub refuses (its bed skip) puts the record back -> handed over again after the skip
    clr(); tick(); T[WI] += 5 * HOUR
    K.check(sync(WI) == 4, "TIME refuse: /time set +5 h on the island -> hand-over")
    F[HUB] = 2
    K.check(int(Life.hubShift(JString(HUB), JLong(5 * HOUR), JString(WI))) == 0, "TIME refuse: the hub in a bed skip refuses")
    F[HUB] = 0
    clr(); tick()
    r = sync(WI)
    K.check(r == 4 and A["exec"] == [(HUB, 16, 5 * HOUR, WI)], "TIME refuse: ... the change is handed over again after the skip: r=%d %s" % (r, A["exec"]))
    Life.hubShift(JString(HUB), JLong(5 * HOUR), JString(WI))
    # 9. setting off: the record goes, a held world is released
    Cfg.SYNC_TIME = False
    sync(WI)
    K.check(not Life.TIME_REC.containsKey(JString(WI)), "TIME the setting off -> the record is forgotten")
    Cfg.SYNC_TIME = True
    gen = open(os.path.join(HERE, "build_skyyislands_%s.py" % VERSION), encoding="utf-8").read()
    K.check("if (this.mode == 16) { @PKG@.IsleLife.hubShift(this.wn, this.ms, this.a); return; }" in gen, "TIME IsleTask 16 runs hubShift")
    st = gen[gen.index("public static int syncTime(String wn, long h, int hf)"):]
    st = st[:st.index('}""")')]
    K.check("TIME_HOLD" not in st and "if (frozen) hold = isle;" in st, "TIME syncTime holds only while the hub's clock is frozen (no 12 h hold any more)")
    Life.API = None
    K.save()


# ================================================================================================ EARLY (0.5.23)
def run_early(out, jar, scratch, _home):
    from jpype import JClass, JString, JLong, JInt, JDouble
    K = HK.Child(out)
    E = Env(scratch, jar, "early")
    Cfg, Life, Task = E.Cfg, E.Life, E.P("IsleTask")
    UUID = JClass("java.util.UUID")
    WI, HUB, ZONE2, SHARD = "skyy-island-early23", "skywynn_zones", "skywynn_z2", "skyy-shard-00000000-0000-4000-8000-000000000023"
    E.files({KO: {"v": "5", "world": WI, "isles": "3"}})
    A = {"now": 100000, "bed": set(), "trip": 1, "trips": [], "rt": 1, "rts": [], "revive": [], "tp": [], "say": [], "home": [], "exec": True, "in": []}

    class EApi(object):
        def now(self):
            return JLong(A["now"])

        def hubWorld(self):
            return JString(HUB)

        def hasBed(self, u, wn):
            return str(wn) in A["bed"]

        def name(self, u):
            return JString("Tester")

        def earlyTrip(self, dw, u, home):
            A["trips"].append((str(dw), str(home)))
            return JInt(A["trip"])

        def respawnTo(self, fw, u, tw, x, y, z):
            A["rts"].append((str(fw), str(tw), float(x), float(y), float(z)))
            return JInt(A["rt"])

        def revive(self, wn, u):
            A["revive"].append(str(wn))
            return True

        def teleport(self, fw, u, tw, x, y, z):
            A["tp"].append(str(tw))
            return JInt(1)

        def say(self, u, text, color):
            A["say"].append(str(text))

        def exec(self, wn, r):
            return A["exec"]

        def players(self, wn):
            rows = [JClass("java.lang.Object")[:]([UUID.fromString(x)]) for x in A["in"]]
            return JClass("java.lang.Object")[:](rows)

        def goHome(self, wn, u, hk, home):
            A["home"].append(str(wn))
            return JInt(1)
    Life.API = stand_in(PKG + "IsleApi", EApi())
    Cfg.RESPAWN_HOME = True
    Cfg.DEATH_KEEP = JString("skyy-shard-")
    ko = UUID.fromString(KO)
    early = lambda dw, u=ko: int(Life.early(JString(dw), u))
    clr = lambda: [A[k].__delitem__(slice(None)) for k in ("trips", "rts", "revive", "tp", "say", "home")]
    # 1. a death in the zone, no bed there, the island loaded -> cancel + ONE trip to the island
    K.check(early(HUB) == 1 and A["trips"] == [(HUB, WI)] and Life.EARLY.containsKey(ko),
            "EARLY a zone death (no bed there) -> the vanilla respawn cancelled, one trip to the island: %s" % A["trips"])
    # 2. a second click while it is on its way: cancelled, no second trip
    clr()
    K.check(early(HUB) == 1 and not A["trips"], "EARLY a second click while the respawn is on its way: cancelled, no second trip")
    K.check(A["say"] == ["[Island] Taking you to your island..."], "EARLY review 2: the swallowed click gets a chat line: %s" % A["say"])
    # 3. landDead (IsleTask 17): done -> counted, EARLY cleared, no fallback
    t = Task(JInt(17), JString(HUB), ko)
    t.ks = JClass("java.lang.String")[:]([JString(WI)])
    t.dead = True
    t.x, t.y, t.z = JDouble(8.5), JDouble(130.0), JDouble(8.5)
    n0 = int(Life.EARLYN.get())
    K.check(int(Life.landDead(t)) == 1 and A["rts"] == [(HUB, WI, 8.5, 130.0, 8.5)] and not A["revive"] and not Life.EARLY.containsKey(ko)
            and int(Life.EARLYN.get()) == n0 + 1, "EARLY landDead: respawned onto the island (counted, EARLY cleared, no fallback)")
    # 4. failed while still dead -> the vanilla respawn (revive) once, BYPASS lets exactly that call through
    clr(); early(HUB); A["rt"] = -1
    K.check(int(Life.landDead(t)) == -1 and A["revive"] == [HUB] and Life.BYPASS.containsKey(ko) and not Life.EARLY.containsKey(ko),
            "EARLY landDead failed while dead -> the vanilla respawn is run (revive) with the one-shot pass")
    K.check(len(A["say"]) == 1 and "Could not respawn you on your island" in A["say"][0], "EARLY review 2: the failed respawn gets a chat line: %s" % A["say"])
    clr()
    K.check(early(HUB) == 0 and not A["trips"] and not Life.BYPASS.containsKey(ko), "EARLY ... the fallback's own RespawnEvent passes (vanilla), the pass is used up")
    K.check(early(HUB) == 1 and len(A["trips"]) == 1, "EARLY ... the next death goes the one-load way again")
    Life.EARLY.clear()
    # 5. not dead / not in that world any more -> nothing
    clr(); A["rt"] = 0
    K.check(int(Life.landDead(t)) == 0 and not A["revive"], "EARLY landDead: no longer dead -> nothing (no fallback)")
    A["rt"] = 1
    # 6. bedLand with the dead flag = the respawn; without it = the 0.5.20 teleport
    clr()
    b = Task(JInt(14), JString(HUB), ko)
    b.ks = t.ks
    b.dead = True
    Life.bedLand(b)
    b2 = Task(JInt(14), JString(HUB), ko)
    b2.ks = t.ks
    Life.bedLand(b2)
    K.check(len(A["rts"]) == 1 and A["tp"] == [WI], "EARLY bedLand: dead -> respawnTo; alive -> the plain teleport (0.5.20): %s %s" % (A["rts"], A["tp"]))
    # 7. review 1: ONE attempt per death - the first attempt silently lost (its task never ran): a click 3 s+ later = vanilla, no second trip
    Life.EARLY.clear(); clr()
    K.check(early(HUB) == 1 and len(A["trips"]) == 1, "EARLY review 1: the attempt starts")
    A["now"] += 2500
    K.check(early(HUB) == 1 and len(A["trips"]) == 1, "EARLY review 1: a click 2.5 s later: still swallowed")
    A["now"] += 1000
    clr()
    K.check(early(HUB) == 0 and not A["trips"] and not Life.EARLY.containsKey(ko) and any("Could not respawn" in x for x in A["say"]),
            "EARLY review 1: a click 3.5 s after a lost attempt -> the VANILLA respawn (no second trip, attempt forgotten, chat line): %s" % A["say"])
    Life.EARLY.clear(); clr()
    Life.EARLY.put(ko, JClass("java.lang.Long")(A["now"] - 20000))
    K.check(early(HUB) == 0 and not A["trips"], "EARLY review 1: an attempt 20 s old (still dead) -> vanilla, never a second attempt")
    clr(); Life.EARLY.put(ko, JClass("java.lang.Long")(A["now"] - 70000))
    K.check(early(HUB) == 1 and len(A["trips"]) == 1, "EARLY review 1: an attempt 70 s old = an earlier death -> forgotten, a new trip")
    Life.EARLY.clear()
    # 7b. review 1: a dead bed trip whose landing task cannot reach the player's world -> the attempt forgotten (next click = vanilla path)
    clr(); Life.EARLY.put(ko, JClass("java.lang.Long")(A["now"])); A["exec"] = False
    bt = Task(JInt(13), JString(WI), ko)
    bt.a = JString(HUB)
    bt.dead = True
    K.check(int(Life.bedTrip(bt)) == -1 and not Life.EARLY.containsKey(ko) and not A["say"],
            "EARLY review 1: a dead bed trip that cannot reach the player's world forgets the attempt: %s" % A["say"])
    A["exec"] = True
    # 7c. review 3: the 1.8 s safety net after OUR respawn waits 6 s (no second trip while the move is on its way), then routes as before
    clr(); A["in"] = [KO]
    Life.DONE.put(ko, JClass("java.lang.Long")(A["now"]))
    A["now"] += 1800
    K.check(int(Life.respawn(JString(HUB), ko, JString(HUB))) == -1 and not A["home"],
            "EARLY review 3: 1.8 s after our respawn, still in the death world -> 'not ready, try again', no second trip")
    K.check(int(Life.respawn(JString(WI), ko, JString(HUB))) == 4 and not A["home"], "EARLY review 3: ... on the island = already home")
    A["now"] += 5000
    K.check(int(Life.respawn(JString(HUB), ko, JString(HUB))) == 1 and A["home"] == [HUB],
            "EARLY review 3: still in the death world 6.8 s after it -> the net takes them home as before: %s" % A["home"])
    Life.DONE.clear(); A["in"] = []
    # 8. every 0.5.22 rule untouched -> 0 (vanilla + the 1.8 s routing), no trip
    clr()
    K.check(early(WI) == 0, "EARLY a death on their own island -> vanilla (the engine puts them at their bed / spawn)")
    A["bed"].add(ZONE2)
    K.check(early(ZONE2) == 0, "EARLY a bed set where they died -> vanilla (bed respawn)")
    A["bed"].clear()
    K.check(early(SHARD) == 0, "EARLY islands.deathKeep (shard) -> vanilla")
    K.check(early(HUB, UUID.fromString(U[9])) == 0, "EARLY no island (the hub route 2) -> vanilla + the old trip")
    K.check(not A["trips"], "EARLY ... none of these started a trip")
    A["trip"] = 0
    K.check(early(ZONE2) == 0 and A["trips"] == [(ZONE2, WI)] and not Life.EARLY.containsKey(ko),
            "EARLY the island not loaded / no spawn point (earlyTrip 0) -> vanilla, nothing remembered")
    A["trip"] = 1
    Cfg.RESPAWN_HOME = False
    clr()
    K.check(early(HUB) == 0 and not A["trips"], "EARLY islands.respawnHome off -> vanilla")
    Cfg.RESPAWN_HOME = True
    Life.EARLY.clear()
    gen = open(os.path.join(HERE, "build_skyyislands_%s.py" % VERSION), encoding="utf-8").read()
    h = gen[gen.index('C(irev, "public IsleRespawnEvt()'):]
    h = h[:h.index('F(pl, "public java.util.concurrent.ScheduledFuture isleTicker;")')]
    K.check("e.isCancelled()" in h and "lv.getRemaining() <= 0" in h and "e.setCancelled(true)" in h,
            "EARLY the hook skips an already cancelled event and permadeath (PlayerLives 0), cancels only on early() == 1")
    K.check("registerSystem(new @PKG@.IsleRespawnEvt())" in gen and '"/4, "' in gen, "EARLY the hook is registered (hooks n/4)")
    rt = gen[gen.index("public int respawnTo(String fromWorld"):]
    rt = rt[:rt.index('}""")')]
    K.check(rt.index("@TP@.createForPlayer(to") < rt.index("st.tryRemoveComponent(r, @DTH@.getComponentType())"),
            "EARLY respawnTo: the Teleport first, then the DeathComponent removed (vanilla ExitInstance order)")
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
    K.check(bool(Cfg.CAMP_CLEAR), "LIVE camp.clearWhenDone on in the live config")
    St.DIR = Paths.get(os.path.join(home, "islands"))
    St.IO = None
    St.STOPPING = False
    St.loadIslandWorlds()
    d = os.path.join(home, "islands")
    owners = [f[:-11] for f in sorted(os.listdir(d)) if f.endswith(".properties")]
    for k in owners:
        s = St.settings(k)
        K.check(s is not None and not bool(s.bad), "LIVE island file %s reads" % k[:12])
        K.check(s.raw is None or (s.raw.getProperty("camp.ids") is None and s.raw.getProperty("boss.id") is None),
                "LIVE %s: no camp.ids / boss.id yet" % k[:12])
    K.notes.append("live: %d island files" % len(owners))
    K.check(HK.tree_hash(home) == h0, "LIVE no file of the copy changed (load writes nothing)")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("early", run_early), ("ids", run_ids), ("boss", run_boss), ("clear", run_clear), ("time", run_time), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyIslands"))
