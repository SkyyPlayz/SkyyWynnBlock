"""Bare-JVM check for SkyySacks 0.7.12 (BENCHES AND INVENTORY CRAFTING USE THE BAGS - research/Bag-Craft-Link-Fix.md: the outbound packet filter,
the output-only mirror guard, the 300 ms refresh rules, PocketCraftWindow, the pre-craft filter, the live-mirror rule, the wording back, the
bench chest count fallback row), kept next to the build so the build report's claims can be re-run. The 0.7.11 harness carried forward:
A-H, J, K, L, M, P, Q, R, S, W prove what they proved (N's bench-pause cases became the live-mirror rule, R checks the 0.7.12 wording, B the
new row, I compares 0.7.11 vs 0.7.12); new T = packet mechanics, U = the filters through PacketAdapters + the pre-craft task, V = accounting,
X = pocket crafting, Y = the 300 ms link, Z = the item-conservation fuzz, O = the chest count fallback + BenchLink.stop().
REVIEW FIXES of the 0.7.12 review (all marked "review fix N" below): 1 the bags.pocketCraft off switch (B row / template / hand edits / kit
path, X live swaps by hook / link / hand edit + an open window declining, O start() with it off + nothing after stop(), R texts without the
inventory crafting claim); 2 declined benches get their close hook (T, Y, the fuzz's disconnects); 3 DELAYED-sync fuzz (Z) + the syncs
of preCraft's own-section branch (U), decline (V) and park (V) proven to be the ones that book; 4 unloaded item ids never offered (V; the
bare JVM's empty Item asset map knows the test ids through SkyyTestKnownMap).

    python SkyySacks/test_skyysacks_0.7.12.py [--jar <0.7.12 jar>] [--old <0.7.11 jar>] [--oracle <0.7.7 jar>] [--cook <SkyyCooking 0.1.3 jar>]
        [--acc <SkyyAccessories 0.5.2 jar>] [--live <Skyy_SkyySacks folder>] [--liveacc <Skyy_SkyyAccessories folder>]
        [--livecook <cooking.properties>] [--dir <scratch>] [--keep] [--zseeds <delayed-sync fuzz seeds, 40>] [--zsteps <steps each, 2500>]

Build first (python SkyySacks/build_skyysacks_0.7.12.py; the 0.7.11 / 0.7.8 / 0.7.7 jars, SkyyAccessories 0.5.2 and SkyyCooking 0.1.3 are
the built ones). The parent copies the live data folders and the live cooking.properties (read only; default: the "HUD mod" world's
mods/Skyy_SkyySacks, mods/Skyy_SkyyAccessories and mods/Skyy_SkyyCooking/cooking.properties) into the scratch folder and starts a child: a
fresh JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + the 0.7.12 jar + SkyyAccessories 0.5.2 + SkyyCooking 0.1.3 +
tools/javassist.jar, java.io.tmpdir / TEMP / TMP in the scratch folder). The 0.7.7 SackDefs (oracle) and the 0.7.11 SackDefs load from their
jars in their own class loaders. The engine's own classes do the work wherever a bare JVM allows: WindowManager.updateWindow /
updateWindows, PacketAdapters (registerOutbound / __handleOutbound / __handleInbound), the vanilla ExtraResources / UpdateWindow /
OpenWindow serializers, DelegateItemContainer + CombinedItemContainer, the window close event registry. Generated test classes: a recording
GamePacketHandler (its writePacket runs the outbound filters first, like PacketHandler.writePacket), a SimpleCraftingWindow that feeds fake
nearby chests when its section is invalid (like BenchWindow + CraftingManager.feedExtraResourcesSection), a PocketCraftWindow whose refill()
gets the player from a lookup (the game: the player's store on its world thread), BenchLink.PLAYERS = the PlayerRef -> Player lookup.
Checks:
  A  every 0.7.12 class (+ the 9 link classes), every SkyyCooking 0.1.3 class (J) and SkyyAccessories' Workbench tab classes (W) load and
     verify (-Xverify:all)
  B  the Server Setup rows (bags.cookedFood, bags.refill / bags.refillDefault, NEW bags.benchChests after them: bool, default off, live,
     template line, hand edits, the kit's set path on a copy of the live config; review fix 1: NEW bags.pocketCraft after it: bool, default
     ON, live, after= SackCfg.pocketChanged - no swap before start())
  C  classification of EVERY item id in Assets.zip + SkyyCooking items + pack Food_ ids + edge ids, switch off / on, cook:prefix off / on:
     homeOf == 0.7.7 catOf except Ingredient_Charcoal -> Smithing; catOf follows; AND == 0.7.11 for every id (none moved)
  D-H the cooked-food rule as 0.7.8 - 0.7.11 tested it (intake, retrieval, bag page, consumption, two starts on the live copies)
  I  class byte-compare 0.7.11 vs 0.7.12: exactly SackPool, SweepTask, BagMirror, CraftLinkTask, RefillPref, SacksPage, SackCfg, the plugin
     and the kit's CfgRows / CfgFn / CfgFile (two more rows) differ - each only in the expected members, + the 9 new link classes; every
     other class byte-identical (CraftPage included); assets: only the manifest version
  J  the Campfire tab line with the real SkyyCooking 0.1.3 (unchanged since 0.7.9; the contrast check still uses the 0.7.8 jar)
  K  charcoal (0.7.10) still: auto-pickup into a Smithing bag / the Omni, Deposit all on the Smithing tab, withdraw, save + reload
  W  the Workbench tab on real engine objects (tools/skyywbtab.py harness_checks, unchanged since 0.7.10)
  L  the two mods' start sequences alone and together in both orders on fresh scratch copies of their live data folders, twice each
     (SkyySacks also starts + stops the bench / pocket link): every file byte-identical, no new file
  M  kept counts (0.7.11, unchanged)
  N  refill in each mode (0.7.11) + 0.7.12 THE LIVE-MIRROR RULE: a bench that took 30 from the mirror is booked BEFORE the refill reads the
     pool, the mirror is trimmed to the pool right after, the refill no longer waits for an open bench; a withdraw after unbooked bench use
     never hands out what the bench used; a sweep never trims
  P  refill + sweep never fight (0.7.11); Q bags add up (0.7.11); S relog / profile switch / busy profile (0.7.11)
  T  packet mechanics with the recording PacketHandler: a valid section + updateWindow sends no list (the 0.7.10 bug), invalidate sends
     one and the filter merges chests + bags (vanilla order first); the section ends Combined{chests, guard}, valid, with the merged list;
     the packet's own ItemQuantity objects are never edited; a null list is left alone; serialize round trips (UpdateWindow + OpenWindow);
     start() twice = still one filter; no bag / no settled key -> vanilla only (+ its close hook, its record gone at close); Diagram /
     Structural / window 0 untouched; ProcessingBench fed; always false, errors caught
  U  PacketAdapters.__handleOutbound with the registered filter merges and never blocks; another PacketHandler kind is untouched; inbound
     craft / tier-upgrade packets are never blocked; preCraft (the 2nd click in the same tick) re-feeds + attaches, books first; on its OWN
     section it books a pocket craft's unbooked use of the shared mirror before topping up
  V  accounting: pool {Stick 100, Rubble 50} -> attach -> remove [Stick 4, Rubble 2] through Combined{inventory, section} -> sync {96, 48},
     a second sync books nothing; inserts through the guard / Combined{full inventory, section} refused; an OLD combined container across a
     rebuild still books; park books (use after the last 300 ms run) then empties (and the old container then finds nothing); merge; fit;
     a declined refresh (bag put away) books the bench's unbooked use; an unloaded item id is never offered (bench list, mirror, /craft)
  X  pocket crafting: the supplier swap in start() + restore in stop() (prev none, replaced later), PocketCraftWindow (type, data, starts
     invalid, no world thread = empty + still invalid), refill with bags / no key / no bag, a craft takes the inventory first then the bags,
     the refresh books once, inserts refused, the shared mirror with a bench (union of wanted inputs, no refresh ping-pong), close hooks;
     bags.pocketCraft off / on live (after= hook, the 300 ms backstop, a hand edit through reload): vanilla supplier back / ours in, an
     open pocket window refreshed and declining, no double swap
  Y  the 300 ms link: quiet when nothing changed; a shown change -> one refresh, 1 s rate limit; a change above the 4-stack view -> none;
     carried bags changed / all gone (synced + emptied) / back; invalid windows never read; a foreign rebuild; a window the filter never saw;
     prune; park + retire on a profile switch; a quick switch before the task ran (the next attach retires); no window -> dropped
  Z  item-conservation fuzz (review fix 3: 40 seeds x 2,500 steps with DELAYED syncing + 4 seeds x 1,250 synced after each step): bench
     crafts (with / without the pre-craft task), pocket crafts, timed crafts (units started, completed, cancelled mid-way with the vanilla
     refund), withdraws, Deposit all, 2 s ticks (sweep + refill), uses, pickups, bag drops / pick-ups, profile switches + settling, packets,
     link runs, window opens / closes, inserts into the guard, disconnects (every window closed), filter failures, bags.pocketCraft flips,
     late syncs - after EVERY step, with NO extra sync: every container slot <= its slot table, the tables of a key <= its pool, every item
     id conserved once the unbooked use is taken off (inventory + both pools + chests + ground - unbooked = start + picked up - used),
     outputs = successful crafts; each seed ends with a disconnect: exact totals, no mirror and no record left; proof every path ran
  O  Server Setup bags.benchChests: off = vanilla, on = 1 nearby chest when bags are linked (open packet + window data + updates), real
     chests / no bag untouched; BenchLink.stop() deregisters both filters and restores the vanilla pocket supplier; review fix 1: no swap
     after stop(), start() with bags.pocketCraft off keeps the vanilla pocket window (benches still linked)
  0.7.11 REVIEW FIXES stay proven (B rows 8, N 13, S 4 / 10, R wording now the 0.7.12 claim).
Not testable without the game (UNVERIFIED): the client honouring the list for pocket crafting (window 0) and with 0 nearby chests (the O
fallback), the page on a client, real pickups / block placing / crafting packets / world threads, the engine's events firing.
Nothing is deployed and nothing under AppData is written. Default scratch folder tools/dev/scratch/sacks0712/run (deleted unless --keep).
Exit code 1 on any failure.
"""
import os, sys, re, shutil, subprocess, zipfile, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyywbtab as WB   # 0.7.10: the Workbench tab tables + harness_checks
VERSION, OLD, ORACLE_V, COOK_V, ACC_V = "0.7.12", "0.7.11", "0.7.7", "0.1.3", "0.5.2"
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


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "sacks0712", "run")))
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
    print("A. loaded + verified %d classes (-Xverify:all; SkyySacks 0.7.12 + SkyyCooking 0.1.3 for J + SkyyAccessories 0.5.2 tab classes for W)" % len(names))
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
    Defs10 = JClass(Cls.forName("com.skyy.sacks.SackDefs", True, l10))   # 0.7.12: the 0.7.11 (OLD) rules, to prove no id moved

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
    # review fix 4 (0.7.12): BagMirror.rebuild now skips an id the Item asset map does not know (ProcBench.item == null). The empty map
    # knows none, so the ids the mirror tests pool are made KNOWN here: getAsset answers Item.UNKNOWN for them (= what ItemStack.getItem
    # already falls back to - stack sizes unchanged) and null for every other id, exactly as before (J, W and the classification see no
    # change). An id outside KNOWN plays an item of a removed pack mod.
    DAMN = "com.hypixel.hytale.assetstore.map.DefaultAssetMap"
    kmap = jp.makeClass("com.hypixel.hytale.assetstore.map.SkyyTestKnownMap", jp.get(DAMN))
    kmap.addField(JClass("javassist.CtField").make("public static final java.util.HashSet KNOWN = new java.util.HashSet();", kmap))
    kmap.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyTestKnownMap() { super(); }", kmap))
    kmap.addMethod(JClass("javassist.CtNewMethod").make(
        "public com.hypixel.hytale.assetstore.JsonAsset getAsset(Object key) { if (key != null && KNOWN.contains(key)) "
        "return com.hypixel.hytale.server.core.asset.type.item.config.Item.UNKNOWN; return super.getAsset(key); }", kmap))
    KMap = JClass(kmap.toClass(JClass(DAMN).class_))
    for kid_ in ("Ingredient_Stick", "Rubble_Stone", "Wood_Oak_Trunk", "Ore_Copper", "Ingredient_Fibre", "Rock_Stone", "Ingredient_Bone_Fragment",
                 "Food_Bread", "Plant_Crop_Wheat_Item"):
        KMap.KNOWN.add(kid_)
    fm.set(store, KMap())
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
        # 0.7.12: bags.benchChests (bench chest count fallback) through the same kit set path
        r8 = fn.apply(OA(["set", "bags.benchChests", "true", None, "console", "yes", "console"]))
        CfgPub.flush()
        kt4 = open(os.path.join(kd, "config.properties"), "rb").read().decode("latin-1").replace("\r\n", "\n")
        check(r8 is not None and str(r8[0]) == "ok" and bool(Cfg.CHEST_FIX) is True and "\nbags.benchChests=true" in kt4,
              "B 0.7.12: kit set bags.benchChests=true: field on, line written (%s)" % (None if r8 is None else str(r8[2])))
        Cfg.MTIME = -1
        Cfg.CHEST_FIX = False
        Cfg.reload()
        check(bool(Cfg.CHEST_FIX) is True, "B 0.7.12: SackCfg.reload reads the kit-written bags.benchChests line")
        r9 = fn.apply(OA(["set", "bags.benchChests", "false", None, "console", "yes", "console"]))
        CfgPub.flush()
        check(str(r9[0]) == "ok" and bool(Cfg.CHEST_FIX) is False, "B 0.7.12: and back off")
        # 0.7.12 review fix 1: bags.pocketCraft through the same kit set path; its after= hook (SackCfg.pocketChanged -> BenchLink.pocketApply)
        # never swaps a window before BenchLink.start() (the bare JVM has no pocket crafting registration: nothing may appear)
        crwt_b = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.Window").CLIENT_REQUESTABLE_WINDOW_TYPES
        pk_b = JClass("com.hypixel.hytale.protocol.packets.window.WindowType").PocketCrafting
        r10 = fn.apply(OA(["set", "bags.pocketCraft", "false", None, "console", "yes", "console"]))
        CfgPub.flush()
        kt5 = open(os.path.join(kd, "config.properties"), "rb").read().decode("latin-1").replace("\r\n", "\n")
        check(r10 is not None and str(r10[0]) == "ok" and bool(Cfg.POCKET_CRAFT) is False and "\nbags.pocketCraft=false" in kt5
              and not crwt_b.containsKey(pk_b) and not bool(J("BenchLink").POCKET_ON),
              "B review fix 1: kit set bags.pocketCraft=false: field off, line written, the after= hook swaps nothing before start() (%s)"
              % (None if r10 is None else str(r10[2])))
        Cfg.MTIME = -1
        Cfg.POCKET_CRAFT = True
        Cfg.reload()
        check(bool(Cfg.POCKET_CRAFT) is False and not crwt_b.containsKey(pk_b), "B review fix 1: SackCfg.reload reads the kit-written bags.pocketCraft line")
        r11 = fn.apply(OA(["set", "bags.pocketCraft", "true", None, "console", "yes", "console"]))
        CfgPub.flush()
        check(str(r11[0]) == "ok" and bool(Cfg.POCKET_CRAFT) is True and not crwt_b.containsKey(pk_b), "B review fix 1: and back on")
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
    # 0.7.12: the bench chest count fallback row (research/Bag-Craft-Link-Fix.md risk 2): right after bags.refillDefault, bool, default
    # false, live, the template's commented line, hand edits through SackCfg.reload (linkKeys)
    ci_ = keys.index("bags.benchChests") if "bags.benchChests" in keys else -1
    check(ci_ == keys.index("bags.refillDefault") + 1 and str(Rows.TYPES[ci_]) == "bool" and str(Rows.DEFS[ci_]) == "false"
          and str(Rows.LABELS[ci_]) == "Bench chest count fallback" and str(Rows.CATS[ci_]) == "bags"
          and str(Rows.FLAGS[ci_]).split(",") == ["live"] and 0 < len(str(Rows.HELPS[ci_])) <= 100 and len(str(Rows.LABELS[ci_])) <= 40,
          "B 0.7.12: row bags.benchChests (bool, default false, live, Bags group, after bags.refillDefault): %r" % (str(Rows.HELPS[ci_]) if ci_ >= 0 else None))
    check("#bags.benchChests=false" in tpl and tpl.index("#bags.refillDefault=hotbar") < tpl.index("#bags.benchChests=false")
          and "\nbags.benchChests" not in tpl, "B 0.7.12: the template carries the commented #bags.benchChests=false after the refill lines")
    for val_, want_ in (("true", True), ("on", True), ("false", False), ("maybe", False), ("1", True)):
        open(cf, "w", encoding="utf8").write(tpl + "bags.benchChests=%s\n" % val_)
        Cfg.MTIME = -1
        Cfg.reload()
        check(bool(Cfg.CHEST_FIX) is want_, "B 0.7.12: file bags.benchChests=%s -> %s" % (val_, want_))
    open(cf, "w", encoding="utf8").write(tpl)
    Cfg.MTIME = -1
    Cfg.reload()
    check(bool(Cfg.CHEST_FIX) is False, "B 0.7.12: the template alone -> chest fallback off")
    # 0.7.12 review fix 1: the pocket crafting swap's off switch - right after bags.benchChests, bool, default TRUE, live, the template's
    # commented line, hand edits through SackCfg.reload (linkKeys) - the way an owner turns it off without joining
    pi_ = keys.index("bags.pocketCraft") if "bags.pocketCraft" in keys else -1
    check(pi_ == ci_ + 1 and str(Rows.TYPES[pi_]) == "bool" and str(Rows.DEFS[pi_]) == "true"
          and str(Rows.LABELS[pi_]) == "Bags in inventory crafting" and str(Rows.CATS[pi_]) == "bags"
          and str(Rows.FLAGS[pi_]).split(",") == ["live"] and 0 < len(str(Rows.HELPS[pi_])) <= 100 and len(str(Rows.LABELS[pi_])) <= 40
          and str(Rows.BAFTER[pi_]).endswith(".SackCfg.pocketChanged"),
          "B review fix 1: row bags.pocketCraft (bool, default true, live, Bags group, after bags.benchChests, after= SackCfg.pocketChanged): %r"
          % ([str(x[pi_]) for x in (Rows.TYPES, Rows.DEFS, Rows.LABELS, Rows.CATS, Rows.FLAGS, Rows.HELPS, Rows.BAFTER)] + [pi_, ci_] if pi_ >= 0 else None))
    check("#bags.pocketCraft=true" in tpl and tpl.index("#bags.benchChests=false") < tpl.index("#bags.pocketCraft=true")
          and "\nbags.pocketCraft" not in tpl, "B review fix 1: the template carries the commented #bags.pocketCraft=true after the chest fallback line")
    for val_, want_ in (("false", False), ("off", False), ("true", True), ("maybe", True), ("0", False), ("on", True)):
        open(cf, "w", encoding="utf8").write(tpl + "bags.pocketCraft=%s\n" % val_)
        Cfg.MTIME = -1
        Cfg.reload()
        check(bool(Cfg.POCKET_CRAFT) is want_, "B review fix 1: file bags.pocketCraft=%s -> %s" % (val_, want_))
    open(cf, "w", encoding="utf8").write(tpl)
    Cfg.MTIME = -1
    Cfg.reload()
    check(bool(Cfg.POCKET_CRAFT) is True, "B review fix 1: the template alone -> bags in inventory crafting on (the default)")
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
    # against the OLD (0.7.11) rules directly - no id changed bag (homeOf and catOf, both switch states)
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
            check(not moved10, "C: vs %s homeOf / catOf (prefix %s, switch %s): no id moved: %s" % (OLD, prefix, sw, moved10[:6]))
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

    # ---------------- I. class byte-compare 0.7.11 vs 0.7.12 (+ assets)
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

    def slot(c_):     # each try / catch stores its Throwable in a local slot: an inserted one shifts the next locals
        return [re.sub(r"^([ai](?:store|load))(?:_\d| \d+)$", r"\1", l) for l in canon(c_)]

    zo, zn = zipfile.ZipFile(OLDJAR), zipfile.ZipFile(JAR)
    co = dict((n, zo.read(n)) for n in zo.namelist() if n.endswith(".class"))
    cn = dict((n, zn.read(n)) for n in zn.namelist() if n.endswith(".class"))
    NEWN = ("MirrorGuard", "LinkRec", "BenchLink", "MirrorClose", "CraftPacketFilter", "CraftInFilter", "PreCraftTask", "PocketCraftWindow",
            "PocketSupplier")
    NEWC = ["com/skyy/sacks/%s.class" % c for c in NEWN]
    check(sorted(cn) == sorted(list(co) + NEWC), "I: the 0.7.11 classes + the 9 link classes (%d)" % len(cn))
    same = sorted(n for n in co if cn.get(n) == co[n])
    diff = sorted(n for n in co if n in cn and co[n] != cn[n])
    SW = "Lcom/hypixel/hytale/server/core/entity/entities/Player;"
    HM = "Ljava/util/HashMap;"
    IQD = "[Lcom/hypixel/hytale/protocol/ItemQuantity;"
    UCBD = "Lcom/hypixel/hytale/server/core/ui/builder/UICommandBuilder;"
    UEBD = "Lcom/hypixel/hytale/server/core/ui/builder/UIEventBuilder;"
    WDR = "m withdraw(%sLjava/lang/String;Ljava/lang/String;I)I" % SW
    RFL = "m refill(%sLjava/lang/String;ILjava/util/Set;Ljava/util/Set;%s)I" % (SW, HM)
    ITM_ = "m items(%sLjava/lang/String;Ljava/util/UUID;)[I" % SW
    NBG = "m buildNoBag(%s%sLjava/lang/String;%sLjava/util/UUID;)V" % (UCBD, SW, HM)
    RRW = "m refillRow(%s%sI)V" % (UCBD, UEBD)
    REB = "m rebuild(%sLjava/util/Set;)Ljava/lang/String;" % HM
    ADD = "m add(Ljava/lang/String;Ljava/lang/String;J)V"
    EXPECT = {
        # the change counter, the negative-clamp warning, PENDQ gone
        "SackPool": {"f CHG", "f PENDQ", "m <clinit>()V", ADD, "m chg(Ljava/lang/String;)J", "m forgetSeen(Ljava/util/UUID;)V"},
        # the live-mirror rule in withdraw + refill; the bench pause (benchFed + PENDQ) gone from items
        "SweepTask": {WDR, RFL, ITM_, "m benchFed(%sLjava/lang/String;)Z" % SW},
        # the guard, the content version, owns / merge / fit, beforeTake / afterTake; retireOther / park moved to BenchLink
        "BagMirror": {"f combined", "f vanilla", "f guard", "f ver", "m <init>(Ljava/lang/String;)V", REB, "m empty()V",
                      "m afterTake(Ljava/lang/String;Ljava/lang/String;)I", "m beforeTake(Ljava/lang/String;)I", "m fit(Ljava/lang/String;)I",
                      "m merge(%s%s)%s" % (IQD, IQD, IQD), "m owns(Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;)Z",
                      "m sumInto(Ljava/util/LinkedHashMap;%s)V" % IQD,
                      "m park(Lcom/hypixel/hytale/server/core/entity/entities/player/windows/WindowManager;Ljava/util/List;Ljava/util/UUID;)I",
                      "m retireOther(Ljava/util/UUID;Ljava/lang/String;)Lcom/skyy/sacks/BagMirror;"},
        "CraftLinkTask": {"f DBG", "m <clinit>()V", "m run()V"},
        "RefillPref": {"f OFFSRV", "f HELPB", "f OFFSRVB", "m <clinit>()V"},  # the help lines (wording back) + review fix 1: the pocket-off lines
        "SacksPage": {NBG, RRW},                                             # the no-bag hint + the inlined OFFSRV constant
        "SackCfg": {"f CHEST_FIX", "f POCKET_CRAFT", "m <clinit>()V", "m linkKeys(Ljava/util/Properties;Z)V", "m reload()V",
                    "m pocketChanged(Ljava/lang/String;)V"},                 # + review fix 1: bags.pocketCraft
        "SkyySacksPlugin": {"m setup()V", "m start()V", "m shutdown()V"},
        "CfgFile": None, "CfgRows": None, "CfgFn": None,                     # the kit: VERSION, the new row (checked below)
    }
    report = []
    for n in diff:
        cname = n[:-6].replace("/", ".")
        short = cname.rsplit(".", 1)[1]
        mo, mn = members(OLDJAR, cname), members(JAR, cname)
        changed = sorted(kk for kk in set(mo) | set(mn) if canon(mo.get(kk)) != canon(mn.get(kk)))
        cpool = sorted(kk for kk in set(mo) & set(mn) if mo.get(kk) != mn.get(kk) and kk not in changed)
        report.append("%s: %s%s" % (short, ", ".join(c.split("(")[0] for c in changed) or "(constant pool only)",
                                    (" | constant pool only: " + ", ".join(c.split("(")[0] for c in cpool)) if cpool else ""))
        allowed = EXPECT.get(short, "missing")
        if short == "CfgFile":
            co_, cn_ = canon(mo.get("m <clinit>()V")), canon(mn.get("m <clinit>()V"))
            pairs = [] if co_ is None or cn_ is None or len(co_) != len(cn_) else [(a_, b_) for a_, b_ in zip(co_, cn_) if a_ != b_]
            check(changed == ["m <clinit>()V"] and pairs and all(pq_ == ("bipush 13", "bipush 15") for pq_ in pairs),
                  "I: CfgFile differs only in its per-row array sizes (13 -> 15 rows: + bags.benchChests, bags.pocketCraft): %s %s" % (changed, pairs[:3]))
            continue
        if short == "CfgRows":
            check(set(changed) <= {"m <clinit>()V", "f VERSION", "m header()[Ljava/lang/Object;"}
                  and all(canon(mo[c].replace(OLD, VERSION)) == canon(mn[c]) for c in changed if c.startswith("m header")),
                  "I: CfgRows: only the table initialiser, VERSION and header() (VERSION only) differ: %s" % changed)
            lo_ = UCL(JArray(URL)([File(OLDJAR).toURI().toURL(), File(B.SERVER_JAR).toURI().toURL()]),
                      JClass("java.lang.ClassLoader").getPlatformClassLoader())
            RO = Cls.forName(PKG + "CfgRows", True, lo_)

            def arr(cls_, name_):
                v_ = cls_.getField(name_).get(None)
                return None if v_ is None else [str(x) for x in v_]
            ko = arr(RO, "KEYS")
            at_ = ko.index("bags.refillDefault") + 1
            bad_ = []
            for name_ in ("KEYS", "LABELS", "CATS", "TYPES", "DEFS", "MINS", "MAXS", "OPTS", "UNITS", "FLAGS", "HELPS", "BK", "BF", "BFT",
                          "BCONF", "BENT", "BSC", "BCLS", "BNAME", "BFK", "BCK", "BAFTER", "BCHECK", "BSEP", "VTYPES"):
                ao, an = arr(RO, name_), arr(Rows.class_, name_)
                if ao is None or an is None or len(an) != len(ao) + 2 or an[:at_] != ao[:at_] or an[at_ + 2:] != ao[at_:]:
                    bad_.append(name_)
            kn = arr(Rows.class_, "KEYS")
            check(not bad_ and kn[at_] == "bags.benchChests" and kn[at_ + 1] == "bags.pocketCraft",
                  "I: CfgRows tables = 0.7.11's + bags.benchChests + bags.pocketCraft right after bags.refillDefault, entry by entry (differ: %s)" % bad_)
            do = arr(RO, "DL0")
            dn = arr(Rows.class_, "DL0")
            ins = do.index("#bags.refillDefault=hotbar") + 1
            check(dn[:ins] == do[:ins] and dn[ins + 6:] == do[ins:] and dn[ins + 2] == "#bags.benchChests=false" and dn[ins + 5] == "#bags.pocketCraft=true"
                  and len(dn) == len(do) + 6,
                  "I: CfgRows template lines = 0.7.11's + the 3 chest-fallback + the 3 pocket-crafting lines after #bags.refillDefault=hotbar")
            check(str(RO.getField("VERSION").get(None)) == OLD and str(Rows.VERSION) == VERSION, "I: CfgRows VERSION %s -> %s" % (OLD, VERSION))
            continue
        if allowed is None:
            # the config kit inlines VERSION: every changed member differs only in that string
            okk = all(mo.get(c) is not None and mn.get(c) is not None and canon(mo[c].replace(OLD, VERSION)) == canon(mn[c]) for c in changed)
            check(okk, "I: config kit class %s differs only in VERSION %s -> %s: %s" % (short, OLD, VERSION, changed))
            continue
        extra = sorted(set(changed) - (allowed if allowed != "missing" else set()))
        check(allowed != "missing" and not extra, "I: class %s differs only in the expected members (unexpected: %s)" % (short, extra))
        if short == "SackPool":
            check("SackPool.CHG" in mn[ADD] and "would go below zero" in mn[ADD] and subseq(canon(mo[ADD]), canon(mn[ADD]))
                  and "PENDQ" not in mn.get("m forgetSeen(Ljava/util/UUID;)V", "") and "f PENDQ" not in mn and "f CHG" in mn,
                  "I: SackPool.add = 0.7.11's + the below-zero warning + the CHG bump; PENDQ gone")
        if short == "SweepTask":
            for keep_m in ("m caps(Lcom/hypixel/hytale/server/core/inventory/Inventory;)%s" % HM, "m sweep(%sLjava/lang/String;Ljava/lang/String;Z%s)I" % (SW, HM),
                           "m sweepLeft(Lcom/hypixel/hytale/server/core/inventory/Inventory;Ljava/lang/String;%s)Ljava/util/HashSet;" % HM, "m run()V"):
                check(mo.get(keep_m) is not None and canon(mo.get(keep_m)) == canon(mn.get(keep_m)), "I: SweepTask.%s unchanged" % keep_m.split("(")[0][2:])
            check(subseq(canon(mo[WDR]), canon(mn[WDR])) and "BagMirror.beforeTake" in mn[WDR] and "BagMirror.afterTake" in mn[WDR]
                  and mn[WDR].index("BagMirror.beforeTake") < mn[WDR].index("SackPool.get")
                  and mn[WDR].index("SackPool.add") < mn[WDR].index("BagMirror.afterTake"),
                  "I: SweepTask.withdraw = 0.7.11's + beforeTake before the pool is read + afterTake right after the pool move")
            check(subseq(canon(mo[RFL]), canon(mn[RFL])) and "BagMirror.beforeTake" in mn[RFL] and "BagMirror.afterTake" in mn[RFL],
                  "I: SweepTask.refill = 0.7.11's + the live-mirror rule")
            check("benchFed" in mo[ITM_] and "benchFed" not in mn[ITM_] and "PENDQ" not in mn[ITM_] and "m benchFed(%sLjava/lang/String;)Z" % SW not in mn,
                  "I: SweepTask.items: the 0.7.11 bench pause (benchFed + PENDQ) is gone")
        if short == "BagMirror":
            for keep_m in ("m sync()I", "m quantities()%s" % IQD, "m syncAll()I", "m holds()Z", "m of(Ljava/lang/String;)Lcom/skyy/sacks/BagMirror;",
                           "m wantedFor(Ljava/lang/Object;)Ljava/util/Set;"):
                check(mo.get(keep_m) is not None and canon(mo.get(keep_m)) == canon(mn.get(keep_m)), "I: BagMirror.%s unchanged" % keep_m.split("(")[0][2:])
            check(subseq(canon(mo[REB]), canon(mn[REB])) and "BagMirror.ver" in mn[REB] and "ProcBench.item" in mn[REB],
                  "I: BagMirror.rebuild = 0.7.11's + the content version + (review fix 4) the unloaded-item skip")
        if short == "SkyySacksPlugin":
            so, sn = mo["m setup()V"], mn["m setup()V"]
            new_l = [l for l in ldcs(sn) if l not in ldcs(so)]
            gone_l = [l for l in ldcs(so) if l not in ldcs(sn)]
            check(len(new_l) == 1 and new_l[0].startswith("[SkyySacks] %s ready" % VERSION) and len(gone_l) == 1
                  and canon(so.replace(gone_l[0], new_l[0])) == canon(sn),
                  "I: SkyySacksPlugin.setup = 0.7.11's with only the ready line changed")
            check(subseq(slot(mo["m start()V"]), slot(mn["m start()V"])) and "BenchLink.start" in mn["m start()V"] and "WbTab.start" in mn["m start()V"],
                  "I: SkyySacksPlugin.start = 0.7.11's (the Workbench tab) + BenchLink.start()")
            sh = mn["m shutdown()V"]
            check(subseq(slot(mo["m shutdown()V"]), slot(sh)) and sh.index("SackPool.CLOSED") < sh.index("BenchLink.stop") < sh.index("BagMirror.syncAll"),
                  "I: SkyySacksPlugin.shutdown = 0.7.11's + BenchLink.stop() right after the shutdown latch, before the final mirror sync")
        if short == "SackCfg":
            ro_, rn_ = mo["m reload()V"], mn["m reload()V"]
            new_r = [l for l in ldcs(rn_) if l not in ldcs(ro_)]
            check(subseq(canon(ro_), canon(rn_)) and "SackCfg.linkKeys" in rn_ and "#bags.benchChests=false" in rn_ and "#bags.pocketCraft=true" in rn_
                  and all("enchChests" in l or "chest" in l.lower() or "ocketCraft" in l or "inventory (pocket) crafting" in l or "inventory crafting misbehaves" in l for l in new_r),
                  "I: SackCfg.reload = 0.7.11's + the chest fallback / pocket crafting template lines + linkKeys; new strings %s" % [x[:50] for x in new_r])
        if short == "CraftLinkTask":
            check("BenchLink.link" in mn["m run()V"] and "updateWindow" not in mn["m run()V"] and "setValid" not in mn["m run()V"]
                  and "updateWindow" in mo["m run()V"] and "f DBG" not in mn,
                  "I: CraftLinkTask.run hands the work to BenchLink.link (no setValid / updateWindow of its own any more)")
    check(sorted(r.split(":")[0] for r in report) == sorted(EXPECT), "I: exactly %s changed: %s" % (", ".join(sorted(EXPECT)), diff))
    print("I. classes byte-identical: %d of %d (%s); new: %s" % (len(same), len(co), OLD, ", ".join(NEWN)))
    print("   classes that differ: %d" % len(diff))
    for r in report:
        print("     " + r)
    ao_ = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    an_ = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    adiff = sorted(n for n in set(ao_) | set(an_) if ao_.get(n) != an_.get(n))
    check(adiff == ["manifest.json"], "I: assets: only the manifest differs (items, lang, qualities, the tab icon unchanged): %s" % adiff)
    mo_, mn_ = json.loads(ao_["manifest.json"]), json.loads(an_["manifest.json"])
    check(mo_["Version"] == OLD and mn_["Version"] == VERSION and mn_["Name"] == VERSION + " SkyySacks"
          and dict(mo_, Version=0, Name=0) == dict(mn_, Version=0, Name=0), "I: manifest: only Name / Version -> %s" % VERSION)
    print("   assets that differ: manifest.json only (%d asset files)" % len(an_))

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
          "K: charcoal: homeOf / catOf Smithing (as in 0.7.10 / %s)" % OLD)
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
        J("BenchLink").start()                       # 0.7.12: start() also starts the bench / pocket link (no file involved)
        J("BenchLink").stop()
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
    # 0.7.12 THE LIVE-MIRROR RULE (replaces the 0.7.11 refill pause while a bench is open - research/Bag-Craft-Link-Fix.md invariant 7): a
    # bench / pocket window holding the bag mirror no longer pauses the refill. What the bench already took out of the mirror is booked
    # BEFORE the refill reads the pool (BagMirror.beforeTake = sync) and the mirror is trimmed to the pool right after the move
    # (BagMirror.afterTake = fit, never booked) - the mirror never offers more than the pool holds, nothing can be used twice
    WMC = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager")
    wm_field = jfield(PLA.class_, "windowManager")
    wins_field = jfield(WMC.class_, "windows")

    def held(m_, iid):          # what the mirror offers of an item (its slot table; = the container after a sync)
        return sum(int(m_.slotQty[s_]) for s_ in range(36) if m_.slotIds[s_] is not None and str(m_.slotIds[s_]) == iid)

    def cont_has(m_, iid):      # what the mirror's container really holds of an item
        n_ = 0
        for s_ in range(36):
            it_ = m_.cont.getItemStack(JShort(s_))
            if it_ is not None and not it_.isEmpty() and str(it_.getItemId()) == iid:
                n_ += int(it_.getQuantity())
        return n_

    def bench_take(m_, iid, n):  # a bench craft takes n of an item out of the mirror THROUGH ITS GUARD (the only way a section reaches it)
        lst_ = JClass("java.util.ArrayList")()
        lst_.add(JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")(iid, None, None, n, None))
        tx_ = m_.guard.removeMaterials(lst_, True, True, True)
        return bool(tx_.succeeded())

    k, p, hot, sto, bp = n_setup(0, pool_n=100, name="n7")
    put(hot, 0, ST, 64)
    Pool.keep(k, ST, 64)
    tick(p, k, UN)
    mb = Mirror.of(k)
    mb.rebuild(Sweep.caps(p.getInventory()))
    off0 = held(mb, ST)
    took = bench_take(mb, ST, 30)               # the bench crafts with 30 stone out of the mirror (not booked yet)
    use(hot, 0, 40)
    bu = totals(p, k)                            # inventory 24 + pool 100 (the bench's 30 are not booked yet)
    r = tick(p, k, UN)                           # refill: books the 30 (pool 70), tops 24 -> 64 (40 out: 30 left), trims the mirror to 30
    check(off0 == 100 and took and r == (0, 40) and at(hot, 0) == (ST, MAXS) and pool_counts(k).get(ST) == 30
          and total_of(p, k, ST) == bu[ST] - 30 and held(mb, ST) <= 30 and cont_has(mb, ST) == held(mb, ST) and System.identityHashCode(Mirror.MIRRORS.get(k)) == System.identityHashCode(mb),
          "N 0.7.12 live mirror: a bench took 30 -> booked BEFORE the refill (pool 100 - 30 - 40 = 30), the mirror trimmed to %d <= the pool, "
          "the refill no longer waits: %s" % (held(mb, ST), r))
    use(hot, 0, 50)
    r2 = tick(p, k, UN)
    check(r2 == (0, 30) and ST not in pool_counts(k) and held(mb, ST) == 0 and cont_has(mb, ST) == 0 and not bench_take(mb, ST, 1),
          "N 0.7.12 live mirror: the last 30 refilled -> the mirror offers no stone any more; a bench craft finds none: %s" % (r2,))
    # a withdraw (bag page click) with unbooked bench use: the same rule - the 20 the bench used are booked first, only the rest comes out
    k, p, hot, sto, bp = n_setup(0, pool_n=50, name="n7b")
    mw_ = Mirror.of(k)
    mw_.rebuild(Sweep.caps(p.getInventory()))
    tk = bench_take(mw_, ST, 20)
    bw = totals(p, k)
    got_w = int(Sweep.withdraw(p, k, ST, 64))
    check(tk and got_w == 30 and ST not in pool_counts(k) and held(mw_, ST) == 0 and inv_counts(p).get(ST) == 30
          and total_of(p, k, ST) == bw[ST] - 20,
          "N 0.7.12 live mirror: withdraw after the bench used 20 of 50 -> 30 come out (never the 20 already used), mirror trimmed to 0")
    # a pickup (the sweep puts items IN) never trims: the mirror keeps offering what the pool holds
    k, p, hot, sto, bp = n_setup(0, pool_n=40, name="n7c")
    mp_ = Mirror.of(k)
    mp_.rebuild(Sweep.caps(p.getInventory()))
    put(sto, 0, ST, 12)
    tick(p, k, UN)
    check(held(mp_, ST) == 40 and pool_counts(k).get(ST) == 52, "N 0.7.12: a sweep adds to the pool, the mirror (40) stays within it (52)")
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
          "metadata stack untouched, the live-mirror rule (bench use booked first, mirror trimmed), max stack 1, every case counted")

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

    # ============================================================================ 0.7.12 sections (research/Bag-Craft-Link-Fix.md)
    import random as _rnd
    from jpype import JLong
    Link, LRec, MG = J("BenchLink"), J("LinkRec"), J("MirrorGuard")
    PocketW, PocketSup, CPF, CIF, PreT = J("PocketCraftWindow"), J("PocketSupplier"), J("CraftPacketFilter"), J("CraftInFilter"), J("PreCraftTask")
    MERSc = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.MaterialExtraResourcesSection")
    IQc = JClass("com.hypixel.hytale.protocol.ItemQuantity")
    ERc = JClass("com.hypixel.hytale.protocol.ExtraResources")
    UWc = JClass("com.hypixel.hytale.protocol.packets.window.UpdateWindow")
    OWc = JClass("com.hypixel.hytale.protocol.packets.window.OpenWindow")
    WTc = JClass("com.hypixel.hytale.protocol.packets.window.WindowType")
    SWAc = JClass("com.hypixel.hytale.protocol.packets.window.SendWindowAction")
    CRAc = JClass("com.hypixel.hytale.protocol.packets.window.CraftRecipeAction")
    TUAc = JClass("com.hypixel.hytale.protocol.packets.window.TierUpgradeAction")
    PAc = JClass("com.hypixel.hytale.server.core.io.adapter.PacketAdapters")
    CICc = JClass("com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer")
    ICc = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    DICc = JClass("com.hypixel.hytale.server.core.inventory.container.DelegateItemContainer")
    FTc = JClass("com.hypixel.hytale.server.core.inventory.container.filter.FilterType")
    EICc = JClass("com.hypixel.hytale.server.core.inventory.container.EmptyItemContainer")
    MQc = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    ALc = JClass("java.util.ArrayList")
    WinC = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.Window")
    SyncReg = JClass("com.hypixel.hytale.event.SyncEventBusRegistry")
    WCE = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.Window$WindowCloseEvent")
    ABc, JOc = JClass("java.util.concurrent.atomic.AtomicBoolean"), JClass("com.google.gson.JsonObject")
    IntJ = JClass("java.lang.Integer")
    Arena = JClass("java.lang.foreign.Arena")
    CRWT = WinC.CLIENT_REQUESTABLE_WINDOW_TYPES
    win_logger = jfield(WinC.class_, "LOGGER").get(None)
    close_reg_f = jfield(WinC.class_, "closeEventRegistry")
    jfield(JClass("com.hypixel.hytale.server.core.asset.type.item.config.FieldcraftCategory").class_, "ASSET_MAP").set(
        None, JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")())     # a bare JVM has no Fieldcraft categories (the pocket ctor reads them)
    idh = System.identityHashCode
    jp.appendClassPath(JAR)
    # a recording PacketHandler: a GamePacketHandler whose writePacket runs the outbound filters first - exactly PacketHandler.writePacket -
    # and records instead of sending
    GPHN = "com.hypixel.hytale.server.core.io.handlers.game.GamePacketHandler"
    trc = jp.makeClass("com.hypixel.hytale.server.core.io.handlers.game.SkyyTestRec", jp.get(GPHN))
    trc.addField(CtF.make("public static final java.util.ArrayList LOG = new java.util.ArrayList();", trc))
    trc.addMethod(CtM.make("public boolean writePacket(com.hypixel.hytale.protocol.ToClientPacket p, boolean cache) { "
                           "if (com.hypixel.hytale.server.core.io.adapter.PacketAdapters.__handleOutbound(this, p)) return false; LOG.add(p); return true; }", trc))
    RecC = JClass(trc.toClass(JClass(GPHN).class_))
    # a bench window: a SimpleCraftingWindow whose getExtraResourcesSection() feeds fake nearby chests when the section is invalid - exactly
    # what BenchWindow does through CraftingManager.feedExtraResourcesSection (output-only chest container + the per-item list, valid)
    SCWN = "com.hypixel.hytale.builtin.crafting.window.SimpleCraftingWindow"
    MERSN = "com.hypixel.hytale.server.core.entity.entities.player.windows.MaterialExtraResourcesSection"
    IQN = "com.hypixel.hytale.protocol.ItemQuantity"
    tbc = jp.makeClass("com.hypixel.hytale.builtin.crafting.window.SkyyTestBench", jp.get(SCWN))
    tbc.addField(CtF.make("public com.hypixel.hytale.server.core.inventory.container.ItemContainer chests;", tbc))
    tbc.addField(CtF.make("public int feeds;", tbc))
    tbc.addMethod(CtM.make(("public %s[] chestList() { java.util.LinkedHashMap m = new java.util.LinkedHashMap(); short cap = this.chests.getCapacity(); "
                            "for (short s = 0; s < cap; s++) { com.hypixel.hytale.server.core.inventory.ItemStack it = this.chests.getItemStack(s); "
                            "if (it == null || it.isEmpty()) continue; Integer c = (Integer) m.get(it.getItemId()); "
                            "m.put(it.getItemId(), Integer.valueOf((c == null ? 0 : c.intValue()) + it.getQuantity())); } "
                            "%s[] out = new %s[m.size()]; java.util.Iterator i = m.entrySet().iterator(); int k = 0; "
                            "while (i.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) i.next(); out[k++] = new %s((String) e.getKey(), ((Integer) e.getValue()).intValue()); } "
                            "return out; }") % (IQN, IQN, IQN, IQN), tbc))
    tbc.addMethod(CtM.make(("public %s getExtraResourcesSection() { %s s = super.getExtraResourcesSection(); "
                            "if (!s.isValid()) { this.feeds++; s.setItemContainer(this.chests); s.setExtraMaterials(chestList()); s.setValid(true); } return s; }")
                           % (MERSN, MERSN), tbc))
    TBench = JClass(tbc.toClass(JClass(SCWN).class_))
    # the pocket window with its refill() reaching the player through a lookup (production: the player's store on its world thread)
    tpc = jp.makeClass("com.skyy.sacks.SkyyTestPocket", jp.get("com.skyy.sacks.PocketCraftWindow"))
    tpc.addField(CtF.make("public static java.util.function.Function PL;", tpc))
    tpc.addConstructor(CtC.make("public SkyyTestPocket() { super(); }", tpc))
    tpc.addMethod(CtM.make("public void refill() { com.hypixel.hytale.server.core.universe.PlayerRef pr = getPlayerRef(); if (pr == null || PL == null) return; "
                           "refillFor((com.hypixel.hytale.server.core.entity.entities.Player) PL.apply(pr), pr.getUuid()); }", tpc))
    TPocket = JClass(tpc.toClass(PocketW.class_))
    WMC = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager")
    wm_field = jfield(PLA.class_, "windowManager")
    wins_field = jfield(WMC.class_, "windows")
    PLAYERS_ = {}

    def wire(u, storage=(), hotbar=(), backpack=()):
        pp = player(storage, hotbar, backpack)
        prr = mkpr(u)
        rc = us.allocateInstance(RecC.class_)
        jfield(RecC.class_, "playerRef").set(rc, prr)
        jfield(PR.class_, "packetHandler").set(prr, rc)
        wmm = WMC()
        wmm.init(prr)
        wm_field.set(pp, wmm)
        PLAYERS_[str(u)] = pp
        return pp, prr, wmm
    look = Fn(lambda a: PLAYERS_.get(str(a.getUuid())))
    TPocket.PL = look

    def new_bench(raw_=None, items=(), chests=0):
        b_ = us.allocateInstance(TBench.class_)
        for nm_, val_ in (("closeEventRegistry", SyncReg(win_logger, WCE.class_)), ("isDirty", ABc(False)), ("needRebuild", ABc(False)),
                          ("windowType", WTc.BasicCrafting), ("windowData", JOc()), ("extraResourcesSection", MERSc())):
            jfield(TBench.class_, nm_).set(b_, val_)
        if raw_ is None:
            raw_ = SIC(JShort(18))
            for (iid, q) in items:
                raw_.addItemStack(IS(iid, q))
        if chests == 0 and not items and raw_.isEmpty():
            b_.chests = EICc.INSTANCE                # CraftingManager.feedExtraResourcesSection: no chest around -> EmptyItemContainer.INSTANCE
        else:
            d_ = DICc(raw_)                          # ...else output-only delegates of the chests
            d_.setGlobalFilter(FTc.ALLOW_OUTPUT_ONLY)
            b_.chests = d_
        b_.getData().addProperty("nearbyChestCount", IntJ.valueOf(chests))
        return b_, raw_

    def open_bench(prr, wmm, b_, wid=7):     # WindowManager.openWindow: register, onOpen (the vanilla feed), the OpenWindow packet
        wins_field.get(wmm).put(JInt(wid), b_)
        b_.setId(wid)
        b_.init(prr, wmm)
        sec_ = b_.getExtraResourcesSection()
        pk_ = OWc(wid, WTc.BasicCrafting, str(b_.getData().toString()), None, sec_.toPacket())
        prr.getPacketHandler().write(pk_)
        return pk_

    def close_bench(wmm, b_, wid=7):         # WindowManager.closeWindow: removed, onClose0 (refund done by the caller), then the close event
        wins_field.get(wmm).remove(JInt(wid))
        close_reg_f.get(b_).dispatchFor(None).dispatch(WCE())

    def open_pocket(prr, wmm):               # clientOpenWindow (window 0): registered, onOpen marks it dirty, the update goes out
        pw_ = TPocket()
        wins_field.get(wmm).put(JInt(0), pw_)
        pw_.setId(0)
        pw_.init(prr, wmm)
        pw_.invalidateExtraResources()
        wmm.updateWindows()
        return pw_

    def close_pocket(wmm, pw_):
        wins_field.get(wmm).remove(JInt(0))
        pw_.onClose0(None, None)

    def inv_c(pp):                           # InventoryComponent.getCombined(BACKPACK_STORAGE_HOTBAR)
        iv_ = pp.getInventory()
        return CICc(JArray(ICc)([iv_.getBackpack(), iv_.getStorage(), iv_.getHotbar()]))

    def mats(spec, times=1):
        l_ = ALc()
        for (iid, q) in spec:
            l_.add(MQc(iid, None, None, q * times, None))
        return l_

    def snapc(c_):
        out_ = {}
        for i_ in range(int(c_.getCapacity())):
            it_ = c_.getItemStack(JShort(i_))
            if it_ is None or it_.isEmpty():
                continue
            out_[str(it_.getItemId())] = out_.get(str(it_.getItemId()), 0) + int(it_.getQuantity())
        return out_

    def craft_from(comb_, spec, times):      # CraftingManager.craftItem: all or nothing, counted
        l_ = mats(spec, times)
        b0 = snapc(comb_)
        ok_ = bool(comb_.canRemoveMaterials(l_)) and bool(comb_.removeMaterials(l_, True, True, True).succeeded())
        b1 = snapc(comb_)
        removed_ = dict((i_, b0[i_] - b1.get(i_, 0)) for i_ in b0 if b0[i_] > b1.get(i_, 0))
        return ok_, removed_

    def bench_craft(pp, b_, spec, times=1):  # SimpleCraftingWindow.handleAction (instant)
        comb_ = CICc(JArray(ICc)([inv_c(pp), b_.getExtraResourcesSection().getItemContainer()]))
        res_ = craft_from(comb_, spec, times)
        b_.invalidateExtraResources()
        return res_

    def pocket_craft(pp, pw_, spec, times=1):   # PocketCraftWindow.handleAction (its craftContainer)
        res_ = craft_from(pw_.craftContainer(inv_c(pp)), spec, times)
        pw_.invalidateExtraResources()
        return res_

    def last_pkt():
        n_ = int(RecC.LOG.size())
        return RecC.LOG.get(n_ - 1) if n_ > 0 else None

    def resmap(er_):
        if er_ is None or er_.resources is None:
            return None
        return dict((str(x.itemId), int(x.quantity)) for x in er_.resources)

    def last_res():                          # the list of the last packet sent (None: no packet / no list) - a failing check never crashes
        lp_ = last_pkt()
        return None if lp_ is None else resmap(lp_.extraResources)

    def mirror_q(m_):
        return dict((str(x.itemId), int(x.quantity)) for x in m_.quantities())

    def held(m_, iid):
        return sum(int(m_.slotQty[s_]) for s_ in range(36) if m_.slotIds[s_] is not None and str(m_.slotIds[s_]) == iid)

    def mirror_ok(m_):                       # after a sync: the container = the slot table, and never more than the pool holds
        if m_ is None:
            return True
        m_.sync()
        pc_ = pool_counts(str(m_.key))
        tab_ = {}
        for s_ in range(36):
            if m_.slotIds[s_] is None:
                continue
            it_ = m_.cont.getItemStack(JShort(s_))
            act_ = 0 if it_ is None or it_.isEmpty() else int(it_.getQuantity())
            if act_ != int(m_.slotQty[s_]):
                return False
            tab_[str(m_.slotIds[s_])] = tab_.get(str(m_.slotIds[s_]), 0) + act_
        return all(v_ <= pc_.get(i_, 0) for i_, v_ in tab_.items())

    def link_reset():
        Mirror.MIRRORS.clear()
        Mirror.LASTKEY.clear()
        Link.RECS.clear()
        Link.WARNED.clear()
        RecC.LOG.clear()
        for k_ in list(bridge.keySet()):
            if str(k_).startswith("profile:"):
                bridge.remove(k_)
        Pool.CHANGEDAT.clear()
        Pool.SEENKEY.clear()
        Pool.SEENEPOCH.clear()
        Pool.UNKNOWN.clear()
    STK, RUB, OAK, ORE_C, FIB = "Ingredient_Stick", "Rubble_Stone", "Wood_Oak_Trunk", "Ore_Copper", "Ingredient_Fibre"
    # the vanilla pocket window registration CraftingPlugin.setup makes (a bare JVM has none): a stand-in start() must replace and stop()
    # restore (only its identity matters here)
    van_sup = JClass("java.lang.Object")()
    CRWT.put(WTc.PocketCrafting, van_sup)
    Link.PLAYERS = look
    Link.start()
    started_ok = Link.OUT is not None and Link.IN is not None and bool(Link.POCKET_ON) and CRWT.get(WTc.PocketCrafting) is not None \
        and str(CRWT.get(WTc.PocketCrafting).getClass().getName()) == "com.skyy.sacks.PocketSupplier"

    # ---------------- T. packet mechanics (a recording PacketHandler): research doc 2 + fix A
    check(started_ok, "T: BenchLink.start(): outbound + inbound filters registered, the pocket crafting supplier is ours")
    fresh_pools(os.path.join(SCRATCH, "pools-t"))
    link_reset()
    UT = mkuuid(0x71)
    kT = str(UT)
    Pool.add(kT, STK, 100)
    Pool.add(kT, RUB, 50)
    p, prT, wmT = wire(UT, hotbar=[(MIN_L, 1), (FOR_S, 1)])
    b, rawT = new_bench(items=[(STK, 3), (OAK, 5)], chests=1)
    wins_field.get(wmT).put(JInt(7), b)
    b.setId(7)
    b.init(prT, wmT)
    b.getExtraResourcesSection()
    RecC.LOG.clear()
    wmT.updateWindow(b)
    p1 = last_pkt()
    check(p1 is not None and p1.extraResources is None and b.isValid() and int(b.feeds) == 1,
          "T: a VALID section + updateWindow sends no extra-materials list (the 0.7.10 bug: valid + update = the client never learnt the bags)")
    b.invalidateExtraResources()
    RecC.LOG.clear()
    wmT.updateWindows()                       # PlayerSendInventorySystem: the dirty window goes out, the vanilla code re-feeds the chests
    p2 = last_pkt()
    rm2 = resmap(p2.extraResources) if p2 is not None else None
    secT = b.getExtraResourcesSection()
    mT = Mirror.MIRRORS.get(kT)
    check(rm2 == {STK: 103, OAK: 5, RUB: 50} and [str(x.itemId) for x in p2.extraResources.resources] == [STK, OAK, RUB],
          "T: invalidate -> the update carries a list; the filter merged chests (3 sticks, 5 logs) + bags (100 sticks, 50 rubble), vanilla order first: %s" % rm2)
    check(mT is not None and secT.isValid() and mT.owns(secT.getItemContainer()) and idh(Link.peel(secT.getItemContainer())) == idh(b.chests)
          and resmap(secT.toPacket()) == rm2 and int(b.feeds) == 2,
          "T: the section now holds Combined{the vanilla chests, the guard}, valid, its list = the merged one (no extra vanilla feed)")
    Link.start()                              # a second start (a plugin started again): the first registration is undone first
    hp2 = UWc(7, "{}", None, ERc(JArray(IQc)([IQc(STK, 3), IQc(OAK, 5)])))
    prT.getPacketHandler().writeNoCache(hp2)
    check(resmap(hp2.extraResources) == rm2 and Link.OUT is not None and str(CRWT.get(WTc.PocketCrafting).getClass().getName()) == "com.skyy.sacks.PocketSupplier"
          and idh(Link.POCKET_PREV) == idh(van_sup),
          "T: start() twice -> still ONE outbound filter (the bags merged once, not twice: %s); the vanilla pocket supplier still kept" % resmap(hp2.extraResources))
    RecC.LOG.clear()
    RecC.LOG.add(p2)
    va = JArray(IQc)([IQc(STK, 3), IQc(OAK, 5)])
    hp = UWc(7, "{}", None, ERc(va))
    prT.getPacketHandler().writeNoCache(hp)
    check([(str(x.itemId), int(x.quantity)) for x in va] == [(STK, 3), (OAK, 5)] and resmap(hp.extraResources) == rm2
          and int(RecC.LOG.size()) == 2, "T: the packet's own ItemQuantity objects are never edited (a new merged array is set); the packet still went out")
    pn = UWc(7, "{}", None, None)
    prT.getPacketHandler().writeNoCache(pn)
    check(pn.extraResources is None and idh(last_pkt()) == idh(pn), "T: a packet without a list is left alone and still sent")
    for pk_ in (p2,):
        n_ = int(pk_.computeSize())
        seg_ = Arena.ofAuto().allocate(n_ + 16)
        pk_.serialize(seg_, 0)
        back_ = UWc.toObject(seg_)
        check(resmap(back_.extraResources) == rm2 and int(back_.id) == 7, "T: the filtered UpdateWindow survives a serialize round trip: %s" % resmap(back_.extraResources))
    b8, raw8 = new_bench(items=[(FIB, 4)], chests=1)
    po = open_bench(prT, wmT, b8, 8)
    rmo = resmap(po.extraResources)
    seg_ = Arena.ofAuto().allocate(int(po.computeSize()) + 16)
    po.serialize(seg_, 0)
    bo_ = OWc.toObject(seg_)
    check(rmo == {FIB: 4, STK: 100, RUB: 50} and resmap(bo_.extraResources) == rmo and str(bo_.windowType) == "BasicCrafting",
          "T: OpenWindow (a second bench): merged chests + bags, survives a serialize round trip: %s" % rmo)
    wins_field.get(wmT).remove(JInt(8))
    Link.closed(UT, b8)
    # no bag carried / no settled key -> vanilla only
    UT2 = mkuuid(0x72)
    Pool.add(str(UT2), STK, 40)
    p_nb, pr_nb, wm_nb = wire(UT2, storage=[(OAK, 2)])
    bnb, _r = new_bench(items=[(STK, 2)], chests=1)
    pnb = open_bench(pr_nb, wm_nb, bnb)
    rec_nb = Link.recOf(UT2, bnb, False)
    check(resmap(pnb.extraResources) == {STK: 2} and rec_nb is not None and not bool(rec_nb.attached) and str(rec_nb.why) == "no bag carried"
          and not Mirror.MIRRORS.containsKey(str(UT2)), "T: no bag carried -> the vanilla list only (declined, no mirror made)")
    # review fix 2: the DECLINED bench got its close hook too - its close (a disconnect closes every window; prune only runs for online
    # players) drops its record and window
    check(rec_nb.reg is not None, "T review fix 2: the declined bench has its close hook")
    close_bench(wm_nb, bnb)
    check(Link.recOf(UT2, bnb, False) is None and not Link.RECS.containsKey(UT2),
          "T review fix 2: the declined bench closed -> its record (and the window it holds) is gone, no 300 ms prune needed")
    bridge.put("profile:fn:key", Fn(lambda a: JString("unsettled")))     # SkyyProfiles present, no epoch for the player -> settledKey null
    p_us, pr_us, wm_us = wire(mkuuid(0x73), hotbar=[(MIN_L, 1), (FOR_S, 1)])
    bus, _r = new_bench(items=[(STK, 2)], chests=1)
    pus = open_bench(pr_us, wm_us, bus)
    check(resmap(pus.extraResources) == {STK: 2} and str(Link.recOf(mkuuid(0x73), bus, False).why) == "profile not settled"
          and Link.recOf(mkuuid(0x73), bus, False).reg is not None,
          "T: no settled profile key -> the vanilla list only (review fix 2: close hook on this declined bench too)")
    link_reset()
    Link.PLAYERS = look
    # a Diagram / Structural bench and the pocket window id 0 are never touched by the filter
    DIAG = us.allocateInstance(JClass("com.hypixel.hytale.builtin.crafting.window.DiagramCraftingWindow").class_)
    STRU = us.allocateInstance(JClass("com.hypixel.hytale.builtin.crafting.window.StructuralCraftingWindow").class_)
    PROC = us.allocateInstance(JClass("com.hypixel.hytale.builtin.crafting.window.ProcessingBenchWindow").class_)
    check(not bool(Link.isBench(DIAG)) and not bool(Link.isBench(STRU)) and bool(Link.isBench(PROC)) and bool(Link.isBench(b))
          and bool(Link.isPocket(TPocket())) and not bool(Link.isBench(TPocket())),
          "T: the link feeds SimpleCraftingWindow + ProcessingBenchWindow only (Diagram / Structural use their own slots); the pocket window is its own")
    wins_field.get(wmT).put(JInt(9), DIAG)
    pd_ = UWc(9, "{}", None, ERc(JArray(IQc)([IQc(STK, 1)])))
    p0_ = UWc(0, "{}", None, ERc(JArray(IQc)([IQc(STK, 7)])))
    prT.getPacketHandler().writeNoCache(pd_)
    prT.getPacketHandler().writeNoCache(p0_)
    check(resmap(pd_.extraResources) == {STK: 1} and resmap(p0_.extraResources) == {STK: 7},
          "T: a Diagram bench packet and a window-0 packet keep their lists (the pocket window fills its own)")
    wins_field.get(wmT).remove(JInt(9))
    check(not bool(CPF().test(prT, p2)) and not bool(CPF().test(prT, pn)) and not bool(CPF().test(None, None)),
          "T: the outbound filter always returns false (true would drop the packet)")
    RuntimeExc = JClass("java.lang.IllegalStateException")

    def boom(a):
        raise RuntimeExc("boom")
    Link.PLAYERS = Fn(boom)
    pb_ = UWc(7, "{}", None, ERc(JArray(IQc)([IQc(STK, 3)])))
    check(not bool(CPF().test(prT, pb_)) and resmap(pb_.extraResources) == {STK: 3} and Link.WARNED.containsKey("filter"),
          "T: an error inside the filter is caught (logged once), the packet goes out unchanged")
    Link.PLAYERS = look
    print("T. packet mechanics: valid + update = no list, invalidate = a merged list, OpenWindow merged, round trips, vanilla arrays untouched, "
          "no bag / no key / Diagram / window 0 left vanilla, always false")

    # ---------------- U. the filters through PacketAdapters (registered by start()) + the pre-craft task
    link_reset()
    Link.PLAYERS = look
    fresh_pools(os.path.join(SCRATCH, "pools-u"))
    UU = mkuuid(0x81)
    kU = str(UU)
    Pool.add(kU, STK, 64)
    p, prU, wmU = wire(UU, hotbar=[(FOR_S, 1)])
    bU, rawU = new_bench(items=[(OAK, 2)], chests=1)
    wins_field.get(wmU).put(JInt(7), bU)
    bU.setId(7)
    bU.init(prU, wmU)
    bU.getExtraResourcesSection()
    pkU = UWc(7, "{}", None, bU.getExtraResourcesSection().toPacket())
    blocked = bool(PAc.__handleOutbound(prU.getPacketHandler(), pkU))
    check(not blocked and resmap(pkU.extraResources) == {OAK: 2, STK: 64},
          "U: PacketAdapters.__handleOutbound with the registered filter: not blocked, the list merged: %s" % resmap(pkU.extraResources))
    other = us.allocateInstance(JClass("com.hypixel.hytale.server.core.io.handlers.InitialPacketHandler").class_)
    pkO = UWc(7, "{}", None, ERc(JArray(IQc)([IQc(OAK, 2)])))
    check(not bool(PAc.__handleOutbound(other, pkO)) and resmap(pkO.extraResources) == {OAK: 2},
          "U: a handler that is not a GamePacketHandler: the player filter is not called, the packet is untouched")
    for act_, nm_ in ((CRAc("Recipe_Test", 1), "craft"), (TUAc(), "tier upgrade"), (None, "no action")):
        sw_ = SWAc(7, act_) if act_ is not None else SWAc()
        check(not bool(PAc.__handleInbound(prU.getPacketHandler(), sw_)), "U: inbound %s action: never blocked (no world in a bare JVM: nothing queued)" % nm_)
    check(not bool(CIF().test(prU, SWAc(0, CRAc("Recipe_Test", 1)))) and not bool(CIF().test(prU, pkU)),
          "U: the inbound filter ignores window 0 and every other packet, always false")
    # the pre-craft task's work (it runs on the world thread before the vanilla handler)
    mU = Mirror.MIRRORS.get(kU)
    okc, remc = bench_craft(p, bU, [(STK, 10)])       # a first craft: through the section (ours), then invalidated
    check(okc and remc == {STK: 10} and not bU.isValid(), "U: a bench craft takes 10 sticks through the section and invalidates it")
    feeds0 = int(bU.feeds)
    did = bool(Link.preCraft(p, UU, 7))               # a second click in the same tick: the section is invalid -> re-feed + attach
    secU = bU.getExtraResourcesSection()
    check(did and secU.isValid() and mU.owns(secU.getItemContainer()) and int(bU.feeds) == feeds0 + 1 and pool_counts(kU).get(STK) == 54
          and held(mU, STK) == 54 and resmap(secU.toPacket()) == {OAK: 2, STK: 54},
          "U: preCraft on an invalid section: the vanilla re-feed + the mirror attached (the 10 booked first: 54 offered) - the 2nd click sees the bags")
    okc2, remc2 = bench_craft(p, bU, [(STK, 50)])
    check(okc2 and remc2 == {STK: 50}, "U: so the second craft (50 sticks) succeeds from the bags")
    bU.getExtraResourcesSection()                      # (vanilla handler of a later click: re-fed, not ours)
    did2 = bool(Link.preCraft(p, UU, 7))
    check(did2 and pool_counts(kU).get(STK) == 4 and held(mU, STK) == 4, "U: a not-ours valid section is attached too (50 booked: 4 left)")
    did3 = bool(Link.preCraft(p, UU, 7))
    check(not did3 and mU.owns(bU.getExtraResourcesSection().getItemContainer()), "U: preCraft on our own section only books + tops up (returns false)")
    check(not bool(Link.preCraft(p, UU, 9)) and not bool(Link.preCraft(p, UU, 0)), "U: preCraft ignores a window that is not open / window 0")
    # review fix 3: the sync in preCraft's OWN-section branch is the one that books. A pocket craft took 5 bag sticks from the SHARED mirror
    # while the bench's section stayed valid + ours; the pre-craft check of the next bench click must book them before it tops up
    link_reset()
    Link.PLAYERS = look
    fresh_pools(os.path.join(SCRATCH, "pools-u2"))
    UU2 = mkuuid(0x82)
    kU2 = str(UU2)
    Pool.add(kU2, STK, 40)
    pU2, prU2, wmU2 = wire(UU2, hotbar=[(FOR_S, 1)])
    bU2, _r = new_bench(items=[], chests=0)
    open_bench(prU2, wmU2, bU2)
    pwU2 = open_pocket(prU2, wmU2)
    mU2 = Mirror.MIRRORS.get(kU2)
    shared_ = bool(mU2.owns(pwU2.getExtraResourcesSection().getItemContainer())) and bool(mU2.owns(bU2.getExtraResourcesSection().getItemContainer()))
    okp2, remp2 = pocket_craft(pU2, pwU2, [(STK, 5)])
    stk_u2, cont_u2 = pool_counts(kU2).get(STK), cont_has(mU2, STK)    # read first: the pocket window's own refill would book them
    check(shared_ and okp2 and remp2 == {STK: 5} and stk_u2 == 40 and cont_u2 == 35 and bU2.isValid()
          and mU2.owns(bU2.getExtraResourcesSection().getItemContainer()),
          "U review fix 3: a pocket craft took 5 bag sticks out of the shared mirror (not booked yet: pool %s, mirror holds %s); the bench "
          "section is still valid + ours" % (stk_u2, cont_u2))
    did4 = bool(Link.preCraft(pU2, UU2, 7))
    check(not did4 and pool_counts(kU2).get(STK) == 35 and held(mU2, STK) == 35 and cont_has(mU2, STK) == 35,
          "U review fix 3: preCraft on the bench's own section books those 5 first (pool 35), then tops the mirror up to exactly the pool")
    close_pocket(wmU2, pwU2)
    close_bench(wmU2, bU2)
    check(pool_counts(kU2).get(STK) == 35 and Mirror.MIRRORS.get(kU2) is None and not Link.RECS.containsKey(UU2),
          "U review fix 3: both closed -> nothing more booked (35), the mirror dropped, no record left")
    link_reset()
    Link.PLAYERS = None
    pkR = UWc(7, "{}", None, ERc(JArray(IQc)([IQc(OAK, 2)])))
    prU.getPacketHandler().writeNoCache(pkR)
    check(resmap(pkR.extraResources) == {OAK: 2}, "U: without the harness lookup the filter needs the player's own store (not in a bare JVM): packet untouched")
    Link.PLAYERS = look
    print("U. filters: __handleOutbound merges + never blocks, other handlers untouched, inbound never blocks; preCraft re-feeds + attaches, books")

    # ---------------- V. accounting (research doc test plan): exactly-once booking, the guard, old containers, park, merge, fit
    link_reset()
    Link.PLAYERS = look
    fresh_pools(os.path.join(SCRATCH, "pools-v"))
    UV = mkuuid(0x91)
    kV = str(UV)
    Pool.add(kV, STK, 100)
    Pool.add(kV, RUB, 50)
    p, prV, wmV = wire(UV, hotbar=[(MIN_L, 1), (FOR_S, 1)])
    bV, rawV = new_bench(items=[], chests=0)
    open_bench(prV, wmV, bV)
    mV = Mirror.MIRRORS.get(kV)
    secV = bV.getExtraResourcesSection()
    check(mV is not None and idh(secV.getItemContainer()) == idh(mV.guard) and resmap(secV.toPacket()) == {STK: 100, RUB: 50},
          "V: no chests -> the section gets the bare guard; list = the pool {Stick 100, Rubble 50}")
    combV = CICc(JArray(ICc)([inv_c(p), secV.getItemContainer()]))
    okv, remv = craft_from(combV, [(STK, 4), (RUB, 2)], 1)
    c1 = int(mV.sync())
    c2 = int(mV.sync())
    check(okv and remv == {STK: 4, RUB: 2} and c1 == 6 and c2 == 0 and pool_counts(kV) == {STK: 96, RUB: 48},
          "V: remove [Stick 4, Rubble 2] through Combined{inventory, section} -> sync books {96, 48}; a second sync books nothing")
    before_g = mirror_q(mV)
    tg = mV.guard.addItemStack(IS(STK, 5))
    full = player(storage=[(ORE_C, 64)] * 36, hotbar=[(ORE_C, 64)] * 9, backpack=[(ORE_C, 64)] * 9)
    tf = CICc(JArray(ICc)([inv_c(full), secV.getItemContainer()])).addItemStack(IS(STK, 5))
    check(not bool(tg.succeeded()) and not bool(tf.succeeded()) and mirror_q(mV) == before_g and int(mV.sync()) == 0,
          "V: an insert through the guard is refused, and through Combined{full inventory, section} too - the mirror never takes items in")
    oldc = CICc(JArray(ICc)([inv_c(p), secV.getItemContainer()]))   # a queued timed job keeps the container of its queue time
    Pool.add(kV, STK, 20)
    v0 = int(mV.ver)
    mV.rebuild(Sweep.caps(p.getInventory()), Link.union(UV, kV))
    oko, remo = craft_from(oldc, [(STK, 3)], 1)
    c3 = int(mV.sync())
    check(int(mV.ver) == v0 + 1 and oko and remo == {STK: 3} and c3 == 3 and pool_counts(kV).get(STK) == 113,
          "V: an OLD combined container (a timed job's) across a rebuild still books exactly what it removes (96 + 20 - 3 = 113)")
    check(mirror_ok(mV), "V: after every step the mirror's container = its slot table and never exceeds the pool")
    # park (a profile switch settling): sync first, then empty, the window detached + asked to refresh. Review fix 3: the 8 rubble are used
    # AFTER the last settled 300 ms run (which books everything before it) - so park's own sync is the one that books them
    keyb = [kV]
    bridge.put("profile:fn:key", Fn(lambda a: JString(keyb[0])))
    bridge.put("profile:epoch:" + kV, LongJ.valueOf(1))
    check(str(Pool.settledKey(UV)) == kV, "V: profile baseline")
    Link.link(p, UV, wmV.getWindows(), JLong(1000))
    okp, remp = craft_from(oldc, [(RUB, 8)], 1)       # unbooked use right before the switch
    rub_unbooked = pool_counts(kV).get(RUB)
    bridge.put("profile:epoch:" + kV, LongJ.valueOf(2))
    keyb[0] = "v-other"
    Link.link(p, UV, wmV.getWindows(), JLong(1300))
    recV = Link.recOf(UV, bV, False)
    check(okp and remp == {RUB: 8} and rub_unbooked == 48 and pool_counts(kV).get(RUB) == 40 and not bool(mV.holds()) and not bV.isValid()
          and recV is not None and not bool(recV.attached),
          "V: park while the switch settles: the 8 rubble used after the last 300 ms run are booked BY PARK (48 -> 40), then the mirror "
          "emptied, the bench detached + refreshed")
    RecC.LOG.clear()
    wmV.updateWindows()
    check(resmap(last_pkt().extraResources) == {} and not bool(mV.owns(bV.getExtraResourcesSection().getItemContainer())),
          "V: the refresh while settling: vanilla only (no chests here: an empty list), nothing attached")
    okz, remz = craft_from(oldc, [(STK, 1)], 1)
    check(not okz, "V: the old container finds nothing in the emptied mirror (bags off while the switch settles)")
    link_reset()
    Link.PLAYERS = look
    mg_ = Mirror.merge(JArray(IQc)([IQc(STK, 3), IQc(OAK, 5), IQc("Zero", 0), None]), JArray(IQc)([IQc(STK, 100), IQc(RUB, 50)]))
    check([(str(x.itemId), int(x.quantity)) for x in mg_] == [(STK, 103), (OAK, 5), (RUB, 50)], "V: merge sums by id, vanilla order first, zeros / nulls skipped")
    # fit: trim one item to the pool (never booked)
    fresh_pools(os.path.join(SCRATCH, "pools-v2"))
    Pool.add("v2", STK, 200)
    mf = Mirror("v2")
    mf.rebuild(Sweep.caps(player(hotbar=[(FOR_S, 1)]).getInventory()))
    Pool.add("v2", STK, -150)
    gone = int(mf.fit(STK))
    check(held(mf, STK) == 50 and gone == 150 and pool_counts("v2").get(STK) == 50 and mirror_ok(mf),
          "V: fit trims the mirror to the pool (200 offered, pool 50 -> 150 taken off, nothing booked)")
    # review fix 3: the sync in DECLINE is the one that books - a bench craft used 7 bag sticks and the bag is put away before anything
    # else ran; the vanilla refresh of that bench is declined (no bag carried) and must book the 7 before it empties the mirror
    link_reset()
    Link.PLAYERS = look
    fresh_pools(os.path.join(SCRATCH, "pools-v3"))
    UV3 = mkuuid(0x93)
    kV3 = str(UV3)
    Pool.add(kV3, STK, 60)
    pV3, prV3, wmV3 = wire(UV3, hotbar=[(FOR_S, 1)])
    bV3, _r = new_bench(items=[], chests=0)
    open_bench(prV3, wmV3, bV3)
    mV3 = Mirror.MIRRORS.get(kV3)
    okd, remd = bench_craft(pV3, bV3, [(STK, 7)])
    pV3.getInventory().getHotbar().removeItemStackFromSlot(JShort(0), JInt(1))     # the Foraging bag put away
    stk_unbooked = pool_counts(kV3).get(STK)
    RecC.LOG.clear()
    wmV3.updateWindows()                                 # the crafted bench's vanilla refresh -> declined (no bag carried)
    recV3 = Link.recOf(UV3, bV3, False)
    check(okd and remd == {STK: 7} and stk_unbooked == 60 and pool_counts(kV3).get(STK) == 53 and not bool(mV3.holds()) and recV3 is not None
          and not bool(recV3.attached) and str(recV3.why) == "no bag carried" and last_res() == {},
          "V review fix 3: the bag put away right after a bench craft (7 sticks, not booked) -> the declined refresh books them (60 -> 53), "
          "then empties the mirror; the bench shows the vanilla list")
    close_bench(wmV3, bV3)
    check(pool_counts(kV3).get(STK) == 53 and not Link.RECS.containsKey(UV3), "V review fix 3: ...the bench closed: nothing booked twice (53)")
    # review fix 4: a pool entry whose item the Item asset map no longer knows (a pack mod removed while its items sat in a bag) is never
    # offered - not in the mirror, not in a bench's list, not to /craft; it stays in the pool untouched
    GONE = "Wood_Removedmod_Trunk"
    check(sget(Defs.homeOf(GONE)) == "Foraging" and not KMap.KNOWN.contains(GONE) and J("ProcBench").item(GONE) is None
          and J("ProcBench").item(OAK) is not None, "V review fix 4: (test setup: the id sorts into the Foraging bag; it is not a loaded item)")
    link_reset()
    Link.PLAYERS = look
    fresh_pools(os.path.join(SCRATCH, "pools-v4"))
    UV4 = mkuuid(0x94)
    kV4 = str(UV4)
    Pool.add(kV4, OAK, 12)
    Pool.add(kV4, GONE, 25)
    pV4, prV4, wmV4 = wire(UV4, hotbar=[(FOR_S, 1)])
    bV4, _r = new_bench(items=[], chests=0)
    po4 = open_bench(prV4, wmV4, bV4)
    mV4 = Mirror.MIRRORS.get(kV4)
    okg, remg = bench_craft(pV4, bV4, [(GONE, 1)])
    check(resmap(po4.extraResources) == {OAK: 12} and held(mV4, GONE) == 0 and cont_has(mV4, GONE) == 0 and held(mV4, OAK) == 12
          and not okg and pool_counts(kV4) == {OAK: 12, GONE: 25},
          "V review fix 4: an unloaded item id in the pool (25) is never offered - the bench list shows the 12 logs only, a craft cannot "
          "take it, the 25 stay in the pool")
    mg4 = Mirror("v4-craft")
    Pool.add("v4-craft", GONE, 9)
    Pool.add("v4-craft", STK, 3)
    mg4.rebuild(Sweep.caps(pV4.getInventory()), JClass("java.util.HashSet")(JClass("java.util.Arrays").asList(JArray(JString)([GONE]))))
    check(mirror_q(mg4) == {STK: 3}, "V review fix 4: the /craft mirror skips it too, even when a recipe wants it: %s" % mirror_q(mg4))
    close_bench(wmV4, bV4)
    link_reset()
    print("V. accounting: exactly-once booking, guard refuses inserts, old containers still book, park syncs then empties (park books), "
          "merge, fit, decline books, unloaded ids never offered")

    # ---------------- X. pocket crafting: the supplier swap + restore, PocketCraftWindow refill / craft / close
    ours = CRWT.get(WTc.PocketCrafting)
    check(str(ours.getClass().getName()) == "com.skyy.sacks.PocketSupplier" and idh(Link.POCKET_PREV) == idh(van_sup),
          "X: start() put PocketSupplier in Window.CLIENT_REQUESTABLE_WINDOW_TYPES and kept the vanilla supplier to restore")
    pwn = ours.get()
    check(str(pwn.getClass().getName()) == "com.skyy.sacks.PocketCraftWindow" and str(pwn.getType()) == "PocketCrafting"
          and "Fieldcraft" in str(pwn.getData()) and not bool(pwn.isValid()),
          "X: the supplier makes a PocketCraftWindow (window type PocketCrafting, the vanilla Fieldcraft data, its section starts invalid)")
    secn = pwn.getExtraResourcesSection()
    check(not bool(pwn.isValid()) and idh(secn.getItemContainer()) == idh(EICc.INSTANCE) and resmap(secn.toPacket()) == {},
          "X: off its world thread (no store) the real refill() does nothing - an empty container, still invalid (asked again later), no crash")
    Link.pocketStop()
    check(idh(CRWT.get(WTc.PocketCrafting)) == idh(van_sup) and not bool(Link.POCKET_ON), "X: pocketStop restores the vanilla supplier")
    Link.pocketStart()
    other_sup = JClass("java.lang.Object")()
    CRWT.put(WTc.PocketCrafting, other_sup)
    Link.pocketCheck()
    Link.pocketCheck()
    check(bool(Link.POCKET_WARNED), "X: another mod replacing the supplier later is noticed (warned once)")
    Link.pocketStop()
    check(idh(CRWT.get(WTc.PocketCrafting)) == idh(other_sup), "X: ...and stop() leaves that mod's supplier in place")
    CRWT.remove(WTc.PocketCrafting)
    Link.pocketStart()
    check(Link.POCKET_PREV is None and str(CRWT.get(WTc.PocketCrafting).getClass().getName()) == "com.skyy.sacks.PocketSupplier",
          "X: nothing registered before (no crafting plugin): ours is used anyway (warned)")
    Link.pocketStop()
    check(not CRWT.containsKey(WTc.PocketCrafting), "X: ...and stop() removes it again (nothing to restore)")
    CRWT.put(WTc.PocketCrafting, van_sup)
    Link.pocketStart()
    # the window: refill / craft / refresh / close
    link_reset()
    Link.PLAYERS = look
    fresh_pools(os.path.join(SCRATCH, "pools-x"))
    UX = mkuuid(0xA1)
    kX = str(UX)
    Pool.add(kX, OAK, 30)
    Pool.add(kX, FIB, 12)
    Pool.add(kX, RUB, 9)
    p, prX, wmX = wire(UX, storage=[(FIB, 2)], hotbar=[(FOR_S, 1)])
    RecC.LOG.clear()
    pw = open_pocket(prX, wmX)
    pkx = last_pkt()
    mX = Mirror.MIRRORS.get(kX)
    secX = pw.getExtraResourcesSection()
    check(pkx is not None and int(pkx.id) == 0 and resmap(pkx.extraResources) == {OAK: 30, FIB: 12} and mX is not None
          and idh(secX.getItemContainer()) == idh(mX.guard) and pw.isValid(),
          "X: pocket crafting opened: window 0 gets the Foraging bag items (30 logs, 12 fibre; no Mining bag = no rubble), container = the guard")
    okx, remx = pocket_craft(p, pw, [(FIB, 5), (OAK, 2)])
    check(okx and remx == {FIB: 5, OAK: 2} and inv_counts(p).get(FIB) is None and not pw.isValid(),
          "X: a pocket craft takes the inventory first (2 fibre), then the bags (3 fibre + 2 logs), and refreshes the window")
    RecC.LOG.clear()
    wmX.updateWindows()
    check(pool_counts(kX) == {OAK: 28, FIB: 9, RUB: 9} and resmap(last_pkt().extraResources) == {OAK: 28, FIB: 9} and mirror_ok(mX),
          "X: the refresh books the bag part once (28 logs, 9 fibre) and sends the new counts")
    fullp = player(storage=[(ORE_C, 64)] * 36, hotbar=[(ORE_C, 64)] * 9, backpack=[(ORE_C, 64)] * 9)
    tx_ = pw.craftContainer(inv_c(fullp)).addItemStack(IS(OAK, 4))
    check(not bool(tx_.succeeded()) and int(mX.sync()) == 0, "X: nothing can be put into pocket crafting's bag part (full inventory + guard refuse)")
    bridge.put("profile:fn:key", Fn(lambda a: JString("x-unsettled")))
    pw.invalidateExtraResources()
    pw.getExtraResourcesSection()
    recx = Link.recOf(UX, pw, False)
    check(idh(pw.getExtraResourcesSection().getItemContainer()) == idh(EICc.INSTANCE) and recx is not None and not bool(recx.attached)
          and not bool(mX.holds()), "X: no settled key -> an empty section (inventory only); the mirror it used is synced + emptied")
    link_reset()
    Link.PLAYERS = look
    pw.invalidateExtraResources()
    pw.getExtraResourcesSection()
    mX2 = Mirror.MIRRORS.get(kX)
    check(mX2 is not None and idh(pw.getExtraResourcesSection().getItemContainer()) == idh(mX2.guard), "X: settled again -> the bags are back")
    # pocket + bench share ONE mirror (one live mirror per key): rebuilt with the union of what both can use, no refresh ping-pong
    bX, rawX = new_bench(items=[(STK, 1)], chests=1)
    open_bench(prX, wmX, bX)
    secb = bX.getExtraResourcesSection()
    check(idh(Mirror.MIRRORS.get(kX)) == idh(mX2) and mX2.owns(secb.getItemContainer()) and mX2.owns(pw.getExtraResourcesSection().getItemContainer()),
          "X: a bench opened next to pocket crafting uses the same mirror")
    ra_ = Link.recOf(UX, pw, False)
    rb_ = Link.recOf(UX, bX, False)
    ra_.wanted = JClass("java.util.HashSet")(JClass("java.util.Arrays").asList(JArray(JString)([FIB])))
    rb_.wanted = JClass("java.util.HashSet")(JClass("java.util.Arrays").asList(JArray(JString)([OAK, STK])))
    un_ = sorted(str(x) for x in Link.union(UX, kX))
    check(un_ == sorted([FIB, OAK, STK]), "X: the shared mirror is rebuilt for the union of both windows' recipe inputs: %s" % un_)
    inv0 = []
    for t_ in range(8):
        Link.link(p, UX, wmX.getWindows(), JLong(10000 + 2000 * t_))
        inv0.append((bool(bX.isValid()), bool(pw.isValid())))
        wmX.updateWindows()
    check(all(x == (True, True) for x in inv0), "X: 8 link runs with nothing changing: neither window is refreshed (no ping-pong): %s" % inv0[:3])
    close_pocket(wmX, pw)
    check(idh(Mirror.MIRRORS.get(kX)) == idh(mX2) and Link.recOf(UX, pw, False) is None, "X: pocket crafting closed -> its record goes, the mirror stays (the bench uses it)")
    okb, remb = bench_craft(p, bX, [(OAK, 3)])
    close_bench(wmX, bX)
    check(okb and Mirror.MIRRORS.get(kX) is None and pool_counts(kX).get(OAK) == 25 and Link.recOf(UX, bX, False) is None
          and not Link.RECS.containsKey(UX),
          "X: the bench closed (close hook): its craft booked at once (25 logs), the last window dropped the mirror, no record left")
    # review fix 1: Server Setup bags.pocketCraft = the pocket crafting swap's OFF switch (live; also read from config.properties before start())
    link_reset()
    Link.PLAYERS = look
    fresh_pools(os.path.join(SCRATCH, "pools-x2"))
    UX2 = mkuuid(0xA2)
    kX2 = str(UX2)
    Pool.add(kX2, OAK, 30)
    pX2, prX2, wmX2 = wire(UX2, hotbar=[(FOR_S, 1)])
    RecC.LOG.clear()
    pw2 = open_pocket(prX2, wmX2)
    check(bool(Cfg.POCKET_CRAFT) and bool(Link.POCKET_ON) and last_res() == {OAK: 30},
          "X review fix 1: bags.pocketCraft on (the default): pocket crafting shows the bags")
    Cfg.POCKET_CRAFT = False
    Cfg.pocketChanged("bags.pocketCraft")               # the row's after= hook (Server Setup)
    check(not bool(Link.POCKET_ON) and idh(CRWT.get(WTc.PocketCrafting)) == idh(van_sup),
          "X review fix 1: switched off -> the vanilla pocket crafting supplier is back at once (the next inventory open is vanilla)")
    Link.link(pX2, UX2, wmX2.getWindows(), JLong(700000))
    check(not pw2.isValid(), "X review fix 1: the pocket window still open with the bags is refreshed by the 300 ms link")
    RecC.LOG.clear()
    wmX2.updateWindows()
    rx2 = Link.recOf(UX2, pw2, False)
    lpx2, mx2 = last_pkt(), Mirror.MIRRORS.get(kX2)
    check(lpx2 is not None and resmap(lpx2.extraResources) == {} and idh(pw2.getExtraResourcesSection().getItemContainer()) == idh(EICc.INSTANCE)
          and rx2 is not None and not bool(rx2.attached) and str(rx2.why) == "inventory crafting link off (bags.pocketCraft)"
          and pool_counts(kX2) == {OAK: 30} and mx2 is not None and not bool(mx2.holds()),
          "X review fix 1: ...it declines: an empty list, the inventory only, nothing booked, the mirror emptied")
    okx2, remx2 = pocket_craft(pX2, pw2, [(OAK, 1)])
    check(not okx2 and pool_counts(kX2) == {OAK: 30}, "X review fix 1: a pocket craft there cannot take a bag log any more")
    close_pocket(wmX2, pw2)
    Cfg.POCKET_CRAFT = True                             # back on WITHOUT the hook: the 300 ms link applies it (the backstop)
    Link.link(pX2, UX2, wmX2.getWindows(), JLong(702000))
    check(bool(Link.POCKET_ON) and str(CRWT.get(WTc.PocketCrafting).getClass().getName()) == "com.skyy.sacks.PocketSupplier"
          and idh(Link.POCKET_PREV) == idh(van_sup),
          "X review fix 1: back on (hook missed) -> the 300 ms link puts ours back; the vanilla supplier is still the one to restore")
    # a hand edit picked up by SackCfg.reload (linkKeys; not the first load) applies it at once - the owner's way without joining
    xcf = os.path.join(SCRATCH, "cfg-x", "config.properties")
    os.makedirs(os.path.dirname(xcf), exist_ok=True)
    open(xcf, "w", encoding="utf8").write("bags.pocketCraft=false\n")
    Cfg.FILE = Paths.get(xcf)
    Cfg.MTIME = 0
    Cfg.reload()
    check(bool(Cfg.POCKET_CRAFT) is False and not bool(Link.POCKET_ON) and idh(CRWT.get(WTc.PocketCrafting)) == idh(van_sup),
          "X review fix 1: a hand edit bags.pocketCraft=false (SackCfg.reload) swaps the vanilla window back at once")
    open(xcf, "w", encoding="utf8").write("bags.pocketCraft=true\n")
    Cfg.MTIME = 0
    Cfg.reload()
    Cfg.FILE = None
    check(bool(Cfg.POCKET_CRAFT) and bool(Link.POCKET_ON) and str(CRWT.get(WTc.PocketCrafting).getClass().getName()) == "com.skyy.sacks.PocketSupplier"
          and idh(Link.POCKET_PREV) == idh(van_sup), "X review fix 1: ...=true puts ours back (never our own supplier recorded as the one to restore)")
    Link.pocketStart()
    check(idh(Link.POCKET_PREV) == idh(van_sup), "X review fix 1: a second pocketStart while ours is in does nothing (no double swap)")
    link_reset()
    print("X. pocket crafting: supplier swap + restore (+ prev none, + replaced later), refill, craft (inventory first), refresh, no key = empty, "
          "shared mirror with a bench (union, no ping-pong), close hooks book at once, the bags.pocketCraft off switch (hook / link / hand edit)")

    # ---------------- Y. the 300 ms link task: refresh only when stale, at most once a second, retire / park / prune, invalid windows untouched
    link_reset()
    Link.PLAYERS = look
    fresh_pools(os.path.join(SCRATCH, "pools-y"))
    UY = mkuuid(0xB1)
    kY = str(UY)
    Pool.add(kY, STK, 30)
    Pool.add(kY, RUB, 400)
    p, prY, wmY = wire(UY, hotbar=[(MIN_L, 1), (FOR_S, 1)])
    hY, sY, bpY = conts(p)
    bY, rawY = new_bench(items=[(OAK, 1)], chests=1)
    open_bench(prY, wmY, bY)
    mY = Mirror.MIRRORS.get(kY)
    clock = [100000]

    def run_link(dt=300):
        clock[0] += dt
        Link.link(p, UY, wmY.getWindows(), JLong(clock[0]))
        return bool(bY.isValid())
    v_ = [run_link() for _ in range(10)]
    check(all(v_) and int(RecC.LOG.size()) >= 1, "Y: nothing changed -> 10 runs, no refresh asked")
    Pool.add(kY, STK, 5)                                # a sweep puts 5 sticks in (shown: sticks are under the 4-stack limit)
    a1 = run_link()
    wmY.updateWindows()
    s1 = resmap(last_pkt().extraResources)
    Pool.add(kY, STK, 5)
    a2 = run_link(300)                                  # within the second: no second refresh yet
    a3 = run_link(800)                                  # the second has passed
    check(not a1 and s1 == {OAK: 1, STK: 35, RUB: 256} and a2 and not a3,
          "Y: a shown item changed -> one refresh (the client gets 35 sticks), the next change waits for the 1 s rate limit: %s" % s1)
    wmY.updateWindows()
    Pool.add(kY, RUB, 20)                               # rubble 400 -> 420: above the mirror's 4 stacks (256 shown) - nothing to show
    check(run_link(1200) and run_link(1200), "Y: a change above the mirror's 4 stacks changes nothing on screen -> no refresh")
    hY.removeItemStackFromSlot(JShort(0), JInt(1))      # the Mining bag is put away: rubble may no longer be offered
    a4 = run_link(1200)
    wmY.updateWindows()
    s4 = resmap(last_pkt().extraResources)
    check(not a4 and s4 == {OAK: 1, STK: 40} and held(mY, RUB) == 0, "Y: a carried bag changed -> refresh; the re-attach offers no rubble any more: %s" % s4)
    hY.removeItemStackFromSlot(JShort(1), JInt(1))      # no bag at all
    a5 = run_link(1200)
    wmY.updateWindows()
    s5 = resmap(last_pkt().extraResources)
    recY = Link.recOf(UY, bY, False)
    check(not a5 and s5 == {OAK: 1} and not bool(recY.attached) and not bool(mY.holds()),
          "Y: no bag carried any more -> refresh, the vanilla list only, the mirror synced + emptied (bags only work while carried)")
    put(hY, 0, MIN_L, 1)
    put(hY, 1, FOR_S, 1)
    a6 = run_link(1200)
    wmY.updateWindows()
    check(not a6 and resmap(last_pkt().extraResources) == {OAK: 1, STK: 40, RUB: 256}, "Y: bags picked up again -> refresh, the bags are back")
    feeds_ = int(bY.feeds)
    bY.invalidateExtraResources()                       # a craft just invalidated it: a refresh is on its way
    Pool.add(kY, STK, 3)
    run_link(1200)
    run_link(1200)
    check(int(bY.feeds) == feeds_ and not bY.isValid(), "Y: an invalid window is never touched (no section read = no silent vanilla re-feed)")
    wmY.updateWindows()
    mY = Mirror.MIRRORS.get(kY)
    mY.rebuild(Sweep.caps(p.getInventory()), JClass("java.util.HashSet")(JClass("java.util.Arrays").asList(JArray(JString)([STK]))))
    a7 = run_link(1200)
    check(not a7, "Y: someone else rebuilt the mirror (a /craft page view with other recipes) -> the bench refreshes once")
    wmY.updateWindows()
    check(run_link(1200) and run_link(1200), "Y: ...and then stays quiet")
    # a window the filter never saw: one refresh, then the filter's attach (or its decline) is what the task compares with
    bQ, rawQ = new_bench(items=[], chests=0)
    wins_field.get(wmY).put(JInt(11), bQ)
    bQ.setId(11)
    bQ.init(prY, wmY)
    bQ.getExtraResourcesSection()
    run_link(1200)
    check(not bQ.isValid() and Link.recOf(UY, bQ, False) is not None and Link.recOf(UY, bQ, False).reg is not None,
          "Y: a bench the filter never saw -> one refresh asked (review fix 2: the record the task made has its close hook)")
    wmY.updateWindows()
    check(mY.owns(bQ.getExtraResourcesSection().getItemContainer()) and run_link(1200) and bool(bQ.isValid()),
          "Y: ...the vanilla update went out, the filter attached the mirror, then quiet")
    wins_field.get(wmY).remove(JInt(11))
    run_link(1200)
    check(Link.recOf(UY, bQ, False) is None and idh(Mirror.MIRRORS.get(kY)) == idh(mY), "Y: a window gone without a close event -> its record pruned, the mirror stays for the other")
    # key change: retire (the old key's mirror synced, emptied, dropped; windows detached + refreshed)
    okr, remr = bench_craft(p, bY, [(STK, 2)])
    wmY.updateWindows()
    kb = [kY]
    bridge.put("profile:fn:key", Fn(lambda a: JString(kb[0])))
    bridge.put("profile:epoch:" + kY, LongJ.valueOf(1))
    run_link(1200)
    okr2, remr2 = bench_craft(p, bY, [(STK, 1)])      # unbooked when the switch comes
    wmY.updateWindows()
    bridge.put("profile:epoch:" + kY, LongJ.valueOf(2))
    kb[0] = "y-profile-B"
    Pool.add("y-profile-B", OAK, 7)
    run_link(1200)                                      # settling: park
    Pool.CHANGEDAT.clear()                              # the 6 s settle window passed
    run_link(1200)                                      # settled on the new key: retire the old one
    check(okr and okr2 and Mirror.MIRRORS.get(kY) is None and pool_counts(kY).get(STK) == 40 and str(Mirror.LASTKEY.get(UY)) == "y-profile-B"
          and not bY.isValid(), "Y: profile switch -> park then retire: the old key's bench use booked (43 - 3 = 40), its mirror dropped, the bench refreshed")
    wmY.updateWindows()
    check(resmap(last_pkt().extraResources) == {OAK: 8}, "Y: ...and the new profile's bags show (7 logs + 1 in the chest)")
    wins_field.get(wmY).remove(JInt(7))
    run_link(1200)
    check(Mirror.MIRRORS.get("y-profile-B") is None and not Link.RECS.containsKey(UY), "Y: no crafting window open -> the mirror synced, emptied, dropped")
    # a quick switch before the 300 ms task ever ran: the filter attached key A, the switch settles, the next attach (key B) retires A
    link_reset()
    Link.PLAYERS = look
    UQ = mkuuid(0xB7)
    kq_ = ["yq-A"]
    bridge.put("profile:fn:key", Fn(lambda a: JString(kq_[0])))
    bridge.put("profile:epoch:" + str(UQ), LongJ.valueOf(1))
    Pool.add("yq-A", STK, 50)
    Pool.add("yq-B", OAK, 9)
    pq_, prq_, wmq_ = wire(UQ, hotbar=[(FOR_S, 1)])
    bq_, _r = new_bench(items=[], chests=0)
    open_bench(prq_, wmq_, bq_)
    mqa = Mirror.MIRRORS.get("yq-A")
    okq, remq = bench_craft(pq_, bq_, [(STK, 6)])
    kq_[0] = "yq-B"
    bridge.put("profile:epoch:" + str(UQ), LongJ.valueOf(2))
    check(Pool.settledKey(UQ) is None, "Y: (quick switch) settling")
    Pool.CHANGEDAT.clear()
    RecC.LOG.clear()
    wmq_.updateWindows()                               # the first packet after the switch, still before any 300 ms run
    check(mqa is not None and okq and Mirror.MIRRORS.get("yq-A") is None and not bool(mqa.holds()) and pool_counts("yq-A").get(STK) == 44
          and resmap(last_pkt().extraResources) == {OAK: 9} and str(Mirror.LASTKEY.get(UQ)) == "yq-B",
          "Y: a quick profile switch before the 300 ms task ran: the new key's attach retired the old mirror (6 booked: 44, emptied, dropped)")
    print("Y. link: quiet when nothing changed, refresh on a shown change only, 1 s rate limit, bags changed / gone / back, invalid windows "
          "untouched, foreign rebuild, unseen window, prune, park + retire on a profile switch, dropped when no window")

    # ---------------- Z. item-conservation fuzz: bench + pocket crafts, timed crafts cancelled mid-way, withdraws, refills, sweeps, bag drops,
    # profile switches, inserts into the guard, disconnects, filter failures, the bags.pocketCraft switch, late syncs.
    # Review fix 3: DELAYED syncing - no syncAll after a step (that hid every interleaving of unbooked bench / pocket use with withdraws,
    # parks, closes and declines); after EVERY step a no-sync audit of every mirror seen (live, or dropped and not empty): each container
    # slot holds at most its slot-table amount of the same item, the tables of one key never offer more than its pool, and conservation
    # holds once the unbooked use (table - container) is taken off: inventory + both pools + chests + ground - unbooked = start + picked up
    # - used. A few seeds also run the old way (every mirror synced after each step: then nothing may stay unbooked). Each seed ends with a
    # disconnect (every window closed), a late sync and the exact totals; nothing of the player may stay in BenchLink.RECS (review fix 2).
    ZIDS = (STK, RUB, OAK, ORE_C, FIB)
    RECIPES = ([(STK, 4), (RUB, 2)], [(OAK, 1)], [(FIB, 3), (STK, 1)], [(ORE_C, 2)], [(RUB, 5)])
    OUTID = "Skyy_Test_Output"
    BAGIDS = (MIN_L, FOR_S, MIN_S)
    zstats = {}
    zfail = [0]

    def zst(k_, n_=1):
        zstats[k_] = zstats.get(k_, 0) + n_

    def fuzz(seed, n_ops, eager=False):
        R = _rnd.Random(seed)
        link_reset()
        Link.PLAYERS = look
        Cfg.POCKET_CRAFT = True
        Link.pocketApply()
        fresh_pools(os.path.join(SCRATCH, "pools-z%d" % seed))
        u = mkuuid(0xC00 + seed)
        keys = ["z%dA" % seed, "z%dB" % seed]
        kbx = [keys[0]]
        ep = [1]
        bridge.put("profile:fn:key", Fn(lambda a: JString(kbx[0])))
        bridge.put("profile:epoch:" + str(u), LongJ.valueOf(1))
        for kk in keys:
            for i in ZIDS:
                Pool.add(kk, i, R.randint(0, 220))
        stor = [(R.choice(ZIDS), R.randint(1, 64)) for _ in range(R.randint(3, 14))]
        pp, prr, wmm = wire(u, storage=stor, hotbar=[(MIN_L, 1), (FOR_S, 1)], backpack=[(MIN_S, 1)])
        hb, st_, bk = conts(pp)
        chests = SIC(JShort(18))
        for _ in range(R.randint(0, 5)):
            chests.addItemStack(IS(R.choice(ZIDS), R.randint(1, 40)))
        ground = {}
        consumed = {}
        spawned = {}
        produced = [0]
        state = {"bench": None, "pocket": None, "jobs": []}
        clk = [500000]
        tracked = []

        def sysc():
            out = dict(inv_counts(pp))
            for kk in keys:
                for i, q in pool_counts(kk).items():
                    out[i] = out.get(i, 0) + q
            for i, q in snapc(chests).items():
                out[i] = out.get(i, 0) + q
            for i, q in ground.items():
                out[i] = out.get(i, 0) + q
            return out

        def addd(d, i, q):
            d[i] = d.get(i, 0) + q
            if d[i] == 0:
                del d[i]
        init = sysc()

        def track():                         # every mirror object ever live (a dropped one stays tracked while it is not empty)
            for mm in list(Mirror.MIRRORS.values()):
                h_ = idh(mm)
                if not any(idh(x) == h_ and bool(x.equals(mm)) for x in tracked):
                    tracked.append(mm)

        def audit():                         # NO sync: returns (unbooked use per item, problems)
            unb, bad, per_key, keep = {}, [], {}, []
            for mm in tracked:
                key = str(mm.key)
                cur = Mirror.MIRRORS.get(key)
                live = cur is not None and idh(cur) == idh(mm) and bool(cur.equals(mm))
                ids_, qs_ = mm.slotIds, mm.slotQty
                nonempty = False
                for s_ in range(36):
                    sid, q = ids_[s_], int(qs_[s_])
                    it_ = mm.cont.getItemStack(JShort(s_))
                    act = 0 if it_ is None or it_.isEmpty() else int(it_.getQuantity())
                    if q > 0 or act > 0:
                        nonempty = True
                    if sid is None:
                        if act > 0:
                            bad.append("mirror %s slot %d holds %d %s outside its slot table" % (key, s_, act, it_.getItemId()))
                        continue
                    sid = str(sid)
                    if act > q or (act > 0 and str(it_.getItemId()) != sid):
                        bad.append("mirror %s slot %d: container %d > table %d of %s (something was put into the mirror)" % (key, s_, act, q, sid))
                        continue
                    if q > act:
                        unb[sid] = unb.get(sid, 0) + (q - act)
                    pk_ = per_key.setdefault(key, {})
                    pk_[sid] = pk_.get(sid, 0) + q
                if live or nonempty:
                    keep.append(mm)
            tracked[:] = keep
            for key, items in per_key.items():
                pc_ = pool_counts(key)
                for i, q in items.items():
                    if q > pc_.get(i, 0):
                        bad.append("key %s: its mirror tables offer %d %s, its pool holds %d (could be used twice)" % (key, q, i, pc_.get(i, 0)))
            return unb, bad

        def totals_bad(unb):                 # conservation with the unbooked use taken off
            now_ = sysc()
            bad_ = []
            for i in set(now_) | set(init) | set(spawned) | set(consumed) | set(unb):
                if i == OUTID:
                    continue
                want = init.get(i, 0) + spawned.get(i, 0) - consumed.get(i, 0)
                if now_.get(i, 0) - unb.get(i, 0) != want:
                    bad_.append("%s %d - unbooked %d (want %d)" % (i, now_.get(i, 0), unb.get(i, 0), want))
            if now_.get(OUTID, 0) != produced[0]:
                bad_.append("output %d (want %d)" % (now_.get(OUTID, 0), produced[0]))
            return bad_

        def settled():
            return Pool.settledKey(u)

        def give(i, q):                      # into the inventory (storage first), overflow to the ground (addOrDropItemStack)
            tx = inv_c(pp).addItemStack(IS(i, q))
            rem = tx.getRemainder()
            r = 0 if rem is None or rem.isEmpty() else int(rem.getQuantity())
            if r > 0:
                addd(ground, i, r)

        def op_craft_result(res):
            ok, removed = res
            for i, q in removed.items():
                addd(consumed, i, q)
            if ok:
                zst("=craft ok")
                produced[0] += 1
                give(OUTID, 1)

        def cancel_jobs():                   # the vanilla close: cancelAllCrafting refunds the started, unfinished unit into the inventory
            jobs = state["jobs"]
            if jobs:
                j = jobs[0]
                if j["started"] > j["done"]:
                    zst("=timed unit refunded at close")
                    for i, q in j["removed"].get(j["started"] - 1, {}).items():
                        give(i, q)
                        addd(consumed, i, -q)
            state["jobs"] = []

        def close_all():                     # a disconnect: closeAllWindows - each window closes (bench: refund, onClose0, close event)
            order = ["bench", "pocket"]
            R.shuffle(order)
            for o_ in order:
                if o_ == "bench" and state["bench"] is not None:
                    cancel_jobs()
                    close_bench(wmm, state["bench"])
                    state["bench"] = None
                elif o_ == "pocket" and state["pocket"] is not None:
                    close_pocket(wmm, state["pocket"])
                    state["pocket"] = None

        def fail(msg):
            zfail[0] += 1
            check(False, "Z seed %d: %s" % (seed, msg))

        def step(name):
            zst(name)
            b_ = state["bench"]
            pw_ = state["pocket"]
            if name == "bench_open" and b_ is None:
                nb, _r = new_bench(raw_=chests, chests=1)
                open_bench(prr, wmm, nb)
                state["bench"] = nb
            elif name == "bench_close" and b_ is not None:
                cancel_jobs()
                close_bench(wmm, b_)
                state["bench"] = None
            elif name == "pocket_open" and pw_ is None:
                if bool(Link.POCKET_ON):
                    state["pocket"] = open_pocket(prr, wmm)
                else:
                    zst("=inventory opened while bags.pocketCraft is off (vanilla window)")
            elif name == "pocket_close" and pw_ is not None:
                close_pocket(wmm, pw_)
                state["pocket"] = None
            elif name == "bench_craft" and b_ is not None:
                if R.random() < 0.5:
                    Link.preCraft(pp, u, 7)
                op_craft_result(bench_craft(pp, b_, R.choice(RECIPES), R.randint(1, 3)))
            elif name == "pocket_craft" and pw_ is not None:
                op_craft_result(pocket_craft(pp, pw_, R.choice(RECIPES), R.randint(1, 3)))
            elif name == "timed_queue" and b_ is not None and len(state["jobs"]) < 3:
                comb = CICc(JArray(ICc)([inv_c(pp), b_.getExtraResourcesSection().getItemContainer()]))
                state["jobs"].append({"comb": comb, "spec": R.choice(RECIPES), "qty": R.randint(1, 4), "started": 0, "done": 0, "removed": {}})
                b_.invalidateExtraResources()
            elif name == "timed_tick" and state["jobs"]:
                j = state["jobs"][0]
                if j["started"] == j["done"] and j["started"] < j["qty"]:
                    ok, removed = craft_from(j["comb"], j["spec"], 1)
                    for i, q in removed.items():
                        addd(consumed, i, q)
                    if not ok:
                        state["jobs"].pop(0)         # missing ingredient: the job is dropped (nothing was taken)
                    else:
                        zst("=timed unit started")
                        j["removed"][j["started"]] = removed
                        j["started"] += 1
                    if b_ is not None:
                        b_.invalidateExtraResources()
                elif j["started"] > j["done"]:
                    j["done"] += 1
                    produced[0] += 1
                    give(OUTID, 1)
                    if j["done"] >= j["qty"]:
                        state["jobs"].pop(0)
            elif name == "send":
                if pw_ is not None or b_ is not None:
                    wmm.updateWindows()
            elif name == "link":
                clk[0] += R.randint(100, 2500)
                Link.link(pp, u, wmm.getWindows(), JLong(clk[0]))
            elif name == "withdraw":
                k = settled()
                if k is not None:
                    wd_ = int(Sweep.withdraw(pp, str(k), R.choice(ZIDS), R.choice((1, 16, 64))))
                    if wd_ > 0:
                        zst("=withdrawn items", wd_)
            elif name == "deposit_all":
                k = settled()
                if k is not None:
                    cat = R.choice(("Mining", "Foraging"))
                    Pool.clearKeptCat(str(k), cat)
                    Pool.forgetSeen(u)
                    Sweep.sweep(pp, str(k), cat, True)
            elif name == "tick":
                k = settled()
                if k is not None:
                    ti_ = Sweep.items(pp, str(k), u)
                    if int(ti_[1]) > 0:
                        zst("=refilled items", int(ti_[1]))
                    if int(ti_[0]) > 0:
                        zst("=swept items", int(ti_[0]))
            elif name == "use":                      # blocks placed / items eaten: they leave the game
                c_ = R.choice((hb, st_, bk))
                slots = [i for i in range(int(c_.getCapacity())) if at(c_, i) is not None and at(c_, i)[0] in ZIDS]
                if slots:
                    i = R.choice(slots)
                    iid, q = at(c_, i)
                    n = R.randint(1, q)
                    c_.removeItemStackFromSlot(JShort(i), JInt(n))
                    addd(consumed, iid, n)
            elif name == "pickup":
                iid = R.choice(ZIDS)
                n = R.randint(1, 30)
                c_ = R.choice((st_, st_, hb))
                tx = c_.addItemStack(IS(iid, n))
                rem = tx.getRemainder()
                got = n - (0 if rem is None or rem.isEmpty() else int(rem.getQuantity()))
                if got > 0:
                    addd(spawned, iid, got)
            elif name == "bag_drop":
                c_ = R.choice((hb, bk, st_))
                slots = [i for i in range(int(c_.getCapacity())) if at(c_, i) is not None and at(c_, i)[0] in BAGIDS]
                if slots:
                    i = R.choice(slots)
                    iid, q = at(c_, i)
                    c_.removeItemStackFromSlot(JShort(i), JInt(q))
                    addd(ground, iid, q)
            elif name == "bag_pick":
                bags = [i for i in ground if i in BAGIDS]
                if bags:
                    iid = R.choice(bags)
                    tx = R.choice((hb, st_)).addItemStack(IS(iid, 1))
                    rem = tx.getRemainder()
                    if rem is None or rem.isEmpty():
                        addd(ground, iid, -1)
            elif name == "switch":
                kbx[0] = keys[1] if kbx[0] == keys[0] else keys[0]
                ep[0] += 1
                bridge.put("profile:epoch:" + str(u), LongJ.valueOf(ep[0]))
            elif name == "settle":
                Pool.CHANGEDAT.remove(u)
            elif name == "craft_page":
                k = settled()
                if k is not None:
                    m = Mirror.of(str(k))
                    m.sync()
                    wl = JClass("java.util.HashSet")()
                    for i in R.sample(ZIDS, R.randint(0, 3)):
                        wl.add(i)
                    m.rebuild(Sweep.caps(pp.getInventory()), wl)
                    comb = CICc(JArray(ICc)([inv_c(pp), m.cont]))
                    op_craft_result(craft_from(comb, R.choice(RECIPES), R.randint(1, 2)))
                    m.sync()
            elif name == "insert_attack":                # a fresh stack pushed at the guard and at every open crafting section (alone and as
                # the overflow of a full inventory, like a shift-click): any accepted insert is a failure (no sync - the attack books nothing)
                m = Mirror.MIRRORS.get(str(kbx[0]))
                iid = R.choice(ZIDS)
                targets = []
                if m is not None:
                    targets.append(("the guard", m.guard))
                if b_ is not None and bool(b_.isValid()):     # (a valid section only: reading an invalid bench section would re-feed it)
                    targets.append(("the bench section", b_.getExtraResourcesSection().getItemContainer()))
                if pw_ is not None and bool(pw_.isValid()):
                    targets.append(("the pocket section", pw_.getExtraResourcesSection().getItemContainer()))
                before = [snapc(x.cont) for x in tracked]
                for nm_, tgt_ in targets:
                    zst("=inserts refused")
                    if bool(tgt_.addItemStack(IS(iid, 1)).succeeded()) or bool(CICc(JArray(ICc)([inv_c(full), tgt_])).addItemStack(IS(iid, 1)).succeeded()):
                        fail("an insert of %s was accepted by %s" % (iid, nm_))
                if [snapc(x.cont) for x in tracked] != before:
                    fail("an insert of %s reached a mirror" % iid)
            elif name == "sync_all":                     # a late sync (the shutdown's BagMirror.syncAll)
                bk_ = int(Mirror.syncAll())
                if bk_ > 0:
                    zst("=booked by late syncs", bk_)
            elif name == "close_all":
                close_all()
                zst("=disconnects")
                if Link.RECS.containsKey(u):
                    fail("a disconnect (every window closed) left records in BenchLink.RECS (review fix 2)")
            elif name == "filter_boom" and b_ is not None:   # a bench packet while the filter fails (caught): the window stays vanilla
                Link.PLAYERS = Fn(boom)
                try:
                    b_.invalidateExtraResources()
                    wmm.updateWindows()
                finally:
                    Link.PLAYERS = look
                zst("=filter failures")
            elif name == "pocket_switch":                # Server Setup bags.pocketCraft flipped (the row's after= hook)
                Cfg.POCKET_CRAFT = not bool(Cfg.POCKET_CRAFT)
                Cfg.pocketChanged("bags.pocketCraft")
                zst("=bags.pocketCraft flips")
                if bool(Link.POCKET_ON) != bool(Cfg.POCKET_CRAFT):
                    fail("bags.pocketCraft %s but the pocket window swap is %s" % (bool(Cfg.POCKET_CRAFT), bool(Link.POCKET_ON)))
        W = (("bench_open", 6), ("bench_close", 4), ("pocket_open", 4), ("pocket_close", 3), ("bench_craft", 14), ("pocket_craft", 10),
             ("timed_queue", 5), ("timed_tick", 10), ("send", 14), ("link", 14), ("withdraw", 8), ("deposit_all", 2), ("tick", 10),
             ("use", 6), ("pickup", 8), ("bag_drop", 2), ("bag_pick", 3), ("switch", 2), ("settle", 4), ("insert_attack", 2),
             ("craft_page", 4), ("sync_all", 2), ("close_all", 2), ("filter_boom", 1), ("pocket_switch", 1))
        names = [w[0] for w in W]
        weights = [w[1] for w in W]
        for s_ in range(n_ops):
            name = R.choices(names, weights)[0]
            track()
            step(name)
            track()
            if eager:
                bk_ = int(Mirror.syncAll())             # the old way: what the 300 ms task / the close hooks do, after every step
                if bk_ > 0:
                    zst("=booked from bags (eager)", bk_)
            unb, bad_ = audit()
            if unb:
                zst("=steps with unbooked bag use", 1)
                zst("=unbooked bag items seen", sum(unb.values()))
                if eager:
                    bad_.append("unbooked after a full sync: %s" % unb)
            bad_ += totals_bad(unb)
            if bad_:
                fail("step %d (%s): %s" % (s_, name, "; ".join(bad_[:4])))
                return s_ + 1
            OKS[0] += 1
        # the end of the seed: a disconnect, one more 300 ms run on a settled profile (no window: its mirror is dropped), a late sync -
        # then nothing may be unbooked, the totals exact, no record of the player and no mirror of the settled key left. settledKey first:
        # a switch nobody looked at yet starts its settle window only when it is seen - then the window is passed. (A mirror of the OTHER
        # profile may stay: /craft makes one without the link's last-key memory, and a switch back before any 300 ms run - the game runs it
        # every 300 ms - leaves it to the next attach of that key; no window can reach it and the audit keeps it within its pool.)
        Pool.settledKey(u)
        Pool.CHANGEDAT.remove(u)
        close_all()
        clk[0] += 2000
        Link.link(pp, u, wmm.getWindows(), JLong(clk[0]))
        Mirror.syncAll()
        track()
        unb, bad_ = audit()
        bad_ += totals_bad(unb)
        ck_ = Pool.settledKey(u)
        if unb or bad_ or Link.RECS.containsKey(u) or ck_ is None or Mirror.MIRRORS.containsKey(ck_):
            fail("end of the seed: unbooked %s, %s, records left %s, mirrors left %s (settled key %s, last key %s, keys %s)"
                 % (unb, "; ".join(bad_[:4]), bool(Link.RECS.containsKey(u)), [(str(k_), bool(Mirror.MIRRORS.get(k_).holds())) for k_ in Mirror.MIRRORS.keySet()],
                    ck_, Mirror.LASTKEY.get(u), keys))
        elif not Mirror.MIRRORS.isEmpty():
            zst("=seeds ending with a /craft mirror of the other profile (unreachable, within its pool)")
        OKS[0] += 1
        Cfg.POCKET_CRAFT = True
        Link.pocketApply()
        return n_ops
    ZSEEDS = int(arg("--zseeds", "40"))
    ZSTEPS = int(arg("--zsteps", "2500"))
    zruns = []
    for seed_ in range(1, ZSEEDS + 1):
        zruns.append(fuzz(seed_, ZSTEPS))
    zeager = []
    for seed_ in (1001, 1002, 1003, 1004):
        zeager.append(fuzz(seed_, 1250, eager=True))
    check(zfail[0] == 0, "Z: %d fuzz steps over %d seeds with DELAYED syncing + %d steps over 4 seeds synced after each step: 0 items created, "
          "lost or used twice; every container <= its slot table, the tables of a key <= its pool; nothing left after a disconnect"
          % (sum(zruns), ZSEEDS, sum(zeager)))
    for k_ in ("=craft ok", "=booked from bags (eager)", "=timed unit started", "=timed unit refunded at close", "=withdrawn items",
               "=refilled items", "=swept items", "=steps with unbooked bag use", "=booked by late syncs", "=disconnects", "=filter failures",
               "=bags.pocketCraft flips", "=inventory opened while bags.pocketCraft is off (vanilla window)", "=inserts refused"):
        check(zstats.get(k_, 0) > 0, "Z: the fuzz really exercised %s (%d)" % (k_[1:], zstats.get(k_, 0)))
    print("Z. item-conservation fuzz: %d delayed-sync steps (%d seeds) + %d synced steps (%s) - 0 created / lost / double-used"
          % (sum(zruns), ZSEEDS, sum(zeager), ", ".join("%s %d" % (k_, v_) for k_, v_ in sorted(zstats.items()))))

    # ---------------- O. Server Setup bags.benchChests (research doc risk 2 fallback, off by default) + BenchLink.stop()
    link_reset()
    Link.PLAYERS = look
    fresh_pools(os.path.join(SCRATCH, "pools-o"))
    UO = mkuuid(0xD1)
    Pool.add(str(UO), STK, 20)
    p, prO, wmO = wire(UO, hotbar=[(FOR_S, 1)])
    Cfg.CHEST_FIX = False
    b0_, _r = new_bench(items=[], chests=0)
    po0 = open_bench(prO, wmO, b0_)
    check('"nearbyChestCount":0' in str(po0.windowData) and int(b0_.getData().get("nearbyChestCount").getAsInt()) == 0,
          "O: fallback OFF (default): a bench without chests still says 0 nearby chests (vanilla look)")
    wins_field.get(wmO).remove(JInt(7))
    Link.closed(UO, b0_)
    Cfg.CHEST_FIX = True
    b1_, _r = new_bench(items=[], chests=0)
    po1 = open_bench(prO, wmO, b1_)
    check('"nearbyChestCount":1' in str(po1.windowData) and int(b1_.getData().get("nearbyChestCount").getAsInt()) == 1
          and resmap(po1.extraResources) == {STK: 20}, "O: fallback ON: the open packet + the window data report 1 nearby chest when bags are linked")
    b1_.invalidateExtraResources()
    RecC.LOG.clear()
    wmO.updateWindows()
    check('"nearbyChestCount":1' in str(last_pkt().windowData), "O: ...and later updates keep it")
    wins_field.get(wmO).remove(JInt(7))
    Link.closed(UO, b1_)
    b2_, _r = new_bench(items=[(OAK, 3)], chests=2)
    po2 = open_bench(prO, wmO, b2_)
    check('"nearbyChestCount":2' in str(po2.windowData), "O: real chests: the count is left as it is")
    wins_field.get(wmO).remove(JInt(7))
    Link.closed(UO, b2_)
    pn_, prn_, wmn_ = wire(mkuuid(0xD2))
    b3_, _r = new_bench(items=[], chests=0)
    po3 = open_bench(prn_, wmn_, b3_)
    check('"nearbyChestCount":0' in str(po3.windowData), "O: no bag carried: nothing linked, nothing changed")
    Cfg.CHEST_FIX = False
    Link.stop()
    pz = UWc(7, "{}", None, ERc(JArray(IQc)([IQc(OAK, 1)])))
    wins_field.get(wmO).put(JInt(7), b2_)
    prO.getPacketHandler().writeNoCache(pz)
    check(Link.OUT is None and Link.IN is None and not bool(Link.POCKET_ON) and idh(CRWT.get(WTc.PocketCrafting)) == idh(van_sup)
          and resmap(pz.extraResources) == {OAK: 1},
          "O: BenchLink.stop(): both filters deregistered (a later packet is not merged), the vanilla pocket supplier restored")
    # review fix 1: after stop() the bags.pocketCraft switch swaps nothing (a SackSaver reload during shutdown); start() with the switch
    # OFF (config.properties read in setup(), before start()) keeps the vanilla pocket window and still links the benches
    Cfg.POCKET_CRAFT = True
    Link.pocketApply()
    Link.pocketCheck()
    check(not bool(Link.STARTED) and not bool(Link.POCKET_ON) and idh(CRWT.get(WTc.PocketCrafting)) == idh(van_sup),
          "O review fix 1: after stop() the switch swaps nothing")
    Cfg.POCKET_CRAFT = False
    Link.start()
    check(bool(Link.STARTED) and Link.OUT is not None and Link.IN is not None and not bool(Link.POCKET_ON)
          and idh(CRWT.get(WTc.PocketCrafting)) == idh(van_sup),
          "O review fix 1: start() with bags.pocketCraft off: both filters on (benches use the bags), the vanilla pocket window stays")
    Cfg.POCKET_CRAFT = True
    Cfg.pocketChanged("bags.pocketCraft")
    check(bool(Link.POCKET_ON) and str(CRWT.get(WTc.PocketCrafting).getClass().getName()) == "com.skyy.sacks.PocketSupplier"
          and idh(Link.POCKET_PREV) == idh(van_sup), "O review fix 1: ...switched on while running -> ours, the vanilla one kept to restore")
    Link.stop()
    check(not bool(Link.STARTED) and idh(CRWT.get(WTc.PocketCrafting)) == idh(van_sup) and Link.OUT is None,
          "O review fix 1: ...and stop() restores it again")
    CRWT.remove(WTc.PocketCrafting)
    Link.PLAYERS = None
    link_reset()
    print("O. bench chest count fallback: off = vanilla, on = 1 nearby chest when bags are linked (open + updates), real chests / no bag "
          "untouched; stop() restores everything")

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
    # 0.7.12 WORDING BACK (0.7.11 review fix 1 removed it on purpose - now true): every refill help line, the no-bag view's hint and the
    # ready log line say that benches and inventory crafting use the bags you carry; no line says the refill pauses while a bench is open
    for h_ in list(RF.HELP) + [RF.OFFSRV]:
        check(len(str(h_)) <= 140 and "Benches and inventory crafting" in str(h_) and "paused" not in str(h_),
              "R 0.7.12 wording: the help line says benches and inventory crafting use the bags (%d chars): %r" % (len(str(h_)), str(h_)))
    check(str(RF.HELP[0]).startswith("A hotbar stack you use tops back up") and str(RF.HELP[1]).startswith("Any stack you use")
          and str(RF.HELP[2]).startswith("Stacks never top up"), "R 0.7.12 wording: Hotbar only / Full inventory / Off keep their meaning")
    check("Benches and inventory crafting use the materials in the bags you carry, and so does /craft." in t_,
          "R 0.7.12 wording: the how-to-craft view's hint says benches and inventory crafting use the bags (and /craft)")
    ready_ = [l for l in ldcs(members(JAR, PKG + "SkyySacksPlugin")["m setup()V"]) if l.startswith("[SkyySacks] %s ready" % VERSION)]
    check(len(ready_) == 1 and "benches and inventory crafting use the bags you carry" in ready_[0]
          and "vanilla benches do not show bag materials yet" not in ready_[0] and "bags.pocketCraft" in ready_[0],
          "R 0.7.12 wording: the ready log line says benches and inventory crafting use the bags you carry (+ the bags.pocketCraft off switch)")
    # review fix 1: with Server Setup bags.pocketCraft OFF no text claims inventory crafting (the refill help line of each mode, the
    # server-off line, the how-to-craft hint); back on = the full claim again
    check(len(RF.HELPB) == 3 and all("Benches" in str(h_) and "inventory crafting" not in str(h_) and len(str(h_)) <= 140 for h_ in list(RF.HELPB) + [RF.OFFSRVB]),
          "R review fix 1: the pocket-off lines say benches only: %r" % [str(h_) for h_ in list(RF.HELPB) + [RF.OFFSRVB]])
    Cfg.POCKET_CRAFT = False
    for mode in (0, 1, 2):
        RF.set(UR, mode)
        tb_, _pg = page_text(pr_, "r", "Mining", prR)
        check(str(RF.HELPB[mode]) in tb_ and str(RF.HELP[mode]) not in tb_ and "inventory crafting" not in tb_,
              "R review fix 1 (bags.pocketCraft off, mode %d): the help line without the inventory crafting claim" % mode)
    Cfg.REFILL_ON = False
    tb_, _pg = page_text(pr_, "r", "Mining", prR)
    check(str(RF.OFFSRVB) in tb_ and str(RF.OFFSRV) not in tb_, "R review fix 1 (bags.pocketCraft off, refill off on the server): the benches-only server-off line")
    Cfg.REFILL_ON = True
    tb_, _pg = page_text(player(), "r", "Combat", prR)
    check("Benches use the materials in the bags you carry, and so does /craft." in tb_ and "inventory crafting" not in tb_,
          "R review fix 1 (bags.pocketCraft off): the how-to-craft hint says benches (and /craft) only")
    Cfg.POCKET_CRAFT = True
    tb_, _pg = page_text(player(), "r", "Combat", prR)
    check("Benches and inventory crafting use the materials in the bags you carry" in tb_, "R review fix 1: bags.pocketCraft on again -> the full claim")
    RF.set(UR, 0)
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
    for opt_ in ("--zseeds", "--zsteps"):    # review fix 3: the delayed-sync fuzz size (defaults 40 seeds x 2,500 steps)
        if arg(opt_) is not None:
            args += [opt_, arg(opt_)]
    rc = subprocess.call(args, env=env, cwd=ROOT)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyySacks %s bare-JVM check: %s (exit code %d)%s" % (VERSION, "PASS" if rc == 0 else "FAIL", rc, "" if KEEP else " (scratch folder removed)"))
    sys.exit(rc)


if __name__ == "__main__":
    main()
