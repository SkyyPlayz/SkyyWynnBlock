"""Harness for SkyyCollections 0.2.23 (MENU PATTERN sweep S1: every Collections view on the kit 1.7 hub_page - rows 1 + 2 on top, ONE
sub-tab row, no back buttons, a category = one scroll list with grow rows; tools/collections_0_2_23_patch.py). Build first:
    python tools/collections_0_2_23_patch.py && python SkyyCollections/build_skyycollections_0.2.23.py

    python SkyyCollections/test_skyycollections_0.2.23.py [--jar <SkyyCollections-0.2.23.jar>] [--dir <scratch>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the hub phases on tools/hub_tab_kit.py's engine stand-ins - the REAL PageManager,
UICommandBuilder / UIEventBuilder, a CommandManager that records lines - with -Xverify:all):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.22 -> 0.2.23: exactly the listed members differ; non-class entries: only manifest.json (items, recipes, lang, art =
               byte-identical: the frozen 103-row Enchanted table)
  B    bytes    every non-class entry of the 0.2.22 jar == the 0.2.23 jar's (Server/Item items + recipes, the lang files, Common art,
               the kit art) and manifest.json differs only in its version
  M    pages    EXECUTED on a REAL registry (CollReg.loadAll on a scratch folder) + a real counts file, recipe unlocks injected (CollReg.RECIPES):
       PAGES  every view BUILT through the real builders (Overview, a category, a short grown category, a collection with / without
              /craft, no recipe, 40 / 45 recipes, the error view): check_page, kit paths (+ the hub tab art), every b.set / binding names
              an element, SUI.assert_menu_page on the REAL commands (1600 x 980, row 1 + row 2, one sub row, no back button / < Menu,
              no pager, the content fits)
       SUB    the sub-tab row = the Python twin (SUI.sub_tab_markup) byte for byte: Overview | Farming | Mining | Foraging | Combat
              (+ the picked collection's name, selected, not bound); the clicks: a category sub-tab -> its list, Overview -> Home,
              the category sub-tab from a collection -> that category (was '< Back to <category>'), row 2's Collections tab -> Overview,
              row 1's own hub -> Overview; the old cback / chome clicks still work; the old pager clicks change nothing
       LIST   a category shows EVERY collection (no 12 a page), a card past the old first page opens its collection; a short category
              gets the bigger rows (HubBar.growSize = grow_pick); a short recipe list gets the bigger rows, 40+ rows the normal ones
       (0.2.22's checks kept) recipe rows sorted tier then name, NEW, CRAFT / Known / Tier V, forged / stale clicks, NONE, /recipes, FIT
  D    live     the setup's file steps TWICE on a scratch COPY of the live Skyy_SkyyCollections (no file changes), then every live
               profile's every visible collection page built (every b.set / binding names an element; assert_menu_page on a sample)
  AA   audit    the engine-access audit
Scratch: tools/dev/scratch/menuS1/coll/h (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, zipfile, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "ci"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import hub_tab_kit as HT
import skyyui as SUI

VERSION = "0.2.23"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-0.2.22.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menuS1", "coll", "h")))
PKG = "com.skyy.collections."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCollections")
EXPECT = {
    "CollPage": ["+f GRIDHS", "+f GRIDIN", "+f ROWGAP", "+f RPHS", "+f RPIN", "+f gk", "+m subRow", "-f CATBACK", "~<clinit>",
                 "~m build", "~m buildCat", "~m buildDetail", "~m buildHome", "~m card", "~m handleDataEvent", "~m recipePanel"],
    # the kit 1.7 HubBar (install_hub_bar row=True, page=True: kit 1.6 row + merged tabs + big rows + page17 / subTab / growSize / hasArt)
    "HubBar": ['+<clinit>', '+f ROW_IDS', '+f ROW_TITLES', '+m bigLab', '+m bigRow', '+m bigRowFill', '+m bigTabLab', '+m bigTabsFill', '+m build2', '+m buildRow', '+m def4', '+m defOf', '+m defTab', '+m goHub', '+m growSize', '+m hasArt', '+m hostOf', '+m hostShown', '+m hostTab', '+m hubs', '+m iconOf', '+m okIcon', '+m okItem', '+m openSub', '+m page17', '+m pickTab', '+m putIcon', '+m putSub', '+m route', '+m rowLab', '+m rowStyle', '+m rowWidth', '+m selOf', '+m subIcon', '+m subTab', '+m subTabs', '+m tabBStyle', '+m tabLab', '+m titleOf'],
    "SkyyCollectionsPlugin": ["~m setup"],                   # the ready line (version, page id)
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],      # the kit's version texts
}
ADDED = []
PREFIX = "SkyyCollF"
SUBTABS = ["Overview", "Farming", "Mining", "Foraging", "Combat"]
CRUMB_W = 300




def P_(n):
    from jpype import JClass
    return JClass(PKG + n)


def jstrs(xs):
    from jpype import JArray, JString
    return JArray(JString)(list(xs))


def ids_of(cmds):
    out = set()
    for ty, s, t, d in cmds:
        if t:
            out |= set(m.group(2) for m in HT.DECL_RE.finditer(t))
    return out


def sets_of(cmds):
    return dict((s, d) for ty, s, t, d in cmds if ty == "Set")


def txt(sets, sel):
    """the text a b.set line sends: the builder's data is JSON {"0": <value>}"""
    v = sets.get(sel)
    if v is None:
        return None
    try:
        j = json.loads(str(v))
        return j.get("0") if isinstance(j, dict) else j
    except ValueError:
        return str(v)


def binds(evs):
    return dict((s, t) for s, t in evs)


def kids(cmds, sel):
    """the markups appended into one element, in order"""
    return [t for ty, s, t, d in cmds if t is not None and s == sel]


def pcheck(K, built, what):
    """THE kit 1.7 page check on the REAL commands: check_page, kit paths (+ hub tab art), every b.set / binding names an element,
    SUI.assert_menu_page (1600 x 980, rows 1 + 2, one sub row, no back / < Menu / pager text, the content fits 676). Returns
    (w, h, sets {selector: data}, bindings [(selector, text)])."""
    cmds, evs = built
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, d) for ty, s, t, d in cmds if ty == "Set"]
    K.check(len(apps) > 8 and len(apps) + len(sets) == len(cmds), "%s: %d appends + %d sets" % (what, len(apps), len(sets)))
    try:
        SUI.check_page(apps, "SkyyC")
        K.check(True, "%s: check_page" % what)
    except Exception as e:
        K.check(False, "%s: check_page (markup rules, parents, no duplicate id): %s" % (what, e))
    try:
        els = SUI.check_sky_paths(apps, tab_icons=True)
        allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
        K.check(not [p for p in allp if p.startswith('"../')], "%s: no texture path leaves Common/UI/Custom (%d)" % (what, len(allp)))
        K.check({"Header", "HeaderOrnament", SUI.HUB_FRAME["character"], "Close"} <= set(els), "%s: the Sky Window page shell (%s)" % (what, sorted(els)))
    except Exception as e:
        K.check(False, "%s: sky paths: %s" % (what, e))
    ids = ids_of(cmds)
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s, _t in evs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(evs), bad[:4]))
    m = HT.WH_RE.search(apps[0][1])
    w, h = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    try:
        sh = SUI.hub_page(PREFIX, "character", sub=True, footer=True, content_id="SkyyColl", content_w=1216, content_layout="Top")
        info = SUI.assert_menu_page(apps, sh, what=what, sets=[(s, txt(dict(sets), s)) for s, _d in sets])
        K.check(info["rows"] == 2 and info["subs"] == 1, "%s: assert_menu_page (1600 x 980, rows 1 + 2, one sub row, no back button, no pager, content <= %d)" % (
            what, sh.content_h))
    except Exception as ex:
        K.check(False, "%s: assert_menu_page: %s" % (what, ex))
    K.eq((w, h), (1600, 980), "%s: the 1600 x 980 hub page" % what)
    K.check(not ({"SkyyCBack", "SkyyCHome", "SkyyCPrev", "SkyyCNext", "SkyyCPager", "SkyyCollFHubMenu", "SkyyCollFHubTabs"} & ids),
            "%s: no back / home / pager element, no kit 1.5 bar" % what)
    big = kids(cmds, "#" + PREFIX + "BigRow")
    tabs = [t for t in kids(cmds, "#" + PREFIX + "BigTabs") if t.startswith("Button")]
    K.check(len([t for t in big if t.startswith("Button")]) == 8 and len(tabs) >= 1, "%s: row 1 = Home + 7 hubs (%d), row 2 drawn (%d tabs)" % (
        what, len([t for t in big if t.startswith("Button")]), len(tabs)))
    labs = [t for ty, s, t, d in cmds if t and s and s.startswith("#" + PREFIX + "BigT") and 'Text: "Collections"' in t]
    K.check(bool(labs), "%s: row 2 shows the Collections tab" % what)
    return w, h, dict(sets), evs


def sub_expect(view, cat=0, crumb=None):
    """the sub-tab row the page must draw (the kit twin, byte for byte)"""
    out = []
    labs = [(lab, view == 0 if i == 0 else (view == 1 and cat == i - 1), SUI.SUB_TAB_W) for i, lab in enumerate(SUBTABS)]
    if crumb is not None:
        labs.append((crumb, True, CRUMB_W))
    for i, (lab, sel, w) in enumerate(labs):
        if i:
            out.append("Group { Anchor: (Width: %d); }" % SUI.SUB_TAB_GAP)
        out.append(SUI.sub_tab_markup(PREFIX, i, lab, sel, w))
    return out


HUB_DEFS = [(h, "Home" if h == "home" else SUI.hub_title_now(h), "Skyy_Menu") for h in SUI.HUB_ROW_IDS]


def put_defs(E):
    """the hub:def:<hub> keys SkyyMenu publishes (row 1 draws one button per def; without SkyyMenu it shows the hub title)"""
    from jpype import JClass
    for h, title, icon in HUB_DEFS:
        JClass(E.HB).def4(h, title, "skymenu", icon, None)


def rows_bytes(K, built, what, tabs):
    """row 1 + row 2 as built == the kit 1.7 Python twins (hub_big_row_preview / hub_big_tabs_preview), byte for byte"""
    apps = [(s.lstrip("#"), t_) for ty, s, t_, d in built[0] if t_ is not None and s]
    for nm, pv in (("row 1", SUI.hub_big_row_preview(PREFIX, HUB_DEFS, "character", SUI.HUB_PAGE_IW)),
                   ("row 2", SUI.hub_big_tabs_preview(PREFIX, "character", tabs, "collections"))):
        par = set(p for p, _m in pv)
        got = [(p, m_) for p, m_ in apps if p in par]
        K.check(got == [(p, SUI.render(m_)) for p, m_ in pv] and len(got) >= 2, "%s: %s == the kit twin byte for byte (%d appends)" % (what, nm, len(got)))


def stage_player(K, scratch, jar, sub, uid):
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    Reg, Store = P_("CollReg"), P_("CollStore")
    base = os.path.join(scratch, sub, "Skyy_SkyyCollections")
    os.makedirs(base, exist_ok=True)
    Reg.BASE = E.Paths.get(base)
    Store.DIR = Reg.BASE.resolve("counts")
    Reg.loadAll()
    K.check(Reg.D is not None and int(Reg.D.n) > 50, "the registry loaded (%s collections)" % (None if Reg.D is None else int(Reg.D.n)))
    P = E.mkp(E.UUID.fromString(uid), "CollMerge")
    P_("CollHubOpen").register()
    put_defs(E)
    return E, Reg, Store, P


def open_coll(E, P, c):
    P_("CollPage").openFor(P.pr, P.st, P.ref, c)
    E.pump(P)
    return E.pg(P)


def click(E, P, pg, word):
    pg.handleDataEvent(P.ref, P.st, '{"a":"%s"}' % word)
    E.pump(P)
    return E.pg(P)


# ------------------------------------------------------------------------------------------------------------------- B: the bytes
def run_bytes(out, jar, scratch, _home):
    K = HK.Child(out)
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    ea = sorted(n for n in za.namelist() if not n.endswith(".class"))
    eb = sorted(n for n in zb.namelist() if not n.endswith(".class"))
    K.eq(ea, eb, "B: the same non-class entries (%d)" % len(ea))
    diff = [n for n in ea if n in eb and za.read(n) != zb.read(n)]
    K.eq(diff, ["manifest.json"], "B: every non-class entry byte-identical but manifest.json")
    cnt = lambda pre: sum(1 for n in ea if n.startswith(pre))
    K.check(cnt("Server/Item/Items/") >= 103 and cnt("Server/Item/Recipes/") > 0 and any("/Languages/" in n or n.endswith(".lang") for n in ea),
            "B: items %d, recipes %d, lang files %d, art %d - all identical" % (cnt("Server/Item/Items/"), cnt("Server/Item/Recipes/"),
                                                                              sum(1 for n in ea if n.endswith(".lang")), cnt("Common/")))
    ma, mb = json.loads(za.read("manifest.json")), json.loads(zb.read("manifest.json"))
    dk = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
    K.check(dk == ["Name", "Version"] and (ma["Version"], ma["Name"]) == ("0.2.22", "0.2.22 SkyyCollections") and (mb["Version"], mb["Name"]) == (VERSION, VERSION + " SkyyCollections"),
            "B: manifest.json differs only in its version (Name '<version> SkyyCollections', Version) (%s)" % dk)
    K.check("103 Enchanted materials" in mb.get("Description", ""), "B: the manifest still names the frozen 103 Enchanted materials")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- M: the pages
def run_pages(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    E, Reg, Store, P = stage_player(K, scratch, jar, "merge", "00000000-0000-0000-0000-0000000000d2")
    u = P.pr.getUuid()
    R = Reg.D
    Tier, Page, New, Unl, Craft = P_("CollTier"), P_("CollPage"), P_("CollNew"), P_("CollUnlocks"), P_("CollCraft")
    HM, Long = JClass("java.util.HashMap"), JClass("java.lang.Long")
    HB = JClass(E.HB)
    K.eq([int(x) for x in Page.GRIDHS], SUI.grow_row_sizes(630, 88), "GROW the category row tiers = SUI.grow_row_sizes(630, 88)")
    K.eq([int(x) for x in Page.RPHS], SUI.grow_row_sizes(385, 32), "GROW the recipe row tiers = SUI.grow_row_sizes(385, 32)")
    for n_ in (1, 2, 3, 4, 5, 7, 12, 40):
        K.eq(int(HB.growSize(n_, int(Page.GRIDIN), Page.GRIDHS, int(Page.ROWGAP))), SUI.grow_pick(n_, 630, SUI.grow_row_sizes(630, 88)),
             "GROW HubBar.growSize(%d rows) = grow_pick" % n_)
    # ---------------------------------------------------------------- the collection + its injected recipe unlocks (0.2.22's set-up)
    c = int(R.byId.get("wheat"))
    none_c = int(R.byId.get("oaklog"))
    rc = {1: ["Ingredient_Bar_Iron_Recipe_Generated_0", "Zzz_Thing_Recipe_Generated_0"],
          2: ["Armor_Copper_Head_Recipe_Generated_0", "Armor_Copper_Chest_Recipe_Generated_0"],
          3: ["Ingredient_Bar_Iron_Recipe_Generated_0"], 5: ["Tool_Pickaxe_Mithril_Recipe_Generated_0"]}
    m = HM()
    for t, rs in rc.items():
        m.put("%d.%d" % (c, t), jstrs(rs))
    Reg.RECIPES = m
    d = Store.data(u)
    it = str(R.items[c][0])
    d.items.put(it, Long.valueOf(int(Reg.threshold(R, c, 2))))
    K.eq(int(Reg.tierOf(R, c, Store.sum(d, R, c))), 2, "M the player is at Wheat tier 2")
    un = Unl.compute(d)
    key = str(P_("CollUtil").pkey(u))
    E.CM.cmds.put("craft", E.U.allocateInstance(JClass("skyymenu19.Cmd").class_))
    # ---------------------------------------------------------------- OVERVIEW (Home)
    pg = open_coll(E, P, -1)
    K.check(pg is not None and int(pg.view) == 0, "HOME /collections opens Overview (view 0)")
    built = HT.build(pg, P)
    w, h, sets, evs = pcheck(K, built, "HOME")
    rows_bytes(K, built, "HOME", [("collections", "Collections")])
    hid, bd = ids_of(built[0]), binds(evs)
    K.eq(kids(built[0], "#SkyyCollFSub"), sub_expect(0), "SUB Overview: the sub-tab row = the kit twin (Overview selected)")
    K.check(all(("#SkyyCollFSub%d" % (i + 1)) in bd and ("ccat%d" % i) in bd["#SkyyCollFSub%d" % (i + 1)] for i in range(4)) and "chome" in bd.get("#SkyyCollFSub0", ""),
            "SUB the sub-tabs are bound: Overview chome, the categories ccat0-3")
    K.check("SkyyCRefresh" in hid and "SkyyCClose" in hid and "SkyyCStatus" in hid and "SkyyCRecipes" not in hid, "HOME the footer: the result line, Refresh, Close")
    K.check(all(("SkyyCCat%d" % i) in hid for i in range(4)), "HOME the 4 category cards keep their OPEN buttons")
    K.check("Open one to see its tiers and the recipes it unlocks." in str(txt(sets, "#SkyyCHint.Text") or ""), "HOME the hint (unchanged)")
    foot = [t for t in kids(built[0], "#SkyyCollFFoot") if t.startswith("TextButton")]
    K.check(len(foot) == 2 and "#SkyyCClose " in foot[-1] and "Height: 48" in foot[-1], "HOME the 48 px footer buttons, Close right-most")
    for old in ("crecipes", "clocked", "crgo0", "crcraft0", "ccraft1", "crprev", "cprev", "cnext"):
        cur = click(E, P, pg, old)
        K.check(E.same(cur, pg) and int(pg.view) == 0, "HOME an old click '%s' changes nothing" % old)
    # ---------------------------------------------------------------- a CATEGORY = one scroll list
    click(E, P, pg, "ccat2")
    K.check(int(pg.view) == 1 and int(pg.cat) == 2, "SUB the Foraging sub-tab opens its list (view 1, cat 2)")
    built = HT.build(pg, P)
    w, h, sets, evs = pcheck(K, built, "CATEGORY Foraging")
    K.eq(kids(built[0], "#SkyyCollFSub"), sub_expect(1, 2), "SUB Foraging: the sub-tab row = the kit twin (Foraging selected)")
    vis = [cc for cc in range(int(R.n)) if int(R.cat[cc]) == 2 and not bool(R.hidden[cc])]
    cids = ids_of(built[0])
    K.check(len(vis) > 12 and all(("SkyyCCd%d" % n_) in cids for n_ in range(len(vis))) and ("SkyyCCd%d" % len(vis)) not in cids,
            "LIST every Foraging collection on the one list (%d cards, the old page held 12)" % len(vis))
    grid = [t for ty, s, t, dd in built[0] if t and t.startswith("Group #SkyyCGrid ")]
    K.check(bool(grid) and "LayoutMode: TopScrolling" in grid[0] and "Height: 638" in grid[0], "LIST the list scrolls (TopScrolling, 638 px)")
    K.check(not any(t and "#SkyyCGRow" in t and "Height: 127" in t for ty, s, t, dd in built[0]), "LIST %d rows: the normal 88 px rows" % ((len(vis) + 1) // 2))
    K.eq(int(pg.gk), 0, "LIST a long list: grow tier 0")
    # a card past the old first page: discover 14 Foraging collections (discovered ones list first, in registry order) and open the 14th
    for cc in vis[:14]:
        d.items.put(str(R.items[cc][0]), Long.valueOf(1))
    built = HT.build(pg, P)
    evs = built[1]
    late = 13
    lc = int(pg.cards[late])
    K.eq(lc, vis[13], "LIST card 13 = the 14th discovered Foraging collection")
    K.check(("#SkyyCCard%d" % late) in binds(evs) and ("ccard%d" % late) in binds(evs)["#SkyyCCard%d" % late],
            "LIST card %d (past the old 12 a page) is bound ccard%d" % (late, late))
    click(E, P, pg, "ccard%d" % late)
    K.check(int(pg.view) == 2 and int(pg.coll) == lc, "LIST its OPEN click opens that collection (view 2, %s)" % R.id[lc])
    built = HT.build(pg, P)
    pcheck(K, built, "COLLECTION %s" % R.id[lc])
    K.eq(kids(built[0], "#SkyyCollFSub"), sub_expect(2, 2, str(SUI.hub_clean(str(R.name[lc])))), "SUB a collection: + its name, selected (the breadcrumb)")
    bd = binds(built[1])
    K.check("#SkyyCollFSub5" not in bd and "ccat2" in bd.get("#SkyyCollFSub3", ""), "SUB the breadcrumb is not bound; Foraging (its category) is")
    click(E, P, pg, "ccat2")
    K.check(int(pg.view) == 1 and int(pg.cat) == 2, "SUB the category sub-tab from a collection = its list (was '< Back to Foraging')")
    pg.view, pg.coll = 2, lc
    click(E, P, pg, "cback")
    K.check(int(pg.view) == 1, "SUB the old 'cback' click still leads to the category")
    click(E, P, pg, "chome")
    K.check(int(pg.view) == 0, "SUB Overview (chome) = Home")
    pg.view, pg.coll = 2, lc
    click(E, P, pg, "hub:collections")
    K.check(int(pg.view) == 0, "SUB row 2's Collections tab on a collection = Overview (HubBar.route 'self')")
    pg.view, pg.coll = 1, -1
    click(E, P, pg, "hub:h:character")
    K.check(int(pg.view) == 0, "SUB row 1's own hub (Character) = Overview")
    # a SHORT category grows its rows (rule 7): hide all but 3 Mining collections
    mine = [cc for cc in range(int(R.n)) if int(R.cat[cc]) == 1 and not bool(R.hidden[cc])]
    for cc in mine[3:]:
        R.hidden[cc] = True
    click(E, P, pg, "ccat1")
    built = HT.build(pg, P)
    pcheck(K, built, "CATEGORY Mining (3)")
    K.eq(int(pg.gk), SUI.grow_pick(2, 630, SUI.grow_row_sizes(630, 88)), "GROW 3 collections = 2 lines: the biggest tier")
    K.check(any(t and t.startswith("Group #SkyyCGRow0 ") and "Height: 176" in t for ty, s, t, dd in built[0])
            and any(t and t.startswith("Group #SkyyCCd0 ") and "Height: 176" in t for ty, s, t, dd in built[0]),
            "GROW the lines and the cards are 176 px (2x)")
    for cc in mine[3:8]:
        R.hidden[cc] = False
    click(E, P, pg, "ccat1")
    built = HT.build(pg, P)
    pcheck(K, built, "CATEGORY Mining (8)")
    K.eq(int(pg.gk), 1, "GROW 8 collections = 4 lines: the middle tier (127 px)")
    K.check(any(t and t.startswith("Group #SkyyCGRow0 ") and "Height: 127" in t for ty, s, t, dd in built[0]), "GROW the 127 px lines")
    for cc in mine:
        R.hidden[cc] = False
    # ---------------------------------------------------------------- the collection page (0.2.22's LIST checks on the kit page)
    pg = open_coll(E, P, c)
    K.check(pg is not None and int(pg.view) == 2 and int(pg.coll) == c, "LIST /collections wheat = the Wheat page (view 2)")
    New.mark(d, key, R, c, 1, 2)
    built = HT.build(pg, P)
    w, h, sets, evs = pcheck(K, built, "COLLECTION Wheat")
    rows_bytes(K, built, "COLLECTION Wheat", [("collections", "Collections")])
    K.eq(kids(built[0], "#SkyyCollFSub"), sub_expect(2, 0, "Wheat"), "SUB Wheat: Overview | the categories | WHEAT (selected)")
    bd = binds(evs)
    names = [txt(sets, "#SkyyCPr%dN.Text" % i) for i in range(5)]
    K.eq([n[5:] if n and n.startswith("NEW  ") else n for n in names],
         [str(P_("CollUtil").prettyRecipe(r)) for r in ("Zzz_Thing_Recipe_Generated_0", "Armor_Copper_Chest_Recipe_Generated_0", "Armor_Copper_Head_Recipe_Generated_0",
                                                          "Ingredient_Bar_Iron_Recipe_Generated_0", "Tool_Pickaxe_Mithril_Recipe_Generated_0")],
         "LIST the 5 rows in tier-then-name order (%s)" % names)
    K.check(all(n.startswith("NEW  ") for n in names[:4]), "LIST NEW before the 4 unlocked names")
    K.eq([txt(sets, "#SkyyCPr%dG.Text" % i) for i in range(5)], ["", "T2", "T2", "T3", "T7"], "LIST the tier tags")
    K.check(all(("#SkyyCPr%dGo" % i) in bd and "cpk%d" % i in bd["#SkyyCPr%dGo" % i] for i in range(4)) and "#SkyyCPr4Go" not in bd,
            "LIST the 4 unlocked rows have CRAFT (cpk<i>), the locked one none")
    K.eq(txt(sets, "#SkyyCPr4S.Text"), "Tier V", "LIST the locked Mithril pickaxe: 'Tier V'")
    rowmk = [t for ty, s, t, dd in built[0] if t and "#SkyyCPr4 " in t][:1]
    K.check(bool(rowmk) and rowmk[0].count(SUI.COLOR["disabled"]) >= 3, "LIST the locked row is greyed")
    K.eq(int(pg.gk), SUI.grow_pick(5, 385, SUI.grow_row_sizes(385, 32)), "GROW 5 recipes: the biggest recipe row tier")
    K.check(all(any(t and t.startswith("Group #SkyyCPr%d " % i) and "Height: 64" in t for ty, s, t, dd in built[0]) for i in range(5)),
            "GROW the 5 recipe rows are 64 px (2x)")
    gom = [t for ty, s, t, dd in built[0] if t and "TextButton #SkyyCPr0Go " in t]
    K.check(bool(gom) and "Top: 16" in gom[0] and "Height: 32" in gom[0], "GROW the CRAFT button stays 32 px, centred in the taller row")
    tiers = int(Reg.maxTier(R, c))
    rew = [txt(sets, "#SkyyCRew%d.Text" % t) for t in range(1, tiers + 1)]
    K.check(rew[0].startswith("2 recipes") and rew[1].startswith("2 recipes") and rew[2].startswith("1 recipe"), "LIST the tier cells: recipes by count (%s)" % (rew[:3],))
    tl = [t for ty, s, t, dd in built[0] if t and t.startswith("Group #SkyyCTiers ")]
    K.check(bool(tl) and "Height: 393" in tl[0] and "TopScrolling" in tl[0], "LIST the tier table scrolls, 393 px (0.2.22: 358)")
    K.check(int(P_("CollStore").meta(d, New.mkey(R, c))) == 0, "LIST the NEW markers are cleared once the page showed them")
    foot = [t for t in kids(built[0], "#SkyyCollFFoot") if t.startswith("TextButton")]
    K.check(len(foot) == 1 and "#SkyyCClose " in foot[0], "COLLECTION the footer: the result line + Close only (no Back / Home)")
    # ---------------------------------------------------------------- CRAFT (unchanged behaviour)
    E.CM.lines.clear()
    q0 = str(Craft.query(jstrs(["Armor_Copper_Chest_Recipe_Generated_0"]), un))
    click(E, P, pg, "cpk1")
    K.eq([str(x) for x in E.CM.lines], ["craft " + q0], "CRAFT row 1 (Copper chest) runs /craft searching for it as the player")
    pg = open_coll(E, P, c)
    HT.build(pg, P)
    E.CM.lines.clear()
    cur = click(E, P, pg, "cpk4")
    K.check(E.same(cur, pg) and not list(E.CM.lines) and str(pg.status) == "That recipe is not unlocked yet."
            and str(pg.statusColor(pg.status)) == SUI.COLOR["error"], "CRAFT a forged click on the locked row: nothing runs, a red 'not unlocked yet'")
    built = HT.build(pg, P)
    K.eq(txt(sets_of(built[0]), "#SkyyCStatus.Text"), "That recipe is not unlocked yet.", "CRAFT the result line (in the footer) says so")
    stm = [t for t in kids(built[0], "#SkyyCollFFoot") if "#SkyyCStatus " in t]
    K.check(bool(stm) and SUI.COLOR["error"] in stm[0], "CRAFT the footer's result line is red")
    cur = click(E, P, pg, "cpk9")
    K.check(E.same(cur, pg) and not list(E.CM.lines) and str(pg.status) == "That recipe is not on this page any more.", "CRAFT a stale row: the page says so")
    E.CM.cmds.remove("craft")
    pg = open_coll(E, P, c)
    built = HT.build(pg, P)
    sets, bd = sets_of(built[0]), binds(built[1])
    K.check([txt(sets, "#SkyyCPr%dS.Text" % i) for i in range(5)] == ["Known"] * 4 + ["Tier V"] and not any(k.endswith("Go") and "SkyyCPr" in k for k in bd),
            "CRAFT no /craft on the server: the unlocked rows say 'Known', no CRAFT button")
    pcheck(K, built, "COLLECTION (no /craft)")
    E.CM.cmds.put("craft", E.U.allocateInstance(JClass("skyymenu19.Cmd").class_))
    # ---------------------------------------------------------------- NONE + 40 / 45 recipes
    pg = open_coll(E, P, none_c)
    built = HT.build(pg, P)
    pcheck(K, built, "COLLECTION no recipe")
    K.check("SkyyCPrNone" in ids_of(built[0]) and "unlocks no recipes" in str(txt(sets_of(built[0]), "#SkyyCPrNone.Text")), "NONE the one grey line")
    m2 = HM()
    m2.put("%d.1" % c, jstrs(["Zz_Item%02d_Recipe_Generated_0" % i for i in range(45)]))
    Reg.RECIPES = m2
    pg = open_coll(E, P, c)
    built = HT.build(pg, P)
    pcheck(K, built, "COLLECTION 45 recipes")
    K.check(int(len(pg.prid)) == 40 and "SkyyCPr39" in ids_of(built[0]) and int(pg.gk) == 0, "LIST 45 recipes: 40 rows, the normal 32 px rows")
    K.eq(txt(sets_of(built[0]), "#SkyyCPrMore.Text"), "+5 more - /craft lists every recipe", "LIST 45 recipes: '+5 more'")
    Reg.RECIPES = m
    # ---------------------------------------------------------------- the ERROR view
    D0 = Reg.D
    Reg.D = None
    pg = open_coll(E, P, -1)
    built = HT.build(pg, P)
    pcheck(K, built, "ERROR")
    K.check("SkyyCErr" in ids_of(built[0]) and "#SkyyCClose" in binds(built[1]), "ERROR the error line + Close on the kit page")
    Reg.D = D0
    # ---------------------------------------------------------------- /recipes (unchanged)
    Cmd = P_("CollRecipesCmd")
    rcmd = Cmd()
    K.eq((str(rcmd.getName()), sorted(str(a) for a in (rcmd.getAliases() or []))), ("recipes", []), "CMD /recipes, no alias")
    Ctx = JClass("com.hypixel.hytale.server.core.command.system.CommandContext")
    ex = [mm for mm in Cmd.class_.getDeclaredMethods() if str(mm.getName()) == "execute" and len(mm.getParameterTypes()) == 5][0]
    ex.setAccessible(True)
    for line, view, coll in (("recipes", 0, None), ("recipes wheat", 2, c)):
        ex.invoke(rcmd, Ctx(rcmd, P.pr, line), P.st, P.ref, P.pr, None)
        E.pump(P)
        pg = E.pg(P)
        K.check(pg is not None and int(pg.view) == view and (coll is None or int(pg.coll) == coll), "CMD '/%s': the Collections page, view %d" % (line, view))
    # ---------------------------------------------------------------- the page id the build checked
    gen = open(os.path.join(HERE, "build_skyycollections_%s.py" % VERSION), encoding="utf8").read()
    mm_ = re.search(r'COLL_PAGE_CHECKED = "([0-9a-z]+)"', gen)
    plug = zipfile.ZipFile(jar).read("com/skyy/collections/SkyyCollectionsPlugin.class")
    pid = re.search(rb", page ([0-9a-f]{12})", plug)
    K.check(re.search(rb"\[SkyyCollections\] 0\.2\.23 ready", plug) is not None, "PAGE the ready line names 0.2.23")
    K.notes.append("PAGE id in the jar: %s; COLL_PAGE_CHECKED: %s" % (pid.group(1).decode() if pid else None, mm_.group(1) if mm_ else None))
    K.check(mm_ is not None and pid is not None and pid.group(1).decode() == mm_.group(1),
            "PAGE the jar's page id (ready line) = COLL_PAGE_CHECKED: %s vs %s" % (pid.group(1) if pid else None, mm_.group(1) if mm_ else None))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- D: live copy, twice
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    P_("CollHubOpen").register()
    put_defs(E)
    Reg, Store = P_("CollReg"), P_("CollStore")
    b_ = E.Paths.get(home)
    h0 = HK.tree_hash(home)
    msgs, hs = [], []
    for start in (1, 2):
        Reg.BASE = b_
        Store.DIR = b_.resolve("counts")
        r = [str(P_("CollBagMigrate").run(b_)), str(P_("CollBypassMig").run(b_)), str(P_("CollCoinMig").run(b_))]
        Reg.loadAll()
        r += [str(P_("CollCobMig").run(b_)), str(P_("CollSigMig").run(b_)), str(P_("CollShardMig").run(b_)), str(P_("CollToolMig").run(b_)),
              str(P_("CollRw21Mig").run(b_))]
        msgs.append(r)
        hs.append(HK.tree_hash(home))
    K.check(hs[0] == h0 and hs[1] == h0, "D both starts change no file of the live copy (%d files)" % len(h0))
    R = Reg.D
    out_ = JClass("java.util.HashMap")()
    for cc_ in range(int(R.n)):
        for t in range(1, int(Reg.maxTier(R, cc_)) + 1):
            toks = Reg.REWARDS.get(str(R.id[cc_]).lower() + "." + str(t))
            rs = [str(x)[7:] for x in (toks or []) if str(x).startswith("recipe:")]
            if rs:
                out_.put("%d.%d" % (cc_, t), jstrs(rs))
    P_("CollEnch").merge(out_, R, P_("CollEnch").present())
    Reg.RECIPES = out_
    keys = sorted(f[:-11] for f in os.listdir(os.path.join(home, "counts")) if f.endswith(".properties")) if os.path.isdir(os.path.join(home, "counts")) else []
    UU = JClass("java.util.UUID")
    pages, bad, sampled = 0, [], 0
    vis = [cc for cc in range(int(R.n)) if not bool(R.hidden[cc])]
    for k in keys:
        try:
            u = UU.fromString(k[:36])
        except Exception:
            continue
        if str(P_("CollUtil").pkey(u)) != k:
            continue
        P = E.mkp(u, "Live" + k[:4])
        for i, cc in enumerate(vis):
            pg = open_coll(E, P, cc)
            cmds, evs = HT.build(pg, P)
            ids = ids_of(cmds)
            miss = [s for s in sets_of(cmds) if s.lstrip("#").split(".")[0] not in ids] + [s for s, _t in evs if s.lstrip("#") not in ids]
            if miss or int(pg.view) != 2:
                bad.append("%s %s %s" % (k[:8], R.id[cc], miss[:2]))
            if i % 25 == 0 and sampled < 12:
                pcheck(K, (cmds, evs), "D live %s %s" % (k[:8], R.id[cc]))
                sampled += 1
            pages += 1
        for cat in range(4):           # every category list of the live profile
            pg = open_coll(E, P, -1)
            click(E, P, pg, "ccat%d" % cat)
            cmds, evs = HT.build(pg, P)
            if sampled < 20:
                pcheck(K, (cmds, evs), "D live %s category %d" % (k[:8], cat))
                sampled += 1
            nvis = sum(1 for cc in vis if int(R.cat[cc]) == cat)
            if not all(("SkyyCCd%d" % n_) in ids_of(cmds) for n_ in range(nvis)):
                bad.append("%s category %d: not every card" % (k[:8], cat))
    K.check(not bad, "D every live profile's collection pages + category lists build (%d pages, %d profiles): every b.set / binding names an element (%s)" % (
        pages, len(keys), bad[:3]))
    K.notes.append("D: %d live profile(s), %d collection pages built, %d visible collections, %d pages through assert_menu_page" % (len(keys), pages, len(vis), sampled))
    ch = sorted(k_ for k_, v_ in HK.tree_hash(home).items() if h0.get(k_) != v_)
    K.check(all(x.startswith("counts") for x in ch), "D the page builds changed no file but counts files (a shown NEW marker is cleared and saved): %s" % ch[:4])
    K.save()


if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("bytes", run_bytes), ("pages", run_pages), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyCollections"))
