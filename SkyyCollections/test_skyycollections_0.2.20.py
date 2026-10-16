"""Harness for SkyyCollections 0.2.20 (round tools01 part B: the Enchanted Stick + recipe rewards only while their recipe is loaded + the
stone-table reader fix; tools/collections_0_2_20_patch.py). Build first:
    python tools/collections_0_2_20_patch.py && python SkyyCollections/build_skyycollections_0.2.20.py

    python SkyyCollections/test_skyycollections_0.2.20.py [--jar <SkyyCollections-0.2.20.jar>] [--dir <scratch>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.19 -> 0.2.20: exactly the listed members differ; non-class entries: manifest.json + server.lang + the Enchanted Stick's
                3 files (item JSON, texture, icon) - nothing else (the 32 stone recipe files and every other Enchanted file byte-identical)
  J    jar      the Enchanted Stick: item JSON (recipe = 100 Ingredient_Stick -> 1, Workbench Compressing tab, KnowledgeRequired, quality
                Enchanted, stack 100, not placeable), its files = tools/skyyench.py rebuilt now (byte-identical), Model / Texture / Icon
                exist, lang name + description = "T1 Crude - ..." (tools/tier_tags.py), 20 Enchanted items / recipes in the jar, server.lang
                = 0.2.19's + exactly the Stick's 4 lines; the stone recipe files = 0.2.19's; the ready line / manifest say 20
  X    exec     EXECUTED on the compiled classes (registry from the default files in scratch): CollEnch table row 20 (idx, name, recipe,
                TKEY ench.tier.stick, TDEF 3, COLL Stick, CREDIT Ingredient_Stick); load: absent key = 3 (no migration), 5 read, bad = 3;
                the fresh config.properties carries ench.tier.stick=3; Server Setup row ench.tier.stick (CollKit.checkEnchTier 1..ladder);
                merge puts the Stick recipe at the Stick collection tier III once; compute: Stick tier II = no, tier III = the recipe
                (bought tier never); wantSig / syncData over the 20 managed entries (learn + forget the Stick, a foreign entry kept);
                alias(Skyy_Ench_Stick, 1) = 100 Ingredient_Stick, 64 ok, 65 refused; bare JVM (no recipe store) = every recipe shown;
                the 32 stone recipes never pay at the SkyyBazaar 0.1.16 jar's REAL (x4.5) prices (base x1.1 / x0.9 and its quotes)
  H    hide     recipe rewards on a REAL engine CraftingRecipe store (AssetRegistryLoader.init, recipes decoded through the store codec and
                loaded with loadAssets): validate() puts Tool_Hoe_Copper's recipe at Wheat III; SkyyGear-style removeAssets of it AFTER
                the check -> recipesAt / rewardText / rewardLines (chat + "Next:" line) / CollCraft.query (CRAFT button) / compute0
                (coll:recipes) leave it out, the other recipes of the store stay; loading it again shows it again (the cache follows the
                store); rewards.properties / config.properties bytes untouched
  D    live     a scratch COPY of the live Skyy_SkyyCollections (NewBetaTest; read-only source) with 0.2.19 and 0.2.20 (loadAll + validate
                + every profile's unlocks, twice): the folder bytes never change; 0.2.20's unlocks = 0.2.19's + only the Enchanted Stick
                recipe, and only for a profile at Stick tier III+
  AA   audit    the engine-access audit
Scratch: tools/dev/scratch/tools01-ench/coll (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "ci"))
import skyybuild as B
import harness_kit as HK
import skyyench as EN
import tier_tags as TT



def loader_for(jar):
    """the jar in its own class loader (the 0.2.11 harness's helper; that harness runs at import, so it is not loaded here)"""
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


VERSION = "0.2.20"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-0.2.19.jar")
BZ_JAR = os.path.join(ROOT, "SkyyBazaar", "SkyyBazaar-0.1.16.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "tools01-ench", "coll")))
PKG = "com.skyy.collections."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCollections")
STICK = EN.PREFIX + "Stick"
STICK_RID = STICK + EN.RECIPE_SUFFIX
LANG = "Server/Languages/en-US/server.lang"
EXPECT = {
    "CollReg": ["+f RLIVE", "+f RLIVEN", "+m loaded", "+m liveOnly", "~m recipesAt", "~m configText", "~<clinit>", "~m rewardsText"],   # <clinit>: RLIVE's map
    # B1: the catch-up table + giver with its marker name, the catch-up in settle / itemOwed
    "CollRewards": ["+f CU_COLL", "+f CU_TIER", "+f CU_ID", "+f CU_N", "+m giveTierM", "+m cuHas", "+m cuTier", "+m cuBase", "+m cuOwed",
                    "~m giveTier", "~m itemOwed", "~m settle", "~<clinit>"],
    "CollEnch": ["~<clinit>"],                         # the table arrays: + the Stick row
    "EnchRank": ["~<clinit>"],                         # the Compressing tab order (table order): + the Stick
    "SkyyCollectionsPlugin": ["~m setup"],              # the ready line
    "CfgFn": ["~m opExport"],                           # the kit's version text
    "CfgRows": ["~<clinit>", "~m header"],              # + the ench.tier.stick row, the version text
    "CfgFile": ["~<clinit>"],                           # the default config.properties text (+ ench.tier.stick=3)
}
ADDED = ["CollToolMig"]
STICK_FILES = ["Server/Item/Items/SkyyCollections/%s.json" % STICK, "Common/Items/SkyyCollections/Ench/Stick.png",
               "Common/Icons/ItemsGenerated/SkyyCollections_Ench_Stick.png"]

if HK.arg("--phase") == "compare":
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            exp = sorted(["manifest.json", LANG] + STICK_FILES)
            return self.check(sorted(got) == exp, "C: non-class entries changed = manifest.json + server.lang + the Enchanted Stick's 3 files "
                                                  "(extra %s, missing %s)" % (sorted(set(got) - set(exp)), sorted(set(exp) - set(got))))
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq


def stones():
    k = ["Aqua", "Basalt", "Calcite", "Chalk", "Lime", "Magma_Cooled", "Marble", "Quartzite", "Sandstone", "Sandstone_Red", "Sandstone_White",
         "Shale", "Slate", "Stone", "Stone_Mossy", "Volcanic"]
    return [(s, "Rock_Stone_Cobble_Mossy" if s == "Stone_Mossy" else "Rock_%s_Cobble" % s, "Rubble_" + s) for s in k]


# ------------------------------------------------------------------------------------------------------------------- J: the jar
def run_jar(out, jar, scratch, _home):
    import skyyart as SA
    K = HK.Child(out)
    z, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    names = set(z.namelist())
    with SA.assets() as az:
        vnames = set(az.namelist())
        files, _lang = EN.build_assets(az, SA)
    for p in STICK_FILES:
        K.check(p in names and p not in zo.namelist(), "J %s is new in the jar" % p)
        d = files.get(p)
        K.check(d is not None and z.read(p) == (d.encode("utf-8") if isinstance(d, str) else d), "J %s = tools/skyyench.py rebuilt now (byte-identical)" % p)
    n = json.loads(z.read(STICK_FILES[0]))
    r = n["Recipe"]
    K.eq((r["Input"], r["OutputQuantity"], r["KnowledgeRequired"]), ([{"ItemId": "Ingredient_Stick", "Quantity": 100}], 1, True),
         "J the recipe = 100 Ingredient_Stick -> 1, KnowledgeRequired")
    K.eq(r["BenchRequirement"], [{"Type": "Crafting", "Id": "Workbench", "Categories": ["Workbench_SkyyCompressing"]}], "J Workbench, Compressing tab")
    K.check("BlockType" not in n and n["MaxStack"] == 100 and n["Quality"] == "Skyy_Enchanted" and "Interactions" not in n,
            "J not placeable, stack 100, quality Enchanted")
    for k in ("Model", "Texture", "Icon"):
        q = "Common/" + n[k]
        K.check(q in names or q in vnames, "J %s %s exists (jar or Assets.zip)" % (k, n[k]))
    K.eq(SA.png_size(z.read("Common/" + n["Icon"])), (64, 64), "J the icon is 64 x 64")
    items = [p for p in names if p.startswith("Server/Item/Items/SkyyCollections/") and p.endswith(".json")]
    K.eq(sorted(os.path.basename(p)[:-5] for p in items), sorted(EN.IDS), "J the 20 Enchanted item JSONs")
    # lang: 0.2.19's + exactly the Stick's 4 lines; the description carries the tier tag first
    ln, lo = z.read(LANG).decode("utf-8").split("\n"), zo.read(LANG).decode("utf-8").split("\n")
    K.eq(sorted(set(ln) - set(lo)), sorted(l for l in ln if STICK + "." in l), "J server.lang = 0.2.19's + only the Stick's lines")
    K.eq(sorted(set(lo) - set(ln)), [], "J server.lang: no 0.2.19 line removed or changed")
    st = [l for l in ln if STICK + "." in l]
    K.eq(len(st), 4, "J 4 Stick lang lines (items. / server.items. name + description)")
    tag = TT.tag_for(STICK)
    K.check(tag.startswith("T1 ") and all(l.split("=", 1)[1].startswith(tag + " - ") for l in st if ".description=" in l)
            and all(l.split("=", 1)[1] == "Enchanted Stick" for l in st if ".name=" in l), "J name 'Enchanted Stick', description starts '%s - '" % tag)
    K.notes.append("J: %s" % [l for l in st if l.startswith("items.") and ".description=" in l][0])
    # the stone recipe files: 0.2.19's, and still no profit at the Bazaar 0.1.16 jar's real (x4.5) seed prices
    sr = sorted(p for p in names if p.startswith("Server/Item/Recipes/SkyyCollections/"))
    K.check(len(sr) == 32 and all(z.read(p) == zo.read(p) for p in sr) and sr == sorted(p for p in zo.namelist() if p.startswith("Server/Item/Recipes/")),
            "J the 32 stone recipe files = 0.2.19's (byte-identical)")
    plug = z.read("com/skyy/collections/SkyyCollectionsPlugin.class")
    K.check(b"0.2.20 ready" in plug and b"20 Enchanted materials" in plug and b"19 Enchanted" not in plug, "J the ready line: 0.2.20, 20 Enchanted materials")
    K.check("including the 20 Enchanted materials" in json.loads(z.read("manifest.json"))["Description"], "J the manifest says 20")
    K.save(stone_files=[(p, json.loads(z.read(p))) for p in sr])


# ------------------------------------------------------------------------------------------------------------------- X: exec
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    L = loader_for(jar)
    jc = lambda n: JClass(PKG + n, loader=L)
    En, Reg, Store, Util, Unl, Kit = jc("CollEnch"), jc("CollReg"), jc("CollStore"), jc("CollUtil"), jc("CollUnlocks"), jc("CollKit")
    Paths, Props, HashMap, HashSet, UUID = (JClass("java.nio.file.Paths"), JClass("java.util.Properties"), JClass("java.util.HashMap"),
                                            JClass("java.util.HashSet"), JClass("java.util.UUID"))
    k = int(En.idx(STICK))
    K.eq((k, len(En.ID), str(En.ID[k]), str(En.RID[k]), str(En.NAME[k]), str(En.TKEY[k]), int(En.TDEF[k]), str(En.COLL[k]), str(En.CREDIT[k])),
         (19, 20, STICK, STICK_RID, "Enchanted Stick", "ench.tier.stick", 3, "Stick", "Ingredient_Stick"), "X CollEnch row 20 = the Enchanted Stick")
    K.eq((str(Util.prettyItem(STICK)), str(Util.recipeLabel(STICK_RID)), int(Util.bagRank(STICK_RID)), bool(Util.autoOk(STICK_RID))),
         ("Enchanted Stick", "Enchanted Stick recipe", 9, False), "X names, coins never buy it, the auto rule refuses it")
    # config: absent = the default 3 (no one-time migration), a value read, a bad value = 3
    K.check(str(En.load(Props())).endswith("/3") and int(En.TIER[k]) == 3, "X load: no ench.tier.stick line = tier 3 (the default)")
    p = Props()
    p.setProperty("ench.tier.stick", "5")
    En.load(p)
    K.eq(int(En.TIER[k]), 5, "X load: ench.tier.stick=5 is read")
    p.setProperty("ench.tier.stick", "zero")
    En.load(p)
    K.eq(int(En.TIER[k]), 3, "X load: a bad value = 3")
    En.load(Props())
    # registry from the default files
    wbase = os.path.join(scratch, "x", "Skyy_SkyyCollections")
    os.makedirs(wbase)
    Reg.BASE = Paths.get(wbase)
    Store.DIR = Paths.get(wbase).resolve("counts")
    Reg.loadAll()
    R = Reg.D
    cfg = open(os.path.join(wbase, "config.properties"), encoding="utf-8").read()
    K.check("ench.tier.stick=3" in cfg and str(Reg.configText()) == cfg, "X the fresh config.properties carries ench.tier.stick=3 (= configText)")
    BYID = dict((str(R.id[c]), c) for c in range(R.n))
    sc = BYID["Stick"]
    mx = int(Reg.maxTier(R, sc))
    K.check(Kit.checkEnchTier("ench.tier.stick", "1") is None and Kit.checkEnchTier("ench.tier.stick", str(mx)) is None
            and Kit.checkEnchTier("ench.tier.stick", str(mx + 1)) is not None and Kit.checkEnchTier("ench.tier.stick", "x") is not None,
            "X Server Setup row ench.tier.stick: 1..%d accepted, %d / x refused" % (mx, mx + 1))
    rows = open(os.path.join(wbase, "config.properties"), encoding="utf-8").read()
    allp = HashSet()
    for r_ in EN.RIDS:
        allp.add(r_)
    o1 = HashMap()
    note = str(En.merge(o1, R, allp))
    where = [str(kk) for kk in o1.keySet() if STICK_RID in [str(x) for x in o1.get(kk)]]
    K.eq(where, ["%d.3" % sc], "X merge: the Stick recipe at the Stick collection tier III, once (%s)" % note)
    K.check("20 of 20" in note, "X merge note: %s" % note)
    # compute: Stick II -> no, Stick III -> yes
    rec = HashMap()
    for c in range(R.n):
        for t_ in range(1, int(Reg.maxTier(R, c)) + 1):
            toks = Reg.REWARDS.get(str(R.id[c]).lower() + "." + str(t_))
            if toks is not None:
                ids = [str(x)[7:].strip() for x in toks if str(x).startswith("recipe:")]
                if ids:
                    rec.put("%d.%d" % (c, t_), JArray(JString)(ids))
    En.merge(rec, R, allp)
    Reg.RECIPES = rec
    Reg.VALIDATED = True
    cd = os.path.join(wbase, "counts")
    os.makedirs(cd, exist_ok=True)
    got = {}
    for t_ in (2, 3):
        uid = "11111111-2222-3333-4444-00000000000%d" % t_
        open(os.path.join(cd, uid + ".properties"), "w").write("_schema=2\nIngredient_Stick=%d\n" % int(Reg.threshold(R, sc, t_)))
        got[t_] = sorted(str(x) for x in Unl.compute(Store.data(UUID.fromString(uid))))
    K.check(STICK_RID not in got[2] and STICK_RID in got[3], "X compute: Stick tier II does not unlock it, tier III does")
    K.check(all(not str(x).startswith(EN.PREFIX) or str(x) == STICK_RID for x in got[3]), "X compute: Stick III unlocks no other Enchanted recipe")
    # bare JVM: no CraftingRecipe store -> loaded() shows everything (as before)
    rs = Reg.recipesAt(sc, 3)
    K.check(STICK_RID in [str(x) for x in rs] and bool(Reg.loaded("Anything_Recipe_Generated_0")), "X no recipe store (bare JVM): every recipe shown")
    # knowledge over the 20 managed entries
    some = HashSet()
    some.add(STICK_RID)
    w = str(En.wantSig(some))
    K.eq(w, "0" * 19 + "1", "X wantSig: 20 entries, the Stick last")
    PCD = JClass("com.hypixel.hytale.server.core.entity.entities.player.data.PlayerConfigData")
    pd = PCD()
    ks = HashSet()
    ks.add("Armor_Bronze_Chest")
    pd.setKnownRecipes(ks)
    K.check(bool(En.syncData(pd, w)) and sorted(str(x) for x in pd.getKnownRecipes()) == sorted(["Armor_Bronze_Chest", STICK]),
            "X syncData: the Stick is learned, a foreign entry kept")
    K.check(bool(En.syncData(pd, "0" * 20)) and sorted(str(x) for x in pd.getKnownRecipes()) == ["Armor_Bronze_Chest"], "X syncData: forgotten again")
    K.check(En.next(pd.getKnownRecipes(), "0" * 19) is None, "X next: a 19-long (old) want is refused")
    # alias credit
    a1, a64 = En.alias(STICK, 1), En.alias(STICK, 64)
    K.check(a1 is not None and str(a1[0]) == "Ingredient_Stick" and int(a1[1].longValue()) == 100 and int(a64[1].longValue()) == 6400
            and En.alias(STICK, 65) is None and En.alias(STICK, 0) is None, "X coll:fn:add alias: 1 / 64 Enchanted Sticks = 100 / 6400 Sticks; 0 / 65 refused")
    # the stone recipes (0.2.19's) at the SkyyBazaar 0.1.16 jar's REAL seed prices (x4.5): still no profit at the 10 % spread
    sp_ = importlib.util.spec_from_file_location("bz016test", os.path.join(ROOT, "SkyyBazaar", "test_skyybazaar_0.1.16.py"))
    T16 = importlib.util.module_from_spec(sp_)
    sp_.loader.exec_module(T16)
    bz = T16.Bz16(BZ_JAR, os.path.join(scratch, "bz"))
    z = zipfile.ZipFile(jar)
    eco = []
    for p_ in sorted(n_ for n_ in z.namelist() if n_.startswith("Server/Item/Recipes/SkyyCollections/")):
        d_ = json.loads(z.read(p_))
        i_, qi = d_["Input"][0]["ItemId"], d_["Input"][0]["Quantity"]
        o_, qo = d_["PrimaryOutput"]["ItemId"], d_["PrimaryOutput"]["Quantity"]
        pi, po = float(bz.C.get(i_).base), float(bz.C.get(o_).base)
        if bool(bz.C.isAuto(i_)) or bool(bz.C.isAuto(o_)) or not (qo * po * 0.9 < qi * pi * 1.1):
            eco.append((os.path.basename(p_), pi, po))
        if bz.q(o_, qo, False) >= bz.q(i_, qi, True):
            eco.append((os.path.basename(p_), "quote", bz.q(i_, qi, True), bz.q(o_, qo, False)))
    K.eq(eco, [], "X the 32 stone recipes never pay at the SkyyBazaar 0.1.16 prices (fixed, x4.5: Cobblestone %g, Stone Rubble %g)"
         % (float(bz.C.get("Rock_Stone_Cobble").base), float(bz.C.get("Rubble_Stone").base)))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- H: hide
def engine_stores(scratch):
    """a bare server: Options, a HytaleServer with an EventBus, a Universe with no players, then AssetRegistryLoader.init (the real stores)"""
    from jpype import JClass, JArray, JString
    Uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    Uf.setAccessible(True)
    U = Uf.get(None)

    def jf(cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(scratch, "universe")]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    jf(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    jf(HS, "instance").set(None, hs)
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu, wm = CHM(), CHM()
    jf(UNI, "playersByUuid").set(uni, pbu)
    jf(UNI, "players").set(uni, JClass("java.util.Collections").unmodifiableCollection(pbu.values()))
    jf(UNI, "worlds").set(uni, wm)
    jf(UNI, "worldsByUuid").set(uni, CHM())
    jf(UNI, "unmodifiableWorlds").set(uni, JClass("java.util.Collections").unmodifiableMap(wm))
    jf(UNI, "instance").set(None, uni)
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()


def run_hide(out, jar, scratch, _home):
    from jpype import JClass
    import skyyart as SA
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    engine_stores(scratch)
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    AEI, ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo"), JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR, Paths, AL, Coll = (JClass("com.hypixel.hytale.codec.util.RawJsonReader"), JClass("java.nio.file.Paths"), JClass("java.util.ArrayList"),
                            JClass("java.util.Collections"))
    st = AR.getAssetStore(CRR.class_)

    def load(rid, d):
        ei = AEI(Paths.get(rid + ".json"), ADT(CRR.class_, rid, None))
        o = st.getCodec().decodeJsonAsset(RJR.fromJsonString(json.dumps(d)), ei)
        lst = AL()
        lst.add(o)
        return not st.loadAssets("Hytale:Hytale", lst).hasFailed()
    # the vanilla recipes as the game generates them from the item JSONs (<item>_Recipe_Generated_0): the Wheat ladder's tools
    want = {"Tool_Sickle_Crude": 1, "Tool_Hoe_Copper": 3, "Tool_Sickle_Copper": 4}
    with SA.assets() as az:
        ip = dict((os.path.basename(n)[:-5], n) for n in az.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
        ok = True
        for item in want:
            r = json.loads(az.read(ip[item]).decode("utf-8-sig"))["Recipe"]
            d = {"Input": r["Input"], "PrimaryOutput": {"ItemId": item, "Quantity": r.get("OutputQuantity", 1)},
                 "BenchRequirement": r.get("BenchRequirement", []), "TimeSeconds": r.get("TimeSeconds", 0)}
            ok = load(item + "_Recipe_Generated_0", d) and ok
    K.check(ok and int(CRR.getAssetMap().getAssetMap().size()) == 3, "H: 3 vanilla tool recipes decoded + loaded into the REAL CraftingRecipe store")
    L = loader_for(jar)
    jc = lambda n: JClass(PKG + n, loader=L)
    Reg, Store, Unl, Craft = jc("CollReg"), jc("CollStore"), jc("CollUnlocks"), jc("CollCraft")
    wbase = os.path.join(scratch, "h", "Skyy_SkyyCollections")
    os.makedirs(wbase)
    Reg.BASE = Paths.get(wbase)
    Store.DIR = Paths.get(wbase).resolve("counts")
    Reg.loadAll()
    files0 = dict((f, open(os.path.join(wbase, f), "rb").read()) for f in ("rewards.properties", "config.properties"))
    # 0.2.20 B1: the default file no longer names tool recipes - the 0.2.19 Wheat lines (a live file an admin kept) go in memory here
    from jpype import JArray as _JA, JString as _JS
    for k_, r_ in (("wheat.1", "Tool_Sickle_Crude"), ("wheat.3", "Tool_Hoe_Copper"), ("wheat.4", "Tool_Sickle_Copper")):
        Reg.REWARDS.put(k_, _JA(_JS)(["recipe:%s_Recipe_Generated_0" % r_]))
    v = str(Reg.validate())
    R = Reg.D
    wc = [c for c in range(R.n) if str(R.id[c]) == "Wheat"][0]
    hoe, crude, cop = ("%s_Recipe_Generated_0" % i for i in ("Tool_Hoe_Copper", "Tool_Sickle_Crude", "Tool_Sickle_Copper"))
    at = lambda t: [str(x) for x in Reg.recipesAt(wc, t)]
    K.check(at(3) == [hoe] and at(1) == [crude] and at(4) == [cop], "H validate: Wheat I / III / IV = Crude Sickle / Copper Hoe / Copper Sickle recipes (%s)" % v[:120])
    lines3 = [str(x) for x in Reg.rewardLines(R, wc, 3)]
    K.check(any("Copper Hoe" in x for x in lines3), "H before: Wheat III's reward lines name the Copper Hoe recipe (%s)" % lines3)
    # a profile at Wheat IV: coll:recipes holds the three
    cd = os.path.join(wbase, "counts")
    os.makedirs(cd)
    uid = "11111111-2222-3333-4444-555555555555"
    open(os.path.join(cd, uid + ".properties"), "w").write("_schema=2\nPlant_Crop_Wheat_Item=%d\n" % int(Reg.threshold(R, wc, 4)))
    d = Store.data(JClass("java.util.UUID").fromString(uid))
    before = sorted(str(x) for x in Unl.compute(d))
    K.check(set([hoe, crude, cop]) <= set(before), "H before: compute (coll:recipes) holds the 3 tool recipes")
    un = JClass("java.util.HashSet")()
    for x in before:
        un.add(x)
    K.check(Craft.query(Reg.recipesAt(wc, 3), un) is not None, "H before: Wheat III has a CRAFT query (%s)" % Craft.query(Reg.recipesAt(wc, 3), un))
    # SkyyGear 0.3.13's move, AFTER the start-up check: the Copper Hoe recipe leaves the store
    gone = st.removeAssets(Coll.singletonList(hoe))
    K.check(hoe in [str(x) for x in gone] and CRR.getAssetMap().getAsset(hoe) is None, "H: removeAssets took the Copper Hoe recipe out (%s)" % gone)
    K.eq((at(1), at(3), at(4)), ([crude], [], [cop]), "H after: recipesAt leaves the removed recipe out, the others stay")
    l3 = [str(x) for x in Reg.rewardLines(R, wc, 3)]
    t3 = str(Reg.rewardText(R, wc, 3))
    K.check(not any("Hoe" in x for x in l3) and "Hoe" not in t3, "H after: rewardLines (chat, 'Next:') / rewardText (tier row) no longer name it (%s | %s)" % (l3, t3))
    K.check(Craft.query(Reg.recipesAt(wc, 3), un) is None, "H after: Wheat III has no CRAFT button (query = null)")
    after = sorted(str(x) for x in Unl.compute(d))
    K.eq(sorted(set(before) - set(after)), [hoe], "H after: compute (coll:recipes) loses exactly the removed recipe")
    # it comes back with the recipe (the cache follows the store)
    ok2 = None
    with SA.assets() as az:
        r = json.loads(az.read(ip["Tool_Hoe_Copper"]).decode("utf-8-sig"))["Recipe"]
        ok2 = load(hoe, {"Input": r["Input"], "PrimaryOutput": {"ItemId": "Tool_Hoe_Copper", "Quantity": 1},
                         "BenchRequirement": r.get("BenchRequirement", []), "TimeSeconds": r.get("TimeSeconds", 0)})
    K.check(ok2 and at(3) == [hoe] and hoe in [str(x) for x in Unl.compute(d)], "H again: loaded again -> shown again (no restart)")
    K.eq(dict((f, open(os.path.join(wbase, f), "rb").read()) for f in files0), files0, "H: rewards.properties / config.properties untouched")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- D: live
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    before = HK.tree_hash(home)
    keys = sorted(f[:-11] for f in os.listdir(os.path.join(home, "counts")) if f.endswith(".properties")) if os.path.isdir(os.path.join(home, "counts")) else []
    res, stick3 = {}, {}
    for start in (1, 2):
        for tag, j in (("old", OLD_JAR), ("new", jar)):
            L = loader_for(j)
            jc = lambda n: JClass(PKG + n, loader=L)
            Reg, Store, Unl, En = jc("CollReg"), jc("CollStore"), jc("CollUnlocks"), jc("CollEnch")
            P = JClass("java.nio.file.Paths")
            Reg.BASE = P.get(home)
            Store.DIR = P.get(home).resolve("counts")
            Reg.loadAll()
            Reg.validate()
            R = Reg.D
            hs = JClass("java.util.HashSet")()           # the asset pack's Enchanted recipes, present as in game
            for r_ in [str(x) for x in En.RID]:
                hs.add(r_)
            rec = JClass("java.util.HashMap")(Reg.RECIPES)
            En.merge(rec, R, hs)
            Reg.RECIPES = rec
            sc = [c for c in range(R.n) if str(R.id[c]) == "Stick"][0]
            got = {}
            for k in keys:
                d = Store.dataK(k)
                got[k] = None if d is None else sorted(str(x) for x in Unl.compute(d))
                if tag == "new" and d is not None:
                    stick3[k] = int(Store.effTier(d, R, sc))
            res[(start, tag)] = got
        K.eq(HK.tree_hash(home), before, "D start %d: the live copy's bytes are unchanged (no migration, no rewrite)" % start)
    for k in keys:
        o, n = res[(1, "old")][k], res[(1, "new")][k]
        if o is None:
            K.check(n is None, "D %s: unreadable on both" % k[:8])
            continue
        extra = [x for x in n if x not in o]
        K.eq(([x for x in o if x not in n], extra), ([], [STICK_RID] if stick3.get(k, 0) >= 3 else []),
             "D %s: 0.2.20 = 0.2.19 + the Enchanted Stick recipe only when Stick tier >= III (tier %d)" % (k[:8], stick3.get(k, 0)))
        K.eq(res[(2, "new")][k], n, "D %s: the second start gives the same" % k[:8])
    K.notes.append("D: %d live profiles, Stick tiers %s" % (len(keys), dict((k[:8], v) for k, v in stick3.items())))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- T: tool rewards (B1)
TL_NEW = {"Wheat.1": "item:Skyy_Ench_Wheat:2,recipe:Skyy_Sack_Farming_Small_Recipe_Generated_0",
          "Wheat.3": "item:Skyy_Ench_Wheat:6,recipe:Skyy_Sack_Farming_Medium_Recipe_Generated_0", "Wheat.4": "item:Skyy_Ench_Wheat:8",
          "Wheat.6": "item:Skyy_Sigil_Unique:1", "Wheat.7": "item:Skyy_Ench_Wheat:14,recipe:Skyy_Sack_Farming_Large_Recipe_Generated_0",
          "OakLog.1": "item:Skyy_Ench_Oak:2,recipe:Skyy_Sack_Foraging_Small_Recipe_Generated_0", "OakLog.6": "item:Skyy_Sigil_Unique:1",
          "Cobblestone.1": "item:Skyy_Ench_Cobblestone:2,recipe:Skyy_Sack_Mining_Small_Recipe_Generated_0", "Cobblestone.6": "item:Skyy_Sigil_Unique:1"}
GIVE_IDS = ("Skyy_Ench_Wheat", "Skyy_Ench_Oak", "Skyy_Ench_Cobblestone", "Skyy_Sigil_Unique", "Rock_Stone")


def give_fixture():
    """the 0.2.13 harness's give fixture: an Item AssetStore stand-in (javassist subclass, allocated without a constructor) holding the
    reward items, real SimpleItemContainers per player through the SECS / ITEMOK seams. Returns (INVS, secs(), count())"""
    from jpype import JClass, JImplements, JOverride, JArray, JShort, JInt
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)

    def jf(c_, n_):
        k_ = c_.class_ if hasattr(c_, "class_") else c_
        while k_ is not None:
            try:
                f_ = k_.getDeclaredField(n_)
                f_.setAccessible(True)
                return f_
            except Exception:
                k_ = k_.getSuperclass()
        raise KeyError(n_)
    AST, ITMc, DAM = (JClass("com.hypixel.hytale.assetstore.AssetStore"), JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item"),
                      JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap"))
    jcp = JClass("javassist.ClassPool")(True)
    jct = jcp.makeClass("com.hypixel.hytale.assetstore.SkyyCollFakeStore20", jcp.get("com.hypixel.hytale.assetstore.AssetStore"))
    jct.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyCollFakeStore20() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", jct))
    HAST = JClass(jct.toClass(AST.class_).getName())
    am_ = us.allocateInstance(DAM.class_)
    jf(DAM, "assetMapLock").set(am_, JClass("java.util.concurrent.locks.StampedLock")())
    mp_ = JClass("java.util.HashMap")()
    for iid_ in GIVE_IDS:
        it_ = us.allocateInstance(ITMc.class_)
        jf(ITMc, "id").set(it_, iid_)
        jf(ITMc, "maxStack").setInt(it_, JInt(16 if "Sigil" in iid_ else 100))
        mp_.put(iid_, it_)
    jf(DAM, "assetMap").set(am_, mp_)
    st_ = us.allocateInstance(HAST.class_)
    jf(AST, "assetMap").set(st_, am_)
    jf(ITMc, "ASSET_STORE").set(None, st_)
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    ICON = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    INVS = {}

    @JImplements("java.util.function.Function")
    class SecsF(object):
        @JOverride
        def apply(self, u):
            v_ = INVS.get(str(u))
            return None if v_ is None else JArray(ICON)(v_)

    @JImplements("java.util.function.Predicate")
    class ItemOk(object):
        @JOverride
        def test(self, o):
            return True
    Rew = JClass(PKG + "CollRewards")
    Rew.SECS = SecsF()
    Rew.ITEMOK = ItemOk()

    def secs(n_st=6, n_bp=2, n_hb=2):
        return [SIC(JShort(n_st)), SIC(JShort(n_bp)), SIC(JShort(n_hb))]

    def count(cs_, iid):
        n_ = 0
        for c_ in cs_:
            for i_ in range(int(c_.getCapacity())):
                s_ = c_.getItemStack(JShort(i_))
                if s_ is not None and not s_.isEmpty() and str(s_.getItemId()) == iid:
                    n_ += int(s_.getQuantity())
        return n_
    return INVS, secs, count, (SecsF, ItemOk)


def run_tools(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JShort, JInt
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Reg, Store, Util, Rew, Tm, Cob, Kit = P("CollReg"), P("CollStore"), P("CollUtil"), P("CollRewards"), P("CollToolMig"), P("CollCobMig"), P("CollKit")
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    base = os.path.join(scratch, "t", "Skyy_SkyyCollections")
    os.makedirs(base)
    Reg.BASE = Paths.get(base)
    Store.DIR = Paths.get(base).resolve("counts")
    Reg.loadAll()
    R = Reg.D
    # ---- T1 a fresh install: the new defaults + the marker (CollToolMig never runs on it)
    DEF = str(Reg.rewardsText())
    dl = DEF.split("\n")
    K.check(str(Tm.MARK4) in dl and dl.index(str(Tm.MARK4)) == dl.index(str(P("CollSigMig").MARK3)) + 1
            and all(("%s=%s" % kv) in dl for kv in TL_NEW.items()) and "Tool_" not in DEF.replace("Tool_Shears_Basic", ""),
            "T1: a fresh rewards.properties has the 0.2.20 lines, the run-once marker under the 0.2.13 one, no normal tool recipe left")
    K.check(Tm.update(DEF) is None, "T1: CollToolMig on a fresh file = nothing to do (the marker)")
    cW, cO, cC = [int(R.byId.get(k)) for k in ("wheat", "oaklog", "cobblestone")]
    ia = lambda c, t: None if Reg.itemAt(R, c, t) is None else (str(Reg.itemAt(R, c, t)[0]), int(Reg.itemAt(R, c, t)[1]))
    K.eq([ia(cW, t) for t in (1, 3, 4, 6, 7)] + [ia(cO, 1), ia(cC, 1)],
         [("Skyy_Ench_Wheat", 2), ("Skyy_Ench_Wheat", 6), ("Skyy_Ench_Wheat", 8), ("Skyy_Sigil_Unique", 1), ("Skyy_Ench_Wheat", 14),
          ("Skyy_Ench_Oak", 2), ("Skyy_Ench_Cobblestone", 2)], "T1: itemAt reads the new item rewards")
    K.check("+2 Enchanted Wheat" in str(Reg.rewardTextB(R, cW, 1, False)) and "+14 Enchanted Wheat" in [str(x) for x in Reg.rewardLines(R, cW, 7)],
            "T1: the tier row / rank-up lines say '+2 Enchanted Wheat' / '+14 Enchanted Wheat' (%s)" % str(Reg.rewardTextB(R, cW, 1, False)))
    K.check(Kit.checkReward("rewards[Wheat.1]", TL_NEW["Wheat.1"]) is None or str(Kit.checkReward("rewards[Wheat.1]", TL_NEW["Wheat.1"])).startswith("?"),
            "T1: Server Setup accepts the new Wheat.1 value (%s)" % Kit.checkReward("rewards[Wheat.1]", TL_NEW["Wheat.1"]))
    # ---- T2 CollToolMig.update on the LIVE rewards.properties text (read only) + variants
    live = open(os.path.join(LIVE_DIR, "rewards.properties"), "rb").read().decode("latin-1")

    def upd(t_):
        r_ = Tm.update(t_)
        return None if r_ is None else (str(r_[0]), [str(x) for x in r_[1]], str(r_[2]), int(r_[3]), int(r_[4]), bool(r_[5]), int(r_[6]))

    def table(t_):
        return dict((str(k), [str(x) for x in v]) for k, v in Cob.table(JArray(JString)([l_.rstrip("\r") for l_ in t_.split("\n")])).items())
    u_ = upd(live)
    want = table(live)
    for k_, v_ in TL_NEW.items():
        want[k_.lower()] = v_.split(",")
    K.check(u_ is not None and u_[5] and u_[3] == 9 and u_[4] == 0 and u_[6] == 5 and table(u_[0]) == want and len(u_[1]) == 27
            and upd(u_[0]) is None, "T2: the LIVE file: 9 lines updated + 5 commented proposals, the loader reads exactly the old table with those 9 "
            "entries replaced, 9 Undo rows; a 2nd run = nothing (%s)" % (u_[2].strip().replace("\n", " | ")[:300] if u_ else None))
    lo, ln = live.split("\n"), u_[0].split("\n")
    changed = [(a, b) for a, b in zip(lo, [l_ for l_ in ln if l_ != str(Tm.MARK4)]) if a != b]
    K.check(len(changed) == 14 and all(a.split("=", 1)[0] == b.split("=", 1)[0] for a, b in changed), "T2: only the 9 + 5 lines changed, keys kept (%d)" % len(changed))
    crlf = live.replace("\r\n", "\n").replace("\n", "\r\n")
    uc = upd(crlf)
    K.check(uc is not None and uc[5] and uc[0].count("\r\n") == uc[0].count("\n") and uc[3] == 9, "T2: CRLF kept on every line")
    une = upd(live.rstrip("\n"))
    K.check(une is not None and une[5] and not une[0].endswith("\n") and une[3] == 9, "T2: no final newline stays none")
    hand = live.replace("Wheat.3=recipe:Tool_Hoe_Copper_Recipe_Generated_0,", "Wheat.3=recipe:Tool_Hoe_Copper_Recipe_Generated_0,coins:5,")
    uh = upd(hand)
    two_ = live.replace("Wheat.4=recipe:Tool_Sickle_Copper_Recipe_Generated_0", "Wheat.4=recipe:Tool_Sickle_Copper_Recipe_Generated_0\nWheat.4=coins:10")
    u2_ = upd(two_)
    rem = "\n".join(l_ for l_ in live.split("\n") if not l_.startswith("OakLog.6="))
    ur = upd(rem)
    K.check(uh[5] and uh[3] == 8 and uh[4] == 1 and "kept hand-edited line" in uh[2] and table(uh[0]).get("wheat.3", [None])[1] == "coins:5"
            and u2_[5] and u2_[3] == 8 and u2_[4] == 2 and ur[5] and ur[3] == 8 and "an admin removed it" in ur[2] and "oaklog.6" not in table(ur[0]),
            "T2: a hand-edited line is KEPT + logged, two lines of a key kept, a removed line not re-added: %s" % uh[2].strip().split("\n")[-1][:160])
    # ---- T3 the gives (real containers, the 0.2.13 fixture)
    INVS, secs, count, _keep = give_fixture()
    Cred = P("CollCredit")
    wheat = str(R.items[cW][0])
    thr = lambda c, t: int(Reg.threshold(R, c, t))

    def ilog():
        f_ = os.path.join(base, "rewards-items.log")
        return open(f_, encoding="utf-8").read() if os.path.isfile(f_) else ""
    # (a) a new player gathering Wheat to tier IV: the normal loop pays I + III + IV once (2 + 6 + 8)
    u1 = UUID.fromString("00000000-0000-0000-0000-0000000c0201")
    k1 = str(Util.pkey(u1))
    INVS[str(u1)] = secs()
    from jpype import JLong
    Cred.creditOne(None, u1, k1, wheat, JLong(thr(cW, 4)), True)
    d1 = Store.dataK(k1)
    a1 = (count(INVS[str(u1)], "Skyy_Ench_Wheat"), int(Store.meta(d1, "_paiditem.Wheat")), int(Store.meta(d1, "_cu020.Wheat")))
    Rew.settleAll(None, u1, k1)
    a2 = (count(INVS[str(u1)], "Skyy_Ench_Wheat"), int(Store.meta(d1, "_paiditem.Wheat")))
    K.check(a1 == (16, 4, 0) and a2 == (16, 4), "T3a: Wheat to tier IV pays 2 + 6 + 8 Enchanted Wheat once (marker 4, no catch-up); settle again = nothing: %s %s" % (a1, a2))
    # (b) a 0.2.19 player who already got the Wheat VI Sigil (marker 6) and sits at tier VII: catch-up I / III / IV + the normal VII, once
    u2 = UUID.fromString("00000000-0000-0000-0000-0000000c0202")
    k2 = str(Util.pkey(u2))
    INVS[str(u2)] = secs()
    cdir = os.path.join(base, "counts")
    os.makedirs(cdir, exist_ok=True)
    open(os.path.join(cdir, k2 + ".properties"), "w").write("_schema=2\n%s=%d\n_paid.Wheat=7\n_paidxp.Wheat=7\n_paiditem.Wheat=6\n" % (wheat, thr(cW, 7)))
    Store.DATA.remove(k2)
    d2 = Store.dataK(k2)
    Rew.settleAll(None, u2, k2)
    b1 = (count(INVS[str(u2)], "Skyy_Ench_Wheat"), count(INVS[str(u2)], "Skyy_Sigil_Unique"), int(Store.meta(d2, "_paiditem.Wheat")),
          int(Store.meta(d2, "_cu020.Wheat")), int(Store.meta(d2, "_cub020.Wheat")))
    Rew.settleAll(None, u2, k2)
    Rew.settleAll(None, u2, k2)
    b2 = (count(INVS[str(u2)], "Skyy_Ench_Wheat"), int(Store.meta(d2, "_cu020.Wheat")), int(Store.meta(d2, "_paiditem.Wheat")))
    cf = open(os.path.join(cdir, k2 + ".properties"), encoding="latin-1").read()
    gl = [l_ for l_ in ilog().split("\n") if "\tGIVE\t" in l_ and k2 in l_]
    K.check(b1 == (30, 0, 7, 4, 7) and b2 == (30, 4, 7) and "_cu020.Wheat=4" in cf and "_cub020.Wheat=7" in cf and len(gl) == 4,
            "T3b: past the Sigil (marker 6) at tier VII: catch-up I + III + IV (2 + 6 + 8) + the normal VII (14) = 30 Enchanted Wheat, no 2nd Sigil, "
            "markers _cu020=4 / _cub020=7 / _paiditem=7 on disk, 4 GIVE lines; two more settles = nothing: %s %s" % (b1, b2))
    # (c) catch-up with a full inventory: owed (owedAny), nothing given, then given once when there is room
    u3 = UUID.fromString("00000000-0000-0000-0000-0000000c0203")
    k3 = str(Util.pkey(u3))
    full = secs(1, 1, 1)
    for c_ in full:
        c_.setItemStackForSlot(JShort(0), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")("Rock_Stone", JInt(1)))
    INVS[str(u3)] = full
    open(os.path.join(cdir, k3 + ".properties"), "w").write("_schema=2\n%s=%d\n_paid.Wheat=6\n_paidxp.Wheat=6\n_paiditem.Wheat=6\n" % (wheat, thr(cW, 6)))
    Store.DATA.remove(k3)
    d3 = Store.dataK(k3)
    Rew.settleAll(None, u3, k3)
    c1 = (count(full, "Skyy_Ench_Wheat"), int(Store.meta(d3, "_cu020.Wheat")), bool(Rew.owedAny(d3, R)), bool(Rew.itemOwed(d3, R, cW, 6)))
    full[0].removeItemStackFromSlot(JShort(0))
    Rew.settleAll(None, u3, k3)
    c2 = (count(full, "Skyy_Ench_Wheat"), int(Store.meta(d3, "_cu020.Wheat")), bool(Rew.owedAny(d3, R)))
    K.check(c1 == (0, 0, True, True) and c2[1] >= 1 and c2[0] >= 2 and c2[0] <= 16, "T3c: full inventory -> owed, nothing given; with room the catch-up "
            "continues (what fits now; the rest stays owed): %s -> %s" % (c1, c2))
    # (d) an admin changed Wheat.3: the catch-up skips that tier (only the 0.2.20 default item is caught up)
    REW = Reg.REWARDS
    old3 = REW.get("wheat.3")
    REW.put("wheat.3", JArray(JString)(["item:Skyy_Ench_Wheat:20"]))
    u4 = UUID.fromString("00000000-0000-0000-0000-0000000c0204")
    k4 = str(Util.pkey(u4))
    INVS[str(u4)] = secs()
    open(os.path.join(cdir, k4 + ".properties"), "w").write("_schema=2\n%s=%d\n_paid.Wheat=6\n_paidxp.Wheat=6\n_paiditem.Wheat=6\n" % (wheat, thr(cW, 6)))
    Store.DATA.remove(k4)
    d4 = Store.dataK(k4)
    Rew.settleAll(None, u4, k4)
    REW.put("wheat.3", old3)
    K.check(count(INVS[str(u4)], "Skyy_Ench_Wheat") == 10 and int(Store.meta(d4, "_cu020.Wheat")) == 4,
            "T3d: an admin's own Wheat.3 item is not caught up (I + IV = 10): %d" % count(INVS[str(u4)], "Skyy_Ench_Wheat"))
    # (e) a profile with no item ever paid at Wheat VI: the normal loop pays I / III / IV / the Sigil, the catch-up nothing (stamp 1)
    u5 = UUID.fromString("00000000-0000-0000-0000-0000000c0205")
    k5 = str(Util.pkey(u5))
    INVS[str(u5)] = secs()
    open(os.path.join(cdir, k5 + ".properties"), "w").write("_schema=2\n%s=%d\n_paid.Wheat=6\n_paidxp.Wheat=6\n" % (wheat, thr(cW, 6)))
    Store.DATA.remove(k5)
    d5 = Store.dataK(k5)
    Rew.settleAll(None, u5, k5)
    Rew.settleAll(None, u5, k5)
    K.check((count(INVS[str(u5)], "Skyy_Ench_Wheat"), count(INVS[str(u5)], "Skyy_Sigil_Unique"), int(Store.meta(d5, "_paiditem.Wheat")),
             int(Store.meta(d5, "_cub020.Wheat")), int(Store.meta(d5, "_cu020.Wheat"))) == (16, 1, 6, 1, 0),
            "T3e: no item paid yet at Wheat VI: the normal loop pays 16 Enchanted Wheat + the Sigil, the catch-up nothing, never twice")
    Rew.SECS = None
    Rew.ITEMOK = None
    K.save()


def run_live2(out, jar, scratch, home):
    """the migration + the gives on a scratch COPY of the live folder (the setup order), started twice"""
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Reg, Store, Util, Rew, Tm = P("CollReg"), P("CollStore"), P("CollUtil"), P("CollRewards"), P("CollToolMig")
    b_ = JClass("java.nio.file.Paths").get(home)
    rf = os.path.join(home, "rewards.properties")
    old = open(rf, "rb").read()
    msgs, snaps = [], []
    for start in (1, 2):
        Reg.BASE = b_
        Store.DIR = b_.resolve("counts")
        P("CollBagMigrate").run(b_)
        P("CollBypassMig").run(b_)
        Reg.loadAll()
        P("CollCobMig").run(b_)
        P("CollSigMig").run(b_)
        P("CollShardMig").run(b_)
        msgs.append(str(Tm.run(b_)))
        snaps.append(open(rf, "rb").read())
    new = open(rf, "rb").read()
    hist = []
    for r_, _d, fs_ in os.walk(os.path.join(home, "config-history")):
        hist += [open(os.path.join(r_, f_), "rb").read() for f_ in fs_]
    chg = open(os.path.join(home, "config-changes.log"), encoding="latin-1").read() if os.path.isfile(os.path.join(home, "config-changes.log")) else ""
    rows = [l_ for l_ in chg.split("\n") if "SkyyCollections 0.2.20" in l_]
    R = Reg.D
    cW = int(R.byId.get("wheat"))
    K.check(msgs[0].startswith("tool-recipe rewards became Enchanted items") and "9 of 9" in msgs[0] and msgs[1] == "" and snaps[0] == snaps[1],
            "D2: the 1st start updates rewards.properties once (%s), the 2nd changes nothing" % msgs[0][:140])
    K.check(any(h == old for h in hist) and len(rows) == 9 and all("\trewards[" in r_ for r_ in rows) and os.path.isfile(os.path.join(home, "migration-tools.log"))
            and str(Reg.itemAt(R, cW, 1)[0]) == "Skyy_Ench_Wheat", "D2: the old file byte for byte in config-history, 9 Undo rows (rewards[<key>] old -> new) "
            "in config-changes.log, migration-tools.log, the loaded table pays Enchanted Wheat at Wheat I")
    K.notes.append("D2: Undo row: %s" % (rows[0].split("\t", 4)[-1][:200] if rows else None))
    K.check(new.count(b"\r\n") == old.count(b"\r\n") and len(new.split(b"\n")) == len(old.split(b"\n")) + 1, "D2: the line endings / line count kept (+ the marker)")
    # the gives for every live profile, twice
    INVS, secs, count, _keep = give_fixture()
    keys = sorted(f[:-11] for f in os.listdir(os.path.join(home, "counts")) if f.endswith(".properties"))
    got = {}
    for rnd in (1, 2):
        for k in keys:
            u = JClass("java.util.UUID").fromString(k.split("~")[0][:36]) if len(k) >= 36 else None
            if u is None or str(Util.pkey(u)) != k:
                continue
            INVS.setdefault(str(u), secs())
            Rew.settleAll(None, u, k)
            got[(rnd, k)] = tuple(count(INVS[str(u)], i) for i in ("Skyy_Ench_Wheat", "Skyy_Ench_Oak", "Skyy_Ench_Cobblestone"))
    K.check(len(keys) >= 1 and len(got) == 2 * len(keys), "D2: every live profile settled twice (%d profiles)" % len(keys))
    K.notes.append("D2: live gives (Enchanted Wheat / Oak / Cobblestone): %s" % dict((k[:8], got.get((1, k))) for k in keys))
    for k in keys:
        if (1, k) in got:
            d = Store.dataK(k)
            tiers = tuple(int(Store.countTier(d, R, int(R.byId.get(c)))) for c in ("wheat", "oaklog", "cobblestone"))
            exp = tuple((2 if t >= 1 else 0) + (6 if c == "wheat" and t >= 3 else 0) + (8 if c == "wheat" and t >= 4 else 0) + (14 if c == "wheat" and t >= 7 else 0)
                        for c, t in zip(("wheat", "oaklog", "cobblestone"), tiers))
            K.check(got[(1, k)] == exp and got[(2, k)] == got[(1, k)], "D2 %s (Wheat / OakLog / Cobblestone tiers %s): given %s once (a 2nd settle adds nothing)"
                    % (k[:8], tiers, got[(1, k)]))
    Rew.SECS = None
    Rew.ITEMOK = None
    K.save()


if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("jar", run_jar), ("exec", run_exec), ("hide", run_hide), ("tools", run_tools), ("live", run_live), ("live2", run_live2)], __file__,
           live=(LIVE_DIR, "Skyy_SkyyCollections"))
