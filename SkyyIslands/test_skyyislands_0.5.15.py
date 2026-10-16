"""Harness for SkyyIslands 0.5.15 (the Shardkeeper stops after the quest, every death of a player with an island ends on that island, the
old bed in island 1's ruins; tools/islands_0_5_15_patch.py). Build first:
python tools/islands_0_5_15_patch.py && python SkyyIslands/build_skyyislands_0.5.15.py

    python SkyyIslands/test_skyyislands_0.5.15.py [--dir <folder inside tools/dev/scratch/>] [--keep]

  A / C / AA  verify (-Xverify:all), class compare 0.5.14 -> 0.5.15 (exactly the planned members + manifest + the layout data), engine-access
        audit
  P15   EXECUTED on stand-in worlds (IsleLife.API = a Python IsleApi; real IslandStore island files in scratch, real config kit rows):
        CFG     boss.stopAfterQuest: a fresh file lists it, default on, hand edit read, an old file without it = default (not rewritten),
                the Server Setup row (Starter islands, bool, live)
        BOSS    quest unknown -> spawns as before (the OWNER's tutorial.mini_boss asked); not done -> spawns after the cooldown; done +
                repaired portal -> no new Shardkeeper, boss.done=1 saved, asked at most every 10 s; a living one is left alone; restart
                -> the file answers (no ask); the owner's Hub Shard (hubshards.properties) without SkyyQuests -> stops; co-op: only the
                owner's task is asked (a member's never); no lock-out: portal broken + nobody holds a shard -> it still comes, a member
                holding a shard -> not; boss.stopAfterQuest off -> 0.5.14 (respawns); bytecode order (setting + bossDone before spawn)
        DEATH   route table; the EXACT sequences: died on the own island (engine kept them there) -> to the bed / spawn on it (goHome),
                already there -> nothing (4); died on the island but the engine moved them to the default world's spawn (= the hub) ->
                routed from the world they are IN to the ISLAND (never the hub); died in the hub -> island; co-op member on the co-op
                island -> the co-op island; shard death -> kept; no island -> hub; IsleTask mode 5 -> 4 on the current world
                review fixes: spawn not ready on the own island (-2) / not in the named world yet (-1) -> exactly ONE retry in 1 s, then
                silently nothing (no /island line, no hub)
        BED     the layout has the ruins bed (cells free, on grass, beside the wall); an existing 3-island island gets it once (12 cells
                air + grass ground), bed.placed=1, never again; a player's block in a cell / on the ground -> never (skip); a cell not
                loaded -> later; a new island (bed in the layout) -> only remembered; a classic island -> nothing; /island reset clears
                boss.done + bed.placed
  The REAL server phase is NOT RUN here (tools/smoke_test.py covers the ready line) - the bed's fillers / facing are UNVERIFIED in game.
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import soundpass_kit as SK

VERSION = "0.5.15"
PKG = "com.skyy.islands."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-0.5.14.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "islands0515", "h")))

EXPECT = {
    "IslandCfg": ["+f BOSS_STOP", "~<clinit>", "~m load"],
    "CfgFile": ["~<clinit>"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],                                  # the version string
    "IslandStore": ["~m setWorldName0"],                       # /island reset clears boss.done + bed.placed
    "IsleApi": ["+m worldOf", "+m later"],
    "IsleEng": ["+m worldOf", "+m later", "~m goHome"],
    "IsleState": ["+f bossDone", "+f bossAt", "+f bedDone"],
    "IsleTask": ["~m run"],
    "IsleLife": ["+f BOSS_TASK", "+f BED_ID", "+f BEDP", "+f BED_CELLS", "+f BED_GROUND", "+f BEDS", "~<clinit>", "+m bossDone",
                 "+m bossNeeded", "~m bossTick", "+m bedOnce", "~m tickWorld", "~m route", "-m respawn", "+m respawn", "+m respawnRetry"],
    "SkyyIslandsPlugin": ["~m setup"],
    "FillTask": ["~m run"],                                    # the layout's block count + 1 (the bed)
    "StarterIsles": ["~<clinit>", "~m decode", "~m fill"],     # the layout data (+ the bed)
}
ADDED = []


def run_compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """the kit's compare; its non-class check replaced: only the manifest changes (Version / Name)"""
    HK._kit_compare(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    d["fails"] = [f for f in d["fails"] if not f.startswith("C: non-class entries changed")]
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    na = set(n_ for n_ in za.namelist() if not n_.endswith(".class"))
    nb = set(n_ for n_ in zb.namelist() if not n_.endswith(".class"))
    changed = sorted(n_ for n_ in na & nb if za.read(n_) != zb.read(n_))
    if na != nb or changed != ["manifest.json"]:
        d["fails"].append("C: non-class entries: added %s removed %s changed %s" % (sorted(nb - na), sorted(na - nb), changed))
    ma, mb = json.loads(za.read("manifest.json")), json.loads(zb.read("manifest.json"))
    for m_, v_ in ((ma, "0.5.14"), (mb, VERSION)):
        if m_.pop("Version", None) != v_ or m_.pop("Name", None) != v_ + " SkyyIslands":
            d["fails"].append("C: manifest Version / Name are not %s" % v_)
    if ma != mb:
        d["fails"].append("C: manifest changed beyond Version / Name")
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


KA, KB, KC, KD, KE, KN, KM = ["00000000-0000-4000-8000-0000000%05x" % (0xa0515 + i) for i in range(7)]
WA, WC, WD, WE, WS = "skyy-island-" + KA, "skyy-island-" + KC, "skyy-island-" + KD, "skyy-island-" + KE, "skyy-shard-" + KA


def run_p15(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride, JArray, JObject, JString, JLong, JInt
    K = HK.Child(out)
    m = layout_of(VERSION)
    m14 = layout_of("0.5.14")
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    P = lambda n: JClass(PKG + n)
    St, Cfg, Life, Task, Rows = P("IslandStore"), P("IslandCfg"), P("IsleLife"), P("IsleTask"), P("CfgRows")
    Paths, UUID, Double, HashSet = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Double"), JClass("java.util.HashSet")
    uA, uB, uC, uD, uE, uN, uM = [UUID.fromString(k) for k in (KA, KB, KC, KD, KE, KN, KM)]
    shutil.rmtree(os.path.join(scratch, "p15"), ignore_errors=True)
    home = os.path.join(scratch, "p15", "Skyy_SkyyIslands")
    isl = os.path.join(home, "islands")
    os.makedirs(isl, exist_ok=True)

    # ---------------------------------------------------------------- CFG
    cf = os.path.join(home, "config.properties")
    Cfg.FILE = Paths.get(cf)
    Cfg.load("")
    txt = open(cf, encoding="utf-8").read()
    K.check("boss.stopAfterQuest=true" in txt.splitlines() and bool(Cfg.BOSS_STOP), "CFG a fresh config.properties lists boss.stopAfterQuest=true; default on")
    old = "\n".join(l for l in txt.splitlines() if "boss.stopAfterQuest" not in l and "0.5.15" not in l and "portal is broken and nobody" not in l) + "\n"
    open(cf, "w", encoding="utf-8").write(old)
    Cfg.BOSS_STOP = False
    Cfg.load("")
    K.check(bool(Cfg.BOSS_STOP) and open(cf, encoding="utf-8").read() == old, "CFG a 0.5.14 file without the line = default on, not rewritten")
    open(cf, "w", encoding="utf-8").write(old + "boss.stopAfterQuest=FALSE\n")
    Cfg.load("")
    K.check(not bool(Cfg.BOSS_STOP), "CFG hand edit (FALSE) read")
    open(cf, "w", encoding="utf-8").write(txt)
    Cfg.load("")
    rows = SK.kit_rows(Rows)
    r_ = rows.get("boss.stopAfterQuest")
    K.check(r_ is not None and tuple(r_[2:5]) == ("isles", "bool", "true") and "live" in r_[9],
            "ROW Server Setup -> Starter islands -> Boss stops after the quest (bool, default on, live): %s" % (r_ and r_[:5],))

    # ---------------------------------------------------------------- island files + the stand-in engine
    def wfile(k, props):
        with open(os.path.join(isl, k + ".properties"), "w", encoding="utf-8") as f:
            f.write("".join("%s=%s\n" % kv for kv in props.items()))

    def fread(k):
        p = os.path.join(isl, k + ".properties")
        return dict(l.split("=", 1) for l in open(p, encoding="utf-8").read().splitlines() if "=" in l and not l.startswith("#"))
    wfile(KA, {"v": "5", "world": WA, "members": KB, "isles": "3", "portal": "1"})
    wfile(KC, {"v": "5", "world": WC, "isles": "3"})
    wfile(KD, {"v": "5", "world": WD, "isles": "3"})
    wfile(KE, {"v": "5", "world": WE})                      # a classic island (no isles=3 - the probe finds no deep stone)
    St.DIR = Paths.get(isl)
    St.IO = None
    St.STOPPING = False
    St.SETTINGS.clear()
    St.loadIslandWorlds()
    K.check(bool(St.isIslandWorld(WA)) and str(St.ownerOf(WA)) == KA and str(St.homeKey(uB)) == KA and str(St.homeKey(uN)) == KN,
            "SETUP island A (member B), C, D, E (classic); B's home is A's island; N has no island")

    class World(object):
        def __init__(self, blocks):
            self.blocks, self.players, self.npcs, self.unloaded = dict(blocks), {}, {}, set()

    class Api(object):
        def __init__(self):
            self.t = 5000000
            self.w = {WA: World(m.S3_L), WC: World(m14.S3_L), WD: World(m.S3_L), WE: World({}), WS: World({}), "hub": World({}), "default": World({})}
            self.inv, self.quest, self.where, self.beds = {}, {}, {}, set()
            self.log, self.queue, self.home_ret, self.n, self.later = [], [], 2, 0, []

        def ev(self, *a):
            self.log.append(a)

        def kinds(self, k):
            return [e for e in self.log if e[0] == k]

        def drain(self):
            while self.queue:
                self.queue.pop(0).run()
    A = Api()

    @JImplements(PKG + "IsleApi")
    class Stand(object):
        @JOverride
        def now(self):
            return JLong(A.t)

        @JOverride
        def players(self, wn):
            w = A.w.get(str(wn))
            return JArray(JObject)([] if w is None else [JArray(JObject)([UUID.fromString(k), Double(v[0]), Double(v[1]), Double(v[2])]) for k, v in w.players.items()])

        @JOverride
        def npcs(self, wn, x, y, z, r):
            out_ = JClass("java.util.ArrayList")()
            w = A.w.get(str(wn))
            for k, v in ([] if w is None else w.npcs.items()):
                if v[4] and (v[1] - x) ** 2 + (v[2] - y) ** 2 + (v[3] - z) ** 2 <= r * r:
                    out_.add(JArray(JObject)([JString(k), JString(v[0])]))
            return out_

        @JOverride
        def alive(self, wn, uuid):
            w = A.w.get(str(wn))
            return bool(w is not None and uuid is not None and str(uuid) in w.npcs and w.npcs[str(uuid)][4])

        @JOverride
        def roleOk(self, role):
            return True

        @JOverride
        def spawn(self, wn, role, x, y, z, yaw):
            A.n += 1
            k = "00000000-0000-4000-9000-%012d" % A.n
            A.w[str(wn)].npcs[k] = [str(role), float(x), float(y), float(z), True]
            A.ev("spawn", str(wn), str(role), k)
            return JString(k)

        @JOverride
        def level(self, wn, uuid, lvl, name):
            return True

        @JOverride
        def block(self, wn, x, y, z):
            w = A.w.get(str(wn))
            if w is None or (int(x), int(y), int(z)) in w.unloaded:
                return None
            return JString(w.blocks.get((int(x), int(y), int(z)), ""))

        @JOverride
        def setBlock(self, wn, x, y, z, bid):
            k = (int(x), int(y), int(z))
            w = A.w[str(wn)]
            if str(bid):
                w.blocks[k] = str(bid)
            else:
                w.blocks.pop(k, None)
            A.ev("set", str(wn), k, str(bid))
            return True

        @JOverride
        def count(self, wn, u, bid):
            return JLong(A.inv.get(str(u), {}).get(str(bid), 0))

        @JOverride
        def take(self, wn, u, bid, n):
            have = A.inv.setdefault(str(u), {}).get(str(bid), 0)
            t = min(have, int(n))
            A.inv[str(u)][str(bid)] = have - t
            return JLong(t)

        @JOverride
        def give(self, wn, u, bid, n):
            bag = A.inv.setdefault(str(u), {})
            bag[str(bid)] = bag.get(str(bid), 0) + int(n)
            return JLong(int(n))

        @JOverride
        def say(self, u, text, color):
            A.ev("say", str(u), str(text))

        @JOverride
        def name(self, u):
            return JString("P" + str(u)[-4:])

        @JOverride
        def toHub(self, wn, u):
            A.ev("hub", str(wn), str(u))
            return True

        @JOverride
        def hasBed(self, u, inWorld):
            return (str(u), str(inWorld)) in A.beds

        @JOverride
        def goHome(self, wn, u, hk, homew):
            A.ev("home", str(wn), str(u), str(hk), str(homew))
            return JInt(A.home_ret)

        @JOverride
        def exec(self, wn, r):
            if str(wn) not in A.w:
                return False
            A.queue.append(r)
            return True

        @JOverride
        def save(self, r):
            r.run()
            return False

        @JOverride
        def quest(self, u, key):
            A.ev("quest", str(u), str(key))
            return True

        @JOverride
        def isAdmin(self, u):
            return False

        @JOverride
        def hubWorld(self):
            return JString("hub")

        @JOverride
        def islandWorlds(self):
            s_ = HashSet()
            for k, w in A.w.items():
                if w.players and St.isIslandWorld(k):
                    s_.add(JString(k))
            return s_

        @JOverride
        def relight(self, wn):
            A.ev("relight", str(wn))

        @JOverride
        def rot(self, wn, x, y, z):
            return -1

        @JOverride
        def gameTime(self, wn):
            return JLong(-(2 ** 63))

        @JOverride
        def timeFlags(self, wn):
            return -1

        @JOverride
        def setGameTime(self, wn, ms):
            return False

        @JOverride
        def setTimePaused(self, wn, p):
            return False

        @JOverride
        def timeWorlds(self):
            return HashSet()

        @JOverride
        def questDone(self, owner, task):
            A.ev("ask", str(owner), str(task))
            return int(A.quest.get(str(owner), -1))

        @JOverride
        def worldOf(self, u):
            w = A.where.get(str(u))
            return None if w is None else JString(w)

        @JOverride
        def later(self, r, ms):
            A.later.append((r, int(ms)))
            return True
    Life.API = Stand()
    Life.ST.clear()
    Life.loadGot(Paths.get(os.path.join(home, "hubshards.properties")))
    ISL1, ARENA = (8.5, 129.0, 8.5), (71.5, 130.0, 34.5)
    ROLE = str(Cfg.BOSS_ROLE)

    def tick(wn):
        return int(Life.tickWorld(JString(wn)))

    def place(wn, k, pos):
        for w in A.w.values():
            w.players.pop(k, None)
        A.w[wn].players[k] = list(pos)

    def clear_players():
        for w in A.w.values():
            w.players.clear()

    def spawns(wn):
        return [e for e in A.kinds("spawn") if e[1] == wn]

    def kill_all(wn):
        for k in list(A.w[wn].npcs):
            A.w[wn].npcs[k][4] = False
        st_ = Life.state(JString(wn))
        st_.boss = None
        st_.bossNext = JLong(0)

    L0 = m.S3_L
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

    # ---------------------------------------------------------------- BOSS
    K.eq(str(Life.BOSS_TASK), "tutorial.mini_boss", "BOSS the task id = SkyyQuests 0.3.3 line tutorial, task mini_boss (Defeat the mini boss)")
    qsrc = open(os.path.join(ROOT, "SkyyQuests", "build_skyyquests_0.3.3.py"), encoding="utf-8").read()
    K.check('("mini_boss", "Defeat the mini boss"' in qsrc and '("defeat_mobs", "Defeat 5 mobs"' in qsrc, "BOSS SkyyQuests 0.3.3 names the task mini_boss (as defeat_mobs for the camp)")
    clear_players()
    place(WA, KB, ARENA)                     # a co-op member at the arena; the owner offline (quest unknown); portal repaired (Skyy's case)
    tick(WA)
    K.check(len(spawns(WA)) == 1 and spawns(WA)[0][2] == ROLE and A.kinds("ask")[-1:] == [("ask", KA, "tutorial.mini_boss")],
            "BOSS quest state unknown (owner offline / no SkyyQuests), no Hub Shard record -> the Shardkeeper spawns as before; the OWNER's task asked")
    boss1 = spawns(WA)[0][3]
    A.quest[KA] = 0
    kill_all(WA)
    A.t += 11000
    tick(WA)
    K.eq(len(spawns(WA)), 2, "BOSS the owner has not done Defeat the mini boss -> it spawns again after the cooldown (spawns before done)")
    A.quest[KA] = 1
    A.quest[KB] = 1
    A.t += 3000
    na = len(A.kinds("ask"))
    tick(WA)                                # the second one is alive: nothing asked, nothing spawned
    K.check(len(A.kinds("ask")) == na and len(spawns(WA)) == 2, "BOSS while a Shardkeeper is alive nothing is asked")
    alive_id = spawns(WA)[1][3]
    st = Life.state(JString(WA))
    st.boss = None                          # forget the tracked id: the live one is found again by the arena scan, not respawned
    A.t += 400000
    tick(WA)
    K.check(len(spawns(WA)) == 2 and A.w[WA].npcs[alive_id][4] and str(st.boss) == alive_id,
            "BOSS a living Shardkeeper is left alone (found again, never despawned, no second one)")
    kill_all(WA)
    A.t += 1000
    na = len(A.kinds("ask"))
    tick(WA)
    K.check(len(spawns(WA)) == 2 and fread(KA).get("boss.done") == "1" and A.kinds("ask")[na:] == [("ask", KA, "tutorial.mini_boss")],
            "BOSS done + portal repaired -> no new Shardkeeper (none after); boss.done=1 in the island file")
    na = len(A.kinds("ask"))
    for _ in range(3):
        A.t += 2000
        tick(WA)
    K.check(len(A.kinds("ask")) == na and len(spawns(WA)) == 2, "BOSS remembered: no more asks, no spawns")
    Life.ST.clear()
    A.quest.pop(KA)
    A.t += 400000
    tick(WA)
    K.check(len(spawns(WA)) == 2 and len(A.kinds("ask")) == na, "BOSS after a restart the island file answers (no ask, no spawn)")
    Cfg.BOSS_STOP = False
    kill_all(WA)
    A.t += 1000
    tick(WA)
    K.eq(len(spawns(WA)), 3, "BOSS boss.stopAfterQuest off -> 0.5.14 behaviour (respawns after the cooldown)")
    Cfg.BOSS_STOP = True
    # the 10 s ask throttle (a fresh island D, owner online-unknown -> not done)
    clear_players()
    place(WD, KD, ARENA)
    A.quest[KD] = 0
    tick(WD)
    nd = len(spawns(WD))
    kill_all(WD)
    A.t += 3000
    na = len(A.kinds("ask"))
    tick(WD)
    K.check(len(A.kinds("ask")) == na, "BOSS asked at most every 10 s (%d spawns)" % nd)
    # co-op uses the owner: island C (owner C, member M) - a member's done task never counts
    wfile(KC, {"v": "5", "world": WC, "members": KM, "isles": "3", "portal": "1"})
    St.reloadOne(KC)
    St.loadIslandWorlds()
    Life.ST.clear()
    clear_players()
    A.quest[KM] = 1
    A.quest[KC] = 0
    place(WC, KM, ARENA)
    na = len(A.kinds("ask"))
    tick(WC)
    asks = A.kinds("ask")[na:]
    K.check(len(spawns(WC)) == 1 and asks and all(a_[1] == KC for a_ in asks), "BOSS co-op: only the island OWNER's task is asked (the member's done task does not stop it)")
    A.quest[KC] = 1
    kill_all(WC)
    A.t += 11000
    tick(WC)
    K.check(len(spawns(WC)) == 1 and fread(KC).get("boss.done") == "1", "BOSS co-op: the owner's done task stops it for the whole island")
    # the Hub Shard record without SkyyQuests: island D owner got their first shard (hubshards.properties), quest unknown
    with open(os.path.join(home, "hubshards.properties"), "w", encoding="utf-8") as f:
        f.write("%s=123\n" % KD)
    Life.loadGot(Paths.get(os.path.join(home, "hubshards.properties")))
    wfile(KD, dict(list(fread(KD).items()) + [("portal", "1")]))
    St.reloadOne(KD)
    A.quest.pop(KD)
    Life.ST.clear()
    clear_players()
    place(WD, KD, ARENA)
    kill_all(WD)
    nd = len(spawns(WD))
    A.t += 11000
    na = len(A.kinds("ask"))
    tick(WD)
    K.check(len(spawns(WD)) == nd and fread(KD).get("boss.done") == "1" and len(A.kinds("ask")) == na,
            "BOSS the owner already has their Hub Shard (no SkyyQuests / owner offline) -> stops, boss.done=1, nothing asked")
    # no lock-out: island A (done) after a reset-like state - portal broken, nobody holds a shard -> it still comes; a member holds one -> not
    wfile(KA, dict((k_, v_) for k_, v_ in fread(KA).items() if k_ != "portal"))
    St.reloadOne(KA)
    Life.ST.clear()
    clear_players()
    sock = tuple(m.S3_P2["socket"])
    A.w[WA].blocks[sock] = L0.get(sock, "")        # the broken socket again (a repaired pad there would count as repaired)
    place(WA, KB, ARENA)
    kill_all(WA)
    A.inv[KB] = {str(Life.SHARD): 1}
    A.t += 1000
    n0 = len(spawns(WA))
    tick(WA)
    K.eq(len(spawns(WA)), n0, "BOSS done, portal broken, a member there holds a Hub Shard -> no new Shardkeeper")
    A.inv[KB] = {}
    A.t += 1000
    tick(WA)
    K.eq(len(spawns(WA)), n0 + 1, "BOSS done, portal broken, NOBODY holds a Hub Shard -> it still comes (the shard's only source - no lock-out)")
    bt = code("IsleLife", "bossTick")
    K.check(0 <= bt.find("IslandCfg.BOSS_STOP") < bt.find("IsleLife.bossDone") < bt.find("IsleLife.bossNeeded") < bt.find("IsleApi.spawn")
            and bt.find("IsleApi.alive") < bt.find("IslandCfg.BOSS_STOP"), "BOSS shape: bossTick = alive / found first, then the setting + bossDone + bossNeeded, then spawn")
    bd = code("IsleLife", "bossDone")
    K.check('"boss.done"' in bd and "ConcurrentHashMap.containsKey" in bd and "IsleApi.questDone" in bd, "BOSS shape: bossDone = the file, the Hub Shard record, quest:fn:done")

    # ---------------------------------------------------------------- DEATH (respawn routing)
    rt = lambda *a: int(Life.route(*[JString(x) if isinstance(x, str) else x for x in a]))
    table = [((WA, WA, False, "hub", True), 3, "died on the own island -> its bed / spawn (3)"),
             ((WA, WA, True, "hub", True), 3, "died on the own island with a bed there -> the bed (3)"),
             ((WC, WA, False, "hub", True), 1, "died on another island -> own island"),
             ((WC, WA, True, "hub", True), 0, "another island with a bed set there -> that bed (kept)"),
             (("hub", WA, False, "hub", True), 1, "died in the hub -> own island"),
             (("default", WA, False, "hub", True), 1, "died in another world -> own island"),
             (("hub", None, False, "hub", True), 0, "no island, died in the hub -> stay"),
             (("default", None, False, "hub", True), 2, "no island, died elsewhere -> hub"),
             ((WA, WA, False, "hub", False), 0, "setting off -> engine")]
    K.eq([rt(*t[0]) for t in table], [t[1] for t in table], "DEATH route table: " + "; ".join(t[2] for t in table))
    A.log[:] = []
    clear_players()
    A.home_ret = 2
    # (1) died on the own island, the engine kept them there
    place(WA, KA, ARENA)
    A.where[KA] = WA
    K.eq(int(Life.respawn(JString(WA), uA, JString(WA))), 3, "DEATH died on the own island -> routed (3)")
    K.check(A.kinds("home")[-1:] == [("home", WA, KA, KA, WA)] and not A.kinds("hub"), "DEATH ... goHome to the island's bed / spawn, never the hub")
    A.home_ret = 4
    K.eq(int(Life.respawn(JString(WA), uA, JString(WA))), 4, "DEATH ... already at the bed / spawn -> nothing more (4)")
    A.home_ret = 2
    # (2) Skyy's sequence: died on the island (void / boss), the engine respawned them at the default world's spawn = the hub
    A.log[:] = []
    place("hub", KA, (-295.0, 123.0, 72.6))
    A.where[KA] = "hub"
    Task(5, JString(WA), uA).run()
    K.check(len(A.queue) == 1 and str(A.queue[0].wn) == "hub" and str(A.queue[0].a) == WA and int(A.queue[0].mode) == 4,
            "DEATH mode 5 queues the routing on the world the player is IN (the hub), remembering the death world")
    A.drain()
    K.check(A.kinds("home") == [("home", "hub", KA, KA, WA)] and not A.kinds("hub"),
            "DEATH died on the island, put at the hub's spawn -> sent to the ISLAND (not left in / sent to the hub)")
    # (3) the log's 01:16 sequence: died in the hub world -> the island
    A.log[:] = []
    Task(5, JString("hub"), uA).run()
    A.drain()
    K.check(A.kinds("home") == [("home", "hub", KA, KA, WA)], "DEATH died in the hub -> the island")
    # (4) died on the island, the engine kept them on the island, worldOf unknown -> the death world
    A.log[:] = []
    place(WA, KA, ISL1)
    A.where.pop(KA)
    Task(5, JString(WA), uA).run()
    A.drain()
    K.check(A.kinds("home") == [("home", WA, KA, KA, WA)], "DEATH worldOf unknown -> routed on the death world as before")
    # co-op member on the co-op island
    A.log[:] = []
    place(WA, KB, ARENA)
    K.eq(int(Life.respawn(JString(WA), uB, JString(WA))), 3, "DEATH a co-op member died on the co-op island -> routed (3)")
    K.check(A.kinds("home")[-1:] == [("home", WA, KB, KA, WA)], "DEATH ... to the CO-OP island (homeKey)")
    # shard death kept, no island -> hub, not in the world -> -1, a bed where they died (another island) kept
    place(WS, KA, ISL1)
    K.eq(int(Life.respawn(JString(WS), uA, JString(WS))), 0, "DEATH a shard world keeps its own respawn (islands.respawnKeep)")
    A.log[:] = []
    place("default", KN, (0.0, 100.0, 0.0))
    K.eq(int(Life.respawn(JString("default"), uN, JString("default"))), 2, "DEATH no island -> the hub")
    K.check(A.kinds("hub") == [("hub", "default", KN)] and not A.kinds("home"), "DEATH ... toHub, no island trip")
    K.eq(int(Life.respawn(JString(WC), uN, JString(WC))), -1, "DEATH not in that world -> -1")
    place(WC, KA, ISL1)
    A.beds.add((KA, WC))
    A.log[:] = []
    K.eq(int(Life.respawn(JString(WC), uA, JString(WC))), 0, "DEATH a bed set on the island where they died (not theirs) -> that bed stays")
    gh = code("IsleEng", "goHome")
    K.check("TransformComponent.getPosition" in gh and "Transform.getPosition" in gh and "double 4.0" in gh and gh.find("double 4.0") < gh.find("Teleport.createForPlayer"),
            "DEATH shape: goHome skips a same-world teleport within 2 blocks of the bed / spawn")
    wo = code("IsleEng", "worldOf")
    K.check("PlayerRef.getWorldUuid" in wo and "Universe.getWorld" in wo, "DEATH shape: worldOf = the PlayerRef's world")
    tr = code("IsleTask", "run")
    K.check("IsleApi.worldOf" in tr and "IsleLife.respawn" in tr and "IsleLife.respawnRetry" in tr, "DEATH shape: IsleTask mode 5 -> worldOf -> mode 4 there (-> one retry)")
    # review fix 1: died on the own island, the island spawn point not ready (goHome -2) -> once more in 1 s, then silently nothing
    gi = gh.find("IslandCmd.go")
    K.check(gh.count("bipush 254") == 2 and 0 < gh.rfind("bipush 254") < gi,   # bipush 0xFE = -2 (the printer shows the byte unsigned)
            "DEATH shape: goHome answers -2 (twice: spawn not ready / teleport failed on the island) before /island's path")
    A.log[:] = []
    A.later[:] = []
    A.queue[:] = []
    clear_players()
    place(WA, KA, ISL1)
    A.where[KA] = WA
    A.home_ret = -2
    Task(5, JString(WA), uA).run()
    A.drain()
    K.check(len(A.later) == 1 and A.later[0][1] == 1000 and int(A.later[0][0].mode) == 5 and int(A.later[0][0].fl) == 1 and str(A.later[0][0].wn) == WA,
            "DEATH spawn not ready on the own island -> ONE retry in 1 s (mode 5, the death world)")
    r1, _ms = A.later.pop(0)
    r1.run()
    A.drain()
    K.check(not A.later and len(A.kinds("home")) == 2 and not A.kinds("hub") and not A.kinds("say"),
            "DEATH ... the retry still not ready -> gives up silently (no third try, no chat line, no hub)")
    A.home_ret = 2
    A.log[:] = []
    Task(5, JString(WA), uA).run()
    A.drain()
    K.check(not A.later and A.kinds("home") == [("home", WA, KA, KA, WA)], "DEATH ... ready at once -> no retry")
    # review fix 2: at +0.8 s the engine is still moving the player (worldOf names a world they are not in) -> once more 1 s later
    A.log[:] = []
    clear_players()
    A.where[KA] = WA                      # still named the island, but the player is in transit (in no world)
    Task(5, JString(WA), uA).run()
    A.drain()
    K.check(len(A.later) == 1 and not A.kinds("home"), "DEATH not in the named world yet (-1) -> ONE retry in 1 s")
    place("hub", KA, (-295.0, 123.0, 72.6))  # arrived at the default world's spawn (= the hub)
    A.where[KA] = "hub"
    A.later.pop(0)[0].run()
    A.drain()
    K.check(not A.later and A.kinds("home") == [("home", "hub", KA, KA, WA)], "DEATH ... the retry finds them in the hub -> routed to the island")
    A.log[:] = []
    clear_players()
    A.where[KA] = WA
    Task(5, JString(WA), uA).run()
    A.drain()
    A.later.pop(0)[0].run()
    A.drain()
    K.check(not A.later and not A.kinds("home") and not A.kinds("hub"), "DEATH ... still nowhere on the retry -> gives up silently")

    # ---------------------------------------------------------------- BED
    L, L14 = m.S3_L, m14.S3_L
    bed = tuple(m.S3_BED)
    K.check(set(L) - set(L14) == {bed} and all(L[k] == L14[k] for k in L14) and L[bed] == "Furniture_Human_Ruins_Bed",
            "BED the 0.5.15 layout = 0.5.14 + exactly the ruins bed at %s" % (bed,))
    K.check(all(c not in L14 for c in m.S3_BED_CELLS) and all(L14.get(g) == "Soil_Grass" for g in m.S3_BED_GROUND)
            and all((bed[0] - 1, bed[1], bed[2] + dz) in L14 for dz in range(3)), "BED its 12 cells are empty, the 6 under it grass, the old wall beside it")
    K.check(list(Life.BEDP) == list(bed) and len(list(Life.BED_CELLS)) == 36 and len(list(Life.BED_GROUND)) == 18 and str(Life.BED_ID) == L[bed],
            "BED IsleLife constants = the layout")
    with zipfile.ZipFile(jar) as zj:
        K.check(any(n_.startswith("com/skyy/islands/StarterIsles") for n_ in zj.namelist()), "BED the layout ships in StarterIsles")
    K.eq(int(P("StarterIsles").BLOCKS), len(L), "BED StarterIsles.BLOCKS = the layout's block count (+1)")
    Life.ST.clear()
    clear_players()
    A.log[:] = []
    # an existing 3-island island (0.5.14 layout: no bed) - placed once (island C already got it during the boss checks: start it afresh)
    K.eq(fread(KC).get("bed.placed"), "1", "BED (island C got its bed on the first visit during the boss checks)")
    wfile(KC, dict((k_, v_) for k_, v_ in fread(KC).items() if k_ != "bed.placed"))
    St.reloadOne(KC)
    A.w[WC] = World(L14)
    wc = A.w[WC]
    place(WC, KC, ISL1)
    tick(WC)
    bset = lambda wn: [e for e in A.kinds("set") if e[1] == wn and e[2] in [tuple(c_) for c_ in m.S3_BED_CELLS]]
    K.check(bset(WC) == [("set", WC, bed, "Furniture_Human_Ruins_Bed")] and fread(KC).get("bed.placed") == "1"
            and ("relight", WC) in A.log, "BED an existing island gets the old bed once (12 cells air, grass under); bed.placed=1")
    wc.blocks.pop(bed)                     # the player breaks it - never put back
    A.t += 5000
    tick(WC)
    Life.ST.clear()
    tick(WC)
    K.eq(len(bset(WC)), 1, "BED never placed again (broken by the player, after a restart too)")
    # a player's block in one of the cells -> skip
    WX = "skyy-island-" + KN
    wfile(KN, {"v": "5", "world": WX, "isles": "3"})
    St.reloadOne(KN)
    St.loadIslandWorlds()
    A.w[WX] = World(L14)
    cell = m.S3_BED_CELLS[7]
    A.w[WX].blocks[cell] = "Wood_Oak_Planks"
    place(WX, KN, ISL1)
    tick(WX)
    K.check(not bset(WX) and fread(KN).get("bed.placed") == "skip" and A.w[WX].blocks[cell] == "Wood_Oak_Planks",
            "BED a player's block in a bed cell -> never placed (bed.placed=skip), the block stays")
    # ground changed -> skip; a cell not loaded -> later
    WY = "skyy-island-" + KE
    wfile(KE, {"v": "5", "world": WY, "isles": "3"})
    St.reloadOne(KE)
    St.loadIslandWorlds()
    A.w[WY] = World(L14)
    A.w[WY].unloaded.add(m.S3_BED_CELLS[3])
    place(WY, KE, ISL1)
    tick(WY)
    K.check(not bset(WY) and "bed.placed" not in fread(KE), "BED a cell not loaded -> nothing, nothing remembered (later)")
    A.w[WY].unloaded.clear()
    A.w[WY].blocks[m.S3_BED_GROUND[2]] = "Wood_Oak_Planks"
    A.t += 1000
    tick(WY)
    K.check(not bset(WY) and fread(KE).get("bed.placed") == "skip", "BED a player's block under it -> never (skip)")
    # a new island (the layout has the bed) -> only remembered
    clear_players()
    place(WD, KD, ISL1)
    Life.ST.clear()
    tick(WD)
    K.check(not bset(WD) and fread(KD).get("bed.placed") == "1", "BED a new / reset island (bed in the layout) -> only remembered")
    # a classic island -> nothing (the 3-island probe fails, no file key)
    WZ = "skyy-island-classic"
    kz = "00000000-0000-4000-8000-0000000c1a55"
    wfile(kz, {"v": "5", "world": WZ})
    St.reloadOne(kz)
    St.loadIslandWorlds()
    A.w[WZ] = World({(x, 128, z): "Soil_Grass" for x in range(-3, 4) for z in range(-3, 4)})
    place(WZ, kz, (0.5, 129.0, 0.5))
    for _ in range(2):
        A.t += 61000
        tick(WZ)
    K.check(not bset(WZ) and "bed.placed" not in fread(kz), "BED a classic island -> no bed")
    tw = code("IsleLife", "tickWorld")
    K.check(0 <= tw.find("IsleLife.three") < tw.find("IsleLife.bedOnce"), "BED shape: only 3-island islands (after the three() probe)")
    # reset clears boss.done + bed.placed
    wfile(KC, dict(list(fread(KC).items()) + [("boss.done", "1")]))
    St.reloadOne(KC)
    St.RESETTING.put(JString(KC), JArray(JObject)([JString("reset"), JInt(1)]))
    K.eq(int(St.setWorldName0(JString(KC), JString(WC + "-r1"))), 1, "RESET setWorldName0 with a pending reset -> 1")
    fc = fread(KC)
    K.check("boss.done" not in fc and "bed.placed" not in fc and "camp.done" not in fc, "RESET /island reset clears boss.done / bed.placed")
    Life.API = None
    K.save()


if __name__ == "__main__":
    print("S. real-server phase: NOT RUN in this harness (tools/smoke_test.py) - the bed's fillers / facing UNVERIFIED in game")
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("p15", run_p15)], script=__file__)
