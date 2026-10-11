"""Harness for SkyyWardrobe 0.2 "Requip" (derived from test_skyywardrobe_0.1.py). Build first:
    python SkyyWardrobe/build_skyywardrobe_0.2.py
    python SkyyWardrobe/test_skyywardrobe_0.2.py [--jar <SkyyWardrobe-0.2.jar>] [--old <SkyyWardrobe-0.1.jar>] [--dir <scratch>]
                                                 [--live <world mods folder>] [--gear <SkyyGear jar>] [--seed N] [--keep]

Parent (plain Python, read only): J the jar (manifest, exactly the expected classes, no asset / .ui / lang file).
Children (fresh JVMs, the game's own JRE, -Xverify:all, -XX:-UsePerfData, java.io.tmpdir in scratch; HytaleServer.jar on the class path):
  F   stand-ins compiled with javassist (FakePr, MapStore, TestPage, FlakyBox, TestPM, TestAssets, LookupIn, BadAccess)
  M01 the 0.1 JAR (SkyyWardrobe-0.1.jar, the SET pin) in its own JVM makes REAL 0.1 files as migration fixtures: stored loadouts + the
      equipped one + an orphan; a crashed equip (a pending 0.1 journal) with the live inventory at the crash; + a scratch COPY of the real
      live 0.1 file (read only)
  X   EVERY NEW CODE PATH on REAL engine containers (SimpleItemContainer, ItemStack with metadata, the real ItemStack.CODEC, a REAL Item
      asset map: Item objects with real ItemArmor slots / ItemWeapon / ItemTool / consumable / max stack / ItemStackContainerConfig, so
      the classifier runs the engine's own getters) with the REAL component lookups (EntityModule / DamageModule / Universe /
      TimeResource primed by reflection) and the real Store.isInThread (its thread field): config (0.1 rows kept, new rows' defaults,
      every check hook), the classifier (P2), the stamp (P1 engine side: withMetadata / withDurability / the codec keep it), deposit /
      Deposit all / caps / refusals, picks, EQUIP (pool trips, the shared item in two loadouts, Keep / Empty, spills, not-with-you,
      kinds, pocket blocks through a fake SkyySacks incl. give-back, keep ids), Take out / fetch / Forget / gone, Use what I wear,
      Returned items, the gate, save / put / rollback failures, CRASH AT EVERY STEP of every transaction (each move, mid-save after every
      file, after the save) with the live inventory as it was AND rolled back to before, chained changes, a random-operation FUZZ with
      the invariant "every item exists exactly once" (live + pool) after every op and every crash, profile switches, the 0.1 MIGRATION
      (fixtures from M01: pending journal repaired first, refused stacks -> Returned items, the equipped loadout asked once, run once, the
      0.1 file untouched, History snapshot = its bytes, a crash in the middle of the first save), unreadable / newer files (shut, never
      written), shard boundaries, the page (every view + click), the commands, every bridge fn (+ off-thread null), the join task,
      the timer, quit, auto-store, and the stamp through SkyyGear's own GearData.put (the SkyyGear jar in the same JVM)
  P   /requip (aliases) + 3 variants = hytale:Adventurer; /requipadmin + 3 variants require skyywardrobe.admin, empty groups (no leak)
  B   BYTECODE: setup() order; every set / remove overload; no ItemGridSlot; the journal before the first move; SkyyGear's GearView.apply /
      GearData.put only write metadata with withMetadata(key, value) (the stamp survives reforge / level-up / identify - spec F2)
  AA  THE ENGINE-ACCESS AUDIT (MethodHandles.privateLookupIn every class; every engine member referenced must be accessible)
  D   START TWICE on a scratch COPY of the live world mods folder (writes nothing), then the live 0.1 file migrates on that COPY
  C   CLASS COMPARE old (0.1) vs new (0.2): kept / added / removed classes and the public members of the kept ones
Scratch: tools/dev/scratch/requip02/test (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, hashlib, time, re, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.2"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


def newest_gear_jar():
    best = None
    for n in os.listdir(os.path.join(ROOT, "SkyyGear")):
        m = re.fullmatch(r"SkyyGear-([0-9.]+)\.jar", n)
        if m:
            v = tuple(int(x) for x in m.group(1).split("."))
            if best is None or v > best[0]:
                best = (v, os.path.join(ROOT, "SkyyGear", n))
    return best[1] if best else ""


JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyWardrobe-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyWardrobe-0.1.jar")))
GEAR = arg("--gear", newest_gear_jar())
SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "requip02", "test")))
SEED = int(arg("--seed", "20261010"))
# X13 fuzz seeds run after the --seed one (requip021: 4242 = the phantom NOT WITH YOU case + 20 more; --fuzz-seeds a,b,c overrides)
FUZZ_SEEDS = [int(x) for x in arg("--fuzz-seeds", "4242,1,2,3,7,11,14,42,99,123,256,777,1001,2026,3141,5150,8080,9001,12345,31337,65535").split(",") if x.strip()]
# requip021fix: COLLIDING-KIND fuzz seeds (the pool = 3 kinds with the SAME metadata: Iron legs / Iron head / Iron sword; 8030 = the stamp lost
# by a failed-save put-back) - each runs --collide-ops random ops; --collide-seeds a,b,c overrides ("-" = none)
COLLIDE_SEEDS = [int(x) for x in arg("--collide-seeds", "8030,7000,7001,7002,7003,8000,8001,8002").split(",") if x.strip() and x.strip() != "-"]
FAKE_DIR = os.path.join(SCRATCH, "fake")
FAKE_PKG = "skyyrqtest"
MAPSTORE = "com.hypixel.hytale.component.SkyyRqTestStore"
TESTPM = "com.hypixel.hytale.server.core.entity.entities.player.pages.SkyyRqTestPM"
PKG = "com.skyy.wardrobe."
NODE = "skyywardrobe.admin"
OURS = ["WdLog", "WdApi", "WdInvApi", "WdEng", "WdCfg", "WdCodec", "WdClass", "WdInv", "Wd01Load", "Wd01Data", "Wd01", "WdEntry", "WdLoad",
        "WdData", "WdStore", "WdJournal", "WdSlots", "WdBridge", "WdMove", "WdTx", "WdGate", "WdAuto", "WdMig", "WdOps", "WdSort", "WdPage",
        "WdRepairTask", "WdHop", "WdOpenTask", "WdFloorTask", "WdAutoTask", "WdFn", "WdTimer", "WdReady", "WdQuit", "WdCmds", "WdScan",
        "WdArg1Cmd", "WdArg2Cmd", "WdArg3Cmd", "WdCmd", "WdAdminArg1Cmd", "WdAdminArg2Cmd", "WdAdminArg3Cmd", "WdAdminCmd", "SkyyWardrobePlugin"]
KITC = ["CfgFile", "CfgFn", "CfgHist", "CfgLog", "CfgPub", "CfgRows", "CfgSaveTask"]
CLASSES = sorted(PKG + c for c in OURS + KITC)
FAILS, OKS = [], [0]

# the test items: id -> (kind, armor slot / max stack / container capacity)
ITEMS = {
    "Armor_Iron_Head": ("armor", 0), "Armor_Iron_Chest": ("armor", 1), "Armor_Iron_Hands": ("armor", 2), "Armor_Iron_Legs": ("armor", 3),
    "Armor_Copper_Head": ("armor", 0), "Armor_Copper_Chest": ("armor", 1), "Armor_Copper_Hands": ("armor", 2), "Armor_Copper_Legs": ("armor", 3),
    "Armor_Gold_Head": ("armor", 0),
    "Weapon_Sword_Iron": ("weapon", 1), "Weapon_Sword_Mithril": ("weapon", 1), "Weapon_Bow_Wood": ("weapon", 1), "Weapon_Kunai_Test": ("plain", 1),
    "Tool_Pickaxe_Iron": ("tool", 1), "Tool_Hatchet_Iron": ("tool", 1),
    "Potion_Health": ("consumable", 25), "Food_Bread": ("consumable", 25),
    "Rock_Stone": ("plain", 100), "Wood_Oak_Log": ("plain", 100), "Ingredient_Bar_Iron": ("plain", 100),
    "Backpack_Test": ("container", 9), "Skyy_Sack_Mining_Normal": ("plain", 1), "Skyy_Menu": ("plain", 1), "Skyy_Vault_Prev": ("plain", 1),
    "Skyy_Unid_Bag_Rare": ("plain", 1), "Skyy_Talisman_Speed": ("plain", 1),
}


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
    F(fb, "public static int FAIL_AT = -1;")
    F(fb, "public static boolean FAIL_ALL = false;")
    F(fb, "public static boolean STICKY = false;")
    F(fb, "public static int SETS = 0;")
    fb.addConstructor(CtNewConstructor.make("public FlakyBox(short n) { super(n); }", fb))
    M(fb, ("public %s setItemStackForSlot(short s, %s i, boolean f) { SETS = SETS + 1; if (FAIL_ALL) return null; "
           "if (FAIL_AT == 0) { FAIL_AT = -1; if (STICKY) FAIL_ALL = true; return null; } if (FAIL_AT > 0) FAIL_AT = FAIL_AT - 1; "
           "return super.setItemStackForSlot(s, i, f); }") % (ISST, IS))
    fb.writeFile(out_dir)
    PP = "com.hypixel.hytale.server.core.entity.entities.player.pages."
    pm = cp.makeClass(TESTPM)
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
        for l in self.code(cls, getter):
            m = re.search(r"(getfield|getstatic) #\d+ = Field ([\w.$]+)\.(\w+)\(", l)
            if m:
                return m.group(2), m.group(3)
        raise KeyError("%s.%s" % (cls, getter))

    def singleton(self, cls):
        c2, f = self.field_of(cls, "get")
        K = self.J(c2)
        fld = self.jf(K, f)
        o = fld.get(None)
        if o is None:
            o = self.U.allocateInstance(K.class_)
            fld.set(None, o)
        return o

    def prime(self, cls, getter, value):
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


def item_map(E):
    """a REAL item asset map: Item objects whose real getters answer (armor slot, weapon, tool, consumable, max stack, container)"""
    J = E.J
    AS = J("com.hypixel.hytale.assetstore.AssetStore")
    st0 = E.U.allocateInstance(J(FAKE_PKG + ".TestAssets").class_)
    am = J("com.hypixel.hytale.assetstore.map.DefaultAssetMap")()
    E.jf(AS, "assetMap").set(st0, am)
    I = J("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    E.jf(I, "ASSET_STORE").set(None, st0)
    inner = E.jf(J("com.hypixel.hytale.assetstore.map.DefaultAssetMap"), "assetMap").get(am)
    Slot = J("com.hypixel.hytale.protocol.ItemArmorSlot")
    IA = J("com.hypixel.hytale.server.core.asset.type.item.config.ItemArmor")
    IW = J("com.hypixel.hytale.server.core.asset.type.item.config.ItemWeapon")
    IT = J("com.hypixel.hytale.server.core.asset.type.item.config.ItemTool")
    CC = J("com.hypixel.hytale.server.core.asset.type.item.config.ItemStackContainerConfig")
    from jpype import JShort
    for iid, (kind, n) in ITEMS.items():
        it = I(iid)
        E.jf(I, "maxStack").setInt(it, n if kind in ("consumable", "plain", "container") and n > 1 else 1)
        if kind == "armor":
            a = E.U.allocateInstance(IA.class_)
            E.jf(IA, "armorSlot").set(a, Slot.values()[n])
            E.jf(I, "armor").set(it, a)
        elif kind == "weapon":
            E.jf(I, "weapon").set(it, E.U.allocateInstance(IW.class_))
        elif kind == "tool":
            E.jf(I, "tool").set(it, E.U.allocateInstance(IT.class_))
        elif kind == "consumable":
            E.jf(I, "consumable").setBoolean(it, True)
        elif kind == "container":
            c = CC()
            E.jf(CC, "capacity").setShort(c, JShort(n))
            E.jf(I, "itemStackContainerConfig").set(it, c)
        inner.put(iid, it)
    return am


def boot(K, scratch_mods, pkg=PKG):
    """the bare engine + the mod's statics pointed at a scratch mods folder; returns a dict of handles"""
    from jpype import JClass, JArray, JString
    E = Eng()
    U = E.U
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "universe")]))
    item_map(E)
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
    World = JClass("com.hypixel.hytale.server.core.universe.world.World")
    world = U.allocateInstance(World.class_)
    Q = JClass("java.util.concurrent.LinkedBlockingDeque")()
    E.jf(World, "acceptingTasks").set(world, JClass("java.util.concurrent.atomic.AtomicBoolean")(True))
    E.jf(World, "taskQueue").set(world, Q)
    E.jf(World, "name").set(world, "requiptest")
    UUID = JClass("java.util.UUID")
    WU = UUID.fromString("00000000-0000-0000-0000-0000000000d1")
    wbu.put(WU, world)
    wmap.put("requiptest", world)
    br = CHM()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    P = lambda n: JClass(pkg + n)
    lines = JClass("java.util.ArrayList")()
    P("WdLog").LINES = lines
    Paths = JClass("java.nio.file.Paths")
    P("WdCfg").load(Paths.get(scratch_mods))
    root = Paths.get(scratch_mods).resolve("Skyy_SkyyWardrobe")
    P("WdStore").ROOT = root
    if pkg == PKG and hasattr(P("WdStore"), "RQ"):
        P("WdStore").DIR01 = root.resolve("loadouts")
        P("WdStore").RQ = root.resolve("requip")
        P("WdStore").LOGF = root.resolve("requip.log")
    else:
        P("WdStore").DIR = root.resolve("loadouts")
        P("WdStore").LOGF = root.resolve("wardrobe.log")
    return {"E": E, "U": U, "uni": uni, "pbu": pbu, "types": types, "world": world, "Q": Q, "WU": WU, "br": br, "lines": lines}


def drain(H):
    n = 0
    while not H["Q"].isEmpty():
        t = H["Q"].poll()
        t.run()
        n += 1
    return n


class World(object):
    """test players on REAL engine containers inside real InventoryComponents in a MapStore (whose Store.thread = this thread)"""

    def __init__(self, H):
        from jpype import JClass, JShort, JByte
        self.H, self.E, self.U, self.types = H, H["E"], H["U"], H["types"]
        self.J = JClass
        self.JShort, self.JByte = JShort, JByte
        self.UUID = JClass("java.util.UUID")
        self.IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
        self.BD = JClass("org.bson.BsonDocument")
        self.SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
        self.Flaky = JClass(FAKE_PKG + ".FlakyBox")
        self.MapStore, self.FakePr = JClass(MAPSTORE), JClass(FAKE_PKG + ".FakePr")
        self.IdM = JClass("java.util.IdentityHashMap")
        INV = "com.hypixel.hytale.server.core.inventory.InventoryComponent$"
        self.Arm, self.Hot, self.Sto, self.Bak = JClass(INV + "Armor"), JClass(INV + "Hotbar"), JClass(INV + "Storage"), JClass(INV + "Backpack")
        self.RefC = JClass("com.hypixel.hytale.component.Ref")
        self.Player = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
        self.TestPM = JClass(TESTPM)
        self.TR = JClass("com.hypixel.hytale.server.core.modules.time.TimeResource")
        self.Inst = JClass("java.time.Instant")
        self.Thread = JClass("java.lang.Thread")
        self.hotreg = {}

    def stack(self, i, q=1, meta=None):
        return self.IS(i, q, 100.0, 100.0, 0, self.BD.parse(meta) if meta else None)

    def player(self, uid, name, flaky=False, bak=9):
        W = self
        S = self.JShort

        class P_(object):
            pass
        p = P_()
        p.u = W.UUID.fromString(uid)
        p.name = name
        p.arm = W.Flaky(S(4)) if flaky else W.SIC(S(4))
        p.hot, p.sto, p.bak = W.SIC(S(9)), W.SIC(S(36)), W.SIC(S(bak))
        p.st = W.MapStore()
        p.st.comps = W.IdM()
        W.E.jf(W.J("com.hypixel.hytale.component.Store"), "thread").set(p.st, W.Thread.currentThread())
        p.ref = W.U.allocateInstance(W.RefC.class_)
        W.E.jf(W.RefC, "store").set(p.ref, p.st)
        p.pr = W.FakePr()
        p.pr.fu, p.pr.fname, p.pr.fref, p.pr.fworld = p.u, name, p.ref, W.H["WU"]
        p.pla = W.U.allocateInstance(W.Player.class_)
        W.E.jf(W.Player, "pageManager").set(p.pla, W.TestPM())
        m = W.IdM()
        m.put(W.types["pr"], p.pr)
        m.put(W.types["pla"], p.pla)
        m.put(W.types["arm"], W.Arm(p.arm))
        m.put(W.types["hot"], W.Hot(p.hot, W.JByte(0)))
        m.put(W.types["sto"], W.Sto(p.sto))
        m.put(W.types["bak"], W.Bak(p.bak))
        p.st.comps.put(p.ref, m)
        tr = W.U.allocateInstance(W.TR.class_)
        W.E.jf(W.TR, "now").set(tr, W.Inst.now())
        p.st.res = tr
        W.H["pbu"].put(p.u, p.pr)
        p.secs = [p.arm, p.hot, p.sto, p.bak]
        W.hotreg[str(p.u)] = p.hot
        return p

    def setc(self, c, i, s):
        c.setItemStackForSlot(self.JShort(i), s, False)

    def getc(self, c, i):
        s = c.getItemStack(self.JShort(i))
        return None if s is None or s.isEmpty() else s

    def snap(self, p):
        """the live inventory as it is (the engine's last save)"""
        out = []
        for c in p.secs:
            out.append([c.getItemStack(self.JShort(i)) for i in range(int(c.getCapacity()))])
        return out

    def restore(self, p, sn):
        for c, sl in zip(p.secs, sn):
            for i, s in enumerate(sl):
                if s is None or s.isEmpty():
                    c.removeItemStackFromSlot(self.JShort(i), False)
                else:
                    c.setItemStackForSlot(self.JShort(i), s, False)

    def clear(self, p):
        for c in p.secs:
            for i in range(int(c.getCapacity())):
                c.removeItemStackFromSlot(self.JShort(i), False)

    def dump(self, p, Codec):
        out = []
        for c in p.secs:
            sec = []
            for i in range(int(c.getCapacity())):
                s = c.getItemStack(self.JShort(i))
                sec.append(None if s is None or s.isEmpty() else json.loads(str(Codec.toJson(Codec.slotDoc(i, s)))))
            out.append(sec)
        return out

    def load(self, p, dumpd, Codec):
        self.clear(p)
        for c, sec in zip(p.secs, dumpd):
            for i, sd in enumerate(sec):
                if sd is not None:
                    c.setItemStackForSlot(self.JShort(i), Codec.stackOf(self.BD.parse(json.dumps(sd))), False)


GEARDOC = '{"SkyyGear": {"v": 1, "r": "%s", "lvl": %d, "id": true}}'


def gdoc(r, lv):
    return GEARDOC % (r, lv)


def fake_bridges(br, state):
    """SkyyPets / SkyyClasses / SkyySkills / SkyyProfiles / SkyySacks stand-ins (state = a dict the test changes)"""
    from jpype import JImplements, JOverride, JArray, JObject, JInt, JLong

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, a):
            return self.f(a)

    calls = state.setdefault("calls", {"pets": [], "abil": [], "take": [], "put": [], "commit": [], "deposit": []})

    def pets_set(a):
        calls["pets"].append((str(a[0]), str(a[1]), str(a[2])))
        state["pets"] = str(a[1]) + "|" + str(a[2])
        return "+Pets set."

    def abil_set(a):
        calls["abil"].append(str(a[1]))
        state["abil"] = str(a[1])
        return "+Abilities set."

    def bag(a):
        return state.setdefault("bags", {}).setdefault(str(a[0]), {})

    def take(a):
        b, q = bag(a), int(a[2])
        have = b.get(str(a[1]), 0)
        g = min(have, q)
        b[str(a[1])] = have - g
        calls["take"].append((str(a[1]), g))
        return JLong(g)

    def put(a):
        b = bag(a)
        b[str(a[1])] = b.get(str(a[1]), 0) + int(a[2])
        calls["put"].append((str(a[1]), int(a[2])))
        return JLong(int(a[2]))

    def commit(a):
        calls["commit"].append((str(a[1]), int(a[2])))
        return JLong(int(a[2]))

    def deposit(a):
        """the REAL SkyySacks 0.7.17 contract: {UUID, id, Long n, Integer hotbar slot}; the 3-argument form is refused (0); takes up to n
        of the plain stack IN THAT HOTBAR SLOT (read from the slot itself), what does not fit stays there"""
        from jpype import JShort
        if len(a) < 4 or a[3] is None:
            calls.setdefault("deposit3", []).append(str(a[1]))
            return JLong(0)
        hb = state.get("hotreg", {}).get(str(a[0]))
        slot = int(a[3])
        if hb is None:
            return JLong(0)
        s = hb.getItemStack(JShort(slot))
        if s is None or s.isEmpty() or str(s.getItemId()) != str(a[1]) or (s.getMetadata() is not None and not s.getMetadata().isEmpty()):
            return JLong(0)
        b, q = bag(a), int(a[2])
        acc = min(q, int(s.getQuantity()), state.get("bagRoom", 10 ** 9))
        if acc <= 0:
            return JLong(0)
        if acc == int(s.getQuantity()):
            hb.removeItemStackFromSlot(JShort(slot), False)
        else:
            hb.setItemStackForSlot(JShort(slot), s.withQuantity(int(s.getQuantity()) - acc), False)
        b[str(a[1])] = b.get(str(a[1]), 0) + acc
        calls["deposit"].append((str(a[1]), acc, slot))
        return JLong(acc)

    def count(a):
        return JLong(bag(a).get(str(a[1]), 0))

    def all_(u):
        """sacks:fn:all UUID -> HashMap id -> Long (SkyySacks 0.7.16+)"""
        from jpype import JClass
        m = JClass("java.util.HashMap")()
        for k_, v_ in state.setdefault("bags", {}).get(str(u), {}).items():
            m.put(k_, JLong(v_))
        return m
    fns = {"pets:fn:loadoutGet": lambda u: state.get("pets", "pA|sA"), "pets:fn:loadoutSet": pets_set,
           "pets:fn:petName": lambda a: "Pet-" + str(a[1]), "class:fn:loadoutGet": lambda u: state.get("abil", "v=1;class=Mage;p1=Meteor;n1=Meteor"),
           "class:fn:loadoutSet": abil_set, "profile:fn:key": lambda u: state.get("key", {}).get(str(u), str(u)),
           "skill:fn:overall": lambda u: JArray(JObject)([JInt(state.get("overall", 0)), JInt(0)]),
           "sacks:fn:take": take, "sacks:fn:put": put, "sacks:fn:commit": commit, "sacks:fn:deposit": deposit, "sacks:fn:count": count, "sacks:fn:all": all_}
    objs = {}
    for k, f in fns.items():
        objs[k] = Fn(f)
        br.put(k, objs[k])
    return objs


# ====================================================================================================== child M01: REAL 0.1 files
def run_mk01(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, OLD, FAKE_DIR])
    fx = os.path.join(SCRATCH, "fx01")
    mods = os.path.join(fx, "mods")
    shutil.rmtree(fx, ignore_errors=True)
    os.makedirs(mods)
    H = boot(K, mods)
    W = World(H)
    P = lambda n: JClass(PKG + n)
    Codec, Ops, Tx, Gate, Store, Jr = P("WdCodec"), P("WdOps"), P("WdTx"), P("WdGate"), P("WdStore"), P("WdJournal")
    state = {"pets": "petA|sumA", "abil": "v=1;class=Priest;p1=SacredHeal;n1=Sacred Heal"}
    fake_bridges(H["br"], state)
    meta = {}
    # ---- A: loadout 1 stores a full set (+ potion, a block, a bag, a bow orphan), loadout 2 is EQUIPPED (its gear is on the player)
    A = W.player("00000000-0000-0000-0000-0000000001a1", "Ann")
    for i, a in enumerate(["Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs"]):
        W.setc(A.arm, i, W.stack(a, 1, gdoc("rare", 12 + i)))
    W.setc(A.hot, 0, W.stack("Weapon_Sword_Iron", 1, gdoc("legendary", 20)))
    W.setc(A.hot, 1, W.stack("Potion_Health", 5))
    W.setc(A.hot, 2, W.stack("Rock_Stone", 64))
    W.setc(A.hot, 3, W.stack("Backpack_Test", 1))
    W.setc(A.hot, 4, W.stack("Armor_Gold_Head", 1))          # armor in a hotbar slot (0.1 allowed it)
    W.setc(A.hot, 8, W.stack("Skyy_Menu", 1))
    r1 = str(Ops.run(A.pr, A.ref, A.st, 2, 0, None))
    Gate.LAST.clear()
    r2 = str(Ops.run(A.pr, A.ref, A.st, 4, 0, "Combat"))
    r3 = str(Ops.run(A.pr, A.ref, A.st, 1, 1, None))          # equip the EMPTY loadout 2: the gear goes home into loadout 1
    Gate.LAST.clear()
    W.setc(A.arm, 0, W.stack("Armor_Copper_Head", 1, gdoc("unique", 5)))
    W.setc(A.arm, 1, W.stack("Armor_Copper_Chest", 1))
    W.setc(A.hot, 0, W.stack("Tool_Pickaxe_Iron", 1, gdoc("normal", 3)))
    state["pets"] = "petB|"
    r4 = str(Ops.run(A.pr, A.ref, A.st, 2, 1, None))          # save current 2 (the equipped one: pets + abilities only)
    d = Store.get(str(A.u), A.u)
    d.orphan("loadout0:hotbar:6:test", W.stack("Weapon_Bow_Wood", 1, gdoc("rare", 7)))
    d.rev = d.rev + 1
    Store.save(d)
    K.check(r1.startswith("+Saved") and r3.startswith("+Equipped Loadout 2") and r4.startswith("+Saved") and d.worn == 1
            and d.slots[0].count() == 9 and d.orphans.size() == 1, "M01 A: loadout 1 stores 9 stacks + an orphan, loadout 2 is equipped (%s / %s / %s / %s)" % (r1, r2, r3, r4))
    meta["A"] = {"key": str(A.u), "live": W.dump(A, Codec)}
    # ---- B: loadout 1 stores gold head + a mithril sword; equipping it "crashes" after one move: a pending (moving) 0.1 journal
    Bo = W.player("00000000-0000-0000-0000-0000000001b2", "Bo")
    W.setc(Bo.arm, 0, W.stack("Armor_Gold_Head", 1, gdoc("fabled", 30)))
    W.setc(Bo.hot, 0, W.stack("Weapon_Sword_Mithril", 1, gdoc("mythic", 40)))
    W.setc(Bo.hot, 1, W.stack("Food_Bread", 7))
    Ops.run(Bo.pr, Bo.ref, Bo.st, 2, 0, None)
    Gate.LAST.clear()
    Ops.run(Bo.pr, Bo.ref, Bo.st, 1, 1, None)
    Gate.LAST.clear()
    W.setc(Bo.arm, 0, W.stack("Armor_Copper_Head", 1))
    W.setc(Bo.hot, 0, W.stack("Weapon_Bow_Wood", 1))
    Tx.CRASH_AT = 1
    crashed = False
    try:
        Ops.run(Bo.pr, Bo.ref, Bo.st, 1, 0, None)
    except Exception as e:
        crashed = "harness crash" in str(e)
    Tx.CRASH_AT = -1
    jf = os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", str(Bo.u) + ".journal.json")
    K.check(crashed and os.path.isfile(jf) and json.load(open(jf))["stage"] == "moving", "M01 B: a crashed 0.1 equip left a pending journal")
    meta["B"] = {"key": str(Bo.u), "live": W.dump(Bo, Codec)}
    json.dump(meta, open(os.path.join(fx, "meta.json"), "w"), indent=1)
    K.save()


# ====================================================================================================== child X
def run_x(out):
    from jpype import JClass, JImplements, JOverride, JArray, JObject, JString, JInt, JShort, JLong, JByte
    K = Child(out)
    cp = [B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR] + ([GEAR] if GEAR and os.path.isfile(GEAR) else [])
    _jvm(cp)
    mods = os.path.join(SCRATCH, "x-mods")
    shutil.rmtree(mods, ignore_errors=True)
    os.makedirs(mods)
    H = boot(K, mods)
    W = World(H)
    E, U, types, br = H["E"], H["U"], H["types"], H["br"]
    P = lambda n: JClass(PKG + n)
    Cfg, Store, Tx, Ops, Gate, Jr, Slots, Brg, Codec, Cls, Inv, Mig, Auto = (P("WdCfg"), P("WdStore"), P("WdTx"), P("WdOps"), P("WdGate"),
                                                                              P("WdJournal"), P("WdSlots"), P("WdBridge"), P("WdCodec"), P("WdClass"),
                                                                              P("WdInv"), P("WdMig"), P("WdAuto"))
    Paths = JClass("java.nio.file.Paths")
    Auto.load(Paths.get(mods).resolve("Skyy_SkyyWardrobe").resolve("requip").resolve("autostore.json"))
    state = {"hotreg": W.hotreg}
    fns = fake_bridges(br, state)
    stack, setc, getc = W.stack, W.setc, W.getc
    UUID_ = JClass("java.util.UUID")
    Wd = os.path.join(mods, "Skyy_SkyyWardrobe")

    def ein(e):
        return bool(getattr(e, "in_")) if hasattr(e, "in_") else bool(getattr(e, "in"))

    def jn(v):
        if isinstance(v, dict):
            for k_ in ("$numberInt", "$numberLong"):
                if k_ in v:
                    return int(v[k_])
        return v

    def ukey(s):
        s2 = Codec.unstamp(s)
        md = s2.getMetadata()
        return (str(s2.getItemId()), "" if md is None or md.isEmpty() else str(md.toJson()))

    def census(p, k=None):
        """every physical item once: live (stamp stripped) + the pool FILES (IN gear, kind counts) + Returned items"""
        k = k or str(Store.pkey(p.u))
        d = Store.load(k, str(p.u))
        tot = {}

        def add(s, q):
            kk = ukey(s)
            tot[kk] = tot.get(kk, 0) + q
        for c in p.secs:
            for i in range(int(c.getCapacity())):
                s = c.getItemStack(JShort(i))
                if s is not None and not s.isEmpty():
                    add(s, int(s.getQuantity()))
        for e in d.entries.values():
            if e.kind and e.stack is not None:
                add(e.stack, int(e.count))
            elif ein(e) and e.stack is not None:
                add(e.stack, int(e.stack.getQuantity()))
        for o in d.orphans:
            s = Codec.stackOf(o.asDocument())
            if s is not None:
                add(s, int(s.getQuantity()))
        return {kk: v for kk, v in tot.items() if v}, d

    def once(p, d=None, allow_out=()):
        """every gear entry exactly once: IN in the pool XOR its stamp in the live inventory; no live stamp the pool does not know"""
        if d is None:
            _c, d = census(p)
        live = {}
        for c in p.secs:
            for i in range(int(c.getCapacity())):
                e = Codec.stampOf(c.getItemStack(JShort(i)))
                if e is not None:
                    live[str(e)] = live.get(str(e), 0) + 1
        bad = []
        for e in d.entries.values():
            if e.kind:
                continue
            n = (1 if ein(e) else 0) + live.get(str(e.eid), 0)
            if n != 1 and not (n == 0 and str(e.eid) in allow_out):
                bad.append("%s %s in=%s live=%d" % (e.eid, e.itemId(), ein(e), live.get(str(e.eid), 0)))
        for k_ in live:
            if d.entry(k_) is None:
                bad.append("live stamp %s unknown to the pool" % k_)
            elif live[k_] > 1:
                bad.append("stamp %s on %d stacks" % (k_, live[k_]))
        return bad

    def run(p, op, n=0, a=None):
        return str(Ops.run(p.pr, p.ref, p.st, op, n, a))

    def gap():
        Gate.LAST.clear()

    def restart():
        """a server restart: memory gone (cache, pending journals, busy flags)"""
        Store.CACHE.clear()
        Jr.PENDING.clear()
        Gate.BUSY.clear()
        Tx.KEPT.clear()
        Auto.SEEN.clear()

    def jresolved(k):
        """the journal is resolved: gone, or (fixer 2, data critic 2) a SAVED journal of older saved steps still inside the keep window"""
        f = os.path.join(Wd, "requip", k, "journal.json")
        if not os.path.isfile(f):
            return True
        j = json.load(open(f))
        return j.get("stage") == "saved" and bool(Jr.PENDING.containsKey(k)) and all(st_.get("savedAt") is not None for st_ in j.get("steps", []))

    def stamps_of(p):
        return [str(Codec.stampOf(c.getItemStack(JShort(i)))) for c in p.secs for i in range(int(c.getCapacity())) if Codec.stampOf(c.getItemStack(JShort(i))) is not None]

    def ent_by_id(d, iid):
        return [e for e in d.entries.values() if str(e.itemId()) == iid]

    try:
        # ============================================================ A: every class loads + verifies + initialises
        Cls_, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
        bad = []
        for cn in CLASSES:
            try:
                Cls_.forName(cn, True, loader)
            except Exception as e:
                bad.append("%s: %s" % (cn, e))
        K.check(not bad, "A. every class loads, verifies (-Xverify:all) and initialises: %s" % bad)

        # ============================================================ X1 config: 0.1 rows kept, new rows' defaults, checks, Server Setup
        cfgf = os.path.join(Wd, "config.properties")
        txt = open(cfgf).read()
        K.check("slots.free=4" in txt and "space.armorCap=1000" in txt and "autoStore.enabled=true" in txt and "swap.strict=false" in txt, "X1 a fresh default config.properties holds the 0.1 rows and the new rows")
        K.check(int(Cfg.ARMOR_CAP) == 1000 and int(Cfg.ITEMS_CAP) == 1000 and int(Cfg.shard()) == 100 and not bool(Cfg.DEP_HOT) and bool(Cfg.POCKET)
                and int(Cfg.POCKET_N) == 0 and bool(Cfg.POCKET_BACK) and bool(Cfg.AUTO_ON) and int(Cfg.AUTO_S) == 2 and int(Cfg.FREE) == 4
                and str(Cfg.DENY_IDS) == "-" and str(Cfg.ALLOW_IDS) == "-", "X1 every new row reads its default")
        # the LIVE 0.1 file (no new keys): the new rows keep their defaults, the 0.1 values stay
        old01 = ("wardrobe.enabled=true\nslots.free=4\nslots.max=18\nslots.byLevel=6:10,10:20,14:30,18:40\nswap.hotbar=true\nswap.strict=false\n"
                 "swap.keepIds=Skyy_Menu,Skyy_Vault_*\nswap.gapSeconds=1\ncombatSeconds=10\nafterSwitchSeconds=30\njournalKeepSeconds=30\nnameMax=16\n")
        live_cfg = os.path.join(LIVE, "Skyy_SkyyWardrobe", "config.properties")
        if os.path.isfile(live_cfg):
            old01 = open(live_cfg, encoding="latin-1").read()
        open(cfgf, "w", encoding="latin-1").write(old01)
        Cfg.reloadAll()
        K.check(int(Cfg.ARMOR_CAP) == 1000 and bool(Cfg.POCKET) and int(Cfg.FREE) == 4 and list(Cfg.keepList()) == ["Skyy_Menu", "Skyy_Vault_*"],
                "X1 a 0.1 config.properties (the live one): 0.1 values kept, new rows at their defaults, nothing rewritten")
        K.check(open(cfgf, encoding="latin-1").read() == old01, "X1 ... and the file is byte for byte the same")
        K.check(Cfg.checkIds("items.deny", "Foo_*,Bar") is None and Cfg.checkIds("items.deny", "*") is not None and Cfg.checkIds("items.allow", "a b") is not None,
                "X1 check= on items.deny / items.allow")
        P("CfgPub").start(Paths.get(mods), None)
        cfn = br.get("config:fn:SkyyWardrobe")

        def cop(*args):
            a = JArray(JObject)(len(args))
            for i, x in enumerate(args):
                a[i] = x
            return cfn.apply(a)
        r = cop("set", "items.allow", "Weapon_Kunai_*", None, None, "yes", "console")
        r2 = cop("set", "items.deny", "**", None, None, "yes", "console")
        K.check(str(r[0]) == "ok" and str(r2[0]) != "ok" and bool(Cfg.allow("Weapon_Kunai_Test")) and str(cop("get", "space.itemsCap")) == "1000",
                "X1 Server Setup (config:fn): set / check refuses / get (%s / %s)" % (list(r), list(r2)))
        P("CfgPub").flush()

        # ============================================================ X2 the classifier (P2: the engine's own Item getters)
        cl = lambda iid, q=1, m=None: str(Cls.classify(stack(iid, q, m)))
        K.check([cl(x) for x in ("Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs")] == ["a0", "a1", "a2", "a3"],
                "X2 armor -> its armor slot (getArmor().getArmorSlot(): Head, Chest, Hands, Legs = 0-3)")
        K.check(cl("Weapon_Sword_Iron") == "i" and cl("Tool_Pickaxe_Iron") == "i" and cl("Potion_Health", 5) == "i" and cl("Weapon_Kunai_Test") == "i",
                "X2 weapon / tool / consumable / items.allow -> Items")
        refused = {x: cl(x) for x in ("Rock_Stone", "Ingredient_Bar_Iron", "Backpack_Test", "Skyy_Sack_Mining_Normal", "Skyy_Menu", "Skyy_Vault_Prev",
                                      "Skyy_Unid_Bag_Rare", "Skyy_Talisman_Speed", "Gone_Item")}
        K.check(all(v.startswith("-") for v in refused.values()) and "Magic Bags" in refused["Rock_Stone"] and "holds items" in refused["Backpack_Test"]
                and "Identify" in refused["Skyy_Unid_Bag_Rare"] and "Accessory" in refused["Skyy_Talisman_Speed"] and "no longer knows" in refused["Gone_Item"],
                "X2 refused: blocks, materials, a container item, a bag, the menu item, vault arrows, a mystery bag, a talisman, an unknown id (%s)" % refused)
        K.check(cl("Weapon_Sword_Iron", 1, '{"SkyyGear": {"r": "rare", "id": false}}').startswith("-Identify"), "X2 unidentified gear (SkyyGear id:false) is refused")
        Cfg.DENY_IDS = "Weapon_Bow_*"
        K.check(cl("Weapon_Bow_Wood").startswith("-The server"), "X2 items.deny")
        Cfg.DENY_IDS = "-"
        K.check(bool(Cls.unique(stack("Weapon_Sword_Iron"))) and not bool(Cls.unique(stack("Potion_Health", 3))) and int(Codec.maxStack("Potion_Health")) == 25,
                "X2 gear = max stack 1 (one entry each); potions = a kind")

        # ============================================================ X3 the stamp (P1 engine side) + the lossless format
        g = stack("Weapon_Sword_Iron", 1, gdoc("rare", 12))
        g.setOverrideDroppedItemAnimation(True)
        s1 = Codec.stamp(g, "00aa00aa00aa00aa")
        K.check(str(Codec.stampOf(s1)) == "00aa00aa00aa00aa" and str(Codec.rar(s1)) == "rare" and int(Codec.lv(s1)) == 12 and s1.getOverrideDroppedItemAnimation()
                and Codec.stampOf(g) is None, "X3 stamp: the eid rides along, the SkyyGear document + the drop animation flag are kept, the original is untouched")
        s2 = Codec.unstamp(s1)
        K.check(Codec.stampOf(s2) is None and Codec.same(s2, g) and Codec.same(Codec.unstamp(stack("Weapon_Sword_Iron")), stack("Weapon_Sword_Iron")),
                "X3 unstamp gives back exactly the plain item")
        s3 = Codec.unstamp(Codec.stamp(stack("Tool_Pickaxe_Iron"), "x"))
        K.check(s3.getMetadata() is None, "X3 unstamping an item that had no metadata leaves NO empty document (stacks / recipes as before)")
        d1 = s1.withDurability(40.0)
        K.check(str(Codec.stampOf(d1)) == "00aa00aa00aa00aa" and abs(float(d1.getDurability()) - 40.0) < 1e-6, "X3 P1: durability loss (withDurability) keeps the stamp")
        rt = Codec.stackOf(JClass("org.bson.BsonDocument").parse(str(Codec.toJson(Codec.slotDoc(0, s1)))))
        K.check(Codec.same(rt, s1) and str(Codec.stampOf(rt)) == "00aa00aa00aa00aa" and rt.getOverrideDroppedItemAnimation(), "X3 the lossless slot format (codec + explicit fields) keeps the stamp")
        ITEMCODEC = JClass("com.hypixel.hytale.server.core.inventory.ItemStack").CODEC
        rt2 = ITEMCODEC.decode(ITEMCODEC.encode(s1))
        K.check(str(Codec.stampOf(rt2)) == "00aa00aa00aa00aa", "X3 P1: the engine's own ItemStack.CODEC (player saves) keeps the stamp")

        # ============================================================ X4 deposit (single), kinds, refusals, caps
        A = W.player("00000000-0000-0000-0000-00000000000a", "Alice")
        kA = str(A.u)
        setc(A.sto, 0, stack("Armor_Iron_Head", 1, gdoc("rare", 12)))
        setc(A.sto, 1, stack("Potion_Health", 5))
        setc(A.sto, 2, stack("Potion_Health", 7))
        setc(A.sto, 3, stack("Rock_Stone", 64))
        setc(A.hot, 8, stack("Skyy_Menu", 1))
        base, _ = census(A)
        r = run(A, 6, 0, "2:0")
        d = Store.get(kA, A.u)
        e0 = ent_by_id(d, "Armor_Iron_Head")
        K.check(r.startswith("+Into Requip: Armor_Iron_Head") and getc(A.sto, 0) is None and len(e0) == 1 and ein(e0[0]) and e0[0].space == 0 and e0[0].spot == 0
                and str(Codec.stampOf(e0[0].stack)) == str(e0[0].eid) and str(e0[0].rar) == "rare", "X4 deposit a helmet: Armor space, Head spot, IN, the stored copy carries its eid (%s)" % r)
        r = run(A, 6, 0, "2:1")
        r2 = run(A, 6, 0, "2:2")
        d = Store.get(kA, A.u)
        pk = ent_by_id(d, "Potion_Health")
        K.check(r.startswith("+") and r2.startswith("+") and len(pk) == 1 and pk[0].kind and int(pk[0].count) == 12 and int(pk[0].stack.getQuantity()) == 1,
                "X4 two potion stacks: ONE kind entry with count 12 (template qty 1)")
        r = run(A, 6, 0, "2:3")
        r2 = run(A, 6, 0, "1:8")
        K.check(r.startswith("-Blocks and materials go in your Magic Bags") and r2.startswith("-The SkyWynn Menu item") and getc(A.sto, 3) is not None,
                "X4 a block and the menu item are refused, nothing moves (%s / %s)" % (r, r2))
        c_after, dA = census(A)
        K.check(c_after == base and not once(A, dA), "X4 conservation + exactly once")
        jfile = os.path.join(Wd, "requip", kA, "journal.json")
        K.check(os.path.isfile(jfile) and json.load(open(jfile))["stage"] == "saved" and Jr.PENDING.containsKey(kA), "X4 the journal is kept (saved) inside its keep window")
        jd = json.load(open(jfile))
        K.check(len(jd["steps"]) == 3 and all(st["op"] == "deposit" for st in jd["steps"]) and jd["steps"][0]["moves"][0]["fresh"] is True
                and jn(jd["steps"][0]["moves"][0]["kb"]) == 1 and jn(jd["steps"][2]["moves"][0]["cnt"]) == 5, "X4 chained steps, each with its evidence (kb / cnt)")
        Cfg.ARMOR_CAP = 1
        setc(A.sto, 5, stack("Armor_Iron_Chest", 1))
        r = run(A, 6, 0, "2:5")
        K.check(r.startswith("-Armor space full (1)") and getc(A.sto, 5) is not None, "X4 a full space refuses, nothing moves (%s)" % r)
        Cfg.ARMOR_CAP = 1000
        files = sorted(os.listdir(os.path.join(Wd, "requip", kA)))
        K.check(files == ["armor-000.json", "index.json", "items-000.json", "journal.json", "loadouts.json", "orphans.json"],
                "X4 the profile folder: index + shards + loadouts + orphans + journal (%s)" % files)
        ix = json.load(open(os.path.join(Wd, "requip", kA, "index.json")))
        K.check(jn(ix["format"]) == 2, "X4 index.json format 2")

        # ============================================================ X5 Deposit all (storage + backpack; the hotbar only with deposit.hotbar)
        Bea = W.player("00000000-0000-0000-0000-00000000000b", "Bea")
        kB = str(Bea.u)
        for i, a in enumerate(["Armor_Copper_Head", "Armor_Copper_Chest", None, "Armor_Copper_Legs"]):
            if a:
                setc(Bea.arm, i, stack(a, 1, gdoc("unique", 5 + i)))
        setc(Bea.hot, 0, stack("Tool_Pickaxe_Iron", 1, gdoc("normal", 3)))
        setc(Bea.hot, 1, stack("Food_Bread", 3))
        setc(Bea.hot, 8, stack("Skyy_Menu", 1))
        for i, a in enumerate(["Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs"]):
            setc(Bea.sto, i, stack(a, 1, gdoc("rare", 20 + i)))
        setc(Bea.sto, 4, stack("Weapon_Sword_Iron", 1, gdoc("rare", 15)))
        setc(Bea.sto, 5, stack("Weapon_Sword_Mithril", 1, gdoc("legendary", 30)))
        setc(Bea.sto, 6, stack("Potion_Health", 10))
        setc(Bea.sto, 7, stack("Rock_Stone", 64))
        setc(Bea.bak, 0, stack("Weapon_Bow_Wood", 1, gdoc("rare", 9)))
        setc(Bea.hot, 2, stack("Tool_Hatchet_Iron", 1))
        baseB, _ = census(Bea)
        r = run(Bea, 7)
        dB = Store.get(kB, Bea.u)
        K.check(r.startswith("+Deposited 8 stacks (1 stayed out: Blocks and materials go in your Magic Bags") and getc(Bea.sto, 7) is not None
                and getc(Bea.hot, 2) is not None and getc(Bea.hot, 0) is not None and dB.count(0) == 4 and dB.count(1) == 4,
                "X5 Deposit all: storage + backpack in (4 armor, 3 weapons, 1 potion kind), the block stays, the HOTBAR is untouched (%s)" % r)
        Cfg.DEP_HOT = True
        r = run(Bea, 7)
        Cfg.DEP_HOT = False
        K.check(r.startswith("+Deposited 3 stacks") and getc(Bea.hot, 2) is None and getc(Bea.hot, 8) is not None and getc(Bea.hot, 0) is None,
                "X5 deposit.hotbar on: the hotbar too, never the SkyWynn Menu item (%s)" % r)
        r = run(Bea, 7)
        K.check(r.startswith("-Nothing could go in: Blocks") , "X5 nothing left but the block: refused with the reason (%s)" % r)
        cB, dB = census(Bea)
        K.check(cB == baseB and not once(Bea, dB), "X5 conservation + exactly once")
        # take the hatchet + pickaxe + bread back out for the equip tests (Take out = plain items again)
        for iid in ("Tool_Pickaxe_Iron", "Tool_Hatchet_Iron"):
            r = run(Bea, 8, 0, str(ent_by_id(Store.get(kB, Bea.u), iid)[0].eid))
            K.check(r.startswith("+Taken out: " + iid + " - it is a plain item again"), "X8 Take out %s (%s)" % (iid, r))
        r = run(Bea, 8, 0, str(ent_by_id(Store.get(kB, Bea.u), "Food_Bread")[0].eid))
        dB = Store.get(kB, Bea.u)
        K.check(r.startswith("+Taken out: Food_Bread x3") and not ent_by_id(dB, "Food_Bread") and not stamps_of(Bea), "X8 Take out a kind: the whole count (3), the empty unpicked kind entry goes, nothing stamped")
        cB, dB = census(Bea)
        K.check(cB == baseB and not once(Bea, dB), "X8 conservation after Take out")
        # move the taken-out items back to where the equip test wants them
        for c in Bea.secs:
            for i in range(int(c.getCapacity())):
                s = getc(c, i)
                if s is not None and str(s.getItemId()) in ("Tool_Pickaxe_Iron", "Food_Bread") and c is not Bea.hot:
                    c.removeItemStackFromSlot(JShort(i), False)
                    setc(Bea.hot, 0 if str(s.getItemId()) == "Tool_Pickaxe_Iron" else 1, s)

        # ============================================================ X6 picks (references only: no item moves)
        dB = Store.get(kB, Bea.u)
        eid = lambda iid: str(ent_by_id(Store.get(kB, Bea.u), iid)[0].eid)
        snapB = W.snap(Bea)
        res = [run(Bea, 10, 0, "%d|e:%s" % (k_, eid(a))) for k_, a in enumerate(["Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs"])]
        res.append(run(Bea, 10, 0, "4|e:" + eid("Weapon_Sword_Mithril")))
        res.append(run(Bea, 10, 0, "5|k:" + eid("Potion_Health")))
        res.append(run(Bea, 10, 0, "6|empty"))
        K.check(all(x.startswith("+") for x in res), "X6 picks: 4 armor pieces, a sword in hotbar 1, a potion kind in hotbar 2, Empty (%s)" % res)
        bad = [run(Bea, 10, 0, "0|e:" + eid("Armor_Iron_Chest")), run(Bea, 10, 0, "7|e:" + eid("Weapon_Sword_Mithril")),
               run(Bea, 10, 0, "8|e:" + eid("Armor_Iron_Head")), run(Bea, 10, 0, "1|k:" + eid("Potion_Health")),
               run(Bea, 10, 0, "2|pocket"), run(Bea, 10, 0, "9|pocket"), run(Bea, 10, 0, "4|e:ffffffffffffffff"), run(Bea, 10, 0, "13|keep")]
        K.check(bad[0].startswith("-That piece does not go on Head") and bad[1].startswith("-It is already picked for Hotbar 1")
                and bad[2].startswith("-Armor goes in the armor slots") and bad[3].startswith("-Potions and food go in hotbar")
                and bad[4].startswith("-Pocket blocks are for hotbar slots only") and bad[5].startswith("-Hold the block you want in hotbar slot 6")
                and bad[6].startswith("-That item is not in Requip") and bad[7].startswith("-Pick a slot"), "X6 every refused pick (%s)" % bad)
        setc(Bea.hot, 5, stack("Wood_Oak_Log", 3))
        r = run(Bea, 10, 0, "9|pocket")
        Bea.hot.removeItemStackFromSlot(JShort(5), False)
        K.check(r.startswith("+Loadout 1: Hotbar 6 fills with Wood_Oak_Log from your Magic Bags"), "X6 Pocket pick takes the block held in that slot (%s)" % r)
        r = run(Bea, 4, 0, "Combat")
        dB = Store.get(kB, Bea.u)
        L0 = dB.slots[0]
        K.check([str(L0.picks[k_]) if L0.picks[k_] is not None else None for k_ in (6, 9, 10)] == ["x", "p:Wood_Oak_Log:0", None] and str(L0.name) == "Combat"
                and W.snap(Bea) == snapB, "X6 the loadout file holds the picks (Empty, pocket, Keep), the name; no item moved")
        ld = json.load(open(os.path.join(Wd, "requip", kB, "loadouts.json")))
        K.check(ld["loadouts"][0]["picks"][9] == "p:Wood_Oak_Log:0" and ld["loadouts"][0]["picks"][12] == "", "X6 loadouts.json (Keep = \"\")")

        # ============================================================ X7 EQUIP
        state.setdefault("bags", {})[str(Bea.u)] = {"Wood_Oak_Log": 500, "Rock_Stone": 10}
        state["calls"]["take"][:] = []
        baseB, _ = census(Bea)
        gap()
        r = run(Bea, 1, 0)
        dB = Store.get(kB, Bea.u)
        K.check(r.startswith("+Equipped Combat (11 moves, 1 pocket slots filled)"), "X7 Equip Combat: 5 deposits + 6 withdrawals + the pocket slot (%s)" % r)
        arm = [str(getc(Bea.arm, i).getItemId()) if getc(Bea.arm, i) else None for i in range(4)]
        K.check(arm == ["Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs"] and all(Codec.stampOf(getc(Bea.arm, i)) is not None for i in range(4)),
                "X7 the picked armor is on, each stamped with its eid (%s)" % arm)
        K.check(str(getc(Bea.hot, 0).getItemId()) == "Weapon_Sword_Mithril" and str(Codec.stampOf(getc(Bea.hot, 0))) == eid("Weapon_Sword_Mithril")
                and str(getc(Bea.hot, 1).getItemId()) == "Potion_Health" and int(getc(Bea.hot, 1).getQuantity()) == 10 and Codec.stampOf(getc(Bea.hot, 1)) is None,
                "X7 the sword (stamped) in hotbar 1, the potions (10 = all of the kind, never stamped) in hotbar 2")
        K.check(getc(Bea.hot, 5) is not None and str(getc(Bea.hot, 5).getItemId()) == "Wood_Oak_Log" and int(getc(Bea.hot, 5).getQuantity()) == 100
                and state["bags"][str(Bea.u)]["Wood_Oak_Log"] == 400 and ("Wood_Oak_Log", 100) in state["calls"]["commit"],
                "X7 the pocket slot took a full stack (100) from the Magic Bags (sacks:fn:take), committed")
        pm = br.get("requip:pocket:" + kB)
        K.check(pm is not None and dict((int(k_), str(v)) for k_, v in pm.items()) == {5: "Wood_Oak_Log"}, "X7 requip:pocket:<uuid> = {hotbar 6: Wood_Oak_Log}")
        K.check(getc(Bea.hot, 8) is not None and str(getc(Bea.hot, 8).getItemId()) == "Skyy_Menu" and dB.lastWorn == 0, "X7 the menu item stays (Keep), loadout 1 is LAST WORN")
        cp_ = ent_by_id(dB, "Armor_Copper_Head") + ent_by_id(dB, "Tool_Pickaxe_Iron") + ent_by_id(dB, "Food_Bread")
        K.check(len(cp_) == 3 and all(ein(e) for e in cp_), "X7 what was worn in the picked slots went INTO the pool (copper, pickaxe, bread kind)")
        cB, dB = census(Bea)
        exp = dict(baseB)
        exp[("Wood_Oak_Log", "")] = exp.get(("Wood_Oak_Log", ""), 0) + 100
        K.check(cB == exp and not once(Bea, dB), "X7 conservation (+100 logs from the bags) + exactly once")
        # loadout 2 picks the SAME sword (shared) in another slot + the pickaxe + the copper head; Equip moves the sword hotbar 1 -> 3
        res = [run(Bea, 10, 1, "6|e:" + eid("Weapon_Sword_Mithril")), run(Bea, 10, 1, "4|e:" + eid("Tool_Pickaxe_Iron")),
               run(Bea, 10, 1, "0|e:" + eid("Armor_Copper_Head")), run(Bea, 10, 1, "9|empty")]
        K.check(all(x.startswith("+") for x in res) and Store.get(kB, Bea.u).picked(eid("Weapon_Sword_Mithril")) == 2, "X7 the same sword picked in 2 loadouts (%s)" % res)
        swordEid = eid("Weapon_Sword_Mithril")
        baseB, _ = census(Bea)
        gap()
        state["bagRoom"] = 60
        r = run(Bea, 1, 1)
        state.pop("bagRoom")
        dB = Store.get(kB, Bea.u)
        K.check(r.startswith("=Equipped Loadout 2") and "40 pocket blocks did not fit your bags - they are in your storage" in r and str(getc(Bea.hot, 2).getItemId()) == "Weapon_Sword_Mithril" and str(Codec.stampOf(getc(Bea.hot, 2))) == swordEid
                and str(getc(Bea.hot, 0).getItemId()) == "Tool_Pickaxe_Iron" and str(getc(Bea.arm, 0).getItemId()) == "Armor_Copper_Head"
                and str(getc(Bea.arm, 1).getItemId()) == "Armor_Iron_Chest", "X7 Equip 2: the shared sword moved hotbar 1 -> 3 (same eid), pickaxe on, copper head on, Keep slots keep the iron (%s)" % r)
        K.check(not ein(dB.entry(swordEid)) and ein(ent_by_id(dB, "Armor_Iron_Head")[0]), "X7 ... the sword is OUT (never IN at the end), the iron head went in")
        K.check(br.get("requip:pocket:" + kB) is None and state["bags"][str(Bea.u)]["Wood_Oak_Log"] == 460 and getc(Bea.hot, 5) is None
                and any(getc(Bea.sto, i) is not None and str(getc(Bea.sto, i).getItemId()) == "Wood_Oak_Log" and int(getc(Bea.sto, i).getQuantity()) == 40 for i in range(36)),
                "X7 leaving the pocket slot: its blocks went to storage, 60 back into the bags (sacks:fn:deposit, bag full), 40 stay in storage; requip:pocket removed")
        K.check(("Wood_Oak_Log", 60, 5) in state["calls"]["deposit"] and not state["calls"].get("deposit3"),
                "FIX-E1 the give-back calls sacks:fn:deposit with the HOTBAR SLOT (4th argument, SkyySacks 0.7.17 contract) BEFORE the Equip lifts the stack; Sacks took 60 from slot 6 itself (%s)" % state["calls"]["deposit"])
        cB, dB = census(Bea)
        exp = dict(baseB)
        exp[("Wood_Oak_Log", "")] = exp.get(("Wood_Oak_Log", ""), 0) - 60
        K.check(cB == exp and not once(Bea, dB), "X7 conservation (-60 logs to the bags) + exactly once")
        # NOT WITH YOU: the sword leaves the inventory (dropped), Equip 1 keeps that slot with a note; removed picks too
        sw = getc(Bea.hot, 2)
        Bea.hot.removeItemStackFromSlot(JShort(2), False)
        gap()
        r = run(Bea, 1, 0)
        K.check(r.startswith("=Equipped Combat") and "Hotbar 1: Weapon_Sword_Mithril is not with you" in r and getc(Bea.hot, 0) is not None
                and str(getc(Bea.hot, 0).getItemId()) == "Tool_Pickaxe_Iron", "X7 a picked item that is not with you: that slot is kept, a note (%s)" % r)
        setc(Bea.hot, 2, sw)
        cB, dB = census(Bea)
        K.check(not once(Bea, dB), "X7 exactly once (the sword is back)")
        # a slot holding something refused (a block) with an Empty pick: it moves to storage; no room anywhere: kept + note
        setc(Bea.hot, 5, stack("Rock_Stone", 5))
        gap()
        r = run(Bea, 1, 1)
        K.check(getc(Bea.hot, 5) is None and any(getc(Bea.sto, i) is not None and str(getc(Bea.sto, i).getItemId()) == "Rock_Stone" and int(getc(Bea.sto, i).getQuantity()) == 5 for i in range(36)),
                "X7 Empty on a slot holding a block: the block moves to storage (spill) (%s)" % r)
        filler = []
        for c in (Bea.sto, Bea.bak):
            for i in range(int(c.getCapacity())):
                if getc(c, i) is None:
                    setc(c, i, stack("Ingredient_Bar_Iron", 1))
                    filler.append((c, i))
        setc(Bea.hot, 6, stack("Rock_Stone", 7))
        r = run(Bea, 10, 0, "10|empty")
        gap()
        r = run(Bea, 1, 0)
        K.check("Hotbar 7: no room in your inventory for Rock_Stone - kept" in r and getc(Bea.hot, 6) is not None, "X7 no room for a spill: the slot is kept + note (%s)" % r)
        for c, i in filler:
            c.removeItemStackFromSlot(JShort(i), False)
        Bea.hot.removeItemStackFromSlot(JShort(6), False)
        cB, dB = census(Bea)
        K.check(not once(Bea, dB), "X7 exactly once after the spill tests")
        # a picked item that was taken out: the pick shows removed, Equip keeps the slot
        gap()
        run(Bea, 1, 1)
        hb = ent_by_id(Store.get(kB, Bea.u), "Armor_Iron_Head")[0]
        r0 = run(Bea, 8, 0, str(hb.eid)) if ein(hb) else "-not in the pool"
        gap()
        r = run(Bea, 1, 0)
        K.check(r0.startswith("+Taken out") and "Head: the picked item was taken out of Requip" in r, "X7 a picked item that was taken out: noted, the slot kept (%s / %s)" % (r0, r))
        cB, dB = census(Bea)
        K.check(not once(Bea, dB), "X7 exactly once")
        # locked loadout
        gap()
        r = run(Bea, 1, 6)
        K.check(r.startswith("-Loadout 7 is unlocks at Overall Level 20") or "unlocks at Overall Level" in r, "X7 a locked loadout cannot be equipped (%s)" % r)

        # ============================================================ X8 fetch / Forget / pets + abilities
        dB = Store.get(kB, Bea.u)
        bow = ent_by_id(dB, "Weapon_Bow_Wood")[0]
        r = run(Bea, 14, 0, str(bow.eid))
        dB = Store.get(kB, Bea.u)
        K.check(r == "+ok" and not ein(dB.entry(str(bow.eid))) and str(bow.eid) in stamps_of(Bea), "X8 fetch: into the inventory, stamp kept, the entry is OUT (%s)" % r)
        r = run(Bea, 9, 0, str(bow.eid))
        K.check(r.startswith("-It is with you"), "X8 Forget refuses an item that is with you (%s)" % r)
        for c in Bea.secs:
            for i in range(int(c.getCapacity())):
                if Codec.stampOf(getc(c, i)) == bow.eid:
                    c.removeItemStackFromSlot(JShort(i), False)
        r = run(Bea, 10, 0, "11|e:" + str(bow.eid))
        r2 = run(Bea, 9, 0, str(bow.eid))
        dB = Store.get(kB, Bea.u)
        K.check(r.startswith("+") and r2.startswith("+Forgotten: Weapon_Bow_Wood") and dB.entry(str(bow.eid)) is None and dB.slots[0].picks[11] is None,
                "X8 Forget an OUT entry that is not with you: gone, and every pick of it cleared (%s)" % r2)
        r = run(Bea, 9, 0, eid("Weapon_Sword_Iron"))
        K.check(r.startswith("-It is in Requip"), "X8 Forget refuses an IN entry")
        state["pets"], state["abil"] = "pX|sY", "v=1;class=Mage;p1=Meteor;n1=Meteor"
        r = run(Bea, 2, 2)
        dB = Store.get(kB, Bea.u)
        K.check(r.startswith("+Saved into Loadout 3: your pets and your abilities") and dB.slots[2].hasPets and str(dB.slots[2].pet) == "pX", "X8 Save pets/abilities (%s)" % r)
        state["calls"]["pets"][:] = []
        gap()
        r = run(Bea, 1, 2)
        K.check(r.startswith("+Equipped Loadout 3 (0 moves)") and state["calls"]["pets"] == [(kB, "pX", "sY")], "X8 Equip a loadout without item picks: nothing moves, pets applied (%s)" % r)

        # ============================================================ X9 Use what I wear (registered IN PLACE) + the round trip
        Cy = W.player("00000000-0000-0000-0000-00000000000c", "Cyd")
        kC = str(Cy.u)
        for i, a in enumerate(["Armor_Gold_Head", "Armor_Iron_Chest", None, "Armor_Iron_Legs"]):
            if a:
                setc(Cy.arm, i, stack(a, 1, gdoc("rare", 30 + i)))
        setc(Cy.hot, 0, stack("Weapon_Sword_Iron", 1, gdoc("epic", 33)))
        setc(Cy.hot, 1, stack("Potion_Health", 4))
        setc(Cy.hot, 2, stack("Rock_Stone", 20))
        setc(Cy.hot, 3, stack("Ingredient_Bar_Iron", 3, '{"x": 1}'))
        setc(Cy.hot, 8, stack("Skyy_Menu", 1))
        baseC, _ = census(Cy)
        snapC = [[str(s.getItemId()) if s is not None and not s.isEmpty() else None for s in sec] for sec in W.snap(Cy)]
        r = run(Cy, 12, 0)
        dC = Store.get(kC, Cy.u)
        L = dC.slots[0]
        picks = [str(x) if x is not None else None for x in L.picks]
        K.check("Loadout 1 now uses what you wear (4 gear, 1 potion / food stacks)" in r and "Hotbar 4: Blocks and materials" in r and [p_[:2] if p_ else None for p_ in picks] == ["e:", "e:", None, "e:", "e:", "k:", "p:", None, None, None, None, None, None],
                "X9 Use what I wear: 4 gear picks, the potion kind, the block as a pocket pick, the metadata material + empty slots Keep (%s / %s)" % (r, picks))
        snapC2 = [[str(s.getItemId()) if s is not None and not s.isEmpty() else None for s in sec] for sec in W.snap(Cy)]
        K.check(snapC2 == snapC and len(stamps_of(Cy)) == 4 and all(not ein(e) for e in dC.entries.values() if not e.kind), "X9 nothing moved; the 4 gear pieces are stamped IN PLACE, their entries are OUT")
        cC, dC = census(Cy)
        K.check(cC == baseC and not once(Cy, dC), "X9 conservation + exactly once")
        r = run(Cy, 12, 0)
        dC = Store.get(kC, Cy.u)
        K.check("Loadout 1 now uses what you wear" in r and len([e for e in dC.entries.values() if not e.kind]) == 4, "X9 again: the same entries are re-used (no new eids)")
        gap()
        r = run(Cy, 1, 1)
        K.check(r.startswith("+Equipped Loadout 2 (0 moves)"), "X9 an empty loadout keeps everything (Keep) (%s)" % r)
        for k_ in range(13):
            run(Cy, 10, 1, "%d|empty" % k_)
        gap()
        r = run(Cy, 1, 1)
        dC = Store.get(kC, Cy.u)
        K.check(r.startswith("=Equipped Loadout 2") and all(getc(Cy.arm, i) is None for i in range(4)) and getc(Cy.hot, 0) is None and getc(Cy.hot, 8) is not None
                and all(ein(e) for e in dC.entries.values()), "X9 an all-Empty loadout puts everything away (blocks to storage, the menu item stays) (%s)" % r)
        cC, dC = census(Cy)
        K.check(cC == baseC and not once(Cy, dC), "X9 conservation")
        gap()
        r = run(Cy, 1, 0)
        cC, dC = census(Cy)
        K.check("Equipped Loadout 1" in r and "no Rock_Stone in your Magic Bags for hotbar 3" in r and str(getc(Cy.arm, 0).getItemId()) == "Armor_Gold_Head" and str(getc(Cy.hot, 0).getItemId()) == "Weapon_Sword_Iron"
                and int(getc(Cy.hot, 1).getQuantity()) == 4 and cC == baseC and not once(Cy, dC), "X9 Equip it back: the same gear returns (%s)" % r)

        # ============================================================ X10 the gate (REAL DeathComponent / DamageDataComponent / TimeResource reads)
        DDC = JClass("com.hypixel.hytale.server.core.entity.damage.DamageDataComponent")
        Death = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
        TR = JClass("com.hypixel.hytale.server.core.modules.time.TimeResource")
        Inst = JClass("java.time.Instant")
        G = W.player("00000000-0000-0000-0000-000000000010", "Gil")
        kG = str(G.u)
        setc(G.sto, 0, stack("Weapon_Sword_Iron", 1))
        setc(G.sto, 1, stack("Weapon_Bow_Wood", 1))
        comps = G.st.comps.get(G.ref)
        gap()
        Gate.BUSY.put(G.u, True)
        r = run(G, 1, 0)
        Gate.BUSY.remove(G.u)
        K.check(r.startswith("-One Requip change at a time"), "X10 a second click while a change runs: refused (%s)" % r)
        dc = U.allocateInstance(DDC.class_)
        tl = Inst.now()
        E.jf(TR, "now").set(G.st.res, tl)
        for g_ in ("getLastDamageTime", "getLastCombatAction"):
            E.jf(DDC, E.field_of("com.hypixel.hytale.server.core.entity.damage.DamageDataComponent", g_)[1]).set(dc, tl.minusSeconds(3))
        comps.put(types["ddc"], dc)
        r = run(G, 1, 0)
        r2 = run(G, 6, 0, "2:0")
        K.check(r.startswith("-You are in combat - wait 7 s") and r2.startswith("+Into Requip"), "X10 in combat: Equip refused, a deposit still works (%s / %s)" % (r, r2))
        comps.put(types["death"], U.allocateInstance(Death.class_))
        r = run(G, 1, 0)
        r2 = run(G, 6, 0, "2:1")
        K.check(r.startswith("-You cannot use Requip while dead") and r2.startswith("-You cannot use Requip while dead"), "X10 dead: everything refused (%s)" % r2)
        comps.remove(types["death"])
        comps.remove(types["ddc"])
        br.put("profile:busy:" + kG, True)
        r = run(G, 6, 0, "2:1")
        br.remove("profile:busy:" + kG)
        r2 = run(G, 6, 0, "2:1")
        K.check(r.startswith("-Your profile is still loading") and r2.startswith("-Requip opens again 30 s after a profile switch"), "X10 profile:busy, then the 30 s settle (%s / %s)" % (r, r2))
        Gate.BUSYAT.clear()
        Gate.EPOCH.put(G.u, JLong(5))
        br.put("profile:epoch:" + kG, JLong(6))
        r = run(G, 6, 0, "2:1")
        K.check(r.startswith("-Requip opens again"), "X10 a profile epoch change opens the settle window (%s)" % r)
        Gate.EPOCHAT.clear()
        Cfg.ON = False
        r = run(G, 6, 0, "2:1")
        r2 = run(G, 8, 0, str(ent_by_id(Store.get(kG, G.u), "Weapon_Sword_Iron")[0].eid))
        Cfg.ON = True
        K.check(r.startswith("-Requip is switched off") and r2.startswith("+Taken out"), "X10 switched off: deposits refused, Take out still works (%s / %s)" % (r, r2))

        # ============================================================ X11 save failure / put failure / rollback failure -> LOCKED -> admin repair
        Fk = W.player("00000000-0000-0000-0000-000000000011", "Fay", flaky=True)
        kF = str(Fk.u)
        for i, a in enumerate(["Armor_Iron_Head", "Armor_Iron_Chest"]):
            setc(Fk.sto, i, stack(a, 1, gdoc("rare", 3)))
        setc(Fk.arm, 0, stack("Armor_Copper_Head", 1))
        setc(Fk.arm, 1, stack("Armor_Copper_Chest", 1))
        run(Fk, 7)
        dF = Store.get(kF, Fk.u)
        run(Fk, 10, 0, "0|e:" + str(ent_by_id(dF, "Armor_Iron_Head")[0].eid))
        run(Fk, 10, 0, "1|e:" + str(ent_by_id(dF, "Armor_Iron_Chest")[0].eid))
        baseF, _ = census(Fk)
        snapF = W.snap(Fk)
        Store.FAIL_NEXT = 1
        gap()
        r = run(Fk, 1, 0)
        cF, dF = census(Fk)
        jF0 = json.load(open(os.path.join(Wd, "requip", kF, "journal.json"))) if os.path.isfile(os.path.join(Wd, "requip", kF, "journal.json")) else {"steps": [], "stage": "saved"}
        K.check(r.startswith("-Could not save Requip - everything was put back") and cF == baseF and not once(Fk, dF) and W.snap(Fk) == snapF
                and jF0["stage"] == "saved" and not [st for st in jF0["steps"] if st["op"] == "equip"], "X11 a save failure: every move rolled back, the journal back to its earlier steps (%s)" % r)
        Flaky = JClass(FAKE_PKG + ".FlakyBox")
        Flaky.FAIL_AT = 1
        gap()
        r = run(Fk, 1, 0)
        Flaky.FAIL_AT = -1
        cF, dF = census(Fk)
        K.check(r.startswith("-Equip stopped (could not put") and "everything was put back" in r and cF == baseF and not once(Fk, dF), "X11 a put failure mid-Equip: rolled back (%s)" % r)
        Flaky.FAIL_AT, Flaky.STICKY = 1, True
        gap()
        r = run(Fk, 1, 0)
        Flaky.FAIL_AT, Flaky.STICKY, Flaky.FAIL_ALL = -1, False, False
        dF = Store.get(kF, Fk.u)
        jF = json.load(open(os.path.join(Wd, "requip", kF, "journal.json")))
        K.check(r.startswith("-The change failed and could not be undone - Requip is locked") and dF.bad and jF["stage"] == "failed", "X11 a failed rollback: LOCKED, journal 'failed' (%s)" % r)
        r = run(Fk, 6, 0, "2:5")
        r2 = run(Fk, 5)
        K.check(r.startswith("-") and "locked" in r and r2 == "=Nothing to repair.", "X11 locked: every change refused, a normal repair leaves a failed journal alone (%s / %s)" % (r, r2))
        restart()
        Fk.pr.msgs = None
        P("WdRepairTask")(Fk.u, 0, True, None).run()
        cF, dF = census(Fk)
        K.check(not dF.bad and cF == baseF and not once(Fk, dF) and not os.path.isfile(os.path.join(Wd, "requip", kF, "journal.json")),
                "X11 /requipadmin repair (force): reconciled from the live inventory, unlocked, every item once (%s)" % (Fk.pr.msgs,))

        # ============================================================ X12 CRASH AT EVERY STEP of every transaction, live as-is AND rolled back
        cases = [0]
        crash_fail = []
        uid_n = [100]

        def fresh(name):
            uid_n[0] += 1
            return W.player("00000000-0000-0000-0000-%012d" % uid_n[0], name)

        def setup_equip(p):
            for i, a in enumerate(["Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs"]):
                setc(p.sto, i, stack(a, 1, gdoc("rare", 10 + i)))
            setc(p.sto, 4, stack("Weapon_Sword_Mithril", 1, gdoc("mythic", 40)))
            setc(p.sto, 5, stack("Potion_Health", 10))
            setc(p.sto, 6, stack("Weapon_Sword_Iron", 1, gdoc("rare", 2)))
            run(p, 7)
            setc(p.arm, 0, stack("Armor_Copper_Head", 1, gdoc("unique", 1)))
            setc(p.arm, 1, stack("Armor_Copper_Chest", 1))
            setc(p.hot, 0, stack("Tool_Pickaxe_Iron", 1, gdoc("normal", 2)))
            setc(p.hot, 1, stack("Food_Bread", 3))
            setc(p.hot, 2, stack("Rock_Stone", 10))
            setc(p.hot, 8, stack("Skyy_Menu", 1))
            d = Store.get(str(p.u), p.u)
            e_ = lambda iid: str(ent_by_id(d, iid)[0].eid)
            for k_, a in enumerate(["Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs"]):
                run(p, 10, 0, "%d|e:%s" % (k_, e_(a)))
            run(p, 10, 0, "4|e:" + e_("Weapon_Sword_Mithril"))
            run(p, 10, 0, "5|k:" + e_("Potion_Health"))
            run(p, 10, 0, "6|empty")
            run(p, 10, 0, "7|e:" + e_("Weapon_Sword_Iron"))
            # loadout 2: the mithril sword (out on you after loadout 1) in hotbar 3 = a pool round trip; the pickaxe back on
            run(p, 10, 1, "6|e:" + e_("Weapon_Sword_Mithril"))
            run(p, 10, 1, "0|empty")

        def op_equip1(p):
            gap()
            return run(p, 1, 0)

        def setup_equip2(p):
            setup_equip(p)
            gap()
            run(p, 1, 0)
            d = Store.get(str(p.u), p.u)
            run(p, 10, 1, "4|e:" + str(ent_by_id(d, "Tool_Pickaxe_Iron")[0].eid))

        def op_equip2(p):
            gap()
            return run(p, 1, 1)

        def setup_dep(p):
            setc(p.sto, 0, stack("Armor_Iron_Head", 1, gdoc("rare", 1)))
            setc(p.sto, 1, stack("Potion_Health", 6))
            setc(p.sto, 2, stack("Weapon_Sword_Iron", 1))
            setc(p.sto, 3, stack("Weapon_Sword_Iron", 1))
            setc(p.bak, 0, stack("Potion_Health", 4))
            setc(p.bak, 1, stack("Rock_Stone", 3))

        def op_depall(p):
            return run(p, 7)

        def setup_take(p):
            setup_dep(p)
            run(p, 7)

        def op_take(p):
            d = Store.get(str(p.u), p.u)
            return run(p, 8, 0, str(ent_by_id(d, "Weapon_Sword_Iron")[0].eid))

        def op_takekind(p):
            d = Store.get(str(p.u), p.u)
            return run(p, 8, 0, str(ent_by_id(d, "Potion_Health")[0].eid))

        def op_fetch(p):
            d = Store.get(str(p.u), p.u)
            return run(p, 14, 0, str(ent_by_id(d, "Armor_Iron_Head")[0].eid))

        def setup_ret(p):
            d = Store.get(str(p.u), p.u)
            d.orphan("test", stack("Weapon_Bow_Wood", 1, gdoc("rare", 9)))
            d.rev = d.rev + 1
            Store.save(d)

        def op_ret(p):
            return run(p, 13)

        def op_craft(p):
            return str(Ops.craft(p.pr, p.ref, p.st, stack("Weapon_Sword_Mithril", 1, gdoc("rare", 22)), "test", ""))

        def count_points(setup, op):
            """how many moves (the op's journal step) and file writes the op makes, on a fresh player"""
            p = fresh("count")
            setup(p)
            f0 = int(Store.FILES)
            op(p)
            f1 = int(Store.FILES)
            jf_ = os.path.join(Wd, "requip", str(Store.pkey(p.u)), "journal.json")
            n_ = len(json.load(open(jf_))["steps"][-1]["moves"]) if os.path.isfile(jf_) else 0
            return n_, f1 - f0

        def crash_case(label, setup, op, how, n, roll, craft=False):
            cases[0] += 1
            p = fresh(label)
            setup(p)
            base, _ = census(p)
            if craft:
                base[(u"Weapon_Sword_Mithril", str(JClass("org.bson.BsonDocument").parse(gdoc("rare", 22)).toJson()))] = 1
            before = W.snap(p)
            if how == "at":
                Tx.CRASH_AT = n
            elif how == "save":
                Tx.CRASH_AFTER_SAVE = True
            else:
                Store.CRASH_FILES = n
            died = False
            res = ""
            try:
                res = op(p)
            except Exception as ex_:
                died = "harness crash" in str(ex_)
            Tx.CRASH_AT, Tx.CRASH_AFTER_SAVE, Store.CRASH_FILES = -1, False, -1
            if not died:
                return "nodie"
            if roll:
                W.restore(p, before)
            restart()
            r = run(p, 5)
            c, d = census(p)
            if craft and roll is False and c != base:
                pass
            bad = once(p, d)
            ok = c == base and not bad and jresolved(str(p.u)) and not d.bad
            if not ok:
                crash_fail.append("%s %s=%d roll=%s: repair %s; census diff %s; once %s" % (label, how, n, roll, r,
                                  {k_: (base.get(k_), c.get(k_)) for k_ in set(base) | set(c) if base.get(k_) != c.get(k_)}, bad))
            return "ok" if ok else "bad"

        for label, setup, op, craft in (("eq1", setup_equip, op_equip1, False), ("eq2", setup_equip2, op_equip2, False), ("depall", setup_dep, op_depall, False),
                                        ("take", setup_take, op_take, False), ("takekind", setup_take, op_takekind, False), ("fetch", setup_take, op_fetch, False),
                                        ("ret", setup_ret, op_ret, False), ("craft", lambda p: None, op_craft, True)):
            nm, nf = count_points(setup, op)
            for roll in (False, True):
                res_ = [crash_case(label, setup, op, "at", n, roll, craft) for n in range(nm + 1)]
                res_.append(crash_case(label, setup, op, "save", 0, roll, craft))
                res_ += [crash_case(label, setup, op, "files", f, roll, craft) for f in range(nf)]
                if "nodie" in res_:
                    crash_fail.append("%s roll=%s: a crash point did not fire (%s)" % (label, roll, res_))
            K.notes.append("X12 %s: %d move points + after the save + %d file points, x2 (live as-is / rolled back)" % (label, nm, nf))
        K.check(not crash_fail, "X12 a crash after every move, mid-save after every file and after the save, live as-is and rolled back (%d cases): every item exactly once, the journal resolved: %s" % (cases[0], crash_fail[:4]))

        # chained changes inside one journal window (deposit, equip, take out), then a crash with the live inventory rolled back to before the first
        Ch = fresh("chain")
        setup_equip(Ch)
        base, _ = census(Ch)
        snapCh = W.snap(Ch)
        gap()
        run(Ch, 1, 0)
        setc(Ch.sto, 20, stack("Weapon_Bow_Wood", 1))
        run(Ch, 6, 0, "2:20")
        run(Ch, 8, 0, str(ent_by_id(Store.get(str(Ch.u), Ch.u), "Weapon_Bow_Wood")[0].eid))
        jC = json.load(open(os.path.join(Wd, "requip", str(Ch.u), "journal.json")))
        n_steps = len(jC["steps"])
        Tx.CRASH_AFTER_SAVE = True
        try:
            gap()
            run(Ch, 1, 1)
        except Exception:
            pass
        Tx.CRASH_AFTER_SAVE = False
        W.restore(Ch, snapCh)
        restart()
        r = run(Ch, 5)
        c, d = census(Ch)
        exp = dict(base)
        exp[("Weapon_Bow_Wood", "")] = 1
        K.check(n_steps >= 4 and c == exp and not once(Ch, d), "X12 CHAINED: %d steps in one journal + a crashed Equip, the live inventory rolled back before them all: every item once (%s; diff %s; once %s)"
                % (n_steps, r, {k_: (exp.get(k_), c.get(k_)) for k_ in set(exp) | set(c) if exp.get(k_) != c.get(k_)}, once(Ch, d)))
        # profile switch: a journal of profile 1 is never repaired against profile 2's inventory
        Pp = fresh("prof")
        state.setdefault("key", {})[str(Pp.u)] = str(Pp.u) + "-p1"
        setc(Pp.sto, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 4)))
        setc(Pp.sto, 1, stack("Armor_Iron_Head", 1))
        run(Pp, 7)
        inv1 = W.snap(Pp)
        base1, _ = census(Pp, str(Pp.u) + "-p1")
        W.clear(Pp)
        setc(Pp.sto, 0, stack("Weapon_Bow_Wood", 1))
        state["key"][str(Pp.u)] = str(Pp.u) + "-p2"
        restart()
        r2 = run(Pp, 5)
        K.check(r2 == "=Nothing to repair." and os.path.isfile(os.path.join(Wd, "requip", str(Pp.u) + "-p1", "journal.json")), "X12 profile 2 active: profile 1's journal is left alone (%s)" % r2)
        W.clear(Pp)
        W.restore(Pp, inv1)
        state["key"][str(Pp.u)] = str(Pp.u) + "-p1"
        r1 = run(Pp, 5)
        c1, d1 = census(Pp, str(Pp.u) + "-p1")
        K.check(r1.startswith("=An interrupted Requip change") and c1 == base1 and not once(Pp, d1), "X12 back on profile 1: its journal is reconciled with ITS inventory (%s)" % r1)
        del state["key"][str(Pp.u)]

        # ============================================================ X13 random-operation FUZZ (invariant after every op and every crash)
        # requip021: the --seed run + seed 4242 (the phantom NOT WITH YOU after take out -> deposit -> take out -> crash) + 20 more seeds
        fz_seeds = [(s_, False) for s_ in [SEED] + [s_ for s_ in FUZZ_SEEDS if s_ != SEED]] + [(s_, True) for s_ in COLLIDE_SEEDS]
        for fz_seed, collide in fz_seeds:
            rnd = random.Random(fz_seed)
            Z = fresh("fuzz")
            kZ = str(Z.u)
            pool_ids = ["Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs", "Armor_Copper_Head", "Armor_Copper_Chest", "Armor_Copper_Legs",
                        "Weapon_Sword_Iron", "Weapon_Sword_Mithril", "Weapon_Bow_Wood", "Tool_Pickaxe_Iron", "Tool_Hatchet_Iron"]
            # requip021fix: COLLIDING-KIND = many identical items (same id + same metadata) - lineages, merges and put-backs of twins
            # (its own list: pool_ids is used again by X15)
            fz_ids = ["Armor_Iron_Legs", "Armor_Iron_Head", "Weapon_Sword_Iron"] if collide else pool_ids
            for i in range(14):
                setc(Z.sto, i, stack(fz_ids[i % len(fz_ids)], 1, gdoc("rare", 7) if collide else gdoc(rnd.choice(["rare", "unique", "normal"]), rnd.randint(1, 50))))
            setc(Z.sto, 14, stack("Potion_Health", 12))
            setc(Z.sto, 15, stack("Food_Bread", 9))
            setc(Z.sto, 16, stack("Rock_Stone", 30))
            expect, _ = census(Z)
            engine = W.snap(Z)
            Cfg.SETTLE_S = 0
            state["bagRoom"] = 0
            log_ = []
            hist_ = []
            fz_fail = []
            crashes = 0
            engine_step = -1
            fallback = []
            for step in range(int(arg("--collide-ops", "400")) if collide else int(arg("--fuzz", "260"))):
                d = Store.get(kZ, Z.u)
                ops_ = ["dep", "depall", "take", "fetch", "pick", "pick", "pick", "equip", "equip", "wear", "craft", "save", "ret", "shuffle", "auto"]
                o = rnd.choice(ops_)
                # fixer 2 (data critic): failing saves (1-3 in a row: the put-back + kept-journal paths) on any op
                if rnd.random() < 0.1:
                    Store.FAIL_NEXT = rnd.randint(1, 3)
                crash = rnd.random() < 0.12
                if crash:
                    how = rnd.choice(["at", "at", "save", "files"])
                    if how == "at":
                        Tx.CRASH_AT = rnd.randint(0, 6)
                    elif how == "save":
                        Tx.CRASH_AFTER_SAVE = True
                    else:
                        Store.CRASH_FILES = rnd.randint(0, 3)
                died = False
                res = ""
                try:
                    if o == "dep":
                        slots = [(s_, i) for s_ in (1, 2, 3) for i in range(int(Z.secs[s_].getCapacity())) if getc(Z.secs[s_], i) is not None]
                        if slots:
                            s_, i = rnd.choice(slots)
                            res = run(Z, 6, 0, "%d:%d" % (s_, i))
                    elif o == "depall":
                        res = run(Z, 7)
                    elif o in ("take", "fetch"):
                        ins = [e for e in d.entries.values() if ein(e) and (not e.kind or o == "take") and (e.kind is False or e.count > 0)]
                        if ins:
                            res = run(Z, 8 if o == "take" else 14, 0, str(rnd.choice(ins).eid))
                    elif o == "pick":
                        n = rnd.randint(0, 3)
                        k_ = rnd.randint(0, 12)
                        cand = [e for e in d.entries.values() if (k_ < 4 and not e.kind and e.space == 0 and e.spot == k_) or (k_ >= 4 and e.space == 1)]
                        choice = rnd.random()
                        if choice < 0.15:
                            res = run(Z, 10, n, "%d|keep" % k_)
                        elif choice < 0.3:
                            res = run(Z, 10, n, "%d|empty" % k_)
                        elif cand:
                            e = rnd.choice(cand)
                            res = run(Z, 10, n, "%d|%s:%s" % (k_, "k" if e.kind else "e", e.eid))
                    elif o == "equip":
                        gap()
                        res = run(Z, 1, rnd.randint(0, 3))
                    elif o == "wear":
                        res = run(Z, 12, rnd.randint(0, 3))
                    elif o == "craft":
                        res = str(Ops.craft(Z.pr, Z.ref, Z.st, stack("Weapon_Bow_Wood", 1, gdoc("rare", 60 + step)), "fuzz", ""))
                        if res.startswith("eid:"):
                            expect[("Weapon_Bow_Wood", str(JClass("org.bson.BsonDocument").parse(gdoc("rare", 60 + step)).toJson()))] = 1
                    elif o == "save":
                        # time passes: the engine saves the player, the journal keep window ends
                        engine = W.snap(Z)
                        engine_step = step
                        old_k = Cfg.JKEEP_S
                        Cfg.JKEEP_S = 0
                        Jr.sweep(int(time.time() * 1000) + 1000)
                        Cfg.JKEEP_S = old_k
                    elif o == "ret":
                        res = run(Z, 13)
                    elif o == "shuffle":
                        # the player moves stacks around inside the inventory (no Requip involved)
                        sl_ = [(s_, i) for s_ in (1, 2, 3) for i in range(int(Z.secs[s_].getCapacity()))]
                        (s1, i1), (s2, i2) = rnd.sample(sl_, 2)
                        x1, x2 = getc(Z.secs[s1], i1), getc(Z.secs[s2], i2)
                        if x1 is not None:
                            Z.secs[s1].removeItemStackFromSlot(JShort(i1), False)
                        if x2 is not None:
                            Z.secs[s2].removeItemStackFromSlot(JShort(i2), False)
                        if x1 is not None:
                            setc(Z.secs[s2], i2, x1)
                        if x2 is not None:
                            setc(Z.secs[s1], i1, x2)
                        res = "shuffled"
                    elif o == "auto":
                        Auto.ON.put(kZ, True)
                        Auto.LASTRUN.clear()
                        try:
                            P("WdAutoTask")(Z.u).run()
                        finally:
                            Auto.ON.remove(kZ)
                        res = "auto"
                except Exception as ex_:
                    died = "harness crash" in str(ex_)
                    if not died:
                        fz_fail.append("step %d %s raised %s" % (step, o, ex_))
                Tx.CRASH_AT, Tx.CRASH_AFTER_SAVE, Store.CRASH_FILES = -1, False, -1
                Store.FAIL_NEXT = 0
                if o == "craft" and not died and str(res).startswith("refused:"):
                    # the caller (SkyyGear) keeps a refused crafted item: it falls back to the inventory
                    fr = [i for i in range(int(Z.sto.getCapacity())) if getc(Z.sto, i) is None]
                    if fr:
                        setc(Z.sto, fr[0], stack("Weapon_Bow_Wood", 1, gdoc("rare", 60 + step)))
                        expect[("Weapon_Bow_Wood", str(JClass("org.bson.BsonDocument").parse(gdoc("rare", 60 + step)).toJson()))] = 1
                        fallback.append((("Weapon_Bow_Wood", str(JClass("org.bson.BsonDocument").parse(gdoc("rare", 60 + step)).toJson())), step))
                if o == "craft" and died:
                    # a craft that died before its journal step could not have taken materials (none here): it may or may not have landed
                    pass
                rolled = False
                rolled_from = engine_step
                if died:
                    crashes += 1
                    if rnd.random() < 0.5:
                        W.restore(Z, engine)
                        rolled = True
                    restart()
                    jz = os.path.join(Wd, "requip", kZ, "journal.json")
                    if os.path.isfile(jz):
                        shutil.copy(jz, os.path.join(SCRATCH, "fz-%d-%d.json" % (fz_seed, step)))
                    live_dump = W.dump(Z, Codec)
                    res = "CRASH -> " + run(Z, 5)
                    engine = W.snap(Z)
                    engine_step = step
                c, dz = census(Z)
                bad = once(Z, dz)
                # a refused craft the caller gave to the inventory AFTER the engine last saved the player: a rollback undoes that give too (and,
                # in game, the materials it cost) - not Requip's item
                if rolled:
                    for kk_, st_ in fallback:
                        if st_ > rolled_from and c.get(kk_, 0) == 0 and expect.get(kk_) == 1:
                            del expect[kk_]
                # a craft that crashed: the repair keeps the crafted entry (no material evidence) or the craft never journaled
                if o == "craft" and died and c != expect:
                    kk = ("Weapon_Bow_Wood", str(JClass("org.bson.BsonDocument").parse(gdoc("rare", 60 + step)).toJson()))
                    if c.get(kk, 0) == 0 and expect.get(kk) == 1:
                        del expect[kk]
                    elif c.get(kk, 0) == 1 and expect.get(kk) is None:
                        expect[kk] = 1
                if (c != expect or bad) and died:
                    json.dump(live_dump, open(os.path.join(SCRATCH, "fz-%d-%d-live.json" % (fz_seed, step)), "w"))
                if c != expect or bad:
                    fz_fail.append("step %d %s%s: %s; before %s; diff %s; once %s" % (step, o, " (crash)" if died else "", res, hist_[-3:],
                                    {k_: (expect.get(k_), c.get(k_)) for k_ in set(expect) | set(c) if expect.get(k_) != c.get(k_)}, bad))
                    expect = c
                if not died and o != "save" and rnd.random() < 0.3:
                    engine = W.snap(Z)      # the engine saved the player in the MIDDLE of a journal window (a later crash rolls back to here)
                    engine_step = step
                log_.append("%s%s" % (o, "!" if died else ""))
                hist_.append("%d %s %s" % (step, o, str(res)[:70]))
            Cfg.SETTLE_S = 30
            state.pop("bagRoom", None)
            K.check(not fz_fail, "X13 FUZZ%s seed %d: %d random ops (%d crashes, half with the live inventory rolled back), every item exactly once after each: %s" % (" COLLIDING-KIND" if collide else "", fz_seed, len(log_), crashes, fz_fail[:3]))
            K.notes.append(("X13 fuzz%s seed %d ops: " % (" collide" if collide else "", fz_seed)) + " ".join(log_[:80]) + " ...")

        # ============================================================ X13b requip021: LINEAGES in the crash repair (fuzz seed 4242, made exact)
        # an item that was OUT (stamped) when the journal began is deposited, taken out (plain), deposited again (a NEW entry), taken out
        # again; then the server dies. Before the fix the repair counted that one plain item twice and kept the first entry as a phantom
        # NOT WITH YOU. B: the same, but the second entry is fetched (its stamp is in the inventory). C: a journal whose lineage link is
        # wrong (two items in the pool, one lineage): the IN count still follows conservation (the fill-up pass) - nothing is lost.
        def legs_slot(p):
            for s_ in (1, 2, 3):
                for i in range(int(p.secs[s_].getCapacity())):
                    x = getc(p.secs[s_], i)
                    if x is not None and str(x.getItemId()) == "Armor_Iron_Legs":
                        return "%d:%d" % (s_, i)
            return None

        def lin_start(name):
            p = fresh(name)
            setc(p.sto, 0, stack("Armor_Iron_Legs", 1, gdoc("unique", 18)))
            setc(p.sto, 1, stack("Weapon_Sword_Iron", 1, gdoc("rare", 3)))
            run(p, 6, 0, "2:0")
            d = Store.get(str(p.u), p.u)
            e0 = str(ent_by_id(d, "Armor_Iron_Legs")[0].eid)
            r = run(p, 14, 0, e0)                       # fetch: the legs are OUT, stamped, in the inventory
            old_k = Cfg.JKEEP_S
            Cfg.JKEEP_S = 0
            Jr.sweep(int(time.time() * 1000) + 1000)    # the keep window ends: the next change starts a NEW journal
            Cfg.JKEEP_S = old_k
            base, _d = census(p)
            return p, e0, base, r

        for case in ("A", "B"):
            p, e0, base, r0 = lin_start("lineage" + case)
            k_ = str(p.u)
            r1 = run(p, 6, 0, legs_slot(p))             # deposit the stamped legs (the entry that was OUT)
            r2 = run(p, 8, 0, e0)                       # Take out: a plain item again, the entry is gone
            r3 = run(p, 6, 0, legs_slot(p))             # deposit again: a NEW entry
            d = Store.get(k_, p.u)
            e1 = [str(e.eid) for e in ent_by_id(d, "Armor_Iron_Legs")]
            r4 = run(p, 8 if case == "A" else 14, 0, e1[0] if e1 else "")   # A: Take out again (plain) / B: fetch (stamped, OUT)
            jx = os.path.isfile(os.path.join(Wd, "requip", k_, "journal.json"))
            restart()                                   # the server dies inside the keep window
            rr = run(p, 5)
            c, d = census(p)
            bad = once(p, d)
            legs = ent_by_id(d, "Armor_Iron_Legs")
            want = [] if case == "A" else [(e1[0] if e1 else "?", False)]
            got = [(str(e.eid), ein(e)) for e in legs]
            K.check(jx and rr.startswith("=An interrupted Requip change") and c == base and not bad and got == want,
                    "X13b lineage %s: OUT legs deposited, taken out, deposited again, %s, crash -> no phantom NOT WITH YOU, every item once "
                    "(%s | %s | %s | %s | %s | entries %s want %s, once %s)" % (case, "taken out again" if case == "A" else "fetched", r1, r2, r3, r4, rr, got, want, bad))

        # C: a lineage link that is wrong (hand-made journal): two plain legs deposited as two new entries, a fake Take out of the first
        # between them links the second to it - both must stay IN (conservation), never one deleted
        p = fresh("lineageC")
        k_ = str(p.u)
        setc(p.sto, 0, stack("Armor_Iron_Legs", 1, gdoc("unique", 18)))
        setc(p.sto, 1, stack("Armor_Iron_Legs", 1, gdoc("unique", 18)))
        base, _d = census(p)
        rc1 = run(p, 6, 0, "2:0")
        rc2 = run(p, 6, 0, "2:1")
        jp = os.path.join(Wd, "requip", k_, "journal.json")
        okC = os.path.isfile(jp)
        if okC:
            jj = json.load(open(jp))
            okC = len(jj["steps"]) == 2 and len(jj["steps"][0]["moves"]) == 1
            if okC:
                fake = json.loads(json.dumps(jj["steps"][0]))
                fake["op"] = "take"
                m_ = fake["moves"][0]
                m_["t"] = {"$numberInt": "4"}
                m_["del"] = True
                m_["fresh"] = False
                jj["steps"].insert(1, fake)
                json.dump(jj, open(jp, "w"))
        restart()
        rc = run(p, 5)
        c, d = census(p)
        legs = ent_by_id(d, "Armor_Iron_Legs")
        K.check(okC and rc.startswith("=An interrupted Requip change") and c == base and not once(p, d) and len(legs) == 2 and all(ein(e) for e in legs),
                "X13b lineage C: a wrong lineage link never deletes an item the pool must hold - both legs stay IN (%s | %s | %s | %s)" % (rc1, rc2, rc, [(str(e.eid), ein(e)) for e in legs]))

        # ============================================================ X13c requip021fix: "Use what I wear" with a FAILED save (colliding fuzz seed 8030)
        # the worn gear is stamped in place; before the fix a failed save dropped the new entries but left the stamps on the items (a stamp
        # the pool did not know). Now every item is put back exactly as it was; a retry that saves stamps them as usual.
        p = fresh("wearfail")
        k_ = str(p.u)
        setc(p.arm, 3, stack("Armor_Iron_Legs", 1, gdoc("rare", 7)))
        setc(p.hot, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 7)))
        setc(p.hot, 1, stack("Weapon_Bow_Wood", 1, gdoc("rare", 9)))
        setc(p.sto, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 7)))
        before_w = [str(x.toString()) if x is not None else None for x in (getc(p.arm, 3), getc(p.hot, 0), getc(p.hot, 1))]
        base, _d = census(p)
        Store.FAIL_NEXT = 1
        rw = run(p, 12, 0)
        Store.FAIL_NEXT = 0
        c, d = census(p)
        after_w = [str(x.toString()) if x is not None else None for x in (getc(p.arm, 3), getc(p.hot, 0), getc(p.hot, 1))]
        K.check(rw.startswith("-Could not save") and not stamps_of(p) and not once(p, d) and c == base and after_w == before_w and not [e for e in d.entries.values() if not e.kind],
                "X13c Use what I wear, the save fails: every worn item put back unstamped, exactly as it was, no entry (%s | stamps %s | once %s)" % (rw, stamps_of(p), once(p, d)))
        rw2 = run(p, 12, 0)
        c, d = census(p)
        K.check(rw2.startswith("+") and len(stamps_of(p)) == 3 and not once(p, d) and c == base,
                "X13c ... a retry that saves stamps the worn gear as usual (%s | stamps %s | once %s)" % (rw2, stamps_of(p), once(p, d)))

        # ============================================================ X14 MIGRATION of 0.1 files (fixtures made by the REAL 0.1 jar in M01)
        fx = os.path.join(SCRATCH, "fx01")
        meta = json.load(open(os.path.join(fx, "meta.json"))) if os.path.isfile(os.path.join(fx, "meta.json")) else None
        K.check(meta is not None, "X14 the M01 fixtures exist (the 0.1 jar ran)")
        lo01 = os.path.join(Wd, "loadouts")
        os.makedirs(lo01, exist_ok=True)

        def census01(f01, live_dump):
            """the items a 0.1 file + a live inventory dump hold (the stamp-free kind keys of the 0.2 census)"""
            tot = {}
            d01 = json.load(open(f01))
            docs = []
            for L_ in d01["loadouts"]:
                docs += L_["armor"] + L_["hotbar"]
            docs += d01["orphans"]
            for sec in live_dump:
                docs += [x for x in sec if x is not None]
            for x in docs:
                s_ = Codec.stackOf(JClass("org.bson.BsonDocument").parse(json.dumps(x)))
                kk = ukey(s_)
                tot[kk] = tot.get(kk, 0) + int(s_.getQuantity())
            return tot
        if meta:
            # ---- A: stored loadout 1 (armor + sword + potion + a block + a bag + armor in a hotbar slot), loadout 2 EQUIPPED, an orphan
            kA1 = meta["A"]["key"]
            src = os.path.join(fx, "mods", "Skyy_SkyyWardrobe", "loadouts", kA1 + ".json")
            shutil.copy(src, os.path.join(lo01, kA1 + ".json"))
            raw01 = open(os.path.join(lo01, kA1 + ".json"), "rb").read()
            Mi = W.player(kA1, "Ann")
            W.load(Mi, meta["A"]["live"], Codec)
            exp01 = census01(os.path.join(lo01, kA1 + ".json"), meta["A"]["live"])
            restart()
            dM = Store.get(kA1, Mi.u)
            K.check(dM.mig == 1 and not dM.exists, "X14 a key with a 0.1 file and no Requip folder waits for its migration")
            r = run(Mi, 5)
            dM = Store.get(kA1, Mi.u)
            cM, dMf = census(Mi)
            K.check(dM.mig == 0 and dMf.migrated is not None and "0.1 rev" in str(dMf.migrated) and cM == exp01 and not once(Mi, dMf),
                    "X14 A migrated on the first load: every 0.1 stack is in the pool or a Returned item, nothing lost or doubled (%s; %s)" % (r, dMf.migrated))
            L1, L2 = dMf.slots[0], dMf.slots[1]
            pk1 = [str(x)[:2] if x is not None else None for x in L1.picks]
            K.check(str(L1.name) == "Combat" and pk1[:4] == ["e:"] * 4 and pk1[4] == "e:" and pk1[5] == "k:" and pk1[6] is None and pk1[7] is None and pk1[8] is None
                    and L1.hasPets and str(L1.pet) == "petA" and "Priest" in str(L1.abil), "X14 loadout 1: name, pets, abilities kept; picks point at the new entries; block / bag / misplaced armor = Keep (%s)" % pk1)
            K.check(L2.hasPets and str(L2.pet) == "petB" and L2.picked() == 0 and dMf.lastWorn == 1 and dMf.ask01 == 1,
                    "X14 the EQUIPPED loadout 2: pets kept, Keep everywhere (its gear stays on you), asked once (ask01)")
            rets = [str(Codec.stackOf(o.asDocument()).getItemId()) for o in dMf.orphans]
            K.check(sorted(rets) == ["Backpack_Test", "Rock_Stone"] and len(ent_by_id(dMf, "Armor_Gold_Head")) == 1 and len(ent_by_id(dMf, "Weapon_Bow_Wood")) == 1,
                    "X14 refused 0.1 stacks (the block, the bag) became Returned items; the misplaced helmet + the 0.1 orphan bow became pool entries (%s)" % rets)
            K.check(open(os.path.join(lo01, kA1 + ".json"), "rb").read() == raw01 and open(os.path.join(Wd, "requip", kA1, "from01", kA1 + ".json"), "rb").read() == raw01,
                    "X14 the 0.1 file is untouched; the History snapshot holds its exact bytes")
            restart()
            dM2 = Store.get(kA1, Mi.u)
            r2 = run(Mi, 5)
            cM2, dM3 = census(Mi)
            K.check(dM2.mig == 0 and r2 == "=Nothing to repair." and cM2 == exp01 and len(dM3.entries) == len(dMf.entries), "X14 RUN ONCE: a restart does not migrate again")
            # the 0.1 question: "Use what you wear for Loadout 2?" -> registered in place
            r = run(Mi, 12, 1)
            dM = Store.get(kA1, Mi.u)
            cM, dMf = census(Mi)
            K.check("Loadout 2 now uses what you wear" in r and dM.ask01 == -1 and dM.slots[1].picked() >= 3 and cM == exp01 and not once(Mi, dMf),
                    "X14 Yes = Use what I wear for the old equipped loadout: picked in place, asked no more (%s)" % r)
            r = run(Mi, 13)
            r2 = run(Mi, 13)
            r3 = run(Mi, 13)
            cM, dMf = census(Mi)
            K.check(r.startswith("+Returned item") and r2.startswith("+Returned item") and r3 == "=There are no returned items." and dMf.orphans.size() == 0
                    and cM == exp01, "X14 Returned items come out one per click (%s / %s / %s)" % (r, r2, r3))
            # ---- B: a PENDING 0.1 journal (a crashed 0.1 equip): repaired FIRST against the live inventory, then migrated
            kB1 = meta["B"]["key"]
            for ext in (".json", ".journal.json"):
                shutil.copy(os.path.join(fx, "mods", "Skyy_SkyyWardrobe", "loadouts", kB1 + ext), os.path.join(lo01, kB1 + ext))
            Mb = W.player(kB1, "Bo")
            for roll in (False, True):
                W.load(Mb, meta["B"]["live"], Codec)
                if roll:
                    # the engine rolled the inventory back to before the 0.1 equip: copper head + bow worn, nothing of loadout 1
                    W.clear(Mb)
                    setc(Mb.arm, 0, stack("Armor_Copper_Head", 1))
                    setc(Mb.hot, 0, stack("Weapon_Bow_Wood", 1))
                shutil.rmtree(os.path.join(Wd, "requip", kB1), ignore_errors=True)
                restart()
                r = run(Mb, 5)
                cB1, dB1 = census(Mb)
                j01 = json.load(open(os.path.join(lo01, kB1 + ".journal.json")))
                exp = {("Armor_Gold_Head", str(JClass("org.bson.BsonDocument").parse(gdoc("fabled", 30)).toJson())): 1,
                       ("Weapon_Sword_Mithril", str(JClass("org.bson.BsonDocument").parse(gdoc("mythic", 40)).toJson())): 1,
                       ("Food_Bread", ""): 7, ("Armor_Copper_Head", ""): 1, ("Weapon_Bow_Wood", ""): 1}
                K.check(cB1 == exp and not once(Mb, dB1) and "0.1 journal repaired first" in str(dB1.migrated) and j01["stage"] == "moving",
                        "X14 B (live %s): the pending 0.1 journal was repaired FIRST (in memory), every item once; the 0.1 journal file untouched (%s; %s; diff %s)"
                        % ("rolled back" if roll else "as at the crash", r, dB1.migrated, {k_: (exp.get(k_), cB1.get(k_)) for k_ in set(exp) | set(cB1) if exp.get(k_) != cB1.get(k_)}))
            # ---- C: a FAILED 0.1 journal keeps the profile shut until /requipadmin repair
            kC1 = "00000000-0000-0000-0000-0000000001c3"
            shutil.copy(os.path.join(fx, "mods", "Skyy_SkyyWardrobe", "loadouts", kB1 + ".json"), os.path.join(lo01, kC1 + ".json"))
            jf_ = json.load(open(os.path.join(fx, "mods", "Skyy_SkyyWardrobe", "loadouts", kB1 + ".journal.json")))
            jf_["stage"] = "failed"
            json.dump(jf_, open(os.path.join(lo01, kC1 + ".journal.json"), "w"))
            Mc = W.player(kC1, "Cid")
            W.load(Mc, meta["B"]["live"], Codec)
            restart()
            r = run(Mc, 6, 0, "1:0")
            dC1 = Store.get(kC1, Mc.u)
            K.check(r.startswith("-An interrupted 0.1 loadout change must be checked first") and dC1.bad and not os.path.isfile(os.path.join(Wd, "requip", kC1, "index.json")),
                    "X14 a FAILED 0.1 journal: Requip stays shut, nothing migrated (%s)" % r)
            P("WdRepairTask")(Mc.u, 0, True, None).run()
            cC1, dC1 = census(Mc)
            K.check(not dC1.bad and dC1.migrated is not None and not once(Mc, dC1) and cC1 == exp, "X14 /requipadmin repair: the failed 0.1 journal is repaired, then migrated (%s)" % dC1.migrated)
            # ---- D: a crash in the middle of the FIRST save of a migration: leftovers moved aside, migrated again, nothing doubled
            kD1 = "00000000-0000-0000-0000-0000000001d4"
            shutil.copy(src, os.path.join(lo01, kD1 + ".json"))
            Md = W.player(kD1, "Dee")
            W.load(Md, meta["A"]["live"], Codec)
            expD = census01(os.path.join(lo01, kD1 + ".json"), meta["A"]["live"])
            restart()
            Store.CRASH_FILES = 2
            died = False
            try:
                run(Md, 5)
            except Exception as ex_:
                died = "harness crash" in str(ex_)
            Store.CRASH_FILES = -1
            left = sorted(os.listdir(os.path.join(Wd, "requip", kD1)))
            restart()
            r = run(Md, 5)
            cD1, dD1 = census(Md)
            stale = [n_ for n_ in os.listdir(os.path.join(Wd, "requip", kD1)) if n_.startswith("stale-")]
            K.check(died and "index.json" not in left and stale and cD1 == expD and not once(Md, dD1) and dD1.migrated is not None,
                    "X14 a crash mid-way through the migration's first save: no index.json, so the next load moves the half files aside and migrates again (%s -> %s, %s)" % (left, stale, r))
            # ---- E: the REAL live 0.1 file (a scratch COPY, read only)
            live01 = os.path.join(LIVE, "Skyy_SkyyWardrobe", "loadouts")
            n_live = 0
            if os.path.isdir(live01):
                for f in sorted(os.listdir(live01)):
                    if not f.endswith(".json") or f.endswith(".journal.json"):
                        continue
                    k_ = f[:-5]
                    shutil.copy(os.path.join(live01, f), os.path.join(lo01, f))
                    uid = k_[:36]
                    state.setdefault("key", {})[uid] = k_
                    Ml = W.player(uid, "Skyy")
                    restart()
                    r = run(Ml, 5)
                    dL = Store.load(k_, uid)
                    j_ = json.load(open(os.path.join(live01, f)))
                    K.check(dL.migrated is not None and not dL.bad and dL.lastWorn == jn(j_["worn"]) and dL.ask01 == jn(j_["worn"]),
                            "X14 the live 0.1 file %s (copy) migrates: equipped loadout %d asked once, %d entries (%s)" % (f, jn(j_["worn"]) + 1, len(dL.entries), r))
                    del state["key"][uid]
                    n_live += 1
            K.notes.append("X14 live 0.1 files migrated (copies): %d" % n_live)

        # ============================================================ X15 files: unreadable / newer (shut, never written), shards, caps
        Fs = W.player("00000000-0000-0000-0000-000000000015", "Fil")
        kFs = str(Fs.u)
        Cfg.SHARD_RUN = 25
        for i in range(36):
            setc(Fs.sto, i, stack(pool_ids[i % len(pool_ids)], 1, gdoc("rare", i + 1)))
        r = run(Fs, 7)
        for i in range(30):
            setc(Fs.sto, i, stack("Weapon_Sword_Iron", 1, gdoc("unique", 100 + i)))
        r2 = run(Fs, 7)
        files = sorted(n_ for n_ in os.listdir(os.path.join(Wd, "requip", kFs)) if n_.startswith(("armor-", "items-")))
        K.check(r.startswith("+Deposited 36") and r2.startswith("+Deposited 30") and files == ["armor-000.json", "items-000.json", "items-001.json"],
                "X15 shards of 25 (pool.shardSize): 21 armor -> 1 file, 45 items -> 2 files (%s)" % files)
        sz = {n_: len(json.load(open(os.path.join(Wd, "requip", kFs, n_)))["entries"]) for n_ in files}
        K.check(sz == {"armor-000.json": 21, "items-000.json": 25, "items-001.json": 20}, "X15 ... filled in order (%s)" % sz)
        mt = {n_: os.path.getmtime(os.path.join(Wd, "requip", kFs, n_)) for n_ in files}
        time.sleep(0.05)
        f0 = int(Store.FILES)
        last = [e for e in Store.get(kFs, Fs.u).entries.values() if e.shard == 1 and e.space == 1][0]
        r = run(Fs, 14, 0, str(last.eid))
        mt2 = {n_: os.path.getmtime(os.path.join(Wd, "requip", kFs, n_)) for n_ in files}
        K.check(r == "+ok" and int(Store.FILES) - f0 == 2 and [n_ for n_ in files if mt2[n_] != mt[n_]] == ["items-001.json"],
                "X15 a change rewrites ONLY the shard it touches (+ index.json) (%s)" % [n_ for n_ in files if mt2[n_] != mt[n_]])
        restart()
        d15 = Store.get(kFs, Fs.u)
        K.check(d15.count(0) == 21 and d15.count(1) == 45 and not d15.bad, "X15 reload: every shard read back")
        Cfg.SHARD_RUN = 0
        Cfg.ITEMS_CAP = 40
        setc(Fs.sto, 35, stack("Weapon_Bow_Wood", 1))
        r = run(Fs, 6, 0, "2:35")
        restart()
        K.check(r.startswith("-Items space full (40)") and Store.get(kFs, Fs.u).count(1) == 45, "X15 a cap LOWER than the space: deposits refused, nothing deleted (%s)" % r)
        Cfg.ITEMS_CAP = 1000
        # unreadable shard / newer format: shut, never written over
        sh = os.path.join(Wd, "requip", kFs, "items-001.json")
        good = open(sh, "rb").read()
        open(sh, "wb").write(b"{ not json")
        restart()
        r = run(Fs, 6, 0, "2:35")
        d15 = Store.get(kFs, Fs.u)
        K.check(d15.bad and r.startswith("-Your Requip files could not be read") and open(sh, "rb").read() == b"{ not json", "X15 an unreadable shard: Requip shut, the file never written over (%s)" % r)
        ix = os.path.join(Wd, "requip", kFs, "index.json")
        ixb = open(ix, "rb").read()
        open(sh, "wb").write(good)
        open(ix, "w").write(json.dumps({"format": 3, "rev": 1}))
        restart()
        r = run(Fs, 6, 0, "2:35")
        K.check(Store.get(kFs, Fs.u).bad and "format 3" in r and json.load(open(ix))["format"] == 3, "X15 a NEWER format: shut, not written (%s)" % r)
        open(ix, "wb").write(ixb)
        restart()
        r = run(Fs, 6, 0, "2:35")
        K.check(r.startswith("+Into Requip") and not Store.get(kFs, Fs.u).bad, "X15 fixed by hand (+ reload): open again (%s)" % r)
        r = str(P("WdCmds").admin(None, JArray(JString)(["reload"])))
        K.check(r.startswith("+Reloaded:"), "X15 /requipadmin reload")

        # ============================================================ X16 THE PAGE (real builders, every view, every click)
        TP = JClass(FAKE_PKG + ".TestPage")
        UCB, UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
        Pg = W.player("00000000-0000-0000-0000-000000000016", "Pia")
        kPg = str(Pg.u)
        for i, a in enumerate(["Armor_Iron_Head", "Armor_Copper_Head", "Armor_Iron_Chest", "Weapon_Sword_Iron", "Weapon_Sword_Mithril"]):
            setc(Pg.sto, i, stack(a, 1, gdoc(["rare", "unique", "normal", "legendary", "mythic"][i], 5 * i)))
        setc(Pg.sto, 5, stack("Potion_Health", 9))
        setc(Pg.sto, 6, stack("Rock_Stone", 9))
        setc(Pg.hot, 8, stack("Skyy_Menu", 1))
        run(Pg, 7)
        setc(Pg.sto, 10, stack("Weapon_Bow_Wood", 1))
        br.put("profile:name:" + kPg, "Fox")
        pg = TP(Pg.pr)

        def build():
            b, ev = UCB(), UEB()
            pg.build(Pg.ref, b, ev, Pg.st)
            cmds_ = list(b.getCommands())
            text = " ".join(" ".join(str(x) for x in (c.selector, c.text, c.data) if x is not None) for c in cmds_)
            return text, list(ev.getEvents())

        def click(a, **kw):
            d_ = {"a": a, "t": str(pg.tok)}
            d_.update(kw)
            pg.handleDataEvent(Pg.ref, Pg.st, json.dumps(d_))
            return str(pg.info)

        text, evs = build()
        K.check("Profile Fox" in text and "Armor 3 / 1000" in text and "Items 3 / 1000" in text and "Loadouts 0 of 4" in text and "#SkyyRqL4" in text
                and "#SkyyRqL5" not in text, "X16 the head line + 4 open loadouts and the next locked one")
        K.check('ItemId: ""' not in text and not [m for m in re.findall(r"#(SkyyRq\w+)", text) if "_" in m], "X16 no empty ItemId (no client warning), no underscore in any element id")
        K.check("ItemGridSlot" not in text and "Auto-store: OFF" in text, "X16 icons only (no ItemGridSlot), auto-store shows OFF")
        r = click("sl", i="0")
        text, evs = build()
        K.check(pg.slot == 0 and pg.view == 0 and "Head pieces - click one to pick it" in text and "Selected: Head" in text, "X16 click the Head slot: the Armor space shows Head pieces")
        ihead = [c for c in pg.cells if c]
        K.check(len(ihead) == 2, "X16 ... exactly the 2 helmets (%s)" % ihead)
        r = click("pc", i="0")
        K.check(r.startswith("+Loadout 1: Head takes"), "X16 click a pool item with a slot selected = pick it (%s)" % r)
        build()
        r = click("sl", i="4")
        build()
        K.check(pg.view == 1 and len([c for c in pg.cells if c]) == 3, "X16 a hotbar slot shows the Items space (swords + the potion kind)")
        r = click("pk", v="empty")
        K.check(r.startswith("+Loadout 1: Hotbar 1 goes into Requip"), "X16 Empty (%s)" % r)
        build()
        r = click("pk", v="keep")
        build()
        # FIX2-F2 (fidelity critic 2): Pocket with no block held there shows the blocks in your Magic Bags; a click picks one
        state.setdefault("bags", {})[str(Pg.u)] = {"Rock_Stone": 120, "Ingredient_Bar_Iron": 0, "Weapon_Sword_Iron": 3}
        hb0 = getc(Pg.hot, 0)
        if hb0 is not None:
            Pg.hot.removeItemStackFromSlot(JShort(0), False)
        r = click("pk", v="pocket")
        text, evs = build()
        cellsP = [c for c in pg.cells if c]
        K.check(pg.view == 3 and r.startswith("=Click a block from your Magic Bags") and cellsP == ["b:Rock_Stone"] and "Blocks in your Magic Bags - click one for Hotbar 1" in text
                and "Pocket blocks" in text, "FIX2-F2 Pocket with nothing held: the page lists the BLOCKS in your Magic Bags (not the sword, not a 0 count) (%s / %s)" % (r, cellsP))
        r = click("pc", i="0")
        text, evs = build()
        pk4 = Store.get(str(Store.pkey(Pg.u)), Pg.u).slots[pg.sel].picks[4]
        K.check(r.startswith("+Loadout 1: Hotbar 1 fills with Rock_Stone") and pg.view == 1 and str(pk4) == "p:Rock_Stone:0",
                "FIX2-F2 ... a click on a bag block makes it the pocket pick, no block held (%s, %s)" % (r, pk4))
        r = click("pk", v="keep")
        build()
        if hb0 is not None:
            setc(Pg.hot, 0, hb0)
        r = click("so")
        text, evs = build()
        K.check(pg.sort == 1 and "Sort: rarity" in text, "X16 sort cycles (rarity)")
        r = click("q", **{"@RqQ": "mithril"})
        text, evs = build()
        K.check(len([c for c in pg.cells if c]) == 1 and "search: mithril" in text, "X16 search by id")
        click("q", **{"@RqQ": "sword mithril"})
        build()
        n1 = len([c for c in pg.cells if c])
        click("q", **{"@RqQ": "Sword_Mithril"})
        build()
        K.check(n1 == 1 and len([c for c in pg.cells if c]) == 1, "FIX-F3 search matches the readable name the page shows (sword mithril) as well as the id")
        r = click("qc")
        build()
        r = click("tab", v="2")
        text, evs = build()
        K.check(pg.view == 2 and pg.slot == -1 and "Your hotbar (top row) and storage" in text and "#SkyyRqP15Out" in text, "X16 Your inventory: page 1 = hotbar + storage; the refused block is covered")
        bow_cell = 9 + 10
        K.check(str(pg.cells[bow_cell]) == "s2:10:Weapon_Bow_Wood", "FIX-E3 an inventory cell remembers the item it showed (%s)" % pg.cells[bow_cell])
        setc(Pg.sto, 10, stack("Tool_Pickaxe_Iron", 1))
        r0 = click("pc", i=str(bow_cell))
        K.check(r0.startswith("-That slot changed - here it is again.") and str(getc(Pg.sto, 10).getItemId()) == "Tool_Pickaxe_Iron",
                "FIX-E3 a click on a cell whose slot changed since the page was drawn deposits NOTHING (%s)" % r0)
        setc(Pg.sto, 10, stack("Weapon_Bow_Wood", 1))
        build()
        r = click("pc", i=str(bow_cell))
        K.check(r.startswith("+Into Requip: Weapon_Bow_Wood"), "X16 click an inventory item = deposit (%s)" % r)
        build()
        r = click("pc", i="8")
        K.check(r.startswith("-The SkyWynn Menu item"), "X16 the menu item refuses with its reason (%s)" % r)
        build()
        r = click("pg", v="1")
        text, evs = build()
        K.check(pg.pg == 1 and "Your worn armor (top row) and backpack" in text, "X16 page 2 of the inventory = worn armor + backpack")
        click("pg", v="-1")
        build()
        click("tab", v="1")
        build()
        swd = [c for c in pg.cells if c][0]
        click("pc", i="0")
        text, evs = build()
        K.check(pg.det == swd and "#SkyyRqDn" in text and "In Requip. Picked in" in text, "X16 click an item without a slot = its details")
        r = click("dt")
        r2 = click("dt")
        K.check(r.startswith("+Taken out") or r.startswith("=Press Take out again"), "X16 Take out (asks twice only when it is picked) (%s / %s)" % (r, r2))
        build()
        r = click("da")
        build()
        click("tab", v="0")
        build()
        click("pc", i="0")
        build()
        r = click("df")
        r2 = click("df")
        K.check(r.startswith("=Press Forget again") and r2.startswith("-It is in Requip"), "X16 Forget asks twice, then refuses an IN entry (%s / %s)" % (r, r2))
        build()
        r = click("rn", **{"@RqName": "Tank"})
        build()
        K.check(str(Store.get(kPg, Pg.u).slots[0].name) == "Tank", "X16 Rename reads the name box (%s)" % r)
        r = click("sv")
        build()
        gap()
        r = click("eq")
        text, evs = build()
        K.check(r.startswith("+Equipped Tank") and "last worn" in text, "X16 Equip from the page (%s)" % r)
        r = click("uw")
        build()
        K.check("now uses what you wear" in r, "X16 Use what I wear from the page (%s)" % r)
        r = click("rs")
        r2 = click("rs")
        build()
        K.check(r.startswith("=Press Reset again") and r2.startswith("+Tank was reset"), "X16 Reset asks twice (%s / %s)" % (r, r2))
        r = click("au")
        text, evs = build()
        K.check(r.startswith("+Auto-store is ON") and "Auto-store: ON" in text, "X16 the auto-store toggle (%s)" % r)
        click("au")
        build()
        dP = Store.get(kPg, Pg.u)
        dP.ask01 = 0
        dP.orphan("test", stack("Weapon_Bow_Wood", 1, gdoc("rare", 99)))
        Store.save(dP)
        text, evs = build()
        K.check("Your old Wardrobe had" in text and "#SkyyRqY1" in text, "X16 the 0.1 question shows Yes / No")
        r = click("n1")
        text, evs = build()
        K.check(Store.get(kPg, Pg.u).ask01 == -1 and "returned item waits" in text and "#SkyyRqRo" in text, "X16 No: asked no more; then the Returned items line (%s)" % r)
        r = click("ro")
        K.check(r.startswith("+Returned item"), "X16 Take one out (%s)" % r)
        build()
        old_tok = str(pg.tok)
        pg.handleDataEvent(Pg.ref, Pg.st, json.dumps({"a": "eq", "t": "stale"}))
        K.check(str(pg.info).startswith("=The page changed"), "X16 a click from a stale page: rebuilt, nothing done")
        pg.handleDataEvent(Pg.ref, Pg.st, '{"a":"close"}')
        K.check(pg.closes == 1 and pg.rebuilds > 20, "X16 Close")
        cPg, dPg = census(Pg)
        K.check(not once(Pg, dPg), "X16 exactly once after every page click")

        # ============================================================ X17 the commands (player + admin forms)
        Cmds = P("WdCmds")
        Pg.pr.msgs = None
        for a_ in (["help"], ["dump"], ["auto"], ["auto", "off"], ["1"], ["equip", "2"], ["save", "1"], ["wear", "2"], ["name", "2", "Mine"], ["dance", "2"]):
            gap()
            Cmds.player(Pg.pr, Pg.ref, Pg.st, JArray(JString)(a_))
        said = [str(x) for x in (Pg.pr.msgs or [])]
        K.check(len(said) == 10 and said[0].startswith("[Requip] /requip opens") and said[2].startswith("[Requip] Auto-store is ON") and said[3].startswith("[Requip] Auto-store is OFF")
                and "Equipped" in said[4] and "Equipped" in said[5] and "Saved into" in said[6] and "now uses what you wear" in said[7] and "Mine" in said[8] and "/requip opens" in said[9],
                "X17 /requip help | dump | auto | auto off | <n> | equip | save | wear | name | unknown (%s)" % said)
        res = [str(Cmds.admin(None, JArray(JString)(a_))) for a_ in (["help"], ["info", "Pia"], ["slots", "Pia", "9"], ["slots", "Pia", "99"], ["info", "Nobody"])]
        nt_ = drain(H) if False else 0
        time.sleep(0.4)
        nt_ = drain(H)
        K.check(res[0].startswith("=/requipadmin") and res[1].startswith("=" + kPg) and res[2].startswith("=Slots change queued") and nt_ == 1 and Store.get(kPg, Pg.u).floor == 9
                and res[3].startswith("-Slots is 0") and res[4].startswith("-Nobody is not online"), "X17 /requipadmin forms; slots runs on the player's world thread (%s)" % res)

        # ============================================================ X18 the bridge functions (research/Requip-Smithing-Spec.md section 5)
        Fn = P("WdFn")
        Q = W.player("00000000-0000-0000-0000-000000000018", "Quin")
        kQ = str(Q.u)

        def fa(mode, *args):
            a = JArray(JObject)(len(args))
            for i, x in enumerate(args):
                a[i] = x
            return Fn(mode).apply(a)
        TPM = JClass(TESTPM)
        TPM.OPENS = 0
        K.check(bool(Fn(0).apply(Q.u)) and drain(H) == 1 and TPM.OPENS == 1 and str(TPM.CUR.getClass().getSimpleName()) == "WdPage"
                and not bool(Fn(0).apply("x")) and not bool(Fn(0).apply(UUID_.randomUUID())), "X18 wardrobe:fn:open (+ requip:fn:open): the page opens on the world thread; bad / offline -> FALSE")
        K.check(fa(1, Q.u, "Armor_Iron_Head", JInt(1)) is None and str(fa(1, Q.u, "Rock_Stone", JInt(5))).startswith("Blocks") and str(fa(1, Q.u, "Gone_Item", JInt(1))).startswith("The game no longer knows"),
                "X18 canDeposit: armor accepted (null), a block / an unknown id refused with the reason")
        Cfg.ARMOR_CAP = 0 + 1
        setc(Q.sto, 0, stack("Armor_Gold_Head", 1))
        r = str(fa(2, Q.u, "storage", JInt(0)))
        K.check(r.startswith("eid:") and len(r) == 20 and str(fa(1, Q.u, "Armor_Iron_Head", JInt(1))) == "Armor space full (1)", "X18 depositSlot -> eid:<hex>; then canDeposit says the space is full (%s)" % r)
        Cfg.ARMOR_CAP = 1000
        setc(Q.hot, 3, stack("Rock_Stone", 4))
        r2 = str(fa(2, Q.u, "hotbar", JInt(3)))
        r3 = str(fa(2, Q.u, "pocket", JInt(3)))
        K.check(r2.startswith("refused:Blocks") and r3.startswith("refused:unknown section"), "X18 depositSlot refusals (%s / %s)" % (r2, r3))
        craft = stack("Weapon_Sword_Mithril", 1, gdoc("rare", 33))
        r = str(fa(3, Q.u, craft, "smithing", '{"inv": {"Wood_Oak_Log": 5}}'))
        dQ = Store.get(kQ, Q.u)
        eC = dQ.entry(r[4:])
        K.check(r.startswith("eid:") and eC is not None and ein(eC) and str(Codec.rar(eC.stack)) == "rare", "X18 deposit (a crafted stack in no inventory) -> eid:<hex>, IN (%s)" % r)
        r = str(fa(3, Q.u, stack("Potion_Health", 3), "smithing", ""))
        K.check(r.startswith("kind:") and int(Store.get(kQ, Q.u).entry(r[5:]).count) == 3, "X18 deposit of a stackable -> kind:<hex> (%s)" % r)
        # a craft deposit that crashed: materials back (the engine rolled the inventory back) -> undone; materials gone -> kept
        for back in (True, False):
            setc(Q.sto, 20, stack("Ingredient_Bar_Iron", 5 if back else 1))
            Tx.CRASH_AT = 0
            died = False
            try:
                fa(3, Q.u, stack("Weapon_Bow_Wood", 1, gdoc("unique", 44 if back else 45)), "smithing", '{"inv": {"Ingredient_Bar_Iron": 5}}')
            except Exception as ex_:
                died = "harness crash" in str(ex_)
            Tx.CRASH_AT = -1
            restart()
            r = run(Q, 5)
            bows = [e for e in Store.get(kQ, Q.u).entries.values() if str(e.itemId()) == "Weapon_Bow_Wood"]
            K.check(died and (len(bows) == (0 if back else 1)) and (("undone" in r) == back), "X18 a crashed craft deposit, materials %s: %s (%s)" % ("back" if back else "spent", "undone" if back else "kept", r))
            Q.sto.removeItemStackFromSlot(JShort(20), False)
        lst = fa(4, Q.u, "armor")
        lsi = [x for x in fa(4, Q.u, "items") if str(x[1]) == "Weapon_Sword_Mithril"]
        K.check(len(lst) == 1 and str(lst[0][1]) == "Armor_Gold_Head" and len(lsi) == 1 and sorted(str(x[1]) for x in fa(4, Q.u, "items")) == ["Weapon_Bow_Wood", "Weapon_Sword_Mithril"]
                and len(fa(4, Q.u, "all")) == 3, "X18 list: IN gear only (kinds left out), per space")
        lst[0][2].put("x", JClass("org.bson.BsonString")("y")) if lst[0][2] is not None else None
        K.check(Store.get(kQ, Q.u).entry(str(lst[0][0])).stack.getMetadata() is None or not Store.get(kQ, Q.u).entry(str(lst[0][0])).stack.getMetadata().containsKey("x"),
                "X18 list hands out COPIES (changing one changes nothing)")
        r = str(fa(5, Q.u, str(lsi[0][0])))
        r2 = str(fa(5, Q.u, str(lsi[0][0])))
        K.check(r == "ok" and r2.startswith("It is not in Requip right now") and str(lsi[0][0]) in stamps_of(Q), "X18 fetch: ok (stamp kept, OUT); again: the reason (%s / %s)" % (r, r2))
        rp = run(Q, 10, 0, "4|e:" + str(lsi[0][0]))
        K.check(rp.startswith("+") and bool(fa(6, Q.u, str(lsi[0][0]), "merged")) and not bool(fa(6, Q.u, str(lst[0][0]), "merged")) and str(Store.get(kQ, Q.u).entry(str(lsi[0][0])).gone) == "merged"
                and run(Q, 10, 1, "4|e:" + str(lsi[0][0])).startswith("-That item is used up (merged)"), "X18 gone: an OUT entry is marked used up (merged); an IN entry refuses; it cannot be picked any more")
        for c in Q.secs:
            for i in range(int(c.getCapacity())):
                if Codec.stampOf(getc(c, i)) == lsi[0][0]:
                    c.removeItemStackFromSlot(JShort(i), False)
        gap()
        r = run(Q, 1, 0)
        K.check("Hotbar 1: Weapon_Sword_Mithril is used up (merged)" in r, "X18 a picked item that was used up: Equip notes it (%s)" % r)
        # off the player's world thread: null (never blocks, never hops)
        other = JClass("java.lang.Thread")()
        E.jf(JClass("com.hypixel.hytale.component.Store"), "thread").set(Q.st, other)
        K.check(fa(2, Q.u, "storage", JInt(0)) is None and fa(4, Q.u, "all") is None and fa(5, Q.u, "x") is None and fa(3, Q.u, craft, "s", "") is None
                and fa(6, Q.u, "x", "y") is None, "X18 every world-thread fn answers null off the world thread (the REAL Store.isInThread)")
        E.jf(JClass("com.hypixel.hytale.component.Store"), "thread").set(Q.st, JClass("java.lang.Thread").currentThread())
        K.check(fa(2, "x") is None and Fn(4).apply("x") is None, "X18 bad arguments -> null")

        # ============================================================ X19 join task, timer, quit, auto-store, admin repair through the hop
        Jn = W.player("00000000-0000-0000-0000-000000000019", "Jo")
        kJ = str(Jn.u)
        setc(Jn.sto, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 1)))
        setc(Jn.hot, 4, stack("Wood_Oak_Log", 2))
        run(Jn, 10, 0, "8|pocket") if False else None
        setc(Jn.hot, 0, stack("Wood_Oak_Log", 2))
        run(Jn, 10, 0, "4|pocket")
        Jn.hot.removeItemStackFromSlot(JShort(0), False)
        state.setdefault("bags", {})[str(Jn.u)] = {"Wood_Oak_Log": 50}
        gap()
        run(Jn, 1, 0)
        base, _ = census(Jn)
        Tx.CRASH_AT = 0
        try:
            run(Jn, 6, 0, "2:0")
        except Exception:
            pass
        Tx.CRASH_AT = -1
        restart()
        br.remove("requip:pocket:" + kJ)
        PRE = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent")
        evr = U.allocateInstance(PRE.class_)
        E.jf(PRE, "playerRef").set(evr, Jn.ref)
        br.put("profile:busy:" + kJ, True)
        P("WdReady")().accept(evr)
        time.sleep(2.6)
        n1 = drain(H)
        K.check(n1 == 1 and os.path.isfile(os.path.join(Wd, "requip", kJ, "journal.json")), "X19 join: the repair task waits while profile:busy (%d tasks)" % n1)
        br.remove("profile:busy:" + kJ)
        time.sleep(1.4)
        n2 = drain(H)
        c, d = census(Jn)
        pm = br.get("requip:pocket:" + kJ)
        K.check(n2 == 1 and not os.path.isfile(os.path.join(Wd, "requip", kJ, "journal.json")) and c == base and not once(Jn, d)
                and pm is not None and dict((int(k_), str(v)) for k_, v in pm.items()) == {0: "Wood_Oak_Log"},
                "X19 ... then repairs on the world thread and publishes requip:pocket of the last worn loadout (%d tasks)" % n2)
        P("WdReady")().accept(evr)
        time.sleep(2.4)
        K.check(drain(H) == 0, "X19 PlayerReadyEvent again (a world switch): once per session")

        @JImplements(PKG + "WdApi")
        class Api:
            @JOverride
            def online(self):
                return JArray(UUID_)([Jn.u])

            @JOverride
            def byName(self, n):
                return Jn.u

            @JOverride
            def nameOf(self, u):
                return "Jo"

            @JOverride
            def tell(self, u, t, c):
                pass
        P("WdEng").API = Api()
        Gate.EPOCH.put(Jn.u, JLong(1))
        br.put("profile:epoch:" + kJ, JLong(2))
        state.setdefault("key", {})[kJ] = kJ + "-p2"
        P("WdTimer")().run()
        K.check(br.get("requip:pocket:" + kJ) is None and Gate.settleLeft(Jn.u, int(time.time() * 1000)) > 25000,
                "X19 the timer sees the profile switch: settle window + requip:pocket of the old profile dropped")
        del state["key"][kJ]
        Gate.EPOCHAT.clear()
        Gate.BUSYAT.clear()
        # auto-store: plain armor / weapons / tools from storage + backpack (never the hotbar, potions, blocks or stamped items)
        setc(Jn.sto, 5, stack("Armor_Copper_Legs", 1))
        setc(Jn.sto, 6, stack("Potion_Health", 2))
        setc(Jn.sto, 7, stack("Rock_Stone", 2))
        setc(Jn.bak, 0, stack("Tool_Hatchet_Iron", 1))
        setc(Jn.hot, 6, stack("Weapon_Bow_Wood", 1))
        st_before = stamps_of(Jn)
        Cfg.AUTO_HOT = False
        run(Jn, 11, 0, "on")
        Auto.LASTRUN.clear()
        Jn.pr.msgs = None
        P("WdTimer")().run()
        na = drain(H)
        dJ = Store.get(kJ, Jn.u)
        K.check(na == 1 and getc(Jn.sto, 5) is None and getc(Jn.bak, 0) is None and getc(Jn.sto, 6) is not None and getc(Jn.sto, 7) is not None
                and getc(Jn.hot, 6) is not None and getc(Jn.sto, 0) is None and stamps_of(Jn) == st_before and any("Auto-stored 3 items" in str(m) for m in (Jn.pr.msgs or [])),
                "X19 auto-store ON: the timer queues a world task that stores the plain sword, copper legs + hatchet only (%s)" % [str(m) for m in (Jn.pr.msgs or [])])
        P("WdTimer")().run()
        K.check(drain(H) == 0, "X19 auto-store waits autoStore.seconds between runs")
        aj = json.load(open(os.path.join(Wd, "requip", "autostore.json")))
        K.check(aj["players"].get(kJ) is True, "X19 the per-player switch is saved (autostore.json)")
        Auto.load(Auto.FILE)
        K.check(bool(Auto.isOn(Jn.u)), "X19 ... and read back after a restart")
        Cfg.AUTO_ON = False
        Auto.LASTRUN.clear()
        P("WdTimer")().run()
        K.check(drain(H) == 0, "X19 the server switch off: no auto-store runs")
        Cfg.AUTO_ON = True
        # FIX-F1 (fidelity critic 1) + FIX2-F1 (fixer 2, fidelity critic 1): autoStore.hotbar (default on) takes gear that ARRIVES in the
        # hotbar (pickups) - never what was already there (your own tools) and never the HELD slot
        ASIC = JClass("com.hypixel.hytale.server.core.inventory.ActiveSlotInventoryComponent")
        hotc = Jn.st.comps.get(Jn.ref).get(W.types["hot"])
        E.jf(ASIC, "activeSlot").set(hotc, JByte(3))
        setc(Jn.hot, 3, stack("Weapon_Sword_Iron", 1))
        Cfg.AUTO_HOT = True
        Auto.SEEN.clear()
        Auto.LASTRUN.clear()
        Jn.pr.msgs = None
        P("WdTimer")().run()
        na0 = drain(H)
        K.check(na0 == 1 and getc(Jn.hot, 6) is not None and getc(Jn.hot, 3) is not None and not any("Auto-stored" in str(m) for m in (Jn.pr.msgs or [])),
                "FIX2-F1 auto-store's first look at the hotbar: the bow already in hotbar 7 and the held sword are YOURS - nothing is swept (%s)" % [str(m) for m in (Jn.pr.msgs or [])])
        setc(Jn.hot, 7, stack("Tool_Pickaxe_Iron", 1))
        setc(Jn.hot, 8, stack("Weapon_Bow_Wood", 1))
        Auto.LASTRUN.clear()
        Jn.pr.msgs = None
        P("WdTimer")().run()
        na = drain(H)
        K.check(na == 1 and int(Ops.heldSlot(Jn.st, Jn.ref)) == 3 and getc(Jn.hot, 7) is None and getc(Jn.hot, 6) is not None and getc(Jn.hot, 8) is None
                and getc(Jn.hot, 3) is not None and getc(Jn.hot, 0) is not None and any("Auto-stored 2 items" in str(m) for m in (Jn.pr.msgs or [])),
                "FIX-F1/FIX2-F1 auto-store with autoStore.hotbar: the pickaxe and the 2nd bow that ARRIVED in the hotbar go in; the bow that was there, the HELD sword (4) and the pocket blocks stay (%s)" % [str(m) for m in (Jn.pr.msgs or [])])
        Auto.LASTRUN.clear()
        Jn.pr.msgs = None
        Jn.hot.removeItemStackFromSlot(JShort(6), False)
        P("WdTimer")().run()
        drain(H)
        setc(Jn.hot, 5, stack("Weapon_Bow_Wood", 1))
        Auto.LASTRUN.clear()
        P("WdTimer")().run()
        drain(H)
        K.check(getc(Jn.hot, 5) is None, "FIX2-F1 ... a bow dropped from the hotbar and picked up again is a pickup: it goes in")
        Auto.SEEN.put(Jn.u, JArray(JObject)([JLong(-99), JClass("java.util.HashMap")()]))
        hk_ = Auto.hotKeep(Jn.u, JArray(JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer"))(Jn.secs))
        K.check(hk_ is None, "FIX2-F1 ... after a profile switch (another epoch) the new hotbar is looked at fresh (nothing swept)")
        picks = [e for e in ent_by_id(Store.get(kJ, Jn.u), "Tool_Pickaxe_Iron") if ein(e)]
        r = run(Jn, 8, 0, str(picks[0].eid))
        where = [(i, x) for i, x in enumerate(Jn.secs) for q in range(int(x.getCapacity())) if getc(x, q) is not None and str(getc(x, q).getItemId()) == "Tool_Pickaxe_Iron"]
        Auto.LASTRUN.clear()
        P("WdTimer")().run()
        drain(H)
        where2 = [(i, q) for i, x in enumerate(Jn.secs) for q in range(int(x.getCapacity())) if getc(x, q) is not None and str(getc(x, q).getItemId()) == "Tool_Pickaxe_Iron"]
        K.check(r.startswith("+Taken out: Tool_Pickaxe_Iron") and len(where) == 1 and len(where2) == 1,
                "FIX-F1 what you Take out stays out: auto-store does not put the taken-out pickaxe straight back (%s, %s)" % (r, where2))
        sec_, sl_ = where2[0]
        Jn.secs[sec_].removeItemStackFromSlot(JShort(sl_), False)
        Auto.LASTRUN.clear()
        P("WdTimer")().run()
        drain(H)
        setc(Jn.sto, 9, stack("Tool_Pickaxe_Iron", 1))
        Auto.LASTRUN.clear()
        P("WdTimer")().run()
        drain(H)
        K.check(getc(Jn.sto, 9) is None and Auto.KEEP.get(Jn.u) is not None and Auto.KEEP.get(Jn.u).isEmpty(),
                "FIX-F1 ... the keep-out shrinks when you no longer carry it: a pickaxe picked up later is auto-stored again")
        Jn.hot.removeItemStackFromSlot(JShort(3), False)
        E.jf(ASIC, "activeSlot").set(hotc, JByte(0))
        run(Jn, 11, 0, "off")
        PDE = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent")
        Gate.LAST.put(Jn.u, JLong(1))
        br.put("requip:pocket:" + kJ, JClass("java.util.HashMap")())
        P("WdQuit")().accept(PDE(Jn.pr))
        K.check(not P("WdReady").SESSION.containsKey(Jn.u) and not Gate.LAST.containsKey(Jn.u) and br.get("requip:pocket:" + kJ) is None, "X19 disconnect: session state + requip:pocket forgotten")
        P("WdEng").API = None
        onl = [str(x) for x in P("WdEng").online()]
        K.check(kJ in onl and str(P("WdEng").nameOf(Jn.u)) == "Jo", "X19 the real online() / nameOf (Universe)")
        Jr.PENDING.put("somekey", JLong(1))
        os.makedirs(os.path.join(Wd, "requip", "somekey"), exist_ok=True)
        open(os.path.join(Wd, "requip", "somekey", "journal.json"), "w").write('{"stage": "saved"}')
        Jr.PENDING.put("movekey", JLong(1))
        os.makedirs(os.path.join(Wd, "requip", "movekey"), exist_ok=True)
        open(os.path.join(Wd, "requip", "movekey", "journal.json"), "w").write('{"stage": "moving"}')
        P("WdTimer")().run()
        drain(H)
        K.check(not os.path.isfile(os.path.join(Wd, "requip", "somekey", "journal.json")) and os.path.isfile(os.path.join(Wd, "requip", "movekey", "journal.json")),
                "X19 the timer deletes saved journals past their keep time, never a moving one")
        Jr.PENDING.clear()
        Jr.PENDING.put("k2", JLong(int(time.time() * 1000)))
        os.makedirs(os.path.join(Wd, "requip", "k2"), exist_ok=True)
        open(os.path.join(Wd, "requip", "k2", "journal.json"), "w").write("{}")
        K.check(Jr.dropAll() == 1 and not os.path.isfile(os.path.join(Wd, "requip", "k2", "journal.json")), "X19 shutdown: pending journals dropped")
        open(os.path.join(Wd, "requip", "autostore.json"), "w").write("{ broken")
        Auto.load(Auto.FILE)
        r = run(Jn, 11, 0, "on")
        K.check(bool(Auto.BAD) and r.startswith("-Your auto-store switch could not be saved") and open(os.path.join(Wd, "requip", "autostore.json")).read() == "{ broken",
                "X19 an unreadable autostore.json: every switch off, never written over (%s)" % r)

        # ============================================================ X20 the stamp through SkyyGear's own document write (the jar in this JVM)
        if GEAR and os.path.isfile(GEAR):
            try:
                GD = JClass("com.skyy.gear.GearData")
                s0 = Codec.stamp(stack("Weapon_Sword_Iron", 1, gdoc("rare", 12)), "5eed5eed5eed5eed")
                doc = JClass("org.bson.BsonDocument").parse('{"v": 1, "r": "legendary", "lvl": 14, "id": true}')
                o = GD.put(s0, doc, None)
                md = o.getMetadata()
                K.check(str(Codec.stampOf(o)) == "5eed5eed5eed5eed" and str(Codec.rar(o)) == "legendary" and int(Codec.lv(o)) == 14,
                        "X20 SkyyGear %s GearData.put (reforge / level-up / identify write the document this way) keeps the SkyyRequip stamp (keys %s)"
                        % (os.path.basename(GEAR), sorted(str(k_) for k_ in md.keySet())))
            except Exception as ex_:
                K.notes.append("X20 SkyyGear GearData.put could not run in the bare JVM (%s) - the bytecode check (B) covers it" % ex_)
        else:
            K.notes.append("X20 no SkyyGear jar - skipped")

        # ============================================================ X21 the fixer round (critics of R1): one check per fix
        # FIX-S1: a save that fails after SOME files were written (index.json locked) - the files are rewritten from memory, or the
        # journal STAYS so the next action / join repairs them: never an item both on you and IN the pool after a restart
        ICA = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
        F1 = W.player("00000000-0000-0000-0000-000000000f01", "Fae")
        kF1 = str(F1.u)
        setc(F1.sto, 0, stack("Weapon_Sword_Mithril", 1, gdoc("rare", 3)))
        setc(F1.sto, 1, stack("Weapon_Sword_Mithril", 1, gdoc("rare", 4)))
        setc(F1.sto, 2, stack("Weapon_Sword_Iron", 1))
        base, _ = census(F1)
        r = run(F1, 6, 0, "2:0")
        ixp = os.path.join(Wd, "requip", kF1, "index.json")
        FIS = JClass("java.io.FileInputStream")
        lockf = FIS(ixp)
        kept0 = int(Tx.SAVE_KEPT)
        try:
            r2 = run(F1, 6, 0, "2:1")
            jkept = os.path.isfile(os.path.join(Wd, "requip", kF1, "journal.json"))
            r3 = run(F1, 6, 0, "2:2")
        finally:
            lockf.close()
        K.check(r.startswith("+") and r2.startswith("-Could not save Requip - everything was put back; Requip checks its files") and getc(F1.sto, 1) is not None
                and int(Tx.SAVE_KEPT) == kept0 + 1 and jkept and r3.startswith("-Requip still cannot save its files"),
                "FIX-S1 index.json locked: the 2nd deposit is put back, its files cannot be rewritten -> the journal is KEPT; the next action retries the save from memory first (FIX2-D2) (%s / %s / %s)" % (r, r2, r3))
        restart()
        r4 = run(F1, 5)
        c, d = census(F1)
        K.check(c == base and not once(F1, d) and jresolved(kF1) and len([e for e in ent_by_id(d, "Weapon_Sword_Mithril") if ein(e)]) == 1,
                "FIX-S1 ... after a restart the repair reconciles: ONE Mithril sword in the pool, one on you - no copy (%s; %s)" % (r4, c))
        Store.FAIL_NEXT = 1
        r5 = run(F1, 6, 0, "2:1")
        jp_ = os.path.join(Wd, "requip", kF1, "journal.json")
        jd = json.load(open(jp_)) if os.path.isfile(jp_) else None
        restart()
        c, d = census(F1)
        K.check(r5 == "-Could not save Requip - everything was put back (see the server log)." and getc(F1.sto, 1) is not None and c == base and not once(F1, d),
                "FIX-S1 a save that fails but whose files are rewritten from memory: the step is dropped, files match what you carry (%s, journal %s)" % (r5, None if jd is None else jd.get("stage")))
        Jr.PENDING.clear()
        os.makedirs(os.path.join(Wd, "requip", kF1), exist_ok=True)
        open(jp_, "w").write('{"format": 3, "stage": "moving", "steps": []}')
        dF = Store.get(kF1, F1.u)
        csF = JArray(ICA)(F1.secs)
        mvl = JClass("java.util.ArrayList")()
        mvl.add(Tx.depMove(dF, csF, 2, 1, JClass("java.util.HashMap")(), JArray(JInt)(2), JClass("java.util.ArrayList")()))
        rg = str(Tx.run(dF, "deposit", mvl, csF, "Deposit"))
        K.check(rg.startswith("-An interrupted Requip change is still being checked") and getc(F1.sto, 1) is not None and json.load(open(jp_))["stage"] == "moving",
                "FIX-S1 a transaction never writes over an unrepaired journal (%s)" % rg)
        os.remove(jp_)

        # FIX-S2: a journal left on a profile you were NOT using is repaired the moment you switch INTO it (not at your first Requip
        # action, after you may have picked up more of the same kind)
        @JImplements(PKG + "WdApi")
        class Api2:
            def __init__(self, u):
                self.u = u

            @JOverride
            def online(self):
                return JArray(UUID_)([self.u])

            @JOverride
            def byName(self, n):
                return self.u

            @JOverride
            def nameOf(self, u):
                return "Sam"

            @JOverride
            def tell(self, u, t, c):
                pass
        Sm = W.player("00000000-0000-0000-0000-000000000f02", "Sam")
        kS = str(Sm.u)
        state.setdefault("key", {})[kS] = kS + "-p1"
        P("WdEng").API = Api2(Sm.u)
        br.put("profile:epoch:" + kS, JLong(5))
        P("WdTimer")().run()
        drain(H)
        setc(Sm.sto, 0, stack("Armor_Iron_Head", 1))
        base1, _ = census(Sm, kS + "-p1")
        Tx.CRASH_AFTER_SAVE = True
        try:
            run(Sm, 6, 0, "2:0")
        except Exception:
            pass
        Tx.CRASH_AFTER_SAVE = False
        jp1 = os.path.join(Wd, "requip", kS + "-p1", "journal.json")
        restart()
        snap1 = W.snap(Sm)
        W.clear(Sm)
        state["key"][kS] = kS + "-p2"
        br.put("profile:epoch:" + kS, JLong(6))
        sw0 = int(P("WdTimer").SWITCH_REPAIRS.get())
        P("WdTimer")().run()
        time.sleep(0.6)
        drain(H)
        sw1 = int(P("WdTimer").SWITCH_REPAIRS.get())
        still = os.path.isfile(jp1)
        W.restore(Sm, snap1)
        state["key"][kS] = kS + "-p1"
        br.put("profile:epoch:" + kS, JLong(7))
        P("WdTimer")().run()
        time.sleep(0.6)
        nt = drain(H)
        sw2 = int(P("WdTimer").SWITCH_REPAIRS.get())
        gone1 = not os.path.isfile(jp1)
        setc(Sm.sto, 1, stack("Armor_Iron_Head", 1))
        c, d = census(Sm, kS + "-p1")
        exp = dict(base1)
        exp[("Armor_Iron_Head", "")] = exp.get(("Armor_Iron_Head", ""), 0) + 1
        K.check(still and sw1 == sw0 and sw2 == sw0 + 1 and nt >= 1 and gone1 and c == exp and len([e for e in ent_by_id(d, "Armor_Iron_Head") if ein(e)]) == 1,
                "FIX-S2 switching to profile 2 leaves profile 1's journal alone; switching BACK repairs it at once (the helmet stays IN), so a helmet picked up afterwards is never counted against it (%s %s %s %s %s %s)" % (still, sw0, sw1, sw2, nt, c))
        P("WdEng").API = None
        del state["key"][kS]
        br.remove("profile:epoch:" + kS)
        Gate.EPOCHAT.clear()
        Gate.BUSYAT.clear()

        # FIX-S4: zero / unreadable material counts are no evidence (a crash then KEEPS the crafted item)
        Mt = W.player("00000000-0000-0000-0000-000000000f04", "Mat")
        setc(Mt.sto, 0, stack("Ingredient_Bar_Iron", 2))
        csM = JArray(ICA)(Mt.secs)
        K.check(not bool(Tx.matsBack('{"inv":{"Ingredient_Bar_Iron":0}}', csM, str(Mt.u))) and not bool(Tx.matsBack('{"inv":{"Ingredient_Bar_Iron":"3"}}', csM, str(Mt.u)))
                and bool(Tx.matsBack('{"inv":{"Ingredient_Bar_Iron":2}}', csM, str(Mt.u))) and not bool(Tx.matsBack('{"inv":{"Ingredient_Bar_Iron":3}}', csM, str(Mt.u)))
                and bool(Tx.matsBack('{"inv":{"Ingredient_Bar_Iron":2, "Wood_Oak_Log":0}}', csM, str(Mt.u))),
                "FIX-S4 matsBack: a 0 or string count never proves the materials are back; real counts still do")
        craftS = stack("Weapon_Sword_Iron", 1, gdoc("rare", 7))
        Tx.CRASH_AT = 0
        diedM = False
        try:
            fa(3, Mt.u, craftS, "test", '{"inv":{"Ingredient_Bar_Iron":0}}')
        except Exception as ex_:
            diedM = "harness crash" in str(ex_)
        Tx.CRASH_AT = -1
        restart()
        rr = run(Mt, 5)
        dM = Store.get(str(Mt.u), Mt.u)
        K.check(diedM and len([e for e in ent_by_id(dM, "Weapon_Sword_Iron") if ein(e)]) == 1 and "undone" not in rr,
                "FIX-S4 a crashed craft deposit whose evidence is all zero keeps the crafted sword (%s)" % rr)

        # FIX-S5: a pocket slot never gets more than the block's max stack (pocket.target 500, Rock_Stone stacks to 100)
        Pk = W.player("00000000-0000-0000-0000-000000000f05", "Pok")
        setc(Pk.hot, 0, stack("Rock_Stone", 2))
        rp = run(Pk, 10, 0, "4|pocket")
        Pk.hot.removeItemStackFromSlot(JShort(0), False)
        state.setdefault("bags", {})[str(Pk.u)] = {"Rock_Stone": 1000}
        Cfg.POCKET_N = 500
        gap()
        r = run(Pk, 1, 0)
        Cfg.POCKET_N = 0
        K.check(rp.startswith("+") and getc(Pk.hot, 0) is not None and int(getc(Pk.hot, 0).getQuantity()) == 100 and state["bags"][str(Pk.u)]["Rock_Stone"] == 900,
                "FIX-S5 pocket.target 500: the slot gets 100 (the max stack), 900 stay in the bags (%s)" % r)

        # ============================================================ X22 fixer 2 (the second critics): one check per fix
        # FIX2-D1 (data critic 1): a craft deposit whose save fails twice is refused - the caller keeps the item. Its journal step is marked
        # aborted, so the repair after a restart never rebuilds it as IN (even when a failed save had already written it into a shard)
        Cr = W.player("00000000-0000-0000-0000-000000000f06", "Cra")
        kC = str(Cr.u)
        setc(Cr.sto, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 5)))
        r0 = run(Cr, 6, 0, "2:0")
        craftB = stack("Weapon_Bow_Wood", 1, gdoc("rare", 77))
        Store.FAIL_NEXT = 2
        rc = str(fa(3, Cr.u, craftB, "test", ""))
        Store.FAIL_NEXT = 0
        jC = os.path.join(Wd, "requip", kC, "journal.json")
        jdC = json.load(open(jC)) if os.path.isfile(jC) else {}
        abC = [m for st_ in jdC.get("steps", []) for m in st_.get("moves", []) if jn(m.get("t")) == 5]
        K.check(r0.startswith("+") and rc.startswith("refused:Could not save Requip - everything was put back; Requip checks") and len(abC) == 1 and abC[0].get("ab") is True
                and bool(Tx.KEPT.containsKey(kC)), "FIX2-D1 a craft deposit whose save fails twice: refused, its journal move is marked aborted, the memory is kept (%s / %s)" % (rc, abC))
        setc(Cr.sto, 5, craftB)      # the caller (SkyyGear) falls back to the inventory
        eidC = str(abC[0]["eid"]) if abC else "0000000000000000"
        shp = Paths.get(os.path.join(Wd, "requip", kC, "items-000.json"))
        shd = Store.readDoc(shp)
        En = P("WdEntry")(eidC)
        En.space = 1
        En.spot = -1
        setattr(En, "in_", True)
        En.stack = Codec.stamp(craftB, eidC)
        En.setShow(craftB)
        shd.getArray("entries").add(En.toDoc())
        Store.atomicWrite(shp, JString(str(Codec.toJson(shd))).getBytes("UTF-8"))
        restart()
        K.check(len([e for e in ent_by_id(Store.load(kC, kC), "Weapon_Bow_Wood") if ein(e)]) == 1, "FIX2-D1 ... (set-up: a phantom IN bow in the shard, as a half-written save leaves it)")
        rrC = run(Cr, 5)
        c, d = census(Cr)
        bowk = ("Weapon_Bow_Wood", str(JClass("org.bson.BsonDocument").parse(gdoc("rare", 77)).toJson()))
        jdC2 = json.load(open(jC)) if os.path.isfile(jC) else {}
        K.check(c.get(bowk) == 1 and not once(Cr, d) and not [e for e in ent_by_id(d, "Weapon_Bow_Wood") if ein(e)] and jresolved(kC),
                "FIX2-D1 ... after a restart the repair drops the aborted craft: ONE bow (the caller's), none IN the pool (%s; %s)" % (rrC, c.get(bowk)))

        # FIX2-D2 (data critic 2): the change put back after a double save failure is fixed FROM MEMORY on the next action, and the older
        # saved step stays in the journal - a crash that later rolls the inventory back past it still finds its evidence
        R2 = W.player("00000000-0000-0000-0000-000000000f07", "Ret")
        kR = str(R2.u)
        setc(R2.sto, 0, stack("Weapon_Sword_Mithril", 1, gdoc("rare", 8)))
        setc(R2.sto, 1, stack("Weapon_Sword_Iron", 1, gdoc("rare", 9)))
        r00 = run(R2, 6, 0, "2:1")      # the files exist; the engine saves the player after it
        restart()
        Jr.delete(kR)
        engR = W.snap(R2)
        baseR, _ = census(R2)
        rA = run(R2, 6, 0, "2:0")
        kr0 = int(Tx.KEPT_RETRIES)
        Store.FAIL_NEXT = 2
        setc(R2.sto, 2, stack("Armor_Iron_Head", 1))
        rB = run(R2, 6, 0, "2:2")
        Store.FAIL_NEXT = 0
        keptB = bool(Tx.KEPT.containsKey(kR))
        rC = run(R2, 5)
        jR = os.path.join(Wd, "requip", kR, "journal.json")
        jdR = json.load(open(jR)) if os.path.isfile(jR) else {}
        K.check(r00.startswith("+") and rA.startswith("+") and rB.startswith("-Could not save Requip - everything was put back; Requip checks") and keptB and not Tx.KEPT.containsKey(kR)
                and int(Tx.KEPT_RETRIES) == kr0 + 1 and jdR.get("stage") == "saved" and len(jdR.get("steps", [])) == 1 and bool(Jr.PENDING.containsKey(kR)) and getc(R2.sto, 2) is not None,
                "FIX2-D2 the next action rewrites the files from memory; the journal keeps the older SAVED step (pending) (%s / %s / %s / %s)" % (rA, rB, rC, jdR.get("stage")))
        R2.sto.removeItemStackFromSlot(JShort(2), False)
        W.restore(R2, engR)
        restart()
        rD = run(R2, 5)
        c, d = census(R2)
        K.check(c == baseR and not once(R2, d) and len([e for e in ent_by_id(d, "Weapon_Sword_Mithril") if ein(e)]) == 0,
                "FIX2-D2 ... a crash that rolls the inventory back past that step: its evidence is still there - the Mithril sword is on you, NOT also in the pool (%s)" % rD)
        Jr.delete(kR)

        # FIX2-D3 (data critic 3): an unreadable journal no longer blocks for good: every change says why; /requipadmin repair moves it aside
        Ux = W.player("00000000-0000-0000-0000-000000000f08", "Unr")
        kU = str(Ux.u)
        setc(Ux.sto, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 10)))
        setc(Ux.sto, 1, stack("Weapon_Sword_Iron", 1, gdoc("rare", 11)))
        run(Ux, 6, 0, "2:0")
        Jr.delete(kU)
        jU = os.path.join(Wd, "requip", kU, "journal.json")
        open(jU, "w").write("{ broken")
        restart()
        rU = run(Ux, 6, 0, "2:1")
        heldU = getc(Ux.sto, 1) is not None
        P("WdRepairTask")(Ux.u, 0, True, None).run()
        aside = [f for f in os.listdir(os.path.join(Wd, "requip", kU)) if f.startswith("journal-unreadable-")]
        goneU = not os.path.isfile(jU)
        rU2 = run(Ux, 6, 0, "2:1")
        K.check(rU.startswith("-The Requip journal of this profile cannot be read") and heldU and len(aside) == 1 and goneU and rU2.startswith("+"),
                "FIX2-D3 an unreadable journal: the change says why, /requipadmin repair moves the file aside, then Requip works again (%s / %s / %s)" % (rU, aside, rU2))

        # FIX2-E1 (engine critic 1): idle profiles leave the memory cache (never one with a journal / pending / kept / unsaved marks)
        Jr.delete(kU)
        Store.get(kF1, F1.u)
        Store.get(kC, Cr.u)
        Jr.PENDING.put(kC, JLong(int(time.time() * 1000)))
        hs = JClass("java.util.HashSet")()
        hs.add(kU)
        Store.get(kU, Ux.u)
        ev0 = int(P("WdTimer").EVICTED)
        nE = int(P("WdTimer").evict(hs))
        K.check(nE >= 1 and not Store.CACHE.containsKey(kF1) and Store.CACHE.containsKey(kC) and Store.CACHE.containsKey(kU) and int(P("WdTimer").EVICTED) == ev0 + nE,
                "FIX2-E1 the timer drops idle profiles from memory; the online one and one with a pending journal stay (%d evicted)" % nE)
        Jr.PENDING.remove(kC)
        cE, dE = census(F1)
        K.check(not Store.get(kF1, F1.u).bad and not once(F1, dE), "FIX2-E1 ... an evicted profile reloads from its files on demand")

        # FIX2-E2 (engine critic 2): wardrobe:fn:canDeposit never answers "accepted" (null) on a failure or a malformed call
        rq0 = Store.RQ
        Store.RQ = None
        try:
            ce = Fn(1).apply(JArray(JObject)([UUID_.fromString("00000000-0000-0000-0000-000000000f09"), JString("Weapon_Sword_Iron"), JInt(1)]))
        finally:
            Store.RQ = rq0
        cm = Fn(1).apply(JArray(JObject)([UUID_.fromString("00000000-0000-0000-0000-000000000f09")]))
        cm2 = Fn(1).apply(JString("x"))
        cok = fa(1, Q.u, "Weapon_Sword_Iron", JInt(1))
        K.check(str(ce) == "Requip error - try again" and str(cm) == "not storable" and str(cm2) == "not storable" and cok is None,
                "FIX2-E2 canDeposit: a failure says 'Requip error', a malformed call 'not storable', a real accept stays null (%s / %s / %s / %s)" % (ce, cm, cm2, cok))
        Store.CACHE.remove("00000000-0000-0000-0000-000000000f09")

        # FIX2-E3 (engine critic 3): the start only lists folders; the full pool-file read runs once in the background
        sh = list(Store.scanAll(False))
        P("WdScan")().run()
        dp = list(P("WdScan").LAST)
        K.check(sh[3] == -1 and dp[3] > 0 and dp[0] == sh[0] and dp[2] == sh[2], "FIX2-E3 scanAll(false) parses no pool file; WdScan reads them all (%s / %s)" % (sh, dp))

        # FIX2-F2 (fidelity critic 2): the pick op takes a bag block by id (no block held)
        pr1 = run(Pk, 10, 0, "5|pocket:Rock_Stone")
        pr2 = run(Pk, 10, 0, "5|pocket:Weapon_Sword_Iron")
        pr3 = run(Pk, 10, 0, "0|pocket:Rock_Stone")
        K.check(pr1.startswith("+Loadout 1: Hotbar 2 fills with Rock_Stone") and pr2.startswith("-That is not a block") and pr3.startswith("-Pocket blocks are for hotbar slots only"),
                "FIX2-F2 pick 'pocket:<id>': a block by id, never a sword, never an armor slot (%s / %s / %s)" % (pr1, pr2, pr3))




    except Exception as ex:
        import traceback
        traceback.print_exc()
        K.check(False, "X crashed: %s" % ex)
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
    # setup()'s order: config load, the store paths, auto-store file, the start scan, the kit, the bridge functions
    P("WdCfg").load(Paths.get(home))
    root = Paths.get(home).resolve("Skyy_SkyyWardrobe")
    P("WdStore").ROOT = root
    P("WdStore").DIR01 = root.resolve("loadouts")
    P("WdStore").RQ = root.resolve("requip")
    P("WdStore").LOGF = root.resolve("requip.log")
    P("WdAuto").load(P("WdStore").RQ.resolve("autostore.json"))
    sc = list(P("WdStore").scanAll(True))
    P("CfgPub").start(Paths.get(home), HL.get("SkyyWardrobeLive"))
    P("WdLog").bridge().put("wardrobe:fn:open", P("WdFn")(0))
    n01 = len([f for f in os.listdir(os.path.join(home, "Skyy_SkyyWardrobe", "loadouts")) if f.endswith(".json") and not f.endswith(".journal.json")]) if os.path.isdir(os.path.join(home, "Skyy_SkyyWardrobe", "loadouts")) else 0
    if step in ("1", "2"):
        K.check(sc[0] == 0 and sc[1] == 0 and sc[4] == n01 and int(P("WdCfg").FREE) == 4, "D %s: no Requip profiles yet, %d 0.1 wardrobes waiting (%s)" % (step, n01, sc))
    else:
        # step 3: the live 0.1 file(s) migrate on this COPY (no journal: file -> file, no inventory needed)
        done = []
        for f in sorted(os.listdir(os.path.join(home, "Skyy_SkyyWardrobe", "loadouts"))):
            if not f.endswith(".json") or f.endswith(".journal.json"):
                continue
            k = f[:-5]
            before = open(os.path.join(home, "Skyy_SkyyWardrobe", "loadouts", f), "rb").read()
            d = P("WdStore").get(k, None)
            r = P("WdMig").run(d, None, False)
            d2 = P("WdStore").load(k, "")
            hist = os.path.join(home, "Skyy_SkyyWardrobe", "requip", k, "from01", f)
            K.check(d.mig == 0 and not d.bad and d2.migrated is not None and os.path.isfile(hist) and open(hist, "rb").read() == before
                    and open(os.path.join(home, "Skyy_SkyyWardrobe", "loadouts", f), "rb").read() == before,
                    "D3 the live 0.1 file %s migrated on the COPY: run-once marker, History snapshot = its bytes, the 0.1 file untouched (%s; %s)" % (f, r, d2.migrated))
            done.append((k, int(d2.ask01), d2.count(0) + d2.count(1)))
        K.notes.append("D3 migrated live copies: %s" % done)
    P("CfgPub").shutdown()
    P("WdJournal").dropAll()
    K.save()


# ====================================================================================================== P / B / AA / C
def run_perm(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fld = AC.class_.getDeclaredField("permissionGroups")
    fld.setAccessible(True)
    for cn in ("WdAdminCmd", "WdAdminArg1Cmd", "WdAdminArg2Cmd", "WdAdminArg3Cmd"):
        c = JClass(PKG + cn)()
        perm, groups = c.getPermission(), fld.get(c)
        K.check(perm is not None and NODE in str(perm), "P. %s requires %s (%s)" % (cn, NODE, perm))
        K.check(groups is not None and len(groups) == 0, "P. %s permission groups empty" % cn)
        if cn == "WdAdminCmd":
            rec = c.getPermissionGroupsRecursive()
            leak = [str(k) for k in rec.keySet() if rec.get(k) is not None and any(NODE in str(x) for x in rec.get(k))]
            K.check(not leak and str(c.getName()) == "requipadmin" and sorted(str(a) for a in c.getAliases()) == ["wardrobeadmin"],
                    "P. /requipadmin (alias /wardrobeadmin) gives %s to no group (leak %s)" % (NODE, leak))
    for cn in ("WdCmd", "WdArg1Cmd", "WdArg2Cmd", "WdArg3Cmd"):
        c = JClass(PKG + cn)()
        K.check(list(fld.get(c)) == ["hytale:Adventurer"] and (c.getPermission() is None or NODE not in str(c.getPermission())), "P. %s = hytale:Adventurer" % cn)
    m = JClass(PKG + "WdCmd")()
    K.check(str(m.getName()) == "requip" and sorted(str(a) for a in m.getAliases()) == ["loadout", "loadouts", "rq", "wardrobe", "wardrobes", "wd"],
            "P. /requip aliases rq, wardrobe, wd, loadout, loadouts, wardrobes (%s)" % sorted(str(a) for a in m.getAliases()))
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
    want = ["load", "load", "scanAll", "start"] + ["put"] * 9 + ["registerCommand", "registerCommand", "registerGlobal", "registerGlobal", "schedule", "scheduleWithFixedDelay"]
    seq = [n for n in names if n in set(want)]
    K.check(seq == want, "B setup() order: config, autostore, the folder scan, kit, 8 bridge fns + stampKey, 2 commands, 2 events, the background file check (FIX2-E3), the timer (%s)" % seq)
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
    run_ = bytecode_calls(CPl, IP, PKG + "WdTx", "run")
    jb = next(i for i, l in enumerate(run_) if "WdJournal.begin" in l)
    dm = next(i for i, l in enumerate(run_) if "WdTx.doMove" in l)
    sv = next(i for i, l in enumerate(run_) if "WdStore.save" in l)
    K.check(jb < dm < sv, "B the journal is written before the first move, the files after the moves")
    # FIX-S1: after a failed save + rollback the files are rewritten (a 2nd save) BEFORE the journal step may be dropped (abort)
    sv2 = [i for i, l in enumerate(run_) if "WdStore.save" in l]
    ab = [i for i, l in enumerate(run_) if "WdJournal.abort" in l]
    K.check(len(sv2) >= 2 and ab and sv2[1] < ab[-1], "FIX-S1 bytecode: WdTx.run saves again from the restored memory before the journal's abort")
    # FIX-E1: the pocket give-back (sacks:fn:deposit with the hotbar slot) runs BEFORE the Equip transaction
    ops_ = bytecode_calls(CPl, IP, PKG + "WdOps", "run")
    gb = [i for i, l in enumerate(ops_) if "WdOps.giveBack" in l]
    tr = [i for i, l in enumerate(ops_) if "WdTx.run" in l]
    K.check(gb and tr and gb[0] < tr[0], "FIX-E1 bytecode: giveBack before the Equip transaction")

    def catches(cls, meth):
        out_ = []
        for m in CPl.get(cls).getDeclaredMethods():
            if str(m.getName()) != meth:
                continue
            ca = m.getMethodInfo().getCodeAttribute()
            et, cp = ca.getExceptionTable(), m.getMethodInfo().getConstPool()
            for i in range(int(et.size())):
                ct = int(et.catchType(i))
                if ct:
                    out_.append(str(cp.getClassInfo(ct)))
        return out_
    K.check("java.util.ConcurrentModificationException" in catches(PKG + "WdFn", "canDeposit") and "java.util.ConcurrentModificationException" in catches(PKG + "WdCmds", "admin"),
            "FIX-E2 bytecode: wardrobe:fn:canDeposit and /requipadmin info answer 'busy' when a read meets a change on the player's world thread")
    wm = [l for l in allcode if "ItemStack.withMetadata" in l]
    K.check(wm and all("(Ljava/lang/String;Lorg/bson/BsonValue;)" in l or "(Lorg/bson/BsonDocument;)" in l for l in wm), "B the stamp is written with withMetadata(key, value) only")
    # spec F2 desk check: SkyyGear's own document writes keep foreign keys (GearView.apply / GearData.put use withMetadata(key, value))
    if GEAR and os.path.isfile(GEAR):
        CPl.appendClassPath(GEAR)
        gv = bytecode_calls(CPl, IP, "com.skyy.gear.GearView", "apply")
        gp = bytecode_calls(CPl, IP, "com.skyy.gear.GearData", "put")
        bad = [l for l in gv + gp if ("ItemStack.withMetadata((Lorg/bson/BsonDocument;)" in l) or ("new #" in l and "ItemStack" in l and "Class com.hypixel.hytale.server.core.inventory.ItemStack" in l)]
        K.check(gv and gp and not bad, "B F2 (%s): GearView.apply / GearData.put never build a new ItemStack or replace the whole metadata - the stamp survives reforge / level-up / identify (%s)" % (os.path.basename(GEAR), bad[:3]))
    else:
        K.notes.append("B F2: no SkyyGear jar found - the SkyyGear desk check was skipped")
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


def run_compare(out):
    """C: class compare 0.1 vs 0.2 (javassist reads both jars; nothing is loaded)"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    res = {}
    for tag, jar in (("old", OLD), ("new", JAR)):
        cp = JClass("javassist.ClassPool")(False)
        cp.appendSystemPath()
        cp.appendClassPath(B.SERVER_JAR)
        cp.appendClassPath(jar)
        m = {}
        for n in zipfile.ZipFile(jar).namelist():
            if not n.endswith(".class"):
                continue
            cn = n[:-6].replace("/", ".")
            cc = cp.get(cn)
            m[cn] = sorted("%s%s" % (x.getName(), x.getSignature()) for x in cc.getDeclaredMethods()) + sorted("F:%s" % f.getName() for f in cc.getDeclaredFields())
        res[tag] = m
    old, new = res["old"], res["new"]
    kept = sorted(set(old) & set(new))
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = {c.rsplit(".", 1)[-1]: {"-": len(set(old[c]) - set(new[c])), "+": len(set(new[c]) - set(old[c]))} for c in kept if old[c] != new[c]}
    K.check(removed == [PKG + "WdOpenFn"], "C the only 0.1 class gone is WdOpenFn (replaced by WdFn, mode 0 = the same wardrobe:fn:open contract) (%s)" % removed)
    K.check(set(c.rsplit(".", 1)[-1] for c in added) == {"WdClass", "WdInv", "Wd01Load", "Wd01Data", "Wd01", "WdEntry", "WdMove", "WdAuto", "WdMig", "WdSort", "WdAutoTask", "WdFn", "WdScan"},
            "C added classes (%s)" % [c.rsplit(".", 1)[-1] for c in added])
    K.notes.append("C kept %d classes, %d changed: %s" % (len(kept), len(changed), changed))
    K.save()


# ====================================================================================================== parent driver
def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--old", OLD, "--live", LIVE,
                                                                                   "--gear", GEAR or "-", "--seed", str(SEED), "--fuzz", arg("--fuzz", "260"),
                                                                                   "--fuzz-seeds", ",".join(str(s_) for s_ in FUZZ_SEEDS),
                                                                                   "--collide-seeds", ",".join(str(s_) for s_ in COLLIDE_SEEDS) or "-",
                                                                                   "--collide-ops", arg("--collide-ops", "400")], env=env)


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
    global GEAR
    if GEAR == "-":
        GEAR = ""
    for flag, fn in (("--mkfake", lambda: run_mkfake(FAKE_DIR)), ("--mk01", lambda: run_mk01(arg("--out"))), ("--x", lambda: run_x(arg("--out"))),
                     ("--perm", lambda: run_perm(arg("--out"))), ("--bc", lambda: run_bytecode(arg("--out"))), ("--audit", lambda: run_audit(arg("--out"))),
                     ("--cmp", lambda: run_compare(arg("--out")))):
        if flag in sys.argv:
            fn()
            return
    if "--live-step" in sys.argv:
        run_live(arg("--live-step"), arg("--out"))
        return
    only = arg("--only")
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
    child(env, "--mkfake")
    steps = [("--mk01", "M01"), ("--x", "X"), ("--perm", "P"), ("--bc", "B"), ("--cmp", "C")]
    for flag, label in steps:
        if only and label not in only.split(","):
            continue
        o = os.path.join(SCRATCH, "%s.json" % label)
        child(env, flag, "--out", o)
        take(o, label)
    if not only or "AA" in only.split(","):
        o = os.path.join(SCRATCH, "AA.json")
        child(env, "--audit", "--out", o)
        if os.path.isfile(o):
            a = json.load(open(o))
            check(not a["refused"] and a["refs"] > 500 and a["classes"] == len(CLASSES), "AA every engine member referenced is accessible (%d refs, %d classes): %s" % (a["refs"], a["classes"], a["refused"][:5]))
            check(len(a["control"]) >= 1, "AA the control class (a protected engine call) IS refused")
        else:
            check(False, "AA wrote no result")
    # ---- D: start twice on a scratch COPY of the live world mods folder, then the live 0.1 file migrates on that copy
    if not only or "D" in only.split(","):
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
            exp_added = [] if "Skyy_SkyyWardrobe/config.properties" in before else ["Skyy_SkyyWardrobe/config.properties"]
            check(added == exp_added and not changed, "D start 1 writes nothing (the 0.1 config + files stay byte for byte) (added %s, changed %s)" % (added, changed))
            o = os.path.join(SCRATCH, "D2.json")
            child(env, "--live-step", "2", "--out", o)
            take(o, "D2")
            after = tree_hash(home)
            check(after == mid, "D start 2 writes nothing (%s)" % sorted(k for k in set(after) | set(mid) if after.get(k) != mid.get(k)))
            o = os.path.join(SCRATCH, "D3.json")
            child(env, "--live-step", "3", "--out", o)
            take(o, "D3")
            after3 = tree_hash(home)
            ch3 = sorted(k for k in before if after3.get(k) != before[k])
            add3 = sorted(set(after3) - set(before))
            check(not ch3 and add3 and all(k.startswith("Skyy_SkyyWardrobe/requip/") or k == "Skyy_SkyyWardrobe/requip.log" for k in add3),
                  "D3 the migration only ADDED files under Skyy_SkyyWardrobe/requip/ (+ the requip.log MIGRATE line) (changed %s, added %s)" % (ch3, add3))
            check(not os.path.exists(os.path.join(LIVE, "Skyy_SkyyWardrobe", "requip")), "D nothing was written into the live folder itself")
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


