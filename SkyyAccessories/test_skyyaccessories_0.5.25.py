"""Harness for SkyyAccessories 0.5.25 (THE FURNACE CHARM; tools/accessories_0_5_25_patch.py, research/Zone-Ores-Alloys-Spec.md 4).
Build first: python tools/accessories_0_5_25_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.25.py

    python SkyyAccessories/test_skyyaccessories_0.5.25.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.5.24 -> 0.5.25: + AccCharm, AccCharmRecipe; the listed members differ; non-class entries: manifest, server.lang, the six
                charm item files + their six icons only
  0.5.22's phases on the new jar (via test_skyyaccessories_0.5.24.py - its renamed craft lines): power, retire, rows, page, live; 0.5.23's
  client-model phase
  FA   the charm ASSETS: six items, ids absent from Assets.zip, no Recipe, the bench rarity ladder, own icons (64 x 64 PNG, all different),
       name + description in both key twins, every description starts with its tier tag ("T<n> Charm - "; Eternal Flame "T5 Charm"), the
       tag = tools/tier_tags.py ladder_tag(n, "Charm")
  F    THE CHARM, EXECUTED on the jar (the 0.5.18 harness World: fake item / recipe asset maps, test inventories, the stand-in Void):
         F1 the id rules (isCharm, tierOf 1..6, groupOf C:Furnace, rarity I Normal .. IV+ Legendary, benchOf null, no Accessory Power)
         F2 acc:smelt text: none / T1..T5 / Eternal Flame / switched off / custom numbers / a bad number line = the built-in numbers
         F3 the bridge (5 fields, the 5th = the profile key) on EQUIP / UNEQUIP / PROFILE SWITCH (publish, checkEpoch, the 1 s smeltNow), on a
            JOIN (smeltNow), removed on LEAVE / SHUTDOWN (smeltPrune) - an inventory copy never counts
         F4 the CRAFT rows (Gathering sub tab, one row = the next step): T1 from scratch, the tier-ups IN PLACE with exact item counts
            (inventory, Void, bag: no dupe, no loss; a spare copy in the inventory is untouched), a stale / double click uses nothing, not
            enough materials uses nothing, a Void that gives short rolls everything back, a material this server has no item for = LOCKED
         F5 Eternal Flame: locked without SkyyCollections, locked below furnace.eternalTier, then upgraded in place -> "5|50|0|1"
         F6 settings: AccDefs.fcLoad (defaults, bad lines -> defaults + the reason), fcCheck / fcCostWhy refusals, a custom cost rebuilds
            the recipe list, furnace.on off locks the rows and publishes 0|0|0|0
         F7 texts: Bonuses row, the grid hover, /charms lines, admin give, Server Setup rows (category Furnace Charm, 10 rows, field binds)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyonce_harness as OH

_sp = importlib.util.spec_from_file_location("acc_h524", os.path.join(HERE, "test_skyyaccessories_0.5.24.py"))
T24 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T24)
T22, T23 = T24.T22, T24.T23
# 0.5.25 adds assets: the non-class entries may differ in manifest.json, server.lang and the charm items / icons
HK.run_compare = OH.compare_allowing(lambda n: n.endswith(".lang") or n.startswith("Server/Item/Items/Utility/Skyy_Charm_Furnace_")
                                     or n.startswith("Common/Icons/ItemsGenerated/SkyyAccessories_Charm_Furnace_"))

VERSION = "0.5.25"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-0.5.24.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "ores-b2", "acc")))
PKG = T22.PKG
FC = ["Skyy_Charm_Furnace_T%d" % t for t in range(1, 6)] + ["Skyy_Charm_Furnace_Eternal"]
NAMES = ["Furnace Charm I", "Furnace Charm II", "Furnace Charm III", "Furnace Charm IV", "Furnace Charm V", "Eternal Flame"]
COST = [[("Ingredient_Bar_Copper", 32), ("Ingredient_Bar_Iron", 32)], [("Ingredient_Bar_Thorium", 64), ("Ingredient_Bar_Lead_SkyWynn", 64)],
        [("Ingredient_Bar_Cobalt", 128), ("Ingredient_Bar_Chromium_SkyWynn", 128)], [("Ingredient_Bar_Adamantite", 192), ("Ingredient_Bar_Slag_SkyWynn", 192)],
        [("Ingredient_Bar_Mithril", 256), ("Ingredient_Bar_Titanium_SkyWynn", 256)], [("Skyy_Ench_Charcoal", 16), ("Ingredient_Bar_Lumen_SkyWynn", 64)]]
EXPECT = {
    "AccAdmin": ["~m giveable"],
    "AccCfg": ["~m load", "~m writeDefaults"],
    "AccCraft": ["+f CLIST", "~<clinit>", "~m craft", "~m lineRow", "~m recipes", "~m subOf"],
    "AccDefs": ["+f FC_ALLOYS", "+f FC_COLL", "+f FC_COST1", "+f FC_COST2", "+f FC_COST3", "+f FC_COST4", "+f FC_COST5", "+f FC_COSTE",
                "+f FC_COST_DEF", "+f FC_COST_KEYS", "+f FC_ETIER", "+f FC_ETIER_DEF", "+f FC_ETIER_MAX", "+f FC_FP", "+f FC_FUEL", "+f FC_FUEL_DEF",
                "+f FC_FUEL_MAX", "+f FC_IDS", "+f FC_NAMES", "+f FC_ON", "+f FC_PSIG", "+f FC_PUBSIG", "+f FC_TIME", "+f FC_TIME_DEF",
                "+f FC_TIME_MAX", "+f FC_TP", "+m fcAlloys", "+m fcBest", "+m fcChanged", "+m fcCheck", "+m fcCostWhy", "+m fcFuel", "+m fcFx",
                "+m fcLoad", "+m fcName", "+m fcNums", "+m fcParse", "+m fcSig", "+m fcSmelt", "+m fcStatus", "+m fcStep", "+m fcText", "+m fcTime",
                "+m isCharm", "~<clinit>", "~m benchOf", "~m bonusRows", "~m groupOf", "~m isAccessory", "~m lineLabel", "~m linesText", "~m pretty",
                "~m tierOf"],
    "AccPage": ["~m effects"],
    "AccStore": ["+f SMELTED", "+m smeltIn", "+m smeltNow", "+m smeltPrune", "+m smeltPut", "~<clinit>", "~m accCount", "~m publish", "~m publishOnline", "~m restamp"],
    "AccEffects": ["~m tick"],
    "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"],
    "CfgFn": ["~m opExport"],
    "SkyyAccessoriesPlugin": ["~m setup", "~m shutdown"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def tag(n):
    import tier_tags as TT
    return TT.ladder_tag(n, "Charm")


# ======================================================================================== FA: the charm assets
def run_fassets(out, jar, scratch, _home):
    K = HK.Child(out)
    import serverjar as SJ
    z = zipfile.ZipFile(jar)
    za = zipfile.ZipFile(SJ.assets_zip())
    van = set(os.path.basename(n)[:-5] for n in za.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    lang = z.read("Server/Languages/en-US/server.lang").decode("utf8")
    lmap = {}
    dup = []
    for ln in lang.split("\n"):
        if "=" in ln:
            k, v = ln.split("=", 1)
            if k in lmap:
                dup.append(k)
            lmap[k] = v
    K.check(not dup, "FA no lang key twice (%s)" % dup[:3])
    icons = []
    for i, iid in enumerate(FC):
        t = i + 1
        p = "Server/Item/Items/Utility/%s.json" % iid
        K.check(p in z.namelist() and iid not in van, "FA %s is in the jar and not a vanilla id" % iid)
        n = json.loads(z.read(p))
        want_q = ["", "Skyy_Acc_Normal", "Skyy_Acc_Unique", "Skyy_Acc_Rare", "Skyy_Acc_Legendary", "Skyy_Acc_Legendary", "Skyy_Acc_Legendary"][t]
        K.check("Recipe" not in n and n["Quality"] == want_q and n["MaxStack"] == 1 and n.get("Categories") == ["Items.Tools"] and "Variant" not in n,
                "FA %s: no item recipe (made at run time), quality %s, one per stack, in the creative library" % (iid, want_q))
        K.check(("Common/" + n["Icon"]) in z.namelist() and "SkyyAccessories_Charm_Furnace_" in n["Icon"], "FA %s: its own icon %s" % (iid, n["Icon"]))
        png = z.read("Common/" + n["Icon"])
        icons.append(png)
        K.check(png[:8] == b"\x89PNG\r\n\x1a\n" and png[16:24] == b"\x00\x00\x00\x40\x00\x00\x00\x40", "FA %s: the icon is a 64 x 64 PNG" % iid)
        K.check(("Common/" + n["Model"]) in za.namelist() and ("Common/" + n["Texture"]) in za.namelist(), "FA %s: the vanilla model + texture exist" % iid)
        for pre in ("items.", "server.items."):
            K.eq(lmap.get("%s%s.name" % (pre, iid)), NAMES[i], "FA %s%s.name" % (pre, iid))
            d = lmap.get("%s%s.description" % (pre, iid), "")
            K.check(d.startswith(tag(min(t, 5)) + " - "), "FA %s%s.description starts with its tier tag %r: %s" % (pre, iid, tag(min(t, 5)), d[:60]))
    K.check(len(set(icons)) == 6, "FA six different icons")
    K.check("smelts 30% faster but burns 45% more fuel, and you can smelt Bronze, Dusk and Azurvane" in lmap["items.Skyy_Charm_Furnace_T3.description"],
            "FA the T3 text names the built-in numbers + the alloys")
    K.check("needs no fuel" in lmap["items.Skyy_Charm_Furnace_Eternal.description"] and "Charcoal collection tier 7" in lmap["items.Skyy_Charm_Furnace_Eternal.description"],
            "FA the Eternal Flame text: no fuel, Charcoal tier 7")
    old = zipfile.ZipFile(OLD_JAR)
    added = sorted(set(z.namelist()) - set(old.namelist()))
    K.eq([a for a in added if not a.endswith(".class")], sorted(["Server/Item/Items/Utility/%s.json" % i for i in FC] +
         ["Common/Icons/ItemsGenerated/SkyyAccessories_Charm_Furnace_%s.png" % w for w in ("T1", "T2", "T3", "T4", "T5", "Eternal")]), "FA exactly 12 asset files added")
    ol = old.read("Server/Languages/en-US/server.lang").decode("utf8")
    K.check(lang.startswith(ol) and all("Skyy_Charm_Furnace_" in x for x in lang[len(ol):].strip().split("\n")),
            "FA server.lang = 0.5.24's + only the charm lines (%d)" % len(lang[len(ol):].strip().split("\n")))
    K.save()


# ======================================================================================== F: the charm, executed
def run_charm(out, jar, scratch, _home):
    K = HK.Child(out)
    M = T22.m18()
    W = M.World(os.path.join(scratch, "f"))
    C, D, A = W.Craft, W.Defs, W.Acc
    from jpype import JClass, JImplements, JOverride, JObject, JShort
    Pw, Page, Adm, Ch = W.J("AccPower"), W.J("AccPage"), W.J("AccAdmin"), W.J("AccCharm")
    Props = JClass("java.util.Properties")
    # F1 the id rules
    K.eq([int(D.tierOf(i)) for i in FC], [1, 2, 3, 4, 5, 6], "F1 tierOf: I..V = 1..5, Eternal Flame = 6")
    K.eq([int(D.rarityOf(i)) for i in FC], [1, 2, 3, 4, 4, 4], "F1 rarity: I Normal, II Unique, III Rare, IV and up Legendary")
    K.check(all(bool(D.isCharm(i)) and bool(D.isAccessory(i)) and str(D.groupOf(i)) == "C:Furnace" and D.benchOf(i) is None for i in FC),
            "F1 every step: a charm, an accessory, line C:Furnace, no bench")
    K.check(not D.isCharm("Skyy_Charm_Furnace_T6") and not D.isAccessory("Skyy_Charm_Other") and D.groupOf("Skyy_Charm_Other") is None,
            "F1 an unknown Skyy_Charm_ id is nothing of ours")
    K.eq([str(D.pretty(i)) for i in FC], NAMES, "F1 names")
    arr = W.JArray(JClass("java.lang.String"))(3)
    arr[0], arr[1], arr[2] = FC[2], "Skyy_Talisman_Speed_Common", None
    K.check(int(Pw.apRaw(FC[2], False)) == 0 and int(Pw.apOf(arr)) == int(Pw.apRaw("Skyy_Talisman_Speed_Common", False)) and int(Pw.apOne(arr, FC[2])) == 0,
            "F1 no Accessory Power from a charm (AP of the bag = the Speed accessory's alone)")
    # F2 the acc:smelt text
    def sm(*ids):
        a = W.JArray(JClass("java.lang.String"))(max(1, len(ids)))
        for k, x in enumerate(ids):
            a[k] = x
        return str(D.fcSmelt(a))
    K.eq([sm(), sm("Skyy_Talisman_Speed_Common")], ["0|0|0|0", "0|0|0|0"], "F2 no charm = 0|0|0|0")
    K.eq([sm(FC[t]) for t in range(5)], ["1|10|15|0", "2|20|30|0", "3|30|45|0", "4|40|60|0", "5|50|75|0"], "F2 T1..T5 = the spec numbers")
    K.eq(sm(FC[5]), "5|50|0|1", "F2 Eternal Flame = tier 5, the T5 time, no fuel, eternal 1")
    K.eq(sm(FC[0], FC[3], FC[1]), "4|40|60|0", "F2 the best step in the bag counts")
    D.FC_ON = False
    K.eq(sm(FC[3]), "0|0|0|0", "F2 furnace.on off = 0|0|0|0")
    D.FC_ON = True
    D.FC_TIME, D.FC_FUEL = "5,10,15,20,25", "1,2,3,4,5"
    K.eq(sm(FC[2]), "3|15|3|0", "F2 custom numbers apply at once (the kit's field set)")
    D.FC_TIME, D.FC_FUEL = "5,10,15", "x"
    K.eq(sm(FC[2]), "3|30|45|0", "F2 a bad number line = the built-in numbers")
    D.FC_TIME, D.FC_FUEL = "10,20,30,40,50", "15,30,45,60,75"
    # F3 the bridge on equip / unequip / profile switch
    for iid in FC:
        W.item(iid, 1, 900)
    for m_ in ["Ingredient_Bar_Copper", "Ingredient_Bar_Iron", "Ingredient_Bar_Thorium", "Ingredient_Bar_Lead_SkyWynn", "Ingredient_Bar_Cobalt",
               "Ingredient_Bar_Adamantite", "Ingredient_Bar_Slag_SkyWynn", "Ingredient_Bar_Mithril", "Ingredient_Bar_Titanium_SkyWynn",
               "Ingredient_Bar_Lumen_SkyWynn", "Skyy_Ench_Charcoal"]:
        W.item(m_, 100, 0)      # (Chromium stays unknown until F4's lock check)
    VOID = {"n": {}, "owe": {}, "paused": False, "short": 0, "calls": []}
    _keep = M.void_bridge(W, VOID)
    inv = W.inv(put=[("s", 0, "Ingredient_Bar_Copper", 32), ("s", 1, "Ingredient_Bar_Iron", 20), ("s", 9, FC[1], 1)])
    VOID["n"]["Ingredient_Bar_Iron"] = 12
    p, pr, U = W.player(inv, "Furnace")
    k = str(U)
    key = "acc:smelt:%s" % U

    def sv(want_key=None):
        """the first four fields of acc:smelt; the fifth must be the profile key it was computed for (default: this player's own)"""
        v = str(W.bridge.get(key))
        f = v.split("|")
        if len(f) != 5 or f[4] != (want_key or str(W.KEYS.get(k, k))):
            return "BAD:" + v
        return "|".join(f[:4])
    A.publish(U)
    K.eq(sv(), "0|0|0|0", "F3 a charm in the INVENTORY counts for nothing (only Void Charms)")
    r = str(A.equipK(U, k, FC[0]))
    K.eq((r, sv()), ("", "1|10|15|0"), "F3 equip (a free slot) -> acc:smelt at once (save -> publish)")
    idx = W.bag(U).index(FC[0])
    K.eq((str(A.unequipK(U, k, idx)), sv()), (FC[0], "0|0|0|0"), "F3 unequip -> 0|0|0|0 at once")
    A.putK(U, "prof2", 0, FC[3])
    A.putK(U, k, 0, FC[0])
    K.eq(sv(), "1|10|15|0", "F3 back in")
    W.KEYS[k] = "prof2"
    W.bridge.put("profile:epoch:%s" % U, JObject(2, "java.lang.Long"))
    K.check(bool(A.checkEpoch(U)) and sv() == "4|40|60|0", "F3 a profile switch republishes from the NEW profile's Void Charms: %s" % W.bridge.get(key))
    W.KEYS[k] = k
    W.bridge.put("profile:epoch:%s" % U, JObject(3, "java.lang.Long"))
    K.check(bool(A.checkEpoch(U)) and sv() == "1|10|15|0", "F3 ... and back: %s" % W.bridge.get(key))
    K.check(not A.checkEpoch(U), "F3 no switch = no republish")
    K.check(bool(D.fcChanged()) and not D.fcChanged(), "F3 fcChanged: once true per settings change (the 5 s tick republishes every player then)")
    D.FC_ON = False
    K.check(bool(D.fcChanged()), "F3 ... a Server Setup change is seen")
    D.FC_ON = True
    D.fcChanged()
    # critic fix: the fifth field + smeltNow (join / switch within a second) + removal on leave / shutdown
    K.check(str(W.bridge.get(key)).endswith("|" + k), "F3 the fifth field is the profile key the value is for (here the UUID text): %s" % W.bridge.get(key))
    W.KEYS[k] = "prof2"
    A.smeltNow(U)
    K.check(str(W.bridge.get(key)) == "4|40|60|0|prof2", "F3 smeltNow (the 1 s effect tick): a switch to prof2 is published at once, with its key: %s" % W.bridge.get(key))
    W.KEYS[k] = k
    A.smeltNow(U)
    K.eq(str(W.bridge.get(key)), "1|10|15|0|" + k, "F3 ... and back")
    pj, prj, UJ = W.player(W.inv(), "Joiner")
    kj = "acc:smelt:%s" % UJ
    K.check(W.bridge.get(kj) is None, "F3 a new player has no acc:smelt before the tick")
    A.smeltNow(UJ)
    K.eq(str(W.bridge.get(kj)), "0|0|0|0|%s" % UJ, "F3 the first effect tick after a join publishes 0|0|0|0|<key> (no 5 s wait)")
    on = JClass("java.util.HashSet")()
    on.add(U)
    A.smeltPrune(on)
    K.check(W.bridge.get(kj) is None and W.bridge.get(key) is not None, "F3 smeltPrune (5 s tick): the player who left loses acc:smelt, the online one keeps it")
    A.smeltPrune(None)
    K.check(W.bridge.get(key) is None, "F3 smeltPrune(null) (shutdown): every acc:smelt of ours is removed")
    A.publish(U)
    A.unequipK(U, k, 0)

    # F4 the CRAFT rows
    def view(sub=2):
        rows = []
        for e in C.rowsFor(U, k, p, sub):
            ri = [str(x) for x in C.lineRow(U, k, p, e)]
            rid = C.ridOf(e)
            rows.append((ri[0], ri[6], ri[2], ri[4], None if rid is None else str(rid)))
        return [x for x in rows if x[0].startswith("Skyy_Charm_")]

    def craft(rid):
        return str(C.craft(pr, None, None, p, U, k, rid))

    def charms():
        return sorted([x for x in W.bag(U) if x and x.startswith("Skyy_Charm_")]), sum(W.count(inv, i) for i in FC)
    v = view()
    K.check(len(v) == 1 and v[0][0] == FC[0] and v[0][1] == "c" and v[0][2] == "NORMAL - CAN CRAFT" and v[0][4] == FC[0] + "_Recipe_SkyyCharm",
            "F4 none in Void Charms: the Furnace Charm I CRAFT row in Gathering (Void iron counts): %s" % v)
    K.check(not [x for x in view(0) + view(1)], "F4 ... and in no other sub tab")
    K.check("Copper Ingot" in v[0][3] or "Ingredient Bar Copper" in v[0][3] or "32/32" in v[0][3], "F4 the cost line: %s" % v[0][3])
    s0, b0 = W.slots(inv), W.bag(U)
    r = craft(FC[1] + "_Recipe_SkyyCharm")
    K.check(r == "that row changed - the list is up to date now, nothing was used" and W.slots(inv) == s0 and W.bag(U) == b0, "F4 a click on a step that is not next: nothing used: " + r)
    r = craft(FC[0] + "_Recipe_SkyyCharm")
    K.eq(r, "crafted Furnace Charm I - it went straight into your Void Charms", "F4 T1 crafted")
    K.check(W.count(inv, "Ingredient_Bar_Copper") == 0 and W.count(inv, "Ingredient_Bar_Iron") == 0 and VOID["n"]["Ingredient_Bar_Iron"] == 0
            and VOID["owe"].get("Ingredient_Bar_Iron", 0) == 0 and charms() == ([FC[0]], 1),
            "F4 ... exactly 32 Copper (inventory) + 32 Iron (20 inventory + 12 Void, committed) used; one T1 in Void Charms, the spare T2 in the inventory untouched")
    K.eq(sv(), "1|10|15|0", "F4 ... acc:smelt follows the craft")
    s1, b1 = W.slots(inv), W.bag(U)
    r = craft(FC[0] + "_Recipe_SkyyCharm")
    K.check(r == "that row changed - the list is up to date now, nothing was used" and W.slots(inv) == s1 and W.bag(U) == b1, "F4 a double click: nothing used: " + r)
    v = view()
    K.check(len(v) == 1 and v[0][0] == FC[1] and v[0][1] == "u" and v[0][2].endswith("NEEDS MATERIALS") and "Upgrades your Furnace Charm I" in v[0][3],
            "F4 the row moved on to the T2 UPGRADE (the T2 in the inventory does not count): %s" % v)
    inv.getStorage().setItemStackForSlot(JShort(2), W.IS("Ingredient_Bar_Thorium", 64))
    inv.getStorage().setItemStackForSlot(JShort(3), W.IS("Ingredient_Bar_Lead_SkyWynn", 40))
    VOID["n"]["Ingredient_Bar_Lead_SkyWynn"] = 24
    VOID["short"] = 1
    s2, b2 = W.slots(inv), W.bag(U)
    r = craft(FC[1] + "_Recipe_SkyyCharm")
    K.check(r.startswith("the Void gave") and r.endswith("nothing was used") and W.slots(inv) == s2 and W.bag(U) == b2 and VOID["n"]["Ingredient_Bar_Lead_SkyWynn"] == 24
            and VOID["owe"].get("Ingredient_Bar_Lead_SkyWynn", 0) == 0, "F4 a Void that gives short: everything rolled back (inventory, Void, bag): " + r)
    VOID["short"] = 0
    slot = W.bag(U).index(FC[0])
    r = craft(FC[1] + "_Recipe_SkyyCharm")
    K.eq(r, "upgraded to Furnace Charm II in your Void Charms - your Furnace Charm I was used for it", "F4 T2 upgraded in place")
    K.check(W.bag(U)[slot] == FC[1] and charms() == ([FC[1]], 1) and W.count(inv, FC[1]) == 1 and W.count(inv, "Ingredient_Bar_Thorium") == 0
            and W.count(inv, "Ingredient_Bar_Lead_SkyWynn") == 0 and VOID["n"]["Ingredient_Bar_Lead_SkyWynn"] == 0 and sv() == "2|20|30|0",
            "F4 ... the same slot holds T2, the T1 is gone (no dupe), the spare T2 in the inventory stays (no loss), 64 + 64 used, acc:smelt 2|20|30|0")
    v = view()
    K.check(len(v) == 1 and v[0][0] == FC[2] and v[0][2] == "RARE - LOCKED" and "needs Ingredient Bar Chromium SkyWynn - that item is not on this server" in v[0][3],
            "F4 T3 with Chromium not on this server: LOCKED with the reason: %s" % v)
    inv.getStorage().setItemStackForSlot(JShort(4), W.IS("Ingredient_Bar_Cobalt", 100))
    inv.getStorage().setItemStackForSlot(JShort(5), W.IS("Ingredient_Bar_Cobalt", 28))
    s3, b3 = W.slots(inv), W.bag(U)
    r = craft(FC[2] + "_Recipe_SkyyCharm")
    K.check(r.startswith("Furnace Charm III is locked - needs") and W.slots(inv) == s3 and W.bag(U) == b3, "F4 ... the click refuses, nothing used: " + r)
    W.item("Ingredient_Bar_Chromium_SkyWynn", 100, 0)
    inv.getStorage().setItemStackForSlot(JShort(6), W.IS("Ingredient_Bar_Chromium_SkyWynn", 100))
    inv.getStorage().setItemStackForSlot(JShort(7), W.IS("Ingredient_Bar_Chromium_SkyWynn", 27))
    s4, b4 = W.slots(inv), W.bag(U)
    v = view()
    r = craft(FC[2] + "_Recipe_SkyyCharm")
    K.check(v[0][2] == "RARE - NEEDS MATERIALS" and "127/128" in v[0][3] and r == "not enough materials for Furnace Charm III - nothing was used"
            and W.slots(inv) == s4 and W.bag(U) == b4, "F4 127 of 128 Chromium: NEEDS MATERIALS, the click uses nothing: %s / %s" % (v, r))
    inv.getStorage().setItemStackForSlot(JShort(8), W.IS("Ingredient_Bar_Chromium_SkyWynn", 1))
    r = craft(FC[2] + "_Recipe_SkyyCharm")
    K.check(r.startswith("upgraded to Furnace Charm III") and charms() == ([FC[2]], 1) and W.count(inv, "Ingredient_Bar_Cobalt") == 0
            and W.count(inv, "Ingredient_Bar_Chromium_SkyWynn") == 0 and sv() == "3|30|45|0", "F4 T3 upgraded once the item exists: " + r)
    # F5 Eternal Flame
    A.putK(U, k, W.bag(U).index(FC[2]), FC[4])
    K.eq(sv(), "5|50|75|0", "F5 a T5 in Void Charms (admin put)")
    inv.getStorage().setItemStackForSlot(JShort(10), W.IS("Skyy_Ench_Charcoal", 16))
    inv.getStorage().setItemStackForSlot(JShort(11), W.IS("Ingredient_Bar_Lumen_SkyWynn", 64))
    v = view()
    s5, b5 = W.slots(inv), W.bag(U)
    r = craft(FC[5] + "_Recipe_SkyyCharm")
    K.check(v and v[0][0] == FC[5] and v[0][2] == "LEGENDARY - LOCKED" and "needs the Charcoal collection (SkyyCollections)" in v[0][3]
            and r.startswith("Eternal Flame is locked") and W.slots(inv) == s5 and W.bag(U) == b5, "F5 no SkyyCollections: Eternal Flame locked, nothing used: %s / %s" % (v, r))
    TIER = {"v": 6, "calls": []}

    @JImplements("java.util.function.Function")
    class TierFn(object):
        @JOverride
        def apply(self, a):
            TIER["calls"].append((str(a[0]), str(a[1])))
            return None if TIER["v"] is None else JObject(TIER["v"], "java.lang.Integer")
    tf = TierFn()
    W.bridge.put("coll:fn:tier", tf)
    v = view()
    r = craft(FC[5] + "_Recipe_SkyyCharm")
    K.check("reach Charcoal collection tier 7 to unlock it (you have tier 6)" in v[0][3] and r.startswith("Eternal Flame is locked")
            and W.slots(inv) == s5 and W.bag(U) == b5 and TIER["calls"][-1] == (str(U), "Charcoal"), "F5 Charcoal tier 6 of 7: locked, nothing used: %s" % v[0][3])
    TIER["v"] = None
    K.check("needs the Charcoal collection" in view()[0][3], "F5 SkyyCollections without a Charcoal collection (null): locked")
    TIER["v"] = 7
    v = view()
    r = craft(FC[5] + "_Recipe_SkyyCharm")
    K.check(v[0][2] == "LEGENDARY - CAN UPGRADE" and r == "upgraded to Eternal Flame in your Void Charms - your Furnace Charm V was used for it"
            and charms() == ([FC[5]], 1) and W.count(inv, "Skyy_Ench_Charcoal") == 0 and W.count(inv, "Ingredient_Bar_Lumen_SkyWynn") == 0
            and sv() == "5|50|0|1", "F5 tier 7: Eternal Flame upgraded in place, acc:smelt 5|50|0|1: %s / %s" % (v, r))
    v = view()
    K.check(len(v) == 1 and v[0][1] == "m" and v[0][2] == "LEGENDARY - MAX", "F5 the row says MAX now: %s" % v)
    jr = open(W.LOGF, encoding="utf8").read() if os.path.exists(W.LOGF) else ""
    K.check(jr.count("upgraded in place") == 3 and jr.count("ROLLBACK") == 1 and "LOST" not in jr and "_Recipe_SkyyCharm" in jr,
            "F the journal: 1 craft + 3 in-place upgrades, the one rollback, nothing lost")
    # F6 settings
    pr_ = Props()
    K.eq(str(D.fcLoad(pr_)), "", "F6 an empty file = every default, no complaint")
    K.check(bool(D.FC_ON) and str(D.FC_TIME) == "10,20,30,40,50" and int(D.FC_ETIER) == 7 and str(D.FC_COST2) == "Ingredient_Bar_Thorium:64,Ingredient_Bar_Lead_SkyWynn:64",
            "F6 ... the defaults")
    for k_, v_ in (("furnace.on", "off"), ("furnace.timePct", "1,2,3"), ("furnace.fuelPct", "1,2,3,4,5"), ("furnace.eternalTier", "99"),
                   ("furnace.cost.T1", "Ingredient_Bar_Copper:1"), ("furnace.cost.T2", "Skyy_Charm_Furnace_T1:1,Ingredient_Bar_Iron:2")):
        pr_.setProperty(k_, v_)
    w = str(D.fcLoad(pr_))
    K.check(not D.FC_ON and str(D.FC_TIME) == "10,20,30,40,50" and str(D.FC_FUEL) == "1,2,3,4,5" and int(D.FC_ETIER) == 7
            and str(D.FC_COST1) == "Ingredient_Bar_Copper:1" and str(D.FC_COST2).startswith("Ingredient_Bar_Thorium:64")
            and "furnace.timePct" in w and "furnace.eternalTier" in w and "furnace.cost.T2" in w and "furnace.fuelPct" not in w,
            "F6 good lines apply, bad lines keep the default and are named: %s" % w)
    K.eq([D.fcCheck("furnace.timePct", "10,20,30,40,50"), D.fcCheck("furnace.cost.T3", "Ingredient_Bar_Cobalt:9999")], [None, None], "F6 fcCheck accepts good values")
    bad = [str(D.fcCheck(a, b)) for a, b in (("furnace.timePct", "10,20,30,40,91"), ("furnace.fuelPct", "a,b,c,d,e"), ("furnace.cost.T1", ""),
                                             ("furnace.cost.T1", "Ingredient_Bar_Copper"), ("furnace.cost.T1", "Ingredient_Bar_Copper:0"),
                                             ("furnace.cost.T1", "Ingredient_Bar_Copper:1,Ingredient_Bar_Copper:2"), ("furnace.cost.T1", "Bad id!:3"),
                                             ("furnace.cost.T1", "Skyy_Charm_Furnace_T2:1"))]
    K.check(all(b != "None" for b in bad) and "listed twice" in bad[5] and "taken by itself" in bad[7], "F6 fcCheck refuses with a reason: %s" % bad)
    # the custom T1 cost + furnace.on off on a fresh player
    inv2 = W.inv(put=[("s", 0, "Ingredient_Bar_Copper", 5)])
    p2, pr2, U2 = W.player(inv2, "Furnace2")
    rows2 = [[str(x) for x in C.lineRow(U2, str(U2), p2, e)] for e in C.rowsFor(U2, str(U2), p2, 2)]
    rows2 = [x for x in rows2 if x[0].startswith("Skyy_Charm_")]
    K.check(rows2 and rows2[0][2] == "NORMAL - LOCKED" and "switched off" in rows2[0][4], "F6 furnace.on off: the row is LOCKED: %s" % rows2)
    D.FC_ON = True
    rows2 = [[str(x) for x in C.lineRow(U2, str(U2), p2, e)] for e in C.rowsFor(U2, str(U2), p2, 2)]
    rows2 = [x for x in rows2 if x[0].startswith("Skyy_Charm_")]
    K.check(rows2 and rows2[0][2] == "NORMAL - CAN CRAFT" and "1/1" in rows2[0][4], "F6 a custom cost (1 Copper) rebuilds the recipe: %s" % rows2)
    r = str(C.craft(pr2, None, None, p2, U2, str(U2), FC[0] + "_Recipe_SkyyCharm"))
    K.check(r.startswith("crafted Furnace Charm I") and W.count(inv2, "Ingredient_Bar_Copper") == 4, "F6 ... and crafts with it: " + r)
    D.fcLoad(Props())
    # F7 texts
    s = W.JArray(JClass("java.lang.String"))(2)
    s[0] = FC[2]
    br_ = [str(x) for x in D.bonusRows(s)]
    K.check("Furnace Charm" in br_ and br_[br_.index("Furnace Charm") + 1] == "-30% smelt time in the /craft Furnace, +45% fuel burned - Bronze, Dusk and Azurvane unlocked",
            "F7 the Bonuses row: %s" % br_[:4])
    K.eq(str(Page.effects(FC[5])), "-50% smelt time in the /craft Furnace, no fuel needed - every alloy unlocked", "F7 the grid hover of Eternal Flame")
    ln = [str(x) for x in D.linesText(True)]
    K.check(any(x.startswith("Furnace Charm (/craft Furnace): T1 -10% smelt time") and "Eternal Flame -50%" in x for x in ln)
            and any(FC[5] in x and x.startswith("    ids:") for x in ln), "F7 /charms lines has the charm line + ids")
    K.check(all(Adm.giveable(i) is None for i in FC), "F7 admins may /charms give every step")
    R = W.J("CfgRows")
    keys = [str(x) for x in R.KEYS]
    fk = [x for x in keys if x.startswith("furnace.")]
    K.eq(fk, ["furnace.on", "furnace.timePct", "furnace.fuelPct", "furnace.eternalTier", "furnace.cost.T1", "furnace.cost.T2", "furnace.cost.T3",
              "furnace.cost.T4", "furnace.cost.T5", "furnace.cost.eternal"], "F7 the ten Server Setup rows")
    K.check("Furnace Charm" in [str(x) for x in R.CAT_LABELS] and str(R.TITLE) == "Void Charms", "F7 category Furnace Charm under Void Charms")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["AccCharm", "AccCharmRecipe"],
           phases=[("fassets", run_fassets), ("charm", run_charm), ("power", T22.run_power), ("retire", T22.run_retire), ("rows", T22.run_rows),
                   ("page", T22.run_page), ("client", T23.run_client), ("live", T22.run_live)],
           script=__file__, live=(T22.LIVE_DIR, "Skyy_SkyyAccessories"))
