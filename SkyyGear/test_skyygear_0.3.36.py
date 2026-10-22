"""Harness for SkyyGear 0.3.36 (Balance P6 part B + Skyy's P5 follow-ups - tools/gear_0_3_36_patch.py). Build first:
    python tools/gear_0_3_36_patch.py && python SkyyGear/build_skyygear_0.3.36.py
    python SkyyGear/test_skyygear_0.3.36.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S  static   the patch re-runs to identical bytes, line endings kept, one new class (GearPickLockSys), its one registerSystem in the plugin's
              list, no new command, setup order migrateP5 -> migrateP6 -> load, the hooks (GearToolHitSys clamp, useNo best-owned)
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.35 -> 0.3.36 (EXPECT below)
  X  exec     EXECUTES the new paths in a bare JVM:
              X1 the ladders through the REAL loader + GearUp's own parser (tab / written): every P6 step = tools/balance_model.py p6_armor /
                 p6_tool (x the crop q), no Enchanted cost below Dusk, Dusk / Azurvane / Cinder / Lumen paid in Skyy_Ench_<Alloy>, spec 2.3 rows
              X2 craft XP: the P3 curve (GearRoll.xpTier), the rarity bases, the current band starts (GearRoll.xpStart), GearRoll.craftXp
              X3 gate.minHitsOwn: GearLL.minHitsI on own / higher / lower-tier ore, stone, off (0), 3 hits; the 2-hit / 1-hit proof on BlockHealth
              X4 the best owned tool (GearLL.best / pickWhy on a planted lifelong registry): crops, mushrooms, herbs, fruit; a better tool in the
                 registry lets bare hands pick, a missing uid / another kind / gate.pickup off / an unread registry = the held item only
              X5 level-up caps 10 (Mythic 2, Untiered 3); X6 utpow defaults + the REAL GearUtFx.lines (fake Item store) = stat max x utpow x level
                 factor; every row >= its Fabled reference or listed at the cap; a utpow file row read, a bad one = the default
              X7 armor bags: a random armor bag = grp a, "Unidentified Armor", identify picks among armor slots (>= 2 slots), stays armor; a smart
                 bag = grp h keeps its slot; a bag saved before 0.3.36 (no grp) shows + keeps its slot; a Mythic boss bag (pz) and grp k keep it;
                 unid.typeAtIdentify off shows the slot; weapon bags unchanged
              X8 the Normal quality asset TextColor #fefefe (the other qualities their rarity colour)
              X9 hp6Update on the REAL 0.3.35 default file: only the planned rows move + the utpow rows appended (Properties), marker, second run
                 null, a hand-edited ladder / cap kept + noted, CRLF kept, p6Same; hp6Log table rows as table[entry]
  D  live     migrate0330 + migrateP4 + migrateP5 + migrateP6 on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear/config.properties: only
              planned keys change, config-history copy, change-log lines; a SECOND start changes nothing; the file loads (caps 10, utpow)
  AA engine-access audit
FIX ROUND (critics 2026-10-22): X1b the crafted Mining sets' P6 recipe costs (the jar's item / recipe files); X4 mushrooms + herbs on the 15-step
ladder (T15 / T2 / T5 / T8) against the best owned hoe / Harvester (T13 refused, T14 in the bag passes), an uncached registry read from its file;
X6 the 600 cap, all 40 rows >= Fabled (fix round 2), Courier cc cd; X9 a hand-set utline.power gets no utpow rows; X7 why() lets a grp a bag open when only ANOTHER armor slot fits; XR GearPickLockSys first, GearMinHitSys last (RootDependency).
Scratch: tools/dev/scratch/balp6b/gear (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, math, json, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.36"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp6b", "gear")]
import skyybuild as B
import harness_kit as HK
import balance_model as BM

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.35.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_36_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.35.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
EXPECT = {"CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"],
          "GearBoxFn": ["~m apply"],          # the bridge's armor bag hides its piece
          "GearCfg": ["+f GATE_MINOWN", "+f HP6_ADDK", "+f HP6_ADDV", "+f HP6_KEYS", "+f HP6_MARK", "+f HP6_MARK_ID", "+f HP6_NEW", "+f HP6_OLD", "+f HP6_TBK", "+f HP6_TBL",
                      "+f HP6_WHO", "+f PICK_GATE", "+f UTPOW", "+f UTP_ID", "+f UTP_PC", "+m hp6Lk", "+m hp6Log", "+m hp6Lv", "+m hp6Update", "+m migrateP6", "+m p6Same",
                      "~<clinit>", "~m apply", "~m defaultsText"],
          "GearLL": ["+f PK_CAT", "+f PK_M", "+f PK_PRE", "+f PN", "+m best", "+m bestL", "+m catP", "+m minHits", "+m minHitsI", "+m pickNo", "+m pickWhy", "~<clinit>", "~m useNo"],
          "GearLuck": ["~m smartBag"], "GearRoll": ["~<clinit>", "~m reX"],          # the craft XP tier levels + the curve default (XPC_DEF inlined)
          "GearToolHitSys": ["~m handle"],
          "GearUnid": ["+m fitA", "+m groupedA", "+m grpA", "+m hidA", "+m hiddenA", "+m tagA", "~m fromItem", "~m open", "~m roll", "~m tname", "~m why"],
          "GearUt": ["+m pickA", "~m bag"], "GearUtFx": ["+m bodyValP", "+m checkPow", "+m utPow", "~m body", "~m lines"],
          "SkyyGearPlugin": ["~m setup"]}
_RC = HK.run_compare


def _planned_nonclass(za, zb):
    """(the changed non-class entries, the unplanned ones): the Normal quality's TextColor, the crafted Mining sets' Recipe Input (fix round),
    their server.lang descriptions, manifest.json"""
    ea = [n for n in za.namelist() if not n.endswith(".class")]
    eb = [n for n in zb.namelist() if not n.endswith(".class")]
    ed = sorted(n for n in set(ea) | set(eb) if n not in ea or n not in eb or za.read(n) != zb.read(n))
    bad = []
    for n in ed:
        if n == "manifest.json" or n not in ea or n not in eb:
            if n != "manifest.json":
                bad.append(n)
            continue
        if n == "Server/Languages/en-US/server.lang":
            la, lb = za.read(n).decode("utf-8").splitlines(), zb.read(n).decode("utf-8").splitlines()
            if len(la) != len(lb) or any(x != y and not (x.startswith("items.Armor_Mining_") and ".description = " in x and x.split(" = ")[0] == y.split(" = ")[0]) for x, y in zip(la, lb)):
                bad.append(n)
            continue
        ja, jb = json.loads(za.read(n).decode("utf-8")), json.loads(zb.read(n).decode("utf-8"))
        dk = sorted(k for k in set(ja) | set(jb) if ja.get(k) != jb.get(k))
        if n == "Server/Item/Qualities/Skyy_Gear_Normal.json":
            ok = dk == ["TextColor"] and ja["TextColor"] == "#ffffff" and jb["TextColor"] == "#fefefe"
        elif n.startswith("Server/Item/Items/SkyyGear/MiningArmor/Armor_Mining_"):
            ok = dk == ["Recipe"] and sorted(k for k in set(ja["Recipe"]) | set(jb["Recipe"]) if ja["Recipe"].get(k) != jb["Recipe"].get(k)) == ["Input"]
        elif n.startswith("Server/Item/Recipes/SkyyGear/SkyyGear_Recipe_Armor_Bronze_"):
            ok = dk == ["Input"]
        else:
            ok = False
        if not ok:
            bad.append(n)
    return ed, bad


def _run_compare(out, jar, old_jar, pkg, expect, added, removed):
    """the kit's compare (it allows only manifest.json to change) + the planned asset changes (_planned_nonclass)"""
    _RC(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ed, bad = _planned_nonclass(za, zb)
    fl = [f for f in d["fails"] if f.startswith("C: non-class entries changed:")]
    if fl and not bad:
        d["fails"].remove(fl[0])
        d["ok"] += 1
        d["notes"].append("C: the non-class changes are the planned ones (%d): Skyy_Gear_Normal TextColor #fefefe, %d crafted Mining set recipes (Input only), "
                          "their descriptions, manifest.json" % (len(ed), len([n for n in ed if "Armor_Mining_" in n or "Armor_Bronze_" in n])))
    elif bad:
        d["notes"].append("C: UNPLANNED non-class changes: %s" % bad[:6])
    json.dump(d, open(out, "w"), indent=1)


HK.run_compare = _run_compare
ADDED = ["GearMinHitSys", "GearPickLockSys"]
SLOTS = ("Head", "Chest", "Legs", "Hands")


def _props(txt):
    from jpype import JClass
    out = {}
    p = JClass("java.util.Properties")()
    p.load(JClass("java.io.StringReader")(txt))
    for k in p.stringPropertyNames():
        out[str(k)] = str(p.getProperty(k))
    return out


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.36 - build script') and g.count('VERSION = "0.3.36"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s text" % w)
    K.eq(g.count('mk("') - o.count('mk("'), 2, "S two new classes (GearPickLockSys, GearMinHitSys)")
    K.check(g.replace("\r\n", "\n").count('"GearPickLockSys",\n                                                        # 0.3.36 fix round') == 1 and g.count('"GearMinHitSys")))') == 1 and g.count('gplk = mk("GearPickLockSys", EES)') == 1 and g.count('gmhs = mk("GearMinHitSys", EES)') == 1,
            "S GearPickLockSys + GearMinHitSys in the plugin's one registerSystem list")
    K.check('M(gplk, "public java.util.Set getDependencies() { return com.hypixel.hytale.component.dependency.RootDependency.firstSet(); }")' in g
            and 'M(gmhs, "public java.util.Set getDependencies() { return com.hypixel.hytale.component.dependency.RootDependency.lastSet(); }")' in g,
            "S GearPickLockSys ordered first, GearMinHitSys last")
    su = g[g.index("@PKG@.GearCfg.migrate02();"):]
    K.check(su.index("migrateP4();") < su.index("migrateP5();") < su.index("migrateP6();") < su.index("@PKG@.GearCfg.load();"), "S setup: migrateP4 -> migrateP5 -> migrateP6 -> load")
    K.check(g.count("d1 = @PKG@.GearLL.minHits(e.getItemInHand(), e.getBlockType(), d1);") == 1, "S the fewest-hits clamp sits in GearToolHitSys once")
    K.check("Object[] bo = best(pr == null ? null : pr.getUuid(), hand ? null : s.getItemId(), cm[0], cm[1]);" in g, "S useNo reads the best owned tool")
    K.check(g.count("@PKG@.GearUnid.groupedA(") == 2 and g.count("@PKG@.GearUnid.hiddenA(b)") == 1 and g.count("groupedA(bx)") == 1 and g.count("groupedA(fb)") == 1 and g.count("groupedA(ub6)") == 1,
            "S the armor bag sites: roll, fromItem (+ its orange branch), GearUt.bag, the bridge, smart bags")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def _old_default_text():
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(2)
    arr[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
    arr[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    ld = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    oc = JClass(PKG + "GearCfg", loader=ld)
    return str(oc.defaultsText())


def fake_items(JClass, ids):
    """a bare JVM has no Item asset store: one holding bare Item objects (only the id set) for ids, so Gear.item(id) != null (0.3.35's)"""
    from jpype import JString, JObject
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    DM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    C = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    US = uf.get(None)
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fk = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestItemStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fk.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyTestItemStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fk))
    FKC = fk.toClass(AS.class_)

    def fld(c, n):
        f = c.class_.getDeclaredField(n)
        f.setAccessible(True)
        return f
    mp = JClass("java.util.concurrent.ConcurrentHashMap")()
    for i in ids:
        o = US.allocateInstance(C.class_)
        fld(C, "id").set(o, JString(i))
        mp.put(JObject(JString(i), JClass("java.lang.Object")), o)
    m = DM(mp)
    st = US.allocateInstance(FKC)
    fld(AS, "tClass").set(st, C.class_)
    fld(AS, "assetMap").set(st, m)
    fld(JClass("com.hypixel.hytale.assetstore.AssetRegistry"), "storeMap").get(None).put(C.class_, st)
    fld(C, "ASSET_STORE").set(None, st)
    return int(sum(1 for i in ids if C.getAssetMap().getAsset(i) is not None))


def _lt(TT, i):
    """the ladder T of a tier-up target (the build's _lt29t)"""
    if TT.tier(i):
        return TT.tier(i)
    for w in i.split("_")[1:]:
        if TT.metal_tier(w):
            return TT.metal_tier(w)
    return None


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JString, JInt, JFloat, JObject
    import re
    import tier_tags as TT
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    P = lambda n: JClass(PKG + n)
    Cfg, Defs, Roll, LL, Unid, Pool, Ut, Up, GData, Fx, Lv = (P(x) for x in (
        "GearCfg", "GearDefs", "GearRoll", "GearLL", "GearUnid", "GearPool", "GearUt", "GearUp", "GearData", "GearUtFx", "GearLevel"))
    SK = [str(x) for x in Defs.S_KEY]
    RID = [str(x) for x in Defs.R_ID]
    pd = JClass("java.util.Properties")()
    dtext = str(Cfg.defaultsText())
    pd.load(JClass("java.io.StringReader")(dtext))
    Cfg.apply(pd, False)
    dp = _props(dtext)
    nfi = fake_items(JClass, sorted(set([str(x) for x in Cfg.UTAB[0]] + [str(x) for x in Pool.P_ID] + ["Tool_Hoe_Crude", "Tool_Hoe_Copper", "Tool_Hoe_Iron", "Tool_Hoe_Thorium",
                                                                                                  "Tool_Sickle_Harvester_Thorium", "Tool_Hatchet_Copper", "Tool_Hatchet_Cobalt", "Tool_Pickaxe_Copper",
                                                                                                  "Tool_Sickle_Harvester_Mithril", "Tool_Sickle_Harvester_Titanium_SkyWynn"])))
    K.check(nfi > 200, "X0 the test Item store: the Untiered ids, the bag pool and the test tools (%d ids)" % nfi)
    # ============================================================== X1 the ladders
    q = BM.p6_crop_q()
    bad, n_steps, alloy_ok, plain_low = [], 0, [], True
    for key in ("lifelong.ladders", "can.ladders", "harvester.ladders", "multi.ladders", "garmor.ladders", "garmor.ladders.foraging", "garmor.ladders.farming"):
        for row in dp[key].split(","):
            for st in row.split(">")[1:]:
                m = re.match(r"^([^()]+)\((.*)\)$", st)
                tid, cost = m.group(1), m.group(2)
                t = _lt(TT, tid)
                if t is None or t < 2:
                    continue
                n_steps += 1
                kind = ("multi" if tid.startswith("Tool_Hatchet_Pickaxe_Multitool_") else "pick" if tid.startswith("Tool_Pickaxe_") else "hatch" if tid.startswith("Tool_Hatchet_")
                        else "farmtool" if tid.startswith(("Tool_Hoe_", "Tool_Sickle_", "Tool_WaterCan_")) else "farmor" if tid.startswith("Armor_Foraging_")
                        else "parmor" if tid.startswith("Armor_Farming_") else "marmor")
                slot = tid.rsplit("_", 1)[1]
                for c in cost.split("+"):
                    i, n = c.rsplit("*", 1)
                    n = int(n)
                    if i.startswith("Skyy_Ench_") and t < 6:
                        plain_low = False
                    base = i
                    if i.startswith("Skyy_Ench_"):
                        base = None
                    if re.match(r"^(Ingredient_Bar_|Skyy_Ench_)(Copper|Iron|Bronze|Thorium|Lead|Dusk|Cobalt|Chromium|Azurvane|Adamantite|Slag|Cinder|Mithril|Titanium|Lumen)(_SkyWynn)?$", i):
                        w = re.match(r"^(?:Ingredient_Bar_|Skyy_Ench_)([A-Za-z]+)", i).group(1)
                        if kind in ("pick", "multi", "marmor"):
                            want = BM.p6_armor("Mining", t)[slot] if kind == "marmor" else BM.p6_tool("Mining", t)
                            if n != want:
                                bad.append((tid, i, n, want))
                        if t >= 6 and w in ("Dusk", "Azurvane", "Cinder", "Lumen"):
                            alloy_ok.append(i == "Skyy_Ench_" + w)
                    elif i.startswith("Wood_") or (kind in ("hatch", "multi", "farmor") and i.startswith("Skyy_Ench_") and not re.match(r"^Skyy_Ench_(Copper|Iron|Bronze|Thorium|Lead|Dusk|Cobalt|Chromium|Azurvane|Adamantite|Slag|Cinder|Mithril|Titanium|Lumen)$", i)):
                        want = BM.p6_armor("Foraging", t)[slot] if kind == "farmor" else BM.p6_tool("Foraging", t)
                        if n != want:
                            bad.append((tid, i, n, want))
                    elif i.startswith("Plant_Crop_") or (kind in ("farmtool", "parmor") and i.startswith("Skyy_Ench_")):
                        cw = re.match(r"^(?:Plant_Crop_|Skyy_Ench_)([A-Za-z]+)", i).group(1)
                        want = BM.p6_armor("Farming", t, q.get(cw, 1.0))[slot] if kind == "parmor" else BM.p6_tool("Farming", t, q.get(cw, 1.0))
                        if n != want:
                            bad.append((tid, i, n, want))
    K.check(n_steps >= 150 and not bad, "X1 every P6 step = tools/balance_model.py p6_armor / p6_tool (%d steps): %s" % (n_steps, bad[:4]))
    K.check(plain_low, "X1 no Enchanted cost below Dusk (PLAIN29 kept)")
    K.check(len(alloy_ok) >= 20 and all(alloy_ok), "X1 every Dusk / Azurvane / Cinder / Lumen step pays Skyy_Ench_<Alloy> (%d)" % len(alloy_ok))
    for st in ("Armor_Iron_Chest(Ingredient_Bar_Iron*135)", "Armor_Cobalt_Head(Skyy_Ench_Cobalt*3)", "Tool_Pickaxe_Dusk_SkyWynn(Skyy_Ench_Dusk*3)", "Tool_Pickaxe_Lumen_SkyWynn(Skyy_Ench_Lumen*12)",
               "Tool_Hoe_Iron(Plant_Crop_Lettuce_Item*280)", "Tool_Hatchet_Iron(Ingredient_Bar_Iron*75+Wood_Beech_Trunk*225)"):
        K.check(any(st in dp[k] for k in dp if k.endswith("ladders") or ".ladders." in k), "X1 spec 2.3 row: %s" % st)
    # X1b (fix round, critic 1): the CRAFTED Mining sets (zone sets + Bronze) - the recipe's bar input = the P6 set cost, T6+ the Enchanted metal
    zj0 = zipfile.ZipFile(jar)
    zm_bad, zm_n = [], 0
    for n in zj0.namelist():
        if n.startswith("Server/Item/Items/SkyyGear/MiningArmor/Armor_Mining_") and n.endswith(".json"):
            iid = n.rsplit("/", 1)[1][:-5]
            metal, sl = iid.split("_")[2], iid.split("_")[3]
            inp = json.loads(zj0.read(n).decode("utf-8"))["Recipe"]["Input"]
        elif n.startswith("Server/Item/Recipes/SkyyGear/SkyyGear_Recipe_Armor_Bronze_"):
            metal, sl = "Bronze", n.rsplit("_", 1)[1][:-5]
            inp = json.loads(zj0.read(n).decode("utf-8"))["Input"]
        else:
            continue
        zm_n += 1
        t = TT.metal_tier(metal)
        want = (("Skyy_Ench_" + metal) if t >= 6 else ("Ingredient_Bar_Bronze" if metal == "Bronze" else "Ingredient_Bar_%s_SkyWynn" % metal), BM.p6_armor("Mining", t)[sl])
        got = [(str(x.get("ItemId")), int(x["Quantity"])) for x in inp if str(x.get("ItemId", "")).startswith(("Ingredient_Bar_", "Skyy_Ench_"))]
        if got != [want]:
            zm_bad.append((n.rsplit("/", 1)[1], got, want))
    K.check(zm_n == 36 and not zm_bad, "X1b the 36 crafted Mining set recipes (8 zone sets + Bronze) pay the P6 set cost (%d): %s" % (zm_n, zm_bad[:3]))
    lang = zj0.read("Server/Languages/en-US/server.lang").decode("utf-8")
    lum = [l for l in lang.splitlines() if l.startswith("items.Armor_Mining_Lumen_Chest.description = ")]
    lea = [l for l in lang.splitlines() if l.startswith("items.Armor_Mining_Lead_Head.description = ")]
    K.check(len(lum) == 1 and "mining armor from Enchanted Lumen." in lum[0] and len(lea) == 1 and "mining armor from Lead bars." in lea[0],
            "X1b the descriptions name what the recipe asks (%s | %s)" % (lum[:1], lea[:1]))
    # GearUp's own parser (the Anvil tier-up reads tab / written)
    K.check(int(Up.writtenSteps()) > 40 and str(Up.next("Tool_Pickaxe_Copper")) == "Tool_Pickaxe_Iron", "X1 GearUp.tab parses the P6 lifelong.ladders (%d written steps)" % int(Up.writtenSteps()))
    wr = Up.written("Tool_Pickaxe_Copper", "Tool_Pickaxe_Iron")
    K.notes.append("X1 GearUp.written(Copper -> Iron pickaxe) = %s" % (None if wr is None else [str(x) if not hasattr(x, "__len__") else [str(y) for y in x] for x in wr]))
    K.check(wr is not None and "125" in str([str(x) if not hasattr(x, "__len__") else [str(y) for y in x] for x in wr]), "X1 GearUp.written: the Iron pickaxe costs 125 Iron bars")
    # ============================================================== X2 craft XP
    K.eq(str(Cfg.XPC_CURVE), dp["xp.craftCurve"], "X2 the curve field = the file")
    K.check(dp["xp.craftCurve"].startswith("1:1,8:2.11,15:3.6,20:4.91,28:7.43") and dp["xp.craftCurve"].endswith("95:48.56,100:53.07"), "X2 xp.craftCurve = the P3 tier factor at the band starts")
    K.eq([int(dp["xp.craft." + r]) for r in ("normal", "unique", "rare", "legendary", "fabled", "mythic", "set")], [80, 160, 320, 640, 1280, 2560, 640], "X2 xp.craft rarity bases / 6.4")
    xs = dict((i, int(Roll.xpStart(i))) for i in ("Weapon_Sword_Copper", "Weapon_Sword_Iron", "Weapon_Sword_Thorium", "Weapon_Sword_Cobalt", "Weapon_Sword_Mithril"))
    K.eq(xs, {"Weapon_Sword_Copper": 1, "Weapon_Sword_Iron": 8, "Weapon_Sword_Thorium": 20, "Weapon_Sword_Cobalt": TT.band("Cobalt")[0], "Weapon_Sword_Mithril": TT.band("Mithril")[0]},
         "X2 xpStart = the CURRENT band starts")
    xt = [round(float(Roll.xpTier(JInt(L))), 3) for L in (1, 8, 20, 25, 100)]
    K.eq(xt, [1.0, 2.11, 4.91, round(4.91 + (7.43 - 4.91) * 5 / 8, 3), 53.07], "X2 xpTier (straight lines between the points)")
    cx = [int(Roll.craftXp("Weapon_Sword_Iron", JInt(0))), int(Roll.craftXp("Weapon_Sword_Mithril", JInt(5)))]
    K.eq(cx, [int(math.floor(80 * 2.11 + 0.5)), int(math.floor(2560 * round(BM.F_T[BM.BAND.index(TT.band("Mithril")[0])], 2) + 0.5))], "X2 craftXp: a Normal Iron sword / a Mythic Mithril sword")
    # ============================================================== X3 the fewest hits
    mh = lambda tool, blk, d: round(float(LL.minHitsI(tool, blk, JFloat(d))), 4)
    K.eq(int(Cfg.GATE_MINOWN), 2, "X3 gate.minHitsOwn default 2")
    r3 = [mh("Tool_Pickaxe_Copper", "Ore_Copper_Stone", 0.9), mh("Tool_Pickaxe_Copper", "Ore_Iron_Stone", 0.9), mh("Tool_Pickaxe_Iron", "Ore_Copper_Stone", 0.9),
          mh("Tool_Pickaxe_Copper", "Rock_Stone", 0.9), mh("Tool_Pickaxe_Copper", "Ore_Copper_Stone", 0.3), mh("Tool_Hatchet_Copper", "Ore_Copper_Stone", 0.9),
          mh("Tool_Hatchet_Pickaxe_Multitool_Copper", "Ore_Copper_Stone", 0.9), mh("Tool_Pickaxe_Copper", "Wood_Oak_Trunk", 0.9)]
    K.eq(r3, [0.5, 0.5, 0.9, 0.9, 0.3, 0.9, 0.5, 0.9], "X3 own / higher-tier ore capped at 1/2, lower-tier ore + stone + a weak hit + non-pickaxes + logs unchanged, the multitool capped")
    hb = 1.0
    hits = 0
    while not bool(JClass("com.hypixel.hytale.server.core.modules.blockhealth.BlockHealth").isDestroyed(JFloat(hb))) and hits < 9:
        hb = hb - float(LL.minHitsI("Tool_Pickaxe_Copper", "Ore_Copper_Stone", JFloat(5.0)))
        hits += 1
    K.eq(hits, 2, "X3 a huge own-tier hit still needs 2 hits (BlockHealth.isDestroyed on full health 1.0)")
    Cfg.GATE_MINOWN = 3
    hb, hits = 1.0, 0
    while not bool(JClass("com.hypixel.hytale.server.core.modules.blockhealth.BlockHealth").isDestroyed(JFloat(hb))) and hits < 9:
        hb = hb - float(LL.minHitsI("Tool_Pickaxe_Copper", "Ore_Copper_Stone", JFloat(5.0)))
        hits += 1
    Cfg.GATE_MINOWN = 0
    off = mh("Tool_Pickaxe_Copper", "Ore_Copper_Stone", 0.9)
    Cfg.GATE_MINOWN = 2
    K.check(hits == 3 and off == 0.9, "X3 gate.minHitsOwn 3 = 3 hits (%d), 0 = off (%s)" % (hits, off))
    K.notes.append("X3 model hits / blocks an hour (own tier, min 2): " + ", ".join("T%d %d / %.0f" % (t, BM.p6_hits(t, t, BM.p6_bp(t, "best")), BM.p6_blocks_h(BM.p6_hits(t, t, BM.p6_bp(t, "best")))) for t in (1, 6, 15)))
    # ============================================================== X4 the best owned tool + the pick-up gate
    U = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000000a6")
    pk = str(JClass(PKG + "Gear").pkey(U))
    RP = JClass("java.util.Properties")()
    LL.REG.put(pk, RP)
    pw = lambda bid: LL.pickWhy(U, bid)
    cats = [list(LL.catP(b_)) for b_ in ("Plant_Crop_Mushroom_Cap_Red", "Plant_Crop_Health3_Block", "Plant_Crop_Mana1", "Plant_Crop_Stamina2", "Plant_Fruit_Spiral",
                                          "Plant_Crop_Potato_StageFinal", "Rock_Stone", "Plant_Fruit_Coconut")]
    K.eq(cats, [[5, 15], [5, 8], [5, 2], [5, 5], [3, int(dict(zip([str(x) for x in LL.WOOD_W], [int(x) for x in LL.WOOD_M]))["Spiral"])], [4, 7], [0, -1], [0, -1]],
         "X4 catP: mushroom T15 + herbs T8 / T2 / T5 on the LADDER (fix round), fruit by its tree, a crop by the hit gate's table, stone / an untied fruit none")
    r_none = [pw(b_) is not None for b_ in ("Plant_Crop_Mushroom_Cap_Red", "Plant_Crop_Health3_Block", "Plant_Crop_Mana1", "Plant_Crop_Stamina2", "Rock_Stone")]
    K.eq(r_none, [True, True, False, True, False], "X4 no tools (hands = T1): a mushroom, a T8 and a T5 herb refused; a T2 herb + stone not")
    RP.setProperty("hoe.uid", "u1")
    RP.setProperty("hoe.id", "Tool_Hoe_Iron")
    r_iron = [pw(b_) is None for b_ in ("Plant_Crop_Mushroom_Cap_Red", "Plant_Crop_Stamina2", "Plant_Crop_Mana1")]
    K.eq(r_iron, [False, False, True], "X4 an Iron hoe (T2) owned: a mushroom (T15) and a T5 herb still refused - spec 11.7 step 6 (a Zone 1 hoe on a mushroom)")
    RP.setProperty("hoe.id", "Tool_Hoe_Thorium")
    b_th = LL.best(U, None, JInt(4), JInt(8))
    r_th = [pw(b_) is None for b_ in ("Plant_Crop_Mushroom_Cap_Red", "Plant_Crop_Stamina2", "Plant_Crop_Health3_Block")]
    K.check(r_th == [False, True, False] and int(b_th[0][0]) == 0 and str(b_th[1]) == "Tool_Hoe_Thorium",
            "X4 a Thorium hoe (T4): a T5 herb passes, a mushroom + a T8 herb refused; the F-harvest of a crop keeps the hit gate's rule (best = the Thorium hoe, full) %s" % r_th)
    RP.remove("hoe.uid")
    K.check(pw("Plant_Crop_Stamina2") is not None, "X4 a registry id without its uid (not owned) does not count")
    RP.setProperty("sickle.uid", "u2")
    RP.setProperty("sickle.id", "Tool_Sickle_Harvester_Mithril")
    bm = pw("Plant_Crop_Mushroom_Cap_Red")
    K.check(bm is not None and [int(x) for x in bm[0]][:4] == [2, 5, 15, 13] and str(bm[1]) == "Tool_Sickle_Harvester_Mithril",
            "X4 spec 11.4: a T15 mushroom with a best-owned T13 Harvester is refused (2 tiers up; the popup names it)")
    RP.setProperty("sickle.id", "Tool_Sickle_Harvester_Titanium_SkyWynn")
    K.check(pw("Plant_Crop_Mushroom_Cap_Red") is None and pw("Plant_Crop_Health3_Block") is None and str(LL.best(U, None, JInt(4), JInt(8))[1]) == "Tool_Sickle_Harvester_Titanium_SkyWynn",
            "X4 spec 11.4: a T14 Harvester in the bag lets bare hands pick the mushroom; the Harvester (sickle kind) counts for crops")
    K.check(LL.best(U, "Tool_Hoe_Crude", JInt(4), JInt(8))[1] is not None and int(LL.best(U, "Tool_Hoe_Crude", JInt(4), JInt(8))[0][0]) == 0, "X4 the held item is only the floor")
    RP.setProperty("hatchet.uid", "u3")
    RP.setProperty("hatchet.id", "Tool_Hatchet_Copper")
    f1 = (pw("Plant_Fruit_Apple") is None, pw("Plant_Fruit_Spiral") is not None)
    RP.setProperty("hatchet.id", "Tool_Hatchet_Cobalt")
    f2 = pw("Plant_Fruit_Spiral") is None
    K.check(f1 == (True, True) and f2, "X4 fruit: a Copper hatchet picks an Apple fruit, not a Spiral one (its tree %d tiers up); a Cobalt hatchet in the bag does %s" % (int(LL.catP("Plant_Fruit_Spiral")[1]) - 1, (f1, f2)))
    Cfg.PICK_GATE = False
    off4 = (pw("Plant_Crop_Mushroom_Cap_Red"), str(LL.best(U, None, JInt(4), JInt(8))[1]))
    Cfg.PICK_GATE = True
    K.check(off4[0] is None and off4[1] == "None", "X4 gate.pickup off: no pick-up gate, useNo reads the held item only (%s)" % (off4,))
    # fix round (critic 5): a registry not cached yet is read from its file once (GearLL.reg) - here DIR is unset (no file: hands), then a scratch file
    LL.REG.remove(pk)
    K.check(pw("Plant_Crop_Mushroom_Cap_Red") is not None, "X4 no registry file = hands only (refused)")
    dir0 = Cfg.DIR
    cfgd = os.path.join(scratch, "cfg")
    os.makedirs(os.path.join(cfgd, "lifelong"), exist_ok=True)
    fn = pk.replace("/", "_").replace("\\", "_").replace(":", "_").replace(".", "_") + ".properties"
    open(os.path.join(cfgd, "lifelong", fn), "w").write("sickle.uid=u9\nsickle.id=Tool_Sickle_Harvester_Titanium_SkyWynn\n")
    Cfg.DIR = JClass("java.nio.file.Paths").get(cfgd)
    LL.REG.remove(pk)
    rf = pw("Plant_Crop_Mushroom_Cap_Red")
    K.check(rf is None and LL.REG.get(pk) is not None, "X4 a registry not cached yet is read from its file (a T14 Harvester there: the mushroom passes, now cached)")
    Cfg.DIR = dir0
    LL.REG.put(pk, RP)
    gsrc = open(GEN, encoding="utf8").read()
    K.check("if (e.isCancelled() || e.getItemInHand() != null || !@PKG@.GearCfg.PICK_GATE) return;" in gsrc and "pl.getGameMode() == @GM@.Creative) return;" in gsrc[gsrc.index('event_system(gplk, "GearPickLockSys"'):][:900]
            and "if (@PKG@.GearLL.pickNo(pr, e.getBlockType())) e.setCancelled(true);" in gsrc, "X4 GearPickLockSys: only the no-item pick-up, creative skipped, cancel on refusal")
    K.check("BlockHarvestUtils.shouldPickupByInteraction(bt)" in gsrc, "X4 pickNo only gates blocks the engine picks up by interaction")
    K.notes.append("X4 UNVERIFIED in a bare JVM: the cancelled BreakBlockEvent's client side (the engine re-sends the block: performPickupByInteraction -> "
                   "BlockSection.invalidateBlock, VERIFIED bytecode) - Skyy's in-game step")
    # ============================================================== XR (fix round, engine critics 1 + 2): GearPickLockSys FIRST, GearMinHitSys LAST + its handle
    dpl = str(P("GearPickLockSys")().getDependencies())
    mhs = P("GearMinHitSys")()
    dmh = str(mhs.getDependencies())
    K.check("priority=-1431655764" in dpl and "order=AFTER" in dpl and "priority=1431655764" in dmh, "XR GearPickLockSys = RootDependency first (%s), GearMinHitSys = last (%s)" % (dpl, dmh))
    BT = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    btc = uf.get(None).allocateInstance(BT.class_)
    idf = BT.class_.getDeclaredField("id")
    idf.setAccessible(True)
    idf.set(btc, JString("Ore_Copper_Stone"))
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    DBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent")
    V3 = JClass(str(DBE.class_.getConstructors()[0].getParameterTypes()[1].getName()))          # the engine's Vector3i (org.joml)
    evs = [DBE(IS(JString("Tool_Pickaxe_Copper"), JInt(1)), V3(0, 0, 0), btc, JFloat(1.0), JFloat(d_)) for d_ in (0.9, 0.3, 0.9)]
    evs[2].setCancelled(True)
    for e_ in evs:
        mhs.handle(JInt(0), None, None, None, e_)
    K.eq([round(float(e_.getDamage()), 3) for e_ in evs], [0.5, 0.3, 0.9], "XR GearMinHitSys.handle: a 0.9 own-tier hit (another mod raised it) -> 0.5, a 0.3 hit kept, a cancelled hit left alone")
    # ============================================================== X5 level-up caps
    lc = dict(zip(RID, [int(x) for x in Cfg.LV_CAP]))
    K.eq(lc, {"normal": 10, "unique": 10, "rare": 10, "legendary": 10, "fabled": 10, "mythic": 2, "set": 10, "untiered": 3}, "X5 levelUp.cap: the rest +10, Mythic +2, Untiered +3")
    # ============================================================== X6 utpow
    up = dict((str(k), int(str(v))) for k, v in Cfg.UTPOW.items())
    fx = sorted((k[5:], v) for k, v in dp.items() if k.startswith("utfx."))
    K.check(len(fx) == 40 and sorted(up) == sorted(i for i, v in fx) and all(int(dp["utpow." + i]) == up[i] for i in up), "X6 a utpow row for each of the %d Untiered rows (default file = field)" % len(fx))
    smax = dict((SK[i], float(Cfg.S_MAX[i])) for i in range(len(SK)))
    tab = BM.p5_roll_table()
    fab_w = math.log(tab["fabled"][0])
    fab_a = math.log(tab["fabled"][2] * tab["fabled"][4]) / 4.0
    UNMOD = ("swing", "range", "pierce", "heal", "kb", "mregen")
    ARMW = (("Head", ("Head", "Helm", "Crown", "Hood", "Cap", "Mask")), ("Chest", ("Chest", "Plate", "Robe", "Jacket", "Cuirass")),
            ("Legs", ("Legs", "Leggings", "Greaves", "Trousers", "Skirt", "Boots")), ("Hands", ("Hands", "Gauntlets", "Gloves", "Cuffs")))

    def slot(iid):
        if iid.startswith("Weapon_"):
            return "Weapon"
        for sl, ws in ARMW:
            if any(w in iid for w in ws):
                return sl
        return "Weapon" if not iid.startswith("Armor_") else None

    def net(iid, row, p):
        body, _c, fixed = row.partition(",")
        tt, dm, em = {}, 1.0, 1.0
        spw = BM.P5_SLOT_POWER.get(slot(iid) or "", 100.0) / 100.0
        for k in body.split():
            tt[k] = tt.get(k, 0.0) + smax.get(k, 0.0) * p / 100.0 * spw
        for w in fixed.split():
            if w.startswith(UNMOD):
                continue
            j = max(w.rfind("+"), w.rfind("-"))
            k, n = w[:j], float(w[j:])
            if k == "hp":
                tt["hpp"] = tt.get("hpp", 0.0) + n
            elif k == "taken":
                em = em / (1 + n / 100.0)
            elif k == "lowhp":
                dm = dm * (1 + n / 200.0)
            elif k == "back":
                dm = dm * (1 + 0.25 * n / 100.0)
            elif k == "front":
                dm = dm * (1 + 0.5 * n / 100.0)
            else:
                tt[k] = tt.get(k, 0.0) + n
        return math.log(BM.p5_dps(tt, caster="mp" in body.split()) * dm * BM.p5_ehp(tt) * em), (fab_w if slot(iid) == "Weapon" else fab_a)
    rows, below, at_cap, dead = [], [], [], []
    for iid, row in fx:
        a, r = net(iid, row, up[iid])
        a70, _r = net(iid, row, 70)
        rows.append("%s %d%% %.2f (70%%: %.2f) vs %.2f" % (iid, up[iid], a, a70, r))
        if a < r - 1e-9:
            below.append(iid)
        elif up[iid] > 70 and net(iid, row, up[iid] - 5)[0] >= r - 1e-9:
            at_cap.append(iid)          # fix round 2: not the smallest 5 % step
    K.check(not below and len(fx) == 40, "X6 fix round 2: ALL %d Untiered rows >= their Fabled reference at their utpow (no exemptions): below %s" % (len(fx), below))
    K.check(not at_cap and all(70 <= up[i] <= 600 for i in up), "X6 each utpow is the smallest 5 %% step from 70 (cap 600): too high %s" % at_cap)
    K.check(all(dict(fx)["Armor_UT_Courier_" + sl_].startswith("cc cd,") for sl_ in ("Head", "Chest", "Hands", "Legs")), "X6 the Courier set's body lines are cc cd (fix round 2)")
    K.notes.append("X6 Untiered net log power at utpow (all 40): " + "; ".join(rows))
    # the REAL body lines (GearUtFx.lines on an identified Untiered document) = stat max x utpow x the level factor (+ the fixed lines)
    iid0 = [i for i, v in fx if i.startswith("Weapon_Sword_UT_")][0]
    row0 = dict(fx)[iid0]
    dd = Roll.newDoc(iid0, Defs.R_UT, True, "box", JInt(40))
    ln = Fx.lines(iid0, dd)
    b0 = row0.partition(",")[0].split()
    want = dict((k, int(round(smax[k] * up[iid0] / 100.0 * float(Lv.factor(JInt(int(Lv.level(iid0, dd))))) / 100.0))) for k in b0)
    got = dict((k, int(ln[SK.index(k)])) for k in b0)
    fixed0 = dict((w[:max(w.rfind("+"), w.rfind("-"))], float(w[max(w.rfind("+"), w.rfind("-")):])) for w in row0.partition(",")[2].split() if not w.startswith(UNMOD) and "=" not in w)
    K.check(ln is not None and all(got[k] - int(fixed0.get(k, 0)) == want[k] for k in b0), "X6 GearUtFx.lines(%s) body = stat max x utpow %d %% x level factor: %s vs %s" % (iid0, up[iid0], got, want))
    p2 = JClass("java.util.Properties")()
    p2.load(JClass("java.io.StringReader")(dtext.replace("\nutpow.%s=%d\n" % (iid0, up[iid0]), "\nutpow.%s=250\n" % iid0).replace("\nutpow.GhostSword=", "\nutpow.GhostSword=999\nutpow.Junk=")))
    Cfg.apply(p2, False)
    up2 = dict((str(k), int(str(v))) for k, v in Cfg.UTPOW.items())
    K.check(up2[iid0] == 250 and up2["GhostSword"] == up["GhostSword"] and int(Fx.utPow(iid0)) == 250 and int(Fx.utPow("Not_An_Ut_Item")) == int(Cfg.UT_POWER),
            "X6 a utpow file row is read, a bad one (999) = the default, an item without a row = utline.power")
    K.check(Fx.checkPow("utpow.x", "120") is None and Fx.checkPow("utpow.x", "600") is None and Fx.checkPow("utpow.x", "601") is not None
            and Fx.checkPow("utpow.x", "0") is not None and Fx.checkPow("utpow.x", "abc") is not None, "X6 checkPow 1-600")
    Cfg.apply(pd, False)
    # ============================================================== X7 armor bags hide their piece
    arm = [t for t in range(len(Pool.T_KEY)) if bool(Pool.T_ARM[t])]
    ab, wb = [], []
    for i in range(400):
        b = Unid.roll(JInt(5 + (i % 40)), JInt(-1), "mob", "test", JInt(0), None, JInt(1), JInt(5))
        if b is None:
            continue
        d = Unid.doc(b)
        (ab if bool(Pool.T_ARM[int(Unid.type(d))]) else wb).append(d)
    K.check(len(ab) > 20 and all(str(GData.str(d, "grp", "")) == "a" and bool(Unid.grpA(d)) and str(Unid.title(d)) == "Unidentified Armor" for d in ab),
            "X7 every random armor bag = grp a, 'Unidentified Armor' (%d)" % len(ab))
    K.check(all(str(Unid.title(d)) == "Unidentified Weapon" for d in wb) and len(wb) > 20, "X7 weapon bags unchanged ('Unidentified Weapon', %d)" % len(wb))
    K.check(all("Head" not in str(Unid.descMsg(d).getAnsiMessage() if hasattr(Unid.descMsg(d), "getAnsiMessage") else "") for d in ab[:5]), "X7 the tooltip does not name the piece")
    slots, okk = set(), True
    for d in ab[:40]:
        o = Unid.open(d, None)
        if o is None:
            okk = False
            continue
        t = int(Pool.typeOfId(str(o[0])))
        slots.add(str(Pool.T_KEY[t]))
        okk = okk and bool(Pool.T_ARM[t])
    K.check(okk and len(slots) >= 2, "X7 identify picks the piece among the armor slots (%s), always armor" % sorted(slots))
    K.check(all(Unid.why(d) is None for d in ab[:20]), "X7 why() lets a grp a bag open")
    # fix round (safety critic 1): a grp a bag whose STORED slot has nothing in its range while another armor slot has - why() lets it open, identify picks
    # a fitting slot; the same bag without grp (an old bag) keeps the refusal
    case = None
    for L_ in range(1, 102):
        for at_ in range(0, 4):
            fits = [t for t in arm if Unid.fit(JInt(t), JInt(at_), JInt(L_), JInt(L_)) is not None]
            if fits and len(fits) < len(arm):
                case = ([t for t in arm if t not in fits][0], at_, L_, fits)
                break
        if case:
            break
    if case is None:
        K.notes.append("X7 no level where one armor slot is empty and another not in this catalogue - fitA checked directly")
        K.check(all(bool(Unid.fitA(d)) for d in ab[:20]), "X7 fitA on random armor bags")
    else:
        t_, at_, L_, fits = case
        gb = Unid.doc(Unid.groupedA(Unid.make(JInt(t_), JInt(at_), JInt(0), JInt(L_), JInt(L_), "test", "test", JInt(0))))
        ob = Unid.doc(Unid.make(JInt(t_), JInt(at_), JInt(0), JInt(L_), JInt(L_), "test", "test", JInt(0)))
        go = Unid.open(gb, None)
        K.check(bool(Unid.grpA(gb)) and Unid.why(gb) is None and go is not None and int(Pool.typeOfId(str(go[0]))) in fits and Unid.why(ob) is not None,
                "X7 a grp a bag of an empty slot (%s, Lv %d, weight %d) opens into a fitting slot (%s); without grp it is refused (%s)"
                % (str(Pool.T_KEY[t_]), L_, at_, None if go is None else str(go[0]), str(Unid.why(ob))[:60]))
    # a smart bag (forced type -> hiddenA): hidden, kept
    tchest = int(Pool.typeIdx("Armor_Chest"))
    sb = Unid.hiddenA(Unid.roll(JInt(12), JInt(tchest), "mob", "smart", JInt(0), None, JInt(1), JInt(12)))
    sd = Unid.doc(sb)
    so = set(str(Pool.T_KEY[int(Pool.typeOfId(str(Unid.open(sd, None)[0])))]) for _ in range(12))
    K.check(str(GData.str(sd, "grp", "")) == "h" and str(Unid.title(sd)) == "Unidentified Armor" and not bool(Unid.grpA(sd)) and so == {"Armor_Chest"},
            "X7 a smart bag (grp h) hides the piece and keeps it (opens as %s)" % sorted(so))
    # a bag saved before 0.3.36 (no grp) shows + keeps its piece; a Mythic boss bag / grp k keep it; typeAtIdentify off shows it
    od = ab[0].clone()
    od.remove("grp")
    oty = str(Pool.T_KEY[int(Unid.type(od))])
    ots = set(str(Pool.T_KEY[int(Pool.typeOfId(str(Unid.open(od, None)[0])))]) for _ in range(8) if Unid.open(od, None) is not None)
    K.check("Armor" not in str(Unid.title(od)).replace("Unidentified ", "")[:5] and str(Unid.title(od)) != "Unidentified Armor" and ots == {oty},
            "X7 an old armor bag (no grp) shows its piece (%s) and opens as it" % str(Unid.title(od)))
    mb = Unid.makeZ(JInt(tchest), JInt(0), Defs.R_MY, JInt(20), JInt(20), "boss", "zone1", JInt(0), JInt(1))
    K.check(Unid.groupedA(mb) is not None and str(GData.str(Unid.doc(Unid.groupedA(mb)), "grp", "")) == "" and str(Unid.title(Unid.doc(mb))) != "Unidentified Armor",
            "X7 a Mythic boss bag keeps its piece (groupedA leaves it)")
    kb = Unid.kept(Unid.groupedA(Unid.make(JInt(tchest), JInt(0), JInt(0), JInt(10), JInt(12), "admin", "admin", JInt(0))))
    K.check(str(GData.str(Unid.doc(kb), "grp", "")) == "k" and str(Unid.title(Unid.doc(kb))) != "Unidentified Armor", "X7 an asked type (grp k) keeps its piece")
    Cfg.UNID_TYPEID = False
    t_off = str(Unid.title(ab[0]))
    Cfg.UNID_TYPEID = True
    K.check(t_off != "Unidentified Armor", "X7 unid.typeAtIdentify off shows the stored piece (%s)" % t_off)
    # orange armor bags: hidden; the piece is picked among the slots with Untiered rows (a bare JVM's fake items carry no ArmorSlot, so the Untiered
    # armor rows have no slot here - the 0.3.35 harness saw no orange armor bag either): an orange chest bag through GearUt.bag / make + groupedA
    Lu = [L for L in range(1, 102) if bool(Ut.covers(JInt(L)))]
    ub = None
    for L_ in Lu:
        ub = Ut.bag(JInt(L_), JInt(tchest), "meter", "meter", JInt(0))
        if ub is not None:
            break
    if ub is None:
        ub = Unid.groupedA(Unid.make(JInt(tchest), JInt(0), Defs.R_UT, JInt(Lu[0]), JInt(Lu[0] + 4), "meter", "meter", JInt(0)))
    udd = Unid.doc(ub)
    pa = set(str(Pool.T_KEY[int(Ut.pickA(JInt(tchest), JInt(0), Defs.R_UT, JInt(Lu[0]), JInt(Lu[-1])))]) for _ in range(20))
    K.check(str(Unid.title(udd)) == "Unidentified Untiered Armor" and bool(Unid.grpA(udd)) and all(x.startswith("Armor_") for x in pa),
            "X7 an orange armor bag: 'Unidentified Untiered Armor', grp a; GearUt.pickA picks an armor slot %s (the stored one when no slot has a row)" % sorted(pa))
    # ============================================================== X8 the Normal quality colour
    zj = zipfile.ZipFile(jar)
    ql = dict((n, json.loads(zj.read(n).decode("utf-8"))) for n in zj.namelist() if n.startswith("Server/Item/Qualities/Skyy_Gear_"))
    K.check(ql["Server/Item/Qualities/Skyy_Gear_Normal.json"]["TextColor"] == "#fefefe" and ql["Server/Item/Qualities/Skyy_Gear_Unique.json"]["TextColor"] == "#ffff55"
            and "#ffffff" not in [v["TextColor"] for v in ql.values()], "X8 Skyy_Gear_Normal TextColor #fefefe, no Gear quality draws #ffffff")
    # ============================================================== X9 migrateP6 on the REAL 0.3.35 default file
    old = _old_default_text()
    keys = [str(x) for x in Cfg.HP6_KEYS]
    po = _props(old)
    K.check(all(po.get(k) == str(o_) for k, o_ in zip(keys, Cfg.HP6_OLD)), "X9 the 0.3.35 default file holds every HP6_OLD text (%d rows)" % len(keys))
    r = Cfg.hp6Update(old)
    pn = _props(str(r[0]))
    want = dict(po)
    want.update(dict(zip(keys, [str(x) for x in Cfg.HP6_NEW])))
    want.update(dict(zip([str(x) for x in Cfg.HP6_ADDK], [str(x) for x in Cfg.HP6_ADDV])))
    K.eq(sorted(k for k in set(pn) | set(want) if pn.get(k) != want.get(k)), [], "X9 hp6Update: the planned rows move + the utpow rows appended, nothing else (Properties)")
    K.check(str(Cfg.HP6_MARK_ID) in str(r[0]) and len(r[2]) == 0 and len(r[3]) == 3 * (len(keys) + len(Cfg.HP6_ADDK)), "X9 the marker + one change-log row each, no notes")
    K.check(Cfg.hp6Update(str(r[0])) is None, "X9 a second update = null (marker)")
    K.check(bool(Cfg.p6Same(JString(old).getBytes("ISO-8859-1"), JString(str(r[0])).getBytes("ISO-8859-1"), r[3])), "X9 p6Same: only the planned keys differ")
    lgs = [str(Cfg.hp6Log(k_, o_, n_)).split("\t")[4:7] for k_, o_, n_ in (("levelUp.cap.normal", "6", "10"), ("utpow.GhostSword", "(none)", "155"), ("xp.craft.normal", "500", "80"),
                                                                           ("lifelong.ladders", "a>b(c*1)", "a>b(c*2)"))]
    K.eq(lgs, [["levelUp.cap[normal]", "6", "10"], ["utpow[GhostSword]", "(none)", "155"], ["xp.craft[normal]", "500", "80"], ["lifelong.ladders", "a>b(c*1)", "a>b(c*2)"]],
         "X9 hp6Log: table rows as table[entry], text rows as they are")
    rc = Cfg.hp6Update(old.replace("\n", "\r\n"))
    K.check(_props(str(rc[0])) == want and "\n" not in str(rc[0]).replace("\r\n", ""), "X9 CRLF kept")
    hand = old.replace("\nlevelUp.cap.rare=6\n", "\nlevelUp.cap.rare=8\n").replace("\nmulti.ladders=", "\nmulti.ladders=Tool_Hatchet_Pickaxe_Multitool_Crude>Tool_Hatchet_Pickaxe_Multitool_Copper(Ingredient_Bar_Copper*5)\n#multi.ladders=")
    rh = Cfg.hp6Update(hand)
    ph = _props(str(rh[0]))
    K.check(ph["levelUp.cap.rare"] == "8" and ph["levelUp.cap.normal"] == "10" and ph["multi.ladders"].endswith("(Ingredient_Bar_Copper*5)") and len(rh[2]) == 2,
            "X9 hand-set rows kept + noted: %s" % [str(x)[:70] for x in rh[2]])
    hu = old + "utpow.GhostSword=111\n"
    K.check(_props(str(Cfg.hp6Update(hu)[0]))["utpow.GhostSword"] == "111", "X9 a utpow line already there is kept")
    # fix round 2 (critic 1): an admin's utline.power = no utpow rows appended (they would override it), kept + noted; the rest still moves
    K.check(po.get("utline.power") == "70" and "\nutline.power=70\n" in old, "X9 the 0.3.35 default file holds utline.power=70")
    ru = Cfg.hp6Update(old.replace("\nutline.power=70\n", "\nutline.power=100\n"))
    pu = _props(str(ru[0]))
    K.check(pu["utline.power"] == "100" and not [k for k in pu if k.startswith("utpow.")] and str(Cfg.HP6_MARK_ID) in str(ru[0])
            and pu["levelUp.cap.normal"] == "10" and len(ru[2]) == 1 and "utline.power=100 kept" in str(ru[2][0]) and len(ru[3]) == 3 * len(keys),
            "X9 a hand-set utline.power (100): no utpow rows, one note, the planned rows still move: %s" % [str(x)[:90] for x in ru[2]])
    addv = dict(zip([str(x) for x in Cfg.HP6_ADDK], [str(x) for x in Cfg.HP6_ADDV]))
    K.check(_props(str(Cfg.hp6Update(old.replace("\nutline.power=70\n", "\nutline.power= 70 \n"))[0])).get("utpow.GhostSword") == addv["utpow.GhostSword"],
            "X9 utline.power=70 (spaces) = the default: the utpow rows are appended")
    # fix round 2: the Courier utfx rows move from cd to cc cd; a hand-edited Courier row is kept + noted
    K.check(pn["utfx.Armor_UT_Courier_Chest"] == "cc cd,spd+4 cc+2 taken+5" and po["utfx.Armor_UT_Courier_Chest"] == "cd,spd+4 cc+2 taken+5", "X9 the Courier utfx rows move cd -> cc cd")
    rcu = Cfg.hp6Update(old.replace("\nutfx.Armor_UT_Courier_Head=cd,spd+4 cc+1 taken+5\n", "\nutfx.Armor_UT_Courier_Head=str,spd+4 cc+1 taken+5\n"))
    pcu = _props(str(rcu[0]))
    K.check(pcu["utfx.Armor_UT_Courier_Head"] == "str,spd+4 cc+1 taken+5" and pcu["utfx.Armor_UT_Courier_Legs"].startswith("cc cd,")
            and len(rcu[2]) == 1 and "utfx.Armor_UT_Courier_Head" in str(rcu[2][0]), "X9 a hand-edited Courier row kept + noted: %s" % [str(x)[:90] for x in rcu[2]])
    K.eq(str(Cfg.hp6Log("utfx.Armor_UT_Courier_Head", "cd,spd+4 cc+1 taken+5", "cc cd,spd+4 cc+1 taken+5")).split("\t")[4:7],
         ["utfx[Armor_UT_Courier_Head]", "cd|spd+4 cc+1 taken+5", "cc cd|spd+4 cc+1 taken+5"], "X9 hp6Log: a utfx row as utfx[id] with its two columns")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "GearCfg")
    P = JClass("java.nio.file.Paths")
    fc = os.path.join(home, "config.properties")
    Cfg.FILE = P.get(fc)
    lgp = os.path.join(home, "config-changes.log")
    log0 = open(lgp, "rb").read() if os.path.isfile(lgp) else b""
    oc = open(fc, "rb").read()
    msgs = []
    for m in ("migrate0330", "migrateP4", "migrateP5"):
        msgs.append(str(getattr(Cfg, m)()))
    mid = open(fc, "rb").read()
    msg = str(Cfg.migrateP6())
    nc = open(fc, "rb").read()
    K.check("0.3.36" in msg, "D start 1: %s" % msg[:300].replace("\n", " | "))
    pm, pn = _props(mid.decode("latin-1")), _props(nc.decode("latin-1"))
    changed = sorted(k for k in set(pm) | set(pn) if pm.get(k) != pn.get(k))
    allowed = set(str(x) for x in Cfg.HP6_KEYS) | set(str(x) for x in Cfg.HP6_ADDK)
    K.check(changed and set(changed) <= allowed, "D migrateP6 changes only planned keys: %d (%s)" % (len(changed), [k for k in changed if k not in allowed][:5]))
    K.notes.append("D live rows moved by migrateP6: %s" % [k for k in changed if not k.startswith("utpow.")] + " + %d utpow rows" % len([k for k in changed if k.startswith("utpow.")]))
    K.notes.append("D migrateP5 / P4 / 0330 on the live copy (P5 had not run on the live file yet): %s" % [m_[:160] for m_ in msgs if m_])
    K.check(str(Cfg.HP6_MARK_ID).encode() in nc, "D the marker is in the live file")
    found = any(open(os.path.join(r_, f_), "rb").read() == mid for r_, _d, fs in os.walk(os.path.join(home, "config-history")) for f_ in fs)
    K.check(found, "D the config-history copy holds the bytes before migrateP6")
    lg = open(lgp, "rb").read()[len(log0):].decode("utf-8")
    K.eq(lg.count("\tSkyyGear 0.3.36\t-\tupdate\t"), len(changed), "D one change-log line per changed row")
    K.check((b"\r\n" in oc) == (b"\r\n" in nc), "D line endings kept")
    s1 = open(fc, "rb").read()
    msg2 = "".join(str(getattr(Cfg, m)()) for m in ("migrate0330", "migrateP4", "migrateP5", "migrateP6"))
    K.check(msg2 == "" and open(fc, "rb").read() == s1, "D start 2: nothing changes (%r)" % msg2[:120])
    Cfg.load()
    lc = [int(x) for x in Cfg.LV_CAP]
    K.check(lc[0] in (10, int(pn.get("levelUp.cap.normal", "10"))) and len(Cfg.UTPOW) >= 40 and int(Cfg.GATE_MINOWN) == 2 and bool(Cfg.PICK_GATE),
            "D the live file loads (level-up cap %d, %d utpow, minHitsOwn %d)" % (lc[0], len(Cfg.UTPOW), int(Cfg.GATE_MINOWN)))
    K.save()


HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
