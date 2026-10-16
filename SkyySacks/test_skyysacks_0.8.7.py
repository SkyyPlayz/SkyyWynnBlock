"""Harness for SkyySacks 0.8.7 (/craft ARTIFACTS TAB; tools/sacks_0_8_7_patch.py).
Build first: python tools/sacks_0_8_7_patch.py && python SkyySacks/build_skyysacks_0.8.7.py

    python SkyySacks/test_skyysacks_0.8.7.py [--keep] [--dir <scratch>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.8.6 -> 0.8.7: CraftPage (+ ACCDEFSRC / ACCDEFS / accDefIds / artifactId / artifact, buildTabs, recipesFor, build) + the
              version texts only
  X / L / SND / D   the 0.8.6 harness's exec, late (+ its /craft CraftRecipeEvent$Pre cases), sound and live phases on the 0.8.7 jar
  ART NEW: the 0.8.4 REAL Store fixture (reused verbatim, as the 0.8.6 late phase does) + a stand-in CraftingRecipe store with the engine's
              own CraftingRecipe / MaterialQuantity / BenchRequirement; a player with Workbench / Weaponbench / Farmingbench T1 accessories:
                recipesFor("A:art") = exactly the accessory recipes (Skyy_Talisman_*, Skyy_Accessory_Bag, Skyy_Accessory_<Bench>_T<n>, a
                Farmingbench talisman, an acc:defs-only id); Crafting / Smithing / Farming hold none of them and keep their own; a
                bench tier above the accessory / a timed (Furnace) talisman stay out; the Lantern (KnowledgeRequired) only when known;
                acc:defs parsed per published value (a new value re-read, none = prefixes only); buildTabs = Crafting, Artifacts,
                Smithing, Farming; search finds artifacts + the rest; handleDataEvent: the tab click opens Artifacts, a Craft click
                on an Artifacts row pays from the inventory and hands the talisman out, All crafts what is left, a knowledge recipe
                not known is refused with nothing used, a cancelling CraftRecipeEvent$Pre listener refuses with nothing used;
                static: the search texts name Artifacts, Artifacts is the 2nd tab, the first tab row fits the page
  AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.8.7"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-0.8.6.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sacks087", "sacks")))
PKG = "com.skyy.sacks."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySacks")
EXPECT = {
    "CraftPage": ["+f ACCDEFSRC", "+f ACCDEFS", "+m accDefIds", "+m artifactId", "+m artifact", "~<clinit>", "~m buildTabs", "~m recipesFor", "~m build"],
    "SkyySacksPlugin": ["~m setup"],    # the ready line's version
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~m header"],
}
ADDED = []


def _t086():
    sp = importlib.util.spec_from_file_location("t086", os.path.join(HERE, "test_skyysacks_0.8.6.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    m.VERSION = VERSION   # its static checks (and the 0.8.5 module it loads) read the 0.8.7 generated script
    return m


def run_exec(out, jar, scratch, home):
    _t086().run_exec(out, jar, scratch, home)


def run_late(out, jar, scratch, home):
    _t086().run_late(out, jar, scratch, home)


def run_snd(out, jar, scratch, home):
    _t086().run_snd(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    _t086().run_live(out, jar, scratch, home)


def run_art(out, jar, scratch, home):
    m = _t086()
    ns, src = m.ns084()
    a = src.index("def run_exec(")
    b = src.index(m.BLOCK_MARK, a)
    body = src[a:b].replace("def run_exec(", "def run_art_fixture(", 1) + "    _ART(locals())\n    K.save()\n"
    mark = "    st = REG.addStore("
    assert body.count(mark) == 1
    body = body.replace(mark, "    _PRE(locals())\n" + mark, 1)   # the 0.8.6 CraftRecipeEvent$Pre stand-in, registered before the stores
    ns["_PRE"], ns["_ART"] = m.pre_system, lambda L: art_cases(L, m.PRE)
    exec(compile(body, m.T084 + " (fixture slice)", "exec"), ns)
    ns["run_art_fixture"](out, jar, scratch, home)


def art_cases(L, PRE):
    from jpype import JClass, JArray, JString, JShort, JInt, JFloat
    K, st, jfield, IS, SIC, cnt, us, bridge = L["K"], L["st"], L["jfield"], L["IS"], L["SIC"], L["cnt"], L["us"], L["bridge"]
    jp, CtF, CtM, CtC, ItemC, KMap, Pool = L["jp"], L["CtF"], L["CtM"], L["CtC"], L["ItemC"], L["KMap"], L["Pool"]
    player, T_PLA, T_PR, fm, astore = L["player"], L["T_PLA"], L["T_PR"], L["fm"], L["astore"]
    C = PRE["C"]
    Page = JClass(PKG + "CraftPage")
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    BR = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    BT = JClass("com.hypixel.hytale.protocol.BenchType")
    DAM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    FCC = JClass("com.hypixel.hytale.server.core.asset.type.item.config.FieldcraftCategory")
    HMap, HSet, AList = JClass("java.util.HashMap"), JClass("java.util.HashSet"), JClass("java.util.ArrayList")

    # ---- the stand-in recipe store (the 0.7.17 harness pattern): CraftingRecipe.ASSET_STORE -> a DefaultAssetMap of our recipes,
    # FieldcraftCategory.ASSET_MAP empty (so craftSet = the bench recipes up to the accessory tier)
    rmap = HMap()
    rstore = us.allocateInstance(astore.getClass())
    fm.set(rstore, DAM(rmap))
    jfield(CRR.class_, "ASSET_STORE").set(None, rstore)
    jfield(FCC.class_, "ASSET_MAP").set(None, DAM(HMap()))

    def item(iid, mx=100):
        it_ = ItemC(JString(iid))
        jfield(ItemC.class_, "maxStack").setInt(it_, mx)
        KMap.CUSTOM.put(JString(iid), it_)

    def mq(iid, q):
        return MQ(JString(iid), None, None, JInt(q), None)

    def recipe(rid, out, ins, bench="Workbench", tier=1, btype="Crafting", know=False):
        item(out, 1 if out.startswith(("Skyy_Talisman_", "Skyy_Acc", "Weapon_")) else 100)
        ia = JArray(MQ)([mq(i, q) for i, q in ins])
        po = mq(out, 1)
        br = JArray(BR)([BR(BT.valueOf(btype), JString(bench), None, JInt(tier), None)])
        r_ = CRR(ia, po, JArray(MQ)([po]), JInt(1), br, JFloat(0.0), know, JInt(0))
        jfield(CRR.class_, "id").set(r_, JString(rid))
        rmap.put(JString(rid), r_)
        return r_
    CU = "Ore_Copper"
    R = {}
    R["plank"] = recipe("T_Plank", "Ingredient_Test_Plank", [(CU, 1)])
    R["reg"] = recipe("T_TalReg", "Skyy_Talisman_Regeneration_Common", [(CU, 2)])
    R["lan"] = recipe("T_TalLan", "Skyy_Talisman_Lantern_Common", [(CU, 1)], know=True)
    R["bag"] = recipe("T_AccBag", "Skyy_Accessory_Bag", [(CU, 1)])
    R["accwb"] = recipe("T_AccWb", "Skyy_Accessory_Workbench_T2", [(CU, 1)])
    R["charm"] = recipe("T_Charm", "Skyy_Test_Charm", [(CU, 1)])                   # an artifact only through acc:defs
    R["feather"] = recipe("T_FarmTal", "Skyy_Talisman_Feather_T1", [(CU, 1)], "Farmingbench")
    R["seed"] = recipe("T_Seed", "Ingredient_Test_Seed", [(CU, 1)], "Farmingbench")
    R["sword"] = recipe("T_Sword", "Weapon_Sword_Test", [(CU, 1)], "Weaponbench")
    R["crit2"] = recipe("T_TalT3", "Skyy_Talisman_Crit_T2", [(CU, 1)], "Workbench", 3)   # bench tier 3 > the accessory's 1
    R["furn"] = recipe("T_TalFurn", "Skyy_Talisman_Defense_T1", [(CU, 1)], "Furnace", 1, "Processing")   # timed: never instant
    R["pick"] = recipe("T_TalPick", "Skyy_Talisman_Pickaxe_Test", [(CU, 1)])         # the Pre stand-in cancels any *Pickaxe* output
    Page.BENCHIDS = None

    U, RF = player(st, "Arti", (80.5, 64.0, 80.5))
    k = str(U)
    bridge.put("acc:has:" + k, JString("Skyy_Accessory_Workbench_T1,Skyy_Accessory_Weaponbench_T1,Skyy_Accessory_Farmingbench_T1"))
    bridge.remove("acc:defs")
    pg = None
    try:
        pg = Page(st.getComponent(RF, T_PR), JString("A:craft"))
    except Exception as e:   # noqa
        K.notes.append("ART: CraftPage constructor not runnable in the bare JVM (%s) - allocated instead" % str(e)[:120])
        pg = us.allocateInstance(Page.class_)
        jfield(Page.class_, "playerRef").set(pg, st.getComponent(RF, T_PR))
        pg.tab, pg.info, pg.query = "A:craft", "", ""
    pg.known = HSet()
    pg.coll = HSet()

    def outs(lst):
        return sorted(str(r.getPrimaryOutput().getItemId()) for r in lst)
    ART = ["Skyy_Accessory_Bag", "Skyy_Accessory_Workbench_T2", "Skyy_Talisman_Feather_T1", "Skyy_Talisman_Pickaxe_Test",
           "Skyy_Talisman_Regeneration_Common"]
    K.eq(outs(pg.recipesFor("A:art", U)), ART, "ART: the Artifacts tab = every accessory recipe the player's benches reach (talismans, the "
         "Accessory Bag, a bench accessory, a Farmingbench talisman); not the tier-3 one, not the timed Furnace one, not the unknown Lantern")
    K.eq(outs(pg.recipesFor("A:craft", U)), ["Ingredient_Test_Plank", "Skyy_Test_Charm"], "ART: Crafting keeps its own recipes, no accessory")
    K.eq(outs(pg.recipesFor("A:smith", U)), ["Weapon_Sword_Test"], "ART: Smithing unchanged")
    K.eq(outs(pg.recipesFor("A:farm", U)), ["Ingredient_Test_Seed"], "ART: Farming keeps its seed; the Farmingbench talisman moved to Artifacts")
    # acc:defs (SkyyAccessories' own list) adds ids the prefixes miss; parsed per published value
    bridge.put("acc:defs", JString("Vitality:Skyy_Talisman_Vitality:1:Skyy_Talisman_Vitality_T1:Normal:10:Craft,Charm:Skyy_Test_Charm:2:Skyy_Test_Charm:Unique:13:Craft,bad"))
    K.check("Skyy_Test_Charm" in outs(pg.recipesFor("A:art", U)) and outs(pg.recipesFor("A:craft", U)) == ["Ingredient_Test_Plank"],
            "ART: an id SkyyAccessories lists in acc:defs moves to Artifacts (a short / bad record ignored)")
    K.check(bool(Page.artifactId("Skyy_Talisman_Vitality_T1")) and not bool(Page.artifactId("Ingredient_Test_Plank")) and not bool(Page.artifactId(None)),
            "ART: artifactId - listed / prefixed yes, plain item / null no")
    bridge.put("acc:defs", JString("X:Y:1:Skyy_Other_Thing:Normal:10:Craft"))
    K.check("Skyy_Test_Charm" not in outs(pg.recipesFor("A:art", U)) and bool(Page.artifactId("Skyy_Other_Thing")),
            "ART: a NEW acc:defs value is read again (the old list dropped)")
    bridge.remove("acc:defs")
    K.check(not bool(Page.artifactId("Skyy_Other_Thing")) and bool(Page.artifactId("Skyy_Accessory_Omni")),
            "ART: no acc:defs (SkyyAccessories absent) -> the Skyy_Talisman_ / Skyy_Acc prefixes only")
    # the Lantern line: KnowledgeRequired (SkyyAccessories' Tree Sap gate) - shown only once known
    pg.known = HSet()
    pg.known.add("Skyy_Talisman_Lantern_Common")
    K.check("Skyy_Talisman_Lantern_Common" in outs(pg.recipesFor("A:art", U)) and "Skyy_Talisman_Lantern_Common" not in outs(pg.recipesFor("A:craft", U)),
            "ART: the Lantern recipe shows on Artifacts once known (Tree Sap gate), never on Crafting")
    pg.known = HSet()
    # search: the whole merged set, artifacts included
    K.eq(outs(pg.searchRecipes(U, "talisman")), ["Skyy_Talisman_Feather_T1", "Skyy_Talisman_Pickaxe_Test", "Skyy_Talisman_Regeneration_Common"],
         "ART: search 'talisman' finds the artifacts (unknown Lantern / tier-3 / timed still out)")
    K.eq(outs(pg.searchRecipes(U, "test")), sorted(["Ingredient_Test_Plank", "Ingredient_Test_Seed", "Skyy_Test_Charm", "Weapon_Sword_Test",
                                                     "Skyy_Talisman_Pickaxe_Test"]), "ART: search covers Crafting, Artifacts, Smithing and Farming")
    # the tab row
    tabs = pg.buildTabs(None, U, k)
    labels = [str(t[1]) for t in tabs]
    K.eq(labels[:4], ["Crafting", "Artifacts", "Smithing", "Farming"], "ART: the tab row reads Crafting, Artifacts, Smithing, Farming")
    K.eq([str(t[0]) for t in tabs][1], "A:art", "ART: the Artifacts tab id is A:art (an A: tab - search row, unlock click check)")

    # ---- handleDataEvent on the REAL store: tab click + crafting from the Artifacts tab
    INVN = "com.hypixel.hytale.server.core.inventory.Inventory"
    ICN = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
    CICN = "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer"
    tinv = jp.makeClass("com.hypixel.hytale.server.core.inventory.SkyyTestInv", jp.get(INVN))
    for f in ("s", "h", "b"):
        tinv.addField(CtF.make("public %s %s;" % (ICN, f), tinv))
    tinv.addConstructor(CtC.make("public SkyyTestInv(%s s, %s h, %s b) { super(); this.s = s; this.h = h; this.b = b; }" % (ICN, ICN, ICN), tinv))
    for m_, f in (("getStorage", "s"), ("getHotbar", "h"), ("getBackpack", "b")):
        tinv.addMethod(CtM.make("public %s %s() { return this.%s; }" % (ICN, m_, f), tinv))
    for m_, order in (("getCombinedBackpackStorageHotbar", "this.b, this.s, this.h"), ("getCombinedStorageHotbarBackpack", "this.s, this.h, this.b")):
        tinv.addMethod(CtM.make("public %s %s() { return new %s(new %s[] { %s }); }" % (CICN, m_, CICN, ICN, order), tinv))
    TInv = JClass(tinv.toClass(JClass(INVN).class_))
    sto, hot, bp = SIC(JShort(9)), SIC(JShort(9)), SIC(JShort(9))
    sto.addItemStack(IS(CU, 5))
    pla = st.getComponent(RF, T_PLA)
    jfield(pla.getClass(), "inventory").set(pla, TInv(sto, hot, bp))
    allinv = lambda: cnt(sto)
    pg.tabs = tabs
    pg.handleDataEvent(RF, st, JString('{"a":"tab:1"}'))
    K.eq((str(pg.tab), str(pg.query)), ("A:art", ""), "ART: clicking the 2nd tab opens Artifacts")
    pg.key = Pool.settledKey(U)
    pg.rows = AList()
    pg.rows.add(R["reg"])
    pg.info = ""
    pg.handleDataEvent(RF, st, JString('{"a":"craft:0:1"}'))
    K.check(allinv() == {CU: 3, "Skyy_Talisman_Regeneration_Common": 1} and str(pg.info).startswith("crafted 1 x"),
            "ART: Craft on an Artifacts row pays 2 copper from the inventory and hands the talisman out: %s / %r" % (allinv(), str(pg.info)))
    pg.handleDataEvent(RF, st, JString('{"a":"craft:0:0"}'))
    K.check(allinv() == {CU: 1, "Skyy_Talisman_Regeneration_Common": 2} and str(pg.info).startswith("crafted 1 x"),
            "ART: All crafts what the materials allow (1 more), nothing else: %s / %r" % (allinv(), str(pg.info)))
    pg.handleDataEvent(RF, st, JString('{"a":"craft:0:10"}'))
    K.check(allinv() == {CU: 1, "Skyy_Talisman_Regeneration_Common": 2} and str(pg.info) == "not enough materials",
            "ART: x10 with 1 copper left -> not enough materials, nothing used: %s / %r" % (allinv(), str(pg.info)))
    sto.addItemStack(IS(CU, 4))
    pg.rows = AList()
    pg.rows.add(R["lan"])
    pg.handleDataEvent(RF, st, JString('{"a":"craft:0:1"}'))
    K.check(allinv() == {CU: 5, "Skyy_Talisman_Regeneration_Common": 2} and str(pg.info) == "You have not unlocked this recipe",
            "ART: the Lantern (knowledge not known at click time) is refused, nothing used: %s / %r" % (allinv(), str(pg.info)))
    pg.rows = AList()
    pg.rows.add(R["pick"])
    C.ON = True
    pg.handleDataEvent(RF, st, JString('{"a":"craft:0:1"}'))
    C.ON = False
    K.check(allinv() == {CU: 5, "Skyy_Talisman_Regeneration_Common": 2} and str(pg.info) == "this craft was refused - nothing was used",
            "ART: a cancelling CraftRecipeEvent$Pre listener refuses an Artifacts craft, nothing used (0.8.6 veto): %s / %r" % (allinv(), str(pg.info)))
    pg.handleDataEvent(RF, st, JString('{"a":"craft:0:1"}'))
    K.check(allinv() == {CU: 4, "Skyy_Talisman_Regeneration_Common": 2, "Skyy_Talisman_Pickaxe_Test": 1},
            "ART: the same click with the listener off crafts: %s" % allinv())
    K.eq(int(Page.limit(R["reg"], sto)), 2, "ART: the row limit (Craftable only / All N) counts the Artifacts recipe like any other")

    # ---- static: texts + the tab row width
    gen = open(os.path.join(HERE, "build_skyysacks_%s.py" % VERSION), encoding="utf8").read()
    K.check('" found in Crafting, Artifacts, Smithing and Farming"' in gen and '"  searches Crafting, Artifacts, Smithing and Farming"' in gen
            and '" in Crafting, Artifacts, Smithing or Farming."' in gen and "found in Crafting, Smithing and Farming" not in gen,
            "ART: the search row texts name Artifacts")
    b_ = gen[gen.index("public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{"):]
    K.check("int cap = tabRow == 0 ? 6 : 8;" in b_ and "Anchor: (Width: 150, Height: 32); Text: \\\\\"< Back to the Void" in b_
            and "TextButton #SkyyCTab\" + i + \" {{ Anchor: (Width: 110, Height: 32)" in b_ and "Anchor: (Width: 1000, Height: 830)" in b_,
            "ART: tab row layout unchanged (6 tabs on row 1: 150 + 14 + 6 x 116 = 860 <= 968 inner width; the rest wrap)")
    Pool.WRITER.shutdownNow()   # the fixture's writer thread - else the JVM never exits


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("exec", run_exec), ("late", run_late), ("art", run_art), ("snd", run_snd), ("live", run_live)], __file__,
           live=(LIVE_DIR, "Skyy_SkyySacks"))
