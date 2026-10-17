"""Harness for SkyyMenu 0.3.35 (round K of the MENU PATTERN sweep: every Menu page on the kit 1.7 hub_page, no back buttons, Your Stats one
scroll list, Settings one scroll list per category, Server Setup crumbs, Settings drops Edit shortcuts; tools/menu_0_3_35_patch.py). Build first:
    python tools/menu_0_3_35_patch.py && python SkyyMenu/build_skyymenu_0.3.35.py

    python SkyyMenu/test_skyymenu_0.3.35.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py - the 0.3.34 harness's way: -Xverify:all over the SkyyMenu 0.3.19 engine stand-ins):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.34 -> 0.3.35: exactly the listed members differ
  M    EXECUTED:
       REG     Menu puts 6 tabs (no settings:layout), hub:art = the tab art it ships
       PAGES   every Menu page BUILT through the real builders - Home, Teleport, Players, a player, Mods, Settings, Server Setup (list,
               a mod, the change log, locked), Your Stats: page rules (check_page, kit paths, every b.set / binding has its element) +
               SUI.assert_menu_page (1600 x 980, row 1 + row 2, one sub row at most, no back button / < Menu, no pager but the grid's
               slot pages)
       BYTES   Home's row 1 and Teleport's rows 1 + 2 as built == the kit 1.7 previews (hub_big_row_preview / hub_big_tabs_preview)
       STATS   one list: the Main / Combat / Gathering heads, no Skills / Profile section, the YOUR STATS | SKILLS sub-tabs bound
       SETTINGS the categories in the sub row, every row of a category drawn (no pages), a short list uses the bigger row size, a sub-tab
               click switches the category, ON / OFF saves
       SETUP   the crumbs: list [All mods], a mod [All mods | the mod], the change log [All mods | Changes]; All mods leads to the list;
               the footer holds no back button
       LAYOUT  a saved Edit shortcuts shortcut still looks ok and opens the editor
       INFO    the classic info panel lines (mod bodies, view intros, player actions) at 15 px vs its 636 px text room
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (NewBetaTest): the registry, Home built both times; nothing written
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, time, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

_s29 = importlib.util.spec_from_file_location("test_skyymenu_0_3_29", os.path.join(HERE, "test_skyymenu_0.3.29.py"))
T29 = importlib.util.module_from_spec(_s29)
_s29.loader.exec_module(T29)
_s34 = importlib.util.spec_from_file_location("test_skyymenu_0_3_34", os.path.join(HERE, "test_skyymenu_0.3.34.py"))
T34 = importlib.util.module_from_spec(_s34)
_s34.loader.exec_module(T34)
T19 = T29.T19
build_page, jf = T29.build_page, T29.jf

VERSION = "0.3.35"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.34.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menuK", "menu")))
PKG = "com.skyy.menu."
LIVE_DIR = T34.LIVE_DIR
ADDED = []
SKYY = T34.SKYY
EXPECT = {
    'AdminPage': ['+m crumbAct', '+m crumbs', '~c ', '~m drawFileOnly', '~m drawHist', '~m drawIo', '~m drawList', '~m drawLog', '~m drawMod', '~m drawTable', '~m frame', '~m jump', '~m jumpTo', '~m tail'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~m header'],
    'HubBar': ['+m bigLab', '+m bigRow', '+m bigRowFill', '+m bigTabLab', '+m bigTabsFill', '+m growSize', '+m hasArt', '+m page17', '+m subTab'],
    'MenuData': ['+f ADM_ROWW', '+f ADM_ST0', '+f ADM_ST1', '+f ADM_ST2', '+f ADM_ST3', '+f ADM_SUBN', '+f ADM_SUBSEL', '+f ADM_SUBSTYLE', '+f CL_INFO_LINES', '+f STG_LIST_H', '+f STG_ROW_H', '+f STG_TAB_W', '+f UI_CCLOSE', '+f UI_CFSP', '+f UI_CGAP', '+f UI_CGRID', '+f UI_CGRIDNT', '+f UI_CGRIDWRAP', '+f UI_CHINT', '+f UI_CHINTST', '+f UI_CINFO', '+f UI_CINFOBOX', '+f UI_CINFODESC', '+f UI_CINFONAME', '+f UI_CNEXT', '+f UI_CNOPAGE', '+f UI_CPREV', '+f UI_HLEAD', '+f UI_SDESCB', '+f UI_SFSP', '+f UI_SNAMEB', '+f UI_SOFFB', '+f UI_SOFFSELB', '+f UI_SONB', '+f UI_SONSELB', '+f UI_SROWB', '+f UI_STXTB', '+f UI_TLEADY', '-f UI_BTNBACK', '-f UI_BTNNEXT', '-f UI_BTNPREV', '-f UI_SDESC', '-f UI_SFOOT', '-f UI_SGAP3', '-f UI_SLEADA', '-f UI_SLEADB', '-f UI_SMENU', '-f UI_SNAME', '-f UI_SNEXT', '-f UI_SOFF', '-f UI_SOFFSEL', '-f UI_SON', '-f UI_SONSEL', '-f UI_SPREV', '-f UI_SROW', '-f UI_SSP12', '-f UI_STAB', '-f UI_STABN', '-f UI_STABS0', '-f UI_STABS1', '-f UI_STABSEL', '-f UI_STABSELN', '-f UI_STXT', '~<clinit>'],
    'MenuHub': ['~m register'],
    'MenuPage': ['~m build', '~m buildDash', '~m fillPlayer', '~m foot', '~m look', '~m nav'],
    'OpsPage': ['~<clinit>'],
    'SettingsPage': ['~m build'],
    'SkyyMenuPlugin': ['~m setup'],
    'StatsCalc': ['+m allRows'],
    'StatsPage': ['~m build'],
}


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


def page_rules(K, cmds, evs, what, prefix_ok="Skyy"):
    """T29.page_rules with the hub tab art allowed (kit 1.7 row 2 draws SkyyHubTabs/<hub>_<tab>.png)"""
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, d) for ty, s, t, d in cmds if ty == "Set"]
    try:
        SUI.check_page(apps, prefix_ok)
        K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
    except Exception as e:
        K.check(False, "%s: check_page: %s" % (what, e))
    els = []
    try:
        els = SUI.check_sky_paths(apps, tab_icons=True)
        allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
        K.check(not [p for p in allp if p.startswith('"../')], "%s: no texture path leaves Common/UI/Custom (%d)" % (what, len(allp)))
    except Exception as e:
        K.check(False, "%s: sky paths: %s" % (what, e))
    for _p, mk in apps:
        if re.search(r"(Vertical|Horizontal)Alignment\s*:\s*(Top|Bottom|Left|Right)\b", mk):
            K.check(False, "%s: a Top/Bottom/Left/Right alignment: %s" % (what, mk[:80]))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in T29.DECL_RE.finditer(SUI.render(mk)))
    bs = [s for s, _t in evs]
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    return apps, els


def run_m(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls_m")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    home = os.path.join(scratch, "home_m")
    os.makedirs(os.path.join(home, "layouts"), exist_ok=True)
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(os.path.join(home, "layouts"))
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    JV("SetStore").DIR = Paths.get(os.path.join(home, "settings"))
    JV("SetReg").ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    JV("SetReg").registerOwn()
    JV("MenuIO").begin()
    HB, MH, MD = JV("HubBar"), JV("MenuHub"), JV("MenuData")
    br = JV("MenuUtil").bridge()
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = jf(UniC.class_, "playersByUuid").get(UniC.get())

    def mkp(uid, name):
        X = E.player(uid, name=name)
        byU.put(uid, X.pr)
        E.UniH.PL.add(X.pr)
        E.PLAYERS.add(X.pr)
        return X
    P = mkp(E.PLAIN, "SkyyPlain")
    O = mkp(E.OP, "SkyyOp")
    Q = mkp(JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000000c3"), "SkyyFriend")
    u = P.pr.getUuid()
    PGM = lambda X: X.pm.getCustomPage()

    def openp(X, pg):
        X.pm.openCustomPage(X.ref, X.st, pg)
        E.pump(X)
        return pg

    def click(X, pg, a, extra=""):
        pg.handleDataEvent(X.ref, X.st, '{"a":"%s"%s}' % (a, extra))
        E.pump(X)
        return PGM(X)

    def built(X, pg, what, hub, pager_ok=False):
        c, e = build_page(pg, X)
        apps, _els = page_rules(K, c, e, what)
        sets = [(s, unq(d)) for ty, s, t, d in c if ty == "Set"]
        try:
            info = SUI.assert_menu_page(apps, hub=hub, what=what, sets=sets, pager_ok=pager_ok)
            K.check(True, "%s: assert_menu_page (1600 x 980, rows %d, sub rows %d, no back button%s)" % (what, info["rows"], info["subs"],
                                                                                                          "" if pager_ok else ", no pager"))
        except Exception as ex:
            K.check(False, "%s: assert_menu_page: %s" % (what, ex))
        return c, e, apps, sets
    # ================================================================ REG
    n = int(MH.register())
    K.eq(n, 6, "REG: Menu puts its 6 own tabs (Settings dropped Edit shortcuts)")
    K.check(br.get("hub:tab:settings:layout") is None, "REG: no settings:layout tab")
    art = br.get("hub:art")
    K.check(art is not None and list(art) == list(MD.TAB_ART) and len(list(art)) > 20, "REG: hub:art = the tab art SkyyMenu ships (%d)" % (0 if art is None else len(list(art))))
    for n_ in ("profiles", "smithing", "reforge", "upgrade", "identify", "bazaar", "vault"):
        E.CM.cmds.put(n_, E.U.allocateInstance(JClass("skyymenu19.Cmd").class_))
    # ================================================================ PAGES
    hm = openp(P, JV("MenuPage")(P.pr, "main"))
    hc, he, happs, _hs = built(P, hm, "Home", "home", pager_ok=True)
    tp = openp(P, JV("MenuPage")(P.pr, "tp"))
    tc, te, tapps, _ts = built(P, tp, "Teleport", "world", pager_ok=True)
    pl = openp(P, JV("MenuPage")(P.pr, "players"))
    plc, ple, _pa, pls = built(P, pl, "Players", "social", pager_ok=True)
    K.check(not any("SkyyMBack" in str(s) for s, _d in ple) and not any(t and "SkyyMBack" in t for _ty, _s, t, _d in plc),
            "NOBACK: the Players page has no back button")
    pl.selU = Q.pr.getUuid()
    pl.open("player")
    pl.selU = Q.pr.getUuid()
    pc, pe, _pp, _ps = built(P, pl, "a player's page", "social", pager_ok=True)
    pg2 = click(P, pl, "hub:players")
    K.check(str(pl.view) == "players", "NOBACK: the Players tab (row 2) on a player's page leads back to the players list (%s)" % pl.view)
    md = openp(O, JV("MenuPage")(O.pr, "mods"))
    built(O, md, "Mods", "settings", pager_ok=True)
    # 12 switches of a test mod in a category that has none yet (more than the old 8-row page)
    S_, TRUE_ = JClass("java.lang.String"), JClass("java.lang.Boolean").TRUE
    ecat = [i for i in range(len(list(MD.SET_CAT_ID))) if len(list(JV("SetReg").visible(i, u))) == 0][0]
    for i_ in range(12):
        JV("SetReg").register(JArray(JObject)([S_("SkyyTest"), S_("test.row%d" % i_), S_("Test row %d" % i_), S_(str(MD.SET_CAT_ID[ecat])), TRUE_, S_("a test switch")]))
    sg = openp(P, JV("SettingsPage")(P.pr, -1))
    sgc, sge, sgapps, sgs = built(P, sg, "Settings", "settings")
    stp = openp(P, JV("StatsPage")(P.pr, 0))
    stc, ste, stapps, sts = built(P, stp, "Your Stats", "character")
    ad = openp(O, JV("AdminPage")(O.pr, "list", None))
    adc, ade, _aa, ads = built(O, ad, "Server Setup (list)", "settings", pager_ok=True)
    am = openp(O, JV("AdminPage")(O.pr, "mod", "SkyyMenu"))
    amc, ame, _ab, ams = built(O, am, "Server Setup (a mod)", "settings", pager_ok=True)
    al = openp(O, JV("AdminPage")(O.pr, "log", None))
    alc, ale, _ac, als = built(O, al, "Server Setup (change log)", "settings", pager_ok=True)
    lk = openp(P, JV("AdminPage")(P.pr, "list", None))
    built(P, lk, "Server Setup (locked)", "settings", pager_ok=True)
    # ================================================================ BYTES
    hubs = []
    for i in SUI.HUB_ROW_IDS:
        d = br.get("hub:def:" + i)
        hubs.append((i, str(d[0]), str(d[2])))
    rows1 = lambda cmds_, pre: [(s.lstrip("#"), t) for ty, s, t, d in cmds_ if t is not None and (s == "#%sBigRow" % pre or (s or "").startswith("#%sBigR" % pre)) and not (s or "").startswith("#%sBigRow" % pre + "T")]
    want = [(p_, SUI.render(mk)) for p_, mk in SUI.hub_big_row_preview("SkyyMHm", hubs, "home", 1552)]
    got = [(s, t) for s, t in rows1(hc, "SkyyMHm") if s != "SkyyMHmB" and not t.startswith("Group #SkyyMHmBigRow {")]
    K.check(got == want, "BYTES: Home's row 1 as built == the kit's hub_big_row_preview (%d / %d)" % (len(got), len(want)))
    wt = [(str(x[0]), str(x[1])) for x in HB.shown(HB.tabs("world", u), "teleport", 10)]
    want2 = [(p_, SUI.render(mk)) for p_, mk in SUI.hub_big_tabs_preview("SkyyMTp", "world", wt, "teleport", 1552, art=[str(x) for x in MD.TAB_ART])]
    got2 = [(s.lstrip("#"), t) for ty, s, t, d in tc if t is not None and ((s or "") == "#SkyyMTpBigTabs" or (s or "").startswith("#SkyyMTpBigT")) and not t.startswith("Group #SkyyMTpBigTabs {")]
    K.check(got2 == want2 and len(wt) >= 1, "BYTES: Teleport's row 2 as built == the kit's hub_big_tabs_preview (%d tabs, %d / %d commands)" % (len(wt), len(got2), len(want2)))
    K.check(any("SkyyHubTabs/world_teleport_on.png" in (t or "") for _ty, _s, t, _d in tc), "BYTES: the Teleport tab shows its art (hub:art)")
    # ================================================================ STATS
    heads = [unq(d) for ty, s, t, d in stc if ty == "Set" and re.match(r"#SkyyStatN\d+\.Text", s or "")]
    K.check(heads[:1] == ["Main"] and "Combat" in heads and "Gathering" in heads and "Profile" not in heads and "Skills" not in heads,
            "STATS: one list with the Main / Combat / Gathering heads, no Skills / Profile section (%s)" % heads[:3])
    K.check(not any((t or "").startswith("TextButton #SkyyStatTab") for _ty, _s, t, _d in stc), "STATS: no inner tab row")
    sb = dict((s, d) for s, d in ste)
    K.check("hub:stats" in str(sb.get("#SkyyStatFSub0")) and "hub:skills" in str(sb.get("#SkyyStatFSub1")), "STATS: the YOUR STATS | SKILLS sub-tabs are bound")
    K.check("#SkyyStatRefresh" in sb and "#SkyyStatClose" in sb and "#SkyyStatMenu" not in sb, "STATS: the footer = Refresh, Change Profile, Close (no menu button)")
    K.check(any((t or "").startswith("Group #SkyyStatList {") and "TopScrolling" in t for _ty, _s, t, _d in stc), "STATS: the list scrolls")
    # ================================================================ SETTINGS
    sub = [(s, t) for ty, s, t, d in sgc if (s or "") == "#SkyyStgHSub" and (t or "").startswith("TextButton")]
    vis = [i for i in range(len(list(MD.SET_CAT_ID))) if len(list(JV("SetReg").visible(i, u))) > 0]
    K.check(len(sub) == len(vis) >= 1, "SETTINGS: the categories are the sub-tab row (%d buttons, %d categories with rows)" % (len(sub), len(vis)))
    keys = list(sg.rowKeys)
    K.check(len(keys) == len(list(JV("SetReg").visible(int(sg.cat), u))) and len(keys) >= 1, "SETTINGS: every row of the category is drawn (%d) - no pages" % len(keys))
    K.check(not any("SkyyStgPrev" in (t or "") or "SkyyStgMenu" in (t or "") for _ty, _s, t, _d in sgc), "SETTINGS: no page buttons, no menu button")
    rh = [int(re.search(r"Height: (\d+)", t).group(1)) for _ty, s, t, _d in sgc if re.match(r"Group #SkyyStgRow\d+ ", t or "")]
    sz = int(HB.growSize(len(keys), int(MD.STG_LIST_H) - 8, MD.STG_ROW_H, 3))
    K.check(rh and all(h == list(MD.STG_ROW_H)[sz] for h in rh), "SETTINGS: %d rows drawn %d px high (size %d of %s - a short list grows)" % (len(rh), rh[0] if rh else -1, sz, list(MD.STG_ROW_H)))
    K.check(ecat in vis, "SETTINGS: the test mod's category shows in the sub row")
    click(P, sg, "stab%d" % ecat)
    K.check(int(sg.cat) == ecat and len(list(sg.rowKeys)) == 12, "SETTINGS: a sub-tab click switches the category - all 12 rows in ONE list (%d)" % len(list(sg.rowKeys)))
    c12, _e12 = build_page(sg, P)
    rh12 = [int(re.search(r"Height: (\d+)", t).group(1)) for _ty, s, t, _d in c12 if re.match(r"Group #SkyyStgRow\d+ ", t or "")]
    K.check(len(rh12) == 12 and set(rh12) == {list(MD.STG_ROW_H)[0]}, "SETTINGS: 12 rows = the normal row size, the list scrolls (%s)" % sorted(set(rh12)))
    k0 = str(sg.rowKeys[0])
    click(P, sg, "soff0")
    v0 = JV("SetStore").get(u, k0)
    K.check(v0 is not None and not v0.booleanValue(), "SETTINGS: OFF on row 0 saves (%s)" % k0)
    click(P, sg, "son0")
    # ================================================================ SETUP
    crumbs = lambda cmds_: [unq(re.search(r'Text: "([^"]*)"', t).group(1)) for _ty, s, t, _d in cmds_ if (s or "") == "#SkyyAdmHSub" and (t or "").startswith("TextButton")]
    K.eq(crumbs(adc), ["All mods"], "SETUP: the list's crumbs")
    K.eq(crumbs(amc), ["All mods", "Menu"], "SETUP: a mod's crumbs")
    K.eq(crumbs(alc), ["All mods", "Changes"], "SETUP: the change log's crumbs")
    ameb = dict((s, d) for s, d in ame)
    K.check("amods" in str(ameb.get("#SkyyAdmCr0")) and "#SkyyAdmCr1" not in ameb, "SETUP: on a mod, All mods is bound, the active crumb is not")
    for cm_, what in ((adc, "list"), (amc, "a mod"), (alc, "the log")):
        fb = [re.search(r'Text: "([^"]*)"', t).group(1) for _ty, s, t, _d in cm_ if (s or "") == "#SkyyAdmHFoot" and (t or "").startswith("TextButton")]
        K.check(fb and not any(SUI.MENU_BACK_RE.match(x) for x in fb) and "Close" in fb, "SETUP: the %s footer %s has no back button" % (what, fb))
    click(O, am, "amods")
    K.check(str(am.view) == "list", "SETUP: All mods leads to the mod list (%s)" % am.view)
    # ================================================================ LAYOUT
    hm2 = openp(P, JV("MenuPage")(P.pr, "main"))
    lk2 = hm2.look("tab:settings:layout", False)
    K.check(lk2 is not None and str(lk2[5]) == "ok" and str(lk2[1]) == "Edit shortcuts", "LAYOUT: a saved Edit shortcuts shortcut still looks ok (%s)" % (None if lk2 is None else [str(x) for x in lk2][:2]))
    hm2.shortcut(P.ref, P.st, "tab:settings:layout")
    E.pump(P)
    K.check(bool(hm2.editing) or str(hm2.status) == str(MD.EDIT_WAIT), "LAYOUT: ... and opens the editor (editing %s)" % hm2.editing)
    # ================================================================ INFO
    # every info text (mod bodies, view intros, player actions): its first line wraps in the description (0.3.34: 2 lines of a 728 px box,
    # 0.3.35: 4 lines of 636 px), the rest one 15 / 14 px line each (0.3.34: 728 px, 0.3.35: 636 px) - 0.3.35 must cut no more than 0.3.34
    bodies = []
    for arr in (MD.MOD_BODY, MD.V_INTRO, MD.PA_BODY):
        bodies.extend(str(t).replace("%P", "W" * 16).split("\n") for t in list(arr))
    cut = lambda room, dl: sum((1 if SUI.text_width(b[0], 16) > dl * room * 0.85 else 0) + sum(1 for ln in b[1:] if SUI.text_width(ln, 15) > room) for b in bodies)
    n_old, n_new = cut(728, 2), cut(636, 4)
    print("INFO: lines cut 0.3.34 %d, 0.3.35 %d (of %d texts)" % (n_old, n_new, len(bodies)))
    K.check(n_new <= n_old, "INFO: the classic info panel cuts no more text than 0.3.34 (%d <= %d)" % (n_new, n_old))
    MH.clearAll()
    JV("MenuIO").stop(2000)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hclasses_live")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(os.path.join(home, "layouts"))
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    JV("SetStore").DIR = Paths.get(os.path.join(home, "settings"))
    JV("Given").DIR = Paths.get(os.path.join(home, "given-profile"))
    JV("Given").LEGACY = Paths.get(os.path.join(home, "given"))
    JV("SetReg").ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    Cfg = JV("MenuCfg")
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = jf(UniC.class_, "playersByUuid").get(UniC.get())
    snaps = [T19.snap(home)]
    res = []
    for n_ in range(2):
        ML.OWN.clear()
        ML.MIGRATED.clear()
        JV("MenuIO").begin()
        Cfg.init()
        Cfg.load()
        ML.loadDefault()
        JV("SetReg").loadAdmin(True)
        JV("SetReg").registerOwn()
        JV("SetReg").drain()
        P = E.player(E.UUID.fromString(SKYY))
        byU.put(P.pr.getUuid(), P.pr)
        n = int(JV("MenuHub").register())
        JV("SetLoadTask").preload(P.pr)
        ML.preload(P.pr.getUuid())
        hm = JV("MenuPage")(P.pr, "main")
        P.pm.openCustomPage(P.ref, P.st, hm)
        E.pump(P)
        c, _e = build_page(hm, P)
        ok = len(c) > 10
        time.sleep(0.8)
        ML.flushAll()
        JV("SetStore").flushAll()
        JV("MenuIO").stop(2000)
        JV("MenuHub").clearAll()
        snaps.append(T19.snap(home))
        res.append([n >= 6, ok])
    K.eq(res, [[True, True], [True, True]], "D: two starts on a COPY of the live Skyy_SkyyMenu: registry + Home built")
    a, b1, b2 = snaps
    K.check(a == b1 == b2, "D: neither start wrote a file (changed: %s)" % sorted(set(k for k in set(a) | set(b2) if a.get(k) != b2.get(k))))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("m", run_m), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMenu"))
