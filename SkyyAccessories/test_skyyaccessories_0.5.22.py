"""Harness for SkyyAccessories 0.5.22 (VOID CHARMS + ACCESSORY POWER; tools/accessories_0_5_22_patch.py, research/Accessory-Power-Spec.md).
Build first: python tools/accessories_0_5_22_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.22.py

    python SkyyAccessories/test_skyyaccessories_0.5.22.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.5.21 -> 0.5.22: + AccPower, AccPowerFn, AccPowerCmd, AccHubOpen, HubBar; - AccOnce* (the lifelong bag item); the listed members
                differ; non-class entries: manifest, server.lang, the 15 drop-up upgrade items + the bag item (S), the 59 kit art files
  S    assets   the 15 drop-only upgrade recipes (Unique / Rare / Legendary of Brawler, Runic, Stonehide, Razorfang, Feather: the rarity below +
                materials, the bag's own category; the Normal never gets one), the retired bag item (hidden, no recipe, renamed), the texts
                (no /accessories, 'Accessory Bag' only in the old item's name), the shared Bags tab text, the kit art
  P    POWER, EXECUTED on the jar's AccPower / AccDefs / AccGear:
         P1 the AP sum (best of each line, lower copies / duplicates 0, Lantern, benches by rarity + half / none, the Omni = 143 and a bench
            next to it 0, retired 0, the bag item 0, a switched-off line 0) + apOne / apIf (the hover texts)
         P2 the multiplier at 0 / 60 / 350 / 1,200 AP (spec 2) and the guard
         P3 EVERY Power stat at 3 AP levels (60, 350, 1,200) = the Python twin (rounded like it is applied)
         P4 the pick: free, the 5 s wait, the file per profile, 'already', unknown / hidden names, profile:busy writes nothing
         P5 the Combat 15 lock (no SkyySkills, Combat 14, Combat 15) + the fallback when a pick becomes locked / hidden
         P6 the doors: acc:power:<uuid>, skill:bonus source 'accessories' (only the stats with a reader; bp / swing / fish flags), busy and
            leave remove it, the combat sums for AccEffects
         P7 the gear:extra text = the lines + the Power, signed (Glass Cannon)
         P8 power.properties: written once when missing, custom numbers / hidden Powers / a bad power.ap, the kit hooks checkAp / checkStat
         P9 acc:fn:power get / set (no wait for a loadout)
  R    THE BAG ITEM RETIREMENT (AccStarter on the 0.5.18 harness World): every copy removed, journal REMOVE + DONE first, the one-time chat
       line exactly once (relog), a crash before the marker write removes a copy that came back again (no loss: the bag file is untouched)
  K    CRAFT: drop-only lines - no row while none is in the bag (an inventory copy does not count), the next rarity as UPGRADE once one is in
       the bag, upgraded IN PLACE exactly once (a double click uses nothing), never a from-scratch recipe; a normal line still crafts
  M    THE PAGE on the real engine page manager (tools/hub_tab_kit.py): the hub tab registered (Void Charms, /charms), BAG / CRAFT / POWER
       built and checked as kit 1.7 hub pages (SUI.assert_menu_page: 1600 x 980, rows 1 + 2, ONE sub row, no back button, no pager), the
       60-cell bag grid + the inventory grid, select + Equip / Unequip through the clicks, Pick + the switch wait through the clicks
  D    live     start twice on a scratch COPY of the live NewBetaTest Skyy_SkyyAccessories (config + power.properties): the first start
                writes power.properties only, the second changes nothing
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyonce_harness as OH
import skyyui as SUI

VERSION = "0.5.22"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-0.5.21.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "ap1", "acc")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyAccessories")
PKG = "com.skyy.accessories."
BAGCAT = "SkyyAccessoryBag"
BAG_REQ = [{"Type": "Crafting", "Id": BAGCAT, "Categories": [BAGCAT]}]
OMNI = "Skyy_Accessory_Omni"
BAG = "Skyy_Accessory_Bag"
DROP_UP = ["Strength", "MagicPower", "Defense", "Crit", "Feather"]
ADDED = ["AccHubOpen", "AccPower", "AccPowerCmd", "AccPowerFn", "HubBar"]
REMOVED = ["AccOnce", "AccOnceDropSys", "AccOnceFn", "AccOnceInvSys", "AccOnceReady", "AccOnceTask", "AccOnceThrowSys"]
EXPECT = {
    "AccAdmin": ["~m giveCmd", "~m giveable", "~m msg"],                    # the bag item is not given any more; [Void Charms] / /charms texts
    "AccCfg": ["~<clinit>", "~m load", "~m reload", "~m writeDefaults"],   # reload + AccPower.load; the default text without the retired switches
    "AccCmd": ["~c ", "~m execute"],                                         # /charms (/charm, /ch) + power; no AccOnce recall
    "AccCraft": ["~m autoOne", "~m autoRun", "~m back", "~m craft", "~m rowsFor", "~m step", "~m takeBag", "~m why"],   # drop-up step 'd' + the texts
    "AccDefs": ["~m retiredChat"],
    "AccEffects": ["+f F_POWER", "+m manaMod2", "+m modSigned", "~<clinit>", "~m tick"],
    "AccGear": ["+m textOf2"],
    "AccGiveCmd": ["~c ", "~m execute"], "AccGiveTierCmd": ["~c ", "~m execute"], "AccLinesCmd": ["~m execute"], "AccReloadCmd": ["~m execute"],
    "AccNotice": ["~m check"], "AccStore": ["~m campCheck"],               # the texts only
    "AccPage": ["+f bagIds", "+f cells", "+f filt", "+f sel", "+m apTag", "+m bagOrder", "+m buildBag", "+m buildPower", "+m cell", "+m clearGrid",
                "+m effects", "+m filtOf", "+m has", "+m jsonInt", "+m jsonStr", "+m rarer", "+m selMode", "+m tip", "~c ", "~m build", "~m buildCraft",
                "~m giveBack", "~m handleDataEvent", "~m infoColor"],
    "AccStarter": ["+f LOGF", "+f STUCK", "+f STUCK_MS", "+m journal", "+m removeIn", "+m where", "~<clinit>", "~m dispatch", "~m gate", "~m markerOf",
                   "~m prune", "~m stepK", "~m writeMarker"],
    "AccTick": ["~m run"],
    "CfgFile": ["~<clinit>", "~m init"], "CfgFn": ["~m opExport"], "CfgRows": ["+f DL2", "~<clinit>", "~m defLines", "~m header"],   # + power.properties
    "SkyyAccessoriesPlugin": ["~m setup", "~m shutdown"],
    "WbTab": ["~m start"],                                                   # the shared tab text 'Bags' (tools/skyywbtab.py TAB_TEXT)
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
# the Power table (= tools/accessories_0_5_22_patch.py PW_TABLE): the Python twin the Java is compared with
_PT = open(os.path.join(ROOT, "tools", "accessories_0_5_22_patch.py"), encoding="utf8").read()
PW_TABLE = eval(_PT[_PT.index("PW_TABLE = [") + len("PW_TABLE = "):_PT.index("]\nPW_GROUPS")] + "]")
PW_E = [(_i, _k, _v) for _i, _p in enumerate(PW_TABLE) for _k, _v in _p[3]]


def kind(k):
    if k in ("hp", "def", "str", "mp", "mana", "cc", "cd") or (k.startswith("dd.") and not k.endswith(".fishing")):
        return "whole"
    return "dec"


def twin(v, m, k):
    x = v * m
    return float(round(x)) if kind(k) == "whole" else round(x * 10.0) / 10.0


def jround(x):
    """Java Math.round (half up) - Python round() is half-even"""
    import math
    return math.floor(x + 0.5)


def twinj(v, m, k):
    x = v * m
    return float(jround(x)) if kind(k) == "whole" else jround(x * 10.0) / 10.0


def mult(ap, base=100, curve=0.6, guard=20.0):
    return 0.0 if ap <= 0 else min(guard, (float(ap) / base) ** curve)


def m18():
    """the 0.5.18 harness module (its World stand-in) on THIS jar; its HK.Child override is undone"""
    keep = HK.Child
    sp = importlib.util.spec_from_file_location("acc_h518", os.path.join(HERE, "test_skyyaccessories_0.5.18.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    HK.Child = keep
    m.JAR = JAR
    return m


# ======================================================================================== S: the asset files
def run_assets(out, jar, scratch, _home):
    K = HK.Child(out)
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    ea = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    eb = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    added = sorted(set(eb) - set(ea))
    K.check(len(added) == 59 and all(n.startswith("Common/UI/Custom/SkyyKit/") for n in added), "S: the 59 kit art files added (%d)" % len(added))
    K.eq(sorted(set(ea) - set(eb)), [], "S: no non-class file removed")
    K.eq(int(SUI.check_jar_kit(jar, need=("Header", "Tab", "Close", "Frame_Character"))), 59, "S: the jar's kit art is the kit's (sha256)")
    changed = sorted(n for n in ea if ea[n] != eb.get(n))
    items = sorted(n for n in changed if n.startswith("Server/Item/Items/"))
    want = sorted(["Server/Item/Items/Utility/Skyy_Talisman_%s_T%d.json" % (f, t) for f in DROP_UP for t in (2, 3, 4)] + ["Server/Item/Items/Utility/%s.json" % BAG])
    K.eq(items, want, "S: the 15 drop-up upgrade items + the bag item changed")
    for f in DROP_UP:
        a1 = json.loads(eb["Server/Item/Items/Utility/Skyy_Talisman_%s_T1.json" % f])
        K.check("Recipe" not in a1, "S: %s Normal: no recipe (it drops)" % f)
        for t in (2, 3, 4):
            n = "Server/Item/Items/Utility/Skyy_Talisman_%s_T%d.json" % (f, t)
            a, b = json.loads(ea[n]), json.loads(eb[n])
            r = b.get("Recipe") or {}
            ins = r.get("Input") or []
            K.check("Recipe" not in a and r.get("BenchRequirement") == BAG_REQ and ins and ins[0] == {"ItemId": "Skyy_Talisman_%s_T%d" % (f, t - 1), "Quantity": 1}
                    and len(ins) >= 2 and all(x.get("ItemId", "").startswith(("Ingredient_", "Rock_")) for x in ins[1:]),
                    "S: %s T%d: an upgrade from T%d + %d materials in the bag's category" % (f, t, t - 1, len(ins) - 1))
            del b["Recipe"]
            K.check(a == b, "S: %s T%d: nothing else changed" % (f, t))
    bo, bn = json.loads(ea["Server/Item/Items/Utility/%s.json" % BAG]), json.loads(eb["Server/Item/Items/Utility/%s.json" % BAG])
    K.check(bn.get("Variant") is True and "Categories" not in bn and "Recipe" not in bn and "Categories" in bo, "S: the bag item: hidden (Variant, no Categories), no recipe")
    K.check(bn.get("Interactions") == bo.get("Interactions"), "S: the bag item still opens the page (a stray copy in a chest)")
    lt = eb["Server/Languages/en-US/server.lang"].decode("utf-8")
    lm = dict(l.split("=", 1) for l in lt.splitlines() if "=" in l)
    K.check("/accessories" not in lt and "/accbag" not in lt and "/acc " not in lt, "S: no text names /accessories, /acc or /accbag")
    K.check([k for k, v in lm.items() if "Accessory Bag" in v] == ["items.%s.name" % BAG, "server.items.%s.name" % BAG] and lm["items.%s.name" % BAG] == "Old Accessory Bag",
            "S: 'Accessory Bag' only in the old item's name (Old Accessory Bag)")
    K.check("Void Charms" in lm["items.%s.description" % BAG] and "/charms" in lm["items.%s.description" % BAG], "S: the old item says where the accessories went")
    K.eq((lm.get("benchCategories.workbench.skyyaccessories"), lm.get("server.benchCategories.workbench.skyyaccessories")), ("Bags", "Bags"),
         "S: the shared Workbench tab reads Bags (tools/skyywbtab.py TAB_TEXT; this mod is its only writer)")
    for f in DROP_UP:
        d = lm["items.Skyy_Talisman_%s_T1.description" % f]
        K.check("drop only - upgrade it in the Craft tab of Void Charms" in d, "S: %s Normal's tooltip: where the upgrade is made" % f)
    langs = [n for n in changed if n.endswith(".lang")]
    K.eq(langs, ["Server/Languages/en-US/server.lang"], "S: server.lang changed")
    cc = zn.read("com/skyy/accessories/AccCmd.class")
    lits = set(x.decode("latin-1") for x in re.findall(rb"\x01\x00[\x01-\x40]([ -~]{1,64})", cc))
    K.check({"charms", "charm", "ch"} <= lits and not {"accessories", "acc", "accbag"} & lits, "S: /charms with the aliases /charm /ch; no /accessories, /acc, /accbag (HANDOFF section 3 rule 3)")
    K.check(not any(n.startswith("com/skyy/accessories/AccOnce") for n in zn.namelist()), "S: the lifelong bag classes (AccOnce*) are gone")
    rest = [n for n in changed if n not in items and n not in langs and n != "manifest.json"]
    K.eq(rest, [], "S: no other file changed")
    K.save()


# ======================================================================================== P: Accessory Power
def run_power(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JObject, JImplements, JOverride, JDouble
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Pw, Defs, Gear, Acc = (JClass(PKG + n) for n in ("AccPower", "AccDefs", "AccGear", "AccStore"))
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    home = os.path.join(scratch, "p")
    os.makedirs(os.path.join(home, "power"), exist_ok=True)
    Pw.FILE = Paths.get(os.path.join(home, "power.properties"))
    Pw.DIR = Paths.get(os.path.join(home, "power"))
    S = lambda *ids: JArray(JString)([JString(i) if i is not None else None for i in ids])
    ap = lambda *ids: int(Pw.apOf(S(*ids)))
    # ===== P8 first: a missing file is written once with the built-in text
    r0 = str(Pw.load())
    t0 = open(os.path.join(home, "power.properties"), encoding="utf8").read()
    K.check(t0 == str(Pw.DEFAULT_TEXT) and "power.ap=10,13,16,19,22,25" in t0 and "pw.Slayer.str=7" in t0 and "pw.Jackpot.cc=9" in t0,
            "P8 a missing power.properties is written once with the built-in lines: " + r0[:80])
    Pw.load()
    K.check(open(os.path.join(home, "power.properties"), encoding="utf8").read() == t0, "P8 ... a second load changes nothing")
    # ===== P1 the AP sum
    K.eq(ap(), 0, "P1 an empty bag: 0 AP")
    K.eq(ap("Skyy_Talisman_Vitality_Common"), 10, "P1 one Normal: 10")
    K.eq(ap("Skyy_Talisman_Vitality_Common", "Skyy_Talisman_Vitality_Uncommon"), 13, "P1 a lower copy of the same line adds 0 (Unique 13 counts)")
    K.eq(ap("Skyy_Talisman_Vitality_Uncommon", "Skyy_Talisman_Vitality_Uncommon"), 13, "P1 a duplicate adds 0")
    K.eq(ap("Skyy_Talisman_Vitality_Common", "Skyy_Talisman_Speed_Rare", "Skyy_Talisman_Lantern_Epic"), 10 + 16 + 19, "P1 three lines: 10 + 16 + 19 (Lantern Legendary)")
    K.eq(ap("Skyy_Talisman_Vitality_Ring"), 16, "P1 a legacy id counts as its rarity (Ring = Rare 16)")
    K.eq(ap("Skyy_Talisman_Strength_T4"), 19, "P1 a part 2 line (Brawler Legendary): 19")
    K.eq(ap("Skyy_Accessory_Workbench_T1"), 10, "P1 a bench accessory I: Normal 10")
    K.eq(ap("Skyy_Accessory_Workbench_T3", "Skyy_Accessory_Workbench_T1"), 16, "P1 bench III = Rare 16, the lower one adds 0")
    K.eq(ap("Skyy_Accessory_Farmingbench_T4"), 19, "P1 bench IV = Legendary 19")
    K.eq(ap(OMNI), 143, "P1 the Omni = the 11 active top-tier bench accessories (143)")
    K.eq(int(Pw.omniAp()), 143, "P1 omniAp = 143")
    K.eq(ap(OMNI, "Skyy_Accessory_Workbench_T3", "Skyy_Accessory_Campfire_T1"), 143, "P1 bench accessories next to the Omni add 0")
    K.eq(ap(OMNI, "Skyy_Talisman_Speed_Common"), 153, "P1 the Omni + a stat line: 143 + 10")
    K.eq(ap("Skyy_Accessory_Alchemybench_T1", "Skyy_Talisman_NightVision_Rare"), 0, "P1 retired accessories add 0")
    K.eq(ap(BAG), 0, "P1 the old bag item adds 0")
    K.eq(ap("Skyy_Talisman_Unknown_T1"), 0, "P1 an unknown line adds 0")
    Defs.LINE_HEALTH = False
    K.eq(ap("Skyy_Talisman_Vitality_Epic", "Skyy_Talisman_Speed_Common"), 10, "P1 a switched-off line adds 0")
    Defs.LINE_HEALTH = True
    Defs.LINE_LANTERN = False
    K.eq(ap("Skyy_Talisman_Lantern_Epic"), 0, "P1 the Lantern switched off adds 0")
    Defs.LINE_LANTERN = True
    Pw.BENCH = "half"
    K.eq((ap("Skyy_Accessory_Workbench_T3"), ap(OMNI)), (8, sum(x // 2 for x in [16, 16, 16, 19, 13, 13, 10, 10, 10, 10, 10])), "P1 benches half: III 8, the Omni half of each")
    Pw.BENCH = "none"
    K.eq((ap("Skyy_Accessory_Workbench_T3", "Skyy_Talisman_Speed_Common"), ap(OMNI)), (10, 0), "P1 benches none: 0 (the stat line still counts)")
    Pw.BENCH = "full"
    s1 = S("Skyy_Talisman_Vitality_Common", "Skyy_Talisman_Vitality_Rare", OMNI, "Skyy_Accessory_Workbench_T2", "Skyy_Accessory_Alchemybench_T1")
    K.eq([int(Pw.apOne(s1, x)) for x in ("Skyy_Talisman_Vitality_Common", "Skyy_Talisman_Vitality_Rare", OMNI, "Skyy_Accessory_Workbench_T2", "Skyy_Accessory_Alchemybench_T1")],
         [-1, 16, 143, -2, -4], "P1 apOne (the hover): lower copy -1, the best 16, the Omni 143, a bench the Omni covers -2, retired -4")
    K.eq([int(Pw.apIf(x)) for x in ("Skyy_Talisman_Speed_Epic", "Skyy_Accessory_Workbench_T1", OMNI)], [19, 10, 143], "P1 apIf (an inventory accessory on its own)")
    # ===== P2 the multiplier
    K.check(float(Pw.mult(0)) == 0.0 and all(abs(float(Pw.mult(a)) - mult(a)) < 1e-9 for a in (60, 250, 350, 1200)), "P2 M = (AP / 100) ^ 0.6, 0 at 0 AP")
    K.eq([str(Pw.multText(Pw.mult(a))) for a in (60, 350, 1200)], ["0.74", "2.12", "4.44"], "P2 x0.74 at 60, x2.12 at 350, x4.44 at 1,200 (spec 2)")
    K.check(abs(float(Pw.mult(10 ** 6)) - 20.0) < 1e-9, "P2 the guard: at most x20")
    # ===== P3 every Power stat at three AP levels = the Python twin
    bad = []
    for a in (60, 350, 1200):
        m = mult(a)
        for e, (i, k, v) in enumerate(PW_E):
            got = float(Pw.valueAt(e, Pw.mult(a)))
            if abs(got - twinj(v, m, k)) > 1e-9:
                bad.append((a, PW_TABLE[i][0], k, got, twinj(v, m, k)))
    K.eq(bad, [], "P3 all %d Power stats x 3 AP levels (60 / 350 / 1,200) = the twin (whole points / Fortune, else 1 decimal)" % len(PW_E))
    K.eq(len(list(Pw.PW_ID)), 15, "P3 15 Powers")
    K.eq([str(x) for x in Pw.PW_NAME], [p[1] for p in PW_TABLE], "P3 the names (Glass Cannon, Jackpot = the combat Fortune renamed)")
    K.eq(str(Pw.statText(2, Pw.mult(350))), "+4 HP, +2 Def, +15 Str, +21% Crit Dmg", "P3 Slayer at 350 AP (spec 2.3)")
    K.eq(str(Pw.statText(0, Pw.mult(60))), "+9 HP, +4 Def", "P3 Tank at 60 AP (spec 2.3)")
    K.eq(str(Pw.statText(7, Pw.mult(350))), "-8 HP, -4 Def, +25 Str, +6% Crit, +34% Crit Dmg", "P3 Glass Cannon at 350 AP: the debuffs signed")
    K.check(str(Pw.statText(1, 0.0)).startswith("nothing yet"), "P3 at 0 AP: nothing yet")
    # ===== P5 visibility + the Combat 15 lock (no SkyySkills yet)
    u1 = UUID.fromString("00000000-0000-0000-0000-00000000ac01")
    vis = [str(Pw.PW_ID[i]) for i in range(15) if bool(Pw.visible(i))]
    K.eq(vis, [p[0] for p in PW_TABLE if p[2] != 2], "P5 without SkyySkills / readers: the 11 combat Powers only (gathering stats have no reader)")
    K.check(str(Pw.lockOf(u1, 5)).startswith("needs SkyySkills"), "P5 a Combat 15 Power without SkyySkills: locked (%s)" % Pw.lockOf(u1, 5))
    LV = {"v": 14}

    @JImplements("java.util.function.Function")
    class LvFn(object):
        @JOverride
        def apply(self, a):
            return JObject(LV["v"], "java.lang.Integer")
    lvfn = LvFn()
    br.put("skill:fn:level", lvfn)
    Pw.LV.clear()
    K.check(str(Pw.lockOf(u1, 7)) == "unlocks at Combat 15 (you are Combat 14)" and Pw.lockOf(u1, 0) is None, "P5 Combat 14: Glass Cannon locked, Tank free")
    LV["v"] = 15
    Pw.LV.clear()
    K.check(Pw.lockOf(u1, 7) is None, "P5 Combat 15: unlocked")
    vis2 = [str(Pw.PW_ID[i]) for i in range(15) if bool(Pw.visible(i))]
    K.eq(vis2, [p[0] for p in PW_TABLE if p[0] != "Fishing"], "P5 SkyySkills running: Mining / Foraging / Farming (Fortune) show; Fishing waits for its reader")
    # ===== P4 the pick
    k1 = str(u1)
    K.eq(int(Pw.effIndex(u1, k1)), 1, "P4 no file: Balance (power.start)")
    now = 1000000
    r = str(Pw.pick(u1, k1, "slayer", now, True))
    K.eq(r, "Power is now Slayer - your stats follow within a second", "P4 pick Slayer (free)")
    pf = os.path.join(home, "power", k1 + ".properties")
    K.check(os.path.exists(pf) and "power=Slayer" in open(pf).read() and ("switched=%d" % now) in open(pf).read(), "P4 ... power/<pkey>.properties power=Slayer switched=<ms>")
    K.eq(str(Pw.pick(u1, k1, "Tank", now + 1000, True)), "wait 4 s before you switch your Power again", "P4 a second switch 1 s later: wait 4 s")
    K.eq(str(Pw.pick(u1, k1, "Slayer", now + 2000, True)), "Slayer is already your Power", "P4 the same Power: already")
    K.eq(str(Pw.pick(u1, k1, "Glass Cannon", now + 5000, True)), "Power is now Glass Cannon - your stats follow within a second", "P4 5 s later: switched (by its display name)")
    K.check(str(Pw.pick(u1, k1, "Fortune", now + 20000, True)).startswith("there is no Power called Fortune here"), "P4 'Fortune' is not a Power (Jackpot)")
    K.check(str(Pw.pick(u1, k1, "Fishing", now + 20000, True)).startswith("there is no Power called Fishing here"), "P4 a hidden Power (Fishing, no reader) cannot be picked")
    br.put("profile:busy:" + k1, JObject(True, "java.lang.Boolean"))
    t1 = open(pf).read()
    K.check(str(Pw.pick(u1, k1, "Tank", now + 30000, True)).startswith("your profile is still loading") and open(pf).read() == t1, "P4 profile:busy: refused, the file untouched")
    br.remove("profile:busy:" + k1)
    Pw.PICK.clear()
    K.eq(int(Pw.effIndex(u1, k1)), 7, "P4 after a restart (cache cleared) the file answers: Glass Cannon")
    LV["v"] = 3
    Pw.LV.clear()
    K.eq(int(Pw.effIndex(u1, k1)), 1, "P5 Combat drops below 15 (a rebirth): Glass Cannon is locked -> Balance works (the pick stays saved)")
    LV["v"] = 20
    Pw.LV.clear()
    Pw.ON_GLASSCANNON = False
    K.eq(int(Pw.effIndex(u1, k1)), 1, "P5 an admin hides Glass Cannon: Balance")
    Pw.ON_GLASSCANNON = True
    K.eq(str(Pw.pick(u1, k1, "Tank", now + 10 ** 7, False)), "Power is now Tank - your stats follow within a second", "P4 wait=false (a loadout): no wait")
    # ===== P6 the doors
    u2 = UUID.fromString("00000000-0000-0000-0000-00000000ac02")
    k2 = str(u2)
    Pw.pick(u2, k2, "Mining", now, False)
    bag = S("Skyy_Talisman_Lantern_Epic", OMNI, "Skyy_Talisman_Speed_Epic", "Skyy_Talisman_Vitality_Epic", "Skyy_Talisman_Crit_T4",
            "Skyy_Talisman_Strength_T2", "Skyy_Talisman_Defense_T1")   # 19 + 143 + 19 + 19 + 19 + 13 + 10 = 242
    K.eq(int(Pw.apOf(bag)), 242, "P6 a late-ish bag: 242 AP")
    c = [float(x) for x in Pw.tick(u2, bag)]
    sb = br.get("skill:bonus:" + k2)
    m242 = mult(242)
    K.check(str(br.get("acc:power:" + k2)) == "Mining|242", "P6 acc:power = Mining|242 (%s)" % br.get("acc:power:" + k2))
    K.check(sb is not None and dict((str(kk), float(vv)) for kk, vv in dict(sb.get("accessories")).items()) == {"dd.mining": twinj(6, m242, "dd.mining") / 100.0},
            "P6 skill:bonus source accessories = Fortune only (dd.mining = %s / 100; bp / swing have no reader yet): %s" % (twinj(6, m242, "dd.mining"), sb and sb.get("accessories")))
    K.check(c == [0.0] * 8, "P6 a gathering Power: no combat sums")
    br.put("skill:bonus:reads:bp", JObject(True, "java.lang.Boolean"))
    br.put("skill:bonus:reads:swing", JObject(True, "java.lang.Boolean"))
    Pw.tick(u2, bag)
    got = dict((str(kk), float(vv)) for kk, vv in dict(br.get("skill:bonus:" + k2).get("accessories")).items())
    K.eq(sorted(got), ["bp.mining", "dd.mining", "swing.mining"], "P6 with the bp / swing readers: all three Mining stats")
    K.check(abs(got["bp.mining"] - twinj(14, m242, "bp.mining") / 100.0) < 1e-9, "P6 bp.mining = %s %% / 100" % twinj(14, m242, "bp.mining"))
    vv0 = br.get("skill:bonus:" + k2).get("accessories")
    Pw.tick(u2, bag)
    K.check(br.get("skill:bonus:" + k2).get("accessories") is vv0 or br.get("skill:bonus:" + k2).get("accessories").equals(vv0), "P6 unchanged: not replaced")
    br.put("skill:bonus:reads:fish", JObject(True, "java.lang.Boolean"))
    K.check(bool(Pw.visible(14)), "P6 the fish reader: Fishing shows")
    other = JClass("java.util.HashMap")()
    other.put("dd.mining", JObject(0.25, "java.lang.Double"))
    br.get("skill:bonus:" + k2).put("gear", other)
    br.put("profile:busy:" + k2, JObject(True, "java.lang.Boolean"))
    cb = Pw.tick(u2, bag)
    K.check(br.get("skill:bonus:" + k2).get("accessories") is None and br.get("skill:bonus:" + k2).get("gear") is not None and cb is None,
            "P6 profile:busy: our source removed (another source stays), null = AccEffects writes no stat this second")
    br.remove("profile:busy:" + k2)
    Pw.pick(u2, k2, "GlassCannon", now + 10 ** 7, False)
    c = [float(x) for x in Pw.tick(u2, bag)]
    K.eq(c, [twinj(v, m242, k) if k in [kk for kk, _ in PW_TABLE[7][3]] else 0.0 for k, v in [(kk, dict(PW_TABLE[7][3]).get(kk, 0)) for kk in ("hp", "def", "str", "cc", "cd", "mp", "mana", "spd")]],
         "P6 Glass Cannon: the combat sums (hp, def, str, cc, cd, mp, mana, spd) for AccEffects")
    K.check(br.get("skill:bonus:" + k2).get("accessories") is None, "P6 a combat Power: the gathering source goes")
    K.eq(str(br.get("acc:power:" + k2)), "GlassCannon|242", "P6 acc:power follows")
    # ===== P7 the gear:extra text
    best = Defs.activeTiers(bag)
    K.eq(str(Gear.textOf(best)), "cc:8,cd:16,def:3,str:6", "P7 the lines alone (0.5.21's text)")
    g = str(Gear.textOf2(best, JArray(JDouble)(c)))
    want = {"cc": 8 + int(c[3]), "cd": 16 + int(c[4]), "def": 3 + int(c[1]), "str": 6 + int(c[2])}
    K.eq(g, ",".join("%s:%d" % (k_, v_) for k_, v_ in sorted(want.items()) if v_ != 0), "P7 lines + Glass Cannon, signed: " + g)
    K.eq(str(Gear.textOf2(Defs.activeTiers(S()), JArray(JDouble)([0.0, -4.0, -2.0, 0, 0, 0, 0, 0]))), "def:-4,str:-2", "P7 a debuff alone goes out below 0")
    K.eq(str(Gear.textOf2(Defs.activeTiers(S()), JArray(JDouble)([0.0, -400.0, 0, 0, 0, 0, 0, 0]))), "def:-50", "P7 a debuff never goes below -50 (Defense stays above -100 in SkyyGear's formula)")
    Defs.COMBAT_TO_GEAR = False
    K.eq(str(Gear.textOf2(best, JArray(JDouble)(c))), ",".join("%s:%d" % (k_, int(c[i_])) for i_, k_ in sorted([(3, "cc"), (4, "cd"), (1, "def"), (2, "str")], key=lambda x: x[1]) if int(c[i_]) != 0),
         "P7 combatToGear off: only the Power")
    Defs.COMBAT_TO_GEAR = True
    # leave
    on = JClass("java.util.HashSet")()
    Pw.pick(u2, k2, "Mining", now + 2 * 10 ** 7, False)
    Pw.tick(u2, bag)
    K.check(br.get("skill:bonus:" + k2).get("accessories") is not None, "P6 (Mining again: the source is back)")
    Pw.prune(on)
    K.check(br.get("skill:bonus:" + k2).get("accessories") is None and br.get("acc:power:" + k2) is None and br.get("skill:bonus:" + k2).get("gear") is not None,
            "P6 the player left: our source and acc:power removed, another mod's source stays")
    # ===== P8 the settings file + hooks
    open(os.path.join(home, "power.properties"), "w", encoding="utf8").write(
        t0.replace("pw.Tank.hp=12", "pw.Tank.hp=20").replace("power.show.Lucky=true", "power.show.Lucky=false").replace("power.ap=10,13,16,19,22,25", "power.ap=1,2,3")
        .replace("power.wait=5", "power.wait=99999").replace("power.start=Balance", "power.start=GlassCannon"))
    r8 = str(Pw.load())
    K.check(float(Pw.E_VAL[0]) == 20.0 and not bool(Pw.visible(3)) and list(Pw.AP)[1:] == [10, 13, 16, 19, 22, 25] and int(Pw.WAIT) == 3600 and str(Pw.START) == "Balance",
            "P8 custom Tank.hp 20, Lucky hidden, a bad power.ap -> the built-in one, wait clamped to 3600, a Combat 15 start -> Balance: " + r8[:160])
    K.check(Pw.checkAp("power.ap", "10,13,16,19,22,25") is None and "six whole numbers" in str(Pw.checkAp("power.ap", "1,2")), "P8 checkAp")
    K.check(Pw.checkStat("pw[Tank.hp]", "-5") is None and "-100 to 100" in str(Pw.checkStat("pw[Tank.hp]", "500")) and "Unknown entry" in str(Pw.checkStat("pw[Tank.zz]", "1"))
            and "stays" in str(Pw.checkStat("pw[Tank.hp]", None)), "P8 checkStat (the pw table's hook)")
    open(os.path.join(home, "power.properties"), "w", encoding="utf8").write(t0)
    Pw.load()
    # ===== P9 acc:fn:power
    Fn = JClass(PKG + "AccPowerFn")()
    u3 = UUID.fromString("00000000-0000-0000-0000-00000000ac03")
    K.eq(str(Fn.apply(JArray(JObject)([JString("get"), u3]))), "Balance", "P9 get: Balance")
    K.eq(str(Fn.apply(JArray(JObject)([JString("set"), u3, JString("Lucky")]))), "Power is now Lucky - your stats follow within a second", "P9 set Lucky")
    K.eq(str(Fn.apply(JArray(JObject)([JString("set"), u3, JString("Tank")]))), "Power is now Tank - your stats follow within a second", "P9 set again at once (a loadout: no wait)")
    K.check(Fn.apply(JString("x")) is None and Fn.apply(JArray(JObject)([JString("nope"), u3])) is None, "P9 bad arguments: null")
    K.check(bool(JClass(PKG + "AccPowerFn")(1).apply(JArray(JObject)([u3, JString(str(u3))]))), "P9 once:item:Skyy_Accessory_Bag (mode 1): TRUE - the retired item never goes into a starter kit")
    K.check(bool(Pw.dropUp("T:Strength")) and not bool(Pw.dropUp("T:Speed")) and not bool(Pw.dropUp("Workbench")) and "upgrade it in Craft" in str(Pw.dropText("Skyy_Talisman_Crit_T2")),
            "P9 the drop-up lines")
    K.save()


# ======================================================================================== R: the bag item retirement
def run_retire(out, jar, scratch, _home):
    K = HK.Child(out)
    M = m18()
    W = M.World(os.path.join(scratch, "r"))
    from jpype import JClass, JShort
    for iid, st, lv in [(BAG, 1, 18), ("Skyy_Talisman_Speed_Common", 1, 4), ("Ingredient_Stick", 100, 0)]:
        W.item(iid, st, lv)
    St = W.J("AccStarter")
    Paths = W.Paths
    rdir = os.path.join(scratch, "r", "retired")
    logf = os.path.join(scratch, "r", "retired.log")
    St.DIR = Paths.get(rdir)
    St.LOGF = Paths.get(logf)
    St.DELAY_MS = 0
    inv = W.inv(put=[("s", 0, BAG, 1), ("h", 3, BAG, 1), ("s", 5, "Ingredient_Stick", 7)])
    p, pr, U = W.player(inv, "Ann")
    k = str(U)
    W.Acc.putK(U, k, 2, "Skyy_Talisman_Speed_Common")
    bf = os.path.join(scratch, "r", "bags", "%s.properties" % k)
    b0 = open(bf, "rb").read()
    c0 = W.chats()
    r = str(St.stepK(pr, p, U, k))
    lg = open(logf, encoding="utf8").read()
    K.check(r == "removed" and W.count(inv, BAG) == 0 and W.count(inv, "Ingredient_Stick") == 7, "R1 both copies removed (storage + hotbar), nothing else: %s" % r)
    K.check(lg.count(" REMOVE Ann ") == 1 and ": 2 x %s (storage 1, hotbar 1)" % BAG in lg and lg.count(" DONE Ann ") == 1 and ": 2 removed" in lg
            and lg.index(" REMOVE ") < lg.index(" DONE "), "R1 the journal: REMOVE (what, where) before DONE")
    K.eq(W.chats() - c0, 1, "R1 the one-time chat line")
    K.check(open(bf, "rb").read() == b0 and W.bag(U)[2] == "Skyy_Talisman_Speed_Common", "R1 the bag file (the accessories) untouched")
    r = str(St.stepK(pr, p, U, k))
    K.check(r == "none" and W.chats() - c0 == 1 and open(logf, encoding="utf8").read() == lg, "R2 again (the next 5 s pass / a relog): nothing, no second line, no journal line")
    # a crash before the player save: the copy comes back, the marker is not written yet (DUE pending), the run starts fresh
    assert inv.getStorage().setItemStackForSlot(JShort(0), W.IS(BAG, 1)).succeeded()
    St.DONE.clear()
    St.DUE.clear()
    r = str(St.stepK(pr, p, U, k))
    K.check(r == "removed" and W.count(inv, BAG) == 0 and open(logf, encoding="utf8").read().count(" REMOVE Ann ") == 2 and W.chats() - c0 == 2,
            "R3 a crash before the save: the copy that came back is removed again (journaled), the line again (no marker yet)")
    St.flush(True)
    mk = os.path.join(rdir, k + ".properties")
    K.check(os.path.exists(mk) and "retiredBag=removed-1" in open(mk).read(), "R4 the marker retired/<pkey>.properties is written")
    St.DONE.clear()
    assert inv.getBackpack().setItemStackForSlot(JShort(1), W.IS(BAG, 1)).succeeded()
    r = str(St.stepK(pr, p, U, k))
    K.check(r == "removed" and W.count(inv, BAG) == 0 and W.chats() - c0 == 2, "R4 after a restart a copy pulled out of a chest is removed, no chat (the marker)")
    K.check(open(bf, "rb").read() == b0, "R nothing in the bag file changed through all of it")
    # the gate: profile busy -> nothing
    assert inv.getStorage().setItemStackForSlot(JShort(0), W.IS(BAG, 1)).succeeded()
    W.bridge.put("profile:busy:" + k, W.JObject(True, "java.lang.Boolean"))
    K.eq(str(St.step(pr, p)), "blocked", "R5 profile:busy: nothing is touched")
    K.eq(W.count(inv, BAG), 1, "R5 ... the copy stays until the profile is loaded")
    W.bridge.remove("profile:busy:" + k)
    W.bridge.put("profile:" + k, W.JObject(1, "java.lang.Long"))   # SkyyProfiles' profile:<uuid> (the gate asks for it when profile:fn:key exists)
    K.eq(str(St.step(pr, p)), "removed", "R5 loaded: removed")
    # a copy that would not go (marked stuck): quiet for a minute - no journal line, no log - then tried again
    assert inv.getStorage().setItemStackForSlot(JShort(0), W.IS(BAG, 1)).succeeded()
    lg = open(logf, encoding="utf8").read()
    import time as _t
    St.STUCK.put(k, W.JClass("java.lang.Long")(int(_t.time() * 1000)))
    rq = [str(St.stepK(pr, p, U, k)) for _ in range(5)]
    K.check(rq == ["stuck-quiet"] * 5 and open(logf, encoding="utf8").read() == lg and W.count(inv, BAG) == 1,
            "R6 a stuck copy: 5 passes inside the minute write no journal line and touch nothing")
    St.STUCK.put(k, W.JClass("java.lang.Long")(int(_t.time() * 1000) - 61000))
    K.check(str(St.stepK(pr, p, U, k)) == "removed" and W.count(inv, BAG) == 0 and k not in [str(x) for x in St.STUCK.keySet()],
            "R6 a minute later it is tried again (removed, the mark cleared)")
    K.save()


# ======================================================================================== K: craft rows of the drop-only lines
def recipe(W, out, ins, know=False):
    arr = W.JArray(W.MQ)(len(ins))
    for i, (a, q) in enumerate(ins):
        arr[i] = W.mq(a, None, q)
    po = W.mq(out, None, 1)
    outs = W.JArray(W.MQ)(1)
    outs[0] = po
    cats = W.JArray(W.JClass("java.lang.String"))(1)
    cats[0] = BAGCAT
    br = W.JArray(W.BRQ)(1)
    br[0] = W.BRQ(W.BT.Crafting, BAGCAT, cats, 0, W.JArray(W.JClass("java.lang.String"))(0))
    r = W.CRR(arr, po, outs, 1, br, 0.0, bool(know), 0)
    rid = out + "_Recipe_Generated_0"
    W.jfield(W.CRR, "id").set(r, rid)
    W.rmap.put(rid, r)
    return rid


def run_rows(out, jar, scratch, _home):
    K = HK.Child(out)
    M = m18()
    W = M.World(os.path.join(scratch, "k"))
    C = W.Craft
    from jpype import JShort
    for iid, st, lv in [("Skyy_Talisman_Strength_T1", 1, 30), ("Skyy_Talisman_Strength_T2", 1, 31), ("Skyy_Talisman_Strength_T3", 1, 32),
                        ("Skyy_Talisman_Speed_Common", 1, 4), ("Skyy_Accessory_Workbench_T1", 1, 1), ("Skyy_Accessory_Workbench_T2", 1, 20),
                        ("Ingredient_Bone_Fragment", 100, 0), ("Ingredient_Bar_Copper", 100, 0), ("Ingredient_Bar_Iron", 100, 0), ("Bench_WorkBench", 100, 0)]:
        W.item(iid, st, lv)
    ids = {"s2": recipe(W, "Skyy_Talisman_Strength_T2", [("Skyy_Talisman_Strength_T1", 1), ("Ingredient_Bone_Fragment", 10), ("Ingredient_Bar_Copper", 4)]),
           "s3": recipe(W, "Skyy_Talisman_Strength_T3", [("Skyy_Talisman_Strength_T2", 1), ("Ingredient_Bar_Iron", 10)]),
           "spd": recipe(W, "Skyy_Talisman_Speed_Common", [("Ingredient_Bar_Copper", 2)]),
           "wb1": recipe(W, "Skyy_Accessory_Workbench_T1", [("Bench_WorkBench", 1), ("Ingredient_Bar_Copper", 4)]),
           "wb2": recipe(W, "Skyy_Accessory_Workbench_T2", [("Skyy_Accessory_Workbench_T1", 1), ("Ingredient_Bar_Copper", 3)])}
    VOID = {"n": {}, "owe": {}, "paused": False, "short": 0, "calls": []}
    _keep = M.void_bridge(W, VOID)

    def view(u, sub, p):
        rows = []
        for e in C.rowsFor(u, str(u), p, sub):
            ri = [str(x) for x in C.lineRow(u, str(u), p, e)]
            rid = C.ridOf(e)
            rows.append((ri[0], ri[6], ri[2], None if rid is None else str(rid)))
        return rows

    def craft(p, pr, u, rid):
        return str(C.craft(pr, None, None, p, u, str(u), rid))

    inv = W.inv(put=[("s", 0, "Skyy_Talisman_Strength_T1", 1), ("s", 1, "Ingredient_Bone_Fragment", 20), ("s", 2, "Ingredient_Bar_Copper", 20)])
    p, pr, U = W.player(inv, "Kit")
    v = view(U, 1, p)
    K.check(not any(r[0].startswith("Skyy_Talisman_Strength_") for r in v) and any(r[0] == "Skyy_Talisman_Speed_Common" and r[1] == "c" for r in v),
            "K1 Brawler with none in the bag: no row (a Normal in the INVENTORY does not count), Speed still has its craft row: %s" % v)
    K.check(not any(str(C.outId(r_)) == "Skyy_Talisman_Strength_T1" for r_ in C.recipes()), "K1 the Normal has no recipe (it drops)")
    s0, b0 = W.slots(inv), W.bag(U)
    r = craft(p, pr, U, ids["s2"])
    K.check(r == "that row changed - the list is up to date now, nothing was used" and W.slots(inv) == s0 and W.bag(U) == b0,
            "K1 a forged / stale click on the Unique recipe with none in the bag: nothing used (never from scratch): " + r)
    W.Acc.putK(U, str(U), 4, "Skyy_Talisman_Strength_T1")
    v = [x for x in view(U, 1, p) if x[0].startswith("Skyy_Talisman_Strength_")]
    K.check(v == [("Skyy_Talisman_Strength_T2", "u", "UNIQUE - CAN UPGRADE", ids["s2"])], "K2 one in the bag: the Unique UPGRADE row: %s" % v)
    r = craft(p, pr, U, ids["s2"])
    K.check(r == "upgraded to Unique Brawler Accessory in your bag - your Normal Brawler Accessory was used for it", "K3 upgraded in place: " + r)
    K.check(W.bag(U)[4] == "Skyy_Talisman_Strength_T2" and W.count(inv, "Skyy_Talisman_Strength_T1") == 1 and W.count(inv, "Ingredient_Bone_Fragment") == 10
            and W.count(inv, "Ingredient_Bar_Copper") == 16, "K3 ... slot 4 holds the Unique, the inventory Normal untouched (bag first), the materials used once")
    s1, b1 = W.slots(inv), W.bag(U)
    r = craft(p, pr, U, ids["s2"])
    K.check(r == "that row changed - the list is up to date now, nothing was used" and W.slots(inv) == s1 and W.bag(U) == b1, "K3 a double click: nothing used: " + r)
    v = [x for x in view(U, 1, p) if x[0].startswith("Skyy_Talisman_Strength_")]
    K.check(v and v[0][0] == "Skyy_Talisman_Strength_T3" and v[0][1] == "u", "K3 the row moved on to the Rare: %s" % v)
    # a normal line still crafts from scratch (0.5.21)
    put = inv.getStorage().setItemStackForSlot(JShort(8), W.IS("Bench_WorkBench", 1))
    r = craft(p, pr, U, ids["wb1"])
    K.check(r == "crafted Workbench I - it went straight into your bag" and "Skyy_Accessory_Workbench_T1" in W.bag(U), "K4 a normal line: crafted into the bag: " + r)
    r = craft(p, pr, U, ids["wb2"])
    K.check(r.startswith("upgraded to Workbench II") and W.bag(U).count("Skyy_Accessory_Workbench_T2") == 1 and "Skyy_Accessory_Workbench_T1" not in W.bag(U), "K4 ... upgraded in place: " + r)
    jr = open(W.LOGF, encoding="utf8").read() if os.path.exists(W.LOGF) else ""
    K.check(jr.count("upgraded in place") == 2 and "LOST" not in jr, "K the journal: two in-place upgrades, nothing lost")
    K.save()


# ======================================================================================== M: the page on the real engine page manager
DECL_RE = re.compile(r"\b([A-Za-z]+) #([A-Za-z0-9]+) \{")


def unq(d):
    if d is None:
        return ""
    d = str(d)
    try:
        v = json.loads(d)
    except Exception:
        return d
    if isinstance(v, dict) and len(v) == 1:
        v = list(v.values())[0]
    return v if isinstance(v, str) else d


def menu_page(K, built, what):
    cmds, evs = built
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, unq(d)) for ty, s, t, d in cmds if ty == "Set"]
    try:
        SUI.check_page(apps, "Skyy")
        K.check(True, "%s: check_page (markup rules, parents, no duplicate id; %d appends)" % (what, len(apps)))
    except Exception as e:
        K.check(False, "%s: check_page: %s" % (what, e))
    try:
        SUI.check_sky_paths(apps, tab_icons=True)
        K.check(True, "%s: kit paths" % what)
    except Exception as e:
        K.check(False, "%s: sky paths: %s" % (what, e))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in DECL_RE.finditer(SUI.render(mk)))
    bs = [s for s, _t in evs]
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    try:
        info = SUI.assert_menu_page(apps, hub="character", what=what, sets=sets)
        K.check(info["rows"] == 2 and info["subs"] == 1, "%s: assert_menu_page (1600 x 980, rows %d, sub rows %d, no back button, no pager)" % (what, info["rows"], info["subs"]))
    except Exception as ex:
        K.check(False, "%s: assert_menu_page: %s" % (what, ex))
    return apps, dict(sets), evs


def run_page(out, jar, scratch, _home):
    from jpype import JClass, JShort
    import hub_tab_kit as HT
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    J = lambda n: JClass(PKG + n)
    Paths, UUID, IS = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    home = os.path.join(scratch, "m")
    os.makedirs(os.path.join(home, "bags"), exist_ok=True)
    J("AccStore").DIR = Paths.get(os.path.join(home, "bags"))
    J("AccPower").FILE = Paths.get(os.path.join(home, "power.properties"))
    J("AccPower").DIR = Paths.get(os.path.join(home, "power"))
    J("AccPower").load()
    J("AccCraft").LOGF = Paths.get(os.path.join(home, "crafts.log"))
    K.eq(str(J("AccHubOpen").register()), "character:accessories", "REG the Void Charms tab is registered")
    t = E.bridge.get("hub:tab:character:accessories")
    K.check(t is not None and str(t[0]) == "SkyyAccessories" and str(t[1]) == "Void Charms" and int(t[2]) == 60 and str(t[3]) == "charms",
            "REG hub:tab:character:accessories = {SkyyAccessories, Void Charms, 60, charms, open, null}")
    P1 = E.mkp(UUID.fromString("00000000-0000-0000-0000-0000000ac0f1"), "Charmer")
    u1 = P1.pr.getUuid()
    E.bridge.put("profile:epoch:%s" % u1, JClass("java.lang.Long")(1))
    K.check(bool(J("AccHubOpen")().apply(u1)), "REG the tab's open Function opens the page")
    E.pump(P1)
    pg = E.pg(P1)
    K.check(pg is not None and str(pg.getClass().getName()) == PKG + "AccPage", "REG ... the open page is Void Charms")
    Acc = J("AccStore")
    k1 = str(u1)
    Acc.putK(u1, k1, 0, "Skyy_Talisman_Speed_Epic")
    Acc.putK(u1, k1, 1, OMNI)
    Acc.putK(u1, k1, 2, "Skyy_Talisman_Speed_Common")
    P1.slots["storage"].getInventory().addItemStackToSlot(JShort(0), IS("Skyy_Talisman_Vitality_Rare", 1))
    _it = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item").getAssetMap().getAsset("Skyy_Talisman_Vitality_Rare")
    HT.jf(_it.getClass(), "maxStack").setInt(_it, 1)   # the stand-in item map's ONE item (every id): stack 1 like our accessories, so a give fits

    def click(a, extra=""):
        pg.handleDataEvent(P1.ref, P1.st, '{"a":"%s"%s}' % (a, extra))
        E.pump(P1)
        return str(pg.info)

    def subs(cmds):
        return [t_ for ty, s_, t_, d in cmds if t_ and "TextButton #SkyyAccSub" in t_]

    # BAG
    b0 = HT.build(pg, P1)
    _a, s0, e0 = menu_page(K, b0, "PAGE Bag")
    sel = [s for s, _t in e0]
    sb = subs(b0[0])
    K.check(len(sb) == 3 and "Primary" in sb[0] and 'Text: "Power"' in sb[2], "BAG the ONE sub-tab row: BAG (Primary) | CRAFT | POWER")
    K.check(all(("#SkyyAccSub%d" % i) in sel for i in range(3)) and "#SkyyAccClose" in sel and "#SkyyAccChg" in sel and "#SkyyAccGrid" in sel and "#SkyyAccInvG" in sel,
            "BAG bound: the sub-tabs, Close, Change Power, both grids")
    K.check(any(s_ == "#SkyyAccBigT%d" % i and "hub:accessories" in t_ for s_, t_ in e0 for i in range(8)), "BAG row 2 holds the Void Charms tab (hub:accessories)")
    gs = [d for ty, s_, t_, d in b0[0] if ty == "Set" and s_ == "#SkyyAccGrid.Slots"]
    K.check(len(gs) == 1 and int(pg.cells) == 100, "BAG the bag grid (60 cells) + the inventory grid (40) are filled (%s)" % pg.cells)
    K.check("Accessory Power %d - Power: Balance" % (143 + 19) == str(s0.get("#SkyyAccApL.Text")), "BAG the strip: %s" % s0.get("#SkyyAccApL.Text"))
    K.check(list(pg.bagIds)[:3] == [OMNI, "Skyy_Talisman_Speed_Epic", "Skyy_Talisman_Speed_Common"] or list(pg.bagIds)[:3] == ["Skyy_Talisman_Speed_Epic", OMNI, "Skyy_Talisman_Speed_Common"],
            "BAG rarest first: %s" % list(pg.bagIds))
    K.check("Nothing selected" in str(s0.get("#SkyyAccSelNone.Text")), "BAG nothing selected yet")
    # select the inventory accessory, Equip
    r = click("ig", ',"SlotIndex":0')
    K.check(r.startswith("selected Rare Health Accessory"), "SEL a click in the inventory grid selects: " + r)
    b1 = HT.build(pg, P1)
    _a, s1, e1 = menu_page(K, b1, "PAGE Bag (inventory selection)")
    K.check("#SkyyAccSelAct" in [s for s, _t in e1] and "Equip" in str([t_ for ty, s_, t_, d in b1[0] if t_ and "#SkyyAccSelAct" in t_]), "SEL the Equip button")
    r = click("eq")
    K.check(r == "equipped Rare Health Accessory" and "Skyy_Talisman_Vitality_Rare" in [str(x) for x in Acc.snapshot(u1)], "EQ equipped through the page: " + r)
    r = click("un")
    K.check(r == "unequipped Rare Health Accessory" and "Skyy_Talisman_Vitality_Rare" not in [str(x) for x in Acc.snapshot(u1)], "UN the selection follows it: unequipped again: " + r)
    r = click("fl:1")
    HT.build(pg, P1)
    K.check(int(pg.filt) == 1 and OMNI not in list(pg.bagIds) and "Skyy_Talisman_Speed_Epic" in list(pg.bagIds), "FILT Combat: the Omni (Benches) left out")
    click("fl:0")
    # CRAFT
    click("tb:craft")
    b2 = HT.build(pg, P1)
    _a, s2, e2 = menu_page(K, b2, "PAGE Craft")
    sb2 = subs(b2[0])
    K.check(int(pg.mode) == 1 and "Primary" in sb2[1] and "Primary" not in sb2[0] and all(("#SkyyAccSt%d" % i) in [s for s, _t in e2] for i in range(3)),
            "CRAFT the sub-tab CRAFT active, the Benches / Combat / Gathering filters bound")
    # POWER
    click("tb:power")
    b3 = HT.build(pg, P1)
    _a, s3, e3 = menu_page(K, b3, "PAGE Power")
    acts = sorted(s for s, _t in e3 if s.startswith("#SkyyAccPw") and s.endswith("Act"))
    K.check(int(pg.mode) == 2 and acts == ["#SkyyAccPw%dAct" % i for i in (0, 2, 3, 4)], "POWER Pick bound for the free starter Powers (Balance picked; Combat 15 locked; no gathering reader): %s" % acts)
    K.check(str(s3.get("#SkyyAccPw1Nm.Text")) == "Balance - PICKED" and str(s3.get("#SkyyAccPw7Nm.Text")) == "Glass Cannon - Combat 15", "POWER Balance PICKED, Glass Cannon locked (Combat 15)")
    r = click("pw:2")
    K.eq(r, "Power is now Slayer - your stats follow within a second", "POWER Pick Slayer")
    r = click("pw:0")
    K.check(r.startswith("wait ") and r.endswith(" s before you switch your Power again"), "POWER a second Pick at once: the 5 s wait: " + r)
    b4 = HT.build(pg, P1)
    _a, s4, _e4 = menu_page(K, b4, "PAGE Power (Slayer)")
    K.check(str(s4.get("#SkyyAccPw2Nm.Text")) == "Slayer - PICKED" and "You can switch again in" in str(s4.get("#SkyyAccPsR.Text")), "POWER Slayer PICKED + the wait shown")
    # the hub row: our own tab = back to the BAG view; Close closes
    click("hub:accessories")
    K.eq(int(pg.mode), 0, "HUB our own tab (self) = the BAG view")
    click("cl")
    K.check(E.pg(P1) is None or not E.same(E.pg(P1), pg), "HUB Close closes the page")
    K.save()


# ======================================================================================== D: live start twice
def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.dirname(home)
    f = os.path.join(home, "config.properties")
    had = os.path.exists(os.path.join(home, "power.properties"))
    h0 = HK.tree_hash(home)
    snaps = []
    for start in (1, 2):
        L = loader_for(jar)
        J = lambda n: JClass(PKG + n, loader=L)
        J("AccStore").DIR = Paths.get(os.path.join(home, "bags"))
        J("AccCfg").FILE = Paths.get(f)
        J("AccCfg").migrate051()
        J("AccCfg").migrate055()
        J("AccCfg").migrate0518()
        J("AccPower").FILE = Paths.get(os.path.join(home, "power.properties"))
        J("AccPower").DIR = Paths.get(os.path.join(home, "power"))
        J("AccPower").load()
        J("AccCfg").load(True)
        J("AccNotice").FILE = Paths.get(os.path.join(home, "notices.properties"))
        J("AccNotice").load()
        J("AccSnd").load(Paths.get(home))
        J("CfgPub").start(Paths.get(mods), None)
        if start == 1:
            from jpype import JArray, JObject, JString
            fn = JClass("java.lang.System").getProperties().get("skyy.bridge").get("config:fn:SkyyAccessories")
            g = lambda k_: str(fn.apply(JArray(JObject)([JString("get"), JString(k_)])))
            K.eq([g("power.enabled"), g("power.ap"), g("power.bench"), g("power.wait"), g("power.start"), g("power.unlock"), g("power.show.Jackpot")],
                 ["true", "10,13,16,19,22,25", "full", "5", "Balance", "15", "true"], "D Server Setup > Accessories > Accessory Power: the rows answer (kit get)")
            kk = fn.apply(JArray(JObject)([JString("keys"), JString("pw"), JString("")]))
            K.check(kk is not None and len(list(kk[0])) == 62 and "Slayer.str" in [str(x) for x in kk[0]], "D the pw table lists the 62 Power stats (%s)" % (None if kk is None else len(list(kk[0]))))
            K.check(fn.apply(JArray(JObject)([JString("get"), JString("starter.bag")])) is None and fn.apply(JArray(JObject)([JString("get"), JString("lifelong.bag")])) is None,
                    "D the retired bag-item switches have no row any more")
        J("CfgPub").shutdown()
        snaps.append(HK.tree_hash(home))
    new = sorted(set(snaps[0]) - set(h0))
    K.check(all(snaps[0].get(k_) == v_ for k_, v_ in h0.items()) and new == ([] if had else [x for x in new if x.endswith("power.properties")]) and (had or len(new) == 1),
            "D the first start changes no file of the copy and adds only power.properties (%s)" % new)
    K.check(snaps[1] == snaps[0], "D the second start changes nothing (%d files)" % len(snaps[1]))
    K.save()


HK.run_compare = OH.compare_allowing(lambda n: n.endswith(".lang") or n.startswith("Server/Item/Items/") or n.startswith("Common/UI/Custom/SkyyKit/"))


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED, removed=REMOVED,
           phases=[("assets", run_assets), ("power", run_power), ("retire", run_retire), ("rows", run_rows), ("page", run_page), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyAccessories"))
