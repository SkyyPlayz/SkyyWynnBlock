"""SkyySkills 0.4.66 - harness for "Ranching XP for taming, Capture Crates and milking" (tools/skills_0_4_66_patch.py; starter archipelago
R6). Build first:
    python tools/skills_0_4_66_patch.py && python SkyySkills/build_skyyskills_0.4.66.py
    python SkyySkills/test_skyyskills_0.4.66.py [--keep]
Phases (each a fresh child JVM: -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes, line endings kept, + exactly 4 classes / 2 systems, no command, VERSION, the 7 rows
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.4.65 -> 0.4.66: exactly the planned members (EXPECT) + the 4 new classes (ADDED)
  F2    fakes    the SkyyZones 0.2.0 harness's engine stand-ins (Store / ArchetypeChunk / World / PlayerRef subclasses)
  X     EXECUTED on the stand-ins with REAL engine objects (NPCEntity, UUIDComponent, TransformComponent, Hotbar + SimpleItemContainer, ItemStack
                 with real CapturedNPCMetadata metadata, real Slot / ItemStackSlot / ItemStack / List / Move transactions, a real
                 InventoryChangeEvent, a real World task queue): RanchAct.read (defaults, custom values, clamps, 0 = off), the Assets tables
                 (tame pairs, crate roles with "*X" globs, milk ids), the tame rule (UNLOAD -> LOAD within 3 s as the right Tamed_ role; a
                 chunk reload, a wrong role, a stale entry, a SPAWN never), RanchNpcSys.onEntityRemove / onEntityAdded (tame queued; crate
                 queued only for a crate role without a DeathComponent), RanchActTask.run (tame: nearest player in range in the same store;
                 fix round: a crate catch = the catcher's crate fill PAIRED with the animal's REMOVE (either order, never a bystander or a
                 despawn), released animals never pay (release mark + spawn, either order), the XP-only waits 0 by default, a relog keeps
                 a running wait; the milking decided one task later so a same-tick pickup note refuses it, 250 ms pairing), the milk scanner
                 (held empty bucket out of the ACTIVE hotbar slot + filled bucket in, either order, a move never, another slot never),
                 RanchInvSys.handle (a pair queues one RanchTask; a drop note / milk pickup note refuses; the milk cooldown), retain
  LIVE  start twice on a scratch COPY of the live Skyy_SkyySkills (the 0.4.64 harness's live phase): nothing written, start 2 changes nothing
  LIVE2 a scratch COPY: SkillCfg.load on the live xp.properties (no 0.4.66 lines) -> RanchAct reads every code default, the file is unchanged
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): the real RoleChangeSystem / UseCaptureCrateInteraction / cow harvest firing these systems in a running
server (the engine order is asserted at build time from the bytecode); RanchTask's award itself is the 0.4.37 pickup path (unchanged).
"""
import os, sys, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "ranch6fix", "sk")]


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T65 = _mod(os.path.join(HERE, "test_skyyskills_0.4.65.py"), "test_skyyskills_0_4_65")
T64 = T65.T64
VERSION = "0.4.66"
PKG = "com.skyy.skills."
GEN = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyskills_0.4.65.py")
PATCH = os.path.join(TOOLS, "skills_0_4_66_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.65.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T65.LIVE_DIR
ADDED = ["RanchAct", "RanchNpcSys", "RanchInvSys", "RanchActTask"]
EXPECT = {   # checked 2026-10-25 (the class compare vs 0.4.65 of the first harness run): the new hooks + the version / default-file text
    'Acro': ['~m retainSet'],                      # + RanchAct.retain(online)
    'CfgFile': ['~<clinit>'],                      # the default xp.properties (+ the 0.4.66 block)
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],         # + the 7 Server Setup rows
    'CurveP9Mig': ['~m run'],
    'ManaGuard': ['~m armReport2', '~m intReport', '~m packReport'],
    'RanchDropSys': ['~m handle'],                 # + the drop note
    'RanchPickSys': ['~m onEntityAdded'],          # + the milk-bucket pickup note
    'SkillCfg': ['~m load'],                       # + RanchAct.read(p)
    'SkyySkillsPlugin': ['~m setup'],              # + RanchNpcSys / RanchInvSys registered, the ready line
}
R66_KEYS = [("ranching.tameXp", "250"), ("ranching.captureXp", "100"), ("ranching.milkXp", "100"), ("ranching.captureCooldownSec", "0"),
            ("ranching.milkCooldownSec", "0"), ("ranching.cowCooldownSec", "0"), ("ranching.animalCooldownSec", "0"), ("ranching.actRange", "8")]   # fix round: the XP-only waits 0 = off


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyySkills 0.4.66') and g.count('VERSION = "0.4.66"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand("), "S no new command")
    K.check(g.count("registerSystem(") == o.count("registerSystem(") + 2 and g.count("registerSystem(new {PKG}.RanchNpcSys())") == 1
            and g.count("registerSystem(new {PKG}.RanchInvSys())") == 1, "S exactly 2 new systems (RanchNpcSys, RanchInvSys), one registerSystem each")
    K.check(g.count("makeClass(") == o.count("makeClass(") + 4, "S exactly 4 new classes")
    for k, v in R66_KEYS:
        K.check(g.count('CFG_ROWS.append(("%s",' % k) == 1, "S Server Setup row %s" % k)
    K.check(g.count('{PKG}.RanchAct.read(p);') == 1 and g.count('{PKG}.RanchAct.retain(online);') == 1, "S SkillCfg.load reads + SkillTick retains RanchAct")
    K.check('{PKG}.Ranch.text() + "; " + {PKG}.RanchAct.text()' in g, "S the ready line names the new sources")
    K.check('"At most this much Ranching XP per player per minute: pickups, taming, crates, milking (0 = no cap).", "reload"),' in g
            and '"Animal products you pick up pay Ranching XP (pickups only). Items a player dropped pay nothing.", "reload"),' in g
            and '"At most this much Ranching XP from pickups per player per minute (0 = no cap).", "reload"),' not in g, "S FIX the cap row names every Ranching source, the pickup row says pickups only")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_fakes(out, jar, scratch, _home):
    T = T65.t20()
    os.makedirs(os.path.join(scratch, "fake2"), exist_ok=True)
    T.run_mkfake(os.path.join(scratch, "fake2"))
    K = HK.Child(out)
    K.check(os.path.isdir(os.path.join(scratch, "fake2")), "F2: the stand-ins are written")
    K.save()


def run_x(out, jar, scratch, _home):
    from jpype import JClass, JInt, JLong, JByte, JShort, JBoolean
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, os.path.join(scratch, "fake2")], verify=True)
    T = T65.t20()
    T.SCRATCH = scratch
    try:
        E = T.engine(K)
        U, jfield = E["U"], E["jfield"]
        FAKE = T.FAKE
        J = lambda n: JClass(PKG + n)
        Cfg, Sto, RA, RNS, RIS, RAT, RT, Ranch = (J(n) for n in ("SkillCfg", "SkillStore", "RanchAct", "RanchNpcSys", "RanchInvSys", "RanchActTask", "RanchTask", "Ranch"))
        Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
        MS, MB, MCH, FW, FP = (JClass(FAKE + "." + n) for n in ("MapStore", "MapBuffer", "MapChunk", "FakeWorld", "FakePr"))
        WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
        EST = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
        PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
        UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
        REF = JClass("com.hypixel.hytale.component.Ref")
        IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
        NPCc = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
        UUC = JClass("com.hypixel.hytale.server.core.entity.UUIDComponent")
        TC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
        DTH = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
        DMOD = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageModule")
        EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
        HOTB = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar")
        STOR = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$Storage")
        SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
        CNM = JClass("com.hypixel.hytale.server.npc.metadata.CapturedNPCMetadata")
        CT = JClass("com.hypixel.hytale.component.ComponentType")
        ADR = JClass("com.hypixel.hytale.component.AddReason")
        RMR = JClass("com.hypixel.hytale.component.RemoveReason")
        SLT = JClass("com.hypixel.hytale.server.core.inventory.transaction.SlotTransaction")
        ISST = JClass("com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction")
        IST = JClass("com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction")
        LTX = JClass("com.hypixel.hytale.server.core.inventory.transaction.ListTransaction")
        MVT = JClass("com.hypixel.hytale.server.core.inventory.transaction.MoveTransaction")
        MVY = JClass("com.hypixel.hytale.server.core.inventory.transaction.MoveType")
        ACT = JClass("com.hypixel.hytale.server.core.inventory.transaction.ActionType")
        ICE = JClass("com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent")
        V3D = JClass("org.joml.Vector3d")
        IHM, UUID, HM, AL, PROPS = (JClass("java.util.IdentityHashMap"), JClass("java.util.UUID"), JClass("java.util.HashMap"),
                                    JClass("java.util.ArrayList"), JClass("java.util.Properties"))
        HSet = JClass("java.util.HashSet")

        def findf(k, n):
            while k is not None:
                try:
                    f = k.getDeclaredField(n)
                    f.setAccessible(True)
                    return f
                except Exception:
                    k = k.getSuperclass()
            raise KeyError(n)

        def setany(o, n, v):
            findf(o.getClass(), n).set(o, v)
        # the component types the new code asks for: NPCEntity (EntityModule.classToComponentType) + DeathComponent (a DamageModule)
        em = EM.get()
        n_ = [900]

        def newct():
            v = U.allocateInstance(CT.class_)
            n_[0] += 1
            jfield(CT, "index").set(v, JInt(n_[0]))
            return v
        c2c = findf(EM.class_, "classToComponentType").get(em)
        if c2c is None:
            c2c = HM()
            findf(EM.class_, "classToComponentType").set(em, c2c)
        c2c.put(NPCc.class_, newct())
        dm = U.allocateInstance(DMOD.class_)
        findf(DMOD.class_, "deathComponentType").set(dm, newct())
        jfield(DMOD, "instance").set(None, dm)
        K.check(NPCc.getComponentType() is not None and DTH.getComponentType() is not None and HOTB.getComponentType() is not None
                and UUC.getComponentType() is not None and TC.getComponentType() is not None, "X the stand-in engine answers every component type the new code asks for")
        # a world with a real task queue + a store
        w = U.allocateInstance(FW.class_)
        jfield(WLD, "name").set(w, "skyy-island-ranch6")
        jfield(WLD, "acceptingTasks").set(w, JClass("java.util.concurrent.atomic.AtomicBoolean")(True))
        q = JClass("java.util.concurrent.LinkedBlockingDeque")()
        jfield(WLD, "taskQueue").set(w, q)
        es = U.allocateInstance(EST.class_)
        jfield(EST, "world").set(es, w)
        st = U.allocateInstance(MS.class_)
        st.comps = IHM()
        st.ext = es
        st2 = U.allocateInstance(MS.class_)   # another world's store
        st2.comps = IHM()
        st2.ext = es
        cb = U.allocateInstance(MB.class_)
        refn = [0]

        def ent(store, comps):
            refn[0] += 1
            r_ = REF(store, JInt(refn[0]))
            m_ = IHM()
            for t_, c_ in comps:
                m_.put(t_, c_)
            store.comps.put(r_, m_)
            return r_

        def tcomp(x, y, z):
            t_ = TC()
            setany(t_, "position", V3D(float(x), float(y), float(z)))
            return t_

        def npc(store, role, uid, x=0, y=64, z=0, dead=False):
            n0 = U.allocateInstance(NPCc.class_)
            setany(n0, "roleName", role)
            cs = [(NPCc.getComponentType(), n0), (UUC.getComponentType(), UUC(uid)), (TC.getComponentType(), tcomp(x, y, z))]
            if dead:
                cs.append((DTH.getComponentType(), U.allocateInstance(DTH.class_)))
            return ent(store, cs), n0
        pbu = findf(UNI.class_, "playersByUuid").get(UNI.get())

        def hotbar(items, active):
            hb = U.allocateInstance(HOTB.class_)
            c_ = SIC(JShort(9))
            for i_, it_ in enumerate(items):
                if it_ is not None:
                    c_.setItemStackForSlot(JShort(i_), it_)
            setany(hb, "inventory", c_)
            setany(hb, "activeSlot", JByte(active))
            return hb

        def player(store, name, k, x, y, z, hb=None):
            pr_ = U.allocateInstance(FP.class_)
            u_ = UUID.fromString("00000000-0000-4000-8000-%012x" % (0x6600 + k))
            jfield(PRc, "uuid").set(pr_, u_)
            jfield(PRc, "username").set(pr_, name)
            cs = [(PRc.getComponentType(), pr_), (TC.getComponentType(), tcomp(x, y, z))]
            if hb is not None:
                cs.append((HOTB.getComponentType(), hb))
            r_ = ent(store, cs)
            jfield(PRc, "entity").set(pr_, r_)
            pbu.put(u_, pr_)
            return pr_, r_

        # ---------------- RanchAct.read + the tables
        RA.read(PROPS())
        K.check(int(RA.TAME_XP) == 250 and int(RA.CAPTURE_XP) == 100 and int(RA.MILK_XP) == 100 and int(RA.CAP_CD) == 0 and int(RA.MILK_CD) == 0
                and int(RA.ANIMAL_MS) == 0 and int(RA.COW_MS) == 0 and float(RA.RANGE) == 8.0, "X FIX read: no lines = the code defaults (250 / 100 / 100, every XP-only wait 0 = off, 8 blocks)")
        K.check(bool(RA.isMilkRole("Tamed_Cow")) and bool(RA.isMilkRole("Tamed_Mosshorn")) and not bool(RA.isMilkRole("Cow")) and not bool(RA.isMilkRole("Tamed_Sheep")),
                "X tables: the milkable roles (Tamed_Cow, Tamed_Mosshorn*) from Assets.zip")
        p_ = PROPS()
        for k_, v_ in (("ranching.tameXp", "-5"), ("ranching.captureXp", "99999999"), ("ranching.milkXp", "x"), ("ranching.actRange", "999"),
                       ("ranching.captureCooldownSec", "0"), ("ranching.milkCooldownSec", "3"), ("ranching.animalCooldownSec", "10")):
            p_.setProperty(k_, v_)
        RA.read(p_)
        K.check(int(RA.TAME_XP) == 0 and int(RA.CAPTURE_XP) == 1000000 and int(RA.MILK_XP) == 100 and float(RA.RANGE) == 64.0 and int(RA.CAP_CD) == 0
                and int(RA.MILK_CD) == 3000 and int(RA.ANIMAL_MS) == 10000, "X read: clamps (negative -> 0 = off, > 1,000,000, range <= 64), a bad number = the default")
        RA.read(PROPS())
        K.check(str(RA.tameOf("Cow")) == "Tamed_Cow" and str(RA.tameOf("Sheep_Lamb")) == "Tamed_Sheep_Lamb" and RA.tameOf("Tamed_Cow") is None
                and bool(RA.isTamed("Tamed_Chicken")) and not bool(RA.isTamed("Chicken")), "X tables: wild -> tamed role pairs from Assets.zip")
        K.check(all(bool(RA.crateRole(r_)) for r_ in ("Chicken", "Tamed_Chicken", "Cow_Calf", "Tamed_Sheep_Lamb", "Mouse", "Frog_Green"))
                and not any(bool(RA.crateRole(r_)) for r_ in ("Cow", "Sheep", "Tamed_Cow", "Mouse_Big", None)), "X tables: Capture_Crate roles ('*X' = ends in X, else exact); adults never")
        K.check(str(RA.text()).startswith("taming 250 / Capture Crate 100 (one paid catch per 0 s) / milking 100") and "36 tameable roles" in str(RA.text()), "X text: %s" % RA.text())

        # ---------------- tame rule (T1)
        a1, a2 = UUID.randomUUID(), UUID.randomUUID()
        now = 1000000
        K.check(bool(RA.unloaded(a1, "Cow", JLong(now))) and bool(RA.tamedNow(a1, "Tamed_Cow", JLong(now + 50))), "X tame: UNLOAD Cow -> LOAD Tamed_Cow (same UUID, 50 ms) = a tame")
        K.check(not bool(RA.tamedNow(a1, "Tamed_Cow", JLong(now + 60))), "X tame: the entry is used up (one tame per role change)")
        RA.unloaded(a2, "Cow", JLong(now))
        K.check(not bool(RA.tamedNow(a2, "Tamed_Sheep", JLong(now + 10))), "X tame: a LOAD as another tamed role is no tame")
        RA.unloaded(a2, "Cow", JLong(now))
        K.check(not bool(RA.tamedNow(a2, "Tamed_Cow", JLong(now + 3500))), "X tame: a stale entry (> 3 s) is no tame")
        K.check(not bool(RA.unloaded(a2, "Tamed_Cow", JLong(now))) and not bool(RA.unloaded(a2, "Zombie", JLong(now))), "X tame: only tameable wild roles are remembered")
        RA.unloaded(a2, "Cow", JLong(now))
        K.check(not bool(RA.tamedNow(a2, "Cow", JLong(now + 10))), "X tame: a chunk reload (LOAD as the same wild role) is no tame")
        RA.PEND.clear()

        # ---------------- RanchNpcSys + RanchActTask (tame)
        RA.read(PROPS())
        ns = RNS()
        K.check(ns.getQuery() is not None, "X RanchNpcSys.getQuery = NPCEntity")
        pa, ra_ = player(st, "Alice", 1, 3, 64, 0)       # 3 blocks away
        pb, rb_ = player(st, "Bob", 2, 6, 64, 0)         # 6 blocks away
        po, ro_ = player(st2, "Other", 3, 0, 64, 0)      # another world's store (0 blocks, never)
        uA = UUID.randomUUID()
        rc, nc = npc(st, "Cow", uA)
        q.clear()
        ns.onEntityRemove(rc, RMR.UNLOAD, st, cb)
        K.check(q.size() == 0 and RA.PEND.size() == 1, "X NPC UNLOAD of a wild Cow: remembered, nothing queued")
        setany(nc, "roleName", "Tamed_Cow")
        ns.onEntityAdded(rc, ADR.LOAD, st, cb)
        K.check(q.size() == 1 and isinstance(q.peekLast(), RAT) and int(q.peekLast().kind) == 0, "X NPC LOAD as Tamed_Cow right after: a tame task is queued")
        t0 = int(RA.TAMES.get())
        q.pollLast().run()
        K.check(int(RA.TAMES.get()) == t0 + 1 and bool(RA.SEEN_TAME), "X RanchActTask (tame): the nearest player (Alice, 3 blocks; Other in another store skipped) is paid")
        K.check(RA.ANIMAL.containsKey("0|" + str(uA)) and bool(RA.animalOk(JInt(0), uA, JLong(JClass("java.lang.System").currentTimeMillis()))),
                "X the tamed animal is marked (per-animal memory), but ranching.animalCooldownSec 0 = no wait")
        K.check(RA.COWS.contains(rc), "X the freshly tamed cow (LOAD as Tamed_Cow) joins the milkable registry")
        rs, ns_ = npc(st, "Sheep", UUID.randomUUID())
        ns.onEntityAdded(rs, ADR.SPAWN, st, cb)
        setany(ns_, "roleName", "Tamed_Sheep")
        ns.onEntityAdded(rs, ADR.SPAWN, st, cb)
        ns.onEntityAdded(rs, ADR.LOAD, st, cb)
        K.check(q.size() == 0, "X a pen animal spawned as Tamed_Sheep (SPAWN) or loaded without an UNLOAD first: no tame")
        rfar, nfar = npc(st, "Chicken", UUID.randomUUID(), 50, 64, 0)
        ns.onEntityRemove(rfar, RMR.UNLOAD, st, cb)
        setany(nfar, "roleName", "Tamed_Chicken")
        ns.onEntityAdded(rfar, ADR.LOAD, st, cb)
        nb0 = int(RA.NOBODY.get())
        K.check(q.size() == 1, "X a far tame is queued too")
        q.pollLast().run()
        K.check(int(RA.NOBODY.get()) == nb0 + 1 and int(RA.TAMES.get()) == t0 + 1, "X nobody within 8 blocks: no XP")
        RA.TAME_XP = 0
        rz, nz = npc(st, "Cow", UUID.randomUUID())
        ns.onEntityRemove(rz, RMR.UNLOAD, st, cb)
        setany(nz, "roleName", "Tamed_Cow")
        ns.onEntityAdded(rz, ADR.LOAD, st, cb)
        K.check(q.size() == 0, "X ranching.tameXp 0: taming is off")
        RA.read(PROPS())

        # ---------------- crate (T2) = a PAIR of the catcher's crate fill + the animal's REMOVE (fix round), the released-animal ledger (T2b)
        def crate(role):
            m_ = CNM()
            if role is not None:
                m_.setNpcNameKey(role)
            return IS("Tool_Capture_Crate", 1).withMetadata(CNM.KEYED_CODEC, m_)
        empty = IS("Tool_Capture_Crate", 1)
        K.check(str(crate("Chicken").getFromMetadataOrNull(CNM.KEYED_CODEC).getNpcNameKey()) == "Chicken" and empty.getFromMetadataOrNull(CNM.KEYED_CODEC) is None,
                "X a full crate's CapturedEntity metadata round-trips through the real codec (an empty crate has none)")

        def cslt(slot, before, after):
            return SLT(JBoolean(True), ACT.REPLACE if hasattr(ACT, "REPLACE") else ACT.ADD, JShort(slot), before, after, None, JBoolean(False), JBoolean(False), JBoolean(False))
        K.eq(str(RA.crateTx(cslt(1, empty, crate("Chicken")), 1)), "CChicken", "X crate scan: the ACTIVE slot's empty crate filled with a Chicken = a catch")
        K.eq(str(RA.crateTx(cslt(1, crate("Chicken"), empty), 1)), "RChicken", "X crate scan: the ACTIVE slot's Chicken crate emptied = a release")
        K.check(RA.crateTx(cslt(2, empty, crate("Chicken")), 1) is None and RA.crateTx(cslt(1, None, crate("Chicken")), 1) is None
                and RA.crateTx(cslt(1, crate("Chicken"), crate("Chicken")), 1) is None and RA.crateTx(cslt(1, IS("Food_Bread", 1), empty), 1) is None,
                "X crate scan: another slot, a crate put into an empty slot, no change, another item = nothing")
        hbC = hotbar([IS("Food_Bread", 1), empty], 1)
        pc_, rc_ = player(st, "Carol", 4, 0, 64, 2, hbC)
        pd_, rd_ = player(st, "Dave", 5, 0, 64, 1, hotbar([crate("Chicken")], 0))   # NEARER, already holding a full Chicken crate (a bystander)
        isy = RIS()
        K.check(isy.getQuery() is not None, "X RanchInvSys.getQuery = Player")
        chC = U.allocateInstance(MCH.class_)
        chC.ref = rc_

        def iceC(tx):
            return ICE(HOTB.getComponentType(), hbC, SIC(JShort(9)), tx)

        def fill(role="Chicken"):
            isy.handle(0, chC, st, cb, iceC(cslt(1, empty, crate(role))))

        def release(role="Chicken"):
            isy.handle(0, chC, st, cb, iceC(cslt(1, crate(role), empty)))
        RA.GONE.clear(); RA.CATCH.clear(); RA.RELMARK.clear(); RA.SPAWNED.clear(); RA.RELEASED.clear()
        q.clear()
        c0 = int(RA.CAPTURES.get())
        uC = UUID.randomUUID()
        rch, _ = npc(st, "Chicken", uC, 0, 64, 0)
        ns.onEntityRemove(rch, RMR.UNLOAD, st, cb)
        K.check(q.size() == 0 and RA.GONE.size() == 0, "X a chicken's chunk UNLOAD is no crate catch")
        rdead, _ = npc(st, "Chicken", UUID.randomUUID(), 0, 64, 0, dead=True)
        ns.onEntityRemove(rdead, RMR.REMOVE, st, cb)
        K.check(q.size() == 0 and RA.GONE.size() == 0, "X a dead chicken's REMOVE (a kill) is no crate catch")
        radult, _ = npc(st, "Cow", UUID.randomUUID(), 0, 64, 0)
        ns.onEntityRemove(radult, RMR.REMOVE, st, cb)
        K.check(q.size() == 0 and RA.GONE.size() == 0, "X an adult cow's REMOVE (not a crate role) is nothing")
        # 1 the crate fills first, then the animal goes
        fill()
        K.check(q.size() == 0 and RA.CATCH.size() == 1, "X FIX catch: Carol's crate fill alone waits for the animal (nothing paid)")
        ns.onEntityRemove(rch, RMR.REMOVE, st, cb)
        K.check(q.size() == 1 and int(q.peekLast().kind) == 1 and str(q.peekLast().u) == str(pc_.getUuid()), "X FIX catch: + the live chicken's REMOVE = a crate task for CAROL (Dave, nearer with a full crate, is a bystander)")
        q.pollLast().run()
        K.check(int(RA.CAPTURES.get()) == c0 + 1 and bool(RA.SEEN_CRATE) and RA.CATCH.size() == 0, "X FIX catch: Carol is paid once")
        # 2 the animal goes first, then the crate fills
        rch2, _ = npc(st, "Chicken", UUID.randomUUID(), 0, 64, 0)
        ns.onEntityRemove(rch2, RMR.REMOVE, st, cb)
        K.check(q.size() == 0 and RA.GONE.size() == 1, "X FIX catch: a chicken REMOVE alone waits (a despawn / cull / command removal near a full crate pays nothing)")
        fill()
        K.check(q.size() == 1 and int(q.peekLast().kind) == 1, "X FIX catch: + Carol's crate filling right after = the pair")
        q.pollLast().run()
        K.check(int(RA.CAPTURES.get()) == c0 + 2, "X FIX catch (animal first): paid; ranching.captureCooldownSec 0 = no wait")
        # a crate fill of ANOTHER role does not pair
        rcalf, _ = npc(st, "Cow_Calf", UUID.randomUUID(), 0, 64, 0)
        ns.onEntityRemove(rcalf, RMR.REMOVE, st, cb)
        fill("Chicken")
        K.check(q.size() == 0, "X FIX catch: a calf REMOVE + a CHICKEN crate fill = no pair")
        RA.GONE.clear(); RA.CATCH.clear()
        # out of range
        rfarc, _ = npc(st, "Chicken", UUID.randomUUID(), 40, 64, 0)
        fill()
        ns.onEntityRemove(rfarc, RMR.REMOVE, st, cb)
        nb1 = int(RA.NOBODY.get())
        q.pollLast().run()
        K.check(int(RA.CAPTURES.get()) == c0 + 2 and int(RA.NOBODY.get()) == nb1 + 1, "X catch: an animal 40 blocks from the catcher pays nothing")
        # 3 the released-animal ledger (T2b): release first, then the spawn
        release()
        K.check(RA.RELMARK.size() == 1 and q.size() == 0, "X FIX release: Carol's crate emptied = a release mark")
        uRel = UUID.randomUUID()
        rrel, _ = npc(st, "Chicken", uRel, 0, 64, 0)
        ns.onEntityAdded(rrel, ADR.SPAWN, st, cb)
        K.check(RA.RELEASED.containsKey(uRel) and RA.RELMARK.size() == 0, "X FIX release: + the chicken spawning right after = marked released")
        fill()
        ns.onEntityRemove(rrel, RMR.REMOVE, st, cb)
        r1 = int(RA.REFUSED.get())
        q.pollLast().run()
        K.check(int(RA.CAPTURES.get()) == c0 + 2 and int(RA.REFUSED.get()) == r1 + 1 and not RA.RELEASED.containsKey(uRel),
                "X FIX catch / release loop: catching the animal you released pays NOTHING (no timer needed)")
        # the spawn first, then the release
        uRel2 = UUID.randomUUID()
        rrel2, _ = npc(st, "Chicken", uRel2, 0, 64, 0)
        ns.onEntityAdded(rrel2, ADR.SPAWN, st, cb)
        K.check(RA.SPAWNED.size() == 1 and not RA.RELEASED.containsKey(uRel2), "X FIX release: a chicken spawn alone is only remembered for 1 s")
        release()
        K.check(RA.RELEASED.containsKey(uRel2) and RA.SPAWNED.size() == 0, "X FIX release (spawn first): + the crate emptying right after = marked released")
        ns.onEntityAdded(rrel2, ADR.LOAD, st, cb)
        K.check(RA.SPAWNED.size() == 0, "X release: a chunk LOAD is never a release spawn")
        release("Cow_Calf")
        uW = UUID.randomUUID()
        rwildc, _ = npc(st, "Chicken", uW, 0, 64, 0)
        ns.onEntityAdded(rwildc, ADR.SPAWN, st, cb)
        K.check(not RA.RELEASED.containsKey(uW), "X release: a calf released + a wild CHICKEN spawning = the chicken is not marked")
        RA.RELMARK.clear(); RA.SPAWNED.clear(); RA.RELEASED.clear()
        # an admin wait (ranching.captureCooldownSec 60)
        RA.PCOOL.clear()   # the earlier catches' stamps (recorded even while the wait is 0)
        RA.CAP_CD = 60000
        for i_ in range(2):
            rcx, _ = npc(st, "Chicken", UUID.randomUUID(), 0, 64, 0)
            fill()
            ns.onEntityRemove(rcx, RMR.REMOVE, st, cb)
            q.pollLast().run()
        K.check(int(RA.CAPTURES.get()) == c0 + 3, "X catch: with an admin's ranching.captureCooldownSec 60 the second catch in a minute pays nothing")
        RA.read(PROPS())
        RA.CAPTURE_XP = 0
        fill()
        K.check(RA.CATCH.size() == 0 and q.size() == 0, "X ranching.captureXp 0 = crates off")
        RA.read(PROPS())
        RA.PCOOL.clear(); RA.GONE.clear(); RA.CATCH.clear()

        # ---------------- the milk scanner (T3) on real transactions
        bucket, milk = IS("Container_Bucket", 1), IS("*Container_Bucket_State_Filled_Milk", 1)
        bucket3, bucket2 = IS("Container_Bucket", 3), IS("Container_Bucket", 2)

        def slt(slot, before, after, ok=True):
            return SLT(JBoolean(ok), ACT.REMOVE, JShort(slot), before, after, None, JBoolean(False), JBoolean(False), JBoolean(False))

        def isst(slot, before, after):
            return ISST(JBoolean(True), ACT.ADD, JShort(slot), before, after, None, JBoolean(False), JBoolean(False), JBoolean(False), JBoolean(False), None, None)

        def ist(*ss):
            l_ = AL()
            for s_ in ss:
                l_.add(s_)
            return IST(JBoolean(True), ACT.ADD, None, None, JBoolean(False), JBoolean(False), l_)
        K.eq(int(RA.scanTx(slt(2, bucket, None), True, 2)), 1, "X scan: the held empty bucket leaves the ACTIVE hotbar slot = 1")
        K.eq(int(RA.scanTx(slt(2, bucket3, bucket2), True, 2)), 1, "X scan: one of a held stack of 3 buckets = 1")
        K.eq(int(RA.scanTx(slt(3, bucket, None), True, 2)), 0, "X scan: another hotbar slot = 0")
        K.eq(int(RA.scanTx(slt(2, bucket, None), False, -1)), 0, "X scan: a storage slot = 0")
        K.eq(int(RA.scanTx(slt(2, bucket, None, ok=False), True, 2)), 0, "X scan: a failed transaction = 0")
        K.eq(int(RA.scanTx(ist(isst(5, None, milk)), False, -1)), 2, "X scan: a filled milk bucket arrives (ItemStackTransaction, any container) = 2")
        K.eq(int(RA.scanTx(ist(isst(5, IS("*Container_Bucket_State_Filled_Milk", 1), IS("*Container_Bucket_State_Filled_Milk", 2))), False, -1)), 2, "X scan: added onto a milk stack = 2")
        K.eq(int(RA.scanTx(ist(isst(5, None, IS("*Deco_Bucket_State_Filled_Mosshorn_Milk", 1))), False, -1)), 2, "X scan: a mosshorn milk deco bucket = 2")
        K.eq(int(RA.scanTx(ist(isst(5, None, IS("*Container_Bucket_State_Filled_Water", 1))), False, -1)), 0, "X scan: a WATER bucket = 0")
        K.eq(int(RA.scanTx(slt(2, bucket, milk), True, 2)), 3, "X scan: the held bucket turned into milk in one change = 3")
        l_ = AL()
        l_.add(slt(2, bucket, None))
        l_.add(ist(isst(4, None, milk)))
        K.eq(int(RA.scanTx(LTX(JBoolean(True), l_), True, 2)), 3, "X scan: a ListTransaction of both = 3")
        mv = MVT(JBoolean(True), slt(2, bucket, None), MVY.MOVE_TO_SELF, SIC(JShort(4)), ist(isst(4, None, milk)))
        K.eq(int(RA.scanTx(mv, True, 2)), 0, "X scan: a MOVE (chest, drag) never counts")
        l2 = AL()
        l2.add(mv)
        K.eq(int(RA.scanTx(LTX(JBoolean(True), l2), True, 2)), 0, "X scan: a move inside a list never counts")

        # ---------------- the milk pair
        uM = UUID.randomUUID()
        K.check(not bool(RA.milkPair(uM, JInt(1), JLong(5000))) and bool(RA.milkPair(uM, JInt(2), JLong(5100))), "X pair: bucket out, then milk in 100 ms = one milking")
        K.check(not bool(RA.milkPair(uM, JInt(2), JLong(5150))), "X pair: cleared after paying (a second milk add alone is nothing)")
        RA.MILKST.clear()
        K.check(not bool(RA.milkPair(uM, JInt(2), JLong(7000))) and bool(RA.milkPair(uM, JInt(1), JLong(7200))), "X pair: milk in first, then bucket out = one milking")
        K.check(not bool(RA.milkPair(uM, JInt(1), JLong(9000))) and not bool(RA.milkPair(uM, JInt(2), JLong(10500))), "X pair: 1.5 s apart = no milking")
        RA.MILKST.clear()
        K.check(bool(RA.milkPair(uM, JInt(3), JLong(20000))), "X pair: both at once (3) = a milking")
        RA.MILKST.clear()
        K.check(not bool(RA.milkPair(uM, JInt(1), JLong(50000))) and not bool(RA.milkPair(uM, JInt(2), JLong(50300))), "X FIX pair: 300 ms apart (more than one tick) = no milking")
        RA.MILKST.clear()
        RA.note(uM, JInt(0), JLong(30000))
        K.check(bool(RA.noted(uM, JLong(30500))), "X noted: the player dropped something 0.5 s before = no milking")
        K.check(not bool(RA.noted(uM, JLong(32000))), "X noted: 2 s after the drop = a milking again")
        RA.notePick(uM, "Food_Egg", JLong(40000))
        K.check(not bool(RA.noted(uM, JLong(40100))), "X noted: an egg pickup does not block")
        RA.notePick(uM, "*Container_Bucket_State_Filled_Milk", JLong(41000))
        K.check(bool(RA.noted(uM, JLong(41100))), "X noted: a milk-bucket PICKUP 0.1 s before = no milking")
        RA.NOTE.clear()
        RA.MILKST.clear()

        # ---------------- RanchInvSys.handle with real InventoryChangeEvents (fix round: the pair queues a RanchActTask kind 2, decided later)
        isy = RIS()
        RA.COWS.clear()
        RA.PCOOL.clear()
        hbE = hotbar([None, None, bucket], 2)
        pe_, re_ = player(st, "Erin", 6, 0, 64, 0, hbE)
        chE = U.allocateInstance(MCH.class_)
        chE.ref = re_
        stor = U.allocateInstance(STOR.class_)

        def ice(hot, tx):
            return ICE(HOTB.getComponentType() if hot else newct(), hbE if hot else stor, SIC(JShort(9)), tx)

        def runq():
            n_q = q.size()
            while q.size() > 0:
                q.pollFirst().run()
            return n_q
        q.clear()
        m0 = int(RA.MILKS.get())
        isy.handle(0, chE, st, cb, ice(True, slt(2, bucket, milk)))
        K.check(q.size() == 1 and isinstance(q.peekLast(), RAT) and int(q.peekLast().kind) == 2, "X FIX InvSys: a pair queues a milking decision (RanchActTask kind 2) for one world task later")
        runq()
        K.check(int(RA.MILKS.get()) == m0, "X InvSys: a bucket -> milk pair with NO tamed cow within range (a bought bucket) = nothing")
        RA.MILKST.clear()
        rfarcow, _ = npc(st, "Tamed_Cow", UUID.randomUUID(), 30, 64, 0)
        ns.onEntityAdded(rfarcow, ADR.SPAWN, st, cb)
        isy.handle(0, chE, st, cb, ice(True, slt(2, bucket, milk)))
        runq()
        K.check(int(RA.MILKS.get()) == m0, "X InvSys: a tamed cow 30 blocks away is out of range = nothing")
        RA.MILKST.clear()
        uCow1, uCow2 = UUID.randomUUID(), UUID.randomUUID()
        rcow1, _ = npc(st, "Tamed_Cow", uCow1, 1, 64, 0)
        rwild, _ = npc(st, "Cow", UUID.randomUUID(), 0, 64, 0)
        rcow2, _ = npc(st2, "Tamed_Cow", uCow2, 0, 64, 0)
        for r_ in (rcow1, rwild):
            ns.onEntityAdded(r_, ADR.SPAWN, st, cb)
        ns.onEntityAdded(rcow2, ADR.SPAWN, st2, cb)
        K.check(RA.COWS.size() == 3 and not RA.COWS.contains(rwild), "X the registry: tamed cows in (any add reason), a WILD cow never")
        K.eq(str(RA.cowNear(st, 0.0, 64.0, 0.0)), str(uCow1), "X cowNear: the nearest tamed cow of THIS store within range")
        isy.handle(0, chE, st, cb, ice(True, slt(2, bucket, None)))
        K.check(q.size() == 0, "X InvSys: the bucket leaving the hand alone queues nothing")
        isy.handle(0, chE, st, cb, ice(False, ist(isst(7, None, milk))))
        K.check(q.size() == 1, "X InvSys: + the milk bucket arriving in storage = one decision queued")
        runq()
        K.check(int(RA.MILKS.get()) == m0 + 1, "X InvSys: ... which pays ONE milking (the pickup award path)")
        isy.handle(0, chE, st, cb, ice(True, slt(2, bucket, milk)))
        runq()
        K.check(int(RA.MILKS.get()) == m0 + 2, "X FIX InvSys: the same cow again right away pays too - no XP-only wait by default (the cow's own Harvest wait is the real limit)")
        RA.MILK_CD = 2000
        isy.handle(0, chE, st, cb, ice(True, slt(2, bucket, milk)))
        runq()
        K.check(int(RA.MILKS.get()) == m0 + 2, "X InvSys: with an admin's ranching.milkCooldownSec 2 another milking within 2 s pays nothing")
        RA.MILK_CD = 0
        RA.PCOOL.clear()
        RA.COW_MS = 600000
        isy.handle(0, chE, st, cb, ice(True, slt(2, bucket, milk)))
        runq()
        K.check(int(RA.MILKS.get()) == m0 + 2, "X InvSys: with an admin's ranching.cowCooldownSec 600 the SAME cow again pays nothing")
        RA.read(PROPS())
        RA.PCOOL.clear()
        RA.MILKST.clear()
        ns.onEntityRemove(rcow1, RMR.UNLOAD, st, cb)
        K.check(not RA.COWS.contains(rcow1), "X the registry: a cow that leaves (unload / death / crate) is dropped")
        rcow3, _ = npc(st, "Tamed_Mosshorn", UUID.randomUUID(), 2, 64, 0)
        ns.onEntityAdded(rcow3, ADR.LOAD, st, cb)
        isy.handle(0, chE, st, cb, ice(True, slt(2, bucket, milk)))
        runq()
        K.check(int(RA.MILKS.get()) == m0 + 3, "X InvSys: a mosshorn nearby = paid")
        isy.handle(0, chE, st, cb, ice(True, slt(1, bucket, None)))
        isy.handle(0, chE, st, cb, ice(False, ist(isst(7, None, milk))))
        K.check(q.size() == 0, "X InvSys: a bucket leaving a NON-active hotbar slot + milk = nothing")
        RA.MILKST.clear()
        isy.handle(0, chE, st, cb, ice(True, mv))
        K.check(q.size() == 0, "X InvSys: a move of a bucket + milk = nothing")
        RA.note(pe_.getUuid(), JInt(0), JLong(JClass("java.lang.System").currentTimeMillis()))
        isy.handle(0, chE, st, cb, ice(True, slt(2, bucket, milk)))
        runq()
        K.check(int(RA.MILKS.get()) == m0 + 3, "X InvSys: right after a drop = nothing")
        RA.NOTE.clear()
        r2 = int(RA.REFUSED.get())
        isy.handle(0, chE, st, cb, ice(True, slt(2, bucket, milk)))
        K.check(q.size() == 1, "X FIX (order) the pair is queued before the pickup's note exists ...")
        RA.notePick(pe_.getUuid(), "*Container_Bucket_State_Filled_Milk", JLong(JClass("java.lang.System").currentTimeMillis()))   # RanchPickSys, later in the same tick
        runq()
        K.check(int(RA.MILKS.get()) == m0 + 3 and int(RA.REFUSED.get()) == r2 + 1, "X FIX (order) ... a milk-bucket PICKUP noted AFTER the inventory event (same tick) still refuses it")
        RA.NOTE.clear()
        RA.MILK_XP = 0
        isy.handle(0, chE, st, cb, ice(True, slt(2, bucket, milk)))
        K.check(q.size() == 0, "X InvSys: ranching.milkXp 0 = off")
        RA.read(PROPS())

        # ---------------- the pickup / drop notes (RanchPickSys keeps working with pickup XP off)
        Ranch.ON = False
        RA.NOTE.clear()
        K.check(int(RA.MILK_XP) == 100, "X (milk on)")
        # retain: players who left are forgotten
        RA.PCOOL.clear()
        RA.CAP_CD = 60000
        nowr = int(JClass("java.lang.System").currentTimeMillis())
        uR = UUID.randomUUID()
        RA.markPlayer(JInt(2), uM, JLong(1))
        RA.markPlayer(JInt(1), uR, JLong(nowr))
        RA.note(uM, JInt(1), JLong(1))
        RA.milkPair(uM, JInt(1), JLong(1))
        RA.GONE.clear()
        RA.catchMark(uM, None, "Chicken", st, JLong(1))
        on = HSet()
        RA.retain(on)
        K.check(RA.NOTE.size() == 0 and RA.MILKST.size() == 0 and RA.CATCH.size() == 0, "X retain: the pair state of players who left is dropped")
        K.check(RA.PCOOL.size() == 1 and RA.PCOOL.containsKey(uR), "X FIX retain: a wait still running is KEPT while its player is offline (a relog never resets it); an old one is pruned by age")
        RA.read(PROPS())
        RA.retain(on)
        K.check(RA.PCOOL.size() == 0, "X retain: with the waits off (0) every stamp is pruned")
        Ranch.ON = True
        K.check(not bool(RA.FAILED), "X no RanchAct path failed (FAILED stays false)")
    except Exception as e:
        import traceback
        traceback.print_exc()
        K.check(False, "X: run crashed: %s" % str(e)[:400])
    K.save()


def run_live(out, jar, scratch, home):
    T64.run_live(out, jar, scratch, home)


def run_live2(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    L = T64.T48.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Cfg, RA = J("SkillCfg"), J("RanchAct")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    xp = os.path.join(home, "xp.properties")
    before = open(xp, "rb").read()
    K.check(not any((k + "=") in before.decode("utf8", "replace") for k, v in R66_KEYS), "LIVE2 the live xp.properties has no 0.4.66 line yet")
    Cfg.FILE = T64.jpath(xp)
    r = str(Cfg.load())
    K.check(int(RA.TAME_XP) == 250 and int(RA.CAPTURE_XP) == 100 and int(RA.MILK_XP) == 100 and int(RA.CAP_CD) == 0 and int(RA.COW_MS) == 0 and float(RA.RANGE) == 8.0
            and RA.TAME.size() >= 20, "LIVE2 the live file reads every RanchAct code default (load: %s)" % r[:80])
    K.check(open(xp, "rb").read() == before, "LIVE2 the live xp.properties is unchanged (no migration)")
    K.save()


if __name__ == "__main__":
    phases = [("static", run_static), ("fakes", run_fakes), ("x", run_x), ("live", run_live), ("live2", run_live2)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
