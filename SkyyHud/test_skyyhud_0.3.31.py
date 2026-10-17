"""Harness for SkyyHud 0.3.31 (MENU PATTERN sweep S4, M7 Hud half: Settings > HUD = the widget list on the kit 1.7 hub_page, a widget's
settings = the same page + the ONE sub-tab row, no back buttons, the Quest row's tutorial toggle; tools/hud_0_3_31_patch.py) = the 0.3.26
harness (tools/hub_tab_harness.py phases) with the kit 1.5 page check replaced by the KIT 1.7 one, compare 0.3.30 -> 0.3.31, plus:
  PAGE17  EVERY view BUILT through the REAL builders and checked (check_page, kit paths, the root 1600 x 980, SUI.assert_menu_page on the
          REAL commands: rows 1 + 2, no sub row on the list / ONE on a widget's settings, no kit 1.5 bar, no back / < Menu text, no pager;
          every b.set / binding names an element): the list (with and without SkyyQuests), Coordinates / Skills / Combat / Minimap settings
  LIST    one row per Widgets.edIds() widget: the name, ON / OFF (the active one Tertiary_Active), Settings; the rows' grow tier
          (HubBar.growSize = SUI.grow_pick: 17 rows = 56 px); the footer = the hint + Open HUD editor (Primary) bound hudedit
  TOGGLE  OFF / ON on the list = WLayout.en saved (the layout file) and the page rebuilt (still the list); Settings opens that widget's
          settings view
  QUEST   SkyyQuests loaded (quest:fn:hud): the Quest row has the tutorial button - settings:fn:get FALSE = "shown", click -> /quests hide
          as the player + the page shows hidden; settings:fn:get TRUE = "hidden", click -> /quests show; no SkyyMenu = shown;
          no SkyyQuests = no button (and a stray tut:hide runs nothing)
  SUB     a widget's settings: [All widgets] bound wlist, [<widget>] selected and unbound; wlist / row 2's HUD tab / an old back payload
          -> the list; hudedit -> the editor; the old settings clicks still save (Background, Size); no #SkyySetBack / #SkyyMmSBack /
          #SkyyMmSBar any more
  EDITOR  the editor's Widgets / Settings button opens the list (HudHubPage)
Build first:
python tools/hud_0_3_31_patch.py && python SkyyHud/build_skyyhud_0.3.31.py

    python SkyyHud/test_skyyhud_0.3.31.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Not testable without the game (UNVERIFIED): the client drawing the 1600 x 980 page, the sub row, the sky footer, the Tertiary toggle look.
Exit code 1 on any failure.
"""
import os, sys, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import hub_tab_harness as H
import skyyui as SUI

VERSION = "0.3.31"
PKG = "com.skyy.hud."
PFX = "SkyyHudHF"
PL = {}


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
    from jpype import JClass
    os.makedirs(os.path.join(home, "layouts"), exist_ok=True)
    J("LayoutStore").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyHud")
    J("LayoutStore").DIR = E.Paths.get(os.path.join(home, "layouts"))
    J("HudCfg").LOG = J("LayoutStore").LOG
    J("HudCfg").FILE = E.Paths.get(os.path.join(home, "config.properties"))
    pl = E.U.allocateInstance(J("SkyyHudPlugin").class_)
    H.jf(J("SkyyHudPlugin").class_, "huds").set(pl, JClass("java.util.concurrent.ConcurrentHashMap")())
    PL["pl"] = pl
    PL["home"] = home


def register(J):
    return J("HudHubOpen").register(PL["pl"])


def build(P, page):
    from jpype import JClass
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    page.build(P.ref, b, ev, P.st)
    return H.cmds_of(b), H.events_of(ev)


def page_check17(K, E, S, P, page, hb, what, subs=None):
    """the KIT 1.7 page check (replaces hub_tab_harness.page_check, which checks the kit 1.5 bar); returns (apps, sets, evs)"""
    cmds, evs = build(P, page)
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cmds if t is not None and ty and "Append" in ty])
    sets = [(s, d) for ty, s, t, d in cmds if ty == "Set"]
    K.check(len(apps) > 5 and len(apps) + len(sets) == len(cmds), "%s: %d appends + %d sets" % (what, len(apps), len(sets)))
    try:
        SUI.check_page(apps, "Skyy")
        K.check(True, "%s: check_page (markup rules, parents, no duplicate id)" % what)
    except Exception as e:
        K.check(False, "%s: check_page: %s" % (what, e))
    try:
        els = SUI.check_sky_paths(apps, tab_icons=True)
        allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
        K.check(not [p for p in allp if p.startswith('"../')] and {"Header", "HeaderOrnament", SUI.HUB_FRAME["settings"], "Close"} <= set(els),
                "%s: the Sky Window paths, none leaves Common/UI/Custom (%d paths)" % (what, len(allp)))
    except Exception as e:
        K.check(False, "%s: sky paths: %s" % (what, e))
    roots = [mk for p, mk in apps if p is None]
    K.check(len(roots) == 1 and roots[0].startswith("Group #%s { Anchor: (Width: 1600, Height: 980); }" % PFX), "%s: ONE root #%s, 1600 x 980" % (what, PFX))
    if subs is None:
        subs = 0 if str(page.getClass().getSimpleName()) == "HudHubPage" else 1
    try:
        info = SUI.assert_menu_page(apps, hub="settings", what=what, sets=[(s, unq(d)) for s, d in sets], pager_ok=False)
        K.check(info["rows"] == 2 and info["subs"] == subs, "%s: assert_menu_page (1600 x 980, rows 1 + 2, %d sub row, no back / < Menu, no pager)" % (what, subs))
    except Exception as ex:
        K.check(False, "%s: assert_menu_page: %s" % (what, ex))
    texts = [m.group(1) for _p, mk in apps for v in SUI._variants(mk) for m in re.finditer(r'Text: "((?:[^"\\]|\\.)*)"', SUI.render(v))]
    K.check(not [mk for p, mk in apps if "HubMenu" in mk or "HubTabs" in mk] and not [t for t in texts + [unq(d) for _s, d in sets] if re.search(r"\bBack\b", t) or "< Menu" in t],
            "%s: no kit 1.5 bar, no Back / < Menu text anywhere" % what)
    gone = [i for i in ("SkyyWidgets", "SkyyWBack", "SkyySetBack", "SkyyMmSBack", "SkyyDsSBack", "SkyyMmSBar", "SkyyDsSBar", "SkyyHudHWid", "SkyyHudHActs")
            if [mk for p, mk in apps if ("#%s " % i) in mk]]
    K.check(not gone, "%s: no old launcher / widgets page / back button / own title bar (%s)" % (what, gone))
    K.check(any("hub:close" in t for s, t in evs if s == "#%sHubClose" % PFX), "%s: the X = hub:close" % what)
    vis = [str(r[0]) for r in hb.tabs("settings", P.pr.getUuid())]
    tabs = [mk for p, mk in apps if p == PFX + "BigTabs" and mk.startswith("Button")]
    K.eq(len(tabs), len(vis), "%s: row 2 = one tab per visible Settings tab %s" % (what, vis))
    for k, t in enumerate(vis):
        K.check(any(("hub:" + t) in tx for s, tx in evs if s == "#%sBigT%d" % (PFX, k)), "%s: row 2 tab %d bound to hub:%s" % (what, k, t))
    ids = set()
    for _p, mk in apps:
        ids |= set(x.group(2) for x in H.DECL_RE.finditer(SUI.render(mk)))
    bs = [s for s, _t in evs]
    bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s in bs if s.lstrip("#") not in ids]
    K.check(not bad, "%s: every b.set and binding names an element that exists (%d sets, %d bindings): %s" % (what, len(sets), len(bs), bad[:4]))
    return apps, dict((s, unq(d)) for s, d in sets), evs


def _pc(K, E, S, P, page, hb, what):
    page_check17(K, E, S, P, page, hb, what)


H.page_check = _pc      # run_hub calls H.page_check: the kit 1.7 check from now on


def chk_editor(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "EditorPage", "CLICK: Open HUD editor opens the full-screen editor (%s)"
            % (None if after is None else after.getClass().getSimpleName()))


def after_open(K, E, J, P, pg):
    from jpype import JClass
    # the HUD of the harness player counts as attached: Open HUD editor goes straight to the editor
    PL["pl"].huds.put(P.pr.getUuid(), JClass("java.lang.Object")())


def extra_hub(K, W, J):
    import jpype
    from jpype import JClass, JImplements, JOverride
    E, P = W.E, W.P
    u = P.pr.getUuid()
    HB = J("HubBar")
    TRUE, FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE
    pl = PL["pl"]
    J("HudHubOpen").unregister()
    K.check(J("HudHubOpen").PLUGIN is None and J("HudHubOpen")().apply(u) == FALSE, "REG: unregister clears PLUGIN; the open Function then answers FALSE (the bar runs /skyyhud)")
    J("HudHubOpen").register(pl)
    pl.huds.remove(u)        # no HUD attached: rebuildFor(u) finds none (the stand-in has no client HUD)

    def openp(page):
        P.pm.openCustomPage(P.ref, P.st, page)
        E.pump(P)
        return P.pm.getCustomPage()

    def click(a):
        P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, '{"a":"%s"}' % a))
        E.pump(P)
        return P.pm.getCustomPage()

    name = lambda pg: None if pg is None else str(pg.getClass().getSimpleName())
    ids = [str(x) for x in J("Widgets").edIds()]
    # ---------------------------------------------------------------- LIST
    pg = openp(J("HudHubPage")(P.pr, pl))
    apps, sets, evs = page_check17(K, E, None, P, pg, HB, "LIST (no SkyyQuests)", subs=0)
    rows = [mk for p, mk in apps if p == "SkyyHudWList"]
    K.eq(len(rows), len(ids), "LIST: one row per widget (%d: %s)" % (len(ids), ",".join(ids)))
    K.check(all(("Height: %d," % SUI.ROW_H_READABLE) in r for r in rows), "LIST: %d rows = the normal 56 px tier (HubBar.growSize)" % len(rows))
    lay = J("LayoutStore").get(u)
    for k, i in enumerate(ids):
        en = bool(lay.get(i).en)
        K.eq(sets.get("#SkyyHudWName%d.Text" % k), str(J("Widgets").label(i)), "LIST: row %d names %s" % (k, i))
        onmk = [mk for p, mk in apps if p == "SkyyHudWR%d" % k and ("#SkyyHudWOn%d " % k) in mk]
        offmk = [mk for p, mk in apps if p == "SkyyHudWR%d" % k and ("#SkyyHudWOff%d " % k) in mk]
        K.check(len(onmk) == 1 and len(offmk) == 1 and (("Tertiary_Active" in onmk[0]) == en) and (("Tertiary_Active" in offmk[0]) == (not en)),
                "LIST: row %d %s ON / OFF shows %s" % (k, i, "ON" if en else "OFF"))
        for kind, a in (("On", "on:"), ("Off", "off:"), ("Cog", "cog:")):
            K.check(any(a + i in t for s, t in evs if s == "#SkyyHudW%s%d" % (kind, k)), "LIST: row %d %s bound %s%s" % (k, kind, a, i))
    K.check("#SkyyHudWTut " not in "".join(mk for p, mk in apps), "QUEST: no SkyyQuests = no tutorial button")
    K.check(sets.get("#SkyyHudHInfo.Text", "").startswith("Chat: /skyyhud") and any("hudedit" in t for s, t in evs if s == "#SkyyHudHEdit")
            and any("#SkyyHudHEdit " in mk and "Open HUD editor" in mk and "Primary" in mk for p, mk in apps if p == PFX + "Foot"),
            "LIST: the footer = the hint + Open HUD editor (Primary) bound hudedit")
    hs = [int(x) for x in J("HudHubPage").HS]
    K.eq(hs, SUI.grow_row_sizes(716 - 2 * SUI.WELL_LIST_PAD, SUI.ROW_H_READABLE, gap=SUI.ROW_GAP), "GROW: HudHubPage.HS = the kit's grow_row_sizes")
    K.check(all(int(HB.growSize(n, 708, J("HudHubPage").HS, 3)) == SUI.grow_pick(n, 708, hs, 3) for n in range(1, 30)), "GROW: HubBar.growSize = SUI.grow_pick for 1-29 rows")
    # ---------------------------------------------------------------- TOGGLE
    f = os.path.join(PL["home"], "layouts")
    k0 = ids.index("Coords")
    p2 = click("off:Coords")
    K.check(name(p2) == "HudHubPage" and not bool(J("LayoutStore").get(u).get("Coords").en), "TOGGLE: OFF on Coordinates = WLayout.en false, still the list")
    a2, s2, e2 = page_check17(K, E, None, P, p2, HB, "LIST after OFF", subs=0)
    K.check(any("Tertiary_Active" in mk for p, mk in a2 if p == "SkyyHudWR%d" % k0 and "#SkyyHudWOff%d " % k0 in mk), "TOGGLE: the rebuilt row shows OFF")
    lf = os.path.join(f, str(u) + ".properties")
    line = lambda: ([l for l in open(lf, encoding="latin-1").read().splitlines() if l.startswith("Coords=")] or [""])[0] if os.path.isfile(lf) else ""
    off_line = line()
    K.check(off_line != "", "TOGGLE: the layout file is written (%s)" % off_line)
    p3 = click("on:Coords")
    K.check(name(p3) == "HudHubPage" and bool(J("LayoutStore").get(u).get("Coords").en), "TOGGLE: ON on Coordinates = WLayout.en true again")
    K.check(line() != "" and line() != off_line, "TOGGLE: the saved Coords line changed back (%s -> %s)" % (off_line, line()))
    # ---------------------------------------------------------------- QUEST
    @JImplements("java.util.function.Function")
    class Fn:
        def __init__(self, ans):
            self.ans, self.calls = ans, []

        @JOverride
        def apply(self, o):
            try:
                self.calls.append([str(x) for x in o])
            except Exception:
                self.calls.append(str(o))
            return self.ans
    qfn = Fn(None)
    E.br.put("quest:fn:hud", qfn)
    sfn = Fn(FALSE)
    E.br.put("settings:fn:get", sfn)
    kq = ids.index("Quest")
    pg = openp(J("HudHubPage")(P.pr, pl))
    a4, s4, e4 = page_check17(K, E, None, P, pg, HB, "LIST (SkyyQuests, tutorial shown)", subs=0)
    tut = [mk for p, mk in a4 if p == "SkyyHudWR%d" % kq and "#SkyyHudWTut " in mk]
    K.check(len(tut) == 1 and s4.get("#SkyyHudWTut.Text") == "Tutorial tasks: shown" and any("tut:hide" in t for s, t in e4 if s == "#SkyyHudWTut"),
            "QUEST: the Quest row's button says 'Tutorial tasks: shown', bound tut:hide (%s)" % s4.get("#SkyyHudWTut.Text"))
    K.check(sfn.calls and sfn.calls[-1] == [str(u), "tutorial.hide"], "QUEST: the state is read with settings:fn:get [UUID, tutorial.hide] (%s)" % sfn.calls[-1:])
    K.check(sum(1 for p, mk in a4 if "#SkyyHudWTut " in mk) == 1, "QUEST: only the Quest row has it")
    E.CM.lines.clear()
    p5 = click("tut:hide")
    K.check([str(x) for x in E.CM.lines] == ["quests hide"], "QUEST: click when shown runs /quests hide as the player (%s)" % list(E.CM.lines))
    a5, s5, e5 = page_check17(K, E, None, P, p5, HB, "LIST (tutorial just hidden)", subs=0)
    K.check(name(p5) == "HudHubPage" and s5.get("#SkyyHudWTut.Text") == "Tutorial tasks: hidden" and "hidden" in s5.get("#SkyyHudHInfo.Text", ""),
            "QUEST: the page is rebuilt showing hidden (the clicked state) + the status line (%s / %s)" % (s5.get("#SkyyHudWTut.Text"), s5.get("#SkyyHudHInfo.Text")))
    sfn.ans = TRUE
    pg = openp(J("HudHubPage")(P.pr, pl))
    a6, s6, e6 = page_check17(K, E, None, P, pg, HB, "LIST (SkyyQuests, tutorial hidden)", subs=0)
    K.check(s6.get("#SkyyHudWTut.Text") == "Tutorial tasks: hidden" and any("tut:show" in t for s, t in e6 if s == "#SkyyHudWTut"),
            "QUEST: settings:fn:get TRUE = 'Tutorial tasks: hidden', bound tut:show")
    E.CM.lines.clear()
    click("tut:show")
    K.check([str(x) for x in E.CM.lines] == ["quests show"], "QUEST: click when hidden runs /quests show as the player (%s)" % list(E.CM.lines))
    E.br.remove("settings:fn:get")
    pg = openp(J("HudHubPage")(P.pr, pl))
    _a, s7, _e = page_check17(K, E, None, P, pg, HB, "LIST (SkyyQuests, no SkyyMenu)", subs=0)
    K.eq(s7.get("#SkyyHudWTut.Text"), "Tutorial tasks: shown", "QUEST: no SkyyMenu (no settings:fn:get) = shown")
    E.br.remove("quest:fn:hud")
    E.CM.lines.clear()
    click("tut:hide")
    K.check(list(E.CM.lines) == [], "QUEST: without SkyyQuests a stray tut:hide runs nothing")
    # ---------------------------------------------------------------- SUB (a widget's settings)
    pg = openp(J("HudHubPage")(P.pr, pl))
    ps = click("cog:Coords")
    K.check(name(ps) == "SettingsPage" and str(ps.wid) == "Coords", "TOGGLE: Settings on Coordinates opens its settings view (%s)" % name(ps))
    for w in ("Coords", "Skills", "Combat", "Minimap", "Party"):
        pw = openp(J("SettingsPage")(P.pr, pl, w))
        aw, sw, ew = page_check17(K, E, None, P, pw, HB, "SUB %s settings" % w, subs=1)
        subs_ = [mk for p, mk in aw if p == PFX + "Sub" and mk.startswith("TextButton")]
        K.check(len(subs_) == 2 and '"All widgets"' in subs_[0] and ('"%s"' % J("Widgets").label(w)) in subs_[1]
                and subs_[0] == SUI.sub_tab_markup(PFX, 0, "All widgets", False, SUI.SUB_TAB_W) and subs_[1] == SUI.sub_tab_markup(PFX, 1, str(J("Widgets").label(w)), True, 320),
                "SUB %s: the sub row [All widgets | %s] = the kit's sub_tab_markup, the widget's selected" % (w, J("Widgets").label(w)))
        K.check(any("wlist" in t for s, t in ew if s == "#%sSub0" % PFX) and not [s for s, t in ew if s == "#%sSub1" % PFX],
                "SUB %s: All widgets bound wlist, the selected tab unbound" % w)
        root = "SkyyMmS" if w == "Minimap" else "SkyySet"
        K.check([p for p, mk in aw if mk.startswith("Group #%s " % root)] == ["SkyySetL"] and any(mk.startswith("Group #SkyySetL ") and "TopScrolling" in mk for p, mk in aw if p == "SkyyHudSC"),
                "SUB %s: the rows (#%s) sit in the scroll list #SkyySetL inside the content" % (w, root))
        K.check(any("hudedit" in t for s, t in ew if s == "#SkyyHudHEdit"), "SUB %s: the footer's Open HUD editor bound hudedit" % w)
    pw = openp(J("SettingsPage")(P.pr, pl, "Coords"))
    bg0 = bool(J("LayoutStore").get(u).get("Coords").bg)
    p8 = click("bgoff" if bg0 else "bgon")
    K.check(name(p8) == "SettingsPage" and bool(J("LayoutStore").get(u).get("Coords").bg) == (not bg0), "SUB: the old Background click still saves (%s -> %s)" % (bg0, not bg0))
    p9 = click("sz:150")
    K.check(int(J("LayoutStore").get(u).get("Coords").scale) == 150, "SUB: the old Size click still saves (150 %%)")
    click("sz:100")
    click("bgon" if bg0 else "bgoff")
    K.eq(name(click("wlist")), "HudHubPage", "SUB: All widgets -> the list")
    openp(J("SettingsPage")(P.pr, pl, "Coords"))
    K.eq(name(click("hub:hud")), "HudHubPage", "SUB: row 2's HUD tab on a settings view -> the list")
    openp(J("SettingsPage")(P.pr, pl, "Coords"))
    K.eq(name(click("hub:h:settings")), "HudHubPage", "SUB: row 1's Settings on a settings view -> the list")
    openp(J("SettingsPage")(P.pr, pl, "Coords"))
    K.eq(name(click("back")), "HudHubPage", "SUB: an old back payload -> the list")
    openp(J("SettingsPage")(P.pr, pl, "Minimap"))
    K.eq(name(click("mm:back")), "HudHubPage", "SUB: an old Minimap back payload -> the list")
    openp(J("SettingsPage")(P.pr, pl, "Coords"))
    K.check(click("hub:close") is None, "SUB: the X closes a settings view")
    pl.huds.put(u, JClass("java.lang.Object")())
    openp(J("SettingsPage")(P.pr, pl, "Coords"))
    K.eq(name(click("hudedit")), "EditorPage", "SUB: Open HUD editor on a settings view -> the editor")
    # ---------------------------------------------------------------- EDITOR
    pe = openp(J("EditorPage")(P.pr, pl))
    pl.huds.remove(u)
    P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, '{"a":"widgets"}'))
    E.pump(P)
    K.eq(name(P.pm.getCustomPage()), "HudHubPage", "EDITOR: the editor's Widgets / Settings button opens the list")
    pl.huds.put(u, JClass("java.lang.Object")())


EXPECT_HUBBAR = ["+<clinit>", "+f ROW_IDS", "+f ROW_TITLES"] + ["+m " + m for m in (     # the kit 1.7 members (row / sub / big / page)
    "bigLab", "bigRow", "bigRowFill", "bigTabLab", "bigTabsFill", "build2", "buildRow", "def4", "defOf", "defTab", "goHub", "growSize",
    "hasArt", "hostOf", "hostShown", "hostTab", "hubs", "iconOf", "okIcon", "okItem", "openSub", "page17", "pickTab", "putIcon", "putSub",
    "route", "rowLab", "rowStyle", "rowWidth", "selOf", "subIcon", "subTab", "subTabs", "tabBStyle", "tabLab", "titleOf")]

S = H.Spec(name="SkyyHud", version=VERSION, pkg=PKG, hub="settings", tab="hud", mod="SkyyHud", open_cls="HudHubOpen", vis_cls=None,
           page_cls="HudHubPage", prefix=PFX, idp="Skyy", plugin_cls="SkyyHudPlugin", register_call="HudHubOpen.register",
           drop_call="HudHubOpen.unregister", register=register, prep=prep, after_open=after_open,
           clicks=[('{"a":"hudedit"}', chk_editor)], extra_hub=extra_hub,
           jar=os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION))), old_jar=os.path.join(HERE, "SkyyHud-0.3.30.jar"),
           scratch=os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menuS4", "hud", "harness"))), script=__file__,
           added=[], removed=["WidgetsPage"],
           expect={"HudHubPage": ["+<clinit>", "+f HS", "+f info", "+f tutWant", "~c ", "~m build", "~m handleDataEvent", "+m tutHidden"],
                   "SettingsPage": ["~m build", "~m handleDataEvent", "+m hubAck", "+m openEditor", "+m openList"],
                   "EditorPage": ["~m handleDataEvent"],
                   "MmUi": ["~m settings"], "DsUi": ["~m settings"],
                   "HubBar": EXPECT_HUBBAR,
                   "SkyyHudPlugin": ["~m setup"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"]})
H.KIT_FILES = []   # 0.3.30 -> 0.3.31: the 59 kit files are already in 0.3.30 (byte-equal), so only manifest.json changes

if __name__ == "__main__":
    H.run(S)
