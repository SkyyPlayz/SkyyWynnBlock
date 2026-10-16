"""Derive SkyyMenu/build_skyymenu_0.3.30.py from the LIVE SkyyMenu 0.3.29 (python tools/menu_0_3_30_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_29_patch.py -> 0.3.29 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.30. The harness SkyyMenu/test_skyymenu_0.3.30.py is its own file.

0.3.30 (2026-10-16) = round menu0330 (docs/answered/ui.md 2026-10-16: STORAGE ICON, MENU: NO DUPLICATES + BIGGER + RIGHT NOW, MENU ICON
DUPLICATES, SHORTCUT GRID 5x5, SMITHING HUB 'COMING SOON'; research/Hubs-Spec.md + research/Unified-Menu-Plan.md section 2):
  1. NO DUPLICATES. (a) every hub / page / old tile / teleport has its OWN icon: 17 new icon items (wave 3) painted at BUILD TIME with the
     sheet-1 painter (tools/art/make_menu_icons.py, 64 px grid) from the approved motifs of art/hub-tab-icons (tools/art/make_hub_tab_icons.py
     builders, unfaded, scaled 72 -> 64 at the sample points, so every pixel is painted at 64 px): the 7 hubs (Skyy: "storage and pocket
     dimension look the same", World = the Teleport portal) + Trees, Class, Profiles, Requip (was the vanilla Village Wardrobe), Gear,
     Upgrade, Explore, Quests, Merchants, Edit shortcuts. Build check: no icon item names two pages. (b) the same page twice is ONE entry:
     a page's keys (tab:<hub>:<tab>, its old tile tile:<key>, and a hub whose DEFAULT tab it is - Character -> Skills, now World -> Teleport)
     share one canonical page (MenuLayout.canon): + Add lists it once (the tab), a grid never holds it twice. Saved grids holding a page
     twice keep the most exact key (tab, else the old tile, else the hub; ties = reading order) - the default Home drops hub:world (it was
     World + Teleport side by side).
  1c. 5 x 5 SHORTCUT GRID (Skyy: "5x5 is big enough for the shortcuts."), Home and Teleport, view and edit. The files keep 0.3.29's 7 x 5
     NUMBERING (g.<slot> / t.<slot>, 17 = the centre): the 5 x 5 grid is its columns 1 - 5, so a rollback to 0.3.29 reads every pin where it
     is. ONE-TIME UPDATE (PROJECT-RULES 4) only when a saved grid changes (a pin in column 0 / 6 moves to the nearest free slot, reading
     order; a duplicate page is merged): verified History copy first, the change APPENDED to the file's exact bytes in its own line ending
     (_g5=1 = the run-once marker + only the g. / t. lines that change; empty = removed), one config-changes.log line. More pins than 25:
     the first 25 kept, the rest wait in + Add and the player is told once (chat + the Home info line). Skyy's live grid fits as it is (no
     write).
  2. SCALED UP (Skyy: "scale up this menu a lot"): Home 1600 x 926 (was 1268 x 616), Teleport 1300 x 962 (was 804 x 704); 120 px slots /
     88 px icons (were 84 / 62); You and Right now 456 px wide (were 300) with 20 px lines; foot buttons normal size 48 px; ROW 1 (the hubs,
     48 px buttons, 32 px icons, 18 px labels) and Teleport's ROW 2 (the World tabs, 56 px, 48 px tab icons, 20 px labels) are drawn big
     inside the body under the kit's fixed 38 px title bar (crest + page title). The centre slot keeps 0.3.28 slot 13's screen spot (0, +4)
     on both pages (asserted). Every other Menu page keeps its size (Players / Mods / Stats / Settings / Server Setup already fill 980).
  3. RIGHT NOW (Unified-Menu-Plan 2): always shown next to You and the grid; rows from existing bridges only - "Quest: <the first undone
     task> <progress>" (quest:fn:hud) -> World > Quests; "N mystery bags to identify" (the Skyy_Unid_Bag_* items in your inventory, while
     gear:fn:smithing exists) -> Smithing > Identify; then every home:alert:<mod> line. Empty = "Nothing waiting". Read when Home is drawn
     (no ticking). No bridge exists today for tree AP, shards ready or party invites (those rows wait for their mods: home:alert:<mod>).
  4. QUEUED: Invite to Guild (Social > Players > a player: /guild invite <name>, next to Invite to Party); Stats > Main 'Health Regen'
     (skill:fn:hpregen {"row", uuid}); Spellblade / Battlemagic in the class roster texts; HUB TAB ICONS: the 32 art/hub-tab-icons files
     (+ _on) ship at Common/UI/Custom/SkyyHubTabs/<hub>_<tab>@2x.png = the kit 1.6 hook path (tools/HUBS-CONTRACT.md "Tab icons"; the art
     README named SkyyKit/HubTab, the kit's compiled HubBar draws SkyyHubTabs - the kit wins); Menu's own tabs and its stand-in tabs are put
     with HubBar.putIcon; Menu's big Teleport strip draws the art for every contract tab.
  5. NO 'COMING SOON' WHERE A PAGE EXISTS: SkyyMenu puts a STAND-IN hub tab for every contract tab (skyyui.HUB_TABS) whose owner put none
     (SkyyGear has no hub tabs: Smithing was empty -> "coming soon"): only while that key is free (an owner's own tab always wins, now or
     later), visible only while its command exists, open = SkyyGear's gear:fn:smithing (gear craft / reforge / upgrade / identify), else the
     contract command as the player (kit HubBar.open). So the Smithing tile / row button opens /smithing, Storage > Pocket = /sacks, World >
     Quests = /quests ... everywhere (every mod's row 1 too). Multitool is left out (Skyy: "we scrapped the multitool menu").
  FIX ROUND (menu0330fix): the HUD shortcut (Settings > HUD on Home) runs /skyyhud directly (ui.md 2026-10-16 HUD SHORTCUT OPENS THE
     EDITOR); the "Some shortcuts did not fit" Right now row stays until Edit shortcuts opens (chat + info line still once); the 5 x 5
     update's config-changes.log line names the pins that found no slot + the undo (old lines above + the History copy); an unknown key's
     line is never blanked by the update; the ready line tests /smithing itself.
  FIX ROUND 2 (menu0330fix2): when BOTH grids have pins without a free slot, the Teleport ones are no longer dropped from the log line /
     chat note / Right now (MenuLayout.joinSpill); Invite to Guild wears a vanilla banner (player-page actions never wear a Menu page icon
     except 0.3.26's three teleport actions - build check).
Saved data: layouts/<uuid>.properties + layout-default.properties (format unchanged; the one-time update above). ROUND_PINS = {}.
Rollback to 0.3.29: safe - it reads the same g. / t. lines (the 5 x 5 pins sit in its columns 1 - 5); its stand-in tabs vanish with 0.3.30.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.29.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.30.py")
CR, LF = chr(13), chr(10)
raw = open(src, encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.29"' in s and "0.3.29: UNIFIED MENU U1 (notes" in s and "0.3.30" not in s, "not the generated 0.3.29 script"
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
    return s[i:j + len(end)]


# ---------------------------------------------------------------------------------------------------------------- the pages block (0.3.30)
PAGES30 = r'''# ---- 0.3.30: HOME + TELEPORT SCALED UP (Skyy 2026-10-16 "scale up this menu a lot"): 120 px slots / 88 px icons (were 84 / 62), You and
# Right now 456 px wide (were 300) with 20 px lines, foot buttons in the normal size (48 px), and BOTH tab rows drawn big INSIDE the body:
# row 1 (Home + the hubs: 48 px buttons, 32 px item icons, 18 px labels) and, on Teleport, row 2 (the World tabs: 56 px, the 48 px tab icon
# behind each word, 20 px labels). The title bar keeps the kit's fixed 38 px Header (it holds the crest + the page title; the kit says
# never scale it). Ids start with SkyyM (the grid keeps #SkyyMGrid: the same slot binding, clearGrid and click path). Every page stays
# inside the kit's 1600 x 980 page (1080p with the vanilla UI scale); the centre slot keeps 0.3.28 slot 13's screen spot (asserted).
SLOT30, SLOT30_ICON = 120, 88
HG_W, HG_H = SLOT30 * HG_COLS, SLOT30 * HG_ROWS        # 600 x 600
HOME_W = SUI.MAX_PAGE_W                                  # 1600
HOME_GAP = 20
HOME_SIDE = (HOME_W - 2 * HUB_PAD - HG_W - 2 * HOME_GAP) // 2
YOU_PAD = 18
YOU_BAR_W = HOME_SIDE - 2 * YOU_PAD
# row 1 (big): BR_*; row 2 (big, Teleport): BT_*
BR_H, BR_GAP, BR_BELOW, BR_PAD, BR_PADV, BR_ICON, BR_ICON_GAP, BR_LAB, BR_LAB_MIN, BR_ICON_MIN = 48, 6, 8, 10, 6, 32, 6, 18, 12, 120
BT_H, BT_BELOW, BT_GAP, BT_ICON, BT_LAB, BT_LAB_MIN, BT_MIN, BT_PAD = 56, 8, 6, 48, 20, 14, 150, 8
BT_ICON_TOP = (BT_H - BT_ICON) // 2
BR_LABN = ("(FontSize: %d, TextColor: %s, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center, ShrinkTextToFit: true, "
           "MinShrinkTextToFitFontSize: %d)" % (BR_LAB, SUI.color("button2Text"), BR_LAB_MIN))
BR_LABSEL = ("(FontSize: %d, TextColor: %s, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center, ShrinkTextToFit: true, "
             "MinShrinkTextToFitFontSize: %d)" % (BR_LAB, SUI.color("buttonText"), BR_LAB_MIN))
BT_LAB = ("(FontSize: %d, TextColor: %s, RenderBold: true, HorizontalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: %d, "
          "VerticalAlignment: Center)" % (BT_LAB, SUI.color("buttonText"), BT_LAB_MIN))
HOME_MIDT_H, HOME_MIDGAP, HOME_GRID_TOP = 40, 6, 3
HOME_MAIN_H = HOME_MIDT_H + HOME_MIDGAP + HOME_GRID_TOP + HG_H + 3
HOME_FOOT_H, HOME_FOOTGAP, FOOT_BTN_H = 56, 10, 48
HINFO_FS, HINFO_H = 16, 48                            # the Home info line: 16 px, wraps to TWO lines in its 48 px
HOME_H = 926


def big_shell(prefix, w, h, hub, title, body_id):
    """kit 1.6 hub_shell(row=True) minus row 1 (and the 44 px tab strip): the 38 px Header gets the crest + the page title instead (the
    kit's own non-row title bar pieces), the big rows go into the body at run time (MenuPage.bigRow / bigTabs)"""
    sh = SUI.hub_shell(prefix, w, h, hub, row=True, body_id=body_id)
    ow, oh, otop = SUI.THEME_ORNAMENT["sky"]
    apps = SUI.Appends()
    for _p, _mk in sh.appends:
        if (prefix + "HubRow") in _mk or (prefix + "HubTabs") in _mk:
            continue
        apps.append((_p, _mk))
        if _mk.startswith("Group #%s {" % sh.bar):
            apps.append((sh.bar, "Group { Anchor: (Width: %d, Height: %d, Top: %d); Background: %s; }" % (ow, oh, otop, SUI.THEME["sky"]["ornament"])))
            apps.append((sh.bar, SUI.title_label(prefix + "Title", title)))
    kw = dict(sh.__dict__)
    kw.pop("sets", None)
    kw.update(appends=apps, inner_h=sh.h - SUI.TITLE_H - 2 * sh.pad, tabs=None, tabs_w=0, parts=SUI.HUB_PART_CLOSE, row=False, row_w=0,
              row_id=None, title=prefix + "Title")
    out = SUI.Shell(**kw)
    assert len(apps) == len(sh.appends) - (1 if hub == "home" else 2) + 2 and out.close == prefix + "HubClose"
    return out


HOME_SH = big_shell("SkyyMHm", HOME_W, HOME_H, "home", "SkyWynn Menu", "SkyyMHome")
HOME_FOOT_W = HOME_ROW_W = HOME_SH.inner_w
assert (HOME_W, HOME_SH.inner_w, HOME_SIDE) == (1600, 1552, 456)
assert BR_H + BR_BELOW + HOME_MAIN_H + HOME_FOOTGAP + HOME_FOOT_H <= HOME_SH.inner_h, "0.3.30: the Home body fits"
# ---- TELEPORT (World > Teleport): big row 1, big row 2 (the World tabs), the grid (centred by a lead), a two-line info box, the foot
TP_W, TP_H = 1300, 962
TP_INFO_H, TP_GAP = 58, 8
TP_SH = big_shell("SkyyMTp", TP_W, TP_H, "world", "World", "SkyyMTpB")
TP_FOOT_W = TP_ROW_W = TP_SH.inner_w
TP_LEAD = (TP_SH.inner_w - HG_W) // 2
assert TP_LEAD == 326 and BR_H + BR_BELOW + BT_H + BT_BELOW + HG_H + HOME_GRID_TOP + TP_GAP + TP_INFO_H + TP_GAP + HOME_FOOT_H <= TP_SH.inner_h, \
    "0.3.30: the Teleport body fits"
# THE CENTRE SLOT UNDER THE MOUSE (Skyy: "open it, click twice, and be at my island without moving the mouse"). A page opens centred on the
# screen with the mouse at the screen centre; 0.3.28's slot 13 sat at the page centre + (0, +4) - computed from the 0.3.28 markup itself.
_hpx = lambda mk: int(re.search(r"Height: (\d+)", mk).group(1))
OLD_SLOT13 = (22 + OLD_CC * SLOT + SLOT // 2 - PW // 2,
              14 + _hpx(UI["ACCENT"]) + _hpx(UI["TITLE"]) + _hpx(UI["HINT"]) + _hpx(UI["INFOBOX"]) + _hpx(UI["GAP"]) + 3 + OLD_CR * SLOT + SLOT // 2 - PH // 2)
assert "Top: 3" in UI["GRID"] and "Padding: (Horizontal: 22, Vertical: 14)" in UI["ROOT"]
HOME_C = (HUB_PAD + HOME_SIDE + HOME_GAP + HG_CC * SLOT30 + SLOT30 // 2 - HOME_W // 2,
          SUI.TITLE_H + HUB_PAD + BR_H + BR_BELOW + HOME_MIDT_H + HOME_MIDGAP + HOME_GRID_TOP + HG_CR * SLOT30 + SLOT30 // 2 - HOME_H // 2)
TP_C = (HUB_PAD + TP_LEAD + HG_CC * SLOT30 + SLOT30 // 2 - TP_W // 2,
        SUI.TITLE_H + HUB_PAD + BR_H + BR_BELOW + BT_H + BT_BELOW + HOME_GRID_TOP + HG_CR * SLOT30 + SLOT30 // 2 - TP_H // 2)
assert OLD_SLOT13 == (0, 4) and HOME_C == OLD_SLOT13 and TP_C == OLD_SLOT13, "0.3.30: the centre slot keeps slot 13's screen spot %s / %s / %s" % (
    OLD_SLOT13, HOME_C, TP_C)
assert SUI.MAX_PAGE_H >= max(HOME_H, TP_H) and SUI.MAX_PAGE_W >= max(HOME_W, TP_W), "0.3.30: both pages fit 1080p"
_K = SUI.THEME["sky"]
_gridmk = lambda tips: ("ItemGrid #SkyyMGrid { Anchor: (Horizontal: 0, Top: %d, Width: %d, Height: %d); SlotsPerRow: %d; AreItemsDraggable: false; %s"
                        "Style: (SlotSize: %d, SlotIconSize: %d, SlotSpacing: 0); }" % (HOME_GRID_TOP, HG_W, HG_H, HG_COLS, "" if tips else "InfoDisplay: None; ",
                                                                                         SLOT30, SLOT30_ICON))
_ALAB = ("(FontSize: 17, TextColor: %s, RenderBold: true, HorizontalAlignment: Start, VerticalAlignment: Center, ShrinkTextToFit: true, "
         "MinShrinkTextToFitFontSize: 13)" % SUI.color("rowName"))
UI29 = {
    "HMAIN": SUI.group("SkyyMHmMain", "Left", h=HOME_MAIN_H),
    "HYOU": "Button #SkyyMHmYou { Anchor: (Width: %d, Height: %d); LayoutMode: Top; Padding: (Full: %d); Style: ButtonStyle(Default: (Background: %s), "
            "Hovered: (Background: %s), Pressed: (Background: %s), Sounds: %s); }" % (HOME_SIDE, HOME_MAIN_H, YOU_PAD, _K["panel"], _K["card"], _K["inset"],
                                                                                        SUI.sounds("light")),
    "HYT": SUI.label("SkyyMHmYT", HOME_TXT["HT_YOU_TITLE"], "panelTitle", h=32, size=20),
    "HYN": SUI.label("SkyyMHmYN", "", "heading", h=40, size=26, wrap=False),
    "HYBAR0": "Group #SkyyMHmYBar { Anchor: (Width: %d, Height: 12, Bottom: 8); Background: %s; Group #SkyyMHmYFill { Anchor: (Left: 0, Width: " % (
        YOU_BAR_W, SUI.color("progressTrack")),
    "HYBAR1": ", Height: 12); Background: %s; } }" % SUI.color("progressFill"),
    "HYH": SUI.label("SkyyMHmYH", HOME_TXT["HT_YOU_HINT"], "caption", h=30, size=17),
    "HSP16": SUI.spacer(w=HOME_GAP),
    "HMID": SUI.group("SkyyMHmMid", "Top", w=HG_W, h=HOME_MAIN_H),
    "HMIDT": SUI.label("SkyyMHmMidT", "", "heading", h=HOME_MIDT_H, size=22, align="Center", wrap=False),
    "HGAP5": SUI.spacer(h=HOME_MIDGAP),
    "HGW": "Group #SkyyMGW { Anchor: (Width: %d, Height: %d); }" % (HG_W, HG_H + HOME_GRID_TOP),
    "HGRID": _gridmk(True),
    "HGRIDNT": _gridmk(False),
    "HNOW": "Group #SkyyMHmNow { Anchor: (Width: %d, Height: %d); LayoutMode: Top; Padding: (Full: %d); Background: %s; }" % (HOME_SIDE, HOME_MAIN_H, YOU_PAD, _K["panel"]),
    "HNOWT": SUI.label("SkyyMHmNowT", HOME_TXT["HT_NOW_TITLE"], "panelTitle", h=32, size=20),
    "HNOWNONE": SUI.label("SkyyMHmNowE", HOME_TXT["HT_NOW_NONE"], "caption", h=34, size=18),
    "HGAP8": SUI.spacer(h=HOME_FOOTGAP),
    "HFOOT": "Group #SkyyMHmFoot { Anchor: (Height: %d); LayoutMode: Left; Padding: (Top: %d); }" % (HOME_FOOT_H, HOME_FOOT_H - FOOT_BTN_H - 4),
    "HINFO0": "Label #SkyyMHmInfo { Anchor: (Width: ",
    "HINFO1": ', Height: %d); Padding: (Horizontal: 8); Text: ""; Style: %s; }' % (HINFO_H, SUI.text_style(HINFO_FS, "rowName", wrap=True)),
    "FSP": SUI.spacer(w=10),
    "BROW": "Group #SkyyMBRow { Anchor: (Height: %d, Bottom: %d); LayoutMode: Left; }" % (BR_H, BR_BELOW),
    "BTABS": "Group #SkyyMBTabs { Anchor: (Height: %d, Bottom: %d); LayoutMode: Left; }" % (BT_H, BT_BELOW),
    "TROW": SUI.group("SkyyMTpRow", "Left", h=HG_H + HOME_GRID_TOP),
    "TLEAD": SUI.spacer(w=TP_LEAD),
    "TINFO": "Group #SkyyMTpInfo { Anchor: (Height: %d); LayoutMode: Top; Padding: (Horizontal: 16, Vertical: 4); Background: %s; }" % (TP_INFO_H, _K["inset"]),
    "TIN": SUI.label("SkyyMTpIN", "", "rowName", h=26, size=19, wrap=False),
    "TID": SUI.label("SkyyMTpID", "", "default", h=22, size=16, wrap=False),
    "TGAP": SUI.spacer(h=TP_GAP),
    "TFOOT": "Group #SkyyMTpFoot { Anchor: (Height: %d); LayoutMode: Left; Padding: (Top: %d); }" % (HOME_FOOT_H, HOME_FOOT_H - FOOT_BTN_H - 4),
}
UI29_HYL = [SUI.label("SkyyMHmYL%d" % i, "", "default", h=34, size=20, col="rowName", wrap=False) for i in range(7)]
UI29_HA = ['TextButton #SkyyMHmA%d { Anchor: (Height: 52, Bottom: 8); Padding: (Horizontal: 12); Text: ""; Style: TextButtonStyle(Default: (Background: %s, '
           'LabelStyle: %s), Hovered: (Background: %s, LabelStyle: %s), Pressed: (Background: %s, LabelStyle: %s), Sounds: %s); }' % (
               i, _K["row"], _ALAB, _K["rowHovered"], _ALAB, _K["rowSelected"], _ALAB, SUI.sounds("light")) for i in range(AL_SHOW)]
assert 32 + AL_SHOW * 60 + 2 * YOU_PAD <= HOME_MAIN_H and 32 + 40 + 7 * 34 + 20 + 30 + 2 * YOU_PAD <= HOME_MAIN_H, "0.3.30: You / Right now fit"
# the foot buttons (one table, both pages): word -> (label, width, kind, sound). The event is a = "f<word>". 0.3.30: the normal size, 48 px.
FB = [("hedit", "Edit shortcuts", 230, "secondary", None), ("close", "Close", 150, "secondary", "cancel"),
      ("prev", "< Prev", 130, "secondary", None), ("next", "Next >", 130, "secondary", None),
      ("eremove", "Remove", 130, "destructive", None), ("ereset", "Reset", 120, "secondary", None),
      ("esrv", "Set default", 170, "secondary", None), ("estd", "Clear default", 190, "secondary", None),
      ("eold", "Old tiles back", 200, "secondary", None), ("edone", "Done", 120, "primary", None),
      # fix round 2: an admin's in-game Undo of the SERVER DEFAULT's one-time update (PROJECT-RULES 4): the old default's tiles back
      # (shown on Home edit while the server default keeps an _old line and no tile is picked up)
      ("edold", "Old default", 170, "secondary", None),
      ("aprev", "< Prev", 130, "secondary", None), ("anext", "Next >", 130, "secondary", None), ("acancel", "Cancel", 140, "secondary", "cancel")]
FB_GAP = 10
_fbmk = lambda pre, w_, lab, wid, kind, snd: 'TextButton #%sF%s { Anchor: (Width: %d, Height: %d); Padding: (Horizontal: 10); Text: "%s"; %s }' % (
    pre, w_, wid, FOOT_BTN_H, lab, SUI.theme_button_style(kind, "normal", theme="sky", sound=snd))
UI29_FBH = [_fbmk("SkyyMHm", w_, lab, wid, kind, snd) for w_, lab, wid, kind, snd in FB]
FB_TW = [130 if w_ == "hedit" else wid for w_, _l, wid, _k, _s in FB]
UI29_FBT = [_fbmk("SkyyMTp", w_, "Edit" if w_ == "hedit" else lab, tw, kind, snd) for (w_, lab, _wid, kind, snd), tw in zip(FB, FB_TW)]
for _w, _l, _wid, _k, _s in FB:
    assert SUI.text_width(_l, 17, bold=True, upper=True) <= _wid - 24, "0.3.30: foot button %s fits (%d px)" % (_l, SUI.text_width(_l, 17, bold=True, upper=True))
_mode_words = {"home": [["hedit", "close"], ["eremove", "ereset", "esrv", "estd", "eold", "edone"], ["ereset", "esrv", "estd", "eold", "edold", "edone"],
                        ["aprev", "anext", "acancel"]],
               "tp": [["hedit", "prev", "next", "close"], ["eremove", "ereset", "esrv", "estd", "edone"], ["aprev", "anext", "acancel"]]}
_fbw = dict((w_, wid) for w_, _l, wid, _k, _s in FB)
for _ws in _mode_words["home"]:
    assert HOME_FOOT_W - sum(_fbw[w_] + FB_GAP for w_ in _ws) >= 400, "0.3.30: the Home info line keeps 400 px in every foot row"
# EVERY text the Home info line can show fits its TWO wrapped lines in the NARROWEST foot row - the hints, the edit texts, every status
# literal of the page code below (a name in it counted as the longest tile or hub name; the literals of both ternary branches added up,
# so this over-counts), the no-pages / fail / wait lines. 0.85 = the room a word wrap may waste. The Teleport info box shows the same
# texts on one line (16 px, cut at its end).
HINFO_ROOM = HOME_FOOT_W - max(sum(_fbw[w_] + FB_GAP for w_ in _ws) for _ws in _mode_words["home"]) - 16
TP_INFO_ROOM = TP_SH.inner_w - 32
_name24 = max([_n for _k, _n in zip(E_KEY, E_NAME) if _k] + [SUI.HUB_DEFS[_h][0] for _h in SUI.HUBS], key=len)   # the longest tile / hub name
_src29 = open(os.path.abspath(__file__), encoding="utf8").read()
_msgs29 = [HOME_TXT[k] for k in ("HT_HINT", "HT_HINT_OFF", "HT_EDIT", "HT_EDIT_START", "HT_ADD", "HT_TP_HINT")]
_msgs29 += [EDIT_TXT["KEPT_MSG"], EDIT_TXT["EDIT_WAIT"], HUB_TXT_FAIL] + ["[%s] %s" % (SUI.HUB_DEFS[_h][0], HUB_SOON[_h]) for _h in SUI.HUBS]
_stl29 = re.findall(r'this\.status = ([^;\n]*);', _src29)
assert len(_stl29) >= 30, "0.3.29: the status lines are found (%d)" % len(_stl29)
for _st in _stl29:
    _lits = re.findall(r'"((?:[^"\\]|\\.)*)"', _st)
    if _lits:
        _msgs29.append(_name24.join([_x for _x in _lits if _x]))
_tpcut = 0
for _m in _msgs29:
    assert SUI.text_width(_m, HINFO_FS) <= 2 * HINFO_ROOM * 0.85, "0.3.30: the Home info line fits 2 lines of %d px: %s (%d px)" % (
        HINFO_ROOM, _m, SUI.text_width(_m, HINFO_FS))
    if SUI.text_width(_m, 16) > TP_INFO_ROOM:
        _tpcut += 1
assert _tpcut <= 3, "0.3.30: at most a few over-counted texts reach the end of the Teleport info line (%d)" % _tpcut
# the Right now lines: an AL_MAX-character line in capitals + "  >" fits its button (the panel minus its padding and the button's) at 13 px
assert SUI.text_width(("Abcd Efgh " * 6)[:AL_MAX] + "  >", 13, bold=True) <= HOME_SIDE - 2 * YOU_PAD - 24, "0.3.30: an alert line fits its button"
assert all(SUI.text_width(HOME_TXT[_k] + "  >", 13, bold=True) <= HOME_SIDE - 2 * YOU_PAD - 24 and len(HOME_TXT[_k]) <= AL_MAX for _k in ("AL_MIG", "AL_SET")), \
    "0.3.30: SkyyMenu's own alerts fit"
print("0.3.30 info line: %d px (2 lines of %d px), %d texts checked; Teleport info line %d px (%d cut)" % (HINFO_ROOM, HINFO_FS, len(_msgs29), TP_INFO_ROOM, _tpcut))
_fbtw = dict(zip([f[0] for f in FB], FB_TW))
for _ws in _mode_words["tp"]:
    assert sum(_fbtw[w_] for w_ in _ws) + FB_GAP * (len(_ws) - 1) <= TP_FOOT_W, "0.3.30: the Teleport foot fits"


# ---- the big rows' Python twins (= MenuPage.bigRow / bigTabs, byte for byte - the harness compares the built pages with these)
def big_row_preview(parent, hubs, my, w):
    ap = SUI.Appends([(parent, UI29["BROW"])])
    n = len(hubs)
    bw = (w - BR_GAP * (n - 1)) // n
    icons = bw >= BR_ICON_MIN
    for i, (hid, title, icon) in enumerate(hubs):
        sel = hid == my
        if i > 0:
            ap.append(("SkyyMBRow", "Group { Anchor: (Width: %d); }" % BR_GAP))
        bid = "SkyyMBR%d" % i
        ap.append(("SkyyMBRow", "Button #%s { Anchor: (Width: %d, Height: %d); LayoutMode: Left; Padding: (Horizontal: %d, Vertical: %d); %s }" % (
            bid, bw, BR_H, BR_PAD, BR_PADV, SUI._row_style(sel, "sky"))))
        lw = bw - 2 * BR_PAD
        if icons:
            ap.append((bid, 'ItemIcon { Anchor: (Width: %d, Height: %d); ItemId: "%s"; }' % (BR_ICON, BR_ICON, icon)))
            ap.append((bid, "Group { Anchor: (Width: %d); }" % BR_ICON_GAP))
            lw = lw - BR_ICON - BR_ICON_GAP
        ap.append((bid, 'Label { Anchor: (Width: %d); Text: "%s"; Style: %s; }' % (lw, title, BR_LABSEL if sel else BR_LABN)))
    return ap


def big_tabs_preview(parent, hub, tabs, my, w):
    ap = SUI.Appends([(parent, UI29["BTABS"])])
    n = len(tabs)
    tw = (w - BT_GAP * (n - 1)) // n
    for i, (tid, lab) in enumerate(tabs):
        sel = tid == my
        if i > 0:
            ap.append(("SkyyMBTabs", "Group { Anchor: (Width: %d); }" % BT_GAP))
        bid = "SkyyMBT%d" % i
        ap.append(("SkyyMBTabs", "Button #%s { Anchor: (Width: %d, Height: %d); %s }" % (bid, tw, BT_H, SUI._tab_btn_style(sel, "sky"))))
        stem = "%s_%s" % (hub, tid)
        if stem in TAB_ART:
            ap.append((bid, 'Group { Anchor: (Left: %d, Top: %d, Width: %d, Height: %d); Background: "SkyyHubTabs/%s%s.png"; }' % (
                (tw - BT_ICON) // 2, BT_ICON_TOP, BT_ICON, BT_ICON, stem, "_on" if sel else "")))
        ap.append((bid, 'Label { Anchor: (Left: 0, Top: 0, Width: %d, Height: %d); Padding: (Horizontal: %d); Text: "%s"; Style: %s; }' % (
            tw, BT_H, BT_PAD, lab, BT_LAB)))
    return ap


_ROWHUBS = [(i, t, "Skyy_Menu" if i == "home" else HUB_ICON_ITEM[i]) for i, t in zip(SUI.HUB_ROW_IDS, SUI.HUB_ROW_TITLES)]
for _rw in (HOME_ROW_W, TP_ROW_W):
    _bw = (_rw - BR_GAP * (len(_ROWHUBS) - 1)) // len(_ROWHUBS)
    assert _bw >= BR_ICON_MIN and all(SUI.text_width(_t, BR_LAB_MIN, bold=True) <= _bw - 2 * BR_PAD - BR_ICON - BR_ICON_GAP for _i, _t, _c in _ROWHUBS), \
        "0.3.30: every row-1 title fits its %d px button with the icon" % _bw
_wtabs = [(t, l) for t, o, _m, l, _c in SUI.hub_tabs("world")]
assert (TP_ROW_W - BT_GAP * (len(_wtabs) - 1)) // len(_wtabs) >= BT_MIN and TP_ROW_W // BT_MIN >= len(_wtabs)
for _t, _l in _wtabs:
    assert SUI.text_width(_l, BT_LAB_MIN, bold=True) <= BT_MIN - 2 * BT_PAD, "0.3.30: tab %s fits" % _l
# every look of both pages, checked as pages (markup rules, parents, no duplicate id, proven properties only, kit / tab-icon textures only)
_hp = SUI.Appends(list(HOME_SH.appends))
_hp.extend(big_row_preview("SkyyMHome", _ROWHUBS, "home", HOME_ROW_W))
_hp.append(("SkyyMHome", UI29["HMAIN"]))
_hp.append(("SkyyMHmMain", UI29["HYOU"]))
for _k in ("HYT", "HYN"):
    _hp.append(("SkyyMHmYou", UI29[_k]))
for _mk in UI29_HYL:
    _hp.append(("SkyyMHmYou", _mk))
_hp.append(("SkyyMHmYou", UI29["HYBAR0"] + "136" + UI29["HYBAR1"]))
_hp.append(("SkyyMHmYou", UI29["HYH"]))
_hp.append(("SkyyMHmMain", UI29["HSP16"]))
_hp.append(("SkyyMHmMain", UI29["HMID"]))
for _k in ("HMIDT", "HGAP5", "HGW"):
    _hp.append(("SkyyMHmMid", UI29[_k]))
_hp.append(("SkyyMGW", UI29["HGRID"]))
_hp.append(("SkyyMHmMain", UI29["HSP16"]))
_hp.append(("SkyyMHmMain", UI29["HNOW"]))
_hp.append(("SkyyMHmNow", UI29["HNOWT"]))
for _mk in UI29_HA:
    _hp.append(("SkyyMHmNow", _mk))
_hp.append(("SkyyMHome", UI29["HGAP8"]))
_hp.append(("SkyyMHome", UI29["HFOOT"]))
_hp.append(("SkyyMHmFoot", UI29["HINFO0"] + "400" + UI29["HINFO1"]))
for _mk in UI29_FBH:
    _hp.append(("SkyyMHmFoot", UI29["FSP"]))
    _hp.append(("SkyyMHmFoot", _mk))
SUI.check_page(_hp, "SkyyM")
SUI.assert_proven(_hp, what="Home page")
_hels = SUI.check_sky_paths(_hp)
assert {"Frame", "Header", "HeaderOrnament", "Panel", "CardFrame", "PanelInset", "Row", "Close", "Primary", "Tertiary"} <= set(_hels), "0.3.30: Home uses the sky kit: %s" % _hels
assert SUI.used_height(SUI.Appends([(p_, mk) for p_, mk in _hp if p_ == "SkyyMHome"]), "SkyyMHome") <= HOME_SH.inner_h, "0.3.30: the Home body fits"
_hp2 = SUI.Appends(list(HOME_SH.appends) + [("SkyyMHome", UI29["HMAIN"]), ("SkyyMHmMain", UI29["HNOW"]), ("SkyyMHmNow", UI29["HNOWT"]),
                                            ("SkyyMHmNow", UI29["HNOWNONE"]), ("SkyyMHmMain", UI29["HMID"]), ("SkyyMHmMid", UI29["HGW"]),
                                            ("SkyyMGW", UI29["HGRIDNT"])])
SUI.check_page(_hp2, "SkyyM")
SUI.assert_proven(_hp2, what="Home page (nothing waiting, tooltips off)")
_tp = SUI.Appends(list(TP_SH.appends))
_tp.extend(big_row_preview("SkyyMTpB", _ROWHUBS, "world", TP_ROW_W))
_tp.extend(big_tabs_preview("SkyyMTpB", "world", _wtabs, "teleport", TP_ROW_W))
_tp.append(("SkyyMTpB", UI29["TROW"]))
_tp.append(("SkyyMTpRow", UI29["TLEAD"]))
_tp.append(("SkyyMTpRow", UI29["HGW"]))
_tp.append(("SkyyMGW", UI29["HGRID"]))
_tp.append(("SkyyMTpB", UI29["TGAP"]))
_tp.append(("SkyyMTpB", UI29["TINFO"]))
_tp.append(("SkyyMTpInfo", UI29["TIN"]))
_tp.append(("SkyyMTpInfo", UI29["TID"]))
_tp.append(("SkyyMTpB", UI29["TGAP"]))
_tp.append(("SkyyMTpB", UI29["TFOOT"]))
for _mk in UI29_FBT:
    _tp.append(("SkyyMTpFoot", _mk))
SUI.check_page(_tp, "SkyyM")
SUI.assert_proven(_tp, what="Teleport page")
assert {"Frame_World", "Header", "HeaderOrnament", "PanelInset", "Tab_Selected", "Tab", "Close"} <= set(SUI.check_sky_paths(_tp, tab_icons=True))
assert SUI.used_height(SUI.Appends([(p_, mk) for p_, mk in _tp if p_ == "SkyyMTpB"]), "SkyyMTpB") <= TP_SH.inner_h, "0.3.30: Teleport fits"
for _mk in list(UI29.values()) + UI29_HYL + UI29_HA + UI29_FBH + UI29_FBT:
    assert not re.search(r"(Vertical|Horizontal)Alignment\s*:\s*(Top|Bottom|Left|Right)\b", _mk), "0.3.29: Start / Center / End alignments only"
    for _eid in re.findall(r"#([A-Za-z0-9_]+)\s*\{", _mk):
        assert "_" not in _eid
# every kit 1.6 hub page of SkyyMenu (Home / Teleport draw their own big rows): the bar-less height + the 52 px strip fits 1080p and the
# hub's FULL contract tab list fits (row 1 is in the title bar)
HUB_PAGES = [("stats", ST_SH, "character", "stats"), ("players", MENU_HUB_SH["social"], "social", "players"), ("mods", MENU_HUB_SH["settings"], "settings", "mods"),
             ("settings", STG_HUB_SH, "settings", "settings"), ("setup", ADM_HUB_SH, "settings", "setup")]
HUB_LABEL_FIT = {}
for _t, _sh, _h, _my in HUB_PAGES:
    assert _sh.row and SUI.assert_hub_page(_sh.w, _sh.h - SUI.HUB_BAR_H, old_title_h=0, hub=_h, pad=_sh.pad) == (_sh.w, _sh.h), "0.3.29: %s fits 1080p" % _t
    _tw = SUI.assert_hub_fits(_h, _sh.tabs_w)
    _pp = os.path.commonprefix([_sh.prefix, _sh.body])
    SUI.check_page(_sh.appends, _pp)
    SUI.assert_proven(_sh.appends, what="row shell " + _t)
    _els = SUI.check_sky_paths(_sh.appends)
    assert {"Header", SUI.HUB_FRAME[_h], "Close"} <= set(_els) and not any("HubMenu" in mk for _p, mk in _sh.appends), "0.3.29: %s row shell: %s" % (_t, _els)
    assert any(_sh.prefix + "HubRow" in mk for _p, mk in _sh.appends if _p == _sh.bar), "0.3.29: row 1 sits in the %s title bar" % _t
    assert SUI.assert_hub_row_fits(_sh.row_w)[1], "0.3.29: row 1 shows its icons on %s" % _t
    for _rows in (SUI.hub_tabs(_h), [r for r in SUI.hub_tabs(_h) if r[2] == "SkyyMenu"]):
        _lab = [(t, OWN_LABEL.get(t, l) if m == "SkyyMenu" else l, o) for t, o, m, l, _c in _rows]
        _bar = SUI.hub_bar_preview2(_sh.prefix, _lab, _my, _sh.tabs_w)
        SUI.check_page(SUI.Appends(list(_sh.appends) + list(_bar)), _pp)
        SUI.check_sky_paths(_bar)
        _w1 = SUI.hub_tab_width(_sh.tabs_w, len(_rows))
        for _r in _lab:
            assert SUI.text_width(_r[1], 12, bold=True) <= _w1 - 2 * SUI.HUB_TAB_PAD, "0.3.29: tab %s fits %d px at 12 px" % (_r[1], _w1)
    HUB_LABEL_FIT[_t] = _tw
MH_JAVA = dict((h, MENU_HUB_SH[h].java("b")) for h in MENU_HUB_SH)
HOME_JAVA = HOME_SH.java("b")
TP_JAVA = TP_SH.java("b")
STG_HUB_JAVA = STG_HUB_SH.java("b")
ADM_HUB_JAVA = ADM_HUB_SH.java("b")
ST_HUB_JAVA = SUI.java_hub_build(ST_SH, "stats", cls="@PKG@.HubBar")
STG_HUB_BUILD = SUI.java_hub_build(STG_HUB_SH, "settings", cls="@PKG@.HubBar", uuid="u")
ADM_HUB_BUILD = SUI.java_hub_build(ADM_HUB_SH, "setup", cls="@PKG@.HubBar", uuid="me()")
MH_BUILD = '@PKG@.HubBar.build2(b, ev, "SkyyMenuH", hubName(), hubTab(), %d, this.playerRef.getUuid(), %d, %d);' % (
    GW, SUI.HUB_PART_ROW | SUI.HUB_PART_CLOSE, MENU_HUB_SH["social"].row_w)
assert ST_HUB_JAVA.startswith('@PKG@.HubBar.build2(b, ev, "SkyyStatF", "character", "stats", 1066,') and ST_HUB_JAVA.endswith(", 6, %d);" % (ST_W - 50))
assert "HubRow" not in HOME_JAVA + TP_JAVA and "HubTabs" not in HOME_JAVA + TP_JAVA and "SkyyMHmHubClose" in HOME_JAVA and "SkyyMTpHubClose" in TP_JAVA
print("0.3.30 pages: Home %d x %d (grid %d x %d of %d px slots, sides %d px, centre slot at page centre %+d / %+d = 0.3.28 slot 13), Teleport %d x %d, row 1 %d px buttons, %s" % (
    HOME_W, HOME_H, HG_W, HG_H, SLOT30, HOME_SIDE, HOME_C[0], HOME_C[1], TP_W, TP_H, (HOME_ROW_W - BR_GAP * 7) // 8,
    ", ".join("%s %d px tabs" % (t, HUB_LABEL_FIT[t]) for t, _s, _h, _m in HUB_PAGES)))
'''


def JAVA30():
    # ------------------------------------------------------------------------------------------------------------ texts
    rep('''    "AL_MIG": "Menu updated: hubs replaced old tiles", "AL_SET": "Your settings could not be read",
}''', '''    "AL_MIG": "Menu updated: hubs replaced old tiles", "AL_SET": "Your settings could not be read",
    "HT_NOW_NONE": "Nothing waiting",                                 # 0.3.30: the Right now panel with nothing to do
    "AL_SPILL": "Some shortcuts did not fit",                         # 0.3.30: the 5 x 5 update had more pins than slots
}''')
    rep('''    if _k in ("HT_YOU_TITLE", "HT_YOU_HINT", "HT_NOW_TITLE"):   # baked into the UI29 markup at build time; never read at runtime''',
        '''    if _k in ("HT_YOU_TITLE", "HT_YOU_HINT", "HT_NOW_TITLE", "HT_NOW_NONE"):   # baked into the UI29 markup at build time; never read at runtime''')

    # ------------------------------------------------------------------------------------------------------------ MenuLayout
    rep('''# ================= 0.3.29 MenuLayout: every player's HOME shortcut grid + TELEPORT grid (Skyy 2026-10-15, the unified menu) =================
# A grid = String[HG_N] of shortcut keys (null = an empty slot; MenuData.HG_N = 35, 7 x 5).''',
        '''# ================= 0.3.29 MenuLayout: every player's HOME shortcut grid + TELEPORT grid (Skyy 2026-10-15, the unified menu) =================
# 0.3.30: a grid = String[HG_N] of shortcut keys, 5 x 5 (25). The files keep 0.3.29's 7 x 5 numbering (G7: slot = row * 7 + column, the
# 5 x 5 grid = columns 1 - 5); fold() reads a 7 x 5 line set into the 5 x 5 grid (columns 0 / 6 move to the nearest free slot, the same
# page twice is kept once), lines() writes it back in the 7 x 5 numbering. A record grows two elements: [6] Boolean "the 0.3.30 update
# changed this grid and is not written yet", [7] String "<n>|<keys>" = pins that found no free slot (they wait in + Add).
# 0.3.29: A grid = String[HG_N] of shortcut keys (null = an empty slot).''')
    rep('''F(lay, "public static volatile int MIGRATIONS;")''', '''F(lay, "public static volatile int MIGRATIONS;")
F(lay, "public static volatile int FOLDS;")            # 0.3.30: grids the 5 x 5 update changed at their first read
F(lay, "public static final java.util.concurrent.ConcurrentHashMap SPILL = new java.util.concurrent.ConcurrentHashMap();")   # 0.3.30: uuid -> "<n>|<keys>"''')
    rep('''M(lay, "public static String[] blank() { return new String[@PKG@.MenuData.HG_N]; }")''',
        '''M(lay, "public static String[] blank() { return new String[@PKG@.MenuData.HG_N]; }")
M(lay, "public static String[] blank7() { return new String[@PKG@.MenuData.G7_N]; }")   # 0.3.30: the 7 x 5 numbering of the files
M(lay, "public static int to7(int s) { return (s / @PKG@.MenuData.HG_COLS) * @PKG@.MenuData.G7_COLS + s % @PKG@.MenuData.HG_COLS + @PKG@.MenuData.G7_OFF; }")
M(lay, "public static Object el(Object[] r, int i) { return r != null && i >= 0 && i < r.length ? r[i] : null; }")''')
    # slotLines reads the 7 x 5 numbering
    rep('''# g.<slot> / t.<slot> lines -> a grid; a bad key, a slot outside 0 - 34 or a key already on the grid is skipped
M(lay, r"""
public static String[] slotLines(java.util.Properties p, String pre, boolean tp) {
  String[] g = blank();''', '''# g.<slot> / t.<slot> lines -> a 7 x 5 grid (0.3.30: fold() makes it 5 x 5); a bad key, a slot outside 0 - 34 or a key already on it is skipped
M(lay, r"""
public static String[] slotLines(java.util.Properties p, String pre, boolean tp) {
  String[] g = blank7();''')
    # mapSlot / placeOutside / migrate on the 7 x 5 grid, then fold
    rep('''  int r = s / @PKG@.MenuData.OLD_COLS - @PKG@.MenuData.OLD_CR + @PKG@.MenuData.HG_CR;
  int c = s % @PKG@.MenuData.OLD_COLS - @PKG@.MenuData.OLD_CC + @PKG@.MenuData.HG_CC;
  if (r < 0 || r >= @PKG@.MenuData.HG_ROWS || c < 0 || c >= @PKG@.MenuData.HG_COLS) return -1;
  return r * @PKG@.MenuData.HG_COLS + c;''', '''  int r = s / @PKG@.MenuData.OLD_COLS - @PKG@.MenuData.OLD_CR + @PKG@.MenuData.G7_CR;
  int c = s % @PKG@.MenuData.OLD_COLS - @PKG@.MenuData.OLD_CC + @PKG@.MenuData.G7_CC;
  if (r < 0 || r >= @PKG@.MenuData.G7_ROWS || c < 0 || c >= @PKG@.MenuData.G7_COLS) return -1;
  return r * @PKG@.MenuData.G7_COLS + c;''')
    rep('''    int r = s / @PKG@.MenuData.OLD_COLS - @PKG@.MenuData.OLD_CR + @PKG@.MenuData.HG_CR;
    int c = s % @PKG@.MenuData.OLD_COLS - @PKG@.MenuData.OLD_CC + @PKG@.MenuData.HG_CC;
    if (r < 0) r = 0;
    if (r > @PKG@.MenuData.HG_ROWS - 1) r = @PKG@.MenuData.HG_ROWS - 1;
    if (c < 0) c = 0;
    if (c > @PKG@.MenuData.HG_COLS - 1) c = @PKG@.MenuData.HG_COLS - 1;
    int best = -1;
    int bd = 0;
    for (int x = 0; x < g.length; x++) {
      if (g[x] != null) continue;
      int dr = x / @PKG@.MenuData.HG_COLS - r;
      int dc = x % @PKG@.MenuData.HG_COLS - c;''', '''    int r = s / @PKG@.MenuData.OLD_COLS - @PKG@.MenuData.OLD_CR + @PKG@.MenuData.G7_CR;
    int c = s % @PKG@.MenuData.OLD_COLS - @PKG@.MenuData.OLD_CC + @PKG@.MenuData.G7_CC;
    if (r < 0) r = 0;
    if (r > @PKG@.MenuData.G7_ROWS - 1) r = @PKG@.MenuData.G7_ROWS - 1;
    if (c < 0) c = 0;
    if (c > @PKG@.MenuData.G7_COLS - 1) c = @PKG@.MenuData.G7_COLS - 1;
    int best = -1;
    int bd = 0;
    for (int x = 0; x < g.length; x++) {
      if (g[x] != null) continue;
      int dr = x / @PKG@.MenuData.G7_COLS - r;
      int dc = x % @PKG@.MenuData.G7_COLS - c;''')
    rep('''M(lay, r"""
public static String[] migrate(int[] old, boolean hubs) {
  String[] g = blank();''', '''M(lay, r"""
public static String[] migrate7(int[] old, boolean hubs) {
  String[] g = blank7();''')
    # twin -> canon / rank / hasSame / fold / migrate
    _tw = block('''# fix round 2: an old tile and the hub tab it IS (MenuData.MIG_TAB) are the SAME page''', '''public static boolean hasSame(String[] g, String k) {
  return has(g, k) || has(g, twin(k));
}""")''')
    rep(_tw, r'''# 0.3.30: ONE ENTRY PER PAGE (Skyy 2026-10-16 "make sure we dont have any duplicates"). canon() = the page a key opens: an old tile ->
# the hub tab it IS (MenuData.MIG_TAB, fix round 2's twin), a hub with a DEFAULT tab (Character -> skills, World -> teleport) -> that tab,
# anything else -> itself. + Add lists a page once and a grid never holds it twice (hasSame). rank(): which key of a page a saved grid keeps
# - the tab (0), else the old tile (1), else the hub (2).
M(lay, r"""
public static String canon(String k) {
  if (k == null) return null;
  if (k.startsWith("tile:")) {
    int i = keyIndex(k.substring(5));
    if (i >= 0 && @PKG@.MenuData.MIG_TAB[i].length() > 0) return "tab:" + @PKG@.MenuData.MIG_TAB[i];
    return k;
  }
  if (k.startsWith("hub:")) {
    int h = hubIdx(k.substring(4));
    if (h >= 0 && @PKG@.MenuData.HUB_DEFTAB[h].length() > 0) return "tab:" + @PKG@.MenuData.HUB_ID[h] + ":" + @PKG@.MenuData.HUB_DEFTAB[h];
  }
  return k;
}""")
M(lay, r"""
public static int rank(String k) {
  if (k == null) return 9;
  if (k.equals(canon(k))) return 0;
  return k.startsWith("tile:") ? 1 : 2;
}""")
M(lay, r"""
public static boolean hasSame(String[] g, String k) {
  if (g == null || k == null) return false;
  String c = canon(k);
  for (int i = 0; i < g.length; i++) { if (g[i] != null && c.equals(canon(g[i]))) return true; }
  return false;
}""")
# + Add's list: k unless its page is listed already (cs = the pages listed so far)
M(lay, r"""
public static void addOnce(java.util.ArrayList out, java.util.ArrayList cs, String k) {
  String c = canon(k);
  if (c == null || cs.contains(c)) return;
  cs.add(c);
  out.add(k);
}""")
# THE 5 x 5 FOLD (0.3.30): a 7 x 5 grid (the files' numbering) -> Object[]{ String[25] grid, Boolean changed, String "<n>|<keys>" or null }.
# Columns 1 - 5 keep their place; the same page twice keeps its best key (rank, ties = reading order; Home only); a pin in column 0 / 6
# goes to the free slot nearest its spot pulled inside (ties = reading order; the pins in reading order) unless its page is on the grid
# already (then the more exact of the two keys stays in that slot); no free slot = it waits in + Add (counted, named in [2]). changed = anything moved or merged.
M(lay, r"""
public static Object[] fold(String[] g7, boolean tp) {
  String[] g = blank();
  boolean ch = false;
  java.util.ArrayList over = new java.util.ArrayList();
  int cols = @PKG@.MenuData.HG_COLS;
  for (int s = 0; g7 != null && s < g7.length && s < @PKG@.MenuData.G7_N; s++) {
    if (g7[s] == null) continue;
    int r = s / @PKG@.MenuData.G7_COLS;
    int c = s % @PKG@.MenuData.G7_COLS - @PKG@.MenuData.G7_OFF;
    if (c >= 0 && c < cols && r < @PKG@.MenuData.HG_ROWS) g[r * cols + c] = g7[s];
    else over.add(Integer.valueOf(s));
  }
  if (!tp) {
    for (int i = 0; i < g.length; i++) {
      if (g[i] == null) continue;
      String ci = canon(g[i]);
      for (int j = 0; j < g.length; j++) {
        if (j == i || g[j] == null || !ci.equals(canon(g[j]))) continue;
        int ri = rank(g[i]);
        int rj = rank(g[j]);
        if (rj < ri || (rj == ri && j < i)) { g[i] = null; ch = true; break; }
      }
    }
  }
  int ns = 0;
  StringBuilder sp = new StringBuilder();
  for (int k = 0; k < over.size(); k++) {
    int s = ((Integer) over.get(k)).intValue();
    String key = g7[s];
    ch = true;
    if (tp ? has(g, key) : hasSame(g, key)) {
      if (!tp) {   // the same page is on the grid already: the more exact key stays (in that slot)
        for (int j = 0; j < g.length; j++) { if (g[j] != null && canon(g[j]).equals(canon(key)) && rank(key) < rank(g[j])) g[j] = key; }
      }
      continue;
    }
    int r = s / @PKG@.MenuData.G7_COLS;
    int c = s % @PKG@.MenuData.G7_COLS - @PKG@.MenuData.G7_OFF;
    if (c < 0) c = 0;
    if (c > cols - 1) c = cols - 1;
    if (r > @PKG@.MenuData.HG_ROWS - 1) r = @PKG@.MenuData.HG_ROWS - 1;
    int best = -1;
    int bd = 0;
    for (int x = 0; x < g.length; x++) {
      if (g[x] != null) continue;
      int dr = x / cols - r;
      int dc = x % cols - c;
      int d = dr * dr + dc * dc;
      if (best < 0 || d < bd) { best = x; bd = d; }
    }
    if (best < 0) {
      ns = ns + 1;
      if (sp.length() > 0) sp.append(',');
      sp.append(key);
      continue;
    }
    g[best] = key;
  }
  return new Object[] { g, Boolean.valueOf(ch), ns == 0 ? null : ns + "|" + sp.toString() };
}""")
# fix 2: both grids' spill lists in one "<n>|<keys>" (Home first, then Teleport) - the log line, the chat note and Right now name them all
M(lay, r"""
public static String joinSpill(String a, String b) {
  if (a == null) return b;
  if (b == null) return a;
  int i = a.indexOf('|');
  int j = b.indexOf('|');
  int n = 0;
  try { n = Integer.parseInt(a.substring(0, i)) + Integer.parseInt(b.substring(0, j)); } catch (Throwable t) { n = 0; }
  return n + "|" + a.substring(i + 1) + "," + b.substring(j + 1);
}""")
# the 0.3.28 update (migrate7, the 7 x 5 grid 0.3.29 made) then the 5 x 5 fold
M(lay, r"""
public static String[] migrate(int[] old, boolean hubs) {
  return (String[]) fold(migrate7(old, hubs), false)[0];
}""")''')
    # parse: fold + the two new record elements
    rep('''  if (hm == null) {
    if (old == null) return null;
    return new Object[] { migrate(old, true), null, oldLine(old), compatText(old), Boolean.TRUE, nm };
  }
  String[] home = null;
  if ("1".equals(hm.trim())) home = slotLines(p, "g.", false);
  String[] tp = null;
  if ("1".equals(p.getProperty("_tp", "").trim())) tp = slotLines(p, "t.", true);''', '''  if (hm == null) {
    if (old == null) return null;
    Object[] f0 = fold(migrate7(old, true), false);
    return new Object[] { f0[0], null, oldLine(old), compatText(old), Boolean.TRUE, nm, Boolean.FALSE, f0[2] };
  }
  String[] home = null;
  Object[] fh = null;
  if ("1".equals(hm.trim())) { fh = fold(slotLines(p, "g.", false), false); home = (String[]) fh[0]; }
  String[] tp = null;
  Object[] ft = null;
  if ("1".equals(p.getProperty("_tp", "").trim())) { ft = fold(slotLines(p, "t.", true), true); tp = (String[]) ft[0]; }
  boolean ch = (fh != null && Boolean.TRUE.equals(fh[1])) || (ft != null && Boolean.TRUE.equals(ft[1]));
  String sp = joinSpill(fh != null ? (String) fh[2] : null, ft != null ? (String) ft[2] : null);   // fix 2: Home + Teleport''')
    rep('''  return new Object[] { home, tp, ol, ct, Boolean.FALSE, nm };
}""")''', '''  return new Object[] { home, tp, ol, ct, Boolean.FALSE, nm, Boolean.valueOf(ch), sp };
}""")''')
    # lines() in the 7 x 5 numbering; tail() carries the run-once marker
    rep('''  for (int s = 0; s < g.length; s++) { if (g[s] != null) sb.append(pre).append(s).append('=').append(g[s]).append('\\n'); }''',
        '''  for (int s = 0; s < g.length; s++) { if (g[s] != null) sb.append(pre).append(to7(s)).append('=').append(g[s]).append('\\n'); }   // 0.3.30: 7 x 5 numbering''')
    rep('''  if (r[2] != null) sb.append("_old=").append((String) r[2]).append('\\n');
  lines(sb, "g.", (String[]) r[0]);''', '''  if (r[2] != null) sb.append("_old=").append((String) r[2]).append('\\n');
  sb.append("_g5=1\\n");   // 0.3.30: the 5 x 5 run-once marker
  lines(sb, "g.", (String[]) r[0]);''')
    rep('''    if (l.startsWith("g.") || l.startsWith("t.") || l.startsWith("_home") || l.startsWith("_tp") || l.startsWith("_old")) return true;''',
        '''    if (l.startsWith("g.") || l.startsWith("t.") || l.startsWith("_home") || l.startsWith("_tp") || l.startsWith("_old") || l.startsWith("_g5")) return true;''')
    # bytesFor: the 0.3.30 append (only the lines that change)
    _bf = block('''M(lay, r"""
public static byte[] bytesFor(byte[] was, boolean mig, Object[] r, String head) throws java.io.IOException {''', '''  String t = text(r, head);
  if (!nl.equals("\\n")) t = t.replace("\\n", nl);
  return t.getBytes("UTF-8");
}""")''')
    rep(_bf, r'''# 0.3.30: the 5 x 5 update's lines for one grid: every 7 x 5 slot whose value changes (a slot that loses its pin: "<pre><slot>=" - an empty
# value is no key for 0.3.29 or 0.3.30). Later lines win in a properties file, so 0.3.29 (a rollback) reads the same 5 x 5 grid.
M(lay, r"""
public static void diff(StringBuilder sb, java.util.Properties p, String pre, String[] g) {
  if (g == null) return;
  String[] n7 = blank7();
  for (int s = 0; s < g.length; s++) { if (g[s] != null) n7[to7(s)] = g[s]; }
  for (int s = 0; s < n7.length; s++) {
    String ov = p.getProperty(pre + s);
    if (ov != null) ov = ov.trim();
    if (n7[s] == null) { if (ov != null && ov.length() > 0 && okKey(ov, pre.equals("t."))) sb.append(pre).append(s).append("=\n"); }   // fix: an unknown key stays as it was
    else if (!n7[s].equals(ov)) sb.append(pre).append(s).append('=').append(n7[s]).append('\n');
  }
}""")
M(lay, r"""
public static String foldTail(String old, Object[] r) throws java.io.IOException {
  java.util.Properties p = new java.util.Properties();
  p.load(new java.io.StringReader(old));
  StringBuilder sb = new StringBuilder();
  sb.append("# 0.3.30: the shortcuts are a 5 x 5 grid (columns 1 - 5 of the numbering above): pins from columns 0 and 6 moved in, a page held twice kept once - every line above is kept as it was\n");
  sb.append("_g5=1\n");
  diff(sb, p, "g.", (String[]) r[0]);
  diff(sb, p, "t.", (String[]) r[1]);
  return sb.toString();
}""")
M(lay, r"""
public static byte[] appendTo(byte[] was, String add, String nl) throws java.io.IOException {
  if (was.length > 0 && was[was.length - 1] != (byte) 10) add = "\n" + add;
  if (!nl.equals("\n")) add = add.replace("\n", nl);
  byte[] tb = add.getBytes("UTF-8");
  byte[] out = new byte[was.length + tb.length];
  System.arraycopy(was, 0, out, 0, was.length);
  System.arraycopy(tb, 0, out, was.length, tb.length);
  return out;
}""")
# the bytes to write. THE ONE-TIME UPDATES (PROJECT-RULES 4 "keep the file's bytes and line endings"): the old file's EXACT bytes + the new
# lines appended in its own line ending - 0.3.29's (a 0.3.28 layout: every line of the record) and 0.3.30's (a 0.3.29 layout whose grid
# the 5 x 5 fold changed: only the lines that change). Any later save: the whole file in the file's own line ending (CRLF stays CRLF).
M(lay, r"""
public static byte[] bytesFor(byte[] was, boolean mig, boolean fold, Object[] r, String head) throws java.io.IOException {
  String old = null;
  if (was != null) old = new String(was, "UTF-8");
  String nl = (old != null && old.indexOf("\r\n") >= 0) ? "\r\n" : "\n";
  if (mig && old != null && !hasNewLines(old))
    return appendTo(was, "# 0.3.29: the Home shortcuts (the one-time update - every line above is the 0.3.28 layout exactly as it was)\n" + tail(r), nl);
  if (fold && old != null) return appendTo(was, foldTail(old, r), nl);
  String t = text(r, head);
  if (!nl.equals("\n")) t = t.replace("\n", nl);
  return t.getBytes("UTF-8");
}""")''')
    rep('''    history(f, what, "before the 0.3.29 Home shortcuts update (the old layout also stays in the file)");''',
        '''    history(f, what, "before the SkyyMenu shortcuts update (the old layout also stays in the file)");''')
    rep('''M(lay, r"""
public static void finishMig(String k, Object[] r) {
  SNAPPED.put(k, Boolean.TRUE);
  HFAIL.remove(k);
  logMigration(k, r);
}""")''', '''# 0.3.30: the 5 x 5 update's config-changes.log line (status done: the old lines stay in the file above the appended ones; a rollback to
# 0.3.29 reads the same grid - there is nothing to undo in game, the pins only moved inside the grid or a page held twice was kept once)
M(lay, r"""
public static void logFold(String k, Object[] r) {
  try {
    @PKG@.CfgLog.add(null, "SkyyMenu update", "update", "menu.layout[" + k + "]", "7 x 5",
      "(0.3.30 the 5 x 5 shortcut grid: " + summary(r[0]) + (el(r, 7) != null ? "; no free slot (they wait in Edit shortcuts, + Add): " + el(r, 7) : "")
      + " - undo: the old lines stay in the file above the new ones, and the History copy made just before holds the whole old file)", "done");
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not log the menu layout update of " + k + " in config-changes.log: " + t); }
}""")
M(lay, r"""
public static void finishMig(String k, Object[] r, boolean mig) {
  SNAPPED.put(k, Boolean.TRUE);
  HFAIL.remove(k);
  if (mig) logMigration(k, r); else logFold(k, r);
}""")''')
    rep('''  boolean mig = Boolean.TRUE.equals(r[4]) && !Boolean.TRUE.equals(SNAPPED.get(k));
  if (mig) snapFirst(k, f, what);
  byte[] was = readWas(f);
  if (empty(r)) java.nio.file.Files.deleteIfExists(f);''', '''  boolean mig = Boolean.TRUE.equals(r[4]) && !Boolean.TRUE.equals(SNAPPED.get(k));
  boolean fold = Boolean.TRUE.equals(el(r, 6)) && !Boolean.TRUE.equals(SNAPPED.get(k));   // 0.3.30
  if (mig || fold) snapFirst(k, f, what);
  byte[] was = readWas(f);
  if (empty(r)) java.nio.file.Files.deleteIfExists(f);''')
    rep('''      + "# g.<slot> = the Home grid, t.<slot> = the Teleport grid (7 x 5, slot = row * 7 + column, 17 = the centre). _home / _tp 0 = the default.\\n"''',
        '''      + "# g.<slot> = the Home grid, t.<slot> = the Teleport grid: 5 x 5 = columns 1 - 5 of slot = row * 7 + column (17 = the centre). _home / _tp 0 = the default.\\n"''')
    rep('''    @PKG@.MenuUtil.atomicWrite(f, bytesFor(was, mig, r, head));
  }
  if (mig) finishMig(k, r);
}""")''', '''    @PKG@.MenuUtil.atomicWrite(f, bytesFor(was, mig, fold, r, head));
  }
  if (mig || fold) finishMig(k, r, mig);
}""")''')
    rep('''  boolean mig = Boolean.TRUE.equals(d[4]) && !Boolean.TRUE.equals(SNAPPED.get(DEF_KEY));
  if (mig) snapFirst(DEF_KEY, f, "layout-default.properties");
  byte[] was = readWas(f);
  String head = "# SkyyMenu: the SERVER DEFAULT shortcuts - every player without their own gets them. g.<slot> = Home, t.<slot> = Teleport (7 x 5).\\n"
    + "# Set in game by an admin: Home - Edit shortcuts - Set default. Delete this file = the standard shortcuts.\\n";
  @PKG@.MenuUtil.atomicWrite(f, bytesFor(was, mig, d, head));
  if (mig) finishMig(DEF_KEY, d);''', '''  boolean mig = Boolean.TRUE.equals(d[4]) && !Boolean.TRUE.equals(SNAPPED.get(DEF_KEY));
  boolean fold = Boolean.TRUE.equals(el(d, 6)) && !Boolean.TRUE.equals(SNAPPED.get(DEF_KEY));   // 0.3.30
  if (mig || fold) snapFirst(DEF_KEY, f, "layout-default.properties");
  byte[] was = readWas(f);
  String head = "# SkyyMenu: the SERVER DEFAULT shortcuts - every player without their own gets them. g.<slot> = Home, t.<slot> = Teleport (5 x 5 = columns 1 - 5 of slot = row * 7 + column).\\n"
    + "# Set in game by an admin: Home - Edit shortcuts - Set default. Delete this file = the standard shortcuts.\\n";
  @PKG@.MenuUtil.atomicWrite(f, bytesFor(was, mig, fold, d, head));
  if (mig || fold) finishMig(DEF_KEY, d, mig);''')
    # own(): the 0.3.30 update at the first read too
    rep('''  if ((r instanceof Object[]) && Boolean.TRUE.equals(((Object[]) r)[4])) {
    SNAPPED.remove(k);    // fix round 2: a 0.3.28 file read again (an admin restored a .bak by hand) = a NEW update: History copy + append again
    HFAIL.remove(k);
    MIGRATED.put(k, Boolean.TRUE);
    MIGRATIONS = MIGRATIONS + 1;
    @PKG@.MenuUtil.info("menu layout layouts/" + k + ".properties: the 0.3.29 one-time update - hubs replace the old tiles they cover, the other tiles keep their place, Hover Tooltips goes (Settings has it); the old layout stays in the file (_old + the 0.3.28 lines) and a History copy goes to config-history first");
    saveSoon(k);
  }''', '''  if (r instanceof Object[] && el((Object[]) r, 7) != null) {   // 0.3.30: pins that found no free slot in the 5 x 5 grid - the player is told once
    SPILL.putIfAbsent(k, el((Object[]) r, 7));   // fix: a second read never re-arms the one-time chat note
    @PKG@.MenuUtil.info("menu layout layouts/" + k + ".properties: " + el((Object[]) r, 7) + " - more shortcuts than the 25 slots; they wait in Edit shortcuts, + Add");
  }
  boolean fd = (r instanceof Object[]) && Boolean.TRUE.equals(el((Object[]) r, 6));
  if ((r instanceof Object[]) && (Boolean.TRUE.equals(((Object[]) r)[4]) || fd)) {
    SNAPPED.remove(k);    // fix round 2: a 0.3.28 file read again (an admin restored a .bak by hand) = a NEW update: History copy + append again
    HFAIL.remove(k);
    if (Boolean.TRUE.equals(((Object[]) r)[4])) {
      MIGRATED.put(k, Boolean.TRUE);
      MIGRATIONS = MIGRATIONS + 1;
      @PKG@.MenuUtil.info("menu layout layouts/" + k + ".properties: the 0.3.29 one-time update - hubs replace the old tiles they cover, the other tiles keep their place, Hover Tooltips goes (Settings has it); the old layout stays in the file (_old + the 0.3.28 lines) and a History copy goes to config-history first");
    } else {
      FOLDS = FOLDS + 1;
      @PKG@.MenuUtil.info("menu layout layouts/" + k + ".properties: the 0.3.30 one-time update - the 5 x 5 shortcut grid (pins of columns 0 and 6 moved in, a page held twice kept once): " + summary(((Object[]) r)[0]) + "; a History copy goes to config-history first, the old lines stay in the file");
    }
    saveSoon(k);
  }''')
    rep('''  Object[] nx = new Object[] { migrate(parseOldLine((String) d[2]), true), d[1], d[2], d[3], d[4], d[5] };''',
        '''  Object[] nx = new Object[] { migrate(parseOldLine((String) d[2]), true), d[1], d[2], d[3], d[4], d[5], el(d, 6), el(d, 7) };''')
    rep('''  Object[] nx = new Object[] { null, null, null, null, Boolean.FALSE, null };
  if (o instanceof Object[]) {''', '''  Object[] nx = new Object[] { null, null, null, null, Boolean.FALSE, null, Boolean.FALSE, null };
  if (o instanceof Object[]) {''')
    rep('''  Object[] nx = new Object[] { null, null, null, null, Boolean.FALSE, null };
  if (d != null) { for (int i = 0; i < 5 && i < d.length; i++) nx[i] = d[i]; }''', '''  Object[] nx = new Object[] { null, null, null, null, Boolean.FALSE, null, Boolean.FALSE, null };
  if (d != null) { for (int i = 0; i < 5 && i < d.length; i++) nx[i] = d[i]; nx[6] = el(d, 6) == null ? Boolean.FALSE : el(d, 6); }''')
    rep('''  Object[] nx = new Object[] { d[0], d[1], d[2], d[3], d[4], null };''', '''  Object[] nx = new Object[] { d[0], d[1], d[2], d[3], d[4], null, el(d, 6) == null ? Boolean.FALSE : el(d, 6), null };''')
    rep('''  if (r instanceof Object[]) {
    DEF = (Object[]) r;
    if (Boolean.TRUE.equals(DEF[4])) {''', '''  if (r instanceof Object[]) {
    DEF = (Object[]) r;
    if (!Boolean.TRUE.equals(DEF[4]) && Boolean.TRUE.equals(el(DEF, 6))) {   // 0.3.30: the server default's 5 x 5 update (written once)
      SNAPPED.remove(DEF_KEY);
      HFAIL.remove(DEF_KEY);
      FOLDS = FOLDS + 1;
      @PKG@.MenuUtil.info("menu layout layout-default.properties: the 0.3.30 one-time update of the server default - the 5 x 5 grid: " + summary(DEF[0]));
      saveSoon(DEF_KEY);
    }
    if (Boolean.TRUE.equals(DEF[4])) {''')
    rep('''  java.util.ArrayList ms = new java.util.ArrayList(MIGRATED.keySet());
  for (int i = 0; i < ms.size(); i++) { if (!onlineK.contains(ms.get(i))) MIGRATED.remove(ms.get(i)); }''', '''  java.util.ArrayList ms = new java.util.ArrayList(MIGRATED.keySet());
  for (int i = 0; i < ms.size(); i++) { if (!onlineK.contains(ms.get(i))) MIGRATED.remove(ms.get(i)); }
  java.util.ArrayList sps = new java.util.ArrayList(SPILL.keySet());
  for (int i = 0; i < sps.size(); i++) { if (!onlineK.contains(sps.get(i))) SPILL.remove(sps.get(i)); }''')

    # ------------------------------------------------------------------------------------------------------------ MenuPage: Home / Teleport
    rep('''public static String tabIcon(String h, String t) {
  String k = h + ":" + t;
  for (int i = 0; i < @PKG@.MenuData.E_KEY.length; i++) { if (@PKG@.MenuData.MIG_TAB[i].equals(k)) return @PKG@.MenuData.E_ICON[i]; }''',
        '''public static String tabIcon(String h, String t) {
  String k = h + ":" + t;
  for (int i = 0; i < @PKG@.MenuData.TAB_KEY.length; i++) { if (@PKG@.MenuData.TAB_KEY[i].equals(k)) return @PKG@.MenuData.TAB_ICON[i]; }   // 0.3.30''')
    rep('''    String body = @PKG@.MenuData.HUB_BLURB[hi] + "\\n" + (t.isEmpty() ? @PKG@.MenuData.HUB_SOON[hi] : "Tabs: " + sb.toString()) + "\\nCommand: /" + @PKG@.MenuData.HUB_CMD[hi];''',
        '''    String dt = @PKG@.MenuData.HUB_DEFTAB[hi];
    String body = @PKG@.MenuData.HUB_BLURB[hi] + "\\n" + (t.isEmpty() ? @PKG@.MenuData.HUB_SOON[hi] : "Tabs: " + sb.toString())
      + (dt.length() > 0 ? "\\nOpens on its " + dt.substring(0, 1).toUpperCase() + dt.substring(1) + " page." : "\\nOpens the page you used last.") + "\\nCommand: /" + @PKG@.MenuData.HUB_CMD[hi];''')
    _cand = block('''  if (home) {
    for (int i = 0; i < @PKG@.MenuData.HUB_ID.length; i++) out.add("hub:" + @PKG@.MenuData.HUB_ID[i]);''', '''      if (l[5].equals("ok") || l[5].equals("dim")) out.add("tile:" + @PKG@.MenuData.E_KEY[i]);
    }
  }''')
    rep(_cand, '''  if (home) {
    // 0.3.30: one entry per page (MenuLayout.canon): a hub whose default tab is shown here is listed as that TAB (Teleport, Skills - the
    // key a saved grid keeps too), then every other hub, every tab, every old tile that is not one of them
    java.util.ArrayList cs = new java.util.ArrayList();
    java.util.ArrayList tk = new java.util.ArrayList();
    for (int i = 0; i < @PKG@.MenuData.HUB_ID.length; i++) {
      java.util.ArrayList t = @PKG@.HubBar.tabs(@PKG@.MenuData.HUB_ID[i], me);
      for (int j = 0; j < t.size(); j++) tk.add("tab:" + @PKG@.MenuData.HUB_ID[i] + ":" + (String) ((Object[]) t.get(j))[0]);
    }
    for (int i = 0; i < @PKG@.MenuData.HUB_ID.length; i++) {
      String hk = "hub:" + @PKG@.MenuData.HUB_ID[i];
      String c = @PKG@.MenuLayout.canon(hk);
      if (!c.equals(hk) && tk.contains(c)) continue;
      @PKG@.MenuLayout.addOnce(out, cs, hk);
    }
    for (int i = 0; i < tk.size(); i++) @PKG@.MenuLayout.addOnce(out, cs, (String) tk.get(i));
    for (int i = 0; i < @PKG@.MenuData.E_VIEW.length; i++) {
      if (!@PKG@.MenuLayout.isMain(i) || "-".equals(@PKG@.MenuData.MIG[i])) continue;
      String[] l = tileLook(i, admin);
      if (l[5].equals("ok") || l[5].equals("dim")) @PKG@.MenuLayout.addOnce(out, cs, "tile:" + @PKG@.MenuData.E_KEY[i]);
    }
  }''')
    # Right now (quest:fn:hud, mystery bags, home:alert:*) + the big rows
    rep('''M(page, r"""
public int youLine(@UCB@ b, int n, String text) {''', '''# 0.3.30 RIGHT NOW rows (research/Unified-Menu-Plan.md section 2; Skyy 2026-10-16 "the menu is missing this right now section from the
# design."): from existing bridges only, read while Home is drawn (world thread, no ticking). quest:fn:hud (SkyyQuests: Object[]{ title,
# "3 / 24", then per shown task name, progress, frac, where, dir, Boolean done }) -> the first undone task; all shown tasks done = claim.
M(page, r"""
public static String questLine(java.util.UUID u) {
  Object f = @PKG@.MenuUtil.bridge().get("quest:fn:hud");
  if (u == null || !(f instanceof java.util.function.Function)) return null;
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(u); }
  catch (Throwable t) {
    if (@PKG@.MenuData.TILE_WARNED.putIfAbsent("quest:fn:hud", "quest:fn:hud") == null) @PKG@.MenuUtil.warn("quest:fn:hud failed (the Right now quest line is left out): " + t);
    return null;
  }
  if (!(r instanceof Object[])) return null;
  Object[] a = (Object[]) r;
  boolean any = false;
  for (int i = 2; i + 5 < a.length; i += 6) {
    any = true;
    if (Boolean.TRUE.equals(a[i + 5])) continue;
    String nm = (a[i] instanceof String) ? ((String) a[i]).trim() : "";
    String pg = (a[i + 1] instanceof String) ? ((String) a[i + 1]).trim() : "";
    if (nm.length() == 0) continue;
    return @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe("Quest: " + nm + (pg.length() > 0 ? " " + pg : "")), @PKG@.MenuData.AL_MAX);
  }
  return any ? "Quest done - claim it" : null;
}""")
# SkyyGear's mystery bags (Skyy_Unid_Bag_<Rarity>) in the player's inventory - only while SkyyGear is loaded (gear:fn:smithing); world thread
M(page, r"""
public int unidBags(@REF@ ref, @ST@ st) {
  if (ref == null || st == null || !(@PKG@.MenuUtil.bridge().get("gear:fn:smithing") instanceof java.util.function.Function)) return 0;
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    return @PKG@.MenuUtil.countPrefix(p, "Skyy_Unid_Bag_");
  } catch (Throwable t) { return 0; }
}""")
M(page, r"""
public java.util.ArrayList nowRows(@REF@ ref, @ST@ st) {
  java.util.ArrayList out = new java.util.ArrayList();
  String q = questLine(this.playerRef.getUuid());
  if (q != null) out.add(new String[] { q, "world:quests" });
  int nb = unidBags(ref, st);
  if (nb > 0) out.add(new String[] { nb + (nb == 1 ? " mystery bag to identify" : " mystery bags to identify"), "smithing:identify" });
  java.util.ArrayList al = alerts();
  for (int i = 0; i < al.size() && out.size() < @PKG@.MenuData.AL_SHOW; i++) out.add(al.get(i));
  return out;
}""")
# 0.3.30 THE BIG ROW 1 (Home + every hub with a hub:def, kit 1.6 HubBar.hubs order) in the body of Home / Teleport: the kit's row button art,
# 48 px, a 32 px item icon, an 18 px label. Clicks a = "hub:h:<id>" (hubClick, as the kit row). Twin: big_row_preview in the build script.
M(page, r"""
public void bigRow(@UCB@ b, @UEB@ ev, String parent, String myHub, int w) {
  java.util.ArrayList h = @PKG@.HubBar.hubs();
  b.appendInline(parent, @PKG@.MenuData.UI_BROW);
  int n = h.size();
  if (n == 0) return;
  int bw = (w - @PKG@.MenuData.BR_GAP * (n - 1)) / n;
  boolean icons = bw >= @PKG@.MenuData.BR_ICON_MIN;
  for (int i = 0; i < n; i++) {
    Object[] e = (Object[]) h.get(i);
    String id = (String) e[0];
    boolean sel = id.equals(myHub);
    if (i > 0) b.appendInline("#SkyyMBRow", "Group { Anchor: (Width: " + @PKG@.MenuData.BR_GAP + "); }");
    String bid = "SkyyMBR" + i;
    b.appendInline("#SkyyMBRow", "Button #" + bid + " { Anchor: (Width: " + bw + ", Height: " + @PKG@.MenuData.BR_H + "); LayoutMode: Left; Padding: (Horizontal: " + @PKG@.MenuData.BR_PAD + ", Vertical: " + @PKG@.MenuData.BR_PADV + "); " + @PKG@.HubBar.rowStyle(sel) + " }");
    int lw = bw - 2 * @PKG@.MenuData.BR_PAD;
    String ic = (String) e[2];
    if (icons && @PKG@.HubBar.okItem(ic)) {
      b.appendInline("#" + bid, "ItemIcon { Anchor: (Width: " + @PKG@.MenuData.BR_ICON + ", Height: " + @PKG@.MenuData.BR_ICON + "); ItemId: \\"" + ic + "\\"; }");
      b.appendInline("#" + bid, "Group { Anchor: (Width: " + @PKG@.MenuData.BR_ICON_GAP + "); }");
      lw = lw - @PKG@.MenuData.BR_ICON - @PKG@.MenuData.BR_ICON_GAP;
    }
    b.appendInline("#" + bid, "Label { Anchor: (Width: " + lw + "); Text: \\"" + (String) e[1] + "\\"; Style: " + (sel ? @PKG@.MenuData.BR_LABSEL : @PKG@.MenuData.BR_LABN) + "; }");
    ev.addEventBinding(@BT@.Activating, "#" + bid, @EVD@.of("a", "hub:h:" + id));
  }
}""")
M(page, r"""
public static boolean hasTabArt(String stem) {
  for (int i = 0; i < @PKG@.MenuData.TAB_ART.length; i++) { if (@PKG@.MenuData.TAB_ART[i].equals(stem)) return true; }
  return false;
}""")
# 0.3.30 THE BIG ROW 2 (Teleport: the World tabs): 56 px tabs (the kit's tab art), each tab's icon behind its word (its putIcon icon, else
# the contract art SkyyMenu ships - SkyyHubTabs/<hub>_<tab>.png, "_on" while active), a 20 px label. Clicks a = "hub:<tab>" (hubClick).
M(page, r"""
public void bigTabs(@UCB@ b, @UEB@ ev, String parent, String hub, String myTab, int w) {
  java.util.UUID u = this.playerRef.getUuid();
  @PKG@.HubBar.remember(u, hub, myTab);
  b.appendInline(parent, @PKG@.MenuData.UI_BTABS);
  int cap = (w + @PKG@.MenuData.BT_GAP) / (@PKG@.MenuData.BT_MIN + @PKG@.MenuData.BT_GAP);
  java.util.ArrayList t = @PKG@.HubBar.shown(@PKG@.HubBar.tabs(hub, u), myTab, cap < 1 ? 1 : cap);
  int n = t.size();
  if (n == 0) return;
  int tw = (w - @PKG@.MenuData.BT_GAP * (n - 1)) / n;
  for (int i = 0; i < n; i++) {
    Object[] e = (Object[]) t.get(i);
    String id = (String) e[0];
    boolean sel = id.equals(myTab);
    if (i > 0) b.appendInline("#SkyyMBTabs", "Group { Anchor: (Width: " + @PKG@.MenuData.BT_GAP + "); }");
    String bid = "SkyyMBT" + i;
    b.appendInline("#SkyyMBTabs", "Button #" + bid + " { Anchor: (Width: " + tw + ", Height: " + @PKG@.MenuData.BT_H + "); " + @PKG@.HubBar.tabBStyle(sel) + " }");
    String stem = @PKG@.HubBar.iconOf((Object[]) e[3]);
    if (stem == null && hasTabArt(hub + "_" + id)) stem = hub + "_" + id;
    if (stem != null) b.appendInline("#" + bid, "Group { Anchor: (Left: " + ((tw - @PKG@.MenuData.BT_ICON) / 2) + ", Top: " + @PKG@.MenuData.BT_ICON_TOP + ", Width: " + @PKG@.MenuData.BT_ICON + ", Height: " + @PKG@.MenuData.BT_ICON + "); Background: \\"" + @PKG@.MenuData.TAB_ART_DIR + stem + (sel ? "_on" : "") + ".png\\"; }");
    b.appendInline("#" + bid, "Label { Anchor: (Left: 0, Top: 0, Width: " + tw + ", Height: " + @PKG@.MenuData.BT_H + "); Padding: (Horizontal: " + @PKG@.MenuData.BT_PAD + "); Text: \\"" + @PKG@.HubBar.clean((String) e[1]) + "\\"; Style: " + @PKG@.MenuData.BT_LAB + "; }");
    ev.addEventBinding(@BT@.Activating, "#" + bid, @EVD@.of("a", "hub:" + id));
  }
}""")
M(page, r"""
public int youLine(@UCB@ b, int n, String text) {''')
    _np = block('''M(page, r"""
public void nowPanel(@UCB@ b, @UEB@ ev) {''', '''    ev.addEventBinding(@BT@.Activating, "#SkyyMHmA" + i, @EVD@.of("a", "halert" + i));
  }
}""")''')
    rep(_np, '''# 0.3.30: always drawn (Skyy's design: You | Pinned | Right now); nothing to do = "Nothing waiting"
M(page, r"""
public void nowPanel(@UCB@ b, @UEB@ ev, @REF@ ref, @ST@ st) {
  java.util.ArrayList al = nowRows(ref, st);
  this.alertT = new String[al.size()];
  b.appendInline("#SkyyMHmMain", @PKG@.MenuData.UI_HNOW);
  b.appendInline("#SkyyMHmNow", @PKG@.MenuData.UI_HNOWT);
  if (al.isEmpty()) { b.appendInline("#SkyyMHmNow", @PKG@.MenuData.UI_HNOWNONE); return; }
  for (int i = 0; i < al.size() && i < @PKG@.MenuData.UI_HA.length; i++) {
    String[] a = (String[]) al.get(i);
    this.alertT[i] = a[1];
    b.appendInline("#SkyyMHmNow", @PKG@.MenuData.UI_HA[i]);
    b.set("#SkyyMHmA" + i + ".Text", a[0] + (a[1].length() > 0 ? "  >" : ""));
    ev.addEventBinding(@BT@.Activating, "#SkyyMHmA" + i, @EVD@.of("a", "halert" + i));
  }
}""")
# 0.3.30: the 5 x 5 update left pins without a slot - told once (chat + the Home info line), by name; null = nothing to tell
M(page, r"""
public String spillNote() {
  String u = this.playerRef.getUuid().toString();
  Object o = @PKG@.MenuLayout.SPILL.get(u);
  if (!(o instanceof String) || ((String) o).startsWith("!")) return null;   // fix: told once ('!'); the Right now row stays until Edit shortcuts opens
  String sv = (String) o;
  @PKG@.MenuLayout.SPILL.put(u, "!" + sv);
  int bar = sv.indexOf('|');
  String[] ks = (bar >= 0 ? sv.substring(bar + 1) : sv).split(",");
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < ks.length && i < 8; i++) { if (ks[i].length() == 0) continue; if (sb.length() > 0) sb.append(", "); sb.append(nameOf(ks[i])); }
  return ks.length + (ks.length == 1 ? " shortcut" : " shortcuts") + " did not fit the 5 x 5 grid - they wait in Edit shortcuts, + Add: " + @PKG@.MenuUtil.clip(sb.toString(), 90);
}""")''')
    _bd = block('''M(page, r"""
public void buildDash(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st, java.util.ArrayList slots, boolean tipsOff) {''', '''  b.set("#SkyyMGrid.Slots", slots);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyMGrid", @EVD@.of("a", "mslot"), false);
}""")''')
    rep(_bd, '''# 0.3.30: Home and Teleport scaled up - the kit's 38 px title bar holds the crest + the page title; row 1 (and Teleport's row 2) are drawn
# big as the body's first children (bigRow / bigTabs); the close X is the shell's (bound here: a = "hub:close")
M(page, r"""
public void buildDash(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st, java.util.ArrayList slots, boolean tipsOff) {
  boolean home = this.view.equals("main");
  java.util.UUID me = this.playerRef.getUuid();
  String stx = this.status == null ? "" : this.status;
  boolean add = this.editing && this.addSlot >= 0;
  @PKG@.MenuHub.ensure(me);
  if (home) {
    String sp = spillNote();
    if (sp != null) {
      stx = sp;
      try { this.playerRef.sendMessage(@MSG@.raw("[SkyWynn Menu] " + sp)); } catch (Throwable t) { }
    }
""" + "\\n".join("    " + ln for ln in HOME_JAVA.split("\\n")) + r"""
    bigRow(b, ev, "#SkyyMHome", "home", @PKG@.MenuData.HOME_ROW_W);
    b.appendInline("#SkyyMHome", @PKG@.MenuData.UI_HMAIN);
    youPanel(b, ev, ref, st);
    b.appendInline("#SkyyMHmMain", @PKG@.MenuData.UI_HSP16);
    b.appendInline("#SkyyMHmMain", @PKG@.MenuData.UI_HMID);
    b.appendInline("#SkyyMHmMid", @PKG@.MenuData.UI_HMIDT);
    b.appendInline("#SkyyMHmMid", @PKG@.MenuData.UI_HGAP5);
    b.appendInline("#SkyyMHmMid", @PKG@.MenuData.UI_HGW);
    b.appendInline("#SkyyMGW", tipsOff ? @PKG@.MenuData.UI_HGRIDNT : @PKG@.MenuData.UI_HGRID);
    b.appendInline("#SkyyMHmMain", @PKG@.MenuData.UI_HSP16);
    nowPanel(b, ev, ref, st);
    b.appendInline("#SkyyMHome", @PKG@.MenuData.UI_HGAP8);
    b.appendInline("#SkyyMHome", @PKG@.MenuData.UI_HFOOT);
    String info = stx.length() > 0 ? stx : (add ? @PKG@.MenuData.HT_ADD : (this.editing ? @PKG@.MenuData.HT_EDIT : (tipsOff ? @PKG@.MenuData.HT_HINT_OFF : @PKG@.MenuData.HT_HINT)));
    foot(b, ev, true, info);
    b.set("#SkyyMHmMidT.Text", add ? @PKG@.MenuData.HT_MID_ADD + pageOf(this.addPage, this.addPages)
                                   : (this.editing ? @PKG@.MenuData.HT_MID_EDIT : @PKG@.MenuData.HT_MID));
    ev.addEventBinding(@BT@.Dismissing, "#SkyyMHm", @EVD@.of("a", "mesc"), false);
    ev.addEventBinding(@BT@.Activating, "#SkyyMHmHubClose", @EVD@.of("a", "hub:close"));
  } else {
""" + "\\n".join("    " + ln for ln in TP_JAVA.split("\\n")) + r"""
    bigRow(b, ev, "#SkyyMTpB", "world", @PKG@.MenuData.TP_ROW_W);
    bigTabs(b, ev, "#SkyyMTpB", "world", "teleport", @PKG@.MenuData.TP_ROW_W);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TROW);
    b.appendInline("#SkyyMTpRow", @PKG@.MenuData.UI_TLEAD);
    b.appendInline("#SkyyMTpRow", @PKG@.MenuData.UI_HGW);
    b.appendInline("#SkyyMGW", tipsOff ? @PKG@.MenuData.UI_HGRIDNT : @PKG@.MenuData.UI_HGRID);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TGAP);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TINFO);
    b.appendInline("#SkyyMTpInfo", @PKG@.MenuData.UI_TIN);
    b.appendInline("#SkyyMTpInfo", @PKG@.MenuData.UI_TID);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TGAP);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TFOOT);
    foot(b, ev, false, null);
    String iname = this.infoName;
    String ibody = this.infoBody;
    if (iname == null) {
      iname = add ? "Add a teleport" + pageOf(this.addPage, this.addPages)
                  : (this.editing ? "Editing the Teleport page - no dragging" : "Teleport" + pageOf(this.pageNo, this.pages));
      ibody = add ? @PKG@.MenuData.HT_ADD : (this.editing ? @PKG@.MenuData.HT_EDIT : @PKG@.MenuData.HT_TP_HINT);
    }
    String[] lines = (ibody == null ? "" : ibody).split("\\n");
    b.set("#SkyyMTpIN.Text", iname);
    b.set("#SkyyMTpID.Text", stx.length() > 0 ? stx : (lines.length > 0 ? lines[0] : ""));   // 0.3.30: the status line moved into the info box
    ev.addEventBinding(@BT@.Dismissing, "#SkyyMTp", @EVD@.of("a", "mesc"), false);
    ev.addEventBinding(@BT@.Activating, "#SkyyMTpHubClose", @EVD@.of("a", "hub:close"));
  }
  b.set("#SkyyMGrid.Slots", slots);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyMGrid", @EVD@.of("a", "mslot"), false);
}""")''')
    rep('''    if (@PKG@.MenuLayout.hasSame(g, k)) { this.status = nameOf(k) + " is on your grid already."; rebuild(); return; }''',
        '''    if (@PKG@.MenuLayout.hasSame(g, k)) { this.status = nameOf(k) + " is on your grid already (that page has one shortcut)."; rebuild(); return; }''')

    # ------------------------------------------------------------------------------------------------------------ MenuAlert + MenuHub
    rep('''    if (@PKG@.SetStore.isBroken(u)) { if (sb.length() > 0) sb.append('\\n'); sb.append(@PKG@.MenuData.AL_SET).append("|settings:settings"); }''',
        '''    if (@PKG@.SetStore.isBroken(u)) { if (sb.length() > 0) sb.append('\\n'); sb.append(@PKG@.MenuData.AL_SET).append("|settings:settings"); }
    if (@PKG@.MenuLayout.SPILL.containsKey(u.toString())) { if (sb.length() > 0) sb.append('\\n'); sb.append(@PKG@.MenuData.AL_SPILL).append("|edit"); }   // 0.3.30''')
    rep('''# setup(): hub:def:<hub> for the 7 hubs + Menu's own 7 tabs''', '''# 0.3.30: a STAND-IN tab's Functions. MenuVtOpen = the owner's bridge Function (gear:fn:smithing {UUID, tab}); anything but TRUE = the kit's
# HubBar.open runs the tab's command as the player. MenuVtVis = the tab shows only while its command is on this server.
mvo.addInterface(pool.get("java.util.function.Function"))
F(mvo, "public String fn;")
F(mvo, "public String arg;")
C(mvo, "public MenuVtOpen(String fn, String arg) { this.fn = fn; this.arg = arg; }")
M(mvo, r"""
public Object apply(Object o) {
  if (!(o instanceof java.util.UUID)) return Boolean.FALSE;
  Object f = @PKG@.MenuUtil.bridge().get(this.fn);
  if (!(f instanceof java.util.function.Function)) return Boolean.FALSE;
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(new Object[] { o, this.arg }); } catch (Throwable t) { r = null; }
  return Boolean.TRUE.equals(r) ? Boolean.TRUE : Boolean.FALSE;
}""")
mvv.addInterface(pool.get("java.util.function.Function"))
F(mvv, "public String cmd;")
C(mvv, "public MenuVtVis(String cmd) { this.cmd = cmd; }")
M(mvv, r"""
public Object apply(Object o) {
  return @PKG@.MenuUtil.cmd(@PKG@.MenuUtil.firstWord(this.cmd)) != null ? Boolean.TRUE : Boolean.FALSE;
}""")
F(mhub, "public static volatile int PROXIES;")
# setup(): hub:def:<hub> for the 7 hubs + Menu's own 7 tabs''')
    rep('''    Object[] e = @PKG@.HubBar.put(@PKG@.MenuData.HT_HUB[j], @PKG@.MenuData.HT_TAB[j], "SkyyMenu", @PKG@.MenuData.HT_LABEL[j], @PKG@.MenuData.HT_ORDER[j],
                                  c.length() == 0 ? null : c, new @PKG@.MenuHubOpen(@PKG@.MenuData.HT_TAB[j]), vis);
    if (e != null) n = n + 1;
  }
  return n;''', '''    Object[] e = @PKG@.HubBar.putIcon(@PKG@.MenuData.HT_HUB[j], @PKG@.MenuData.HT_TAB[j], "SkyyMenu", @PKG@.MenuData.HT_LABEL[j], @PKG@.MenuData.HT_ORDER[j],
                                  c.length() == 0 ? null : c, new @PKG@.MenuHubOpen(@PKG@.MenuData.HT_TAB[j]), vis, @PKG@.MenuData.HT_HUB[j] + "_" + @PKG@.MenuData.HT_TAB[j]);   // 0.3.30: + its tab icon
    if (e != null) n = n + 1;
  }
  // 0.3.30 STAND-IN TABS (Skyy 2026-10-16 "smithing still working"): every contract tab whose owner put none - only while the key is free (the
  // owner's own tab always wins: put before us = we skip it, put after us = it replaces ours; shutdown removes only what still is ours)
  int px = 0;
  for (int j = 0; j < @PKG@.MenuData.VT_HUB.length; j++) {
    if (@PKG@.HubBar.get("hub:tab:" + @PKG@.MenuData.VT_HUB[j] + ":" + @PKG@.MenuData.VT_TAB[j]) != null) continue;
    Object op = @PKG@.MenuData.VT_FN[j].length() == 0 ? null : new @PKG@.MenuVtOpen(@PKG@.MenuData.VT_FN[j], @PKG@.MenuData.VT_ARG[j]);
    Object[] e = @PKG@.HubBar.putIcon(@PKG@.MenuData.VT_HUB[j], @PKG@.MenuData.VT_TAB[j], "SkyyMenu", @PKG@.MenuData.VT_LABEL[j], @PKG@.MenuData.VT_ORDER[j],
                                      @PKG@.MenuData.VT_CMD[j], op, new @PKG@.MenuVtVis(@PKG@.MenuData.VT_CMD[j]), @PKG@.MenuData.VT_HUB[j] + "_" + @PKG@.MenuData.VT_TAB[j]);
    if (e != null) px = px + 1;
  }
  PROXIES = px;
  return n;''')


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.29: UNIFIED MENU U1 (notes''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.30: MENU0330 (notes: tools/menu_0_3_30_patch.py; docs/answered/ui.md 2026-10-16): no duplicate icons / pages (17 new icon items painted
       at build time; one entry per page, hub:def world -> teleport), the 5 x 5 shortcut grid (+ the one-time update of saved grids), Home
       + Teleport scaled up (120 px slots, big row 1 / row 2), the Right now panel (quest:fn:hud, mystery bags, home:alert:*), stand-in hub
       tabs for contract tabs nobody put (Smithing opens /smithing), hub tab icons, Invite to Guild, Stats Health Regen, Battlemagic.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.30.py.
0.3.29: UNIFIED MENU U1 (notes''')
rep('VERSION = "0.3.29"\n', 'VERSION = "0.3.30"\n')

# ---------------------------------------------------------------------------------------------------------------- ICONS WAVE 3 (build time)
rep('''ICON_PETS = "Skyy_Menu_Icon_Pets"             # 0.3.14''', '''# ---- 0.3.30: OUR OWN ICONS, WAVE 3 - no icon item used by two pages (Skyy 2026-10-16: "storage and pocket dimension look the same",
# "we have world and teleport that look the same", "class tree and profile have the same icon."). Painted HERE, at build time, with the
# sheet-1 painter (tools/art/make_menu_icons.py: palette ramps, top-left light, bevels, 1 px tinted outline, hard alpha) on its 64 px grid,
# from the approved motifs of art/hub-tab-icons (tools/art/make_hub_tab_icons.py builders, imported, not edited; drawn for a 72 px square,
# so every sample point is scaled 72 / 64 - each pixel is still painted and ramp-snapped at 64 px, then centred). Original pixels only.
# (name, item name, motif hub, motif tab)
MENU_ICONS_3 = [("HubCharacter", "Character", "hubrow", "character"), ("HubStorage", "Storage", "hubrow", "storage"),
                ("HubMarket", "Market", "hubrow", "market"), ("HubSmithing", "Smithing", "hubrow", "smithing"),
                ("HubWorld", "World", "hubrow", "world"), ("HubSocial", "Social", "hubrow", "social"),
                ("HubSettings", "Settings", "settings", "settings"),   # the sliders: the Settings tile keeps its two cogs
                ("Trees", "Trees", "character", "trees"), ("Class", "Class", "character", "class"),
                ("Profiles", "Profiles", "character", "profiles"), ("Requip", "Requip", "storage", "requip"),
                ("Gear", "Gear", "smithing", "gear"), ("Upgrade", "Upgrade", "smithing", "upgrade"),
                ("Explore", "Explore", "world", "explore"), ("Quests", "Quests", "world", "quests"),
                ("Merchants", "Merchants", "market", "merchants"), ("Layout", "Edit shortcuts", "settings", "layout")]


def _paint_wave3():
    """{item id: 64 x 64 RGBA8 PNG bytes} - deterministic (checked: one icon painted twice is byte-identical)"""
    _art_dir = os.path.join(HERE, "..", "tools", "art")
    if _art_dir not in sys.path:
        sys.path.insert(0, _art_dir)
    import make_hub_tab_icons as _HT
    _M, _P = _HT.M, _HT.P
    _k = 72.0 / 64.0

    class _SShape(object):
        def __init__(self, sh):
            self.sh = sh
            self.bb = tuple(v / _k for v in sh.bb)

        def __call__(self, x, y):
            return self.sh(x * _k, y * _k)

    class _SLayer(object):
        def __init__(self, ly):
            self.ly, self.shape = ly, _SShape(ly.shape)
            self.pal, self.cast, self.line, self.rim = ly.pal, ly.cast, ly.line, ly.rim

        def t(self, x, y):
            return self.ly.t(x * _k, y * _k)

    _fn = dict(((h, t), f) for h, t, _l, f, _w in _HT.ALL)

    def _one(h, t):
        ic = _fn[(h, t)]()
        ic.layers = [_SLayer(l) for l in ic.layers]
        ic.pix = [(int(round(x / _k)), int(round(y / _k)), c) for (x, y, c) in ic.pix]
        _old = _M.N
        _M.N = 64
        try:
            img = ic.render()
        finally:
            _M.N = _old
        pts = [(x, y) for y in range(64) for x in range(64) if img[y][x][3]]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        dx, dy = int(round((63 - max(xs) - min(xs)) / 2.0)), int(round((63 - max(ys) - min(ys)) / 2.0))
        out = _P.new(64, 64)
        for x, y in pts:
            if 0 <= x + dx < 64 and 0 <= y + dy < 64:
                out[y + dy][x + dx] = list(img[y][x])
        return _M.png_bytes(out)
    out = {}
    for _nm, _lab, _h, _t in MENU_ICONS_3:
        out["Skyy_Menu_Icon_" + _nm] = _one(_h, _t)
    assert _one(MENU_ICONS_3[0][2], MENU_ICONS_3[0][3]) == out["Skyy_Menu_Icon_" + MENU_ICONS_3[0][0]], "0.3.30: the wave-3 painter is deterministic"
    return out


GEN_ICON_PNG = _paint_wave3()
for _nm, _lab, _h, _t in MENU_ICONS_3:
    assert "Skyy_Menu_Icon_" + _nm not in ICON_ITEMS, "0.3.30: %s clashes with an icon item we already ship" % _nm
    ICON_ITEMS["Skyy_Menu_Icon_" + _nm] = ("gen:%s_%s" % (_h, _t), "Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % _nm, None, _lab, "Farming_Collar")
assert len(set(GEN_ICON_PNG.values())) == len(GEN_ICON_PNG), "0.3.30: every wave-3 icon is its own picture"
print("0.3.30 wave-3 icons painted at build time:", ", ".join("%s (%d bytes)" % (n, len(GEN_ICON_PNG["Skyy_Menu_Icon_" + n])) for n, _l, _h, _t in MENU_ICONS_3))
ICON_PETS = "Skyy_Menu_Icon_Pets"             # 0.3.14''')
rep('''    import hashlib, struct
    art, rel, man, _nm, _look = ICON_ITEMS[iid]
''', '''    import hashlib, struct
    if iid in GEN_ICON_PNG:    # 0.3.30: wave 3 is painted by this build (no art file / manifest): checked for the same PNG shape
        data = GEN_ICON_PNG[iid]
        assert data[:8] == b"\\x89PNG\\r\\n\\x1a\\n" and data[12:16] == b"IHDR" and struct.unpack(">II", data[16:24]) == (64, 64) \\
            and data[24:26] == b"\\x08\\x06", "icon item %s: not a 64 x 64 RGBA8 PNG" % iid
        return data
    art, rel, man, _nm, _look = ICON_ITEMS[iid]
''')
rep('''    ("main", 36, "Furniture_Village_Wardrobe", "Wardrobe",''',
    '''    ("main", 36, "Skyy_Menu_Icon_Requip", "Wardrobe",     # 0.3.30: our own Requip icon (was the vanilla Village Wardrobe)''')

rep('''_main["Wardrobe"][2] == "Furniture_Village_Wardrobe" and''', '''_main["Wardrobe"][2] == "Skyy_Menu_Icon_Requip" and''')   # 0.3.30

# ---------------------------------------------------------------------------------------------------------------- Invite to Guild
_pa = block('''    # 0.3.26: 29 / 30 / 31 reuse our Hub / Spawn / My Island icons''', '''"Click to trust", "island trust %P", False),
''')
rep(_pa, '''    # 0.3.26: the teleport actions reuse our Hub / Spawn / My Island icons. 0.3.30: they moved one slot left (28 - 31) so Invite to Guild
    # (RESUME queue, Menu 0.3.30) sits right of Invite to Party; the island actions keep 33 / 34 (PA_LEGACY names 33)
    (28, "Skyy_Menu_Icon_Hub", "Send Teleport Request", ["Ask %P if you may teleport to them. They have 60 seconds to accept.", "Command: /tpa %P"],
        "Click to send", "tpa %P", False),
    (29, "Skyy_Menu_Icon_Spawn", "Invite Them Here", ["Ask %P to teleport to you.", "Command: /tpahere %P"], "Click to send", "tpahere %P", False),
    (30, "Skyy_Menu_Icon_MyIsland", "Visit Their Island", ["Teleport to the island of %P and look around (you can only build with their build rights).",
        "Command: /island visit %P"], "Click to visit", "island visit %P", True),
    (31, "Deco_Scroll", "Invite to Party", ["Invite %P to your party.", "Command: /party invite %P"], "Click to invite", "party invite %P", False),
    (32, "Furniture_Human_Ruins_Banner", "Invite to Guild", ["Invite %P to your guild (guild leaders and officers who may invite).",
        "They answer it on their Guild page.", "Command: /guild invite %P"], "Click to invite", "guild invite %P", False),
    (33, "Tool_Hammer_Iron", "Invite to Your Island", ["Invite %P to join your island as a co-op member. Only do this for friends.",
        "They join with /island accept.", "Command: /island invite %P"], "Click to invite", "island invite %P", False),
    (34, "Tool_Pickaxe_Iron", "Let Them Build", ["Let %P build on YOUR island without making them a member.",
        "Undo with /island untrust.", "Command: /island trust %P"], "Click to trust", "island trust %P", False),
''')
rep('''assert [a[1] for a in PLAYER_ACTIONS if a[0] in (29, 30, 31)] == ["Skyy_Menu_Icon_Hub", "Skyy_Menu_Icon_Spawn", "Skyy_Menu_Icon_MyIsland"]''',
    '''assert [a[1] for a in PLAYER_ACTIONS if a[0] in (28, 29, 30)] == ["Skyy_Menu_Icon_Hub", "Skyy_Menu_Icon_Spawn", "Skyy_Menu_Icon_MyIsland"]   # 0.3.30: one slot left
# fix 2: the player-page ACTIONS are buttons, not pages (never in + Add / Home / row 1). Only 0.3.26's three teleport actions wear the icon
# of the page they belong to (on purpose); every other action wears a vanilla item, never a Menu page icon (Invite to Guild = a banner)
assert not [a for a in PLAYER_ACTIONS if a[0] not in (28, 29, 30) and a[1].startswith("Skyy_Menu_Icon_")], "0.3.30: an action wears a page icon"''')
rep('''[a[1] for a in PLAYER_ACTIONS if a[0] in (29, 30, 31)] if _v in _was]''', '''[a[1] for a in PLAYER_ACTIONS if a[0] in (28, 29, 30)] if _v in _was]''')

# ---------------------------------------------------------------------------------------------------------------- Battlemagic
rep('''CLASS_PLAYABLE = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk"]''',
    '''CLASS_PLAYABLE = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk", "Spellblade"]   # 0.3.30: + the Spellblade (SkyyClasses 0.1.25+)''')
rep('''CLASS_SKILLS   = ["Archery", "Swordsmanship", "Sorcery", "Fury", "Divinity", "Assassination", "Zen"]''',
    '''CLASS_SKILLS   = ["Archery", "Swordsmanship", "Sorcery", "Fury", "Divinity", "Assassination", "Zen", "Battlemagic"]   # 0.3.30: + Battlemagic''')

rep('''         "or Zen) and more. "''', '''         "Zen or Battlemagic) and more. "   # 0.3.30: + the Spellblade's Battlemagic''')
rep('''(Archery, Swordsmanship, Sorcery, Fury, Divinity, Assassination "
         "Zen or''', '''(Archery, Swordsmanship, Sorcery, Fury, Divinity, Assassination, "
         "Zen or''')
rep('''its own class (Archer, Warrior, Mage, Berserker, Priest, Assassin or Monk), island''', '''its own class (Archer, Warrior, Mage, Berserker, Priest, Assassin, Monk or Spellblade), island''')
rep('''Divinity, Assassination or Zen, on its own XP curve) - level up and pay coins. Stronger mobs pay more kill XP and early gathering is faster.''',
    '''Divinity, Assassination, Zen or Battlemagic, on its own XP curve) - level up and pay coins. Stronger mobs pay more kill XP.''')
rep('''"Classes: Archer, Warrior, Mage, Berserker, Priest (the party healer), Assassin or Monk. Each''', '''"Classes: Archer, Warrior, Mage, Berserker, Priest (the party healer), Assassin, Monk or Spellblade (a melee mage). Each''')
rep('''assert "Assassin or Monk" in _bym["SkyyClasses"]["desc"] and "Assassin or Monk" in _bym["SkyyProfiles"]["desc"], "0.3.9: Assassin + Monk named"
assert "Assassination or Zen" in _bym["SkyySkills"]["desc"] and len(_bym["SkyySkills"]["desc"]) <= 390, "0.3.9: the Skills text (0.3.13: Zen)"''',
    '''assert "Monk or Spellblade" in _bym["SkyyClasses"]["desc"] and "Monk or Spellblade" in _bym["SkyyProfiles"]["desc"], "0.3.30: + the Spellblade named"
assert "Zen or Battlemagic" in _bym["SkyySkills"]["desc"] and len(_bym["SkyySkills"]["desc"]) <= 390, "0.3.9: the Skills text (0.3.13: Zen; 0.3.30: Battlemagic)"''')

# ---------------------------------------------------------------------------------------------------------------- Stats: Health Regen
rep('''  if (sb.length() == 0) sb.append("no bonus - skill tree nodes add Mana Regen");
  return new String[] { signed(tot) + "%", sb.toString() };
}""")''', '''  if (sb.length() == 0) sb.append("no bonus - skill tree nodes add Mana Regen");
  return new String[] { signed(tot) + "%", sb.toString() };
}""")
# 0.3.30: the Health Regen row (RESUME queue, Menu 0.3.30): SkyySkills 0.4.43's skill:fn:hpregen {"row", UUID} -> String[]{value, detail}
# ("3.5/s", "1.2/s in combat; ..."); without it "-" + what it needs
M(scl, r"""
public static String[] hpRegen(java.util.UUID u) {
  Object r = call("skill:fn:hpregen", new Object[] { "row", u });
  if ((r instanceof String[]) && ((String[]) r).length >= 2) {
    String[] a = (String[]) r;
    String v = a[0] == null ? "-" : @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(a[0]), 20);
    String d = a[1] == null ? "" : @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(a[1]), 70);
    return new String[] { v.length() == 0 ? "-" : v, d };
  }
  return new String[] { "-", "needs SkyySkills 0.4.43" };
}""")''')
rep('''  add(rows, "Mana Regen", mr[0], mr[1]);
''', '''  add(rows, "Mana Regen", mr[0], mr[1]);
  String[] hr = hpRegen(u);   // 0.3.30
  add(rows, "Health Regen", hr[0], hr[1]);
''')

# ---------------------------------------------------------------------------------------------------------------- hub data
rep('''HUB_ICON_ITEM = {"character": "Skyy_Menu_Icon_YourProfile", "storage": "Skyy_Menu_Icon_PocketDimension", "market": "Skyy_Menu_Icon_Bazaar",
                 "smithing": "Skyy_Menu_Icon_Reforge", "world": "Skyy_Menu_Icon_Teleport", "social": "Skyy_Menu_Icon_Players",
                 "settings": "Skyy_Menu_Icon_Settings"}''',
    '''# 0.3.30: each hub wears its OWN wave-3 icon (0.3.28 - 0.3.29 reused a page's icon: Storage = Pocket Dimension, World = Teleport, ...)
HUB_ICON_ITEM = {"character": "Skyy_Menu_Icon_HubCharacter", "storage": "Skyy_Menu_Icon_HubStorage", "market": "Skyy_Menu_Icon_HubMarket",
                 "smithing": "Skyy_Menu_Icon_HubSmithing", "world": "Skyy_Menu_Icon_HubWorld", "social": "Skyy_Menu_Icon_HubSocial",
                 "settings": "Skyy_Menu_Icon_HubSettings"}''')
_soon = block('''HUB_SOON = {"character": "The Character hub has no pages yet - coming soon.",''', '''"settings": "The Settings hub has no pages yet - coming soon."}''')
rep(_soon, '''# 0.3.30 (Skyy 2026-10-16 "smithing still working"): no "coming soon" where a page exists - the stand-in tabs (MenuHub.register) give
# every hub its contract pages whose command is on this server; this line is only for a hub with truly nothing to open
HUB_SOON = dict((_h, "No %s pages are on this server right now." % SUI.HUB_DEFS[_h][0]) for _h in SUI.HUBS)''')
rep('''HG_COLS, HG_ROWS = 7, 5
HG_N = HG_COLS * HG_ROWS
HG_CR, HG_CC = 2, 3                          # the centre: row 2, column 3 = slot 17
HG_CENTRE = HG_CR * HG_COLS + HG_CC
OLD_COLS, OLD_CR, OLD_CC = 9, 1, 4            # the 0.3.28 main view: 9 wide, its centre (the mouse spot) row 1 column 4 = slot 13
assert HG_CENTRE == 17 and OLD_CR * OLD_COLS + OLD_CC == 13''', '''HG_COLS, HG_ROWS = 5, 5                      # 0.3.30: 5 x 5 (Skyy 2026-10-16 "5x5 is big enough for the shortcuts."; 0.3.29: 7 x 5)
HG_N = HG_COLS * HG_ROWS
HG_CR, HG_CC = 2, 2                          # the centre: row 2, column 2 = slot 12
HG_CENTRE = HG_CR * HG_COLS + HG_CC
# 0.3.30: the saved files keep 0.3.29's 7 x 5 NUMBERING (g.<slot> / t.<slot> = row * 7 + column, 17 = the centre); the 5 x 5 grid is its
# columns 1 - 5 (G7_OFF), so a rollback to 0.3.29 reads every pin where it is. Pins in columns 0 / 6 move once (MenuLayout.fold).
G7_COLS, G7_ROWS, G7_CR, G7_CC, G7_OFF = 7, 5, 2, 3, 1
G7_N = G7_COLS * G7_ROWS
OLD_COLS, OLD_CR, OLD_CC = 9, 1, 4            # the 0.3.28 main view: 9 wide, its centre (the mouse spot) row 1 column 4 = slot 13
assert HG_CENTRE == 12 and G7_CR * G7_COLS + G7_CC == 17 and HG_CC + G7_OFF == G7_CC and HG_CR == G7_CR and HG_ROWS == G7_ROWS \\
    and OLD_CR * OLD_COLS + OLD_CC == 13''')
rep('''HUB_DEFTAB = {"character": "skills"}          # Skyy 2026-10-15 "id do skills as the default one for this" (hub:def element 3)''',
    '''HUB_DEFTAB = {"character": "skills",         # Skyy 2026-10-15 "id do skills as the default one for this" (hub:def element 3)
              "world": "teleport"}            # 0.3.30: World IS its Teleport page (Skyy 10-16 "world and teleport ... do the same thing"): one entry''')
rep('''BUILTIN_HOME = {17: "tab:world:teleport", 10: "hub:character", 24: "hub:market", 16: "hub:storage", 18: "hub:smithing",
                9: "hub:social", 11: "hub:settings", 23: "hub:world"}
BUILTIN_TP = {16: "tp:island", 17: "tp:hub", 18: "tp:spawn"}        # the Teleport page: My Island | Hub (centre, as today) | Spawn''',
    '''# 0.3.30: the 5 x 5 default - the same spots round the centre as 0.3.29; World left out (it opens the Teleport page that IS the centre)
BUILTIN_HOME = {12: "tab:world:teleport", 7: "hub:character", 17: "hub:market", 11: "hub:storage", 13: "hub:smithing",
                6: "hub:social", 8: "hub:settings"}
BUILTIN_TP = {11: "tp:island", 12: "tp:hub", 13: "tp:spawn"}        # the Teleport page: My Island | Hub (centre, as today) | Spawn''')
rep('''AL_MAX, AL_SHOW = 40, 8                      # an alert line: at most 40 characters (fits its 252 px button at 11 px); at most 8 lines (3 per mod)''',
    '''AL_MAX, AL_SHOW = 40, 8                      # an alert line: at most 40 characters (fits its 252 px button at 11 px); at most 8 lines (3 per mod)
# ---- 0.3.30: ONE ICON PER PAGE. TAB_ICON = every contract tab's icon item: the old tile's icon where the tab IS an old tile (TILE_TAB),
# else its wave-3 icon. A page shown under several keys (tab / old tile / the hub whose default tab it is) is ONE entry with one icon.
VT_SKIP = ("smithing:multitool",)             # Skyy 2026-10-15 (art/hub-tab-icons README v1.1): "we scrapped the multitool menu"
TAB_ICON = {}
for _k, _t in TILE_TAB.items():
    TAB_ICON[_t] = [e[2] for e in ENTRIES if e[0] == "main" and re.sub(r"[^a-z0-9]", "", e[3].lower()) == _k][0]
TAB_ICON.update({"character:trees": "Skyy_Menu_Icon_Trees", "character:class": "Skyy_Menu_Icon_Class", "character:profiles": "Skyy_Menu_Icon_Profiles",
                 "smithing:gear": "Skyy_Menu_Icon_Gear", "smithing:upgrade": "Skyy_Menu_Icon_Upgrade", "world:explore": "Skyy_Menu_Icon_Explore",
                 "world:quests": "Skyy_Menu_Icon_Quests", "market:merchants": "Skyy_Menu_Icon_Merchants", "settings:layout": "Skyy_Menu_Icon_Layout"})
_ctabs = ["%s:%s" % (_r[0], _r[1]) for _r in SUI.HUB_TABS]
assert sorted(TAB_ICON) == sorted(_t for _t in _ctabs if _t not in VT_SKIP) and all(_v in ICON_ITEMS for _v in TAB_ICON.values()), \\
    "0.3.30: every contract tab (but Multitool) has our icon item: %s" % sorted(set(TAB_ICON) ^ set(_ctabs))
# THE NO-DUPLICATE CHECK: the 7 hubs + every contract tab (the old tiles are those tabs) + the 3 teleports = one icon item each
_ICON_USE = [("hub:" + _h, HUB_ICON_ITEM[_h]) for _h in SUI.HUBS] + [("tab:" + _t, _i) for _t, _i in sorted(TAB_ICON.items())] + \\
    [("tp:island", "Skyy_Menu_Icon_MyIsland"), ("tp:hub", "Skyy_Menu_Icon_Hub"), ("tp:spawn", "Skyy_Menu_Icon_Spawn")]
_dup = [(_i, [_e for _e, _j in _ICON_USE if _j == _i]) for _i in sorted(set(_j for _e, _j in _ICON_USE)) if [_j for _e, _j in _ICON_USE].count(_i) > 1]
assert not _dup and MENU_ITEM_ID not in [_j for _e, _j in _ICON_USE], "0.3.30: an icon item names two pages: %s" % _dup
print("0.3.30 one icon per page: %d entries, %d icon items, none shared" % (len(_ICON_USE), len(set(_j for _e, _j in _ICON_USE))))
# ---- 0.3.30: STAND-IN TABS (Skyy 2026-10-16 "smithing still working" - the Smithing hub said "coming soon"): every contract tab not owned by
# SkyyMenu, with a command, that its owner did not put (SkyyGear has no hub tabs) - put by SkyyMenu only while the key is free, visible only
# while the command exists; open = the owner's bridge Function where it has one (VT_FN), else the command as the player (kit HubBar.open)
VT = [(_h, _t, _o, _l, _c) for _h, _t, _o, _m, _l, _c in SUI.HUB_TABS if _m != "SkyyMenu" and _c and "%s:%s" % (_h, _t) not in VT_SKIP]
VT_FN = {"smithing:gear": ("gear:fn:smithing", "craft"), "smithing:reforge": ("gear:fn:smithing", "reforge"),
         "smithing:upgrade": ("gear:fn:smithing", "upgrade"), "smithing:identify": ("gear:fn:smithing", "identify")}
assert all(_k in ["%s:%s" % (_r[0], _r[1]) for _r in VT] for _k in VT_FN) and ("smithing", "gear", 10, "Gear", "smithing") in VT, \\
    "0.3.30: the Smithing hub's first stand-in tab runs /smithing (SkyyGear's Craft / Anvil / Upgrade / Identify page)"
# the tab icon art (art/hub-tab-icons, our own; README there) shipped at the kit 1.6 hook path Common/UI/Custom/SkyyHubTabs/<hub>_<tab>@2x.png
TAB_ART_DIR = "art/hub-tab-icons"
_TAM = json.load(open(os.path.join(HERE, "..", *(TAB_ART_DIR + "/manifest.json").split("/")), encoding="utf8"))
TAB_ART = sorted("%s_%s" % (_i["hub"], _i["tab"]) for _i in _TAM["icons"] if _i["hub"] != "hubrow")
assert TAB_ART == sorted(_t.replace(":", "_") for _t in TAB_ICON), "0.3.30: one tab icon picture per contract tab (no Multitool)"''')

# ---------------------------------------------------------------------------------------------------------------- build checks of the tables
rep('''assert BUILTIN_HOME[HG_CENTRE] == "tab:world:teleport" and sorted(v[4:] for v in BUILTIN_HOME.values() if v.startswith("hub:")) == sorted(SUI.HUBS), \\
    "0.3.29: the default Home = Teleport in the centre + the 7 hubs"''',
    '''assert BUILTIN_HOME[HG_CENTRE] == "tab:world:teleport" and sorted(v[4:] for v in BUILTIN_HOME.values() if v.startswith("hub:")) == \\
    sorted(_h for _h in SUI.HUBS if _h != "world") and HUB_DEFTAB["world"] == "teleport", \\
    "0.3.30: the default Home = Teleport in the centre + the 6 other hubs (World IS the centre's page)"''')

# ---------------------------------------------------------------------------------------------------------------- the pages: geometry
_geo = block('''# ---- HOME (the overview page): row 1 | YOU | the 7 x 5 shortcut grid | RIGHT NOW | the foot row.''',
             '''", ".join("%s %d px tabs" % (t, HUB_LABEL_FIT[t]) for t, _s, _h, _m in HUB_PAGES)))
''')
rep(_geo, PAGES30)

# ---------------------------------------------------------------------------------------------------------------- MenuData fields
rep('''for _n, _v in (("HG_N", HG_N), ("HG_COLS", HG_COLS), ("HG_ROWS", HG_ROWS), ("HG_CR", HG_CR), ("HG_CC", HG_CC), ("OLD_COLS", OLD_COLS),
               ("OLD_CR", OLD_CR), ("OLD_CC", OLD_CC), ("HOME_FOOT_W", HOME_FOOT_W), ("TP_FOOT_W", TP_FOOT_W), ("FB_GAP", FB_GAP),
               ("AL_MAX", AL_MAX), ("AL_SHOW", AL_SHOW), ("YOU_BAR_W", HOME_SIDE - 28)):
    F(dat, "public static final int %s = %d;" % (_n, _v))''',
    '''for _n, _v in (("HG_N", HG_N), ("HG_COLS", HG_COLS), ("HG_ROWS", HG_ROWS), ("HG_CR", HG_CR), ("HG_CC", HG_CC), ("OLD_COLS", OLD_COLS),
               ("OLD_CR", OLD_CR), ("OLD_CC", OLD_CC), ("HOME_FOOT_W", HOME_FOOT_W), ("TP_FOOT_W", TP_FOOT_W), ("FB_GAP", FB_GAP),
               ("AL_MAX", AL_MAX), ("AL_SHOW", AL_SHOW), ("YOU_BAR_W", YOU_BAR_W),
               # 0.3.30: the 7 x 5 file numbering, the big row 1 / row 2 of Home and Teleport
               ("G7_N", G7_N), ("G7_COLS", G7_COLS), ("G7_ROWS", G7_ROWS), ("G7_OFF", G7_OFF), ("G7_CR", G7_CR), ("G7_CC", G7_CC), ("HOME_ROW_W", HOME_ROW_W),
               ("TP_ROW_W", TP_ROW_W), ("BR_H", BR_H), ("BR_GAP", BR_GAP), ("BR_PAD", BR_PAD), ("BR_PADV", BR_PADV), ("BR_ICON", BR_ICON),
               ("BR_ICON_GAP", BR_ICON_GAP), ("BR_ICON_MIN", BR_ICON_MIN), ("BT_H", BT_H), ("BT_GAP", BT_GAP), ("BT_ICON", BT_ICON),
               ("BT_ICON_TOP", BT_ICON_TOP), ("BT_MIN", BT_MIN), ("BT_PAD", BT_PAD)):
    F(dat, "public static final int %s = %d;" % (_n, _v))
for _n, _v in (("BR_LABN", BR_LABN), ("BR_LABSEL", BR_LABSEL), ("BT_LAB", BT_LAB), ("TAB_ART_DIR", "SkyyHubTabs/")):
    F(dat, "public static final String %s = %s;" % (_n, jstr(_v)))
assert SUI.HUB_TAB_ICON_DIR == "SkyyHubTabs/", "0.3.30: the kit 1.6 tab icon folder"
F(dat, "public static final String[] TAB_KEY = %s;" % jarr(sorted(TAB_ICON)))
F(dat, "public static final String[] TAB_ICON = %s;" % jarr([TAB_ICON[_k] for _k in sorted(TAB_ICON)]))
F(dat, "public static final String[] TAB_ART = %s;" % jarr(TAB_ART))
F(dat, "public static final String[] VT_HUB = %s;" % jarr([_r[0] for _r in VT]))
F(dat, "public static final String[] VT_TAB = %s;" % jarr([_r[1] for _r in VT]))
F(dat, "public static final int[] VT_ORDER = %s;" % jints([_r[2] for _r in VT]))
F(dat, "public static final String[] VT_LABEL = %s;" % jarr([_r[3] for _r in VT]))
F(dat, "public static final String[] VT_CMD = %s;" % jarr([_r[4] for _r in VT]))
F(dat, "public static final String[] VT_FN = %s;" % jarr([VT_FN.get("%s:%s" % (_r[0], _r[1]), ("", ""))[0] for _r in VT]))
F(dat, "public static final String[] VT_ARG = %s;" % jarr([VT_FN.get("%s:%s" % (_r[0], _r[1]), ("", ""))[1] for _r in VT]))''')

# ---------------------------------------------------------------------------------------------------------------- MenuUtil: count by prefix
rep('''# last hotbar slot if free (Hypixel keeps the menu in slot 9), else any hotbar slot, else storage, else backpack''',
    '''# 0.3.30: items whose id starts with a prefix (Right now: SkyyGear's mystery bags Skyy_Unid_Bag_<Rarity>) - world thread only
M(utl, r"""
public static int countInPrefix(@IC@ c, String pre) {
  if (c == null || pre == null) return 0;
  int n = 0;
  short cap = c.getCapacity();
  for (short s = 0; s < cap; s++) {
    @IS@ it = c.getItemStack(s);
    if (it == null || it.isEmpty()) continue;
    String id = it.getItemId();
    if (id != null && id.startsWith(pre)) n += it.getQuantity();
  }
  return n;
}""")
M(utl, r"""
public static int countPrefix(@PLA@ p, String pre) {
  @INV@ inv = p == null ? null : p.getInventory();
  if (inv == null) return 0;
  return countInPrefix(inv.getStorage(), pre) + countInPrefix(inv.getHotbar(), pre) + countInPrefix(inv.getBackpack(), pre)
       + countInPrefix(inv.getUtility(), pre) + countInPrefix(inv.getTools(), pre);
}""")
# last hotbar slot if free (Hypixel keeps the menu in slot 9), else any hotbar slot, else storage, else backpack''')

# ---------------------------------------------------------------------------------------------------------------- the new classes
rep('''mhv  = mk("MenuHubVis")''', '''mhv  = mk("MenuHubVis")
mvo  = mk("MenuVtOpen")     # 0.3.30: a stand-in tab's open Function (the owner's bridge Function, e.g. gear:fn:smithing)
mvv  = mk("MenuVtVis")      # 0.3.30: a stand-in tab's visible Function (its command exists)''')
rep('''         hubb, mhub, mho, mhv, hcch, hcst, hcmk, hctr, hcso, mal, pl)   # 0.3.28: the hub classes; 0.3.29: MenuAlert''',
    '''         hubb, mhub, mho, mhv, hcch, hcst, hcmk, hctr, hcso, mal, mvo, mvv, pl)   # 0.3.28: the hub classes; 0.3.29: MenuAlert; 0.3.30: MenuVt*''')

JAVA30()

# ---------------------------------------------------------------------------------------------------------------- the jar: art + checks
rep('''    len(ICON_ITEMS) == 1 + len(PET_ART) + len(MENU_ICONS) - 1 + len(MENU_ICONS_2), \\''',
    '''    len(ICON_ITEMS) == 1 + len(PET_ART) + len(MENU_ICONS) - 1 + len(MENU_ICONS_2) + len(MENU_ICONS_3), \\''')
rep('''print("0.3.28 kit art:", len(_kit), "files under Common/UI/Custom/SkyyKit/ (%d bytes)" % sum(len(v) for v in _kit.values()))''',
    '''print("0.3.28 kit art:", len(_kit), "files under Common/UI/Custom/SkyyKit/ (%d bytes)" % sum(len(v) for v in _kit.values()))
# 0.3.30: the hub tab icons (art/hub-tab-icons, manifest sha256 + bytes) at the kit 1.6 hook path - SkyyHubTabs/<hub>_<tab>(_on)@2x.png
_tabart = {}
for _st in TAB_ART:
    _h, _t = _st.split("_", 1)
    _pp = SUI.hub_tab_icon_paths(_h, _t)
    for _fn, _jp in (("%s.png" % _st, _pp[2]), ("%s_on.png" % _st, _pp[3])):
        _data = open(os.path.join(HERE, "..", *(TAB_ART_DIR + "/" + _fn).split("/")), "rb").read()
        _me = [f for f in _TAM["files"] if f["path"] == _fn]
        assert len(_me) == 1 and hashlib.sha256(_data).hexdigest() == _me[0]["sha256"] and len(_data) == _me[0]["bytes"], "0.3.30: %s = its manifest entry" % _fn
        assert _jp.startswith("Common/UI/Custom/SkyyHubTabs/") and _jp.endswith("@2x.png") and _jp not in files and _jp not in COMMON
        _tabart[_jp] = _data
files.update(_tabart)
print("0.3.30 hub tab icons:", len(_tabart), "files under Common/UI/Custom/SkyyHubTabs/ (%d bytes)" % sum(len(v) for v in _tabart.values()))''')

# ---------------------------------------------------------------------------------------------------------------- fix round (menu0330fix)
# docs/answered/ui.md 2026-10-16 HUD SHORTCUT OPENS THE EDITOR (Skyy: "this shortcut should open the hud editor directly."): a Home shortcut
# on Settings > HUD runs /skyyhud straight away (the old HUD Editor tile already did; SkyyHud 0.3.28 publishes no bridge fn for its editor);
# the hub row's HUD tab keeps its page; no /skyyhud on this server (SkyyHud absent) = one chat line, the menu stays as it is
rep('''  if (k.startsWith("hub:")) { openHub(ref, st, k.substring(4)); return; }
  if (k.startsWith("tab:")) {''', '''  if (k.startsWith("hub:")) { openHub(ref, st, k.substring(4)); return; }
  if (k.equals("tab:settings:hud")) {   // fix: the HUD editor directly (= the player typing /skyyhud); no SkyyHud = one chat line
    if (@PKG@.MenuUtil.cmd("skyyhud") != null) { runCmd(ref, st, "skyyhud", true); return; }
    try { this.playerRef.sendMessage(@MSG@.raw("[Menu] The HUD editor is not on this server - SkyyHud is not installed.")); } catch (Throwable t) { }
    return;
  }
  if (k.startsWith("tab:")) {''')
# the "Some shortcuts did not fit" Right now row stays until the player opens Edit shortcuts (spillNote only tells chat + the info line once)
rep('''public void startEdit() {
  this.editing = true;''', '''public void startEdit() {
  @PKG@.MenuLayout.SPILL.remove(this.playerRef.getUuid().toString());   // fix: the 5 x 5 spill note is seen - Right now drops its row
  this.editing = true;''')

# ---------------------------------------------------------------------------------------------------------------- the ready line
rep('''Home + Edit shortcuts (kit 1.6 row 1, 7 x 5 grid, " + @PKG@.MenuLayout.MIGRATIONS + " layout update(s) at start); page guard on''',
    '''Home + Edit shortcuts (5 x 5 grid, big row 1, " + @PKG@.MenuLayout.MIGRATIONS + " + " + @PKG@.MenuLayout.FOLDS + " layout update(s) at start), " + @PKG@.MenuHub.PROXIES + " stand-in hub tab(s) (Smithing " + (@PKG@.MenuUtil.cmd("smithing") != null ? "opens /smithing" : "has no /smithing") + "); page guard on''')

# ---------------------------------------------------------------------------------------------------------------- done
for _w in ("UI_THINT", "UI_TGAP3", "UI_HNOWE", "HOME_BUILD", "TP_BUILD", "public static String twin(", "HUB_SOON[i])));\n      return \"soon\";\n"):
    assert _w not in s or _w.startswith("HUB_SOON"), "0.3.30: %s is still used" % _w
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:100]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.29 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.29 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
