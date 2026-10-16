"""Harness for SkyySacks 0.8.14 (round sacks0814: every Enchanted item has its Void home, Greater Essence of Life instead of the Enchanted one,
the bigger scrolling /craft list, no accessory recipe in /craft; tools/sacks_0_8_14_patch.py). Build first:
    python tools/sacks_0_8_14_patch.py && python SkyySacks/build_skyysacks_0.8.14.py

    python SkyySacks/test_skyysacks_0.8.14.py [--keep] [--dir <folder inside tools/dev/scratch/>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.8.13 -> 0.8.14: exactly the planned members (SackDefs.enchCat, RecipeCmp's tier table, CraftPage's list / row / tabs /
                filters, VoidStore.upgrade + SacksPage.upgradeBox, WbTab's tab text); non-class entries: manifest.json + server.lang (only
                the two Workbench tab name lines removed - SkyyAccessories, the owner, writes them)
  NEW  EXECUTED on the 0.8.0 harness's Void stand-ins (real SimpleItemContainers in a stand-in Inventory, a stand-in Item store, a scratch
       pool folder) and REAL CraftingRecipe objects:
       HOME  every tools/skyyench.py row (102) -> its category through enchCat / homeOf / catOf; the retired Skyy_Ench_LifeEssence -> none;
             vanilla Greater Essence of Life -> Farming
       DEP   the Void page DEPOSIT ALL with C1 Enchanted items of all five categories + Greater Essence: each in its home, the retired id stays
             in the inventory; DEPOSIT <category> (Combat) takes only that category's Enchanted item
       UPG   the Void upgrade at Lv 1 (old gate 10): items missing -> refused; every item -> Unique, exactly the cost paid; no 'Needs Lv' line
       TIER  RecipeCmp: Enchanted Corn = Corn's tier, grouped crop -> Enchanted crop -> seeds -> Eternal seeds
       LIST  the scrolling list: listOpen (TopScrolling, the vanilla scrollbar, the height = the body minus what is above), 12 bigger rows
             (drawRow: 92 high, 22 px names, 17 px costs) INSIDE #SkyyCList, the foot without a pager (pages 0) and with one (the fuel
             picker), listMore after MAXROWS
       SIZE  few rows -> larger rows that all fit (Skyy "if there are only a few items try to scale them to all fit."): rowSize by count,
             a 168-high row with 32 px names / 140 px icon, buttons centred
       CRAFT a craft of the 12th row (place 11 = page 2 in 0.8.13) through craftOne: materials paid, output given
       ART   artifact() for accessory outputs; buildTabs has no Artifacts tab; (source) every /craft list + search skip artifact() recipes
  D    START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyySacks (0.8.10's run_live10 on this jar)
  AA   engine-access audit
Not testable without the game (UNVERIFIED): the look in game, the scroll wheel / bar, the scroll position after a click (a rebuild starts
at the top again, as SkyyCollections' lists). Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import skyyench as EN

VERSION = "0.8.14"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-0.8.13.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sacks0814", "h")))
PKG = "com.skyy.sacks."
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_10", os.path.join(HERE, "test_skyysacks_0.8.10.py"))
T0810 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T0810)
T089 = T0810.T089
EXPECT = {
    "SackDefs": ["~m enchCat"],
    "VoidStore": ["~m upgrade"], "SacksPage": ["~m upgradeBox"], "CfgRows": ["~<clinit>", "~m header"],   # the pd.gate rows' text
    "WbTab": ["~m start"],                                              # tools/skyywbtab.py TAB_TEXT "Bags"                                         # tools/skyyench.py live: 102 rows
    "RecipeCmp": ["~<clinit>"],                                         # tools/tier_tags.py live: the C1 Enchanted rows
    "CraftPage": ["+f L_NAMEB", "+f L_NAMEDIMB", "+f L_TIERB", "+f L_HAVEB", "+f L_OUTB", "+f L_CAPB", "+f LIST_A", "+f LIST_B",
                  "+f BODYH", "+f MAXROWS", "+f usedH", "+m listH", "+m listOpen", "+m listMore",
                  "+f L_NAME2", "+f L_NAMEDIM2", "+f L_TIER2", "+f L_HAVE2", "+f L_OUT2", "+f L_CAP2", "+f L_NAME3", "+f L_NAMEDIM3",
                  "+f L_TIER3", "+f L_HAVE3", "+f L_OUT3", "+f L_CAP3", "+f ROWHS", "+f rowSz", "+m rowSize", "+m pick3", "+m pickI", "~<clinit>",
                  "+m rowOf", "~m handleProc", "~m handleDataEvent",
                  "~m drawRow", "~m foot", "~m build", "~m buildProc", "~m buildTabs", "~m recipesFor", "~m searchRecipes"],
    "SkyySacksPlugin": ["~m setup"], "CfgFn": ["~m opExport"],
}
ADDED = []
NONCLASS = ["Server/Languages/en-US/server.lang", "manifest.json"]   # server.lang: the two Workbench tab name lines gone (Accessories owns them)


def run_compare14(out, jar, old_jar, pkg, expect, added, removed=()):
    """harness_kit.run_compare with this round's non-class entries + the server.lang diff = exactly the two tab lines"""
    import zipfile
    _eq = HK.Child.eq

    def eq(self, got, want, what):
        if what == "C: non-class entries changed":
            want = NONCLASS
            la = zipfile.ZipFile(old_jar).read(NONCLASS[0]).decode("utf8").splitlines()
            lb = zipfile.ZipFile(jar).read(NONCLASS[0]).decode("utf8").splitlines()
            self.eq(sorted(set(la) - set(lb)), sorted(["benchCategories.workbench.skyyaccessories=Accessories & Bags",
                    "server.benchCategories.workbench.skyyaccessories=Accessories & Bags"]), "C: server.lang lost only the Workbench tab name lines")
            self.eq(sorted(set(lb) - set(la)), [], "C: server.lang gained nothing (SkyyAccessories owns the tab name)")
        return _eq(self, got, want, what)
    HK.Child.eq = eq
    try:
        return _orig_compare(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        HK.Child.eq = _eq


_orig_compare = HK.run_compare
HK.run_compare = run_compare14
BETA = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyySacks")


def run_new(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
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
    from jpype import JClass, JString, JArray, JInt, JFloat
    Defs, Cfg = L["Defs"], L["Cfg"]
    fresh, player, pc, inv_counts, custom_item, drain, coll = (L[n] for n in ("fresh", "player", "pc", "inv_counts", "custom_item", "drain", "coll"))
    UUID, us, jfield, pref, bridge = (L[n] for n in ("UUID", "us", "jfield", "pref", "bridge"))
    CtF, CtM, CtC, jp = L["CtF"], L["CtM"], L["CtC"], L["jp"]
    J = lambda n: JClass(PKG + n)
    RC, CP, SPage = J("RecipeCmp"), J("CraftPage"), J("SacksPage")
    Obj, Int = JClass("java.lang.Object"), JClass("java.lang.Integer")
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    CR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    BR = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    CIC = JClass("com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer")
    ICc = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    UCBc, UEBc = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    s_ = lambda v: None if v is None else str(v)

    st_c = jp.makeClass("com.hypixel.hytale.component.SkyyTestCraftStore14", jp.get("com.hypixel.hytale.component.Store"))
    st_c.addConstructor(CtC.make("public SkyyTestCraftStore14() { super((com.hypixel.hytale.component.ComponentRegistry) null, 0, (Object) null, "
                                 "(com.hypixel.hytale.component.IResourceStorage) null); }", st_c))
    st_c.addMethod(CtM.make("public void invoke(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.system.EcsEvent e) { }", st_c))
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

    def dump(b_, getter="getCommands"):
        out_ = []
        for c_ in getattr(b_, getter)():
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

    U = UUID.fromString("00000000-0000-0000-0000-0000000c0f14")
    k = str(U)
    base = os.path.join(scratch, "new")

    # ============================================================== HOME (tools/skyyench.py, live)
    bad = [(t[0], s_(Defs.enchCat(JString(EN.PREFIX + t[0]))), s_(Defs.homeOf(JString(EN.PREFIX + t[0]))), s_(Defs.catOf(JString(EN.PREFIX + t[0]))))
           for t in EN.TABLE if not (s_(Defs.enchCat(JString(EN.PREFIX + t[0]))) == s_(Defs.homeOf(JString(EN.PREFIX + t[0])))
                                     == s_(Defs.catOf(JString(EN.PREFIX + t[0]))) == t[5])]
    K.check(len(EN.TABLE) == 102 and not bad, "HOME: all %d tools/skyyench.py rows -> their category (enchCat = homeOf = catOf): bad %s" % (len(EN.TABLE), bad[:5]))
    cats = sorted(set(t[5] for t in EN.TABLE))
    K.eq(cats, ["Combat", "Farming", "Foraging", "Mining", "Smithing"], "HOME: the rows use all five categories (Combat / Smithing homes too)")
    K.check(Defs.enchCat(JString("Skyy_Ench_LifeEssence")) is None and Defs.homeOf(JString("Skyy_Ench_LifeEssence")) is None,
            "HOME: the retired Skyy_Ench_LifeEssence has no Void home (Skyy: use the vanilla version)")
    K.check(s_(Defs.homeOf(JString("Ingredient_Life_Essence_Concentrated"))) == "Farming" and s_(Defs.catOf(JString("Ingredient_Life_Essence_Concentrated"))) == "Farming"
            and s_(Defs.homeOf(JString("Ingredient_Life_Essence"))) == "Farming", "HOME: vanilla Greater Essence of Life (and Essence of Life) -> Farming")
    K.check(Defs.enchCat(JString("Skyy_Ench_NoSuch")) is None, "HOME: an unknown Enchanted id has no home")

    # ============================================================== DEP (the Void page)
    ids = [("Skyy_Ench_Marble", "Mining", 7), ("Skyy_Ench_Ash", "Foraging", 6), ("Skyy_Ench_Corn", "Farming", 5), ("Skyy_Ench_Bone", "Combat", 4),
           ("Skyy_Ench_HideLight", "Smithing", 3), ("Ingredient_Life_Essence_Concentrated", "Farming", 8)]
    for i_, _c, _n in ids:
        custom_item(i_, 100)
    custom_item("Skyy_Ench_LifeEssence", 100)

    def sp_page(cat):
        sp = us.allocateInstance(SPage.class_)
        jfield(SPage.class_, "playerRef").set(sp, pref(U))
        jfield(SPage.class_, "info").set(sp, JString(""))
        jfield(SPage.class_, "amount").set(sp, JString(""))
        jfield(SPage.class_, "cat").set(sp, JString(cat))
        return sp
    drain()
    fresh(base)
    coll(U, {"Mining": 0, "Foraging": 0, "Farming": 0})
    pP = player(storage=[(i_, n_) for i_, _c, n_ in ids] + [("Skyy_Ench_LifeEssence", 2)])
    sp = sp_page("Foraging")
    err = try_(lambda: sp.onEvent(None, None, pP, JString('{"a":"depevery"}')))
    drain()
    after = pc(k)
    info = str(jfield(SPage.class_, "info").get(sp) or "")
    K.check(all(after.get(i_) == n_ for i_, _c, n_ in ids) and inv_counts(pP) == {"Skyy_Ench_LifeEssence": 2} and info.startswith("+Deposited 33 items into 5 bags"),
            "DEP: Deposit all (on Foraging) puts the C1 Enchanted items of all five categories + Greater Essence in; the retired id stays: %s inv %s %r (%s)"
            % (after, inv_counts(pP), info, err))
    drain()
    fresh(base)
    coll(U, {"Mining": 0})
    pC = player(storage=[("Skyy_Ench_Bone", 4), ("Skyy_Ench_Marble", 7)])
    sp = sp_page("Combat")
    err = try_(lambda: sp.onEvent(None, None, pC, JString('{"a":"depall"}')))
    drain()
    K.check(pc(k).get("Skyy_Ench_Bone") == 4 and "Skyy_Ench_Marble" not in pc(k) and inv_counts(pC) == {"Skyy_Ench_Marble": 7},
            "DEP: Deposit Combat takes the Enchanted Bone only (the Enchanted Marble stays): %s %s (%s)" % (pc(k), inv_counts(pC), err))

    # ============================================================== UPG (no level gate on the Void upgrade; Skyy "if i have the stuff, my lvl shouldn't stop me on this")
    VS = L["VS"]
    drain()
    fresh(base)
    coll(U, {"Mining": 0})                      # storage level 1 (the old Unique gate was Lv 10)
    VS.st(k).first = 1
    cost = Cfg.parseCost(Cfg.cost(0, 1))
    need = dict((str(e.getKey()), int(e.getValue())) for e in cost.entrySet())
    stacks = []
    for i_, n_ in need.items():
        custom_item(i_, 100)
        while n_ > 0:
            stacks.append((i_, min(100, n_)))
            n_ -= 100
    lv0 = int(VS.level(U, k, 0))
    poor = player(storage=stacks[:-1])          # one stack short
    r0 = str(VS.upgrade(poor, U, k, 0, 0))
    K.check(r0.startswith("-") and "Lv" not in r0 and int(VS.st(k).rar[0]) == 0, "UPG: missing items -> still refused, no rarity change (%r)" % r0)
    rich = player(storage=stacks)
    sp = sp_page("Mining")
    bu = UCBc()
    err = try_(lambda: sp.render(bu, UEBc(), rich, k, U))
    tu = dump(bu)
    K.check(err is None and "Pay the items below to upgrade" in tu and "Needs Mining Lv" not in tu and "Level gate" not in tu,
            "UPG: the Upgrade box has no 'Needs Mining Lv' line at Lv %d (%s)" % (lv0, err))
    r1 = str(VS.upgrade(rich, U, k, 0, 0))
    drain()
    K.check(lv0 < 10 and r1.startswith("+Mining is now Unique") and int(VS.st(k).rar[0]) == 1 and inv_counts(rich) == {},
            "UPG: Lv %d (below the old gate 10) with every item -> upgraded, exactly the cost paid (%r, cost %s, left %s)" % (lv0, r1, need, inv_counts(rich)))

    # ============================================================== TIER (tools/tier_tags.py, live)
    tk = lambda i: int(RC.tierKey(JString(i)))
    K.eq([tk(i) for i in ("Plant_Crop_Corn_Item", "Skyy_Ench_Corn", "Skyy_Ench_Wheat", "Skyy_Ench_Ash")], [3, 3, 2, tk("Wood_Ash_Trunk")],
         "TIER: Enchanted Corn = Corn's tier (C1 rows in the table); Enchanted Ash = Ash's")
    farm = ["Plant_Seeds_Corn_Eternal", "Skyy_Ench_Corn", "Plant_Seeds_Corn", "Plant_Crop_Corn_Item", "Plant_Crop_Carrot_Item", "Skyy_Ench_Carrot"]
    ent = JClass("java.util.ArrayList")()
    for i in farm:
        ent.add(JArray(Obj)([JString(i), Int(0), Int(int(RC.sortKey(JString(i)))), RC.sortName(JString(i))]))
    JClass("java.util.Collections").sort(ent, RC())
    got = [str(e[0]) for e in ent]
    K.check(got.index("Plant_Crop_Corn_Item") + 1 == got.index("Skyy_Ench_Corn") and got.index("Skyy_Ench_Corn") + 1 == got.index("Plant_Seeds_Corn")
            and got.index("Plant_Seeds_Corn") + 1 == got.index("Plant_Seeds_Corn_Eternal") and got.index("Plant_Crop_Carrot_Item") + 1 == got.index("Skyy_Ench_Carrot"),
            "TIER: crop grouping kept for the C1 crops: corn, Enchanted corn, seeds, Eternal seeds (%s)" % got)

    # ============================================================== LIST (the scrolling list + the bigger rows)
    BAR, ORE = "Ingredient_Bar_Copper", "Ore_Copper"
    custom_item(BAR, 100)
    custom_item(ORE, 100)
    outs = ["Skyy_Test_Out%d" % n for n in range(12)]
    for o in outs:
        custom_item(o, 100)
    rows = [recipe("Skyy_Test_R%d" % n, outs[n], [(BAR, 2), (ORE, 1)]) for n in range(12)]
    p = player(storage=[(BAR, 9), (ORE, 9)])
    m_ = CIC(JArray(ICc)([p.getInventory().getCombinedBackpackStorageHotbar()]))
    pg = page("A:craft")
    used = 42 + 40 + 22 + 66
    br_, er_ = UCBc(), UEBc()

    def draw():
        CP.listOpen(br_, used)
        for n in range(12):
            pg.drawRow(br_, er_, n, rows[n], m_, int(CP.limit(rows[n], m_)), "", int(CP.limit(rows[n], m_)), False, "")
        CP.listMore(br_, 12, 12)
        pg.foot(br_, er_, 0, 0, False, True, False)
    err = try_(draw)
    t_ = dump(br_)
    h = int(CP.BODYH) - used - 4
    K.check(err is None and "Group #SkyyCList { Anchor: (Height: %d); LayoutMode: TopScrolling; ScrollbarStyle:" % h in t_ and "Common/ScrollbarHandle.png" in t_,
            "LIST: ONE TopScrolling list with the vanilla scrollbar, %d high (the body %d minus %d above + the foot) (%s)" % (h, int(CP.BODYH), used, err))
    K.check(int(CP.BODYH) == 822 and h >= 6 * 98, "LIST: about 6 rows of 98 show at once with one tab row + the search row (%d px = %.1f rows)" % (h, h / 98.0))
    lines = t_.split("\n")
    K.check(all(("SkyyCRow%d" % n) in t_ for n in range(12)) and t_.count("Anchor: (Height: 92, Bottom: 6)") == 12,
            "LIST: all 12 rows drawn (no pages), each 92 high")
    K.check(sum(1 for l in lines if l == "#SkyyCList") >= 12, "LIST: the rows are appended INSIDE #SkyyCList (%d appends there)" % sum(1 for l in lines if l == "#SkyyCList"))
    K.check("FontSize: 22" in t_ and "FontSize: 17" in t_ and "Width: 72, Height: 72" in t_ and "Width: 36, Height: 36" in t_,
            "LIST: bigger rows - 22 px names, 17 px costs, a 72 px output icon, 36 px cost icons")
    K.check("SkyyCPrev" not in t_ and "SkyyCNext" not in t_ and "Page 1" not in t_ and "SkyyCOnly" in t_, "LIST: the foot of a list view has no pager, Craftable only stays")
    ev_t = dump(er_, "getEvents") if hasattr(er_, "getEvents") else ""
    K.check(not ev_t or ("craft:11:1:Skyy_Test_R11" in ev_t and "craft:11:10:Skyy_Test_R11" in ev_t and "craft:11:0:Skyy_Test_R11" in ev_t),
            "LIST: row 12's Craft / x10 / All events carry its recipe id = craft:11:1:<id> / :10 / :0")
    K.check('ItemId: "Skyy_Test_Out0"' in t_ and 'ItemId: "Ingredient_Bar_Copper"' in t_ and 'ItemId: "Ore_Copper"' in t_ and "ItemId:  +" not in t_,
            "LIST (critic fix 1): the row markup names the real item ids - output icon ItemId: \"Skyy_Test_Out0\", cost icons ItemId: \"Ingredient_Bar_Copper\"")
    gdr = open(os.path.join(HERE, "build_skyysacks_%s.py" % VERSION), encoding="utf8").read()
    gdr = gdr[gdr.index("public void drawRow("):]
    gdr = gdr[:gdr.index('}"""), cpg))')]
    K.check(gdr.count("boolean ok = allN > 0;") == 1 and gdr.count('b.appendInline("#" + rid, gap(8));') == 1, "LIST (critic fix 2): drawRow has no duplicated lines")
    if not ev_t:
        K.notes.append("LIST: no getEvents on this engine's UIEventBuilder - the events are checked in the source")
    b2 = UCBc()
    err = try_(lambda: pg.foot(b2, UEBc(), 0, 3, False, False, False))
    K.check(err is None and "SkyyCPrev" in dump(b2) and "Page 1 / 3" in dump(b2), "LIST: pages > 0 (the ADD FUEL picker) keeps its pager (%s)" % err)
    b3 = UCBc()
    err = try_(lambda: CP.listMore(b3, 150, 163))
    K.check(err is None and "Showing the first 150 of 163" in dump(b3) and int(CP.MAXROWS) == 150, "LIST: after MAXROWS a closing line says how many more (%s)" % err)
    K.eq(int(CP.listH(2000)), 200, "LIST: never lower than 200 px")
    # SIZE (Skyy "i dont mind scrolling, but if there are only a few items try to scale them to all fit.")
    sz = [int(CP.rowSize(n, used)) for n in (0, 1, 3, 4, 6, 12)]
    K.eq(sz, [2, 2, 2, 1, 0, 0], "SIZE: rowSize by count with one tab row + search (%d px): 1-3 rows 168 high, 4 rows 128, 6+ normal 92 (scrolls)" % h)
    K.check(all(int(CP.rowSize(n, used)) == 0 or n * (int(list(CP.ROWHS)[int(CP.rowSize(n, used))]) + 6) <= h - 8 for n in range(1, 20)),
            "SIZE: a larger size is only picked when every row fits without scrolling")
    for zs, rh_, nf, ic in ((1, 128, 28, 104), (2, 168, 32, 140)):
        b4, e4 = UCBc(), UEBc()
        jfield(CP.class_, "rowSz").setInt(pg, zs)
        err = try_(lambda: (CP.listOpen(b4, used), pg.drawRow(b4, e4, 0, rows[0], m_, 4, "", 4, False, ""), pg.drawRow(b4, e4, 1, rows[1], m_, 0, "", 0, True, "5s each")))
        t4 = dump(b4)
        K.check(err is None and t4.count("Anchor: (Height: %d, Bottom: 6)" % rh_) == 2 and ("FontSize: %d" % nf) in t4 and ("Width: %d, Height: %d" % (ic, ic)) in t4
                and ("Top: %d" % ((rh_ - 32) // 2)) in t4, "SIZE %d: rows %d high, %d px names, %d px icons, buttons centred (%s)" % (zs, rh_, nf, ic, err))
    jfield(CP.class_, "rowSz").setInt(pg, 0)
    gen = open(os.path.join(HERE, "build_skyysacks_%s.py" % VERSION), encoding="utf8").read()
    bd_ = gen[gen.index("public void build(@REF@ ref"):]
    bd_ = bd_[:bd_.index('}""".replace("@SHELL@"')]
    bp_ = gen[gen.index("public void buildProc("):]
    bp_ = bp_[:bp_.index('}"""), cpg))')]
    K.check("listOpen(b, this.usedH);" in bd_ and "i < MAXROWS" in bd_ and "foot(b, ev, 0, 0, only, true, false);" in bd_ and "int per = 9;" not in bd_
            and "listOpen(b, this.usedH);" in bp_ and "foot(b, ev, 0, 0, only, true, true);" in bp_ and "int per = 7;" not in bp_,
            "LIST: (source) the instant tabs and the Furnace / Tannery tabs build one scrolling list, no pages")

    # ============================================================== CRAFT (a row from the list)
    jfield(CP.class_, "tab").set(pg, JString("X:test"))   # not a knowledge-gated tab (KnowSync needs the real player data)
    lst = JClass("java.util.ArrayList")()
    for r in rows:
        lst.add(r)
    jfield(CP.class_, "rows").set(pg, lst)
    # critic fix 3: the click names its recipe; resolved BY ID against the current list
    K.check(pg.rowOf(JString("11:1:Skyy_Test_R11")) == rows[11] and pg.rowOf(JString("3:1:Skyy_Test_R11")) == rows[11]
            and pg.rowOf(JString("3:1:Skyy_Gone")) is None and pg.rowOf(JString("3:1")) is None and pg.rowOf(JString("x:1:Skyy_Test_R2")) == rows[2],
            "CRAFT (fix 3): rowOf = the recipe by id (place first, then a search); a gone id / an old two-part event = none")
    lst2 = JClass("java.util.ArrayList")()
    for r in rows[1:]:
        lst2.add(r)
    jfield(CP.class_, "rows").set(pg, lst2)
    K.check(pg.rowOf(JString("11:1:Skyy_Test_R11")) == rows[11] and pg.rowOf(JString("11:1:Skyy_Test_R0")) is None,
            "CRAFT (fix 3): after the list changed (one row less) a stale click still finds ITS recipe or nothing - never the row now at that place")
    jfield(CP.class_, "rows").set(pg, lst)
    gh = open(os.path.join(HERE, "build_skyysacks_%s.py" % VERSION), encoding="utf8").read()
    K.check('@CRR@ r = rowOf(act.substring(6));' in gh and 'That row changed - nothing was crafted' in gh and '@CRR@ pr0 = want < 0 ? null : rowOf(act.substring(3));' in gh
            and "this.rows.get(idx)" not in gh[gh.index("String act = jsonStr(data, \"a\");"):],
            "CRAFT (fix 3, source): the craft and queue clicks resolve through rowOf, never this.rows.get(idx)")
    r11 = jfield(CP.class_, "rows").get(pg).get(11)
    res = str(pg.craftOne(None, st, p, U, k, r11, 1, False))
    drain()
    K.check(res.startswith("crafted 1 x") and inv_counts(p) == {BAR: 7, ORE: 8, outs[11]: 1},
            "CRAFT: the 12th row (page 2 in 0.8.13) crafts from the list: 2 bars + 1 ore paid, its output given (%r %s)" % (res, inv_counts(p)))

    # ============================================================== ART (no accessory recipe in /craft)
    K.check(bool(CP.artifact(recipe("Skyy_Test_A1", "Skyy_Talisman_Speed_Common", [(BAR, 1)]))) and bool(CP.artifact(recipe("Skyy_Test_A2", "Skyy_Accessory_Furnace_T2", [(BAR, 1)])))
            and not bool(CP.artifact(rows[0])), "ART: artifact() = accessory outputs (Talismans, Skyy_Acc*), not other items")
    tabs = []
    err = try_(lambda: tabs.extend(str(t[0]) for t in page("A:craft").buildTabs(p, U, k)))
    K.check(err is None and "A:art" not in tabs and tabs[:2] == ["A:craft", "A:smith"], "ART: buildTabs has no Artifacts tab: %s (%s)" % (tabs, err))
    rf_ = gen[gen.index("public java.util.ArrayList recipesFor(String tabId"):]
    rf_ = rf_[:rf_.index('}}""", cpg))')]
    sr_ = gen[gen.index("public java.util.ArrayList searchRecipes("):]
    sr_ = sr_[:sr_.index('}}""", cpg))')]
    K.check("if (artifact(rc)) continue;\n    if (grp >= 0 && tabGroup(rc) != grp) continue;" in rf_ and "grp = 3" not in rf_
            and rf_.index("if (artifact(rc)) continue;") < rf_.index("out.add(rc);") and "if (artifact(rc)) continue;" in sr_,
            "ART: (source) recipesFor skips accessory recipes on EVERY tab (Collections + bench tabs too) and search skips them")
    drain()


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("new", run_new), ("live", T0810.run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
