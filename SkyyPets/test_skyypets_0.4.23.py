"""Harness for SkyyPets 0.4.23 (F WORKS ON PETS AGAIN - RIDE YOUR DRAGON: pass-through without a permanent Intangible;
tools/pets_0_4_23_patch.py). Build first:
    python tools/pets_0_4_23_patch.py && python SkyyPets/build_skyypets_0.4.23.py
    python SkyyPets/test_skyypets_0.4.23.py [--keep] [--expect-dump]

  S     static   the patch re-runs to identical bytes; 0.4.22's patch still regenerates 0.4.22 byte for byte; no class / system / command
                 added; line endings kept; Intangible is put in ONE place (PetWorld.passthrough, mode ghost only); the new row; the jar: no
                 entry added / removed, the only changed non-class entry = manifest.json
  A/C/AA          (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.22 -> 0.4.23, engine-access audit
  PT    EXECUTED on REAL engine component types + REAL Archetypes (EntityModule / ProjectileModule / TimeModule stand-ins): the REAL
                 PetWorld.passthrough per mode (all / shots = ProjectilePassthrough only, ghost = Intangible + ProjectilePassthrough, off =
                 none, unknown = all) and the REAL engine spatial queries (all = still in the entity index the hit tests / Use read, ghost =
                 out); the REAL PetViews.fightMs / fighting on a REAL DamageDataComponent + TimeResource (3 s after a hit = fighting, 9 s =
                 not, row 0 / Arrows and bolts = never)
  RD    EXECUTED on a stand-in world (PetWorld.API + PetRide.API + PetFight.API seams, real PetViews / PetRide / PetFight / PetGuardSys):
                 a Lv 10 Plain Dragon in the summon slot is NEVER Intangible (spawn, upkeep, a fight); F (PetViews.use) on it = the
                 ride request -> the mount job -> riding (the F path end to end); a Lv 9 dragon in a fight = ghost, after the fight = all,
                 F = petted + the level hint; a walking pet in the pet slot: F = "You pet ..." (3), ghost in a fight, all again after;
                 THE DAMAGE CANCEL PATHS through the REAL PetGuardSys.handle: your melee / a player's shot on a pet = cancelled (Everything),
                 a mob's hit on a walking pet = untouched (its role is Invulnerable), Arrows and bolts / Off = untouched, a ridden pet =
                 untouched; a summoned dragon = PetFight.guard (your hit cancelled, a mob's hit cancelled + its pool lowered)
  live  0.4.17's start-twice on a scratch COPY of the live Skyy_SkyyPets (no saved-data change; the new row = its default)
NOT COVERED (UNVERIFIED in game): the client's own targeting (F shows the prompt on a tangible pet - the 0.2 test passed before
Intangible), a swing that "hits" a pet first still reaching the mob behind it, mobs choosing to attack a tangible rideable dragon.
Exit code 1 on any failure.
"""
import os, sys, zipfile, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "ride", "pets")]
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


T422 = _mod(os.path.join(HERE, "test_skyypets_0.4.22.py"), "test_skyypets_0_4_22")
T413 = _mod(os.path.join(HERE, "test_skyypets_0.4.13.py"), "test_skyypets_0_4_13")
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T417, T44, T41 = T422.T417, T413.T44, T413.T41

VERSION = "0.4.23"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.22.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.22.py")
PATCH = os.path.join(TOOLS, "pets_0_4_23_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T44.PKG = T413.PKG = PKG
EXPECT = {   # the class compare 0.4.22 -> 0.4.23 (the patch's finish() proves nothing else changed in the script)
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'PetGuardSys': ['~m handle'],
    'PetWorld': ['~m passthrough'],
    'PetViews': ['+f GHOSTS', '+f SHIELDS', '+m ago', '+m byRef', '+m fightMs', '+m fighting', '+m pass', '+m passText', '+m shield', '~<clinit>', '~m pass', '~m status', '~m upkeep'],
    'PetsCfg': ['+f PASS_FIGHT', '~<clinit>', '~m applyAll', '~m applyScalars', '~m seed'],
    'PetsMigP5': ['~m mgLog', '~m run'],
    'PetsMigS2': ['~m run'],
    'PetsMigW15': ['~m run'],
    'SkyyPetsPlugin': ['~m setup'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.23 - build script') and g.count('VERSION = "0.4.23"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(") and g.count("= cls(") == o.count("= cls("),
            "S no class, system or command added")
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    K.eq(g.count("@INTG@.INSTANCE)"), 1, "S Intangible is put in ONE place (PetWorld.passthrough)")
    K.check('boolean wi = "ghost".equals(m);' in g and 'boolean wi = "all".equals(m);' not in g, "S ... only for mode ghost (all no longer puts it)")
    K.eq(g.count('m = "ghost";'), 1, "S one place picks ghost (PetViews.pass, after the canRide check)")
    K.check('("pets.passthrough.fight", "Pets ghost while you fight", "show", "int", "8", "0", "60"' in g, "S the new row pets.passthrough.fight (0-60 s, default 8)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "pets_0_4_22_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn - on), [], "S the jar adds no entry")
    K.eq(sorted(on - nn), [], "S the jar removes nothing")
    K.eq(sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


# ======================================================================================================== PT: real component types
def _modules(JClass, JInt):
    """stand-in EntityModule / ProjectileModule / TimeModule: Unsafe instances whose ComponentType fields hold fresh real ComponentTypes"""
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    MOD = JClass("java.lang.reflect.Modifier")
    n_ = [0]
    idx = CT.class_.getDeclaredField("index")
    idx.setAccessible(True)
    tcf = CT.class_.getDeclaredField("tClass")
    tcf.setAccessible(True)

    def newct():
        v = U.allocateInstance(CT.class_)
        n_[0] += 1
        idx.set(v, JInt(n_[0]))
        return v
    for mod in ("com.hypixel.hytale.server.core.modules.entity.EntityModule", "com.hypixel.hytale.server.core.modules.projectile.ProjectileModule",
                "com.hypixel.hytale.server.core.modules.time.TimeModule"):
        C_ = JClass(mod)
        inst = U.allocateInstance(C_.class_)
        for f in C_.class_.getDeclaredFields():
            if not MOD.isStatic(f.getModifiers()) and f.getType() == CT.class_:
                f.setAccessible(True)
                f.set(inst, newct())
        for f in C_.class_.getDeclaredFields():
            if MOD.isStatic(f.getModifiers()) and f.getType() == C_.class_:
                f.setAccessible(True)
                f.set(None, inst)
    return U, tcf


def run_pt(out, jar, scratch, _home):
    from jpype import JClass, JInt, JProxy, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    U, tcf = _modules(JClass, JInt)
    EC = "com.hypixel.hytale.server.core.modules.entity.component."
    INTG, PPT = JClass(EC + "Intangible"), JClass(EC + "ProjectilePassthrough")
    ARCH, Ref_, Store_ = JClass("com.hypixel.hytale.component.Archetype"), JClass("com.hypixel.hytale.component.Ref"), JClass("com.hypixel.hytale.component.Store")
    ti, tp = INTG.getComponentType(), PPT.getComponentType()
    K.check(ti is not None and tp is not None and int(ti.getIndex()) != int(tp.getIndex()), "PT the real Intangible / ProjectilePassthrough component types resolve")
    PW = JClass(PKG + "PetWorld")
    PW.API = None
    st = U.allocateInstance(Store_.class_)
    pet = Ref_(st, 41)
    TC, BB = JClass(EC + "TransformComponent"), JClass(EC + "BoundingBox")
    comps = [TC.getComponentType(), BB.getComponentType()]          # the stand-in entry's component types (a real Archetype is built from them)

    def arch(r):
        return ARCH.of(JClass("com.hypixel.hytale.component.ComponentType")[:](comps)) if comps else ARCH.empty()

    def put(r, t, c):
        if not any(int(x.getIndex()) == int(t.getIndex()) for x in comps):
            comps.append(t)

    def rem(r, t):
        n0 = len(comps)
        comps[:] = [x for x in comps if int(x.getIndex()) != int(t.getIndex())]
        return len(comps) != n0
    acc = JProxy("com.hypixel.hytale.component.ComponentAccessor", dict={"getArchetype": arch, "putComponent": put, "tryRemoveComponent": rem})
    QE = None
    try:
        f_ = JClass("com.hypixel.hytale.server.core.modules.entity.system.EntitySpatialSystem").class_.getDeclaredField("QUERY")
        f_.setAccessible(True)
        QE = f_.get(None)
    except Exception as ex_:
        K.check(False, "PT the engine's entity spatial query could not be read: %s" % str(ex_)[:200])
    seq = []
    for mode in ("all", "ghost", "all", "shots", "off", "garbage", "ghost", "all"):
        got = PW.passthrough(acc, pet, mode)
        a = arch(pet)
        seq.append((mode, str(got), bool(a.contains(ti)), bool(a.contains(tp)), None if QE is None else bool(QE.test(a))))
    K.eq(seq, [("all", "all", False, True, True), ("ghost", "ghost", True, True, False), ("all", "all", False, True, True),
               ("shots", "shots", False, True, True), ("off", "off", False, False, True), ("garbage", "all", False, True, True),
               ("ghost", "ghost", True, True, False), ("all", "all", False, True, True)],
         "PT the REAL PetWorld.passthrough on REAL Archetypes: all / shots = ProjectilePassthrough only and the creature stays in the engine's "
         "entity index (targetable); ghost = + Intangible (out of the index); off = neither; an unknown mode = all")
    K.check(PW.passthrough(None, pet, "all") is None and PW.passthrough(acc, None, "ghost") is None, "PT no store / no ref = null (never throws)")
    # ---- the fight check: a REAL DamageDataComponent + a REAL TimeResource behind a stand-in accessor
    V, Cfg = JClass(PKG + "PetViews"), JClass(PKG + "PetsCfg")
    DDC, TR, Inst = (JClass("com.hypixel.hytale.server.core.entity.damage.DamageDataComponent"), JClass("com.hypixel.hytale.server.core.modules.time.TimeResource"),
                     JClass("java.time.Instant"))
    t0 = Inst.parse("2026-11-03T12:00:00Z")
    tr = TR(t0)
    dc = DDC()
    owner = Ref_(st, 42)
    oacc = JProxy("com.hypixel.hytale.component.ComponentAccessor", dict={"getComponent": lambda r, t: dc if r == owner else None, "getResource": lambda t: tr})
    K.eq(int(V.fightMs(oacc, owner)), -1, "PT fightMs: a player who never fought = -1")
    dc.setLastCombatAction(t0.minusSeconds(3))
    K.eq(int(V.fightMs(oacc, owner)), 3000, "PT fightMs: 3 s after your last hit (last combat action)")
    dc.setLastDamageTime(t0.minusSeconds(1))
    K.eq(int(V.fightMs(oacc, owner)), 1000, "PT fightMs: the newer of last hit / last hurt (1 s ago you were hit)")
    Cfg.PASS, Cfg.PASS_FIGHT = "all", 8
    f1 = bool(V.fighting(oacc, owner))
    dc2 = DDC()
    dc2.setLastCombatAction(t0.minusSeconds(9))
    oacc2 = JProxy("com.hypixel.hytale.component.ComponentAccessor", dict={"getComponent": lambda r, t: dc2, "getResource": lambda t: tr})
    f2 = bool(V.fighting(oacc2, owner))
    Cfg.PASS_FIGHT = 0
    f3 = bool(V.fighting(oacc, owner))
    Cfg.PASS_FIGHT, Cfg.PASS = 8, "shots"
    f4 = bool(V.fighting(oacc, owner))
    Cfg.PASS = "all"
    f5 = bool(V.fighting(None, owner)) or bool(V.fighting(oacc, None)) or int(V.fightMs(JProxy("com.hypixel.hytale.component.ComponentAccessor", dict={"getComponent": lambda r, t: None, "getResource": lambda t: tr}), owner)) != -1
    K.eq([f1, f2, f3, f4, f5], [True, False, False, False, False],
         "PT fighting: 1 s after a hit with the row at 8 s = yes; 9 s = no; the row at 0 = never; Arrows and bolts = never; no accessor / owner / component = no")
    K.save()


# ======================================================================================================== RD: F -> ride + the damage cancels
def run_rd(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "rd")
    K, JClass, JProxy = W["K"], W["JClass"], W["JProxy"]
    from jpype import JString, JArray, JDouble, JFloat, JObject, JInt
    P_ = lambda n: JClass(PKG + n)
    Cfg, Views, PW, Store, Ops, Fg, Rd = (P_("PetsCfg"), P_("PetViews"), P_("PetWorld"), P_("PetStore"), P_("PetOps"), P_("PetFight"), P_("PetRide"))
    told = []
    names = {"00000000-0000-0000-0000-000000009901": "Rider", "00000000-0000-0000-0000-000000009902": "Other"}
    P_("PetsEng").API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, list(W["names"])), "byName": lambda n: None,
                                                      "nameOf": lambda u: names.get(str(u), "?"), "tell": lambda u, t, c: told.append((names.get(str(u), "?"), str(t)))})
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    Ref, Store_, World = JClass("com.hypixel.hytale.component.Ref"), JClass("com.hypixel.hytale.component.Store"), JClass("com.hypixel.hytale.server.core.universe.world.World")
    Dmg, ES = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage"), JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    PS = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$ProjectileSource")
    UUID = W["UUID"]
    st = U.allocateInstance(Store_.class_)
    w = U.allocateInstance(World.class_)
    ents, jobs, calls = {}, [], []
    nxt = [200]

    def new_ref(uuid, role, pos, player=None):
        nxt[0] += 1
        r = Ref(st, nxt[0])
        ents[int(r.getIndex())] = {"uuid": uuid, "role": role, "pos": list(pos), "removed": False, "ref": r, "player": player, "net": nxt[0] + 5000,
                                   "ground": 1, "tags": "", "pass": None}
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
        return r

    def remove(acc, r):
        e = ent(r)
        if e is None or e["removed"]:
            return False
        e["removed"] = True
        return True

    def setp(acc, r, x, y, z, yaw):
        ent(r)["pos"] = [float(x), float(y), float(z)]

    def passthrough(acc, r, m):
        e = ent(r)
        mm = str(m) if str(m) in ("off", "shots", "ghost") else "all"
        if e is not None:
            e["pass"] = mm
            calls.append(("pass", e["role"], mm))
        return JString(mm)
    api = {"roleIndex": lambda role: roles.get(str(role), -1), "model": lambda m, s: JString("%s@%s" % (m, round(float(s), 3))),
           "modelPinned": lambda m, s, seed: JString("%s@%s#%s" % (m, round(float(s), 3), seed)),
           "spawn": spawn, "store": lambda w_: st, "ownerRef": lambda u_: oref if str(u_) == str(uo) else (xref if str(u_) == str(ux) else None),
           "refOf": lambda w_, u_: None, "execute": lambda w_, r_: (jobs.append(r_), True)[1],
           "pos": lambda acc, r: None if ent(r) is None or ent(r)["removed"] else JArray(JDouble)(ent(r)["pos"]), "setPos": setp, "teleport": setp,
           "dead": lambda acc, r: False, "uuid": lambda acc, r: (ent(r) or {}).get("uuid"), "roleOf": lambda acc, r: (ent(r) or {}).get("role"),
           "tags": lambda acc, r: JString((ent(r) or {}).get("tags", "")), "prepare": lambda acc, r, t: None, "plate": lambda acc, r, t: None,
           "clearDebug": lambda acc, r: None, "mark": lambda acc, r, o: None, "remove": remove,
           "hearts": lambda *a: calls.append(("hearts",)), "anim": lambda *a: None, "stopAnim": lambda *a: None,
           "vanillaScale": lambda mid: 1.55 if "Plain_4" in str(mid) else 1.0, "fx": lambda *a: None, "passthrough": passthrough}
    PW.API = JProxy(PKG + "PetWorldApi", dict=api)
    rider = {"mid": 0, "comp": set()}

    def r_mount(s, pet, o, ax, ay, az, mv):
        calls.append(("mount", str(mv)))
        rider["mid"] = ent(pet)["net"]
        rider["comp"].add(int(pet.getIndex()))
        return JString("")

    def r_dismount(acc, o):
        rider["mid"] = 0
        rider["comp"].clear()
    rapi = {"mount": r_mount, "mountedId": lambda acc, o: int(rider["mid"]) if str((ent(o) or {}).get("uuid")) == str(uo) else 0,
            "netId": lambda acc, r: int((ent(r) or {}).get("net", 0)), "hasMount": lambda acc, r: r is not None and int(r.getIndex()) in rider["comp"],
            "unmount": lambda acc, r_: (rider["comp"].discard(int(r_.getIndex())), True)[1], "dismount": r_dismount,
            "resetMove": lambda acc, o: True, "move": lambda acc, o, mid: True, "ground": lambda acc, r: int((ent(r) or {}).get("ground", -1)),
            "fly": lambda acc, o, on, h, v: True, "flyState": lambda acc, o: -1,
            "saddled": lambda m, s, seed: JString("%s@%s#%s+saddle" % (m, round(float(s), 3), seed)), "held": lambda s, o: None}
    Rd.API = JProxy(PKG + "PetRideApi", dict=rapi)
    vpass = Views.pass_          # PetViews.pass (jpype names it pass_: a Python keyword)
    Fg.API = JProxy(PKG + "PetFightApi", dict={"hit": lambda cb, t, src, cause, amt: True, "health": lambda acc, r_: JArray(JFloat)([100.0, 0.0, 100.0]),
                                               "playerOf": lambda acc, r_: (ent(r_) or {}).get("player"), "guarded": lambda acc, r_: False})
    Cfg.SPAWN_DELAY = 0
    Cfg.SLOT2_MODE = "always"
    Cfg.PASS, Cfg.PASS_FIGHT = "all", 8
    W["names"][str(uo)] = "Rider"
    key = str(Store.pkey(uo))
    Store.KEYOF.put(uo, key)
    r = Store.get(key)
    r.set("starter", "1")
    pid = str(Ops.create(r, None, "DragonPlain", 3, 10, 0, "test", "harness", False))
    rab = str(Ops.create(r, None, "Rabbit", 1, 5, 0, "test", "harness", False))
    r.set("active.2", pid)
    r.set("active.1", rab)
    clock = [0]

    def second(plus=1000):
        clock[0] += plus
        Fg.NOW_OFF = clock[0]
        Rd.NOW_OFF = clock[0]
        Views.second(uo, oref, st, None, w, "default")
        while jobs:
            jobs.pop(0).run()
    now = lambda: int(Rd.now())
    Views.SEEN.put(uo, JArray(JObject)(["default", JClass("java.lang.Long").valueOf(0)]))
    for _ in range(3):
        second()
    dv, pv = Views.view(uo, 2), Views.view(uo, 1)
    K.check(dv is not None and pv is not None, "RD the Lv 10 Plain Dragon (summon slot) and the Rabbit (pet slot) are out")
    if dv is None or pv is None:
        K.save()
        return
    dref, pref = dv.ref, pv.ref
    K.check(Rd.canRide(dv) is None, "RD the Lv 10 summoned dragon is rideable now (PetRide.canRide = null)")
    K.check(ent(dref)["pass"] == "all" and ent(pref)["pass"] == "all" and not [c for c in calls if c[0] == "pass" and c[2] == "ghost"],
            "RD spawn + upkeep: every pet = all (ProjectilePassthrough only, NO Intangible): %s" % [c for c in calls if c[0] == "pass"])
    # ---- a fight: the walking pet goes ghost, the rideable dragon NEVER
    vpass(None, pv, True)
    vpass(None, dv, True)
    K.check(ent(pref)["pass"] == "ghost" and ent(dref)["pass"] == "all" and int(Views.GHOSTS.get()) == 1,
            "RD in a fight: the Rabbit = ghost (legacy shots pass), the rideable dragon stays all (never Intangible): %s / %s" % (ent(pref)["pass"], ent(dref)["pass"]))
    for _ in range(5):
        vpass(None, dv, True)
    K.check(not [c for c in calls if c[0] == "pass" and c[1] == "Skyy_Pet_Dragon" and c[2] == "ghost"], "RD a rideable summon is NEVER Intangible (5 more fight seconds)")
    vpass(None, pv, False)
    K.check(ent(pref)["pass"] == "all", "RD after the fight the Rabbit is all again (targetable: F works)")
    second()
    K.check(ent(pref)["pass"] == "all" and ent(dref)["pass"] == "all", "RD the real upkeep (no fight readable) keeps all")
    # ---- F on the Rabbit = pet it; F on the dragon = the ride request -> the mount job -> riding
    told[:] = []
    k = int(Views.use(uo, pv, now()))
    K.check(k == 3 and any(t.startswith("[Pets] You pet ") for _n, t in told), "RD F on your Rabbit (PetViews.use) = 'You pet ...' (3): %s" % told)
    while jobs:          # the petting job (hearts + the animation)
        jobs.pop(0).run()
    K.check(("hearts",) in calls, "RD ... the hearts play (PetPetJob)")
    told[:] = []
    calls[:] = []
    k = int(Views.use(uo, dv, now()))
    K.check(k == 4 and len(jobs) == 1 and "PetRideJob" in str(jobs[0].getClass().getName()), "RD F on your Lv 10 dragon (PetViews.use -> PetRide.request) = the mount job queued (4)")
    while jobs:
        jobs.pop(0).run()
    K.check([c for c in calls if c[0] == "mount"] == [("mount", "Skyy_Dragon_Glide")], "RD the mount job seats you (Skyy_Dragon_Glide): %s" % [c for c in calls if c[0] == "mount"])
    second()
    second()          # (upkeep sets the pass mode before PetRide.second marks it ridden: the next second = off)
    K.check(bool(dv.riding) and ent(dref)["pass"] == "off" and any("You ride your Plain Dragon" in t for _n, t in told),
            "RD it took: riding, the ride line, the ridden dragon = off (normal): %s" % told)
    vpass(None, dv, True)
    K.check(ent(dref)["pass"] == "off", "RD a ridden dragon in a fight stays off (never ghost)")
    # ---- THE DAMAGE CANCEL PATHS through the REAL PetGuardSys.handle (damage Filter group)
    AC = JClass("com.hypixel.hytale.component.ArchetypeChunk")
    gs = P_("PetGuardSys")()

    def hit(victim, src, amt=20.0):
        ch = U.allocateInstance(AC.class_)
        fr = AC.class_.getDeclaredField("refs")
        fr.setAccessible(True)
        fr.set(ch, JArray(Ref)([victim]))
        fs = AC.class_.getDeclaredField("entitiesSize")
        fs.setAccessible(True)
        fs.setInt(ch, JInt(1))
        d = Dmg(src, 0, float(amt))
        gs.handle(JInt(0), ch, st, None, d)
        return (bool(d.isCancelled()), round(float(d.getAmount()), 2))
    mob = new_ref(UUID.randomUUID(), "Trork_Warrior", [14.0, 70.0, 10.0])
    s0 = int(Views.SHIELDS.get())
    shot = new_ref(UUID.randomUUID(), None, [12.0, 70.0, 10.0])
    res = [hit(pref, ES(oref)), hit(pref, ES(xref)), hit(pref, PS(oref, shot)), hit(pref, ES(mob))]
    K.eq(res, [(True, 0.0), (True, 0.0), (True, 0.0), (False, 20.0)],
         "RD PetGuardSys on the Rabbit (Everything): your melee / another player's hit / your shot (Damage$ProjectileSource) = cancelled; a mob's hit = untouched (the role is Invulnerable)")
    K.eq(int(Views.SHIELDS.get()) - s0, 3, "RD ... 3 player hits counted")
    Cfg.PASS = "shots"
    a1 = hit(pref, ES(oref))
    Cfg.PASS = "off"
    a2 = hit(pref, ES(oref))
    Cfg.PASS = "all"
    K.eq([a1, a2], [(False, 20.0), (False, 20.0)], "RD Arrows and bolts / Off: a player's hit on the Rabbit is not cancelled by us (swings hit pets there, as designed)")
    # the dragon: off it first so it is a plain summoned (tracked) dragon again
    dv.riding = False
    dv.passOn = None
    vpass(None, dv)
    g0, h0 = int(Fg.GUARDED.get()), int(Fg.HURT.get())
    hp0 = float(dv.fhp) if float(dv.fhp) > 0.0 else -1.0
    d1 = hit(dref, ES(oref))
    d2 = hit(dref, ES(mob), 5.0)
    K.eq([d1, d2], [(True, 0.0), (True, 0.0)], "RD the summoned dragon: your hit + a mob's hit both cancelled (PetFight.guard, the real health never moves)")
    K.check(int(Fg.GUARDED.get()) - g0 == 2 and int(Fg.HURT.get()) - h0 == 1 and float(dv.fhp) < float(dv.fhpMax),
            "RD ... the mob's hit lowered its own pool (R6: %.1f / %.1f), yours did not" % (float(dv.fhp), float(dv.fhpMax)))
    # a ridden pet is normal: the shield leaves it alone
    pv.riding = True
    K.eq(hit(pref, ES(oref)), (False, 20.0), "RD a ridden pet: your hit is not cancelled by the shield (a ridden creature is normal)")
    pv.riding = False
    K.check(not bool(P_("PetGuardSys").FAILED_ONCE), "RD the real PetGuardSys never threw")
    st_ = str(Views.status())
    K.check("Attacks pass through pets: all (player hits on pets cancelled" in st_ and "fight ghosts 1" in st_, "RD /petadmin status names the pass-through: %s" % st_[-200:])
    # ---- a Lv 9 dragon: not rideable -> ghost in a fight, F = pet it + the level hint
    r.set("pet.%s.level" % pid, "9")
    K.check(Rd.canRide(dv) is not None, "RD a Lv 9 dragon is not rideable yet")
    dv.passOn = None
    vpass(None, dv, True)
    K.eq(ent(dref)["pass"], "ghost", "RD a Lv 9 summoned dragon in a fight = ghost (it is no mount yet)")
    vpass(None, dv, False)
    told[:] = []
    k = int(Views.use(uo, dv, now() + 60000))
    K.check(ent(dref)["pass"] == "all" and k == 3 and ("Rider", "[Pets] Your dragon can carry you from Lv 10.") in told,
            "RD after the fight: all again; F = petted + the level hint: %s" % told)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("pt", run_pt), ("rd", run_rd), ("live", T417.run_live)],
           script=__file__, live=(T422.T421.T41.LIVE, "Skyy_SkyyPets"))
