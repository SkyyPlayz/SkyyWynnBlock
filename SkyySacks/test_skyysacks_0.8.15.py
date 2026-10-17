"""Harness for SkyySacks 0.8.15 (MENU PATTERN sweep S2: the Void = Storage > Pocket and /craft = Crafting > Crafting on the kit 1.7 hub page,
no back buttons, scroll lists, the ADD FUEL picker in place; tools/sacks_0_8_15_patch.py). Build first:
    python tools/sacks_0_8_15_patch.py && python SkyySacks/build_skyysacks_0.8.15.py

    python SkyySacks/test_skyysacks_0.8.15.py [--keep] [--dir <folder inside tools/dev/scratch/>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.8.14 -> 0.8.15: exactly the planned members (SacksPage render / onEvent / hubAck, CraftPage's shell / sub row / footer /
                fuel picker / renderPage, HubBar kit 1.7, the plugin's setup, SacksCmd), + VoidHubOpen; non-class entries: manifest.json +
                the storage_pocket tab icon pair
  NEW  EXECUTED on the 0.8.0 harness's Void stand-ins (real SimpleItemContainers in a stand-in Inventory, a stand-in Item store, a scratch
       pool folder) and REAL CraftingRecipe objects; every page / view BUILT through the real page code (SacksPage.render, CraftPage.renderPage)
       and checked with SUI.assert_menu_page (1600 x 980, row 1 + row 2, one sub row at most, no back button / < Menu, no pager) + the
       markup rules (check_page, kit paths, every b.set / binding names an element that exists):
       VOID  the Void with 40+ kinds in one category: ONE scroll grid (12 columns, every kind drawn, no Prev / Next), the count line,
             rows 1 + 2 (Pocket selected), the X; an empty category; the Upgrade confirm view (Pay / Cancel in place)
       VOPS  cell:<n> beyond the old 36 selects; Withdraw 5 + Deposit (amount box) move exactly those items; Deposit all; row 2's own tab =
             a rebuild (route "self"); /sacks opens with openCustomPage (no container window) - source
       CRAFT /craft: the crafter tabs = the ONE sub-tab row (bound tab:<i>, the open one Primary), no back-to-the-Void button; 12 rows in ONE
             list (normal size), 2 rows (the big size, shared growSize rule = skyyui.grow_pick), search; the footer (result line, Craftable
             only, 48 px); a craft of row 12 through craftOne with the bound event's recipe id
       PROC  the Furnace tab (queue list, fuel row, Refresh in the footer); ADD FUEL open (the fuel scroll list, big rows for a few fuels, no
             Cancel / Back, no pager) and with a fuel picked (the amount box + Load on top, the list below, Picked)
       TAB   VoidHubOpen.register puts hub:tab:storage:pocket (SkyySacks, Pocket, order 10, /sacks, storage_pocket)
  D    START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyySacks (0.8.10's run_live10 on this jar)
  AA   engine-access audit
Not testable without the game (UNVERIFIED): the look in game, the scroll wheel / bar, the scroll position after a click (a rebuild starts at
the top again), the row 2 tab art, that the client is fine without the inventory panel under the Void. Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import skyyench as EN
import skyyui as SUI
import tier_tags as TT

VERSION = "0.8.15"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-0.8.14.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menuS2", "sacks", "h")))
PKG = "com.skyy.sacks."
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_10", os.path.join(HERE, "test_skyysacks_0.8.10.py"))
T0810 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T0810)
T089 = T0810.T089
EXPECT = {
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],                  # the config kit's version text (0.8.15)
    "SacksPage": ["+m hubAck", "~m onEvent", "~m render"],               # the hub page shell + rows, the scroll grid, the hub route, cell:<n>
    "SacksCmd": ["~m execute"],                                          # openCustomPage (no container window)
    "CraftPage": ["+f FLIST_A", "+f FLIST_B", "+f FUELHS", "+f F_SEC", "+f F_TER", "+f F_TERON", "+m fbtn", "+m renderPage", "~<clinit>",
                  "~m build", "~m buildProc", "~m drawRow", "~m foot", "~m fuelPicker", "~m listH", "~m rowSize"],   # listH: BODYH 822 -> 676
    "HubBar": ["+m bigLab", "+m bigRow", "+m bigRowFill", "+m bigTabLab", "+m bigTabsFill", "+m growSize", "+m hasArt", "+m hostOf",
               "+m hostShown", "+m hostTab", "+m openSub", "+m page17", "+m putSub", "+m selOf", "+m subIcon", "+m subTab", "+m subTabs"],   # kit 1.7
    "SkyySacksPlugin": ["~m setup"],                                     # VoidHubOpen.register + the ready line
}
ADDED = ["VoidHubOpen"]
_PV = SUI.hub_tab_icon_paths("storage", "pocket")
NONCLASS = sorted(["manifest.json", _PV[2], _PV[3]])


def run_compare15(out, jar, old_jar, pkg, expect, added, removed=()):
    """harness_kit.run_compare with this round's non-class entries (manifest.json + the Pocket tab icon pair)"""
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
HK.run_compare = run_compare15
BETA = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyySacks")
DECL_RE = re.compile(r"\b([A-Za-z]+) #([A-Za-z0-9]+) \{")


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
    Defs, Cfg, Pool = L["Defs"], L["Cfg"], L["Pool"]
    fresh, player, pc, inv_counts, custom_item, drain, coll = (L[n] for n in ("fresh", "player", "pc", "inv_counts", "custom_item", "drain", "coll"))
    UUID, us, jfield, pref, bridge = (L[n] for n in ("UUID", "us", "jfield", "pref", "bridge"))
    CtF, CtM, CtC, jp = L["CtF"], L["CtM"], L["CtC"], L["jp"]
    J = lambda n: JClass(PKG + n)
    CP, SPage, HubBar = J("CraftPage"), J("SacksPage"), J("HubBar")
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    CR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    BR = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    CIC = JClass("com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer")
    ICc = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    UCBc, UEBc = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Coll = JClass("java.util.Collection")
    s_ = lambda v: None if v is None else str(v)

    def try_(f):
        try:
            f()
            return None
        except Exception as e:
            st_txt = e.stacktrace() if hasattr(e, "stacktrace") else ""
            return (str(e)[:160] + " @ " + " | ".join(l.strip() for l in str(st_txt).splitlines()[1:6]))[:700]

    # ---- the built page's commands + bindings (SkyyMenu 0.3.29 harness's cmds_of / events_of)
    def cmds_of(b_):
        res = []
        for c_ in list(b_.getCommands()):
            g = lambda n: (lambda v: None if v is None else str(v))(jfield(c_.getClass(), n).get(c_))
            res.append((g("type"), g("selector"), g("text"), g("data")))
        return res

    def events_of(ev_):
        res = []
        for f_ in ev_.getClass().getDeclaredFields():
            f_.setAccessible(True)
            v_ = f_.get(ev_)
            if v_ is None or not Coll.class_.isInstance(v_):
                continue
            for e in list(v_):
                sel, parts = None, []
                c = e.getClass()
                while c is not None and str(c.getName()) != "java.lang.Object":
                    for g in c.getDeclaredFields():
                        try:
                            g.setAccessible(True)
                            x = g.get(e)
                            if x is None:
                                continue
                            if str(g.getName()) == "selector":
                                sel = str(x)
                            parts.append(str(x))
                            for h in x.getClass().getDeclaredFields():
                                try:
                                    h.setAccessible(True)
                                    y = h.get(x)
                                    if y is not None:
                                        parts.append(str(y))
                                except Exception:
                                    pass
                        except Exception:
                            pass
                    c = c.getSuperclass()
                res.append((sel, " ".join(parts)))
        return res

    def unq(d):
        if d is None:
            return ""
        try:
            v = json.loads(d)
        except Exception:
            return d
        if isinstance(v, dict) and len(v) == 1:
            v = list(v.values())[0]
        return v if isinstance(v, str) else d

    def checked(b_, ev_, what, hub):
        """page rules + SUI.assert_menu_page on the REAL built commands"""
        c, e = cmds_of(b_), events_of(ev_)
        apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in c if t is not None and ty and "Append" in ty])
        sets = [(s, unq(d)) for ty, s, t, d in c if ty == "Set"]
        try:
            SUI.check_page(apps, "Skyy")
            K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
        except Exception as ex:
            K.check(False, "%s: check_page: %s" % (what, ex))
        try:
            SUI.check_sky_paths(apps, tab_icons=True)
            K.check(True, "%s: kit texture paths only" % what)
        except Exception as ex:
            K.check(False, "%s: sky paths: %s" % (what, ex))
        ids = set()
        for _p, mk in apps:
            ids |= set(x.group(2) for x in DECL_RE.finditer(SUI.render(mk)))
        bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s, _t in e if s and s.lstrip("#") not in ids]
        K.check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(e), bad[:4]))
        try:
            info = SUI.assert_menu_page(apps, hub=hub, what=what, sets=sets)
            K.check(info["rows"] == 2, "%s: assert_menu_page (1600 x 980, rows %d, sub rows %d, no back button, no pager)" % (what, info["rows"], info["subs"]))
        except Exception as ex:
            K.check(False, "%s: assert_menu_page: %s" % (what, ex))
        txt = "\n".join(t or "" for _ty, _s, t, _d in c) + "\n" + "\n".join(str(d) for _ty, _s, _t, d in c)
        K.check(not re.search(r"<\s?(Back|Menu|The Void)|Go Back|\"Back\"", txt),
                "%s: no Back / < Menu / < The Void text anywhere on the page" % what)
        return c, e, apps, sets, txt

    U = UUID.fromString("00000000-0000-0000-0000-0000000c0f15")
    k = str(U)
    base = os.path.join(scratch, "new")

    # ============================================================== TAB: the Storage > Pocket contract tab + the Crafting tab
    n1 = int(J("VoidHubOpen").register())
    n2 = int(J("CraftHubOpen").register())
    e1 = bridge.get("hub:tab:storage:pocket")
    K.check(n1 == 1 and n2 == 1 and e1 is not None and str(e1[0]) == "SkyySacks" and str(e1[1]) == "Pocket" and int(e1[2]) == 10
            and str(e1[3]) == "sacks" and str(e1[6]) == "storage_pocket" and str(e1[4].getClass().getName()) == PKG + "VoidHubOpen",
            "TAB: VoidHubOpen.register puts hub:tab:storage:pocket = SkyySacks / Pocket / 10 / sacks / VoidHubOpen / storage_pocket (%s)"
            % (None if e1 is None else [str(x) for x in e1]))

    # ============================================================== VOID (the page, built)
    cats = list(Defs.CATS)
    pool_ids = sorted(set(list(TT.ROWS) + [EN.PREFIX + t[0] for t in EN.TABLE]))
    by = {}
    for i_ in pool_ids:
        h_ = s_(Defs.homeOf(JString(i_)))
        if h_:
            by.setdefault(h_, []).append(i_)
    big = max(by, key=lambda c_: len(by[c_]))
    many = by[big][:48]
    K.check(len(many) > 36, "VOID: %d homeable kinds in %s for the scroll test (more than the old 36-cell page)" % (len(many), big))
    for i_ in many:
        custom_item(i_, 100)
    drain()
    fresh(base)
    coll(U, dict((c_, 0) for c_ in cats))
    for n_, i_ in enumerate(many):        # 2 of each (under the level 1 space of 150: deposits are not refused for space)
        Pool.pool(k).put(JString(i_), JClass("java.lang.Long")(2))

    def sp_page(cat):
        sp = us.allocateInstance(SPage.class_)
        jfield(SPage.class_, "playerRef").set(sp, pref(U))
        jfield(SPage.class_, "info").set(sp, JString(""))
        jfield(SPage.class_, "amount").set(sp, JString(""))
        jfield(SPage.class_, "cat").set(sp, JString(cat))
        return sp

    def vbuild(sp, pl, what):
        b_, e_ = UCBc(), UEBc()
        err = try_(lambda: sp.render(b_, e_, pl, k, U))
        K.check(err is None, "%s: SacksPage.render ran (%s)" % (what, err))
        return checked(b_, e_, what, "storage")
    pV = player(storage=[])
    sp = sp_page(big)
    c, e, apps, sets, txt = vbuild(sp, pV, "VOID (%d kinds)" % len(many))
    binds = [d for s, d in e]
    K.check(all(("SkyyVCell%d" % n_) in txt for n_ in range(len(many))) and all(any(("cell:%d" % n_) in d for d in binds) for n_ in (0, 36, len(many) - 1)),
            "VOID: every kind is a cell of ONE grid (%d cells drawn, cell:36 and cell:%d bound - the old page 2)" % (len(many), len(many) - 1))
    K.check("Group #SkyyVGrid { Anchor: (Height:" in txt and "TopScrolling" in txt and "SkyyVPrev" not in txt and "SkyyVNext" not in txt and "Page 1" not in txt,
            "VOID: the grid is a TopScrolling list, no Prev / Next / Page line")
    _gr = sum(1 for _ty, s, t, _d in c if s == "#SkyyVGrid" and t and t.startswith("Group #SkyyVRow"))
    _gc = sum(1 for _ty, s, t, _d in c if s and s.startswith("#SkyyVRow") and t and "#SkyyVCell" in t)
    K.check(_gr >= (len(many) + 11) // 12 and _gc == 12 * _gr, "VOID: 12 columns - %d rows inside #SkyyVGrid, %d cells (empty ones fill the rows that show)" % (_gr, _gc))
    K.check(any(s == "#SkyyVCount.Text" and ("%d kinds of items" % len(many)) in unq(d) for s, d in sets), "VOID: the count line says %d kinds" % len(many))
    K.check("SkyyVHBigRow" in txt and "SkyyVHBigTabs" in txt and any("hub:close" in d for d in binds) and any("hub:pocket" in d for d in binds),
            "VOID: row 1 + row 2 (the Pocket tab bound) + the X")
    K.check('Group #SkyyVH { Anchor: (Width: 1600, Height: 980); }' in txt and "SkyySacks {" not in txt.split("\n")[0],
            "VOID: the page root is the 1600 x 980 hub page (was 1300 x 690)")
    # an empty category
    empty_cat = [c_ for c_ in cats if c_ != big][0]
    vbuild(sp_page(empty_cat), pV, "VOID empty %s" % empty_cat)

    # ============================================================== VOPS (the old paths, through onEvent)
    err = try_(lambda: sp.onEvent(None, None, pV, JString('{"a":"cell:40","@Amt":""}')))
    sel40 = s_(jfield(SPage.class_, "sel").get(sp))
    cells_ = [s_(x) for x in (jfield(SPage.class_, "cells").get(sp) or [])]
    K.check(err is None and len(cells_) > 40 and sel40 is not None and sel40 == cells_[40],
            "VOPS: cell:40 (beyond the old 36) selects that kind (%s, %s)" % (sel40, err))
    before = pc(k).get(sel40, 0)
    err = try_(lambda: sp.onEvent(None, None, pV, JString('{"a":"wd","@Amt":"2"}')))
    drain()
    K.check(err is None and before == 2 and pc(k).get(sel40, 0) == 0 and inv_counts(pV).get(sel40) == 2,
            "VOPS: Withdraw 2 (the amount box) takes exactly 2 into the inventory (%d -> %d, inv %s) %s" % (before, pc(k).get(sel40, 0), inv_counts(pV), err))
    err = try_(lambda: sp.onEvent(None, None, pV, JString('{"a":"dep","@Amt":""}')))
    drain()
    K.check(err is None and pc(k).get(sel40, 0) == before and inv_counts(pV).get(sel40) is None,
            "VOPS: Deposit (empty amount = all you carry) puts the 2 back (%d, inv %s) %s" % (pc(k).get(sel40, 0), inv_counts(pV), err))
    pD = player(storage=[(many[0], 7), (many[1], 3)])
    err = try_(lambda: sp.onEvent(None, None, pD, JString('{"a":"depevery","@Amt":""}')))
    drain()
    K.check(err is None and inv_counts(pD) == {} and pc(k).get(many[0]) == 9 and pc(k).get(many[1]) == 5,
            "VOPS: Deposit all moves every Void item from the inventory (%s, %s) %s" % (inv_counts(pD), [pc(k).get(many[0]), pc(k).get(many[1])], err))
    err = try_(lambda: sp.onEvent(None, None, pV, JString('{"a":"hub:pocket","@Amt":""}')))
    K.check(err is None, "VOPS: row 2's own tab (route self) is handled without an error (%s)" % err)
    gen = open(os.path.join(HERE, "build_skyysacks_%s.py" % VERSION), encoding="utf8").read()
    cm_ = gen[gen.index('public SacksCmd() {'):]
    cm_ = cm_[:cm_.index("# ================= SacksPageFactory")]
    K.check("openCustomPageWithWindows" not in gen and "player.getPageManager().openCustomPage(ref, store, new {PKG}.SacksPage(pr, (String) null));" in cm_,
            "VOPS: (source) /sacks opens the page with openCustomPage - no container window")
    ev_src = gen[gen.index("public void onEvent(@REF@ ref, @ST@ st, @PLA@ player0, String data) {"):]
    K.check(ev_src.index('HubBar.route(this.playerRef, data, "storage", "pocket")') < ev_src.index('String a = field(data, "a");'),
            "VOPS: (source) the hub rows' clicks are routed first (HubBar.route storage / pocket)")

    # ============================================================== UPG (the Upgrade confirm view, in place)
    VS = L["VS"]
    drain()
    fresh(base)
    coll(U, {"Mining": 0})
    cost = Cfg.parseCost(Cfg.cost(0, 1))
    stacks = []
    for e_ in cost.entrySet():
        i_, n_ = str(e_.getKey()), int(e_.getValue())
        custom_item(i_, 100)
        while n_ > 0:
            stacks.append((i_, min(100, n_)))
            n_ -= 100
    rich = player(storage=stacks)
    su = sp_page("Mining")
    jfield(SPage.class_, "confirm").setBoolean(su, True)
    c, e, apps, sets, txt = vbuild(su, rich, "UPG confirm view")
    K.check("SkyyVUpYes" in txt and "SkyyVUpNo" in txt and any("upgok:0:0" in d for _s, d in e), "UPG: Pay / Cancel replace Upgrade in place (upgok:0:0 bound)")

    # ============================================================== CRAFT (/craft, built through renderPage)
    BAR, ORE = "Ingredient_Bar_Copper", "Ore_Copper"
    custom_item(BAR, 100)
    custom_item(ORE, 100)

    def recipe(rid, out_, inputs, bench=None):
        ins = JArray(MQ)([MQ(JString(i), None, None, JInt(q), None) for i, q in inputs])
        po = MQ(JString(out_), None, None, JInt(1), None)
        r = CR(ins, po, JArray(MQ)([po]), JInt(1), JArray(BR)(0), JFloat(0.0), False, JInt(0))
        jfield(CR.class_, "id").set(r, JString(rid))
        return r
    outs = ["Skyy_Test_Out%d" % n for n in range(12)]
    for o in outs:
        custom_item(o, 100)
    rows = [recipe("Skyy_Test_R%d" % n, outs[n], [(BAR, 2), (ORE, 1)]) for n in range(12)]
    # a CraftPage whose recipe lists come from the harness (the real asset maps are not loaded here); everything else is the real page
    tcp = jp.makeClass(PKG + "SkyyTestCP15", jp.get(PKG + "CraftPage"))
    tcp.addField(CtF.make("public static java.util.ArrayList R = new java.util.ArrayList();", tcp))
    tcp.addMethod(CtM.make("public java.util.ArrayList recipesFor(String t, java.util.UUID u) { return new java.util.ArrayList(R); }", tcp))
    tcp.addMethod(CtM.make("public java.util.ArrayList searchRecipes(java.util.UUID u, String q) { java.util.ArrayList o = new java.util.ArrayList(); "
                           "for (int i = 0; i < R.size(); i++) if (i % 2 == 0) o.add(R.get(i)); return o; }", tcp))
    TCP = JClass(tcp.toClass(CP.class_))

    def setR(lst):
        TCP.R.clear()
        for r in lst:
            TCP.R.add(r)

    def cpage(tab=None, query=""):
        pg = us.allocateInstance(TCP.class_)
        jfield(CP.class_, "playerRef").set(pg, pref(U))
        jfield(CP.class_, "info").set(pg, JString(""))
        jfield(CP.class_, "query").set(pg, JString(query))
        jfield(CP.class_, "tab").set(pg, None if tab is None else JString(tab))
        return pg

    def cbuild(pg, pl, what):
        b_, e_ = UCBc(), UEBc()
        err = try_(lambda: pg.renderPage(b_, e_, pl, U))
        K.check(err is None, "%s: CraftPage.renderPage ran (%s)" % (what, err))
        r_ = checked(b_, e_, what, "smithing")
        return r_
    drain()
    fresh(base)
    coll(U, {"Mining": 0})
    bridge.put("acc:has:" + k, JString("Skyy_Accessory_Furnace_T1"))
    pC = player(storage=[(BAR, 9), (ORE, 9)])
    setR(rows)
    pg = cpage("A:craft")
    c, e, apps, sets, txt = cbuild(pg, pC, "CRAFT 12 rows")
    binds = [d for s, d in e]
    subs = [t for _ty, s, t, _d in c if s == "#SkyyCraftSub" and t and t.startswith("TextButton #SkyyCraftSub")]
    K.check(len(subs) >= 3 and "Crafting" in subs[0] and "Primary" in subs[0] and any("tab:1" in d for d in binds) and any("Furnace" in t for t in subs),
            "CRAFT: the crafter tabs are the ONE sub-tab row (%d buttons, Crafting Primary, tab:<i> bound, Furnace there)" % len(subs))
    K.check("SkyyCBags" not in txt and "SkyyCTabs0" not in txt and "SkyyCraftBigRow" in txt and "SkyyCraftBigTabs" in txt and any("hub:recipes" in d for d in binds),
            "CRAFT: no back-to-the-Void button / old tab rows; rows 1 + 2 (Crafting bound)")
    K.check(all(("SkyyCRow%d" % n) in txt for n in range(12)) and txt.count("Anchor: (Height: 92, Bottom: 6)") == 12 and "SkyyCPrev" not in txt,
            "CRAFT: all 12 rows in ONE list at the normal 92 px (no pages)")
    K.check(any(s == "#SkyyCraftFoot" and t and "SkyyCInfo" in t for _ty, s, t, _d in c) and any(s == "#SkyyCraftFoot" and t and "SkyyCOnly" in t and "Height: 48" in t for _ty, s, t, _d in c),
            "CRAFT: the footer holds the result line + Craftable only (48 px)")
    gdr = open(os.path.join(HERE, "build_skyysacks_%s.py" % VERSION), encoding="utf8").read()
    K.check(any(sl == "#SkyyCCraft11" for sl, _d in e) and 'ev.addEventBinding(@BT@.Activating, "#" + bid + i, @EVD@.of("a", a0 + i + ":1" + rk));' in gdr,
            "CRAFT: row 12's Craft button is bound (craft:11:1:<its recipe id> - drawRow unchanged)")
    st_c = jp.makeClass("com.hypixel.hytale.component.SkyyTestCraftStore15", jp.get("com.hypixel.hytale.component.Store"))
    st_c.addConstructor(CtC.make("public SkyyTestCraftStore15() { super((com.hypixel.hytale.component.ComponentRegistry) null, 0, (Object) null, "
                                 "(com.hypixel.hytale.component.IResourceStorage) null); }", st_c))
    st_c.addMethod(CtM.make("public void invoke(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.system.EcsEvent e) { }", st_c))
    TStore = JClass(st_c.toClass(JClass("com.hypixel.hytale.component.Store").class_))
    st = us.allocateInstance(TStore.class_)
    r11 = pg.rowOf(JString("11:1:Skyy_Test_R11"))
    res = str(pg.craftOne(None, st, pC, U, k, r11, 1, False)) if r11 is not None else "no row"
    drain()
    K.check(res.startswith("crafted 1 x") and inv_counts(pC) == {BAR: 7, ORE: 8, outs[11]: 1},
            "CRAFT: a craft of row 12 (its event's recipe id) pays 2 bars + 1 ore and gives its output (%r %s)" % (res, inv_counts(pC)))
    # few rows -> the big size (the shared rule)
    setR(rows[:2])
    pg2 = cpage("A:craft")
    c, e, apps, sets, txt = cbuild(pg2, pC, "CRAFT 2 rows")
    K.check(txt.count("Anchor: (Height: 168, Bottom: 6)") == 2, "CRAFT: 2 rows use the big 168 px size (Skyy rule 7)")
    hs = [int(x) for x in CP.ROWHS]
    bad = [(n, u_) for u_ in (62, 86, 198) for n in range(1, 25)
           if int(CP.rowSize(n, u_)) != SUI.grow_pick(n, int(CP.listH(u_)) - 8, hs, 6)]
    K.check(hs == [92, 128, 168] and not bad, "CRAFT: rowSize = the shared rule (HubBar.growSize = skyyui.grow_pick) for 1-24 rows: %s" % bad[:4])
    # search view
    setR(rows)
    pg3 = cpage("A:craft", "test")
    c, e, apps, sets, txt = cbuild(pg3, pC, "CRAFT search")
    K.check("SkyyCSearchRow" in txt and not any("Primary" in t for t in [t for _ty, s, t, _d in c if s == "#SkyyCraftSub" and t and t.startswith("TextButton")]),
            "CRAFT: searching - the search row, no sub-tab selected")

    # ============================================================== PROC (the Furnace tab + ADD FUEL)
    PB = J("ProcBench")
    fuels = ["Ingredient_Stick", "Wood_Oak_Trunk", "Ingredient_Charcoal"]   # the real list comes from the Item asset map (not loaded here)
    _fl = JClass("java.util.ArrayList")()
    for f_ in fuels:
        _fl.add(JString(f_))
    PB.FUELS = _fl
    _pb = J("ProcStore").of(JString(k), JString("Furnace"))
    _pb.needsFuel = True                                                     # (benchNeedsFuel reads the bench asset - not loaded here)
    for f_ in fuels:
        custom_item(f_, 100)
    pF = player(storage=[(BAR, 9), (ORE, 9)] + [(f_, 20 + 10 * n) for n, f_ in enumerate(fuels)])
    setR(rows[:3])
    pp = cpage("P:Furnace")
    c, e, apps, sets, txt = cbuild(pp, pF, "PROC Furnace")
    K.check("SkyyPStat" in txt and "SkyyPAddF" in txt and any(s == "#SkyyCraftFoot" and t and "SkyyPRefresh" in t for _ty, s, t, _d in c),
            "PROC: the Furnace tab (status, Add fuel, Refresh in the footer)")
    jfield(CP.class_, "fuelPick").setBoolean(pp, True)
    c, e, apps, sets, txt = cbuild(pp, pF, "PROC ADD FUEL list")
    binds = [d for s, d in e]
    K.check("Group #SkyyPFList { Anchor: (Height:" in txt and "TopScrolling" in txt and all(("SkyyPFRow%d" % n) in txt for n in range(len(fuels)))
            and "SkyyPFCancel" not in txt and "SkyyPFBack" not in txt and "SkyyCPrev" not in txt and any("pfpick:0" in d for d in binds),
            "PROC: ADD FUEL = ONE scroll list of the %d fuels (pfpick bound), no Cancel / Back / pager" % len(fuels))
    K.check(txt.count("Anchor: (Height: 96, Bottom: 4)") == len(fuels), "PROC: a few fuels use the big 96 px rows (grow_row_sizes of 48)")
    fl = list(jfield(CP.class_, "fuelList").get(pp))
    jfield(CP.class_, "fuelSel").set(pp, JString(fl[0]))
    c, e, apps, sets, txt = cbuild(pp, pF, "PROC ADD FUEL picked")
    binds = [d for s, d in e]
    K.check("SkyyPFSel" in txt and "SkyyPFLoad" in txt and "Picked" in txt and "SkyyPFList" in txt and any("pfload" in d for d in binds)
            and not any("pfpick:0" in d for d in binds) and any("pfpick:1" in d for d in binds),
            "PROC: a picked fuel = the amount box + Load on top, the list stays below (that row Picked, the others pickable)")
    drain()


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("new", run_new), ("live", T0810.run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
