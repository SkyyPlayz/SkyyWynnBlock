"""Bare-JVM check for SkyySacks 0.7.11 (KEPT counts replace the 10-minute exemption, STACK AUTO-REFILL with the per-player 3-way setting,
BAGS ADD UP - Skyy 2026-10-02, OPEN-QUESTIONS Q&A rounds 2-4), kept next to the build so the build report's claims can be re-run. The
0.7.10 harness carried forward: A, B, C, F, G, H, J, W unchanged in what they prove (C now compares every id with 0.7.10 too: no id moved),
D / E / K use the 0.7.11 Deposit all (clearKeptCat instead of the exemption), E proves that taken-out items stay (kept), I compares
0.7.10 vs 0.7.11, L also loads the refill choices at start; new M = kept counts, N = the stack refill in each mode, P = refill + sweep
never fight (20 ticks per scenario), Q = bags add up, R = the refill setting (persisted, page row, clicks), S = relog / profile switch /
busy profile.

    python SkyySacks/test_skyysacks_0.7.11.py [--jar <0.7.11 jar>] [--old <0.7.10 jar>] [--oracle <0.7.7 jar>] [--cook <SkyyCooking 0.1.3 jar>]
        [--acc <SkyyAccessories 0.5.2 jar>] [--live <Skyy_SkyySacks folder>] [--liveacc <Skyy_SkyyAccessories folder>]
        [--livecook <cooking.properties>] [--dir <scratch>] [--keep]

Build first (python SkyySacks/build_skyysacks_0.7.11.py; the 0.7.10 / 0.7.8 / 0.7.7 jars, SkyyAccessories 0.5.2 and SkyyCooking 0.1.3 are
the built ones). The parent copies the live data folders and the live cooking.properties (read only; default: the "HUD mod" world's
mods/Skyy_SkyySacks, mods/Skyy_SkyyAccessories and mods/Skyy_SkyyCooking/cooking.properties) into the scratch folder and starts a child: a
fresh JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + the 0.7.11 jar + SkyyAccessories 0.5.2 + SkyyCooking 0.1.3 +
tools/javassist.jar, java.io.tmpdir / TEMP / TMP in the scratch folder). The 0.7.7 SackDefs (oracle) and the 0.7.10 SackDefs load from their
jars in their own class loaders.
Checks:
  A  every 0.7.11 class, every SkyyCooking 0.1.3 class (J) and SkyyAccessories' Workbench tab classes (W) load and verify (-Xverify:all)
  B  the Server Setup rows (bags.cookedFood; the Unique bag help says bags add up) and the kit's set path on a copy of the live config
  C  classification of EVERY item id in Assets.zip + SkyyCooking items + pack Food_ ids + edge ids, switch off / on, cook:prefix off / on:
     homeOf == 0.7.7 catOf except Ingredient_Charcoal -> Smithing; catOf follows; AND homeOf == 0.7.10 homeOf for every id (none moved)
  D-H the cooked-food rule as 0.7.8 - 0.7.10 tested it (intake, retrieval, bag page, consumption, two starts on the live copies)
  I  class byte-compare 0.7.10 vs 0.7.11: exactly SackPool, SweepTask, SacksPage, SackSaver, SackCfg, the plugin and the kit's CfgRows /
     CfgFn / CfgFile (review fix 8: two more rows) differ, + RefillPref / KeptQuit; every other class byte-identical; assets: only the
     manifest version
  J  the Campfire tab line with the real SkyyCooking 0.1.3 (unchanged since 0.7.9; the contrast check still uses the 0.7.8 jar)
  K  charcoal (0.7.10) still: auto-pickup into a Smithing bag / the Omni, Deposit all on the Smithing tab, withdraw, save + reload
  W  the Workbench tab on real engine objects (tools/skyywbtab.py harness_checks, unchanged since 0.7.10)
  L  the two mods' start sequences alone and together in both orders on fresh scratch copies of their live data folders, twice each
     (SkyySacks now also loads refill.properties): every file byte-identical, no new file
  M  kept: withdraw 512 -> the sweep leaves 512 (also split 64 hotbar + 448 storage), mining +10 -> the sweep takes 10 (also when the 10
     land in the hotbar), placing lowers kept, a hand-moved stack is no change, Pick up all adds, Deposit all clears that tab only
  N  refill in each mode: HOTBAR tops a used hotbar stack (never storage, never an empty slot, never an unused stack); FULL also tops the
     main inventory and backpack; OFF does nothing; the pool runs out; no bag (or another type's bag) -> nothing; a metadata stack is never
     touched; a bench fed from the bags -> the refill waits, the use stays pending and is refilled once it closes; refilled items add to
     kept and stay; every case counted (inventory + pool totals)
  P  refill + sweep never fight: 7 scenarios x 20 ticks (idle, use then idle, bag full with spare stone in storage x 2 modes, mined excess
     + a used stack, a steady builder, single pickups into free hotbar slots): no item moves back the other way, nothing moves once idle
  Q  bags add up: 2 Normal = 2x, Normal + Legendary, Omni + Legendary, Omni alone / two Omni, a stack of 2 bags, unknown bag ids skipped,
     the int clamp, the sweep uses the summed room, dropping a bag deletes nothing, the page's cap line + "From N bags" line
  R  the refill setting: default Hotbar only, set / save / load round trip (refill.properties), an unknown word is kept, an unreadable
     file is left untouched (session only), the page row in both views (the chosen button on Tertiary_Active, the help line), the
     refill:<word> clicks change it and the next tick uses it
  S  relog (KeptQuit on a PlayerDisconnectEvent) and a profile switch (settledKey) reset kept + the refill memory; a busy / settling /
     unknown profile = the 2 s tick does nothing (inventory and pool unchanged over 5 ticks)
  0.7.11 REVIEW FIXES (2026-10-02, the review's finding numbers): B also proves the owner rows bags.refill / bags.refillDefault (8: rows,
     template, hand edits, the kit set path); I expects exactly the review-fix members (and compares the kit's row tables with 0.7.10's
     entry by entry); N: the refill waits only while a bench WINDOW is open - a left-over mirror is synced (its consumption booked) and
     dropped, then refilled on the right pool (9) - and a stack with an EMPTY metadata document tops up (13); S: an epoch-only change keeps
     kept (4), KeptQuit writes the quitting player's unsaved pool at once and the shutdown latch stops every move (10); R: no help line,
     hint or log claims that benches use the bags (1), bags.refill off / bags.refillDefault (8)
Not testable without the game (UNVERIFIED): the page on a client, real pickups / block placing, the engine's PlayerDisconnectEvent firing.
Nothing is deployed and nothing under AppData is written. Default scratch folder tools/dev/scratch/sacks0711/run (deleted unless --keep).
Exit code 1 on any failure.
"""
import os, sys, re, shutil, subprocess, zipfile, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyywbtab as WB   # 0.7.10: the Workbench tab tables + harness_checks
VERSION, OLD, ORACLE_V, COOK_V, ACC_V = "0.7.11", "0.7.10", "0.7.7", "0.1.3", "0.5.2"
NEW_SMITH = {"Ingredient_Charcoal": "Smithing"}   # 0.7.10: the only id whose bag changed since the 0.7.7 oracle
PKG = "com.skyy.sacks."
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DEFAULT = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySacks")
COOK_JAR = os.path.join(APPDATA, "Hytale", "UserData", "Mods", "SkyyCooking.jar")
LIVECOOK_DEFAULT = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyCooking", "cooking.properties")
LIVEACC_DEFAULT = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyAccessories")


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "sacks0711", "run")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLDJAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyySacks-%s.jar" % OLD)))
ORACLEJAR = os.path.abspath(arg("--oracle", os.path.join(HERE, "SkyySacks-%s.jar" % ORACLE_V)))
COOKJAR = os.path.abspath(arg("--cook", os.path.join(ROOT, "SkyyCooking", "SkyyCooking-%s.jar" % COOK_V)))
ACCJAR = os.path.abspath(arg("--acc", os.path.join(ROOT, "SkyyAccessories", "SkyyAccessories-%s.jar" % ACC_V)))
J78JAR = os.path.join(HERE, "SkyySacks-0.7.8.jar")   # section J's contrast check (the CraftPage before 0.7.9)
LIVEACC = os.path.abspath(arg("--liveacc", LIVEACC_DEFAULT))
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
    import builtins
    import skyybuild as B
    # checks per section for the report: every "X. ..." summary line records the running ok / fail counts (the last line of a section wins)
    SEC = []
    _print = builtins.print

    def sec_print(*a, **kw):
        if a and isinstance(a[0], str) and re.match(r"^[A-Z]\. ", a[0]):
            SEC.append((a[0][0], OKS[0], len(FAILS)))
        _print(*a, **kw)
    builtins.print = sec_print
    from jpype import JClass, JArray, JObject, JShort, JString, JInt
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, JAR, COOKJAR, ACCJAR, B.JAVASSIST], convertStrings=True)
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()

    # ---------------- A. load + verify
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(JAR).namelist() if n.endswith(".class")]
    names += [n[:-6].replace("/", ".") for n in zipfile.ZipFile(COOKJAR).namelist() if n.endswith(".class")]
    names += ["com.skyy.accessories.WbRank", "com.skyy.accessories.WbTab", "com.skyy.accessories.WbAssetL"]   # W (SkyyAccessories 0.5.2)
    for n in names:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("load " + n + ": " + str(e))
            print("LOAD FAIL", n, e)
    print("A. loaded + verified %d classes (-Xverify:all; SkyySacks 0.7.11 + SkyyCooking 0.1.3 for J + SkyyAccessories 0.5.2 tab classes for W)" % len(names))
    if FAILS:
        return

    # the 0.7.7 SackDefs (oracle) in its own loader (parent = the platform loader: catOf uses java.* only)
    URL = JClass("java.net.URL")
    UCL = JClass("java.net.URLClassLoader")
    File = JClass("java.io.File")
    old_loader = UCL(JArray(URL)([File(ORACLEJAR).toURI().toURL()]), JClass("java.lang.ClassLoader").getPlatformClassLoader())
    OldDefs = JClass(Cls.forName("com.skyy.sacks.SackDefs", True, old_loader))
    check(str(OldDefs.class_.getClassLoader()) != str(loader), "the 0.7.7 oracle comes from its own loader")
    l10 = UCL(JArray(URL)([File(OLDJAR).toURI().toURL()]), JClass("java.lang.ClassLoader").getPlatformClassLoader())
    Defs10 = JClass(Cls.forName("com.skyy.sacks.SackDefs", True, l10))   # 0.7.11: the 0.7.10 rules, to prove no id moved

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
        Pool.KEPT.clear()          # 0.7.11: the kept counts + the refill memory replace the exemption map
        Pool.KEPTKEY.clear()
        Pool.SEENQ.clear()
        Pool.PENDQ.clear()
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
    # 0.7.11: the Unique bag row and the template comment say bags add up (no "best bag carried counts" left)
    hm = str(Rows.HELPS[keys.index("bag.medium")])
    check(hm == "Most of each item a Unique bag (the old Medium) holds. Carried bags of a type add up." and len(hm) <= 100
          and not any("best bag" in str(h) for h in Rows.HELPS), "B: the Unique bag help says bags add up (%d chars): %r" % (len(hm), hm))
    dl = [str(x) for x in Rows.defLines(0)]
    check(any("The bags a player carries add up." in x for x in dl) and not any("best bag" in x for x in dl),
          "B: the config template comment says the carried bags add up")
    check(str(Rows.VERSION) == VERSION, "B: config kit VERSION %s" % Rows.VERSION)
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
        # review fix 8: the owner's stack refill rows through the same kit set path (SkyyMenu Server Setup)
        r3 = fn.apply(OA(["set", "bags.refill", "false", None, "console", "yes", "console"]))
        r4 = fn.apply(OA(["set", "bags.refillDefault", "full", None, "console", "yes", "console"]))
        r5 = fn.apply(OA(["set", "bags.refillDefault", "sideways", None, "console", "yes", "console"]))
        CfgPub.flush()
        kt3 = open(os.path.join(kd, "config.properties"), "rb").read().decode("latin-1").replace("\r\n", "\n")
        check(r3 is not None and str(r3[0]) == "ok" and bool(Cfg.REFILL_ON) is False and "\nbags.refill=false" in kt3
              and r4 is not None and str(r4[0]) == "ok" and str(Cfg.REFILL_DEF) == "full" and "\nbags.refillDefault=full" in kt3
              and r5 is not None and str(r5[0]) != "ok" and "sideways" not in kt3,
              "B review fix 8: kit set bags.refill=false + bags.refillDefault=full: fields + lines written; 'sideways' refused (%s)"
              % (None if r5 is None else str(r5[0])))
        Cfg.MTIME = -1
        Cfg.REFILL_ON, Cfg.REFILL_DEF = True, "hotbar"
        Cfg.reload()
        check(bool(Cfg.REFILL_ON) is False and str(Cfg.REFILL_DEF) == "full", "B review fix 8: SackCfg.reload reads the kit-written refill lines")
        r6 = fn.apply(OA(["set", "bags.refill", "true", None, "console", "yes", "console"]))
        r7 = fn.apply(OA(["set", "bags.refillDefault", "hotbar", None, "console", "yes", "console"]))
        CfgPub.flush()
        check(str(r6[0]) == "ok" and str(r7[0]) == "ok" and bool(Cfg.REFILL_ON) is True and str(Cfg.REFILL_DEF) == "hotbar",
              "B review fix 8: and back (on, hotbar)")
        try:
            CfgPub.shutdown()
        except Exception:
            pass
    else:
        print("note: no live config.properties copy - kit set path skipped")
    Defs.COOKED_FARM = False
    # review fix 8: the two rows (after the cooked food row, Bags group, live), the template lines, the hand-edit reload, the after= hook
    for key_, typ_, def_, lab_ in (("bags.refill", "bool", "true", "Stack refill from bags"),
                                   ("bags.refillDefault", "choice", "hotbar", "Stack refill default")):
        ri_ = keys.index(key_) if key_ in keys else -1
        check(ri_ > ri and str(Rows.TYPES[ri_]) == typ_ and str(Rows.DEFS[ri_]) == def_ and str(Rows.LABELS[ri_]) == lab_
              and str(Rows.CATS[ri_]) == "bags" and str(Rows.FLAGS[ri_]).split(",") == ["live"] and 0 < len(str(Rows.HELPS[ri_])) <= 100,
              "B review fix 8: row %s (%s, default %s, live, Bags group, after the cooked food row)" % (key_, typ_, def_))
    check(keys.index("bags.refillDefault") == keys.index("bags.refill") + 1 == ri + 2, "B review fix 8: the two rows follow the cooked food row")
    check(str(Rows.OPTS[keys.index("bags.refillDefault")]) == "hotbar|Hotbar only,full|Full inventory,off|Off",
          "B review fix 8: bags.refillDefault offers hotbar / full / off")
    check("#bags.refill=true" in tpl and "#bags.refillDefault=hotbar" in tpl and tpl.index("#bags.cookedFood=false") < tpl.index("#bags.refill=true")
          and "\nbags.refill" not in tpl, "B review fix 8: the missing-file template carries the two commented refill lines after the cooked food line")
    Cfg.FILE = Paths.get(cf)
    for val_, on_, d_raw, d_ in (("false", False, "full", "full"), ("off", False, "OFF", "off"), ("true", True, "hotbar", "hotbar"),
                                 ("maybe", True, "sideways", "hotbar"), ("on", True, "", "hotbar")):
        open(cf, "w", encoding="utf8").write(tpl + "bags.refill=%s\nbags.refillDefault=%s\n" % (val_, d_raw))
        Cfg.MTIME = -1
        Cfg.reload()
        check(bool(Cfg.REFILL_ON) is on_ and str(Cfg.REFILL_DEF) == d_,
              "B review fix 8: file bags.refill=%s bags.refillDefault=%r -> %s / %s" % (val_, d_raw, on_, d_))
    open(cf, "w", encoding="utf8").write(tpl)
    Cfg.MTIME = -1
    Cfg.reload()
    check(bool(Cfg.REFILL_ON) is True and str(Cfg.REFILL_DEF) == "hotbar", "B review fix 8: the template alone -> on / hotbar")
    try:
        Cfg.refillChanged("bags.refill")
        OKS[0] += 1
    except Exception as e:
        check(False, "after= hook refillChanged threw %s" % e)
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
                if i in NEW_SMITH:
                    if old is not None:
                        bad.append("%s was already in a bag in 0.7.7 (%s)" % (i, old))
                    old = NEW_SMITH[i]   # 0.7.10
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
    check(not bad, "classification: %d ids x 2 switch states x 3 prefix states agree with 0.7.7 + the rule (+ charcoal -> Smithing)%s"
          % (len(ids), "" if not bad else " - " + "; ".join(bad[:8])))
    # 0.7.11: against the 0.7.10 rules directly - no id changed bag (homeOf and catOf, both switch states)
    for prefix in (None, "Skyy_Cook_Food_"):
        if prefix is None:
            bridge.remove("cook:prefix")
        else:
            bridge.put("cook:prefix", prefix)
        for sw in (False, True):
            Defs.COOKED_FARM = sw
            Defs10.COOKED_FARM = sw
            moved10 = [(i, sget(Defs10.homeOf(i)), sget(Defs.homeOf(i))) for i in ids if sget(Defs10.homeOf(i)) != sget(Defs.homeOf(i))
                       or sget(Defs10.catOf(i)) != sget(Defs.catOf(i))]
            check(not moved10, "C: vs 0.7.10 homeOf / catOf (prefix %s, switch %s): no id moved: %s" % (prefix, sw, moved10[:6]))
    Defs.COOKED_FARM = False
    Defs10.COOKED_FARM = False
    bridge.remove("cook:prefix")
    check("Ingredient_Charcoal" in vanilla, "C: Ingredient_Charcoal is a vanilla item id")
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
            Pool.clearKeptCat(k2, "Farming")      # 0.7.11: the button clears that tab's kept counts (was: every exemption)
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
    # 0.7.11: everything taken out is KEPT - the automatic sweep leaves it in the inventory (no 10-minute timer any more)
    check(all(int(Pool.kept(k, i)) == q for i, q in COOKED_IN + RAW_IN), "E: every item taken out is kept (kept = what was taken)")
    Sweep.sweep(p, k, None, False)
    check(not pool_counts(k) and totals(p, k) == b0, "E: the next automatic sweep leaves every taken-out item in the inventory (kept)")
    Pool.clearKeptCat(k, "Farming")    # the Deposit all button on the Farming tab
    Sweep.sweep(p, k, "Farming", True)
    pc = pool_counts(k)
    check(not any(i in pc for i, _q in COOKED_IN) and all(pc.get(i) == q for i, q in RAW_IN) and totals(p, k) == b0,
          "E: Deposit all (kept cleared) puts the raw produce back but never the cooked food")
    print("E. stored cooked food: withdraw / Pick up all / kept / Deposit all checked")

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

    # ---------------- I. class byte-compare 0.7.10 vs 0.7.11 (+ assets)
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

    def ldcs(code):
        return sorted(m.group(1) for m in re.finditer(r'^ldc(?:_w)? "(.*)"$', code, re.M))

    def norm(code):   # branch targets are absolute offsets: drop them so an inserted block does not shift every later line
        return [re.sub(r"^((?:if\w*|goto\w*|jsr\w*)) -?\d+$", r"\1", l) for l in code.split("\n")]

    def subseq(a, b):
        it = iter(b)
        return all(any(x == y for y in it) for x in a)

    def canon(code):  # + ldc_w -> ldc: new constants earlier in a class push later ones past index 255 (same instruction, wider index)
        return None if code is None else [re.sub(r"^ldc_w ", "ldc ", l) for l in norm(code)]

    z10, z11 = zipfile.ZipFile(OLDJAR), zipfile.ZipFile(JAR)
    c10 = dict((n, z10.read(n)) for n in z10.namelist() if n.endswith(".class"))
    c11 = dict((n, z11.read(n)) for n in z11.namelist() if n.endswith(".class"))
    NEWC = ["com/skyy/sacks/%s.class" % c for c in ("RefillPref", "KeptQuit")]
    check(sorted(c11) == sorted(list(c10) + NEWC), "I: the 0.7.10 classes + RefillPref / KeptQuit (%d)" % len(c11))
    same = sorted(n for n in c10 if c11.get(n) == c10[n])
    diff = sorted(n for n in c10 if n in c11 and c10[n] != c11[n])
    SW = "Lcom/hypixel/hytale/server/core/entity/entities/Player;"
    IV = "Lcom/hypixel/hytale/server/core/inventory/Inventory;"
    HM = "Ljava/util/HashMap;"
    UCBD = "Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;"
    UEBD = "Lcom/hypixel/hytale/server/core/ui/builder/UIEventBuilder;"
    HDE = "m handleDataEvent(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;Ljava/lang/String;)V"
    SKEY = "m settledKey(Ljava/util/UUID;)Ljava/lang/String;"
    WDR = "m withdraw(%sLjava/lang/String;Ljava/lang/String;I)I" % SW
    NBG = "m buildNoBag(%s%sLjava/lang/String;%sLjava/util/UUID;)V" % (UCBD, SW, HM)
    EXPECT = {
        "SackPool": {"f EXEMPT", "f KEPT", "f KEPTKEY", "f SEENQ", "f PENDQ", "f CLOSED", "m <clinit>()V",
                     "m exempt(Ljava/lang/String;Ljava/lang/String;J)V", "m isExempt(Ljava/lang/String;Ljava/lang/String;)Z",
                     "m clearExempt(Ljava/lang/String;)V", "m keptMap(Ljava/lang/String;Z)Ljava/util/concurrent/ConcurrentHashMap;",
                     "m kept(Ljava/lang/String;Ljava/lang/String;)J", "m keep(Ljava/lang/String;Ljava/lang/String;J)V",
                     "m raiseKept(Ljava/lang/String;Ljava/lang/String;J)V",
                     "m clearKeptCat(Ljava/lang/String;Ljava/lang/String;)I", "m forgetSeen(Ljava/util/UUID;)V",
                     "m forgetKept(Ljava/util/UUID;)V", "m dropKept(Ljava/util/UUID;Ljava/lang/String;Ljava/lang/String;)V", SKEY},
        "SweepTask": {"m offer(%s%sLjava/lang/String;II)V" % (HM, HM), "m offerId(Ljava/lang/String;%s%s)V" % (HM, HM),
                      "m addBag(%s%s%sLjava/lang/String;III)V" % (HM, HM, HM), "m bagOf(Ljava/lang/String;I%s%s%s)V" % (HM, HM, HM),
                      "m scanN(%s%s%s%s)V" % (IV, HM, HM, HM), "m scan(%s%s%s)V" % (IV, HM, HM), "m carried(%s)%s" % (IV, HM),
                      "m keptDrop(%sLjava/lang/String;)I" % HM,
                      "m countIn(Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;Ljava/lang/String;)I",
                      "m sweep(%sLjava/lang/String;Ljava/lang/String;Z%s)I" % (SW, HM),
                      "m sweep(%sLjava/lang/String;Ljava/lang/String;Z)I" % SW,
                      "m sweepLeft(%sLjava/lang/String;%s)Ljava/util/HashSet;" % (IV, HM), WDR,
                      "m refill(%sLjava/lang/String;ILjava/util/Set;Ljava/util/Set;%s)I" % (SW, HM),
                      "m benchFed(%sLjava/lang/String;)Z" % SW,      # review fix 9
                      "m items(%sLjava/lang/String;Ljava/util/UUID;)[I" % SW, "m run()V"},
        "SacksPage": {"m bagCount([I)I", "m bagsLine([I)Ljava/lang/String;", "m refillRow(%s%sI)V" % (UCBD, UEBD),
                      "m render(%s%s%sLjava/lang/String;%s%s)V" % (UCBD, UEBD, SW, HM, HM), HDE,
                      NBG},                                            # review fix 1: the no-bag hint
        "SackSaver": {"m run()V"},
        # review fix 8: the owner switches (2 bound fields + their initial values in <clinit>, the reload lines, the after= hook)
        "SackCfg": {"m reload()V", "f REFILL_ON", "f REFILL_DEF", "m <clinit>()V", "m refillChanged(Ljava/lang/String;)V",
                    "m refillKeys(Ljava/util/Properties;Z)V"},
        "CfgFile": None,      # review fix 8: the kit sizes its per-row arrays by the row count (11 -> 13 rows; checked below)
        "SkyySacksPlugin": {"m setup()V", "m shutdown()V"},
        "CfgRows": None,      # the kit's tables: VERSION, the Unique bag help, the template lines (checked below)
        "CfgFn": None,
    }
    OLDH, NEWH = "The best bag carried counts.", "Carried bags of a type add up."
    OLDT = "for every bag type (the best bag a player carries counts)."
    NEWT = "for every bag type. The bags a player carries add up."
    report = []
    for n in diff:
        cname = n[:-6].replace("/", ".")
        short = cname.rsplit(".", 1)[1]
        m10, m11 = members(OLDJAR, cname), members(JAR, cname)
        # a member whose code is the same once branch offsets and ldc / ldc_w are normalised only moved in the constant pool
        changed = sorted(kk for kk in set(m10) | set(m11) if canon(m10.get(kk)) != canon(m11.get(kk)))
        cpool = sorted(kk for kk in set(m10) & set(m11) if m10.get(kk) != m11.get(kk) and kk not in changed)
        report.append("%s: %s%s" % (short, ", ".join(c.split("(")[0] for c in changed) or "(constant pool only)",
                                    (" | constant pool only: " + ", ".join(c.split("(")[0] for c in cpool)) if cpool else ""))
        allowed = EXPECT.get(short, "missing")
        if short == "CfgFile":
            # review fix 8: the kit's per-row arrays are sized by the row count - 11 rows in 0.7.10, 13 now; nothing else differs
            c10_, c11_ = canon(m10.get("m <clinit>()V")), canon(m11.get("m <clinit>()V"))
            pairs = [] if c10_ is None or c11_ is None or len(c10_) != len(c11_) else [(a_, b_) for a_, b_ in zip(c10_, c11_) if a_ != b_]
            check(changed == ["m <clinit>()V"] and pairs and all(pq_ == ("bipush 11", "bipush 13") for pq_ in pairs),
                  "I: CfgFile differs only in its per-row array sizes (11 -> 13 rows): %s %s" % (changed, pairs[:3]))
            continue
        if short == "CfgRows":
            # review fix 8: the kit's row tables = 0.7.10's + the two refill rows right after bags.cookedFood (+ the bags-add-up help and
            # template text, VERSION), compared entry by entry with the 0.7.10 class loaded on its own; besides the table initialiser only
            # the VERSION constant and header() (which returns it) differ
            check(set(changed) <= {"m <clinit>()V", "f VERSION", "m header()[Ljava/lang/Object;"}
                  and all(canon(m10[c].replace("0.7.10", "0.7.11")) == canon(m11[c]) for c in changed if c.startswith("m header")),
                  "I: CfgRows: only the table initialiser, VERSION and header() (VERSION only) differ: %s" % changed)
            l10r = UCL(JArray(URL)([File(OLDJAR).toURI().toURL(), File(B.SERVER_JAR).toURI().toURL()]),
                       JClass("java.lang.ClassLoader").getPlatformClassLoader())
            R10 = Cls.forName(PKG + "CfgRows", True, l10r)

            def arr(cls_, name_):
                v_ = cls_.getField(name_).get(None)
                return None if v_ is None else [str(x) for x in v_]
            k10 = arr(R10, "KEYS")
            at_ = k10.index("bags.cookedFood") + 1
            bad_ = []
            for name_ in ("KEYS", "LABELS", "CATS", "TYPES", "DEFS", "MINS", "MAXS", "OPTS", "UNITS", "FLAGS", "HELPS", "BK", "BF", "BFT",
                          "BCONF", "BENT", "BSC", "BCLS", "BNAME", "BFK", "BCK", "BAFTER", "BCHECK", "BSEP", "VTYPES"):
                a10, a11 = arr(R10, name_), arr(Rows.class_, name_)
                if name_ == "HELPS" and a10 is not None:
                    a10 = [x.replace(OLDH, NEWH) for x in a10]
                if a10 is None or a11 is None or len(a11) != len(a10) + 2 or a11[:at_] != a10[:at_] or a11[at_ + 2:] != a10[at_:]:
                    bad_.append(name_)
            k11 = arr(Rows.class_, "KEYS")
            check(not bad_ and k11[at_:at_ + 2] == ["bags.refill", "bags.refillDefault"],
                  "I: CfgRows tables = 0.7.10's + bags.refill / bags.refillDefault after the cooked food row, entry by entry (differ: %s)" % bad_)
            d10 = [x.replace(OLDT, NEWT) for x in arr(R10, "DL0")]
            d11 = arr(Rows.class_, "DL0")
            ins = d10.index("#bags.cookedFood=false") + 1
            check(d11[:ins] == d10[:ins] and d11[ins + 4:] == d10[ins:] and d11[ins + 1] == "#bags.refill=true"
                  and d11[ins + 3] == "#bags.refillDefault=hotbar" and len(d11) == len(d10) + 4,
                  "I: CfgRows template lines = 0.7.10's (bags add up) + the 4 refill lines after #bags.cookedFood=false")
            check(str(R10.getField("VERSION").get(None)) == OLD and str(Rows.VERSION) == VERSION, "I: CfgRows VERSION 0.7.10 -> 0.7.11")
            continue
        if allowed is None:
            # the config kit inlines VERSION and holds the help / template text: every changed member differs only in those strings
            okk = all(m10.get(c) is not None and m11.get(c) is not None
                      and canon(m10[c].replace("0.7.10", "0.7.11").replace(OLDH, NEWH).replace(OLDT, NEWT)) == canon(m11[c]) for c in changed)
            check(okk, "I: config kit class %s differs only in VERSION 0.7.10 -> 0.7.11 + the bags-add-up help / template text: %s"
                  % (short, changed))
            continue
        extra = sorted(set(changed) - (allowed if allowed != "missing" else set()))
        check(allowed != "missing" and not extra, "I: class %s differs only in the expected members (unexpected: %s)" % (short, extra))
        if short == "SackCfg":
            r10, r11 = m10["m reload()V"], m11["m reload()V"]
            # review fix 8: 0.7.10's reload (template comment: bags add up) stays an in-order subsequence; the only new strings are the
            # two template lines pairs and the refill keys / words / warning / log texts
            new_r = [l for l in ldcs(r11) if l not in ldcs(r10.replace(OLDT, NEWT))]
            ok_new = all(any(w in l for w in ("refill", "Refill", "hotbar", "Hotbar")) or l in (")", "full", "off") for l in new_r)
            check(subseq(canon(r10.replace(OLDT, NEWT)), canon(r11)) and OLDT in r10 and ok_new
                  and "#bags.refill=true" in r11 and "#bags.refillDefault=hotbar" in r11 and "SackCfg.refillKeys" in r11,
                  "I: SackCfg.reload = 0.7.10's (template comment: bags add up) + the refill template lines and keys; new strings %s"
                  % [x[:40] for x in new_r if "refill" not in x.lower()])
        if short == "SackSaver":
            s10, s11 = m10["m run()V"], m11["m run()V"]
            check(subseq(canon(s10), canon(s11)) and "RefillPref.save" in s11 and len(norm(s11)) - len(norm(s10)) <= 8,
                  "I: SackSaver.run = 0.7.10's + RefillPref.save()")
        if short == "SkyySacksPlugin":
            s10, s11 = m10["m setup()V"], m11["m setup()V"]
            new_l = [l for l in ldcs(s11) if l not in ldcs(s10)]
            gone_l = [l for l in ldcs(s10) if l not in ldcs(s11)]
            check(all(l.startswith("[SkyySacks] 0.7.11 ready") or l == "refill.properties" for l in new_l)
                  and all(l.startswith("[SkyySacks] 0.7.10 ready") for l in gone_l) and "KeptQuit" in s11 and "registerGlobal" in s11
                  and "RefillPref.load" in s11 and "PlayerDisconnectEvent" in s11,
                  "I: SkyySacksPlugin.setup = 0.7.10's + the refill file / load + the quit listener; new strings %s" % [x[:60] for x in new_l])
            # each try / catch stores its Throwable in a new local slot: the catch after the inserted one moves to the next slot
            slot = lambda c_: [re.sub(r"^astore(?:_\d| \d+)$", "astore", l) for l in canon(c_)]
            check(subseq(slot(m10["m shutdown()V"]), slot(m11["m shutdown()V"])) and "RefillPref.save" in m11["m shutdown()V"],
                  "I: SkyySacksPlugin.shutdown = 0.7.10's + RefillPref.save()")
        if short == "SweepTask":
            for keep_m in ("m caps(%s)%s" % (IV, HM), "m best(%s)%s" % (IV, HM), "m legendCount(%s)I" % IV,
                           "m restamp(%s)I" % IV, "m cookedHeld(%s)I" % IV):
                check(m10.get(keep_m) is not None and canon(m10.get(keep_m)) == canon(m11.get(keep_m)), "I: SweepTask.%s unchanged" % keep_m.split("(")[0][2:])
            check("SackPool.exempt" in m10[WDR] and "SackPool.keep" in m11[WDR] and "SackPool.raiseKept" in m11[WDR] and "SackPool.exempt" not in m11[WDR]
                  and "600000" in m10[WDR] and "600000" not in m11[WDR],
                  "I: SweepTask.withdraw: the 10-minute exempt -> keep(what really left the pool)")
        if short == "SackPool":
            check("dropKept" in m11[SKEY] and "SackPool.CLOSED" in m11[SKEY] and subseq(canon(m10[SKEY]), canon(m11[SKEY])),
                  "I: SackPool.settledKey = 0.7.10's + the shutdown latch (review fix 10) + dropKept on a key change (review fix 4)")
        if short == "SacksPage":
            check("clearExempt" in m10[HDE] and "clearExempt" not in m11[HDE] and "clearKeptCat" in m11[HDE] and "forgetSeen" in m11[HDE]
                  and "RefillPref.set" in m11[HDE], "I: SacksPage.handleDataEvent: Deposit all clears the tab's kept counts; refill:<word> clicks")
    check(sorted(r.split(":")[0] for r in report) == sorted(EXPECT), "I: exactly %s changed: %s" % (", ".join(sorted(EXPECT)), diff))
    print("I. classes byte-identical: %d of %d (0.7.10); new: RefillPref, KeptQuit" % (len(same), len(c10)))
    print("   classes that differ: %d" % len(diff))
    for r in report:
        print("     " + r)
    a10 = dict((n, z10.read(n)) for n in z10.namelist() if not n.endswith(".class"))
    a11 = dict((n, z11.read(n)) for n in z11.namelist() if not n.endswith(".class"))
    adiff = sorted(n for n in set(a10) | set(a11) if a10.get(n) != a11.get(n))
    check(adiff == ["manifest.json"], "I: assets: only the manifest differs (items, lang, qualities, the tab icon unchanged): %s" % adiff)
    m10_, m11_ = json.loads(a10["manifest.json"]), json.loads(a11["manifest.json"])
    check(m10_["Version"] == OLD and m11_["Version"] == VERSION and m11_["Name"] == "0.7.11 SkyySacks"
          and dict(m10_, Version=0, Name=0) == dict(m11_, Version=0, Name=0), "I: manifest: only Name / Version -> 0.7.11")
    print("   assets that differ: manifest.json only (%d asset files)" % len(a11))

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
        l78 = UCL(JArray(URL)([File(J78JAR).toURI().toURL(), File(B.SERVER_JAR).toURI().toURL()]), JClass("java.lang.ClassLoader").getPlatformClassLoader())
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

    # ---------------- K. charcoal goes in the Smithing bag (0.7.10)
    CH = "Ingredient_Charcoal"
    dk = os.path.join(SCRATCH, "pools-k")
    check(sget(Defs.homeOf(CH)) == "Smithing" and sget(Defs.catOf(CH)) == "Smithing" and sget(Defs10.homeOf(CH)) == "Smithing",
          "K: charcoal: homeOf / catOf Smithing (as in 0.7.10)")
    for bag in ("Skyy_Sack_Smithing_Small", "Skyy_Sack_Smithing_Large", "Skyy_Sack_Omni"):
        fresh_pools(dk)
        k = "k-" + bag
        p = player(storage=[(CH, 8), ("Ingredient_Stick", 5), ("Ore_Copper", 3), ("Ingredient_Bar_Iron", 2)], hotbar=[(bag, 1), (CH, 4)],
                   backpack=[(CH, 2)])
        before = totals(p, k)
        moved = int(Sweep.sweep(p, k, None, False))
        inv, pc = inv_counts(p), pool_counts(k)
        omni = bag == "Skyy_Sack_Omni"
        check(totals(p, k) == before, "K auto-pickup (%s): every item counted" % bag)
        check(pc.get(CH) == 8 and inv.get(CH) == 6 and pc.get("Ingredient_Bar_Iron") == 2 and inv.get(bag) == 1,
              "K auto-pickup (%s): the 8 charcoal in the main inventory pooled with the iron bars; the 4 in the hotbar + 2 in the backpack stay "
              "(the 2 s sweep reads the main inventory only - every bag item, by design)" % bag)
        check((pc.get("Ingredient_Stick") == 5 and pc.get("Ore_Copper") == 3) if omni else (inv.get("Ingredient_Stick") == 5 and inv.get("Ore_Copper") == 3),
              "K auto-pickup (%s): sticks / ore %s" % (bag, "pooled too (Omni = every bag)" if omni else "stay (not Smithing items)"))
        check(moved == (8 + 2 + (8 if omni else 0)), "K auto-pickup (%s): moved %d" % (bag, moved))
        Pool.clearKeptCat(k, "Smithing")
        dep = int(Sweep.sweep(p, k, "Smithing", True))
        check(dep == 6 and pool_counts(k).get(CH) == 14 and CH not in inv_counts(p) and totals(p, k) == before,
              "K Deposit all on the Smithing tab (%s): the hotbar + backpack charcoal follow (6, counted)" % bag)
        check(int(Pool.catTotal(k, "Smithing")) == 16, "K catTotal(Smithing) counts the charcoal (%s)" % bag)
    for bags, label in (((), "no bag"), ((("Skyy_Sack_Foraging_Small", 1),), "a Foraging bag only"), ((("Skyy_Sack_Mining_Large", 1),), "a Mining bag only"),
                        ((("Skyy_Sack_Combat_Rare", 1), ("Skyy_Sack_Farming_Medium", 1)), "Combat + Farming bags")):
        fresh_pools(dk)
        k = "k-none-" + label
        p = player(storage=[(CH, 8)], hotbar=list(bags) + [(CH, 4)])
        Sweep.sweep(p, k, None, False)
        check(inv_counts(p).get(CH) == 12 and CH not in pool_counts(k), "K without a Smithing bag (%s): the 12 charcoal stay in the inventory" % label)
    # Deposit all (the button: exemptions cleared, every container, only that tab's category)
    fresh_pools(dk)
    k = "k-dep"
    p = player(storage=[(CH, 6), ("Ingredient_Stick", 3)], hotbar=[("Skyy_Sack_Omni", 1)], backpack=[(CH, 1)])
    b0 = totals(p, k)
    Pool.clearKeptCat(k, "Foraging")
    d1 = int(Sweep.sweep(p, k, "Foraging", True))
    check(d1 == 3 and inv_counts(p).get(CH) == 7 and pool_counts(k).get("Ingredient_Stick") == 3, "K Deposit all on the Foraging tab: sticks in, charcoal stays")
    Pool.clearKeptCat(k, "Smithing")
    d2 = int(Sweep.sweep(p, k, "Smithing", True))
    check(d2 == 7 and CH not in inv_counts(p) and pool_counts(k).get(CH) == 7 and totals(p, k) == b0, "K Deposit all on the Smithing tab: takes all 7 charcoal (counted)")
    # taking it out
    nobag = player()
    check(int(Sweep.withdraw(nobag, k, CH, 64)) == 0 and pool_counts(k).get(CH) == 7, "K no bag on you: nothing taken out")
    pw = player(hotbar=[("Skyy_Sack_Smithing_Medium", 1)])
    bw = totals(pw, k)
    g1 = int(Sweep.withdraw(pw, k, CH, 1))
    g2 = int(Sweep.withdraw(pw, k, CH, 64))
    check(g1 == 1 and g2 == 6 and CH not in pool_counts(k) and inv_counts(pw).get(CH) == 7 and totals(pw, k) == bw,
          "K withdraw with a Smithing bag: right click 1, left click the other 6 (counted)")
    Pool.add(k, CH, 9)
    Pool.save(k)
    Pool.POOLS.clear()
    check(pool_counts(k).get(CH) == 9, "K save + reload keeps the stored charcoal (9)")
    # report: every Assets.zip item with a FuelQuality and the bag it goes to (only charcoal moved: harness C)
    with zipfile.ZipFile(za) as z:
        nodes = {}
        for n in z.namelist():
            if n.startswith("Server/Item/Items/") and n.endswith(".json"):
                try:
                    nodes[os.path.basename(n)[:-5]] = json.loads(z.read(n).decode("utf-8-sig"))
                except Exception:
                    pass

    def fq(i, depth=0):
        d = nodes.get(i)
        if d is None or depth > 12:
            return None
        if "FuelQuality" in d:
            return d["FuelQuality"]
        return fq(d.get("Parent"), depth + 1) if d.get("Parent") else None
    fuels = sorted(i for i in nodes if (fq(i) or 0) > 0)
    groups = {}
    for i in fuels:
        groups.setdefault(sget(Defs.homeOf(i)) or "no bag", []).append(i)
    check(CH in groups.get("Smithing", []), "K report: charcoal is the Smithing bag's fuel")
    print("K. charcoal: Smithing bag (Normal / Legendary) + Omni take it, no Smithing bag = stays, Deposit all Smithing only, withdraw, save")
    for g in sorted(groups):
        wood = [i for i in groups[g] if i.startswith("Wood_")]
        rest_ = [("%s (FQ %s)" % (i, fq(i))) for i in groups[g] if not i.startswith("Wood_")]
        print("   fuel items -> %-9s %s%s" % (g + ":", ", ".join(rest_), (" + %d Wood_ logs / planks" % len(wood)) if wood else ""))

    # ---------------- W. the Workbench tab (tools/skyywbtab.py, both mods' classes on the classpath)
    for l in WB.harness_checks(check, B.SERVER_JAR):
        print(l)

    # ---------------- L. both mods' start sequences alone / together on scratch copies of the live data: no file churn
    live_s, live_a = os.path.join(SCRATCH, "live"), os.path.join(SCRATCH, "liveacc")
    AJ = lambda n: JClass("com.skyy.accessories." + n)

    def snap(d):
        out_ = {}
        for root, _ds, fs in os.walk(d):
            for f in fs:
                pth = os.path.join(root, f)
                out_[os.path.relpath(pth, d)] = open(pth, "rb").read()
        return out_

    def start_sacks(d):
        Cfg.FILE = Paths.get(os.path.join(d, "config.properties"))
        Cfg.MTIME = -1
        Cfg.reload()
        N = J("SackNotice")
        N.SEEN.clear()
        N.BROKEN = False
        N.DIRTY = False
        N.FILE = Paths.get(os.path.join(d, "notices.properties"))
        N.load()
        # 0.7.11: setup() loads the stack refill choices too (refill.properties; no file until a player changes the setting)
        RF = J("RefillPref")
        RF.MODES.clear()
        RF.BROKEN = False
        RF.DIRTY = False
        RF.FILE = Paths.get(os.path.join(d, "refill.properties"))
        RF.load()
        pd = os.path.join(d, "pools")
        fresh_pools(pd)
        n = 0
        for f in sorted(os.listdir(pd)) if os.path.isdir(pd) else []:
            if f.endswith(".properties"):
                Pool.pool(f[:-11])
                n += 1
        J("WbTab").start()
        # the SackSaver's saves (they write only what changed: nothing, on a start)
        Pool.flushDirty()
        N.save()
        RF.save()
        return "%d pools, %d refill choices" % (n, int(RF.MODES.size()))

    def start_acc(d):
        AJ("AccStore").DIR = Paths.get(os.path.join(d, "bags"))
        AJ("AccCfg").FILE = Paths.get(os.path.join(d, "config.properties"))
        m51 = str(AJ("AccCfg").migrate051())
        cs = str(AJ("AccCfg").load(True))
        AJ("AccNotice").FILE = Paths.get(os.path.join(d, "notices.properties"))
        AJ("AccNotice").load()
        AJ("WbTab").start()
        return (m51 + " " + cs).strip()[:80]

    if not os.path.isdir(live_s):
        print("note: no live SkyySacks data copy - L skipped")
    else:
        has_acc = os.path.isdir(live_a)
        runs = [["sacks"]] + ([["acc"], ["sacks", "acc"], ["acc", "sacks"]] if has_acc else [])
        for ri, order in enumerate(runs):
            base = os.path.join(SCRATCH, "l-%d" % ri)
            ds, da = os.path.join(base, "sacks"), os.path.join(base, "acc")
            shutil.copytree(live_s, ds)
            if has_acc:
                shutil.copytree(live_a, da)
            b_s, b_a = snap(ds), (snap(da) if has_acc else {})
            notes = []
            for rnd in (1, 2):
                for m in order:
                    notes.append(start_sacks(ds) if m == "sacks" else start_acc(da))
            a_s, a_a = snap(ds), (snap(da) if has_acc else {})
            ch_s = sorted(k_ for k_ in set(b_s) | set(a_s) if b_s.get(k_) != a_s.get(k_))
            ch_a = sorted(k_ for k_ in set(b_a) | set(a_a) if b_a.get(k_) != a_a.get(k_))
            check(not ch_s and not ch_a, "L start %s (twice) on copies of the live data: no file changed (%d + %d files) %s %s"
                  % ("+".join(order), len(b_s), len(b_a), ch_s[:4], ch_a[:4]))
            print("L. start %-11s twice: SkyySacks %d files, SkyyAccessories %d files unchanged (%s)" % ("+".join(order), len(b_s), len(b_a), "; ".join(sorted(set(notes)))[:150]))


    # ============================================================================ 0.7.11 sections (Skyy 2026-10-02, Q&A rounds 2-4)
    RF, KQ = J("RefillPref"), J("KeptQuit")
    PDEv = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent")
    ItemC = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    BsonDocument, BsonString = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonString")
    LongJ = JClass("java.lang.Long")
    ms_f = jfield(ItemC.class_, "maxStack")
    OLD_MS = int(ms_f.getInt(ItemC.UNKNOWN))
    ms_f.setInt(ItemC.UNKNOWN, 64)      # a bare JVM has only Item.UNKNOWN (max stack 100): 64 = the game's usual block / material stack
    MAXS = 64
    Defs.CAP_SMALL, Defs.CAP_MEDIUM, Defs.CAP_RARE, Defs.CAP_LARGE, Defs.CAP_OMNI = 640, 2240, 6720, 20160, 100000
    Defs.COOKED_FARM = False
    RF.MODES.clear()
    RF.BROKEN = False
    RF.DIRTY = False
    RF.FILE = None
    # review fixes 9 / 10 run the SackSaver (SackPool.saveSoon) from inside these sections: its SackCfg.reload must not re-read a config
    # file of an earlier section halfway through a scenario (R points SackCfg.FILE at its own file again)
    Cfg.FILE = None
    Cfg.REFILL_ON, Cfg.REFILL_DEF = True, "hotbar"
    for k_ in list(bridge.keySet()):
        if str(k_).startswith("profile:"):
            bridge.remove(k_)
    ST, ORE, LOG, BONE = "Rock_Stone", "Ore_Copper", "Wood_Oak_Trunk", "Ingredient_Bone_Fragment"
    MIN_S, MIN_L, FOR_S, COM_S, OMNI = "Skyy_Sack_Mining_Small", "Skyy_Sack_Mining_Large", "Skyy_Sack_Foraging_Small", "Skyy_Sack_Combat_Small", "Skyy_Sack_Omni"

    def mkuuid(n):
        return UUID.fromString("00000000-0000-0000-0000-%012x" % n)

    def mkpr(u):
        r_ = us.allocateInstance(PR.class_)
        jfield(PR.class_, "uuid").set(r_, u)
        return r_

    def conts(p):
        inv = p.getInventory()
        return inv.getHotbar(), inv.getStorage(), inv.getBackpack()

    def put(cont, i, iid, q, meta=False):
        st_ = IS(iid, q, BsonDocument().append("skyy", BsonString("test"))) if meta else IS(iid, q)
        cont.setItemStackForSlot(JShort(i), st_)

    def at(cont, i):
        it_ = cont.getItemStack(JShort(i))
        return None if it_ is None or it_.isEmpty() else (str(it_.getItemId()), int(it_.getQuantity()))

    def use(cont, i, n):        # the player places / eats / crafts n items from that slot
        before_ = at(cont, i)
        tx_ = cont.removeItemStackFromSlot(JShort(i), JInt(n))
        after_ = at(cont, i)
        assert before_ is not None and (after_ is None and before_[1] == n or after_ is not None and after_[1] == before_[1] - n), (before_, after_, n)

    def tick(p, k, u):
        r_ = Sweep.items(p, k, u)
        return int(r_[0]), int(r_[1])

    def tick_gate(p, u):        # exactly SweepTask.run(): the settled key or nothing
        k_ = Pool.settledKey(u)
        return None if k_ is None else tick(p, str(k_), u)

    def total_of(p, k, iid):
        return inv_counts(p).get(iid, 0) + pool_counts(k).get(iid, 0)

    # ---------------- M. KEPT counts (R3: "auto-collect LEAVES ALONE THE AMOUNT YOU TOOK ... placing blocks lowers it; anything above it,
    # e.g. newly mined, still goes in; no timer; Deposit all resets")
    UM = mkuuid(0x11)
    RF.set(UM, 2)                          # M tests the kept counts alone: stack refill OFF for this player (N tests the refill)
    fresh_pools(os.path.join(SCRATCH, "pools-m"))
    k = "m-kept"
    Pool.add(k, ST, 2000)
    p = player(hotbar=[(MIN_L, 1)])
    hot, sto, bp = conts(p)
    b0 = totals(p, k)
    got = sum(int(Sweep.withdraw(p, k, ST, 64)) for _ in range(8))
    check(got == 512 and int(Pool.kept(k, ST)) == 512 and inv_counts(p).get(ST) == 512 and pool_counts(k).get(ST) == 1488 and totals(p, k) == b0,
          "M: 8 left clicks take 512 stone out - kept 512, counted")
    res = [tick(p, k, UM) for _ in range(3)]
    check(res == [(0, 0)] * 3 and inv_counts(p).get(ST) == 512 and pool_counts(k).get(ST) == 1488 and int(Pool.kept(k, ST)) == 512,
          "M: the 2 s sweep leaves the 512 taken-out stone alone (3 ticks: %s)" % res)
    # Skyy's case: only one stack fits the hotbar - 64 go to the hotbar by hand, 448 stay in the main inventory
    si = [i for i in range(36) if at(sto, i) == (ST, 64)][0]
    use(sto, si, 64)
    put(hot, 1, ST, 64)
    check(tick(p, k, UM) == (0, 0) and inv_counts(p).get(ST) == 512 and int(Pool.kept(k, ST)) == 512 and totals(p, k) == b0,
          "M: a stack moved by hand to the hotbar (64 + 448) changes nothing")
    sto.addItemStack(IS(ST, 10))          # mined: 10 new stone in the main inventory
    b1 = totals(p, k)
    r1 = tick(p, k, UM)
    check(r1 == (10, 0) and inv_counts(p).get(ST) == 512 and pool_counts(k).get(ST) == 1498 and totals(p, k) == b1,
          "M: mining +10 -> the sweep takes exactly the 10 above kept (%s)" % (r1,))
    put(hot, 2, ST, 10)                    # mined into a free hotbar slot (Hytale's default pickup location)
    b2 = totals(p, k)
    r2 = tick(p, k, UM)
    check(r2 == (10, 0) and inv_counts(p).get(ST) == 512 and at(hot, 2) == (ST, 10) and totals(p, k) == b2,
          "M: +10 landing in the hotbar -> 10 leave the main inventory (the hotbar is never swept; kept counts all you carry): %s" % (r2,))
    use(hot, 1, 30)                        # 30 blocks placed
    b3 = totals(p, k)
    r3 = tick(p, k, UM)
    check(r3 == (0, 0) and int(Pool.kept(k, ST)) == 482 and inv_counts(p).get(ST) == 482 and totals(p, k) == b3,
          "M: placing 30 blocks lowers kept to 482 (what you carry)")
    sto.addItemStack(IS(ST, 5))
    b4 = totals(p, k)
    check(tick(p, k, UM) == (5, 0) and inv_counts(p).get(ST) == 482 and totals(p, k) == b4, "M: after placing, 5 newly mined go in, 482 stay")
    # Pick up all (the page loop) adds to kept; Deposit all on the Mining tab clears only Mining kept counts
    Pool.add(k, ORE, 70)
    tot_ = 0
    while True:
        a_ = int(Sweep.withdraw(p, k, ORE, 64))
        tot_ += a_
        if a_ <= 0:
            break
    put(hot, 3, FOR_S, 1)
    Pool.add(k, LOG, 20)
    Sweep.withdraw(p, k, LOG, 64)
    check(tot_ == 70 and int(Pool.kept(k, ORE)) == 70 and int(Pool.kept(k, LOG)) == 20, "M: Pick up all keeps 70 ore, a log withdraw keeps 20 logs")
    b5 = totals(p, k)
    Pool.clearKeptCat(k, "Mining")
    Pool.forgetSeen(UM)
    dep = int(Sweep.sweep(p, k, "Mining", True))
    ic = inv_counts(p)
    check(int(Pool.kept(k, ST)) == 0 and int(Pool.kept(k, ORE)) == 0 and int(Pool.kept(k, LOG)) == 20 and ST not in ic and ORE not in ic
          and ic.get(LOG) == 20 and dep == 482 + 70 and totals(p, k) == b5,
          "M: Deposit all (Mining) clears the Mining kept counts, deposits all %d (hotbar too), the Foraging kept 20 logs stay" % dep)
    check(tick(p, k, UM) == (0, 0) and inv_counts(p).get(LOG) == 20, "M: the next sweep leaves the 20 kept logs alone")
    # taking a stack out while some of that item already sits in the hotbar / backpack (never swept): those count as kept, so the new
    # stack is not pulled back in their place (without it: 30 + 64 carried, kept 64 -> the sweep would take 30 of the new stack)
    fresh_pools(os.path.join(SCRATCH, "pools-m2"))
    k = "m-hot"
    Pool.add(k, ST, 300)
    p = player(hotbar=[(MIN_L, 1), (ST, 30)], backpack=[(ST, 6)])
    bm = totals(p, k)
    got = int(Sweep.withdraw(p, k, ST, 64))
    rh = [tick(p, k, UM) for _ in range(3)]
    check(got == 64 and int(Pool.kept(k, ST)) == 30 + 6 + 64 and rh == [(0, 0)] * 3 and inv_counts(p).get(ST) == 100 and totals(p, k) == bm,
          "M: 30 in the hotbar + 6 in the backpack, take 64 -> kept 100, the new stack stays (3 ticks: %s)" % rh)
    sto2 = p.getInventory().getStorage()
    sto2.addItemStack(IS(ST, 8))
    bm2 = totals(p, k)
    check(tick(p, k, UM) == (8, 0) and inv_counts(p).get(ST) == 100 and totals(p, k) == bm2, "M: and 8 newly mined still go in")
    print("M. kept: 512 taken -> 512 stay (also 64 hotbar + 448), +10 mined -> 10 go in (storage or hotbar pickup), placing lowers kept, "
          "Pick up all, Deposit all clears that tab only, a stack taken with some in the hotbar stays")

    # ---------------- N. STACK AUTO-REFILL in each mode (R3 / R4)
    UN = mkuuid(0x22)

    def n_setup(mode, pool_n=1000, bags=(MIN_L,), name="n"):
        fresh_pools(os.path.join(SCRATCH, "pools-" + name))
        RF.MODES.clear()
        if mode is not None:
            RF.set(UN, mode)
        kk = "k-" + name
        Pool.add(kk, ST, pool_n)
        pp = player()
        h_, s_, b_ = conts(pp)
        for j_, bag_ in enumerate(bags):
            put(h_, 8 - j_, bag_, 1)
        return kk, pp, h_, s_, b_

    # HOTBAR ONLY (the default: no RefillPref line)
    k, p, hot, sto, bp = n_setup(None, bags=(MIN_L, COM_S), name="n1")
    put(hot, 0, ST, 64)
    put(sto, 0, ST, 30)
    put(hot, 5, BONE, 3)                   # a picked-up partial stack nobody uses
    Pool.add(k, BONE, 100)
    Pool.keep(k, ST, 94)
    check(int(RF.mode(UN)) == 0, "N: the default mode is Hotbar only")
    check(tick(p, k, UN) == (0, 0), "N: first tick = baseline, nothing moves")
    use(hot, 0, 20)
    bu = totals(p, k)
    r = tick(p, k, UN)
    check(r == (0, 20) and at(hot, 0) == (ST, MAXS) and at(sto, 0) == (ST, 30) and at(hot, 5) == (BONE, 3)
          and all(at(hot, i) is None for i in (1, 2, 3, 4, 6)) and pool_counts(k).get(ST) == 980 and totals(p, k) == bu,
          "N HOTBAR: the used hotbar stack tops back up 44 -> 64 (20 from the bag), the main inventory stack and the unused bones stay, "
          "no empty slot filled, counted: %s" % (r,))
    check(int(Pool.kept(k, ST)) == 94, "N: kept follows: 94 - 20 used + 20 refilled = %d" % int(Pool.kept(k, ST)))
    check([tick(p, k, UN) for _ in range(3)] == [(0, 0)] * 3 and at(hot, 0) == (ST, MAXS) and pool_counts(k).get(ST) == 980,
          "N HOTBAR: refilled stone stays (kept) - nothing moves on the next 3 ticks")
    use(sto, 0, 6)                         # a craft takes 6 stone from the main inventory: the ITEM is in use
    use(hot, 0, 4)
    bu = totals(p, k)
    r = tick(p, k, UN)
    check(r == (0, 4) and at(hot, 0) == (ST, MAXS) and at(sto, 0) == (ST, 24) and totals(p, k) == bu,
          "N HOTBAR: stone used from the main inventory + hotbar -> only the hotbar stack tops up: %s" % (r,))
    # FULL INVENTORY: hotbar + main inventory + backpack
    k, p, hot, sto, bp = n_setup(1, name="n2")
    put(hot, 0, ST, 64)
    put(sto, 0, ST, 30)
    put(bp, 0, ST, 10)
    Pool.keep(k, ST, 104)
    tick(p, k, UN)
    use(hot, 0, 5)
    bu = totals(p, k)
    r = tick(p, k, UN)
    check(r == (0, 5 + 34 + 54) and at(hot, 0) == (ST, MAXS) and at(sto, 0) == (ST, MAXS) and at(bp, 0) == (ST, MAXS)
          and pool_counts(k).get(ST) == 1000 - 93 and int(Pool.kept(k, ST)) == 3 * MAXS and totals(p, k) == bu
          and all(at(sto, i) is None for i in range(1, 36)) and all(at(bp, i) is None for i in range(1, 9)),
          "N FULL: every stack of the used item tops up - hotbar +5, main inventory +34, backpack +54 = 93, no empty slot filled: %s" % (r,))
    check([tick(p, k, UN) for _ in range(3)] == [(0, 0)] * 3, "N FULL: the topped-up main inventory stack is kept - the sweep leaves it")
    # OFF
    k, p, hot, sto, bp = n_setup(2, name="n3")
    put(hot, 0, ST, 64)
    Pool.keep(k, ST, 64)
    tick(p, k, UN)
    use(hot, 0, 10)
    bu = totals(p, k)
    r0 = tick(p, k, UN)
    sto.addItemStack(IS(ST, 7))            # mined
    bu2 = totals(p, k)
    r = tick(p, k, UN)
    check(r0 == (0, 0) and r == (7, 0) and at(hot, 0) == (ST, 54) and totals(p, k) == bu2 and bu2[ST] == bu[ST] + 7,
          "N OFF: nothing tops up; the sweep still takes the 7 mined: %s %s" % (r0, r))
    # a use and a pickup of the same item inside ONE 2 s interval net out (documented edge): used 5 + mined 7 = carried +2 -> no "use"
    # is seen (no refill this time) and only the 2 above kept go in; the 5 mined that replace the used ones stay
    use(hot, 0, 5)
    sto.addItemStack(IS(ST, 7))
    RF.set(UN, 0)
    bu3 = totals(p, k)
    r = tick(p, k, UN)
    check(r == (2, 0) and at(hot, 0) == (ST, 49) and inv_counts(p).get(ST) == 54 and totals(p, k) == bu3,
          "N edge: used 5 + mined 7 inside one 2 s -> the net +2 go in, no refill this tick: %s" % (r,))
    # the pool runs out
    k, p, hot, sto, bp = n_setup(0, pool_n=12, name="n4")
    put(hot, 0, ST, 64)
    Pool.keep(k, ST, 64)
    tick(p, k, UN)
    use(hot, 0, 30)
    bu = totals(p, k)
    r = tick(p, k, UN)
    check(r == (0, 12) and at(hot, 0) == (ST, 46) and ST not in pool_counts(k) and totals(p, k) == bu, "N: the pool runs out: 12 of 30 refilled: %s" % (r,))
    use(hot, 0, 5)
    check(tick(p, k, UN) == (0, 0) and at(hot, 0) == (ST, 41), "N: empty pool -> nothing more")
    # no bag carried / another type's bag only
    for bags, label in (((), "no bag"), ((FOR_S,), "a Foraging bag only"), ((COM_S,), "a Combat bag only")):
        k, p, hot, sto, bp = n_setup(1, bags=bags, name="n5" + str(len(label)))
        put(hot, 0, ST, 64)
        tick(p, k, UN)
        use(hot, 0, 10)
        bu = totals(p, k)
        check(tick(p, k, UN) == (0, 0) and at(hot, 0) == (ST, 54) and pool_counts(k).get(ST) == 1000 and totals(p, k) == bu,
              "N: %s -> no refill (FULL mode)" % label)
    # a stack with metadata is never touched (FULL mode, the plain stack of the same item still tops up)
    k, p, hot, sto, bp = n_setup(1, name="n6")
    put(hot, 0, ST, 40, meta=True)
    put(hot, 1, ST, 40)
    Pool.keep(k, ST, 80)
    tick(p, k, UN)
    use(hot, 0, 5)
    use(hot, 1, 5)
    bu = totals(p, k)
    r = tick(p, k, UN)
    m0 = hot.getItemStack(JShort(0))
    check(r == (0, 29) and at(hot, 0) == (ST, 35) and m0.getMetadata() is not None and at(hot, 1) == (ST, MAXS) and totals(p, k) == bu,
          "N: the stack with metadata stays 35 (never touched), the plain one tops up 35 -> 64: %s" % (r,))
    # review fix 13: an EMPTY metadata document counts as none - that stack tops up too (merged with a copy of the empty document, which
    # isStackableWith needs); a document with entries is still never touched
    k, p, hot, sto, bp = n_setup(1, name="n6b")
    hot.setItemStackForSlot(JShort(0), IS(ST, 40, BsonDocument()))
    put(hot, 1, ST, 40, meta=True)
    Pool.keep(k, ST, 80)
    tick(p, k, UN)
    use(hot, 0, 5)
    use(hot, 1, 5)
    bu = totals(p, k)
    r = tick(p, k, UN)
    e0, m1_ = hot.getItemStack(JShort(0)), hot.getItemStack(JShort(1))
    check(r == (0, 29) and at(hot, 0) == (ST, MAXS) and e0.getMetadata() is not None and bool(e0.getMetadata().isEmpty())
          and at(hot, 1) == (ST, 35) and m1_.getMetadata() is not None and not bool(m1_.getMetadata().isEmpty()) and totals(p, k) == bu
          and int(Pool.kept(k, ST)) == 70 + 29,
          "N review fix 13: the stack with an EMPTY metadata document tops up 35 -> 64 (document kept), a real one stays 35: %s" % (r,))
    # a bench fed from the bags (a BagMirror for the key + an open bench window): the refill waits, the use stays pending, refilled once
    # the bench closes. Review fix 9: the wait needs a really OPEN bench window (a MaterialContainerWindow in the player's WindowManager);
    # a mirror left behind with no open bench (a bench link that failed before removing it) is synced - what a bench took is booked - and
    # dropped, then the refill runs on the right pool
    MCWN = "com.hypixel.hytale.server.core.entity.entities.player.windows.MaterialContainerWindow"
    tbw = jp.makeClass("com.hypixel.hytale.server.core.entity.entities.player.windows.SkyyTestBenchWin")
    tbw.addInterface(jp.get(MCWN))
    TBW = JClass(tbw.toClass(JClass(MCWN).class_))
    WMC = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager")
    wm_field = jfield(PLA.class_, "windowManager")
    wins_field = jfield(WMC.class_, "windows")

    def open_bench(pp):         # the player opens a bench: a MaterialContainerWindow in their WindowManager
        wm_ = WMC()
        wins_field.get(wm_).put(JInt(7), us.allocateInstance(TBW.class_))
        wm_field.set(pp, wm_)
        return wm_

    def close_bench(wm_):       # the window closes; its mirror stays (as if the bench link had failed before removing it)
        wins_field.get(wm_).remove(JInt(7))
    k, p, hot, sto, bp = n_setup(0, name="n7")
    put(hot, 0, ST, 64)
    Pool.keep(k, ST, 64)
    tick(p, k, UN)
    mir_ = Mirror.of(k)
    use(hot, 0, 10)
    bu = totals(p, k)
    r_nb = tick(p, k, UN)        # a mirror but NO open bench window: synced, dropped, refilled (0.7.11 before the fix waited forever)
    check(r_nb == (0, 10) and at(hot, 0) == (ST, MAXS) and Mirror.MIRRORS.get(k) is None and Pool.PENDQ.get(UN) is None and totals(p, k) == bu,
          "N review fix 9: a left-over mirror with no open bench no longer pauses the refill (dropped, 10 refilled): %s" % (r_nb,))
    mir_ = Mirror.of(k)
    wm7 = open_bench(p)
    use(hot, 0, 10)
    bu = totals(p, k)
    r = tick(p, k, UN)
    pend = Pool.PENDQ.get(UN)
    check(r == (0, 0) and at(hot, 0) == (ST, 54) and pend is not None and pend.contains(ST) and Mirror.MIRRORS.get(k) is not None
          and totals(p, k) == bu, "N: a bench window open + fed from the bags -> no refill, the used stone stays pending: %s" % (r,))
    check([tick(p, k, UN) for _ in range(2)] == [(0, 0)] * 2 and at(hot, 0) == (ST, 54) and Pool.PENDQ.get(UN) is not None,
          "N: still no refill while that bench stays open (the use stays pending)")
    close_bench(wm7)
    r = tick(p, k, UN)
    check(r == (0, 10) and at(hot, 0) == (ST, MAXS) and Pool.PENDQ.get(UN) is None and Mirror.MIRRORS.get(k) is None and totals(p, k) == bu,
          "N: bench closed (its mirror left behind) -> synced + dropped, the pending use is refilled on the next tick: %s" % (r,))
    # a left-over mirror whose bench TOOK items: the take is booked before the refill reads the pool - never counted twice
    k, p, hot, sto, bp = n_setup(0, pool_n=100, name="n7b")
    put(hot, 0, ST, 64)
    Pool.keep(k, ST, 64)
    tick(p, k, UN)
    wm7b = open_bench(p)
    mb = Mirror.of(k)
    mb.rebuild(Sweep.caps(p.getInventory()))
    took = 0
    for s_ in range(36):                     # the bench crafts with 30 stone out of the mirror
        if mb.slotIds[s_] is not None and str(mb.slotIds[s_]) == ST:
            mb.cont.removeItemStackFromSlot(JShort(s_), JInt(30))
            took = 30
            break
    use(hot, 0, 40)
    bu = totals(p, k)                        # inventory 24 + pool 100 (the bench's 30 are not booked yet)
    r1 = tick(p, k, UN)                      # bench open -> pending
    close_bench(wm7b)
    r2 = tick(p, k, UN)                      # mirror synced (30 booked: pool 70), then the refill tops 24 -> 64 (40 from the pool: 30 left)
    check(took == 30 and r1 == (0, 0) and r2 == (0, 40) and at(hot, 0) == (ST, MAXS) and pool_counts(k).get(ST) == 30
          and total_of(p, k, ST) == bu[ST] - 30 and Mirror.MIRRORS.get(k) is None,
          "N review fix 9: the bench's 30 are booked before the refill (pool 100 - 30 - 40 = 30), nothing counted twice: %s %s" % (r1, r2))
    wm_field.set(p, None)
    # a non-stacking item (max stack 1) is never refilled
    ms_f.setInt(ItemC.UNKNOWN, 1)
    k, p, hot, sto, bp = n_setup(1, name="n8")
    put(hot, 0, ST, 1)
    put(hot, 1, ST, 1)
    tick(p, k, UN)
    use(hot, 0, 1)
    check(tick(p, k, UN) == (0, 0) and at(hot, 1) == (ST, 1) and at(hot, 0) is None, "N: max stack 1 -> never refilled, the emptied slot stays empty")
    ms_f.setInt(ItemC.UNKNOWN, MAXS)
    print("N. refill: HOTBAR tops a used hotbar stack only, FULL all three containers, OFF nothing, pool runs out, no bag / other bag, "
          "metadata stack untouched, bench open -> pending, max stack 1, every case counted")

    # ---------------- P. refill + sweep never fight: 20 ticks per scenario
    UP = mkuuid(0x33)

    def run20(p, k, u, actions, label, settle_after=None):
        """20 ticks; actions = {tick: fn} run before that tick. Checks: inventory + pool (+ what the actions removed / added) conserved,
        no item's pool movement flips direction between two ticks unless the player acted right before the later one, and once the
        player has stopped acting nothing moves after one tick."""
        last_d = {}
        moves = []
        act_ticks = sorted(actions)
        for t_ in range(20):
            acted = t_ in actions
            if acted:
                actions[t_]()
            before_p = pool_counts(k)
            before_t = totals(p, k)
            tick(p, k, u)
            after_p = pool_counts(k)
            check(totals(p, k) == before_t, "P %s tick %d: every item counted" % (label, t_))
            d = dict((i, after_p.get(i, 0) - before_p.get(i, 0)) for i in set(before_p) | set(after_p) if after_p.get(i, 0) != before_p.get(i, 0))
            moves.append(d)
            for i, dv in d.items():
                pv = last_d.get(i)
                if pv is not None and (pv > 0) != (dv > 0) and not acted:
                    check(False, "P %s tick %d: %s flipped direction (%+d after %+d) with no player action - ping-pong" % (label, t_, i, dv, pv))
            last_d = d if d else {}
        quiet_from = (act_ticks[-1] + 2) if act_ticks else 1
        late = [(t_, m_) for t_, m_ in enumerate(moves) if t_ >= quiet_from and m_]
        check(not late, "P %s: nothing moves once the player is idle (from tick %d): %s" % (label, quiet_from, late[:3]))
        return moves

    def p_setup(mode, name, cap_bag=MIN_S):
        fresh_pools(os.path.join(SCRATCH, "pools-p" + name))
        RF.MODES.clear()
        RF.set(UP, mode)
        kk = "p-" + name
        pp = player()
        h_, s_, b_ = conts(pp)
        put(h_, 8, cap_bag, 1)
        return kk, pp, h_, s_, b_

    k, p, hot, sto, bp = p_setup(0, "1")
    Pool.add(k, ST, 500)
    put(hot, 0, ST, 50)
    mv = run20(p, k, UP, {}, "idle HOTBAR (a mined 50 in the hotbar)")
    check(not any(mv) and at(hot, 0) == (ST, 50), "P idle: a mined partial hotbar stack is never topped up (not used), nothing moves in 20 ticks")
    k, p, hot, sto, bp = p_setup(0, "2")
    Pool.add(k, ST, 500)
    put(hot, 0, ST, 64)
    Pool.keep(k, ST, 64)
    mv = run20(p, k, UP, {3: lambda: use(hot, 0, 20)}, "use then idle")
    check(mv[3] == {ST: -20} and at(hot, 0) == (ST, MAXS), "P use then idle: one refill of 20 at tick 3, then nothing: %s" % mv[3])
    for mode, nm in ((1, "3"), (0, "4")):      # the bag is full and spare stone sits in the main inventory
        k, p, hot, sto, bp = p_setup(mode, nm)
        Pool.add(k, ST, 640)                    # = the Normal bag's cap
        put(sto, 0, ST, 64)
        put(sto, 1, ST, 36)
        put(hot, 0, ST, 64)
        Pool.keep(k, ST, 64)
        mv = run20(p, k, UP, {2: lambda: use(hot, 0, 10)}, "bag full + spare in storage (%s)" % ("FULL" if mode else "HOTBAR"))
        check(not any(mv) and at(hot, 0) == (ST, 54) and pool_counts(k).get(ST) == 640,
              "P bag full + 100 spare in the main inventory (%s): no refill (the next sweep would only take it back), nothing moves"
              % ("FULL" if mode else "HOTBAR"))
    k, p, hot, sto, bp = p_setup(1, "5")      # FULL: a taken-out (kept) main inventory stack + a used hotbar stack
    Pool.add(k, ST, 300)
    put(sto, 0, ST, 40)
    put(hot, 0, ST, 64)
    Pool.keep(k, ST, 104)
    mv = run20(p, k, UP, {2: lambda: use(hot, 0, 10)}, "kept storage stack + used stack (FULL)")
    check(at(hot, 0) == (ST, MAXS) and at(sto, 0) == (ST, MAXS) and int(Pool.kept(k, ST)) == 2 * MAXS and mv[2] == {ST: -34},
          "P FULL: both stone stacks top up once (+10 hotbar, +24 main inventory = %s at tick 2) and stay kept, then nothing" % mv[2])
    k, p, hot, sto, bp = p_setup(0, "5b")     # HOTBAR: 40 mined into the main inventory, later a used hotbar stack
    Pool.add(k, ST, 300)
    put(hot, 0, ST, 64)
    Pool.keep(k, ST, 64)
    mv = run20(p, k, UP, {2: lambda: sto.addItemStack(IS(ST, 40)), 5: lambda: use(hot, 0, 10)}, "mined then used (HOTBAR)")
    check(mv[2] == {ST: 40} and mv[5] == {ST: -10} and at(hot, 0) == (ST, MAXS) and all(at(sto, i) is None for i in range(36)),
          "P mined excess goes in at tick 2 (%s), the used stack tops up at tick 5 (%s), nothing else moves" % (mv[2], mv[5]))
    k, p, hot, sto, bp = p_setup(0, "6")      # a steady builder: 3 blocks every tick
    Pool.add(k, ST, 500)
    put(hot, 0, ST, 64)
    Pool.keep(k, ST, 64)
    placed = [0]

    def build3():
        use(hot, 0, 3)
        placed[0] += 3
    mv = run20(p, k, UP, dict((t_, build3) for t_ in range(1, 20)), "steady builder")
    check(all(v <= 0 for m_ in mv for v in m_.values()) and at(hot, 0) == (ST, MAXS) and total_of(p, k, ST) + placed[0] == 564,
          "P steady builder: only refills (never a sweep back), the stack is full after every tick, %d placed, all counted" % placed[0])
    k, p, hot, sto, bp = p_setup(0, "7", cap_bag=COM_S)   # pickups into free hotbar slots (Hytale's default pickup location)
    Pool.add(k, BONE, 200)
    got_b = [0]

    def pick():
        hot.addItemStack(IS(BONE, 1))
        got_b[0] += 1
    mv = run20(p, k, UP, dict((t_, pick) for t_ in range(0, 20, 3)), "single pickups")
    check(not any(mv) and inv_counts(p).get(BONE) == got_b[0] and pool_counts(k).get(BONE) == 200,
          "P pickups: %d single bones picked up into the hotbar are never turned into full stacks from the bag (never used)" % got_b[0])
    print("P. refill + sweep never fight: 8 scenarios x 20 ticks - no direction flip without a player action, idle = no movement, all counted")

    # ---------------- Q. BAGS ADD UP (R4)
    def capsof(*stacks):
        pp = player(hotbar=list(stacks)) if len(stacks) <= 9 else None
        cc, rr, nn = HashMap(), HashMap(), HashMap()
        Sweep.scanN(pp.getInventory(), cc, rr, nn)
        return (dict((str(e.getKey()), int(e.getValue())) for e in cc.entrySet()), dict((str(e.getKey()), int(e.getValue())) for e in rr.entrySet()),
                dict((str(e.getKey()), [int(x) for x in e.getValue()]) for e in nn.entrySet()))

    def two_slots(a_id, b_id):
        pp = player()
        h_ = pp.getInventory().getHotbar()
        put(h_, 0, a_id, 1)
        put(h_, 1, b_id, 1)
        return dict((str(e.getKey()), int(e.getValue())) for e in Sweep.caps(pp.getInventory()).entrySet())
    c2 = two_slots(MIN_S, MIN_S)
    check(c2 == {"Mining": 1280}, "Q: two Normal Mining bags = 2 x 640 = 1,280: %s" % c2)
    cnl = two_slots(MIN_S, MIN_L)
    check(cnl == {"Mining": 640 + 20160}, "Q: Normal + Legendary Mining = 20,800: %s" % cnl)
    col = two_slots(OMNI, MIN_L)
    check(col == dict([(c_, 100000 + (20160 if c_ == "Mining" else 0)) for c_ in [str(x) for x in Defs.CATS]]),
          "Q: Omni + Legendary Mining = Mining 120,160, every other type 100,000: %s" % col)
    c1, r1_, n1_ = capsof((OMNI, 1))
    check(c1 == dict((str(x), 100000) for x in Defs.CATS) and all(v == 6 for v in r1_.values()), "Q: the Omni alone = 100,000 for every type (rank 6)")
    coo = two_slots(OMNI, OMNI)
    check(coo == dict((str(x), 200000) for x in Defs.CATS), "Q: two Omni bags = 200,000 for every type")
    cs, rs, ns = capsof((MIN_S, 2))          # one stack of 2 bags (merged in a bare JVM; MaxStack 1 in game)
    check(cs == {"Mining": 1280} and ns.get("Mining") == [2, 0, 0, 0, 0], "Q: a stack of 2 Normal bags counts twice: %s %s" % (cs, ns))
    pq = player()
    hq = pq.getInventory().getHotbar()
    for j_, bid in enumerate((MIN_S, MIN_S, MIN_L, OMNI, "Skyy_Sack_Mining_Epic", "Skyy_Sack_Fishing_Small", FOR_S)):
        put(hq, j_, bid, 1)
    cc, rr, nn = HashMap(), HashMap(), HashMap()
    Sweep.scanN(pq.getInventory(), cc, rr, nn)
    check(int(cc.get("Mining")) == 2 * 640 + 20160 + 100000 and int(cc.get("Foraging")) == 640 + 100000 and int(rr.get("Mining")) == 6
          and [int(x) for x in nn.get("Mining")] == [2, 0, 0, 1, 1] and not any(str(x) == "Fishing" for x in cc.keySet()),
          "Q: 2 Normal + Legendary + Omni (Mining 121,440), unknown tier / type ids skipped, counts per rarity %s" % [int(x) for x in nn.get("Mining")])
    Defs.CAP_LARGE = 1000000
    cb, rb, nb_ = HashMap(), HashMap(), HashMap()
    Sweep.bagOf(MIN_L, 3000, cb, rb, nb_)
    check(int(cb.get("Mining")) == 2147483647, "Q: 3,000 bags of 1,000,000 clamp at Integer.MAX_VALUE (no overflow)")
    Defs.CAP_LARGE = 20160
    # the sweep uses the summed room; dropping a bag never deletes pooled items
    fresh_pools(os.path.join(SCRATCH, "pools-q"))
    k = "q"
    pq = player()
    hq, sq, _bq = conts(pq)
    put(hq, 7, MIN_S, 1)
    put(hq, 8, MIN_S, 1)
    for j_ in range(24):
        put(sq, j_, ST, MAXS)               # 1,536 stone
    bq_ = totals(pq, k)
    mvq = int(Sweep.sweep(pq, k, None, False))
    check(mvq == 1280 and pool_counts(k).get(ST) == 1280 and inv_counts(pq).get(ST) == 256 and totals(pq, k) == bq_,
          "Q: two Normal bags -> the sweep fills 1,280 of each item (one bag stopped at 640)")
    hq.removeItemStackFromSlot(JShort(8), JInt(1))      # one bag dropped
    mvq2 = int(Sweep.sweep(pq, k, None, False))
    got2 = int(Sweep.withdraw(pq, k, ST, 64))
    check(mvq2 == 0 and pool_counts(k).get(ST) == 1280 - got2 and got2 == 64,
          "Q: one bag dropped -> 640 space, nothing deleted (1,280 stay), intake stops, withdraw works (%d)" % got2)
    # the page: cap line + the bags line
    fresh_pools(os.path.join(SCRATCH, "pools-q2"))
    kq = "q2"
    Pool.add(kq, ST, 1234)
    for stacks, cap_txt, line in ((((MIN_S, 1), (MIN_S, 1), (MIN_L, 1)), "Mining - 3 bags - up to 21,440 of each item - 1,234 stored",
                                   "From 3 bags: 2 Normal + 1 Legendary - their space adds up"),
                                  (((MIN_L, 1),), "Mining - Legendary bag - up to 20,160 of each item - 1,234 stored",
                                   "From 1 Legendary bag - another bag of this type adds its space"),
                                  (((OMNI, 1),), "Mining - Mythic Omni Bag - up to 100,000 of each item - 1,234 stored",
                                   "From the Mythic Omni Bag - any other bag you carry adds its space"),
                                  (((OMNI, 1), (MIN_L, 1)), "Mining - 2 bags - up to 120,160 of each item - 1,234 stored",
                                   "From 2 bags: 1 Legendary + 1 Mythic Omni - their space adds up")):
        pp = player()
        h_ = pp.getInventory().getHotbar()
        for j_, (bid, n_) in enumerate(stacks):
            put(h_, j_, bid, n_)
        t_, _c = render(pp, kq, "Mining")
        check(cap_txt in t_ and line in t_, "Q page: %r + %r" % (cap_txt, line))
    print("Q. bags add up: 2 Normal 1,280, Normal + Legendary 20,800, Omni + Legendary 120,160, Omni 100,000 / two 200,000, stacks, unknown "
          "ids, clamp, the sweep's room, a dropped bag deletes nothing, the page lines")

    # ---------------- S. relog / profile switch / busy profile
    US = mkuuid(0x44)
    import time as _stime
    fresh_pools(os.path.join(SCRATCH, "pools-s"))
    k = "s-relog"
    Pool.add(k, ST, 300)
    p = player(hotbar=[(MIN_S, 1)])
    Sweep.withdraw(p, k, ST, 64)
    tick(p, k, US)
    check(int(Pool.kept(k, ST)) == 64 and str(Pool.KEPTKEY.get(US)) == k and Pool.SEENQ.get(US) is not None, "S: kept 64 + refill memory before the relog")
    pfile = os.path.join(SCRATCH, "pools-s", k + ".properties")
    check(bool(Pool.DIRTY.containsKey(k)) and not os.path.exists(pfile), "S: before the quit the pool has an unsaved move (no file yet)")
    KQ().accept(PDEv(mkpr(US)))
    check(int(Pool.kept(k, ST)) == 0 and Pool.KEPTKEY.get(US) is None and Pool.SEENQ.get(US) is None,
          "S: KeptQuit on a PlayerDisconnectEvent forgets the kept counts (key %s) and the refill memory" % k)
    # review fix 10: the engine saves the inventory at disconnect - KeptQuit writes that player's unsaved pool at once (the SackSaver on
    # the scheduler, SackPool.saveSoon), not up to 10 s later
    for _w in range(50):
        if os.path.exists(pfile) and not bool(Pool.DIRTY.containsKey(k)):
            break
        _stime.sleep(0.1)
    ptxt = open(pfile, encoding="latin-1").read() if os.path.exists(pfile) else ""
    check("%s=236" % ST in ptxt and not bool(Pool.DIRTY.containsKey(k)),
          "S review fix 10: KeptQuit writes the quitting player's unsaved pool at once (%s)" % [l for l in ptxt.splitlines() if ST in l])
    bs = totals(p, k)
    check(tick(p, k, US) == (64, 0) and totals(p, k) == bs, "S: after the relog the next sweep collects the 64 stone again (no timer, no memory)")
    # profile switch: settledKey sees a new key / epoch
    keybox = ["pA"]
    bridge.put("profile:fn:key", Fn(lambda a: JString(keybox[0])))
    bridge.put("profile:epoch:" + str(US), LongJ.valueOf(1))
    fresh_pools(os.path.join(SCRATCH, "pools-s2"))
    for kk in ("pA", "pB"):
        Pool.add(kk, ST, 200)
    Pool.CHANGEDAT.clear()
    Pool.SEENKEY.clear()
    Pool.SEENEPOCH.clear()
    p = player(hotbar=[(MIN_S, 1)])
    check(str(Pool.settledKey(US)) == "pA", "S: profile pA settled")
    Sweep.withdraw(p, "pA", ST, 64)
    Pool.keep("pB", ST, 5)
    check(tick_gate(p, US) == (0, 0) and int(Pool.kept("pA", ST)) == 64, "S: kept 64 on profile pA")
    # review fix 4: a new epoch with the SAME key (a profile created, /profileadmin setclass of the active one) keeps the kept counts -
    # the settle window still pauses the tick; afterwards the 64 taken-out stone are NOT swept back in
    bridge.put("profile:epoch:" + str(US), LongJ.valueOf(2))
    bs4 = totals(p, "pA")
    gate4 = [tick_gate(p, US) for _ in range(3)]
    check(gate4 == [None] * 3 and int(Pool.kept("pA", ST)) == 64 and int(Pool.kept("pB", ST)) == 5 and Pool.SEENQ.get(US) is not None
          and totals(p, "pA") == bs4, "S review fix 4: same key pA, epoch 1 -> 2: kept 64 (and pB's 5) stay, the settle window pauses the tick")
    Pool.CHANGEDAT.remove(US)                # the 6 s settle window passed
    r4 = [tick_gate(p, US) for _ in range(3)]
    check(r4 == [(0, 0)] * 3 and inv_counts(p).get(ST) == 64 and int(Pool.kept("pA", ST)) == 64 and totals(p, "pA") == bs4,
          "S review fix 4: after the window the 64 taken-out stone stay in the inventory (before the fix they were swept back): %s" % r4)
    keybox[0] = "pB"
    bridge.put("profile:epoch:" + str(US), LongJ.valueOf(3))
    bs = totals(p, "pA")
    gate = [tick_gate(p, US) for _ in range(5)]
    check(gate == [None] * 5 and int(Pool.kept("pA", ST)) == 0 and int(Pool.kept("pB", ST)) == 0 and Pool.SEENQ.get(US) is None
          and totals(p, "pA") == bs, "S: switch pA -> pB: both keys' kept counts and the refill memory reset; 5 ticks while it settles do nothing")
    Pool.CHANGEDAT.remove(US)                # the 6 s settle window passed
    check(str(Pool.settledKey(US)) == "pB", "S: pB settled after the window")
    # busy (crash recovery pending) and unknown profile state: the tick does nothing
    fresh_pools(os.path.join(SCRATCH, "pools-s3"))
    keybox[0] = "pC"
    Pool.CHANGEDAT.clear()
    Pool.SEENKEY.clear()
    Pool.SEENEPOCH.clear()
    Pool.add("pC", ST, 100)
    RF.set(US, 1)
    p = player()
    h_, s_, b_ = conts(p)
    put(h_, 8, MIN_S, 1)
    put(h_, 0, ST, 64)
    Pool.keep("pC", ST, 64)
    check(tick_gate(p, US) == (0, 0), "S: pC baseline")
    put(s_, 0, ST, 20)                       # mined
    bridge.put("profile:busy:" + str(US), JString("recovering"))
    bs = (inv_counts(p), pool_counts("pC"))
    gate = [tick_gate(p, US) for _ in range(5)]
    check(gate == [None] * 5 and (inv_counts(p), pool_counts("pC")) == bs, "S: profile busy -> 5 ticks: no sweep, no refill, nothing moves")
    bridge.remove("profile:busy:" + str(US))
    bridge.remove("profile:epoch:" + str(US))
    Pool.UNKNOWN.clear()
    check(tick_gate(p, US) is None and (inv_counts(p), pool_counts("pC")) == bs, "S: SkyyProfiles without an epoch for the player -> nothing moves")
    bridge.put("profile:epoch:" + str(US), LongJ.valueOf(3))      # the same epoch as before: an absent epoch is no change
    r = tick_gate(p, US)
    use(h_, 0, 10)
    r2 = tick_gate(p, US)
    check(r == (20, 0) and r2 == (0, 10) and at(h_, 0) == (ST, MAXS),
          "S: state known again -> the 20 mined go in (%s), a later use tops up (%s)" % (r, r2))
    # review fix 10: the shutdown latch - once SkyySacksPlugin.shutdown() began, settledKey answers null: no sweep, no refill
    put(s_, 1, ST, 7)                        # mined
    use(h_, 0, 3)
    bsl = (inv_counts(p), pool_counts("pC"))
    Pool.CLOSED = True
    gl = [tick_gate(p, US) for _ in range(3)]
    Pool.CLOSED = False
    check(gl == [None] * 3 and (inv_counts(p), pool_counts("pC")) == bsl and str(Pool.settledKey(US)) == "pC",
          "S review fix 10: shutdown latch closed -> 3 ticks move nothing (7 mined, 3 used stay); open again -> the key is back")
    for k_ in list(bridge.keySet()):
        if str(k_).startswith("profile:"):
            bridge.remove(k_)
    Pool.CHANGEDAT.clear()
    Pool.SEENKEY.clear()
    Pool.SEENEPOCH.clear()
    Pool.UNKNOWN.clear()
    print("S. relog (KeptQuit) and profile switch reset kept + refill memory; busy / settling / unknown profile = nothing moves")

    # ---------------- R. the refill setting: persisted per player, the page row, the clicks (last: a click runs the SackSaver)
    UR, UR2 = mkuuid(0x55), mkuuid(0x56)
    rdir = os.path.join(SCRATCH, "refill")
    os.makedirs(rdir, exist_ok=True)
    rf_file = os.path.join(rdir, "refill.properties")
    RF.MODES.clear()
    RF.BROKEN = False
    RF.DIRTY = False
    RF.FILE = Paths.get(rf_file)
    RF.load()
    check(int(RF.mode(UR)) == 0 and not os.path.exists(rf_file), "R: no file, no line -> Hotbar only")
    RF.save()
    check(not os.path.exists(rf_file), "R: nothing changed -> no file written")
    RF.set(UR, 1)
    RF.set(UR2, 2)
    RF.save()
    txt = open(rf_file, encoding="latin-1").read()
    check(("%s=full" % UR) in txt and ("%s=off" % UR2) in txt and not bool(RF.DIRTY), "R: two choices saved (uuid=full / uuid=off)")
    RF.MODES.clear()
    RF.load()
    check(int(RF.mode(UR)) == 1 and int(RF.mode(UR2)) == 2, "R: reloaded after a restart: Full inventory / Off")
    RF.set(UR, 0)
    RF.save()
    RF.MODES.clear()
    RF.load()
    check(int(RF.mode(UR)) == 0 and ("%s=hotbar" % UR) in open(rf_file, encoding="latin-1").read(), "R: back to Hotbar only, saved")
    with open(rf_file, "a", encoding="latin-1") as fh:
        fh.write("00000000-0000-0000-0000-0000000000ff=fulll\n")
    RF.MODES.clear()
    RF.load()
    RF.set(UR2, 1)
    RF.save()
    t2 = open(rf_file, encoding="latin-1").read()
    check(int(RF.mode(mkuuid(0xff))) == 0 and "=fulll" in t2 and ("%s=full" % UR2) in t2, "R: an unknown word reads as the default and is kept on save")
    bad = os.path.join(rdir, "broken")
    os.makedirs(os.path.join(bad, "refill.properties"))
    RF.MODES.clear()
    RF.BROKEN = False
    RF.FILE = Paths.get(os.path.join(bad, "refill.properties"))
    RF.load()
    RF.set(UR, 2)
    RF.save()
    check(bool(RF.BROKEN) and int(RF.mode(UR)) == 2 and os.path.isdir(os.path.join(bad, "refill.properties")),
          "R: an unreadable file is left untouched, the choice holds for this session")
    RF.MODES.clear()
    RF.BROKEN = False
    RF.DIRTY = False
    RF.FILE = Paths.get(rf_file)
    RF.load()
    # the page row: both views, the chosen button on Tertiary_Active, the help line
    prR = mkpr(UR)

    def page_text(pp, k, cat, u_pr):
        pg = us.allocateInstance(Page.class_)
        PAGE_PR.set(pg, u_pr)
        pg.cat = cat
        pg.info = ""
        caps_, ranks_ = HashMap(), HashMap()
        Sweep.scan(pp.getInventory(), caps_, ranks_)
        b_ = UCB()
        pg.render(b_, UEB(), pp, k, caps_, ranks_)
        out = []
        for c_ in b_.getCommands():
            for f_ in ("data", "text", "selector"):
                try:
                    v_ = getattr(c_, f_)
                    if v_ is not None:
                        out.append(str(v_))
                except Exception:
                    pass
        return "\n".join(out), pg

    def chosen(text):
        got_ = []
        for suf in ("Hotbar", "Full", "Off"):
            m_ = re.search(r"TextButton #SkyySRefill%s \{[^\n]*?Default: \(Background: \(TexturePath: \"Common/Buttons/(Tertiary(?:_Active)?)\.png\"" % suf, text)
            got_.append(m_.group(1) if m_ else None)
        return got_

    fresh_pools(os.path.join(SCRATCH, "pools-r"))
    pr_ = player(hotbar=[(MIN_S, 1)])
    for mode in (0, 1, 2):
        RF.set(UR, mode)
        t_, _pg = page_text(pr_, "r", "Mining", prR)
        want = ["Tertiary"] * 3
        want[mode] = "Tertiary_Active"
        check(chosen(t_) == want and str(J("RefillPref").HELP[mode]) in t_ and "Stack refill from your bags" in t_
              and "Group #SkyySacks { Anchor: (Width: 1000, Height: 690); }" in t_,
              "R page (carried view, mode %d): the chosen button on Tertiary_Active %s, the help line, root 690" % (mode, chosen(t_)))
    t_, _pg = page_text(player(), "r", "Combat", prR)
    check(chosen(t_) == ["Tertiary", "Tertiary", "Tertiary_Active"] and "you do not carry one yet" in t_ and "#SkyySRefillOff" in t_,
          "R page (how-to-craft view): the refill row is there too")
    # review fix 1: vanilla benches do NOT use the bags yet (research/Bag-Craft-Link-Fix.md, 0.7.12) - no help line, page hint or log line
    # may say they do; the Hotbar / Full lines say the refill pauses while a bench is open (SweepTask.benchFed)
    BENCH_CLAIM = re.compile(r"[Bb]ench(es)? (already |still )?(use|craft)|[Ww]orkbench can use|use (your|the) bags")
    for h_ in list(RF.HELP) + [RF.OFFSRV]:
        check(len(str(h_)) <= 120 and not BENCH_CLAIM.search(str(h_)),
              "R review fix 1: the help line makes no bench claim (%d chars): %r" % (len(str(h_)), str(h_)))
    check(all("paused while a bench is open" in str(RF.HELP[i_]) for i_ in (0, 1)) and str(RF.HELP[2]).startswith("Stacks never top up"),
          "R review fix 1: Hotbar only / Full inventory say the refill pauses while a bench is open")
    check(not BENCH_CLAIM.search(t_) and "/craft can use the materials in the bags you carry" in t_,
          "R review fix 1: the how-to-craft view's hint names /craft, not the Workbench")
    ready_ = [l for l in ldcs(members(JAR, PKG + "SkyySacksPlugin")["m setup()V"]) if l.startswith("[SkyySacks] 0.7.11 ready")]
    check(len(ready_) == 1 and "benches craft from your bags" not in ready_[0] and "/craft crafts from your bags" in ready_[0],
          "R review fix 1: the ready log line no longer says benches craft from your bags")
    # the clicks (the event data the client sends) change the mode and save it through the SackSaver
    Cfg.FILE = Paths.get(os.path.join(rdir, "config.properties"))
    Cfg.MTIME = -1
    Cfg.reload()
    Notice = J("SackNotice")
    Notice.FILE = Paths.get(os.path.join(rdir, "notices.properties"))
    Notice.DIRTY = False
    RF.set(UR, 0)
    RF.DIRTY = False
    for word, mode in (("off", 2), ("full", 1), ("hotbar", 0)):
        _t, pg = page_text(pr_, "r", "Mining", prR)
        pg.handleDataEvent(None, None, '{"a":"refill:%s"}' % word)
        check(int(RF.mode(UR)) == mode and str(pg.info) == "Stack refill: " + str(RF.LABELS[mode]), "R click refill:%s -> mode %d (%s)" % (word, mode, pg.info))
    import time as _time
    for _w in range(50):
        if not bool(RF.DIRTY) and ("%s=hotbar" % UR) in open(rf_file, encoding="latin-1").read():
            break
        _time.sleep(0.1)
    RF.save()
    check(("%s=hotbar" % UR) in open(rf_file, encoding="latin-1").read(), "R: the clicked choice is saved (SackSaver / RefillPref.save)")
    # the next tick uses the clicked mode: FULL tops up the main inventory
    k = "r"
    fresh_pools(os.path.join(SCRATCH, "pools-r2"))
    Pool.add(k, ST, 300)
    p = player()
    h_, s_, b_ = conts(p)
    put(h_, 8, MIN_S, 1)
    put(h_, 0, ST, 64)
    put(s_, 0, ST, 40)
    Pool.keep(k, ST, 104)
    _t, pg = page_text(p, k, "Mining", prR)
    pg.handleDataEvent(None, None, '{"a":"refill:full"}')
    tick(p, k, UR)
    use(h_, 0, 4)
    r = tick(p, k, UR)
    check(r == (0, 4 + 24) and at(s_, 0) == (ST, MAXS), "R: after the Full inventory click the next refill tops the main inventory too: %s" % (r,))
    # review fix 8: the owner's switches. bags.refill off = no refill for anyone - the page keeps showing each player's pick and says the
    # server turned it off; bags.refillDefault = the mode of players who never picked one (an unknown word = hotbar)
    Cfg.FILE = None                          # no SackSaver reload of the R config file in between (the fields are set by hand here)
    RF.set(UR, 0)
    Cfg.REFILL_ON = False
    t_off, _pg = page_text(pr_, "r", "Mining", prR)
    check(int(RF.mode(UR)) == 2 and int(RF.choice(UR)) == 0 and chosen(t_off) == ["Tertiary_Active", "Tertiary", "Tertiary"]
          and str(RF.OFFSRV) in t_off and str(RF.HELP[0]) not in t_off,
          "R review fix 8: bags.refill off -> mode off, the page shows the player's pick (Hotbar only) + the server-off line")
    _pg.handleDataEvent(None, None, '{"a":"refill:full"}')
    check(int(RF.choice(UR)) == 1 and int(RF.mode(UR)) == 2 and "turned off on this server" in str(_pg.info),
          "R review fix 8: a click while it is off saves the pick and says so (%s)" % _pg.info)
    RF.set(UR, 0)
    fresh_pools(os.path.join(SCRATCH, "pools-r3"))
    Pool.add("r3", ST, 300)
    p3 = player()
    h3, s3, b3 = conts(p3)
    put(h3, 8, MIN_S, 1)
    put(h3, 0, ST, 64)
    Pool.keep("r3", ST, 64)
    tick(p3, "r3", UR)
    use(h3, 0, 10)
    r_off = tick(p3, "r3", UR)
    Cfg.REFILL_ON = True
    use(h3, 0, 5)
    r_on = tick(p3, "r3", UR)
    check(r_off == (0, 0) and r_on == (0, 15) and at(h3, 0) == (ST, MAXS),
          "R review fix 8: bags.refill off -> a used stack is not refilled (%s); back on -> the next use tops it up to full (%s)" % (r_off, r_on))
    UR3 = mkuuid(0x57)                       # a player who never picked a mode
    Cfg.REFILL_DEF = "full"
    t_def, _pg = page_text(pr_, "r", "Mining", mkpr(UR3))
    check(int(RF.mode(UR3)) == 1 and int(RF.choice(UR3)) == 1 and chosen(t_def) == ["Tertiary", "Tertiary_Active", "Tertiary"]
          and str(RF.HELP[1]) in t_def and int(RF.mode(UR)) == 0,
          "R review fix 8: bags.refillDefault=full -> a player who never picked gets Full inventory (page + tick); a picked Hotbar only stays")
    Cfg.REFILL_DEF = "off"
    check(int(RF.mode(UR3)) == 2 and int(RF.mode(UR)) == 0, "R review fix 8: bags.refillDefault=off -> off for players who never picked")
    Cfg.REFILL_DEF = "sideways"
    check(int(RF.mode(UR3)) == 0, "R review fix 8: an unknown default word reads as Hotbar only")
    Cfg.REFILL_DEF = "hotbar"
    ms_f.setInt(ItemC.UNKNOWN, OLD_MS)
    print("R. refill setting: default, save / load, unknown word kept, unreadable file untouched, page row (both views), clicks, next tick")
    builtins.print = _print
    last = {}
    order = []
    for name, ok_, bad_ in SEC:
        if name not in last:
            order.append(name)
        last[name] = (ok_, bad_)
    prev, parts = (0, 0), []
    for name in order:
        ok_, bad_ = last[name]
        parts.append("%s %d%s" % (name, ok_ - prev[0], (" (%d failed)" % (bad_ - prev[1])) if bad_ > prev[1] else ""))
        prev = (ok_, bad_)
    print("checks per section: " + ", ".join(parts))


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
    for p in (JAR, OLDJAR, ORACLEJAR, COOKJAR, ACCJAR, J78JAR):
        if not os.path.isfile(p):
            raise SystemExit("missing " + p + " (build it first)")
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"))
    if os.path.isdir(LIVE):
        shutil.copytree(LIVE, os.path.join(SCRATCH, "live"))      # READ ONLY copy of the live data
        print("copied live data (read only): %s" % LIVE)
    else:
        print("note: live data folder not found: %s" % LIVE)
    if os.path.isdir(LIVEACC):
        shutil.copytree(LIVEACC, os.path.join(SCRATCH, "liveacc"))      # READ ONLY copy (section L)
        print("copied live data (read only): %s" % LIVEACC)
    else:
        print("note: live SkyyAccessories data folder not found: %s" % LIVEACC)
    if os.path.isfile(LIVECOOK):
        os.makedirs(os.path.join(SCRATCH, "livecook"))
        shutil.copyfile(LIVECOOK, os.path.join(SCRATCH, "livecook", "cooking.properties"))      # READ ONLY copy
        print("copied the live cooking.properties (read only): %s" % LIVECOOK)
    else:
        print("note: live cooking.properties not found: %s" % LIVECOOK)
    env = dict(os.environ, TEMP=os.path.join(SCRATCH, "tmp"), TMP=os.path.join(SCRATCH, "tmp"))
    env.pop("JAVA_TOOL_OPTIONS", None)
    args = [sys.executable, os.path.abspath(__file__), "--child", "--dir", SCRATCH, "--jar", JAR, "--old", OLDJAR, "--oracle", ORACLEJAR,
            "--cook", COOKJAR, "--acc", ACCJAR]
    rc = subprocess.call(args, env=env, cwd=ROOT)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyySacks %s bare-JVM check: %s (exit code %d)%s" % (VERSION, "PASS" if rc == 0 else "FAIL", rc, "" if KEEP else " (scratch folder removed)"))
    sys.exit(rc)


if __name__ == "__main__":
    main()
