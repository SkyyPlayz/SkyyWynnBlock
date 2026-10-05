"""Bare-JVM harness for SkyyBazaar 0.1.4 (progression prices + the one-time price update), extended from the 0.1.3 harness (every
Magic Bag item in its tab, processed goods at a premium, the vanilla-kit page - all re-run on the 0.1.4 jar).

    python SkyyBazaar/test_skyybazaar_0.1.4.py [--jar <0.1.4 jar>] [--old <0.1.3 jar>] [--sacks <SkyySacks SET jar>]
                                               [--live <Skyy_SkyyBazaar folder>] [--dir <scratch folder>] [--keep]

Build first (python tools/bazaar_0_1_4_patch.py, then python SkyyBazaar/build_skyybazaar_0.1.4.py). The parent copies the live data folder
(read only; default: the "HUD mod" world's mods/Skyy_SkyyBazaar - 0.1.3 data) into the scratch folder (default tools/dev/scratch/test-bazaar-0.1.4;
deleted at the end unless --keep) and starts a child: ONE fresh JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, java.io.tmpdir / TEMP / TMP in the scratch
folder; HytaleServer.jar + the 0.1.4 jar + tools/javassist.jar).
0.1.4 changes to the 0.1.3 sections: B compares 0.1.3 -> 0.1.4 (only Catalog + SkyyBazaarPlugin change; CfgRows / CfgFn differ only by
the version text); F also checks the 0.1.4 marker and every PRICE_014 price on a fresh start; P / Z use the new prices (Iron Ore 16 ->
bar 19.2, Onyxium 3712 -> 4454.4, Cotton 16 -> bolts 19.2, Bronze 40 and the Ancient Steel chain flagged at the 0.1.3 Bronze 21); Z5b
runs on the live 0.1.2 backup. NEW N: the vanilla farming path re-read from Assets.zip, the crop / seed / eternal ladders and caps, ores /
hides / logs, the loop check over vanilla + every SET jar's recipes on the runtime table. NEW S (replaces 0.1.3's 0.1.2 -> 0.1.3 S): the
live 0.1.3 data -> 0.1.4 (plain, hand-set prices incl. "already 16" / own 100 / " 12.0 " spelling / own tab / a duplicate line, CRLF, no
final newline): only moved price texts change (+ the 0.1.3 line-keeping save of moved auto prices), history copy = old bytes, marker
appended to pricing.properties with its bytes kept, trades.log PRICE / KEPT lines with undo, market kept, second start writes nothing,
the 0.1.3 Catalog reads the result, a removed marker re-runs harmlessly; failure paths (pricing.properties unreadable, config-history
not a folder - then retried, not UTF-8) change nothing; a lost 0.1.3 marker re-runs 0.1.3's update without making bars FIXED; 0.1.2 data
goes through both updates.
The 0.1.2 jar and the SkyySacks SET jar load in their own class loaders. Stand-ins (a bare JVM has no ECS): an Item asset store that knows
the product ids (Item.UNKNOWN for them, like the SkyySacks harness), an Inventory of three SimpleItemContainers, a Player allocated
without its constructor, a PlayerRef subclass that records its messages, and a coins bridge (coins:fn:get / take / add on a purse map,
the SkyyCoins contract). The build script's own derivation, auto-price and money-loop functions are read out of the generated script
(ast, never imported) and run here on the RUNTIME prices.
  A  every class of the 0.1.3 jar loads and initialises under -Xverify:all (and the 0.1.2 jar's in their own loader)
  B  class compare 0.1.2 -> 0.1.3: the money core byte-identical (Coins, Product, Market, Inv, TradeResult, Trader, BzUtil, BzCmd,
     BzPageFactory, the /bazaaradmin subcommands); changed exactly Catalog, BzPage, BzAdminCmd, BzTick, SkyyBazaarPlugin; new BzCfg + the
     7 config-kit classes; the manifest says 0.1.3
  X  engine-access audit on the final jar bytes (every class / member reference resolved with the JVM's access rules; a protected
     engine member only from its subclass) - 0 refused; control: a non-page class calling CustomUIPage.close is refused
  F  FRESH START (empty data folder): the one-time update seeds 415 products, pricing.properties marks every processed good auto + the
     marker; tabs Mining / Foraging / Farming / Combat / Smithing with 123 / 49 / 183 / 20 / 46 products in seed order
  G  every bag item has a product: the build's bag_items runs here with the REAL SkyySacks SackDefs; every derived item is a product
     whose tabs include its bag, every product's bag holds it, Combat + Smithing = every item SackDefs.catOf puts there (all Assets.zip
     ids); the two-tab items (light / medium / heavy hides + leathers) are ONE Product object, one price, in Combat AND Smithing
  P  processed premium vs inputs: every processed good = floor(raw inputs x (1 + premium), 0.01) - the Java (Catalog.reprice0) equals
     the build's auto_prices at premium 0 / 20 / 22 and after a fixed cheap charcoal (the fuel term then costs: copper bar > ore x 1.2);
     the spread cap (an admin spread of 0.05 caps the premium below 10.53 %); FIXED / auto through /bazaaradmin price (incl. the loop
     cap refusal), a raw input price change moves its processed goods; the Server Setup row through the config kit (cmdSetConsole 15 ->
     bars at 15 %, 25 refused, the after= hook, the tick catches a direct field change)
  L  money loops over the WHOLE runtime table at premium 0 / 20 / 22: the build's 0.1.2 check_assets (unchanged) and its fuel + charcoal
     extension on the prices the jar really uses - none; for every processed good sell(1) <= buy(inputs) at factor 1.0
  T  every one of the 415 products traded through the real Trader: buy 64 + sell 64 (and buy 1 + sell 1 where a single sale is worth a
     coin): the purse moves by exactly the quoted totals, the items by exactly the amounts, a sell never pays more than the buy cost,
     the market factor moves and is saved; nothing created or lost
  S  SAVED STATE on a scratch COPY of the live data folder, started TWICE (BzCfg.load, migrate, load, Market.load, reprice, publishAll,
     flushIfDirty, a tick, flush): market.properties keeps every factor / counter / setting; products.properties: default lines updated
     (bars -> Smithing + auto price, Life Essence -> Farming, hides / leathers -> Smithing), every other byte kept, 379 lines appended;
     products.properties.v012bak = the old bytes; the second start changes no byte and writes no file. Variants: hand-edited lines (a bar
     price, a category) kept byte for byte (the bar FIXED), 0.1.2 "6.0" number style, CRLF endings, an unreadable pricing.properties
     (nothing overwritten), a missing marker re-run (idempotent). The migrated file still loads in the 0.1.2 Catalog (rollback)
  W  the page on real data through the engine's UICommandBuilder / UIEventBuilder in 11 states (each tab, the last Farming page, nothing /
     a raw / a processed / a two-tab product selected, 7 tabs, no coins bridge, Sell inventory armed): every appended markup passes the
     kit's check_markup + assert_proven, every row fits 1046 px (used_width), the body is exactly 835 px (used_height), every b.set
     target exists, one binding per shown cell + the pager / tabs / Close; the page clicks tab / prev / next / close / cell move the
     right state; the processed-goods and price lines fit one line (the client's font tables)
  Z  FIX ROUND (review 2026-10-03), one block per finding: (1) the build's loop_check self-test, and the check flags the Ancient Steel
     chain when Bronze is put back to 16 (premium 20) while the jar's prices have no loop at every premium 0..22 (L); (2) the total bag
     guard re-run (every SackDefs.catOf item listed or skipped), the reviewer's missing materials listed in their tab, skip samples per
     reason; (3) Onyxium / Prisma Ingot follow their ores (AUTO, admin ore change moves them); (4) the cloth bolts are AUTO (cotton /
     wool scraps x (1 + premium), follow an admin cotton change, "weaving" line, "(1 makes 4)"); Dawnstone not premium-stacked;
     the admin price guard (the jar's recipe edges = the build's, Java loopingEdges = the build's edge_loops, 7 loop-making admin prices
     refused with nothing changed, the start / reload warning, an old loop does not block an unrelated price, a safe price passes);
     (5a) a FIXED processed good above its no-loop limit is held at it (+ the hand-edit variant of S); (5b) lines load() refuses
     (category over 16 characters, price 0, price 2e9) do not hide a product - its seed line is appended; (5c) a save keeps the file:
     a premium change rewrites only the moved lines, CRLF + comments + "6.0" spellings stay
Not testable without the game (UNVERIFIED in the build docstring): how the client draws the kit page, the real world thread and packet
timing, SkyyMenu's Server Setup page for the new row. Nothing is deployed. Default scratch folder tools/dev/scratch/test-bazaar-0.1.4
(deleted at the end unless --keep); --dir must be INSIDE tools/dev/scratch and new, empty or an earlier run's (marker file). Live data
is only READ (copied). Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, zipfile, math, subprocess, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.1.4", "0.1.3"
PKG = "com.skyy.bazaar."
SCRIPT = os.path.join(HERE, "build_skyybazaar_%s.py" % VERSION)
MARK = ".skyybazaar-0.1.4-harness"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH_ROOT = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
SCRATCH = os.path.realpath(os.path.abspath(arg("--dir", os.path.join(SCRATCH_ROOT, "test-bazaar-0.1.4"))))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyBazaar-%s.jar" % OLD_VERSION)))
HYTALE = os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale")
LIVE = os.path.abspath(arg("--live", os.path.join(HYTALE, "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyBazaar")))
KEEP = "--keep" in sys.argv
FAILS, OKS = [], [0]
# fix round counts (the build prints the same): 415 products, tabs, 41 processed goods; the live 0.1.2 file has 36 product lines
N_PROD, N_PROC = 415, 41
TAB_SIZES = {"Mining": 123, "Foraging": 49, "Farming": 183, "Combat": 20, "Smithing": 46}


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL:", what)
    return bool(cond)


def sacks_jar():
    t = ast.parse(open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf8").read())
    for n in t.body:
        if isinstance(n, ast.Assign) and any(getattr(x, "id", "") == "SET" for x in n.targets):
            return os.path.join(ROOT, "SkyySacks", "SkyySacks-%s.jar" % dict(ast.literal_eval(n.value))["SkyySacks"])
    raise SystemExit("no SET in tools/deploy_set.py")


SACKS = os.path.abspath(arg("--sacks", sacks_jar()))


def build_namespace():
    """the build script's own tables + functions, read with ast (never imported: importing would run the build)"""
    src = open(SCRIPT, encoding="utf8").read()
    t = ast.parse(src)
    want_f = {"_load_json", "check_assets", "load_assets", "asset_model", "bag_items", "processed_table", "proc_order", "fuel_list",
              "auto_prices", "loop_check", "loop_check_selftest", "edge_table", "edge_loops", "set_jars", "set_model", "farming_path"}
    want_v = {"SPREAD", "BAG_TABS", "ALL_OF_BAG", "SKIP", "NOSRC", "PREMIUM_BENCHES", "PREMIUM_ITEMS", "PREMIUM_DEF",
              "PREMIUM_MIN", "PREMIUM_MAX", "AUTO", "PRODUCTS", "EXTRA_TABS", "PRODUCTS_012", "PRICE_014", "VANILLA_SEED_TIER",
              "PRICE_TIER", "CROP_PRICE", "SEED_PRICE", "ETERNAL_PRICE", "SEED_CAP", "ETERNAL_CAP", "SAPLING_TIER", "SAPLING_ESSENCE"}
    body = []
    got_f, got_v = set(), set()
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
    from jpype import JClass, JArray, JShort, JString
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, JAR, B.JAVASSIST], convertStrings=True)
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    URL, UCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
    NS = build_namespace()

    # ---------------- A. load + verify
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(JAR).namelist() if n.endswith(".class")]
    for n in names:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("load " + n + ": " + str(e))
            print("LOAD FAIL", n, e)
    # the 0.1.3 jar with its OWN copy of the engine classes (parent = the platform loader: never the 0.1.3 classes of the classpath)
    old_loader = UCL(JArray(URL)([File(OLD).toURI().toURL(), File(B.SERVER_JAR).toURI().toURL()]),
                     JClass("java.lang.ClassLoader").getPlatformClassLoader())
    old_names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(OLD).namelist() if n.endswith(".class")]
    for n in old_names:
        try:
            Cls.forName(n, False, old_loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("load 0.1.3 " + n + ": " + str(e))
    print("A. loaded + verified %d classes of 0.1.4 (-Xverify:all) and %d of 0.1.3 (own loader)" % (len(names), len(old_names)))
    if FAILS:
        return

    # ---------------- B. class compare
    za, zb = zipfile.ZipFile(OLD), zipfile.ZipFile(JAR)
    ca = dict((n.split("/")[-1][:-6], za.read(n)) for n in za.namelist() if n.endswith(".class"))
    cb = dict((n.split("/")[-1][:-6], zb.read(n)) for n in zb.namelist() if n.endswith(".class"))
    same = ["Coins", "Product", "Market", "Inv", "TradeResult", "Trader", "BzUtil", "BzCmd", "BzPageFactory", "BzAdmPriceCmd",
            "BzAdmPriceShowCmd", "BzAdmReloadCmd", "BzAdmResetCmd", "BzAdmInfoCmd", "BzPage", "BzAdminCmd", "BzTick", "BzCfg",
            "CfgLog", "CfgHist", "CfgSaveTask", "CfgFile", "CfgPub"]
    changed = ["Catalog", "SkyyBazaarPlugin", "CfgRows", "CfgFn"]          # CfgRows / CfgFn carry the mod version (kit)
    for c in ("CfgRows", "CfgFn"):
        check(c in ca and c in cb and ca[c].replace(b"0.1.3", b"0.1.4") == cb[c], "class %s differs only by the version text" % c)
    for c in same:
        check(c in ca and c in cb and ca[c] == cb[c], "class %s byte-identical 0.1.3 -> 0.1.4" % c)
    for c in changed:
        check(c in ca and c in cb and ca[c] != cb[c], "class %s changed" % c)
    check(set(cb) == set(ca), "no class added or removed: %s / %s" % (sorted(set(cb) - set(ca)), sorted(set(ca) - set(cb))))
    check(sorted(set(ca)) == sorted(same + changed), "every 0.1.3 class is either identical or one of the 3 changed")
    man = json.loads(zb.read("manifest.json"))
    check(man["Version"] == VERSION and man["Name"] == "0.1.4 SkyyBazaar" and man["Main"] == "com.skyy.bazaar.SkyyBazaarPlugin", "manifest")
    print("B. class compare 0.1.3 -> 0.1.4: %d identical, %d changed (%s)" % (len(same), len(changed), ", ".join(changed)))

    # ---------------- X. engine-access audit on the jar bytes (the build's rule, with javassist on the real engine classes)
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    jp.appendClassPath(JAR)
    Mod = JClass("javassist.Modifier")
    CP = JClass("javassist.bytecode.ConstPool")
    CF, DI, BI = JClass("javassist.bytecode.ClassFile"), JClass("java.io.DataInputStream"), JClass("java.io.ByteArrayInputStream")
    AOPS = {0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5, 0x12, 0x13}

    def pkg(n):
        return n.rsplit(".", 1)[0] if "." in n else ""

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
                    if op in (0x12, 0x13) and tag != CP.CONST_Class:
                        continue
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        cname, member = str(cp.getClassInfo(idx)), None
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        cname, member = str(cp.getFieldrefClassName(idx)), ("field", str(cp.getFieldrefName(idx)), str(cp.getFieldrefType(idx)))
                    elif tag == CP.CONST_InterfaceMethodref:
                        cname, member = str(cp.getInterfaceMethodrefClassName(idx)), ("method", str(cp.getInterfaceMethodrefName(idx)), str(cp.getInterfaceMethodrefType(idx)))
                    else:
                        cname, member = str(cp.getMethodrefClassName(idx)), ("method", str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                    seen += 1
                    try:
                        en = elem(cname)
                        if en is not None and pkg(en) != pkg(dn) and not Mod.isPublic(jp.get(en).getModifiers()):
                            refused.append("%s: class %s not public" % (dn, en))
                        if member is None:
                            continue
                        kind, name, desc = member
                        Cc = jp.get("java.lang.Object" if cname.startswith("[") else cname)
                        x = Cc.getField(name, desc) if kind == "field" else (Cc.getConstructor(desc) if name == "<init>" else Cc.getMethod(name, desc))
                        md, decl = x.getModifiers(), x.getDeclaringClass()
                        dcn = str(decl.getName())
                        if Mod.isPublic(md) or (pkg(dcn) == pkg(dn) and not Mod.isPrivate(md)):
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
    check(not refused and seen > 2000, "access audit: %d references, refused %s" % (seen, refused[:5]))
    ctl = jp.makeClass(PKG + "AuditControl")
    ctl.addMethod(JClass("javassist.CtNewMethod").make(
        "public static void bad(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) { p.close(); }", ctl))
    r2, _u2, _s2 = audit([(ctl, CF(DI(BI(ctl.toBytecode()))))])
    check(len(r2) == 1 and "close" in r2[0], "access audit control refused: %s" % r2)
    print("X. access audit: %d references, 0 refused; non-public used from their subclass: %s; control refused" % (seen, ", ".join(sorted(used))))

    # ---------------- engine stand-ins (the SkyySacks harness pattern)
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyBzFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyyBzFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    store = us.allocateInstance(fake.toClass(AS.class_))
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    DAMN = "com.hypixel.hytale.assetstore.map.DefaultAssetMap"
    kmap = jp.makeClass("com.hypixel.hytale.assetstore.map.SkyyBzKnownMap", jp.get(DAMN))
    kmap.addField(JClass("javassist.CtField").make("public static final java.util.HashSet KNOWN = new java.util.HashSet();", kmap))
    kmap.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyBzKnownMap() { super(); }", kmap))
    kmap.addMethod(JClass("javassist.CtNewMethod").make(
        "public com.hypixel.hytale.assetstore.JsonAsset getAsset(Object key) { if (key != null && KNOWN.contains(key)) "
        "return com.hypixel.hytale.server.core.asset.type.item.config.Item.UNKNOWN; return super.getAsset(key); }", kmap))
    KMap = JClass(kmap.toClass(JClass(DAMN).class_))
    fm.set(store, KMap())
    fi_ = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item").class_.getDeclaredField("ASSET_STORE")
    fi_.setAccessible(True)
    fi_.set(None, store)
    INVN = "com.hypixel.hytale.server.core.inventory.Inventory"
    ICN = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
    tinv = jp.makeClass("com.hypixel.hytale.server.core.inventory.SkyyBzTestInv", jp.get(INVN))
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
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
    # the coins bridge (SkyyCoins contract: get(UUID) -> Long, take(Object[]{UUID, Long}) -> Boolean, add(Object[]{UUID, Long}) -> Long),
    # Python Function proxies on one purse map (jpype JImplements)
    from jpype import JImplements, JOverride
    LongJ, BoolJ = JClass("java.lang.Long"), JClass("java.lang.Boolean")

    class Purse:
        P = {}

        @staticmethod
        def get(u):
            return Purse.P.get(str(u), 0)

    @JImplements("java.util.function.Function")
    class CoinsGet:
        @JOverride
        def apply(self, o):
            return LongJ(Purse.get(o))

    @JImplements("java.util.function.Function")
    class CoinsTake:
        @JOverride
        def apply(self, o):
            u, n = o[0], int(o[1].longValue())
            h = Purse.get(u)
            if n <= 0 or h < n:
                return BoolJ.FALSE
            Purse.P[str(u)] = h - n
            return BoolJ.TRUE

    @JImplements("java.util.function.Function")
    class CoinsAdd:
        @JOverride
        def apply(self, o):
            u, n = o[0], int(o[1].longValue())
            Purse.P[str(u)] = Purse.get(u) + n
            return LongJ(Purse.P[str(u)])
    UUID, Paths, Long_ = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long")
    System = JClass("java.lang.System")
    bridge = JClass("java.util.concurrent.ConcurrentHashMap")()
    System.getProperties().put("skyy.bridge", bridge)

    def coins_on():
        bridge.put("coins:fn:get", CoinsGet())
        bridge.put("coins:fn:take", CoinsTake())
        bridge.put("coins:fn:add", CoinsAdd())

    def coins_off():
        for k in ("coins:fn:get", "coins:fn:take", "coins:fn:add"):
            bridge.remove(k)
    coins_on()
    U1 = UUID.fromString("00000000-0000-0000-0000-00000000b0b0")
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

    def player():
        p = us.allocateInstance(PLA.class_)
        inv_field.set(p, TInv(SIC(JShort(36)), SIC(JShort(9)), SIC(JShort(9))))
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

    def pref(name="Tester"):
        pr = us.allocateInstance(TPR.class_)
        jfield(JClass(PRN).class_, "uuid").set(pr, U1)
        jfield(JClass(PRN).class_, "username").set(pr, JString(name))
        return pr

    Jc = lambda n: JClass(PKG + n)
    Cat, Mkt, Cfg, Trd, Page, Adm, Fn, Pub, Tick = (Jc("Catalog"), Jc("Market"), Jc("BzCfg"), Jc("Trader"), Jc("BzPage"), Jc("BzAdminCmd"),
                                                    Jc("CfgFn"), Jc("CfgPub"), Jc("BzTick"))
    SEED = [str(x) for x in Cat.SEED]
    PIDS = [s.split("=", 1)[0] for s in SEED]
    for pid in PIDS:
        KMap.KNOWN.add(pid)
    KMap.KNOWN.add("Skyy_Test_Admin_Item")

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

    LAST14 = [None]

    def start(d):
        """SkyyBazaarPlugin.setup()'s data steps on folder d (the commands / scheduler / kit publish need the server)"""
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
        Cat.warnLoops(Mkt.SPREAD)          # fix round: setup warns about recipes that pay at the prices on disk
        if mig is not None:
            Mkt.log(mig)
        if mig14 is not None:
            for x in Cat.M14_LOG:
                Mkt.log(x)
        Cat.M14_LOG.clear()
        LAST14[0] = None if mig14 is None else str(mig14)
        return mig, n

    def files(d):
        out = {}
        for root, _ds, fs in os.walk(d):
            for f in fs:
                p = os.path.join(root, f)
                out[os.path.relpath(p, d)] = open(p, "rb").read()
        return out

    def props(path):
        out = {}
        for ln in open(path, encoding="utf8").read().splitlines():
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                out[k] = v
        return out

    def base_of(pid):
        return float(Cat.get(pid).base)

    def runtime_prices():
        return dict((str(p.id), float(p.base)) for p in Cat.all())

    # ---------------- F. fresh start
    reset_state()
    d0 = os.path.join(SCRATCH, "fresh")
    os.makedirs(d0)
    mig, n = start(d0)
    check(mig is not None and ("seeded %d" % N_PROD) in str(mig), "fresh start seeds %d products: %s" % (N_PROD, mig))
    check(n == N_PROD and len(SEED) == N_PROD, "%d products loaded (%d)" % (N_PROD, n))
    pf = props(os.path.join(d0, "pricing.properties"))
    procs = [str(e[0]) for e in Cat.PROC]
    check(len(procs) == N_PROC and procs[0] == "Ingredient_Charcoal", "%d processed goods, charcoal first: %s" % (N_PROC, procs[:3]))
    check(procs.index("Rock_Quartzite") < procs.index("Rock_Dawnstone") and procs.index("Rock_Quartzite") < procs.index("Rock_Dawnstone_Cobble"),
          "PROC order: Quartzite before the Dawnstone made from it")
    check(all(pf.get("mode." + p) == "auto" for p in procs) and pf.get("migrated.0.1.3"), "pricing.properties: every processed good auto + marker")
    check(pf.get("migrated.0.1.4") and LAST14[0] is not None and ("rewrote 0 kept 0 already %d" % len(NS["PRICE_014"])) in LAST14[0],
          "fresh start: the 0.1.4 update finds every price already at 0.1.4 and marks itself done (%s)" % LAST14[0])
    check(not os.path.exists(os.path.join(d0, "config-history")), "fresh start: no history copy (nothing rewritten)")
    for i_, (o_, n_) in NS["PRICE_014"].items():
        check(abs(base_of(i_) - n_) < 1e-9, "fresh start: %s at its 0.1.4 price %s (%s)" % (i_, n_, base_of(i_)))
    cats = [str(c) for c in Cat.categories()]
    check(cats == ["Mining", "Foraging", "Farming", "Combat", "Smithing"], "tabs %s" % cats)
    sizes = dict((c, Cat.inCat(c).size()) for c in cats)
    check(sizes == TAB_SIZES, "tab sizes %s" % sizes)
    order = [str(p.id) for p in Cat.inCat("Mining")]
    check(order == [s_.split("=", 1)[0] for s_ in SEED if s_.split("=", 1)[1].startswith("Mining,")],
          "Mining tab in seed order (ores by tier first): %s" % order[:3])
    lines = open(os.path.join(d0, "products.properties"), encoding="utf8").read().splitlines()
    check([l for l in lines if not l.startswith("#")] == SEED, "fresh products.properties = the %d seed lines" % N_PROD)
    print("F. fresh start: %d products, %d processed (auto), tabs %s" % (N_PROD, N_PROC, sizes))

    # ---------------- G. every bag item has a product (the build's own derivation with the real SkyySacks rule)
    sl = UCL(JArray(URL)([File(SACKS).toURI().toURL()]), JClass("java.lang.ClassLoader").getPlatformClassLoader())
    Defs = JClass(Cls.forName("com.skyy.sacks.SackDefs", True, sl))

    def bag_of(i):
        c = Defs.catOf(i)
        return None if c is None else str(c)
    NS["bag_of"] = bag_of
    js, data, drops, recfiles, lang = NS["load_assets"]()
    M = NS["asset_model"](js, data, drops, recfiles)
    bags, why, skipped, bnames = NS["bag_items"](js, data, drops, M, lang)
    tot = 0
    for b, ids in bags.items():
        for i in ids:
            p = Cat.get(i)
            tot += 1
            check(p is not None and b in [str(t) for t in Cat.tabsOf(p)], "bag item %s (%s) is a product in its tab" % (i, b))
    # fix round: the guard is total - every id SackDefs.catOf puts in a bag is listed or skipped, never both, never neither
    listed = set(i for l in bags.values() for i in l)
    skip_ids = dict((i, r) for _b, i, r in skipped)
    catof = [i for i in sorted(data) if bag_of(i) is not None]
    check(len(catof) == len(listed) + len(skip_ids) and not (listed & set(skip_ids)) and all(i in listed or i in skip_ids for i in catof),
          "total bag guard: %d bag items = %d listed + %d skipped" % (len(catof), len(listed), len(skip_ids)))
    check(not [i for i in PIDS if i in skip_ids], "no product is a skipped bag item")
    check(all(r in [x[1] for x in NS["SKIP"]] or r == NS["NOSRC"] for r in skip_ids.values()), "every skip carries a written reason")
    for pid in PIDS:
        b = bag_of(pid)
        check(b is not None and b in [str(t) for t in Cat.tabsOf(Cat.get(pid))], "product %s is held by the %s bag" % (pid, b))
    for i in sorted(data):
        b = bag_of(i)
        if b in ("Combat", "Smithing"):
            check(Cat.get(i) is not None, "every %s bag item is listed: %s" % (b, i))
    two = ["Ingredient_Hide_Light", "Ingredient_Hide_Medium", "Ingredient_Hide_Heavy", "Ingredient_Leather_Light",
           "Ingredient_Leather_Medium", "Ingredient_Leather_Heavy"]
    combat = list(Cat.inCat("Combat"))
    smith = list(Cat.inCat("Smithing"))
    for pid in two:
        pc = [p for p in combat if str(p.id) == pid]
        ps = [p for p in smith if str(p.id) == pid]
        check(len(pc) == 1 and len(ps) == 1 and pc[0].equals(ps[0]) and pc[0] is not None and Cat.get(pid).equals(pc[0]),
              "%s: one Product object in Combat and Smithing" % pid)
        check([str(t) for t in Cat.tabsOf(Cat.get(pid))] == ["Combat", "Smithing"], "%s tabs Combat + Smithing" % pid)
    print("G. bag rule (SkyySacks %s, the build's bag_items): %d bag items, all listed in their tab; Combat + Smithing = every catOf id; "
          "6 two-tab items share one Product" % (os.path.basename(SACKS), tot))

    # ---------------- P. processed premium vs inputs
    fuels, charcoal = NS["fuel_list"](M, set(PIDS))
    proc_py = NS["processed_table"](M, set(PIDS))
    fixed_base = dict((pid, base_of(pid)) for pid in PIDS if pid not in proc_py)
    check(set(proc_py) == set(procs), "the jar's processed table = the build's")
    for prem in (0, 20, 22):
        Cfg.PREMIUM = prem
        Cat.reprice()
        want = NS["auto_prices"](fixed_base, proc_py, fuels, charcoal, prem / 100.0)
        for pid in procs:
            check(abs(base_of(pid) - want[pid]) < 1e-9, "premium %d: %s = %s (build %s)" % (prem, pid, base_of(pid), want[pid]))
        bar, ore = base_of("Ingredient_Bar_Copper"), base_of("Ore_Copper")
        check(abs(bar - math.floor(ore * (1 + prem / 100.0) * 100 + 1e-9) / 100) < 1e-9, "copper bar = ore x %d%% (%s)" % (100 + prem, bar))
        for pid in procs:
            e = Cat.procEntry(pid)
            v = float(Cat.valueOf(e))
            check(base_of(pid) <= v * (1 + prem / 100.0) + 1e-9 and base_of(pid) >= v * (1 + prem / 100.0) - 0.01 - 1e-9,
                  "%s within 0.01 below inputs x (1 + %d%%)" % (pid, prem))
    Cfg.PREMIUM = 20
    Cat.reprice()
    pr = pref("Admin")
    TPR.SAID.clear()
    # fixed cheap charcoal -> the fuel term costs something: the copper bar rises above ore x 1.2 by the fuel's net cost
    Adm.run(pr, "price", "Ingredient_Charcoal", "0.5")
    check(not Cat.isAuto("Ingredient_Charcoal") and base_of("Ingredient_Charcoal") == 0.5, "charcoal FIXED at 0.5")
    fb2 = dict(fixed_base); fb2["Ingredient_Charcoal"] = 0.5
    p2 = dict((k, v) for k, v in proc_py.items() if k != "Ingredient_Charcoal")
    want = NS["auto_prices"](fb2, p2, fuels, charcoal, 0.20)
    check(abs(base_of("Ingredient_Bar_Copper") - want["Ingredient_Bar_Copper"]) < 1e-9 and want["Ingredient_Bar_Copper"] > 6.0,
          "fuel term: copper bar %s = build %s > 6.0 (ore x 1.2)" % (base_of("Ingredient_Bar_Copper"), want["Ingredient_Bar_Copper"]))
    # loop cap: a fixed bar price above inputs x 1.1 / 0.9 is refused and changes nothing
    cap = float(Cat.loopCap("Ingredient_Bar_Iron"))
    before = base_of("Ingredient_Bar_Iron")
    Adm.run(pr, "price", "Ingredient_Bar_Iron", str(cap + 1))
    check(base_of("Ingredient_Bar_Iron") == before and Cat.isAuto("Ingredient_Bar_Iron") and "at most" in str(TPR.SAID[-1]),
          "loop cap refusal (%s > %s): %s" % (cap + 1, cap, TPR.SAID[-1]))
    Adm.run(pr, "price", "Ingredient_Bar_Iron", str(round(cap - 0.5, 2)))
    check(abs(base_of("Ingredient_Bar_Iron") - round(cap - 0.5, 2)) < 1e-9 and not Cat.isAuto("Ingredient_Bar_Iron"), "bar FIXED under the cap")
    Adm.run(pr, "price", "Ingredient_Charcoal", "auto")
    check(Cat.isAuto("Ingredient_Charcoal") and abs(base_of("Ingredient_Charcoal") - 2.4) < 1e-9, "charcoal auto -> 2.4")
    Adm.run(pr, "price", "Ingredient_Bar_Iron", "auto")
    check(Cat.isAuto("Ingredient_Bar_Iron") and abs(base_of("Ingredient_Bar_Iron") - 19.2) < 1e-9, "price auto -> 19.2 again (%s)" % base_of("Ingredient_Bar_Iron"))
    Adm.run(pr, "price", "Ore_Iron", "auto")
    check("only processed goods" in str(TPR.SAID[-1]) and base_of("Ore_Iron") == 16.0, "auto refused on a raw good")
    # a raw input price change moves its processed good
    Adm.run(pr, "price", "Ore_Iron", "10")
    check(base_of("Ore_Iron") == 10.0 and abs(base_of("Ingredient_Bar_Iron") - 12.0) < 1e-9, "ore 10 -> bar 12.0 (%s)" % base_of("Ingredient_Bar_Iron"))
    Adm.run(pr, "price", "Ore_Iron", "16")
    check(abs(base_of("Ingredient_Bar_Iron") - 19.2) < 1e-9, "ore back to 16 -> bar 19.2")
    pf = props(os.path.join(d0, "pricing.properties"))
    check(pf.get("mode.Ingredient_Bar_Iron") == "auto" and pf.get("migrated.0.1.3") and pf.get("migrated.0.1.4"),
          "pricing.properties saved by the admin path, both markers kept")
    # the spread cap
    Mkt.SPREAD = 0.05
    Cat.reprice()
    eff = float(Cfg.effective())
    check(eff < 2 * 0.05 / 0.95 and abs(base_of("Ingredient_Bar_Copper") - math.floor(5 * (1 + eff) * 100 + 1e-9) / 100) < 1e-9,
          "spread 0.05 caps the premium at %.4f (bar %s)" % (eff, base_of("Ingredient_Bar_Copper")))
    check(base_of("Ingredient_Bar_Copper") * 0.95 <= 5 * 1.05 + 1e-9, "spread 0.05: sell(bar) <= buy(ore)")
    Mkt.SPREAD = 0.10
    Cat.reprice()
    # the Server Setup row through the config kit
    os.makedirs(os.path.join(SCRATCH, "fresh_mods", "Skyy_SkyyBazaar"), exist_ok=True)
    Pub.start(Paths.get(os.path.join(SCRATCH, "fresh_mods")), None)
    msg = str(Fn.cmdSetConsole("processed.premium", "15"))
    check(int(Cfg.PREMIUM) == 15 and abs(base_of("Ingredient_Bar_Copper") - 5.75) < 1e-9, "kit set 15: %s / bar %s" % (msg, base_of("Ingredient_Bar_Copper")))
    msg = str(Fn.cmdSetConsole("processed.premium", "25"))
    check(int(Cfg.PREMIUM) == 15 and "22" in msg, "kit refuses 25: %s" % msg)
    defv = JClass("java.lang.System").getProperties().get("skyy.bridge").get("config:def:SkyyBazaar")
    check(defv is not None and str(defv[1]) == "SkyyBazaar" and str(defv[7][0][0]) == "processed.premium", "config:def:SkyyBazaar published")
    Cfg.PREMIUM = 20            # a hand edit applied by the kit sets the field without the after= hook: the tick catches it
    Cat.tick()
    check(abs(base_of("Ingredient_Bar_Copper") - 6.0) < 1e-9, "tick reprices after a direct field change")
    Pub.flush()
    print("P. premium: Java = build at 0/20/22 %%, fuel term with cheap charcoal (bar %s), loop cap %s, admin fixed / auto, raw input moves "
          "its bar, spread cap, kit row 15 / 25 refused, tick" % (want["Ingredient_Bar_Copper"], cap))

    # ---------------- L. money loops over the whole runtime table (fix round: the 0.1.3 check at EVERY whole premium 0..22, like the build)
    for prem in range(0, 23):
        Cfg.PREMIUM = prem
        Cat.reprice()
        px = runtime_prices()
        check(len(px) == N_PROD, "runtime table has %d prices" % N_PROD)
        if prem in (0, 15, 20, 22):
            try:
                NS["check_assets"](px, NS["SPREAD"])
                OKS[0] += 1
            except SystemExit as e:
                FAILS.append("check_assets at %d%%: %s" % (prem, e))
        try:
            loops, costable, nrec, passes = NS["loop_check"](M, px, NS["SPREAD"])
        except SystemExit as e:
            loops = ["did not reach a fixed point: %s" % e]
        check(not loops, "co-product + liquidation loop check at %d%%: %s" % (prem, loops[:3]))
        for pid in procs:
            e = Cat.procEntry(pid)
            v = float(Cat.valueOf(e))
            check(px[pid] * (1 - NS["SPREAD"]) <= v * (1 + NS["SPREAD"]) + 1e-9, "%s: sell(1) <= buy(inputs) at %d%%" % (pid, prem))
    Cfg.PREMIUM = 20
    Cat.reprice()
    print("L. money loops on the jar's runtime prices: 0.1.2 check_assets at 0 / 15 / 20 / 22 %, the co-product + liquidation check at every "
          "premium 0-22 %: none")

    # ---------------- N. 0.1.4 progression prices: the vanilla farming path re-read, the ladders, the SET jars' recipes on the runtime table
    fp = NS["farming_path"](data)
    check(fp == NS["VANILLA_SEED_TIER"], "N: Farmingbench seed tiers in Assets.zip = VANILLA_SEED_TIER: %s" % fp)
    for c_, vt in fp.items():
        t_ = NS["PRICE_TIER"][vt]
        for i_, want_, cap_ in (("Plant_Crop_%s_Item" % c_, NS["CROP_PRICE"][t_], None), ("Plant_Seeds_%s" % c_, NS["SEED_PRICE"][t_], NS["SEED_CAP"].get(c_)),
                                ("Plant_Seeds_%s_Eternal" % c_, NS["ETERNAL_PRICE"][t_], NS["ETERNAL_CAP"].get(c_))):
            check(abs(base_of(i_) - (want_ if cap_ is None else cap_)) < 1e-9, "N: %s (vanilla tier %d -> price tier %d) = %s" % (i_, vt, t_, base_of(i_)))
    # saplings: x2 per log tier of the 0.1.3 sapling price, capped at floor-to-0.5 of 0.6 x the Essence of Life of their recipe (own or
    # inherited); the same cap rule gives the seed caps; every capped price keeps buy essence -> craft -> sell below 1.0
    old_sap = dict((str(x).split("=", 1)[0], float(str(x).split(",")[1])) for x in JClass(Cls.forName("com.skyy.bazaar.Catalog", True, old_loader)).SEED)
    for s_, tier_ in NS["SAPLING_TIER"].items():
        i_ = "Plant_Sapling_" + s_
        n_ess = NS["SAPLING_ESSENCE"][s_]
        cap_ = None if n_ess is None else math.floor(0.6 * n_ess * 2 + 1e-9) / 2.0
        want_ = old_sap[i_] * 2 ** (tier_ - 1)
        exp_ = want_ if cap_ is None or want_ <= cap_ else cap_
        check(abs(base_of(i_) - exp_) < 1e-9 and base_of(i_) >= old_sap[i_], "N: %s tier %d: %s (0.1.3 %s, cap %s)" % (i_, tier_, base_of(i_), old_sap[i_], cap_))
        if n_ess is not None:
            check(base_of(i_) * 0.9 < n_ess * 0.5 * 1.1, "N: %s: buy %d essence -> craft -> sell does not pay" % (i_, n_ess))
    ladder = [base_of(o) for o in ("Ore_Copper", "Ore_Iron", "Ore_Thorium", "Ore_Cobalt", "Ore_Adamantite", "Ore_Mithril", "Ore_Onyxium")]
    check(ladder == [5.0, 16.0, 48.0, 144.0, 480.0, 1440.0, 3712.0] and all(abs(ladder[k] - [5, 8, 12, 18, 30, 45, 58][k] * 2 ** k) < 1e-9 for k in range(7)),
          "N: ores = 0.1.3 x 2^tier step: %s" % ladder)
    hides = [base_of("Ingredient_Hide_" + h) for h in ("Soft", "Light", "Medium", "Heavy", "Scaled", "Storm", "Dark", "Prismic")]
    check(hides == [8.0, 12.0, 24.0, 36.0, 48.0, 60.0, 72.0, 90.0], "N: hides x2 flat: %s" % hides)
    check([base_of("Ingredient_Leather_" + h) for h in ("Light", "Medium", "Heavy")] == [14.4, 28.8, 43.2], "N: leathers follow (+20%)")
    check([base_of(w) for w in ("Wood_Oak_Trunk", "Wood_Bamboo_Trunk", "Wood_Maple_Trunk", "Wood_Redwood_Trunk", "Wood_Azure_Trunk", "Wood_Fire_Trunk",
                                "Wood_Hardwood_Planks")] == [3.0, 2.0, 8.0, 20.0, 48.0, 128.0, 2.0], "N: logs x2 per tier, planks unchanged")
    SM, scan = NS["set_model"](M, data)
    check(len(SM["recipes"]) > len(M["recipes"]) and any(m_ == "SkyySacks" and r_ == 21 for m_, _i, r_ in scan),
          "N: the SET jars add recipes (%s)" % [(m_, i_, r_) for m_, i_, r_ in scan if i_ or r_])
    for prem in (0, 20, 22):
        Cfg.PREMIUM = prem
        Cat.reprice()
        loops = NS["loop_check"](SM, runtime_prices(), NS["SPREAD"])[0]
        check(not loops, "N: vanilla + SET jar recipes on the runtime table at %d%%: no loop %s" % (prem, [l[1] for l in loops[:3]]))
    Cfg.PREMIUM = 20
    Cat.reprice()
    print("N. progression prices: vanilla farming path re-read (%s), crop / seed / eternal ladders + caps, ores / hides / logs, the SET jars' "
          "%d extra recipes - no loop at 0 / 20 / 22 %%" % (", ".join("%s %d" % kv for kv in sorted(fp.items(), key=lambda x: x[1])),
                                                             len(SM["recipes"]) - len(M["recipes"])))

    # ---------------- T. every product traded
    Mkt.reset(None)
    maxst = int(JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item").UNKNOWN.getMaxStack())
    QB = min(64, 54 * max(1, maxst))
    pl = player()
    Purse.P[str(U1)] = 10 ** 12
    traded = 0
    for pid in PIDS:
        for q in (QB, 1):
            qb = int(Mkt.quote(pid, q, True))
            p0 = Purse.get(U1)
            h0 = held(pl, pid)
            r = Trd.buy(pl, U1, "Tester", pid, q)
            got = held(pl, pid) - h0
            check(bool(r.ok) and int(r.qty) == q and got == q and p0 - Purse.get(U1) == int(r.coins) == qb,
                  "buy %d %s: ok %s qty %s got %d paid %d quote %d" % (q, pid, r.ok, r.qty, got, p0 - Purse.get(U1), qb))
            qs = int(Mkt.quote(pid, q, False))
            p1 = Purse.get(U1)
            if qs <= 0:
                # a single 0.5-coin item sells for 0 coins: 0.1.2's refusal ("sell more at once") - nothing moves, the item stays
                r2 = Trd.sell(pl, U1, "Tester", pid, q)
                check(not r2.ok and held(pl, pid) == h0 + q and Purse.get(U1) == p1, "a 0-coin sale of %s is refused, nothing moves" % pid)
                check(int(Jc("Inv").take(pl, pid, q)) == q and held(pl, pid) == h0, "test cleanup: the unsold %s taken back out" % pid)
                continue
            r2 = Trd.sell(pl, U1, "Tester", pid, q)
            check(bool(r2.ok) and int(r2.qty) == q and held(pl, pid) == h0 and Purse.get(U1) - p1 == int(r2.coins) == qs,
                  "sell %d %s: ok %s back to %d, paid %d quote %d" % (q, pid, r2.ok, held(pl, pid), Purse.get(U1) - p1, qs))
            check(qs <= qb, "%s: selling %d never pays more than buying (%d <= %d)" % (pid, q, qs, qb))
            traded += 1
        check(Mkt.getBought(pid) >= QB and Mkt.getSold(pid) >= QB, "%s lifetime counters moved" % pid)
    left = [pid for pid in PIDS if held(pl, pid) != 0]
    check(not left, "nothing left over in the inventory: %s" % left[:5])
    Mkt.flush()
    mp = props(os.path.join(d0, "market.properties"))
    check(any(k.startswith("f.Rock_Gem_Diamond") for k in mp), "factors saved for new products")
    print("T. traded every product: %d buy + sell pairs through the real Trader, purse and items exact" % traded)

    # ---------------- S. SAVED STATE (0.1.4): scratch copies of the LIVE 0.1.3 data -> the one-time progression price update, started twice
    P14 = NS["PRICE_014"]
    BzU = Jc("BzUtil")

    def with_price(body, np_):
        """the Java Catalog.withPrice in Python (the price text only; its surrounding spaces stay)"""
        eq = body.index("=")
        c1 = body.index(",", eq + 1)
        c2 = body.find(",", c1 + 1)
        end = len(body) if c2 < 0 else c2
        tok = body[c1 + 1:end]
        a = len(tok) - len(tok.lstrip())
        b = len(tok.rstrip())
        return body[:c1 + 1] + tok[:a] + np_ + tok[b:] + body[end:]

    def expect_lines(before_txt, nl):
        """what products.properties must hold after a 0.1.4 start on before_txt: a first line of an id whose price is exactly its
        0.1.3 default -> the 0.1.4 price text; a processed good whose runtime price moved -> the line-keeping save's line; else as it was"""
        out, seen = [], set()
        for ln in before_txt.split(nl):
            p = Cat.peek(ln)
            if p is None or str(p.id) in seen:
                out.append(ln)
                continue
            pid = str(p.id)
            seen.add(pid)
            if pid in P14 and abs(float(p.base) - P14[pid][0]) < 1e-9:
                out.append(with_price(ln, "%g" % P14[pid][1]))
            elif pid in procs and abs(float(p.base) - base_of(pid)) > 1e-9:
                out.append("%s=%s,%s,%s" % (pid, p.cat, BzU.num(base_of(pid)), p.name))
            else:
                out.append(ln)
        return out

    OCat0 = JClass(Cls.forName("com.skyy.bazaar.Catalog", True, old_loader))
    check([str(x) for x in Cat.SEED013] == [str(x) for x in OCat0.SEED], "Catalog.SEED013 = the 0.1.3 jar's seed lines (%d)" % len(Cat.SEED013))
    m14 = dict(zip([str(x) for x in Cat.M14_ID], zip([float(x) for x in Cat.M14_OLD], [float(x) for x in Cat.M14_NEW])))
    check(m14 == dict((k, (float(o), float(n))) for k, (o, n) in P14.items()), "the jar's update table = the build's PRICE_014")
    old_seed_px = dict((str(x).split("=", 1)[0], float(str(x).split(",")[1])) for x in OCat0.SEED)
    check(all(abs(old_seed_px[k] - o) < 1e-9 for k, (o, n) in P14.items()), "every PRICE_014 old value = the 0.1.3 jar's seed price")
    live0 = os.path.join(SCRATCH, "live")
    if os.path.isdir(live0) and os.path.exists(os.path.join(live0, "pricing.properties")):
        old_txt = open(os.path.join(live0, "products.properties"), "rb").read().decode("utf8")
        old_pp = open(os.path.join(live0, "pricing.properties"), "rb").read()
        mk0 = props(os.path.join(live0, "market.properties"))
        check(b"migrated.0.1.3=" in old_pp and b"migrated.0.1.4" not in old_pp, "the live data is 0.1.3 data (0.1.3 marker, no 0.1.4 marker)")
        at_old = [pid for pid in P14 if re.search(r"(?m)^%s=[^,]*,%s," % (pid, re.escape("%g" % P14[pid][0])), old_txt)]
        check(len(at_old) == len(P14), "the live file holds every one of the %d moved products at its 0.1.3 default (%d)" % (len(P14), len(at_old)))
        HAND = {"Ore_Iron": ("Ore_Iron=Mining,8,Iron Ore", "Ore_Iron=Mining,16,Iron Ore"),                # set live by Skyy = the new price
                "Ore_Mithril": ("Ore_Mithril=Mining,45,Mithril Ore", "Ore_Mithril=Mining,100,Mithril Ore"),  # Skyy's own price: kept
                "Ore_Thorium": ("Ore_Thorium=Mining,12,Thorium Ore", "Ore_Thorium=Mining, 12.0 ,Thorium Ore"),  # spelling: still the default
                "Wood_Maple_Trunk": ("Wood_Maple_Trunk=Foraging,4,Maple Log", "Wood_Maple_Trunk=Wood,4,Maple Log")}  # own tab, default price
        for name, mutate in (("live", None), ("handset", "hand"), ("crlf", "crlf"), ("nofinalnl", "nonl")):
            d = os.path.join(SCRATCH, "s_" + name)
            shutil.copytree(live0, d)
            pfile = os.path.join(d, "products.properties")
            ppath = os.path.join(d, "pricing.properties")
            t = old_txt
            if mutate == "hand":
                for a_, b_ in HAND.values():
                    check(t.count(a_) == 1, "handset: the live file has %s" % a_)
                    t = t.replace(a_, b_)
                t = t + "Plant_Crop_Potato_Item=Farming,2,Potato\n"          # a duplicate (load() ignores it): never touched
            elif mutate == "crlf":
                t = t.replace("\n", "\r\n")
                open(ppath, "wb").write(old_pp.replace(b"\n", b"\r\n"))
            elif mutate == "nonl":
                t = t.rstrip("\n")
            open(pfile, "wb").write(t.encode("utf8"))
            before = open(pfile, "rb").read()
            pp_before = open(ppath, "rb").read()
            nl = "\r\n" if mutate == "crlf" else "\n"
            reset_state()
            mig, n = start(d)
            Mkt.flush()
            Cat.tick()
            snap1 = files(d)
            s14 = LAST14[0] or ""
            n_moved = len(P14) - (2 if mutate == "hand" else 0)        # Iron already 16, Mithril kept; Thorium / Maple moved
            check(mig is None and ("MIGRATE-0.1.4 rewrote %d kept %d already %d" % (n_moved, 1 if mutate == "hand" else 0,
                                                                                   1 if mutate == "hand" else 0)) in s14 and n == N_PROD,
                  "%s: the 0.1.4 update ran: %s (%d products)" % (name, s14, n))
            after = open(pfile, "rb").read().decode("utf8")
            want = expect_lines(before.decode("utf8"), nl)
            got = after.split(nl)
            if mutate == "nonl":
                # 0.1.3's line-keeping save (a moved auto price) ends the file with a line ending; the update alone keeps it open (below)
                want = want + [""]
            bad = [(i, w, g) for i, (w, g) in enumerate(zip(want, got)) if w != g]
            check(len(want) == len(got) and not bad, "%s: every line = the expected one (moved price text / moved auto price / byte-identical): %s"
                  % (name, bad[:3]))
            eol_ok = (after.count("\n") == after.count("\r\n") and "\r\n" in after) if mutate == "crlf" else ("\r" not in after)
            check(eol_ok and (after.endswith(nl) == before.decode("utf8").endswith(nl) or mutate == "nonl"), "%s: line endings kept" % name)
            if mutate == "nonl":
                # the update alone (no load / save): the last line keeps having no line ending
                d2 = d + "_only"
                shutil.copytree(live0, d2)
                open(os.path.join(d2, "products.properties"), "wb").write(before)
                reset_state()
                Cat.FILE = Paths.get(os.path.join(d2, "products.properties"))
                Cat.PFILE = Paths.get(os.path.join(d2, "pricing.properties"))
                check(Cat.migrate() is None and Cat.migrate14() is not None, "nonl: update alone ran")
                only = open(os.path.join(d2, "products.properties"), "rb").read().decode("utf8")
                Cat.M14_LOG.clear()
                exp_only = []
                for ln in before.decode("utf8").split("\n"):
                    p_ = Cat.peek(ln)
                    if p_ is not None and str(p_.id) in P14 and abs(float(p_.base) - P14[str(p_.id)][0]) < 1e-9:
                        ln = with_price(ln, "%g" % P14[str(p_.id)][1])
                    exp_only.append(ln)
                check(not only.endswith("\n") and only == "\n".join(exp_only),
                      "nonl: the update alone keeps the missing final line ending and changes only the moved prices")
                reset_state()
                start(d)                    # back to the variant's own folder (already updated: nothing runs)
            hist = os.path.join(d, "config-history")
            hfiles = sorted(os.listdir(hist)) if os.path.isdir(hist) else []
            check(len(hfiles) == 1 and re.match(r"^Skyy_SkyyBazaar~products\.properties\.\d{8}-\d{6}-\d{3}\.bak$", hfiles[0])
                  and open(os.path.join(hist, hfiles[0]), "rb").read() == before, "%s: history copy = the old bytes (%s)" % (name, hfiles))
            pp_after = open(ppath, "rb").read()
            check(pp_after.startswith(pp_before) and pp_after.count(b"migrated.0.1.4=") == 1 and pp_after.endswith(nl.encode())
                  and (pp_after.count(b"\n") == pp_after.count(b"\r\n") if mutate == "crlf" else b"\r" not in pp_after),
                  "%s: pricing.properties = its old bytes + the 0.1.4 marker, line endings kept" % name)
            check(dict((k, v) for k, v in props(ppath).items() if k.startswith("mode.")) ==
                  dict((k, v) for k, v in props(os.path.join(live0, "pricing.properties")).items() if k.startswith("mode.")),
                  "%s: processed goods keep their auto / fixed modes" % name)
            tl = open(os.path.join(d, "trades.log"), encoding="utf8").read()
            check(tl.count("MIGRATE-0.1.4 PRICE ") == n_moved and "MIGRATE-0.1.4 PRICE Ore_Onyxium 58 -> 3712 (undo: /bazaaradmin price Ore_Onyxium 58)" in tl
                  and ("MIGRATE-0.1.4 KEPT Ore_Mithril 100.0 (your price; the 0.1.3 default was 45, the 0.1.4 default is 1440)" in tl) == (mutate == "hand"),
                  "%s: trades.log: %d PRICE lines with their undo command%s" % (name, n_moved, " + the KEPT line" if mutate == "hand" else ""))
            for pid, (o_, n_) in P14.items():
                if mutate == "hand" and pid == "Ore_Mithril":
                    check(abs(base_of(pid) - 100.0) < 1e-9, "handset: Skyy's Mithril Ore 100 kept")
                else:
                    check(Cat.get(pid) is not None and abs(base_of(pid) - n_) < 1e-9, "%s: %s now %s (%s)" % (name, pid, n_, Cat.get(pid) and base_of(pid)))
            check(abs(base_of("Ingredient_Bar_Iron") - 19.2) < 1e-9 and abs(base_of("Ingredient_Leather_Light") - 14.4) < 1e-9
                  and abs(base_of("Ingredient_Bar_Onyxium") - 4454.4) < 1e-9, "%s: auto ingots / leathers follow (Iron 19.2, Light Leather 14.4, Onyxium 4454.4)" % name)
            if mutate == "hand":
                check("Ore_Thorium=Mining, 48 ,Thorium Ore" in after and "Wood_Maple_Trunk=Wood,8,Maple Log" in after
                      and after.endswith("Plant_Crop_Potato_Item=Farming,2,Potato\n") and "Ore_Iron=Mining,16,Iron Ore" in after,
                      "handset: ' 12.0 ' -> ' 48 ' (spacing kept), Maple keeps its own tab at 8, the duplicate Potato line untouched")
                check([str(t_) for t_ in Cat.tabsOf(Cat.get("Wood_Maple_Trunk"))] == ["Foraging", "Wood"], "handset: Maple in Foraging + Wood")
            mk1 = props(os.path.join(d, "market.properties"))
            for k, v in mk0.items():
                if k.startswith("f."):
                    check(k in mk1 and abs(float(mk1[k]) - float(v)) < 0.01, "%s: factor %s kept (%s -> %s)" % (name, k, v, mk1.get(k)))
                elif k.startswith(("bought.", "sold.")) or k in ("spread", "impactCoins", "halfLifeMinutes"):
                    check(mk1.get(k) == v, "%s: %s kept" % (name, k))
            # second start: nothing written
            reset_state()
            mig2, n2 = start(d)
            Mkt.flush()
            Cat.tick()
            snap2 = files(d)
            changed_files = [k for k in snap2 if snap1.get(k) != snap2[k] and k not in ("market.properties", "trades.log")]
            check(mig2 is None and LAST14[0] is None and n2 == N_PROD and not changed_files and set(snap1) == set(snap2),
                  "%s: second start writes nothing (%s, new %s)" % (name, changed_files, sorted(set(snap2) - set(snap1))))
            if name == "live":
                # rollback: the updated file loads in the 0.1.3 Catalog with the new prices
                OCat = JClass(Cls.forName("com.skyy.bazaar.Catalog", True, old_loader))
                OCat.FILE = Paths.get(pfile)
                on = int(OCat.load())
                check(on == N_PROD and abs(float(OCat.get("Ore_Iron").base) - 16.0) < 1e-9, "rollback: 0.1.3 reads %d products, Iron Ore 16" % on)
                # a missing 0.1.4 marker re-runs the update: nothing to move, the file unchanged, the marker back once
                keep_pp = open(ppath, "rb").read()
                open(ppath, "wb").write(b"".join(l for l in keep_pp.splitlines(True) if not l.startswith(b"migrated.0.1.4")))
                prev = open(pfile, "rb").read()
                reset_state()
                start(d)
                check(LAST14[0] is not None and "rewrote 0 kept 0 already %d" % len(P14) in LAST14[0] and open(pfile, "rb").read() == prev
                      and open(ppath, "rb").read().count(b"migrated.0.1.4=") == 1, "marker removed: re-run moves nothing (%s)" % LAST14[0])
        # failure paths on fresh copies: nothing changes, no marker, the next start retries
        for tag in ("ppdir", "histfile", "notutf8", "nomark13"):
            d = os.path.join(SCRATCH, "f_" + tag)
            shutil.copytree(live0, d)
            pfile, ppath = os.path.join(d, "products.properties"), os.path.join(d, "pricing.properties")
            if tag == "ppdir":
                os.remove(ppath)
                os.makedirs(ppath)
            elif tag == "histfile":
                open(os.path.join(d, "config-history"), "wb").write(b"not a folder")
            elif tag == "notutf8":
                open(pfile, "wb").write(b"# caf\xe9 (Latin-1)\n" + old_txt.encode("utf8"))
            elif tag == "nomark13":
                open(ppath, "wb").write(b"".join(l for l in old_pp.splitlines(True) if not l.startswith(b"migrated.0.1.3")))
            b0 = open(pfile, "rb").read()
            reset_state()
            mig_, n_ = start(d)
            pp_now = open(ppath, "rb").read() if os.path.isfile(ppath) else b""
            if tag == "nomark13":
                # 0.1.3's update runs first again (idempotent on 0.1.3 lines), then 0.1.4's
                check(LAST14[0] is not None and pp_now.count(b"migrated.0.1.4=") == 1 and abs(base_of("Ore_Iron") - 16.0) < 1e-9
                      and all(Cat.isAuto(p_) for p_ in procs) and abs(base_of("Ingredient_Bar_Iron") - 19.2) < 1e-9,
                      "no 0.1.3 marker: 0.1.3's update re-runs, then 0.1.4's (%s / %s)" % (mig_, LAST14[0]))
                continue
            check(LAST14[0] is None and b"migrated.0.1.4" not in pp_now and open(pfile, "rb").read() == b0,
                  "%s: the update fails safely - products.properties unchanged, no marker" % tag)
            if tag == "histfile":
                os.remove(os.path.join(d, "config-history"))
                reset_state()
                start(d)
                check(LAST14[0] is not None and ("rewrote %d" % len(P14)) in LAST14[0], "histfile: the next start retries and succeeds (%s)" % LAST14[0])
        # the 0.1.2 chain: a server that never ran 0.1.3 (the live 0.1.2 backup, no pricing.properties) gets 0.1.3's update, then 0.1.4's
        v012 = os.path.join(live0, "products.properties.v012bak")
        if os.path.exists(v012):
            d = os.path.join(SCRATCH, "s_from012")
            os.makedirs(d)
            shutil.copy(v012, os.path.join(d, "products.properties"))
            shutil.copy(os.path.join(live0, "market.properties"), os.path.join(d, "market.properties"))
            reset_state()
            mig_, n_ = start(d)
            ppf = props(os.path.join(d, "pricing.properties"))
            txt = open(os.path.join(d, "products.properties"), encoding="utf8").read()
            check(mig_ is not None and LAST14[0] is not None and ppf.get("migrated.0.1.3") and ppf.get("migrated.0.1.4") and n_ == N_PROD
                  and "Ore_Iron=Mining,16,Iron Ore" in txt and "Plant_Crop_Potato_Item=Farming,40,Potato" in txt
                  and abs(base_of("Ingredient_Hide_Light") - 12.0) < 1e-9,
                  "0.1.2 data: 0.1.3's update (%s) then 0.1.4's (%s) - 0.1.2 default lines end at the 0.1.4 prices" % (mig_, LAST14[0]))
        print("S. saved state (0.1.4 update) on scratch copies of the live 0.1.3 data (live, hand-set prices, CRLF, no final newline): "
              "%d default prices moved (price text only), hand-set kept + logged, history copy = old bytes, marker appended, market kept, "
              "second start writes nothing; rollback read; re-run; 3 failure paths change nothing; the 0.1.2 chain" % len(P14))
    else:
        print("S. no live 0.1.3 data folder copied - skipped")

    # ---------------- Z. FIX ROUND (review 2026-10-03): one block per finding
    reset_state()
    dZ = os.path.join(SCRATCH, "fix")
    os.makedirs(dZ)
    start(dZ)
    Cfg.PREMIUM = 20
    Cat.reprice()
    prz = pref("Admin")
    # (1) the loop check sees co-products and liquidation: its self-test, the review's Ancient Steel chain at Bronze 16
    try:
        st = NS["loop_check_selftest"]()
        check("craft Gear" in st and "salvage Gear" in st, "Z1: the build's loop check self-test passes: %s" % st)
    except AssertionError as e:
        FAILS.append("Z1 self-test: %s" % e)
    px = runtime_prices()
    check(abs(px["Ingredient_Bar_Bronze"] - 40.0) < 1e-9, "Z1: Bronze Ingot is 40 (%s)" % px["Ingredient_Bar_Bronze"])
    px16 = dict(px)
    px16["Ingredient_Bar_Bronze"] = 21.0                 # 0.1.4: the 0.1.3 price pays at the new Iron Ore / hide prices
    old_blind = True
    try:
        NS["check_assets"](px16, NS["SPREAD"])
    except SystemExit:
        old_blind = False
    loops16 = NS["loop_check"](M, px16, NS["SPREAD"])[0]
    names16 = sorted(set(str(l[1]).split("/")[-1] for l in loops16))
    check(any("Armor_Steel_Ancient_Hands" in n for n in names16),
          "Z1: at Bronze 21 (0.1.3's price) the liquidation check flags the Ancient Steel chain (0.1.2 check blind: %s): %s"
          % (old_blind, [n for n in names16 if "Steel_Ancient" in n][:4]))
    check(not NS["loop_check"](M, px, NS["SPREAD"])[0], "Z1: at the jar's Bronze 40 (premium 20) no loop")
    # (2) the review's missing materials are listed in their bag's tab; skip samples carry their reason
    want = {"Mining": ["Rock_Gem_Emerald", "Rock_Gem_Topaz", "Rock_Gem_Voidstone", "Rock_Gem_Zephyr", "Ore_Onyxium", "Ore_Prisma",
                       "Rock_Ice_Permafrost", "Soil_Ash", "Soil_Mud", "Soil_Gravel", "Rock_Basalt", "Rock_Dawnstone"],
            "Foraging": ["Wood_Sticks"] + ["Wood_%s_Planks" % w for w in ("Blackwood", "Darkwood", "Deadwood", "Drywood", "Goldenwood",
                                                                           "Greenwood", "Hardwood", "Lightwood", "Redwood", "Softwood",
                                                                           "Tropicalwood")],
            "Farming": ["Plant_Hay_Bundle", "Plant_Sapling_Oak", "Plant_Seeds_Health1", "Plant_Seeds_Mana2", "Plant_Seeds_Stamina3",
                        "Plant_Seeds_Wild", "Ingredient_Life_Essence_Concentrated", "Food_Fish_Raw_Uncommon"]
                       + ["Plant_Seeds_%s_Eternal" % c for c in ("Carrot", "Lettuce", "Potato", "Wheat", "Corn", "Cotton", "Onion", "Rice",
                                                                  "Tomato", "Turnip", "Aubergine", "Cauliflower", "Chilli", "Pumpkin")]}
    for tab, lst in want.items():
        for i in lst:
            p = Cat.get(i)
            check(p is not None and tab in [str(t) for t in Cat.tabsOf(p)], "Z2: %s listed in %s" % (i, tab))
    for i, word in (("Rock_Stone_Brick_Stairs", "building shape"), ("Wood_Oak_Trunk_Half", "building shape"),
                    ("Plant_Cactus_1", "decoration plant"), ("Plant_Flower_Common_Red", "decoration plant"),
                    ("Ore_Iron_Stone", "world form"), ("Plant_Crop_Wheat_Block", "world form"),
                    ("Plant_Seeds_Oak", "never obtainable"), ("Rubble_Stone_Medium", "never obtainable"), ("Rock_Stone", "never obtainable")):
        check(i in skip_ids and word in skip_ids[i], "Z2: %s skipped as '%s' (%s)" % (i, word, skip_ids.get(i)))
    # (3) Onyxium / Prisma Ingot follow their ores
    for bar, ore, wb in (("Ingredient_Bar_Onyxium", "Ore_Onyxium", 4454.4), ("Ingredient_Bar_Prisma", "Ore_Prisma", 90.0)):
        check(Cat.isAuto(bar) and abs(base_of(bar) - wb) < 1e-9 and abs(base_of(bar) - math.floor(base_of(ore) * 1.2 * 100 + 1e-9) / 100) < 1e-9,
              "Z3: %s AUTO = %s x 1.2 = %s" % (bar, ore, base_of(bar)))
    Adm.run(prz, "price", "Ore_Onyxium", "4000")
    check(abs(base_of("Ingredient_Bar_Onyxium") - 4800.0) < 1e-9, "Z3: Onyxium Ore 4000 -> its ingot 4800 (%s)" % base_of("Ingredient_Bar_Onyxium"))
    Adm.run(prz, "price", "Ore_Onyxium", "3712")
    check(abs(base_of("Ingredient_Bar_Onyxium") - 4454.4) < 1e-9, "Z3: Onyxium Ore back to 3712 -> 4454.4")
    # (4) the cloth bolts are processed goods (AUTO) and follow their input; Dawnstone is not premium-stacked
    bolts7 = ["Ingredient_Bolt_%s" % b for b in ("Linen", "Cotton", "Silk", "Shadoweave", "Cindercloth", "Stormsilk", "Prismaloom")]
    check(all(Cat.isAuto(b) and abs(base_of(b) - 19.2) < 1e-9 for b in bolts7),
          "Z4: the 7 Loombench bolts AUTO at 19.2 = Cotton 16 x 1.2: %s" % [base_of(b) for b in bolts7])
    check(Cat.isAuto("Ingredient_Bolt_Wool") and abs(base_of("Ingredient_Bolt_Wool") - 1.2) < 1e-9,
          "Z4: Bolt of Wool AUTO 1.2 = Wool Scraps 4 / 4 x 1.2 (%s)" % base_of("Ingredient_Bolt_Wool"))
    Adm.run(prz, "price", "Plant_Crop_Cotton_Item", "17")
    check(all(abs(base_of(b) - 20.4) < 1e-9 for b in bolts7), "Z4: Cotton 17 -> every Loombench bolt 20.4: %s" % [base_of(b) for b in bolts7])
    Adm.run(prz, "price", "Plant_Crop_Cotton_Item", "16")
    check(all(abs(base_of(b) - 19.2) < 1e-9 for b in bolts7), "Z4: Cotton back to 16 -> 19.2")
    pl_c = str(Cat.procLine(Cat.get("Ingredient_Bolt_Cotton")))
    pl_w = str(Cat.procLine(Cat.get("Ingredient_Bolt_Wool")))
    check("20% more" in pl_c and "the Cotton" in pl_c and "weaving it yourself" in pl_c, "Z4: bolt line: %s" % pl_c)
    check("Wool Scraps (1 makes 4)" in pl_w and "weaving it yourself" in pl_w, "Z4: wool bolt line: %s" % pl_w)
    check(abs(base_of("Rock_Dawnstone") - 4.8) < 1e-9 and abs(base_of("Rock_Quartzite") - 2.4) < 1e-9,
          "Z4: Dawnstone 4.8 = 4 Quartzite Cobble x 1.2, not 2 Quartzite x 1.2 = 5.76 (%s)" % base_of("Rock_Dawnstone"))
    pl_d = str(Cat.procLine(Cat.get("Rock_Dawnstone")))
    check("its raw inputs" in pl_d and "smelting it yourself" in pl_d, "Z4: Dawnstone line names its raw inputs: %s" % pl_d)
    # (4b) the admin price guard: a price that makes a recipe among products pay in one step is refused and changes nothing
    edges = NS["edge_table"](M, set(PIDS), charcoal)
    check(len(edges) == int(Cat.EDGE.size()) and len(edges) > 200, "Z4: the jar carries the build's %d recipe edges (%d)" % (len(edges), int(Cat.EDGE.size())))

    def java_loops():
        return sorted(int(x) for x in Cat.loopingEdges(Mkt.SPREAD))
    check(java_loops() == [] and NS["edge_loops"](edges, runtime_prices(), NS["SPREAD"], fuels, charcoal) == [],
          "Z4: no recipe edge pays at the default prices (Java + build)")
    for item, v in (("Ingredient_Life_Essence", "1"), ("Plant_Crop_Cotton_Item", "1"), ("Wood_Bamboo_Trunk", "1"), ("Ingredient_Stick", "0.2"),
                    ("Rubble_Stone", "0.1"), ("Ingredient_Life_Essence_Concentrated", "70"), ("Plant_Sapling_Oak", "20")):
        b0, bolt0 = base_of(item), base_of("Ingredient_Bolt_Cotton")
        TPR.SAID.clear()
        Adm.run(prz, "price", item, v)
        said = str(TPR.SAID[-1]) if TPR.SAID.size() else ""
        check(base_of(item) == b0 and base_of("Ingredient_Bolt_Cotton") == bolt0 and "refused" in said and " -> " in said and not java_loops(),
              "Z4: price %s %s refused, nothing changed (%s)" % (item, v, said[:170]))
        print("   guard: /bazaaradmin price %s %s -> %s" % (item, v, said[:200]))
    # Java = build on a table with a loop made by a hand edit (setBase skips the guard), the warning, and an old loop does not block
    Cat.setBase("Ingredient_Life_Essence", 1.0)
    Cat.reprice()
    jl = java_loops()
    pyl = sorted(NS["edge_loops"](edges, runtime_prices(), NS["SPREAD"], fuels, charcoal))
    check(jl and jl == pyl, "Z4: Java loopingEdges = the build's edge_loops on a hand-edited table: %s / %s" % (jl[:6], pyl[:6]))
    n_w = int(Cat.warnLoops(Mkt.SPREAD))
    check(n_w == len(jl) and any(str(w).startswith("edge:") for w in Cat.WARNED), "Z4: reload / start warn about each paying recipe (%d)" % n_w)
    TPR.SAID.clear()
    Adm.run(prz, "price", "Ore_Copper", "6")
    check(abs(base_of("Ore_Copper") - 6.0) < 1e-9 and "refused" not in str(TPR.SAID[-1]), "Z4: an unrelated price passes next to an old loop")
    Adm.run(prz, "price", "Ore_Copper", "5")
    Cat.setBase("Ingredient_Life_Essence", 0.5)
    Cat.reprice()
    check(java_loops() == [], "Z4: the hand edit undone - no recipe edge pays")
    TPR.SAID.clear()
    Adm.run(prz, "price", "Ingredient_Life_Essence_Concentrated", "55")
    check(abs(base_of("Ingredient_Life_Essence_Concentrated") - 55.0) < 1e-9 and "refused" not in str(TPR.SAID[-1]),
          "Z4: a safe price for a crafted good passes (Greater Essence of Life 55)")
    Adm.run(prz, "price", "Ingredient_Life_Essence_Concentrated", "50")
    # (5a) a FIXED processed good above its no-loop limit is held at it (setBase = a hand edit + reload, no cap check)
    Cat.setBase("Ingredient_Bar_Gold", 40.0)
    Cat.reprice()
    cap = float(Cat.loopCap("Ingredient_Bar_Gold"))
    check(not Cat.isAuto("Ingredient_Bar_Gold") and abs(cap - 24.44) < 1e-9 and abs(base_of("Ingredient_Bar_Gold") - cap) < 1e-9,
          "Z5a: Gold Ingot fixed at 40 is held at its limit %s (%s)" % (cap, base_of("Ingredient_Bar_Gold")))
    Adm.run(prz, "price", "Ingredient_Bar_Gold", "23")
    check(abs(base_of("Ingredient_Bar_Gold") - 23.0) < 1e-9, "Z5a: a fixed price under the limit stays (23)")
    Adm.run(prz, "price", "Ore_Gold", "10")
    check(abs(base_of("Ingredient_Bar_Gold") - 12.22) < 1e-9,
          "Z5a: Gold Ore made cheaper (10) -> the fixed ingot held at the new limit 12.22 (%s)" % base_of("Ingredient_Bar_Gold"))
    Adm.run(prz, "price", "Ore_Gold", "20")
    Adm.run(prz, "price", "Ingredient_Bar_Gold", "auto")
    check(Cat.isAuto("Ingredient_Bar_Gold") and abs(base_of("Ingredient_Bar_Gold") - 24.0) < 1e-9, "Z5a: auto again -> 24")
    # (5b) a line load() refuses does not hide the product: its seed line is appended, the refused line kept (0.1.3's update runs on
    #      0.1.2 data: the live 0.1.2 backup without pricing.properties; 0.1.4: the appended seed line carries the 0.1.4 price)
    v012z = os.path.join(SCRATCH, "live", "products.properties.v012bak")
    if os.path.exists(v012z):
        live_txt = open(v012z, "rb").read().decode("utf8")
        live_ids_z = set(m.group(1) for m in re.finditer(r"(?m)^([A-Za-z0-9_]+)=", live_txt))
        add_z = len([s_ for s_ in SEED if s_.split("=", 1)[0] not in live_ids_z]) + 1
        good = "Plant_Crop_Pumpkin_Item=Farming,5,Pumpkin"
        seed_p = [s_ for s_ in SEED if s_.startswith("Plant_Crop_Pumpkin_Item=")][0]
        for tag, bad in (("cat17", "Plant_Crop_Pumpkin_Item=AVeryLongCategoryX,5,Pumpkin"), ("price0", "Plant_Crop_Pumpkin_Item=Farming,0,Pumpkin"),
                         ("price2e9", "Plant_Crop_Pumpkin_Item=Farming,2000000000,Pumpkin")):
            d = os.path.join(SCRATCH, "z5b_" + tag)
            os.makedirs(d)
            pf_ = os.path.join(d, "products.properties")
            check(good in live_txt, "Z5b: the 0.1.2 file has the Pumpkin line")
            open(pf_, "wb").write(live_txt.replace(good, bad).encode("utf8"))
            reset_state()
            mig_, n_ = start(d)
            after_ = open(pf_, "rb").read().decode("utf8")
            pump = Cat.get("Plant_Crop_Pumpkin_Item")
            check(pump is not None and abs(float(pump.base) - 6.0) < 1e-9 and n_ == N_PROD and (bad + "\n") in after_
                  and after_.count(seed_p) == 1 and ("added %d " % add_z) in str(mig_),
                  "Z5b %s: the refused line is kept, the 0.1.4 seed line appended, Pumpkin loads at 6 (%s)" % (tag, mig_))
    # (5c) a save keeps the file: a premium change rewrites only the moved processed lines; CRLF, a comment, "5.0" stay
    d = os.path.join(SCRATCH, "z5c")
    os.makedirs(d)
    pf_ = os.path.join(d, "products.properties")
    lines_ = ["# my own note", ""] + [l.replace("Ore_Copper=Mining,5,", "Ore_Copper=Mining,5.0,") for l in SEED]
    open(pf_, "wb").write(("\r\n".join(lines_) + "\r\n").encode("utf8"))
    reset_state()
    mig_c, _n = start(d)
    before_ = open(pf_, "rb").read()
    check(mig_c is not None and "added 0 rewrote 0" in str(mig_c) and before_ == ("\r\n".join(lines_) + "\r\n").encode("utf8"),
          "Z5c: the one-time update on a current file changes nothing (%s)" % mig_c)
    Cfg.PREMIUM = 15
    Cat.tick()
    after_ = open(pf_, "rb").read()
    bl_, al_ = before_.decode("utf8").split("\r\n"), after_.decode("utf8").split("\r\n")
    moved_ids = set(bl_[i].split("=", 1)[0] for i in range(min(len(bl_), len(al_))) if bl_[i] != al_[i])
    check(len(bl_) == len(al_) and after_.count(b"\n") == after_.count(b"\r\n") and al_[0] == "# my own note" and al_[1] == ""
          and "Ore_Copper=Mining,5.0,Copper Ore" in al_ and moved_ids and moved_ids <= set(procs),
          "Z5c: premium 15 rewrote only %d processed lines; CRLF, the comment and 'Ore_Copper 5.0' stay" % len(moved_ids))
    check(any(l.startswith("Ingredient_Bar_Copper=Smithing,5.75,") for l in al_), "Z5c: Copper Ingot line now 5.75")
    Cfg.PREMIUM = 20
    print("Z. fix round: loop check sees the Ancient Steel chain at Bronze 21 (the 0.1.3 price), %d missing materials listed + skip reasons, Onyxium / Prisma "
          "ingots + cloth bolts follow their inputs, Dawnstone not stacked, fixed price held at the limit, refused lines do not hide "
          "a product, line-keeping save" % sum(len(v) for v in want.values()))

    # ---------------- W. the page on real data
    reset_state()
    dW = os.path.join(SCRATCH, "page")
    os.makedirs(dW)
    start(dW)
    coins_on()
    Purse.P[str(U1)] = 123456
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    IW, INNER_H = 1080 - 34, 907 - 38 - 34

    def render(page, pl_):
        b, ev = UCB(), UEB()
        page.render(b, ev, U1, pl_)
        ap = SUI.Appends()
        sets = []
        for c in b.getCommands():
            t = str(c.type)
            if t == "AppendInline":
                ap.append((None if c.selector is None else str(c.selector).lstrip("#"), str(c.text)))
            elif t == "Set":
                sets.append((str(c.selector), str(c.data)))
        binds = [(str(e.type), str(e.selector), str(e.data)) for e in ev.getEvents()]
        return ap, sets, binds

    def page_checks(label, ap, sets, binds, ncells, selected):
        for p, mk in ap:
            try:
                SUI.check_markup(mk, root=(p is None))
                OKS[0] += 1
            except Exception as e:
                FAILS.append("%s: markup %s: %s" % (label, mk[:80], e))
        try:
            SUI.assert_proven(ap)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("%s: assert_proven: %s" % (label, e))
        check(SUI.used_height(ap, "SkyyBz") == INNER_H, "%s: body %s = %d" % (label, SUI.used_height(ap, "SkyyBz"), INNER_H))
        rows = ["SkyyBzHead", "SkyyBzTabs", "SkyyBzFoot"] + ["SkyyBzRow%d" % r for r in range(4)] + (["SkyyBzActs", "SkyyBzAmtRow"] if selected else [])
        for r in rows:
            check(SUI.used_width(ap, r) <= IW, "%s: row %s %s <= %d" % (label, r, SUI.used_width(ap, r), IW))
        ids = set()
        for _p, mk in ap:
            ids.update(m.group(1) for m in re.finditer(r"#([A-Za-z0-9]+)", mk))
        for sel, _d in sets:
            check(sel.split(".")[0].lstrip("#") in ids, "%s: b.set target %s exists" % (label, sel))
        cells = [x for x in binds if x[1].startswith("#SkyyBzCell")]
        check(len(cells) == ncells, "%s: %d cell bindings (%d)" % (label, ncells, len(cells)))
        for want in ("#SkyyBzPgPrev", "#SkyyBzPgNext", "#SkyyBzClose", "#SkyyBzSellInv", "#SkyyBzTab0"):
            check(any(x[1] == want for x in binds), "%s: binding %s" % (label, want))
        return ids

    pl = player()
    for t, n_ in (("Mining", 52), ("Foraging", 49), ("Farming", 52), ("Combat", 20), ("Smithing", 46)):
        pg = Page(pref(), None)
        pg.cat = t
        ap, sets, binds = render(pg, pl)
        page_checks("tab " + t, ap, sets, binds, n_, False)
    pg = Page(pref(), "Plant_Crop_Wheat_Item")
    pg.cat = "Farming"
    pg.pageNo = 3
    ap, sets, binds = render(pg, pl)
    page_checks("Farming page 4", ap, sets, binds, TAB_SIZES["Farming"] - 3 * 52, True)
    check(any("Page 4 of 4" in d for s_, d in sets if s_ == "#SkyyBzPgPage.Text"), "Farming page 4 caption")
    for pid, t in (("Ingredient_Bar_Copper", "Smithing"), ("Ingredient_Leather_Light", "Combat")):
        pg = Page(pref(), pid)
        pg.cat = t
        ap, sets, binds = render(pg, pl)
        page_checks("selected " + pid, ap, sets, binds, 46 if t == "Smithing" else 20, True)
        proc = [d for s_, d in sets if s_ == "#SkyyBzDProc.Text"]
        check(proc and ("20% more" in proc[0] if pid.startswith("Ingredient_Bar") else "listed in the Combat and Smithing" in proc[0]),
              "%s line %s" % (pid, proc))
    # 7 tabs: two admin categories on top of the five bags
    adm_prod = JClass(PKG + "Product")("Skyy_Test_Admin_Item", "Extra", 1.0, "Test")
    Cat.LIST.add(adm_prod)
    Cat.BY_ID.put("Skyy_Test_Admin_Item", adm_prod)
    Cat.get("Ore_Copper").cat = "Rocks"
    Cat.CACHE.clear(); Cat.CATS = None
    pg = Page(pref(), None)
    ap, sets, binds = render(pg, pl)
    page_checks("7 tabs", ap, sets, binds, 52, False)
    check(len([x for x in binds if x[1].startswith("#SkyyBzTab")]) == 6 and any("1 more tabs" in d for s_, d in sets if s_ == "#SkyyBzSub.Text"),
          "7 tabs: 6 drawn + the note")
    Cat.get("Ore_Copper").cat = "Mining"
    _keep = [x for x in Cat.LIST if str(x.id) != "Skyy_Test_Admin_Item"]
    Cat.LIST.clear()
    for x in _keep:
        Cat.LIST.add(x)
    Cat.BY_ID.remove("Skyy_Test_Admin_Item")
    Cat.CACHE.clear(); Cat.CATS = None
    coins_off()
    pg = Page(pref(), "Ore_Iron")
    ap, sets, binds = render(pg, pl)
    page_checks("no coins", ap, sets, binds, 52, True)
    check(any("not loaded" in d for s_, d in sets if s_ == "#SkyyBzPurse.Text"), "no coins: purse line says so")
    coins_on()
    pg = Page(pref(), None)
    pg.confirmUntil = 2 ** 62
    ap, sets, binds = render(pg, pl)
    page_checks("sell inventory armed", ap, sets, binds, 52, False)
    check(any("Confirm sell" in mk for _p, mk in ap), "armed: Confirm sell label")
    # clicks (rebuild / close return at once without a live player entity)
    pg = Page(pref(), None)
    render(pg, pl)
    pg.handleDataEvent(None, None, '{"a":"tab:2"}')
    check(str(pg.cat) == "Farming" and int(pg.pageNo) == 0, "click tab:2 -> Farming page 1")
    for _k in range(4):
        pg.handleDataEvent(None, None, '{"a":"next"}')
    render(pg, pl)
    check(int(pg.pageNo) == 3, "next x4 clamps at the last page (%d)" % int(pg.pageNo))
    pg.handleDataEvent(None, None, '{"a":"prev"}')
    check(int(pg.pageNo) == 2, "prev -> page 3")
    render(pg, pl)
    first = str(pg.cells[0])
    pg.handleDataEvent(None, None, '{"a":"cell:0"}')
    check(str(pg.sel) == first, "cell:0 selects %s" % first)
    p0 = Purse.get(U1)
    pg.handleDataEvent(None, None, '{"a":"close"}')
    check(str(pg.sel) == first and Purse.get(U1) == p0, "close moves nothing")
    pg.handleDataEvent(None, None, '{"a":"prev"}')
    pg.handleDataEvent(None, None, '{"a":"prev"}')
    pg.handleDataEvent(None, None, '{"a":"prev"}')
    check(int(pg.pageNo) == 0, "prev stops at page 1")
    # one-line text fit of the detail lines for every product (the 884 px text column)
    widest = (0, "")
    for pid in PIDS:
        p = Cat.get(pid)
        for txt, size in ((str(Cat.procLine(p)), 15), (str(p.name), 18)):
            w = SUI.text_width(txt, size)
            if w > widest[0]:
                widest = (w, txt)
    check(widest[0] <= 884, "the longest detail line fits 884 px: %d px (%s)" % (widest[0], widest[1]))
    print("W. page: 11 states on real data - markup checked, proven properties only, body %d px, rows <= %d px, set targets, bindings; "
          "clicks tab / next / prev / cell / close; widest detail line %d px" % (INNER_H, IW, widest[0]))


# ============================================================================================================== parent
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
    open(os.path.join(SCRATCH, MARK), "w").write("SkyyBazaar 0.1.4 harness scratch\n")
    if os.path.isdir(LIVE):
        shutil.copytree(LIVE, os.path.join(SCRATCH, "live"))
        print("copied the live data folder (read only):", LIVE)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.makedirs(env["TEMP"], exist_ok=True)
    rc = subprocess.run([sys.executable, os.path.abspath(__file__), "--child"] + sys.argv[1:], env=env).returncode
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.exit(rc)


if __name__ == "__main__":
    main()
