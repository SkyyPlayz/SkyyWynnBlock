"""Harness for SkyyPets 0.4.25 (the dragon keeps out of the way and hunts; tools/pets_0_4_25_patch.py). Build first:
    python tools/pets_0_4_25_patch.py && python SkyyPets/build_skyypets_0.4.25.py
    python SkyyPets/test_skyypets_0.4.25.py [--keep] [--expect-dump]

  S     static   the patch re-runs to identical bytes; two classes + one interface added, no system / command; role JSON (Walk + Fly, initial Walk, Seek only under Walk, no Player fallback);
                 the rows in the Dragons group; setup order; the jar: only the new classes added, changed non-class entries = manifest, the role, the lang lines
  A/C/AA          (tools/harness_kit.py, -Xverify:all) verify, class compare 0.4.24 -> 0.4.25, engine-access audit
  IDLE  EXECUTED on the stand-in world (real PetViews / PetFight / PetRide / PetIdle): the flying circle (radius, height, moving), Fly / Walk switches, every row live, the room rule + hysteresis,
                 the ground hold (Seek on / off by distance), crouch call, catch-up, world change, ride takes over (riding / mounting / landing: no idle step), Fly back after a ride
  AGG   EXECUTED: the pick = nearest of what passes; EVERY excluded kind (player, other's pet, Tamed / _Ally, passive animal, merchant / quest NPC, invulnerable, dead, dormant, safe zone, out of sight, no level,
                 no SkyyMobs, island + shard worlds, other modes, fighting off); keeps at it, leaves the range, next one; the owner's hit takes over; air fight stays in the air; 30 s pass on a target it cannot reach
  MIG   EXECUTED PetsMigDrg: untouched follow -> aggressive (LF, CRLF, spaces), defend / aggressive kept (note), bytes outside the line, History, Changes line, marker, twice = once, fresh home; the normaliser
  ECS/RIDE/PT/RD  0.4.24's and 0.4.23's phases on this jar (fights, riding, pass-through; old fights on follow mode)
  live  0.4.17's start-twice on a scratch COPY of the live Skyy_SkyyPets
NOT COVERED (only the game can prove it): the Fly animations (FlyIdle) and how smooth the circle looks; Role.setActiveMotionController on a live NPC (a real role with a real controller is only exercised for the read + refused paths);
a real TargetUtil scan; the client's F prompt on a flying dragon.
Exit code 1 on any failure.
"""
import os, sys, json, math, zipfile, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "drg025fix", "pets")]
import skyybuild as B
import harness_kit as HK

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T424 = _mod(os.path.join(HERE, "test_skyypets_0.4.24.py"), "test_skyypets_0_4_24")
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T423, T44, T417, T41 = T424.T423, T424.T44, T424.T417, T424.T41

VERSION = "0.4.25"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.24.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.24.py")
PATCH = os.path.join(TOOLS, "pets_0_4_25_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T424.JAR, T424.OLD_JAR, T423.JAR, T423.OLD_JAR = JAR, OLD_JAR, JAR, OLD_JAR
ADDED = ["PetIdle", "PetIdleApi", "PetsMigDrg"]
EXPECT = {
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'PetFight': ['+m aggressive', '~m defend', '~m second', '~m text'],
    'PetRide': ['~m cardLine'],
    'PetView': ['+f iair', '+f ibad', '+f ibadAt', '+f ibadT', '+f icall', '+f icr', '+f icrAt', '+f ifought', '+f ih', '+f ihold', '+f iok', '+f ir', '+f iseek'],
    'PetViews': ['~m steer', '~m upkeep'],
    'PetsCfg': ['+f DRAGON_AGGRO', '+f DRAGON_IDLE_CALL', '+f DRAGON_IDLE_H', '+f DRAGON_IDLE_MODE', '+f DRAGON_IDLE_R', '+f DRAGON_IDLE_SPEED', '+f DRAGON_NOAGGRO', '~<clinit>', '~m applyAll', '~m applyScalars', '~m seed'],
    'PetsMigP5': ['~m mgLog', '~m run'],
    'PetsMigS2': ['~m run'],
    'PetsMigW15': ['~m run'],
    'SkyyPetsPlugin': ['~m setup'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}

_eq0 = HK.Child.eq


def _eq(self, got, want, what):
    if what == "C: non-class entries changed" and want == ["manifest.json"]:
        return self.check(sorted(got) == ["Server/NPC/Roles/SkyyPets/Skyy_Pet_Dragon.json", "manifest.json"], "C: non-class entries changed = manifest.json + the dragon role: %s" % sorted(got))
    return _eq0(self, got, want, what)


HK.Child.eq = _eq


# old harness phases keep on the old behaviours (a fresh Cfg is aggressive + circling): follow + ground
def _old(fn):
    def run(out, jar, scratch, home):
        W0 = T44._world

        def wr(*a):
            W = W0(*a)
            C_ = W["PetsCfg"]
            C_.DRAGON_FMODE = "follow"
            C_.DRAGON_IDLE_MODE = "follow"
            return W
        T44._world = wr
        try:
            fn(out, jar, scratch, home)
        finally:
            T44._world = W0
    return run


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.25 - build script') and g.count('VERSION = "0.4.25"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem("), "S no system or command added")
    K.eq(g.count("= cls(") - o.count("= cls("), 2, "S two classes added (PetIdle + PetsMigDrg)")
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "pets_0_4_24_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn - on), sorted("com/skyy/pets/%s.class" % a for a in ADDED), "S the jar adds only the three classes")
    K.eq(sorted(on - nn), [], "S the jar removes nothing")
    chg = sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n))
    K.eq(chg, ["Server/NPC/Roles/SkyyPets/Skyy_Pet_Dragon.json", "manifest.json"], "S changed non-class entries = the dragon role + manifest.json")
    rl = json.loads(zn.read("Server/NPC/Roles/SkyyPets/Skyy_Pet_Dragon.json").decode("utf8"))
    K.eq([c["Type"] for c in rl["MotionControllerList"]], ["Walk", "Fly"], "S role: Walk first, then Fly")
    K.eq(rl.get("InitialMotionController"), "Walk", "S role: Walk for sure at spawn (the engine picks a random one otherwise)")
    fly_ref = json.loads(zn.read("Server/NPC/Roles/SkyyPets/Skyy_Pet_Fly.json").decode("utf8"))["MotionControllerList"][0]
    K.check(rl["MotionControllerList"][1] == fly_ref, "S role: the Fly controller = the one every flying pet uses")
    inner = rl["Instructions"][0]["Instructions"]
    K.eq(len(inner), 1, "S role: one branch only")
    K.eq(inner[0]["Sensor"], {"Type": "MotionController", "MotionController": "Walk"}, "S role: Seek only while Walk is active (Fly = no steering of its own)")
    K.check(inner[0]["Instructions"][0]["Sensor"]["Type"] == "Target" and inner[0]["Instructions"][0]["BodyMotion"]["Type"] == "Seek" and len(inner[0]["Instructions"]) == 1, "S role: Target -> Seek, no Player fallback")
    su = g[g.index("java.nio.file.Path mods = getDataDirectory().getParent();"):]
    K.check(su.index("PetsMigW15.run(") < su.index("PetsMigDrg.run(") < su.index("PetsCfg.load(mods)"), "S setup: ... MigW15 -> MigDrg -> load")
    for key in ("pets.dragon.idle.mode", "pets.dragon.idle.radius", "pets.dragon.idle.height", "pets.dragon.idle.speed", "pets.dragon.idle.crouchCall", "pets.dragon.fight.aggroRange", "pets.dragon.fight.noAggroWorlds"):
        K.check(('("%s",' % key) in g and ('"dragons"') in g[g.index('("%s",' % key):g.index('("%s",' % key) + 200] and '"live"' in g[g.index('("%s",' % key):g.index('("%s",' % key) + 300], "S row %s: Dragons group, live" % key)
    K.check('"pets.dragon.fight.mode", "Who the dragon fights", "dragons", "choice", "aggressive"' in g and "aggressive|Aggressive,follow|Follow,defend|Defend" in g, "S fight.mode: default aggressive, three choices")
    K.save()


# ======================================================================================================== the stand-in world + the idle API
def _idle_world(out, jar, scratch, tag):
    W = T44._world(out, jar, scratch, tag)
    K, JClass, JProxy = W["K"], W["JClass"], W["JProxy"]
    from jpype import JString, JArray, JDouble, JFloat, JObject
    P_ = lambda n: JClass(PKG + n)
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    Ref, Store_, World = JClass("com.hypixel.hytale.component.Ref"), JClass("com.hypixel.hytale.component.Store"), JClass("com.hypixel.hytale.server.core.universe.world.World")
    UUID = W["UUID"]
    S = dict(st=U.allocateInstance(Store_.class_), st2=U.allocateInstance(Store_.class_), w=U.allocateInstance(World.class_))
    ents, jobs, nxt = {}, [], [200]

    def new_ref(uuid, role, pos, store=None, **extra):
        nxt[0] += 1
        r = Ref(store if store is not None else S["st"], nxt[0])
        ents[int(r.getIndex())] = dict(uuid=uuid, role=role, pos=list(pos), net=nxt[0] + 5000, ground=1, ref=r, ctrl="Walk", att="HOSTILE", hp=[100.0, 0.0, 100.0], player=None, guarded=False, dead=False, **extra)
        return r
    ent = lambda r: None if r is None else ents.get(int(r.getIndex()))
    uo = UUID.fromString("00000000-0000-0000-0000-000000009901")
    oref = new_ref(uo, None, [10.0, 70.0, 10.0])
    ent(oref)["player"] = uo
    roles = {"Skyy_Pet_Walk": 11, "Skyy_Pet_Fly": 12, "Skyy_Pet_Dragon": 13, "Test_Pet": 7, "Test_Fly": 8, "Empty_Role": 3}
    marks, tps, sets, solid = {}, [], [], set()

    def spawn(s, role, x, y, z, yaw, model):
        return new_ref(UUID.randomUUID(), [k for k, v in roles.items() if v == int(role)][0], [float(x), float(y), float(z)])

    def setp(acc, r, x, y, z, yaw):
        ent(r)["pos"] = [float(x), float(y), float(z)]
        sets.append(int(r.getIndex()))

    def tele(acc, r, x, y, z, yaw):
        ent(r)["pos"] = [float(x), float(y), float(z)]
        tps.append((int(r.getIndex()), [float(x), float(y), float(z)]))

    def mark(acc, r, o):
        if o is not None:
            marks[int(r.getIndex())] = int(o.getIndex())
    api = {"roleIndex": lambda role: roles.get(str(role), -1), "model": lambda m, s: JString(str(m)), "modelPinned": lambda m, s, seed: JString(str(m)),
           "spawn": spawn, "store": lambda w_: S["st"], "ownerRef": lambda u_: oref if str(u_) == str(uo) else None, "refOf": lambda w_, u_: None, "execute": lambda w_, r_: (jobs.append(r_), True)[1],
           "pos": lambda acc, r: JArray(JDouble)(ent(r)["pos"]) if ent(r) else None, "setPos": setp, "teleport": tele, "dead": lambda acc, r: bool((ent(r) or {}).get("dead")), "uuid": lambda acc, r: (ent(r) or {}).get("uuid"),
           "roleOf": lambda acc, r: (ent(r) or {}).get("role"), "tags": lambda acc, r: JString(""), "prepare": lambda acc, r, t: None, "plate": lambda acc, r, t: None,
           "clearDebug": lambda acc, r: None, "mark": mark, "remove": lambda acc, r: True, "hearts": lambda *a: None, "anim": lambda *a: None, "stopAnim": lambda *a: None,
           "vanillaScale": lambda mid: 1.0, "fx": lambda *a: None, "passthrough": lambda acc, r, m: JString(str(m)), "interact": lambda acc, r: False}
    PW = P_("PetWorld")
    PW.API = JProxy(PKG + "PetWorldApi", dict=api)
    rider = {"mid": 0, "mount": set()}

    def r_mount(s, pet, o, ax, ay, az, mv):
        rider["mid"] = ent(pet)["net"]
        rider["mount"].add(int(pet.getIndex()))
        return JString("")
    rapi = {"mount": r_mount, "mountedId": lambda acc, o: int(rider["mid"]), "netId": lambda acc, r: int((ent(r) or {}).get("net", 0)),
            "hasMount": lambda acc, r: r is not None and int(r.getIndex()) in rider["mount"], "unmount": lambda acc, r_: (rider["mount"].discard(int(r_.getIndex())), True)[1],
            "dismount": lambda acc, o: (rider.__setitem__("mid", 0), rider["mount"].clear())[0], "resetMove": lambda acc, o: True, "move": lambda acc, o, mid: True,
            "ground": lambda acc, r: int((ent(r) or {}).get("ground", -1)), "fly": lambda acc, o, on, h, v: True, "flyState": lambda acc, o: -1,
            "saddled": lambda m, s, seed: JString(str(m)), "held": lambda s, o: None}
    Rd, Fg, Cfg, Views, Store, Ops, Idle = P_("PetRide"), P_("PetFight"), P_("PetsCfg"), P_("PetViews"), P_("PetStore"), P_("PetOps"), P_("PetIdle")
    Rd.API = JProxy(PKG + "PetRideApi", dict=rapi)
    Fg.API = JProxy(PKG + "PetFightApi", dict={"hit": lambda cb, t, src, cause, amt: True, "health": lambda acc, r_: JArray(JFloat)((ent(r_) or {}).get("hp", [100.0, 0.0, 100.0])),
                                               "playerOf": lambda acc, r_: (ent(r_) or {}).get("player"), "guarded": lambda acc, r_: bool((ent(r_) or {}).get("guarded"))})
    idle = dict(crouch=False, roles_no_fly=set(), unmarks=[], scans=[0], ground=True, last=None, clobber=False)

    def motion(acc, r, typ):
        e = ent(r)
        if e is None or e.get("role") != "Skyy_Pet_Dragon":
            return 0
        if str(typ) == "Fly" and int(r.getIndex()) in idle["roles_no_fly"]:
            return 0
        if e["ctrl"] == str(typ):
            return 1
        e["ctrl"] = str(typ)
        return 2

    def scan(acc, x, y, z, rg):
        idle["scans"][0] += 1
        l = JClass("java.util.ArrayList")()
        for e in ents.values():
            if e.get("role") is None and e.get("player") is None and not e.get("drop"):
                continue
            p = e["pos"]
            if (p[0] - float(x)) ** 2 + (p[1] - float(y)) ** 2 + (p[2] - float(z)) ** 2 <= float(rg) ** 2 + 1e-6 and e["ref"].getStore() == S["st"]:
                l.add(e["ref"])
        idle["last"] = l          # the engine hands out its per-thread list; "clobber" = a later spatial query refills it
        return l
    iapi = {"motion": motion, "unmark": lambda acc, r: (idle["unmarks"].append(int(r.getIndex())), marks.pop(int(r.getIndex()), None), True)[2], "crouching": lambda acc, o: bool(idle["crouch"]),
            "solid": lambda x, y, z: (int(x), int(y), int(z)) in solid or (idle["ground"] and int(y) == 69), "scan": scan, "attitude": lambda acc, t: JString((ent(t) or {}).get("att", ""))}
    Idle.API = JProxy(PKG + "PetIdleApi", dict=iapi)
    Cfg.SPAWN_DELAY = 0
    Cfg.SLOT2_MODE = "always"
    W["names"][str(uo)] = "Rider"
    key = str(Store.pkey(uo))
    Store.KEYOF.put(uo, key)
    r = Store.get(key)
    r.set("starter", "1")
    pid = str(Ops.create(r, None, "DragonPlain", 3, 10, 0, "test", "harness", False))
    r.set("active.2", pid)
    clock = [0]
    levels = {}
    BR = W["BR"]

    def lvl(u):
        if idle["clobber"] and idle["last"] is not None:
            idle["last"].clear()
        return JClass("java.lang.Integer").valueOf(levels.get(str(u), 0))
    BR.put("mob:fn:level", JProxy("java.util.function.Function", dict={"apply": lvl}))

    def second(plus=1000, wn="default"):
        clock[0] += plus
        Fg.NOW_OFF = clock[0]
        Rd.NOW_OFF = clock[0]
        Views.second(uo, oref, S["st"], None, S["w"], wn)
        while jobs:
            jobs.pop(0).run()

    def steer(n=1, dt=0.05):
        for _ in range(n):
            Views.steer(uo, oref, None, JFloat(dt))
    Views.SEEN.put(uo, JArray(JObject)(["default", JClass("java.lang.Long").valueOf(0)]))
    W.update(K=K, S=S, ent=ent, new_ref=new_ref, uo=uo, oref=oref, UUID=UUID, marks=marks, tps=tps, sets=sets, solid=solid, rider=rider, jobs=jobs, levels=levels, idle=idle, Idle=Idle, Cfg=Cfg, Views=Views, Rd=Rd, Fg=Fg, Ops=Ops, Store=Store, PW=PW, second=second, steer=steer, clock=clock, BR=BR, JString=JString, JProxy=JProxy, JClass=JClass, pid=pid, r=r, api=api, Px=JProxy)
    return W


def _dv(W):
    for _ in range(3):
        W["second"]()
    return W["Views"].view(W["uo"], 2)


def _dist2(a, b):
    return math.hypot(a[0] - b[0], a[2] - b[2])


# ======================================================================================================== IDLE
def run_idle(out, jar, scratch, _home):
    W = _idle_world(out, jar, scratch, "idle")
    K, Idle, Cfg, Views, Rd, ent, second, steer, oref, solid = W["K"], W["Idle"], W["Cfg"], W["Views"], W["Rd"], W["ent"], W["second"], W["steer"], W["oref"], W["solid"]
    dv = _dv(W)
    K.check(dv is not None and str(dv.role) == "Skyy_Pet_Dragon" and int(dv.motion) == 0, "IDLE the dragon is out, role Skyy_Pet_Dragon, motion 0 (walk) = the steer branch")
    d = ent(dv.ref)
    K.eq(str(Cfg.DRAGON_IDLE_MODE), "circle", "IDLE default mode = circle")
    K.check(float(Cfg.DRAGON_IDLE_R) == 7.0 and float(Cfg.DRAGON_IDLE_H) == 4.0 and float(Cfg.DRAGON_IDLE_SPEED) == 3.0 and int(Cfg.DRAGON_AGGRO) == 16, "IDLE defaults 7 / 4 / 3 / 16")
    K.check(bool(dv.iair) and d["ctrl"] == "Fly", "IDLE not fighting, not ridden: the Fly controller is on: iair %s, ctrl %s" % (bool(dv.iair), d["ctrl"]))
    steer(800)
    op = ent(oref)["pos"]
    K.check(abs(_dist2(d["pos"], op) - 7.0) < 0.8 and abs(d["pos"][1] - (op[1] + 4.0)) < 0.6, "IDLE the circle: %.2f blocks out, %.2f above you" % (_dist2(d["pos"], op), d["pos"][1] - op[1]))
    a0 = math.atan2(d["pos"][2] - op[2], d["pos"][0] - op[0])
    steer(20)
    a1 = math.atan2(d["pos"][2] - op[2], d["pos"][0] - op[0])
    wrap = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    K.check(wrap > 0.05, "IDLE it moves around you: the angle moved %.3f rad in 1 s (~3 blocks a second at 7)" % wrap)
    # ---- the pure sums
    K.check(list(Idle.space(dv, W["JClass"]("com.skyy.pets.PetFly").orbit(10.0, 70.0, 10.0, 0.0, 0.0, 0.0, 0.0))) == [7.0, 4.0], "IDLE the widest circle that fits: 7 x 4 in open air")
    op_ = W["JClass"]("com.skyy.pets.PetFly").orbit(10.0, 70.0, 10.0, 0.0, 0.0, 0.0, 0.0)
    # ---- rows are live
    Cfg.DRAGON_IDLE_R = 12.0
    Cfg.DRAGON_IDLE_H = 8.0
    second()
    steer(800)
    op = ent(oref)["pos"]
    K.check(abs(_dist2(d["pos"], op) - 12.0) < 1.0 and abs(d["pos"][1] - (op[1] + 8.0)) < 0.7, "IDLE radius and height rows are live: %.2f out, %.2f above" % (_dist2(d["pos"], op), d["pos"][1] - op[1]))
    Cfg.DRAGON_IDLE_R, Cfg.DRAGON_IDLE_H = 7.0, 4.0
    second()
    steer(800)
    Cfg.DRAGON_IDLE_SPEED = 0.0
    steer(200)
    p0 = list(d["pos"])
    steer(60)
    K.check(_dist2(p0, d["pos"]) < 0.05, "IDLE speed 0 = it hovers: moved %.3f in 3 s" % _dist2(p0, d["pos"]))
    Cfg.DRAGON_IDLE_SPEED = 3.0
    # ---- mode switch to follow: walk, hold distance
    sets0 = len(W["sets"])
    W["marks"].clear()
    Cfg.DRAGON_IDLE_MODE = "follow"
    second()
    K.eq(d["ctrl"], "Walk", "IDLE mode follow (live): back to Walk")
    K.check(bool(dv.ihold) and not bool(dv.iair) and W["tps"][-1][1][1] == 70.0, "IDLE ... put down beside you (no fall), hold on")
    sets0 = len(W["sets"])
    steer(5)
    K.eq(len(W["sets"]), sets0, "IDLE follow: no flying steps at all")
    idx = int(dv.ref.getIndex())
    K.check(idx not in W["marks"] and int(dv.ref.getIndex()) in W["idle"]["unmarks"], "IDLE follow: near you no Seek target")
    d["pos"] = [op[0] + 10.0, op[1], op[2]]
    steer(1)
    K.eq(W["marks"].get(idx), int(oref.getIndex()), "IDLE follow: past radius + 1 the Seek on you goes on")
    d["pos"] = [op[0] + 6.5, op[1], op[2]]
    steer(1)
    K.check(idx not in W["marks"], "IDLE follow: inside the radius it stops")
    # ---- room to fly: mode circle again, column blocked -> ground after 3 s, clear -> air after 2
    Cfg.DRAGON_IDLE_MODE = "circle"
    second()
    second()
    K.check(bool(dv.iair) and d["ctrl"] == "Fly", "IDLE back to circle: it needs 2 clear seconds first, then Fly")
    steer(200)
    ox, oy, oz = int(math.floor(op[0])), int(math.floor(op[1])), int(math.floor(op[2]))
    for y in range(oy + 1, oy + 7):
        solid.add((ox, y, oz))
    second()
    K.check(bool(dv.iair), "IDLE a block above you: still flying after 1 s (hysteresis)")
    second()
    K.check(bool(dv.iair), "IDLE ... and after 2 s")
    second()
    K.check(not bool(dv.iair) and bool(dv.ihold) and d["ctrl"] == "Walk", "IDLE ... 3 s under a roof: down, on the ground, Walk (no room)")
    K.check(int(Idle.NOROOM.get()) >= 1, "IDLE the no-room counter")
    solid.clear()
    second()
    K.check(not bool(dv.iair), "IDLE clear again: one second is not enough")
    second()
    K.check(bool(dv.iair), "IDLE clear for 2 s: flying again")
    # a wall on the ring at full radius but room at 60 %: the circle shrinks
    steer(200)
    fy = int(math.floor(op[1] + 4.0))
    ring = (int(math.floor(op[0] + 7.0)), fy, int(math.floor(op[2])))
    solid.add(ring)
    second()
    K.check(abs(float(dv.ir) - 4.2) < 0.01 and bool(dv.iair), "IDLE a wall on the ring: the circle shrinks to 60 %%: r = %.2f" % float(dv.ir))
    solid.clear()
    second()
    K.check(float(dv.ir) == 7.0, "IDLE it widens back")
    # ---- the set-down spot: a free spot with ground under it, never a wall or a ledge
    op_j = _ja(W, op)
    fy0 = int(math.floor(op[1]))
    spots = [(op[0] + math.cos(i * math.pi / 4.0) * 3.0, op[2] + math.sin(i * math.pi / 4.0) * 3.0) for i in range(8)]
    cell = lambda s_: (int(math.floor(s_[0])), int(math.floor(s_[1])))
    L = lambda: list(Idle.landing(dv, op_j))
    K.check(abs(L()[0] - spots[0][0]) < 1e-6 and L()[1] == op[1] and abs(L()[2] - spots[0][1]) < 1e-6, "LAND open ground: the first compass point, your height: %s" % L())
    for lbl, dy in (("feet", 0), ("head", 1), ("the top of a tall dragon", 2)):
        solid.clear()
        solid.add((cell(spots[0])[0], fy0 + dy, cell(spots[0])[1]))
        K.check(abs(L()[0] - spots[1][0]) < 1e-6 and abs(L()[2] - spots[1][1]) < 1e-6, "LAND a wall at its %s: the next compass point: %s" % (lbl, L()))
    solid.clear()
    W["idle"]["ground"] = False
    solid.add((cell(spots[5])[0], fy0 - 1, cell(spots[5])[1]))
    K.check(abs(L()[0] - spots[5][0]) < 1e-6 and abs(L()[2] - spots[5][1]) < 1e-6, "LAND a ledge: only the point with ground under it: %s" % L())
    solid.clear()
    K.eq([float(x) for x in L()], [float(x) for x in op], "LAND over the void on every side: your own column")
    W["idle"]["ground"] = True
    for s_ in spots:
        solid.add((cell(s_)[0], fy0, cell(s_)[1]))
    K.eq([float(x) for x in L()], [float(x) for x in op], "LAND walled in on all 8 points: your own column")
    solid.clear()
    # ---- double-tap crouch: held = nothing, one tap = nothing, two slow = nothing, two quick = down
    idl = W["idle"]

    def tap():
        idl["crouch"] = True
        steer(2)
        idl["crouch"] = False
        steer(2)
    calls0 = int(Idle.CALLS.get())
    idl["crouch"] = True
    steer(30)
    second()
    second()
    K.check(bool(dv.iair) and int(Idle.CALLS.get()) == calls0, "CROUCH held (building, a void edge): it stays up")
    idl["crouch"] = False
    steer(2)
    tap()
    second()
    K.check(bool(dv.iair) and int(Idle.CALLS.get()) == calls0, "CROUCH one tap: it stays up")
    tap()
    K.check(int(Idle.CALLS.get()) == calls0, "CROUCH a tap 1 s after the last is not a double tap")
    W["clock"][0] += 900
    W["Fg"].NOW_OFF = W["clock"][0]
    tap()
    K.check(int(Idle.CALLS.get()) == calls0, "CROUCH two taps 0.9 s apart: too slow")
    second()
    Cfg.DRAGON_IDLE_CALL = False
    tap()
    tap()
    K.check(int(Idle.CALLS.get()) == calls0, "CROUCH row off: a double tap does nothing")
    Cfg.DRAGON_IDLE_CALL = True
    second()
    W["marks"].clear()
    tap()
    tap()
    K.check(int(Idle.CALLS.get()) == calls0 + 1, "CROUCH a double tap between two seconds counts (read every tick)")
    second()
    K.check(not bool(dv.iair) and not bool(dv.ihold) and d["ctrl"] == "Walk" and W["marks"].get(idx) == int(oref.getIndex()), "CROUCH it comes down, Walk, the old follow marks you (F reachable)")
    K.check(_dist2(W["tps"][-1][1], op) < 3.5, "CROUCH ... set down within F reach")
    for _ in range(6):
        second()
    K.check(not bool(dv.iair), "CROUCH ... it waits the 8 s")
    second()
    second()
    second()
    K.check(bool(dv.iair), "IDLE ... then flies off again")
    # ---- catch-up
    steer(200)
    tps0 = len(W["tps"])
    d["pos"] = [op[0] + 200.0, op[1] + 4.0, op[2]]
    second()
    K.eq(len(W["tps"]), tps0, "IDLE far away one second: not yet")
    d["pos"] = [op[0] + 200.0, op[1] + 4.0, op[2]]
    second()
    K.check(len(W["tps"]) == tps0 + 1 and abs(_dist2(W["tps"][-1][1], op) - 7.0) < 0.5 and abs(W["tps"][-1][1][1] - 74.0) < 0.5 and int(Idle.CATCHUPS.get()) >= 1, "IDLE far for 2 s: it hops back to its place on the circle")
    # ---- ride takes over
    W["steer"](10)
    n0 = len(W["sets"])
    K.eq(int(Views.use(W["uo"], dv, int(Rd.now()))), 4, "IDLE F: the mount job")
    while W["jobs"]:
        W["jobs"].pop(0).run()
    steer(5)
    K.eq(len(W["sets"]), n0, "IDLE mounting (rideAt set): no flying step (the mount job is not fought)")
    second()
    K.check(bool(dv.riding), "IDLE it took")
    d["ctrl"] = "Empty"
    d["role"] = "Empty_Role"
    n0 = len(W["sets"])
    steer(5)
    second()
    K.eq(len(W["sets"]), n0, "IDLE while ridden: not one flying step")
    K.eq(d["ctrl"], "Empty", "IDLE while ridden: PetIdle never touches the controller")
    d["role"] = "Skyy_Pet_Dragon"
    d["ctrl"] = "Walk"
    W["rider"]["mid"] = 0
    W["rider"]["mount"].clear()
    second()
    K.check(not bool(dv.riding) and bool(dv.landing), "IDLE you get off: it lands (the 0.4.13 landing)")
    steer(10)
    dv.landing = False
    second()
    K.check(bool(dv.iair) and d["ctrl"] == "Fly", "IDLE ... after the landing it takes off again (the role change's Walk reset is undone)")
    # ---- owner world change: the view is removed, never moved into the other world
    W["steer"](2)
    n0 = len(W["sets"])
    second(wn="other")
    K.check(bool(dv.gone) and Views.view(W["uo"], 2) != dv, "IDLE you change world: the old dragon is removed, never moved")
    nv = Views.view(W["uo"], 2)
    K.check(nv is None or str(nv.world) == "other", "IDLE ... a new one appears in the new world (as every pet)")
    ent(dv.ref)["pos"][0] += 0.0
    dv.ref = W["new_ref"](W["UUID"].randomUUID(), "Skyy_Pet_Dragon", [0, 0, 0], store=W["S"]["st2"])
    dv.gone = False
    n1 = len(W["sets"])
    steer(3)
    K.eq(len(W["sets"]), n1, "IDLE ... a view on another world's store is never steered (steer's store check)")
    # ---- only the summon slot, only dragons
    from jpype import JFloat
    v2 = W["JClass"]("com.skyy.pets.PetView")()
    v2.slot, v2.kind = 1, JString_("DragonPlain")
    K.check(not bool(Idle.second(v2, oref, None, W["JClass"]("com.skyy.pets.PetFly").orbit(10.0, 70.0, 10.0, 0.0, 0.0, 0.0, 0.0))), "IDLE not in the pet slot")
    v3 = W["JClass"]("com.skyy.pets.PetView")()
    v3.slot, v3.kind, v3.ref = 2, JString_("Rabbit"), W["new_ref"](W["UUID"].randomUUID(), "Skyy_Pet_Walk", [0, 0, 0])
    K.check(not bool(Idle.second(v3, oref, None, W["JClass"]("com.skyy.pets.PetFly").orbit(10.0, 70.0, 10.0, 0.0, 0.0, 0.0, 0.0))), "IDLE not for other pets")
    K.check("controller switches" in str(Idle.text()), "IDLE status text")
    K.save()


def JString_(s):
    from jpype import JString
    return JString(s)


# ======================================================================================================== REAL: PetIdle.motion on a real Role (the read + refused paths)
def run_real(out, jar, scratch, _home):
    from jpype import JClass, JProxy, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    Idle = JClass(PKG + "PetIdle")
    K.check(Idle.API is None, "REAL the real seam (no stand-in)")
    K.check(bool(Idle.solidAt(None, 0, 64, 0)), "REAL solidAt: no world = solid (never fly into the unknown)")
    W_ = U.allocateInstance(JClass("com.hypixel.hytale.server.core.universe.world.World").class_)
    K.check(bool(Idle.solidAt(W_, 0, 64, 0)) and not bool(Idle.solidAt(W_, 0, 320, 0)) and bool(Idle.solidAt(W_, 0, -1, 0)), "REAL solidAt: unreadable = solid, above the world = air")
    K.eq(int(Idle.motion(None, None, JString("Fly"))), 0, "REAL motion on nothing = 0")
    K.check(not bool(Idle.unmark(None, None)) and not bool(Idle.crouching(None, None)), "REAL unmark + crouching on nothing: never throw")
    K.eq(int(Idle.scan(None, 0.0, 0.0, 0.0, 16.0).size()), 0, "REAL scan without an accessor: empty, never throw")
    K.eq(str(Idle.attitude(None, None)), "", "REAL attitude on nothing: empty")
    # a real Role: hasMotionController + getActiveMotionController().getType() are the engine's own
    mw = JProxy("com.hypixel.hytale.server.npc.movement.controllers.MotionController", dict={"getType": lambda: JString("Walk"), "deactivate": lambda: None, "activate": lambda: None})
    ctrls = JClass("java.util.HashMap")()
    ctrls.put(JString("Walk"), mw)
    Role = JClass("com.hypixel.hytale.server.npc.role.Role")
    rl = U.allocateInstance(Role.class_)

    def fld(c, name):
        while c is not None:
            for f in c.getDeclaredFields():
                if str(f.getName()) == name:
                    f.setAccessible(True)
                    return f
            c = c.getSuperclass()
        raise KeyError(name)
    fld(rl.getClass(), "motionControllers").set(rl, ctrls)
    fld(rl.getClass(), "activeMotionController").set(rl, mw)
    from jpype import JObject
    K.check(bool(rl.hasMotionController(JString("Walk"))) and not bool(rl.hasMotionController(JString("Fly"))), "REAL hasMotionController (the engine's own)")
    MC_ = JClass("com.hypixel.hytale.server.npc.movement.controllers.MotionController")
    K.eq(str(JObject(rl.getActiveMotionController(), MC_).getType()), "Walk", "REAL getActiveMotionController().getType() (the engine's own)")
    K.save()


# ======================================================================================================== AGG
def run_agg(out, jar, scratch, _home):
    W = _idle_world(out, jar, scratch, "agg")
    K, Idle, Cfg, Views, Rd, Fg, ent, second, steer, oref, new_ref, levels, UUID, solid, BR = W["K"], W["Idle"], W["Cfg"], W["Views"], W["Rd"], W["Fg"], W["ent"], W["second"], W["steer"], W["oref"], W["new_ref"], W["levels"], W["UUID"], W["solid"], W["BR"]
    S = W["S"]
    dv = _dv(W)
    d = ent(dv.ref)
    K.eq(str(Cfg.DRAGON_FMODE), "aggressive", "AGG default mode = aggressive")
    for _ in range(3):
        second()
    K.check(bool(dv.iair), "AGG it was flying before the fight")
    op = ent(oref)["pos"]

    def mob(role, off, att="HOSTILE", level=5, **kw):
        u = UUID.randomUUID()
        r = new_ref(u, role, [op[0] + off[0], op[1] + off[1], op[2] + off[2]])
        e = ent(r)
        e["att"] = att
        e.update(kw)
        if level:
            levels[str(u)] = level
        return r
    # ---- every excluded kind, each standing closest: none is ever picked
    bad = []
    bad.append(("a player", mob(None, (2, 0, 0), level=0, player=UUID.randomUUID(), att="HOSTILE")))
    bad.append(("your other pet", mob("Skyy_Pet_Walk", (2.1, 0, 0))))
    bad.append(("another player's pet", mob("Skyy_Pet_Dragon", (2.2, 0, 0))))
    bad.append(("a Tamed role", mob("Tamed_Wolf", (2.3, 0, 0))))
    bad.append(("an _Ally role", mob("Goblin_Ally", (2.4, 0, 0))))
    bad.append(("a passive animal (Neutral attitude + no level)", mob("Cow", (2.5, 0, 0), att="NEUTRAL", level=0)))
    bad.append(("a hostile-attitude bird without a level (Pigeon, the engine's default)", mob("Pigeon", (2.6, 0, 0), att="HOSTILE", level=0)))
    bad.append(("a merchant", mob("Klops_Merchant", (2.7, 0, 0), att="FRIENDLY", level=0)))
    bad.append(("a quest NPC", mob("Skyy_Quest_Npc", (2.8, 0, 0), att="NEUTRAL", level=0)))
    bad.append(("an invulnerable one", mob("Boss_Stage", (2.9, 0, 0), guarded=True)))
    bad.append(("a dead one", mob("Skeleton", (3.0, 0, 0), dead=True)))
    bad.append(("a dormant boss", mob("Dungeon_Dormant_Boss", (3.1, 0, 0))))
    second()
    K.check(dv.ftgt is None and int(Idle.PICKS.get()) == 0, "AGG no pick among every excluded kind: ftgt %s" % dv.ftgt)
    K.check(len(bad) == 12, "AGG 12 excluded kinds tested")
    # ---- each kind on its own, as the closest: the filter names why
    for name, r in bad:
        w = Idle.why(dv, S["st"], r, W["JClass"]("com.skyy.pets.PetFly").orbit(op[0], op[1], op[2], 0.0, 0.0, 0.0, 0.0), ent(r)["pos"] if False else _ja(W, ent(r)["pos"]), int(Fg.now()))
        K.check(w is not None, "AGG never: %s (%s)" % (name, w))
    # ---- zones, sight, worlds
    for name, r in bad:
        ent(r)["pos"] = [op[0] + 99.0, op[1], op[2]]
    z = mob("Skeleton", (5, 0, 0))
    zr = [True]
    zc = [0]

    def zf(a):
        zc[0] += 1
        return W["JClass"]("java.lang.Boolean").valueOf(zr[0])
    BR.put("zones:fn:noSpawn", W["JProxy"]("java.util.function.Function", dict={"apply": zf}))
    second()
    K.check(dv.ftgt is None, "AGG a town / safe zone: no pick (zones:fn:noSpawn)")
    many = [mob("Skeleton", (3 + i * 0.1, 0, 0)) for i in range(9)]
    zc[0] = 0
    second()
    K.check(dv.ftgt is None and 0 < zc[0] <= int(Idle.MAX_TRY), "AGG the dear checks stay capped: %d Zones calls for 10 mobs" % zc[0])
    for r_ in many:
        ent(r_)["pos"] = [op[0] + 99.0, op[1], op[2]]
    zr[0] = False
    ent(z)["pos"] = [op[0] + 99.0, op[1], op[2]]
    # sight line: a wall between you and it
    t2 = mob("Skeleton", (9, 0, 0))
    for y in range(0, 6):
        solid.add((int(math.floor(op[0] + 4.5)), int(math.floor(op[1])) + y, int(math.floor(op[2]))))
    second()
    K.check(dv.ftgt is None and int(Idle.REFUSED.get()) >= 1, "AGG behind a wall: no pick (it would lunge into the cave)")
    solid.clear()
    # worlds
    W["Cfg"].DRAGON_NOAGGRO = "skyy-island-,skyy-shard-"
    dv.world = W["JString"]("skyy-island-abc")
    second(wn="skyy-island-abc")
    K.check(dv.ftgt is None, "AGG on an island: no pick")
    dv.world = W["JString"]("skyy-shard-abc")
    second(wn="skyy-shard-abc")
    K.check(dv.ftgt is None, "AGG on a Combat Shard (Soul Cages): no pick")
    dv.world = W["JString"]("default")
    # other modes
    Cfg.DRAGON_FMODE = "follow"
    second()
    K.check(dv.ftgt is None, "AGG mode follow: no pick")
    K.check(not bool(Fg.defend()), "AGG follow mode: defend() false")
    Cfg.DRAGON_FMODE = "defend"
    second()
    K.check(dv.ftgt is None and bool(Fg.defend()) and not bool(Fg.aggressive()), "AGG mode defend: no pick, defend() true")
    Cfg.DRAGON_FMODE = "aggressive"
    Cfg.DRAGON_FIGHT = False
    second()
    K.check(dv.ftgt is None, "AGG fighting off: no pick")
    Cfg.DRAGON_FIGHT = True
    # no SkyyMobs: no picks
    f0 = BR.remove("mob:fn:level")
    second()
    K.check(dv.ftgt is None, "AGG no SkyyMobs in the set: no pick (no way to tell a fighter from a bird)")
    BR.put("mob:fn:level", f0)
    # ---- the pick: the nearest; keeps at it; air fight
    ent(t2)["pos"] = [op[0] + 10.0, op[1], op[2]]
    near = mob("Skeleton", (6, 0, 0))
    far_ = t2
    ent(z)["pos"] = [op[0] + 15.0, op[1], op[2]]
    bites0 = int(Fg.BITES.get())
    # everything a farm or hub has lying around, all nearer than the mob, more than MAX_TRY of them
    junk = []
    for i in range(10):
        junk.append(new_ref(UUID.randomUUID(), None, [op[0] + 1.0 + i * 0.1, op[1], op[2]], drop=True))
        junk.append(mob("Cow", (1.05 + i * 0.1, 0, 0), att="NEUTRAL", level=0))
        junk.append(mob("Pigeon", (1.02 + i * 0.1, 0, 0), att="HOSTILE", level=0))
    W["idle"]["clobber"] = True          # every level lookup refills the engine's shared list, as a spatial query in another mod would
    second()
    W["idle"]["clobber"] = False
    K.check(dv.ftgt is not None and int(dv.ftgt.getIndex()) == int(near.getIndex()), "AGG the nearest hostile wins, past 30 drops / cows / pigeons (never starved), on a copy of the engine's list")
    for r_ in junk:
        ent(r_)["pos"] = [op[0] + 99.0, op[1], op[2]]
    K.eq(int(dv.fpri), 0, "AGG its own pick = the lowest priority")
    K.check("hostile" in str(dv.fwhy), "AGG the reason is kept: %s" % dv.fwhy)
    K.check(bool(dv.iair) and d["ctrl"] == "Fly", "AGG in an air fight it stays flying (no fall)")
    steer(120)
    fp = d["pos"]
    tp = ent(near)["pos"]
    K.check(_dist2(fp, tp) < 4.5 and abs(fp[1] - tp[1]) < 2.0, "AGG the tick brings it next to the target: %.2f away" % _dist2(fp, tp))
    second()
    K.check(int(Fg.BITES.get()) > bites0, "AGG it bites (the PetFight path)")
    c0 = int(Idle.CALLS.get())
    for _ in range(2):
        W["idle"]["crouch"] = True
        steer(2)
        W["idle"]["crouch"] = False
        steer(2)
    second()
    K.check(int(Idle.CALLS.get()) == c0 and bool(dv.iair) and dv.ftgt is not None, "AGG a double-tap crouch in a fight calls nothing")
    # ---- owner's hit takes over from its own pick
    t0 = dv.ftgt
    K.check(bool(Fg.setTarget(dv, far_, W["JString"]("you hit it"), int(Fg.now()), 2)) and int(dv.ftgt.getIndex()) == int(far_.getIndex()) and int(dv.fpri) == 2, "AGG what you hit (pri 2) takes over at once")
    Fg.drop(dv, W["JString"]("t"))
    # ---- the pick dies -> next
    ent(near)["dead"] = True
    second()
    K.check(dv.ftgt is not None and int(dv.ftgt.getIndex()) != int(near.getIndex()), "AGG it dies: the next one (%s)" % (None if dv.ftgt is None else int(dv.ftgt.getIndex())))
    cur_t = dv.ftgt
    # ---- leaves the range (+4)
    ent(cur_t)["pos"] = [op[0] + 21.0, op[1], op[2]]
    second()
    K.check(dv.ftgt is None or int(dv.ftgt.getIndex()) != int(cur_t.getIndex()), "AGG it leaves the range: dropped")
    for r_ in (t2, z):
        ent(r_)["pos"] = [op[0] + 99.0, op[1], op[2]]
    Fg.drop(dv, W["JString"]("t"))
    second()
    K.check(dv.ftgt is None, "AGG nothing left in range")
    # ---- back to the circle
    steer(50)
    K.check(bool(dv.iair) and not bool(dv.ifought), "AGG the fight over: back on the circle (fought flag cleared, angle from where it is)")
    steer(400)
    K.check(abs(_dist2(d["pos"], op) - 7.0) < 0.8, "AGG ... settled on the circle")
    # ---- range row (live)
    Cfg.DRAGON_AGGRO = 10
    n2 = mob("Skeleton", (12, 0, 0))
    second()
    K.check(dv.ftgt is None, "AGG aggroRange 10: nothing picked at 12")
    Cfg.DRAGON_AGGRO = 16
    second()
    K.check(dv.ftgt is not None and int(dv.ftgt.getIndex()) == int(n2.getIndex()), "AGG aggroRange 16 (live): picked")
    # ---- a target it cannot reach: 20 s, then left alone for 30 s, others still taken
    long_ms = int(Fg.IDLE_MS)
    K.eq(long_ms, 20000, "AGG 20 s rule")
    dv.ftgtAt = int(Fg.now()) - long_ms - 1
    ent(n2)["pos"] = [op[0] + 13.0, op[1], op[2]]
    second()
    K.check(dv.ftgt is None and dv.ibadT is not None and int(dv.ibadT.getIndex()) == int(n2.getIndex()), "AGG nobody got it for 20 s: dropped + noted")
    second()
    K.check(dv.ftgt is None, "AGG ... and left alone for now")
    W["clock"][0] += int(Idle.BAD_MS)
    second()
    K.check(dv.ftgt is not None and int(dv.ftgt.getIndex()) == int(n2.getIndex()), "AGG ... 30 s later it may be picked again")
    Fg.drop(dv, W["JString"]("t"))
    ent(n2)["pos"] = [op[0] + 99.0, op[1], op[2]]
    # ---- scans only once a second (a tick never scans)
    s0 = W["idle"]["scans"][0]
    steer(40)
    K.eq(W["idle"]["scans"][0], s0, "AGG 40 ticks: no scan (the 1 s cadence only)")
    second()
    K.eq(W["idle"]["scans"][0], s0 + 1, "AGG one second: one scan")
    # ---- ridden: no picks
    dv.riding = True
    n3 = mob("Skeleton", (6, 0, 0))
    K.check(not bool(Fg.setTarget(dv, n3, W["JString"]("x"), int(Fg.now()), 0)), "AGG ridden: setTarget refuses")
    dv.riding = False
    # ---- ground dragon: fights on foot as before
    Cfg.DRAGON_IDLE_MODE = "follow"
    Fg.drop(dv, W["JString"]("t"))
    ent(n3)["pos"] = [op[0] + 99.0, op[1], op[2]]
    second()
    K.check(not bool(dv.iair) and d["ctrl"] == "Walk" and dv.ftgt is None and bool(dv.ihold), "AGG follow mode: on the ground, holding a distance")
    n0_ = len(W["sets"])
    ent(n3)["pos"] = [op[0] + 6.0, op[1], op[2]]
    W["marks"].clear()
    second()
    K.check(dv.ftgt is not None and d["ctrl"] == "Walk" and W["marks"].get(int(dv.ref.getIndex())) == int(n3.getIndex()) and not bool(dv.ihold), "AGG on the ground it walks at the target as before (the Seek on the target, hold off)")
    steer(10)
    K.eq(len(W["sets"]), n0_, "AGG ... no flying steps on the ground")
    K.save()


def _ja(W, a):
    from jpype import JArray, JDouble
    return JArray(JDouble)(list(a))


# ======================================================================================================== MIG
def run_mig(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Mg, Log, Cfg = P_("PetsMigDrg"), P_("PetsLog"), P_("PetsCfg")
    Log.LINES = JClass("java.util.ArrayList")()

    def upd(t):
        r = Mg.mgUpdate(JString(t))
        return str(r[0]), int(r[1]), str(r[2]), str(r[3])
    src = "# SkyyPets\npets.enabled=true\npets.dragon.fight.mode=follow\npets.dragon.fight=true\n"
    t1, n1, no1, o1 = upd(src)
    K.check(n1 == 1 and t1 == src.replace("mode=follow", "mode=aggressive") and no1 == "" and o1 == "follow", "MIG untouched follow -> aggressive, nothing else")
    t2, n2, _, _ = upd(src.replace("\n", "\r\n"))
    K.check(n2 == 1 and t2 == t1.replace("\n", "\r\n"), "MIG CRLF kept")
    t3, n3, _, o3 = upd(src.replace("pets.dragon.fight.mode=follow", "pets.dragon.fight.mode = Follow  "))
    K.check(n3 == 1 and "pets.dragon.fight.mode = aggressive  \n" in t3 and o3 == "Follow", "MIG spaces kept, Follow counts as the old default: %r" % t3)
    for v in ("defend",):
        tv, nv, nov, _ = upd(src.replace("mode=follow", "mode=" + v))
        K.check(nv == 0 and tv == src.replace("mode=follow", "mode=" + v) and ("kept hand-set pets.dragon.fight.mode=" + v) in nov, "MIG hand-set %s kept + noted" % v)
    tl, nl, nol, _ = upd(src.replace("mode=follow", "mode=aggressive"))
    K.check(nl == 0 and nol == "", "MIG already aggressive: nothing, no note")
    K.eq(upd("pets.enabled=true\n")[1], 0, "MIG no line = nothing (the new default applies)")
    old_b = src.encode("latin-1")
    K.check(bool(Mg.sameAfter(old_b, t1.encode("latin-1"))) and not bool(Mg.sameAfter(old_b, (t1 + "x=1\n").encode("latin-1"))) and not bool(Mg.sameAfter(old_b, t1.replace("enabled=true", "enabled=false").encode("latin-1"))), "MIG sameAfter: only the planned line may change")
    Paths = JClass("java.nio.file.Paths")
    for tag, data, moved in (("untouched", src.replace("\n", "\r\n").encode("latin-1"), True), ("hand", src.replace("mode=follow", "mode=defend").encode("latin-1"), False)):
        d = os.path.join(scratch, "mig-" + tag, "Skyy_SkyyPets")
        os.makedirs(d, exist_ok=True)
        cfg = os.path.join(d, "config.properties")
        open(cfg, "wb").write(data)
        m1 = str(Mg.run(Paths.get(d)))
        after1 = open(cfg, "rb").read()
        want = data.replace(b"mode=follow", b"mode=aggressive") if moved else data
        K.check(after1 == want and os.path.isfile(os.path.join(d, "migrations", "pets-dr25.done")), "MIG run() %s: file %s, marker written: %s" % (tag, "updated" if moved else "kept", m1[:140]))
        lg = os.path.join(d, "config-changes.log")
        lines = [l for l in open(lg, encoding="utf-8").read().splitlines() if "\tupdate\tpets.dragon.fight.mode\t" in l] if os.path.isfile(lg) else []
        if moved:
            K.check(len(lines) == 1 and lines[0].endswith("\tSkyyPets 0.4.25\t-\tupdate\tpets.dragon.fight.mode\tfollow\taggressive\tok"), "MIG one Changes line (Undo in Server Setup): %s" % lines)
            hd = os.path.join(d, "config-history")
            hist = [os.path.join(dp, f) for dp, _dn, fs in os.walk(hd) for f in fs] if os.path.isdir(hd) else []
            K.check(any(open(h, "rb").read() == data for h in hist), "MIG the History copy holds the old bytes (%d files)" % len(hist))
            K.check("have the dragon target mobs aggressively" in m1, "MIG the INFO line")
        else:
            K.check(lines == [] and "kept hand-set pets.dragon.fight.mode=defend" in m1, "MIG hand-set defend: no Changes line, the note: %s" % m1[-120:])
        m2 = str(Mg.run(Paths.get(d)))
        K.check(m2 == "" and open(cfg, "rb").read() == after1, "MIG %s: a second run = nothing (marker; bytes identical)" % tag)
    d2 = os.path.join(scratch, "mig-fresh", "Skyy_SkyyPets")
    os.makedirs(d2, exist_ok=True)
    K.check("aggressive dragon default applies" in str(Mg.run(Paths.get(d2))) and os.path.isfile(os.path.join(d2, "migrations", "pets-dr25.done")) and not os.path.isfile(os.path.join(d2, "config.properties")), "MIG a fresh home: marker only")
    # the normaliser: an unknown value = the new default; the older jar's own normaliser turns aggressive into follow (rollback note)
    Cfg.DRAGON_FMODE = "bogus"
    a0 = open(GEN, encoding="utf8").read()
    K.check('if (!"aggressive".equals(DRAGON_FMODE) && !"follow".equals(DRAGON_FMODE) && !"defend".equals(DRAGON_FMODE)) DRAGON_FMODE = "aggressive";' in a0, "MIG normaliser: unknown -> aggressive")
    o0 = open(GEN_OLD, encoding="utf8").read()
    K.check('if (!"follow".equals(DRAGON_FMODE) && !"defend".equals(DRAGON_FMODE)) DRAGON_FMODE = "follow";' in o0, "MIG rollback: 0.4.24 reads aggressive as follow")
    K.save()


def run_live2(out, jar, scratch, home):
    """start twice on a scratch COPY of the live folder with 0.4.25's one-time update in the chain"""
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Log, Mg = P_("PetsCfg"), P_("PetStore"), P_("PetsLog"), P_("PetsMigDrg")
    Paths = JClass("java.nio.file.Paths")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.dirname(home)
    cf = os.path.join(home, "config.properties")
    b0 = open(cf, "rb").read() if os.path.isfile(cf) else b""
    had = b"pets.dragon.fight.mode" in b0
    t0 = T41.tree(home)

    def start():
        o_ = str(Mg.run(Paths.get(home)))
        Cfg.load(Paths.get(mods))
        Store.ROOT = Paths.get(home)
        Store.DIR = Store.ROOT.resolve("pets")
        return o_, [int(x) for x in Store.scanAll()]
    o1, sc1 = start()
    print("   live: pets.dragon.fight.mode line in the file: %s; PetsMigDrg: %s" % (had, o1[:200]))
    b1 = open(cf, "rb").read() if os.path.isfile(cf) else b""
    K.check(os.path.isfile(os.path.join(home, "migrations", "pets-dr25.done")), "LIVE2 the marker is written")
    K.check(b1 == b0 or (had and len(b0.splitlines()) == len(b1.splitlines())), "LIVE2 config.properties unchanged, or only the one line")
    K.check(sc1[2] == 0 and sc1[3] == 0, "LIVE2 every pet file reads (%s)" % sc1)
    K.eq(str(Cfg.DRAGON_FMODE), "aggressive" if b"pets.dragon.fight.mode=defend" not in b0 else "defend", "LIVE2 the mode after the start")
    t1 = T41.tree(home)
    o2, sc2 = start()
    K.check(o2 == "" and T41.tree(home) == t1 and sc2 == sc1, "LIVE2 start 2 writes nothing")
    K.check(sorted(x for x in set(t0) | set(t1) if t0.get(x) != t1.get(x) and not x.startswith(("config-history", "migrations", "config.properties", "config-changes"))) == [], "LIVE2 start 1 touched only config files")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("idle", run_idle), ("agg", run_agg), ("real", run_real), ("mig", run_mig), ("ecs", T424.run_ecs), ("ride", _old(T424.run_ride)), ("pt", _old(T423.run_pt)), ("rd", _old(T423.run_rd)), ("live", T417.run_live), ("live2", run_live2)],
           script=__file__, live=(T423.T422.T421.T41.LIVE, "Skyy_SkyyPets"))
