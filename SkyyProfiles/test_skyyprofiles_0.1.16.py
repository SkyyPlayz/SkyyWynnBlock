"""Harness for SkyyProfiles 0.1.16 (MENU PATTERN sweep S1: both views on the kit 1.7 hub_page - 1600 x 980, row 1 + row 2 + the ONE
sub-tab row PROFILES | CREATE PROFILE, no Back, short card lists grow; tools/profiles_0_1_16_patch.py).
Build first: python tools/profiles_0_1_16_patch.py && python SkyyProfiles/build_skyyprofiles_0.1.16.py

    python SkyyProfiles/test_skyyprofiles_0.1.16.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.1.15 -> 0.1.16: ProfilePage buildList / buildCreate / handleDataEvent (+ LIST_HS / CREATE_HS), the kit 1.7 HubBar members
                (row / sub / big / page), the version texts only; non-class entries: manifest.json
  PAGES EXECUTED (tools/hub_tab_kit.stage: the engine stand-ins, the REAL PageManager / UICommandBuilder, -Xverify:all; hub:def rows
       for every hub as SkyyMenu puts them):
       REG    the Profiles tab key as 0.1.14 (register / unregister / setup / shutdown, bytecode)
       every view BUILT through the real builders and checked: SUI.check_page, the Sky paths, every b.set / binding names an element,
              SUI.assert_menu_page (1600 x 980, row 1 + row 2, ONE sub row, no Back / < Menu text, no pager, no kit 1.5 bar) - the
              first-profile Create view (picked / not picked), the profile list (footer / switch question / delete question / rename
              row), the Create view with a profile (picked / not picked)
       FIRST  no profile: row 2 = ONLY the Profiles tab (the kit's own markup at the full-row width, selected, bound hub:profiles) even
              with other Character tabs registered; the sub row = ONLY CREATE PROFILE (selected, unbound); the title 'Create your
              first profile'; Later (pfback) bound and closes with the reminder; row 1 Home / the X / Later leave with the reminder;
              the Profiles tab and row 1 Character keep the Create view
       LIST   row 2 = the visible Character tabs (= hub_big_tabs_preview byte for byte), Profiles selected; sub row PROFILES (selected,
              unbound) | CREATE PROFILE (pfnew) = the kit's sub_tab_markup byte for byte; the well 602 high, TopScrolling; few cards
              grow (3 cards = 184 px, 4 = 133 px, 7 = 92 px = HubBar.growSize = SUI.grow_pick)
       CLICK  the sub row's CREATE PROFILE -> the Create view (no Back button / binding, PROFILES bound hub:profiles); hub:profiles,
              row 1 Character and the old pfback -> the list; row 1 Home runs /skymenu; a switch question cleared by row 2; Close;
              the kit's bar clicks (hub_tab_kit.clicks: the own tab, a Function tab, the command fallback, hidden / missing, the X)
       CALLS  bytecode: handleDataEvent -> HubBar.route; both builds -> HubBar.page17 + subTab + growSize; no HubBar.build any more
  GATE / RB  test_skyyprofiles_0.1.15.py's HudGate / OpenTask / PageRedraw phase + 0.1.13's rebirth-busy phase on the 0.1.16 jar
             (RB with the SET pin's SkyyRebirth jar: its old SkyyRebirth 0.2 jar is tidied away)
  AA   engine-access audit
Not testable without the game (UNVERIFIED): the client drawing the 1600 x 980 page, the grown cards and the sub row.
Exit code 1 on any failure.
"""
import os, sys, re, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import hub_tab_kit as HT
import skyyui as SUI

VERSION = "0.1.16"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyProfiles-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyProfiles-0.1.15.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menuS1", "prof", "harness")))
PKG = "com.skyy.profiles."
EXPECT = {"ProfilePage": ["~<clinit>", "+f CREATE_HS", "+f LIST_HS", "~m buildCreate", "~m buildList", "~m handleDataEvent"],
          # the version texts only (constant pools checked)
          "SkyyProfilesPlugin": ["~m setup"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "ProfCfg": ["~m capMigrate"],
          "ProfDel": ["~m archiveLocked"]}
EXPECT["HubBar"] = ["+<clinit>", "+f ROW_IDS", "+f ROW_TITLES"] + ["+m " + m for m in (     # the kit 1.7 members (row / sub / big / page)
    "bigLab", "bigRow", "bigRowFill", "bigTabLab", "bigTabsFill", "build2", "buildRow", "def4", "defOf", "defTab", "goHub", "growSize",
    "hasArt", "hostOf", "hostShown", "hostTab", "hubs", "iconOf", "okIcon", "okItem", "openSub", "page17", "pickTab", "putIcon", "putSub",
    "route", "rowLab", "rowStyle", "rowWidth", "selOf", "subIcon", "subTab", "subTabs", "tabBStyle", "tabLab", "titleOf")]
ADDED = []
RB_VER = "0.3.4"         # the tools/deploy_set.py SET pin of SkyyRebirth
FAIL_TEXT = "That tab could not open right now - try again."
PFX = "SkyyPfF"
SUBS = ("Profiles", "Create profile")


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


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


def run_pages(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject, JInt
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    P_ = lambda n: JClass(PKG + n)
    Cfg, S, Del, HO, HB, PG = P_("ProfCfg"), P_("ProfStore"), P_("ProfDel"), P_("ProfHubOpen"), P_("HubBar"), P_("ProfilePage")
    home = os.path.join(scratch, "pages-mods", "Skyy_SkyyProfiles")
    os.makedirs(os.path.join(home, "players"), exist_ok=True)
    Paths = E.Paths
    Cfg.FILE = Paths.get(home, "config.properties")
    S.DIR, S.SWDIR, S.INVDIR, S.LOGF = Paths.get(home, "players"), Paths.get(home, "switching"), Paths.get(home, "inventories"), Paths.get(home, "switches.log")
    Del.ARCDIR = Paths.get(home, "archive")
    Str = JClass("java.lang.String")
    K.check(E.same(HB.map(), E.bridge), "the kit HubBar and the harness share ONE bridge map (skyy.bridge)")
    # row 1 as SkyyMenu publishes it: hub:def:<hub> = {title, command, icon item} for Home + every hub
    for hid in SUI.HUB_ROW_IDS:
        title = "Home" if hid == SUI.HUB_HOME else SUI.hub_title_now(hid)
        cmd = "skymenu" if hid == SUI.HUB_HOME else SUI.HUB_DEFS[hid][1]
        E.bridge.put("hub:def:" + hid, JArray(JObject)([Str(title), Str(cmd), Str("Skyy_Menu")]))
    # ---------------------------------------------------------------- REG (as 0.1.14)
    K.eq(str(HO.register()), "character:profiles", "REG: register() answers the tab it put")
    HT.reg_check(K, E, "character", "profiles", "SkyyProfiles", "Profiles", 80, "profiles", PKG + "ProfHubOpen")
    K.eq(int(HO.unregister()), 1, "REG: unregister() removes our 1 key")
    K.check(E.bridge.get("hub:tab:character:profiles") is None, "REG: the tab is gone after unregister()")
    HO.register()
    g = PW.calls(jar)
    K.check(PKG + "ProfHubOpen.register" in g.get("SkyyProfilesPlugin.setup", set()) and PKG + "ProfHubOpen.unregister" in g.get("SkyyProfilesPlugin.shutdown", set()),
            "REG: setup() / shutdown() call ProfHubOpen.register / unregister (bytecode)")
    # ---------------------------------------------------------------- CALLS
    for m in ("buildList", "buildCreate"):
        got = g.get("ProfilePage." + m, set())
        K.check({PKG + "HubBar.page17", PKG + "HubBar.subTab", PKG + "HubBar.growSize"} <= got and PKG + "HubBar.build" not in got,
                "CALLS: ProfilePage.%s -> HubBar.page17 + subTab + growSize, no kit 1.5 HubBar.build" % m)
    K.check(PKG + "HubBar.bigRowFill" in g.get("ProfilePage.buildCreate", set()) and PKG + "HubBar.hasArt" in g.get("ProfilePage.buildCreate", set()),
            "CALLS: the first-profile Create view draws row 1 itself (bigRowFill) + the Profiles tab art when loaded (hasArt)")
    hd = g.get("ProfilePage.handleDataEvent", set())
    K.check(PKG + "HubBar.route" in hd and PKG + "HubBar.handle" not in hd, "CALLS: handleDataEvent asks HubBar.route first (row 1 + row 2 + the X)")
    LHS, CHS = [int(x) for x in PG.LIST_HS], [int(x) for x in PG.CREATE_HS]
    K.eq(LHS, SUI.grow_row_sizes(602 - 8, 92, gap=4), "GROW: LIST_HS = the kit's grow_row_sizes for the 602 px well (%s)" % LHS)
    K.eq(CHS, SUI.grow_row_sizes(506 - 8, 92, gap=4), "GROW: CREATE_HS = the kit's grow_row_sizes for the 506 px well (%s)" % CHS)
    for n in range(1, 13):
        for av, hs in ((594, LHS), (498, CHS)):
            jhs = JArray(JInt)(hs)
            if int(HB.growSize(n, av, jhs, 4)) != SUI.grow_pick(n, av, hs, gap=4):
                K.check(False, "GROW: HubBar.growSize(%d, %d) != grow_pick" % (n, av))
    K.check(True, "GROW: HubBar.growSize = SUI.grow_pick for 1-12 cards in both wells")

    # ---------------------------------------------------------------- helpers
    def built(pg, P, what):
        cmds, evs = HT.build(pg, P)
        apps = SUI.Appends([(None if s_ is None else s_.lstrip("#"), t) for ty, s_, t, d in cmds if t is not None and ty and "Append" in ty])
        sets = [(s_, unq(d)) for ty, s_, t, d in cmds if ty == "Set"]
        K.check(len(apps) > 8 and len(apps) + len(sets) == len(cmds), "%s: %d appends + %d sets" % (what, len(apps), len(sets)))
        try:
            SUI.check_page(apps, "SkyyPf")
            K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
        except Exception as e:
            K.check(False, "%s: check_page: %s" % (what, e))
        try:
            els = SUI.check_sky_paths(apps, tab_icons=True)
            allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
            K.check(not [p for p in allp if p.startswith('"../')] and {"Header", "HeaderOrnament", SUI.HUB_FRAME["character"], "Close"} <= set(els),
                    "%s: the Sky Window paths, none leaves Common/UI/Custom (%d)" % (what, len(allp)))
        except Exception as e:
            K.check(False, "%s: sky paths: %s" % (what, e))
        ids = set()
        for _p, mk in apps:
            ids |= set(x.group(2) for x in HT.DECL_RE.finditer(SUI.render(mk)))
        bs = [s_ for s_, _t in evs]
        bad = [s_ for s_, _d in sets if s_.lstrip("#").split(".")[0] not in ids] + [s_ for s_ in bs if s_.lstrip("#") not in ids]
        K.check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
        try:
            info = SUI.assert_menu_page(apps, hub="character", what=what, sets=sets)
            K.check(info["rows"] == 2 and info["subs"] == 1, "%s: assert_menu_page (1600 x 980, rows 1 + 2, ONE sub row, no back button, no pager)" % what)
        except Exception as ex:
            K.check(False, "%s: assert_menu_page: %s" % (what, ex))
        root = apps[0][1] if apps else ""
        K.check(apps and apps[0][0] is None and root.startswith("Group #%s { Anchor: (Width: 1600, Height: 980)" % PFX), "%s: the root #%s 1600 x 980" % (what, PFX))
        return cmds, evs, apps, dict(sets)

    def kids(apps, parent):
        return [mk for p, mk in apps if p == parent]

    def bound(evs, sel):
        return [t for s_, t in evs if s_ == sel]

    def subrow(apps):
        return [mk for mk in kids(apps, PFX + "Sub") if mk.startswith("TextButton")]

    def well_of(apps):
        return [mk for _p, mk in apps if "#SkyyPfList " in mk]

    def card_h(apps, ident):
        mk = [m_ for _p, m_ in apps if m_.startswith("Group #%s " % ident)]
        m = re.search(r"Height: (\d+)", mk[0]) if mk else None
        return int(m.group(1)) if m else None

    def click(pg, P, a):
        n0 = len(list(E.sent(P)))
        pg.handleDataEvent(P.ref, P.st, '{"a":"%s"}' % a)
        E.pump(P)
        return E.pg(P), E.strs_of(P, n0)

    fn = HO()
    P = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000000f1"), "ProfPages")
    u = P.pr.getUuid()

    def open_page(X=None):
        X = X or P
        r = fn.apply(X.pr.getUuid())
        E.pump(X)
        pg = E.pg(X)
        return pg if (r == E.TRUE and pg is not None and str(pg.getClass().getName()) == PKG + "ProfilePage") else None
    fk = HT.Fakes(E, "character")
    vis = HT.hub_tabs(E, "character", u)
    K.eq(sorted(vis), ["fnno", "fnok", "profiles"], "3 Character tabs are registered and visible (Profiles + 2 stand-ins)")
    # ---------------------------------------------------------------- FIRST (no profile)
    pg = open_page()
    K.check(pg is not None and int(pg.view) == 1 and bool(pg.first), "FIRST: no profile = the Create view (first)")
    c, e, apps, sets = built(pg, P, "PAGE create (first, not picked)")
    tw = SUI.assert_big_tabs_fit("character", SUI.HUB_PAGE_IW)
    want = SUI.hub_big_tabs_preview(PFX, "character", [("profiles", "Profiles")], "profiles", w=tw)
    got = [(p, mk) for p, mk in apps if p in (PFX + "BigTabs", PFX + "BigT0")]
    K.check(got == list(want), "FIRST: row 2 = ONLY the Profiles tab, the kit's own markup at the full-row width %d px, selected (%s)" % (tw, [m_[:50] for _p, m_ in got]))
    K.check(not [p for p, mk in apps if p == PFX + "BigTabs" and "#%sBigT1 " % PFX in mk], "FIRST: no second tab in row 2")
    K.check([t for t in bound(e, "#%sBigT0" % PFX) if "hub:profiles" in t] and len(bound(e, "#%sBigT0" % PFX)) == 1, "FIRST: the tab bound to hub:profiles")
    sr = subrow(apps)
    K.check(sr == [SUI.sub_tab_markup(PFX, 0, SUBS[1], True)] and not bound(e, "#%sSub0" % PFX),
            "FIRST: the sub row = ONLY CREATE PROFILE, selected (the kit's sub_tab_markup), unbound (%s)" % [m_[:60] for m_ in sr])
    K.eq(sets.get("#%sTitle.Text" % PFX), "Create your first profile", "FIRST: the title says Create your first profile")
    rows1 = [mk for mk in kids(apps, PFX + "BigRow") if mk.startswith("Button")]
    K.eq(len(rows1), len(SUI.HUB_ROW_IDS), "FIRST: row 1 = Home + every hub (%d buttons)" % len(rows1))
    K.check(all(bound(e, "#%sBigR%d" % (PFX, i)) for i in range(len(rows1))) and bound(e, "#%sHubClose" % PFX), "FIRST: row 1 + the X bound")
    lat = [mk for _p, mk in apps if mk.startswith("TextButton #SkyyPfBack ")]
    K.check(len(lat) == 1 and 'Text: "Later"' in lat[0] and any("pfback" in t for t in bound(e, "#SkyyPfBack")), "FIRST: Later (pfback) is there and bound")
    ws = well_of(apps)
    K.check(len(ws) == 1 and "TopScrolling" in ws[0] and "Height: 506" in ws[0], "FIRST: the class list scrolls, 506 high")
    K.eq(card_h(apps, "SkyyPfCls0"), 92, "FIRST: 8 classes do not fit bigger cards - normal 92 px cards, the list scrolls")
    # picked (the Create profile button active)
    pg.handleDataEvent(P.ref, P.st, '{"a":"pfcls0"}')
    E.pump(P)
    c, e, apps, sets = built(pg, P, "PAGE create (first, picked)")
    K.check(any("pfmake" in t for t in bound(e, "#SkyyPfMake")) and any("pfback" in t for t in bound(e, "#SkyyPfBack")), "FIRST picked: Create profile + Later bound")
    cur, _t = click(pg, P, "hub:profiles")
    K.check(E.same(cur, pg) and int(pg.view) == 1 and bool(pg.first), "FIRST: the Profiles tab keeps the Create view")
    cur, _t = click(pg, P, "hub:h:character")
    K.check(E.same(cur, pg) and int(pg.view) == 1 and bool(pg.first), "FIRST: row 1 Character keeps the Create view")
    E.CM.lines.clear()
    cur, txt = click(pg, P, "hub:h:home")
    K.check([str(x) for x in E.CM.lines] == ["skymenu"] and "You have no profile yet" in txt,
            "FIRST: row 1 Home runs /skymenu + the first-profile reminder (as 0.1.14's '< Menu') (%s)" % list(E.CM.lines))
    E.CM.lines.clear()
    pg = open_page()
    cur, txt = click(pg, P, "pfback")
    K.check(cur is None and "You have no profile yet" in txt, "FIRST: Later closes + the first-profile reminder")
    pg = open_page()
    cur, txt = click(pg, P, "hub:close")
    K.check(cur is None and "You have no profile yet" in txt, "FIRST: the X closes + the first-profile reminder")
    # ---------------------------------------------------------------- LIST
    S.create(u, "1", "Banana", "Priest", True)
    S.create(u, "2", "Kiwi", "Mage", False)
    pg = open_page()
    K.check(pg is not None and int(pg.view) == 0 and not bool(pg.first), "LIST: a player with profiles = the profile list")
    c, e, apps, sets = built(pg, P, "PAGE list (2 profiles)")
    tabs_v = [("profiles", "Profiles"), ("fnok", "Fn Ok"), ("fnno", "Fn No")]
    want = SUI.hub_big_tabs_preview(PFX, "character", tabs_v, "profiles")
    got = [(p, mk) for p, mk in apps if p == PFX + "BigTabs" or (p or "").startswith(PFX + "BigT")]
    K.check(got == list(want), "LIST: row 2 = the visible Character tabs, Profiles selected = hub_big_tabs_preview byte for byte (%d)" % len(got))
    for k, (t, _l) in enumerate(tabs_v):
        K.check(any(("hub:" + t) in x for x in bound(e, "#%sBigT%d" % (PFX, k))), "LIST: row 2 tab %d bound to hub:%s" % (k, t))
    sr = subrow(apps)
    K.check(sr == [SUI.sub_tab_markup(PFX, 0, SUBS[0], True), SUI.sub_tab_markup(PFX, 1, SUBS[1], False)],
            "LIST: the sub row PROFILES (selected) | CREATE PROFILE = the kit's sub_tab_markup (%s)" % [m_[:50] for m_ in sr])
    K.check(not bound(e, "#%sSub0" % PFX) and any("pfnew" in t for t in bound(e, "#%sSub1" % PFX)), "LIST: PROFILES unbound (this view), CREATE PROFILE = pfnew")
    ws = well_of(apps)
    K.check(len(ws) == 1 and "TopScrolling" in ws[0] and "Height: 602" in ws[0], "LIST: the profile list scrolls, 602 high")
    K.check(any("Priest Banana - ACTIVE" in (d or "") for ty, s_, t, d in c), "LIST: the active profile card")
    K.check(card_h(apps, "SkyyPfCard1") == LHS[2] and card_h(apps, "SkyyPfCard2") == LHS[2] and card_h(apps, "SkyyPfNewCard") == LHS[2],
            "LIST GROW: 2 profiles + Create new = 3 cards at %d px (fills the well)" % LHS[2])
    K.eq(SUI.grow_pick(3, 594, LHS), 2, "LIST GROW: the Python twin agrees (3 cards -> the biggest tier)")
    S.create(u, "3", "Plum", "Archer", False)
    c, e, apps, sets = built(open_page(), P, "PAGE list (3 profiles)")
    K.check(card_h(apps, "SkyyPfCard1") == LHS[1] and card_h(apps, "SkyyPfNewCard") == LHS[1], "LIST GROW: 4 cards at %d px" % LHS[1])
    for i, (nm, cl) in enumerate((("Lime", "Warrior"), ("Pear", "Monk"), ("Date", "Assassin")), 4):
        S.create(u, str(i), nm, cl, False)
    c, e, apps, sets = built(open_page(), P, "PAGE list (6 profiles)")
    K.check(card_h(apps, "SkyyPfCard1") == 92 and card_h(apps, "SkyyPfCard6") == 92, "LIST GROW: 7 cards = normal 92 px cards, the list scrolls")
    # the question rows in the footer's place (every state is a whole menu page)
    pg = open_page()
    pg.handleDataEvent(P.ref, P.st, '{"a":"pfsw2"}')
    E.pump(P)
    K.check(str(pg.pending) == "2", "CLICK a switch question is open (pending 2)")
    c, e, apps, sets = built(pg, P, "PAGE list (switch question)")
    K.check(bound(e, "#SkyyPfYes") and bound(e, "#SkyyPfNo"), "PAGE list switch question: Confirm / Cancel bound")
    cur, _t = click(pg, P, "hub:profiles")
    K.check(pg.pending is None and int(pg.view) == 0, "CLICK the Profiles tab clears a pending switch question")
    pg.handleDataEvent(P.ref, P.st, '{"a":"pfdel2"}')
    E.pump(P)
    c, e, apps, sets = built(pg, P, "PAGE list (delete question)")
    K.check(str(pg.delAsk) == "2" and bound(e, "#SkyyPfDelYes") and bound(e, "#SkyyPfDelNo"), "PAGE list delete question: Delete / Cancel bound")
    cur, _t = click(pg, P, "hub:h:character")
    K.check(pg.delAsk is None and int(pg.view) == 0 and E.same(cur, pg), "CLICK row 1 Character = the list (clears the delete question)")
    pg.handleDataEvent(P.ref, P.st, '{"a":"pfren1"}')
    E.pump(P)
    c, e, apps, sets = built(pg, P, "PAGE list (rename row)")
    K.check(str(pg.renId) == "1" and bound(e, "#SkyyPfRenOk") and bound(e, "#SkyyPfRenF"), "PAGE list rename row: Save + the field bound")
    pg.handleDataEvent(P.ref, P.st, '{"a":"pfrnno"}')
    E.pump(P)
    # ---------------------------------------------------------------- CREATE (with a profile) through the sub row
    cur, _t = click(pg, P, "pfnew")
    K.check(E.same(cur, pg) and int(pg.view) == 1 and not bool(pg.first), "CLICK the sub row's CREATE PROFILE (pfnew) = the Create view")
    c, e, apps, sets = built(pg, P, "PAGE create (new, not picked)")
    sr = subrow(apps)
    K.check(sr == [SUI.sub_tab_markup(PFX, 0, SUBS[0], False), SUI.sub_tab_markup(PFX, 1, SUBS[1], True)]
            and any("hub:profiles" in t for t in bound(e, "#%sSub0" % PFX)) and not bound(e, "#%sSub1" % PFX),
            "CREATE: the sub row PROFILES (hub:profiles) | CREATE PROFILE (selected, unbound)")
    K.check(not [mk for _p, mk in apps if "#SkyyPfBack " in mk] and not bound(e, "#SkyyPfBack"), "CREATE: no Back button, no pfback binding")
    K.check(len([mk for p, mk in apps if p == PFX + "BigTabs" and mk.startswith("Button")]) == 3, "CREATE: row 2 = all 3 visible tabs (with a profile)")
    K.check(("#%sTitle.Text" % PFX) not in sets, "CREATE: the hub title stays (Character)")
    pg.handleDataEvent(P.ref, P.st, '{"a":"pfcls1"}')
    E.pump(P)
    c, e, apps, sets = built(pg, P, "PAGE create (new, picked)")
    mrow = [mk for p, mk in apps if p == "SkyyPfMakeRow"]
    K.check(len(mrow) == 2 and "#SkyyPfMakeRowQ " in mrow[0] and "#SkyyPfMake " in mrow[1] and any("pfmake" in t for t in bound(e, "#SkyyPfMake")),
            "CREATE picked: the make row = the question + Create profile only (%d parts)" % len(mrow))
    cur, _t = click(pg, P, "hub:profiles")
    K.check(E.same(cur, pg) and int(pg.view) == 0, "CLICK the sub row's PROFILES (hub:profiles) = back to the list")
    pg.handleDataEvent(P.ref, P.st, '{"a":"pfnew"}')
    E.pump(P)
    cur, _t = click(pg, P, "pfback")
    K.check(E.same(cur, pg) and int(pg.view) == 0, "CLICK the old pfback action still leads to the list")
    E.CM.lines.clear()
    cur, _t = click(pg, P, "hub:h:home")
    K.check([str(x) for x in E.CM.lines] == ["skymenu"], "CLICK row 1 Home runs /skymenu (%s)" % list(E.CM.lines))
    E.CM.lines.clear()
    pg = open_page()
    cur, _t = click(pg, P, "pfclose")
    K.check(cur is None, "CLICK the page's own Close still closes")

    def open_new():
        p_ = open_page()
        p_.handleDataEvent(P.ref, P.st, '{"a":"pfnew"}')
        E.pump(P)
        return p_
    HT.clicks(K, E, P, open_new, "character", "profiles", "CLICK create new", fk,
              self_check=lambda p_: int(p_.view) == 0 and str(p_.info) == "", fail_text=FAIL_TEXT)
    S.BROKEN.put(u, "x")
    K.check(fn.apply(u) == E.FALSE and "could not be read" in str(HO.LAST), "OPEN: an unreadable profile file = FALSE (%s)" % HO.LAST)
    S.BROKEN.remove(u)
    fk.remove()
    K.save()


def _old(name):
    def f(out, jar, scratch, home):
        if name == "gate":
            tmod("test_skyyprofiles_0.1.15.py", "tp0115").run_gate(out, jar, scratch, home)
        else:
            T13 = tmod("test_skyyprofiles_0.1.14.py", "tp0114").T13
            # its SkyyRebirth 0.2 jar is tidied away: the SET pin's SkyyRebirth jar (the same RbFn / RbStore.BUSY / RbCfg.BRIDGE)
            T13.RB_JAR = os.path.join(ROOT, "SkyyRebirth", "SkyyRebirth-%s.jar" % RB_VER)
            T13.run_rb(out, jar, scratch, home)
    return f


if __name__ == "__main__":
    HK.run(name="SkyyProfiles", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("pages", run_pages), ("gate", _old("gate")), ("rb", _old("rb"))], script=__file__)
