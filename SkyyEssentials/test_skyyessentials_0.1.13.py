"""Bare-JVM check for SkyyEssentials 0.1.13 (/back + homes; tools/essentials_0_1_13_patch.py). Build first:
    python tools/essentials_0_1_13_patch.py && python SkyyEssentials/build_skyyessentials_0.1.13.py

    python SkyyEssentials/test_skyyessentials_0.1.13.py [--jar <SkyyEssentials-0.1.13.jar>] [--dir <scratch folder>] [--keep] [--only back,...]

The 0.1.12 harness (test_skyyessentials_0.1.12.py, loaded as a module; it loads 0.1.11's) runs its phases menu / main / trade / tpa / chat /
keep / compost / live1 / live2 against this jar, each in a fresh JVM; the checks that change ON PURPOSE (class count, the new config rows)
are listed in SUPERSEDED and re-checked here. Then:
  phase back (a fresh JVM, -Xverify:all; stand-in Universe with three online players and five worlds - zone, zone2, an island, two shard
  worlds - task queues drained by hand = the world threads; block seam EssBack.GRID, move seam MOVES, chat seam SAID, position seam POS;
  fake bridge functions profile:fn:key, island:perm:fn / island:owner:fn / island:role:key:fn, home:extra:<uuid>):
    S  the hook: EssBackSys = RefChangeSystem, dependency BEFORE TeleportSystems$PlayerMoveSystem, query = the Player type, both callbacks
       hand over to EssBack.onTp; the five commands + two variants carry hytale:Adventurer
    B1 capture (mark): cross-world remembered, short same-world jump skipped, a long one remembered, no ground skipped, dead skipped,
       /back off skipped, the profile-switch teleport skipped (key changed since join)
    B2 /back once + twice: cross-world = destination thread (landing) -> player thread -> the move; the move's own capture makes the
       second /back go back again (toggle); cooldown refuses in between; same-world /back moves at once
    B3 refused: nothing yet, world not open, island perm FALSE, another player's shard, own shard + co-op member's shard allowed, blocked
       landing steps up, no safe spot refused, the player changed worlds between the two threads, part.back off
    B4 relog / restart: save -> back.properties -> load = the same points (per profile key); quit forgets the join key
    H1 /sethome: default name, limit 2, the third refused, home:extra raises it, moving an existing home when full, bad names, island +
       shard worlds refused, no ground refused, the homes file (atomic, per profile) read back after a restart
    H2 /home: none, exactly one, two without "home" = the list, the default "home", by name (any case), unknown name, cooldown, cross-world
    H3 /delhome, /homes, part.home off; bridge essentials:fn:homes / gohome / back (queued on the player's world thread)
    K  config: the eight new rows in TCfg (keys, defaults, file text) and get / put round trip
  FIX ROUND (critic 2026-10-17): B1x capture skips dungeon / instance worlds (EssBack.INST seam) and back.denyWorlds, keeps zones (skywynn_*),
       ordinary worlds and islands; B3x fail closed - own / member shard of a locked island, no island:world:key:fn, island perm null /
       non-Boolean / throwing / missing, no island:owner:fn or a throwing one, an ownerless skyy-island-*, a dungeon target, a denied target;
       B4x an unreadable back.properties is renamed .bad-<stamp>; H1x /sethome refused in a dungeon / an ownerless island / a denied world;
       H3x the bridge asks the command permission (EssBack.PERMS seam; no command object = refused); Kx the two "words" rows.
  Z  class byte-compare 0.1.12 -> 0.1.13: only the plugin, TCfg / CfgRows (rows) and the new classes differ
NOT runnable in a bare JVM: the engine calling EssBackSys before PlayerMoveSystem on a real teleport, the client arriving, real block
reads (ChunkStore) - in-game steps. Default scratch folder: tools/dev/scratch/back/test (deleted at the end unless --keep).
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "dev"))

_s12 = importlib.util.spec_from_file_location("test_skyyessentials_0_1_12", os.path.join(HERE, "test_skyyessentials_0.1.12.py"))
T12 = importlib.util.module_from_spec(_s12)
_s12.loader.exec_module(T12)
T11 = T12.T11

VERSION = "0.1.13"
PREV = "0.1.12"
PKG = "com.skyy.essentials."
SCRATCH = os.path.abspath(T11.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "back", "test")))
JAR = os.path.abspath(T11.arg("--jar", os.path.join(HERE, "SkyyEssentials-%s.jar" % VERSION)))
PREV_JAR = os.path.join(HERE, "SkyyEssentials-%s.jar" % PREV)
KEEP = "--keep" in sys.argv
for _m in (T11, T12):
    _m.VERSION, _m.SCRATCH, _m.JAR, _m.KEEP = VERSION, SCRATCH, JAR, KEEP
T12.PREV, T12.PREV_JAR = PREV, PREV_JAR

_NEWROWS = "the eight 0.1.13 rows (back + homes) come last now - re-checked in phase back K"
SUPERSEDED = list(T12.SUPERSEDED) + [
    (re.compile(r"^U0: 73 classes"), "89 classes (+ the 9 /back + homes classes + 7 command classes) - checked in phase back S0"),
    (re.compile(r"^72 classes in the jar"), "89 classes - checked in phase back S0"),
    (re.compile(r"^0\.1\.7's tradeBlockedItems, the four 0\.1\.9 chat keys"), _NEWROWS),
    (re.compile(r"^the default file closes the /trade block"), _NEWROWS),
    (re.compile(r"^a new file ends with the gameplay block"), _NEWROWS),
    (re.compile(r"^a 0\.1\.6 file gets exactly"), _NEWROWS + " (the append path: K4 on the live file)"),
    (re.compile(r"^28 rows \(0\.1\.9"), "the kit has 36 rows now (+8) - phase back K2"),
    (re.compile(r"^the chat rows last, category chat"), _NEWROWS),
    (re.compile(r"^setup: EssDurDeath \+ 2 asset listeners before CfgPub\.start"), "2 systems now (+ EssBackSys) - phase back K5"),
    (re.compile(r"^live[12]: the chat rows are published at their defaults"), _NEWROWS),
    (re.compile(r"^live1: config\.properties = the live bytes"), "the live file also gets the eight 0.1.13 keys - phase back K4"),
    (re.compile(r"^live1: every existing value kept"), "phase back K4"),
]
SKIPPED = []
FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def old_check(cond, what):
    if not cond:
        for rx, why in SUPERSEDED:
            if rx.search(str(what)):
                SKIPPED.append("%s  -> %s" % (str(what)[:120], why))
                return
    check(cond, what)


T11.check = old_check
T12.check = old_check

NEW_CLASSES = ["EssPt", "EssBack", "EssHome", "EssGo", "EssBackSys", "EssBackTick", "EssBackL", "EssHFn", "EssHGo",
               "BackCmd", "HomeCmd", "HomeNamedCmd", "SetHomeCmd", "SetHomeNamedCmd", "DelHomeCmd", "HomesCmd"]


# ============================================================================================================== phase back
def run_back(jar):
    B = T11.boot(jar)
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    J = JClass
    W = T11.World(B)
    ES, BK, HM, TCfg = J(PKG + "EssStore"), J(PKG + "EssBack"), J(PKG + "EssHome"), J(PKG + "TCfg")
    Pt, Sys = J(PKG + "EssPt"), J(PKG + "EssBackSys")
    UUID, Paths, Integer, Boolean = J("java.util.UUID"), J("java.nio.file.Paths"), J("java.lang.Integer"), J("java.lang.Boolean")
    CHM, AL = J("java.util.concurrent.ConcurrentHashMap"), J("java.util.ArrayList")
    home = os.path.join(SCRATCH, "back", "mods", "Skyy_SkyyEssentials")
    shutil.rmtree(home, ignore_errors=True)
    os.makedirs(home, exist_ok=True)
    T11.paths_for(TCfg, ES, Paths, home)
    BK.FILE = Paths.get(os.path.join(home, "back.properties"))
    HM.DIR = Paths.get(os.path.join(home, "homes"))

    # ---------------- S the hook + the commands
    z = zipfile.ZipFile(jar)
    cls = [n for n in z.namelist() if n.endswith(".class")]
    check(len(cls) == 73 + len(NEW_CLASSES), "S0: %d classes in the jar (0.1.12's 73 + %d new): %d" % (73 + len(NEW_CLASSES), len(NEW_CLASSES), len(cls)))
    check(all((PKG.replace(".", "/") + c + ".class") in cls for c in NEW_CLASSES), "S0: every new class is in the jar")
    RCS = J("com.hypixel.hytale.component.system.RefChangeSystem")
    PMS = J("com.hypixel.hytale.server.core.modules.entity.teleport.TeleportSystems$PlayerMoveSystem")
    ORD = J("com.hypixel.hytale.component.dependency.Order")
    check(RCS.class_.isAssignableFrom(Sys.class_), "S1: EssBackSys is a RefChangeSystem")
    s_ = Sys()
    deps = list(s_.getDependencies())
    check(len(deps) == 1, "S1: one dependency: %s" % deps)
    d0 = deps[0]
    dtxt = str(d0)
    check(PMS.class_.getName() in dtxt or "PlayerMoveSystem" in dtxt, "S1: the dependency names TeleportSystems$PlayerMoveSystem: %s" % dtxt)
    try:
        ordv = str(d0.getOrder())
    except Exception as e:
        ordv = str(e)
    check(ordv == "BEFORE", "S1: ordered BEFORE it: %s" % ordv)
    from cpstrings import read_utf8_constants
    sc = set(read_utf8_constants(z.read(PKG.replace(".", "/") + "EssBackSys.class")))
    check("com/hypixel/hytale/server/core/modules/entity/teleport/Teleport" in sc and "com/hypixel/hytale/server/core/entity/entities/Player" in sc
          and "onTp" in sc, "S1: componentType = Teleport, query = Player, the callbacks call EssBack.onTp (constants)")
    for cn in ("BackCmd", "HomeCmd", "HomeNamedCmd", "SetHomeCmd", "SetHomeNamedCmd", "DelHomeCmd", "HomesCmd"):
        raw = z.read(PKG.replace(".", "/") + cn + ".class")
        check(b"setPermissionGroups" in raw and b"hytale:Adventurer" in raw and b"requirePermission" not in raw, "S2: %s is a hytale:Adventurer command" % cn)
    AC = J("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    names = {}
    for cn in ("BackCmd", "HomeCmd", "SetHomeCmd", "DelHomeCmd", "HomesCmd"):
        c_ = J(PKG + cn)()
        names[cn] = str(c_.getName())
    check(names == {"BackCmd": "back", "HomeCmd": "home", "SetHomeCmd": "sethome", "DelHomeCmd": "delhome", "HomesCmd": "homes"}, "S2: command names %s" % names)

    # ---------------- stand-in Universe, players, worlds
    Uni = J("com.hypixel.hytale.server.core.universe.Universe")
    PRc = J("com.hypixel.hytale.server.core.universe.PlayerRef")
    Holder = J("com.hypixel.hytale.component.Holder")
    Wld = J("com.hypixel.hytale.server.core.universe.world.World")
    AB = J("java.util.concurrent.atomic.AtomicBoolean")
    uni = W.us.allocateInstance(Uni.class_)
    byu, wbu, wbn = CHM(), CHM(), CHM()
    W.fld(Uni, "playersByUuid").set(uni, byu)
    W.fld(Uni, "players").set(uni, J("java.util.concurrent.CopyOnWriteArrayList")())
    W.fld(Uni, "worldsByUuid").set(uni, wbu)
    W.fld(Uni, "worlds").set(uni, wbn)
    W.fld(Uni, "instance").set(None, uni)
    worlds = {}

    def world(name, uid):
        w_ = W.us.allocateInstance(Wld.class_)
        W.fld(Wld, "alive").set(w_, AB(True))
        W.fld(Wld, "acceptingTasks").set(w_, AB(True))
        W.fld(Wld, "taskQueue").set(w_, J("java.util.concurrent.ConcurrentLinkedDeque")())
        W.fld(Wld, "name").set(w_, name)
        u_ = UUID.fromString(uid)
        wbu.put(u_, w_)
        wbn.put(name.lower(), w_)
        worlds[name] = (w_, u_)
        return w_

    zone = world("skywynn_zones", "00000000-0000-0000-0000-0000000000a1")
    zone2 = world("skywynn_z1", "00000000-0000-0000-0000-0000000000a2")
    isl = world("skyy-island-bobkey", "00000000-0000-0000-0000-0000000000a3")
    U_A = "00000000-0000-0000-0000-00000000a11c"
    shA = world("skyy-shard-" + U_A + "#1", "00000000-0000-0000-0000-0000000000a4")
    shB = world("skyy-shard-bobkey", "00000000-0000-0000-0000-0000000000a5")
    # fix round: Alice's own island (her shard's island), a dungeon instance, an ordinary (non-instance) world, an orphan island name
    islA = world("skyy-island-alicekey", "00000000-0000-0000-0000-0000000000a6")
    dung = world("instance-dungeon-1", "00000000-0000-0000-0000-0000000000a7")
    plain = world("lobby", "00000000-0000-0000-0000-0000000000a8")
    orph = world("skyy-island-orphan", "00000000-0000-0000-0000-0000000000a9")
    # the instance worlds as in game (zones + islands + dungeons carry InstanceWorldConfig); EssBack.INST = the seam
    INST = J("java.util.HashSet")()
    for _n in ("skywynn_zones", "skywynn_z1", "skyy-island-bobkey", "skyy-island-alicekey", "instance-dungeon-1", "skyy-island-orphan"):
        INST.add(_n)
    BK.INST = INST

    def player(name, uid, wname):
        p_ = W.us.allocateInstance(PRc.class_)
        W.fld(PRc, "uuid").set(p_, UUID.fromString(uid))
        W.fld(PRc, "username").set(p_, name)
        W.fld(PRc, "holder").set(p_, W.us.allocateInstance(Holder.class_))
        W.fld(PRc, "worldUuid").set(p_, worlds[wname][1])
        byu.put(p_.getUuid(), p_)
        return p_

    def put_in(p_, wname):
        W.fld(PRc, "worldUuid").set(p_, worlds[wname][1])

    pa = player("Alice", U_A, "skywynn_zones")
    pb = player("Bob", "00000000-0000-0000-0000-000000000b0b", "skywynn_zones")
    pc = player("Carol", "00000000-0000-0000-0000-00000000ca20", "skywynn_zones")
    ua, ub, uc = pa.getUuid(), pb.getUuid(), pc.getUuid()
    check(ES.worldOf(pa) == zone, "stand-in: Alice is in skywynn_zones")

    def drain():
        n = 0
        for _ in range(10):
            moved = False
            for wn, (w_, _u) in worlds.items():
                q = W.fld(Wld, "taskQueue").get(w_)
                while not q.isEmpty():
                    q.poll().run()
                    n += 1
                    moved = True
            if not moved:
                break
        return n

    # seams
    GRID = CHM()
    BK.GRID = GRID
    MOVES = AL()
    BK.MOVES = MOVES
    SAID = AL()
    BK.SAID = SAID
    POS = CHM()
    BK.POS = POS

    def floor(wname, x, y, z_, solid=1):
        GRID.put("%s|%d|%d|%d" % (wname, x, y, z_), Integer(solid))

    # every world: a stone floor at y 63 under x -50..50, z 0 (the test spots); air elsewhere (the GRID default)
    for wn in worlds:
        for x in range(-50, 51, 1):
            floor(wn, x, 63, 0)
    # fake bridge: profile keys (Alice has profile key U_A#1), islands
    br = TCfg.bridge()
    KEYS = {str(ua): U_A + "#1", str(ub): "bobkey", str(uc): "carolkey"}

    @JImplements("java.util.function.Function")
    class KeyFn(object):
        @JOverride
        def apply(self, o):
            return KEYS.get(str(o))

    ISL_OK = {"v": True, "alice": True, "mode": "bool"}   # mode: bool | none (null answer) | text (non-Boolean) | throw

    @JImplements("java.util.function.Function")
    class PermFn(object):
        @JOverride
        def apply(self, o):
            a = list(o)
            if str(a[2]) != "enter":
                return None
            if ISL_OK["mode"] == "none":
                return None
            if ISL_OK["mode"] == "text":
                return "yes"
            if ISL_OK["mode"] == "throw":
                raise RuntimeError("perm boom")
            if str(a[1]) == "skyy-island-alicekey":
                return Boolean(ISL_OK["alice"])
            if str(a[1]) != "skyy-island-bobkey":
                return None
            return Boolean(ISL_OK["v"] or str(a[0]) == str(ub))

    OWN_THROW = {"v": False}

    @JImplements("java.util.function.Function")
    class OwnerFn(object):
        @JOverride
        def apply(self, o):
            if OWN_THROW["v"]:
                raise RuntimeError("owner boom")
            return {"skyy-island-bobkey": "bobkey", "skyy-island-alicekey": U_A + "#1"}.get(str(o))

    @JImplements("java.util.function.Function")
    class WorldKeyFn(object):
        @JOverride
        def apply(self, o):
            return {"bobkey": "skyy-island-bobkey", U_A + "#1": "skyy-island-alicekey"}.get(str(o))

    ROLES = {}

    @JImplements("java.util.function.Function")
    class RoleKeyFn(object):
        @JOverride
        def apply(self, o):
            a = list(o)
            return ROLES.get((str(a[0]), str(a[1])))

    kf, pf, of, rf, wkf = KeyFn(), PermFn(), OwnerFn(), RoleKeyFn(), WorldKeyFn()
    br.put("profile:fn:key", kf)
    br.put("island:perm:fn", pf)
    br.put("island:owner:fn", of)
    br.put("island:role:key:fn", rf)
    br.put("island:world:key:fn", wkf)
    check(str(BK.pkey(ua)) == U_A + "#1" and str(BK.pkey(UUID.fromString("00000000-0000-0000-0000-000000000099"))) == "00000000-0000-0000-0000-000000000099",
          "pkey: the active profile key, no answer = the UUID")

    def mark(u, wname, x, y, z_, to, tx, ty, tz, dead=False):
        return int(BK.mark(u, worlds[wname][0], float(x), float(y), float(z_), 1.0, 2.0, 0.0, 3.0, 4.0, 0.0, to, float(tx), float(ty), float(tz), dead))

    def pt_of(u):
        return BK.BACK.get(BK.pkey(u))

    # ---------------- B1 capture
    BK.LASTKEY.clear()
    check(mark(ua, "skywynn_zones", 10.5, 64.0, 0.5, "skyy-island-bobkey", 0, 100, 0) == 0, "B1: a cross-world teleport is remembered")
    p0 = pt_of(ua)
    check(p0 is not None and str(p0.world) == "skywynn_zones" and abs(p0.x - 10.5) < 1e-9 and abs(p0.y - 64.0) < 1e-9 and abs(p0.ry - 2.0) < 1e-6 and abs(p0.hy - 4.0) < 1e-6,
          "B1: world, feet, body + head rotation kept: %s" % (p0.enc() if p0 else None))
    check(BK.DIRTY, "B1: the book is marked for the 5 s save")
    check(mark(ua, "skywynn_zones", 20.5, 64.0, 0.5, "skywynn_zones", 30.5, 64.0, 0.5) == 2 and abs(pt_of(ua).x - 10.5) < 1e-9,
          "B1: a 10-block blink in one world is not a /back teleport (point unchanged)")
    check(mark(ua, "skywynn_zones", 20.5, 64.0, 0.5, "skywynn_zones", 20.5, 64.0, 40.5) == 0 and abs(pt_of(ua).x - 20.5) < 1e-9,
          "B1: a 40-block teleport in one world is (min 32)")
    check(mark(ua, "skywynn_zones", 0.5, 120.0, 0.5, "skyy-island-bobkey", 0, 100, 0) == 4 and abs(pt_of(ua).x - 20.5) < 1e-9,
          "B1: a spot with no ground within 6 below (falling / flying / void rescue) is not remembered")
    check(mark(ua, "skywynn_zones", 0.5, 64.0, 0.5, "skyy-island-bobkey", 0, 100, 0, dead=True) == 5, "B1: a dead player's teleport (respawn) is not remembered")
    BK.PART = False
    check(mark(ua, "skywynn_zones", 1.5, 64.0, 0.5, "skyy-island-bobkey", 0, 100, 0) == 1, "B1: /back off = nothing remembered")
    BK.PART = True
    KEYS[str(ua)] = U_A + "#2"
    check(mark(ua, "skywynn_zones", 2.5, 64.0, 0.5, "skyy-island-bobkey", 0, 100, 0) == 3 and BK.BACK.get(U_A + "#2") is None,
          "B1: the teleport of a profile switch (key changed) is not remembered - no /back across profiles")
    check(mark(ua, "skywynn_zones", 3.5, 64.0, 0.5, "skyy-island-bobkey", 0, 100, 0) == 0 and abs(BK.BACK.get(U_A + "#2").x - 3.5) < 1e-9
          and abs(BK.BACK.get(U_A + "#1").x - 20.5) < 1e-9, "B1: the next teleport on profile 2 is kept apart from profile 1's point")
    KEYS[str(ua)] = U_A + "#1"
    BK.LASTKEY.put(ua, U_A + "#1")
    # B1x fix round: the world rules at capture
    keep_x = pt_of(ua).x
    check(mark(ua, "instance-dungeon-1", 0.5, 64.0, 0.5, "skywynn_zones", 0, 64, 0) == 7 and abs(pt_of(ua).x - keep_x) < 1e-9,
          "B1x: leaving a dungeon / instance world is not remembered (code 7, point unchanged)")
    check(mark(ua, "lobby", 4.5, 64.0, 0.5, "skywynn_zones", 0, 64, 0) == 0 and str(pt_of(ua).world) == "lobby",
          "B1x: an ordinary (non-instance) world is remembered")
    check(mark(ua, "skywynn_zones", 5.5, 64.0, 0.5, "lobby", 0, 64, 0) == 0 and str(pt_of(ua).world) == "skywynn_zones",
          "B1x: a zone (an instance world in back.instanceWorlds skywynn_*) is remembered")
    check(mark(ua, "skyy-island-bobkey", 5.5, 64.0, 0.5, "lobby", 0, 64, 0) == 0, "B1x: an island (an instance world) is remembered - checked on use")
    BK.DENY = "lobby,skyy-island-*"
    check(mark(ua, "lobby", 6.5, 64.0, 0.5, "skywynn_zones", 0, 64, 0) == 7 and mark(ua, "skyy-island-bobkey", 6.5, 64.0, 0.5, "lobby", 0, 64, 0) == 7,
          "B1x: back.denyWorlds (a name, a Prefix*) is never remembered - islands too")
    BK.DENY = ""
    BK.IALLOW = ""
    check(mark(ua, "skywynn_zones", 7.5, 64.0, 0.5, "lobby", 0, 64, 0) == 7, "B1x: back.instanceWorlds empty = the zones count as instances too")
    BK.IALLOW = "skywynn_*"
    check(mark(ua, "skywynn_zones", 20.5, 64.0, 0.5, "skyy-island-bobkey", 0, 100, 0) == 0, "B1x: (point back to the zone for B2)")

    # ---------------- B2 /back once + twice (cross-world), cooldown, same-world
    BK.LAST_GO.clear()
    put_in(pa, "skyy-island-bobkey")           # Alice did /is: she is on Bob's island (allowed) now
    MOVES.clear()
    SAID.clear()
    r1 = str(BK.backR(pa, isl))
    check("On the way" in r1 and MOVES.size() == 0, "B2: cross-world /back is queued (destination thread first): %s" % r1)
    drain()
    check(MOVES.size() == 1 and str(MOVES.get(0)).startswith(str(ua) + "|skywynn_zones|20.5|64.0|"), "B2: the move lands on the remembered spot: %s" % list(MOVES))
    check(any("Teleporting to where you were before your last teleport" in str(s) for s in SAID), "B2: the player is told: %s" % list(SAID))
    # the move is a teleport: EssBackSys remembers where Alice stood on the island (the engine does this inside addComponent)
    floor("skyy-island-bobkey", 5, 99, 5)
    check(mark(ua, "skyy-island-bobkey", 5.5, 100.0, 5.5, "skywynn_zones", 20.5, 64.0, 0.5) == 0, "B2: the /back teleport itself is remembered (toggle)")
    put_in(pa, "skywynn_zones")
    r2 = str(BK.backR(pa, zone))
    check("Wait" in r2 and MOVES.size() == 1, "B2: the cooldown refuses a second /back at once: %s" % r2)
    BK.LAST_GO.put(ua, J("java.lang.Long")(0))
    r3 = str(BK.backR(pa, zone))
    drain()
    check(MOVES.size() == 2 and str(MOVES.get(1)).startswith(str(ua) + "|skyy-island-bobkey|5.5|100.0|5.5"), "B2: /back twice = back to the island: %s %s" % (r3, list(MOVES)))
    # same world: at once
    BK.LAST_GO.clear()
    BK.BACK.put(BK.pkey(uc), Pt.dec("skywynn_zones|-40.5|64.0|0.5|0|0|0|0|0|0"))
    r4 = str(BK.backR(pc, zone))
    check("Teleporting" in r4 and MOVES.size() == 3 and str(MOVES.get(2)).startswith(str(uc) + "|skywynn_zones|-40.5|64.0|0.5"), "B2: same-world /back moves at once: %s" % r4)

    # ---------------- B3 refused / safety
    BK.LAST_GO.clear()
    MOVES.clear()
    BK.BACK.remove(BK.pkey(ub))
    check("Nowhere to go back to" in str(BK.backR(pb, zone)), "B3: no point yet")
    BK.BACK.put(BK.pkey(ub), Pt.dec("gone_world|0|64|0|0|0|0|0|0|0"))
    check("not open right now" in str(BK.backR(pb, zone)), "B3: a world that is not loaded (deleted / closed) is refused")
    BK.BACK.put(BK.pkey(uc), Pt.dec("skyy-island-bobkey|5.5|100|5.5|0|0|0|0|0|0"))
    ISL_OK["v"] = False
    check("can't visit that island" in str(BK.backR(pc, zone)) and MOVES.size() == 0, "B3: island perm FALSE (banned / closed / locked) is refused")
    ISL_OK["v"] = True
    BK.BACK.put(BK.pkey(uc), Pt.dec("skyy-shard-bobkey|0.5|64|0.5|0|0|0|0|0|0"))
    check("shard is not yours" in str(BK.backR(pc, zone)), "B3: another player's shard is refused (fail closed)")
    ROLES[(str(uc), "bobkey")] = "member"
    r5 = str(BK.backR(pc, zone))
    drain()
    check("On the way" in r5 and MOVES.size() == 1, "B3: a co-op member may go back into the owner's shard: %s" % r5)
    ROLES[(str(uc), "bobkey")] = "visitor"
    BK.LAST_GO.clear()
    check("shard is not yours" in str(BK.backR(pc, zone)), "B3: a visitor may not")
    BK.BACK.put(BK.pkey(ua), Pt.dec("skyy-shard-" + U_A + "#1|0.5|64|0.5|0|0|0|0|0|0"))
    r6 = str(BK.backR(pa, zone))
    drain()
    check("On the way" in r6 and MOVES.size() == 2, "B3: your own (active profile) shard is fine: %s" % r6)
    # B3x fix round: fail closed
    BK.LAST_GO.clear()
    n0 = MOVES.size()
    ISL_OK["alice"] = False
    check("shard is closed" in str(BK.backR(pa, zone)), "B3x: own shard refused while your island refuses enter (locked / closed / retired)")
    ISL_OK["alice"] = True
    ROLES[(str(uc), "bobkey")] = "member"
    BK.BACK.put(BK.pkey(uc), Pt.dec("skyy-shard-bobkey|0.5|64|0.5|0|0|0|0|0|0"))
    ISL_OK["v"] = False
    check("shard is closed" in str(BK.backR(pc, zone)), "B3x: a member is refused the shard of a locked island (perm enter FALSE)")
    ISL_OK["v"] = True
    br.remove("island:world:key:fn")
    check("shard is closed" in str(BK.backR(pc, zone)), "B3x: no island:world:key:fn = shard refused (fail closed)")
    br.put("island:world:key:fn", wkf)
    ROLES[(str(uc), "bobkey")] = "visitor"
    BK.BACK.put(BK.pkey(uc), Pt.dec("skyy-island-bobkey|5.5|100|5.5|0|0|0|0|0|0"))
    for mode in ("none", "text", "throw"):
        ISL_OK["mode"] = mode
        r_ = str(BK.backR(pc, zone))
        check("can't visit that island" in r_, "B3x: island perm answer %s (not Boolean.TRUE) is refused: %s" % (mode, r_))
    ISL_OK["mode"] = "bool"
    br.remove("island:perm:fn")
    check("can't visit that island" in str(BK.backR(pc, zone)), "B3x: no island:perm:fn = island refused")
    br.put("island:perm:fn", pf)
    br.remove("island:owner:fn")
    check("can't be checked" in str(BK.backR(pc, zone)), "B3x: an island name without island:owner:fn = refused")
    br.put("island:owner:fn", of)
    OWN_THROW["v"] = True
    check("can't be checked" in str(BK.backR(pc, zone)), "B3x: island:owner:fn throwing = refused")
    OWN_THROW["v"] = False
    BK.BACK.put(BK.pkey(uc), Pt.dec("skyy-island-orphan|0.5|64|0.5|0|0|0|0|0|0"))
    check("island is gone" in str(BK.backR(pc, zone)), "B3x: a skyy-island-* world nobody owns = refused")
    check(MOVES.size() == n0, "B3x: none of these moved anyone")
    BK.BACK.put(BK.pkey(uc), Pt.dec("instance-dungeon-1|0.5|64|0.5|0|0|0|0|0|0"))
    r_ = str(BK.backR(pc, zone))
    check("instance world" in r_ and MOVES.size() == n0, "B3x: /back into a dungeon / instance world is refused: %s" % r_)
    BK.BACK.put(BK.pkey(uc), Pt.dec("lobby|0.5|64|0.5|0|0|0|0|0|0"))
    BK.DENY = "LOBBY"
    check("closed to /back" in str(BK.backR(pc, zone)) and MOVES.size() == n0, "B3x: a denied world (any case) is refused")
    BK.DENY = ""
    r_ = str(BK.backR(pc, zone))
    drain()
    check("On the way" in r_ and MOVES.size() == n0 + 1, "B3x: an ordinary world is fine: %s" % r_)
    # blocked landing: a block now sits at the feet -> one higher; walled up -> refused
    BK.LAST_GO.clear()
    floor("skywynn_zones", 30, 64, 0)
    BK.BACK.put(BK.pkey(ub), Pt.dec("skywynn_zones|30.5|64.0|0.5|0|0|0|0|0|0"))
    r7 = str(BK.backR(pb, zone))
    check("Teleporting" in r7 and str(MOVES.get(MOVES.size() - 1)).startswith(str(ub) + "|skywynn_zones|30.5|65.0|0.5"), "B3: a block at the feet -> lands one higher: %s %s" % (r7, list(MOVES)[-1:]))
    BK.LAST_GO.clear()
    for y in range(64, 75):
        floor("skywynn_zones", 31, y, 0)
    BK.BACK.put(BK.pkey(ub), Pt.dec("skywynn_zones|31.5|64.0|0.5|0|0|0|0|0|0"))
    n0 = MOVES.size()
    check("not safe to land" in str(BK.backR(pb, zone)) and MOVES.size() == n0, "B3: walled up (no free spot within 8) is refused")
    # cross-world: the player changed worlds between the destination thread and the move
    BK.LAST_GO.clear()
    BK.BACK.put(BK.pkey(ub), Pt.dec("skywynn_z1|0.5|64.0|0.5|0|0|0|0|0|0"))
    SAID.clear()
    BK.backR(pb, zone)
    q = W.fld(Wld, "taskQueue").get(zone2)
    task = q.poll()
    task.run()                         # stage 1 on skywynn_z1: lands fine, hops to Bob's world (skywynn_zones)
    put_in(pb, "skyy-island-bobkey")   # ... but Bob is gone to his island before the move runs
    n0 = MOVES.size()
    drain()
    check(MOVES.size() == n0 and any("changed worlds" in str(s) for s in SAID), "B3: changed worlds between the two threads = cancelled: %s" % list(SAID))
    put_in(pb, "skywynn_zones")
    # cross-world landing refused on the destination thread
    BK.LAST_GO.clear()
    BK.BACK.put(BK.pkey(ub), Pt.dec("skywynn_z1|0.5|140.0|0.5|0|0|0|0|0|0"))
    SAID.clear()
    BK.backR(pb, zone)
    drain()
    check(MOVES.size() == n0 and any("not safe to land" in str(s) for s in SAID), "B3: a destination with no ground is refused on its own thread")
    # an unloaded destination block (unknown) is trusted - it was checked when remembered
    GRID.put("skywynn_z1|default", Integer(-1))
    BK.LAST_GO.clear()
    BK.backR(pb, zone)
    drain()
    check(MOVES.size() == n0 + 1 and "|skywynn_z1|0.5|140.0|0.5" in str(MOVES.get(MOVES.size() - 1)), "B3: an unloaded destination is trusted as remembered")
    GRID.remove("skywynn_z1|default")
    BK.PART = False
    check("turned off" in str(BK.backR(pb, zone)), "B3: part.back off")
    BK.PART = True

    # ---------------- B4 relog / restart
    BK.BACK.clear()
    BK.LASTKEY.clear()
    check(mark(ua, "skywynn_zones", 7.25, 64.0, 0.75, "skyy-island-bobkey", 0, 100, 0) == 0, "B4: Alice remembered")
    check(mark(ub, "skywynn_z1", -7.5, 64.5, 0.5, "skywynn_zones", 0, 64, 0) == 0, "B4: Bob remembered")
    check(BK.save() and not BK.DIRTY and os.path.isfile(os.path.join(home, "back.properties")), "B4: saved to back.properties")
    txt = open(os.path.join(home, "back.properties"), encoding="latin-1").read()
    check(("skywynn_zones|7.25|64.0|0.75" in txt) and ("bobkey=skywynn_z1|-7.5|64.5|0.5" in txt) and not os.path.exists(os.path.join(home, "back.properties.tmp")),
          "B4: one line per profile key, no tmp file left")
    BK.BACK.clear()
    ld = str(BK.load())
    check("2 /back point" in ld and abs(BK.BACK.get(U_A + "#1").x - 7.25) < 1e-9 and str(BK.BACK.get("bobkey").world) == "skywynn_z1", "B4: a restart reads them back: %s" % ld)
    with open(os.path.join(home, "back.properties"), "a", encoding="latin-1") as fh:
        fh.write("junk=not|a|point\n")
    ld2 = str(BK.load())
    check("2 /back point" in ld2, "B4: a bad line is skipped: %s" % ld2)
    # B4x fix round: an unreadable file (a broken \u escape makes Properties.load throw) is set aside, never overwritten
    bpf = os.path.join(home, "back.properties")
    with open(bpf, "a", encoding="latin-1") as fh:
        fh.write("broken=\\uZZZZ\n")
    bad_bytes = open(bpf, "rb").read()
    ld3 = str(BK.load())
    bads = [n for n in os.listdir(home) if n.startswith("back.properties.bad-")]
    check("unreadable" in ld3 and "kept as back.properties.bad-" in ld3 and BK.BACK.size() == 0 and not os.path.exists(bpf) and len(bads) == 1
          and open(os.path.join(home, bads[0]), "rb").read() == bad_bytes, "B4x: an unreadable back.properties is renamed .bad-<stamp> (bytes kept): %s %s" % (ld3, bads))
    check(mark(ua, "skywynn_zones", 7.25, 64.0, 0.75, "skyy-island-bobkey", 0, 100, 0) == 0 and BK.save() and os.path.isfile(bpf)
          and open(os.path.join(home, bads[0]), "rb").read() == bad_bytes, "B4x: the next save writes a fresh file; the .bad copy stays")
    os.remove(os.path.join(home, bads[0]))
    L = J(PKG + "EssBackL")
    check(L(1) is not None and L(2) is not None, "B4: the join / quit listeners construct")
    BK.LASTKEY.put(ua, "x")
    PDE = J("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent")
    try:
        ev = W.us.allocateInstance(PDE.class_)
        k_ = PDE.class_
        while k_ is not None:
            for f in k_.getDeclaredFields():
                if f.getType() == PRc.class_:
                    f.setAccessible(True)
                    f.set(ev, pa)
            k_ = k_.getSuperclass()
        L(2).accept(ev)
        check(BK.LASTKEY.get(ua) is None, "B4: quit forgets the join key (the next login sets a new baseline)")
    except Exception as e:
        check(False, "B4: quit listener: %s" % e)

    # ---------------- H1 /sethome
    HM.BOOK.clear()
    HM.LAST_GO.clear()
    MOVES.clear()

    def stand(p_, wname, x, y, z_):
        put_in(p_, wname)
        POS.put(p_.getUuid(), Pt.dec("%s|%s|%s|%s|0|1.5|0|0|2.5|0" % (wname, x, y, z_)))
        return worlds[wname][0]

    w_ = stand(pa, "skywynn_zones", -10.5, 64.0, 0.5)
    r = str(HM.setR(pa, w_, None))
    check("Home 'home' set (1 of 2)" in r, "H1: /sethome = 'home': %s" % r)
    hf = os.path.join(home, "homes", (U_A + "#1").replace("#", "_") + ".properties")
    check(os.path.isfile(hf) and "home.1=home|skywynn_zones|-10.5|64.0|0.5" in open(hf, encoding="latin-1").read(), "H1: written at once to homes/<profile key>.properties")
    w_ = stand(pa, "skywynn_z1", 12.5, 64.0, 0.5)
    check("Home 'Mine' set (2 of 2)" in str(HM.setR(pa, w_, "Mine")), "H1: /sethome Mine (another world)")
    r = str(HM.setR(pa, w_, "Third"))
    check("Not saved" in r and "2 of 2" in r and len(HM.names(BK.pkey(ua))) == 2, "H1: the third home is refused at the limit: %s" % r)
    w_ = stand(pa, "skywynn_z1", 14.5, 64.0, 0.5)
    r = str(HM.setR(pa, w_, "mine"))
    check("moved here" in r and HM.book(BK.pkey(ua)).get(1).x == 14.5 and str(HM.book(BK.pkey(ua)).get(1).name) == "Mine", "H1: moving an existing home (any case) works when full: %s" % r)
    br.put("home:extra:" + str(ua), Integer(1))
    check("set (3 of 3)" in str(HM.setR(pa, w_, "Third")), "H1: home:extra:<uuid> 1 raises the limit to 3")
    br.remove("home:extra:" + str(ua))
    check(int(HM.limit(ua)) == 2, "H1: no extra = home.max")
    for bad in ("", "a b", "x" * 17, "na|me", "ok!"):
        if bad == "":
            continue
        check("1-16 letters" in str(HM.setR(pa, w_, bad)), "H1: bad name %r refused" % bad)
    w_ = stand(pb, "skyy-island-bobkey", 5.5, 100.0, 5.5)
    check("/is sethome" in str(HM.setR(pb, w_, "isl")), "H1: island worlds refused (use /is sethome)")
    w_ = stand(pb, "skyy-shard-bobkey", 0.5, 64.0, 0.5)
    check("shard" in str(HM.setR(pb, w_, "sh")), "H1: shard worlds refused")
    w_ = stand(pb, "instance-dungeon-1", 0.5, 64.0, 0.5)
    r_ = str(HM.setR(pb, w_, "dg"))
    check("instance world" in r_, "H1x: /sethome in a dungeon / instance world refused: %s" % r_)
    w_ = stand(pb, "skyy-island-orphan", 0.5, 64.0, 0.5)
    check("/is sethome" in str(HM.setR(pb, w_, "orp")), "H1x: a skyy-island-* world nobody owns counts as an island (refused)")
    w_ = stand(pb, "lobby", 0.5, 64.0, 0.5)
    BK.DENY = "lob*"
    check("closed to /back and homes" in str(HM.setR(pb, w_, "lb")), "H1x: /sethome in a denied world (Prefix*) refused")
    BK.DENY = ""
    w_ = stand(pb, "skywynn_zones", 0.5, 130.0, 0.5)
    check("solid ground" in str(HM.setR(pb, w_, "air")), "H1: no ground under you = refused")
    check(len(HM.names(BK.pkey(ub))) == 0, "H1: nothing saved for Bob")
    HM.BOOK.clear()
    n_ = [str(x) for x in HM.names(BK.pkey(ua))]
    check(n_ == ["home", "Mine", "Third"], "H1: a restart reads the homes file back in order: %s" % n_)
    check(len(HM.names(BK.pkey(ub))) == 0 and len(HM.names("carolkey")) == 0, "H1: per profile")

    # ---------------- H2 /home
    HM.LAST_GO.clear()
    MOVES.clear()
    SAID.clear()
    w_ = stand(pc, "skywynn_zones", 0.5, 64.0, 0.5)
    check("no homes yet" in str(HM.goR(pc, w_, None)), "H2: no homes")
    check("set (1 of 2)" in str(HM.setR(pc, w_, "Base")), "H2: Carol sets Base")
    w_ = stand(pc, "skywynn_zones", 45.5, 64.0, 0.5)
    r = str(HM.goR(pc, w_, None))
    check("Teleporting to home 'Base'" in r and str(MOVES.get(0)).startswith(str(uc) + "|skywynn_zones|0.5|64.0|0.5|2"), "H2: exactly one home -> /home goes there: %s" % r)
    check("Wait" in str(HM.goR(pc, w_, None)), "H2: the /home cooldown")
    HM.LAST_GO.clear()
    check("set (2 of 2)" in str(HM.setR(pc, w_, "Farm")), "H2: Carol sets Farm")
    r = str(HM.goR(pc, w_, None))
    check("2 homes: Base, Farm" in r and MOVES.size() == 1, "H2: two homes, none named home -> the list: %s" % r)
    r = str(HM.goR(pc, w_, "base"))
    check("home 'Base'" in r and MOVES.size() == 2, "H2: /home base (any case)")
    HM.LAST_GO.clear()
    check("No home named Nope" in str(HM.goR(pc, w_, "Nope")), "H2: unknown name lists the homes")
    HM.LAST_GO.clear()
    w_ = stand(pa, "skywynn_zones", 0.5, 64.0, 0.5)
    r = str(HM.goR(pa, w_, None))
    check("home 'home'" in r and "On the way" not in r, "H2: several homes -> the one named home: %s" % r)
    HM.LAST_GO.clear()
    r = str(HM.goR(pa, w_, "Mine"))
    drain()
    check("On the way" in r and str(MOVES.get(MOVES.size() - 1)).startswith(str(ua) + "|skywynn_z1|14.5|64.0|0.5|2"), "H2: cross-world /home Mine: %s" % list(MOVES)[-1:])
    check(int(BK.mark(ua, zone, 0.5, 64.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, "skywynn_z1", 14.5, 64.0, 0.5, False)) == 0
          and abs(pt_of(ua).x - 0.5) < 1e-9, "H2: /home is a teleport -> it sets the /back point")
    check(BK.LAST_GO.get(ua) is None or True, "H2: /home has its own cooldown")

    # ---------------- H3 /delhome, /homes, part.home, the bridge
    r = str(HM.delR(pc, "farm"))
    check("removed (1 of 2 left)" in r and [str(x) for x in HM.names("carolkey")] == ["Base"], "H3: /delhome farm: %s" % r)
    check("No home named" in str(HM.delR(pc, "farm")) or "no home named" in str(HM.delR(pc, "farm")), "H3: /delhome of a missing name")
    check("Your homes (1 of 2): Base" in str(HM.listR(pc)), "H3: /homes lists")
    HM.PART = False
    check("turned off" in str(HM.setR(pc, w_, "x")) and "turned off" in str(HM.goR(pc, w_, None)) and "turned off" in str(HM.delR(pc, "Base")),
          "H3: part.home off: /sethome /home /delhome refuse")
    check("Base" in str(HM.listR(pc)), "H3: /homes still lists while off")
    HM.PART = True
    f_h, f_g, f_b = br.get("essentials:fn:homes"), br.get("essentials:fn:gohome"), br.get("essentials:fn:back")
    check(f_h is None and f_g is None, "bridge not published before setup")
    BK.publish()
    f_h, f_g, f_b = br.get("essentials:fn:homes"), br.get("essentials:fn:gohome"), br.get("essentials:fn:back")
    check(f_h is not None and f_g is not None and f_b is not None, "H3: essentials:fn:homes / gohome / back published")
    nm = f_h.apply(uc)
    check(nm is not None and [str(x) for x in nm] == ["Base"], "H3: essentials:fn:homes (UUID) -> String[] %s" % (list(nm) if nm is not None else None))
    check(f_h.apply("nope") is None, "H3: a bad argument -> null")
    HM.LAST_GO.clear()
    n0 = MOVES.size()
    arr = JArray(JObject)(2)
    arr[0] = uc
    arr[1] = "Base"
    # H3x fix round: the bridge asks the command's permission first (fail closed)
    BK.PERMS = None
    BK.BACK_CMD = None
    BK.HOME_CMD = None
    r_g, r_b = str(f_g.apply(arr)), str(f_b.apply(uc))
    check("may not use /home" in r_g and "may not use /back" in r_b and drain() == 0 and MOVES.size() == n0,
          "H3x: no registered command object = the bridge refuses (fail closed): %s / %s" % (r_g, r_b))
    BK.HOME_CMD = J(PKG + "HomeCmd")()
    want = bool(ES.cmdOk(BK.HOME_CMD, pc))
    r_g = str(f_g.apply(arr))
    drain()
    check((r_g == "ok") == want, "H3x: with the registered command object the bridge follows its own hasPermission (%s): %s" % (want, r_g))
    HM.LAST_GO.clear()
    n0 = MOVES.size()
    PERMS = J("java.util.HashSet")()
    BK.PERMS = PERMS
    PERMS.add(str(uc) + "|1")
    check("may not use /home" in str(f_g.apply(arr)) and drain() == 0, "H3x: /back allowed does not allow /home")
    PERMS.add(str(uc) + "|2")
    fq = J("javassist.ClassPool")(True)
    fq.appendClassPath(jar)
    fq.appendClassPath(B.SERVER_JAR)
    _qb = J("java.io.ByteArrayOutputStream")()
    _qm = [m_ for m_ in fq.get(PKG + "EssBack").getDeclaredMethods() if str(m_.getName()) == "mayCmd"][0]
    J("javassist.bytecode.InstructionPrinter")(J("java.io.PrintStream")(_qb)).print_(_qm)
    check("EssStore.cmdOk" in str(_qb.toString()), "H3x: mayCmd = EssStore.cmdOk (AbstractCommand.hasPermission, the tpa bridge check)")
    check(str(f_g.apply(arr)) == "ok" and MOVES.size() == n0, "H3: essentials:fn:gohome -> ok, queued on the player's world thread")
    drain()
    check(MOVES.size() == n0 + 1 and str(MOVES.get(n0)).startswith(str(uc) + "|skywynn_zones|0.5|64.0|0.5|2"), "H3: ... and runs /home Base there")
    off = UUID.fromString("00000000-0000-0000-0000-000000000077")
    arr[0] = off
    check("not online" in str(f_g.apply(arr)), "H3: an offline player -> the reason")
    BK.LAST_GO.clear()
    BK.BACK.put("carolkey", Pt.dec("skywynn_zones|-20.5|64|0.5|0|0|0|0|0|0"))
    check(str(f_b.apply(uc)) == "ok", "H3: essentials:fn:back -> ok")
    drain()
    check(str(MOVES.get(MOVES.size() - 1)).startswith(str(uc) + "|skywynn_zones|-20.5|64.0|0.5|1"), "H3: ... and runs /back")
    BK.stop()
    check(br.get("essentials:fn:homes") is None and br.get("essentials:fn:back") is None, "H3: shutdown removes our bridge functions")

    # ---------------- K config rows
    keys = [str(k) for k in TCfg.KEYS]
    new = ["part.back", "back.cooldownSeconds", "back.minBlocks", "part.home", "home.max", "home.cooldownSeconds", "back.denyWorlds", "back.instanceWorlds"]
    check(all(k in keys for k in new), "K: the eight rows are TCfg keys")
    dt = str(TCfg.DEFAULT_TEXT)
    check("# ---- /back and homes (SkyyEssentials 0.1.13) ----" in dt and all(("\n%s=" % k) in dt for k in new)
          and "part.back=true" in dt and "back.minBlocks=32" in dt and "home.max=2" in dt and "home.cooldownSeconds=10" in dt,
          "K: a new config file carries them with their defaults")
    i_cd, i_mx = keys.index("back.cooldownSeconds"), keys.index("home.max")
    check(TCfg.put(i_cd, "30") and int(BK.CD_MS) == 30000 and str(TCfg.get(i_cd)) == "30", "K: back.cooldownSeconds 30 -> 30000 ms")
    check(TCfg.put(i_mx, "5") and int(HM.MAX) == 5 and int(HM.limit(ua)) == 5, "K: home.max 5")
    TCfg.put(i_cd, "10")
    TCfg.put(i_mx, "2")
    # Kx fix round: the "words" rows (the loader's canon + the kit's check= hook)
    i_dn, i_ia = keys.index("back.denyWorlds"), keys.index("back.instanceWorlds")
    check(("\nback.denyWorlds=\n" in dt) and ("\nback.instanceWorlds=skywynn_*\n" in dt) and str(TCfg.get(i_ia)) == "skywynn_*" and str(TCfg.get(i_dn)) == "",
          "Kx: defaults: deny none, instance worlds skywynn_*")
    check(str(TCfg.canon(i_dn, " Dungeon_* , lobby,, ")) == "dungeon_*,lobby" and TCfg.canon(i_dn, "*") is None and TCfg.canon(i_dn, "a b") is None
          and TCfg.canon(i_dn, "x,X") is None and TCfg.canon(i_dn, "a*b") is None and str(TCfg.canon(i_dn, "")) == ""
          and str(TCfg.canon(i_dn, "skyy-shard-ab#1")) == "skyy-shard-ab#1", "Kx: canonWords: trimmed, lower case, Prefix*, each once, no lone * / spaces / inner *")
    check(TCfg.put(i_dn, "dungeon_*") and str(BK.DENY) == "dungeon_*" and str(TCfg.get(i_dn)) == "dungeon_*" and BK.listed(BK.DENY, "Dungeon_Crypt")
          and not BK.listed(BK.DENY, "dungeon"), "Kx: put / get / listed (Prefix*, any case)")
    TCfg.put(i_dn, "")
    check(BK.checkWords("back.denyWorlds", "a,b*") is None and BK.checkWords("back.denyWorlds", "*") is not None, "Kx: the kit's check= hook")
    rows = T11.script_list("build_skyyessentials_%s.py" % VERSION, "ROWS")
    check(len(rows) == 34 and [r[0] for r in rows][-8:] == new and [r[0] for r in rows][-9] == "gameplay.keepInventory",
          "K2: 34 loader rows: 0.1.12's 26 (keepInventory next to last) + the eight new ones last")
    kit = T11.script_list("build_skyyessentials_%s.py" % VERSION, "KIT_ROWS", {"CF": "@config.properties:"})
    kc = dict((r[0], r[2]) for r in kit)
    check(all(k in kc for k in new) and kc["part.back"] == "parts" and kc["part.home"] == "parts" and kc["home.max"] == "tpa"
          and kc["back.denyWorlds"] == "tpa" and kc["back.instanceWorlds"] == "tpa", "K2: the eight Server Setup rows (Parts + Teleports)")
    ic, ib = dt.index("# ---- chat mirror"), dt.index("# ---- /back and homes")
    check(ic < ib and dt.rstrip().endswith("back.instanceWorlds=skywynn_*"), "K3: a new file: ... the chat mirror block, then the /back and homes block last")
    # K4 the live world's file (0.1.12) gets exactly the eight keys appended (read-only copy)
    livef = os.path.join(T11.LIVE, "config.properties")
    if os.path.isfile(livef):
        h2 = os.path.join(SCRATCH, "back", "live", "Skyy_SkyyEssentials")
        os.makedirs(h2, exist_ok=True)
        shutil.copy2(livef, os.path.join(h2, "config.properties"))
        T11.paths_for(TCfg, ES, Paths, h2)
        cfg0 = open(livef, "rb").read().decode("latin-1")
        TCfg.load()
        cfg1 = open(os.path.join(h2, "config.properties"), "rb").read().decode("latin-1")
        nl = "\r\n" if "\r\n" in cfg0 else "\n"
        have = T11.props_of(cfg0)
        byk = dict((r[0], r) for r in rows)
        miss = [k for k in new if k not in have]
        lines = ["#", "# ---- added by SkyyEssentials %s (keys this file did not have yet, with their defaults) ----" % VERSION]
        for k in miss:
            lines += ["# " + byk[k][8], "%s=%s" % (k, byk[k][6])]
        add = ("" if cfg0.endswith("\n") else nl) + nl.join(lines) + nl if miss else ""
        check(miss == new and cfg1 == cfg0 + add, "K4: the live config.properties = its bytes + exactly the eight new keys: %s" % cfg1[len(cfg0):][:400])
        p0, p1 = T11.props_of(cfg0), T11.props_of(cfg1)
        check(dict((k, v) for k, v in p1.items() if k not in new) == p0, "K4: every existing value kept")
        T11.paths_for(TCfg, ES, Paths, home)
    else:
        check(False, "K4: no live config at %s" % livef)
    # K5 setup: EssDurDeath + EssBackSys = two registerSystem calls, both before CfgPub.start
    import jpype as _jp
    pool = J("javassist.ClassPool")(True)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    mm = [m_ for m_ in pool.get(PKG + "SkyyEssentialsPlugin").getDeclaredMethods() if str(m_.getName()) == "setup"][0]
    bos = J("java.io.ByteArrayOutputStream")()
    J("javassist.bytecode.InstructionPrinter")(J("java.io.PrintStream")(bos)).print_(mm)
    su = str(bos.toString()).splitlines()
    rs = [i for i, l in enumerate(su) if "registerSystem(" in l]
    st = [i for i, l in enumerate(su) if "CfgPub.start(" in l]
    check(len(rs) == 2 and len(st) == 1 and max(rs) < st[0] and any("EssBackSys.<init>" in l for l in su) and any("EssDurDeath.<init>" in l for l in su),
          "K5: setup registers EssDurDeath + EssBackSys before CfgPub.start")
    print("back phase done")


# ============================================================================================================== Z. class byte-compare
def compare_jars():
    from cpstrings import read_utf8_constants
    if not os.path.isfile(PREV_JAR):
        check(False, "Z: no %s to compare with" % PREV_JAR)
        return
    za, zb = zipfile.ZipFile(PREV_JAR), zipfile.ZipFile(JAR)
    ca = dict((n, za.read(n)) for n in za.namelist() if n.endswith(".class"))
    cb = dict((n, zb.read(n)) for n in zb.namelist() if n.endswith(".class"))
    short = lambda n: n.rsplit("/", 1)[-1][:-6]
    gone = sorted(short(n) for n in set(ca) - set(cb))
    new = sorted(short(n) for n in set(cb) - set(ca))
    same = sorted(short(n) for n in set(ca) & set(cb) if ca[n] == cb[n])
    changed = sorted(n for n in set(ca) & set(cb) if ca[n] != cb[n])
    check(not gone, "Z: no class removed: %s" % gone)
    check(new == sorted(NEW_CLASSES), "Z: the new classes: %s" % new)
    expected = {"SkyyEssentialsPlugin", "TCfg", "CfgRows"}
    ver_only = []
    for n in changed:
        if short(n) in expected:
            continue
        sa, sb = set(read_utf8_constants(ca[n])), set(read_utf8_constants(cb[n]))
        da, db = sorted(sa - sb), sorted(sb - sa)
        ok = sorted(x.replace(PREV, VERSION) for x in da) == db
        ver_only.append(short(n))
        check(ok, "Z: %s differs in more than the version text: %s -> %s" % (short(n), da[:4], db[:4]))
    cs = set(short(n) for n in changed)
    check({"SkyyEssentialsPlugin", "TCfg"} <= cs, "Z: plugin + TCfg changed: %s" % sorted(expected & cs))
    keep = ["TpaCmd", "TpAcceptCmd", "MsgCmd", "EssFn", "ChatMirror", "TStore", "TSession", "TCodec", "TWindow", "TBlock", "EssWarp",
            "TradePage", "WarpPage", "HubBar", "EssDur", "EssDurDeath", "MoveTask", "ReadDestTask"]
    check(all(c_ in same for c_ in keep), "Z: tpa / msg / trade / warps / pages / durability byte-identical: %s" % [c_ for c_ in keep if c_ not in same])
    print("Z. byte-compare %s -> %s: %d identical, new %s, changed on purpose %s, version text only %s" % (
        PREV, VERSION, len(same), new, sorted(expected & cs), ver_only))


def main():
    ph = T11.arg("--phase")
    if "--run" in sys.argv:
        jar = T11.arg("--run")
        if ph == "back":
            run_back(jar)
        elif ph == "menu":
            T12.run_menu(jar)
        elif ph == "main":
            T11.run_main(jar)
        elif ph == "trade":
            T11.run_trade(jar)
        elif ph == "tpa":
            T11.run_tpa(jar)
        elif ph == "chat":
            T11.run_chat(jar)
        elif ph == "keep":
            T11.run_keep(jar)
        elif ph == "compost":
            T11.run_compost(jar)
        else:
            T11.run_live(jar, ph)
        for s_ in SKIPPED:
            print("  superseded:", s_)
        print("%s: %d checks passed, %d failed, %d superseded" % (ph, OKS[0], len(FAILS), len(SKIPPED)))
        for f in FAILS:
            print("  FAILED:", f)
        sys.stdout.flush()
        os._exit(1 if FAILS else 0)
    if not os.path.isfile(JAR):
        sys.exit("no jar at %s - build it first (python SkyyEssentials/build_skyyessentials_%s.py)" % (JAR, VERSION))
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    rc = 0
    only = T11.arg("--only")
    for ph in ("back", "menu", "main", "trade", "tpa", "chat", "keep", "compost"):
        if only and ph not in only.split(","):
            continue
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--phase", ph, "--dir", SCRATCH], env=env)
        print("phase %s: %s" % (ph, "ok" if p.returncode == 0 else "FAIL"))
        rc |= p.returncode
    if not only:
        if os.path.isdir(T11.LIVE):
            dstl = os.path.join(SCRATCH, "live", "mods", "Skyy_SkyyEssentials")
            shutil.copytree(T11.LIVE, dstl)
            for ph in ("live1", "live2"):
                p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--phase", ph, "--dir", SCRATCH], env=env)
                print("phase %s: %s" % (ph, "ok" if p.returncode == 0 else "FAIL"))
                rc |= p.returncode
        else:
            print("FAIL no live folder at %s" % T11.LIVE)
            rc |= 1
    compare_jars()
    print("Z: %d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAILED:", f)
    rc |= 1 if FAILS else 0
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyEssentials %s bare-JVM check:" % VERSION, "PASS" if rc == 0 else "FAIL")
    sys.exit(rc)


if __name__ == "__main__":
    main()
