"""Derive SkyyMenu/build_skyymenu_0.3.28.py from the LIVE SkyyMenu 0.3.27 (python tools/menu_0_3_28_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_27_patch.py -> 0.3.27 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.28. The harness SkyyMenu/test_skyymenu_0.3.28.py is its own file.

0.3.28 (2026-10-15) = HUBS H2 (research/Hubs-Spec.md 1.2 / 2.1-2.4 / 7 + the build table row H2; the kit skyyui 1.5 hub contract
tools/HUBS-CONTRACT.md). Skyy 2026-10-10 (docs/answered/ui.md): picked ALL hubs, "could we tidy and simplify them any more from here?",
"I like 2 the best ... beautiful! can we design it all with the new theme"; 2026-10-15 "And when are we condensing menus together?".
  1. The registry: SkyyMenu installs the kit's HubBar (SUI.install_hub_bar, theme sky) in its own package, puts hub:def:<hub> for the 7
     hubs (SUI.HUB_DEFS: title, command, an icon item of ours) and its OWN 7 tabs (SUI.HUB_TABS rows owned by SkyyMenu, same labels /
     orders): character:stats, world:teleport, social:players, settings:settings, settings:layout, settings:mods (admins, or everyone
     while menu.modsHelp is on), settings:setup (admins). Each tab = an open Function (MenuHubOpen: opens the page for the UUID on the
     world thread) + a visible Function where the tab has a rule (MenuHubVis). All removed in shutdown (HubBar.removeAll + hub:last).
  2. hub:last:<uuid> (memory only): MenuHub.ensure makes it at join / when a hub page draws; MenuQuit + SeenTick + shutdown remove it.
  3. The hub commands /character (/char), /storage, /market, /travel, /social (hytale:Adventurer, HANDOFF section 3): the hub's last tab
     if it is still visible, else its first visible tab; a hub with no tab yet says it is coming soon (Storage / Market until H3).
  4. The pages: each Menu tab page draws in the kit's hub_shell (Sky Window: the hub's Frame mood, Header + HeaderOrnament crest, "< Menu"
     in the title bar, the close X, the shared tab strip filled at runtime by HubBar.build) and keeps its content; only its own title row
     goes (spec 2.4). Stats (1114 x 966: the old body exactly), Settings (1128 x 980: status shown in the hint row, rows 3 px apart),
     Server Setup (1128 x 980: the view title and subtitle share one line), and the menu views Teleport / Players (+ a player) / Mods /
     the layout editor (804 x 980: status in the hint row, 8 info lines). The SkyWynn Menu's main view is unchanged (H8 later).
     Tab clicks: the page's own tab = redraw, "< Menu" = the SkyWynn Menu, the X = close, a Menu-owned tab of the same MenuPage = switched
     in place, any other tab = its open Function (or its command). Tab labels: 16 px, ShrinkTextToFit down to 12 (kit).
  5. The jar ships the kit's 59 Sky Window files (SUI.kit_texture_files: Common/UI/Custom/SkyyKit/, sha256-pinned, never a ../ path).
  6. Review fixes (2026-10-15): a hub click disarms Settings' Reset all; the own tab of Settings (nothing to clear) and of Server Setup
     draws nothing (the bar's click carries no field values - a redraw dropped typed text); Server Setup's one-line title drops the
     "Server Setup - " prefix and is cut at 140 characters (measured); "the Void" (bags.md LOCKED) in the new Storage texts; the layout
     editor's first status ends "Done to finish." (it replaces the hint row in the hub shell).
Saved data: none. ROUND_PINS = {}. Rollback to 0.3.27: safe (the hub keys are memory only; old pages come back).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.27.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.28.py")
CR, LF = chr(13), chr(10)
raw = open(src, encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.27"' in s and "0.3.27: THE SHARDS TILE GOES" in s and "0.3.28" not in s, "not the generated 0.3.27 script"
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    assert new, "a change never deletes outright (the undo check needs the new text)"
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


def block(start, end):
    """the unique text from `start` up to and including `end` (both must be unique, in that order)"""
    assert s.count(start) == 1, "block start count %d: %s" % (s.count(start), start[:120])
    i = s.index(start)
    j = s.index(end, i)
    assert s.count(end) >= 1
    return s[i:j + len(end)]


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.27: THE SHARDS TILE GOES''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.28: HUBS H2 (notes: tools/menu_0_3_28_patch.py; research/Hubs-Spec.md 1.2 / 2 / 7; kit skyyui 1.5 tools/HUBS-CONTRACT.md; Skyy
       2026-10-10 picked ALL hubs + "can we design it all with the new theme"): the kit's HubBar in this jar; hub:def:<hub> for the 7
       hubs; SkyyMenu's own tabs (character:stats, world:teleport, social:players, settings:settings / layout / mods / setup) with open
       (+ visible) Functions; hub:last:<uuid> in memory (removed on disconnect); /character (/char), /storage, /market, /travel, /social
       open the hub's last / first tab (coming soon while a hub has none); Stats, Settings, Server Setup and the menu's Teleport /
       Players / Mods / layout-editor views draw in the Sky Window hub shell with the shared tab bar (only their title row goes); the
       main menu view is unchanged; the 59 kit textures ship under Common/UI/Custom/SkyyKit/. No saved data. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.28.py.
0.3.27: THE SHARDS TILE GOES''')
rep('VERSION = "0.3.27"\n', 'VERSION = "0.3.28"\n')
rep('''                  "/stats (or /profilestats) - all your stats on one page",
''', '''                  "/stats (or /profilestats) - all your stats on one page",
                  "/character (/char), /travel, /social, /storage, /market - open a hub",   # 0.3.28
''')

# ---------------------------------------------------------------------------------------------------------------- hub data (MENU DATA)
rep('''# ================= build-time checks: icons exist, text is safe, slots are sane =================
''', r'''# ---- 0.3.28: HUBS H2 (research/Hubs-Spec.md 1.2 + 2.1-2.4; the contract tables live in tools/skyyui.py kit 1.5: HUBS, HUB_DEFS, HUB_TABS)
# SkyyMenu's OWN tabs = the HUB_TABS rows whose owner is SkyyMenu (same hub, tab id, order, label, fallback command - None = no command)
HUB_OWN = [(h, t, o, l, c) for h, t, o, m, l, c in SUI.HUB_TABS if m == "SkyyMenu"]
assert [(h, t) for h, t, _o, _l, _c in HUB_OWN] == [("character", "stats"), ("world", "teleport"), ("social", "players"), ("settings", "settings"),
                                                  ("settings", "layout"), ("settings", "mods"), ("settings", "setup")], "0.3.28: Menu's 7 tabs (spec 1.2)"
HUB_OWN_VIS = ("mods", "setup")      # the tabs with a visible Function: mods = admins or everyone while menu.modsHelp is on; setup = admins
# hub:def:<hub> = {title, command, icon item}: the icon is one of OUR tile icon items (the SkyWynn Menu's art/menu-icons set)
HUB_ICON_ITEM = {"character": "Skyy_Menu_Icon_YourProfile", "storage": "Skyy_Menu_Icon_PocketDimension", "market": "Skyy_Menu_Icon_Bazaar",
                 "smithing": "Skyy_Menu_Icon_Reforge", "world": "Skyy_Menu_Icon_Teleport", "social": "Skyy_Menu_Icon_Players",
                 "settings": "Skyy_Menu_Icon_Settings"}
assert sorted(HUB_ICON_ITEM) == sorted(SUI.HUBS) and all(v in ICON_ITEMS for v in HUB_ICON_ITEM.values()), "0.3.28: every hub has our icon item"
# the chat line of a hub command while the hub has no tab yet (the other mods add theirs in the H3 rounds)
HUB_SOON = {"character": "The Character hub has no pages yet - coming soon.",
            "storage": "The Storage hub is coming soon. For now: /sacks (the Void), /vault and /bank.",
            "market": "The Market hub is coming soon. For now: /bz (Bazaar) and /ah (Auction House).",
            "smithing": "The Smithing hub is coming soon. For now: /craft, /reforge and /identify.",
            "world": "The World hub has no pages yet - coming soon.",
            "social": "The Social hub has no pages yet - coming soon.",
            "settings": "The Settings hub has no pages yet - coming soon."}
assert sorted(HUB_SOON) == sorted(SUI.HUBS)
# the hub commands SkyyMenu registers (spec 2.3; /smithing stays SkyyGear's, /settings is Menu's own page already): word, aliases, hub
HUB_CMDS = [("character", ("char",), "character"), ("storage", (), "storage"), ("market", (), "market"), ("travel", (), "world"),
            ("social", (), "social")]
assert all(SUI.HUB_DEFS[h][1] == w for w, _a, h in HUB_CMDS), "0.3.28: each hub command is the contract's command (SUI.HUB_DEFS)"
HUB_INFO_LINES = 8                   # the menu views in the hub shell: 8 info lines (the 980 px page; the main view keeps 9)
HUB_TXT_FAIL = "That tab could not open right now - try again."
ADM_SUBMAX = 140                     # Server Setup in the hub shell: "<view title>   -   <subtitle>" on one line, cut at 140 characters
                                     # (measured: ~1020 px of the 1080 px line at 16 px bold - the check below)
ADM_PREFIX = "Server Setup - "       # dropped from the view title in the hub shell (the active tab already says Server Setup)
assert all(len(HUB_SOON[_h]) <= 100 for _h in SUI.HUBS), "0.3.28: the coming-soon lines stay short"

# ================= build-time checks: icons exist, text is safe, slots are sane =================
''')

# the hub command words: free in every other Skyy build script and no vanilla command class is named after one
rep('''print("server setup command: /%s /%s (free)" % (ADMIN_CMD, ADMIN_ALIAS))
''', r'''print("server setup command: /%s /%s (free)" % (ADMIN_CMD, ADMIN_ALIAS))
# 0.3.28: the hub commands (spec 2.3) - no other Skyy build script takes one of the words as a root command or alias, no vanilla command
# class is named after one (best effort; the plugin also logs a clash when it registers them and still loads)
HUB_WORDS = [w for w, _a, _h in HUB_CMDS] + [a for _w, al, _h in HUB_CMDS for a in al]
HUB_TAKEN = []
for p in glob.glob(os.path.join(B.PROJECT, "*", "build_*.py")):
    if os.path.basename(os.path.dirname(p)) == "SkyyMenu":
        continue
    t = open(p, encoding="utf-8", errors="ignore").read()
    for w in HUB_WORDS:
        if takes_root(t, w):
            HUB_TAKEN.append((w, os.path.relpath(p, B.PROJECT)))
assert not HUB_TAKEN, "0.3.28: a hub command word is taken elsewhere: %s" % HUB_TAKEN
with zipfile.ZipFile(B.SERVER_JAR) as zj:
    _vh = [n for n in zj.namelist() if n.endswith("Command.class") and n.rsplit("/", 1)[-1][:-len("Command.class")].lower() in HUB_WORDS]
assert not _vh, "0.3.28: the vanilla jar has a command class named after a hub word: %s" % _vh
print("hub commands: %s (free)" % ", ".join("/" + w for w in HUB_WORDS))
''')

# ---------------------------------------------------------------------------------------------------------------- menu views: UI strings
rep('''    "BTNCLOSE": 'TextButton #SkyyMClose { Anchor: (Width: 168, Height: 40); Text: "Close"; ' + BS + " }",
}''', '''    "BTNCLOSE": 'TextButton #SkyyMClose { Anchor: (Width: 168, Height: 40); Text: "Close"; ' + BS + " }",
    # 0.3.28: the menu views in the hub shell (Teleport / Players / Mods / the layout editor): the status shows IN the hint row (same id,
    # the STATUS look) and the info box is 256 high (8 lines) - the shell's title bar + tab strip replace the accent + title row
    "HINTST":   'Label #SkyyMHint { Anchor: (Height: 22); Text: ""; Style: (FontSize: 15, RenderBold: true, TextColor: #ffd27f, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "INFOBOXH": "Group #SkyyMInfoBox { Anchor: (Height: 256); Background: #142030(0.9); Padding: (Horizontal: 14, Vertical: 8); LayoutMode: Top; }",
}''')
rep('''assert 26 + 42 + 20 * INFO_LINES + 16 <= 266, 'info box too small for its lines'
''', '''assert 26 + 42 + 20 * INFO_LINES + 16 <= 266, 'info box too small for its lines'
assert 26 + 42 + 20 * HUB_INFO_LINES + 16 <= 256 < 26 + 42 + 20 * (HUB_INFO_LINES + 1) + 16 and HUB_INFO_LINES <= INFO_LINES, '0.3.28: the hub info box holds its 8 lines'
''')

# ---------------------------------------------------------------------------------------------------------------- Settings page block
_sb = block('SPW, SPH = 1120, 980            # 0.3.25: 930 -> 980 (the search row)\n',
            'assert 25 + 150 + 150 + 300 + 220 + 170 + 4 * 10 <= SPW - 40 and 185 + 300 + 220 + 170 + 2 * 10 <= SPW - 40, "the settings footer is wider than the page"\n')
_nb = _sb
for _a, _b, _n in (
        ('SPW, SPH = 1120, 980            # 0.3.25: 930 -> 980 (the search row)\n',
         'SPW, SPH = 1128, 980            # 0.3.28: the hub shell (1080 inside + the sky padding 2 x 24); 0.3.25: 930 -> 980 (the search row)\n'
         'SPI = SPW - 2 * 24              # 0.3.28: the width inside the hub shell (= 0.3.27\'s 1120 - 2 x 20)\n', 1),
        ('SPW - 40', 'SPI', None),
        ('''    "SROOT":     "Group #SkyyStg { Anchor: (Width: %d, Height: %d); Background: #0b1524(0.96); Padding: (Horizontal: 20, Vertical: 14); LayoutMode: Top; }" % (SPW, SPH),
    "SACCENT":   "Group { Anchor: (Height: 3); Background: #e0b060; }",
    "STITLE":    'Label #SkyyStgTitle { Anchor: (Height: 48); Text: "Settings"; Style: (FontSize: 28, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }',
''', '''    # 0.3.28: the page root, accent and title row are the kit's hub shell now (STG_HUB_SH below: root SkyyStgH, body = #SkyyStg)
''', 1),
        ('''    "SGAP6":     "Group { Anchor: (Height: 6); }",
''', '''    "SGAP3":     "Group { Anchor: (Height: 3); }",      # 0.3.28: rows 3 px apart (was 6) - the hub tab strip needs the room
''', 1),
        ('''    "SROWS":     "Group #SkyyStgRows { Anchor: (Height: %d); LayoutMode: Top; }" % (SET_ROWS * 67),     # 0.3.1: rows 61 + gap 6
''', '''    "SROWS":     "Group #SkyyStgRows { Anchor: (Height: %d); LayoutMode: Top; }" % (SET_ROWS * 64),     # 0.3.28: rows 61 + gap 3
''', 1),
        ('''    "SSTATUS":   'Label #SkyyStgStatus { Anchor: (Height: 30); Text: ""; Style: (FontSize: 17, RenderBold: true, TextColor: #ffd27f, HorizontalAlignment: Center, VerticalAlignment: Center); }',
''', '''    # 0.3.28: the status shows IN the hint row (same id #SkyyStgHint, the old status look) - no separate status row in the hub shell
    "SHINTST":   'Label #SkyyStgHint { Anchor: (Height: 26); Text: ""; Style: (FontSize: 17, RenderBold: true, TextColor: #ffd27f, HorizontalAlignment: Center, VerticalAlignment: Center); }',
''', 1),
        ('''assert "Width" in UI_S["SROOT"] and "Top:" not in UI_S["SROOT"].split("Anchor: (")[1].split(")")[0], "settings root anchor must be Width/Height only"
''', '''# 0.3.28: the root is the kit's hub shell (its root anchor is checked by the kit: Width / Height only)
''', 1),
        ('''_stall = 2 * 14 + 3 + 48 + 26 + SFIND_H + 58 + 58 + 8 + 40 + SET_ROWS * 67 + 26 + 30 + 62   # 0.3.25: + the search row
''', '''_stall = SUI.TITLE_H + 2 * 24 + SUI.HUB_BAR_H + 26 + SFIND_H + 58 + 58 + 8 + 40 + SET_ROWS * 64 + 26 + 62   # 0.3.28: the hub shell
''', 1)):
    assert _nb.count(_a) == (_n if _n is not None else _nb.count(_a)) and _a in _nb, ("settings block", _a[:80], _nb.count(_a))
    _nb = _nb.replace(_a, _b)
assert "SPW - 40" not in _nb and _nb.count("SPI") >= 8
rep(_sb, _nb)

# ---------------------------------------------------------------------------------------------------------------- Server Setup block
_ab = block('APW, APH = 1120, 930\n', 'assert 2 * 14 + 3 + 48 + 26 + A_BODY + 30 + 62 == APH and APH <= 1080 - 100, "the server setup page must fit a 1080 px high screen"\n')
_nb = _ab
for _a, _b in (
        ('APW, APH = 1120, 930\n', 'APW, APH = 1128, 980                                 # 0.3.28: the hub shell (1080 inside + the sky padding 2 x 24)\n'),
        ('A_INNER = APW - 40                                   # 1080: the root has Horizontal padding 20\n',
         'A_INNER = APW - 2 * 24                               # 1080: the hub shell body has padding 24 (0.3.27: 1120 - 2 x 20)\n'),
        ('A_BODY = APH - 2 * 14 - 3 - 48 - 26 - 30 - 62        # 733: accent, title, subtitle, (body), status, footer\n',
         'A_BODY = APH - SUI.TITLE_H - 2 * 24 - SUI.HUB_BAR_H - 26 - 30 - 62   # 0.3.28: 724 = title bar, padding, tab strip, title line, (body), status, footer\n'),
        ('''    "AROOT":    "Group #SkyyAdm { Anchor: (Width: %d, Height: %d); Background: #0b1524(0.96); Padding: (Horizontal: 20, Vertical: 14); LayoutMode: Top; }" % (APW, APH),
    "AACCENT":  "Group { Anchor: (Height: 3); Background: #e0b060; }",
    "ATITLE":   _TXT("SkyyAdmTitle", 48, 28, "#ffe9c9", True, True),
    "ASUB":     _TXT("SkyyAdmSub", 26, 16, "#9fb8cc", False, True),
''', '''    # 0.3.28: the page root, accent and title row are the kit's hub shell now (ADM_HUB_SH below: root SkyyAdmH, body = #SkyyAdm); the
    # view's title and subtitle share ONE line ("<title>   -   <subtitle>", cut at ADM_SUBMAX characters)
    "ASUB":     _TXT("SkyyAdmSub", 26, 16, "#ffe9c9", True, True),
'''),
        ('''assert "Width" in UI_A["AROOT"] and "Top:" not in UI_A["AROOT"].split("Anchor: (")[1].split(")")[0], "server setup root anchor must be Width/Height only"
''', '''# 0.3.28: the root is the kit's hub shell (its root anchor is checked by the kit: Width / Height only)
'''),
        ('assert 2 * 14 + 3 + 48 + 26 + A_BODY + 30 + 62 == APH and APH <= 1080 - 100, "the server setup page must fit a 1080 px high screen"\n',
         'assert SUI.TITLE_H + 2 * 24 + SUI.HUB_BAR_H + 26 + A_BODY + 30 + 62 == APH and APH <= SUI.MAX_PAGE_H, "the server setup page must fit a 1080 px high screen"\n')):
    assert _nb.count(_a) == 1, ("admin block", _a[:80], _nb.count(_a))
    _nb = _nb.replace(_a, _b)
rep(_ab, _nb)

# ---------------------------------------------------------------------------------------------------------------- the Stats page shell
rep('''ST_W, ST_H = 1100, 900               # fits 1080 px with the ornaments (asserted)
''', '''ST_W, ST_H = 1114, 966               # 0.3.28: the hub shell (sky padding 24 + the 52 px tab strip) around 0.3.27's body (1066 x 828)
''')
rep('''    sh = SUI.page_shell("SkyyStatF", ST_W, ST_H, "Your Stats", body_id="SkyyStat")
''', '''    sh = SUI.hub_shell("SkyyStatF", ST_W, ST_H, "character", body_id="SkyyStat")    # 0.3.28: Character > Stats (was page_shell "Your Stats")
    assert (sh.inner_w, sh.inner_h) == (1100 - 2 * SUI.CONTENT_PAD, 900 - SUI.TITLE_H - 2 * SUI.CONTENT_PAD), "0.3.28: the stats body = 0.3.27's"
''')

# ---------------------------------------------------------------------------------------------------------------- the hub shells (after the Stats page)
rep('''print("stats page: %d x %d, %d rows per tab, %d px left in the body, kit %s" % (ST_W, ST_H, ST_ROWS, ST_LEFT, SUI_KIT_ID))
''', r'''print("stats page: %d x %d, %d rows per tab, %d px left in the body, kit %s" % (ST_W, ST_H, ST_ROWS, ST_LEFT, SUI_KIT_ID))

# ================= 0.3.28 HUBS H2: the hub page shells (kit skyyui 1.5 hub_shell in the Sky Window theme) =================
# Every Menu tab page draws in the kit's hub_shell: the hub's Frame mood, the Header title bar with the HeaderOrnament crest and the hub
# title, "< Menu" in the title bar, the close X, the tab strip (#<prefix>HubTabs, filled at runtime by HubBar.build). The OLD page root
# id becomes the shell's body (body_id), so every old appendInline into it still lands in the body; only the old title row is gone.
assert SUI.HUB_THEME == "sky" and SUI.THEME_PAD["sky"] == 24 and SUI.KIT_VERSION == "1.5", "0.3.28: kit skyyui 1.5, hub pages in the sky theme"
HUB_PAD = SUI.THEME_PAD["sky"]
MH_W, MH_H = GW + 2 * HUB_PAD, SUI.MAX_PAGE_H        # the menu views: 804 x 980 (the 756 px grid inside)
MENU_HUB_SH = dict((h, SUI.hub_shell("SkyyMenuH", MH_W, MH_H, h, body_id="SkyyMenu")) for h in ("world", "social", "settings"))
STG_HUB_SH = SUI.hub_shell("SkyyStgH", SPW, SPH, "settings", body_id="SkyyStg")
ADM_HUB_SH = SUI.hub_shell("SkyyAdmH", APW, APH, "settings", body_id="SkyyAdm")
# body budgets: each page's old content (minus its title row) fills the room under the tab strip exactly
for _h, _sh in MENU_HUB_SH.items():
    assert _sh.inner_w == GW and _sh.inner_h == 22 + 256 + 8 + (GH + 6) + 46, "0.3.28: the %s menu view fits its hub shell" % _h
    assert _sh.tabs_w == GW and _sh.parts == SUI.HUB_PART_MENU | SUI.HUB_PART_CLOSE
assert STG_HUB_SH.inner_w == SPI and STG_HUB_SH.inner_h == 26 + SFIND_H + 58 + 58 + 8 + 40 + SET_ROWS * 64 + 26 + 62, "0.3.28: settings fit"
assert ADM_HUB_SH.inner_w == A_INNER and ADM_HUB_SH.inner_h == 26 + A_BODY + 30 + 62, "0.3.28: server setup fits"
# every hub page: the bar-less height + the 52 px bar fits 1080p (assert_hub_page) and the hub's FULL contract tab list fits its strip
# (as if every H3 mod were loaded: assert_hub_fits at the sky minimum 110 px)
HUB_PAGES = [("stats", ST_SH, "character", "stats"), ("teleport", MENU_HUB_SH["world"], "world", "teleport"),
             ("players", MENU_HUB_SH["social"], "social", "players"), ("layout", MENU_HUB_SH["settings"], "settings", "layout"),
             ("mods", MENU_HUB_SH["settings"], "settings", "mods"), ("settings", STG_HUB_SH, "settings", "settings"),
             ("setup", ADM_HUB_SH, "settings", "setup")]
assert sorted(t for t, _s, _h, _m in HUB_PAGES) == sorted(t for _h, t, _o, _l, _c in HUB_OWN), "0.3.28: one hub page per own tab"
HUB_LABEL_FIT = {}
for _t, _sh, _h, _my in HUB_PAGES:
    assert SUI.assert_hub_page(_sh.w, _sh.h - SUI.HUB_BAR_H, old_title_h=0, hub=_h, pad=_sh.pad) == (_sh.w, _sh.h), "0.3.28: %s fits 1080p" % _t
    _tw = SUI.assert_hub_fits(_h, _sh.tabs_w)
    _pp = os.path.commonprefix([_sh.prefix, _sh.body])     # the page's id prefix (shell ids + the old root id = the body)
    SUI.check_page(_sh.appends, _pp)
    SUI.assert_proven(_sh.appends, what="hub shell " + _t)
    _els = SUI.check_sky_paths(_sh.appends)
    assert {"Header", "HeaderOrnament", SUI.HUB_FRAME[_h], "Close", "Tertiary"} <= set(_els), "0.3.28: %s uses the sky kit: %s" % (_t, _els)
    assert any(_sh.prefix + "HubMenu" in mk for _p, mk in _sh.appends if _p == _sh.bar), "0.3.28: < Menu sits in the %s title bar" % _t
    # the bar with every contract tab of the hub (H3) and with Menu's own tabs only (today): valid markup, the active tab selected,
    # every label 16 px or shrunk to 12 px inside its tab
    for _rows in (SUI.hub_tabs(_h), [r for r in SUI.hub_tabs(_h) if r[2] == "SkyyMenu"]):
        _bar = SUI.hub_bar_preview(_sh.prefix, [(t, l, o) for t, o, _m, l, _c in _rows], _my, _sh.tabs_w)
        SUI.check_page(SUI.Appends(list(_sh.appends) + list(_bar)), _pp)
        SUI.check_sky_paths(_bar)
        _btn = [mk for _p, mk in _bar if mk.startswith("TextButton")]
        assert len(_btn) == len(_rows) and sum(1 for mk in _btn if "Tab_Selected" in mk) == 1 and all("ShrinkTextToFit: true" in mk for mk in _btn)
        _w1 = SUI.hub_tab_width(_sh.tabs_w, len(_rows))
        for _r in _rows:
            assert SUI.text_width(_r[3], 12, bold=True) <= _w1 - 2 * SUI.HUB_TAB_PAD, "0.3.28: tab %s fits %d px at 12 px" % (_r[3], _w1)
    HUB_LABEL_FIT[_t] = _tw
MH_JAVA = dict((h, MENU_HUB_SH[h].java("b")) for h in MENU_HUB_SH)
STG_HUB_JAVA = STG_HUB_SH.java("b")
ADM_HUB_JAVA = ADM_HUB_SH.java("b")
ST_HUB_JAVA = SUI.java_hub_build(ST_SH, "stats", cls="@PKG@.HubBar")
STG_HUB_BUILD = SUI.java_hub_build(STG_HUB_SH, "settings", cls="@PKG@.HubBar", uuid="u")
ADM_HUB_BUILD = SUI.java_hub_build(ADM_HUB_SH, "setup", cls="@PKG@.HubBar", uuid="me()")
MH_BUILD = '@PKG@.HubBar.build(b, ev, "SkyyMenuH", hubName(), hubTab(), %d, this.playerRef.getUuid(), %d);' % (GW, SUI.HUB_PART_MENU | SUI.HUB_PART_CLOSE)
assert "SkyyStatF" in ST_HUB_JAVA and '"character", "stats", 1066,' in ST_HUB_JAVA and ST_HUB_JAVA.endswith(", 3);")
# Server Setup: the one-line title (AdminPage.frame: the "Server Setup - " prefix dropped, "<title>   -   <subtitle>", MenuUtil.clip at
# ADM_SUBMAX). The real worst cases (a 24-character config TITLE - skyycfg's limit -, the longest mod id of the SET, a long version, the
# longest subtitles: View only / not running / saved / no page) show WHOLE and fit the 1080 px line; the longer fixed lines (History,
# Export) fit once cut. A_INNER at 16 px bold, the kit's own glyph widths.
def adm_line(t, s):
    if t.startswith(ADM_PREFIX):
        t = t[len(ADM_PREFIX):]
    j = t if not s else t + "   -   " + s
    return j if len(j) <= ADM_SUBMAX else j[:ADM_SUBMAX - 3] + "..."
_am = max([_m["mod"] for _m in MODS] + ["SkyyAbilityProbe"], key=len)     # the longest mod id the Mods list knows (16+ characters)
_at, _av = "Accessories and Talisman", "0.10.12"
assert len(_at) == 24
_whole = [("Server Setup - %s (%s %s)" % (_at, _am, _av), "View only - changing %s needs %s.admin." % (_am, _am.lower())),
          ("Server Setup - %s (%s %s)" % (_at, _am, _av), "%s is not running - its settings cannot be changed now." % _am),
          ("Server Setup - %s (%s %s)" % (_at, _am, _av), "Saved to config.properties - changes are written at once."),
          ("Server Setup - %s %s" % (_am, _av), "This version has no Server Setup page yet - edit its file, then reload it."),
          ("Server Setup - Changes", "Every change made in game, by command or by hand, newest first. Undo puts one value back."),
          ("Export / Import - %s (%s)" % (_at, _am), "A code copies this setup to another world. It never holds player data.")]
_cutok = [("History - config.properties (%s)" % _am,
           "Each config file keeps its newest versions. Preview one, then Restore it - a restore can be undone the same way.")]
for _t, _s in _whole + _cutok:
    _ln = adm_line(_t, _s)
    assert not _ln.startswith(ADM_PREFIX), "0.3.28: the Server Setup prefix stays off the line: " + _ln
    assert SUI.text_width(_ln, 16, bold=True) <= A_INNER - 40, "0.3.28: the Server Setup title line is too wide: %s (%d px)" % (_ln, SUI.text_width(_ln, 16, bold=True))
    assert (_t, _s) in _cutok or not _ln.endswith("..."), "0.3.28: a real Server Setup title line was cut: " + _ln
ADM_LINE_MAX = max(SUI.text_width(adm_line(_t, _s), 16, bold=True) for _t, _s in _whole + _cutok)
print("hub pages (kit %s, sky): %s; menu views %d x %d, settings %d x %d, server setup %d x %d (title line <= %d of %d px), stats %d x %d" % (
    SUI.kit_id(), ", ".join("%s %s:%s %d px tabs" % (t, h, m, HUB_LABEL_FIT[t]) for t, _s, h, m in HUB_PAGES), MH_W, MH_H, SPW, SPH, APW, APH,
    ADM_LINE_MAX, A_INNER, ST_W, ST_H))
''')

# ---------------------------------------------------------------------------------------------------------------- MenuData: the hub tables
rep('''for _n, _v in UI_AARR.items():
    F(dat, "public static final String[] UI_%s = %s;" % (_n, jarr(_v)))
''', '''for _n, _v in UI_AARR.items():
    F(dat, "public static final String[] UI_%s = %s;" % (_n, jarr(_v)))
# 0.3.28: hubs H2 - the 7 hubs (SUI.HUBS order: hub:def:<hub> = {title, command, icon}), the "coming soon" lines, SkyyMenu's own tabs
F(dat, "public static final int HUB_INFO_LINES = %d;" % HUB_INFO_LINES)
F(dat, "public static final String HUB_TXT_FAIL = %s;" % jstr(HUB_TXT_FAIL))
F(dat, "public static final int ADM_SUBMAX = %d;" % ADM_SUBMAX)
F(dat, "public static final String ADM_PREFIX = %s;" % jstr(ADM_PREFIX))
F(dat, "public static final String[] HUB_ID = %s;" % jarr(list(SUI.HUBS)))
F(dat, "public static final String[] HUB_TITLE = %s;" % jarr([SUI.HUB_DEFS[_h][0] for _h in SUI.HUBS]))
F(dat, "public static final String[] HUB_CMD = %s;" % jarr([SUI.HUB_DEFS[_h][1] for _h in SUI.HUBS]))
F(dat, "public static final String[] HUB_ICON = %s;" % jarr([HUB_ICON_ITEM[_h] for _h in SUI.HUBS]))
F(dat, "public static final String[] HUB_SOON = %s;" % jarr([HUB_SOON[_h] for _h in SUI.HUBS]))
F(dat, "public static final String[] HT_HUB = %s;" % jarr([r[0] for r in HUB_OWN]))
F(dat, "public static final String[] HT_TAB = %s;" % jarr([r[1] for r in HUB_OWN]))
F(dat, "public static final int[] HT_ORDER = %s;" % jints([r[2] for r in HUB_OWN]))
F(dat, "public static final String[] HT_LABEL = %s;" % jarr([r[3] for r in HUB_OWN]))
F(dat, "public static final String[] HT_CMD = %s;" % jarr([r[4] or "" for r in HUB_OWN]))
F(dat, "public static final boolean[] HT_VIS = %s;" % jbools([r[1] in HUB_OWN_VIS for r in HUB_OWN]))
''')

# ---------------------------------------------------------------------------------------------------------------- the hub classes
rep('''pl   = mk("SkyyMenuPlugin", JP)
''', '''pl   = mk("SkyyMenuPlugin", JP)
# 0.3.28: hubs H2 - the kit's HubBar (kit skyyui 1.5, sky tabs) in OUR package (cross-jar classes are not allowed: every hub mod has its
# own copy of the same code), MenuHub (hub:last, the hub commands, Menu's own tab pages), the open / visible Functions, the 5 commands
hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod)
MADE.append(hubb)
mhub = mk("MenuHub")
mho  = mk("MenuHubOpen")
mhv  = mk("MenuHubVis")
hcch = mk("HubCharCmd", T["APC"])
hcst = mk("HubStorageCmd", T["APC"])
hcmk = mk("HubMarketCmd", T["APC"])
hctr = mk("HubTravelCmd", T["APC"])
hcso = mk("HubSocialCmd", T["APC"])
''')

# MenuHub part 1 (before every page: the pages call ensure / click / opened)
rep('''# ================= MenuPage (inline page; views switched with rebuild()) =================
''', r'''# ================= 0.3.28 MenuHub part 1: hub:last + the hub click helper (the pages use these; part 2 opens pages, after them) =========
# hub:last:<uuid> = a java.util.Map (hub -> last tab) on the bridge, MEMORY ONLY (spec 2.1): made at join (MenuReady) and whenever a hub
# page draws (ensure), removed on disconnect (MenuQuit), for players gone (SeenTick, a fresh online list) and at shutdown. LAST = the uuids
# whose map THIS mod made (forget removes only a key that still holds our map). Every HubBar.build (any mod) writes into it.
F(mhub, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")
M(mhub, r"""
public static java.util.Map ensure(java.util.UUID u) {
  if (u == null) return null;
  try {
    java.util.Map br = @PKG@.MenuUtil.bridge();
    String k = "hub:last:" + u.toString();
    Object o = br.get(k);
    if (o == null) {
      java.util.concurrent.ConcurrentHashMap m = new java.util.concurrent.ConcurrentHashMap();
      Object prev = br.putIfAbsent(k, m);
      o = prev == null ? m : prev;
    }
    if (!(o instanceof java.util.Map)) return null;
    LAST.put(u, o);
    return (java.util.Map) o;
  } catch (Throwable t) { return null; }
}""")
M(mhub, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  Object mine = LAST.remove(u);
  if (mine == null) return;
  try { @PKG@.MenuUtil.bridge().remove("hub:last:" + u.toString(), mine); } catch (Throwable t) { }
}""")
M(mhub, r"""
public static int sweep(java.util.Set online) {
  java.util.Set base = @PKG@.SoundSw.live();
  if (base == null) base = online;
  if (base == null) return 0;
  java.util.ArrayList ks = new java.util.ArrayList(LAST.keySet());
  int n = 0;
  for (int i = 0; i < ks.size(); i++) {
    Object o = ks.get(i);
    if (!base.contains(o)) { forget((java.util.UUID) o); n = n + 1; }
  }
  return n;
}""")
M(mhub, r"""
public static int clearAll() {
  java.util.ArrayList ks = new java.util.ArrayList(LAST.keySet());
  for (int i = 0; i < ks.size(); i++) forget((java.util.UUID) ks.get(i));
  return @PKG@.HubBar.removeAll();
}""")
M(mhub, r"""
public static int hubIndex(String hub) {
  if (hub == null) return -1;
  for (int i = 0; i < @PKG@.MenuData.HUB_ID.length; i++) { if (@PKG@.MenuData.HUB_ID[i].equals(hub)) return i; }
  return -1;
}""")
# the visible rule of Menu's own tabs (the TILE_RULES of the Mods / Server Setup tiles): mods = admins, or everyone while menu.modsHelp is
# on; setup = admins (the Server Setup page re-checks its node on every click - its own guard)
M(mhub, r"""
public static boolean visible(String tab, @PR@ pr) {
  if (tab == null) return false;
  if (tab.equals("setup")) return @PKG@.MenuUtil.isAdmin(pr);
  if (tab.equals("mods")) return @PKG@.MenuUtil.isAdmin(pr) || @PKG@.MenuCfg.MODS_HELP;
  return true;
}""")
M(mhub, r"""
public static boolean opened(String r) {
  return "back".equals(r) || "bridge".equals(r) || "command".equals(r);
}""")
# a page's click: null = not a hub click; "close" (the X); "menu" (< Menu: the page opens the SkyWynn Menu itself - never /skymenu, which
# would also hand out a lost menu item); else HubBar.handle's answer ("self", "bridge", "command", "hidden", "missing", "nocmd", "failed")
M(mhub, r"""
public static String click(@PR@ pr, String data, String hub, String tab) {
  if (data == null || data.indexOf("\"hub:") < 0) return null;
  String a = @PKG@.HubBar.jsonStr(data, "a");
  if (!a.startsWith("hub:")) return null;
  if (a.equals("hub:back")) return "menu";
  return @PKG@.HubBar.handle(pr, data, hub, tab);
}""")
# the tab a hub command opens: the hub's last tab while it is still shown to this player, else the first shown tab; null = none yet
M(mhub, r"""
public static String pick(String hub, java.util.UUID u) {
  java.util.ArrayList t = @PKG@.HubBar.tabs(hub, u);
  if (t.isEmpty()) return null;
  Object m = u == null ? null : @PKG@.HubBar.get("hub:last:" + u.toString());
  if (m instanceof java.util.Map) {
    Object l = ((java.util.Map) m).get(hub);
    for (int i = 0; i < t.size(); i++) {
      Object[] e = (Object[]) t.get(i);
      if (e[0].equals(l)) return (String) e[0];
    }
  }
  return (String) ((Object[]) t.get(0))[0];
}""")

# ================= MenuPage (inline page; views switched with rebuild()) =================
''')

# ---------------------------------------------------------------------------------------------------------------- MenuPage: the hub views
_mb = block('''M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.cleared = false;''', '''  ev.addEventBinding(@BT@.Dismissing, "#SkyyMenu", @EVD@.of("a", "mesc"), false);
}""")
''')
assert _mb.count("b.appendInline((String) null, @PKG@.MenuData.UI_ROOT);") == 1 and "#SkyyMStatus.Text" in _mb
_mn = _mb
for _a, _b in (
        ('''M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.cleared = false;''', '''# 0.3.28: the views that are hub tabs draw in the hub shell: tp = World > Teleport, players / player = Social > Players, mods = Settings >
# Mods, the main view while editing = Settings > Menu layout. The main view itself keeps the 0.3.27 menu (H8 reduces it later).
M(page, r"""
public boolean hubMode() {
  String v = this.view == null ? "main" : this.view;
  return v.equals("tp") || v.equals("players") || v.equals("player") || v.equals("mods") || (v.equals("main") && this.editing);
}""")
M(page, r"""
public String hubName() {
  String v = this.view == null ? "main" : this.view;
  if (v.equals("tp")) return "world";
  if (v.equals("players") || v.equals("player")) return "social";
  return "settings";
}""")
M(page, r"""
public String hubTab() {
  String v = this.view == null ? "main" : this.view;
  if (v.equals("tp")) return "teleport";
  if (v.equals("players") || v.equals("player")) return "players";
  if (v.equals("mods")) return "mods";
  return "layout";
}""")
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.cleared = false;'''),
        ('''  try { fill(slots); } catch (Throwable t) { @PKG@.MenuUtil.warn("menu view " + this.view + " failed: " + t); }
  b.appendInline((String) null, @PKG@.MenuData.UI_ROOT);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_ACCENT);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_TITLE);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_HINT);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_INFOBOX);
  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFONAME);
  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFODESC);
  for (int i = 0; i < @PKG@.MenuData.UI_INFO.length; i++) b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFO[i]);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_GAP);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_GRIDWRAP);
  b.appendInline("#SkyyMGridWrap", tipsOff ? @PKG@.MenuData.UI_GRIDNOTIPS : @PKG@.MenuData.UI_GRID);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_STATUS);
''', '''  try { fill(slots); } catch (Throwable t) { @PKG@.MenuUtil.warn("menu view " + this.view + " failed: " + t); }
  boolean hub = hubMode();
  String stx = this.status == null ? "" : this.status;
  int nInfo = hub ? @PKG@.MenuData.HUB_INFO_LINES : @PKG@.MenuData.UI_INFO.length;
  if (hub) {
    @PKG@.MenuHub.ensure(this.playerRef.getUuid());
    String hn = hubName();
    if (hn.equals("world")) {
""" + "\\n".join("      " + ln for ln in MH_JAVA["world"].split("\\n")) + r"""
    } else if (hn.equals("social")) {
""" + "\\n".join("      " + ln for ln in MH_JAVA["social"].split("\\n")) + r"""
    } else {
""" + "\\n".join("      " + ln for ln in MH_JAVA["settings"].split("\\n")) + r"""
    }
    b.appendInline("#SkyyMenu", stx.length() > 0 ? @PKG@.MenuData.UI_HINTST : @PKG@.MenuData.UI_HINT);
    b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_INFOBOXH);
  } else {
    b.appendInline((String) null, @PKG@.MenuData.UI_ROOT);
    b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_ACCENT);
    b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_TITLE);
    b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_HINT);
    b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_INFOBOX);
  }
  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFONAME);
  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFODESC);
  for (int i = 0; i < nInfo; i++) b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFO[i]);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_GAP);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_GRIDWRAP);
  b.appendInline("#SkyyMGridWrap", tipsOff ? @PKG@.MenuData.UI_GRIDNOTIPS : @PKG@.MenuData.UI_GRID);
  if (!hub) b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_STATUS);
'''),
        ('''  b.set("#SkyyMTitle.Text", this.title == null ? "SkyWynn Menu" : this.title);
  b.set("#SkyyMHint.Text", this.editing && this.view.equals("main") ? @PKG@.MenuData.EDIT_HINT
                         : (tipsOff ? "Tooltips off - the speech bubble at the top right turns them on. Click an item to use it."
                                    : "Hover an item for details - click it to use it. Esc closes the menu."));
''', '''  if (!hub) b.set("#SkyyMTitle.Text", this.title == null ? "SkyWynn Menu" : this.title);
  String hint = this.editing && this.view.equals("main") ? @PKG@.MenuData.EDIT_HINT
              : (tipsOff ? "Tooltips off - the speech bubble at the top right turns them on. Click an item to use it."
                         : "Hover an item for details - click it to use it. Esc closes the menu.");
  b.set("#SkyyMHint.Text", hub && stx.length() > 0 ? stx : hint);
'''),
        ('''  int nInfo = @PKG@.MenuData.UI_INFO.length;
  for (int i = 0; i < nInfo; i++) {''', '''  for (int i = 0; i < nInfo; i++) {'''),
        ('''  b.set("#SkyyMStatus.Text", this.status == null ? "" : this.status);
''', '''  if (!hub) b.set("#SkyyMStatus.Text", stx);
'''),
        ('''  ev.addEventBinding(@BT@.Dismissing, "#SkyyMenu", @EVD@.of("a", "mesc"), false);
}""")
''', '''  ev.addEventBinding(@BT@.Dismissing, hub ? "#SkyyMenuH" : "#SkyyMenu", @EVD@.of("a", "mesc"), false);
  if (hub) """ + MH_BUILD + r"""
}""")
''')):
    assert _mn.count(_a) == 1, ("menu build", _a[:90], _mn.count(_a))
    _mn = _mn.replace(_a, _b)
rep(_mb, _mn)

# MenuPage: the layout editor's first status line ends "Done to finish." - in the hub shell the status replaces the hint row (EDIT_HINT)
rep('''  this.status = "Edit mode - no dragging: click a tile, then click its new slot.";
''', '''  this.status = "Edit mode - no dragging: click a tile, then click its new slot. Done to finish.";   // 0.3.28
''')
# MenuPage: the hub clicks (after startEdit / clearGrid / closePage exist; before handleDataEvent)
rep('''M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    if (data.indexOf("\\"skyymenucheck\\"") >= 0) {''', r'''# 0.3.28: a click on the hub bar of a menu view. The X closes (closePage: grid emptied first); "< Menu" = the main view in place; the active
# tab = redraw (a player's page -> the players list); Mods / Menu layout from each other = switched in place (same page); any other tab =
# the grid emptied once, then HubBar.handle (its open Function or its command - RefreshTask redraws the menu when a command opened no
# page); a tab that could not open = the status line.
M(page, r"""
public void hubClick(@REF@ ref, @ST@ st, String data) {
  String a = @PKG@.HubBar.jsonStr(data, "a");
  if (!a.startsWith("hub:")) return;
  String id = a.substring(4);
  this.status = "";
  this.cfgArm = null;
  if (id.equals("close")) { closePage(ref, st); return; }
  if (!hubMode()) { rebuild(); return; }
  if (id.equals("back")) { this.editing = false; this.editSel = -1; open("main"); rebuild(); return; }
  String hn = hubName();
  String my = hubTab();
  if (id.equals(my)) {
    if (this.view.equals("player")) open("players");
    rebuild();
    return;
  }
  if (hn.equals("settings") && id.equals("mods")) {
    if (!@PKG@.MenuHub.visible("mods", this.playerRef)) { this.status = @PKG@.MenuData.HUB_TXT_FAIL; rebuild(); return; }
    this.editing = false;
    this.editSel = -1;
    open("mods");
    rebuild();
    return;
  }
  if (hn.equals("settings") && id.equals("layout")) {
    if (@PKG@.MenuLayout.unreadable(this.playerRef.getUuid())) { this.status = @PKG@.MenuData.EDIT_WAIT; rebuild(); return; }
    open("main");
    startEdit();
    rebuild();
    return;
  }
  clearGrid();
  String r = @PKG@.HubBar.handle(this.playerRef, data, hn, my);
  if ("close".equals(r)) { closePage(ref, st); return; }
  if ("command".equals(r)) { @PKG@.RefreshTask.schedule(this, this.playerRef, 900L); return; }
  if (@PKG@.MenuHub.opened(r)) return;
  this.status = @PKG@.MenuData.HUB_TXT_FAIL;
  rebuild();
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    if (data.indexOf("\"skyymenucheck\"") >= 0) {''')
rep('''    if (data.indexOf("mesc\\"") >= 0) { new @PKG@.CloseTask(this, this.playerRef).accept(null, null); return; }
''', '''    if (data.indexOf("mesc\\"") >= 0) { new @PKG@.CloseTask(this, this.playerRef).accept(null, null); return; }
    if (data.indexOf("\\"hub:") >= 0) { hubClick(ref, st, data); return; }   // 0.3.28: the hub bar of a menu view
''')

# ---------------------------------------------------------------------------------------------------------------- StatsPage
rep('''""" + "\\n".join("  " + ln for ln in ST_SHELL_JAVA.split("\\n")) + r"""
""" + "\\n".join("  " + ln for ln in ST_TABS_JAVA.split("\\n")) + r"""
''', '''""" + "\\n".join("  " + ln for ln in ST_SHELL_JAVA.split("\\n")) + r"""
  @PKG@.MenuHub.ensure(u);
  """ + ST_HUB_JAVA + r"""
""" + "\\n".join("  " + ln for ln in ST_TABS_JAVA.split("\\n")) + r"""
''')
rep('''public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    if (data.indexOf("\\"tclose\\"") >= 0) {''', '''public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String hr = @PKG@.MenuHub.click(this.playerRef, data, "character", "stats");   // 0.3.28: the hub bar
    if (hr != null) {
      if (hr.equals("close")) {
        @PLA@ hc = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
        if (hc != null) hc.getPageManager().setPage(ref, st, @PGE@.None);
        return;
      }
      if (hr.equals("menu")) {
        @PLA@ hm = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
        if (hm != null) hm.getPageManager().openCustomPage(ref, st, new @PKG@.MenuPage(this.playerRef, "main"));
        return;
      }
      if (@PKG@.MenuHub.opened(hr)) return;
      this.status = hr.equals("self") ? "" : @PKG@.MenuData.HUB_TXT_FAIL;
      rebuild();
      return;
    }
    if (data.indexOf("\\"tclose\\"") >= 0) {''')

# ---------------------------------------------------------------------------------------------------------------- SettingsPage
rep('''  this.rowKeys = new String[per];
  b.appendInline((String) null, @PKG@.MenuData.UI_SROOT);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SACCENT);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_STITLE);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SHINT);
''', '''  this.rowKeys = new String[per];
  String stt = this.status == null ? "" : this.status;
  if (stt.length() == 0 && @PKG@.SetStore.isBroken(u)) stt = @PKG@.MenuData.SET_TXT_BROKEN;
  @PKG@.MenuHub.ensure(u);
""" + "\\n".join("  " + ln for ln in STG_HUB_JAVA.split("\\n")) + r"""
  b.appendInline("#SkyyStg", stt.length() > 0 ? @PKG@.MenuData.UI_SHINTST : @PKG@.MenuData.UI_SHINT);   // 0.3.28: the status shows here
''')
rep('''    b.appendInline("#SkyyStgRows", @PKG@.MenuData.UI_SGAP6);
''', '''    b.appendInline("#SkyyStgRows", @PKG@.MenuData.UI_SGAP3);
''')
rep('''  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SALWAYS);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SSTATUS);
''', '''  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SALWAYS);
''')
rep('''  b.set("#SkyyStgHint.Text", @PKG@.MenuData.SET_TXT_HINT);
''', '''  b.set("#SkyyStgHint.Text", stt.length() > 0 ? stt : @PKG@.MenuData.SET_TXT_HINT);
''')
rep('''  b.set("#SkyyStgAlways.Text", find ? @PKG@.MenuData.SET_TXT_FIND : @PKG@.MenuData.SET_ALWAYS[this.cat]);
  String stt = this.status == null ? "" : this.status;
  if (stt.length() == 0 && @PKG@.SetStore.isBroken(u)) stt = @PKG@.MenuData.SET_TXT_BROKEN;
  b.set("#SkyyStgStatus.Text", stt);
}""")''', '''  b.set("#SkyyStgAlways.Text", find ? @PKG@.MenuData.SET_TXT_FIND : @PKG@.MenuData.SET_ALWAYS[this.cat]);
  """ + STG_HUB_BUILD + r"""
}""")''')
rep('''    if (data == null) return;
    String fk = String.valueOf((char) 64) + "Find";''', '''    if (data == null) return;
    String hr = @PKG@.MenuHub.click(this.playerRef, data, "settings", "settings");   // 0.3.28: the hub bar
    if (hr != null) {
      boolean hadArm = this.armedAt > 0L;
      this.armedAt = 0L;                     // a hub click disarms Reset all, like every other click on this page
      if (hr.equals("close")) {
        @PLA@ hc = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
        if (hc != null) hc.getPageManager().setPage(ref, st, @PGE@.None);
        return;
      }
      if (hr.equals("menu")) {
        @PLA@ hm = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
        if (hm != null) hm.getPageManager().openCustomPage(ref, st, new @PKG@.MenuPage(this.playerRef, "main"));
        return;
      }
      if (@PKG@.MenuHub.opened(hr)) return;
      // the page's own tab with nothing to clear: no redraw, so a search the player is typing stays in its box (the bar sends no fields)
      if (hr.equals("self") && !hadArm && (this.status == null || this.status.length() == 0)) return;
      this.status = hr.equals("self") ? "" : @PKG@.MenuData.HUB_TXT_FAIL;
      rebuild();
      return;
    }
    String fk = String.valueOf((char) 64) + "Find";''')

# ---------------------------------------------------------------------------------------------------------------- AdminPage (Server Setup)
rep('''public void frame(@UCB@ b, String title, String sub) {
  b.appendInline((String) null, @MD@.UI_AROOT);
  b.appendInline("#SkyyAdm", @MD@.UI_AACCENT);
  b.appendInline("#SkyyAdm", @MD@.UI_ATITLE);
  b.appendInline("#SkyyAdm", @MD@.UI_ASUB);
  b.appendInline("#SkyyAdm", @MD@.UI_ABODY);
  b.set("#SkyyAdmTitle.Text", title == null ? "" : title);
  b.set("#SkyyAdmSub.Text", sub == null ? "" : sub);
}""")''', '''public void frame(@UCB@ b, String title, String sub) {
""" + "\\n".join("  " + ln for ln in ADM_HUB_JAVA.split("\\n")) + r"""
  b.appendInline("#SkyyAdm", @MD@.UI_ASUB);
  b.appendInline("#SkyyAdm", @MD@.UI_ABODY);
  String t = title == null ? "" : title;
  if (t.startsWith(@MD@.ADM_PREFIX)) t = t.substring(@MD@.ADM_PREFIX.length());   // the Server Setup tab already names the page
  String s = sub == null ? "" : sub;
  b.set("#SkyyAdmSub.Text", @MU@.clip(s.length() == 0 ? t : t + "   -   " + s, @MD@.ADM_SUBMAX));
}""")''')
rep('''    b.appendInline("#SkyyAdmFoot", btn(id, ((Integer) this.fW.get(i)).intValue(), 50, (String) this.fT.get(i), @MD@.ADM_BS));
    bind(ev, id, (String) this.fA.get(i));
  }
}""")''', '''    b.appendInline("#SkyyAdmFoot", btn(id, ((Integer) this.fW.get(i)).intValue(), 50, (String) this.fT.get(i), @MD@.ADM_BS));
    bind(ev, id, (String) this.fA.get(i));
  }
  @PKG@.MenuHub.ensure(me());   // 0.3.28: every view ends here (tail) - the hub tab strip of Settings > Server Setup
  """ + ADM_HUB_BUILD + r"""
}""")''')
rep('''# 0.3.23: the mod list's "Admin" button opens the Admin page (replaces this page; never close-then-open)
M(apg, r"""
public void openOps''', r'''# 0.3.28: after a hub bar click (MenuHub.click's answer): the X closes, "< Menu" opens the SkyWynn Menu, an opened tab owns the screen,
# the page's own tab draws nothing (the bar's click carries no field values: a redraw would drop typed text), a tab that could not open
# says so. Called from handleDataEvent AFTER guard() and from lockedClick.
M(apg, r"""
public void hubAfter(@REF@ ref, @ST@ st, String hr) {
  if (hr.equals("close")) { this.drafts = new java.util.HashMap(); closeNow(ref, st); return; }
  if (hr.equals("menu")) { openMenu(ref, st); return; }
  if (@PKG@.MenuHub.opened(hr)) return;
  if (hr.equals("self")) return;   // the page's own tab: nothing changes - no redraw, so typed values / an Import paste stay in their boxes
  setStatus(@MD@.HUB_TXT_FAIL, 3);
  rebuild();
}""")
# 0.3.23: the mod list's "Admin" button opens the Admin page (replaces this page; never close-then-open)
M(apg, r"""
public void openOps''')
rep('''    if (!guard()) { lockedClick(ref, st, data); return; }
    if (data == null) return;
    String a = @MU@.jstr(data, "a", 40);''', '''    if (!guard()) { lockedClick(ref, st, data); return; }
    if (data == null) return;
    String hr = @PKG@.MenuHub.click(this.playerRef, data, "settings", "setup");   // 0.3.28: the hub bar (after the guard)
    if (hr != null) { hubAfter(ref, st, hr); return; }
    String a = @MU@.jstr(data, "a", 40);''')
rep('''public void lockedClick(@REF@ ref, @ST@ st, String data) {
  if (data != null && "aclose".equals(@MU@.jstr(data, "a", 40))) { closeNow(ref, st); return; }''', '''public void lockedClick(@REF@ ref, @ST@ st, String data) {
  String hr = @PKG@.MenuHub.click(this.playerRef, data, "settings", "setup");   // 0.3.28: the hub bar works on the locked page too
  if (hr != null) { hubAfter(ref, st, hr); return; }
  if (data != null && "aclose".equals(@MU@.jstr(data, "a", 40))) { closeNow(ref, st); return; }''')

# ---------------------------------------------------------------------------------------------------------------- MenuHub part 2 + Functions + commands
rep('''# ================= MenuPageFactory (right-click on the menu item -> OpenCustomUI "SkyyMenu") =================
''', r'''# ================= 0.3.28 MenuHub part 2: Menu's own tab pages, the open / visible Functions, the registry, the hub commands =========
# page(): the page a Menu tab opens. openFor(): the open Function's body - the player's world thread (a page event or a command is the
# caller, HUBS-CONTRACT 1): the player's page manager opens the page (a SkyWynn Menu on screen gets its grid emptied first, the 0.1.3
# stuck-tooltip rule for every hand-off). Anything that goes wrong = false (the bar then tries the tab's command, HUBS-CONTRACT 1).
M(mhub, r"""
public static @PAGE@ page(@PR@ pr, String tab) {
  if (pr == null || tab == null) return null;
  if (tab.equals("stats")) return new @PKG@.StatsPage(pr, 0);
  if (tab.equals("teleport")) return new @PKG@.MenuPage(pr, "tp");
  if (tab.equals("players")) return new @PKG@.MenuPage(pr, "players");
  if (tab.equals("settings")) return new @PKG@.SettingsPage(pr, -1);
  if (tab.equals("mods")) return new @PKG@.MenuPage(pr, "mods");
  if (tab.equals("setup")) return new @PKG@.AdminPage(pr, "list", null);
  if (tab.equals("layout")) {
    @PKG@.MenuPage m = new @PKG@.MenuPage(pr, "main");
    if (@PKG@.MenuLayout.unreadable(pr.getUuid())) m.status = @PKG@.MenuData.EDIT_WAIT;
    else m.startEdit();
    return m;
  }
  return null;
}""")
M(mhub, r"""
public static boolean openFor(java.util.UUID u, String tab) {
  if (u == null || tab == null) return false;
  try {
    @PR@ pr = @UNI@.get().getPlayer(u);
    if (pr == null || !pr.isValid()) return false;
    if (!visible(tab, pr)) return false;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return false;
    @ST@ st = r.getStore();
    if (st == null) return false;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return false;
    @PGM@ pm = p.getPageManager();
    if (pm == null) return false;
    @PAGE@ pg = page(pr, tab);
    if (pg == null) return false;
    Object cur = pm.getCustomPage();
    if (cur instanceof @PKG@.MenuPage) ((@PKG@.MenuPage) cur).clearGrid();
    pm.openCustomPage(r, st, pg);
    return true;
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("the hub tab " + tab + " could not open: " + t);
    return false;
  }
}""")
mho.addInterface(pool.get("java.util.function.Function"))
F(mho, "public String tab;")
C(mho, "public MenuHubOpen(String tab) { this.tab = tab; }")
M(mho, r"""
public Object apply(Object o) {
  if (!(o instanceof java.util.UUID)) return Boolean.FALSE;
  return @PKG@.MenuHub.openFor((java.util.UUID) o, this.tab) ? Boolean.TRUE : Boolean.FALSE;
}""")
mhv.addInterface(pool.get("java.util.function.Function"))
F(mhv, "public String tab;")
C(mhv, "public MenuHubVis(String tab) { this.tab = tab; }")
M(mhv, r"""
public Object apply(Object o) {
  if (!(o instanceof java.util.UUID)) return Boolean.FALSE;
  @PR@ pr = null;
  try { pr = @UNI@.get().getPlayer((java.util.UUID) o); } catch (Throwable t) { pr = null; }
  if (pr == null) return Boolean.FALSE;
  return @PKG@.MenuHub.visible(this.tab, pr) ? Boolean.TRUE : Boolean.FALSE;
}""")
# setup(): hub:def:<hub> for the 7 hubs + Menu's own 7 tabs (HubBar.put: Object[]{mod, label, Integer order, command, open, visible});
# shutdown() removes them (clearAll -> HubBar.removeAll: only keys that still hold OUR arrays). Returns the tabs put.
M(mhub, r"""
public static int register() {
  for (int i = 0; i < @PKG@.MenuData.HUB_ID.length; i++) {
    @PKG@.HubBar.def(@PKG@.MenuData.HUB_ID[i], @PKG@.MenuData.HUB_TITLE[i], @PKG@.MenuData.HUB_CMD[i], @PKG@.MenuData.HUB_ICON[i]);
  }
  int n = 0;
  for (int j = 0; j < @PKG@.MenuData.HT_TAB.length; j++) {
    String c = @PKG@.MenuData.HT_CMD[j];
    Object vis = null;
    if (@PKG@.MenuData.HT_VIS[j]) vis = new @PKG@.MenuHubVis(@PKG@.MenuData.HT_TAB[j]);
    Object[] e = @PKG@.HubBar.put(@PKG@.MenuData.HT_HUB[j], @PKG@.MenuData.HT_TAB[j], "SkyyMenu", @PKG@.MenuData.HT_LABEL[j], @PKG@.MenuData.HT_ORDER[j],
                                  c.length() == 0 ? null : c, new @PKG@.MenuHubOpen(@PKG@.MenuData.HT_TAB[j]), vis);
    if (e != null) n = n + 1;
  }
  return n;
}""")
# a hub command (world thread): the hub's last tab while it is still shown, else its first shown tab (HubBar.open: its open Function,
# else its command); no tab yet = the "coming soon" chat line; a tab that could not open = one chat line. Returns open()'s answer.
M(mhub, r"""
public static String run(@PR@ pr, String hub) {
  if (pr == null) return "failed";
  int i = hubIndex(hub);
  String title = i < 0 ? String.valueOf(hub) : @PKG@.MenuData.HUB_TITLE[i];
  try {
    java.util.UUID u = pr.getUuid();
    ensure(u);
    String tab = pick(hub, u);
    if (tab == null) {
      pr.sendMessage(@MSG@.raw("[" + title + "] " + (i < 0 ? "Nothing here yet." : @PKG@.MenuData.HUB_SOON[i])));
      return "soon";
    }
    String r = @PKG@.HubBar.open(pr, u, hub, tab);
    if (opened(r)) return r;
    pr.sendMessage(@MSG@.raw("[" + title + "] " + @PKG@.MenuData.HUB_TXT_FAIL));
    return r;
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("/" + hub + " failed: " + t);
    try { pr.sendMessage(@MSG@.raw("[" + title + "] Could not open the " + title + " hub.")); } catch (Throwable t2) { }
    return "failed";
  }
}""")
# the five hub commands (spec 2.3): everyone (hytale:Adventurer, HANDOFF section 3), no arguments; /travel opens the World hub
C(hcch, r"""
public HubCharCmd() {
  super("character", "Open the Character hub - your stats and more, one tab each");
  addAliases(new String[] { "char" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(hcch, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.MenuHub.run(pr, "character");
}""")
C(hcst, r"""
public HubStorageCmd() {
  super("storage", "Open the Storage hub - the Void, Requip, Vault and Bank in one place");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(hcst, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.MenuHub.run(pr, "storage");
}""")
C(hcmk, r"""
public HubMarketCmd() {
  super("market", "Open the Market hub - Bazaar, Auction House and Merchants in one place");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(hcmk, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.MenuHub.run(pr, "market");
}""")
C(hctr, r"""
public HubTravelCmd() {
  super("travel", "Open the World hub - teleports, warps, your island and exploring");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(hctr, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.MenuHub.run(pr, "world");
}""")
C(hcso, r"""
public HubSocialCmd() {
  super("social", "Open the Social hub - players online, your party and guild");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(hcso, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.MenuHub.run(pr, "social");
}""")

# ================= MenuPageFactory (right-click on the menu item -> OpenCustomUI "SkyyMenu") =================
''')

# ---------------------------------------------------------------------------------------------------------------- join / quit / upkeep / plugin
rep('''    @PKG@.SoundSw.ready(pr.getUuid());   // 0.3.25
''', '''    @PKG@.SoundSw.ready(pr.getUuid());   // 0.3.25
    @PKG@.MenuHub.ensure(pr.getUuid());   // 0.3.28: hub:last:<uuid> (memory only)
''')
rep('''    @PKG@.SoundSw.forget(pr.getUuid());   // 0.3.25
''', '''    @PKG@.SoundSw.forget(pr.getUuid());   // 0.3.25
    @PKG@.MenuHub.forget(pr.getUuid());   // 0.3.28: hub:last:<uuid> goes with the player
''')
rep('''    @PKG@.SoundSw.sweep(online);   // 0.3.25
''', '''    @PKG@.SoundSw.sweep(online);   // 0.3.25
    @PKG@.MenuHub.sweep(online);   // 0.3.28: hub:last of players who left
''')
rep('''  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /stats (another mod may own it) - the Your Profile tile still opens the Stats page: " + t); }
''', '''  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /stats (another mod may own it) - the Your Profile tile still opens the Stats page: " + t); }
  // 0.3.28: hubs H2 - the registry (hub:def:* + Menu's own tabs) and the hub commands (a clash is logged and the menu still loads)
  int hubTabs = @PKG@.MenuHub.register();
  int hubCmds = 0;
  try { getCommandRegistry().registerCommand(new @PKG@.HubCharCmd()); hubCmds = hubCmds + 1; }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /character (another mod may own it): " + t); }
  try { getCommandRegistry().registerCommand(new @PKG@.HubStorageCmd()); hubCmds = hubCmds + 1; }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /storage (another mod may own it): " + t); }
  try { getCommandRegistry().registerCommand(new @PKG@.HubMarketCmd()); hubCmds = hubCmds + 1; }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /market (another mod may own it): " + t); }
  try { getCommandRegistry().registerCommand(new @PKG@.HubTravelCmd()); hubCmds = hubCmds + 1; }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /travel (another mod may own it): " + t); }
  try { getCommandRegistry().registerCommand(new @PKG@.HubSocialCmd()); hubCmds = hubCmds + 1; }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /social (another mod may own it): " + t); }
''')
rep('''page look """ + SUI_KIT_ID + r"""; page guard on''', '''page look """ + SUI_KIT_ID + r"""; hubs: " + hubTabs + " own tabs, " + hubCmds + " of 5 hub commands (/character /char /storage /market /travel /social), Sky Window kit textures shipped; page guard on''')
rep('''  try { @PKG@.SoundSw.clearAll(); } catch (Throwable t) { }   // 0.3.25
''', '''  try { @PKG@.SoundSw.clearAll(); } catch (Throwable t) { }   // 0.3.25
  try { @PKG@.MenuHub.clearAll(); } catch (Throwable t) { }   // 0.3.28: hub:def / Menu's tabs / hub:last off the bridge
''')
rep('''         scl, stp, sta, stc, pet, lay, lsv, spt, mio, midx, gsv, mhk, hko, ops, snt, stv, stm, ssw, pl)''',
    '''         scl, stp, sta, stc, pet, lay, lsv, spt, mio, midx, gsv, mhk, hko, ops, snt, stv, stm, ssw,
         hubb, mhub, mho, mhv, hcch, hcst, hcmk, hctr, hcso, pl)   # 0.3.28: the hub classes''')

# ---------------------------------------------------------------------------------------------------------------- the kit art in the jar
rep('''jar = os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)
''', r'''# 0.3.28: the Sky Window kit art - all 59 files, byte-identical in every hub jar (sha256-pinned by the kit; HUBS-CONTRACT 2.7), under
# Common/UI/Custom/SkyyKit/ only (a texture outside Common/UI/Custom disconnects the client - probe k1b, 2026-10-15)
_kit = SUI.kit_texture_files()
assert len(_kit) == len(SUI.SKY_FILES) == 59 and all(p.startswith("Common/UI/Custom/SkyyKit/") and ".." not in p for p in _kit), "0.3.28: the kit art"
assert not set(_kit) & set(files), "0.3.28: a kit file clashes with a file of this jar"
files.update(_kit)
print("0.3.28 kit art:", len(_kit), "files under Common/UI/Custom/SkyyKit/ (%d bytes)" % sum(len(v) for v in _kit.values()))
jar = os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)
''')
rep('''if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyMenu.jar")''', '''# 0.3.28: the built jar carries the full kit set, byte for byte, and no SkyyKit file outside the custom root (silent: the build ends with
# the "assembled" line)
assert SUI.check_jar_kit(jar, need=("Header", "HeaderOrnament", "Tab", "Tab_Selected", "Close", "Frame", "Frame_Character", "Frame_World",
                                     "Frame_Social", "Tertiary")) == 59, "0.3.28: the jar's kit art"
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyMenu.jar")''')

# ---------------------------------------------------------------------------------------------------------------- done
for _w in ("UI_SROOT", "UI_SACCENT", "UI_STITLE", "UI_SSTATUS", "UI_SGAP6", "#SkyyStgStatus", "#SkyyStgTitle", "UI_AROOT", "UI_AACCENT",
           "UI_ATITLE", "#SkyyAdmTitle"):
    assert _w not in s, "0.3.28: %s is still used" % _w
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:100]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.27 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.27 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
