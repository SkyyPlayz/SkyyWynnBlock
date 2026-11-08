"""Harness for SkyySacks 0.8.37 (round sk837 - tools/sacks_0_8_37_patch.py: ingots first on the Furnace tab; Skyy "filter ingots to the top, in order of tier").
Build first:
    python tools/sacks_0_8_37_patch.py && python SkyySacks/build_skyysacks_0.8.37.py

    python SkyySacks/test_skyysacks_0.8.37.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A / C   verify (-Xverify:all) + compare 0.8.36 -> 0.8.37 (RecipeCmp's new members, CraftPage.buildProc and the version lines only: compare and the instant tabs' build are byte-identical)
  F37     KEYS   ingotOf / furnaceKey / furnaceName on every real bar + all 18 Enchanted metals; the whole ladder in tier order, each Enchanted right after its plain ingot
          ORDER  the REAL CraftPage.buildProc on P:Furnace with a mixed list, in a shuffled input order; non-ingots in today's order below the ingots
          LOCK   greyed alloys keep their place with and without the charm; Craftable only; a recipe with no output; rowOf on the new order
          TANNERY the REAL buildProc on P:Tannery: the same list in the old order
  S36 / BC36 / ALL35   the 0.8.36 and 0.8.35 cases on THIS jar (regression)
  D       start twice on a scratch COPY of NewBetaTest's Skyy_SkyySacks: no migration, no byte changed
NOT COVERED (UNVERIFIED in game): how the client draws the list; real display names (the harness has no language table, so names fall back to the id).
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyench as EN
import tier_tags as TT

_argv = list(sys.argv)
_RC = HK.run_compare
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_36", os.path.join(HERE, "test_skyysacks_0.8.36.py"))
T36 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T36)
sys.argv = _argv
HK.run_compare = _RC
T35, T089, T30, BETA = T36.T35, T36.T089, T36.T30, T36.BETA

VERSION = "0.8.37"
OLD_VERSION = "0.8.36"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
T30.OLD_JAR = OLD_JAR
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sk837", "sacks")))
PKG = "com.skyy.sacks."
EXPECT = {"SkyySacksPlugin": ["~m setup"], "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],
          "RecipeCmp": ["+f ING_BASE", "+f ING_ENCH", "+m furnaceKey", "+m furnaceName", "+m ingotOf", "~<clinit>"],
          "CraftPage": ["~m buildProc"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
BARS = ["Ingredient_Bar_" + w for w in ("Copper", "Iron", "Bronze", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium", "Gold", "Silver", "Prisma")] + \
       ["Ingredient_Bar_%s_SkyWynn" % w for w in ("Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen", "Electrum")]
TABLE = [t for t in list(EN.TABLE) + list(EN.TABLE_ALLOYS) if t[2].startswith("Ingredient_Bar_")]
PAIRS = [(EN.PREFIX + t[0], t[2]) for t in TABLE]
MC, MI, MB, ML = "Ingredient_Bar_Copper", "Ingredient_Bar_Iron", "Ingredient_Bar_Bronze", "Ingredient_Bar_Lead_SkyWynn"
ME, MS, MG, MP, MT = "Ingredient_Bar_Electrum_SkyWynn", "Ingredient_Bar_Silver", "Ingredient_Bar_Gold", "Ingredient_Bar_Prisma", "Ingredient_Bar_Thorium"
XC, XI, XB, XS = "Skyy_Ench_Copper", "Skyy_Ench_Iron", "Skyy_Ench_Bronze", "Skyy_Ench_Silver"
OTHERS = ["Rock_Basalt", "Potion_Empty", "Rock_Marble", "Soil_Clay_Raw_Brick", "Ore_Iron", "Skyy_Ench_Cobblestone", "Ingredient_Charcoal"]
INGOTS_WANT = [MC, XC, MI, XI, MB, XB, ME, MT, ML, MG, MP, MS, XS]
ORE = "Ore_Copper"


def cases37(K, L, scratch):
    from jpype import JClass, JString, JArray, JInt, JFloat
    Defs, Pool = L["Defs"], L["Pool"]
    fresh, write_pool, player, custom_item, drain = (L[n] for n in ("fresh", "write_pool", "player", "custom_item", "drain"))
    UUID, bridge, us, jfield, jp, pref = (L[n] for n in ("UUID", "bridge", "us", "jfield", "jp", "pref"))
    CtF, CtM = L["CtF"], L["CtM"]
    J = lambda n: JClass(PKG + n)
    RC, CP, PS, VS = J("RecipeCmp"), J("CraftPage"), J("ProcStore"), L["VS"]
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    CRc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    BR = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    UCBc, UEBc = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Paths, AL, Bool = JClass("java.nio.file.Paths"), JClass("java.util.ArrayList"), JClass("java.lang.Boolean")

    # ================================================= KEYS
    def ingot(i):
        v = RC.ingotOf(None if i is None else JString(i))
        return None if v is None else str(v)

    K.eq([ingot(None), ingot("Rock_Basalt"), ingot("Skyy_Ench_Cobblestone"), ingot("Skyy_Ench_Charcoal"), ingot("Skyy_Ench_Nothing"), ingot("Ingredient_Charcoal")], [None] * 6, "KEYS not ingots: null, a rock, Enchanted non-metals, an unknown Enchanted id, Charcoal")
    K.eq([ingot(b) for b in BARS], BARS, "KEYS every real bar is its own ingot")
    K.check(len(PAIRS) == 18 and all(ingot(e) == b for e, b in PAIRS), "KEYS all 18 Enchanted metals (alloys too) name their plain bar")
    K.eq([int(RC.furnaceKey(JString(i))) == int(RC.sortKey(JString(i))) and str(RC.furnaceName(JString(i))) == str(RC.sortName(JString(i))) for i in OTHERS], [True] * len(OTHERS), "KEYS a non-ingot keeps sortKey + sortName exactly")
    K.check(int(RC.furnaceKey(None)) == int(RC.sortKey(None)) and str(RC.furnaceName(None)) == "", "KEYS a null id does not throw")
    allids = BARS + [e for e, b in PAIRS]
    fk = lambda i: int(RC.furnaceKey(JString(i)))
    K.check(all(fk(i) < 0 for i in allids) and all(int(RC.sortKey(JString(i))) >= 0 for i in allids + OTHERS), "KEYS every ingot key is below every sortKey (no other row can get between)")
    order = sorted(allids, key=lambda i: (fk(i), str(RC.furnaceName(JString(i)))))
    tiered = [i for i in order if int(RC.tierKey(JString(ingot(i)))) > 0]
    tiers = [int(RC.tierKey(JString(ingot(i)))) for i in tiered]
    K.check(tiers == sorted(tiers) and tiers[0] == 1 and tiers[-1] == 16, "KEYS the whole ladder runs T1 .. T16: %s" % tiers)
    K.eq(order[-5:], [MG, "Skyy_Ench_Gold", MP, MS, "Skyy_Ench_Silver"], "KEYS Gold, Prisma, Silver (no tier) after every tiered ingot, each Enchanted beside its plain")
    apart = [e for e, b in PAIRS if b in order and order.index(e) != order.index(b) + 1]
    K.check(not apart, "KEYS each Enchanted metal sits directly after its plain ingot (apart: %s)" % apart)
    K.check(sum(1 for i in order if i.startswith(EN.PREFIX)) == 18 and len(set(order)) == len(BARS) + 18, "KEYS nothing lost in the sort")

    # ================================================= the REAL buildProc
    tc = jp.makeClass(PKG + "TestCP37", jp.get(PKG + "CraftPage"))
    tc.addField(CtF.make("public static java.util.ArrayList LIST = new java.util.ArrayList();", tc))
    tc.addMethod(CtM.make("public java.util.ArrayList recipesFor(String tabId, java.util.UUID u) { return LIST; }", tc))
    from jpype import JClass as _JC
    ctor = _JC("javassist.CtNewConstructor").make("public TestCP37() { super((com.hypixel.hytale.server.core.universe.PlayerRef) null, \"\"); }", tc)
    tc.addConstructor(ctor)
    TP = JClass(tc.toClass(CP.class_))

    for i_ in BARS + [e for e, b in PAIRS] + OTHERS + [ORE]:
        custom_item(i_, 100)
    U = UUID.fromString("00000000-0000-0000-0000-0000000f0937")
    k = str(U)
    base = os.path.join(scratch, "f37")
    d = os.path.join(scratch, "f37proc")
    os.makedirs(d, exist_ok=True)

    def mk():
        drain()
        fresh(base)
        PS.DIR = Paths.get(d)
        bridge.put(JString("coll:recipes:" + k), JString(""))
        bridge.put(JString("acc:has:" + k), JString("Skyy_Accessory_Furnace_T1,Skyy_Accessory_Tannery_T1"))
        write_pool(os.path.join(base, "pools"), k, {ORE: 500})
        VS.st(k).first = 1

    def recipe(out):
        mi = JArray(MQ)([MQ(JString(ORE), None, None, JInt(1), None)])
        po = MQ(JString(out), None, None, JInt(1), None)
        req = JArray(BR)(0)
        if out in (MB, ME):   # a real alloy: the SkyyAlloy requirement buildProc greys without the Furnace Charm
            b_ = BR()
            b_.id = JString("SkyyAlloy")
            b_.requiredTierLevel = 1
            req = JArray(BR)([b_])
        r = CRc(mi, po, JArray(MQ)([po]), JInt(1), req, JFloat(0.0), False, JInt(0))
        jfield(CRc.class_, "id").set(r, JString("Skyy_Test37_" + out))
        return r

    def no_output(rid):
        mi = JArray(MQ)([MQ(JString(ORE), None, None, JInt(1), None)])
        r = CRc(mi, None, JArray(MQ)(0), JInt(1), JArray(BR)(0), JFloat(0.0), False, JInt(0))
        jfield(CRc.class_, "id").set(r, JString(rid))
        return r

    def page(tab, recipes):
        pg = us.allocateInstance(TP.class_)
        for n_, v_ in (("info", JString("")), ("query", JString("")), ("tab", JString(tab))):
            jfield(CP.class_, n_).set(pg, v_)
        jfield(CP.class_, "playerRef").set(pg, pref(U))
        TP.LIST = AL()
        for r in recipes:
            TP.LIST.add(r)
        return pg

    def text(b_):
        out_ = []
        for c_ in b_.getCommands():
            k_ = c_.getClass()
            while k_ is not None:
                for f_ in k_.getDeclaredFields():
                    if JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()):
                        continue
                    f_.setAccessible(True)
                    v_ = f_.get(c_)
                    if v_ is not None:
                        out_.append(str(v_))
                k_ = k_.getSuperclass()
        return "\n".join(out_)

    def show(tab, recipes):
        pg = page(tab, recipes)
        b_, e_ = UCBc(), UEBc()
        pg.buildProc(b_, e_, player(storage=[]), U, JString(k))
        rows = [str(r.getPrimaryOutput().getItemId()) if r.getPrimaryOutput() is not None else "NOOUT:" + str(r.getId()) for r in list(jfield(CP.class_, "rows").get(pg))]
        return pg, rows, text(b_)

    def old_order(ids):
        return sorted(ids, key=lambda i: (int(RC.sortKey(JString(i))), str(RC.sortName(JString(i)))))

    # shuffled on purpose: the non-ingots first, the ingots back to front
    MIXED = OTHERS + list(reversed(INGOTS_WANT))
    recipes = [recipe(i) for i in MIXED]
    mk()
    pg, rows, tx = show("P:Furnace", recipes)
    K.eq(rows[:len(INGOTS_WANT)], INGOTS_WANT, "ORDER ingots first, by tier, plain then Enchanted, ties by name, then the untiered ingots")
    K.eq(rows[len(INGOTS_WANT):], old_order(OTHERS), "ORDER every other recipe below them, in today's order")
    K.eq(len(rows), len(MIXED), "ORDER nothing dropped")
    K.check(rows[0] == MC and rows[1] == XC and rows.index("Rock_Basalt") > rows.index(XS), "ORDER Skyy's screenshot: Basalt no longer above the ingots")
    pg2, rows2, _t = show("P:Furnace", list(reversed(recipes)))
    K.eq(rows2, rows, "ORDER the same list from any input order")
    K.eq([str(r.getPrimaryOutput().getItemId()) for r in [pg.rowOf(JString("%d:1:%s" % (i, "Skyy_Test37_" + rows[i]))) for i in (0, 3, len(rows) - 1)]], [rows[0], rows[3], rows[-1]], "ORDER rowOf finds the recipe at its new place (a click queues the row you see)")

    # ================================================= LOCK
    K.check(tx.count("unlocks this") == 2, "LOCK no charm: Bronze and Electrum are greyed with the charm note (%d)" % tx.count("unlocks this"))
    pool_key = str(Pool.pkey(U))
    bridge.put(JString("acc:smelt:" + k), JString("5|100|100|0|" + pool_key))
    _pgU, rowsU, txU = show("P:Furnace", recipes)
    K.eq(rowsU, rows, "LOCK a greyed alloy keeps its place: the same order with the Furnace Charm on")
    K.check("unlocks this" not in txU, "LOCK the charm really opened them (no lock note this time)")
    bridge.remove(JString("acc:smelt:" + k))
    # Craftable only: the locked alloys go, the rest keep the order
    J("CraftPage").ONLY.put(U, Bool.TRUE)
    _pgO, rowsO, _tO = show("P:Furnace", recipes)
    J("CraftPage").ONLY.remove(U)
    K.check(MB not in rowsO and len(rowsO) < len(rows) and rowsO == [i for i in rows if i in rowsO], "LOCK Craftable only hides the locked rows, the rest keep their order: %s" % rowsO[:6])
    # a recipe with no primary output whose id looks like a bar: not an ingot
    nout = no_output("Ingredient_Bar_Fake37")
    _pgN, rowsN, _tN = show("P:Furnace", [recipe(MC), recipe("Rock_Basalt"), nout])
    K.eq(rowsN[0], MC, "LOCK no primary output: a real ingot still first")
    K.check(rowsN.index("NOOUT:Ingredient_Bar_Fake37") > 0 and int(RC.furnaceKey(JString(MC))) < 0, "LOCK no primary output: never counted as an ingot (%s)" % rowsN)
    K.eq(rowsN[1:], [str(x) if x != "Ingredient_Bar_Fake37" else "NOOUT:Ingredient_Bar_Fake37" for x in old_order(["Rock_Basalt", "Ingredient_Bar_Fake37"])], "LOCK no primary output: keeps today's place among the others")

    # ================================================= TANNERY
    _pgT, rowsT, _tT = show("P:Tannery", recipes)
    K.eq(rowsT, old_order(MIXED), "TANNERY the same recipes in today's tier-then-name order (no ingots first)")
    K.check(rowsT != rows and rowsT[0] != MC, "TANNERY really differs from the Furnace list (first row: %s)" % rowsT[0])
    K.notes.append("Furnace order: " + ", ".join(rows))
    K.notes.append("Tannery order: " + ", ".join(rowsT))


def run_f37(out, jar, scratch, home):
    T089.void_cases = cases37
    T089.run_void(out, jar, scratch, home)


if __name__ == "__main__":
    os.makedirs(SCRATCH, exist_ok=True)
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [],
           [("f37", run_f37), ("s36", T36.run_s36), ("all35", T35.run_all35), ("bc36", T36.run_bc36), ("live", T30.T0827.run_live27), ("live2", T30.T0827.T0810.run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
