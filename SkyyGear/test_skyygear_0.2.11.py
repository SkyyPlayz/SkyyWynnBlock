"""Harness for SkyyGear 0.2.11 (THE LOOT ROUND - mystery bags picked at identify, re-identify, drop-only vanilla gear in the bag pool, 6 %
extra mob bags, the extra bag in fresh loot chests, gear:fn:box; Skyy LOCKED docs/answered/gear.md 2026-10-08 "yes to all").
Build first: python tools/gear_0_2_11_patch.py && python SkyyGear/build_skyygear_0.2.11.py

    python SkyyGear/test_skyygear_0.2.11.py [--jar <SkyyGear-0.2.11.jar>] [--dir <scratch>] [--keep] [--skip-carried]

  R  THE CARRIED HARNESS: SkyyGear/test_skyygear_0.2.10.py (itself every 0.1 ... 0.2.10 section) runs on the 0.2.11 jar with VERSION 0.2.11;
     the checks that MUST read differently are listed in DEVIATIONS211 with the reason (bags instead of 0.2-style tags in fresh / first-open
     chests, the fresh file ending with the loot block, the 0.2.9 -> 0.2.10 compare); any other failure fails the run. It carries the
     live-data start-twice section (AH3) on the new jar.
  Children (fresh JVMs, the game's JRE, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch):
  F  stand-ins compiled with javassist (FakeChunk / FakeStore / FakeBuffer ECS parts, a container that refuses writes, a page that records
     rebuild / close, the audit helpers)
  A  every class of the jar loads + verifies (-Xverify:all)
  V  THE ENGINE ASSET VALIDATORS: the vanilla pack loaded store by store (every codec validator), then THE JAR as its own pack - no failed
     store, no SEVERE / WARNING; the 7 bag items + qualities in the stores, toPacket() works, MaxStack 1, the bag model / textures / icons
     resolve; NEGATIVE CONTROLS (one-entry Parallel, a missing model) are refused; no "Parallel" in the jar
  X  EVERY NEW CODE PATH EXECUTED (-Xverify:all, the REAL item store from V): GearPool (table, levels, range, pick*, lean, exclude,
     drop-only weight, typeOfId / atOfId), GearUnid (make / view / rarity odds + level boost / roll / fromItem / why / open / re-roll /
     costs / fnBox / logText), GearIdent (identify a bag: success, fingerprint, poor, no coins, refused before coins, write refused ->
     refund, free; re-identify x3 + the limit + refund; rows / rerollRows / row texts / costOf / refuse; Identify all), IdentifyPage (pick,
     detailBox, detailReroll, list, build, one, the two-click re-roll, handleDataEvent "rr"), GearTag (marks with levels, unid -> bag,
     spread, tagContainer), GearLoot (mobLevel, killer, capOk, lean, mobRoll every branch, chestLevel, chestExtra, texts), GearDeathMark.tick
     + GearDropSys.onEntityAdded + GearChestTag.onEntityAdded on stand-in ECS parts, GearBoxFn, gear:fn:* on bags, GearForge.fp, /gear box +
     /gear loot, the extra mob drop's real spawn lines by bytecode (= NPCDamageSystems$DropDeathItems)
  C  CLASS COMPARE 0.2.10 -> 0.2.11 (javassist members): exactly the listed changes + the 4 new classes + 2 sub-commands; the non-class
     entries changed = the bag assets + lang + manifest
  P  /gear box + /gear loot: skyygear.admin, no permission groups (the engine's own AbstractCommand code)
  D  START TWICE on a scratch COPY of the live Skyy_SkyyGear folder (setup()'s config order): the file is not touched (new keys = no
     one-time update), the loot rows read their defaults (no live line held the planned 4 % - nothing to migrate)
  AA THE ENGINE-ACCESS AUDIT: every class / field / method reference resolved with MethodHandles.privateLookupIn the referencing class
Scratch: tools/dev/scratch/loot01fix/gear (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.2.11"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.2.10.jar")
SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "loot01fix", "gear")))
FAKE_DIR = os.path.join(SCRATCH, "fake")
FAKE_PKG = "skyygeartest"
PKG = "com.skyy.gear."
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGear")
FAILS, OKS = [], [0]
NEW_CLASSES = ["GearBoxCmd", "GearBoxFn", "GearLoot", "GearLootCmd", "GearPool", "GearUnid"]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def _jvm(cp, verify=True, big=False):
    import jpype
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    opts = (["-Xverify:all"] if verify else []) + (["-Xmx6g"] if big else []) + ["-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED",
                                                                                 "-Djava.io.tmpdir=" + tmp]
    jpype.startJVM(jvm, *opts, classpath=list(cp), convertStrings=True)


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


def jar_classes(j):
    return sorted(n[:-6].replace("/", ".") for n in zipfile.ZipFile(j).namelist() if n.endswith(".class"))


# ====================================================================================================== R: the carried harness
DEVIATIONS211 = [
    ("AA3(a) no placer: first open -> sword, armor and the 3 spears (split per item) unidentified",
     "0.2.11: a single undocumented gear item in a first-opened world container becomes a MYSTERY BAG (LOCKED 2026-10-02 'vanilla gear drops "
     "become mystery items too'); X7 checks the bag spread / tag path"),
    ("AA3(a) no placer: every item id counted before = after", "0.2.11: the vanilla gear ids are replaced by Skyy_Unid_Bag_* ids (one bag per item - X7)"),
    ("AA3(a) a prefab builder's placer: first open -> sword, armor and the 3 spears (split per item) unidentified", "0.2.11: bags (as above)"),
    ("AA3(a) a prefab builder's placer: every item id counted before = after", "0.2.11: bags (as above)"),
    ("AA3(a): rarities follow the Chest odds column", "0.2.11: bags carry their rarity in their own document (SkyyUnid), not a gear document - X2 "
     "checks the bag rarity odds"),
    ("AG0: the fresh 0.2.6 file keeps the 0.2.5 blocks", "0.2.11: the fresh file ends with the loot block (X0 checks it)"),
    ("AK6: Server Setup -> Gear -> Combat row gear.signatureKeep", "0.2.11: the fresh file now ends with the loot block after it (X0)"),
    ("AK7: the six GearSig classes added, none removed", "0.2.11: the 0.2.9 -> 0.2.10 compare reads the 0.2.11 jar - C compares 0.2.10 -> 0.2.11"),
    ("AK7: no difference outside the listed 0.2.10 parts", "0.2.11: C compares 0.2.10 -> 0.2.11"),
    ("AK7: every listed 0.2.10 part is really in the jar", "0.2.11: C compares 0.2.10 -> 0.2.11"),
    ("AK7: non-class entries: only manifest.json changed", "0.2.11: the bag assets (C lists them)"),
    ("Z1: fresh default file: stats.chg under stats.cd, the marker + the three rows under speed.per",
     "0.2.11: carried Z1 reads the 0.1.2 layout up to the file end - the loot block follows at the end now (X0)"),
]


def run_carried():
    H210 = os.path.join(HERE, "test_skyygear_0.2.10.py")
    t = open(H210, encoding="utf-8").read()
    cut = t.rindex('_g = {"__name__": "__main__"')
    ns = {"__name__": "skyygear_h210", "__file__": H210, "__builtins__": __builtins__}
    exec(compile(t[:cut], H210 + " (the 0.2.10 harness text, not run)", "exec"), ns)
    src = ns["src"]
    dev210 = ns["DEV29"] + ns["DEVIATIONS210"]

    def sub(old, new, count=1):
        nonlocal src
        n = src.count(old)
        assert n == count, "carried harness text changed: anchor count %d (want %d): %s" % (n, count, old[:120])
        src = src.replace(old, new)
    sub('VERSION = "0.2.10"\nDEVIATIONS = %r' % (dev210,), 'VERSION = "0.2.11"\nDEVIATIONS = %r' % (dev210 + DEVIATIONS211,))
    sub('os.path.join(TOOLS, "dev", "scratch", "sigkeep01", "harness")', 'os.path.join(TOOLS, "dev", "scratch", "loot01fix", "carried")')
    sub('print("DEVIATION (0.2.5/0.2.6/0.2.7/0.2.8/0.2.9/0.2.10, expected):"', 'print("DEVIATION (0.2.5 ... 0.2.11, expected):"')
    sub('expected 0.2.5 / 0.2.6 / 0.2.7 / 0.2.8 / 0.2.9 / 0.2.10 deviations (%d listed kinds seen)',
        'expected 0.2.5 ... 0.2.11 deviations (%d listed kinds seen)')
    # the 0.2.9 -> 0.2.10 compare reads SkyyGear-0.2.9.jar vs the jar under test: its expected lists are 0.2.10's (C below compares 0.2.10 -> 0.2.11)
    # the carried parent re-runs THIS file with "--run <jar>" for its JVM child (the root harness: subprocess [python, __file__, "--run", ...]),
    # so __file__ is this harness and main() hands "--run" back to run_carried
    g = {"__name__": "__main__", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
    if "--run" not in sys.argv:
        sys.argv = [g["__file__"], "--jar", JAR, "--dir", os.path.join(TOOLS, "dev", "scratch", "loot01fix", "carried")]
    exec(compile(src, H210 + " (run as the SkyyGear 0.2.11 carried harness)", "exec"), g)


# ====================================================================================================== F: stand-ins
def run_mkfake(out_dir):
    from jpype import JClass
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    P = FAKE_PKG
    CT, CMP, RF = "com.hypixel.hytale.component.ComponentType", "com.hypixel.hytale.component.Component", "com.hypixel.hytale.component.Ref"
    fs = cp.makeClass(P + ".FakeStore")
    fs.setSuperclass(cp.get("com.hypixel.hytale.component.Store"))
    fs.addField(CtField.make("public java.util.Map comps;", fs))
    fs.addField(CtField.make("public java.lang.Object ext;", fs))
    fs.addConstructor(CtNewConstructor.make("public FakeStore() { super(null, 0, null, null); }", fs))   # never run (Unsafe)
    fs.addMethod(CtNewMethod.make("public %s getComponent(%s r, %s t) { if (this.comps == null || r == null) return null; java.util.Map m = (java.util.Map) this.comps.get(r); if (m == null) return null; return (%s) m.get(t); }" % (CMP, RF, CT, CMP), fs))
    fs.addMethod(CtNewMethod.make("public java.lang.Object getExternalData() { return this.ext; }", fs))
    fs.writeFile(out_dir)
    fb = cp.makeClass(P + ".FakeBuffer")
    fb.setSuperclass(cp.get("com.hypixel.hytale.component.CommandBuffer"))
    fb.addField(CtField.make("public %s.FakeStore st;" % P, fb))
    fb.addField(CtField.make("public java.util.ArrayList added;", fb))
    fb.addConstructor(CtNewConstructor.make("public FakeBuffer() { super(null); }", fb))                  # never run (Unsafe)
    fb.addMethod(CtNewMethod.make("public %s getComponent(%s r, %s t) { if (this.st == null) return null; return this.st.getComponent(r, t); }" % (CMP, RF, CT), fb))
    fb.addMethod(CtNewMethod.make("public java.lang.Object getExternalData() { return this.st == null ? null : this.st.ext; }", fb))
    fb.addMethod(CtNewMethod.make("public %s[] addEntities(com.hypixel.hytale.component.Holder[] hs, com.hypixel.hytale.component.AddReason why) { if (this.added == null) this.added = new java.util.ArrayList(); for (int i = 0; i < hs.length; i++) this.added.add(hs[i]); return new %s[hs.length]; }" % (RF, RF), fb))
    fb.writeFile(out_dir)
    fc = cp.makeClass(P + ".FakeChunk")
    fc.setSuperclass(cp.get("com.hypixel.hytale.component.ArchetypeChunk"))
    fc.addField(CtField.make("public java.util.Map comps;", fc))
    fc.addField(CtField.make("public %s ref;" % RF, fc))
    fc.addConstructor(CtNewConstructor.make("public FakeChunk() { super(null, null); }", fc))             # never run (Unsafe)
    fc.addMethod(CtNewMethod.make("public %s getComponent(int i, %s t) { if (this.comps == null) return null; return (%s) this.comps.get(t); }" % (CMP, CT, CMP), fc))
    fc.addMethod(CtNewMethod.make("public %s getReferenceTo(int i) { return this.ref; }" % RF, fc))
    fc.writeFile(out_dir)
    fx = cp.makeClass(P + ".FailContainer")
    fx.setSuperclass(cp.get("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"))
    fx.addField(CtField.make("public boolean refuse;", fx))
    fx.addConstructor(CtNewConstructor.make("public FailContainer(short n) { super(n); }", fx))
    fx.addMethod(CtNewMethod.make("public com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction setItemStackForSlot(short s, com.hypixel.hytale.server.core.inventory.ItemStack i) { if (this.refuse) throw new java.lang.IllegalStateException(\"test: the slot refuses\"); return super.setItemStackForSlot(s, i); }", fx))
    fx.writeFile(out_dir)
    fp = cp.makeClass(P + ".FakeIdPage")
    fp.setSuperclass(cp.get(PKG + "IdentifyPage"))
    fp.addField(CtField.make("public int rebuilds;", fp))
    fp.addField(CtField.make("public int closes;", fp))
    fp.addConstructor(CtNewConstructor.make("public FakeIdPage(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr); }", fp))
    fp.addMethod(CtNewMethod.make("public void rebuild() { this.rebuilds = this.rebuilds + 1; }", fp))
    fp.addMethod(CtNewMethod.make("public void close() { this.closes = this.closes + 1; }", fp))
    fp.writeFile(out_dir)
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
    # module singletons made in Java (a Class object of BlockModule crossing into Python makes JPype initialise its nested systems)
    fu = cp.makeClass(P + ".FakeUtil")
    fu.addMethod(CtNewMethod.make("""public static void single(String cn) throws java.lang.Exception {
  java.lang.Class c = java.lang.Class.forName(cn, false, java.lang.ClassLoader.getSystemClassLoader());
  java.lang.reflect.Field uf = java.lang.Class.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe");
  uf.setAccessible(true);
  java.lang.Object us = uf.get(null);
  java.lang.reflect.Method alloc = us.getClass().getMethod("allocateInstance", new java.lang.Class[] { java.lang.Class.class });
  java.lang.reflect.Field f = c.getDeclaredField("instance");
  f.setAccessible(true);
  java.lang.Object o = f.get(null);
  if (o == null) { o = alloc.invoke(us, new java.lang.Object[] { c }); f.set(null, o); }
  java.lang.Class ct = java.lang.Class.forName("com.hypixel.hytale.component.ComponentType");
  java.lang.Class k = c;
  while (k != null && k != java.lang.Object.class) {
    java.lang.reflect.Field[] fs = k.getDeclaredFields();
    for (int i = 0; i < fs.length; i++) {
      if (fs[i].getType() != ct || java.lang.reflect.Modifier.isStatic(fs[i].getModifiers())) continue;
      fs[i].setAccessible(true);
      if (fs[i].get(o) == null) fs[i].set(o, alloc.invoke(us, new java.lang.Object[] { ct }));
    }
    k = k.getSuperclass();
  }
}""", fu))
    fu.addMethod(CtNewMethod.make("""public static void mapType(String cn, String field, String key) throws java.lang.Exception {
  java.lang.Class c = java.lang.Class.forName(cn, false, java.lang.ClassLoader.getSystemClassLoader());
  java.lang.reflect.Field f = c.getDeclaredField("instance");
  f.setAccessible(true);
  java.lang.Object o = f.get(null);
  java.lang.reflect.Field m = c.getDeclaredField(field);
  m.setAccessible(true);
  java.util.Map mp = (java.util.Map) m.get(o);
  if (mp == null) { mp = new java.util.HashMap(); m.set(o, mp); }
  java.lang.reflect.Field uf = java.lang.Class.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe");
  uf.setAccessible(true);
  java.lang.Object us = uf.get(null);
  java.lang.reflect.Method alloc = us.getClass().getMethod("allocateInstance", new java.lang.Class[] { java.lang.Class.class });
  java.lang.Class k = java.lang.Class.forName(key, false, java.lang.ClassLoader.getSystemClassLoader());
  if (mp.get(k) == null) mp.put(k, alloc.invoke(us, new java.lang.Object[] { java.lang.Class.forName("com.hypixel.hytale.component.ComponentType") }));
}""", fu))
    fu.writeFile(out_dir)
    print("F. stand-ins written to", out_dir)


# ====================================================================================================== A: verify
def run_verify(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR], verify=True)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = jar_classes(JAR)
    for n in names:
        try:
            Cls.forName(n, True, loader)
            K.ok += 1
        except Exception as e:
            K.check(False, "A: load + verify %s: %s" % (n, str(e)[:300]))
    K.notes.append("A: %d classes loaded + initialised with -Xverify:all" % len(names))
    K.save()


# ====================================================================================================== V + X
def engine_boot(K):
    """the SkyyFishing 0.1 V child's bare server (vanilla pack store by store with every codec validator, then the jar as its own pack)"""
    from jpype import JClass, JArray, JString, JImplements, JOverride
    Options = JClass("com.hypixel.hytale.server.core.Options")
    Options.parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "v-universe")]))
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)

    def jf(c, n):
        k = c.class_ if hasattr(c, "class_") else c
        while k is not None:
            try:
                f = k.getDeclaredField(n)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(n)
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = us.allocateInstance(HS.class_)
    jf(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    jf(HS, "shutdown").set(hs, JClass("java.util.concurrent.atomic.AtomicReference")())
    jf(HS, "instance").set(None, hs)
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = us.allocateInstance(UNI.class_)
    pbu, wmap = CHM(), CHM()
    jf(UNI, "playersByUuid").set(uni, pbu)
    jf(UNI, "players").set(uni, JClass("java.util.Collections").unmodifiableCollection(pbu.values()))
    jf(UNI, "worlds").set(uni, wmap)
    jf(UNI, "worldsByUuid").set(uni, CHM())
    jf(UNI, "unmodifiableWorlds").set(uni, JClass("java.util.Collections").unmodifiableMap(wmap))
    jf(UNI, "instance").set(None, uni)
    HLB = JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend")
    CAPLOG = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    HLB.subscribe(CAPLOG)

    def records(start=0):
        out = []
        for r in list(CAPLOG)[start:]:
            try:
                msg = str(r.getMessage())
                ps = r.getParameters()
                if ps is not None and len(ps) > 0:
                    try:
                        msg = str(JClass("java.lang.String").format(msg, ps))
                    except Exception:
                        msg = msg + " " + " ".join(str(p) for p in ps)
                th = r.getThrown()
                if th is not None:
                    msg += " | " + str(th)[:300]
                out.append((str(r.getLevel()), msg))
            except Exception as e:
                out.append(("?", str(e)))
        return out
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    HAS = JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    DAMc = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
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

    @JImplements("java.util.function.Predicate")
    class IsUnknown:
        @JOverride
        def test(self, o): return bool(o.isUnknown())
    PI = "com.hypixel.hytale.server.core.modules.interaction.interaction.config."
    INTc, ROOTc = JClass(PI + "Interaction"), JClass(PI + "RootInteraction")
    UIc = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.UnarmedInteractions")
    JCLS = JClass("java.lang.Class")
    ESTc0 = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")

    def reg_ilt(c, path, codec, unknown=False, after=(), before=()):
        b_ = HAS.builder(c.class_, ILT(ArrOf(c))).setPath(path).setCodec(codec).setKeyFunction(GetId()).setReplaceOnRemove(NoRep())
        if unknown:
            b_ = b_.setIsUnknown(IsUnknown())
        if after:
            b_ = b_.loadsAfter(JArray(JCLS)([JClass(a).class_ for a in after]))
        if before:
            b_ = b_.loadsBefore(JArray(JCLS)([JClass(a).class_ for a in before]))
        AR.register(b_.build())
        for a in before:
            st_ = AR.getAssetStore(JClass(a).class_)
            if st_ is not None:
                st_.injectLoadsAfter(c.class_)
    if AR.getAssetStore(ESTc0.class_) is None:
        reg_ilt(ESTc0, "Entity/Stats", ESTc0.CODEC)
    SV = "com.hypixel.hytale.server.core."
    reg_ilt(INTc, "Item/Interactions", INTc.CODEC, True,
            after=[SV + "modules.entitystats.asset.EntityStatType", SV + "asset.type.entityeffect.config.EntityEffect", SV + "asset.type.trail.config.Trail",
                   SV + "asset.type.itemanimation.config.ItemPlayerAnimations", SV + "asset.type.soundevent.config.SoundEvent",
                   SV + "asset.type.particle.config.ParticleSystem", SV + "asset.type.model.config.ModelAsset",
                   SV + "modules.entity.hitboxcollision.HitboxCollisionConfig"])
    reg_ilt(ROOTc, "Item/RootInteractions", ROOTc.CODEC, after=[PI + "Interaction"],
            before=[SV + "asset.type.blocktype.config.BlockType", SV + "asset.type.item.config.Item"])
    AR.register(HAS.builder(UIc.class_, DAMc()).setPath("Item/Unarmed/Interactions").setCodec(UIc.CODEC).setKeyFunction(GetId()).build())
    SMOD = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MODc = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier")
    try:
        MODc.CODEC.register("Boost", SMOD.class_, SMOD.ENTITY_CODEC)
        MODc.CODEC.register("Static", SMOD.class_, SMOD.ENTITY_CODEC)
    except Exception:
        pass
    CPj = JClass("javassist.ClassPool")(True)
    CPj.appendClassPath(B.SERVER_JAR)
    CPool = JClass("javassist.bytecode.ConstPool")
    imc = CPj.get("com.hypixel.hytale.server.core.modules.interaction.InteractionModule")
    ms_ = [x for x in imc.getDeclaredMethods() if str(x.getName()) == "setup"][0]
    cp_, it_ = ms_.getMethodInfo().getConstPool(), ms_.getMethodInfo().getCodeAttribute().iterator()
    last_s, last_c, regs = None, None, []
    while it_.hasNext():
        p_ = it_.next()
        op_ = it_.byteAt(p_)
        if op_ in (0x12, 0x13):
            idx = it_.byteAt(p_ + 1) if op_ == 0x12 else it_.u16bitAt(p_ + 1)
            t_ = cp_.getTag(idx)
            if t_ == CPool.CONST_String:
                last_s = str(cp_.getStringInfo(idx))
            elif t_ == CPool.CONST_Class:
                last_c = str(cp_.getClassInfo(idx))
        elif op_ == 0xb6:
            idx = it_.u16bitAt(p_ + 1)
            if str(cp_.getMethodrefClassName(idx)).endswith("AssetCodecMapCodec") and str(cp_.getMethodrefName(idx)) == "register":
                regs.append((last_s, last_c))
    for nm_, cl_ in regs:
        C_ = JClass(cl_)
        INTc.CODEC.register(nm_, C_.class_, jf(C_, "CODEC").get(None))
    PRJIc = JClass("com.hypixel.hytale.server.core.modules.projectile.interaction.ProjectileInteraction")
    INTc.CODEC.register("Projectile", PRJIc.class_, PRJIc.CODEC)
    SPCc = JClass("com.hypixel.hytale.server.core.modules.projectile.config.StandardPhysicsConfig")
    JClass("com.hypixel.hytale.server.core.modules.projectile.config.PhysicsConfig").CODEC.register("Standard", SPCc.class_, SPCc.CODEC)
    CAR = JClass("com.hypixel.hytale.server.core.asset.common.CommonAssetRegistry")
    FCA = JClass("com.hypixel.hytale.server.core.asset.common.asset.FileCommonAsset")
    Paths, FSs, HashMap = JClass("java.nio.file.Paths"), JClass("java.nio.file.FileSystems"), JClass("java.util.HashMap")
    ZFS = {}

    def zfs(zpath):
        if zpath not in ZFS:
            ZFS[zpath] = FSs.newFileSystem(Paths.get(zpath), HashMap())
        return ZFS[zpath]

    import hashlib

    def add_common(pack, zpath, real):
        n = 0
        fs = zfs(zpath)
        with zipfile.ZipFile(zpath) as z:
            for nm in z.namelist():
                if nm.startswith("Common/") and not nm.endswith("/"):
                    h = hashlib.sha256(z.read(nm)).hexdigest() if real else "0" * 64
                    CAR.addCommonAsset(pack, FCA(fs.getPath("/" + nm), nm[len("Common/"):], h, None))
                    n += 1
        return n
    AP = JClass("com.hypixel.hytale.assetstore.AssetPack")
    Files, LinkOption = JClass("java.nio.file.Files"), JClass("java.nio.file.LinkOption")

    def store_order():
        stores = dict((st.getAssetClass(), st) for st in AR.getStoreMap().values())
        done, order = set(), []

        def visit(c, stack):
            if c in done or c not in stores or c in stack:
                return
            stack.add(c)
            for d in stores[c].getLoadsAfter():
                visit(d, stack)
            done.add(c)
            order.append(stores[c])
        for c in list(stores):
            visit(c, set())
        return order

    def loadpack(zpath, name, immutable):
        n0 = len(CAPLOG)
        pack = AP(Paths.get(zpath), name, zfs(zpath).getPath("/"), zfs(zpath), immutable, None, None)
        srv = pack.getRoot().resolve("Server")
        failed = []
        for st in store_order():
            d = srv.resolve(st.getPath())
            if not Files.isDirectory(d, JArray(LinkOption)(0)):
                continue
            try:
                if st.loadAssetsFromDirectory(name, d).hasFailed():
                    failed.append(str(st.getAssetClass().getSimpleName()))
            except Exception as e:
                failed.append("%s EXC %s" % (st.getAssetClass().getSimpleName(), str(e)[:200]))
        return failed, records(n0)
    t0 = time.time()
    nv = add_common("Hytale:Hytale", ASSETS, False)
    vfail, vrec = loadpack(ASSETS, "Hytale:Hytale", True)
    ITEM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    K.check(ITEM.getAssetMap().getAssetMap().size() > 1000, "V: the vanilla items are in the real Item store (%d)" % ITEM.getAssetMap().getAssetMap().size())
    print("V. vanilla pack loaded (%d common files, %.0f s)" % (nv, time.time() - t0))
    pack_name = "Skyy:%s SkyyGear" % VERSION
    add_common(pack_name, JAR, True)
    fail, rec = loadpack(JAR, pack_name, False)
    return {"us": us, "jf": jf, "AR": AR, "ITEM": ITEM, "records": records, "loadpack": loadpack, "fail": fail, "rec": rec, "uni": uni,
            "vfail": vfail, "vrec": vrec}


def run_engine(out):
    from jpype import JClass, JArray, JInt, JLong, JShort, JString, JFloat, JDouble, JImplements, JOverride, JObject, JBoolean, JByte
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=True, big=True)
    E = engine_boot(K)
    us, jf, ITEM = E["us"], E["jf"], E["ITEM"]
    jz = zipfile.ZipFile(JAR)
    # ============================================================================ V
    bad = [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING")]
    # a bare JVM lacks a few codecs / stats the game has: vanilla's own melee attacks fail the SAME two ways here (the Selector codec of
    # the attack selectors, the Stamina stat of the stamina conditions). SkyyGear's live 0.2.6 speed copies of those attacks hit exactly
    # these and nothing else; anything else - or anything about the 0.2.11 bags - is a real failure
    def kind(m_):
        if "Failed to decode asset" in m_ and "Failed to decode 'Selector'" in m_:
            return "selector"
        if "Failed to validate asset" in m_ and "Asset 'Stamina' of type" in m_:
            return "stamina"
        if m_.startswith("Removing child asset 'SkyyGear_Spd") or m_.startswith("Removing child asset '***SkyyGear_Spd") or m_.startswith("Removing child asset 'Weapon_"):
            return "removed"
        if m_.startswith("Failed to decode asset: ***"):
            return "inline"
        return "other"
    vk = set(kind(r[1]) for r in E["vrec"] if r[0] == "SEVERE")
    vkw = set(kind(r[1]) for r in E["vrec"] if r[0] == "WARNING")
    ok_known = [r for r in bad if (kind(r[1]) in ("selector", "stamina") and kind(r[1]) in vk and ("SkyyGear/Speed/" in r[1] or "***SkyyGear_Spd" in r[1]))
                or (kind(r[1]) == "removed" and "SkyyGear_Spd" in r[1])
                or (kind(r[1]) == "inline" and "inline" in vk and "***SkyyGear_Spd" in r[1])]
    print("V. our pack's records by kind: %s (vanilla SEVERE kinds %s, WARNING kinds %s)" % (
        dict((k_, sum(1 for r in bad if kind(r[1]) == k_)) for k_ in ("selector", "stamina", "removed", "inline", "other")), sorted(vk), sorted(vkw)))
    real = [r for r in bad if r not in ok_known]
    newf = [r for r in bad if "Unid" in r[1]]
    for r in real[:40]:
        print("   V real:", kind(r[1]), r[0], r[1][:300].replace("\n", " / "))
    K.check(not real and not newf and set(E["fail"]) <= set(E["vfail"]),
            "V: the jar as its own pack: no failure of its own (the %d bare-JVM lines are the Selector / Stamina gaps vanilla's own attacks hit "
            "too, on the live 0.2.6 speed copies; failed stores %s are vanilla's too %s); NOTHING about the bags (%d)" % (len(ok_known), E["fail"], E["vfail"], len(newf)))
    BAGS = ["Skyy_Unid_Bag_" + n for n in ("Normal", "Unique", "Rare", "Legendary", "Fabled", "Mythic", "Set")]
    gone, pk = [], []
    for b in BAGS:
        it = ITEM.getAssetMap().getAsset(b)
        if it is None:
            gone.append(b)
            continue
        try:
            p = it.toPacket()
            if int(it.getMaxStack()) != 1 or it.getWeapon() is not None or it.getArmor() is not None:
                pk.append((b, "stack / weapon / armor"))
            if str(it.getQualityId()) if hasattr(it, "getQualityId") else False:
                pass
        except Exception as e:
            pk.append((b, str(e)[:150]))
    K.check(not gone and not pk, "V: the 7 bag items are in the Item store, toPacket() works, MaxStack 1, no Weapon / Armor block (missing %s, bad %s)" % (gone, pk))
    IQ = JClass("com.hypixel.hytale.server.core.asset.type.item.config.ItemQuality")
    K.check(all(IQ.getAssetMap().getAsset("Skyy_Gear_" + n) is not None for n in ("Normal", "Unique", "Rare", "Legendary", "Fabled", "Mythic", "Set")),
            "V: the 7 Skyy_Gear_* qualities the bags use are in the ItemQuality store")
    names = set(jz.namelist())
    with zipfile.ZipFile(ASSETS) as az:
        anames = set(az.namelist())
    miss = []
    for b in BAGS:
        d = json.loads(jz.read("Server/Item/Items/SkyyGear/%s.json" % b))
        for k in ("Model", "Texture", "Icon"):
            pth = "Common/" + d[k]
            if pth not in names and pth not in anames:
                miss.append(pth)
    K.check(not miss, "V: every bag Model / Texture / Icon resolves (the jar or Assets.zip): %s" % miss)
    def one_par(o_):
        if isinstance(o_, dict):
            if o_.get("Type") == "Parallel" and len(o_.get("Interactions") or []) < 2:
                return True
            return any(one_par(v_) for v_ in o_.values())
        if isinstance(o_, list):
            return any(one_par(v_) for v_ in o_)
        return False
    onep = [n for n in names if n.endswith(".json") and one_par(json.loads(jz.read(n)))]
    K.check(not onep, "V: no ONE-entry Parallel anywhere in the jar (the 2026-10-08 SkyyArmory lesson): %s" % onep[:3])
    ctl = [("one-entry Parallel", "Server/Item/Interactions/SkyyGearCtl/SkyyGearCtl_Parallel.json",
            json.dumps({"Type": "Simple", "RunTime": 0.1, "Next": {"Type": "Parallel", "Interactions": [{"Interactions": [{"Type": "Simple", "RunTime": 0.1}]}]}}),
            "Array size is invalid"),
           ("Model file missing", "Server/Item/Items/SkyyGearCtl/SkyyGearCtl_Model.json",
            json.dumps(dict(json.loads(jz.read("Server/Item/Items/SkyyGear/Skyy_Unid_Bag_Rare.json")), Model="Items/SkyyGearCtl_NoSuch.blockymodel")),
            "SkyyGearCtl_NoSuch.blockymodel")]
    for i, (what, path, text, needle) in enumerate(ctl):
        zp = os.path.join(SCRATCH, "v-ctl%d.jar" % i)
        with zipfile.ZipFile(zp, "w") as z:
            z.writestr(path, text)
        f_, r2 = E["loadpack"](zp, "Skyy:test ctl%d" % i, False)
        hit = [r for r in r2 if r[0] == "SEVERE" and needle in r[1]]
        K.check(bool(hit), "V CONTROL: %s is refused by the engine validator (SEVERE)" % what)
    print("V. the jar as a pack: %d failed stores, %d SEVERE / WARNING; 7 bags + qualities; controls run" % (len(E["fail"]), len(bad)))

    # ============================================================================ X: set-up
    P = lambda n: JClass(PKG + n)
    Cfg, Pool, Unid, Loot, BoxFn, Ident, Tag, Data, Forge, Roll, Lvl, Defs, View, Fn, Admin, Gear = (
        P("GearCfg"), P("GearPool"), P("GearUnid"), P("GearLoot"), P("GearBoxFn"), P("GearIdent"), P("GearTag"), P("GearData"), P("GearForge"),
        P("GearRoll"), P("GearLevel"), P("GearDefs"), P("GearView"), P("GearFn"), P("GearAdmin"), P("Gear"))
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    Props = JClass("java.util.Properties")
    UUID = JClass("java.util.UUID")
    AL = JClass("java.util.ArrayList")
    IDM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata")
    bridge = JClass("java.lang.System").getProperties()
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    bridge.put("skyy.bridge", br)
    Cfg.apply(Props(), False)

    def defaults():
        Cfg.apply(Props(), False)
        Pool.TAB = None
    # coins (SkyyCoins' bridge contract: get / take Boolean / add)
    PURSE = {}

    @JImplements("java.util.function.Function")
    class CoinGet:
        @JOverride
        def apply(self, u): return JLong(PURSE.get(str(u), 0))

    @JImplements("java.util.function.Function")
    class CoinTake:
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(a[1])
            if PURSE.get(u, 0) < n:
                return JBoolean(False)
            PURSE[u] = PURSE.get(u, 0) - n
            return JBoolean(True)

    @JImplements("java.util.function.Function")
    class CoinAdd:
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(a[1])
            PURSE[u] = PURSE.get(u, 0) + n
            return JLong(PURSE[u])

    def coins_on():
        br.put("coins:fn:get", CoinGet())
        br.put("coins:fn:take", CoinTake())
        br.put("coins:fn:add", CoinAdd())

    def coins_off():
        for k in ("coins:fn:get", "coins:fn:take", "coins:fn:add"):
            br.remove(k)
    coins_on()
    U1 = UUID.fromString("00000000-0000-0000-0000-00000000b001")

    def bagdoc(s):
        return Unid.doc(s)

    def stack(iid, q=1):
        return IS(iid, JInt(q))

    # ============================================================================ X0 the rows + the fresh file
    dt = str(Cfg.defaultsText())
    lt_keys = ["part.lootMob", "loot.mob.chance", "loot.mob.capPerHour", "part.lootChest", "loot.chest.chance", "unid.bags", "unid.rangeHalf",
               "unid.showArmorType", "unid.reroll.max", "unid.reroll.mult", "loot.armorShare", "loot.classLean", "loot.levelTop",
               "loot.dropOnlyWeight", "loot.exclude", "loot.levelShift"]
    tail = dt.strip().split("\n")[-(2 * len(lt_keys) + 1):]
    K.check(tail[0].startswith("# ---- loot:") and [l.split("=", 1)[0] for l in tail[2::2]] == lt_keys,
            "X0: the fresh file ends with the loot heading + its 16 rows (help + key=value each): %s" % tail[:3])
    vals = dict(l.split("=", 1) for l in tail[2::2])
    K.check(vals["loot.mob.chance"] == "6" and vals["loot.chest.chance"] == "33" and vals["unid.reroll.max"] == "3" and vals["unid.reroll.mult"] == "5"
            and vals["unid.rangeHalf"] == "2" and vals["loot.levelTop"] == "49" and vals["loot.mob.capPerHour"] == "20",
            "X0: Skyy's 'yes to all' defaults: mob 6 %%, chest 33 %%, re-identify x5 max 3, range +-2, top 49, cap 20/h: %s" % vals)
    K.check(float(Cfg.LOOT_MOB_PCT) == 6.0 and bool(Cfg.UNID_BAGS) and int(Cfg.REROLL_MAX) == 3 and float(Cfg.REROLL_MULT) == 5.0
            and bool(Cfg.LOOT_MOB) and bool(Cfg.LOOT_CHEST) and abs(float(Cfg.LEVEL_SHIFT) - 0.02) < 1e-9,
            "X0: a file with no loot line loads the defaults (6.0 %% / bags on / 3 / x5 / boost 0.02)")
    pr_ = Props()
    for k, v in (("loot.mob.chance", "250"), ("unid.reroll.max", "-4"), ("loot.levelTop", "0"), ("loot.exclude", " Weapon_Sword_* ")):
        pr_.setProperty(k, v)
    Cfg.apply(pr_, True)
    K.check(float(Cfg.LOOT_MOB_PCT) == 100.0 and int(Cfg.REROLL_MAX) == 0 and int(Cfg.LOOT_TOP) == 1 and str(Cfg.LOOT_EXCLUDE) == "Weapon_Sword_*",
            "X0: hand-edited out-of-range lines are clamped (250 -> 100, -4 -> 0, 0 -> 1, exclude trimmed)")
    defaults()

    # ============================================================================ X1 GearPool
    t = Pool.table()
    ok = [bool(x) for x in t[2]]
    np_ = len(Pool.P_ID)
    K.check(np_ >= 250 and sum(ok) == np_, "X1: every pool id is a live gear item in the real store (%d / %d)" % (sum(ok), np_))
    TK = [str(x) for x in Pool.T_KEY]
    ti = dict((k, i) for i, k in enumerate(TK))
    K.check(len(TK) == 18 and TK[-4:] == ["Armor_Head", "Armor_Chest", "Armor_Hands", "Armor_Legs"] and "Weapon_Sword" in TK and "Weapon_Kunai" in TK,
            "X1: 18 bag types (14 weapon families + 4 armor slots): %s" % TK)
    lv_s = [bool(x) for x in Pool.levels(JInt(ti["Weapon_Sword"]), JInt(0))]
    lv_k = [i for i, x in enumerate(Pool.levels(JInt(ti["Weapon_Kunai"]), JInt(0))) if x]
    K.check(all(lv_s[1:50]) and not lv_s[50] and not lv_s[0] and lv_k == list(range(20, 28)),
            "X1: swords cover Lv 1-49, the one kunai 20-27 (the live bands): %s" % lv_k)
    r1 = list(Pool.range(JInt(ti["Weapon_Kunai"]), JInt(0), JInt(5), JInt(2)))
    r2 = list(Pool.range(JInt(ti["Weapon_Sword"]), JInt(0), JInt(43), JInt(2)))
    r3 = list(Pool.range(JInt(ti["Weapon_Sword"]), JInt(0), JInt(1), JInt(2)))
    r4 = list(Pool.range(JInt(ti["Weapon_Sword"]), JInt(0), JInt(60), JInt(2)))
    K.check(r1 == [20, 22, 20] and r2 == [41, 45, 43] and r3 == [1, 3, 1] and r4 == [47, 49, 49],
            "X1: range = the nearest level with a candidate +-2, clamped / trimmed: kunai@5 %s, sword@43 %s, @1 %s, @60 %s" % (r1, r2, r3, r4))
    K.check(Pool.range(JInt(ti["Weapon_Kunai"]), JInt(0), JInt(10), JInt(0)) is not None and int(Pool.levelCount(JInt(ti["Weapon_Kunai"]), JInt(0), JInt(1), JInt(19))) == 0,
            "X1: levelCount 0 below the kunai band")
    # pickLevel / pickItem
    seen_l, seen_i, badpick = set(), set(), []
    for _ in range(400):
        L = int(Pool.pickLevel(JInt(ti["Weapon_Sword"]), JInt(0), JInt(41), JInt(45)))
        seen_l.add(L)
        iid = str(Pool.pickItem(JInt(ti["Weapon_Sword"]), JInt(0), JInt(L)))
        seen_i.add(iid)
        b_ = list(Lvl.band(iid))
        if not iid.startswith("Weapon_Sword_") or not (b_[0] <= L <= b_[1]):
            badpick.append((L, iid, b_))
    K.check(seen_l == set(range(41, 46)) and not badpick and len(seen_i) >= 2,
            "X1: pickLevel uniform over 41-45 (%s); pickItem = a sword whose LIVE band holds the level (%d different: %s; bad %s)" % (sorted(seen_l), len(seen_i), sorted(seen_i)[:6], badpick[:3]))
    Cfg.DROPONLY_W = 0.0
    dro = [str(Pool.P_ID[i]) for i in range(np_) if bool(Pool.P_DROP[i])]
    picks0 = set(str(Pool.pickItem(JInt(ti["Weapon_Sword"]), JInt(0), JInt(L))) for L in range(1, 50) for _ in range(6))
    K.check(not (picks0 & set(dro)) and "None" not in picks0 or not (picks0 - {"None"}) & set(dro),
            "X1: loot.dropOnlyWeight 0 -> no drop-only sword is ever picked (%d drop-only ids in the pool)" % len(dro))
    Cfg.DROPONLY_W = 1.0
    K.check(len(dro) >= 100 and "Weapon_Sword_Onyxium" in dro and "Armor_Prisma_Chest" in dro and "Weapon_Sword_Iron" not in dro,
            "X1: the drop-only flag: Onyxium sword / Prisma armor drop-only, the Iron sword craftable (%d drop-only)" % len(dro))
    Cfg.LOOT_EXCLUDE = "Weapon_Sword_*,Weapon_Kunai"
    Pool.TAB = None
    K.check(Pool.range(JInt(ti["Weapon_Sword"]), JInt(0), JInt(10), JInt(2)) is None and Pool.range(JInt(ti["Weapon_Kunai"]), JInt(0), JInt(20), JInt(2)) is None
            and bool(Pool.excluded("Weapon_Sword_Iron", "Weapon_Sword_*")) and not bool(Pool.excluded("Weapon_Sword_Iron", "Weapon_Sword")),
            "X1: loot.exclude (Prefix* and exact ids) removes candidates; a type with none left gets no range")
    defaults()
    ats = set()
    for _ in range(200):
        ats.add(int(Pool.pickAt(JInt(ti["Armor_Chest"]), JInt(20))))
    K.check(ats == {1, 2, 3} and int(Pool.pickAt(JInt(ti["Weapon_Sword"]), JInt(20))) == 0,
            "X1: pickAt: Lv 20 chestplates exist as Heavy / Light / Cloth (%s); weapons 0" % sorted(ats))
    Cfg.CLASS_LEAN = 100
    lean = JArray(JString)(["Weapon_Shortbow_", "Weapon_Crossbow_"])
    lt_ = set(TK[int(Pool.pickType(False, JInt(20), lean))] for _ in range(80))
    Cfg.CLASS_LEAN = 0
    nl_ = set(TK[int(Pool.pickType(False, JInt(20), lean))] for _ in range(300))
    arm_ = set(TK[int(Pool.pickType(True, JInt(20), None))] for _ in range(100))
    defaults()
    K.check(lt_ <= {"Weapon_Shortbow", "Weapon_Crossbow"} and len(nl_) >= 8 and arm_ == {"Armor_Head", "Armor_Chest", "Armor_Hands", "Armor_Legs"},
            "X1: class lean 100 %% -> only the class's weapons %s; lean 0 -> any weapon type (%d); armor group -> the 4 slots" % (sorted(lt_), len(nl_)))
    K.check(int(Pool.typeOfId("Weapon_Sword_Iron")) == ti["Weapon_Sword"] and int(Pool.typeOfId("Weapon_Sword_SkyTest")) == ti["Weapon_Sword"]
            and int(Pool.typeOfId("Armor_Leather_Light_Legs")) == ti["Armor_Legs"] and int(Pool.typeOfId("Ingredient_Stick")) == -1
            and int(Pool.typeOfId("Weapon_Scythe_X")) == -1 and int(Pool.atOfId("Armor_Leather_Light_Legs")) == 2
            and int(Pool.atOfId("Armor_Cloth_Silk_Head")) == 3 and int(Pool.atOfId("Armor_Iron_Chest")) == 1 and int(Pool.atOfId("Weapon_Sword_Iron")) == 0,
            "X1: typeOfId (pool id, an unknown sword by family word, armor by slot, not gear, an unknown family) + atOfId (Heavy / Light / Cloth)")
    K.check("bag pool" in str(Pool.statusText()), "X1: statusText: %s" % Pool.statusText())

    # ============================================================================ X2 GearUnid
    bags = {}
    for r in range(7):
        s_ = Unid.make(JInt(ti["Weapon_Sword"]), JInt(0), JInt(r), JInt(41), JInt(45), "test", "test", JInt(0))
        bags[r] = s_
    d3 = bagdoc(bags[3])
    md3 = bags[3].getMetadata()
    K.check([str(bags[r].getItemId()) for r in range(7)] == BAGS and str(d3.getString("mys").getValue()) == "Weapon_Sword"
            and str(d3.getString("r").getValue()) == "legendary" and int(d3.getInt32("lo").getValue()) == 41 and int(d3.getInt32("hi").getValue()) == 45
            and str(d3.getString("at").getValue()) == "-" and not bool(d3.getBoolean("id").getValue()) and int(d3.getInt32("v").getValue()) == 2
            and md3.containsKey(IDM.KEY) and not md3.containsKey("SkyyGear"),
            "X2: make(): one bag id per rarity; the SkyyUnid document {v 2, mys, r, lo, hi, at, src, ls, tier, t, n, id:false}, a per-stack "
            "display, NO gear document")
    n1, n2 = int(bagdoc(bags[1]).getInt64("n").getValue()), int(bagdoc(bags[2]).getInt64("n").getValue())
    K.check(n1 != n2 and str(Forge.fp(bags[1])) != str(Forge.fp(Unid.make(JInt(ti["Weapon_Sword"]), JInt(0), JInt(1), JInt(41), JInt(45), "test", "test", JInt(0)))),
            "X2: every bag has its own nonce -> its own fingerprint (GearForge.fp reads the bag document)")
    dmsg = str(IDM.KEYED_CODEC.getOrNull(md3) if hasattr(IDM.KEYED_CODEC, "getOrNull") else bags[3].getFromMetadataOrNull(IDM.KEYED_CODEC))
    K.check("Unidentified Sword" in dmsg or "Unidentified Sword" in str(md3.toJson()),
            "X2: the bag's display name is 'Unidentified Sword' (the rarity colour): %s" % dmsg[:160])
    jtxt = str(md3.toJson())
    K.check("Lv 41-45" in jtxt and "Legendary" in jtxt and "Cannot be used until identified" in jtxt and "/identify" in jtxt,
            "X2: the tooltip lines: range + rarity, what identify does, cannot be used, the cost")
    ab = Unid.make(JInt(ti["Armor_Chest"]), JInt(2), JInt(2), JInt(10), JInt(14), "test", "test", JInt(0))
    K.check("Light armor" in str(ab.getMetadata().toJson()) and "Cannot be worn" in str(ab.getMetadata().toJson()),
            "X2: an armor bag says 'Light armor' + 'Cannot be worn until identified'")
    Cfg.SHOW_AT = False
    K.check("Light armor" not in str(Unid.make(JInt(ti["Armor_Chest"]), JInt(2), JInt(2), JInt(10), JInt(14), "t", "t", JInt(0)).getMetadata().toJson()),
            "X2: unid.showArmorType off hides the armor type line")
    defaults()
    K.check(Unid.make(JInt(-1), JInt(0), JInt(0), JInt(1), JInt(3), "t", "t", JInt(0)) is None and Unid.make(JInt(0), JInt(0), JInt(9), JInt(1), JInt(3), "t", "t", JInt(0)) is None,
            "X2: make() refuses a bad type / rarity")
    # rarity odds: base Mob column vs the level boost at Lv 50 (above Normal x1.98)
    import collections
    c0 = collections.Counter(int(Unid.rarity(JInt(1), JInt(0))) for _ in range(20000))
    c50 = collections.Counter(int(Unid.rarity(JInt(1), JInt(50))) for _ in range(20000))
    om = [float(x) for x in Cfg.O_MOB]
    want0 = om[0] / sum(om)
    w50 = [om[0]] + [x * (1 + 0.02 * 49) for x in om[1:]]
    want50 = w50[0] / sum(w50)
    K.check(abs(c0[0] / 20000.0 - want0) < 0.02 and abs(c50[0] / 20000.0 - want50) < 0.02 and c50[0] < c0[0],
            "X2: rarity(): the Mob odds (Normal %.3f vs %.3f) and the R5 level boost at Lv 50 (Normal %.3f vs %.3f)" % (c0[0] / 20000.0, want0, c50[0] / 20000.0, want50))
    # roll(): armor share, forced type, range
    kinds = collections.Counter()
    for _ in range(600):
        b_ = Unid.roll(JInt(25), JInt(-1), "mob", "mob", JInt(0), None, JInt(1), JInt(25))
        d_ = bagdoc(b_)
        kinds["armor" if str(d_.getString("mys").getValue()).startswith("Armor_") else "weapon"] += 1
        lo_, hi_ = int(d_.getInt32("lo").getValue()), int(d_.getInt32("hi").getValue())
        if not (lo_ <= 25 <= hi_ and hi_ - lo_ <= 4):
            kinds["badrange"] += 1
    K.check(abs(kinds["armor"] / 600.0 - 0.5) < 0.08 and kinds["badrange"] == 0,
            "X2: roll(): loot.armorShare 50 %% (%s), every range holds the level and is at most 5 wide" % dict(kinds))
    fb_ = bagdoc(Unid.roll(JInt(25), JInt(ti["Weapon_Kunai"]), "t", "t", JInt(2), None, JInt(2), JInt(0)))
    K.check(str(fb_.getString("mys").getValue()) == "Weapon_Kunai" and int(fb_.getInt32("tier").getValue()) == 2,
            "X2: roll() with a forced type + the luggage tier")
    # fromItem
    fi = Unid.fromItem(stack("Weapon_Sword_Copper"), JInt(1), JInt(30), "mob")
    fa = Unid.fromItem(stack("Armor_Leather_Light_Legs"), JInt(2), JInt(-1), None)
    K.check(fi is not None and str(bagdoc(fi).getString("mys").getValue()) == "Weapon_Sword" and int(bagdoc(fi).getInt32("lo").getValue()) == 28
            and str(bagdoc(fi).getString("src").getValue()) == "drop" and str(bagdoc(fi).getString("ls").getValue()) == "mob",
            "X2: fromItem(a copper sword, mob Lv 30) -> a sword bag Lv 28-32 (the MOB's level, not the copper band)")
    K.check(fa is not None and str(bagdoc(fa).getString("at").getValue()) == "Light" and str(bagdoc(fa).getString("ls").getValue()) == "band"
            and str(bagdoc(fa).getString("src").getValue()) == "chest",
            "X2: fromItem(light leather legs, no level) -> a Light leggings bag at the item's band start (ls band, src chest)")
    tagged = Data.put(stack("Weapon_Sword_Copper"), Roll.unidDoc("Weapon_Sword_Copper", JInt(2), "chest"), None)
    Cfg.UNID_BAGS = False
    off_ = Unid.fromItem(stack("Weapon_Sword_Copper"), JInt(1), JInt(30), "mob")
    defaults()
    K.check(Unid.fromItem(stack("Weapon_Spear_Iron", 2), JInt(2), JInt(10), "zone") is None and Unid.fromItem(tagged, JInt(2), JInt(10), "zone") is None
            and Unid.fromItem(stack("Ingredient_Stick"), JInt(2), JInt(10), "zone") is None and off_ is None,
            "X2: fromItem refuses a stack, an item that already has a document, a non-gear item and unid.bags off")
    # why / open
    K.check(Unid.why(bagdoc(bags[3])) is None and "unreadable" in str(Unid.why(None)), "X2: why(): an openable bag passes; no document is refused")
    nd_ = bagdoc(Unid.make(JInt(ti["Weapon_Kunai"]), JInt(0), JInt(1), JInt(20), JInt(22), "t", "t", JInt(0)))
    Cfg.LOOT_EXCLUDE = "Weapon_Kunai"
    Pool.TAB = None
    K.check("any more" in str(Unid.why(nd_)), "X2: why(): a bag whose candidates are gone is refused: %s" % Unid.why(nd_))
    defaults()
    got = Unid.open(bagdoc(bags[3]), U1)
    gid, gL, gdoc, gst = str(got[0]), int(got[1]), got[2], got[3]
    bx = Unid.boxOf(gdoc)
    K.check(gid.startswith("Weapon_Sword_") and 41 <= gL <= 45 and int(Lvl.level(gid, gdoc)) == gL and bool(Data.identified(gdoc))
            and str(Defs.R_ID[int(Data.rarity(gdoc))]) == "legendary" and bx is not None and int(bx.getInt32("n").getValue()) == 0
            and str(gst.getItemId()) == gid and str(gdoc.getString("src").getValue()) == "box",
            "X2: open(): a sword picked AT IDENTIFY, Lv %d inside 41-45, legendary, identified, box {..., n:0}: %s" % (gL, gid))
    # re-roll
    K.check(Unid.rerollable(gst) and not Unid.rerollable(bags[3]) and not Unid.rerollable(Data.put(stack("Weapon_Sword_Iron"), Roll.newDoc("Weapon_Sword_Iron", JInt(1), True, "craft"), None)),
            "X2: rerollable: an item from a bag yes, a bag no, a crafted item no")
    ladder = [int(Unid.rerollCost(JInt(3), JInt(45), JInt(n))) for n in range(3)]
    base = int(Cfg.costIdentify(JInt(3), JInt(45)))
    K.check(ladder == [base * 5, base * 25, base * 125], "X2: re-identify costs = identify x5 per re-roll: %d -> %s" % (base, ladder))
    rr = Unid.reroll(gdoc, U1)
    rdoc = rr[2]
    K.check(str(rr[0]).startswith("Weapon_Sword_") and 41 <= int(rr[1]) <= 45 and int(Unid.rerolls(Unid.boxOf(rdoc))) == 1
            and str(Defs.R_ID[int(Data.rarity(rdoc))]) == "legendary",
            "X2: reroll(): same type + range + rarity, n 0 -> 1 (%s Lv %s)" % (rr[0], rr[1]))
    mx_ = Unid.boxOf(rdoc).clone()
    mx_.put("n", JClass("org.bson.BsonInt32")(JInt(3)))
    dmx = rdoc.clone()
    dmx.put("box", mx_)
    K.check("limit" in str(Unid.rerollWhy(dmx)) and Unid.rerollWhy(rdoc) is None and "Only items" in str(Unid.rerollWhy(Roll.newDoc("Weapon_Sword_Iron", JInt(1), True, "craft"))),
            "X2: rerollWhy: the 3-re-roll limit, ok below it, refused on gear that never was a bag")
    fb0 = Unid.fnBox(JInt(0), BAGS[3], bags[3].getMetadata())
    K.check(list(fb0)[0] == "Unidentified Sword" and "Lv 41-45" in str(list(fb0)[1]) and str(Unid.fnBox(JInt(2), BAGS[3], bags[3].getMetadata())) == "legendary"
            and int(Unid.fnBox(JInt(3), BAGS[3], bags[3].getMetadata())) == 41 and not bool(Unid.fnBox(JInt(4), BAGS[3], bags[3].getMetadata()))
            and "|bag|legendary|Weapon_Sword|41-45|" in str(Unid.fnBox(JInt(5), BAGS[3], bags[3].getMetadata())),
            "X2: fnBox: describe / rarity / level (low end) / identified false / sig")
    K.check("Weapon_Sword legendary lv41-45" in str(Unid.logText(bags[3])) and str(Unid.titleOf(bags[3])) == "Unidentified Sword",
            "X2: logText + titleOf: %s" % Unid.logText(bags[3]))

    # ============================================================================ X3 identify a bag (the write-safe core)
    def idf(c_, slot_, s_, free_=False, u_=U1):
        return Ident.identify(c_, JInt(slot_), s_.getItemId(), Forge.fp(s_), u_, "Tester", free_, None, None)
    c = SIC(JShort(9))
    bag = Unid.make(JInt(ti["Armor_Chest"]), JInt(1), JInt(2), JInt(18), JInt(22), "t", "t", JInt(0))
    c.setItemStackForSlot(JShort(4), bag)
    cost = int(Unid.cost(bagdoc(bag)))
    K.check(cost == int(Ident.costOf(bag)) and cost == int(Cfg.costIdentify(JInt(2), JInt(22))) and Ident.refuse(bag, None) is None,
            "X3: costOf / refuse on a bag = the identify price of (rarity, hi): %d" % cost)
    PURSE[str(U1)] = cost - 1
    r_poor = idf(c, 4, bag)
    PURSE[str(U1)] = cost + 50
    other = Unid.make(JInt(ti["Armor_Chest"]), JInt(1), JInt(2), JInt(18), JInt(22), "t", "t", JInt(0))
    r_fp = Ident.identify(c, JInt(4), bag.getItemId(), Forge.fp(other), U1, "Tester", False, None, None)
    coins_off()
    r_nc = idf(c, 4, bag)
    coins_on()
    K.check(int(r_poor[0]) == 0 and "Not enough coins" in str(r_poor[1]) and int(r_fp[0]) == 0 and "moved or changed" in str(r_fp[1])
            and int(r_nc[0]) == 0 and "Coins are not available" in str(r_nc[1]) and PURSE[str(U1)] == cost + 50
            and str(c.getItemStack(JShort(4)).getItemId()) == bag.getItemId(),
            "X3: refused before anything moves: too poor / another bag's fingerprint / SkyyCoins missing - the bag stays, no coin moved")
    r_ok = idf(c, 4, bag)
    now_ = c.getItemStack(JShort(4))
    nd = Data.effective(now_.getItemId(), now_.getMetadata())
    K.check(int(r_ok[0]) == 1 and str(now_.getItemId()).startswith("Armor_"), "X3: identify a bag -> the item in the SAME slot (%s)" % r_ok[1])
    K.check(int(r_ok[0]) == 1 and int(Pool.typeOfId(now_.getItemId())) == ti["Armor_Chest"] and int(Pool.atOfId(now_.getItemId())) == 1
            and 18 <= int(Lvl.level(now_.getItemId(), nd)) <= 22 and str(Defs.R_ID[int(Data.rarity(nd))]) == "rare" and bool(Data.identified(nd))
            and PURSE[str(U1)] == 50 and int(r_ok[5]) == cost and Unid.boxOf(nd) is not None,
            "X3: it is a HEAVY chestplate Lv 18-22, rare, identified, box kept, %d coins taken: %s" % (cost, now_.getItemId()))
    r_again = idf(c, 4, bag)
    K.check(int(r_again[0]) == 0, "X3: the old bag's fingerprint never identifies again (no dupe): %s" % r_again[1])
    # refused before coins: no candidate any more
    c2 = SIC(JShort(3))
    kb = Unid.make(JInt(ti["Weapon_Kunai"]), JInt(0), JInt(0), JInt(20), JInt(22), "t", "t", JInt(0))
    c2.setItemStackForSlot(JShort(0), kb)
    Cfg.LOOT_EXCLUDE = "Weapon_Kunai"
    Pool.TAB = None
    PURSE[str(U1)] = 100000
    r_none = idf(c2, 0, kb)
    defaults()
    K.check(int(r_none[0]) == 0 and "any more" in str(r_none[1]) and PURSE[str(U1)] == 100000 and str(c2.getItemStack(JShort(0)).getItemId()) == kb.getItemId(),
            "X3: no candidate in its range -> refused BEFORE coins move (%s)" % r_none[1])
    # the write fails -> refund, the bag stays
    FX = JClass(FAKE_PKG + ".FailContainer")
    fx = FX(JShort(3))
    fbag = Unid.make(JInt(ti["Weapon_Sword"]), JInt(0), JInt(0), JInt(5), JInt(9), "t", "t", JInt(0))
    fx.setItemStackForSlot(JShort(1), fbag)
    fx.refuse = True
    PURSE[str(U1)] = 5000
    r_ref = idf(fx, 1, fbag)
    fx.refuse = False
    K.check(int(r_ref[0]) == -1 and "refunded" in str(r_ref[1]) and PURSE[str(U1)] == 5000 and str(fx.getItemStack(JShort(1)).getItemId()) == fbag.getItemId(),
            "X3: the slot refuses the write -> REFUND, the bag stays (%s)" % r_ref[1])
    r_free = idf(fx, 1, fbag, free_=True)
    K.check(int(r_free[0]) == 1 and PURSE[str(U1)] == 5000 and str(fx.getItemStack(JShort(1)).getItemId()).startswith("Weapon_Sword_"),
            "X3: free (admin /gear identify) -> no coins")

    # ============================================================================ X4 re-identify x3 + the limit
    rc = SIC(JShort(9))
    first = Unid.open(bagdoc(Unid.make(JInt(ti["Weapon_Shortbow"]), JInt(0), JInt(3), JInt(30), JInt(34), "t", "t", JInt(0))), U1)[3]
    rc.setItemStackForSlot(JShort(2), first)
    PURSE[str(U1)] = 10 ** 9
    steps = []
    for k in range(4):
        cur = rc.getItemStack(JShort(2))
        before = PURSE[str(U1)]
        rr_ = Ident.reroll(rc, JInt(2), cur.getItemId(), Forge.fp(cur), U1, "Tester")
        aft = rc.getItemStack(JShort(2))
        ad = Data.effective(aft.getItemId(), aft.getMetadata())
        steps.append((int(rr_[0]), before - PURSE[str(U1)], str(aft.getItemId()), int(Unid.rerolls(Unid.boxOf(ad))), str(Defs.R_ID[int(Data.rarity(ad))]),
                      int(Lvl.level(aft.getItemId(), ad)), str(rr_[1])))
    b34 = int(Cfg.costIdentify(JInt(3), JInt(34)))
    K.check([s_[0] for s_ in steps] == [1, 1, 1, 0] and [s_[1] for s_ in steps] == [b34 * 5, b34 * 25, b34 * 125, 0]
            and [s_[3] for s_ in steps] == [1, 2, 3, 3] and all(s_[4] == "legendary" and s_[2].startswith("Weapon_Shortbow_") and 30 <= s_[5] <= 34 for s_ in steps)
            and "limit" in steps[3][6],
            "X4: re-identify 3 times (x5 ladder %s), the 4th is refused (limit); rarity, type and range kept: %s" % ([s_[1] for s_ in steps], [s_[:4] for s_ in steps]))
    rfd = Data.effective(rc.getItemStack(JShort(2)).getItemId(), rc.getItemStack(JShort(2)).getMetadata())
    K.check(not rfd.containsKey("rf") and not rfd.containsKey("rfN"), "X4: a re-identified item carries no reforge fields (reforges are cleared)")
    # refund on a refused write
    fx2 = FX(JShort(3))
    ff = Unid.open(bagdoc(Unid.make(JInt(ti["Weapon_Mace"]), JInt(0), JInt(1), JInt(15), JInt(19), "t", "t", JInt(0))), U1)[3]
    fx2.setItemStackForSlot(JShort(0), ff)
    fx2.refuse = True
    PURSE[str(U1)] = 100000
    rr2 = Ident.reroll(fx2, JInt(0), ff.getItemId(), Forge.fp(ff), U1, "Tester")
    fx2.refuse = False
    PURSE[str(U1)] = 1
    rr3 = Ident.reroll(fx2, JInt(0), ff.getItemId(), Forge.fp(ff), U1, "Tester")
    crafted = Data.put(stack("Weapon_Sword_Iron"), Roll.newDoc("Weapon_Sword_Iron", JInt(1), True, "craft"), None)
    fx2.setItemStackForSlot(JShort(1), crafted)
    rr4 = Ident.reroll(fx2, JInt(1), crafted.getItemId(), Forge.fp(crafted), U1, "Tester")
    K.check(int(rr2[0]) == -1 and "refunded" in str(rr2[1]) and int(rr3[0]) == 0 and "Not enough coins" in str(rr3[1]) and PURSE[str(U1)] == 1
            and int(rr4[0]) == 0 and "mystery bag" in str(rr4[1]) and str(fx2.getItemStack(JShort(0)).getItemId()) == ff.getItemId(),
            "X4: re-identify: refused write -> refund; too poor; never on crafted gear")

    # ============================================================================ X5 rows, Identify all, the inventory
    INV = JClass("com.hypixel.hytale.server.core.inventory.Inventory")
    ICOMP = "com.hypixel.hytale.server.core.inventory.InventoryComponent$"

    def comp(kind, cont):
        Cc = JClass(ICOMP + kind)
        for args in ((cont, JByte(0)), (cont,)):
            try:
                return Cc(*args)
            except Exception:
                pass
        o_ = us.allocateInstance(Cc.class_)
        jf(Cc, "inventory").set(o_, cont)
        return o_

    def mkinv():
        inv_ = INV()
        cs_ = {"hotbar": SIC(JShort(9)), "storage": SIC(JShort(36)), "backpack": SIC(JShort(9)), "armor": SIC(JShort(4)), "utility": SIC(JShort(4)), "tools": SIC(JShort(4))}
        for f_, kind in (("hotbar", "Hotbar"), ("storage", "Storage"), ("backpack", "Backpack"), ("armor", "Armor"), ("utility", "Utility"), ("tools", "Tool")):
            jf(INV, f_).set(inv_, comp(kind, cs_[f_]))
        return inv_, cs_
    inv, cs = mkinv()
    K.check(inv.getHotbar() is cs["hotbar"] or inv.getHotbar().equals(cs["hotbar"]), "X5: the stand-in inventory answers its real containers")
    b1 = Unid.make(JInt(ti["Weapon_Axe"]), JInt(0), JInt(1), JInt(10), JInt(14), "t", "t", JInt(0))
    b2 = Unid.make(JInt(ti["Armor_Legs"]), JInt(3), JInt(0), JInt(20), JInt(24), "t", "t", JInt(0))
    from_bag = Unid.open(bagdoc(Unid.make(JInt(ti["Weapon_Sword"]), JInt(0), JInt(2), JInt(25), JInt(29), "t", "t", JInt(0))), U1)[3]
    old_unid = Data.put(stack("Weapon_Sword_Copper"), Roll.unidDoc("Weapon_Sword_Copper", JInt(2), "chest"), None)
    cs["hotbar"].setItemStackForSlot(JShort(0), b1)
    cs["storage"].setItemStackForSlot(JShort(5), b2)
    cs["backpack"].setItemStackForSlot(JShort(1), from_bag)
    cs["storage"].setItemStackForSlot(JShort(6), old_unid)
    rows = [tuple(x) for x in Ident.rows(inv)]
    rrows = [tuple(x) for x in Ident.rerollRows(inv)]
    K.check(set(rows) == {(0, 0), (1, 5), (1, 6)} and rrows == [(2, 1)], "X5: rows = the 2 bags + the old-style unidentified item; rerollRows = the item from a bag: %s / %s" % (rows, rrows))
    nm1, sb1 = str(Ident.rowName(b1, None)), str(Ident.rowSub(b1, None, Ident.rowRarity(b1, None), JInt(0)))
    fbd = Data.effective(from_bag.getItemId(), from_bag.getMetadata())
    sbr = str(Ident.rowSub(from_bag, fbd, Ident.rowRarity(from_bag, fbd), Lvl.level(from_bag.getItemId(), fbd)))
    K.check(nm1 == "Unidentified Axe" and sb1 == "Unique - Lv 10-14" and sbr.startswith("Re-identify 0/3 - Lv ") and int(Ident.rowRarity(b2, None)) == 0,
            "X5: row texts: '%s' / '%s' / '%s'" % (nm1, sb1, sbr))
    PURSE[str(U1)] = 10 ** 7
    bysec = JArray(JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer"))([cs["hotbar"], cs["storage"], cs["backpack"], cs["armor"], cs["utility"], cs["tools"]])
    recent = AL()
    resall = Ident.allIn(bysec, Ident.rows(inv), U1, "Tester", recent)
    K.check(int(resall[0]) == 3 and not Unid.isBox(cs["hotbar"].getItemStack(JShort(0)).getItemId()) and not Unid.isBox(cs["storage"].getItemStack(JShort(5)).getItemId())
            and any("Unidentified" not in str(x) and ":" in str(x) for x in recent) and str(cs["backpack"].getItemStack(JShort(1)).getItemId()) == str(from_bag.getItemId()),
            "X5: Identify all: both bags + the old item identified, the re-roll item untouched; recent names the revealed items: %s" % [str(x)[:50] for x in recent])

    # ============================================================================ X6 IdentifyPage
    def uitext(ub_):
        out_ = []
        for c_ in ub_.getCommands():
            for f_ in ("selector", "data", "text"):
                try:
                    v_ = getattr(c_, f_)
                    if v_ is not None:
                        out_.append(str(v_))
                except Exception:
                    pass
        return chr(10).join(out_)
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    prx = us.allocateInstance(PR.class_)
    jf(PR, "uuid").set(prx, U1)
    jf(PR, "username").set(prx, "Tester")
    FP = JClass(FAKE_PKG + ".FakeIdPage")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    inv2, cs2 = mkinv()
    pb = Unid.make(JInt(ti["Weapon_Daggers"]), JInt(0), JInt(4), JInt(30), JInt(34), "t", "t", JInt(0))
    cs2["hotbar"].setItemStackForSlot(JShort(2), pb)
    pg = FP(prx)
    K.check(bool(pg.pick(inv2, JInt(0), JInt(2))) and "Unidentified Daggers" in str(pg.info), "X6: pick() a bag: %s" % pg.info)
    ub, ue = UCB(), UEB()
    ub.appendInline(None, "Group #SkyyGMain { }")
    pg.detail(ub, ue, U1, pb, inv2)
    cmds = uitext(ub)
    K.check("Mystery bag" in cmds and "Unidentified Daggers" in cmds and "SkyyGBtnId" in cmds and "Lv 30-34" in cmds,
            "X6: detail() of a bag = detailBox (header Mystery bag, the bag name, its range, the Identify button)")
    PURSE[str(U1)] = 10 ** 7
    pg.lastClick = JLong(0)
    pg.one(inv2)
    now2 = cs2["hotbar"].getItemStack(JShort(2))
    K.check(str(pg.info).startswith("+It was ") and not Unid.isBox(now2.getItemId()) and str(pg.selId) == str(now2.getItemId()),
            "X6: one() on a bag: '%s'; the page now selects the revealed item" % pg.info)
    ub2, ue2 = UCB(), UEB()
    ub2.appendInline(None, "Group #SkyyGMain { }")
    pg.detail(ub2, ue2, U1, now2, inv2)
    c2s = uitext(ub2)
    K.check("Re-identify" in c2s and "re-roll 1 of 3" in c2s and "reforges are lost" in c2s, "X6: detail() of an item from a bag = detailReroll (cost, 1 of 3, the warning)")
    b4 = PURSE[str(U1)]
    pg.lastClick = JLong(0)
    pg.reroll(inv2)
    armed = str(pg.info)
    same = str(cs2["hotbar"].getItemStack(JShort(2)).getItemId()) == str(now2.getItemId()) and PURSE[str(U1)] == b4
    pg.lastClick = JLong(0)
    pg.reroll(inv2)
    K.check("Confirm" in armed and same and str(pg.info).startswith("+It is now ") and PURSE[str(U1)] < b4,
            "X6: the two-click re-identify: the first click only arms ('%s'), the second does it ('%s')" % (armed[:60], str(pg.info)[:60]))
    ub3, ue3 = UCB(), UEB()
    ub3.appendInline(None, "Group #SkyyGMain { }")
    pg.rows = Ident.rows(inv2)
    pg.rows.addAll(Ident.rerollRows(inv2))
    pg.list(ub3, ue3, inv2)
    c3s = uitext(ub3)
    K.check("Unidentified gear + bags" in c3s and "Re-identify 1/3" in c3s, "X6: list(): the bag + re-roll rows and the new heading")
    # build() + handleDataEvent("rr") through the stand-in store (the player component -> this inventory)
    EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    CTYc = JClass("com.hypixel.hytale.component.ComponentType")
    MODr = JClass("java.lang.reflect.Modifier")

    def single(cn):
        JClass(FAKE_PKG + ".FakeUtil").single(cn)
    for cn in ("com.hypixel.hytale.server.core.modules.entity.EntityModule", "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule",
               "com.hypixel.hytale.server.core.modules.block.BlockModule"):
        single(cn)
    single("com.hypixel.hytale.server.core.universe.Universe")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    pl = us.allocateInstance(PLA.class_)
    jf(PLA, "inventory").set(pl, inv2)
    REFc = JClass("com.hypixel.hytale.component.Ref")
    ref = us.allocateInstance(REFc.class_)
    jf(REFc, "index").setInt(ref, JInt(7))
    FS, FBuf, FCh = JClass(FAKE_PKG + ".FakeStore"), JClass(FAKE_PKG + ".FakeBuffer"), JClass(FAKE_PKG + ".FakeChunk")
    IHM = JClass("java.util.IdentityHashMap")
    st = us.allocateInstance(FS.class_)
    st.comps = JClass("java.util.HashMap")()
    pm = IHM()
    pm.put(PLA.getComponentType(), pl)
    pm.put(PR.getComponentType(), prx)
    st.comps.put(ref, pm)
    jf(REFc, "store").set(ref, st)
    ub4, ue4 = UCB(), UEB()
    pg.build(ref, ub4, ue4, st)
    c4s = uitext(ub4)
    K.check("Identify" in c4s and "SkyyGBtnAll" in c4s, "X6: build() through the stand-in store renders the whole page")
    rb0 = int(pg.rebuilds)
    PURSE[str(U1)] = 10 ** 9
    pg.lastClick = JLong(0)
    pg.handleDataEvent(ref, st, '{"a":"rr"}')
    K.check(int(pg.rebuilds) == rb0 + 1 and ("Confirm" in str(pg.info) or str(pg.info).startswith("+") or str(pg.info).startswith("-")),
            "X6: handleDataEvent('rr') -> reroll() + rebuild: %s" % str(pg.info)[:80])

    # ============================================================================ X7 GearTag: marks, unid -> bag, spread, tagContainer
    Tag.MARKS.clear()
    Tag.mark("w", JDouble(10.0), JDouble(65.0), JDouble(10.0), JInt(33))
    Tag.mark("w", JDouble(50.0), JDouble(65.0), JDouble(10.0))
    K.check(int(Tag.levelNear("w", JDouble(10.5), JDouble(65.0), JDouble(10.2))) == 33 and int(Tag.levelNear("w", JDouble(50.0), JDouble(65.0), JDouble(10.0))) == -1
            and int(Tag.levelNear("w", JDouble(30.0), JDouble(65.0), JDouble(10.0))) == -1 and bool(Tag.near("w", JDouble(10.0), JDouble(65.0), JDouble(10.0))),
            "X7: marks carry the mob level (33 near, -1 for a mark without one / none near)")
    ub_ = Tag.unid(stack("Weapon_Battleaxe_Iron"), JInt(1), JInt(33), "mob")
    st_ = Tag.unid(stack("Weapon_Spear_Iron", 3), JInt(1), JInt(33), "mob")
    K.check(Unid.isBox(ub_.getItemId()) and str(bagdoc(ub_).getString("mys").getValue()) == "Weapon_Battleaxe" and int(bagdoc(ub_).getInt32("lo").getValue()) == 31
            and not Unid.isBox(st_.getItemId()) and Data.gearDoc(st_.getMetadata()) is not None,
            "X7: unid(): a single mob-dropped battleaxe -> a bag Lv 31-35; a stack of 3 spears keeps the 0.2 document")
    ch = SIC(JShort(9))
    ch.setItemStackForSlot(JShort(0), stack("Weapon_Spear_Iron", 3))
    ch.setItemStackForSlot(JShort(1), stack("Armor_Iron_Head"))
    ch.setItemStackForSlot(JShort(2), stack("Ingredient_Stick", 5))
    nt = int(Tag.tagContainer(ch, "test", JInt(17), "zone"))
    ids = [str(ch.getItemStack(JShort(i)).getItemId()) if ch.getItemStack(JShort(i)) is not None and not ch.getItemStack(JShort(i)).isEmpty() else "-" for i in range(9)]
    nbags = sum(1 for x in ids if x.startswith("Skyy_Unid_Bag_"))
    K.check(nbags == 4 and ids[2] == "Ingredient_Stick" and nt >= 2, "X7: tagContainer(): the 3-spear stack spread into 3 bags + the helmet -> 4 bags; the sticks untouched: %s (%d)" % (ids, nt))
    full = SIC(JShort(2))
    full.setItemStackForSlot(JShort(0), stack("Weapon_Spear_Iron", 3))
    full.setItemStackForSlot(JShort(1), stack("Ingredient_Stick"))
    Tag.tagContainer(full, "test", JInt(17), "zone")
    f0 = full.getItemStack(JShort(0))
    K.check(not Unid.isBox(f0.getItemId()) and int(f0.getQuantity()) >= 1 and Data.gearDoc(f0.getMetadata()) is not None,
            "X7: no empty slot -> the stack stays one 0.2-style unidentified stack (nothing lost)")
    # review fix: a refused slot write during the spread never leaves MORE items than the stack had (critic: the last write was unchecked)
    FAT = JClass("com.hypixel.hytale.server.core.inventory.container.filter.FilterActionType")
    SFl = JClass("com.hypixel.hytale.server.core.inventory.container.filter.SlotFilter")

    def ctotal(c_):
        n_ = 0
        for i_ in range(int(c_.getCapacity())):
            x_ = c_.getItemStack(JShort(i_))
            if x_ is not None and not x_.isEmpty():
                n_ += int(x_.getQuantity())
        return n_

    def denied(deny):
        c_ = SIC(JShort(3))
        c_.setItemStackForSlot(JShort(0), stack("Weapon_Spear_Iron", 3))
        for d_ in deny:
            c_.setSlotFilter(FAT.ADD, JShort(d_), SFl.DENY)
        n_ = int(Tag.spread(c_, JInt(0), JInt(17), "zone"))
        bags_ = sum(1 for i_ in range(3) if c_.getItemStack(JShort(i_)) is not None and not c_.getItemStack(JShort(i_)).isEmpty()
                    and Unid.isBox(c_.getItemStack(JShort(i_)).getItemId()))
        return n_, bags_, ctotal(c_)
    ctl = SIC(JShort(2))
    ctl.setSlotFilter(FAT.ADD, JShort(1), SFl.DENY)
    ctl_ok = bool(ctl.setItemStackForSlot(JShort(1), stack("Ingredient_Stick")).succeeded())
    r_b1, r_b2, r_src, r_ok = denied([1]), denied([2]), denied([0]), denied([])
    K.check(not ctl_ok and r_b1 == (0, 0, 3) and r_b2 == (1, 1, 3) and r_src == (0, 0, 3) and r_ok == (3, 3, 3),
            "X7: spread() with a REFUSED slot write (a DENY filter; control: a direct write is refused): the first bag slot refused -> "
            "all 3 back as one stack; the last bag slot refused -> 1 bag + a stack of 2; the source slot refused -> nothing changes; none "
            "refused -> 3 bags; never more than the 3 items: %s %s %s %s" % (r_b1, r_b2, r_src, r_ok))
    Cfg.UNID_BAGS = False
    ch2 = SIC(JShort(4))
    ch2.setItemStackForSlot(JShort(0), stack("Armor_Iron_Head"))
    Tag.tagContainer(ch2, "test")
    defaults()
    K.check(not Unid.isBox(ch2.getItemStack(JShort(0)).getItemId()) and Data.gearDoc(ch2.getItemStack(JShort(0)).getMetadata()) is not None,
            "X7: unid.bags off -> the 0.2 tag (old 2-argument tagContainer)")

    # ============================================================================ X8 GearLoot
    UUIDC = JClass("com.hypixel.hytale.server.core.entity.UUIDComponent")
    HRC = JClass("com.hypixel.hytale.server.core.modules.entity.component.HeadRotation")
    TC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    DTH = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    DMG = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    DENT = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    R3F = JClass("com.hypixel.hytale.math.vector.Rotation3f")
    V3 = JClass("org.joml.Vector3d")
    GM = JClass("com.hypixel.hytale.protocol.GameMode")
    NPC_U = UUID.fromString("00000000-0000-0000-0000-0000000c0001")
    LEVEL = {"lv": 24}

    @JImplements("java.util.function.Function")
    class MobLevel:
        @JOverride
        def apply(self, a):
            return JInt(LEVEL["lv"]) if a is not None else JInt(-1)
    br.put("mob:fn:level", MobLevel())

    def uuidc(u_):
        o_ = us.allocateInstance(UUIDC.class_)
        jf(UUIDC, "uuid").set(o_, u_)
        return o_

    def headrot():
        o_ = us.allocateInstance(HRC.class_)
        jf(HRC, "rotation").set(o_, R3F())
        return o_

    def death(src_):
        o_ = us.allocateInstance(DTH.class_)
        d_ = us.allocateInstance(DMG.class_)
        jf(DMG, "source").set(d_, src_)
        jf(DTH, "deathInfo").set(o_, d_)
        return o_
    killer = us.allocateInstance(REFc.class_)
    jf(REFc, "index").setInt(killer, JInt(3))
    jf(REFc, "store").set(killer, st)
    kpl = us.allocateInstance(PLA.class_)
    jf(PLA, "gameMode").set(kpl, GM.Adventure)
    km = IHM()
    km.put(PLA.getComponentType(), kpl)
    km.put(PR.getComponentType(), prx)
    st.comps.put(killer, km)
    chunk = us.allocateInstance(FCh.class_)

    def mkchunk(npc_u, with_hr=True, player=False):
        m_ = IHM()
        m_.put(UUIDC.getComponentType(), uuidc(npc_u))
        if with_hr:
            m_.put(HRC.getComponentType(), headrot())
        if player:
            m_.put(PLA.getComponentType(), kpl)
        chunk.comps = m_
        return chunk
    K.check(int(Loot.mobLevel(mkchunk(NPC_U), JInt(0), "w")) == 24, "X8: mobLevel reads mob:fn:level with the NPC's uuid")
    src_ok = DENT(killer)
    other_store = us.allocateInstance(FS.class_)
    kother = us.allocateInstance(REFc.class_)
    jf(REFc, "index").setInt(kother, JInt(4))
    jf(REFc, "store").set(kother, other_store)
    kdead = us.allocateInstance(REFc.class_)
    jf(REFc, "index").setInt(kdead, JInt(-2147483648))
    jf(REFc, "store").set(kdead, st)
    K.check(Loot.killer(death(src_ok), st) is not None and Loot.killer(death(DENT(kother)), st) is None and Loot.killer(death(DENT(kdead)), st) is None
            and Loot.killer(death(None), st) is None and Loot.killer(None, st) is None,
            "X8: killer(): an EntitySource whose ref is live and in THIS store; another store / a dead ref / no source -> none")
    SPAWNED = []

    @JImplements("java.util.function.BiFunction")
    class Spawn:
        @JOverride
        def apply(self, box_, at_):
            SPAWNED.append((box_, float(at_.y())))
            return None
    Loot.SPAWN = Spawn()
    buf = us.allocateInstance(FBuf.class_)
    buf.st = st
    pos = V3(JDouble(5.0), JDouble(70.0), JDouble(5.0))
    Cfg.LOOT_MOB_PCT = 100.0
    Loot.HOUR.clear()
    Loot.ROLLED.clear()
    n_ok = int(Loot.mobRoll(mkchunk(NPC_U), JInt(0), st, buf, death(src_ok), pos, JInt(24), "w"))
    n_twice = int(Loot.mobRoll(mkchunk(NPC_U), JInt(0), st, buf, death(src_ok), pos, JInt(24), "w"))
    sb_ = SPAWNED[0][0] if SPAWNED else None
    K.check(n_ok == 1 and n_twice == 0 and len(SPAWNED) == 1 and Unid.isBox(sb_.getItemId()) and SPAWNED[0][1] == 71.0
            and int(bagdoc(sb_).getInt32("lo").getValue()) <= 24 <= int(bagdoc(sb_).getInt32("hi").getValue()) and str(bagdoc(sb_).getString("src").getValue()) == "mob",
            "X8: mobRoll at 100 %%: ONE bag at the mob's level, spawned at the mob + (0, 1, 0); the same death never rolls twice")
    cases = []
    jf(PLA, "gameMode").set(kpl, GM.Creative)
    cases.append(("creative killer", int(Loot.mobRoll(mkchunk(UUID.randomUUID()), JInt(0), st, buf, death(src_ok), pos, JInt(24), "w"))))
    jf(PLA, "gameMode").set(kpl, GM.Adventure)
    cases.append(("no killer", int(Loot.mobRoll(mkchunk(UUID.randomUUID()), JInt(0), st, buf, death(None), pos, JInt(24), "w"))))
    cases.append(("no level", int(Loot.mobRoll(mkchunk(UUID.randomUUID()), JInt(0), st, buf, death(src_ok), pos, JInt(0), "w"))))
    cases.append(("no head rotation", int(Loot.mobRoll(mkchunk(UUID.randomUUID(), with_hr=False), JInt(0), st, buf, death(src_ok), pos, JInt(24), "w"))))
    cases.append(("a player died", int(Loot.mobRoll(mkchunk(UUID.randomUUID(), player=True), JInt(0), st, buf, death(src_ok), pos, JInt(24), "w"))))
    Cfg.LOOT_MOB_PCT = 0.0
    cases.append(("chance 0", int(Loot.mobRoll(mkchunk(UUID.randomUUID()), JInt(0), st, buf, death(src_ok), pos, JInt(24), "w"))))
    Cfg.LOOT_MOB_PCT = 100.0
    Cfg.LOOT_MOB = False
    cases.append(("part off", int(Loot.mobRoll(mkchunk(UUID.randomUUID()), JInt(0), st, buf, death(src_ok), pos, JInt(24), "w"))))
    Cfg.LOOT_MOB = True
    K.check(all(n_ == 0 for _w, n_ in cases) and len(SPAWNED) == 1, "X8: mobRoll refuses: %s" % cases)
    # the hourly cap: 20 per player (memory), then none
    Loot.HOUR.clear()
    capn = sum(int(Loot.mobRoll(mkchunk(UUID.randomUUID()), JInt(0), st, buf, death(src_ok), pos, JInt(24), "w")) for _ in range(25))
    K.check(capn == 20 and int(Loot.N[3]) >= 5, "X8: loot.mob.capPerHour 20 -> 20 of 25 kills drop a bag, the rest count as cap hits")
    # the real spawn lines (= DropDeathItems') by bytecode
    CPb = JClass("javassist.ClassPool")(False)
    CPb.appendSystemPath()
    CPb.appendClassPath(B.SERVER_JAR)
    CPb.appendClassPath(JAR)
    IPk = JClass("javassist.bytecode.InstructionPrinter")

    def bc(cls, m):
        out_ = []
        for mm in CPb.get(cls).getDeclaredMethods():
            if str(mm.getName()) == m:
                bos_ = JClass("java.io.ByteArrayOutputStream")()
                IPk(JClass("java.io.PrintStream")(bos_)).print_(mm)
                out_.append(str(bos_.toString()))
        return "\n".join(out_)
    mr = bc(PKG + "GearLoot", "mobRoll")
    dd = bc("com.hypixel.hytale.server.npc.systems.NPCDamageSystems$DropDeathItems", "tick")
    seq = ["Vector3d.<init>((Lorg/joml/Vector3dc;)V)", "Vector3d.add((DDD)", "Rotation3f.<init>((Lcom/hypixel/hytale/math/vector/Rotation3fc;)V)",
           "ItemComponent.generateItemDrops", "AddReason.SPAWN", "CommandBuffer.addEntities"]
    pos_mr = [mr.find(x) for x in seq]
    pos_dd = [dd.find(x) for x in seq]
    K.check(all(p_ >= 0 for p_ in pos_mr) and pos_mr == sorted(pos_mr) and all(p_ >= 0 for p_ in pos_dd) and "HeadRotation.getRotation" in mr,
            "X8: the real spawn = DropDeathItems' own lines in the same order (new Vector3d(pos).add(0,1,0), new Rotation3f(head), generateItemDrops, "
            "addEntities SPAWN): %s / %s" % (pos_mr, pos_dd))
    # chestLevel
    @JImplements("java.util.function.Function")
    class LevelAt:
        @JOverride
        def apply(self, a):
            return JArray(JObject)([JInt(12), JInt(16), "biome", "test"])
    br.put("mob:fn:levelAt", LevelAt())
    cl1 = [list(Loot.chestLevel("w", JInt(1), JInt(2), JInt(3), "Zone3_Encounters_Tier1")) for _ in range(40)]
    br.remove("mob:fn:levelAt")
    cl2 = [list(Loot.chestLevel("w", JInt(1), JInt(2), JInt(3), "Zone2_Goblin_Tier2")) for _ in range(40)]
    cl3 = Loot.chestLevel("w", JInt(1), JInt(2), JInt(3), "Portals_Oasis")
    K.check(all(12 <= a_ <= 16 and b_ == 1 for a_, b_ in cl1) and all(20 <= a_ <= 30 and b_ == 2 for a_, b_ in cl2) and cl3 is None,
            "X8: chestLevel: mob:fn:levelAt's band (12-16) first, else the drop list's Zone<N> band (Zone2 20-30), else none")
    cx = SIC(JShort(3))
    cx.setItemStackForSlot(JShort(0), stack("Ingredient_Stick"))
    Cfg.LOOT_CHEST_PCT = 100.0
    e1 = int(Loot.chestExtra(cx, JInt(17), "test"))
    full2 = SIC(JShort(1))
    full2.setItemStackForSlot(JShort(0), stack("Ingredient_Stick"))
    e2 = int(Loot.chestExtra(full2, JInt(17), "test"))
    Cfg.LOOT_CHEST_PCT = 0.0
    e3 = int(Loot.chestExtra(SIC(JShort(3)), JInt(17), "test"))
    defaults()
    K.check(e1 == 1 and sum(1 for i in range(3) if cx.getItemStack(JShort(i)) is not None and Unid.isBox(cx.getItemStack(JShort(i)).getItemId())) == 1
            and e2 == 0 and int(Loot.N[6]) >= 1 and e3 == 0,
            "X8: chestExtra: one bag into an EMPTY slot; a full chest gets none (counted); chance 0 none")
    st_txt, ct_txt = str(Loot.statusText()), str(Loot.countsText())
    K.check("extra mob bags 6.0%" in st_txt and "bags dropped" in ct_txt, "X8: statusText / countsText: %s | %s" % (st_txt[:90], ct_txt[:90]))
    lb = []
    br.put("class:" + str(U1), "Archer")
    br.put("class:list", "Warrior:Swordsmanship,Archer:Archery")
    br.put("class:weapons:Archer", "Weapon_Shortbow_,Weapon_Crossbow_")
    lb.append(list(Loot.lean(U1) or []))
    br.put("class:list", "Warrior:Swordsmanship")
    lb.append(Loot.lean(U1))
    br.remove("class:" + str(U1))
    lb.append(Loot.lean(U1))
    K.check(lb[0] == ["Weapon_Shortbow_", "Weapon_Crossbow_"] and lb[1] is None and lb[2] is None,
            "X8: lean(): the killer's ENABLED class weapon prefixes, none for a disabled class / no class")

    # ============================================================================ X9 GearBoxFn + gear:fn:* + /gear box
    bf = BoxFn()
    o1 = bf.apply(JArray(JObject)([None, JInt(15), "lootchest", JInt(4), U1]))
    o2 = bf.apply(JArray(JObject)(["Weapon_Sword", JInt(15), "lootchest", JInt(1), None]))
    o3 = bf.apply(JArray(JObject)(["NoSuchType", JInt(15), "x", JInt(1), None]))
    o4 = bf.apply(JArray(JObject)([stack("Armor_Cloth_Silk_Chest"), JInt(22), "lootchest", JInt(2), U1]))
    o5 = bf.apply(JArray(JObject)([stack("Weapon_Spear_Iron", 2), JInt(22), "x", JInt(2), U1]))
    o6 = bf.apply("nonsense")
    o7 = bf.apply(JArray(JObject)([None, JInt(0), "x", JInt(1), None]))
    K.check(Unid.isBox(o1.getItemId()) and int(bagdoc(o1).getInt32("tier").getValue()) == 4 and str(bagdoc(o2).getString("mys").getValue()) == "Weapon_Sword"
            and o3 is None and str(bagdoc(o4).getString("mys").getValue()) == "Armor_Chest" and str(bagdoc(o4).getString("at").getValue()) == "Cloth"
            and o5 is None and o6 is None and o7 is None,
            "X9: gear:fn:box: a random bag (tier 4), a forced type, an unknown type refused, a vanilla Silk chestplate -> a Cloth chestplate bag, a "
            "stack refused, bad arguments refused")
    t4 = collections.Counter(int(Unid.rarity(JInt(2), JInt(21))) for _ in range(20000))
    t1 = collections.Counter(int(Unid.rarity(JInt(2), JInt(0))) for _ in range(20000))
    K.check(t4[0] < t1[0], "X9: luggage tier IV shifts the Chest odds up (Normal %d vs %d of 20000)" % (t4[0], t1[0]))
    fnd, fnr, fnl, fni, fns = Fn(JInt(0)), Fn(JInt(2)), Fn(JInt(3)), Fn(JInt(4)), Fn(JInt(5))
    K.check(list(fnd.apply(bags[3]))[0] == "Unidentified Sword" and str(fnr.apply(bags[3])) == "legendary" and int(fnl.apply(bags[3])) == 41
            and not bool(fni.apply(bags[3])) and "|bag|" in str(fns.apply(bags[3])),
            "X9: gear:fn:describe / rarity / level / identified / sig answer for a bag (the AH and other mods)")
    inv3, cs3 = mkinv()
    try:
        tg_ = Unid.make(JInt(ti["Weapon_Sword"]), JInt(0), JInt(0), JInt(5), JInt(9), "t", "t", JInt(0))
        print("X9 debug: give() ->", Admin.give(inv3, tg_), "roll ->", Unid.roll(JInt(30), JInt(ti["Weapon_Shortbow"]), "admin", "admin", JInt(0), None, JInt(1), JInt(0)))
        for i in range(36):
            cs3["storage"].setItemStackForSlot(JShort(i), None)
    except Exception as e_:
        print("X9 debug: give failed", e_)
    try:
        Admin.boxCmd(prx, inv3, "rare 30 bow")
    except Exception as e_:
        print("X9 debug: boxCmd threw", e_)
    Admin.boxCmd(prx, inv3, "nonsense")
    Admin.boxCmd(prx, inv3, "")
    Admin.lootCmd(prx)
    gb = [cs3["storage"].getItemStack(JShort(i)) for i in range(36)]
    gb = [g_ for g_ in gb if g_ is not None and not g_.isEmpty()]
    gbh = [cs3["hotbar"].getItemStack(JShort(i)) for i in range(9)]
    print("X9 debug: storage %s hotbar %s" % ([str(g_.getItemId()) + " " + str(Unid.logText(g_)) for g_ in gb],
                                             [str(g_.getItemId()) for g_ in gbh if g_ is not None and not g_.isEmpty()]))
    K.check(len(gb) == 1 and str(gb[0].getItemId()) == "Skyy_Unid_Bag_Rare" and str(bagdoc(gb[0]).getString("mys").getValue()) == "Weapon_Shortbow"
            and int(bagdoc(gb[0]).getInt32("lo").getValue()) <= 30 <= int(bagdoc(gb[0]).getInt32("hi").getValue()),
            "X9: /gear box rare 30 bow -> a Rare bow bag around Lv 30 in storage (storage first); a bad rarity / no args give nothing; /gear loot runs")

    # ============================================================================ X10 the systems on stand-in ECS parts
    # GearDeathMark.tick: the DropDeathItems condition, the mark WITH the level, the extra roll
    ILM = JClass("com.hypixel.hytale.server.core.asset.type.gameplay.DeathConfig$ItemsLossMode")
    NPCE = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    ROLE = JClass("com.hypixel.hytale.server.npc.role.Role")
    DM = P("GearDeathMark")
    dmk = DM(False)
    npc = us.allocateInstance(NPCE.class_)
    role = us.allocateInstance(ROLE.class_)
    jf(NPCE, "role").set(npc, role)
    try:
        jf(ROLE, "dropDeathItemsInstantly").setBoolean(role, True)
    except Exception:
        pass
    tcomp = us.allocateInstance(TC.class_)
    jf(TC, "position").set(tcomp, V3(JDouble(100.0), JDouble(64.0), JDouble(100.0)))
    dc = death(src_ok)
    jf(DTH, "itemsLossMode").set(dc, ILM.ALL)
    JClass(FAKE_PKG + ".FakeUtil").mapType("com.hypixel.hytale.server.core.modules.entity.EntityModule", "classToComponentType",
                                           "com.hypixel.hytale.server.npc.entities.NPCEntity")
    npc_type = NPCE.getComponentType()
    m_ = IHM()
    m_.put(DTH.getComponentType(), dc)
    m_.put(npc_type, npc)
    m_.put(TC.getComponentType(), tcomp)
    m_.put(UUIDC.getComponentType(), uuidc(UUID.randomUUID()))
    m_.put(HRC.getComponentType(), headrot())
    chunk.comps = m_
    ES = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
    wld = us.allocateInstance(WLD.class_)
    jf(WLD, "name").set(wld, "testworld")
    es = us.allocateInstance(ES.class_)
    jf(ES, "world").set(es, wld)
    st.ext = es
    Tag.MARKS.clear()
    Loot.HOUR.clear()
    Cfg.LOOT_MOB_PCT = 100.0
    sp0 = len(SPAWNED)
    LEVEL["lv"] = 37
    dmk.tick(JFloat(0.05), JInt(0), chunk, st, buf)
    defaults()
    K.check(int(Tag.levelNear("testworld", JDouble(100.0), JDouble(65.0), JDouble(100.0))) == 37 and len(SPAWNED) == sp0 + 1
            and int(bagdoc(SPAWNED[-1][0]).getInt32("lo").getValue()) <= 37,
            "X10: GearDeathMark.tick: the death mark carries the mob's level (37) and the extra roll spawned one bag")
    # GearDropSys.onEntityAdded: a dropped vanilla sword next to the mark becomes a bag at the mark's level
    DSYS = P("GearDropSys")
    ITC = JClass("com.hypixel.hytale.server.core.modules.entity.item.ItemComponent")
    ADDR = JClass("com.hypixel.hytale.component.AddReason")
    ic = ITC(stack("Weapon_Mace_Iron"))
    dref = us.allocateInstance(REFc.class_)
    jf(REFc, "index").setInt(dref, JInt(11))
    tcd = us.allocateInstance(TC.class_)
    jf(TC, "position").set(tcd, V3(JDouble(100.2), JDouble(65.0), JDouble(100.1)))
    dmp = IHM()
    dmp.put(ITC.getComponentType(), ic)
    dmp.put(TC.getComponentType(), tcd)
    st.comps.put(dref, dmp)
    DSYS().onEntityAdded(dref, ADDR.SPAWN, st, buf)
    got_ = ic.getItemStack()
    K.check(Unid.isBox(got_.getItemId()) and str(bagdoc(got_).getString("mys").getValue()) == "Weapon_Mace" and int(bagdoc(got_).getInt32("lo").getValue()) == 35,
            "X10: GearDropSys.onEntityAdded: the mob's own mace drop -> a mace bag Lv 35-39 (the death mark's level 37)")
    # GearChestTag.onEntityAdded: after the stash roll - level, bags, the extra bag only after a real fill (the drop list cleared)
    ICBc = JClass("com.hypixel.hytale.server.core.modules.block.components.ItemContainerBlock")
    CHT = P("GearChestTag")
    icb = us.allocateInstance(ICBc.class_)
    cont = SIC(JShort(9))
    cont.setItemStackForSlot(JShort(0), stack("Armor_Iron_Legs"))
    jf(ICBc, "itemContainer").set(icb, cont)
    cref = us.allocateInstance(REFc.class_)
    jf(REFc, "index").setInt(cref, JInt(12))
    cm_ = IHM()
    cm_.put(ICBc.getComponentType(), icb)
    st.comps.put(cref, cm_)
    Tag.chestMark(cref, "Zone2_Encounters_Tier1")
    Cfg.LOOT_CHEST_PCT = 100.0
    CHT(False).onEntityAdded(cref, ADDR.SPAWN, st, buf)
    cids = [str(cont.getItemStack(JShort(i)).getItemId()) for i in range(9) if cont.getItemStack(JShort(i)) is not None and not cont.getItemStack(JShort(i)).isEmpty()]
    lvls = [int(bagdoc(cont.getItemStack(JShort(i))).getInt32("lo").getValue()) for i in range(9) if cont.getItemStack(JShort(i)) is not None and not cont.getItemStack(JShort(i)).isEmpty()]
    defaults()
    K.check(len(cids) == 2 and all(x.startswith("Skyy_Unid_Bag_") for x in cids) and all(18 <= l_ <= 30 for l_ in lvls),
            "X10: GearChestTag: the iron legs -> a bag at the Zone 2 level + the 33 %% extra bag (forced 100 %%) after a real fill: %s %s" % (cids, lvls))
    cont2 = SIC(JShort(9))
    jf(ICBc, "itemContainer").set(icb, cont2)
    jf(ICBc, "droplist").set(icb, "Zone2_Encounters_Tier1")
    Tag.chestMark(cref, "Zone2_Encounters_Tier1")
    Cfg.LOOT_CHEST_PCT = 100.0
    CHT(False).onEntityAdded(cref, ADDR.SPAWN, st, buf)
    defaults()
    K.check(all(cont2.getItemStack(JShort(i)) is None or cont2.getItemStack(JShort(i)).isEmpty() for i in range(9)),
            "X10: GearChestTag: the drop list was NOT cleared (no real fill) -> no extra bag")
    Loot.SPAWN = None
    K.save()


# ====================================================================================================== C: class compare
def run_compare(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_
    pa, pb = pool_of(OLD_JAR), pool_of(JAR)
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def members(p_, cn):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature())
        def code(b_):
            mi_ = b_.getMethodInfo()
            ca_ = mi_.getCodeAttribute()
            if ca_ is None:
                return ""
            it_ = ca_.iterator()
            cpl_ = mi_.getConstPool()
            lines_ = []
            while it_.hasNext():
                pos_ = it_.next()
                lines_.append(re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, cpl_))))
            return "\n".join(lines_)
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_
    na, nb = jar_classes(OLD_JAR), jar_classes(JAR)
    added = sorted(c[len(PKG):] for c in set(nb) - set(na))
    removed = sorted(set(na) - set(nb))
    K.check(added == NEW_CLASSES and not removed, "C: classes added %s, removed %s" % (added, removed))
    diffs = {}
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn), members(pb, cn)
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(PKG):]] = [("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd]
    EXPECT = {"CfgFile", "CfgFn", "CfgRows", "Gear", "GearAdmin", "GearCfg", "GearChestTag", "GearCmd", "GearDeathMark", "GearDefs", "GearDropSys",
              "GearFn", "GearForge", "GearIdent", "GearTag", "IdentifyPage", "SkyyGearPlugin", "GearLevel", "GearRoll", "GearView"}
    unexpected = sorted(set(diffs) - EXPECT)
    print("C. class compare 0.2.10 -> 0.2.11:")
    for k in sorted(diffs):
        print("   %-16s %s" % (k, ", ".join(diffs[k])[:300]))
    K.check(not unexpected, "C: only the loot round's classes differ (unexpected: %s)" % {k: diffs[k] for k in unexpected})
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    ea = [n for n in za.namelist() if not n.endswith(".class")]
    eb = [n for n in zb.namelist() if not n.endswith(".class")]
    ed = sorted(n for n in set(ea) | set(eb) if n not in ea or n not in eb or za.read(n) != zb.read(n))
    allowed = [n for n in ed if n.startswith(("Common/Icons/ItemsGenerated/Skyy_Unid_Bag_", "Common/Items/SkyyGear/Unid/Bag_", "Server/Item/Items/SkyyGear/Skyy_Unid_Bag_"))
               or n in ("manifest.json", "Server/Languages/en-US/server.lang")]
    K.check(ed == allowed and len(ed) == 7 * 3 + 2, "C: non-class entries changed = the 7 bag items + icons + textures, the lang file, the manifest: %d %s" % (len(ed), [n for n in ed if n not in allowed]))
    la, lb = za.read("Server/Languages/en-US/server.lang").decode(), zb.read("Server/Languages/en-US/server.lang").decode()
    K.check(lb.startswith(la) and lb[len(la):].count("Mystery Bag") == 7, "C: the lang file only gains the 14 bag lines")
    K.save(diffs=diffs)


# ====================================================================================================== P: permissions
def run_perm(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR], verify=True)
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fld = AC.class_.getDeclaredField("permissionGroups")
    fld.setAccessible(True)
    for cn in ("GearBoxCmd", "GearLootCmd"):
        c = JClass(PKG + cn)()
        perm, groups = c.getPermission(), [str(g) for g in (fld.get(c) or [])]
        K.check(perm is not None and "skyygear.admin" in str(perm) and groups == [], "P: %s requires skyygear.admin with no groups (%s, %s)" % (cn, perm, groups))
    root = JClass(PKG + "GearCmd")()
    subs = [str(x) for x in root.getSubCommands().keySet()] if hasattr(root, "getSubCommands") else []
    K.check(not subs or ("box" in subs and "loot" in subs), "P: /gear has box + loot: %s" % subs)
    rec = root.getPermissionGroupsRecursive()
    leak = [str(k) for k in rec.keySet() if rec.get(k) is not None and any("skyygear.admin" in str(x) for x in rec.get(k))]
    K.check(not leak, "P: skyygear.admin is given to no group (leak %s)" % leak)
    K.save()


# ====================================================================================================== D: start twice on a live copy
def run_live(out, home):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR], verify=True)
    Cfg = JClass(PKG + "GearCfg")
    Path = JClass("java.nio.file.Paths")
    Cfg.DIR = Path.get(home)
    Cfg.FILE = Path.get(os.path.join(home, "config.properties"))
    JClass(PKG + "GearLog").FILE = Path.get(os.path.join(home, "gear.log"))
    before = open(os.path.join(home, "config.properties"), "rb").read()
    for step in (1, 2):
        for m in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025"):
            getattr(Cfg, m)()
        Cfg.load()
        after = open(os.path.join(home, "config.properties"), "rb").read()
        K.check(after == before, "D start %d: the live config.properties copy is byte-identical (the loot keys need no one-time update)" % step)
        K.check(float(Cfg.LOOT_MOB_PCT) == 6.0 and bool(Cfg.UNID_BAGS) and int(Cfg.REROLL_MAX) == 3,
                "D start %d: the loot rows read their defaults from a file without them (6 %%, bags on, 3 re-identifies)" % step)
    txt = before.decode("utf-8", "replace")
    K.check("loot.mob.chance" not in txt and "loot." not in txt.replace("loot chests", ""),
            "D: the live file has NO loot line - the planned 4 %% never shipped, so there is nothing to migrate to 6 %%")
    K.save()


# ====================================================================================================== AA: access audit
def run_audit(out):
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
                            cname, name, desc = (str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)), str(cp.getInterfaceMethodrefType(idx)))
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
                        except Exception:
                            ok_ = False
                    if not ok_:
                        refused.append("%s: %s" % (where, ex_))
        return refused, n
    names = jar_classes(JAR)
    res = {"classes": len(names), "refs": 0, "refused": []}
    for cn in names:
        try:
            r_, k_ = lookup_audit(cn)
        except Exception as ex_:
            r_, k_ = ["%s: could not audit: %s" % (cn, ex_)], 0
        res["refused"] += r_
        res["refs"] += k_
    res["control"] = lookup_audit(FAKE_PKG + ".BadAccess")[0]
    json.dump(res, open(out, "w"), indent=1)


# ====================================================================================================== parent
def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR], env=env)


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
    for flag, fn in (("--carried", run_carried), ("--run", run_carried), ("--mkfake", lambda: run_mkfake(arg("--mkfake"))), ("--verify", lambda: run_verify(arg("--out"))),
                     ("--engine", lambda: run_engine(arg("--out"))), ("--compare", lambda: run_compare(arg("--out"))),
                     ("--perm", lambda: run_perm(arg("--out"))), ("--live", lambda: run_live(arg("--out"), arg("--live"))),
                     ("--audit", lambda: run_audit(arg("--out")))):
        if flag in sys.argv:
            try:
                fn()
            except SystemExit:
                raise
            except Exception:
                import traceback
                traceback.print_exc()
                sys.exit(1)
            return
    assert os.path.isfile(JAR), JAR
    assert os.path.isfile(OLD_JAR), OLD_JAR
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(os.path.join(TOOLS, "dev", "scratch", "loot01fix")) + os.sep), "the scratch folder must be inside tools/dev/scratch/loot01fix"
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        if "--skip-carried" not in sys.argv:
            print("R. the carried 0.2.10 harness on the 0.2.11 jar ...")
            pr = subprocess.run([sys.executable, os.path.abspath(__file__), "--carried", "--jar", JAR], env=env)
            check(pr.returncode == 0, "R: the carried 0.2.10 harness passes on the 0.2.11 jar with only the listed deviations (exit %s)" % pr.returncode)
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        for label, flag in (("verify", "--verify"), ("engine", "--engine"), ("compare", "--compare"), ("perm", "--perm")):
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        home = os.path.join(SCRATCH, "live")
        shutil.copytree(LIVE_DIR, home)
        print("D. live Skyy_SkyyGear copied (read-only source %s)" % LIVE_DIR)
        out = os.path.join(SCRATCH, "live.json")
        pr = child(env, "--live", home, "--out", out)
        check(pr.returncode == 0, "D: the child exited cleanly")
        take(out, "live")
        outa = os.path.join(SCRATCH, "audit.json")
        pa = child(env, "--audit", "--out", outa)
        check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            check(not a["refused"] and a["refs"] > 10000, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: the control is refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, 0 refused, control refused" % (a["refs"], a["classes"]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
