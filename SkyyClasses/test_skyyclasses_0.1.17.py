"""SkyyClasses 0.1.17 (+ SkyyHud 0.3.18) - bare-JVM harness for THE CLASS ABILITY ENGINE, ROUND R3 (Mana Barrier + Shield Bubble) and the
R2 bridge data (tools/classes_0_1_17_patch.py, tools/hud_0_3_18_patch.py; research/cloud/Ability-Engine-Plan.md R2 + R3). Child JVMs run the
game's own JRE with HytaleServer.jar on the class path, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder.
Live save data is only ever READ and copied into scratch (checked afterwards).

    python SkyyClasses/test_skyyclasses_0.1.17.py --dir <empty folder inside tools/dev/scratch/> [--keep]

SECTIONS
  A   every class of SkyyClasses 0.1.17 loads, verifies (-Xverify:all) and initialises; SkyyClasses 0.1.16, SkyySkills 0.4.27 / 0.4.28 and
      SkyyHud 0.3.18 in their own loaders too
  CC  CLASS COMPARE SkyyClasses 0.1.16 -> 0.1.17 (javassist instruction text): only the planned classes / methods change; AbilZone,
      AbilShieldSys, AbilShieldSysU are the only new classes
  N   the WHOLE 0.1.16 R1 run again on the 0.1.17 jar (engine stand-ins: a map-backed Store / CommandBuffer, the REAL EntityStatMap with
      the vanilla stat types from Assets.zip, real Ref / PlayerRef / Player / MovementStatesComponent / Damage): every R1 check kept; the
      only R1 expectations that change are the ones about Mana Barrier, which is BUILT now (it casts instead of "comes in a later update")
  Z   ZONES (R3) EXECUTED: Mana Barrier + Shield Bubble cast on test players (spot = the aim / the feet, cost + cooldown, the rings), the
      REAL AbilShieldSys.handle (the Filter-group hook) with real Damage objects: Mana instead of Health (2 HP per Mana), partly / fully
      soaked, 0 Mana ends it, the 100 % cap ends it, outside = untouched, out-of-world damage untouched, another player in the dome
      untouched; the bubble soaks attacks on the Priest + a party member (a stranger and fall damage untouched), 4 heal pulses at 75 /
      50 / 25 / 0 % through the REAL AbilTick, the break, the absorb XP, a profile switch (barrier ends; bubble no XP), expiry, maxZones,
      the world cap with zones, the ordered + fallback system (SystemDependency AFTER ArmorDamageReduction), a throwing zone is dropped
  H   the HUD bridge: class:fn:abil = Object[44]; per ability state (ready / cooldown / unaffordable / locked / creative free / crouch =
      alts) from the REAL AbilTick world-thread sample; no class = null; SkyyHud 0.3.18 (its own loader, the SAME bridge map): the
      Abilities widget model for each state (rows, right texts, grey, bars, icons, crouch swap) and hidden without class:fn:abil
  SK  SkyySkills 0.4.28 on the SAME bridge (unchanged: an ability kill pays the caster's class skill)
  ST  START TWICE on a scratch COPY of the live Skyy_SkyyClasses folder (config part of setup in its real order, each start its own JVM):
      nothing written, the R3 rows read their defaults; Server Setup sets ab.ManaBarrier.walk.cooldown 20 -> one line + one log line +
      one History copy, read back by the next start
FIX ROUND checks ("FIX Z..." / "FIX H..."): the dome covers the Mage (a look point past radius - 0.5 -> her feet), ab.ManaBarrier.keep
(4 Mana left after the cost, refused + nothing spent below it, the bridge's affordable counts it), AbilShieldSys ordered AFTER the engine
filters that drop hits, an Invulnerable victim untouched, no absorb XP for a PLAYER's hit, the dome-shaped rims (edge + upper ring + top).
"""
import os, sys, re, json, time, shutil, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.1.17", "0.1.16"
PKG = "com.skyy.classes."
SPKG = "com.skyy.skills."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "abil02", "classes0117")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyClasses-%s.jar" % PREV_VERSION)))
SK_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.28.jar")
SK_PREV = os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.27.jar")
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyClasses")
ASSETS = os.path.join(APPDATA, "Hytale", "install", "release", "package", "game", "latest", "Assets.zip")
FAILS, OKS = [], [0]
R1_CLASSES = ["AbilCfg", "AbilDmg", "AbilHitFn", "AbilDefs", "AbilMath", "AbilStore", "AbilSave", "AbilJob", "AbilWorld", "Abil", "AbilFn",
              "AbilTick", "CastCmd", "CastArgCmd", "AdminAbilCmd"]
NEW_CLASSES = ["AbilZone", "AbilShieldSys", "AbilShieldSysU"]
HUD_JAR = os.path.join(ROOT, "SkyyHud", "SkyyHud-0.3.18.jar")


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def sk():
    """the SkyySkills 0.4.27 harness module (shared JVM helpers + run_cc); imported, never run"""
    spec = importlib.util.spec_from_file_location("ts0427", os.path.join(ROOT, "SkyySkills", "test_skyyskills_0.4.27.py"))
    m = importlib.util.module_from_spec(spec)
    saved = list(sys.argv)
    sys.argv = [sys.argv[0], "--dir", SCRATCH]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    m.SCRATCH = SCRATCH
    return m


def jvm(extra):
    import jpype
    import skyybuild as B
    j = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(j):
        j = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(j, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, B.JAVASSIST] + list(extra), convertStrings=True)
    return B


# ============================================================================================================ child: A + N + SK
def run_n(out):
    import jpype
    from jpype import JClass, JArray, JString, JImplements, JOverride, JObject, JFloat, JDouble, JLong, JInt, JBoolean
    hcls = os.path.join(SCRATCH, "hcls")
    os.makedirs(hcls, exist_ok=True)
    B = jvm([hcls, JAR])
    R = {"checks": [], "notes": []}

    def ck(cond, what):
        R["checks"].append([bool(cond), what])

    Cls = JClass("java.lang.Class")
    sysl = JClass("java.lang.ClassLoader").getSystemClassLoader()
    # ---------------- A. every class of the new jar, -Xverify:all, initialised
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(JAR).namelist() if n.endswith(".class")]
    afails = []
    for n in names:
        try:
            c = Cls.forName(n, True, sysl)
            c.getDeclaredMethods()
            c.getDeclaredFields()
        except Exception as e:
            afails.append("%s: %s" % (n, str(e)[:200]))
    ck(not afails, "A: all %d SkyyClasses 0.1.17 classes load, verify (-Xverify:all) and initialise: %s" % (len(names), afails[:3]))
    ck(all(PKG + c in names for c in R1_CLASSES + NEW_CLASSES), "A: the 15 R1 ability classes + AbilZone / AbilShieldSys / AbilShieldSysU are in the jar")
    S = sk()
    ldk, ldo = S.loader(SK_JAR), S.loader(SK_PREV)
    nk, fk = S.load_all(SK_JAR, ldk)
    no, fo = S.load_all(SK_PREV, ldo)
    np_, fp = S.load_all(PREV_JAR, S.loader(PREV_JAR))
    ldh = S.loader(HUD_JAR)
    nh, fh = S.load_all(HUD_JAR, ldh)
    ck(not fk and not fo and not fp and not fh, "A: SkyySkills 0.4.28 (%d), 0.4.27 (%d), SkyyClasses 0.1.16 (%d) and SkyyHud 0.3.18 (%d) classes load + verify in their own loaders: %s"
       % (nk, no, np_, nh, (fk + fo + fp + fh)[:3]))

    Uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    Uf.setAccessible(True)
    U = Uf.get(None)

    def jfield(cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f

    def setf(o, cls, name, v):
        jfield(cls, name).set(o, v)
    C = lambda n: JClass(PKG + n)
    UUID, ArrayList, HashMap, CHM = JClass("java.util.UUID"), JClass("java.util.ArrayList"), JClass("java.util.HashMap"), JClass("java.util.concurrent.ConcurrentHashMap")
    Paths = JClass("java.nio.file.Paths")
    CPj = JClass("javassist.ClassPool")(True)
    CPj.appendClassPath(B.SERVER_JAR)
    CtNM, CTF, CNC = JClass("javassist.CtNewMethod"), JClass("javassist.CtField"), JClass("javassist.CtNewConstructor")

    # ---------------- N0. the engine stand-ins
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "universe")]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    setf(hs, HS, "eventBus", JClass("com.hypixel.hytale.event.EventBus")(False))
    jfield(HS, "instance").set(None, hs)
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu = CHM()
    setf(uni, UNI, "playersByUuid", pbu)
    setf(uni, UNI, "players", JClass("java.util.Collections").unmodifiableCollection(pbu.values()))
    wmap = CHM()
    setf(uni, UNI, "worlds", wmap)
    setf(uni, UNI, "worldsByUuid", CHM())
    setf(uni, UNI, "unmodifiableWorlds", JClass("java.util.Collections").unmodifiableMap(wmap))
    jfield(UNI, "instance").set(None, uni)
    # the vanilla stat types (Mana / Stamina / Health indices) from Assets.zip through the engine's own codec + store
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    HAS = JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    ARR = JClass("java.lang.reflect.Array")
    ESTc = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")

    @JImplements("java.util.function.Function")
    class GetId:
        @JOverride
        def apply(self, o): return o.getId()

    @JImplements("java.util.function.IntFunction")
    class ArrOf:
        def __init__(self, c): self.c = c

        @JOverride
        def apply(self, n): return ARR.newInstance(self.c.class_, n)

    @JImplements("java.util.function.Function")
    class NoRep:
        @JOverride
        def apply(self, k): return None
    try:
        AR.register(HAS.builder(ESTc.class_, ILT(ArrOf(ESTc))).setPath("Entity/Stats").setCodec(ESTc.CODEC).setKeyFunction(GetId())
                    .setReplaceOnRemove(NoRep()).build())
    except Exception as e:
        R["notes"].append("stat store: %s" % str(e)[:200])
    AEI, ADT, RJR = (JClass("com.hypixel.hytale.assetstore.AssetExtraInfo"), JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data"),
                     JClass("com.hypixel.hytale.codec.util.RawJsonReader"))
    stl = ArrayList()
    with zipfile.ZipFile(ASSETS) as z:
        for n in z.namelist():
            if n.startswith("Server/Entity/Stats/") and n.endswith(".json"):
                key = n.rsplit("/", 1)[1][:-5]
                d = json.loads(z.read(n).decode("utf-8-sig"))
                for k_ in ("Regenerating", "MinValueEffects", "MaxValueEffects"):     # only the ids / ranges matter here (no interaction store)
                    d.pop(k_, None)
                ei = AEI(Paths.get(key + ".json"), ADT(ESTc.class_, key, None))
                o = AR.getAssetStore(ESTc.class_).getCodec().decodeJsonAsset(RJR.fromJsonString(json.dumps(d)), ei)
                if o is not None:
                    stl.add(o)
    AR.getAssetStore(ESTc.class_).loadAssets("Hytale:Hytale", stl)
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    DST.update()
    MANA, STAM, HP = int(DST.getMana()), int(DST.getStamina()), int(DST.getHealth())
    ck(MANA >= 0 and STAM >= 0 and HP >= 0 and len({MANA, STAM, HP}) == 3, "N0: the vanilla stat types load (Mana %d, Stamina %d, Health %d)" % (MANA, STAM, HP))

    def gfield(clsname, meth):
        cc_ = CPj.get(clsname)
        ms_ = [x for x in cc_.getDeclaredMethods() if str(x.getName()) == meth]
        while not ms_:
            cc_ = cc_.getSuperclass()
            ms_ = [x for x in cc_.getDeclaredMethods() if str(x.getName()) == meth]
        m_ = ms_[0]
        it_ = m_.getMethodInfo().getCodeAttribute().iterator()
        cp_ = m_.getMethodInfo().getConstPool()
        while it_.hasNext():
            p_ = it_.next()
            if it_.byteAt(p_) == 0xb4:
                return str(cp_.getFieldrefName(it_.u16bitAt(p_ + 1)))
        return None

    @JImplements("java.util.function.Supplier")
    class Sup:
        def __init__(self, f): self.f = f

        @JOverride
        def get(self): return self.f()

    ESr = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    em = U.allocateInstance(EMc.class_)
    reg_ = ESr.REGISTRY
    TCc = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    PLAc = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    MSCc = JClass("com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent")
    MSTc = JClass("com.hypixel.hytale.protocol.MovementStates")
    INVUc = JClass("com.hypixel.hytale.server.core.modules.entity.component.Invulnerable")
    NPCc = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    ESMc = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    DTHc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    INVC = "com.hypixel.hytale.server.core.inventory.InventoryComponent"
    EMN = "com.hypixel.hytale.server.core.modules.entity.EntityModule"
    reg_errs = []
    setf(em, EMc, gfield(EMN, "getTransformComponentType"), reg_.registerComponent(TCc.class_, "Transform", jfield(TCc, "CODEC").get(None)))
    for getter_, cls_ in (("getPlayerComponentType", PLAc), ("getMovementStatesComponentType", MSCc), ("getInvulnerableComponentType", INVUc),
                          ("getToolInventoryComponentType", JClass(INVC + "$Tool")), ("getHotbarInventoryComponentType", JClass(INVC + "$Hotbar")),
                          ("getUtilityInventoryComponentType", JClass(INVC + "$Utility")),
                          ("getKnockbackComponentType", JClass("com.hypixel.hytale.server.core.entity.knockback.KnockbackComponent"))):
        try:
            setf(em, EMc, gfield(EMN, getter_), reg_.registerComponent(cls_.class_, Sup(lambda: None)))
        except Exception as e_:
            reg_errs.append("%s: %s" % (getter_, str(e_)[:120]))
    npc_t = reg_.registerComponent(NPCc.class_, Sup(lambda: None))
    c2t = HashMap()
    c2t.put(NPCc.class_, npc_t)
    setf(em, EMc, "classToComponentType", c2t)
    setf(em, JClass("com.hypixel.hytale.server.core.plugin.PluginBase"), "state", JClass("com.hypixel.hytale.server.core.plugin.PluginState").ENABLED)
    jfield(EMc, "instance").set(None, em)
    setf(uni, UNI, gfield("com.hypixel.hytale.server.core.universe.Universe", "getPlayerRefComponentType"), reg_.registerComponent(PRc.class_, Sup(lambda: None)))
    ESMOD = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    esmod = U.allocateInstance(ESMOD.class_)
    setf(esmod, ESMOD, "entityStatMapComponentType", reg_.registerComponent(ESMc.class_, Sup(lambda: ESMc())))
    jfield(ESMOD, "instance").set(None, esmod)
    DMOD_ = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageModule")
    dmod = U.allocateInstance(DMOD_.class_)
    setf(dmod, DMOD_, "deathComponentType", reg_.registerComponent(DTHc.class_, Sup(lambda: None)))
    jfield(DMOD_, "instance").set(None, dmod)
    DCSc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCause")
    if DCSc.PROJECTILE is None:
        jfield(DCSc, "PROJECTILE").set(None, DCSc("Projectile"))
    ck(not reg_errs and PLAc.getComponentType() is not None and MSCc.getComponentType() is not None and INVUc.getComponentType() is not None
       and NPCc.getComponentType() is not None and PRc.getComponentType() is not None, "N0: the component types are registered like the modules do: %s" % reg_errs)

    def stub(name, sup, fields, methods, ctor=None):
        c_ = CPj.makeClass("abilharness." + name, CPj.get(sup))
        if ctor is not None:
            c_.addConstructor(CNC.make(ctor, c_))
        for f_ in fields:
            c_.addField(CTF.make(f_, c_))
        for m_ in methods:
            c_.addMethod(CtNM.make(m_, c_))
        c_.writeFile(hcls)
        return JClass("abilharness." + name)
    CP_ = "com.hypixel.hytale.component."
    GETC = ("public " + CP_ + "Component getComponent(" + CP_ + "Ref r, " + CP_ + "ComponentType t) { java.util.Map m = (java.util.Map) abilharness.TStore.COMP.get(r); "
            "if (m == null) return null; return (" + CP_ + "Component) m.get(t); }")
    PUTC = ("public void putComponent(" + CP_ + "Ref r, " + CP_ + "ComponentType t, " + CP_ + "Component c) { java.util.Map m = (java.util.Map) abilharness.TStore.COMP.get(r); "
            "if (m == null) { m = new java.util.HashMap(); abilharness.TStore.COMP.put(r, m); } m.put(t, c); }")
    TSt = stub("TStore", CP_ + "Store", ["public static java.util.HashMap COMP = new java.util.HashMap();", "public static Object EXT = null;"],
               [GETC, PUTC, "public Object getExternalData() { return EXT; }",
                "public " + CP_ + "Resource getResource(" + CP_ + "ResourceType t) { return null; }"],
               ctor="public TStore() { super((" + CP_ + "ComponentRegistry) null, 0, (Object) null, (" + CP_ + "IResourceStorage) null); }")
    TBf = stub("TBuf", CP_ + "CommandBuffer", ["public static java.util.ArrayList EVENTS = new java.util.ArrayList();", "public static " + CP_ + "Store STORE = null;"],
               [GETC, PUTC, "public Object getExternalData() { return abilharness.TStore.EXT; }",
                "public " + CP_ + "Resource getResource(" + CP_ + "ResourceType t) { return null; }",
                "public void invoke(" + CP_ + "Ref r, " + CP_ + "system.EcsEvent e) { EVENTS.add(new Object[] { r, e }); }",
                "public " + CP_ + "Store getStore() { return STORE; }",
                "public void tryRemoveComponent(" + CP_ + "Ref r, " + CP_ + "ComponentType t) { }"])
    WLDc = JClass("com.hypixel.hytale.server.core.universe.world.World")
    TWd = stub("TWorld", "com.hypixel.hytale.server.core.universe.world.World", [], ["public void execute(java.lang.Runnable r) { r.run(); }"],
               ctor="public TWorld() { super((String) null, (java.nio.file.Path) null, (com.hypixel.hytale.server.core.universe.world.WorldConfig) null); }")
    tst = U.allocateInstance(TSt.class_)
    TBf.STORE = tst
    tbuf = U.allocateInstance(TBf.class_)
    world = U.allocateInstance(TWd.class_)
    setf(world, WLDc, "name", "abil-test")
    es = U.allocateInstance(ESr.class_)
    setf(es, ESr, gfield("com.hypixel.hytale.server.core.universe.world.storage.EntityStore", "getWorld"), world)
    ebu = HashMap()
    setf(es, ESr, "entitiesByUuid", ebu)
    TSt.EXT = es
    REFc = JClass(CP_ + "Ref")
    V3 = JClass("org.joml.Vector3d")
    R3 = JClass("com.hypixel.hytale.math.vector.Rotation3f")
    SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MT = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CT_ = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    GM = JClass("com.hypixel.hytale.protocol.GameMode")
    AtomRef = JClass("java.util.concurrent.atomic.AtomicReference")

    def put(r_, t_, c_):
        tst.putComponent(r_, t_, c_)

    def stats(mana=55.0, stam=14.0, hp=100.0, hpmax=100.0):
        m_ = ESMc()
        m_.update()
        for i_, want_ in ((MANA, 500.0), (STAM, 50.0)):
            m_.putModifier(i_, "abiltest", SMO(MT.MAX, CT_.ADDITIVE, JFloat(want_)))
        hm = float(m_.get(HP).getMax())
        if hm != hpmax:
            m_.putModifier(HP, "abiltest", SMO(MT.MAX, CT_.ADDITIVE, JFloat(hpmax - hm)))
        m_.setStatValue(MANA, JFloat(mana))
        m_.setStatValue(STAM, JFloat(stam))
        m_.setStatValue(HP, JFloat(hp))
        return m_

    def sv(m_, i_):
        return round(float(m_.get(i_).get()), 3)

    PLAYERS = {}

    def player(i_, x, y, z, name, gm="Adventure", **kw):
        u_ = UUID.fromString("00000000-0000-0000-00ab-%012d" % i_)
        r_ = REFc(tst, i_)
        pr_ = U.allocateInstance(PRc.class_)
        setf(pr_, PRc, "uuid", u_)
        setf(pr_, PRc, "entity", r_)
        setf(pr_, PRc, "username", name)
        pbu.put(u_, pr_)
        ebu.put(u_, r_)
        put(r_, PRc.getComponentType(), pr_)
        put(r_, TCc.getComponentType(), TCc(V3(x, y, z), R3(0.0, 0.0, 0.0)))
        m_ = stats(**kw)
        put(r_, ESMc.getComponentType(), m_)
        msc = MSCc()
        msc.setMovementStates(MSTc())
        put(r_, MSCc.getComponentType(), msc)
        pl_ = U.allocateInstance(PLAc.class_)
        setf(pl_, PLAc, "waitingForClientReady", AtomRef())
        setf(pl_, PLAc, "gameMode", getattr(GM, gm))
        put(r_, PLAc.getComponentType(), pl_)
        PLAYERS[name] = (u_, r_, pr_, m_, pl_, msc)
        return u_, r_, pr_, m_, pl_, msc

    def npc(i_, x, y, z, hp=100.0, invu=False):
        r_ = REFc(tst, i_)
        put(r_, NPCc.getComponentType(), TCc())
        put(r_, ESMc.getComponentType(), stats(hp=hp))
        put(r_, TCc.getComponentType(), TCc(V3(x, y, z), R3(0.0, 0.0, 0.0)))
        if invu:
            put(r_, INVUc.getComponentType(), INVUc.INSTANCE)
        return r_

    # ---------------- the mod's statics, seams and the fake partner bridges
    Cfg, Defs, Store = C("ClassCfg"), C("ClassDefs"), C("ClassStore")
    AC, AD, AM, AS, AW, A, AJ = C("AbilCfg"), C("AbilDefs"), C("AbilMath"), C("AbilStore"), C("AbilWorld"), C("Abil"), C("AbilJob")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyClasses")
    home = os.path.join(SCRATCH, "n-home")
    shutil.rmtree(home, ignore_errors=True)
    os.makedirs(os.path.join(home, "players"))
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    load_txt = str(Cfg.load())
    Store.DIR = Paths.get(os.path.join(home, "players"))
    AS.DIR = Paths.get(os.path.join(home, "abilities"))
    AS.SYNC = True
    PSEEN, SAID = ArrayList(), ArrayList()
    A.PSEEN = PSEEN
    A.SAID = SAID
    SOUNDS = ArrayList()
    A.SOUNDS = SOUNDS
    br = Cfg.bridge()
    LEVEL, COMBAT, HEALXP, PROFKEY, HANDS, AIMS, NEARL = {}, {}, [], {}, {}, {}, []

    @JImplements("java.util.function.Function")
    class LevelFn:
        @JOverride
        def apply(self, o):
            a_ = list(o)
            return JInt(LEVEL.get((str(a_[0]), str(a_[1])), 0))

    @JImplements("java.util.function.Function")
    class CombatFn:
        @JOverride
        def apply(self, o): return JLong(COMBAT.get(str(o), 0))

    @JImplements("java.util.function.Function")
    class HealXp:
        @JOverride
        def apply(self, o):
            a_ = list(o)
            HEALXP.append([str(a_[0]), round(float(a_[1]), 3), str(a_[2]), len(a_) > 4])
            return JBoolean(True)

    @JImplements("java.util.function.Function")
    class KeyFn:
        @JOverride
        def apply(self, o): return PROFKEY.get(str(o), str(o))

    @JImplements("java.util.function.Function")
    class Members:
        @JOverride
        def apply(self, o): return JArray(JObject)([JString(x) for x in MEMBERS.get(str(o), [])])

    @JImplements("java.util.function.Function")
    class ArmInfo:
        @JOverride
        def apply(self, o):
            a_ = list(o)
            if str(a_[0]) == "staff" and str(a_[1]) == "Weapon_Staff_Wood":
                return JArray(JObject)([JInt(10), JInt(2), JDouble(1.0), JInt(50), JInt(10), JDouble(100.0), JString("o"), JString("q")])
            if str(a_[0]) == "wand" and str(a_[1]) == "Weapon_Wand_Iron":
                return JArray(JObject)([JInt(15), JInt(3), JDouble(3.5), JInt(88), JInt(18), JDouble(120.0), JString("o"), JString("q")])
            return None

    @JImplements("java.util.function.Function")
    class Hand:
        @JOverride
        def apply(self, r_):
            v_ = HANDS.get(int(r_.getIndex()))
            return None if v_ is None else JString(v_)

    @JImplements("java.util.function.Function")
    class Aim:
        @JOverride
        def apply(self, o):
            v_ = AIMS.get("spot")
            return None if v_ is None else JArray(JDouble)(v_)

    @JImplements("java.util.function.Function")
    class Near:
        @JOverride
        def apply(self, o):
            l_ = ArrayList()
            for r_ in NEARL:
                l_.add(r_)
            return l_
    MEMBERS = {}
    br.put("skill:fn:level", LevelFn())
    br.put("skill:fn:combat", CombatFn())
    br.put("skill:fn:healxp", HealXp())
    br.put("profile:fn:key", KeyFn())
    br.put("party:fn:members", Members())
    br.put("armory:fn:info", ArmInfo())
    br.put("class:fn:abilhit", C("AbilHitFn")())
    br.put("class:fn:allowed", C("AllowedFn")())
    for i_, n_ in enumerate(Defs.NAMES):
        br.put("class:weapons:" + str(n_), str(Defs.prefixesOf(i_)))

    def setclass(u_, cls):
        br.put("profile:" + str(u_), "1")
        if cls is None:
            br.remove("profile:class:" + str(u_))
            br.remove("class:" + str(u_))
        else:
            br.put("profile:class:" + str(u_), cls)
            br.put("class:" + str(u_), cls)

    def cast(name, a="1"):
        u_, r_, pr_ = PLAYERS[name][:3]
        return str(A.cast(pr_, tst, r_, world, a))

    def said():
        out_ = [str(x) for x in SAID]
        SAID.clear()
        return out_

    def unthrottle():
        AS.TOLD.clear()

    # ---------------- N1. AbilMath (pure)
    ck([int(AM.slotOf(x)) for x in ("1", " 2 ", "3", "alt1", "4", "A2", "p1", "x", "", "5")] == [0, 1, 2, 2, 3, 3, 0, -1, -1, -1],
       "N1: slotOf - 1 / 2 = primaries, 3 / alt1 and 4 / alt2 = alts, anything else refused")
    ck([int(AM.resolve(s_, c_)) for s_, c_ in ((0, False), (1, False), (0, True), (1, True), (2, True), (3, False), (4, False))] == [0, 1, 2, 3, 2, 3, -1],
       "N1: resolve - crouch held on key 1 / 2 = alt 1 / 2 (Skyy's lock); the alt keys stay alts")
    ck([int(AM.secs(x)) for x in (0, 1, 999, 1000, 1001, 13999, 14000)] == [0, 1, 1, 1, 2, 14, 14] and str(AM.readyText(13001)) == "ready in 14 s",
       "N1: whole seconds rounded up ('ready in 14 s')")
    ck(bool(AM.enough(23.0, 23.0)) and not bool(AM.enough(22.99, 23.0)) and bool(AM.enough(0.0, 0.0)), "N1: enough - exactly the cost is enough")
    ck([str(AM.fmt(x)) for x in (23.0, 2.5, 9.04, 150.0)] == ["23", "2.5", "9", "150"], "N1: fmt")
    ck([round(float(AM.heal(*a_)), 3) for a_ in ((100.0, 25, False, 20), (100.0, 25, True, 20), (80.0, 25, True, 0), (0.0, 25, True, 20))] == [25.0, 30.0, 20.0, 0.0],
       "N1: Sacred Heal 25% of max Health, the Priest 20% more = 30% (spec 2.4)")
    ck(round(float(AM.capLeft(100.0, 60, 42.0)), 3) == 18.0 and float(AM.capLeft(100.0, 60, 70.0)) == 0.0, "N1: the 60% per-cast cap")
    ck(round(float(AM.hOf(JArray(JObject)([JInt(1), JInt(1), JDouble(1.0), JInt(50), JInt(1), JDouble(100.0)]), 25.0)), 3) == 50.0
       and round(float(AM.hOf(JArray(JObject)([JInt(1), JInt(1), JDouble(1.0), JInt(88), JInt(1), JDouble(120.0)]), 25.0)), 3) == 105.6
       and float(AM.hOf(None, 25.0)) == 25.0 and float(AM.hOf(None, 0.0)) == 1.0, "N1: H = charged damage x tune % (Wood staff 50, Iron wand 88 x 120% = 105.6); unknown = the fallback")
    ck([int(AM.ticks(x)) for x in (4.0, 0.0, 0.4, 2.6, 100.0)] == [4, 0, 1, 3, 60], "N1: heal-over-time pulses = seconds (one a second)")
    ck(bool(AM.words("Kweebec_Pet_Tamed", "Merchant, pet ,Mount")) and not bool(AM.words("Trork_Warrior", "Merchant,Pet")) and not bool(AM.words(None, "Pet"))
       and not bool(AM.words("Pet", " , ")), "FIX N1: AbilMath.words - a role holding one of the comma-separated words (case-insensitive)")

    # ---------------- N2. the registry
    mage, priest, warrior = int(Defs.indexOf("Mage")), int(Defs.indexOf("Priest")), int(Defs.indexOf("Warrior"))
    ck([str(x) for x in AD.IDS] == ["Meteor", "ManaBarrier", "FrostNova", "Starfall", "ArcaneBeam", "SacredHeal", "ShieldBubble", "GuardianSpirit",
                                     "Sanctuary", "MartyrsGrace"] and [str(AD.IDS[i]) for i in range(10) if AD.BUILT[i]] == ["Meteor", "ManaBarrier", "SacredHeal", "ShieldBubble"],
       "N2 (0.1.17): the 10 Mage + Priest abilities; Meteor, Mana Barrier, Sacred Heal, Shield Bubble built")
    ck(int(AD.find("meteor")) == 0 and int(AD.find("Sacred Heal")) == 5 and int(AD.find("nope")) == -1 and int(AD.of(priest, 2)) == 7
       and bool(AD.classHas(mage)) and bool(AD.classHas(priest)) and not bool(AD.classHas(warrior)), "N2: find / of / classHas")
    own = lambda lv, g=False, pk="A": [str(AD.IDS[i]) for i in range(10) if AD.CLS[i] == mage and AD.owns(i, lv, g, pk)]
    ck(own(0) == [] and own(1) == ["Meteor"] and own(9) == ["Meteor"] and own(10) == ["Meteor", "ManaBarrier"]
       and own(20) == ["Meteor", "ManaBarrier", "FrostNova"] and own(30) == ["Meteor", "ManaBarrier", "FrostNova", "Starfall"]
       and own(30, pk="B") == ["Meteor", "ManaBarrier", "FrostNova", "ArcaneBeam"] and own(0, True) == ["Meteor", "ManaBarrier", "FrostNova", "Starfall"],
       "N2: owned by class level 1 / 10 / 20 / 30 (Skyy's lock), the A1-alt pick locks out the other, the admin grant owns all four: %s" % [own(x) for x in (0, 1, 10, 20, 30)])
    ck([str(x) for x in AD.defaults(mage, "A")] == ["Meteor", "ManaBarrier", "FrostNova", "Starfall"]
       and [str(x) for x in AD.defaults(priest, "B")] == ["SacredHeal", "ShieldBubble", "GuardianSpirit", "MartyrsGrace"],
       "N2: the default loadout = A1, A2 primaries; A2-alt, A1-alt crouch alts")
    v1 = AD.valid(JArray(JString)(["ManaBarrier", "meteor", "FrostNova", "Starfall"]), mage, "A")
    ck(v1 is not None and [str(x) for x in v1] == ["ManaBarrier", "Meteor", "FrostNova", "Starfall"]
       and AD.valid(JArray(JString)(["Meteor", "Meteor", "FrostNova", "Starfall"]), mage, "A") is None
       and AD.valid(JArray(JString)(["SacredHeal", "ManaBarrier", "FrostNova", "Starfall"]), mage, "A") is None
       and AD.valid(JArray(JString)(["Meteor", "ManaBarrier", "FrostNova", "ArcaneBeam"]), mage, "A") is None
       and AD.valid(JArray(JString)(["Meteor", None, "FrostNova", "Starfall"]), mage, "A") is None,
       "N2: a stored loadout counts only as a re-ordering of the class's 4 slots (no duplicates, no other class, no locked-out alt)")
    ck([round(float(AD.mana(i)), 3) for i in (0, 5, 1, 6, 2)] == [23.0, 18.0, 16.0, 20.0, 0.0] and [round(float(AD.stamina(i)), 3) for i in (0, 5, 1, 6)] == [2.0, 2.0, 1.0, 2.0]
       and [int(AD.cdMs(i)) for i in (0, 5, 1, 6, 2)] == [14000, 14000, 30000, 24000, 0] and int(AD.MANAB) == 1 and int(AD.BUBBLE) == 6,
       "N2: costs = spec 2.3 / 2.4 after the power split: Meteor 23 Mana + 2 Stamina / 14 s, Sacred Heal 18 + 2 / 14 s, Mana Barrier 16 + 1 / 30 s, Shield Bubble 20 + 2 / 24 s")

    # ---------------- N3. config: the default file has every ability row; a file without them reads the defaults
    txt = open(os.path.join(home, "config.properties")).read()
    ck("ab.Meteor.walk.mana=23" in txt and "ab.SacredHeal.hotTime=4" in txt and "part.abilities=true" in txt and "abil.unlock.a1alt=30" in txt
       and "abilities=on (unlock 1/10/20/30, Meteor 23+2/14s, Sacred Heal 18+2/14s, Mana Barrier 16+1/30s, Shield Bubble 20+2/24s)" in load_txt,
       "N3: a NEW config.properties carries the ability rows; load() summary: %s" % load_txt[-120:])
    ck("abil.maxLive=48" in txt and "abil.safeWords=Merchant,Trader,Shopkeeper,Vendor,NPC,Pet,Mount,Tamed,Hub" in txt and int(AC.MAX_LIVE) == 48
       and str(AC.SAFE_WORDS) == "Merchant,Trader,Shopkeeper,Vendor,NPC,Pet,Mount,Tamed,Hub",
       "FIX N3: the new rows abil.maxLive (48, the engine spec) + abil.safeWords (the SkyyArmory grapple.noYankWords default) in the file and read")
    open(os.path.join(home, "config.properties"), "w").write("\n".join(l for l in txt.split("\n") if not (l.startswith("ab.") or l.startswith("abil.") or l.startswith("part.abil")))
                                                             + "\nab.Meteor.walk.cooldown=9999\nabil.healCap=5\n")
    Cfg.load()
    ck(float(AC.M_CD) == 600.0 and int(AC.HEAL_CAP) == 10 and int(AC.MAX_LIVE) == 48 and str(AC.SAFE_WORDS).startswith("Merchant,") and float(AC.M_MANA) == 23.0 and bool(AC.PART) and int(AC.UNLOCK_A2) == 10,
       "N3: missing keys = their defaults; hand-typed values are clamped to the row bounds (cooldown 9999 -> 600, heal cap 5 -> 10)")
    open(os.path.join(home, "config.properties"), "w").write(txt)
    Cfg.load()
    ck(float(AC.M_CD) == 14.0 and int(AC.HEAL_CAP) == 60, "N3: back to the defaults")

    # ---------------- N4. THE PIPELINE - the Mage
    mu, mr, mpr, mm, mpl, mmsc = player(1, 0.5, 64.0, 0.5, "Mage1")
    setclass(mu, "Mage")
    LEVEL[(str(mu), "Sorcery")] = 1
    cu_, cr_, cpr_ = player(9, 1.5, 64.0, 0.5, "NoClass")[:3]
    setclass(cu_, None)
    wu_, wr_, wpr_ = player(8, 1.5, 64.0, 2.5, "Warrior1")[:3]
    setclass(wu_, "Warrior")
    AC.PART = False
    ck(cast("Mage1") == "off" and said() == ["Class abilities are switched off on this server."], "N4: part.abilities off -> refused")
    AC.PART = True
    unthrottle()
    ck(cast("Mage1", "x") == "usage" and cast("NoClass") == "noclass" and cast("Warrior1") == "noabil", "N4: bad slot / classless / a class without abilities yet")
    said()
    br.put("profile:busy:" + str(mu), True)
    unthrottle()
    ck(cast("Mage1") == "busy", "N4: profile still switching -> refused")
    said()
    br.remove("profile:busy:" + str(mu))
    LEVEL[(str(mu), "Sorcery")] = 0
    unthrottle()
    ck(cast("Mage1") == "locked" and said() == ["Meteor unlocks at Sorcery 1 (you are 0)."], "N4: a level-0 Mage owns nothing yet (unlock 1)")
    LEVEL[(str(mu), "Sorcery")] = 1
    unthrottle()
    r_ = cast("Mage1")
    ck(r_ == "weapon" and said() == ["Hold your Mage weapon (Staves / Spellbooks) to cast Meteor."], "N4: the REAL hand read (InventoryComponent.getItemInHand, empty) -> 'Hold your Mage weapon': %s" % r_)
    A.HAND = Hand()
    HANDS[1] = "Food_Bread"
    unthrottle()
    ck(cast("Mage1") == "weapon", "N4: food in hand -> refused")
    HANDS[1] = "Weapon_Wand_Iron"
    unthrottle()
    ck(cast("Mage1") == "weapon", "N4: another class's weapon (a Priest wand) -> refused")
    HANDS[1] = "Weapon_Staff_Wood"
    unthrottle()
    ck(cast("Mage1") == "aim" and sv(mm, MANA) == 55.0 and int(AS.left(str(mu), "Meteor", int(time.time() * 1000))) == 0,
       "N4: the REAL TargetUtil aim (no world here) finds no spot -> refused, NOTHING spent, no cooldown: %s" % said())
    A.AIM = Aim()
    AIMS["spot"] = [10.5, 64.0, 0.5]
    A.NEAR = Near()
    ck(round(float(A.hOf("Weapon_Spellbook_Wood")), 3) == 50.0 and round(float(A.hOf("Weapon_Spellbook_Grimoire_Brown")), 3) == 25.0
       and round(float(A.hOf("Weapon_Staff_Wood")), 3) == 50.0 and round(float(A.hOf("Weapon_Staff_Wizard")), 3) == 25.0,
       "FIX2 N4: H of a spellbook = its same-metal SkyyArmory staff (Weapon_Spellbook_Wood -> Weapon_Staff_Wood 50); a vanilla grimoire / staff = the fallback 25")
    n_in, n_far, n_invu, n_dead = npc(20, 11.0, 64.0, 0.5), npc(21, 30.0, 64.0, 0.5), npc(22, 10.0, 64.0, 1.5, invu=True), npc(23, 10.0, 64.0, 0.0, hp=0.0)
    other_u, other_r = player(7, 10.5, 64.0, 1.0, "Bystander")[:2]
    setclass(other_u, "Archer")
    n_pet = REFc(tst, 24)
    pet_e = U.allocateInstance(NPCc.class_)
    setf(pet_e, NPCc, "roleName", "Kweebec_Pet_Tamed")
    put(n_pet, NPCc.getComponentType(), pet_e)
    put(n_pet, ESMc.getComponentType(), stats())
    put(n_pet, TCc.getComponentType(), TCc(V3(10.0, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    ck(str(pet_e.getRoleName()) == "Kweebec_Pet_Tamed" and not bool(A.enemy(tst, n_pet, mr)) and bool(A.enemy(tst, n_in, mr)),
       "FIX N4: Abil.enemy - a live, NOT Invulnerable NPC whose role holds an abil.safeWords word (a tamed pet) is never an enemy")
    NEARL[:] = [n_in, n_invu, n_dead, n_pet, other_r, mr, n_in]
    AIMS["spot"] = [40.5, 64.0, 0.5]
    unthrottle()
    ck(cast("Mage1") == "aim", "N4: a spot further than the Meteor reach (25 blocks) -> refused")
    AIMS["spot"] = [10.5, 64.0, 0.5]
    unthrottle()
    SAID.clear()
    PSEEN.clear()
    t0 = int(time.time() * 1000)
    r_ = cast("Mage1")
    aw = AW.of("abil-test")
    ck(r_ == "ok:Meteor mana=23 stamina=2 H=50 damage=150 at=10.5,64,0.5" and sv(mm, MANA) == 32.0 and sv(mm, STAM) == 12.0,
       "N4: METEOR cast - 55 -> 32 Mana, 14 -> 12 Stamina, H = the Wood staff's 50 x 3.0 = 150: %s (Mana %s, Stamina %s)" % (r_, sv(mm, MANA), sv(mm, STAM)))
    ck(13000 <= int(AS.left(str(mu), "Meteor", t0)) <= 15000 and int(AS.total(str(mu), "Meteor")) == 14000 and int(aw.size()) == 1,
       "N4: the 14 s cooldown is armed for this profile, one impact job queued in the world list")
    ck([str(x) for x in PSEEN] == ["Fire_AoE_Spawn"] and said() == ["Meteor! -23 Mana, -2 Stamina. Ready again in 14 s."],
       "N4: the warning burst at the spot (vanilla Fire_AoE_Spawn) + the cast line")
    unthrottle()
    SOUNDS.clear()
    ck(cast("Mage1") == "cooldown" and said() == ["Meteor is ready in 14 s."], "N4: cast again at once -> 'Meteor is ready in 14 s.', nothing spent")
    ck(cast("Mage1") == "cooldown" and said() == [] and sv(mm, MANA) == 32.0, "N4: a second refusal within abil.refuse (1 s) sends no line")
    ck([str(x) for x in SOUNDS] == ["SFX_Bow_No_Ammo"], "FIX N4: the refusal plays the vanilla fail sound once (the throttled one is silent): %s" % [str(x) for x in SOUNDS])
    AC.CD_MSG = False
    unthrottle()
    SOUNDS.clear()
    said()
    r_ = cast("Mage1")
    ck(r_ == "cooldown" and said() == [] and [str(x) for x in SOUNDS] == ["SFX_Bow_No_Ammo"] and sv(mm, MANA) == 32.0,
       "FIX2 N4: row abil.cdMessage off -> the cooldown refusal sends no line, only the click: %s" % r_)
    AC.CD_MSG = True
    # the impact: AbilTick (once per world tick), after the delay; the caster swapped to FOOD meanwhile (the weapon is checked at the cast only)
    HANDS[1] = "Food_Bread"
    TBf.EVENTS.clear()
    tick = C("AbilTick")()
    tick.tick(JFloat(0.05), 0, None, tst, tbuf)
    ck(TBf.EVENTS.size() == 0 and int(aw.size()) == 1, "N5: AbilTick before the 1 s delay: nothing lands")
    time.sleep(1.05)
    aw.lastNs = 0
    PSEEN.clear()
    tick.tick(JFloat(0.05), 0, None, tst, tbuf)
    ev = [(int(e[0].getIndex()), round(float(e[1].getAmount()), 3), str(e[1].getSource().getClass().getSimpleName()), int(e[1].getSource().getRef().getIndex()))
          for e in TBf.EVENTS]
    ck(ev == [(20, 150.0, "EntitySource", 1)], "N5: METEOR impact through executeDamage: ONLY the live NPC in range (not the far / invulnerable / dead / pet NPC, "
       "not a player, not the caster, a duplicate ref once): 150 damage, source = the caster: %s" % ev)
    ck([str(x) for x in PSEEN] == ["Explosion_Medium"] and int(aw.size()) == 0 and said() == ["Meteor hit 1 enemy (150 damage each before armour)."],
       "N5: the explosion (vanilla Explosion_Medium), the job is done, the caster's hit line")
    dmg = TBf.EVENTS.get(0)[1]
    ck(bool(C("AbilDmg").mine(dmg)) and str(C("AbilHitFn")().apply(dmg)) == str(mu) and str(C("AbilDmg").whatOf(dmg)) == "Meteor"
       and C("AbilHitFn")().apply(JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")(
           JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")(mr), DCSc.PROJECTILE, JFloat(5.0))) is None,
       "N5: the damage is TAGGED; class:fn:abilhit names the caster (an untagged Damage -> null)")
    # DamageLock: a live forbidden launch of the caster (ShotTrack.liveBad = 'they are using a weapon their class may not use') cancels
    # an UNTAGGED hit from them, never the tagged ability damage
    SR = C("ShotRec")
    C("ShotTrack").SHOTS.put(UUID.randomUUID(), SR(mu, "Weapon_Shortbow_Crude", False, "Weapon_Shortbow_Crude", None))
    Dm = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    DEs = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    plain = Dm(DEs(mr), DCSc.PROJECTILE, JFloat(150.0))
    lock = C("DamageLock")()
    lock.handle(0, None, tst, tbuf, plain)
    lock.handle(0, None, tst, tbuf, dmg)
    ck(bool(plain.isCancelled()) and float(plain.getAmount()) == 0.0 and not bool(dmg.isCancelled()) and float(dmg.getAmount()) == 150.0,
       "N5: the REAL DamageLock cancels an untagged hit of the caster (control) but lets the TAGGED Meteor damage through (plan 4.2 finding)")
    C("ShotTrack").SHOTS.clear()
    said()
    # Mana / Stamina refusals, creative = free
    AS.clearCd(str(mu))
    mm.setStatValue(MANA, JFloat(9.0))
    unthrottle()
    HANDS[1] = "Weapon_Staff_Wood"
    ck(cast("Mage1") == "mana" and said() == ["Not enough Mana for Meteor: 9 / 23."] and sv(mm, MANA) == 9.0 and int(AS.left(str(mu), "Meteor", int(time.time() * 1000))) == 0,
       "N6: not enough Mana -> 'Not enough Mana for Meteor: 9 / 23.', nothing spent, no cooldown")
    mm.setStatValue(MANA, JFloat(55.0))
    mm.setStatValue(STAM, JFloat(1.0))
    unthrottle()
    ck(cast("Mage1") == "stamina" and said() == ["Not enough Stamina for Meteor: 1 / 2."] and sv(mm, MANA) == 55.0, "N6: not enough Stamina -> refused, no Mana taken")
    mm.setStatValue(STAM, JFloat(14.0))
    TSt.COMP.get(mr).remove(ESMc.getComponentType())   # no stat map (a profile still loading): Mana / Stamina unreadable
    unthrottle()
    n0_ = int(aw.size())
    r_ = cast("Mage1")
    TSt.COMP.get(mr).put(ESMc.getComponentType(), mm)
    ck(r_ == "nostats" and said() == ["Your Mana and Stamina are not ready yet - try again in a moment (nothing was spent)."]
       and int(AS.left(str(mu), "Meteor", int(time.time() * 1000))) == 0 and int(aw.size()) == n0_,
       "FIX2 N6: Mana / Stamina unreadable -> refused (never a free cast), no cooldown, nothing queued: %s" % r_)
    unthrottle()
    r1_ = cast("Mage1")
    said()
    AS.clearCd(str(mu))
    r2_ = cast("Mage1")
    said()
    ck(r1_.startswith("ok:Meteor mana=23") and r2_.startswith("ok:Meteor mana=23") and sv(mm, MANA) == 9.0,
       "N6: TWO Meteors from a full level-1 pool (55 -> 32 -> 9 Mana, Skyy's 'main ability at least 2 casts')")
    AS.clearCd(str(mu))
    setf(mpl, PLAc, "gameMode", GM.Creative)
    r_ = cast("Mage1")
    said()
    ck(r_.startswith("ok:Meteor mana=0 stamina=0") and sv(mm, MANA) == 9.0, "N6: creative + abil.creativeFree -> cast for free: %s" % r_)
    setf(mpl, PLAc, "gameMode", GM.Adventure)
    for a_ in list(aw.due(int(time.time() * 1000) + 100000)):
        pass
    # crouch = alt; owned / built / passive refusals
    mm.setStatValue(MANA, JFloat(200.0))
    AS.clearCd(str(mu))
    LEVEL[(str(mu), "Sorcery")] = 10
    mmsc.getMovementStates().crouching = True
    unthrottle()
    ck(cast("Mage1") == "locked" and said() == ["No alt yet - Frost Nova unlocks at Sorcery 20 (you are 10)."],
       "N7: CROUCH + /cast 1 at Sorcery 10 = the alt on that key (Frost Nova) -> 'No alt yet'")
    LEVEL[(str(mu), "Sorcery")] = 30
    unthrottle()
    ck(cast("Mage1") == "soon" and said() == ["Frost Nova comes in a later update - nothing was spent."] and sv(mm, MANA) == 200.0,
       "N7: crouch + /cast 1 at 30 -> Frost Nova (not built in R1), nothing spent")
    unthrottle()
    ck(cast("Mage1", "2") == "soon" and said() == ["Starfall comes in a later update - nothing was spent."], "N7: crouch + /cast 2 = alt 2 = Starfall")
    mmsc.getMovementStates().crouching = False
    unthrottle()
    r7_ = cast("Mage1", "2")
    s7_ = said()
    ck(r7_.startswith("ok:ManaBarrier mana=16 stamina=1 at=0.5,64,0.5 r=4") and s7_[0] == "Mana Barrier! -16 Mana, -1 Stamina. Ready again in 30 s." and sv(mm, MANA) == 184.0,
       "N7 (0.1.17): /cast 2 standing = primary 2 = Mana Barrier - BUILT now: the aim is 10 blocks off, so (FIX ROUND) the dome goes at her feet (16 Mana + 1 Stamina, 30 s): %s %s" % (r7_, s7_))
    unthrottle()
    ck(cast("Mage1", "4") == "soon" and cast("Mage1", "3") == "soon", "N7: /cast 3 / 4 = the alts directly")
    said()
    r_ = cast("Mage1", "1")
    ck(r_.startswith("ok:Meteor") and " crouch" not in r_, "N7: /cast 1 standing = Meteor")
    rc_ = None
    AS.clearCd(str(mu))
    mmsc.getMovementStates().crouching = True
    said()
    ck(cast("Mage1", "3").startswith("soon"), "N7: /cast 3 is the alt with or without crouch")
    mmsc.getMovementStates().crouching = False
    said()
    # loadout swap (out of combat), the file, a profile switch
    COMBAT[str(mu)] = 4000
    ck(str(A.swap(mpr)) == "combat" and said() == ["Leave combat first - abilities are swapped only out of combat."], "N8: swap in combat -> refused")
    COMBAT[str(mu)] = 0
    ck(str(A.swap(mpr)) == "ok" and said() == ["Swapped: /cast 1 = Mana Barrier, /cast 2 = Meteor."], "N8: /cast swap out of combat")
    f1 = os.path.join(home, "abilities", str(mu) + ".properties")
    p1 = dict(l.split("=", 1) for l in open(f1).read().splitlines() if l and not l.startswith("#"))
    ck(p1 == {"p1": "ManaBarrier", "p2": "Meteor", "a1": "FrostNova", "a2": "Starfall"}, "N8: abilities/<pkey>.properties written atomically: %s" % p1)
    AS.clearCd(str(mu))
    unthrottle()
    ck(cast("Mage1", "1").startswith("ok:ManaBarrier") and cast("Mage1", "2").startswith("ok:Meteor"), "N8: after the swap /cast 1 casts Mana Barrier, /cast 2 Meteor")
    said()
    PROFKEY[str(mu)] = str(mu) + "-p2"
    unthrottle()
    r_ = cast("Mage1", "1")
    ck(r_.startswith("ok:Meteor"), "N8: PROFILE 2 has its own loadout (the defaults: /cast 1 = Meteor) and its own cooldowns: %s" % r_)
    said()
    del PROFKEY[str(mu)]
    unthrottle()
    ck(cast("Mage1", "2") == "cooldown" and cast("Mage1", "1") == "cooldown", "N8: back on profile 1: its swapped loadout and its running cooldowns are still there")
    said()
    AS.DATA.clear()
    ck([str(x) for x in AS.slots(str(mu), mage)] == ["ManaBarrier", "Meteor", "FrostNova", "Starfall"], "N8: the loadout reads back from the file (a server restart)")
    A.swap(mpr)
    said()
    # relog keeps cooldowns (ClassQuit only drops the refusal throttle)
    PDE = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent")
    pde = U.allocateInstance(PDE.class_)
    fn_ = gfield("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent", "getPlayerRef")
    k_ = PDE.class_
    while True:
        try:
            f_ = k_.getDeclaredField(fn_)
            break
        except Exception:
            k_ = k_.getSuperclass()
    f_.setAccessible(True)
    f_.set(pde, mpr)
    AS.TOLD.put(mu, JLong(int(time.time() * 1000)))
    left0 = int(AS.left(str(mu), "Meteor", int(time.time() * 1000)))
    C("ClassQuit")().accept(pde)
    ck(not AS.TOLD.containsKey(mu) and left0 > 0 and int(AS.left(str(mu), "Meteor", int(time.time() * 1000))) > 0,
       "N8: a disconnect (the REAL ClassQuit) keeps the cooldown (a relog does not reset it), drops the refusal throttle")
    # admin: no permission module = denied; grant / reset / info / ungrant
    au, ar_, apr = player(3, 50.0, 64.0, 50.0, "Admin")[:3]
    ck(str(A.admin(apr, "Mage1", "grant")) == "denied", "N9: /classadmin abil without skyyclasses.admin -> denied")
    said()
    LEVEL[(str(mu), "Sorcery")] = 1
    said()
    ck(str(A.swap(mpr)) == "locked" and said() == ["Both primaries must be unlocked to swap - Mana Barrier unlocks at Sorcery 10 (you are 1)."]
       and [str(x) for x in AS.slots(str(mu), mage)][:2] == ["Meteor", "ManaBarrier"],
       "FIX2 N8: /cast swap at Sorcery 1 (Mana Barrier locked) -> refused, the loadout unchanged")
    ck(str(A.adminDo(apr, "Mage1", "grant")) == "grant" and bool(AS.granted(str(mu))), "N9: grant -> all four owned (testing)")
    ck("grant=true" in open(f1).read(), "N9: the grant is saved in the profile's ability file")
    unthrottle()
    r9_ = cast("Mage1", "2")
    ck(r9_ == "cooldown" or r9_.startswith("ok:ManaBarrier"), "N9: a Sorcery 1 Mage with the grant owns Mana Barrier (not locked): %s" % r9_)
    said()
    ck(str(A.adminDo(apr, "Mage1", "reset")) == "reset" and int(AS.left(str(mu), "Meteor", int(time.time() * 1000))) == 0, "N9: reset clears the cooldowns")
    said()
    ck(str(A.adminDo(apr, "Mage1", "info")) == "info" and any("Abilities - Mage, Sorcery 1 (admin grant: all four):" in x for x in said()), "N9: info lists the abilities")
    ck(str(A.adminDo(apr, "Mage1", "ungrant")) == "ungrant" and not bool(AS.granted(str(mu))) and "grant=" not in open(f1).read(), "N9: ungrant")
    said()
    ck(str(A.adminDo(apr, "nobody-here", "grant")) == "who" and str(A.adminDo(apr, "Mage1", "explode")) == "usage", "N9: unknown player / action")
    said()
    # the HUD bridge + the list
    AS.arm(str(mu), "Meteor", int(time.time() * 1000), 14000)
    hud = C("AbilFn")().apply(mu)
    hv = [str(x) if i % 4 in (0, 3) else int(x) for i, x in enumerate(list(hud)[:16])]
    ck(len(hud) == 44 and hv[0] == "Meteor" and 13000 <= hv[1] <= 14000 and hv[2] == 14000 and hv[3] == "cooldown" and hv[4:8] == ["Mana Barrier", 0, 0, "locked"]
       and hv[11] == "locked" and hv[15] == "locked", "N10: class:fn:abil [0-15] = 4 x {name, ms left, ms total, state} as in 0.1.16 (now 44 long): %s" % hv)
    ck(C("AbilFn")().apply(cu_) is None and C("AbilFn")().apply(JString("x")) is None, "N10: class:fn:abil -> null without a class with abilities / a bad argument")
    ll = [str(x) for x in A.listLines(mu)]
    ck(len(ll) == 6 and ll[0] == "Abilities - Mage, Sorcery 1:" and ll[1].startswith("  /cast 1: Meteor - ready in ")
       and ll[2] == "  /cast 2: Mana Barrier - unlocks at Sorcery 10" and ll[3] == "  crouch + /cast 1 (or /cast 3): Frost Nova - unlocks at Sorcery 20",
       "N10: /cast list: %s" % ll)
    AS.clearCd(str(mu))
    ll = [str(x) for x in A.listLines(mu)]
    ck(ll[1] == "  /cast 1: Meteor - ready (23 Mana + 2 Stamina, cooldown 14 s)", "N10: list when ready: %s" % ll[1])
    # the world cap: a full list refuses (never silently drops a paid cast)
    aw.due(int(time.time() * 1000) + 100000)   # the earlier casts' impacts (never ticked) leave the list first
    for z_ in list(aw.zoneArr()):                # 0.1.17: and the Mana Barriers of N7 / N8 (zones count toward the cap - section Z)
        aw.dropZone(z_)
    for i_ in range(47):
        aw.add(AJ(1, int(time.time() * 1000) + 600000, mu, "x", 0.0, 0.0, 0.0, 1.0, 0.0))
    full47 = bool(aw.full())
    aw.add(AJ(1, int(time.time() * 1000) + 600000, mu, "x", 0.0, 0.0, 0.0, 1.0, 0.0))
    mm.setStatValue(MANA, JFloat(55.0))
    unthrottle()
    ck(not full47 and cast("Mage1") == "full" and sv(mm, MANA) == 55.0 and int(AS.left(str(mu), "Meteor", int(time.time() * 1000))) == 0,
       "N11 (FIX): abil.maxLive 48 live jobs in the world -> refused, nothing spent (47 = not full)")
    AC.MAX_LIVE = 256
    ck(not bool(aw.full()), "FIX N11: the cap follows the Server Setup row live (256 -> not full)")
    AC.MAX_LIVE = 48
    aw.due(int(time.time() * 1000) + 700000)
    said()
    # FIX2: a job more than 30 s past its time (a world that emptied right after the cast) is dropped unrun; a late but recent one still runs
    now_ = int(time.time() * 1000)
    aw.add(AJ(1, now_ - 31000, mu, "Meteor", 10.5, 64.0, 0.5, 4.0, 10.0))
    full_ = bool(aw.full())
    left_ = int(aw.size())
    aw.add(AJ(1, now_ - 31000, mu, "Meteor", 10.5, 64.0, 0.5, 4.0, 10.0))
    aw.add(AJ(1, now_ - 5000, mu, "Meteor", 10.5, 64.0, 0.5, 4.0, 10.0))
    aw.lastNs = 0
    TBf.EVENTS.clear()
    tick.tick(JFloat(0.05), 0, None, tst, tbuf)
    ck(not full_ and left_ == 0 and TBf.EVENTS.size() == 1 and int(aw.size()) == 0,
       "FIX2 N11: a stale job (31 s late) is pruned by full() and dropped unrun by the tick; a 5 s late one still lands (%d events)" % TBf.EVENTS.size())
    said()
    # the caster leaves the world before the impact: it lands (particles), nobody is hurt
    r_ = cast("Mage1")
    ebu.remove(mu)
    time.sleep(1.05)
    aw.lastNs = 0
    TBf.EVENTS.clear()
    tick.tick(JFloat(0.05), 0, None, tst, tbuf)
    ck(r_.startswith("ok:Meteor") and TBf.EVENTS.size() == 0 and int(aw.size()) == 0, "N11: the caster gone from the world at the impact -> no damage, job done")
    ebu.put(mu, mr)
    said()
    # FIX: a profile switch between the cast and the impact -> the meteor lands, nobody is hurt (no kill XP for the new profile's class)
    AS.clearCd(str(mu))
    mm.setStatValue(MANA, JFloat(55.0))
    mm.setStatValue(STAM, JFloat(14.0))
    r_ = cast("Mage1")
    job_ = [j for j in list(aw.jobs)][0]
    pk_ok = str(job_.pkey) == str(mu)
    PROFKEY[str(mu)] = str(mu) + "-p2"
    job_.at = int(time.time() * 1000)   # due now (0 would be a stale job - FIX2)
    aw.lastNs = 0
    TBf.EVENTS.clear()
    tick.tick(JFloat(0.05), 0, None, tst, tbuf)
    ck(r_.startswith("ok:Meteor") and pk_ok and TBf.EVENTS.size() == 0 and int(aw.size()) == 0,
       "FIX N11: the job carries the caster's profile; switched profile before the impact -> no damage, job done: %s" % r_)
    del PROFKEY[str(mu)]
    # control: the same profile at the impact still hits
    AS.clearCd(str(mu))
    r_ = cast("Mage1")
    job_ = [j for j in list(aw.jobs)][0]
    job_.at = int(time.time() * 1000)   # due now (0 would be a stale job - FIX2)
    aw.lastNs = 0
    TBf.EVENTS.clear()
    tick.tick(JFloat(0.05), 0, None, tst, tbuf)
    ck(TBf.EVENTS.size() == 1, "FIX N11: control - the same profile at the impact hits (%d events)" % TBf.EVENTS.size())
    said()
    # FIX: an executor that throws after the payment -> Mana, Stamina and the cooldown are given back, nothing queued
    AS.clearCd(str(mu))
    mm.setStatValue(MANA, JFloat(55.0))
    mm.setStatValue(STAM, JFloat(14.0))
    A.PSEEN = JClass("java.util.Collections").emptyList()   # the warning particle's seam list refuses add -> meteorCast throws
    w0 = int(Cfg.FAILS)
    r_ = cast("Mage1")
    A.PSEEN = PSEEN
    sd_ = said()
    ck(r_ == "failed" and sv(mm, MANA) == 55.0 and sv(mm, STAM) == 14.0 and int(AS.left(str(mu), "Meteor", int(time.time() * 1000))) == 0
       and int(aw.size()) == 0 and sd_[-1] == "Meteor could not be cast - your Mana, Stamina and cooldown were given back (the server log has the details).",
       "FIX N11: a failing executor refunds Mana + Stamina, clears the cooldown, queues no impact: %s %s Mana %s" % (r_, sd_, sv(mm, MANA)))

    # ---------------- N12. SACRED HEAL - the Priest, a party member, a stranger, a far player
    pu, pr_r, ppr, pm = player(4, 100.5, 64.0, 100.5, "Priest1", hp=50.0, mana=47.0, stam=15.0)[:4]
    qu, qr, qpr, qm = player(5, 104.5, 64.0, 100.5, "Friend", hp=40.0)[:4]
    su, sr, spr, sm = player(6, 100.5, 64.0, 106.5, "Stranger", hp=90.0)[:4]
    fu, fr, fpr, fm = player(10, 120.5, 64.0, 100.5, "Far", hp=50.0)[:4]
    setclass(pu, "Priest")
    for x_ in (qu, su, fu):
        setclass(x_, "Archer")
    LEVEL[(str(pu), "Divinity")] = 1
    MEMBERS[str(pu)] = [str(qu)]
    HANDS[4] = "Weapon_Wand_Wood"
    # FIX: nobody in range needs healing -> refused, nothing spent, no cooldown (everyone full; the far player does not count)
    hp0 = [sv(x, HP) for x in (pm, qm, sm)]
    for x_ in (pm, qm, sm):
        x_.setStatValue(HP, JFloat(100.0))
    unthrottle()
    said()
    r_ = cast("Priest1")
    ck(r_ == "noneed" and said() == ["Nobody within 9 blocks needs healing - nothing was spent."] and sv(pm, MANA) == 47.0
       and int(AS.left(str(pu), "SacredHeal", int(time.time() * 1000))) == 0 and int(aw.size()) == 0,
       "FIX N12: Sacred Heal with nobody hurt in range (the hurt far player does not count) -> refused, nothing spent: %s" % r_)
    for x_, h_ in zip((pm, qm, sm), hp0):
        x_.setStatValue(HP, JFloat(h_))
    HEALXP.clear()
    PSEEN.clear()
    C("HealMsg").GIVEN.clear()
    unthrottle()
    r_ = cast("Priest1")
    ck(r_ == "ok:SacredHeal mana=18 stamina=2 targets=3 healed=3 hp=65" and sv(pm, MANA) == 29.0 and sv(pm, STAM) == 13.0,
       "N12: SACRED HEAL cast - 18 Mana + 2 Stamina, 3 players in 9 blocks healed (the far one not): %s" % r_)
    ck([sv(pm, HP), sv(qm, HP), sv(sm, HP), sv(fm, HP)] == [80.0, 65.0, 100.0, 50.0],
       "N12: the Priest +30 (25%% x 1.2), the party member +25, the stranger +12.5 x othersPercent 50%% -> +10 (Health full), far = nothing: %s"
       % [sv(pm, HP), sv(qm, HP), sv(sm, HP), sv(fm, HP)])
    ck(sorted(HEALXP) == sorted([[str(pu), 35.0, "classes:heal", False], [str(pu), 30.0, "classes:heal:self", True]]),
       "N12: Divinity XP: 35 HP on others, 30 on self (the self rate flag): %s" % HEALXP)
    ck([str(x) for x in PSEEN] == ["Magic_Hit"] * 3 and said() == ["Sacred Heal! -18 Mana, -2 Stamina. Ready again in 14 s.", "Sacred Heal: +65 HP to 3 players, healing over 4 s."]
       and C("HealMsg").GIVEN.containsKey(pu), "N12: a holy flash on each healed player (vanilla Magic_Hit), the lines, the heal chat totals")
    job = [j for j in list(aw.jobs)][0]
    ck(int(job.kind) == 2 and int(job.left) == 4 and int(job.every) == 1000 and float(job.per[0]) == 3.0 and sorted(round(float(x), 3) for x in job.per) == [1.25, 2.5, 3.0],
       "N12: the heal over time = 40%% of each instant heal over 4 s (4 pulses: 3.0 / 2.5 / 1.25): %s" % [int(job.kind), int(job.left), int(job.every), [float(x) for x in job.per], int(aw.size())])
    HEALXP.clear()
    for k_ in range(4):
        job.at = int(time.time() * 1000)
        aw.lastNs = 0
        tick.tick(JFloat(0.05), 0, None, tst, tbuf)
    ck([sv(pm, HP), sv(qm, HP), sv(sm, HP)] == [92.0, 75.0, 100.0] and int(aw.size()) == 0,
       "N12: 4 pulses -> the Priest 92, the party member 75, the stranger stays full; the job ends: %s" % [sv(pm, HP), sv(qm, HP), sv(sm, HP)])
    ck(round(sum(x[1] for x in HEALXP if x[2] == "classes:heal"), 3) == 10.0 and round(sum(x[1] for x in HEALXP if x[2] == "classes:heal:self"), 3) == 12.0,
       "N12: the pulses pay Divinity XP too (10 others, 12 self): %s" % HEALXP)
    # FIX: the Priest switches profile during the heal over time -> the pulses still heal, but pay no XP
    AS.clearCd(str(pu))
    pm.setStatValue(HP, JFloat(50.0))
    qm.setStatValue(HP, JFloat(40.0))
    pm.setStatValue(MANA, JFloat(47.0))
    cast("Priest1")
    said()
    job = [j for j in list(aw.jobs)][0]
    PROFKEY[str(pu)] = str(pu) + "-p2"
    HEALXP.clear()
    hb_ = sv(qm, HP)
    for k_ in range(4):
        job.at = int(time.time() * 1000)
        aw.lastNs = 0
        tick.tick(JFloat(0.05), 0, None, tst, tbuf)
    ck(str(job.pkey) == str(pu) and HEALXP == [] and sv(qm, HP) > hb_ and int(aw.size()) == 0,
       "FIX N12: a profile switch during the heal over time -> still heals (%s -> %s), no Divinity XP to the new profile: %s" % (hb_, sv(qm, HP), HEALXP))
    del PROFKEY[str(pu)]
    # the cap: 80% heal, no self bonus, cap 60% -> a player at 1 HP gets 60, the heal over time adds nothing more
    AC.S_HEAL, AC.S_SELF = 80, 0
    AS.clearCd(str(pu))
    pm.setStatValue(HP, JFloat(1.0))
    qm.setStatValue(HP, JFloat(100.0))
    pm.setStatValue(MANA, JFloat(47.0))
    said()
    r_ = cast("Priest1")
    job = [j for j in list(aw.jobs)][0]
    for k_ in range(4):
        job.at = int(time.time() * 1000)
        aw.lastNs = 0
        tick.tick(JFloat(0.05), 0, None, tst, tbuf)
    ck(sv(pm, HP) == 61.0, "N12: abil.healCap 60%% of max Health per target per cast (instant + heal over time): %s" % sv(pm, HP))
    AC.S_HEAL, AC.S_SELF = 25, 20
    # creative Priest: free, heals, no XP
    AS.clearCd(str(pu))
    setf(PLAYERS["Priest1"][4], PLAc, "gameMode", GM.Creative)
    HEALXP.clear()
    qm.setStatValue(HP, JFloat(50.0))
    said()
    r_ = cast("Priest1")
    ck(r_.startswith("ok:SacredHeal mana=0") and HEALXP == [] and sv(qm, HP) == 75.0, "N12: a creative Priest casts free and earns no XP (the Priest itself is not healed in creative): %s" % r_)
    setf(PLAYERS["Priest1"][4], PLAc, "gameMode", GM.Adventure)
    aw.due(int(time.time() * 1000) + 900000)
    said()
    # FIX2: an error AFTER the first heal (commit phase) -> no refund (the heal landed), no XP, no heal over time; the cast ends there
    AS.clearCd(str(pu))
    pm.setStatValue(HP, JFloat(50.0))
    qm.setStatValue(HP, JFloat(40.0))
    pm.setStatValue(MANA, JFloat(47.0))
    HEALXP.clear()
    A.PSEEN = JClass("java.util.Collections").emptyList()   # the first heal flash throws
    unthrottle()
    r_ = cast("Priest1")
    A.PSEEN = PSEEN
    ck(r_.startswith("ok:SacredHeal mana=18") and " partial" in r_ and sv(pm, MANA) == 29.0 and sv(pm, HP) == 80.0 and sv(qm, HP) == 40.0
       and HEALXP == [] and int(aw.size()) == 0 and int(AS.left(str(pu), "SacredHeal", int(time.time() * 1000))) > 0,
       "FIX2 N12: Sacred Heal failing after the first heal keeps the payment + cooldown, pays NO XP, queues no heal over time: %s (HP %s / %s)"
       % (r_, sv(pm, HP), sv(qm, HP)))
    said()

    # ---------------- N13. the ability file: unreadable = never written; the real save path
    bad = os.path.join(home, "abilities", "badkey.properties")
    os.makedirs(bad)
    ck(not bool(AS.set("badkey", JArray(JString)(["p1"]), JArray(JString)(["Meteor"]))) and os.path.isdir(bad), "N13: an unreadable ability file is never written")
    AS.SYNC = False
    s0 = int(AS.SAVES)
    AS.set("savekey", JArray(JString)(["grant"]), JArray(JString)(["true"]))
    AS.saveSoon("savekey")
    time.sleep(0.5)
    ck(int(AS.SAVES) == s0 + 1 and os.path.isfile(os.path.join(home, "abilities", "savekey.properties")), "N13: saveSoon writes on the scheduler (HytaleServer.SCHEDULED_EXECUTOR)")
    # FIX: monitors - load (the world thread) takes no lock on a cache hit; the write + its retry sleep hold only the AbilSave monitor
    Mod = JClass("java.lang.reflect.Modifier")
    Str = JClass("java.lang.String").class_
    sync = lambda c_, n_: bool(Mod.isSynchronized(c_.class_.getMethod(n_, Str).getModifiers()))
    ck(not sync(AS, "load") and sync(AS, "loadMiss") and not sync(AS, "save") and sync(C("AbilSave"), "write") and not sync(AS, "granted"),
       "FIX N13: load / save are not synchronized; loadMiss (AbilStore) and write (AbilSave) are")
    import threading
    held, release = threading.Event(), threading.Event()

    def hold():
        with jpype.synchronized(C("AbilSave").class_):
            held.set()
            release.wait(5)
    th = threading.Thread(target=hold)
    th.start()
    held.wait(5)
    t1 = time.time()
    g_ = bool(AS.granted("savekey"))
    sl_ = [str(x) for x in AS.slots(str(mu), mage)]
    AS.set("savekey", JArray(JString)(["alt"]), JArray(JString)(["A"]))
    dt_ = time.time() - t1
    release.set()
    th.join()
    ck(g_ and len(sl_) == 4 and dt_ < 0.5, "FIX N13: while a write holds the AbilSave monitor, the world-thread reads + a set do not wait (%.3f s)" % dt_)
    # FIX: a failed write stays DIRTY, is retried 5 s later, and the shutdown flush writes what is left
    goodDir = AS.DIR
    blocker = os.path.join(home, "blocker")
    open(blocker, "w").write("x")
    AS.DIR = Paths.get(os.path.join(blocker, "sub"))              # a FILE as the parent folder -> createDirectories fails
    AS.set("flushkey", JArray(JString)(["grant"]), JArray(JString)(["true"]))
    AS.saveSoon("flushkey")
    time.sleep(0.5)
    ck(bool(AS.DIRTY.containsKey("flushkey")), "FIX N13: a failed write leaves the key DIRTY (memory and disk differ, so it is kept for a retry)")
    AS.DIR = goodDir
    time.sleep(5.6)
    ck(not bool(AS.DIRTY.containsKey("flushkey")) and os.path.isfile(os.path.join(home, "abilities", "flushkey.properties")),
       "FIX N13: the failed write is retried 5 s later on the scheduler and lands")
    AS.SYNC = True
    AS.DIR = Paths.get(os.path.join(blocker, "sub"))
    AS.set("flushkey2", JArray(JString)(["grant"]), JArray(JString)(["true"]))
    AS.saveSoon("flushkey2")
    AS.DIR = goodDir
    ck(bool(AS.DIRTY.containsKey("flushkey2")) and int(AS.flush()) == 1 and not bool(AS.DIRTY.containsKey("flushkey2"))
       and "grant=true" in open(os.path.join(home, "abilities", "flushkey2.properties")).read(),
       "FIX N13: AbilStore.flush (the plugin's shutdown) writes every DIRTY key")
    ck(int(AS.flush()) == 0, "FIX N13: nothing dirty -> flush writes nothing")

    # ================================================================================== Z. ZONES (round R3) - Mana Barrier + Shield Bubble
    try:
        now_ms = lambda: int(time.time() * 1000)
        aw.due(now_ms() + 9000000)
        for z_ in list(aw.zoneArr()):
            aw.dropZone(z_)
        AZ = C("AbilZone")
        ShS, ShU = C("AbilShieldSys"), C("AbilShieldSysU")
        ORDc = JClass("com.hypixel.hytale.component.dependency.Order")
        ADRn = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction"
        TCh = stub("TChunk", CP_ + "ArchetypeChunk", ["public static java.util.HashMap REFS = new java.util.HashMap();"],
                   ["public " + CP_ + "Ref getReferenceTo(int i) { return (" + CP_ + "Ref) REFS.get(Integer.valueOf(i)); }"])
        chunk = U.allocateInstance(TCh.class_)
        # the engine sets DamageCause.OUT_OF_WORLD / COMMAND / ... at asset load; here: a DamageCause store with those causes (the stat store way)
        DCS_OK = False
        causes = {}
        try:
            if AR.getAssetStore(DCSc.class_) is None:
                AR.register(HAS.builder(DCSc.class_, ILT(ArrOf(DCSc))).setPath("Entity/Damage").setCodec(DCSc.CODEC).setKeyFunction(GetId())
                            .setReplaceOnRemove(NoRep()).build())
            dl = ArrayList()
            for key in ("OutOfWorld", "Command", "Physical", "Fall", "Projectile"):
                o = AR.getAssetStore(DCSc.class_).getCodec().decodeJsonAsset(RJR.fromJsonString("{}"), AEI(Paths.get(key + ".json"), ADT(DCSc.class_, key, None)))
                causes[key] = o
                dl.add(o)
            AR.getAssetStore(DCSc.class_).loadAssets("Hytale:Hytale", dl)
            jfield(DCSc, "OUT_OF_WORLD").set(None, causes["OutOfWorld"])
            jfield(DCSc, "COMMAND").set(None, causes["Command"])
            DCS_OK = Dm(DEs(mr), causes["OutOfWorld"], JFloat(1.0)).getCause() == causes["OutOfWorld"]
        except Exception as e:
            R["notes"].append("DamageCause store: %s" % str(e)[:300])
        ck(DCS_OK, "Z0: a DamageCause store with the vanilla cause ids: Damage.getCause() gives the OUT_OF_WORLD object back (the hook's exclusion can be tested)")

        def mv(r_, x, y, z):
            put(r_, TCc.getComponentType(), TCc(V3(x, y, z), R3(0.0, 0.0, 0.0)))

        def hit(r_, amount, src=None, cause=None):
            d_ = Dm(DEs(n_in) if src is None else src, DCSc.PROJECTILE if cause is None else cause, JFloat(amount))
            TCh.REFS.put(JInt(0), r_)
            sys_.handle(0, chunk, tst, tbuf, d_)
            return d_

        def ztick():
            aw.lastNs = 0
            aw.nextZone = 0
            tick.tick(JFloat(0.05), 0, None, tst, tbuf)

        sys_ = ShS(True)
        deps_ = list(sys_.getDependencies())
        DSn = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$"
        ck(len(deps_) == 4 and all(x.getOrder() == ORDc.AFTER for x in deps_)
           and [str(x.getSystemClass().getName()) for x in deps_] == [ADRn, DSn + "FilterUnkillable", DSn + "FilterPlayerWorldConfig", DSn + "PlayerDamageFilterSystem"],
           "FIX Z0: AbilShieldSys runs AFTER ArmorDamageReduction AND the engine filters that drop hits (FilterUnkillable, FilterPlayerWorldConfig, "
           "PlayerDamageFilterSystem): %s" % [str(x.getSystemClass().getSimpleName()) for x in deps_])
        ck(len(deps_) >= 1 and deps_[0].getOrder() == ORDc.AFTER and str(deps_[0].getSystemClass().getName()) == ADRn
           and ShU().getDependencies().isEmpty() and sys_.getQuery() == PLAc.getComponentType() and ShU().getQuery() == PLAc.getComponentType()
           and ShS.class_.isAssignableFrom(ShU.class_),
           "Z0: AbilShieldSys = players only, SystemDependency(AFTER, DamageSystems$ArmorDamageReduction); the fallback AbilShieldSysU has no order")
        # ---- Z1: MANA BARRIER cast (Sorcery 10 = owned at unlock, the plan 4.4 pool 145 Mana / 14.5 Stamina)
        zu, zr, zpr, zm, zpl, zmsc = player(30, 500.5, 64.0, 500.5, "MageZ", mana=145.0, stam=14.5)
        setclass(zu, "Mage")
        LEVEL[(str(zu), "Sorcery")] = 10
        HANDS[30] = "Weapon_Staff_Wood"
        AIMS["spot"] = [503.5, 64.0, 500.5]   # FIX ROUND: 3 blocks off (inside radius 4 - 0.5); 5 blocks puts the dome at her feet (FIX Z2)
        unthrottle()
        said()
        PSEEN.clear()
        r_ = cast("MageZ", "2")
        sd_ = said()
        zs_ = list(aw.zoneArr())
        ck(r_ == "ok:ManaBarrier mana=16 stamina=1 at=503.5,64,500.5 r=4 cap=100" and sv(zm, MANA) == 129.0 and sv(zm, STAM) == 13.5
           and int(AS.total(str(zu), "ManaBarrier")) == 30000 and len(zs_) == 1,
           "Z1: MANA BARRIER at Sorcery 10 (owned at unlock, affordable: 145 Mana) - at the aimed spot, 16 Mana + 1 Stamina, 30 s cooldown, one zone: %s %s/%s" % (r_, sv(zm, MANA), sv(zm, STAM)))
        bz = zs_[0] if zs_ else None
        ck(bz is not None and int(bz.kind) == 1 and int(bz.until) - int(bz.start) == 12000 and float(bz.cap) == 100.0 and float(bz.ratio) == 2.0
           and float(bz.r) == 4.0 and str(bz.pkey) == str(zu),
           "Z1: the dome = 4 blocks, 12 s, 2 HP per Mana, soaks at most 100 % of max Health (100), keeps the caster's profile")
        ck([str(x) for x in PSEEN] == ["Rings_Rings"] * 23 and int(AM.ringPoints(4.0)) == 13 and int(AM.ringPoints(2.8)) == 9
           and sd_ == ["Mana Barrier! -16 Mana, -1 Stamina. Ready again in 30 s.",
                       "Mana Barrier: a dome of 4 blocks for 12 s - damage to you inside costs Mana (2 per Mana) instead of Health."],
           "FIX Z1: the see-through DOME = 13 small vanilla Rings_Rings bursts on the edge + 9 on an upper ring + 1 on top, and the two lines: %s %s" % ([str(x) for x in PSEEN][:2], sd_))
        unthrottle()
        ck(cast("MageZ", "2") == "cooldown" and sv(zm, MANA) == 129.0 and len(list(aw.zoneArr())) == 1, "Z1: cast again -> cooldown, nothing spent, no second dome")
        said()
        # ---- Z2: the spot
        AIMS["spot"] = [503.5, 64.0, 500.5]
        a1 = [round(float(x), 3) for x in A.spot(tst, zr, 8.0)]
        a0 = [round(float(x), 3) for x in A.spot(tst, zr, 0.0)]
        AIMS["spot"] = None
        af = [round(float(x), 3) for x in A.spot(tst, zr, 8.0)]
        AIMS["spot"] = [520.5, 64.0, 500.5]
        ar = [round(float(x), 3) for x in A.spot(tst, zr, 8.0)]
        ck(a1 == [503.5, 64.0, 500.5] and a0 == [500.5, 64.0, 500.5] and af == [500.5, 64.0, 500.5] and ar == [500.5, 64.0, 500.5],
           "Z2: the spot = where you look within the reach; reach 0 / nothing looked at / too far -> at your feet: %s %s %s %s" % (a1, a0, af, ar))
        # FIX Z2: the dome must cover the Mage - a look point 5 blocks away (radius 4) puts it at her feet
        AS.clearCd(str(zu))
        AIMS["spot"] = [505.5, 64.0, 500.5]
        unthrottle()
        said()
        rf_ = cast("MageZ", "2")
        zf_ = list(aw.zoneArr())
        ck(rf_.startswith("ok:ManaBarrier ") and " at=500.5,64,500.5 r=4 " in rf_ and len(zf_) == 2,
           "FIX Z2: Mana Barrier looked 5 blocks away (radius 4) -> the dome goes at the Mage's feet (she stands in it): %s" % rf_)
        aw.dropZone(zf_[-1])
        # FIX Z2: ab.ManaBarrier.keep - 4 Mana must be LEFT after the cost; 18 Mana = refused, nothing spent; 20 = cast
        AS.clearCd(str(zu))
        zm.setStatValue(MANA, JFloat(18.0))
        unthrottle()
        said()
        rk_ = cast("MageZ", "2")
        sdk_ = said()
        ck(rk_ == "mana" and sv(zm, MANA) == 18.0 and round(sv(zm, STAM), 2) == 12.5 and len(list(aw.zoneArr())) == 1
           and int(AS.left(str(zu), "ManaBarrier", now_ms())) == 0
           and sdk_ == ["Not enough Mana to power the Mana Barrier: 16 to cast + 4 left to soak with (you have 18) - nothing was spent."],
           "FIX Z2: 18 Mana (16 cost + 4 kept needed) -> refused, nothing spent, no cooldown, no dome: %s %s" % (rk_, sdk_))
        zm.setStatValue(MANA, JFloat(20.0))
        unthrottle()
        rk2_ = cast("MageZ", "2")
        said()
        ck(rk2_.startswith("ok:ManaBarrier ") and sv(zm, MANA) == 4.0 and len(list(aw.zoneArr())) == 2, "FIX Z2: 20 Mana -> cast, 4 left to soak with: %s" % rk2_)
        aw.dropZone(list(aw.zoneArr())[-1])
        zm.setStatValue(MANA, JFloat(129.0))
        zm.setStatValue(STAM, JFloat(13.5))
        said()
        # ---- Z3: the REAL hook (AbilShieldSys.handle, the Filter group)
        ck(float(AM.barrierTake(10.0, 129.0, 2.0, 100.0)) == 10.0 and float(AM.barrierTake(10.0, 3.0, 2.0, 100.0)) == 6.0
           and float(AM.barrierTake(150.0, 145.0, 2.0, 100.0)) == 100.0 and float(AM.barrierTake(10.0, 0.0, 2.0, 100.0)) == 0.0
           and float(AM.bubbleTake(30.0, 100.0)) == 30.0 and float(AM.bubbleTake(50.0, 40.0)) == 40.0
           and [int(AM.pulsesDue(100.0, h)) for h in (100.0, 76.0, 75.0, 50.0, 26.0, 25.0, 0.1, 0.0)] == [0, 0, 1, 2, 2, 3, 3, 4],
           "Z3: the pure rules - soaked = min(damage, Mana x ratio, cap left); bubble = min(damage, HP); pulses at 75 / 50 / 25 / 0 %")
        mv(zr, 498.5, 64.0, 500.5)
        d0 = hit(zr, 10.0)
        ck(not bool(d0.isCancelled()) and float(d0.getAmount()) == 10.0 and sv(zm, MANA) == 129.0, "Z3: the Mage OUTSIDE her dome (5 blocks from its centre) -> untouched")
        mv(zr, 505.5, 64.0, 501.5)
        d1 = hit(zr, 10.0)
        ck(bool(d1.isCancelled()) and float(d1.getAmount()) == 0.0 and sv(zm, MANA) == 124.0 and float(bz.absorbed) == 10.0 and float(bz.manaPaid) == 5.0,
           "Z3: the Mage INSIDE: a 10 hit costs 5 Mana (2 HP per Mana) and is cancelled - Health untouched (Mana %s)" % sv(zm, MANA))
        TSt.COMP.get(zr).put(INVUc.getComponentType(), INVUc.INSTANCE)
        dI = hit(zr, 10.0)
        TSt.COMP.get(zr).remove(INVUc.getComponentType())
        ck(not bool(dI.isCancelled()) and float(dI.getAmount()) == 10.0 and sv(zm, MANA) == 124.0 and float(bz.absorbed) == 10.0,
           "FIX Z3: an INVULNERABLE Mage inside (the engine drops the hit) -> untouched, no Mana spent")
        # FIX3: a profile switch with the dome up -> the hook ignores the dome at once (no Mana from the new profile, no soak) before the zone tick ends it
        PROFKEY[str(zu)] = str(zu) + "-p2"
        dP = hit(zr, 10.0)
        del PROFKEY[str(zu)]
        ck(not bool(dP.isCancelled()) and float(dP.getAmount()) == 10.0 and sv(zm, MANA) == 124.0 and float(bz.absorbed) == 10.0 and float(bz.manaPaid) == 5.0,
           "FIX3 Z3: switched profile inside the dome (before the zone tick ends it) -> the hit is not soaked, no Mana taken from the new profile")
        d2 = hit(zr, 3.0, cause=causes.get("OutOfWorld") if DCS_OK else None)
        ck(DCS_OK and not bool(d2.isCancelled()) and float(d2.getAmount()) == 3.0 and sv(zm, MANA) == 124.0, "Z3: out-of-world damage inside the dome -> untouched")
        d3 = Dm(DEs(n_in), DCSc.PROJECTILE, JFloat(8.0))
        C("AbilDmg").tag(d3, zu, "x")
        TCh.REFS.put(JInt(0), zr)
        sys_.handle(0, chunk, tst, tbuf, d3)
        d4 = Dm(DEs(n_in), DCSc.PROJECTILE, JFloat(8.0))
        d4.setCancelled(True)
        sys_.handle(0, chunk, tst, tbuf, d4)
        ck(float(d3.getAmount()) == 8.0 and not bool(d3.isCancelled()) and sv(zm, MANA) == 124.0, "Z3: ability (tagged) damage and an already cancelled hit -> untouched")
        ou, orr, opr, om = player(34, 505.5, 64.0, 499.5, "Bystander2", mana=50.0)[:4]
        setclass(ou, "Archer")
        d5 = hit(orr, 10.0)
        ck(not bool(d5.isCancelled()) and float(d5.getAmount()) == 10.0 and sv(om, MANA) == 50.0, "Z3: another player inside the Mage's dome -> untouched (her dome is hers)")
        d6 = Dm(JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage").NULL_SOURCE, causes.get("Fall") if DCS_OK else DCSc.PROJECTILE, JFloat(6.0))
        TCh.REFS.put(JInt(0), zr)
        sys_.handle(0, chunk, tst, tbuf, d6)
        ck(bool(d6.isCancelled()) and sv(zm, MANA) == 121.0, "Z3: fall damage (no attacker) inside the dome is soaked too ('damage you take') - 6 -> 3 Mana")
        zm.setStatValue(MANA, JFloat(3.0))
        d7 = hit(zr, 10.0)
        ck(not bool(d7.isCancelled()) and float(d7.getAmount()) == 4.0 and sv(zm, MANA) == 0.0 and bool(bz.ended) and str(bz.why) == "mana",
           "Z3: 3 Mana left: 6 of a 10 hit soaked, 4 goes through, Mana 0 -> the dome ends: %s %s" % (float(d7.getAmount()), str(bz.why)))
        PSEEN.clear()
        said()
        ztick()
        ck(len(list(aw.zoneArr())) == 0 and [str(x) for x in PSEEN] == ["Item_Break_GlassMagic"]
           and said() == ["Mana Barrier ended - out of Mana (22 damage soaked for 11 Mana)."],
           "Z3: the next zone tick (the REAL AbilTick) ends it: the quiet vanilla burst + one line: %s" % [str(x) for x in PSEEN])
        d8 = hit(zr, 10.0)
        ck(not bool(d8.isCancelled()) and float(d8.getAmount()) == 10.0, "Z3: no dome any more -> untouched")
        # the cap: 100 % of max Health per dome
        AS.clearCd(str(zu))
        zm.setStatValue(MANA, JFloat(145.0))
        AIMS["spot"] = [505.5, 64.0, 500.5]
        unthrottle()
        cast("MageZ", "2")
        said()
        bz = list(aw.zoneArr())[0]
        d9 = hit(zr, 150.0)
        ck(not bool(d9.isCancelled()) and float(d9.getAmount()) == 50.0 and sv(zm, MANA) == 79.0 and bool(bz.ended) and str(bz.why) == "cap",
           "Z3: a 150 hit with 129 Mana: the dome soaks its cap (100 = 100 %% of max Health) for 50 Mana, 50 goes through, the dome ends: %s Mana %s" % (float(d9.getAmount()), sv(zm, MANA)))
        ztick()
        ck(len(list(aw.zoneArr())) == 0 and said() == ["Mana Barrier ended - it soaked all it can (100 damage soaked for 50 Mana)."], "Z3: the cap end line")
        # ---- Z4: the barrier's own ends: Mana 0 without a hit, a profile switch, the Mage gone, time
        def fresh_barrier():
            AS.clearCd(str(zu))
            zm.setStatValue(MANA, JFloat(145.0))
            unthrottle()
            r0_ = cast("MageZ", "2")
            said()
            return r0_, list(aw.zoneArr())[-1]
        r_, bz = fresh_barrier()
        zm.setStatValue(MANA, JFloat(0.0))
        ztick()
        ck(len(list(aw.zoneArr())) == 0 and said() == ["Mana Barrier ended - out of Mana (0 damage soaked for 0 Mana)."], "Z4: Mana spent elsewhere to 0 -> the dome ends at its next tick")
        r_, bz = fresh_barrier()
        PROFKEY[str(zu)] = str(zu) + "-p2"
        PSEEN.clear()
        ztick()
        ck(len(list(aw.zoneArr())) == 0 and said() == [] and [str(x) for x in PSEEN] == ["Item_Break_GlassMagic"], "Z4: a profile switch -> the dome ends quietly (no line, the burst)")
        del PROFKEY[str(zu)]
        r_, bz = fresh_barrier()
        ebu.remove(zu)
        ztick()
        ebu.put(zu, zr)
        ck(len(list(aw.zoneArr())) == 0 and said() == [], "Z4: the Mage left the world -> the dome ends")
        r_, bz = fresh_barrier()
        bz.nextFx = now_ms() + 600000
        PSEEN.clear()
        ztick()
        rims = [str(x) for x in PSEEN]
        bz.nextFx = 0
        PSEEN.clear()
        ztick()
        ck(len(list(aw.zoneArr())) == 1 and rims == [] and [str(x) for x in PSEEN] == ["Rings_Rings"] * 23, "Z4: a live dome re-draws its rim (the 23-point dome) once a second (not every tick)")
        bz.until = now_ms() - 1
        ztick()
        ck(len(list(aw.zoneArr())) == 0 and said() == ["Mana Barrier ended (0 damage soaked for 0 Mana)."], "Z4: after its time (12 s) the dome ends")
        # ---- Z5: SHIELD BUBBLE (Divinity 10, the plan 4.4 pool 92 Mana / 15.6 Stamina), a party member, a stranger
        pzu, pzr, pzpr, pzm = player(31, 600.5, 64.0, 600.5, "PriestZ", mana=92.0, stam=15.6)[:4]
        mtu, mtr, mtpr, mtm = player(32, 602.5, 64.0, 600.5, "Mate", hp=50.0)[:4]
        stu, str_, stpr, stm = player(33, 600.5, 64.0, 602.5, "Stranger2", hp=50.0)[:4]
        setclass(pzu, "Priest")
        setclass(mtu, "Archer")
        setclass(stu, "Archer")
        LEVEL[(str(pzu), "Divinity")] = 10
        HANDS[31] = "Weapon_Wand_Wood"
        MEMBERS[str(pzu)] = [str(mtu)]
        AIMS["spot"] = [600.5, 64.0, 600.5]
        PSEEN.clear()
        HEALXP.clear()
        unthrottle()
        said()
        r_ = cast("PriestZ", "2")
        sd_ = said()
        ub = list(aw.zoneArr())[-1]
        ck(r_ == "ok:ShieldBubble mana=20 stamina=2 at=600.5,64,600.5 r=6 hp=100" and sv(pzm, MANA) == 72.0 and round(sv(pzm, STAM), 2) == 13.6
           and int(ub.kind) == 2 and float(ub.hpMax) == 100.0 and int(ub.until) - int(ub.start) == 12000
           and [str(x) for x in PSEEN] == ["Shield_Block"] + ["Rings_Rings_Ice"] * 30
           and sd_ == ["Shield Bubble! -20 Mana, -2 Stamina. Ready again in 24 s.",
                       "Shield Bubble: 100 HP for 12 s - it soaks attacks on you and your party inside and heals at 75 / 50 / 25 % and when it breaks."],
           "Z5: SHIELD BUBBLE at Divinity 10 (owned, affordable: 92 Mana) - 20 Mana + 2 Stamina, 24 s, HP = 100 %% of max Health, 6 blocks, 12 s, "
           "the placing flash + 30 rim bursts (16 edge + 13 upper + 1 top - FIX: a dome): %s %s" % (r_, sd_))
        e1 = hit(mtr, 30.0)
        ck(bool(e1.isCancelled()) and float(ub.hp) == 70.0 and int(ub.pulsesDue) == 1 and float(ub.xpOthers) == 30.0,
           "Z5: an attack (30) on the PARTY member inside -> soaked by the bubble (HP 70, one pulse due at 75 %%)")
        e2 = hit(str_, 10.0)
        ck(not bool(e2.isCancelled()) and float(e2.getAmount()) == 10.0 and float(ub.hp) == 70.0, "Z5: a stranger (not in the party) inside -> not shielded")
        e3 = Dm(JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage").NULL_SOURCE, causes.get("Fall") if DCS_OK else DCSc.PROJECTILE, JFloat(5.0))
        TCh.REFS.put(JInt(0), pzr)
        sys_.handle(0, chunk, tst, tbuf, e3)
        ck(not bool(e3.isCancelled()) and float(ub.hp) == 70.0, "Z5: fall damage on the Priest (no attacker) -> the bubble only soaks attacks")
        e3b = Dm(JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$ProjectileSource")(n_in, n_in), DCSc.PROJECTILE, JFloat(1.0))
        TCh.REFS.put(JInt(0), pzr)
        sys_.handle(0, chunk, tst, tbuf, e3b)
        ck(bool(e3b.isCancelled()) and float(ub.hp) == 69.0, "Z5: an ARROW (Damage$ProjectileSource) at the Priest inside -> blocked by the bubble (soaked)")
        e3c = hit(mtr, 10.0, src=DEs(orr))
        ck(bool(e3c.isCancelled()) and float(ub.hp) == 59.0 and float(ub.xpOthers) == 30.0 and float(ub.xpSelf) == 1.0,
           "FIX Z5: a PLAYER's attack (10) on the party member inside -> soaked, but NO absorb XP (no Divinity farming with an alt): xpOthers %s" % float(ub.xpOthers))
        ub.hp = 70.0
        ub.xpSelf = 0.0
        ub.absorbed = 30.0
        ub.nextFx = now_ms() + 600000
        PSEEN.clear()
        said()
        ztick()
        ck([sv(pzm, HP), sv(mtm, HP), sv(stm, HP)] == [100.0, 58.0, 54.0] and int(ub.pulsesDone) == 1
           and [str(x) for x in PSEEN] == ["Magic_Hit", "Magic_Hit"],
           "Z5: pulse 1 (the REAL AbilTick): everyone inside gets 8 %% of max Health - the party member +8, the stranger the othersPercent share +4, "
           "the full Priest nothing: %s" % [sv(pzm, HP), sv(mtm, HP), sv(stm, HP)])
        ck(sorted(HEALXP) == sorted([[str(pzu), 12.0, "classes:heal", False], [str(pzu), 15.0, "classes:heal", False]]),
           "Z5: Divinity XP: 12 HP healed on others + the absorb XP 30 x 0.5 = 15: %s" % HEALXP)
        HEALXP.clear()
        e4 = hit(pzr, 30.0)
        ztick()
        ck(bool(e4.isCancelled()) and float(ub.hp) == 40.0 and int(ub.pulsesDone) == 2 and [sv(mtm, HP), sv(stm, HP)] == [66.0, 58.0]
           and sorted(HEALXP) == sorted([[str(pzu), 12.0, "classes:heal", False], [str(pzu), 15.0, "classes:heal:self", True]]),
           "Z5: an attack on the PRIEST (30) -> HP 40, pulse 2; the Priest's own soak pays the self rate (15): %s" % HEALXP)
        e5 = hit(mtr, 50.0)
        HEALXP.clear()
        PSEEN.clear()
        ztick()
        ck(not bool(e5.isCancelled()) and float(e5.getAmount()) == 10.0 and float(ub.hp) == 0.0 and int(ub.pulsesDone) == 4 and len(list(aw.zoneArr())) == 0
           and [sv(mtm, HP), sv(stm, HP)] == [82.0, 66.0] and [str(x) for x in PSEEN][-1] == "Shield_Shatter"
           and said() == ["Shield Bubble broke (100 damage soaked, 4 heal pulses)."],
           "Z5: a 50 hit with 40 HP left: 40 soaked, 10 goes through, the bubble BREAKS -> pulses 3 + 4, the shatter burst, one line: %s %s" % ([sv(mtm, HP), sv(stm, HP)], [str(x) for x in PSEEN][-2:]))
        # overlapping bubbles: the one with the most HP soaks; a profile switch: heals on, no XP; time; maxZones; the per-bubble heal cap
        AS.clearCd(str(pzu))
        pzm.setStatValue(MANA, JFloat(92.0))
        unthrottle()
        cast("PriestZ", "2")
        said()
        u1 = list(aw.zoneArr())[-1]
        u2 = AZ(2, pzu, 600.5, 64.0, 600.5, 6.0, now_ms(), now_ms() + 12000)
        u2.hpMax = 100.0
        u2.hp = 90.0
        u2.pkey = str(pzu)
        aw.addZone(u2)
        u1.hp = 50.0
        e6 = hit(mtr, 10.0)
        ck(bool(e6.isCancelled()) and float(u2.hp) == 80.0 and float(u1.hp) == 50.0, "Z5: two bubbles overlap -> the one with the most HP soaks")
        mtm.setStatValue(HP, JFloat(50.0))
        PROFKEY[str(pzu)] = str(pzu) + "-p2"
        HEALXP.clear()
        u1.pulsesDue = 2
        ztick()
        ck(sv(mtm, HP) == 66.0 and HEALXP == [] and int(u1.pulsesDone) == 2, "Z5: the Priest switched profile -> the bubble still heals (2 pulses), no Divinity XP")
        del PROFKEY[str(pzu)]
        AC.HEAL_CAP = 10
        u2.pulsesDue = 2
        mtm.setStatValue(HP, JFloat(50.0))
        ztick()
        AC.HEAL_CAP = 60
        ck(sv(mtm, HP) == 60.0, "Z5: abil.healCap per target per bubble (10 %%: 8 + 2, the second pulse capped): %s" % sv(mtm, HP))
        u1.until = now_ms() - 1
        u2.until = now_ms() - 1
        ztick()
        ck(len(list(aw.zoneArr())) == 0 and said() == ["Shield Bubble faded (0 damage soaked, 2 heal pulses).", "Shield Bubble faded (10 damage soaked, 2 heal pulses)."],
           "Z5: after their time both fade with one line each")
        AC.MAX_ZONES = 1
        AS.clearCd(str(pzu))
        pzm.setStatValue(MANA, JFloat(92.0))
        unthrottle()
        cast("PriestZ", "2")
        AS.clearCd(str(pzu))
        unthrottle()
        r_ = cast("PriestZ", "2")
        said()
        zl_ = list(aw.zoneArr())
        ck(" replaced=1" in r_ and len(zl_) == 2 and bool(zl_[0].ended) and str(zl_[0].why) == "replaced" and not bool(zl_[1].ended),
           "Z5: abil.maxZones 1 -> the new bubble ends the Priest's older one: %s" % r_)
        ztick()
        ck(len(list(aw.zoneArr())) == 1 and said() == ["Shield Bubble ended - a newer zone replaced it (0 damage soaked, 0 heal pulses)."], "Z5: the replaced one ends at the next tick")
        AC.MAX_ZONES = 2
        # the world cap counts zones: 47 jobs + 1 zone = 48 -> full, refused, nothing spent
        for i_ in range(47):
            aw.add(AJ(1, now_ms() + 600000, mu, "x", 0.0, 0.0, 0.0, 1.0, 0.0))
        AS.clearCd(str(zu))
        zm.setStatValue(MANA, JFloat(145.0))
        unthrottle()
        r_ = cast("MageZ", "2")
        ck(r_ == "full" and sv(zm, MANA) == 145.0 and int(AS.left(str(zu), "ManaBarrier", now_ms())) == 0, "Z6: 47 jobs + 1 zone = abil.maxLive 48 -> refused, nothing spent: %s" % r_)
        aw.due(now_ms() + 700000)
        said()
        # a zone whose tick throws is dropped (logged), the others keep going
        bad_ = AZ(2, pzu, 600.5, 64.0, 600.5, 6.0, now_ms(), now_ms() + 12000)
        bad_.hpMax = 100.0
        bad_.hp = 70.0
        bad_.pulsesDue = 1
        bad_.healed = None
        aw.addZone(bad_)
        mtm.setStatValue(HP, JFloat(50.0))
        n0_ = len(list(aw.zoneArr()))
        ztick()
        ck(n0_ == 2 and len(list(aw.zoneArr())) == 1 and list(aw.zoneArr())[0] != bad_, "Z6: a zone whose tick throws is dropped; the other bubble keeps going")
        for z_ in list(aw.zoneArr()):
            aw.dropZone(z_)
        said()
        # the cast pipeline refunds a failing zone executor (nothing live, Mana + cooldown back)
        AS.clearCd(str(zu))
        zm.setStatValue(MANA, JFloat(145.0))
        A.PSEEN = JClass("java.util.Collections").emptyList()
        unthrottle()
        r_ = cast("MageZ", "2")
        A.PSEEN = PSEEN
        ck(r_ == "failed" and sv(zm, MANA) == 145.0 and len(list(aw.zoneArr())) == 0 and int(AS.left(str(zu), "ManaBarrier", now_ms())) == 0,
           "Z6: a Mana Barrier executor that throws before the dome is live -> refunded, no zone: %s" % r_)
        said()
    except Exception:
        import traceback
        R["checks"].append([False, "Z crashed: " + traceback.format_exc()[-2500:]])

    # ================================================================================== H. the HUD bridge (R2 data) + SkyyHud 0.3.18 on it
    try:
        for z_ in list(aw.zoneArr()):
            aw.dropZone(z_)
        AFn = C("AbilFn")()
        br.put("class:fn:abil", AFn)   # what SkyyClassesPlugin.setup puts (the harness has no plugin)
        jb = lambda x: None if x is None else bool(x)
        AS.WANT.clear()
        AS.SAMPLE.clear()
        AS.clearCd(str(zu))
        zm.setStatValue(MANA, JFloat(145.0))
        zm.setStatValue(STAM, JFloat(14.5))
        mv(zr, 500.5, 64.0, 500.5)
        TCh.REFS.put(JInt(0), zr)
        tick.tick(JFloat(0.05), 0, chunk, tst, tbuf)
        ck(AS.SAMPLE.isEmpty(), "H1: nobody's HUD asked -> the tick takes no sample (zero cost without the widget)")
        a = list(AFn.apply(zu))
        ck(len(a) == 44 and [str(x) for x in a[16:20]] == ["Meteor", "ManaBarrier", "FrostNova", "Starfall"]
           and [float(x) for x in a[20:24]] == [23.0, 16.0, 0.0, 0.0] and [float(x) for x in a[24:28]] == [2.0, 1.0, 0.0, 0.0]
           and [jb(x) for x in a[28:33]] == [None] * 5 and str(a[33]) == "Mage" and str(a[37]) == "abil2" and [int(x) for x in a[38:42]] == [1, 10, 20, 30]
           and [str(a[i * 4 + 3]) for i in range(4)] == ["ready", "ready", "locked", "locked"] and bool(AS.WANT.containsKey(zu)),
           "H1: class:fn:abil = Object[44]: ids, Mana / Stamina costs, class, 'abil2', unlock levels; affordable / crouch unknown before the first "
           "sample; the ask is remembered (WANT): %s" % [str(x) for x in a[16:44]])
        tick.tick(JFloat(0.05), 0, chunk, tst, tbuf)
        smp = list(AS.SAMPLE.get(zu))
        a = list(AFn.apply(zu))
        ck([round(x, 2) for x in smp[:4]] == [145.0, 14.5, 0.0, 0.0] and [jb(x) for x in a[28:32]] == [True, True, None, None]
           and jb(a[32]) is False and float(a[34]) == 145.0 and float(a[35]) == 14.5 and jb(a[36]) is False and 0 <= int(a[42]) < 3000,
           "H2: the REAL AbilTick samples Mana / Stamina / crouch / creative on the world thread; READY + affordable: %s" % a[28:43])
        zm.setStatValue(MANA, JFloat(20.0))
        AS.SAMPLE.put(zu, JArray(JDouble)([999.0, 14.5, 0.0, 0.0, float(now_ms())]))
        tick.tick(JFloat(0.05), 0, chunk, tst, tbuf)
        throttled = round(float(list(AS.SAMPLE.get(zu))[0]), 1)
        AS.SAMPLE.clear()
        tick.tick(JFloat(0.05), 0, chunk, tst, tbuf)
        a = list(AFn.apply(zu))
        ck(throttled == 999.0 and [jb(a[28]), jb(a[29])] == [False, True], "H3: a sample at most every 0.2 s; Mana 20 -> Meteor (23) UNAFFORDABLE, Mana Barrier (16 + 4 kept) affordable: %s" % a[28:30])
        zm.setStatValue(MANA, JFloat(18.0))
        AS.SAMPLE.clear()
        tick.tick(JFloat(0.05), 0, chunk, tst, tbuf)
        a = list(AFn.apply(zu))
        zm.setStatValue(MANA, JFloat(20.0))
        AS.SAMPLE.clear()
        tick.tick(JFloat(0.05), 0, chunk, tst, tbuf)
        ck([jb(a[28]), jb(a[29])] == [False, False] and float(a[21]) == 16.0, "FIX H3: Mana 18 -> Mana Barrier NOT affordable (16 + 4 kept), its cost still 16: %s" % a[28:30])
        AS.arm(str(zu), "Meteor", now_ms(), 14000)
        a = list(AFn.apply(zu))
        ck(str(a[3]) == "cooldown" and 13000 <= int(a[1]) <= 14000 and int(a[2]) == 14000 and jb(a[28]) is False, "H3: COOLDOWN: ms left / total; still unaffordable")
        zmsc.getMovementStates().crouching = True
        setf(zpl, PLAc, "gameMode", GM.Creative)
        AS.SAMPLE.clear()
        tick.tick(JFloat(0.05), 0, chunk, tst, tbuf)
        a = list(AFn.apply(zu))
        ck(jb(a[32]) is True and jb(a[36]) is True and [jb(a[28]), jb(a[29])] == [True, True], "H4: CROUCHING sampled; creative + abil.creativeFree -> free = affordable")
        zmsc.getMovementStates().crouching = False
        setf(zpl, PLAc, "gameMode", GM.Adventure)
        AS.SAMPLE.put(zu, JArray(JDouble)([145.0, 14.5, 0.0, 0.0, float(now_ms() - 4000)]))
        a = list(AFn.apply(zu))
        ck([jb(x) for x in a[28:33]] == [None] * 5, "H5: a sample older than 3 s is not used (affordable / crouch unknown)")
        AS.WANT.put(zu, JLong(now_ms() - 6000))
        tick.tick(JFloat(0.05), 0, chunk, tst, tbuf)
        ck(not AS.WANT.containsKey(zu) and not AS.SAMPLE.containsKey(zu), "H5: no ask for 5 s -> the player leaves the sample list")
        AS.WANT.put(mu, JLong(now_ms()))
        AS.SAMPLE.put(mu, JArray(JDouble)([1.0, 1.0, 0.0, 0.0, float(now_ms())]))
        C("ClassQuit")().accept(pde)
        ck(not AS.WANT.containsKey(mu) and not AS.SAMPLE.containsKey(mu), "H5: a disconnect (the REAL ClassQuit) drops the player's sample")
        LEVEL[(str(pzu), "Divinity")] = 20
        AS.clearCd(str(pzu))
        a = list(AFn.apply(pzu))
        ck([str(a[i * 4 + 3]) for i in range(4)] == ["ready", "ready", "passive", "locked"] and str(a[33]) == "Priest", "H5: a Priest at Divinity 20: Guardian Spirit = passive")
        LEVEL[(str(pzu), "Divinity")] = 10
        # ---- SkyyHud 0.3.18 (its own class loader) on the SAME bridge map: the Abilities widget model per state
        W = JClass("com.skyy.hud.Widgets", loader=ldh)
        WLh = JClass("com.skyy.hud.WLayout", loader=ldh)

        def model(u_, icons=True, fresh=True):
            AS.SAMPLE.clear()
            AFn.apply(u_)
            if fresh:
                TCh.REFS.put(JInt(0), PLAYERS[[k for k, v in PLAYERS.items() if str(v[0]) == str(u_)][0]][1])
                tick.tick(JFloat(0.05), 0, chunk, tst, tbuf)
            return [None if x is None else str(x) for x in W.abilModelU(u_, icons)]
        AS.clearCd(str(zu))
        zm.setStatValue(MANA, JFloat(145.0))
        m = model(zu)
        ck(m[2:7] == ["Meteor", "23 Mana + 2 Stam", None, "n", "SkyyHud/Abil/Meteor.png"] and m[7:12] == ["Mana Barrier", "16 Mana + 1 Stam", None, "n", "SkyyHud/Abil/ManaBarrier.png"]
           and m[12] == "p" and m[13] == "1" and m[1] == "Meteor 23 Mana + 2 Stam" and m[0] == "Ap1|-nSkyyHud/Abil/Meteor.png|-nSkyyHud/Abil/ManaBarrier.png",
           "HW1 (FIX2: both costs): the widget READY: the two primaries with icon, name and cost in the widget colour: %s" % m)
        AS.arm(str(zu), "Meteor", now_ms(), 14000)
        m = model(zu)
        ck(m[2:6] == ["Meteor", "14s", m[4], "n"] and m[4] is not None and 0.9 <= float(m[4]) <= 1.0 and m[0].startswith("Ap1|bn"),
           "HW2: COOLDOWN: the countdown '14s' + a bar (Value %s) - the shape changes (a re-send)" % m[4])
        AS.clearCd(str(zu))
        zm.setStatValue(MANA, JFloat(20.0))
        m = model(zu)
        ck(m[2:6] == ["Meteor", "23 Mana + 2 Stam", None, "g"] and m[7:11] == ["Mana Barrier", "16 Mana + 1 Stam", None, "n"], "HW3: UNAFFORDABLE (20 Mana): Meteor GREY with its cost, Mana Barrier not: %s" % m[2:11])
        zm.setStatValue(STAM, JFloat(0.5))
        m = model(zu)
        ck(m[8] == "16 Mana + 1 Stam" and m[10] == "g", "HW3 (FIX2): Stamina short -> 'Mana Barrier 16 Mana + 1 Stam' grey: %s" % m[7:11])
        zm.setStatValue(STAM, JFloat(14.5))
        zm.setStatValue(MANA, JFloat(18.0))
        m = model(zu)
        ck(m[7:11] == ["Mana Barrier", "16 Mana + 1 Stam", None, "g"], "FIX HW3: 18 Mana (Mana Barrier keeps 4) -> grey with the whole cost: %s" % m[7:11])
        zm.setStatValue(STAM, JFloat(14.5))
        zm.setStatValue(MANA, JFloat(145.0))
        LEVEL[(str(zu), "Sorcery")] = 9
        m = model(zu)
        ck(m[7:11] == ["Mana Barrier", "Lv 10", None, "g"], "HW4: LOCKED at Sorcery 9: 'Mana Barrier  Lv 10' grey: %s" % m[7:11])
        LEVEL[(str(zu), "Sorcery")] = 10
        zmsc.getMovementStates().crouching = True
        m = model(zu)
        zmsc.getMovementStates().crouching = False
        ck(m[12] == "a" and m[2:7] == ["Frost Nova", "Lv 20", None, "g", "SkyyHud/Abil/FrostNova.png"] and m[7:12] == ["Starfall", "Lv 30", None, "g", "SkyyHud/Abil/Starfall.png"]
           and m[0].startswith("Aa1|"), "HW5: CROUCHING -> the rows swap to the two alts (Skyy: 'HUD swaps to alts while crouching'): %s" % m)
        setf(zpl, PLAc, "gameMode", GM.Creative)
        m = model(zu)
        setf(zpl, PLAc, "gameMode", GM.Adventure)
        ck(m[3] == "Free" and m[8] == "Free", "HW6: creative -> 'Free'")
        m = model(zu, icons=False)
        ck(m[6] is None and m[11] is None and m[13] == "0" and m[0].startswith("Ap0|"), "HW6: Settings 'Icons Hide' -> names only")
        m = model(zu, fresh=False)
        ck(m[3] == "23 Mana + 2 Stam" and m[5] == "n", "HW6: no fresh sample yet (the first second) -> costs shown, not greyed")
        ck(model(cu_)[0] == "A0" and model(wu_)[0] == "A0", "HW7: no class / a class without abilities -> the widget is hidden")
        real = br.get("class:fn:abil")

        @JImplements("java.util.function.Function")
        class Old16:
            @JOverride
            def apply(self, o):
                r0 = real.apply(o)
                return None if r0 is None else JArray(JObject)(list(r0)[:16])
        br.put("class:fn:abil", Old16())
        LEVEL[(str(zu), "Sorcery")] = 9
        m = model(zu)
        ck(m[2:7] == ["Meteor", "Ready", None, "n", None] and m[7:11] == ["Mana Barrier", "Locked", None, "g"] and m[13] == "0",
           "HW8: SkyyClasses 0.1.16's 16-field answer -> 'Ready' / 'Locked', no icons (still works): %s" % m[2:14])
        LEVEL[(str(zu), "Sorcery")] = 10
        br.remove("class:fn:abil")
        ck(model(zu)[0] == "A0" and not bool(W.abilHave(br)) and str(list(W.abilSample(True))[2]) == "Needs SkyyClasses 0.1.17",
           "HW9: NO SkyyClasses (no class:fn:abil) -> hidden; the editor sample says 'Needs SkyyClasses 0.1.17'")
        br.put("class:fn:abil", real)
        # the markup of a cooling-down row (icon Group, labels, the bar) and the box maths
        AS.arm(str(zu), "Meteor", now_ms(), 14000)
        m = model(zu)
        wl_ = getattr(W, "def_", None) or getattr(W, "def")
        lay_ = wl_("Abilities")
        mk = str(W.abilBody("SkyyWAbilities", lay_, 100, JArray(JString)(m), 6, 200))
        ck('Group #SkyyWAbilitiesI0 { Anchor: (Left: ' in mk and 'Background: "SkyyHud/Abil/Meteor.png"; }' in mk and "ProgressBar #SkyyWAbilitiesBar0" in mk
           and "ProgressBar #SkyyWAbilitiesBar1" not in mk and "Label #SkyyWAbilitiesN0Txt" in mk and "Label #SkyyWAbilitiesS1Txt" in mk
           and int(W.bodyH("Abilities", JArray(JString)(m), 100)) == 59 and [str(x) for x in W.barPairs("Abilities", JArray(JString)(m))] == ["Bar0", m[4]]
           and bool(lay_.en) and str(lay_.anchor) == "tl" and int(lay_.dx) == 8 and int(lay_.dy) == 760 and int(lay_.bw) == 220 and int(lay_.bh) == 59,
           "HW10: the markup: icon Group with the shipped picture, name / right labels, the bar under the cooling row; 59 px high; default ON tl 8,760")
        AS.clearCd(str(zu))
    except Exception:
        import traceback
        R["checks"].append([False, "H crashed: " + traceback.format_exc()[-2500:]])

    # ---------------- SK. SkyySkills 0.4.28 on the SAME bridge: an ability kill pays the caster's class skill (food in hand)
    try:
        SC28 = JClass(SPKG + "SkillClass", loader=ldk)
        SC27 = JClass(SPKG + "SkillClass", loader=ldo)
        f28 = SC28.allowedFn()
        slot = int(SC28.slotOfClass("Mage"))
        HANDS[1] = "Food_Bread"
        ck(str(SC28.abilCaster(dmg)) == str(mu) and SC28.abilCaster(plain) is None and SC28.abilCaster(None) is None, "SK: abilCaster = class:fn:abilhit")
        ck(bool(SC28.weaponOrAbil(mu, slot, f28, tst, mr, dmg)) and not bool(SC28.weaponOrAbil(mu, slot, f28, tst, mr, plain))
           and not bool(SC28.weaponOrAbil(au, slot, f28, tst, ar_, dmg)), "SK: weaponOrAbil - the caster's tagged damage counts as a class weapon hit (nothing in hand); "
           "an untagged hit / another player's ability damage does not")
        ck(int(SC28.killSlot(mpr, tst, mr, dmg)) == slot and int(SC28.killSlot(mpr, tst, mr, plain)) == -1 and int(SC28.killSlot(mpr, tst, mr)) == -1,
           "SK: KILL XP - SkillClass.killSlot(pr, acc, att, the killing Damage) = the Sorcery slot for a Meteor kill with food in hand; a plain kill "
           "with food = -1 (unchanged), the old 3-argument form = -1")
        ck(int(SC27.killSlot(mpr, tst, mr)) == -1, "SK: control - SkyySkills 0.4.27 pays nothing for the same kill (the plan's finding)")
        br.remove("class:fn:abilhit")
        ck(SC28.abilCaster(dmg) is None and int(SC28.killSlot(mpr, tst, mr, dmg)) == -1, "SK: without SkyyClasses 0.1.16 (no class:fn:abilhit) 0.4.28 = 0.4.27")
        br.put("class:fn:abilhit", C("AbilHitFn")())
    except Exception:
        import traceback
        R["checks"].append([False, "SK crashed: " + traceback.format_exc()[-1500:]])
    R["warn_fails"] = int(Cfg.FAILS)
    json.dump(R, open(out, "w"), indent=1)
    os._exit(0)


# ============================================================================================================ child: CC
def run_cc(jar, prev, out, repl):
    sk().run_cc(jar, prev, out, repl)
    os._exit(0)


# ============================================================================================================ child: ST (one start)
def run_s(home, step):
    from jpype import JClass, JArray, JObject
    jvm([JAR])
    Cfg, Pub, AC, AS = JClass(PKG + "ClassCfg"), JClass(PKG + "CfgPub"), JClass(PKG + "AbilCfg"), JClass(PKG + "AbilStore")
    Paths = JClass("java.nio.file.Paths")
    out = {"step": step}
    base = os.path.join(home, "Skyy_SkyyClasses")
    Cfg.FILE = Paths.get(os.path.join(base, "config.properties"))
    out["mig"] = str(Cfg.migrate0110())
    out["load"] = str(Cfg.load())
    AS.DIR = Paths.get(os.path.join(base, "abilities"))
    pdir = os.path.join(base, "players")
    keys = [f[:-len(".properties")] for f in os.listdir(pdir) if f.endswith(".properties")] if os.path.isdir(pdir) else []
    for k in keys:
        AS.load(k)
    out["keys"] = len(keys)
    Pub.start(Paths.get(home), None)
    fn = Cfg.bridge().get("config:fn:SkyyClasses")

    def op(*args):
        a = JArray(JObject)(len(args))
        for i, x in enumerate(args):
            a[i] = x
        return fn.apply(a)
    out["vals"] = {"M_CD": float(AC.M_CD), "M_MANA": float(AC.M_MANA), "S_MANA": float(AC.S_MANA), "PART": bool(AC.PART), "UNLOCK_A1X": int(AC.UNLOCK_A1X),
                   "B_CD": float(AC.B_CD), "B_MANA": float(AC.B_MANA), "U_MANA": float(AC.U_MANA), "U_PULSE": int(AC.U_PULSE), "TICK": float(AC.TICK),
                   "MAX_ZONES": int(AC.MAX_ZONES), "B_RATIO": float(AC.B_RATIO)}
    out["gets"] = dict((k, None if op("get", k) is None else str(op("get", k))) for k in ("ab.Meteor.walk.cooldown", "part.abilities", "abil.healCap",
                                                                                          "ab.ManaBarrier.walk.cooldown", "ab.ShieldBubble.pulse", "abil.maxZones"))
    out["status"] = [str(x) for x in op("status")]
    if step == "set":
        r = op("set", "ab.ManaBarrier.walk.cooldown", "20", None, None, "yes", "console")
        out["set"] = [None if x is None else str(x) for x in r]
        out["after_set"] = float(AC.B_CD)
    out["summary"] = str(Cfg.summary())
    Pub.flush()
    time.sleep(0.6)
    Pub.shutdown()
    json.dump(out, open(os.path.join(home, "s-%s.json" % step), "w"), indent=1)
    os._exit(0)


# ============================================================================================================ parent
def main():
    if "--n" in sys.argv:
        run_n(arg("--out"))
    if "--cc" in sys.argv:
        run_cc(arg("--cc"), arg("--prevjar"), arg("--out"), arg("--repl"))
    if "--s" in sys.argv:
        run_s(arg("--home"), arg("--step"))
    os.makedirs(SCRATCH, exist_ok=True)
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    env = dict(os.environ, TEMP=tmp, TMP=tmp)
    me = os.path.abspath(__file__)
    live_snap0 = snapdir(LIVE)

    # ---- A + N + SK
    out = os.path.join(SCRATCH, "n.json")
    p = subprocess.run([sys.executable, me, "--n", "--out", out, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(out), "N: the child JVM ran")
    if os.path.isfile(out):
        R = json.load(open(out))
        for ok, what in R["checks"]:
            check(ok, what)
        for n in R.get("notes", []):
            print("note:", n)
        print("A/N/SK: %d checks (%d warnings logged by the mod - expected: the real engine calls without a world)" % (len(R["checks"]), R.get("warn_fails", 0)))

    # ---- CC
    vers_c = ["0.1.17", "0.1.16"]
    rules_c = []
    outc = os.path.join(SCRATCH, "cc-classes.json")
    p = subprocess.run([sys.executable, me, "--cc", JAR, "--prevjar", PREV_JAR, "--out", outc, "--repl", json.dumps({"versions": vers_c, "rules": rules_c}),
                        "--dir", SCRATCH], env=env)
    if p.returncode == 0 and os.path.isfile(outc):
        d = json.load(open(outc))
        check(sorted(d["added"]) == sorted(NEW_CLASSES) and not d["gone"], "CC: AbilZone, AbilShieldSys, AbilShieldSysU are the only new classes, none gone: %s / %s" % (d["added"], d["gone"]))
        # every class / method / field that may differ (javassist instruction text; constants-only differences are allowed anywhere)
        CC_ALLOWED = {'Abil': {'fields_gone': [],
                  'fields_new': ['FX_BARRIER:Ljava/lang/String;',
                                 'FX_BREAK:Ljava/lang/String;',
                                 'FX_BUBBLE:Ljava/lang/String;',
                                 'FX_BUBBLE_ON:Ljava/lang/String;',
                                 'FX_END:Ljava/lang/String;'],
                  'same_shape': True,
                  'structural': ['barrierCast(Lcom/hypixel/hytale/server/core/universe/PlayerRef;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/Ref;Ljava/util/UUID;Lcom/skyy/classes/AbilWorld;[DJ)Ljava/lang/String; '
                                 '(new)',
                                 'bubbleCast(Lcom/hypixel/hytale/server/core/universe/PlayerRef;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/Ref;Ljava/util/UUID;Lcom/skyy/classes/AbilWorld;[DJ)Ljava/lang/String; '
                                 '(new)',
                                 'castNow(Lcom/hypixel/hytale/server/core/universe/PlayerRef;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/universe/world/World;Ljava/lang/String;)Ljava/lang/String;',
                                 'endLine(Lcom/skyy/classes/AbilZone;)Ljava/lang/String; (new)',
                                 'inside(Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/ComponentAccessor;Lcom/skyy/classes/AbilZone;Ljava/util/ArrayList;Ljava/util/ArrayList;)V '
                                 '(new)',
                                 'payXp(Lcom/skyy/classes/AbilZone;Z)V (new)',
                                 'pulse(Lcom/skyy/classes/AbilZone;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/ComponentAccessor;Z)D '
                                 '(new)',
                                 'ring(Ljava/lang/String;Lcom/skyy/classes/AbilZone;Lcom/hypixel/hytale/component/ComponentAccessor;)V (new)',
                                 'sample(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/ComponentAccessor;J)V (new)',
                                 'shield(Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/modules/entity/damage/Damage;J)Ljava/lang/String; '
                                 '(new)',
                                 'spot(Lcom/hypixel/hytale/component/ComponentAccessor;Lcom/hypixel/hytale/component/Ref;D)[D (new)',
                                 'spotText(Lcom/skyy/classes/AbilZone;)Ljava/lang/String; (new)',
                                 'xpOk(Lcom/skyy/classes/AbilZone;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/ComponentAccessor;)Z '
                                 '(new)',
                                 'zoneEnd(Lcom/skyy/classes/AbilZone;Lcom/hypixel/hytale/component/ComponentAccessor;)V (new)',
                                 'zoneTick(Lcom/skyy/classes/AbilZone;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;J)Z '
                                 '(new)']},
         'AbilCfg': {'fields_gone': [],
                     'fields_new': ['B_CD:D',
                                    'B_KEEP:D',
                                    'B_MANA:D',
                                    'B_MAX:J',
                                    'B_RADIUS:D',
                                    'B_RANGE:D',
                                    'B_RATIO:D',
                                    'B_STAM:D',
                                    'B_TIME:D',
                                    'MAX_ZONES:J',
                                    'TICK:D',
                                    'U_CD:D',
                                    'U_HP:J',
                                    'U_MANA:D',
                                    'U_PULSE:J',
                                    'U_RADIUS:D',
                                    'U_RANGE:D',
                                    'U_STAM:D',
                                    'U_TIME:D'],
                     'same_shape': True,
                     'structural': ['<clinit>', 'read(Ljava/util/Properties;)V', 'text()Ljava/lang/String;']},
         'AbilDefs': {'fields_gone': [],
                      'fields_new': ['BUBBLE:I', 'MANAB:I'],
                      'same_shape': True,
                      'structural': ['<clinit>', 'cdMs(I)J', 'mana(I)D', 'stamina(I)D']},
         'AbilFn': {'fields_gone': [], 'fields_new': [], 'same_shape': True, 'structural': ['apply(Ljava/lang/Object;)Ljava/lang/Object;']},
         'AbilMath': {'fields_gone': [],
                      'fields_new': [],
                      'same_shape': True,
                      'structural': ['barrierTake(DDDD)D (new)', 'bubbleTake(DD)D (new)', 'pulsesDue(DD)I (new)', 'ringPoints(D)I (new)']},
         'AbilStore': {'fields_gone': [],
                       'fields_new': ['SAMPLE:Ljava/util/concurrent/ConcurrentHashMap;', 'WANT:Ljava/util/concurrent/ConcurrentHashMap;'],
                       'same_shape': True,
                       'structural': ['<clinit>']},
         'AbilTick': {'fields_gone': [],
                      'fields_new': [],
                      'same_shape': True,
                      'structural': ['tick(FILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;)V']},
         'AbilWorld': {'fields_gone': [],
                       'fields_new': ['nextZone:J', 'nz:I', 'zones:Ljava/util/ArrayList;'],
                       'same_shape': True,
                       'structural': ['<init>(Ljava/lang/String;)V',
                                      'addZone(Lcom/skyy/classes/AbilZone;)I (new)',
                                      'dropZone(Lcom/skyy/classes/AbilZone;)V (new)',
                                      'full()Z',
                                      'idle()Z',
                                      'prune(J)I',
                                      'run(Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;J)V',
                                      'zoneArr()[Lcom/skyy/classes/AbilZone; (new)',
                                      'zoneCount()I (new)']},
         'CfgFile': {'fields_gone': [], 'fields_new': [], 'same_shape': True, 'structural': ['<clinit>']},
         'CfgRows': {'fields_gone': [], 'fields_new': [], 'same_shape': True, 'structural': ['<clinit>']},
         'ClassCfg': {'fields_gone': [], 'fields_new': [], 'same_shape': True, 'structural': ['<clinit>']},
         'ClassQuit': {'fields_gone': [], 'fields_new': [], 'same_shape': True, 'structural': ['accept(Ljava/lang/Object;)V']},
         'SkyyClassesPlugin': {'fields_gone': [], 'fields_new': [], 'same_shape': True, 'structural': ['setup()V']}}
        got = dict((c, {"structural": sorted(v["structural"]), "fields_new": sorted(v["fields_new"]), "fields_gone": sorted(v["fields_gone"]), "same_shape": v["same_shape"]})
                   for c, v in d["classes"].items() if v["structural"] or v["fields_new"] or v["fields_gone"] or not v["same_shape"])
        if "--cc-write" in sys.argv:
            json.dump(got, open(os.path.join(SCRATCH, "cc-got.json"), "w"), indent=1, sort_keys=True)
        check(CC_ALLOWED is not None and got == CC_ALLOWED, "CC: SkyyClasses 0.1.16 -> 0.1.17 changes exactly the planned classes / methods / fields (AbilCfg rows, AbilDefs "
              "costs, AbilMath + AbilStore + AbilWorld zone parts, Abil zone executors + castNow, AbilFn, AbilTick.tick, ClassQuit, setup, the kit rows): %s"
              % json.dumps(dict((c, got[c]) for c in sorted(set(got) ^ set(CC_ALLOWED or {})) or [c for c in got if CC_ALLOWED and got[c] != CC_ALLOWED.get(c)]))[:2500])
        print("CC classes: changed %s" % dict((c, v["structural"] + ["const:" + x for x in v["const_only"]]) for c, v in d["classes"].items()))
    else:
        check(False, "CC: the classes compare child ran")

    # ---- ST: start twice on a scratch COPY of the live folder
    part_st(env, me)
    check(snapdir(LIVE) == live_snap0, "LIVE: the live Skyy_SkyyClasses folder was only read")
    print("\n%d checks, %d FAIL" % (OKS[0] + len(FAILS), len(FAILS)))
    for f in FAILS:
        print("  FAIL:", f[:400])
    if "--keep" not in sys.argv:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.exit(1 if FAILS else 0)


def snapdir(d):
    if not os.path.isdir(d):
        return {}
    return dict((os.path.relpath(os.path.join(r, f), d), open(os.path.join(r, f), "rb").read()) for r, _ds, fs in os.walk(d) for f in fs)


def part_st(env, me):
    if not os.path.isfile(os.path.join(LIVE, "config.properties")):
        print("ST: no live config - skipped")
        return
    home = os.path.join(SCRATCH, "st", "mods")
    shutil.rmtree(os.path.dirname(home), ignore_errors=True)
    os.makedirs(home)
    shutil.copytree(LIVE, os.path.join(home, "Skyy_SkyyClasses"))
    sdir = os.path.join(home, "Skyy_SkyyClasses")

    def state():
        return snapdir(sdir)

    def start(step):
        p = subprocess.run([sys.executable, me, "--s", "--home", home, "--step", step, "--dir", SCRATCH], env=env)
        j = os.path.join(home, "s-%s.json" % step)
        check(p.returncode == 0 and os.path.isfile(j), "ST: the %s start's child JVM ran" % step)
        return json.load(open(j)) if os.path.isfile(j) else {}
    s0 = state()
    t0 = s0["config.properties"].decode("latin-1")
    r1 = start("first")
    s1 = state()
    check(s1 == s0, "ST1: the first 0.1.17 start on the live copy writes NOTHING (config, history, log, players, ability files): %s"
          % sorted(set(s1) ^ set(s0)))
    live_m_cd = None
    for ln_ in t0.replace("\r", "").split("\n"):
        if ln_.startswith("ab.Meteor.walk.cooldown="):
            live_m_cd = ln_.split("=", 1)[1].strip()
    want_vals = {"M_CD": float(live_m_cd) if live_m_cd else 14.0, "M_MANA": 23.0, "S_MANA": 18.0, "PART": True, "UNLOCK_A1X": 30, "B_CD": 30.0,
                 "B_MANA": 16.0, "U_MANA": 20.0, "U_PULSE": 8, "TICK": 0.25, "MAX_ZONES": 2, "B_RATIO": 2.0}
    check(r1.get("vals") == want_vals and "ab.ManaBarrier" not in t0 and "ab.ShieldBubble" not in t0
          and (r1.get("gets") or {}).get("ab.ManaBarrier.walk.cooldown") == "30" and (r1.get("gets") or {}).get("ab.ShieldBubble.pulse") == "8"
          and (r1.get("gets") or {}).get("abil.maxZones") == "2" and r1.get("status", [""])[0] == "ok"
          and r1.get("mig") == "", "ST1: the live file has no R3 lines -> their defaults (Server Setup shows them); the R1 values as live; kit status ok: %s" % r1)
    r2 = start("second")
    check(state() == s0 and r2.get("vals") == r1.get("vals") and r2.get("summary") == r1.get("summary"), "ST2: the second start changes nothing and reads the same")
    r3 = start("set")
    s3 = state()
    t3 = s3["config.properties"].decode("latin-1")
    added = [x for x in t3.replace("\r", "").split("\n") if x not in t0.replace("\r", "").split("\n")]
    gone = [x for x in t0.replace("\r", "").split("\n") if x not in t3.replace("\r", "").split("\n")]
    check(r3.get("set", [None])[0] == "ok" and r3.get("after_set") == 20.0 and added == ["ab.ManaBarrier.walk.cooldown=20"] and not gone,
          "ST3: Server Setup -> Classes -> Ability numbers -> Mana Barrier cooldown 20: applied at once, ONE line added, every other line kept: %s %s" % (r3.get("set"), added))
    lg0 = s0.get("config-changes.log", b"")
    lg3 = s3.get("config-changes.log", b"")
    nl = lg3[len(lg0):].decode("utf8").strip().split("\n")
    check(lg3.startswith(lg0) and len(nl) == 1 and nl[0].split("\t")[3:8] == ["console", "ab.ManaBarrier.walk.cooldown", "30", "20", "ok"],
          "ST3: one config-changes.log line (Undo-able): %s" % nl)
    hist_new = [k for k in s3 if k not in s0 and k.startswith("config-history")]
    check(len(hist_new) == 1 and s3[hist_new[0]] == s0["config.properties"], "ST3: one History copy of the file before the change: %s" % hist_new)
    r4 = start("fourth")
    check(state() == s3 and r4.get("vals", {}).get("B_CD") == 20.0, "ST4: the next start reads the cooldown 20 back and writes nothing")
    print("ST. start twice on the live copy (%d player files): nothing written; Server Setup Mana Barrier cooldown 20 -> one line + one log line + one History "
          "copy; read back at the next start" % r1.get("keys", 0))


if __name__ == "__main__":
    main()
