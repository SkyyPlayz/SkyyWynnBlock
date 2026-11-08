"""Harness for SkyyPets 0.4.24 (RIDING: the mount no longer breaks on Interactable; tools/pets_0_4_24_patch.py). Build first:
    python tools/pets_0_4_24_patch.py && python SkyyPets/build_skyypets_0.4.24.py
    python SkyyPets/test_skyypets_0.4.24.py [--keep] [--expect-dump]

  S     static   the patch re-runs to identical bytes; 0.4.23's patch still regenerates 0.4.23 byte for byte; no class / system / command added;
                 line endings kept; the jar: no entry added / removed, the only changed non-class entry = manifest.json
  A/C/AA          (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.23 -> 0.4.24, engine-access audit
  ECS   EXECUTED on the REAL engine classes: a real ComponentRegistry + Store, the REAL NPCMountSystems$OnAdd registered, the REAL
                 RoleChangeSystem.tick, real Interactable / NPCMountComponent / NetworkId / MountNPC; the REAL PetRide.mountReal / unmount and
                 PetWorld.interact (only NPCPlugin / EntityModule / MountPlugin / the packet channel are stand-ins).
                 THE BUG: a creature without Interactable re-added with a mount component = the exact log line, "Archetype doesn't contain ComponentType!".
                 THE FIX: mountReal on that creature -> RoleChangeSystem -> no throw, mount component + Empty_Role on, your mount id = its network id,
                 one MountNPC, Interactable taken by OnAdd; unmount -> the role back; PetWorld.interact puts it back; the SECOND mount works too;
                 mountReal while the creature is still Empty_Role = refused ("it is still settling"); Interactions survive every role change;
                 the real PetRide.settle: a statue gets its own role after 3 s, never a creature with a rider or a mount under way
  RIDE  EXECUTED on the stand-in world (the 0.4.23 world, real PetViews / PetRide): upkeep restores F only on a summon nobody is on or mounting;
                 a mount id counts only when it is the creature's current network id; F while settling = its wording, no failed ride, fight target kept;
                 the ride notes + the separate trouble lines; a give-up keeps working
  PT/RD 0.4.23's phases re-run on this jar (pass-through, fight ghosts, F -> ride, the damage cancels: PetWorldApi.interact defaulted)
  live  0.4.17's start-twice on a scratch COPY of the live Skyy_SkyyPets (no saved-data change)
NOT COVERED (UNVERIFIED in game): what the CLIENT does with MountNPC (seat, sitting still, sending DismountNPC by itself); the ride notes will show it.
Exit code 1 on any failure.
"""
import os, sys, zipfile, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "ride2", "pets")]
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


T423 = _mod(os.path.join(HERE, "test_skyypets_0.4.23.py"), "test_skyypets_0_4_23")
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T44, T417, T41 = T423.T44, T423.T417, T423.T41

VERSION = "0.4.24"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.23.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.23.py")
PATCH = os.path.join(TOOLS, "pets_0_4_24_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T423.JAR, T423.OLD_JAR = JAR, OLD_JAR
EXPECT = {
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'PetRide': ['+f NOTES', '+f NOTES_BAD', '+f REARMED', '+f SETTLING', '+m note', '+m noteBad', '+m settle', '~<clinit>', '~m mountNow', '~m mountReal', '~m second', '~m text'],
    'PetView': ['+f emptySecs'],
    'PetViews': ['~m upkeep'],
    'PetWorld': ['+m interact'],
    'PetWorldApi': ['+m interact'],
    'PetsCfg': ['~m applyAll', '~m seed'],
    'PetsMigP5': ['~m mgLog', '~m run'],
    'PetsMigS2': ['~m run'],
    'PetsMigW15': ['~m run'],
    'SkyyPetsPlugin': ['~m setup'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}

_world0 = T44._world


def _world(out, jar, scratch, tag):
    """the 0.4.13-era stand-in world; a PetWorldApi stand-in written before 0.4.24 gets interact = nothing to do"""
    W = _world0(out, jar, scratch, tag)
    P0 = W["JProxy"]

    def Px(iface, dict=None, **kw):
        if dict is not None and str(iface).endswith("PetWorldApi"):
            dict.setdefault("interact", lambda acc, r: False)
        return P0(iface, dict=dict, **kw)
    W["JProxy"] = Px
    return W


T44._world = _world


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.24 - build script') and g.count('VERSION = "0.4.24"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(") and g.count("= cls(") == o.count("= cls("),
            "S no class, system or command added")
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    K.eq(g.count("@PKG@.PetWorld.interact("), 2, "S Interactable is put back in two places only: the mount and upkeep")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "pets_0_4_23_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn - on), [], "S the jar adds no entry")
    K.eq(sorted(on - nn), [], "S the jar removes nothing")
    K.eq(sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


# ======================================================================================================== ECS: the real Store + OnAdd + RoleChangeSystem
def run_ecs(out, jar, scratch, _home):
    W = _world(out, jar, scratch, "ecs")
    K, JClass, JProxy = W["K"], W["JClass"], W["JProxy"]
    from jpype import JObject, JString, JInt, JFloat, JArray, JException
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    MOD = JClass("java.lang.reflect.Modifier")

    def fld(cls_, name):
        c = cls_
        while c is not None:
            for f in c.getDeclaredFields():
                if str(f.getName()) == name:
                    f.setAccessible(True)
                    return f
            c = c.getSuperclass()
        raise KeyError(name)

    def setf(o, name, val):
        fld(o.getClass(), name).set(o, val)

    def alloc(cn):
        return U.allocateInstance(JClass(cn).class_)

    def single(cn):
        """a stand-in plugin: allocated, put in the class's own static instance field"""
        C_ = JClass(cn)
        i = U.allocateInstance(C_.class_)
        for f in C_.class_.getDeclaredFields():
            if MOD.isStatic(f.getModifiers()) and f.getType() == C_.class_:
                f.setAccessible(True)
                f.set(None, i)
        return i
    EM, MP, NP = "com.hypixel.hytale.server.core.modules.entity.EntityModule", "com.hypixel.hytale.builtin.mounts.MountPlugin", "com.hypixel.hytale.server.npc.NPCPlugin"
    ITB, MNT = "com.hypixel.hytale.server.core.modules.entity.component.Interactable", "com.hypixel.hytale.builtin.mounts.NPCMountComponent"
    NPC, NID = "com.hypixel.hytale.server.npc.entities.NPCEntity", "com.hypixel.hytale.server.core.modules.entity.tracker.NetworkId"
    PLA, PREF = "com.hypixel.hytale.server.core.entity.entities.Player", "com.hypixel.hytale.server.core.universe.PlayerRef"
    em, mp, np = single(EM), single(MP), single(NP)
    reg = JClass("com.hypixel.hytale.component.ComponentRegistry")()

    def ct(cn):
        C_ = JClass(cn).class_
        return reg.registerComponent(C_, JProxy("java.util.function.Supplier", dict={"get": lambda: U.allocateInstance(C_)}))
    tI, tM, tN, tD, tP, tR = ct(ITB), ct(MNT), ct(NPC), ct(NID), ct(PLA), ct(PREF)
    setf(em, "interactableComponentType", tI)
    setf(em, "networkIdComponentType", tD)
    setf(em, "playerComponentType", tP)
    c2t = JClass("java.util.HashMap")()
    c2t.put(JClass(NPC).class_, tN)
    setf(em, "classToComponentType", c2t)
    setf(mp, "mountComponentType", tM)
    setf(single("com.hypixel.hytale.server.core.universe.Universe"), "playerRefComponentType", tR)
    filler = [ct("com.hypixel.hytale.server.core.modules.entity.component." + n) for n in ("Invulnerable", "ProjectilePassthrough", "Intangible", "HeadRotation", "BoundingBox", "TransformComponent")]
    filler += [ct("com.hypixel.hytale.server.core.modules.physics.component.Velocity"), ct("com.hypixel.hytale.server.core.modules.physics.component.PhysicsValues")]
    tRep = ct("com.hypixel.hytale.server.core.modules.entity.repulsion.Repulsion")
    ITS = "com.hypixel.hytale.server.core.modules.interaction.Interactions"
    ITY = JClass("com.hypixel.hytale.protocol.InteractionType")
    tIts = ct(ITS)
    setf(em, "repulsionComponentType", tRep)
    RC = "com.hypixel.hytale.server.npc.systems.RoleChangeSystem"
    Q = JClass(RC + "$RoleChangeQueue")
    tQ = reg.registerResource(Q.class_, JProxy("java.util.function.Supplier", dict={"get": lambda: Q()}))
    setf(np, "roleChangeQueueResourceType", tQ)
    bm = alloc("com.hypixel.hytale.server.npc.asset.builder.BuilderManager")
    n2i = JClass("it.unimi.dsi.fastutil.objects.Object2IntOpenHashMap")()
    n2i.defaultReturnValue(JInt(-2147483648))
    ROLES = {"Skyy_Pet_Walk": 11, "Empty_Role": 3}
    for k_, v_ in ROLES.items():
        n2i.put(JString(k_), JInt(v_))
    setf(bm, "nameToIndexMap", n2i)
    setf(bm, "indexLock", JClass("java.util.concurrent.locks.ReentrantReadWriteLock")())
    bc = JClass("com.hypixel.fastutil.ints.Int2ObjectConcurrentHashMap")()
    infos = {}
    for k_, v_ in ROLES.items():
        bi = alloc("com.hypixel.hytale.server.npc.asset.builder.BuilderInfo")
        setf(bi, "keyName", JString(k_))
        bc.put(JInt(v_), bi)
        infos[k_] = bi
    setf(bm, "builderCache", bc)
    setf(np, "builderManager", bm)
    # the REAL OnAdd, registered in the real registry (it fires inside the real Store.addEntity)
    OnAdd = JClass("com.hypixel.hytale.builtin.mounts.NPCMountSystems$OnAdd")
    reg.registerSystem(OnAdd(tM, tN, tD))
    ERS = JClass("com.hypixel.hytale.component.EmptyResourceStorage")
    st = reg.addStore(JObject(JClass("java.lang.Object")()), ERS.get())
    try:
        fld(st.getClass(), "thread").set(st, JClass("java.lang.Thread").currentThread())
    except KeyError:
        pass
    rcs = JClass(RC)(tQ, filler[0], filler[1], filler[2], filler[3], filler[4], filler[5], filler[6], filler[7])
    # the rider: a real PlayerRef with a holder (PlayerRef.getComponent reads it) + the packet channel stand-in
    sent = []
    NC = JClass("com.hypixel.hytale.protocol.NetworkChannel")
    CC = JClass("com.hypixel.hytale.protocol.io.ChannelConnection")
    conn = JProxy("com.hypixel.hytale.protocol.io.ChannelConnection", dict={"write": lambda *a: sent.append(str(a[0].getClass().getSimpleName())),
                                                                              "writeAndFlush": lambda *a: sent.append(str(a[0].getClass().getSimpleName())),
                                                                              "flush": lambda: None, "isOpen": lambda: True})
    ph = alloc("com.hypixel.hytale.server.core.io.handlers.game.GamePacketHandler")
    chs = JArray(CC)(len(NC.values()))
    for i_ in range(len(chs)):
        chs[i_] = conn
    setf(ph, "channels", chs)
    pl = alloc(PLA)
    ph_ = reg.newHolder()
    ph_.putComponent(tP, pl)
    pr = alloc(PREF)
    setf(pr, "holder", ph_)
    setf(pr, "packetHandler", ph)
    Add = JClass("com.hypixel.hytale.component.AddReason")
    oh = reg.newHolder()
    oh.putComponent(tP, pl)
    oh.putComponent(tR, pr)
    owner = st.addEntity(oh, Add.SPAWN)

    def creature(net, interactable, mounted=False, role="Skyy_Pet_Walk"):
        h = reg.newHolder()
        n = alloc(NPC)
        setf(n, "role", alloc("com.hypixel.hytale.server.npc.role.Role"))
        setf(n, "roleName", JString(role))
        h.putComponent(tN, n)
        h.putComponent(tD, JClass(NID)(JInt(net)))
        if interactable:
            h.putComponent(tI, JClass(ITB).INSTANCE)
        its = JClass(ITS)()
        its.setInteractionId(ITY.Use, JString("SkyyTest_Use"))
        its.setInteractionHint(JString("SkyyTest_Hint"))
        h.putComponent(tIts, its)
        if mounted:
            c = JClass(MNT)()
            c.setOwnerPlayerRef(pr)
            c.setOriginalRoleIndex(JInt(11))
            h.putComponent(tM, c)
        return h

    def live(net):
        """the live Ref of the creature with this network id (a role change gives it a new Ref)"""
        got = []

        def v(chunk, cb):
            for i in range(int(chunk.size())):
                r = chunk.getReferenceTo(JInt(i))
                d = st.getComponent(r, tD)
                if d is not None and int(d.getId()) == net:
                    got.append(r)
        st.forEachChunk(JProxy("java.util.function.BiConsumer", dict={"accept": v}))
        if got:          # RoleBuilderSystem (not in this registry) builds the new role in the game
            setf(st.getComponent(got[0], tN), "role", alloc("com.hypixel.hytale.server.npc.role.Role"))
        return got[0] if got else None

    def tick():
        rcs.tick(JFloat(0.05), JInt(0), st)
    Rd, PW = JClass(PKG + "PetRide"), JClass(PKG + "PetWorld")
    has = lambda r, t: st.getComponent(r, t) is not None
    role = lambda r: str(st.getComponent(r, tN).getRoleName())
    # ---- THE BUG: Skyy's log line, on the real rules
    msg = ""
    try:
        st.addEntity(creature(900, False, mounted=True), Add.LOAD)
    except Exception as x:
        msg = str(x)
    K.check("Archetype doesn't contain ComponentType!" in msg and "Interactable" in msg, "ECS the bug: no Interactable + a mount component = the log's exact throw from the real Store.addEntity + OnAdd: %s" % msg[:90])
    ok = ""
    r0 = st.addEntity(creature(901, True, mounted=True), Add.LOAD)
    K.check(not has(r0, tI) and has(r0, tM), "ECS with Interactable on, the same add is fine and OnAdd takes it off")
    # ---- THE FIX: the real mountReal -> the real role change -> the real OnAdd, on a creature WITHOUT Interactable
    pet = st.addEntity(creature(902, False), Add.SPAWN)
    sent[:] = []
    res = str(Rd.mountReal(st, pet, owner, JFloat(0.0), JFloat(1.6), JFloat(0.0), JString("Mount")))
    K.eq(res, "", "ECS mountReal on a creature without Interactable says go")
    K.check(has(pet, tI) and has(pet, tM), "ECS ... Interactable is on BEFORE the role change, next to the mount component")
    tick()
    pet2 = live(902)
    K.check(pet2 is not None and pet2 != pet, "ECS the real role change re-added the creature under a new Ref (PetViews.onLoad re-attaches: LOAD)")
    K.check(pet2 is not None and has(pet2, tM) and not has(pet2, tI), "ECS ... no throw: the mount component is on and OnAdd took Interactable (as vanilla)")
    K.eq(role(pet2) if pet2 is not None else "", "Empty_Role", "ECS ... the ridden role is Empty_Role")
    its2 = st.getComponent(pet2, tIts) if pet2 is not None else None
    K.check(its2 is not None and str(its2.getInteractionId(ITY.Use)) == "SkyyTest_Use" and str(its2.getInteractionHint()) == "SkyyTest_Hint", "ECS ... Interactions (the F root + hint) survive the real role change, so only Interactable needs putting back")
    K.eq(int(pl.getMountEntityId()), 902, "ECS ... you are on it (Player.getMountEntityId = its network id)")
    K.eq(sent, ["CachedPacket"], "ECS ... one MountNPC packet went to you (the engine sends it as a CachedPacket)")
    # ---- get off (the real unmount: role back, component off), F comes back, ride again
    pl.setMountEntityId(JInt(0))
    K.check(bool(Rd.unmount(st, pet2)) and not has(pet2, tM), "ECS unmount: the mount component is off")
    K.eq(str(Rd.mountReal(st, pet2, owner, JFloat(0.0), JFloat(1.6), JFloat(0.0), JString("Mount"))), "it is still settling", "ECS F while its role is still on the way back = refused, never Empty_Role as its 'original' role")
    K.check(not has(pet2, tM), "ECS ... and nothing was put on it")
    tick()
    pet3 = live(902)
    K.eq(role(pet3) if pet3 is not None else "", "Skyy_Pet_Walk", "ECS the role change brought its own role back")
    K.check(pet3 is not None and not has(pet3, tI), "ECS ... and the engine did NOT restore Interactable (why upkeep must)")
    its3 = st.getComponent(pet3, tIts) if pet3 is not None else None
    K.check(its3 is not None and str(its3.getInteractionId(ITY.Use)) == "SkyyTest_Use" and str(its3.getInteractionHint()) == "SkyyTest_Hint", "ECS ... Interactions survive the role change back too")
    K.check(bool(PW.interact(st, pet3)) and has(pet3, tI), "ECS PetWorld.interact puts it back when missing (upkeep)")
    K.check(not bool(PW.interact(st, pet3)), "ECS ... and does nothing when it is there")
    sent[:] = []
    K.eq(str(Rd.mountReal(st, pet3, owner, JFloat(0.0), JFloat(1.6), JFloat(0.0), JString("Mount"))), "", "ECS the second mount says go")
    tick()
    pet4 = live(902)
    K.check(pet4 is not None and has(pet4, tM) and not has(pet4, tI) and int(pl.getMountEntityId()) == 902 and len(sent) == 1, "ECS ... and takes: mount component on, you are on it, one MountNPC")
    # the third mount with NO upkeep in between (F right after the role came back): mountReal alone is enough
    pl.setMountEntityId(JInt(0))
    Rd.unmount(st, pet4)
    tick()
    pet5 = live(902)
    K.check(pet5 is not None and not has(pet5, tI), "ECS got off again: no Interactable")
    sent[:] = []
    K.eq(str(Rd.mountReal(st, pet5, owner, JFloat(0.0), JFloat(1.6), JFloat(0.0), JString("Mount"))), "", "ECS a mount straight after (no upkeep in between) says go")
    tick()
    pet6 = live(902)
    K.check(pet6 is not None and has(pet6, tM) and int(pl.getMountEntityId()) == 902 and len(sent) == 1, "ECS ... and takes too (mountReal alone is enough)")
    # ---- a statue (Empty_Role, nobody on it, its role change back lost): the real settle -> the real role change -> its own role
    View = JClass(PKG + "PetView")
    sv = View()
    sv.slot, sv.kind, sv.uuid, sv.role = 2, JString("Horse"), JString("statue"), JString("Skyy_Pet_Walk")
    sv.ref = st.addEntity(creature(903, True, role="Empty_Role"), Add.SPAWN)
    K.check(not bool(Rd.settle(sv, st)) and not bool(Rd.settle(sv, st)), "ECS settle waits: nothing asked for in the first 2 seconds")
    tick()
    K.eq(role(live(903)), "Empty_Role", "ECS ... still Empty_Role then (the normal settling window is left alone)")
    K.check(bool(Rd.settle(sv, st)), "ECS settle asks for its own role at the third second")
    tick()
    K.eq(role(live(903)), "Skyy_Pet_Walk", "ECS ... the real role change gave the statue its own role back")
    K.eq(int(sv.emptySecs), 0, "ECS ... and the count is cleared")
    sv.ref = live(903)
    K.eq(str(Rd.mountReal(st, sv.ref, owner, JFloat(0.0), JFloat(1.6), JFloat(0.0), JString("Mount"))), "", "ECS ... and it can be mounted again")
    tick()
    # ---- settle leaves a creature someone is on (or mounting) alone
    rv = View()
    rv.slot, rv.kind, rv.uuid, rv.role = 2, JString("Horse"), JString("ridden"), JString("Skyy_Pet_Walk")
    rv.ref = st.addEntity(creature(904, True, mounted=True, role="Empty_Role"), Add.LOAD)
    K.check(not any(bool(Rd.settle(rv, st)) for _ in range(5)), "ECS settle never touches a creature with the mount component")
    tick()
    K.eq(role(rv.ref), "Empty_Role", "ECS ... it stays Empty_Role")
    K.eq(int(rv.emptySecs), 0, "ECS ... with no count")
    wv = View()
    wv.slot, wv.kind, wv.uuid, wv.role, wv.rideAt = 2, JString("Horse"), JString("mounting"), JString("Skyy_Pet_Walk"), 1
    wv.ref = st.addEntity(creature(905, True, role="Empty_Role"), Add.SPAWN)
    K.check(not any(bool(Rd.settle(wv, st)) for _ in range(5)), "ECS settle waits while a mount is under way (rideAt set)")
    K.save()


# ======================================================================================================== RIDE: upkeep + the watch on the stand-in world
def run_ride(out, jar, scratch, _home):
    W = _world(out, jar, scratch, "ride")
    K, JClass, JProxy = W["K"], W["JClass"], W["JProxy"]
    from jpype import JString, JArray, JDouble, JFloat, JObject
    P_ = lambda n: JClass(PKG + n)
    Cfg, Views, PW, Store, Ops, Fg, Rd, Log = (P_("PetsCfg"), P_("PetViews"), P_("PetWorld"), P_("PetStore"), P_("PetOps"), P_("PetFight"), P_("PetRide"), P_("PetsLog"))
    told = []
    names = {"00000000-0000-0000-0000-000000009901": "Rider"}
    P_("PetsEng").API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, list(W["names"])), "byName": lambda n: None,
                                                      "nameOf": lambda u: names.get(str(u), "?"), "tell": lambda u, t, c: told.append(str(t))})
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    Ref, Store_, World = JClass("com.hypixel.hytale.component.Ref"), JClass("com.hypixel.hytale.component.Store"), JClass("com.hypixel.hytale.server.core.universe.world.World")
    UUID = W["UUID"]
    st = U.allocateInstance(Store_.class_)
    w = U.allocateInstance(World.class_)
    ents, jobs, inter, mounts = {}, [], [], []
    nxt = [200]

    def new_ref(uuid, role, pos):
        nxt[0] += 1
        r = Ref(st, nxt[0])
        ents[int(r.getIndex())] = {"uuid": uuid, "role": role, "pos": list(pos), "net": nxt[0] + 5000, "ground": 1, "ref": r}
        return r
    ent = lambda r: None if r is None else ents.get(int(r.getIndex()))
    uo = UUID.fromString("00000000-0000-0000-0000-000000009901")
    oref = new_ref(uo, None, [10.0, 70.0, 10.0])
    roles = {"Skyy_Pet_Walk": 11, "Skyy_Pet_Fly": 12, "Skyy_Pet_Dragon": 13, "Test_Pet": 7, "Test_Fly": 8, "Empty_Role": 3}

    def spawn(s, role, x, y, z, yaw, model):
        return new_ref(UUID.randomUUID(), [k for k, v in roles.items() if v == int(role)][0], [float(x), float(y), float(z)])

    def setp(acc, r, x, y, z, yaw):
        ent(r)["pos"] = [float(x), float(y), float(z)]
    api = {"roleIndex": lambda role: roles.get(str(role), -1), "model": lambda m, s: JString(str(m)), "modelPinned": lambda m, s, seed: JString(str(m)),
           "spawn": spawn, "store": lambda w_: st, "ownerRef": lambda u_: oref, "refOf": lambda w_, u_: None, "execute": lambda w_, r_: (jobs.append(r_), True)[1],
           "pos": lambda acc, r: JArray(JDouble)(ent(r)["pos"]), "setPos": setp, "teleport": setp, "dead": lambda acc, r: False, "uuid": lambda acc, r: (ent(r) or {}).get("uuid"),
           "roleOf": lambda acc, r: (ent(r) or {}).get("role"), "tags": lambda acc, r: JString(""), "prepare": lambda acc, r, t: None, "plate": lambda acc, r, t: None,
           "clearDebug": lambda acc, r: None, "mark": lambda acc, r, o: None, "remove": lambda acc, r: True, "hearts": lambda *a: None, "anim": lambda *a: None, "stopAnim": lambda *a: None,
           "vanillaScale": lambda mid: 1.0, "fx": lambda *a: None, "passthrough": lambda acc, r, m: JString(str(m)),
           "interact": lambda acc, r: (inter.append(int(r.getIndex())), True)[1]}
    PW.API = JProxy(PKG + "PetWorldApi", dict=api)
    rider = {"mid": 0, "mount": set()}

    def r_mount(s, pet, o, ax, ay, az, mv):
        mounts.append(str(mv))
        rider["mid"] = ent(pet)["net"] + rider.get("shift", 0)
        rider["mount"].add(int(pet.getIndex()))
        return JString("")
    rapi = {"mount": r_mount, "mountedId": lambda acc, o: int(rider["mid"]), "netId": lambda acc, r: int((ent(r) or {}).get("net", 0)),
            "hasMount": lambda acc, r: r is not None and int(r.getIndex()) in rider["mount"], "unmount": lambda acc, r_: (rider["mount"].discard(int(r_.getIndex())), True)[1],
            "dismount": lambda acc, o: (rider.__setitem__("mid", 0), rider["mount"].clear())[0], "resetMove": lambda acc, o: True, "move": lambda acc, o, mid: True,
            "ground": lambda acc, r: int((ent(r) or {}).get("ground", -1)), "fly": lambda acc, o, on, h, v: True, "flyState": lambda acc, o: -1,
            "saddled": lambda m, s, seed: JString(str(m)), "held": lambda s, o: None}
    Rd.API = JProxy(PKG + "PetRideApi", dict=rapi)
    Fg.API = JProxy(PKG + "PetFightApi", dict={"hit": lambda cb, t, src, cause, amt: True, "health": lambda acc, r_: JArray(JFloat)([100.0, 0.0, 100.0]),
                                               "playerOf": lambda acc, r_: None, "guarded": lambda acc, r_: False})
    Cfg.SPAWN_DELAY = 0
    Cfg.SLOT2_MODE = "always"
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
    K.check(dv is not None and pv is not None, "RIDE the dragon (summon slot) and the Rabbit (pet slot) are out")
    dref, pref = dv.ref, pv.ref
    did = int(dref.getIndex())
    K.check(did in inter and int(pref.getIndex()) not in inter, "RIDE upkeep keeps F on the summon (PetWorld.interact), never on a pet-slot pet: %s" % inter)
    inter[:] = []
    # ---- riding: none while mounting or on it
    K.eq(int(Views.use(uo, dv, now())), 4, "RIDE F = the mount job")
    while jobs:
        jobs.pop(0).run()
    second()
    K.check(not inter and len(mounts) == 1 and bool(dv.riding) and any("You ride" in t for t in told), "RIDE it took (the ride line) and upkeep left Interactable alone while mounting: %s" % inter)
    second()
    K.check(not inter, "RIDE ... and while ridden")
    # ---- get off: F comes back on the next second
    rider["mid"] = 0
    rider["mount"].clear()
    second()
    K.check(not bool(dv.riding) and int(Rd.DISMOUNTS.get()) == 1, "RIDE got off (the game's own dismount)")
    second()
    K.check(did in inter and int(Rd.REARMED.get()) >= 1, "RIDE F is restored the second after you got off: %s" % inter)
    # ---- a mount under another network id still counts as riding
    while bool(dv.landing):
        dv.landing = False
    rider["shift"] = 77
    told[:] = []
    K.eq(int(Views.use(uo, dv, now())), 4, "RIDE F again")
    while jobs:
        jobs.pop(0).run()
    ent(dref)["net"] += 77          # its current network id is the one you are on; v.netId is the older one
    second()
    K.check(bool(dv.riding) and int(dv.netId) == int(rider["mid"]) and any("You ride" in t for t in told), "RIDE a mount id that differs from the id read before the role change counts when it IS the creature's current network id (id now %s)" % int(dv.netId))
    rider["mid"] = 0
    rider["mount"].clear()
    rider["shift"] = 0
    second()
    second()
    # ---- on ANOTHER mount inside the take window (the mount component is on ours): not riding this one
    while bool(dv.landing):
        dv.landing = False
    told[:] = []
    K.eq(int(Views.use(uo, dv, now())), 4, "RIDE F (you then end up on something else)")
    while jobs:
        jobs.pop(0).run()
    rider["mid"] = 424242
    second()
    K.check(not bool(dv.riding) and not any("You ride" in t for t in told) and int(dv.netId) != 424242, "RIDE another mount's id never counts as this pet, even with the mount component on it: netId %s" % int(dv.netId))
    rider["mid"] = 0
    for _ in range(5):
        second()
    K.check(not bool(dv.riding) and int(dv.rideAt) == 0, "RIDE ... the wrong-mount try ends in the give-up")
    # ---- F in the ticks while its role comes back: the settling wording, not a failed ride; a refused mount keeps the fight target
    while bool(dv.landing):
        dv.landing = False
    rapi3 = dict(rapi)
    rapi3["mount"] = lambda s, pet, o, ax, ay, az, mv: JString("it is still settling")
    Rd.API = JProxy(PKG + "PetRideApi", dict=rapi3)
    told[:] = []
    f0 = int(Rd.FAILS.get())
    dv.ftgt = pref
    K.eq(int(Views.use(uo, dv, now())), 4, "RIDE F while it is settling")
    while jobs:
        jobs.pop(0).run()
    K.check(any("is still settling - press F on it again" in t for t in told) and not any("could not carry you" in t for t in told), "RIDE settling = the settling wording, never 'could not carry you': %s" % told)
    K.eq(int(Rd.FAILS.get()), f0, "RIDE ... and it is not counted as a failed ride")
    K.check(dv.ftgt is not None and int(dv.rideAt) == 0, "RIDE ... the refused mount keeps the fight target and leaves no mount under way")
    Rd.API = JProxy(PKG + "PetRideApi", dict=rapi)
    K.eq(int(Views.use(uo, dv, now())), 4, "RIDE F once it has settled")
    while jobs:
        jobs.pop(0).run()
    K.check(dv.ftgt is None and int(dv.rideAt) > 0, "RIDE ... a mount that goes ahead drops the fight target")
    second()
    K.check(bool(dv.riding), "RIDE ... and it takes")
    rider["mid"] = 0
    rider["mount"].clear()
    second()
    second()
    while bool(dv.landing):
        dv.landing = False
    # ---- a mount that never takes: no ride, no stuck component, the give-up line
    inter[:] = []
    rapi2 = dict(rapi)

    def r_mount_silent(s, pet, o, ax, ay, az, mv):
        mounts.append(str(mv))
        rider["mount"].add(int(pet.getIndex()))
        return JString("")
    rapi2["mount"] = r_mount_silent
    Rd.API = JProxy(PKG + "PetRideApi", dict=rapi2)
    told[:] = []
    K.eq(int(Views.use(uo, dv, now())), 4, "RIDE F a third time (this mount never seats you)")
    while jobs:
        jobs.pop(0).run()
    for _ in range(4):
        second()
    K.check(not bool(dv.riding) and int(dv.rideAt) == 0 and did not in [int(x) for x in rider["mount"]] and any("could not carry you" in t for t in told),
            "RIDE the give-up: not riding, the mount component cleared, the line told: %s" % told)
    second()
    K.check(did in inter, "RIDE ... and F is restored after it")
    # ---- the notes
    ls = [str(x) for x in Log.LINES]
    notes = [x for x in ls if "ride DragonPlain" in x]
    K.check(any("mounting" in x for x in notes) and any("took" in x for x in notes) and any("got off" in x for x in notes) and any("gave up" in x for x in notes), "RIDE the ride notes: mounting / took / got off / gave up: %s" % notes[:6])
    n0 = int(Rd.NOTES.get())
    for _ in range(40):
        Rd.note(dv, "x")
    K.check(len([x for x in [str(y) for y in Log.LINES] if x.endswith(": x")]) == max(0, 30 - n0), "RIDE the notes stop at 30 lines per run")
    b0 = int(Rd.NOTES_BAD.get())
    K.check(b0 < 30 and any("gave up" in x for x in notes), "RIDE trouble lines have their own count (%s used)" % b0)
    for _ in range(40):
        Rd.noteBad(dv, "y")
    K.check(len([x for x in [str(y) for y in Log.LINES] if x.endswith(": y")]) == 30 - b0, "RIDE with the normal lines used up, trouble lines still print, up to their own 30")
    K.check("F restored" in str(Rd.text()), "RIDE /petadmin status names the restores")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("ecs", run_ecs), ("ride", run_ride), ("pt", T423.run_pt), ("rd", T423.run_rd), ("live", T417.run_live)],
           script=__file__, live=(T423.T422.T421.T41.LIVE, "Skyy_SkyyPets"))
