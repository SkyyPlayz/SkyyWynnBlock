"""Bare-JVM harness for SkyyBazaar 0.1.5 (sell from the Magic Bags through SkyySacks 0.7.13's bridge, the real Hytale max stack on Buy / Sell
<stack>, Tree Sap default 12 - tools/bazaar_0_1_5_patch.py). Runs the 0.1.5 jar TOGETHER with the real SkyySacks 0.7.13 jar in one JVM, so every
sale from the bags goes through the real SackBridge / SackPool / BagMirror code.

    python SkyyBazaar/test_skyybazaar_0.1.5.py [--jar <0.1.5 jar>] [--old <0.1.4 jar>] [--sacks <SkyySacks 0.7.13 jar>]
                                               [--live <Skyy_SkyyBazaar folder>] [--livesacks <Skyy_SkyySacks folder>] [--dir <scratch>] [--keep]

Build first (python tools/bazaar_0_1_5_patch.py + python SkyyBazaar/build_skyybazaar_0.1.5.py, python tools/sacks_0_7_13_patch.py +
python SkyySacks/build_skyysacks_0.7.13.py). The parent copies the live data folders (read only; default: the "HUD mod" world's
mods/Skyy_SkyyBazaar and mods/Skyy_SkyySacks) into the scratch folder (default tools/dev/scratch/bazaar015/bz-run, deleted at the end unless
--keep) and starts a child: one fresh JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, java.io.tmpdir / TEMP / TMP in the scratch
folder; HytaleServer.jar + the 0.1.5 jar + the SkyySacks 0.7.13 jar + tools/javassist.jar). The 0.1.4 jar loads in its own class loader.
Stand-ins (a bare JVM has no ECS / universe): an Item asset store (Item.UNKNOWN for the product ids + REAL engine Items decoded through
Item.CODEC with their Parent chain for the max-stack checks), an Inventory of three SimpleItemContainers, a Player allocated without its
constructor, a PlayerRef that records its messages, a Store whose getComponent answers the test player (page clicks), the coins bridge as
generated Java Functions (a purse map; an "add fails" switch), SackBridge.PLAYERS = a Java Function answering the test player.
  A  every 0.1.5 class + every SkyySacks 0.7.13 class loads and verifies (-Xverify:all); the 0.1.4 jar in its own loader
  B  class compare 0.1.4 -> 0.1.5: new Bags; changed Trader, BzPage, TradeResult, Catalog (only its seed table: exactly the sap line) and the
     classes that carry the version text; every other class byte-identical (Coins, Market, Inv, Product, BzUtil, the admin commands, BzTick ...)
  X  engine-access audit on the jar bytes - 0 refused; control refused
  F  fresh start: 415 products, Tree Sap seeded at 12, SEED = 0.1.4's except the sap line, SEED013 / OLD_SEED = 0.1.4's (sap 4 there)
  P  sap with saved prices: the live data (Skyy's /bazaaradmin price ... 12) started twice -> 12, no file changed; the live copy with the sap
     line at 4 (the old default) / 20 (a hand price) -> kept as it is (no migration); 0.1.2-era data (the live products.properties.v012bak,
     no markers) -> the 0.1.3 update moves sap 4 -> 12, a hand-set sap 5 there stays 5
  M  max stack: every product's Item decoded through the engine's Item.CODEC with its Parent chain (decodeAndInheritJsonAsset, then the
     engine's own processConfig default) -> Trader.stack(id) = the Assets.zip expectation for all 415 (ores 25, blocks 100, food 25,
     inherit-only items such as Rock_Gem_Diamond <- Rock_Gem_Emerald); unknown id / 0 -> 100; no product is a tool / weapon / armor (the
     reduced decode is exact for them); the page shows "Buy 25" / "Sell 25" and "for 25" for Copper Ore, "Buy 100" for Tree Sap
  K  selling with the bags (real SkyySacks 0.7.13): Sell 1 / Sell <stack> / Sell all / the custom Sell (Trader.sellN and the page's armed
     max flow) / Sell inventory with items split between the inventory and the bags - inventory first, then the bags; the coins paid always =
     the quote of what really left (computed before the trade); pool + file + trades.log ("bags=") follow; partial availability (a bridge
     that removes only half; a count that over-reports); a bag not carried; SkyySacks absent / older (no take) = 0.1.4 behaviour; two sells in
     one tick and two Java threads selling 1 at a time (conservation); the payment failing (bag part back through sacks:fn:put, the rest into
     the inventory; put missing -> all into the inventory); a Magic Bag product line refused everywhere and never sold by Sell inventory;
     the page (cell counts, "You hold N (M in your bags)", Sell inventory's confirm text, page clicks buystk / sellstk / sellinv)
  L  money loops on the 0.1.5 runtime table (the build's check_assets + loop_check at every premium 0..22): none; sap 12 does not open one
  S  start twice on scratch COPIES of the live data (Bazaar + Sacks), then a real Sell <stack> of Tree Sap by the live player from the
     inventory + the copy's bag pool: exactly the sap line of that pool file, market.properties and trades.log change
Exit code 1 on any failure. Live data is only READ (copied). Nothing is deployed.
"""
import os, sys, re, ast, json, shutil, zipfile, math, subprocess, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION, SACKS_VERSION = "0.1.5", "0.1.4", "0.7.13"
PKG = "com.skyy.bazaar."
SCRIPT = os.path.join(HERE, "build_skyybazaar_%s.py" % VERSION)
MARK = ".skyybazaar-0.1.5-harness"
N_PROD = 415
SAP = "Ingredient_Tree_Sap"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH_ROOT = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.realpath(os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "bazaar015", "bz-run"))))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyBazaar-%s.jar" % OLD_VERSION)))
SACKS = os.path.abspath(arg("--sacks", os.path.join(ROOT, "SkyySacks", "SkyySacks-%s.jar" % SACKS_VERSION)))
HYTALE = os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale")
LIVE = os.path.abspath(arg("--live", os.path.join(HYTALE, "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyBazaar")))
LIVES = os.path.abspath(arg("--livesacks", os.path.join(HYTALE, "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySacks")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL:", what)
    return bool(cond)


def build_namespace():
    """the build script's own tables + functions, read with ast (never imported: importing would run the build)"""
    src = open(SCRIPT, encoding="utf8").read()
    t = ast.parse(src)
    want_f = {"_load_json", "check_assets", "load_assets", "asset_model", "processed_table", "proc_order", "fuel_list", "auto_prices", "loop_check"}
    want_v = {"SPREAD", "BAG_TABS", "ALL_OF_BAG", "SKIP", "NOSRC", "PREMIUM_BENCHES", "PREMIUM_ITEMS", "PREMIUM_DEF", "PREMIUM_MIN",
              "PREMIUM_MAX", "AUTO", "PRODUCTS", "EXTRA_TABS", "PRODUCTS_012", "PRICE_014", "PRICE_015"}
    body, got_f, got_v = [], set(), set()
    for n in t.body:
        if isinstance(n, ast.FunctionDef) and n.name in want_f:
            body.append(n)
            got_f.add(n.name)
        elif isinstance(n, ast.Assign):
            names = [x.id for x in n.targets if isinstance(x, ast.Name)] + [e.id for x in n.targets if isinstance(x, ast.Tuple)
                                                                               for e in x.elts if isinstance(e, ast.Name)]
            if set(names) & want_v:
                body.append(n)
                got_v.update(names)
    assert want_f <= got_f and want_v <= got_v, (want_f - got_f, want_v - got_v)
    import skyybuild as B
    ns = {"os": os, "re": re, "json": json, "zipfile": zipfile, "math": math, "collections": collections, "ast": ast, "HERE": HERE,
          "ASSETS": os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")}
    exec(compile(ast.Module(body=body, type_ignores=[]), SCRIPT, "exec"), ns)
    return ns


# ============================================================================================================== child
def run():
    import jpype
    import skyybuild as B
    import skyyui as SUI
    SUI.verify()
    from jpype import JClass, JArray, JShort, JString, JInt, JObject, JImplements, JOverride
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, JAR, SACKS, B.JAVASSIST], convertStrings=True)
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    URL, UCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
    NS = build_namespace()

    # ---------------- A. load + verify
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(JAR).namelist() if n.endswith(".class")]
    snames = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(SACKS).namelist() if n.endswith(".class")]
    for n in names + snames:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("load " + n + ": " + str(e))
            print("LOAD FAIL", n, e)
    old_loader = UCL(JArray(URL)([File(OLD).toURI().toURL(), File(B.SERVER_JAR).toURI().toURL()]),
                     JClass("java.lang.ClassLoader").getPlatformClassLoader())
    old_names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(OLD).namelist() if n.endswith(".class")]
    for n in old_names:
        try:
            Cls.forName(n, False, old_loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("load %s %s: %s" % (OLD_VERSION, n, e))
    print("A. loaded + verified %d classes of SkyyBazaar %s and %d of SkyySacks %s (-Xverify:all), %d of %s (own loader)"
          % (len(names), VERSION, len(snames), SACKS_VERSION, len(old_names), OLD_VERSION))
    if FAILS:
        return

    # ---------------- B. class compare 0.1.4 -> 0.1.5
    za, zb = zipfile.ZipFile(OLD), zipfile.ZipFile(JAR)
    ca = dict((n.split("/")[-1][:-6], za.read(n)) for n in za.namelist() if n.endswith(".class"))
    cb = dict((n.split("/")[-1][:-6], zb.read(n)) for n in zb.namelist() if n.endswith(".class"))
    check(sorted(cb) == sorted(list(ca) + ["Bags"]), "B: the 0.1.4 classes + Bags: %s / %s" % (sorted(set(cb) - set(ca)), sorted(set(ca) - set(cb))))
    ob, nb = OLD_VERSION.encode(), VERSION.encode()
    same = sorted(c for c in ca if ca[c] == cb.get(c))
    vers = sorted(c for c in ca if c in cb and ca[c] != cb[c] and ca[c].replace(ob, nb) == cb[c])
    other = sorted(c for c in ca if c in cb and ca[c] != cb[c] and c not in vers)
    check(other == ["BzPage", "Catalog", "TradeResult", "Trader"], "B: changed beyond the version text: exactly BzPage, Catalog, TradeResult, Trader (%s)" % other)
    check(set(vers) <= {"SkyyBazaarPlugin", "CfgRows", "CfgFn", "CfgFile", "CfgPub"}, "B: version-text-only classes: %s" % vers)
    for c in ("Coins", "Market", "Inv", "Product", "BzUtil", "BzCmd", "BzPageFactory", "BzAdminCmd", "BzAdmPriceCmd", "BzAdmPriceShowCmd",
              "BzAdmReloadCmd", "BzAdmResetCmd", "BzAdmInfoCmd", "BzTick", "BzCfg"):
        check(c in same, "B: %s byte-identical %s -> %s" % (c, OLD_VERSION, VERSION))
    OldCat = JClass(Cls.forName("com.skyy.bazaar.Catalog", True, old_loader))
    Cat = JClass(PKG + "Catalog")
    so_, sn_ = [str(x) for x in OldCat.SEED], [str(x) for x in Cat.SEED]
    dif = [(a, b) for a, b in zip(so_, sn_) if a != b]
    check(len(so_) == len(sn_) == N_PROD and dif == [("Ingredient_Tree_Sap=Foraging,4,Tree Sap", "Ingredient_Tree_Sap=Foraging,12,Tree Sap")],
          "B: Catalog.SEED = 0.1.4's except the sap line 4 -> 12: %s" % dif[:3])
    for fld in ("SEED013", "OLD_SEED", "M14_ID", "M14_TXT", "M14_OTXT", "TAB_ORDER", "EXTRA_ID", "EXTRA_TAB", "EDGES"):
        check([str(x) for x in getattr(OldCat, fld)] == [str(x) for x in getattr(Cat, fld)], "B: Catalog.%s identical to 0.1.4's" % fld)
    check(str(OldCat.PROC_SPEC) == str(Cat.PROC_SPEC) and str(OldCat.FUEL_SPEC) == str(Cat.FUEL_SPEC), "B: processed / fuel tables identical")
    man = json.loads(zb.read("manifest.json"))
    check(man["Version"] == VERSION and man["Main"] == "com.skyy.bazaar.SkyyBazaarPlugin", "B: manifest %s" % man["Version"])
    print("B. class compare %s -> %s: %d identical, %d version-text only (%s), changed BzPage / Catalog (seed: the sap line) / TradeResult / Trader, + Bags"
          % (OLD_VERSION, VERSION, len(same), len(vers), ", ".join(vers)))

    # ---------------- X. engine-access audit
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    jp.appendClassPath(JAR)
    jp.appendClassPath(SACKS)
    Mod = JClass("javassist.Modifier")
    CPo = JClass("javassist.bytecode.ConstPool")
    CF, DI, BI = JClass("javassist.bytecode.ClassFile"), JClass("java.io.DataInputStream"), JClass("java.io.ByteArrayInputStream")
    AOPS = {0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5, 0x12, 0x13}
    pkgof = lambda n: n.rsplit(".", 1)[0] if "." in n else ""

    def elem(n):
        n2 = n.replace("/", ".").lstrip("[")
        if n2.startswith("L") and n2.endswith(";"):
            return n2[1:-1]
        return None if len(n2) == 1 and n.startswith("[") else n2

    def audit(items):
        refused, used, seen = [], set(), 0
        for D, cf in items:
            dn = str(D.getName())
            for mi in cf.getMethods():
                ca_ = mi.getCodeAttribute()
                if ca_ is None:
                    continue
                cp, it = mi.getConstPool(), ca_.iterator()
                while it.hasNext():
                    pos = it.next()
                    op = it.byteAt(pos)
                    if op not in AOPS:
                        continue
                    if op == 0xba:
                        refused.append("invokedynamic in " + dn)
                        continue
                    idx = it.byteAt(pos + 1) if op == 0x12 else it.u16bitAt(pos + 1)
                    tag = cp.getTag(idx)
                    if op in (0x12, 0x13) and tag != CPo.CONST_Class:
                        continue
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        cname, member = str(cp.getClassInfo(idx)), None
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        cname, member = str(cp.getFieldrefClassName(idx)), ("field", str(cp.getFieldrefName(idx)), str(cp.getFieldrefType(idx)))
                    elif tag == CPo.CONST_InterfaceMethodref:
                        cname, member = str(cp.getInterfaceMethodrefClassName(idx)), ("method", str(cp.getInterfaceMethodrefName(idx)), str(cp.getInterfaceMethodrefType(idx)))
                    else:
                        cname, member = str(cp.getMethodrefClassName(idx)), ("method", str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                    seen += 1
                    try:
                        en = elem(cname)
                        if en is not None and pkgof(en) != pkgof(dn) and not Mod.isPublic(jp.get(en).getModifiers()):
                            refused.append("%s: class %s not public" % (dn, en))
                        if member is None:
                            continue
                        kind, name, desc = member
                        Cc = jp.get("java.lang.Object" if cname.startswith("[") else cname)
                        x = Cc.getField(name, desc) if kind == "field" else (Cc.getConstructor(desc) if name == "<init>" else Cc.getMethod(name, desc))
                        md, decl = x.getModifiers(), x.getDeclaringClass()
                        dcn = str(decl.getName())
                        if Mod.isPublic(md) or (pkgof(dcn) == pkgof(dn) and not Mod.isPrivate(md)):
                            continue
                        ok = (dcn == dn) if Mod.isPrivate(md) else (bool(D.subclassOf(decl)) if Mod.isProtected(md) else False)
                        if ok:
                            used.add("%s.%s" % (dcn.rsplit(".", 1)[-1], name))
                        else:
                            refused.append("%s: %s %s.%s%s" % (dn, Mod.toString(md), dcn, name, desc))
                    except Exception as e:
                        refused.append("%s: %s %s does not resolve: %s" % (dn, cname, member, e))
        return refused, used, seen
    items = [(jp.get(n[:-6].replace("/", ".")), CF(DI(BI(zb.read(n))))) for n in zb.namelist() if n.endswith(".class")]
    refused, used, seen = audit(items)
    check(not refused and seen > 2000, "X: access audit: %d references, refused %s" % (seen, refused[:5]))
    ctl = jp.makeClass(PKG + "AuditControl")
    ctl.addMethod(JClass("javassist.CtNewMethod").make(
        "public static void bad(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) { p.close(); }", ctl))
    r2, _u2, _s2 = audit([(ctl, CF(DI(BI(ctl.toBytecode()))))])
    check(len(r2) == 1 and "close" in r2[0], "X: control refused: %s" % r2)
    print("X. access audit: %d references, 0 refused; non-public used from their subclass: %s; control refused" % (seen, ", ".join(sorted(used))))

    # ---------------- stand-ins
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyBzFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(CtC.make("public SkyyBzFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    FAKEC = fake.toClass(AS.class_)
    store = us.allocateInstance(FAKEC)
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    DAMN = "com.hypixel.hytale.assetstore.map.DefaultAssetMap"
    ITMN = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
    kmap = jp.makeClass("com.hypixel.hytale.assetstore.map.SkyyBzKnownMap", jp.get(DAMN))
    kmap.addField(CtF.make("public static final java.util.HashSet KNOWN = new java.util.HashSet();", kmap))
    kmap.addField(CtF.make("public static final java.util.HashMap REAL = new java.util.HashMap();", kmap))
    kmap.addConstructor(CtC.make("public SkyyBzKnownMap() { super(); }", kmap))
    kmap.addMethod(CtM.make(
        "public com.hypixel.hytale.assetstore.JsonAsset getAsset(Object key) { if (key != null && REAL.containsKey(key)) return "
        "(com.hypixel.hytale.assetstore.JsonAsset) REAL.get(key); if (key != null && KNOWN.contains(key)) return %s.UNKNOWN; "
        "return super.getAsset(key); }" % ITMN, kmap))
    KMap = JClass(kmap.toClass(JClass(DAMN).class_))
    fm.set(store, KMap())
    ITM = JClass(ITMN)
    fi_ = ITM.class_.getDeclaredField("ASSET_STORE")
    fi_.setAccessible(True)
    fi_.set(None, store)
    INVN = "com.hypixel.hytale.server.core.inventory.Inventory"
    ICN = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
    tinv = jp.makeClass("com.hypixel.hytale.server.core.inventory.SkyyBzTestInv", jp.get(INVN))
    for f in ("s", "h", "b"):
        tinv.addField(CtF.make("public %s %s;" % (ICN, f), tinv))
    tinv.addConstructor(CtC.make("public SkyyBzTestInv(%s s, %s h, %s b) { super(); this.s = s; this.h = h; this.b = b; }" % (ICN, ICN, ICN), tinv))
    for m, f in (("getStorage", "s"), ("getHotbar", "h"), ("getBackpack", "b")):
        tinv.addMethod(CtM.make("public %s %s() { return this.%s; }" % (ICN, m, f), tinv))
    TInv = JClass(tinv.toClass(JClass(INVN).class_))
    PRN = "com.hypixel.hytale.server.core.universe.PlayerRef"
    tpr = jp.makeClass("com.hypixel.hytale.server.core.universe.SkyyBzTestPR", jp.get(PRN))
    tpr.addField(CtF.make("public static final java.util.ArrayList SAID = new java.util.ArrayList();", tpr))
    tpr.addMethod(CtM.make("public void sendMessage(com.hypixel.hytale.server.core.Message m) { SAID.add(m == null ? null : m.getRawText()); }", tpr))
    TPR = JClass(tpr.toClass(JClass(PRN).class_))
    # a Store whose getComponent answers the test player (page clicks: handleDataEvent reads the Player from the store)
    STN = "com.hypixel.hytale.component.Store"
    tst = jp.makeClass("com.hypixel.hytale.component.SkyyBzTestStore", jp.get(STN))
    tst.addField(CtF.make("public static volatile Object P;", tst))
    tst.addMethod(CtM.make("public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, "
                           "com.hypixel.hytale.component.ComponentType t) { return (com.hypixel.hytale.component.Component) P; }", tst))
    tst.addMethod(CtM.make("public boolean isInThread() { return true; }", tst))
    TStore = JClass(tst.toClass(JClass(STN).class_))
    TSTORE = us.allocateInstance(TStore.class_)
    EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    fem = EM.class_.getDeclaredField("instance")
    fem.setAccessible(True)
    if fem.get(None) is None:
        try:
            fem.set(None, us.allocateInstance(EM.class_))
        except Exception:
            us.putObject(us.staticFieldBase(fem), us.staticFieldOffset(fem), us.allocateInstance(EM.class_))
    # the coins bridge as Java Functions (thread-safe; FAILADD = coins:fn:add refuses)
    tcn = jp.makeClass(PKG + "SkyyBzTestCoins")
    tcn.addInterface(jp.get("java.util.function.Function"))
    tcn.addField(CtF.make("public static final java.util.concurrent.ConcurrentHashMap P = new java.util.concurrent.ConcurrentHashMap();", tcn))
    tcn.addField(CtF.make("public static volatile boolean FAILADD = false;", tcn))
    tcn.addField(CtF.make("public int mode;", tcn))
    tcn.addConstructor(CtC.make("public SkyyBzTestCoins(int mode) { this.mode = mode; }", tcn))
    tcn.addMethod(CtM.make("""public static synchronized long bal(String k) { Long v = (Long) P.get(k); return v == null ? 0L : v.longValue(); }""", tcn))
    tcn.addMethod(CtM.make("""public Object apply(Object o) {
  synchronized (com.skyy.bazaar.SkyyBzTestCoins.class) {
    if (this.mode == 0) return Long.valueOf(bal(String.valueOf(o)));
    Object[] a = (Object[]) o;
    String k = String.valueOf(a[0]);
    long n = ((Long) a[1]).longValue();
    long h = bal(k);
    if (this.mode == 1) { if (n <= 0L || h < n) return Boolean.FALSE; P.put(k, Long.valueOf(h - n)); return Boolean.TRUE; }
    if (FAILADD) return Boolean.FALSE;
    P.put(k, Long.valueOf(h + n));
    return Long.valueOf(h + n);
  }
}""", tcn))
    Coins_ = JClass(tcn.toClass(JClass(PKG + "Coins").class_))
    tpl = jp.makeClass(PKG + "SkyyBzTestPlayers")
    tpl.addInterface(jp.get("java.util.function.Function"))
    tpl.addField(CtF.make("public static volatile Object P;", tpl))
    tpl.addConstructor(CtC.make("public SkyyBzTestPlayers() { }", tpl))
    tpl.addMethod(CtM.make("public Object apply(Object o) { return P; }", tpl))
    TPlayers = JClass(tpl.toClass(JClass(PKG + "Coins").class_))
    tsl = jp.makeClass(PKG + "SkyyBzTestSeller")
    tsl.addInterface(jp.get("java.lang.Runnable"))
    for fdecl in ("public Object p;", "public java.util.UUID u;", "public String id;", "public int loops;", "public long coins;", "public int qty;",
                  "public java.util.concurrent.CountDownLatch go;"):
        tsl.addField(CtF.make(fdecl, tsl))
    tsl.addConstructor(CtC.make("public SkyyBzTestSeller() { }", tsl))
    tsl.addMethod(CtM.make("""public void run() {
  try { this.go.await(); } catch (Throwable t) { }
  for (int i = 0; i < this.loops; i++) {
    com.skyy.bazaar.TradeResult r = com.skyy.bazaar.Trader.sell((com.hypixel.hytale.server.core.entity.entities.Player) this.p, this.u, "T", this.id, 1);
    if (r.ok) { this.coins += r.coins; this.qty += r.qty; }
  }
}""", tsl))
    TSeller = JClass(tsl.toClass(JClass(PKG + "Coins").class_))
    System, Paths, Long_, UUID = JClass("java.lang.System"), JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.util.UUID")
    Thread, Latch = JClass("java.lang.Thread"), JClass("java.util.concurrent.CountDownLatch")
    bridge = JClass("java.util.concurrent.ConcurrentHashMap")()
    System.getProperties().put("skyy.bridge", bridge)

    def coins_on():
        for i, k in enumerate(("coins:fn:get", "coins:fn:take", "coins:fn:add")):
            bridge.put(k, Coins_(i))
    coins_on()
    U1 = UUID.fromString("00000000-0000-0000-0000-00000000b0b0")
    purse = lambda: int(Coins_.bal(str(U1)))

    def set_purse(v):
        Coins_.P.put(str(U1), Long_(v))
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")

    def jfield(cls, name):
        c = cls
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)
    inv_field = jfield(PLA.class_, "inventory")

    def player(storage=(), hotbar=(), backpack=()):
        s, h, b = SIC(JShort(36)), SIC(JShort(9)), SIC(JShort(9))
        for cont, its in ((s, storage), (h, hotbar), (b, backpack)):
            for (iid, q) in its:
                tx = cont.addItemStack(IS(iid, q))
                assert tx.succeeded(), (iid, q)
        p = us.allocateInstance(PLA.class_)
        inv_field.set(p, TInv(s, h, b))
        return p

    def held(p, iid):
        n = 0
        inv = p.getInventory()
        for cont in (inv.getStorage(), inv.getHotbar(), inv.getBackpack()):
            for i in range(int(cont.getCapacity())):
                it = cont.getItemStack(JShort(i))
                if it is not None and not it.isEmpty() and str(it.getItemId()) == iid:
                    n += int(it.getQuantity())
        return n

    def inv_all(p):
        out = {}
        inv = p.getInventory()
        for cont in (inv.getStorage(), inv.getHotbar(), inv.getBackpack()):
            for i in range(int(cont.getCapacity())):
                it = cont.getItemStack(JShort(i))
                if it is not None and not it.isEmpty():
                    out[str(it.getItemId())] = out.get(str(it.getItemId()), 0) + int(it.getQuantity())
        return out

    def pref(name="Tester"):
        pr = us.allocateInstance(TPR.class_)
        jfield(JClass(PRN).class_, "uuid").set(pr, U1)
        jfield(JClass(PRN).class_, "username").set(pr, JString(name))
        return pr

    Jc = lambda n: JClass(PKG + n)
    Mkt, Cfg, Trd, Page, Bags, Res = Jc("Market"), Jc("BzCfg"), Jc("Trader"), Jc("BzPage"), Jc("Bags"), Jc("TradeResult")
    SEED = [str(x) for x in Cat.SEED]
    PIDS = [s.split("=", 1)[0] for s in SEED]
    for pid in PIDS:
        KMap.KNOWN.add(pid)

    def reset_state():
        Cat.LIST.clear(); Cat.BY_ID.clear(); Cat.WARNED.clear(); Cat.CACHE.clear(); Cat.AUTO.clear()
        Cat.CATS = None
        Cat.DIRTY = False
        Cat.MODES_BAD = False
        Cat.MIGRATED = ""
        Cat.MIGRATED14 = ""
        Cat.M14_LOG.clear()
        Cat.PREM = -1.0
        Cat.PCT = -1
        Mkt.F.clear(); Mkt.BOUGHT.clear(); Mkt.SOLD.clear(); Mkt.LOGQ.clear()
        Mkt.LAST = 0
        Cfg.PREMIUM = 20

    def start(d):
        """SkyyBazaarPlugin.setup()'s data steps on folder d (as the 0.1.4 harness: the commands / scheduler / kit need the server)"""
        dp = Paths.get(d)
        Cat.FILE = dp.resolve("products.properties")
        Cat.PFILE = dp.resolve("pricing.properties")
        Mkt.FILE = dp.resolve("market.properties")
        Mkt.LOGFILE = dp.resolve("trades.log")
        Cfg.load(dp)
        mig = Cat.migrate()
        mig14 = Cat.migrate14()
        n = Cat.load()
        Mkt.load()
        Cat.reprice()
        Mkt.publishAll()
        Cat.flushIfDirty()
        Cat.warnLoops(Mkt.SPREAD)
        if mig is not None:
            Mkt.log(mig)
        if mig14 is not None:
            for x in Cat.M14_LOG:
                Mkt.log(x)
        Cat.M14_LOG.clear()
        return mig, mig14, n

    def stop():
        Mkt.flush()
        Cat.flushIfDirty()

    def files(d):
        out = {}
        for root, _ds, fs in os.walk(d):
            for f in fs:
                p = os.path.join(root, f)
                out[os.path.relpath(p, d)] = open(p, "rb").read()
        return out

    def base_of(pid):
        return float(Cat.get(pid).base)

    def mprops(b):
        out = {}
        for l in b.decode("latin-1").splitlines():
            if l and not l.startswith("#") and "=" in l:
                k, v = l.split("=", 1)
                out[k.strip()] = v.strip()
        return out

    def churn(before, after):
        """changed files, market.properties only when its meaning changed: same keys and counters / settings, every demand factor at the
        same place or decayed toward 1.0 (Market.decay on load / save - time based, the Market class is byte-identical to 0.1.4's)"""
        ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        if "market.properties" in ch and "market.properties" in before and "market.properties" in after:
            mb, ma = mprops(before["market.properties"]), mprops(after["market.properties"])
            ok = set(mb) == set(ma)
            for k in mb:
                if not ok:
                    break
                if k.startswith("f."):
                    o, n = float(mb[k]), float(ma[k])
                    ok = abs(n - 1.0) <= abs(o - 1.0) + 1e-12 and (n - 1.0) * (o - 1.0) >= 0
                elif k != "lastDecayMillis":
                    ok = mb[k] == ma[k]
            if ok:
                ch.remove("market.properties")
        return ch

    # ---------------- F. fresh start
    reset_state()
    d0 = os.path.join(SCRATCH, "fresh")
    os.makedirs(d0)
    mig, mig14, n = start(d0)
    check(n == N_PROD and base_of(SAP) == 12.0, "F: fresh start: %d products, Tree Sap at 12 (%s)" % (n, base_of(SAP)))
    lines = open(os.path.join(d0, "products.properties"), encoding="utf8").read().splitlines()
    check("Ingredient_Tree_Sap=Foraging,12,Tree Sap" in lines and [l for l in lines if not l.startswith("#")] == SEED, "F: the seeded file holds sap 12")
    print("F. fresh start: %d products, Tree Sap seeded at 12" % n)

    # ---------------- P. sap with saved prices (no migration of saved values)
    live = os.path.join(SCRATCH, "live")
    have_live = os.path.isdir(live) and os.path.exists(os.path.join(live, "products.properties"))
    if not have_live:
        print("note: no live SkyyBazaar data copy - P (live variants) skipped")
    else:
        lp = open(os.path.join(live, "products.properties"), "rb").read()
        sapl = [l for l in lp.decode("utf8").splitlines() if l.startswith(SAP + "=")]
        variants = [("live", None)]
        if sapl:
            variants += [("sap4", sapl[0].replace(sapl[0].split(",")[1], "4", 1)), ("sap20", sapl[0].replace(sapl[0].split(",")[1], "20", 1))]
        for vn, newl in variants:
            d = os.path.join(SCRATCH, "p-" + vn)
            shutil.copytree(live, d)
            if newl is not None:
                b = open(os.path.join(d, "products.properties"), "rb").read().replace(sapl[0].encode("utf8"), newl.encode("utf8"))
                open(os.path.join(d, "products.properties"), "wb").write(b)
            want = float(newl.split(",")[1]) if newl else (float(sapl[0].split(",")[1]) if sapl else 12.0)
            before = files(d)
            for _r in (1, 2):
                reset_state()
                m1, m14, n1 = start(d)
                check(m1 is None and m14 is None and base_of(SAP) == want, "P %s start %d: no update runs, sap stays %s (%s)" % (vn, _r, want, base_of(SAP)))
                stop()
            after = files(d)
            ch = churn(before, after)
            check(not ch, "P %s: two starts change no file (market.properties: only the demand decay) (%s)" % (vn, ch[:4]))
        v012 = os.path.join(live, "products.properties.v012bak")
        if os.path.exists(v012):
            for vn, sap_txt, want in (("v012", None, 12.0), ("v012-hand5", "5", 5.0)):
                d = os.path.join(SCRATCH, "p-" + vn)
                os.makedirs(d)
                b = open(v012, "rb").read()
                if sap_txt is not None:
                    ls = b.decode("utf8").split("\n")
                    if any(l.startswith(SAP + "=") for l in ls):
                        ls = [(l.replace(",4,", "," + sap_txt + ",", 1) if l.startswith(SAP + "=") else l) for l in ls]
                    else:
                        ls.insert(len(ls) - 1 if ls and ls[-1] == "" else len(ls), SAP + "=Foraging," + sap_txt + ",Tree Sap")
                    b = "\n".join(ls).encode("utf8")
                open(os.path.join(d, "products.properties"), "wb").write(b)
                had = any(l.startswith(SAP + "=") for l in b.decode("utf8").splitlines())
                reset_state()
                m1, m14, n1 = start(d)
                check(m1 is not None and base_of(SAP) == want, "P %s: 0.1.2 data (sap line %s) -> the 0.1.3 update, sap %s (%s; %s)"
                      % (vn, "present" if had else "absent", want, base_of(SAP), str(m1)[:80]))
                stop()
        print("P. Tree Sap: live data (Skyy's price) kept through two starts, 4 and 20 kept (no migration of saved values), 0.1.2 data -> 12, hand 5 kept")

    # ---------------- M. max stack from the engine's Item (decoded with the Parent chain)
    AZ = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    AN = AZ.namelist()
    ITEMS = dict((n.rsplit("/", 1)[1][:-5], n) for n in AN if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    JS = {}

    def ij(k):
        if k not in JS:
            JS[k] = json.loads(AZ.read(ITEMS[k]).decode("utf-8-sig"))
        return JS[k]

    def expect(k):   # Assets.zip: MaxStack, else the Parent's, else the engine default (tool / weapon / armor 1, else 100)
        d = ij(k)
        if "MaxStack" in d:
            return int(d["MaxStack"])
        if d.get("Parent") in ITEMS:
            return expect(d["Parent"])
        return 1 if any(x in d for x in ("Tool", "Weapon", "Armor", "BuilderTool", "BlockSelectorTool")) else 100

    def gearish(k):
        d = ij(k)
        if any(x in d for x in ("Tool", "Weapon", "Armor", "BuilderTool", "BlockSelectorTool")):
            return True
        return gearish(d["Parent"]) if d.get("Parent") in ITEMS else False
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    AEI, ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo"), JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR = JClass("com.hypixel.hytale.codec.util.RawJsonReader")
    F_AM, F_KTI = JClass(DAMN).class_.getDeclaredField("assetMap"), ILT.class_.getDeclaredField("keyToIndex")
    F_T, F_M = AS.class_.getDeclaredField("tClass"), AS.class_.getDeclaredField("assetMap")
    F_SM = JClass("com.hypixel.hytale.assetstore.AssetRegistry").class_.getDeclaredField("storeMap")
    for f_ in (F_AM, F_KTI, F_T, F_M, F_SM):
        f_.setAccessible(True)

    @JImplements("java.util.function.IntFunction")
    class Arr(object):
        def __init__(self, c):
            self.c = c

        @JOverride
        def apply(self, n):
            return JArray(self.c)(int(n))

    def install(cname, keys):
        C = JClass(cname)
        m = ILT(Arr(C))
        am, kti = F_AM.get(m), F_KTI.get(m)
        for i, k in enumerate(keys):
            am.put(k, us.allocateInstance(C.class_))
            kti.put(JObject(JString(k), JClass("java.lang.Object")), JInt(i + 1))
        st = us.allocateInstance(FAKEC)
        F_T.set(st, C.class_)
        F_M.set(st, m)
        F_SM.get(None).put(C.class_, st)
        try:
            fa = C.class_.getDeclaredField("ASSET_STORE")
            fa.setAccessible(True)
            if fa.get(None) is None:
                fa.set(None, st)
        except Exception:
            pass
    STORE_KEYS = {"com.hypixel.hytale.server.core.asset.type.item.config.ItemQuality": "Server/Item/Qualities/",
                  "com.hypixel.hytale.server.core.asset.type.itemsound.config.ItemSoundSet": "Server/Audio/ItemSounds/"}
    DONE, DEC, REGS = set(), {}, []

    def decode(key):
        """the engine's Item codec on the item's MaxStack (the only field the stack depends on for a material) over its decoded Parent"""
        if key in DEC:
            return DEC[key]
        d = ij(key)
        parent = decode(d["Parent"]) if d.get("Parent") in ITEMS else None
        txt = json.dumps(dict((k2, v2) for k2, v2 in d.items() if k2 == "MaxStack"))
        for _i in range(12):
            ei = AEI(Paths.get(key + ".json"), ADT(ITM.class_, key, None))
            try:
                o = ITM.CODEC.decodeAndInheritJsonAsset(RJR.fromJsonString(txt), parent, ei) if parent is not None else \
                    ITM.CODEC.decodeJsonAsset(RJR.fromJsonString(txt), ei)
            except Exception as e:
                th = e
                while th.getCause() is not None:
                    th = th.getCause()
                fr = list(th.getStackTrace())
                m2 = re.search(r'value of "([\w.$]+)\.getAssetStore\(\)" is null', str(th))
                cls_ = m2.group(1) if m2 else (str(fr[0].getClassName()) if "AssetRegistry.getAssetStore" in str(th.getMessage()) and fr
                                               and str(fr[0].getMethodName()) == "getAssetMap" else None)
                if cls_ and cls_ not in DONE:
                    DONE.add(cls_)
                    pre = STORE_KEYS.get(cls_)
                    install(cls_, sorted(set(n.rsplit("/", 1)[1][:-5] for n in AN if pre and n.startswith(pre) and n.endswith(".json"))))
                    REGS.append(cls_.rsplit(".", 1)[1])
                    continue
                raise
            DEC[key] = o
            return o
        raise RuntimeError("too many stores for " + key)
    gear = [pid for pid in PIDS if pid in ITEMS and gearish(pid)]
    check(not gear and all(pid in ITEMS for pid in PIDS), "M: every product is an Assets.zip item and none is a tool / weapon / armor (%s)" % gear[:4])
    bad, inherit, dist = [], [], collections.Counter()
    for pid in PIDS:
        try:
            o = decode(pid)
        except Exception as e:
            bad.append("%s: decode %s" % (pid, str(e)[:120]))
            continue
        KMap.REAL.put(pid, o)
        want = expect(pid)
        got = int(Trd.stack(pid))
        dist[got] += 1
        if "MaxStack" not in ij(pid) and ij(pid).get("Parent") in ITEMS and want != 100:
            inherit.append(pid)
        if got != want or int(o.getMaxStack()) != want:
            bad.append("%s: Trader.stack %d, engine %d, Assets.zip %d" % (pid, got, int(o.getMaxStack()), want))
    check(not bad, "M: Trader.stack = the engine Item's max stack = the Assets.zip rule for all %d products: %s" % (len(PIDS), bad[:5]))
    for pid, want in (("Ore_Copper", 25), ("Ore_Mithril", 25), ("Rock_Stone", 100), (SAP, 100), ("Rock_Gem_Diamond", 25)):
        check(int(Trd.stack(pid)) == want, "M: %s stack %d (%d)" % (pid, want, int(Trd.stack(pid))))
    check("Rock_Gem_Diamond" in inherit and len(inherit) >= 3, "M: inherit-only items read their Parent's MaxStack: %s" % inherit[:6])
    food = [pid for pid in PIDS if pid.startswith("Food_")]
    check(not food or all(int(Trd.stack(f)) == expect(f) for f in food), "M: food stacks (%s)" % [(f, int(Trd.stack(f))) for f in food[:3]])
    check(int(Trd.stack("No_Such_Item_Id")) == 100 and int(Trd.stack(None)) == 100, "M: an unknown id -> 100 (the engine's plain-item default)")
    ms = jfield(ITM.class_, "maxStack")
    zero = us.allocateInstance(ITM.class_)
    ms.setInt(zero, 0)
    KMap.REAL.put("Skyy_Test_Zero", zero)
    big = us.allocateInstance(ITM.class_)
    ms.setInt(big, 999999999)
    KMap.REAL.put("Skyy_Test_Big", big)
    check(int(Trd.stack("Skyy_Test_Zero")) == 100 and int(Trd.stack("Skyy_Test_Big")) == int(Trd.MAXQ), "M: a 0 max stack -> 100; never above the per-trade limit")
    print("M. max stack: %d products decoded through Item.CODEC with their Parent chain (stores added: %s) - Trader.stack = engine = Assets.zip; "
          "stacks %s; inherit-only %s" % (len(PIDS), ", ".join(REGS), dict(sorted(dist.items())), inherit[:5]))

    # ---------------- K. selling with the bags (real SkyySacks 0.7.13)
    SP, SB, SFn, SMir, SLog = (JClass("com.skyy.sacks." + n) for n in ("SackPool", "SackBridge", "SackFn", "BagMirror", "CraftLog"))
    FOR_S, MIN_S, OMNI = "Skyy_Sack_Foraging_Small", "Skyy_Sack_Mining_Small", "Skyy_Sack_Omni"
    OAK, COP = "Wood_Oak_Trunk", "Ore_Copper"

    def sacks_on():
        for i, k in enumerate(("sacks:fn:count", "sacks:fn:take", "sacks:fn:put", "sacks:fn:all", "sacks:fn:commit")):
            bridge.put(k, SFn(i))

    def sacks_off():
        for k in ("sacks:fn:count", "sacks:fn:take", "sacks:fn:put", "sacks:fn:all", "sacks:fn:commit"):
            bridge.remove(k)
    K1 = str(U1)
    kd = os.path.join(SCRATCH, "k-pools")

    def pools(vals, d=kd):
        for m_ in (SP.POOLS, SP.DIRTY, SP.BADPOOL, SP.SEENEPOCH, SP.SEENKEY, SP.CHANGEDAT, SP.UNKNOWN, SMir.MIRRORS, SB.OWED, SB.LASTKEY):
            m_.clear()
        SP.DIR = Paths.get(d)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, K1 + ".properties"), "w", encoding="latin-1") as f:
            f.write("#t\n" + "".join("%s=%d\n" % (a, b) for a, b in vals.items()))

    def pool(iid):
        v = SP.pool(K1).get(iid)
        return 0 if v is None else int(v.longValue())

    def onfile(iid):
        SP.flushDirty()
        for l in open(os.path.join(SP.DIR.toString(), K1 + ".properties"), encoding="latin-1").read().splitlines():
            if l.startswith(iid + "="):
                return int(l.split("=", 1)[1])
        return 0

    def setp(p):
        TPlayers.P = p
        TSTORE_P(p)

    def TSTORE_P(p):
        TStore.P = p
    reset_state()
    dK = os.path.join(SCRATCH, "k-bazaar")
    os.makedirs(dK)
    start(dK)
    sacks_on()
    SB.PLAYERS = TPlayers()
    set_purse(10 ** 9)
    qS = lambda iid, q: int(Mkt.quote(iid, q, False))
    stk_sap = int(Trd.stack(SAP))
    check(stk_sap == 100, "K: Tree Sap stack 100")

    def sell(p, iid, q, label, inv_take, bag_take, n_expect=None):
        """one sale; the coins must equal the quote (taken BEFORE the trade) of what really left; the inventory part first"""
        h0, b0, c0 = held(p, iid), pool(iid), purse()
        want_total = inv_take + bag_take
        quote = qS(iid, want_total) if want_total > 0 else 0
        r = Trd.sell(p, U1, "Tester", iid, q)
        h1, b1, c1 = held(p, iid), pool(iid), purse()
        ok = (bool(r.ok) == (want_total > 0) and h0 - h1 == inv_take and b0 - b1 == bag_take and c1 - c0 == quote == int(r.coins)
              and int(r.qty) == want_total and int(r.fromBags) == bag_take)
        check(ok, "K %s: inventory -%d (%d), bags -%d (%d), coins +%d = quote %d (%s) - %s" % (label, h0 - h1, inv_take, b0 - b1, bag_take, c1 - c0,
                                                                                            quote, r.coins, r.msg))
        return r
    # K1 Sell 1 / stack / all with sap split 30 inventory + 200 bag (Foraging bag in the hotbar)
    pools({SAP: 200, OAK: 40, COP: 60})
    p = player(storage=[(SAP, 30)], hotbar=[(FOR_S, 1)])
    setp(p)
    sell(p, SAP, 1, "Sell 1 (inventory first)", 1, 0)
    r = sell(p, SAP, stk_sap, "Sell 100 (29 inventory + 71 bags)", 29, 71)
    check("(71 from your bags)" in str(r.msg) and onfile(SAP) == 129, "K: message names the bag part; the pool file says 129")
    logs = [str(x) for x in Mkt.LOGQ.toArray()]
    check(any((" SELL Tester %s %s 100 " % (U1, SAP)) in l and l.endswith(" bags=71") for l in logs), "K: trades.log SELL line ends bags=71")
    r = sell(p, SAP, 0, "Sell all (all 129 from the bags)", 0, 129)
    check(pool(SAP) == 0 and onfile(SAP) == 0 and str(r.msg).endswith("(129 from your bags)"), "K: the bag is empty and saved")
    # REVIEW FIX 1: every PAID bag part was committed - nothing of the 200 is left in SkyySacks' refund ledger, a put returns nothing
    check(SB.OWED.get(K1 + "|" + SAP) is None, "FIX1: paid sales committed their bag part (owed ledger empty)")
    check(int(bridge.get("sacks:fn:put").apply(JArray(JObject)([U1, JString(SAP), Long_(200)])).longValue()) == 0 and pool(SAP) == 0,
          "FIX1: sacks:fn:put of 200 right after the paid sales -> 0 (no free items)")
    r = Trd.sell(p, U1, "Tester", SAP, 1)
    check(not r.ok and str(r.msg) == "you have no Tree Sap", "K: nothing left -> 'you have no Tree Sap'")
    # K2 custom amount (Trader.sellN): 10 inventory + 40 of the bags; more than held is refused, nothing moves
    pools({SAP: 100})
    p = player(storage=[(SAP, 10)], hotbar=[(FOR_S, 1)])
    setp(p)
    c0 = purse()
    r = Trd.sellN(p, U1, "Tester", SAP, 111, Long_(0))
    check(not r.ok and "you only hold 110" in str(r.msg) and held(p, SAP) == 10 and pool(SAP) == 100 and purse() == c0, "K: custom 111 of 110 refused, nothing moves")
    q50 = qS(SAP, 50)
    r = Trd.sellN(p, U1, "Tester", SAP, 50, Long_(q50))
    check(bool(r.ok) and held(p, SAP) == 0 and pool(SAP) == 60 and purse() - c0 == q50, "K: custom Sell 50 = 10 inventory + 40 bags for exactly %d" % q50)
    # the page's custom flow: amount "all", Sell armed then confirmed -> everything (inventory + bags)
    p = player(storage=[(SAP, 5)], hotbar=[(FOR_S, 1)])
    setp(p)
    pg = Page(pref(), SAP)
    pg.amount = "all"
    now = int(System.currentTimeMillis())
    pg.amountAction(p, U1, "Tester", "asell", Long_(now))
    armed = str(pg.info)
    c0 = purse()
    q65 = qS(SAP, 65)
    pg.amountAction(p, U1, "Tester", "asell", Long_(now + 100))
    check("Sell 65 Tree Sap for %d coins" % q65 in armed and held(p, SAP) == 0 and pool(SAP) == 0 and purse() - c0 == q65,
          "K: page custom 'all' = 5 inventory + 60 bags: armed '%s', sold for %d" % (armed[:60], purse() - c0))
    # K3 Sell inventory: sap split, oak only in the bag, copper in the inventory + the pool but NO Mining bag carried
    pools({SAP: 40, OAK: 25, COP: 60})
    p = player(storage=[(SAP, 12), (COP, 7)], hotbar=[(FOR_S, 1)])
    setp(p)
    pv = [int(x) for x in Trd.preview(p, U1)]
    exp_coins = qS(SAP, 52) + qS(OAK, 25) + qS(COP, 7)
    check(pv == [52 + 25 + 7, exp_coins, 40 + 25], "K: Sell inventory preview = {84 items, %d coins, 65 from the bags}: %s" % (exp_coins, pv))
    c0 = purse()
    r = Trd.sellInventory(p, U1, "Tester")
    check(bool(r.ok) and int(r.qty) == 84 and int(r.coins) == exp_coins == purse() - c0 and int(r.fromBags) == 65 and "(65 from your bags)" in str(r.msg),
          "K: Sell inventory sold 84 (65 from the bags) for exactly %d: %s" % (exp_coins, r.msg))
    check(inv_all(p) == {FOR_S: 1} and pool(SAP) == 0 and pool(OAK) == 0 and pool(COP) == 60,
          "K: after Sell inventory only the Magic Bag is left; the Mining pool (no Mining bag carried) untouched: %s" % inv_all(p))
    # K4 partial availability: a bridge whose take removes only half of what is asked
    REAL_TAKE = bridge.get("sacks:fn:take")

    @JImplements("java.util.function.Function")
    class HalfTake:
        @JOverride
        def apply(self, o):
            o[2] = Long_(int(o[2].longValue()) // 2)
            return REAL_TAKE.apply(o)
    pools({SAP: 200})
    p = player(storage=[(SAP, 20)], hotbar=[(FOR_S, 1)])
    setp(p)
    bridge.put("sacks:fn:take", HalfTake())
    sell(p, SAP, stk_sap, "partial take (asked 80, the bags give 40)", 20, 40)
    bridge.put("sacks:fn:take", REAL_TAKE)

    @JImplements("java.util.function.Function")
    class LieCount:
        @JOverride
        def apply(self, o):
            return Long_(int(SFn(0).apply(o).longValue()) + 50)
    pools({SAP: 30})
    p = player(storage=[(SAP, 5)], hotbar=[(FOR_S, 1)])
    setp(p)
    bridge.put("sacks:fn:count", LieCount())
    sell(p, SAP, 0, "count over-reports by 50 (Sell all pays only the 35 that left)", 5, 30)
    bridge.put("sacks:fn:count", SFn(0))
    # K5 no bag carried / SkyySacks absent / an older SkyySacks (count but no take)
    pools({SAP: 50})
    p = player(storage=[(SAP, 8)])
    setp(p)
    sell(p, SAP, 0, "no Foraging bag carried (inventory only)", 8, 0)
    r = Trd.sell(p, U1, "Tester", SAP, 1)
    check(not r.ok and pool(SAP) == 50, "K: inventory empty + bag not carried -> nothing sold, the pool keeps 50")
    p = player(storage=[(SAP, 8)], hotbar=[(FOR_S, 1)])
    setp(p)
    sacks_off()
    sell(p, SAP, 0, "SkyySacks absent (0.1.4 behaviour)", 8, 0)
    bridge.put("sacks:fn:count", SFn(0))
    p = player(storage=[(SAP, 3)], hotbar=[(FOR_S, 1)])
    setp(p)
    sell(p, SAP, 0, "an older SkyySacks (count, no take) = no bags", 3, 0)
    check(not bool(Bags.on()) and int(Bags.count(U1, SAP)) == 0, "K: Bags.on() needs both count and take")
    sacks_on()
    # K6 two sells in one tick (the page handles clicks one by one on the world thread) + two Java threads
    pools({SAP: 120})
    p = player(storage=[(SAP, 50)], hotbar=[(FOR_S, 1)])
    setp(p)
    sell(p, SAP, stk_sap, "double click #1 (50 inventory + 50 bags)", 50, 50)
    sell(p, SAP, stk_sap, "double click #2 (the 70 left in the bags)", 0, 70)
    r = Trd.sell(p, U1, "Tester", SAP, stk_sap)
    check(not r.ok and pool(SAP) == 0 and held(p, SAP) == 0, "K: double click #3 -> nothing left, nothing paid")
    pools({SAP: 300})
    p = player(storage=[(SAP, 100)], hotbar=[(FOR_S, 1)])
    setp(p)
    c0 = purse()
    latch = Latch(1)
    ws, ts = [], []
    for _i in range(2):
        w = TSeller()
        w.p, w.u, w.id, w.loops, w.go = p, U1, SAP, 250, latch
        ws.append(w)
        t = Thread(w)
        t.start()
        ts.append(t)
    latch.countDown()
    for t in ts:
        t.join(300000)
    sold = sum(int(w.qty) for w in ws)
    paid = sum(int(w.coins) for w in ws)
    check(sold == 400 and held(p, SAP) == 0 and pool(SAP) == 0 and purse() - c0 == paid and paid > 0,
          "K: two threads x 250 Sell 1 against 100 inventory + 300 bags -> exactly 400 sold, coins = their sum (%d / %d)" % (sold, paid))
    # K7 the payment fails: the bag part goes back to the bags (sacks:fn:put), the inventory part to the inventory
    pools({SAP: 90})
    p = player(storage=[(SAP, 15)], hotbar=[(FOR_S, 1)])
    setp(p)
    c0 = purse()
    Coins_.FAILADD = True
    r = Trd.sell(p, U1, "Tester", SAP, stk_sap)
    check(not r.ok and "items were returned" in str(r.msg) and held(p, SAP) == 15 and pool(SAP) == 90 and purse() == c0,
          "K: coins:fn:add refuses -> inventory 15 and bags 90 back exactly, no coins: %s" % r.msg)
    check(any("PAY-FAILED" in str(x) and "bags=85" in str(x) for x in Mkt.LOGQ.toArray()), "K: the PAY-FAILED log line names the bag part")
    PUT = bridge.get("sacks:fn:put")
    bridge.remove("sacks:fn:put")
    r = Trd.sell(p, U1, "Tester", SAP, 50)
    check(not r.ok and held(p, SAP) + pool(SAP) == 105 and held(p, SAP) == 50 and pool(SAP) == 55 and purse() == c0,
          "K: no sacks:fn:put -> the bag part goes into the inventory (50 = 15 + 35), nothing lost: inv %d pool %d" % (held(p, SAP), pool(SAP)))
    bridge.put("sacks:fn:put", PUT)
    Coins_.FAILADD = False
    check(SB.OWED.get(K1 + "|" + SAP) is None, "FIX1: the 35 that went to the inventory were committed (the ledger can never return them to the bag too)")
    # REVIEW FIX 3: a full inventory + the profile pausing between the take and the failed payment -> the bag part still goes back
    pools({SAP: 60})
    full = [(COP, 25)] * 36
    p = player(storage=full, hotbar=[(FOR_S, 1)] + [(COP, 25)] * 8, backpack=[(COP, 25)] * 9)
    setp(p)
    check(int(JClass(PKG + "Inv").give(p, SAP, 1)) == 0, "FIX3: the test inventory is full (a give fits 0)")

    @JImplements("java.util.function.Function")
    class PauseThenRefuse:
        @JOverride
        def apply(self, o):
            bridge.put("profile:busy:" + str(U1), JString("x"))   # a switch / crash recovery flag lands mid-sale
            return JObject(False, JClass("java.lang.Boolean"))
    ADD = bridge.get("coins:fn:add")
    bridge.put("coins:fn:add", PauseThenRefuse())
    c0 = purse()
    r = Trd.sell(p, U1, "Tester", SAP, 0)
    bridge.put("coins:fn:add", ADD)
    paused = int(bridge.get("sacks:fn:count").apply(JArray(JObject)([U1, JString(SAP)])).longValue())
    bridge.remove("profile:busy:" + str(U1))
    check(not r.ok and not r.alert and "items were returned" in str(r.msg) and pool(SAP) == 60 and onfile(SAP) == 60 and held(p, SAP) == 0
          and purse() == c0 and paused == -1, "FIX3: busy mid-sale + full inventory -> all 60 back in the bag (before: 0 fit, 60 lost): %s" % r.msg)
    # K8 a Magic Bag product line (an admin hand edit) is refused everywhere; Sell inventory never sells a bag
    bagp = JClass(PKG + "Product")(MIN_S, "Mining", 50.0, "Mining Bag")
    Cat.LIST.add(bagp)
    Cat.BY_ID.put(MIN_S, bagp)
    KMap.KNOWN.add(MIN_S)
    Cat.CACHE.clear()
    Cat.CATS = None
    pools({})
    p = player(storage=[(MIN_S, 1), (COP, 3)])
    setp(p)
    rb, rs = Trd.buy(p, U1, "Tester", MIN_S, 1), Trd.sell(p, U1, "Tester", MIN_S, 1)
    r = Trd.sellInventory(p, U1, "Tester")
    check(not rb.ok and not rs.ok and "Magic Bags" in str(rb.msg) and "Magic Bags" in str(rs.msg) and bool(r.ok) and int(r.qty) == 3
          and held(p, MIN_S) == 1 and int(Trd.preview(p, U1)[0]) == 0, "K: a Skyy_Sack_* product: buy / sell refused, Sell inventory keeps the bag")
    Cat.LIST.remove(bagp)
    Cat.BY_ID.remove(MIN_S)
    Cat.CACHE.clear()
    Cat.CATS = None
    # K9 the page: cells and the hold line count the bags; the stack buttons; page clicks
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def render(pg_, pl_):
        b, ev = UCB(), UEB()
        pg_.render(b, ev, U1, pl_)
        ap, sets = [], []
        for c in b.getCommands():
            t = str(c.type)
            if t == "AppendInline":
                ap.append((None if c.selector is None else str(c.selector).lstrip("#"), str(c.text)))
            elif t == "Set":
                dd = str(c.data)
                try:
                    v_ = json.loads(dd)
                    dd = str(v_.get("0", dd)) if isinstance(v_, dict) else dd
                except Exception:
                    pass
                sets.append((str(c.selector), dd))
        binds = [(str(e.type), str(e.selector), re.sub(r"\s+", "", str(e.data))) for e in ev.getEvents()]
        return ap, sets, binds
    pools({SAP: 340, OAK: 7})
    p = player(storage=[(SAP, 20), (COP, 4)], hotbar=[(FOR_S, 1)])
    setp(p)
    pg = Page(pref(), SAP)
    ap, sets, binds = render(pg, p)
    for _p, mk in ap:
        try:
            SUI.check_markup(mk, root=(_p is None))
            OKS[0] += 1
        except Exception as e:
            FAILS.append("K page markup %s: %s" % (mk[:60], e))
    sd = dict(sets)
    hold = sd.get("#SkyyBzDHold.Text", "")
    check(hold.startswith("You hold 360 (340 in your bags)") and ("selling all pays %d coins" % qS(SAP, 360)) in hold, "K page: %s" % hold)
    cells = [(s_, d_) for s_, d_ in sets if s_.startswith("#SkyyBzCell") and s_.endswith("Qty.Text")]
    check(("360" in [d_ for _s, d_ in cells]) and ("7" in [d_ for _s, d_ in cells]), "K page: the Foraging grid shows sap 360 and oak 7 (bags counted): %s" % cells[:4])
    acts = " ".join(mk for _p, mk in ap if "SkyyBzBuyStk" in mk or "SkyyBzSellStk" in mk)
    check('Text: "Buy 100"' in acts and 'Text: "Sell 100"' in acts and "QzStkQz" not in " ".join(mk for _p, mk in ap),
          "K page: the stack buttons read Buy 100 / Sell 100 for Tree Sap")
    check(" for 100   -   " in sd.get("#SkyyBzDBuy.Text", "") and " for 100   -   " in sd.get("#SkyyBzDSell.Text", ""), "K page: the price lines say 'for 100'")
    bmap = dict((s_, d_) for _t, s_, d_ in binds)
    check('"a":"buystk"' in bmap.get("#SkyyBzBuyStk", "") and '"a":"sellstk"' in bmap.get("#SkyyBzSellStk", "")
          and "#SkyyBzBuy64" not in bmap and "#SkyyBzSell64" not in bmap, "K page: bindings #SkyyBzBuyStk -> buystk, #SkyyBzSellStk -> sellstk")
    lim = [d_ for s_, d_ in sets if s_ == "#SkyyBzLimits.Text"]
    check(lim and "sell up to 360" in lim[0], "K page: the limits line counts the bags: %s" % lim)
    # REVIEW FIX 4: a cell count of 10,000,000+ shows as 12.3M (the cell fits 7 digits), the hold line keeps the exact number
    pools({SAP: 12345678, OAK: 7})
    ap3, sets3, _b3 = render(Page(pref(), SAP), p)
    cells3 = [d_ for s_, d_ in sets3 if s_.startswith("#SkyyBzCell") and s_.endswith("Qty.Text")]
    check("12.3M" in cells3 and "7" in cells3 and dict(sets3).get("#SkyyBzDHold.Text", "").startswith("You hold 12345698 (12345678 in your bags)"),
          "FIX4: 12,345,698 held -> cell '12.3M', hold line exact: %s / %s" % (cells3[:3], dict(sets3).get("#SkyyBzDHold.Text", "")[:50]))
    pools({SAP: 340, OAK: 7})
    pc = Page(pref(), COP)
    pc.cat = "Mining"
    ap2, sets2, _b2 = render(pc, p)
    acts2 = " ".join(mk for _p, mk in ap2 if "SkyyBzBuyStk" in mk or "SkyyBzSellStk" in mk)
    check('Text: "Buy 25"' in acts2 and 'Text: "Sell 25"' in acts2 and " for 25   -   " in dict(sets2).get("#SkyyBzDBuy.Text", ""),
          "K page: Copper Ore reads Buy 25 / Sell 25, 'for 25'")
    # page clicks through handleDataEvent (the test Store answers the player)
    c0 = purse()
    qq = qS(SAP, 100)
    pg.handleDataEvent(None, TSTORE, '{"a":"sellstk","@BzAmount":""}')
    check(held(p, SAP) == 0 and pool(SAP) == 260 and purse() - c0 == qq and "(80 from your bags)" in str(pg.info),
          "K click sellstk: 20 inventory + 80 bags for exactly %d: %s" % (qq, pg.info))
    c0 = purse()
    qb = int(Mkt.quote(COP, 25, True))
    pc.handleDataEvent(None, TSTORE, '{"a":"buystk","@BzAmount":""}')
    check(held(p, COP) == 29 and c0 - purse() == qb, "K click buystk on Copper Ore buys 25 for %d: %s" % (qb, pc.info))
    pg.handleDataEvent(None, TSTORE, '{"a":"sellinv"}')
    pre = str(pg.info)
    exp = qS(SAP, 260) + qS(OAK, 7) + qS(COP, 29)
    c0 = purse()
    pg.handleDataEvent(None, TSTORE, '{"a":"sellinv"}')
    check(("sell 296 items (267 from your bags) for about %d coins" % exp) in pre and purse() - c0 == exp and inv_all(p) == {FOR_S: 1}
          and pool(SAP) == 0 and pool(OAK) == 0, "K click sellinv x2: preview '%s', then sold for %d" % (pre[:80], purse() - c0))
    print("K. sold from the bags through the real SkyySacks 0.7.13: Sell 1 / 100 / all, custom (Trader + page max), Sell inventory, partial "
          "take, over-reporting count, no bag / no SkyySacks / old SkyySacks, double click, 2 threads, failed payment (put / no put), a bag "
          "product refused, the page (counts, Buy 100 / Buy 25, clicks) - coins always = the quote of what left")

    # ---------------- L. money loops on the 0.1.5 runtime table
    SDefs = JClass("com.skyy.sacks.SackDefs")
    NS["bag_of"] = lambda i: None if SDefs.catOf(i) is None else str(SDefs.catOf(i))
    js, data, drops, recfiles, lang = NS["load_assets"]()
    M = NS["asset_model"](js, data, drops, recfiles)
    reset_state()
    start(os.path.join(SCRATCH, "fresh"))
    procs = [str(e[0]) for e in Cat.PROC]
    for prem in range(0, 23):
        Cfg.PREMIUM = prem
        Cat.reprice()
        px = dict((str(x.id), float(x.base)) for x in Cat.all())
        check(len(px) == N_PROD and px[SAP] == 12.0, "L: runtime table %d prices, sap 12 at %d%%" % (len(px), prem))
        if prem in (0, 15, 20, 22):
            try:
                NS["check_assets"](px, NS["SPREAD"])
                OKS[0] += 1
            except SystemExit as e:
                FAILS.append("L: check_assets at %d%%: %s" % (prem, e))
        try:
            loops, _c, _n, _p = NS["loop_check"](M, px, NS["SPREAD"])
        except SystemExit as e:
            loops = ["no fixed point: %s" % e]
        check(not loops, "L: co-product + liquidation loop check at %d%%: %s" % (prem, loops[:3]))
    Cfg.PREMIUM = 20
    Cat.reprice()
    print("L. money loops on the 0.1.5 runtime prices (sap 12): check_assets at 0 / 15 / 20 / 22 %, loop_check at every premium 0-22 %: none")

    # ---------------- S. start twice on copies of the live data (Bazaar + Sacks), then a real sale from the copy's bag pool
    lives = os.path.join(SCRATCH, "livesacks")
    if not (have_live and os.path.isdir(os.path.join(lives, "pools"))):
        print("note: no live data copies - S skipped")
    else:
        dB, dS = os.path.join(SCRATCH, "s-bazaar"), os.path.join(SCRATCH, "s-sacks")
        shutil.copytree(live, dB)
        shutil.copytree(lives, dS)
        bB, bS = files(dB), files(dS)
        for _r in (1, 2):
            reset_state()
            start(dB)
            for m_ in (SP.POOLS, SP.DIRTY, SP.BADPOOL, SP.SEENEPOCH, SP.SEENKEY, SP.CHANGEDAT, SP.UNKNOWN, SMir.MIRRORS, SB.OWED):
                m_.clear()
            SP.DIR = Paths.get(os.path.join(dS, "pools"))
            for f in sorted(os.listdir(os.path.join(dS, "pools"))):
                if f.endswith(".properties"):
                    SP.pool(f[:-11])
            sacks_on()
            stop()
            SP.flushDirty()
        aB, aS = files(dB), files(dS)
        chB = churn(bB, aB)
        chS = sorted(k for k in set(bS) | set(aS) if bS.get(k) != aS.get(k))
        check(not chB and not chS, "S: two starts on the live copies change no file (%s %s)" % (chB[:3], chS[:3]))
        keys = sorted(f[:-11] for f in os.listdir(os.path.join(dS, "pools")) if f.endswith(".properties"))
        target, most = None, 0
        for kk in keys:
            for l in open(os.path.join(dS, "pools", kk + ".properties"), encoding="latin-1").read().splitlines():
                if l.startswith(SAP + "=") and int(l.split("=", 1)[1]) > most:
                    target, most = kk, int(l.split("=", 1)[1])
        if target is None:
            print("note: no pool with Tree Sap in the live copy - S sale skipped")
        else:
            Ut = UUID.fromString(target[:36])
            if "-p" in target:
                @JImplements("java.util.function.Function")
                class KeyFn:
                    @JOverride
                    def apply(self, u):
                        return JString(target)
                bridge.put("profile:fn:key", KeyFn())
                bridge.put("profile:epoch:" + target[:36], Long_(1))
                SP.settledKey(Ut)
                SP.CHANGEDAT.clear()
            Coins_.P.put(target[:36], Long_(1000))
            p = player(storage=[(SAP, 10)], hotbar=[(FOR_S, 1)])
            setp(p)
            pf = os.path.join(dS, "pools", target + ".properties")
            readp = lambda: dict(l.split("=", 1) for l in open(pf, encoding="latin-1").read().splitlines() if l and not l.startswith("#"))
            pb = readp()
            nsell = 10 + min(most, 90)
            q = qS(SAP, nsell)
            r = Trd.sell(p, Ut, "LivePlayer", SAP, nsell)
            SP.flushDirty()
            stop()
            pa = readp()
            aB2, aS2 = files(dB), files(dS)
            chB2 = sorted(k for k in set(aB) | set(aB2) if aB.get(k) != aB2.get(k))
            chS2 = sorted(k for k in set(aS) | set(aS2) if aS.get(k) != aS2.get(k))
            dk = sorted(k for k in set(pb) | set(pa) if pb.get(k) != pa.get(k))
            check(bool(r.ok) and int(Coins_.bal(target[:36])) == 1000 + q and dk == [SAP] and int(pa.get(SAP, "0")) == int(pb[SAP]) - min(most, 90) and held(p, SAP) == 0
                  and chS2 == [os.path.join("pools", target + ".properties")] and sorted(chB2) == ["market.properties", "trades.log"],
                  "S: Sell %d Tree Sap by %s on the copies: 10 inventory + %d bags for %d coins; only the sap line of that pool file, "
                  "market.properties and trades.log changed (%s / %s)" % (nsell, target, min(most, 90), q, chS2, chB2))
            bridge.remove("profile:fn:key")
        print("S. two starts on the live Bazaar + Sacks copies: no file changed; a real Sell 100 from the copy's bag pool changes exactly the sap "
              "line of that pool file + market.properties + trades.log")


def main():
    if "--child" in sys.argv:
        try:
            run()
        except Exception as e:
            import traceback
            traceback.print_exc()
            FAILS.append("crash: %s" % e)
        print("%d ok, %d fail" % (OKS[0], len(FAILS)))
        sys.exit(1 if FAILS else 0)
    if not (SCRATCH + os.sep).startswith(SCRATCH_ROOT + os.sep) or SCRATCH == SCRATCH_ROOT:
        raise SystemExit("--dir must be inside tools/dev/scratch")
    if os.path.exists(SCRATCH) and os.listdir(SCRATCH) and not os.path.exists(os.path.join(SCRATCH, MARK)):
        raise SystemExit("%s is not empty and not an earlier run of this harness - refusing to use it" % SCRATCH)
    if os.path.exists(SCRATCH):
        shutil.rmtree(SCRATCH)
    os.makedirs(SCRATCH)
    open(os.path.join(SCRATCH, MARK), "w").write("SkyyBazaar 0.1.5 harness scratch\n")
    if os.path.isdir(LIVE):
        shutil.copytree(LIVE, os.path.join(SCRATCH, "live"))
        print("copied the live data folder (read only):", LIVE)
    if os.path.isdir(LIVES):
        shutil.copytree(LIVES, os.path.join(SCRATCH, "livesacks"))
        print("copied the live data folder (read only):", LIVES)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env.pop("JAVA_TOOL_OPTIONS", None)
    os.makedirs(env["TEMP"], exist_ok=True)
    rc = subprocess.run([sys.executable, os.path.abspath(__file__), "--child"] + sys.argv[1:], env=env).returncode
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyBazaar %s bare-JVM check: %s (exit code %d)" % (VERSION, "PASS" if rc == 0 else "FAIL", rc))
    sys.exit(rc)


if __name__ == "__main__":
    main()
