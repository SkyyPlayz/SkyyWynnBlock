"""Harness for SkyyWardrobe 0.1 (NEW mod: loadouts of armor + hotbar + pets + abilities). Build first:
    python SkyyWardrobe/build_skyywardrobe_0.1.py
    python SkyyWardrobe/test_skyywardrobe_0.1.py [--jar <SkyyWardrobe-0.1.jar>] [--dir <scratch>] [--live <world mods folder>] [--keep]

Parent (plain Python, read only): J the jar (manifest, exactly the expected classes, no asset / .ui / lang file).
Children (fresh JVMs, the game's own JRE, -Xverify:all, -XX:-UsePerfData, java.io.tmpdir in scratch; HytaleServer.jar on the class path):
  F  stand-ins compiled with javassist: FakePr (a PlayerRef), MapStore (a Store: components + one resource), TestPage (WdPage with
     rebuild / close counted), FlakyBox (a SimpleItemContainer whose set can be made to fail), TestPM (a PageManager), LookupIn / BadAccess
  A  every class of the jar loads, verifies (-Xverify:all) and initialises
  X  EVERY NEW CODE PATH on REAL engine containers (SimpleItemContainer, ItemStack with metadata, the real ItemStack.CODEC, an empty
     item asset map) with the REAL component lookups (EntityModule / DamageModule / Universe / TimeResource primed by reflection: the
     real InventoryComponent$Armor / $Hotbar / $Storage / $Backpack, DeathComponent, DamageDataComponent, TimeResource):
     config (seed, every row, both check= hooks, keep ids, the kit's config:fn set / get / reload), slots (free, Overall Level through
     skill:fn:overall and skill:overall:<uuid>, the admin floor, slots.max, lockText, shown), SAVE CURRENT (link + pets + abilities,
     refused while another loadout is equipped / on a loadout that stores gear), EQUIP (home rule, strict return, keep rule without an
     equipped loadout, the SkyWynn Menu item never moved / stored, partial loadouts, the bridge calls + every missing / failing bridge
     note), CLEAR (storage first, inventory full, the equipped one only unlinks, the ask-twice on the page), RENAME (sanitising),
     the refusals (dead, combat, busy, after a profile switch, the gap, one at a time), a STORED ITEM THAT NO LONGER EXISTS, an
     UNDECODABLE stack (orphan, kept, retried), a SAVE FAILURE (rolled back), a PUT FAILURE (rolled back) and a ROLLBACK FAILURE (locked;
     /wardrobeadmin repair unlocks it), CRASH BETWEEN STEPS (equip and clear: after 0 / 1 / some / all moves and after the save, each
     with the live inventory as it was at the crash AND rolled back to before the change; the next "start" repairs from the journal),
     PROFILE SWITCH MID-SWAP (one key per operation; a journal of profile 1 is never repaired against profile 2's inventory), PER-PROFILE
     ISOLATION, unreadable / newer-format files (shut, never written), the page (build + every click + the stale token + close),
     the commands (every player / admin form), wardrobe:fn:open, the join repair (PlayerReadyEvent -> scheduler -> world task, waiting
     for profile:busy), the disconnect cleanup, the 1 s timer (epochs + the journal keep window), the plugin shutdown pieces.
     FIXER ROUND (X27-X36): CHAINED crashes (two / three changes inside one journal window, live rolled back to each stage, an
     exception inside the second change), NO epoch rule (an epoch bump without a save is repaired; a switch away and back
     replays to no change), a failed repair save stops the op, the timer never deletes
     a moving / failed journal, Clear while switched off, displaced pieces parked (reachable), the pets / abilities you leave are kept
     with that loadout, swap.strict off (the LOCKED keep rule) vs on, Save current greyed where it would be refused, the hint text.
     FIXER 2 (X37-X40): swapped-in / cleared stacks eaten from or moved inside the window then a crash (no dupe), an admin repair of
     a saved change of this run (nothing), a failed move whose own slot cannot be restored (locked, then repaired), unreadable
     armor / hotbar during a repair (journal kept).
     After every item operation: ITEM CONSERVATION - the multiset of every stack (live armor + hotbar + storage + backpack + every
     loadout in the FILE + orphans) equals the one before; nothing doubled, nothing lost.
  P  /wardrobe (aliases loadout, loadouts, wd) + its 3 usage variants = hytale:Adventurer; /wardrobeadmin + 3 variants require
     skyywardrobe.admin with empty permission groups (no group leak)
  B  BYTECODE: setup() order (config, scan, kit, bridge fn, 2 commands, 2 events, the timer; no ECS system); the swap writes only through
     setItemStackForSlot(short, ItemStack, boolean=false) / removeItemStackFromSlot(short, boolean=false); no ItemGridSlot anywhere
  AA THE ENGINE-ACCESS AUDIT (MethodHandles.privateLookupIn every class; every engine member it references must be accessible)
  D  START TWICE on a scratch COPY of the live world mods folder: only Skyy_SkyyWardrobe/config.properties appears; start 2 writes nothing
  C  CLASS COMPARE: new mod - no older SkyyWardrobe exists; the class list is the expected list (J)
Scratch: tools/dev/scratch/wardrobe01/test (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, hashlib, time, re

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


JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyWardrobe-%s.jar" % VERSION)))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "wardrobe01", "test")))
FAKE_DIR = os.path.join(SCRATCH, "fake")
FAKE_PKG = "skyywdtest"
MAPSTORE = "com.hypixel.hytale.component.SkyyWdTestStore"
TESTPM = "com.hypixel.hytale.server.core.entity.entities.player.pages.SkyyWdTestPM"
PKG = "com.skyy.wardrobe."
NODE = "skyywardrobe.admin"
OURS = ["WdLog", "WdApi", "WdInvApi", "WdEng", "WdCfg", "WdCodec", "WdLoad", "WdData", "WdStore", "WdJournal", "WdSlots", "WdBridge", "WdTx",
        "WdGate", "WdOps", "WdPage", "WdRepairTask", "WdHop", "WdOpenTask", "WdFloorTask", "WdOpenFn", "WdTimer", "WdReady", "WdQuit", "WdCmds",
        "WdArg1Cmd", "WdArg2Cmd", "WdArg3Cmd", "WdCmd", "WdAdminArg1Cmd", "WdAdminArg2Cmd", "WdAdminArg3Cmd", "WdAdminCmd", "SkyyWardrobePlugin"]
KITC = ["CfgFile", "CfgFn", "CfgHist", "CfgLog", "CfgPub", "CfgRows", "CfgSaveTask"]
CLASSES = sorted(PKG + c for c in OURS + KITC)
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


LIVE = os.path.abspath(arg("--live", os.path.join(B.USERDATA, "Saves", deploy_world(), "mods")))


def tree_hash(root):
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            out[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


# ====================================================================================================== children: shared
def _jvm(cp, verify=True):
    import jpype
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    opts = (["-Xverify:all"] if verify else []) + ["-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp]
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


def run_mkfake(out_dir):
    from jpype import JClass
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    P = FAKE_PKG

    def mk(name, sup=None):
        c = cp.makeClass(P + "." + name)
        if sup:
            c.setSuperclass(cp.get(sup))
        return c

    def F(c, s):
        c.addField(CtField.make(s, c))

    def M(c, s):
        c.addMethod(CtNewMethod.make(s, c))
    CR = "com.hypixel.hytale.component."
    ms = cp.makeClass(MAPSTORE)      # in the engine's package: Store's constructor is package-private
    ms.setSuperclass(cp.get(CR + "Store"))
    for d in ("java.util.Map comps", "java.lang.Object res", "java.lang.Object ext"):
        F(ms, "public %s;" % d)
    ms.addConstructor(CtNewConstructor.make("public MapStore() { super(null, 0, null, null); }", ms))
    M(ms, """public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  if (r == null || this.comps == null) return null;
  java.util.Map m = (java.util.Map) this.comps.get(r);
  return m == null ? null : (com.hypixel.hytale.component.Component) m.get(t);
}""")
    M(ms, "public com.hypixel.hytale.component.Resource getResource(com.hypixel.hytale.component.ResourceType t) { return (com.hypixel.hytale.component.Resource) this.res; }")
    M(ms, "public java.lang.Object getExternalData() { return this.ext; }")
    ms.writeFile(out_dir)
    fp = mk("FakePr", "com.hypixel.hytale.server.core.universe.PlayerRef")
    for d in ("java.util.List msgs", "java.util.UUID fu", "String fname", "com.hypixel.hytale.component.Ref fref", "java.util.UUID fworld"):
        F(fp, "public %s;" % d)
    fp.addConstructor(CtNewConstructor.make("public FakePr() { super((com.hypixel.hytale.component.Holder) null, (java.util.UUID) null, (String) null, (String) null, (com.hypixel.hytale.server.core.io.PacketHandler) null, (com.hypixel.hytale.server.core.modules.entity.player.ChunkTracker) null); }", fp))
    M(fp, "public java.util.UUID getUuid() { return this.fu; }")
    M(fp, "public String getUsername() { return this.fname; }")
    M(fp, "public com.hypixel.hytale.component.Ref getReference() { return this.fref; }")
    M(fp, "public java.util.UUID getWorldUuid() { return this.fworld; }")
    M(fp, "public void sendMessage(com.hypixel.hytale.server.core.Message m) { if (this.msgs == null) this.msgs = new java.util.ArrayList(); this.msgs.add(m == null ? \"null\" : m.getRawText()); }")
    fp.writeFile(out_dir)
    tp = mk("TestPage", PKG + "WdPage")
    F(tp, "public int rebuilds;")
    F(tp, "public int closes;")
    tp.addConstructor(CtNewConstructor.make("public TestPage(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr); }", tp))
    M(tp, "public void rebuild() { this.rebuilds = this.rebuilds + 1; }")
    M(tp, "public void close() { this.closes = this.closes + 1; }")
    tp.writeFile(out_dir)
    IS, ISST = "com.hypixel.hytale.server.core.inventory.ItemStack", "com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction"
    fb = mk("FlakyBox", "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    F(fb, "public static int FAIL_AT = -1;")         # this many sets work, then ONE set does nothing (-1 = never)
    F(fb, "public static boolean FAIL_ALL = false;") # every set does nothing
    F(fb, "public static boolean STICKY = false;")   # the one failure switches FAIL_ALL on
    F(fb, "public static int SETS = 0;")
    fb.addConstructor(CtNewConstructor.make("public FlakyBox(short n) { super(n); }", fb))
    M(fb, ("public %s setItemStackForSlot(short s, %s i, boolean f) { SETS = SETS + 1; if (FAIL_ALL) return null; "
           "if (FAIL_AT == 0) { FAIL_AT = -1; if (STICKY) FAIL_ALL = true; return null; } if (FAIL_AT > 0) FAIL_AT = FAIL_AT - 1; "
           "return super.setItemStackForSlot(s, i, f); }") % (ISST, IS))
    fb.writeFile(out_dir)
    PP = "com.hypixel.hytale.server.core.entity.entities.player.pages."
    pm = cp.makeClass(TESTPM)        # in the engine's package (the PageManager constructor)
    pm.setSuperclass(cp.get(PP + "PageManager"))
    F(pm, "public static java.lang.Object CUR = null;")
    F(pm, "public static int OPENS = 0;")
    pm.addConstructor(CtNewConstructor.make("public TestPM() { super(); }", pm))
    M(pm, "public void openCustomPage(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.Store s, %sCustomUIPage p) { CUR = p; OPENS = OPENS + 1; }" % PP)
    M(pm, "public %sCustomUIPage getCustomPage() { return (%sCustomUIPage) CUR; }" % (PP, PP))
    pm.writeFile(out_dir)
    ta = mk("TestAssets", "com.hypixel.hytale.assetstore.AssetStore")
    ta.addConstructor(CtNewConstructor.make("public TestAssets() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", ta))
    ta.writeFile(out_dir)
    lk = mk("LookupIn")
    M(lk, "public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
          "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}")
    lk.writeFile(out_dir)
    ba = mk("BadAccess")
    M(ba, "public static void send(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) {\n"
          "  p.sendUpdate(new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder());\n}")
    ba.writeFile(out_dir)
    print("F. stand-ins written to", out_dir)


# ====================================================================================================== the engine stand-in
class Eng(object):
    """Unsafe-allocated engine singletons, primed so the REAL getComponentType() / getResourceType() lookups answer."""

    def __init__(self):
        from jpype import JClass
        self.J = JClass
        uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
        uf.setAccessible(True)
        self.U = uf.get(None)
        self.CP = JClass("javassist.ClassPool")(False)
        self.CP.appendSystemPath()
        self.CP.appendClassPath(B.SERVER_JAR)
        self.IP = JClass("javassist.bytecode.InstructionPrinter")

    def jf(self, c, n):
        k = c.class_ if hasattr(c, "class_") else c
        while k is not None:
            try:
                f = k.getDeclaredField(n)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(n)

    def code(self, cls, meth):
        cc = self.CP.get(cls)
        m = [x for x in cc.getDeclaredMethods() if str(x.getName()) == meth][0]
        ca = m.getMethodInfo().getCodeAttribute()
        it, cp, out = ca.iterator(), m.getMethodInfo().getConstPool(), []
        while it.hasNext():
            out.append(str(self.IP.instructionString(it, it.next(), cp)))
        return out

    def field_of(self, cls, getter):
        """the field a plain getter (getfield X.f / getstatic X.f) returns"""
        for l in self.code(cls, getter):
            m = re.search(r"(getfield|getstatic) #\d+ = Field ([\w.$]+)\.(\w+)\(", l)
            if m:
                return m.group(2), m.group(3)
        raise KeyError("%s.%s" % (cls, getter))

    def singleton(self, cls):
        """Mod.get() -> its static instance (allocated once)"""
        c2, f = self.field_of(cls, "get")
        K = self.J(c2)
        fld = self.jf(K, f)
        o = fld.get(None)
        if o is None:
            o = self.U.allocateInstance(K.class_)
            fld.set(None, o)
        return o

    def prime(self, cls, getter, value):
        """make the real cls.getter() (Module.get().getX()) answer value"""
        lines = self.code(cls, getter)
        mod = None
        for l in lines:
            m = re.search(r"invokestatic #\d+ = Method ([\w.$]+)\.get\(\(\)", l)
            if m:
                mod = m.group(1)
            m2 = re.search(r"invokevirtual #\d+ = Method ([\w.$]+)\.(\w+)\(\(\)", l)
            if m2 and mod:
                inst = self.singleton(mod)
                c2, f = self.field_of(m2.group(1), m2.group(2))
                self.jf(self.J(c2), f).set(inst, value)
                return value
        raise KeyError("%s.%s" % (cls, getter))


def boot(K, scratch_mods):
    """the bare engine + the mod's statics pointed at a scratch mods folder; returns a dict of handles"""
    from jpype import JClass, JImplements, JOverride, JArray, JString
    E = Eng()
    U = E.U
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "universe")]))
    # the item asset store: an empty map so ItemStack constructors run (the SkyyGear / SkyyVault harness pattern)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    st0 = U.allocateInstance(JClass(FAKE_PKG + ".TestAssets").class_)
    E.jf(AS, "assetMap").set(st0, JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")())
    E.jf(JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item"), "ASSET_STORE").set(None, st0)
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    E.jf(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    E.jf(HS, "instance").set(None, hs)
    CHM, COLL = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.Collections")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu, wmap, wbu = CHM(), CHM(), CHM()
    for n, v in (("playersByUuid", pbu), ("players", COLL.unmodifiableCollection(pbu.values())), ("worlds", wmap), ("worldsByUuid", wbu),
                 ("unmodifiableWorlds", COLL.unmodifiableMap(wmap))):
        E.jf(UNI, n).set(uni, v)
    E.jf(UNI, "instance").set(None, uni)
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    types = {}
    for key, cls, getter in (("pr", "com.hypixel.hytale.server.core.universe.PlayerRef", "getComponentType"),
                             ("pla", "com.hypixel.hytale.server.core.entity.entities.Player", "getComponentType"),
                             ("arm", "com.hypixel.hytale.server.core.inventory.InventoryComponent$Armor", "getComponentType"),
                             ("hot", "com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar", "getComponentType"),
                             ("sto", "com.hypixel.hytale.server.core.inventory.InventoryComponent$Storage", "getComponentType"),
                             ("bak", "com.hypixel.hytale.server.core.inventory.InventoryComponent$Backpack", "getComponentType"),
                             ("death", "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent", "getComponentType"),
                             ("ddc", "com.hypixel.hytale.server.core.entity.damage.DamageDataComponent", "getComponentType")):
        if key == "pr":
            types[key] = CT()
            E.jf(UNI, "playerRefComponentType").set(uni, types[key])
            continue
        types[key] = E.prime(cls, getter, CT())
    RT = JClass("com.hypixel.hytale.component.ResourceType")
    types["time"] = E.prime("com.hypixel.hytale.server.core.modules.time.TimeResource", "getResourceType", RT())
    # one world whose execute() queues the task (drained by the harness = "the world thread")
    World = JClass("com.hypixel.hytale.server.core.universe.world.World")
    world = U.allocateInstance(World.class_)
    Q = JClass("java.util.concurrent.LinkedBlockingDeque")()
    E.jf(World, "acceptingTasks").set(world, JClass("java.util.concurrent.atomic.AtomicBoolean")(True))
    E.jf(World, "taskQueue").set(world, Q)
    E.jf(World, "name").set(world, "wardrobetest")
    UUID = JClass("java.util.UUID")
    WU = UUID.fromString("00000000-0000-0000-0000-0000000000d1")
    wbu.put(WU, world)
    wmap.put("wardrobetest", world)
    br = CHM()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    P = lambda n: JClass(PKG + n)
    lines = JClass("java.util.ArrayList")()
    P("WdLog").LINES = lines
    Paths = JClass("java.nio.file.Paths")
    P("WdCfg").load(Paths.get(scratch_mods))
    P("WdStore").ROOT = Paths.get(scratch_mods).resolve("Skyy_SkyyWardrobe")
    P("WdStore").DIR = P("WdStore").ROOT.resolve("loadouts")
    P("WdStore").LOGF = P("WdStore").ROOT.resolve("wardrobe.log")
    return {"E": E, "U": U, "uni": uni, "pbu": pbu, "types": types, "world": world, "Q": Q, "WU": WU, "br": br, "lines": lines}


def drain(H):
    n = 0
    while not H["Q"].isEmpty():
        t = H["Q"].poll()
        t.run()
        n += 1
    return n


# ====================================================================================================== child X
def run_x(out):
    from jpype import JClass, JImplements, JOverride, JArray, JObject, JString, JInt, JShort, JLong, JByte
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR])
    mods = os.path.join(SCRATCH, "x-mods")
    shutil.rmtree(mods, ignore_errors=True)
    os.makedirs(mods)
    H = boot(K, mods)
    E, U, types, br = H["E"], H["U"], H["types"], H["br"]
    P = lambda n: JClass(PKG + n)
    Cfg, Store, Tx, Ops, Gate, Jr, Slots, Brg, Codec = (P("WdCfg"), P("WdStore"), P("WdTx"), P("WdOps"), P("WdGate"), P("WdJournal"), P("WdSlots"),
                                                       P("WdBridge"), P("WdCodec"))
    UUID, IS, BD = JClass("java.util.UUID"), JClass("com.hypixel.hytale.server.core.inventory.ItemStack"), JClass("org.bson.BsonDocument")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    Flaky = JClass(FAKE_PKG + ".FlakyBox")
    MapStore, FakePr = JClass(MAPSTORE), JClass(FAKE_PKG + ".FakePr")
    AL, HM, IdM = JClass("java.util.ArrayList"), JClass("java.util.HashMap"), JClass("java.util.IdentityHashMap")
    INV = "com.hypixel.hytale.server.core.inventory.InventoryComponent$"
    Arm, Hot, Sto, Bak = JClass(INV + "Armor"), JClass(INV + "Hotbar"), JClass(INV + "Storage"), JClass(INV + "Backpack")
    RefC = JClass("com.hypixel.hytale.component.Ref")
    Player = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    TestPM = JClass(TESTPM)
    Inst = JClass("java.time.Instant")
    TR = JClass("com.hypixel.hytale.server.core.modules.time.TimeResource")
    DDC = JClass("com.hypixel.hytale.server.core.entity.damage.DamageDataComponent")
    Death = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")

    def stack(i, q=1, meta=None):
        return IS(i, q, 100.0, 100.0, 0, BD.parse(meta) if meta else None)

    class Player_(object):
        """one test player: real containers inside real InventoryComponents in a MapStore, a FakePr, a Ref, a Player with a TestPM"""

        def __init__(self, uid, name, flaky=False):
            self.u = UUID.fromString(uid)
            self.arm = Flaky(JShort(4)) if flaky else SIC(JShort(4))
            self.hot, self.sto, self.bak = SIC(JShort(9)), SIC(JShort(36)), SIC(JShort(9))
            self.st = MapStore()
            self.st.comps = IdM()
            self.ref = U.allocateInstance(RefC.class_)
            E.jf(RefC, "store").set(self.ref, self.st)
            self.pr = FakePr()
            self.pr.fu, self.pr.fname, self.pr.fref, self.pr.fworld = self.u, name, self.ref, H["WU"]
            self.pla = U.allocateInstance(Player.class_)
            E.jf(Player, "pageManager").set(self.pla, TestPM())
            m = IdM()
            m.put(types["pr"], self.pr)
            m.put(types["pla"], self.pla)
            m.put(types["arm"], Arm(self.arm))
            m.put(types["hot"], Hot(self.hot, JByte(0)))
            m.put(types["sto"], Sto(self.sto))
            m.put(types["bak"], Bak(self.bak))
            self.st.comps.put(self.ref, m)
            tr = U.allocateInstance(TR.class_)
            E.jf(TR, "now").set(tr, Inst.now())
            self.st.res = tr
            H["pbu"].put(self.u, self.pr)

        def comps(self):
            return self.st.comps.get(self.ref)

        def live(self):
            out = []
            for c in (self.arm, self.hot, self.sto, self.bak):
                for i in range(int(c.getCapacity())):
                    s = c.getItemStack(JShort(i))
                    if s is not None and not s.isEmpty():
                        out.append(key_of(s))
            return out

        def said(self):
            return [str(x) for x in (self.pr.msgs or [])]

    def key_of(s):
        md = s.getMetadata()
        return (str(s.getItemId()), int(s.getQuantity()), "" if md is None or md.isEmpty() else str(md.toJson()))

    def file_stacks(k):
        d = Store.readFile(k, "")
        out = []
        for i in range(len(d.slots)):
            L = d.slots[i]
            for part in (0, 1):
                for s in L.arr(part):
                    if s is not None and not s.isEmpty():
                        out.append(key_of(s))
        for o in d.orphans:
            od = o.asDocument()
            s = Codec.stackOf(od)
            out.append(key_of(s) if s is not None else ("orphan", 0, str(od.toJson())))
        return out, d

    def everything(p, k):
        fs, _d = file_stacks(k)
        tot = {}
        for (i_, q_, m_) in p.live() + fs:
            tot[(i_, m_)] = tot.get((i_, m_), 0) + q_
        return sorted(tot.items())

    def run(p, op, n, a=None, ref=None):
        return str(Ops.run(p.pr, p.ref if ref is None else ref, p.st, op, n, a))

    def setc(c, i, s):
        c.setItemStackForSlot(JShort(i), s, False)

    def getc(c, i):
        s = c.getItemStack(JShort(i))
        return None if s is None or s.isEmpty() else key_of(s)

    def clear_gap():
        Gate.LAST.clear()

    # ---------------------------------------------------------------- the fake SkyyPets / SkyyClasses bridge functions
    calls = {"pets": [], "abil": []}
    state = {"pets": "pA|sA", "abil": "v=1;class=Mage;alt=A;p1=Meteor;p2=ManaBarrier;a1=FrostNova;a2=Starfall;n1=Meteor;n2=Mana Barrier;n3=Frost Nova;n4=Starfall;mods=",
             "petsres": "+Pet slot: Biscuit, summon slot: Skeleton.", "abilres": "+Abilities: /cast 1 Meteor."}

    @JImplements("java.util.function.Function")
    class PetsGet:
        @JOverride
        def apply(self, u):
            return state["pets"]

    @JImplements("java.util.function.Function")
    class PetsSet:
        @JOverride
        def apply(self, a):
            calls["pets"].append((str(a[0]), str(a[1]), str(a[2])))
            if not str(state["petsres"]).startswith("-"):
                state["pets"] = str(a[1]) + "|" + str(a[2])
            return state["petsres"]

    @JImplements("java.util.function.Function")
    class PetName:
        @JOverride
        def apply(self, a):
            return None if str(a[1]) == "gone" else "Pet-" + str(a[1])

    @JImplements("java.util.function.Function")
    class AbilGet:
        @JOverride
        def apply(self, u):
            return state["abil"]

    @JImplements("java.util.function.Function")
    class AbilSet:
        @JOverride
        def apply(self, a):
            calls["abil"].append(str(a[1]))
            if not str(state["abilres"]).startswith("-"):
                state["abil"] = str(a[1])
            return state["abilres"]

    @JImplements("java.util.function.Function")
    class Overall:
        @JOverride
        def apply(self, u):
            return JArray(JObject)([JInt(state.get("overall", 0)), JInt(0), JInt(0), JInt(0), JInt(0)])

    @JImplements("java.util.function.Function")
    class KeyFn:
        @JOverride
        def apply(self, u):
            return state.get("key", {}).get(str(u), str(u))

    def bridge_on(pets=True, abil=True):
        for k_, v_ in (("pets:fn:loadoutGet", PetsGet()), ("pets:fn:loadoutSet", PetsSet()), ("pets:fn:petName", PetName())):
            if pets:
                br.put(k_, v_)
            else:
                br.remove(k_)
        for k_, v_ in (("class:fn:loadoutGet", AbilGet()), ("class:fn:loadoutSet", AbilSet())):
            if abil:
                br.put(k_, v_)
            else:
                br.remove(k_)
    br.put("profile:fn:key", KeyFn())
    # the real item lookup (an empty asset map in a bare JVM = nothing exists), then the seam: every id exists unless listed
    K.check(not Codec.known("Weapon_Sword_Iron") and not Codec.known("") and not Codec.known(None), "X0 WdCodec.known: the REAL asset-map lookup (empty map -> gone)")
    Codec.UNKNOWN_IDS = JClass("java.util.HashSet")()

    try:
        # ============================================================ A: every class loads + verifies + initialises
        Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
        bad = []
        for cn in CLASSES:
            try:
                Cls.forName(cn, True, loader)
            except Exception as e:
                bad.append("%s: %s" % (cn, e))
        K.check(not bad, "A. every class loads, verifies (-Xverify:all) and initialises: %s" % bad)

        # ============================================================ config
        cfgf = os.path.join(mods, "Skyy_SkyyWardrobe", "config.properties")
        K.check(os.path.isfile(cfgf) and "slots.free=4" in open(cfgf).read() and "swap.keepIds=Skyy_Menu,Skyy_Vault_*" in open(cfgf).read(), "X1 the default config.properties is seeded")
        K.check(int(Cfg.FREE) == 4 and int(Cfg.MAX) == 18 and list(Cfg.levels()) == [6, 10, 10, 20, 14, 30, 18, 40] and bool(Cfg.HOTBAR)
                and int(Cfg.GAP_S) == 1 and int(Cfg.COMBAT_S) == 10 and int(Cfg.SETTLE_S) == 30 and int(Cfg.JKEEP_S) == 30 and int(Cfg.NAME_MAX) == 16 and bool(Cfg.ON) and not bool(Cfg.STRICT),
                "X1 every row reads its default")
        K.check(Cfg.keep("Skyy_Menu") and Cfg.keep("Skyy_Vault_Prev") and not Cfg.keep("Skyy_Menu2") and not Cfg.keep("Weapon_Sword_Iron"), "X1 keep ids: exact + a trailing *")
        K.check(Cfg.checkLevels("k", "6:10,10:20") is None and Cfg.checkLevels("k", "-") is None and Cfg.checkLevels("k", "6-10") is not None
                and Cfg.checkLevels("k", "30:5") is not None and list(Cfg.parseLevels("10:20, 6:10")) == [6, 10, 10, 20], "X1 check= slots.byLevel (sorted, bounds)")
        K.check(Cfg.checkIds("k", "Skyy_Menu,Foo_*") is None and Cfg.checkIds("k", "*") is not None and Cfg.checkIds("k", "a b") is not None
                and Cfg.checkIds("k", "-") is None, "X1 check= swap.keepIds")
        open(cfgf, "a").write("slots.byLevel=junk\nswap.keepIds=***\n")
        Cfg.reloadAll()
        K.check(list(Cfg.levels()) == [] and list(Cfg.keepList()) == ["Skyy_Menu"] and any("slots.byLevel=junk" in str(l) for l in H["lines"]), "X1 a bad hand edit: no level slots, the menu item still protected, warned")
        P("CfgPub").start(JClass("java.nio.file.Paths").get(mods), None)
        fn = br.get("config:fn:SkyyWardrobe")

        def op(*args):
            a = JArray(JObject)(len(args))
            for i, x in enumerate(args):
                a[i] = x
            return fn.apply(a)
        r = op("set", "slots.byLevel", "6:10,10:20,14:30,18:40", None, None, "yes", "console")
        r2 = op("set", "slots.byLevel", "junk", None, None, "yes", "console")
        r3 = op("set", "swap.keepIds", "Skyy_Menu,Skyy_Vault_*", None, None, "yes", "console")
        K.check(str(r[0]) == "ok" and str(r2[0]) != "ok" and str(r3[0]) == "ok" and list(Cfg.levels()) == [6, 10, 10, 20, 14, 30, 18, 40] and list(Cfg.keepList()) == ["Skyy_Menu", "Skyy_Vault_*"]
                and str(op("get", "slots.free")) == "4", "X1 Server Setup (config:fn): set / check refuses / get (%s / %s / %s)" % (list(r), list(r2), list(r3)))
        P("CfgPub").flush()
        Cfg.reloadAll()
        K.check(list(Cfg.keepList()) == ["Skyy_Menu", "Skyy_Vault_*"] and "slots.byLevel=6:10,10:20,14:30,18:40" in open(cfgf).read(), "X1 the file agrees after a reload")

        # ============================================================ slots
        A = Player_("00000000-0000-0000-0000-00000000000a", "Alice")
        kA = str(A.u)
        dA = Store.get(kA, A.u)
        K.check(Slots.overall(A.u) == -1 and Slots.unlocked(A.u, dA) == 4, "X2 no SkyySkills: 4 free slots")
        br.put("skill:overall:" + kA, JInt(12))
        K.check(Slots.overall(A.u) == 12 and Slots.unlocked(A.u, dA) == 6, "X2 skill:overall:<uuid> 12 -> 6 slots")
        br.put("skill:fn:overall", Overall())
        state["overall"] = 41
        K.check(Slots.unlocked(A.u, dA) == 18, "X2 skill:fn:overall 41 -> 18 slots")
        state["overall"] = 3
        dA.floor = 7
        K.check(Slots.unlocked(A.u, dA) == 7, "X2 the admin floor")
        dA.floor = 0
        Cfg.MAX = 3
        K.check(Slots.unlocked(A.u, dA) == 3 and "locked by the server" in str(Slots.lockText(3)), "X2 slots.max caps it")
        Cfg.MAX = 18
        K.check(str(Slots.lockText(4)) == "unlocks at Overall Level 10" and str(Slots.lockText(9)) == "unlocks at Overall Level 20" and str(Slots.lockText(10)) == "unlocks at Overall Level 30"
                and Slots.shown(dA, 4) == 5, "X2 lockText + shown (4 open + the next locked one)")

        # ============================================================ save current + equip (the home rule) - X3-X12 run with swap.strict ON
        Cfg.STRICT = True
        bridge_on()
        C_ = [stack("Armor_Iron_Head", 1, '{"rar":"Rare","lvl":12}'), stack("Armor_Iron_Chest", 1, '{"rar":"Epic"}'),
              stack("Armor_Iron_Hands", 1), stack("Armor_Iron_Legs", 1, '{"lvl":3}')]
        CH = {0: stack("Weapon_Sword_Iron", 1, '{"rar":"Rare"}'), 1: stack("Food_Bread", 16), 2: stack("Rock_Stone", 64), 8: stack("Skyy_Menu", 1)}
        for i, s in enumerate(C_):
            setc(A.arm, i, s)
        for i, s in CH.items():
            setc(A.hot, i, s)
        base = everything(A, kA)
        r = run(A, 2, 0)
        d = Store.get(kA, A.u)
        K.check(r.startswith("+Saved Loadout 1") and d.worn == 0 and d.slots[0].hasPets and str(d.slots[0].pet) == "pA" and str(d.slots[0].summon) == "sA"
                and "class=Mage" in str(d.slots[0].abil) and d.slots[0].count() == 0 and everything(A, kA) == base, "X3 Save current: linked (nothing moves) + pets + abilities: %s" % r)
        K.check(os.path.isfile(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", kA + ".json")) and Store.readFile(kA, "").worn == 0, "X3 the file says loadout 1 is equipped")
        r = run(A, 1, 1)
        K.check(r.startswith("-One loadout change at a time"), "X3 within swap.gapSeconds of the last change: refused (%s)" % r)
        clear_gap()
        r = run(A, 4, 0, "  Combat<> Set!!  ")
        K.check(r.startswith("+") and str(Store.get(kA, A.u).slots[0].name) == "Combat Set", "X3 Rename sanitises (%s)" % r)
        r = run(A, 4, 0, "abcdefghijklmnopqrstuvwxyz")
        K.check(str(Store.get(kA, A.u).slots[0].name) == "abcdefghijklmnop", "X3 Rename keeps nameMax 16 characters")
        run(A, 4, 0, "Combat")
        # Equip the EMPTY loadout 2: everything goes home to loadout 1, the menu item stays
        r = run(A, 1, 1)
        d = Store.get(kA, A.u)
        K.check(r.startswith("+Equipped Loadout 2 (7 pieces moved)") and d.worn == 1 and d.slots[0].countPart(0) == 4 and d.slots[0].countPart(1) == 3
                and all(getc(A.arm, i) is None for i in range(4)) and getc(A.hot, 8) == key_of(CH[8]) and [getc(A.hot, i) for i in range(8)] == [None] * 8,
                "X4 Equip an empty loadout: the worn gear goes HOME to the equipped one, the SkyWynn Menu item stays (%s)" % r)
        K.check(everything(A, kA) == base and not any("Skyy_Menu" == x[0] for x in file_stacks(kA)[0]), "X4 conservation + the menu item is never stored")
        K.check(not calls["pets"] and not calls["abil"], "X4 a loadout without pets / abilities saved calls neither bridge")
        clear_gap()
        # wear the mining set, save it into loadout 2 (it is the equipped one: refs only)
        M_ = [stack("Armor_Copper_Head", 1, '{"m":1}'), stack("Armor_Copper_Chest", 1), None, stack("Armor_Copper_Legs", 1)]
        MH = {0: stack("Tool_Pickaxe_Iron", 1, '{"lvl":20}'), 2: stack("Furniture_Torch", 32)}
        for i, s in enumerate(M_):
            if s is not None:
                setc(A.arm, i, s)
        for i, s in MH.items():
            setc(A.hot, i, s)
        base = everything(A, kA)
        state["pets"] = "pB|"
        state["abil"] = state["abil"].replace("p1=Meteor;p2=ManaBarrier", "p1=ManaBarrier;p2=Meteor")
        r = run(A, 2, 1)
        d = Store.get(kA, A.u)
        K.check(r.startswith("+Saved Loadout 2") and str(d.slots[1].pet) == "pB" and str(d.slots[1].summon) == "" and "p1=ManaBarrier" in str(d.slots[1].abil)
                and everything(A, kA) == base, "X5 Save current on the equipped loadout: pets + abilities only (%s)" % r)
        clear_gap()
        r = run(A, 2, 2)
        K.check(r.startswith("-You are wearing Loadout 2"), "X5 Save current on another loadout while one is equipped: refused (%s)" % r)
        r = run(A, 2, 0)
        K.check(r.startswith("-You are wearing"), "X5 ... also on a loadout that stores gear")
        clear_gap()
        r = run(A, 1, 0)
        d = Store.get(kA, A.u)
        K.check(r.startswith("+Equipped Combat") and d.worn == 0 and [getc(A.arm, i) for i in range(4)] == [key_of(s) for s in C_]
                and getc(A.hot, 0) == key_of(CH[0]) and getc(A.hot, 1) == key_of(CH[1]) and getc(A.hot, 2) == key_of(CH[2]) and getc(A.hot, 8) == key_of(CH[8])
                and d.slots[0].count() == 0 and d.slots[1].countPart(0) == 3 and d.slots[1].countPart(1) == 2, "X6 Equip 1 from 2: combat on, mining HOME into 2 (%s)" % r)
        K.check(everything(A, kA) == base, "X6 conservation")
        K.check(calls["pets"] == [(kA, "pA", "sA")] and len(calls["abil"]) == 1 and "p1=Meteor" in calls["abil"][0], "X6 the pets + abilities of loadout 1 were applied (%s)" % calls)
        K.check(not os.path.isfile(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", kA + ".journal.json")) or Jr.PENDING.containsKey(kA), "X6 the journal is kept only inside its keep window (PENDING)")
        jf = os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", kA + ".journal.json")
        jd = json.loads(open(jf).read()) if os.path.isfile(jf) else {}
        js_ = (jd.get("steps") or [{}])[-1]
        K.check(jd.get("stage") == "saved" and js_.get("op") == "equip" and len(js_.get("moves", [])) == 7 and "pre" in js_, "X6 the journal: stage saved, newest step = this equip with 7 moves + its pre copy (%s)" % {k_: jd.get(k_) for k_ in ("stage", "prevSteps")})
        clear_gap()
        r = run(A, 1, 1)
        K.check(r.startswith("+Equipped Loadout 2") and everything(A, kA) == base and [getc(A.arm, i) for i in range(4)] == [key_of(M_[0]), key_of(M_[1]), None, key_of(M_[3])]
                and Store.get(kA, A.u).slots[0].count() == 7, "X6 and back: the hands spot of loadout 2 is empty, so the combat hands went home too (strict)")
        K.check(calls["pets"][-1] == (kA, "pB", ""), "X6 pets of loadout 2 (empty summon)")
        # ---- notes: SkyyPets missing / failing, SkyyClasses failing
        clear_gap()
        bridge_on(pets=False)
        r = run(A, 1, 0)
        K.check(r.startswith("=Equipped Combat") and "Pets in loadouts need SkyyPets 0.2.3" in r and everything(A, kA) == base, "X7 SkyyPets missing: items swap, a short note (%s)" % r)
        clear_gap()
        bridge_on()
        state["pets"] = "pA|sA"     # loadout 1's pets are what the player has (its pets part was skipped above)
        state["petsres"] = "-That summon is not a Mount or Fighter."
        state["abilres"] = "=Abilities: ... Skipped: Starfall (choose it at Wisdom 30)."
        r = run(A, 1, 1)
        K.check(r.startswith("=Equipped Loadout 2") and "pets: That summon is not a Mount or Fighter" in r and "abilities: Abilities" in r and everything(A, kA) == base,
                "X7 a failing / partial bridge part is reported, the items stay swapped (%s)" % r)
        state["petsres"], state["abilres"] = "+ok", "+ok"
        # ---- the page view of the cards needs the pet names: petName answers, a gone pet says so
        L0 = Store.get(kA, A.u).slots[0]
        K.check(str(Brg.petsText(A.u, L0)) == "Pet: Pet-pA    Summon: Pet-sA", "X7 pet names through pets:fn:petName")
        L0x = P("WdLoad")(5)
        L0x.hasPets, L0x.pet, L0x.summon = True, "gone", ""
        K.check(str(Brg.petsText(A.u, L0x)) == "Pet: gone (gone)    Summon: none" and "not saved" in str(Brg.petsText(A.u, P("WdLoad")(6))), "X7 a gone pet / no pets saved")
        K.check(str(Brg.abilText(L0.abil)).startswith("Abilities (Mage): Meteor, Mana Barrier - alts Frost Nova, Starfall"), "X7 the ability line (%s)" % Brg.abilText(L0.abil))

        # ============================================================ keep rule WITHOUT an equipped loadout + partial loadouts
        Bp = Player_("00000000-0000-0000-0000-00000000000b", "Bob")
        kB = str(Bp.u)
        setc(Bp.arm, 0, stack("Armor_Leather_Head", 1))
        setc(Bp.hot, 4, stack("Food_Apple", 5))
        dB = Store.get(kB, Bp.u)
        dB.slots[2].armor[1] = stack("Armor_Gold_Chest", 1, '{"g":1}')
        dB.slots[2].hot[4] = stack("Tool_Hatchet_Iron", 1)
        dB.rev = dB.rev + 1
        K.check(Store.save(dB), "X8 setup: a partial loadout 3 stored")
        base = everything(Bp, kB)
        r = run(Bp, 1, 2)
        K.check(r.startswith("+Equipped Loadout 3 (2 pieces moved)") and getc(Bp.arm, 0) == key_of(stack("Armor_Leather_Head", 1)) and getc(Bp.arm, 1) == key_of(dB.slots[2].armor[1] or stack("Armor_Gold_Chest", 1, '{"g":1}'))
                and getc(Bp.hot, 4) == key_of(stack("Tool_Hatchet_Iron", 1)) and Store.get(kB, Bp.u).slots[2].countPart(1) == 1 and everything(Bp, kB) == base,
                "X8 no equipped loadout: where the loadout stores nothing the worn piece stays on; where it does, a swap with it (%s)" % r)

        # ============================================================ a stored item that no longer exists
        clear_gap()
        Codec.UNKNOWN_IDS.add("Armor_Iron_Head")
        base = everything(A, kA)
        r = run(A, 1, 0)
        d = Store.get(kA, A.u)
        K.check(r.startswith("=Equipped Combat") and "Armor_Iron_Head no longer exists" in r and d.slots[0].armor[0] is not None and getc(A.arm, 0) is None
                and d.slots[1].armor[0] is not None and everything(A, kA) == base, "X9 a gone item stays STORED (never put on); the worn piece still goes home (%s) %s" % (r, [d.slots[0].armor[0] is not None, getc(A.arm, 0), d.slots[1].armor[0] is not None, everything(A, kA) == base, [x for x in everything(A, kA) if x not in base], [x for x in base if x not in everything(A, kA)]]))
        Codec.UNKNOWN_IDS.clear()
        clear_gap()
        r = run(A, 1, 1)
        clear_gap()
        r = run(A, 1, 0)
        K.check(everything(A, kA) == base and getc(A.arm, 0) == key_of(C_[0]), "X9 once it exists again it equips normally (%s)" % r)

        # ============================================================ double click / one at a time / the gate
        clear_gap()
        Gate.BUSY.put(A.u, True)
        r = run(A, 1, 1)
        Gate.BUSY.remove(A.u)
        K.check(r.startswith("-One loadout change at a time"), "X10 a second click while a change runs: refused")
        dc = U.allocateInstance(DDC.class_)
        tl = Inst.now()
        E.jf(TR, "now").set(A.st.res, tl)
        for g in ("getLastDamageTime", "getLastCombatAction"):
            E.jf(DDC, E.field_of("com.hypixel.hytale.server.core.entity.damage.DamageDataComponent", g)[1]).set(dc, tl.minusSeconds(3))
        A.comps().put(types["ddc"], dc)
        r = run(A, 1, 1)
        K.check(r.startswith("-You are in combat - wait 7 s"), "X10 in combat (the REAL DamageDataComponent + TimeResource reads): %s" % r)
        for g in ("getLastDamageTime", "getLastCombatAction"):
            E.jf(DDC, E.field_of("com.hypixel.hytale.server.core.entity.damage.DamageDataComponent", g)[1]).set(dc, tl.minusSeconds(30))
        A.comps().put(types["death"], U.allocateInstance(Death.class_))
        r = run(A, 1, 1)
        K.check(r.startswith("-You cannot change loadouts while dead"), "X10 dead (the REAL DeathComponent read): %s" % r)
        A.comps().remove(types["death"])
        br.put("profile:busy:" + kA, True)
        r = run(A, 1, 1)
        K.check(r.startswith("-Your profile is still loading"), "X10 profile:busy: %s" % r)
        br.remove("profile:busy:" + kA)
        r = run(A, 1, 1)
        K.check(r.startswith("-Loadouts open again 30 s after a profile switch"), "X10 30 s after busy was last seen: %s" % r)
        Gate.BUSYAT.clear()
        br.put("profile:epoch:" + kA, JLong(5))
        Gate.observe(A.u, 1)
        br.put("profile:epoch:" + kA, JLong(6))
        r = run(A, 1, 1)
        K.check(r.startswith("-Loadouts open again"), "X10 a profile epoch change opens the settle window: %s" % r)
        Gate.EPOCHAT.clear()
        K.check(Gate.why(False, -1, False, 0, 0) is None and str(Gate.why(False, 9999, False, 0, 0)).startswith("-You are in combat - wait 1 s")
                and Gate.why(False, 10000, False, 0, 0) is None, "X10 the combat edge (10 s)")
        Cfg.ON = False
        K.check(run(A, 1, 1).startswith("-Loadouts are switched off"), "X10 the part switch off")
        Cfg.ON = True

        # ============================================================ locked slots
        clear_gap()
        r = run(A, 1, 9)
        K.check(r.startswith("-Loadout 10 is unlocks at Overall Level 20") or r.startswith("-Loadout 10 is "), "X11 a locked empty loadout: Equip refused (%s)" % r)
        K.check(run(A, 2, 9).startswith("-Loadout 10 is") and run(A, 4, 9, "x").startswith("-Loadout 10 is"), "X11 ... Save current / Rename refused")
        dA2 = Store.get(kA, A.u)
        dA2.slots[9].hot[3] = stack("Food_Cheese", 2)
        dA2.rev = dA2.rev + 1
        Store.save(dA2)
        base = everything(A, kA)
        r = run(A, 1, 9)
        K.check(r.startswith("+Equipped Loadout 10") and everything(A, kA) == base, "X11 a locked loadout that still holds gear: Equip works (locked but full) (%s)" % r)
        clear_gap()
        r = run(A, 1, 0)
        clear_gap()
        r = run(A, 3, 9)
        K.check(r.startswith("+Cleared Loadout 10") and everything(A, kA) == base, "X11 ... and Clear works (%s)" % r)

        # ============================================================ CLEAR: storage first, inventory full, unlink
        clear_gap()
        r = run(A, 3, 1)
        d = Store.get(kA, A.u)
        K.check(r.startswith("+Cleared Loadout 2: 5 stacks moved") and d.slots[1].blank() and everything(A, kA) == base
                and getc(A.sto, 0) is not None, "X12 Clear: its gear goes to storage, refs + name forgotten (%s)" % r)
        clear_gap()
        r = run(A, 3, 0)
        d = Store.get(kA, A.u)
        K.check("your gear stays on you" in r and d.worn == -1 and everything(A, kA) == base and getc(A.arm, 0) is not None, "X12 Clear the equipped loadout: only unlinks (%s) %s" % (r, [d.worn, everything(A, kA) == base, getc(A.arm, 0)]))
        # inventory full: Bob's loadout 3 stores gear; his storage + hotbar + backpack are full of junk
        clear_gap()
        dB = Store.get(kB, Bp.u)
        for c in (Bp.sto, Bp.hot, Bp.bak):
            for i in range(int(c.getCapacity())):
                if c.getItemStack(JShort(i)) is None or c.getItemStack(JShort(i)).isEmpty():
                    setc(c, i, stack("Rock_Junk_%d" % i, 64))
        base = everything(Bp, kB)
        before = dB.slots[2].count()
        r = run(Bp, 3, 2)
        K.check(r.startswith("=Cleared") and "no room for" in r and Store.get(kB, Bp.u).slots[2].count() == before and everything(Bp, kB) == base,
                "X12 inventory full: every stack stays stored, nothing dropped (%s)" % r)

        Cfg.STRICT = False          # from here on the default (the LOCKED keep rule)
        # ============================================================ save failure / put failure / rollback failure -> lock -> repair
        Cc = Player_("00000000-0000-0000-0000-00000000000c", "Cara", flaky=True)
        kC = str(Cc.u)
        for i, s in enumerate([stack("Armor_A_Head", 1, '{"x":1}'), stack("Armor_A_Chest", 1), stack("Armor_A_Hands", 1), stack("Armor_A_Legs", 1)]):
            setc(Cc.arm, i, s)
        setc(Cc.hot, 0, stack("Weapon_A", 1, '{"y":2}'))
        run(Cc, 2, 0)
        clear_gap()
        run(Cc, 1, 1)
        for i, s in enumerate([stack("Armor_B_Head", 1), stack("Armor_B_Chest", 1, '{"b":1}')]):
            setc(Cc.arm, i, s)
        clear_gap()
        r0 = run(Cc, 2, 1)
        base = everything(Cc, kC)
        livebefore = sorted(Cc.live())
        filebefore = open(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", kC + ".json"), "rb").read()
        clear_gap()
        Store.FAIL_NEXT = 1
        r = run(Cc, 1, 0)
        K.check(r.startswith("-Could not save your wardrobe - everything was put back") and sorted(Cc.live()) == livebefore and everything(Cc, kC) == base
                and open(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", kC + ".json"), "rb").read() == filebefore and Store.get(kC, Cc.u).worn == 1,
                "X13 a SAVE FAILURE: the live moves are rolled back, the file and memory unchanged (%s / %s)" % (r0, r))
        jC = os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", kC + ".journal.json")
        jCd = json.loads(open(jC).read()) if os.path.isfile(jC) else {}
        K.check(jCd.get("stage") == "saved" and len(jCd.get("steps", [])) == 1 and Jr.PENDING.containsKey(kC),
                "X13 ... and its journal is back to the EARLIER saved change (the chain is kept, not deleted): %s" % {k_: jCd.get(k_) for k_ in ("stage", "prevSteps")})
        clear_gap()
        Flaky.FAIL_AT = 2
        r = run(Cc, 1, 0)
        Flaky.FAIL_AT = -1
        K.check(r.startswith("-Equip stopped (could not put on") and sorted(Cc.live()) == livebefore and everything(Cc, kC) == base, "X14 a PUT FAILURE: rolled back (%s)" % r)
        clear_gap()
        # one set works, then EVERY set fails: the move stops AND the rollback cannot put the pieces back
        Flaky.FAIL_AT, Flaky.STICKY = 1, True
        r = run(Cc, 1, 0)
        d = Store.get(kC, Cc.u)
        K.check(r.startswith("-The change failed and could not be undone") and d.bad and json.loads(open(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", kC + ".journal.json")).read()).get("stage") == "failed",
                "X15 a ROLLBACK FAILURE: the wardrobe is LOCKED, the journal says failed (%s)" % r)
        Flaky.FAIL_ALL, Flaky.STICKY, Flaky.FAIL_AT = False, False, -1
        clear_gap()
        K.check(run(Cc, 1, 0).startswith("-The change failed") and run(Cc, 4, 0, "x").startswith("-The change failed"), "X15 every change refused while locked")
        Store.CACHE.clear()
        K.check(Store.get(kC, Cc.u).bad, "X15 a restart keeps it locked (the failed journal is read at load)")
        notes = AL()
        rr = Tx.repair(Store.get(kC, Cc.u), Cc.arm, Cc.hot, Cc.sto, Cc.bak, True, notes)
        d = Store.get(kC, Cc.u)
        K.check(rr is not None and not d.bad and everything(Cc, kC) == base and not os.path.isfile(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", kC + ".journal.json")),
                "X15 /wardrobeadmin repair (force) reconciles from the live inventory and unlocks it: %s" % rr)
        clear_gap()
        r = run(Cc, 1, 0)
        K.check(r.startswith("+Equipped") and everything(Cc, kC) == base, "X15 ... and it works again (%s)" % r)

        # ============================================================ CRASH BETWEEN STEPS (equip + clear), live as-is and live rolled back
        def crash_case(label, setup, opn, n, at, after_save, revert):
            Dn = Player_(str(UUID.randomUUID()), "Crash")
            kD = str(Dn.u)
            setup(Dn)
            base_ = everything(Dn, kD)
            pre_live = [Dn.arm.getItemStack(JShort(i)) for i in range(4)] + [Dn.hot.getItemStack(JShort(i)) for i in range(9)] \
                + [Dn.sto.getItemStack(JShort(i)) for i in range(36)] + [Dn.bak.getItemStack(JShort(i)) for i in range(9)]
            clear_gap()
            Tx.CRASH_AT, Tx.CRASH_AFTER_SAVE = at, after_save
            crashed = False
            try:
                run(Dn, opn, n)
            except Exception as e:
                crashed = "harness crash" in str(e)
            Tx.CRASH_AT, Tx.CRASH_AFTER_SAVE = -1, False
            if revert:   # the engine never saved the player after the change: the live inventory comes back as it was before
                cs = [(Dn.arm, 4), (Dn.hot, 9), (Dn.sto, 36), (Dn.bak, 9)]
                k_ = 0
                for c, n_ in cs:
                    for i in range(n_):
                        Tx.put(c, JShort(i), pre_live[k_])
                        k_ += 1
            Store.CACHE.remove(kD)     # "the restart": memory gone, PENDING (this run's journals) gone
            Jr.PENDING.remove(kD)
            clear_gap()
            rep = run(Dn, 5, 0)
            ok = crashed and everything(Dn, kD) == base_ and not os.path.isfile(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", kD + ".journal.json"))
            K.check(ok, "X16 CRASH %s (at %s, after save %s, live %s): conserved after the join repair (%s; crashed %s)" % (label, at, after_save, "rolled back" if revert else "as at the crash", rep, crashed))
            clear_gap()
            r2 = run(Dn, 1, 0)
            clear_gap()
            r3 = run(Dn, 1, 1)
            K.check(everything(Dn, kD) == base_ and not r2.startswith("-The change") and not r3.startswith("-The change"), "X16 CRASH %s: the wardrobe keeps working (%s / %s)" % (label, r2, r3))

        def eq_setup(Dn):
            for i in range(4):
                setc(Dn.arm, i, stack("Armor_W_%d" % i, 1, '{"w":%d}' % i))
            setc(Dn.hot, 0, stack("Weapon_W", 1, '{"z":1}'))
            setc(Dn.hot, 1, stack("Food_W", 10))
            setc(Dn.hot, 8, stack("Skyy_Menu", 1))
            run(Dn, 2, 0)
            clear_gap()
            run(Dn, 1, 1)      # all home to 1
            for i in range(3):
                setc(Dn.arm, i, stack("Armor_V_%d" % i, 1))
            setc(Dn.hot, 0, stack("Tool_V", 1, '{"v":1}'))
            clear_gap()
            run(Dn, 2, 1)

        def cl_setup(Dn):
            eq_setup(Dn)
            setc(Dn.sto, 0, stack("Food_W", 30))     # the same kind as a stored stack: the count rule
        for strict in (False, True):
            Cfg.STRICT = strict
            for at in (0, 1, 3, 99):
                for rv in (False, True):
                    crash_case("equip%s" % (" strict" if strict else ""), eq_setup, 1, 0, at, False, rv)
            for rv in (False, True):
                crash_case("equip%s" % (" strict" if strict else ""), eq_setup, 1, 0, -1, True, rv)
        Cfg.STRICT = False
        for at in (0, 1):
            for rv in (False, True):
                crash_case("clear", cl_setup, 3, 0, at, False, rv)
        for rv in (False, True):
            crash_case("clear", cl_setup, 3, 0, -1, True, rv)

        # ============================================================ PROFILE SWITCH MID-SWAP + per-profile isolation
        Ep = Player_("00000000-0000-0000-0000-00000000000e", "Eve")
        kE1 = str(Ep.u)
        kE2 = kE1 + "-p2"
        eq_setup(Ep)
        base1 = everything(Ep, kE1)
        clear_gap()
        Tx.CRASH_AT = 1
        try:
            run(Ep, 1, 0)
        except Exception:
            pass
        Tx.CRASH_AT = -1
        Store.CACHE.clear()
        Jr.PENDING.clear()
        j1 = os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", kE1 + ".journal.json")
        K.check(os.path.isfile(j1), "X17 setup: profile 1 crashed mid-swap (its journal is on disk)")
        # SkyyProfiles switched to profile 2: another live inventory, another key
        state.setdefault("key", {})[kE1] = kE2
        live1 = [Ep.arm.getItemStack(JShort(i)) for i in range(4)] + [Ep.hot.getItemStack(JShort(i)) for i in range(9)]
        for i in range(4):
            Tx.put(Ep.arm, JShort(i), None)
        for i in range(9):
            Tx.put(Ep.hot, JShort(i), None)
        setc(Ep.arm, 0, stack("Armor_P2_Head", 1, '{"p":2}'))
        clear_gap()
        r = run(Ep, 2, 0)
        b1 = open(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", kE1 + ".json"), "rb").read()
        K.check(r.startswith("+Saved") and os.path.isfile(j1) and os.path.isfile(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", kE2 + ".json")),
                "X17 on profile 2: its own file; profile 1's journal is NOT repaired against profile 2's inventory (%s)" % r)
        clear_gap()
        r = run(Ep, 1, 1)
        K.check(open(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", kE1 + ".json"), "rb").read() == b1 and Store.get(kE2, Ep.u).worn == 1, "X17 per-profile isolation: profile 1's file untouched")
        # back to profile 1 (its inventory as SkyyProfiles saved it at the switch = as at the crash)
        state["key"][kE1] = kE1
        for i in range(4):
            Tx.put(Ep.arm, JShort(i), live1[i])
        for i in range(9):
            Tx.put(Ep.hot, JShort(i), live1[4 + i])
        clear_gap()
        r = run(Ep, 5, 0)
        K.check(everything(Ep, kE1) == base1 and not os.path.isfile(j1), "X17 back on profile 1: its journal repaired, conserved (%s)" % r)

        # ============================================================ unreadable / newer format / orphans
        Fp = Player_("00000000-0000-0000-0000-00000000000f", "Finn")
        kF = str(Fp.u)
        ff = os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", kF + ".json")
        open(ff, "w").write("{ not json")
        bytes0 = open(ff, "rb").read()
        clear_gap()
        r1, r2_, r3_ = run(Fp, 2, 0), run(Fp, 4, 0, "x"), run(Fp, 3, 0)
        K.check(all(x.startswith("-Your wardrobe file could not be read") for x in (r1, r2_, r3_)) and open(ff, "rb").read() == bytes0,
                "X18 an UNREADABLE file: shut, never written (%s)" % r1)
        open(ff, "w").write('{"format": 2, "loadouts": []}')
        Store.CACHE.remove(kF)
        bytes0 = open(ff, "rb").read()
        r1 = run(Fp, 2, 0)
        K.check(r1.startswith("-Your wardrobe file has format 2") and open(ff, "rb").read() == bytes0, "X18 a NEWER format: shut, never written (%s)" % r1)
        open(ff, "w").write(json.dumps({"format": 1, "rev": 3, "worn": -1, "loadouts": [{"n": 0, "name": "Old", "armor": [
            {"slot": 0, "id": "Armor_Gone_Head", "qty": 0}, {"slot": 1, "id": "Armor_Ok_Chest", "qty": 1, "durability": 50.0, "maxDurability": 100.0, "quality": 0}],
            "hotbar": [{"slot": 3, "id": "Food_X", "qty": 2}, {"slot": 3, "id": "Food_Y", "qty": 1}]}, {"n": 40, "armor": [{"slot": 0, "id": "Armor_Far", "qty": 1}]}], "orphans": []}))
        Store.CACHE.remove(kF)
        d = Store.get(kF, Fp.u)
        K.check(not d.bad and d.orphans.size() == 3 and d.slots[0].countPart(0) == 1 and d.slots[0].countPart(1) == 1 and d.items() == 5,
                "X19 orphans: an undecodable stack, a slot taken twice, a loadout number out of range - all kept (%d orphans)" % d.orphans.size())
        clear_gap()
        r = run(Fp, 4, 0, "Renamed")
        d2 = Store.readFile(kF, "")
        K.check(r.startswith("+") and Store.countDoc(BD.parse(open(ff).read())) == 5 and BD.parse(open(ff).read()).getArray("orphans").size() == 3,
                "X19 a save keeps every orphan (count 5)")
        K.check(d2.orphans.size() == 1 and d2.items() == 5, "X32 at the next load the taken-twice and out-of-range stacks go into free spots (reachable); only the undecodable one stays an orphan (%d)" % d2.orphans.size())
        doc = json.loads(open(ff).read())
        for o in doc["orphans"]:
            if o.get("id") == "Food_Y":
                o["from"] = "loadout0:hotbar:4"
        open(ff, "w").write(json.dumps(doc))
        Store.CACHE.remove(kF)
        d = Store.get(kF, Fp.u)
        K.check(d.orphans.size() == 1 and d.slots[0].hot[4] is not None and str(d.slots[0].hot[4].getItemId()) == "Food_Y" and d.items() == 5,
                "X19 an orphan whose spot is free goes back at the next load (%d orphans)" % d.orphans.size())

        # ============================================================ THE PAGE (real builders, every click)
        TP = JClass(FAKE_PKG + ".TestPage")
        UCB, UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
        Gp = Player_("00000000-0000-0000-0000-000000000011", "Gwen")
        kG = str(Gp.u)
        for i, s in enumerate([stack("Armor_G_Head", 1, '{"g":1}'), stack("Armor_G_Chest", 1)]):
            setc(Gp.arm, i, s)
        setc(Gp.hot, 0, stack("Weapon_G", 1))
        setc(Gp.hot, 8, stack("Skyy_Menu", 1))
        br.put("profile:name:" + kG, "Fox")
        pg = TP(Gp.pr)

        def build():
            b, ev = UCB(), UEB()
            pg.build(Gp.ref, b, ev, Gp.st)
            cmds = list(b.getCommands())
            text = " ".join(" ".join(str(x) for x in (c.selector, c.text, c.data) if x is not None) for c in cmds)
            evs = list(ev.getEvents())
            return text, evs, cmds

        text, evs, cmds = build()
        K.check("TextButton #SkyyWdC0Eq" in text and "#SkyyWdC4 " in text and "SkyyWdC5" not in text and len(evs) == 4 * 4 + 1
                and "Profile Fox" in text and "0 of 4 loadouts used" in text, "X20 the page: 4 open cards + the next locked one, 4 buttons each + Close (%d events)" % len(evs))
        K.check("Locked" in text and "unlocks at Overall Level 10" in text, "X20 the locked card says how it unlocks")
        pg.handleDataEvent(Gp.ref, Gp.st, '{"a":"sv","i":"0","t":"%s"}' % pg.tok)
        K.check(str(pg.info).startswith("+Saved Loadout 1") and pg.rebuilds == 1, "X20 Save current from the page (%s)" % pg.info)
        text, evs, cmds = build()
        K.check("EQUIPPED - you wear it" in text and "Armor_G_Head" in text and "Weapon_G" in text and "Skyy_Menu" not in text,
                "X20 the EQUIPPED card shows the LIVE armor + hotbar (not the menu item)")
        svb = [e for e in evs if "Sv" in str(e.selector)]
        K.check(len(evs) == 4 + 3 * 3 + 1 and len(svb) == 1 and "#SkyyWdC1Sv" in text and "The SkyWynn Menu item never moves." in text,
                "X36 while loadout 1 is equipped, Save current on the other cards is greyed and unbound (%d events, %d save bindings)" % (len(evs), len(svb)))
        Cfg.KEEP_IDS = "Skyy_Vault_*"
        text2, _e2, _c2 = build()
        Cfg.KEEP_IDS = "-"
        text3, _e3, _c3 = build()
        Cfg.KEEP_IDS = "Skyy_Menu,Skyy_Vault_*"
        K.check("Never moved: Skyy_Vault_*" in text2 and "Every hotbar slot swaps." in text3, "X36 the hint follows swap.keepIds")
        dG0 = Store.get(kG, Gp.u)
        dG0.slots[2].hot[6] = stack("Food_GoneItem", 1)
        dG0.slots[2].hot[7] = stack("Food_HereItem", 1)
        dG0.rev = dG0.rev + 1
        Store.save(dG0)
        Codec.UNKNOWN_IDS.add("Food_GoneItem")
        text, evs, cmds = build()
        K.check("Food_HereItem" in text and "Food_GoneItem" not in text, "X20 a stored item that no longer exists shows an empty frame (no client warning)")
        Codec.UNKNOWN_IDS.clear()
        dG0.slots[2].hot[6] = None
        dG0.slots[2].hot[7] = None
        dG0.rev = dG0.rev + 1
        Store.save(dG0)
        tok_old = pg.tok
        pg.handleDataEvent(Gp.ref, Gp.st, '{"a":"eq","i":"1","t":"stale"}')
        K.check(str(pg.info).startswith("=The page changed") and Store.get(kG, Gp.u).worn == 0, "X20 a click from a stale page: rebuilt, nothing done")
        build()
        clear_gap()
        pg.handleDataEvent(Gp.ref, Gp.st, '{"a":"eq","i":"1","t":"%s"}' % pg.tok)
        K.check(str(pg.info).startswith("+Equipped Loadout 2") and Store.get(kG, Gp.u).worn == 1, "X20 Equip from the page (%s)" % pg.info)
        build()
        pg.handleDataEvent(Gp.ref, Gp.st, '{"a":"rn","i":"0","t":"%s","@WdName":"Tank Set"}' % pg.tok)
        K.check(str(Store.get(kG, Gp.u).slots[0].name) == "Tank Set", "X20 Rename reads the name box (@WdName) (%s)" % pg.info)
        build()
        clear_gap()
        pg.handleDataEvent(Gp.ref, Gp.st, '{"a":"cl","i":"0","t":"%s"}' % pg.tok)
        K.check(str(pg.info).startswith("=Press Clear again") and Store.get(kG, Gp.u).slots[0].count() == 3, "X20 Clear asks once")
        build()
        pg.handleDataEvent(Gp.ref, Gp.st, '{"a":"cl","i":"0","t":"%s"}' % pg.tok)
        K.check(str(pg.info).startswith("+Cleared Tank Set") and Store.get(kG, Gp.u).slots[0].blank(), "X20 ... the second click clears (%s)" % pg.info)
        text, evs, cmds = build()
        pg.handleDataEvent(Gp.ref, Gp.st, '{"a":"close"}')
        K.check(pg.closes == 1, "X20 Close")
        bad_ids = [m for m in re.findall(r"#(SkyyWd\w+)", text) if "_" in m]
        K.check(not bad_ids, "X20 no underscores in any element id")

        # ============================================================ commands (player + admin forms)
        Cmds = P("WdCmds")
        Gp.pr.msgs = None
        Cmds.player(Gp.pr, Gp.ref, Gp.st, JArray(JString)(["help"]))
        clear_gap()
        Cmds.player(Gp.pr, Gp.ref, Gp.st, JArray(JString)(["1"]))
        clear_gap()
        Cmds.player(Gp.pr, Gp.ref, Gp.st, JArray(JString)(["equip", "2"]))
        clear_gap()
        Cmds.player(Gp.pr, Gp.ref, Gp.st, JArray(JString)(["name", "2", "Mine"]))
        Cmds.player(Gp.pr, Gp.ref, Gp.st, JArray(JString)(["dance", "2"]))
        said = Gp.said()
        K.check(len(said) == 5 and said[0].startswith("[Wardrobe] /wardrobe opens") and said[1].startswith("[Wardrobe] Equipped") and "Mine" in said[3] and "/wardrobe opens" in said[4],
                "X21 /wardrobe help | <n> | equip <n> | name <n> <name> | unknown (%s)" % said)
        res = [str(Cmds.admin(None, JArray(JString)(a))) for a in (["help"], ["info", "Gwen"], ["slots", "Gwen", "9"], ["slots", "Gwen", "99"], ["info", "Nobody"], ["reload"])]
        f0 = Store.get(kG, Gp.u).floor
        time.sleep(0.4)
        nt_ = drain(H)
        K.check(res[0].startswith("=/wardrobeadmin") and res[1].startswith("=" + kG) and res[2].startswith("=Slots change queued") and f0 != 9 and nt_ == 1
                and Store.get(kG, Gp.u).floor == 9 and any("now has at least 9" in str(l) for l in H["lines"])
                and res[3].startswith("-Slots is 0") and res[4].startswith("-Nobody is not online") and res[5].startswith("+Reloaded"),
                "X21 /wardrobeadmin forms; slots runs on the TARGET's world thread (%s; %d tasks)" % (res, nt_))

        # ============================================================ wardrobe:fn:open, the join repair, quit, timer, hop
        TPM = JClass(TESTPM)
        ofn = P("WdOpenFn")()
        TPM.OPENS = 0
        K.check(bool(ofn.apply(Gp.u)) and drain(H) == 1 and TPM.OPENS == 1 and str(TPM.CUR.getClass().getSimpleName()) == "WdPage", "X22 wardrobe:fn:open -> the world thread opens the page")
        K.check(not bool(ofn.apply("x")) and not bool(ofn.apply(UUID.randomUUID())), "X22 wardrobe:fn:open: bad / offline -> FALSE")
        # a crashed journal for Gwen, then PlayerReadyEvent: the hop waits 2 s, then the world task repairs (after profile:busy clears)
        base = everything(Gp, kG)
        clear_gap()
        Tx.CRASH_AT = 0
        try:
            run(Gp, 1, 0)
        except Exception:
            pass
        Tx.CRASH_AT = -1
        Store.CACHE.clear()
        Jr.PENDING.clear()
        PRE = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent")
        ev = U.allocateInstance(PRE.class_)
        E.jf(PRE, "playerRef").set(ev, Gp.ref)
        br.put("profile:busy:" + kG, True)
        P("WdReady")().accept(ev)
        time.sleep(2.6)
        n1 = drain(H)
        K.check(n1 == 1 and os.path.isfile(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", kG + ".journal.json")), "X23 join: the repair task waits while profile:busy (%d tasks)" % n1)
        br.remove("profile:busy:" + kG)
        time.sleep(1.4)
        n2 = drain(H)
        K.check(n2 == 1 and not os.path.isfile(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", kG + ".journal.json")) and everything(Gp, kG) == base,
                "X23 ... then repairs on the world thread, conserved (%d tasks, %s)" % (n2, Gp.said()[-1:]))
        P("WdReady")().accept(ev)
        time.sleep(2.4)
        K.check(drain(H) == 0, "X23 PlayerReadyEvent again (a world switch): once per session")
        PDE = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent")
        Gate.LAST.put(Gp.u, JLong(1))
        P("WdQuit")().accept(PDE(Gp.pr))
        K.check(not P("WdReady").SESSION.containsKey(Gp.u) and not Gate.LAST.containsKey(Gp.u), "X24 disconnect: the session state is forgotten")
        # admin repair through the hop (force) with an admin to tell: loadout 4 stores a piece, the equip "crashes" after its move
        dG = Store.get(kG, Gp.u)
        dG.slots[3].hot[5] = stack("Food_Admin", 3, '{"a":1}')
        dG.rev = dG.rev + 1
        Store.save(dG)
        base = everything(Gp, kG)
        Tx.CRASH_AT = 99
        clear_gap()
        try:
            run(Gp, 1, 3)
        except Exception:
            pass
        Store.CACHE.clear()
        Jr.PENDING.clear()
        Tx.CRASH_AT = -1
        Gp.pr.msgs = None
        r = str(Cmds.admin(Gp.pr, JArray(JString)(["repair", "Gwen"])))
        time.sleep(0.4)
        drain(H)
        K.check(r.startswith("=Repair queued") and any("interrupted loadout change" in m for m in Gp.said()) and everything(Gp, kG) == base, "X24 /wardrobeadmin repair <player> (%s)" % Gp.said())
        # the timer: epochs + the journal keep window
        @JImplements(PKG + "WdApi")
        class Api:
            @JOverride
            def online(self):
                return JArray(UUID)([Gp.u])

            @JOverride
            def byName(self, n):
                return Gp.u

            @JOverride
            def nameOf(self, u):
                return "Gwen"

            @JOverride
            def tell(self, u, t, c):
                pass
        P("WdEng").API = Api()
        br.put("profile:epoch:" + kG, JLong(1))
        P("WdTimer")().run()
        br.put("profile:epoch:" + kG, JLong(2))
        P("WdTimer")().run()
        K.check(Gate.settleLeft(Gp.u, int(time.time() * 1000)) > 25000, "X25 the timer notices the profile switch (settle window)")
        Gate.EPOCHAT.clear()
        Jr.PENDING.put("somekey", JLong(1))
        open(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", "somekey.journal.json"), "w").write('{"stage": "saved"}')
        Jr.PENDING.put("movekey", JLong(1))
        open(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", "movekey.journal.json"), "w").write('{"stage": "moving"}')
        P("WdTimer")().run()
        K.check(not os.path.isfile(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", "somekey.journal.json")) and not Jr.PENDING.containsKey("somekey"), "X25 the timer deletes journals past their keep time")
        K.check(os.path.isfile(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", "movekey.journal.json")) and not Jr.PENDING.containsKey("movekey"),
                "X30 ... but never a journal whose file says moving / failed (a stale PENDING entry is only forgotten)")
        os.remove(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", "movekey.journal.json"))
        Jr.PENDING.put("k2", JLong(int(time.time() * 1000)))
        open(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", "k2.journal.json"), "w").write("{}")
        K.check(Jr.dropAll() == 1 and not os.path.isfile(os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", "k2.journal.json")), "X25 shutdown: pending journals dropped")
        P("WdEng").API = None
        onl = [str(x) for x in P("WdEng").online()]
        P("WdTimer")().run()
        K.check(kG in onl and kA in onl and int(P("WdTimer").RUNS.get()) >= 4 and str(P("WdEng").nameOf(Gp.u)) == "Gwen", "X25 the real online() / nameOf (Universe) + the timer without the seam")
        # ============================================================ FIXER ROUND: X27 CHAINED changes inside one journal window
        Cfg.STRICT = False
        Store.FAIL_NEXT = 0
        LD = os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts")

        def snap(p):
            return [p.arm.getItemStack(JShort(i)) for i in range(4)] + [p.hot.getItemStack(JShort(i)) for i in range(9)] \
                + [p.sto.getItemStack(JShort(i)) for i in range(36)] + [p.bak.getItemStack(JShort(i)) for i in range(9)]

        def set_live(p, sn):
            k_ = 0
            for c, n_ in ((p.arm, 4), (p.hot, 9), (p.sto, 36), (p.bak, 9)):
                for i in range(n_):
                    Tx.put(c, JShort(i), sn[k_])
                    k_ += 1

        def pos(p):
            d_ = Store.get(str(p.u), p.u)
            return (int(d_.worn), int(d_.slots[0].count()), int(d_.slots[1].count()), int(d_.slots[2].count()))

        def three_sets(p):
            k = str(p.u)
            for i in range(4):
                setc(p.arm, i, stack("Armor_W%d" % i, 1, '{"w":%d}' % i))
            setc(p.hot, 0, stack("Weapon_W", 1, '{"w":9}'))
            run(p, 2, 0)
            clear_gap()
            run(p, 1, 1)          # put away into loadout 1
            clear_gap()
            for i in range(4):
                setc(p.arm, i, stack("Armor_C%d" % i, 1))
            setc(p.hot, 0, stack("Tool_C", 1, '{"c":1}'))
            run(p, 2, 1)
            clear_gap()
            run(p, 1, 2)          # put away into loadout 2
            clear_gap()
            for i in range(3):
                setc(p.arm, i, stack("Armor_D%d" % i, 1, '{"d":%d}' % i))
            setc(p.hot, 0, stack("Tool_D", 1))
            setc(p.hot, 3, stack("Food_D", 7))
            run(p, 2, 2)
            clear_gap()
            run(p, 1, 0)          # wear W again: D goes home to loadout 3
            clear_gap()
            Jr.delete(k)          # the setup's own journals are long saved

        def chain_case(label, ops, stage, crash_last=-1):
            Dn = Player_(str(UUID.randomUUID()), "Chain")
            kD = str(Dn.u)
            three_sets(Dn)
            base_ = everything(Dn, kD)
            snaps, poss = [snap(Dn)], [pos(Dn)]
            for q, (op_, n_) in enumerate(ops):
                clear_gap()
                if q == len(ops) - 1 and crash_last >= 0:
                    Tx.CRASH_AT = crash_last
                try:
                    run(Dn, op_, n_)
                except Exception:
                    pass
                Tx.CRASH_AT = -1
                snaps.append(snap(Dn))
                poss.append(pos(Dn))
            jd = json.loads(open(os.path.join(LD, kD + ".journal.json")).read())
            nsteps = len(jd.get("steps", []))
            if stage is not None:
                set_live(Dn, snaps[stage])
            Store.CACHE.remove(kD)     # "the restart"
            Jr.PENDING.remove(kD)
            clear_gap()
            rep = run(Dn, 5, 0)
            got = pos(Dn)
            ok = everything(Dn, kD) == base_ and not os.path.isfile(os.path.join(LD, kD + ".journal.json")) and nsteps == len(ops)
            if stage is not None and crash_last < 0:   # the live inventory may match several stages (A -> B -> A): any of them is right
                same_ = [i for i in range(len(snaps)) if [key_of(x) if x is not None and not x.isEmpty() else None for x in snaps[i]] == [key_of(x) if x is not None and not x.isEmpty() else None for x in snaps[stage]]]
                ok = ok and got in [poss[i] for i in same_]
            K.check(ok, "X27 CHAIN %s, live %s: every piece exactly once after the join repair (%d steps in ONE journal; wardrobe %s, expected %s; %s)"
                    % (label, "as at the crash" if stage is None else "at stage %d" % stage, nsteps, got, poss[stage] if stage is not None else "-", rep))
            clear_gap()
            r2 = run(Dn, 1, 1)
            clear_gap()
            r3 = run(Dn, 1, 0)
            K.check(everything(Dn, kD) == base_ and not r2.startswith("-The change") and not r3.startswith("-The change"), "X27 CHAIN %s stage %s: the wardrobe keeps working (%s / %s)" % (label, stage, r2, r3))

        for st_ in (0, 1, 2):
            chain_case("equip 2 then equip 3 (the critic's case)", [(1, 1), (1, 2)], st_)
        for st_ in (0, 1, 2, 3):
            chain_case("equip 2, equip 3, equip 1", [(1, 1), (1, 2), (1, 0)], st_)
        for st_ in (0, 1, 2):
            chain_case("equip 2 then clear 3", [(1, 1), (3, 2)], st_)
        for st_ in (None, 0, 1):
            chain_case("equip 2 then equip 3 interrupted after 1 move", [(1, 1), (1, 2)], st_, crash_last=1)
        # the chain drops steps saved longer ago than the keep window; a new change takes its journal out of PENDING (X30)
        Dn = Player_(str(UUID.randomUUID()), "Prune")
        kD = str(Dn.u)
        three_sets(Dn)
        clear_gap()
        run(Dn, 1, 1)
        jf_ = os.path.join(LD, kD + ".journal.json")
        jd = json.loads(open(jf_).read())
        sa = jd["steps"][0]["savedAt"]
        sav = int(sa["$numberLong"]) if isinstance(sa, dict) else int(sa)
        jd["steps"][0]["savedAt"] = {"$numberLong": str(sav - 60000)}
        open(jf_, "w").write(json.dumps(jd))
        clear_gap()
        run(Dn, 1, 2)
        jd2 = json.loads(open(jf_).read())
        K.check(len(jd2.get("steps", [])) == 1 and jd2.get("stage") == "saved", "X27 a step saved longer ago than journalKeepSeconds is dropped from the chain (%d steps)" % len(jd2.get("steps", [])))
        clear_gap()
        Tx.CRASH_AT = 0
        try:
            run(Dn, 1, 0)
        except Exception:
            pass
        Tx.CRASH_AT = -1
        jd3 = json.loads(open(jf_).read())
        K.check(jd3.get("stage") == "moving" and len(jd3.get("steps", [])) == 2 and not Jr.PENDING.containsKey(kD),
                "X30 a change in progress: its journal (stage moving, chained) is out of PENDING, so the timer can never delete it")
        Jr.PENDING.put(kD, JLong(1))      # even a stale PENDING entry: the sweep reads the file first
        Jr.sweep(int(time.time() * 1000))
        K.check(os.path.isfile(jf_) and not Jr.PENDING.containsKey(kD), "X30 the sweep keeps a moving journal")
        clear_gap()
        run(Dn, 5, 0)

        # ============================================================ X28 (fixer 2) NO epoch rule: an epoch bump is not an inventory save
        Ob = Player_("00000000-0000-0000-0000-000000000012", "Olly")
        kO = str(Ob.u)
        br.put("profile:epoch:" + kO, JLong(5))
        three_sets(Ob)
        base_ = everything(Ob, kO)
        pre_ = snap(Ob)
        clear_gap()
        run(Ob, 1, 1)
        jfo = os.path.join(LD, kO + ".journal.json")
        K.check(json.loads(open(jfo).read()).get("epoch") in (5, {"$numberLong": "5"}), "X28 the journal still carries the profile epoch (log only) (%s)" % json.loads(open(jfo).read()).get("epoch"))
        set_live(Ob, pre_)                 # the engine never saved the swap (crash) ...
        Store.CACHE.remove(kO)
        Jr.PENDING.remove(kO)
        br.put("profile:epoch:" + kO, JLong(7))   # ... while the epoch moved WITHOUT a switch (first profile / admin setclass / join repair)
        clear_gap()
        r = run(Ob, 5, 0)
        K.check(everything(Ob, kO) == base_ and not os.path.isfile(jfo) and "OBSOLETE" not in open(os.path.join(mods, "Skyy_SkyyWardrobe", "wardrobe.log")).read(),
                "X28 the critic's case: equip, epoch bump with no inventory save, crash -> the journal is REPAIRED, every piece once (%s)" % r)
        # a real switch away and back: SkyyProfiles saved the inventory AFTER the change -> the replay finds every move done, nothing changes
        clear_gap()
        Gate.observe(Ob.u, JLong(int(time.time() * 1000)))
        Gate.EPOCHAT.remove(Ob.u)          # (the settle window after the bump is X10's subject)
        r0 = run(Ob, 1, 2)
        post_ = snap(Ob)
        base_ = everything(Ob, kO)
        Store.CACHE.remove(kO)
        Jr.PENDING.remove(kO)
        br.put("profile:epoch:" + kO, JLong(9))
        set_live(Ob, post_)
        clear_gap()
        r = run(Ob, 5, 0)
        K.check(r0.startswith("+Equipped") and everything(Ob, kO) == base_ and not os.path.isfile(jfo) and Store.get(kO, Ob.u).worn == 2 and "4 done, 0 not done, 0 unclear" in r,
                "X28 a profile switched away and back (saved after the change): the replay keeps everything as it is (%s / %s)" % (r0, r))
        br.remove("profile:epoch:" + kO)

        # ============================================================ X29 a repair that cannot be saved stops the op
        Rp = Player_(str(UUID.randomUUID()), "Rhea")
        kR = str(Rp.u)
        three_sets(Rp)
        base_ = everything(Rp, kR)
        pre_ = snap(Rp)
        clear_gap()
        run(Rp, 1, 1)
        set_live(Rp, pre_)
        Store.CACHE.remove(kR)
        Jr.PENDING.remove(kR)
        clear_gap()
        Store.FAIL_NEXT = 1
        r = run(Rp, 4, 0, "NewName")
        Store.FAIL_NEXT = 0
        K.check(r.startswith("-The repair could not be saved") and str(Store.get(kR, Rp.u).slots[0].name) != "NewName" and os.path.isfile(os.path.join(LD, kR + ".journal.json")),
                "X29 the repair could not be saved: the op is refused, the journal kept (%s)" % r)
        clear_gap()
        r = run(Rp, 5, 0)
        K.check(everything(Rp, kR) == base_ and not os.path.isfile(os.path.join(LD, kR + ".journal.json")), "X29 ... the next try repairs it, conserved (%s)" % r)

        # ============================================================ X31 Clear still works while the wardrobe is switched off
        Cl = Player_(str(UUID.randomUUID()), "Cleo")
        kL = str(Cl.u)
        three_sets(Cl)
        base_ = everything(Cl, kL)
        Cfg.ON = False
        clear_gap()
        r1 = run(Cl, 1, 1)
        clear_gap()
        r2 = run(Cl, 3, 1)
        Cfg.ON = True
        K.check(r1.startswith("-Loadouts are switched off") and r2.startswith("+Cleared") and Store.get(kL, Cl.u).slots[1].count() == 0 and everything(Cl, kL) == base_,
                "X31 switched off: Equip refused, Clear still takes the gear out (%s / %s)" % (r1, r2))

        # ============================================================ X32 a piece displaced by a repair is parked in a free spot (reachable)
        Pk = Player_(str(UUID.randomUUID()), "Park")
        kP = str(Pk.u)
        dP = Store.get(kP, Pk.u)
        dP.uuid = kP
        dP.slots[0].armor[0] = stack("Armor_Old_Head", 1)
        dP.slots[1].armor[1] = stack("Armor_Busy", 1)
        ch_ = Tx.setSpot(dP, 0, 0, 0, stack("Armor_New_Head", 1), "test", 1)
        parked = [i for i in range(len(dP.slots)) if dP.slots[i].armor[0] is not None and str(dP.slots[i].armor[0].getItemId()) == "Armor_Old_Head"]
        K.check(ch_ and dP.orphans.size() == 0 and parked and parked[0] not in (0, 1), "X32 repair setSpot: the displaced piece goes into a free spot of another loadout (%s), not an orphan" % parked)
        for i in range(len(dP.slots)):
            if dP.slots[i].armor[2] is None:
                dP.slots[i].armor[2] = stack("Armor_Fill_%d" % i, 1)
        Tx.setSpot(dP, 0, 0, 2, stack("Armor_New_Hands", 1), "test", -1)
        K.check(dP.orphans.size() == 1 and "loadout0:armor:2" in str(dP.orphans.get(0).asDocument().getString("from").getValue()),
                "X32 ... no free spot: an orphan with a loadout origin, retried at every load")

        # ============================================================ X34 the pets + abilities you have go with the loadout you leave
        bridge_on()
        state["petsres"], state["abilres"] = "+ok", "+ok"
        Rf = Player_(str(UUID.randomUUID()), "Refs")
        kF2 = str(Rf.u)
        state["pets"] = "p1|s1"
        setc(Rf.arm, 0, stack("Armor_R_Head", 1))
        run(Rf, 2, 0)
        clear_gap()
        run(Rf, 1, 1)
        clear_gap()
        state["pets"] = "p2|"
        setc(Rf.arm, 0, stack("Armor_S_Head", 1))
        run(Rf, 2, 1)
        clear_gap()
        run(Rf, 1, 0)
        state["pets"] = "p9|s9"            # the player picked another pet while loadout 1 is equipped
        clear_gap()
        del calls["pets"][:]
        run(Rf, 1, 1)
        dF = Store.get(kF2, Rf.u)
        clear_gap()
        run(Rf, 1, 0)
        K.check(str(dF.slots[0].pet) == "p9" and str(dF.slots[0].summon) == "s9" and calls["pets"][-1] == (kF2, "p9", "s9") and str(Store.readFile(kF2, "").slots[0].pet) == "p9",
                "X34 Equip keeps your current pets / abilities with the loadout you leave (saved with the same write): %s" % calls["pets"])

        # ============================================================ X35 swap.strict off (LOCKED keep) vs on
        Kp = Player_(str(UUID.randomUUID()), "Keep")
        kK = str(Kp.u)
        AH = [stack("Armor_KA_%d" % i, 1, '{"a":%d}' % i) for i in range(4)]
        for i in range(4):
            setc(Kp.arm, i, AH[i])
        setc(Kp.hot, 0, stack("Weapon_KA", 1))
        run(Kp, 2, 0)
        clear_gap()
        run(Kp, 1, 1)
        clear_gap()
        setc(Kp.arm, 0, stack("Armor_KB_0", 1))
        setc(Kp.arm, 1, stack("Armor_KB_1", 1))
        setc(Kp.hot, 0, stack("Tool_KB", 1))
        run(Kp, 2, 1)
        clear_gap()
        run(Kp, 1, 0)
        base_ = everything(Kp, kK)
        Cfg.STRICT = False
        clear_gap()
        r = run(Kp, 1, 1)
        dK = Store.get(kK, Kp.u)
        K.check(r.startswith("+Equipped") and getc(Kp.arm, 2) == key_of(AH[2]) and getc(Kp.arm, 3) == key_of(AH[3]) and dK.slots[0].count() == 3 and everything(Kp, kK) == base_,
                "X35 swap.strict OFF (default): a spot the partial loadout leaves empty keeps the worn piece (%s, loadout 1 stores %d)" % (r, dK.slots[0].count()))
        Cfg.STRICT = True
        clear_gap()
        r = run(Kp, 1, 0)
        dK = Store.get(kK, Kp.u)
        K.check(r.startswith("+Equipped") and getc(Kp.arm, 2) is None and getc(Kp.arm, 3) is None and dK.slots[1].count() == 5 and everything(Kp, kK) == base_,
                "X35 swap.strict ON: you wear exactly the loadout, the rest goes home (%s)" % r)
        Cfg.STRICT = False
        Cfg.ON = True

        # ============================================================ X37 (fixer 2) a swapped-in piece used / moved inside the window
        def food_sets(p, food_q=10):
            setc(p.arm, 0, stack("Armor_F0", 1, '{"f":0}'))
            setc(p.hot, 0, stack("Weapon_F", 1, '{"f":9}'))
            run(p, 2, 0)
            clear_gap()
            run(p, 1, 1)          # put away into loadout 1
            clear_gap()
            setc(p.arm, 0, stack("Armor_G0", 1))
            setc(p.hot, 0, stack("Tool_G", 1, '{"g":1}'))
            setc(p.hot, 2, stack("Food_G", food_q, '{"g":2}'))
            run(p, 2, 1)
            clear_gap()
            run(p, 1, 0)          # loadout 1 on again: loadout 2 stores Armor_G0, Tool_G, Food_G x10
            clear_gap()
            Jr.delete(str(p.u))

        def tot(p, k, item):
            return sum(q for (i_, m_), q in everything(p, k) if i_ == item)

        def restart(p):
            Store.CACHE.remove(str(p.u))
            Jr.PENDING.remove(str(p.u))
            clear_gap()

        # (a) the critic's case: Food x10 swapped in, 4 eaten, crash -> 6 food, never 16
        Fa = Player_(str(UUID.randomUUID()), "Food")
        kFa = str(Fa.u)
        food_sets(Fa)
        clear_gap()
        r0 = run(Fa, 1, 1)
        setc(Fa.hot, 2, stack("Food_G", 6, '{"g":2}'))
        after_ = everything(Fa, kFa)
        restart(Fa)
        r = run(Fa, 5, 0)
        K.check(r0.startswith("+Equipped") and tot(Fa, kFa, "Food_G") == 6 and everything(Fa, kFa) == after_ and not os.path.isfile(os.path.join(LD, kFa + ".journal.json")),
                "X37 a swapped-in stack eaten from (x10 -> x6) then a crash: 6 food, never 16 (%d; %s)" % (tot(Fa, kFa, "Food_G"), r))
        # (b) eaten AND moved to the storage (its spot is empty again) + the swapped-in tool moved: still in the inventory, not re-stored
        Fb = Player_(str(UUID.randomUUID()), "Moved")
        kFb = str(Fb.u)
        food_sets(Fb)
        clear_gap()
        run(Fb, 1, 1)
        Tx.put(Fb.hot, JShort(2), None)
        setc(Fb.sto, 5, stack("Food_G", 6, '{"g":2}'))
        Tx.put(Fb.hot, JShort(0), None)
        setc(Fb.sto, 6, stack("Tool_G", 1, '{"g":1}'))
        after_ = everything(Fb, kFb)
        restart(Fb)
        r = run(Fb, 5, 0)
        K.check(tot(Fb, kFb, "Food_G") == 6 and tot(Fb, kFb, "Tool_G") == 1 and tot(Fb, kFb, "Weapon_F") == 1 and everything(Fb, kFb) == after_,
                "X37 swapped-in pieces moved to the storage (one eaten from) then a crash: nothing doubled, the weapon taken off kept (%s; %s)" % (everything(Fb, kFb), r))
        # (c) the same swap with the live inventory as BEFORE it (the engine never saved it): undone, every piece once
        Fc = Player_(str(UUID.randomUUID()), "Undo")
        kFc = str(Fc.u)
        food_sets(Fc)
        base_ = everything(Fc, kFc)
        pre_ = snap(Fc)
        clear_gap()
        run(Fc, 1, 1)
        set_live(Fc, pre_)
        restart(Fc)
        r = run(Fc, 5, 0)
        K.check(everything(Fc, kFc) == base_ and tot(Fc, kFc, "Food_G") == 10, "X37 ... and with the inventory from before the swap: undone, 10 food once (%s)" % r)
        # (d) a cleared stack eaten from inside the window, then a crash: not brought back into the wardrobe
        Fd = Player_(str(UUID.randomUUID()), "Clear")
        kFd = str(Fd.u)
        food_sets(Fd)
        clear_gap()
        rc = run(Fd, 3, 1)
        fs_ = [(c_, i) for c_ in (Fd.sto, Fd.hot, Fd.bak) for i in range(int(c_.getCapacity())) if getc(c_, i) is not None and getc(c_, i)[0] == "Food_G"]
        c_, i_ = fs_[0]
        setc(c_, i_, stack("Food_G", 3, '{"g":2}'))
        after_ = everything(Fd, kFd)
        restart(Fd)
        r = run(Fd, 5, 0)
        K.check(rc.startswith("+Cleared") and len(fs_) == 1 and tot(Fd, kFd, "Food_G") == 3 and everything(Fd, kFd) == after_,
                "X37 a cleared stack eaten from, then a crash: 3 food, never 13 (%s; %s)" % (rc, r))

        # ============================================================ X38 (fixer 2) an admin repair inside the keep window changes nothing
        Fe = Player_(str(UUID.randomUUID()), "Admin")
        kFe = str(Fe.u)
        food_sets(Fe)
        clear_gap()
        run(Fe, 1, 1)
        setc(Fe.hot, 2, stack("Food_G", 6, '{"g":2}'))
        after_ = everything(Fe, kFe)
        notes = AL()
        rr = Tx.repair(Store.get(kFe, Fe.u), Fe.arm, Fe.hot, Fe.sto, Fe.bak, True, notes)
        K.check(rr is None and everything(Fe, kFe) == after_ and Jr.PENDING.containsKey(kFe), "X38 /wardrobeadmin repair (force) on a SAVED change of this run: nothing to repair (%s)" % rr)

        # ============================================================ X39 (fixer 2) the failed move's own slot cannot be restored -> LOCKED
        Fy = Player_(str(UUID.randomUUID()), "Flaky", flaky=True)
        kFy = str(Fy.u)
        for i in range(4):
            setc(Fy.arm, i, stack("Armor_Y_%d" % i, 1))
        run(Fy, 2, 0)
        clear_gap()
        run(Fy, 1, 1)             # put away: the Y set is stored in loadout 1
        clear_gap()
        setc(Fy.arm, 0, stack("Armor_Z_0", 1))
        run(Fy, 2, 1)
        clear_gap()
        Jr.delete(kFy)
        base_ = everything(Fy, kFy)
        Flaky.FAIL_AT, Flaky.STICKY = 0, True      # Z_0 comes off, Y_0 will not go on, and Z_0 will not go back either
        r = run(Fy, 1, 0)
        Flaky.FAIL_ALL, Flaky.STICKY, Flaky.FAIL_AT = False, False, -1
        jy = os.path.join(LD, kFy + ".journal.json")
        K.check(r.startswith("-The change failed and could not be undone") and Store.get(kFy, Fy.u).bad and os.path.isfile(jy) and json.loads(open(jy).read()).get("stage") == "failed",
                "X39 a failed move whose own slot cannot be restored: LOCKED, never 'everything was put back' (%s)" % r)
        notes = AL()
        rr = Tx.repair(Store.get(kFy, Fy.u), Fy.arm, Fy.hot, Fy.sto, Fy.bak, True, notes)
        K.check(rr is not None and not Store.get(kFy, Fy.u).bad and everything(Fy, kFy) == base_ and tot(Fy, kFy, "Armor_Z_0") == 1,
                "X39 ... /wardrobeadmin repair brings the piece back from the journal: every piece once (%s)" % rr)

        # ============================================================ X40 (fixer 2) unreadable armor / hotbar: the journal is kept, the op refused
        Fz = Player_(str(UUID.randomUUID()), "NoRead")
        kFz = str(Fz.u)
        food_sets(Fz)
        base_ = everything(Fz, kFz)
        pre_ = snap(Fz)
        clear_gap()
        run(Fz, 1, 1)
        set_live(Fz, pre_)
        restart(Fz)
        fbz = open(os.path.join(LD, kFz + ".json"), "rb").read()
        dZ = Store.get(kFz, Fz.u)
        rr1 = str(Tx.repair(dZ, Fz.arm, None, Fz.sto, Fz.bak, False, AL()))
        rr2 = str(Tx.repair(dZ, None, Fz.hot, Fz.sto, Fz.bak, True, AL()))
        K.check(rr1.startswith("-Your inventory could not be read") and rr2.startswith("-Your inventory could not be read") and os.path.isfile(os.path.join(LD, kFz + ".journal.json"))
                and open(os.path.join(LD, kFz + ".json"), "rb").read() == fbz and int(dZ.worn) == 1,
                "X40 a repair without the armor / hotbar: the journal and the file are kept, nothing marked undone (%s / %s)" % (rr1, rr2))
        clear_gap()
        r = run(Fz, 5, 0)
        K.check(everything(Fz, kFz) == base_ and not os.path.isfile(os.path.join(LD, kFz + ".journal.json")), "X40 ... the next readable try repairs it (%s)" % r)

        # the log
        logt = open(os.path.join(mods, "Skyy_SkyyWardrobe", "wardrobe.log")).read()
        K.check(all(w in logt for w in ("EQUIP ", "SAVE ", "CLEAR ", "RENAME ", "REPAIR ", "LOCKED ", "ADMIN ")) and "meta" not in logt, "X26 wardrobe.log: one line per kind, no metadata")
        K.check(int(Tx.EQUIPS) > 10 and int(Tx.REPAIRS) >= 16 and int(Tx.ROLLBACKS) >= 3, "X26 counters (equips %d, repairs %d, rollbacks %d)" % (int(Tx.EQUIPS), int(Tx.REPAIRS), int(Tx.ROLLBACKS)))
        P("CfgPub").shutdown()
    except Exception:
        import traceback
        K.check(False, "X crashed: " + traceback.format_exc()[-3000:])
    K.save()


# ====================================================================================================== D: start twice on a live copy
def run_live(step, out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    home = os.path.join(SCRATCH, "live")
    P = lambda n: JClass(PKG + n)
    Paths = JClass("java.nio.file.Paths")
    HL = JClass("com.hypixel.hytale.logger.HytaleLogger")
    # setup()'s order: config load, the store + the start scan, the kit, the bridge function
    P("WdCfg").load(Paths.get(home))
    P("WdStore").ROOT = Paths.get(home).resolve("Skyy_SkyyWardrobe")
    P("WdStore").DIR = P("WdStore").ROOT.resolve("loadouts")
    P("WdStore").LOGF = P("WdStore").ROOT.resolve("wardrobe.log")
    sc = list(P("WdStore").scanAll())
    P("CfgPub").start(Paths.get(home), HL.get("SkyyWardrobeLive"))
    P("WdLog").bridge().put("wardrobe:fn:open", P("WdOpenFn")())
    K.check(sc == [0, 0, 0, 0] and int(P("WdCfg").FREE) == 4, "D %s: no wardrobe files yet, the defaults read (%s)" % (step, sc))
    P("CfgPub").shutdown()
    P("WdJournal").dropAll()
    K.save()


# ====================================================================================================== P / B / AA
def run_perm(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fld = AC.class_.getDeclaredField("permissionGroups")
    fld.setAccessible(True)
    vf = AC.class_.getDeclaredField("variantCommands") if any(str(f.getName()) == "variantCommands" for f in AC.class_.getDeclaredFields()) else None
    for cn in ("WdAdminCmd", "WdAdminArg1Cmd", "WdAdminArg2Cmd", "WdAdminArg3Cmd"):
        c = JClass(PKG + cn)()
        perm, groups = c.getPermission(), fld.get(c)
        K.check(perm is not None and NODE in str(perm), "P. %s requires %s (%s)" % (cn, NODE, perm))
        K.check(groups is not None and len(groups) == 0, "P. %s permission groups empty" % cn)
        if cn == "WdAdminCmd":
            rec = c.getPermissionGroupsRecursive()
            leak = [str(k) for k in rec.keySet() if rec.get(k) is not None and any(NODE in str(x) for x in rec.get(k))]
            K.check(not leak and str(c.getName()) == "wardrobeadmin", "P. /wardrobeadmin gives %s to no group (leak %s)" % (NODE, leak))
    for cn in ("WdCmd", "WdArg1Cmd", "WdArg2Cmd", "WdArg3Cmd"):
        c = JClass(PKG + cn)()
        K.check(list(fld.get(c)) == ["hytale:Adventurer"] and (c.getPermission() is None or NODE not in str(c.getPermission())), "P. %s = hytale:Adventurer" % cn)
    m = JClass(PKG + "WdCmd")()
    K.check(str(m.getName()) == "wardrobe" and sorted(str(a) for a in m.getAliases()) == ["loadout", "loadouts", "wardrobes", "wd"], "P. /wardrobe aliases loadout, loadouts, wd, wardrobes")
    K.save()


def bytecode_calls(CPl, IP, cls, meth):
    cc = CPl.get(cls)
    out = []
    for m in cc.getDeclaredMethods():
        if str(m.getName()) != meth:
            continue
        ca = m.getMethodInfo().getCodeAttribute()
        if ca is None:
            continue
        it, cp = ca.iterator(), m.getMethodInfo().getConstPool()
        while it.hasNext():
            out.append(str(IP.instructionString(it, it.next(), cp)))
    return out


def run_bytecode(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR], verify=False)
    CPl = JClass("javassist.ClassPool")(False)
    CPl.appendSystemPath()
    CPl.appendClassPath(B.SERVER_JAR)
    CPl.appendClassPath(JAR)
    IP = JClass("javassist.bytecode.InstructionPrinter")
    s = bytecode_calls(CPl, IP, PKG + "SkyyWardrobePlugin", "setup")
    names = [re.search(r"\.(\w+)\(\(", l).group(1) for l in s if ("invoke" in l and re.search(r"\.(\w+)\(\(", l))]
    want = ["load", "scanAll", "start", "put", "registerCommand", "registerCommand", "registerGlobal", "registerGlobal", "scheduleWithFixedDelay"]
    seq = [n for n in names if n in set(want)]
    K.check(seq == want, "B setup() order: %s" % seq)
    K.check(not any("registerSystem" in l for l in s), "B no ECS system")
    allcode = []
    for n in zipfile.ZipFile(JAR).namelist():
        if not n.endswith(".class"):
            continue
        cc = CPl.get(n[:-6].replace("/", "."))
        for m in cc.getDeclaredMethods():
            allcode += bytecode_calls(CPl, IP, n[:-6].replace("/", "."), str(m.getName()))
    sets = [l for l in allcode if "setItemStackForSlot" in l]
    rems = [l for l in allcode if "removeItemStackFromSlot" in l]
    K.check(sets and all("(SLcom/hypixel/hytale/server/core/inventory/ItemStack;Z)" in l for l in sets), "B every setItemStackForSlot is (short, ItemStack, boolean)")
    K.check(rems and all("(SZ)" in l for l in rems), "B every removeItemStackFromSlot is (short, boolean)")
    K.check(not any("ItemGridSlot" in l for l in allcode), "B no ItemGridSlot anywhere (icons only, metadata-free)")
    eq = bytecode_calls(CPl, IP, PKG + "WdTx", "equip")
    K.check(any("WdJournal.begin" in l for l in eq) and eq.index(next(l for l in eq if "WdJournal.begin" in l)) < eq.index(next(l for l in eq if "WdTx.put" in l or "WdTx.takeOff" in l)),
            "B the journal is written before the first move")
    K.save()


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
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn or (not JMod_.isPrivate(md) and str(C_.getPackageName()) == str(D.getPackageName()))):
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
    names = [n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(JAR).namelist() if n_.endswith(".class")]
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
        run_mkfake(FAKE_DIR)
        return
    if "--x" in sys.argv:
        run_x(arg("--out"))
        return
    if "--live-step" in sys.argv:
        run_live(arg("--live-step"), arg("--out"))
        return
    if "--perm" in sys.argv:
        run_perm(arg("--out"))
        return
    if "--bc" in sys.argv:
        run_bytecode(arg("--out"))
        return
    if "--audit" in sys.argv:
        run_audit(arg("--out"))
        return
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH)
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp)
    env = dict(os.environ, TEMP=tmp, TMP=tmp)
    # ---- J: the jar
    z = zipfile.ZipFile(JAR)
    names = z.namelist()
    man = json.loads(z.read("manifest.json"))
    classes = sorted(n[:-6].replace("/", ".") for n in names if n.endswith(".class"))
    check(man["Name"] == "%s SkyyWardrobe" % VERSION and man["Main"] == PKG + "SkyyWardrobePlugin" and man["IncludesAssetPack"] is False, "J manifest")
    check(classes == CLASSES, "J exactly the expected classes (extra %s, missing %s)" % (sorted(set(classes) - set(CLASSES)), sorted(set(CLASSES) - set(classes))))
    check(not [n for n in names if not n.endswith(".class") and n != "manifest.json"], "J no asset / .ui / lang file")
    # ---- children
    child(env, "--mkfake")
    for flag, label in (("--x", "X"), ("--perm", "P"), ("--bc", "B")):
        o = os.path.join(SCRATCH, "%s.json" % label)
        child(env, flag, "--out", o)
        take(o, label)
    o = os.path.join(SCRATCH, "AA.json")
    child(env, "--audit", "--out", o)
    if os.path.isfile(o):
        a = json.load(open(o))
        check(not a["refused"] and a["refs"] > 500 and a["classes"] == len(CLASSES), "AA every engine member referenced is accessible (%d refs, %d classes): %s" % (a["refs"], a["classes"], a["refused"][:5]))
        check(len(a["control"]) >= 1, "AA the control class (a protected engine call) IS refused")
    else:
        check(False, "AA wrote no result")
    # ---- D: start twice on a scratch COPY of the live world mods folder
    home = os.path.join(SCRATCH, "live")
    if os.path.isdir(LIVE):
        shutil.copytree(LIVE, home)
        before = tree_hash(home)
        o = os.path.join(SCRATCH, "D1.json")
        child(env, "--live-step", "1", "--out", o)
        take(o, "D1")
        mid = tree_hash(home)
        added = sorted(set(mid) - set(before))
        changed = sorted(k for k in before if k in mid and mid[k] != before[k])
        check(added == ["Skyy_SkyyWardrobe/config.properties"] and not changed, "D start 1: only Skyy_SkyyWardrobe/config.properties appears (added %s, changed %s)" % (added, changed))
        o = os.path.join(SCRATCH, "D2.json")
        child(env, "--live-step", "2", "--out", o)
        take(o, "D2")
        after = tree_hash(home)
        check(after == mid, "D start 2 writes nothing (%s)" % sorted(k for k in set(after) | set(mid) if after.get(k) != mid.get(k)))
        check(not os.path.exists(os.path.join(LIVE, "Skyy_SkyyWardrobe")), "D nothing was written into the live folder itself")
    else:
        check(False, "D the live world mods folder is missing: " + LIVE)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAIL", f)
    if "--keep" not in sys.argv:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
