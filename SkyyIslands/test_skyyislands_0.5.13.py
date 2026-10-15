"""Harness for SkyyIslands 0.5.13 (island time = hub time, the frameless hub portal facing the doorway, the camp stops after the quest, start
on your island; tools/islands_0_5_13_patch.py) on top of the 0.5.12 harness. Build first:
python tools/islands_0_5_13_patch.py && python SkyyIslands/build_skyyislands_0.5.13.py

    python SkyyIslands/test_skyyislands_0.5.13.py [--dir <folder inside tools/dev/scratch/>] [--keep]

  P13   EXECUTED on stand-in worlds (IsleLife.API = a Python IsleApi with world clocks, block rotations and quest state; real IslandStore
        files in scratch, real config kit rows, -Xverify:all):
        LAYOUT  0.5.13 layout = 0.5.12 minus exactly the 13 frame cells (S3_FRAME), the socket kept; FRAME = those 13 + 0.5.12's 3 top cells
        PORTAL  rotFor (pad / socket = 1), IsleEng.setBlock passes rotFor(id) + "" = BlockType.EMPTY; an OLD island (0.5.12 layout, frame
                standing) keeps its frame until repaired; the repair clears only frame cells still holding the generator's id (a player's
                block in a frame cell and next to it stay), no top filled in, portal=1 + portal.frame=gone, island:portal still fires;
                an already-repaired 0.5.12 island (pad rotation 0, frame + filled top) -> pad turned once + frame cleared on the next visit;
                a frameless island with 2 player blocks in frame cells -> untouched; an unloaded frame cell -> retried; reset clears the keys
        CAMP    quest unknown (no SkyyQuests / owner offline) -> spawns as before; quest not done -> spawns; done -> no new skeletons,
                camp.done=1 saved, asked at most every 10 s, the file answers after a restart, the living ones are left alone; setting off
        TIME    timeAll -> one hub task (never two queued), 5 s per world, the hub's clock handed to each world's task; syncTime table:
                behind -> forward to the hub, within 60 game-s -> nothing, ahead 8 h (bed) -> held (paused, time.held=1) then released
                when the hub catches up, ahead 20 h -> forward to the hub's time of day, days ahead + same time -> nothing, bed skip
                running -> nothing, hub paused -> mirrored, shard worlds never paused, setting off -> release (also after a restart via
                time.held), a 500-step random walk never moves a clock backwards; engine shapes (WorldTimeResource.setGameTime, the pause)
        LOGIN   RouteTask.decide table (own / co-op island, another island, hub, shard, zone; Hub on login switch; setting off; no
                island), hubPref (settings:fn:get TRUE only), run() shape (decide -> IslandCmd.go / HubCmd.sendToHub), first ready only,
                the switch's default is now off
        CFG     3 new config lines + Server Setup rows (fresh / 0.5.12 file / hand edits)
  P2    the 0.5.12 part-2 phase on the 0.5.13 jar (its stand-in gets neutral answers for the 7 new engine calls); the ONE check that tested
        the dropped top-filling on repair is replaced by the P13 PORTAL checks
  S3 / MOUTH  the 0.5.10 + 0.5.11 layout checks on the 0.5.13 jar (the 0.5.10 design check sees the frame cells put back - they are the
        only layout change; the jar's data = the 0.5.13 layout block for block)
  A / C / AA  verify, class compare 0.5.12 -> 0.5.13, engine-access audit
  SND, X, D   the 0.5.9 / 0.5.8 / 0.5.12 phases on the 0.5.13 jar
  The REAL server phase is NOT RUN here - UNVERIFIED in game.
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util, random, types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "islands0513", "h")]
if "--no-server" not in sys.argv and "--phase" not in sys.argv:
    sys.argv.append("--no-server")
import skyybuild as B
import harness_kit as HK
import soundpass_kit as SK
import jpype

VERSION = "0.5.13"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-0.5.12.jar")
if "--jar" not in sys.argv:
    sys.argv += ["--jar", JAR]          # the 0.5.12 harness module reads --jar at import

_spec = importlib.util.spec_from_file_location("test_skyyislands_0_5_12", os.path.join(HERE, "test_skyyislands_0.5.12.py"))
T512 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T512)
T511, T510, T59, T58 = T512.T511, T512.T510, T512.T59, T512.T58
T512.VERSION = VERSION                  # its phases load the 0.5.13 layout / generated script
T512.JAR = T511.JAR = T510.JAR = JAR
SCRATCH = T510.SCRATCH
PKG = T510.PKG
HK.run_compare = T512._orig_compare     # 0.5.12's own compare wrapper expects the 0.5.11 -> 0.5.12 files; ours is below

EXPECT = {
    "IslandCfg": ["+f SYNC_TIME", "+f ISLAND_LOGIN", "+f CAMP_STOP", "~<clinit>", "~m load"],
    "IslandStore": ["~m setWorldName0"],
    "IsleApi": ["+m rot", "+m gameTime", "+m timeFlags", "+m setGameTime", "+m setTimePaused", "+m timeWorlds", "+m questDone"],
    "IsleState": ["+f campDone", "+f questAt", "+f rotOk", "+f frameDone"],
    "IsleEng": ["+m rotFor", "~m setBlock", "+m rot", "+m gameTime", "+m timeFlags", "+m setGameTime", "+m setTimePaused", "+m timeWorlds",
                "+m questDone"],
    "IsleTask": ["+f ms", "+f fl", "~m run"],
    "IsleLife": ["+f FRAME", "+f FRAME_IDS", "+f FRAME_NEED", "+f QUEST_TASK", "+f TIME_AT", "+f HELD", "+f HUBQ", "+f TIME_GAP", "+f TIME_TOL",
                 "+f TIME_HOLD", "+f DAY_MS", "+f SYNCS", "+f FRAMES", "~<clinit>", "+m campDone", "~m campTick", "+m padTurn", "+m frameClear", "+m releaseHeld",
                 "~m portalBlocks", "~m repair", "+m markHeld", "+m heldFile", "+m release", "+m syncTime", "+m timeHub", "+m timeAll", "~m tickAll"],
    "RouteTask": ["+f HOME", "+m keep", "+m decide", "+m hubPref", "~m run", "+<clinit>"],
    "SkyyIslandsPlugin": ["~m setup"],
    "CfgFile": ["~<clinit>"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],                                  # the version string
    "FillTask": ["~m run"],                                    # the layout's block count 12710 -> 12697 (13 frame blocks fewer)
    "StarterIsles": ["~<clinit>", "~m decode", "~m fill"],     # the layout data (no frame)
}
ADDED = []
CHANGED_FILES = ["Server/Item/Items/SkyyIslands/Skyy_Island_Portal_Socket.json", "manifest.json"]
# the 0.5.12 p2 check that tested what 0.5.13 deliberately drops (the frame's top filled in on repair) - replaced by P13 PORTAL
P2_REPLACED = ["PORTAL the frame's broken top filled in - only empty cells (the player's plank stays)"]
KA, KB, KT, KV, KN, KC = T512.KA, T512.KB, T512.KT, T512.KV, T512.KN, T512.KC
WA, WC = T512.WA, T512.WC
WO = "skyy-island-" + KN          # an OLD island (0.5.12 layout, frame standing)
WS = "skyy-shard-" + KA


def run_compare(out, jar, old_jar, pkg, expect, added):
    """the kit's compare, then its non-class check replaced by the exact 0.5.13 expectation: the socket's item file + the manifest"""
    T512._orig_compare(out, jar, old_jar, pkg, expect, added)
    d = json.load(open(out))
    d["fails"] = [f for f in d["fails"] if not f.startswith("C: non-class entries changed")]
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    na, nb = set(n_ for n_ in za.namelist() if not n_.endswith(".class")), set(n_ for n_ in zb.namelist() if not n_.endswith(".class"))
    if na != nb:
        d["fails"].append("C: non-class entries added %s / removed %s" % (sorted(nb - na), sorted(na - nb)))
    changed = sorted(n_ for n_ in na & nb if za.read(n_) != zb.read(n_))
    if changed != CHANGED_FILES:
        d["fails"].append("C: changed non-class entries %s, want %s" % (changed, CHANGED_FILES))
    ma, mb = json.loads(za.read("manifest.json")), json.loads(zb.read("manifest.json"))
    for m_, v_ in ((ma, "0.5.12"), (mb, VERSION)):
        if m_.pop("Version", None) != v_ or m_.pop("Name", None) != v_ + " SkyyIslands":
            d["fails"].append("C: manifest Version / Name are not %s" % v_)
    if ma != mb:
        d["fails"].append("C: manifest changed beyond Version / Name")
    so, sn = json.loads(za.read(CHANGED_FILES[0])), json.loads(zb.read(CHANGED_FILES[0]))
    bt = sn["BlockType"]
    ok = (bt["CustomModel"] == "Blocks/Miscellaneous/Platform_MagicInactive.blockymodel" and "Particles" not in bt and "AmbientSoundEventId" not in bt
          and "CustomModelAnimation" not in bt and bt["VariantRotation"] == "NESW" and bt["Gathering"]["Breaking"]["GatherType"] == "Unbreakable"
          and bt["InteractionHint"] == so["BlockType"]["InteractionHint"] and bt["Interactions"] == so["BlockType"]["Interactions"])
    if not ok:
        d["fails"].append("C: the socket is not the dormant pad (model, no swirl / sound / animation, NESW, unbreakable, same F use)")
    d["ok"] += 2
    d["notes"] = d.get("notes", []) + ["C: non-class: manifest (Version / Name) + the socket's item file (the dormant pad)"]
    json.dump(d, open(out, "w"), indent=1)


HK.run_compare = run_compare


# ---------------------------------------------------------------------------------------------------------------- the 0.5.12 p2 phase
_JIMPL = jpype.JImplements
_NEW_API = {"rot": lambda self, wn, x, y, z: -1, "gameTime": lambda self, wn: jpype.JLong(-(2 ** 63)), "timeFlags": lambda self, wn: -1,
            "setGameTime": lambda self, wn, ms: False, "setTimePaused": lambda self, wn, p: False,
            "timeWorlds": lambda self: jpype.JClass("java.util.HashSet")(), "questDone": lambda self, owner, task: -1}


def _jimpl(*ifaces, **kw):
    """JImplements for the 0.5.12 stand-in: the 7 new IsleApi calls answer 'unknown' (= the 0.5.12 behaviour) so its checks still run"""
    dec = _JIMPL(*ifaces, **kw)

    def wrap(cls):
        if (PKG + "IsleApi") in [str(i) for i in ifaces]:
            for k_, f_ in _NEW_API.items():
                if not hasattr(cls, k_):
                    setattr(cls, k_, jpype.JOverride(f_))
        return dec(cls)
    return wrap


def run_p2(out, jar, scratch, home):
    jpype.JImplements = _jimpl
    try:
        T512.run_p2(out, jar, scratch, home)
    finally:
        jpype.JImplements = _JIMPL
    d = json.load(open(out))
    gone = [f for f in d["fails"] if any(f.startswith(r) for r in P2_REPLACED)]
    d["fails"] = [f for f in d["fails"] if f not in gone]
    d["notes"] = d.get("notes", []) + ["P2: replaced by P13 PORTAL (0.5.13 drops the top filling): %s" % gone]
    json.dump(d, open(out, "w"), indent=1)


# ---------------------------------------------------------------------------------------------------------------- S3: layout checks
def _with_frame(m):
    """the 0.5.13 layout with the old frame put back (and the dirt 0.5.12 put under it) = the 0.5.12 layout (P13 LAYOUT proves it)"""
    n = types.SimpleNamespace(**dict((k, getattr(m, k)) for k in dir(m) if k.startswith("S3_")))
    n.S3_L = dict(m.S3_L)
    for x, y, z, b in m.S3_FRAME:
        n.S3_L[(x, y, z)] = b
        if n.S3_L.get((x, y - 1, z)) == "Soil_Grass":
            n.S3_L[(x, y - 1, z)] = "Soil_Dirt"
    return n


def run_s3m(out, jar, scratch, home):
    """the 0.5.10 design + 0.5.11 mouth checks see the frame put back (the only layout change); the jar's data check uses the real layout"""
    od, om = T510.design_checks, T511.mouth_checks
    T510.design_checks = lambda K, m: od(K, _with_frame(m))
    T511.mouth_checks = lambda K, m, old: om(K, _with_frame(m), old)
    try:
        T512.run_s3m(out, jar, scratch, home)
    finally:
        T510.design_checks, T511.mouth_checks = od, om


# ---------------------------------------------------------------------------------------------------------------- P13
def run_p13(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject, JString, JDouble, JInt, JLong, JBoolean
    K = HK.Child(out)
    m = T511.layout_of(VERSION)
    m12 = T511.layout_of("0.5.12")
    P2 = m.S3_P2
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    P = lambda n: JClass(PKG + n)
    St, Cfg, Life, Task, Eng, Route, Rows = P("IslandStore"), P("IslandCfg"), P("IsleLife"), P("IsleTask"), P("IsleEng"), P("RouteTask"), P("CfgRows")
    Paths, UUID, Double, HashSet, Function = (JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Double"),
                                              JClass("java.util.HashSet"), "java.util.function.Function")
    uA, uB, uT, uV, uN, uC = [UUID.fromString(k) for k in (KA, KB, KT, KV, KN, KC)]
    import shutil
    shutil.rmtree(os.path.join(scratch, "p13"), ignore_errors=True)
    home = os.path.join(scratch, "p13", "Skyy_SkyyIslands")
    isl = os.path.join(home, "islands")
    os.makedirs(isl, exist_ok=True)

    # ---------------------------------------------------------------- CFG
    cf = os.path.join(home, "config.properties")
    Cfg.FILE = Paths.get(cf)
    Cfg.load("")
    txt = open(cf, encoding="utf-8").read()
    new_lines = ["islands.syncTime=true", "islands.islandOnLogin=true", "camp.stopAfterQuest=true"]
    K.check(all(l in txt.splitlines() for l in new_lines), "CFG a fresh config.properties lists the 3 new lines")
    cur = lambda: (bool(Cfg.SYNC_TIME), bool(Cfg.ISLAND_LOGIN), bool(Cfg.CAMP_STOP))
    K.eq(cur(), (True, True, True), "CFG defaults on")
    old = "\n".join(l for l in txt.splitlines() if l not in new_lines and "0.5.13" not in l) + "\n"
    open(cf, "w", encoding="utf-8").write(old)
    Cfg.SYNC_TIME = False
    Cfg.load("")
    K.check(cur() == (True, True, True) and open(cf, encoding="utf-8").read() == old, "CFG a 0.5.12 file without the lines = defaults, not rewritten")
    open(cf, "w", encoding="utf-8").write(old + "islands.syncTime=false\nislands.islandOnLogin=FALSE\ncamp.stopAfterQuest=false\n")
    Cfg.load("")
    K.eq(cur(), (False, False, False), "CFG hand edits read")
    open(cf, "w", encoding="utf-8").write(txt)
    Cfg.load("")
    rows = SK.kit_rows(Rows)
    want = {"islands.syncTime": ("hub", "bool", "true"), "islands.islandOnLogin": ("hub", "bool", "true"), "camp.stopAfterQuest": ("isles", "bool", "true")}
    K.check(all(k in rows and tuple(rows[k][2:5]) == v and "live" in rows[k][9] for k, v in want.items()),
            "ROW the 3 Server Setup rows (Hub / Starter islands), live, default on: %s" % [(k, rows.get(k, [None] * 5)[2:5]) for k in want])

    # ---------------------------------------------------------------- LAYOUT
    L, L12 = m.S3_L, m12.S3_L
    gone = sorted(set(L12) - set(L))
    under = sorted(k for k in L if L[k] != L12[k])          # 0.5.12 turned grass under the frame into dirt (vanilla grass under a block)
    K.check(sorted(m.S3_FRAME) == sorted((k[0], k[1], k[2], L12[k]) for k in gone) and len(gone) == 13 and not (set(L) - set(L12))
            and all((k[0], k[1] + 1, k[2]) in gone and L[k] == "Soil_Grass" and L12[k] == "Soil_Dirt" for k in under),
            "LAYOUT 0.5.13 = 0.5.12 minus exactly the 13 frame cells (+ the grass under them stays grass): %d gone, %d grass" % (len(gone), len(under)))
    K.check(L.get(tuple(P2["socket"])) == "Rock_Stone_Brick_Smooth", "LAYOUT the socket stays (the portal's own base)")
    fr = list(Life.FRAME)
    fids = [str(x) for x in Life.FRAME_IDS]
    K.check(len(fr) == 48 and [tuple(fr[i:i + 3]) for i in range(0, 48, 3)] == [tuple(c[:3]) for c in P2["frame"]] and fids == [c[3] for c in P2["frame"]]
            and fids[13:] == [f[3] for f in P2["fix"]] and int(Life.FRAME_NEED) == 6, "LAYOUT FRAME = the 13 frame cells + 0.5.12's 3 top cells (16), need 6")

    # ---------------------------------------------------------------- island files + the stand-in engine
    def wfile(k, props):
        with open(os.path.join(isl, k + ".properties"), "w", encoding="utf-8") as f:
            f.write("".join("%s=%s\n" % kv for kv in props.items()))

    def fread(k):
        p = os.path.join(isl, k + ".properties")
        return dict(l.split("=", 1) for l in open(p, encoding="utf-8").read().splitlines() if "=" in l and not l.startswith("#"))
    wfile(KA, {"v": "5", "world": WA, "members": KB, "trusted": KT, "isles": "3"})
    wfile(KN, {"v": "5", "world": WO, "isles": "3"})
    wfile(KC, {"v": "5", "world": WC, "isles": "3"})
    St.DIR = Paths.get(isl)
    St.IO = None
    St.STOPPING = False
    St.SETTINGS.clear()
    St.loadIslandWorlds()
    K.check(bool(St.isIslandWorld(WA)) and bool(St.isIslandWorld(WO)) and St.ownerOf(WS) is None, "SETUP islands A, N (old), C; the shard has no owner")

    class World(object):
        def __init__(self, blocks):
            self.blocks, self.rot, self.players, self.npcs, self.unloaded = dict(blocks), {}, {}, {}, set()
            self.clock, self.flags = 0, 0

    class Api(object):
        def __init__(self):
            self.t = 5000000
            self.w = {WA: World(L), WO: World(L12), WC: World(L), WS: World({}), "hub": World({})}
            self.inv, self.admins, self.quest = {}, set(), {}
            self.log, self.queue, self.msgs, self.n = [], [], [], 0

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
            w.rot[k] = int(Eng.rotFor(JString(str(bid))))      # what the real IsleEng.setBlock places it with
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
            A.msgs.append((str(u), str(text)))

        @JOverride
        def name(self, u):
            return JString("P" + str(u)[-4:])

        @JOverride
        def toHub(self, wn, u):
            A.ev("hub", str(wn), str(u))
            return True

        @JOverride
        def hasBed(self, u, inWorld):
            return False

        @JOverride
        def goHome(self, wn, u, hk, homew):
            return JInt(2)

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
            return str(u) in A.admins

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
            w = A.w.get(str(wn))
            k = (int(x), int(y), int(z))
            if w is None or k in w.unloaded or k not in w.blocks:
                return -1
            return w.rot.get(k, 0)

        @JOverride
        def gameTime(self, wn):
            w = A.w.get(str(wn))
            return JLong(-(2 ** 63) if w is None else w.clock)

        @JOverride
        def timeFlags(self, wn):
            w = A.w.get(str(wn))
            return -1 if w is None else w.flags

        @JOverride
        def setGameTime(self, wn, ms):
            w = A.w[str(wn)]
            A.ev("time", str(wn), w.clock, int(ms))
            w.clock = int(ms)
            return True

        @JOverride
        def setTimePaused(self, wn, p):
            w = A.w[str(wn)]
            if bool(w.flags & 1) == bool(p):
                return False
            w.flags = (w.flags | 1) if p else (w.flags & ~1)
            A.ev("pause", str(wn), bool(p))
            return True

        @JOverride
        def timeWorlds(self):
            s_ = HashSet()
            for k, w in A.w.items():
                if w.players and (k.startswith("skyy-island-") or k.startswith("skyy-shard-")):
                    s_.add(JString(k))
            return s_

        @JOverride
        def questDone(self, owner, task):
            A.ev("ask", str(owner), str(task))
            return int(A.quest.get(str(owner), -1))
    Life.API = Stand()
    Life.ST.clear()
    Life.loadGot(Paths.get(os.path.join(home, "hubshards.properties")))
    ISL1, ISL2 = (8.5, 129.0, 8.5), (46.5, 128.0, 14.5)
    SOCK = tuple(P2["socket"])
    PAD, SOCKET = "Skyy_Island_Hub_Portal", "Skyy_Island_Portal_Socket"
    FR = [tuple(c[:3]) for c in P2["frame"]]
    FRID = dict((tuple(c[:3]), c[3]) for c in P2["frame"])

    def tick(wn):
        return int(Life.tickWorld(JString(wn)))

    def clear_players():
        for w in A.w.values():
            w.players.clear()

    # ---------------------------------------------------------------- PORTAL
    K.eq([int(Eng.rotFor(JString(x))) for x in (PAD, SOCKET, "Rock_Stone", "")], [1, 1, 0, 0], "PORTAL rotFor: pad + socket = 1 (yaw 90), others 0")
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
    sb = code("IsleEng", "setBlock")
    K.check("IsleEng.rotFor" in sb and "BlockType.EMPTY" in sb and 0 <= sb.find("IsleEng.rotFor") < sb.find("BlockOperations.setBlock"),
            "PORTAL IsleEng.setBlock: rotation = rotFor(id) passed to BlockOperations.setBlock; \"\" = BlockType.EMPTY (air)")
    K.check("BlockSection.getRotationIndex" in code("IsleEng", "rot"), "PORTAL IsleEng.rot reads BlockSection.getRotationIndex")
    # an OLD island (0.5.12 layout: the frame stands) - a player's blocks: one frame cell rebuilt in planks, a brick beside the frame
    WOw = A.w[WO]
    f0 = FR[0]
    WOw.blocks[f0] = "Wood_Oak_Planks"
    beside = (SOCK[0] - 1, SOCK[1], SOCK[2] - 2)
    WOw.blocks[beside] = "Rock_Stone_Brick"
    place_ = lambda wn, k, pos: A.w[wn].players.__setitem__(k, list(pos))
    place_(WO, KN, (79.5, 134.0, 42.5))
    tick(WO)
    K.check(WOw.blocks.get(SOCK) == SOCKET and all(WOw.blocks.get(c) == FRID[c] for c in FR[1:13]),
            "PORTAL an unrepaired old island: the socket goes in, the frame stays (only a repair removes it)")
    K.eq(WOw.rot.get(SOCK), 1, "PORTAL the socket placed with rotation 1")
    A.inv[KN] = {"Skyy_Hub_Shard": 1}
    A.t += 5000
    nq = len(A.kinds("quest"))
    K.eq(str(Life.useSocket(JString(WO), uN, JLong(A.t))), "repaired", "PORTAL the owner repairs the old island's portal")
    K.check(WOw.blocks.get(SOCK) == PAD and WOw.rot.get(SOCK) == 1, "PORTAL the pad stands in the socket with rotation 1 (faces the doorway)")
    K.check(all(c not in WOw.blocks for c in FR[1:13]) and WOw.blocks.get(f0) == "Wood_Oak_Planks" and WOw.blocks.get(beside) == "Rock_Stone_Brick",
            "PORTAL the frame's 12 generator blocks gone; the player's planks in a frame cell and the brick beside it stay")
    K.check(all(c not in WOw.blocks for c in FR[13:]), "PORTAL no broken top filled in (0.5.12's top filling is gone)")
    fo = fread(KN)
    K.check(fo.get("portal") == "1" and fo.get("portal.frame") == "gone", "PORTAL portal=1 + portal.frame=gone in the island file")
    K.check(("quest", KN, "island:portal") in A.kinds("quest")[nq:] and ("relight", WO) in A.log, "PORTAL island:portal still sent to SkyyQuests; light re-queued")
    nset = len(A.kinds("set"))
    A.t += 31000
    tick(WO)
    Life.ST.clear()
    A.t += 31000
    tick(WO)
    K.eq(len(A.kinds("set")), nset, "PORTAL later ticks / a restart: no more block changes (portal.frame=gone, pad already turned)")
    hubs0 = len(A.kinds("hub"))
    place_(WO, KN, (SOCK[0] + 0.5, SOCK[1] + 0.1, SOCK[2] + 0.5))
    A.t += 5000
    tick(WO)
    K.eq(len(A.kinds("hub")), hubs0 + 1, "PORTAL stepping onto the pad still sends to the hub")
    # an island repaired WITH 0.5.12: pad rotation 0, frame + filled top standing, no portal.frame key
    W2 = "skyy-island-" + KT
    wfile(KT, {"v": "5", "world": W2, "isles": "3", "portal": "1", "portal.at": "1", "portal.by": "X"})
    St.reloadOne(KT)
    St.loadIslandWorlds()
    A.w[W2] = World(L12)
    w2 = A.w[W2]
    for c in FR[13:]:
        w2.blocks[c] = FRID[c]
    w2.blocks[SOCK] = PAD
    w2.rot[SOCK] = 0
    clear_players()
    place_(W2, KT, ISL1)
    tick(W2)
    K.check(w2.blocks.get(SOCK) == PAD and w2.rot.get(SOCK) == 1 and [e[3] for e in A.kinds("set") if e[1] == W2 and e[2] == SOCK] == ["", PAD],
            "PORTAL a 0.5.12 pad (rotation 0) is turned once on the next visit (air, then the pad with rotation 1)")
    K.check(all(c not in w2.blocks for c in FR) and fread(KT).get("portal.frame") == "gone" and fread(KT).get("portal") == "1",
            "PORTAL a 0.5.12-repaired island: all 16 old frame blocks cleared on the next visit, portal=1 kept")
    # a frameless (0.5.13) island: 2 player blocks with frame ids in frame cells (< 6) -> untouched on repair
    WF = "skyy-island-" + KV
    wfile(KV, {"v": "5", "world": WF, "isles": "3"})
    St.reloadOne(KV)
    St.loadIslandWorlds()
    A.w[WF] = World(L)
    wf = A.w[WF]
    wf.blocks[FR[1]] = FRID[FR[1]]
    wf.blocks[FR[2]] = FRID[FR[2]]
    wf.unloaded.add(FR[7])
    clear_players()
    place_(WF, KV, ISL1)
    tick(WF)
    A.inv[KV] = {"Skyy_Hub_Shard": 1}
    A.t += 5000
    K.eq(str(Life.useSocket(JString(WF), uV, JLong(A.t))), "repaired", "PORTAL a new frameless island repaired")
    K.check("portal.frame" not in fread(KV) and wf.blocks.get(FR[1]) == FRID[FR[1]], "PORTAL a frame cell not loaded -> nothing cleared, nothing marked (later)")
    wf.unloaded.clear()
    Life.state(WF).blocksAt = 0
    A.t += 31000
    tick(WF)
    K.check(wf.blocks.get(FR[1]) == FRID[FR[1]] and wf.blocks.get(FR[2]) == FRID[FR[2]] and fread(KV).get("portal.frame") == "gone",
            "PORTAL a frameless island: 2 player blocks with frame ids in frame cells (< 6) stay; marked done")
    # reset clears the new keys
    wfile(KC, dict(list(fread(KC).items()) + [("portal.frame", "gone"), ("camp.done", "1"), ("time.held", "1")]))
    St.reloadOne(KC)
    St.RESETTING.put(JString(KC), JArray(JObject)([JString("reset"), JInt(1)]))
    K.eq(int(St.setWorldName0(JString(KC), JString(WC + "-r1"))), 1, "RESET setWorldName0 with a pending reset -> 1")
    fc = fread(KC)
    K.check(not [k for k in ("portal.frame", "camp.done", "time.held") if k in fc], "RESET /island reset clears portal.frame / camp.done / time.held")
    St.reloadOne(KC)

    # ---------------------------------------------------------------- CAMP: stops after the quest
    Life.ST.clear()
    clear_players()
    WAw = A.w[WA]
    place_(WA, KB, ISL2)        # a co-op member on island 2
    A.t += 1000
    tick(WA)
    sp1 = [e for e in A.kinds("spawn") if e[1] == WA]
    K.check(len(sp1) == 3 and A.kinds("ask")[-1:] == [("ask", KA, "tutorial.defeat_mobs")],
            "CAMP quest state unknown (no SkyyQuests / owner offline) -> 3 skeletons as before; the OWNER's task asked")
    for k in list(WAw.npcs):
        WAw.npcs[k][4] = False
    Life.state(WA).campNext = 0
    A.quest[KA] = 0
    A.t += 11000
    tick(WA)
    K.eq(len([e for e in A.kinds("spawn") if e[1] == WA]), 6, "CAMP the owner has not done Defeat 5 mobs -> the camp refills")
    A.quest[KA] = 1
    na = len(A.kinds("ask"))
    A.t += 3000
    for k in list(WAw.npcs)[3:4]:
        WAw.npcs[k][4] = False
    Life.state(WA).due.clear()
    tick(WA)
    K.check(len(A.kinds("ask")) == na, "CAMP asked at most every 10 s")
    A.t += 10000
    n0 = len([e for e in A.kinds("spawn") if e[1] == WA])
    for k in [k_ for k_, v_ in WAw.npcs.items() if v_[4]][:1]:
        WAw.npcs[k][4] = False            # one more dies - the camp would refill it
    Life.state(WA).due.clear()
    tick(WA)
    K.check(len([e for e in A.kinds("spawn") if e[1] == WA]) == n0 and fread(KA).get("camp.done") == "1",
            "CAMP done -> no new skeletons; camp.done=1 in the island file")
    alive = [k for k, v in WAw.npcs.items() if v[4]]
    K.check(len(alive) == 2, "CAMP the skeletons still alive are left alone (no despawn, nothing lost): %d" % len(alive))
    Life.ST.clear()
    A.quest.pop(KA)
    na = len(A.kinds("ask"))
    for k in alive:
        WAw.npcs[k][4] = False
    A.t += 61000
    tick(WA)
    K.check(len([e for e in A.kinds("spawn") if e[1] == WA]) == n0 and len(A.kinds("ask")) == na, "CAMP after a restart the island file answers (no ask, no spawn)")
    Cfg.CAMP_STOP = False
    Life.state(WA).campNext = 0
    A.t += 61000
    tick(WA)
    K.check(len([e for e in A.kinds("spawn") if e[1] == WA]) == n0 + 3, "CAMP camp.stopAfterQuest off -> the camp as before")
    Cfg.CAMP_STOP = True
    K.check(0 <= code("IsleLife", "campTick").find("IslandCfg.CAMP_STOP") < code("IsleLife", "campTick").find("IsleLife.campDone") < code("IsleLife", "campTick").find("IsleApi.spawn"),
            "CAMP shape: campTick checks the setting + campDone before any spawn")
    qd = code("IsleEng", "questDone")
    K.check(all(x in qd for x in ('"quest:fn:done"', "IslandStore.ownerUuid", "IslandStore.online", "IslandStore.pkey")), "CAMP shape: questDone = quest:fn:done, owner online on that profile")

    # ---------------------------------------------------------------- TIME
    DAY, H = 86400000, 3600000
    hub = A.w["hub"]
    T0 = -62135596800000 + 27 * DAY + 9 * H          # Day 28, 09:00
    hub.clock = T0
    clear_players()
    A.queue[:] = []
    Life.TIME_AT.clear()
    Life.HELD.clear()
    Life.HUBQ = 0
    A.w[WA].clock = -62135596800000 + 9 * H         # Day 1 09:00 (a new island)
    A.w[WS].clock = T0 - 5 * H
    place_(WA, KA, ISL1)
    place_(WS, KB, ISL1)
    hub.players[KC] = [0.0, 0.0, 0.0]
    K.eq(int(Life.timeAll(JLong(A.t))), 2, "TIME timeAll: 2 worlds due (island + shard; not the hub) -> one hub task")
    K.check(len(A.queue) == 1 and int(A.queue[0].mode) == 12 and str(A.queue[0].wn) == "hub", "TIME the hub task runs on the hub's thread")
    K.eq(int(Life.timeAll(JLong(A.t + 1000))), 0, "TIME never a second hub task while one is queued / within 5 s per world")
    A.queue.pop(0).run()
    K.check(len(A.queue) == 2 and all(int(t.mode) == 10 and int(t.ms) == T0 and int(t.fl) == 0 for t in A.queue), "TIME the hub's clock handed to each world's own task")
    A.drain()
    K.check(A.w[WA].clock == T0 and A.w[WS].clock == T0, "TIME a world behind the hub (Day 1 vs Day 28) jumps FORWARD to the hub's day + time")
    K.eq(int(Life.timeAll(JLong(A.t + 4000))), 0, "TIME nothing due within 5 s")
    K.eq(int(Life.timeAll(JLong(A.t + 5000))), 2, "TIME 5 s later due again")
    A.queue[:] = []
    Life.HUBQ = 0

    def sync(wn, i, h, f=0, hf=0):
        A.w[wn].clock, A.w[wn].flags = i, f
        n0_ = len(A.log)
        r = int(Life.syncTime(JString(wn), JLong(h), JInt(hf)))
        return r, A.w[wn].clock, A.w[wn].flags, A.log[n0_:]
    r = sync(WA, T0 + 30000, T0)
    K.check(r[0] == 0 and r[1] == T0 + 30000 and not r[3], "TIME within 60 game-seconds -> nothing: %r" % (r,))
    r = sync(WA, T0 + 8 * H, T0)
    K.check(r[1] == T0 + 8 * H and r[2] & 1 and "1" == fread(KA).get("time.held") and Life.HELD.containsKey(WA),
            "TIME ahead 8 h (a bed skipped the night) -> HELD: paused, never set back; time.held=1")
    r = sync(WA, T0 + 8 * H, T0 + 4 * H, f=1)
    K.check(r[1] == T0 + 8 * H and r[2] & 1 and not [e for e in r[3] if e[0] == "time"], "TIME still ahead -> stays paused, clock untouched")
    r = sync(WA, T0 + 8 * H, T0 + 8 * H - 20000, f=1)
    K.check(not (r[2] & 1) and r[1] == T0 + 8 * H and fread(KA).get("time.held") == "0" and not Life.HELD.containsKey(WA),
            "TIME the hub caught up -> unpaused, released (time.held=0): %r %r" % (r, fread(KA).get("time.held")))
    r = sync(WA, T0 + 20 * H, T0)
    K.check(r[1] == T0 + DAY and (r[1] - T0) % DAY == 0 and not (r[2] & 1), "TIME ahead 20 h (> 12 h) -> FORWARD to the hub's next same time of day")
    r = sync(WA, T0 + 3 * DAY + 10000, T0)
    K.check(r[0] == 0 and not r[3], "TIME whole days ahead at the same time of day -> nothing")
    r = sync(WA, T0 + 3 * DAY + 2 * H, T0)
    K.check(r[2] & 1 and r[1] == T0 + 3 * DAY + 2 * H, "TIME days ahead + 2 h -> held")
    r = sync(WA, T0 - 5 * DAY, T0, f=2)
    K.check(r[0] == 0 and not r[3], "TIME a bed skip running on the island -> left alone")
    r = sync(WA, T0 - H, T0, f=0, hf=1)
    K.check(r[1] == T0 and r[2] & 1, "TIME the hub's clock paused -> mirrored on the island (time set + paused)")
    r = sync(WA, T0, T0, f=1, hf=0)
    K.check(not (r[2] & 1), "TIME the hub resumes -> the island resumes")
    A.w[WA].flags = 0
    r = sync(WS, T0 + 8 * H, T0)
    K.check(r[1] == T0 + DAY and not (r[2] & 1) and not [e for e in r[3] if e[0] == "pause"], "TIME a SHARD world ahead -> forward to the hub's time of day, never paused")
    r = sync(WS, T0 - 2 * H, T0, hf=1)
    K.check(r[0] == 0 and r[1] == T0 - 2 * H, "TIME hub paused -> a shard world is left alone")
    r = sync(WS, T0 - 2 * H, T0)
    K.check(r[1] == T0, "TIME a shard world behind -> forward")
    # the setting off: release what we paused (also after a restart, via time.held)
    sync(WA, T0 + 8 * H, T0)
    K.check(A.w[WA].flags & 1, "TIME (set-up) island held")
    Cfg.SYNC_TIME = False
    r = sync(WA, T0 + 8 * H, T0, f=1)
    K.check(not (r[2] & 1) and r[1] == T0 + 8 * H and fread(KA).get("time.held") == "0", "TIME setting off -> the held island is unpaused, nothing set")
    A.w[WC].flags = 1
    r = int(Life.syncTime(JString(WC), JLong(T0), JInt(0)))
    K.check(A.w[WC].flags & 1 and r == 0, "TIME setting off -> a clock WE did not pause stays as it is")
    Cfg.SYNC_TIME = True
    sync(WA, T0 + 8 * H, T0)
    Life.HELD.clear()                                 # a restart mid-hold
    Cfg.SYNC_TIME = False
    Life.TIME_AT.clear()
    A.queue[:] = []
    K.eq(int(Life.timeAll(JLong(A.t + 60000))), 1, "TIME restart mid-hold + setting off: the island with time.held=1 gets a release task")
    A.drain()
    K.check(not (A.w[WA].flags & 1) and fread(KA).get("time.held") == "0", "TIME ... and its clock is unpaused")
    Cfg.SYNC_TIME = True
    # review: the hub's clock cannot be read -> held islands are released (never paused forever)
    sync(WA, T0 + 8 * H, T0)
    K.check(A.w[WA].flags & 1 and Life.HELD.containsKey(WA), "TIME (set-up) island held")
    saved_hub = A.w.pop("hub")
    Life.TIME_AT.clear()
    Life.HUBQ = 0
    A.queue[:] = []
    K.eq(int(Life.timeAll(JLong(A.t + 70000))), 1, "TIME hub world not loaded (exec fails) -> a release task for the held island (the shard is not held)")
    A.drain()
    K.check(not (A.w[WA].flags & 1) and not Life.HELD.containsKey(WA) and fread(KA).get("time.held") == "0", "TIME ... and its clock runs again")
    A.w["hub"] = saved_hub
    sync(WA, T0 + 8 * H, T0)
    A.queue[:] = []
    K.eq(int(Life.timeHub(JString("nohub"), JArray(JString)([JString(WA), JString(WS)]))), 0, "TIME timeHub with an unreadable hub clock -> no sync tasks")
    K.check([int(t_.mode) for t_ in A.queue] == [11], "TIME ... only a release task, for the held island")
    A.drain()
    K.check(not (A.w[WA].flags & 1) and int(Life.HUBQ) == 0, "TIME ... released, the hub task flag cleared")
    # never backwards: a random walk of hub / island clocks, bed skips, hub pauses
    rnd = random.Random(513)
    back = []
    hc, ic, fl = T0, T0, 0
    for step in range(500):
        hc += rnd.choice((0, 240000, 240000, 240000, 3 * H))
        kind = rnd.random()
        if kind < 0.05:
            ic += 9 * H                               # a bed skip on the island
        elif kind < 0.08:
            ic += rnd.randint(1, 4) * DAY + rnd.randint(0, 23) * H
        elif not (fl & 1):
            ic += rnd.choice((0, 230000, 240000, 250000))
        before = ic
        A.w[WA].clock, A.w[WA].flags = ic, fl
        Life.syncTime(JString(WA), JLong(hc), JInt(1 if rnd.random() < 0.05 else 0))
        ic, fl = A.w[WA].clock, A.w[WA].flags
        if ic < before:
            back.append((step, before, ic))
        if hc - ic > DAY:
            back.append(("lag", step, hc - ic))
    K.check(not back, "TIME 500 random steps: the island clock never moved backwards and never fell a day behind the hub: %s" % back[:3])
    K.check(abs(ic - hc) < 13 * H or (ic - hc) % DAY < 13 * H, "TIME after the walk the island is at the hub's time of day (or held < 12 h)")
    st_ = code("IsleEng", "setGameTime")
    K.check("WorldTimeResource.setGameTime" in st_ and "Instant.ofEpochMilli" in st_, "TIME shape: setGameTime = WorldTimeResource.setGameTime (what /time set uses)")
    sp_ = code("IsleEng", "setTimePaused")
    K.check("WorldConfig.setGameTimePaused" in sp_ and "WorldConfig.markChanged" in sp_, "TIME shape: setTimePaused = WorldConfig.setGameTimePaused + markChanged")
    tf_ = code("IsleEng", "timeFlags")
    K.check("WorldSomnolence.getState" in tf_ and "instanceof" in tf_ and "isGameTimePaused" in tf_ and "toEpochMilli" in code("IsleEng", "gameTime"),
            "TIME shape: flags = paused + bed skip (WorldSomnolence state instanceof WorldSlumber)")
    K.check("long 60000" in code("IsleLife", "syncTime") and "long -60000" not in code("IsleLife", "syncTime"), "TIME the tolerance compiled as +60000 game ms (javassist minus folding avoided)")
    K.check("IsleLife.timeAll" in code("IsleLife", "tickAll"), "TIME shape: the 1 s ticker calls timeAll")
    tr_ = code("IsleTask", "run")
    K.check(all(x in tr_ for x in ("IsleLife.syncTime", "IsleLife.release", "IsleLife.timeHub")), "TIME shape: IsleTask modes 10 / 11 / 12")
    K.check('"skyy-shard-"' in code("IsleEng", "timeWorlds") and '"skyy-island-"' in code("IsleEng", "timeWorlds"), "TIME island + shard worlds by name")

    # ---------------------------------------------------------------- LOGIN
    def dec(wn, home_, on_isl, on=True, hp=False):
        return int(Route.decide(JString(wn) if wn else None, JString(home_) if home_ else None, on_isl, on, hp))
    table = [(("hub", WA, False), 1, "logged in in the hub -> own island"),
             ((WA, WA, True), 0, "logged in on own / co-op island -> stay"),
             ((WC, WA, True), 1, "logged in on ANOTHER island -> own island"),
             ((WS, WA, False), 0, "logged in in a shard -> stay (SkyyShards' router)"),
             (("skywynn_z1", WA, False), 0, "logged in in a zone world (islands.respawnKeep) -> stay"),
             (("default", WA, False), 1, "logged in in another world -> own island")]
    K.eq([dec(*a[0]) for a in table], [a[1] for a in table], "LOGIN decide: hub -> island, own island -> stay, another island -> own, shard / zone (respawnKeep) -> stay, other world -> island")
    Cfg.RESPAWN_KEEP = "myzone_, ,"
    K.eq([dec("myzone_1", WA, False), dec("skywynn_z1", WA, False), dec(WS, WA, False)], [0, 1, 0],
         "LOGIN islands.respawnKeep edited: its worlds stay (myzone_), a world no longer listed goes home, shards always stay")
    Cfg.RESPAWN_KEEP = "skyy-shard-,skywynn_z"
    rd = code("RouteTask", "decide")
    K.check("RouteTask.keep" in rd and "IslandCfg.RESPAWN_KEEP" in code("RouteTask", "keep"), "LOGIN shape: decide -> keep (islands.respawnKeep, as the respawn hook)")
    K.eq([dec(WA, WA, True, True, True), dec("hub", WA, False, True, True)], [2, 0], "LOGIN Hub on login switch ON -> as before (island world -> hub, hub -> stay)")
    K.eq([dec(WA, WA, True, False), dec("hub", WA, False, False)], [2, 0], "LOGIN islands.islandOnLogin off -> as before")
    K.eq([dec(WC, None, True), dec("hub", None, False)], [2, 0], "LOGIN no island yet -> as before (island world -> hub, else stay)")
    K.eq(dec(None, WA, False), 0, "LOGIN no world -> nothing")
    K.check(not bool(Route.hubPref(uA)), "LOGIN no settings provider -> not hub (start on the island)")

    @JImplements(Function)
    class SetFn(object):
        def __init__(self, v):
            self.v = v

        @JOverride
        def apply(self, o):
            return self.v
    for v, want_ in ((JBoolean(True), True), (JBoolean(False), False), (None, False)):
        br.put("settings:fn:get", SetFn(v))
        K.eq(bool(Route.hubPref(uA)), want_, "LOGIN hubPref: settings:fn:get %r -> %s" % (v, want_))
    br.remove("settings:fn:get")
    rr = code("RouteTask", "run")
    K.check(0 <= rr.find("RouteTask.decide") < rr.find("IslandCmd.go") < rr.find("HubCmd.sendToHub") and "IslandStore.homeKey" in rr and "IslandCfg.ISLAND_LOGIN" in rr,
            "LOGIN shape: run = homeKey -> decide -> 1: IslandCmd.go (/island's path, loads the world first) / 2: HubCmd.sendToHub")
    ac = code("IslandReady", "accept")
    K.check(0 <= ac.find("ConcurrentHashMap.putIfAbsent") < ac.find("RouteTask.schedule"), "LOGIN only the first ready of the session routes (SEEN) - no loops")
    gen = open(os.path.join(HERE, "build_skyyislands_%s.py" % VERSION), encoding="utf-8").read()
    K.check('regSetting("islands.hubOnLogin", "Hub on login", "profiles", false,' in gen, "LOGIN the Hub on login switch's default is now OFF (a stored ON keeps the hub)")
    Life.API = None
    K.save()


if __name__ == "__main__":
    print("S. real-server phase: NOT RUN in this round (no server start) - UNVERIFIED in game")
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("p13", run_p13), ("p2", run_p2), ("s3", run_s3m), ("snd", T59.run_snd), ("exec", T58.run_exec), ("live", T512.run_live2)],
           script=__file__, live=(T58.LIVE_DIR, "Skyy_SkyyIslands"))
