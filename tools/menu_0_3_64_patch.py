"""Derive SkyyMenu/build_skyymenu_0.3.64.py + SkyyMenu/test_skyymenu_0.3.64.py from the SET pin SkyyMenu 0.3.63 (generated - never re-run
its patch). Run:  python tools/menu_0_3_64_patch.py   then   python SkyyMenu/build_skyymenu_0.3.64.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.64.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run).

0.3.64 (2026-11-22, round tab6) = TAB SCREENS ROUND 6: THE SETTINGS TAB - ONE SCREEN (your settings + HUD + Mods + Server Setup).
Skyy's words: 11-14 popup on research/ui-theme-art/tab-plan.png (12 tabs -> 7) "Yes, both"; 11-21 "build and deploy everything on your list",
"pc is back on if you wana keep building". Approved art: research/ui-theme-art/settings-page.png + README 'Tab pages' (Settings = SETTINGS
search + toggles, HUD LAYOUT, TOP TAB ORDER, MODS with Help, SERVER SETUP locked for non-admins) and the nothing-lost table (Settings >
Settings, HUD, Menu layout, Mods, Server Setup -> Settings). No new picture (tools/ci/ui_budget.py unchanged: this jar ships no new picture).
SURVEY: vanilla has no settings screen for server mods; no pack mod draws one. The screen reads ONLY what SkyyMenu already has (no other
mod changes): the Settings page's own registry + store (SetReg.visible / info / may, SetStore.get / set / resetAll, SoundSw.crouchChoice -
the same reads / writes as SettingsPage), the Mods list (MenuData.MOD_NAME, AdminPage.installed, MenuUtil.liveVersion, MenuHub.visible
"mods"), Server Setup's own mod list (AdminPage.cfgMods / hdr / hs, MenuUtil.isAdmin) and the command manager (/skyyhud).
  1. THE SETTINGS TAB of the inventory's top bar (and the skill page's / pets / market / world / social screen's Settings tab) opens the new
     SETTINGS SCREEN (SettingsTab: an inline Skyglass page, kit tools/skyyui.py, the inventory's frame + the same 7-tab top bar with
     Settings selected; coins in the bar):
     LEFT   SETTINGS: the search box (Find / Clear - every word in the key, label, help or tab name, like the old page; 2 letters at least),
            the category rail (only the categories with a row you may change), 9 rows a page (< Page >): name, help, ON / OFF (the double-tap
            crouch row: Fold quests / Open menu / Nothing - the old page's three-way choice), the category's 'always shown' line, your-
            settings hint (or the broken-file warning) and Reset all (click twice within 10 s) - every write = the old page's write
            (SetReg.may first, SetStore.set / resetAll, the same captions)
     RIGHT  HUD (Open HUD editor = /skyyhud as you, the page closed first - the Home shortcut's path; hidden when SkyyHud is not here) |
            MODS (the installed SkyWynn mods with versions, 12 shown; Mods page = the old page with each mod's help; same visibility as
            the old Mods tab: admins, or everyone while menu.modsHelp is on) | SERVER SETUP (ADMIN / LOCKED; admins: a button per mod with
            server settings - opens Server Setup on that mod, the Mods list's path - and Open Server Setup = the old hub tab; both re-check
            skyymenu.modconfig on the click)
     This page holds a page token: an ON / OFF / choice / Reset / HUD / Server Setup click from an older drawing = "The page changed"
     (nothing written); every write draws the page again (a new token), so a double click never writes twice.
  2. FALLBACK: the screen always opens; a missing SkyyHud / no mods list / not an admin = said on its card. 'Full page' (top bar) = today's
     Settings page (unchanged, /settings still opens it).
  NOT BUILT (next rounds, nothing half-wired): TOP TAB ORDER (README question 6 - needs a saved per-player order every screen's top bar
  reads), the HUD LAYOUT preview picture (art), a search inside Server Setup from this screen (Server Setup's own search stays), /settings
  opening this screen (the command keeps the old page = the 'Full page').
  New classes SettingsTabData + SettingsTab; no command, no setting, no lang key, no system, no saved data, no picture.
  ROLLBACK to 0.3.63: safe alone (nothing saved by the screen itself; the settings it writes are the old page's files).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.63.py"), os.path.join(MOD, "build_skyymenu_0.3.64.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.63.py"), os.path.join(MOD, "test_skyymenu_0.3.64.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.63"\n') and P.has("tools/menu_0_3_63_patch.py") and P.has("SocialTab")
assert not P.has("SettingsTab"), "not the generated SkyyMenu 0.3.63 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.63: THE SOCIAL TAB = ONE SCREEN''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.64: THE SETTINGS TAB = ONE SCREEN (SettingsTab: SETTINGS - search, categories, 9 rows a page with ON / OFF (the crouch row's three-way
       choice), Reset all - the old Settings page's reads / writes; HUD - Open HUD editor = /skyyhud; MODS - installed mods + Mods page; SERVER
       SETUP - ADMIN / LOCKED, a button per mod + Open Server Setup. 'Full page' = the old Settings page)
       (notes: tools/menu_0_3_64_patch.py). CHECKED: see SkyyMenu/test_skyymenu_0.3.64.py.
0.3.63: THE SOCIAL TAB = ONE SCREEN''')
P.rep('VERSION = "0.3.63"\n', 'VERSION = "0.3.64"\n')

# ---------- (1) the SETTINGS SCREEN markup (one page data list drawn by SettingsTab.build)
SG_PAGE = r'''
# ================= 0.3.64 THE SETTINGS TAB: ONE SCREEN (tools/menu_0_3_64_patch.py; approved art research/ui-theme-art/settings-page.png; popup
# 11-14 "Yes, both" on the 7 tabs) =================
# The inventory's frame and top bar (Settings selected); LEFT: your settings (search, categories, rows, Reset all); RIGHT: HUD | Mods | Server Setup.
SG = "SkyyGtab"
SG_L = 1000
SG_R = IV_IW - SG_L - IV_GAP                                # 546
SG_LI, SG_RI = SG_L - 20, SG_R - 20
SG_CW = 180                                                 # the category rail
SG_LW = SG_LI - SG_CW - 10                                  # the settings list (790)
SG_RN, SG_RH = 9, 58                                        # 9 rows a page (nothing scrolls)
SG_ONW, SG_CHW = 80, 100                                    # ON / OFF, the three choice buttons
SG_BW = 3 * (SG_CHW + 6)                                    # a row's button strip (each button has Left: 6)
SG_SPW = SG_BW - 2 * (SG_ONW + 6)                           # the spacer before ON / OFF (they sit on the right)
SG_TW = SG_LW - 20 - SG_BW - 10                             # a row's name column (the buttons sit right of it)
SG_DW = SG_LW - 20                                          # a row's help line: the row's full width, under the name + buttons (fix: 70 cut)
SG_DCLIP = 100                                              # the help line's cap = SetReg.register's own help cap (clip 100): help never cut here
SG_MH = 660                                                 # the rail + list row
SG_HH, SG_OH = 150, 290                                     # the HUD card, the Mods card
SG_SH = IV_BODY_H - SG_HH - SG_OH - 16                      # the Server Setup card
SG_MON = 12                                                 # mods shown (2 x 6)
SG_MCW = (SG_RI - 20) // 2
SG_SN, SG_SC = 15, 3                                        # Server Setup mod buttons (3 x 5)
SG_SW = (SG_RI - 3 * 4) // SG_SC
SG_CH = ["Fold quests", "Open menu", "Nothing"]             # the double-tap crouch choice (MenuData.STG_CH_LABELS order)
assert len(SG_CH) == len(STG_CH_LABELS) == 3, "0.3.64: the crouch row's three choices = the old page's"
SG_TXT = {
    "cap0": "Click ON or OFF - it saves at once. Tabs on top.",
    "hud1": "Move, resize, show or hide the widgets on your screen.",
    "hudon": "Opens the HUD editor (/skyyhud) - this page closes first.",
    "hudoff": "The HUD editor is not on this server right now.",
    "modson": "Each mod's help and commands: the Mods page.",
    "modsoff": "The mods list is for admins on this server.",
    "setup1": "Every mod's server settings - pick one or open the list.",
    "setup0": "Only admins change the server's settings here.",
    "setupnone": "No mod has server settings yet.",
    "noaccess": "You no longer have access to Server Setup.",
}
assert all(32 <= ord(c_) < 127 and c_ not in '"\\' for v_ in SG_TXT.values() for c_ in v_), "0.3.64: plain texts"
for _k in ("hud1", "hudon", "hudoff", "modson", "modsoff", "setup1", "setup0", "setupnone"):
    assert SUI.text_width(SG_TXT[_k], 13) <= SG_RI, ("0.3.64: a card line fits", _k)
for _l in SG_CH:
    assert SUI.text_width(_l, 13, bold=True) <= SG_CHW - 12, ("0.3.64: a choice label fits", _l)
for _l in ("ON", "OFF"):
    assert SUI.text_width(_l, 13, bold=True) <= SG_ONW - 12
for _t in SET_TABS:
    assert SUI.text_width(_t[1], 14, bold=True) <= SG_CW - 16, ("0.3.64: a category name fits the rail", _t[1])
# fix (critic: the 70-character cut lost help text): every known row's help shows WHOLE on the full-width help line, in the
# category view and in search (the longest "Tab (Mod): " prefix any category could give it)
_sg_lt = max((_t[1] for _t in SET_TABS), key=len)
for _k, _cat, _label, _help, _by in SET_KNOWN:
    assert len(_help) <= SG_DCLIP, ("0.3.64: a known row's help is never cut", _k, len(_help))
    _wp = "%s (%s): %s" % (_sg_lt, "SkyyCollections", _help)
    assert SUI.text_width(_wp, 12) <= SG_DW, ("0.3.64: a known row's help + search prefix fits the help line", _k, SUI.text_width(_wp, 12))
    assert SUI.text_width(_label, 15, bold=True) <= SG_TW, ("0.3.64: a known row's name fits", _k)
assert len(SET_TABS) * 36 <= SG_MH, "0.3.64: every category fits the rail"
# the run-time markup: a category button, a row button, the spacer before ON / OFF
SG_ST_TAB, SG_ST_SEL = SUI.glass_button_style("tab", 13), SUI.glass_button_style("tabSelected", 13)
SG_ST_TAB14, SG_ST_SEL14 = SUI.glass_button_style("tab", 14), SUI.glass_button_style("tabSelected", 14)
SG_CAT = "TextButton #SkyyGtab{I} { Anchor: (Width: %d, Height: 32, Bottom: 4); {S} }" % SG_CW
SG_BTN = "TextButton #SkyyGtab{I} { Anchor: (Width: {W}, Height: 30, Left: 6); {S} }"
SG_SPC = "Group { Anchor: (Width: {W}); }"
for _mk in (SG_CAT.replace("{I}", "Kt0").replace("{S}", SG_ST_SEL14), SG_BTN.replace("{I}", "R0on").replace("{W}", "80").replace("{S}", SG_ST_SEL),
            SG_BTN.replace("{I}", "R0c2").replace("{W}", "100").replace("{S}", SG_ST_TAB), SG_SPC.replace("{W}", "146")):
    SUI.check_markup(_mk, prefix=SG, kit_paths=True)
    assert "@" not in _mk and "\n" not in _mk, "0.3.64: a run-time markup line Java can hold"


def _sg_page():
    ap = SUI.Appends()
    G_ = SUI
    lab = G_.glass_label

    def head(parent, ident, title, w, right_w):
        hd = SG + ident
        ap.append(("#" + parent, G_.glass_group(hd, w, 24, layout="Left")))
        ap.append(("#" + hd, lab(None, title, 15, "accentHi", bold=True, w=w - right_w, h=24)))
        return hd
    ap.append((None, "Group #%s { Anchor: (Width: %d, Height: %d); }" % (SG, IV_PAGE_W, IV_PAGE_H)))
    win = SG + "Win"
    ap.append(("#" + SG, G_.glass_group(win, IV_W, IV_FRAME_H, role="frame", layout="Top", pad=IV_PAD,
                                         anchor={"left": (IV_PAGE_W - IV_W) // 2, "top": IV_FRAME_TOP})))   # under the top bar (0.3.60)
    # ---- the top bar: the same 7 tabs (Settings selected), Full page, coins, the X
    top = SG + "Top"
    ap.append(iv_bar(G_, "#" + SG, top))
    for i, (lb, _h, _t) in enumerate(IV_TABS):
        ap.append(("#" + top, G_.glass_button("%sT%d" % (SG, i), lb, "tabSelected" if i == 6 else "tab", w=IV_TAB_W, h=IV_TAB_H, size=16,
                                              anchor={"right": IV_TAB_GAP, "top": 2})))
    cw_ = IV_COIN_W + 96
    sp = IV_IW - len(IV_TABS) * (IV_TAB_W + IV_TAB_GAP) - 120 - 8 - cw_ - IV_X - 8
    assert sp >= 0, sp
    ap.append(("#" + top, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + top, G_.glass_button(SG + "Full", "Full page", "secondary", w=120, h=34, size=13, anchor={"right": 8, "top": 7})))
    ap.append(("#" + top, lab(SG + "Coins", "", 14, "xp", bold=True, w=cw_, h=IV_TOP_H, halign="End", anchor={"right": 8})))
    ap.append(("#" + top, G_.glass_button(SG + "Close", "X", "close", w=IV_X, h=IV_X, size=16, anchor={"top": 4})))
    body = SG + "Body"
    ap.append(("#" + win, G_.glass_group(body, IV_IW, IV_BODY_H, layout="Left")))
    # ======== LEFT: SETTINGS (the old Settings page: search, categories, rows, Reset all)
    le = SG + "Le"
    ap.append(("#" + body, G_.glass_group(le, SG_L, IV_BODY_H, role="panel", layout="Top", pad=10)))
    sh = head(le, "Sh", "SETTINGS", SG_LI, 260)
    ap.append(("#" + sh, lab(SG + "Sc", "", 12, "xp", bold=True, w=260, h=24, halign="End")))
    srow = SG + "Srow"
    ap.append(("#" + le, G_.glass_group(srow, SG_LI, 32, layout="Left", anchor={"top": 6})))
    ap.append(("#" + srow, G_.text_field(SG + "QBox", SG + "Q", w=SG_LI - 128, h=32, placeholder="Search your settings", max_length=40, size=13)))
    ap.append(("#" + srow, G_.glass_button(SG + "Find", "Find", "secondary", w=60, h=32, size=13, anchor={"left": 4})))
    ap.append(("#" + srow, G_.glass_button(SG + "Fx", "Clear", "secondary", w=60, h=32, size=13, anchor={"left": 4})))
    mr = SG + "Mr"
    ap.append(("#" + le, G_.glass_group(mr, SG_LI, SG_MH, layout="Left", anchor={"top": 8})))
    ap.append(("#" + mr, G_.glass_group(SG + "Cats", SG_CW, SG_MH, layout="Top", anchor={"right": 10})))
    ls = SG + "Ls"
    ap.append(("#" + mr, G_.glass_group(ls, SG_LW, SG_MH, layout="Top")))
    ap.append(("#" + ls, lab(SG + "Lh", "", 15, "title", bold=True, w=SG_LW, h=24)))
    rws = SG + "Rows"
    ap.append(("#" + ls, G_.glass_group(rws, SG_LW, SG_RN * (SG_RH + 4), layout="Top", anchor={"top": 6})))
    for k_ in range(SG_RN):
        rw = "%sR%d" % (SG, k_)
        ap.append(("#" + rws, G_.glass_group(rw, SG_LW, SG_RH, role="inset", layout="Left", pad={"horizontal": 10}, anchor={"bottom": 4})))
        rx = rw + "X"     # the top line: name | buttons; the help line below it uses the row's full width
        ap.append(("#" + rw, G_.glass_group(rx, SG_DW, 30, layout="Left", anchor={"top": 4})))
        ap.append(("#" + rx, lab(rw + "N", "", 15, "row", bold=True, w=SG_TW, h=30, anchor={"right": 10})))
        ap.append(("#" + rx, G_.glass_group(rw + "B", SG_BW, 30, layout="Left")))
        ap.append(("#" + rw, lab(rw + "D", "", 12, "dim", w=SG_DW, h=22)))
    assert SG_TW + 10 + SG_BW <= SG_DW and 20 + SG_DW <= SG_LW and 4 + 30 + 22 <= SG_RH, "0.3.64: a settings row fits"
    pr_ = SG + "Pr"
    ap.append(("#" + ls, G_.glass_group(pr_, SG_LW, 30, layout="Left", anchor={"top": 6})))
    ap.append(("#" + pr_, G_.glass_button(SG + "Pp", "<", "secondary", w=36, h=28, size=14, anchor={"right": 4})))
    ap.append(("#" + pr_, lab(SG + "Pg", "", 12, "text", bold=True, w=110, h=28, halign="Center")))
    ap.append(("#" + pr_, G_.glass_button(SG + "Pn", ">", "secondary", w=36, h=28, size=14, anchor={"left": 4})))
    ap.append(("#" + ls, lab(SG + "Al", "", 12, "dim", w=SG_LW, h=20, anchor={"top": 6})))
    assert 24 + 6 + SG_RN * (SG_RH + 4) + 6 + 30 + 6 + 20 <= SG_MH, "0.3.64: the settings list fits"
    ft = SG + "Ft"
    ap.append(("#" + le, G_.glass_group(ft, SG_LI, 34, layout="Left", anchor={"top": 8})))
    ap.append(("#" + ft, lab(SG + "St", "", 13, "text", w=SG_LI - 170, h=34, anchor={"right": 10})))
    ap.append(("#" + ft, G_.glass_button(SG + "Reset", "Reset all", "secondary", w=160, h=34, size=14)))
    assert 20 + 24 + 6 + 32 + 8 + SG_MH + 8 + 34 <= IV_BODY_H, "0.3.64: the settings panel fits"
    ap.append(("#" + body, "Group { Anchor: (Width: %d); }" % IV_GAP))
    # ======== RIGHT: HUD | MODS | SERVER SETUP
    rt = SG + "Rt"
    ap.append(("#" + body, G_.glass_group(rt, SG_R, IV_BODY_H, layout="Top")))
    hu = SG + "Hu"
    ap.append(("#" + rt, G_.glass_group(hu, SG_R, SG_HH, role="panel", layout="Top", pad=10)))
    ap.append(("#" + hu, lab(None, "HUD", 15, "accentHi", bold=True, w=SG_RI, h=24)))
    ap.append(("#" + hu, lab(SG + "H1", "", 13, "text", w=SG_RI, h=20, anchor={"top": 6})))
    ap.sets.append((SG + "H1", "Text", SG_TXT["hud1"]))
    ap.append(("#" + hu, lab(SG + "H2", "", 12, "dim", w=SG_RI, h=18)))
    ap.append(("#" + hu, G_.glass_button(SG + "Hud", "Open HUD editor", "primary", w=200, h=34, size=14, anchor={"top": 10})))
    assert 20 + 24 + 26 + 18 + 44 <= SG_HH, "0.3.64: the HUD card fits"
    mo = SG + "Mo"
    ap.append(("#" + rt, G_.glass_group(mo, SG_R, SG_OH, role="panel", layout="Top", pad=10, anchor={"top": 8})))
    mh = head(mo, "Mh", "MODS", SG_RI, 200)
    ap.append(("#" + mh, lab(SG + "Mc", "", 12, "xp", bold=True, w=200, h=24, halign="End")))
    mg = SG + "Mg"
    rows_ = SG_MON // 2
    ap.append(("#" + mo, G_.glass_group(mg, SG_RI, rows_ * 24, layout="Left", anchor={"top": 8})))
    for c_ in range(2):
        col_ = "%sMg%d" % (SG, c_)
        ap.append(("#" + mg, G_.glass_group(col_, SG_MCW, rows_ * 24, layout="Top", anchor={"right": 20} if c_ == 0 else None)))
        for r_ in range(rows_):
            ap.append(("#" + col_, lab("%sM%d" % (SG, c_ * rows_ + r_), "", 13, "row", w=SG_MCW, h=24)))
    ap.append(("#" + mo, lab(SG + "Mn", "", 12, "dim", w=SG_RI, h=18, anchor={"top": 6})))
    ap.append(("#" + mo, G_.glass_button(SG + "Mpage", "Mods page", "secondary", w=160, h=34, size=14, anchor={"top": 8})))
    assert 20 + 24 + 8 + rows_ * 24 + 24 + 42 <= SG_OH and 2 * SG_MCW + 20 <= SG_RI, "0.3.64: the mods card fits"
    se = SG + "Se"
    ap.append(("#" + rt, G_.glass_group(se, SG_R, SG_SH, role="panel", layout="Top", pad=10, anchor={"top": 8})))
    seh = head(se, "Seh", "SERVER SETUP", SG_RI, 160)
    ap.append(("#" + seh, lab(SG + "Sb", "", 13, "xp", bold=True, w=160, h=24, halign="End")))
    ap.append(("#" + se, lab(SG + "Sl", "", 13, "text", w=SG_RI, h=20, anchor={"top": 6})))
    sg_ = SG + "Sg"
    srn = SG_SN // SG_SC
    ap.append(("#" + se, G_.glass_group(sg_, SG_RI, srn * 34, layout="Top", anchor={"top": 8})))
    for r_ in range(srn):
        sr = "%sSr%d" % (SG, r_)
        ap.append(("#" + sg_, G_.glass_group(sr, SG_RI, 34, layout="Left")))
        for c_ in range(SG_SC):
            ap.append(("#" + sr, G_.glass_button("%sS%d" % (SG, r_ * SG_SC + c_), "", "secondary", w=SG_SW, h=30, size=13,
                                                 anchor={"right": 4, "bottom": 4})))
    ap.append(("#" + se, lab(SG + "Sn", "", 12, "dim", w=SG_RI, h=18, anchor={"top": 6})))
    ap.append(("#" + se, G_.glass_button(SG + "Spage", "Open Server Setup", "primary", w=220, h=34, size=14, anchor={"top": 8})))
    assert 20 + 24 + 26 + 8 + srn * 34 + 24 + 42 <= SG_SH and SG_SC * (SG_SW + 4) <= SG_RI, "0.3.64: the server setup card fits"
    assert (IV_PAGE_H <= SUI.MAX_PAGE_H and IV_PAGE_W <= SUI.MAX_PAGE_W and SG_HH + 8 + SG_OH + 8 + SG_SH == IV_BODY_H
            and SG_L + SG_R + IV_GAP == IV_IW), "0.3.64: the settings screen fits one 1080p screen"
    # ---- the caption + key hints
    hn = SG + "Hints"
    ap.append(("#" + win, G_.glass_group(hn, IV_IW, IV_HINT_H, layout="Left", anchor={"top": 6})))
    parts = [G_.glass_key_hint(SG + "Kh%d" % k_, k, t, h=IV_HINT_H) for k_, (k, t) in enumerate((("LMB", "Pick / switch"), ("Tab / Esc", "Close")))]
    hw = sum(w_ for _m, w_ in parts)
    ap.append(("#" + hn, lab(SG + "Cap", "", 14, "dim", w=IV_IW - hw - 20, h=IV_HINT_H)))
    assert SUI.text_width(SG_TXT["cap0"], 14) <= IV_IW - hw - 20, "0.3.64: the caption fits the caption line"
    for mk_, _w in parts:
        ap.append(("#" + hn, mk_))
    binds = [("#%sT%d" % (SG, i), "tab:%d" % i) for i in range(len(IV_TABS))] + [("#" + SG + "Close", "close"), ("#" + SG + "Full", "full"),
                                                                                  ("#" + SG + "Pp", "pg:-1"), ("#" + SG + "Pn", "pg:1"),
                                                                                  ("#" + SG + "Fx", "fclear"), ("#" + SG + "Mpage", "mods"),
                                                                                  ("#" + SG + "Spage", "setup")]
    return ap, binds


SG_AP, SG_BINDS = _sg_page()
SUI.check_page(SG_AP, SG)
for _p, _mk in SG_AP:
    SUI.check_markup(_mk, prefix=SG, root=(_p is None), kit_paths=True)
    assert "Scrolling" not in SUI.render(_mk), "0.3.64: the settings screen never scrolls"
_sg_ids = set(i_ for _p, mk_ in SG_AP for i_ in SUI._static_ids(mk_))
for _s, _a in SG_BINDS:
    assert _s[1:] in _sg_ids, ("0.3.64: binding target", _s)
SG_DYN = (["Coins", "Close", "Full", "Cap", "Sc", "Q", "Find", "Fx", "Cats", "Lh", "Rows", "Pp", "Pg", "Pn", "Al", "St", "Reset", "H1", "H2", "Hud",
           "Mc", "Mn", "Mpage", "Sb", "Sl", "Sn", "Spage"]
          + ["R%d%s" % (k_, x_) for k_ in range(SG_RN) for x_ in ("", "N", "D", "B")]
          + ["M%d" % k_ for k_ in range(SG_MON)]
          + ["S%d" % k_ for k_ in range(SG_SN)])
for _g in SG_DYN:
    assert SG + _g in _sg_ids, "0.3.64: the settings screen has #" + SG + _g
_sg_tok = SUI.proven_tokens(list(SG_AP))
SG_UNPROVEN = sorted(k_ for k_, g_ in _sg_tok.items() if g_ == "unknown" or (g_ is not None and not all(x in SUI.PROBED for x in g_)))
assert set(SG_UNPROVEN) <= set(["SlotBackground"]), "0.3.64: only SlotBackground (proven on the inventory page, TEST 282): %s" % SG_UNPROVEN
assert not [k_ for k_ in _sg_tok if k_ in ("MouseEntered", "MouseExited", "TooltipText")], "0.3.64: no hover events / tooltips of ours"
SUI.assert_glass_paths(SG_AP)
_sg_glass = set(re.findall(r"SkyyGlass/([A-Za-z0-9]+)\.png", " ".join(SUI.render(mk_) for _p, mk_ in SG_AP)))
assert _sg_glass <= _mt_glass, ("0.3.64: the settings screen names only Skyglass pictures the market screen already ships (no new picture)", sorted(_sg_glass - _mt_glass))
SG_SHELL_ELEMENTS = sum(len(re.findall(r"(?:^|(?<=[;{}]))\s*[A-Z][A-Za-z]*(?:\s+#[A-Za-z0-9]+)?\s*\{", SUI._strip_quoted(SUI.render(mk_)))) for _p, mk_ in SG_AP)
SG_RUNTIME_MAX = len(SET_TABS) + SG_RN * 3                    # a category button each + per row ON / OFF + spacer, or the three choices
SG_ELEMENTS = SG_SHELL_ELEMENTS + SG_RUNTIME_MAX
assert SG_ELEMENTS <= 800, "0.3.64: the settings screen stays well under the ~1,600 element budget (%d static + %d at run time)" % (SG_SHELL_ELEMENTS, SG_RUNTIME_MAX)
SG_LK, SG_LP, SG_LB = [], [], []
for _p, _mk in SG_AP:
    SG_LK.append("A")
    SG_LP.append("" if _p is None else SUI.render(_p if _p.startswith("#") else "#" + _p))
    SG_LB.append(SUI.render(_mk))
for _i, _pr, _v in SG_AP.sets:
    SG_LK.append("S")
    SG_LP.append("#%s.%s" % (SUI.render(_i).lstrip("#"), _pr))
    SG_LB.append(_v)
for _s, _a in SG_BINDS:
    SG_LK.append("E")
    SG_LP.append(_s)
    SG_LB.append(_a)
assert SG_LK[0] == "A" and SG_LP[0] == "", "0.3.64: the page data starts with the root"
for _x in SG_LP + SG_LB:
    assert "@" not in _x and "\n" not in _x and len(_x.encode("utf-8")) < 60000, "0.3.64: a page line Java can hold"
print("0.3.64 settings screen: %d elements (shell %d + at most %d at run time; budget ~1,600), %d appends, %d b.set, %d bindings; unproven: %s"
      % (SG_ELEMENTS, SG_SHELL_ELEMENTS, SG_RUNTIME_MAX, len(SG_AP), len(SG_AP.sets), len(SG_BINDS), ", ".join(SG_UNPROVEN)))

'''
P.rep('''PKG = T["PKG"]
# 0.2: every class goes through mk()''', SG_PAGE.lstrip("\n") + '''PKG = T["PKG"]
# 0.2: every class goes through mk()''')

# ---------- the two new classes
P.rep('''stab = mk("SocialTab", T["PAGE"])   # 0.3.63: THE SOCIAL TAB = ONE SCREEN
''', '''stab = mk("SocialTab", T["PAGE"])   # 0.3.63: THE SOCIAL TAB = ONE SCREEN
sgd  = mk("SettingsTabData")   # 0.3.64: the settings screen's data (LK / LP / LB, the run-time markup)
sgt  = mk("SettingsTab", T["PAGE"])   # 0.3.64: THE SETTINGS TAB = ONE SCREEN
''')
P.rep('''wtd, wtab, scd, stab, pl)''', '''wtd, wtab, scd, stab, sgd, sgt, pl)''')

# ---------- SettingsTabData constants + SettingsTab fields / constructor (after the SocialTab constructor)
SG_DATA = r'''# 0.3.64: THE SETTINGS SCREEN DATA (SettingsTabData) + the SettingsTab fields
F(sgd, "public static final String LK = %s;" % jstr("".join(SG_LK)))
F(sgd, "public static final String[] LP = %s;" % jarr(SG_LP))
F(sgd, "public static final String[] LB = %s;" % jarr(SG_LB))
for _n, _v in (("RN", SG_RN), ("MON", SG_MON), ("SN", SG_SN), ("ONW", SG_ONW), ("CHW", SG_CHW), ("SPW", SG_SPW), ("DCLIP", SG_DCLIP)):
    F(sgd, "public static final int %s = %d;" % (_n, _v))
for _n, _v in (("CAT", SG_CAT), ("BTN", SG_BTN), ("SPC", SG_SPC), ("ST_TAB", SG_ST_TAB), ("ST_SEL", SG_ST_SEL), ("ST_TAB14", SG_ST_TAB14),
               ("ST_SEL14", SG_ST_SEL14), ("CAP0", SG_TXT["cap0"]), ("HUDON", SG_TXT["hudon"]), ("HUDOFF", SG_TXT["hudoff"]),
               ("MODSON", SG_TXT["modson"]), ("MODSOFF", SG_TXT["modsoff"]), ("SETUP1", SG_TXT["setup1"]), ("SETUP0", SG_TXT["setup0"]),
               ("SETUPNONE", SG_TXT["setupnone"]), ("NOACCESS", SG_TXT["noaccess"])):
    F(sgd, "public static final String %s = %s;" % (_n, jstr(_v)))
F(sgd, "public static final String[] CH = %s;" % jarr(SG_CH))
for _f in ("public static volatile int OPENS = 0;", "public static volatile int STALE = 0;", "public static volatile int ACTS = 0;",
           "public volatile boolean closed;", "public boolean answered;", "public String via;", "public String tcap;", "public long seq;", "public long base;",
           "public String tok;", "public int cat;", "public int page;", "public int pages;", "public String query;", "public String draft;",
           "public String[] rowKeys;", "public long armedAt;", "public boolean drained;", "public String[] mods;",
           "public @REF@ pref;", "public @ST@ pst;", "public int builds;", "public int answers;"):
    F(sgt, _f)
C(sgt, r"""
public SettingsTab(@PR@ pr, String via) {
  super(pr, @LIFE@.CanDismiss);
  this.via = via;
  this.closed = false;
  this.answered = false;
  this.tcap = "";
  this.seq = 0L;
  this.base = System.nanoTime() & 0xffffffL;
  this.tok = "";
  this.cat = -1;
  this.page = 0;
  this.pages = 1;
  this.query = "";
  this.draft = "";
  this.rowKeys = new String[0];
  this.armedAt = 0L;
  this.drained = false;
  this.mods = new String[0];
  this.builds = 0;
  this.answers = 0;
}""")
'''
P.rep('''  this.fnames = new String[0];
  this.builds = 0;
  this.answers = 0;
}""")
''', '''  this.fnames = new String[0];
  this.builds = 0;
  this.answers = 0;
}""")
''' + SG_DATA)

# ---------- SettingsTab.open BEFORE the social screen's open (every caller below can reach it)
SG_OPEN = r'''# ---- 0.3.64: the SETTINGS SCREEN opens (the inventory's / skill page's / pets / market / world / social screen's Settings tab); null = it
# could not open = the caller opens today's Settings page instead. Needs no bridge key.
M(sgt, r"""
public static @PKG@.SettingsTab open(@REF@ ref, @ST@ st, @PR@ pr, String via) {
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null || pr == null) return null;
  @PKG@.SettingsTab pg = new @PKG@.SettingsTab(pr, via);
  pg.pref = ref;
  pg.pst = st;
  try { p.getPageManager().openCustomPage(ref, st, pg); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("settings screen could not open for " + pr.getUsername() + ": " + t); pg.closed = true; return null; }
  OPENS = OPENS + 1;
  return pg;
}""")
'''
P.rep('''# ---- 0.3.63: the SOCIAL SCREEN opens (the inventory's / skill page's / pets / market / world screen's Social tab); null = it could not open =
''', SG_OPEN + '''# ---- 0.3.63: the SOCIAL SCREEN opens (the inventory's / skill page's / pets / market / world screen's Social tab); null = it could not open =
''')
# the skill page's Settings tab = this screen (else today's route, as before)
P.rep('''M(skpg, r"""
public void tabGo(int i) {
  if (i == 0) { toInv("c", -1); return; }''', '''# 0.3.64: the Settings tab = the settings screen (false = it could not open: today's route below)
M(skpg, r"""
public boolean settingsTab() {
  @PKG@.SettingsTab pg = null;
  try { pg = @PKG@.SettingsTab.open(this.pref, this.pst, this.playerRef, "skill page"); } catch (Throwable t) { pg = null; @PKG@.MenuUtil.warn("skill page: the settings screen failed: " + t); }
  if (pg == null) return false;
  this.answered = true;
  if (!still()) finish("settings");
  return true;
}""")
M(skpg, r"""
public void tabGo(int i) {
  if (i == 0) { toInv("c", -1); return; }''')
P.rep('''  if (i == 5 && socialTab()) return;   // 0.3.63
''', '''  if (i == 5 && socialTab()) return;   // 0.3.63
  if (i == 6 && settingsTab()) return;   // 0.3.64
''')
# the pets / market / world screen's Settings tab = this screen
for _who in ("pets screen", "market screen", "world screen"):
    P.rep('''    try { so = @PKG@.SocialTab.open(this.pref, this.pst, this.playerRef, "%s"); } catch (Throwable t) { so = null; @PKG@.MenuUtil.warn("%s: the social screen failed: " + t); }
    if (so != null) { if (!still()) finish("social"); return; }
  }
''' % (_who, _who), '''    try { so = @PKG@.SocialTab.open(this.pref, this.pst, this.playerRef, "%s"); } catch (Throwable t) { so = null; @PKG@.MenuUtil.warn("%s: the social screen failed: " + t); }
    if (so != null) { if (!still()) finish("social"); return; }
  }
  if (i == 6) {   // 0.3.64: the settings screen (else today's route below)
    @PKG@.SettingsTab sg = null;
    try { sg = @PKG@.SettingsTab.open(this.pref, this.pst, this.playerRef, "%s"); } catch (Throwable t) { sg = null; @PKG@.MenuUtil.warn("%s: the settings screen failed: " + t); }
    if (sg != null) { if (!still()) finish("settings"); return; }
  }
''' % (_who, _who, _who, _who))
# the social screen's Settings tab = this screen
P.rep('''  if (i == 5) { say("You are on Social"); return; }
''', '''  if (i == 5) { say("You are on Social"); return; }
  if (i == 6) {   // 0.3.64: the settings screen (else today's route below)
    @PKG@.SettingsTab sg = null;
    try { sg = @PKG@.SettingsTab.open(this.pref, this.pst, this.playerRef, "social screen"); } catch (Throwable t) { sg = null; @PKG@.MenuUtil.warn("social screen: the settings screen failed: " + t); }
    if (sg != null) { if (!still()) finish("settings"); return; }
  }
''')

SG_JAVA = r'''# ================= 0.3.64 SettingsTab: THE SETTINGS TAB = ONE SCREEN (approved settings-page.png) =================
# Reads / writes only what the old Settings page does (SetReg.visible / info / may, SetStore.get / set / resetAll, SoundSw.crouchChoice) +
# the Mods list (MenuData.MOD_NAME, AdminPage.installed) + Server Setup's mod list (AdminPage.cfgMods / hdr / hs) + /skyyhud. Every click
# answers with ONE page packet; every write carries the page token.
M(sgt, r"""
public void say(String cap) {
  @UCB@ ub = new @UCB@();
  this.tcap = cap == null ? "" : cap;
  ub.set("#SkyyGtabCap.Text", this.tcap);
  this.answered = true;
  this.answers = this.answers + 1;
  this.sendUpdate(ub);
}""")
M(sgt, r"""
public void finish(String why) { this.closed = true; }""")
M(sgt, r"""
public void shut() { finish("closed"); this.close(); }""")
M(sgt, r"""
public boolean still() {
  try {
    @PLA@ p = (@PLA@) this.pst.getComponent(this.pref, @PLA@.getComponentType());
    return p != null && p.getPageManager().getCustomPage() == this;
  } catch (Throwable t) { return false; }
}""")
M(sgt, r"""
public void redraw() {
  this.answered = true;
  if (!still()) { finish("replaced"); return; }
  this.answers = this.answers + 1;
  this.rebuild();
}""")
# every write carries the page token and the search box (a draft survives any click, like the old page)
M(sgt, r"""
public @EVD@ evd(String a) {
  return @EVD@.of("a", a).append("t", this.tok).append(String.valueOf((char) 64) + "Q", "#SkyyGtabQ.Value");
}""")
# the search text: letters, digits, space, . - _ only, at most 40 characters
M(sgt, r"""
public static String clean(String s) {
  if (s == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length() && sb.length() < 40; i++) {
    char c = s.charAt(i);
    if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == ' ' || c == '.' || c == '-' || c == '_') sb.append(c);
  }
  return sb.toString().trim();
}""")
# SETTINGS: the old page's rows (SetReg.visible per category = only what this player may change), its search (every word in key, tab name,
# label, help), 9 a page; ON / OFF (the crouch row: the three choices, SoundSw.crouchChoice), the category's always-shown line
M(sgt, r"""
public void fillSettings(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = this.playerRef.getUuid();
  int nCat = @PKG@.MenuData.SET_CAT_ID.length;
  Object[] vis = new Object[nCat];
  int first = -1;
  int total = 0;
  for (int i = 0; i < nCat; i++) {
    String[] vk = @PKG@.SetReg.visible(i, u);
    vis[i] = vk;
    total = total + vk.length;
    if (first < 0 && vk.length > 0) first = i;
  }
  if (this.cat < 0 || this.cat >= nCat || (first >= 0 && ((String[]) vis[this.cat]).length == 0)) {
    this.cat = first >= 0 ? first : 0;
    this.page = 0;
  }
  String q = this.query == null ? "" : this.query;
  boolean find = q.length() >= 2;
  java.util.ArrayList ks = new java.util.ArrayList();
  java.util.ArrayList ts = new java.util.ArrayList();
  for (int i = 0; i < nCat; i++) {
    if (!find && i != this.cat) continue;
    String[] vk = (String[]) vis[i];
    for (int k = 0; k < vk.length; k++) {
      if (find) {
        Object[] d = @PKG@.SetReg.info(vk[k]);
        String hay = vk[k] + " " + @PKG@.MenuData.SET_TAB[i] + (d == null ? "" : " " + String.valueOf(d[2]) + " " + String.valueOf(d[5]));
        if (!@PKG@.SettingsPage.words(hay, q)) continue;
      }
      ks.add(vk[k]);
      ts.add(Integer.valueOf(i));
    }
  }
  int n = ks.size();
  b.set("#SkyyGtabSc.Text", total == 1 ? "1 setting" : total + " settings");
  for (int i = 0; i < nCat; i++) {
    if (((String[]) vis[i]).length == 0) continue;
    boolean on = !find && i == this.cat;
    b.appendInline("#SkyyGtabCats", @PKG@.SettingsTabData.CAT.replace("{I}", "Kt" + i).replace("{S}", on ? @PKG@.SettingsTabData.ST_SEL14 : @PKG@.SettingsTabData.ST_TAB14));
    b.set("#SkyyGtabKt" + i + ".Text", @PKG@.MenuData.SET_TAB[i]);
    ev.addEventBinding(@BT@.Activating, "#SkyyGtabKt" + i, evd("cat:" + i));
  }
  int rn = @PKG@.SettingsTabData.RN;
  this.pages = n == 0 ? 1 : (n + rn - 1) / rn;
  if (this.page >= this.pages) this.page = this.pages - 1;
  if (this.page < 0) this.page = 0;
  int from = this.page * rn;
  b.set("#SkyyGtabLh.Text", (find ? "Search: " + @PKG@.MenuUtil.clip(q, 30) : @PKG@.MenuData.SET_HEAD[this.cat]) + "   -   " + n + (n == 1 ? " setting" : " settings"));
  b.set("#SkyyGtabPg.Text", "Page " + (this.page + 1) + " / " + this.pages);
  this.rowKeys = new String[rn];
  for (int r = 0; r < rn; r++) {
    String rw = "SkyyGtabR" + r;
    int j = from + r;
    if (j >= n) {
      boolean none = n == 0 && r == 0;
      b.set("#" + rw + ".Visible", none);
      if (none) {
        b.set("#" + rw + "N.Text", find ? "Nothing matches" : "Nothing to switch here yet");
        b.set("#" + rw + "D.Text", @PKG@.MenuUtil.clip(find ? @PKG@.MenuData.SET_TXT_NOFIND : @PKG@.MenuData.SET_TXT_EMPTY, @PKG@.SettingsTabData.DCLIP));
      }
      continue;
    }
    String key = (String) ks.get(j);
    this.rowKeys[r] = key;
    Object[] d = @PKG@.SetReg.info(key);
    Boolean v = @PKG@.SetStore.get(u, key);
    boolean on = v == null || v.booleanValue();
    boolean ch3 = @PKG@.MenuData.HOTKEY_KEY.equals(key);
    b.set("#" + rw + ".Visible", true);
    b.set("#" + rw + "N.Text", @PKG@.MenuUtil.clip(d == null ? key : String.valueOf(d[2]), 40));
    String desc = d == null ? "" : String.valueOf(d[5]);
    if (find) {
      int ti = ((Integer) ts.get(j)).intValue();
      String own = d == null || d[0] == null ? "SkyyMenu" : String.valueOf(d[0]);
      String pre = @PKG@.MenuData.SET_TAB[ti] + ("SkyyMenu".equals(own) ? "" : " (" + @PKG@.MenuUtil.clip(own, 24) + ")") + ": ";
      desc = pre + @PKG@.MenuUtil.clip(desc, @PKG@.SettingsTabData.DCLIP);
    } else desc = @PKG@.MenuUtil.clip(desc, @PKG@.SettingsTabData.DCLIP);
    b.set("#" + rw + "D.Text", desc);
    String bx = "#" + rw + "B";
    if (ch3) {
      int cv = @PKG@.SoundSw.crouchChoice(u);
      for (int c = 0; c < 3; c++) {
        String id = "R" + r + "c" + c;
        b.appendInline(bx, @PKG@.SettingsTabData.BTN.replace("{I}", id).replace("{W}", String.valueOf(@PKG@.SettingsTabData.CHW))
            .replace("{S}", c == cv ? @PKG@.SettingsTabData.ST_SEL : @PKG@.SettingsTabData.ST_TAB));
        b.set("#SkyyGtab" + id + ".Text", @PKG@.SettingsTabData.CH[c]);
        ev.addEventBinding(@BT@.Activating, "#SkyyGtab" + id, evd("ch:" + r + ":" + c));
      }
    } else {
      b.appendInline(bx, @PKG@.SettingsTabData.SPC.replace("{W}", String.valueOf(@PKG@.SettingsTabData.SPW)));
      String w = String.valueOf(@PKG@.SettingsTabData.ONW);
      b.appendInline(bx, @PKG@.SettingsTabData.BTN.replace("{I}", "R" + r + "on").replace("{W}", w).replace("{S}", on ? @PKG@.SettingsTabData.ST_SEL : @PKG@.SettingsTabData.ST_TAB));
      b.appendInline(bx, @PKG@.SettingsTabData.BTN.replace("{I}", "R" + r + "of").replace("{W}", w).replace("{S}", on ? @PKG@.SettingsTabData.ST_TAB : @PKG@.SettingsTabData.ST_SEL));
      b.set("#SkyyGtabR" + r + "on.Text", "ON");
      b.set("#SkyyGtabR" + r + "of.Text", "OFF");
      ev.addEventBinding(@BT@.Activating, "#SkyyGtabR" + r + "on", evd("on:" + r));
      ev.addEventBinding(@BT@.Activating, "#SkyyGtabR" + r + "of", evd("off:" + r));
    }
  }
  b.set("#SkyyGtabAl.Text", @PKG@.MenuUtil.clip(find ? @PKG@.MenuData.SET_TXT_FIND : @PKG@.MenuData.SET_ALWAYS[this.cat], 125));
  boolean armed = this.armedAt > 0L && System.currentTimeMillis() - this.armedAt <= 10000L;
  b.set("#SkyyGtabSt.Text", @PKG@.SetStore.isBroken(u) ? @PKG@.MenuData.SET_TXT_BROKEN : @PKG@.MenuData.SET_TXT_HINT);
  b.set("#SkyyGtabReset.Text", armed ? "Click again" : "Reset all");
  ev.addEventBinding(@BT@.Activating, "#SkyyGtabReset", evd("reset"));
  String dr = this.draft == null ? "" : this.draft;
  if (dr.length() > 0) b.set("#SkyyGtabQ.Value", dr);
  ev.addEventBinding(@BT@.Validating, "#SkyyGtabQ", evd("find"), false);
  ev.addEventBinding(@BT@.Activating, "#SkyyGtabFind", evd("find"));
}""")
# HUD: Open HUD editor = /skyyhud as the player (the Home shortcut's path, MenuPage.shortcut "tab:settings:hud"); hidden without the command
M(sgt, r"""
public void fillHud(@UCB@ b, @UEB@ ev) {
  boolean on = @PKG@.MenuUtil.cmd("skyyhud") != null;
  b.set("#SkyyGtabH2.Text", on ? @PKG@.SettingsTabData.HUDON : @PKG@.SettingsTabData.HUDOFF);
  b.set("#SkyyGtabHud.Visible", on);
  if (on) ev.addEventBinding(@BT@.Activating, "#SkyyGtabHud", evd("hud"));
}""")
# MODS: the installed SkyWynn mods (the Mods list's own test: a live version or its command), the same visibility as the old Mods tab
M(sgt, r"""
public void fillMods(@UCB@ b) {
  boolean vis = @PKG@.MenuHub.visible("mods", this.playerRef);
  java.util.ArrayList ls = new java.util.ArrayList();
  if (vis) {
    for (int k = 0; k < @PKG@.MenuData.MOD_NAME.length; k++) {
      if (!@PKG@.AdminPage.installed(k)) continue;
      String lv = @PKG@.MenuUtil.liveVersion(@PKG@.MenuData.MOD_NAME[k]);
      ls.add(@PKG@.MenuData.MOD_NAME[k] + " " + (lv != null ? lv : @PKG@.MenuData.MOD_VER[k]));
    }
  }
  int n = ls.size();
  int m = @PKG@.SettingsTabData.MON;
  b.set("#SkyyGtabMc.Text", vis ? n + " installed" : "");
  for (int k = 0; k < m; k++) {
    String e = "#SkyyGtabM" + k;
    if (k >= n) { b.set(e + ".Visible", false); continue; }
    b.set(e + ".Visible", true);
    b.set(e + ".Text", k == m - 1 && n > m ? "+" + (n - m + 1) + " more on the Mods page" : @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe((String) ls.get(k)), 30));
  }
  b.set("#SkyyGtabMn.Text", vis ? @PKG@.SettingsTabData.MODSON : @PKG@.SettingsTabData.MODSOFF);
  b.set("#SkyyGtabMpage.Visible", vis);
}""")
# SERVER SETUP: admins (skyymenu.modconfig, MenuUtil.isAdmin) see a button per mod with a readable config:def (AdminPage.cfgMods) + the list
M(sgt, r"""
public void fillSetup(@UCB@ b, @UEB@ ev) {
  boolean adm = @PKG@.MenuUtil.isAdmin(this.playerRef);
  b.set("#SkyyGtabSb.Text", adm ? "ADMIN" : "LOCKED");
  b.set("#SkyyGtabSl.Text", adm ? @PKG@.SettingsTabData.SETUP1 : @PKG@.SettingsTabData.SETUP0);
  String[] ms = adm ? @PKG@.AdminPage.cfgMods() : new String[0];
  int sn = @PKG@.SettingsTabData.SN;
  this.mods = new String[sn];
  for (int k = 0; k < sn; k++) {
    String e = "#SkyyGtabS" + k;
    if (k >= ms.length) { b.set(e + ".Visible", false); continue; }
    this.mods[k] = ms[k];
    Object[] h = @PKG@.AdminPage.hdr(ms[k]);
    String t = h == null ? "" : @PKG@.AdminPage.hs(h, 2);
    if (t == null || t.length() == 0) t = ms[k];
    b.set(e + ".Visible", true);
    b.set(e + ".Text", @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(t), 18));
    ev.addEventBinding(@BT@.Activating, e, evd("sm:" + k));
  }
  int more = ms.length - sn;
  b.set("#SkyyGtabSn.Text", !adm ? "" : (ms.length == 0 ? @PKG@.SettingsTabData.SETUPNONE : (more > 0 ? "+" + more + " more in Server Setup" : "")));
  b.set("#SkyyGtabSpage.Visible", adm);
}""")
M(sgt, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.pref = ref;
  this.pst = st;
  String lk = @PKG@.SettingsTabData.LK;
  for (int i = 0; i < lk.length(); i++) {
    char k = lk.charAt(i);
    String x = @PKG@.SettingsTabData.LP[i];
    String y = @PKG@.SettingsTabData.LB[i];
    if (k == 'A') b.appendInline(x.length() == 0 ? (String) null : x, y);
    else if (k == 'S') b.set(x, y);
    else if (k == 'E') ev.addEventBinding(@BT@.Activating, x, @EVD@.of("a", y));
  }
  this.seq = this.seq + 1L;
  this.tok = Long.toHexString(this.base + this.seq);
  this.builds = this.builds + 1;
  if (!this.drained) { this.drained = true; try { @PKG@.SetReg.drainIdx(); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings screen: the settings drain failed: " + t); } }
  java.util.UUID u = this.playerRef.getUuid();
  long c = -1L;
  try { c = @PKG@.MenuUtil.purse(u); } catch (Throwable t) { c = -1L; }
  b.set("#SkyyGtabCoins.Text", c < 0L ? "" : "Coins " + @PKG@.MenuUtil.fmt(c));
  try { fillSettings(b, ev); } catch (Throwable t) { this.rowKeys = new String[0]; @PKG@.MenuUtil.warn("settings screen: the settings list failed: " + t); }
  try { fillHud(b, ev); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings screen: the HUD card failed: " + t); }
  try { fillMods(b); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings screen: the mods card failed: " + t); }
  try { fillSetup(b, ev); } catch (Throwable t) { this.mods = new String[0]; @PKG@.MenuUtil.warn("settings screen: the server setup card failed: " + t); }
  b.set("#SkyyGtabCap.Text", this.tcap.length() > 0 ? this.tcap : @PKG@.SettingsTabData.CAP0);
}""")
# ---- the actions (each answers with ONE packet: a redraw, a caption, a page that replaces this one, or the close)
M(sgt, r"""
public void hub(String hub, String tab, String label) {
  this.answered = true;
  String r = null;
  try {
    if (tab != null && tab.length() > 0) r = @PKG@.HubBar.open(this.playerRef, this.playerRef.getUuid(), hub, tab);
    if (r == null || !@PKG@.MenuHub.opened(r)) r = @PKG@.MenuHub.run(this.playerRef, hub);
  } catch (Throwable t) { r = "failed"; @PKG@.MenuUtil.warn("settings screen: opening " + label + " failed: " + t); }
  if (!still()) { finish("hub " + hub); return; }
  say(@PKG@.MenuHub.opened(r) ? "Opening " + label : label + " is not on this server right now");
}""")
M(sgt, r"""
public void tabGo(int i) {
  this.answered = true;
  if (i == 0) {
    @PKG@.InvPage pg = null;
    try { pg = @PKG@.InvState.openAt(this.pref, this.pst, this.playerRef, "settings screen", "c", -1); } catch (Throwable t) { pg = null; @PKG@.MenuUtil.warn("settings screen: the inventory failed: " + t); }
    if (pg == null) { if (still()) say("The inventory could not open here"); return; }
    if (!still()) finish("inventory");
    return;
  }
  if (i == 1) {
    @PKG@.SkillPage sp = null;
    try { sp = @PKG@.SkillPage.open(this.pref, this.pst, this.playerRef, @PKG@.SkillPage.lastOf(this.playerRef.getUuid()), "settings screen"); } catch (Throwable t) { sp = null; @PKG@.MenuUtil.warn("settings screen: the skill page failed: " + t); }
    if (sp == null) { hub(@PKG@.InvData.TAB_HUB[1], @PKG@.InvData.TAB_TAB[1], @PKG@.InvData.TAB_NAME[1]); return; }
    if (!still()) finish("skills");
    return;
  }
  if (i == 2) {
    @PKG@.PetsTab pt = null;
    try { pt = @PKG@.PetsTab.open(this.pref, this.pst, this.playerRef, "settings screen"); } catch (Throwable t) { pt = null; @PKG@.MenuUtil.warn("settings screen: the pets screen failed: " + t); }
    if (pt == null) { hub(@PKG@.InvData.TAB_HUB[2], @PKG@.InvData.TAB_TAB[2], @PKG@.InvData.TAB_NAME[2]); return; }
    if (!still()) finish("pets");
    return;
  }
  if (i == 3) {
    @PKG@.MarketTab mt = null;
    try { mt = @PKG@.MarketTab.open(this.pref, this.pst, this.playerRef, "settings screen"); } catch (Throwable t) { mt = null; @PKG@.MenuUtil.warn("settings screen: the market screen failed: " + t); }
    if (mt == null) { hub(@PKG@.InvData.TAB_HUB[3], @PKG@.InvData.TAB_TAB[3], @PKG@.InvData.TAB_NAME[3]); return; }
    if (!still()) finish("market");
    return;
  }
  if (i == 4) {
    @PKG@.WorldTab wt = null;
    try { wt = @PKG@.WorldTab.open(this.pref, this.pst, this.playerRef, "settings screen"); } catch (Throwable t) { wt = null; @PKG@.MenuUtil.warn("settings screen: the world screen failed: " + t); }
    if (wt == null) { hub(@PKG@.InvData.TAB_HUB[4], @PKG@.InvData.TAB_TAB[4], @PKG@.InvData.TAB_NAME[4]); return; }
    if (!still()) finish("world");
    return;
  }
  if (i == 5) {
    @PKG@.SocialTab so = null;
    try { so = @PKG@.SocialTab.open(this.pref, this.pst, this.playerRef, "settings screen"); } catch (Throwable t) { so = null; @PKG@.MenuUtil.warn("settings screen: the social screen failed: " + t); }
    if (so == null) { hub(@PKG@.InvData.TAB_HUB[5], @PKG@.InvData.TAB_TAB[5], @PKG@.InvData.TAB_NAME[5]); return; }
    if (!still()) finish("social");
    return;
  }
  if (i == 6) { say("You are on Settings"); return; }
  say("No such tab");
}""")
# a command line as the player - the old pages' MenuPage.runCmd checks in its order: the command exists, the server's version has the
# subcommand (needOf), the player's permission; close = the page closes first (the HUD editor opens its own page)
M(sgt, r"""
public void runLine(String line, boolean close) {
  this.answered = true;
  String name = @PKG@.MenuUtil.firstWord(line);
  @ACM@ c = @PKG@.MenuUtil.cmd(name);
  if (c == null) { this.tcap = "/" + name + " is not on this server - that mod is not installed."; redraw(); return; }
  String need = @PKG@.MenuUtil.needOf(line);
  if (need != null) { this.tcap = "/" + line + " needs " + need + " - this server has an older version."; redraw(); return; }
  boolean ok = false;
  boolean checked = true;
  try { ok = c.hasPermission(this.playerRef); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("permission check for /" + name + " failed: " + t); ok = false; checked = false; }
  if (!checked) { this.tcap = "Could not check your permission for /" + name + ". Ask an admin."; redraw(); return; }
  if (!ok) {
    String node = null;
    try { node = c.getPermission(); } catch (Throwable t) { node = null; }
    this.tcap = "You do not have permission for /" + name + (node == null ? "" : " (" + @PKG@.MenuUtil.safe(node) + ")") + ". Ask an admin.";
    redraw();
    return;
  }
  ACTS = ACTS + 1;
  if (close) {
    shut();
    try { @CMGR@.get().handleCommand(this.playerRef, line); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings screen: /" + line + " failed: " + t); }
    return;
  }
  try { @CMGR@.get().handleCommand(this.playerRef, line); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("settings screen: /" + line + " failed: " + t); this.tcap = "/" + name + " could not be run."; redraw(); return; }
  this.tcap = "/" + line + "  - see your chat";
  redraw();
}""")
# ON / OFF on a row: the old page's write (SetReg.may first - a lost node = GONE; SetStore.set; the same captions)
M(sgt, r"""
public void toggle(int r, boolean val) {
  this.answered = true;
  if (r < 0 || this.rowKeys == null || r >= this.rowKeys.length || this.rowKeys[r] == null) { say("No setting there"); return; }
  String key = this.rowKeys[r];
  if (@PKG@.MenuData.HOTKEY_KEY.equals(key)) { say("Pick one of the three buttons on that row"); return; }
  java.util.UUID u = this.playerRef.getUuid();
  if (!@PKG@.SetReg.may(u, key)) { this.tcap = @PKG@.MenuData.SET_TXT_GONE; redraw(); return; }
  int ok = @PKG@.SetStore.set(u, key, val, false);
  Object[] d = @PKG@.SetReg.info(key);
  String label = d == null ? key : String.valueOf(d[2]);
  ACTS = ACTS + 1;
  this.tcap = ok == 1 ? label + (val ? ": ON - saved." : ": OFF - saved.") : @PKG@.MenuData.SET_TXT_BROKEN;
  redraw();
}""")
# the double-tap crouch row's three buttons (the old page's sch<r>n<c>: Nothing = menu.hotkey OFF; Fold / Open = ON + menu.crouchfold)
M(sgt, r"""
public void choice(int r, int c) {
  this.answered = true;
  if (r < 0 || c < 0 || c > 2 || this.rowKeys == null || r >= this.rowKeys.length || this.rowKeys[r] == null) { say("No setting there"); return; }
  String ck = this.rowKeys[r];
  if (!@PKG@.MenuData.HOTKEY_KEY.equals(ck)) { say("That row has ON and OFF"); return; }
  java.util.UUID u = this.playerRef.getUuid();
  if (!@PKG@.SetReg.may(u, ck)) { this.tcap = @PKG@.MenuData.SET_TXT_GONE; redraw(); return; }
  int ok = @PKG@.SetStore.set(u, ck, c != 2, false);
  if (ok == 1 && c != 2) ok = @PKG@.SetStore.set(u, @PKG@.MenuData.CFOLD_KEY, c == 0, false);
  ACTS = ACTS + 1;
  this.tcap = ok == 1 ? "Double-tap crouch: " + @PKG@.MenuData.STG_CH_LABELS[c] + " - saved." : @PKG@.MenuData.SET_TXT_BROKEN;
  redraw();
}""")
# Server Setup on one mod (the Mods list's modcfg path, MenuPage.openAdmin(mod)): the node re-checked, the mod still has its page
M(sgt, r"""
public void setupMod(int k) {
  this.answered = true;
  if (!@PKG@.MenuUtil.isAdmin(this.playerRef)) { this.tcap = @PKG@.SettingsTabData.NOACCESS; redraw(); return; }
  if (k < 0 || this.mods == null || k >= this.mods.length || this.mods[k] == null) { say("No mod there"); return; }
  String m = this.mods[k];
  if (@PKG@.AdminPage.hdr(m) == null) { this.tcap = @PKG@.MenuUtil.safe(m) + " has no Server Setup page right now."; redraw(); return; }
  @PLA@ p = null;
  try { p = (@PLA@) this.pst.getComponent(this.pref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null) { say("Server Setup could not open here"); return; }
  try { p.getPageManager().openCustomPage(this.pref, this.pst, new @PKG@.AdminPage(this.playerRef, "mod", m)); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("settings screen: Server Setup for " + m + " failed: " + t); if (still()) say("Server Setup could not open here"); return; }
  if (!still()) finish("server setup");
}""")
M(sgt, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {
  String a = @PKG@.InvPage.val(d, "a");
  if (a == null) a = "";
  this.answered = false;
  try {
    if (this.closed) { this.answered = true; return; }
    this.pref = ref;
    this.pst = st;
    String dq = @PKG@.InvPage.val(d, String.valueOf((char) 64) + "Q");
    if (dq != null) this.draft = clean(dq);
    long now = System.currentTimeMillis();
    boolean wasArmed = this.armedAt > 0L && now - this.armedAt <= 10000L;
    this.armedAt = 0L;                                  // every click but a second Reset disarms Reset all (the old page's rule)
    if (a.equals("close")) { this.answered = true; shut(); return; }
    if (a.startsWith("tab:")) { tabGo(@PKG@.InvPage.toInt(a.substring(4), -1)); return; }
    if (a.equals("full")) { hub("settings", "settings", "the Settings page"); return; }
    if (a.equals("mods")) {                             // fix: re-check the old Mods tab's rule (a stale click never falls back to the hub)
      if (!@PKG@.MenuHub.visible("mods", this.playerRef)) { this.tcap = @PKG@.SettingsTabData.MODSOFF; redraw(); return; }
      hub("settings", "mods", "the Mods page");
      return;
    }
    if (a.equals("setup")) {
      if (!@PKG@.MenuUtil.isAdmin(this.playerRef)) { this.tcap = @PKG@.SettingsTabData.NOACCESS; redraw(); return; }
      hub("settings", "setup", "Server Setup");
      return;
    }
    if (a.equals("find")) {
      String q = this.draft == null ? "" : this.draft;
      if (q.length() == 1) { this.tcap = @PKG@.MenuData.SET_TXT_SHORT; redraw(); return; }
      this.query = q;
      this.page = 0;
      this.tcap = q.length() == 0 ? "Type a word, then Find" : "";
      redraw();
      return;
    }
    if (a.equals("fclear")) { this.query = ""; this.draft = ""; this.page = 0; this.tcap = ""; redraw(); return; }
    if (a.startsWith("pg:")) {
      int dp = @PKG@.InvPage.toInt(a.substring(3), 0);
      int np = this.page + (dp < 0 ? -1 : 1);
      if (np < 0 || np >= this.pages) { say(np < 0 ? "This is the first page" : "This is the last page"); return; }
      this.page = np;
      this.tcap = "";
      redraw();
      return;
    }
    if (a.startsWith("cat:")) {
      int k = @PKG@.InvPage.toInt(a.substring(4), -1);
      if (k < 0 || k >= @PKG@.MenuData.SET_CAT_ID.length) { say("No such category"); return; }
      this.cat = k;
      this.query = "";
      this.draft = "";
      this.page = 0;
      this.tcap = "";
      redraw();
      return;
    }
    String t = @PKG@.InvPage.val(d, "t");
    if (t == null || !t.equals(this.tok)) {
      STALE = STALE + 1;
      this.tcap = "The page changed - here it is again. Nothing happened.";
      redraw();
      return;
    }
    if (a.startsWith("on:")) { toggle(@PKG@.InvPage.toInt(a.substring(3), -1), true); return; }
    if (a.startsWith("off:")) { toggle(@PKG@.InvPage.toInt(a.substring(4), -1), false); return; }
    if (a.startsWith("ch:")) {
      String[] f = a.substring(3).split(":");
      choice(f.length > 0 ? @PKG@.InvPage.toInt(f[0], -1) : -1, f.length > 1 ? @PKG@.InvPage.toInt(f[1], -1) : -1);
      return;
    }
    if (a.equals("reset")) {
      if (!wasArmed) { this.armedAt = now; this.tcap = @PKG@.MenuData.SET_TXT_ARM; redraw(); return; }
      ACTS = ACTS + 1;
      this.tcap = @PKG@.SetStore.resetAll(this.playerRef.getUuid()) == 1 ? @PKG@.MenuData.SET_TXT_RESET : @PKG@.MenuData.SET_TXT_BROKEN;
      redraw();
      return;
    }
    if (a.equals("hud")) { runLine("skyyhud", true); return; }
    if (a.startsWith("sm:")) { setupMod(@PKG@.InvPage.toInt(a.substring(3), -1)); return; }
    say("Pick a setting");
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("settings screen event '" + a + "' failed: " + t);
  } finally {
    if (!this.answered && !this.closed) {
      this.answered = true;
      this.answers = this.answers + 1;
      try { this.sendUpdate(); } catch (Throwable t2) { @PKG@.MenuUtil.warn("settings screen: the empty answer failed: " + t2); }
    }
  }
}""")
M(sgt, r"""
public void onDismiss(@REF@ ref, @ST@ st) { finish("dismissed"); }""")
'''
P.rep('''# the Tab key on the world thread (a press route() TOOK): our page open = it closes; else window 0 closed first (the CORE redirect step) and
''', SG_JAVA + '''# the Tab key on the world thread (a press route() TOOK): our page open = it closes; else window 0 closed first (the CORE redirect step) and
''')
# Tab while the settings screen is open = it closes
P.rep('''  if (sp0 instanceof @PKG@.SocialTab && !((@PKG@.SocialTab) sp0).closed) { ((@PKG@.SocialTab) sp0).shut(); return; }   // 0.3.63
''', '''  if (sp0 instanceof @PKG@.SocialTab && !((@PKG@.SocialTab) sp0).closed) { ((@PKG@.SocialTab) sp0).shut(); return; }   // 0.3.63
  if (sp0 instanceof @PKG@.SettingsTab && !((@PKG@.SettingsTab) sp0).closed) { ((@PKG@.SettingsTab) sp0).shut(); return; }   // 0.3.64
''')
# ---------- the inventory: the Settings tab opens the settings screen
P.rep('''M(ipg, r"""
public void goTab(int i) {''', '''# 0.3.64: the Settings tab = the settings screen (false = it could not open: today's Settings route below)
M(ipg, r"""
public boolean openSetTab() {
  @PKG@.SettingsTab sg = null;
  try { sg = @PKG@.SettingsTab.open(this.pref, this.pst, this.playerRef, "inventory"); } catch (Throwable t) { sg = null; @PKG@.MenuUtil.warn("inventory: the settings screen failed: " + t); }
  if (sg == null) return false;
  this.answered = true;
  if (!still()) finish("settings");
  return true;
}""")
M(ipg, r"""
public void goTab(int i) {''')
P.rep('''  if (i == 5 && openSocial()) return;   // 0.3.63: the social screen (else today's Social route below)
''', '''  if (i == 5 && openSocial()) return;   // 0.3.63: the social screen (else today's Social route below)
  if (i == 6 && openSetTab()) return;   // 0.3.64: the settings screen (else today's Settings route below)
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.64: no new system / command"
_i = P.s.index
assert _i("public SettingsTab(@PR@ pr, String via)") < _i("public static @PKG@.SettingsTab open(") < _i("public static @PKG@.SocialTab open(")
assert _i("public static @PKG@.SettingsTab open(") < _i("public boolean settingsTab()") < _i('try { sg = @PKG@.SettingsTab.open(this.pref, this.pst, this.playerRef, "pets screen")')
assert _i('try { sg = @PKG@.SettingsTab.open(this.pref, this.pst, this.playerRef, "social screen")') > _i("public static @PKG@.SettingsTab open(")
assert _i("public void shut() { finish(\"closed\"); this.close(); }\"\"\")\nM(sgt") < _i("if (sp0 instanceof @PKG@.SettingsTab")
assert _i("public boolean openSetTab()") < _i("public void goTab(int i)") and _i('F(sgd, "public static final String LK') < _i("public static @PKG@.SettingsTab open(")
assert _i("public static @PKG@.SocialTab open(") < _i('try { so = @PKG@.SocialTab.open(this.pref, this.pst, this.playerRef, "settings screen")')
assert _i("public void act(int i)") < _i("public void fillSettings(@UCB@ b, @UEB@ ev)"), "0.3.64: the settings screen's methods come after SocialTab's"
assert _i("public static boolean words(String hay, String q)") < _i("public void fillSettings(@UCB@ b, @UEB@ ev)")
assert _i("public static String[] cfgMods()") < _i("public void fillSetup(@UCB@ b, @UEB@ ev)")
P.finish()


# ======================================================================= the HARNESS (derived from the 0.3.63 harness: every 0.3.63 check
# runs again on the 0.3.64 jar - the Settings tab of every screen now opens the settings screen -, plus TAB6)
def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


T.rep('''"""Harness for SkyyMenu 0.3.63 (the Social tab = one screen; tools/menu_0_3_63_patch.py, round tab5).
GENERATED by tools/menu_0_3_63_patch.py from the 0.3.62 harness (edit the patch, not this file): every 0.3.62 check runs again on the
0.3.63 jar''', '''"""Harness for SkyyMenu 0.3.64 (the Settings tab = one screen; tools/menu_0_3_64_patch.py, round tab6).
GENERATED by tools/menu_0_3_64_patch.py from the 0.3.63 harness (edit the patch, not this file): every 0.3.63 check runs again on the
0.3.64 jar (each screen's Settings tab now opens the settings screen - still ONE packet), plus
  TAB6 (EXECUTED on the real SetReg / SetStore with harness switches registered (one behind a permission node), a harness config:def mod
       for Server Setup, an admin player (hytale:Admin) and a plain one, and the harness' own command manager (/skyyhud)):
       OPEN    the inventory's / skill page's / pets / market / world / social screen's Settings tab = the SETTINGS SCREEN (ONE packet)
       FALL    no /skyyhud = the HUD card says so (no button); a plain player = Server Setup LOCKED (no buttons, a forged click = said);
               the Mods card follows the old Mods tab's rule
       PAGE    the category rail = the categories with a row you may change (the gated row hidden from a plain player, shown to an admin);
               9 rows a page + pager; ON / OFF selected = your value; the crouch row's three choices; search (2 letters, every word,
               the tab + mod prefix), Clear
       ACT     ON / OFF = SetStore.set + the old captions; a row you lost = SET_TXT_GONE, nothing written; the crouch choices (Nothing =
               hotkey OFF, Fold / Open = ON + crouchfold); Reset all twice = resetAll; Open HUD editor = /skyyhud (closed first); a mod's
               Server Setup button = AdminPage on that mod; Open Server Setup / Full page / Mods page = the old pages (ONE packet)
       SAFE    a stale page token / a double click = nothing written twice
       TABS    every tab from the screen; the Tab key and X close it
The 0.3.63 harness text follows:
Harness for SkyyMenu 0.3.63 (the Social tab = one screen; tools/menu_0_3_63_patch.py, round tab5).
GENERATED by tools/menu_0_3_63_patch.py from the 0.3.62 harness (edit the patch, not this file): every 0.3.62 check runs again on the
0.3.63 jar''')
T.rep('VERSION = "0.3.63"\nJAR', 'VERSION = "0.3.64"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.62.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.63.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.62.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.63.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_63_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_64_patch.py")')
T.rep('"scratch", "tab5", "menu"', '"scratch", "tab6", "menu"')
T.rep('ADDED = ["SocialTabData", "SocialTab"]   # 0.3.63: the social screen\n', 'ADDED = ["SettingsTabData", "SettingsTab"]   # 0.3.64: the settings screen\n')
T.rep(cut(T.s, 'EXPECT = {   # 0.3.63:', 'if "--expect-dump" in sys.argv:'), '''EXPECT = {   # 0.3.64: the Settings tab opens the settings screen (inventory + skill page + pets / market / world / social screen); Tab closes it
    "InvPage": ["+m openSetTab", "~m goTab"],
    "InvState": ["~m tab"],
    "SkillPage": ["+m settingsTab", "~m tabGo"],
    "PetsTab": ["~m tabGo"],
    "MarketTab": ["~m tabGo"],
    "WorldTab": ["~m tabGo"],
    "SocialTab": ["~m tabGo"],
    "SkyyMenuPlugin": ["~m setup"],                      # the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],   # the version string + the Mods list
}
''')
T.rep('''    K.check(g.count('VERSION = "0.3.63"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.64"') == 1, "S VERSION")
    # 0.3.64: the settings screen fits one 1080p screen, never scrolls, element budget, no new picture
    K.check("0.3.64: the settings screen fits one 1080p screen" in g and "0.3.64: the settings screen never scrolls" in g
            and "0.3.64: the settings screen names only Skyglass pictures the market screen already ships" in g,
            "TAB6 STATIC the build asserts the settings screen fits 1080 (both columns sum to the body), has no scrolling list and no new picture")
    mw6_ = re.search(r"SG_ELEMENTS <= (\\d+)", g)
    K.check(mw6_ is not None and int(mw6_.group(1)) <= 800, "TAB6 STATIC the settings screen's element budget assert is <= 800 (the ~1,600 client budget)")''')
T.rep('''("WorldTabData", "SkyyWtab"), ("SocialTabData", "SkyyStab")):''',
      '''("WorldTabData", "SkyyWtab"), ("SocialTabData", "SkyyStab"), ("SettingsTabData", "SkyyGtab")):''')
# every screen's Settings tab is now the settings screen (still ONE packet - the old checks stay, their words say so)
for _old, _new in (
        ('''    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SettingsPage" and bool(SP.closed), "TAB1 ACT Settings = our Settings page")''',
         '''    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SettingsTab" and bool(SP.closed), "TAB1 ACT Settings = (0.3.64) the settings screen")'''),
        ('''    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SettingsPage" and bool(PS.closed), "TAB2 TABS Settings = our Settings page")''',
         '''    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SettingsTab" and bool(PS.closed), "TAB2 TABS Settings = (0.3.64) the settings screen")'''),
        ('''    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SettingsPage" and bool(MS.closed), "TAB3 TABS Settings = our Settings page")''',
         '''    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SettingsTab" and bool(MS.closed), "TAB3 TABS Settings = (0.3.64) the settings screen")'''),
        ('''    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SettingsPage" and bool(WS.closed), "TAB4 TABS Settings = our Settings page")''',
         '''    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SettingsTab" and bool(WS.closed), "TAB4 TABS Settings = (0.3.64) the settings screen")'''),
        ('''    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SettingsPage" and bool(SS.closed), "TAB5 TABS Settings = our Settings page")''',
         '''    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SettingsTab" and bool(SS.closed), "TAB5 TABS Settings = (0.3.64) the settings screen")'''),
        ('''    K.check(cur is not None and str(cur.getClass().getSimpleName()) == "SettingsPage" and bool(pg.closed) and ST.PAGES.get(PI.pr.getUuid()) is None
            and not [x_ for x_ in pages(PI, f0) if "#SkyyInvCap.Text" in cmap(x_)], "TABS Settings: our own Settings page opens (bridge), ours forgotten, no stray caption (%s)"''',
         '''    K.check(cur is not None and str(cur.getClass().getSimpleName()) == "SettingsTab" and bool(pg.closed) and ST.PAGES.get(PI.pr.getUuid()) is None
            and not [x_ for x_ in pages(PI, f0) if "#SkyyInvCap.Text" in cmap(x_)], "TABS Settings: (0.3.64) the settings screen opens, ours forgotten, no stray caption (%s)"''')):
    T.rep(_old, _new)

HARNESS_TAB6 = r'''    # ---- TAB6 (0.3.64; popup 11-14 "Yes, both" on the 7 tabs; Skyy 11-21 "build and deploy everything on your list"): THE SETTINGS SCREEN
    SGB, SGD, SRG, SST = JV("SettingsTab"), JV("SettingsTabData"), JV("SetReg"), JV("SetStore")
    MDc6 = JV("MenuData")
    uk6 = PK.pr.getUuid()
    OBJ6 = JClass("java.lang.Object")
    if PK.pm.getCustomPage() is not None:
        PK.pm.handleLegacyCustomPageEvent(PK.ref, PK.st, E.CPE(E.CPT.Dismiss, None))
    E.pump(PK)
    HUD6 = E.CM.cmds.remove("skyyhud")

    def g_ev(obj, what, n=1, page=None, P_=None):
        P_ = P_ or PK
        pg_ = page if page is not None else P_.pm.getCustomPage()
        f_ = len(E.sent(P_))
        pg_.handleDataEvent(P_.ref, P_.st, json.dumps(obj))
        ps_ = pages(P_, f_)
        if n is not None:
            K.eq(len(ps_), n, what + ": exactly %d page packet" % n)
        return ps_[0] if ps_ else None

    def g_open(what, P_=None):
        P_ = P_ or PK
        if P_.pm.getCustomPage() is not None:
            P_.pm.handleLegacyCustomPageEvent(P_.ref, P_.st, E.CPE(E.CPT.Dismiss, None))
        E.pump(P_)
        f_ = len(E.sent(P_))
        gg_ = SGB.open(P_.ref, P_.st, P_.pr, "test")
        E.pump(P_)
        ps_ = pages(P_, f_)
        K.check(gg_ is not None and len(ps_) == 1, what + ": SettingsTab.open = ONE page packet")
        return gg_, (ps_[0] if ps_ else None)
    vis6 = lambda c_, k_: sval(c_, "#SkyyGtab%s.Visible" % k_) in (True, "true")
    txt6 = lambda c_, k_: str(sval(c_, "#SkyyGtab%s.Text" % k_))
    cap6 = lambda p_: str(sval(cmap(p_), "#SkyyGtabCap.Text"))
    cats6 = lambda p_: [int(m_) for m_ in re.findall(r"#SkyyGtabKt(\d+) ", " ".join(str(c_.text or "") for c_ in cmds_of(p_)))]
    names6 = lambda c_: [txt6(c_, "R%dN" % k_) for k_ in range(int(SGD.RN)) if vis6(c_, "R%d" % k_)]
    sel6 = lambda p_, id_: str(SGD.ST_SEL) in mk_of(p_, "SkyyGtab" + id_)
    tab6 = lambda p_, id_: str(SGD.ST_TAB) in mk_of(p_, "SkyyGtab" + id_)
    sel14 = lambda p_, id_: str(SGD.ST_SEL14) in mk_of(p_, "SkyyGtab" + id_)
    bv = lambda v_: None if v_ is None else bool(v_)
    vcats = lambda u_: [i_ for i_ in range(len(MDc6.SET_CAT_ID)) if len(SRG.visible(i_, u_)) > 0]
    # OPEN from the inventory: only SkyyMenu's own switches, no /skyyhud, a plain player
    pgI_ = ST.openPage(PK.ref, PK.st, PK.pr, "test")
    E.pump(PK)
    f0_ = len(E.sent(PK))
    pgI_.handleDataEvent(PK.ref, PK.st, '{"a":"tab:6"}')
    pk_ = pages(PK, f0_)
    GS = PK.pm.getCustomPage()
    K.check(len(pk_) == 1 and GS is not None and str(GS.getClass().getSimpleName()) == "SettingsTab" and bool(pgI_.closed) and ST.PAGES.get(PK.pr.getUuid()) is None,
            "TAB6 OPEN the inventory's Settings tab = the SETTINGS SCREEN (ONE page packet), the inventory page forgotten")
    cm = cmap(pk_[0]) if pk_ else {}
    K.notes.append("TAB6 the screen's first packet: %d commands, %d bindings, categories %s" % (len(cmds_of(pk_[0])) if pk_ else 0, len(binds_of(pk_[0])) if pk_ else 0, cats6(pk_[0]) if pk_ else None))
    own0_ = vcats(uk6)
    K.check(pk_ and cats6(pk_[0]) == own0_ and len(own0_) >= 1 and sel14(pk_[0], "Kt%d" % own0_[0]) and int(GS.cat) == own0_[0],
            "TAB6 PAGE the rail = the categories with a row this player may change, the first selected (%s)" % own0_)
    K.check(not vis6(cm, "Hud") and txt6(cm, "H2") == str(SGD.HUDOFF), "TAB6 FALL no /skyyhud = the HUD card says so, no button")
    K.check(txt6(cm, "Sb") == "LOCKED" and not vis6(cm, "Spage") and not vis6(cm, "S0") and txt6(cm, "Sl") == str(SGD.SETUP0),
            "TAB6 FALL a plain player = Server Setup LOCKED, no buttons")
    mv_ = bool(MH.visible("mods", PK.pr))
    K.check(vis6(cm, "Mpage") == mv_ and txt6(cm, "Mn") == str(SGD.MODSON if mv_ else SGD.MODSOFF), "TAB6 PAGE the Mods card follows the old Mods tab's rule (visible %s)" % mv_)
    K.check(txt6(cm, "Cap") == str(SGD.CAP0) and txt6(cm, "St") == str(MDc6.SET_TXT_HINT) and txt6(cm, "Reset") == "Reset all",
            "TAB6 PAGE the caption, the hint, Reset all")
    # harness switches: 11 in Cooking (2 pages), one more there behind a permission node only admins hold
    cook_ = list(MDc6.SET_CAT_ID).index("cooking")
    for i_ in range(1, 12):
        SRG.register(_JA(OBJ6)(["SkyyHarness", "harness.k%02d" % i_, "Harness %02d" % i_, "cooking", TRUE, "help line %02d" % i_]))
    SRG.register(_JA(OBJ6)(["SkyyHarness", "harness.secret", "Secret switch", "cooking", TRUE, "admins only", "skyyharness.secret"]))
    p_ = g_ev({"a": "cat:%d" % cook_, "t": str(GS.tok)}, "TAB6 ACT the Cooking category")
    cm = cmap(p_)
    K.check(names6(cm) == ["Harness %02d" % i_ for i_ in range(1, 10)] and txt6(cm, "Pg") == "Page 1 / 2" and sel14(p_, "Kt%d" % cook_)
            and "11 settings" in txt6(cm, "Lh") and "Secret switch" not in str(cm) and txt6(cm, "R0D") == "help line 01"
            and txt6(cm, "Al") == str(MDc6.SET_ALWAYS[cook_])[:125],
            "TAB6 PAGE Cooking: 9 rows a page, page 1 / 2, 11 settings (the gated row hidden from a plain player), help + the always line (%s)" % names6(cm))
    K.check(sel6(p_, "R0on") and tab6(p_, "R0of") and len([b_ for b_ in binds_of(p_) if '"on:' in b_[2] or '"off:' in b_[2]]) == 18
            and all(str(GS.tok) in b_[2] for b_ in binds_of(p_) if '"on:' in b_[2]),
            "TAB6 PAGE ON selected on a default-ON row, ON / OFF bound on each of the 9 rows with the page token")
    p_ = g_ev({"a": "pg:1"}, "TAB6 ACT next page")
    K.check(names6(cmap(p_)) == ["Harness 10", "Harness 11"] and txt6(cmap(p_), "Pg") == "Page 2 / 2", "TAB6 PAGE page 2 = the last two rows")
    p_ = g_ev({"a": "pg:1"}, "TAB6 ACT past the last page")
    K.check("last page" in cap6(p_), "TAB6 PAGE > on the last page = a caption")
    p_ = g_ev({"a": "pg:-1"}, "TAB6 ACT back to page 1")
    # ACT: OFF on row 0
    old_ = str(GS.tok)
    a0_ = int(SGB.ACTS)
    p_ = g_ev({"a": "off:0", "t": old_}, "TAB6 ACT OFF")
    K.check(bv(SST.get(uk6, "harness.k01")) is False and cap6(p_) == "Harness 01: OFF - saved." and sel6(p_, "R0of") and tab6(p_, "R0on")
            and int(SGB.ACTS) == a0_ + 1, "TAB6 ACT OFF = SetStore.set (the old page's write + caption), OFF now selected (%s)" % cap6(p_))
    p_ = g_ev({"a": "on:0", "t": old_}, "TAB6 SAFE double click")
    K.check(bv(SST.get(uk6, "harness.k01")) is False and "The page changed" in cap6(p_) and int(SGB.STALE) >= 1 and int(SGB.ACTS) == a0_ + 1,
            "TAB6 SAFE a click from an older drawing = said, nothing written")
    p_ = g_ev({"a": "off:1", "t": "forged"}, "TAB6 SAFE forged token")
    K.check(bv(SST.get(uk6, "harness.k02")) is True and "The page changed" in cap6(p_), "TAB6 SAFE a forged token = nothing written")
    p_ = g_ev({"a": "on:0", "t": str(GS.tok)}, "TAB6 ACT ON")
    K.check(bv(SST.get(uk6, "harness.k01")) is True and cap6(p_) == "Harness 01: ON - saved.", "TAB6 ACT ON = written back ON")
    p_ = g_ev({"a": "off:1", "t": str(GS.tok)}, "TAB6 ACT OFF row 2")
    K.check(bv(SST.get(uk6, "harness.k02")) is False, "TAB6 ACT OFF on Harness 02")
    # a row the player lost between the draw and the click (refused for this run = may() false)
    tk_ = str(GS.tok)
    SRG.refuse("harness.k03", TRUE, "harness: lost")
    p_ = g_ev({"a": "off:2", "t": tk_}, "TAB6 SAFE a lost row")
    K.check(cap6(p_) == str(MDc6.SET_TXT_GONE) and SST.own(uk6, "harness.k03") is None and "Harness 03" not in names6(cmap(p_)),
            "TAB6 SAFE a row the player can no longer change = SET_TXT_GONE, nothing written, the row gone on the redraw")
    p_ = g_ev({"a": "on:20", "t": str(GS.tok)}, "TAB6 SAFE a row past the list")
    K.check("No setting there" in cap6(p_), "TAB6 SAFE ON on an empty row = a caption (%s)" % cap6(p_))
    # SEARCH: one letter, a word, every word, Clear
    p_ = g_ev({"a": "find", "t": str(GS.tok), "@Q": "h"}, "TAB6 ACT search one letter")
    K.check(cap6(p_) == str(MDc6.SET_TXT_SHORT) and str(GS.query) == "", "TAB6 ACT a one-letter search = the old page's 'at least 2 letters'")
    p_ = g_ev({"a": "find", "t": str(GS.tok), "@Q": "harness 05"}, "TAB6 ACT search")
    cm = cmap(p_)
    K.check(names6(cm) == ["Harness 05"] and txt6(cm, "R0D").startswith("Cooking (SkyyHarness): help line 05") and "Search: harness 05" in txt6(cm, "Lh")
            and txt6(cm, "Al") == str(MDc6.SET_TXT_FIND)[:125] and not [c_ for c_ in cats6(p_) if sel14(p_, "Kt%d" % c_)]
            and sval(cm, "#SkyyGtabQ.Value") == "harness 05",
            "TAB6 ACT search = every word in key / tab / label / help, the tab + mod prefix, no category selected, the box keeps the text (%s)" % names6(cm))
    p_ = g_ev({"a": "off:0", "t": str(GS.tok)}, "TAB6 ACT OFF in the search")
    K.check(bv(SST.get(uk6, "harness.k05")) is False and names6(cmap(p_)) == ["Harness 05"], "TAB6 ACT OFF on a search result writes that key, the search stays")
    p_ = g_ev({"a": "find", "t": str(GS.tok), "@Q": "nothing like this"}, "TAB6 ACT search with no match")
    K.check(names6(cmap(p_)) == ["Nothing matches"] and not vis6(cmap(p_), "R1") and mk_of(p_, "SkyyGtabR0on") == "", "TAB6 ACT no match = said, no buttons")
    p_ = g_ev({"a": "fclear"}, "TAB6 ACT Clear")
    K.check(str(GS.query) == "" and names6(cmap(p_))[:1] == ["Harness 01"] and txt6(cmap(p_), "Pg") == "Page 1 / 2" and "10 settings" in txt6(cmap(p_), "Lh"),
            "TAB6 ACT Clear = back to the category (Cooking, 10 rows after the lost one)")
    # the double-tap crouch row's three choices
    gen_ = list(MDc6.SET_CAT_ID).index(str(SRG.info(MDc6.HOTKEY_KEY)[3])) if SRG.info(MDc6.HOTKEY_KEY) is not None else -1
    K.check(gen_ >= 0 and SRG.may(uk6, MDc6.HOTKEY_KEY), "TAB6 PAGE the double-tap crouch switch is one of SkyyMenu's own rows")
    p_ = g_ev({"a": "cat:%d" % gen_, "t": str(GS.tok)}, "TAB6 ACT the crouch row's category")
    rk_ = [str(x_) if x_ is not None else None for x_ in GS.rowKeys]
    while str(MDc6.HOTKEY_KEY) not in rk_ and int(GS.page) + 1 < int(GS.pages):
        p_ = g_ev({"a": "pg:1"}, "TAB6 ACT find the crouch row")
        rk_ = [str(x_) if x_ is not None else None for x_ in GS.rowKeys]
    r_ = rk_.index(str(MDc6.HOTKEY_KEY)) if str(MDc6.HOTKEY_KEY) in rk_ else -1
    K.check(r_ >= 0 and [mk_of(p_, "SkyyGtabR%dc%d" % (r_, c_)) != "" for c_ in range(3)] == [True, True, True] and mk_of(p_, "SkyyGtabR%don" % r_) == ""
            and sel6(p_, "R%dc%d" % (r_, int(JV("SoundSw").crouchChoice(uk6)))),
            "TAB6 PAGE the crouch row = Fold quests / Open menu / Nothing (the current one selected), no ON / OFF")
    p_ = g_ev({"a": "ch:%d:2" % r_, "t": str(GS.tok)}, "TAB6 ACT crouch Nothing")
    K.check(bv(SST.get(uk6, MDc6.HOTKEY_KEY)) is False and int(JV("SoundSw").crouchChoice(uk6)) == 2 and cap6(p_) == "Double-tap crouch: Nothing - saved."
            and sel6(p_, "R%dc2" % r_), "TAB6 ACT Nothing = menu.hotkey OFF (the old page's write)")
    p_ = g_ev({"a": "ch:%d:1" % r_, "t": str(GS.tok)}, "TAB6 ACT crouch Open menu")
    K.check(bv(SST.get(uk6, MDc6.HOTKEY_KEY)) is True and bv(SST.own(uk6, MDc6.CFOLD_KEY)) is False and int(JV("SoundSw").crouchChoice(uk6)) == 1,
            "TAB6 ACT Open menu = menu.hotkey ON + menu.crouchfold OFF")
    p_ = g_ev({"a": "ch:%d:0" % r_, "t": str(GS.tok)}, "TAB6 ACT crouch Fold")
    K.check(int(JV("SoundSw").crouchChoice(uk6)) == 0 and bv(SST.own(uk6, MDc6.CFOLD_KEY)) is True, "TAB6 ACT Fold quests = menu.crouchfold ON")
    p_ = g_ev({"a": "on:%d" % r_, "t": str(GS.tok)}, "TAB6 SAFE ON on the crouch row")
    K.check("three buttons" in cap6(p_), "TAB6 SAFE a forged ON on the crouch row = a caption, nothing written")
    # RESET ALL: click, then again (10 s); another click between disarms
    p_ = g_ev({"a": "reset", "t": str(GS.tok)}, "TAB6 ACT Reset all (arm)")
    K.check(cap6(p_) == str(MDc6.SET_TXT_ARM) and txt6(cmap(p_), "Reset") == "Click again" and bv(SST.get(uk6, "harness.k02")) is False,
            "TAB6 ACT Reset all once = armed (the old page's words), nothing reset")
    p_ = g_ev({"a": "pg:1"}, "TAB6 ACT a click between")
    p_ = g_ev({"a": "reset", "t": str(GS.tok)}, "TAB6 ACT Reset all after another click")
    K.check(cap6(p_) == str(MDc6.SET_TXT_ARM) and bv(SST.get(uk6, "harness.k02")) is False, "TAB6 SAFE another click disarms - Reset arms again, nothing reset")
    p_ = g_ev({"a": "reset", "t": str(GS.tok)}, "TAB6 ACT Reset all (confirm)")
    K.check(cap6(p_) == str(MDc6.SET_TXT_RESET) and bv(SST.get(uk6, "harness.k02")) is True and bv(SST.get(uk6, "harness.k05")) is True
            and SST.own(uk6, MDc6.HOTKEY_KEY) is None and SST.own(uk6, MDc6.CFOLD_KEY) is None,
            "TAB6 ACT Reset all twice = SetStore.resetAll (every switch back to its default, the crouch choice too)")
    # SERVER SETUP for a plain player: forged clicks
    p_ = g_ev({"a": "setup"}, "TAB6 SAFE Open Server Setup, plain player")
    K.check(cap6(p_) == str(SGD.NOACCESS) and str(PK.pm.getCustomPage().getClass().getSimpleName()) == "SettingsTab", "TAB6 SAFE a plain player's Open Server Setup = said, no page")
    p_ = g_ev({"a": "sm:0", "t": str(GS.tok)}, "TAB6 SAFE a mod button, plain player")
    K.check(cap6(p_) == str(SGD.NOACCESS), "TAB6 SAFE a plain player's mod button = said, no page")
    # HUD: /skyyhud as the player, the page closed first
    E.CM.cmds.put("skyyhud", Ucls.allocateInstance(JClass("skyymenu19.Cmd").class_))
    p_ = g_ev({"a": "cat:%d" % cook_}, "TAB6 a redraw with /skyyhud")
    K.check(vis6(cmap(p_), "Hud") and txt6(cmap(p_), "H2") == str(SGD.HUDON) and len([b_ for b_ in binds_of(p_) if '"hud"' in b_[2]]) == 1,
            "TAB6 PAGE with SkyyHud = Open HUD editor shown + bound")
    l0_ = int(E.CM.lines.size())
    old_ = str(GS.tok)
    g_ev({"a": "hud", "t": old_}, "TAB6 ACT Open HUD editor", n=None)
    lines6 = [str(E.CM.lines.get(i_)) for i_ in range(l0_, int(E.CM.lines.size()))]
    K.check(bool(GS.closed) and lines6 == ["skyyhud"], "TAB6 ACT Open HUD editor = the page closed + /skyyhud as the player (%s)" % lines6)
    g_ev({"a": "hud", "t": old_}, "TAB6 SAFE double click on the HUD editor", n=0, page=GS)
    K.check(int(E.CM.lines.size()) == l0_ + 1, "TAB6 SAFE a double click on Open HUD editor = ONE command")
    # links to the old pages (each ONE packet)
    for a_, what, want_ in (("full", "Full page", "SettingsPage"), ("mods", "Mods page", None)):
        GS, p_ = g_open("TAB6 reopen for " + what)
        f0_ = len(E.sent(PK))
        GS.handleDataEvent(PK.ref, PK.st, json.dumps({"a": a_}))
        cur_ = PK.pm.getCustomPage()
        K.check(len(pages(PK, f0_)) == 1 and (want_ is None or (cur_ is not None and str(cur_.getClass().getSimpleName()) == want_)),
                "TAB6 LINK %s = the old page's route, ONE packet (%s)" % (what, None if cur_ is None else cur_.getClass().getSimpleName()))
    # ADMIN: the gated row shows, Server Setup unlocked with a button per mod
    PO6 = E.player(uid=E.OP, name="SkyyOp")
    byU.put(PO6.pr.getUuid(), PO6.pr)
    BR.put("config:def:SkyyHarness", _JA(OBJ6)(["x", "", "Harness Mod", "1.0", "", _JA(JS)([]), _JA(JS)([]), _JA(OBJ6)([]), "", ""]))
    JV("MenuIdx").scan()
    cfg6 = [str(x_) for x_ in JV("AdminPage").cfgMods()]
    K.check(bool(JV("MenuUtil").isAdmin(PO6.pr)) and not bool(JV("MenuUtil").isAdmin(PK.pr)) and "SkyyHarness" in cfg6,
            "TAB6 the harness: the op is an admin, the plain player is not; the harness mod has a Server Setup header (%s)" % cfg6)
    GO, p_ = g_open("TAB6 open as the admin", P_=PO6)
    cm = cmap(p_)
    hk_ = cfg6.index("SkyyHarness") if "SkyyHarness" in cfg6 else -1
    K.check(txt6(cm, "Sb") == "ADMIN" and vis6(cm, "Spage") and txt6(cm, "Sl") == str(SGD.SETUP1) and hk_ >= 0 and hk_ < int(SGD.SN)
            and vis6(cm, "S%d" % hk_) and txt6(cm, "S%d" % hk_) == "Harness Mod" and len([b_ for b_ in binds_of(p_) if '"sm:' in b_[2]]) == min(len(cfg6), int(SGD.SN)),
            "TAB6 PAGE admin: Server Setup ADMIN, a button per mod with its Server Setup title, Open Server Setup (%s)" % cfg6)
    p_ = g_ev({"a": "cat:%d" % cook_, "t": str(GO.tok)}, "TAB6 admin Cooking", P_=PO6)
    K.check("11 settings" in txt6(cmap(p_), "Lh") and "secret" in [str(x_) for x_ in SRG.visible(cook_, PO6.pr.getUuid())][-1],
            "TAB6 PAGE admin: the row behind skyyharness.secret is shown to its holder (11 in Cooking, the plain player has 10)")
    f0_ = len(E.sent(PO6))
    GO.handleDataEvent(PO6.ref, PO6.st, json.dumps({"a": "sm:%d" % hk_, "t": str(GO.tok)}))
    cur_ = PO6.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "AdminPage" and str(cur_.view) == "mod" and str(cur_.mod) == "SkyyHarness"
            and bool(GO.closed) and len(pages(PO6, f0_)) == 1,
            "TAB6 ACT admin: a mod's button = Server Setup on that mod (AdminPage view mod), ONE packet (%s)" % (None if cur_ is None else cur_.getClass().getSimpleName()))
    GO, p_ = g_open("TAB6 reopen as the admin", P_=PO6)
    f0_ = len(E.sent(PO6))
    GO.handleDataEvent(PO6.ref, PO6.st, '{"a":"setup"}')
    cur_ = PO6.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "AdminPage" and len(pages(PO6, f0_)) == 1,
            "TAB6 ACT admin: Open Server Setup = the old hub tab (AdminPage list), ONE packet")
    GO, p_ = g_open("TAB6 reopen as the admin for a gone mod", P_=PO6)
    BR.remove("config:def:SkyyHarness")
    p_ = g_ev({"a": "sm:%d" % hk_, "t": str(GO.tok)}, "TAB6 SAFE a mod whose Server Setup went away", P_=PO6)
    K.check("has no Server Setup page right now" in cap6(p_) and not bool(GO.closed), "TAB6 SAFE a mod's button after its header went away = said, no page")
    if PO6.pm.getCustomPage() is not None:
        PO6.pm.handleLegacyCustomPageEvent(PO6.ref, PO6.st, E.CPE(E.CPT.Dismiss, None))
    byU.remove(PO6.pr.getUuid())
    JV("MenuIdx").scan()
    # FIX (tab6 fixer): the help line uses the row's full width (name | buttons on top), help never cut at 70 characters
    wd_ = lambda id_: [int(m_) for m_ in re.findall(r"#%s \{ *Anchor: *\(Width: *(\d+)" % id_, " ".join(str(x_) for x_ in SGD.LB))]
    K.check(wd_("SkyyGtabR0D")[:1] and wd_("SkyyGtabR0N")[:1] and wd_("SkyyGtabR0D")[0] > wd_("SkyyGtabR0N")[0] + 300 and int(SGD.DCLIP) >= 100,
            "TAB6 FIX the help line spans the row (help %s px, name %s px, cap %d chars)" % (wd_("SkyyGtabR0D"), wd_("SkyyGtabR0N"), int(SGD.DCLIP)))
    GS, p_ = g_open("TAB6 reopen for long help")
    h100_ = ("Long help start " + "abcd " * 30)[:96] + " END"
    h200_ = ("Huge help start " + "efgh " * 60)[:200]
    SRG.register(_JA(OBJ6)(["SkyyHarness", "harness.long", "Long help", "cooking", TRUE, h100_]))
    SRG.register(_JA(OBJ6)(["SkyyHarness", "harness.huge", "Huge help", "cooking", TRUE, h200_]))
    p_ = g_ev({"a": "find", "t": str(GS.tok), "@Q": "long help"}, "TAB6 FIX search a 100-character help")
    K.check(names6(cmap(p_)) == ["Long help"] and txt6(cmap(p_), "R0D") == "Cooking (SkyyHarness): " + h100_,
            "TAB6 FIX a 100-character help shows WHOLE in search, after its Tab (Mod) prefix (%s)" % txt6(cmap(p_), "R0D")[-30:])
    p_ = g_ev({"a": "find", "t": str(GS.tok), "@Q": "huge help"}, "TAB6 FIX search a 200-character help")
    d_ = txt6(cmap(p_), "R0D")
    K.check(d_ == "Cooking (SkyyHarness): " + h200_[:100].strip(),
            "TAB6 FIX a 200-character help (the registry keeps 100) shows all 100 after its prefix, nothing more cut (%d chars)" % len(d_))
    p_ = g_ev({"a": "fclear"}, "TAB6 FIX back to Cooking")
    hd_ = {}
    for pg_ in range(int(GS.pages)):
        cm = cmap(g_ev({"a": "pg:1"}, "TAB6 FIX Cooking next page") if pg_ > 0 else p_)
        for k_ in range(int(SGD.RN)):
            if vis6(cm, "R%d" % k_):
                hd_[txt6(cm, "R%dN" % k_)] = txt6(cm, "R%dD" % k_)
    K.check(hd_.get("Long help") == h100_ and hd_.get("Huge help") == h200_[:100].strip(),
            "TAB6 FIX the category view: a 100-character help WHOLE, a 200-character one = the registry's 100 (%s)" % sorted(hd_))
    hk6_ = str(MDc6.HOTKEY_KEY)
    hi_ = SRG.info(hk6_)
    p_ = g_ev({"a": "find", "t": str(GS.tok), "@Q": hk6_}, "TAB6 FIX search the crouch row by its key")
    K.check(hi_ is not None and names6(cmap(p_))[:1] == [str(hi_[2])] and txt6(cmap(p_), "R0D").endswith(str(hi_[5])) and len(str(hi_[5])) > 70,
            "TAB6 FIX the double-tap crouch row's %d-character help (the longest known row) shows whole: %s" % (len(str(hi_[5])) if hi_ is not None else -1, txt6(cmap(p_), "R0D")[-40:]))
    SRG.refuse("harness.long", TRUE, "harness: done")
    SRG.refuse("harness.huge", TRUE, "harness: done")
    # FIX (tab6 fixer): a stale Mods page click after the mods list was switched off = the caption, no hub fallback
    MCF6 = JV("MenuCfg")
    mh0_ = bool(MCF6.MODS_HELP)
    MCF6.MODS_HELP = False
    try:
        GS, p_ = g_open("TAB6 reopen with the mods list off")
        f0_ = len(E.sent(PK))
        GS.handleDataEvent(PK.ref, PK.st, json.dumps({"a": "mods"}))
        cur_ = PK.pm.getCustomPage()
        K.check(not bool(MH.visible("mods", PK.pr)) and cur_ is not None and bool(cur_.equals(GS)) and not bool(GS.closed) and len(pages(PK, f0_)) == 1
                and str(sval(cmap(E.sent(PK)[-1]), "#SkyyGtabCap.Text")) == str(SGD.MODSOFF),
                "TAB6 FIX a Mods page click with the mods list off (plain player) = the 'admins' caption on ONE redraw of the same screen, no hub page (vis %s, page %s, closed %s, pages %d, cap %s)"
                % (bool(MH.visible("mods", PK.pr)), None if cur_ is None else cur_.getClass().getSimpleName(), bool(GS.closed), len(pages(PK, f0_)),
                   str(sval(cmap(E.sent(PK)[-1]), "#SkyyGtabCap.Text")) if E.sent(PK) else None))
    finally:
        MCF6.MODS_HELP = mh0_
    # TABS
    GS, p_ = g_open("TAB6 reopen for tabs")
    p_ = g_ev({"a": "tab:6"}, "TAB6 TABS Settings")
    K.eq(cap6(p_), "You are on Settings", "TAB6 TABS Settings = a caption")
    p_ = g_ev({"a": "tab:5"}, "TAB6 TABS Social")
    SO6 = PK.pm.getCustomPage()
    K.check(SO6 is not None and str(SO6.getClass().getSimpleName()) == "SocialTab" and bool(GS.closed), "TAB6 TABS Social = the social screen")
    p_ = g_ev({"a": "tab:6"}, "TAB6 OPEN the social screen's Settings tab")
    GS = PK.pm.getCustomPage()
    K.check(GS is not None and str(GS.getClass().getSimpleName()) == "SettingsTab" and bool(SO6.closed), "TAB6 OPEN the social screen's Settings tab = the settings screen")
    p_ = g_ev({"a": "tab:4"}, "TAB6 TABS World")
    WS6 = PK.pm.getCustomPage()
    K.check(WS6 is not None and str(WS6.getClass().getSimpleName()) == "WorldTab" and bool(GS.closed), "TAB6 TABS World = the world screen")
    p_ = g_ev({"a": "tab:6"}, "TAB6 OPEN the world screen's Settings tab")
    GS = PK.pm.getCustomPage()
    K.check(GS is not None and str(GS.getClass().getSimpleName()) == "SettingsTab" and bool(WS6.closed), "TAB6 OPEN the world screen's Settings tab = the settings screen")
    p_ = g_ev({"a": "tab:1"}, "TAB6 TABS Skills")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "SkillPage" and bool(GS.closed), "TAB6 TABS Skills = the skill page")
    p_ = g_ev({"a": "tab:0"}, "TAB6 TABS Inventory (from the skill page)", n=None)
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "InvPage", "TAB6 the skill page's Inventory tab")
    GS, p_ = g_open("TAB6 reopen for Inventory")
    p_ = g_ev({"a": "tab:0"}, "TAB6 TABS Inventory")
    cur_ = PK.pm.getCustomPage()
    K.check(cur_ is not None and str(cur_.getClass().getSimpleName()) == "InvPage" and str(cur_.mode) == "c" and bool(GS.closed), "TAB6 TABS Inventory = the inventory screen")
    GS, p_ = g_open("TAB6 reopen for the Tab key")
    ST.tab(PK.ref, PK.st, PK.pr, PK.pl, "test")
    K.check(PK.pm.getCustomPage() is None and bool(GS.closed), "TAB6 TABS the Tab key closes the settings screen")
    GS, p_ = g_open("TAB6 reopen for X")
    GS.handleDataEvent(PK.ref, PK.st, '{"a":"close"}')
    K.check(PK.pm.getCustomPage() is None and bool(GS.closed), "TAB6 TABS X closes the screen")
    p_ = g_ev({"a": "pg:1"}, "TAB6 SAFE a click on a closed screen", n=0, page=GS)
    K.notes.append("TAB6 counters: opens %d, stale %d, writes / commands %d" % (int(SGB.OPENS), int(SGB.STALE), int(SGB.ACTS)))
    SST.resetAll(uk6)
    E.CM.cmds.remove("skyyhud")
    if HUD6 is not None:
        E.CM.cmds.put("skyyhud", HUD6)
    E.pump(PK)
'''
T.rep('''    # ---- TREEMAP1 (0.3.61; Skyy 11-21 "i wan it to show the smithing skill tree below, not a button to open the old skill tree.")
''', HARNESS_TAB6 + '''    # ---- TREEMAP1 (0.3.61; Skyy 11-21 "i wan it to show the smithing skill tree below, not a button to open the old skill tree.")
''')
if T.dst:
    T.finish()
