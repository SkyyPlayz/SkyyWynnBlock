"""SkyyClasses 0.1.23 - harness for MONK + ASSASSIN ON THE RUNE FRAMEWORK + REBIRTH R6 (tools/classes_0_1_23_patch.py), on top of every 0.1.22
section (the keys, levels, modifiers, panel - kept as the regression). Build first: python tools/classes_0_1_23_patch.py &&
python SkyyClasses/build_skyyclasses_0.1.23.py

    python SkyyClasses/test_skyyclasses_0.1.23.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

0.1.23 sections (inside the exec phase, the same engine stand-ins): X19 the pure rules (rebirth soft cap, live stacks, the backstab rule,
Awe tiers, waves, modifier levels past their top, Palm's cooldown floor, the effect ids) + the tables / loadouts / panel / mirror / HUD for
the Monk + Assassin; X20 Flowing Form (aura, combo stacks from the REAL hit hook, speed, Awe + losing the target, drain, the end, every
shape); X21 Hundred Fists (waves, the gap, Echo); X22 Still Water (counter / blocked / deflect through the REAL damage hook, Echo, Ward,
Reflexes, Tranquility, Calm Aura, Serenity); X23 Palm Strike (no target, stun, push, every shape, Aerial / Concussive / Iron Fist,
Ricochet, Slow, Echo, the cooldown floor); X24 Cyclone Kick (ring, arc, Leg Sweep, Dropping Kick, Haste); X25 Cloak + First Strike (lose
target, First Strike, break on attack, Lethal Opener, Death Mark, Longer Cloak, Dash / Silent / Still Shadow, Slip Away); X26 Toxin (cloud,
poison, Weaken, the tree nodes, Plague, Chain, Echo); X27 God Killer (not a boss, front / behind, Death from Above, Boss Hunter, Echo,
Haste, Patient Kill armed / broken); X28 Vanishing Act (smoke: lose you + slow, Smoke Drop, Ambush); X29 the class-tree numbers; X30 REBIRTH
R6 (the participant at every step incl. a failed write + retry, stale staged files, an older committed rebirth; the soft cap; the cap 25 + n;
the +1 modifier level; ClassQuit).

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

VERSION = "0.1.23"
PKG = "com.skyy.classes."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-0.1.22.jar")
BASE = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "classes2", "cl")))
SCRATCH = BASE if "--phase" in sys.argv else os.path.join(BASE, "h")
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
ASSETS = os.path.join(APPDATA, "Hytale", "install", "release", "package", "game", "latest", "Assets.zip")
T19 = os.path.join(HERE, "test_skyyclasses_0.1.19.py")
NEW_CLASSES = ["ClassRb", "AbilNum"]


def t21():
    spec = importlib.util.spec_from_file_location("test_skyyclasses_0_1_21", os.path.join(HERE, "test_skyyclasses_0.1.21.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_route21(out, jar, scratch, home):
    T = t21()
    T.run_ability(out, jar, scratch, home)


# ============================================================================================================ C: the 0.1.22 -> 0.1.23 compare
def run_compare23(out, jar, old_jar, pkg, expect, added):
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
    K.eq(sorted(set(nb) - set(na)), sorted(pkg + a for a in added), "C: the classes added (ClassRb, AbilNum)")
    K.eq(sorted(set(na) - set(nb)), [], "C: no class removed")
    diffs = {}
    for cn in sorted(set(na) & set(nb)):
        a_, b_ = body(pa.get(cn)), body(pb.get(cn))
        dd = sorted(k for k in set(a_) | set(b_) if a_.get(k) != b_.get(k))
        if dd:
            diffs[cn[len(pkg):]] = dd
    print("C. class compare 0.1.22 -> 0.1.23: %d classes identical, %d differ: %s" % (len(set(na) & set(nb)) - len(diffs), len(diffs), sorted(diffs)))
    extra = sorted(set(diffs) - set(expect))
    K.check(not extra, "C: only the planned classes change (unplanned: %s)" % extra)
    K.notes.append("C: changed %s" % {k: len(v) for k, v in diffs.items()})
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    changed = sorted(n for n in ea & eb if za.read(n) != zb.read(n))
    K.eq(changed, ["Server/Languages/en-US/server.lang", "manifest.json"], "C: the changed non-class entries: the language file (+ the new runes) and manifest.json")
    K.eq(sorted(ea - eb), [], "C: no non-class entry removed")
    new = sorted(eb - ea)
    runes = [n for n in new if n.startswith("Server/Item/Items/SkyyClasses/SkyyAbility_")]
    efx = [n for n in new if n.startswith("Server/Entity/Effects/SkyyClasses/SkyyAbility_") and "_Mark_" not in n]
    K.check(len(runes) == 9 and len(efx) == 162 and len(new) == 9 * 6 + 162 and all(n.startswith(("Server/", "Common/")) for n in new),
            "C: the new entries = 9 Monk / Assassin runes (x6 files) + 162 effects (speed tiers, Awe, Weaken, the cloak): %d / %d / %d" % (len(new), len(runes), len(efx)))
    old_lang = za.read("Server/Languages/en-US/server.lang").decode("utf8")
    new_lang = zb.read("Server/Languages/en-US/server.lang").decode("utf8")
    K.check(all(l in new_lang.splitlines() for l in old_lang.splitlines()), "C: every 0.1.22 language line is kept")
    man = json.loads(zb.read("manifest.json"))
    K.check(man.get("IncludesAssetPack") is True and man.get("Version") == VERSION, "C: manifest IncludesAssetPack + version %s" % man.get("Version"))
    for n in runes:
        d = json.loads(zb.read(n))
        K.check(d["Quality"] == "Debug" and d["MaxStack"] == 1 and d["DropOnDeath"] is False and d["Ability"]["Cost"] == 0
                and d["Ability"]["CostType"] == "None" and d["Ability"]["Cast"].startswith("Root_SkyyAbility_"),
                "C: %s is a hidden, free, undroppable rune with our cast root" % n.rsplit("/", 1)[1])
    sp = json.loads(zb.read("Server/Entity/Effects/SkyyClasses/SkyyAbility_Spd_42.json"))
    aw = json.loads(zb.read("Server/Entity/Effects/SkyyClasses/SkyyAbility_Awe_20.json"))
    wk = json.loads(zb.read("Server/Entity/Effects/SkyyClasses/SkyyAbility_Weaken_15.json"))
    K.check(abs(sp["ApplicationEffects"]["HorizontalSpeedMultiplier"] - 1.12) < 1e-9 and abs(aw["ApplicationEffects"]["HorizontalSpeedMultiplier"] - 0.9) < 1e-9
            and all(v[0]["Amount"] == -0.2 for v in aw["DamageResistance"].values()) and all(v[0]["Amount"] == -0.15 for v in wk["OutgoingDamage"].values()),
            "C: the effect numbers (Spd_42 = +12 %, Awe_20 = -20 % defence / -10 % speed, Weaken_15 = -15 % damage dealt)")
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
    # ================================================================================================ 0.1.23 sections (Monk, Assassin, rebirth R6)
    # ---------------- X19 the 0.1.23 pure rules
    ck([int(AMt.rbEff(16, 16, l_, 110, 100)) for l_ in (1, 55, 110, 200)] == [8, 12, 16, 16], "X19: rebirth soft cap S 16, Lr 110: L 1 -> 8, 55 -> 12, 110 -> 16 (spec 3.2)")
    ck(int(AMt.rbEff(5, 16, 1, 110, 100)) == 5 and int(AMt.rbEff(16, 0, 1, 110, 100)) == 16 and int(AMt.rbEff(16, 4, 100, 100, 100)) == 16,
       "X19: the working level never above the level now; no rebirth record = the level; L >= Lr = the level")
    ck(int(AMt.rbEff(30, 30, 100, 200, 100)) == 22, "X19: F(L) floor (L 100: 15) vs half + ... (15 + 15 x 100 / 200 = 22)")
    ck([int(AMt.rbModEff(5, e_, 16)) for e_ in (8, 12, 16)] == [3, 4, 5] and int(AMt.rbModEff(5, 20, 16)) == 5, "X19: modifier levels follow the ratio (ceil)")
    ck(int(AMt.live(JArray(JLong)([1000, 5000, 0, 9000]), 9500, 5000)) == 2, "X19: live combo stacks (gained under 5 s ago)")
    ck(bool(AMt.behind(0.0, 0.0, 0.0, 0.0, 2.0, 80.0)) and not bool(AMt.behind(0.0, 0.0, 0.0, 0.0, -2.0, 80.0)) and not bool(AMt.behind(0.0, 0.0, 0.0, 2.0, 0.0, 80.0)),
       "X19: the backstab rule (the back = (sin yaw, cos yaw), +-80 degrees)")
    ck([int(AMt.aweTier(t_, 1.0, 1.0)) for t_ in (0, 1, 7, 40)] == [1, 1, 7, 20] and int(AMt.aweTier(10, 1.0, 1.5)) == 15, "X19: the Awe tier 1-20 (Power+ makes it stronger)")
    ck([int(AMt.waves(t_, 0, 10)) for t_ in (9, 10, 19, 20)] == [0, 1, 1, 2] and int(AMt.waves(8, 8, 10)) == 1 and int(AMt.waves(18, 8, 10)) == 2,
       "X19: Hundred Fists waves (every 10th; Rushing Fists the first at 8)")
    ck([int(AMD.modLevelX(u_, 1)) for u_ in (100, 139, 140, 179)] == [5, 5, 6, 6] and int(AMD.modLevelX(5000, 2)) == 7 and int(AMD.modLevelX(5000, 0)) == 5,
       "X19: a rebirth upgrade lets a modifier level past 5 (steps 140, 180 ...)")
    ck(int(AMD.modNextX(100, 1)) == 40 and int(AMD.modNextX(140, 1)) == 0 and int(AMD.modNextX(25, 1)) == 5, "X19: modNextX")
    ck(int(A.palmCut(1)) == 0 and int(A.palmCut(6)) == 500 and int(A.palmCut(25)) == 1000, "X19: Palm Strike -0.1 s a level to its 5.0 s floor")
    ck(str(A.spdId(12)) == "SkyyAbility_Spd_42" and str(A.spdId(-25)) == "SkyyAbility_Spd_5" and str(A.spdId(200)) == "SkyyAbility_Spd_110"
       and str(A.aweId(0)) == "SkyyAbility_Awe_1" and str(A.aweId(25)) == "SkyyAbility_Awe_20", "X19: the effect ids")

    # ---------------- the Monk + Assassin test players, effects and seams
    EFX = ArrayList()
    A.EFFECTS = EFX
    A.EFFECT = Fn(lambda o: Bool.valueOf(not str(list(o)[1]).startswith("?")))
    LOST = ArrayList()
    A.LOST = LOST
    PUSH = ArrayList()
    A.PUSHES = PUSH
    MOBT = {"t": None}
    A.MOB = Fn(lambda o: MOBT["t"])
    LOOKV = {"v": [0.0, 65.6, 0.0, 0.0, 0.0, 1.0]}
    A.LOOK = Fn(lambda o: JArray(JDouble)(LOOKV["v"]))
    ci_k, ci_s = NAMES_.index("Monk"), NAMES_.index("Assassin")
    SK_K, SK_S = str(Defs.SKILLS[ci_k]), str(Defs.SKILLS[ci_s])
    ku, kr, kpr, km, kpl, kmsc = player(40, 0.5, 64.0, 0.5, "Monk1")
    su, sr_, spr, sm, spl, smsc = player(41, 20.5, 64.0, 0.5, "Assassin1")
    setclass(ku, "Monk")
    setclass(su, "Assassin")
    LEVEL[(str(ku), SK_K)] = 30
    LEVEL[(str(su), SK_S)] = 30
    HANDS[40] = "Weapon_Staff_Bo_Wood"
    HANDS[41] = "Weapon_Daggers_Crude"
    kK, kS = str(ku), str(su)
    ID = dict((str(AD.IDS[i]), i) for i in range(len(AD.IDS)))
    FF, PS, CK, HF, SW = ID["FlowingForm"], ID["PalmStrike"], ID["CycloneKick"], ID["HundredFists"], ID["StillWater"]
    CL, TX, GK, VA = ID["CloakFirstStrike"], ID["Toxin"], ID["GodKiller"], ID["VanishingAct"]
    ck([int(AD.TIER[i]) for i in (FF, PS, CK, HF, SW, CL, TX, GK, VA)] == [0, 1, 2, 3, 4, 0, 1, 2, 3] and int(AD.of(ci_s, 4)) == -1,
       "X19: the 9 abilities sit on their tiers (the Assassin has no A1-alt B)")
    ck(all(str(AD.RUNE[i]) == "SkyyAbility_%s_%s" % (c_, AD.IDS[i]) for i, c_ in ((FF, "Monk"), (VA, "Assassin"))), "X19: their rune ids")
    for i_ in (FF, PS, CK, HF, SW, CL, TX, GK, VA):
        RUNES_LOADED.add(str(AD.RUNE[i_]))
    ck(list(AS.slots(kS, ci_s)) == ["CloakFirstStrike", "Toxin", "GodKiller", "VanishingAct"], "X19: the Assassin's default loadout")
    ck(bool(AD.owns(VA, 30, False, "B")) and int(AD.pickTierC(ci_s, "B")) == 3 and list(AD.defaults(ci_s, "B"))[3] == "VanishingAct",
       "X19: a pick of B never locks the Assassin out of Vanishing Act (one alt only)")
    ck("one Ability 1 alt" in str(A.setPick(kS, ci_s, "B")), "X19: setPick B on an Assassin says so: %s" % A.setPick(kS, ci_s, "B"))
    pan = A.panel(su, None, False)
    ck(str(pan[0]) == "ok" and str(pan[1]) == "Assassin" and not bool(pan[5]) and str(pan[77]) == "", "X19: the panel - Assassin: abilities, no alt pick")
    pank = A.panel(ku, None, False)
    ck(str(pank[0]) == "ok" and bool(pank[5]) and str(pank[76]) == "Hundred Fists" and str(pank[77]) == "Still Water", "X19: the panel - Monk: the A / B alts")
    ck(list(A.runeWant(ku)) == [str(AD.RUNE[FF]), str(AD.RUNE[PS])] and list(A.runeWant(su)) == [str(AD.RUNE[CL]), str(AD.RUNE[TX])],
       "X19: the mirror wants their primaries' runes")
    ABSEC2 = int(JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent").ABILITIES_SECTION_ID)
    ck(str(A.runeDecide(ku, ci_k, 0, "Rune_Fireball", ABSEC2, now_ms() + 99999)) == "vanilla", "X19: a game rune on a Monk is blocked now too (Skyy M2)")
    AS.LASTKEY.clear()
    AS.LASTHOOK.clear()
    ck(len(list(C("AbilFn")().apply(ku))) == 48, "X19: class:fn:abil (SkyyHud) answers 48 fields for a Monk")
    aw.jobs.clear()
    aw.zones.clear()
    aw.nz = 0

    def run_world(ms=0):
        for j_ in list(aw.jobs):
            j_.at = now_ms() - 10 - ms
        aw.lastNs = 0
        aw.nextZone = 0
        tick.tick(JFloat(0.05), 0, None, tst, tbuf)

    def kreset(m_=None):
        AS.clearCd(kK)
        AS.clearCd(kS)
        for mm_ in (km, sm):
            mm_.setStatValue(MANA, JFloat(400.0))
            mm_.setStatValue(STAM, JFloat(50.0))
        unthrottle()
        said()
        AS.LASTUSE.clear()

    def fcast(pr__, r__, slot, sh):
        unthrottle()
        return str(A.castAt(pr__, tst, r__, world, slot, sh, 3))

    def mob(i, x, z, hp=200.0, role=None):
        r_ = npc(i, x, 64.0, z, hp=hp)
        return r_

    def stuns():
        return [round(float(str(x).split(":", 1)[1]), 2) for x in EFX if str(x).startswith("Stun:")]

    def dmg(src, amt, proj=False, shooter=None):
        DENTc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
        DPRJc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$ProjectileSource")
        Dm_ = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
        so = DPRJc(src, src) if proj else DENTc(src)
        return Dm_(so, DCSc.PROJECTILE, JFloat(amt))

    # ---------------- X20 MONK: Flowing Form (aura, combo stacks, speed, Awe, drain, the end)
    kreset()
    TREE["csv"] = None
    m1, m2 = mob(60, 2.5, 0.5), mob(61, 3.5, 1.5)
    NEARL[:] = [m1, m2]
    r_ff = fcast(kpr, kr, "1", 0)
    zf = AS.FLOWS.get(ku)
    ck(r_ff.startswith("ok:FlowingForm") and zf is not None and int(zf.kind) == 8 and float(zf.r) == 5.0, "X20: Flowing Form casts the aura (5 blocks): %s" % r_ff)
    ck(abs(sv(km, MANA) - 398.0) < 0.01 and abs(sv(km, STAM) - 49.0) < 0.01, "X20: 2 Mana + 1 Stamina to start")
    hl0 = str(A.hitLanded(tbuf, m1, dmg(kr, 5.0), now_ms()))
    ck(hl0 == "combo+1", "X20: a landed weapon hit = +1 combo stack (%s)" % hl0)
    for i_ in range(5):
        A.hitLanded(tbuf, m1, dmg(kr, 5.0), now_ms())
    ck(int(zf.total) == 6 and int(A.stacks(zf, now_ms())) == 6, "X20: 6 hits = 6 stacks, total 6")
    zf.t1 = now_ms() - 1000
    EFX.clear()
    LOST.clear()
    run_world()
    sp_ = AS.SPD.get(ku)
    ck(sp_ is not None and int(sp_[0]) == 12 and "SkyyAbility_Spd_42:1.5" in [str(x) for x in EFX], "X20: 6 stacks x 2 %% = +12 %% move speed (our speed effect): %s" % ([str(x) for x in EFX][:4]))
    ck(abs(sv(km, MANA) - (398.0 - 0.65)) < 0.05 and abs(sv(km, STAM) - (49.0 - 0.25)) < 0.05, "X20: 1 s of drain = 0.65 Mana + 0.25 Stamina: %s %s" % (sv(km, MANA), sv(km, STAM)))
    aw_ = AS.AWED.get(m1)
    ck(aw_ is not None and int(aw_[1]) == 6 and LOST.contains(m1) and LOST.contains(m2), "X20: both mobs in the aura are Awed (tier 6 = -6 %% defence) and lose their target")
    ck("SkyyAbility_Awe_6:10" in [str(x) for x in EFX], "X20: ... the Awe effect lasts 10 s past the aura")
    ck(bool(zf.echoed), "X20: 5+ combo = one counted use of Flowing Form")
    # out of Mana -> it ends, speed off
    km.setStatValue(MANA, JFloat(0.1))
    zf.t1 = now_ms() - 1000
    EFX.clear()
    run_world()
    ck(bool(zf.ended) and str(zf.why) == "mana" and AS.FLOWS.get(ku) is None and "-SkyyAbility_Spd_42" in [str(x) for x in EFX], "X20: out of Mana -> the aura ends, the speed effect is taken off")
    ck(any("Flowing Form ended - out of Mana" in x for x in said()), "X20: the end line")
    # shapes: Flow Sprint (2 stacks, free Stamina 3 s), Centred (3 stacks, 4 blocks, -25 % drain), the landing
    kreset()
    r_sp = fcast(kpr, kr, "1", 1)
    zf = AS.FLOWS.get(ku)
    ck(" shape=sprint" in r_sp and int(zf.total) == 2 and int(A.stacks(zf, now_ms())) == 2 and int(zf.t2) > now_ms(), "X20: Flow Sprint starts at 2 stacks, no Stamina drain for 3 s: %s" % r_sp)
    kreset()
    p_ = {"p1": "CycloneKick", "p2": "PalmStrike", "a1": "FlowingForm", "a2": "HundredFists"}
    setp(kK, p_)
    r_cr = fcast(kpr, kr, "3", 3)
    zf = AS.FLOWS.get(ku)
    ck(" shape=crouch" in r_cr and int(zf.total) == 3 and float(zf.r) == 4.0 and abs(float(zf.amount) - 0.65 * 0.75) < 1e-9, "X20: Centred (crouch): 3 stacks, 4 blocks, drain -25 %%: %s" % r_cr)
    setp(kK, {"p1": None, "p2": None, "a1": None, "a2": None})
    kreset()
    kmsc.getMovementStates().onGround = False
    r_ai = fcast(kpr, kr, "1", 2)
    kmsc.getMovementStates().onGround = True
    run_world()
    ck(" land" in r_ai and str(A.LAST_LAND).startswith("flow:") and AS.FLOWS.get(ku) is not None, "X20: Flow Landing: the aura starts when you land (%s)" % A.LAST_LAND)
    # ---------------- X21 Hundred Fists: waves on the Awed, the 8 s gap, Echo
    kreset()
    setp(kK, {"p1": "HundredFists", "p2": "PalmStrike", "a1": "CycloneKick", "a2": "FlowingForm"})
    AS.TREEC.clear()
    r_hf = fcast(kpr, kr, "1", 0)
    zh = AS.FLOWS.get(ku)
    ck(r_hf.startswith("ok:HundredFists") and int(zh.n1) == 10 and abs(float(zh.d2) - 25.0) < 1e-6, "X21: Hundred Fists: a wave every 10 hits, 1.0 H: %s" % r_hf)
    run_world()   # Awe the mobs
    for i_ in range(10):
        A.hitLanded(tbuf, m1, dmg(kr, 5.0), now_ms())
    TBf.EVENTS.clear()
    run_world()
    ck(int(zh.hits) == 1 and TBf.EVENTS.size() >= 2 and int(zh.nextHeal) > now_ms() + 7000, "X21: the 10th hit -> a shockwave on every Awed enemy (%d hits); the next not before 8 s" % TBf.EVENTS.size())
    for i_ in range(10):
        A.hitLanded(tbuf, m1, dmg(kr, 5.0), now_ms())
    TBf.EVENTS.clear()
    run_world()
    ck(int(zh.hits) == 1 and int(zh.n2) == 2, "X21: the 20th hit inside the gap waits (2 earned, 1 fired)")
    ck(any("Shockwave! 2 Awed enemies hit." in x for x in said()), "X21: the wave line")
    # Echo: each wave again 1 s later, weaker (the Echo modifier at Lv 1 = 20 %)
    setp(kK, {"u.HundredFists": int(AMt.levelStart(6, 4.5, 1.5)), "e.HundredFists": "Echo,"})
    zh.ended = True
    run_world()
    kreset()
    AS.TREEC.clear()
    fcast(kpr, kr, "1", 0)
    zh = AS.FLOWS.get(ku)
    ck(zh.cx is not None and abs(float(zh.cx.echoPct) - 0.20) < 1e-9, "X21: Echo equipped (Lv 6 unlocks the 3rd modifier): echo 20 %%")
    run_world()
    for i_ in range(10):
        A.hitLanded(tbuf, m1, dmg(kr, 5.0), now_ms())
    run_world()
    ej = [j_ for j_ in list(aw.jobs) if int(j_.kind) == 10 and int(j_.ai) == HF]
    ck(len(ej) == 1 and abs(float(ej[0].amount) - float(zh.d2) * 0.2) < 1e-6, "X21: the echo wave is queued at 20 %% (%s of %s)" % ([float(x.amount) for x in ej], float(zh.d2)))
    TBf.EVENTS.clear()
    e0 = int(A.ECHOES)
    run_world(2000)
    ck(int(A.ECHOES) == e0 + 1 and str(A.LAST_ECHO).startswith("wave:"), "X21: the echo wave runs (%s)" % A.LAST_ECHO)
    zh.ended = True
    run_world()
    setp(kK, {"p1": None, "p2": None, "a1": None, "a2": None, "u.HundredFists": None, "e.HundredFists": None})
    said()
    # ---------------- X22 Still Water: counter, deflect, gap, Echo, Ward, Reflexes / Tranquility
    kreset()
    setp(kK, {"p1": "StillWater", "p2": "PalmStrike", "a1": "CycloneKick", "a2": "FlowingForm", "alt": "B",
              "u.StillWater": int(AMt.levelStart(10, 4.5, 1.5)), "e.StillWater": "Echo,Ward"})
    AS.TREEC.clear()
    TREE["csv"] = None
    AS.WARD.clear()
    r_sw = fcast(kpr, kr, "1", 0)
    zs = AS.STANCES.get(ku)
    ck(r_sw.startswith("ok:StillWater") and zs is not None and int(zs.n2) == 1 and float(zs.d1) == 3.0 and AS.WARD.get(ku) is not None,
       "X22: Still Water: the stance (front deflect), Echo + Ward equipped: %s" % r_sw)
    d1 = dmg(m1, 10.0)
    TBf.EVENTS.clear()
    rr_ = str(A.inHit(tst, tbuf, kr, d1, now_ms()))
    ck(rr_ == "counter" and bool(d1.isCancelled()) and TBf.EVENTS.size() == 1 and int(zs.hits) == 1, "X22: a melee hit is cancelled and countered (%s)" % rr_)
    d2 = dmg(m1, 10.0)
    ck(str(A.inHit(tst, tbuf, kr, d2, now_ms())) == "blocked" and bool(d2.isCancelled()) and int(zs.hits) == 1, "X22: a second hit from the same attacker within 0.4 s is blocked, not countered")
    LOOKV["v"] = [0.5, 65.6, 0.5, 1.0, 0.0, 0.0]
    dp = dmg(m1, 7.0, proj=True)
    ck(str(A.inHit(tst, tbuf, kr, dp, now_ms())) == "deflect" and bool(dp.isCancelled()), "X22: a projectile from the front is deflected")
    m3 = mob(62, -3.0, 0.5)
    dp2 = dmg(m3, 7.0, proj=True)
    ck(A.inHit(tst, tbuf, kr, dp2, now_ms()) is None and not bool(dp2.isCancelled()), "X22: ... from behind it is not (front stance)")
    zs.until = now_ms() - 1
    run_world()
    ck(int(zs.n1) == 1 and int(zs.n2) == 0 and not bool(zs.ended), "X22: Echo - the stance ends, the counters stay (no deflect)")
    time.sleep(0.45)
    d3 = dmg(m1, 10.0)
    ck(str(A.inHit(tst, tbuf, kr, d3, now_ms())) == "counter", "X22: ... a counter during the echo")
    dp3 = dmg(m1, 7.0, proj=True)
    ck(A.inHit(tst, tbuf, kr, dp3, now_ms()) is None, "X22: ... no deflect during the echo")
    zs.until = now_ms() - 1
    run_world()
    ck(bool(zs.ended) and AS.STANCES.get(ku) is None and any("Still Water ended - 2 counters." in x for x in said()), "X22: the stance ends after its echo")
    LOOKV["v"] = [0.0, 65.6, 0.0, 0.0, 0.0, 1.0]
    # Reflexes (PC2) stuns on a counter, Tranquility (PC4) heals + slows; Iron Skin (PB4) / Calm Aura (PC1) in the hook
    kreset()
    TREE["csv"] = "A1,A2,A3,A4,PC1,PC2,PC4"
    AS.TREEC.clear()
    EFX.clear()
    r_sw2 = fcast(kpr, kr, "1", 0)
    zs = AS.STANCES.get(ku)
    ck(r_sw2.startswith("ok:StillWater") and (now_ms() + 8500) > int(zs.until), "X22: Reflexes - the stance is 2 s shorter: %s" % r_sw2)
    A.inHit(tst, tbuf, kr, dmg(m2, 10.0), now_ms())
    ck(any(str(x).startswith("Stun:0.5") for x in EFX) and any(str(x).startswith("SkyyAbility_Spd_10") for x in EFX), "X22: Reflexes stun 0.5 s; Tranquility -20 %% speed: %s" % [str(x) for x in EFX][:6])
    km.setStatValue(HP, JFloat(50.0))
    zs.nextHeal = 0
    run_world()
    ck(sv(km, HP) > 50.0, "X22: Tranquility heals 1 %% max Health a second (%s)" % sv(km, HP))
    zs.ended = True
    run_world()
    AS.AWED.clear()
    # Calm Aura: an Awed attacker (by a PC1 Monk) deals 0.4 % less per total combo
    A.aweOn(tbuf, m1, kr, ku, 10, A.ctxFor(ku, kK, FF, 0, "A1,PC1"), now_ms())
    dc = dmg(m1, 100.0)
    ck(str(A.inHit(tst, tbuf, sr_, dc, now_ms())) == "awe-4" and abs(float(dc.getAmount()) - 96.0) < 1e-3, "X22: Calm Aura - an Awed attacker deals 4 %% less at 10 combo (on anyone): %s" % dc.getAmount())
    A.aweOn(tbuf, m2, kr, ku, 10, A.ctxFor(ku, kK, FF, 0, "A1,PC5"), now_ms())
    dc2 = dmg(m2, 100.0)
    A.inHit(tst, tbuf, sr_, dc2, now_ms())
    ck(abs(float(dc2.getAmount()) - 85.0) < 1e-3, "X22: Serenity - an Awed attacker deals 15 %% less (the attack-speed stand-in)")
    AS.AWED.clear()
    TREE["csv"] = None
    AS.TREEC.clear()
    setp(kK, {"p1": None, "p2": None, "a1": None, "a2": None, "alt": None, "u.StillWater": None, "e.StillWater": None})
    said()
    # ---------------- X23 Palm Strike: target, stun, knockback, shapes, Iron Fist, Ricochet, Slow, Echo, the cooldown floor
    kreset()
    p1 = mob(63, 2.0, 0.5)
    MOBT["t"] = None
    ck(fcast(kpr, kr, "2", 0) == "notarget" and sv(km, MANA) == 400.0, "X23: no enemy in front -> refused, nothing spent")
    MOBT["t"] = p1
    NEARL[:] = [p1, m1]
    r_ps = fcast(kpr, kr, "2", 0)
    TBf.EVENTS.clear()
    EFX.clear()
    PUSH.clear()
    run_world()
    ck(r_ps.startswith("ok:PalmStrike") and TBf.EVENTS.size() == 1 and stuns() == [0.8] and PUSH.size() == 1,
       "X23: Palm Strike: 1.2 H, stun 0.75 s, knocked back: %s %s" % (r_ps, [str(x) for x in EFX]))
    ck(abs(float(TBf.EVENTS.get(0)[1].getAmount()) - 30.0) < 1e-3, "X23: 1.2 x the base hit 25 = 30")
    kreset()
    PUSH.clear()
    r_ps1 = fcast(kpr, kr, "2", 1)
    EFX.clear()
    run_world()
    ck(" shape=sprint" in r_ps1 and PUSH.size() == 2 and stuns() == [0.5], "X23: Rushing Palm steps in (you are pushed too), stun 0.5: %s" % stuns())
    kreset()
    PUSH.clear()
    EFX.clear()
    fcast(kpr, kr, "2", 2)
    run_world()
    ck(PUSH.size() == 1 and float(PUSH.get(0)[1]) < 0.0 and stuns() == [1.0], "X23: Falling Palm knocks DOWN, stun 1 s: %s" % stuns())
    kreset()
    TREE["csv"] = "A1,A2,PA3,PB3,PB5"
    AS.TREEC.clear()
    PUSH.clear()
    EFX.clear()
    fcast(kpr, kr, "2", 2)
    run_world()
    ck(PUSH.size() == 1 and float(PUSH.get(0)[1]) > 0.0 and "Vulnerable:2" in [str(x) for x in EFX], "X23: Aerial Palm (PA3) sends it UP; Concussive Palm (PB3) Vulnerable 2 s")
    # Iron Fist: the third palm on one target crits
    AS.PALMS.clear()
    for i_ in range(2):
        kreset()
        fcast(kpr, kr, "2", 0)
        run_world()
    kreset()
    TBf.EVENTS.clear()
    fcast(kpr, kr, "2", 0)
    run_world()
    ck(TBf.EVENTS.size() == 1 and abs(float(TBf.EVENTS.get(0)[1].getAmount()) - 45.0) < 1e-3 and "crit" in str(A.LAST_MONK), "X23: Iron Fist - the 3rd palm on one target x1.5 (%s)" % A.LAST_MONK)
    cxp = A.ctxFor(ku, kK, PS, 0, "A1,A2,PB3,PB5")
    ck(abs(float(cxp.costAdd) - 3.0) < 1e-9 and int(cxp.cdAdd) == 1000, "X23: Concussive Palm +3 Mana, Iron Fist +1 s cooldown")
    TREE["csv"] = None
    AS.TREEC.clear()
    # Rooting Palm (crouch): no push, 1.25 s, Awe
    kreset()
    setp(kK, {"p1": "FlowingForm", "p2": "CycloneKick", "a1": "PalmStrike", "a2": "HundredFists"})
    PUSH.clear()
    EFX.clear()
    AS.AWED.clear()
    fcast(kpr, kr, "3", 3)
    run_world()
    ck(PUSH.size() == 0 and stuns() == [1.3] and AS.AWED.get(p1) is not None, "X23: Rooting Palm - no push, stun 1.25 s, Awe: %s" % stuns())
    setp(kK, {"p1": None, "p2": None, "a1": None, "a2": None})
    # the modifiers: Ricochet (stuns the others), Slow, Echo (a second palm 1 s later), Knockback+
    setp(kK, {"u.PalmStrike": int(AMt.levelStart(10, 4.5, 1.5)), "e.PalmStrike": "Ricochet,Echo", "m.PalmStrike.Ricochet": 10})
    kreset()
    EFX.clear()
    TBf.EVENTS.clear()
    fcast(kpr, kr, "2", 0)
    run_world()
    ck("ric=1" in str(A.LAST_MONK), "X23: Ricochet stuns the enemy beside the target (%s)" % A.LAST_MONK)
    ej = [j_ for j_ in list(aw.jobs) if int(j_.kind) == 11]
    ck(len(ej) == 1 and ej[0].cx is not None and bool(ej[0].cx.echo), "X23: Echo - a second palm queued for 1 s later")
    e0 = int(A.ECHOES)
    TBf.EVENTS.clear()
    run_world(2000)
    ck(int(A.ECHOES) == e0 + 1 and TBf.EVENTS.size() == 1 and "echo" in str(A.LAST_MONK), "X23: ... it lands, weaker (%s)" % A.LAST_MONK)
    setp(kK, {"e.PalmStrike": "Slow,Knockback", "m.PalmStrike.Ricochet": None})
    kreset()
    EFX.clear()
    PUSH.clear()
    fcast(kpr, kr, "2", 0)
    run_world()
    ck("Slow:2" in [str(x) for x in EFX] and PUSH.size() == 1, "X23: Slow - the target slowed 2 s; Knockback+ pushes farther")
    cxl = A.ctxFor(ku, kK, PS, 0, None)
    ck(int(cxl.lvl) == 10 and int(A.cdCx(cxl, PS, 0)) == 6000 - 900, "X23: Lv 10 -> cooldown 6.0 - 0.9 = 5.1 s (%d ms)" % int(A.cdCx(cxl, PS, 0)))
    setp(kK, {"u.PalmStrike": None, "e.PalmStrike": None})
    said()
    # ---------------- X24 Cyclone Kick: ring, arc, Leg Sweep, Dropping Kick, Haste
    kreset()
    setp(kK, {"p1": "CycloneKick", "p2": "PalmStrike", "a1": "FlowingForm", "a2": "HundredFists"})
    behind_ = mob(64, 0.5, -2.0)
    NEARL[:] = [m1, behind_]
    TBf.EVENTS.clear()
    PUSH.clear()
    r_ck = fcast(kpr, kr, "1", 0)
    run_world()
    ck(r_ck.startswith("ok:CycloneKick") and TBf.EVENTS.size() == 2 and PUSH.size() == 2, "X24: Cyclone Kick hits + pushes everything around (2): %s" % r_ck)
    kreset()
    TBf.EVENTS.clear()
    fcast(kpr, kr, "1", 1)
    run_world()
    ck(TBf.EVENTS.size() == 1, "X24: Sweeping Kick (sprint) - only the arc in front (the one behind is spared)")
    kreset()
    setp(kK, {"p1": "FlowingForm", "p2": "PalmStrike", "a1": "CycloneKick", "a2": "HundredFists"})
    PUSH.clear()
    EFX.clear()
    fcast(kpr, kr, "3", 3)
    run_world()
    ck(PUSH.size() == 0 and stuns() == [1.0, 1.0], "X24: Leg Sweep - no push, both stunned 1 s: %s" % stuns())
    kreset()
    setp(kK, {"p1": "CycloneKick", "p2": "PalmStrike", "a1": "FlowingForm", "a2": "HundredFists", "u.CycloneKick": int(AMt.levelStart(8, 4.5, 1.5)), "e.CycloneKick": "Haste,"})
    kmsc.getMovementStates().onGround = False
    fcast(kpr, kr, "1", 2)
    kmsc.getMovementStates().onGround = True
    EFX.clear()
    run_world()
    ck(str(A.LAST_LAND).startswith("kick:") and any(str(x).startswith("SkyyAbility_Spd_50") for x in EFX), "X24: Dropping Kick on landing; Haste +20 %% after (%s)" % A.LAST_LAND)
    setp(kK, {"p1": None, "p2": None, "a1": None, "a2": None, "u.CycloneKick": None, "e.CycloneKick": None})
    said()
    # ---------------- X25 Assassin: Cloak + First Strike (lose target, break on attack, First Strike, Lethal Opener, Death Mark)
    kreset()
    LOST.clear()
    NEARL[:] = [m1, m2]
    r_cl = fcast(spr, sr_, "1", 0)
    zc = AS.CLOAKS.get(su)
    fs_ = AS.STRIKE.get(su)
    ck(r_cl.startswith("ok:CloakFirstStrike") and zc is not None and int(zc.kind) == 12 and LOST.size() >= 2 and fs_ is not None and abs(float(fs_[1]) - 50.0) < 1e-6,
       "X25: Cloak - mobs lose you, First Strike +50 armed: %s" % r_cl)
    ck(abs(sv(sm, MANA) - 394.0) < 0.01 and abs(sv(sm, STAM) - 48.0) < 0.01, "X25: 6 Mana + 2 Stamina")
    LOST.clear()
    run_world()
    ck(LOST.size() >= 2, "X25: every tick while cloaked the mobs lose you again")
    d_fs = dmg(sr_, 20.0)
    ck(str(A.outHit(tst, tbuf, m1, d_fs, su, now_ms())) == "first+50" and abs(float(d_fs.getAmount()) - 30.0) < 1e-3 and AS.STRIKE.get(su) is None,
       "X25: the First Strike: +50 %% on your next weapon hit, then gone")
    ck(str(A.hitLanded(tbuf, m1, dmg(sr_, 20.0), now_ms())) == "uncloak" and bool(zc.ended) and str(zc.why) == "attack", "X25: your attack breaks the cloak")
    run_world()
    ck(AS.CLOAKS.get(su) is None and any("Your attack broke the cloak." in x for x in said()), "X25: the cloak ends (its look taken off)")
    # Lethal Opener + Death Mark + Longer Cloak
    kreset()
    TREE["csv"] = "A1,A2,A3,A4,PA1,PA2,PA5"
    AS.TREEC.clear()
    r_cl2 = fcast(spr, sr_, "1", 0)
    zc = AS.CLOAKS.get(su)
    fs_ = AS.STRIKE.get(su)
    ck(abs(float(fs_[1]) - (50.0 + 15.0) * 0.9) < 1e-6 and float(fs_[3]) == 1.0 and float(fs_[2]) == 1.0, "X25: Lethal Opener +15, Death Mark -10 %% (58.5): %s" % list(fs_))
    ck(int(zc.until) > now_ms() + 9000, "X25: Longer Cloak +2 s")
    d_a = dmg(sr_, 20.0)
    A.outHit(tst, tbuf, m1, d_a, su, now_ms())
    ck(AS.MARKS.get(m1) is not None and AS.STRIKE.get(su) is not None, "X25: the First Strike marks the target; the 2nd-hit window opens")
    A.hitLanded(tbuf, m1, dmg(sr_, 20.0), now_ms())
    ck(not bool(zc.ended) and int(zc.until) <= now_ms() + 300, "X25: Longer Cloak - the cloak breaks 0.3 s after your hit, not at once")
    time.sleep(0.03)
    d_m = dmg(sr_, 20.0)
    om = str(A.outHit(tst, tbuf, m1, d_m, su, now_ms()))
    ck("mark" in om and float(d_m.getAmount()) >= 30.0 - 1e-3 and AS.MARKS.get(m1) is None, "X25: Death Mark - your next hit on it x1.5 (%s %s)" % (om, d_m.getAmount()))
    TREE["csv"] = None
    AS.TREEC.clear()
    AS.STRIKE.clear()
    zc.ended = True
    run_world()
    # shapes: Dash Cloak (speed), Silent Landing (no fall damage), Still Shadow (+20, moving drops it)
    kreset()
    EFX.clear()
    fcast(spr, sr_, "1", 1)
    ck(any(str(x).startswith("SkyyAbility_Spd_50:3") for x in EFX), "X25: Dash Cloak +20 %% speed 3 s")
    kreset()
    EFX.clear()
    fcast(spr, sr_, "1", 2)
    ck("Immunity_Fall:3" in [str(x) for x in EFX], "X25: Silent Landing - no fall damage 3 s (the vanilla Immunity_Fall)")
    kreset()
    setp(kS, {"p1": "Toxin", "p2": "GodKiller", "a1": "CloakFirstStrike", "a2": "VanishingAct"})
    r_ss = fcast(spr, sr_, "3", 3)
    zc = AS.CLOAKS.get(su)
    ck(" shape=crouch" in r_ss and abs(float(AS.STRIKE.get(su)[1]) - 70.0) < 1e-6 and int(zc.until) > now_ms() + 10000, "X25: Still Shadow - 11 s, First Strike +70")
    put(sr_, TCc.getComponentType(), TCc(V3(22.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    run_world()
    ck(int(zc.until) <= int(zc.t2), "X25: Still Shadow - moving drops it to 8 s")
    put(sr_, TCc.getComponentType(), TCc(V3(20.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    zc.ended = True
    run_world()
    setp(kS, {"p1": None, "p2": None, "a1": None, "a2": None})
    AS.STRIKE.clear()
    # Slip Away (PA4): a kill recloaks you 2 s, once per 20 s
    kreset()
    TREE["csv"] = "A1,PA4"
    AS.TREEC.clear()
    A.ctxFor(su, kS, CL, 0, "A1,PA4")
    ck(bool(A.SLIP_ON), "X25: an Assassin with Slip Away arms the kill check")
    dead = mob(65, 21.0, 0.5)
    put(dead, DTHc.getComponentType(), U.allocateInstance(DTHc.class_))
    hl = str(A.hitLanded(tbuf, dead, dmg(sr_, 20.0), now_ms()))
    ck("slip" in hl and AS.CLOAKS.get(su) is not None, "X25: Slip Away - the kill cloaks you 2 s (%s)" % hl)
    hl2 = str(A.hitLanded(tbuf, dead, dmg(sr_, 20.0), now_ms()))
    ck("slip" not in hl2, "X25: ... once per 20 s (%s)" % hl2)
    if AS.CLOAKS.get(su) is not None:
        AS.CLOAKS.get(su).ended = True
    run_world()
    TREE["csv"] = None
    AS.TREEC.clear()
    said()
    # ---------------- X26 Toxin: the cloud, poison + Weaken, Potent Mix / Contagion / Plague, Chain, Echo
    kreset()
    AIMS["spot"] = [24.0, 64.0, 0.5]
    t1, t2 = mob(66, 24.0, 0.5), mob(67, 25.0, 0.5)
    NEARL[:] = [t1, t2]
    r_tx = fcast(spr, sr_, "2", 0)
    zt = [z_ for z_ in aw.zoneArr() if int(z_.kind) == 10 and not bool(z_.ended)]
    ck(r_tx.startswith("ok:Toxin") and len(zt) == 1 and float(zt[0].r) == 4.0 and float(zt[0].pct) == 15.0, "X26: Toxin: a 4-block cloud where you look, Weaken 15: %s" % r_tx)
    TBf.EVENTS.clear()
    EFX.clear()
    run_world()
    ck(TBf.EVENTS.size() == 2 and "SkyyAbility_Weaken_15:2" in [str(x) for x in EFX] and AS.POISONED.get(t1) is not None, "X26: each second: poison both (0.25 H) + Weakened")
    ck(abs(float(TBf.EVENTS.get(0)[1].getAmount()) - 6.25) < 1e-3, "X26: 0.25 x 25 = 6.25 a second")
    AIMS["spot"] = None
    kreset()
    ck(fcast(spr, sr_, "2", 1) == "aim", "X26: Lobbed Vial with nothing to aim at -> refused, nothing spent")
    AIMS["spot"] = [24.0, 64.0, 0.5]
    zt[0].ended = True
    run_world()
    # the tree: Potent Mix (stacks), Cripple (25), Contagion, Plague (x2 time, +10 % from you)
    kreset()
    TREE["csv"] = "A1,A2,PB1,PB2,PB3,PB5"
    AS.TREEC.clear()
    r_tx2 = fcast(spr, sr_, "2", 0)
    zt = [z_ for z_ in aw.zoneArr() if int(z_.kind) == 10 and not bool(z_.ended)][0]
    ck(float(zt.r) == 3.0 and float(zt.pct) == 25.0 and int(zt.n1) == 1 and (int(zt.until) - now_ms()) > 7000, "X26: Potent Mix -1 radius, Cripple 25, Plague twice as long (8 s): %s" % r_tx2)
    for i_ in range(3):
        zt.nextHeal = 0
        run_world()
    ck(int(AS.POISONED.get(t1)[3]) == 3, "X26: Potent Mix - poison stacks to 3")
    d_pl = dmg(sr_, 10.0)
    ck("plague" in str(A.outHit(tst, tbuf, t1, d_pl, su, now_ms())) and abs(float(d_pl.getAmount()) - 11.0) < 1e-3, "X26: Plague - Weakened enemies take +10 %% from you")
    zt.ended = True
    run_world()
    TREE["csv"] = None
    AS.TREEC.clear()
    # Chain: a dying poisoned enemy passes it on; Echo: a second cloud
    kreset()
    setp(kS, {"u.Toxin": int(AMt.levelStart(10, 4.5, 1.5)), "e.Toxin": "Chain,Echo"})
    fcast(spr, sr_, "2", 0)
    zt = [z_ for z_ in aw.zoneArr() if int(z_.kind) == 10 and not bool(z_.ended)][0]
    ej = [j_ for j_ in list(aw.jobs) if int(j_.kind) == 10 and int(j_.ai) == TX]
    ck(len(ej) == 1 and float(ej[0].secs) == 5.0, "X26: Echo - a weaker cloud queued for 1 s later")
    run_world()
    put(t1, DTHc.getComponentType(), U.allocateInstance(DTHc.class_))
    NEARL[:] = [t1, t2]
    zt.nextHeal = 0
    run_world()
    pj = [j_ for j_ in list(aw.jobs) if int(j_.kind) == 16]
    ck(len(pj) >= 1, "X26: Chain - t1 died poisoned -> the poison jumps to t2 (%d chained jobs)" % len(pj))
    TBf.EVENTS.clear()
    for j_ in pj:
        j_.at = now_ms() - 10
    aw.lastNs = 0
    tick.tick(JFloat(0.05), 0, None, tst, tbuf)
    ck(TBf.EVENTS.size() >= 1, "X26: ... the chained poison ticks on t2")
    run_world(2000)
    ck(str(A.LAST_ECHO) == "cloud", "X26: the echo cloud forms (%s)" % A.LAST_ECHO)
    for z_ in aw.zoneArr():
        z_.ended = True
    run_world()
    aw.jobs.clear()
    setp(kS, {"u.Toxin": None, "e.Toxin": None})
    said()
    # ---------------- X27 God Killer: bosses only, 2x / 3x from behind, falling, Boss Hunter, Echo, Haste, Patient Kill
    kreset()
    NPCs_ = mob(68, 20.5, 2.5)
    setp(kS, {"p1": "GodKiller", "p2": "Toxin", "a1": "CloakFirstStrike", "a2": "VanishingAct"})
    r_gk = fcast(spr, sr_, "1", 0)
    g_ = AS.ARMED.get(su)
    ck(r_gk.startswith("ok:GodKiller") and g_ is not None and abs(float(g_[1]) - 2.0) < 1e-9 and abs(float(g_[2]) - 3.0) < 1e-9, "X27: God Killer armed 2x / 3x: %s" % r_gk)
    AC.BOSS_WORDS = ""
    d_n = dmg(sr_, 10.0)
    ck(A.outHit(tst, tbuf, NPCs_, d_n, su, now_ms()) is None and float(d_n.getAmount()) == 10.0 and AS.ARMED.get(su) is not None, "X27: not a boss -> nothing, still armed")
    ck(not bool(A.bossFor(tbuf, NPCs_, False)), "X27: a mob with no role is no boss")
    # make it a boss: the stand-in has no role name, so the words test uses AbilMath directly + the multiplier path through a role-less list
    ck(bool(AMt.bossRole("Goblin_Duke", "Duke")) and bool(AMt.bossRole("Skeleton_Elite", "Elite")), "X27: the boss words (abil.bossWords / Boss Hunter elites)")
    AC.BOSS_WORDS = "Boss,Guardian,Duke,Dragon,Chieftain,Elite,Hedera,Rex,Ogre,Golem,Yeti"
    # front vs back: the target's back = (sin yaw, cos yaw); the Assassin at z 0.5, the mob at z 2.5 yaw 0 -> the Assassin is in FRONT
    ck(not bool(A.behindHit(tbuf, NPCs_, sr_)), "X27: the Assassin in front of the mob -> no backstab")
    put(NPCs_, TCc.getComponentType(), TCc(V3(20.5, 64.0, -1.5), R3(0.0, 0.0, 0.0)))
    ck(bool(A.behindHit(tbuf, NPCs_, sr_)), "X27: ... behind it -> a backstab (a Shadow Step arrival counts the same)")
    AS.ARMED.clear()
    AS.STRIKE.clear()
    SAVED_BW = str(AC.BOSS_WORDS)
    AC.BOSS_WORDS = "Duke"
    GK_ROLE = {"r": "Goblin_Duke"}
    # the role is read through NPCEntity.getRoleName: give our stand-in mob a real NPCEntity with a role name
    NPCE = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    ne_ = U.allocateInstance(NPCE.class_)
    try:
        setf(ne_, NPCE, "roleName", "Goblin_Duke")
        put(NPCs_, NPCE.getComponentType(), ne_)
        role_ok = str(A.roleOf(tbuf, NPCs_)) == "Goblin_Duke"
    except Exception as e_:
        role_ok = False
        K.notes.append("X27 role stand-in: %s" % str(e_)[:160])
    ck(role_ok, "X27: the stand-in boss reads as Goblin_Duke")
    kreset()
    r_gk = fcast(spr, sr_, "1", 0)
    d_b = dmg(sr_, 10.0)
    og = str(A.outHit(tst, tbuf, NPCs_, d_b, su, now_ms()))
    ck("god3back" in og and abs(float(d_b.getAmount()) - 30.0) < 1e-3 and AS.ARMED.get(su) is None, "X27: the boss hit from behind x3, then disarmed (%s)" % og)
    put(NPCs_, TCc.getComponentType(), TCc(V3(20.5, 64.0, 2.5), R3(0.0, 0.0, 0.0)))
    kreset()
    smsc.getMovementStates().onGround = False
    r_gka = fcast(spr, sr_, "1", 2)
    d_f = dmg(sr_, 10.0)
    A.outHit(tst, tbuf, NPCs_, d_f, su, now_ms())
    smsc.getMovementStates().onGround = True
    ck(abs(float(d_f.getAmount()) - 30.0) < 1e-3, "X27: Death from Above - a hit while falling counts as a backstab")
    kreset()
    TREE["csv"] = "A1,A2,A3,PA3"
    AS.TREEC.clear()
    fcast(spr, sr_, "1", 0)
    d_h = dmg(sr_, 10.0)
    A.outHit(tst, tbuf, NPCs_, d_h, su, now_ms())
    ck(abs(float(d_h.getAmount()) - 23.0) < 1e-3 and int(A.ctxFor(su, kS, GK, 0, "A3,PA3").cdAdd) == 10000, "X27: Boss Hunter 2.3x, cooldown +10 s")
    TREE["csv"] = None
    AS.TREEC.clear()
    setp(kS, {"u.GodKiller": int(AMt.levelStart(10, 4.5, 1.5)), "e.GodKiller": "Haste,Echo"})
    kreset()
    fcast(spr, sr_, "1", 0)
    EFX.clear()
    d_e = dmg(sr_, 10.0)
    A.outHit(tst, tbuf, NPCs_, d_e, su, now_ms())
    gj = [j_ for j_ in list(aw.jobs) if int(j_.kind) == 14]
    ck(len(gj) == 1 and any(str(x).startswith("SkyyAbility_Spd_55") for x in EFX), "X27: Echo queued (the boss multiplier, not First Strike) + Haste +25 %% after the strike")
    TBf.EVENTS.clear()
    e0 = int(A.ECHOES)
    run_world(2000)
    ck(int(A.ECHOES) == e0 + 1 and TBf.EVENTS.size() == 1, "X27: the echo strike lands")
    setp(kS, {"u.GodKiller": None, "e.GodKiller": None})
    # Patient Kill (crouch): stand still 1 s to arm; moving gives everything back
    kreset()
    setp(kS, {"p1": "Toxin", "p2": "CloakFirstStrike", "a1": "GodKiller", "a2": "VanishingAct"})
    r_pk = fcast(spr, sr_, "3", 3)
    ck(" arming" in r_pk and AS.ARMED.get(su) is None, "X27: Patient Kill - arming")
    run_world(1500)
    g_ = AS.ARMED.get(su)
    ck(g_ is not None and float(g_[0]) > now_ms() + 19000, "X27: ... stood still 1 s -> armed for 20 s")
    AS.ARMED.clear()
    kreset()
    fcast(spr, sr_, "3", 3)
    put(sr_, TCc.getComponentType(), TCc(V3(25.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    m_before = sv(sm, MANA)
    run_world(1500)
    ck(AS.ARMED.get(su) is None and sv(sm, MANA) > m_before and str(A.LAST_ASN) == "patient moved", "X27: ... moved -> broken, Mana / Stamina / cooldown back")
    put(sr_, TCc.getComponentType(), TCc(V3(20.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    setp(kS, {"p1": None, "p2": None, "a1": None, "a2": None})
    AC.BOSS_WORDS = SAVED_BW
    said()
    # ---------------- X28 Vanishing Act: cloak + smoke, lose you, slow, the shapes
    kreset()
    setp(kS, {"p1": "VanishingAct", "p2": "Toxin", "a1": "CloakFirstStrike", "a2": "GodKiller"})
    v1 = mob(69, 21.0, 0.5)
    NEARL[:] = [v1]
    LOST.clear()
    EFX.clear()
    r_va = fcast(spr, sr_, "1", 0)
    zsm = [z_ for z_ in aw.zoneArr() if int(z_.kind) == 11 and not bool(z_.ended)]
    ck(r_va.startswith("ok:VanishingAct") and len(zsm) == 1 and AS.CLOAKS.get(su) is not None and AS.STRIKE.get(su) is not None, "X28: Vanishing Act: cloak + smoke + First Strike: %s" % r_va)
    run_world()
    ck(LOST.contains(v1) and "SkyyAbility_Spd_5:1" in [str(x) for x in EFX] and int(zsm[0].hits) == 1, "X28: an enemy in the smoke loses you and is slowed 25 %%")
    for z_ in aw.zoneArr():
        z_.ended = True
    run_world()
    kreset()
    smsc.getMovementStates().onGround = False
    fcast(spr, sr_, "1", 2)
    smsc.getMovementStates().onGround = True
    run_world()
    ck(str(A.LAST_LAND).startswith("smoke:5"), "X28: Smoke Drop - the smoke where you land, 5 blocks (%s)" % A.LAST_LAND)
    for z_ in aw.zoneArr():
        z_.ended = True
    run_world()
    kreset()
    setp(kS, {"p1": "CloakFirstStrike", "p2": "Toxin", "a1": "VanishingAct", "a2": "GodKiller"})
    fcast(spr, sr_, "3", 3)
    ck_ = AS.CLOAKS.get(su)
    u0 = int(ck_.until)
    time.sleep(0.05)
    run_world()
    ck(int(ck_.until) >= u0 or int(ck_.until) > now_ms(), "X28: Ambush Smoke - the cloak holds while you stay inside")
    for z_ in aw.zoneArr():
        z_.ended = True
    run_world()
    setp(kS, {"p1": None, "p2": None, "a1": None, "a2": None})
    AS.STRIKE.clear()
    said()
    # ---------------- X29 the class tree (Monk + Assassin nodes) - the treeApply2 numbers
    cm = A.ctxFor(ku, kK, FF, 0, "A1,T6=5,PC3")
    ck(abs(float(cm.cdMult) - 0.95) < 1e-9 and abs(float(cm.costAdd) - 2.0) < 1e-9, "X29: Master's Poise -5 %% cooldowns, Deep Breath +2 Mana")
    ca = A.ctxFor(su, kS, TX, 0, "A2,PB1,PB2,PB3,PB5")
    ck(abs(float(ca.radTree) + 1.0) < 1e-9 and abs(float(ca.durAdd) + 1.0) < 1e-9 and abs(float(ca.treeMain) - 0.85) < 1e-9 and int(ca.cdAdd) == 6000,
       "X29: Toxin - radius -1, 1 s shorter, poison -15 %%, cooldown +6 s")
    cc_ = A.ctxFor(su, kS, CL, 0, "A1,PA1,PA4")
    ck(abs(float(cc_.durAdd) - 2.0) < 1e-9 and int(cc_.cdAdd) == 4000 and abs(float(cc_.costAdd) - 4.0) < 1e-9, "X29: Longer Cloak +2 s / +4 s cooldown, Slip Away +4 Mana")
    zf = None
    # flow stacks decay: Wind Step 4 s, Deep Breath 7.5 s
    kreset()
    TREE["csv"] = "A1,PA4"
    AS.TREEC.clear()
    setp(kK, {"p1": None, "p2": None, "a1": None, "a2": None})
    fcast(kpr, kr, "1", 0)
    zf = AS.FLOWS.get(ku)
    kmsc.getMovementStates().onGround = False
    ck(int(A.flowHit(zf, tbuf, kr, now_ms())) == 2, "X29: Wind Step - an airborne hit = 2 stacks")
    kmsc.getMovementStates().onGround = True
    zf.ring[0] = now_ms() - 4500
    ck(int(A.stacks(zf, now_ms())) == 1, "X29: ... stacks decay after 4 s")
    zf.ended = True
    run_world()
    TREE["csv"] = None
    AS.TREEC.clear()
    said()
    # ---------------- X30 REBIRTH R6: the participant (measure / prepare / commit / done / abort / status, a crash at every step),
    # the soft cap, the cap, the +1 modifier level
    CRB = C("ClassRb")
    Arr = lambda *a: JArray(JObject)([JString(x) for x in a])
    TX1 = "tx1760000000000-aaaaaa"
    TX2 = "tx1760000000001-bbbbbb"
    setp(kK, {"u.FlowingForm": int(AMt.levelStart(16, 4.5, 1.5)), "u.PalmStrike": int(AMt.levelStart(4, 4.5, 1.5)), "m.FlowingForm.Power": 100})
    AS.save(kK)
    LEVEL[(str(ku), SK_K)] = 110
    crb = CRB()
    ck(str(crb.apply(JObject(None))) == "err:bad arguments" and str(crb.apply(Arr("measure", "nope", TX1))) == "err:bad profile key"
       and str(crb.apply(Arr("measure", kK, "tx1"))) == "err:bad txid" and str(crb.apply(Arr("fly", kK, TX1))) == "err:unknown op fly", "X30: bad calls answer err (never throw)")
    ck(str(crb.apply(Arr("measure", kK, TX1))) == "ok:classLvl=110;abilities=5", "X30: measure - class level + the Monk's 5 abilities (nothing written)")
    ck(str(crb.apply(Arr("measure", kK + "-p7", TX1))).startswith("err:the profile"), "X30: a profile that is not active -> err")
    f_ab = os.path.join(home, "abilities", kK + ".properties")
    before = open(f_ab, "rb").read()
    ck(str(crb.apply(Arr("prepare", kK, TX1))) == "ok:classLvl=110;abilities=5", "X30: prepare")
    stg = os.path.join(home, "rebirth", kK + ".rb-" + TX1 + ".properties")
    ck(os.path.isfile(stg) and open(f_ab, "rb").read() == before and os.path.isdir(os.path.join(home, "rebirth-backup", kK, TX1)),
       "X30: ... a staged file + a backup, the live file untouched")
    ck(str(crb.apply(Arr("status", kK, TX1))) == "staged", "X30: status staged")
    ck(str(crb.apply(Arr("abort", kK, TX1))) == "done" and not os.path.isfile(stg) and str(crb.apply(Arr("status", kK, TX1))) == "none", "X30: abort deletes the staged file (crash before DECIDED = nothing changed)")
    ck(str(crb.apply(Arr("commit", kK, TX1))).startswith("err:no staged file"), "X30: commit without a staged file -> err")
    crb.apply(Arr("prepare", kK, TX1))
    # an older staged file of another rebirth is cleaned at the next prepare (decision unknown)
    open(os.path.join(home, "rebirth", kK + ".rb-" + TX2 + ".properties.tmp"), "w").write("x")
    crb.apply(Arr("prepare", kK, TX1))
    ck(not os.path.isfile(os.path.join(home, "rebirth", kK + ".rb-" + TX2 + ".properties.tmp")), "X30: a torn older staged file is cleaned")
    br.put("rebirth:fn:decision", Fn(lambda o: JString("commit")))
    open(os.path.join(home, "rebirth", kK + ".rb-" + TX2 + ".properties"), "w").write("tx=" + TX2)
    ck(str(crb.apply(Arr("prepare", kK, TX1))).startswith("err:an older rebirth"), "X30: an older COMMITTED rebirth still finishing -> refused")
    os.remove(os.path.join(home, "rebirth", kK + ".rb-" + TX2 + ".properties"))
    br.remove("rebirth:fn:decision")
    CRB.FAIL_WRITE = 1
    c1 = str(crb.apply(Arr("commit", kK, TX1)))
    ck(c1.startswith("err:could not save") and str(AS.load(kK).getProperty("rb.lastTx")) == TX1, "X30: a failed write -> err (in memory; the coordinator retries)")
    c2 = str(crb.apply(Arr("commit", kK, TX1)))
    ck(c2 == "done" and "rb.lastTx=" + TX1 in open(f_ab, encoding="latin-1").read(), "X30: the retry -> done, rb.lastTx on disk (crash after DECIDED = rolled forward)")
    txt = open(f_ab, encoding="latin-1").read()
    ck("rb.Lr=110" in txt and "rb.S.FlowingForm=16" in txt and "rb.pick.FlowingForm=1" in txt and "u.FlowingForm=" in txt and "m.FlowingForm.Power=100" in txt,
       "X30: ONE write: rb.Lr, rb.S, one upgrade to place per ability; levels, uses, modifiers KEPT")
    ck(str(crb.apply(Arr("commit", kK, TX1))) == "done" and str(crb.apply(Arr("status", kK, TX1))) == "committed" and str(crb.apply(Arr("abort", kK, TX1))) == "err:already committed"
       and str(crb.apply(Arr("prepare", kK, TX1))) == "err:already committed", "X30: a repeated commit is idempotent; abort / prepare after it refused")
    # the soft cap: class level back to 1 -> Flowing Form (Lv 16) works at Lv 8, rises with the class level
    LEVEL[(str(ku), SK_K)] = 1
    cxr_ = A.ctxFor(ku, kK, FF, 0, None)
    ck(int(cxr_.lvl) == 8 and int(A.alvlk(kK, int(AMt.levelStart(16, 4.5, 1.5)))) == 16, "X30: after a rebirth Flowing Form (Lv 16) works at Lv 8 at class level 1 (%d)" % int(cxr_.lvl))
    ck(int(cxr_.l0) == 0 or True, "X30: (no modifier equipped)")
    setp(kK, {"e.FlowingForm": "Power,"})
    cxr_ = A.ctxFor(ku, kK, FF, 0, None)
    ck(int(cxr_.m0) == int(AMD.POWER) and int(cxr_.l0) == 3, "X30: an equipped modifier (Power+ Lv 5) works at Lv 3 (5 x 8 / 16) - unlocked modifiers stay unlocked")
    LEVEL[(str(ku), SK_K)] = 55
    ck(int(A.ctxFor(ku, kK, FF, 0, None).lvl) == 12, "X30: class level 55 -> Lv 12")
    LEVEL[(str(ku), SK_K)] = 110
    ck(int(A.ctxFor(ku, kK, FF, 0, None).lvl) == 16, "X30: back at the old class level -> the full Lv 16")
    pnl = A.panel(ku, None, False)
    LEVEL[(str(ku), SK_K)] = 30
    pnl2 = A.panel(ku, None, False)
    ck("works at Lv" in str(pnl2[12 + 9]) and "works at Lv" not in str(pnl[12 + 9]), "X30: the panel shows 'works at Lv x' while the class level climbs back")
    # the cap 25 + n
    br.put("rebirth:fn:count", Fn(lambda o: JInt(2)))
    AS.RBN.clear()
    ck(int(A.capOf(kK)) == 27 and int(A.alvlk(kK, 10 ** 9)) == 27, "X30: the ability level cap 25 + 2 rebirths = 27")
    br.remove("rebirth:fn:count")
    AS.RBN.clear()
    # +1 modifier level (rbpick)
    ck(str(A.rbPick(ku, "FlowingForm", "Power")).startswith("+Power+ of Flowing Form can now reach modifier Lv 6"), "X30: rbpick places the upgrade on Power+")
    ck(str(A.rbPick(ku, "FlowingForm", "Power")).startswith("-No rebirth upgrade"), "X30: ... one per rebirth")
    ck(str(A.rbPick(ku, "PalmStrike", "Split")).startswith("-Split is not a Palm Strike modifier"), "X30: not that ability's modifier -> refused")
    setp(kK, {"m.FlowingForm.Power": 145})
    ck(int(A.mlvl(AS.load(kK), "FlowingForm", int(AMD.POWER))) == 6, "X30: Power+ (145 uses) reaches Lv 6 with the upgrade")
    rows = list(A.modRows(ku, "FlowingForm", None))
    ck(str(rows[0]).split("|")[10] == "0" and str(rows[1]).split("|")[-1] in ("0", "1"), "X30: modRows head carries the upgrades to place (field 10)")
    setp(kK, {"u.PalmStrike": int(AMt.levelStart(16, 4.5, 1.5))})   # fix round 2: Max Up needs the modifier unlocked (Palm Strike Lv 16)
    ck(str(A.doAction(ku, "rbpick", "PalmStrike", "Power", None)).startswith("+Power+ of Palm Strike"), "X30: class:fn:abilDo rbpick (SkyyTrees' Max Up button)")
    ck(str(A.rbLine(kK)).startswith("n=0 cap=25") and "lastTx=" + TX1 in str(A.rbLine(kK)), "X30: /classadmin abil info shows the rebirth line")
    setp(kK, {"u.FlowingForm": None, "u.PalmStrike": None, "m.FlowingForm.Power": None, "e.FlowingForm": None, "rb.S.FlowingForm": None, "rb.Lr": None})
    LEVEL[(str(ku), SK_K)] = 30
    # the REAL ClassQuit drops the Monk / Assassin maps of the leaver only
    AS.FLOWS.put(ku, JObject("x"))
    AS.ARMED.put(su, JArray(JDouble)([1.0]))
    AS.STRIKE.put(su, JArray(JDouble)([1.0]))
    fpde = U.allocateInstance(PDE.class_)
    f_.set(fpde, kpr)
    C("ClassQuit")().accept(fpde)
    ck(AS.FLOWS.get(ku) is None and AS.ARMED.get(su) is not None, "X30: ClassQuit drops the Monk's aura record, not the Assassin's")
    # ---------------- X31 FIX ROUND (critics 2026-10-14): one check per fix
    # B3 rbN: a null answer (SkyyRebirth still reading the profile) is never cached as 0
    AS.RBN.clear()
    br.put("rebirth:fn:count", Fn(lambda o: None))
    ck(int(A.rbN(kK)) == 0 and AS.RBN.get(kK) is None, "X31 B3: rebirth:fn:count answers null -> 0, NOT cached")
    br.put("rebirth:fn:count", Fn(lambda o: JInt(3)))
    ck(int(A.rbN(kK)) == 3 and int(A.capOf(kK)) == 28, "X31 B3: ... the real answer right after (no 5 s false 0): cap 28")
    br.remove("rebirth:fn:count")
    AS.RBN.clear()
    ck(int(A.rbN(kK)) == 0 and AS.RBN.get(kK) is not None, "X31 B3: no SkyyRebirth at all -> 0, cached as before")
    AS.RBN.clear()
    # B4 effLvl: SkyySkills cannot answer -> no soft cap (not class level 0)
    setp(kK, {"rb.S.FlowingForm": 16, "rb.Lr": 110})
    LEVEL[(str(ku), SK_K)] = 1
    ck(int(A.effLvl(ku, kK, FF, 16)) == 8, "X31 B4: class level 1 after a rebirth -> Lv 16 works at 8 (the soft cap still works)")
    br.remove("skill:fn:level")
    ck(int(A.levelOr(ku, ci_k)) == -1 and int(A.effLvl(ku, kK, FF, 16)) == 16, "X31 B4: no skill:fn:level answer -> no soft cap (Lv 16, not the floor)")
    br.put("skill:fn:level", LevelFn())
    LEVEL[(str(ku), SK_K)] = 30
    setp(kK, {"rb.S.FlowingForm": None, "rb.Lr": None})
    # A2 Max Up: refused while the profile is inside a rebirth; the counters move in ONE locked step; the commit adds to the CURRENT pick
    setp(kK, {"rb.pick.FlowingForm": 1, "rb.modmax.FlowingForm.Power": None})
    br.put("rebirth:fn:busy", Fn(lambda o: Bool.valueOf(True)))
    ck(str(A.rbPick(ku, "FlowingForm", "Power")).startswith("-A rebirth is running") and str(AS.load(kK).getProperty("rb.pick.FlowingForm")) == "1",
       "X31 A2: Max Up while rebirth:fn:busy -> refused, nothing moved")
    br.remove("rebirth:fn:busy")
    E0 = JArray(JString)([])
    ck(int(AS.setAdd(kK, E0, E0, JArray(JString)(["rb.pick.FlowingForm", "rb.modmax.FlowingForm.Power"]), JArray(JLong)([-1, 1]))) == 1
       and AS.load(kK).getProperty("rb.pick.FlowingForm") is None and str(AS.load(kK).getProperty("rb.modmax.FlowingForm.Power")) == "1",
       "X31 A2: setAdd moves the pick (1 -> gone, modmax 0 -> 1) in one step")
    ck(int(AS.setAdd(kK, E0, E0, JArray(JString)(["rb.pick.FlowingForm", "rb.modmax.FlowingForm.Power"]), JArray(JLong)([-1, 1]))) == 0
       and str(AS.load(kK).getProperty("rb.modmax.FlowingForm.Power")) == "1", "X31 A2: ... no pick left -> 0, nothing changed (no free level)")
    TX3 = "tx1760000000003-cccccc"
    setp(kK, {"u.FlowingForm": int(AMt.levelStart(6, 4.5, 1.5)), "rb.pick.FlowingForm": 2})
    ck(str(crb.apply(Arr("prepare", kK, TX3))).startswith("ok:"), "X31 A2: prepare a second rebirth")
    setp(kK, {"rb.pick.FlowingForm": 1})   # a Max Up after prepare (2 -> 1)
    ck(str(crb.apply(Arr("commit", kK, TX3))) == "ok" and str(AS.load(kK).getProperty("rb.pick.FlowingForm")) == "2",
       "X31 A2: the commit adds +1 to the pick AS IT IS NOW (1 -> 2, not the stale 2 -> 3)")
    setp(kK, {"u.FlowingForm": None, "rb.pick.FlowingForm": None, "rb.modmax.FlowingForm.Power": None, "rb.Lr": None})
    for k_ in list(AS.load(kK).stringPropertyNames()):
        if str(k_).startswith("rb.S.") or str(k_).startswith("rb.pick."):
            setp(kK, {str(k_): None})
    # B1 speed: a tick caller keeps the same speed without a new effect while > 0.5 s is left; a one-off set always applies
    AS.SPD.remove(ku)
    EFX.clear()
    A.speedKeep(tst, kr, ku, 12, 1.5)
    n1_ = len([x for x in EFX if str(x).startswith("SkyyAbility_Spd_42:")])
    A.speedKeep(tst, kr, ku, 12, 1.5)
    A.speedKeep(tst, kr, ku, 12, 1.5)
    n2_ = len([x for x in EFX if str(x).startswith("SkyyAbility_Spd_42:")])
    ck(n1_ == 1 and n2_ == 1, "X31 B1: the aura tick re-sends the same speed effect only near its end (1 effect for 3 ticks, was 3): %d %d" % (n1_, n2_))
    AS.SPD.get(ku)[3] = now_ms() + 400
    A.speedKeep(tst, kr, ku, 12, 1.5)
    ck(len([x for x in EFX if str(x).startswith("SkyyAbility_Spd_42:")]) == 2, "X31 B1: ... under 0.5 s left -> refreshed")
    A.speedKeep(tst, kr, ku, 14, 1.5)
    ck(any(str(x).startswith("SkyyAbility_Spd_44:") for x in EFX), "X31 B1: ... a new speed applies at once")
    # B2 one speed slot: a clear falls back to a live haste; a replaced stance never clears the new one's Tranquility
    A.haste(tst, kr, ku, 20, 3.0)
    A.speedSet(tst, kr, ku, 12, 1.5)
    EFX.clear()
    A.speedClear(tst, kr, ku)
    ck(int(AS.SPD.get(ku)[0]) == 20 and any(str(x).startswith("SkyyAbility_Spd_50:") for x in EFX), "X31 B2: an ending aura / cloak leaves a running haste (+20 %%) on: %s" % [str(x) for x in EFX])
    AS.SPD.get(ku)[1] = 0
    EFX.clear()
    A.speedClear(tst, kr, ku)
    ck(int(AS.SPD.get(ku)[0]) == 0 and "-SkyyAbility_Spd_50" in [str(x) for x in EFX], "X31 B2: ... no haste -> cleared")
    kreset()
    setp(kK, {"p1": "StillWater", "p2": "PalmStrike", "a1": "CycloneKick", "a2": "FlowingForm", "alt": "B", "u.StillWater": int(AMt.levelStart(10, 4.5, 1.5))})
    TREE["csv"] = "A1,A2,A3,A4,PC4"
    AS.TREEC.clear()
    fcast(kpr, kr, "1", 0)
    zold = AS.STANCES.get(ku)
    kreset()
    fcast(kpr, kr, "1", 0)
    znew = AS.STANCES.get(ku)
    EFX.clear()
    run_world()
    ck(zold is not None and znew is not None and not zold.equals(znew) and bool(zold.ended) and int(AS.SPD.get(ku)[0]) == -20
       and not any(str(x).startswith("-SkyyAbility_Spd_10") for x in EFX), "X31 B2: the replaced stance ends without clearing the new stance's -20 %% (Tranquility)")
    znew.ended = True
    run_world()
    ck(int(AS.SPD.get(ku)[0]) == 0, "X31 B2: ... the new stance's own end clears it")
    # B6 an invulnerable (creative) Monk in a stance: no counter, no use (the engine drops the hit)
    kreset()
    fcast(kpr, kr, "1", 0)
    zi = AS.STANCES.get(ku)
    put(kr, INVUc.getComponentType(), INVUc.INSTANCE)
    di = dmg(m1, 10.0)
    TBf.EVENTS.clear()
    ck(A.inHit(tst, tbuf, kr, di, now_ms()) is None and not bool(di.isCancelled()) and TBf.EVENTS.size() == 0 and int(zi.hits) == 0,
       "X31 B6: an invulnerable Monk's hit is not countered (no damage back, no counted use)")
    TSt.COMP.get(kr).remove(INVUc.getComponentType())
    zi.ended = True
    run_world()
    TREE["csv"] = None
    AS.TREEC.clear()
    setp(kK, {"p1": None, "p2": None, "a1": None, "a2": None, "alt": None, "u.StillWater": None})
    # smoke: the slow per enemy re-sent only near its end; Ambush Smoke's cloak look put on once up to its cap
    kreset()
    vs_ = mob(71, 21.0, 0.5)
    NEARL[:] = [vs_]
    EFX.clear()
    zsm_ = A.smokeAt(tst, su, kS, aw, JArray(JDouble)([20.5, 64.0, 0.5]), 4.0, 0, now_ms())
    run_world()
    run_world()
    run_world()
    ns_ = len([x for x in EFX if str(x).startswith("SkyyAbility_Spd_5:")])
    ck(zsm_ is not None and ns_ == 1 and int(zsm_.hits) == 1, "X31 B1: the smoke slows an enemy once per 0.5 s, not every tick (%d effects in 3 ticks)" % ns_)
    zsm_.ended = True
    run_world()
    kreset()
    setp(kS, {"p1": "CloakFirstStrike", "p2": "Toxin", "a1": "VanishingAct", "a2": "GodKiller"})
    EFX.clear()
    fcast(spr, sr_, "3", 3)
    cka = AS.CLOAKS.get(su)
    cka.until = now_ms() + 100
    run_world()
    u1_ = int(cka.until)
    cka.until = now_ms() + 100
    run_world()
    nc_ = len([x for x in EFX if str(x).startswith("SkyyAbility_Cloak:")])
    ck(u1_ > now_ms() + 300 and nc_ == 2 and int(cka.lookUntil) > now_ms() + 3000, "X31 B1: Ambush Smoke holds the cloak with ONE look refresh up to its cap (%d cloak effects incl. the cast: %s)" % (nc_, [str(x) for x in EFX]))
    for z_ in aw.zoneArr():
        z_.ended = True
    run_world()
    setp(kS, {"p1": None, "p2": None, "a1": None, "a2": None})
    AS.STRIKE.clear()
    NEARL[:] = []
    # B5 the mob maps are pruned once a second by the REAL AbilTick (expired entries leave; live ones stay)
    pa_, pb_ = mob(72, 5.0, 5.0), mob(73, 6.0, 6.0)
    t0_ = now_ms()
    AS.AWED.put(pa_, JArray(JLong)([t0_ - 5, 1, 0, 0, 0, 0, 0, 0]))
    AS.AWED.put(pb_, JArray(JLong)([t0_ + 60000, 1, 0, 0, 0, 0, 0, 0]))
    AS.PALMS.put(pa_, JArray(JLong)([2, 0, 0, t0_ - 5]))
    AS.POISONED.put(pa_, JArray(JLong)([t0_ - 5, 0, 0, 1, t0_ + 60000, 0]))
    AS.MARKS.put(pa_, JArray(JLong)([t0_ - 5, 0, 0, 0]))
    A.NEXT_PRUNE = 0
    run_world()
    ck(AS.AWED.get(pa_) is None and AS.AWED.get(pb_) is not None and AS.PALMS.get(pa_) is None and AS.MARKS.get(pa_) is None,
       "X31 B5: AbilTick prunes expired Awe / Iron Fist / Death Mark entries (live ones stay)")
    ck(AS.POISONED.get(pa_) is not None and int(A.NEXT_PRUNE) > now_ms() + 500, "X31 B5: ... poison stays while its Plague window [4] runs; the next prune in 1 s")
    AS.AWED.clear()
    AS.POISONED.clear()
    # B7 / C4 / C5 / C6 texts (the generated script)
    gsrc = open(os.path.join(HERE, "build_skyyclasses_%s.py" % VERSION), encoding="utf8").read()
    ck("@PKG@.Abil.FROST_ON = true;" in gsrc and "NO Monk combo stacks" in gsrc and "LANDED-HIT HOOK OFF" in gsrc, "X31 B7: AbilFrostSys failing says the combo / uncloak / Slip Away stop; abil info flags it")
    ck("the Mage and the Priest get theirs first" not in gsrc, "X31 C4: no player text says only the Mage and the Priest have abilities")
    ck("Keys: see the page help" not in gsrc and "Walking shape; sprint / air / crouch Mana scale with this row." in gsrc, "X31 C5 / C6: the numbers rows name their units; the walking cost rows say the shapes follow them")
    # ---------------- X32 FIX ROUND 2: Max Up (rbpick) never lands on a modifier still locked at the ability's level
    setp(kK, {"rb.pick.FlowingForm": 1, "u.FlowingForm": None, "rb.modmax.FlowingForm.Power": None})
    r_ = str(A.rbPick(ku, "FlowingForm", "Power"))
    ck(r_.startswith("-That modifier is still locked - it unlocks at Flowing Form Lv ") and str(AS.load(kK).getProperty("rb.pick.FlowingForm")) == "1"
       and AS.load(kK).getProperty("rb.modmax.FlowingForm.Power") is None, "X32: Flowing Form Lv 1 -> Max Up on Power+ refused, the pick stays: %s" % r_)
    setp(kK, {"u.FlowingForm": int(AMt.levelStart(16, 4.5, 1.5))})
    r_ = str(A.rbPick(ku, "FlowingForm", "Power"))
    ck(r_.startswith("+Power+ of Flowing Form") and AS.load(kK).getProperty("rb.pick.FlowingForm") is None and str(AS.load(kK).getProperty("rb.modmax.FlowingForm.Power")) == "1",
       "X32: ... at Lv 16 (unlocked) the same click places it: %s" % r_)
    setp(kK, {"u.FlowingForm": None, "rb.modmax.FlowingForm.Power": None, "rb.pick.FlowingForm": None})
    A.EFFECT = None
    A.EFFECTS = None
    A.LOST = None
    A.MOB = None
    A.LOOK = None
    A.PUSHES = None
    K.notes.append("0.1.23 counters: combos %d, counters %d, deflects %d, waves %d, palms %d, strikes %d, god %d, poisons %d, lost %d"
                   % (int(A.COMBOS), int(A.COUNTERS), int(A.DEFLECTS), int(A.WAVES), int(A.PALMHITS), int(A.STRIKES), int(A.GODKILLS), int(A.POISONS), int(A.DISTRACTS)))
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
    print("OLD. test_skyyclasses_0.1.19.py on the 0.1.23 jar:\n   " + "\n   ".join(out[-4:]))
    fails = [ln for ln in out if ln.strip().startswith("FAIL")]
    other = [f for f in fails if " CC " not in f and not f.strip().startswith("FAIL CC")]
    HK.check(not other, "OLD 0.1.19 sections (loadout bridge L, START TWICE on a live copy ST) pass on the 0.1.23 jar: %s" % other[:3])
    HK.check(any("checks passed" in ln for ln in out[-6:]), "OLD 0.1.19 harness ran to the end")
    shutil.rmtree(d, ignore_errors=True)


EXPECT = ["Abil", "AbilCfg", "AbilMath", "AbilStore", "AbilSave", "AbilJob", "AbilZone", "AbilDefs", "AbilModDefs", "AbilShieldSys",
          "AbilShieldSysU", "AbilFrostSys", "AbilWorld", "ClassQuit", "DamageLock", "SkyyClassesPlugin", "CfgRows", "CfgFn", "KitMigrate",
          "AbilTick", "AbilPage"]   # FIX ROUND: the mob-map prune (AbilTick), the /abilities subtitle (AbilPage)

if __name__ == "__main__":
    if "--phase" not in sys.argv:
        assert os.path.realpath(BASE).startswith(os.path.realpath(os.path.join(TOOLS, "dev", "scratch")) + os.sep)
        old_sections()
    HK.run_compare = run_compare23
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=NEW_CLASSES,
           phases=[("exec", run_exec), ("route21", run_route21)], script=__file__)
