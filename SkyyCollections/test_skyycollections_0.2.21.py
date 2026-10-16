"""Harness for SkyyCollections 0.2.21 (round C1 of research/Collections-Tools-Redesign-Spec.md; tools/collections_0_2_21_patch.py). Build first:
    python tools/collections_0_2_21_patch.py && python SkyyCollections/build_skyycollections_0.2.21.py

    python SkyyCollections/test_skyycollections_0.2.21.py [--jar <SkyyCollections-0.2.21.jar>] [--dir <scratch>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.20 -> 0.2.21: exactly the listed members differ; non-class entries: manifest.json, server.lang + the 83 new Enchanted
                items' files (item JSON, texture, icon) - every 0.2.20 file byte-identical
  J    jar      103 Enchanted item JSONs (the 20 of 0.2.20 byte-identical), every new one = tools/skyyench.py rebuilt now, 100 base -> 1,
                Compressing tab, KnowledgeRequired; lang: 0.2.20's lines kept, the tier tag first on the 37 tiered new items; ready line
  X    exec     EXECUTED on the compiled classes: halved coins, tier-up tokens (rewardText / rewardLines / rank-up line / Server Setup
                check), coll:fn:toolPts (every skill at every tier = 135 / 136 / 137, partial tiers, cap, off, route, bad args),
                coll:tierups + coll:fn:tierups / coll:fn:tierup, the managed knowledge (16 armor pieces learned at the armor tier, forgotten
                below, ench.on off keeps the armor), the C1 table on the default file (every visible collection / tier)
  T    migr     CollCoinMig + CollRw21Mig: on the LIVE files' text (read only) after the older updates, on the 0.2.20 default, CRLF, no final
                newline, hand-edited / removed lines kept, a second run = nothing, a fresh file = nothing
  G    gives    real containers: the gift loop, the C1 catch-up below _paiditem (once), rank gifts (ranks 1 + 2 at once, rank 3 by a credit,
                the cap), full inventory = owed then given, never twice
  D2   live     the setup order on a scratch COPY of the live Skyy_SkyyCollections, started twice: migrations once, History copies, Undo rows,
                every live profile settled twice (gifts once)
  AA   audit    the engine-access audit
Scratch: tools/dev/scratch/c1/coll (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "ci"))
import skyybuild as B
import harness_kit as HK
import skyyench as EN
import tier_tags as TT


def loader_for(jar):
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


VERSION = "0.2.21"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-0.2.20.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "c1", "coll")))
PKG = "com.skyy.collections."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCollections")
LANG = "Server/Languages/en-US/server.lang"
NEW_IDS = [EN.PREFIX + t[0] for t in EN.TABLE_C1]
NEW_FILES = []
for _t in EN.TABLE_C1:
    NEW_FILES += ["Server/Item/Items/SkyyCollections/%s%s.json" % (EN.PREFIX, _t[0]), "Common/Items/SkyyCollections/Ench/%s.png" % _t[0],
                  "Common/Icons/ItemsGenerated/SkyyCollections_Ench_%s.png" % _t[0]]
EXPECT = {
    'CfgFile': ['~<clinit>'],   # the default config.properties (+ toolpts.* / rank.* / 83 ench.tier rows)
    'CfgFn': ['~m opExport'],   # the kit's version text
    'CfgRows': ['~<clinit>', '~m header'],   # + the new rows, the version text
    'CollCredit': ['~m creditOne'],   # a rebirth rank reached pays its gift
    'CollEnch': ['+f MID', '+f MRID', '+f RK_CAP', '+f RK_PER', '+f TP_CAP', '+f TP_KDEF', '+f TP_KEYS', '+f TP_KEYS_DEF', '+f TP_KW', '+f TP_ODEF', '+f TP_ON', '+f TP_OW', '+f TP_SK', '+m cint', '+m loadC1', '+m ofColl', '+m wlist', '~<clinit>', '~m next', '~m wantSig'],   # managed knowledge (+ armor), tool point / rank config, ofColl
    'CollFn': ['~m apply'],   # toolPts / tierups / tierup
    'CollKit': ['~m rewardToken'],   # tierup: tokens
    'CollMsg': ['~m rankParts'],   # tier-ups on the rank-up line
    'CollRebirth': ['+m rankGift', '+m rankItem', '~m maxText'],   # rank gifts (moved above CollRewards)
    'CollReg': ['+f TU_KIND', '+f TU_NAME', '+m tierupLabel', '+m tierupsAt', '~<clinit>', '~m configText', '~m loadConfig', '~m parseReg', '~m regText', '~m rewardLines', '~m rewardTextB', '~m rewardsText'],   # halved coins, tier-up tokens, the C1 default files
    'CollRewards': ['+f CU21_COLL', '+f CU21_ID', '+f CU21_N', '+f CU21_TIER', '+m cuBase21', '+m cuHas21', '+m cuOwed21', '+m cuTier21', '+m giveRank', '+m rankOwed', '+m rankOwedAny', '~<clinit>', '~m itemOwed', '~m mark', '~m settle'],   # rank gifts, the C1 catch-up
    'CollUnlocks': ['~m publishLocked', '~m unpublish'],   # coll:tierups
    'EnchRank': ['~<clinit>'],   # the Compressing tab order (+ 83 rows)
    'SkyyCollectionsPlugin': ['~m setup', '~m shutdown'],   # the two updates, the bridge, the ready line
}
ADDED = ["CollC1", "CollCoinMig", "CollRw21Mig"]

if HK.arg("--phase") == "compare":
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            exp = sorted(["manifest.json", LANG] + NEW_FILES)
            return self.check(sorted(got) == exp, "C: non-class entries changed = manifest.json + server.lang + the 83 new Enchanted items' 3 files each "
                                                  "(extra %s, missing %s)" % (sorted(set(got) - set(exp))[:5], sorted(set(exp) - set(got))[:5]))
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq


# ------------------------------------------------------------------------------------------------------------------- J: the jar
def run_jar(out, jar, scratch, _home):
    import skyyart as SA
    K = HK.Child(out)
    z, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    names, onames = set(z.namelist()), set(zo.namelist())
    with SA.assets() as az:
        files, _lang = EN.build_assets(az, SA)
    items = sorted(os.path.basename(p)[:-5] for p in names if p.startswith("Server/Item/Items/SkyyCollections/") and p.endswith(".json"))
    K.eq(items, sorted(EN.IDS), "J 103 Enchanted item JSONs = tools/skyyench.py")
    same = [p for p in onames if not p.endswith(".class") and p not in ("manifest.json", LANG)]
    K.check(all(p in names and z.read(p) == zo.read(p) for p in same), "J every 0.2.20 file byte-identical (%d files)" % len(same))
    bad = [p for p in NEW_FILES if p not in names or p in onames or z.read(p) != (files[p].encode("utf-8") if isinstance(files[p], str) else files[p])]
    K.eq(bad, [], "J the 249 new files = tools/skyyench.py rebuilt now (byte-identical)")
    rec = []
    for _t in EN.TABLE_C1:
        n = json.loads(z.read("Server/Item/Items/SkyyCollections/%s%s.json" % (EN.PREFIX, _t[0])))
        r = n["Recipe"]
        i0 = r["Input"][0]
        if not (r["KnowledgeRequired"] is True and r["OutputQuantity"] == 1 and i0["Quantity"] == 100 and (i0.get("ItemId") or i0.get("ResourceTypeId")) == _t[2]
                and r["BenchRequirement"] == [{"Type": "Crafting", "Id": "Workbench", "Categories": ["Workbench_SkyyCompressing"]}]
                and n["MaxStack"] == 100 and n["Quality"] == "Skyy_Enchanted" and "BlockType" not in n and "Interactions" not in n):
            rec.append(_t[0])
    K.eq(rec, [], "J every new item: 100 base -> 1, Workbench Compressing tab, KnowledgeRequired, stack 100, Enchanted quality, not placeable / edible")
    ln, lo = z.read(LANG).decode("utf-8").split("\n"), zo.read(LANG).decode("utf-8").split("\n")
    K.eq(sorted(set(lo) - set(ln)), [], "J server.lang: no 0.2.20 line removed or changed")
    added = sorted(set(ln) - set(lo))
    K.check(all(any(i + "." in l for i in NEW_IDS) for l in added) and len(added) == 4 * 83, "J server.lang = 0.2.20's + exactly 4 lines per new item (%d)" % len(added))
    tagged = [i for i in NEW_IDS if TT.tag_for(i)]
    tl = dict((l.split("=", 1)[0], l.split("=", 1)[1]) for l in ln if "=" in l)
    K.check(len(tagged) == 37 and all(tl["server.items.%s.description" % i].startswith(TT.tag_for(i) + " - ") for i in tagged)
            and all(not re.match(r"^T\d ", tl["server.items.%s.description" % i]) for i in NEW_IDS if i not in tagged),
            "J the 37 tiered new items start with their tier tag ('%s'), the other 46 have none" % tl["server.items.Skyy_Ench_Birch.description"][:60])
    plug = z.read("com/skyy/collections/SkyyCollectionsPlugin.class")
    K.check(b"0.2.21 ready" in plug and b"103 Enchanted materials" in plug, "J the ready line: 0.2.21, 103 Enchanted materials")
    K.check("including the 103 Enchanted materials" in json.loads(z.read("manifest.json"))["Description"], "J the manifest says 103")
    K.save()


def P(n):
    from jpype import JClass
    return JClass(PKG + n)


def fresh(scratch, sub):
    from jpype import JClass
    Reg, Store = P("CollReg"), P("CollStore")
    base = os.path.join(scratch, sub, "Skyy_SkyyCollections")
    os.makedirs(os.path.join(base, "counts"))
    Reg.BASE = JClass("java.nio.file.Paths").get(base)
    Store.DIR = Reg.BASE.resolve("counts")
    Reg.loadAll()
    return base


def counts(base, key, pairs, meta=""):
    from jpype import JClass
    Store = P("CollStore")
    open(os.path.join(base, "counts", key + ".properties"), "w").write("_schema=2\n" + "".join("%s=%d\n" % kv for kv in pairs) + meta)
    Store.DATA.remove(key)
    return Store.dataK(key)


# ------------------------------------------------------------------------------------------------------------------- X: exec
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Reg, Store, Util, Unl, Kit, En, C1, Msg, Rb = (P("CollReg"), P("CollStore"), P("CollUtil"), P("CollUnlocks"), P("CollKit"), P("CollEnch"),
                                                  P("CollC1"), P("CollMsg"), P("CollRebirth"))
    Fn = P("CollFn")
    base = fresh(scratch, "x")
    R = Reg.D
    BY = dict((str(R.id[c]), c) for c in range(R.n))
    # coins halved
    K.eq([int(Reg.coinsAt(R, BY["Wheat"], t)) for t in range(1, 10)], [25, 50, 100, 200, 400, 750, 1500, 3000, 6000],
         "X coins halved: Wheat I..IX = 25 .. 6,000")
    K.check("tier.coins=25,50,100,200,400,750,1500,3000,6000,12500" in open(os.path.join(base, "collections.properties")).read(), "X the fresh collections.properties has the halved line + marker")
    # the C1 table: every visible collection / tier has something (an item, a recipe, a tier-up, a Lantern) or is the Enchanted tier
    miss = []
    for c in range(R.n):
        if R.hidden[c]:
            continue
        e = int(En.TIER[int(En.ofColl(R.id[c]))])
        for t in range(1, int(Reg.maxTier(R, c)) + 1):
            toks = Reg.REWARDS.get(str(R.id[c]).lower() + "." + str(t))
            ok_ = t == e or (str(R.id[c]) == "TreeSap" and t in (1, 5, 8)) or (toks is not None and any(not str(x).startswith(("coins:", "recipe:Skyy_Sack_")) for x in toks))
            if not ok_:
                miss.append("%s.%d" % (R.id[c], t))
    K.eq(miss, [], "X every visible collection, every tier unlocks or gives something (103 collections)")
    K.eq([str(x) for x in Reg.tierupsAt(R, BY["Copper"], 4)], ["pickaxe:Copper"], "X Copper IV = the Copper pickaxe tier-up")
    K.eq(sorted(str(x) for x in Reg.tierupsAt(R, BY["Carrot"], 4)), ["can:Iron", "harvester:Iron"], "X Carrot IV = Iron Harvester + Watering Can")
    K.eq([str(x) for x in Reg.tierupsAt(R, BY["Adamantite"], 4)], ["armor.mining:Adamantite", "armor.fishing:Adamantite"], "X Adamantite IV (Elite: II Ench, III tool, IV armor)")
    tx = str(Reg.rewardText(R, BY["Copper"], 4))
    K.check("Copper Pickaxe tier-up" in tx and "+200 coins" in tx, "X tier row text: %s" % tx)
    K.check("Iron Mining Armor tier-up" in [str(x) for x in Reg.rewardLines(R, BY["Iron"], 5)], "X reward lines: %s" % [str(x) for x in Reg.rewardLines(R, BY["Iron"], 5)])
    rp = str(Msg.text(Msg.rankParts(R, BY["Maple" + "Log"], 4, True)))
    K.check("New: Iron Hatchet tier-up" in rp, "X the rank-up line names the tier-up: %s" % rp)
    K.check("+12 Enchanted Corn" in str(Reg.rewardText(R, BY["Corn"], 6)), "X a gift tier: %s" % str(Reg.rewardText(R, BY["Corn"], 6)))
    ck = lambda v: Kit.checkReward("rewards[Copper.4]", v)
    K.check(ck("tierup:pickaxe:Copper") is None and str(ck("tierup:pickaxe:Steel")).startswith("tierup:") and str(ck("tierup:wand:Iron")).startswith("?")
            and str(ck("tierup:pickaxe")).startswith("tierup:"), "X Server Setup check: a tier-up ok, a bad tier refused, an unknown tool asks, a bad form refused")
    # tool points: every collection at its last tier
    uid = "11111111-2222-3333-4444-0000000c1001"
    allmax = [(str(R.items[c][0]), int(Reg.threshold(R, c, int(Reg.maxTier(R, c))))) for c in range(R.n) if not R.hidden[c]]
    d = counts(base, uid, allmax)
    tp = Fn("toolPts")
    got = dict((sk, tp.apply(JArray(JObject)([JString(uid), JString(sk)]))) for sk in ("Mining", "Foraging", "Farming", "Orchard", "Ranching", "Combat"))
    K.eq(dict((k, int(v.longValue())) for k, v in got.items()), {"Mining": 135, "Foraging": 136, "Farming": 137, "Orchard": 8, "Ranching": 12, "Combat": 0},
         "X coll:fn:toolPts at every tier: Mining 135, Foraging 136, Farming 137 (Skyy: raise the others to match Foraging)")
    K.eq(int(tp.apply(JArray(JObject)([JClass("java.util.UUID").fromString(uid), JString("mining")])).longValue()), 135, "X toolPts by player UUID, any case")
    uid2 = "11111111-2222-3333-4444-0000000c1002"
    counts(base, uid2, [("Plant_Crop_Wheat_Item", int(Reg.threshold(R, BY["Wheat"], 6))), ("Plant_Crop_Corn_Item", int(Reg.threshold(R, BY["Corn"], 9))),
                        ("Ore_Iron", int(Reg.threshold(R, BY["Iron"], 5)))])
    q = lambda sk: int(tp.apply(JArray(JObject)([JString(uid2), JString(sk)])).longValue())
    K.eq((q("Farming"), q("Mining")), (7 + 4, 6), "X partial: Wheat VI (key 1,1,1,1,1,2) + Corn IX (other III / VI / IX = 1 + 1 + 2) = 11; Iron V (key 1,1,1,1,2) = 6")
    En.TP_CAP = 100
    K.eq(int(tp.apply(JArray(JObject)([JString(uid), JString("Mining")])).longValue()), 100, "X toolpts.cap 100 caps a skill")
    En.TP_CAP = 0
    En.TP_ON = False
    K.eq(int(tp.apply(JArray(JObject)([JString(uid), JString("Mining")])).longValue()), 0, "X toolpts.on false = 0")
    En.TP_ON = True
    K.check(tp.apply(JArray(JObject)([JString(uid)])) is None and tp.apply(JString("x")) is None, "X toolPts: a bad argument = null")
    # config rows: a hand value read, a bad value = the default
    pr = JClass("java.util.Properties")()
    pr.setProperty("toolpts.key.mining", "3")
    pr.setProperty("toolpts.other.mining", "x,y")
    pr.setProperty("rank.enchPerRank", "7")
    En.loadC1(pr)
    K.eq((int(tp.apply(JArray(JObject)([JString(uid2), JString("Mining")])).longValue()), int(En.RK_PER)), (15, 7), "X toolpts.key.mining=3 read (Iron V = 15), a bad list = the default, rank.enchPerRank=7 read")
    En.loadC1(JClass("java.util.Properties")())
    # tier-ups
    K.eq(str(C1.tierupList(Store.dataK(uid2), R)), "armor.mining:Iron,armor.fishing:Iron,can:Copper,harvester:Copper,pickaxe:Iron".replace(
        "armor.mining:Iron,armor.fishing:Iron", "armor.fishing:Iron,armor.mining:Iron"), "X coll:tierups list of a profile at Wheat VI / Iron V")
    tw = Fn("tierup")
    K.eq(str(tw.apply(JArray(JObject)([JString(uid2), JString("pickaxe:Thorium")]))), "0|Thorium|Thorium Ore|4|250|0", "X coll:fn:tierup locked: Thorium Ore IV (250), 0 gathered")
    K.eq(str(tw.apply(JArray(JObject)([JString(uid2), JString("Pickaxe:Iron")]))), "1|Iron|Iron Ore|4|500|%d" % int(Reg.threshold(R, BY["Iron"], 5)), "X coll:fn:tierup unlocked")
    K.check(tw.apply(JArray(JObject)([JString(uid2), JString("pickaxe:Crude")])) is None and tw.apply(JArray(JObject)([None, JString("hatchet:Copper")])) is not None,
            "X an ungated tier-up = null (SkyyGear: open); no player = still the collection")
    K.check(str(Fn("tierups").apply(JArray(JObject)([JString(uid)]))).count(",") >= 30, "X coll:fn:tierups of a maxed profile")
    # knowledge: the 16 first-set armor pieces
    allp = JClass("java.util.HashSet")()
    for r_ in [str(x) for x in En.MRID]:
        allp.add(r_)
    rec = JClass("java.util.HashMap")()
    Reg.VALIDATED = True
    for c in range(R.n):
        for t in range(1, int(Reg.maxTier(R, c)) + 1):
            toks = Reg.REWARDS.get(str(R.id[c]).lower() + "." + str(t))
            if toks is not None:
                ids = [str(x)[7:].strip() for x in toks if str(x).startswith("recipe:")]
                if ids:
                    rec.put("%d.%d" % (c, t), JArray(JString)(ids))
    En.merge(rec, R, allp)
    Reg.RECIPES = rec
    K.eq((len(En.MID), len(En.ID)), (119, 103), "X managed knowledge = 103 Enchanted + 16 armor pieces")
    PCD = JClass("com.hypixel.hytale.server.core.entity.entities.player.data.PlayerConfigData")
    uid3 = "11111111-2222-3333-4444-0000000c1003"

    def know(n_ore):
        d_ = counts(base, uid3, [("Ore_Copper", n_ore)])
        w_ = str(En.wantSig(Unl.compute(d_)))
        pd = PCD()
        ks = JClass("java.util.HashSet")()
        ks.add("Armor_Bronze_Chest")
        ks.add("Armor_Copper_Head")
        pd.setKnownRecipes(ks)
        En.syncData(pd, w_)
        return sorted(str(x) for x in pd.getKnownRecipes())
    k5, k4 = know(int(Reg.threshold(R, BY["Copper"], 5))), know(int(Reg.threshold(R, BY["Copper"], 4)))
    cu8 = ["Armor_Copper_%s" % s_ for s_ in ("Chest", "Hands", "Head", "Legs")] + ["Armor_Fishing_A1_%s" % s_ for s_ in ("Chest", "Hands", "Head", "Legs")]
    K.check(all(x in k5 for x in cu8) and "Skyy_Ench_Copper" in k5 and "Armor_Bronze_Chest" in k5, "X Copper V: the 8 Copper / angler pieces learned (+ Enchanted Copper), a foreign entry kept")
    K.check(not any(x in k4 for x in cu8) and "Skyy_Ench_Copper" in k4 and "Armor_Bronze_Chest" in k4, "X Copper IV: they are forgotten again (profile below the tier)")
    En.ON = False
    d_ = counts(base, uid3, [("Ore_Copper", int(Reg.threshold(R, BY["Copper"], 5)))])
    w_ = str(En.wantSig(Unl.compute(d_)))
    K.check("1" not in w_[:103] and w_[103:].count("1") == 8, "X ench.on false forgets the Enchanted recipes only - the armor stays")
    En.ON = True
    # rank gift helpers
    ci = BY["Corn"]
    K.eq([int(Rb.rankItem(R, ci, k)[1]) for k in (1, 2, 12, 13, 40)], [5, 10, 60, 64, 64], "X rank gift = 5 x rank, max 64")
    K.eq(str(Rb.rankItem(R, ci, 1)[0]), "Skyy_Ench_Corn", "X rank gift = the collection's own Enchanted item")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- T: migrations
def run_migr(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Reg, Cob, Cm, Rw, Tm, Sg = P("CollReg"), P("CollCobMig"), P("CollCoinMig"), P("CollRw21Mig"), P("CollToolMig"), P("CollSigMig")
    fresh(scratch, "t")
    U_ = JClass("java.net.URL")
    srv = JClass("java.net.URLClassLoader")(JArray(U_)([JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()]), JClass("java.lang.ClassLoader").getPlatformClassLoader())
    L = JClass("java.net.URLClassLoader")(JArray(U_)([JClass("java.io.File")(OLD_JAR).toURI().toURL()]), srv)          # the 0.2.20 classes, never the new jar's
    assert "CollRw21Mig" not in str(JClass(PKG + "CollReg", loader=L).rewardsText()) and "0.2.21" not in str(JClass(PKG + "CollReg", loader=L).rewardsText())
    OLDDEF = str(JClass(PKG + "CollReg", loader=L).rewardsText())
    OLDREG = str(JClass(PKG + "CollReg", loader=L).regText())
    DEF = str(Reg.rewardsText())

    def table(t_):
        return dict((str(k), [str(x) for x in v]) for k, v in Cob.table(JArray(JString)([l_.rstrip("\r") for l_ in t_.split("\n")])).items())

    def upd(t_):
        r_ = Rw.update(t_)
        return None if r_ is None else (str(r_[0]), [str(x) for x in r_[1]], str(r_[2]), int(r_[3]), int(r_[4]), bool(r_[5]), int(r_[6]))
    nk = len(Rw.K)
    K.check(Rw.update(DEF) is None and Tm.update(DEF) is None and Sg.update(DEF) is None, "T a fresh 0.2.21 rewards.properties: every update = nothing (markers)")
    u0 = upd(OLDDEF)
    K.check(u0 is not None and u0[5] and u0[3] == nk and u0[4] == 0 and u0[6] == 30 and table(u0[0]) == table(DEF) and upd(u0[0]) is None,
            "T the 0.2.20 default -> the loader reads exactly the 0.2.21 default (%d entries, 30 proposal comments dropped); a 2nd run = nothing" % nk)
    # the LIVE text (read only): the older updates first, like setup
    live = open(os.path.join(LIVE_DIR, "rewards.properties"), "rb").read().decode("latin-1")
    t1 = Tm.update(live)
    t1 = live if t1 is None else str(t1[0])
    u1 = upd(t1)
    K.check(u1 is not None and u1[5] and u1[3] == nk and u1[4] == 0 and table(u1[0]) == table(DEF) and len(u1[1]) == 3 * nk,
            "T the LIVE file (after CollToolMig): every entry updated / added, the loader reads the 0.2.21 table, %d Undo rows" % nk)
    crlf = t1.replace("\r\n", "\n").replace("\n", "\r\n")
    uc = upd(crlf)
    K.check(uc[5] and uc[0].count("\r\n") == uc[0].count("\n") and uc[3] == nk, "T CRLF kept on every line")
    une = upd(t1.rstrip("\n"))
    K.check(une[5] and not une[0].endswith("\n") and une[3] == nk, "T no final newline stays none")
    hand = t1.replace("Wheat.4=item:Skyy_Ench_Wheat:8", "Wheat.4=item:Skyy_Ench_Wheat:9")
    uh = upd(hand)
    rem = "\n".join(l_ for l_ in t1.split("\n") if not l_.startswith("Cobblestone.5="))
    ur = upd(rem)
    added = t1 + "Corn.2=coins:5\n"
    ua = upd(added)
    K.check(uh[5] and uh[3] == nk - 1 and uh[4] == 1 and table(uh[0])["wheat.4"] == ["item:Skyy_Ench_Wheat:9"] and "kept hand-edited line" in uh[2]
            and ur[5] and ur[3] == nk - 1 and "cobblestone.5" not in table(ur[0]) and "an admin removed it" in ur[2]
            and ua[5] and ua[3] == nk - 1 and ua[4] == 1 and table(ua[0])["corn.2"] == ["coins:5"],
            "T a hand-edited line kept + logged, a removed line not re-added, an admin's own line for a new key kept")
    # collections.properties: the coins
    lc = open(os.path.join(LIVE_DIR, "collections.properties"), "rb").read().decode("latin-1")

    def cupd(t_):
        r_ = Cm.update(t_)
        return None if r_ is None else (str(r_[0]), str(r_[1]), str(r_[2]), [str(x) for x in r_[3]])
    c1 = cupd(lc)
    K.check(c1 is not None and "tier.coins=25,50,100,200,400,750,1500,3000,6000,12500" in c1[0] and c1[1].startswith("tier.coins 50,")
            and cupd(c1[0]) is None and len(c1[0].split("\n")) == len(lc.split("\n")) + 1, "T the LIVE collections.properties: tier.coins halved, + the marker; a 2nd run = nothing")
    K.check([l_ for l_ in c1[0].split("\n") if l_ not in lc.split("\n")] == [str(Cm.MARK), "tier.coins=25,50,100,200,400,750,1500,3000,6000,12500"], "T only that line + the marker changed")
    ch = cupd(lc.replace("tier.coins=50,100,", "tier.coins=60,100,"))
    K.check(ch[1] == "" and "kept" in ch[2] and "tier.coins=60,100," in ch[0], "T a hand-edited coins line is kept (+ a note)")
    K.check(cupd(OLDREG) is not None and "12500" in cupd(OLDREG)[0] and Cm.update(str(Reg.regText())) is None, "T the 0.2.20 default migrates; the 0.2.21 default = nothing")
    cc = cupd(lc.replace("\r\n", "\n").replace("\n", "\r\n"))
    K.check(cc[0].count("\r\n") == cc[0].count("\n"), "T CRLF kept (collections.properties)")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- G: gives
def give_fixture(ids):
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
    jct = jcp.makeClass("com.hypixel.hytale.assetstore.SkyyCollFakeStore21", jcp.get("com.hypixel.hytale.assetstore.AssetStore"))
    jct.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyCollFakeStore21() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", jct))
    HAST = JClass(jct.toClass(AST.class_).getName())
    am_ = us.allocateInstance(DAM.class_)
    jf(DAM, "assetMapLock").set(am_, JClass("java.util.concurrent.locks.StampedLock")())
    mp_ = JClass("java.util.HashMap")()
    for iid_ in ids:
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
    Rew = P("CollRewards")
    Rew.SECS = SecsF()
    Rew.ITEMOK = ItemOk()

    def secs(n_st=36, n_bp=0, n_hb=9):
        return [SIC(JShort(n_st)), SIC(JShort(max(n_bp, 1))), SIC(JShort(n_hb))]

    def count(cs_, iid):
        n_ = 0
        for c_ in cs_:
            for i_ in range(int(c_.getCapacity())):
                s_ = c_.getItemStack(JShort(i_))
                if s_ is not None and not s_.isEmpty() and str(s_.getItemId()) == iid:
                    n_ += int(s_.getQuantity())
        return n_
    return INVS, secs, count, (SecsF, ItemOk)


def run_gives(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JLong, JShort, JInt
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Reg, Store, Util, Rew, Cred, Rb = P("CollReg"), P("CollStore"), P("CollUtil"), P("CollRewards"), P("CollCredit"), P("CollRebirth")
    UUID = JClass("java.util.UUID")
    base = fresh(scratch, "g")
    R = Reg.D
    BY = dict((str(R.id[c]), c) for c in range(R.n))
    INVS, secs, count, _keep = give_fixture(list(EN.IDS) + ["Skyy_Sigil_Unique", "Rock_Stone"])
    thr = lambda c, t: int(Reg.threshold(R, c, t))
    cc = BY["Corn"]
    # (a) a new player gathers Corn to tier IV: gifts I + II + IV (2 + 4 + 8), once
    u1 = UUID.fromString("00000000-0000-0000-0000-0000000c2101")
    k1 = str(Util.pkey(u1))
    INVS[str(u1)] = secs()
    Cred.creditOne(None, u1, k1, "Plant_Crop_Corn_Item", JLong(thr(cc, 4)), True)
    d1 = Store.dataK(k1)
    a1 = (count(INVS[str(u1)], "Skyy_Ench_Corn"), int(Store.meta(d1, "_paiditem.Corn")))
    Rew.settleAll(None, u1, k1)
    K.check(a1 == (14, 4) and count(INVS[str(u1)], "Skyy_Ench_Corn") == 14, "G a: Corn to tier IV pays 2 + 4 + 8 Enchanted Corn once (marker 4): %s" % (a1,))
    # (b) a 0.2.20 profile past the Wheat Sigil (paid marker 7, the 0.2.20 catch-up done): the C1 catch-up gives Wheat II (4) once
    u2 = UUID.fromString("00000000-0000-0000-0000-0000000c2102")
    k2 = str(Util.pkey(u2))
    INVS[str(u2)] = secs()
    d2 = counts(base, k2, [("Plant_Crop_Wheat_Item", thr(BY["Wheat"], 7))],
                "_paid.Wheat=7\n_paidxp.Wheat=7\n_paiditem.Wheat=7\n_cub020.Wheat=7\n_cu020.Wheat=4\n")
    Rew.settleAll(None, u2, k2)
    Rew.settleAll(None, u2, k2)
    b1 = (count(INVS[str(u2)], "Skyy_Ench_Wheat"), int(Store.meta(d2, "_cu021.Wheat")), int(Store.meta(d2, "_cub021.Wheat")), int(Store.meta(d2, "_paiditem.Wheat")))
    cf = open(os.path.join(base, "counts", k2 + ".properties"), encoding="latin-1").read()
    K.check(b1 == (4, 2, 8, 7) and "_cu021.Wheat=2" in cf, "G b: past the Sigil at Wheat VII: the C1 catch-up gives Wheat II's 4 Enchanted Wheat once (markers on disk); 2 settles: %s" % (b1,))
    # (c) a new profile at Wheat VII settles once: the normal loop pays every item tier I..VII (2+4+6+8+Sigil+14), the catch-up nothing
    u3 = UUID.fromString("00000000-0000-0000-0000-0000000c2103")
    k3 = str(Util.pkey(u3))
    INVS[str(u3)] = secs()
    d3 = counts(base, k3, [("Plant_Crop_Wheat_Item", thr(BY["Wheat"], 7))], "_paid.Wheat=7\n_paidxp.Wheat=7\n")
    Rew.settleAll(None, u3, k3)
    Rew.settleAll(None, u3, k3)
    K.eq((count(INVS[str(u3)], "Skyy_Ench_Wheat"), count(INVS[str(u3)], "Skyy_Sigil_Unique"), int(Store.meta(d3, "_cu021.Wheat"))), (34, 1, 0),
         "G c: no item paid yet at Wheat VII: 2 + 4 + 6 + 8 + 14 = 34 Enchanted Wheat + the Sigil, the catch-up nothing, never twice")
    # (d) rank gifts: rise 3 (SkyyRebirth seam), Corn at rank 2 -> 5 + 10 at once; a credit to rank 3 -> 15; then nothing
    @JImplements("java.util.function.Function")
    class Cap(object):
        @JOverride
        def apply(self, a):
            return JInt(103)
    Rb.CAP_TEST = Cap()
    Rb.CACHE.clear()
    u4 = UUID.fromString("00000000-0000-0000-0000-0000000c2104")
    k4 = str(Util.pkey(u4))
    INVS[str(u4)] = secs()
    mx = int(Reg.maxTier(R, cc))
    n2 = int(Rb.need(R, cc, 2))
    pm = "".join("_paid%s.Corn=%d\n" % (x, mx) for x in ("", "xp", "item"))
    d4 = counts(base, k4, [("Plant_Crop_Corn_Item", n2)], pm)
    Rew.mark(k4, d4, R)
    owed0 = k4 in [str(x) for x in Rew.OWED]
    Rew.settleAll(None, u4, k4)
    r1 = (count(INVS[str(u4)], "Skyy_Ench_Corn"), int(Store.meta(d4, "_paidrank.Corn")))
    Cred.creditOne(None, u4, k4, "Plant_Crop_Corn_Item", JLong(int(Rb.need(R, cc, 3)) - n2), True)
    r2 = (count(INVS[str(u4)], "Skyy_Ench_Corn"), int(Store.meta(d4, "_paidrank.Corn")))
    Rew.settleAll(None, u4, k4)
    r3 = (count(INVS[str(u4)], "Skyy_Ench_Corn"), bool(Rew.rankOwedAny(d4, R, k4)))
    gl = [l_ for l_ in open(os.path.join(base, "rewards-items.log"), encoding="utf-8").read().split("\n") if "\tGIVE\t" in l_ and ".rank" in l_ and k4 in l_]
    K.check(owed0 and r1 == (15, 2) and r2 == (30, 3) and r3 == (30, False) and len(gl) == 3,
            "G d: rank gifts: owed at first sight, ranks 1 + 2 = 5 + 10 at one settle, a credit to rank 3 = +15 (the credit path), nothing more; 3 GIVE lines: %s %s %s" % (r1, r2, r3))
    # (e) full inventory: owed, then given once there is room
    u5 = UUID.fromString("00000000-0000-0000-0000-0000000c2105")
    k5 = str(Util.pkey(u5))
    full = [JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")(JShort(1)) for _i in range(3)]
    for c_ in full:
        c_.setItemStackForSlot(JShort(0), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")("Rock_Stone", JInt(1)))
    INVS[str(u5)] = full
    d5 = counts(base, k5, [("Plant_Crop_Corn_Item", int(Rb.need(R, cc, 1)))], pm)
    Rew.settleAll(None, u5, k5)
    e1 = (count(full, "Skyy_Ench_Corn"), int(Store.meta(d5, "_paidrank.Corn")), bool(Rew.rankOwedAny(d5, R, k5)), k5 in [str(x) for x in Rew.OWED])
    full[0].removeItemStackFromSlot(JShort(0))
    Rew.settleAll(None, u5, k5)
    Rew.settleAll(None, u5, k5)
    e2 = (count(full, "Skyy_Ench_Corn"), int(Store.meta(d5, "_paidrank.Corn")), bool(Rew.rankOwedAny(d5, R, k5)))
    K.check(e1 == (0, 0, True, True) and e2 == (5, 1, False), "G e: full inventory -> the rank gift is owed (OWED, retried); with room it is given once: %s -> %s" % (e1, e2))
    # (f) without SkyyRebirth (rise 0) no rank, no gift
    Rb.CAP_TEST = None
    Rb.CACHE.clear()
    u6 = UUID.fromString("00000000-0000-0000-0000-0000000c2106")
    k6 = str(Util.pkey(u6))
    INVS[str(u6)] = secs()
    d6 = counts(base, k6, [("Plant_Crop_Corn_Item", n2)], pm)
    Rew.settleAll(None, u6, k6)
    K.eq((count(INVS[str(u6)], "Skyy_Ench_Corn"), int(Store.meta(d6, "_paidrank.Corn"))), (0, 0), "G f: no SkyyRebirth = no rebirth rank = no rank gift")
    Rew.SECS = None
    Rew.ITEMOK = None
    K.save()


# ------------------------------------------------------------------------------------------------------------------- D2: live copy, twice
def run_live2(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Reg, Store, Util, Rew = P("CollReg"), P("CollStore"), P("CollUtil"), P("CollRewards")
    b_ = JClass("java.nio.file.Paths").get(home)
    rf, cf = os.path.join(home, "rewards.properties"), os.path.join(home, "collections.properties")
    old_r, old_c = open(rf, "rb").read(), open(cf, "rb").read()
    msgs, snaps = [], []
    for start in (1, 2):
        Reg.BASE = b_
        Store.DIR = b_.resolve("counts")
        P("CollBagMigrate").run(b_)
        P("CollBypassMig").run(b_)
        cm = str(P("CollCoinMig").run(b_))
        Reg.loadAll()
        P("CollCobMig").run(b_)
        P("CollSigMig").run(b_)
        P("CollShardMig").run(b_)
        tm = str(P("CollToolMig").run(b_))
        rm = str(P("CollRw21Mig").run(b_))
        msgs.append((cm, tm, rm))
        snaps.append((open(rf, "rb").read(), open(cf, "rb").read()))
    K.check(msgs[0][0].startswith("collections.properties: collection coins halved") and msgs[0][2].startswith("collection rewards updated for round C1")
            and msgs[1] == ("", "", "") and snaps[0] == snaps[1], "D2: the 1st start updates both files once (%s | %s), the 2nd changes nothing" % (msgs[0][0][:90], msgs[0][2][:120]))
    hist = []
    for r_, _d, fs_ in os.walk(os.path.join(home, "config-history")):
        hist += [open(os.path.join(r_, f_), "rb").read() for f_ in fs_]
    chg = open(os.path.join(home, "config-changes.log"), encoding="latin-1").read()
    rows = [l_ for l_ in chg.split("\n") if "SkyyCollections 0.2.21" in l_]
    K.check(any(h == old_c for h in hist) and len(rows) == len(P("CollRw21Mig").K) + 1 and os.path.isfile(os.path.join(home, "migration-c1.log")),
            "D2: the old collections.properties in config-history, %d Undo rows (coins + every reward entry), migration-c1.log" % len(rows))
    K.check(int(Reg.coinsAt(Reg.D, int(Reg.D.byId.get("wheat")), 1)) == 25, "D2: the loaded coins are halved")
    INVS, secs, count, _keep = give_fixture(list(EN.IDS) + ["Skyy_Sigil_Unique", "Rock_Stone"])
    keys = sorted(f[:-11] for f in os.listdir(os.path.join(home, "counts")) if f.endswith(".properties"))
    R = Reg.D
    got = {}
    for rnd in (1, 2):
        for k in keys:
            u = JClass("java.util.UUID").fromString(k[:36])
            if str(Util.pkey(u)) != k:
                continue
            INVS.setdefault(str(u), secs(36, 0, 9))
            Rew.settleAll(None, u, k)
            got[(rnd, k)] = sum(count(INVS[str(u)], i) for i in EN.IDS)
    for k in keys:
        if (1, k) in got:
            d = Store.dataK(k)
            exp = 0
            for c in range(R.n):
                if R.hidden[c]:
                    continue
                for t in range(1, int(Store.countTier(d, R, c)) + 1):
                    it = Reg.itemAt(R, c, t)
                    if it is not None and str(it[0]).startswith(EN.PREFIX):
                        exp += int(it[1])
            K.check(got[(1, k)] == exp and got[(2, k)] == exp, "D2 %s: every reached tier's Enchanted gift once (%d items), a 2nd settle adds nothing" % (k[:8], exp))
    Rew.SECS = None
    Rew.ITEMOK = None
    K.save()


if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT or {}, ADDED,
           [("jar", run_jar), ("exec", run_exec), ("migr", run_migr), ("gives", run_gives), ("live2", run_live2)], __file__,
           live=(LIVE_DIR, "Skyy_SkyyCollections"))
