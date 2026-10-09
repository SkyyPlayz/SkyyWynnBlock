"""Harness for SkyyExploration 0.2.5 (UNCLAIMED LUGGAGE: one claim, VANISHES AT ONCE with a poof; SACK looks instead of chests; the
one-time luggage.shareSeconds 20 -> 0 update ExpLgMig - Skyy 2026-10-09). Derived from the 0.2.4 harness: every 0.2.4 path still runs;
0.2.5 adds the vanish checks (X6 / X9 / X10), the poof (LgEng.poof real + seam), the sack looks + claim hint (V), the ExpLgMig text step
and migrate() on files (X16), the class compare 0.2.4 -> 0.2.5 (C) and the update on the live copy (D). Build first:
python tools/exploration_0_2_5_patch.py && python SkyyExploration/build_skyyexploration_0.2.5.py

    python SkyyExploration/test_skyyexploration_0.2.5.py [--jar <SkyyExploration-0.2.5.jar>] [--dir <scratch>] [--keep]

(The 0.2.4 description below is kept; where it says chest looks / shared claims, 0.2.5 above wins.)

Children (fresh JVMs, the game's JRE, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch):
  F  stand-ins compiled with javassist (FakeStore / FakeBuffer / FakeChunk ECS parts - the buffer records + cancels the engine's drop
     event, a PlayerRef that records chat lines, an InteractionContext with a target block, an Inventory with a given combined container)
  A  every class of the jar loads + verifies (-Xverify:all)
  V  THE ENGINE ASSET VALIDATORS: the vanilla pack store by store (every codec validator), the "SkyyLuggage" page registered as setup()
     does (OpenCustomUIInteraction.PAGE_CODEC), then THE JAR as its own pack: no failed store / SEVERE / WARNING about our files; the 4
     luggage blocks in the Item + BlockType stores, toPacket() works, no block entity (no container), Variant, DropList Empty, the Use
     interaction = OpenCustomUI SkyyLuggage; every model / texture / icon resolves; no one-entry Parallel; NEGATIVE CONTROLS (an unknown
     page id, a missing model) are refused
  X  EVERY NEW PATH EXECUTED (-Xverify:all, the real stores from V; the engine block calls through the LgApi seam = a stand-in world):
     LgSite (parse / line / claim / claimedAt), LgReg (load / save / bad lines / save refused / at / count), LgCore (ground / soft / tiers /
     zones / caps / column / spawn write-ahead / unplace / sweep / respawn / spawnNear / second / use EVERY branch / loot: coins, bags,
     the REAL vanilla Zone<N>_Encounters_Tier<T> roll, XP, overflow -> the engine drop / statsText / flushAll / broken), LgUse.tryCreate,
     LgBreakSys / LgDamageSys on real BlockTypes, LgEng with no seam (no chunk, the mob:fn:levelAt bridge), ExpCfg rows / check / clamps,
     plugin setup / shutdown / ExpTick wiring (bytecode). THE PLAYER-CHEST LOCK: the stand-in world records every clear / place - only
     ever on Skyy_LootChest_T* blocks with a registry line
  C  CLASS COMPARE 0.2.3 -> 0.2.4 (javassist members): the 8 new classes, the listed changes, nothing else
  D  START TWICE on a scratch COPY of the live Skyy_SkyyExploration folder (setup()'s order: ExpCfg.load, ChestReg.loadAll,
     SpotReg.loadAll): every file byte-identical, no luggage folder until luggage exists, the luggage rows read their defaults
  AA THE ENGINE-ACCESS AUDIT (MethodHandles.privateLookupIn every referencing class)
Scratch: tools/dev/scratch/lug025/explore (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, time, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.2.5"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyExploration-0.2.4.jar")
SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "lug025", "explore")))
FAKE_DIR = os.path.join(SCRATCH, "fake")
FAKE_PKG = "skyyexptest"
PKG = "com.skyy.explore."
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyExploration")
NEW_CLASSES = ["ExpLgMig"]
LG_IDS = ["Skyy_LootChest_T%d" % t for t in (1, 2, 3, 4)]
FAILS, OKS = [], [0]


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

    def nullctor(name, sup):
        """a constructor calling the superclass's first constructor with null / 0 (never run: the harness allocates with Unsafe)"""
        c0 = cp.get(sup).getDeclaredConstructors()[0]
        args = []
        for t in c0.getParameterTypes():
            n = str(t.getName())
            args.append({"int": "0", "short": "(short) 0", "byte": "(byte) 0", "long": "0L", "float": "0.0f", "double": "0.0",
                         "boolean": "false", "char": "'a'"}.get(n, "(%s) null" % n.replace("$", ".")))
        return "public %s() { super(%s); }" % (name, ", ".join(args))

    def mk(name, sup, fields=(), meths=(), ctor=True):
        c = cp.makeClass(P + "." + name)
        c.setSuperclass(cp.get(sup))
        for f in fields:
            c.addField(CtField.make(f, c))
        if ctor:
            c.addConstructor(CtNewConstructor.make(nullctor(name, sup), c))
        for m in meths:
            c.addMethod(CtNewMethod.make(m, c))
        c.writeFile(out_dir)
    mk("FakeStore", "com.hypixel.hytale.component.Store", ["public java.util.Map comps;", "public java.lang.Object ext;"],
       ["public %s getComponent(%s r, %s t) { if (this.comps == null || r == null) return null; java.util.Map m = (java.util.Map) this.comps.get(r); if (m == null) return null; return (%s) m.get(t); }" % (CMP, RF, CT, CMP),
        "public java.lang.Object getExternalData() { return this.ext; }"])
    mk("FakeBuffer", "com.hypixel.hytale.component.CommandBuffer",
       ["public %s.FakeStore st;" % P, "public java.util.ArrayList events;"],
       ["public %s getComponent(%s r, %s t) { if (this.st == null) return null; return this.st.getComponent(r, t); }" % (CMP, RF, CT),
        "public java.lang.Object getExternalData() { return this.st == null ? null : this.st.ext; }",
        # the engine's drop path (ItemUtils.throwItem) first fires DropItemEvent$Drop through the accessor: recorded and cancelled here
        "public void invoke(%s r, com.hypixel.hytale.component.system.EcsEvent e) { if (this.events == null) this.events = new java.util.ArrayList(); this.events.add(e); if (e instanceof com.hypixel.hytale.component.system.CancellableEcsEvent) ((com.hypixel.hytale.component.system.CancellableEcsEvent) e).setCancelled(true); }" % RF])
    mk("FakeChunk", "com.hypixel.hytale.component.ArchetypeChunk", ["public java.util.Map comps;"],
       ["public %s getComponent(int i, %s t) { if (this.comps == null) return null; return (%s) this.comps.get(t); }" % (CMP, CT, CMP)])
    mk("FakePR", "com.hypixel.hytale.server.core.universe.PlayerRef", ["public java.util.ArrayList said;"],
       ["public void sendMessage(com.hypixel.hytale.server.core.Message m) { if (this.said == null) this.said = new java.util.ArrayList(); this.said.add(m == null ? \"null\" : m.getRawText()); }"])
    # InteractionContext has only private constructors: the harness allocates a real one and gives it this meta store
    # (InteractionContext.getTargetBlock = metaStore.getIfPresentMetaObject(Interaction.TARGET_BLOCK))
    mk("FakeMeta", "com.hypixel.hytale.server.core.meta.DynamicMetaStore", ["public com.hypixel.hytale.protocol.BlockPosition bp;", "public boolean boom;"],
       ["public java.lang.Object getIfPresentMetaObject(com.hypixel.hytale.server.core.meta.MetaKey k) { if (this.boom) throw new java.lang.IllegalStateException(\"test: no target\"); if (k == com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction.TARGET_BLOCK) return this.bp; return null; }"])
    mk("FakeInv", "com.hypixel.hytale.server.core.inventory.Inventory", ["public com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer comb;"],
       ["public com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer getCombinedStorageHotbarBackpack() { return this.comb; }"], ctor=False)
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
    fu.writeFile(out_dir)
    print("F. stand-ins written to", out_dir)


# ====================================================================================================== A
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
def gear_harness():
    """the SkyyGear 0.2.11 harness's engine_boot (vanilla pack store by store, then a jar as its own pack), pointed at this jar"""
    sp = importlib.util.spec_from_file_location("skyygear_h211", os.path.join(ROOT, "SkyyGear", "test_skyygear_0.2.11.py"))
    G = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(G)
    G.SCRATCH, G.JAR, G.ASSETS, G.VERSION = SCRATCH, JAR, ASSETS, VERSION
    return G


def run_engine(out):
    from jpype import JClass, JArray, JInt, JLong, JShort, JString, JDouble, JImplements, JOverride, JObject, JBoolean, JFloat
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=True, big=True)
    G = gear_harness()
    OCU = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction")
    LgUse = JClass(PKG + "LgUse")
    BC = JClass("com.hypixel.hytale.codec.builder.BuilderCodec")

    @JImplements("java.util.function.Supplier")
    class NewUse:
        @JOverride
        def get(self): return LgUse()
    # what setup() does through registerCustomPageSupplier (PluginBase.getCodecRegistry(PAGE_CODEC).register(id, supplier class, codec))
    OCU.PAGE_CODEC.register("SkyyLuggage", LgUse.class_, BC.builder(LgUse.class_, NewUse()).build())
    BBX = JClass("com.hypixel.hytale.server.core.asset.type.blockhitbox.BlockBoundingBoxes")
    _orig_loadpack = [None]
    E = G.engine_boot(K)
    us, jf, ITEM = E["us"], E["jf"], E["ITEM"]
    jz = zipfile.ZipFile(JAR)
    names = set(jz.namelist())
    # ============================================================================ V
    full = BBX.getAssetMap().getAsset(BBX.DEFAULT)
    K.notes.append("V: the bare JVM's BlockBoundingBoxes store has the runtime default '%s': %s (vanilla's own blocks hit the gap %d times)" % (
        BBX.DEFAULT, full is not None, sum(1 for r in E["vrec"] if ("Asset '%s' of type" % BBX.DEFAULT) in r[1] and "BlockBoundingBoxes" in r[1])))
    if full is None:
        # add it as the game has it (BlockBoundingBoxes.getUnitBoxFor(DEFAULT)), then load the jar again as a second pack
        BBX.getAssetStore().loadAssets("Hytale:Hytale", JClass("java.util.List").of(BBX.getUnitBoxFor(BBX.DEFAULT)))
        K.check(BBX.getAssetMap().getAsset(BBX.DEFAULT) is not None, "V: the runtime default hitbox '%s' added to the bare JVM store" % BBX.DEFAULT)
        f2, r2 = E["loadpack"](JAR, "Skyy:%s SkyyExploration again" % VERSION, False)
        E["fail"], E["rec"] = f2, r2
    ours = [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING") and ("LootChest" in r[1] or "SkyyExploration" in r[1] or "SkyyLuggage" in r[1])]
    for r in ours[:20]:
        print("   V ours:", r[0], r[1][:300])
    K.check(not ours and set(E["fail"]) <= set(E["vfail"]), "V: the jar as its own pack: no SEVERE / WARNING about our files %s, failed "
            "stores %s are vanilla's too %s" % ([r[1][:120] for r in ours[:3]], E["fail"], E["vfail"]))
    BT = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    bad, rows = [], []
    for bid in LG_IDS:
        it, bt = ITEM.getAssetMap().getAsset(bid), BT.getAssetMap().getAsset(bid)
        if it is None or bt is None:
            bad.append((bid, "missing item %s block %s" % (it is None, bt is None)))
            continue
        try:
            it.toPacket()
            bt.toPacket()
            rows.append((bid, str(bt.getId()), bt.getBlockEntity() is None, int(it.getMaxStack())))
            if bt.getBlockEntity() is not None or int(it.getMaxStack()) != 1:
                bad.append((bid, "a block entity / container or MaxStack != 1"))
        except Exception as e:
            bad.append((bid, str(e)[:200]))
    K.check(not bad and len(rows) == 4, "V: the 4 luggage blocks are in the Item + BlockType stores, toPacket() works, NO block entity "
            "(no container: nothing can ever be stored in one), MaxStack 1: %s %s" % (bad, rows))
    with zipfile.ZipFile(ASSETS) as az:
        anames = set(az.namelist())
    miss, shape = [], []
    for bid in LG_IDS:
        d = json.loads(jz.read("Server/Item/Items/SkyyExploration/%s.json" % bid))
        b = d["BlockType"]
        for pth in [b["CustomModel"], d["Icon"]] + [t["Texture"] for t in b["CustomModelTexture"]]:
            if "Common/" + pth not in anames and "Common/" + pth not in names:
                miss.append(pth)
        use = b["Interactions"]["Use"]["Interactions"]
        if not (d.get("Variant") is True and b["Gathering"]["Breaking"]["DropList"] == "Empty" and len(use) == 1
                and use[0]["Type"] == "OpenCustomUI" and use[0]["Page"]["Id"] == "SkyyLuggage" and "Recipe" not in d and "State" not in b
                and "BlockEntity" not in b):
            shape.append(bid)
    K.check(not miss and not shape, "V: every model / texture / icon resolves (vanilla sack looks by path) %s; Variant, DropList Empty, Use = "
            "OpenCustomUI SkyyLuggage, no recipe / state / block entity %s" % (miss, shape))
    # 0.2.5: SACKS, not chests - four different looks, the claim prompt, cloth sounds
    looks, hints = [], []
    for bid in LG_IDS:
        d = json.loads(jz.read("Server/Item/Items/SkyyExploration/%s.json" % bid))
        b = d["BlockType"]
        looks.append((b["CustomModel"], b["CustomModelTexture"][0]["Texture"], d["Icon"], b.get("HitboxType"), b.get("BlockSoundSetId"), b.get("Material")))
        hints.append(b.get("InteractionHint"))
    K.check(not any("Chest" in x for lk in looks for x in lk[:3] if x) and len(set(lk[1] for lk in looks)) == 4 and len(set(lk[2] for lk in looks)) == 4
            and [lk[0] for lk in looks] == ["Items/Tools/Feedbag/Feedbag.blockymodel"] * 2 + ["Blocks/Decorative_Sets/Ancient/Sack.blockymodel", "Items/Tools/Feedbag/Feedbag.blockymodel"]
            and all(lk[4] == "Cloth" and lk[5] == "Solid" for lk in looks),
            "V: 0.2.5 the four tiers are SACKS (no chest model / texture / icon), four different textures + icons, cloth sounds, still Solid: %s" % looks)
    lang = jz.read("Server/Languages/en-US/server.lang").decode("utf-8")
    with zipfile.ZipFile(ASSETS) as az:
        vlang = az.read("Server/Languages/en-US/server.lang").decode("utf-8-sig")
    vopen = [ln for ln in vlang.splitlines() if ln.startswith("interactionHints.open =")]
    K.check(hints == ["server.interactionHints.skyyLuggageClaim"] * 4 and "\ninteractionHints.skyyLuggageClaim = Press [{key}] to claim {name}\n" in "\n" + lang
            and vopen == ["interactionHints.open = Press [{key}] to open {name}"] and "interactionHints.skyyLuggageClaim" not in vlang
            and lang.count("Unclaimed Luggage (") == 4 and "straight into your inventory" in lang,
            "V: 0.2.5 the prompt 'Press [F] to claim Unclaimed Luggage (I)' - our own hint key in our server.lang, same placeholders as vanilla's "
            "interactionHints.open (%s), not a vanilla key: %s" % (vopen, hints))
    clash = [n for n in names if n.startswith("Server/") and n in anames and not n.endswith(".lang")]
    K.check(not clash, "V: no jar file shadows a vanilla file: %s" % clash)

    def one_par(o_):
        if isinstance(o_, dict):
            if o_.get("Type") == "Parallel" and len(o_.get("Interactions") or []) < 2:
                return True
            return any(one_par(v_) for v_ in o_.values())
        if isinstance(o_, list):
            return any(one_par(v_) for v_ in o_)
        return False
    onep = [n for n in names if n.endswith(".json") and one_par(json.loads(jz.read(n)))]
    K.check(not onep, "V: no one-entry Parallel in the jar: %s" % onep)
    src = json.loads(jz.read("Server/Item/Items/SkyyExploration/Skyy_LootChest_T2.json"))
    nopage = json.loads(json.dumps(src))
    nopage["BlockType"]["Interactions"]["Use"]["Interactions"][0]["Page"]["Id"] = "SkyyNoSuchPage"
    nomodel = json.loads(json.dumps(src))
    nomodel["BlockType"]["CustomModel"] = "Blocks/SkyyExpCtl_NoSuch.blockymodel"
    for i, (what, path, text, needle) in enumerate([
            ("an unknown OpenCustomUI page id", "Server/Item/Items/SkyyExpCtl/SkyyExpCtl_Page.json", json.dumps(nopage), "SkyyNoSuchPage"),
            ("a missing block model", "Server/Item/Items/SkyyExpCtl/SkyyExpCtl_Model.json", json.dumps(nomodel), "SkyyExpCtl_NoSuch")]):
        zp = os.path.join(SCRATCH, "v-ctl%d.jar" % i)
        with zipfile.ZipFile(zp, "w") as z:
            z.writestr(path, text)
        f_, r2 = E["loadpack"](zp, "Skyy:test ctl%d" % i, False)
        hit = [r for r in r2 if r[0] in ("SEVERE", "WARNING") and needle in r[1]]
        K.check(bool(hit), "V CONTROL: %s is refused by the engine validator: %s" % (what, [r[1][:150] for r in r2[:3]]))
    print("V. the jar as a pack: %d failed stores, %d records about our files; 4 luggage blocks; controls run" % (len(E["fail"]), len(ours)))

    # ============================================================================ X: set-up
    P = lambda n: JClass(PKG + n)
    Cfg, Site, Reg, Core, Eng, Api, Brk, Dmg, Store_, ChestReg, IO, State, Data = (
        P("ExpCfg"), P("LgSite"), P("LgReg"), P("LgCore"), P("LgEng"), P("LgApi"), P("LgBreakSys"), P("LgDamageSys"), P("ExpStore"),
        P("ChestReg"), P("ExpIO"), P("ExpState"), P("ExpData"))
    Paths, UUID, Props, IHM, CHM = (JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.util.Properties"),
                                    JClass("java.util.IdentityHashMap"), JClass("java.util.concurrent.ConcurrentHashMap"))
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    HL = JClass("com.hypixel.hytale.logger.HytaleLogger")
    Cfg.LOG = HL.get("SkyyExpHarness")
    LOGS0 = len(list(JClass("java.util.ArrayList")()))

    def ourlogs():
        return [m for (lv, m) in E["records"]() if "[SkyyExploration]" in m]
    Cfg.apply(Props())
    br = CHM()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    lgdir = os.path.join(SCRATCH, "x-data", "luggage")
    Reg.DIR = Paths.get(lgdir)
    Store_.DIR = Paths.get(os.path.join(SCRATCH, "x-data", "players"))
    WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")

    def world(name):
        w_ = us.allocateInstance(WLD.class_)
        jf(WLD, "name").set(w_, name)
        return w_
    NOW = [10 ** 12]

    def reset_world(wn):
        Reg.W.remove(str(ChestReg.wf(wn)))
        Core.SWEPT.clear()
    U1, U2, U3 = (UUID.fromString("00000000-0000-0000-0000-0000000e0001"), UUID.fromString("00000000-0000-0000-0000-0000000e0002"),
                  UUID.fromString("00000000-0000-0000-0000-0000000e0003"))

    # ---- the stand-in world (LgApi): ground at y 64 = Soil_Grass everywhere, air above; overrides per block; records place / clear
    class Wd:
        def __init__(self):
            self.blocks, self.heights, self.ents, self.fluids, self.unloaded = {}, {}, set(), set(), set()
            self.placed, self.cleared, self.violations, self.place_ok, self.on_place = [], [], [], True, None
            self.level = (12, 16)
            self.occ, self.sounds = set(), []
            self.poofs, self.clear_ok, self.boom_at, self.boom_n = [], True, None, 0
    WD = Wd()

    @JImplements(PKG + "LgApi")
    class Api_:
        @JOverride
        def blockId(self, w, x, y, z):
            if (int(x) >> 5, int(z) >> 5) in WD.unloaded:
                return None
            k = (int(x), int(y), int(z))
            if WD.boom_at == k:
                WD.boom_n += 1
                if WD.boom_n >= 2:
                    raise RuntimeError("test: the chunk went away")
            if k in WD.blocks:
                return WD.blocks[k]
            return "Soil_Grass" if int(y) <= WD.heights.get((int(x), int(z)), 64) else "Empty"

        @JOverride
        def height(self, w, x, z):
            if (int(x) >> 5, int(z) >> 5) in WD.unloaded:
                return JInt(-1)
            return JInt(WD.heights.get((int(x), int(z)), 64))

        @JOverride
        def hasEntity(self, w, x, y, z):
            return JBoolean((int(x), int(y), int(z)) in WD.ents)

        @JOverride
        def fluid(self, w, x, y, z):
            return JBoolean((int(x), int(y), int(z)) in WD.fluids)

        @JOverride
        def place(self, w, x, y, z, i):
            k = (int(x), int(y), int(z))
            if WD.on_place:
                WD.on_place(k)
            if not str(i).startswith("Skyy_LootChest_T"):
                WD.violations.append(("place", k, str(i)))
            if not WD.place_ok:
                return JBoolean(False)
            WD.blocks[k] = str(i)
            WD.placed.append((k, str(i)))
            return JBoolean(True)

        @JOverride
        def clear(self, w, x, y, z):
            k = (int(x), int(y), int(z))
            cur = WD.blocks.get(k, "Soil_Grass" if k[1] <= 64 else "Empty")
            if not cur.startswith("Skyy_LootChest_T"):
                WD.violations.append(("clear", k, cur))
            if not WD.clear_ok:
                return JBoolean(False)
            WD.blocks[k] = "Empty"
            WD.cleared.append(k)
            return JBoolean(True)

        @JOverride
        def occupied(self, w, x, y, z):
            return JBoolean((int(x), int(z)) in WD.occ)

        @JOverride
        def sound(self, w, x, y, z):
            WD.sounds.append((int(x), int(y), int(z)))

        @JOverride
        def poof(self, w, x, y, z):
            WD.poofs.append((int(x), int(y), int(z), WD.blocks.get((int(x), int(y), int(z)))))

        @JOverride
        def levelAt(self, wn, x, y, z):
            if WD.level is None:
                return None
            return JArray(JObject)([JInt(WD.level[0]), JInt(WD.level[1]), "default", "bands.default"])
    API = Api_()
    Eng.API = API

    def site(x, y, z, tier=1, lvl=12, state=0, placed=None, looted=0, near=None, who=""):
        s = Site()
        s.x, s.y, s.z, s.tier, s.lvl, s.state = x, y, z, tier, lvl, state
        s.placedAt = NOW[0] if placed is None else placed
        s.lootedAt, s.lastNear, s.nonce, s.who = looted, NOW[0] if near is None else near, 7, who
        return s

    def fileof(wn):
        p_ = os.path.join(lgdir, str(ChestReg.wf(wn)) + ".tsv")
        return open(p_, encoding="utf8").read() if os.path.isfile(p_) else None

    # ============================================================================ X1 LgSite
    s1 = Site.parse("10\t65\t-20\t3\t27\t1\t100\t200\t300\t-5\t%s:150" % U1)
    K.check(s1 is not None and [int(s1.x), int(s1.y), int(s1.z), int(s1.tier), int(s1.lvl), int(s1.state), int(s1.placedAt), int(s1.lootedAt),
                                int(s1.lastNear), int(s1.nonce)] == [10, 65, -20, 3, 27, 1, 100, 200, 300, -5] and int(s1.claimedAt(U1)) == 150
            and str(Site.parse(str(s1.line())).line()) == str(s1.line()), "X1: parse / line round trip, claimedAt reads the claim")
    badl = ["", "# a comment", "1\t2\t3", "1\t65\t3\t5\t10\t0\t0\t0\t0\t0", "1\t65\t3\t1\t10\t3\t0\t0\t0\t0", "1\t65\t3\t1\t0\t0\t0\t0\t0\t0",
            "1\t400\t3\t1\t10\t0\t0\t0\t0\t0", "x\t65\t3\t1\t10\t0\t0\t0\t0\t0", None]
    K.check(all(Site.parse(b) is None for b in badl) and Site.parse("1\t65\t3\t1\t10\t0\t0\t0\t0\t0") is not None,
            "X1: every malformed line (short, tier 5, state 3, level 0, y 400, not a number, comment, null) -> null; a 10-field line (no claims) ok")
    s2 = site(0, 65, 0)
    s2.claim(U1, JLong(1000), JLong(10 ** 9))
    s2.claim(U2, JLong(2000), JLong(10 ** 9))
    s2.claim(U1, JLong(5000), JLong(10 ** 9))
    w2 = str(s2.who)
    s2.claim(U3, JLong(10 ** 7), JLong(1000))
    for i in range(80):
        s2.claim(UUID(0, i + 1), JLong(2 * 10 ** 7 + i), JLong(10 ** 9))
    K.check(int(Site.parse(str(site(0, 65, 0, who=w2).line())).claimedAt(U1)) == 5000 and w2.count(str(U1)) == 1 and int(s2.claimedAt(U2)) == 0
            and len(str(s2.who).split(";")) <= 64 and int(s2.claimedAt(UUID(0, 80))) == 2 * 10 ** 7 + 79 and int(s2.claimedAt(U1)) == 0,
            "X1: claim: one entry per player (the newest), claims older than the cooldown dropped, at most 64 kept: %s" % w2)

    # ============================================================================ X2 LgReg
    shutil.rmtree(lgdir, ignore_errors=True)
    wn = "Default"
    W = world(wn)
    reset_world(wn)
    l0 = Reg.sites(wn)
    Reg.add(l0, site(5, 65, 5, tier=2, lvl=20))
    Reg.add(l0, site(50, 65, 5, state=2, looted=1))
    ok = bool(Reg.save(wn))
    txt = fileof(wn)
    reset_world(wn)
    l1 = Reg.sites(wn)
    K.check(ok and txt is not None and txt.startswith("# SkyyExploration Unclaimed Luggage") and int(l1.size()) == 2
            and Reg.at(l1, JInt(5), JInt(65), JInt(5)) is not None and int(Reg.at(l1, JInt(5), JInt(65), JInt(5)).tier) == 2
            and Reg.at(l1, JInt(6), JInt(65), JInt(5)) is None and int(Reg.count(l1, JInt(0))) == 1 and int(Reg.count(l1, JInt(2))) == 1
            and not os.path.exists(os.path.join(lgdir, str(ChestReg.wf(wn)) + ".tsv.tmp")),
            "X2: save (atomic: no .tmp left) -> a fresh load reads the same 2 sites; at() / count()")
    with open(os.path.join(lgdir, str(ChestReg.wf(wn)) + ".tsv"), "a", encoding="utf8") as f:
        f.write("garbage line\n1\t2\n")
    reset_world(wn)
    n_before = len(ourlogs())
    l2 = Reg.sites(wn)
    baks = [f_ for f_ in os.listdir(lgdir) if f_.endswith(".tsv.bad")]
    bak_txt = open(os.path.join(lgdir, baks[0]), encoding="utf8").read() if baks else ""
    K.check(int(l2.size()) == 2 and any("skipped 2 unreadable" in m for m in ourlogs()[n_before:]) and len(baks) == 1 and "garbage line" in bak_txt
            and bak_txt.startswith("# SkyyExploration Unclaimed Luggage"),
            "X2: unreadable lines skipped + warned, the rest kept; FIX: the whole file is copied to <world>-<ms>.tsv.bad BEFORE anything can "
            "overwrite it: %s" % baks)
    # FIX (critic 1): an unreadable file -> null (not cached), save() refuses, the file is never overwritten; it loads once readable
    wf_ = str(ChestReg.wf(wn))
    fpath = os.path.join(lgdir, wf_ + ".tsv")
    keep_txt = open(fpath, encoding="utf8").read()
    reset_world(wn)
    os.remove(fpath)
    os.makedirs(fpath)
    lr = Reg.sites(wn)
    cached = bool(Reg.W.containsKey(wf_))
    sv = bool(Reg.save(wn))
    still_dir = os.path.isdir(fpath)
    os.rmdir(fpath)
    open(fpath, "w", encoding="utf8").write(keep_txt)
    lr2 = Reg.sites(wn)
    K.check(lr is None and not cached and not sv and still_dir and lr2 is not None and int(lr2.size()) == 2
            and any("pauses (nothing placed, claimed or removed)" in m for m in ourlogs()),
            "X2: FIX an UNREADABLE registry -> sites() null and nothing cached, save() refuses (the file is never overwritten), a warning; "
            "readable again -> loads (2 sites)")
    blocker = os.path.join(SCRATCH, "x-data", "afile")
    open(blocker, "w").write("x")
    Reg.DIR = Paths.get(blocker)
    f0 = int(Reg.SAVE_FAILS.get())
    okf = bool(Reg.save(wn))
    Reg.DIR = Paths.get(lgdir)
    K.check(not okf and int(Reg.SAVE_FAILS.get()) == f0 + 1, "X2: a save that cannot be written returns false and counts SAVE FAILS")
    K.check(str(ChestReg.wf("we/ird:name")) != "we/ird:name" and "/" not in str(ChestReg.wf("we/ird:name")), "X2: world file names are safe")
    shutil.rmtree(lgdir, ignore_errors=True)
    reset_world(wn)

    # ============================================================================ X3 helpers
    G_YES = ("Soil_Grass", "Soil_Dirt", "Rock_Stone", "Soil_Sand_Red", "Rock_Stone_Mossy", "Soil_Grass_Full", "Soil_Gravel_Mossy", "Rock_Sandstone_Red")
    G_NO = ("Soil_Dirt_Tilled", "Soil_Pathway", "Wood_Oak_Planks", "Furniture_Crude_Chest_Small", None, "Rock_Stone_Brick", "Rock_Stone_Brick_Roof",
            "Rock_Stone_Cobble", "Rock_Stone_Cobble_Stairs", "Rock_Stone_Half", "Rock_Stone_Stairs", "Rock_Stone_Beam", "Rock_Stone_Brick_Wall",
            "Rock_Sandstone_Brick_Smooth_Half", "Soil_Dirt_Half", "Soil_Dirt_Stairs", "Soil_Gravel_Half", "Soil_Snow_Brick", "Soil_Sand_White_Path_Half",
            "Rock_Stone_Brick_Pillar_Base", "Rock_Stone_Stalactite_Small", "Rock_Stone_Cobble_Corner", "Rock_Stone_Brick_Decorative")
    K.check(all(bool(Core.ground(g)) for g in G_YES) and not any(bool(Core.ground(g)) for g in G_NO),
            "X3: FIX ground(): natural ground yes (prefix list); a player's BUILT shapes no (brick / cobble / roof / stairs / half / wall / "
            "beam / pillar / path...), tilled soil / planks / a chest / null no: %s" % [g for g in G_NO if bool(Core.ground(g))])
    S_YES = ("Empty", "Plant_Grass_Lush", "Plant_Grass_Lush_Tall", "Plant_Grass_Sharp_Wild", "Plant_Petals_Red", "Plant_Fern", "Plant_Fern_Winter",
             "Plant_Moss_Rug_Green", "Plant_Moss_Short_Blue")
    S_NO = ("Plant_Crop_Wheat_Block", "Plant_Sapling_Oak", "Plant_Seeds_Wheat", "Rock_Stone", None, "Plant_Flower_Common_Red", "Plant_Flower_Tall_Red",
            "Plant_Bush_Green", "Plant_Leaves_Oak", "Plant_Hay_Bundle", "Plant_Cactus_1", "Plant_Bramble_Winter", "Plant_Fern_Giant", "Plant_Fern_Tall",
            "Plant_Fern_Wet_Giant_Trunk", "Plant_Sunflower_Block", "Plant_Lavender_Block", "Plant_Coral_Bush_Red", "Plant_Vine_Rug")
    K.check(all(bool(Core.soft(g)) for g in S_YES) and not any(bool(Core.soft(g)) for g in S_NO),
            "X3: FIX soft(): air / wild grass / petals / short moss / small ferns yes; flowers / bushes / hedges (leaves) / hay / cactus / "
            "bramble / giant ferns / crops / saplings / seeds / stone / null no (a player's garden or farm is never replaced): %s %s"
            % ([g for g in S_YES if not bool(Core.soft(g))], [g for g in S_NO if bool(Core.soft(g))]))
    K.check([int(Core.tierOf(i)) for i in LG_IDS + ["Furniture_Crude_Chest_Small", None]] == [1, 2, 3, 4, 0, 0] and bool(Core.ours("Skyy_LootChest_T3"))
            and not bool(Core.ours("Furniture_Crude_Chest_Small")) and not bool(Core.ours(None)),
            "X3: tierOf / ours only for Skyy_LootChest_T*")
    K.check([int(Core.zoneOf(JInt(v))) for v in (1, 19, 20, 29, 30, 44, 45, 100)] == [1, 1, 2, 2, 3, 3, 4, 4], "X3: zoneOf boundaries")
    import collections
    for zone, exp in ((1, [60, 28, 10, 2]), (3, [60, 28, 20, 4])):
        c = collections.Counter(int(Core.pickTier(JInt(zone))) for _ in range(20000))
        tot = float(sum(exp))
        dev = max(abs(c[t + 1] / 20000.0 - exp[t] / tot) for t in range(4))
        K.check(dev < 0.015 and set(c) <= {1, 2, 3, 4}, "X3: pickTier zone %d follows %s (max deviation %.3f): %s" % (zone, exp, dev, dict(c)))
    Cfg.LG_TIER_W = JArray(JDouble)([0.0, 0.0, 0.0, 0.0])
    K.check(int(Core.pickTier(JInt(1))) == 1, "X3: all tier weights 0 -> tier I")
    Cfg.apply(Props())
    Core.HOUR.clear()
    Cfg.LG_CAP = 3
    t0 = NOW[0]
    for i in range(3):
        Core.capAdd(U1, JLong(t0 + i))
    c1 = bool(Core.capOk(U1, JLong(t0 + 10)))
    c2 = bool(Core.capOk(U1, JLong(t0 + 3600001)))
    Core.capAdd(U2, JLong(t0 + 10 ** 6))
    c3 = bool(Core.capOk(U2, JLong(t0)))
    Cfg.LG_CAP = 0
    c4 = bool(Core.capOk(U3, JLong(t0)))
    Cfg.apply(Props())
    Core.HOUR.clear()
    K.check(not c1 and c2 and c3 and not c4, "X3: capOk: 3 claims = the cap reached; an hour later free again; a future time (clock change) "
            "is dropped; cap 0 = never")

    # ============================================================================ X4 column
    l = Reg.sites(wn)

    def col(x, z, self_=None):
        return int(Core.column(W, l, JInt(x), JInt(z), self_))
    base = col(100, 100)
    WD.blocks[(101, 64, 100)] = "Soil_Dirt_Tilled"
    WD.blocks[(102, 65, 100)] = "Plant_Crop_Wheat"
    WD.blocks[(103, 65, 100)] = "Plant_Grass_Tall"
    WD.fluids.add((104, 65, 100))
    WD.heights[(105, 100)] = 317
    WD.unloaded.add((200 >> 5, 200 >> 5))
    WD.ents.add((300 + 8, 66, 300))
    WD.ents.add((400 + 9, 66, 400))
    r = [col(101, 100), col(102, 100), col(103, 100), col(104, 100), col(105, 100), col(200, 200), col(300, 300), col(400, 400)]
    WD.occ.add((600, 600))
    occ_col = col(600, 600)
    WD.occ.clear()
    K.check(occ_col == -1 and col(600, 600) == 65, "X4: FIX column(): a player standing on the column -> -1 (never a solid block into a player)")
    s_near = site(500, 65, 500)
    Reg.add(l, s_near)
    r2 = [col(520, 500), col(500, 500, s_near), col(533, 500)]
    Reg.remove(l, s_near)
    K.check(base == 65 and r == [-1, -1, 65, -1, -1, -1, -1, 65] and r2 == [-1, 65, 65],
            "X4: column(): ground 64 -> 65; tilled / a crop above / water / too high / an unloaded chunk / a block entity 8 away -> -1; a wild "
            "plant ok; a block entity 9 away ok; another luggage within 32 -> -1 (itself excluded, 33 away ok): %s %s %s" % (base, r, r2))

    # ============================================================================ X5 spawn (write-ahead) + unplace
    seen = {}

    def on_place(k):
        seen[k] = fileof(wn)
    WD.on_place = on_place
    sp = Core.spawn(W, wn, l, JInt(110), JInt(65), JInt(110), JInt(2), JInt(17), JLong(NOW[0]))
    pre = seen.get((110, 65, 110)) or ""
    K.check(sp is not None and "110\t65\t110\t2\t17\t0\t" in pre and WD.blocks.get((110, 65, 110)) == "Skyy_LootChest_T2" and int(Core.N[0]) >= 1,
            "X5: spawn(): the registry line is ON DISK before the block is placed (write-ahead), then the tier II block")
    K.check(WD.sounds and WD.sounds[-1] == (110, 65, 110), "X5: FIX spawn() plays the placement sound at the block (spec 5.2): %s" % WD.sounds[-1:])
    Reg.DIR = Paths.get(blocker)
    n_pl = len(WD.placed)
    sp2 = Core.spawn(W, wn, l, JInt(150), JInt(65), JInt(150), JInt(1), JInt(17), JLong(NOW[0]))
    Reg.DIR = Paths.get(lgdir)
    WD.place_ok = False
    sp3 = Core.spawn(W, wn, l, JInt(170), JInt(65), JInt(170), JInt(1), JInt(17), JLong(NOW[0]))
    WD.place_ok = True
    K.check(sp2 is None and len(WD.placed) == n_pl and Reg.at(l, JInt(150), JInt(65), JInt(150)) is None and sp3 is None
            and (150, 65, 150) not in WD.sounds and (170, 65, 170) not in WD.sounds
            and Reg.at(l, JInt(170), JInt(65), JInt(170)) is None and "170\t65\t170" not in (fileof(wn) or ""),
            "X5: the save refused -> nothing placed, no line; the place refused -> the line removed again (memory + disk)")
    WD.blocks[(120, 65, 120)] = "Furniture_Crude_Chest_Small"
    u1 = bool(Core.unplace(W, site(120, 65, 120)))
    u2 = bool(Core.unplace(W, site(110, 65, 110)))
    WD.unloaded.add((900 >> 5, 900 >> 5))
    u3 = bool(Core.unplace(W, site(900, 65, 900)))
    K.check(u1 and WD.blocks[(120, 65, 120)] == "Furniture_Crude_Chest_Small" and u2 and WD.blocks[(110, 65, 110)] == "Empty" and not u3,
            "X5: unplace(): a PLAYER CHEST on the spot is never touched (counts as gone); our block is removed; an unloaded chunk waits")

    # ============================================================================ X6 sweep
    reset_world(wn)
    shutil.rmtree(lgdir, ignore_errors=True)
    l = Reg.sites(wn)
    T = NOW[0]
    Cfg.LG_SHARE_S = 20          # 0.2.5: the shared mode (an admin sets a share time) - the 0.2.4 cases; the default 0 is checked below
    np0 = len(WD.poofs)
    share, desp, resp = int(Cfg.LG_SHARE_S) * 1000, int(Cfg.LG_DESPAWN_S) * 1000, int(Cfg.LG_RESPAWN_S) * 1000
    cases = {"claimed_old": site(1000, 65, 0, state=1, looted=T - share - 1), "claimed_new": site(1100, 65, 0, state=1, looted=T - 1000),
             "out_far": site(1200, 65, 0, placed=T - desp - 5, near=T - desp - 5), "out_seen": site(1300, 65, 0, near=T - 1000),
             "out_player": site(1400, 65, 0), "out_unloaded": site(1600, 65, 0, near=T - desp - 5),
             "gone_old": site(1500, 65, 0, state=2, looted=T - resp - 6 * 3600000 - 1), "gone_new": site(1700, 65, 0, state=2, looted=T - 1000)}
    for k, s in cases.items():
        Reg.add(l, s)
        if s.state != 2:
            WD.blocks[(int(s.x), 65, 0)] = "Skyy_LootChest_T1"
    WD.blocks[(1400, 65, 0)] = "Furniture_Village_Chest_Small"     # a player put a chest where our luggage was
    WD.unloaded.add((1600 >> 5, 0))
    n2, n4, n11 = int(Core.N[2]), int(Core.N[4]), int(Core.N[11])
    ch = int(Core.sweep(W, wn, l, JLong(T)))
    again = int(Core.sweep(W, wn, l, JLong(T + 10)))
    st = dict((k, (int(s.state), Reg.at(l, s.x, s.y, s.z) is not None, WD.blocks.get((int(s.x), 65, 0)))) for k, s in cases.items())
    disk = fileof(wn) or ""
    K.check(st["claimed_old"] == (2, True, "Empty") and st["claimed_new"][:2] == (1, True) and st["claimed_new"][2].startswith("Skyy_")
            and st["out_far"] == (0, False, "Empty") and st["out_seen"][:2] == (0, True) and st["out_player"] == (0, False, "Furniture_Village_Chest_Small")
            and st["out_unloaded"][:2] == (0, True) and st["gone_old"][1] is False and st["gone_new"][:2] == (2, True)
            and ch == 4 and again == 0 and int(Core.N[2]) == n2 + 1 and int(Core.N[4]) == n4 + 1 and int(Core.N[11]) == n11 + 2
            and "1200\t65\t0" not in disk and "1000\t65\t0\t1\t12\t2\t" in disk,
            "X6: sweep(): claimed past the share time -> vanishes (state 2); unvisited past despawn -> goes; a PLAYER CHEST on the spot -> "
            "the line dropped, the chest untouched; an unloaded chunk waits; long-gone forgotten; throttled to once a second; saved: %s ch %d" % (st, ch))
    K.check(WD.poofs[np0:] == [(1000, 65, 0, "Empty")], "X6: 0.2.5 the sweep's vanish shows the poof once, at the vanished block only (not for "
            "the despawn, not for the player chest): %s" % WD.poofs[np0:])
    Cfg.apply(Props())
    K.check(int(Cfg.LG_SHARE_S) == 0, "X6: 0.2.5 default share time 0")
    reset_world(wn)
    shutil.rmtree(lgdir, ignore_errors=True)
    l = Reg.sites(wn)
    s_now = site(1800, 65, 0, state=1, looted=T + 2000)          # claimed this very moment (default share 0) but the claim's removal failed
    Reg.add(l, s_now)
    WD.blocks[(1800, 65, 0)] = "Skyy_LootChest_T1"
    Core.SWEPT.clear()
    ch0 = int(Core.sweep(W, wn, l, JLong(T + 2000)))
    K.check(ch0 == 1 and int(s_now.state) == 2 and WD.blocks[(1800, 65, 0)] == "Empty" and WD.poofs[-1][:3] == (1800, 65, 0)
            and "1800\t65\t0\t1\t12\t2\t" in (fileof(wn) or ""),
            "X6: 0.2.5 share 0 -> a claimed luggage still standing goes on the very next sweep (the retry path), poof, saved")

    # ============================================================================ X7 respawn
    reset_world(wn)
    shutil.rmtree(lgdir, ignore_errors=True)
    l = Reg.sites(wn)
    rc = {"due": site(2000, 65, 0, tier=3, state=2, looted=T - resp - 1), "far": site(2300, 65, 0, state=2, looted=T - resp - 1),
          "early": site(2040, 65, 40, state=2, looted=T - 1000), "moved": site(2000, 65, 60, state=2, looted=T - resp - 1)}
    for s in rc.values():
        Reg.add(l, s)
    WD.blocks[(2000, 64, 60)] = "Soil_Pathway"
    WD.occ.add((2000, 0))
    nr0 = int(Core.respawn(W, wn, l, JDouble(2000.0), JDouble(0.0), JLong(T)))
    st0 = (int(rc["due"].state), Reg.at(l, JInt(2000), JInt(65), JInt(0)) is not None, WD.blocks.get((2000, 65, 0)))
    WD.occ.clear()
    K.check(nr0 == 0 and st0 == (2, True, None), "X7: FIX respawn(): a player standing on the spot -> it waits (still gone, NOT forgotten, "
            "nothing placed): %s" % (st0,))
    nr = int(Core.respawn(W, wn, l, JDouble(2000.0), JDouble(0.0), JLong(T)))
    K.check(nr == 1 and int(rc["due"].state) == 0 and WD.blocks.get((2000, 65, 0)) == "Skyy_LootChest_T3" and int(rc["far"].state) == 2
            and int(rc["early"].state) == 2 and Reg.at(l, JInt(2000), JInt(65), JInt(60)) is None and int(rc["due"].lootedAt) == 0
            and "2000\t65\t0\t3\t12\t0\t" in (fileof(wn) or "") and (2000, 65, 0) in WD.sounds,
            "X7: respawn(): due + near -> back FULL (tier kept, claims reset by state, saved); too far / too early wait; the spot no longer "
            "valid (a path now) -> forgotten")
    s9 = site(2000, 65, 50, state=2, looted=T - resp - 1)
    Reg.add(l, s9)
    Reg.DIR = Paths.get(blocker)
    Core.respawn(W, wn, l, JDouble(2000.0), JDouble(0.0), JLong(T))
    Reg.DIR = Paths.get(lgdir)
    st9 = (int(s9.state), WD.blocks.get((2000, 65, 50)), int(s9.lootedAt) == T - resp - 1)
    WD.place_ok = False
    Core.respawn(W, wn, l, JDouble(2000.0), JDouble(0.0), JLong(T))
    WD.place_ok = True
    K.check(st9 == (2, None, True) and Reg.at(l, JInt(2000), JInt(65), JInt(50)) is None, "X7: save refused -> stays gone, nothing "
            "placed, its times unchanged; place refused -> forgotten: %s" % (st9,))

    # ============================================================================ X8 spawnNear
    reset_world(wn)
    shutil.rmtree(lgdir, ignore_errors=True)
    l = Reg.sites(wn)
    WD.level = (12, 16)
    got = []
    for i in range(3):
        s = Core.spawnNear(W, wn, l, JDouble(5000.0), JDouble(5000.0), JLong(T))
        got.append(s)
    full = Core.spawnNear(W, wn, l, JDouble(5000.0), JDouble(5000.0), JLong(T))
    dd = [((int(s.x) + 0.5 - 5000) ** 2 + (int(s.z) + 0.5 - 5000) ** 2) ** 0.5 for s in got if s is not None]
    K.check(all(s is not None for s in got) and full is None and all(23 <= d <= 66 for d in dd) and all(12 <= int(s.lvl) <= 16 for s in got)
            and all(1 <= int(s.tier) <= 4 for s in got), "X8: spawnNear(): 3 luggage 24-64 blocks away at level 12-16, the 4th refused "
            "(luggage.perPlayer 3): distances %s, full %s, levels %s, tiers %s" % ([round(d) for d in dd], full, [int(s.lvl) for s in got if s is not None],
                                                                                [int(s.tier) for s in got if s is not None]))
    Cfg.LG_PER_PLAYER, Cfg.LG_PER_AREA = 20, 3
    # fixer: centred on the 3 sites (they are 24-64 blocks from 5000,5000): at 5010 one of them could fall outside the 64-block area box
    # (x < 4946) -> area 2, not refused -> a rare random X8 failure (seen once in this round)
    a4 = Core.spawnNear(W, wn, l, JDouble(5000.0), JDouble(5000.0), JLong(T))
    Cfg.LG_PER_AREA, Cfg.LG_WORLD_MAX = 50, 3
    a5 = Core.spawnNear(W, wn, l, JDouble(9000.0), JDouble(9000.0), JLong(T))
    Cfg.apply(Props())
    WD.level = None
    n12 = int(Core.N[12])
    a6 = Core.spawnNear(W, wn, l, JDouble(20000.0), JDouble(0.0), JLong(T))
    WD.level = (0, 0)
    a7 = Core.spawnNear(W, wn, l, JDouble(20000.0), JDouble(0.0), JLong(T))
    WD.level = (12, 16)
    n9 = int(Core.N[9])
    WD.unloaded.update(((30000 + dx) >> 5, (dz) >> 5) for dx in range(-80, 81, 16) for dz in range(-80, 81, 16))
    a8 = Core.spawnNear(W, wn, l, JDouble(30000.0), JDouble(0.0), JLong(T))
    K.check(a4 is None and a5 is None and a6 is None and int(Core.N[12]) == n12 + 1 and a7 is None and a8 is None and int(Core.N[9]) == n9 + 1,
            "X8: per-area / per-world caps refuse; no SkyyMobs level here (islands, the hub) -> none + 'no level'; a level of 0 -> none; no "
            "valid column in 8 tries -> none + 'no spot'")

    # ============================================================================ X9 use() - every branch, the claim written first, the loot
    for cn in ("com.hypixel.hytale.server.core.modules.entity.EntityModule", "com.hypixel.hytale.server.core.modules.item.ItemModule"):
        JClass(FAKE_PKG + ".FakeUtil").single(cn)
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    GM = JClass("com.hypixel.hytale.protocol.GameMode")
    ESc = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    REFc = JClass("com.hypixel.hytale.component.Ref")
    FS, FB, FPR, FI, FMS, FCH = (JClass(FAKE_PKG + "." + n) for n in ("FakeStore", "FakeBuffer", "FakePR", "FakeInv", "FakeMeta", "FakeChunk"))
    TRC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    V3 = JClass("org.joml.Vector3d")

    class Pl:
        pass

    def player(u, name, mode=None, slots=36, w=W):
        p_ = Pl()
        p_.u = u
        p_.pr = us.allocateInstance(FPR.class_)
        jf(PRc, "uuid").set(p_.pr, u)
        jf(PRc, "username").set(p_.pr, name)
        p_.pl = us.allocateInstance(PLA.class_)
        jf(PLA, "gameMode").set(p_.pl, mode or GM.Adventure)
        p_.inv = us.allocateInstance(FI.class_)
        p_.cont = SIC(JShort(slots))
        ICc = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
        p_.inv.comb = JClass("com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer")(JArray(ICc)([p_.cont]))
        jf(PLA, "inventory").set(p_.pl, p_.inv)
        p_.ref = us.allocateInstance(REFc.class_)
        jf(REFc, "index").setInt(p_.ref, JInt(5))
        p_.st = us.allocateInstance(FS.class_)
        p_.st.comps = JClass("java.util.HashMap")()
        m_ = IHM()
        m_.put(PLA.getComponentType(), p_.pl)
        m_.put(PRc.getComponentType(), p_.pr)
        p_.tc = us.allocateInstance(TRC.class_)
        jf(TRC, "position").set(p_.tc, V3(JDouble(0.0), JDouble(70.0), JDouble(0.0)))
        m_.put(TRC.getComponentType(), p_.tc)
        p_.st.comps.put(p_.ref, m_)
        es = us.allocateInstance(ESc.class_)
        jf(ESc, "world").set(es, w)
        p_.st.ext = es
        jf(REFc, "store").set(p_.ref, p_.st)
        p_.buf = us.allocateInstance(FB.class_)
        p_.buf.st = p_.st
        return p_

    def said(p_):
        return [] if p_.pr.said is None else [str(x) for x in p_.pr.said]

    def items(p_):
        out_ = []
        for i in range(int(p_.cont.getCapacity())):
            s_ = p_.cont.getItemStack(JShort(i))
            if s_ is not None and not s_.isEmpty():
                out_.append((str(s_.getItemId()), int(s_.getQuantity())))
        return out_
    PURSE, XP, BOXCALLS, ORDER = {}, [], [], []

    @JImplements("java.util.function.Function")
    class CoinAdd:
        @JOverride
        def apply(self, a):
            ORDER.append(("coins", fileof(wn)))
            PURSE[str(a[0])] = PURSE.get(str(a[0]), 0) + int(a[1])
            return JLong(PURSE[str(a[0])])

    @JImplements("java.util.function.Function")
    class Box:
        @JOverride
        def apply(self, a):
            BOXCALLS.append((None if a[0] is None else str(a[0].getItemId()), int(a[1]), str(a[2]), int(a[3]), str(a[4])))
            return IS("Weapon_Sword_Iron", JInt(1))

    @JImplements("java.util.function.Function")
    class Describe:
        @JOverride
        def apply(self, b):
            return JArray(JString)(["Unidentified Sword", "Rare"])

    @JImplements("java.util.function.Function")
    class AddXp:
        @JOverride
        def apply(self, a):
            XP.append((str(a[0]), str(a[1]), int(a[2])))
            return JBoolean(True)
    br.put("coins:fn:add", CoinAdd())
    br.put("gear:fn:box", Box())
    br.put("gear:fn:describe", Describe())
    br.put("skill:fn:addxp", AddXp())
    reset_world(wn)
    shutil.rmtree(lgdir, ignore_errors=True)
    l = Reg.sites(wn)
    T = int(JClass("java.lang.System").currentTimeMillis())
    A = player(U1, "Alpha")
    Bp = player(U2, "Bravo")
    Cp = player(U3, "Charlie")
    s_main = site(7000, 65, 0, tier=2, lvl=24, placed=T)
    Reg.add(l, s_main)
    WD.blocks[(7000, 65, 0)] = "Skyy_LootChest_T2"
    Reg.save(wn)

    def use(p_, x=7000, y=65, z=0, acc=None):
        return int(Core.use(p_.ref, acc if acc is not None else p_.buf, p_.pr, JInt(x), JInt(y), JInt(z)))
    r_not = use(A, 7001, 65, 0)
    Cfg.LG_ON = False
    r_off = use(A)
    Cfg.LG_ON = True
    Cr = player(UUID(0, 99), "Crea", GM.Creative)
    r_cr = use(Cr)
    br.put("profile:busy:" + str(A.u), "1")
    r_busy = use(A)
    br.remove("profile:busy:" + str(A.u))
    WD.blocks[(7100, 65, 0)] = "Skyy_LootChest_T1"     # an admin placed one: no registry line
    r_admin = use(A, 7100, 65, 0)
    K.check(r_not == -1 and r_off == 0 and r_cr == 0 and r_busy == 0 and r_admin == 0 and not PURSE and not items(A)
            and [x for x in said(A)] == ["[Exploration] Unclaimed Luggage is switched off on this server.",
                                         "[Exploration] Your profile is switching - try again in a moment.", "[Exploration] This luggage is empty."]
            and said(Cr) == ["[Exploration] Luggage cannot be claimed in creative mode."],
            "X9: use(): not our block -> -1 (vanilla handles it); switched off / creative / a profile switch / an admin-placed one (no line) -> "
            "a line, nothing given: %s %s" % (said(A), said(Cr)))
    A.pr.said = None
    n1, n5, n6 = int(Core.N[1]), int(Core.N[5]), int(Core.N[6])
    r_ok = use(A)
    zone = 2
    cmin, cmax = 25 * 1.5, 60 * 1.5
    coins = PURSE.get(str(U1), 0)
    xp_exp = round(300 * float(Cfg.CHEST_ZM[zone - 1]))
    first_order = ORDER[0][1] if ORDER else ""
    ia = items(A)
    K.check(r_ok == 1 and int(s_main.lootedAt) >= T and int(s_main.claimedAt(U1)) >= T and int(Core.N[1]) == n1 + 1
            and first_order is not None and ("%s:" % U1) in first_order and "7000\t65\t0\t2\t24\t1\t" in first_order,
            "X9: a claim: the claim + state 1 ON DISK before the first coin is paid (write-first)")
    K.check(round(cmin) <= coins <= round(cmax) and int(Core.N[6]) == n6 + coins, "X9: coins within tier II x zone 2 (%d..%d): %d" % (cmin, cmax, coins))
    K.check(len([c for c in BOXCALLS if c[0] is None]) == 1 and all(c[1:4] == (24, "lootchest", 2) and c[4] == str(U1) for c in BOXCALLS if c[0] is None)
            and int(Core.N[5]) == n5 + 1, "X9: tier II = 1 mystery bag from gear:fn:box(null, Lv 24, lootchest, tier 2, the player): %s" % BOXCALLS)
    K.check(XP and XP[-1] == (str(U1), "Exploration", xp_exp), "X9: Exploration XP 300 x the zone 2 chest multiplier = %d through the owed "
            "ledger -> skill:fn:addxp: %s" % (xp_exp, XP))
    vanilla = [x for x in ia if not x[0] == "Weapon_Sword_Iron"]
    line = [x for x in said(A) if x.startswith("[Exploration] Unclaimed Luggage (II, Lv 24): ")]
    K.check(vanilla and line and ("+%d coins" % coins) in line[0] and "Unidentified Sword (Rare)" in line[0] and "Exploration XP" in line[0],
            "X9: the REAL vanilla Zone2_Encounters_Tier2 roll lands in the inventory %s; one chat line: %s" % (vanilla, line))
    # 0.2.5: one claim (share 0) -> the block is gone right after the loot (same call), state 2 saved, one poof at the block
    disk_m = fileof(wn) or ""
    K.check(int(s_main.state) == 2 and WD.blocks.get((7000, 65, 0)) == "Empty" and (7000, 65, 0) in WD.cleared
            and [p_[:3] for p_ in WD.poofs].count((7000, 65, 0)) == 1 and "7000\t65\t0\t2\t24\t2\t" in disk_m and int(s_main.claimedAt(U1)) >= T
            and int(s_main.lootedAt) >= T,
            "X9: 0.2.5 VANISH AT ONCE - after the first claim the luggage block is removed in the same call, state 2 (waits to come back, "
            "the claim kept) saved, one poof at the block: state %d, block %s" % (int(s_main.state), WD.blocks.get((7000, 65, 0))))
    A.pr.said = None
    p_b0 = dict(PURSE)
    r_again = use(A)
    r_b = use(Bp)
    K.check(r_again == -1 and r_b == -1 and PURSE.get(str(U2)) is None and not items(Bp) and not said(A) and not said(Bp),
            "X9: 0.2.5 after the vanish the spot is air -> F there is not ours (-1), nobody gets anything")
    # the race: a second player presses F before the block is gone on their screen (or the removal failed) -> 'already claimed', nothing
    s_race = site(7050, 65, 0, tier=1, lvl=5, state=1, looted=T, who="%s:%d" % (U1, T))
    Reg.add(l, s_race)
    WD.blocks[(7050, 65, 0)] = "Skyy_LootChest_T1"
    r_race = use(Bp, 7050, 65, 0)
    K.check(r_race == 0 and said(Bp) == ["[Exploration] This luggage was already claimed."] and PURSE.get(str(U2)) is None and int(s_race.claimedAt(U2)) == 0,
            "X9: 0.2.5 one claim per luggage - a second player on a claimed luggage -> 'already claimed', nothing given: %s" % said(Bp))
    Bp.pr.said = None
    # the removal fails (clear refused) -> the claim + loot stand, the block stays for a moment, state 1; the next sweep removes it
    s_fail = site(7060, 65, 0, tier=1, lvl=5)
    Reg.add(l, s_fail)
    WD.blocks[(7060, 65, 0)] = "Skyy_LootChest_T1"
    WD.clear_ok = False
    r_fail = use(Bp, 7060, 65, 0)
    WD.clear_ok = True
    st_fail = (int(s_fail.state), WD.blocks.get((7060, 65, 0)))
    Core.SWEPT.clear()
    Core.sweep(W, wn, l, JLong(int(s_fail.lootedAt) + 1))
    K.check(r_fail == 1 and st_fail == (1, "Skyy_LootChest_T1") and PURSE.get(str(U2), 0) > 0 and int(s_fail.state) == 2
            and WD.blocks.get((7060, 65, 0)) == "Empty",
            "X9: 0.2.5 a removal that fails -> loot given, state 1 kept; the once-a-second sweep removes it (share 0 = due at once): %s" % (st_fail,))
    # the vanish itself throws (the chunk goes away between the claim and the removal) -> one warning, the claim stands, sweep retries
    s_boom = site(7070, 65, 0, tier=1, lvl=5)
    Reg.add(l, s_boom)
    WD.blocks[(7070, 65, 0)] = "Skyy_LootChest_T1"
    WD.boom_at, WD.boom_n = (7070, 65, 0), 0
    Kp = player(UUID(0, 13), "Kilo")
    r_vb = use(Kp, 7070, 65, 0)
    WD.boom_at = None
    K.check(r_vb == 1 and int(s_boom.state) == 1 and int(s_boom.claimedAt(Kp.u)) > 0 and any("luggage vanish failed" in m for m in ourlogs()),
            "X9: 0.2.5 the vanish throwing -> logged (once a minute), the claim + loot stand, state 1 for the sweep to retry")
    # SHARED mode (an admin sets a share time > 0): the 0.2.4 behaviour - each player nearby claims their own loot, then it vanishes
    Cfg.LG_SHARE_S = 20
    s_sh = site(7080, 65, 0, tier=2, lvl=24)
    Reg.add(l, s_sh)
    WD.blocks[(7080, 65, 0)] = "Skyy_LootChest_T2"
    A.pr.said = None
    r_sa = use(A, 7080, 65, 0)
    r_sa2 = use(A, 7080, 65, 0)
    r_sb = use(Bp, 7080, 65, 0)
    looted_b = int(s_sh.lootedAt)
    K.check(r_sa == 1 and r_sa2 == 0 and "[Exploration] You already claimed this luggage." in said(A) and r_sb == 1 and looted_b == int(s_sh.lootedAt)
            and int(s_sh.state) == 1 and WD.blocks.get((7080, 65, 0)) == "Skyy_LootChest_T2" and int(s_sh.claimedAt(U2)) > 0,
            "X9: share time 20 (Server Setup) -> the 0.2.4 shared mode: it stays, the same player again -> 'already claimed', a second player "
            "nearby gets their OWN loot (the share timer is not restarted)")
    s_sh.lootedAt = T - int(Cfg.LG_SHARE_S) * 1000 - 5
    r_c = use(Cp, 7080, 65, 0)
    Cfg.apply(Props())
    K.check(r_c == 0 and "already claimed" in " ".join(said(Cp)), "X9: after the share time -> 'already claimed'")
    # FIX (critic 3): the default cooldown = the respawn time, and a claim belongs to ONE appearance (placedAt)
    cd = int(Cfg.LG_SITE_CD) * 1000
    K.check(cd == int(Cfg.LG_RESPAWN_S) * 1000 == 1800000, "X9: FIX luggage.siteCooldown default 1800 s = luggage.respawnSeconds")
    s_back = site(7810, 65, 0, tier=1, lvl=5, placed=T, who="%s:%d" % (U1, T - 1800000))     # came back after 30 min: A looted it then
    s_rec = site(7820, 65, 0, tier=1, lvl=5, placed=T, who="%s:%d" % (U1, T - 600000))       # an admin shortened the respawn: 10 min ago
    for s_ in (s_back, s_rec):
        Reg.add(l, s_)
        WD.blocks[(int(s_.x), 65, 0)] = "Skyy_LootChest_T1"
    A.pr.said = None
    r_back, r_rec = use(A, 7810, 65, 0), use(A, 7820, 65, 0)
    K.check(r_back == 1 and r_rec == 0 and any("you can claim it again in 20 min" in x for x in said(A)),
            "X9: FIX a solo player loots the luggage AGAIN as soon as it is back (claimed 30 min ago, came back now); claimed 10 min ago -> "
            "'looted this spot recently - again in 20 min': %s" % said(A)[-2:])
    s_cap = site(7200, 65, 0, tier=1, lvl=5)
    Reg.add(l, s_cap)
    WD.blocks[(7200, 65, 0)] = "Skyy_LootChest_T1"
    Cfg.LG_CAP = 1
    r_cap = use(A, 7200, 65, 0)
    Cfg.LG_CAP = 8
    K.check(r_cap == 0 and "claimed 1 luggage in the last hour" in " ".join(said(A)) and int(s_cap.state) == 0, "X9: the hourly cap refuses (nothing changes)")
    D = player(UUID(0, 4), "Delta")
    Reg.DIR = Paths.get(blocker)
    p0 = dict(PURSE)
    r_sf = use(D, 7200, 65, 0)
    Reg.DIR = Paths.get(lgdir)
    K.check(r_sf == 0 and "could not be saved - nothing was taken" in " ".join(said(D)) and int(s_cap.state) == 0 and str(s_cap.who) == ""
            and int(s_cap.lootedAt) == 0 and PURSE == p0 and not items(D), "X9: the save refused -> the claim rolled back in memory, nothing given")
    Ec = player(UUID(0, 5), "Echo")
    jf(PLA, "inventory").set(Ec.pl, None)
    r_boom = use(Ec, 7200, 65, 0)
    K.check(r_boom == 1 and int(s_cap.claimedAt(Ec.u)) > 0 and "7200\t65\t0\t1\t5\t2\t" in (fileof(wn) or "")
            and any("luggage loot failed (the claim is saved)" in m for m in ourlogs()),
            "X9: the loot itself failing (no inventory) -> the claim stays saved (never twice), one warning; 0.2.5: it still vanishes")
    # FIX (critic 1): the registry cannot be read -> nothing is claimed, the file stays
    wf_ = str(ChestReg.wf(wn))
    fpath = os.path.join(lgdir, wf_ + ".tsv")
    keep_txt = open(fpath, encoding="utf8").read()
    Reg.W.remove(wf_)
    os.remove(fpath)
    os.makedirs(fpath)
    Zp = player(UUID(0, 11), "Zulu")
    WD.blocks[(7090, 65, 0)] = "Skyy_LootChest_T1"
    r_unr = use(Zp, 7090, 65, 0)
    os.rmdir(fpath)
    open(fpath, "w", encoding="utf8").write(keep_txt)
    Reg.W.put(wf_, l)
    K.check(r_unr == 0 and said(Zp) == ["[Exploration] This luggage cannot be claimed right now - try again later."] and not PURSE.get(str(Zp.u))
            and not items(Zp), "X9: FIX an unreadable registry -> 'cannot be claimed right now', nothing given: %s" % said(Zp))
    # overflow: a full inventory -> the engine's own drop path (ItemUtils.dropItem -> DropItemEvent$Drop through the accessor)
    Fp = player(UUID(0, 6), "Foxtrot", slots=1)
    Fp.cont.setItemStackForSlot(JShort(0), IS("Ingredient_Stick", JInt(int(IS("Ingredient_Stick", JInt(1)).getItem().getMaxStack()))))
    s_ov = site(7300, 65, 0, tier=4, lvl=50)
    Reg.add(l, s_ov)
    WD.blocks[(7300, 65, 0)] = "Skyy_LootChest_T4"
    r_ov = use(Fp, 7300, 65, 0)
    evs = [str(e.getClass().getName()) for e in (Fp.buf.events or [])]
    K.check(r_ov == 1 and evs and all(e.endswith("DropItemEvent$Drop") for e in evs), "X9: a full inventory -> every item goes to the engine's "
            "drop at the player's feet (addOrDropItemStack -> ItemUtils.dropItem): %d drop events" % len(evs))
    # vanilla gear in the roll -> asBag (gear:fn:box with the item); no box function -> gear:fn:unid; neither -> the item itself
    BOXCALLS[:] = []
    sw = Core.asBag(IS("Weapon_Sword_Copper", JInt(1)), JInt(9), JInt(3), U1)
    two = Core.asBag(IS("Weapon_Sword_Copper", JInt(2)), JInt(9), JInt(3), U1)
    br.remove("gear:fn:box")

    @JImplements("java.util.function.Function")
    class Unid:
        @JOverride
        def apply(self, a):
            return IS("Ingredient_Stick", JInt(1))
    br.put("gear:fn:unid", Unid())
    viau = Core.asBag(IS("Weapon_Sword_Copper", JInt(1)), JInt(9), JInt(3), U1)
    br.remove("gear:fn:unid")
    plain = Core.asBag(IS("Weapon_Sword_Copper", JInt(1)), JInt(9), JInt(3), U1)
    br.put("gear:fn:box", Box())
    K.check(BOXCALLS == [("Weapon_Sword_Copper", 9, "lootchest", 3, str(U1))] and str(sw.getItemId()) == "Weapon_Sword_Iron"
            and str(two.getItemId()) == "Weapon_Sword_Copper" and str(viau.getItemId()) == "Ingredient_Stick" and str(plain.getItemId()) == "Weapon_Sword_Copper",
            "X9: asBag(): a single vanilla weapon -> gear:fn:box(item, L, lootchest, tier); a stack -> not boxed; no box -> gear:fn:unid; neither -> as it is")
    K.check(str(Core.bagName(IS("Weapon_Sword_Iron", JInt(1)))) == "Unidentified Sword (Rare)", "X9: bagName() through gear:fn:describe")
    br.remove("gear:fn:describe")
    K.check(len(str(Core.bagName(IS("Weapon_Sword_Iron", JInt(1))))) > 0, "X9: bagName() without SkyyGear -> the item's name")
    br.put("gear:fn:describe", Describe())

    @JImplements("java.util.function.Function")
    class Quiet:
        @JOverride
        def apply(self, a):
            return JBoolean(False)
    br.put("settings:fn:get", Quiet())
    G2 = player(UUID(0, 7), "Golf")
    s_q = site(7400, 65, 0, tier=1, lvl=5)
    Reg.add(l, s_q)
    WD.blocks[(7400, 65, 0)] = "Skyy_LootChest_T1"
    r_q = use(G2, 7400, 65, 0)
    br.remove("settings:fn:get")
    K.check(r_q == 1 and not said(G2) and PURSE.get(str(G2.u), 0) > 0, "X9: 'Exploration finds' notifications off -> the loot, no chat line")
    Cfg.LG_VANILLA = False
    H2 = player(UUID(0, 8), "Hotel")
    BOXCALLS[:] = []
    s_nv = site(7500, 65, 0, tier=1, lvl=5)
    Reg.add(l, s_nv)
    WD.blocks[(7500, 65, 0)] = "Skyy_LootChest_T1"
    use(H2, 7500, 65, 0)
    Cfg.apply(Props())
    K.check(all(x[0] == "Weapon_Sword_Iron" for x in items(H2)), "X9: luggage.vanillaRoll off -> no vanilla roll (only bags): %s" % items(H2))

    # ============================================================================ X10 LgUse.tryCreate
    ICX = JClass("com.hypixel.hytale.server.core.entity.InteractionContext")
    ctx = us.allocateInstance(ICX.class_)
    meta = us.allocateInstance(FMS.class_)
    jf(ICX, "metaStore").set(ctx, meta)
    BP = JClass("com.hypixel.hytale.protocol.BlockPosition")
    meta.bp = BP(JInt(7600), JInt(65), JInt(0))
    K.check(int(ctx.getTargetBlock().x) == 7600, "X10: the real InteractionContext.getTargetBlock reads the stand-in meta store")
    s_u = site(7600, 65, 0, tier=1, lvl=5)
    Reg.add(l, s_u)
    WD.blocks[(7600, 65, 0)] = "Skyy_LootChest_T1"
    I2 = player(UUID(0, 9), "India")
    pg = LgUse().tryCreate(I2.ref, I2.buf, I2.pr, ctx)
    pg_null = LgUse().tryCreate(I2.ref, I2.buf, I2.pr, None)
    meta.boom = True
    LgUse.FAILED_ONCE = False
    pg_boom = LgUse().tryCreate(I2.ref, I2.buf, I2.pr, ctx)
    K.check(pg is None and pg_null is None and pg_boom is None and int(s_u.claimedAt(I2.u)) > 0 and bool(LgUse.FAILED_ONCE)
            and int(s_u.state) == 2 and WD.blocks.get((7600, 65, 0)) == "Empty",
            "X10: LgUse.tryCreate: claims at the context's target block and returns NO page (OpenCustomUIInteraction opens nothing); 0.2.5 "
            "the block is gone when it returns; no context -> nothing; a failure -> logged once, no page")

    # ============================================================================ X11 LgBreakSys / LgDamageSys on the real BlockTypes
    BBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent")
    DBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent")
    V3i = JClass("org.joml.Vector3i")
    lgbt, vbt = BT.getAssetMap().getAsset("Skyy_LootChest_T1"), BT.getAssetMap().getAsset("Furniture_Crude_Chest_Small")

    def chunk(mode):
        c_ = us.allocateInstance(FCH.class_)
        c_.comps = IHM()
        if mode is not None:
            pl_ = us.allocateInstance(PLA.class_)
            jf(PLA, "gameMode").set(pl_, mode)
            c_.comps.put(PLA.getComponentType(), pl_)
        return c_
    s_b = site(7700, 65, 0)
    Reg.add(l, s_b)
    Reg.save(wn)

    def brk(bt, mode, pre=False, x=7700):
        e_ = BBE(None, V3i(JInt(x), JInt(65), JInt(0)), bt)
        if pre:
            e_.setCancelled(True)
        Brk().handle(JInt(0), chunk(mode), I2.st, None, e_)
        return bool(e_.isCancelled())

    def dmg(bt, mode, x=7700):
        e_ = DBE(None, V3i(JInt(x), JInt(65), JInt(0)), bt, JFloat(0.0), JFloat(1.0))
        Dmg().handle(JInt(0), chunk(mode), I2.st, None, e_)
        return bool(e_.isCancelled())
    n10 = int(Core.N[10])
    b1, b2, b3, b4 = brk(lgbt, GM.Adventure), brk(lgbt, None), brk(vbt, GM.Adventure), brk(lgbt, GM.Adventure, pre=True)
    line_before = Reg.at(l, JInt(7700), JInt(65), JInt(0)) is not None
    d1, d2, d3 = dmg(lgbt, GM.Adventure), dmg(lgbt, GM.Creative), dmg(vbt, GM.Adventure)
    b5 = brk(lgbt, GM.Creative)
    K.check(b1 and b2 and not b3 and b4 and line_before and not b5 and Reg.at(l, JInt(7700), JInt(65), JInt(0)) is None and int(Core.N[10]) == n10 + 1
            and "7700\t65\t0" not in (fileof(wn) or "") and d1 and not d2 and not d3,
            "X11: break: luggage outside Creative cancelled (no player component too); a vanilla chest untouched; in Creative it breaks and "
            "its line goes (saved); damage the same")
    b_orph, d_orph = brk(lgbt, GM.Adventure, x=7705), dmg(lgbt, GM.Adventure, x=7705)
    wf_ = str(ChestReg.wf(wn))
    fpath = os.path.join(lgdir, wf_ + ".tsv")
    keep_txt = open(fpath, encoding="utf8").read()
    Reg.W.remove(wf_)
    os.remove(fpath)
    os.makedirs(fpath)
    b_unr, d_unr = brk(lgbt, GM.Adventure, x=7705), dmg(lgbt, GM.Adventure, x=7705)
    os.rmdir(fpath)
    open(fpath, "w", encoding="utf8").write(keep_txt)
    Reg.W.put(wf_, l)
    K.check(not b_orph and not d_orph and b_unr and d_unr, "X11: FIX a luggage block with NO registry line (admin-placed / line lost) can be "
            "broken by anyone (it drops nothing - never an unbreakable orphan); while the registry cannot be read every luggage stays protected")

    # ============================================================================ X12 second() (ExpTick, once a second)
    reset_world(wn)
    shutil.rmtree(lgdir, ignore_errors=True)
    l = Reg.sites(wn)
    J = player(UUID(0, 10), "Juliet")
    stt = State()
    TT = [T]

    def tick(p_, w_=W, creative=False, flying=False, n=1, pos=None):
        if pos is not None:
            jf(TRC, "position").set(p_.tc, V3(JDouble(pos[0]), JDouble(70.0), JDouble(pos[1])))
        for _ in range(n):
            TT[0] += 1000
            Core.second(p_.pr, p_.pl, p_.ref, p_.st, p_.u, stt, w_, JBoolean(creative), JBoolean(flying), JLong(TT[0]))
    Cfg.LG_SPAWN_S = 5
    tick(J, n=4, pos=(0.0, 0.0))
    none_yet = int(l.size())
    tick(J, n=1)
    one = int(l.size())
    tick(J, n=5, creative=True)
    tick(J, n=5, flying=True)
    after_cf = int(l.size())
    TT[0] += int(Cfg.LG_AFK_S) * 1000 + 1000
    tick(J, n=5)
    afk = int(l.size())
    tick(J, n=5, pos=(40.0, 0.0))
    moved = int(l.size())
    K.check(none_yet == 0 and one == 1 and after_cf == 1 and afk == 1 and moved == 2 and bool(stt.lgHas) and float(stt.lgX) == 40.0,
            "X12: second(): a new luggage try every luggage.spawnSeconds (5 here); none in Creative / flying; none for an idle player (AFK); "
            "moving 32+ blocks resets the idle timer: %s" % [none_yet, one, after_cf, afk, moved])
    sn = l.get(0)
    sn.lastNear = 0
    tick(J, n=1)
    near_ok = int(sn.lastNear) == TT[0] or ((int(sn.x) - 40) ** 2 + int(sn.z) ** 2) > 96 ** 2
    WI = world("skyy-island-abc")
    li = Reg.sites("skyy-island-abc")
    tick(J, w_=WI, n=10)
    K.check(near_ok and int(li.size()) == 0, "X12: a player within 96 blocks keeps luggage from going away (lastNear); an island world "
            "(excluded) gets none")
    Cfg.LG_ON = False
    out_before = [(int(l.get(i).x), int(l.get(i).y), int(l.get(i).z)) for i in range(int(l.size())) if int(l.get(i).state) != 2]
    n_off = int(l.size())
    tick(J, n=2, pos=(400.0, 0.0))
    left = int(l.size())
    disk_off = fileof(wn) or ""
    Cfg.apply(Props())
    K.check(n_off >= 2 and out_before and left == 0 and all(WD.blocks.get(k) == "Empty" for k in out_before)
            and not any(("%d\t%d\t%d\t" % k) in disk_off for k in out_before),
            "X12: FIX luggage.enabled OFF -> every luggage of the world in a loaded chunk is removed (block + line, saved) - nothing is "
            "stranded: %d -> %d, %s" % (n_off, left, out_before))
    wx = "skyy-island-xyz"
    WX = world(wx)
    lx = Reg.sites(wx)
    Reg.add(lx, site(41000, 65, 0))
    WD.blocks[(41000, 65, 0)] = "Skyy_LootChest_T1"
    Reg.save(wx)
    tick(J, w_=WX, n=2)
    wn_new = "never-had-luggage"
    tick(J, w_=world("skyy-island-new"), n=2)
    K.check(int(lx.size()) == 0 and WD.blocks.get((41000, 65, 0)) == "Empty"
            and not os.path.exists(os.path.join(lgdir, str(ChestReg.wf("skyy-island-new")) + ".tsv"))
            and not bool(Reg.W.containsKey(str(ChestReg.wf("skyy-island-new")))),
            "X12: FIX a world that is EXCLUDED now -> its luggage is removed too; an excluded world that never had luggage gets no file and "
            "no registry entry")

    # ============================================================================ X13 statsText / flushAll / LgEng without the seam
    txt = str(Core.statsText())
    K.check(txt.startswith("Unclaimed Luggage on: out ") and "claims " in txt and "no level " in txt, "X13: statsText: %s" % txt[:160])
    shutil.rmtree(lgdir, ignore_errors=True)
    Core.flushAll()
    K.check(os.path.isfile(os.path.join(lgdir, str(ChestReg.wf(wn)) + ".tsv")), "X13: flushAll (shutdown) writes every world's registry")
    Eng.API = None
    K.check(Eng.blockId(None, JInt(0), JInt(65), JInt(0)) is None and int(Eng.height(None, JInt(0), JInt(0))) == -1
            and bool(Eng.hasEntity(None, JInt(0), JInt(65), JInt(0))) and bool(Eng.fluid(None, JInt(0), JInt(65), JInt(0)))
            and not bool(Eng.place(None, JInt(0), JInt(65), JInt(0), "Skyy_LootChest_T1")) and not bool(Eng.clear(None, JInt(0), JInt(65), JInt(0)))
            and str(Eng.blockId(None, JInt(0), JInt(400), JInt(0))) == "Empty" and not bool(Eng.hasEntity(None, JInt(0), JInt(-1), JInt(0))),
            "X13: LgEng with no seam and no loaded chunk: unknown block (null), height -1, 'entity' + 'fluid' (never spawn next to the "
            "unknown), place / clear refused; out-of-world y")
    LV = []

    @JImplements("java.util.function.Function")
    class LevelAt:
        @JOverride
        def apply(self, a):
            LV.append([str(a[0]), int(a[1]), int(a[2]), int(a[3])])
            return JArray(JObject)([JInt(30), JInt(34), "zone", "k"])
    br.put("mob:fn:levelAt", LevelAt())
    la = Eng.levelAt("Default", JInt(1), JInt(65), JInt(-2))
    br.put("mob:fn:levelAt", Quiet())
    la2 = Eng.levelAt("Default", JInt(1), JInt(65), JInt(-2))
    br.remove("mob:fn:levelAt")
    la3 = Eng.levelAt("Default", JInt(1), JInt(65), JInt(-2))
    # FIX: the REAL LgEng.occupied (World.playerRefs -> PlayerRef.transform -> position) and LgEng.sound (the SoundEvent index lookup)
    TRF = JClass("com.hypixel.hytale.math.vector.Transform")
    wq = world("Default")
    prq = us.allocateInstance(PRc.class_)
    trq = us.allocateInstance(TRF.class_)
    jf(TRF, "position").set(trq, V3(JDouble(100.5), JDouble(65.0), JDouble(200.5)))
    jf(PRc, "transform").set(prq, trq)
    prn = us.allocateInstance(PRc.class_)            # a player ref without a transform yet (just joining)
    alq = JClass("java.util.ArrayList")()
    alq.add(prn)
    alq.add(prq)
    jf(WLD, "playerRefs").set(wq, alq)
    occ = [bool(Eng.occupied(wq, JInt(100), JInt(65), JInt(200))), bool(Eng.occupied(wq, JInt(101), JInt(66), JInt(201))),
           bool(Eng.occupied(wq, JInt(102), JInt(65), JInt(200))), bool(Eng.occupied(wq, JInt(100), JInt(70), JInt(200))),
           bool(Eng.occupied(None, JInt(0), JInt(65), JInt(0)))]
    Eng.SND = JInt(-2147483647)
    Eng.sound(wq, JInt(100), JInt(65), JInt(200))
    snd = int(Eng.SND)
    K.check(occ == [True, True, False, False, True] and snd != -2147483647,
            "X13: FIX the real LgEng.occupied: a player on the block / the one next to it -> yes, 2 blocks away / 5 above -> no, a player "
            "without a position is skipped, no world -> yes; LgEng.sound resolves the sound index (%d = %s) and never throws without a store: %s"
            % (snd, "missing" if snd == -2147483648 else "found", occ))
    if snd == -2147483648:
        K.notes.append("X13: the bare JVM's SoundEvent store has no SFX_Cloth_Land (the build asserts it is in Assets.zip)")
    # 0.2.5: the REAL LgEng.poof - no world / a world without its entity store / a stand-in accessor: never throws; the sound index resolves
    Eng.PSND = JInt(-2147483647)
    poof_err = []
    for args in ((None, None), (wq, None), (wq, I2.buf)):
        try:
            Eng.poof(args[0], JInt(100), JInt(65), JInt(200), args[1])
        except Exception as e_:
            poof_err.append(str(e_)[:120])
    psnd = int(Eng.PSND)
    K.check(not poof_err and psnd != -2147483647, "X13: 0.2.5 the real LgEng.poof (ParticleUtil.spawnParticleEffect Block_Break_Dust + "
            "SFX_Cloth_Break 3D) never throws (no world, no entity store, a stand-in accessor); the sound index lookup ran (%d = %s): %s"
            % (psnd, "missing" if psnd == -2147483648 else "found", poof_err))
    Eng.API = API
    K.check(la is not None and [int(la[0]), int(la[1])] == [30, 34] and LV == [["Default", 1, 65, -2]] and la2 is None and la3 is None,
            "X13: LgEng.levelAt -> mob:fn:levelAt (world name, x, y, z) -> Object[] or null (not an array / SkyyMobs absent)")
    # FIX (critic 3): /exploreadmin luggage + luggage list (LgCore.adminHere / listNear)
    reset_world(wn)
    la_ = Reg.sites(wn)
    Adm = player(UUID(0, 12), "Admin")
    jf(TRC, "position").set(Adm.tc, V3(JDouble(50000.0), JDouble(70.0), JDouble(0.0)))
    n_pl0 = len(WD.placed)
    msg1 = str(Core.adminHere(W, Adm.ref, Adm.st, JLong(T)))
    new_s = [la_.get(i) for i in range(int(la_.size()))]
    dists = [((int(s_.x) + 0.5 - 50000) ** 2 + (int(s_.z) + 0.5) ** 2) ** 0.5 for s_ in new_s]
    lst = str(Core.listNear(W, JDouble(50000.0), JDouble(0.0), JLong(T)))
    jf(TRC, "position").set(Adm.tc, V3(JDouble(60000.0), JDouble(70.0), JDouble(0.0)))
    WD.level = None
    msg2 = str(Core.adminHere(W, Adm.ref, Adm.st, JLong(T)))
    WD.level = (12, 16)
    Cfg.LG_ON = False
    msg3 = str(Core.adminHere(W, Adm.ref, Adm.st, JLong(T)))
    Cfg.apply(Props())
    msg4 = str(Core.adminHere(world("skyy-island-adm"), Adm.ref, Adm.st, JLong(T)))
    K.check(msg1.startswith("+Placed Unclaimed Luggage") and len(new_s) == 1 and len(WD.placed) == n_pl0 + 1 and all(2.0 <= d <= 11.5 for d in dists)
            and lst.startswith("=Unclaimed Luggage in Default (on): 1 site(s)") and " - out - " in lst
            and msg2.startswith("-SkyyMobs gives no mob level here") and msg3.startswith("-Unclaimed Luggage is switched off")
            and msg4.startswith("-This world never gets luggage") and len(new_s) == 1,
            "X13: FIX /exploreadmin luggage places one 3-10 blocks away (through spawn(): write-ahead + every spot rule) and 'luggage list' "
            "shows it; no level / switched off / an excluded world -> refused: %s | %s | %s" % (msg1, lst.replace(chr(10), " / ")[:160], dists))
    K.check(not WD.violations, "X: THE PLAYER-CHEST LOCK - every place / clear in this run was on a Skyy_LootChest_T* block: %s" % WD.violations[:5])

    # ============================================================================ X14 ExpCfg rows / check / clamps
    Cfg.apply(Props())
    dflt = [bool(Cfg.LG_ON), int(Cfg.LG_SPAWN_S), int(Cfg.LG_PER_PLAYER), int(Cfg.LG_PER_AREA), int(Cfg.LG_WORLD_MAX), int(Cfg.LG_RING_MIN),
            int(Cfg.LG_RING_MAX), int(Cfg.LG_SHARE_S), int(Cfg.LG_RESPAWN_S), int(Cfg.LG_DESPAWN_S), int(Cfg.LG_CAP), int(Cfg.LG_SITE_CD),
            int(Cfg.LG_AFK_S), list(Cfg.LG_TIER_W), list(Cfg.LG_BAGS), list(Cfg.LG_COIN_MIN), list(Cfg.LG_COIN_MAX), list(Cfg.LG_COIN_ZM),
            list(Cfg.LG_XP), bool(Cfg.LG_VANILLA)]
    K.check(dflt == [True, 30, 3, 6, 200, 24, 64, 0, 1800, 900, 8, 1800, 300, [60, 28, 10, 2], [0.5, 1, 1.5, 2], [10, 25, 60, 150],
                     [30, 60, 150, 400], [1, 1.5, 2, 3], [150, 300, 600, 1000], True], "X14: defaults (Loot-Round-Revision section 5): %s" % dflt)
    pp = Props()
    for k, v in (("luggage.ringMin", "100"), ("luggage.ringMax", "50"), ("luggage.spawnSeconds", "1"), ("luggage.capPerHour", "99999"),
                 ("luggage.despawnSeconds", "5"), ("luggage.tierWeights", "1,2,x,4"), ("luggage.enabled", "false")):
        pp.setProperty(k, v)
    Cfg.apply(pp)
    cl = [int(Cfg.LG_RING_MIN), int(Cfg.LG_RING_MAX), int(Cfg.LG_SPAWN_S), int(Cfg.LG_CAP), int(Cfg.LG_DESPAWN_S), bool(Cfg.LG_ON)]
    Cfg.apply(Props())
    K.check(cl == [100, 100, 5, 1000, 60, False], "X14: clamps (ring max never under min, 5 s, cap 1000, despawn 60 s): %s" % cl)
    chk = [Cfg.check("luggage.tierWeights", "1,2,3"), Cfg.check("luggage.tierWeights", "60,28,10,2"), Cfg.check("luggage.coinZoneMult", "1,1,1,1,1"),
           Cfg.check("luggage.xp", "1,2,3,x"), Cfg.check("luggage.bags", "0.5,1,1.5,2")]
    K.check(chk[0] is not None and len(str(chk[0])) > 0 and (chk[1] is None or str(chk[1]) == "") and chk[2] is not None and len(str(chk[2])) > 0
            and chk[3] is not None and len(str(chk[3])) > 0 and (chk[4] is None or str(chk[4]) == ""),
            "X14: check(): four numbers per list row (3 or 5 numbers / a word refused): %s" % [None if c is None else str(c)[:40] for c in chk])
    dtx = str(Cfg.DEFAULTS)
    K.check(dtx.rstrip().endswith("luggage.ground=Soil_Grass,Soil_Dirt,Soil_Sand,Soil_Snow,Soil_Gravel,Soil_Mud,Soil_Needles,Soil_Ash,Soil_Pebbles,Rock_Stone,Rock_Sandstone")
            and dtx.count("\nluggage.") == 21, "X14: a fresh config.properties ends with the 21 luggage keys")
    LM = JClass(PKG + "ExpLgMig")
    K.check(("\n" + str(LM.MARK) + "\nluggage.shareSeconds=0\n") in dtx and "luggage.shareSeconds=20" not in dtx and LM.update(dtx) is None,
            "X14: 0.2.5 a fresh config.properties has luggage.shareSeconds=0 with the run-once marker right above it (never updated again)")
    CR = JClass(PKG + "CfgRows")
    rowtxt = []
    for f_ in CR.class_.getDeclaredFields():
        if JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()):
            f_.setAccessible(True)
            v_ = f_.get(None)
            if v_ is not None and f_.getType().isArray():
                rowtxt.extend(str(x) for x in v_ if x is not None)
    lg_rows = sorted(set(x for x in rowtxt if x.startswith("luggage.") and "=" not in x))
    K.check(len(lg_rows) == 21 and "Luggage" in rowtxt, "X14: Server Setup -> Exploration -> Luggage: 21 rows (%d) + the tab: %s" % (len(lg_rows), lg_rows))

    # ============================================================================ X15 wiring (bytecode)
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    CP.appendClassPath(JAR)
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def bc(cn, m):
        out_ = []
        for mm in CP.get(cn).getDeclaredMethods():
            if str(mm.getName()) == m:
                bos = JClass("java.io.ByteArrayOutputStream")()
                IP(JClass("java.io.PrintStream")(bos)).print_(mm)
                out_.append(str(bos.toString()))
        return "\n".join(out_)
    su, sd, tk = bc(PKG + "SkyyExplorationPlugin", "setup"), bc(PKG + "SkyyExplorationPlugin", "shutdown"), bc(PKG + "ExpTick", "second")
    K.check('"SkyyLuggage"' in su and "OpenCustomUIInteraction.registerCustomPageSupplier" in su and "LgUse.<init>" in su
            and "LgBreakSys.<init>" in su and "LgDamageSys.<init>" in su and "LgReg.DIR" in su and su.index("LgReg.DIR") < su.index("ExpCfg.load")
            and "LgCore.flushAll" in sd and "LgCore.second" in tk,
            "X15: setup() sets the luggage folder before the config load, registers the SkyyLuggage page + both block guards; shutdown() "
            "saves the registries; ExpTick calls LgCore.second")
    refs_ = set(str(x) for x in CP.get(PKG + "ExploreAdminCmd").getRefClasses())
    refs2 = set(str(x) for x in CP.get(PKG + "ExLuggageCmd").getRefClasses())
    K.check(PKG + "ExLuggageCmd" in refs_ and PKG + "ExLuggageListCmd" in refs2 and "luggage" in str(JClass(PKG + "ExAdminOps").help()),
            "X15: FIX /exploreadmin luggage (+ list) is a subcommand of /exploreadmin and listed in /exploreadmin help")
    K.check("ExpLgMig.migrate" in su and su.index("ExpCfg.FILE") < su.index("ExpLgMig.migrate") < su.index("ExpCfg.load") < su.index("CfgPub.start"),
            "X15: 0.2.5 setup() runs the one-time update after ExpCfg.FILE is set and BEFORE ExpCfg.load + CfgPub.start")
    us_ = bc(PKG + "LgCore", "use")
    K.check("LgCore.vanish" in us_ and "LgReg.save" in us_ and us_.rindex("LgCore.loot") < us_.index("LgCore.vanish"),
            "X15: 0.2.5 use() removes the block (vanish) only AFTER the loot, then saves")

    # ============================================================================ X16 ExpLgMig: the one-time luggage.shareSeconds 20 -> 0 update
    LM = JClass(PKG + "ExpLgMig")
    MK = str(LM.MARK)

    def upd(txt):
        r_ = LM.update(txt)
        return None if r_ is None else (str(r_[0]), str(r_[1]), None if r_[2] is None else str(r_[2]), [str(x) for x in r_[3]],
                                        None if r_[4] is None else str(r_[4]))
    cases = []
    for nl in ("\n", "\r\n"):
        src_ = "a=1\nluggage.ringMax=64\nluggage.shareSeconds=20\nluggage.respawnSeconds=1800\n".replace("\n", nl)
        exp_ = ("a=1\nluggage.ringMax=64\n" + MK + "\nluggage.shareSeconds=0\nluggage.respawnSeconds=1800\n").replace("\n", nl)
        cases.append(("old default (%r)" % nl, upd(src_), (exp_, "luggage.shareSeconds 20 -> 0", None, ["luggage.shareSeconds", "20", "0"], "20")))
    cases.append(("spaced separator kept", upd("luggage.shareSeconds = 20\n"), (MK + "\nluggage.shareSeconds = 0\n", "luggage.shareSeconds 20 -> 0", None,
                                                                                ["luggage.shareSeconds", "20", "0"], "20")))
    cases.append(("custom 45 kept", upd("x=1\nluggage.shareSeconds=45\n"), ("x=1\n" + MK + "\nluggage.shareSeconds=45\n", "",
                                                                            "luggage.shareSeconds=45 kept (custom) - the 0.2.5 default is 0", [], "45")))
    cases.append(("already 0 silent", upd("luggage.shareSeconds=0\n"), (MK + "\nluggage.shareSeconds=0\n", "", None, [], "0")))
    cases.append(("no line -> marker at the end", upd("a=1\nb=2\n"), ("a=1\nb=2\n" + MK + "\n", "", None, [], None)))
    cases.append(("no line, CRLF", upd("a=1\r\nb=2\r\n"), ("a=1\r\nb=2\r\n" + MK + "\r\n", "", None, [], None)))
    cases.append(("no line, no final break", upd("a=1"), ("a=1\n" + MK + "\n", "", None, [], None)))
    cases.append(("no line, CRLF, no final break", upd("a=1\r\nb=2"), ("a=1\r\nb=2\r\n" + MK + "\r\n", "", None, [], None)))
    cases.append(("empty file", upd(""), (MK + "\n", "", None, [], None)))
    cases.append(("two old lines", upd("luggage.shareSeconds=20\nluggage.shareSeconds=20\n"), (MK + "\nluggage.shareSeconds=0\nluggage.shareSeconds=0\n",
                                                                                               "luggage.shareSeconds 20 -> 0", None, ["luggage.shareSeconds", "20", "0"], "20")))
    cases.append(("last entry custom wins", upd("luggage.shareSeconds=20\nluggage.shareSeconds=30\n"),
                  (MK + "\nluggage.shareSeconds=20\nluggage.shareSeconds=30\n", "", "luggage.shareSeconds=30 kept (custom) - the 0.2.5 default is 0", [], "30")))
    cases.append(("a continued entry kept", upd("luggage.shareSeconds=2\\\n0\n"), (MK + "\nluggage.shareSeconds=2\\\n0\n", "",
                                                                                  "luggage.shareSeconds=20 kept (custom) - the 0.2.5 default is 0", [], "20")))
    cases.append(("a commented-out line is no entry", upd("#luggage.shareSeconds=20\n"), ("#luggage.shareSeconds=20\n" + MK + "\n", "", None, [], None)))
    # fixer 2026-10-09: a file ENDING inside a continued entry (dangling backslash) - the marker must not become part of that value -> top
    cases.append(("FIX dangling continuation at the end", upd("a=1\nb=2\\\n"), (MK + "\na=1\nb=2\\\n", "", None, [], None)))
    cases.append(("FIX dangling continuation, CRLF, no final break", upd("a=1\r\nb=2\\"), (MK + "\r\na=1\r\nb=2\\", "", None, [], None)))
    cases.append(("FIX continued entry closed before the end", upd("a=1\\\n2\nb=3\n"), ("a=1\\\n2\nb=3\n" + MK + "\n", "", None, [], None)))
    cases.append(("FIX escaped backslash is no continuation", upd("a=c:\\\\\n"), ("a=c:\\\\\n" + MK + "\n", "", None, [], None)))
    # ... and java.util.Properties reads the fixed file as before (a / b only, b = "2" - the marker is no part of any value)
    _pp = JClass("java.util.Properties")()
    _pp.load(JClass("java.io.StringReader")(str(LM.update("a=1\nb=2\\\n")[0])))
    K.check(sorted(str(x) for x in _pp.stringPropertyNames()) == ["a", "b"] and str(_pp.getProperty("b")) == "2",
            "X16: FIX a file ending in a dangling backslash: the marker goes to the top, java.util.Properties still reads a=1 b=2: %s" % _pp)
    cases.append(("marked file untouched", upd("x=1\n" + MK + "\nluggage.shareSeconds=20\n"), None))
    bad_ = [(n_, g_, e_) for n_, g_, e_ in cases if g_ != e_]
    for b_ in bad_[:4]:
        print("   X16", b_[0], "got", repr(b_[1])[:300], "want", repr(b_[2])[:300])
    K.check(not bad_, "X16: ExpLgMig.update (pure text step, %d cases: old default LF / CRLF / spaced, custom kept, already 0, no line -> "
            "marker at the end (LF / CRLF / no final break / empty), duplicates, the last entry decides, a continued entry, a comment, a "
            "marked file): wrong %s" % (len(cases), [b_[0] for b_ in bad_]))
    # migrate() on real files (the kit's History + change log; ExpCfg.FILE pointed at a scratch copy)
    mh = os.path.join(SCRATCH, "x-mig")
    shutil.rmtree(mh, ignore_errors=True)
    os.makedirs(mh)
    cfgp = os.path.join(mh, "config.properties")
    old_b = b"# head\r\nluggage.enabled=true\r\nluggage.shareSeconds=20\r\nadmin.log=true\r\n"
    open(cfgp, "wb").write(old_b)
    fold = Cfg.FILE
    Cfg.FILE = Paths.get(cfgp)
    m1 = str(LM.migrate())
    new_b = open(cfgp, "rb").read()
    hist = os.path.join(mh, "config-history")
    baks = sorted(f_ for f_ in os.listdir(hist) if f_.endswith(".bak")) if os.path.isdir(hist) else []
    chlog = open(os.path.join(mh, "config-changes.log"), encoding="utf8").read() if os.path.isfile(os.path.join(mh, "config-changes.log")) else ""
    m2 = str(LM.migrate())
    new_b2 = open(cfgp, "rb").read()
    K.check(new_b == ("# head\r\nluggage.enabled=true\r\n" + MK + "\r\nluggage.shareSeconds=0\r\nadmin.log=true\r\n").encode("ascii")
            and len(baks) == 1 and open(os.path.join(hist, baks[0]), "rb").read() == old_b and "\tSkyyExploration 0.2.5\t-\tupdate\tluggage.shareSeconds\t20\t0\tok" in chlog
            and "luggage.shareSeconds 20 -> 0" in m1 and m2 == "" and new_b2 == new_b and any("updated for 0.2.5" in m for m in ourlogs()),
            "X16: migrate() on a CRLF file: 20 -> 0 + the marker (every other byte + CRLF kept), the old file in config-history (verified), one "
            "Undo-able change-log line, an INFO line; a second start changes nothing: %s | %r | %s" % (m1[:90], chlog[-120:], baks))
    # History cannot be kept -> nothing written (WARN); a directory instead of a file -> the catch (WARN); no file -> nothing
    mh2 = os.path.join(SCRATCH, "x-mig2")
    shutil.rmtree(mh2, ignore_errors=True)
    os.makedirs(mh2)
    cfg2 = os.path.join(mh2, "config.properties")
    open(cfg2, "wb").write(b"luggage.shareSeconds=20\n")
    open(os.path.join(mh2, "config-history"), "w").write("not a folder")
    Cfg.FILE = Paths.get(cfg2)
    m3 = str(LM.migrate())
    keep2 = open(cfg2, "rb").read()
    os.makedirs(os.path.join(mh2, "adir"))
    Cfg.FILE = Paths.get(os.path.join(mh2, "adir"))
    m4 = str(LM.migrate())
    Cfg.FILE = Paths.get(os.path.join(mh2, "missing.properties"))
    m5 = str(LM.migrate())
    Cfg.FILE = None
    m6 = str(LM.migrate())
    Cfg.FILE = fold
    K.check(m3 == "" and keep2 == b"luggage.shareSeconds=20\n" and any("NOT updated for 0.2.5" in m for m in ourlogs()) and m4 == ""
            and any("could not update config.properties for 0.2.5" in m for m in ourlogs()) and m5 == "" and m6 == ""
            and not os.path.exists(os.path.join(mh2, "missing.properties")),
            "X16: History not kept -> the file is NOT written (WARN, the next start retries); an unreadable path -> WARN, nothing; no file / no "
            "path -> nothing (a fresh file comes from the defaults, already 0 + marked)")
    K.save()


# ====================================================================================================== C
def run_compare(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_
    pa, pb = pool_of(OLD_JAR), pool_of(JAR)

    def members(p_, cn):
        c_ = p_.get(cn)
        d_ = {}

        def code(b_):
            mi_ = b_.getMethodInfo()
            ca_ = mi_.getCodeAttribute()
            if ca_ is None:
                return ""
            it_ = ca_.iterator()
            lines_ = []
            while it_.hasNext():
                pos_ = it_.next()
                lines_.append(re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, mi_.getConstPool()))).replace("ldc_w ", "ldc "))
                # an ldc that became ldc_w (more constants) shifts later offsets: compare jumps without their targets
                lines_[-1] = re.sub(r"^((?:if\w*|goto\w*) )\d+$", r"\1L", lines_[-1])
            return "\n".join(lines_)
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature())
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        if c_.getClassInitializer() is not None:
            d_["<clinit>"] = code(c_.getClassInitializer())
        return d_
    na, nb = jar_classes(OLD_JAR), jar_classes(JAR)
    added = sorted(x[len(PKG):] for x in set(nb) - set(na))
    K.check(added == NEW_CLASSES and not (set(na) - set(nb)), "C: ExpLgMig (the one-time update) added, none removed: %s" % added)
    diffs = {}
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn), members(pb, cn)
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(PKG):]] = sorted(("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd)
    print("C. class compare 0.2.4 -> 0.2.5: %s" % json.dumps(diffs, sort_keys=True))
    if "ExpCfg" in diffs and "~m dlist" in diffs["ExpCfg"]:
        ma, mb = members(pa, PKG + "ExpCfg"), members(pb, PKG + "ExpCfg")
        k_ = [k for k in ma if k.startswith("m dlist(")][0]
        import difflib
        print("C. dlist:", list(difflib.unified_diff(ma[k_].splitlines(), mb[k_].splitlines(), lineterm="", n=0))[:12])
    allowed = {
        # 0.2.5: the shareSeconds default 20 -> 0 (field initialiser, apply's fallback, the DEFAULTS text in <clinit>)
        "ExpCfg": {"~<clinit>", "~m apply", "~m load"},
        # the vanish (+ poof) and the claim's 'already claimed' / 'cannot be claimed' lines
        "LgApi": {"+m poof"}, "LgCore": {"+m vanish", "~m sweep", "~m use"},
        # the poof; the placement sound SFX_Chest_Wooden_Close -> SFX_Cloth_Land (sound's ldc), PSND's initialiser
        "LgEng": {"+f PSND", "+m poof", "~<clinit>", "~m sound"},
        "SkyyExplorationPlugin": {"~m setup"},
        # the config kit: the rows' help text + version text (CfgRows / CfgFn), KEEP 20 -> 10 (CfgHist)
        "CfgRows": {"~<clinit>", "~m header"}, "CfgFn": {"~m opExport"}, "CfgHist": {"~m compact", "~m snapshot", "~m versions"},
    }
    extra = dict((k, sorted(set(v) - allowed.get(k, set()))) for k, v in diffs.items() if set(v) - allowed.get(k, set()))
    K.check(not extra and {"ExpCfg", "LgApi", "LgCore", "LgEng", "SkyyExplorationPlugin", "CfgHist"} <= set(diffs),
            "C: only the listed members differ (the share default, the vanish + poof, the placement sound, setup's update call, the kit's "
            "rows / version text / KEEP 10): unexpected %s" % extra)
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    ed = sorted(n for n in set(za.namelist()) | set(zb.namelist()) if not n.endswith(".class") and (n not in za.namelist() or n not in zb.namelist() or za.read(n) != zb.read(n)))
    exp = sorted(["manifest.json", "Server/Languages/en-US/server.lang"] + ["Server/Item/Items/SkyyExploration/%s.json" % b for b in LG_IDS])
    K.check(ed == exp, "C: non-class entries: the 4 luggage blocks + their names + manifest.json: %s" % ed)
    K.save(diffs=diffs)


# ====================================================================================================== D
def run_live(out, home):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    Paths = JClass("java.nio.file.Paths")
    Cfg, Store_, Chest, Spot, Reg = (JClass(PKG + n) for n in ("ExpCfg", "ExpStore", "ChestReg", "SpotReg", "LgReg"))
    base = Paths.get(home)

    def snap():
        out_ = {}
        for r_, ds_, fs_ in os.walk(home):
            for f_ in fs_:
                p_ = os.path.join(r_, f_)
                out_[os.path.relpath(p_, home)] = open(p_, "rb").read()
        return out_
    before = snap()
    Mig = JClass(PKG + "ExpLgMig")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyExpLive")
    mk = str(Mig.MARK)
    old_cfg = before.get("config.properties", b"")
    has_line = any(ln.strip().startswith(b"luggage.shareSeconds") for ln in old_cfg.splitlines())
    crlf = b"\r\n" in old_cfg
    K.notes.append("D: the live copy: %d files, config.properties %d bytes, %s, a luggage.shareSeconds line: %s" % (
        len(before), len(old_cfg), "CRLF" if crlf else "LF", has_line))
    snaps = []
    for step in (1, 2):
        Cfg.FILE = base.resolve("config.properties")
        Store_.DIR = base.resolve("players")
        Chest.DIR = base.resolve("chests")
        Spot.DIR = base.resolve("worlds")
        Reg.DIR = base.resolve("luggage")
        mg = str(Mig.migrate())
        sm = str(Cfg.load())
        Chest.loadAll()
        Spot.loadAll()
        snaps.append((snap(), mg, sm))
    a1, mg1, sm1 = snaps[0]
    a2, mg2, sm2 = snaps[1]
    changed1 = sorted(k for k in set(a1) | set(before) if a1.get(k) != before.get(k))
    hist_new = sorted(k for k in changed1 if k.startswith("config-history"))
    baks = [k for k in hist_new if k.endswith(".bak")]
    if not has_line:
        nlb = b"\r\n" if crlf else b"\n"
        exp_cfg = old_cfg + (b"" if (not old_cfg or old_cfg.endswith(b"\n")) else nlb) + mk.encode("ascii") + nlb
        K.check(a1.get("config.properties") == exp_cfg and "no luggage.shareSeconds line on the old default" in mg1,
                "D start 1: the live file has NO luggage.shareSeconds line -> nothing changes but the run-once marker at the end (%s)" % mg1[:120])
    else:
        K.check(mk.encode("ascii") in a1.get("config.properties", b"") and mg1 != "", "D start 1: the live file's luggage.shareSeconds line was handled: %s" % mg1)
    K.check(set(changed1) - set(hist_new) == {"config.properties"} and len(baks) == 1 and a1[baks[0]] == old_cfg
            and all(a1[k] == before[k] for k in before if k != "config.properties"),
            "D start 1: only config.properties changed (+ its verified History copy %s); every other file byte-identical (players, chests, "
            "worlds, the luggage registry): %s" % (baks, changed1))
    K.check(a2 == a1 and mg2 == "", "D start 2: nothing changes (the marker is there): %s" % sorted(k for k in set(a1) | set(a2) if a1.get(k) != a2.get(k)))
    K.check(bool(Cfg.LG_ON) and int(Cfg.LG_CAP) == 8 and int(Cfg.LG_RESPAWN_S) == 1800 and list(Cfg.LG_COIN_MAX) == [30, 60, 150, 400]
            and int(Cfg.LG_SHARE_S) == 0,
            "D: the luggage rows read their defaults - luggage.shareSeconds 0 (claimed luggage vanishes at once)")
    K.save()


# ====================================================================================================== AA
def run_audit(out):
    from jpype import JClass
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR], verify=False)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    CP.appendClassPath(JAR)
    MH = JClass("java.lang.invoke.MethodHandles")
    MTc, CPool, JMod_ = JClass("java.lang.invoke.MethodType"), JClass("javassist.bytecode.ConstPool"), JClass("java.lang.reflect.Modifier")
    XOPS = {0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5, 0x12, 0x13}

    def jc(n_):
        return Cls.forName(n_.replace("/", "."), False, loader)
    refused, n = [], 0
    for cn in jar_classes(JAR):
        D = jc(cn)
        lk = MH.privateLookupIn(D, MH.lookup())
        cc = CP.get(cn)
        sup = str(cc.getSuperclass().getName()) if cc.getSuperclass() is not None else None
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
                if op == 0xba:
                    refused.append("%s invokedynamic" % cn)
                    continue
                idx = it_.byteAt(p_ + 1) if op == 0x12 else it_.u16bitAt(p_ + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != CPool.CONST_Class:
                    continue
                n += 1
                try:
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        lk.accessClass(jc(str(cp.getClassInfo(idx))))
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        C_ = jc(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", loader).parameterType(0)
                        if op in (0xb2, 0xb3):
                            lk.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lk.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)), str(cp.getInterfaceMethodrefType(idx))
                        else:
                            cname, name, desc = str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx))
                        C_ = jc(cname)
                        mt = MTc.fromMethodDescriptorString(desc, loader)
                        if name == "<init>" and in_ctor and cname in (sup, cn):
                            md = int(C_.getDeclaredConstructor(mt.parameterArray()).getModifiers())
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn):
                                raise ValueError("constructor not accessible")
                        elif name == "<init>":
                            lk.findConstructor(C_, mt)
                        elif op == 0xb8:
                            lk.findStatic(C_, name, mt)
                        elif op == 0xb7:
                            lk.findSpecial(C_, name, mt, D)
                        else:
                            lk.findVirtual(C_, name, mt)
                except Exception as ex_:
                    if "caller-sensitive" not in str(ex_):
                        refused.append("%s: %s" % (cn, ex_))
    json.dump({"refused": refused, "refs": n}, open(out, "w"))


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
    for flag, fn in (("--mkfake", lambda: run_mkfake(FAKE_DIR)), ("--verify", lambda: run_verify(arg("--out"))),
                     ("--engine", lambda: run_engine(arg("--out"))), ("--compare", lambda: run_compare(arg("--out"))),
                     ("--live", lambda: run_live(arg("--out"), arg("--live"))), ("--audit", lambda: run_audit(arg("--out")))):
        if flag in sys.argv:
            try:
                fn()
            except Exception:
                import traceback
                traceback.print_exc()
                sys.exit(1)
            return
    sc = os.path.realpath(SCRATCH)
    _sr = os.path.realpath(os.path.join(TOOLS, "dev", "scratch")) + os.sep      # any task folder: tools/dev/scratch/<task>/<sub>
    assert sc.startswith(_sr) and len(os.path.relpath(sc, _sr).split(os.sep)) >= 2, "scratch must be tools/dev/scratch/<task>/<sub>"
    for j in (JAR, OLD_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    try:
        pr = child(env, "--mkfake")
        check(pr.returncode == 0, "F: the stand-ins were compiled")
        for label, flag in (("verify", "--verify"), ("engine", "--engine"), ("compare", "--compare")):
            if label in ("engine",) and "--skip-engine" in sys.argv:
                continue
            out = os.path.join(SCRATCH, label + ".json")
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        home = os.path.join(SCRATCH, "live")
        shutil.copytree(LIVE_DIR, home)
        out = os.path.join(SCRATCH, "live.json")
        pr = child(env, "--live", home, "--out", out)
        check(pr.returncode == 0, "D: the child exited cleanly")
        take(out, "live")
        outa = os.path.join(SCRATCH, "audit.json")
        pa = child(env, "--audit", "--out", outa)
        check(pa.returncode == 0 and os.path.isfile(outa), "AA: the audit child ran")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            check(not a["refused"] and a["refs"] > 1000, "AA: engine-access audit: %d references, refused %s" % (a["refs"], a["refused"][:5]))
            print("AA. engine-access audit: %d references, %d refused" % (a["refs"], len(a["refused"])))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyExploration %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
