"""Harness for SkyyAbilityProbe 0.1 (Hytale 0.7 release jar). Build first:
    python SkyyAbilityProbe/build_skyyabilityprobe_0.1.py

    python SkyyAbilityProbe/test_skyyabilityprobe_0.1.py [--keep]

  J  (parent) the jar: manifest (Main, Version, IncludesAssetPack FALSE), exactly the 13 classes, NO asset file (nothing overridden); the
     build script never passes --deploy; old vs new class compare = n/a (a NEW mod, no earlier jar)
  A  (child, -Xverify:all -XX:-UsePerfData, game JRE) every class loads, links and initialises; no class is left with an unimplemented
     abstract method (an execute / tick / handle whose signature drifted would silently not override)
  L  AbLogic on plain data: f1 / number / dnum / word / low / perSec / ring / budget / slotOk / kind / yn / join / moveText /
     cancelVerdict (PASS / Mana spent / cooldown running) / p15Text / cdRow
  R  THE STATE-RESET RULE: every AbState probe field set to a non-rest value, AbCmds.clear() puts EVERY one back; plan() clears first
     (p1 cancel -> p4 watch drops the cancel flag + the pending Mana check), refused plans leave the state at rest, finish() clears,
     summary() = one line per timed probe
  X  EVERY code path EXECUTED on real engine objects (module instances + component types allocated, a ComponentAccessor stand-in that
     holds REAL components: AbilitySlots / RuneBag with real SimpleItemContainers, InteractionManager with a real CooldownHandler,
     MovementStatesComponent, TransformComponent, EntityStatMap / EntityStatValue, PlayerRef; Item stand-ins in a stand-in Item asset
     store: a Core rune, a Support rune, a weapon, food):
       /aprobe (help), info, stats, stop, unknown; p1 armed -> REAL InteractionChainStartEvents (Ability2 with a rune + weapon, Ability3
       with food = canUseWith NO, Primary, a broken chain) through AbChainSys.handle; p1 cancel -> the event reads back cancelled, the 1 s
       Mana + server-cooldown check via the tick (PASS and FAIL); the 40-line chat cap -> log only; the window end -> summary; p3 list
       (empty + filled) / set / clear / usage / missing handler; p4 read / put (unknown id, full slot, ok) / take (not ours, ours, empty)
       / bad (no hand, rune in hand, full slot, refused by the REAL engine slot filter = PASS, accepted by a filterless container = FAIL +
       removed) / usage; p4 watch -> REAL InventoryChangeEvents (AbilitySlots / RuneBag / other) through AbInvSys.handle; p13 ticks
       (scan error path, budget, summary); p14 (with + without a bridge profile key); p15 (readable + unreadable); a world change ends a
       probe; the three systems' handle / tick wrappers (null chunk, empty STATES, a throwing call -> logged once); the root command's
       execute(); the four usage variants' execute() through a REAL CommandContext; plugin shutdown() clears
  P  permissions: node skyyabilityprobe.admin, EMPTY permission groups on the root and its 4 variants, getPermissionGroupsRecursive() gives
     the node to no group; /aprobe + alias /abilityprobe; never /abilities
  B  setup()'s calls read from the jar's bytecode (logger, registerCommand(AProbeCmd), registerSystem AbTick / AbInvSys / AbChainSys, the
     "[SkyyAbilityProbe] 0.1 ready" line the smoke test needs)
  D  START TWICE ON A SCRATCH COPY OF LIVE DATA: the live player files (read-only) copied to scratch; two fresh child JVMs each run the
     state / p14 / p15 / p3 paths for every copied player's real uuid + name; the probe writes NOTHING (every scratch file byte-identical,
     no new file) and no state carries into the second start
  F  critic fixes: p4 take / stop only remove the EXACT ItemStack copy the probe put (a swapped-in same-id rune stays), put refuses
     non-runes + warns, stop takes back, p3 ends a running p1 cancel, the cancel check uses the rune Cast root id, no PASS / FAIL /
     CHECK word in non-verdict lines, every U7 id found + no desk line near the 600-char cap
  AA the ENGINE-ACCESS AUDIT: every class / field / method reference of the jar resolved with MethodHandles.privateLookupIn the referencing
     class - 0 refused; the control (a protected engine call) refused
Not testable without the game (the point of the probe): which inputs the client sends for the rune keys, whether a cancel leaves a stuck
animation, whether a server-set cooldown fills the HUD slot, profile switching. Scratch: tools/dev/scratch/abilprobe/test (deleted at the
end unless --keep). Exit 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, hashlib, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.1"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyAbilityProbe-%s.jar" % VERSION)))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "abilprobe", "test")))
PKG = "com.skyy.abilprobe."
CLASSES = sorted(PKG + c for c in ["AbLog", "AbLogic", "AbState", "AbCmds", "AbTick", "AbChainSys", "AbInvSys", "AProbeArg1Cmd",
                                   "AProbeArg2Cmd", "AProbeArg3Cmd", "AProbeArg4Cmd", "AProbeCmd", "SkyyAbilityProbePlugin"])
CMDS = ["AProbeCmd", "AProbeArg1Cmd", "AProbeArg2Cmd", "AProbeArg3Cmd", "AProbeArg4Cmd"]
NODE = "skyyabilityprobe.admin"
KEEP = {"u", "ref", "st", "ns", "nsMax", "ticks"}
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def deploy_world():
    try:
        for l in open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8"):
            if l.startswith("WORLD = "):
                return l.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    return "HUD mod"


LIVE = os.path.abspath(arg("--live", os.path.join(B.USERDATA, "Saves", deploy_world(), "universe", "players")))


class Child(object):
    def __init__(self, out):
        self.out, self.ok, self.fails, self.notes = out, 0, [], []

    def check(self, cond, what):
        if cond:
            self.ok += 1
        else:
            self.fails.append(what)
            print("FAIL", what)

    def save(self, **extra):
        d = {"ok": self.ok, "fails": self.fails, "notes": self.notes}
        d.update(extra)
        json.dump(d, open(self.out, "w"), indent=1)


def _jvm(cp, verify=True):
    import jpype
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    opts = (["-Xverify:all"] if verify else []) + ["-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                                                   "--add-opens=java.base/java.lang=ALL-UNNAMED"]
    jpype.startJVM(jvm, *opts, classpath=list(cp), convertStrings=True)


# ====================================================================================================== parent: J
def part_static():
    z = zipfile.ZipFile(JAR)
    man = json.loads(z.read("manifest.json"))
    check(man["Main"] == PKG + "SkyyAbilityProbePlugin" and man["Version"] == VERSION and man["Name"] == "%s SkyyAbilityProbe" % VERSION,
          "J. manifest Main / Version / Name: %s" % man)
    check(man.get("IncludesAssetPack") is False, "J. manifest IncludesAssetPack false (no assets shipped)")
    cls = sorted(n[:-6].replace("/", ".") for n in z.namelist() if n.endswith(".class"))
    check(cls == CLASSES, "J. exactly the 13 classes: %s" % cls)
    other = sorted(n for n in z.namelist() if not n.endswith(".class") and n != "manifest.json")
    check(other == [], "J. no asset file (nothing vanilla / pack-owned overridden): %s" % other)
    src = open(os.path.join(HERE, "build_skyyabilityprobe_0.1.py"), encoding="utf-8").read()
    check('if "--deploy" in sys.argv:\n    raise SystemExit' in src and "B.deploy(" not in src, "J. the build never deploys")
    old = [f for f in os.listdir(HERE) if f.startswith("SkyyAbilityProbe-") and f.endswith(".jar") and f != os.path.basename(JAR)]
    print("J. class compare old vs new: n/a - a NEW mod (no earlier SkyyAbilityProbe jar: %s)" % (old or "none"))


# ====================================================================================================== child E: engine (A L R X P B)
def run_engine(out):
    from jpype import JClass, JArray, JString, JInt, JFloat, JLong, JShort, JByte, JBoolean, JObject
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR, B.JAVASSIST])
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    JMod = JClass("java.lang.reflect.Modifier")
    # ---------------- A
    for n in CLASSES:
        try:
            c = Cls.forName(n, True, loader)
            c.getDeclaredMethods()
            K.ok += 1
            if not JMod.isAbstract(c.getModifiers()):
                ab = [str(m.getName()) for m in c.getMethods() if JMod.isAbstract(m.getModifiers())]
                K.check(not ab, "A. %s leaves abstract methods unimplemented: %s" % (n, ab))
        except Exception as e:
            K.check(False, "A. load " + n + ": " + str(e))
    print("A. loaded + linked + initialised %d classes (-Xverify:all)" % len(CLASSES))
    if K.fails:
        K.save()
        return
    # ---------------- L
    L = JClass(PKG + "AbLogic")
    K.check(str(L.f1(16.97)) == "17.0" and str(L.f1(float("nan"))) == "?" and str(L.f1(-2.04)) == "-2.0", "L. f1")
    K.check(L.number("x", 30, 5, 300) == 30 and L.number("999", 30, 5, 300) == 300 and L.number("2", 30, 5, 300) == 5, "L. number")
    K.check(L.dnum("NaN", 3.0, 0.0, 9.0) == 3.0 and L.dnum("15", 0.0, 0.0, 90.0) == 15.0 and L.dnum("200", 8.0, 0.5, 120.0) == 120.0, "L. dnum")
    SA = JArray(JString)
    K.check(L.word(SA(["p1", " "]), 1) is None and L.word(None, 0) is None and str(L.word(SA(["p4", "put", "0", "Rune_X"]), 3)) == "Rune_X",
            "L. word (ids keep their case)")
    K.check(L.low(None) is None and str(L.low("P1")) == "p1", "L. low")
    K.check(L.perSec(30, 1000) == 30.0 and L.perSec(5, 0) == 0.0, "L. perSec")
    r0, r4 = L.ring(10.0, 20.0, 4.0, 0, 16), L.ring(10.0, 20.0, 4.0, 4, 16)
    K.check(abs(r0[0] - 14) < 1e-9 and abs(r0[1] - 20) < 1e-9 and abs(r4[0] - 10) < 1e-9 and abs(r4[1] - 24) < 1e-9
            and L.ring(0.0, 0.0, 1.0, 0, 0) is not None, "L. ring")
    K.check(str(L.budget(500.0, 1000.0)).startswith("PASS") and str(L.budget(1500.0, 1000.0)).startswith("OVER"), "L. budget")
    K.check(L.slotOk(0, 6) and L.slotOk(5, 6) and not L.slotOk(6, 6) and not L.slotOk(-1, 6), "L. slotOk")
    K.check(L.kind("Ability2") == 1 and L.kind("Ability3") == 1 and L.kind("Ability1") == 0 and L.kind("Primary") == 0 and L.kind(None) == 0,
            "L. kind")
    K.check(str(L.yn(True)) == "y" and str(L.join(None)) == "-" and str(L.join(SA([]))) == "-" and str(L.join(SA(["a", "b"]))) == "a,b",
            "L. yn / join")
    K.check(str(L.moveText(False, True, True, True, False)) == "movement unknown"
            and str(L.moveText(True, False, True, True, False)) == "crouch n, sprint y, roll y, in air y", "L. moveText")
    v1, v2, v3 = str(L.cancelVerdict(50.0, 50.0, 0.0)), str(L.cancelVerdict(50.0, 20.0, 0.0)), str(L.cancelVerdict(50.0, 50.0, 1.5))
    K.check(v1.startswith("PASS") and v2.startswith("FAIL") and "Mana went DOWN" in v2 and v3.startswith("FAIL") and "1.5 s left" in v3,
            "L. cancelVerdict: %s | %s | %s" % (v1, v2, v3))
    K.check("Expect:" in str(L.p15Text(30.0, 55.0, 100.0)) and "Compare:" in str(L.p15Text(30.0, 155.0, 100.0))
            and "Expect:" in str(L.p15Text(30.0, 55.0, -1.0)), "L. p15Text")
    p15all = [str(L.p15Text(30.0, 55.0, 100.0)), str(L.p15Text(30.0, 155.0, 100.0)), str(L.p15Text(30.0, 55.0, -1.0))]
    K.check(not any(re.search(r"PASS|FAIL|CHECK", x) for x in p15all), "L. FIX4 p15Text says no PASS / FAIL / CHECK (no verdict): %s" % p15all)
    K.check(str(L.cdRow("R", 8.0, 3.0, 1)) == "R: max 8.0 s, 3.0 s left, 1 charge slot(s)" and "unreadable" in str(L.cdRow("R", 8.0, -1.0, -1))
            and "ready" in str(L.cdRow("R", 8.0, 0.0, -1)), "L. cdRow")

    # ---------------- engine stand-ins
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cname, fname, val):
        f = Cls.forName(cname).getDeclaredField(fname)
        f.setAccessible(True)
        f.set(obj, val)

    def alloc(cname):
        return U.allocateInstance(Cls.forName(cname))
    CT = "com.hypixel.hytale.component.ComponentType"
    for mod in ("com.hypixel.hytale.server.core.modules.entity.EntityModule", "com.hypixel.hytale.server.core.universe.Universe",
                "com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule",
                "com.hypixel.hytale.server.core.modules.interaction.InteractionModule"):
        mc = Cls.forName(mod)
        inst = U.allocateInstance(mc)
        for f in mc.getDeclaredFields():
            f.setAccessible(True)
            if JMod.isStatic(f.getModifiers()):
                if f.getType() == mc:
                    f.set(None, inst)
            elif str(f.getType().getName()) == CT:
                f.set(inst, alloc(CT))
    PR, ABS, RNB = (JClass("com.hypixel.hytale.server.core.universe.PlayerRef"),
                    JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$AbilitySlots"),
                    JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$RuneBag"))
    ESM, ESV = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap"), JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue")
    MSC, MST = JClass("com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent"), JClass("com.hypixel.hytale.protocol.MovementStates")
    TCC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    IMOD, IMGR = JClass("com.hypixel.hytale.server.core.modules.interaction.InteractionModule"), JClass("com.hypixel.hytale.server.core.entity.InteractionManager")
    CDH = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.CooldownHandler")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    types = {"pr": PR.getComponentType(), "abs": ABS.getComponentType(), "rnb": RNB.getComponentType(), "esm": ESM.getComponentType(),
             "msc": MSC.getComponentType(), "tc": TCC.getComponentType(), "im": IMOD.get().getInteractionManagerComponent(),
             "pla": PLA.getComponentType()}
    K.check(all(v is not None for v in types.values()) and len(set(id(v) for v in types.values())) == len(types),
            "X. stand-in modules give distinct component types: %s" % [k for k, v in types.items() if v is None])
    # a ComponentAccessor stand-in that holds real components (plain class: implements the interface, nothing else)
    cp = JClass("javassist.ClassPool")(True)
    cp.appendClassPath(B.SERVER_JAR)
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    fa = cp.makeClass("skyyabtest.FakeAcc")
    fa.addInterface(cp.get("com.hypixel.hytale.component.ComponentAccessor"))
    fa.addField(CtF.make("public java.util.Map comps = new java.util.IdentityHashMap();", fa))
    fa.addField(CtF.make("public static int CALLS;", fa))
    fa.addConstructor(CtC.make("public FakeAcc() { }", fa))
    fa.addMethod(CtM.make("""public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  CALLS++;
  if (r == null) return null;
  java.util.Map m = (java.util.Map) this.comps.get(r);
  return m == null ? null : (com.hypixel.hytale.component.Component) m.get(t);
}""", fa))
    fa.addMethod(CtM.make("""public void put(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t, Object c) {
  java.util.Map m = (java.util.Map) this.comps.get(r);
  if (m == null) { m = new java.util.IdentityHashMap(); this.comps.put(r, m); }
  if (c == null) m.remove(t); else m.put(t, c);
}""", fa))
    FakeAcc = JClass(fa.toClass())
    # the Item asset store stand-in (the SkyySacks harness pattern): CUSTOM id -> our Item stand-ins
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    fs = cp.makeClass("com.hypixel.hytale.assetstore.SkyyAbTestStore", cp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fs.addConstructor(CtC.make("public SkyyAbTestStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fs))
    FSC = fs.toClass(AS.class_)
    DAMN = "com.hypixel.hytale.assetstore.map.DefaultAssetMap"
    km = cp.makeClass("com.hypixel.hytale.assetstore.map.SkyyAbTestMap", cp.get(DAMN))
    km.addField(CtF.make("public static final java.util.HashMap CUSTOM = new java.util.HashMap();", km))
    km.addConstructor(CtC.make("public SkyyAbTestMap() { super(); }", km))
    km.addMethod(CtM.make("public com.hypixel.hytale.assetstore.JsonAsset getAsset(Object key) { return key == null ? null : "
                          "(com.hypixel.hytale.assetstore.JsonAsset) CUSTOM.get(key); }", km))
    KMap = JClass(km.toClass(JClass(DAMN).class_))
    istore = U.allocateInstance(FSC)
    setf(istore, "com.hypixel.hytale.assetstore.AssetStore", "assetMap", KMap())
    ITN = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
    setf(None, ITN, "ASSET_STORE", istore)
    CIA = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CoreItemAbility")
    SIA = JClass("com.hypixel.hytale.server.core.asset.type.item.config.SupportItemAbility")
    ACT = JClass("com.hypixel.hytale.protocol.AbilityCostType")

    def item(iid, ability=None, weapon=False):
        it = alloc(ITN)
        setf(it, ITN, "id", iid)
        setf(it, ITN, "maxStack", JInt(1))
        if ability is not None:
            setf(it, ITN, "ability", ability)
        if weapon:
            setf(it, ITN, "weapon", alloc("com.hypixel.hytale.server.core.asset.type.item.config.ItemWeapon"))
        KMap.CUSTOM.put(iid, it)
        return it
    core = CIA()
    for fn, v in (("cost", JFloat(30.0)), ("costType", ACT.values()[0]), ("cooldownS", JFloat(2.0)),
                  ("abilityKeywords", SA(["Damage", "Fire"])), ("castRootId", "Root_Ability_Fireball")):
        setf(core, "com.hypixel.hytale.server.core.asset.type.item.config.CoreItemAbility", fn, v)
    sup = SIA()
    setf(sup, "com.hypixel.hytale.server.core.asset.type.item.config.SupportItemAbility", "requiresAnyAbilityKeyword", SA(["Damage"]))
    setf(sup, "com.hypixel.hytale.server.core.asset.type.item.config.SupportItemAbility", "excludesAnyAbilityKeyword", SA(["Poison"]))
    item("Rune_Fireball", core)
    item("Rune_Damage_Up", sup)
    item("Weapon_Staff_Wood", None, True)
    item("Food_Bread")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    K.check(IS("Rune_Fireball", 1).getItem().getAbility() is not None and CIA.class_.isInstance(IS("Rune_Fireball", 1).getItem().getAbility()),
            "X. Item stand-ins: a Core rune resolves through ItemStack.getItem().getAbility()")
    K.check(core.canUseWith(IS("Weapon_Staff_Wood", 1)) and not core.canUseWith(IS("Food_Bread", 1)) and not core.canUseWith(None),
            "X. the engine's canUseWith: weapon YES, food NO, empty hand NO (the desk rule)")

    # the player: Ref + PlayerRef + components
    Ref, UUID = JClass("com.hypixel.hytale.component.Ref"), JClass("java.util.UUID")
    acc = FakeAcc()
    ref = Ref(None, 0)
    K.check(ref.isValid(), "X. a stand-in Ref is valid")
    u = UUID.randomUUID()
    pr = alloc("com.hypixel.hytale.server.core.universe.PlayerRef")
    setf(pr, "com.hypixel.hytale.server.core.universe.PlayerRef", "uuid", u)
    setf(pr, "com.hypixel.hytale.server.core.universe.PlayerRef", "username", "Tester")
    acc.put(ref, types["pr"], pr)
    abs_ = ABS(JShort(6))
    acc.put(ref, types["abs"], abs_)
    bag = RNB(JShort(10))
    acc.put(ref, types["rnb"], bag)
    im = alloc("com.hypixel.hytale.server.core.entity.InteractionManager")
    handler = CDH()
    setf(im, "com.hypixel.hytale.server.core.entity.InteractionManager", "cooldownHandler", handler)
    acc.put(ref, types["im"], im)
    msc = MSC()
    ms = MST()
    ms.sprinting, ms.rolling, ms.onGround = True, True, True
    msc.setMovementStates(ms)
    acc.put(ref, types["msc"], msc)
    tcc = alloc("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    setf(tcc, "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent", "position", JClass("org.joml.Vector3d")(1.0, 64.0, 2.0))
    acc.put(ref, types["tc"], tcc)
    esm = alloc("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    mana = alloc("com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue")
    setf(mana, "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue", "value", JFloat(40.0))
    setf(mana, "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue", "max", JFloat(55.0))
    MI = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes").getMana()
    vals = JArray(ESV)(MI + 1)
    vals[MI] = mana
    setf(esm, "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap", "values", vals)
    acc.put(ref, types["esm"], esm)
    # the hand: a hotbar with the staff (InventoryComponent.getItemInHand reads the Hotbar / Utility / Tool components)
    HB = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar")
    hb = HB(JShort(9))
    hb.getInventory().addItemStackToSlot(JShort(0), IS("Weapon_Staff_Wood", 1))
    acc.put(ref, HB.getComponentType() if HB.getComponentType() is not None else alloc(CT), hb)

    Log, Cmds, St = JClass(PKG + "AbLog"), JClass(PKG + "AbCmds"), JClass(PKG + "AbState")
    SINK = JClass("java.util.ArrayList")()
    Log.SINK = SINK

    def said():
        r = [str(x) for x in SINK]
        SINK.clear()
        return r
    W = lambda *ws: SA(list(ws))

    def run(*ws):
        Cmds.run(ref, acc, pr, W(*ws))
        return said()
    hand_ok = str(Cmds.hand(acc, ref).getItemId()) if Cmds.hand(acc, ref) is not None else None
    K.notes.append("hand item via InventoryComponent.getItemInHand: %s" % hand_ok)
    # the server log: every chat line also goes there as "[SkyyAbilityProbe] to <name>: ..." (what tools/chat_tail.py --grep reads)
    CAP = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    try:
        JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend").subscribe(CAP)
    except Exception as e:
        K.notes.append("log capture: %s" % e)
    Log.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyAbilityProbe")
    # ---------------- X: commands
    h = run()
    K.check(len(h) == 3 and "p1 [cancel]" in h[1], "X. /aprobe = help (3 lines): %s" % h)
    logged = [str(r_.getMessage()) for r_ in list(CAP)]
    K.check(any(x.startswith("[SkyyAbilityProbe] to Tester: Ability probe for Hytale 0.7") for x in logged)
            and any(x == "[SkyyAbilityProbe] Tester ran /aprobe" for x in logged),
            "X. chat lines reach the server log with the [SkyyAbilityProbe] prefix (%d records): %s" % (len(logged), logged[:3]))
    K.check(len(run("help")) == 3, "X. /aprobe help")
    inf = run("info")
    K.check(len(inf) == 1 + len(list(Cmds.DESK)) and "ability section -11" in inf[0] and "rune bag section -12" in inf[0]
            and any("canUseWith" in x for x in inf) and any("Root_Ability_Fireball" in x for x in inf), "X. info + desk lines: %s" % inf[:2])
    K.check(not any("MISSING" in x for x in inf) and all(any(x.startswith("U7 desk: ") and k in x for x in inf) for k in
                                                         ("Ability_Fireball_Impact", "Ability_Cast_Generic", "frost / slow effects: Ability_"))
            and all(len(x) < 600 for x in inf),
            "X. FIX6 U7 desk line: every id found (a missing one stops the build)")
    K.check(run("stats") == ["No probe state."], "X. stats with no state")
    K.check(run("zz") == ["Unknown probe - /aprobe lists them."] and Cmds.STATES.get(u).mode == 0, "X. unknown probe refused, state at rest")
    # p1 needs the hook
    Cmds.CHAIN_ON = False
    Cmds.CHAIN_WHY = "test off"
    r = run("p1")
    K.check(len(r) == 1 and "hook is off" in r[0] and Cmds.STATES.get(u).mode == 0, "X. p1 refused while the hook is off: %s" % r)
    Cmds.CHAIN_ON = True
    r = run("p1")
    s = Cmds.STATES.get(u)
    K.check(len(r) == 1 and r[0].startswith("P1 armed for 60 s") and s.mode == 1 and not s.cancel, "X. p1 armed: %s" % r)
    # REAL InteractionChainStartEvents
    IT = JClass("com.hypixel.hytale.protocol.InteractionType")
    ICSE = JClass("com.hypixel.hytale.server.core.modules.interaction.event.InteractionChainStartEvent")
    ICN, CXN = "com.hypixel.hytale.server.core.entity.InteractionChain", "com.hypixel.hytale.server.core.entity.InteractionContext"
    RIN = "com.hypixel.hytale.server.core.modules.interaction.interaction.config.RootInteraction"

    def event(typ, root, held, sec, slot):
        ch = alloc(ICN)
        setf(ch, ICN, "type", typ)
        if root is not None:
            ri = alloc(RIN)
            setf(ri, RIN, "id", root)
            setf(ch, ICN, "initialRootInteraction", ri)
        cx = alloc(CXN)
        setf(cx, CXN, "heldItem", held)
        setf(cx, CXN, "heldItemSectionId", JInt(sec))
        setf(cx, CXN, "heldItemSlot", JByte(slot))
        setf(ch, ICN, "context", cx)
        return ICSE(ch)
    # through AbChainSys.handle with a stand-in ArchetypeChunk (refs[0] = our ref)
    ACHN = "com.hypixel.hytale.component.ArchetypeChunk"
    chunk = alloc(ACHN)
    rr = JArray(Ref)(1)
    rr[0] = ref
    setf(chunk, ACHN, "refs", rr)
    setf(chunk, ACHN, "entitiesSize", JInt(1))
    chainSys = JClass(PKG + "AbChainSys")()
    e1 = event(IT.Ability2, "Root_Ability_Fireball", IS("Rune_Fireball", 1), -11, 0)
    # handle(int, ArchetypeChunk, Store, CommandBuffer, EcsEvent): the CommandBuffer is our accessor's place - the system passes buf to
    # onChain as a ComponentAccessor, so call onChain directly with the accessor AND the wrapper with a null buffer (early-safe path)
    Cmds.onChain(e1, ref, acc)
    r = said()
    K.check(len(r) == 1 and r[0].startswith("P1 Ability2 root Root_Ability_Fireball, item Rune_Fireball (section -11 slot 0)")
            and "Core rune: cost 30.0" in r[0] and "keywords Damage,Fire" in r[0] and "canUseWith YES" in r[0]
            and "Weapon block y" in r[0] and "sprint y, roll y, in air n" in r[0] and not e1.isCancelled(),
            "X. p1 Ability2 line (rune + staff, moving): %s" % r)
    e2 = event(IT.Ability3, "Root_Food", IS("Food_Bread", 1), 0, 2)
    Cmds.onChain(e2, ref, acc)
    r = said()
    K.check(len(r) == 1 and "P1 Ability3" in r[0] and "not a rune (Food_Bread)" in r[0], "X. p1 Ability3 with food: %s" % r)
    e3 = event(IT.Primary, "Root_Swing", None, 0, 0)
    Cmds.onChain(e3, ref, acc)
    r = said()
    K.check(len(r) == 1 and "P1 Primary root Root_Swing, item nothing" in r[0] and "|" not in r[0], "X. p1 other chain: %s" % r)
    e4 = event(IT.Ability2, None, None, 0, 0)          # no root interaction: the getter throws inside the engine
    chainSys.handle(JInt(0), chunk, None, None, e4)    # buf null -> prOf(null) -> no player -> nothing (the wrapper never throws)
    K.check(said() == [], "X. AbChainSys.handle with no command buffer does nothing")
    Cmds.onChain(e4, ref, acc)
    r = said()
    K.check(len(r) == 1 and r[0].startswith("P1 Ability2 root ? (NullPointerException), item nothing") and "not a rune" not in r[0]
            and "empty" in r[0], "X. a chain without a root interaction still prints (root '?'): %s" % r)
    chainSys.handle(JInt(0), None, None, None, e1)
    chainSys.handle(JInt(0), chunk, None, None, JClass("com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent")(types["abs"], abs_, abs_.getInventory(), None))
    K.check(said() == [], "X. AbChainSys.handle: null chunk / wrong event type ignored")
    # the 40-line chat cap: Primary chains beyond 6 'other' go to the log only
    for i in range(10):
        Cmds.onChain(event(IT.Primary, "Root_Swing", None, 0, 0), ref, acc)
    r = said()
    s = Cmds.STATES.get(u)
    K.check(len(r) == 5 and s.logOnly == 5 and s.chainOther == 11, "X. other chains: 6 in chat, the rest log only (%d, %d, %d)" % (len(r), s.logOnly, s.chainOther))
    s.lines = 40
    Cmds.onChain(event(IT.Ability2, "Root_Ability_Fireball", IS("Rune_Fireball", 1), -11, 0), ref, acc)
    K.check(said() == [] and s.logOnly == 6, "X. past 40 chat lines even ability lines go to the log only")
    # the window end -> summary via the tick
    s.modeUntil = 1
    Cmds.tickPlayer(ref, acc, acc, JFloat(0.033))
    r = said()
    K.check(len(r) == 1 and r[0].startswith("P1 done: 15 chain starts (4 Ability2/3, 11 other; 6 lines in the log only)") and s.mode == 0,
            "X. p1 window end -> summary + rest: %s" % r)
    K.check("Expect: each rune key" in r[0] and "PASS" not in r[0] and "FAIL" not in r[0], "X. FIX4 the p1 summary carries no PASS / FAIL word: %s" % r)
    # p1 cancel: cancelled + the 1 s check (PASS, then FAIL with Mana spent + a running server cooldown)
    r = run("p1", "cancel")
    s = Cmds.STATES.get(u)
    K.check(s.cancel and "CANCELLED" in r[0], "X. p1 cancel armed: %s" % r)
    e5 = event(IT.Ability2, "Root_Rune_Chain_Fireball", IS("Rune_Fireball", 1), -11, 0)     # chain root != the rune's Cast root
    Cmds.onChain(e5, ref, acc)
    r = said()
    K.check(e5.isCancelled() and r[0].endswith("-> CANCELLED") and s.cancelled == 1 and s.p1CheckAt > 0 and str(s.p1Root) == "Root_Ability_Fireball"
            and abs(s.p1Mana - 40.0) < 1e-6, "X. p1 cancel: the REAL event reads back cancelled + check armed: %s" % r)
    K.check(str(Cmds.cdId(IS("Rune_Fireball", 1), "Root_Rune_Chain_Fireball")) == "Root_Ability_Fireball"
            and str(Cmds.cdId(IS("Food_Bread", 1), "Root_Food")) == "Root_Food" and str(Cmds.cdId(None, None)) == "",
            "X. FIX5 the cancel check reads the cooldown under the held rune's Cast root id (chain root only for a non-rune)")
    e6 = event(IT.Primary, "Root_Swing", None, 0, 0)
    Cmds.onChain(e6, ref, acc)
    K.check(not e6.isCancelled(), "X. p1 cancel never cancels a non-rune chain")
    said()
    s.p1CheckAt = 1
    Cmds.tickPlayer(ref, acc, acc, JFloat(0.033))
    r = said()
    K.check(len(r) == 1 and r[0].startswith("P1 cancel check (Root_Ability_Fireball): PASS") and s.p1CheckAt == 0, "X. cancel check PASS: %s" % r)
    Cmds.onChain(event(IT.Ability3, "Root_Ability_Fireball", IS("Rune_Fireball", 1), -11, 3), ref, acc)
    said()
    setf(mana, "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue", "value", JFloat(10.0))
    handler.getCooldown("Root_Ability_Fireball", JFloat(2.0), IMGR.DEFAULT_CHARGE_TIMES, True, False).resetCooldown()
    s.p1CheckAt = 1
    Cmds.tickPlayer(ref, acc, acc, JFloat(0.033))
    r = said()
    K.check(len(r) == 1 and "FAIL: Mana went DOWN" in r[0] and "server cooldown is running (2.0 s left)" in r[0], "X. cancel check FAIL: %s" % r)
    setf(mana, "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue", "value", JFloat(40.0))
    # the check with Mana unreadable
    vals[MI] = None
    s.p1CheckAt = 1
    Cmds.tickPlayer(ref, acc, acc, JFloat(0.033))
    K.check(said() == ["P1 cancel check: your Mana is unreadable."], "X. cancel check: Mana unreadable")
    vals[MI] = mana
    # FIX1 (critic 3): p3 ends a running p1 CANCEL first, so the U6 rune press right after p3 set is not cancelled
    r = run("p3", "set", "Root_Ability_Fireball", "8")
    K.check(len(r) == 2 and r[0].startswith("P1 cancel ended early (p3 needs your rune key uncancelled)") and r[1].startswith("P3 set: Root_Ability_Fireball")
            and Cmds.STATES.get(u).mode == 0, "X. FIX1c3 p3 set ends a running p1 cancel: %s" % r)
    e7 = event(IT.Ability2, "Root_Rune_Chain_Fireball", IS("Rune_Fireball", 1), -11, 0)
    Cmds.onChain(e7, ref, acc)
    K.check(not e7.isCancelled() and said() == [], "X. FIX1c3 after p3 the rune key press is NOT cancelled")
    handler.getCooldown("Root_Ability_Fireball").setCooldownMax(JFloat(0.0))
    run("p1")
    r = run("p3", "clear", "Root_Ability_Fireball")
    K.check(len(r) == 1 and r[0].startswith("P3 clear") and Cmds.STATES.get(u).mode == 1, "X. FIX1c3 p3 leaves a plain (non-cancel) p1 running: %s" % r)
    run("p1", "cancel")
    # a new probe ends the running one (summary) and drops the cancel flag
    r = run("p4", "watch")
    s = Cmds.STATES.get(u)
    K.check(len(r) == 2 and r[0].startswith("P1 ended early (a new probe was armed)") and "cancelled" in r[0] and r[1].startswith("P4 armed")
            and s.mode == 4 and not s.cancel and s.p1CheckAt == 0, "X. arming p4 watch ends p1 cancel: %s" % r)
    # p4 watch: REAL InventoryChangeEvents through AbInvSys.handle-equivalent
    ICE = JClass("com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent")
    invSys = JClass(PKG + "AbInvSys")()
    abs_.getInventory().addItemStackToSlot(JShort(0), IS("Rune_Fireball", 1))
    Cmds.onInv(ICE(types["abs"], abs_, abs_.getInventory(), None), ref, acc)
    Cmds.onInv(ICE(types["rnb"], bag, bag.getInventory(), None), ref, acc)
    Cmds.onInv(ICE(types["pla"], hb, hb.getInventory(), None), ref, acc)
    r = said()
    s = Cmds.STATES.get(u)
    K.check(len(r) == 2 and "on the AbilitySlots (-11); slots now (6 slots) 0 Rune_Fireball" in r[0] and "RuneBag (-12)" in r[1]
            and s.invSlots == 1 and s.invBag == 1 and s.invOther == 1, "X. p4 watch lines: %s" % r)
    Cmds.summary(s, None, None)
    r = said()
    K.check(len(r) == 1 and "Expect: your drag" in r[0] and "PASS" not in r[0], "X. FIX4 the p4 watch summary carries no PASS word: %s" % r)
    invSys.handle(JInt(0), None, None, None, None)
    invSys.handle(JInt(0), chunk, None, None, e1)
    invSys.handle(JInt(0), chunk, None, None, ICE(types["abs"], abs_, abs_.getInventory(), None))
    K.check(said() == [], "X. AbInvSys.handle: null chunk / wrong event / no buffer ignored")
    abs_.getInventory().removeItemStackFromSlot(JShort(0))
    r = run("stop")
    K.check(len(r) == 2 and r[0].startswith("P4 stopped: 1 InventoryChangeEvents on the AbilitySlots") and r[1] == "Probe state cleared."
            and Cmds.STATES.get(u) is None, "X. stop: summary + cleared: %s" % r)
    K.check(run("stop") == ["Probe state cleared."], "X. stop with nothing running")
    # p4 watch refused without AbilitySlots
    acc.put(ref, types["abs"], None)
    r = run("p4", "watch")
    K.check(r == ["P4 watch: no AbilitySlots on you."] and Cmds.STATES.get(u).mode == 0, "X. p4 watch refused: %s" % r)
    K.check(run("p4") == ["P4: no AbilitySlots on you."], "X. p4 read without AbilitySlots")
    acc.put(ref, types["abs"], abs_)
    # ---------------- p4 read / put / take / bad
    r = run("p4")
    K.check(len(r) == 1 and "(6 slots) 0 -, 1 -" in r[0], "X. p4 read (empty): %s" % r)
    K.check("Usage" in run("p4", "put", "9")[0] and "Usage" in run("p4", "zz", "1")[0] and "Usage" in run("p4", "put")[0],
            "X. p4 slot range / usage")
    K.check("Usage: /aprobe p4 put <slot> <itemId>" in run("p4", "put", "0")[0], "X. p4 put without an id")
    K.check("no item 'Rune_Nope'" in run("p4", "put", "0", "Rune_Nope")[0], "X. p4 put unknown id")
    r = run("p4", "put", "0", "Weapon_Staff_Wood")
    K.check(len(r) == 1 and "is not a rune" in r[0] and Cmds.stackAt(abs_.getInventory(), 0) is None and Cmds.PUT.isEmpty(),
            "X. FIX2 p4 put refuses a non-rune id: %s" % r)
    r = run("p4", "put", "0", "Rune_Fireball")
    ent = Cmds.PUT.get(str(u) + " 0")
    SYS = JClass("java.lang.System")
    K.check(len(r) == 2 and "P4 put Rune_Fireball -> slot 0" in r[0] and "succeeded=" in r[0] and "slot now Rune_Fireball" in r[0]
            and ent is not None and str(ent[0]) == "Rune_Fireball"
            and SYS.identityHashCode(ent[1]) == SYS.identityHashCode(Cmds.stackAt(abs_.getInventory(), 0)),
            "X. p4 put ok (the exact ItemStack copy in the slot is tracked): %s" % r)
    K.check(len(r) == 2 and "REAL rune" in r[1] and "/aprobe stop" in r[1], "X. FIX2 p4 put warns it is a real saved rune: %s" % r[1:])
    # FIX1 (critic 1): the player drags the probe's rune out and drags THEIR OWN same-id rune in -> take must refuse it
    abs_.getInventory().removeItemStackFromSlot(JShort(0))
    abs_.getInventory().addItemStackToSlot(JShort(0), IS("Rune_Fireball", 1))
    r = run("p4", "take", "0")
    K.check(len(r) == 1 and "not the exact copy the probe put there" in r[0] and Cmds.stackAt(abs_.getInventory(), 0) is not None,
            "X. FIX1 p4 take refuses the player's own same-id rune in a slot the probe once filled: %s" % r)
    abs_.getInventory().removeItemStackFromSlot(JShort(0))
    r = run("p4", "put", "0", "Rune_Fireball")
    K.check(r[0].startswith("P4 put Rune_Fireball -> slot 0"), "X. p4 put again after the swap: %s" % r[:1])
    K.check("is not empty" in run("p4", "put", "0", "Rune_Fireball")[0], "X. p4 put into a full slot refused")
    abs_.getInventory().addItemStackToSlot(JShort(1), IS("Rune_Damage_Up", 1))
    r = run("p4", "read")
    K.check(len(r) == 3 and "slot 0 Rune_Fireball: Core rune" in r[1] and "canUseWith YES" in r[1]
            and "slot 1 Rune_Damage_Up: Support rune: requires any Damage, all -, excludes Poison" in r[2], "X. p4 read with runes: %s" % r)
    r = run("p4", "take", "1")
    K.check("not the exact copy the probe put there" in r[0] and "it stays" in r[0] and Cmds.stackAt(abs_.getInventory(), 1) is not None, "X. p4 take refuses a rune it did not put: %s" % r)
    r = run("p4", "take", "0")
    K.check("probe-made" in r[0] and Cmds.stackAt(abs_.getInventory(), 0) is None and Cmds.PUT.isEmpty(), "X. p4 take its own rune: %s" % r)
    K.check(run("p4", "take", "0") == ["P4 take: slot 0 is empty."], "X. p4 take an empty slot")
    # FIX2: /aprobe stop takes back the probe's exact copies, leaves a swapped-in same-id rune alone
    run("p4", "put", "0", "Rune_Fireball")
    r = run("stop")
    K.check(r == ["P4 stop: took back 1 probe-made rune(s).", "Probe state cleared."] and Cmds.stackAt(abs_.getInventory(), 0) is None
            and Cmds.PUT.isEmpty(), "X. FIX2 stop takes back the probe-made rune: %s" % r)
    run("p4", "put", "0", "Rune_Fireball")
    abs_.getInventory().removeItemStackFromSlot(JShort(0))
    abs_.getInventory().addItemStackToSlot(JShort(0), IS("Rune_Fireball", 1))
    r = run("stop")
    K.check(len(r) == 2 and r[0].startswith("P4 stop: took back 0 probe-made rune(s); NOT provably the probe's copy, left in place")
            and "slot 0 Rune_Fireball" in r[0] and Cmds.stackAt(abs_.getInventory(), 0) is not None and Cmds.PUT.isEmpty(),
            "X. FIX2 stop never removes a same-id rune that is not the probe's copy: %s" % r)
    abs_.getInventory().removeItemStackFromSlot(JShort(0))
    K.check(run("stop") == ["Probe state cleared."], "X. FIX2 stop with nothing tracked adds no line")
    abs_.getInventory().removeItemStackFromSlot(JShort(1))
    # bad: hand states
    hb.getInventory().removeItemStackFromSlot(JShort(0))
    K.check("hold any NON-rune" in run("p4", "bad", "2")[0], "X. p4 bad with an empty hand")
    hb.getInventory().addItemStackToSlot(JShort(0), IS("Rune_Fireball", 1))
    hand_now = Cmds.hand(acc, ref)
    if hand_now is not None:
        K.check("you hold a rune" in run("p4", "bad", "2")[0], "X. p4 bad with a rune in hand")
    hb.getInventory().removeItemStackFromSlot(JShort(0))
    hb.getInventory().addItemStackToSlot(JShort(0), IS("Weapon_Staff_Wood", 1))
    abs_.getInventory().addItemStackToSlot(JShort(0), IS("Rune_Fireball", 1))
    r = run("p4", "bad", "0")
    K.check("is not empty - pick an empty slot" in r[0], "X. p4 bad into a full slot: %s" % r)
    abs_.getInventory().removeItemStackFromSlot(JShort(0))
    # the REAL engine filters (AbilitySlots.afterDecode -> ItemContainerUtil.trySetAbilityFilters) refuse a non-rune -> PASS
    try:
        m_ = ABS.class_.getDeclaredMethod("afterDecode")
        m_.setAccessible(True)
        m_.invoke(abs_)
    except Exception as e:
        K.notes.append("afterDecode: %s" % e)
    r = run("p4", "bad", "0")
    K.check(len(r) == 1 and r[0].startswith("P4 bad: PASS - slot 0 refused Weapon_Staff_Wood") and Cmds.stackAt(abs_.getInventory(), 0) is None,
            "X. p4 bad: the engine's own slot filter refuses a code write = PASS: %s" % r)
    # a filterless container accepts -> FAIL branch + removed again
    abs2 = alloc("com.hypixel.hytale.server.core.inventory.InventoryComponent$AbilitySlots")
    setf(abs2, "com.hypixel.hytale.server.core.inventory.InventoryComponent", "inventory",
         JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")(JShort(6)))
    acc.put(ref, types["abs"], abs2)
    r = run("p4", "bad", "0")
    K.check(len(r) == 1 and r[0].startswith("P4 bad: FAIL - a non-rune (Weapon_Staff_Wood) went into slot 0") and "Removed again: yes" in r[0]
            and Cmds.stackAt(abs2.getInventory(), 0) is None, "X. p4 bad: a filterless container = FAIL + removed: %s" % r)
    acc.put(ref, types["abs"], abs_)
    # a throwing container -> the catch line
    abs3 = alloc("com.hypixel.hytale.server.core.inventory.InventoryComponent$AbilitySlots")
    sic = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")(JShort(6))
    setf(abs3, "com.hypixel.hytale.server.core.inventory.InventoryComponent", "inventory", sic)
    acc.put(ref, types["abs"], abs3)
    KMap.CUSTOM.remove("Weapon_Staff_Wood")
    KMap.CUSTOM.put("Weapon_Staff_Wood", None)
    r = run("p4", "put", "4", "Weapon_Staff_Wood")
    K.check(len(r) == 1 and "no item" in r[0], "X. p4 put: an id whose asset vanished: %s" % r)
    item("Weapon_Staff_Wood", None, True)
    acc.put(ref, types["abs"], abs_)
    # ---------------- p3
    acc.put(ref, types["im"], None)
    r = run("p3")
    K.check(len(r) == 1 and r[0].startswith("P3: FAIL - no CooldownHandler"), "X. p3 without an InteractionManager: %s" % r)
    acc.put(ref, types["im"], im)
    handler2 = CDH()
    setf(im, "com.hypixel.hytale.server.core.entity.InteractionManager", "cooldownHandler", handler2)
    r = run("p3")
    K.check(r == ["P3: your server CooldownHandler holds 0 cooldown(s) - cast a vanilla rune, then /aprobe p3 again."], "X. p3 list empty: %s" % r)
    r = run("p3", "set", "Root_Ability_Fireball", "8")
    K.check(len(r) == 1 and r[0].startswith("P3 set: Root_Ability_Fireball: max 8.0 s, 8.0 s left") and abs(Cmds.cdLeft(handler2, "Root_Ability_Fireball") - 8.0) < 1e-6,
            "X. p3 set arms the REAL CooldownHandler: %s" % r)
    for i in range(14):
        handler2.getCooldown("Root_X%d" % i, JFloat(1.0), IMGR.DEFAULT_CHARGE_TIMES, True, False)
    r = run("p3", "list")
    K.check(len(r) == 13 and "holds 15 cooldown(s):" in r[0] and all(x.startswith("P3 Root_") for x in r[1:]),
            "X. p3 list: 12 rows in chat, the rest in the log (%d lines)" % len(r))
    r = run("p3", "clear", "Root_Ability_Fireball")
    K.check(len(r) == 1 and "ready" in r[0] and Cmds.cdLeft(handler2, "Root_Ability_Fireball") == 0.0, "X. p3 clear: %s" % r)
    K.check(run("p3", "clear", "Root_None") == ["P3 clear: Root_None has no cooldown."], "X. p3 clear an unknown id")
    K.check("Usage" in run("p3", "set")[0] and "Usage" in run("p3", "zz", "x")[0], "X. p3 usage")
    setf(handler2, "com.hypixel.hytale.server.core.modules.interaction.interaction.CooldownHandler", "cooldowns", None)
    K.check(run("p3") == ["P3: the handler's cooldown map is unreadable."], "X. p3 with an unreadable map")
    r = run("p3", "set", "Root_Y", "4")
    K.check(len(r) == 1 and r[0].startswith("P3 set failed:"), "X. p3 set: an engine error is caught: %s" % r)
    setf(handler2, "com.hypixel.hytale.server.core.modules.interaction.interaction.CooldownHandler", "cooldowns", JClass("java.util.HashMap")())
    K.check(Cmds.cdLeft(None, "x") == 0.0 and Cmds.cdLeft(handler2, "") == 0.0 and Cmds.left(None) == -1.0 and "no cooldown" in str(Cmds.cdLine("x", None)),
            "X. cooldown helpers on missing data")
    # ---------------- p14 / p15
    r = run("p14")
    K.check(len(r) == 2 and r[0].startswith("P14 profile (no SkyyProfiles key): ability slots -11 (6 slots) all empty; rune bag -12 (10 slots) all empty"),
            "X. p14 without a profile key: %s" % r)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    br.put("profile:key:" + str(u), str(u) + "#2")
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    bag.getInventory().addItemStackToSlot(JShort(3), IS("Rune_Damage_Up", 1))
    r = run("p14")
    K.check(r[0].startswith("P14 profile %s#2:" % u) and "3 Rune_Damage_Up" in r[0], "X. p14 with a key + a rune in the bag: %s" % r)
    JClass("java.lang.System").getProperties().remove("skyy.bridge")
    r = run("p15")
    K.check(len(r) == 1 and r[0].startswith("P15: your Mana 40.0 / 55.0; the Mana stat type's own max (Mana.json) -1.0"), "X. p15: %s" % r)
    acc.put(ref, types["esm"], None)
    K.check(run("p15")[0].startswith("P15: your Mana is unreadable"), "X. p15 unreadable")
    acc.put(ref, types["esm"], esm)
    # ---------------- p13 (the sphere query on a stand-in accessor fails -> the warn path, 0 entities), stats, budget summary
    r = run("p13", "500", "3")
    s = Cmds.STATES.get(u)
    K.check(r[0].startswith("P13 armed for 3 s: 256 zones") and s.zones == 256, "X. p13 armed (zone cap 256): %s" % r)
    for i in range(3):
        Cmds.tickPlayer(ref, acc, acc, JFloat(0.05))
    K.check(s.p13Ticks == 3 and s.p13Scans > 0 and s.ticks == 3, "X. p13 ticks scan (%d ticks, %d scans)" % (s.p13Ticks, s.p13Scans))
    r = run("stats")
    K.check(r[0].startswith("Stats: running P13, 3 ticks"), "X. stats while running: %s" % r)
    s.modeUntil = 1
    Cmds.tickPlayer(ref, acc, acc, JFloat(0.05))
    r = said()
    K.check(len(r) == 1 and r[0].startswith("P13 done: 256 zones x 4.0 Hz") and ("PASS" in r[0] or "OVER" in r[0]), "X. p13 summary: %s" % r)
    acc.put(ref, types["tc"], None)
    run("p13")
    Cmds.tickPlayer(ref, acc, acc, JFloat(0.05))
    K.check(Cmds.STATES.get(u).p13Ticks == 0, "X. p13 without a position does not scan")
    acc.put(ref, types["tc"], tcc)
    # a world change ends a probe
    other_store = JClass("java.lang.Object")()
    Cmds.tickPlayer(ref, other_store, acc, JFloat(0.05))
    r = said()
    K.check(len(r) == 1 and r[0].startswith("P13 ended: you changed world") and Cmds.STATES.get(u) is None, "X. world change ends + drops the state: %s" % r)
    # tick early returns + the AbTick wrapper
    Cmds.tickPlayer(None, acc, acc, JFloat(0.05))
    Cmds.tickPlayer(Ref(None, 0), acc, acc, JFloat(0.05))
    tick = JClass(PKG + "AbTick")()
    K.check(not tick.isParallel(1, 1) and tick.getQuery() is not None, "X. AbTick: not parallel, query = Player")
    run("p13")
    tick.tick(JFloat(0.05), JInt(0), None, None, None)
    JClass(PKG + "AbTick").FAILED_ONCE = False
    tick.tick(JFloat(0.05), JInt(5), chunk, None, None)      # index out of bounds -> caught, logged once
    K.check(JClass(PKG + "AbTick").FAILED_ONCE, "X. AbTick: an engine error is caught and logged once")
    tick.tick(JFloat(0.05), JInt(0), chunk, None, None)      # buffer null -> prOf(null) -> nothing
    run("stop")
    said()
    # ---------------- the command classes' execute() + a REAL CommandContext
    CTXc = JClass("com.hypixel.hytale.server.core.command.system.CommandContext")
    root = JClass(PKG + "AProbeCmd")()
    ex = root.getClass().getDeclaredMethod("execute", CTXc.class_, Cls.forName("com.hypixel.hytale.component.Store"), Ref.class_, PR.class_,
                                          Cls.forName("com.hypixel.hytale.server.core.universe.world.World"))
    ex.setAccessible(True)
    ex.invoke(root, None, None, ref, pr, None)
    K.check(len(said()) == 3, "X. AProbeCmd.execute = help")
    for n_, words in ((1, ["p15"]), (2, ["p4", "read"]), (3, ["p3", "clear", "Root_None"]), (4, ["p3", "set", "Root_Z", "5"])):
        v = JClass(PKG + "AProbeArg%dCmd" % n_)()
        ctx = CTXc(v, None, "aprobe " + " ".join(words))
        av = ctx.getClass().getDeclaredField("argValues")
        av.setAccessible(True)
        mp = av.get(ctx)
        for i in range(n_):
            a_ = v.getClass().getField("a%d" % i).get(v)
            mp.put(a_, words[i])
        # Store parameter: the variant passes store straight to AbCmds.run as the accessor -> run with a Store-typed null is impossible,
        # so call through AbCmds.run with our accessor and check the variant's own word reading on the REAL CommandContext separately
        got = [str(ctx.get(v.getClass().getField("a%d" % i).get(v))) for i in range(n_)]
        K.check(got == words, "X. AProbeArg%dCmd: the REAL CommandContext gives back the words %s" % (n_, got))
        exv = v.getClass().getDeclaredMethod("execute", CTXc.class_, Cls.forName("com.hypixel.hytale.component.Store"), Ref.class_, PR.class_,
                                             Cls.forName("com.hypixel.hytale.server.core.universe.world.World"))
        exv.setAccessible(True)
        exv.invoke(v, ctx, None, ref, pr, None)
        out_ = said()
        K.check(len(out_) >= 1, "X. AProbeArg%dCmd.execute runs /aprobe %s (store null -> the no-component branch): %s" % (n_, " ".join(words), out_[:1]))
        exv.invoke(v, None, None, ref, pr, None)
        K.check(said() == ["Usage: /aprobe <probe> [values]"], "X. AProbeArg%dCmd.execute without a context = usage line" % n_)
    # the plugin's shutdown clears every map
    Cmds.PUT.put("x", "y")
    st0 = St(u, ref, acc)
    Cmds.STATES.put(u, st0)
    plug = U.allocateInstance(Cls.forName(PKG + "SkyyAbilityProbePlugin"))
    sd = plug.getClass().getDeclaredMethod("shutdown")
    sd.setAccessible(True)
    try:
        sd.invoke(plug)
    except Exception as e:
        K.notes.append("plugin shutdown super call on an allocated plugin: %s" % str(e)[:120])
    K.check(Cmds.STATES.isEmpty() and Cmds.PUT.isEmpty(), "X. plugin shutdown clears STATES + PUT")
    # tell() with a PlayerRef that cannot send (no packet handler) still logs + sinks
    Log.tell(pr, "hello")
    Log.tell(None, "hello2")
    K.check(said() == ["hello", "hello2"], "X. AbLog.tell survives a PlayerRef without a connection")
    Log.LOG = None
    Log.info("x")
    Log.warn("y")

    # ---------------- R (the state-reset rule)
    fields = [fl for fl in St.class_.getDeclaredFields() if str(fl.getName()) not in KEEP]

    def dirty(s_):
        for fl in fields:
            t = str(fl.getType().getName())
            if t == "int":
                fl.setInt(s_, 7)
            elif t == "long":
                fl.setLong(s_, 7)
            elif t == "double":
                fl.setDouble(s_, 7.5)
            elif t == "boolean":
                fl.setBoolean(s_, True)
            elif t == "java.lang.String":
                fl.set(s_, "x")
            else:
                K.check(False, "R. unhandled AbState field type %s %s - extend the harness" % (t, fl.getName()))

    def not_rest(s_):
        bad = []
        for fl in fields:
            n_, t, v = str(fl.getName()), str(fl.getType().getName()), fl.get(s_)
            if t in ("int", "long", "double"):
                ok = float(v) == 0.0
            elif t == "boolean":
                ok = not bool(v)
            else:
                ok = str(v) == ""
            if not ok:
                bad.append("%s=%s" % (n_, v))
        return bad
    s = St(UUID.randomUUID(), None, None)
    K.check(not not_rest(s), "R. a fresh state is at rest: %s" % not_rest(s))
    dirty(s)
    Cmds.clear(s)
    K.check(not not_rest(s), "R. clear() resets EVERY probe field: %s" % not_rest(s))
    K.check(Cmds.plan(s, W("p1", "cancel"), 1000) is None and s.mode == 1 and s.cancel and s.modeUntil == 61000, "R. p1 cancel armed")
    dirty(s)
    K.check(Cmds.plan(s, W("p4", "watch"), 2000) is None and s.mode == 4 and not s.cancel and s.p1CheckAt == 0 and str(s.p1Root) == ""
            and s.modeUntil == 62000, "R. arming p4 watch drops p1's cancel flag + pending check")
    dirty(s)
    K.check(Cmds.plan(s, W("p13", "x", "999"), 0) is None and s.zones == 48 and s.modeUntil == 60000 and s.invSlots == 0, "R. p13 defaults / caps")
    dirty(s)
    K.check(Cmds.plan(s, W("p4", "read"), 0) is not None and s.mode == 0 and not not_rest(s), "R. a refused plan leaves the state at rest")
    K.check(Cmds.plan(s, None, 0) is not None and not not_rest(s), "R. an empty plan is refused at rest")
    for m in (1, 4, 13):
        dirty(s)
        s.mode, s.armedAt = m, 1
        Cmds.summary(s, None, None)
        K.check(len(said()) == 1, "R. summary P%d = 1 line" % m)
    s.mode = 7
    Cmds.summary(s, None, None)
    K.check(said() == [], "R. summary of an unknown mode says nothing")
    dirty(s)
    s.mode = 1
    Cmds.finish(s, None, "x")
    K.check(s.mode == 0 and not not_rest(s), "R. finish() clears the state")
    # active(): no window, no action
    pr2 = alloc("com.hypixel.hytale.server.core.universe.PlayerRef")
    u2 = UUID.randomUUID()
    setf(pr2, "com.hypixel.hytale.server.core.universe.PlayerRef", "uuid", u2)
    s2 = St(u2, None, None)
    Cmds.STATES.put(u2, s2)
    s2.mode, s2.modeUntil = 1, 5000
    K.check(Cmds.active(pr2, 1, 4999) is not None and Cmds.active(pr2, 1, 5000) is None and Cmds.active(pr2, 4, 0) is None
            and Cmds.active(pr2, -1, 0) is not None and Cmds.active(None, 1, 0) is None, "R. active(): window + mode")
    Cmds.STATES.clear()

    # ---------------- P (permissions with the engine's own AbstractCommand code)
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fld = AC.class_.getDeclaredField("permissionGroups")
    fld.setAccessible(True)
    for cn in CMDS:
        c = JClass(PKG + cn)()
        perm = c.getPermission()
        groups = fld.get(c)
        K.check(perm is not None and NODE in str(perm), "P. %s requires %s (%s)" % (cn, NODE, perm))
        K.check(groups is not None and len(groups) == 0, "P. %s permission groups empty (%s)" % (cn, groups))
        if cn == "AProbeCmd":
            rec = c.getPermissionGroupsRecursive()
            leak = [str(k) for k in rec.keySet() if rec.get(k) is not None and any(NODE in str(x) for x in rec.get(k))]
            K.check(not leak, "P. getPermissionGroupsRecursive gives %s to no group (leak: %s)" % (NODE, leak))
            als = [str(a) for a in c.getAliases()]
            K.check(str(c.getName()) == "aprobe" and als == ["abilityprobe"] and "abilities" not in als, "P. /aprobe + alias /abilityprobe: %s" % als)
    # ---------------- B (setup()'s calls, bytecode)
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    CP.appendClassPath(JAR)
    cc = CP.get(PKG + "SkyyAbilityProbePlugin")
    mi = [m for m in cc.getClassFile2().getMethods() if str(m.getName()) == "setup"][0]
    cpool, it = mi.getConstPool(), mi.getCodeAttribute().iterator()
    seq, strs = [], []
    CPool = JClass("javassist.bytecode.ConstPool")
    while it.hasNext():
        p = it.next()
        op = it.byteAt(p)
        if op in (0xb6, 0xb7, 0xb8, 0xb9):
            i = it.u16bitAt(p + 1)
            if cpool.getTag(i) == CPool.CONST_InterfaceMethodref:
                seq.append(str(cpool.getInterfaceMethodrefName(i)))
            else:
                seq.append(str(cpool.getMethodrefClassName(i)).rsplit(".", 1)[-1] + "." + str(cpool.getMethodrefName(i)))
        elif op == 0xbb:
            seq.append("new " + str(cpool.getClassInfo(it.u16bitAt(p + 1))).rsplit(".", 1)[-1])
        elif op in (0x12, 0x13):
            i = it.byteAt(p + 1) if op == 0x12 else it.u16bitAt(p + 1)
            if cpool.getTag(i) == CPool.CONST_String:
                strs.append(str(cpool.getStringInfo(i)))
    news = [x for x in seq if x.startswith("new Ab") or x.startswith("new AP")]
    K.check(news == ["new AProbeCmd", "new AbTick", "new AbInvSys", "new AbChainSys"], "B. setup builds the command + 3 systems in order: %s" % news)
    K.check(seq.count("EntityStoreRegistry.registerSystem") + seq.count("ComponentRegistryProxy.registerSystem") + sum(1 for x in seq if x.endswith("registerSystem")) >= 3,
            "B. setup registers 3 systems (one registerSystem per class): %s" % [x for x in seq if "register" in x])
    K.check(any(x.startswith("[SkyyAbilityProbe] 0.1 ready") for x in strs), "B. the ready line the smoke test needs: %s" % [x for x in strs if "ready" in x])
    K.save()


# ====================================================================================================== child D: live data
def run_live(step, out):
    from jpype import JClass, JArray, JString
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    home = os.path.join(SCRATCH, "live")

    def snap():
        d_ = {}
        for r_, _, fs in os.walk(home):
            for f_ in fs:
                p_ = os.path.join(r_, f_)
                d_[os.path.relpath(p_, home)] = hashlib.sha256(open(p_, "rb").read()).hexdigest()
        return d_
    before = snap()
    Cmds, St, Log, UUID = JClass(PKG + "AbCmds"), JClass(PKG + "AbState"), JClass(PKG + "AbLog"), JClass("java.util.UUID")
    K.check(Cmds.STATES.isEmpty() and Cmds.PUT.isEmpty() and not Cmds.CHAIN_ON, "D %s: the probe starts with no state" % step)
    SINK = JClass("java.util.ArrayList")()
    Log.SINK = SINK
    SA = JArray(JString)
    used = 0
    for f in sorted(before):
        if not f.endswith(".json"):
            continue
        try:
            json.load(open(os.path.join(home, f), encoding="utf-8"))
            u = UUID.fromString(os.path.basename(f)[:-5])
        except Exception:
            continue
        s = St(u, None, None)
        Cmds.STATES.put(u, s)
        for words in (["p1", "cancel"], ["p4", "watch"], ["p13", "12", "5"], ["zz"]):
            Cmds.plan(s, SA(words), 1000)
            Cmds.summary(s, None, "test")
        Cmds.clear(s)
        K.check(s.mode == 0 and Cmds.active(None, 1, 0) is None, "D %s %s: the probe paths run for this live player's uuid" % (step, f))
        used += 1
    Cmds.STATES.clear()
    after = snap()
    K.check(before == after, "D %s: the probe wrote NOTHING - every scratch file byte-identical, no new file (%d files)" % (step, len(after)))
    K.notes.append("D %s: %d live player copies used, %d lines" % (step, used, SINK.size()))
    K.save(files=len(after), used=used)


# ====================================================================================================== child AA: engine-access audit
def run_audit(out):
    from jpype import JClass
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR], verify=False)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    for p_ in (B.SERVER_JAR, JAR):
        CP.appendClassPath(p_)
    lk_cls = CP.makeClass("skyyabtest.LookupIn")
    lk_cls.addMethod(JClass("javassist.CtNewMethod").make(
        "public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
        "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}", lk_cls))
    LIN = JClass(lk_cls.toClass())
    ba = CP.makeClass("skyyabtest.BadAccess")
    ba.addMethod(JClass("javassist.CtNewMethod").make(
        "public static void send(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) {\n"
        "  p.sendUpdate(new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder());\n}", ba))
    BAD = ba.toBytecode()
    ba.defrost()
    JClass(ba.toClass())
    MTc, CPool, JMod_ = JClass("java.lang.invoke.MethodType"), JClass("javassist.bytecode.ConstPool"), JClass("java.lang.reflect.Modifier")
    XOPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
            0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
            0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}

    def jvm_class(name):
        return Cls.forName(name.replace("/", "."), False, loader)

    CSENS = set()

    def lookup_audit(cn):
        C_, name, mt = None, None, None
        D = jvm_class(cn)
        lk = LIN.lookupIn(D)
        cc = CP.get(cn)
        sup = str(cc.getSuperclass().getName()) if cc.getSuperclass() is not None else None
        refused, n = [], 0
        for mi in cc.getClassFile2().getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it_ = mi.getConstPool(), ca.iterator()
            in_ctor = str(mi.getName()) == "<init>"
            while it_.hasNext():
                p_ = it_.next()
                op = it_.byteAt(p_)
                if op not in XOPS:
                    continue
                where = "%s.%s @%d %s" % (cn.rsplit(".", 1)[-1], mi.getName(), p_, XOPS[op])
                if op == 0xba:
                    refused.append(where + ": invokedynamic")
                    continue
                idx = it_.byteAt(p_ + 1) if op == 0x12 else it_.u16bitAt(p_ + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != CPool.CONST_Class:
                    continue
                n += 1
                C_ = None
                try:
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        lk.accessClass(jvm_class(str(cp.getClassInfo(idx))))
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        C_ = jvm_class(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", loader).parameterType(0)
                        if op in (0xb2, 0xb3):
                            lk.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lk.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = (str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)),
                                                 str(cp.getInterfaceMethodrefType(idx)))
                        else:
                            cname, name, desc = (str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                        C_ = jvm_class(cname)
                        mt = MTc.fromMethodDescriptorString(desc, loader)
                        if name == "<init>" and in_ctor and cname in (sup, cn):
                            md = int(C_.getDeclaredConstructor(mt.parameterArray()).getModifiers())
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn):
                                raise ValueError("constructor %s %s%s is not accessible from %s" % (JMod_.toString(md), cname, desc, cn))
                        elif name == "<init>":
                            lk.findConstructor(C_, mt)
                        elif op == 0xb8:
                            lk.findStatic(C_, name, mt)
                        elif op == 0xb7:
                            lk.findSpecial(C_, name, mt, D)
                        else:
                            lk.findVirtual(C_, name, mt)
                except Exception as ex_:
                    ok_ = False
                    if "caller-sensitive" in str(ex_) and op in (0xb6, 0xb8, 0xb9):
                        try:      # a caller-sensitive JDK method (Class.forName, Field.get ...): public class + public method = callable
                            mm_ = C_.getMethod(name, mt.parameterArray())
                            ok_ = JMod_.isPublic(int(C_.getModifiers())) and JMod_.isPublic(int(mm_.getModifiers()))
                            if ok_:
                                CSENS.add("%s.%s" % (str(C_.getName()), name))
                        except Exception:
                            ok_ = False
                    if not ok_:
                        refused.append("%s: %s" % (where, str(ex_)[:160]))
        return refused, n
    names = [n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(JAR).namelist() if n_.endswith(".class")]
    res = {"classes": len(names), "refs": 0, "refused": [], "per": {}}
    for cn in names:
        try:
            r_, k_ = lookup_audit(cn)
        except Exception as ex_:
            r_, k_ = ["%s: could not audit: %s" % (cn, ex_)], 0
        res["refused"] += r_
        res["refs"] += k_
        res["per"][cn.rsplit(".", 1)[-1]] = k_
    res["control"] = lookup_audit("skyyabtest.BadAccess")[0]
    res["caller_sensitive"] = sorted(CSENS)
    json.dump(res, open(out, "w"), indent=1)


# ====================================================================================================== parent driver
def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--live", LIVE], env=env)


def take(path, label):
    if not os.path.isfile(path):
        check(False, "%s: the child wrote no result" % label)
        return None
    d = json.load(open(path))
    OKS[0] += d["ok"]
    for f in d["fails"]:
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, n))
    return d


def main():
    for flag, fn in (("--engine", lambda: run_engine(arg("--out"))), ("--live-step", lambda: run_live(arg("--live-step"), arg("--out"))),
                     ("--audit", lambda: run_audit(arg("--out")))):
        if flag in sys.argv:
            fn()
            return
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        part_static()
        out = os.path.join(SCRATCH, "engine.json")
        child(env, "--engine", "--out", out)
        take(out, "engine")
        home = os.path.join(SCRATCH, "live")
        os.makedirs(home, exist_ok=True)
        n = 0
        if os.path.isdir(LIVE):
            for f in sorted(os.listdir(LIVE)):
                if f.endswith(".json") and os.path.isfile(os.path.join(LIVE, f)):
                    shutil.copyfile(os.path.join(LIVE, f), os.path.join(home, f))      # read-only source; the copy is scratch
                    n += 1
        print("D. %d live player files copied (read-only source %s)" % (n, LIVE))
        check(n > 0, "D: live player files found to copy (%s)" % LIVE)
        used = []
        for step in ("start1", "start2"):
            out = os.path.join(SCRATCH, "live-%s.json" % step)
            child(env, "--live-step", step, "--out", out)
            r = take(out, "live " + step)
            used.append((r or {}).get("used", 0))
        check(used[0] > 0 and used[0] == used[1], "D: both starts used the same %s live player copies" % used)
        outa = os.path.join(SCRATCH, "audit.json")
        pa = child(env, "--audit", "--out", outa)
        check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            check(not a["refused"] and a["refs"] > 300 and a["classes"] == len(CLASSES),
                  "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: control refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, %d refused, control refused; caller-sensitive (public JDK reflection): %s"
                  % (a["refs"], a["classes"], len(a["refused"]), a.get("caller_sensitive")))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d ok, %d fail(s)" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAILED:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
