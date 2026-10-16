"""Harness for SkyyAccessories 0.5.21 (ACCESSORY CRAFTING LIVES IN THE ACCESSORY BAG; tools/accessories_0_5_21_patch.py).
Build first: python tools/accessories_0_5_21_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.21.py

    python SkyyAccessories/test_skyyaccessories_0.5.21.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.5.20 -> 0.5.21: only the listed members differ; non-class entries: the manifest, the 50 recipe items, server.lang (S)
  S    assets   every one of the 50 accessory recipes: ONLY its BenchRequirement changed (Workbench tab -> the bag's own SkyyAccessoryBag);
                no item of this mod is on a bench / the Workbench tab / pocket crafting any more; server.lang: only descriptions changed
                ("at a Workbench" -> the Accessory Bag's Craft tab), none says "at a Workbench"
  R    THE LINE ROWS + CRAFT + UPGRADE, EXECUTED on the jar's own AccCraft with REAL engine containers / ItemStacks / CraftingRecipe objects
       (the 0.5.18 harness World: stand-in Inventory of SimpleItemContainers, a test Item + recipe map, the real AccStore bag on scratch
       files, the stand-in SkyySacks Void bridge):
         R1 sub tab grouping + sort (Benches: Farming Bench I, Workbench I, Omni last; Combat: Health, Speed; Gathering: Lantern), every row
            the T1 / Normal with "c" when the bag is empty; a recipe still in the OLD Workbench tab category is on no row
         R2 craft T1 -> straight into the bag; the row moves on to the next tier with "u" and the upgrade cost (the bag's one not listed)
         R3 double click of the old row -> "that row changed", nothing used
         R4 upgrade Workbench I -> II IN PLACE (same slot), materials gone, journal "upgraded in place"
         R5 the bag's copy is the one used even with another copy in the inventory (bag-first order); its double click -> nothing
         R6 FULL bag + FULL inventory: an upgrade from Void-only materials works in place; a NEW craft is refused before anything is
            taken (Void untouched); auto-equip off -> a new craft goes to the inventory as before
         R7 missing materials -> refused, row NEEDS MATERIALS
         R8 MAX: the top of a line in the bag -> "RARITY - MAX", no recipe id (no button); a click on its old recipe -> nothing; a line
            whose next recipe sits only in the old tab is MAX too
         R9 the Omni Accessory in the bag -> every covered bench line is MAX ("Omni")
         R10 swapSlot: a slot that no longer holds the old one -> refused, file unchanged; else one save
         R11 knowledge: locked row + refusal, known -> craft, then upgrade in place
         R12 a legacy id in the bag (Skyy_Talisman_Speed_Talisman = Unique) upgrades in place to Rare
         R13 click data (st:<n>, cr:<n>), the page markup in AccPage.class (sub tabs, scroll list, Upgrade, no pager), nothing LOST
  D    live     start twice on a scratch COPY of the live NewBetaTest Skyy_SkyyAccessories (config load, the kit, AccOnce): no file changed
  AA   engine-access audit
NOT driven here: the page click itself (handleDataEvent needs a live UI page; its branches call AccCraft.subIndex / clickIndex + craft, all
driven) and the CraftRecipeEvent firing (needs a live store: fire() answers true without one). Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyonce_harness as OH

VERSION = "0.5.21"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-0.5.20.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "accraft", "acc")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyAccessories")
PKG = "com.skyy.accessories."
BAGCAT = "SkyyAccessoryBag"
OLDTAB = "Workbench_SkyyAccessories"
WB_REQ = [{"Type": "Crafting", "Id": "Workbench", "Categories": [OLDTAB]}]
BAG_REQ = [{"Type": "Crafting", "Id": BAGCAT, "Categories": [BAGCAT]}]
OMNI = "Skyy_Accessory_Omni"
EXPECT = {
    "AccCraft": ["+f LINES", "+f LINESRC", "+f SUB_DEFAULT", "+f SUB_FAM", "+f SUB_NAMES", "+f SUB_OF", "+m accInputs", "+m addStep",
                 "+m below", "+m bestIn", "+m costRank", "+m lineRow", "+m lines", "+m numAfter", "+m omniCovers", "+m planFor", "+m ridOf",
                 "+m rowBefore", "+m rowsFor", "+m shownId", "+m sortTier", "+m step", "+m stepOf", "+m subIndex", "+m subOf",
                 "+m swapIn", "+m swapSlot", "~<clinit>", "~m craft", "~m ours"],   # ours: the TAB constant (now the bag's category)
    "AccPage": ["+f craftSub", "~m build", "~m buildCraft", "~m handleDataEvent"],   # build: the inventory 'none' texts (constants)
    "AccDefs": ["~m retiredChat", "~m retiredWhy"],   # the Night Vision texts (constants inlined)
    "CfgRows": ["~<clinit>", "~m header"],            # the craft.bag row's help text
    "CfgFn": ["~m opExport"],
    "SkyyAccessoriesPlugin": ["~m setup"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def m18():
    """the 0.5.18 harness module (its World / void_bridge stand-ins) on THIS jar; its HK.Child override is undone"""
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
    K.eq(sorted(set(ea) ^ set(eb)), [], "S: no non-class file added / removed")
    pg = [zn.read(n) for n in zn.namelist() if n.endswith("/AccPage.class")]
    K.check(len(pg) == 1 and b"Only this bag counts - move one in to upgrade it." in pg[0],
            "S: fix round - the Craft hint says only the bag counts (an accessory in the inventory must be moved in)")
    changed = sorted(n for n in ea if ea[n] != eb.get(n))
    items = [n for n in changed if n.startswith("Server/Item/Items/")]
    for n in items:
        a, b = json.loads(ea[n]), json.loads(eb[n])
        K.check(a["Recipe"]["BenchRequirement"] == WB_REQ and b["Recipe"]["BenchRequirement"] == BAG_REQ, "S: %s Workbench tab -> the bag" % n)
        a["Recipe"]["BenchRequirement"] = BAG_REQ
        K.check(a == b and list(a) == list(b) and list(a["Recipe"]) == list(b["Recipe"]), "S: %s: nothing else changed (key order kept)" % n)
    K.eq(len(items), 50, "S: the 50 accessory recipes moved")
    allit = [n for n in eb if n.startswith("Server/Item/Items/")]
    req = []
    for n in allit:
        r = json.loads(eb[n]).get("Recipe")
        if r:
            req.extend(q.get("Id") for q in r.get("BenchRequirement") or [])
    K.eq(sorted(set(req)), [BAGCAT], "S: every recipe of this mod names only the bag's own bench (no Workbench, Fieldcraft or other bench)")
    K.check(not any(OLDTAB.encode() in eb[n] for n in allit), "S: no item of this mod in the Workbench tab category")
    langs = [n for n in changed if n.endswith(".lang")]
    K.eq(langs, ["Server/Languages/en-US/server.lang"], "S: server.lang changed")
    for n in langs:
        la = dict(l.split("=", 1) for l in ea[n].decode("utf-8").splitlines() if "=" in l)
        lb = dict(l.split("=", 1) for l in eb[n].decode("utf-8").splitlines() if "=" in l)
        diff = sorted(k for k in set(la) | set(lb) if la.get(k) != lb.get(k))
        K.check(diff and all(k.endswith(".description") and k in la and k in lb for k in diff), "S: only descriptions changed (%d)" % len(diff))
        K.check(all("at a Workbench" in la[k] and "at a Workbench" not in lb[k] and "Accessory Bag's Craft tab" in lb[k] for k in diff),
                "S: each one: 'at a Workbench' -> the Accessory Bag's Craft tab")
        K.check(all(la[k].replace(" (upgrade it at a Workbench).", " (upgrade it in your Accessory Bag's Craft tab).")
                    .replace("Crafted at a Workbench from all", "Crafted in the Accessory Bag's Craft tab from all")
                    .replace("craft one at a Workbench.", "craft one in your Accessory Bag's Craft tab.") == lb[k] for k in diff),
                "S: ... and nothing else in those texts")
        K.check("at a Workbench" not in eb[n].decode("utf-8"), "S: no text sends players to a Workbench")
    rest = [n for n in changed if n not in items and n not in langs and n != "manifest.json"]
    K.eq(rest, [], "S: no other file changed")
    K.save()


# ======================================================================================== R: the line rows, craft and upgrade
ITEMS = [("Skyy_Accessory_Workbench_T1", 1, 1), ("Skyy_Accessory_Workbench_T2", 1, 20), ("Skyy_Accessory_Farmingbench_T1", 1, 15),
         ("Skyy_Talisman_Speed_Common", 1, 4), ("Skyy_Talisman_Speed_Uncommon", 1, 21), ("Skyy_Talisman_Speed_Rare", 1, 30),
         ("Skyy_Talisman_Vitality_Common", 1, 6), ("Skyy_Talisman_Vitality_Uncommon", 1, 22), ("Skyy_Talisman_Lantern_Common", 1, 2),
         ("Skyy_Talisman_Lantern_Uncommon", 1, 23), (OMNI, 1, 50),
         ("Bench_WorkBench", 100, 0), ("Ingredient_Bar_Copper", 100, 0), ("Ingredient_Crystal_Cyan", 100, 0), ("Ingredient_Feathers_Light", 100, 0),
         ("Furniture_Crude_Torch", 100, 0), ("Ingredient_Stick", 100, 0), ("Ingredient_Crystal_Red", 100, 0)]
SPEED_IN = [("Ingredient_Crystal_Cyan", 2), ("Ingredient_Feathers_Light", 3), ("Ingredient_Bar_Copper", 2)]


def recipe(W, out, ins, cat=BAGCAT, bench=BAGCAT, know=False):
    arr = W.JArray(W.MQ)(len(ins))
    for i, (a, q) in enumerate(ins):
        arr[i] = W.mq(a, None, q)
    po = W.mq(out, None, 1)
    outs = W.JArray(W.MQ)(1)
    outs[0] = po
    cats = W.JArray(W.JClass("java.lang.String"))(1)
    cats[0] = cat
    br = W.JArray(W.BRQ)(1)
    br[0] = W.BRQ(W.BT.Crafting, bench, cats, 0, W.JArray(W.JClass("java.lang.String"))(0))
    r = W.CRR(arr, po, outs, 1, br, 0.0, bool(know), 0)
    rid = out + "_Recipe_Generated_0"
    W.jfield(W.CRR, "id").set(r, rid)
    W.rmap.put(rid, r)
    return rid


def setup(W):
    for iid, st, lv in ITEMS:
        W.item(iid, st, lv)
    ids = {}
    ids["wb1"] = recipe(W, "Skyy_Accessory_Workbench_T1", [("Bench_WorkBench", 1), ("Ingredient_Bar_Copper", 4)])
    ids["wb2"] = recipe(W, "Skyy_Accessory_Workbench_T2", [("Skyy_Accessory_Workbench_T1", 1), ("Ingredient_Bar_Copper", 3)])
    ids["farm1"] = recipe(W, "Skyy_Accessory_Farmingbench_T1", [("Ingredient_Bar_Copper", 2)])
    ids["spd1"] = recipe(W, "Skyy_Talisman_Speed_Common", SPEED_IN)
    ids["spd2"] = recipe(W, "Skyy_Talisman_Speed_Uncommon", [("Skyy_Talisman_Speed_Common", 1), ("Ingredient_Bar_Copper", 4)])
    ids["spd3"] = recipe(W, "Skyy_Talisman_Speed_Rare", [("Skyy_Talisman_Speed_Uncommon", 1), ("Ingredient_Bar_Copper", 2)])
    ids["vit1"] = recipe(W, "Skyy_Talisman_Vitality_Common", [("Ingredient_Crystal_Red", 2)])
    ids["vit2old"] = recipe(W, "Skyy_Talisman_Vitality_Uncommon", [("Skyy_Talisman_Vitality_Common", 1), ("Ingredient_Crystal_Red", 3)],
                            cat=OLDTAB, bench="Workbench")   # a recipe still in the OLD Workbench tab: on no row
    ids["lan1"] = recipe(W, "Skyy_Talisman_Lantern_Common", [("Furniture_Crude_Torch", 4), ("Ingredient_Bar_Copper", 2)], know=True)
    ids["lan2"] = recipe(W, "Skyy_Talisman_Lantern_Uncommon", [("Skyy_Talisman_Lantern_Common", 1), ("Furniture_Crude_Torch", 2)], know=True)
    ids["omni"] = recipe(W, OMNI, [("Skyy_Accessory_Workbench_T2", 1), ("Skyy_Accessory_Farmingbench_T1", 1)])
    return ids


def run_rows(out, jar, scratch, _home):
    K = HK.Child(out)
    M = m18()
    W = M.World(os.path.join(scratch, "r"))
    ids = setup(W)
    C, Acc, Defs, JShort = W.Craft, W.Acc, W.Defs, W.JShort
    VOID = {"n": {}, "owe": {}, "paused": False, "short": 0, "calls": []}
    _keep = M.void_bridge(W, VOID)

    def journal():
        return open(W.LOGF, encoding="utf8").read() if os.path.exists(W.LOGF) else ""

    def craft(p, pr, u, rid):
        return str(C.craft(pr, None, None, p, u, str(u), rid))

    def view(u, sub, p):
        rows = []
        for e in C.rowsFor(u, str(u), p, sub):
            ri = [str(x) for x in C.lineRow(u, str(u), p, e)]
            rid = C.ridOf(e)
            rows.append((ri[0], ri[6], ri[2], ri[4], None if rid is None else str(rid), ri[5]))
        return rows

    def row_of(u, sub, p, item):
        got = [r for r in view(u, sub, p) if r[0] == item]
        return got[0] if len(got) == 1 else None

    def put(inv, sec, sl, iid, q):
        c = {"s": inv.getStorage(), "h": inv.getHotbar(), "b": inv.getBackpack()}[sec]
        assert c.setItemStackForSlot(JShort(sl), W.IS(iid, q)).succeeded()

    # ===== R1 grouping, sort, empty bag
    inv = W.inv()
    p, pr, U = W.player(inv, "Ann")
    K.eq([str(n) for n in C.SUB_NAMES], ["Benches", "Combat", "Gathering"], "R1 the sub tabs")
    v0, v1, v2 = view(U, 0, p), view(U, 1, p), view(U, 2, p)
    K.eq([(r[0], r[1]) for r in v0], [("Skyy_Accessory_Workbench_T1", "c"), ("Skyy_Accessory_Farmingbench_T1", "c"), (OMNI, "c")],
         "R1 Benches: Workbench Accessory I first (LOCKED 10-13, the tutorial's first craft), then the T1 of every bench, the Omni last")
    # fix round: inside a tier easiest to craft first (the 0.5.13 cost order = ItemLevel), name only as the tie-break
    W.item("Skyy_Accessory_Alchemybench_T1", 1, 18)
    W.item("Skyy_Accessory_Furnace_T1", 1, 18)
    JO = W.JArray(W.JClass("java.lang.Object"))

    def rw_(iid):
        a = JO(5)
        a[4] = iid
        return a
    alc, frm, fur, wb1, wb2 = (rw_(i) for i in ("Skyy_Accessory_Alchemybench_T1", "Skyy_Accessory_Farmingbench_T1", "Skyy_Accessory_Furnace_T1",
                                               "Skyy_Accessory_Workbench_T1", "Skyy_Accessory_Workbench_T2"))
    K.check(bool(C.rowBefore(frm, alc)) and not bool(C.rowBefore(alc, frm)),
            "R1 sort: same tier -> the cheaper (Farming, level 15) before Alchemy (level 18) although 'Alchemy' < 'Farming' by name")
    K.check(bool(C.rowBefore(alc, fur)) and not bool(C.rowBefore(fur, alc)), "R1 sort: same tier + same cost -> by name (Alchemy before Furnace)")
    K.check(bool(C.rowBefore(wb1, frm)) and bool(C.rowBefore(wb1, alc)) and bool(C.rowBefore(frm, wb2)),
            "R1 sort: Workbench I before every T1; Workbench II sorts by its tier (after the T1s)")
    K.check(int(C.costRank("Skyy_Accessory_Unknown_T1")) == 999999, "R1 sort: an item without a level sorts after the known ones of its tier")
    K.eq([(r[0], r[1]) for r in v1], [("Skyy_Talisman_Speed_Common", "c"), ("Skyy_Talisman_Vitality_Common", "c")],
         "R1 Combat: the Normal of every stat line, easiest first (Speed level 4 before Health level 6 - not by name)")
    K.eq([(r[0], r[1], r[2]) for r in v2], [("Skyy_Talisman_Lantern_Common", "c", "NORMAL - LOCKED")], "R1 Gathering: the Lantern (locked)")
    K.check(all(r[4] is not None for r in v0 + v1 + v2), "R1 every craft row carries its recipe id (a button)")
    K.check("Skyy_Talisman_Vitality_Uncommon" not in [str(C.outId(r)) for r in C.recipes()], "R1 a recipe in the OLD Workbench tab category is not listed")
    K.eq([int(C.subOf(i)) for i in ("Skyy_Accessory_Campfire_T1", OMNI, "Skyy_Talisman_Lantern_Epic", "Skyy_Talisman_Speed_Rare",
                                    "Skyy_Talisman_Endurance_Common", "Skyy_Talisman_Strength_T1")], [0, 0, 2, 1, 1, 1],
         "R1 subOf: benches + Omni -> Benches, Lantern -> Gathering, stat lines (and an unlisted one) -> Combat")
    # ===== R2 craft T1 -> the bag; the row moves on
    put(inv, "s", 0, "Bench_WorkBench", 1)
    put(inv, "s", 1, "Ingredient_Bar_Copper", 4)
    r = craft(p, pr, U, ids["wb1"])
    K.eq(r, "crafted Workbench I - it went straight into your bag", "R2 craft T1: " + r)
    K.eq((W.bag(U)[0], W.count(inv, "Skyy_Accessory_Workbench_T1"), W.count(inv, "Ingredient_Bar_Copper")), ("Skyy_Accessory_Workbench_T1", 0, 0),
         "R2 ... in the bag, not in the inventory, materials gone")
    rw = row_of(U, 0, p, "Skyy_Accessory_Workbench_T2")
    K.check(rw is not None and rw[1] == "u" and rw[2] == "UNIQUE - NEEDS MATERIALS" and rw[4] == ids["wb2"], "R2 the row now shows the next tier, UPGRADE: %s" % (rw,))
    K.check(rw is not None and rw[3].startswith("Upgrades your Workbench I - cost: ") and "Workbench" not in rw[3].split("cost: ")[1] and "0/3" in rw[3],
            "R2 ... the upgrade cost without the bag's own one: %s" % (rw and rw[3]))
    # ===== R3 double click of the old row
    put(inv, "s", 2, "Bench_WorkBench", 1)
    put(inv, "s", 3, "Ingredient_Bar_Copper", 7)
    s0, b0 = W.slots(inv), W.bag(U)
    r = craft(p, pr, U, ids["wb1"])
    K.eq(r, "that row changed - the list is up to date now, nothing was used", "R3 a second click on the T1 row: " + r)
    K.check(W.slots(inv) == s0 and W.bag(U) == b0, "R3 ... nothing changed")
    rw = row_of(U, 0, p, "Skyy_Accessory_Workbench_T2")
    K.check(rw[2] == "UNIQUE - CAN UPGRADE" and rw[5] == str(C.GREEN), "R3 the upgrade row: CAN UPGRADE, green")
    # ===== R4 the upgrade IN PLACE
    r = craft(p, pr, U, ids["wb2"])
    K.eq(r, "upgraded to Workbench II in your bag - your Workbench I was used for it", "R4 upgrade: " + r)
    K.eq((W.bag(U)[0], W.bag(U)[1], W.count(inv, "Ingredient_Bar_Copper"), W.count(inv, "Skyy_Accessory_Workbench_T1")),
         ("Skyy_Accessory_Workbench_T2", None, 4, 0), "R4 ... the same slot holds the II, 3 Copper used, no I anywhere")
    bf = open(os.path.join(scratch, "r", "bags", "%s.properties" % U), encoding="latin-1").read()
    K.check("slot0=Skyy_Accessory_Workbench_T2" in bf and "Workbench_T1" not in bf, "R4 ... the bag file saved")
    K.check("upgraded in place, slot 0: Skyy_Accessory_Workbench_T1 -> Skyy_Accessory_Workbench_T2" in journal(), "R4 ... journal DONE upgraded in place")
    K.eq(row_of(U, 0, p, "Skyy_Accessory_Workbench_T2")[1:3], ("m", "UNIQUE - MAX"), "R4 the test line's top: MAX")
    # ===== R5 bag-first: the bag's copy is the one upgraded, the inventory's copy stays
    inv5 = W.inv(put=[("s", 0, "Skyy_Talisman_Speed_Common", 1), ("s", 1, "Ingredient_Bar_Copper", 4)])
    p5, pr5, U5 = W.player(inv5, "Ben")
    Acc.putK(U5, str(U5), 3, "Skyy_Talisman_Speed_Common")
    rs = row_of(U5, 1, p5, "Skyy_Talisman_Speed_Uncommon")
    K.check(rs is not None and rs[1] == "u" and rs[2] == "UNIQUE - CAN UPGRADE", "R5 row: Speed Unique UPGRADE: %s" % (rs,))
    r = craft(p5, pr5, U5, ids["spd2"])
    K.eq(r, "upgraded to Unique Speed Accessory in your bag - your Normal Speed Accessory was used for it", "R5 upgrade: " + r)
    K.eq((W.bag(U5)[3], W.bag(U5).count(None), W.count(inv5, "Skyy_Talisman_Speed_Common"), W.count(inv5, "Ingredient_Bar_Copper")),
         ("Skyy_Talisman_Speed_Uncommon", int(Acc.CAP) - 1, 1, 0), "R5 ... bag slot 3 upgraded, the inventory's Normal untouched (bag first), Copper used")
    s0, b0 = W.slots(inv5), W.bag(U5)
    put(inv5, "s", 5, "Ingredient_Bar_Copper", 4)
    s0 = W.slots(inv5)
    r = craft(p5, pr5, U5, ids["spd2"])
    K.check(r == "that row changed - the list is up to date now, nothing was used" and W.slots(inv5) == s0 and W.bag(U5) == b0,
            "R5 DOUBLE CLICK of the upgrade: nothing used (the inventory Normal + Copper would have paid): " + r)
    # ===== R6 full bag + full inventory
    inv6 = W.inv(fill="Ingredient_Stick")
    p6, pr6, U6 = W.player(inv6, "Cal")
    cap = int(Acc.capOf(W.JArray(W.JClass("java.lang.String"))(int(Acc.CAP))))
    Acc.putK(U6, str(U6), 0, "Skyy_Talisman_Speed_Uncommon")
    for i in range(1, cap):
        Acc.putK(U6, str(U6), i, "Skyy_Accessory_Workbench_T1")
    VOID["n"]["Ingredient_Bar_Copper"] = 2
    s0, b0 = W.slots(inv6), W.bag(U6)
    r = craft(p6, pr6, U6, ids["spd3"])
    K.eq(r, "upgraded to Rare Speed Accessory in your bag - your Unique Speed Accessory was used for it",
         "R6 full bag (%d of %d) + full inventory, materials in the Void: upgraded in place: %s" % (cap, cap, r))
    b1 = list(b0)
    b1[0] = "Skyy_Talisman_Speed_Rare"
    K.check(W.bag(U6) == b1 and W.slots(inv6) == s0 and VOID["n"]["Ingredient_Bar_Copper"] == 0 and VOID["owe"].get("Ingredient_Bar_Copper") == 0,
            "R6 ... only slot 0 changed, inventory identical, 2 Copper from the Void (committed)")
    VOID["n"]["Ingredient_Crystal_Red"] = 2
    VOID["calls"][:] = []
    r = craft(p6, pr6, U6, ids["vit1"])
    K.eq(r, "your Accessory Bag has no free slot for Normal Health Accessory - free one first, nothing was used", "R6 a NEW craft into a full bag: " + r)
    K.check(VOID["calls"] == [] and VOID["n"]["Ingredient_Crystal_Red"] == 2 and W.bag(U6) == b1 and W.slots(inv6) == s0,
            "R6 ... refused before anything was taken (no Void take)")
    K.eq(row_of(U6, 1, p6, "Skyy_Talisman_Vitality_Common")[2], "NORMAL - CAN CRAFT", "R6 (the row itself still offers it - the click answers)")
    inv6b = W.inv(put=[("s", 0, "Ingredient_Bar_Copper", 2)])
    p6b, pr6b, U6b = W.player(inv6b, "Cal2")
    Defs.AUTO = False
    r = craft(p6b, pr6b, U6b, ids["farm1"])
    Defs.AUTO = True
    K.eq((r, W.count(inv6b, "Skyy_Accessory_Farmingbench_T1"), W.bag(U6b)[0]),
         ("crafted Farming Bench I - it is in your inventory", 1, None), "R6 auto-equip off: a new craft goes to the inventory (as before)")
    # ===== R7 missing materials
    inv7 = W.inv()
    p7, pr7, U7 = W.player(inv7, "Dee")
    K.eq(row_of(U7, 1, p7, "Skyy_Talisman_Speed_Common")[2], "NORMAL - NEEDS MATERIALS", "R7 row: NEEDS MATERIALS")
    s0 = W.slots(inv7)
    r = craft(p7, pr7, U7, ids["spd1"])
    K.check(r == "not enough materials for Normal Speed Accessory - nothing was used" and W.slots(inv7) == s0 and W.bag(U7) == [None] * int(Acc.CAP),
            "R7 craft without materials: " + r)
    # ===== R8 MAX
    rm = row_of(U6, 1, p6, "Skyy_Talisman_Speed_Rare")
    K.check(rm is not None and rm[1:3] == ("m", "RARE - MAX") and rm[4] is None and rm[3].startswith("Fully upgraded"), "R8 the top of the line: MAX, no recipe: %s" % (rm,))
    put(inv7, "s", 0, "Ingredient_Bar_Copper", 20)
    s0 = W.slots(inv7)
    Acc.putK(U7, str(U7), 0, "Skyy_Talisman_Speed_Rare")
    r = craft(p7, pr7, U7, ids["spd3"])
    K.check(r == "that row changed - the list is up to date now, nothing was used" and W.slots(inv7) == s0, "R8 a click on a MAX line's old recipe: " + r)
    Acc.putK(U7, str(U7), 1, "Skyy_Talisman_Vitality_Common")
    rv = row_of(U7, 1, p7, "Skyy_Talisman_Vitality_Common")
    K.check(rv is not None and rv[1] == "m", "R8 Health Normal in the bag, its Unique recipe only in the old tab -> MAX: %s" % (rv,))
    # ===== R9 the Omni covers the benches
    inv9 = W.inv()
    p9, pr9, U9 = W.player(inv9, "Eli")
    Acc.putK(U9, str(U9), 0, OMNI)
    v = view(U9, 0, p9)
    K.check([r_[1] for r_ in v] == ["m", "m", "m"] and [r_[3].startswith("Your Omni Accessory") for r_ in v] == [True, True, False] and all(r_[4] is None for r_ in v),
            "R9 Omni in the bag: both bench lines MAX ('your Omni Accessory'), the Omni line MAX: %s" % [(r_[0], r_[3][:30]) for r_ in v])
    # ===== R10 swapSlot
    from jpype import JBoolean
    ok = W.JArray(JBoolean)(1)
    f9 = os.path.join(scratch, "r", "bags", "%s.properties" % U9)
    t0 = open(f9, "rb").read()
    C.swapSlot(U9, str(U9), 0, "Skyy_Accessory_Workbench_T1", "Skyy_Accessory_Workbench_T2", ok)
    K.check(not bool(ok[0]) and W.bag(U9)[0] == OMNI and open(f9, "rb").read() == t0, "R10 swapSlot: the slot does not hold the old one -> refused, file unchanged")
    C.swapSlot(U9, str(U9), 0, OMNI, "Skyy_Accessory_Workbench_T2", ok)
    K.check(bool(ok[0]) and W.bag(U9)[0] == "Skyy_Accessory_Workbench_T2" and "slot0=Skyy_Accessory_Workbench_T2" in open(f9, encoding="latin-1").read(),
            "R10 swapSlot: swapped + saved")
    # ===== R11 knowledge
    inv11 = W.inv(put=[("s", 0, "Furniture_Crude_Torch", 6), ("s", 1, "Ingredient_Bar_Copper", 2)])
    p11, pr11, U11 = W.player(inv11, "Fin")
    s0 = W.slots(inv11)
    K.eq(craft(p11, pr11, U11, ids["lan1"]), "Normal Lantern Accessory is locked - collect Tree Sap to unlock it (Collections)", "R11 locked")
    K.check(W.slots(inv11) == s0, "R11 ... nothing used")
    p11b, pr11b, U11b = W.player(inv11, "Fin2", known=["Skyy_Talisman_Lantern_Common", "Skyy_Talisman_Lantern_Uncommon"])
    K.eq(view(U11b, 2, p11b)[0][2], "NORMAL - CAN CRAFT", "R11 known: CAN CRAFT")
    K.eq(craft(p11b, pr11b, U11b, ids["lan1"]), "crafted Normal Lantern Accessory - it went straight into your bag", "R11 known: crafted")
    rl = view(U11b, 2, p11b)[0]
    K.check(rl[0] == "Skyy_Talisman_Lantern_Uncommon" and rl[1] == "u" and rl[2] == "UNIQUE - CAN UPGRADE" and "Torch 2/2" in rl[3]
            and "Lantern" not in rl[3].split("cost: ")[1], "R11 the Gathering row: Unique Lantern, UPGRADE, its cost: %s" % (rl,))
    K.eq(craft(p11b, pr11b, U11b, ids["lan2"]), "upgraded to Unique Lantern Accessory in your bag - your Normal Lantern Accessory was used for it", "R11 upgrade the Lantern in place")
    K.eq((W.bag(U11b)[0], W.count(inv11, "Furniture_Crude_Torch")), ("Skyy_Talisman_Lantern_Uncommon", 0), "R11 ... slot 0, the torches used")
    # ===== R12 a legacy id in the bag
    inv12 = W.inv(put=[("s", 0, "Ingredient_Bar_Copper", 2)])
    p12, pr12, U12 = W.player(inv12, "Gil")
    Acc.putK(U12, str(U12), 0, "Skyy_Talisman_Speed_Talisman")
    rg = row_of(U12, 1, p12, "Skyy_Talisman_Speed_Rare")
    K.check(rg is not None and rg[1] == "u", "R12 legacy Speed Talisman (= Unique) in the bag -> the Rare upgrade row: %s" % (rg,))
    r = craft(p12, pr12, U12, ids["spd3"])
    K.eq((r, W.bag(U12)[0]), ("upgraded to Rare Speed Accessory in your bag - your Unique Speed Accessory was used for it", "Skyy_Talisman_Speed_Rare"),
         "R12 ... upgraded in place")
    # ===== R13 click data, markup, nothing lost
    K.eq([int(C.subIndex(d)) for d in ('{"a":"st:2"}', '{"a":"st:0"}', '{"a":"st:3"}', '{"a":"st:"}', '{"a":"cr:1"}', None)],
         [2, 0, -1, -1, -1, -1], "R13 subIndex: st:<n> of an existing sub tab only")
    K.eq([int(C.clickIndex(d)) for d in ('{"a":"cr:7"}', '{"a":"st:1"}')], [7, -1], "R13 clickIndex unchanged")
    z = zipfile.ZipFile(JAR)
    pc = z.read("com/skyy/accessories/AccPage.class")
    K.check(all(x in pc for x in (b"#SkyyAccSts", b"#SkyyAccSt0", b"#SkyyAccSt2", b"TopScrolling", b"Upgrade", b"st:", b"this.craftSub") if x != b"this.craftSub"),
            "R13 the page: sub tabs, the scrolling list, the Upgrade button")
    K.check(b"#SkyyAccCpPrev" not in pc and b"#SkyyAccCpNext" not in pc, "R13 the Craft view has no pager any more")
    K.check(b"craft accessories at a Workbench" not in pc and b"or at a Workbench" not in pc, "R13 no page text sends players to a Workbench")
    cc = z.read("com/skyy/accessories/AccCraft.class")
    K.check(BAGCAT.encode() in cc and OLDTAB.encode() not in cc and b"Gathering" in cc, "R13 AccCraft lists the bag's own category (not the Workbench tab) + the sub tab names")
    z.close()
    K.check("LOST" not in journal(), "R nothing was ever lost (journal)")
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
    h0 = HK.tree_hash(home)
    snaps, rows = [], []
    for start in (1, 2):
        L = loader_for(jar)
        J = lambda n: JClass(PKG + n, loader=L)
        J("AccStore").DIR = Paths.get(os.path.join(home, "bags"))
        J("AccCfg").FILE = Paths.get(f)
        J("AccCfg").migrate051()
        J("AccCfg").migrate055()
        J("AccCfg").migrate0518()
        J("AccCfg").load(True)
        J("AccNotice").FILE = Paths.get(os.path.join(home, "notices.properties"))
        J("AccNotice").load()
        J("AccSnd").load(Paths.get(home))
        J("AccOnce").DIR = Paths.get(os.path.join(home, "lifelong"))
        J("AccOnce").publish()
        J("CfgPub").start(Paths.get(mods), None)
        rows.append(int(J("AccCraft").rowsFor(None, None, None, 0).size()))
        J("CfgPub").shutdown()
        J("AccOnce").unpublish()
        snaps.append(HK.tree_hash(home))
    K.check(snaps[0] == h0 and snaps[1] == h0, "D neither start changed any file of the copy (%d files)" % len(h0))
    K.eq(rows, [0, 0], "D the line table without a recipe store: empty, no throw")
    K.save()


HK.run_compare = OH.compare_allowing(lambda n: n.endswith(".lang") or n.startswith("Server/Item/Items/"))


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("assets", run_assets), ("rows", run_rows), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyAccessories"))
