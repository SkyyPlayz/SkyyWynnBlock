"""Harness for SkyyIslands 0.5.18 (MENU PATTERN sweep S3: the island menu on the kit 1.7 hub_page - 1600 x 980, row 1 + row 2 + the ONE
sub-tab row OVERVIEW | MEMBERS | PERMISSIONS | VISITORS | ISLAND (+ Refresh), scroll lists instead of pagers, short lists grow;
tools/islands_0_5_18_patch.py).
Build first: python tools/islands_0_5_18_patch.py && python SkyyIslands/build_skyyislands_0.5.18.py

    python SkyyIslands/test_skyyislands_0.5.18.py [--jar <jar>] [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; tools/hub_tab_kit.stage = the engine stand-ins with the REAL PageManager /
UICommandBuilder, -Xverify:all):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.5.17 -> 0.5.18: IslandMenuPage's build methods + rowG + hubClick, the kit 1.7 HubBar members, the version texts only;
                non-class entries: manifest.json
  PAGES every view BUILT through the real page and checked: SUI.check_page, the Sky paths, every b.set / binding names an element,
        SUI.assert_menu_page (1600 x 980, row 1 + row 2, ONE sub row, no Back / < Menu text, no pager, no kit 1.5 bar), the content
        column = role line + #SkyyIsBody (every child fits its 656 px) + result line; row 1 = Home + every hub (World selected), row 2
        = the World tabs (= hub_big_tabs_preview byte for byte, Island selected); the sub row = the kit's sub_tab_markup byte for byte
        (the open view selected + unbound, the others bound tabov / tabmem / tabperm / tabvis / tabisl) + Refresh (refresh);
        states: owner with few members / trusted / bans (rows GROW: HubBar.growSize = SUI.grow_pick), owner with 30 trusted + 250 bans
        (scroll, 200 rows + the '... and N more' line, no pager), a co-op member (read-only views), a player without an island (the
        create view, the other views' empty lines)
  CLICK the sub row switches views on the same page; Refresh; row 1 World = self (the page stays), row 1 Home runs /skymenu; the kit's
        bar clicks (hub_tab_kit.clicks: the own tab, a Function tab, the command fallback, hidden / missing, the X); bytecode:
        handleDataEvent -> hubClick -> HubBar.route, build -> HubBar.page17, buildTabs -> HubBar.subTab, the lists -> HubBar.growSize
  LOGIC 0.5.17 vs 0.5.18 SIDE BY SIDE (one child JVM each, the same scenario): ~45 page clicks - name box, invite, trust, accept,
        promote / demote, kick (arm + confirm), untrust, every permission toggle kind, reset permissions (arm + confirm), visit modes,
        visitor limit - / +, visit ping, PvP, mob spawning, unban, the old pager / Refresh list actions, every view switch - give the
        SAME result line, confirm arm, view, name box after every click, the SAME island files at the end and the SAME texts on every
        view (the 0.5.17 pager captions excepted)
  D    live: a scratch COPY of the live Skyy_SkyyIslands; the menu of one of its island owners, every view, assert_menu_page; no file
       of the copy changed
  AA   engine-access audit
Not testable without the game (UNVERIFIED): the client drawing the 1600 x 980 page, the grown rows, the sub row, the scroll wells.
Exit code 1 on any failure.
"""
import os, sys, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import hub_tab_kit as HT
import skyyui as SUI

VERSION = "0.5.18"
OLD = "0.5.17"
PKG = "com.skyy.islands."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menuS3", "islands", "harness")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyIslands")
PFX = "SkyyIsF"
SUBS = ["Overview", "Members", "Permissions", "Visitors", "Island"]
PAYS = ["tabov", "tabmem", "tabperm", "tabvis", "tabisl"]
FAIL_TEXT = "That tab could not open right now - try again."
# buildOverview: the invite row / Create button are 1552 wide now; buildIsland + hubAck are byte-identical
EXPECT = {"IslandMenuPage": ["+m rowG", "~m build", "~m buildTabs", "~m buildMembers", "~m buildPerms", "~m buildVisitors",
                             "~m buildOverview", "~m hubClick"],
          "SkyyIslandsPlugin": ["~m setup"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "IslandCfg": ["~m load"]}
EXPECT["HubBar"] = ["+<clinit>", "+f ROW_IDS", "+f ROW_TITLES"] + ["+m " + m for m in (     # the kit 1.7 members (row / sub / big / page)
    "bigLab", "bigRow", "bigRowFill", "bigTabLab", "bigTabsFill", "build2", "buildRow", "def4", "defOf", "defTab", "goHub", "growSize",
    "hasArt", "hostOf", "hostShown", "hostTab", "hubs", "iconOf", "okIcon", "okItem", "openSub", "page17", "pickTab", "putIcon", "putSub",
    "route", "rowLab", "rowStyle", "rowWidth", "selOf", "subIcon", "subTab", "subTabs", "tabBStyle", "tabLab", "titleOf")]


# 0.5.13's own button labels (kbtn: inline through safe(), live since 0.5.4 and seen in game): only the kit's stricter inline-text rule
# refuses their brackets / signs - blanked for check_page only (the 0.5.14 harness' legacy_texts)
LEGACY = re.compile(r'\A(Trust \(build only\)|Public \(anyone\)|Closed \(members only\)|Friends \(members \+ trusted\)|\+|Disband co-op \(\d+\))\Z')


def blank_legacy(apps):
    return SUI.Appends([(p, re.sub(r'Text: "((?:[^"\\]|\\.)*)"', lambda m: 'Text: ""' if LEGACY.match(m.group(1)) else m.group(0), mk)) for p, mk in apps])


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


def prep(J, Paths, home):
    from jpype import JClass
    J("IslandStore").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyIslands")
    b = Paths.get(home)
    J("IslandStore").DIR = b.resolve("islands")
    J("IslandCfg").FILE = b.resolve("config.properties")
    J("IslandCfg").load("Cow,Sheep,Pig,Chicken")
    J("IslandStore").HUB_FILE = b.resolve("hub.properties")
    J("IslandStore").loadHub()
    J("IslandStore").loadIslandWorlds()
    J("IslandStore").STOPPING = False


def setup(scratch, jar, home):
    from jpype import JClass, JArray, JObject
    os.makedirs(os.path.join(home, "islands"), exist_ok=True)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    J = lambda n: JClass(PKG + n)
    prep(J, E.Paths, home)
    Str = JClass("java.lang.String")
    for hid in SUI.HUB_ROW_IDS:
        title = "Home" if hid == SUI.HUB_HOME else SUI.hub_title_now(hid)
        cmd = "skymenu" if hid == SUI.HUB_HOME else SUI.HUB_DEFS[hid][1]
        E.bridge.put("hub:def:" + hid, JArray(JObject)([Str(title), Str(cmd), Str("Skyy_Menu")]))
    return E, J


def make_built(K, E):
    """build(pg, P, what) -> (cmds, evs, apps, sets) with the kit 1.7 page checks"""
    sh = SUI.hub_page(PFX, "world", sub=True, body_id="SkyyIsFB", content_id="SkyyIsRoot")

    def built(pg, P, what):
        cmds, evs = HT.build(pg, P)
        apps = SUI.Appends([(None if s_ is None else s_.lstrip("#"), t) for ty, s_, t, d in cmds if t is not None and ty and "Append" in ty])
        sets = [(s_, unq(d)) for ty, s_, t, d in cmds if ty == "Set"]
        K.check(len(apps) > 8 and len(apps) + len(sets) == len(cmds), "%s: %d appends + %d sets" % (what, len(apps), len(sets)))
        try:
            SUI.check_page(blank_legacy(apps), "SkyyIs")
            K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
        except Exception as e:
            K.check(False, "%s: check_page: %s" % (what, e))
        try:
            els = SUI.check_sky_paths(apps, tab_icons=True)
            K.check({"Header", "HeaderOrnament", SUI.HUB_FRAME["world"], "Close"} <= set(els), "%s: the Sky Window paths" % what)
        except Exception as e:
            K.check(False, "%s: sky paths: %s" % (what, e))
        ids = set()
        for _p, mk in apps:
            ids |= set(x.group(2) for x in HT.DECL_RE.finditer(SUI.render(mk)))
        bs = [s_ for s_, _t in evs]
        bad = [s_ for s_, _d in sets if s_.lstrip("#").split(".")[0] not in ids] + [s_ for s_ in bs if s_.lstrip("#") not in ids]
        K.check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
        try:
            info = SUI.assert_menu_page(apps, sh, what=what, sets=sets)
            K.check(info["rows"] == 2 and info["subs"] == 1, "%s: assert_menu_page (1600 x 980, rows 1 + 2, ONE sub row, no back button, no pager)" % what)
        except Exception as ex:
            K.check(False, "%s: assert_menu_page: %s" % (what, ex))
        try:
            used = SUI.used_height(SUI.Appends([(p, mk) for p, mk in apps if p == "SkyyIsBody"]), "SkyyIsBody")
            K.check(used <= 656, "%s: the view's content fits #SkyyIsBody (%d / 656 px)" % (what, used))
        except Exception as ex:
            K.check(False, "%s: body height: %s" % (what, ex))
        root = apps[0][1] if apps else ""
        K.check(apps and apps[0][0] is None and root.startswith("Group #%s { Anchor: (Width: 1600, Height: 980)" % PFX), "%s: the root 1600 x 980" % what)
        K.check(not [mk for _p, mk in apps if re.search(r"#SkyyIs(Tabs|TNav|BPg|VNav|Tp|Tn|Bp|Bn|TabOv|TabMem)\b", mk)],
                "%s: no old tab row / pager / nav row" % what)
        return cmds, evs, apps, dict(sets)
    return built


def kids(apps, parent):
    return [mk for p, mk in apps if p == parent]


def bound(evs, sel):
    return [t for s_, t in evs if s_ == sel]


def height_of(apps, ident):
    mk = [m_ for _p, m_ in apps if m_.startswith("Group #%s " % ident)]
    m = re.search(r"Height: (\d+)", mk[0]) if mk else None
    return int(m.group(1)) if m else None


def run_pages(out, jar, scratch, _home):
    from jpype import JClass, JArray, JInt
    K = HK.Child(out)
    home = os.path.join(scratch, "pages-mods", "Skyy_SkyyIslands")
    E, J = setup(os.path.join(scratch, "pages"), jar, home)
    HB, IS, PG, HO = J("HubBar"), J("IslandStore"), J("IslandMenuPage"), J("IslandHubOpen")
    built = make_built(K, E)
    K.check(int(HO.register()) == 1, "REG: IslandHubOpen.register puts hub:tab:world:island")
    HT.reg_check(K, E, "world", "island", "SkyyIslands", "Island", 20, "island menu", PKG + "IslandHubOpen")
    O = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000015b1"), "Owner")
    A = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000015b2"), "Alby")
    N = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000015b3"), "Nobody")
    u = O.pr.getUuid()
    hk = str(IS.homeKey(u))
    s = IS.settings(hk)
    s.world = "skyy-island-harness"                     # in memory only: the menu shows the owner's full island
    ka = str(IS.pkey(A.pr.getUuid()))

    def keys(n, tag):
        return ["00000000-0000-0000-%04d-%012d" % (tag, i) for i in range(n)]

    def set_lists(members, trusted, banned):
        s.members = ",".join(members)
        s.trusted = ",".join(trusted)
        s.banned = ",".join(banned)
        for k in members + trusted + banned:
            s.names.put(k, "P" + k[-4:])
    fn = HO()

    def open_page(X=None, tab=0):
        X = X or O
        r = fn.apply(X.pr.getUuid())
        E.pump(X)
        pg = E.pg(X)
        ok = r == E.TRUE and pg is not None and str(pg.getClass().getName()) == PKG + "IslandMenuPage"
        if ok and tab:
            pg.tab = tab
        return pg if ok else None

    tw = SUI.assert_big_tabs_fit("world", SUI.HUB_PAGE_IW)
    world_tabs = [str(t[0]) for t in HB.tabs("world", u)]
    K.eq(world_tabs, ["island"], "only the Island tab is registered in this JVM (row 2 = Island)")
    # ---------------------------------------------------------------- the owner, few entries: every view, rows grow
    set_lists([ka], keys(3, 1), keys(1, 2))
    hs = {"M": SUI.grow_row_sizes(223 - 8, 40, gap=3), "T": SUI.grow_row_sizes(255 - 8, 40, gap=3),
          "P": SUI.grow_row_sizes(555 - 8, 40, gap=3), "V": SUI.grow_row_sizes(488 - 8, 40, gap=3)}
    for t, name in enumerate(SUBS):
        pg = open_page(tab=t)
        K.check(pg is not None, "PAGE owner %s: the page opens (IslandHubOpen)" % name)
        c, e, apps, sets = built(pg, O, "PAGE owner few %s" % name)
        row1 = [mk for mk in kids(apps, PFX + "BigRow") if mk.startswith("Button")]
        K.eq(len(row1), len(SUI.HUB_ROW_IDS), "PAGE %s: row 1 = Home + every hub (%d buttons)" % (name, len(row1)))
        K.check(all(bound(e, "#%sBigR%d" % (PFX, i)) for i in range(len(row1))) and bound(e, "#%sHubClose" % PFX), "PAGE %s: row 1 + the X bound" % name)
        want2 = SUI.hub_big_tabs_preview(PFX, "world", [("island", "Island")], "island", w=SUI.HUB_PAGE_IW)
        got2 = [(p, mk) for p, mk in apps if p in (PFX + "BigTabs", PFX + "BigT0")]
        K.check(got2 == list(want2), "PAGE %s: row 2 = the kit's own markup (Island selected) byte for byte" % name)
        K.check([x for x in bound(e, "#%sBigT0" % PFX) if "hub:island" in x], "PAGE %s: row 2 Island bound hub:island" % name)
        sr = [mk for mk in kids(apps, PFX + "Sub") if mk.startswith("TextButton")]
        want_sr = [SUI.sub_tab_markup(PFX, i, SUBS[i], i == t) for i in range(5)]
        K.check(sr[:5] == want_sr and len(sr) == 6 and sr[5].startswith("TextButton #SkyyIsRef ") and 'Text: "Refresh"' in sr[5],
                "PAGE %s: the sub row = the kit's 5 sub-tabs (this one selected) + Refresh" % name)
        K.check(not bound(e, "#%sSub%d" % (PFX, t)) and all([x for x in bound(e, "#%sSub%d" % (PFX, i)) if PAYS[i] in x] for i in range(5) if i != t)
                and [x for x in bound(e, "#SkyyIsRef") if "refresh" in x], "PAGE %s: the open sub-tab unbound, the others + Refresh bound" % name)
        K.check("'s Island      Your role: Owner" in sets.get("#SkyyIsL1.Text", ""), "PAGE %s: the role line (%s)" % (name, sets.get("#SkyyIsL1.Text", "")[:60]))
        if name == "Members":
            K.check(height_of(apps, "SkyyIsMList") == 223 and height_of(apps, "SkyyIsTList") == 255, "PAGE Members: the two scroll wells 223 / 255")
            K.check(all("TopScrolling" in mk for mk in [m_ for _p, m_ in apps if m_.startswith("Group #SkyyIsMList ") or m_.startswith("Group #SkyyIsTList ")]),
                    "PAGE Members: both lists scroll")
            K.eq(height_of(apps, "SkyyIsMr0"), hs["M"][2], "PAGE Members: 2 members = the biggest rows (%s)" % hs["M"])
            K.check("Top: %d" % ((hs["M"][2] - 40) // 2) in [m_ for _p, m_ in apps if m_.startswith("Group #SkyyIsMr0 ")][0],
                    "PAGE Members: the grown row's content is centred (padding top)")
            K.eq(height_of(apps, "SkyyIsTr0"), hs["T"][2], "PAGE Members: 2 trusted rows = the biggest rows")
            K.check(any("SkyyIsPr1" in mk for mk in kids(apps, "SkyyIsMr1")) and any("SkyyIsKk1" in mk for mk in kids(apps, "SkyyIsMr1")),
                    "PAGE Members: Promote + Kick on the member row")
            K.check([x for x in bound(e, "#SkyyIsInvBtn") if "invite" in x] and [x for x in bound(e, "#SkyyIsTrustBtn") if "trust" in x],
                    "PAGE Members: Invite / Trust bound")
        if name == "Permissions":
            n = len(list(J("IslandPerms").LABELS))
            k = SUI.grow_pick(n, 547, hs["P"], gap=3)
            K.eq(height_of(apps, "SkyyIsPRow0"), hs["P"][k], "PAGE Permissions: %d rows -> tier %d" % (n, k))
            K.check(height_of(apps, "SkyyIsPList") == 555 and [x for x in bound(e, "#SkyyIsPc00v") if "pc00v" in x], "PAGE Permissions: the 555 px well, cells bound")
        if name == "Visitors":
            K.check(height_of(apps, "SkyyIsVList") == 488 and height_of(apps, "SkyyIsVRow0") == hs["V"][2], "PAGE Visitors: the 488 px well, 1 ban row grows")
            K.check([x for x in bound(e, "#SkyyIsVu0") if "vu0" in x] and not [mk for _p, mk in apps if "Refresh list" in mk], "PAGE Visitors: Unban bound, no nav row")
    # grow = the kit's grow_pick for 1..30 rows in every list
    for key, av in (("M", 215), ("T", 247), ("P", 547), ("V", 480)):
        jhs = JArray(JInt)(hs[key])
        bad = [n for n in range(1, 31) if int(HB.growSize(n, av, jhs, 3)) != SUI.grow_pick(n, av, hs[key], gap=3)]
        K.check(not bad, "GROW %s: HubBar.growSize = SUI.grow_pick for 1-30 rows (%s)" % (key, hs[key]))
    # ---------------------------------------------------------------- many entries: scroll, 200 rows + the more line, no pager
    set_lists([ka] + keys(4, 3), keys(30, 4), keys(250, 5))
    pg = open_page(tab=1)
    c, e, apps, sets = built(pg, O, "PAGE owner many Members")
    K.eq(len([mk for mk in kids(apps, "SkyyIsTList") if mk.startswith("Group #SkyyIsTr")]), 15, "MANY: 30 trusted = 15 rows, all in the well (no pager)")
    K.eq(height_of(apps, "SkyyIsTr0"), 40, "MANY: 15 rows do not fit bigger rows - 40 px, the list scrolls")
    K.eq(len([mk for mk in kids(apps, "SkyyIsMList") if mk.startswith("Group #SkyyIsMr")]), 6, "MANY: every co-op member (6) in the well (no 5-row cap)")
    pg = open_page(tab=3)
    c, e, apps, sets = built(pg, O, "PAGE owner many Visitors")
    K.eq(len([mk for mk in kids(apps, "SkyyIsVList") if mk.startswith("Group #SkyyIsVRow")]), 200, "MANY: 250 bans -> 200 rows in the well")
    K.check([v for k_, v in sets.items() if "and 50 more banned" in v], "MANY: the '... and 50 more banned' line")
    # ---------------------------------------------------------------- a co-op member: read-only views
    IS.MEMBER_OF.put(ka, hk)
    for t, name in enumerate(SUBS):
        pg = open_page(A, tab=t)
        if pg is None:
            K.check(False, "MEMBER %s: the page opens" % name)
            continue
        built(pg, A, "PAGE member %s" % name)
    # ---------------------------------------------------------------- no island
    for t, name in enumerate(SUBS):
        pg = open_page(N, tab=t)
        c, e, apps, sets = built(pg, N, "PAGE no island %s" % name)
        if t == 0:
            K.check([x for x in bound(e, "#SkyyIsCreate") if "create" in x], "NO ISLAND: Create my island bound")
    # ---------------------------------------------------------------- CLICK
    set_lists([ka], keys(3, 1), keys(1, 2))

    def click(pg, a, X=None):
        X = X or O
        pg.handleDataEvent(X.ref, X.st, '{"a":"%s"}' % a)
        E.pump(X)
        return E.pg(X)
    pg = open_page()
    for t in (1, 2, 3, 4, 0):
        cur = click(pg, PAYS[t])
        K.check(E.same(cur, pg) and int(pg.tab) == t, "CLICK: the sub row's %s switches the view on the same page" % SUBS[t])
    pg.info = "+x"
    cur = click(pg, "refresh")
    K.check(E.same(cur, pg) and str(pg.info) == "", "CLICK: Refresh redraws (result line cleared)")
    cur = click(pg, "hub:h:world")
    K.check(E.same(cur, pg), "CLICK: row 1 World = this hub - the page stays")
    E.CM.lines.clear()
    E.bridge.put("config:def:SkyyMenu", "stand-in")
    cur = click(pg, "hub:h:home")
    K.check([str(x) for x in E.CM.lines] == ["skymenu"], "CLICK: row 1 Home runs /skymenu (%s)" % list(E.CM.lines))
    E.CM.lines.clear()
    fk = HT.Fakes(E, "world")
    HT.clicks(K, E, O, open_page, "world", "island", "CLICK bar", fk, self_check=lambda p_: int(p_.tab) == 0, fail_text=FAIL_TEXT)
    fk.remove()
    # ---------------------------------------------------------------- CALLS (bytecode)
    import perfworld_kit as PW
    g = PW.calls(jar)
    K.check(PKG + "HubBar.route" in g.get("IslandMenuPage.hubClick", set()) and PKG + "HubBar.handle" not in g.get("IslandMenuPage.hubClick", set()),
            "CALLS: hubClick asks HubBar.route (row 1 + row 2 + the X)")
    K.check(PKG + "HubBar.page17" in g.get("IslandMenuPage.build", set()) and PKG + "HubBar.build" not in g.get("IslandMenuPage.build", set()),
            "CALLS: build -> HubBar.page17, no kit 1.5 HubBar.build")
    K.check(PKG + "HubBar.subTab" in g.get("IslandMenuPage.buildTabs", set()), "CALLS: buildTabs -> HubBar.subTab")
    K.check(all(PKG + "HubBar.growSize" in g.get("IslandMenuPage." + m, set()) for m in ("buildMembers", "buildPerms", "buildVisitors")),
            "CALLS: the three list views -> HubBar.growSize")
    gen = open(os.path.join(HERE, "build_skyyislands_%s.py" % VERSION), encoding="utf8").read()
    m = re.search(r'IS_PAGE_CHECKED = "([0-9a-f]{12})"', gen)
    import zipfile
    data = zipfile.ZipFile(jar).read("com/skyy/islands/SkyyIslandsPlugin.class")
    pid = re.search(rb"page ([0-9a-f]{12})", data)
    K.notes.append("page id in the jar: %s" % (pid.group(1).decode() if pid else None))
    K.check(m is not None and pid is not None and (m.group(1) == pid.group(1).decode() or jar.endswith("-UNCHECKED.jar")),
            "GATE: the built page id = IS_PAGE_CHECKED %s (or an -UNCHECKED harness jar: %s)" % (m and m.group(1), pid and pid.group(1)))
    HB.removeAll()
    K.save()


# ======================================================================================================== LOGIC: 0.5.17 vs 0.5.18
SCEN = [
    ("O", "tabmem", None), ("O", "name", "Alby"), ("O", "invite", "Alby"), ("O", "invite", ""), ("O", "trust", "Bea"), ("O", "trust", "Nobodyhere"),
    ("A", "acc", None), ("O", "refresh", None), ("O", "pr1", None), ("O", "dm1", None), ("O", "pr1", None), ("O", "kk1", None),
    ("O", "tabov", None), ("O", "kk1", None), ("O", "tabmem", None), ("O", "kk1", None), ("O", "kk1", None), ("O", "ut0", None),
    ("O", "tp", None), ("O", "tn", None), ("O", "tabperm", None), ("O", "pc00v", None), ("O", "pc00v", None), ("O", "pc03m", None),
    ("O", "pc05a", None), ("O", "pc99v", None), ("O", "pdef", None), ("O", "pdef", None), ("O", "tabvis", None), ("O", "vm0", None),
    ("O", "vm2", None), ("O", "vm1", None), ("O", "vlp", None), ("O", "vlp", None), ("O", "vlm", None), ("O", "vn", None), ("O", "vn", None),
    ("O", "vu0", None), ("O", "bp", None), ("O", "bn", None), ("O", "vr", None), ("O", "tabisl", None), ("O", "ipvp", None),
    ("O", "ipvp", None), ("O", "ispawn", None), ("O", "ispawn", None), ("O", "tabmem", None), ("O", "trust", "Alby"), ("O", "disb", None),
    ("O", "tabov", None), ("O", "reset", None)]
PAGER_TEXT = re.compile(r"\A(Page|Bans) \d+ / \d+\Z")


def run_logic(out, jar, scratch, _home, tag):
    from jpype import JClass
    K = HK.Child(out)
    home = os.path.join(scratch, "logic-" + tag, "Skyy_SkyyIslands")
    os.makedirs(os.path.join(home, "islands"), exist_ok=True)
    # the owner's island file (as /island writes it): world + a trusted player + two bans
    with open(os.path.join(home, "islands", "00000000-0000-0000-0000-0000000016c1.properties"), "w", encoding="latin-1", newline="\n") as f:
        f.write("v=5\nworld=skyy-island-harness\nownerName=Owner\ntrusted=00000000-0000-0000-0008-000000000001\n"
                "banned=00000000-0000-0000-0007-000000000001,00000000-0000-0000-0007-000000000002\n")
    E, J = setup(os.path.join(scratch, "logic-" + tag), jar, home)
    IS, PG = J("IslandStore"), J("IslandMenuPage")
    O = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000016c1"), "Owner")
    A = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000016c2"), "Alby")
    Bp = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000016c3"), "Bea")
    X = {"O": O, "A": A}
    u = O.pr.getUuid()
    hk = str(IS.homeKey(u))
    s = IS.settings(hk)
    K.check(str(s.world) == "skyy-island-harness" and int(IS.count(s.banned)) == 2, "LOGIC: the owner's island file is read (%s, %s)" % (s.world, s.banned))
    pages = {}
    rec = []

    def page_of(w):
        P = X[w]
        pg = E.pg(P)
        if pg is None or str(pg.getClass().getName()) != PKG + "IslandMenuPage":
            pg = PG(P.pr)
            P.pm.openCustomPage(P.ref, P.st, pg)
            E.pump(P)
            pg = E.pg(P)
        return pg

    def texts(pg, P):
        cmds, _evs = HT.build(pg, P)
        tx = [unq(d) for ty, s_, t, d in cmds if ty == "Set" and s_ and s_.endswith(".Text") and s_.startswith("#SkyyIsL")]
        for ty, s_, t, d in cmds:
            if t:
                tx += [m.group(2) for m in re.finditer(r'TextButton #(SkyyIs(?!Tab|Ref|FSub|FBig|FHub)[A-Za-z0-9]+) \{[^{}]*?Text: "((?:[^"\\]|\\.)*)"', t)]
        return sorted(x for x in tx if not PAGER_TEXT.match(x))
    for w, a, nm in SCEN:
        P = X[w]
        pg = page_of(w)
        d = {"a": a}
        if nm is not None:
            d["@IsName"] = nm
        try:
            pg.handleDataEvent(P.ref, P.st, json.dumps(d))
            E.pump(P)
        except Exception as ex:
            rec.append([w, a, "EXC %s" % ex])
            continue
        cur = E.pg(P)
        if cur is None:
            rec.append([w, a, "closed"])
            continue
        rec.append([w, a, str(cur.info), str(cur.confirm), int(cur.tab), str(cur.keepName)])
    views = {}
    for w in ("O", "A"):
        P = X[w]
        pg = page_of(w)
        for t in range(5):
            pg.tab = t
            views["%s%d" % (w, t)] = texts(pg, P)
    files = {}
    d_ = os.path.join(home, "islands")
    for f in sorted(os.listdir(d_)) if os.path.isdir(d_) else []:
        fp = os.path.join(d_, f)
        if os.path.isfile(fp):
            files[f] = "\n".join(ln for ln in open(fp, encoding="latin-1").read().splitlines() if not ln.startswith("#"))
    K.save(rec=rec, views=views, files=files)


def run_logic_old(out, jar, scratch, home):
    run_logic(out, OLD_JAR, scratch, home, "old")


def run_logic_new(out, jar, scratch, home):
    run_logic(out, jar, scratch, home, "new")
    K = HK.Child(out)
    a = json.load(open(os.path.join(scratch, "logicold.json")))
    b = json.load(open(out))
    ok = [r for r in b["rec"] if len(r) > 2 and r[2].startswith("+")]
    K.check(len(b["rec"]) == len(SCEN) and len(ok) >= 10, "LOGIC: %d clicks ran, %d answered with a success line" % (len(b["rec"]), len(ok)))
    diff = [(x, y) for x, y in zip(a["rec"], b["rec"]) if x != y]
    K.check(not diff and len(a["rec"]) == len(b["rec"]), "LOGIC: every click = 0.5.17's result line / arm / view / name box (%s)" % diff[:3])
    K.check(a["files"] == b["files"] and len(b["files"]) >= 1, "LOGIC: the island files at the end = 0.5.17's (%d files)" % len(b["files"]))
    # 0.5.18 drops the Visitors nav row's 'Refresh list' (vr still works; Refresh is in the sub row) - the one planned difference
    K.check(all(("Refresh list" in v) == (k[1] == "3" and k[0] == "O") for k, v in a["views"].items()) and
            not [k for k, v in b["views"].items() if "Refresh list" in v], "LOGIC: 'Refresh list' was 0.5.17's owner Visitors view only and is gone")
    for k in a["views"]:
        a["views"][k] = [x for x in a["views"][k] if x != "Refresh list"]
    vd = [k for k in a["views"] if a["views"][k] != b["views"].get(k)]
    for k in vd[:3]:
        K.notes.append("view %s: only 0.5.17 %s / only 0.5.18 %s" % (k, sorted(set(a["views"][k]) - set(b["views"][k]))[:6],
                                                                       sorted(set(b["views"][k]) - set(a["views"][k]))[:6]))
    K.check(not vd, "LOGIC: every view of the owner and the member shows 0.5.17's texts and buttons (the pager captions excepted): %s" % vd)
    for r in b["rec"]:
        K.notes.append("click %s" % r)
    K.save(rec=b["rec"], views=b["views"], files=b["files"])


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    h0 = HK.tree_hash(home)
    E, J = setup(os.path.join(scratch, "livepages"), jar, home)
    built = make_built(K, E)
    d = os.path.join(home, "islands")
    owners = [f[:-11] for f in sorted(os.listdir(d)) if f.endswith(".properties") and len(f) == 36 + 11] if os.path.isdir(d) else []
    K.check(bool(owners), "D: the live copy has island owners (%d)" % len(owners))
    if owners:
        P = E.mkp(E.UUID.fromString(owners[0]), "SkyyLive")
        for t, name in enumerate(SUBS):
            pg = J("IslandMenuPage")(P.pr)
            pg.tab = t
            P.pm.openCustomPage(P.ref, P.st, pg)
            E.pump(P)
            built(E.pg(P), P, "D live %s" % name)
    K.check(HK.tree_hash(home) == h0, "D: no file of the copy changed")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("pages", run_pages), ("logicold", run_logic_old), ("logicnew", run_logic_new), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyIslands"))
