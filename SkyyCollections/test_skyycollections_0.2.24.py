"""Harness for SkyyCollections 0.2.24 (round coll24: the live 102-row Enchanted table, the retired Enchanted Essence of Life -> vanilla
Greater Essence of Life 1:1, gifts sized to the tier, Eternal seeds locked to crop collection tier 4; tools/collections_0_2_24_patch.py).
Build first:
    python tools/collections_0_2_24_patch.py && python SkyyCollections/build_skyycollections_0.2.24.py

    python SkyyCollections/test_skyycollections_0.2.24.py [--jar <SkyyCollections-0.2.24.jar>] [--dir <scratch>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.23 -> 0.2.24: exactly the listed members differ; non-class entries: manifest.json, server.lang and the retired item's
                JSON (its recipe gone) - every other file byte-identical
  J    jar      102 Enchanted items with their recipe + Skyy_Ench_LifeEssence WITHOUT one (icon / texture / name kept, "Retired" text);
                no recipe anywhere makes it; the ready line / manifest say 102
  X    exec     the default rewards: no retired id, every Enchanted gift <= GIFT_SHARE % of its tier's step (and the 0.2.21 size); the
                Eternal seeds: merged at tier 4 (eternal.tier read / clamped), bagRank 9 (a BOUGHT tier never unlocks them), the auto rule
                never, coll:recipes (compute) at tier 3 / 4, the managed knowledge (learned at IV, forgotten at III, a foreign entry kept,
                ench.on off keeps them), coll:fn:eternal ("" / the reason / null), the KnowledgeRequired flag set on REAL CraftingRecipe
                objects (eterFlip, idempotent); prettyItem names; the rank gift sizes (Greater Essence for Life Essence)
  T    migr     CollRw24Mig on the 0.2.21 default (from the 0.2.23 jar), on the LIVE rewards.properties text (read only) after the older
                updates, CRLF, no final newline, hand-edited / removed lines kept, a removed gift line, a 2nd run = nothing, the new default
  G    retire   real containers: the 1:1 conversion in the same slots (storage / backpack / hotbar), other items untouched, the journal +
                _retired marker, a 2nd scan (relog) = nothing, an engine rollback after a crash (old inventory back) converts again 1:1
                (never two copies), SkyyProfiles hold / the new item not loaded = nothing done; tier + rank gifts at the new sizes, once
  D    live     the setup order on a scratch COPY of the live Skyy_SkyyCollections, started twice: CollRw24Mig once (History copy, Undo rows,
                migration-coll24.log), the 2nd start changes nothing; every live profile settled twice (gifts once)
  DP   live     every live profile's collection pages + category lists built on the kit 1.7 stand-ins (assert_menu_page on a sample) and
                the 0.2.23 page phase (menu-sweep layout kept)
  M    pages    the 0.2.23 page phase (SkyyCollections/test_skyycollections_0.2.23.py run_pages) on this jar: assert_menu_page on every view
  AA   audit    the engine-access audit
Scratch: tools/dev/scratch/coll24/coll (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "ci"))
import skyybuild as B
import harness_kit as HK
import skyyench as EN

VERSION = "0.2.24"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-0.2.23.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "coll24", "coll")))
PKG = "com.skyy.collections."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCollections")
LANG = "Server/Languages/en-US/server.lang"
RET = "Skyy_Ench_LifeEssence"
GREATER = "Ingredient_Life_Essence_Concentrated"
EXPECT = {}          # filled from the first compare run (see the bottom of this file)
ADDED = ["CollEterL", "CollRetire", "CollRetireTask", "CollRw24Mig"]

if HK.arg("--phase") == "compare":
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            exp = sorted(["manifest.json", LANG, "Server/Item/Items/SkyyCollections/%s.json" % RET])
            return self.check(sorted(got) == exp, "C: non-class entries changed = manifest.json + server.lang + the retired item's JSON (extra %s, missing %s)" % (
                sorted(set(got) - set(exp))[:5], sorted(set(exp) - set(got))[:5]))
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq


def _mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def T21():
    return _mod("t21", os.path.join(HERE, "test_skyycollections_0.2.21.py"))


def T23():
    return _mod("t23", os.path.join(HERE, "test_skyycollections_0.2.23.py"))


def P(n):
    from jpype import JClass
    return JClass(PKG + n)


CURVES = {"B": [50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000], "S": [50, 100, 250, 500, 1000, 2500, 5000, 10000, 20000],
          "R": [25, 50, 100, 250, 500, 1000, 2500, 5000], "E": [10, 25, 50, 100, 250, 500, 1000]}


# ------------------------------------------------------------------------------------------------------------------- J: the jar
def run_jar(out, jar, scratch, _home):
    K = HK.Child(out)
    z, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    its = dict((n.rsplit("/", 1)[1][:-5], json.loads(z.read(n))) for n in z.namelist() if n.startswith("Server/Item/Items/SkyyCollections/"))
    K.eq(sorted(its), sorted(EN.IDS + [RET]), "J the Enchanted item JSONs = the live 102 + the retired one")
    K.check(all("Recipe" in its[i] and its[i]["Recipe"]["Input"][0]["Quantity"] == EN.RATIO and its[i]["Recipe"]["KnowledgeRequired"] is True for i in EN.IDS),
            "J every live Enchanted item keeps its recipe (100 base -> 1, KnowledgeRequired)")
    old = json.loads(zo.read("Server/Item/Items/SkyyCollections/%s.json" % RET))
    new = its[RET]
    K.check("Recipe" not in new and dict((k, v) for k, v in old.items() if k != "Recipe") == new, "J the retired item: the 0.2.23 JSON without its recipe (nothing else changed)")
    for p in ("Common/Icons/ItemsGenerated/SkyyCollections_Ench_LifeEssence.png", "Common/Items/SkyyCollections/Ench/LifeEssence.png"):
        K.check(p in z.namelist() and z.read(p) == zo.read(p), "J the retired item keeps %s (byte-identical)" % p.rsplit("/", 1)[1])
    # no recipe of this jar (item recipes or recipe files) outputs the retired item
    outs = []
    for n in z.namelist():
        if n.startswith("Server/") and n.endswith(".json"):
            j = json.loads(z.read(n))
            r = j.get("Recipe") if "/Items/" in n else j
            if isinstance(r, dict) and (r.get("Input") or r.get("Output")):
                o = [x.get("ItemId") for x in (r.get("Output") or []) if isinstance(x, dict)] or [n.rsplit("/", 1)[1][:-5]]
                outs += o
    K.check(RET not in outs and len(outs) >= 102, "J no recipe in the jar makes %s (%d recipes)" % (RET, len(outs)))
    lang = z.read(LANG).decode("utf-8")
    lo = zo.read(LANG).decode("utf-8")
    nl = dict(l.split("=", 1) for l in lang.split("\n") if "=" in l)
    ol = dict(l.split("=", 1) for l in lo.split("\n") if "=" in l)
    ch = sorted(k for k in set(nl) | set(ol) if nl.get(k) != ol.get(k))
    K.eq(ch, sorted(["items.%s.description" % RET, "server.items.%s.description" % RET]), "J lang: only the retired item's description changed")
    K.check(nl["server.items.%s.description" % RET].startswith("Retired - Greater Essence of Life replaces it") and nl["server.items.%s.name" % RET] == "Enchanted Essence of Life",
            "J the retired item keeps its name, its description says it is retired")
    plug = z.read("com/skyy/collections/SkyyCollectionsPlugin.class")
    K.check(b"0.2.24 ready" in plug and b"102 Enchanted materials" in plug and b"Eternal seeds at crop tier" in plug, "J the ready line: 0.2.24, 102 Enchanted, Eternal seeds")
    K.check("including the 102 Enchanted materials" in json.loads(z.read("manifest.json"))["Description"], "J the manifest says 102")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- X: exec
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JObject, JInt
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    t21 = T21()
    Reg, Store, Util, En, Unl, Rb = P("CollReg"), P("CollStore"), P("CollUtil"), P("CollEnch"), P("CollUnlocks"), P("CollRebirth")
    base = t21.fresh(scratch, "x")
    R = Reg.D
    BY = dict((str(R.id[c]), c) for c in range(R.n))
    curve = lambda c: [int(Reg.threshold(R, c, t)) for t in range(1, int(Reg.maxTier(R, c)) + 1)]
    # (a) the default rewards: no retired id; every Enchanted / Greater Essence gift <= GIFT_SHARE % of its tier's step
    gifts, bad, n_tiers = 0, [], 0
    gid = set(EN.IDS) | {GREATER}
    for c in range(R.n):
        a = curve(c)
        for t in range(1, len(a) + 1):
            n_tiers += 1
            toks = [str(x) for x in (Reg.REWARDS.get(str(R.id[c]).lower() + "." + str(t)) or [])]
            if any(RET in x for x in toks):
                bad.append("%s.%d names the retired item" % (R.id[c], t))
            it = Reg.itemAt(R, c, t)
            if it is not None and str(it[0]) in gid:
                gifts += 1
                step = a[t - 1] - (a[t - 2] if t > 1 else 0)
                if int(it[1]) * 100 * EN.RATIO > EN.GIFT_SHARE * step:
                    bad.append("%s.%d gift %s x%d for a step of %d" % (R.id[c], t, it[0], int(it[1]), step))
    K.check(not bad and gifts > 200, "X the default rewards: %d Enchanted / Greater Essence gifts, each <= %d%% of its tier's step, none names the retired item (%s)" % (
        gifts, EN.GIFT_SHARE, bad[:3]))
    le = BY["LifeEssence"]
    lg = [(t, str(Reg.itemAt(R, le, t)[0]), int(Reg.itemAt(R, le, t)[1])) for t in range(1, len(curve(le)) + 1) if Reg.itemAt(R, le, t) is not None]
    K.check(len(lg) == 10 and all(i in (GREATER, "Ingredient_Life_Essence") for _t, i, _n in lg) and any(i == GREATER for _t, i, _n in lg),
            "X Life Essence gifts = Greater Essence of Life, plain Essence of Life where under one Greater (every tier): %s" % lg)
    mi = BY["Mithril"]
    mg = [(t, str(Reg.itemAt(R, mi, t)[0]), int(Reg.itemAt(R, mi, t)[1])) for t in range(1, 8) if Reg.itemAt(R, mi, t) is not None]
    K.check(mg and all(i == "Ore_Mithril" for _t, i, _n in mg), "X Mithril (Elite curve): no Enchanted Mithril gift (was 2 + 10 + 12 + 14 = 38), Mithril Ore instead: %s" % mg)
    # base-item gifts (Skyy "Give base items there"): the collection's first item, 1 - 64, <= 10 % of the step
    bb, nb = [], 0
    for c in range(R.n):
        a = curve(c)
        first = str(R.items[c][0])
        for t in range(1, len(a) + 1):
            it = Reg.itemAt(R, c, t)
            if it is not None and str(it[0]) == first and first not in gid:
                nb += 1
                step = a[t - 1] - (a[t - 2] if t > 1 else 0)
                if int(it[1]) != EN.base_gift_size(step):
                    bb.append((str(R.id[c]), t, int(it[1]), step))
    K.check(nb > 300 and not bb, "X %d base-item gifts, each = base_gift_size(step) (10 %% of the step, 1 - 64): %s" % (nb, bb[:3]))
    # (b) the Eternal seeds: tables, merge at eternal.tier, clamps, bagRank / autoOk
    E_ID, E_RID, E_COLL = [str(x) for x in En.ETER_ID], [str(x) for x in En.ETER_RID], [str(x) for x in En.ETER_COLL]
    K.check(len(E_ID) == 14 and all(r == i + "_Recipe_Generated_0" for i, r in zip(E_ID, E_RID)) and "Wheat" in E_COLL and int(En.ET_TIER) == 4,
            "X 14 Eternal seed recipes, default tier 4: %s" % E_COLL)
    K.check(all(int(Util.bagRank(r)) == 9 for r in E_RID) and not any(bool(Util.autoOk(r)) for r in E_RID) and int(Util.bagRank("Plant_Seeds_Wheat_Recipe_Generated_0")) == 0,
            "X bagRank = 9 (coins never unlock one), the auto rule never; a normal seed recipe untouched")
    have = JClass("java.util.HashSet")()
    for r in [str(x) for x in En.MRID]:
        have.add(r)
    rec = JClass("java.util.HashMap")()
    Reg.VALIDATED = True
    for c in range(R.n):
        for t in range(1, int(Reg.maxTier(R, c)) + 1):
            toks = Reg.REWARDS.get(str(R.id[c]).lower() + "." + str(t))
            ids = [str(x)[7:].strip() for x in (toks or []) if str(x).startswith("recipe:")]
            if ids:
                rec.put("%d.%d" % (c, t), JArray(JString)(ids))
    En.merge(rec, R, have)
    note = str(En.eterMerge(rec, R, have))
    Reg.RECIPES = rec
    wc = BY["Wheat"]
    K.check(E_RID[E_COLL.index("Wheat")] in [str(x) for x in (rec.get("%d.4" % wc) or [])] and "14 of 14 at crop tier 4" in note,
            "X eterMerge: Plant_Seeds_Wheat_Eternal at Wheat IV (%s)" % note)
    pr = JClass("java.util.Properties")()
    for v, want in (("3", 3), ("10", 10), ("0", 4), ("x", 4), ("11", 4)):
        pr.setProperty("eternal.tier", v)
        En.loadC1(pr)
        K.eq(int(En.ET_TIER), want, "X eternal.tier=%s -> %d (1-10, else the default 4)" % (v, want))
    En.loadC1(JClass("java.util.Properties")())
    # (c) coll:recipes + the managed knowledge at Wheat III / IV, a BOUGHT tier IV = still locked
    uid = "11111111-2222-3333-4444-0000000e2401"
    UU = JClass("java.util.UUID")
    th = lambda c, t: int(Reg.threshold(R, c, t))
    PCD = JClass("com.hypixel.hytale.server.core.entity.entities.player.data.PlayerConfigData")
    ei = [str(x) for x in En.MID].index("Plant_Seeds_Wheat_Eternal")

    def know(n, meta=""):
        d_ = t21.counts(base, uid, [("Plant_Crop_Wheat_Item", n)], meta)
        ids_ = Unl.compute(d_)
        w_ = str(En.wantSig(ids_))
        pd = PCD()
        ks = JClass("java.util.HashSet")()
        ks.add("Armor_Bronze_Chest")
        ks.add("Plant_Seeds_Wheat_Eternal")          # an admin's /recipe learn - the sync owns this entry
        pd.setKnownRecipes(ks)
        En.syncData(pd, w_)
        return set(str(x) for x in ids_), w_, sorted(str(x) for x in pd.getKnownRecipes())
    s4, w4, k4 = know(th(wc, 4))
    s3, w3, k3 = know(th(wc, 4) - 1)
    sb, wb, kb = know(th(wc, 3), "_bought.Wheat=4\n")
    rid = "Plant_Seeds_Wheat_Eternal_Recipe_Generated_0"
    K.check(rid in s4 and w4[ei] == "1" and "Plant_Seeds_Wheat_Eternal" in k4 and "Armor_Bronze_Chest" in k4,
            "X Wheat IV: coll:recipes holds the Eternal recipe, the bag is learned (a foreign entry kept)")
    K.check(rid not in s3 and w3[ei] == "0" and "Plant_Seeds_Wheat_Eternal" not in k3 and "Armor_Bronze_Chest" in k3,
            "X one Wheat short of IV: not in coll:recipes, forgotten (even an admin-learned one)")
    K.check(rid not in sb and wb[ei] == "0", "X Wheat III with tier IV BOUGHT: still locked (coins never unlock it)")
    En.ON = False
    _s, wo, _k = know(th(wc, 4))
    En.ON = True
    K.check(wo[ei] == "1" and "1" not in wo[:len(En.ID)], "X ench.on off forgets the Enchanted recipes only - the Eternal seeds stay")
    # (d) coll:fn:eternal
    Fn = lambda mode: JClass(PKG + "CollFn")(mode)
    fe = Fn("eternal")
    t21.counts(base, uid, [("Plant_Crop_Wheat_Item", 120)])
    why = fe.apply(JArray(JObject)([UU.fromString(uid), JString("Plant_Seeds_Wheat_Eternal")]))
    K.eq(str(why), "Wheat Seed Bag (Eternal) unlocks at Wheat collection IV (120 / %s)" % "{:,}".format(th(wc, 4)), "X coll:fn:eternal locked: the reason line")
    t21.counts(base, uid, [("Plant_Crop_Wheat_Item", th(wc, 4))])
    K.eq(str(fe.apply(JArray(JObject)([UU.fromString(uid), JString("Plant_Seeds_Wheat_Eternal")]))), "", "X coll:fn:eternal unlocked = \"\"")
    K.eq(str(fe.apply(JArray(JObject)([UU.fromString(uid), JString("Plant_Seeds_Wheat")]))), "", "X coll:fn:eternal: not an Eternal seed = \"\"")
    K.check(fe.apply(JArray(JObject)([JString(uid), JString("Plant_Seeds_Wheat_Eternal")])) is None and fe.apply(JString("x")) is None,
            "X coll:fn:eternal: a bad argument = null (the Bazaar refuses)")
    pr.setProperty("eternal.tier", "1")
    En.loadC1(pr)
    t21.counts(base, uid, [("Plant_Crop_Wheat_Item", th(wc, 1))])
    K.eq(str(fe.apply(JArray(JObject)([UU.fromString(uid), JString("Plant_Seeds_Wheat_Eternal")]))), "", "X eternal.tier=1: Wheat I unlocks it")
    En.loadC1(JClass("java.util.Properties")())
    # (e) the KnowledgeRequired flag on REAL CraftingRecipe objects (a fake asset store holding them)
    from jpype import JImplements, JOverride
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)

    def jf(c_, n_):
        k_ = c_.class_
        while k_ is not None:
            try:
                f_ = k_.getDeclaredField(n_)
                f_.setAccessible(True)
                return f_
            except Exception:
                k_ = k_.getSuperclass()
        raise KeyError(n_)
    AST, CRR, DAM = (JClass("com.hypixel.hytale.assetstore.AssetStore"), JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe"),
                     JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap"))
    jcp = JClass("javassist.ClassPool")(True)
    jct = jcp.makeClass("com.hypixel.hytale.assetstore.SkyyCollFakeStore24", jcp.get("com.hypixel.hytale.assetstore.AssetStore"))
    jct.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyCollFakeStore24() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", jct))
    HAST = JClass(jct.toClass(AST.class_).getName())
    am_ = us.allocateInstance(DAM.class_)
    jf(DAM, "assetMapLock").set(am_, JClass("java.util.concurrent.locks.StampedLock")())
    mp_ = JClass("java.util.HashMap")()
    objs = {}
    for r in E_RID[:-1]:          # the last one "not loaded"
        o = us.allocateInstance(CRR.class_)
        jf(CRR, "id").set(o, r)
        mp_.put(r, o)
        objs[r] = o
    jf(CRR, "knowledgeRequired").setBoolean(objs[E_RID[0]], True)
    jf(DAM, "assetMap").set(am_, mp_)
    st_ = us.allocateInstance(HAST.class_)
    jf(AST, "assetMap").set(st_, am_)
    jf(CRR, "ASSET_STORE").set(None, st_)
    before = [bool(objs[r].isKnowledgeRequired()) for r in E_RID[:-1]]
    n1 = str(En.eterFlip())
    after = [bool(objs[r].isKnowledgeRequired()) for r in E_RID[:-1]]
    n2 = str(En.eterFlip())
    K.check(before.count(True) == 1 and all(after) and "13 of 14 recipes need knowledge (1 already), 1 not loaded" in n1 and "(13 already)" in n2,
            "X eterFlip sets KnowledgeRequired on the real recipe objects, idempotent, a missing one skipped: %s | %s" % (n1, n2))
    pres = En.eterPresent()
    K.check(pres.size() == 13 and not pres.contains(E_RID[-1]), "X eterPresent = the 13 loaded")
    jf(CRR, "ASSET_STORE").set(None, None)
    # (f) names + rank gifts
    K.eq((str(Util.prettyItem(GREATER)), str(Util.prettyItem("Plant_Seeds_Wheat_Eternal")), str(Util.prettyItem("Skyy_Ench_Corn"))),
         ("Greater Essence of Life", "Wheat Seed Bag (Eternal)", "Enchanted Corn"), "X prettyItem: Greater Essence, the Eternal seed bag, an Enchanted item")
    K.eq((str(En.giftOf("LifeEssence")), str(En.giftOf("Corn")), En.giftOf("NoSuch")), (GREATER, "Skyy_Ench_Corn", None), "X giftOf: vanilla / own / none")
    rk = []
    for cid in ("Corn", "LifeEssence", "Mithril", "OakLog"):
        c = BY[cid]
        last = th(c, int(Reg.maxTier(R, c)))
        row = []
        for k in range(1, 6):
            it = Rb.rankItem(R, c, k)
            step = int(Rb.need(R, c, k)) - (last if k == 1 else int(Rb.need(R, c, k - 1)))
            want = min(5 * k, 64, EN.gift_size(step, 64))
            got = 0 if it is None else int(it[1])
            if got != want or (it is not None and str(it[0]) != str(En.giftOf(cid))):
                bad.append((cid, k, got, want))
            row.append(got)
        rk.append("%s %s" % (cid, row))
    K.check(not [b for b in bad if isinstance(b, tuple)] and bool(Rb.rankOn(R, BY["LifeEssence"])), "X rank gifts = min(5 x k, 64, %d%% of the rank's step); Life Essence pays Greater Essence: %s" % (EN.GIFT_SHARE, "; ".join(rk)))
    K.notes.append("X rank gifts ranks 1-5: " + "; ".join(rk))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- T: migr
def run_migr(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    t21 = T21()
    Reg, Cob, Rw, R21, Tm = P("CollReg"), P("CollCobMig"), P("CollRw24Mig"), P("CollRw21Mig"), P("CollToolMig")
    t21.fresh(scratch, "t")
    U_ = JClass("java.net.URL")
    srv = JClass("java.net.URLClassLoader")(JArray(U_)([JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()]), JClass("java.lang.ClassLoader").getPlatformClassLoader())
    L = JClass("java.net.URLClassLoader")(JArray(U_)([JClass("java.io.File")(OLD_JAR).toURI().toURL()]), srv)
    OLDDEF = str(JClass(PKG + "CollReg", loader=L).rewardsText())          # the 0.2.21 - 0.2.23 default
    DEF = str(Reg.rewardsText())

    def table(t_):
        return dict((str(k), [str(x) for x in v]) for k, v in Cob.table(JArray(JString)([l_.rstrip("\r") for l_ in t_.split("\n")])).items())

    def upd(t_):
        r_ = Rw.update(t_)
        return None if r_ is None else (str(r_[0]), [str(x) for x in r_[1]], str(r_[2]), int(r_[3]), int(r_[4]), bool(r_[5]), int(r_[6]))
    nk = len(Rw.K)
    K.check(Rw.update(DEF) is None and R21.update(DEF) is None and Tm.update(DEF) is None, "T a fresh 0.2.24 rewards.properties: every update = nothing (markers)")
    u0 = upd(OLDDEF)
    K.check(u0 is not None and u0[5] and u0[3] == nk and u0[4] == 0 and table(u0[0]) == table(DEF) and upd(u0[0]) is None,
            "T the 0.2.21 default -> the loader reads exactly the 0.2.24 default (%d entries); a 2nd run = nothing" % nk)
    rem = [r for r in range(0, len(u0[1]), 3) if u0[1][r + 2] == "(none)"]
    K.check(not rem, "T no line removed (a gift under one Enchanted item became a base-item gift): %d removals" % len(rem))
    t0 = table(OLDDEF)
    tn = table(u0[0])
    K.check(all(any(x.startswith("item:") for x in tn.get(k, [])) for k, v in t0.items() if any(x.startswith("item:") for x in v)),
            "T every tier with a 0.2.21 gift still gives an item (Enchanted or base)")
    K.check(RET not in u0[0].split("# coll24")[1] and "LifeEssence.10=item:%s:" % GREATER in u0[0], "T no line names the retired item; Life Essence pays Greater Essence")
    # the LIVE text (read only): the older updates first, like setup
    live = open(os.path.join(LIVE_DIR, "rewards.properties"), "rb").read().decode("latin-1")
    t1 = Tm.update(live)
    t1 = live if t1 is None else str(t1[0])
    t2 = R21.update(t1)
    t2 = t1 if t2 is None else str(t2[0])
    u1 = upd(t2)
    K.check(u1 is not None and u1[5] and upd(u1[0]) is None, "T the LIVE file: updated (%d entries, %d kept by hand), the loader reads exactly the old table with those entries replaced; a 2nd run = nothing" % (u1[3], u1[4]))
    K.check(u1[4] > 0 or table(u1[0]) == table(DEF), "T the LIVE file reads as the 0.2.24 default (no hand edits) or keeps its hand edits")
    crlf = t2.replace("\r\n", "\n").replace("\n", "\r\n")
    uc = upd(crlf)
    K.check(uc[5] and uc[0].count("\r\n") == uc[0].count("\n") and uc[3] == u1[3], "T CRLF kept on every line")
    une = upd(t2.rstrip("\n"))
    K.check(une[5] and not une[0].endswith("\n") and une[3] == u1[3], "T no final newline stays none")
    hand = t2.replace("Wheat.2=item:Skyy_Ench_Wheat:4", "Wheat.2=item:Skyy_Ench_Wheat:3")
    uh = upd(hand)
    gone = "\n".join(l_ for l_ in t2.split("\n") if not l_.startswith("Cobblestone.9="))
    ur = upd(gone)
    K.check(uh[5] and uh[3] == u1[3] - 1 and uh[4] == u1[4] + 1 and table(uh[0])["wheat.2"] == ["item:Skyy_Ench_Wheat:3"] and "kept hand-edited line" in uh[2]
            and ur[5] and ur[3] == u1[3] - 1 and "cobblestone.9" not in table(ur[0]) and "an admin removed it" in ur[2],
            "T a hand-edited gift line kept + logged; a line an admin removed is not re-added")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- G: the conversion + gifts
def run_retire(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JLong, JShort, JInt
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    t21 = T21()
    Reg, Store, Util, Rew, Cred, Ret = P("CollReg"), P("CollStore"), P("CollUtil"), P("CollRewards"), P("CollCredit"), P("CollRetire")
    UUID = JClass("java.util.UUID")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    base = t21.fresh(scratch, "g")
    R = Reg.D
    BY = dict((str(R.id[c]), c) for c in range(R.n))
    INVS, secs, count, keep_ = t21.give_fixture(list(EN.IDS) + [RET, GREATER, "Skyy_Sigil_Unique", "Rock_Stone"])
    logf = os.path.join(base, "retired-items.log")

    def put(cs, sec, slot, iid, n):
        cs[sec].setItemStackForSlot(JShort(slot), IS(iid, JInt(n)))

    def snap(cs):
        out_ = []
        for k_, c_ in enumerate(cs):
            for i_ in range(int(c_.getCapacity())):
                s_ = c_.getItemStack(JShort(i_))
                if s_ is not None and not s_.isEmpty():
                    out_.append((k_, i_, str(s_.getItemId()), int(s_.getQuantity())))
        return out_
    # (a) 3 stacks in storage / backpack / hotbar + other items: converted in their slots, 1:1
    u1 = UUID.fromString("00000000-0000-0000-0000-0000000e2411")
    k1 = str(Util.pkey(u1))
    cs = secs(36, 4, 9)
    INVS[str(u1)] = cs
    t21.counts(base, k1, [("Plant_Crop_Wheat_Item", 10)])
    put(cs, 0, 2, RET, 37)
    put(cs, 1, 3, RET, 5)
    put(cs, 2, 0, RET, 100)
    put(cs, 0, 5, "Rock_Stone", 12)
    put(cs, 0, 6, GREATER, 9)
    s0 = snap(cs)
    n = int(Ret.convert(u1))
    s1 = snap(cs)
    want = [(k, i, GREATER if iid == RET else iid, q) for k, i, iid, q in s0]
    K.check(n == 142 and s1 == want, "G a: 37 + 5 + 100 converted in their own slots (storage / backpack / hotbar), the other stacks untouched: %d, %s" % (n, s1))
    K.eq((count(cs, RET), count(cs, GREATER)), (0, 151), "G a: no retired item left, Greater Essence = 9 + 142")
    lg = open(logf, encoding="utf-8").read().split("\n")
    K.check(sum(1 for l in lg if "\tCONVERT-BEGIN\t" in l) == 3 and sum(1 for l in lg if "\tCONVERT\t" in l) == 3, "G a: the journal: 3 CONVERT-BEGIN + 3 CONVERT lines")
    K.eq(int(Store.meta(Store.dataK(k1), "_retired." + RET)), 142, "G a: _retired marker on the profile = 142")
    # (b) a relog / the next scan: nothing more
    n2 = int(Ret.convert(u1))
    K.check(n2 == 0 and snap(cs) == s1 and int(Store.meta(Store.dataK(k1), "_retired." + RET)) == 142, "G b: a 2nd scan (relog) converts nothing, changes nothing")
    # (c) a crash before the engine saved the inventory: the old inventory comes back -> converted again 1:1, never two copies
    for k, i, iid, q in s0:
        put(cs, k, i, iid, q)
    for k in range(3):
        for i in range(int(cs[k].getCapacity())):
            if (k, i) not in [(a, b) for a, b, _x, _y in s0]:
                cs[k].removeItemStackFromSlot(JShort(i))
    n3 = int(Ret.convert(u1))
    K.check(n3 == 142 and snap(cs) == want and count(cs, GREATER) == 151, "G c: after an engine rollback (old inventory back) the scan converts again: 142 -> still 151 Greater Essence in all, never 293")
    # (d) SkyyProfiles holds the inventory / the new item is not loaded: nothing happens
    u2 = UUID.fromString("00000000-0000-0000-0000-0000000e2412")
    cs2 = secs(36, 1, 9)
    INVS[str(u2)] = cs2
    put(cs2, 0, 0, RET, 7)
    Util.bridge().put("profile:busy:" + str(u2), "switching")
    h1 = int(Ret.convert(u2))
    Util.bridge().remove("profile:busy:" + str(u2))

    @JImplements("java.util.function.Predicate")
    class NoGreater(object):
        @JOverride
        def test(self, o):
            return str(o) != GREATER
    Rew.ITEMOK = NoGreater()
    h2 = int(Ret.convert(u2))
    Rew.ITEMOK = keep_[1]()
    K.check(h1 == -1 and h2 == -1 and count(cs2, RET) == 7 and count(cs2, GREATER) == 0, "G d: a SkyyProfiles hold / Greater Essence not loaded = nothing done (-1), retried later")
    K.eq((int(Ret.convert(u2)), count(cs2, RET), count(cs2, GREATER)), (7, 0, 7), "G d: then converted")
    K.check(int(Ret.convert(UUID.fromString("00000000-0000-0000-0000-0000000e24ff"))) == -1, "G an offline player (no inventory) = -1")
    # (e) tier gifts at the new sizes, once: Corn to tier IX
    u3 = UUID.fromString("00000000-0000-0000-0000-0000000e2413")
    k3 = str(Util.pkey(u3))
    INVS[str(u3)] = secs()
    cc = BY["Corn"]
    mx = int(Reg.maxTier(R, cc))
    Cred.creditOne(None, u3, k3, "Plant_Crop_Corn_Item", JLong(int(Reg.threshold(R, cc, mx))), True)
    Rew.settleAll(None, u3, k3)
    Rew.settleAll(None, u3, k3)
    exp = sum(int(Reg.itemAt(R, cc, t)[1]) for t in range(1, mx + 1) if Reg.itemAt(R, cc, t) is not None and str(Reg.itemAt(R, cc, t)[0]) == "Skyy_Ench_Corn")
    a = [int(Reg.threshold(R, cc, t)) for t in range(1, mx + 1)]
    py = sum(EN.gift_size(a[t - 1] - (a[t - 2] if t > 1 else 0), 64) for t in range(1, mx + 1) if Reg.itemAt(R, cc, t) is not None and str(Reg.itemAt(R, cc, t)[0]) == "Skyy_Ench_Corn")
    K.check(count(INVS[str(u3)], "Skyy_Ench_Corn") == exp == py and exp < 2 * sum(range(1, mx + 1)), "G e: Corn to its last tier pays the sized gifts once: %d Enchanted Corn (0.2.21: up to %d)" % (exp, 2 * sum(range(1, mx + 1))))
    # (f) a Life Essence rebirth rank gift = Greater Essence
    Rb = P("CollRebirth")

    @JImplements("java.util.function.Function")
    class Cap(object):
        @JOverride
        def apply(self, a_):
            return JInt(103)
    Rb.CAP_TEST = Cap()
    Rb.CACHE.clear()
    u4 = UUID.fromString("00000000-0000-0000-0000-0000000e2414")
    k4 = str(Util.pkey(u4))
    INVS[str(u4)] = secs()
    lc = BY["LifeEssence"]
    lm = int(Reg.maxTier(R, lc))
    pm = "".join("_paid%s.LifeEssence=%d\n" % (x, lm) for x in ("", "xp", "item"))
    d4 = t21.counts(base, k4, [("Ingredient_Life_Essence", int(Rb.need(R, lc, 3)))], pm)
    Rew.settleAll(None, u4, k4)
    Rew.settleAll(None, u4, k4)
    wantg = sum(0 if Rb.rankItem(R, lc, k) is None else int(Rb.rankItem(R, lc, k)[1]) for k in (1, 2, 3))
    K.check(count(INVS[str(u4)], GREATER) == wantg > 0 and int(Store.meta(d4, "_paidrank.LifeEssence")) == 3 and count(INVS[str(u4)], RET) == 0,
            "G f: Life Essence rebirth ranks 1-3 pay %d Greater Essence of Life once (no retired item)" % wantg)
    Rb.CAP_TEST = None
    Rew.SECS = None
    Rew.ITEMOK = None
    K.save()


# ------------------------------------------------------------------------------------------------------------------- D: live (migrations + settles)
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    t21 = T21()
    Reg, Store, Util, Rew = P("CollReg"), P("CollStore"), P("CollUtil"), P("CollRewards")
    b_ = JClass("java.nio.file.Paths").get(home)
    rf = os.path.join(home, "rewards.properties")
    h0 = HK.tree_hash(home)
    msgs, hs = [], []
    for start in (1, 2):
        Reg.BASE = b_
        Store.DIR = b_.resolve("counts")
        P("CollBagMigrate").run(b_)
        P("CollBypassMig").run(b_)
        P("CollCoinMig").run(b_)
        Reg.loadAll()
        for m in ("CollCobMig", "CollSigMig", "CollShardMig", "CollToolMig", "CollRw21Mig"):
            P(m).run(b_)
        msgs.append(str(P("CollRw24Mig").run(b_)))
        hs.append(HK.tree_hash(home))
    ch1 = sorted(k for k, v in hs[0].items() if h0.get(k) != v)
    K.check(msgs[0].startswith("collection gifts sized to their tiers") and msgs[1] == "" and hs[0] == hs[1],
            "D the 1st start sizes the gifts once (%s), the 2nd changes nothing" % msgs[0][:140])
    K.check("rewards.properties" in ch1 and "migration-coll24.log" in ch1 and all(c in ("rewards.properties", "migration-coll24.log", "config-changes.log") or c.startswith("config-history") for c in ch1),
            "D only rewards.properties, its history copy, config-changes.log and migration-coll24.log changed: %s" % ch1[:6])
    chg = open(os.path.join(home, "config-changes.log"), encoding="latin-1").read()
    rows = [l_ for l_ in chg.split("\n") if "SkyyCollections 0.2.24" in l_]
    K.check(len(rows) > 100, "D %d Undo rows (one per entry)" % len(rows))
    INVS, secs, count, _keep = t21.give_fixture(list(EN.IDS) + [RET, GREATER, "Skyy_Sigil_Unique", "Rock_Stone"])
    keys = sorted(f[:-11] for f in os.listdir(os.path.join(home, "counts")) if f.endswith(".properties"))
    got = {}
    for rnd in (1, 2):
        for k in keys:
            try:
                u = JClass("java.util.UUID").fromString(k[:36])
            except Exception:
                continue
            if str(Util.pkey(u)) != k:
                continue
            INVS.setdefault(str(u), secs(36, 0, 9))
            Rew.settleAll(None, u, k)
            got[(rnd, k)] = sum(count(INVS[str(u)], i) for i in EN.IDS + [GREATER])
    K.check(all(got[(1, k)] == got[(2, k)] for k in keys if (1, k) in got) and not any(count(v, RET) for v in INVS.values()),
            "D every live profile settled twice: the gifts (if any were owed) once, never the retired item (%s)" % dict((k[:8], got.get((1, k))) for k in keys))
    Rew.SECS = None
    Rew.ITEMOK = None
    K.save()


# ------------------------------------------------------------------------------------------------------------------- DP: live pages + M pages
def run_livepages(out, jar, scratch, home):
    from jpype import JClass
    t23 = T23()
    HT = t23.HT
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    P("CollHubOpen").register()
    t23.put_defs(E)
    Reg, Store = P("CollReg"), P("CollStore")
    b_ = E.Paths.get(home)
    Reg.BASE = b_
    Store.DIR = b_.resolve("counts")
    P("CollCoinMig").run(b_)
    Reg.loadAll()
    for m in ("CollCobMig", "CollSigMig", "CollShardMig", "CollToolMig", "CollRw21Mig", "CollRw24Mig"):
        P(m).run(b_)
    R = Reg.D
    out_ = JClass("java.util.HashMap")()
    for cc_ in range(int(R.n)):
        for t in range(1, int(Reg.maxTier(R, cc_)) + 1):
            toks = Reg.REWARDS.get(str(R.id[cc_]).lower() + "." + str(t))
            rs = [str(x)[7:] for x in (toks or []) if str(x).startswith("recipe:")]
            if rs:
                out_.put("%d.%d" % (cc_, t), t23.jstrs(rs))
    have = JClass("java.util.HashSet")()
    for r in [str(x) for x in P("CollEnch").MRID]:
        have.add(r)
    P("CollEnch").merge(out_, R, have)
    P("CollEnch").eterMerge(out_, R, have)
    Reg.RECIPES = out_
    Reg.VALIDATED = True
    keys = sorted(f[:-11] for f in os.listdir(os.path.join(home, "counts")) if f.endswith(".properties")) if os.path.isdir(os.path.join(home, "counts")) else []
    UU = JClass("java.util.UUID")
    pages, bad, sampled = 0, [], 0
    vis = [cc for cc in range(int(R.n)) if not bool(R.hidden[cc])]
    for k in keys:
        try:
            u = UU.fromString(k[:36])
        except Exception:
            continue
        if str(P("CollUtil").pkey(u)) != k:
            continue
        P_ = E.mkp(u, "Live" + k[:4])
        for i, cc in enumerate(vis):
            pg = t23.open_coll(E, P_, cc)
            cmds, evs = HT.build(pg, P_)
            ids = t23.ids_of(cmds)
            miss = [s for s in t23.sets_of(cmds) if s.lstrip("#").split(".")[0] not in ids] + [s for s, _t in evs if s.lstrip("#") not in ids]
            if miss or int(pg.view) != 2:
                bad.append("%s %s %s" % (k[:8], R.id[cc], miss[:2]))
            if (i % 25 == 0 or str(R.id[cc]) in ("Wheat", "LifeEssence")) and sampled < 14:
                t23.pcheck(K, (cmds, evs), "DP live %s %s" % (k[:8], R.id[cc]))
                sampled += 1
            pages += 1
    K.check(not bad and pages > 0, "DP every live profile's collection pages build (%d pages, %d profiles) - every b.set / binding names an element (%s)" % (pages, len(keys), bad[:3]))
    K.notes.append("DP: %d live profile(s), %d pages, %d through assert_menu_page" % (len(keys), pages, sampled))
    K.save()


def run_pages(out, jar, scratch, home):
    """the 0.2.23 page phase as it is; its one version check (the ready line names 0.2.23) asks for 0.2.24 instead"""
    ck0 = HK.Child.check
    plug = zipfile.ZipFile(jar).read("com/skyy/collections/SkyyCollectionsPlugin.class")

    def ck(self, cond, what):
        if what == "PAGE the ready line names 0.2.23":
            return ck0(self, re.search(rb"\[SkyyCollections\] 0\.2\.24 ready", plug) is not None, "PAGE the ready line names 0.2.24")
        return ck0(self, cond, what)
    HK.Child.check = ck
    T23().run_pages(out, jar, scratch, home)


EXPECT = {
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],          # the kit's version texts + the eternal.tier row
    # the live table, the Eternal seeds (tables, merge, flag, coll:fn:eternal), the gift item / retired ids / names, eternal.tier
    "CollEnch": ["+f ETER_COLL", "+f ETER_DEF", "+f ETER_ID", "+f ETER_NAME", "+f ETER_NOTE", "+f ETER_RID", "+f ETER_WARNAT", "+f ET_TIER", "+f GSHARE",
                 "+f RET_ID", "+f RET_TO", "+f VCOLL", "+f VID", "+f VNAME", "+m eterFlip", "+m eterIdx", "+m eterMerge", "+m eterPresent",
                 "+m eternalWhy", "+m giftName", "+m giftOf", "+m plainName", "+m retIdx", "~<clinit>", "~m loadC1"],
    "CollFn": ["~m apply"],                                                   # coll:fn:eternal
    "CollRebirth": ["+m rankOn", "~m rankGift", "~m rankItem"],               # sized rank gifts, the vanilla gift item
    "CollReg": ["~m configText", "~m rewardsText", "~m validate"],            # the 0.2.24 defaults, the Eternal merge
    "CollRewards": ["~m rankOwed", "~m settle"],                              # rankOn gate (+ an owed later rank)
    "CollSaver": ["~m run"],                                                  # the conversion scan
    "CollUtil": ["~m autoOk", "~m bagRank", "~m prettyItem"],                 # Eternal seeds never by coins / auto; names
    "EnchRank": ["~<clinit>"],                                                # the Compressing tab order (102 rows)
    "SkyyCollectionsPlugin": ["~m setup", "~m shutdown", "~m start"],         # CollRw24Mig, coll:fn:eternal, the listener, the flip, ready line
}

if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("jar", run_jar), ("exec", run_exec), ("migr", run_migr), ("retire", run_retire), ("pages", run_pages),
            ("live", run_live), ("livepages", run_livepages)], __file__, live=(LIVE_DIR, "Skyy_SkyyCollections"))
