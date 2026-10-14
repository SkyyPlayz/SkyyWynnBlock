"""SkyyClasses 0.1.22 - harness for THE ABILITY KEYS (Hytale 0.7 runes), ABILITY LEVELS + MODIFIERS and THE PANEL BRIDGES for SkyyTrees 0.3.7
(tools/classes_0_1_22_patch.py). Build first: python tools/classes_0_1_22_patch.py && python SkyyClasses/build_skyyclasses_0.1.22.py

    python SkyyClasses/test_skyyclasses_0.1.22.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Every JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch. Live save data is only READ / copied.
  OLD  test_skyyclasses_0.1.19.py on the 0.1.22 jar: the loadout bridge (L) + START TWICE on a scratch COPY of the live Skyy_SkyyClasses
       folder (ST: nothing written); its CC part needs the 0.1.18 jar (gone) and is skipped
  A    verify   every class loads + initialises with -Xverify:all (tools/harness_kit.py)
  C    compare  0.1.21 -> 0.1.22: the 11 new classes, only the planned classes change, non-class entries = manifest.json + the rune asset pack
  X    EXECUTED on test players / NPCs (the 0.1.18 engine stand-ins: a map-backed Store / CommandBuffer, the REAL EntityStatMap, real Damage
       objects, the REAL AbilTick; a stand-in ability-slot container behind the REAL InventoryComponent$AbilitySlots; REAL
       InteractionChainStartEvent / InteractionChain / InteractionContext / ItemStack objects):
       X1 the pure rules (uses per level, diminishing returns, modifier unlock / steps, the tree csv); X2 THE HOOK's decision (runeDecide);
       X3 THE HOOK (onRune on a real event: cancelled + cast a tick later through RuneCast, door 1); X4 REFUSAL through the hook (cooldown,
       no Mana, tree gate, keys off, roll); X5 a game rune on a Mage (blocked: cancelled, no cast, one hint) / abil.vanillaRunes; X6 THE MARKER
       FALLBACK (markerPress: dup within 700 ms, cast through RuneCast door 2); X7 THE MIRROR (runeWant, mirrorNeed, mirrorSet, runeTick
       -> MirrorTask, a stray rune, a vanilla rune kept, the guard onInv -> InvClean); X8 LEVELS BY USE (used: the counted use, the gap,
       echo / switched, the level-up line, the file); X9 a REAL Meteor through the key -> impact -> one counted use; X10 MODIFIERS (unlock,
       equip, the double rule, tree slots, the cast context, modifier level-up); X11 doAction (swap / pick / equip / unequip); X12 THE PANEL
       (class:fn:abilPanel Object[78], abilMods, abilDo, abilUnlock); X13 PROFILE SWITCH (levels / mods / slots per profile, the mirror
       follows); X14 M5 cooldowns clear on relog; X15 /cast stays (door 0) + abil.castCmd off; X16 Echo
  R21  test_skyyclasses_0.1.21.py's ability-line routing phase on the 0.1.22 jar (Abil.say unchanged)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, time, shutil, zipfile, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.22"
PKG = "com.skyy.classes."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-0.1.21.jar")
BASE = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "abiltree", "cl")))
SCRATCH = BASE if "--phase" in sys.argv else os.path.join(BASE, "h")
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
ASSETS = os.path.join(APPDATA, "Hytale", "install", "release", "package", "game", "latest", "Assets.zip")
T19 = os.path.join(HERE, "test_skyyclasses_0.1.19.py")
NEW_CLASSES = ["AbilModDefs", "AbilCtx", "AbilRuneSys", "AbilInvSys", "RuneCast", "MirrorTask", "InvClean", "AbilPanelFn", "AbilModsFn",
               "AbilDoFn", "AbilUnlockFn"]


def t21():
    spec = importlib.util.spec_from_file_location("test_skyyclasses_0_1_21", os.path.join(HERE, "test_skyyclasses_0.1.21.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_route21(out, jar, scratch, home):
    T = t21()
    T.run_ability(out, jar, scratch, home)


# ============================================================================================================ C: the 0.1.21 -> 0.1.22 compare
def run_compare22(out, jar, old_jar, pkg, expect, added):
    from jpype import JClass
    import re
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_
    pa, pb = pool_of(old_jar), pool_of(jar)
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def body(c_):
        d_ = {}
        for m_ in list(c_.getDeclaredMethods()) + list(c_.getDeclaredConstructors()):
            ca_ = m_.getMethodInfo().getCodeAttribute()
            t_ = []
            if ca_ is not None:
                it_ = ca_.iterator()
                cp_ = m_.getMethodInfo().getConstPool()
                while it_.hasNext():
                    p_ = it_.next()
                    t_.append(re.sub(r"^((?:if\w*|goto(?:_w)?)) -?\d+$", r"\1", re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, p_, cp_)))))
            d_[str(m_.getName()) + str(m_.getSignature())] = "\n".join(t_)
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature())
        return d_
    na, nb = HK.jar_classes(old_jar), HK.jar_classes(jar)
    K.eq(sorted(set(nb) - set(na)), sorted(pkg + a for a in added), "C: the classes added")
    K.eq(sorted(set(na) - set(nb)), [], "C: no class removed")
    diffs = {}
    for cn in sorted(set(na) & set(nb)):
        a_, b_ = body(pa.get(cn)), body(pb.get(cn))
        dd = sorted(k for k in set(a_) | set(b_) if a_.get(k) != b_.get(k))
        if dd:
            diffs[cn[len(pkg):]] = dd
    print("C. class compare 0.1.21 -> 0.1.22: %d classes identical, %d differ: %s" % (len(set(na) & set(nb)) - len(diffs), len(diffs), sorted(diffs)))
    extra = sorted(set(diffs) - set(expect))
    K.check(not extra, "C: only the planned classes change (unplanned: %s)" % extra)
    K.notes.append("C: changed %s" % {k: len(v) for k, v in diffs.items()})
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    changed = sorted(n for n in ea & eb if za.read(n) != zb.read(n))
    K.eq(changed, ["manifest.json"], "C: the only changed non-class entry is manifest.json")
    K.eq(sorted(ea - eb), [], "C: no non-class entry removed")
    new = sorted(eb - ea)
    runes = [n for n in new if n.startswith("Server/Item/Items/SkyyClasses/SkyyAbility_")]
    K.check(len(new) == 56 and len(runes) == 9 and all(n.startswith(("Server/", "Common/")) for n in new),
            "C: the new entries are the rune asset pack (56 files, 9 rune items): %d / %d" % (len(new), len(runes)))
    man = json.loads(zb.read("manifest.json"))
    K.check(man.get("IncludesAssetPack") is True and man.get("Version") == VERSION, "C: manifest IncludesAssetPack + version %s" % man.get("Version"))
    for n in runes:
        d = json.loads(zb.read(n))
        K.check(d["Quality"] == "Debug" and d["MaxStack"] == 1 and d["DropOnDeath"] is False and d["Ability"]["Cost"] == 0
                and d["Ability"]["CostType"] == "None" and d["Ability"]["Cast"].startswith("Root_SkyyAbility_"),
                "C: %s is a hidden, free, undroppable rune with our cast root" % n.rsplit("/", 1)[1])
    K.save()


# ============================================================================================================ X: executed
def run_exec(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JArray, JString, JImplements, JOverride, JObject, JFloat, JDouble, JLong, JInt, JBoolean
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls")
    os.makedirs(hcls, exist_ok=True)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    SCRATCH = scratch
    R = {"notes": K.notes}

    def ck(cond, what):
        K.check(bool(cond), what)

    Cls = JClass("java.lang.Class")
    # ---- the engine stand-ins (copied from test_skyyclasses_0.1.18.py run_n, N0)
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

    # ================================================================================================ 0.1.22 sections
    AW, AMD, ACX = C("AbilWorld"), C("AbilModDefs"), C("AbilCtx")
    Bool = JClass("java.lang.Boolean")
    tick = C("AbilTick")()
    now_ms = lambda: int(time.time() * 1000)

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    RUNES_LOADED = set(str(x) for x in AD.RUNE if str(x))
    A.ITEMS = Fn(lambda o: Bool.valueOf(str(o) in RUNES_LOADED))
    MARK_IX = dict((str(m), 100 + i) for i, m in enumerate(AD.MARK) if str(m))
    A.MARKS = Fn(lambda o: JInt(MARK_IX.get(str(o), -1)))
    TREE = {"csv": None}
    br.put("tree:fn:abil", Fn(lambda o: None if TREE["csv"] is None else JString(TREE["csv"])))
    NAMES_ = [str(x) for x in Defs.NAMES]
    ci_m, ci_p = NAMES_.index("Mage"), NAMES_.index("Priest")
    SK_M, SK_P = str(Defs.SKILLS[ci_m]), str(Defs.SKILLS[ci_p])
    mu, mr, mpr, mm, mpl, mmsc = player(1, 0.5, 64.0, 0.5, "Mage1")
    pu, pr_r, ppr, pm, ppl, pmsc = player(2, 3.5, 64.0, 0.5, "Priest1")
    setclass(mu, "Mage")
    setclass(pu, "Priest")
    LEVEL[(str(mu), SK_M)] = 30
    LEVEL[(str(pu), SK_P)] = 30
    A.HAND = Hand()
    A.AIM = Aim()
    A.NEAR = Near()
    HANDS[1] = "Weapon_Staff_Wood"
    HANDS[2] = "Weapon_Wand_Iron"
    AIMS["spot"] = [10.5, 64.0, 0.5]
    ID = dict((str(AD.IDS[i]), i) for i in range(len(AD.IDS)))
    METEOR, MANAB, SACRED = ID["Meteor"], ID["ManaBarrier"], ID["SacredHeal"]
    R_MET, R_MB = str(AD.RUNE[METEOR]), str(AD.RUNE[MANAB])

    def mana(m_, v):
        m_.setStatValue(MANA, JFloat(v))
        m_.setStatValue(STAM, JFloat(50.0))

    def reset_m():
        AS.clearCd(str(mu))
        AS.clearCd(str(mu) + "-p2")
        mana(mm, 400.0)
        unthrottle()
        said()
        AS.LASTKEY.clear()
        AS.LASTHOOK.clear()
        AS.TREEC.clear()

    # ---------------- X1 the pure rules
    AMt = C("AbilMath")
    ck([int(AMt.usesFor(n, 4.5, 1.5)) for n in (1, 2, 3, 10)] == [0, 13, 23, 142], "X1: uses for level n = round(4.5 x n ^ 1.5) (2 -> 13, 3 -> 23, 10 -> 142)")
    ck([int(AMt.levelOf(u_, 25, 4.5, 1.5)) for u_ in (0, 12, 13, 35, 36, 10 ** 9)] == [1, 1, 2, 2, 3, 25], "X1: levelOf (13 uses = Lv 2, 36 = Lv 3, the cap 25)")
    ck([round(float(AMt.bonusPct(l_, 2.0, 10, 20)), 3) for l_ in (1, 2, 10, 11, 20, 21, 25)] == [0.0, 2.0, 18.0, 19.0, 28.0, 28.5, 30.5],
       "X1: diminishing returns - +2 % a level to 10, +1 % to 20, +0.5 % after (Lv 25 = +30.5 %)")
    ck([int(AMD.unlockAt(k_)) for k_ in range(5)] == [2, 4, 6, 8, 10] and int(AMD.unlockAt(5)) == 12, "X1: modifiers unlock at ability Lv 2 / 4 / 6 / 8 / 10")
    ck([int(AMD.modLevel(u_)) for u_ in (0, 9, 10, 29, 30, 60, 100, 5000)] == [1, 1, 2, 2, 3, 4, 5, 5] and int(AMD.modNext(25)) == 5 and int(AMD.modNext(100)) == 0,
       "X1: modifier levels by use (10 / 30 / 60 / 100 uses), modNext")
    ck(bool(AMD.csvHas("A1,T4=10,PB2", "T4")) and not bool(AMD.csvHas("A1,T4=10", "A2")) and float(AMD.csvAmt("A1,T4=10", "T4", 3.0)) == 10.0
       and float(AMD.csvAmt("A1,T4", "T4", 3.0)) == 3.0 and float(AMD.csvAmt("A1", "T4", 3.0)) == 0.0, "X1: the tree csv (node, node=amount)")
    ck([int(A.lineOf(i_)) for i_ in range(5)] == [1, 2, 3, 4, 4], "X1: ability lines A1-A4 (both Ability 1 alts on A4)")

    # ---------------- X2 the hook's decision
    reset_m()
    t0 = now_ms()
    D = lambda u_, ci_, k_, held, sec, t: str(A.runeDecide(u_, ci_, k_, held, sec, t))
    ABSEC = int(JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent").ABILITIES_SECTION_ID)
    ci_a = NAMES_.index("Archer")
    ck(D(mu, ci_m, 0, R_MET, ABSEC, t0) == "cast", "X2: our rune on Ability 2 -> cast")
    ck(D(mu, ci_m, 0, R_MET, ABSEC, t0 + 50) == "repeat", "X2: the same key again within 120 ms -> repeat (the double-fire guard)")
    ck(D(mu, ci_m, 0, R_MET, ABSEC, t0 + 300) == "cast", "X2: the same key after 120 ms -> cast")
    ck(D(mu, ci_m, 1, R_MB, ABSEC, t0 + 301) == "cast", "X2: the other key is its own guard")
    ck(D(mu, ci_m, 0, "Rune_Fireball", ABSEC, t0 + 900) == "vanilla", "X2: a game rune in the ability slots of a Mage -> vanilla (blocked)")
    ck(D(mu, ci_m, 0, "Weapon_Staff_Wood", 0, t0 + 1300) == "ignore", "X2: a weapon's own Ability 2 move (not a rune slot) -> ignore")
    ck(D(mu, ci_a, 0, "Rune_Fireball", ABSEC, t0 + 1700) == "ignore", "X2: an Archer (no class abilities) -> ignore (game runes work)")
    ck(D(mu, ci_m, 2, R_MET, ABSEC, t0 + 2100) == "ignore" and D(None, ci_m, 0, R_MET, ABSEC, t0) == "ignore", "X2: a bad key / no player -> ignore")
    AC.VAN_RUNES = True
    ck(D(mu, ci_m, 0, "Rune_Fireball", ABSEC, t0 + 2500) == "allow" and D(mu, ci_m, 0, R_MET, ABSEC, t0 + 2900) == "cast",
       "X2: abil.vanillaRunes ON -> a game rune is allowed, ours still casts")
    AC.VAN_RUNES = False
    AC.RUNE_KEYS = False
    ck(D(mu, ci_m, 0, R_MET, ABSEC, t0 + 3300) == "ignore", "X2: abil.runeKeys OFF -> ignore")
    AC.RUNE_KEYS = True

    # ---------------- X3 THE HOOK on a real event
    ISc = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    ICHc = JClass("com.hypixel.hytale.server.core.entity.InteractionChain")
    ICXc = JClass("com.hypixel.hytale.server.core.entity.InteractionContext")
    ICSEc = JClass("com.hypixel.hytale.server.core.modules.interaction.event.InteractionChainStartEvent")
    ITc = JClass("com.hypixel.hytale.protocol.InteractionType")

    def stack(id_, q=1):
        s_ = U.allocateInstance(ISc.class_)
        setf(s_, ISc, "itemId", id_)
        setf(s_, ISc, "quantity", JInt(q))
        return s_

    def event(type_, held, sec):
        cx_ = U.allocateInstance(ICXc.class_)
        if held is not None:
            setf(cx_, ICXc, "heldItem", stack(held))
        setf(cx_, ICXc, "heldItemSectionId", JInt(sec))
        ch_ = U.allocateInstance(ICHc.class_)
        setf(ch_, ICHc, "type", getattr(ITc, type_))
        setf(ch_, ICHc, "context", cx_)
        return ICSEc(ch_)
    reset_m()
    TBf.EVENTS.clear()
    ev = event("Ability2", R_MET, ABSEC)
    r0 = int(A.RUNES)
    hk = str(A.onRune(ev, 0, mr, tst, tbuf))
    lr = str(A.LAST_RUNE)
    ck(hk == "cast" and bool(ev.isCancelled()), "X3: the hook takes our rune press: the chain is CANCELLED (the engine sends the client its cancel): %s" % hk)
    ck(lr.startswith("ok:Meteor ") and lr.endswith(" key") and int(A.RUNES) == r0 + 1, "X3: ... and the cast runs through RuneCast (door 1): %s" % lr)
    ck(sv(mm, MANA) < 400.0 and int(AS.left(str(mu), "Meteor", now_ms())) > 0, "X3: Mana paid, the cooldown armed (Mana %s)" % sv(mm, MANA))
    sd = said()
    ck(sd and sd[0].startswith("Meteor! -"), "X3: the cast line: %s" % sd[:1])
    aw = AW.of("abil-test")
    ck(int(aw.size()) >= 1, "X3: the impact job is queued (%d)" % int(aw.size()))
    ev2 = event("Ability3", R_MB, ABSEC)
    hk2 = str(A.onRune(ev2, 1, mr, tst, tbuf))
    ck(hk2 == "cast" and bool(ev2.isCancelled()) and str(A.LAST_RUNE).startswith("ok:ManaBarrier ") and str(A.LAST_RUNE).endswith(" key"),
       "X3: Ability 3 -> the second primary (Mana Barrier): %s" % A.LAST_RUNE)
    said()
    ev3 = event("Primary", "Weapon_Staff_Wood", 0)
    ck(str(A.onRune(ev3, 0, mr, tst, tbuf)) == "ignore" and not bool(ev3.isCancelled()), "X3: a weapon press -> ignored, NOT cancelled")
    ev4 = event("Ability2", R_MET, ABSEC)
    ck(str(A.onRune(ev4, 0, pr_r, tst, tbuf)) == "cast" and bool(ev4.isCancelled()), "X3: a Priest pressing a rune the Mage owns -> cancelled + cast attempt")
    ck(not str(A.LAST_RUNE).startswith("ok:Meteor"), "X3: ... the Priest's own slot casts, never the Mage's Meteor: %s" % A.LAST_RUNE)
    said()
    # the system wrapper itself: a null chunk / another event type does nothing
    rs = C("AbilRuneSys")()
    rs.handle(0, None, tst, tbuf, event("Ability2", R_MET, ABSEC))
    ck(not bool(C("AbilRuneSys").FAILED_ONCE), "X3: AbilRuneSys.handle with no chunk returns quietly")

    # ---------------- X4 refusals through the hook
    time.sleep(0.13)
    ev = event("Ability2", R_MET, ABSEC)
    hk = str(A.onRune(ev, 0, mr, tst, tbuf))
    sd = said()
    ck(hk == "cast" and bool(ev.isCancelled()) and str(A.LAST_RUNE) == "cooldown" and sd and "Meteor is ready in" in sd[0],
       "X4: REFUSED (cooldown) through the key: cancelled, nothing cast, the line: %s %s" % (A.LAST_RUNE, sd))
    reset_m()
    mana(mm, 1.0)
    time.sleep(0.13)
    A.onRune(event("Ability2", R_MET, ABSEC), 0, mr, tst, tbuf)
    sd = said()
    ck(str(A.LAST_RUNE) == "mana" and sv(mm, MANA) == 1.0 and sd and sd[0].startswith("Not enough Mana for Meteor"), "X4: no Mana -> refused, nothing spent: %s" % sd)
    reset_m()
    TREE["csv"] = "T6=5"
    ck(str(A.runeCast(mpr, 0, 1)) == "tree" and "enable Meteor in your class tree first: /tree class, node A1" in " ".join(said()),
       "X4: class trees on, A1 not bought -> refused 'enable Meteor in your class tree first' (nothing spent)")
    ck(list(A.runeWant(mu)) == ["", ""], "X4: ... and no rune is wanted in the slots")
    TREE["csv"] = "A1"
    reset_m()
    ck(str(A.runeCast(mpr, 0, 1)).startswith("ok:Meteor") and list(A.runeWant(mu)) == [R_MET, ""], "X4: A1 bought -> Meteor casts; only its rune is wanted")
    AC.TREE_GATE = False
    AS.TREEC.clear()
    ck(list(A.runeWant(mu)) == [R_MET, R_MB], "X4: abil.treeGate OFF -> both runes wanted")
    AC.TREE_GATE = True
    TREE["csv"] = None
    AS.TREEC.clear()
    ck(list(A.runeWant(mu)) == [R_MET, R_MB], "X4: SkyyTrees absent / class trees off (no csv) -> no gate")
    reset_m()
    AC.RUNE_KEYS = False
    ck(str(A.runeCast(mpr, 0, 1)) == "keysoff" and str(A.runeCast(mpr, 0, 2)) == "keysoff", "X4: abil.runeKeys OFF -> the key and the marker do nothing")
    AC.RUNE_KEYS = True
    ms_ = mmsc.getMovementStates()
    ms_.rolling = True
    AC.ROLL_CAST = False
    ck(str(A.runeCast(mpr, 0, 1)) == "roll" and "Not while rolling" in " ".join(said()), "X4: rolling + abil.rollCast OFF -> refused")
    AC.ROLL_CAST = True
    reset_m()
    rr = str(A.runeCast(mpr, 0, 1))
    ck(rr.startswith("ok:Meteor") and "shape=sprint" in rr, "X4: rolling + abil.rollCast ON -> cast (a roll counts as sprinting = Comet): %s" % rr)
    ms_.rolling = False
    said()

    # ---------------- X5 a game rune on a Mage
    reset_m()
    time.sleep(0.13)
    ev = event("Ability2", "Rune_Fireball", ABSEC)
    AS.VANTOLD.clear()
    A.LAST_RUNE = "none"
    vb0 = int(A.VANBLOCK)
    hk = str(A.onRune(ev, 0, mr, tst, tbuf))
    sd = said()
    ck(hk == "vanilla" and bool(ev.isCancelled()) and str(A.LAST_RUNE) == "none" and int(A.VANBLOCK) == vb0 + 1,
       "X5: a game rune on a Mage -> BLOCKED (Skyy M2): cancelled, no class cast: %s" % A.LAST_RUNE)
    ck([x for x in sd if "Game runes are blocked for Mages" in x and "Rune_Fireball" in x], "X5: ... one hint line: %s" % sd)
    time.sleep(0.13)
    reset_m()
    A.onRune(event("Ability2", "Rune_Fireball", ABSEC), 0, mr, tst, tbuf)
    ck(not [x for x in said() if "Game runes are blocked" in x], "X5: the hint once per 30 s")

    # ---------------- X6 the marker fallback
    reset_m()
    t1 = now_ms()
    AS.LASTHOOK.put(mu, JLong(t1))
    f0, d0 = int(A.FALLBACKS), int(A.FB_DUP)
    ck(str(A.markerPress(mpr, mu, 0, world, t1 + 200)) == "dup" and int(A.FB_DUP) == d0 + 1, "X6: the marker within 700 ms of a hook press -> dup (no second cast)")
    lr0 = str(A.LAST_RUNE)
    ck(str(A.markerPress(mpr, mu, 0, world, t1 + 900)) == "cast" and int(A.FALLBACKS) == f0 + 1, "X6: the marker alone (the hook did not fire) -> cast")
    ck(str(A.LAST_RUNE).startswith("ok:Meteor") and str(A.LAST_RUNE).endswith(" marker"), "X6: ... through RuneCast door 2: %s" % A.LAST_RUNE)
    said()

    # ---------------- X7 THE MIRROR (the ability slots)
    ICc = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    IS_ = "com.hypixel.hytale.server.core.inventory.ItemStack"
    TR_ = "com.hypixel.hytale.server.core.inventory.transaction."
    TIc = stub("TSlots", "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
               ["public " + IS_ + "[] s = new " + IS_ + "[4];"],
               ["public short getCapacity() { return (short) s.length; }",
                "public " + IS_ + " getItemStack(short i) { return s[i]; }",
                "public " + TR_ + "SlotTransaction removeItemStackFromSlot(short i) { s[i] = null; return null; }",
                "public " + TR_ + "ItemStackSlotTransaction addItemStackToSlot(short i, " + IS_ + " it) { if (s[i] == null) s[i] = it; return null; }",
                "protected Object readAction(java.util.function.Supplier a) { return a.get(); }",
                "protected Object readAction(java.util.function.Function a, Object b) { return a.apply(b); }",
                "protected Object writeAction(java.util.function.Supplier a) { return a.get(); }",
                "protected Object writeAction(java.util.function.Function a, Object b) { return a.apply(b); }",
                "protected " + IS_ + " internal_getSlot(short i) { return s[i]; }",
                "protected " + IS_ + " internal_setSlot(short i, " + IS_ + " it) { " + IS_ + " o = s[i]; s[i] = it; return o; }",
                "protected " + IS_ + " internal_removeSlot(short i) { " + IS_ + " o = s[i]; s[i] = null; return o; }"],
               ctor="public TSlots() { super(); }")
    ABSc = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$AbilitySlots")
    INVCc = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent")
    try:
        setf(em, EMc, gfield("com.hypixel.hytale.server.core.modules.entity.EntityModule", "getAbilitySlotsInventoryComponentType"),
             reg_.registerComponent(ABSc.class_, Sup(lambda: None)))
    except Exception as e_:
        K.notes.append("X7 ability slots type: %s" % str(e_)[:200])
    slots_c = TIc()
    abs_ = U.allocateInstance(ABSc.class_)
    setf(abs_, INVCc, "inventory", slots_c)
    put(mr, ABSc.getComponentType(), abs_)

    def ids():
        return [("" if x is None else str(x.getItemId())) for x in slots_c.s]
    reset_m()
    ck(A.abilSlots(tst, mr) is not None and int(A.mirrorNeed(slots_c, A.runeWant(mu))) == 1, "X7: the REAL AbilitySlots component read; empty slots -> a write is needed")
    real_stack = None
    try:
        real_stack = ISc(R_MET, 1)
    except Exception as e_:
        K.notes.append("X7: new ItemStack(rune, 1) in the bare JVM: %s" % str(e_)[:160])
    m0 = int(A.MIRRORS)
    got = str(A.mirrorSet(mpr, mu))
    ck(got == "+0 +3" and ids() == [R_MET, "", "", R_MB] and int(A.MIRRORS) == m0 + 1, "X7: mirrorSet puts Meteor in slot 0 (Ability 2), Mana Barrier in slot 3 (Ability 3): %s %s" % (got, ids()))
    ck(int(A.mirrorNeed(slots_c, A.runeWant(mu))) == 0 and str(A.mirrorSet(mpr, mu)) == "", "X7: right already -> nothing to do")
    slots_c.s[1] = stack(R_MET)
    ck(int(A.mirrorNeed(slots_c, A.runeWant(mu))) == 1 and str(A.mirrorSet(mpr, mu)) == "-1" and ids()[1] == "", "X7: a stray copy of our rune in slot 1 is removed")
    slots_c.s[0] = stack("Rune_Fireball")
    slots_c.s[3] = None
    got = str(A.mirrorSet(mpr, mu))
    ck(got == "+3" and ids() == ["Rune_Fireball", "", "", R_MB], "X7: a game rune in slot 0 is never touched (ours waits); slot 3 refilled: %s %s" % (got, ids()))
    slots_c.s[0] = None
    # runeTick -> the MirrorTask on the world thread (the stand-in world runs it at once)
    AS.MIRROR.clear()
    A.runeTick(mpr, mu, mr, tst, now_ms())
    rec = AS.MIRROR.get(mu)
    ck(ids()[0] == R_MET and rec is not None and str(rec[0]) == R_MET and int(rec[4]) == MARK_IX[str(AD.MARK[METEOR])],
       "X7: runeTick sees slot 0 empty -> MirrorTask fills it; the record holds the wanted runes + their marker effects: %s" % ids())
    A.runeTick(mpr, mu, mr, tst, now_ms())
    ck(ids() == [R_MET, "", "", R_MB], "X7: the next tick within 2 s does nothing")
    # the guard: an inventory change on the ability slots -> look again at once; one of our runes elsewhere -> InvClean
    ICEc = JClass("com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent")
    ice = U.allocateInstance(ICEc.class_)
    setf(ice, ICEc, "componentType", ABSc.getComponentType())
    ck(str(A.onInv(ice, mr, tbuf)) == "slots" and int(AS.MIRROR.get(mu)[2]) == 0, "X7: the guard - ability slots changed -> the mirror looks at the next tick")
    other_c = TIc()
    other_c.s[2] = stack(R_MET)
    ice2 = U.allocateInstance(ICEc.class_)
    setf(ice2, ICEc, "itemContainer", other_c)
    ck(str(A.onInv(ice2, mr, tbuf)) == "clean" and AS.CLEANQ.get(mu) is None, "X7: our rune in another container -> InvClean queued and run (the queue mark cleared)")
    ck(int(A.cleanIc(other_c)) == 1 and other_c.s[2] is None, "X7: cleanIc removes our rune from a container (counted)")
    other_c.s[1] = stack("Rune_Fireball")
    ck(int(A.cleanIc(other_c)) == 0 and other_c.s[1] is not None, "X7: ... never a game rune")
    ice3 = U.allocateInstance(ICEc.class_)
    setf(ice3, ICEc, "itemContainer", other_c)
    ck(A.onInv(ice3, mr, tbuf) is None, "X7: a container with no rune of ours -> nothing")

    # ---------------- X8 LEVELS BY USE
    reset_m()
    k_ = str(mu)
    AC.USE_EVERY = 0.0
    for i_ in range(12):
        A.used(mu, k_, METEOR, None)
    said()
    r13 = str(A.used(mu, k_, METEOR, None))
    sd = said()
    ck(r13 == "use 13 level 2" or r13.startswith("use 13 level 2"), "X8: the 13th counted use -> Meteor Lv 2: %s" % r13)
    ck(sd and sd[0] == "Meteor reached Lv 2! +2 % damage. New modifier: Power+ - equip it in /tree class.", "X8: the level-up line names the new modifier: %s" % sd)
    ck(str(AS.load(k_).getProperty("u.Meteor")) == "13" and AS.DIRTYAT.get(k_) is not None, "X8: kept in memory (u.Meteor=13), marked for the 30 s flush")
    f_ = os.path.join(home, "abilities", k_ + ".properties")
    AS.flushOld(now_ms() + 60000, 30000)
    ck(os.path.isfile(f_) and "u.Meteor=13" in open(f_).read() and AS.DIRTYAT.get(k_) is None, "X8: the flush writes it (abilities/<pkey>.properties)")
    AC.USE_EVERY = 3.0
    AS.LASTUSE.clear()
    ck(str(A.used(mu, k_, METEOR, None)) == "use 14" and str(A.used(mu, k_, METEOR, None)) == "soon", "X8: one counted use per ability per abil.useEvery (3 s)")
    ecx = ACX()
    ecx.echo = True
    ck(str(A.used(mu, k_, METEOR, ecx)) == "echo" and str(A.used(mu, k_ + "-p9", METEOR, None)) == "switched", "X8: an echo never counts; a cast from a profile you left never counts")
    AC.LEVELS = False
    ck(str(A.used(mu, k_, METEOR, None)) == "off" and int(A.alvl(500)) == 1, "X8: abil.levels OFF -> no counting, every ability Lv 1")
    AC.LEVELS = True
    ck(str(A.levelLine(mu, METEOR)) == "Lv 2 - 1 / 23 uses", "X8: the level text: %s" % A.levelLine(mu, METEOR))

    # ---------------- X9 a REAL Meteor through the key -> the impact -> one counted use
    reset_m()
    AS.LASTUSE.clear()
    n30 = npc(30, 11.0, 64.0, 0.5)
    NEARL[:] = [n30]
    aw.jobs.clear()
    time.sleep(0.13)
    A.onRune(event("Ability2", R_MET, ABSEC), 0, mr, tst, tbuf)
    lr = str(A.LAST_RUNE)
    for j_ in list(aw.jobs):
        j_.at = now_ms() - 10
    aw.lastNs = 0
    TBf.EVENTS.clear()
    tick.tick(JFloat(0.05), 0, None, tst, tbuf)
    ck(lr.startswith("ok:Meteor") and " lv=2" in lr and TBf.EVENTS.size() >= 1, "X9: the key cast (Lv 2 shows) lands on the NPC: %s, %d hits" % (lr, TBf.EVENTS.size()))
    ck(str(AS.load(k_).getProperty("u.Meteor")) == "15", "X9: the hit counted ONE use (14 -> 15): %s" % AS.load(k_).getProperty("u.Meteor"))
    dmg_lv2 = round(float(TBf.EVENTS.get(0)[1].getAmount()), 3) if TBf.EVENTS.size() else 0
    ck(dmg_lv2 == round(150.0 * 1.02, 3), "X9: Lv 2 = +2 %% damage (150 -> 153): %s" % dmg_lv2)
    said()

    # ---------------- X10 MODIFIERS
    reset_m()
    def setp(k__, kv):
        AS.set(k__, JArray(JString)(list(kv.keys())), JArray(JString)([None if v is None else str(v) for v in kv.values()]))
    EQ = lambda slot, mod, csv=None, cok=False: str(A.equipMod(mu, "Meteor", slot, mod, csv, cok))
    setp(k_, {"u.Meteor": 0})
    ck(EQ(0, "Power").startswith("-Power+ unlocks at Meteor Lv 2 (Lv 1 now)"), "X10: a modifier locked below its unlock level: %s" % EQ(0, "Power"))
    setp(k_, {"u.Meteor": int(AMt.levelStart(4, 4.5, 1.5))})
    ck(int(A.alvl(int(AMt.levelStart(4, 4.5, 1.5)))) == 4, "X10: Meteor Lv 4")
    ck(EQ(0, "Power") == "+Meteor: slot 1 Power+, slot 2 empty.", "X10: equip Power+ in slot 1: %s" % EQ(0, "Power"))
    ck(EQ(1, "Power") == "-Power+ can go in both slots from modifier Lv 2.", "X10: doubling needs modifier Lv 2")
    ck(EQ(1, "Slow") == "-Slow is not a Meteor modifier.", "X10: not this ability's modifier")
    ck(EQ(1, "Split").startswith("-Split unlocks at Meteor Lv 6"), "X10: Split (3rd) unlocks at Lv 6")
    ck(EQ(2, "Radius") == "-Pick modifier slot 1 or 2.", "X10: a bad slot")
    setp(k_, {"m.Meteor.Power": 10})
    ck(EQ(1, "Power") == "+Meteor: slot 1 Power+, slot 2 Power+.", "X10: Power+ Lv 2 -> DOUBLED (both slots)")
    cx_ = A.ctxFor(mu, k_, METEOR, 0, None)
    ck(int(cx_.m0) == int(AMD.POWER) and int(cx_.m1) == int(AMD.POWER) and int(cx_.eff(AMD.POWER)) == 4,
       "X10: the cast context - doubled Power+ Lv 2 counts 2 x 2 = 4 levels")
    ck(round(float(cx_.main), 4) == round(float(A.lvlMult(4)) * 1.20, 4), "X10: main = level (+6 %%) x Power+ (+20 %%) = %s" % cx_.main)
    setp(k_, {"u.Meteor": int(AMt.levelStart(10, 4.5, 1.5)), "m.Meteor.Split": 10})
    ck(EQ(0, "Split") == "+Meteor: slot 1 Split, slot 2 Power+." and EQ(1, "Split") == "-Split cannot be equipped twice.", "X10: a non-stackable modifier never doubles")
    ck(str(A.equipMod(mu, "Meteor", 1, "Radius", "A1,M1A", False)) == "-Modifier slot 2 of Meteor is not open - unlock M1B in your class tree.",
       "X10: the tree gives the slots (M1A only -> slot 2 closed)")
    ck(int(A.modSlots("A1,M1A,M1B", METEOR)) == 2 and int(A.modSlots("A1", METEOR)) == 0 and int(A.modSlots(None, METEOR)) == 2, "X10: modSlots from the tree")
    eqs = list(A.equipped(AS.load(k_), METEOR, 10, 1))
    ck(eqs == [int(AMD.SPLIT), -1], "X10: with 1 tree slot only slot 1 works: %s" % eqs)
    COMBAT[str(mu)] = now_ms() + 5000
    ck(EQ(0, "Radius").startswith("-Leave combat first"), "X10: no changes in combat")
    del COMBAT[str(mu)]
    ck(EQ(0, "") == "+Meteor: slot 1 empty, slot 2 Power+." and EQ(0, "") == "-Modifier slot 1 of Meteor is empty.", "X10: unequip")
    # a use with a doubled stackable modifier: +2 modifier uses; the modifier level-up line
    setp(k_, {"e.Meteor": "Power,Power", "m.Meteor.Power": 28})
    AS.LASTUSE.clear()
    said()
    ru = str(A.used(mu, k_, METEOR, None))
    sd = said()
    ck(str(AS.load(k_).getProperty("m.Meteor.Power")) == "30" and "mods Power+ Lv 3" in ru and [x for x in sd if x == "Meteor modifier up: Power+ Lv 3."],
       "X10: a doubled modifier gains 2 uses a counted use (28 -> 30 = Lv 3, the line): %s %s" % (ru, sd))
    AC.MODS_ON = False
    cx_ = A.ctxFor(mu, k_, METEOR, 0, None)
    ck(int(cx_.m0) == -1 and str(A.equipMod(mu, "Meteor", 0, "Power", None, False)).startswith("-Ability modifiers are switched off"), "X10: mods.on OFF -> nothing applies")
    AC.MODS_ON = True
    # a real /cast shows them
    reset_m()
    rr = str(A.cast(mpr, tst, mr, world, "1"))
    ck(rr.startswith("ok:Meteor") and " m0=Power3 m1=Power3" in rr and " lv=10" in rr, "X10: the cast carries its level + modifiers: %s" % rr)
    said()

    # ---------------- X11 doAction
    reset_m()
    DO = lambda act, a=None, b=None, csv=None: str(A.doAction(mu, act, a, b, csv))
    sl0 = [str(x) for x in AS.slots(k_, ci_m)]
    r_ = DO("swap", "0", "1")
    sl1 = [str(x) for x in AS.slots(k_, ci_m)]
    ck(r_.startswith("+") and sl1[0] == sl0[1] and sl1[1] == sl0[0], "X11: swap 0 1: %s %s -> %s" % (r_, sl0, sl1))
    ck(list(A.runeWant(mu)) == [R_MB, R_MET], "X11: ... the runes follow (Mana Barrier now on Ability 2)")
    DO("swap", "0", "1")
    ck(DO("swap", "0", "x") == "-Pick two slots." and DO("dance") == "-Unknown action.", "X11: bad arguments")
    pk0 = str(AS.pick(k_))
    r_ = DO("pick", "B" if pk0 == "A" else "A")
    ck(r_.startswith("+Your Ability 1 alt is now"), "X11: pick the other Ability 1 alt: %s" % r_)
    DO("pick", pk0)
    LEVEL[(str(mu), SK_M)] = 12
    ck(DO("pick", "B").startswith("-You choose your Ability 1 alt at %s 30" % SK_M), "X11: the alt pick needs the Lv 30 unlock")
    LEVEL[(str(mu), SK_M)] = 30
    ck(DO("equip", "Meteor", "0:Radius") == "+Meteor: slot 1 Radius+, slot 2 Power+." and DO("unequip", "Meteor", "0") == "+Meteor: slot 1 empty, slot 2 Power+.",
       "X11: equip / unequip through abilDo")
    ck(DO("equip", "Meteor", "Radius") == "-Usage: equip <ability> <slot>:<modifier>." and DO("equip", "SacredHeal", "0:Power") == "-That is not one of your abilities.",
       "X11: bad equip / another class's ability")
    ck(str(A.doAction(JClass("java.util.UUID").randomUUID(), "swap", "0", "1", None)) == "-Your class has no abilities yet.", "X11: no class")

    # ---------------- X12 THE PANEL (the bridges SkyyTrees calls)
    reset_m()
    PF, MF, DF, UF = C("AbilPanelFn")(), C("AbilModsFn")(), C("AbilDoFn")(), C("AbilUnlockFn")()
    o = PF.apply(mu)
    ck(o is not None and len(o) == 78 and str(o[0]) == "ok" and str(o[1]) == "Mage" and int(o[2]) == 30 and str(o[7]) == "1,10,20,30",
       "X12: class:fn:abilPanel(UUID) -> Object[78] ok / Mage / 30 / unlocks 1,10,20,30")
    ck(str(o[12]) == "Meteor" and str(o[13]) == "Meteor" and str(o[14]) == R_MET and bool(o[15]) and bool(o[16]) and int(o[17]) == 1 and int(o[18]) == 10,
       "X12: card 1 = Meteor, its rune, owned, enabled, line 1, Lv 10")
    ck(str(o[22]) == "" and str(o[24]) == "Power+" and int(o[25]) == 3 and int(o[26]) == 2 and str(o[27]) == "ready",
       "X12: card 1's modifiers by DISPLAY name (slot 2 Power+ Lv 3), 2 slots, ready: %s" % [str(x) for x in o[22:28]])
    o2 = PF.apply(JArray(JObject)([mu, JString("A1,M1A")]))
    ck(bool(o2[16]) and not bool(o2[12 + 16 + 4]) and str(o2[12 + 16 + 15]) == "disabled" and int(o2[26]) == 1 and bool(o2[6]),
       "X12: with this page's tree csv: line 2 not enabled -> 'disabled'; Meteor has 1 modifier slot; the gate shows: %s" % [str(o2[i_]) for i_ in (6, 16, 26, 32, 43)])
    ck(PF.apply(JString("x")) is None and str(PF.apply(JClass("java.util.UUID").randomUUID())[0]) == "noclass", "X12: bad input -> null; no class -> noclass")
    rows = MF.apply(JArray(JObject)([mu, JString("Meteor"), JString("A1,M1A,M1B")]))
    ck(rows is not None and len(rows) == 1 + int(AMD.count(METEOR)) and str(rows[0]).startswith("Meteor|Meteor|10|"), "X12: class:fn:abilMods -> header + %d rows" % (len(rows) - 1 if rows else -1))
    pw = str(rows[1]).split("|")
    ck(pw[0] == "Power" and pw[1] == "Power+" and pw[2] == "2" and pw[3] == "1" and pw[4] == "3" and pw[8] == "1" and pw[11] == "1",
       "X12: the Power row: unlocked at 2, Lv 3, stackable, can double: %s" % pw)
    ech = str(rows[5]).split("|")
    ck(ech[0] == "Echo" and ech[3] == "1" and ech[9].startswith("again at 20 % after 1 s"), "X12: the Echo row (unlocked at Lv 10): %s" % ech)
    ck(str(DF.apply(JArray(JObject)([mu, JString("equip"), JString("Meteor"), JString("0:Echo"), JString("A1,M1A,M1B")]))) == "+Meteor: slot 1 Echo, slot 2 Power+.",
       "X12: class:fn:abilDo equips through the bridge")
    ul = [UF.apply(JInt(x)) for x in (1, 2, 3, 4)]
    ck([int(x) for x in ul] == [1, 10, 20, 30] and UF.apply(JInt(5)) is None and UF.apply(JString("x")) is None,
       "X12: class:fn:abilUnlock line 1-4 -> 1 / 10 / 20 / 30 (Skyy's unlock levels); a bad line -> null")

    # ---------------- X13 PROFILE SWITCH
    reset_m()
    PROFKEY[str(mu)] = str(mu) + "-p2"
    k2 = str(mu) + "-p2"
    o = PF.apply(mu)
    ck(int(o[18]) == 1 and str(o[22]) == "" and str(o[24]) == "", "X13: profile 2 starts at Meteor Lv 1, no modifiers (levels + mods are per profile)")
    ck(str(A.equipMod(mu, "Meteor", 0, "Power", None, False)).startswith("-Power+ unlocks at Meteor Lv 2"), "X13: profile 2's own level gates its modifiers")
    AS.LASTUSE.clear()
    A.used(mu, k2, METEOR, None)
    ck(str(AS.load(k2).getProperty("u.Meteor")) == "1" and str(AS.load(k_).getProperty("u.Meteor")) != "1", "X13: a use counts on the active profile only")
    DO("swap", "0", "1")
    ck(list(A.runeWant(mu)) == [R_MB, R_MET], "X13: profile 2's own slot order -> its own runes")
    AS.MIRROR.clear()
    A.runeTick(mpr, mu, mr, tst, now_ms())
    ck(ids()[0] == R_MB and ids()[3] == R_MET, "X13: the mirror swaps the rune slots for the new profile: %s" % ids())
    del PROFKEY[str(mu)]
    AS.MIRROR.clear()
    A.runeTick(mpr, mu, mr, tst, now_ms())
    ck(ids()[0] == R_MET and ids()[3] == R_MB, "X13: back to profile 1 -> its runes again: %s" % ids())

    # ---------------- X14 M5: cooldowns clear on relog
    AS.arm(k_, "Meteor", now_ms(), 14000)
    AS.arm(k2, "Meteor", now_ms(), 14000)
    AS.arm(str(pu), "SacredHeal", now_ms(), 14000)
    n_ = int(AS.clearCdOf(mu))
    ck(n_ == 2 and int(AS.left(k_, "Meteor", now_ms())) == 0 and int(AS.left(k2, "Meteor", now_ms())) == 0 and int(AS.left(str(pu), "SacredHeal", now_ms())) > 0,
       "X14: clearCdOf - every profile's cooldowns of that player go, nobody else's (%d)" % n_)

    # ---------------- X15 /cast stays
    reset_m()
    rr = str(A.cast(mpr, tst, mr, world, "1"))
    ck(rr.startswith("ok:Meteor") and not rr.endswith(" key") and not rr.endswith(" marker"), "X15: /cast 1 still casts (door 0): %s" % rr)
    reset_m()
    AC.CAST_CMD = False
    ck(str(A.cast(mpr, tst, mr, world, "1")) == "cmdoff" and str(A.runeCast(mpr, 0, 1)).startswith("ok:Meteor"), "X15: abil.castCmd OFF -> /cast 1 refused, the key casts")
    AC.CAST_CMD = True
    said()

    # ---------------- X16 Echo (Meteor: again at 20 % after 1 s, never counted)
    reset_m()
    setp(k_, {"e.Meteor": "Echo,Power"})
    aw.jobs.clear()
    rr = str(A.cast(mpr, tst, mr, world, "1"))
    kinds = sorted(int(j.kind) for j in list(aw.jobs))
    ck(rr.startswith("ok:Meteor") and " m0=Echo" in rr and 10 in kinds, "X16: a Meteor with Echo queues its echo job (kind 10): %s %s" % (rr, kinds))
    for j_ in list(aw.jobs):
        j_.at = now_ms() - 10
    AS.LASTUSE.clear()
    u0 = int(AS.load(k_).getProperty("u.Meteor"))
    for _i in range(3):
        aw.lastNs = 0
        tick.tick(JFloat(0.05), 0, None, tst, tbuf)
        for j_ in list(aw.jobs):
            j_.at = now_ms() - 10
    ck(int(A.ECHOES) >= 1, "X16: the echo ran (%d)" % int(A.ECHOES))
    ck(int(AS.load(k_).getProperty("u.Meteor")) == u0 + 1, "X16: the cast counted once, its echo never (%d -> %s)" % (u0, AS.load(k_).getProperty("u.Meteor")))
    said()

    # ---------------- X17 FIX ROUND (critics): ward per profile, the failed-write retry, the mirror back-off, Layered Ward, Spirit
    # Shield, the leave clean-up (the REAL ClassQuit)
    Dm = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")

    def hit_(amt):
        return Dm(Dm.NULL_SOURCE, DCSc.PROJECTILE, JFloat(amt))
    AS.WARD.clear()
    AS.WARDP.clear()
    ck(float(A.wardGive(mu, 10.0, now_ms() + 5000)) == 10.0 and str(AS.WARDP.get(mu)) == str(mu), "X17: a ward remembers the profile it was given to")
    d_ = hit_(4.0)
    ck(str(A.wardHit(tst, tbuf, mr, d_, now_ms())) == "ward:4 cancelled" and bool(d_.isCancelled()), "X17: the ward soaks a hit on its own profile")
    PROFKEY[str(mu)] = str(mu) + "-p2"
    d_ = hit_(4.0)
    ck(str(A.wardHit(tst, tbuf, mr, d_, now_ms())) == "otherprofile" and not bool(d_.isCancelled()) and float(d_.getAmount()) == 4.0
       and AS.WARD.get(mu) is None and AS.WARDP.get(mu) is None, "X17: after a profile switch the old profile's ward is dropped, the hit lands in full")
    ck(float(A.wardGive(mu, 6.0, now_ms() + 5000)) == 6.0, "X17: the new profile gets its own ward")
    del PROFKEY[str(mu)]
    ck(float(A.wardGive(mu, 3.0, now_ms() + 5000)) == 3.0 and str(AS.WARDP.get(mu)) == str(mu),
       "X17: back on profile 1 a weaker ward still replaces profile 2's (a stronger ward only wins on the same profile)")
    AS.WARD.clear()
    AS.WARDP.clear()
    # a failed ability-file write stays queued for the next 30 s flush
    AS.load(k_)
    AS.markDirty(k_)
    blocker = os.path.join(SCRATCH, "not-a-dir")
    open(blocker, "w").write("x")
    dir0 = AS.DIR
    AS.DIR = Paths.get(blocker)
    n_ = int(AS.flushOld(now_ms() + 60000, 30000))
    ck(n_ == 0 and AS.DIRTYAT.get(k_) is not None and AS.DIRTY.containsKey(k_), "X17: a failed write stays in DIRTYAT (the 30 s flush retries it): n=%d" % n_)
    AS.DIR = dir0
    n_ = int(AS.flushOld(now_ms() + 60000, 30000))
    ck(n_ >= 1 and AS.DIRTYAT.get(k_) is None and not AS.DIRTY.containsKey(k_), "X17: ... and the next flush writes it: n=%d" % n_)
    # the mirror back-off: a refused rune write is logged once, 2 s, 2 s, then 60 s; a working write clears it
    AS.MIRFAIL.clear()
    f0 = int(Cfg.FAILS)
    w_ = [int(A.mirrorWait(mpr, mu, "!0")) for _i in range(3)]
    ck(w_ == [2000, 2000, 60000] and int(Cfg.FAILS) == f0 + 1 and int(list(AS.MIRFAIL.get(mu))[0]) == 3,
       "X17: refused rune writes -> logged once (%d), waits %s" % (int(Cfg.FAILS) - f0, w_))
    ck(int(A.mirrorWait(mpr, mu, "")) == 2000 and AS.MIRFAIL.get(mu) is not None, "X17: nothing to do keeps the count")
    ck(int(A.mirrorWait(mpr, mu, "+0 +3")) == 2000 and AS.MIRFAIL.get(mu) is None, "X17: a write that works clears the count")
    AS.MIRROR.clear()
    A.runeTick(mpr, mu, mr, tst, now_ms())
    rec = AS.MIRROR.get(mu)
    A.mirrorNow(mpr)
    ck(rec is not None and 0 < int(rec[2]) - now_ms() <= 2100, "X17: mirrorNow (through mirrorWait) sets the next look 2 s ahead")
    # LAYERED WARD (Priest PB3): a real Shield Bubble cast with the node - 2 s shorter, the inner half regrows 3 % a second
    PRI = PLAYERS["Priest1"]

    def bubbles():
        return [z_ for z_ in list(aw.zoneArr()) if int(z_.kind) == 2 and str(z_.caster) == str(pu)]
    for z_ in list(aw.zoneArr()):
        aw.dropZone(z_)
    sl_p = [str(x) for x in AS.slots(str(pu), ci_p)]
    bkey = str(sl_p.index("ShieldBubble") + 1)
    TREE["csv"] = "A1,A2,A3,A4,PB3"
    AS.TREEC.clear()
    AS.clearCd(str(pu))
    mana(pm, 400.0)
    unthrottle()
    r_ = cast("Priest1", bkey)
    bz = bubbles()
    ck(r_.startswith("ok:ShieldBubble") and len(bz) == 1 and int(bz[0].nextHeal) > 0, "X17: Layered Ward - the bubble has two layers: %s" % r_)
    life_l = int(bz[0].until) - int(bz[0].start) if bz else -1
    sd = said()
    ck(any("Two layers: the inner half regrows 3 % a second." in x for x in sd), "X17: ... its line says so: %s" % sd[-1:])
    if bz:
        z_ = bz[0]
        hm_ = float(z_.hpMax)
        z_.hp = hm_ * 0.2
        add_ = float(A.layerRegrow(z_, now_ms()))
        ck(abs(add_ - hm_ * 0.03) < 1e-6 and abs(float(z_.hp) - hm_ * 0.23) < 1e-6, "X17: the inner half regrows 3 %% of the bubble's HP (+%s)" % add_)
        z_.hp = hm_ * 0.49
        A.layerRegrow(z_, now_ms())
        ck(abs(float(z_.hp) - hm_ * 0.5) < 1e-6, "X17: ... only up to the inner half's top")
        z_.hp = hm_ * 0.8
        ck(float(A.layerRegrow(z_, now_ms())) == 0.0, "X17: the outer layer never regrows")
        z_.hp = hm_ * 0.3
        z_.pulsesDue = 2
        z_.pulsesDone = 2
        z_.nextHeal = now_ms() - 1
        alive_ = bool(A.zoneTick0(z_, tst, tbuf, now_ms()))
        ck(alive_ and float(z_.hp) > hm_ * 0.3 and int(z_.pulsesDone) == 2, "X17: the REAL zone tick regrows it (%.2f -> %.2f), the earned pulses stay" % (hm_ * 0.3, float(z_.hp)))
    for z_ in list(aw.zoneArr()):
        aw.dropZone(z_)
    TREE["csv"] = "A1,A2,A3,A4"
    AS.TREEC.clear()
    AS.clearCd(str(pu))
    mana(pm, 400.0)
    unthrottle()
    r_ = cast("Priest1", bkey)
    bz = bubbles()
    life_n = int(bz[0].until) - int(bz[0].start) if bz else -1
    ck(r_.startswith("ok:ShieldBubble") and len(bz) == 1 and int(bz[0].nextHeal) == 0 and life_n - life_l == 2000,
       "X17: without the node: one layer, and the Layered bubble was 2 s shorter (%d vs %d ms)" % (life_l, life_n))
    for z_ in list(aw.zoneArr()):
        aw.dropZone(z_)
    said()
    # SPIRIT SHIELD (Priest PB4): a killing blow on the Priest -> saved at 20 % (not 30 %) + a 4 s bubble (a ward of 15 % max Health)
    GUARD_HP = int(AC.GS_HP)

    def save_once(csv):
        TREE["csv"] = csv
        AS.TREEC.clear()
        AS.GUARD.clear()
        AS.WARD.clear()
        AS.WARDP.clear()
        mana(pm, 400.0)
        pm.setStatValue(HP, JFloat(50.0))
        return str(A.guard(tst, tbuf, pr_r, hit_(500.0), now_ms()))
    g1 = save_once("A1,A2,A3,A4")
    ck(g1.startswith("saved:Priest1") and (" hp=%d" % GUARD_HP) in g1 and " spirit" not in g1 and AS.WARD.get(pu) is None,
       "X17: Guardian Spirit without the node: saved at %d %%, no bubble: %s" % (GUARD_HP, g1))
    g2 = save_once("A1,A2,A3,A4,PB4")
    wd = AS.WARD.get(pu)
    ck(g2.startswith("saved:Priest1") and " spirit" in g2 and (" hp=%s " % str(AM.fmt(GUARD_HP * 2.0 / 3.0))) in g2 + " " and float(GUARD_HP * 2.0 / 3.0) < GUARD_HP,
       "X17: Spirit Shield: saved at 2/3 (20 %% at the default 30): %s" % g2)
    ck(wd is not None and abs(float(wd[0]) - 15.0) < 1e-6 and 3900 <= int(float(wd[1])) - now_ms() <= 4000 and str(AS.WARDP.get(pu)) == str(pu),
       "X17: ... + a 4 s bubble = a ward of 15 %% max Health: %s" % (list(wd) if wd is not None else None))
    sd = said()
    ck(any("Spirit Shield: 4 s bubble." in x for x in sd), "X17: the save line names it: %s" % sd[-2:])
    TREE["csv"] = None
    AS.TREEC.clear()
    AS.GUARD.clear()
    AS.WARD.clear()
    AS.WARDP.clear()
    pm.setStatValue(HP, JFloat(100.0))
    # ---------------- X18 SECOND FIX ROUND (critics)
    kM = str(Cfg.pkey(mu))
    JObj = JClass("java.lang.Object")
    # (a) a FAILED tree read ("!err" from SkyyTrees, or a throw) is never "no gate": the last good answer (any age), else "" (closed)
    TREE["csv"] = "A1"
    AS.TREEC.clear()
    ck(str(A.treeCsv(mu)) == "A1", "X18: a good tree read is cached")
    AS.TREEC.put(mu, JArray(JObj)([JString(kM), JLong(now_ms() - 5000), JString("A1")]))
    TREE["csv"] = "!err"
    te0 = int(A.TREE_ERR)
    ck(str(A.treeCsv(mu)) == "A1" and str(list(AS.TREEC.get(mu))[2]) == "A1" and int(list(AS.TREEC.get(mu))[1]) < now_ms() - 4000,
       "X18: '!err' -> the last good answer of this profile kept (not re-cached)")
    AS.TREEC.clear()
    tc_ = A.treeCsv(mu)
    ck(tc_ is not None and str(tc_) == "" and AS.TREEC.get(mu) is None and int(A.TREE_ERR) == te0 + 1 and not bool(A.lineOn(tc_, METEOR)),
       "X18: '!err' with nothing cached -> '' (fail CLOSED: Meteor not enabled), not cached, counted")
    ck(list(str(x) for x in A.runeWant(mu)) == ["", ""], "X18: ... and the mirror wants no rune")
    AS.TREEC.put(mu, JArray(JObj)([JString(kM + "-other"), JLong(now_ms() - 5000), JString("A1")]))
    ck(str(A.treeCsv(mu)) == "", "X18: another profile's cached answer is never used")

    @JImplements("java.util.function.Function")
    class Throw(object):
        @JOverride
        def apply(self, o):
            raise RuntimeError("boom")
    br.put("tree:fn:abil", Throw())
    AS.TREEC.put(mu, JArray(JObj)([JString(kM), JLong(now_ms() - 5000), JString("A1,A2")]))
    ck(str(A.treeCsv(mu)) == "A1,A2", "X18: a throwing bridge -> the last good answer too")
    br.put("tree:fn:abil", Fn(lambda o: None if TREE["csv"] is None else JString(TREE["csv"])))
    AS.TREEC.clear()
    # (b) the "enable it in /tree" hint: once per profile per session, 8 s after the first look
    TREE["csv"] = ""
    said()
    h_ = str(A.enableHint(mpr, mu, kM))
    sd = said()
    ck("Meteor" in h_ and "ManaBarrier" not in h_ and any("open /tree, class tab, and click Enable (free)" in x and "Meteor" in x for x in sd),
       "X18: trees on, nothing enabled -> one line names the owned abilities: %s / %s" % (h_, sd))
    TREE["csv"] = "A1,A2,A3,A4"
    AS.TREEC.clear()
    ck(str(A.enableHint(mpr, mu, kM)) == "" and not said(), "X18: everything enabled -> no line")
    TREE["csv"] = None
    AS.TREEC.clear()
    ck(str(A.enableHint(mpr, mu, kM)) == "" and not said(), "X18: class trees off -> no line")
    TREE["csv"] = "A1"
    AS.TREEC.clear()
    AS.HINTED.clear()
    t0_ = now_ms()
    r1_, r2_ = str(A.hintTick(mpr, mu, kM, t0_)), str(A.hintTick(mpr, mu, kM, t0_ + 2000))
    r3_ = str(A.hintTick(mpr, mu, kM, t0_ + 8000))
    r4_ = str(A.hintTick(mpr, mu, kM, t0_ + 20000))
    sd = said()
    ck(r1_ == "wait" and r2_ == "" and "Meteor" not in r3_ and len(r3_) > 0 and r4_ == "" and len([x for x in sd if "open /tree" in x]) == 1,
       "X18: hintTick: wait, quiet, one line at 8 s (A1 enabled -> the other three named), then never again: %s %s %s %s" % (r1_, r2_, r3_, r4_))
    # the REAL tick path calls it (runeTick -> hintTick puts the profile in HINTED)
    AS.HINTED.clear()
    AS.MIRROR.remove(mu)
    A.runeTick(mpr, mu, mr, tst, now_ms())
    ck(AS.HINTED.get(kM) is not None, "X18: runeTick (the full look) starts the hint clock")
    TREE["csv"] = None
    AS.TREEC.clear()
    said()
    # (c) Chain: the drop cut stops at the Lv 5 one (8 %), a doubled Chain adds targets only
    GRACE_ = ID["MartyrsGrace"]
    ck(abs(float(A.chainCut(2)) - 3.2) < 1e-9 and float(A.chainCut(5)) == 8.0 and float(A.chainCut(10)) == 8.0 and float(A.chainCut(-1)) == 0.0,
       "X18: chainCut 2 -> 3.2, 5 -> 8, 10 (doubled Lv 5) -> 8")
    mt_ = str(A.modText(GRACE_, int(AMD.CHAIN), 5, 2))
    ck(mt_.startswith("+10 targets, 8 % less drop") and "drop floor" in mt_, "X18: doubled Chain Lv 5 text: %s" % mt_)
    pc_ = [float(AM.chainPct(k__, 75.0, float(AC.G_DROP) - float(A.chainCut(10)))) for k__ in range(15)]
    ck(sum(1 for v in pc_ if v > 0.0) == 11, "X18: doubled Chain Lv 5 at the default 15 %% drop -> 11 heals before it fades, not 15: %s" % pc_)
    # (d) Lingering: 3 s at Lv 1 (Mage.md, Locked), +0.5 s a level
    ck(str(A.modText(METEOR, int(AMD.LINGER), 1, 1)).startswith("burns 3 s") and str(A.modText(METEOR, int(AMD.LINGER), 5, 1)).startswith("burns 5 s"),
       "X18: Lingering text: %s / %s" % (A.modText(METEOR, int(AMD.LINGER), 1, 1), A.modText(METEOR, int(AMD.LINGER), 5, 1)))
    # (e) /classadmin abil maxlevels | resetlevels: a backup first, maxlevels only raises
    top_ = int(AMt.levelStart(int(AC.MAX_LVL), float(AC.USES_COEF), float(AC.USES_EXP)))
    setp(kM, {"u.Meteor": top_ + 50, "u.ManaBarrier": 7, "m.Meteor.Power": 500})
    abd = os.path.join(home, "abilities")
    bak0 = set(f for f in os.listdir(abd) if ".lvl-" in f) if os.path.isdir(abd) else set()
    ra_ = str(A.adminDo(mpr, str(mu), "maxlevels"))
    sd = said()
    pm_ = AS.load(kM)
    bak1 = set(f for f in os.listdir(abd) if ".lvl-" in f) - bak0
    ck(ra_ == "maxlevels" and int(str(pm_.getProperty("u.Meteor"))) == top_ + 50 and int(str(pm_.getProperty("u.ManaBarrier"))) == top_
       and int(str(pm_.getProperty("m.Meteor.Power"))) == 500 and int(str(pm_.getProperty("m.Meteor.Radius"))) == int(list(AMD.steps())[-1]),
       "X18: maxlevels only RAISES (Meteor %s kept, Mana Barrier 7 -> top, Power+ 500 kept)" % pm_.getProperty("u.Meteor"))
    bk_ = os.path.join(abd, sorted(bak1)[0]) if len(bak1) == 1 else None
    btxt = open(bk_, encoding="latin-1").read() if bk_ else ""
    ck(len(bak1) == 1 and sorted(bak1)[0].startswith(kM + ".properties.lvl-") and "u.ManaBarrier=7" in btxt and any("Backup: abilities/" in x for x in sd),
       "X18: ... after a backup of the old counts: %s" % sorted(bak1))
    time.sleep(0.01)
    rr_ = str(A.adminDo(mpr, str(mu), "resetlevels"))
    pm_ = AS.load(kM)
    bak2 = set(f for f in os.listdir(abd) if ".lvl-" in f) - bak0
    ck(rr_ == "resetlevels" and pm_.getProperty("u.Meteor") is None and pm_.getProperty("m.Meteor.Power") is None and len(bak2) == 2,
       "X18: resetlevels clears the counts, after a second backup: %s" % sorted(bak2))
    sAD = AS.DIR
    AS.DIR = None
    ck(str(A.adminDo(mpr, str(mu), "resetlevels")) == "nobak" and any("Could not back up" in x for x in said()), "X18: no backup -> nothing changes")
    AS.DIR = sAD
    setp(kM, {"u.Meteor": None, "u.ManaBarrier": None})
    said()
    # (f) the ClassQuit below also drops HINTED
    AS.HINTED.put(kM, JArray(JLong)([1, 1]))
    # the leave clean-up: the REAL ClassQuit drops this player's LASTKEY / LASTUSE / WARDP / MIRFAIL entries, nobody else's
    AS.LASTKEY.put(str(mu) + "|0", JLong(1))
    AS.LASTKEY.put(str(mu) + "|1", JLong(1))
    AS.LASTKEY.put(str(pu) + "|0", JLong(1))
    AS.LASTUSE.put(str(mu) + "|Meteor", JLong(1))
    AS.LASTUSE.put(str(mu) + "-p2|Meteor", JLong(1))
    AS.LASTUSE.put(str(pu) + "|SacredHeal", JLong(1))
    AS.WARDP.put(mu, str(mu))
    AS.MIRFAIL.put(mu, JArray(JInt)([1]))
    PDE = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent")
    pde = U.allocateInstance(PDE.class_)
    fn_ = gfield("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent", "getPlayerRef")
    kc_ = PDE.class_
    while True:
        try:
            f_ = kc_.getDeclaredField(fn_)
            break
        except Exception:
            kc_ = kc_.getSuperclass()
    f_.setAccessible(True)
    f_.set(pde, mpr)
    C("ClassQuit")().accept(pde)
    lk = sorted(str(x) for x in AS.LASTKEY.keySet())
    lu = sorted(str(x) for x in AS.LASTUSE.keySet())
    ck(lk == [str(pu) + "|0"] and str(pu) + "|SacredHeal" in lu and not any(x.startswith(str(mu)) for x in lu) and AS.WARDP.get(mu) is None and AS.MIRFAIL.get(mu) is None and AS.HINTED.get(kM) is None,
       "X17: the REAL ClassQuit clears the leaver's key maps only: %s %s" % (lk, lu))
    K.notes.append("counters: hooks %d, runes %d, fallbacks %d, mirrors %d, uses %d, echoes %d" % (int(A.HOOKS), int(A.RUNES), int(A.FALLBACKS), int(A.MIRRORS), int(A.USES), int(A.ECHOES)))
    K.save()
    os._exit(0)


# ============================================================================================================ OLD: the 0.1.19 sections
def old_sections():
    d = os.path.join(BASE, "t19")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "tmp"))
    env = dict(os.environ, TEMP=os.path.join(d, "tmp"), TMP=os.path.join(d, "tmp"), JAVA_TOOL_OPTIONS="-XX:-UsePerfData")
    p = subprocess.run([sys.executable, T19, "--jar", JAR, "--dir", d], env=env, capture_output=True, text=True)
    out = (p.stdout or "").strip().splitlines()
    print("OLD. test_skyyclasses_0.1.19.py on the 0.1.22 jar:\n   " + "\n   ".join(out[-4:]))
    fails = [ln for ln in out if ln.strip().startswith("FAIL")]
    other = [f for f in fails if " CC " not in f and not f.strip().startswith("FAIL CC")]
    HK.check(not other, "OLD 0.1.19 sections (loadout bridge L, START TWICE on a live copy ST) pass on the 0.1.22 jar: %s" % other[:3])
    HK.check(any("checks passed" in ln for ln in out[-6:]), "OLD 0.1.19 harness ran to the end")
    shutil.rmtree(d, ignore_errors=True)


EXPECT = ["Abil", "AbilCfg", "AbilMath", "AbilStore", "AbilJob", "AbilZone", "AbilDefs", "AbilLoadout", "AbilFn", "AbilShieldSys", "ClassQuit",
          "ClassTick", "ClassReady", "SkyyClassesPlugin", "CfgRows", "CfgFn", "KitMigrate", "AdminAbilCmd", "AbilPage", "AbilWorld"]

if __name__ == "__main__":
    if "--phase" not in sys.argv:
        assert os.path.realpath(BASE).startswith(os.path.realpath(os.path.join(TOOLS, "dev", "scratch")) + os.sep)
        old_sections()
    HK.run_compare = run_compare22
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=NEW_CLASSES,
           phases=[("exec", run_exec), ("route21", run_route21)], script=__file__)
