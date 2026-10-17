"""Derive SkyyRanks/build_skyyranks_0.1.2.py from the LIVE SkyyRanks 0.1.1 (build_skyyranks_0.1.1.py = the tools/deploy_set.py SET pin; it
was hand-written - "copy + edit: SkyyRanks has no patch scripts" - so 0.1.2 is the first GENERATED SkyyRanks script: never edit it, edit
this patch). Every anchor is asserted; at the end every change is undone on a copy and compared with 0.1.1 (tools/soundpass_gen.Patch).
Line endings kept.
Run:  python tools/ranks_0_1_2_patch.py   then   python SkyyRanks/build_skyyranks_0.1.2.py   (never --deploy)
Check: python SkyyRanks/test_skyyranks_0.1.2.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.1.2 (2026-10-16) = MENU PATTERN sweep S4 (Settings hub + windows), the SkyyRanks part (research/Menu-Pattern.md section 3, the S4 row of
section 4, rules 7-8; kit skyyui 1.7 hub_page; recipe tools/HUBS-CONTRACT.md 'Kit 1.7' -> 'How to move a page'). Skyy (docs/answered/ui.md
2026-10-16): "Double check every menu and make sure it's fully and completely built out / designed properly in the cohesive menu system we
made. I never want to have to use a back button. The menus at the top should always be there for easy navigation." + "work through the
small things and the next up list" + popups: every hub page Home size 1600 x 980, row 2 big like Teleport (56 px).
  1. THE RANKS EDITOR IS A SETTINGS HUB PAGE: SUI.hub_page("SkyyRk", "settings", sub=True, footer=True) - 1600 x 980 (was the 1120 x 860
     hand-styled @DecoratedContainer window), the sky theme, title bar 'Settings' + the X, row 1 (Home + the hubs) and row 2 (the Settings
     tabs with SERVER SETUP selected - ranks are server setup made in game; Ranks puts no contract tab of its own) from the kit's
     HubBar.page17 (install_hub_bar row=True, page=True), the content 1552 x 676 (keeps the old body id #SkyyRkBody), the footer.
  2. ONE SUB-TAB ROW (HubBar.subTab, 150 px small buttons, the active one Primary, drawn not bound): [RANKS][PLAYERS], with a rank open
     + [SETTINGS][GRANTS][MEMBERS] (the rank's own views), with a player open + [PLAYER]. Same click actions as the 0.1.1 190 x 40 tabs
     (tab0 - tab4); the old in-page tab strip, its separator and the window frame are gone.
  3. NO BACK BUTTONS (rule 8): '< Server Setup' is gone (row 2's Server Setup tab opens /modconfig ranks exactly as it did), 'Close' is
     gone (the X), the add row's search toggles say 'Show grants' / 'Show members' / 'Show denies' (were 'Back to ...'). The in-page
     Confirm view stays an in-page view (rows 1 + 2 above it; Confirm / Cancel) - NO separate 3.6 window is left.
  4. SCROLL LISTS (Menu-Pattern 3.3, rule 7): every list (ranks, players, a rank's grants / search hits / members / online players, a
     player's denies / search hits) is ONE SUI.scroll_list - no pager, no '< Prev' / 'Next >'; up to 200 rows, then a 'Show more' row
     (+200). Few rows grow: SUI.grow_row_sizes over the 66 px row (66 / 95 / 132; the Settings view 66 / 95 / 132 in its taller list),
     HubBar.growSize picks the biggest tier whose rows all fit, past that the list scrolls at 66 px.
  5. KIT LOOK: every style from tools/skyyui.py (SUI.verify() at build time): sky row panels, sky small row buttons (32 px, centred in the
     row's 42 px text band), sky normal buttons in the add row, kit labels / colours (SUI.COLOR), the kit text field and scroll list. The
     0.1.1 hand-copied vanilla styles and their VANILLA_CHECK block are gone (the kit proves its own values). The result line moved into
     the footer (left, + green / - red / = gold as before), Refresh on its right. The jar ships the kit's 59 Sky Window files
     (IncludesAssetPack true: Common/UI/Custom/SkyyKit/ only).
  6. Clicks: handleDataEvent asks HubBar.route right after 'close' (row 1 'hub:h:<id>': Settings = this page; Home runs /skymenu; another
     hub opens its tab; row 2's tabs; the X = hub:close = close) - BEFORE the editor's own access guard, so a player without
     skyyranks.admin can still leave by the top rows. Row 2's Server Setup ('hub:setup') = openSetup() (/modconfig ranks, the old
     '< Server Setup' button). Every other action string is unchanged (prev / next / setup / close still work, they are just not drawn).
  No logic / data / command / permission change: /rankadmin (+ player / reload / sync) and every /rank command keep requirePermission
  skyyranks.admin with no permission groups; ranks.properties, players.properties, config.properties, the bridge keys and the chat
  hook are untouched. ROLLBACK to 0.1.1: safe (layout only; no saved-data change).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyRanks", "build_skyyranks_0.1.1.py"), os.path.join(ROOT, "SkyyRanks", "build_skyyranks_0.1.2.py"))
assert P.has('VERSION = "0.1.1"\n') and P.has("(copy + edit: SkyyRanks has no patch scripts)") and not P.has("SUI.hub_page("), \
    "not the hand-written SkyyRanks 0.1.1 script"
SYS0, CMD0, REQ0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count("requirePermission(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.2 (2026-10-16)"):].rstrip() + "\n\n"


def cut(start, end):
    """the exact text of the script from start up to and including end (start unique, end the first one after it)"""
    assert P.s.count(start) == 1, "start anchor count %d: %s" % (P.s.count(start), start[:120])
    i = P.s.index(start)
    j = P.s.index(end, i)
    return P.s[i:j + len(end)]


# ---------- docstring + version
P.rep('''"""SkyyRanks 0.1.1 - build script (javassist via jpype), derived from build_skyyranks_0.1.py (copy + edit: SkyyRanks has no patch scripts).''',
      '''"""SkyyRanks 0.1.2 - build script (javassist via jpype), GENERATED by tools/ranks_0_1_2_patch.py from build_skyyranks_0.1.1.py (the
hand-written 0.1.1, itself a copy + edit of build_skyyranks_0.1.py) - never edit this file, edit the patch.''')
P.rep('''Run:   python build_skyyranks_0.1.1.py        -> SkyyRanks/SkyyRanks-0.1.1.jar''',
      '''Run:   python build_skyyranks_0.1.2.py        -> SkyyRanks/SkyyRanks-0.1.2.jar   (check: python SkyyRanks/test_skyyranks_0.1.2.py)''')
P.rep('''0.1.1 CHANGES (Skyy's 2026-09-25 lock;''', NOTE + '''0.1.1 CHANGES (Skyy's 2026-09-25 lock;''')
P.rep('VERSION = "0.1.1"\n', 'VERSION = "0.1.2"\n')

# ---------- the kit import (0.1.2: the page is a kit 1.7 hub page)
P.rep('''import skyycfg as CFG\n''', '''import skyycfg as CFG
import skyyui as SUI       # 0.1.2: the ONE shared UI kit (research/Vanilla-UI-Style-Guide.md, kit 1.7 hub_page)
SUI.verify()               # proves every vanilla value / texture / sound the kit emits against Assets.zip (read-only); stops on drift
# data colours (not UI styles): the seeded rank prefix colours, the colour words of /rank colour, the chat reply colours (lint kit colours)
UI_DATA_COLORS = ["#ff5555", "#55ffff", "#ffaa00", "#aa0000", "#ff8800", "#ffff55", "#55ff55", "#00aa00", "#5555ff", "#0000aa", "#aa00aa",
                  "#ff55ff", "#aaaaaa", "#000000", "#ffd27f", "#8fe08f", "#ff8f8f"]
''')

# ---------- RankUI: the whole markup section (0.1.1 vanilla copies + VANILLA_CHECK -> the kit 1.7 hub page)
OLD_UI = cut("# ================= RankUI: every inline markup string", '''M(ui, r"""public static String w(String t, int w) { return t.replace("%W", String.valueOf(w)); }""")\n''')
NEW_UI = r'''# ================= RankUI: every inline markup string (validated below: balanced, no underscore ids, ids start with SkyyRk) =================
# 0.1.2 MENU PATTERN (kit skyyui 1.7, research/Menu-Pattern.md 3; tools/HUBS-CONTRACT.md 'Kit 1.7'): the editor is a SUI.hub_page of the
# Settings hub - 1600 x 980, row 1 + row 2 (Server Setup selected), the ONE sub-tab row, the content 1552 x 676 (#SkyyRkBody, the old body
# id), the footer. Every style below comes from the kit (proven by SUI.verify() above): sky row panels, sky buttons, kit labels / colours,
# the kit text field and scroll list. The 0.1.1 hand-copied vanilla styles and their VANILLA_CHECK are gone (the kit proves its own).
assert SUI.KIT_PAGE_VERSION == "1.7" and SUI.HUB_THEME == "sky" and SUI.HUB_PAGE_IW == 1552, "0.1.2: kit skyyui 1.7 hub pages, sky theme"
SKY = SUI.HUB_THEME
RK_PREFIX, RK_HUB, RK_TAB = "SkyyRk", "settings", "setup"
assert RK_TAB in [r_[0] for r_ in SUI.hub_page_tabs(RK_HUB)], "0.1.2: row 2 = the Settings hub with Server Setup selected"
SH = SUI.hub_page(RK_PREFIX, RK_HUB, sub=True, footer=True, body_id="SkyyRkFB", content_id="SkyyRkBody")
IW, CH = SH.content_w, SH.content_h           # 1552 x 676
assert (IW, CH) == (1552, 676) and SH.foot == "SkyyRkFoot" and SH.sub == "SkyyRkSub" and SH.title == "SkyyRkTitle"
ROW_H, ROW_GAP, BTN_H = 66, 6, 42             # a list row (normal tier), the gap after it, the text band inside it (name 24 + caption 18)
ACT_H = SUI.BTN_SMALL_H                       # 32: the row actions are small kit buttons ...
ACT_TOP = (BTN_H - ACT_H) // 2                # ... centred in the 42 px band
FIELD_H = SUI.BTN_H                           # 44: the add row's fields and buttons (normal kit size)
HINT_H, HEAD_H, ADD_H = 26, 34, 58
LIST_H = CH - HINT_H - HEAD_H - ADD_H         # 558: the rows' scroll list, the add row under it
LISTX_H = CH - HINT_H - HEAD_H                # 616: no add row (a rank's Settings, the default rank's Members)
LIST_IN, LISTX_IN = LIST_H - 2 * SUI.WELL_LIST_PAD, LISTX_H - 2 * SUI.WELL_LIST_PAD
RW = IW - 2 * SUI.WELL_LIST_PAD - (SUI.SCROLL_SIZE + SUI.SCROLL_SPACING)   # 1532: a row inside the scrolling list well
HS = SUI.grow_row_sizes(LIST_IN, ROW_H, gap=ROW_GAP)        # Skyy rule 7: few rows grow (66 / 95 / 132)
HSX = SUI.grow_row_sizes(LISTX_IN, ROW_H, gap=ROW_GAP)
CAP = 200                                     # rows a list draws before its Show more row (Menu-Pattern 3.3; the Java says 200)
SUB_W = SUI.SUB_TAB_W                         # 150
SUB_SEP = 48 - SUI.SUB_TAB_GAP                # the space between [RANKS][PLAYERS] and a rank's / player's own sub-tabs (the 0.1.1 48 px)
SUBS = ["Ranks", "Players", "Settings", "Grants", "Members", "Player"]
assert SUI.assert_sub_tabs_fit(SUBS[:5], SUB_W) + SUB_SEP <= IW
FOOT_BTN_W = SUI.BTN_MIN_W                    # 172: Refresh
INFO_W = IW - SUI.FOOT_GAP - FOOT_BTN_W       # the result line, left of Refresh
CONF_W, CONF_GAP = 250, 40                    # Confirm / Cancel
MORE_W = 260
assert ROW_H in HS and HS[0] == ROW_H and HSX[0] == ROW_H and all(h_ <= 2 * ROW_H for h_ in HS + HSX)
TABS = ["Ranks", "Players", "Settings", "Grants", "Members"]     # the 0.1.1 tab names = the sub-tab row (tab0 - tab4)
assert SUBS[:5] == TABS


def _sid(t):
    return t.replace("%R", "9R9")             # the kit checks ids; %R (the row number) is filled at runtime


def _rid(t):
    return t.replace("9R9", "%R")


def sbtn(ident, w, text, kind="secondary", sel=False):
    """a row action: a small kit button (32 high) centred in the row's 42 px text band"""
    return 'TextButton #%s { Anchor: (Width: %d, Height: %d, Top: %d); Text: "%s"; %s }' % (
        ident, w, ACT_H, ACT_TOP, text, SUI.theme_button_style(kind, "small", selected=sel, theme=SKY))


def nbtn(ident, w, text, kind="secondary", h=FIELD_H):
    """a normal kit button (44 high): the add row's actions, Confirm / Cancel"""
    return 'TextButton #%s { Anchor: (Width: %s, Height: %d); Text: "%s"; %s }' % (ident, w, h, text, SUI.theme_button_style(kind, "normal", theme=SKY))


def lab(ident, kind, **kw):
    return _rid(SUI.label(_sid(ident), "", kind, **kw))


def field(box, fid, w, h, max_len, placeholder=None):
    """the kit text field split into its box Group and its TextField (the page appends them one after the other)"""
    mk = SUI.text_field(_sid(box), _sid(fid), w=777, h=h, placeholder="XPHX" if placeholder else "", max_length=max_len)
    i = mk.index(" TextField #")
    bx, tf = mk[:i] + " }", mk[i + 1:-2]
    assert tf.endswith("}") and bx.count("{") == bx.count("}") and tf.count("{") == tf.count("}"), mk
    bx = bx.replace("Width: 777", "Width: %W" if w is None else "Width: %d" % w)
    tf = tf.replace('PlaceholderText: "XPHX"', 'PlaceholderText: "%P"')
    return _rid(bx), _rid(tf)


BOX_, IN_ = field("SkyyRkBox%R", "SkyyRkIn%R", 400, BTN_H, 40)
FB0_, F0_ = field("SkyyRkFB0", "SkyyRkF0", None, FIELD_H, 80, True)
FB1_, F1_ = field("SkyyRkFB1", "SkyyRkF1", None, FIELD_H, 80, True)
ST_ = dict((k_, SUI.label("SkyyRkStatus", "", "default", w=INFO_W, h=SUI.FOOT_BTN_H, size=16, bold=True, col=c_, wrap=True,
                          padding={"horizontal": 8})) for k_, c_ in (("STOK", "success"), ("STBAD", "error"), ("STINFO", "gold")))
UI = {
    "HINT":   SUI.label("SkyyRkHint", "", "default", h=HINT_H, size=16, align="Center"),
    "SP48":   "Group { Anchor: (Width: %d); }" % SUB_SEP,
    "GAP8":   "Group { Anchor: (Height: 8); }",
    "GAP6":   "Group { Anchor: (Height: %d); }" % ROW_GAP,
    "HEAD":   SUI.label("SkyyRkHead", "", "section", h=HEAD_H, size=16),
    "ROWS":   SUI.scroll_list("SkyyRkRows", h=LIST_H, well=True),
    "ROWSX":  SUI.scroll_list("SkyyRkRows", h=LISTX_H, well=True),
    "ROW":    "Group #SkyyRkRow%%R { Anchor: (Height: %%H); Background: %s; LayoutMode: Left; Padding: (Top: %%Q); }" % SUI.theme_bg("row", SKY),
    "LEAD":   "Group { Anchor: (Width: 4, Height: %d); Background: %s; }" % (BTN_H, SUI.COLOR["selected"]),
    "SP10":   "Group { Anchor: (Width: 10, Height: %d); }" % BTN_H,
    "GAPUD":  "Group { Anchor: (Width: 180, Height: %d); }" % BTN_H,
    "TXTA":   "Group #SkyyRkTxt%%R { Anchor: (Width: 900, Height: %d); LayoutMode: Top; }" % BTN_H,
    "TXTB":   "Group #SkyyRkTxt%%R { Anchor: (Width: 900, Height: %d); LayoutMode: Top; }" % BTN_H,
    "TXTC":   "Group #SkyyRkTxt%%R { Anchor: (Width: 1300, Height: %d); LayoutMode: Top; }" % BTN_H,
    "TXTD":   "Group #SkyyRkTxt%%R { Anchor: (Width: 1180, Height: %d); LayoutMode: Top; }" % BTN_H,
    "TXTE":   "Group #SkyyRkTxt%%R { Anchor: (Width: 700, Height: %d); LayoutMode: Top; }" % BTN_H,
    "TXTF":   "Group #SkyyRkTxt%%R { Anchor: (Width: 900, Height: %d); LayoutMode: Top; }" % BTN_H,
    "NAME":   lab("SkyyRkName%R", "rowName", h=24, size=18, bold=True),
    "NAMEDIM": lab("SkyyRkName%R", "rowName", h=24, size=18, bold=True, col="disabled"),
    "DESC":   lab("SkyyRkDesc%R", "rowSub", h=18, size=15),
    "PRE":    lab("SkyyRkPre%R", "rowName", w=150, h=BTN_H, size=18, bold=True, col="white").replace("TextColor: %s" % SUI.COLOR["white"], "TextColor: %C"),
    "PICK":   SUI.label("SkyyRkPick", "", "gold", w=220, h=BTN_H, size=18, bold=True, align="Center"),
    "BOX":    BOX_,
    "IN":     IN_,
    "UP":     sbtn("SkyyRkUp%R", 80, "Up"),
    "DOWN":   sbtn("SkyyRkDown%R", 80, "Down"),
    "EDIT":   sbtn("SkyyRkEdit%R", 110, "Edit"),
    "DEL":    sbtn("SkyyRkDel%R", 110, "Delete", "destructive"),
    "REM":    sbtn("SkyyRkRem%R", 150, "Remove", "destructive"),
    "OPEN":   sbtn("SkyyRkOpen%R", 150, "Open"),
    "ADDR":   sbtn("SkyyRkAddr%R", 150, "Add"),
    "GR":     sbtn("SkyyRkGr%R", 150, "Grant"),
    "DENYB":  sbtn("SkyyRkDn%R", 150, "Deny", "destructive"),
    "SET":    sbtn("SkyyRkSet%R", 110, "Set"),
    "CLR":    sbtn("SkyyRkClr%R", 110, "Clear"),
    "ON":     sbtn("SkyyRkOn%R", 120, "ON", "tertiary"),
    "ONSEL":  sbtn("SkyyRkOn%R", 120, "ON", "tertiary", sel=True),
    "OFF":    sbtn("SkyyRkOff%R", 120, "OFF", "tertiary"),
    "OFFSEL": sbtn("SkyyRkOff%R", 120, "OFF", "tertiary", sel=True),
    "UP2":    sbtn("SkyyRkUp%R", 120, "Up"),
    "DOWN2":  sbtn("SkyyRkDown%R", 120, "Down"),
    "MK":     sbtn("SkyyRkMk%R", 200, "Make default"),
    "DEL2":   sbtn("SkyyRkDel%R", 120, "Delete", "destructive"),
    "CYP":    sbtn("SkyyRkCyp", 60, "<"),
    "CYN":    sbtn("SkyyRkCyn", 60, ">"),
    "SETRANK": sbtn("SkyyRkSetRank", 180, "Set rank", "primary"),
    "EMPTY":  SUI.empty_state("SkyyRkEmpty", h=90),
    "MOREROW": "Group #SkyyRkMoreRow { Anchor: (Height: %d); LayoutMode: Left; Padding: (Top: 6); }" % (ACT_H + 12),
    "MORESP": "Group { Anchor: (Width: %d, Height: %d); }" % ((RW - MORE_W) // 2, ACT_H),
    "MORE":   'TextButton #SkyyRkMore { Anchor: (Width: %d, Height: %d); Text: "Show more"; %s }' % (MORE_W, ACT_H, SUI.theme_button_style("secondary", "small", theme=SKY)),
    "ADD":    "Group #SkyyRkAdd { Anchor: (Height: %d); LayoutMode: Left; Padding: (Top: 8); }" % ADD_H,
    "ADDLBL": SUI.label("SkyyRkAddLbl", "", "section", w=130, h=FIELD_H, size=15, align="Center"),
    "ADDSP":  "Group { Anchor: (Width: 10, Height: %d); }" % FIELD_H,
    "FB0":    FB0_,
    "FB1":    FB1_,
    "F0":     F0_,
    "F1":     F1_,
    "ACT0":   nbtn("SkyyRkAct0", "%W", "%T", "primary"),
    "ACT1":   nbtn("SkyyRkAct1", "%W", "%T", "secondary"),
    "STOK":   ST_["STOK"],
    "STBAD":  ST_["STBAD"],
    "STINFO": ST_["STINFO"],
    "FSP":    "Group { Anchor: (Width: %d); }" % SUI.FOOT_GAP,
    "REFRESH": SUI.foot_button("SkyyRkRefresh", "Refresh", FOOT_BTN_W),
    "MSGBOX": "Group #SkyyRkMsgBox { Anchor: (Height: 300); Background: %s; Padding: (Horizontal: 40, Vertical: 24); LayoutMode: Top; }" % SUI.theme_bg("row", SKY),
    "WARN":   SUI.label("SkyyRkWarn", "", "warning", h=76, size=26, bold=True, align="Center", wrap=True),
    "MSG":    SUI.label("SkyyRkMsg", "", "default", h=170, size=18, align="Center", wrap=True),
    "CROW":   "Group #SkyyRkCRow { Anchor: (Height: 80); LayoutMode: Left; Padding: (Top: 18); }",
    "CLEAD":  "Group { Anchor: (Width: %d, Height: %d); }" % ((IW - 2 * CONF_W - CONF_GAP) // 2, FIELD_H),
    "CSP":    "Group { Anchor: (Width: %d, Height: %d); }" % (CONF_GAP, FIELD_H),
    "YES":    nbtn("SkyyRkYes", CONF_W, "Confirm", "destructive"),
    "NO":     nbtn("SkyyRkNo", CONF_W, "Cancel", "secondary"),
}
# placeholder and button texts that are substituted into F0/F1 (%P) and ACT0/ACT1 (%T) at runtime - validated like fixed inline text.
# 0.1.2 (rule 8): the search toggles say Show ... (were "Back to ..." - a back text)
TXT = {
    "P_ID": "id like vip", "P_NAME": "Display name like VIP", "P_NODE": "permission node or search words", "P_PLAYER": "player name or UUID",
    "P_FIND": "player name", "P_DENY": "permission node to deny",
    "A_CREATE": "Create rank", "A_GRANT": "Grant", "A_SEARCH": "Search", "A_BACKG": "Show grants", "A_ADDM": "Add member",
    "A_ONLINE": "Online players", "A_BACKM": "Show members", "A_FIND": "Search", "A_ALL": "Show all", "A_DENY": "Deny",
    "A_BACKD": "Show denies",
}


def fill(s, r=0, h=ROW_H, w=100, ph="x", t="x"):
    """one markup string with its runtime placeholders filled the way RankUI.r / RankUI.w / rowStart / field / act do"""
    return (s.replace("%R", str(r)).replace("%H", str(h)).replace("%Q", str((h - BTN_H) // 2)).replace("%C", SUI.COLOR["white"])
            .replace("%W", str(w)).replace("%P", ph).replace("%T", t))


def _check_ui(s, name):
    t = fill(s)
    assert t.count("{") == t.count("}") and t.count("(") == t.count(")"), "unbalanced inline UI %s: %s" % (name, s)
    for eid in re.findall(r"#([A-Za-z0-9_]+)\s*\{", t):
        assert "_" not in eid, "underscore in element id #" + eid
        assert eid.startswith("SkyyRk"), "ranks page ids start with SkyyRk: #" + eid
    assert "Anchow" not in t and ";;" not in t, name
    for txt_ in re.findall(r'(?:\bText|PlaceholderText): "([^"]*)"', t):
        assert re.match(r"^[A-Za-z0-9 <>/-]*$", txt_), "inline text with unproven characters (use b.set): " + txt_
        assert not SUI.MENU_BACK_RE.match(txt_) and not SUI.MENU_PAGER_RE.match(txt_), "0.1.2 rule 8 / 3.3: no back / pager text: " + txt_
    assert "%" not in t, "unfilled %% placeholder in " + name


for k_, v_ in UI.items():
    _check_ui(v_, k_)
for k_, v_ in TXT.items():
    assert re.match(r"^[A-Za-z0-9 <>/-]+$", v_), "text constant with unproven characters: " + k_
    assert not SUI.MENU_BACK_RE.match(v_) and not SUI.MENU_PAGER_RE.match(v_), "0.1.2 rule 8 / 3.3: no back / pager text: " + v_
# the content (676 px, Menu-Pattern 3.1): hint 26 + head 34 + the list 558 + the add row 58 (or the list 616 without an add row);
# the Confirm view: hint 26 + gap 8 + the message box 300 + the button row 80
assert HINT_H + HEAD_H + LIST_H + ADD_H == CH and HINT_H + HEAD_H + LISTX_H == CH
assert HINT_H + 8 + 300 + 80 <= CH and 76 + 170 + 2 * 24 <= 300, "confirm view parts"
for w_, what in ((14 + 900 + 150 + 10 + 80 + 10 + 80 + 10 + 110 + 10 + 110, "ranks row"), (14 + 900 + 400 + 10 + 110, "name row"),
                 (14 + 700 + 150 + 400 + 10 + 110 + 10 + 110, "prefix row"), (14 + 1180 + 120 + 10 + 120, "on/off row"),
                 (14 + 1180 + 200, "default row"), (14 + 1300 + 10 + 150, "list row"), (14 + 900 + 60 + 10 + 220 + 10 + 60 + 10 + 180, "rank picker"),
                 ((RW - MORE_W) // 2 + MORE_W, "show more row")):
    assert w_ <= RW, "%s is %d px wide, a list row has %d" % (what, w_, RW)
for w_, what in ((130 + 10 + 220 + 10 + 340 + 10 + 220 + 10, "new rank row"), (130 + 10 + 480 + 10 + 180 + 10 + 200 + 10, "add row"),
                 (INFO_W + SUI.FOOT_GAP + FOOT_BTN_W, "footer"), (2 * ((IW - 2 * CONF_W - CONF_GAP) // 2) + 2 * CONF_W + CONF_GAP, "confirm row")):
    assert w_ <= IW, "%s is %d px wide, the page has %d" % (what, w_, IW)
# the Java statements the page's build() runs: the hub page shell (#SkyyRk ... #SkyyRkBody, #SkyyRkFoot) and HubBar.page17 (row 1, row 2
# with Server Setup selected, the X). this.me = the viewer (the harness page has no PlayerRef).
RK_SHELL_JAVA = SH.java("b")
RK_PAGE17 = SUI.java_hub_page(SH, RK_TAB, cls="@PKG@.HubBar", uuid="this.me")
assert RK_PAGE17 == '@PKG@.HubBar.page17(b, ev, "SkyyRk", "settings", "setup", 1552, this.me, 2);', RK_PAGE17


def rk_preview(view):
    """0.1.2 build-time check: one view as build() draws it (the shell + rows 1 + 2 + the sub row + the content + the footer) through the
    kit checks - check_page, assert_proven, the Sky paths, assert_menu_page (1600 x 980, rows 1 + 2, one sub row, no back / pager text,
    the content fits 676)."""
    pv = SUI.hub_page_preview(SH, tabs=[(r_[0], SUI.hub_tab_label(RK_HUB, r_[0])) for r_ in SUI.hub_page_tabs(RK_HUB)], my_tab=RK_TAB)
    ap = SUI.Appends(pv)
    if view == "settings":
        labs, sel = SUBS[:5], 2
    elif view == "player":
        labs, sel = SUBS[:2] + SUBS[5:], 2
    else:
        labs, sel = SUBS[:2], (None if view == "confirm" else 0)
    if view != "confirm":
        ap.extend(SUI.sub_tabs_preview(RK_PREFIX, labs, sel, SUB_W))
    ap.append(("SkyyRkBody", UI["HINT"]))
    sets = [("SkyyRkHint.Text", "x")]
    if view == "confirm":
        for p_, k_ in (("SkyyRkBody", "GAP8"), ("SkyyRkBody", "MSGBOX"), ("SkyyRkMsgBox", "WARN"), ("SkyyRkMsgBox", "MSG"), ("SkyyRkBody", "CROW"),
                       ("SkyyRkCRow", "CLEAD"), ("SkyyRkCRow", "YES"), ("SkyyRkCRow", "CSP"), ("SkyyRkCRow", "NO")):
            ap.append((p_, UI[k_]))
    else:
        ap.append(("SkyyRkBody", UI["HEAD"]))
        ap.append(("SkyyRkBody", UI["ROWSX" if view == "settings" else "ROWS"]))
        hs = HSX if view == "settings" else HS
        n = 7 if view in ("settings", "player") else 3
        h = hs[SUI.grow_pick(n, LISTX_IN if view == "settings" else LIST_IN, hs, ROW_GAP)]
        for r in range(n):
            ap.append(("SkyyRkRows", fill(UI["ROW"], r, h)))
            rid = "SkyyRkRow%d" % r
            for k_ in ("LEAD", "SP10"):
                ap.append((rid, UI[k_]))
            ap.append((rid, fill(UI["TXTA" if view == "ranks" else ("TXTD" if view == "settings" else "TXTC")], r)))
            ap.append(("SkyyRkTxt%d" % r, fill(UI["NAME"], r)))
            ap.append(("SkyyRkTxt%d" % r, fill(UI["DESC"], r)))
            if view == "ranks":
                for k_ in ("PRE", "SP10", "UP", "SP10", "DOWN", "SP10", "EDIT", "SP10", "DEL"):
                    ap.append((rid, fill(UI[k_], r)))
            elif view == "settings":
                for k_ in ("ONSEL", "SP10", "OFF"):
                    ap.append((rid, fill(UI[k_], r)))
            else:
                for k_ in ("SP10", "REM"):
                    ap.append((rid, fill(UI[k_], r)))
            ap.append(("SkyyRkRows", UI["GAP6"]))
        ap.append(("SkyyRkRows", UI["MOREROW"]))
        ap.append(("SkyyRkMoreRow", UI["MORESP"]))
        ap.append(("SkyyRkMoreRow", UI["MORE"]))
        if view != "settings":
            for p_, mk_ in (("SkyyRkBody", UI["ADD"]), ("SkyyRkAdd", UI["ADDLBL"]), ("SkyyRkAdd", UI["ADDSP"]), ("SkyyRkAdd", fill(UI["FB0"], w=480)),
                            ("SkyyRkFB0", fill(UI["F0"], ph=TXT["P_NODE"])), ("SkyyRkAdd", UI["ADDSP"]), ("SkyyRkAdd", fill(UI["ACT0"], w=180, t=TXT["A_GRANT"])),
                            ("SkyyRkAdd", UI["ADDSP"]), ("SkyyRkAdd", fill(UI["ACT1"], w=200, t=TXT["A_BACKG"]))):
                ap.append((p_, mk_))
    for k_ in ("STOK", "FSP", "REFRESH"):
        ap.append(("SkyyRkFoot", UI[k_]))
    SUI.check_page(ap, RK_PREFIX)
    SUI.assert_proven(ap, what="SkyyRanks 0.1.2 " + view)
    SUI.check_sky_paths(ap, tab_icons=True)
    return SUI.assert_menu_page(ap, SH, what="SkyyRanks 0.1.2 " + view, sets=sets)


for v_ in ("ranks", "settings", "player", "confirm"):
    _i = rk_preview(v_)
    assert _i["rows"] == 2 and _i["subs"] == 1, (v_, _i)
print("0.1.2 MENU PATTERN: the ranks editor on the kit 1.7 hub_page %dx%d (Settings hub, Server Setup selected), content %dx%d, list %d / %d px "
      "(rows %s / %s), sub row %s - checked: ranks, settings, player, confirm" % (SUI.HUB_PAGE_W, SUI.HUB_PAGE_H, IW, CH, LIST_H, LISTX_H, HS, HSX,
                                                                                    " | ".join(SUBS)))

ui = mk("RankUI")
for k_, v_ in UI.items():
    F(ui, "public static final String %s = %s;" % (k_, jlit(v_)))
for k_, v_ in TXT.items():
    F(ui, "public static final String %s = %s;" % (k_, jlit(v_)))
F(ui, "public static final int[] HS = new int[] { %s };" % ", ".join(str(x) for x in HS))       # 0.1.2: the grow tiers (rule 7)
F(ui, "public static final int[] HSX = new int[] { %s };" % ", ".join(str(x) for x in HSX))
F(ui, "public static final int LIST_IN = %d;" % LIST_IN)
F(ui, "public static final int LISTX_IN = %d;" % LISTX_IN)
F(ui, "public static final int CAP = %d;" % CAP)
M(ui, r"""public static String r(String t, int r) { return t.replace("%R", String.valueOf(r)); }""")
M(ui, r"""public static String w(String t, int w) { return t.replace("%W", String.valueOf(w)); }""")
'''
P.rep(OLD_UI, NEW_UI)

# ---------- HubBar (kit 1.7: page17 / subTab / growSize / route) - before RankPage, which calls it
P.rep('''# ================= RankPage: the big ranks editor (inline; guard() first in build() and handleDataEvent()) =================\n''',
      '''# ================= HubBar: the kit's hub bar class in this jar (0.1.2: kit 1.7 - page17 / subTab / growSize / route) =================
hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True, page=True)

# ================= RankPage: the big ranks editor (inline; HubBar.route, then guard() first in build() and handleDataEvent()) =================\n''')

# ---------- RankPage: state (row height of the grow tier, the Show more cap)
P.rep('''          "public boolean setupCmd;", "public java.util.ArrayList hits;", "public String[] fkeys;", "public String[] fids;"):''',
      '''          "public boolean setupCmd;", "public java.util.ArrayList hits;", "public String[] fkeys;", "public String[] fids;",
          "public int rowH;", "public int cap;"):       # 0.1.2: the list rows' grow tier height, the rows a list draws (Show more)''')
P.rep('''  this.setupCmd = false;\n  try { this.setupCmd''', '''  this.setupCmd = false;\n  this.rowH = 66; this.cap = @PKG@.RankUI.CAP;\n  try { this.setupCmd''')
P.rep('''public void clearDrafts() { this.d0 = ""; this.d1 = ""; this.i0 = ""; this.i1 = ""; this.i2 = ""; }''',
      '''public void clearDrafts() { this.d0 = ""; this.d1 = ""; this.i0 = ""; this.i1 = ""; this.i2 = ""; this.cap = @PKG@.RankUI.CAP; }''')
# no pages any more: one scroll list (pages = the list's length; the head says when only the first rows are drawn)
P.rep('''public void setPages(int n) {
  this.pages = n <= 7 ? 1 : (n + 6) / 7;
  if (this.pageNo >= this.pages) this.pageNo = this.pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
}""")
M(page, r"""
public String pageText() { return this.pages > 1 ? "   -   page " + (this.pageNo + 1) + " of " + this.pages : ""; }""")''',
      '''public void setPages(int n) {
  this.pages = n;
  this.pageNo = 0;
}""")
M(page, r"""
public String pageText() { return this.pages > this.cap ? "   -   the first " + this.cap + " shown" : ""; }""")
# 0.1.2 Skyy rule 7: few rows grow - the biggest tier (HubBar.growSize) whose n rows all fit the list; else 66 px rows and the list scrolls
M(page, r"""
public void grow(int n, boolean add) {
  int[] hs = add ? @PKG@.RankUI.HS : @PKG@.RankUI.HSX;
  this.rowH = hs[@PKG@.HubBar.growSize(Math.min(n, this.cap), add ? @PKG@.RankUI.LIST_IN : @PKG@.RankUI.LISTX_IN, hs, 6)];
}""")''')
P.rep('''  b.appendInline("#SkyyRkRows", @PKG@.RankUI.r(@PKG@.RankUI.ROW, r));''',
      '''  b.appendInline("#SkyyRkRows", @PKG@.RankUI.r(@PKG@.RankUI.ROW, r).replace("%H", String.valueOf(this.rowH)).replace("%Q", String.valueOf((this.rowH - 42) / 2)));''')
# the Show more row (a list longer than the cap; + 200 per click)
P.rep('''M(page, r"""
public void addRow(@UCB@ b, String label) {''', '''M(page, r"""
public void more(@UCB@ b, @UEB@ ev, int n) {
  if (n <= this.cap) return;
  b.appendInline("#SkyyRkRows", @PKG@.RankUI.MOREROW);
  b.appendInline("#SkyyRkMoreRow", @PKG@.RankUI.MORESP);
  b.appendInline("#SkyyRkMoreRow", @PKG@.RankUI.MORE);
  bind(ev, "SkyyRkMore", "more");
}""")
M(page, r"""
public void addRow(@UCB@ b, String label) {''')
# the sub-tab row (was the 190 x 40 tab strip): [RANKS][PLAYERS] (+ the open rank's [SETTINGS][GRANTS][MEMBERS] or the open [PLAYER])
P.rep(cut('''M(page, r"""
public void tab(@UCB@ b, @UEB@ ev, int i, boolean sel) {''', '''    tab(b, ev, 4, this.sub == 2);
  }
}""")'''), '''M(page, r"""
public void tab(@UCB@ b, @UEB@ ev, int i, String label, boolean sel) {
  @PKG@.HubBar.subTab(b, ev, "SkyyRk", i, label, sel, sel ? null : "tab" + i, 150);
}""")
M(page, r"""
public void buildTabs(@UCB@ b, @UEB@ ev) {
  boolean rk = this.view.equals("rank");
  tab(b, ev, 0, "Ranks", this.view.equals("ranks"));
  tab(b, ev, 1, "Players", this.view.equals("players"));
  if (rk) {
    b.appendInline("#SkyyRkSub", @PKG@.RankUI.SP48);
    tab(b, ev, 2, "Settings", this.sub == 0);
    tab(b, ev, 3, "Grants", this.sub == 1);
    tab(b, ev, 4, "Members", this.sub == 2);
  } else if (this.view.equals("player")) {
    b.appendInline("#SkyyRkSub", @PKG@.RankUI.SP48);
    @PKG@.HubBar.subTab(b, ev, "SkyyRk", 2, "Player", true, null, 150);
  }
}""")''')
# the result line + Refresh = the hub page footer (Prev / Next, < Server Setup and Close are gone: the scroll lists, row 2, the X)
P.rep('''  b.appendInline("#SkyyRkBody", t);
  b.set("#SkyyRkStatus.Text", @PKG@.RankCfg.textOf(s));''', '''  b.appendInline("#SkyyRkFoot", t);
  b.set("#SkyyRkStatus.Text", @PKG@.RankCfg.textOf(s));''')
P.rep(cut('''public void buildFoot(@UCB@ b, @UEB@ ev, boolean paging) {''', '''  b.appendInline("#SkyyRkFoot", @PKG@.RankUI.CLOSE); bind(ev, "SkyyRkClose", "close");
}"""'''), '''public void buildFoot(@UCB@ b, @UEB@ ev, boolean paging) {
  if (!this.locked) {
    b.appendInline("#SkyyRkFoot", @PKG@.RankUI.FSP);
    b.appendInline("#SkyyRkFoot", @PKG@.RankUI.REFRESH); bind(ev, "SkyyRkRefresh", "refresh");
  }
}"""''')
# ---- the views: no title text (the title bar says Settings - the hub), one scroll list each, few rows grow
P.rep('''  b.set("#SkyyRkTitle.Text", "Ranks");
  b.set("#SkyyRkHint.Text", "Each rank also gets''', '''  b.set("#SkyyRkHint.Text", "Each rank also gets''')
P.rep('''  setPages(n);
  b.set("#SkyyRkHead.Text", "Ranks   -   " + n + "   -   highest first" + pageText());''',
      '''  setPages(n);
  grow(n, true);
  b.set("#SkyyRkHead.Text", "Ranks   -   " + n + "   -   highest first" + pageText());''')
assert P.s.count('''  int from = this.pageNo * 7;\n  int to = Math.min(n, from + 7);\n''') == 4
for _k in range(4):
    _i = P.s.index('''  int from = this.pageNo * 7;\n  int to = Math.min(n, from + 7);\n''')
    P.rep(P.s[_i - 120:_i] + '''  int from = this.pageNo * 7;\n  int to = Math.min(n, from + 7);\n''',
          P.s[_i - 120:_i] + '''  int from = 0;\n  int to = Math.min(n, this.cap);\n''')
P.rep('''  if (n == 0) empty(b, "No ranks - ranks.properties could not be read.");''',
      '''  more(b, ev, n);
  if (n == 0) empty(b, "No ranks - ranks.properties could not be read.");''')
# Settings: 7 fixed rows in the taller list (no add row)
P.rep('''  b.set("#SkyyRkHead.Text", rk.name + "   -   settings");
  b.appendInline("#SkyyRkBody", @PKG@.RankUI.ROWS);''', '''  b.set("#SkyyRkHead.Text", rk.name + "   -   settings");
  grow(7, false);
  b.appendInline("#SkyyRkBody", @PKG@.RankUI.ROWSX);''')
# Grants
P.rep('''  int n = items.size();
  setPages(n);
  if (this.mode == 1) b.set("#SkyyRkHead.Text", "Search''', '''  int n = items.size();
  setPages(n);
  grow(n, true);
  if (this.mode == 1) b.set("#SkyyRkHead.Text", "Search''')
P.rep('''  if (n == 0) empty(b, this.mode == 1 ? "No registered node matches.''', '''  more(b, ev, n);
  if (n == 0) empty(b, this.mode == 1 ? "No registered node matches.''')
# Members (the default rank: no list rows, no add row -> the taller list)
P.rep('''  boolean isDef = rk.id.equals(@PKG@.RankStore.defaultId());
  b.appendInline("#SkyyRkBody", @PKG@.RankUI.ROWS);
  if (isDef) {''', '''  boolean isDef = rk.id.equals(@PKG@.RankStore.defaultId());
  b.appendInline("#SkyyRkBody", isDef ? @PKG@.RankUI.ROWSX : @PKG@.RankUI.ROWS);
  if (isDef) {''')
P.rep('''  int n = items.size();
  setPages(n);
  b.set("#SkyyRkHead.Text", this.mode == 1 ? "Online players''', '''  int n = items.size();
  setPages(n);
  grow(n, true);
  b.set("#SkyyRkHead.Text", this.mode == 1 ? "Online players''')
P.rep('''  if (n == 0) empty(b, this.mode == 1 ? "Nobody is online."''', '''  more(b, ev, n);
  if (n == 0) empty(b, this.mode == 1 ? "Nobody is online."''')
# Players
P.rep('''  b.set("#SkyyRkTitle.Text", "Ranks - Players");\n  b.set("#SkyyRkHint.Text", "Open a player''', '''  b.set("#SkyyRkHint.Text", "Open a player''')
P.rep('''  int n = items.size();
  setPages(n);
  b.set("#SkyyRkHead.Text", "Players   -   "''', '''  int n = items.size();
  setPages(n);
  grow(n, true);
  b.set("#SkyyRkHead.Text", "Players   -   "''')
P.rep('''  if (n == 0) empty(b, f.length() > 0 ? "No player matches "''', '''  more(b, ev, n);
  if (n == 0) empty(b, f.length() > 0 ? "No player matches "''')
# One player: the picker row, the groups row, then every deny (or search hit) in the same list
P.rep('''  b.set("#SkyyRkTitle.Text", "Player - " + this.targetName);\n  b.set("#SkyyRkHint.Text", "A personal deny''', '''  b.set("#SkyyRkHint.Text", "A personal deny''')
P.rep('''  int n = d.length;
  this.pages = n <= 5 ? 1 : (n + 4) / 5;
  if (this.pageNo >= this.pages) this.pageNo = this.pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;''', '''  int n = d.length;
  setPages(n);
  grow(2 + Math.max(1, n), true);''')
P.rep('''  int from = this.pageNo * 5;
  int to = Math.min(n, from + 5);
  for (int i = from; i < to; i++) {
    int ri = i - from + 2;''', '''  int from = 0;
  int to = Math.min(n, this.cap);
  for (int i = from; i < to; i++) {
    int ri = i - from + 2;''')
P.rep('''  if (n == 0) {
    rowStart(b, 2, @PKG@.RankUI.TXTC);''', '''  more(b, ev, n);
  if (n == 0) {
    rowStart(b, 2, @PKG@.RankUI.TXTC);''')
# Confirm: an in-page view of the hub page (rows 1 + 2 above it), no title text
P.rep('''  b.set("#SkyyRkTitle.Text", "Please confirm");
  b.set("#SkyyRkHint.Text", "Nothing has changed yet.");''', '''  b.set("#SkyyRkHint.Text", "Please confirm - nothing has changed yet.");''')
# build(): the hub page shell + HubBar.page17 (row 1, row 2 with Server Setup selected, the X) instead of the 0.1.1 window
P.rep('''  b.appendInline((String) null, @PKG@.RankUI.ROOT);
  b.appendInline("#SkyyRk", @PKG@.RankUI.BAR);
  b.appendInline("#SkyyRkBar", @PKG@.RankUI.DECOT);
  b.appendInline("#SkyyRkBar", @PKG@.RankUI.TITLE);
  b.appendInline("#SkyyRk", @PKG@.RankUI.BODY);
  b.appendInline("#SkyyRk", @PKG@.RankUI.DECOB);
  b.appendInline("#SkyyRkBody", @PKG@.RankUI.HINT);
  if (!ok) {
    b.set("#SkyyRkTitle.Text", "Ranks");
    b.set("#SkyyRkHint.Text", "");''', '''""" + RK_SHELL_JAVA + "\\n  " + RK_PAGE17 + r"""
  b.appendInline("#SkyyRkBody", @PKG@.RankUI.HINT);
  if (!ok) {
    b.set("#SkyyRkHint.Text", "");''')
P.rep('''  buildTabs(b, ev);
  b.appendInline("#SkyyRkBody", @PKG@.RankUI.SEP);
  b.appendInline("#SkyyRkBody", @PKG@.RankUI.GAP8);
  b.appendInline("#SkyyRkBody", @PKG@.RankUI.HEAD);''', '''  buildTabs(b, ev);
  b.appendInline("#SkyyRkBody", @PKG@.RankUI.HEAD);''')
P.rep('''    b.set("#SkyyRkTitle.Text", "Rank - " + rk.name);\n    b.set("#SkyyRkHint.Text", rk.id.equals''', '''    b.set("#SkyyRkHint.Text", rk.id.equals''')
P.rep('''    else { this.pages = 1; buildSettings(b, ev, rk); }''', '''    else { setPages(0); buildSettings(b, ev, rk); }''')
# clicks: Show more
P.rep('''  if (a.equals("refresh")) { this.status = ""; return true; }''', '''  if (a.equals("refresh")) { this.status = ""; return true; }
  if (a.equals("more")) { this.cap = this.cap + @PKG@.RankUI.CAP; return true; }''')
# the top rows (HubBar.route): before the access guard, so anyone can leave by them; row 2's Server Setup = the old < Server Setup button
P.rep('''M(page, r"""
public void click(String a) {''', '''M(page, r"""
public void hubClick(@REF@ ref, @ST@ st, String data) {
  String r = null;
  try { r = @PKG@.HubBar.route(this.playerRef, data, "settings", "setup"); } catch (Throwable t) { r = null; }
  if (r == null) return;
  if (r.equals("close")) { closePage(ref, st); return; }
  if (r.equals("self")) { redraw(); return; }
  if (r.equals("back") || r.equals("bridge") || r.equals("command")) return;
  this.status = "-That tab could not open right now - try again.";
  redraw();
}""")
M(page, r"""
public void click(String a) {''')
P.rep('''    if (a.equals("close")) { closePage(ref, st); return; }
    if (!guard()) { redraw(); return; }''', '''    if (a.equals("close")) { closePage(ref, st); return; }
    if (a.equals("hub:setup")) { openSetup(); return; }
    if (a.startsWith("hub:")) { hubClick(ref, st, data); return; }
    if (!guard()) { redraw(); return; }''')

# ---------- the jar: the HubBar class + the kit's Sky Window art (the page names SkyyKit textures -> an asset pack now)
P.rep('''ALL = [cfg, ui, rk, perm, st, sav, eng, dtask, bulk, hk, ops, fmt, cwr, chk, ofn, stt, join, rdy, quit_, page] + CMDS + [pl]''',
      '''ALL = [cfg, ui, rk, perm, st, sav, eng, dtask, bulk, hk, ops, fmt, cwr, chk, ofn, stt, join, rdy, quit_, page, hubb] + CMDS + [pl]''')
P.rep('''man["IncludesAssetPack"] = False
B.assemble(jar, man, OUT)''', '''# 0.1.2: the Sky Window kit art - all 59 files, byte-identical in every hub jar (sha256-pinned by the kit; HUBS-CONTRACT 2.7), under
# Common/UI/Custom/SkyyKit/ only (a texture outside Common/UI/Custom disconnects the client - probe k1b) -> the jar is an asset pack now
_kit_art = SUI.kit_texture_files()
assert len(_kit_art) == len(SUI.SKY_FILES) == 59 and all(p_.startswith("Common/UI/Custom/SkyyKit/") and ".." not in p_ for p_ in _kit_art), "0.1.2: the kit art"
man["IncludesAssetPack"] = True
B.assemble(jar, man, OUT, extra_files=_kit_art)
assert SUI.check_jar_kit(jar, need=("Header", "HeaderOrnament", "Close", SUI.HUB_FRAME.get(RK_HUB, "Frame"), "Row", "Secondary")) == 59, "0.1.2: the jar's kit art"''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count("requirePermission(") == REQ0, \
    "0.1.2 changes no system / command / permission"
assert "#SkyyRkTitle.Text" not in P.s and "RankUI.ROOT" not in P.s and "RankUI.PREV" not in P.s and "RankUI.SETUP" not in P.s \
    and "RankUI.CLOSE" not in P.s and "RankUI.TAB" not in P.s and "VANILLA_CHECK = [" not in P.s
P.finish()
