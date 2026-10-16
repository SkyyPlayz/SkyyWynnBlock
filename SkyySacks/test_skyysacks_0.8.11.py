"""Harness for SkyySacks 0.8.11 (round craft01: THE CRAFTING HUB + CRAFTER LOOK + ADD FUEL + SORT BY TIER + BENCHES USE THE ACCESSORY BAG + VOID
DEPOSIT ALL; tools/sacks_0_8_11_patch.py). Build first:
    python tools/sacks_0_8_11_patch.py && python SkyySacks/build_skyysacks_0.8.11.py
    (and SkyyAccessories 0.5.19: python tools/accessories_0_5_19_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.19.py)

    python SkyySacks/test_skyysacks_0.8.11.py [--keep] [--dir <scratch>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.8.10 -> 0.8.11: exactly the planned members; + AccLink, AccSettle, CraftHubOpen, HubBar; non-class entries = the 59 Sky
                Window files + the Crafting tab icon pair + manifest.json
  NEW  EXECUTED on the 0.8.0 harness's Void stand-ins (real SimpleItemContainers in a stand-in Inventory, a stand-in Item store, a scratch
       pool folder) WITH THE REAL SkyyAccessories 0.5.19 jar (its AccBagFn = acc:fn:bag on the same skyy.bridge, its AccStore on scratch
       bag files), a stand-in Store (CraftRecipeEvent$Pre goes nowhere / can be cancelled) and REAL CraftingRecipe objects:
       TIER  RecipeCmp: tierKey / tierText / sortKey / sortName (tools/tier_tags.py rows, _T<n>, rarities, metal words, untiered 0);
             a farming list sorts tier -> crop, Enchanted crop, seeds, Eternal seeds per crop -> the rest; no craftable-first
       ACC   the Accessory Bag link: list / extras / cont; /craft craftOne of a T2 upgrade whose T1 sits in the BAG (bag -> gone, T2 out,
             copper paid, exactly once; a second click finds no T1 and changes nothing; a cancelled Pre changes nothing); the bench path
             pullFor -> (the vanilla craft, simulated) -> settle: used = nothing back; not used = back in its slot; already in the
             inventory = nothing moved; inventory full = back in the bag + the mark; the bag refuses (T2 equipped meanwhile) = stays in the
             inventory; no SkyyAccessories = nothing; accessories never a Void category
       FUEL  ADD FUEL: fuelsOwned (inventory + Void, most first), procFuelN (more than the mirror offers at once, conserved, the room cap),
             the quick bar = 64; the picker clicks (paddf / pfpick / pfload with a typed amount / a bad amount / pfback / pfcancel) and
             the Furnace view markup (Add fuel button, the picker rows, the amount box)
       DEP   the Void page: DEPOSIT ALL (every category, each up to its space, kept counts cleared, the result line) and the side button
             named after the open category
       HUB   CraftHubOpen.register = hub:tab:smithing:recipes {SkyySacks, Crafting, 5, craft, open, null, smithing_recipes}; removeAll
             removes only ours; HubBar.route answers for the page; the row markup (drawRow) for a craftable and a not-craftable recipe
  D    START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyySacks (0.8.10's run_live10 on this jar)
  AA   engine-access audit
Not testable without the game (UNVERIFIED): the look in game, the bench window showing the bag accessory (the list only), the vanilla
handler running after PreCraftTask with the accessory in the inventory, a real hub click. Exit code 1 on any failure.
"""
import os, sys, json, shutil, importlib.util, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

VERSION = "0.8.11"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-0.8.10.jar")
ACC_JAR = os.path.join(ROOT, "SkyyAccessories", "SkyyAccessories-0.5.19.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "craft01", "sacks")))
PKG = "com.skyy.sacks."
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_10", os.path.join(HERE, "test_skyysacks_0.8.10.py"))
T0810 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T0810)
T089 = T0810.T089
EXPECT = {
    "RecipeCmp": ["+f TT_IDS", "+f TT_TIER", "+f TT_GRP", "+f TT_RANK", "+f LADDER", "+f METAL_W", "+f METAL_T", "+f TTMAP", "+m ttMap",
                  "+m ttIndex", "+m metalTier", "+m suffixTier", "+m tierText", "+<clinit>", "~m tierKey", "~m sortKey", "~m sortName", "~m compare"],
    "CraftPage": ["+f B_PRI", "+f B_SEC", "+f B_TER", "+f B_TERON", "+f B_PRIDIS", "+f B_SECDIS", "+f BG_ROW", "+f BG_ROWDIM", "+f BG_SLOT",
                  "+f BG_PANEL", "+f C_TRACK", "+f C_FILL", "+f L_NAME", "+f L_NAMEDIM", "+f L_HAVE", "+f L_OUT", "+f L_TIER", "+f L_CAP",
                  "+f L_CAPC", "+f L_INFO", "+f L_STAT", "+f L_TEXTC", "+f L_HEAD", "+f L_OUTL", "+f L_TEXT", "+f SEARCH_MK", "+f FUEL_MK",
                  "+f fuelPick", "+f fuelSel", "+f fuelPage", "+f fuelList", "+m btn", "+m lbl", "+m gap", "+m procFuelN", "+m fuelHave",
                  "+m fuelsOwned", "+m drawRow", "+m foot", "+m fuelPicker", "+m viewMatsAcc", "+m craftOne", "+m hubAck", "+m handleProc",
                  "-m handleProc", "~m procFuel", "~m buildTabs", "~m smithNoteText", "~m buildProc", "~m build", "~m handleDataEvent"],
    "SacksPage": ["+f DEPCAT", "+<clinit>", "~m render", "~m onEvent"],
    "BenchLink": ["~m attach", "~m refresh"],
    "LinkRec": ["+f accSig"],
    "SweepTask": ["~m sweep"],
    "PreCraftTask": ["+f rid", "+f qty", "~m run"],
    "CraftInFilter": ["~m test"],
    "SkyySacksPlugin": ["~m setup", "~m shutdown"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],
}
ADDED = ["AccLink", "AccSettle", "CraftHubOpen", "HubBar"]
BETA = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyySacks")
NONCLASS = sorted(list(SUI.kit_texture_files()) + list(SUI.hub_tab_icon_paths("smithing", "recipes")[2:]) + ["manifest.json"])


def run_compare11(out, jar, old_jar, pkg, expect, added, removed=()):
    """harness_kit.run_compare with this round's non-class entries (the kit art + the tab icon pair + manifest.json)"""
    _eq = HK.Child.eq

    def eq(self, got, want, what):
        if what == "C: non-class entries changed":
            want = NONCLASS
        return _eq(self, got, want, what)
    HK.Child.eq = eq
    try:
        return _orig_compare(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        HK.Child.eq = _eq


_orig_compare = HK.run_compare
HK.run_compare = run_compare11


def run_new(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST, ACC_JAR], verify=True)
    src = open(T089.T080, encoding="utf8").read()
    a = src.index("    # ---------------- stand-ins (the 0.7.12+ harness pattern)\n")
    b = src.index("    # ---------------- D. categories\n", a)
    head = ("def run_void_fixture():\n    import jpype\n    import skyybuild as B\n"
            "    from jpype import JClass, JArray, JShort, JString, JInt, JLong, JImplements, JOverride\n"
            "    jp = JClass(\"javassist.ClassPool\")(True)\n    jp.appendClassPath(B.SERVER_JAR)\n    jp.appendClassPath(JAR)\n")
    body = head + src[a:b] + "    _VOID(locals())\n"
    ns = {"__file__": T089.T080, "__name__": "t080"}
    exec(compile(src[:src.index("def run():")], T089.T080, "exec"), ns)
    ns.update(JAR=jar, SCRATCH=os.path.join(scratch, "new"), _VOID=lambda L: new_cases(K, L, scratch))
    exec(compile(body, T089.T080 + " (stand-in slice)", "exec"), ns)
    try:
        ns["run_void_fixture"]()
    finally:
        for f in ns["FAILS"]:
            K.check(False, "NEW fixture: " + f)
        K.save()
        try:
            __import__("jpype").JClass(PKG + "SackPool").WRITER.shutdownNow()
        except Exception:
            pass


def new_cases(K, L, scratch):
    from jpype import JClass, JString, JShort, JArray, JInt, JFloat, JLong
    VS, Defs, Cfg, Pool, Swp = L["VS"], L["Defs"], L["Cfg"], L["Pool"], L["Swp"]
    fresh, player, pc, inv_counts, custom_item, drain, coll = (L[n] for n in ("fresh", "player", "pc", "inv_counts", "custom_item", "drain", "coll"))
    UUID, IS, SIC, bridge, us, jfield, jp, pref, ItemC = (L[n] for n in ("UUID", "IS", "SIC", "bridge", "us", "jfield", "jp", "pref", "ItemC"))
    CtF, CtM, CtC = L["CtF"], L["CtM"], L["CtC"]
    Paths = JClass("java.nio.file.Paths")
    J = lambda n: JClass(PKG + n)
    RC, AL, CP, HB, SPage, PB, PStore = J("RecipeCmp"), J("AccLink"), J("CraftPage"), J("HubBar"), J("SacksPage"), J("ProcBench"), J("ProcStore")
    Obj, Int, Bool = JClass("java.lang.Object"), JClass("java.lang.Integer"), JClass("java.lang.Boolean")
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    CR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    BR = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    CIC = JClass("com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer")
    ICc = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    CRM = JClass("com.hypixel.hytale.builtin.crafting.component.CraftingManager")
    UCBc, UEBc = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    s_ = lambda v: None if v is None else str(v)

    # ---- the stand-in Store: CraftRecipeEvent$Pre (CraftPage.preCraft) goes to no system; CANCEL = every Pre is cancelled
    st_c = jp.makeClass("com.hypixel.hytale.component.SkyyTestCraftStore", jp.get("com.hypixel.hytale.component.Store"))
    st_c.addField(CtF.make("public static boolean CANCEL = false;", st_c))
    st_c.addField(CtF.make("public static int SEEN = 0;", st_c))
    st_c.addConstructor(CtC.make("public SkyyTestCraftStore() { super((com.hypixel.hytale.component.ComponentRegistry) null, 0, (Object) null, "
                                 "(com.hypixel.hytale.component.IResourceStorage) null); }", st_c))
    st_c.addMethod(CtM.make("public void invoke(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.system.EcsEvent e) { SEEN++; "
                            "if (CANCEL && e instanceof com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Pre) "
                            "((com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Pre) e).setCancelled(true); }", st_c))
    TStore = JClass(st_c.toClass(JClass("com.hypixel.hytale.component.Store").class_))
    st = us.allocateInstance(TStore.class_)

    def recipe(rid, out, inputs, qty_out=1):
        ins = JArray(MQ)([MQ(JString(i), None, None, JInt(q), None) for i, q in inputs])
        po = MQ(JString(out), None, None, JInt(qty_out), None)
        r = CR(ins, po, JArray(MQ)([po]), JInt(1), JArray(BR)(0), JFloat(0.0), False, JInt(0))
        jfield(CR.class_, "id").set(r, JString(rid))
        return r

    def page(tab=None):
        pg = us.allocateInstance(CP.class_)
        jfield(CP.class_, "playerRef").set(pg, pref(U))
        jfield(CP.class_, "info").set(pg, JString(""))
        jfield(CP.class_, "query").set(pg, JString(""))
        jfield(CP.class_, "tab").set(pg, None if tab is None else JString(tab))
        return pg

    def ucb_text(b_):
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

    def try_(f):
        try:
            f()
            return None
        except Exception as e:
            st_txt = e.stacktrace() if hasattr(e, "stacktrace") else ""
            return (str(e)[:160] + " @ " + " | ".join(l.strip() for l in str(st_txt).splitlines()[1:6]))[:700]

    U = UUID.fromString("00000000-0000-0000-0000-0000000c0f11")
    k = str(U)
    base = os.path.join(scratch, "new")

    # ============================================================== TIER (RecipeCmp, tools/tier_tags.py at build time)
    tk = lambda i: int(RC.tierKey(JString(i)))
    tt = lambda i: str(RC.tierText(JString(i)))
    K.eq([tk(i) for i in ("Ore_Iron", "Plant_Crop_Wheat_Item", "Plant_Seeds_Onion_Eternal", "Skyy_Ench_Cobalt", "Tool_Pickaxe_Thorium",
                          "Weapon_Sword_Cobalt", "Armor_Mithril_Chest", "Skyy_Accessory_Furnace_T2", "Skyy_Talisman_Speed_Rare", "Ingredient_Fibre",
                          "Skyy_AccessoryBag_Omni", "Tool_Hoe_Crude", "Weapon_Staff_Wood")],
         [3, 2, 8, 5, 4, 5, 7, 2, 3, 0, 99, 1, 1], "TIER: tierKey = the tier_tags display tier / metal word / _T<n> / rarity / untiered 0 / the Omni last")
    K.eq([tt(i) for i in ("Ore_Iron", "Tool_Pickaxe_Thorium", "Weapon_Sword_Cobalt", "Skyy_Accessory_Furnace_T2", "Ingredient_Fibre")],
         ["T3 Iron", "T4 Thorium", "T5 Cobalt", "T2", ""], "TIER: the row's tier tag (the plan's 'T3 Iron' format; own ladders 'T2')")
    farm = ["Plant_Seeds_Wheat_Eternal", "Ingredient_Fibre", "Plant_Crop_Lettuce_Item", "Skyy_Ench_Wheat", "Plant_Seeds_Wheat", "Plant_Crop_Wheat_Item",
            "Tool_Hoe_Crude", "Plant_Crop_Carrot_Item", "Plant_Seeds_Lettuce", "Tool_Hoe_Copper", "Plant_Seeds_Lettuce_Eternal", "Skyy_Ench_Carrot"]
    ent = JClass("java.util.ArrayList")()
    for n_, i in enumerate(farm):
        ent.add(JArray(Obj)([JString(i), Int(5 if n_ % 2 else 0), Int(int(RC.sortKey(JString(i)))), RC.sortName(JString(i))]))
    JClass("java.util.Collections").sort(ent, RC())
    got = [str(e[0]) for e in ent]
    want = ["Ingredient_Fibre", "Tool_Hoe_Crude",
            "Plant_Crop_Lettuce_Item", "Plant_Seeds_Lettuce", "Plant_Seeds_Lettuce_Eternal",
            "Plant_Crop_Wheat_Item", "Skyy_Ench_Wheat", "Plant_Seeds_Wheat", "Plant_Seeds_Wheat_Eternal", "Tool_Hoe_Copper",
            "Plant_Crop_Carrot_Item", "Skyy_Ench_Carrot"]
    K.eq(got, want, "TIER: a farming list = tier, then per crop: crop, Enchanted crop, seeds, Eternal seeds, then the tier's other items "
                    "(craftable or not makes no difference)")

    # ============================================================== ACC (the Accessory Bag link)
    T1, T2, BAR = "Skyy_Accessory_Furnace_T1", "Skyy_Accessory_Furnace_T2", "Ingredient_Bar_Copper"
    for i_ in (T1, T2):
        custom_item(i_, 1)
    custom_item(BAR, 100)
    Store, BagFn = JClass("com.skyy.accessories.AccStore"), JClass("com.skyy.accessories.AccBagFn")
    adir = os.path.join(base, "accbags")
    drain()
    fresh(base)
    os.makedirs(adir, exist_ok=True)
    Store.DIR = Paths.get(adir)
    Store.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyAccessories")
    bridge.put("acc:fn:bag", BagFn())
    up = recipe("Skyy_Accessory_Furnace_T2", T2, [(T1, 1), (BAR, 5)])
    bag = lambda: [x for x in (s_(BagFn().apply(JArray(Obj)(["list", U, k]))) or "").split(",") if x]
    Store.equipK(U, k, JString(T1))
    K.eq(bag(), [T1], "ACC: the bag holds the Furnace Accessory I (real AccStore, scratch file)")
    W = JClass("java.util.HashSet")()
    W.add(JString(T1))
    ex = list(AL.extras(U, k, W))
    K.check(len(ex) == 1 and str(ex[0].itemId) == T1 and int(ex[0].quantity) == 1 and len(list(AL.extras(U, k, JClass("java.util.HashSet")()))) == 0,
            "ACC: the bench display list = the bag accessories its recipes use (T1 x1); none wanted = none shown")
    c_ = AL.cont(AL.list(U, k), W)
    K.check(c_ is not None and int(c_.getCapacity()) == 1 and str(c_.getItemStack(JShort(0)).getItemId()) == T1, "ACC: /craft's copy container = one T1")
    K.check(Defs.homeOf(JString(T1)) is None and Defs.catOf(JString(T1)) is None, "ACC: an accessory is never a Void category (the sweep never takes one)")
    # /craft: craftOne with T1 in the BAG + 5 copper bars in the inventory
    p = player(storage=[(BAR, 5)])
    pg = page("A:art")
    jfield(CP.class_, "tab").set(pg, JString("X:test"))   # not a knowledge-gated tab (KnowSync needs the real player data)
    r1 = str(pg.craftOne(None, st, p, U, k, up, 1, False))
    drain()
    K.check(r1.startswith("crafted 1 x") and "(1 from your Accessory Bag)" in r1 and bag() == [] and inv_counts(p) == {T2: 1},
            "ACC: /craft T2 with T1 in the bag: T1 left the BAG, 5 copper paid, T2 given - exactly once: %r bag %s inv %s" % (r1, bag(), inv_counts(p)))
    r2 = str(pg.craftOne(None, st, p, U, k, up, 1, False))
    K.check(r2 == "not enough materials" and inv_counts(p) == {T2: 1} and bag() == [], "ACC: a second click: no T1 anywhere -> nothing changes (%r)" % r2)
    # a cancelled Pre (another mod refuses): nothing moves
    Store.equipK(U, k, JString(T1))
    p = player(storage=[(BAR, 5)])
    TStore.CANCEL = True
    r3 = str(pg.craftOne(None, st, p, U, k, up, 1, False))
    TStore.CANCEL = False
    K.check(r3 == "this craft was refused - nothing was used" and bag() == [T1] and inv_counts(p) == {BAR: 5}, "ACC: a refused craft: the bag and the inventory unchanged (%r)" % r3)
    # bench: used
    why = JClass("java.lang.StringBuilder")()
    moves = AL.pullFor(p, st, None, U, k, up, 1, why)
    K.check(int(moves.size()) == 1 and bag() == [] and inv_counts(p) == {BAR: 5, T1: 1} and why.length() == 0,
            "BENCH: before the vanilla handler T1 moves bag -> inventory (counted): moves %d bag %s inv %s" % (int(moves.size()), bag(), inv_counts(p)))
    inv = p.getInventory().getCombinedBackpackStorageHotbar()
    ins = CRM.getInputMaterials(up, 1)
    K.check(bool(inv.canRemoveMaterials(ins)), "BENCH: the vanilla check (inventory only) now passes")
    inv.removeMaterials(ins)
    p.getInventory().getStorage().addItemStack(IS(T2, 1))
    K.eq(int(AL.settle(p, st, None, U, k, moves)), 0, "BENCH: settle after a craft that USED it: nothing goes back")
    K.check(bag() == [] and inv_counts(p) == {T2: 1}, "BENCH: T1 used exactly once (bag empty, inventory = T2): %s %s" % (bag(), inv_counts(p)))
    # bench: not used (the craft failed)
    Store.equipK(U, k, JString(T1))
    p = player(storage=[(BAR, 2)])
    moves = AL.pullFor(p, st, None, U, k, up, 1, why)
    f0 = os.path.join(adir, k + ".properties")
    K.check(int(moves.size()) == 1 and inv_counts(p).get(T1) == 1, "BENCH: moved for a craft that will fail (2 of 5 bars)")
    K.check(int(AL.settle(p, st, None, U, k, moves)) == 1 and bag() == [T1] and inv_counts(p) == {BAR: 2} and "slot0=" + T1 in open(f0, encoding="latin-1").read(),
            "BENCH: settle after a craft that did NOT use it: T1 back in its bag slot, gone from the inventory")
    # bench: already in the inventory -> nothing moved
    p = player(storage=[(BAR, 5), (T1, 1)])
    K.check(int(AL.pullFor(p, st, None, U, k, up, 1, why).size()) == 0 and bag() == [T1], "BENCH: a T1 in the inventory already -> the bag one stays")
    # bench: inventory full -> back into the bag + the mark
    p = player(storage=[("Rock_Stone_Cobble", 100)] * 36, hotbar=[("Rock_Stone_Cobble", 100)] * 9, backpack=[("Rock_Stone_Cobble", 100)] * 9)
    why2 = JClass("java.lang.StringBuilder")()
    mv = AL.pullFor(p, st, None, U, k, up, 1, why2)
    K.check(int(mv.size()) == 0 and why2.length() > 0 and bag() == [T1] and T1 not in inv_counts(p), "BENCH: inventory full -> T1 stays in the bag, the player is told")
    # bench: the bag refuses the way back (T2 equipped meanwhile) -> it stays in the inventory
    p = player(storage=[(BAR, 1)])
    moves = AL.pullFor(p, st, None, U, k, up, 1, why)
    Store.equipK(U, k, JString(T2))
    K.check(int(AL.settle(p, st, None, U, k, moves)) == 0 and inv_counts(p).get(T1) == 1 and bag() == [T2],
            "BENCH: the bag refuses T1 (T2 of its line is in now) -> T1 stays in the inventory (never lost)")
    # review fix B2: the bag lists T1 but refuses the take (changed meanwhile) -> nothing is used at all
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class LiarBag(object):
        @JOverride
        def apply(self, a):
            op = str(a[0])
            if op == "list":
                return JString(T1)
            if op == "take":
                return Int(-1)
            return Bool.FALSE
    realfn = bridge.get("acc:fn:bag")
    bridge.put("acc:fn:bag", LiarBag())
    pl_ = player(storage=[(BAR, 5)])
    r4 = str(pg.craftOne(None, st, pl_, U, k, up, 1, False))
    bridge.put("acc:fn:bag", realfn)
    K.check(r4 == "your Accessory Bag changed - nothing was used" and inv_counts(pl_) == {BAR: 5},
            "ACC (fix B2): a take refused BEFORE the removal -> nothing used, no item paid out (%r %s)" % (r4, inv_counts(pl_)))
    # review fix A5: the need summed per id (a recipe listing T1 twice needs 2; the bag has 1 -> 1 moved); a resource-type-only want shows nothing
    Store.BAGS.clear()
    for f_ in os.listdir(adir):
        os.remove(os.path.join(adir, f_))
    Store.BAGS.clear()
    Store.equipK(U, k, JString(T1))
    twice = recipe("Skyy_Test_Twice", T2, [(T1, 1), (T1, 1)])
    pl_ = player()
    mv5 = AL.pullFor(pl_, st, None, U, k, twice, 1, why)
    K.check(int(mv5.size()) == 1 and inv_counts(pl_) == {T1: 1} and bag() == [], "BENCH (fix A5): T1 twice in a recipe = need 2, the bag's one moved once")
    AL.settle(pl_, st, None, U, k, mv5)
    K.check(bag() == [T1], "BENCH (fix A5): ... and back")
    W2 = JClass("java.util.HashSet")()
    W2.add(JString("Fuel"))
    K.check(len(list(AL.extras(U, k, W2))) == 0 and AL.cont(AL.list(U, k), W2) is None, "ACC (fix A5): only exact item-id inputs show / count")
    K.eq(str(AL.sig(U, k)), T1, "ACC (fix B1): the bag signature = its list")
    # no SkyyAccessories 0.5.19
    fnk = bridge.remove("acc:fn:bag")
    K.check(len(list(AL.list(U, k))) == 0 and len(list(AL.extras(U, k, W))) == 0 and AL.cont(AL.list(U, k), W) is None
            and int(AL.pullFor(player(), st, None, U, k, up, 1, why).size()) == 0, "ACC: without acc:fn:bag nothing is shown or moved")
    bridge.put("acc:fn:bag", fnk)
    K.check(len(list(AL.list(U, "someone-else"))) == 0, "ACC: another profile's key -> the bag is not read")

    # ============================================================== FUEL (ADD FUEL)
    STICK, PLANK = "Ingredient_Stick", "Wood_Oak_Planks"
    IRT = JClass("com.hypixel.hytale.protocol.ItemResourceType")
    for i_ in (STICK, PLANK):
        it_ = custom_item(i_, 64)
        jfield(ItemC.class_, "resourceTypes").set(it_, JArray(IRT)([IRT(JString("Fuel"), JInt(1))]))
        jfield(ItemC.class_, "fuelQuality").setDouble(it_, 1.0)
    fl = JClass("java.util.ArrayList")()
    fl.add(JString(PLANK))
    fl.add(JString(STICK))
    jfield(PB.class_, "FUELS").set(None, fl)
    drain()
    pdir = fresh(base)
    L["write_pool"](pdir, k, {STICK: 1000})
    coll(U, {"Foraging": 100000})
    p = player(storage=[(STICK, 30), (PLANK, 50)])
    own = [(str(e[0]), int(e[1].longValue())) for e in CP.fuelsOwned(p, k)]
    K.eq(own, [(STICK, 1030), (PLANK, 50)], "FUEL: the picker list = every fuel you own (inventory + the Void), most first")
    r = str(CP.procFuelN(p, st, None, k, "Furnace", STICK, 500))
    drain()
    fb = PStore.of(k, JString("Furnace"))
    left = inv_counts(p).get(STICK, 0) + pc(k).get(STICK, 0)
    K.check(r.startswith("loaded 500 ") and int(fb.fuelCount()) == 500 and left == 530,
            "FUEL: Load 500 sticks (more than the mirror's 4 stacks): 500 in the fuel slot, 530 left - conserved (%r, inv+Void %d)" % (r, left))
    r = str(CP.procFuelN(p, st, None, k, "Furnace", STICK, 5000))
    drain()
    K.check(int(fb.fuelCount()) == int(PB.FUEL_CAP) and "loaded %d " % (int(PB.FUEL_CAP) - 500) in r, "FUEL: asking more than fits -> the room left (%r)" % r)
    r = str(CP.procFuelN(p, st, None, k, "Furnace", STICK, 10))
    K.check(r.startswith("the fuel slot is full"), "FUEL: a full fuel slot -> nothing taken (%r)" % r)
    fb.unloadFuel()
    fb.takeOut(JString(STICK), JInt(int(PB.FUEL_CAP)))
    before = inv_counts(p).get(PLANK, 0)
    r = str(CP.procFuel(p, st, None, k, "Furnace", PLANK))
    K.check(r.startswith("loaded 50 ") and inv_counts(p).get(PLANK, 0) == before - 50, "FUEL: the quick-load bar still loads one press (up to 64): %r" % r)
    # the picker clicks (handleProc; the rebuild() inside cannot run without a client - the state + the result line are checked)
    Pool.add(k, JString(STICK), JLong(1000))
    p.getInventory().getStorage().addItemStack(IS(PLANK, 40))
    pgf = page("P:Furnace")
    hp = lambda data, act: try_(lambda: pgf.handleProc(None, st, p, U, k, JString(data), JString(act)))
    hp('{"a":"paddf"}', "paddf")
    K.check(bool(pgf.fuelPick) and pgf.fuelSel is None, "FUEL: Add fuel opens the picker")
    bp, ep = UCBc(), UEBc()
    err = try_(lambda: pgf.fuelPicker(bp, ep, p, k, "Furnace", fb))
    t_ = ucb_text(bp)
    K.check(err is None and "SkyyPFPick0" in t_ and "SkyyPFPick1" in t_ and "Pick a fuel - most first" in t_ and list(pgf.fuelList)[:2] == [STICK, PLANK],
            "FUEL: the picker rows: sticks first, then planks, each with Pick (%s)" % err)
    hp('{"a":"pfpick:0"}', "pfpick:0")
    K.check(str(pgf.fuelSel) == STICK, "FUEL: Pick -> the amount step for sticks")
    bp = UCBc()
    pgf.fuelPicker(bp, UEBc(), p, k, "Furnace", fb)
    t_ = ucb_text(bp)
    K.check("SkyyCFuelAmt" in t_ and "SkyyPFLoad" in t_ and "Room in the fuel slot" in t_, "FUEL: the amount step: the amount box + Load + what you have / the room")
    f0_ = int(fb.fuelCount())
    hp('{"a":"pfload","@FuelAmt":"abc"}', "pfload")
    K.check("type a number" in str(pgf.info) and int(fb.fuelCount()) == f0_, "FUEL: a bad amount -> refused, nothing loaded")
    hp('{"a":"pfload","@FuelAmt":"120"}', "pfload")
    drain()
    K.check(int(fb.fuelCount()) == f0_ + 120 and str(pgf.info).startswith("loaded 120 ") and not bool(pgf.fuelPick), "FUEL: typed 120 -> 120 loaded, the picker closes (%s)" % pgf.info)
    hp('{"a":"paddf"}', "paddf")
    hp('{"a":"pfpick:0"}', "pfpick:0")
    hp('{"a":"pfback"}', "pfback")
    K.check(bool(pgf.fuelPick) and pgf.fuelSel is None, "FUEL: Back -> the list again")
    hp('{"a":"pfcancel"}', "pfcancel")
    K.check(not bool(pgf.fuelPick), "FUEL: Cancel closes the picker")
    hp('{"a":"paddf"}', "paddf")
    hp('{"a":"pfpick:1"}', "pfpick:1")
    hp('{"a":"pfload","@FuelAmt":""}', "pfload")
    K.check(str(pgf.info).startswith("loaded ") and inv_counts(p).get(PLANK, 0) == 0, "FUEL: an empty amount = all that fits (every plank): %s" % pgf.info)
    # the Furnace view: Add fuel next to the quick bar (buildProc on the stand-ins; the bench has no tier here = no recipes)
    bb = UCBc()
    pgf.fuelPick = False
    jfield(PB.class_, "needsFuel").setBoolean(PStore.get(k, JString("Furnace")), True)   # the stand-in has no BlockType store: say it burns fuel
    p.getInventory().getStorage().addItemStack(IS(PLANK, 20))
    bridge.remove("acc:has:" + k)   # the bag published a Furnace accessory above: no bench tier here = no recipe scan (no recipe store in this JVM)
    err = try_(lambda: pgf.buildProc(bb, UEBc(), p, U, k))
    t_ = ucb_text(bb)
    K.check(err is None and "SkyyPStat" in t_ and "SkyyPCollect" in t_ and "SkyyCNav" in t_, "FUEL: the Furnace view builds (%s)" % err)
    K.check("SkyyPFuelRow" in t_ and "SkyyPAddF" in t_ and "Add fuel" in t_ and "SkyyPFuel0" in t_ and "SkyyPUnload" in t_
            and t_.index("SkyyPFuel0") < t_.index("SkyyPAddF"), "FUEL: the fuel row = the quick-load bar (kept) + Add fuel; Unload fuel next to Collect")
    bb2 = UCBc()
    pgf.fuelPick = True
    err2 = try_(lambda: pgf.buildProc(bb2, UEBc(), p, U, k))
    t2_ = ucb_text(bb2)
    K.check(err2 is None and "SkyyPFPick0" in t2_ and "SkyyCRow" not in t2_, "FUEL: with the picker open the Furnace view shows the fuel list instead of the recipe rows (%s)" % err2)
    gen = open(os.path.join(HERE, "build_skyysacks_%s.py" % VERSION), encoding="utf8").read()
    bp_ = gen[gen.index("public void buildProc("):]
    bp_ = bp_[:bp_.index('}"""), cpg))')]
    K.check(bp_.index("SkyyPFuel\" + sI") < bp_.index("SkyyPAddF") and "fuelPicker(b, ev, p, k, bench, view)" in bp_,
            "FUEL: (source) the quick-load buttons come first, then Add fuel; the picker replaces the recipe rows")

    # ============================================================== DEP (the Void page: DEPOSIT ALL = every bag)
    drain()
    fresh(base)
    coll(U, {"Mining": 0, "Foraging": 0, "Farming": 0})
    pP = player(storage=[("Ore_Copper", 50), ("Wood_Oak_Trunk", 40), ("Plant_Crop_Wheat_Item", 30), ("Ingredient_Bar_Iron", 7), (T1, 1)])
    sp = us.allocateInstance(SPage.class_)
    jfield(SPage.class_, "playerRef").set(sp, pref(U))
    jfield(SPage.class_, "info").set(sp, JString(""))
    jfield(SPage.class_, "amount").set(sp, JString(""))
    jfield(SPage.class_, "cat").set(sp, JString("Mining"))
    try_(lambda: sp.onEvent(None, None, pP, JString('{"a":"depevery"}')))
    drain()
    after = pc(k)
    info = str(jfield(SPage.class_, "info").get(sp) or "")
    K.check(after.get("Ore_Copper") == 50 and after.get("Wood_Oak_Trunk") == 40 and after.get("Plant_Crop_Wheat_Item") == 30 and after.get("Ingredient_Bar_Iron") == 7
            and inv_counts(pP) == {T1: 1} and info.startswith("+Deposited 127 items into 4 bags"),
            "DEP: Deposit all on the Mining tab puts EVERY category in (Mining, Foraging, Farming, Smithing); the accessory stays: %s %r" % (after, info))
    drain()
    fresh(base)
    coll(U, {"Mining": 0})
    old_pl = int(Cfg.PD_PER_LEVEL)
    Cfg.PD_PER_LEVEL = 20
    pP = player(storage=[("Ore_Copper", 50), ("Wood_Oak_Trunk", 10)])
    try_(lambda: sp.onEvent(None, None, pP, JString('{"a":"depevery"}')))
    drain()
    Cfg.PD_PER_LEVEL = old_pl
    K.check(pc(k).get("Ore_Copper") == 20 and pc(k).get("Wood_Oak_Trunk") == 10 and inv_counts(pP) == {"Ore_Copper": 30},
            "DEP: each bag only up to its own space (Mining 20 of 50 copper, the logs all in): %s %s" % (pc(k), inv_counts(pP)))
    bd = UCBc()
    jfield(SPage.class_, "cat").set(sp, JString("Smithing"))
    err = try_(lambda: sp.render(bd, UEBc(), pP, k, U))
    t_ = ucb_text(bd)
    K.check(err is None and "SkyyVDepEvery" in t_ and "Deposit all" in t_ and "Deposit Smithing" in t_ and t_.index("SkyyVDepEvery") < t_.index("SkyyVCraft")
            and t_.index("SkyyVCraft") < t_.index("SkyyVDepAll"), "DEP: the page: DEPOSIT ALL at the top (before Craft); the side button says Deposit Smithing (%s)" % err)
    gen_dep = gen[gen.index('if (a.equals("depevery")) {'):]
    gen_dep = gen_dep[:gen_dep.index("rebuild();")]
    K.check("for (int c = 0; c < cats.length; c++) @PKG@.SackPool.clearKeptCat(k, cats[c]);" in gen_dep and "sweep(player, k, (String) null, true" in gen_dep,
            "DEP: (source) every category's kept counts cleared, then ONE sweep with no category")

    # review fix A4: a stack with extra data is never swept (DEPOSIT ALL leaves it); a plain one of the same item goes in
    drain()
    fresh(base)
    coll(U, {"Mining": 0})
    BDc = JClass("org.bson.BsonDocument")
    md_ = BDc()
    md_.put("SkyyTest", JClass("org.bson.BsonString")("x"))
    pA = player(storage=[("Ore_Copper", 5)])
    pA.getInventory().getStorage().addItemStack(IS(JString("Ore_Copper"), JInt(3), md_))
    try_(lambda: sp.onEvent(None, None, pA, JString('{"a":"depevery"}')))
    drain()
    K.check(pc(k).get("Ore_Copper") == 5 and inv_counts(pA) == {"Ore_Copper": 3}, "DEP (fix A4): the 3 copper with extra data stay, the 5 plain ones go in (%s %s)" % (pc(k), inv_counts(pA)))
    # the other fixes, in the generated source
    K.check("AccLink.sig(u, k).equals(rec.accSig" in gen and "rec.accSig = @PKG@.AccLink.sig(u, m.key);" in gen and "@PKG@.AccLink.touch(p);" in gen,
            "FIX B1 (source): the bench link refreshes on a bag change (signature) and after a put-back")
    sk_ = gen[gen.index("public static int sortKey(String id) {"):]
    sk_ = sk_[:sk_.index("}")]
    K.check("level(" not in sk_, "FIX B4 (source): the sort key is tier (+ the crop grouping) only - then the name")
    as_ = gen[gen.index("public static int benchPre("):]
    as_ = as_[:as_.index("}" + "'" * 3)]
    K.check("SCHEDULED_EXECUTOR.schedule(as, 250L" in as_ and "moved from the bag to the inventory:" in as_, "FIX A1 + A2 (source): the settle goes scheduler -> world thread; the move is logged with its ids")
    K.check('"A:smith", "Gear"' in gen and 'get("acc:fn:bag") instanceof java.util.function.Function) ? "Materials come from your inventory, the Void and your Accessory Bag' in gen,
            "FIX B5 + B6 (source): the crafter's gear tab is Gear; the Accessory Bag is named only while acc:fn:bag runs")

    # ============================================================== HUB
    K.eq(int(J("CraftHubOpen").register()), 1, "HUB: CraftHubOpen.register puts one tab")
    e_ = bridge.get("hub:tab:smithing:recipes")
    K.check(e_ is not None and [s_(x) for x in list(e_)[:4]] == ["SkyySacks", "Crafting", "5", "craft"] and e_[4] is not None and e_[5] is None
            and s_(e_[6]) == "smithing_recipes", "HUB: hub:tab:smithing:recipes = {SkyySacks, Crafting, 5, craft, open, null, smithing_recipes}: %s" % [s_(x) for x in list(e_ or [])])
    K.check(not bool(e_[4].apply(U)), "HUB: the open Function for a player who is not online -> FALSE (the bar then runs /craft)")
    pr_ = pref(U)
    K.eq([s_(HB.route(pr_, JString('{"a":"hub:recipes"}'), "smithing", "recipes")), s_(HB.route(pr_, JString('{"a":"hub:close"}'), "smithing", "recipes")),
          s_(HB.route(pr_, JString('{"a":"craft:0:1"}'), "smithing", "recipes")), s_(HB.route(pr_, JString('{"a":"hub:h:smithing"}'), "smithing", "recipes"))],
         ["self", "close", None, "self"], "HUB: route: its own tab = self, the X = close, a page click = not a hub click, its own hub in row 1 = self")
    other = JArray(Obj)(["SkyyMenu", "Crafting", Int(5), "craft", None, None])
    bridge.put("hub:tab:smithing:gear", other)
    K.check(int(HB.removeAll()) >= 1 and bridge.get("hub:tab:smithing:recipes") is None and bridge.get("hub:tab:smithing:gear") is not None,
            "HUB: removeAll (shutdown) removes our tab only")
    # the row markup (drawRow) for a craftable and a not-craftable recipe
    p = player(storage=[(BAR, 9)])
    pgr = page("A:craft")
    br_, er_ = UCBc(), UEBc()
    m_ = CIC(JArray(ICc)([p.getInventory().getCombinedBackpackStorageHotbar()]))
    plain = recipe("Skyy_Test_Iron", "Ore_Iron", [(BAR, 3), ("Ore_Copper", 2)])
    err = try_(lambda: (pgr.drawRow(br_, er_, 0, plain, m_, 0, "", 0, False, ""), pgr.drawRow(br_, er_, 1, up, m_, 1, "", 1, False, "")))
    t_ = ucb_text(br_)
    K.check(err is None and "SkyyCRow0" in t_ and "SkyyCRow1" in t_ and "SkyyCC0x0" in t_ and "SkyyCC1x1" in t_ and "T3 Iron" in t_ and "SkyyKit/Row.png" in t_
            and "SkyyKit/PanelInset.png" in t_ and "Disabled" in t_ and "_" not in "".join(x for x in t_.split() if x.startswith("#")),
            "HUB: drawRow: a slot frame + name + tier tag + one chip per input; the not-craftable row dimmed and its buttons Disabled; ids without '_' (%s)" % err)
    evs = str(er_.getEvents() if hasattr(er_, "getEvents") else "")
    K.notes.append("HUB: drawRow event builder %s" % evs[:80])
    drain()


if __name__ == "__main__":
    assert os.path.isfile(ACC_JAR), "build SkyyAccessories 0.5.19 first: " + ACC_JAR
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("new", run_new), ("live", T0810.run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
