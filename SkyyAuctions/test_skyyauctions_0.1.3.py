"""Harness for SkyyAuctions 0.1.3 (Auction House sort + filters; Skyy 2026-10-09 "auction house needs sorting filters too").
Build first: python tools/auctions_0_1_3_patch.py && python SkyyAuctions/build_skyyauctions_0.1.3.py

    python SkyyAuctions/test_skyyauctions_0.1.3.py [--jar <SkyyAuctions-0.1.3.jar>] [--dir <scratch>] [--keep]

Children (fresh JVMs, the game's JRE, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch):
  F  stand-ins compiled with javassist: FakeAhPage (a real AhPage whose rebuild() only counts), LookupIn + BadAccess (the audit)
  A  every class of the jar loads + initialises with -Xverify:all
  X  EVERY NEW CODE PATH EXECUTED (-Xverify:all, a bridge with stand-in gear:fn:* functions): AhItem.fcatRule (table), fcat (cache, the
     asset path with a real Item in the item asset map), levelOfRec (gear / not gear / cache / rev + tiers invalidation / no SkyyGear),
     AhPage.parseLv, lvText, filtersOn, filterLine, readFields, browseAct (every action), results (each sort order, each category, each
     rarity, level ranges, combinations with search, empty results, SkyyGear off), render (the Browse view with and without SkyyGear,
     every empty text, the pager, the 1080 height sum, no level binding outside Browse), handleDataEvent (Browse clicks through the
     real event path, the bad-level warning, paging + clamping, Reset)
  C  CLASS COMPARE 0.1.2 -> 0.1.3 (javassist members + bytecode): exactly the listed members differ, no class added / removed
  D  START TWICE on a scratch COPY of the live Skyy_SkyyAuctions folder (setup()'s order: migrate, load, blocked, builtin, listings,
     restoreFromLog, scanStarts): no file changes on either start; the live listings sort into the new categories (counts printed)
  AA THE ENGINE-ACCESS AUDIT: every class / field / method reference resolved with MethodHandles.privateLookupIn the referencing class
Scratch: tools/dev/scratch/ah013/harness (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, time, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.1.3"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyAuctions-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAuctions-0.1.2.jar")
SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "ah013", "harness")))
FAKE_DIR = os.path.join(SCRATCH, "fake")
FAKE_PKG = "skyyahtest"
PKG = "com.skyy.auctions."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyAuctions")
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


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

    def eq(self, got, want, what):
        self.check(got == want, "%s: got %r, want %r" % (what, got, want))

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
    fp = cp.makeClass(P + ".FakeAhPage", cp.get(PKG + "AhPage"))
    fp.addField(CtField.make("public int rebuilds;", fp))
    fp.addConstructor(CtNewConstructor.make("public FakeAhPage(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr, \"browse\"); }", fp))
    fp.addMethod(CtNewMethod.make("public void rebuild() { this.rebuilds = this.rebuilds + 1; }", fp))
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


# ====================================================================================================== X: every new code path
# the Python model of AhItem.fcatRule (tools/auctions_0_1_3_patch.py B) - an independent oracle
MATP = ["Ingredient_", "Ore_", "Metal_", "Rock_", "Wood_", "Plant_", "Soil_", "Cloth_", "Rubble_"]
TOOLP = ["Tool_", "SkyyFishing_Rod", "SkyyFishing_Line", "SkyyFishing_Hook", "SkyyFishing_Sinker", "SkyyFishing_Reel"]


def fcat_py(i, stored, cats="", tool=False):
    i, stored, cats = i or "", stored or "", cats or ""
    if stored == "ACCESSORIES" or i.startswith("Skyy_Talisman_") or (i.startswith("Skyy_Accessory_") and i != "Skyy_Accessory_Bag"):
        return "ACCESSORIES"
    if i.startswith("Skyy_Unid_Weapon_"):
        return "WEAPONS"
    if i.startswith("Skyy_Unid_Armor_"):
        return "ARMOR"
    if stored in ("WEAPONS", "ARMOR", "CONSUMABLES"):
        return stored
    if tool or "|Items.Tools|" in cats or any(i.startswith(p) for p in TOOLP):
        return "TOOLS"
    if "|Furniture." in cats:
        return "OTHER"
    if stored == "BLOCKS" or "|Items.Ingredients|" in cats or "|Blocks." in cats or any(i.startswith(p) for p in MATP):
        return "MATERIALS"
    return "OTHER"


TIERS = ("normal:Normal:#FFFFFF,unique:Unique:#FFFF55,rare:Rare:#FF55FF,legendary:Legendary:#55FFFF,fabled:Fabled:#FF5555,"
         "mythic:Mythic:#CC66CC,set:Set:#55FF55,untiered:Untiered:#AAAAAA")
# item id -> (gear rarity id, level) for the stand-in gear:fn:rarity / level / describe; ids not here are "not gear"
GEAR = {"Weapon_Sword_Iron": ("rare", 20), "Armor_Iron_Chest": ("legendary", 25), "Tool_Pickaxe_Iron": ("normal", 18),
        "Skyy_Unid_Weapon_Sword": ("rare", 30), "Skyy_Unid_Bag_Rare": ("rare", 12), "Weapon_Kunai_Onyxium": ("mythic", 45),
        "Armor_Adamantite_Legs": ("set", 40), "Weapon_Bow_Untiered": ("untiered", 10), "Skyy_Unid_Armor_Chest": ("unique", 5)}
CAT_LABELS = ["All", "Weapons", "Armor", "Tools", "Accessories", "Materials", "Consumables", "Other"]
FCAT = ["ALL", "WEAPONS", "ARMOR", "TOOLS", "ACCESSORIES", "MATERIALS", "CONSUMABLES", "OTHER"]


def run_exec(out):
    from jpype import JClass, JImplements, JOverride, JArray, JString, JInt
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR, FAKE_DIR], verify=True)
    Sys, CHM = JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap")
    br = CHM()
    Sys.getProperties().put("skyy.bridge", br)
    Integer = JClass("java.lang.Integer")
    BD = JClass("org.bson.BsonDocument")
    Item, Store, Page, Rec = JClass(PKG + "AhItem"), JClass(PKG + "AhStore"), JClass(PKG + "AhPage"), JClass(PKG + "AhRec")
    UCB, UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f, self.calls = f, 0

        @JOverride
        def apply(self, o):
            self.calls += 1
            return self.f(o)

    def gid(o):
        try:
            return str(o[0])
        except Exception:
            return None
    f_rar = Fn(lambda o: GEAR[gid(o)][0] if gid(o) in GEAR else None)
    f_lvl = Fn(lambda o: Integer.valueOf(GEAR[gid(o)][1]) if gid(o) in GEAR else None)
    f_desc = Fn(lambda o: JArray(JString)(["Gear " + gid(o)]) if gid(o) in GEAR else None)

    def gear_on():
        br.put("gear:tiers", TIERS)
        br.put("gear:fn:rarity", f_rar)
        br.put("gear:fn:level", f_lvl)
        br.put("gear:fn:describe", f_desc)

    def gear_off():
        for k in ("gear:tiers", "gear:fn:rarity", "gear:fn:level", "gear:fn:describe"):
            br.remove(k)
    gear_on()

    # ---------------------------------------------------------------- X1 fcatRule (pure)
    rule_cases = [
        ("Skyy_Talisman_Speed", "MISC", "", False), ("Skyy_Accessory_Ring", "MISC", "", False), ("Skyy_Accessory_Bag", "MISC", "", False),
        ("Anything", "ACCESSORIES", "", False), ("Skyy_Unid_Weapon_Sword", "MISC", "", False), ("Skyy_Unid_Armor_Chest", "MISC", "", False),
        ("Skyy_Unid_Bag_Rare", "MISC", "", False), ("Weapon_Sword_Iron", "WEAPONS", "|Items.Weapons|", False),
        ("Armor_Iron_Chest", "ARMOR", "", False), ("Food_Bread", "CONSUMABLES", "", False), ("Tool_Pickaxe_Iron", "MISC", "", False),
        ("Template_Glider", "MISC", "|Items.Tools|", False), ("Mystery_Thing", "MISC", "", True), ("SkyyFishing_Rod_Wood", "MISC", "", False),
        ("SkyyFishing_Hook_Iron", "MISC", "", False), ("SkyyFishing_Reel_Gold", "MISC", "", False), ("SkyyFishing_Sinker_Lead", "MISC", "", False),
        ("SkyyFishing_Line_Silk", "MISC", "", False), ("SkyyFishing_Fish_Cod", "MISC", "", False),
        ("Furniture_Ancient_Bed", "BLOCKS", "|Furniture.Beds|", False), ("Furniture_Ancient_Bed", "BLOCKS", "", False),
        ("Rock_Stone_Brick", "BLOCKS", "|Blocks.Rocks|", False), ("Ingredient_Bar_Iron", "MISC", "|Items.Ingredients|", False),
        ("Ingredient_Bar_Iron", "MISC", "", False), ("Ore_Iron", "MISC", "", False), ("Metal_Bronze", "MISC", "", False),
        ("Wood_Oak_Trunk", "MISC", "", False), ("Plant_Fiber", "MISC", "", False), ("Soil_Clay", "MISC", "", False),
        ("Cloth_Roof_Blue", "MISC", "", False), ("Rubble_Stone", "MISC", "", False), ("Tree_Sap_Glob", "MISC", "|Blocks.Plants|", False),
        ("Skyy_Sack_Mining", "MISC", "", False), ("Upgrade_Backpack_1", "MISC", "|Upgrade|", False), ("", "", "", False),
        (None, None, None, False), ("Tool_Map", "MISC", "|Tool|", False), ("Weapon_Deployable_Totem", "MISC", "|Items.Utility|", False)]
    for c in rule_cases:
        K.eq(str(Item.fcatRule(c[0], c[1], c[2], c[3])), fcat_py(*c), "X1 fcatRule%r" % (c,))
    seen = set(str(Item.fcatRule(*c)) for c in rule_cases)
    K.check(seen == set(FCAT[1:]), "X1: the rule table reaches every category: %s" % sorted(seen))
    K.eq([str(x) for x in Item.FCAT], FCAT, "X1 FCAT")
    K.eq([str(x) for x in Item.FCAT_LABEL], CAT_LABELS, "X1 FCAT_LABEL")

    # ---------------------------------------------------------------- records
    now = int(Sys.currentTimeMillis())
    seq = [100]

    def rec(iid, price, cat, created_ago, ends_in, name=None, seller="Bob", qty=1, rev=1, quality=0):
        seq[0] += 1
        rid = str(seq[0])
        nm = name or iid.replace("_", " ")
        d = {"v": 1, "id": rid, "type": "BIN", "state": "ACTIVE", "closed": False, "rev": {"$numberLong": str(rev)},
             "seller": {"uuid": "00000000-0000-0000-0000-0000000000b0", "key": "00000000-0000-0000-0000-0000000000b0", "name": seller, "profile": ""},
             "item": {"id": iid, "qty": qty, "quality": quality, "durability": 0.0, "maxDurability": 0.0},
             "name": nm, "search": (nm + " " + iid + " " + seller).lower(), "category": cat,
             "price": {"$numberLong": str(price)}, "startBid": {"$numberLong": str(price)}, "topBid": {"$numberLong": "0"},
             "createdAt": {"$numberLong": str(now - created_ago)}, "graceUntil": {"$numberLong": str(now - created_ago)},
             "endsAt": {"$numberLong": str(now + ends_in)}, "duration": "24h",
             "fee": {"listing": {"$numberLong": "0"}, "duration": {"$numberLong": "0"}, "refunded": False},
             "claims": {"sellerCoins": "NONE", "sellerItem": "NONE", "buyerItem": "NONE", "sellerItemQty": {"$numberLong": "0"}, "buyerItemQty": {"$numberLong": "0"}},
             "noticed": {"seller": False}}
        r = BD.parse(json.dumps(d))
        Store.LIVE.put(rid, r)
        return r
    base = [
        rec("Weapon_Sword_Iron", 5000, "WEAPONS", 50000, 3600000, name="Iron Sword"),
        rec("Armor_Iron_Chest", 12000, "ARMOR", 40000, 600000, name="Iron Chestplate"),
        rec("Tool_Pickaxe_Iron", 800, "MISC", 30000, 7200000, name="Iron Pickaxe"),
        rec("Skyy_Talisman_Speed", 25000, "ACCESSORIES", 20000, 900000, name="Speed Talisman", seller="Alice"),
        rec("Ingredient_Bar_Iron", 100, "MISC", 60000, 5000000, name="Iron Bar", qty=10),
        rec("Food_Bread", 50, "CONSUMABLES", 70000, 4000000, name="Bread"),
        rec("Rock_Stone_Brick", 20, "BLOCKS", 80000, 3000000, name="Stone Brick"),
        rec("Skyy_Unid_Weapon_Sword", 3000, "MISC", 15000, 3500000, name="Unidentified Sword"),
        rec("Skyy_Unid_Bag_Rare", 2500, "MISC", 14000, 3400000, name="Rare Mystery Bag"),
        rec("Skyy_Sack_Mining", 900, "MISC", 13000, 3300000, name="Mining Sack"),
        rec("SkyyFishing_Rod_Wood", 700, "MISC", 12000, 3200000, name="Wooden Rod"),
        rec("Weapon_Kunai_Onyxium", 900000, "WEAPONS", 1000, 60000, name="Onyxium Kunai", seller="Alice"),
        rec("Armor_Adamantite_Legs", 70000, "ARMOR", 2000, 7000000, name="Adamantite Legs"),
        rec("Weapon_Bow_Untiered", 5000, "WEAPONS", 3000, 3600000, name="Old Bow"),
        rec("Skyy_Unid_Armor_Chest", 1500, "MISC", 4000, 3700000, name="Unidentified Chestplate"),
        rec("Mystery_Widget", 333, "MISC", 5000, 2000000, name="Widget")]
    # 26 more Iron Ore listings for paging (Materials: 26 + bar + brick = 28 -> 4 pages of 8)
    ores = [rec("Ore_Iron", 10 * (i + 1), "MISC", 100000 + i, 1000000 + 1000 * i, name="Iron Ore", seller="Miner") for i in range(26)]
    # a closed and a read-only record never show up
    rx = rec("Weapon_Sword_Iron", 1, "WEAPONS", 1, 1000000, name="Sold Sword")
    rx.put("state", JClass("org.bson.BsonString")("SOLD"))
    ry = rec("Weapon_Sword_Iron", 1, "WEAPONS", 1, -1000, name="Expired Sword")
    ALL = base + ores
    py = {}
    for r in ALL:
        iid = str(Rec.subStr(r, "item", "id", ""))
        py[str(Rec.id(r))] = {"id": iid, "price": int(Rec.lng(r, "price", 0)), "created": int(Rec.lng(r, "createdAt", 0)),
                              "ends": int(Rec.lng(r, "endsAt", 0)), "num": int(Rec.numId(r)), "search": str(Rec.str(r, "search", "")),
                              "stored": str(Rec.str(r, "category", "")), "lvl": GEAR[iid][1] if iid in GEAR else -1}

    # ---------------------------------------------------------------- X2 fcat on records + cache + the asset path
    Item.FCACHE.clear()
    for r in ALL:
        p_ = py[str(Rec.id(r))]
        K.eq(str(Item.fcat(r)), fcat_py(p_["id"], p_["stored"]), "X2 fcat %s" % p_["id"])
    K.check(Item.FCACHE.size() == len(set((py[k]["id"], py[k]["stored"]) for k in py)), "X2: FCACHE holds one entry per id + stored category (%d)" % Item.FCACHE.size())
    K.eq(str(Item.fcat(base[0])), "WEAPONS", "X2 fcat from the cache")
    # the asset branch: a REAL Item (Unsafe-made, categories + a Tool block) in the item asset map
    asset_note = "not reached"
    try:
        uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
        uf.setAccessible(True)
        us = uf.get(None)
        ItemC = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")

        def setf(obj, cls, name, val):
            k = cls.class_
            while k is not None:
                try:
                    f = k.getDeclaredField(name)
                    f.setAccessible(True)
                    f.set(obj, val)
                    return True
                except Exception:
                    k = k.getSuperclass()
            return False
        # the bare JVM has no item asset store: a HytaleAssetStore shell (Unsafe) holding a fresh DefaultAssetMap becomes Item.ASSET_STORE
        DAM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
        sf = ItemC.class_.getDeclaredField("ASSET_STORE")
        sf.setAccessible(True)
        old_store = sf.get(None)
        # HytaleAssetStore's static init reads the parsed server options (the gear harness' engine_boot does the same)
        JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "x-universe")]))
        shell = us.allocateInstance(JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore").class_)
        amap0 = DAM()
        K.check(setf(shell, JClass("com.hypixel.hytale.assetstore.AssetStore"), "assetMap", amap0), "X2: the stand-in store holds a DefaultAssetMap")
        sf.set(None, shell)
        amap = ItemC.getAssetMap()
        K.check(amap.equals(amap0), "X2: Item.getAssetMap() is the stand-in map")
        inner = None
        try:
            f = DAM.class_.getDeclaredField("assetMap")
            f.setAccessible(True)
            inner = f.get(amap)
        except Exception:
            inner = None
        if inner is None:
            asset_note = "item asset map has no reachable inner map (%s)" % amap.getClass().getName()
        else:
            it1 = us.allocateInstance(ItemC.class_)
            K.check(setf(it1, ItemC, "id", "Test_Fancy_Chair") and setf(it1, ItemC, "categories", JArray(JString)(["Furniture.Furniture"])),
                    "X2: stand-in chair fields")
            it2 = us.allocateInstance(ItemC.class_)
            K.check(setf(it2, ItemC, "id", "Test_Hammer") and setf(it2, ItemC, "tool", us.allocateInstance(JClass("com.hypixel.hytale.server.core.asset.type.item.config.ItemTool").class_)),
                    "X2: stand-in hammer fields")
            it3 = us.allocateInstance(ItemC.class_)
            K.check(setf(it3, ItemC, "id", "Test_Gem") and setf(it3, ItemC, "categories", JArray(JString)(["Items.Ingredients", "Blocks.Ores"])),
                    "X2: stand-in gem fields")
            K.check(it2.getTool() is not None and it1.getTool() is None and list(it3.getCategories()) == ["Items.Ingredients", "Blocks.Ores"],
                    "X2: the stand-ins answer getTool / getCategories")
            inner.put("Test_Fancy_Chair", it1)
            inner.put("Test_Hammer", it2)
            inner.put("Test_Gem", it3)
            K.check(amap.getAsset("Test_Hammer") is not None, "X2: the stand-in Item is in the item asset map")
            K.eq(str(Item.fcat(BD.parse('{"item":{"id":"Test_Fancy_Chair"},"category":"BLOCKS"}'))), "OTHER", "X2 asset: Furniture.* block -> OTHER")
            K.eq(str(Item.fcat(BD.parse('{"item":{"id":"Test_Hammer"},"category":"MISC"}'))), "TOOLS", "X2 asset: Tool block -> TOOLS")
            K.eq(str(Item.fcat(BD.parse('{"item":{"id":"Test_Gem"},"category":"MISC"}'))), "MATERIALS", "X2 asset: Items.Ingredients -> MATERIALS")
            asset_note = "asset branch executed (Furniture / Tool / Ingredients)"
            for k in ("Test_Fancy_Chair", "Test_Hammer", "Test_Gem"):
                inner.remove(k)
        sf.set(None, old_store)
    except Exception as e:
        asset_note = "asset branch error: %s" % str(e)[:200]
    K.check(asset_note.startswith("asset branch executed"), "X2: " + asset_note)
    K.notes.append("X2: " + asset_note)

    # ---------------------------------------------------------------- X3 levelOfRec
    Item.LCACHE.clear()
    f_lvl.calls = 0
    for r in ALL:
        p_ = py[str(Rec.id(r))]
        K.eq(int(Item.levelOfRec(r)), p_["lvl"], "X3 levelOfRec %s" % p_["id"])
    c0 = f_lvl.calls
    for r in ALL:
        Item.levelOfRec(r)
    K.eq(f_lvl.calls, c0, "X3: the second pass is served from LCACHE (bridge calls)")
    r0 = base[0]
    r0.put("rev", JClass("org.bson.BsonInt64")(2))
    Item.levelOfRec(r0)
    K.eq(f_lvl.calls, c0 + 1, "X3: a new rev re-reads the level")
    br.put("config:epoch:SkyyGear", Integer.valueOf(7))
    Item.levelOfRec(r0)
    K.eq(f_lvl.calls, c0 + 2, "X3: a SkyyGear config epoch change re-reads the level")
    br.remove("gear:fn:level")
    K.eq(int(Item.levelOfRec(r0)), 20, "X3: same key, cached (the level fn is not asked)")
    br.put("gear:tiers", TIERS + ",x:X:#000000")
    K.eq(int(Item.levelOfRec(r0)), -1, "X3: no gear:fn:level after a tiers change -> -1")
    br.put("gear:tiers", TIERS)
    br.put("gear:fn:level", f_lvl)
    br.put("gear:fn:level", Fn(lambda o: "bad"))
    br.put("config:epoch:SkyyGear", Integer.valueOf(8))
    K.eq(int(Item.levelOfRec(r0)), -1, "X3: a non-number answer -> -1")
    br.put("gear:fn:level", Fn(lambda o: Integer.valueOf(-4)))
    br.put("config:epoch:SkyyGear", Integer.valueOf(9))
    K.eq(int(Item.levelOfRec(r0)), -1, "X3: a negative level -> -1")
    br.put("gear:fn:level", f_lvl)
    br.put("config:epoch:SkyyGear", Integer.valueOf(10))
    K.eq(int(Item.levelOfRec(r0)), 20, "X3: back to the real level")

    # ---------------------------------------------------------------- X4 parseLv / lvText
    for s_, want in (("", 0), ("  ", 0), (None, 0), ("7", 7), (" 12 ", 12), ("007", 7), ("999", 999), ("1000", 999), ("12345", -1),
                     ("-5", -1), ("a", -1), ("1a", -1), ("0", 0), ("4.5", -1)):
        K.eq(int(Page.parseLv(s_)), want, "X4 parseLv(%r)" % (s_,))
    for a, z, want in ((0, 0, ""), (10, 0, "Lv 10+"), (0, 20, "Lv up to 20"), (10, 20, "Lv 10 to 20"), (15, 15, "Lv 15")):
        K.eq(str(Page.lvText(a, z)), want, "X4 lvText(%d, %d)" % (a, z))

    # ---------------------------------------------------------------- a real page (FakeAhPage: AhPage whose rebuild() only counts)
    us_f = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    us_f.setAccessible(True)
    UNS = us_f.get(None)
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UUID = JClass("java.util.UUID")
    me = UUID.fromString("00000000-0000-0000-0000-0000000000a1")
    pr = UNS.allocateInstance(PR.class_)
    for fname, val in (("uuid", me), ("username", JString("Tester"))):
        f = PR.class_.getDeclaredField(fname)
        f.setAccessible(True)
        f.set(pr, val)
    FP = JClass(FAKE_PKG + ".FakeAhPage")
    pg = FP(pr)
    K.eq((int(pg.cat), int(pg.sort), int(pg.rar), int(pg.lvMin), int(pg.lvMax), bool(pg.lvShown), str(pg.view)), (0, 0, 0, 0, 0, False, "browse"),
         "X5 a new page starts on the defaults")
    K.eq([str(x) for x in Page.SORT_NAME], ["Price low-high", "Price high-low", "Ending soonest", "Newest listed"], "X5 sort names")

    def oracle(cat=0, rar_name=None, lo=0, hi=0, q="", sort=0, gear=True):
        out_ = []
        for r in ALL:
            k = str(Rec.id(r))
            p_ = py[k]
            if cat and fcat_py(p_["id"], p_["stored"]) != FCAT[cat]:
                continue
            if rar_name is not None and str(Item.tierOfRec(r)) != rar_name:
                continue
            if gear and (lo or hi):
                l = p_["lvl"]
                if l < 0 or (lo and l < lo) or (hi and l > hi):
                    continue
            if q and q.strip().lower() not in p_["search"]:
                continue
            out_.append(k)
        keyf = {0: lambda k: (py[k]["price"], py[k]["ends"], py[k]["num"]), 1: lambda k: (-py[k]["price"], py[k]["ends"], py[k]["num"]),
                2: lambda k: (py[k]["ends"], py[k]["num"]), 3: lambda k: (-py[k]["created"], py[k]["ends"], py[k]["num"])}[sort]
        return sorted(out_, key=keyf)

    def got(p_):
        return [str(Rec.id(r)) for r in p_.results(now)]

    def setp(p_, cat=0, rar=0, lo=0, hi=0, q="", sort=0):
        p_.cat, p_.rar, p_.lvMin, p_.lvMax, p_.query, p_.sort, p_.browsePage = cat, rar, lo, hi, q, sort, 0
    Item.tiers()
    TN = [str(x) for x in Item.TIER_NAME]
    K.check(TN[:8] == ["Normal", "Unique", "Rare", "Legendary", "Fabled", "Mythic", "Set", "Untiered"],
            "X6: the rarity ladder is gear:tiers first, incl. Mythic / Set / Untiered: %s" % TN)
    # ---------------------------------------------------------------- X6 results: each sort, each category, each rarity, levels, combos
    for so in range(4):
        setp(pg, sort=so)
        K.eq(got(pg), oracle(sort=so), "X6 sort %d (%s), no filter" % (so, Page.SORT_NAME[so]))
    K.check(got(pg)[0] == str(Rec.id(base[11])), "X6: Newest listed puts the 1 s old Kunai first")
    setp(pg, sort=2)
    K.check(got(pg)[0] == str(Rec.id(base[11])), "X6: Ending soonest puts the 60 s Kunai first")
    setp(pg, sort=1)
    K.check(got(pg)[0] == str(Rec.id(base[11])), "X6: Price high-low puts the 900,000 Kunai first")
    setp(pg, sort=0)
    K.check(got(pg)[0] == str(Rec.id(ores[0])), "X6: Price low-high puts a 10-coin ore first")
    K.check(str(Rec.id(rx)) not in got(pg) and str(Rec.id(ry)) not in got(pg), "X6: sold / expired records never show")
    counts = {}
    for ci in range(8):
        for so in range(4):
            setp(pg, cat=ci, sort=so)
            g = got(pg)
            K.eq(g, oracle(cat=ci, sort=so), "X6 category %s sort %d" % (FCAT[ci], so))
        counts[FCAT[ci]] = len(g)
    K.notes.append("X6 category counts: %s" % counts)
    K.check(all(counts[c] > 0 for c in FCAT), "X6: every category button has listings in the test set")
    for ri in range(len(TN) + 1):
        setp(pg, rar=ri)
        K.eq(got(pg), oracle(rar_name=None if ri == 0 else TN[ri - 1]), "X6 rarity %s" % ("Any" if ri == 0 else TN[ri - 1]))
    for nm, n in (("Mythic", 1), ("Set", 1), ("Untiered", 1), ("Rare", 3)):
        setp(pg, rar=TN.index(nm) + 1)
        K.eq(len(got(pg)), n, "X6 rarity %s count" % nm)
    for lo, hi in ((10, 0), (0, 20), (10, 25), (20, 20), (46, 0), (0, 4), (1, 999)):
        for so in (0, 3):
            setp(pg, lo=lo, hi=hi, sort=so)
            K.eq(got(pg), oracle(lo=lo, hi=hi, sort=so), "X6 level %d..%d sort %d" % (lo, hi, so))
    setp(pg, lo=46)
    K.eq(got(pg), [], "X6: Lv 46+ = empty")
    setp(pg, lo=1)
    K.check(all(py[k]["lvl"] >= 1 for k in got(pg)) and len(got(pg)) == len(GEAR), "X6: any level bound hides every non-gear listing")
    combos = [dict(cat=1, q="sword"), dict(cat=1, q="SWORD"), dict(cat=5, q="ore", sort=1), dict(rar=TN.index("Rare") + 1, lo=15, hi=35),
              dict(cat=2, rar=TN.index("Set") + 1, lo=30), dict(cat=7, q="bag"), dict(q="alice", sort=3), dict(cat=4, q="alice"),
              dict(cat=1, q="nothing-like-this"), dict(cat=6, lo=1), dict(cat=3, lo=10, hi=20, q="pick", sort=2)]
    for cb in combos:
        setp(pg, **cb)
        o_ = dict(cb)
        if "rar" in o_:
            o_["rar_name"] = TN[o_.pop("rar") - 1]
        K.eq(got(pg), oracle(**o_), "X6 combination %r" % (cb,))
    setp(pg, cat=1, q="nothing-like-this")
    K.eq(got(pg), [], "X6: an empty result")
    # SkyyGear off: the level bound is ignored, rarities fall back to the vanilla tiers
    gear_off()
    Item.LCACHE.clear()
    setp(pg, lo=10, hi=20)
    K.eq(got(pg), oracle(gear=False), "X6: without SkyyGear the level bound is ignored")
    gear_on()

    # ---------------------------------------------------------------- X7 readFields / browseAct
    def data(a, q="", lo="", hi=""):
        return json.dumps({"a": a, "@AhSearch": q, "@AhLvMin": lo, "@AhLvMax": hi})
    setp(pg)
    pg.browsePage = 3
    K.check(pg.readFields(data("search", "Sword", "10", "30")) is None, "X7 readFields: a good level -> no warning")
    K.eq((str(pg.query), int(pg.lvMin), int(pg.lvMax), int(pg.browsePage)), ("Sword", 10, 30, 0), "X7 readFields search + levels, page 1")
    pg.browsePage = 2
    pg.readFields(data("search", "Sword", "10", "30"))
    K.eq(int(pg.browsePage), 2, "X7 readFields: nothing changed -> the page stays")
    pg.readFields(data("search", "Sword", "40", "5"))
    K.eq((int(pg.lvMin), int(pg.lvMax)), (5, 40), "X7 readFields: min > max is swapped")
    w = pg.readFields(data("search", "Sword", "abc", "50"))
    K.check(w is not None and "whole number" in str(w), "X7 readFields: a bad level warns: %r" % w)
    K.eq((int(pg.lvMin), int(pg.lvMax)), (5, 50), "X7 readFields: the bad bound keeps its old value, the good one applies")
    pg.readFields(data("search", "  " + "x" * 60 + "  ", "", ""))
    K.eq((len(str(pg.query)), int(pg.lvMin), int(pg.lvMax)), (40, 0, 0), "X7 readFields: search cut at 40, empty levels clear")
    pg.readFields(json.dumps({"a": "search", "@AhSearch": "bow"}))
    K.eq((str(pg.query), int(pg.lvMin)), ("bow", 0), "X7 readFields: search only (no level keys = SkyyGear off)")
    K.check(pg.readFields(None) is None, "X7 readFields(null)")
    pg.lvMin = 7
    pg.readFields(json.dumps({"a": "x", "@AhPrice": "5"}))
    K.eq(int(pg.lvMin), 7, "X7 readFields: a Create event leaves the browse fields alone")
    setp(pg)
    for i in range(8):
        K.check(pg.browseAct("cat:%d" % i) and int(pg.cat) == i, "X7 browseAct cat:%d" % i)
    pg.browseAct("cat:8")
    pg.browseAct("cat:-1")
    pg.browseAct("cat:x")
    K.eq(int(pg.cat), 7, "X7 browseAct: out-of-range categories are ignored")
    so_seen = []
    for _ in range(5):
        pg.browsePage = 2
        pg.browseAct("sort")
        so_seen.append(int(pg.sort))
    K.eq(so_seen, [1, 2, 3, 0, 1], "X7 browseAct sort cycles the 4 orders")
    K.eq(int(pg.browsePage), 0, "X7 browseAct sort -> page 1")
    rr = []
    for _ in range(len(TN) + 1):
        pg.browseAct("rar")
        rr.append(int(pg.rar))
    K.eq(rr, list(range(1, len(TN) + 1)) + [0], "X7 browseAct rarity cycles Any + every tier")
    for a in ("refresh", "search"):
        K.check(pg.browseAct(a), "X7 browseAct %s handled" % a)
    pg.query = "abc"
    pg.browseAct("clear")
    K.eq(str(pg.query), "", "X7 browseAct clear")
    pg.browsePage = 0
    pg.browseAct("prev")
    K.eq(int(pg.browsePage), 0, "X7 browseAct prev at page 1 stays")
    pg.browseAct("next")
    pg.browseAct("next")
    pg.browseAct("prev")
    K.eq(int(pg.browsePage), 1, "X7 browseAct next / prev")
    setp(pg, cat=3, rar=2, lo=4, hi=9, q="zz", sort=2)
    pg.browsePage = 3
    K.check(pg.browseAct("reset"), "X7 browseAct reset handled")
    K.eq((int(pg.cat), int(pg.sort), int(pg.rar), str(pg.query), int(pg.lvMin), int(pg.lvMax), int(pg.browsePage)), (0, 0, 0, "", 0, 0, 0),
         "X7 reset -> every default")
    K.check("reset" in str(pg.status).lower(), "X7 reset says so: %r" % str(pg.status))
    for a in ("view:0", "nav:create", "buy", "mprev", "unknown"):
        K.check(not pg.browseAct(a), "X7 browseAct does not take %s" % a)
    K.check(not pg.browseAct(None), "X7 browseAct(null)")
    K.check(not pg.filtersOn(), "X7 filtersOn after reset")
    for kw in (dict(cat=1), dict(rar=1), dict(lo=3), dict(hi=3), dict(q="a")):
        setp(pg, **kw)
        K.check(pg.filtersOn(), "X7 filtersOn %r" % kw)
    setp(pg)
    K.eq(str(pg.filterLine()), "Showing every listing", "X7 filterLine default")
    setp(pg, cat=1, rar=TN.index("Rare") + 1, lo=10, hi=20, q="sword")
    K.eq(str(pg.filterLine()), "Showing Weapons, Rare, Lv 10 to 20, 'sword'", "X7 filterLine all filters")
    setp(pg, q="y" * 40, cat=6, rar=TN.index("Legendary") + 1, lo=100, hi=200)
    K.check(len(str(pg.filterLine())) <= 80, "X7 filterLine is clipped to 80: %r" % str(pg.filterLine()))
    K.eq(str(pg.filterLine()), "Showing Consumables, Legendary, Lv 100 to 200, '" + "y" * 16 + "..'", "X7 filterLine cuts the search at 18")
    try:
        sys.path.insert(0, TOOLS)
        import skyyui as SUI
        wst = "Showing Consumables, Legendary, Lv 100 to 200, '" + "W" * 16 + "..'"
        K.check(SUI.text_width(wst, 14) <= 636, "X7 the widest summary fits its 636 px label: %d" % SUI.text_width(wst, 14))
    except ImportError:
        K.notes.append("X7: skyyui not importable - width not measured")

    # ---------------------------------------------------------------- X8 render (Browse view through the real UI builders)
    def render(p_):
        b, ev = UCB(), UEB()
        p_.render(b, ev, me, None)
        # (type, selector, data, text); an appendInline carries its markup in text, a set its JSON value in data
        cmds = [(str(c.type), str(c.selector) if c.selector is not None else None, str(c.data) if c.data is not None else None,
                 str(c.text) if c.text is not None else None) for c in b.getCommands()]
        evs = [(str(e.type), str(e.selector), str(e.data) if e.data is not None else "") for e in ev.getEvents()]
        return cmds, evs

    def texts(cmds):
        d_ = {}
        for t_, sel, dat, txt in cmds:
            if sel and sel.endswith(".Text"):
                v_ = json.loads(dat) if dat else dat
                d_[sel[1:-5]] = v_.get("0") if isinstance(v_, dict) else v_
        return d_

    def blob(cmds):
        return "\n".join("%s %s %s" % (sel, dat, txt) for _t, sel, dat, txt in cmds)

    def top_heights(cmds):
        hs = []
        for t_, sel, dat, txt in cmds:
            mk = (txt or "") if t_ != "Set" else ""
            if sel == "#SkyyAh" and mk:
                m = re.match(r"\s*\w+(?:\s+#\w+)?\s*\{\s*Anchor:\s*\(([^)]*)\)", mk)
                if m:
                    mh = re.search(r"Height:\s*(\d+)", m.group(1))
                    hs.append(int(mh.group(1)) if mh else 0)
        return hs
    setp(pg)
    pg.view = "browse"
    cmds, evs = render(pg)
    T_ = texts(cmds)
    bl = blob(cmds)
    K.check(bool(pg.lvShown), "X8: SkyyGear loaded -> the level fields are shown")
    K.eq([T_.get("SkyyAhCat%d" % i) for i in range(8)], CAT_LABELS, "X8: the 8 category buttons")
    K.eq(T_.get("SkyyAhSort"), "Sort: Price low-high", "X8: the default sort button")
    K.eq(T_.get("SkyyAhRar"), "Rarity: Any", "X8: the rarity button")
    K.eq(T_.get("SkyyAhReset"), "Reset", "X8: the Reset button")
    K.eq(T_.get("SkyyAhFiltTxt"), "Showing every listing", "X8: the summary line")
    K.check("TextField #SkyyAhLvMin" in bl and "TextField #SkyyAhLvMax" in bl, "X8: the two level fields")
    K.check(any(sel == "#SkyyAhLvMin" and t_ == "Validating" for t_, sel, d_ in evs), "X8: Enter in the min field applies")
    K.check(any(sel == "#SkyyAhLvMax" and t_ == "Validating" for t_, sel, d_ in evs), "X8: Enter in the max field applies")
    bev = [d_ for t_, sel, d_ in evs if sel.startswith("#SkyyAh")]
    K.check(bev and all("#SkyyAhLvMin.Value" in d_ and "#SkyyAhSearch.Value" in d_ for d_ in bev),
            "X8: every Browse binding (incl. the top nav) carries the search + level fields")
    K.eq(T_.get("SkyyAhPageTxt"), "Page 1 / %d - %d listings" % ((len(ALL) + 7) // 8, len(ALL)), "X8: the pager")
    hs = top_heights(cmds)
    K.check(sum(hs) <= 880 - 2 * 14, "X8: the Browse view fits the 852 inner px: %d (%s)" % (sum(hs), hs))
    K.notes.append("X8: browse height %d of 852 (%d top-level parts)" % (sum(hs), len(hs)))
    K.check("#6a2e2e" not in [x for t_, sel, d_, x in cmds if x and "TextButton #SkyyAhReset " in x][0], "X8: Reset is not red on the defaults")
    K.check("Width: 1120, Height: 880" in bl, "X8: the page root is still 1120 x 880")
    # filters on -> gold rarity, red Reset, summary, empty text
    setp(pg, cat=1, rar=TN.index("Mythic") + 1, lo=10, hi=50, q="kunai", sort=1)
    cmds, evs = render(pg)
    T_ = texts(cmds)
    K.eq(T_.get("SkyyAhSort"), "Sort: Price high-low", "X8: the sort button follows the order")
    K.eq(T_.get("SkyyAhRar"), "Rarity: Mythic", "X8: the rarity button follows the tier")
    vals = dict((sel, dat) for t_, sel, dat, x in cmds if sel and sel.endswith(".Value"))
    K.check("10" in (vals.get("#SkyyAhLvMin.Value") or ""), "X8: the min field shows 10: %r" % vals.get("#SkyyAhLvMin.Value"))
    K.check("50" in (vals.get("#SkyyAhLvMax.Value") or ""), "X8: the max field shows 50: %r" % vals.get("#SkyyAhLvMax.Value"))
    K.check("#6a2e2e" in [x for t_, sel, d_, x in cmds if x and "TextButton #SkyyAhReset " in x][0], "X8: Reset turns red when filters are on")
    K.check("#e0b060" in [x for t_, sel, d_, x in cmds if x and "TextButton #SkyyAhRar " in x][0], "X8: the rarity button is gold while picked")
    K.eq(T_.get("SkyyAhPageTxt"), "Page 1 / 1 - 1 listing", "X8: one Mythic Kunai")
    setp(pg, cat=1, q="nothing-like-this")
    cmds, evs = render(pg)
    K.eq(texts(cmds).get("SkyyAhEmpty"), "Nothing matches these filters - click Reset to see every listing", "X8: empty with filters")
    hs = top_heights(cmds)
    K.check(sum(hs) <= 852, "X8: the empty Browse view fits: %d" % sum(hs))
    setp(pg, q="nothing-like-this")
    cmds, evs = render(pg)
    K.eq(texts(cmds).get("SkyyAhEmpty"), "No match for 'nothing-like-this'", "X8: empty with only a search")
    saved = dict((k, Store.LIVE.get(k)) for k in list(Store.LIVE.keySet()))
    Store.LIVE.clear()
    setp(pg)
    cmds, evs = render(pg)
    K.eq(texts(cmds).get("SkyyAhEmpty"), "Nothing listed here yet - be the first: Create BIN", "X8: empty market")
    for k, v in saved.items():
        Store.LIVE.put(k, v)
    # paging: Materials = 28 listings = 4 pages; a page past the end clamps
    setp(pg, cat=5)
    pg.browsePage = 9
    cmds, evs = render(pg)
    K.eq(texts(cmds).get("SkyyAhPageTxt"), "Page 4 / 4 - 28 listings", "X8: a page past the end clamps to the last page")
    K.eq(int(pg.browsePage), 3, "X8: browsePage clamped")
    K.eq(sum(1 for x in pg.rowIds if x is not None), 4, "X8: the last page holds 4 rows")
    want_last = oracle(cat=5)[24:28]
    K.eq([str(x) for x in pg.rowIds if x is not None], want_last, "X8: the last page rows are the oracle's 25th-28th")
    hs = top_heights(cmds)
    K.check(sum(hs) <= 852, "X8: a part-filled page fits: %d" % sum(hs))
    # SkyyGear off: no level field, no level binding anywhere
    gear_off()
    setp(pg, lo=10)
    cmds, evs = render(pg)
    T_ = texts(cmds)
    K.check(not bool(pg.lvShown), "X8: SkyyGear off -> no level fields")
    K.eq(T_.get("SkyyAhLvOff"), "Level filter needs SkyyGear", "X8: SkyyGear off -> the hint")
    K.check("SkyyAhLvMin" not in blob(cmds) and not any("SkyyAhLvMin" in d_ or "SkyyAhLvMin" in sel for t_, sel, d_ in evs),
            "X8: SkyyGear off -> nothing refers to the level fields")
    K.eq((int(pg.lvMin), int(pg.lvMax)), (0, 0), "X8: SkyyGear off clears a stale level bound")
    K.check(sum(top_heights(cmds)) <= 852, "X8: SkyyGear off fits")
    gear_on()
    # the Manage view never binds the level fields (lvShown is only true on a Browse render)
    setp(pg)
    pg.view = "manage"
    cmds, evs = render(pg)
    K.check(not bool(pg.lvShown) and not any("SkyyAhLvMin" in d_ for t_, sel, d_ in evs), "X8: Manage view binds no level field")
    pg.view = "browse"

    # ---------------------------------------------------------------- X9 handleDataEvent: the real click path
    pg2 = FP(pr)
    render(pg2)

    def click(a, q="", lo="", hi="", extra=None):
        d_ = {"a": a, "@AhSearch": q, "@AhLvMin": lo, "@AhLvMax": hi}
        if extra:
            d_.update(extra)
        n0 = int(pg2.rebuilds)
        pg2.handleDataEvent(None, None, json.dumps(d_))
        K.eq(int(pg2.rebuilds), n0 + 1, "X9 click %s rebuilds once" % a)
    click("cat:2")
    K.eq(int(pg2.cat), 2, "X9 category click")
    click("sort")
    click("sort")
    K.eq(int(pg2.sort), 2, "X9 two sort clicks -> Ending soonest")
    click("rar")
    K.eq(int(pg2.rar), 1, "X9 rarity click")
    click("search", q="iron", lo="20", hi="30")
    K.eq((str(pg2.query), int(pg2.lvMin), int(pg2.lvMax)), ("iron", 20, 30), "X9 Enter / Search applies search + levels")
    click("search", q="iron", lo="2x", hi="30")
    K.check("whole number" in str(pg2.status) and int(pg2.statusKind) == 2, "X9 a bad level shows the warning: %r" % str(pg2.status))
    K.eq(int(pg2.lvMin), 20, "X9 the bad level keeps the old bound")
    click("reset", q="iron", lo="20", hi="30")
    K.eq((int(pg2.cat), int(pg2.sort), int(pg2.rar), str(pg2.query), int(pg2.lvMin), int(pg2.lvMax)), (0, 0, 0, "", 0, 0),
         "X9 Reset wins over the fields it carries")
    K.check("reset" in str(pg2.status).lower(), "X9 Reset status")
    click("cat:5")
    click("next")
    click("next")
    K.eq(int(pg2.browsePage), 2, "X9 two Next clicks")
    click("cat:5")
    K.eq(int(pg2.browsePage), 0, "X9 a category click goes back to page 1")
    click("next")
    click("search", lo="1")
    K.eq(int(pg2.browsePage), 0, "X9 a new level bound goes back to page 1")
    click("prev")
    K.eq(int(pg2.browsePage), 0, "X9 Prev on page 1 stays")
    click("clear", q="abc")
    K.eq(str(pg2.query), "", "X9 Clear")
    click("view:0")
    K.eq(str(pg2.view), "item", "X9 View still opens a listing (the old path after browseAct)")
    click("back")
    K.eq(str(pg2.view), "browse", "X9 Back")
    K.save(asset=asset_note)


# ====================================================================================================== C: class compare
EXPECT = {
    "AhItem": {"+f FCAT", "+f FCAT_LABEL", "+f MAT_PREFIX", "+f TOOL_PREFIX", "+f FCACHE", "+f LCACHE", "+m fcatRule", "+m fcat",
               "+m levelOfRec", "~<clinit>"},
    "AhPage": {"+f lvMin", "+f lvMax", "+f lvShown", "~<clinit>", "~c ", "~m evd", "+m parseLv", "+m lvText", "+m filtersOn",
               "+m filterLine", "~m results", "~m renderBrowse", "~m render", "+m readFields", "+m browseAct", "~m handleDataEvent"},
    "SkyyAuctionsPlugin": {"~m setup"},     # the version text
    "AhCmds": {"~m status"},                # the version text (/ahadmin)
}


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
                # ldc / ldc_w: the same constant, only the pool index width differs once the pool passes 256 entries
                # and the jump targets move with it (ldc_w is one byte longer): compare the instruction, not the offset
                ln_ = re.sub(r"^ldc_w ", "ldc ", re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, cpl_))))
                lines_.append(re.sub(r"^((?:if\w*|goto(?:_w)?|jsr(?:_w)?)) -?\d+$", r"\1", ln_))
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
    K.check(na == nb, "C: the same classes (added %s, removed %s)" % (sorted(set(nb) - set(na)), sorted(set(na) - set(nb))))
    diffs = {}
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn), members(pb, cn)
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(PKG):]] = set(("+" if k not in ma else ("-" if k not in mb else "~")) + (k.split("(")[0] if not k.startswith("c ") else "c ")
                                       for k in dd)
    print("C. class compare 0.1.2 -> 0.1.3:")
    for k in sorted(diffs):
        print("   %-20s %s" % (k, ", ".join(sorted(diffs[k]))))
    K.eq(sorted(diffs), sorted(EXPECT), "C: the classes that differ")
    for k in EXPECT:
        K.eq(sorted(diffs.get(k, set())), sorted(EXPECT[k]), "C: %s members" % k)
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    ea = [n for n in za.namelist() if not n.endswith(".class")]
    eb = [n for n in zb.namelist() if not n.endswith(".class")]
    ed = sorted(n for n in set(ea) | set(eb) if n not in ea or n not in eb or za.read(n) != zb.read(n))
    K.eq(ed, ["manifest.json"], "C: non-class entries changed")
    K.notes.append("C: %s" % {k: sorted(v) for k, v in diffs.items()})
    K.save()


# ====================================================================================================== D: start twice on a live copy
def tree_hash(d):
    out_ = {}
    for base, _dirs, files in os.walk(d):
        for f in files:
            p_ = os.path.join(base, f)
            out_[os.path.relpath(p_, d)] = hashlib.sha1(open(p_, "rb").read()).hexdigest()
    return out_


def run_live(out, home):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR], verify=True)
    Paths = JClass("java.nio.file.Paths")
    Cfg, Lg, Store, Util = JClass(PKG + "AhCfg"), JClass(PKG + "AhLog"), JClass(PKG + "AhStore"), JClass(PKG + "AhUtil")
    Item, Rec = JClass(PKG + "AhItem"), JClass(PKG + "AhRec")
    Sys = JClass("java.lang.System")
    Sys.getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    dir_ = Paths.get(home)
    h0 = tree_hash(home)
    res = []
    for start in (1, 2):
        Store.LIVE.clear()
        Cfg.DIR = dir_
        Cfg.FILE = dir_.resolve("config.properties")
        Cfg.BLOCKED = dir_.resolveSibling("Skyy_Market").resolve("blocked.txt")
        Lg.FILE = dir_.resolve("auctions.log")
        Store.DIR = dir_
        Store.LDIR = dir_.resolve("listings")
        Store.ADIR = dir_.resolve("archive")
        Store.BADDIR = dir_.resolve("listings").resolve("bad")
        Store.STATE = dir_.resolve("state.properties")
        m = Cfg.migrate()
        Cfg.load()
        nb = Cfg.loadBlocked()
        Cfg.applyBuiltin()
        n = Store.load()
        rs = Store.restoreFromLog()
        un = Lg.scanStarts()
        h = tree_hash(home)
        K.eq(h, h0, "D: start %d changes no file in the copy" % start)
        now = int(Sys.currentTimeMillis())
        act = Store.active(now)
        cats = {}
        for i in range(act.size()):
            c = str(Item.fcat(act.get(i)))
            cats[c] = cats.get(c, 0) + 1
        res.append((int(n), int(rs), int(un), int(nb), int(act.size()), cats))
        K.notes.append("D start %d: migrate=%r open=%d restored=%d unfinished=%d blocked=%d active=%d categories=%s"
                       % (start, str(m) if m is not None else None, n, rs, un, nb, act.size(), cats))
    K.eq(res[0], res[1], "D: both starts read the same")
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
    for flag, fn in (("--mkfake", lambda: run_mkfake(arg("--mkfake"))), ("--verify", lambda: run_verify(arg("--out"))),
                     ("--exec", lambda: run_exec(arg("--out"))), ("--compare", lambda: run_compare(arg("--out"))),
                     ("--live", lambda: run_live(arg("--out"), arg("--live"))), ("--audit", lambda: run_audit(arg("--out")))):
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
    assert sc.startswith(os.path.realpath(os.path.join(TOOLS, "dev", "scratch", "ah013")) + os.sep), "the scratch folder must be inside tools/dev/scratch/ah013"
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        for label, flag in (("verify", "--verify"), ("exec", "--exec"), ("compare", "--compare")):
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        if os.path.isdir(LIVE_DIR):
            home = os.path.join(SCRATCH, "live", "Skyy_SkyyAuctions")
            shutil.copytree(LIVE_DIR, home)
            mk = os.path.join(os.path.dirname(LIVE_DIR), "Skyy_Market")
            if os.path.isdir(mk):
                shutil.copytree(mk, os.path.join(SCRATCH, "live", "Skyy_Market"))
            print("D. live Skyy_SkyyAuctions copied (read-only source %s)" % LIVE_DIR)
            out = os.path.join(SCRATCH, "live.json")
            pr = child(env, "--live", home, "--out", out)
            check(pr.returncode == 0, "D: the child exited cleanly")
            take(out, "live")
        else:
            check(False, "D: no live Skyy_SkyyAuctions folder at %s" % LIVE_DIR)
        outa = os.path.join(SCRATCH, "audit.json")
        pa = child(env, "--audit", "--out", outa)
        check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            check(not a["refused"] and a["refs"] > 1000, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: the control is refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, 0 refused, control refused" % (a["refs"], a["classes"]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyAuctions %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
