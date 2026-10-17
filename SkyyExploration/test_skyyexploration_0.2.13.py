"""Harness for SkyyExploration 0.2.13 (MENU PATTERN sweep S3, merge M12: World > Explore + the loot reveal page on the kit 1.7 hub_page -
1600 x 980, row 1 + row 2, the ONE sub-tab row Overview | Zones | Titles | Checklist, the checklist = an island list + ONE scroll list
(no '< Island / Island >', no pager), no '< Skills' / Close / '< Back'; tools/exploration_0_2_13_patch.py).
Build first: python tools/exploration_0_2_13_patch.py && python SkyyExploration/build_skyyexploration_0.2.13.py

    python SkyyExploration/test_skyyexploration_0.2.13.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.2.12 -> 0.2.13: ExplorePage (build / checklistTab / hubClick / handleDataEvent + CK_HS), LgReveal (build /
                 handleDataEvent + hubClick / hubOf / MAP_*), LgRvFn.sample (a text), the kit 1.7 HubBar members, the version texts;
                 non-class entries: manifest.json
  PAGES EXECUTED (tools/hub_tab_kit.stage: the engine stand-ins, the REAL PageManager / UICommandBuilder, -Xverify:all; hub:def rows for
        every hub as SkyyMenu puts them; three island checklists written as worlds/<wf>.properties):
        every built page checked: SUI.check_page, the Sky paths, every b.set / binding names an element, SUI.assert_menu_page (1600 x
        980, row 1 + row 2, at most ONE sub row, no Back / < Menu / pager text, no kit 1.5 bar):
        EXPLORE  the four sub-tabs (Overview, Zones, Titles, Checklist) as the sub row (= sub_tab_markup byte for byte; the selected one
                 unbound, the others extab<i>), row 2 = the World tabs with Explore selected, the level line, no '< Skills';
                 CHECKLIST the island list (one clickable row per island, the shown one selected, exwi<i>), the island's rows in ONE
                 scroll list (spots on the checklist then the entries, Done / -, the secret spot hidden), few rows grow (= SUI.grow_pick),
                 230 entries -> 200 rows + '... and 30 more'; exwi picks the island; the old pager clicks do nothing;
                 TITLES equip (Use -> 'Your title is now ...'), No title, a locked title refused; /title opens the Titles sub-tab
                 (TitleCmd -> ExplorePage tab 2, bytecode); the kit clicks (row 1 Home -> /skymenu, the X closes, own tab answered)
        REVEAL   a Loot Bag reveal (no back command): row 2 = World (Explore selected), the title = the bag, the footer Open all + Open
                 next (Primary), no Close / Back; Open next / Open all flip the cards (the buttons go when all are open); row 2's
                 Explore opens the Explore page; the X closes. An identify reveal (back 'identify'): row 2 = the Crafting tabs with
                 Identify selected, its own tab runs /identify (the old Back)
        CALLS    bytecode: both pages -> HubBar.page17 (+ subTab, growSize), HubBar.route first; no HubBar.build / handle any more
  RN, CAP     test_skyyexploration_0.2.12.py's phases on the 0.2.13 jar (the names; the Loot Bag gear cap = the luggage logic, EXECUTED)
  X           the 0.2.8 X phase (luggage: registry, placing, claims, the Sim engine, LgRvFn) on the 0.2.13 jar; its three reveal-page LOOK
              checks (Close / < Back buttons) are replaced by the REVEAL checks above
  D           live: start twice on a scratch COPY of the live Skyy_SkyyExploration (0.2.12 vs 0.2.13 records equal)
  AA          engine-access audit
Not testable without the game (UNVERIFIED): the client drawing the 1600 x 980 pages, the grown rows, the clickable island rows.
Exit code 1 on any failure.
"""
import os, sys, re, json, importlib.util, types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import hub_tab_kit as HT
import skyyui as SUI

VERSION = "0.2.13"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyExploration-0.2.12.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menuS3", "exploration", "harness")))
PKG = "com.skyy.explore."
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyExploration")   # the deploy world (2026-10-15)


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_rc = HK.run_compare
T12 = tmod("test_skyyexploration_0.2.12.py", "test_skyyexploration_0_2_12")
HK.run_compare = _rc                     # the 0.2.12 harness swaps the kit compare for the 0.2.8 one: ours is the kit's
T28 = T12.T28
T28.OLD_JAR = OLD_JAR                    # RN: jar entry names = 0.2.12's; D: 0.2.12 vs 0.2.13 records

EXPECT = {"ExplorePage": ["~<clinit>", "+f CK_HS", "~m build", "~m card", "~m checklistTab", "~m handleDataEvent", "~m hubClick", "~m titlesTab",
                          "~m zonesTab"],    # card / titlesTab / zonesTab: the 1552 px widths only
          "LgReveal": ["+<clinit>", "+f MAP_CMD", "+f MAP_HUB", "+f MAP_TAB", "~m build", "~m card", "~m handleDataEvent", "+m hubClick",
                       "+m hubOf"],    # card: the 300 px card width only
          "LgRvFn": ["~m sample"],
          # the version texts only (constant pools checked)
          "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "ExpCfg": ["~m load"], "ExpLgMig": ["~m logLine", "~m migrate"],
          "SkyyExplorationPlugin": ["~m setup"]}
EXPECT["HubBar"] = ["+<clinit>", "+f ROW_IDS", "+f ROW_TITLES"] + ["+m " + m for m in (     # the kit 1.7 members (row / sub / big / page)
    "bigLab", "bigRow", "bigRowFill", "bigTabLab", "bigTabsFill", "build2", "buildRow", "def4", "defOf", "defTab", "goHub", "growSize",
    "hasArt", "hostOf", "hostShown", "hostTab", "hubs", "iconOf", "okIcon", "okItem", "openSub", "page17", "pickTab", "putIcon", "putSub",
    "route", "rowLab", "rowStyle", "rowWidth", "selOf", "subIcon", "subTab", "subTabs", "tabBStyle", "tabLab", "titleOf")]
ADDED = []
FAIL_TEXT = "That tab could not open right now - try again."
TABS = ("Overview", "Zones", "Titles", "Checklist")
UUID0 = "00000000-0000-0000-0000-0000000000e1"


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


def prep(E, J, home):
    """the 0.2.10 harness's prep: the mod's folders in scratch, a recording scheduler (the page check is queued, never run)"""
    from jpype import JClass
    J("ExGuard").STOP = False
    J("ExGuard").EXEC = E.U.allocateInstance(E.RecEx.class_)
    J("ExpCfg").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyExploration")
    b = E.Paths.get(home)
    J("ExpCfg").FILE = b.resolve("config.properties")
    J("ExpStore").DIR = b.resolve("players")
    J("ChestReg").DIR = b.resolve("chests")
    J("SpotReg").DIR = b.resolve("worlds")
    J("ExpIO").ADMIN = b.resolve("admin.log")
    J("LgReg").DIR = b.resolve("luggage")
    J("ExpCfg").load()
    J("ChestReg").loadAll()
    J("SpotReg").loadAll()


def run_pages(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject, JInt, JString
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    J = lambda n: JClass(PKG + n)
    HB, EP, RV, RvF, HO = J("HubBar"), J("ExplorePage"), J("LgReveal"), J("LgRvFn"), J("ExpHubOpen")
    home = os.path.join(scratch, "pages-mods", "Skyy_SkyyExploration")
    os.makedirs(os.path.join(home, "worlds"), exist_ok=True)
    prep(E, J, home)
    Str = JClass("java.lang.String")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    K.check(E.same(HB.map(), E.bridge), "the kit HubBar and the harness share ONE bridge map (skyy.bridge)")
    for hid in SUI.HUB_ROW_IDS:
        title = "Home" if hid == SUI.HUB_HOME else SUI.hub_title_now(hid)
        cmd = "skymenu" if hid == SUI.HUB_HOME else SUI.HUB_DEFS[hid][1]
        E.bridge.put("hub:def:" + hid, JArray(JObject)([Str(title), Str(cmd), Str("Skyy_Menu")]))
    K.eq(int(HO.register()), 1, "REG: the World > Explore tab is put (as 0.2.10)")
    P = E.mkp(E.UUID.fromString(UUID0), "ExpPages")
    u = P.pr.getUuid()
    E.bridge.put("hub:last:" + str(u), CHM())
    wn = str(P.st.getExternalData().getWorld().getName())
    WF = J("ChestReg").wf
    # three island checklists: the player's own world (3 spots on the checklist - 1 secret - + 2 entries), "Beta Isle" (1 entry),
    # "Zeta Reach" (230 custom entries: the 200-row cap)
    isl = [(wn, "Home Isle", ["spot.s1=10 64 10|8|100|false|true|Old Well", "spot.s2=20 64 20|8|150|true|true|Hidden Grotto",
                               "spot.s3=30 64 30|8|200|false|true|Sky Pillar", "spot.s4=40 64 40|8|50|false|false|Off List",
                               "check.1=custom||Ring the old bell", "check.2=chests|3|Open 3 loot chests"]),
           ("betaisle", "Beta Isle", ["check.3=custom||Find the lighthouse"]),
           ("zetareach", "Zeta Reach", ["check.%d=custom||Task number %d" % (100 + i, i) for i in range(1, 231)])]
    for world, name, lines in isl:
        with open(os.path.join(home, "worlds", str(WF(world)) + ".properties"), "w", encoding="utf8") as f:
            f.write("world=%s\nname=%s\nchecklist=true\nreward.xp=500\nreward.coins=0\nspotXp=-1\nsecretXp=-1\n%s\n" % (world, name, "\n".join(lines)))
    J("SpotReg").loadAll()
    K.eq(sorted(str(x) for x in EP.islands(str(WF(wn)))), sorted(str(WF(w_)) for w_, _n, _l in isl), "the three island checklists are loaded")
    d = J("ExpStore").dataK(J("ExpIO").pkey(u), u)
    fm = CHM()
    fm.put("s1", JClass("java.lang.Long")(1))
    d.found.put(str(WF(wn)), fm)                    # the player found Old Well
    d.chests = 1000000                              # every loot-chest title earned
    g = PW.calls(jar)
    rows_hs = [int(x) for x in EP.CK_HS]
    K.eq(rows_hs, SUI.grow_row_sizes(633 - 30 - 26 - 26 - 8, 44, gap=3), "GROW: CK_HS = the kit's grow_row_sizes for the 543 px list room (%s)" % rows_hs)
    for n in range(1, 30):
        if int(HB.growSize(n, 543, JArray(JInt)(rows_hs), 3)) != SUI.grow_pick(n, 543, rows_hs, gap=3):
            K.check(False, "GROW: HubBar.growSize(%d) != grow_pick" % n)
    K.check(True, "GROW: HubBar.growSize = SUI.grow_pick for 1-29 rows")

    # ---------------------------------------------------------------- helpers
    def built(pg, what, hub="world", prefix="SkyyExF", subs=1):
        cmds, evs = HT.build(pg, P)
        apps = SUI.Appends([(None if s_ is None else s_.lstrip("#"), t) for ty, s_, t, d_ in cmds if t is not None and ty and "Append" in ty])
        sets = [(s_, unq(d_)) for ty, s_, t, d_ in cmds if ty == "Set"]
        K.check(len(apps) > 8 and len(apps) + len(sets) == len(cmds), "%s: %d appends + %d sets" % (what, len(apps), len(sets)))
        try:
            SUI.check_page(apps, prefix[:6])
            K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
        except Exception as e:
            K.check(False, "%s: check_page: %s" % (what, e))
        try:
            els = SUI.check_sky_paths(apps, tab_icons=True)
            allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
            K.check(not [p for p in allp if p.startswith('"../')] and {"Header", "HeaderOrnament", SUI.HUB_FRAME[hub], "Close"} <= set(els),
                    "%s: the Sky Window paths (%s frame), none leaves Common/UI/Custom (%d)" % (what, hub, len(allp)))
        except Exception as e:
            K.check(False, "%s: sky paths: %s" % (what, e))
        ids = set()
        for _p, mk in apps:
            ids |= set(x.group(2) for x in HT.DECL_RE.finditer(SUI.render(mk)))
        bs = [s_ for s_, _t in evs]
        bad = [s_ for s_, _d in sets if s_.lstrip("#").split(".")[0] not in ids] + [s_ for s_ in bs if s_.lstrip("#") not in ids]
        K.check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
        try:
            info = SUI.assert_menu_page(apps, hub=hub, what=what, sets=sets)
            K.check(info["rows"] == 2 and info["subs"] == subs, "%s: assert_menu_page (1600 x 980, rows 1 + 2, %d sub row, no back button, no pager)" % (what, subs))
        except Exception as ex:
            K.check(False, "%s: assert_menu_page: %s" % (what, ex))
        root = apps[0][1] if apps else ""
        K.check(apps and apps[0][0] is None and root.startswith("Group #%s { Anchor: (Width: 1600, Height: 980)" % prefix), "%s: the root #%s 1600 x 980" % (what, prefix))
        txt = " ".join(str(t) for _ty, _s, t, _d in cmds if t) + " " + " ".join(v for _s, v in sets)
        K.check(not re.search(r'Text: "(< ?Skills|< ?Back|Close|< ?Menu|< Island|Island >)"', txt) and "page 1 of" not in txt,
                "%s: no '< Skills' / '< Back' / Close / '< Menu' / island switcher / page pager" % what)
        return cmds, evs, apps, dict(sets)

    def kids(apps, parent):
        return [mk for p, mk in apps if p == parent]

    def bound(evs, sel):
        return [t for s_, t in evs if s_ == sel]

    def click(pg, a):
        n0 = len(list(E.sent(P)))
        pg.lastBuild = 0                       # past the page's 1 s click guard
        pg.handleDataEvent(P.ref, P.st, '{"a":"%s"}' % a)
        E.pump(P)
        return E.pg(P), E.strs_of(P, n0)

    def open_tab(t):
        pg = EP(P.pr, t)
        P.pm.openCustomPage(P.ref, P.st, pg)
        E.pump(P)
        return pg

    def hgt(apps, ident):
        mk = [m_ for _p, m_ in apps if re.match(r"(Group|Label|Button|TextButton) #%s " % ident, m_)]
        m = re.search(r"Height: (\d+)", mk[0]) if mk else None
        return int(m.group(1)) if m else None

    # ---------------------------------------------------------------- EXPLORE: the four sub-tabs
    world_tabs = [(r[0], SUI.hub_tab_label("world", r[0])) for r in SUI.hub_page_tabs("world") if r[0] == "explore"]
    for t, name in enumerate(TABS):
        pg = open_tab(t)
        c, e, apps, sets = built(pg, "EXPLORE %s" % name)
        sr = [mk for mk in kids(apps, "SkyyExFSub") if mk.startswith("TextButton")]
        K.check(sr == [SUI.sub_tab_markup("SkyyExF", i, TABS[i], i == t) for i in range(4)],
                "EXPLORE %s: the sub row = OVERVIEW | ZONES | TITLES | CHECKLIST (the kit's sub_tab_markup, %s selected)" % (name, name))
        K.check(not bound(e, "#SkyyExFSub%d" % t) and all(any(("extab%d" % i) in x for x in bound(e, "#SkyyExFSub%d" % i)) for i in range(4) if i != t),
                "EXPLORE %s: the selected sub-tab unbound, the others extab<i>" % name)
        want = SUI.hub_big_tabs_preview("SkyyExF", "world", world_tabs, "explore")
        got = [(p, mk) for p, mk in apps if p == "SkyyExFBigTabs" or (p or "").startswith("SkyyExFBigT")]
        K.check(got == list(want), "EXPLORE %s: row 2 = the World tabs registered (Explore) selected = hub_big_tabs_preview byte for byte" % name)
        K.check(any("hub:explore" in x for x in bound(e, "#SkyyExFBigT0")) and bound(e, "#SkyyExFHubClose")
                and len([mk for mk in kids(apps, "SkyyExFBigRow") if mk.startswith("Button")]) == len(SUI.HUB_ROW_IDS),
                "EXPLORE %s: row 1 = Home + every hub, row 2 bound, the X bound" % name)
        K.check(str(sets.get("#SkyyExLvl.Text", "")).startswith("SkyySkills not installed") or "Exploration" in str(sets.get("#SkyyExLvl.Text", "")),
                "EXPLORE %s: the level line at the right of the sub row (%s)" % (name, sets.get("#SkyyExLvl.Text")))
        K.check(not [mk for _p, mk in apps if "#SkyyExSkills " in mk] and not [mk for _p, mk in apps if "#SkyyExTab0 " in mk],
                "EXPLORE %s: no '< Skills' button, no old tab row" % name)
        if t == 0:
            K.check("#SkyyExCard7" in " ".join(mk for _p, mk in apps) and "Width: 380" in " ".join(kids(apps, "SkyyExRow0")),
                    "OVERVIEW: the 8 cards, 380 px wide on 1552")
        if t == 1:
            K.check(any("#SkyyExZoneL " in mk for _p, mk in apps) and any("#SkyyExZoneR " in mk for _p, mk in apps), "ZONES: the two region wells")
    # ---------------------------------------------------------------- CHECKLIST
    pg = open_tab(3)
    c, e, apps, sets = built(pg, "CHECKLIST (own island)")
    names = [sets.get("#SkyyExIs%dNm.Text" % i) for i in range(3)]
    K.eq(names, ["Home Isle (you are here)", "Beta Isle", "Zeta Reach"], "CHECKLIST: the island list = this world first, then by name")
    K.check("#4274a5" in [mk for _p, mk in apps if mk.startswith("Group #SkyyExIs0 ")][0]
            and "#4274a5" not in [mk for _p, mk in apps if mk.startswith("Group #SkyyExIs1 ")][0], "CHECKLIST: the shown island row selected (the blue bar)")
    K.check(all(any(("exwi%d" % i) in x for x in bound(e, "#SkyyExIs%dP" % i)) for i in range(3)), "CHECKLIST: every island row bound exwi<i>")
    K.check(any("TopScrolling" in mk for _p, mk in apps if mk.startswith("Group #SkyyExCkIsl ")) and any("TopScrolling" in mk for _p, mk in apps if mk.startswith("Group #SkyyExCkList ")),
            "CHECKLIST: the island list and the row list are scroll lists")
    K.eq([sets.get("#SkyyExCkT%d.Text" % i) for i in range(5)], ["Old Well", "??? Secret spot", "Sky Pillar", "Ring the old bell", "Open 3 loot chests"],
         "CHECKLIST Home Isle: the spots on the checklist (the secret one hidden), then the entries (Off List not on it)")
    K.eq([sets.get("#SkyyExCkS%d.Text" % i) for i in range(5)], ["Done", "-", "-", "-", "-"], "CHECKLIST: Old Well done (the player found it)")
    K.check(sets.get("#SkyyExCkV0.Text") == "+100 XP" and sets.get("#SkyyExCkV4.Text") == "0/3", "CHECKLIST: the XP / count badges")
    K.check(str(sets.get("#SkyyExCkHead.Text", "")).startswith("Home Isle (you are here) - 1 of 5 done - 20%") and "secrets 0 of 1" in str(sets.get("#SkyyExCkHead.Text")),
            "CHECKLIST: the head line (%s)" % sets.get("#SkyyExCkHead.Text"))
    k5 = SUI.grow_pick(5, 543, rows_hs, gap=3)
    K.eq(hgt(apps, "SkyyExCkRow0"), rows_hs[k5], "CHECKLIST GROW: 5 rows at %d px (= grow_pick)" % rows_hs[k5])
    cur, _t = click(pg, "exwi1")
    c, e, apps, sets = built(pg, "CHECKLIST (Beta Isle)")
    K.check(E.same(cur, pg) and str(sets.get("#SkyyExCkHead.Text", "")).startswith("Beta Isle - 0 of 1 done") and sets.get("#SkyyExCkT0.Text") == "Find the lighthouse",
            "CHECKLIST: exwi1 shows Beta Isle (%s)" % sets.get("#SkyyExCkHead.Text"))
    K.eq(hgt(apps, "SkyyExCkRow0"), rows_hs[2], "CHECKLIST GROW: 1 row at the biggest tier %d px" % rows_hs[2])
    K.check("#4274a5" in [mk for _p, mk in apps if mk.startswith("Group #SkyyExIs1 ")][0], "CHECKLIST: Beta Isle's row is the selected one now")
    cur, _t = click(pg, "exwi2")
    c, e, apps, sets = built(pg, "CHECKLIST (Zeta Reach, 230 entries)")
    nrow = len([1 for _p, mk in apps if mk.startswith("Group #SkyyExCkRow")])
    K.check(nrow == 200 and sets.get("#SkyyExCkMore.Text") == "... and 30 more checklist entries" and hgt(apps, "SkyyExCkRow0") == 44,
            "CHECKLIST: 230 entries = 200 rows of 44 px + '... and 30 more' (%d rows, %s)" % (nrow, sets.get("#SkyyExCkMore.Text")))
    for a in ("exwp", "exwn", "excp", "excn"):
        cur, _t = click(pg, a)
        K.check(str(pg.ckWorld) == str(WF("zetareach")), "CHECKLIST: the old pager click %s changes nothing" % a)
    cur, _t = click(pg, "extab0")
    K.check(int(pg.tab) == 0, "CLICK: the sub row's OVERVIEW (extab0) switches the tab")
    # ---------------------------------------------------------------- TITLES (equip)
    pg = open_tab(2)
    c, e, apps, sets = built(pg, "TITLES")
    TK = [int(x) for x in J("ExpDefs").T_KIND]
    ic = TK.index(2)
    il = TK.index(5) if 5 in TK else None
    K.check(bound(e, "#SkyyExUse%d" % ic) and bound(e, "#SkyyExNone"), "TITLES: an earned title has Use, No title is bound")
    cur, _t = click(pg, "exuse%d" % ic)
    K.check(str(pg.msg).startswith("Your title is now ") and int(J("ExpTitles").selected(d, 0)) == ic, "TITLES: Use equips it (%s)" % pg.msg)
    c, e, apps, sets = built(pg, "TITLES (equipped)")
    K.eq(sets.get("#SkyyExTS%d.Text" % ic), "In use", "TITLES: the equipped row says In use")
    if il is not None:
        cur, _t = click(pg, "exuse%d" % il)
        K.check("locked" in str(pg.msg) and int(J("ExpTitles").selected(d, 0)) == ic, "TITLES: a locked title is refused (%s)" % pg.msg)
    cur, _t = click(pg, "exnone")
    K.check(str(pg.msg) == "Title removed" and int(J("ExpTitles").selected(d, 0)) < 0, "TITLES: No title removes it (%s)" % pg.msg)
    K.check(PKG + "ExplorePage.<init>" in g.get("TitleCmd.execute", set()) and PKG + "ExplorePage.<init>" in g.get("ExploreCmd.execute", set()),
            "TITLES: /title and /explore open the Explore page (bytecode; /title = tab 2 as 0.2.12)")
    # ---------------------------------------------------------------- the kit clicks
    pg = open_tab(0)
    E.CM.lines.clear()
    cur, txt = click(pg, "hub:h:home")
    K.check("skymenu" in [str(x) for x in E.CM.lines], "CLICK row 1 Home runs /skymenu (%s)" % list(E.CM.lines))
    pg = open_tab(0)
    cur, txt = click(pg, "hub:explore")
    K.check(E.same(cur, pg), "CLICK row 2's own Explore tab keeps the page (answered)")
    cur, txt = click(pg, "hub:h:world")
    K.check(E.same(cur, pg), "CLICK row 1's own World keeps the page (answered)")
    cur, txt = click(pg, "hub:nosuchtab")
    K.check(E.same(cur, pg) and str(pg.msg) == FAIL_TEXT, "CLICK a missing tab says so on the result line (%s)" % pg.msg)
    cur, txt = click(pg, "hub:close")
    K.check(cur is None, "CLICK the X closes the page")
    pg = open_tab(0)
    cur, txt = click(pg, "exskills")
    K.check(cur is not None, "CLICK the old exskills click still works (no SkyySkills: the page says so)")
    # ---------------------------------------------------------------- REVEAL
    cards = RvF.sampleCards()
    Rv = J("LgRv")
    rv = RV(P.pr, Str("Loot Bag (III)"), Str("Lv 23 - 3 finds"), Rv.parse(cards), None)
    P.pm.openCustomPage(P.ref, P.st, rv)
    E.pump(P)
    c, e, apps, sets = built(rv, "REVEAL (Loot Bag, closed cards)", prefix="SkyyRvF", subs=0)
    K.eq(sets.get("#SkyyRvFTitle.Text"), "Loot Bag (III)", "REVEAL: the title = the bag")
    want = SUI.hub_big_tabs_preview("SkyyRvF", "world", world_tabs, "explore")
    got = [(p, mk) for p, mk in apps if p == "SkyyRvFBigTabs" or (p or "").startswith("SkyyRvFBigT")]
    K.check(got == list(want), "REVEAL: row 2 = the World tabs, Explore selected (hub_big_tabs_preview byte for byte)")
    ft = [mk for mk in kids(apps, "SkyyRvFFoot") if mk.startswith("TextButton")]
    K.check(ft == [SUI.foot_button("SkyyRvAll", "Open all", w=SUI.BTN_MIN_W), SUI.foot_button("SkyyRvNext", "Open next", w=SUI.BTN_MIN_W, kind="primary")],
            "REVEAL: the footer Open all + Open next (Primary, right-most)")
    K.check(any("rvall" in x for x in bound(e, "#SkyyRvAll")) and any("rvnext" in x for x in bound(e, "#SkyyRvNext")), "REVEAL: Open all / Open next bound")
    K.check(not [mk for _p, mk in apps if "#SkyyRvClose " in mk or "#SkyyRvBack " in mk], "REVEAL: no Close / Back button")
    K.eq(len([1 for _p, mk in apps if mk.startswith("Group #SkyyRvC") and "Width: 300" in mk]), 3, "REVEAL: 3 cards, 300 px wide on 1552")
    cur, _t = click(rv, "rvnext")
    K.check(E.same(cur, rv) and int(rv.shown) == 1, "REVEAL: Open next flips one")
    cur, _t = click(rv, "rvall")
    c, e, apps, sets = built(rv, "REVEAL (all open)", prefix="SkyyRvF", subs=0)
    K.check(int(rv.shown) == 3 and not [mk for mk in kids(apps, "SkyyRvFFoot") if mk.startswith("TextButton")] and str(sets.get("#SkyyRvMsg.Text", "")).startswith("Best find"),
            "REVEAL: Open all flips the rest, the buttons go, the result line names the best find")
    cur, _t = click(rv, "hub:explore")
    K.check(cur is not None and str(cur.getClass().getName()) == PKG + "ExplorePage" and int(cur.tab) == 0,
            "REVEAL: row 2's Explore (the page's own tab) opens the Explore page")
    rv = RV(P.pr, Str("Loot Bag (I)"), Str("Lv 5"), Rv.parse(cards), None)
    P.pm.openCustomPage(P.ref, P.st, rv)
    E.pump(P)
    cur, _t = click(rv, "hub:close")
    K.check(cur is None, "REVEAL: the X closes")
    fk = HT.Fakes(E, "smithing")
    E.bridge.put("hub:tab:smithing:identify", JArray(JObject)([Str("SkyyGear"), Str("Identify"), JClass("java.lang.Integer")(60), Str("identify"), None, None]))
    rv = RV(P.pr, Str("Identified"), Str("Lv 43"), Rv.parse(cards), Str("identify"))
    P.pm.openCustomPage(P.ref, P.st, rv)
    E.pump(P)
    c, e, apps, sets = built(rv, "REVEAL (identify)", hub="smithing", prefix="SkyyRvF", subs=0)
    K.eq([str(x) for x in RV.hubOf("identify")], ["smithing", "identify"], "REVEAL: hubOf('identify') = Crafting > Identify")
    K.eq([str(x) for x in RV.hubOf(None)], ["world", "explore"], "REVEAL: hubOf(none) = World > Explore")
    K.eq([str(x) for x in RV.hubOf("tree exploration")], ["character", "trees"], "REVEAL: hubOf('tree exploration') = Character > Trees")
    idt = [p for p, mk in apps if (p or "").startswith("SkyyRvFBigT") and 'Text: "Identify"' in mk]
    K.check(len(idt) == 1 and any("hub:identify" in x for x in bound(e, "#" + idt[0])), "REVEAL identify: row 2 = the Crafting tabs with Identify (bound hub:identify)")
    K.eq(sets.get("#SkyyRvFTitle.Text"), "Identified", "REVEAL identify: the title")
    E.CM.lines.clear()
    cur, _t = click(rv, "hub:identify")
    K.check("identify" in [str(x) for x in E.CM.lines], "REVEAL identify: its own tab runs /identify (the old Back) (%s)" % list(E.CM.lines))
    fk.remove()
    # ---------------------------------------------------------------- CALLS
    for m in ("ExplorePage.build", "LgReveal.build"):
        K.check(PKG + "HubBar.page17" in g.get(m, set()) and PKG + "HubBar.build" not in g.get(m, set()), "CALLS: %s -> HubBar.page17, no kit 1.5 HubBar.build" % m)
    K.check(PKG + "HubBar.subTab" in g.get("ExplorePage.build", set()), "CALLS: ExplorePage.build -> HubBar.subTab")
    K.check(PKG + "HubBar.growSize" in g.get("ExplorePage.checklistTab", set()), "CALLS: ExplorePage.checklistTab -> HubBar.growSize")
    for m in ("ExplorePage.hubClick", "LgReveal.hubClick"):
        K.check(PKG + "HubBar.route" in g.get(m, set()) and PKG + "HubBar.handle" not in g.get(m, set()), "CALLS: %s -> HubBar.route (no handle)" % m)
    K.check(PKG + "LgReveal.hubClick" in g.get("LgReveal.handleDataEvent", set()), "CALLS: LgReveal.handleDataEvent asks hubClick first")
    J("HubBar").removeAll()
    K.save()


class _ChildX(T12._Child28):
    """the 0.2.8 X phase on the 0.2.13 jar: its three reveal-page LOOK checks expected Close / < Back buttons - 0.2.13 has neither (rule 8:
    the X closes, row 2's own tab runs the back command); they are re-asked against the 0.2.13 page (the PAGES phase checks it fully)"""
    LOOK = ("X page build: 4 face-down cards", "X page build (all open)", "X page (bridge call)")

    def check(self, cond, what):
        if not cond and what.startswith(self.LOOK):
            what += " (0.2.13: no Close / < Back on the page - replaced by PAGES REVEAL)"
            cond = True
        return T12._Child28.check(self, cond, what)


def run_exec(out, jar, scratch, home):
    _ChildX.JAR = T12._Child28.JAR = jar
    T28.HK = types.SimpleNamespace(**dict(vars(HK), Child=_ChildX))
    T28.run_exec(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyExploration", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("pages", run_pages), ("names", T12.run_names), ("cap", T12.run_cap), ("exec", run_exec), ("live", T28.run_live)],
           script=__file__, live=(LIVE, "Skyy_SkyyExploration"))
