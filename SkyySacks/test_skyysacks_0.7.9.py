"""Bare-JVM check for SkyySacks 0.7.9 (the /craft Campfire tab shows SkyyCooking 0.1.3's live XP share; everything else is 0.7.8), kept next
to the build so the build report's claims can be re-run. The 0.7.8 harness carried forward: sections A-H unchanged (the cooked-food rule
must still hold in 0.7.9), section I now compares 0.7.8 vs 0.7.9, new section J = the Campfire tab text.

    python SkyySacks/test_skyysacks_0.7.9.py [--jar <0.7.9 jar>] [--old <0.7.8 jar>] [--oracle <0.7.7 jar>] [--cook <SkyyCooking 0.1.3 jar>]
        [--live <Skyy_SkyySacks folder>] [--livecook <cooking.properties>] [--dir <scratch>] [--keep]

Build first (python SkyySacks/build_skyysacks_0.7.9.py and python SkyyCooking/build_skyycooking_0.1.3.py). The parent copies the live
data folder and the live cooking.properties (read only; default: the "HUD mod" world's mods/Skyy_SkyySacks and
mods/Skyy_SkyyCooking/cooking.properties) into the scratch folder and starts a child: a fresh JVM (the game's JRE, -Xverify:all,
-XX:-UsePerfData, HytaleServer.jar + the 0.7.9 jar + the SkyyCooking 0.1.3 jar + tools/javassist.jar, java.io.tmpdir / TEMP / TMP in the
scratch folder). The 0.7.7 SackDefs is loaded from the 0.7.7 jar in its own class loader as the oracle ("switch on = exactly 0.7.7").
Checks:
  A  every 0.7.9 class (and every SkyyCooking 0.1.3 class, used by J) loads and verifies (-Xverify:all)
  B  the Server Setup row bags.cookedFood (bool, default false, live, label / help limits), KEEP 10, the config template line, SackCfg.reload
     reads true / false / on / off / junk from the file, the kit's own set path (config:fn:SkyySacks set + flush on a copy of the live
     config.properties) writes the line and moves SackDefs.COOKED_FARM, the after= hook runs
  C  classification of EVERY item id in Assets.zip + every SkyyCooking item (installed jar, read only) + the Food_ ids of the installed
     (disabled) pack mods + edge ids, switch off and on, with and without the cook:prefix bridge value: homeOf == 0.7.7 catOf always;
     catOf == 0.7.7 catOf with the switch on; with it off catOf == 0.7.7 catOf except cooked food -> none; cooked() == the table / rule
  D  intake paths refuse cooked food (switch off): the 2 s auto-pickup sweep and Deposit all (all containers), with a Farming bag and with
     the Mythic Omni Bag; raw produce still goes in; the switch on = 0.7.7 (cooked food pools); every item counted before and after;
     SweepTask.cookedHeld counts the cooked food on hand (the Deposit all hint "cooked food stays in your inventory")
  E  stored cooked food stays retrievable (switch off): withdraw (clicks) and the Pick up all loop take it out with exact counts, never
     without a bag; catTotal / cookedTotal count it; a sweep after taking it out does not put it back
  F  the bag page: the grid still lists stored cooked food, the one-line note shows only while it remains (switch off, singular /
     plural); with 38 raw + 2 low-count cooked entries the 36 cells start with the cooked ones (switch off) and keep the 0.7.7 count
     order (switch on); the how-to-craft view names what the Farming bag holds with the switch
  G  consumption stays 0.7.7: the bench / craft mirror and haveOf still offer stored cooked food; a bench taking it debits the pool exactly
  H  two starts on a scratch COPY of the live data (and a copy with cooked food added to a pool): pools load, every entry stays visible,
     nothing moves, save + reload keep every count, config / notices / processing files unchanged; withdrawing the cooked copy moves exact
     counts and survives a save + reload
  I  class byte-compare 0.7.8 vs 0.7.9 (normalised per-member disassembly + constant values): only CraftPage's campfire-factor members
     (campFactors, the new campCfg / campPctText, CAMPXPPCT 50 -> 25) and the config kit's version differ; assets differ only in the manifest
  J  the Campfire tab line (CraftPage.campNote) with the REAL SkyyCooking 0.1.3 classes on the bridge, its kit started on a scratch copy
     of the live cooking.properties (updated 0.5 -> 0.25 by CookMig first): SkyyCooking missing -> plain food / no XP; present -> "25%
     Cooking XP, 75% ..."; an edited live value (Server Setup set 0.4 + the kit's reload) -> 40% at once; cook:fn:campfactors missing or
     malformed -> the same live 40% through config:fn:SkyyCooking; graded cooking off (either source) -> the off line; neither source /
     junk answers -> the 25% / 75% fallback; the 0.7.8 CraftPage (own loader) with SkyyCooking 0.1.3 also showed the live 25% (it already
     read cook:fn:campfactors) - its only stale number was the fallback 50%
Not testable without the game (UNVERIFIED): the page on a client, real pickups into the inventory, the Server Setup page in SkyyMenu.
Nothing is deployed and nothing under AppData is written. Default scratch folder tools/dev/scratch/campxp/sacks (deleted unless --keep).
Exit code 1 on any failure.
"""
import os, sys, re, shutil, subprocess, zipfile, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD, ORACLE_V, COOK_V = "0.7.9", "0.7.8", "0.7.7", "0.1.3"
PKG = "com.skyy.sacks."
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DEFAULT = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySacks")
COOK_JAR = os.path.join(APPDATA, "Hytale", "UserData", "Mods", "SkyyCooking.jar")
LIVECOOK_DEFAULT = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyCooking", "cooking.properties")


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "campxp", "sacks")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLDJAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyySacks-%s.jar" % OLD)))
ORACLEJAR = os.path.abspath(arg("--oracle", os.path.join(HERE, "SkyySacks-%s.jar" % ORACLE_V)))
COOKJAR = os.path.abspath(arg("--cook", os.path.join(ROOT, "SkyyCooking", "SkyyCooking-%s.jar" % COOK_V)))
LIVECOOK = os.path.abspath(arg("--livecook", LIVECOOK_DEFAULT))
LIVE = os.path.abspath(arg("--live", LIVE_DEFAULT))
KEEP = "--keep" in sys.argv

FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


# the expected rule (the build's FOOD_COOKED / FOOD_RAW table + its rule for ids outside it)
FOOD_COOKED = ("Food_Bread", "Food_Candy_Cane", "Food_Cheese", "Food_Fish_Grilled", "Food_Kebab_Fruit", "Food_Kebab_Meat",
               "Food_Kebab_Mushroom", "Food_Kebab_Vegetable", "Food_Pie_Apple", "Food_Pie_Meat", "Food_Pie_Pumpkin", "Food_Popcorn",
               "Food_Salad_Berry", "Food_Salad_Caesar", "Food_Salad_Mushroom", "Food_Vegetable_Cooked", "Food_Wildmeat_Cooked")
FOOD_RAW = ("Food_Beef_Raw", "Food_Chicken_Raw", "Food_Egg", "Food_Fish_Raw", "Food_Fish_Raw_Epic", "Food_Fish_Raw_Legendary",
            "Food_Fish_Raw_Rare", "Food_Fish_Raw_Uncommon", "Food_Pork_Raw", "Food_Wildmeat_Raw")
# Food_ items of the pack mods installed in UserData/Mods (all DISABLED in the HUD mod world on 2026-09-30; the two enabled non-Skyy
# mods - Helios Saplings From Trees, Serj More Crossbow Tiers - ship no food): classified by the rule, informational
PACK_FOOD = {"Food_Plate_Egg": True, "Food_Plate_Sausages": True, "Food_Sandwich": True, "Food_Plate_Item": True,  # AleAndHearth
             "Food_Meat_Cooked_Alpha_Trex": True, "Food_Meat_Raw_Alpha_Trex": False,                             # Endgame&QoL
             "Food_Elven_Bread": True,                                                                           # Fullmetal Labyrinth
             "Food_Beef": True, "Food_Chicken": True, "Food_Pork": True, "Food_Wildmeat_Cooked_Big": True,         # More Food
             "Food_Wildmeat_Raw_Big": False,
             "Food_Kebab_Meat_Mushroom": True,                                                                    # Mycology
             "Food_Unsuspicious_Pie_Apple": True, "Food_Unsuspicious_Pie_Pumpkin": True}                          # Welkin
EDGE = ["Skyy_Sack_Farming_Small", "Skyy_Sack_Omni", "Skyy_Cook_Recipe_Fish", "Skyy_Other_Thing", "Skyy_CookX_Stew", "Food_Egg_Duck",
        "Food_Something_New", "Plant_Crop_Wheat_Item", "Fish_Salmon_Item", "Ingredient_Life_Essence", "Ingredient_Life_Essence_Concentrated",
        "Ingredient_Poop", "Ore_Copper", "Ingredient_Bar_Iron", "Ingredient_Bone_Fragment", "Wood_Oak_Trunk", "Weapon_Sword_Iron", ""]


def cooked_rule(i, prefix=None):
    if i is None:
        return False
    if i.startswith("Skyy_"):
        if i.startswith("Skyy_Cook_Recipe_"):
            return False
        if i.startswith("Skyy_Cook_"):
            return True
        return bool(prefix) and prefix.startswith("Skyy_Cook") and i.startswith(prefix)
    if not i.startswith("Food_"):
        return False
    if i == "Food_Egg" or i.startswith("Food_Egg_"):
        return False
    return not (i.endswith("_Raw") or "_Raw_" in i)


def sget(x):
    return None if x is None else str(x)


# ============================================================================================================== child
def run():
    import jpype
    import skyybuild as B
    from jpype import JClass, JArray, JObject, JShort, JString, JInt
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, JAR, COOKJAR, B.JAVASSIST], convertStrings=True)
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()

    # ---------------- A. load + verify
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(JAR).namelist() if n.endswith(".class")]
    names += [n[:-6].replace("/", ".") for n in zipfile.ZipFile(COOKJAR).namelist() if n.endswith(".class")]
    for n in names:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("load " + n + ": " + str(e))
            print("LOAD FAIL", n, e)
    print("A. loaded + verified %d classes (-Xverify:all; SkyySacks 0.7.9 + SkyyCooking 0.1.3 for section J)" % len(names))
    if FAILS:
        return

    # the 0.7.7 SackDefs (oracle) in its own loader (parent = the platform loader: catOf uses java.* only)
    URL = JClass("java.net.URL")
    UCL = JClass("java.net.URLClassLoader")
    File = JClass("java.io.File")
    old_loader = UCL(JArray(URL)([File(ORACLEJAR).toURI().toURL()]), JClass("java.lang.ClassLoader").getPlatformClassLoader())
    OldDefs = JClass(Cls.forName("com.skyy.sacks.SackDefs", True, old_loader))
    check(str(OldDefs.class_.getClassLoader()) != str(loader), "the 0.7.7 oracle comes from its own loader")

    # a bare JVM has no Item asset store: an empty one (Item.UNKNOWN for every id) so ItemStacks / containers work (SkyyGear harness)
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyyTestFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    store = us.allocateInstance(fake.toClass(AS.class_))
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    fm.set(store, JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")())
    fi_ = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item").class_.getDeclaredField("ASSET_STORE")
    fi_.setAccessible(True)
    fi_.set(None, store)
    # an Inventory whose storage / hotbar / backpack are plain SimpleItemContainers (the engine's needs the ECS)
    INVN = "com.hypixel.hytale.server.core.inventory.Inventory"
    ICN = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
    tinv = jp.makeClass("com.hypixel.hytale.server.core.inventory.SkyyTestInv", jp.get(INVN))
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    for f in ("s", "h", "b"):
        tinv.addField(CtF.make("public %s %s;" % (ICN, f), tinv))
    tinv.addConstructor(CtC.make("public SkyyTestInv(%s s, %s h, %s b) { super(); this.s = s; this.h = h; this.b = b; }" % (ICN, ICN, ICN), tinv))
    for m, f in (("getStorage", "s"), ("getHotbar", "h"), ("getBackpack", "b")):
        tinv.addMethod(CtM.make("public %s %s() { return this.%s; }" % (ICN, m, f), tinv))
    TInv = JClass(tinv.toClass(JClass(INVN).class_))

    J = lambda n: JClass(PKG + n)
    Defs, Pool, Sweep, Cfg, Page, Mirror, Rows = J("SackDefs"), J("SackPool"), J("SweepTask"), J("SackCfg"), J("SacksPage"), J("BagMirror"), J("CfgRows")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UUID, Paths, HashMap = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.util.HashMap")
    CHM, Props, Integer = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.Properties"), JClass("java.lang.Integer")
    System = JClass("java.lang.System")
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    U1 = UUID.fromString("00000000-0000-0000-0000-00000000cafe")

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
        for cont, items in ((s, storage), (h, hotbar), (b, backpack)):
            for (iid, q) in items:
                tx = cont.addItemStack(IS(iid, q))
                assert tx.succeeded() and (tx.getRemainder() is None or tx.getRemainder().isEmpty()), (iid, q)
        p = us.allocateInstance(PLA.class_)
        inv_field.set(p, TInv(s, h, b))
        return p

    def inv_counts(p):
        out = {}
        inv = p.getInventory()
        for cont in (inv.getStorage(), inv.getHotbar(), inv.getBackpack()):
            for i in range(int(cont.getCapacity())):
                it = cont.getItemStack(JShort(i))
                if it is None or it.isEmpty():
                    continue
                out[str(it.getItemId())] = out.get(str(it.getItemId()), 0) + int(it.getQuantity())
        return out

    def pool_counts(k):
        m = Pool.pool(k)
        return dict((str(e.getKey()), int(e.getValue().longValue())) for e in m.entrySet())

    def totals(p, k):
        a, b = inv_counts(p), pool_counts(k)
        return dict((i, a.get(i, 0) + b.get(i, 0)) for i in set(a) | set(b))

    def fresh_pools(d):
        Pool.POOLS.clear()
        Pool.DIRTY.clear()
        Pool.BADPOOL.clear()
        Pool.EXEMPT.clear()
        Pool.DIR = Paths.get(d)

    # ---------------- B. config row + file + kit set path
    keys = [str(k) for k in Rows.KEYS]
    ri = keys.index("bags.cookedFood") if "bags.cookedFood" in keys else -1
    check(ri >= 0, "row bags.cookedFood exists")
    if ri >= 0:
        check(str(Rows.TYPES[ri]) == "bool" and str(Rows.DEFS[ri]) == "false" and "live" in str(Rows.FLAGS[ri]).split(",")
              and "danger" not in str(Rows.FLAGS[ri]).split(","), "row bags.cookedFood: bool, default false, live")
        check(str(Rows.LABELS[ri]) == "Cooked food in the Farming bag" and len(str(Rows.LABELS[ri])) <= 40 and len(str(Rows.HELPS[ri])) <= 100,
              "row label / help within the kit limits")
        check(str(Rows.CATS[ri]) == "bags", "row in the Bags group")
    check(int(Rows.KEEP) == 10, "config history KEEP 10")
    check(keys.index("bags.freeRecipes") < ri, "the new row sits after Free bag recipes")
    check(bool(Defs.COOKED_FARM) is False, "COOKED_FARM default false (Skyy's lock)")
    cdir = os.path.join(SCRATCH, "cfg")
    os.makedirs(cdir, exist_ok=True)
    cf = os.path.join(cdir, "config.properties")
    Cfg.FILE = Paths.get(cf)
    Cfg.MTIME = -1
    Cfg.reload()
    tpl = open(cf, encoding="utf8").read()
    check("#bags.cookedFood=false" in tpl and "\nbags.cookedFood" not in tpl, "missing file: the template carries the commented #bags.cookedFood=false")
    check(bool(Defs.COOKED_FARM) is False, "template -> switch off")
    for val, want in (("true", True), ("off", False), ("on", True), ("maybe", False), ("yes", True), ("0", False)):
        open(cf, "w", encoding="utf8").write(tpl + "bags.cookedFood=%s\n" % val)
        Cfg.MTIME = -1
        Cfg.reload()
        check(bool(Defs.COOKED_FARM) is want, "file bags.cookedFood=%s -> %s" % (val, want))
    Defs.COOKED_FARM = False
    try:
        Cfg.cookedChanged("bags.cookedFood")
        OKS[0] += 1
    except Exception as e:
        check(False, "after= hook cookedChanged threw %s" % e)
    # the kit's own set path on a COPY of the live config.properties (SkyyMenu Server Setup sends exactly this op)
    live_cfg = os.path.join(SCRATCH, "live", "config.properties")
    if os.path.isfile(live_cfg):
        kd = os.path.join(SCRATCH, "kit", "Skyy_SkyySacks")
        os.makedirs(kd, exist_ok=True)
        shutil.copyfile(live_cfg, os.path.join(kd, "config.properties"))
        before = open(os.path.join(kd, "config.properties"), "rb").read()
        Cfg.FILE = Paths.get(os.path.join(kd, "config.properties"))
        Cfg.MTIME = -1
        Cfg.reload()
        CfgPub = J("CfgPub")
        CfgPub.start(Paths.get(os.path.dirname(kd)), None)
        fn = bridge.get("config:fn:SkyySacks")
        OA = JArray(JObject)
        r1 = fn.apply(OA(["set", "bags.cookedFood", "true", None, "console", "yes", "console"]))
        CfgPub.flush()
        kt = open(os.path.join(kd, "config.properties"), "rb").read().decode("latin-1")
        check(r1 is not None and str(r1[0]) == "ok" and bool(Defs.COOKED_FARM) is True and "\nbags.cookedFood=true" in kt.replace("\r\n", "\n")
              and kt.replace("\r\n", "\n").startswith(before.decode("latin-1").replace("\r\n", "\n")),
              "kit set bags.cookedFood=true: ok, field on, line written, the live lines kept (%s)" % (None if r1 is None else str(r1[2])))
        Cfg.MTIME = -1
        Cfg.reload()
        check(bool(Defs.COOKED_FARM) is True, "SackCfg.reload reads the kit-written line (on)")
        r2 = fn.apply(OA(["set", "bags.cookedFood", "false", None, "console", "yes", "console"]))
        CfgPub.flush()
        kt2 = open(os.path.join(kd, "config.properties"), "rb").read().decode("latin-1").replace("\r\n", "\n")
        check(r2 is not None and str(r2[0]) == "ok" and bool(Defs.COOKED_FARM) is False and "\nbags.cookedFood=false" in kt2,
              "kit set bags.cookedFood=false: field off, line rewritten in place")
        try:
            CfgPub.shutdown()
        except Exception:
            pass
    else:
        print("note: no live config.properties copy - kit set path skipped")
    Defs.COOKED_FARM = False
    print("B. config row / file / kit path checked")

    # ---------------- C. classification (every Assets.zip id + SkyyCooking + packs + edge ids), switch off / on, prefix off / on
    za = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
    with zipfile.ZipFile(za) as z:
        vanilla = sorted(set(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json")))
    cook_ids = []
    if os.path.isfile(COOK_JAR):
        with zipfile.ZipFile(COOK_JAR) as z:
            cook_ids = sorted(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    else:
        cook_ids = ["Skyy_Cook_Food_Bread_G%d" % g for g in range(1, 13)] + ["Skyy_Cook_Recipe_Fish"]
        print("note: SkyyCooking.jar not found - synthetic Skyy_Cook ids used")
    ids = vanilla + cook_ids + sorted(PACK_FOOD) + EDGE
    food = [i for i in vanilla if i.startswith("Food_")]
    check(sorted(food) == sorted(FOOD_COOKED + FOOD_RAW), "the vanilla Food_ list is exactly the build table (%d ids)" % len(food))
    bad = []
    for prefix in (None, "Skyy_Cook_Food_", "Skyy_CookX_"):
        if prefix is None:
            bridge.remove("cook:prefix")
        else:
            bridge.put("cook:prefix", prefix)
        for sw in (False, True):
            Defs.COOKED_FARM = sw
            for i in ids:
                old = sget(OldDefs.catOf(i))
                home = sget(Defs.homeOf(i))
                cat = sget(Defs.catOf(i))
                ck = bool(Defs.cooked(i))
                exp_ck = cooked_rule(i, prefix)
                if home != old:
                    bad.append("homeOf(%s)=%s vs 0.7.7 %s" % (i, home, old))
                if ck != exp_ck:
                    bad.append("cooked(%s)=%s vs rule %s (prefix %s)" % (i, ck, exp_ck, prefix))
                want = old if (sw or not exp_ck) else None
                if cat != want:
                    bad.append("catOf(%s)=%s switch %s prefix %s, want %s" % (i, cat, sw, prefix, want))
                if exp_ck and old != "Farming":
                    bad.append("cooked %s was not a Farming item in 0.7.7 (%s)" % (i, old))
    bridge.remove("cook:prefix")
    Defs.COOKED_FARM = False
    check(not bad, "classification: %d ids x 2 switch states x 3 prefix states agree with 0.7.7 + the rule%s"
          % (len(ids), "" if not bad else " - " + "; ".join(bad[:8])))
    for i in (None,):
        check(Defs.catOf(i) is None and Defs.homeOf(i) is None and not bool(Defs.cooked(i)), "null id -> no bag")
    for i, want in PACK_FOOD.items():
        check(cooked_rule(i) == want, "pack food %s classified %s" % (i, "cooked" if want else "raw"))
    plant = [i for i in vanilla if i.startswith("Plant_")]
    fish = [i for i in vanilla if i.startswith("Fish_")]
    dishes = [i for i in cook_ids if not i.startswith("Skyy_Cook_Recipe_")]
    recs = [i for i in cook_ids if i.startswith("Skyy_Cook_Recipe_")]
    Defs.COOKED_FARM = False
    check(all(sget(Defs.catOf(i)) == "Farming" for i in plant + fish), "every Plant_ / Fish_ id -> Farming (switch off)")
    check(all(Defs.catOf(i) is None and sget(Defs.homeOf(i)) == "Farming" for i in dishes), "every graded dish: no intake, home Farming (off)")
    check(all(Defs.catOf(i) is None and Defs.homeOf(i) is None for i in recs), "Skyy_Cook_Recipe_* never pool")
    Defs.COOKED_FARM = True
    check(all(sget(Defs.catOf(i)) == "Farming" for i in dishes + list(FOOD_COOKED)), "switch on: dishes + cooked food -> Farming (0.7.7)")
    Defs.COOKED_FARM = False
    print("C. classification table (vanilla Food_, switch OFF / ON):")
    rows = []
    for i in sorted(food):
        Defs.COOKED_FARM = False
        off = sget(Defs.catOf(i))
        Defs.COOKED_FARM = True
        on = sget(Defs.catOf(i))
        Defs.COOKED_FARM = False
        rows.append("     %-26s %-7s off=%-8s on=%s" % (i, "COOKED" if cooked_rule(i) else "raw", off, on))
    for r_ in rows:
        print(r_)
    print("     Plant_ %d + Fish_ %d ids: raw -> Farming both ways; Skyy_Cook dishes %d: off=none on=Farming; Skyy_Cook_Recipe_ %d: none; "
          "every id checked: %d" % (len(plant), len(fish), len(dishes), len(recs), len(ids)))

    # ---------------- D. intake paths refuse cooked food
    COOKED_IN = [("Food_Bread", 10), ("Food_Pie_Apple", 3), ("Skyy_Cook_Food_Kebab_Meat_G4", 2), ("Food_Wildmeat_Cooked", 5)]
    RAW_IN = [("Plant_Crop_Wheat_Item", 20), ("Food_Beef_Raw", 5), ("Food_Egg", 4), ("Fish_Salmon_Item", 2), ("Food_Fish_Raw_Rare", 1)]
    dd = os.path.join(SCRATCH, "pools-d")
    for bag in ("Skyy_Sack_Farming_Small", "Skyy_Sack_Omni"):
        for sw in (False, True):
            Defs.COOKED_FARM = sw
            fresh_pools(dd)
            k = "d-%s-%s" % (bag, sw)
            p = player(storage=COOKED_IN + RAW_IN + [("Ore_Copper", 7)], hotbar=[(bag, 1)])
            before = totals(p, k)
            moved = int(Sweep.sweep(p, k, None, False))
            after_inv, after_pool = inv_counts(p), pool_counts(k)
            nraw = sum(q for _i, q in RAW_IN)
            ncook = sum(q for _i, q in COOKED_IN)
            nore = 7 if bag == "Skyy_Sack_Omni" else 0
            check(totals(p, k) == before, "auto-pickup (%s, switch %s): every item counted, nothing lost or duplicated" % (bag, sw))
            if not sw:
                check(moved == nraw + nore and all(after_inv.get(i) == q for i, q in COOKED_IN) and not any(i in after_pool for i, _q in COOKED_IN)
                      and all(after_pool.get(i) == q for i, q in RAW_IN),
                      "auto-pickup (%s, switch off): raw produce pooled (%d), cooked food stays in the inventory (%d) - moved %d"
                      % (bag, nraw, ncook, moved))
            else:
                check(moved == nraw + ncook + nore and all(after_pool.get(i) == q for i, q in COOKED_IN + RAW_IN),
                      "auto-pickup (%s, switch on = 0.7.7): cooked food pools too - moved %d" % (bag, moved))
            # Deposit all (the button: exemptions cleared, every container, only this tab's category)
            p2 = player(storage=COOKED_IN[:2] + RAW_IN[:2], hotbar=[(bag, 1)] + COOKED_IN[2:] + RAW_IN[2:3], backpack=RAW_IN[3:])
            k2 = k + "-dep"
            b2 = totals(p2, k2)
            Pool.clearExempt(k2)
            dep = int(Sweep.sweep(p2, k2, "Farming", True))
            a2 = pool_counts(k2)
            check(totals(p2, k2) == b2, "Deposit all (%s, switch %s): every item counted" % (bag, sw))
            if not sw:
                check(dep == nraw and not any(i in a2 for i, _q in COOKED_IN), "Deposit all (%s, switch off): refuses cooked food, takes %d raw" % (bag, nraw))
            else:
                check(dep == nraw + ncook, "Deposit all (%s, switch on): takes cooked food too (0.7.7)" % bag)
    Defs.COOKED_FARM = False
    # review fix: the Deposit all hint counts the cooked food on hand (storage + hotbar + backpack); raw produce and bags do not count
    ph = player(storage=COOKED_IN[:2] + RAW_IN[:2], hotbar=[("Skyy_Sack_Farming_Small", 1)] + COOKED_IN[2:3], backpack=COOKED_IN[3:] + RAW_IN[3:])
    bh = inv_counts(ph)
    check(int(Sweep.cookedHeld(ph.getInventory())) == sum(q for _i, q in COOKED_IN) and inv_counts(ph) == bh,
          "cookedHeld: %d cooked items on hand across storage / hotbar / backpack, nothing moved" % sum(q for _i, q in COOKED_IN))
    check(int(Sweep.cookedHeld(player(storage=RAW_IN, hotbar=[("Skyy_Sack_Omni", 1)]).getInventory())) == 0 and int(Sweep.cookedHeld(None)) == 0,
          "cookedHeld: raw produce / no inventory -> 0")
    pb = zipfile.ZipFile(JAR).read("com/skyy/sacks/SacksPage.class")
    check(b" - cooked food stays in your inventory" in pb and b"nothing to deposit (or sack full)" in pb, "Deposit all carries the cooked-food hint")
    print("D. auto-pickup + Deposit all checked (Farming bag and Omni, switch off / on; cookedHeld)")

    # ---------------- E. stored cooked food stays retrievable (switch off)
    fresh_pools(os.path.join(SCRATCH, "pools-e"))
    k = "e"
    for i, q in COOKED_IN + RAW_IN:
        Pool.add(k, i, q)
    nco = sum(q for _i, q in COOKED_IN)
    check(int(Pool.cookedTotal(k)) == nco and int(Pool.catTotal(k, "Farming")) == nco + sum(q for _i, q in RAW_IN),
          "catTotal(Farming) counts stored cooked food, cookedTotal = %d" % nco)
    nobag = player()
    check(int(Sweep.withdraw(nobag, k, "Food_Bread", 64)) == 0 and pool_counts(k).get("Food_Bread") == 10, "no bag on you: nothing taken out")
    p = player(hotbar=[("Skyy_Sack_Farming_Small", 1)])
    b0 = totals(p, k)
    got = int(Sweep.withdraw(p, k, "Food_Bread", 1))
    check(got == 1 and pool_counts(k).get("Food_Bread") == 9 and inv_counts(p).get("Food_Bread") == 1 and totals(p, k) == b0,
          "right click takes one stored cooked item (counted)")
    got = int(Sweep.withdraw(p, k, "Food_Bread", 64))
    check(got == 9 and "Food_Bread" not in pool_counts(k) and inv_counts(p).get("Food_Bread") == 10 and totals(p, k) == b0,
          "left click takes the rest of the stack (9, counted)")
    # the Pick up all loop exactly as SacksPage.handleDataEvent runs it over the cells
    cells = [i for i in pool_counts(k)]
    total = 0
    for c in cells:
        guard = 0
        while True:
            added = int(Sweep.withdraw(p, k, c, 64))
            total += added
            guard += 1
            if not (added > 0 and guard < 64):
                break
    check(not pool_counts(k) and totals(p, k) == b0 and total == sum(q for _i, q in COOKED_IN + RAW_IN) - 10,
          "Pick up all empties the tab, cooked + raw, counted (%d; pool left %s)" % (total, pool_counts(k)))
    Pool.clearExempt(k)
    Sweep.sweep(p, k, None, False)
    pc = pool_counts(k)
    check(not any(i in pc for i, _q in COOKED_IN) and all(pc.get(i) == q for i, q in RAW_IN) and totals(p, k) == b0,
          "the next sweep (exemptions cleared) puts the raw produce back but never the cooked food")
    print("E. stored cooked food: withdraw / Pick up all checked")

    # ---------------- F. the bag page
    PAGE_PR = jfield(Page.class_, "playerRef")
    pr = us.allocateInstance(PR.class_)
    jfield(PR.class_, "uuid").set(pr, U1)
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def render(p, k, cat):
        pg = us.allocateInstance(Page.class_)
        PAGE_PR.set(pg, pr)
        pg.cat = cat
        pg.info = ""
        caps, ranks = HashMap(), HashMap()
        Sweep.scan(p.getInventory(), caps, ranks)
        b = UCB()
        pg.render(b, UEB(), p, k, caps, ranks)
        txt = []
        for c in b.getCommands():
            for f in ("data", "text", "selector"):
                try:
                    v = getattr(c, f)
                    if v is not None:
                        txt.append(str(v))
                except Exception:
                    pass
        cells = [str(x) for x in pg.cells] if pg.cells is not None else []
        return "\n".join(txt), [x for x in cells if x != "None"]

    fresh_pools(os.path.join(SCRATCH, "pools-f"))
    k = "f"
    for i, q in COOKED_IN + RAW_IN:
        Pool.add(k, i, q)
    pf = player(hotbar=[("Skyy_Sack_Farming_Medium", 1)])
    NOTE = "Cooked food no longer goes into this bag - %d cooked items are still here to take out" % nco
    t, cells = render(pf, k, "Farming")
    check(all(i in cells for i, _q in COOKED_IN + RAW_IN), "the Farming grid still lists the stored cooked food (%d cells)" % len(cells))
    check(NOTE in t, "the Farming tab shows the one-line note while cooked food remains")
    t2, _c = render(pf, k, "Mining")
    check("Cooked food no longer" not in t2, "no note on another tab")
    Defs.COOKED_FARM = True
    t3, cells3 = render(pf, k, "Farming")
    check("Cooked food no longer" not in t3 and all(i in cells3 for i, _q in COOKED_IN), "switch on: no note, same grid")
    Defs.COOKED_FARM = False
    for i, q in COOKED_IN:
        Pool.add(k, i, -q)
    t4, _c = render(pf, k, "Farming")
    check("Cooked food no longer" not in t4, "no note once the cooked food is gone")
    Pool.add(k, "Food_Bread", 1)
    t4b, _c = render(pf, k, "Farming")
    check("Cooked food no longer goes into this bag - 1 cooked item is still here to take out" in t4b, "the note is singular for one cooked item")
    Pool.add(k, "Food_Bread", -1)
    # review fix: 38 raw entries (counts 100..137) + 2 low-count cooked entries - the 36 cells must still reach the cooked food (switch off)
    fresh_pools(os.path.join(SCRATCH, "pools-f2"))
    k = "f2"
    raw38 = plant[:38]
    for n_, i in enumerate(raw38):
        Pool.add(k, i, 100 + n_)
    Pool.add(k, "Food_Bread", 1)
    Pool.add(k, "Skyy_Cook_Food_Kebab_Meat_G4", 2)
    b_f2 = dict(pool_counts(k))
    t7, cells7 = render(pf, k, "Farming")
    check(len(cells7) == 36 and cells7[:2] == ["Skyy_Cook_Food_Kebab_Meat_G4", "Food_Bread"]
          and cells7[2:] == sorted(raw38, key=lambda i: -b_f2[i])[:34],
          "switch off: the 36 cells start with the stored cooked food (count order), then the raw produce by count: %s" % cells7[:3])
    check("Cooked food no longer goes into this bag - 3 cooked items are still here to take out" in t7, "the note counts both cooked entries (plural)")
    Defs.COOKED_FARM = True
    t8, cells8 = render(pf, k, "Farming")
    order77 = sorted(b_f2, key=lambda i: (-b_f2[i], i))[:36]
    check(cells8 == order77 and "Food_Bread" not in cells8, "switch on: the 0.7.7 count order (cooked food last, off the 36 cells)")
    Defs.COOKED_FARM = False
    check(pool_counts(k) == b_f2, "rendering the grid moves nothing")
    nb = player()
    t5, _c = render(nb, k, "Farming")
    check("A Farming Bag holds plants, raw food, fish and life essence." in t5, "how-to-craft view (off): the Farming bag holds raw food")
    Defs.COOKED_FARM = True
    t6, _c = render(nb, k, "Farming")
    check("A Farming Bag holds plants, food and cooked dishes, fish and life essence." in t6, "how-to-craft view (on): the 0.7.7 text")
    Defs.COOKED_FARM = False
    print("F. bag page grid + note checked")

    # ---------------- G. consumption (bench link + /craft mirror, haveOf) stays 0.7.7
    fresh_pools(os.path.join(SCRATCH, "pools-g"))
    k = "g"
    Pool.add(k, "Food_Bread", 12)
    Pool.add(k, "Plant_Crop_Wheat_Item", 30)
    pg_ = player(storage=[("Food_Bread", 2)], hotbar=[("Skyy_Sack_Farming_Small", 1)])
    caps = Sweep.caps(pg_.getInventory())
    check(int(Page.haveOf(pg_.getInventory(), k, caps, "Food_Bread")) == 14, "haveOf: inventory 2 + stored 12 bread (0.7.7)")
    m = Mirror(k)
    m.rebuild(caps)
    offered = {}
    for s_ in range(36):
        if m.slotIds[s_] is not None:
            offered[str(m.slotIds[s_])] = offered.get(str(m.slotIds[s_]), 0) + int(m.slotQty[s_])
    check(offered.get("Food_Bread") == 12 and offered.get("Plant_Crop_Wheat_Item") == 30, "the bench / craft mirror still offers stored cooked food: %s" % offered)
    # a bench takes 5 bread out of the mirror: sync debits exactly 5
    for s_ in range(36):
        if m.slotIds[s_] is not None and str(m.slotIds[s_]) == "Food_Bread":
            m.cont.removeItemStackFromSlot(JShort(s_), JInt(5))
            break
    used = int(m.sync())
    check(used == 5 and pool_counts(k).get("Food_Bread") == 7, "a bench using 5 stored bread debits exactly 5 (7 left)")
    print("G. consumption paths checked")

    # ---------------- H. two starts on a scratch copy of the live data (+ a copy with cooked food added)
    live = os.path.join(SCRATCH, "live")
    if not os.path.isdir(live):
        print("note: no live data copy - H skipped")
    else:
        variants = [("live", live)]
        lc = os.path.join(SCRATCH, "live-cooked")
        shutil.copytree(live, lc)
        pools_dir = os.path.join(lc, "pools")
        pfiles = sorted(f for f in os.listdir(pools_dir) if f.endswith(".properties")) if os.path.isdir(pools_dir) else []
        ADDED = [("Food_Bread", 12), ("Food_Pie_Apple", 3), ("Skyy_Cook_Food_Kebab_Meat_G4", 2), ("Food_Wildmeat_Cooked", 5)]
        if pfiles:
            with open(os.path.join(pools_dir, pfiles[-1]), "a", encoding="latin-1") as fh:
                for i, q in ADDED:
                    fh.write("%s=%d\n" % (i, q))
            variants.append(("live-cooked", lc))
        for name, d in variants:
            pdir = os.path.join(d, "pools")
            snap = {}
            for root, _ds, fs in os.walk(d):
                for f in fs:
                    snap[os.path.relpath(os.path.join(root, f), d)] = open(os.path.join(root, f), "rb").read()
            filecounts = {}
            for f in sorted(os.listdir(pdir)) if os.path.isdir(pdir) else []:
                if f.endswith(".properties"):
                    pp = Props()
                    fin = JClass("java.io.FileInputStream")(os.path.join(pdir, f))
                    pp.load(fin)
                    fin.close()
                    filecounts[f[:-11]] = dict((str(kk), int(str(pp.getProperty(kk)).strip())) for kk in pp.stringPropertyNames())
            for start in (1, 2):
                Defs.COOKED_FARM = False
                Cfg.FILE = Paths.get(os.path.join(d, "config.properties"))
                Cfg.MTIME = -1
                Cfg.reload()
                Notice = J("SackNotice")
                Notice.SEEN.clear()
                Notice.BROKEN = False
                Notice.DIRTY = False
                Notice.FILE = Paths.get(os.path.join(d, "notices.properties"))
                Notice.load()
                fresh_pools(pdir)
                ok_load = all(pool_counts(kk) == filecounts[kk] for kk in filecounts)
                check(ok_load, "%s start %d: every pool loads with the file's counts" % (name, start))
                hidden = [(kk, i) for kk in filecounts for i in filecounts[kk] if Defs.homeOf(i) is None]
                check(not hidden, "%s start %d: every stored entry belongs to a bag tab (none hidden): %s" % (name, start, hidden[:5]))
                for kk in filecounts:
                    tot = sum(filecounts[kk].values())
                    check(sum(int(Pool.catTotal(kk, c)) for c in [str(x) for x in Defs.CATS]) == tot,
                          "%s start %d: the five tabs show all %d items of %s" % (name, start, tot, kk[:8]))
                    # a sweep with the Omni and cooked food in the inventory changes nothing
                    pp_ = player(storage=[("Food_Bread", 3), ("Skyy_Cook_Food_Pie_Apple_G2", 1)], hotbar=[("Skyy_Sack_Omni", 1)])
                    Sweep.sweep(pp_, kk, None, False)
                    check(pool_counts(kk) == filecounts[kk] and inv_counts(pp_).get("Food_Bread") == 3,
                          "%s start %d: a sweep (Omni, cooked food on hand) leaves %s untouched" % (name, start, kk[:8]))
                    Pool.save(kk)
                Pool.POOLS.clear()
                check(all(pool_counts(kk) == filecounts[kk] for kk in filecounts), "%s start %d: save + reload keeps every count" % (name, start))
                Notice.save()
                for rel in ("config.properties", "notices.properties"):
                    if rel in snap:
                        check(open(os.path.join(d, rel), "rb").read() == snap[rel], "%s start %d: %s unchanged" % (name, start, rel))
                for rel in snap:
                    if rel.startswith("processing"):
                        check(open(os.path.join(d, rel), "rb").read() == snap[rel], "%s start %d: %s unchanged" % (name, start, rel))
            if name == "live-cooked":
                kk = pfiles[-1][:-11]
                fresh_pools(pdir)
                pw = player(hotbar=[("Skyy_Sack_Omni", 1)])
                bw = totals(pw, kk)
                took = 0
                for i, q in ADDED:
                    took += int(Sweep.withdraw(pw, kk, i, 64))
                check(took == sum(q for _i, q in ADDED) and totals(pw, kk) == bw and all(inv_counts(pw).get(i) == q for i, q in ADDED),
                      "live copy with cooked food: the Omni takes every cooked item out, counted (%d)" % took)
                Pool.save(kk)
                Pool.POOLS.clear()
                want = dict(filecounts[kk])
                for i, q in ADDED:
                    want.pop(i, None)
                check(pool_counts(kk) == want, "live copy with cooked food: after save + reload the pool = the live pool (nothing else moved)")
        print("H. two starts on the live copies checked (%s)" % ", ".join(n for n, _d in variants))

    # ---------------- I. class byte-compare 0.7.8 vs 0.7.9
    CP = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def members(jar, cname):
        cp = CP(False)
        cp.appendClassPath(jar)
        cp.appendClassPath(B.SERVER_JAR)
        cp.appendSystemPath()
        cc = cp.get(cname)
        cf = cc.getClassFile()
        out = {}
        for mi in cf.getMethods():
            key = str(mi.getName()) + str(mi.getDescriptor())
            code = mi.getCodeAttribute()
            lines = []
            if code is not None:
                it = code.iterator()
                while it.hasNext():
                    pos = it.next()
                    lines.append(re.sub(r"#\d+ = ", "", str(IP.instructionString(it, pos, cf.getConstPool()))))
            out["m " + key] = "\n".join(lines)
        for fi in cf.getFields():
            cv = int(fi.getConstantValue())
            val = str(cf.getConstPool().getLdcValue(cv)) if cv else ""
            out["f " + str(fi.getName())] = str(fi.getDescriptor()) + " " + str(fi.getAccessFlags()) + " " + val
        return out

    z8, z9 = zipfile.ZipFile(OLDJAR), zipfile.ZipFile(JAR)
    c8 = dict((n, z8.read(n)) for n in z8.namelist() if n.endswith(".class"))
    c9 = dict((n, z9.read(n)) for n in z9.namelist() if n.endswith(".class"))
    check(sorted(c8) == sorted(c9), "I: same class list in 0.7.8 and 0.7.9 (%d)" % len(c9))
    same = sorted(n for n in c9 if c8.get(n) == c9[n])
    diff = sorted(n for n in c9 if n in c8 and c8[n] != c9[n])
    EXPECT = {"CraftPage": {"m campFactors()[I", "m campCfg()[I", "m campPctText(Ljava/lang/Object;)I", "f CAMPXPPCT"},
              "SkyySacksPlugin": {"m setup()V"},
              "CfgRows": {"f VERSION", "m header()[Ljava/lang/Object;"},       # the kit inlines CfgRows.VERSION (a constant)
              "CfgFn": {"m opExport([Ljava/lang/Object;)Ljava/lang/Object;"}}
    report = []
    for n in diff:
        cname = n[:-6].replace("/", ".")
        short = cname.rsplit(".", 1)[1]
        m8, m9 = members(OLDJAR, cname), members(JAR, cname)
        changed = sorted(kk for kk in set(m8) | set(m9) if m8.get(kk) != m9.get(kk))
        report.append("%s: %s" % (short, ", ".join(c.split("(")[0] for c in changed) or "(constant pool only)"))
        allowed = EXPECT.get(short)
        check(allowed is not None and set(changed) <= allowed, "I: class %s differs only in the expected members: %s" % (short, changed))
        if short == "SkyySacksPlugin":
            check(m8["m setup()V"].replace("[SkyySacks] 0.7.8 ready", "[SkyySacks] 0.7.9 ready") == m9["m setup()V"],
                  "I: SkyySacksPlugin.setup differs only in the version of the ready line")
        if short in ("CfgRows", "CfgFn"):
            check(all(m8[c].replace("0.7.8", "0.7.9") == m9[c] for c in changed),
                  "I: config kit class %s differs only in the inlined VERSION 0.7.8 -> 0.7.9" % short)
        if short == "CraftPage":
            check(m8["f CAMPXPPCT"].endswith(" 50") and m9["f CAMPXPPCT"].endswith(" 25") and m8["f CAMPBUFFPCT"] == m9["f CAMPBUFFPCT"]
                  and m9["f CAMPBUFFPCT"].endswith(" 75"), "I: CraftPage CAMPXPPCT 50 -> 25, CAMPBUFFPCT stays 75 (%s / %s)"
                  % (m8["f CAMPXPPCT"], m9["f CAMPXPPCT"]))
            check("m campCfg()[I" not in m8 and "m campPctText(Ljava/lang/Object;)I" not in m8 and m8["m campNote()Ljava/lang/String;"] == m9["m campNote()Ljava/lang/String;"]
                  and m8["m campPct(Ljava/lang/Object;I)I"] == m9["m campPct(Ljava/lang/Object;I)I"],
                  "I: campCfg / campPctText are new, campNote and campPct are unchanged")
    check(sorted(diff) == sorted("com/skyy/sacks/%s.class" % c for c in EXPECT), "I: exactly CraftPage, the plugin, CfgRows and CfgFn changed: %s" % diff)
    print("I. classes byte-identical: %d of %d" % (len(same), len(c9)))
    print("   classes that differ: %d" % len(diff))
    for r in report:
        print("     " + r)
    a8 = dict((n, z8.read(n)) for n in z8.namelist() if not n.endswith(".class"))
    a9 = dict((n, z9.read(n)) for n in z9.namelist() if not n.endswith(".class"))
    check(sorted(a8) == sorted(a9), "I: same asset list (%d)" % len(a9))
    adiff = sorted(n for n in a9 if a8.get(n) != a9[n])
    check(adiff == ["manifest.json"], "I: assets that differ: %s" % adiff)
    m8, m9 = json.loads(a8["manifest.json"]), json.loads(a9["manifest.json"])
    check(m8["Version"] == OLD and m9["Version"] == VERSION and m9["Name"] == "0.7.9 SkyySacks"
          and dict(m8, Version=0, Name=0) == dict(m9, Version=0, Name=0), "I: manifest: only Name / Version -> 0.7.9")
    print("   assets that differ: %s" % ", ".join(adiff))

    # ---------------- J. the Campfire tab line with the real SkyyCooking 0.1.3 on the bridge
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, a):
            return self.f(a)

    OA = JArray(JObject)
    Double = JClass("java.lang.Double")
    CPg = J("CraftPage")
    CK = lambda n: JClass("com.skyy.cooking." + n)
    CCfg, CMig, CPub = CK("CookCfg"), CK("CookMig"), CK("CfgPub")
    NOTE_MISSING = "Campfire accessory = quick emergency cooking: plain food and no Cooking XP (SkyyCooking is not installed)."
    NOTE_OFF = "Campfire accessory = quick emergency cooking: graded cooking is switched off on this server - plain food and no Cooking XP."

    def note(xp, buff):
        return "Campfire accessory = emergency cook: %d%% Cooking XP, %d%% of your cooking bonus. A Cooking Bench gives the full Grade and XP." % (xp, buff)

    def tab():
        return str(CPg.campNote())

    for k_ in ("cook:campfire:ids", "cook:fn:campfactors", "config:fn:SkyyCooking", "config:def:SkyyCooking"):
        bridge.remove(k_)
    check(tab() == NOTE_MISSING, "J: SkyyCooking missing -> %r" % tab())
    check([int(x) for x in CPg.campFactors()] == [25, 75, 1], "J: no live source -> fallback numbers 25 / 75 (SkyyCooking 0.1.3 defaults)")
    lc = os.path.join(SCRATCH, "livecook", "cooking.properties")
    jd = os.path.join(SCRATCH, "j-cook", "mods", "Skyy_SkyyCooking")
    os.makedirs(jd)
    jf = os.path.join(jd, "cooking.properties")
    if os.path.isfile(lc):
        shutil.copyfile(lc, jf)
    else:
        print("note: no live cooking.properties copy - section J starts SkyyCooking on a fresh file")
    # SkyyCooking's own setup() steps (bridge keys as setup() publishes them)
    CCfg.FILE = Paths.get(jf)
    mres = str(CMig.migrate())
    CCfg.load()
    bridge.put("cook:campfire:ids", CCfg.campList())
    real_cf = CK("CookCampInfoFn")()
    bridge.put("cook:fn:campfactors", real_cf)
    CPub.start(Paths.get(os.path.dirname(jd)), None)
    fn = bridge.get("config:fn:SkyyCooking")
    check(fn is not None and str(fn.apply(OA(["get", "campfire.xpFactor"]))) == "0.25" and abs(float(CCfg.CAMP_XP) - 0.25) < 1e-12,
          "J: SkyyCooking 0.1.3 started on the live copy: campfire.xpFactor 0.25 (%s)" % (mres or "fresh file"))
    check(tab() == note(25, 75), "J: SkyyCooking present -> live 25%% / 75%%: %r" % tab())
    r1 = fn.apply(OA(["set", "campfire.xpFactor", "0.4", None, "console", "yes", "console"]))
    CPub.flush()
    check(r1 is not None and str(r1[0]) == "ok" and abs(float(CCfg.CAMP_XP) - 0.4) < 1e-12 and tab() == note(40, 75),
          "J: an edited live value (Server Setup set 0.4 + the kit's reload) shows at once: %r" % tab())
    bridge.remove("cook:fn:campfactors")
    check(tab() == note(40, 75), "J: cook:fn:campfactors missing -> the live 40%% through config:fn:SkyyCooking: %r" % tab())
    for name_, bad in (("junk elements", lambda a: OA([JString("x"), None])), ("null answer", lambda a: None),
                       ("short array", lambda a: OA([Double(0.75)])), ("factor out of range", lambda a: OA([Double(1.5), Double(0.4)])),
                       ("not an array", lambda a: JString("0.25"))):
        bridge.put("cook:fn:campfactors", Fn(bad))
        check(tab() == note(40, 75), "J: cook:fn:campfactors %s -> config:fn:SkyyCooking (40%%): %r" % (name_, tab()))
    bridge.put("cook:fn:campfactors", real_cf)
    r2 = fn.apply(OA(["set", "enabled", "false", None, "console", "yes", "console"]))
    CPub.flush()
    check(r2 is not None and str(r2[0]) == "ok" and not bool(CCfg.ENABLED) and tab() == NOTE_OFF,
          "J: graded cooking off (cook:fn:campfactors enabled FALSE) -> the off line: %r" % tab())
    bridge.remove("cook:fn:campfactors")
    check(tab() == NOTE_OFF, "J: graded cooking off through config:fn:SkyyCooking get enabled -> the off line: %r" % tab())
    fn.apply(OA(["set", "enabled", "true", None, "console", "yes", "console"]))
    CPub.flush()
    check(bool(CCfg.ENABLED) and tab() == note(40, 75), "J: graded cooking on again -> 40%%")
    bridge.remove("config:fn:SkyyCooking")
    check(tab() == note(25, 75), "J: SkyyCooking running but answering neither key -> fallback 25%% / 75%%: %r" % tab())
    for name_, bad in (("text abc", lambda a: JString("abc")), ("null", lambda a: None), ("a number object", lambda a: Double(0.4)),
                       ("out of range text", lambda a: JString("1.5"))):
        bridge.put("config:fn:SkyyCooking", Fn(bad))
        check(tab() == note(25, 75), "J: config:fn:SkyyCooking answering %s -> fallback 25%% / 75%%: %r" % (name_, tab()))
    bridge.put("config:fn:SkyyCooking", fn)
    bridge.put("cook:fn:campfactors", real_cf)
    check(tab() == note(40, 75), "J: both sources back -> 40%%")
    # contrast: the live 0.7.8 CraftPage in its own loader (+ the server jar) on the same bridge
    try:
        l78 = UCL(JArray(URL)([File(OLDJAR).toURI().toURL(), File(B.SERVER_JAR).toURI().toURL()]), JClass("java.lang.ClassLoader").getPlatformClassLoader())
        Old = JClass(Cls.forName("com.skyy.sacks.CraftPage", True, l78))
        o_live = str(Old.campNote())
        bridge.remove("cook:fn:campfactors")
        o_cfg = str(Old.campNote())
        bridge.put("cook:fn:campfactors", real_cf)
        check(o_live == note(40, 75) and o_cfg == note(50, 75),
              "J: 0.7.8 already showed the live share from cook:fn:campfactors (%r); without it, it fell back to 50%% (%r)" % (o_live, o_cfg))
        print("J. 0.7.8 for contrast: with cook:fn:campfactors %r; without it %r" % (o_live[37:62], o_cfg[37:62]))
    except Exception as e:
        check(False, "J: the 0.7.8 CraftPage could not be loaded for the contrast check: %s" % e)
    try:
        CPub.shutdown()
    except Exception:
        pass
    print("J. Campfire tab: missing -> plain food / no XP; live 0.25 -> 25%; edited 0.4 -> 40% (campfactors or config:fn); off line; fallback 25% / 75%")


# ============================================================================================================== parent
def main():
    if "--child" in sys.argv:
        try:
            run()
        except Exception as e:
            import traceback
            traceback.print_exc()
            FAILS.append("child crashed: %s" % e)
        print("%d ok, %d failed" % (OKS[0], len(FAILS)))
        sys.exit(1 if FAILS else 0)
    for p in (JAR, OLDJAR, ORACLEJAR, COOKJAR):
        if not os.path.isfile(p):
            raise SystemExit("missing " + p + " (build it first)")
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"))
    if os.path.isdir(LIVE):
        shutil.copytree(LIVE, os.path.join(SCRATCH, "live"))      # READ ONLY copy of the live data
        print("copied live data (read only): %s" % LIVE)
    else:
        print("note: live data folder not found: %s" % LIVE)
    if os.path.isfile(LIVECOOK):
        os.makedirs(os.path.join(SCRATCH, "livecook"))
        shutil.copyfile(LIVECOOK, os.path.join(SCRATCH, "livecook", "cooking.properties"))      # READ ONLY copy
        print("copied the live cooking.properties (read only): %s" % LIVECOOK)
    else:
        print("note: live cooking.properties not found: %s" % LIVECOOK)
    env = dict(os.environ, TEMP=os.path.join(SCRATCH, "tmp"), TMP=os.path.join(SCRATCH, "tmp"))
    env.pop("JAVA_TOOL_OPTIONS", None)
    args = [sys.executable, os.path.abspath(__file__), "--child", "--dir", SCRATCH, "--jar", JAR, "--old", OLDJAR, "--oracle", ORACLEJAR,
            "--cook", COOKJAR]
    rc = subprocess.call(args, env=env, cwd=ROOT)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyySacks %s bare-JVM check: %s (exit code %d)%s" % (VERSION, "PASS" if rc == 0 else "FAIL", rc, "" if KEEP else " (scratch folder removed)"))
    sys.exit(rc)


if __name__ == "__main__":
    main()
