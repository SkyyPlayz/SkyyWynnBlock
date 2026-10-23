"""Harness for SkyyPets 0.4.13 (RIDE + FLY YOUR DRAGON: research/Dragon-Pet-Spec.md 5 / 6 = round D3; Pet-Core-Spec phase 5;
tools/pets_0_4_13_patch.py). Build first:
    python tools/pets_0_4_13_patch.py && python SkyyPets/build_skyypets_0.4.13.py
    python SkyyPets/test_skyypets_0.4.13.py [--keep] [--expect-dump]

  S     static   the patch re-runs to identical bytes; 2 new classes (PetRide, PetRideJob) + the PetRideApi seam, no new system, no new
                 command; line endings kept; the jar: + the 3 movement configs (Parent Mount, our numbers, never Aures'), the only changed
                 non-class entry = manifest.json; the 19 new rows in the default file
  A/C/AA          (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.12 -> 0.4.13, engine-access audit
  R     EXECUTED on a stand-in world (PetWorld.API + PetRide.API, real PetViews / PetFight): the saddle in the spec from the ride level;
                 F below the ride level = pet + the level hint; someone else's F = "That is <owner>'s dragon." (no mount); YOUR F = the
                 mount job (seat x size, the preset's movement config), it takes (the ride line), no fighting while ridden; FLY mode: the
                 flight switch in the air / on the ground, the live speed rows; MODE SWITCH fly -> glide (flight off) and back; a live
                 PRESET edit re-applies the movement; a level-up waits until you get off; GETTING OFF in the air = the landing (PetFly step
                 next to you, then done; a stuck one hops after 8 s); the RETRY (1 s, once) and the give-up (3 s, movement reset); BLOCKED
                 worlds (F refused, a rider there put off); riding switched off mid-ride; the VOID (ridden + riderless: the rider put off,
                 DOWN + the line, back after the cooldown); a Horse in the summon slot rides at any level (vanilla Mount, its seat, no
                 flight); the saddle item row; the ghost sweep of a pet saved while ridden; the seat / item check hooks; the card lines;
                 the REAL seams never throw without an engine; FIX ROUND: the flight re-set after an outside reset, no pass-through
                 while ridden, the ride level never below the Flyling stage, the landSeconds row, the seat rows behind Advanced, the real
                 fly() only undoing our own Forced flight; FIX ROUND 2: a stuck mount (component on, nobody seated) cleared at the
                 give-up / when F finds it / when a rider is put off mid-mount (F works again), the preset scaling the flight, no
                 target taken while ridden, the ride line naming the way off
  M/F/DG/VW/ST  0.4.12's / 0.4.11's phases EXECUTED on this jar (the card's new ride line), EL410 0.4.10's element phase
  LIVE  START TWICE on a scratch COPY of the live Skyy_SkyyPets (0.4.11's live phase): nothing written, the new rows at their defaults
NOT COVERED (UNVERIFIED in game): the client really flying a mount with FlyMode Forced (learned from DarkMatter Mounts, read only), the
seat heights, the glide presets' feel, NPCMountSystems$OnAdd sending MountNPC for our code mount (P10 passed in 0.1 probe), the dismount
key while flying, the engine's own void kill of a ridden dragon.
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util, subprocess, inspect

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "dragond3", "pets")]
import skyybuild as B
import harness_kit as HK

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq
_s412 = importlib.util.spec_from_file_location("test_skyypets_0_4_12", os.path.join(HERE, "test_skyypets_0.4.12.py"))
T412 = importlib.util.module_from_spec(_s412)
_s412.loader.exec_module(T412)
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T411, T410, T44, T41 = T412.T411, T412.T410, T412.T44, T412.T41

VERSION = "0.4.13"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.12.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.12.py")
PATCH = os.path.join(TOOLS, "pets_0_4_13_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T412.PKG = T411.PKG = T44.PKG = T410.PKG = PKG
T412.JAR, T412.OLD_JAR = JAR, OLD_JAR
T411.JAR, T411.OLD_JAR = JAR, OLD_JAR
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "PetDragon": ["~m card"], "PetFight": ["~m dragonOf", "~m setTarget"],
    "PetView": ["+f flyH", "+f flyOn", "+f flyV", "+f landAt", "+f landing", "+f moveId", "+f netId", "+f rideAt", "+f rideHint", "+f rideTries", "+f riding", "~c "],
    "PetViews": ["~m onLoad", "~m onRemoved", "~m pass", "~m reconcile", "~m removeHere", "~m removeQueued", "~m spawnNow", "~m steer", "~m upkeep", "~m use", "~m want"],
    "PetsCfg": ["+f DRAGON_ANCHOR_DRAGONFIRE", "+f DRAGON_ANCHOR_DRAGONPLAIN", "+f DRAGON_ANCHOR_DRAGONSKY", "+f DRAGON_ANCHOR_DRAGONSTORM", "+f DRAGON_ANCHOR_DRAGONTUNDRA",
                "+f DRAGON_FLY_CLIMB", "+f DRAGON_FLY_SPEED", "+f DRAGON_LAND_S", "+f DRAGON_RIDE", "+f DRAGON_RIDE_BLOCKED", "+f DRAGON_RIDE_LV", "+f DRAGON_RIDE_MODE", "+f DRAGON_RIDE_PRESET",
                "+f DRAGON_SADDLE", "+f DRAGON_VOID_Y", "+f MOUNT_ANCHOR_CAMEL", "+f MOUNT_ANCHOR_HORSE", "+f MOUNT_ANCHOR_RAM", "+f MOUNT_RIDE", "~<clinit>",
                "~m applyAll", "~m applyScalars", "~m seed"],
    "PetsMigP5": ["~m mgLog", "~m run"], "SkyyPetsPlugin": ["~m setup", "~m start"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["PetRide", "PetRideApi", "PetRideJob"]
MOVES = ["Server/Entity/MovementConfig/Skyy_Dragon_Glide_Slow.json", "Server/Entity/MovementConfig/Skyy_Dragon_Glide.json",
         "Server/Entity/MovementConfig/Skyy_Dragon_Glide_Fast.json"]
NEW_ROWS = ["pets.dragon.ride", "pets.dragon.rideLevel", "pets.dragon.saddleItem", "pets.dragon.ride.mode", "pets.dragon.ride.preset",
            "pets.dragon.fly.speed", "pets.dragon.fly.climb", "pets.dragon.ride.blockedWorlds", "pets.dragon.voidY", "pets.dragon.ride.landSeconds",
            "pets.dragon.anchor.DragonPlain", "pets.dragon.anchor.DragonTundra", "pets.dragon.anchor.DragonFire", "pets.dragon.anchor.DragonStorm",
            "pets.dragon.anchor.DragonSky", "pets.mount.ride", "pets.mount.anchor.Camel", "pets.mount.anchor.Horse", "pets.mount.anchor.Ram"]
CARD_OLD = "Riding and flying come in a later version."


def _eq(self, got, want, what):
    """the C compare: the non-class entries that changed = manifest.json + our 3 new movement configs"""
    if what == "C: non-class entries changed" and want == ["manifest.json"]:
        return self.check(sorted(got) == sorted(["manifest.json"] + MOVES), "C: non-class entries changed = manifest.json + the 3 movement configs: %s" % sorted(got))
    return _eq00(self, got, want, what)


HK.Child.eq = _eq


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.13 - build script') and g.count('VERSION = "0.4.13"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem("), "S no new system, no new command")
    K.check(g.count("= cls(") == o.count("= cls(") + 2 and 'rdc = cls("PetRide")' in g and 'rjb = cls("PetRideJob")' in g and 'pool.makeInterface(PKG + ".PetRideApi")' in g,
            "S the new classes: PetRide, PetRideJob + PetRideApi")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    z, oz = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    K.eq(sorted(x for x in set(z.namelist()) - set(oz.namelist()) if not x.endswith(".class")), sorted(MOVES), "S the jar's only new non-class entries = our 3 movement configs")
    ch = sorted(n for n in set(z.namelist()) & set(oz.namelist()) if not n.endswith(".class") and not n.endswith("/") and z.read(n) != oz.read(n))
    K.eq(ch, ["manifest.json"], "S the only changed non-class entry = manifest.json")
    az = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    mnt = json.loads(az.read("Server/Entity/MovementConfig/Mount.json").decode("utf-8-sig"))
    names = set(az.namelist())
    fs = [json.loads(z.read(m)) for m in MOVES]
    K.check(all(f["Parent"] == "Mount" and set(f) - {"Parent"} <= set(mnt) for f in fs) and not any(m in names for m in MOVES),
            "S the movement configs: Parent = vanilla Mount, only Mount.json keys, no vanilla path")
    K.check(fs[0]["JumpForce"] < fs[1]["JumpForce"] < fs[2]["JumpForce"] and fs[1]["JumpForce"] == round(mnt["JumpForce"] * 1.5, 2)
            and all(f["AirDragMax"] > mnt["AirDragMax"] for f in fs) and fs[0]["BaseSpeed"] < fs[2]["BaseSpeed"],
            "S Slow < Normal < Fast, Normal = 1.5 x the vanilla jump, less air drag than vanilla: %s" % [f["JumpForce"] for f in fs])
    nk = [n for n in os.listdir(os.path.join(B.USERDATA, "Mods")) if "Dragon Nestkeeper" in n]
    if nk:
        nz = zipfile.ZipFile(os.path.join(B.USERDATA, "Mods", nk[-1]))
        theirs = [json.loads(nz.read(n).decode("utf-8-sig")) for n in nz.namelist() if n.startswith("Server/Entity/MovementConfig/") and n.endswith(".json")]
        same = [(k, f[k]) for f in fs for t in theirs for k in ("JumpForce", "AirDragMin", "AirDragMax", "AirControlMaxMultiplier", "BaseSpeed") if k in t and t[k] == f[k]]
        K.check(theirs and not same, "S never Aures' movement numbers (%d of their configs compared, read only): %s" % (len(theirs), same))
    K.check("if (!on && s.fly != @FLYM@.Forced) return false;" in g and g.count("return s.fly == @FLYM@.Forced ? 1 : 0;") == 1,
            "S fix: the real fly() only undoes our Forced flight; flyState reads the live setting")
    K.check(g.count('"", "40", "", "", "live,adv",') == 2 and 'r[9] == "live,adv" for r in RIDE_ROWS if ".anchor." in r[0]' in g, "S fix: the 8 seat rows behind Advanced")
    man = json.loads(z.read("manifest.json"))
    K.check("ride and fly them from Lv 10" in json.dumps(man), "S the manifest text")
    K.save()


# ======================================================================================================== R: riding on a stand-in world
def run_r(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "r")
    K, JClass, JProxy = W["K"], W["JClass"], W["JProxy"]
    from jpype import JString, JArray, JDouble, JFloat, JObject
    P_ = lambda n: JClass(PKG + n)
    Dg, Cfg, Views, PW, Store, Ops, Fg, Rd = (P_("PetDragon"), P_("PetsCfg"), P_("PetViews"), P_("PetWorld"), P_("PetStore"), P_("PetOps"),
                                              P_("PetFight"), P_("PetRide"))
    told = []
    names = {"00000000-0000-0000-0000-000000009901": "Rider", "00000000-0000-0000-0000-000000009902": "Other"}
    P_("PetsEng").API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, list(W["names"])), "byName": lambda n: None,
                                                      "nameOf": lambda u: names.get(str(u), "?"), "tell": lambda u, t, c: told.append((names.get(str(u), "?"), str(t)))})
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    Ref, Store_, World, RR = (JClass("com.hypixel.hytale.component.Ref"), JClass("com.hypixel.hytale.component.Store"),
                              JClass("com.hypixel.hytale.server.core.universe.world.World"), JClass("com.hypixel.hytale.component.RemoveReason"))
    Dmg, ES = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage"), JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    UUID = W["UUID"]
    st = U.allocateInstance(Store_.class_)
    w = U.allocateInstance(World.class_)
    ents, jobs, calls = {}, [], []
    nxt = [200]

    def new_ref(uuid, role, pos, player=None):
        nxt[0] += 1
        r = Ref(st, nxt[0])
        ents[int(r.getIndex())] = {"uuid": uuid, "role": role, "pos": list(pos), "removed": False, "ref": r, "player": player, "net": nxt[0] + 5000,
                                   "ground": 1, "tags": ""}
        return r
    ent = lambda r: None if r is None else ents.get(int(r.getIndex()))
    uo = UUID.fromString("00000000-0000-0000-0000-000000009901")
    ux = UUID.fromString("00000000-0000-0000-0000-000000009902")
    oref = new_ref(uo, None, [10.0, 70.0, 10.0], player=uo)
    xref = new_ref(ux, None, [11.0, 70.0, 10.0], player=ux)
    roles = {"Skyy_Pet_Walk": 11, "Skyy_Pet_Fly": 12, "Skyy_Pet_Dragon": 13, "Test_Pet": 7, "Test_Fly": 8, "Empty_Role": 3}

    def spawn(s, role, x, y, z, yaw, model):
        rn = [k for k, v in roles.items() if v == int(role)][0]
        r = new_ref(UUID.randomUUID(), rn, [float(x), float(y), float(z)])
        ent(r)["model"] = str(model)
        calls.append(("spawn", rn, str(model)))
        return r

    def pos(acc, r):
        e = ent(r)
        return None if e is None or e["removed"] else JArray(JDouble)(e["pos"])

    def remove(acc, r):
        e = ent(r)
        if e is None or e["removed"]:
            return False
        e["removed"] = True
        calls.append(("remove", e["role"]))
        return True

    def setpos(acc, r, x, y, z, yaw):
        calls.append(("setPos", round(float(x), 2), round(float(y), 2), round(float(z), 2)))
        ent(r)["pos"] = [float(x), float(y), float(z)]

    def tele(acc, r, x, y, z, yaw):
        calls.append(("teleport", (ent(r) or {}).get("role"), round(float(x), 2), round(float(y), 2), round(float(z), 2)))
        ent(r)["pos"] = [float(x), float(y), float(z)]
    api = {"roleIndex": lambda role: roles.get(str(role), -1), "model": lambda m, s: JString("%s@%s" % (m, round(float(s), 3))),
           "modelPinned": lambda m, s, seed: JString("%s@%s#%s" % (m, round(float(s), 3), seed)),
           "spawn": spawn, "store": lambda w_: st, "ownerRef": lambda u_: oref if str(u_) == str(uo) else (xref if str(u_) == str(ux) else None),
           "refOf": lambda w_, u_: None, "execute": lambda w_, r_: (jobs.append(r_), True)[1], "pos": pos, "setPos": setpos, "teleport": tele,
           "dead": lambda acc, r: False, "uuid": lambda acc, r: (ent(r) or {}).get("uuid"), "roleOf": lambda acc, r: (ent(r) or {}).get("role"),
           "tags": lambda acc, r: JString((ent(r) or {}).get("tags", "")), "prepare": lambda acc, r, t: None, "plate": lambda acc, r, t: None,
           "clearDebug": lambda acc, r: None, "mark": lambda acc, r, o: calls.append(("mark",)), "remove": remove,
           "hearts": lambda *a: calls.append(("hearts",)), "anim": lambda *a: None, "stopAnim": lambda *a: None,
           "vanillaScale": lambda mid: 1.55 if "Plain_4" in str(mid) else 1.0, "fx": lambda *a: None,
           "passthrough": lambda acc, r, m: (calls.append(("pass", str(m))), JString(str(m)))[1]}
    PW.API = JProxy(PKG + "PetWorldApi", dict=api)
    # ---- the ride seam: who rides what (the player's mount id = the creature's network id), the flight, the movement
    rider = {"mid": 0, "take": True, "stuck": False, "fly": None, "flyH": 0.0, "flyV": 0.0, "move": None, "held": None, "comp": set()}

    def r_mount(s, pet, o, ax, ay, az, mv):
        calls.append(("mount", str(mv), round(float(ax), 3), round(float(ay), 3), round(float(az), 3)))
        rider["move"] = str(mv)
        if rider["take"]:
            rider["mid"] = ent(pet)["net"]
            rider["comp"].add(int(pet.getIndex()))
        elif rider["stuck"]:          # fix round 2: the engine keeps the mount component but never seats the owner
            rider["comp"].add(int(pet.getIndex()))
        return JString("")

    def r_unmount(acc, r_):
        had = int(r_.getIndex()) in rider["comp"]
        calls.append(("unmount",))
        rider["comp"].discard(int(r_.getIndex()))
        return had

    def r_dismount(acc, o):
        calls.append(("dismount",))
        rider["mid"] = 0
        rider["comp"].clear()
        rider["move"] = None
        rider["fly"] = None

    def r_fly(acc, o, on, h, v):
        calls.append(("fly", bool(on), round(float(h), 2), round(float(v), 2)))
        rider["fly"], rider["flyH"], rider["flyV"] = bool(on), float(h), float(v)
        return True

    def r_move(acc, o, mid):
        calls.append(("move", str(mid)))
        rider["move"] = str(mid)
        return True
    rapi = {"mount": r_mount, "mountedId": lambda acc, o: int(rider["mid"]) if str((ent(o) or {}).get("uuid")) == str(uo) else 0,
            "netId": lambda acc, r: int((ent(r) or {}).get("net", 0)), "hasMount": lambda acc, r: r is not None and int(r.getIndex()) in rider["comp"], "unmount": r_unmount,
            "dismount": r_dismount, "resetMove": lambda acc, o: (calls.append(("resetMove",)), True)[1], "move": r_move,
            "ground": lambda acc, r: int((ent(r) or {}).get("ground", -1)), "fly": r_fly,
            "flyState": lambda acc, o: -1 if rider["fly"] is None else (1 if rider["fly"] else 0),
            "saddled": lambda m, s, seed: (calls.append(("saddled", str(m), round(float(s), 3))), JString("%s@%s#%s+saddle" % (m, round(float(s), 3), seed)))[1],
            "held": lambda s, o: rider["held"]}
    Rd.API = JProxy(PKG + "PetRideApi", dict=rapi)
    hp = {}
    Fg.API = JProxy(PKG + "PetFightApi", dict={"hit": lambda cb, t, src, cause, amt: True, "health": lambda acc, r_: JArray(JFloat)(hp.get(int(r_.getIndex()), [100.0, 0.0, 100.0])),
                                               "playerOf": lambda acc, r_: (ent(r_) or {}).get("player"), "guarded": lambda acc, r_: False})
    Cfg.SPAWN_DELAY = 0
    Cfg.SLOT2_MODE = "always"
    W["names"][str(uo)] = "Rider"
    key = str(Store.pkey(uo))
    Store.KEYOF.put(uo, key)
    r = Store.get(key)
    r.set("starter", "1")
    pid = str(Ops.create(r, None, "DragonPlain", 3, 9, 0, "test", "harness", False))
    r.set("active.2", pid)
    clock = [0]

    def second(plus=1000, world="default"):
        clock[0] += plus
        Fg.NOW_OFF = clock[0]
        Rd.NOW_OFF = clock[0]
        Views.second(uo, oref, st, None, w, world)
        while jobs:
            jobs.pop(0).run()

    def ticks(n=1, dt=0.05):
        for _ in range(n):
            Views.steer(uo, oref, None, float(dt))
    now = lambda: int(Rd.now())
    Views.SEEN.put(uo, JArray(JObject)(["default", JClass("java.lang.Long").valueOf(0)]))
    # ---- Lv 9 (a Biteling): no saddle, F = pet it + the level hint
    wt = str(Views.want(uo, r, key, 2, "default", False))
    K.check(wt.endswith("|Nestkeeper_Dragon_Plain_3|-1.0|0") and "|S" not in wt, "R Lv 9: no saddle in the spec: %s" % wt)
    second(0)
    second(0)
    v = Views.view(uo, 2)
    K.check(v is not None and not [c for c in calls if c[0] == "saddled"], "R the Lv 9 dragon is out (no saddle model)")
    told[:] = []
    k = int(Views.use(uo, v, now()))
    K.check(k == 3 and ("Rider", "[Pets] Your dragon can carry you from Lv 10.") in told and not [j for j in jobs if "PetRideJob" in str(j.getClass().getName())] and int(Rd.ASKED.get()) == 0,
            "R F below the ride level: petted (3) + the level hint, no mount: %s" % told)
    jobs[:] = []
    # ---- Lv 10: the saddle (the spec's 7th part) + the Flyling
    r.set("pet.%s.level" % pid, "10")
    wt = str(Views.want(uo, r, key, 2, "default", False))
    K.check(wt.endswith("|Nestkeeper_Dragon_Plain_4|-1.0|0|S"), "R Lv 10: the Flyling + |S (the saddle): %s" % wt)
    calls[:] = []
    second()
    second()
    v = Views.view(uo, 2)
    sad = [c for c in calls if c[0] == "saddled"]
    K.check(v is not None and sad == [("saddled", "Nestkeeper_Dragon_Plain_4", 1.55)] and ("spawn", "Skyy_Pet_Dragon", "Nestkeeper_Dragon_Plain_4@1.55#%s+saddle" % pid) in calls,
            "R spawnNow: the saddled pinned model (x1.55): %s" % sad)
    dref = v.ref
    ent(dref)["pos"] = [8.6, 70.0, 11.2]
    # ---- someone else's F
    told[:] = []
    k = int(Views.use(ux, v, now()))
    K.check(k == 1 and told == [("Other", "[Pets] That is Rider's dragon.")] and not jobs, "R another player's F: 'That is Rider's dragon.', nothing else: %s" % told)
    # ---- YOUR F: the mount job (world thread), the seat x size, the preset's movement config, the ride line, no fighting
    mob = new_ref(UUID.randomUUID(), "Trork_Warrior", [14.0, 70.0, 10.0])
    Fg.inspect(None, mob, Dmg(ES(oref), 0, 20.0))
    K.check(v.ftgt == mob, "R (before riding: your hit = its target)")
    told[:] = []
    calls[:] = []
    k = int(Views.use(uo, v, now()))
    K.check(k == 4 and len(jobs) == 1 and int(Rd.ASKED.get()) == 1, "R your F at Lv 10: the mount is queued on the world thread (4)")
    jobs.pop(0).run()
    mt = [c for c in calls if c[0] == "mount"]
    K.check(len(mt) == 1 and mt[0][:3] == ("mount", "Skyy_Dragon_Glide", 0.0) and abs(mt[0][3] - 1.05 * 1.55) < 0.002 and mt[0][4] == 0.0 and v.ftgt is None and int(v.netId) == ent(dref)["net"] and int(Rd.MOUNTS.get()) == 1,
            "R the mount: Normal preset Skyy_Dragon_Glide, seat 1.05 x 1.55 = %.3f, its target dropped: %s" % (1.05 * 1.55, mt))
    second()
    K.check(bool(v.riding) and int(Rd.RIDES.get()) == 1 and any("You ride your Plain Dragon. Jump to take off" in t for _n, t in told), "R it took: riding + the ride line: %s" % told)
    k = int(Views.use(uo, v, now()))
    K.check(k == 5 and not jobs, "R F while riding: nothing (5)")
    Fg.inspect(None, mob, Dmg(ES(oref), 0, 20.0))
    K.check(v.ftgt is None and Fg.dragonOf(uo, None) is None, "R a ridden dragon takes no target (your hit while riding)")
    K.check(not bool(Fg.setTarget(v, mob, "it hit your dragon", now(), 1)) and v.ftgt is None, "R fix 2: a mob hitting a ridden dragon queues no target either")
    K.check(any(t.endswith("Land to walk. Get off as from a horse.") for _n, t in told), "R fix 2: the ride line names the way off: %s" % told)
    calls[:] = []
    second()
    K.check(not [c for c in calls if c[0] in ("mark", "teleport", "remove")], "R riding: no follow mark / teleport / removal: %s" % calls)
    K.check(("pass", "off") in calls, "R fix: a ridden dragon is not pass-through (spec 4): %s" % [c for c in calls if c[0] == "pass"])
    # ---- FLY mode: in the air = flight on (the live speed rows), on the ground = off; one switch each
    calls[:] = []
    ticks(3)
    K.check([c for c in calls if c[0] == "fly"] == [("fly", False, 12.0, 8.0)], "R on the ground: flight off (sent once): %s" % calls)
    ent(dref)["ground"] = 0
    calls[:] = []
    ticks(3)
    K.check([c for c in calls if c[0] == "fly"] == [("fly", True, 12.0, 8.0)] and rider["fly"] is True, "R it left the ground: flight ON (Forced) at 12 / 8 blocks a second: %s" % calls)
    Cfg.DRAGON_FLY_SPEED = 20.0
    calls[:] = []
    ticks(2)
    K.check([c for c in calls if c[0] == "fly"] == [("fly", True, 20.0, 8.0)], "R a live speed edit: re-sent once at 20: %s" % calls)
    rider["fly"] = False          # another mod (/fly off) reset the rider's movement mid-flight
    calls[:] = []
    second()
    ticks(1)
    K.check(int(Rd.REFLY.get()) == 1 and [c for c in calls if c[0] == "fly"] == [("fly", True, 20.0, 8.0)] and rider["fly"] is True,
            "R fix: flight reset from outside while flying: re-checked within a second and set again: %s" % calls)
    calls[:] = []
    second()
    ticks(1)
    K.check(int(Rd.REFLY.get()) == 1 and not [c for c in calls if c[0] == "fly"], "R ... and nothing more while it holds")
    ent(dref)["ground"] = -1
    calls[:] = []
    ticks(2)
    K.check(not [c for c in calls if c[0] == "fly"], "R unknown ground state: no switch")
    # ---- MODE SWITCH fly -> glide (flight off) -> fly
    ent(dref)["ground"] = 0
    Cfg.DRAGON_RIDE_MODE = "glide"
    calls[:] = []
    ticks(3)
    K.check([c for c in calls if c[0] == "fly"] == [("fly", False, 0.0, 0.0)] and rider["fly"] is False, "R mode -> glide: flight off once, then nothing: %s" % calls)
    Cfg.DRAGON_RIDE_MODE = "fly"
    calls[:] = []
    ticks(2)
    K.check([c for c in calls if c[0] == "fly"] == [("fly", True, 20.0, 8.0)], "R mode -> fly again: flight back on: %s" % calls)
    Cfg.reloadAll()
    Cfg.SPAWN_DELAY, Cfg.SLOT2_MODE = 0, "always"
    # ---- a live PRESET edit re-applies the movement
    Cfg.DRAGON_RIDE_PRESET = "fast"
    calls[:] = []
    second()
    K.check(("move", "Skyy_Dragon_Glide_Fast") in calls and str(v.moveId) == "Skyy_Dragon_Glide_Fast" and int(v.flyOn) == -1, "R preset -> Fast: the movement re-applied live: %s" % calls)
    calls[:] = []
    second()
    K.check(not [c for c in calls if c[0] == "move"], "R ... once")
    ticks(1)
    K.check([c for c in calls if c[0] == "fly"] == [("fly", True, 15.0, 10.0)], "R fix 2: Fast scales the flight too (12 / 8 x 1.25): %s" % calls)
    Cfg.DRAGON_RIDE_PRESET = "slow"
    second()
    calls[:] = []
    ticks(1)
    K.check([c for c in calls if c[0] == "fly"] == [("fly", True, 9.6, 6.4)], "R fix 2: Slow = x0.8: %s" % calls)
    Cfg.DRAGON_RIDE_PRESET = "normal"
    second()
    # ---- a level-up while riding: the creature stays until you get off
    r.set("pet.%s.level" % pid, "11")
    calls[:] = []
    second()
    second()
    K.check(str(Views.view(uo, 2).uuid) == str(v.uuid) and not [c for c in calls if c[0] in ("remove", "spawn")], "R a level-up mid-flight: no swap under you")
    # ---- GET OFF in the air: the landing next to you
    ent(dref)["pos"] = [10.0, 90.0, 10.0]
    ent(dref)["ground"] = 0
    rider["mid"] = 0
    rider["comp"].clear()
    calls[:] = []
    second(0)
    K.check(not bool(v.riding) and bool(v.landing) and int(Rd.DISMOUNTS.get()) == 1, "R you got off in the air: landing")
    K.check(str(Views.view(uo, 2).uuid) == str(v.uuid), "R (the deferred look waits for the landing second)")
    calls[:] = []
    ticks(4, 0.1)
    steps = [c for c in calls if c[0] == "setPos"]
    K.check(len(steps) == 4 and steps[0][2] < 90.0 and steps[-1][2] < steps[0][2] and abs(steps[-1][1] - 8.6) < abs(10.0 - 8.6) + 0.5,
            "R the landing: the PetFly step down towards your side each tick: %s" % steps[:2])
    ent(dref)["pos"] = [8.8, 70.2, 11.3]
    ticks(1)
    K.check(not bool(v.landing) and int(Rd.LANDINGS.get()) == 1, "R next to you: landed")
    calls[:] = []
    second()
    second()
    v2 = Views.view(uo, 2)
    K.check(str(v2.uuid) != str(v.uuid) and ("remove", "Skyy_Pet_Dragon") in calls and [c for c in calls if c[0] == "spawn"], "R off it: the waiting level-up look comes now")
    v = v2
    dref = v.ref
    ent(dref)["pos"] = [8.6, 70.0, 11.2]
    # ---- a stuck landing hops after 8 s
    v.landing = True
    v.landAt = now()
    ent(dref)["pos"] = [10.0, 120.0, 10.0]
    Rd.NOW_OFF = clock[0] + 9000
    calls[:] = []
    ticks(1)
    K.check([c for c in calls if c[0] == "teleport"] == [("teleport", "Skyy_Pet_Dragon", 8.6, 70.0, 11.2)] and not bool(v.landing), "R a landing past 8 s: it hops next to you: %s" % calls)
    Rd.NOW_OFF = clock[0]
    Cfg.DRAGON_LAND_S = 3
    v.landing = True
    v.landAt = now()
    ent(dref)["pos"] = [10.0, 120.0, 10.0]
    Rd.NOW_OFF = clock[0] + 2000
    calls[:] = []
    ticks(1)
    K.check(bool(v.landing) and not [c for c in calls if c[0] == "teleport"], "R fix: landSeconds 3 - still gliding at 2 s")
    Rd.NOW_OFF = clock[0] + 3500
    ticks(1)
    K.check(not bool(v.landing) and [c for c in calls if c[0] == "teleport"], "R fix: landSeconds 3 - it hops at 3.5 s (the row, not a constant)")
    Cfg.DRAGON_LAND_S = 8
    Rd.NOW_OFF = clock[0]
    # ---- THE RETRY: the first try does not take (no NPCMountComponent) -> once after 1 s; then the give-up after 3 s
    rider["take"] = False
    told[:] = []
    calls[:] = []
    Views.use(uo, v, now())
    jobs.pop(0).run()
    second(1000)
    K.check(int(Rd.RETRIES.get()) == 1 and len([c for c in calls if c[0] == "mount"]) == 2, "R not riding 1 s later: ONE retry (the P10 rule): %s" % [c for c in calls if c[0] == "mount"])
    second(1000)
    second(1000)
    second(1000)
    K.check(len([c for c in calls if c[0] == "mount"]) == 2 and ("resetMove",) in calls and int(Rd.FAILS.get()) == 1 and int(v.rideAt) == 0
            and any("could not carry you - press F on it again" in t for _n, t in told), "R still not riding 3 s after the retry: give up, your movement reset, one line: %s" % told)
    K.check(("unmount",) not in calls and int(Rd.UNSTUCK.get()) == 0, "R (no component left there: nothing to clear)")
    # ---- fix 2: the engine kept the mount component on it but never seated you -> no retry, the give-up clears it, F works again
    rider["stuck"] = True
    told[:] = []
    calls[:] = []
    K.check(int(Views.use(uo, v, now())) == 4, "R (F again after the give-up)")
    jobs.pop(0).run()
    K.check(int(dref.getIndex()) in rider["comp"] and int(rider["mid"]) == 0, "R (the stuck mount: component on, nobody seated)")
    second(1000)
    second(1000)
    K.check(int(Rd.RETRIES.get()) == 1 and len([c for c in calls if c[0] == "mount"]) == 1, "R fix 2: a stuck mount gets no retry")
    second(1000)
    K.check(("unmount",) in calls and not rider["comp"] and int(Rd.UNSTUCK.get()) == 1 and int(Rd.FAILS.get()) == 2 and int(v.rideAt) == 0,
            "R fix 2: the give-up clears the stuck mount (component off, its role back): %s" % calls)
    rider["stuck"] = False
    rider["take"] = True
    calls[:] = []
    K.check(int(Views.use(uo, v, now())) == 4, "R fix 2: F works again after a stuck mount")
    jobs.pop(0).run()
    second()
    K.check([c for c in calls if c[0] == "mount"] and bool(v.riding), "R ... and it carries you")
    rider["mid"] = 0
    rider["comp"].clear()
    second()
    v.landing = False
    # F finds a stuck component (you are not on it): cleared + "still settling", no mount this time; the next F rides
    rider["comp"].add(int(dref.getIndex()))
    told[:] = []
    calls[:] = []
    K.check(int(Views.use(uo, v, now())) == 4, "R (F with a stuck component)")
    jobs.pop(0).run()
    K.check(("unmount",) in calls and not [c for c in calls if c[0] == "mount"] and not rider["comp"] and int(Rd.UNSTUCK.get()) == 2 and int(v.rideAt) == 0
            and ("Rider", "[Pets] Your Plain Dragon is still settling - press F on it again.") in told, "R fix 2: F on a stuck mount clears it + tells you: %s" % told)
    # a rider put off mid-mount (component on, not seated yet): the component goes too
    v.rideAt = now()
    rider["comp"].add(int(dref.getIndex()))
    calls[:] = []
    K.check(bool(Rd.release(None, v, oref, "test")) and ("unmount",) in calls and ("resetMove",) in calls and not rider["comp"] and int(Rd.UNSTUCK.get()) == 3,
            "R fix 2: put off mid-mount: the component is cleared, your movement reset: %s" % calls)
    # ---- BLOCKED worlds
    Cfg.DRAGON_RIDE_BLOCKED = "default"
    told[:] = []
    k = int(Views.use(uo, v, now()))
    K.check(k == 5 and not jobs and ("Rider", "[Pets] No riding in this world.") in told and int(Rd.REFUSED.get()) == 1, "R F in a blocked world: refused: %s" % told)
    Cfg.DRAGON_RIDE_BLOCKED = ""
    Views.use(uo, v, now() + 6000)
    jobs.pop(0).run()
    second()
    K.check(bool(v.riding), "R (riding again)")
    Cfg.DRAGON_RIDE_BLOCKED = "Dungeon, default"
    told[:] = []
    calls[:] = []
    second()
    K.check(not bool(v.riding) and ("dismount",) in calls and int(Rd.BLOCKS.get()) == 1 and any("No riding in this world. You got off your Plain Dragon." in t for _n, t in told),
            "R the world becomes blocked (live): you get off at once: %s" % told)
    calls[:] = []
    second()
    K.check(("pass", "all") in calls, "R fix: off it again = pass-through as the row says: %s" % [c for c in calls if c[0] == "pass"])
    Cfg.DRAGON_RIDE_BLOCKED = ""
    v.landing = False
    # ---- riding switched off mid-ride
    Views.use(uo, v, now() + 20000)
    jobs.pop(0).run()
    second()
    Cfg.DRAGON_RIDE = False
    calls[:] = []
    second()
    K.check(not bool(v.riding) and ("dismount",) in calls and "Riding dragons is off on this server." in str(Rd.cardLine("DragonPlain", 11)), "R riding switched off mid-ride: you get off; the card says so")
    Cfg.DRAGON_RIDE = True
    v.landing = False
    # ---- THE VOID while ridden: the rider is put off (falls), DOWN + the line, nothing lost
    Views.use(uo, v, now() + 40000)
    jobs.pop(0).run()
    second()
    K.check(bool(v.riding), "R (riding again)")
    ent(dref)["pos"] = [10.0, -3.0, 10.0]
    told[:] = []
    calls[:] = []
    second()
    left = int(Dg.downLeft(pid))
    K.check(("dismount",) in calls and ("remove", "Skyy_Pet_Dragon") in calls and int(Rd.VOIDS.get()) == 1 and 0 < left <= int(Dg.downMs(11)) and Views.view(uo, 2) is None
            and not [c for c in calls if c[0] == "teleport" and c[1] is None], "R ridden below the void line: you get off (no rescue), the dragon DOWN for %d ms" % left)
    second(0)
    K.check(any("Your dragon flew back to its summon slot" in t for _n, t in told) and Views.want(uo, r, key, 2, "default", False) is None, "R the line; nothing while DOWN")
    Dg.DOWN.clear()
    second(0)
    second(0)
    v = Views.view(uo, 2)
    dref = v.ref
    K.check(v is not None and not bool(v.riding), "R after the cooldown: back in the summon slot (never lost)")
    Cfg.DRAGON_VOID_Y = 75
    ent(dref)["pos"] = [10.0, 72.0, 10.0]
    calls[:] = []
    second()
    K.check(int(Rd.VOIDS.get()) == 2 and ("remove", "Skyy_Pet_Dragon") in calls and ("dismount",) not in calls, "R riderless below a raised void line (75): DOWN too, no rider to put off")
    Cfg.reloadAll()
    Cfg.SPAWN_DELAY, Cfg.SLOT2_MODE = 0, "always"
    Dg.DOWN.clear()
    second(0)
    second(0)
    v = Views.view(uo, 2)
    dref = v.ref
    ent(dref)["pos"] = [8.6, 70.0, 11.2]
    # ---- the saddle item row
    Cfg.DRAGON_SADDLE = "Tool_Saddle_Test"
    told[:] = []
    calls[:] = []
    Views.use(uo, v, now() + 60000)
    jobs.pop(0).run()
    K.check(not [c for c in calls if c[0] == "mount"] and ("Rider", "[Pets] Hold Tool_Saddle_Test to ride your dragon.") in told, "R saddle item set, not held: refused")
    rider["held"] = JString("Tool_Saddle_Test")
    Views.use(uo, v, now() + 70000)
    jobs.pop(0).run()
    K.check([c for c in calls if c[0] == "mount"], "R ... held: it carries you")
    second()
    rider["mid"] = 0
    rider["comp"].clear()
    second()
    v.landing = False
    Cfg.DRAGON_SADDLE = ""
    rider["held"] = None
    # ---- a pet loaded from a chunk while it was ridden (Empty_Role): the ghost sweep
    gh = new_ref(UUID.randomUUID(), "Empty_Role", [30.0, 70.0, 30.0])
    ent(gh)["tags"] = "Rider's Dragon (Lv 11)\n" + str(PW.HINT)
    ADR = JClass("com.hypixel.hytale.component.AddReason")
    K.check(int(Views.onLoad(gh, ADR.LOAD, st, None)) == 2 and ent(gh)["removed"] and int(Rd.SWEPT.get()) == 1, "R ghost sweep: our pet saved while ridden (Empty_Role + our name + F hint)")
    hz = new_ref(UUID.randomUUID(), "Empty_Role", [30.0, 70.0, 30.0])
    ent(hz)["tags"] = "Horse (Lv 3)\nserver.interactionHints.mount"
    K.check(int(Views.onLoad(hz, ADR.LOAD, st, None)) == 0 and not ent(hz)["removed"], "R ... never someone's ridden vanilla horse")
    # ---- a HORSE in the summon slot: any level, vanilla Mount movement, its seat, no flight
    hid = str(Ops.create(r, None, "Horse", 1, 1, 0, "test", "harness", False))
    r.set("active.2", hid)
    calls[:] = []
    second()
    second()
    hv = Views.view(uo, 2)
    K.check(hv is not None and str(hv.kind) == "Horse" and "|S" not in str(hv.spec), "R a Lv 1 Horse in the summon slot")
    calls[:] = []
    Views.use(uo, hv, now() + 90000)
    jobs.pop(0).run()
    hm = [c for c in calls if c[0] == "mount"]
    K.check(len(hm) == 1 and hm[0][:3] == ("mount", "Mount", 0.0) and abs(hm[0][3] - 1.6 * float(hv.scale)) < 0.002, "R the Horse: vanilla Mount movement, seat 1.6 x size %.2f: %s" % (float(hv.scale), hm))
    second()
    ent(hv.ref)["ground"] = 0
    calls[:] = []
    ticks(3)
    K.check(bool(hv.riding) and not [c for c in calls if c[0] == "fly"], "R riding the Horse: never a flight switch (ground only)")
    Cfg.MOUNT_RIDE = False
    second()
    K.check(not bool(hv.riding), "R Ride mount pets off: you get off")
    Cfg.MOUNT_RIDE = True
    hv.landing = False
    Views.use(uo, hv, now() + 120000)
    jobs.pop(0).run()
    second()
    K.check(bool(hv.riding), "R (riding the Horse again)")
    r.set("active.2", pid)
    calls[:] = []
    second()
    K.check(("dismount",) in calls and ("remove", "Skyy_Pet_Walk") in calls and str(Views.view(uo, 2) and Views.view(uo, 2).kind) != "Horse",
            "R another pet put in the summon slot while riding: you get off, the Horse goes: %s" % [c for c in calls if c[0] in ("dismount", "remove")])
    # ---- the hooks, the card, the real seams
    K.check(Rd.checkAnchor("k", "0,1.6,0") is None and Rd.checkAnchor("k", "0, 2.25 ,0.2") is None and Rd.checkAnchor("k", "1,2") is not None
            and Rd.checkAnchor("k", "0,x,0") is not None and Rd.checkAnchor("k", "0,99,0") is not None and Rd.checkAnchor("k", None) is None, "R checkAnchor")
    K.check(Rd.checkItem("k", "") is None and Rd.checkItem("k", "-") is None and Rd.checkItem("k", "Tool_Saddle") is None and Rd.checkItem("k", "a b") is not None, "R checkItem")
    Cfg.DRAGON_ANCHOR_DRAGONSKY = "broken"
    K.check([round(x, 3) for x in Rd.seat("DragonSky")] == [0.0, 2.8, 0.0] and [round(x, 3) for x in Rd.seat("Camel")] == [0.0, 2.25, 0.2] and [round(x, 3) for x in Rd.seat("Nope")] == [0.0, 1.6, 0.0],
            "R a broken seat row = the built-in seat; Camel = its vanilla seat; unknown = 1.6")
    Cfg.reloadAll()
    K.eq([str(Rd.cardLine("DragonPlain", 5)), str(Rd.cardLine("DragonPlain", 10)), str(Rd.cardLine("Horse", 10))],
         ["\nRide it from Lv 10 (F on it in the summon slot).", "\nRide it: F on it in the summon slot - jump to take off and fly.", ""], "R the card ride lines")
    tip = str(P_("PetsPage").tip(r, pid, 0))
    K.check("Ride it: F on it in the summon slot - jump to take off and fly." in tip and CARD_OLD not in tip, "R the dragon card")
    K.eq([bool(Rd.saddle("DragonPlain", 10)), bool(Rd.saddle("DragonPlain", 9)), bool(Rd.saddle("DragonFire", 50)), bool(Rd.rideable("DragonFire", 10)),
          bool(Rd.rideable("Horse", 1)), bool(Rd.rideable("Wolf", 50))], [True, False, False, True, True, False], "R saddle / rideable rules")
    Cfg.DRAGON_S4 = 12
    K.eq([int(Rd.rideLevel()), bool(Rd.rideable("DragonPlain", 11)), bool(Rd.saddle("DragonPlain", 11)), bool(Rd.rideable("DragonPlain", 12)),
          str(Rd.cardLine("DragonPlain", 11))], [12, False, False, True, "\nRide it from Lv 12 (F on it in the summon slot)."], "R fix: stage4 raised to 12 above the ride level 10 - riding waits for the Flyling")
    Cfg.DRAGON_RIDE_LV = 20
    K.check(int(Rd.rideLevel()) == 20 and not bool(Rd.rideable("DragonPlain", 19)), "R ... a ride level above the stage still counts")
    Cfg.reloadAll()
    Rd.API = None
    PW.API = None
    K.check(int(Rd.mountedId(None, oref)) == 0 and int(Rd.netId(None, oref)) == 0 and not bool(Rd.hasMount(None, oref)) and not bool(Rd.unmount(None, oref)) and int(Rd.ground(None, oref)) == -1
            and not bool(Rd.fly(None, oref, True, 1.0, 1.0)) and int(Rd.flyState(None, oref)) == -1 and not bool(Rd.move(None, oref, "Mount")) and not bool(Rd.resetMove(None, oref))
            and Rd.saddled("Nestkeeper_Dragon_Plain_4", 1.0, "x") is None, "R the REAL seams never throw without an engine")
    Rd.dismount(None, oref)
    K.check(str(Rd.mountReal(None, None, None, 0.0, 1.0, 0.0, "Mount")) == "it is not here", "R the real mount without a world: a reason, no throw")
    K.check(str(Rd.text()).startswith("riding: dragons from Lv 10 (fly, normal), mount pets on;") and str(Rd.census()).startswith("riding: 0 / 3 ride movement configs"),
            "R the ready-line / census texts: %s | %s" % (Rd.text(), Rd.census()))
    K.save()


# ======================================================================================================== reused phases with the new card line
def _swap(fn, mod, pairs):
    src = inspect.getsource(fn)
    for a, b in pairs:
        assert src.count(a) == 1, (fn.__name__, a)
        src = src.replace(a, b)
    ns = dict(mod.__dict__)
    exec(compile(src, mod.__file__, "exec"), ns)
    return ns[fn.__name__]


def run_f(out, jar, scratch, home):
    f = _swap(T412.run_f, T412, [('''"Riding and flying come in a later version." in tip''', '''"Ride it: F on it in the summon slot - jump to take off and fly." in tip''')])
    f(out, jar, scratch, home)


def run_dg(out, jar, scratch, home):
    src = inspect.getsource(T411.run_dg)
    old = '''and "Fighting, riding and flying come in a later version." in tip'''
    assert src.count(old) == 1
    src = src.replace(old, '''and "Ride it from Lv 10 (F on it in the summon slot)." in tip and "Fights next to you in the summon slot: bites for 0.1 %" in tip''')
    ns = dict(T411.__dict__)
    exec(compile(src, T411.__file__, "exec"), ns)
    ns["run_dg"](out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("r", run_r), ("m", T412.run_m), ("f", run_f), ("dg", run_dg), ("vw", T411.run_vw), ("st", T411.run_st),
                   ("el410", T410.run_el), ("live", T411.run_live)],
           script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
