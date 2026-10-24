"""Harness for SkyyIslands 0.5.25 (the starter archipelago, round R2; tools/islands_0_5_25_patch.py).
Build first: python tools/islands_0_5_25_patch.py && python SkyyIslands/build_skyyislands_0.5.25.py

    python SkyyIslands/test_skyyislands_0.5.25.py [--jar <jar>] [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; stand-in IsleApi = a Python JProxy over a BLOCK MAP, real IslandStore files in scratch,
-Xverify:all):
  S     static   the patch re-runs to identical bytes; no new system / command / listener; the layout (5 islands, 9 bridges, the Combat door,
                 the ring + spokes, no bridge to Combat, every cell outside the starter islands, sections 3-4) is what the jar carries
  A / C / AA  verify, compare 0.5.24 -> 0.5.25 (exactly the planned members + ArchiIsles), audit
  ARCHI  IsleLife.archiOnce on a block map holding the 3 starter islands: element by element (<= one slice a tick) until archi = 1; every
         archipelago block placed, nothing of the starter islands changed but the Combat door's pad; the farm channel's water; the 4 chests
         filled from the config rows; the 6 shard doors sent to shard:fn:door at their cells; the pen's 7 tamed + 4 wild animals; START
         TWICE (a second pass + a fresh IsleState) changes nothing; a not-loaded cell = it waits, then carries on
  BUILT  an existing island with a player's block on the Foraging island's spot: Foraging + its 3 bridges skipped, the block untouched,
         everything else built; the Foraging shard comes as the ITEM once (owner on the island) via shard:fn:give; the Combat pad changed by
         a player = the Combat door skipped; no SkyyShards = the doors wait and are recorded later (30 s)
  LIFE   the copper cave regrows (AIR / stone -> ore; a chest in an ore cell stays); a caught wild animal comes back after
         ranch.respawnSeconds (tamed ones never); an island reset (new world) starts the archipelago again; archi.existing off / new
  CFG    config: the new rows + defaults, starter.design archipelago | three | classic, the one-time update plan (an untouched three is
         planned, classic / an admin's three kept), island:fn:place answers farm / forage / minecave / orchard / ranch only for archipelago
  REG    the 0.5.24 harness phases (unload, early, ids, boss, clear, time) on the 0.5.25 jar
  LIVE   a scratch COPY of the live Skyy_SkyyIslands: every island file reads, the update plan for its config, nothing changed on disk
Not testable without the game (UNVERIFIED): the real chunk loading of cx -2 (the Mining island), water flow in the farm channel, the tamed
animals staying in the pen, the client look of the bridges.
Exit code 1 on any failure.
"""
import os, sys, json, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_spec = importlib.util.spec_from_file_location("isl524", os.path.join(HERE, "test_skyyislands_0.5.24.py"))
T24 = importlib.util.module_from_spec(_spec)
_argv = list(sys.argv)
_spec.loader.exec_module(T24)
sys.argv[:] = _argv
T23 = T24.T23

VERSION = "0.5.25"
OLD = "0.5.24"
PKG = "com.skyy.islands."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "archi1", "ih")))
GEN = os.path.join(HERE, "build_skyyislands_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyislands_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "islands_0_5_25_patch.py")
LIVE_DIR = T24.LIVE_DIR
ADDED = ["ArchiIsles"]
EXPECT = {   # checked by hand 2026-10-23: the version texts (CfgFile / CfgFn / CfgRows), the settings + the one-time update (IslandCfg, IslandHooks,
            # setup), the archipelago (IsleApi / IsleEng / IsleLife / IsleState), the places (StarterIsles), the relight range (RelightNow), the place guard
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "GuardPlace": ["+m shardBlock"],
    "IslandCfg": ["+f ARCHI_EXISTING", "+f ARCHI_ITEMS", "+f CAVE_REGROW", "+f CHEST_FARM", "+f CHEST_FORAGE", "+f CHEST_ORCHARD", "+f CHEST_RANCH", "+f MIG25_BY",
                  "+f MIG25_KEYS", "+f MIG25_NEW", "+f MIG25_NOTE", "+f MIG25_OLD", "+f MIG25_STEP", "+f MIG25_WHY", "+f RANCH_RESPAWN", "+f RANCH_TAMED",
                  "+f RANCH_WILD", "+m markDone25", "+m plan0525", "~<clinit>", "~m load"],
    "IslandHooks": ["+m apply0525"], "IsleApi": ["+m chestFill", "+m shardDoor", "+m shardGive"], "IsleEng": ["+m chestFill", "+m shardDoor", "+m shardGive"],
    "IsleLife": ["+f ANIMALS", "+f ARCHI_BLOCKS", "+f ARCHI_DONE", "+f ARCHI_SKIP", "+f ARCHI_SLICE", "+f DOOR_RETRY", "+f ITEM_TEST", "+f REGROWN", "+m archiBad", "+m archiDoor", "+m archiGet", "+m archiItems",
                 "+m archiOnce", "+m archiSet", "+m archiSet1", "+m archiTick", "+m caveRegrow", "+m chestSpec", "+m expand", "+m itemKnown", "+m ranchSpawn", "~<clinit>", "~m tickWorld"],
    "IsleState": ["+f archiCur", "+f archiEl", "+f archiFor", "+f archiOff", "+f archiPh", "+f archiRuns", "+f caveAt", "+f doorsAt", "+f ranchAt", "~c "],
    "RelightNow": ["~m run"], "SkyyIslandsPlugin": ["~m setup"], "StarterIsles": ["~m placeOf", "~m publish"],
}
KO = "00000000-0000-4000-8000-0000000b0525"
WC = "skyy-island-archi25"


def layout():
    """the generated script's layout (S3_ONLY: no JVM, no build) - the 3 starter islands + the archipelago elements"""
    os.environ["S3_ONLY"] = "1"
    spec = importlib.util.spec_from_file_location("gen525", GEN)
    m = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)
    except ImportError:
        pass
    del os.environ["S3_ONLY"]
    return m


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    for w in ("registerSystem(", "registerCommand(", "registerGlobal("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    m = layout()
    els = m.ARCHI
    names = [e["name"] for e in els]
    K.eq(names[:5], ["farm", "forage", "minecave", "ranch", "orchard"], "S the 5 islands come first")
    br = sorted(n for n in names if n.startswith("b_"))
    K.eq(br, sorted(["b_spawn_farm", "b_spawn_forage", "b_spawn_minecave", "b_spawn_ranch", "b_spawn_orchard", "b_farm_forage", "b_forage_minecave",
                     "b_minecave_ranch", "b_ranch_orchard"]), "S the ring (Farming - Foraging - Mining - Ranching - Orchard) + 5 spokes; no bridge to Combat")
    K.check(names[-1] == "combat" and els[-1]["door"] == (46, 128, 9), "S the Combat door north of the camp (46, 128, 9)")
    ctr = dict((e["name"], e["centre"]) for e in els if e["kind"] == "island")
    import math
    dist = sorted(round(math.hypot(c[0] - 8, c[1] - 8)) for c in ctr.values())
    K.check(dist == sorted(dist) and len(set(dist)) == 5 and 40 <= dist[0] and dist[-1] <= 55, "S uneven distances from the spawn: %s" % dist)
    ang = dict((n, math.degrees(math.atan2(c[1] - 8, c[0] - 8)) % 360) for n, c in ctr.items())
    K.check(ang["minecave"] < ang["forage"] < ang["farm"] or (ang["farm"] < 90 and ang["forage"] > ang["minecave"]), "S Foraging sits between Mining and Farming: %s" % ang)
    S3 = m.S3_L
    allc = {}
    for e in els:
        for c, b in e["cells"].items():
            K.check(c not in allc, "S cell %s in one element only" % (c,)) if c in allc else None
            allc[c] = b
    over = [c for c in allc if c in S3 and c not in els[-1]["cells"]]
    K.check(not over, "S no archipelago cell covers a starter island block (only the Combat pad): %s" % over[:3])
    K.check(all(96 <= c[1] <= 159 for c in allc), "S sections 3 + 4 only")
    doors = dict((e["key"], e["door"]) for e in els if e["door"])
    K.eq(sorted(doors), ["combat", "farming", "foraging", "mining", "orchard", "ranching"], "S six shard doors")
    K.check(all(allc[d] == "Skyy_Shard_" + k.capitalize() for k, d in doors.items()), "S each door cell holds Skyy_Shard_<Kind>")
    K.check(all(allc.get((d[0], d[1] - 1, d[2])) == "Rock_Stone_Brick" for k, d in doors.items()), "S each door stands on the brick pad")
    mine = els[2]
    K.check(len(mine["ores"]) == 46 and all(allc[o] == "Ore_Copper_Stone" for o in mine["ores"]) and doors["mining"][1] == 124, "S the cave: 46 copper ores, the door on the chamber floor")
    K.check(len(els[0]["water"]) == 9 and all(w not in allc for w in els[0]["water"]), "S the farm channel: 9 water cells (no block there)")
    K.check(len([a for a in els[3]["animals"] if a[0] == "in"]) == 7 and len([a for a in els[3]["animals"] if a[0] == "out"]) == 4, "S the pen: 7 spots inside, 4 outside")
    K.check(sum(1 for b in allc.values() if b == "Plant_Crop_Wheat_Block") >= 20 and sum(1 for b in allc.values() if b == "Soil_Dirt_Tilled") >= 60, "S the farm plot: wheat rows + tilled soil")
    K.check(sum(1 for b in allc.values() if b in ("Wood_Oak_Trunk", "Wood_Birch_Trunk")) > 60, "S the Foraging island is covered in trees")
    K.check('"archipelago".equals(@PKG@.IslandCfg.STARTER_DESIGN)' in g and "public String shardBlock(@EV@ ev)" in g and "getItemInHand" in g,
            "S ArchiIsles.on + the place guard's item")
    K.save()


class Api(object):
    """the stand-in engine over a block map: B[(x, y, z)] = id; W = water cells; unloaded = cells that answer null"""

    def __init__(self, A):
        self.A = A

    def now(self):
        from jpype import JLong
        return JLong(1)

    def block(self, wn, x, y, z):
        from jpype import JString
        c = (int(x), int(y), int(z))
        if c in self.A["unloaded"] or (self.A["ranch_unloaded"] and c == self.A.get("ranch_ground")):
            return None
        return JString(self.A["B"].get(c, ""))

    def setBlock(self, wn, x, y, z, id_):
        c = (int(x), int(y), int(z))
        i = str(id_)
        if i.startswith("Skyy_Shard_") and not self.A["shards"]:
            return False
        if i:
            self.A["B"][c] = i
        else:
            self.A["B"].pop(c, None)
        self.A["sets"] += 1
        return True

    def fluid(self, wn, x, y, z):
        from jpype import JInt
        return JInt(1 if (int(x), int(y), int(z)) in self.A["W"] else 0)

    def setWater(self, wn, x, y, z):
        self.A["W"].add((int(x), int(y), int(z)))
        return True

    def chestFill(self, wn, x, y, z, spec):
        from jpype import JInt
        self.A["chests"].append(((int(x), int(y), int(z)), str(spec)))
        return JInt(len(str(spec).split(",")))

    def shardDoor(self, owner, pkey, kind, wn, x, y, z):
        from jpype import JString
        if not self.A["shards"]:
            return None
        if self.A["refuse"].get(str(kind), 0) > 0:          # fix (critic): a passing refusal ("-The shard file could not be saved.")
            self.A["refuse"][str(kind)] -= 1
            self.A["refused"].append(str(kind))
            return JString("-The shard file could not be saved.")
        self.A["doors"].append((str(kind), (int(x), int(y), int(z)), str(pkey)))
        return JString("+")

    def shardGive(self, u, kind):
        from jpype import JString
        self.A["given"].append(str(kind))
        return JString("+")

    def roleOk(self, role):
        return True

    def spawn(self, wn, role, x, y, z, yaw):
        from jpype import JString
        self.A["n"] += 1
        u = "00000000-0000-4000-8000-%012d" % self.A["n"]
        self.A["alive"].add(u)
        self.A["roles"][u] = str(role)
        self.A["spawned"].append((str(role), float(x), float(z)))
        return JString(u)

    def npcs(self, wn, x, y, z, rad):
        """every live animal we spawned + the untracked ones saved in the chunk (A['extra']), when the ranch is loaded"""
        from jpype import JClass, JString
        out = JClass("java.util.ArrayList")()
        if self.A["ranch_unloaded"]:
            return out
        for u in sorted(self.A["alive"]):
            out.add(JClass("java.lang.Object")[:]([JString(u), JString(self.A["roles"].get(u, ""))]))
        for u, r in self.A["extra"]:
            out.add(JClass("java.lang.Object")[:]([JString(u), JString(r)]))
        return out

    def alive(self, wn, uuid):
        return str(uuid) in self.A["alive"]

    def relight(self, wn):
        self.A["relit"] += 1

    def save(self, t):
        self.A["saved"].append((str(t.a), [str(k) for k in t.ks], [str(v) for v in t.vs]))
        return True


def fresh(m):
    B_ = dict(m.S3_L)
    return {"B": B_, "W": set(), "unloaded": set(), "chests": [], "doors": [], "given": [], "spawned": [], "alive": set(), "n": 0, "sets": 0,
            "relit": 0, "saved": [], "shards": True, "refuse": {}, "refused": [], "roles": {}, "extra": [], "ranch_unloaded": False}


def env(scratch, jar, sub, extra=None):
    from jpype import JProxy, JBoolean
    E = T23.Env(scratch, jar, sub)
    props = {"v": "5", "world": WC, "isles": "3"}
    props.update(extra or {})
    E.files({KO: props})
    # fix2: the item asset map stand-in (every id is an item but the made-up No_Such_* ones)
    E.Life.ITEM_TEST = JProxy("java.util.function.Function", dict={"apply": lambda x: JBoolean(not str(x).startswith("No_Such"))})
    return E


def rows_with_owner():
    from jpype import JClass
    return JClass("java.lang.Object")[:]([JClass("java.lang.Object")[:]([JClass("java.util.UUID").fromString(KO), JClass("java.lang.Double")(8.0),
                                                                         JClass("java.lang.Double")(130.0), JClass("java.lang.Double")(8.0)])])


def drive(Life, IS, st, A, rows, limit=4000):
    from jpype import JString, JLong
    n = 0
    while n < limit and not bool(st.archiOff):
        Life.archiOnce(JString(WC), JString(KO), st, JLong(1000 + n), rows)
        n += 1
    return n


def run_archi(out, jar, scratch, _home):
    from jpype import JClass, JString, JLong
    K = HK.Child(out)
    m = layout()
    E = env(scratch, jar, "archi")
    Life, IS, Arc, Cfg = E.Life, E.P("IsleState"), E.P("ArchiIsles"), E.Cfg
    K.check(bool(Arc.on()) and str(Cfg.STARTER_DESIGN) == "archipelago", "ARCHI the default design is archipelago")
    A = fresh(m)
    Life.API = T23.stand_in(PKG + "IsleApi", Api(A))
    st = IS(JString(WC))
    rows = rows_with_owner()
    # a cell of the Mining island not loaded: it waits there
    mc = sorted(m.ARCHI[2]["cells"])[0]
    A["unloaded"].add(mc)
    n0 = drive(Life, IS, st, A, rows, limit=300)
    K.check(not bool(st.archiOff) and int(st.archiEl) == 2, "ARCHI a not-loaded cell: it waits at the Mining island (element %d)" % int(st.archiEl))
    A["unloaded"].clear()
    n = drive(Life, IS, st, A, rows)
    get = lambda k: Life.archiGet(JString(KO), JString(k))
    K.check(bool(st.archiOff) and str(get("archi")) == "1" and all(str(get("archi." + e["name"])) == "done" for e in m.ARCHI),
            "ARCHI all 15 parts done, archi = 1 (%d ticks)" % (n0 + n))
    want = dict(m.S3_L)
    for e in m.ARCHI:
        want.update(e["cells"])
    diff = [c for c in set(want) | set(A["B"]) if want.get(c) != A["B"].get(c)]
    K.check(not diff, "ARCHI the block map = the starter islands + every archipelago block (the Combat pad replaced): %s" % diff[:4])
    K.check(A["W"] == set(m.ARCHI[0]["water"]), "ARCHI the farm channel's 9 water cells")
    chests = dict((c, s) for c, s in A["chests"])
    K.check(len(A["chests"]) == 4 and chests[(m.ARCHI[0]["chests"][0][:3])] == str(Cfg.CHEST_FARM) and chests[m.ARCHI[3]["chests"][0][:3]] == str(Cfg.CHEST_RANCH),
            "ARCHI 4 chests filled once from the archi.chest.* rows")
    doors = dict((k, c) for k, c, pk in A["doors"])
    K.check(len(A["doors"]) == 6 and all(doors[e["key"]] == e["door"] for e in m.ARCHI if e["door"]) and all(pk == KO for k, c, pk in A["doors"]),
            "ARCHI the 6 shard doors sent to shard:fn:door at their cells with the owner's profile key")
    roles = [r for r, x, z in A["spawned"]]
    K.eq(sorted(roles), sorted(["Tamed_Cow"] * 2 + ["Tamed_Sheep"] * 2 + ["Tamed_Chicken"] * 3 + ["Chicken"] * 2 + ["Sheep_Lamb", "Cow_Calf"]),
         "ARCHI the pen: 7 tamed + 4 wild animals")
    ids = str(get("ranch.ids"))
    ents = ids.split(";")
    K.check(sum(1 for x in ents if x.startswith("t|")) == 7 and sum(1 for x in ents if x.startswith("w|")) == 4, "ARCHI ranch.ids keeps them (7 t + 4 w): %s" % ids[:300])
    # start twice: a new IsleState (a restart) on the finished island = nothing at all
    s0, b0 = A["sets"], dict(A["B"])
    st2 = IS(JString(WC))
    drive(Life, IS, st2, A, rows, limit=50)
    K.check(A["sets"] == s0 and A["B"] == b0 and len(A["doors"]) == 6 and len(A["chests"]) == 4 and len(A["spawned"]) == 11, "ARCHI start twice: nothing changes, nothing is given twice")
    # fix (critic): the server stops after the chests went in but before the element was marked done -> the next start never fills them again
    rn = m.ARCHI[3]["name"]
    Life.archiSet1(JString(KO), JString("archi." + rn), JString(""))
    Life.archiSet1(JString(KO), JString("archi"), JString(""))
    st3 = IS(JString(WC))
    drive(Life, IS, st3, A, rows, limit=200)
    K.check(str(get("archi." + rn)) == "done" and len(A["chests"]) == 4 and len(A["spawned"]) == 11 and str(get("archi.chest.%d" % [c[3] for e in m.ARCHI for c in e["chests"]].index("ranch"))) == "1",
            "ARCHI fix: a ranch element run again after its chest was filled: the chest is not filled twice, no second herd (%d fills, %d animals)" % (len(A["chests"]), len(A["spawned"])))
    K.save()


def run_door(out, jar, scratch, _home):
    """fix (critic): a refused shard door ("-...") is not recorded; the 30 s pass asks again until SkyyShards says + / ="""
    from jpype import JClass, JString, JLong
    K = HK.Child(out)
    m = layout()
    E = env(scratch, jar, "door")
    Life, IS = E.Life, E.P("IsleState")
    A = fresh(m)
    A["refuse"] = {"farming": 2}
    Life.API = T23.stand_in(PKG + "IsleApi", Api(A))
    st = IS(JString(WC))
    rows = rows_with_owner()
    drive(Life, IS, st, A, rows)
    get = lambda k: Life.archiGet(JString(KO), JString(k))
    K.check(get("archi.door.farming") is None and A["refused"] == ["farming"] and str(get("archi.farm")) == "done" and int(Life.DOOR_RETRY.get()) >= 1,
            "DOOR fix: a refused Farming door is not recorded (archi.door.farming unset, the island built)")
    mem = JClass("java.util.ArrayList")()
    Life.archiTick(JString(WC), JString(KO), st, mem, rows, JLong(10 ** 9))
    K.check(get("archi.door.farming") is None and A["refused"] == ["farming", "farming"], "DOOR fix: refused again on the next pass - still asked")
    Life.archiTick(JString(WC), JString(KO), st, mem, rows, JLong(10 ** 9 + 31000))
    K.check(str(get("archi.door.farming")) == "+" and sum(1 for k, c, pk in A["doors"] if k == "farming") == 1, "DOOR fix: the third ask is recorded (+)")
    Life.archiTick(JString(WC), JString(KO), st, mem, rows, JLong(10 ** 9 + 62000))
    K.check(sum(1 for k, c, pk in A["doors"] if k == "farming") == 1 and not A["given"], "DOOR fix: ... then never asked again; no shard item given")
    K.save()


def run_fix2(out, jar, scratch, _home):
    """fix2 (critics): a bad island file = no archipelago work (no log flood, nothing stored); chest rows with an unknown item id skip that
    id; a door cell holding a player's block = the door is not recorded (asked again), recorded once the cell is empty"""
    from jpype import JClass, JString, JLong
    K = HK.Child(out)
    m = layout()
    E = env(scratch, jar, "fix2")
    Life, IS, Cfg, St = E.Life, E.P("IsleState"), E.Cfg, E.St
    A = fresh(m)
    Life.API = T23.stand_in(PKG + "IsleApi", Api(A))
    rows = rows_with_owner()
    get = lambda k: Life.archiGet(JString(KO), JString(k))
    s = St.settings(JString(KO))
    s.bad = True
    s.badAt = JLong(int(JClass("java.lang.System").currentTimeMillis()) + 10 ** 9)   # = a file that keeps failing its 5 s re-read
    st = IS(JString(WC))
    for i in range(50):
        Life.archiOnce(JString(WC), JString(KO), st, JLong(1000 + i), rows)
    mem = JClass("java.util.ArrayList")()
    Life.archiTick(JString(WC), JString(KO), st, mem, rows, JLong(10 ** 9))
    Life.archiItems(JString(WC), JString(KO), st, rows, JLong(10 ** 9))
    K.check(bool(Life.archiBad(JString(KO))) and not A["saved"] and A["sets"] == 0 and not A["given"] and not bool(st.archiOff),
            "FIX2 a bad island file: 50 ticks + a 30 s pass do nothing (no start, nothing saved / placed / given)")
    s.bad = False
    K.eq(str(Life.chestSpec(JString("farm"), JString("Plant_Seeds_Wheat:8, No_Such_Item:3 ,Tool_Watering_Can:1"))), "Plant_Seeds_Wheat:8,Tool_Watering_Can:1",
         "FIX2 chestSpec drops an unknown item id, keeps the rest")
    Cfg.CHEST_FARM = JString(str(Cfg.CHEST_FARM) + ",No_Such_Seed:4")
    drive(Life, IS, st, A, rows)
    chests = dict((c, sp) for c, sp in A["chests"])
    fs = chests.get(m.ARCHI[0]["chests"][0][:3], "")
    K.check(str(get("archi")) == "1" and "No_Such_Seed" not in fs and fs and len(A["chests"]) == 4, "FIX2 the farm chest is filled without the unknown id: %s" % fs)
    # the Farming door not recorded yet and a player's block where its portal goes: untouched, not recorded, asked again
    fd = tuple(m.ARCHI[0]["door"])
    Life.archiSet1(JString(KO), JString("archi.door.farming"), JString(""))
    A["B"][fd] = "Furniture_Village_Bench"
    nd = len(A["doors"])
    Life.archiTick(JString(WC), JString(KO), st, mem, rows, JLong(2 * 10 ** 9))
    K.check(A["B"][fd] == "Furniture_Village_Bench" and get("archi.door.farming") is None and len(A["doors"]) == nd and str(get("archi.door.mining")) == "+",
            "FIX2 a block on the Farming door's cell: untouched, that door is not recorded")
    del A["B"][fd]
    Life.archiTick(JString(WC), JString(KO), st, mem, rows, JLong(3 * 10 ** 9))
    K.check(A["B"].get(fd) == "Skyy_Shard_Farming" and str(get("archi.door.farming")) == "+", "FIX2 the cell emptied: the next pass places the portal block and records the door")
    K.save()


def run_built(out, jar, scratch, _home):
    from jpype import JClass, JString, JLong
    K = HK.Child(out)
    m = layout()
    E = env(scratch, jar, "built")
    Life, IS = E.Life, E.P("IsleState")
    A = fresh(m)
    A["shards"] = False                                                   # no SkyyShards: the doors wait (their pads are built)
    fc = sorted(m.ARCHI[1]["cells"])[100]                                 # a player's block on the Foraging island's spot
    A["B"][fc] = "Furniture_Village_Bench"
    pad = sorted(m.ARCHI[-1]["expect"])[0]                                 # ... and on the Combat pad's ground
    A["B"][pad] = "Wood_Softwood_Planks"
    Life.API = T23.stand_in(PKG + "IsleApi", Api(A))
    st = IS(JString(WC))
    rows = rows_with_owner()
    drive(Life, IS, st, A, rows)
    get = lambda k: Life.archiGet(JString(KO), JString(k))
    sk = [e["name"] for e in m.ARCHI if str(get("archi." + e["name"])).startswith("skip")]
    K.eq(sorted(sk), sorted(["forage", "b_spawn_forage", "b_farm_forage", "b_forage_minecave", "combat"]), "BUILT Foraging + its 3 bridges + the Combat door skipped")
    K.check(A["B"][fc] == "Furniture_Village_Bench" and A["B"][pad] == "Wood_Softwood_Planks", "BUILT the player's blocks are untouched")
    K.check(all(c not in A["B"] for c in m.ARCHI[1]["cells"] if c != fc), "BUILT nothing of the Foraging island was placed")
    K.check(all(A["B"].get(c) == b for e in m.ARCHI if str(get("archi." + e["name"])) == "done" for c, b in e["cells"].items() if not b.startswith("Skyy_Shard_")),
            "BUILT every other part is built (door blocks wait for SkyyShards; their pads stand)")
    K.check(not A["doors"] and get("archi.door.farming") is None, "BUILT no SkyyShards: no door recorded yet")
    # SkyyShards arrives: the doors are recorded on the next 30 s pass; the skipped Foraging / Combat shards come as items (owner here)
    A["shards"] = True
    mem = JClass("java.util.ArrayList")()
    Life.archiTick(JString(WC), JString(KO), st, mem, rows, JLong(10 ** 9))
    K.check(sorted(k for k, c, pk in A["doors"]) == ["farming", "mining", "orchard", "ranching"] and str(get("archi.door.farming")) == "+",
            "BUILT the 4 built islands' doors are recorded later")
    dcells = dict((e["key"], (tuple(e["door"]), [b for b in e["cells"].values() if b.startswith("Skyy_Shard_")])) for e in m.ARCHI if e["door"] and str(get("archi." + e["name"])) == "done")
    K.check(sorted(dcells) == ["farming", "mining", "orchard", "ranching"] and all(A["B"].get(c) == ids[0] for c, ids in dcells.values()),
            "BUILT fix2: ... and each recorded door's portal block is placed first (it was only the brick pad): %s" % dict((k, A["B"].get(c)) for k, (c, ids) in dcells.items()))
    K.eq(sorted(A["given"]), ["combat", "foraging"], "BUILT the skipped Foraging + Combat shards come as items (shard:fn:give)")
    Life.archiTick(JString(WC), JString(KO), st, mem, rows, JLong(10 ** 9 + 60000))
    K.check(len(A["given"]) == 2 and len(A["doors"]) == 4, "BUILT ... once")
    st3 = IS(JString(WC))
    nobody = JClass("java.lang.Object")[:]([])
    A2 = len(A["given"])
    Life.archiTick(JString(WC), JString(KO), st3, mem, nobody, JLong(10 ** 9 + 120000))
    K.check(len(A["given"]) == A2, "BUILT the item is never given while the owner is away")
    K.save()


def run_life(out, jar, scratch, _home):
    from jpype import JClass, JString, JLong
    K = HK.Child(out)
    m = layout()
    E = env(scratch, jar, "life")
    Life, IS, Cfg = E.Life, E.P("IsleState"), E.Cfg
    A = fresh(m)
    Life.API = T23.stand_in(PKG + "IsleApi", Api(A))
    st = IS(JString(WC))
    rows = rows_with_owner()
    drive(Life, IS, st, A, rows)
    ores = m.ARCHI[2]["ores"]
    A["B"].pop(ores[0])
    A["B"][ores[1]] = "Rock_Stone"
    A["B"][ores[2]] = "Furniture_Crude_Chest_Small"
    mem = T23.member(-41.0, 4.0)
    Life.archiTick(JString(WC), JString(KO), st, mem, rows, JLong(10 ** 9))
    K.check(A["B"][ores[0]] == "Ore_Copper_Stone" and A["B"][ores[1]] == "Ore_Copper_Stone" and A["B"][ores[2]] == "Furniture_Crude_Chest_Small",
            "LIFE the copper regrows on AIR / stone; a chest in an ore cell stays")
    A["B"].pop(ores[0])
    Life.archiTick(JString(WC), JString(KO), st, mem, rows, JLong(10 ** 9 + 60000))
    K.check(ores[0] not in A["B"], "LIFE ... only every archi.caveRegrowSec (120 s)")
    Life.archiTick(JString(WC), JString(KO), st, mem, rows, JLong(10 ** 9 + 121000))
    K.check(A["B"].get(ores[0]) == "Ore_Copper_Stone", "LIFE ... and then again")
    ids = str(Life.archiGet(JString(KO), JString("ranch.ids")))
    wild = [e.split("|")[2] for e in ids.split(";") if e.startswith("w|")]
    tame = [e.split("|")[2] for e in ids.split(";") if e.startswith("t|")]
    A["alive"].discard(wild[0])
    A["alive"].discard(tame[0])
    n0 = len(A["spawned"])
    Life.archiTick(JString(WC), JString(KO), st, mem, rows, JLong(10 ** 9 + 700000))
    K.check(len(A["spawned"]) == n0 + 1 and A["spawned"][-1][0] in ("Chicken", "Sheep_Lamb", "Cow_Calf"), "LIFE a caught wild animal comes back after ranch.respawnSeconds; a tamed one never")
    # fix (critic): an island that was unloaded (a fresh IsleState): its first pass never respawns; the pen not loaded = nothing; animals of
    # that role already near the ranch (saved in the chunk, untracked) count
    ids2 = str(Life.archiGet(JString(KO), JString("ranch.ids")))
    wild2 = [e.split("|") for e in ids2.split(";") if e.startswith("w|")]
    for e in wild2:
        A["alive"].discard(e[2])
    A["ranch_ground"] = (int(m.ARCHI[3]["animals"][0][1] // 1), int(m.ARCHI[3]["animals"][0][2] // 1) - 1, int(m.ARCHI[3]["animals"][0][3] // 1))
    stR = IS(JString(WC))
    n1 = len(A["spawned"])
    Life.archiTick(JString(WC), JString(KO), stR, mem, rows, JLong(10 ** 10))
    K.check(len(A["spawned"]) == n1 and int(stR.ranchAt) == 10 ** 10, "LIFE fix: a fresh island state (reloaded island) waits one ranch.respawnSeconds before any respawn")
    A["ranch_unloaded"] = True
    Life.archiTick(JString(WC), JString(KO), stR, mem, rows, JLong(10 ** 10 + 700000))
    K.check(len(A["spawned"]) == n1, "LIFE fix: the ranch not loaded: no respawn (the saved animals may still load)")
    A["ranch_unloaded"] = False
    A["extra"] = [("00000000-0000-4000-9000-%012d" % i, e[1]) for i, e in enumerate(wild2)]   # the old animals loaded back, untracked
    stR.ranchAt = 1
    Life.archiTick(JString(WC), JString(KO), stR, mem, rows, JLong(10 ** 10 + 1400000))
    K.check(len(A["spawned"]) == n1, "LIFE fix: %d untracked animals of those roles near the ranch count - no second herd" % len(wild2))
    A["extra"] = []
    stR.ranchAt = 1
    Life.archiTick(JString(WC), JString(KO), stR, mem, rows, JLong(10 ** 10 + 2100000))
    K.check(len(A["spawned"]) == n1 + len(wild2), "LIFE fix: really gone = %d wild animals come back" % len(wild2))
    # an island reset: the new world starts the archipelago again
    E2 = env(scratch, jar, "life2", {"archi.world": "skyy-island-old", "archi": "1", "archi.farm": "done"})
    A2 = fresh(m)
    Life.API = T23.stand_in(PKG + "IsleApi", Api(A2))
    st2 = IS(JString(WC))
    drive(Life, IS, st2, A2, rows)
    K.check(str(Life.archiGet(JString(KO), JString("archi.world"))) == WC and all(A2["B"].get(c) == b for c, b in m.ARCHI[0]["cells"].items()),
            "LIFE a reset island (archi.world was the old world) gets the archipelago again")
    # archi.existing off / new
    E3 = env(scratch, jar, "life3")
    A3 = fresh(m)
    Life.API = T23.stand_in(PKG + "IsleApi", Api(A3))
    Cfg.ARCHI_EXISTING = "off"
    st3 = IS(JString(WC))
    Life.archiOnce(JString(WC), JString(KO), st3, JLong(1), rows)
    K.check(A3["sets"] == 0 and Life.archiGet(JString(KO), JString("archi.world")) is None, "LIFE archi.existing off: nothing")
    Cfg.ARCHI_EXISTING = "new"
    E.St.KITDONE.remove(JString(KO))
    st3 = IS(JString(WC))
    Life.archiOnce(JString(WC), JString(KO), st3, JLong(1), rows)
    K.check(A3["sets"] == 0 and bool(st3.archiOff), "LIFE archi.existing new: an island made before (no kit this session) gets nothing")
    E.St.KITDONE.put(JString(KO), JClass("java.lang.Boolean").TRUE)
    st3 = IS(JString(WC))
    drive(Life, IS, st3, A3, rows)
    K.check(str(Life.archiGet(JString(KO), JString("archi"))) == "1", "LIFE archi.existing new: a new island (its kit went in this session) gets it")
    Cfg.ARCHI_EXISTING = "add"
    E4 = env(scratch, jar, "life4")
    Cfg.STARTER_DESIGN = "three"            # (after env(): its Cfg.load resets the field)
    A4 = fresh(m)
    Life.API = T23.stand_in(PKG + "IsleApi", Api(A4))
    st4 = IS(JString(WC))
    for i_ in range(50):
        Life.archiOnce(JString(WC), JString(KO), st4, JLong(1 + i_), rows)
    K.check(A4["sets"] == 0 and Life.archiGet(JString(KO), JString("archi.world")) is None, "LIFE starter.design three: no archipelago")
    # spec 5 shard.starterItems (archi.offItems): no archipelago here = the 6 shards as items, once each, only with the owner on the island
    nobody = JClass("java.lang.Object")[:](0)
    K.eq(int(Life.archiItems(JString(WC), JString(KO), st4, nobody, JLong(100000))), 0, "LIFE offItems: the owner not on the island = nothing yet")
    st4.doorsAt = 0
    n4 = int(Life.archiItems(JString(WC), JString(KO), st4, rows, JLong(200000)))
    K.check(n4 == 6 and sorted(A4["given"]) == sorted(["farming", "foraging", "mining", "ranching", "orchard", "combat"])
            and all(str(Life.archiGet(JString(KO), JString("archi.item." + k_))) == "given" for k_ in A4["given"]),
            "LIFE offItems: starter.design three = the 6 shards given as items, markers saved: %d %s" % (n4, A4["given"]))
    Life.archiItems(JString(WC), JString(KO), st4, rows, JLong(200000 + 31000))
    st5 = IS(JString(WC))
    Life.archiItems(JString(WC), JString(KO), st5, rows, JLong(900000))
    K.check(len(A4["given"]) == 6, "LIFE offItems: never twice (also after a restart)")
    E6 = env(scratch, jar, "life6")
    Cfg.STARTER_DESIGN = "three"
    Cfg.ARCHI_ITEMS = False
    A6 = fresh(m)
    Life.API = T23.stand_in(PKG + "IsleApi", Api(A6))
    Life.archiItems(JString(WC), JString(KO), IS(JString(WC)), rows, JLong(200000))
    K.check(not A6["given"], "LIFE offItems false: nothing given")
    Cfg.ARCHI_ITEMS = True
    Cfg.STARTER_DESIGN = "archipelago"
    Life.API = T23.stand_in(PKG + "IsleApi", Api(A6))
    st6 = IS(JString(WC))
    drive(Life, IS, st6, A6, rows)
    Life.archiItems(JString(WC), JString(KO), st6, rows, JLong(10 ** 9))
    K.check(not A6["given"], "LIFE offItems: an island with the archipelago gets doors, never the items")
    K.save()


def run_cfg(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    E = T23.Env(scratch, jar, "cfg")
    Cfg, Pl, Arc = E.Cfg, E.P("PlaceFn")(), E.P("ArchiIsles")
    t = open(os.path.join(E.home, "config.properties"), encoding="latin-1").read() if os.path.isfile(os.path.join(E.home, "config.properties")) else ""
    K.check(str(Cfg.STARTER_DESIGN) == "archipelago" and str(Cfg.ARCHI_EXISTING) == "add" and int(Cfg.CAVE_REGROW) == 120 and int(Cfg.RANCH_RESPAWN) == 600
            and str(Cfg.RANCH_TAMED) == "Tamed_Cow:2,Tamed_Sheep:2,Tamed_Chicken:3", "CFG the defaults")
    f = os.path.join(E.home, "config.properties")
    for v, want in (("three", "three"), ("classic", "classic"), ("archipelago", "archipelago"), ("junk", "archipelago")):
        open(f, "w").write("starter.design=%s\narchi.existing=NEW\narchi.caveRegrowSec=99999\n" % v)
        Cfg.load("")
        K.check(str(Cfg.STARTER_DESIGN) == want and str(Cfg.ARCHI_EXISTING) == "new" and int(Cfg.CAVE_REGROW) == 3600, "CFG starter.design=%s reads %s (+ clamps)" % (v, want))
    # the one-time update plan
    open(f, "w").write("starter.design=three\n")
    K.eq(int(Cfg.plan0525()), 1, "CFG plan: an untouched starter.design=three is planned")
    open(f, "w").write("starter.design=classic\n")
    K.check(int(Cfg.plan0525()) == 0 and "kept classic" in str(list(Cfg.MIG25_NOTE)), "CFG plan: classic (an admin's value) kept")
    open(f, "w").write("starter.design=three\n")
    open(os.path.join(E.home, "config-changes.log"), "w", encoding="utf8").write("2026-10-20T10:00:00\tSkyy\t-\tmenu\tstarter.design\tclassic\tthree\tok\n")
    K.check(int(Cfg.plan0525()) == 0, "CFG plan: three set by an admin (config-changes.log) kept")
    open(os.path.join(E.home, "migrations.properties"), "w").write("starter.0.5.25=2026-10-23 | done\n")
    K.eq(int(Cfg.plan0525()), -1, "CFG plan: the step ran before = nothing")
    # island:fn:place
    Cfg.STARTER_DESIGN = "archipelago"
    r = Pl.apply(JString("farm"))
    K.check(r is not None and str(r).startswith("island|29.5|129.0|-25.5"), "CFG island:fn:place farm = the Farming island: %s" % r)
    K.check(all(Pl.apply(JString(n)) is not None for n in ("forage", "minecave", "orchard", "ranch", "island1", "cave")), "CFG every archipelago place + the starter ones")
    Cfg.STARTER_DESIGN = "three"
    K.check(Pl.apply(JString("farm")) is None and Pl.apply(JString("island1")) is not None, "CFG three: no archipelago places")
    Cfg.STARTER_DESIGN = "archipelago"
    K.save()


def run_live25(out, jar, scratch, home):
    from jpype import JClass, JString
    K = HK.Child(out)
    h0 = HK.tree_hash(home)
    E = T23.Env(scratch, jar, "lv")
    Cfg, St = E.Cfg, E.St
    Cfg.FILE = E.Paths.get(os.path.join(home, "config.properties"))
    mask = int(Cfg.plan0525())
    t = open(os.path.join(home, "config.properties"), encoding="latin-1").read()
    K.check(("starter.design=three" in t and mask == 1) or mask in (0, -1), "LIVE the live config's starter.design update plan: %d (%s)" % (mask, list(Cfg.MIG25_NOTE)))
    Cfg.load("")
    isl = os.path.join(home, "islands")
    St.DIR = E.Paths.get(isl)
    St.IO = None
    St.SETTINGS.clear()
    St.loadIslandWorlds()
    keys = [f[:-11] for f in os.listdir(isl) if f.endswith(".properties")] if os.path.isdir(isl) else []
    bad = [k for k in keys if St.settings(JString(k)) is None]
    K.check(keys and not bad, "LIVE every island file reads (%d)" % len(keys))
    K.check(HK.tree_hash(home) == h0, "LIVE nothing changed on disk")
    K.save()


def run_live2(out, jar, scratch, home):
    """START TWICE on a scratch COPY of the live data: the plugin's setup order for the one-time update (plan0525 before the kit, the kit,
    apply0525 through the kit) - start 1 moves an untouched starter.design=three to archipelago (History, change log, the step marker, every
    other byte + the line endings kept), start 2 writes nothing"""
    from jpype import JClass, JString
    K = HK.Child(out)
    E = T23.Env(scratch, jar, "lv2")
    Cfg, St = E.Cfg, E.St
    cfgf = os.path.join(home, "config.properties")
    Cfg.FILE = E.Paths.get(cfgf)
    Pub, Hooks = E.P("CfgPub"), E.P("IslandHooks")
    LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyIslands")
    raw0 = open(cfgf, "rb").read()
    had3 = b"\nstarter.design=three" in b"\n" + raw0

    def snap():
        r = {}
        for dp, _dn, fn in os.walk(home):
            for f_ in fn:
                p_ = os.path.join(dp, f_)
                r[os.path.relpath(p_, home)] = open(p_, "rb").read()
        return r
    notes = []
    for rnd in range(2):
        s0 = snap()
        Cfg.load("")
        mask = int(Cfg.plan0525())
        Pub.start(E.Paths.get(os.path.dirname(home)), LOG)
        res = str(Hooks.apply0525(mask))
        Pub.shutdown()
        Cfg.load("")
        s1 = snap()
        chg = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
        notes.append((rnd + 1, mask, res[:90], chg))
        if rnd == 0 and had3:
            raw1 = open(cfgf, "rb").read()
            K.check(mask == 1 and str(Cfg.STARTER_DESIGN) == "archipelago", "LIVE2 start 1: the live starter.design=three moves to archipelago (%d, %s)" % (mask, res[:80]))
            K.check(raw1.replace(b"starter.design=archipelago", b"starter.design=three") == raw0,
                    "LIVE2 start 1: only that line changed (every other byte and line ending kept)")
            K.check(any(k.startswith("history") or "history" in k.lower() for k in chg), "LIVE2 start 1: a History snapshot was written first: %s" % chg)
            log = open(os.path.join(home, "config-changes.log"), encoding="utf8", errors="replace").read()
            K.check("starter.design" in log.splitlines()[-1] and "archipelago" in log.splitlines()[-1], "LIVE2 start 1: one change-log line (Undo): %s" % log.splitlines()[-1][:120])
            mg = open(os.path.join(home, "migrations.properties"), encoding="utf8").read()
            K.check("starter.0.5.25=" in mg and "defaults.0.5.3=" in mg, "LIVE2 start 1: the step marker written, the 0.5.3 one kept")
        elif rnd == 0:
            K.check(mask in (0, -1), "LIVE2 start 1: the live starter.design is not an untouched three - nothing planned (%d)" % mask)
        else:
            K.check(mask == -1 and not chg, "LIVE2 start 2: the step ran before - nothing written (%d, %s)" % (mask, chg))
    print("LIVE2 two starts on the live copy: %s" % notes)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("archi", run_archi), ("built", run_built), ("door", run_door), ("fix2", run_fix2), ("life", run_life), ("cfg", run_cfg),
                   ("unload", T24.run_unload), ("early", T23.run_early), ("ids", T23.run_ids), ("boss", T23.run_boss), ("clear", T23.run_clear),
                   ("time", T23.run_time), ("live", run_live25), ("live2", run_live2)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyIslands"))
