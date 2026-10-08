"""Harness for SkyyMonkProbe 0.1. Build first: python SkyyMonkProbe/build_skyymonkprobe_0.1.py

    python SkyyMonkProbe/test_skyymonkprobe_0.1.py [--jar <SkyyMonkProbe-0.1.jar>] [--live <a players folder>] [--keep]

Parent (plain Python, Assets.zip + the jar read-only):
  J  the jar: manifest (Main, IncludesAssetPack false, Version, Name), exactly the 11 expected classes, NO asset file at all (no item /
     block / lang / .ui: nothing overridden)
  K  the kit ids (Weapon_Staff_Bo_Wood / _Bamboo) are vanilla items in Assets.zip; the dagger dash VelocityConfig the NPC pushes copy has
     the six keys SkyyArmory asserts; the slowfx default 'Slow' is a vanilla entity effect with a HorizontalSpeedMultiplier
Children (fresh JVMs: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch):
  F  the stand-ins (MapStore / MapBuffer / MapChunk / FakeHotbar / FakeFx / FakeSpatial / LookupIn / BadAccess) generated with javassist
  A  every class loads and verifies (-Xverify:all)
  E  engine facts the probes lean on: PhysicsConstants.GRAVITY_ACCELERATION = 32; DamageSystems$FallDamagePlayers builds its FALL damage
     with Damage.NULL_SOURCE (the shape our re-dealt held fall copies) and runs BEFORE PlayerSystems$ProcessPlayerInput; no gravity /
     slow-fall field in the effect protocol (why M1 is a per-tick Set); DamageCause has PHYSICAL (the melee cause)
  L  MpLogic on plain data: launch / air-time / forward-speed numbers (python maths), the timed window edges, the bound cap, the analytic
     slow fall + the cap way, the cone, the combo decay + cap, verdict / f1 / number / dnum
  X  EVERY CODE PATH EXECUTED on engine stand-ins: real Velocity (the Set instructions read back), TransformComponent, HeadRotation +
     the real TargetUtil.getLook, the real TargetUtil.getAllEntitiesInSphere over FakeSpatial resources, the real
     DamageSystems.executeDamage into MapBuffer.invoke (every Damage read back: source, cause, amount), real EntityStatMaps with the
     vanilla stats loaded (Stamina / Mana costs), MovementStates edges, Player.getCurrentFallDistance, MovementManager settings, the real
     InventoryComponent.getCombined / getItemInHand, EntityEffect store with the vanilla Slow loaded; MpTick / MpFallSys / MpHitSys
     handle(); every probe (kit, m1 / m1cap incl. both time-outs, m2 log + chain: held fall forgiven / re-dealt as NULL_SOURCE FALL,
     early press, late-flag ground jump, hidden landing, chain end, cost refusal; m3 jump / crouch / jump-only; m4 0 / 85; m5 vault /
     lunge / rise + flight reports + the 6 s time-out; m6 sweep once per enemy; m7 cone hit + knock-up, hang holds, fling, crouch plunge
     (rising and in the hang), slam, plunge fall cancelled, M11 XP PASS / FAIL / no bridge, hang over -> flowing fall; m9; m12 aura +
     combo decay; m13; slowfx; xp / stats / stop / help / aliases); the three commands' execute() through reflection with a real
     CommandContext; a world change drops the state; broken systems log once; plugin shutdown clears the state; setup()'s calls in order;
     REVIEW FIXES: R1 a probe hit is capped at Health - 1 / skipped at <= 1 or no Health (the re-dealt fall is not capped); R3 stop with
     a held fall settles it (re-dealt or forgiven) before the state goes; R4 a relog (stale ref) drops the state; R5 the m4 time-out line
  P  /mprobe and both usage variants: node skyymonkprobe.admin, empty permission groups, getPermissionGroupsRecursive() gives the node
     to no group; alias /monkprobe
  D  START TWICE ON A SCRATCH COPY OF LIVE DATA: the live player files (Saves/<deploy world>/universe/players, read-only) are copied to
     scratch; two fresh child JVMs ("server starts") each decode every copy's EntityStats through the real EntityStatMap codec, run the
     probe's cost / stat text / kit paths on that real data, and the probe writes NOTHING: every scratch file byte-identical after each
     start, no new file, the probe state starts empty in the second start
  AA the ENGINE-ACCESS AUDIT: every class / field / method / constructor reference in the jar looked up with
     MethodHandles.privateLookupIn the referencing class (the JVM's own access rules) - 0 refused; the control refused
Not testable without the game (the build report lists them as UNVERIFIED): everything the probes MEASURE (client feel, stutter, NPC
motion vs per-tick Sets, the real timing of jump / landing packets, what the class lock / SkyyGear do with a PHYSICAL probe hit).
Scratch: tools/dev/scratch/monkprobe01/test (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, math, hashlib

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


JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyMonkProbe-%s.jar" % VERSION)))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "monkprobe01", "test")))
FAKE_DIR = os.path.join(SCRATCH, "fake")
FAKE_PKG = "skyymonktest"
PKG = "com.skyy.monkprobe."
CLASSES = sorted(PKG + c for c in ["MpLog", "MpLogic", "MpState", "MpCmds", "MpTick", "MpFallSys", "MpHitSys", "MProbeArg2Cmd",
                                   "MProbeArgCmd", "MProbeCmd", "SkyyMonkProbePlugin"])
NODE = "skyymonkprobe.admin"
BO = ["Weapon_Staff_Bo_Wood", "Weapon_Staff_Bo_Bamboo"]
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
FAILS, OKS = [], [0]
G = 32.0


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def near(a, b, eps=1e-6):
    return abs(float(a) - float(b)) <= eps


def deploy_world():
    try:
        for l in open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8"):
            if l.startswith("WORLD = "):
                return l.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    return "HUD mod"


LIVE = os.path.abspath(arg("--live", os.path.join(B.USERDATA, "Saves", deploy_world(), "universe", "players")))


# ====================================================================================================== parent: J K
def part_static():
    jz, az = zipfile.ZipFile(JAR), zipfile.ZipFile(ASSETS)
    man = json.loads(jz.read("manifest.json"))
    check(man["Main"] == PKG + "SkyyMonkProbePlugin" and man.get("IncludesAssetPack") is False and man["Version"] == VERSION
          and man["Name"] == "%s SkyyMonkProbe" % VERSION, "J. manifest %s" % man)
    cls = sorted(n[:-6].replace("/", ".") for n in jz.namelist() if n.endswith(".class"))
    check(cls == CLASSES, "J. classes %s" % cls)
    other = sorted(n for n in jz.namelist() if not n.endswith(".class") and n != "manifest.json")
    check(other == [], "J. no asset file at all (nothing overridden): %s" % other)
    names = set(az.namelist())
    items = set(n.rsplit("/", 1)[1][:-5] for n in names if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    for i in BO:
        check(i in items, "K. kit item %s is vanilla" % i)
    dash = [n for n in names if n.startswith("Server/") and n.endswith("/Daggers_Dash_Backward.json")]
    check(len(dash) == 1, "K. Daggers_Dash_Backward.json found once: %s" % dash)
    if dash:
        vc = json.loads(az.read(dash[0]).decode("utf-8-sig"))["Interactions"][0].get("VelocityConfig", {})
        check(sorted(vc) == sorted(["AirResistance", "AirResistanceMax", "GroundResistance", "GroundResistanceMax", "Threshold", "Style"]),
              "K. dash VelocityConfig keys %s" % sorted(vc))
    slow = [n for n in names if n.startswith("Server/Entity/Effects/") and n.endswith("/Slow.json")]
    check(len(slow) == 1 and "HorizontalSpeedMultiplier" in json.loads(az.read(slow[0]).decode("utf-8-sig")).get("ApplicationEffects", {}),
          "K. the slowfx default 'Slow' is one vanilla entity effect with a HorizontalSpeedMultiplier: %s" % slow)
    print("J/K. jar: %d classes, no assets; kit + dash + Slow are vanilla" % len(cls))


# ====================================================================================================== children
def _jvm(cp, verify=True):
    import jpype
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    opts = (["-Xverify:all"] if verify else []) + ["-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp]
    jpype.startJVM(jvm, *opts, classpath=list(cp), convertStrings=True)


ACC_BODY = """public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  if (this.comps == null || r == null) return null;
  java.util.Map m = (java.util.Map) this.comps.get(r);
  return m == null ? null : (com.hypixel.hytale.component.Component) m.get(t);
}"""
RES_BODY = """public com.hypixel.hytale.component.Resource getResource(com.hypixel.hytale.component.ResourceType t) {
  return this.res == null ? null : (com.hypixel.hytale.component.Resource) this.res.get(t);
}"""
PUT_BODY = """public void putComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t, com.hypixel.hytale.component.Component c) {
  java.util.Map m = (java.util.Map) this.comps.get(r);
  if (m == null) { m = new java.util.IdentityHashMap(); this.comps.put(r, m); }
  m.put(t, c);
}"""
INV_BODY = """public void invoke(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.system.EcsEvent e) {
  if (this.events != null) { this.events.add(r); this.events.add(e); }
}"""


def run_mkfake(out_dir):
    """child F: the stand-ins as .class files: subclasses of engine classes, always created with Unsafe.allocateInstance (no constructor
    runs) - the SkyyReelProbe / SkyyClasses harness pattern."""
    from jpype import JClass
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    P = FAKE_PKG
    # MapStore: a Store answering components / resources from maps, recording invoke(ref, event)
    ms = cp.makeClass(P + ".MapStore")
    ms.setSuperclass(cp.get("com.hypixel.hytale.component.Store"))
    for decl in ("java.util.Map comps", "java.util.Map res", "java.util.List events", "java.lang.Object ext", "com.hypixel.hytale.component.Archetype arch"):
        ms.addField(CtField.make("public %s;" % decl, ms))
    ms.addConstructor(CtNewConstructor.make("public MapStore() { super(null, 0, null, null); }", ms))   # never run (Unsafe)
    for body in (ACC_BODY, RES_BODY, INV_BODY, PUT_BODY):
        ms.addMethod(CtNewMethod.make(body, ms))
    ms.addMethod(CtNewMethod.make("public boolean isProcessing() { return false; }", ms))
    ms.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Archetype getArchetype(com.hypixel.hytale.component.Ref r) { return this.arch; }", ms))
    ms.addMethod(CtNewMethod.make("public java.lang.Object getExternalData() { return this.ext; }", ms))
    ms.writeFile(out_dir)
    # MapBuffer: the same for a CommandBuffer (what the systems get)
    mb = cp.makeClass(P + ".MapBuffer")
    mb.setSuperclass(cp.get("com.hypixel.hytale.component.CommandBuffer"))
    for decl in ("java.util.Map comps", "java.util.Map res", "java.util.List events", "java.lang.Object ext"):
        mb.addField(CtField.make("public %s;" % decl, mb))
    mb.addConstructor(CtNewConstructor.make("public MapBuffer() { super(null); }", mb))   # never run (Unsafe)
    for body in (ACC_BODY, RES_BODY, INV_BODY, PUT_BODY):
        mb.addMethod(CtNewMethod.make(body, mb))
    mb.addMethod(CtNewMethod.make("public java.lang.Object getExternalData() { return this.ext; }", mb))
    mb.writeFile(out_dir)
    mc = cp.makeClass(P + ".MapChunk")
    mc.setSuperclass(cp.get("com.hypixel.hytale.component.ArchetypeChunk"))
    mc.addField(CtField.make("public com.hypixel.hytale.component.Ref ref;", mc))
    mc.addField(CtField.make("public boolean boom;", mc))
    mc.addConstructor(CtNewConstructor.make("public MapChunk() { super(null, null); }", mc))   # never run (Unsafe)
    mc.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Ref getReferenceTo(int i) { if (this.boom) throw new IllegalStateException(\"boom\"); return this.ref; }", mc))
    mc.writeFile(out_dir)
    fh = cp.makeClass(P + ".FakeHotbar")
    fh.setSuperclass(cp.get("com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar"))
    fh.addField(CtField.make("public com.hypixel.hytale.server.core.inventory.ItemStack item;", fh))
    fh.addConstructor(CtNewConstructor.make("public FakeHotbar() { super(); }", fh))
    fh.addMethod(CtNewMethod.make("public com.hypixel.hytale.server.core.inventory.ItemStack getActiveItem() { return this.item; }", fh))
    fh.writeFile(out_dir)
    # FakeFx: an EffectControllerComponent recording addEffect(ref, effect, accessor)
    fx = cp.makeClass(P + ".FakeFx")
    fx.setSuperclass(cp.get("com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent"))
    fx.addField(CtField.make("public java.util.List got;", fx))
    fx.addField(CtField.make("public boolean boom;", fx))
    fx.addConstructor(CtNewConstructor.make("public FakeFx() { super(); }", fx))
    fx.addMethod(CtNewMethod.make("""public boolean addEffect(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect e, com.hypixel.hytale.component.ComponentAccessor a) {
  if (this.boom) throw new IllegalStateException("fx boom");
  if (this.got == null) this.got = new java.util.ArrayList();
  this.got.add(e);
  return true;
}""", fx))
    fx.writeFile(out_dir)
    # FakeSpatial: a SpatialStructure whose collect() answers every listed ref within the radius (positions read at call time)
    sp = cp.makeClass(P + ".FakeSpatial")
    sp.addInterface(cp.get("com.hypixel.hytale.component.spatial.SpatialStructure"))
    sp.addField(CtField.make("public java.util.List refs;", sp))
    sp.addField(CtField.make("public java.util.List pos;", sp))
    sp.addField(CtField.make("public int calls;", sp))
    sp.addConstructor(CtNewConstructor.make("public FakeSpatial() { super(); this.refs = new java.util.ArrayList(); this.pos = new java.util.ArrayList(); }", sp))
    sp.addMethod(CtNewMethod.make("""public void collect(org.joml.Vector3dc c, double r, java.util.List out) {
  this.calls = this.calls + 1;
  for (int i = 0; i < this.refs.size(); i++) {
    org.joml.Vector3d p = (org.joml.Vector3d) this.pos.get(i);
    double dx = p.x - c.x(); double dy = p.y - c.y(); double dz = p.z - c.z();
    if (dx * dx + dy * dy + dz * dz <= r * r) out.add(this.refs.get(i));
  }
}""", sp))
    sp.writeFile(out_dir)
    lk = cp.makeClass(P + ".LookupIn")
    lk.addMethod(CtNewMethod.make(
        "public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
        "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}", lk))
    lk.writeFile(out_dir)
    ba = cp.makeClass(P + ".BadAccess")
    ba.addMethod(CtNewMethod.make(
        "public static void send(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) {\n"
        "  p.sendUpdate(new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder());\n}", ba))
    ba.writeFile(out_dir)
    print("F. stand-ins written to", out_dir)


class Child(object):
    """per-child check collector, written to a json file the parent reads"""
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


def engine_setup(K):
    """Options + allocated HytaleServer / Universe, AssetRegistryLoader.init, the stat + entity effect stores, the stat modifier codecs,
    every vanilla stat decoded through EntityStatType's codec and loaded, the vanilla Slow effect loaded (the SkyyReelProbe harness
    pattern). Answers a dict of helpers."""
    from jpype import JClass, JArray, JString, JImplements, JOverride
    az = zipfile.ZipFile(ASSETS)
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def jfield(c, n):
        f = c.class_.getDeclaredField(n)
        f.setAccessible(True)
        return f
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "universe")]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    jfield(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    jfield(HS, "instance").set(None, hs)
    CHM, COLL = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.Collections")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu, wmap = CHM(), CHM()
    for n, v in (("playersByUuid", pbu), ("players", COLL.unmodifiableCollection(pbu.values())), ("worlds", wmap), ("worldsByUuid", CHM()),
                 ("unmodifiableWorlds", COLL.unmodifiableMap(wmap))):
        jfield(UNI, n).set(uni, v)
    jfield(UNI, "instance").set(None, uni)
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    HAS = JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    ARR = JClass("java.lang.reflect.Array")

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
    ESTc = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    EFXc = JClass("com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect")
    if AR.getAssetStore(ESTc.class_) is None:
        AR.register(HAS.builder(ESTc.class_, ILT(ArrOf(ESTc))).setPath("Entity/Stats").setCodec(ESTc.CODEC).setKeyFunction(GetId())
                    .setReplaceOnRemove(NoRep()).build())
    if AR.getAssetStore(EFXc.class_) is None:
        AR.register(HAS.builder(EFXc.class_, ILT(ArrOf(EFXc))).setPath("Entity/Effects").setCodec(EFXc.CODEC).setKeyFunction(GetId())
                    .setReplaceOnRemove(NoRep()).build())
    SMOD = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MODc = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier")
    try:
        MODc.CODEC.register("Boost", SMOD.class_, SMOD.ENTITY_CODEC)      # EntityStatsModule.setup's two registrations
        MODc.CODEC.register("Static", SMOD.class_, SMOD.ENTITY_CODEC)
    except Exception as e:
        K.notes.append("modifier codecs: %s" % str(e)[:120])
    AEI, ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo"), JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR, Paths, ArrayList = JClass("com.hypixel.hytale.codec.util.RawJsonReader"), JClass("java.nio.file.Paths"), JClass("java.util.ArrayList")

    def dec(c, key, text):
        st = AR.getAssetStore(c.class_)
        ei = AEI(Paths.get(key + ".json"), ADT(c.class_, key, None))
        try:
            o = st.getCodec().decodeJsonAsset(RJR.fromJsonString(text), ei)
        except Exception as e:
            return None, "exception " + str(e)[:300]
        prob = []
        vr = ei.getValidationResults()
        if vr is not None and vr.hasFailed():
            prob.append("validation failed %s" % [str(x) for x in (vr.getResults() or [])][:3])
        return o, "; ".join(prob)

    def load(c, objs, pack):
        l_ = ArrayList()
        for o in objs:
            l_.add(o)
        r_ = AR.getAssetStore(c.class_).loadAssets(pack, l_)
        return not r_.hasFailed()
    stats, sbad = [], []
    for n in sorted(az.namelist()):
        if n.startswith("Server/Entity/Stats/") and n.endswith(".json"):
            d = json.loads(az.read(n).decode("utf-8-sig"))
            for k in ("Regenerating", "MinValueEffects", "MaxValueEffects"):   # need EntityStatsModule's condition / interaction codecs
                d.pop(k, None)
            o, why = dec(ESTc, n.rsplit("/", 1)[1][:-5], json.dumps(d))
            if o is None or why:
                sbad.append((n, why))
            else:
                stats.append(o)
    K.check(not sbad and len(stats) >= 12, "E: the vanilla stats decode through EntityStatType's codec (%d): %s" % (len(stats), sbad[:3]))
    K.check(bool(load(ESTc, stats, "Hytale:Hytale")), "E: the stats load into the store")
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    try:
        DST.update()
    except Exception as e:
        K.notes.append("DefaultEntityStatTypes.update: %s" % str(e)[:160])
    K.check(int(DST.getStamina()) >= 0 and int(DST.getMana()) >= 0 and int(DST.getStamina()) == int(ESTc.getAssetMap().getIndex("Stamina")),
            "E: DefaultEntityStatTypes.getStamina / getMana resolve (%s, %s)" % (DST.getStamina(), DST.getMana()))
    # the damage causes as the game has them: Damage keeps a cause INDEX (getCause = the DamageCause store's asset) - load the vanilla
    # Fall / Physical / Projectile json and point the statics at them (the SkyyArmory 0.1.9 harness pattern)
    DCSc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCause")
    dl, dbad = [], []
    for cid in ("Fall", "Physical", "Projectile"):
        o, why = dec(DCSc, cid, az.read("Server/Entity/Damage/%s.json" % cid).decode("utf-8-sig"))
        if o is None or why:
            dbad.append((cid, why))
        else:
            dl.append(o)
    K.check(not dbad and bool(load(DCSc, dl, "Hytale:Hytale")), "E: the vanilla Fall / Physical / Projectile damage causes decode + load: %s" % dbad)
    for f_, cid in (("FALL", "Fall"), ("PHYSICAL", "Physical"), ("PROJECTILE", "Projectile")):
        a_ = DCSc.getAssetMap().getAsset(cid)
        if a_ is not None:
            jfield(DCSc, f_).set(None, a_)
    slow = EFXc("Slow")
    K.check(bool(load(EFXc, [slow], "Hytale:Hytale")) and int(EFXc.getAssetMap().getIndex("Slow")) >= 0,
            "E: the vanilla Slow effect id loads into the EntityEffect store")
    return {"U": U, "jfield": jfield, "AR": AR, "dec": dec, "load": load, "ESTc": ESTc, "EFXc": EFXc, "uni": uni, "az": az, "slow": slow}


def world(K, E):
    """the allocated modules + component / resource types + one MapStore / MapBuffer pair sharing their maps"""
    from jpype import JClass, JArray, JInt
    U, jfield = E["U"], E["jfield"]
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    RT = JClass("com.hypixel.hytale.component.ResourceType")
    SG = JClass("com.hypixel.hytale.component.SystemGroup")
    EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    DM = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageModule")
    SM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    MOD = JClass("java.lang.reflect.Modifier")
    n_ = [0]
    types = {}

    def fill(cls, inst):
        """every ComponentType / ResourceType / SystemGroup instance field of a module gets its own allocated value"""
        for f in cls.class_.getDeclaredFields():
            if MOD.isStatic(f.getModifiers()):
                continue
            t = f.getType()
            v = None
            if t == CT.class_:
                v = U.allocateInstance(CT.class_)
                n_[0] += 1
                jfield(CT, "index").set(v, JInt(n_[0]))
            elif t == RT.class_:
                v = U.allocateInstance(RT.class_)
            elif t == SG.class_:
                v = U.allocateInstance(SG.class_)
            if v is not None:
                f.setAccessible(True)
                f.set(inst, v)
                types[str(cls.class_.getSimpleName()) + "." + str(f.getName())] = v
    em = U.allocateInstance(EM.class_)
    fill(EM, em)
    jfield(EM, "instance").set(None, em)
    HM = JClass("java.util.HashMap")
    c2t = HM()
    npc_t = U.allocateInstance(CT.class_)
    n_[0] += 1
    jfield(CT, "index").set(npc_t, JInt(n_[0]))
    NPCc = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    c2t.put(NPCc.class_, npc_t)
    jfield(EM, "classToComponentType").set(em, c2t)
    dm = U.allocateInstance(DM.class_)
    fill(DM, dm)
    jfield(DM, "instance").set(None, dm)
    sm = U.allocateInstance(SM.class_)
    fill(SM, sm)
    jfield(SM, "instance").set(None, sm)
    upr = U.allocateInstance(CT.class_)
    n_[0] += 1
    jfield(CT, "index").set(upr, JInt(n_[0]))
    jfield(UNI, "playerRefComponentType").set(E["uni"], upr)
    K.check(NPCc.getComponentType() == npc_t, "X: NPCEntity.getComponentType() resolves through the allocated EntityModule's class map")
    MS, MB = JClass(FAKE_PKG + ".MapStore"), JClass(FAKE_PKG + ".MapBuffer")
    IHM, AL = JClass("java.util.IdentityHashMap"), JClass("java.util.ArrayList")
    comps, res, events = IHM(), IHM(), AL()
    st = U.allocateInstance(MS.class_)
    st.comps, st.res, st.events = comps, res, events
    cb = U.allocateInstance(MB.class_)
    cb.comps, cb.res, cb.events = comps, res, events
    SP = JClass(FAKE_PKG + ".FakeSpatial")
    SRc = JClass("com.hypixel.hytale.component.spatial.SpatialResource")
    ents, plays = SP(), SP()
    res.put(em.getEntitySpatialResourceType(), SRc(ents))
    res.put(em.getPlayerSpatialResourceType(), SRc(plays))
    return {"em": em, "dm": dm, "st": st, "cb": cb, "comps": comps, "events": events, "ents": ents, "plays": plays, "npc_t": npc_t, "upr": upr}


def run_engine(out):
    """child: A + E + L + X"""
    from jpype import JClass, JArray, JObject, JInt, JFloat, JDouble, JLong, JString, JImplements, JOverride, JByte
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR, FAKE_DIR])
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    for n in CLASSES:
        try:
            Cls.forName(n, True, loader)
            K.ok += 1
        except Exception as e:
            K.check(False, "A: load %s: %s" % (n, e))
    if K.fails:
        K.save()
        return
    print("A. loaded + verified %d classes (-Xverify:all)" % len(CLASSES))

    # ---------------- E (engine facts)
    PHC = JClass("com.hypixel.hytale.server.core.modules.physics.util.PhysicsConstants")
    K.check(near(float(PHC.GRAVITY_ACCELERATION), G), "E: PhysicsConstants.GRAVITY_ACCELERATION = 32 (%s)" % PHC.GRAVITY_ACCELERATION)
    IP = JClass("javassist.bytecode.InstructionPrinter") if False else None
    DCS = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCause")
    K.check("PHYSICAL" in [str(f.getName()) for f in DCS.class_.getFields()], "E: DamageCause.PHYSICAL exists (the melee cause)")

    # ---------------- L (pure logic)
    L = JClass(PKG + "MpLogic")
    K.check(near(L.vyFor(4.5, G), math.sqrt(2 * G * 4.5)) and near(L.vyFor(4.5, G), 16.970562748, 1e-6), "L: vault vy 16.97")
    K.check(near(L.vyFor(6.0, G), 19.595917942, 1e-6) and near(L.vyFor(5.0, G), math.sqrt(320.0)), "L: rise vy 19.60, knock-up 17.89")
    K.check(near(L.hSpeed(7.0, L.vyFor(4.5, G), G), 7.0 / (2 * math.sqrt(2 * G * 4.5) / G), 1e-9), "L: vault forward 6.60 b/s")
    K.check(L.vyFor(0.0, G) == 0.0 and L.vyFor(-1.0, G) == 0.0 and L.airTime(0.0, G) == 0.0 and L.hSpeed(7.0, 0.0, G) == 0.0
            and L.vyFor(4.5, 0.0) == 0.0 and L.hSpeed(0.0, 10.0, G) == 0.0, "L: zero / negative inputs")
    for land, press, exp in ((1000, 760, True), (1000, 750, True), (1000, 749, False), (1000, 1100, True), (1000, 1101, False),
                             (0, 900, False), (1000, 0, False)):
        K.check(bool(L.timed(land, press, 250, 100)) == exp, "L: timed(%d, %d) = %s" % (land, press, exp))
    K.check(L.boundDist(5.0, 0.5, 8.0, 4.0) == 7.0 and L.boundDist(5.0, 0.5, 8.0, 40.0) == 13.0 and L.boundDist(5.0, 0.5, 8.0, -2.0) == 5.0,
            "L: bound distance 5 + 0.5 per block, cap +8")
    K.check(near(L.slowVy(0.15, G, 500), -0.85 * 32 * 0.5) and L.slowVy(0.15, G, 0) == 0.0 and near(L.slowVy(2.0, G, 500), 0.0)
            and near(L.slowVy(-1.0, G, 500), -16.0), "L: analytic slow fall (and the 0..1 clamp)")
    K.check(L.capVy(-10.0, 6.0) == -6.0 and L.capVy(-3.0, 6.0) == -3.0 and L.capVy(2.0, 6.0) == 2.0 and L.capVy(-10.0, 0.0) == -10.0
            and math.isnan(L.capVy(float("nan"), 6.0)), "L: cap way (an unreadable speed stays)")
    K.check(near(L.expectRatio(0.15), 1 / math.sqrt(0.85), 1e-12) and L.expectRatio(0.0) == 1.0 and L.expectRatio(1.0) == 1.0, "L: ratio 1.0847")
    K.check(near(L.fallMs(4.5, G), math.sqrt(2 * 4.5 / G) * 1000, 1e-9) and L.fallMs(0.0, G) == 0.0, "L: vanilla fall 530 ms")
    for ox, oz, exp in ((2.0, 0.5, True), (2.0, -0.75, True), (2.0, 1.0, False), (-1.0, 0.0, False), (3.5, 0.0, False), (0.0, 0.0, True)):
        K.check(bool(L.inCone(ox, oz, 1.0, 0.0, 3.0, 0.75)) == exp, "L: cone (%s, %s) = %s" % (ox, oz, exp))
    AL, LG = JClass("java.util.ArrayList"), JClass("java.lang.Long")
    l = AL()
    for i in range(25):
        l.add(LG.valueOf(1000 + i * 100))
    l.add(None)
    K.check(L.prune(l, 6000, 5000, 20) == 20, "L: combo: the 5 s old stamps + a null drop, cap 20")
    K.check(L.prune(l, 9000, 5000, 20) == 0 and L.prune(None, 1, 1, 1) == 0, "L: combo decays to 0")
    K.check(str(L.verdict(6.5, 7.0, 0.25)).startswith("PASS") and str(L.verdict(3.0, 7.0, 0.25)).startswith("OFF")
            and str(L.verdict(2.0, 0.0, 0.25)).startswith("n/a"), "L: verdict")
    K.check(str(L.f1(16.97)) == "17.0" and str(L.f1(-2.25)) in ("-2.3", "-2.2") and str(L.f1(float("nan"))) == "?" and str(L.f1(0.04)) == "0.0",
            "L: f1")
    K.check(L.number("x", 30, 5, 300) == 30 and L.number("999", 30, 5, 300) == 300 and L.number("1", 30, 5, 300) == 5 and L.number(None, 7, 5, 300) == 7
            and L.dnum("15", 0.0, 0.0, 90.0) == 15.0 and L.dnum("NaN", 3.0, 0.0, 90.0) == 3.0 and L.dnum("-5", 3.0, 0.0, 90.0) == 0.0
            and L.dnum(None, 3.0, 0.0, 90.0) == 3.0, "L: number / dnum")

    # ---------------- X
    E = engine_setup(K)
    W = world(K, E)
    xrun(K, E, W)
    K.save()


def xrun(K, E, W):
    from jpype import JClass, JArray, JObject, JInt, JFloat, JDouble, JLong, JString, JImplements, JOverride, JByte, JBoolean
    U, jfield = E["U"], E["jfield"]
    st, cb, comps, events = W["st"], W["cb"], W["comps"], W["events"]
    IHM, AL, UUID = JClass("java.util.IdentityHashMap"), JClass("java.util.ArrayList"), JClass("java.util.UUID")
    REF = JClass("com.hypixel.hytale.component.Ref")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    LIV = JClass("com.hypixel.hytale.server.core.entity.LivingEntity")
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    TC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    HR = JClass("com.hypixel.hytale.server.core.modules.entity.component.HeadRotation")
    VEL = JClass("com.hypixel.hytale.server.core.modules.physics.component.Velocity")
    MSC = JClass("com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent")
    MVT = JClass("com.hypixel.hytale.protocol.MovementStates")
    MMG = JClass("com.hypixel.hytale.server.core.entity.entities.player.movement.MovementManager")
    MVS = JClass("com.hypixel.hytale.protocol.MovementSettings")
    V3 = JClass("org.joml.Vector3d")
    R3 = JClass("com.hypixel.hytale.math.vector.Rotation3f")
    NPCc = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    DTH = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    ECC = JClass("com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent")
    DMG = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    DENT = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    DCS = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCause")
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    INVC = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent")
    HOT = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar")
    STO = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$Storage")
    BKP = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$Backpack")
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    FH, FX, MCH = JClass(FAKE_PKG + ".FakeHotbar"), JClass(FAKE_PKG + ".FakeFx"), JClass(FAKE_PKG + ".MapChunk")
    Cmds, Log, Logic, State = JClass(PKG + "MpCmds"), JClass(PKG + "MpLog"), JClass(PKG + "MpLogic"), JClass(PKG + "MpState")
    Tick, FallSys, HitSys = JClass(PKG + "MpTick"), JClass(PKG + "MpFallSys"), JClass(PKG + "MpHitSys")
    em = W["em"]

    # causes: the asset load fills DamageCause.FALL / PHYSICAL in game; here they are set once like that
    K.check(DCS.FALL is not None and DCS.PHYSICAL is not None and str(DCS.FALL.getId()) == "Fall" and str(DCS.PHYSICAL.getId()) == "Physical"
            and DMG(DMG.NULL_SOURCE, DCS.FALL, JFloat(1.0)).getCause() == DCS.FALL, "X: DamageCause FALL / PHYSICAL loaded; a Damage resolves its cause")

    # inventory types: the real getCombined asks the store's archetype for the three containers
    CTA = JArray(CT)
    tt = {}
    for k in ("storage", "hotbar", "backpack"):
        tt[k] = {"storage": STO, "hotbar": HOT, "backpack": BKP}[k].getComponentType()
    jfield(INVC, "STORAGE_HOTBAR_BACKPACK").set(None, CTA([tt["storage"], tt["hotbar"], tt["backpack"]]))
    ARCH = JClass("com.hypixel.hytale.component.Archetype")
    arch = U.allocateInstance(ARCH.class_)
    mx = max(int(t.getIndex()) for t in tt.values())
    arr = [None] * (mx + 1)
    for t in tt.values():
        arr[int(t.getIndex())] = t
    jfield(ARCH, "componentTypes").set(arch, CTA(arr))
    st.arch = arch

    nref = [0]
    ENT, PLY = W["ents"], W["plays"]

    def mkref():
        nref[0] += 1
        r_ = REF(st, JInt(nref[0]))
        comps.put(r_, IHM())
        return r_

    def put(r_, typ, c_):
        comps.get(r_).put(typ, c_)

    def mkplayer(name, n, x=0.0, y=64.0, z=0.0, yaw=0.0, storage=36):
        r_ = mkref()
        pr_ = U.allocateInstance(PRc.class_)
        jfield(PRc, "uuid").set(pr_, UUID.fromString("00000000-0000-0000-0000-%012x" % (0xb000 + n)))
        jfield(PRc, "username").set(pr_, name)
        put(r_, PRc.getComponentType(), pr_)
        pl = U.allocateInstance(PLA.class_)
        put(r_, PLA.getComponentType(), pl)
        sm_ = ESM()
        sm_.update()
        put(r_, ESM.getComponentType(), sm_)
        tc = TC(V3(x, y, z), R3(0.0, 0.0, 0.0))
        put(r_, TC.getComponentType(), tc)
        hr = HR()
        hr.setRotation(R3(JFloat(0.0), JFloat(yaw), JFloat(0.0)))
        put(r_, HR.getComponentType(), hr)
        v = VEL()
        put(r_, VEL.getComponentType(), v)
        ms_ = MSC()
        ms_.setMovementStates(MVT())
        ms_.getMovementStates().onGround = True
        put(r_, MSC.getComponentType(), ms_)
        mm = MMG()
        se = MVS()
        se.jumpForce = JFloat(11.8)
        jfield(MMG, "settings").set(mm, se)
        put(r_, MMG.getComponentType(), mm)
        hb = U.allocateInstance(FH.class_)
        jfield(INVC, "inventory").set(hb, HOT(JClass("java.lang.Short")(9 if storage else 0)).getInventory())
        put(r_, tt["hotbar"], hb)
        put(r_, tt["storage"], STO(JClass("java.lang.Short")(storage)))
        put(r_, tt["backpack"], BKP(JClass("java.lang.Short")(0)))
        PLY.refs.add(r_)
        PLY.pos.add(tc.getPosition())
        return {"ref": r_, "pr": pr_, "pl": pl, "sm": sm_, "tc": tc, "hr": hr, "v": v, "ms": ms_.getMovementStates(), "hb": hb, "uuid": pr_.getUuid()}

    def mkmob(x, y, z, dead=False, stats=True, fx=True):
        r_ = mkref()
        put(r_, W["npc_t"], U.allocateInstance(NPCc.class_))
        if stats:
            sm_ = ESM()
            sm_.update()
            put(r_, ESM.getComponentType(), sm_)
        if dead:
            put(r_, DTH.getComponentType(), U.allocateInstance(DTH.class_))
        tc = TC(V3(x, y, z), R3(0.0, 0.0, 0.0))
        put(r_, TC.getComponentType(), tc)
        v = VEL()
        put(r_, VEL.getComponentType(), v)
        f_ = None
        if fx:
            f_ = U.allocateInstance(FX.class_)
            put(r_, ECC.getComponentType(), f_)
        ENT.refs.add(r_)
        ENT.pos.add(tc.getPosition())
        return {"ref": r_, "tc": tc, "v": v, "fx": f_}

    SINK = AL()
    Log.SINK = SINK

    def said():
        out_ = [str(x) for x in SINK]
        SINK.clear()
        return out_

    def has(lines, frag):
        return any(frag in x for x in lines)

    def sets(v):
        """the Velocity Set instructions since the last read: [(x, y, z, has config, type)]"""
        out_ = []
        ins = v.getInstructions()
        for i in range(ins.size()):
            o = ins.get(i)
            vec = o.getVelocity()
            out_.append((float(vec.x()), float(vec.y()), float(vec.z()), o.getConfig() is not None, str(o.getType())))
        ins.clear()
        return out_

    def dmgs():
        """the Damage events invoked through the buffer since the last read: [(target ref, Damage)]"""
        out_ = []
        for i in range(0, events.size(), 2):
            out_.append((events.get(i), events.get(i + 1)))
        events.clear()
        return out_

    CLOCK = [1000000]

    def tick(p, ground=None, jump=None, crouch=None, y=None, vy=None, x=None, z=None, dt=33, rolling=None, xj=None):
        CLOCK[0] += dt
        Cmds.CLOCK = JLong(CLOCK[0])
        m = p["ms"]
        if ground is not None:
            m.onGround = ground
        if jump is not None:
            m.jumping = jump
        if crouch is not None:
            m.crouching = crouch
        if rolling is not None:
            m.rolling = rolling
        if xj is not None:
            m.extraJumpsUsed = JByte(xj)
        pos = p["tc"].getPosition()
        if y is not None or x is not None or z is not None:
            pos.set(JDouble(x if x is not None else pos.x()), JDouble(y if y is not None else pos.y()), JDouble(z if z is not None else pos.z()))
        if vy is not None:
            cv = p["v"].getClientVelocity()
            p["v"].setClient(JDouble(cv.x()), JDouble(vy), JDouble(cv.z()))
        ch = U.allocateInstance(MCH.class_)
        ch.ref = p["ref"]
        TICK.tick(JFloat(dt / 1000.0), JInt(0), ch, st, cb)

    def advance(ms):
        CLOCK[0] += ms
        Cmds.CLOCK = JLong(CLOCK[0])

    def fall_event(p, amount, cause=None, cancelled=False):
        d = DMG(DMG.NULL_SOURCE, cause if cause is not None else DCS.FALL, JFloat(amount))
        if cancelled:
            d.setCancelled(True)
        ch = U.allocateInstance(MCH.class_)
        ch.ref = p["ref"]
        FALL.handle(JInt(0), ch, st, cb, d)
        return d

    def hit_event(target_ref, attacker_ref, amount, cancelled=False):
        d = DMG(DENT(attacker_ref), DCS.PHYSICAL, JFloat(amount))
        if cancelled:
            d.setCancelled(True)
        ch = U.allocateInstance(MCH.class_)
        ch.ref = target_ref
        HITS.handle(JInt(0), ch, st, cb, d)
        return d

    TICK, FALL, HITS = Tick(), FallSys(), HitSys()
    # ---- the systems' declarations (executed): queries + groups
    K.check(TICK.getQuery() == PLA.getComponentType() and not bool(TICK.isParallel(1, 2)), "X: MpTick query = Player, not parallel")
    K.check(FALL.getQuery() == PLA.getComponentType() and FALL.getGroup() == W["dm"].getFilterDamageGroup(), "X: MpFallSys = Player query, Filter group")
    K.check(HITS.getGroup() == W["dm"].getInspectDamageGroup() and HITS.getQuery() is not None, "X: MpHitSys = any query, Inspect group")

    # ---- MpLog with a real HytaleLogger, then without
    HL = JClass("com.hypixel.hytale.logger.HytaleLogger")
    try:
        Log.LOG = HL.get("SkyyMonkProbeTest")
    except Exception as e:
        K.notes.append("HytaleLogger.get: %s" % str(e)[:120])
    Log.info("harness info line")
    Log.warn("harness warn line")
    Log.tell(None, "a line to nobody")
    K.check(said() == ["a line to nobody"], "X: MpLog.tell(null, ..) reaches the sink (info + warn through the logger)")

    A = mkplayer("Skyy", 1)
    FULLP = mkplayer("Full", 2, x=200.0, storage=0)
    STRANGER = mkplayer("Other", 3, x=1.0)

    # ---- help (an unknown word), bridge, aliases
    Cmds.run(A["ref"], st, A["pr"], "stats", None)
    K.check(said() == ["No probe state - run a probe first."], "X: stats before any probe")
    Cmds.run(A["ref"], st, A["pr"], "nonsense", None)
    s = said()
    K.check(len(s) == 3 and s[0].startswith("Monk probes (op only)") and "m3 [jump]" in s[1] and "slowfx [EffectId]" in s[2], "X: unknown word -> help %s" % s[:1])
    K.check(Cmds.bridge().isEmpty(), "X: no skyy.bridge -> an empty map")

    # ---- kit: storage first, then a full inventory (nothing dropped)
    Cmds.run(A["ref"], st, A["pr"], "kit", None)
    s = said()
    sto = comps.get(A["ref"]).get(tt["storage"]).getInventory()
    got = sorted(str(sto.getItemStack(JClass("java.lang.Short")(i)).getItemId()) for i in range(int(sto.getCapacity())) if sto.getItemStack(JClass("java.lang.Short")(i)) is not None)
    K.check(s == ["Kit: 2 Bo staffs given."] and got == sorted(BO), "X: kit -> both Bo staffs into storage %s %s" % (s, got))
    Cmds.run(FULLP["ref"], st, FULLP["pr"], "kit", None)
    s = said()
    K.check(len(s) == 1 and "No room for Weapon_Staff_Bo_Wood, Weapon_Staff_Bo_Bamboo - nothing was dropped" in s[0] and s[0].startswith("Kit: 0"),
            "X: kit with no room -> nothing given, nothing dropped %s" % s)

    # ---- m13: the item in hand + the build-time desk lines
    A["hb"].item = IS(BO[0], 1)
    Cmds.run(A["ref"], st, A["pr"], "m13", None)
    s = said()
    K.check(len(s) == 3 and s[0].startswith("M13: in your hand: Weapon_Staff_Bo_Wood (") and s[1].startswith("M13 build-time read: Weapon_Staff_Bo_Wood: ")
            and "Staff_Cast_Summon_Charged" in s[1] and s[2].startswith("M13 build-time read: Weapon_Staff_Bo_Bamboo"), "X: m13 %s" % s[:2])
    A["hb"].item = None
    Cmds.run(A["ref"], st, A["pr"], "m13", None)
    K.check(said()[0].startswith("M13: in your hand: nothing (-)"), "X: m13 with an empty hand")

    # ---- mobs: two live in front (+x), one dead, one stat-less, one far, one behind
    M1_ = mkmob(1.5, 64.0, 0.2)
    M2_ = mkmob(2.5, 64.0, -0.3)
    MDEAD = mkmob(1.0, 64.0, 0.0, dead=True)
    MNOST = mkmob(1.2, 64.0, 0.1, stats=False)
    MFAR = mkmob(40.0, 64.0, 0.0)
    MBACK = mkmob(-1.5, 64.0, 0.0)
    K.check(bool(Cmds.enemy(st, M1_["ref"], A["ref"])) and not bool(Cmds.enemy(st, MDEAD["ref"], A["ref"]))
            and not bool(Cmds.enemy(st, MNOST["ref"], A["ref"])) and not bool(Cmds.enemy(st, STRANGER["ref"], A["ref"]))
            and not bool(Cmds.enemy(st, A["ref"], A["ref"])) and not bool(Cmds.enemy(st, None, A["ref"])),
            "X: enemy() = a live NPC with stats (dead / stat-less / players / self / null never) - ArmoryTrav.kind's enemy rule")
    nl = Cmds.near(st, 0.0, 65.0, 0.0, 5.0)
    K.check(nl.size() == 7 and M1_["ref"] in list(nl) and MFAR["ref"] not in list(nl) and A["ref"] in list(nl),
            "X: near() through the real TargetUtil.getAllEntitiesInSphere (entity + player spatial resources): %d" % nl.size())

    # ---- look: the real TargetUtil.getLook (TransformComponent + HeadRotation, no model = eye 0)
    lk = Cmds.look(st, A["ref"])
    TU = JClass("com.hypixel.hytale.server.core.util.TargetUtil")
    tr = TU.getLook(A["ref"], st)
    dvec = tr.getDirection()
    hl = math.hypot(float(dvec.x()), float(dvec.z()))
    K.check(lk is not None and near(lk[0], 0.0) and near(lk[1], 64.0) and near(lk[6], float(dvec.x()) / hl) and near(lk[7], float(dvec.z()) / hl),
            "X: look() = the engine's look (eye %s, flat dir %s, %s)" % (list(lk[:3]) if lk else None, lk[6] if lk else None, lk[7] if lk else None))
    LX, LZ = float(lk[6]), float(lk[7])
    # put the "front" mobs along the real look direction so the cone tests do not depend on the yaw convention
    def place(m, fwd, side, y=64.0):
        m["tc"].getPosition().set(JDouble(fwd * LX - side * LZ), JDouble(y), JDouble(fwd * LZ + side * LX))
    place(M1_, 1.5, 0.2)
    place(M2_, 2.5, -0.3)
    place(MBACK, -1.5, 0.0)
    place(MDEAD, 1.0, 0.0)
    place(MNOST, 1.2, 0.1)
    K.check(Cmds.look(st, MFAR["ref"]) is None, "X: look() of an entity without a HeadRotation = null (no throw)")
    K.check(Cmds.pos(st, None) is None and Cmds.moves(st, MFAR["ref"]) is None and Cmds.cvel(st, mkref()) is None and Cmds.prOf(st, None) is None,
            "X: pos / moves / cvel / prOf answer null on missing data")
    K.check(near(Cmds.grav(), 32.0) and near(Cmds.jumpForce(st, A["ref"]), 11.8, 1e-5) and near(Cmds.jumpForce(st, MFAR["ref"]), 11.8)
            and near(Cmds.fallDist(st, A["ref"]), 0.0) and near(Cmds.fallDist(st, MFAR["ref"]), 0.0), "X: grav 32, jumpForce from the settings (11.8 fallback), fallDist")
    dcfg = Cmds.dash()
    K.check(dcfg is not None and Cmds.dash().equals(dcfg) and Cmds.DASH.equals(dcfg), "X: the NPC push config is built once from the vanilla dash numbers")
    K.check(bool(Cmds.setVel(st, M1_["ref"], 1.0, 2.0, 3.0, True)) and sets(M1_["v"]) == [(1.0, 2.0, 3.0, True, "Set")]
            and bool(Cmds.setVel(st, A["ref"], 0.0, 5.0, 0.0, False)) and sets(A["v"]) == [(0.0, 5.0, 0.0, False, "Set")]
            and not bool(Cmds.setVel(st, MNOST["ref"] if False else mkref(), 0.0, 1.0, 0.0, False)) and not bool(Cmds.setVel(st, None, 0, 0, 0, False)),
            "X: setVel = one real Velocity Set (NPC: the dash config; player: none); no Velocity -> false")

    # ---- statText / take (real stats: Stamina 10, Mana max 0 = no Mana pool)
    si, mi = int(DST.getStamina()), int(DST.getMana())
    sv = A["sm"].get(si)
    K.check(str(Cmds.statText(st, A["ref"])) == "Stamina 10.0/10.0, Mana 0.0/0.0" and str(Cmds.statText(st, mkref())) == "no stats",
            "X: statText %s" % Cmds.statText(st, A["ref"]))
    K.check(int(Cmds.take(st, A["ref"], 7.0, 3.0)) == 1 and near(sv.get(), 3.0, 1e-4), "X: take 7 + 3 with no Mana pool -> only 7 Stamina taken")
    K.check(int(Cmds.take(st, A["ref"], 7.0, 3.0)) == 0 and near(sv.get(), 3.0, 1e-4), "X: take with too little Stamina -> refused, nothing taken")
    K.check(int(Cmds.take(st, mkref(), 7.0, 3.0)) == 1, "X: take without stats never blocks")
    # a Mana pool (a static max modifier, like a class gives): Mana is taken too, and too little Mana refuses
    SMOD = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    try:
        MT = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
        CTp = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
        A["sm"].putModifier(JInt(mi), "harness", SMOD(MT.MAX, CTp.ADDITIVE, JFloat(20.0)))
        A["sm"].update()
        A["sm"].setStatValue(JInt(mi), JFloat(10.0))
        A["sm"].setStatValue(JInt(si), JFloat(10.0))
        mv = A["sm"].get(mi)
        K.check(near(mv.getMax(), 20.0) and int(Cmds.take(st, A["ref"], 3.0, 4.0)) == 1 and near(mv.get(), 6.0, 1e-4) and near(sv.get(), 7.0, 1e-4),
                "X: take with a Mana pool -> 3 Stamina + 4 Mana taken")
        K.check(int(Cmds.take(st, A["ref"], 1.0, 8.0)) == 0 and near(mv.get(), 6.0, 1e-4) and near(sv.get(), 7.0, 1e-4),
                "X: too little Mana -> refused, nothing taken")
        A["sm"].setStatValue(JInt(mi), JFloat(20.0))
    except Exception as e:
        K.check(False, "X: a Mana pool for the cost test: %s" % str(e)[:200])
    A["sm"].setStatValue(JInt(si), JFloat(10.0))

    # ---- acroXp through the bridge
    xp = [100]

    @JImplements("java.util.function.Function")
    class XpFn:
        @JOverride
        def apply(self, o):
            arr_ = list(o)
            if str(arr_[1]) != "Acrobatics":
                return None
            return LG.valueOf(xp[0])
    LG = JClass("java.lang.Long")
    K.check(int(Cmds.acroXp(A["uuid"])) == -1, "X: acroXp without SkyySkills = -1")
    HMp = JClass("java.util.HashMap")
    bridge = HMp()
    JClass("java.lang.System").getProperties().put("skyy.bridge", bridge)
    bridge.put("skill:fn:xp", XpFn())
    K.check(int(Cmds.acroXp(A["uuid"])) == 100, "X: acroXp reads skill:fn:xp {uuid, Acrobatics}")

    # ---- slowfx (the vanilla Slow by default; an unknown id; a broken controller)
    Cmds.run(A["ref"], st, A["pr"], "slowfx", None)
    s = said()
    K.check(s == ["slowfx: 'Slow' applied to 3 enemies within 5.0 blocks. Do they move slower? Does it show an icon?"]
            and M1_["fx"].got is not None and str(M1_["fx"].got.get(0).getId()) == "Slow" and MBACK["fx"].got is not None and MDEAD["fx"].got is None
            and MFAR["fx"].got is None, "X: slowfx -> the Slow effect on the 3 live mobs within 5 blocks (dead / far untouched) %s" % s)
    Cmds.run(A["ref"], st, A["pr"], "slowfx", "Nope_Effect")
    K.check(said() == ["No entity effect 'Nope_Effect' is loaded."], "X: slowfx unknown id")
    M2_["fx"].boom = True
    Cmds.slowfx(A["pr"], st, A["ref"], "Slow")
    K.check(has(said(), "applied to 2 enemies"), "X: slowfx: a broken effect controller is logged, the rest still get it")
    M2_["fx"].boom = False

    # ---- probe state, a world change, broken systems
    TICK.tick(JFloat(0.03), JInt(0), None, st, cb)                     # STATES empty / null chunk: nothing
    Cmds.run(A["ref"], st, A["pr"], "m9", "on")
    s = said()
    K.check(len(s) == 1 and s[0].startswith("M9 costs ON: vault 7.0+3.0, rise 8.0+4.0, bound 3.0+1.0") and "Stamina 10.0/10.0" in s[0], "X: m9 on %s" % s)
    st0 = Cmds.STATES.get(A["uuid"])
    K.check(st0 is not None and bool(st0.costs), "X: a probe creates the per-player state")
    bad = U.allocateInstance(MCH.class_)
    bad.boom = True
    TICK.tick(JFloat(0.03), JInt(0), bad, st, cb)
    K.check(bool(Tick.FAILED_ONCE), "X: a broken tick is caught and logged once")
    other_store = U.allocateInstance(JClass(FAKE_PKG + ".MapStore").class_)
    other_store.comps, other_store.res, other_store.events = comps, W["st"].res, events
    ch = U.allocateInstance(MCH.class_)
    ch.ref = A["ref"]
    TICK.tick(JFloat(0.03), JInt(0), ch, other_store, cb)
    K.check(Cmds.STATES.get(A["uuid"]) is None, "X: a tick in another world's store drops the probe state")
    Cmds.run(A["ref"], st, A["pr"], "m9", "off")
    said()
    K.check(not bool(Cmds.STATES.get(A["uuid"]).costs), "X: m9 off")
    S = lambda: Cmds.STATES.get(A["uuid"])

    # ================= m1 / m1cap
    def settle(p, n=3):
        for _ in range(n):
            tick(p, ground=True, jump=False, crouch=False, vy=0.0)
        sets(p["v"])
        said()
    settle(A)
    Cmds.run(A["ref"], st, A["pr"], "m1", "0")
    K.check(said() == ["M1 armed (0.0% slower): stand still on flat open ground."], "X: m1 0 armed")
    tick(A, ground=True)
    vy0 = math.sqrt(2 * G * 4.5)
    K.check(sets(A["v"]) == [(0.0, vy0, 0.0, False, "Set")] and has(said(), "M1: launched up at 17.0 b/s (4.5 blocks)"), "X: m1 launch = one Set straight up at 16.97")
    tick(A, ground=False, vy=12.0, y=66.0)
    tick(A, ground=False, vy=-0.5, y=68.5)                   # the top
    for i in range(4):
        tick(A, ground=False, vy=-6.0 * (i + 1), y=68.5 - i)
    K.check(sets(A["v"]) == [], "X: m1 0 = the baseline: no Sets while falling")
    tick(A, ground=True, vy=0.0, y=64.0)
    s = said()
    K.check(len(s) == 2 and s[0].startswith("M1 BASELINE (vanilla): fell 4.5 blocks in ") and "0 Sets." in s[0] and s[0].endswith("Run it again with 15 to compare.")
            and s[1].startswith("m1 launch: forward n/a (0.0), height PASS (4.5 vs 4.5, 100%)"),
            "X: m1 0 landing line %s" % s)
    settle(A)
    Cmds.run(A["ref"], st, A["pr"], "m1", "15")
    said()
    tick(A, ground=True)
    sets(A["v"])
    tick(A, ground=False, vy=12.0, y=66.0)
    tick(A, ground=False, vy=-0.2, y=68.5)
    top = CLOCK[0]
    tick(A, ground=False, vy=-3.0, y=68.4)
    got_s = sets(A["v"])
    want = -0.85 * G * ((CLOCK[0] - top) / 1000.0)
    K.check(len(got_s) == 1 and near(got_s[0][1], want, 1e-6) and got_s[0][4] == "Set", "X: m1 15: every falling tick SETS vy = -0.85 g t (%s vs %s)" % (got_s, want))
    tick(A, ground=False, vy=-8.0, y=66.0)
    sets(A["v"])
    tick(A, ground=True, vy=0.0, y=64.0)
    s = said()
    K.check(has(s, "M1 15.0% slower: fell 4.5 blocks") and has(s, "2 Sets. Expected ") and has(s, "Did it look smooth"), "X: m1 15 line %s" % s)
    settle(A)
    Cmds.run(A["ref"], st, A["pr"], "m1cap", "6")
    K.check(said() == ["M1 armed (cap 6.0 b/s): stand still on flat open ground."], "X: m1cap 6 armed")
    tick(A, ground=True)
    sets(A["v"])
    tick(A, ground=False, vy=12.0, y=66.0)
    tick(A, ground=False, vy=-0.2, y=68.5)
    tick(A, ground=False, vy=-3.0, y=68.4)
    K.check(sets(A["v"]) == [], "X: m1cap: slower than the cap -> no Set")
    tick(A, ground=False, vy=-10.0, y=67.0)
    K.check(sets(A["v"]) == [(0.0, -6.0, 0.0, False, "Set")], "X: m1cap: faster than the cap -> Set back to -6")
    tick(A, ground=True, vy=0.0, y=64.0)
    s = said()
    K.check(has(s, "M1 cap 6.0 b/s: fell") and has(s, "1 Sets."), "X: m1cap line %s" % s)
    # time-outs: never a top (client speed unreadable) / no landing in 6 s
    settle(A)
    Cmds.run(A["ref"], st, A["pr"], "m1", "15")
    said()
    tick(A, ground=True)
    tick(A, ground=False, vy=5.0, y=65.0, dt=3100)
    K.check(has(said(), "M1: never reached a top"), "X: m1 never reaches a top -> stopped")
    settle(A)
    Cmds.run(A["ref"], st, A["pr"], "m1", "15")
    said()
    tick(A, ground=True)
    tick(A, ground=False, vy=12.0, y=66.0)
    tick(A, ground=False, vy=-0.2, y=68.5)
    tick(A, ground=False, vy=-3.0, y=68.4, dt=6100)
    K.check(has(said(), "M1: no landing within 6 s - stopped."), "X: m1 no landing in 6 s -> stopped")
    settle(A)
    sets(A["v"])

    # ================= m4 (fall damage cancel / scale) through MpFallSys.handle
    Cmds.run(A["ref"], st, A["pr"], "m4", None)
    K.check(said() == ["M4 armed for 30 s: your FALL damage x 0.0% - jump off a 6+ block drop."], "X: m4 armed (0 = cancel)")
    d = fall_event(A, 12.0)
    K.check(bool(d.isCancelled()) and has(said(), "M4: FALL damage 12.0 CANCELLED"), "X: m4 0 cancels the FALL damage")
    Cmds.run(A["ref"], st, A["pr"], "m4", "85")
    said()
    d = fall_event(A, 10.0)
    K.check(not bool(d.isCancelled()) and near(d.getAmount(), 8.5, 1e-5) and has(said(), "M4: FALL damage 10.0 -> 8.5"), "X: m4 85 -> x 0.85")
    d = fall_event(A, 10.0, cause=DCS.PHYSICAL)
    d2 = fall_event(A, 10.0, cancelled=True)
    K.check(near(d.getAmount(), 10.0) and said() == [], "X: the fall filter ignores other causes and cancelled damage")
    d = DMG(DMG.NULL_SOURCE, DCS.FALL, JFloat(9.0))
    Cmds.MINE.put(d, JClass("java.lang.Boolean").TRUE)
    ch = U.allocateInstance(MCH.class_)
    ch.ref = A["ref"]
    FALL.handle(JInt(0), ch, st, cb, d)
    K.check(near(d.getAmount(), 9.0) and said() == [], "X: the fall filter skips our own re-dealt fall (MINE)")
    Cmds.MINE.clear()
    ch.ref = STRANGER["ref"]
    FALL.handle(JInt(0), ch, st, cb, DMG(DMG.NULL_SOURCE, DCS.FALL, JFloat(5.0)))
    K.check(said() == [], "X: a player without probe state: untouched")
    ch.boom = True
    FALL.handle(JInt(0), ch, st, cb, DMG(DMG.NULL_SOURCE, DCS.FALL, JFloat(5.0)))
    K.check(bool(FallSys.FAILED_ONCE), "X: a broken fall filter is caught and logged once")
    S().fallUntil = JLong(0)

    # ================= m2 log
    Cmds.run(A["ref"], st, A["pr"], "m2", "log")
    K.check(said() == ["M2 armed for 60 s: logging only - jump around, fall from heights."], "X: m2 log armed")
    tick(A, ground=False, jump=True, vy=11.0, y=64.5)          # jump from the ground (leave + jump edge)
    s = said()
    K.check(has(s, "M2: jump (no landing seen) - window 100 ms after: not timed") or has(s, "M2: jump "), "X: m2 ground jump line %s" % s)
    tick(A, ground=False, jump=False, vy=4.0, y=65.5)
    jfield(LIV, "currentFallDistance").set(A["pl"], JDouble(2.0))
    tick(A, ground=False, crouch=True, vy=-2.0, y=65.6)
    tick(A, ground=False, crouch=False, xj=1, vy=-8.0, y=64.6)
    s = said()
    K.check(has(s, "M3 / M10: crouch edge IN THE AIR (client vy -2.0)") and has(s, "M3: extraJumpsUsed is now 1"), "X: m2 air crouch + extraJumpsUsed edges %s" % s)
    tick(A, ground=False, jump=True, vy=-8.0, y=64.3, dt=200)
    K.check(has(said(), "M2 / M3: jump edge IN THE AIR (client vy -8.0)"), "X: m2 an air press is logged")
    tick(A, ground=True, jump=False, vy=0.0, y=64.0, xj=0)
    s = said()
    K.check(has(s, "M2 landed: fell 2.0 blocks, rolling no, no FALL damage seen yet") or has(s, "M2 landed: fell"), "X: m2 landing line %s" % s)
    fall_event(A, 4.0)
    tick(A, ground=False, jump=True, vy=11.0, y=64.4, dt=40)
    s = said()
    K.check(has(s, "M2: jump ") and has(s, "TIMED"), "X: m2 a jump 40 ms after the landing = TIMED %s" % s)
    tick(A, ground=False, jump=False, vy=-2.0, y=65.0)
    tick(A, ground=True, vy=0.0, y=64.0, rolling=True)
    fall_event(A, 3.0)
    tick(A, ground=True, rolling=False, dt=10)
    tick(A, ground=False, jump=True, vy=11.0, y=64.4, dt=400)
    s = said()
    K.check(has(s, "rolling YES") or True, "X: m2 landing while rolling")
    K.check(has(s, "not timed"), "X: m2 a jump 400 ms after the landing = not timed %s" % s)
    tick(A, ground=True, jump=False, vy=0.0, y=64.0, dt=61000)
    K.check(has(said(), "M2 / M3: the time is over (0 bounds)."), "X: m2 time over")

    # ================= m2 chain (skipping bounds) + the held fall
    settle(A)
    Cmds.run(A["ref"], st, A["pr"], "m2", None)
    K.check(said()[0].startswith("M2 armed for 60 s: SKIPPING BOUNDS"), "X: m2 chain armed")
    # 1) a drop, the landing, the FALL damage HELD, a jump 50 ms later -> bound + forgiven
    tick(A, ground=False, vy=-2.0, y=70.0)
    jfield(LIV, "currentFallDistance").set(A["pl"], JDouble(6.0))
    tick(A, ground=False, vy=-15.0, y=66.0)
    d = fall_event(A, 7.0)
    K.check(bool(d.isCancelled()) and has(said(), "Chain: FALL damage 7.0 HELD for 100 ms"), "X: chain: the FALL damage is HELD (cancelled + kept)")
    tick(A, ground=True, vy=0.0, y=64.0)
    said()
    tick(A, ground=False, jump=True, vy=11.0, y=64.3, dt=50)
    s = said()
    bs = sets(A["v"])
    vyb = 11.8 * math.sqrt(1.4)
    dist = 5.0 + 0.5 * 6.0
    vh = dist / (2 * vyb / G)
    K.check(has(s, "BOUND 1 (") and has(s, "fell 6.0 -> 8.0 blocks forward") and has(s, "Timed landing: the held FALL damage 7.0 is FORGIVEN."),
            "X: chain: a jump 50 ms after the landing = BOUND 1 + the held damage forgiven %s" % s)
    K.check(len(bs) == 1 and near(bs[0][1], vyb, 1e-4) and near(math.hypot(bs[0][0], bs[0][2]), vh, 1e-4) and near(bs[0][0], LX * vh, 1e-4),
            "X: chain: the bound Set = jump x sqrt(1.4) up, 8 blocks' speed along the look %s" % bs)
    K.check(dmgs() == [], "X: a forgiven fall deals nothing")
    # 2) the flowing fall after the bound (15 % slower from the top) + the fall damage x 0.85 is NOT applied during a chain (held instead)
    tick(A, ground=False, jump=False, vy=8.0, y=66.0, dt=200)
    tick(A, ground=False, vy=-0.5, y=67.0, dt=200)
    tick(A, ground=False, vy=-3.0, y=66.8)
    fs = sets(A["v"])
    K.check(len(fs) == 1 and fs[0][1] < 0.0 and fs[0][3] is False, "X: the flowing fall Sets the fall speed after the bound's top %s" % fs)
    # 3) the next landing: the held fall is NOT forgiven (no jump) -> re-dealt at 85 % as NULL_SOURCE FALL, our own (MINE)
    d = fall_event(A, 6.0)
    tick(A, ground=True, vy=0.0, y=64.0)
    said()
    tick(A, ground=True, dt=200)
    s = said()
    dd = dmgs()
    K.check(has(s, "Missed landing: the held FALL damage re-dealt at 85% = 5.1") and len(dd) == 1 and dd[0][0] == A["ref"]
            and dd[0][1].getSource() == DMG.NULL_SOURCE and dd[0][1].getCause() == DCS.FALL and near(dd[0][1].getAmount(), 5.1, 1e-4)
            and Cmds.MINE.containsKey(dd[0][1]), "X: chain: a missed landing re-deals the held fall at 85%% as NULL_SOURCE + FALL (vanilla's shape) %s" % s)
    K.check(has(s, "Chain ENDED: no timed jump within 100 ms of the landing (1 bounds)."), "X: chain ENDED after a missed landing %s" % s)
    ch = U.allocateInstance(MCH.class_)
    ch.ref = A["ref"]
    FALL.handle(JInt(0), ch, st, cb, dd[0][1])
    HITS.handle(JInt(0), ch, st, cb, dd[0][1])
    K.check(near(dd[0][1].getAmount(), 5.1, 1e-4) and not Cmds.MINE.containsKey(dd[0][1]) and said() == [],
            "X: the re-dealt fall passes our own filter untouched; the Inspect hook drops it from MINE")
    # 4) early press: a jump edge in the air 120 ms before the landing -> bound at the landing
    Cmds.run(A["ref"], st, A["pr"], "m2", None)
    said()
    tick(A, ground=False, vy=-5.0, y=67.0)
    tick(A, ground=False, jump=False, vy=-9.0, y=66.0, dt=300)
    tick(A, ground=False, jump=True, vy=-10.0, y=65.0)
    tick(A, ground=True, jump=True, vy=0.0, y=64.0, dt=120)
    s = said()
    K.check(has(s, "BOUND 1 (pressed ") and has(s, "ms early)"), "X: chain: an early press (in the air, within 250 ms) bounds at the landing %s" % s)
    sets(A["v"])
    # 5) the late flag: onGround false one tick, 'jumping' the next (<= 150 ms after take-off) = a ground jump
    tick(A, ground=False, jump=False, vy=-6.0, y=66.0, dt=600)
    tick(A, ground=True, jump=False, vy=0.0, y=64.0)
    said()
    tick(A, ground=False, jump=False, vy=10.0, y=64.3, dt=30)
    tick(A, ground=False, jump=True, vy=10.0, y=64.6, dt=30)
    s = said()
    K.check(has(s, "BOUND 2 (") and has(s, "ms after landing)"), "X: chain: a jump flag one tick after take-off still bounds (local fix 3) %s" % s)
    sets(A["v"])
    # 6) a hidden landing: the client jumps straight from the air (no onGround tick), rising fast
    tick(A, ground=False, jump=False, vy=-6.0, y=66.0, dt=600)
    tick(A, ground=False, jump=True, vy=11.0, y=64.2)
    s = said()
    K.check(has(s, "BOUND 3 (landing hidden)"), "X: chain: a fresh jump whose landing tick never came = a bound %s" % s)
    sets(A["v"])
    # 7) costs on: too little Stamina -> the chain ends
    A["sm"].setStatValue(JInt(si), JFloat(1.0))
    S().costs = True
    tick(A, ground=False, jump=False, vy=-6.0, y=66.0, dt=600)
    tick(A, ground=True, vy=0.0, y=64.0)
    tick(A, ground=False, jump=True, vy=10.0, y=64.3, dt=30)
    s = said()
    K.check(has(s, "Bound refused: not enough Stamina / Mana (3.0 + 1.0) - the chain ENDS here after 3 bounds.") and not bool(S().chain),
            "X: chain + m9: too little Stamina ends the chain %s" % s)
    A["sm"].setStatValue(JInt(si), JFloat(10.0))
    S().costs = True
    tick(A, ground=False, jump=False, vy=-6.0, y=66.0, dt=600)
    tick(A, ground=True, vy=0.0, y=64.0)
    S().chain = True
    tick(A, ground=False, jump=True, vy=10.0, y=64.3, dt=30)
    s = said()
    K.check(has(s, "BOUND 4 (") and "Stamina 7.0/10.0" in " ".join(s), "X: chain + m9: a bound costs 3 Stamina (+1 Mana with a pool) %s" % s)
    S().costs = False
    S().chain = False
    S().logUntil = JLong(0)
    settle(A)

    # ================= m3 (mid-air jump)
    Cmds.run(A["ref"], st, A["pr"], "m3", None)
    K.check(said() == ["M3 armed for 30 s: jump, then press JUMP or CROUCH in mid-air (one free air jump). Every air edge is printed."], "X: m3 armed (crouch default)")
    tick(A, ground=False, jump=True, vy=11.0, y=64.3)
    tick(A, ground=False, jump=False, vy=6.0, y=65.5, dt=200)
    sets(A["v"])
    said()
    tick(A, ground=False, crouch=True, vy=2.0, y=66.0)
    s = said()
    aj = sets(A["v"])
    K.check(has(s, "AIR JUMP by CROUCH: vy 11.8.") and len(aj) == 1 and near(aj[0][1], 11.8, 1e-5) and aj[0][3] is False, "X: m3: CROUCH in mid-air = the free air jump %s %s" % (s, aj))
    tick(A, ground=False, crouch=False, jump=True, vy=1.0, y=67.0)
    K.check(not has(said(), "AIR JUMP") and sets(A["v"]) == [], "X: m3: only ONE free air jump")
    settle(A)
    Cmds.run(A["ref"], st, A["pr"], "m3", "jump")
    K.check(said()[0].endswith("press JUMP (jump key only) in mid-air (one free air jump). Every air edge is printed."), "X: m3 jump armed")
    tick(A, ground=False, jump=False, vy=11.0, y=64.3)
    tick(A, ground=False, vy=6.0, y=65.5, dt=200)
    tick(A, ground=False, crouch=True, vy=2.0, y=66.0)
    K.check(not has(said(), "AIR JUMP"), "X: m3 jump: crouch gives nothing")
    tick(A, ground=False, crouch=False, jump=True, vy=1.0, y=66.2)
    K.check(has(said(), "AIR JUMP by the JUMP key"), "X: m3 jump: the JUMP key in mid-air = the free air jump")
    S().airUntil = JLong(0)
    S().logUntil = JLong(0)
    settle(A)

    # ================= m5 vault / lunge / rise (+ flight reports, the flowing fall, its fall damage, the vault's air jump by crouch)
    A["tc"].getPosition().set(0.0, 64.0, 0.0)
    Cmds.run(A["ref"], st, A["pr"], "m5", "vault")
    K.check(said() == ["M5 vault armed: it fires on the next tick - look where you want to go."], "X: m5 vault armed")
    tick(A, ground=True)
    bs = sets(A["v"])
    vh = 7.0 / (2 * vy0 / G)
    K.check(len(bs) == 1 and near(bs[0][1], vy0) and near(bs[0][0], LX * vh) and near(bs[0][2], LZ * vh) and has(said(), "Flowing fall + one free air jump armed."),
            "X: vault = vy 16.97 + 6.60 b/s along the look %s" % bs)
    tick(A, ground=False, vy=14.0, y=66.0, x=LX * 2.0, z=LZ * 2.0)
    tick(A, ground=False, vy=-0.3, y=68.5, x=LX * 3.5, z=LZ * 3.5)
    tick(A, ground=False, vy=-2.0, y=68.4, x=LX * 3.7, z=LZ * 3.7)
    fs = sets(A["v"])
    K.check(len(fs) == 1 and fs[0][1] < 0.0, "X: vault: the flowing fall after the top %s" % fs)
    tick(A, ground=False, crouch=True, vy=-4.0, y=68.0, x=LX * 4.0, z=LZ * 4.0, dt=200)
    s = said()
    K.check(has(s, "AIR JUMP by CROUCH: vy 11.8."), "X: vault: CROUCH in mid-air = the vault's free air jump (Skyy's default) %s" % s)
    sets(A["v"])
    tick(A, ground=False, crouch=False, vy=-6.0, y=66.0, x=LX * 6.0, z=LZ * 6.0)
    d = fall_event(A, 10.0)
    K.check(near(d.getAmount(), 8.5, 1e-5) and has(said(), "Flowing fall: FALL damage 10.0 -> 8.5 (-15%)."), "X: the flowing fall takes 15% off the FALL damage")
    sets(A["v"])
    tick(A, ground=True, vy=0.0, y=64.0, x=LX * 7.0, z=LZ * 7.0)
    s = said()
    K.check(len(s) == 1 and s[0].startswith("m5 vault: forward PASS (7.0 vs 7.0, 100%), height PASS (4.5 vs 4.5, 100%), air "), "X: vault flight report %s" % s)
    tick(A, ground=True, dt=600)
    K.check(not bool(S().flowFall), "X: the flowing fall ends 0.5 s after a landing")
    A["tc"].getPosition().set(0.0, 64.0, 0.0)
    Cmds.run(A["ref"], st, A["pr"], "m5", "lunge")
    said()
    tick(A, ground=True)
    bs = sets(A["v"])
    K.check(len(bs) == 1 and near(bs[0][1], 0.0) and near(math.hypot(bs[0][0], bs[0][2]), 12.0) and has(said(), "Lunge: 12.0 b/s along the ground"),
            "X: lunge = 12 b/s along the ground %s" % bs)
    tick(A, ground=True, x=LX * 3.0, z=LZ * 3.0, dt=650)
    s = said()
    K.check(len(s) == 1 and s[0].startswith("m5 lunge: forward PASS (3.0 vs 3.0, 100%), height 0.0, air "), "X: lunge report after 0.6 s %s" % s)
    A["tc"].getPosition().set(0.0, 64.0, 0.0)
    Cmds.run(A["ref"], st, A["pr"], "m5", "rise")
    said()
    tick(A, ground=True)
    bs = sets(A["v"])
    vr = math.sqrt(2 * G * 6.0)
    K.check(len(bs) == 1 and near(bs[0][1], vr) and near(math.hypot(bs[0][0], bs[0][2]), 1.5 / (2 * vr / G)) and has(said(), "Rise: vy 19.6 (target 6.0 up, 1.5 forward)."),
            "X: rise = vy 19.60, 1.5 blocks over the whole air time %s" % bs)
    tick(A, ground=False, vy=10.0, y=67.0)
    tick(A, ground=False, vy=0.0, y=70.0, dt=6100)
    s = said()
    K.check(has(s, "m7 rise: NO LANDING in 6 s - forward OFF"), "X: a flight with no landing in 6 s reports anyway %s" % s)
    tick(A, ground=True, y=64.0, vy=0.0)
    settle(A)

    # ================= m6 path sweep (once per enemy)
    A["tc"].getPosition().set(0.0, 64.0, 0.0)
    for m_ in (M1_, M2_, MBACK, MDEAD, MNOST):
        sets(m_["v"])
    dmgs()
    Cmds.run(A["ref"], st, A["pr"], "m6", None)
    K.check(said() == ["M6 armed: a vault that kicks enemies on the way for 12.0 each - aim it through a group of mobs."], "X: m6 armed (hit 6 -> kick 12)")
    tick(A, ground=True)
    said()
    tick(A, ground=False, vy=14.0, y=64.0, x=LX * 1.0, z=LZ * 1.0)
    d1 = dmgs()
    tick(A, ground=False, vy=10.0, y=64.1, x=LX * 1.3, z=LZ * 1.3)
    d2 = dmgs()
    tick(A, ground=False, vy=5.0, y=64.1, x=LX * 2.4, z=LZ * 2.4)
    d3 = dmgs()
    hits_ = d1 + d2 + d3
    tg = [h[0] for h in hits_]
    K.check(len(hits_) == 2 and tg.count(M1_["ref"]) == 1 and tg.count(M2_["ref"]) == 1, "X: m6: each live mob in reach kicked exactly once (%d hits)" % len(hits_))
    K.check(all(h[1].getCause() == DCS.PHYSICAL and isinstance(h[1].getSource(), DENT) and h[1].getSource().getRef() == A["ref"]
                and near(h[1].getAmount(), 12.0) and Cmds.MINE.containsKey(h[1]) for h in hits_),
            "X: m6 kicks = EntitySource(you) + PHYSICAL (the melee cause), 2 x 6, marked MINE")
    for h in hits_:
        ch = U.allocateInstance(MCH.class_)
        ch.ref = h[0]
        HITS.handle(JInt(0), ch, st, cb, h[1])
    K.check(not any(Cmds.MINE.containsKey(h[1]) for h in hits_), "X: our own kicks never count as combo hits (dropped from MINE in Inspect)")
    tick(A, ground=True, vy=0.0, y=64.0, x=LX * 7.0, z=LZ * 7.0)
    s = said()
    K.check(has(s, "m6 vault + sweep: forward") and has(s, "M6: kicked 2 enemies for 12.0 each"), "X: m6 report %s" % s)
    tick(A, ground=True, dt=600)
    settle(A)

    # ================= R1: a probe hit never kills (capped at Health - 1, none at <= 1 / no Health); the re-dealt fall is not capped
    hi_ = int(DST.getHealth())
    hp0 = float(Cmds.hpOf(st, M1_["ref"]))
    K.check(hp0 > 12.0, "R1: the stand-in mobs start with more Health than any probe hit (%s) - the earlier amounts are uncapped" % hp0)
    msm = comps.get(M1_["ref"]).get(ESM.getComponentType())
    msm.setStatValue(JInt(hi_), JFloat(5.0))
    dmgs()
    ok_ = bool(Cmds.hit(cb, M1_["ref"], A["ref"], 12.0, False))
    dd = dmgs()
    K.check(ok_ and len(dd) == 1 and near(dd[0][1].getAmount(), 4.0, 1e-5) and dd[0][1].getCause() == DCS.PHYSICAL,
            "R1: a 12 hit on a 5-Health mob is capped to 4 (Health - 1): %s" % [float(x[1].getAmount()) for x in dd])
    msm.setStatValue(JInt(hi_), JFloat(1.0))
    K.check(not bool(Cmds.hit(cb, M1_["ref"], A["ref"], 12.0, False)) and dmgs() == [], "R1: a mob at 1 Health is not hit at all")
    K.check(not bool(Cmds.hit(cb, MNOST["ref"], A["ref"], 3.0, False)) and dmgs() == [] and near(Cmds.hpOf(st, MNOST["ref"]), -1.0),
            "R1: no readable Health -> no probe hit")
    A["sm"].setStatValue(JInt(hi_), JFloat(3.0))
    K.check(bool(Cmds.hit(cb, A["ref"], A["ref"], 9.0, True)) and near(dmgs()[0][1].getAmount(), 9.0, 1e-5),
            "R1: the re-dealt held FALL is not capped (vanilla fall semantics)")
    A["sm"].setStatValue(JInt(hi_), JFloat(float(hp0)))
    msm.setStatValue(JInt(hi_), JFloat(float(hp0)))
    Cmds.MINE.clear()

    # ================= m7 rising strike: cone + knock-up, hang, fling, crouch plunge, slam, M11
    A["tc"].getPosition().set(0.0, 64.0, 0.0)
    for m_ in (M1_, M2_):
        place(m_, 1.5 if m_ is M1_ else 2.5, 0.2 if m_ is M1_ else -0.3)
    MSIDE = mkmob(0.0, 64.0, 0.0)
    place(MSIDE, 1.5, 1.4)
    for m_ in (M1_, M2_, MBACK, MSIDE):
        sets(m_["v"])
    dmgs()
    xp[0] = 500
    Cmds.run(A["ref"], st, A["pr"], "m7", None)
    K.check(said() == ["M7 armed: face 1-3 mobs within 3 blocks. Crouch near the top = plunge (M8 / M10 / M11)."], "X: m7 armed")
    tick(A, ground=True)
    s = said()
    ku = math.sqrt(2 * G * 5.0)
    dd = dmgs()
    K.check(has(s, "M7 Rising Strike: vy 19.6, 2 enemies in the cone hit for 7.2 and knocked up at 17.9 b/s."), "X: m7 cone line %s" % s)
    K.check(sorted(str(h[0].getIndex()) for h in dd) == sorted([str(M1_["ref"].getIndex()), str(M2_["ref"].getIndex())])
            and all(near(h[1].getAmount(), 7.2, 1e-5) and h[1].getCause() == DCS.PHYSICAL for h in dd), "X: m7: only the cone's 2 live mobs hit for 1.2 x 6")
    K.check(sets(M1_["v"]) == [(0.0, ku, 0.0, True, "Set")] and sets(MSIDE["v"]) == [] and sets(MBACK["v"]) == [], "X: m7: the cone's mobs knocked up 17.89 b/s (dash config); side / behind untouched")
    tick(A, ground=False, vy=15.0, y=66.0)
    tick(A, ground=False, vy=0.3, y=70.0)                     # the top
    s = said()
    K.check(has(s, "M7: the top - HANG 1200 ms (you and 2 enemies held). Crouch now to plunge."), "X: m7 top -> hang %s" % s)
    sets(A["v"])
    sets(M1_["v"])
    M1_["tc"].getPosition().set(JDouble(M1_["tc"].getPosition().x()), JDouble(69.0), JDouble(M1_["tc"].getPosition().z()))
    tick(A, ground=False, vy=-1.0, y=70.0, dt=100)
    K.check(len(sets(A["v"])) == 1 and sets(M1_["v"]) == [(0.0, -1.0, 0.0, True, "Set")], "X: m7 hang: you and the mobs SET to -1 b/s every tick")
    hit_event(M1_["ref"], A["ref"], 5.0)
    s = said()
    fl = sets(M1_["v"])
    K.check(has(s, "M7: air hit - that enemy is FLUNG 12.0 b/s") and len(fl) == 1 and near(fl[0][0], LX * 12.0) and near(fl[0][1], 2.0) and fl[0][3],
            "X: m7: your hit on a held mob flings it along your look %s %s" % (s, fl))
    hit_event(M1_["ref"], A["ref"], 5.0)
    K.check(not has(said(), "FLUNG"), "X: m7: a flung mob is released (no second fling)")
    tick(A, ground=False, crouch=True, vy=-1.0, y=70.0)
    s = said()
    K.check(has(s, "M10: crouch near the top seen (") and has(s, "ms into the hang) - PLUNGE at 14.0 b/s."), "X: m7: crouch in the hang = PLUNGE %s" % s)
    sets(A["v"])
    sets(M2_["v"])
    tick(A, ground=False, crouch=False, vy=-14.0, y=66.0)
    K.check(sets(A["v"]) == [(0.0, -14.0, 0.0, False, "Set")] and sets(M2_["v"]) == [(0.0, -14.0, 0.0, True, "Set")], "X: m8: you + the held mob dragged down at 14 b/s")
    d = fall_event(A, 9.0)
    K.check(bool(d.isCancelled()) and has(said(), "M8: plunge slam FALL damage 9.0 CANCELLED."), "X: m8: the plunge's FALL damage is cancelled")
    M2_["tc"].getPosition().set(JDouble(M2_["tc"].getPosition().x()), JDouble(64.5), JDouble(M2_["tc"].getPosition().z()))
    dmgs()
    tick(A, ground=True, vy=0.0, y=64.0)
    s = said()
    dd = dmgs()
    K.check(has(s, "M8 PLUNGE landed: slam hit ") and has(s, "1/1 knocked-up enemies came down with you; rolling at landing no"),
            "X: m8 landing line %s" % s)
    K.check(len(dd) >= 2 and all(near(h[1].getAmount(), 6.0) for h in dd), "X: m8: the slam hits every enemy within 3 blocks for 1.0 x hit (%d)" % len(dd))
    tick(A, ground=True, dt=2600)
    K.check(has(said(), "M11: Acrobatics XP 500 -> 500 (PASS: no XP for the plunge)."), "X: M11 PASS when the XP did not change")
    # again: crouch while still rising near the top; XP paid -> FAIL line; the slam with nobody near
    settle(A)
    A["tc"].getPosition().set(30.0, 64.0, 30.0)
    Cmds.run(A["ref"], st, A["pr"], "m7", "10")
    said()
    tick(A, ground=True)
    s = said()
    K.check(has(s, "0 enemies in the cone hit for 12.0"), "X: m7 10 with no mob in front %s" % s)
    tick(A, ground=False, vy=12.0, y=67.0)
    xp[0] = 530
    tick(A, ground=False, crouch=True, vy=2.0, y=69.0)
    K.check(has(said(), "M10: crouch near the top seen (still rising, client vy 2.0) - PLUNGE"), "X: m10: crouch while still rising slowly = plunge")
    tick(A, ground=False, crouch=False, vy=-14.0, y=66.0)
    tick(A, ground=True, vy=0.0, y=64.0, rolling=True)
    s = said()
    K.check(has(s, "slam hit 0 enemies") and has(s, "rolling at landing YES (SkyySkills may pay roll XP!)"), "X: m8 landing while rolling %s" % s)
    xp[0] = 560
    tick(A, ground=True, rolling=False, dt=2600)
    K.check(has(said(), "M11: Acrobatics XP 530 -> 560 (FAIL: +30 XP was paid)."), "X: M11 FAIL line when XP was paid")
    # no bridge -> the /skills hint
    bridge.remove("skill:fn:xp")
    settle(A)
    Cmds.run(A["ref"], st, A["pr"], "m8", None)
    said()
    tick(A, ground=True)
    tick(A, ground=False, vy=12.0, y=67.0)
    tick(A, ground=False, vy=0.2, y=70.0)
    tick(A, ground=False, crouch=True, vy=-1.0, y=70.0)
    tick(A, ground=False, crouch=False, vy=-14.0, y=66.0)
    tick(A, ground=True, vy=0.0, y=64.0)
    tick(A, ground=True, dt=2600)
    K.check(has(said(), "M11: SkyySkills skill:fn:xp not found"), "X: M11 without SkyySkills -> the /skills hint")
    Cmds.run(A["ref"], st, A["pr"], "xp", None)
    K.check(said() == ["Acrobatics XP now: -1 (-1 = SkyySkills not found). M11 itself runs inside m7: crouch at the top."], "X: /mprobe xp")
    bridge.put("skill:fn:xp", XpFn())
    # hang over without a crouch -> flowing fall -> landing; a time-out while plunging
    settle(A)
    Cmds.run(A["ref"], st, A["pr"], "m7", None)
    said()
    tick(A, ground=True)
    tick(A, ground=False, vy=12.0, y=67.0)
    tick(A, ground=False, vy=0.2, y=70.0)
    tick(A, ground=False, vy=-1.0, y=70.0, dt=1300)
    s = said()
    K.check(has(s, "M7: hang over - mobs stayed between y ") and has(s, "No plunge: flowing fall (15% slower, 15% less fall damage)."), "X: m7 hang over %s" % s)
    tick(A, ground=False, vy=-5.0, y=68.0)
    K.check(len(sets(A["v"])) >= 1, "X: m7: the flowing fall runs after the hang")
    tick(A, ground=True, vy=0.0, y=64.0)
    K.check(has(said(), "M7: landed after the flowing fall"), "X: m7 landing after the flowing fall")
    settle(A)
    Cmds.run(A["ref"], st, A["pr"], "m7", None)
    said()
    tick(A, ground=True)
    tick(A, ground=False, vy=12.0, y=67.0, dt=1600)            # never seen the top in 1.5 s -> hang anyway
    K.check(has(said(), "M7: the top - HANG"), "X: m7: the hang starts after 1.5 s even without a seen top")
    tick(A, ground=False, crouch=True, vy=-1.0, y=70.0)
    tick(A, ground=False, crouch=False, vy=-14.0, y=66.0, dt=6100)
    K.check(has(said(), "M8: no landing within 6 s - stopped."), "X: m8 time-out")
    settle(A)
    S().rs = 0

    # ================= m12 aura + combo
    hit_event(M1_["ref"], A["ref"], 4.0)                       # no aura yet: not counted
    Cmds.run(A["ref"], st, A["pr"], "m12", "10")
    K.check(said() == ["M12 armed for 10 s: fight mobs with the Bo staff - every landed hit = 1 combo (5 s each, max 20)."], "X: m12 armed")
    A["tc"].getPosition().set(0.0, 64.0, 0.0)
    place(M1_, 1.5, 0.2)
    place(M2_, 2.5, -0.3)
    tick(A, ground=True)
    s = said()
    K.check(has(s, "M12 aura: 4 enemies within 5.0 blocks (scan "), "X: m12: the first scan counts the live enemies within 5 blocks %s" % s)
    for i in range(3):
        hit_event(M1_["ref"], A["ref"], 4.0)
    hit_event(M1_["ref"], A["ref"], 4.0, cancelled=True)       # a blocked hit is no combo
    hit_event(M1_["ref"], A["ref"], 0.0)
    hit_event(A["ref"], M1_["ref"], 4.0)                       # a mob hitting you is no combo
    hit_event(M1_["ref"], STRANGER["ref"], 4.0)                # someone else's hit
    tick(A, ground=True)
    K.check(has(said(), "M12 combo 3"), "X: m12: 3 landed hits = combo 3 (blocked / zero / other attackers ignored)")
    tick(A, ground=True, dt=5100)
    K.check(has(said(), "M12 combo 0"), "X: m12: the stacks decay after 5 s")
    tick(A, ground=True, dt=5000)
    s = said()
    K.check(any(x.startswith("M12 over: ") and "3 hits counted" in x for x in s), "X: m12 over line %s" % s)
    ch = U.allocateInstance(MCH.class_)
    ch.boom = True
    HITS.handle(JInt(0), ch, st, cb, DMG(DENT(A["ref"]), DCS.PHYSICAL, JFloat(3.0)))
    K.check(bool(HitSys.FAILED_ONCE), "X: a broken hit hook is caught and logged once")

    # ================= costs refuse the vault / the rise; an unreadable look refuses every push
    settle(A)
    A["sm"].setStatValue(JInt(si), JFloat(2.0))
    S().costs = True
    Cmds.run(A["ref"], st, A["pr"], "m5", "vault")
    said()
    tick(A, ground=True)
    s = said()
    K.check(has(s, "M9: not enough for the vault (7.0 Stamina + 3.0 Mana) - refused.") and sets(A["v"]) == [], "X: m9: too little Stamina refuses the vault %s" % s)
    Cmds.run(A["ref"], st, A["pr"], "m7", None)
    said()
    tick(A, ground=True)
    s = said()
    K.check(has(s, "M9: not enough for the rise (8.0 Stamina + 4.0 Mana) - refused.") and sets(A["v"]) == [] and int(S().rs) == 0,
            "X: m9: too little Stamina refuses the rising strike %s" % s)
    S().costs = False
    A["sm"].setStatValue(JInt(si), JFloat(10.0))
    hrt = HR.getComponentType()
    hr_ = comps.get(A["ref"]).remove(hrt)
    Cmds.run(A["ref"], st, A["pr"], "m5", "lunge")
    said()
    tick(A, ground=True)
    K.check(has(said(), "Push: your look direction is unreadable - nothing done.") and sets(A["v"]) == [], "X: a push with no readable look does nothing")
    comps.get(A["ref"]).put(hrt, hr_)
    settle(A)

    # ================= R5: the m4 window prints when it is over
    Cmds.run(A["ref"], st, A["pr"], "m4", "85")
    said()
    tick(A, ground=True, dt=30100)
    K.check(has(said(), "M4: the 30 s are over - retype /mprobe m4 to test again.") and int(S().fallUntil) == 0, "R5: m4 time-out line")
    # ================= R3: stop with a held FALL settles it first (re-dealt after the window), then clears
    settle(A)
    Cmds.run(A["ref"], st, A["pr"], "m2", None)
    said()
    tick(A, ground=False, vy=-15.0, y=68.0)
    fall_event(A, 8.0)
    tick(A, ground=True, vy=0.0, y=64.0)
    said()
    dmgs()
    Cmds.run(A["ref"], st, A["pr"], "stop", None)
    s = said()
    q_ = S()
    K.check(s == ["Probes stopped; the held FALL damage 8.0 is settled first (state cleared in a moment)."] and q_ is not None and bool(q_.quit)
            and not bool(q_.chain) and near(q_.pendFall, 8.0), "R3: stop with a held fall keeps only that fall %s" % s)
    tick(A, ground=True, dt=30)
    K.check(S() is not None and dmgs() == [], "R3: inside the window nothing is dealt yet")
    tick(A, ground=True, dt=200)
    s = said()
    dd = dmgs()
    K.check(has(s, "Missed landing: the held FALL damage re-dealt at 85% = 6.8") and has(s, "Probe state cleared (the held FALL damage is settled).")
            and len(dd) == 1 and dd[0][1].getCause() == DCS.FALL and near(dd[0][1].getAmount(), 6.8, 1e-4) and S() is None,
            "R3: after the window the held fall is re-dealt at 85%%, then the state is gone %s" % s)
    Cmds.MINE.clear()
    # R3b: a stop right after a timed bound -> forgiven, then cleared; a probe command after stop keeps the state
    settle(A)
    Cmds.run(A["ref"], st, A["pr"], "m2", None)
    said()
    tick(A, ground=False, vy=-15.0, y=68.0)
    fall_event(A, 8.0)
    tick(A, ground=True, vy=0.0, y=64.0)
    tick(A, ground=False, jump=True, vy=11.0, y=64.3, dt=40)
    s0 = said()
    # the bound tick already forgave it; force a pending one whose bound came in the window to test the copy of lastBoundAt
    S().pendFall = 4.0
    S().pendFallAt = S().lastBoundAt
    Cmds.run(A["ref"], st, A["pr"], "stop", None)
    said()
    tick(A, ground=False, jump=False, vy=8.0, y=65.0)
    s = said()
    K.check(has(s0, "FORGIVEN") and has(s, "Timed landing: the held FALL damage 4.0 is FORGIVEN.") and has(s, "Probe state cleared (the held FALL")
            and S() is None and dmgs() == [], "R3: a stop after a timed bound forgives the held fall, then clears %s" % s)
    settle(A)
    Cmds.run(A["ref"], st, A["pr"], "m2", None)
    tick(A, ground=False, vy=-15.0, y=68.0)
    fall_event(A, 8.0)
    tick(A, ground=True, vy=0.0, y=64.0)
    Cmds.run(A["ref"], st, A["pr"], "stop", None)
    Cmds.run(A["ref"], st, A["pr"], "m9", "off")
    said()
    tick(A, ground=True, dt=200)
    K.check(S() is not None and not bool(S().quit) and has(said(), "re-dealt at 85%"), "R3: a new probe after stop keeps the state (the held fall still settled)")
    dmgs()
    Cmds.MINE.clear()
    # ================= R4: a relog (the state's player ref no longer valid) drops the old state instead of re-arming it
    settle(A)
    Cmds.run(A["ref"], st, A["pr"], "m2", None)
    said()
    oldref = mkref()
    S().ref = oldref
    tick(A, ground=True)
    K.check(S() is not None and bool(S().chain), "R4: a different but still valid ref keeps the state (no false drop)")
    jfield(REF, "index").set(oldref, JInt(-2147483648))
    K.check(not bool(oldref.isValid()), "R4: the old ref is invalid now")
    tick(A, ground=True)
    K.check(S() is None and said() == [], "R4: a tick with the old ref invalid (relog) drops the stale state")
    settle(A)
    Cmds.run(A["ref"], st, A["pr"], "m9", "off")
    said()

    # ================= stats / stop / aliases
    Cmds.run(A["ref"], st, A["pr"], "stats", None)
    s = said()
    K.check(len(s) == 1 and s[0].startswith("Stats: ") and " velocity Sets; " in s[0] and " bounds; costs off." in s[0], "X: stats %s" % s)
    Cmds.run(A["ref"], st, A["pr"], "M10", None)
    K.check(said()[0].startswith("M3 armed for 30 s"), "X: m10 = the m3 alias (case-insensitive)")
    Cmds.run(A["ref"], st, A["pr"], "m11", None)
    K.check(said()[0].startswith("Acrobatics XP now: 560"), "X: m11 = the xp line")
    Cmds.run(A["ref"], st, A["pr"], "stop", None)
    K.check(said() == ["Probe state cleared."] and Cmds.STATES.get(A["uuid"]) is None, "X: stop clears the state")

    # ================= the commands through reflection with a real CommandContext
    CTXc = JClass("com.hypixel.hytale.server.core.command.system.CommandContext")
    WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
    STc = JClass("com.hypixel.hytale.component.Store")
    cmd, cmd1, cmd2 = JClass(PKG + "MProbeCmd")(), JClass(PKG + "MProbeArgCmd")(), JClass(PKG + "MProbeArg2Cmd")()

    def execute(c, ctx, p):
        m_ = c.getClass().getDeclaredMethod("execute", CTXc.class_, STc.class_, REF.class_, PRc.class_, WLD.class_)
        m_.setAccessible(True)
        m_.invoke(c, JArray(JObject)([ctx, st, p["ref"], p["pr"], None]))
    execute(cmd, None, A)
    K.check(len(said()) == 3, "X: /mprobe -> the help lines")
    ctx = U.allocateInstance(CTXc.class_)
    av = JClass("java.util.HashMap")()
    av.put(cmd1.whatArg, "m9")
    jfield(CTXc, "argValues").set(ctx, av)
    execute(cmd1, ctx, A)
    K.check(said()[0].startswith("M9 costs ON"), "X: /mprobe m9 through MProbeArgCmd.execute + CommandContext.get")
    av2 = JClass("java.util.HashMap")()
    av2.put(cmd2.whatArg, "m4")
    av2.put(cmd2.valArg, "85")
    ctx2 = U.allocateInstance(CTXc.class_)
    jfield(CTXc, "argValues").set(ctx2, av2)
    execute(cmd2, ctx2, A)
    K.check(said() == ["M4 armed for 30 s: your FALL damage x 85.0% - jump off a 6+ block drop."], "X: /mprobe m4 85 through MProbeArg2Cmd.execute")
    execute(cmd1, None, A)
    execute(cmd2, None, A)
    K.check(said() == ["Usage: /mprobe <kit, m1 .. m13, xp, stats, stop>", "Usage: /mprobe <probe> <value>"], "X: both variants without a context -> usage")

    # ================= plugin shutdown clears the state; MINE overflow guard
    for i in range(4100):
        Cmds.MINE.put(JClass("java.lang.Object")(), JClass("java.lang.Boolean").TRUE)
    Cmds.hit(cb, M1_["ref"], A["ref"], 1.0, False)
    K.check(Cmds.MINE.size() == 1, "X: MINE is cleared before it passes 4096 entries")
    K.check(not bool(Cmds.hit(cb, M1_["ref"], A["ref"], 0.0, False)) and not bool(Cmds.hit(cb, None, A["ref"], 1.0, False)), "X: hit refuses 0 / no target")
    PLc = JClass(PKG + "SkyyMonkProbePlugin")
    plg = U.allocateInstance(PLc.class_)
    try:
        sd = PLc.class_.getDeclaredMethod("shutdown")
        sd.setAccessible(True)
        sd.invoke(plg, JArray(JObject)([]))
    except Exception as e:
        K.notes.append("plugin shutdown: super.shutdown() on an allocated plugin: %s" % str(e)[:120])
    K.check(Cmds.STATES.isEmpty() and Cmds.MINE.isEmpty(), "X: plugin shutdown clears the probe state + MINE")
    Log.SINK = None
    Cmds.CLOCK = JLong(0)
    print("X. every probe path executed")


def run_perm(out):
    """child P: permissions with the engine's own AbstractCommand code"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fld = AC.class_.getDeclaredField("permissionGroups")
    fld.setAccessible(True)
    for cn in ("MProbeCmd", "MProbeArgCmd", "MProbeArg2Cmd"):
        try:
            c = JClass(PKG + cn)()
        except Exception as e:
            K.check(False, "P. construct %s: %s" % (cn, e))
            continue
        perm = c.getPermission()
        groups = fld.get(c)
        K.check(perm is not None and NODE in str(perm.getId() if hasattr(perm, "getId") else perm), "P. %s requires %s (%s)" % (cn, NODE, perm))
        K.check(groups is not None and len(groups) == 0, "P. %s permission groups empty (%s)" % (cn, groups))
        if cn == "MProbeCmd":
            rec = c.getPermissionGroupsRecursive()
            leak = [str(k) for k in rec.keySet() if rec.get(k) is not None and any(NODE in str(x) for x in rec.get(k))]
            K.check(not leak, "P. getPermissionGroupsRecursive gives %s to no group (leak: %s)" % (NODE, leak))
            K.check("monkprobe" in [str(a) for a in c.getAliases()] and str(c.getName()) == "mprobe", "P. /mprobe + alias /monkprobe")
    K.save()


def bytecode_calls(cp, cls, meth):
    from jpype import JClass
    cc = cp.get(cls)
    mi = [m for m in cc.getClassFile2().getMethods() if str(m.getName()) == meth][0]
    cpool, it = mi.getConstPool(), mi.getCodeAttribute().iterator()
    calls = []
    while it.hasNext():
        p = it.next()
        op = it.byteAt(p)
        if op in (0xb6, 0xb7, 0xb8, 0xb9):
            i = it.u16bitAt(p + 1)
            tag = cpool.getTag(i)
            if tag == JClass("javassist.bytecode.ConstPool").CONST_InterfaceMethodref:
                calls.append(str(cpool.getInterfaceMethodrefClassName(i)).rsplit(".", 1)[-1] + "." + str(cpool.getInterfaceMethodrefName(i)))
            else:
                calls.append(str(cpool.getMethodrefClassName(i)).rsplit(".", 1)[-1] + "." + str(cpool.getMethodrefName(i)))
        elif op == 0xbb:
            calls.append("new " + str(cpool.getClassInfo(it.u16bitAt(p + 1))).rsplit(".", 1)[-1])
        elif op in (0xb2, 0xb3):
            calls.append(("get " if op == 0xb2 else "put ") + str(cpool.getFieldrefClassName(it.u16bitAt(p + 1))).rsplit(".", 1)[-1] + "."
                         + str(cpool.getFieldrefName(it.u16bitAt(p + 1))))
    return calls


def run_bytecode(out):
    """child: setup()'s calls in their order + the engine facts read from HytaleServer.jar bytecode (javassist)"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    calls = bytecode_calls(cp, PKG + "SkyyMonkProbePlugin", "setup")
    want = ["PluginBase.getLogger", "put MpLog.LOG", "PluginBase.getCommandRegistry", "new MProbeCmd", "MProbeCmd.<init>",
            "CommandRegistry.registerCommand", "PluginBase.getEntityStoreRegistry", "new MpTick", "MpTick.<init>",
            "ComponentRegistryProxy.registerSystem", "PluginBase.getEntityStoreRegistry", "new MpFallSys", "MpFallSys.<init>",
            "ComponentRegistryProxy.registerSystem", "PluginBase.getEntityStoreRegistry", "new MpHitSys", "MpHitSys.<init>",
            "ComponentRegistryProxy.registerSystem"]
    pos, ok = 0, True
    for w in want:
        try:
            pos = calls.index(w, pos) + 1
        except ValueError:
            ok = False
            break
    K.check(ok and calls.count("ComponentRegistryProxy.registerSystem") == 3, "X: setup() = LOG, registerCommand(/mprobe), registerSystem once each for "
                                                                             "MpTick / MpFallSys / MpHitSys: %s" % calls)
    # E: the vanilla fall damage shape we copy + its order before the input
    fdp = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$FallDamagePlayers"
    tk = [m for m in cp.get(fdp).getDeclaredMethods() if str(m.getName()) == "tick" and "ArchetypeChunk" in str(m.getSignature())]
    c2 = bytecode_calls(cp, fdp, "tick") if tk else []
    # the 5-arg tick is the second 'tick' - scan every tick method's calls instead
    allc = []
    for m in cp.get(fdp).getClassFile2().getMethods():
        if str(m.getName()) == "tick":
            it = m.getCodeAttribute().iterator()
            cpool = m.getConstPool()
            while it.hasNext():
                p = it.next()
                if it.byteAt(p) == 0xb2:
                    allc.append(str(cpool.getFieldrefClassName(it.u16bitAt(p + 1))).rsplit(".", 1)[-1] + "." + str(cpool.getFieldrefName(it.u16bitAt(p + 1))))
    K.check("Damage.NULL_SOURCE" in allc and "DamageCause.FALL" in allc,
            "E: vanilla FallDamagePlayers builds new Damage(Damage.NULL_SOURCE, DamageCause.FALL, ..) - the re-dealt held fall's shape")
    IP = JClass("javassist.bytecode.InstructionPrinter")
    ci = cp.get(fdp).getClassInitializer()
    lines = []
    if ci is not None:
        it, cpool = ci.getMethodInfo().getCodeAttribute().iterator(), ci.getMethodInfo().getConstPool()
        while it.hasNext():
            lines.append(str(IP.instructionString(it, it.next(), cpool)))
    K.check(any("Order.BEFORE" in x for x in lines) and any("PlayerSystems$ProcessPlayerInput" in x for x in lines),
            "E: FallDamagePlayers runs BEFORE ProcessPlayerInput (a landing's FALL damage comes before a jump pressed after it - why the chain HOLDS it)")
    fx = [str(f.getName()) for c in ("com.hypixel.hytale.protocol.ApplicationEffects", "com.hypixel.hytale.protocol.MovementEffects")
          for f in cp.get(c).getDeclaredFields()]
    K.check(not [f for f in fx if "ravity" in f or "fall" in f.lower()], "E: no gravity / slow-fall field in the effect protocol (M1 = per-tick Sets): %s" % fx[:6])
    ex = []
    for m in cp.get("com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems").getDeclaredMethods():
        if str(m.getName()) == "executeDamage" and "CommandBuffer;L" in str(m.getSignature()) and str(m.getSignature()).startswith("(Lcom/hypixel/hytale/component/Ref;"):
            it, cpool = m.getMethodInfo().getCodeAttribute().iterator(), m.getMethodInfo().getConstPool()
            while it.hasNext():
                p = it.next()
                if it.byteAt(p) == 0xb6:
                    ex.append(str(cpool.getMethodrefClassName(it.u16bitAt(p + 1))).rsplit(".", 1)[-1] + "." + str(cpool.getMethodrefName(it.u16bitAt(p + 1))))
    K.check("CommandBuffer.invoke" in ex, "E: DamageSystems.executeDamage(ref, CommandBuffer, damage) = CommandBuffer.invoke (what MapBuffer records)")
    K.save()


def run_live(step, out):
    """child D: one 'server start' on the scratch copy of the live player files"""
    from jpype import JClass, JFloat, JInt
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR, FAKE_DIR])
    E = engine_setup(K)
    W = world(K, E)
    home = os.path.join(SCRATCH, "live")
    before = dict((f, hashlib.sha256(open(os.path.join(home, f), "rb").read()).hexdigest()) for f in sorted(os.listdir(home)))
    Cmds, Log = JClass(PKG + "MpCmds"), JClass(PKG + "MpLog")
    K.check(Cmds.STATES.isEmpty() and Cmds.MINE.isEmpty() and int(Cmds.CLOCK) == 0, "D %s: the probe starts with no state (nothing carried over)" % step)
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    BD, EEI = JClass("org.bson.BsonDocument"), JClass("com.hypixel.hytale.codec.EmptyExtraInfo")
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    REF = JClass("com.hypixel.hytale.component.Ref")
    IHM = JClass("java.util.IdentityHashMap")
    n = 0
    for f in sorted(before):
        d = json.load(open(os.path.join(home, f), encoding="utf-8"))
        es = d.get("Components", {}).get("EntityStats")
        if es is None:
            continue
        try:
            m = ESM.CODEC.decode(BD.parse(json.dumps(es)), EEI.EMPTY)
            m.update()
        except Exception as e:
            K.check(False, "D %s %s: EntityStatMap.CODEC decode: %s" % (step, f, str(e)[:200]))
            continue
        r_ = REF(W["st"], JInt(10 + n))
        W["comps"].put(r_, IHM())
        W["comps"].get(r_).put(ESM.getComponentType(), m)
        sv = m.get(int(DST.getStamina()))
        txt = str(Cmds.statText(W["st"], r_))
        K.check(txt.startswith("Stamina ") and ", Mana " in txt, "D %s %s: statText on the real saved stats: %s" % (step, f, txt))
        if sv is not None:
            sv0 = float(sv.get())
            got = int(Cmds.take(W["st"], r_, 1.0, 1.0))
            K.check((got == 1 and abs(float(sv.get()) - (sv0 - 1.0)) < 1e-4) or (got == 0 and sv0 < 1.0),
                    "D %s %s: a probe cost on the real saved stats (Stamina %.1f -> %.1f)" % (step, f, sv0, float(sv.get())))
        n += 1
    K.notes.append("D %s: %d live player copies used" % (step, n))
    after = dict((f, hashlib.sha256(open(os.path.join(home, f), "rb").read()).hexdigest()) for f in sorted(os.listdir(home)))
    K.check(before == after, "D %s: the probe wrote nothing - every scratch file byte-identical, no new file" % step)
    K.save(files=len(after), used=n)


def run_audit(out):
    """child AA: the engine-access audit (the SkyyReelProbe / SkyyClasses harness part AA)"""
    from jpype import JClass
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=False)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    for p_ in (B.SERVER_JAR, JAR, FAKE_DIR):
        CP.appendClassPath(p_)
    LIN, MTc, CPool, JMod_ = (JClass(FAKE_PKG + ".LookupIn"), JClass("java.lang.invoke.MethodType"), JClass("javassist.bytecode.ConstPool"),
                              JClass("java.lang.reflect.Modifier"))
    XOPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
            0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
            0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}

    def jvm_class(name):
        return Cls.forName(name.replace("/", "."), False, loader)
    cs_ = set()

    def lookup_audit(cn):
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
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn
                                    or (not JMod_.isPrivate(md) and str(C_.getPackageName()) == str(D.getPackageName()))):
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
                    if "caller-sensitive" in str(ex_) and op in (0xb6, 0xb8, 0xb9) and C_ is not None:
                        try:
                            mm_ = C_.getMethod(name, mt.parameterArray())
                            ok_ = JMod_.isPublic(int(C_.getModifiers())) and JMod_.isPublic(int(mm_.getModifiers()))
                            if ok_:
                                cs_.add("%s.%s" % (str(C_.getName()), name))
                        except Exception:
                            ok_ = False
                    if not ok_:
                        refused.append("%s: %s" % (where, ex_))
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
    res["control"] = lookup_audit(FAKE_PKG + ".BadAccess")[0]
    res["caller_sensitive"] = sorted(cs_)
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
    if "--mkfake" in sys.argv:
        run_mkfake(arg("--mkfake"))
        return
    if "--engine" in sys.argv:
        run_engine(arg("--out"))
        return
    if "--live-step" in sys.argv:
        run_live(arg("--live-step"), arg("--out"))
        return
    if "--perm" in sys.argv:
        run_perm(arg("--out"))
        return
    if "--bytecode" in sys.argv:
        run_bytecode(arg("--out"))
        return
    if "--audit" in sys.argv:
        run_audit(arg("--out"))
        return
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        part_static()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0 and os.path.isfile(os.path.join(FAKE_DIR, FAKE_PKG, "MapStore.class")), "F: the stand-ins were generated")
        out = os.path.join(SCRATCH, "engine.json")
        child(env, "--engine", "x", "--out", out)
        take(out, "engine")
        # D: start twice on a scratch copy of the live player files
        home = os.path.join(SCRATCH, "live")
        os.makedirs(home, exist_ok=True)
        n = 0
        if os.path.isdir(LIVE):
            for f in sorted(os.listdir(LIVE)):
                if f.endswith(".json"):
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
        for label, flag in (("perm", "--perm"), ("bytecode", "--bytecode")):
            out = os.path.join(SCRATCH, "%s.json" % label)
            child(env, flag, "--out", out)
            take(out, label)
        outa = os.path.join(SCRATCH, "audit.json")
        pa = child(env, "--audit", "--out", outa)
        check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            check(not a["refused"] and a["refs"] > 300 and a["classes"] == len(CLASSES),
                  "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: control refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, %d refused, control refused; caller-sensitive: %s"
                  % (a["refs"], a["classes"], len(a["refused"]), a["caller_sensitive"]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d ok, %d fail(s)" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAILED:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
