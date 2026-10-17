"""Derive SkyyMenu/build_skyymenu_0.3.35.py from the LIVE SkyyMenu 0.3.34 (python tools/menu_0_3_35_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_34_patch.py -> 0.3.34 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.35. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.34 (nothing else changed). The harness SkyyMenu/test_skyymenu_0.3.35.py is its own file.

0.3.35 (2026-10-16) = round K of the MENU PATTERN sweep (research/Menu-Pattern.md section 4; kit tools/skyyui.py 1.7 hub_page). Skyy
(docs/answered/ui.md 2026-10-16): "lets try to reduce and compress the menus together to reduce clutter. then make sure its consistent across
the board, then follow the pattern when making new or adding to existing menus." + "keep this top bar at this size consistent at the top
across every menu." + "I never want to have to use a back button. The menus at the top should always be there for easy navigation." +
popups: every hub page Home size 1600 x 980; row 2 big like Teleport; Your Stats = one scroll list; Settings drops Edit Shortcuts.
  1. EVERY MENU PAGE ON THE KIT 1.7 SHELL (SUI.hub_page, 1600 x 980): Home (926 -> 980 high, the grid's centre slot keeps its screen spot),
     Teleport (1300 x 962 -> 1600 x 980), Players / a player / Mods, Settings, Server Setup, Your Stats. Row 1 + row 2 come from the kit's
     HubBar.page17 (= Home's / Teleport's own rows byte for byte, tools/test_skyyui_hubs.py); the hub tab art is published as hub:art so
     every mod's row 2 can draw it.
  2. NO BACK BUTTONS: the Players / Mods grid loses its Go Back / Close / page tiles and its old footer back button (row 2's Players tab
     leads back from a player's page); Your Stats and Settings lose their old menu button (row 1 Home); Server Setup's view buttons back
     (All mods / the mod) become the ONE sub-tab row (a breadcrumb of sub-tabs) with the view's title beside them.
  3. YOUR STATS = ONE scroll list with section heads (Main, Combat, Gathering) - the inner tabs and the Skills / Profile tabs (duplicates)
     go; the sub-tab row YOUR STATS | SKILLS stays (the one allowed sub row).
  4. SETTINGS: the categories are the ONE sub-tab row (kit small buttons), every row of a category in ONE scroll list (no pages; a short
     list gets bigger rows - Skyy rule 7, HubBar.growSize), the footer = the hint / status line, Reset all, Close.
  5. SETTINGS DROPS EDIT SHORTCUTS (popup 5): the settings:layout tab is no longer put (kit HUB_RETIRED); a saved Edit shortcuts shortcut
     on Home still opens the editor.
  The HUD tab (widget list + Open HUD editor) is SkyyHud's page - sweep group S4. No saved data, no command, no setting.
  ROLLBACK to 0.3.34: safe (the old pages come back; hub:art is ignored by 0.3.34).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import skyyui as SUI

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.34.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.35.py"))
assert P.has('VERSION = "0.3.34"\n') and P.has("REDIR_FROM") and not P.has("SUI.hub_page("), "not the generated SkyyMenu 0.3.34 script"
CMD0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
assert SUI.KIT_PAGE_VERSION == "1.7" and SUI.KIT_HUB_VERSION == "1.6", "kit skyyui 1.7 (hub_page)"


def cut(start, end):
    """the exact text of P.s from start up to and including end (each unique)"""
    assert P.s.count(start) == 1, "start anchor count %d: %s" % (P.s.count(start), start[:120])
    i = P.s.index(start)
    j = P.s.index(end, i)
    assert P.s.count(end) >= 1
    return P.s[i:j + len(end)]


P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.35: MENU PATTERN round K (notes: tools/menu_0_3_35_patch.py; research/Menu-Pattern.md; kit skyyui 1.7 hub_page): every Menu page on the
       1600 x 980 kit shell (row 1 + row 2 from HubBar.page17), no back buttons, Your Stats one scroll list, Settings one scroll list per
       category (categories = the sub-tab row), Server Setup's view crumbs as the sub-tab row, Settings drops Edit shortcuts, hub:art.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.35.py.
''')
P.rep('VERSION = "0.3.34"\n', 'VERSION = "0.3.35"\n')
# old tile icon names (no button on any page)
P.rep('''("Back", "Go Back", "Weapon_Arrow_Iron"), ("Prev", "Previous Page", "Weapon_Arrow_Crude"),''',
      '''("Back", "Go Back", "Weapon_Arrow_Iron"), ("Prev", "Previous Page", "Weapon_Arrow_Crude"),   # menu-pattern-ok: old icon names''')

# ---- 5. Settings drops Edit shortcuts: Menu's own tabs without the retired settings:layout
P.rep('''HUB_OWN_VIS = ("mods", "setup")''', '''HUB_OWN = [_r for _r in HUB_OWN if (_r[0], _r[1]) not in SUI.HUB_RETIRED]   # 0.3.35: Settings drops Edit shortcuts (Skyy popup 5)
assert [(h, t) for h, t, _o, _l, _c in HUB_OWN] == [("character", "stats"), ("world", "teleport"), ("social", "players"), ("settings", "settings"),
                                                  ("settings", "mods"), ("settings", "setup")], "0.3.35: Menu puts 6 tabs (no Edit shortcuts)"
HUB_OWN_VIS = ("mods", "setup")''')

# ---- the classic grid footer buttons (old brown): the back button and the page buttons go (0.3.35 uses the kit footer below)
P.rep('''    "BTNBACK":  'TextButton #SkyyMBack { Anchor: (Width: 168, Height: 40); Text: "< Back"; ' + BS + " }",
    "BTNPREV":  'TextButton #SkyyMPrev { Anchor: (Width: 154, Height: 40); Text: "< Prev page"; ' + BS + " }",
    "BTNNEXT":  'TextButton #SkyyMNext { Anchor: (Width: 154, Height: 40); Text: "Next page >"; ' + BS + " }",
''', '''    # 0.3.35: the old classic footer's back / page buttons went (the kit 1.7 footer: UI35 below)
''')

# ================================================================ 4. THE SETTINGS PAGE (markup)
P.rep(cut('SPW, SPH = 1128, 980            # 0.3.28', '''assert 25 + 150 + 150 + 300 + 220 + 170 + 4 * 10 <= SPI and 185 + 300 + 220 + 170 + 2 * 10 <= SPI, "the settings footer is wider than the page"
'''), '''# 0.3.35 (kit 1.7, research/Menu-Pattern.md M8): Settings > Settings on the 1600 x 980 hub_page - the categories are the ONE sub-tab row
# (HubBar.subTab), the search row, the heading, ONE scroll list of every row of the category (no pages; Skyy rule 7: a short list gets
# bigger rows - HubBar.growSize over STG_ROW_H), the always-on line; the footer = the hint / status line, Reset all, Close (no menu button:
# row 1 Home). The ON / OFF looks stay the SkyyHud green / red Skyy approved; the frame, tabs, rows and buttons are the kit's.
SPW, SPH = SUI.HUB_PAGE_W, SUI.HUB_PAGE_H        # 1600 x 980
SPI = SUI.HUB_PAGE_IW                            # 1552
STG_CH = SPH - SUI.TITLE_H - 2 * 24 - SUI.HUB_BIG_ROW_H - SUI.HUB_BIG_TABS_H - SUI.SUB_ROW_H - SUI.FOOT_H     # 676: the content
SFIND_H, SFIND_BTN = 52, 150
SFIND_W = SPI - 2 * SFIND_BTN - 2 * 10
STG_HEAD_H, STG_ALWAYS_H = 40, 26
STG_LIST_H = STG_CH - SFIND_H - 8 - STG_HEAD_H - STG_ALWAYS_H                   # 550
STG_ROW_H = SUI.grow_row_sizes(STG_LIST_H - 2 * SUI.WELL_LIST_PAD, 61, gap=3)  # [61, 88, 122]
STG_TXT_W = SPI - 2 * SUI.WELL_LIST_PAD - 14 - 120 - 10 - 120 - 24              # the name / help column (24 = the scrollbar + a margin)
STG_TAB_W = SUI.SUB_TAB_W
STG_RESET_W, STG_CLOSE_W = 300, 170
STG_HINT_W = SPI - STG_RESET_W - STG_CLOSE_W - 2 * SUI.FOOT_GAP
_SKY = SUI.THEME["sky"]
UI_S = {
    "SFINDROW":  "Group #SkyyStgFindRow { Anchor: (Height: %d); LayoutMode: Left; Padding: (Top: 2); }" % SFIND_H,
    "SFIND":     SUI.text_field("SkyyStgFindBox", "SkyyStgFind", w=SFIND_W, h=SFIND_H - 4, placeholder="Search every tab by name or words",
                                max_length=40, size=19),
    "SFINDGO":   'TextButton #SkyyStgFindGo { Anchor: (Width: %d, Height: %d); Text: "Search"; %s }' % (SFIND_BTN, SFIND_H - 4, SUI.theme_button_style("secondary", "normal", theme="sky")),
    "SFINDCLR":  'TextButton #SkyyStgFindClr { Anchor: (Width: %d, Height: %d); Text: "Clear"; %s }' % (SFIND_BTN, SFIND_H - 4, SUI.theme_button_style("secondary", "normal", theme="sky")),
    "SSP10F":    SUI.spacer(w=10),
    "SGAP8":     "Group { Anchor: (Height: 8); }",
    "SHEAD":     SUI.label("SkyyStgHead", "", "heading", h=STG_HEAD_H, size=22, wrap=False),
    "SROWS":     SUI.scroll_list("SkyyStgRows", h=STG_LIST_H, well=True),
    "SEMPTY":    SUI.empty_state("SkyyStgEmpty", h=80),
    "SALWAYS":   SUI.label("SkyyStgAlways", "", "caption", h=STG_ALWAYS_H, size=15),
    "SHINT":     SUI.foot_info("SkyyStgHint", STG_HINT_W),
    "SHINTST":   SUI.label("SkyyStgHint", "", "gold", h=SUI.FOOT_BTN_H, w=STG_HINT_W, size=16, wrap=True, padding={"horizontal": 8}),
    "SFSP":      SUI.spacer(w=SUI.FOOT_GAP),
    "SRESET":    SUI.foot_button("SkyyStgReset", "Reset all to defaults", STG_RESET_W),
    "SRESETARM": SUI.foot_button("SkyyStgReset", "Click again to reset ALL", STG_RESET_W, kind="destructive"),
    "SCLOSE":    SUI.foot_button("SkyyStgClose", "Close", STG_CLOSE_W, sound="cancel"),
    "SSP14":     SUI.spacer(w=14),
    "SSP10":     SUI.spacer(w=10),
    # a row's pieces after its runtime id ("Group #SkyyStgRow" + r + UI_SROWB[size], "Label #SkyyStgName" + r + UI_SNAMEB, ...)
    "STXTB":     " { Anchor: (Width: %d, Height: 52); LayoutMode: Top; }" % STG_TXT_W,
    "SNAMEB":    ' { Anchor: (Height: 28); Text: ""; Style: %s; }' % SUI.text_style(19, "rowName", bold=True),
    "SDESCB":    ' { Anchor: (Height: 24); Text: ""; Style: %s; }' % SUI.text_style(15, "text"),
    "SONB":      ' { Anchor: (Width: 120, Height: 52); Text: "ON"; %s }' % SUI.theme_button_style("secondary", "normal", theme="sky"),
    "SONSELB":   ' { Anchor: (Width: 120, Height: 52); Text: "ON"; ' + ON_SEL + " }",
    "SOFFB":     ' { Anchor: (Width: 120, Height: 52); Text: "OFF"; %s }' % SUI.theme_button_style("secondary", "normal", theme="sky"),
    "SOFFSELB":  ' { Anchor: (Width: 120, Height: 52); Text: "OFF"; ' + OFF_SEL + " }",
}
UI_SARR = {
    "SROWB": [" { Anchor: (Height: %d, Bottom: 3); Background: %s; LayoutMode: Left; Padding: (Top: %d); }" % (h_, _SKY["row"], (h_ - 52) // 2)
              for h_ in STG_ROW_H],
}
SET_UI_ALL = list(UI_S.values()) + [x for v in UI_SARR.values() for x in v]
for s_ in SET_UI_ALL:
    assert s_.count("{") == s_.count("}") and s_.count("(") == s_.count(")"), "unbalanced inline UI: " + s_
    for eid in re.findall(r"#([A-Za-z0-9_]+)\\s*\\{", s_):
        assert "_" not in eid, "underscore in element id #" + eid
        assert eid.startswith("SkyyStg"), "settings page ids start with SkyyStg: #" + eid
    assert "Anchow" not in s_ and ";;" not in s_
    for txt_ in re.findall(r'Text: "([^"]*)"', s_):              # fixed inline text: only characters already proven inline
        assert re.match(r"^[A-Za-z0-9 <>/-]*$", txt_), "inline text with unproven characters (use b.set): " + txt_
assert len(SET_TABS) <= 10 and SUI.assert_sub_tabs_fit([t[1] for t in SET_TABS], STG_TAB_W), "0.3.35: every category fits the ONE sub-tab row"
assert SFIND_H + 8 + STG_HEAD_H + STG_LIST_H + STG_ALWAYS_H == STG_CH and STG_ROW_H[0] == 61 and 4 + 52 <= 61, "0.3.35: the settings content fits"
assert 14 + STG_TXT_W + 120 + 10 + 120 <= SPI - 2 * SUI.WELL_LIST_PAD and STG_HINT_W >= 600, "0.3.35: a settings row / the footer fits"
assert SFIND_W >= 600 and SFIND_W + 2 * SFIND_BTN + 2 * 10 <= SPI, "0.3.25: the search row is wider than the Settings page"
''')

# ================================================================ Server Setup sizes (the content of a 1600 x 980 hub_page with the sub row)
P.rep('''A_BODY = APH - SUI.TITLE_H - 2 * 24 - SUI.HUB_BAR_H - 26 - 30 - 62   # 0.3.28: 724 = title bar, padding, tab strip, title line, (body), status, footer
ADM_ROWS, ADM_LROWS, ADM_GROWS, ADM_HROWS = 7, 8, 10, 8
ADM_INFOLINES, ADM_MSGLINES, ADM_PLINES, ADM_FROWS = 24, 16, 12, 4''',
      '''# 0.3.35 (kit 1.7): the page is a 1600 x 980 hub_page - row 1, row 2, the sub-tab row (the view crumbs + the title line), the body (1080
# wide, centred) and the footer (the status line + the view's buttons); the body = what is left: 676 (the title line and status moved out)
A_BODY = SUI.HUB_PAGE_H - SUI.TITLE_H - 2 * 24 - SUI.HUB_BIG_ROW_H - SUI.HUB_BIG_TABS_H - SUI.SUB_ROW_H - SUI.FOOT_H
ADM_ROWS, ADM_LROWS, ADM_GROWS, ADM_HROWS = 6, 8, 10, 8           # 0.3.35: 6 mod rows a page (was 7)
ADM_INFOLINES, ADM_MSGLINES, ADM_PLINES, ADM_FROWS = 23, 16, 12, 3   # 0.3.35: 23 info lines (was 24), 3 import files (was 4)''')
P.rep('''    "RED":   RESET_ARM,
}''', '''    "RED":   RESET_ARM,
    # 0.3.35: the view crumbs (the sub-tab row: kit small buttons), the title line beside them, the footer status line (4 colours)
    "SUBSEL": SUI.theme_button_style("primary", "small", theme="sky"),
    "SUBN":   SUI.theme_button_style("secondary", "small", theme="sky"),
    "SUBSTYLE": SUI.text_style(16, "rowName", bold=True),
    "ST0":    "(FontSize: 17, RenderBold: true, TextColor: #ffd27f, VerticalAlignment: Center, Wrap: true)",
    "ST1":    "(FontSize: 17, RenderBold: true, TextColor: #7fe07f, VerticalAlignment: Center, Wrap: true)",
    "ST2":    "(FontSize: 17, RenderBold: true, TextColor: #ffb347, VerticalAlignment: Center, Wrap: true)",
    "ST3":    "(FontSize: 17, RenderBold: true, TextColor: #ff7a7a, VerticalAlignment: Center, Wrap: true)",
}''')
P.rep('''    "AINFO":    "Group #SkyyAdmInfo { Anchor: (Height: 700); ''', '''    "AINFO":    "Group #SkyyAdmInfo { Anchor: (Height: 670); ''')
P.rep('''assert SUI.TITLE_H + 2 * 24 + SUI.HUB_BAR_H + 26 + A_BODY + 30 + 62 == APH and APH <= SUI.MAX_PAGE_H, "the server setup page must fit a 1080 px high screen"
_abody = {"list": 58 + ADM_LROWS * 76, "mod": 2 * 58 + 8 + 40 + ADM_ROWS * 76, "file": 700,''',
      '''assert SUI.TITLE_H + 2 * 24 + SUI.HUB_BIG_ROW_H + SUI.HUB_BIG_TABS_H + SUI.SUB_ROW_H + A_BODY + SUI.FOOT_H == SUI.HUB_PAGE_H == 980 and A_BODY == 676, \\
    "0.3.35: the server setup page is the 1600 x 980 hub page"
_abody = {"list": 58 + ADM_LROWS * 76, "mod": 2 * 58 + 8 + 40 + ADM_ROWS * 76, "file": 670,''')
P.rep('''assert 24 + ADM_INFOLINES * 27 <= 700 and''', '''assert 24 + ADM_INFOLINES * 27 <= 670 and''')
P.rep('''               ("ADM_MSGLINES", ADM_MSGLINES), ("ADM_PLINES", ADM_PLINES), ("ADM_FROWS", ADM_FROWS), ("ADM_INNER", A_INNER)):''',
      '''               ("ADM_MSGLINES", ADM_MSGLINES), ("ADM_PLINES", ADM_PLINES), ("ADM_FROWS", ADM_FROWS), ("ADM_INNER", A_INNER),
               ("ADM_ROWW", SUI.HUB_PAGE_IW)):   # 0.3.35: the sub-tab row / footer width''')

# ================================================================ 3. YOUR STATS (markup)
P.rep('''ST_W, ST_H = 1114, 974               # 0.3.28: the hub shell (sky padding 24 + the 52 px tab strip) around 0.3.27's body (1066 x 828)
''', '''ST_W, ST_H = SUI.HUB_PAGE_W, SUI.HUB_PAGE_H   # 0.3.35: the kit 1.7 hub page (0.3.28 - 0.3.34: 1114 x 974)
''')
P.rep(cut('def stats_page():', '''print("stats page: %d x %d, %d rows per tab, %d px left in the body, kit %s" % (ST_W, ST_H, ST_ROWS, ST_LEFT, SUI_KIT_ID))
'''), '''def stats_page():
    """0.3.35 (research/Menu-Pattern.md M4; Skyy popup 4 "Your Stats = one scroll list with headings": YES): the Skills tab's YOUR STATS view
    on the kit 1.7 hub_page - row 1, row 2 (Skills selected: Stats is part of it), the ONE sub-tab row YOUR STATS | SKILLS + the caption,
    the heading line, ONE scroll list (the Main / Combat / Gathering section heads + their stat rows; the old Skills and Profile tabs went -
    duplicates of the Skills list and Profiles), the footer: the message line, Refresh, Change Profile (Primary), Close.
    Returns (shell, stat row, head row, foot, sub-tab caption, source width)."""
    J = SUI.J
    sh = SUI.hub_page("SkyyStatF", "character", body_id="SkyyStatFB", content_id="SkyyStat", sub=True, footer=True)
    ap, body, IW = sh.appends, sh.content, sh.content_w
    subw = SUI.assert_sub_tabs_fit(list(ST_SUBTABS), ST_SUBTAB_W)
    capw = SUI.HUB_PAGE_IW - subw - ST_SUBCAP_L
    assert SUI.text_width(ST_SUB, ST_SRC_FS) <= capw, "0.3.35: the caption fits beside the sub-tabs"
    cap = SUI.label("SkyyStatSub", "", "caption", w=capw, h=SUI.SUB_TAB_H, size=ST_SRC_FS, anchor={"left": ST_SUBCAP_L})
    used = [ap.add(body, SUI.label("SkyyStatHead", "", "heading", h=30, size=20, wrap=False, anchor={"bottom": 6}))]
    list_h = sh.content_h - sum(used)
    used.append(ap.add(body, SUI.scroll_list("SkyyStatList", h=list_h, well=True)))
    left = sh.fit(used)
    assert left >= 0, "stats page parts do not fit"
    # one stat row: name | total (right-aligned) | gap | where it comes from; a section head: the section name | its note
    row_w = IW - 2 * SUI.WELL_LIST_PAD - 24
    src_w = row_w - ST_NAME_W - ST_VAL_W - ST_MID_W
    rid = J("i", "0")
    rows = [("SkyyStatList", SUI.group("SkyyStatR" + rid, "Left", h=ST_ROW_H, anchor={"bottom": ST_ROW_GAP})),
            ("SkyyStatR" + rid, SUI.label("SkyyStatN" + rid, "", "rowName", w=ST_NAME_W, h=ST_ROW_H, size=ST_NAME_FS, anchor={"left": 8})),
            ("SkyyStatR" + rid, SUI.label("SkyyStatV" + rid, "", "rowName", w=ST_VAL_W - 8, h=ST_ROW_H, size=ST_VAL_FS, align="End")),
            ("SkyyStatR" + rid, SUI.spacer(w=ST_MID_W, h=ST_ROW_H)),
            ("SkyyStatR" + rid, SUI.label("SkyyStatS" + rid, "", "rowSub", w=src_w, h=ST_ROW_H, size=ST_SRC_FS))]
    head = [("SkyyStatList", SUI.group("SkyyStatR" + rid, "Left", h=ST_HEAD_H, anchor={"top": 6, "bottom": ST_ROW_GAP})),
            ("SkyyStatR" + rid, SUI.label("SkyyStatN" + rid, "", "settingHead", w=ST_NAME_W + ST_VAL_W - 8, h=ST_HEAD_H, anchor={"left": 8})),
            ("SkyyStatR" + rid, SUI.label("SkyyStatS" + rid, "", "caption", w=row_w - ST_NAME_W - ST_VAL_W, h=ST_HEAD_H, size=ST_SRC_FS))]
    # the footer: the message line, Refresh, Change Profile (Primary; or a spacer of its width), Close - filled exactly
    g = SUI.FOOT_GAP
    msg_w = SUI.HUB_PAGE_IW - (g + SUI.BTN_MIN_W + g + ST_FOOT_PROF_W + g + SUI.BTN_MIN_W)
    foot = {
        "msg": SUI.label("SkyyStatMsg", "", "bold", w=msg_w, h=SUI.FOOT_BTN_H, size=16, col="info", wrap=True, padding={"horizontal": 8}),
        "gap": SUI.spacer(w=g),
        "refresh": SUI.foot_button("SkyyStatRefresh", "Refresh"),
        "profile": SUI.foot_button("SkyyStatProfile", "Change Profile", ST_FOOT_PROF_W, kind="primary"),
        "noprofile": SUI.spacer(w=ST_FOOT_PROF_W, h=SUI.FOOT_BTN_H),
        "close": SUI.foot_button("SkyyStatClose", "Close", sound="cancel"),
    }
    # every look this page can show, checked as one page (ids, parents, markup rules, proven properties only, the menu pattern)
    chk = SUI.hub_page_preview(sh, tabs=[(r[0], SUI.hub_tab_label("character", r[0])) for r in SUI.hub_page_tabs("character")], my_tab="skills")
    chk.extend(SUI.sub_tabs_preview("SkyyStatF", list(ST_SUBTABS), 0, ST_SUBTAB_W))
    chk.append(("SkyyStatFSub", cap))
    chk.extend(rows)
    hc = SUI.Appends([(p_.replace("SkyyStatR" + rid, "SkyyStatRh"), SUI.render(mk).replace("SkyyStatN" + SUI.render(rid), "SkyyStatNh")
                       .replace("SkyyStatS" + SUI.render(rid), "SkyyStatSh").replace("SkyyStatR" + SUI.render(rid), "SkyyStatRh")) for p_, mk in head])
    chk.extend(hc)
    for k in ("msg", "gap", "refresh", "gap", "profile", "gap", "close"):
        chk.append(("SkyyStatFFoot", foot[k]))
    chk.check("SkyyStat")
    SUI.assert_proven(chk, what="stats page")
    SUI.assert_proven([foot["noprofile"]], what="stats page footer spacer")
    SUI.check_sky_paths(chk, tab_icons=True)
    SUI.assert_menu_page(chk, sh)
    assert sum(SUI.outer_size(foot[k])[0] for k in ("msg", "gap", "refresh", "gap", "profile", "gap", "close")) == SUI.HUB_PAGE_IW, "footer not filled exactly"
    # every fixed text fits its label (the client's own font tables)
    for _t in ST_NOTES[:3]:
        assert SUI.text_width(_t, ST_SRC_FS) <= row_w - ST_NAME_W - ST_VAL_W, "stats note too wide: " + _t
    for _t in ("Charged Attack Damage", "Collection Recipes", "Other class skills", "Raw Elemental Damage"):
        assert SUI.text_width(_t, ST_NAME_FS, bold=True) <= ST_NAME_W - 8, "stat name too wide: " + _t
    for _t in ("1,000,000,000%", "999,999,999,999", "Level 100", "+1,000,000,000%"):
        assert SUI.text_width(_t, ST_VAL_FS, bold=True) <= ST_VAL_W - 8, "stat total too wide: " + _t
    return sh, rows, head, foot, cap, src_w, left


ST_ROWS = 14                         # (StatsCalc.ROWS: the class-skill packing rule; the page itself has no row limit any more)
ST_HEAD_H = 40
ST_SECTIONS = 3                      # 0.3.35: Main, Combat, Gathering (ST_TABS[:3]) - Skills and Profile went (duplicates)
ST_SH, ST_ROW_MK, ST_HEAD_MK, ST_FOOT_MK, ST_CAP_MK, ST_SRC_W, ST_LEFT = stats_page()
# a stat row's longest source text (the Java clips name + total + source to ST_LINE_MAX characters) fits its column
for _t in ("Gear +40, Accessories +12, Overall +7, Skills +18, Trees +5, base 9",
           "Accessories +4, Overall +2.8, Class +10, Base Mana +10, Skills +2.4, base 9",
           "W" * 8 + " level 100 +50%, Skill trees +50% (max 100%)",
           "some blocks only: Foraging level 100 +50%, Skill trees +50% (max 100%)",
           "Swordsmanship 100, Assassination 100, Zen 100, Sorcery 100",
           "Swordsmanship level 100 +20%, Class balance +12.5%"):   # 0.3.13: the Class Weapon Damage row with skill:dmg
    assert SUI.text_width(_t, ST_SRC_FS) <= ST_SRC_W, "source column too narrow for: " + _t
ST_SHELL_JAVA = ST_SH.java("b")
ST_ROW_JAVA = "\\n".join(SUI.java_append(p, mk) for p, mk in ST_ROW_MK)
ST_HEAD_JAVA = "\\n".join(SUI.java_append(p, mk) for p, mk in ST_HEAD_MK)
ST_FOOT_JAVA = dict((k, SUI.java_append("SkyyStatFFoot", mk)) for k, mk in ST_FOOT_MK.items())
ST_SUB_JAVA = "\\n".join(['@PKG@.HubBar.subTab(b, ev, "SkyyStatF", 0, %s, true, "hub:stats", %d);' % (SUI.java_lit(ST_SUBTABS[0]), ST_SUBTAB_W),
                         '@PKG@.HubBar.subTab(b, ev, "SkyyStatF", 1, %s, false, "hub:skills", %d);' % (SUI.java_lit(ST_SUBTABS[1]), ST_SUBTAB_W),
                         SUI.java_append("SkyyStatFSub", ST_CAP_MK)])
ST_STATIC = [SUI.render(mk) for _p, mk in ST_SH.appends if not SUI.has_j(mk)]
print("stats page: %d x %d, one scroll list (%d sections), %d px left in the body, kit %s" % (ST_W, ST_H, ST_SECTIONS, ST_LEFT, SUI_KIT_ID))
''')
P.rep('''ST_SUBTAB_W, ST_SUBROW_B, ST_SUBCAP_L = 130, 4, 12''', '''ST_SUBTAB_W, ST_SUBROW_B, ST_SUBCAP_L = SUI.SUB_TAB_W, 4, 12   # 0.3.35: the kit's 150 px sub-tabs''')
P.rep('''ST_FOOT_MENU_W, ST_FOOT_PROF_W, ST_FOOT_GAP = 220, 200, 6''', '''ST_FOOT_PROF_W, ST_FOOT_GAP = 200, 6   # 0.3.35: the menu button went (row 1 Home)''')

# ================================================================ 1. THE SHELLS + Home / Teleport
P.rep(cut('''MH_W, MH_H = GW + 2 * HUB_PAD, SUI.MAX_PAGE_H''', '''assert ADM_HUB_SH.inner_w == A_INNER and ADM_HUB_SH.inner_h == 26 + A_BODY + 30 + 62, "0.3.29: server setup fits"
'''), '''# 0.3.35 MENU PATTERN (research/Menu-Pattern.md 3; kit 1.7): every Menu page is the 1600 x 980 hub_page - row 1 (HubBar.bigRowFill), row 2
# (HubBar.bigTabsFill) and the X from HubBar.page17; no page draws its own bars or a back button any more.
assert SUI.KIT_PAGE_VERSION == "1.7" and SUI.HUB_PAGE_IW == 1552, "0.3.35: kit 1.7 (hub_page)"
MH_W, MH_H = SUI.HUB_PAGE_W, SUI.HUB_PAGE_H          # the classic menu views (Players, a player, Mods): 1600 x 980 (0.3.34: 804 x 980)
APW, APH = SUI.HUB_PAGE_W, SUI.HUB_PAGE_H            # Server Setup: 1600 x 980 (its body stays A_INNER = 1080 wide, centred)
MENU_HUB_SH =dict((h, SUI.hub_page("SkyyMenuH", h, body_id="SkyyMenuHB", content_id="SkyyMenu", content_layout="Left", footer=True))
                   for h in ("social", "settings"))
STG_HUB_SH = SUI.hub_page("SkyyStgH", "settings", body_id="SkyyStgHB", content_id="SkyyStg", sub=True, footer=True)
ADM_HUB_SH = SUI.hub_page("SkyyAdmH", "settings", body_id="SkyyAdmHB", content_id="SkyyAdm", content_w=A_INNER, sub=True, footer=True)
assert STG_HUB_SH.content_h == STG_CH and ADM_HUB_SH.content_h == A_BODY and ADM_HUB_SH.content_w == A_INNER, "0.3.35: the Settings / Server Setup content"
# THE CLASSIC VIEWS (Social > Players, a player's page, Settings > Mods): the 9 x 6 grid (96 px slots) on the left, the info panel on the
# right, the footer = the hint / status line, the grid's page arrows (a grid of slots keeps pages - menu-pattern-ok) and Close. The grid's
# Go Back / Close / page tiles went: row 2's Players tab leads back from a player's page, row 1 Home from everywhere.
CL_SLOT, CL_ICON = 96, 70
CL_GW, CL_GH = CL_SLOT * COLS, CL_SLOT * ROWS          # 864 x 576
CL_GAP = 20
CL_INFO_W = SUI.HUB_PAGE_IW - CL_GW - CL_GAP           # 668
CL_INFO_LINES = 18
CL_DESC_H = 84                                         # the wrapped first line: 4 lines of 16 px (0.3.34: 2 lines in a 728 px box)
CL_BTN_W, CL_CLOSE_W = 150, 170
CL_HINT_W = SUI.HUB_PAGE_IW - 2 * CL_BTN_W - CL_CLOSE_W - 3 * SUI.FOOT_GAP
_clgrid = lambda tips: ("ItemGrid #SkyyMGrid { Anchor: (Horizontal: 0, Top: 3, Width: %d, Height: %d); SlotsPerRow: %d; AreItemsDraggable: false; %s"
                        "Style: (SlotSize: %d, SlotIconSize: %d, SlotSpacing: 0); }" % (CL_GW, CL_GH, COLS, "" if tips else "InfoDisplay: None; ", CL_SLOT, CL_ICON))
UI35 = {
    "CGRIDWRAP": "Group #SkyyMGridWrap { Anchor: (Width: %d, Height: %d); }" % (CL_GW, CL_GH + 6),
    "CGRID": _clgrid(True),
    "CGRIDNT": _clgrid(False),
    "CGAP": SUI.spacer(w=CL_GAP),
    "CINFOBOX": "Group #SkyyMInfoBox { Anchor: (Width: %d, Height: %d); LayoutMode: Top; Padding: (Horizontal: 16, Vertical: 12); Background: %s; }" % (
        CL_INFO_W, CL_GH + 6, SUI.THEME["sky"]["inset"]),
    "CINFONAME": SUI.label("SkyyMInfoName", "", "heading", h=32, size=20, wrap=False),
    "CINFODESC": SUI.label("SkyyMInfoDesc", "", "default", h=CL_DESC_H, size=16, col="rowName", wrap=True),
    "CHINT": SUI.foot_info("SkyyMHint", CL_HINT_W),
    "CHINTST": SUI.label("SkyyMHint", "", "gold", h=SUI.FOOT_BTN_H, w=CL_HINT_W, size=16, wrap=True, padding={"horizontal": 8}),
    "CFSP": SUI.spacer(w=SUI.FOOT_GAP),
    "CNOPAGE": SUI.spacer(w=2 * CL_BTN_W + 2 * SUI.FOOT_GAP, h=SUI.FOOT_BTN_H),
    "CPREV": SUI.foot_button("SkyyMPrev", "< Prev", CL_BTN_W),    # menu-pattern-ok: the grid's slot pages
    "CNEXT": SUI.foot_button("SkyyMNext", "Next >", CL_BTN_W),    # menu-pattern-ok: the grid's slot pages
    "CCLOSE": SUI.foot_button("SkyyMClose", "Close", CL_CLOSE_W, sound="cancel"),
}
UI35_CINFO = [SUI.label("SkyyMInfo%d" % i, "", "default", h=22, size=15, wrap=False) for i in range(CL_INFO_LINES)]
assert 32 + CL_DESC_H + CL_INFO_LINES * 22 + 24 <= CL_GH + 6 and CL_GH + 6 <= MENU_HUB_SH["social"].content_h, "0.3.35: the classic info panel + grid fit"
assert CL_HINT_W + SUI.FOOT_GAP + 2 * (CL_BTN_W + SUI.FOOT_GAP) + CL_CLOSE_W == SUI.HUB_PAGE_IW, "0.3.35: the classic footer is filled exactly"
for _h, _sh in MENU_HUB_SH.items():
    _cv = SUI.hub_page_preview(_sh, tabs=[(r[0], SUI.hub_tab_label(_h, r[0])) for r in SUI.hub_page_tabs(_h)], my_tab="players" if _h == "social" else "mods")
    for _k in ("CGRIDWRAP", "CGAP", "CINFOBOX"):
        _cv.append(("SkyyMenu", UI35[_k]))
    _cv.append(("SkyyMGridWrap", UI35["CGRID"]))
    for _k in ("CINFONAME", "CINFODESC"):
        _cv.append(("SkyyMInfoBox", UI35[_k]))
    for _mk in UI35_CINFO:
        _cv.append(("SkyyMInfoBox", _mk))
    for _k in ("CHINT", "CFSP", "CPREV", "CFSP", "CNEXT", "CFSP", "CCLOSE"):
        _cv.append(("SkyyMenuHFoot", UI35[_k]))
    SUI.check_page(_cv, "SkyyM")
    SUI.assert_proven(_cv, what="classic %s view" % _h)
    SUI.check_sky_paths(_cv, tab_icons=True)
    SUI.assert_menu_page(_cv, _sh, pager_ok=True)       # the grid's slot pages (a page of real slots, like the Vault)
    assert SUI.used_width(SUI.Appends([(p_, mk) for p_, mk in _cv if p_ == "SkyyMenu"]), "SkyyMenu") <= SUI.HUB_PAGE_IW, "0.3.35: the classic content fits"
''')
# Home: 1600 x 980 (926 before); the grid moves down by HOME_LEAD so its centre slot keeps its screen spot
P.rep('''HOME_H = 926
''', '''HOME_H = SUI.HUB_PAGE_H                  # 0.3.35: 980 (the kit 1.7 hub page; 0.3.30 - 0.3.34: 926)
HOME_LEAD = (HOME_H - 926) // 2         # 0.3.35: 27 px above the Home body, so the grid's centre slot stays where it was on screen
''')
P.rep(cut('''def big_shell(prefix, w, h, hub, title, body_id):''', '''    return out


'''), '''# 0.3.35: big_shell (0.3.30 - 0.3.34) went - Home and Teleport are kit 1.7 hub pages (SUI.hub_page), their rows the kit's HubBar.page17


''')
P.rep('''HOME_SH = big_shell("SkyyMHm", HOME_W, HOME_H, "home", "SkyWynn Menu", "SkyyMHome")''',
      '''HOME_SH = SUI.hub_page("SkyyMHm", "home", title="SkyWynn Menu", body_id="SkyyMHmB", content_id="SkyyMHome")   # 0.3.35: kit 1.7''')
P.rep('''assert BR_H + BR_BELOW + HOME_MAIN_H + HOME_FOOTGAP + HOME_FOOT_H <= HOME_SH.inner_h, "0.3.30: the Home body fits"''',
      '''assert HOME_LEAD + HOME_MAIN_H + HOME_FOOTGAP + HOME_FOOT_H <= HOME_SH.inner_h and HOME_SH.w == HOME_W, "0.3.35: the Home body fits"''')
P.rep('''TP_W, TP_H = 1300, 962''', '''TP_W, TP_H = SUI.HUB_PAGE_W, SUI.HUB_PAGE_H   # 0.3.35: 1600 x 980 (0.3.30 - 0.3.34: 1300 x 962)
TP_LEAD_Y = (TP_H - 962) // 2                 # 0.3.35: 9 px above the grid row (the centre slot keeps its screen spot)''')
P.rep('''TP_SH = big_shell("SkyyMTp", TP_W, TP_H, "world", "World", "SkyyMTpB")''',
      '''TP_SH = SUI.hub_page("SkyyMTp", "world", body_id="SkyyMTpBody", content_id="SkyyMTpB")   # 0.3.35: kit 1.7''')
P.rep('''assert TP_LEAD == 326 and BR_H + BR_BELOW + BT_H + BT_BELOW + HG_H + HOME_GRID_TOP + TP_GAP + TP_INFO_H + TP_GAP + HOME_FOOT_H <= TP_SH.inner_h, \\''',
      '''assert TP_LEAD == 476 and TP_LEAD_Y + HG_H + HOME_GRID_TOP + TP_GAP + TP_INFO_H + TP_GAP + HOME_FOOT_H <= TP_SH.inner_h, \\''')
P.rep('''          SUI.TITLE_H + HUB_PAD + BR_H + BR_BELOW + HOME_MIDT_H + HOME_MIDGAP + HOME_GRID_TOP + HG_CR * SLOT30 + SLOT30 // 2 - HOME_H // 2)''',
      '''          SUI.TITLE_H + HUB_PAD + BR_H + BR_BELOW + HOME_LEAD + HOME_MIDT_H + HOME_MIDGAP + HOME_GRID_TOP + HG_CR * SLOT30 + SLOT30 // 2 - HOME_H // 2)''')
P.rep('''        SUI.TITLE_H + HUB_PAD + BR_H + BR_BELOW + BT_H + BT_BELOW + HOME_GRID_TOP + HG_CR * SLOT30 + SLOT30 // 2 - TP_H // 2)''',
      '''        SUI.TITLE_H + HUB_PAD + BR_H + BR_BELOW + BT_H + BT_BELOW + TP_LEAD_Y + HOME_GRID_TOP + HG_CR * SLOT30 + SLOT30 // 2 - TP_H // 2)''')
P.rep('''    "TGAP": SUI.spacer(h=TP_GAP),''', '''    "TGAP": SUI.spacer(h=TP_GAP),
    "HLEAD": SUI.spacer(h=HOME_LEAD),        # 0.3.35
    "TLEADY": SUI.spacer(h=TP_LEAD_Y),       # 0.3.35''')
P.rep('''("prev", "< Prev", 130, "secondary", None), ("next", "Next >", 130, "secondary", None),''',
      '''("prev", "< Prev", 130, "secondary", None), ("next", "Next >", 130, "secondary", None),   # menu-pattern-ok: the grid's slot pages''')
P.rep('''("aprev", "< Prev", 130, "secondary", None), ("anext", "Next >", 130, "secondary", None), ("acancel", "Cancel", 140, "secondary", "cancel")]''',
      '''("aprev", "< Prev", 130, "secondary", None), ("anext", "Next >", 130, "secondary", None), ("acancel", "Cancel", 140, "secondary", "cancel")]   # menu-pattern-ok''')
P.rep('''_hp = SUI.Appends(list(HOME_SH.appends))
_hp.extend(big_row_preview("SkyyMHome", _ROWHUBS, "home", HOME_ROW_W))
_hp.append(("SkyyMHome", UI29["HMAIN"]))''', '''_hp = SUI.hub_page_preview(HOME_SH, hubs=_ROWHUBS)          # 0.3.35: the kit 1.7 shell + row 1 (= HubBar.page17)
_hp.append(("SkyyMHome", UI29["HLEAD"]))
_hp.append(("SkyyMHome", UI29["HMAIN"]))''')
P.rep('''_tp = SUI.Appends(list(TP_SH.appends))
_tp.extend(big_row_preview("SkyyMTpB", _ROWHUBS, "world", TP_ROW_W))
_tp.extend(big_tabs_preview("SkyyMTpB", "world", _wtabs, "teleport", TP_ROW_W))
_tp.append(("SkyyMTpB", UI29["TROW"]))''', '''_tp = SUI.hub_page_preview(TP_SH, hubs=_ROWHUBS, tabs=_wtabs, my_tab="teleport", art=TAB_ART)   # 0.3.35: kit 1.7 rows 1 + 2
_tp.append(("SkyyMTpB", UI29["TLEADY"]))
_tp.append(("SkyyMTpB", UI29["TROW"]))''')
P.rep('''SUI.check_page(_tp, "SkyyM")
SUI.assert_proven(_tp, what="Teleport page")''', '''SUI.check_page(_tp, "SkyyM")
SUI.assert_proven(_tp, what="Teleport page")
SUI.assert_menu_page(_hp, HOME_SH, pager_ok=True)     # 0.3.35: the menu pattern (the grid's slot pages keep their arrows)
SUI.assert_menu_page(_tp, TP_SH, pager_ok=True)''')
# the hub pages' build-time checks + Java lines (kit 1.7)
P.rep(cut('''HUB_LABEL_FIT = {}
for _t, _sh, _h, _my in HUB_PAGES:''', '''    HUB_LABEL_FIT[_t] = _tw
'''), '''HUB_LABEL_FIT = {}
for _t, _sh, _h, _my in HUB_PAGES:      # 0.3.35: kit 1.7 hub pages - shell + rows 1 + 2 (Python twins of HubBar.page17), the menu pattern
    assert (_sh.w, _sh.h) == (1600, 980) and _sh.page, "0.3.35: %s is a 1600 x 980 hub page" % _t
    _pp = os.path.commonprefix([_sh.prefix, _sh.content])
    _sel = "skills" if _t == "stats" else _my       # Stats is part of the Skills tab (the strip shows Skills selected)
    _pv = SUI.hub_page_preview(_sh, hubs=_ROWHUBS, tabs=[(r[0], SUI.hub_tab_label(_h, r[0])) for r in SUI.hub_page_tabs(_h)], my_tab=_sel, art=TAB_ART)
    SUI.check_page(_pv, _pp)
    SUI.assert_proven(_pv, what="hub page " + _t)
    _els = SUI.check_sky_paths(_pv, tab_icons=True)
    assert {"Header", "HeaderOrnament", SUI.HUB_FRAME[_h], "Close", "Tab", "Tab_Selected"} <= set(_els), "0.3.35: %s: %s" % (_t, _els)
    SUI.assert_menu_page(_pv, _sh)
    HUB_LABEL_FIT[_t] = SUI.assert_big_tabs_fit(_h)
''')
P.rep('''ST_HUB_JAVA = SUI.java_hub_build(ST_SH, "stats", cls="@PKG@.HubBar")
# 0.3.33: the strip shows the HOST selected (Skills) while Stats is a merged tab (HubBar.selOf; Stats itself when SkyySkills is not loaded)
assert ST_HUB_JAVA.count('"character", "stats", ') == 1
ST_HUB_JAVA = ST_HUB_JAVA.replace('"character", "stats", ', '"character", @PKG@.HubBar.selOf("character", "stats"), ')
STG_HUB_BUILD = SUI.java_hub_build(STG_HUB_SH, "settings", cls="@PKG@.HubBar", uuid="u")
ADM_HUB_BUILD = SUI.java_hub_build(ADM_HUB_SH, "setup", cls="@PKG@.HubBar", uuid="me()")
MH_BUILD = '@PKG@.HubBar.build2(b, ev, "SkyyMenuH", hubName(), hubTab(), %d, this.playerRef.getUuid(), %d, %d);' % (
    GW, SUI.HUB_PART_ROW | SUI.HUB_PART_CLOSE, MENU_HUB_SH["social"].row_w)
assert ST_HUB_JAVA.startswith('@PKG@.HubBar.build2(b, ev, "SkyyStatF", "character", @PKG@.HubBar.selOf("character", "stats"), 1066,') and ST_HUB_JAVA.endswith(", 6, %d);" % (ST_W - 50))''',
      '''# 0.3.33: the strip shows the HOST selected (Skills) while Stats is a merged tab (HubBar.selOf; Stats itself when SkyySkills is not loaded)
ST_HUB_JAVA = SUI.java_hub_page(ST_SH, cls="@PKG@.HubBar", tab_expr='@PKG@.HubBar.selOf("character", "stats")')   # 0.3.35: kit 1.7
STG_HUB_BUILD = SUI.java_hub_page(STG_HUB_SH, "settings", cls="@PKG@.HubBar", uuid="u")
ADM_HUB_BUILD = SUI.java_hub_page(ADM_HUB_SH, "setup", cls="@PKG@.HubBar", uuid="me()")
MH_BUILD = '@PKG@.HubBar.page17(b, ev, "SkyyMenuH", hubName(), hubTab(), %d, this.playerRef.getUuid(), %d);' % (SUI.HUB_PAGE_IW, SUI.HUB_PART_CLOSE)
# Home / Teleport: rows 1 + 2 from the kit (their X keeps its own binding: parts 0)
HOME_PAGE17 = SUI.java_hub_page(HOME_SH, cls="@PKG@.HubBar", uuid="me").replace(", 2);", ", 0);")
TP_PAGE17 = SUI.java_hub_page(TP_SH, "teleport", cls="@PKG@.HubBar", uuid="me").replace(", 2);", ", 0);")
assert HOME_PAGE17.endswith('"home", null, 1552, me, 0);') and TP_PAGE17.endswith('"world", "teleport", 1552, me, 0);')
assert ST_HUB_JAVA == '@PKG@.HubBar.page17(b, ev, "SkyyStatF", "character", @PKG@.HubBar.selOf("character", "stats"), 1552, this.playerRef.getUuid(), 2);\'''')
# MenuData: the 0.3.35 markup
P.rep('''F(dat, "public static final String[] UI_FBT = %s;" % jarr(UI29_FBT))''', '''F(dat, "public static final String[] UI_FBT = %s;" % jarr(UI29_FBT))
for _k, _v in sorted(UI35.items()):        # 0.3.35: the classic views on the kit 1.7 page
    F(dat, "public static final String UI_%s = %s;" % (_k, jstr(_v)))
F(dat, "public static final String[] UI_CINFO = %s;" % jarr(UI35_CINFO))
F(dat, "public static final int CL_INFO_LINES = %d;" % CL_INFO_LINES)''')
P.rep('''for _n, _v in UI_SARR.items():
    F(dat, "public static final String[] UI_%s = %s;" % (_n, jarr(_v)))''', '''for _n, _v in UI_SARR.items():
    F(dat, "public static final String[] UI_%s = %s;" % (_n, jarr(_v)))
F(dat, "public static final int STG_LIST_H = %d;" % STG_LIST_H)           # 0.3.35: the settings list + its row sizes (rule 7)
F(dat, "public static final int[] STG_ROW_H = %s;" % jints(STG_ROW_H))
F(dat, "public static final int STG_TAB_W = %d;" % STG_TAB_W)''')

# ---- the Home / Teleport build: rows 1 + 2 from the kit
P.rep('''    bigRow(b, ev, "#SkyyMHome", "home", @PKG@.MenuData.HOME_ROW_W);
    b.appendInline("#SkyyMHome", @PKG@.MenuData.UI_HMAIN);''', '''    """ + HOME_PAGE17 + r"""   // 0.3.35: row 1 (kit 1.7)
    b.appendInline("#SkyyMHome", @PKG@.MenuData.UI_HLEAD);
    b.appendInline("#SkyyMHome", @PKG@.MenuData.UI_HMAIN);''')
P.rep('''    bigRow(b, ev, "#SkyyMTpB", "world", @PKG@.MenuData.TP_ROW_W);
    bigTabs(b, ev, "#SkyyMTpB", "world", "teleport", @PKG@.MenuData.TP_ROW_W);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TROW);''', '''    """ + TP_PAGE17 + r"""   // 0.3.35: rows 1 + 2 (kit 1.7)
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TLEADY);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TROW);''')

# ---- 2. the classic views' build (Players / a player / Mods)
P.rep(cut('''  int nInfo = @PKG@.MenuData.HUB_INFO_LINES;
  @PKG@.MenuHub.ensure(this.playerRef.getUuid());''', '''  ev.addEventBinding(@BT@.Activating, "#SkyyMClose", @EVD@.of("a", "mclose"));
'''), '''  int nInfo = @PKG@.MenuData.CL_INFO_LINES;
  @PKG@.MenuHub.ensure(this.playerRef.getUuid());
  if (hubName().equals("social")) {
""" + "\\n".join("    " + ln for ln in MH_JAVA["social"].split("\\n")) + r"""
  } else {
""" + "\\n".join("    " + ln for ln in MH_JAVA["settings"].split("\\n")) + r"""
  }
  // 0.3.35: the grid (left) + the info panel (right) in the kit 1.7 page; the footer: hint / status, the grid's page arrows, Close
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_CGRIDWRAP);
  b.appendInline("#SkyyMGridWrap", tipsOff ? @PKG@.MenuData.UI_CGRIDNT : @PKG@.MenuData.UI_CGRID);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_CGAP);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_CINFOBOX);
  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_CINFONAME);
  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_CINFODESC);
  for (int i = 0; i < nInfo; i++) b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_CINFO[i]);
  b.appendInline("#SkyyMenuHFoot", stx.length() > 0 ? @PKG@.MenuData.UI_CHINTST : @PKG@.MenuData.UI_CHINT);
  b.appendInline("#SkyyMenuHFoot", @PKG@.MenuData.UI_CFSP);
  if (this.pages > 1) {
    b.appendInline("#SkyyMenuHFoot", @PKG@.MenuData.UI_CPREV);
    b.appendInline("#SkyyMenuHFoot", @PKG@.MenuData.UI_CFSP);
    b.appendInline("#SkyyMenuHFoot", @PKG@.MenuData.UI_CNEXT);
    b.appendInline("#SkyyMenuHFoot", @PKG@.MenuData.UI_CFSP);
    ev.addEventBinding(@BT@.Activating, "#SkyyMPrev", @EVD@.of("a", "mprev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyMNext", @EVD@.of("a", "mnext"));
  } else {
    b.appendInline("#SkyyMenuHFoot", @PKG@.MenuData.UI_CNOPAGE);
  }
  b.appendInline("#SkyyMenuHFoot", @PKG@.MenuData.UI_CCLOSE);
  ev.addEventBinding(@BT@.Activating, "#SkyyMClose", @EVD@.of("a", "mclose"));
''')
P.rep('''  put(slots, 45, @PKG@.MenuData.ICON_BACK, "Go Back", "Back to " + back + ".", "Click to go back", "back", false);
  put(slots, 49, @PKG@.MenuData.ICON_CLOSE, "Close", "Close the menu.", "Click to close", "close", false);
  if (this.pages > 1) {
    if (this.pageNo > 0) put(slots, 48, @PKG@.MenuData.ICON_PREV, "Previous Page", "Page " + this.pageNo + " of " + this.pages + ".", "Click to go back a page", "prev", false);
    if (this.pageNo < this.pages - 1) put(slots, 50, @PKG@.MenuData.ICON_NEXT, "Next Page", "Page " + (this.pageNo + 2) + " of " + this.pages + ".", "Click for the next page", "next", false);
  }''', '''  // 0.3.35: no grid buttons (the old back / close / page tiles) - rows 1 + 2 lead away, the footer has Close and the page arrows
  if (back == null) return;''')
P.rep('''"Player offline", "That player is no longer online.", "Click to go back", "back", true);''',
      '''"Player offline", "That player is no longer online.", "Players above lists who is online", "info", true);   // 0.3.35''')

# ---- 3. YOUR STATS: StatsCalc.allRows + the page build
P.rep('''# ================= 0.3.10 StatsPage: the Stats page (one inline page, tabs switched with rebuild(); no timers, no MouseEntered/Exited) =================''',
      '''# 0.3.35: Your Stats = ONE scroll list - each section (Main, Combat, Gathering) = a head row {null, name, note} + its stat rows
M(scl, r"""
public static java.util.ArrayList allRows(java.util.UUID u, Object[] vit) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int t = 0; t < 3 && t < TABS.length; t++) {
    java.util.ArrayList rs = rows(u, t, vit);
    out.add(new String[] { null, TABS[t], t < NOTES.length ? NOTES[t] : "" });
    for (int i = 0; i < rs.size(); i++) out.add(rs.get(i));
  }
  return out;
}""")

# ================= 0.3.10 StatsPage: the Stats page (one inline page, tabs switched with rebuild(); no timers, no MouseEntered/Exited) =================''')
P.rep(cut('''  if (this.tab < 0 || this.tab >= @PKG@.StatsCalc.TABS.length) this.tab = 0;
  Object[] vit = null;''', '''  b.set("#SkyyStatMsg.Text", this.status == null ? "" : this.status);
}""")'''), '''  Object[] vit = @PKG@.StatsCalc.vitals(st, ref);
  java.util.ArrayList rows = @PKG@.StatsCalc.allRows(u, vit);      // 0.3.35: one scroll list (Main, Combat, Gathering)
  boolean prof = profilesCmd() != null;
""" + "\\n".join("  " + ln for ln in ST_SHELL_JAVA.split("\\n")) + r"""
  @PKG@.MenuHub.ensure(u);
  """ + ST_HUB_JAVA + r"""
""" + "\\n".join("  " + ln for ln in ST_SUB_JAVA.split("\\n")) + r"""
  for (int i = 0; i < rows.size(); i++) {
    String[] r = (String[]) rows.get(i);
    if (r[0] == null) {
""" + "\\n".join("      " + ln for ln in ST_HEAD_JAVA.split("\\n")) + r"""
      b.set("#SkyyStatN" + i + ".Text", r[1]);
      b.set("#SkyyStatS" + i + ".Text", r[2]);
      continue;
    }
""" + "\\n".join("    " + ln for ln in ST_ROW_JAVA.split("\\n")) + r"""
    b.set("#SkyyStatN" + i + ".Text", r[0]);
    b.set("#SkyyStatV" + i + ".Text", r[1]);
    b.set("#SkyyStatS" + i + ".Text", r[2]);
  }
  """ + ST_FOOT_JAVA["msg"] + r"""
  """ + ST_FOOT_JAVA["gap"] + r"""
  """ + ST_FOOT_JAVA["refresh"] + r"""
  """ + ST_FOOT_JAVA["gap"] + r"""
  if (prof) {
    """ + ST_FOOT_JAVA["profile"] + r"""
    ev.addEventBinding(@BT@.Activating, "#SkyyStatProfile", @EVD@.of("a", "tprofile"));
  } else {
    """ + ST_FOOT_JAVA["noprofile"] + r"""
  }
  """ + ST_FOOT_JAVA["gap"] + r"""
  """ + ST_FOOT_JAVA["close"] + r"""
  ev.addEventBinding(@BT@.Activating, "#SkyyStatRefresh", @EVD@.of("a", "trefresh"));
  ev.addEventBinding(@BT@.Activating, "#SkyyStatClose", @EVD@.of("a", "tclose"));
  b.set("#SkyyStatHead.Text", @PKG@.StatsCalc.header(u, this.playerRef.getUsername()));
  b.set("#SkyyStatSub.Text", @PKG@.StatsCalc.SUB);
  b.set("#SkyyStatMsg.Text", this.status == null ? "" : this.status);
}""")''')

# ---- 4. SETTINGS: the page build (the click handler is unchanged: stab<i>, son<r> / soff<r>, sreset, sfind / sfclr, sclose)
P.rep(cut('''  int per = @PKG@.MenuData.SET_ROWS;
  int pages = keys.length <= 0 ? 1 : (keys.length + per - 1) / per;''', '''  """ + STG_HUB_BUILD + r"""
}""")'''), '''  this.pageNo = 0;                                 // 0.3.35: one scroll list - no pages
  this.rowKeys = new String[keys.length];
  String stt = this.status == null ? "" : this.status;
  if (stt.length() == 0 && @PKG@.SetStore.isBroken(u)) stt = @PKG@.MenuData.SET_TXT_BROKEN;
  @PKG@.MenuHub.ensure(u);
""" + "\\n".join("  " + ln for ln in STG_HUB_JAVA.split("\\n")) + r"""
  int shown = 0;                                   // 0.3.35: the ONE sub-tab row = the categories with rows for this player
  for (int i = 0; i < nCat; i++) {
    if (((String[]) vis[i]).length == 0) continue;
    @PKG@.HubBar.subTab(b, ev, "SkyyStgH", shown, @PKG@.MenuData.SET_TAB[i], i == this.cat && !find, "stab" + i, @PKG@.MenuData.STG_TAB_W);
    shown++;
  }
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SFINDROW);
  b.appendInline("#SkyyStgFindRow", @PKG@.MenuData.UI_SFIND);
  b.appendInline("#SkyyStgFindRow", @PKG@.MenuData.UI_SSP10F);
  b.appendInline("#SkyyStgFindRow", @PKG@.MenuData.UI_SFINDGO);
  b.appendInline("#SkyyStgFindRow", @PKG@.MenuData.UI_SSP10F);
  b.appendInline("#SkyyStgFindRow", @PKG@.MenuData.UI_SFINDCLR);
  String fd = this.findDraft == null ? "" : this.findDraft;
  if (fd.length() > 0) b.set("#SkyyStgFind.Value", fd);
  ev.addEventBinding(@BT@.Activating, "#SkyyStgFindGo", sevd("sfind"));
  ev.addEventBinding(@BT@.Activating, "#SkyyStgFindClr", sevd("sfclr"));
  ev.addEventBinding(@BT@.Validating, "#SkyyStgFind", sevd("sfind"), false);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SGAP8);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SHEAD);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SROWS);
  int sz = @PKG@.HubBar.growSize(keys.length, @PKG@.MenuData.STG_LIST_H - 8, @PKG@.MenuData.STG_ROW_H, 3);   // Skyy rule 7: a short list fills its room
  for (int r = 0; r < keys.length; r++) {
    String key = keys[r];
    this.rowKeys[r] = key;
    Object[] d = @PKG@.SetReg.info(key);
    Boolean v = @PKG@.SetStore.get(u, key);
    boolean on = v == null || v.booleanValue();
    String row = "#SkyyStgRow" + r;
    String txt = "#SkyyStgTxt" + r;
    b.appendInline("#SkyyStgRows", "Group #SkyyStgRow" + r + @PKG@.MenuData.UI_SROWB[sz]);
    b.appendInline(row, @PKG@.MenuData.UI_SSP14);
    b.appendInline(row, "Group #SkyyStgTxt" + r + @PKG@.MenuData.UI_STXTB);
    b.appendInline(txt, "Label #SkyyStgName" + r + @PKG@.MenuData.UI_SNAMEB);
    b.appendInline(txt, "Label #SkyyStgDesc" + r + @PKG@.MenuData.UI_SDESCB);
    b.appendInline(row, "TextButton #SkyyStgOn" + r + (on ? @PKG@.MenuData.UI_SONSELB : @PKG@.MenuData.UI_SONB));
    b.appendInline(row, @PKG@.MenuData.UI_SSP10);
    b.appendInline(row, "TextButton #SkyyStgOff" + r + (on ? @PKG@.MenuData.UI_SOFFB : @PKG@.MenuData.UI_SOFFSELB));
    b.set("#SkyyStgName" + r + ".Text", d == null ? key : String.valueOf(d[2]));
    String desc = d == null ? "" : String.valueOf(d[5]);
    if (find && r < this.findTabs.length) {
      String own = d == null || d[0] == null ? "SkyyMenu" : String.valueOf(d[0]);
      desc = @PKG@.MenuData.SET_TAB[this.findTabs[r]] + ("SkyyMenu".equals(own) ? "" : " (" + own + ")") + ": " + desc;
    }
    b.set("#SkyyStgDesc" + r + ".Text", @PKG@.MenuUtil.clip(desc, 150));
    ev.addEventBinding(@BT@.Activating, "#SkyyStgOn" + r, sevd("son" + r));
    ev.addEventBinding(@BT@.Activating, "#SkyyStgOff" + r, sevd("soff" + r));
  }
  if (keys.length == 0) {
    b.appendInline("#SkyyStgRows", @PKG@.MenuData.UI_SEMPTY);
    b.set("#SkyyStgEmpty.Text", find ? @PKG@.MenuData.SET_TXT_NOFIND : @PKG@.MenuData.SET_TXT_EMPTY);
  }
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SALWAYS);
  boolean armed = this.armedAt > 0L && System.currentTimeMillis() - this.armedAt <= 10000L;
  b.appendInline("#SkyyStgHFoot", stt.length() > 0 ? @PKG@.MenuData.UI_SHINTST : @PKG@.MenuData.UI_SHINT);   // the status shows here
  b.appendInline("#SkyyStgHFoot", @PKG@.MenuData.UI_SFSP);
  b.appendInline("#SkyyStgHFoot", armed ? @PKG@.MenuData.UI_SRESETARM : @PKG@.MenuData.UI_SRESET);
  b.appendInline("#SkyyStgHFoot", @PKG@.MenuData.UI_SFSP);
  b.appendInline("#SkyyStgHFoot", @PKG@.MenuData.UI_SCLOSE);
  ev.addEventBinding(@BT@.Activating, "#SkyyStgReset", sevd("sreset"));
  ev.addEventBinding(@BT@.Activating, "#SkyyStgClose", sevd("sclose"));
  int n = keys.length;
  b.set("#SkyyStgHint.Text", stt.length() > 0 ? stt : @PKG@.MenuData.SET_TXT_HINT);
  String head = find ? "Search \\"" + @PKG@.MenuUtil.clip(q, 30) + "\\"" : @PKG@.MenuData.SET_HEAD[this.cat];
  b.set("#SkyyStgHead.Text", head + "   -   " + n + (n == 1 ? " setting" : " settings"));
  b.set("#SkyyStgAlways.Text", find ? @PKG@.MenuData.SET_TXT_FIND : @PKG@.MenuData.SET_ALWAYS[this.cat]);
  """ + STG_HUB_BUILD + r"""
}""")''')

# ---- 2. SERVER SETUP: the view crumbs (sub-tab row) + the title line beside them; the status line + buttons in the kit footer
P.rep(cut('''M(apg, r"""
public void frame(@UCB@ b, String title, String sub) {''', '''  int lead = (@MD@.ADM_INNER - total) / 2;
  if (lead > 0) b.appendInline("#SkyyAdmFoot", spc(lead, 50));
  for (int i = 0; i < this.fT.size(); i++) {
    if (i > 0) b.appendInline("#SkyyAdmFoot", spc(8, 50));
    String id = "SkyyAdmF" + i;
    b.appendInline("#SkyyAdmFoot", btn(id, ((Integer) this.fW.get(i)).intValue(), 50, (String) this.fT.get(i), @MD@.ADM_BS));
    bind(ev, id, (String) this.fA.get(i));
  }
'''), '''# 0.3.35: the view crumbs = the ONE sub-tab row (Skyy rule 8: no back buttons - a sub view is a sub-tab): All mods | <the mod> | <this view>;
# the active one Primary and unbound, the others lead there (amods = the mod list, aback = the mod's page). In a confirm nothing is bound
# (any other click there = Cancel). {label, action or null, "1" = active}
M(apg, r"""
public java.util.ArrayList crumbs() {
  java.util.ArrayList c = new java.util.ArrayList();
  String v = this.view == null ? "list" : this.view;
  boolean conf = v.equals("confirm");
  boolean lst = v.equals("list") || this.locked;
  c.add(new String[] { "All mods", lst || conf ? null : "amods", lst ? "1" : "0" });
  if (lst) return c;
  if (this.mod != null && !v.equals("log") && !(v.equals("io") && this.ioAll)) {
    boolean here = v.equals("mod");
    String nm = this.mod.startsWith("Skyy") && this.mod.length() > 4 ? this.mod.substring(4) : this.mod;
    c.add(new String[] { nm, here || conf ? null : "aback", here ? "1" : "0" });
  }
  String w = null;
  if (v.equals("table")) w = "Table";
  else if (v.equals("hist")) w = "History";
  else if (v.equals("io")) w = "Export";
  else if (v.equals("log")) w = "Changes";
  else if (conf) w = "Confirm";
  if (w != null) c.add(new String[] { w, null, "1" });
  return c;
}""")
M(apg, r"""
public static boolean crumbAct(String a) {
  return "amods".equals(a) || "aback".equals(a) || "amenu".equals(a);
}""")
M(apg, r"""
public void frame(@UCB@ b, String title, String sub) {
""" + "\\n".join("  " + ln for ln in ADM_HUB_JAVA.split("\\n")) + r"""
  java.util.ArrayList cr = crumbs();
  int cw = 0;
  for (int i = 0; i < cr.size(); i++) {
    String[] c = (String[]) cr.get(i);
    if (i > 0) { b.appendInline("#SkyyAdmHSub", spc(5, 32)); cw = cw + 5; }
    b.appendInline("#SkyyAdmHSub", btn("SkyyAdmCr" + i, 150, 32, c[0], "1".equals(c[2]) ? @MD@.ADM_SUBSEL : @MD@.ADM_SUBN));
    cw = cw + 150;
  }
  b.appendInline("#SkyyAdmHSub", "Label #SkyyAdmSub { Anchor: (Width: " + (@MD@.ADM_ROWW - cw - 12) + ", Height: 32, Left: 12); Text: \\"\\"; Style: " + @MD@.ADM_SUBSTYLE + "; }");
  b.appendInline("#SkyyAdm", @MD@.UI_ABODY);
  String t = title == null ? "" : title;
  if (t.startsWith(@MD@.ADM_PREFIX)) t = t.substring(@MD@.ADM_PREFIX.length());   // the Server Setup tab already names the page
  String s = sub == null ? "" : sub;
  b.set("#SkyyAdmSub.Text", @MU@.clip(s.length() == 0 ? t : t + "   -   " + s, @MD@.ADM_SUBMAX));
}""")
M(apg, r"""
public void fReset() {
  this.fT = new java.util.ArrayList();
  this.fA = new java.util.ArrayList();
  this.fW = new java.util.ArrayList();
}""")
M(apg, r"""
public void foot(String text, String act, int w) {
  this.fT.add(text);
  this.fA.add(act);
  this.fW.add(Integer.valueOf(w));
}""")
M(apg, r"""
public void tail(@UCB@ b, @UEB@ ev) {
  int k = this.statusKind;
  if (k < 0 || k > 3) k = 0;
  java.util.ArrayList cr = crumbs();
  for (int i = 0; i < cr.size(); i++) {
    String[] c = (String[]) cr.get(i);
    if (c[1] != null) bind(ev, "SkyyAdmCr" + i, c[1]);
  }
  int total = 0;
  int nb = 0;
  for (int i = 0; i < this.fW.size(); i++) {
    if (crumbAct((String) this.fA.get(i))) continue;
    total = total + ((Integer) this.fW.get(i)).intValue() + (nb > 0 ? 8 : 0);
    nb++;
  }
  int sw = @MD@.ADM_ROWW - total - 10;
  if (sw < 200) { @MU@.warn("server setup footer is " + total + " px wide"); sw = 200; }
  String sst = k == 1 ? @MD@.ADM_ST1 : (k == 2 ? @MD@.ADM_ST2 : (k == 3 ? @MD@.ADM_ST3 : @MD@.ADM_ST0));
  b.appendInline("#SkyyAdmHFoot", "Label #SkyyAdmStatus { Anchor: (Width: " + sw + ", Height: 48); Text: \\"\\"; Style: " + sst + "; }");
  b.set("#SkyyAdmStatus.Text", firstLine(this.status));
  b.appendInline("#SkyyAdmHFoot", spc(10, 48));
  int j = 0;
  for (int i = 0; i < this.fT.size(); i++) {
    if (crumbAct((String) this.fA.get(i))) continue;
    if (j > 0) b.appendInline("#SkyyAdmHFoot", spc(8, 48));
    String id = "SkyyAdmF" + i;
    b.appendInline("#SkyyAdmHFoot", btn(id, ((Integer) this.fW.get(i)).intValue(), 48, (String) this.fT.get(i), @MD@.ADM_BS));
    bind(ev, id, (String) this.fA.get(i));
    j++;
  }
''')
for _n, _old in enumerate(('''  foot("< SkyWynn Menu", "amenu", 200);
''', '''  foot("< Mods", "amods", 150);
''', '''  foot("< Mods", "amods", 110);
''', '''  foot("< Mods", "amods", 130);
''', '''  foot("< Back", "aback", 150);
''')):
    P.rep(_old, "  // 0.3.35: the view crumbs lead away (sub-tab row; was a footer button, site %d)" % _n + chr(10))
P.rep('''  if (itemsMode && edit) { foot("Save list", "tsave", 150); foot("Undo edits", "tundo", 150); }
  foot("< Back", "aback", 130);
''', '''  if (itemsMode && edit) { foot("Save list", "tsave", 150); foot("Undo edits", "tundo", 150); }
  // 0.3.35: the view crumbs lead away (sub-tab row; was a footer button, table)
''')
P.rep('''  foot("Refresh", "arefresh", 130);
  foot("< Back", "aback", 130);
''', '''  foot("Refresh", "arefresh", 130);
  // 0.3.35: the view crumbs lead away (sub-tab row; was a footer button, history)
''')

# ---- 5 + 1: register() - the hub tab art for every mod's row 2 (kit 1.7 HubBar.hasArt); Menu's tabs without Edit shortcuts (HT_* data)
P.rep('''    am.put("home:alert:SkyyMenu", al);
    @PKG@.HubBar.mine().put("home:alert:SkyyMenu", al);
  }''', '''    am.put("home:alert:SkyyMenu", al);
    @PKG@.HubBar.mine().put("home:alert:SkyyMenu", al);
    String[] art = @PKG@.MenuData.TAB_ART;   // 0.3.35: the hub tab pictures this jar ships (kit 1.7: every mod's row 2 draws them while we are loaded)
    am.put("hub:art", art);
    @PKG@.HubBar.mine().put("hub:art", art);
  }''')
P.rep('''hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True, sub=True)   # 0.3.29: kit 1.6; 0.3.33: + merged tabs''',
      '''hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True, sub=True, page=True)   # 0.3.29: kit 1.6; 0.3.33: + merged tabs; 0.3.35: kit 1.7''')
# a saved Edit shortcuts shortcut (tab:settings:layout) keeps working on Home although the tab is not put any more
P.rep('''  if (k.startsWith("tab:")) {
    String rd = redirect(k, me);          // 0.3.34: a merged-away tab draws as where its page went (never locked)''', '''  if (k.equals("tab:settings:layout")) {   // 0.3.35: Edit shortcuts left the Settings hub (Skyy popup 5); the shortcut still opens the editor
    return new String[] { tabIcon("settings", "layout"), "Edit shortcuts", "Pick what shows on your Home page and the Teleport page.\\nThe same as the Edit shortcuts button at the foot of Home.", "Click to edit!", "sc:" + k, "ok" };
  }
  if (k.startsWith("tab:")) {
    String rd = redirect(k, me);          // 0.3.34: a merged-away tab draws as where its page went (never locked)''')

assert P.s.count("registerCommand(") == CMD0 and P.s.count("registerSystem(") == SYS0, "no command / system added in the script text"
P.finish()
