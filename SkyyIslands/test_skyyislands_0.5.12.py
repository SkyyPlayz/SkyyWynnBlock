"""Harness for SkyyIslands 0.5.12 (STARTER ISLANDS PART 2: camp skeletons, the Shardkeeper + Hub Shard, the working portal, respawn on your
island; tools/islands_0_5_12_patch.py) on top of the 0.5.11 harness. Build first:
python tools/islands_0_5_12_patch.py && python SkyyIslands/build_skyyislands_0.5.12.py

    python SkyyIslands/test_skyyislands_0.5.12.py [--dir <folder inside tools/dev/scratch/>] [--keep]

  P2    EXECUTED on stand-in worlds (IsleLife.API = a Python IsleApi; real IslandStore files in scratch, real config kit rows, -Xverify:all):
        the build-time cells (socket / frame / camp spots / probe) = the layout; 3-island recognition (probe, unloaded retry, classic = no,
        isles=3 remembered); CAMP (members only - owner / co-op / trusted, never a visitor, only on island 2; 3 spawned on free spots,
        roles in turn, Lv 1-3; a death -> 60 s; the max 5 counts leftovers; blocked spots; off; unknown role); BOSS (wakes near the arena,
        Lv 10 "Shardkeeper", one at a time, adopted after a restart, cooldown 300 s / 30 s without a killer); HUB SHARD (killer + members
        near the arena, once per profile key, file saved + reloaded, bags full -> owed -> given later, never on another profile);
        PORTAL (socket placed, visitor refused, no shard -> the repair text, repair takes exactly 1, pad + frame (only air), portal=1 in
        the island file, island:portal to SkyyQuests, everyone told, step-in / F -> hub at most once per 4 s, restart keeps it, admin may
        repair); RESPAWN (route() table; co-op member on the owner's island, member elsewhere -> home, a bed where they died wins,
        no island -> hub, in the hub -> nothing, off, gone); tickAll (one task per world); config lines (fresh / 0.5.11 file / hand edits /
        clamps) + the 13 Server Setup rows; useFlag leaves Skyy_Island_* blocks to IsleUse; the ECS hooks' null paths + their code shape;
        the jar's item / block JSON + lang + icon
  S3 / MOUTH  every 0.5.10 + 0.5.11 layout / design check on the 0.5.12 jar (the layout is unchanged)
  A / C / AA  verify, class compare 0.5.11 -> 0.5.12, engine-access audit
  SND, X, D   the 0.5.9 / 0.5.8 phases on the 0.5.12 jar (D = START TWICE on a scratch COPY of the live Skyy_SkyyIslands, nothing written,
              + the 0.5.12 config / hubshards load on that copy)
  FIX   the critic fixes (fix round isle2fix), each EXECUTED: reset clears the portal / isles keys (and the reset island gets a socket +
        a new shard by the again-rule); the again-rule (co-op of this island, portal broken, holds none; never a visitor / trusted / after
        repair); profile:busy (owed, then given; repair refused); the pad = repaired (lost portal=1 written again); unreadable
        hubshards.properties kept as .bad; pets:fn:ownerOf; per-death camp respawn times; islands.respawnKeep (shard / zone worlds keep
        their respawn, the hub goes home); quest:caller:islands follows design + boss on; /hub from a classic home -> island:portal; no
        floating socket
  The REAL server phase is NOT RUN (no server start in this round) - UNVERIFIED in game.
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "isle2fix", "islands", "h")]
if "--no-server" not in sys.argv and "--phase" not in sys.argv:
    sys.argv.append("--no-server")
import skyybuild as B
import harness_kit as HK
import soundpass_kit as SK

_spec = importlib.util.spec_from_file_location("test_skyyislands_0_5_11", os.path.join(HERE, "test_skyyislands_0.5.11.py"))
T511 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T511)
T510, T59, T58 = T511.T510, T511.T59, T511.T58

VERSION = "0.5.12"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-0.5.11.jar")
SCRATCH = T510.SCRATCH
PKG = T510.PKG
T510.JAR = JAR
T511.JAR = JAR
EXPECT = {
    "IslandCfg": ["+f CAMP_ON", "+f CAMP_COUNT", "+f CAMP_MAX", "+f CAMP_RESPAWN", "+f CAMP_ROLES", "+f CAMP_LV_MIN", "+f CAMP_LV_MAX",
                  "+f BOSS_ON", "+f BOSS_COOLDOWN", "+f BOSS_LEVEL", "+f BOSS_ROLE", "+f BOSS_NAME", "+f RESPAWN_HOME", "+f RESPAWN_KEEP",
                  "~<clinit>", "~m load"],
    "IslandStore": ["~m setWorldName0"],
    "StarterIsles": ["~m publish"],
    "HubCmd": ["~m execute"],
    "IslandPerms": ["~m useFlag"],
    "SkyyIslandsPlugin": ["+f isleTicker", "~m setup", "~m shutdown"],
    "CfgFile": ["~<clinit>"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
}
ADDED = ["IsleApi", "IsleState", "IsleLife", "IsleEng", "IsleTask", "IsleUse", "IsleDeath", "IsleRespawn"]
T510.layout = lambda: T511.layout_of(VERSION)
KA, KB, KT, KV, KN, KC = ("00000000-0000-4000-8000-00000000a512", "00000000-0000-4000-8000-00000000b512", "00000000-0000-4000-8000-00000000c512",
                          "00000000-0000-4000-8000-00000000d512", "00000000-0000-4000-8000-00000000e512", "00000000-0000-4000-8000-00000000f512")
WA, WC, WD = "skyy-island-" + KA, "skyy-island-" + KC, "skyy-island-unloaded"


NEW_FILES = sorted(["Common/Icons/ItemsGenerated/Skyy_Hub_Shard.png", "Server/Item/Items/SkyyIslands/Skyy_Hub_Shard.json",
                    "Server/Item/Items/SkyyIslands/Skyy_Island_Hub_Portal.json", "Server/Item/Items/SkyyIslands/Skyy_Island_Portal_Socket.json",
                    "Server/Languages/en-US/server.lang"])
_orig_compare = HK.run_compare


def run_compare(out, jar, old_jar, pkg, expect, added):
    """the kit's compare, then its non-class check replaced by the exact 0.5.12 expectation: the 5 new asset files, the manifest's Version /
    Name, nothing else (the instance template and everything else byte-identical, nothing removed)"""
    _orig_compare(out, jar, old_jar, pkg, expect, added)
    d = json.load(open(out))
    d["fails"] = [f for f in d["fails"] if not f.startswith("C: non-class entries changed")]
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    na, nb = set(n_ for n_ in za.namelist() if not n_.endswith(".class")), set(n_ for n_ in zb.namelist() if not n_.endswith(".class"))
    if sorted(nb - na) != NEW_FILES or na - nb:
        d["fails"].append("C: non-class entries added %s / removed %s, want added %s" % (sorted(nb - na), sorted(na - nb), NEW_FILES))
    changed = sorted(n_ for n_ in na & nb if za.read(n_) != zb.read(n_))
    if changed != ["manifest.json"]:
        d["fails"].append("C: changed non-class entries %s, want only manifest.json" % changed)
    ma, mb = json.loads(za.read("manifest.json")), json.loads(zb.read("manifest.json"))
    for m_, v_ in ((ma, "0.5.11"), (mb, VERSION)):
        if m_.pop("Version", None) != v_ or m_.pop("Name", None) != v_ + " SkyyIslands":
            d["fails"].append("C: manifest Version / Name are not %s" % v_)
    if ma != mb:
        d["fails"].append("C: manifest changed beyond Version / Name")
    d["ok"] += 1
    d["notes"] = d.get("notes", []) + ["C: non-class: manifest (Version / Name) + the 5 new asset files"]
    json.dump(d, open(out, "w"), indent=1)


HK.run_compare = run_compare      # the kit's builtin "compare" looks the name up at call time


def run_p2(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject, JString, JDouble, JInt, JLong, JBoolean
    K = HK.Child(out)
    m = T511.layout_of(VERSION)
    P2 = m.S3_P2
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    P = lambda n: JClass(PKG + n)
    St, Cfg, Life, Task, Perms, Rows = P("IslandStore"), P("IslandCfg"), P("IsleLife"), P("IsleTask"), P("IslandPerms"), P("CfgRows")
    Paths, UUID, Double, ArrayList, HashSet = (JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Double"),
                                               JClass("java.util.ArrayList"), JClass("java.util.HashSet"))
    uA, uB, uT, uV, uN, uC = [UUID.fromString(k) for k in (KA, KB, KT, KV, KN, KC)]
    import shutil
    shutil.rmtree(os.path.join(scratch, "p2"), ignore_errors=True)     # (a phase re-run starts clean)
    home = os.path.join(scratch, "p2", "Skyy_SkyyIslands")
    isl = os.path.join(home, "islands")
    os.makedirs(isl, exist_ok=True)

    # ---------------------------------------------------------------- config (fresh file, 0.5.11 file, hand edits, clamps) + rows
    cf = os.path.join(home, "config.properties")
    Cfg.FILE = Paths.get(cf)
    Cfg.load("")
    txt = open(cf, encoding="utf-8").read()
    want_lines = ["camp.enabled=true", "camp.count=3", "camp.max=5", "camp.respawnSeconds=60", "camp.roles=Skeleton_Fighter,Skeleton_Fighter,Skeleton_Soldier",
                  "camp.levelMin=1", "camp.levelMax=3", "boss.enabled=true", "boss.cooldownSeconds=300", "boss.level=10", "boss.role=Golem_Crystal_Earth",
                  "boss.name=Shardkeeper", "islands.respawnHome=true", "islands.respawnKeep=skyy-shard-,skywynn_z"]
    K.check(all(l in txt.splitlines() for l in want_lines), "CFG a fresh config.properties lists the 14 part-2 lines")
    defaults = (True, 3, 5, 60, "Skeleton_Fighter,Skeleton_Fighter,Skeleton_Soldier", 1, 3, True, 300, 10, "Golem_Crystal_Earth", "Shardkeeper", True,
                "skyy-shard-,skywynn_z")

    def cur():
        return (bool(Cfg.CAMP_ON), int(Cfg.CAMP_COUNT), int(Cfg.CAMP_MAX), int(Cfg.CAMP_RESPAWN), str(Cfg.CAMP_ROLES), int(Cfg.CAMP_LV_MIN),
                int(Cfg.CAMP_LV_MAX), bool(Cfg.BOSS_ON), int(Cfg.BOSS_COOLDOWN), int(Cfg.BOSS_LEVEL), str(Cfg.BOSS_ROLE), str(Cfg.BOSS_NAME),
                bool(Cfg.RESPAWN_HOME), str(Cfg.RESPAWN_KEEP))
    K.eq(cur(), defaults, "CFG defaults from the fresh file")
    old511 = "\n".join(l for l in txt.splitlines() if not l.split("=")[0] in [w.split("=")[0] for w in want_lines] and "0.5.12" not in l) + "\n"
    open(cf, "w", encoding="utf-8").write(old511)
    Cfg.CAMP_COUNT = 99
    Cfg.RESPAWN_HOME = False
    Cfg.load("")
    K.eq(cur(), defaults, "CFG a 0.5.11 file without the lines = every default (nothing rewritten)")
    K.eq(open(cf, encoding="utf-8").read(), old511, "CFG the 0.5.11 file is not rewritten by load")
    open(cf, "w", encoding="utf-8").write(old511 + "camp.count=4\ncamp.max=99\ncamp.respawnSeconds=1\nislands.respawnHome=false\nboss.name=Keeper\ncamp.enabled=FALSE\n")
    Cfg.load("")
    K.eq((int(Cfg.CAMP_COUNT), int(Cfg.CAMP_MAX), int(Cfg.CAMP_RESPAWN), bool(Cfg.RESPAWN_HOME), str(Cfg.BOSS_NAME), bool(Cfg.CAMP_ON)),
         (4, 20, 5, False, "Keeper", False), "CFG hand edits read, out-of-range values clamped (max 99 -> 20, respawn 1 -> 5 s)")
    open(cf, "w", encoding="utf-8").write(txt)
    Cfg.load("")
    rows = SK.kit_rows(Rows)
    want_rows = {"camp.enabled": ("isles", "bool", "true"), "camp.count": ("isles", "int", "3"), "camp.max": ("isles", "int", "5"),
                 "camp.respawnSeconds": ("isles", "int", "60"), "camp.roles": ("isles", "text", "Skeleton_Fighter,Skeleton_Fighter,Skeleton_Soldier"),
                 "camp.levelMin": ("isles", "int", "1"), "camp.levelMax": ("isles", "int", "3"), "boss.enabled": ("isles", "bool", "true"),
                 "boss.cooldownSeconds": ("isles", "int", "300"), "boss.level": ("isles", "int", "10"), "boss.role": ("isles", "text", "Golem_Crystal_Earth"),
                 "boss.name": ("isles", "text", "Shardkeeper"), "islands.respawnHome": ("hub", "bool", "true"),
                 "islands.respawnKeep": ("hub", "text", "skyy-shard-,skywynn_z")}
    K.check(all(k in rows and tuple(rows[k][2:5]) == v and "live" in rows[k][9] for k, v in want_rows.items()),
            "ROW the 14 Server Setup rows (Starter islands + Hub), live, the right defaults: %s" % [(k, rows.get(k, [None] * 5)[2:5]) for k in want_rows if k not in rows or tuple(rows[k][2:5]) != want_rows[k]])
    K.check(rows["camp.respawnSeconds"][8] == "s" and rows["boss.cooldownSeconds"][8] == "s", "ROW times in seconds")
    gen = open(os.path.join(HERE, "build_skyyislands_%s.py" % VERSION), encoding="utf-8").read()
    K.check("config.properties:boss.enabled;after=IslandHooks.afterDesign" in gen, "FIX(i) ROW boss.enabled re-publishes quest:caller:islands when it changes (after=IslandHooks.afterDesign)")
    hdr = Rows.header()
    K.check("isles" in [str(x) for x in hdr[5]] and "Starter islands" in [str(x) for x in hdr[6]], "ROW new category 'Starter islands'")

    # ---------------------------------------------------------------- the build-time cells = the layout
    L = m.S3_L
    K.eq(list(Life.SOCKETP), list(P2["socket"]), "CELLS socket")
    K.check(L.get(tuple(P2["socket"])) == "Rock_Stone_Brick_Smooth", "CELLS the socket is the frame's smooth brick in the layout")
    K.check(all((f[0], f[1], f[2]) not in L for f in P2["fix"]) and list(Life.FIX_IDS) == [f[3] for f in P2["fix"]], "CELLS the frame's broken top = empty cells")
    sp = list(Life.SPOTS)
    ok_spots = True
    for i in range(0, len(sp), 3):
        x, y, z = int(sp[i] // 1), int(sp[i + 1] // 1), int(sp[i + 2] // 1)
        ok_spots = ok_spots and (x, y, z) not in L and (x, y + 1, z) not in L and (x, y - 1, z) in L and m.S3_ISLE.get((x, z)) == "island2"
    K.check(len(sp) == 18 and ok_spots, "CELLS 6 camp spots on island 2, free with solid ground")
    pr = list(Life.PROBE)
    K.check(len(pr) == 36 and all(L.get((pr[i], pr[i + 1], pr[i + 2])) == "Rock_Stone" for i in range(0, 36, 3)), "CELLS 12 probe cells = deep stone of islands 2 + 3")
    K.eq([round(float(v), 2) for v in Life.CAMP], [round(v, 2) for v in m.S3_PLACES["camp"][:3]], "CELLS camp place")
    K.eq([round(float(v), 2) for v in Life.BOSS], [round(v, 2) for v in m.S3_PLACES["boss"][:3]], "CELLS boss place")

    # ---------------------------------------------------------------- island files (real IslandStore in scratch)
    def wfile(k, props):
        with open(os.path.join(isl, k + ".properties"), "w", encoding="utf-8") as f:
            f.write("".join("%s=%s\n" % kv for kv in props.items()))
    wfile(KA, {"v": "5", "world": WA, "members": KB, "trusted": KT})
    wfile(KC, {"v": "5", "world": WC})
    wfile("00000000-0000-4000-8000-0000000d0000", {"v": "5", "world": WD})
    St.DIR = Paths.get(isl)
    St.IO = None
    St.STOPPING = False
    St.SETTINGS.clear()
    St.loadIslandWorlds()
    K.check(bool(St.isIslandWorld(WA)) and str(St.ownerOf(WA)) == KA and str(St.homeKey(uB)) == KA, "SETUP island A registered, B is A's co-op member (homeKey)")
    K.eq([int(Perms.rankU(KA, u)) for u in (uA, uB, uT, uV)], [4, 2, 1, 0], "SETUP ranks owner / co-op / trusted / visitor")

    # ---------------------------------------------------------------- the stand-in engine
    NAMES = {KA: "Ava", KB: "Ben", KT: "Tia", KV: "Vic", KN: "Nia", KC: "Cal"}

    class World(object):
        def __init__(self, blocks):
            self.blocks, self.players, self.npcs, self.unloaded = dict(blocks), {}, {}, set()

    class Api(object):
        def __init__(self):
            self.t = 1000000
            self.w = {WA: World(L), WC: World({}), WD: World({}), "zone1": World({}), "hub": World({})}
            self.w[WD].unloaded = set((pr[i], pr[i + 1], pr[i + 2]) for i in range(0, 36, 3))
            self.inv, self.cap, self.beds, self.admins = {}, {}, set(), set()
            self.log, self.queue, self.msgs, self.n, self.blk = [], [], [], 0, 0

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
            rows = [] if w is None else [JArray(JObject)([UUID.fromString(k), Double(v[0]), Double(v[1]), Double(v[2])]) for k, v in w.players.items()]
            return JArray(JObject)(rows)

        @JOverride
        def npcs(self, wn, x, y, z, r):
            out = ArrayList()
            w = A.w.get(str(wn))
            for k, v in ([] if w is None else w.npcs.items()):
                if v[4] and (v[1] - x) ** 2 + (v[2] - y) ** 2 + (v[3] - z) ** 2 <= r * r:
                    out.add(JArray(JObject)([JString(k), JString(v[0])]))
            return out

        @JOverride
        def alive(self, wn, uuid):
            w = A.w.get(str(wn))
            return bool(w is not None and uuid is not None and str(uuid) in w.npcs and w.npcs[str(uuid)][4])

        @JOverride
        def roleOk(self, role):
            return str(role) in ("Skeleton_Fighter", "Skeleton_Soldier", "Golem_Crystal_Earth")

        @JOverride
        def spawn(self, wn, role, x, y, z, yaw):
            A.n += 1
            k = "00000000-0000-4000-9000-%012d" % A.n
            A.w[str(wn)].npcs[k] = [str(role), float(x), float(y), float(z), True]
            A.ev("spawn", str(wn), str(role), float(x), float(y), float(z), k)
            return JString(k)

        @JOverride
        def level(self, wn, uuid, lvl, name):
            A.ev("level", str(wn), str(uuid), int(lvl), None if name is None else str(name))
            return True

        @JOverride
        def block(self, wn, x, y, z):
            A.blk += 1
            w = A.w.get(str(wn))
            if w is None or (int(x), int(y), int(z)) in w.unloaded:
                return None
            return JString(w.blocks.get((int(x), int(y), int(z)), ""))

        @JOverride
        def setBlock(self, wn, x, y, z, bid):
            A.w[str(wn)].blocks[(int(x), int(y), int(z))] = str(bid)
            A.ev("set", str(wn), int(x), int(y), int(z), str(bid))
            return True

        @JOverride
        def count(self, wn, u, bid):
            return JLong(A.inv.get(str(u), {}).get(str(bid), 0))

        @JOverride
        def take(self, wn, u, bid, n):
            have = A.inv.setdefault(str(u), {}).get(str(bid), 0)
            t = min(have, int(n))
            A.inv[str(u)][str(bid)] = have - t
            A.ev("take", str(u), str(bid), t)
            return JLong(t)

        @JOverride
        def give(self, wn, u, bid, n):
            bag = A.inv.setdefault(str(u), {})
            room = A.cap.get(str(u), 999) - sum(bag.values())
            g = max(0, min(int(n), room))
            bag[str(bid)] = bag.get(str(bid), 0) + g
            A.ev("give", str(u), str(bid), g)
            return JLong(g)

        @JOverride
        def say(self, u, text, color):
            A.msgs.append((str(u), str(text)))

        @JOverride
        def name(self, u):
            return JString(NAMES.get(str(u), "Someone"))

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
            s = HashSet()
            for k, w in A.w.items():
                if w.players and St.isIslandWorld(k):
                    s.add(JString(k))
            return s

        @JOverride
        def relight(self, wn):
            A.ev("relight", str(wn))
    Life.API = Stand()
    Life.ST.clear()
    Life.GOT.clear()
    Life.PENDING.clear()
    got_file = os.path.join(home, "hubshards.properties")
    K.eq(int(Life.loadGot(Paths.get(got_file))), 0, "SHARD no hubshards.properties yet -> nobody has one; nothing written")
    K.check(not os.path.exists(got_file), "SHARD loadGot writes nothing")

    def tick(wn=WA):
        return int(Life.tickWorld(JString(wn)))

    def place(world, k, pos):
        A.w[world].players[k] = list(pos)

    def clear_players():
        for w in A.w.values():
            w.players.clear()
    ISL1 = (8.5, 129.0, 8.5)
    ISL2 = (46.5, 128.0, 14.5)
    ARENA = (71.5, 130.0, 36.5)

    # ---------------------------------------------------------------- 3-island recognition
    place(WC, KC, ISL2)
    K.eq(tick(WC), 0, "THREE a classic island (no stone at the probe cells) -> nothing at all")
    K.check(int(Life.state(WC).three) == 0 and not A.kinds("spawn"), "THREE classic: three = 0, no spawn")
    place(WD, KC, ISL2)
    tick(WD)
    K.eq(int(Life.state(WD).three), -1, "THREE probe cells not loaded -> unknown (-1), tried again later")
    nb = len(A.kinds("set"))
    place(WA, KA, ISL1)
    K.check(tick(WA) >= 1 and int(Life.state(WA).three) == 1, "THREE island A recognised (12 / 12 deep stone cells)")
    K.check("isles=3" in open(os.path.join(isl, KA + ".properties"), encoding="utf-8").read(), "THREE isles=3 remembered in A's island file (new key)")
    K.check(A.kinds("set")[nb:][:1] == [("set", WA, P2["socket"][0], P2["socket"][1], P2["socket"][2], "Skyy_Island_Portal_Socket")],
            "PORTAL the frame's smooth brick socket becomes Skyy_Island_Portal_Socket on the first tick")
    K.check(not A.kinds("spawn"), "CAMP / BOSS the owner on island 1 -> no spawns")
    Life.ST.clear()
    calls0 = A.blk
    st = Life.state(WA)
    K.check(bool(Life.three(JString(WA), st, JString(KA), JLong(A.t))) and A.blk == calls0, "THREE after a restart the island file answers (no block read)")

    # ---------------------------------------------------------------- camp
    Life.ST.clear()
    clear_players()
    place(WA, KV, ISL2)
    tick()
    K.check(not A.kinds("spawn"), "CAMP a VISITOR alone on island 2 -> no spawns")
    place(WA, KB, ISL2)
    tick()
    sp1 = A.kinds("spawn")
    lv1 = [e for e in A.kinds("level") if e[4] is None]
    K.eq([e[2] for e in sp1], ["Skeleton_Fighter", "Skeleton_Fighter", "Skeleton_Soldier"], "CAMP co-op member on island 2 -> 3 skeletons, roles in turn")
    K.check(len(set((e[3], e[5]) for e in sp1)) == 3 and all((round(e[3], 2), round(e[4], 2), round(e[5], 2)) in [(round(sp[i], 2), round(sp[i + 1], 2), round(sp[i + 2], 2)) for i in range(0, 18, 3)] for e in sp1),
            "CAMP on 3 different camp spots")
    K.check(len(lv1) == 3 and all(1 <= e[3] <= 3 for e in lv1), "CAMP each gets Lv 1-3 (mob:fn:setLevel, no name): %s" % [e[3] for e in lv1])
    tick()
    K.eq(len(A.kinds("spawn")), 3, "CAMP 3 alive -> no more")
    dead = sp1[0][6]
    A.w[WA].npcs[dead][4] = False
    K.eq(int(Life.onDeath(JString(WA), JString("Skeleton_Fighter"), JString(dead), uB, JDouble(sp1[0][3]), JDouble(sp1[0][5]), JLong(A.t))), 1,
         "CAMP death hook: a camp skeleton (tracked) -> 1")
    A.t += 30000
    tick()
    K.eq(len(A.kinds("spawn")), 3, "CAMP 30 s after the death -> still 2 alive, no spawn yet")
    A.t += 31000
    tick()
    K.eq(len(A.kinds("spawn")), 4, "CAMP 61 s after the death -> one new skeleton (back to 3)")
    clear_players()
    place(WA, KB, ISL1)
    for k in list(A.w[WA].npcs):
        A.w[WA].npcs[k][4] = False
    A.t += 120000
    tick()
    K.eq(len(A.kinds("spawn")), 4, "CAMP all dead but the member is on island 1 -> no spawn")
    clear_players()
    place(WA, KT, ISL2)
    tick()
    K.eq(len(A.kinds("spawn")), 7, "CAMP a TRUSTED player on island 2 -> spawns (3)")
    Life.ST.clear()      # restart: the 3 are leftovers in the chunk now (untracked)
    for i in range(2):   # + 2 more leftovers = 5
        A.w[WA].npcs["leftover-%d" % i] = ["Skeleton_Fighter", 50.5, 128.0, 16.5, True]
    Cfg.CAMP_COUNT = 8
    tick()
    K.eq(len(A.kinds("spawn")), 7, "CAMP count 8 but 5 alive (leftovers counted) = camp.max -> no spawn")
    A.w[WA].npcs["leftover-0"][4] = False
    tick()
    K.eq(len(A.kinds("spawn")), 8, "CAMP 4 alive, count 8, max 5 -> exactly 1 more")
    Cfg.CAMP_COUNT = 3
    for k in list(A.w[WA].npcs):
        A.w[WA].npcs[k][4] = False
    saved = {}
    for i in range(0, 18, 3):
        c = (int(sp[i] // 1), int(sp[i + 1] // 1), int(sp[i + 2] // 1))
        saved[c] = A.w[WA].blocks.get(c)
        A.w[WA].blocks[c] = "Rock_Stone"
    Life.ST.clear()
    tick()
    K.check(len(A.kinds("spawn")) == 8 and int(Life.state(WA).campNext) == A.t + 10000, "CAMP every spot built over -> no spawn, tried again in 10 s")
    for c, v in saved.items():
        if v is None:
            A.w[WA].blocks.pop(c, None)
        else:
            A.w[WA].blocks[c] = v
    Cfg.CAMP_ON = False
    A.t += 11000
    tick()
    K.eq(len(A.kinds("spawn")), 8, "CAMP camp.enabled off -> no spawn")
    Cfg.CAMP_ON = True
    Cfg.CAMP_ROLES = "Not_A_Role,Skeleton_Fighter"
    tick()
    K.check([e[2] for e in A.kinds("spawn")[8:]] == ["Skeleton_Fighter"], "CAMP an unknown role in camp.roles is skipped (the others still spawn)")
    Cfg.CAMP_ROLES = "Skeleton_Fighter,Skeleton_Fighter,Skeleton_Soldier"
    K.eq(int(Life.onDeath(JString(WC), JString("Skeleton_Fighter"), JString("x"), uB, JDouble(50.5), JDouble(16.5), JLong(A.t))), 0,
         "CAMP a death on a classic island -> 0 (no camp there)")
    K.eq(int(Life.onDeath(JString(WA), JString("Kweebec_Seedling"), JString("x"), uB, JDouble(50.5), JDouble(16.5), JLong(A.t))), 0, "CAMP another mob's death -> 0")

    # ---------------------------------------------------------------- FIX (g): each camp death has its own respawn time
    clear_players()
    for k in list(A.w[WA].npcs):
        A.w[WA].npcs[k][4] = False
    Life.ST.clear()
    place(WA, KB, ISL2)
    A.t += 20000
    n0 = len(A.kinds("spawn"))
    tick()
    K.eq(len(A.kinds("spawn")), n0 + 3, "FIX(g) camp refilled to 3")
    alive3 = [e[6] for e in A.kinds("spawn")[n0:]]
    A.w[WA].npcs[alive3[0]][4] = False
    Life.onDeath(JString(WA), JString("Skeleton_Fighter"), JString(alive3[0]), uB, JDouble(50.0), JDouble(16.0), JLong(A.t))
    A.t += 30000
    A.w[WA].npcs[alive3[1]][4] = False
    Life.onDeath(JString(WA), JString("Skeleton_Fighter"), JString(alive3[1]), uB, JDouble(50.0), JDouble(16.0), JLong(A.t))
    tick()
    K.eq(len(A.kinds("spawn")), n0 + 3, "FIX(g) kill A at 0 s, B at 30 s: at 30 s nothing yet")
    A.t += 31000
    tick()
    K.eq(len(A.kinds("spawn")), n0 + 4, "FIX(g) at 61 s A's replacement comes (B's death did not push it back)")
    A.t += 20000
    tick()
    K.eq(len(A.kinds("spawn")), n0 + 4, "FIX(g) at 81 s B's is still waiting")
    A.t += 10000
    tick()
    K.eq(len(A.kinds("spawn")), n0 + 5, "FIX(g) at 91 s B's replacement comes (60 s after B died)")

    # ---------------------------------------------------------------- boss + the Hub Shard
    clear_players()
    for k in list(A.w[WA].npcs):
        A.w[WA].npcs[k][4] = False
    Life.ST.clear()
    place(WA, KA, ARENA)                     # owner at the arena
    place(WA, KB, (75.0, 132.0, 40.0))       # co-op member near
    place(WA, KV, (72.0, 130.0, 33.0))       # visitor near
    place(WA, KT, (8.5, 129.0, 8.5))         # trusted far away (island 1)
    nsp = len(A.kinds("spawn"))
    m0 = len(A.msgs)
    tick()
    bs = A.kinds("spawn")[nsp:]
    K.check(len(bs) == 1 and bs[0][2] == "Golem_Crystal_Earth" and (round(bs[0][3], 1), round(bs[0][4], 1), round(bs[0][5], 1)) == (71.5, 130.0, 34.5),
            "BOSS a member near the arena -> ONE Golem_Crystal_Earth at the arena: %s" % bs)
    boss = bs[0][6]
    K.check(("level", WA, boss, 10, "Shardkeeper") in A.log, "BOSS Lv 10, named Shardkeeper (mob:fn:setLevel)")
    K.check(sum(1 for u, t in A.msgs[m0:] if "Shardkeeper has woken" in t) == 3, "BOSS the 3 members are told it woke (not the visitor)")
    tick()
    K.eq(len(A.kinds("spawn")), nsp + 1, "BOSS one at a time")
    A.w[WA].npcs[boss][4] = False
    K.eq(int(Life.onDeath(JString(WA), JString("Golem_Crystal_Earth"), JString(boss), uV, JDouble(71.5), JDouble(34.5), JLong(A.t))), 2,
         "BOSS death hook (the VISITOR killed it) -> 2")
    K.eq(int(Life.state(WA).bossNext), A.t + 300000, "BOSS next one in 300 s")
    A.drain()
    gv = [(e[1], e[3]) for e in A.kinds("give") if e[2] == "Skyy_Hub_Shard"]
    K.eq(sorted(gv), sorted([(KA, 1), (KB, 1), (KV, 1)]), "SHARD the killer (visitor) + the owner + the co-op member near the arena get 1 each; trusted far away none")
    K.check(sorted(Life.GOT.keySet()) == sorted([KA, KB, KV]) and all(k in open(got_file, encoding="utf-8").read() for k in (KA, KB, KV)),
            "SHARD hubshards.properties holds the 3 profile keys")
    A.t += 100000
    tick()
    K.eq(len(A.kinds("spawn")), nsp + 1, "BOSS 100 s later -> still waiting (cooldown)")
    A.t += 201000
    tick()
    boss2 = A.kinds("spawn")[-1]
    K.check(len(A.kinds("spawn")) == nsp + 2 and boss2[2] == "Golem_Crystal_Earth", "BOSS after 300 s -> the next Shardkeeper")
    place(WA, KT, ARENA)
    A.cap[KT] = 0
    A.w[WA].npcs[boss2[6]][4] = False
    Life.onDeath(JString(WA), JString("Golem_Crystal_Earth"), JString(boss2[6]), uA, JDouble(71.5), JDouble(34.5), JLong(A.t))
    ng = len(A.kinds("give"))
    A.drain()
    K.check(not [e for e in A.kinds("give")[ng:] if e[1] in (KA, KB, KV) and e[3] > 0], "SHARD a second kill: nobody gets a second first shard (normal loot only)")
    K.check(str(Life.PENDING.get(uT)) == KT and any("bags are full" in t for u, t in A.msgs if u == KT), "SHARD trusted near with full bags -> owed + told")
    tick()
    K.check(KT not in [k for k in Life.GOT.keySet()], "SHARD still full -> still owed")
    A.cap[KT] = 999
    tick()
    K.check(KT in [str(k) for k in Life.GOT.keySet()] and A.inv[KT]["Skyy_Hub_Shard"] == 1 and Life.PENDING.isEmpty(), "SHARD room made -> the owed shard arrives on the next tick")
    Life.GOT.clear()
    K.eq(int(Life.loadGot(Paths.get(got_file))), 4, "SHARD restart: hubshards.properties read back (4 profile keys)")
    # another profile of the same player gets a new first shard (profile:fn:key on the bridge)

    @JImplements("java.util.function.Function")
    class PKey(object):
        def __init__(self):
            self.p2 = set()

        @JOverride
        def apply(self, o):
            return JString(str(o) + "-p2") if str(o) in self.p2 else JString(str(o))
    pk = PKey()
    br.put("profile:fn:key", pk)
    pk.p2.add(KA)
    Life.ST.clear()
    A.w[WA].npcs[boss2[6]][4] = False
    st = Life.state(WA)
    st.three = 1
    Life.onDeath(JString(WA), JString("Golem_Crystal_Earth"), JString("anyboss"), uA, JDouble(71.5), JDouble(34.5), JLong(A.t))
    ng = len(A.kinds("give"))
    A.drain()
    K.check([(e[1], e[3]) for e in A.kinds("give")[ng:]] == [(KA, 1)] and (KA + "-p2") in [str(k) for k in Life.GOT.keySet()],
            "SHARD the owner on ANOTHER profile -> a new first shard for that profile key")
    pk.p2.clear()
    # owed shard waits for the right profile
    Life.PENDING.put(uB, JString(KB + "-p9"))
    nB = A.inv[KB]["Skyy_Hub_Shard"]
    tick()
    K.check(A.inv[KB]["Skyy_Hub_Shard"] == nB and Life.PENDING.containsKey(uB), "SHARD an owed shard is never given on another profile")
    Life.PENDING.clear()
    # FIX (b): the again-rule - a lost shard never locks the profile out; only a co-op (or higher) member of THIS island, portal broken, holding none
    for k_ in (KA, KV, KT):
        A.inv.setdefault(k_, {})["Skyy_Hub_Shard"] = 0
    got_n = Life.GOT.size()
    Life.state(WA).three = 1
    Life.onDeath(JString(WA), JString("Golem_Crystal_Earth"), JString("again-boss"), uA, JDouble(71.5), JDouble(34.5), JLong(A.t))
    ng = len(A.kinds("give"))
    A.drain()
    K.check([(e[1], e[3]) for e in A.kinds("give")[ng:]] == [(KA, 1)] and Life.GOT.size() == got_n,
            "FIX(b) owner lost the shard, portal broken -> one more; the visitor / the trusted player with none get nothing; no new record: %s" % [(e[1], e[3]) for e in A.kinds("give")[ng:]])
    Life.onDeath(JString(WA), JString("Golem_Crystal_Earth"), JString("again-boss2"), uA, JDouble(71.5), JDouble(34.5), JLong(A.t))
    ng = len(A.kinds("give"))
    A.drain()
    K.check(not A.kinds("give")[ng:], "FIX(b) holding one -> no second (no farming while the bags hold one)")
    # FIX (d): profile:busy -> owed, then given once SkyyProfiles is done
    A.inv[KA]["Skyy_Hub_Shard"] = 0
    br.put("profile:busy:" + KA, JBoolean(True))
    Life.onDeath(JString(WA), JString("Golem_Crystal_Earth"), JString("busy-boss"), uA, JDouble(71.5), JDouble(34.5), JLong(A.t))
    ng = len(A.kinds("give"))
    A.drain()
    tick()
    K.check(not A.kinds("give")[ng:] and str(Life.PENDING.get(uA)) == KA, "FIX(d) profile:busy -> no item move, the shard is owed")
    br.remove("profile:busy:" + KA)
    tick()
    K.check(A.inv[KA]["Skyy_Hub_Shard"] == 1 and not Life.PENDING.containsKey(uA), "FIX(d) busy gone -> the owed shard arrives on the next tick")
    # FIX (f): a pet's killing blow counts for its owner (pets:fn:ownerOf)
    PET = UUID.fromString("00000000-0000-4000-8000-0000000fe700")
    K.check(Life.petOwner(PET) is None, "FIX(f) no SkyyPets on the bridge -> no owner")

    @JImplements("java.util.function.Function")
    class Owner(object):
        @JOverride
        def apply(self, o):
            return JString(KA) if str(o) == str(PET) else None
    br.put("pets:fn:ownerOf", Owner())
    K.check(str(Life.petOwner(PET)) == KA and Life.petOwner(uB) is None, "FIX(f) pets:fn:ownerOf: the pet -> its owner (String answer read), another entity -> none")
    br.remove("pets:fn:ownerOf")
    # restart with a Shardkeeper saved in the chunk -> adopted, named again, no second one
    for k in list(A.w[WA].npcs):
        A.w[WA].npcs[k][4] = False
    Life.ST.clear()
    A.w[WA].npcs["saved-boss"] = ["Golem_Crystal_Earth", 72.0, 130.0, 35.0, True]
    nsp2 = len(A.kinds("spawn"))
    tick()
    K.check(len(A.kinds("spawn")) == nsp2 and ("level", WA, "saved-boss", 10, "Shardkeeper") in A.log and str(Life.state(WA).boss) == "saved-boss",
            "BOSS restart: a Shardkeeper saved in the chunk is adopted (named again), no second one")
    A.w[WA].npcs["saved-boss"][4] = False
    Life.onDeath(JString(WA), JString("Golem_Crystal_Earth"), JString("saved-boss"), None, JDouble(72.0), JDouble(35.0), JLong(A.t))
    q0 = len(A.queue)
    K.check(int(Life.state(WA).bossNext) == A.t + 30000 and q0 == 0, "BOSS died without a player killer -> 30 s, no loot task")
    Cfg.BOSS_ON = False
    A.t += 31000
    tick()
    K.eq(len(A.kinds("spawn")), nsp2, "BOSS boss.enabled off -> none")
    Cfg.BOSS_ON = True

    # ---------------------------------------------------------------- portal
    clear_players()
    place(WA, KV, (79.5, 134.0, 42.5))
    A.inv[KV] = {"Skyy_Hub_Shard": 3}
    A.t += 5000
    K.eq(str(Life.useSocket(JString(WA), uV, JLong(A.t))), "rank", "PORTAL a visitor (with shards) may not repair -> refused")
    A.inv[KB] = {}
    K.eq(str(Life.useSocket(JString(WA), uB, JLong(A.t))), "need", "PORTAL a co-op member without a Hub Shard -> the repair text")
    K.check(any(t == str(Life.REPAIR_TEXT) for u, t in A.msgs if u == KB) and "Shardkeeper on this island drops one" in str(Life.REPAIR_TEXT),
            "PORTAL the text: 'Repair this portal with a Hub Shard (the Shardkeeper on this island drops one)'")
    fx0 = P2["fix"][0]
    A.w[WA].blocks[(fx0[0], fx0[1], fx0[2])] = "Wood_Oak_Planks"     # a player built one of the top cells already
    A.inv[KB] = {"Skyy_Hub_Shard": 2}
    place(WA, KB, (79.5, 134.0, 42.5))
    br.put("profile:busy:" + KB, JBoolean(True))
    A.t += 2000
    K.check(str(Life.useSocket(JString(WA), uB, JLong(A.t))) == "busy" and A.inv[KB]["Skyy_Hub_Shard"] == 2, "FIX(d) profile busy -> no repair, no shard taken")
    br.remove("profile:busy:" + KB)
    nq = len(A.kinds("quest"))
    A.t += 2000
    K.eq(str(Life.useSocket(JString(WA), uB, JLong(A.t))), "repaired", "PORTAL a co-op member WITH a Hub Shard -> repaired")
    K.eq(A.inv[KB]["Skyy_Hub_Shard"], 1, "PORTAL exactly ONE shard taken")
    K.eq(A.w[WA].blocks.get(tuple(P2["socket"])), "Skyy_Island_Hub_Portal", "PORTAL the socket is now the hub portal pad")
    K.check(A.w[WA].blocks[(fx0[0], fx0[1], fx0[2])] == "Wood_Oak_Planks" and all(A.w[WA].blocks.get((f[0], f[1], f[2])) == f[3] for f in P2["fix"][1:]),
            "PORTAL the frame's broken top filled in - only empty cells (the player's plank stays)")
    ftxt = open(os.path.join(isl, KA + ".properties"), encoding="utf-8").read()
    K.check("portal=1" in ftxt and "portal.by=Ben" in ftxt and "portal.at=" in ftxt, "PORTAL portal=1 / portal.by / portal.at in A's island file")
    K.check(("quest", KB, "island:portal") in A.kinds("quest")[nq:] and ("relight", WA) in A.log, "PORTAL island:portal sent to SkyyQuests; the light re-queued")
    K.check(sum(1 for u, t in A.msgs if "repaired the hub portal" in t) == 2, "PORTAL everyone on the island is told (2 players there)")
    nh = len(A.kinds("hub"))
    A.t += 4100
    K.eq(str(Life.useSocket(JString(WA), uV, JLong(A.t))), "trip", "PORTAL after the repair F (even a visitor) -> the hub")
    place(WA, KA, (81.5, 134.1, 42.5))      # standing on the pad
    place(WA, KT, (85.0, 134.0, 42.5))      # next to the frame, outside
    tick()
    hubs = [e[2] for e in A.kinds("hub")[nh:]]
    K.check(hubs == [KV, KA], "PORTAL step-in: the player IN the opening goes to the hub, the one beside it does not: %s" % hubs)
    tick()
    K.eq(len(A.kinds("hub")), nh + 2, "PORTAL still standing in it -> not again within 4 s")
    A.t += 4100
    tick()
    K.eq(len(A.kinds("hub")), nh + 3, "PORTAL 4 s later -> again")
    Life.ST.clear()                         # restart: portal=1 from the file
    A.w[WA].blocks[tuple(P2["socket"])] = "Skyy_Island_Portal_Socket"
    clear_players()
    place(WA, KT, ISL1)
    tick()
    K.eq(A.w[WA].blocks.get(tuple(P2["socket"])), "Skyy_Island_Hub_Portal", "PORTAL restart: the island file says repaired -> the pad is put back over a socket")
    # FIX (c): the portal=1 write was lost but the pad stands -> repaired, written again, never a dead pad
    fa = os.path.join(isl, KA + ".properties")
    ftxt = open(fa, encoding="utf-8").read()
    open(fa, "w", encoding="utf-8").write("".join(l + "\n" for l in ftxt.splitlines() if not l.startswith("portal")))
    St.reloadOne(KA)
    Life.ST.clear()
    K.check(not Life.portalOn(JString(KA), Life.state(WA)), "FIX(c) (set-up) island file without portal=1, fresh memory")
    place(WA, KT, (81.5, 134.1, 42.5))
    nh = len(A.kinds("hub"))
    A.t += 9000
    tick()
    K.check("portal=1" in open(fa, encoding="utf-8").read() and bool(Life.state(WA).portal) and len(A.kinds("hub")) == nh + 1,
            "FIX(c) the pad in the socket = repaired: portal=1 written again and the pad works in the same tick")
    clear_players()
    place(WA, KT, ISL1)
    # FIX (j): never a floating socket over an empty cell with nothing under it
    A.w["fresh"] = World(L)
    sk = tuple(P2["socket"])
    del A.w["fresh"].blocks[sk]
    K.eq(int(Life.portalBlocks(JString("fresh"), Life.state("fresh"), JString(KC), JLong(A.t))), 1, "FIX(j) an empty socket cell with ground under it -> the socket")
    K.eq(int(Life.portalBlocks(JString(WC), Life.state(WC), JString(KC), JLong(A.t))), 0, "FIX(j) an empty cell over the void -> nothing")
    del A.w["fresh"]
    # admin repair on island C-like fresh island: a second 3-island island owned by N
    KN_W = "skyy-island-" + KN
    wfile(KN, {"v": "5", "world": KN_W})
    St.reloadOne(KN)
    A.w[KN_W] = World(L)
    Life.ST.clear()
    place(KN_W, KN, ISL1)
    tick(KN_W)
    A.inv[KV] = {"Skyy_Hub_Shard": 1}
    A.admins.add(KV)
    A.t += 5000
    K.eq(str(Life.useSocket(JString(KN_W), uV, JLong(A.t))), "repaired", "PORTAL a server admin (not a member) may repair")
    A.admins.clear()
    K.check(not Life.usePad(JString(WC), uC, JLong(A.t + 99999)), "PORTAL a classic island has no portal (usePad -> 0)")
    # FIX (a): /island reset clears portal / portal.at / portal.by / isles (with kit) -> the new island is broken again, probed again
    fn_ = os.path.join(isl, KN + ".properties")
    K.check(all(x in open(fn_, encoding="utf-8").read() for x in ("portal=1", "isles=3", "portal.by=")), "FIX(a) (set-up) N's island repaired + isles=3")
    St.RESETTING.put(JString(KN), JArray(JObject)([JString("reset"), JInt(1)]))
    KN_W2 = KN_W + "-r1"
    K.eq(int(St.setWorldName0(JString(KN), JString(KN_W2))), 1, "FIX(a) setWorldName0 with a pending reset -> 1 (reset)")
    ntxt = open(fn_, encoding="utf-8").read()
    K.check(not [l for l in ntxt.splitlines() if l.split("=")[0] in ("portal", "portal.at", "portal.by", "isles", "kit")] and ("world=" + KN_W2) in ntxt,
            "FIX(a) the reset removed portal / portal.at / portal.by / isles / kit; world = the new one")
    St.reloadOne(KN)
    A.w[KN_W2] = World(L)
    Life.ST.clear()
    place(KN_W2, KN, ISL1)
    tick(KN_W2)
    K.check(A.w[KN_W2].blocks.get(tuple(P2["socket"])) == "Skyy_Island_Portal_Socket" and not Life.portalOn(JString(KN), Life.state(KN_W2))
            and "isles=3" in open(fn_, encoding="utf-8").read(), "FIX(a) the reset island: a broken socket (no free pad), probed and isles=3 again")
    Life.GOT.put(JString(KN), JLong(1))       # N got the first shard before the reset and spent it on the old island
    A.inv[KN] = {}
    Life.state(KN_W2).three = 1
    Life.onDeath(JString(KN_W2), JString("Golem_Crystal_Earth"), JString("reset-boss"), uN, JDouble(71.5), JDouble(34.5), JLong(A.t))
    ng = len(A.kinds("give"))
    A.drain()
    K.check([(e[1], e[3]) for e in A.kinds("give")[ng:]] == [(KN, 1)], "FIX(a)+(b) after a reset the owner gets a shard for the new portal")
    clear_players()
    # FIX (i): /hub from a home island known to be classic -> island:portal (SkyyQuests' portal step); never from a 3-island home
    Life.ST.clear()
    nq = len(A.kinds("quest"))
    K.check(not Life.classicTrip(uC), "FIX(i) classic home not probed yet this session -> nothing")
    Life.state(WC).three = 0
    K.check(bool(Life.classicTrip(uC)) and A.kinds("quest")[nq:] == [("quest", KC, "island:portal")], "FIX(i) classic home (probe said no) -> island:portal")
    Life.state(WA).three = 0
    nq = len(A.kinds("quest"))
    K.check(not Life.classicTrip(uA) and not Life.classicTrip(uB) and not A.kinds("quest")[nq:], "FIX(i) home file says isles=3 (owner + co-op) -> nothing")
    Life.ST.clear()
    # FIX (i): quest:caller:islands follows starter.design + boss.enabled
    SI = P("StarterIsles")
    Cfg.STARTER_DESIGN = "three"
    Cfg.BOSS_ON = True
    SI.publish()
    on1 = br.containsKey("quest:caller:islands")
    Cfg.BOSS_ON = False
    SI.publish()
    on2 = br.containsKey("quest:caller:islands")
    Cfg.BOSS_ON = True
    Cfg.STARTER_DESIGN = "classic"
    SI.publish()
    on3 = br.containsKey("quest:caller:islands")
    Cfg.STARTER_DESIGN = "three"
    SI.publish()
    K.check(on1 and not on2 and not on3 and br.containsKey("quest:caller:islands"), "FIX(i) quest:caller:islands only while 3 islands + mini boss on: %s" % [on1, on2, on3])
    # FIX (e): an unreadable hubshards.properties is kept as .bad
    badf = os.path.join(home, "bad", "hubshards.properties")
    os.makedirs(os.path.dirname(badf), exist_ok=True)
    open(badf, "wb").write(b"k=\\uZZZZ\n")
    K.eq(int(Life.loadGot(Paths.get(badf))), 0, "FIX(e) an unreadable hubshards.properties -> nobody known (warned)")
    K.check(os.path.isfile(badf + ".bad") and open(badf + ".bad", "rb").read() == open(badf, "rb").read(), "FIX(e) ... and it is kept as hubshards.properties.bad")
    K.check(int(Life.loadGot(Paths.get(got_file))) >= 4, "FIX(e) (back to the real file)")

    # ---------------------------------------------------------------- respawn
    R = lambda *a: int(Life.route(*a))
    K.eq([R(WA, WA, False, "hub", True), R("zone1", WA, False, "hub", True), R("zone1", WA, True, "hub", True), R("zone1", None, False, "hub", True),
          R("hub", None, False, "hub", True), R("zone1", None, True, "hub", True), R("zone1", WA, False, "hub", False), R(None, WA, False, "hub", True)],
         [0, 1, 0, 2, 0, 0, 0, 0],
         "RESPAWN route(): own island -> engine; elsewhere -> island; a bed where you died -> engine; no island -> hub; in the hub -> engine; off -> engine")
    clear_players()
    nh, nho = len(A.kinds("hub")), len(A.kinds("home"))
    place(WA, KB, ISL1)
    K.eq(int(Life.respawn(JString(WA), uB)), 0, "RESPAWN co-op member B died ON the co-op island -> nothing (the engine uses the island spawn / bed)")
    place("zone1", KB, (0.0, 100.0, 0.0))
    K.eq(int(Life.respawn(JString("zone1"), uB)), 1, "RESPAWN co-op member B died in a zone -> to the CO-OP island")
    K.eq(A.kinds("home")[-1], ("home", "zone1", KB, KA, WA), "RESPAWN goHome(zone1, B, A's key, A's world)")
    A.beds.add((KB, "zone1"))
    K.eq(int(Life.respawn(JString("zone1"), uB)), 0, "RESPAWN B has a bed in that zone -> left to vanilla")
    place(WC, KA, ISL1)
    K.eq(int(Life.respawn(JString(WC), uA)), 1, "RESPAWN owner A died on someone else's island -> home")
    place("zone1", KV, (0.0, 100.0, 0.0))
    K.eq(int(Life.respawn(JString("zone1"), uV)), 2, "RESPAWN no island yet -> the hub")
    place("hub", KV, (0.0, 100.0, 0.0))
    K.eq(int(Life.respawn(JString("hub"), uV)), 0, "RESPAWN no island, died in the hub -> nothing")
    K.eq(int(Life.respawn(JString("zone1"), uN)), -1, "RESPAWN not in that world any more -> -1")
    Cfg.RESPAWN_HOME = False
    K.eq(int(Life.respawn(JString("zone1"), uB)), 0, "RESPAWN islands.respawnHome off -> nothing")
    Cfg.RESPAWN_HOME = True
    # FIX (h): islands.respawnKeep - SkyyShards worlds and the zone islands keep their own respawn; the hub (default spawn) goes home
    for w_ in ("skyy-shard-" + KB, "skywynn_z1"):
        A.w[w_] = World({})
        place(w_, KB, (0.0, 100.0, 0.0))
    place("hub", KB, (0.0, 100.0, 0.0))
    K.eq([int(Life.respawn(JString("skyy-shard-" + KB), uB)), int(Life.respawn(JString("skywynn_z1"), uB)), int(Life.respawn(JString("hub"), uB))], [0, 0, 1],
         "FIX(h) a death in a shard world / a zone island -> their own respawn; in the hub -> home")
    Cfg.RESPAWN_KEEP = ""
    K.eq(int(Life.respawn(JString("skyy-shard-" + KB), uB)), 1, "FIX(h) islands.respawnKeep empty -> a shard death goes home too")
    Cfg.RESPAWN_KEEP = "skyy-shard-,skywynn_z"
    for w_ in ("skyy-shard-" + KB, "skywynn_z1"):
        del A.w[w_]
    A.w["hub"].players.clear()
    nho = len(A.kinds("home"))
    A.beds.clear()
    t5 = Task(5, JString("zone1"), uB)
    t5.run()
    K.check(len(A.queue) == 1, "RESPAWN IsleTask 5 (scheduler) queues mode 4 on the death world")
    A.drain()
    K.eq(len(A.kinds("home")), nho + 1, "RESPAWN ... which routes B home on that world's thread")

    # ---------------------------------------------------------------- tickAll + IO tasks
    clear_players()
    place(WA, KA, ISL1)
    place(WC, KC, ISL1)
    place("zone1", KB, (0.0, 100.0, 0.0))
    Life.QUEUED.clear()
    A.queue[:] = []
    K.eq(int(Life.tickAll()), 2, "TICK one task per ISLAND world with players (A, C; not the zone)")
    K.eq(int(Life.tickAll()), 0, "TICK never a second task while one is queued")
    A.drain()
    K.check(Life.QUEUED.isEmpty() and int(Life.tickAll()) == 2, "TICK after the tasks ran -> queued again")
    A.queue[:] = []
    Life.QUEUED.clear()

    # ---------------------------------------------------------------- useFlag + hooks (null paths) + code shape
    us = JClass("sun.misc.Unsafe")
    f_ = us.class_.getDeclaredField("theUnsafe")
    f_.setAccessible(True)
    U = f_.get(None)
    BTc = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    fid = BTc.class_.getDeclaredField("id")
    fid.setAccessible(True)
    ITY = JClass("com.hypixel.hytale.protocol.InteractionType")
    for bid in ("Skyy_Island_Portal_Socket", "Skyy_Island_Hub_Portal"):
        bt = U.allocateInstance(BTc.class_)
        fid.set(bt, JString(bid))
        K.eq(int(Perms.useFlag(bt, ITY.Use)), -1, "GUARD useFlag(%s, Use) = -1 (IsleUse handles it; visitors may use a repaired portal)" % bid)
    P("IsleDeath")().onComponentAdded(None, None, None, None)
    P("IsleRespawn")().onComponentRemoved(None, None, None, None)
    K.check(True, "HOOKS IsleDeath / IsleRespawn null paths return quietly")
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
    dc = code("IsleDeath", "onComponentAdded")
    K.check(0 <= dc.find("IslandStore.isIslandWorld") < dc.find("NPCEntity.getComponentType") < dc.find("Damage$EntitySource.getRef") < dc.find("IsleLife.petOwner") < dc.find("IsleLife.onDeath"),
            "SHAPE IsleDeath: island worlds only -> the NPC -> the killer (EntitySource; a pet -> its owner) -> IsleLife.onDeath")
    rc = code("IsleRespawn", "onComponentRemoved")
    K.check(0 <= rc.find("IslandCfg.RESPAWN_HOME") < rc.find("PlayerRef.getComponentType") < rc.find("IsleLife.respawnLater"), "SHAPE IsleRespawn: (setting on) the player -> respawnLater")
    K.check("Player.getComponentType" in code("IsleRespawn", "getQuery"), "SHAPE IsleRespawn queries players only")
    uc = code("IsleUse", "handle")
    K.check(0 <= uc.find("InteractionType.Use") < uc.find('"Skyy_Island_Portal_Socket"') < uc.find("IsleTask.<init>") < uc.find("IsleApi.exec"),
            "SHAPE IsleUse: Use only, our two blocks -> an IsleTask on the world thread")
    lc = code("IsleLife", "onDeath")
    K.check("IsleApi.exec" in lc and "IsleApi.give" not in lc and "IslandStore.setProps" not in lc, "SHAPE onDeath (inside the death system) only queues - no give, no file")
    sc = code("SkyyIslandsPlugin", "setup")
    K.check(all(x in sc for x in ("StarterIsles.publish", "IsleUse.<init>", "IsleDeath.<init>", "IsleRespawn.<init>", "IsleLife.loadGot", "hubshards.properties"))
            and "quest:caller:islands" not in sc, "SHAPE setup: StarterIsles.publish (puts quest:caller:islands), the 3 hooks, hubshards.properties")
    hc = code("HubCmd", "execute")
    K.check(0 <= hc.find("HubCmd.sendToHub") < hc.find("IsleLife.classicTrip"), "SHAPE /hub: after a successful send -> IsleLife.classicTrip")
    K.check("profile:busy:" in code("IsleLife", "busy") and "IsleLife.busy" in code("IsleLife", "grant") and "IsleLife.busy" in code("IsleLife", "useSocket"),
            "SHAPE profile:busy checked before every Hub Shard move (grant, repair)")
    K.check("quest:caller:islands" in code("SkyyIslandsPlugin", "shutdown"), "SHAPE shutdown removes quest:caller:islands")
    for meth in ("spawn", "level", "goHome", "toHub", "quest"):
        K.check(len(code("IsleEng", meth)) > 0, "SHAPE IsleEng.%s exists" % meth)
    sp_ = code("IsleEng", "spawn")
    K.check("NPCPlugin.spawnNPC" in sp_ and "Pair.first" in sp_, "SHAPE IsleEng.spawn = NPCPlugin.spawnNPC (the SkyyMerchants / SkyyQuests call shape)")
    K.check("mob:fn:setLevel" in code("IsleEng", "level") and "Nameplate" in code("IsleEng", "level"), "SHAPE IsleEng.level: mob:fn:setLevel, else the Nameplate")
    K.check("SendHubTask.now" in code("IsleEng", "toHub") and "IslandSnd.arm" in code("IsleEng", "toHub"), "SHAPE IsleEng.toHub = the /hub path + portal sound")

    # ---------------------------------------------------------------- the jar's files
    z = zipfile.ZipFile(jar)
    names = set(z.namelist())
    items = dict((n_.rsplit("/", 1)[1][:-5], json.loads(z.read(n_))) for n_ in names if n_.startswith("Server/Item/Items/SkyyIslands/"))
    K.eq(sorted(items), ["Skyy_Hub_Shard", "Skyy_Island_Hub_Portal", "Skyy_Island_Portal_Socket"], "JAR 3 new items")
    K.check("BlockType" not in items["Skyy_Hub_Shard"] and items["Skyy_Hub_Shard"]["Icon"] == "Icons/ItemsGenerated/Skyy_Hub_Shard.png"
            and "Common/Icons/ItemsGenerated/Skyy_Hub_Shard.png" in names, "JAR the Hub Shard: a plain item (cannot be placed) + its icon")
    for b in ("Skyy_Island_Portal_Socket", "Skyy_Island_Hub_Portal"):
        bt = items[b]["BlockType"]
        K.check(bt["Gathering"]["Breaking"]["GatherType"] == "Unbreakable" and "Use" in bt["Interactions"] and "Recipe" not in items[b] and "Parent" not in items[b],
                "JAR %s: unbreakable, F-usable, no recipe, no parent" % b)
    lang = z.read("Server/Languages/en-US/server.lang").decode("utf-8")
    K.check("items.Skyy_Hub_Shard.name=Hub Shard" in lang and "server.items.Skyy_Island_Hub_Portal.name=Hub Portal" in lang, "JAR names in server.lang")
    K.check(not [n_ for n_ in names if n_.lower().endswith(".ui")], "JAR no .ui file")
    Life.API = None
    K.save()


def run_live2(out, jar, scratch, home):
    """D = the 0.5.8 start-twice phase + the 0.5.12 config / hubshards load on the same scratch COPY of the live Skyy_SkyyIslands (one JVM)"""
    from jpype import JClass
    T58.run_live(out, jar, scratch, home)          # starts the JVM (server jar + this jar, -Xverify:all) and writes its own result
    K = HK.Child(out + ".p2.json")
    Cfg, Life, Paths = JClass(PKG + "IslandCfg"), JClass(PKG + "IsleLife"), JClass("java.nio.file.Paths")
    h0 = HK.tree_hash(home)
    for start in (1, 2):
        cf = os.path.join(home, "config.properties")
        if os.path.isfile(cf):
            Cfg.FILE = Paths.get(cf)
            Cfg.load("")
        n = int(Life.loadGot(Paths.get(os.path.join(home, "hubshards.properties"))))
        K.check(HK.tree_hash(home) == h0, "D2 start %d: config + hubshards load on the live copy write nothing (%d first shards known; camp %s, respawnHome %s)"
                % (start, n, bool(Cfg.CAMP_ON), bool(Cfg.RESPAWN_HOME)))
    K.save()
    d = json.load(open(out + ".p2.json"))
    e = json.load(open(out))
    e["ok"] += d["ok"]
    e["fails"] += d["fails"]
    e["notes"] += d.get("notes", [])
    json.dump(e, open(out, "w"), indent=1)


def run_s3m(out, jar, scratch, home):
    K = HK.Child(out)
    T511.mouth_checks(K, T511.layout_of(VERSION), T511.layout_of("0.5.10"))
    K.save()
    T510.run_s3(out + ".s3.json", jar, scratch, home)
    d = json.load(open(out + ".s3.json"))
    e = json.load(open(out))
    e["ok"] += d["ok"]
    e["fails"] += d["fails"]
    e["notes"] += d.get("notes", [])
    json.dump(e, open(out, "w"), indent=1)


if __name__ == "__main__":
    print("S. real-server phase: NOT RUN in this round (no server start allowed) - UNVERIFIED in game")
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("p2", run_p2), ("s3", run_s3m), ("snd", T59.run_snd), ("exec", T58.run_exec), ("live", run_live2)],
           script=__file__, live=(T58.LIVE_DIR, "Skyy_SkyyIslands"))
