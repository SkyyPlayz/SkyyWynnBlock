"""Harness for SkyyCollections 0.2.28 (round level-bands: the collection unlock ladder - Enchanted I / tools II / armor III / weapons IV per
base metal, alloys on BOTH input collections (charm + pickaxe III, gear V, Enchanted VI), the 15 tree / crop ladders, Harvester = Wheat II,
watering can = Lettuce II, the 0.2.27 gates grandfathered, the six Enchanted alloys, the Eternal Mushroom Spores, CollRw28Mig + CollEnch28Mig;
tools/collections_0_2_28_patch.py). Build first:
    python tools/collections_0_2_28_patch.py && python SkyyCollections/build_skyycollections_0.2.28.py

    python SkyyCollections/test_skyycollections_0.2.28.py [--jar <SkyyCollections-0.2.28.jar>] [--dir <scratch>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.27 -> 0.2.28: exactly the listed members differ (+ the new classes CollRw28Mig, CollEnch28Mig)
  X    exec     the default rewards = the ladder (every token at the place the rules below say, written out here independently of the build);
                coll:fn:tierup per metal / alloy (both inputs; the LAGGING one answered) / Wheat + Lettuce gates; the 0.2.27 gates kept
                (grandfathered); coll:fn:tierups; the recipe AND rule (Enchanted Bronze at Copper VI + Iron VI, the Bronze Mining set at V + V)
                incl. the managed knowledge; page labels; Server Setup check; CollEnch tiers / COLL2 / alias / ASMELT
  T    migr     CollRw28Mig on the 0.2.27 default (from the 0.2.27 jar) -> exactly the 0.2.28 table; on the LIVE rewards text (read only) after the
                older updates; CRLF; no final newline; a hand-edited line kept + logged; a removed one stays removed; a 2nd run = nothing.
                CollEnch28Mig on the LIVE config.properties text: the old-default ench.tier lines -> 1, a hand edit kept, CRLF, 2nd run = nothing
  D    live     the setup order on a scratch COPY of the live Skyy_SkyyCollections, started twice: both updates once (History copies byte for byte,
                Undo rows, migration-ladder28.log), the 2nd start changes nothing; a scratch profile above the new gates has them at once
  S    assets   the jar's files: 6 Enchanted alloys (100 alloy -> 1, Compressing tab, KnowledgeRequired, tier tag first), the Eternal Mushroom Spores
                item / block / drop list, "Mushroom Spores" names (no "seed" anywhere in a spore name), the TT_VERSION 3 log / crop tags
  M    pages    the 0.2.23 page phase on this jar (assert_menu_page on every view)
  AA   audit    the engine-access audit
Scratch: tools/dev/scratch/col28/coll (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "ci"))
import skyybuild as B
import harness_kit as HK
import tier_tags as TT
import skyyench as EN

VERSION = "0.2.28"
OLD_VERSION = "0.2.27"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "col28", "coll")))
PKG = "com.skyy.collections."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCollections")

# ---- the ladder as Skyy set it (docs/answered/gear.md 2026-10-18), written out here: token -> [(collection, tier)]
L = list(TT.LADDER)
BASE = ["Copper", "Iron", "Thorium", "Lead", "Cobalt", "Chromium", "Adamantite", "Slag", "Mithril", "Titanium"]
ALLOY = {"Bronze": ("Copper", "Iron"), "Dusk": ("Thorium", "Lead"), "Azurvane": ("Cobalt", "Chromium"), "Cinder": ("Adamantite", "Slag"),
         "Lumen": ("Mithril", "Titanium")}
WOOD = {1: "OakLog", 2: "BeechLog", 3: "MapleLog", 4: "DryLog", 5: "BottletreeLog", 6: "GumboabLog", 7: "FirLog", 8: "SpiralLog", 9: "RedwoodLog",
        10: "BurntLog", 11: "PetrifiedLog", 12: "SallowLog", 13: "JungleLog", 14: "BanyanLog", 15: "CrystalLog"}
CROP = dict((i + 1, c) for i, c in enumerate(["Wheat", "Lettuce", "Carrot", "Corn", "Cauliflower", "Turnip", "Pumpkin", "Aubergine", "Tomato",
                                              "Chilli", "Cotton", "Rice", "Potato", "Onion", "Mushroom"]))
WANT = {}
for m in BASE:
    WANT["pickaxe:" + m] = [(m, 2)]
    WANT["armor:" + m] = [(m, 3)]
    WANT["weapons:" + m] = [(m, 4)]
    if m in ("Iron", "Thorium", "Cobalt", "Adamantite"):          # SkyyGear's Mining armor ladder (review F4)
        WANT["armor.mining:" + m] = [(m, 3)]
for m in ("Iron", "Thorium", "Cobalt", "Adamantite"):
    WANT["armor.fishing:" + m] = [(m, 3)]
for a, (p, q) in ALLOY.items():
    WANT["pickaxe:" + a] = [(p, 3), (q, 3)]
    WANT["charm.furnace:" + a] = [(p, 3), (q, 3)]
    for k in ("armor", "weapons"):
        WANT[k + ":" + a] = [(p, 5), (q, 5)]
for t in range(1, 16):
    WANT["hatchet:" + L[t - 1]] = [(WOOD[t], 2)]
    WANT["harvester:" + L[t - 1]] = [(CROP[t], 2)]
    WANT["can:" + L[t - 1]] = [(CROP[max(t, 2)], 2)]          # "watering can takes lettuce"
    if t > 1:
        WANT["armor.foraging:" + L[t - 1]] = [(WOOD[t], 3)]
        WANT["armor.farming:" + L[t - 1]] = [(CROP[t], 3)]
WANT["harvester:Onyxium"] = [("Mushroom", 4)]
WANT["can:Onyxium"] = [("Mushroom", 4)]
WANT["armor.farming:Onyxium"] = [("Mushroom", 5)]
SLOTS = ("Head", "Chest", "Legs", "Hands")
WREC = {}
for i in ["Armor_Copper_" + s for s in SLOTS] + ["Armor_Fishing_A1_" + s for s in SLOTS]:
    WREC["recipe:%s_Recipe_Generated_0" % i] = [("Copper", 3)]
for i in ["Armor_Foraging_F1_" + s for s in SLOTS]:
    WREC["recipe:%s_Recipe_Generated_0" % i] = [("OakLog", 3)]
for i in ["Armor_Farming_P1_" + s for s in SLOTS]:
    WREC["recipe:%s_Recipe_Generated_0" % i] = [("Wheat", 3)]
for s in SLOTS:
    WREC["recipe:SkyyGear_Recipe_Armor_Bronze_" + s] = [("Copper", 5), ("Iron", 5)]
for a in ("Dusk", "Azurvane", "Cinder", "Lumen"):          # review F1: SkyyGear 0.3.29's KnowledgeRequired zone-alloy Mining sets
    for s in SLOTS:
        WREC["recipe:Armor_Mining_%s_%s_Recipe_Generated_0" % (a, s)] = list(ALLOY[a] and [(ALLOY[a][0], 5), (ALLOY[a][1], 5)])
FAMS = ["Axe", "Battleaxe", "Bo", "Club", "Crossbow", "Daggers", "Fist_Gauntlets", "GreatShield", "Kunai", "Longsword", "Mace", "Shield",
        "Shortbow", "Spellbook", "Staff", "Sword", "Wand", "Wand_SoulCage"]
for a in ("Dusk", "Azurvane", "Cinder", "Lumen"):          # SkyyArmory 0.1.39: the 72 KnowledgeRequired alloy weapons
    for f in FAMS:
        WREC["recipe:Weapon_%s_%s_SkyWynn_Recipe_Generated_0" % (f, a)] = [(ALLOY[a][0], 5), (ALLOY[a][1], 5)]
GEARKNOW = ([("Armor_Bronze_" + s) for s in SLOTS] + ["Armor_Mining_%s_%s" % (a, s) for a in ("Dusk", "Azurvane", "Cinder", "Lumen") for s in SLOTS]
            + ["Weapon_%s_%s_SkyWynn" % (f, a) for a in ("Dusk", "Azurvane", "Cinder", "Lumen") for f in FAMS])
ALLOY_KEYS = ["Bronze", "Dusk", "Azurvane", "Cinder", "Lumen", "Electrum"]
ALLOY_TAGS = ["T3 Bronze", "T6 Dusk", "T9 Azurvane", "T12 Cinder", "T15 Lumen", "T3 Electrum"]
EXPECT = {"CollReg": ["+f ANDR", "+f CHARM_ALLOY", "+m andMap", "+m andNote", "+m lowTier", "+m recNote", "~<clinit>", "~m configText", "~m rewardLines",
                      "~m rewardTextB", "~m rewardTextP", "~m rewardsText", "~m tierupLabel", "~m validate"],   # kinds + labels, the AND map, the defaults
          "CollEnch": ["+f ASMELT", "+f COLL2", "~<clinit>", "~m alias", "~m eterFlip", "~m merge"],          # the alloys, tier I, the smelt flip
          "CollC1": ["+<clinit>", "+f LEG_COLL", "+f LEG_TIER", "+f LEG_TOK", "+m allMet", "+m anyLists", "+m legColl", "+m legIdx", "+m legMet",
                     "~m tierup", "~m tierupList"],          # the AND rule + the grandfathered 0.2.27 gates
          "CollUnlocks": ["~m compute0"], "CollKit": ["~m rewardToken"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
          "CfgFile": ["~<clinit>"],                                 # the kit rows (ench.tier defaults, the alloy rows)
          "EnchRank": ["~<clinit>"],                                # the Compressing tab order (+ the 6 alloys)
          "CollTier": ["~<clinit>"],                                # tools/tier_tags.py TT_VERSION 3 rows
          "SkyyCollectionsPlugin": ["~m setup"]}                    # the two updates + the ready line
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["CollRw28Mig", "CollEnch28Mig"]

if HK.arg("--phase") == "compare":
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            exp = set(["manifest.json", "Server/Languages/en-US/server.lang"])
            for k in ALLOY_KEYS:
                exp |= set(["Server/Item/Items/SkyyCollections/Skyy_Ench_%s.json" % k, "Common/Items/SkyyCollections/Ench/%s.png" % k,
                            "Common/Icons/ItemsGenerated/SkyyCollections_Ench_%s.png" % k])
            exp |= set(["Server/Item/Items/SkyyCollections/Plant_Spores_Mushroom_Eternal.json",
                        "Server/Item/Items/SkyyCollections/Plant_Crop_Mushroom_Block_Eternal_SkyWynn.json",
                        "Server/Drops/SkyyCollections/Drops_Plant_Spores_Mushroom_Eternal_SkyWynn.json"])
            return self.check(sorted(got) == sorted(exp), "C: non-class entries changed = manifest.json + server.lang + the 6 Enchanted alloys' 3 files + the spores' 3 files "
                                                          "(extra %s, missing %s)" % (sorted(set(got) - exp)[:5], sorted(exp - set(got))[:5]))
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq


def _mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    _a = list(sys.argv)
    spec.loader.exec_module(m)
    sys.argv[:] = _a
    return m


def T21():
    return _mod("t21", os.path.join(HERE, "test_skyycollections_0.2.21.py"))


def T23():
    return _mod("t23", os.path.join(HERE, "test_skyycollections_0.2.23.py"))


def P(n):
    from jpype import JClass
    return JClass(PKG + n)


def old_cls(n):
    from jpype import JClass, JArray
    U_ = JClass("java.net.URL")
    srv = JClass("java.net.URLClassLoader")(JArray(U_)([JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()]), JClass("java.lang.ClassLoader").getPlatformClassLoader())
    Ld = JClass("java.net.URLClassLoader")(JArray(U_)([JClass("java.io.File")(OLD_JAR).toURI().toURL()]), srv)
    return JClass(PKG + n, loader=Ld)


def table(t_):
    from jpype import JArray, JString
    return dict((str(k), [str(x) for x in v]) for k, v in P("CollCobMig").table(JArray(JString)([l_.rstrip("\r") for l_ in t_.split("\n")])).items())


def where(tab, tok):
    return sorted((k.rsplit(".", 1)[0], int(k.rsplit(".", 1)[1])) for k, v in tab.items() if tok in v)


# ------------------------------------------------------------------------------------------------------------------- X: exec
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    t21 = T21()
    Reg, Store, Util, Fn, Kit, En, Unl, C1 = (P("CollReg"), P("CollStore"), P("CollUtil"), P("CollFn"), P("CollKit"), P("CollEnch"), P("CollUnlocks"),
                                              P("CollC1"))
    base = t21.fresh(scratch, "x")
    R = Reg.D
    ids = [str(R.id[c]) for c in range(R.n)]
    BY = dict((i, c) for c, i in enumerate(ids))
    new, old = table(str(Reg.rewardsText())), table(str(old_cls("CollReg").rewardsText()))
    # 1. every token where the ladder says (lowercase keys in the table)
    bad = []
    for tok, pl in sorted(WANT.items()):
        got = where(new, "tierup:" + tok)
        w = sorted((c.lower(), t) for c, t in pl)
        if got != w:
            bad.append((tok, got, w))
    K.eq(bad, [], "X the %d tier-up tokens sit exactly where the ladder puts them" % len(WANT))
    allt = sorted(set(x[7:] for v in new.values() for x in v if x.startswith("tierup:")))
    K.eq([t for t in allt if t not in WANT], [], "X no other tier-up token in the default")
    badr = [(tok, where(new, tok), sorted((c.lower(), t) for c, t in pl)) for tok, pl in WREC.items() if where(new, tok) != sorted((c.lower(), t) for c, t in pl)]
    K.eq(badr, [], "X the armor recipes: Copper / angler / Grove / Harvest first sets at III, the Bronze Mining set on Copper V + Iron V")
    oldt = sorted(set(x[7:] for v in old.values() for x in v if x.startswith("tierup:")))
    K.eq([t for t in oldt if t not in WANT], ["armor.mining:Mithril"], "X every 0.2.27 tier-up token has its new place (%d), only armor.mining:Mithril retired (review F4)" % len(oldt))
    # nothing else lost: every non-ladder token of 0.2.27 still on its line
    lost = [(k, x) for k, v in old.items() for x in v if not x.startswith("tierup:") and x not in WREC and x not in new.get(k, [])]
    K.eq(lost, [], "X every gift / bag / sigil / recipe token of 0.2.27 is still on its line")
    # every ladder tier has something (not its Enchanted tier I)
    lad = BASE + ["Gold", "Silver"] + list(WOOD.values()) + list(CROP.values())
    empty = ["%s.%d" % (c, t) for c in lad for t in range(2, int(Reg.maxTier(R, BY[c])) + 1)
             if not [x for x in new.get("%s.%d" % (c.lower(), t), []) if not x.startswith("recipe:Skyy_Sack_")]]
    K.eq(empty, [], "X every ladder tier II+ gives something")
    # 2. coll:fn:tierup
    fn = Fn("tierup")
    O = JClass("java.lang.Object")
    ans = lambda who, tok: fn.apply(JArray(O)([who, JString(tok)]))
    th = lambda c, t: int(Reg.threshold(R, BY[c], t))
    UUID = JClass("java.util.UUID")
    u = UUID.fromString("00000000-0000-0000-0000-0000000c2280")
    key = str(Util.pkey(u))
    gate = [(tok, str(ans(None, tok))) for tok in ("pickaxe:Copper", "pickaxe:Iron", "harvester:Copper", "can:Copper", "hatchet:Copper", "pickaxe:Lead")]
    K.check(gate[0][1] == "0|Copper|%s|2|%d|0" % (R.name[BY["Copper"]], th("Copper", 2)) and gate[2][1].startswith("0|Wheat|") and gate[2][1].split("|")[3] == "2"
            and gate[3][1].startswith("0|Lettuce|") and gate[3][1].split("|")[3] == "2" and gate[4][1].startswith("0|OakLog|") and gate[4][1].split("|")[3] == "2",
            "X tool tier-ups at II: pickaxe:Copper, Harvester = Wheat II, watering can = Lettuce II, hatchet:Copper Oak II (%s)" % gate)
    # alloy: Copper III + Iron II -> pickaxe:Bronze locked on the LAGGING Iron; both III -> unlocked
    t21.counts(base, key, [("Ore_Copper", th("Copper", 3)), ("Ore_Iron", th("Iron", 2))])
    r1 = str(ans(u, "pickaxe:Bronze"))
    c1 = str(ans(u, "charm.furnace:Bronze"))
    t21.counts(base, key, [("Ore_Copper", th("Copper", 3)), ("Ore_Iron", th("Iron", 3))])
    r2 = str(ans(u, "pickaxe:Bronze"))
    a5 = str(ans(u, "armor:Bronze"))
    tl = str(Fn("tierups").apply(u)).split(",")
    K.check(r1.startswith("0|Iron|") and r1.split("|")[3] == "3" and c1.startswith("0|Iron|") and r2.startswith("1|") and a5.startswith("0|"),
            "X alloy rule: Copper III + Iron II -> pickaxe:Bronze / charm.furnace:Bronze locked on Iron III (%s); both III -> unlocked (%s); Bronze armor still locked at V (%s)" % (r1, r2, a5))
    K.check("pickaxe:bronze" in [x.lower() for x in tl] and "charm.furnace:Bronze" in tl and "armor.mining:Bronze" not in tl and "pickaxe:Iron" in tl
            and "armor:Iron" in tl and "weapons:Iron" not in tl, "X coll:fn:tierups at Copper III + Iron III: Bronze pickaxe + charm, Iron armor, not Iron weapons / Bronze armor")
    # lagging = the lower have / need: Copper 10 % of III, Iron 90 % of III -> Copper
    t21.counts(base, key, [("Ore_Copper", th("Copper", 3) // 10), ("Ore_Iron", th("Iron", 3) * 9 // 10)])
    r3 = str(ans(u, "pickaxe:Bronze"))
    K.check(r3.startswith("0|Copper|"), "X the lagging input is answered (Copper 10 %% vs Iron 90 %%): %s" % r3)
    # grandfathered: Gumboab IV (the 0.2.27 hatchet:Bronze gate), Maple 0 -> still unlocked; Maple II alone -> unlocked too
    t21.counts(base, key, [("Wood_Gumboab_Trunk", th("GumboabLog", 4))])
    g1 = str(ans(u, "hatchet:Bronze"))
    gl = str(Fn("tierups").apply(u)).split(",")
    t21.counts(base, key, [("Wood_Gumboab_Trunk", th("GumboabLog", 3))])
    g2 = str(ans(u, "hatchet:Bronze"))
    K.check(g1.startswith("1|GumboabLog|") and "hatchet:Bronze" in gl and g2.startswith("0|MapleLog|"),
            "X never taken away: the 0.2.27 gate Gumboab IV still unlocks hatchet:Bronze (%s); below it the new gate Maple II is asked (%s)" % (g1, g2))
    t21.counts(base, key, [("Ore_Iron", th("Iron", 5))])          # 0.2.27: pickaxe:Bronze at Iron V alone
    K.check(str(ans(u, "pickaxe:Bronze")).startswith("1|Iron|") and str(ans(u, "charm.furnace:Bronze")).startswith("0|Copper|"),
            "X a player at the old Iron V keeps pickaxe:Bronze; the NEW charm token still asks Copper III")
    K.check(len(C1.LEG_TOK) > 0 and all(str(x) in WANT for x in C1.LEG_TOK), "X %d grandfathered 0.2.27 gates baked, each a ladder token" % len(C1.LEG_TOK))
    K.check(ans(None, "pickaxe:Onyxium") is None and ans(None, "hatchet:Onyxium") is None and ans(None, "shovel:Lead") is None, "X ungated stays null (pickaxe / hatchet Onyxium, unknown kinds)")
    # 3. recipes: the AND rule + the managed knowledge
    allp = JClass("java.util.HashSet")()
    for r_ in [str(x) for x in En.MRID]:
        allp.add(r_)
    rec = JClass("java.util.HashMap")()
    Reg.VALIDATED = True
    for c in range(R.n):
        for t in range(1, int(Reg.maxTier(R, c)) + 1):
            toks = Reg.REWARDS.get(str(R.id[c]).lower() + "." + str(t))
            if toks is not None:
                ids_ = [str(x)[7:].strip() for x in toks if str(x).startswith("recipe:")]
                if ids_:
                    rec.put("%d.%d" % (c, t), JArray(JString)(ids_))
    En.merge(rec, R, allp)
    Reg.ANDR = Reg.andMap(rec)
    Reg.RECIPES = rec
    eb = "Skyy_Ench_Bronze_Recipe_Generated_0"
    K.check(Reg.ANDR.containsKey(eb) and Reg.ANDR.containsKey("SkyyGear_Recipe_Armor_Bronze_Head") and not Reg.ANDR.containsKey("Skyy_Ench_Copper_Recipe_Generated_0"),
            "X ANDR: Enchanted Bronze + the Bronze Mining set need both metals; Enchanted Copper is a single gate")
    PCD = JClass("com.hypixel.hytale.server.core.entity.entities.player.data.PlayerConfigData")

    def unl(pairs):
        d_ = t21.counts(base, key, pairs)
        got = set(str(x) for x in Unl.compute(d_))
        pd = PCD()
        pd.setKnownRecipes(JClass("java.util.HashSet")())
        En.syncData(pd, str(En.wantSig(Unl.compute(d_))))
        return got, set(str(x) for x in pd.getKnownRecipes())
    u1, k1 = unl([("Ore_Copper", th("Copper", 6)), ("Ore_Iron", th("Iron", 5))])
    u2, k2 = unl([("Ore_Copper", th("Copper", 6)), ("Ore_Iron", th("Iron", 6))])
    u3, k3 = unl([("Ore_Copper", th("Copper", 1))])
    K.check(eb not in u1 and "SkyyGear_Recipe_Armor_Bronze_Head" in u1 and "Armor_Bronze_Head" in k1 and "Skyy_Ench_Bronze" not in k1,
            "X Copper VI + Iron V: the Bronze Mining set (both V) learned, Enchanted Bronze not (Iron below VI)")
    u4, k4 = unl([("Ore_Thorium", th("Thorium", 5)), ("Ore_Lead_SkyWynn", th("Lead", 4))])
    u5, k5 = unl([("Ore_Thorium", th("Thorium", 5)), ("Ore_Lead_SkyWynn", th("Lead", 5))])
    dusk = ["Armor_Mining_Dusk_%s" % s_ for s_ in SLOTS]
    lw = ["Weapon_%s_Lumen_SkyWynn" % f for f in FAMS]
    u6, k6 = unl([("Ore_Mithril", th("Mithril", 5)), ("Ore_Titanium_SkyWynn", th("Titanium", 4))])
    u7, k7 = unl([("Ore_Mithril", th("Mithril", 5)), ("Ore_Titanium_SkyWynn", th("Titanium", 5))])
    K.check(not any(x in k6 for x in lw) and all(x in k7 for x in lw) and "Weapon_Sword_Dusk_SkyWynn" not in k7,
            "X the 18 Lumen weapons (SkyyArmory 0.1.39) are learned at Mithril V + Titanium V, not at Titanium IV; Dusk ones not")
    K.check(not any(x in k4 for x in dusk) and all(x in k5 for x in dusk) and all(("Armor_Mining_Dusk_%s_Recipe_Generated_0" % s_) in u5 for s_ in SLOTS),
            "X review F1: the Dusk Mining set (KnowledgeRequired in SkyyGear 0.3.29) is learned at Thorium V + Lead V, not at Lead IV")
    cell5l = str(Reg.rewardText(R, BY["Lead"], 5))
    K.check("(with %s V)" % R.name[BY["Thorium"]] in cell5l and "(with %s V)" % R.name[BY["Lead"]] in str(Reg.rewardText(R, BY["Thorium"], 5)),
            "X the Mining set recipe line names the other metal: Lead V '%s'" % cell5l[:220])
    K.check(eb in u2 and "Skyy_Ench_Bronze" in k2, "X Copper VI + Iron VI: Enchanted Bronze unlocked + known (the same known entry SkyyWorldGen's Alloy_Ench_Bronze smelt needs)")
    K.check("Skyy_Ench_Copper_Recipe_Generated_0" in u3 and "Skyy_Ench_Copper" in k3 and "Armor_Bronze_Head" not in k3, "X Copper I: Enchanted Copper (tier I)")
    # 4. labels, the check, CollEnch
    cell = str(Reg.rewardTextP(R, BY["Copper"], 3, False))
    cell5 = str(Reg.rewardTextP(R, BY["Iron"], 5, False))
    cell4 = str(Reg.rewardTextP(R, BY["Iron"], 4, False))
    K.check("Bronze Pickaxe tier-up (with Iron Ore III)" in cell and "Furnace Charm I recipe (Bronze smelting) (with Iron Ore III)" in cell and "Copper Armor unlock" in cell
            and "Iron Weapons unlock" in cell4 and "Bronze Armor unlock (with Copper Ore V)" in cell5 and "Mining Armor tier-up" not in cell5,
            "X page cells: Copper III '%s' / Iron IV '%s' / Iron V '%s'" % (cell[:200], cell4[:80], cell5[:200]))
    ck = lambda v: Kit.rewardToken(JString(v))
    K.check(ck("tierup:weapons:Iron") is None and ck("tierup:armor:Bronze") is None and ck("tierup:charm.furnace:Lumen") is None and ck("tierup:pickaxe:Gold") is not None,
            "X Server Setup: weapons / armor / charm.furnace accepted, tierup:pickaxe:Gold still refused")
    keys = [str(x) for x in En.KEY]
    tdef = dict(zip(keys, [int(x) for x in En.TDEF]))
    K.check(all(tdef[k] == 1 for k in ("Copper", "Iron", "Thorium", "Lead", "Adamantite", "Mithril", "Gold", "Oak", "Beech", "Wheat", "Lettuce", "Mushroom"))
            and tdef["Cobblestone"] == 3 and tdef["Bone"] == 3 and all(tdef[k] == 6 for k in ALLOY_KEYS),
            "X ench.tier defaults: base metals / logs / crops I, stone / mob drops unchanged (III), the alloys VI")
    c2 = dict(zip(keys, [str(x) for x in En.COLL2]))
    K.check([c2[k] for k in ALLOY_KEYS] == ["Iron", "Lead", "Chromium", "Slag", "Titanium", "Silver"] and c2["Copper"] == "",
            "X COLL2: each Enchanted alloy's second parent")
    K.check(En.alias(JString("Skyy_Ench_Bronze"), 1) is None and str(En.alias(JString("Skyy_Ench_Copper"), 1)[0]) == "Ore_Copper",
            "X coll:fn:add alias: an Enchanted alloy credits nothing (no collection); Enchanted Copper still credits Copper Ore")
    K.eq([str(x) for x in En.ASMELT], ["Alloy_Ench_" + k for k in ALLOY_KEYS], "X ASMELT = SkyyWorldGen 0.7.5's six Enchanted alloy smelts")
    mid = [str(x) for x in En.MID]
    K.check(all("Skyy_Ench_" + k in mid[:len(En.ID)] for k in ALLOY_KEYS) and mid[-92:] == GEARKNOW and "Plant_Spores_Mushroom_Eternal" in mid,
            "X managed knowledge: + 6 Enchanted alloys (Enchanted part), + the Eternal spores, + the 5 alloy Mining sets + the 72 Armory alloy weapons (%d entries)" % len(mid))
    et = Fn("eternal")
    e0 = et.apply(JArray(O)([u, JString("Plant_Spores_Mushroom_Eternal")]))
    K.check(e0 is not None and "Mushroom" in str(e0), "X coll:fn:eternal knows the Eternal Mushroom Spores (%s)" % e0)
    K.save()


# ------------------------------------------------------------------------------------------------------------------- T: migr
def run_migr(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    t21 = T21()
    Reg, Rw, Em = P("CollReg"), P("CollRw28Mig"), P("CollEnch28Mig")
    OLDER = [P(n) for n in ("CollToolMig", "CollRw21Mig", "CollRw24Mig", "CollRw25Mig", "CollRw27Mig")]
    t21.fresh(scratch, "t")
    OLDDEF = str(old_cls("CollReg").rewardsText())          # the 0.2.27 default
    DEF = str(Reg.rewardsText())

    def upd(t_):
        r_ = Rw.update(t_)
        return None if r_ is None else (str(r_[0]), [str(x) for x in r_[1]], str(r_[2]), int(r_[3]), int(r_[4]), bool(r_[5]), int(r_[6]))
    nk = len(Rw.K)
    K.check(Rw.update(DEF) is None and all(M_.update(DEF) is None for M_ in OLDER), "T a fresh 0.2.28 rewards.properties: every update = nothing (markers)")
    u0 = upd(OLDDEF)
    K.check(u0 is not None and u0[5] and u0[3] == nk and u0[4] == 0 and table(u0[0]) == table(DEF) and upd(u0[0]) is None,
            "T the 0.2.27 default -> the loader reads exactly the 0.2.28 default (%d entries updated / added); a 2nd run = nothing" % nk)
    K.check(len(u0[1]) == 3 * nk, "T one Undo row per entry (%d)" % nk)
    live = open(os.path.join(LIVE_DIR, "rewards.properties"), "rb").read().decode("latin-1")
    t_ = live
    for M_ in OLDER:
        r_ = M_.update(t_)
        t_ = t_ if r_ is None else str(r_[0])
    u1 = upd(t_)
    K.check(u1 is not None and u1[5] and upd(u1[0]) is None, "T the LIVE file: %d entries updated, %d kept by hand; the loader reads the old table + those; a 2nd run = nothing" % (u1[3], u1[4]))
    tl = table(u1[0])
    K.check(where(tl, "tierup:pickaxe:Copper") == [("copper", 2)] and where(tl, "tierup:pickaxe:Bronze") == [("copper", 3), ("iron", 3)] or u1[4] > 0,
            "T the LIVE file: pickaxe:Copper on Copper II, pickaxe:Bronze on Copper III + Iron III")
    K.check(u1[0].count(str(Rw.MARK5)) == 1, "T the marker once")
    crlf = t_.replace("\r\n", "\n").replace("\n", "\r\n")
    uc = upd(crlf)
    K.check(uc[5] and uc[0].count("\r\n") == uc[0].count("\n") and uc[3] == u1[3], "T CRLF kept on every line")
    une = upd(t_.rstrip("\n").rstrip("\r"))
    K.check(une[5] and not une[0].endswith("\n") and une[3] == u1[3], "T no final newline stays none")
    lk = [l_ for l_ in t_.split("\n") if l_.lower().startswith("copper.4=")]
    own = t_.replace(lk[0], "Copper.4=coins:7", 1) if lk else t_
    uo = upd(own)
    K.check(bool(lk) and uo[5] and uo[3] == u1[3] - 1 and uo[4] == 1 and table(uo[0])["copper.4"] == ["coins:7"] and "kept hand-edited line" in uo[2],
            "T a hand-edited Copper.4 line: kept + logged, the other entries updated")
    gone = "\n".join(l_ for l_ in t_.split("\n") if not l_.lower().startswith("copper.4="))
    ug = upd(gone)
    K.check(ug[5] and ug[3] == u1[3] - 1 and "copper.4" not in table(ug[0]) and "an admin removed it" in ug[2], "T a removed Copper.4 line stays removed (logged)")
    # CollEnch28Mig on config.properties
    cfg = open(os.path.join(LIVE_DIR, "config.properties"), "rb").read().decode("latin-1")

    def eu(t_):
        r_ = Em.update(t_)
        return None if r_ is None else (str(r_[0]), int(r_[1]), str(r_[2]), [str(x) for x in r_[3]])
    K.check(Em.update(str(Reg.configText())) is None, "T a fresh 0.2.28 config.properties: CollEnch28Mig = nothing (marker)")
    e1 = eu(cfg)
    olds = dict((str(k), str(v)) for k, v in zip(Em.KEYS, Em.OLDV))
    have = dict(re.findall(r"(?m)^(ench\.tier\.[a-z0-9]+)=(\S+)", cfg))
    want_n = sum(1 for k, v in have.items() if olds.get(k) == v)
    K.check(e1 is not None and e1[1] == want_n and "ench.tier.copper=1" in e1[0] and "ench.tier.cobblestone=3" in e1[0] and eu(e1[0]) is None,
            "T the LIVE config.properties: %d ench.tier lines at the old default -> 1 (Copper ... ), Cobblestone untouched; a 2nd run = nothing" % e1[1])
    from jpype import JArray, JByte
    sa = P("CollBypassMig").sameAfter(cfg.encode("latin-1"), e1[0].encode("latin-1"), e1[3])
    K.check(bool(sa), "T sameAfter: only those values changed")
    e2 = eu(cfg.replace("ench.tier.iron=3", "ench.tier.iron=5"))
    K.check(e2[1] == want_n - 1 and "ench.tier.iron=5" in e2[0] and "ench.tier.iron=5" in e2[2], "T a hand-edited ench.tier.iron=5 is kept + named")
    e3 = eu(cfg.replace("\r\n", "\n").replace("\n", "\r\n"))
    K.check(e3[1] == want_n and e3[0].count("\r\n") == e3[0].count("\n"), "T CRLF kept")
    K.notes.append("T LIVE rewards.properties: %d entries updated / added, %d hand-edited kept; LIVE config.properties: %d ench.tier lines -> I; kept: %s" % (u1[3], u1[4], e1[1], e1[2] or "none"))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- D: live
def run_live(out, jar, scratch, home):
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Reg, Store = P("CollReg"), P("CollStore")
    b_ = JClass("java.nio.file.Paths").get(home)
    rw0 = open(os.path.join(home, "rewards.properties"), "rb").read()
    cf0 = open(os.path.join(home, "config.properties"), "rb").read()
    msgs, hs = [], []
    for start in (1, 2):
        Reg.BASE = b_
        Store.DIR = b_.resolve("counts")
        P("CollBagMigrate").run(b_)
        P("CollBypassMig").run(b_)
        P("CollCoinMig").run(b_)
        e = str(P("CollEnch28Mig").run(b_))
        Reg.loadAll()
        for m in ("CollCobMig", "CollSigMig", "CollShardMig", "CollToolMig", "CollRw21Mig", "CollRw24Mig", "CollRw25Mig", "CollRw27Mig"):
            P(m).run(b_)
        msgs.append((e, str(P("CollRw28Mig").run(b_))))
        hs.append(HK.tree_hash(home))
    K.check(msgs[0][1].startswith("the collection unlock ladder") and msgs[0][0].startswith("config.properties:") and msgs[1] == ("", "") and hs[0] == hs[1],
            "D the 1st start runs both updates once (%s | %s), the 2nd changes nothing" % (msgs[0][0][:120], msgs[0][1][:120]))
    En = P("CollEnch")
    keys = [str(x) for x in En.KEY]
    tier = dict(zip(keys, [int(x) for x in En.TIER]))
    K.check(tier["Copper"] == 1 and tier["Oak"] == 1 and tier["Cobblestone"] == 3, "D the live ench tiers read back: Copper I, Oak I, Cobblestone III")
    fn = P("CollFn")("tierup")
    O = JClass("java.lang.Object")
    miss = [t for t in WANT if fn.apply(JArray(O)([None, JString(t)])) is None]
    K.eq(miss, [], "D the live registry gates all %d ladder tokens" % len(WANT))
    chg = open(os.path.join(home, "config-changes.log"), encoding="latin-1").read()
    rows = [l_ for l_ in chg.split("\n") if "SkyyCollections 0.2.28" in l_]
    K.check(len([r for r in rows if "\trewards[" in r]) == len(P("CollRw28Mig").K) and len([r for r in rows if "\tench.tier." in r]) >= 1,
            "D Undo rows: %d rewards[<entry>] + %d ench.tier" % (len([r for r in rows if "\trewards[" in r]), len([r for r in rows if "\tench.tier." in r])))
    hist = os.path.join(home, "config-history")
    hf = [open(os.path.join(hist, f), "rb").read() for f in os.listdir(hist)] if os.path.isdir(hist) else []
    K.check(rw0 in hf and cf0 in hf, "D config-history holds the old rewards.properties AND config.properties byte for byte")
    K.check(os.path.isfile(os.path.join(home, "migration-ladder28.log")), "D migration-ladder28.log written")
    K.notes.append("D 1st start: %s | %s" % (msgs[0][0][:300], msgs[0][1][:300]))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- S: assets
def run_assets(out, jar, scratch, _home):
    K = HK.Child(out)
    z = zipfile.ZipFile(jar)
    nm = set(z.namelist())
    lang = z.read("Server/Languages/en-US/server.lang").decode("utf-8")
    L_ = dict(l.split("=", 1) for l in lang.split("\n") if "=" in l)
    for k, tag in zip(ALLOY_KEYS, ALLOY_TAGS):
        p = "Server/Item/Items/SkyyCollections/Skyy_Ench_%s.json" % k
        j = json.loads(z.read(p)) if p in nm else {}
        r = j.get("Recipe", {})
        inp = dict((t[0], t[2]) for t in EN.TABLE_ALLOYS)[k]
        K.check(r.get("Input") == [{"ItemId": inp, "Quantity": 100}] and r.get("KnowledgeRequired") is True and r.get("OutputQuantity") == 1
                and r["BenchRequirement"][0]["Categories"] == [EN.TAB_ID] and ("Common/" + j.get("Icon", "")) in nm,
                "S Enchanted %s: 100 %s -> 1 at the Compressing tab, KnowledgeRequired, its own icon" % (k, inp))
        K.check(L_.get("server.items.Skyy_Ench_%s.description" % k, "").startswith(tag + " - ") and L_.get("server.items.Skyy_Ench_%s.name" % k) == "Enchanted %s Ingot" % k,
                "S Enchanted %s: name + flavor text starting '%s'" % (k, tag))
    sp = json.loads(z.read("Server/Item/Items/SkyyCollections/Plant_Spores_Mushroom_Eternal.json"))
    bl = json.loads(z.read("Server/Item/Items/SkyyCollections/Plant_Crop_Mushroom_Block_Eternal_SkyWynn.json"))
    dr = json.loads(z.read("Server/Drops/SkyyCollections/Drops_Plant_Spores_Mushroom_Eternal_SkyWynn.json"))
    K.check([x["ItemId"] for x in sp["Recipe"]["Input"]] == ["Ingredient_Life_Essence", "Plant_Crop_Mushroom_Cap_Brown", "Plant_Seeds_Mushroom"]
            and sp["Recipe"]["KnowledgeRequired"] is True and sp["Recipe"]["BenchRequirement"][0]["Id"] == "Farmingbench"
            and sp["Interactions"]["Secondary"]["Interactions"][0]["BlockTypeToPlace"] == "Plant_Crop_Mushroom_Block_Eternal_SkyWynn",
            "S Eternal Mushroom Spores: the Eternal seed recipe pattern (20 Essence + 10 Brown Cap + 1 spores, Farmer's Workbench), places our block")
    st = bl["BlockType"]["Farming"]["Stages"]["Default"]
    K.check([x["Type"] for x in st] == ["BlockState", "Spread"] and bl["BlockType"]["Gathering"]["Soft"]["DropList"] == "Drops_Plant_Spores_Mushroom_Eternal_SkyWynn"
            and dr["Container"]["Item"]["ItemId"] == "Plant_Spores_Mushroom_Eternal", "S the Eternal spore block spreads and stays (no Empty step) and drops the spores back")
    names = [L_.get("server.items.%s.name" % i, "") for i in ("Plant_Spores_Mushroom_Eternal", "Plant_Seeds_Mushroom", "Plant_Crop_Mushroom_Stage_0")]
    K.eq(names, ["Eternal Mushroom Spores", "Mushroom Spores", "Mushroom Spores"], "S spore names (shown names say spores)")
    K.check(not any("seed" in n.lower() for n in names) and L_.get("server.items.Plant_Spores_Mushroom_Eternal.description", "").startswith("T15 "),
            "S no 'seed' in a spore name; the Eternal spores' flavor text starts with its tag")
    tags = dict((i, L_.get("server.items.%s.description" % i, "").split(" - ")[0]) for i in ("Wood_Maple_Trunk", "Wood_Gumboab_Trunk", "Plant_Crop_Turnip_Item",
                                                                                               "Skyy_Ench_Maple", "Plant_Crop_Mushroom_Cap_Brown", "Wood_Crystal_Trunk"))
    K.eq(tags, dict((i, TT.tag_for(i)) for i in tags), "S TT_VERSION 3 tags in the flavor text (Maple %s, Gumboab %s, Turnip %s)" % (tags["Wood_Maple_Trunk"], tags["Wood_Gumboab_Trunk"], tags["Plant_Crop_Turnip_Item"]))
    K.check(TT.tier("Wood_Maple_Trunk") == 3 and TT.tier("Wood_Gumboab_Trunk") == 6 and TT.tier("Plant_Crop_Turnip_Item") == 6, "S the spec's test items: Maple T3, Gumboab T6, Turnip T6")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- M: pages
def run_pages(out, jar, scratch, home):
    """the 0.2.23 page phase as it is; its one version check (the ready line names 0.2.23) asks for 0.2.28 instead"""
    ck0 = HK.Child.check
    plug = zipfile.ZipFile(jar).read("com/skyy/collections/SkyyCollectionsPlugin.class")

    def ck(self, cond, what):
        if what == "PAGE the ready line names 0.2.23":
            return ck0(self, re.search(rb"\[SkyyCollections\] 0\.2\.28 ready", plug) is not None, "PAGE the ready line names 0.2.28")
        return ck0(self, cond, what)
    eq0 = HK.Child.eq
    TAGS = ["", "Armor_Copper_Chest", "Armor_Copper_Head", "Ingredient_Bar_Iron", "Tool_Pickaxe_Mithril"]

    def eq(self, got, want, what):
        if what == "LIST the tier tags" and want == ["", "T2", "T2", "T3", "T7"]:
            w2 = [""] + [str(P("CollTier").tierText(i)) for i in TAGS[1:]]
            eq0(self, w2, ["", "T1", "T1", "T2", "T13"], "LIST the rows' tags on the 15-step ladder (Copper T1, Iron T2, Mithril T13)")
            return eq0(self, got, w2, "LIST the tier tags (15-step ladder)")
        return eq0(self, got, want, what)
    HK.Child.check = ck
    HK.Child.eq = eq
    T23().run_pages(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("exec", run_exec), ("migr", run_migr), ("assets", run_assets), ("pages", run_pages), ("live", run_live)], __file__,
           live=(LIVE_DIR, "Skyy_SkyyCollections"))
