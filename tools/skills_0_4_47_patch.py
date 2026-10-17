"""Derive SkyySkills/build_skyyskills_0.4.47.py from the GENERATED SkyySkills 0.4.46 (build_skyyskills_0.4.46.py = the tools/deploy_set.py SET
pin; 0.4.46 came from 0.4.45 by tools/skills_0_4_46_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with
0.4.46 (nothing else changed); 0.4.46 stays untouched, its line endings are kept (tools/soundpass_gen.Patch).
Run:  python tools/skills_0_4_47_patch.py   then   python SkyySkills/build_skyyskills_0.4.47.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.47.py
(0.4.47 was first reserved for the T1 tool-upgrade round - that round takes the next free version.)
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import skyyui as SUI

NOTE = '''0.4.47 (2026-10-16) = MENU PATTERN sweep S1 (Character hub), the SkyySkills half (research/Menu-Pattern.md 3 + 4; kit skyyui 1.7
  hub_page; tools/HUBS-CONTRACT.md "Kit 1.7" -> "How to move a page"). Skyy (docs/answered/ui.md 2026-10-16): "Double check every menu and
  make sure it's fully and completely built out / designed properly in the cohesive menu system we made. I never want to have to use a back
  button. The menus at the top should always be there for easy navigation." + "keep this top bar at this size consistent at the top across
  every menu." + "i dont mind scrolling, but if there are only a few items try to scale them to all fit." + popups: every hub page Home
  size 1600 x 980, row 2 big like Teleport (56 px).
  1. /skills (the list + its Top 10 view), a skill's Stats page and the Overall page are kit 1.7 hub pages (SUI.hub_page, 1600 x 980; the
     content 1552 wide): row 1 (Home + the hubs) and row 2 (the Character tabs, Skills selected) from HubBar.page17 on all three
     (0.4.41 - 0.4.46: the kit 1.5 hub window 974 x 980 / 914 / 755 with the small tab strip and the title-bar menu button).
  2. ONE sub-tab row (the Skills tab hosts the merged character:stats tab): [Your Stats] [Skills] [Overall], and on a skill's Stats page
     and its Top 10 view a breadcrumb [<Skill>] [Top 10] after them (SkillsPage.subRow; Your Stats = hub:stats -> SkyyMenu's Stats page
     through HubBar.openSub, shown only while that tab is published, exactly as SkyyMenu 0.3.35's Your Stats page shows [Your Stats]
     [Skills]; Skills = hub:skills = the list; Overall = skstatov; <Skill> = skstat<slot>; Top 10 = sttop - the existing actions). The
     list's hint caption sits beside the sub-tabs.
  3. NO BACK BUTTONS: the Top 10 view's BACK (skback), the Stats page's < BACK (stback) and the Overall page's BACK (ovback) went - the
     sub-tab row and rows 1 + 2 lead away; the Stats page's TOP 10 button is the Top 10 sub-tab; SKILL TREE stays (beside the how-to
     caption). The old handlers stay (no binding sends them any more).
  4. Lists: the skill list scrolls (670 px; 12 rows keep their 62 / 82 px - a short list would grow: HubBar.growSize over SK_ROW_HS, Skyy
     rule 7); the Top 10 rows grow when there are few (SK_TOP_HS 55 / 79 / 110).
  5. Clicks: HubBar.route (row 1 hub:h:<hub>, row 2, the X); a click on the Skills tab or the Character hub = the skill list. The Stats and
     Overall pages also open Your Stats (hub:stats) and the Stats page the Overall page (skstatov). HubBar = the kit's with row + page
     (install_hub_bar(row=True, sub=True, page=True)).
  6. Lint: the old docstring quotes of the menu button / back button in single quotes; the dodge direction strings (Back, BackLeft ...) marked
     menu-pattern-ok (no UI text).
  No XP / data / saved-file / command / setting change. ROLLBACK to 0.4.46: safe (the old kit 1.5 pages come back).
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.46.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.47.py"))
assert P.has('VERSION = "0.4.46"') and P.has("packStep") and not P.has("SUI.hub_page("), "not the generated SkyySkills 0.4.46 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
assert SUI.KIT_PAGE_VERSION == "1.7" and SUI.HUB_PAGE_IW == 1552, "kit skyyui 1.7 (hub_page)"


def cut(start, end):
    """the exact text of P.s from start up to and including end (start unique)"""
    assert P.s.count(start) == 1, "start anchor count %d: %s" % (P.s.count(start), start[:120])
    i = P.s.index(start)
    j = P.s.index(end, i)
    return P.s[i:j + len(end)]


def sub1(text, old, new):
    """text.replace(old, new) with old exactly once in text"""
    assert text.count(old) == 1, "inner anchor count %d: %s" % (text.count(old), old[:120])
    return text.replace(old, new, 1)


# ================================================================================================ docstring + version
P.rep('''"""SkyySkills 0.4.46 - build script (derived from the generated 0.4.45 by tools/skills_0_4_46_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.47 - build script (derived from the generated 0.4.46 by tools/skills_0_4_47_patch.py - edit the patch, not this file;
''' + NOTE + '''  CHECKED: SkyySkills/test_skyyskills_0.4.47.py.
0.4.46 was derived from the generated 0.4.45 by tools/skills_0_4_46_patch.py;
''')
P.rep('VERSION = "0.4.46"', 'VERSION = "0.4.47"')

# ================================================================================================ lint: old history notes + dodge directions
P.rep('''     Window: the Character Frame mood, the Header title bar with the crest and the hub title, "< Menu" in the title bar, the close X, the
''', '''     Window: the Character Frame mood, the Header title bar with the crest and the hub title, '< Menu' in the title bar, the close X, the
''')
P.rep('''  4. Clicks: handleDataEvent asks HubBar.handle FIRST - the X closes, "< Menu" opens the SkyWynn Menu (/skymenu), the Skills tab = the
''', '''  4. Clicks: handleDataEvent asks HubBar.handle FIRST - the X closes, '< Menu' opens the SkyWynn Menu (/skymenu), the Skills tab = the
''')
P.rep('''     skill gives right now (numbers) and what the next level adds (+ its coins), how to earn XP, "< Back" (to /skills) and
''', '''     skill gives right now (numbers) and what the next level adds (+ its coins), how to earn XP, '< Back' (to /skills) and
''')
P.rep('''assert [_r[0] for _r in DODGE_ROLLS] == ["Forward", "ForwardLeft", "ForwardRight", "Back", "BackLeft", "BackRight"]
''', '''assert [_r[0] for _r in DODGE_ROLLS] == ["Forward", "ForwardLeft", "ForwardRight", "Back", "BackLeft", "BackRight"]   # menu-pattern-ok: dodge direction
''')
P.rep('''for _k in ("Forward", "Back"):
''', '''for _k in ("Forward", "Back"):   # menu-pattern-ok: dodge direction
''')
P.rep('''STYLE_FLIP_ANIM = {"Back": "Backflip", "Left": "SideflipLeft", "Right": "SideflipRight"}   # vanilla Server/Item/Animations/Shortbow.json
''', '''STYLE_FLIP_ANIM = {"Back": "Backflip", "Left": "SideflipLeft", "Right": "SideflipRight"}   # vanilla Server/Item/Animations/Shortbow.json; menu-pattern-ok: dodge direction
''')
P.rep('''STYLE_DIRS = [("Forward", 0, -1), ("ForwardLeft", -_SD7, -_SD7), ("ForwardRight", _SD7, -_SD7), ("Back", 0, 1), ("BackLeft", -_SD7, _SD7),
''', '''STYLE_DIRS = [("Forward", 0, -1), ("ForwardLeft", -_SD7, -_SD7), ("ForwardRight", _SD7, -_SD7), ("Back", 0, 1), ("BackLeft", -_SD7, _SD7),   # menu-pattern-ok: dodge direction
''')
P.rep('''    return "Forward" if k.startswith("Forward") else ("Back" if k.startswith("Back") else k)
''', '''    return "Forward" if k.startswith("Forward") else ("Back" if k.startswith("Back") else k)   # menu-pattern-ok: dodge direction
''')
P.rep('''for _g in ("Forward", "Back", "Left", "Right"):
''', '''for _g in ("Forward", "Back", "Left", "Right"):   # menu-pattern-ok: dodge direction
''')
_l68 = [ln for ln in P.s.split("\n") if ln.startswith('    _names = [_v for _k2, _v in _fb.items() if _k2 in ("Next", "Failed", "Forward", "Back",')]
assert len(_l68) == 1 and "  # " not in _l68[0], _l68
P.rep(_l68[0] + "\n", _l68[0] + "   # menu-pattern-ok: dodge direction\n")

# ================================================================================================ HubBar: kit 1.7 (row 1 + row 2 + the sub row)
P.rep('''hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, sub=True)   # 0.4.45: + the kit's MERGED TABS methods (openSub)
''', '''assert SUI.KIT_PAGE_VERSION == "1.7", "0.4.47: kit skyyui 1.7 (hub_page, HubBar.page17)"
hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True, sub=True, page=True)   # 0.4.45: + MERGED TABS (openSub); 0.4.47: kit 1.7 (page17 / subTab / growSize / route)
''')

# ================================================================================================ sizes: the content 1552 wide
P.rep('''SK_W = 960
SK_IN_W = SK_W - 2 * SUI.CONTENT_PAD                                   # 926: the body's inner width
''', '''SK_W = SUI.HUB_PAGE_IW + 2 * SUI.CONTENT_PAD                           # 0.4.47: 1586 -> the content 1552 wide (the kit 1.7 hub page; 0.4.46: 960)
SK_IN_W = SK_W - 2 * SUI.CONTENT_PAD                                   # 1552: the content's inner width (0.4.46: 926)
''')
P.rep('''SK_TOP_SPEC = SUI.column_spec([("Rank", 100), ("Player", 444), ("Level", 150), ("XP", 200)], avail=SK_IN_W - 2 * SUI.WELL_LIST_PAD, pad_left=12)   # 0.4.41: the Top 10 well stays fixed (918)
''', '''SK_TOP_SPEC = SUI.column_spec([("Rank", 160), ("Player", 780), ("Level", 280), ("XP", 300)], avail=SK_IN_W - 2 * SUI.WELL_LIST_PAD, pad_left=12)   # 0.4.47: the 1544 px well (0.4.41: 918)
''')
P.rep('''assert SK_TEXT_W == {True: 646, False: 742}, SK_TEXT_W      # 0.4.41: 12 px narrower (the scrolling list; 0.4.40: 658 / 754)
''', '''assert SK_TEXT_W == {True: 1272, False: 1368}, SK_TEXT_W    # 0.4.47: the 1552 px content (0.4.41: 646 / 742; 0.4.40: 658 / 754)
''')
P.rep(cut('''# 0.4.41 HUBS: the three pages in the Character hub window''', '''assert SUI.assert_hub_fits(HUB, SK_IN_W) >= 110, "0.4.41: the 8 Character tabs fit the 926 px strip"
'''), '''# 0.4.47 MENU PATTERN (research/Menu-Pattern.md 3; kit skyyui 1.7 hub_page; tools/HUBS-CONTRACT.md "Kit 1.7"): the three pages are 1600 x 980
# hub pages - the title bar, row 1 (Home + the hubs), row 2 (the Character tabs, Skills selected; HubBar.page17), the ONE sub-tab row
# [Your Stats] [Skills] [Overall] (+ [<Skill>] [Top 10] on a skill's Stats page and its Top 10 view; SkillsPage.subRow) and the content,
# 1552 wide (SK_W above) and SK_CH high. No back buttons, no footer. (0.4.41 - 0.4.46: the kit 1.5 hub window, 974 x 980 / 914 / 755.)
assert SUI.KIT_PAGE_VERSION == "1.7" and SK_IN_W == SUI.HUB_PAGE_IW == 1552, "0.4.47: kit 1.7 hub_page, the content 1552 wide"
SK_CH = SUI.HUB_PAGE_H - SUI.TITLE_H - 2 * SUI.HUB_PAGE_PAD - SUI.HUB_BIG_ROW_H - SUI.HUB_BIG_TABS_H - SUI.SUB_ROW_H   # 734: the content
SK_SUB_W, SK_SUB_CAP_L = SUI.SUB_TAB_W, 12                     # the kit's 150 px sub-tabs; the hint caption 12 px after them
SK_HINT_W = SK_IN_W - 3 * SK_SUB_W - 2 * SUI.SUB_TAB_GAP - SK_SUB_CAP_L   # 1080: beside Your Stats | Skills | Overall
SK_HUB_LIST_H = SK_CH - (SK_OV_H + SK_OV_M)                    # 670: the scrolling skill list (0.4.45: 743)
SK_LIST_AVAIL = SK_HUB_LIST_H - 2 * SUI.WELL_LIST_PAD - (SK_ACRO_H - SK_ROW_H)   # 642: the room the rows share (the Acrobatics row's +20 off)
SK_ROW_HS = SUI.grow_row_sizes(SK_LIST_AVAIL, SK_ROW_H)        # Skyy rule 7: a short list grows - HubBar.growSize picks the size in build()
SK_TOP_LIST_H = SK_CH - SK_TOP_HEAD_H - (SK_RANK_M + SK_RANK_H)   # 666: the Top 10 well (0.4.41: 722; its footer row went)
SK_TOP_HS = SUI.grow_row_sizes(SK_TOP_LIST_H - 2 * SUI.WELL_LIST_PAD, SK_TOP_ROW_H)   # a short Top 10 gets bigger rows
ST_TREE_W = 8 + SUI.BTN_MIN_W                                   # SKILL TREE beside the how-to caption (the Stats footer row went)
assert (SK_CH, SK_HUB_LIST_H, SK_TOP_LIST_H, SK_LIST_AVAIL) == (734, 670, 666, 642), (SK_CH, SK_HUB_LIST_H, SK_TOP_LIST_H, SK_LIST_AVAIL)
assert SK_ROW_HS[0] == SK_ROW_H and SK_TOP_HS[0] == SK_TOP_ROW_H and len(SK_ROW_HS) == len(SK_TOP_HS) == 3, (SK_ROW_HS, SK_TOP_HS)
assert SUI.text_width(SK_HINT, 12) <= SK_HINT_W, "0.4.47: the hint fits beside the sub-tabs"
assert SUI.grow_pick(len(SK_ROW_SLOTS), SK_LIST_AVAIL, SK_ROW_HS) == 0, "0.4.47: the 12 skill rows keep their 62 / 82 px and scroll"
assert SK_HUB_LIST_H >= 2 * SUI.WELL_LIST_PAD + SK_ACRO_H + 8 * (SK_ROW_H + SUI.ROW_GAP), "0.4.47: at least 9 skill rows show at once"
assert SK_TOP_LIST_H >= SUI.list_well_h(10, SK_TOP_ROW_H), "0.4.47: the Top 10 well holds its 10 rows"
assert ST_BODY - SK_FOOT_H <= SK_CH and OV_BODY - SK_FOOT_H <= SK_CH, "0.4.47: the Stats / Overall bodies (without their footer row) fit"
for _sn in sorted(set(SLOT_LABELS + [_x[1] for _x in CLASS_ROWS] + ["Combat"])):   # every skill name a breadcrumb sub-tab can show
    SUI.assert_sub_tabs_fit(["Your Stats", "Skills", "Overall", _sn, "Top 10"], SK_SUB_W)
''')

# ================================================================================================ the page pieces
P.rep('''def sk_shell():
    """/skills (both views): the plain window SkyySkF (960 x 786); 0.4.6's root #SkyySkills is the body. The title is set at runtime:
    SKILLS on the overview, TOP 10 - <SKILL> on the leaderboard view (0.4.6's two title labels)."""
    title = SUI.J('this.view < 0 || this.view >= ' + PKG + '.SkillDefs.N ? "Skills" : "Top 10 - " + ' + PKG + '.SkillDefs.LABELS[this.view]',
                  "Skills")
    return SUI.hub_shell("SkyySkF", SK_HUB_W, SK_HUB_H, HUB, body_id="SkyySkills")   # 0.4.41: the Character hub shell (title = the hub)
''', '''def sk_shell():
    """/skills (both views): 0.4.47 the kit 1.7 hub page SkyySkF (1600 x 980, the sub-tab row, no footer); 0.4.6's root #SkyySkills is the
    content. The title bar says Character on the list and "Character - Top 10 - <Skill>" on the leaderboard view (b.set, 0.4.41)."""
    return SUI.hub_page("SkyySkF", HUB, sub=True, body_id="SkyySkFB", content_id="SkyySkills")
''')
P.rep(cut('''def sk_overview(ap, body):''', '''    ap.add(body, SUI.scroll_list("SkyySkList", w=SK_IN_W, h=SK_HUB_LIST_H, well=True))   # 0.4.41: scrolls (0.4.40: the fixed 808 px well)
'''), '''def sk_overview(ap, body):
    """The overview's static parts: the Overall well (#SkyySkOvRow: #SkyySkOv + the OVERALL button #SkyySkOvStat), the scrolling list well
    #SkyySkList (the rows go in there). #SkyySkOv's text is b.set by the kept 0.4.6 line. 0.4.47: the sub-tab row is the page's ONE sub-tab
    row (SkillsPage.subRow + sk_hint), no longer part of the body (0.4.45: #SkyySkSubRow)."""
    ap.add(body, SUI.panel("SkyySkOvRow", "well", h=SK_OV_H, layout="Left", anchor={"bottom": SK_OV_M}))
    ap.add("SkyySkOvRow", SUI.label("SkyySkOv", "", "rowName", w=SK_OV_LABEL_W, h=SUI.BTN_H))
    ap.add("SkyySkOvRow", SUI.button("SkyySkOvStat", "Overall", "secondary", anchor={"left": 8}))
    ap.add(body, SUI.scroll_list("SkyySkList", w=SK_IN_W, h=SK_HUB_LIST_H, well=True))   # 0.4.41: scrolls; 0.4.47: 670 px


def sk_hint(prefix):
    """0.4.47: the hint caption #SkyySkHint beside the sub-tabs in #<prefix>Sub (0.4.45: beside the body's own sub-tab row)."""
    ap = SUI.Appends()
    ap.text(prefix + "Sub", "SkyySkHint", SK_HINT, "caption", w=SK_HINT_W, h=SUI.SUB_TAB_H, anchor={"left": SK_SUB_CAP_L})
    return ap
''')
P.rep('''def sk_row(i, rh, pw, tw, bw, fill, col, icon, title, prog):''', '''def sk_row(i, rh, pw, tw, bw, fill, col, icon, title, prog, tp=SK_TEXT_TOP):''')
P.rep('''    ap.add(r + "P", SUI.group(t, "Top", w=tw, h=rh, pad={"top": SK_TEXT_TOP}))
''', '''    ap.add(r + "P", SUI.group(t, "Top", w=tw, h=rh, pad={"top": tp}))   # 0.4.47: tp centres the text in a grown row (2 at the normal size)
''')
P.rep('''def sk_top_row(i, me, cells):
    """One leaderboard row #SkyySkTopRow<i> (a vanilla table row, cells C0-C3 under the heads; texts b.set); your own row (me) in
    white bold: a J("me") picks it at runtime (both looks create the same ids and set the same texts)."""
    mine = SK_TOP_SPEC.row("SkyySkTopRow" + i, cells, h=SK_TOP_ROW_H, kinds="strong")
    other = SK_TOP_SPEC.row("SkyySkTopRow" + i, cells, h=SK_TOP_ROW_H, kinds="default")''', '''def sk_top_row(i, me, cells, h=SK_TOP_ROW_H):
    """One leaderboard row #SkyySkTopRow<i> (a vanilla table row, cells C0-C3 under the heads; texts b.set); your own row (me) in
    white bold: a J("me") picks it at runtime (both looks create the same ids and set the same texts). 0.4.47: h = one of SK_TOP_HS."""
    mine = SK_TOP_SPEC.row("SkyySkTopRow" + i, cells, h=h, kinds="strong")
    other = SK_TOP_SPEC.row("SkyySkTopRow" + i, cells, h=h, kinds="default")''')
P.rep('''def sk_top_foot(ap, body, rank_text):
    """The rank line #SkyySkRank (b.set) and the footer #SkyySkNav (0.4.6's id) with BACK #SkyySkBack right-aligned."""
    ap.text(body, "SkyySkRank", rank_text, "default", h=SK_RANK_H, align="Center", anchor={"top": SK_RANK_M})
    ap.add(body, SUI.button_row("SkyySkNav", align="right", used=SUI.BTN_MIN_W, avail=SK_IN_W))
    ap.add("SkyySkNav", SUI.button("SkyySkBack", "Back", "secondary", sound="cancel"))
''', '''def sk_top_foot(ap, body, rank_text):
    """The rank line #SkyySkRank (b.set). 0.4.47: the footer #SkyySkNav and its back button went (the sub-tab row and rows 1 + 2 lead away)."""
    ap.text(body, "SkyySkRank", rank_text, "default", h=SK_RANK_H, align="Center", anchor={"top": SK_RANK_M})
''')
P.rep('''def st_shell(name):
    """The Stats page: the plain window SkyyStF (960 x 848), the title bar = the skill name; 0.4.6's root #SkyySkStats is the body."""
    return SUI.hub_shell("SkyyStF", STATS_HUB_W, STATS_HUB_H, HUB, body_id="SkyySkStats")   # 0.4.41: the Character hub shell (the name is in the body's first line)
''', '''def st_shell(name):
    """The Stats page: 0.4.47 the kit 1.7 hub page SkyyStF (1600 x 980, the sub-tab row with the skill's breadcrumb, no footer); 0.4.6's
    root #SkyySkStats is the content (the skill name is in its first line)."""
    return SUI.hub_page("SkyyStF", HUB, sub=True, body_id="SkyyStFB", content_id="SkyySkStats")
''')
P.rep(cut('''def st_how(ap, body, text):''', '''def st_tree():
    return SUI.Appends([("SkyyStNav", SUI.button("SkyyStTree", "Skill tree", "secondary", anchor={"left": 6}))])
'''), '''def st_how(ap, body, text):
    """The separator and the how-to row #SkyyStHowRow: the caption #SkyyStHow (wraps; b.set) and - st_tree, when that skill has a tree -
    SKILL TREE beside it. 0.4.47: the footer row #SkyyStNav (its back button, TOP 10, SKILL TREE) went - Top 10 is a sub-tab now."""
    ap.add(body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN}))
    ap.add(body, SUI.group("SkyyStHowRow", "Left", h=ST_HOW_H))
    ap.text("SkyyStHowRow", "SkyyStHow", text, "caption", w=SK_IN_W - ST_TREE_W, h=ST_HOW_H, wrap=True)


def st_tree():
    """SKILL TREE #SkyyStTree right of the how-to caption, centred in its row (#SkyyStTreeBox)."""
    return SUI.Appends([("SkyyStHowRow", SUI.group("SkyyStTreeBox", "Top", w=ST_TREE_W, h=ST_HOW_H,
                                                    pad={"left": 8, "top": (ST_HOW_H - SUI.BTN_H) // 2})),
                        ("SkyyStTreeBox", SUI.button("SkyyStTree", "Skill tree", "secondary"))])
''')
P.rep('''def ov_shell():
    """The Overall page: the plain window, 0.4.6's ids kept for every frame part (root #SkyyOvPage, title bar #SkyyOvHead, title
    #SkyyOvHeadTxt, body #SkyyOvBody)."""
    return SUI.hub_shell("SkyyOvPage", OV_HUB_W, OV_HUB_H, HUB, body_id="SkyyOvBody")   # 0.4.41: the Character hub shell (root #SkyyOvPage kept)
''', '''def ov_shell():
    """The Overall page: 0.4.47 the kit 1.7 hub page (1600 x 980, the sub-tab row with Overall selected, no footer): root #SkyyOvPage kept,
    0.4.6's body #SkyyOvBody is the content."""
    return SUI.hub_page("SkyyOvPage", HUB, sub=True, body_id="SkyyOvPageB", content_id="SkyyOvBody")
''')
P.rep('''def ov_foot(ap, body):
    ap.add(body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN}))
    ap.text(body, "SkyyOvHow", OV_HOW, "caption", h=OV_HOW_H, wrap=True)
    ap.add(body, SUI.button_row("SkyyOvNav", align="right", used=SUI.BTN_MIN_W, avail=SK_IN_W))
    ap.add("SkyyOvNav", SUI.button("SkyyOvBack", "Back", "secondary", sound="cancel"))
''', '''def ov_foot(ap, body):
    """The separator and the how-to caption. 0.4.47: the footer row #SkyyOvNav and its back button went (the sub-tab row leads away)."""
    ap.add(body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN}))
    ap.text(body, "SkyyOvHow", OV_HOW, "caption", h=OV_HOW_H, wrap=True)
''')
P.rep(cut('''def _sk_hub(sh, idp):''', '''    return "  " + SUI.java_hub_build(sh, HUB_TAB, cls=PKG + ".HubBar", uuid="u")
'''), '''def _sk_hub(sh, idp):
    """0.4.47: a Skills tab page on the kit 1.7 hub_page - the shell + rows 1 + 2 as HubBar.page17 draws them (every contract tab of the
    hub, Skills selected): markup rules, proven properties, kit paths, the menu pattern -> its HubBar.page17 line for build()"""
    assert sh.page and (sh.w, sh.h) == (SUI.HUB_PAGE_W, SUI.HUB_PAGE_H) and sh.content_w == SK_IN_W and sh.content_h == SK_CH, sh.prefix
    assert sh.parts == SUI.HUB_PART_CLOSE and sh.sub == sh.prefix + "Sub" and sh.foot is None, sh.prefix
    pv = SUI.hub_page_preview(sh, tabs=[(r[0], SUI.hub_tab_label(HUB, r[0])) for r in SUI.hub_page_tabs(HUB)], my_tab=HUB_TAB)
    SUI.check_page(pv, idp)
    SUI.assert_proven(pv)
    els = SUI.check_sky_paths(pv, tab_icons=True)
    assert {"Header", "HeaderOrnament", SUI.HUB_FRAME[HUB], "Close"} <= set(els), "0.4.47: the Sky Window shell: %s" % els
    SUI.assert_menu_page(pv, sh)
    assert SUI.assert_big_tabs_fit(HUB) >= SUI.HUB_BIG_TAB_MIN, "0.4.47: the Character tabs fit row 2"
    return "  " + SUI.java_hub_page(sh, HUB_TAB, cls=PKG + ".HubBar", uuid="u")
''')
P.rep('''assert SK_HUB_JAVA == '  com.skyy.skills.HubBar.build(b, ev, "SkyySkF", "character", "skills", 926, u, 3);', SK_HUB_JAVA
''', '''assert SK_HUB_JAVA == '  com.skyy.skills.HubBar.page17(b, ev, "SkyySkF", "character", "skills", 1552, u, 2);', SK_HUB_JAVA   # 0.4.47
''')
P.rep('''SK_OVERVIEW_JAVA = _sk_java(_ap, "SkyySk", "    ", known=["SkyySkills"])
''', '''SK_OVERVIEW_JAVA = _sk_java(_ap, "SkyySk", "    ", known=["SkyySkills"])
SK_HINT_JAVA = _sk_java(sk_hint("SkyySkF"), "SkyySk", "    ", known=["SkyySkFSub"])   # 0.4.47: the hint beside the sub-tabs
''')
P.rep('''                              SUI.J("prog", "1234 / 5000 XP to level 13")), "SkyySk", "      ", known=["SkyySkList"])
''', '''                              SUI.J("prog", "1234 / 5000 XP to level 13"), tp=SUI.J("tp", str(SK_TEXT_TOP))), "SkyySk", "      ", known=["SkyySkList"])
''')
P.rep(cut('''_row = sk_top_row(_I, SUI.J("me"), [''', '''SK_TOP_ROW_JAVA = _sk_java(_ap, "SkyySk", "    ", known=["SkyySkTop"])
'''), '''_top_cells = [SUI.J('(i + 1) + "."', "1."), SUI.J("e[0]", "Skyy"), SUI.J('"Level " + ' + PKG + '.SkillDefs.levelOf(s, x)', "Level 12"),
              SUI.J(PKG + '.SkillDefs.fmt(x) + " XP"', "12.3k XP")]
SK_TOP_ROWS_JAVA = []      # 0.4.47: one per row size (SK_TOP_HS; HubBar.growSize picks it in build())
for _th in SK_TOP_HS:
    _ap = SUI.Appends()
    _ap.add("SkyySkTop", sk_top_row(_I, SUI.J("me"), _top_cells, h=_th))
    SK_TOP_ROWS_JAVA.append(_sk_java(_ap, "SkyySk", "      ", known=["SkyySkTop"]))
SK_TOP_ROW_JAVA, SK_TOP_ROW_JAVA1, SK_TOP_ROW_JAVA2 = SK_TOP_ROWS_JAVA
''')
P.rep('''_ap = SUI.Appends()
st_nav(_ap, "SkyySkStats", SUI.J("tree != null ? %d : %d" % (ST_NAV_GAP[True], ST_NAV_GAP[False]), str(ST_NAV_GAP[True])))
ST_NAV_JAVA = _sk_java(_ap, "SkyyS", "  ", known=["SkyySkStats"])
ST_TREE_JAVA = _sk_java(st_tree(), "SkyyS", "    ", known=["SkyyStNav"])
''', '''ST_TREE_JAVA = _sk_java(st_tree(), "SkyyS", "    ", known=["SkyyStHowRow"])   # 0.4.47: beside the how-to caption (the footer row went)
''')

# ================================================================================================ the sample states (build-time checks)
P.rep(cut('''# ---- build-time check of whole sample states:''', '''      % (SK_HUB_W, SK_HUB_H, STATS_HUB_W, STATS_HUB_H, OV_HUB_W, OV_HUB_H, KIT_ID, len(_sk_checked)))
'''), '''# ---- build-time check of whole sample states: the pieces put together the way the build() methods emit them, with concrete values.
# 0.4.47: each state on its kit 1.7 page - SUI.hub_page_preview (rows 1 + 2 as HubBar.page17 draws them), the sub-tab row as
# SkillsPage.subRow draws it (SUI.sub_tabs_preview), then the content; SUI.assert_menu_page: 1600 x 980, row 1 + row 2, ONE sub row, no
# back button / pager (inline or b.set), the content fits SK_CH.
_SK_TABS = [(r[0], SUI.hub_tab_label(HUB, r[0])) for r in SUI.hub_page_tabs(HUB)]


def sk_sub_labels(sel, skill=None, stats=True):
    """the sub-tab row (= SkillsPage.subRow): [Your Stats] (while SkyyMenu's Stats tab is published) [Skills] [Overall] (+ [<skill>]
    [Top 10] with a skill); sel 1 = Skills, 2 = Overall, 3 = the skill, 4 = Top 10 -> (labels, the selected index)"""
    labels = (["Your Stats"] if stats else []) + ["Skills", "Overall"] + ([skill, "Top 10"] if skill is not None else [])
    return labels, (1 if stats else 0) + sel - 1


def _sk_whole(parts, prefix, sh, sub, lists=(), hint=False):
    labels, sel = sub
    pv = SUI.hub_page_preview(sh, tabs=_SK_TABS, my_tab=HUB_TAB)
    pv.extend(SUI.sub_tabs_preview(sh.prefix, labels, sel, SK_SUB_W))
    if hint:
        pv.extend(sk_hint(sh.prefix))
    for p in parts:
        pv.extend(p)
    SUI.check_page(pv, prefix)
    SUI.assert_proven(pv)
    SUI.check_sky_paths(pv, tab_icons=True)
    SUI.assert_menu_page(pv, sh, sets=[("#%s.%s" % (i_, k_), v_) for i_, k_, v_ in pv.sets])
    left = SUI.fit([SUI.used_height(pv, sh.content)], sh.content_h, sh.content)
    for lid, lh in lists:
        SUI.fit([SUI.used_height(pv, lid)], lh - 2 * SUI.WELL_LIST_PAD, lid)
    return pv, left


def sk_state_overview(trees, rows, stats=True):
    """rows = [(slot, title, prog, fill, tree)]; trees = SkyyTrees running; stats = SkyyMenu's Stats tab published."""
    sh = sk_shell()
    parts = []
    ap = SUI.Appends()
    sk_overview(ap, sh.content)
    ap.sets.append(("SkyySkOv", "Text", "Overall Level 12  -  average 12.4 of 9 skills"))
    parts.append(ap)
    for i, (sl, title, prog, fill, tree) in enumerate(rows):
        acro = sl == ACRO_SLOT
        rh = SK_ACRO_H if acro else SK_ROW_H
        parts.append(sk_row(str(i), rh, SK_PANEL_W[trees], SK_TEXT_W[trees], SK_XP_W[trees], fill, SLOT_COLORS[sl], SLOT_ICONS[sl], title,
                            prog))
        if acro:
            b = sk_bonus(str(i))
            b.sets.append(("SkyySkBonus", "Text", "Speed 5%   Jump 0.3 blocks   Fall damage -10%"))
            parts.append(b)
        if trees:
            parts.append(sk_tree(str(i), rh) if tree else sk_tree_gap(str(i), rh))
        parts.append(sk_stat(str(i), rh))
    whole, left = _sk_whole(parts, "SkyySk", sh, sk_sub_labels(1, stats=stats), [("SkyySkList", SK_LIST_H)], hint=True)
    assert left == 0, "the /skills content is not filled exactly: %d px left" % left
    for i in range(len(rows)):
        assert SUI.used_width(whole, "SkyySkRow%d" % i) == SK_LIST_IN, "row %d is %d px of %d" % (i, SUI.used_width(whole, "SkyySkRow%d" % i),
                                                                                            SK_LIST_IN)
    return whole


def sk_state_top(rows, me_at, rank_text):
    sh = sk_shell()
    parts = []
    ap = SUI.Appends()
    sk_top(ap, sh.content)
    parts.append(ap)
    if not rows:
        parts.append(sk_top_empty())
    th = SK_TOP_HS[SUI.grow_pick(min(len(rows), 10), SK_TOP_LIST_H - 2 * SUI.WELL_LIST_PAD, SK_TOP_HS)]   # = HubBar.growSize in build()
    for i, (nm, lv, xp) in enumerate(rows[:10]):
        a = SUI.Appends()
        a.add("SkyySkTop", sk_top_row(str(i), i == me_at, ["%d." % (i + 1), nm, "Level %d" % lv, xp + " XP"], h=th))
        parts.append(a)
    ap = SUI.Appends()
    sk_top_foot(ap, sh.content, rank_text)
    parts.append(ap)
    whole, left = _sk_whole(parts, "SkyySk", sh, sk_sub_labels(4, skill="Mining"), [("SkyySkTop", SK_TOP_LIST_H)])
    assert left == 0, "the Top 10 content is not filled exactly: %d px left" % left
    return whole


def st_state(name, fill, note, now, nxt, legacy, maxed, tree):
    sh = st_shell(name)
    parts = []
    ap = SUI.Appends()
    st_top(ap, sh.content)
    ap.sets += [("SkyyStTitle", "Text", name + " - level 12 of 100"), ("SkyyStSub", "Text", "1.2k / 5k XP to level 13  (3.8k to go)")]
    parts += [ap, st_bar(fill)]
    if note:
        n = st_note()
        n.sets.append(("SkyyStNote", "Text", "You are not a Mage right now - these boosts work while you are one"))
        parts.append(n)
    else:
        parts.append(st_note_gap())
    ap = SUI.Appends()
    st_mid(ap, sh.content)
    ap.sets.append(("SkyyStNowHd", "Text", "Boosts right now (level 12)"))
    parts.append(ap)
    for i, t in enumerate(now[:ST_LINES]):
        parts.append(st_line("SkyyStNowBox", "SkyyStNow%d" % i, t, "white"))
    if legacy:
        parts.append(SUI.Appends([(sh.content, SUI.spacer(h=ST_HEAD_T + ST_HEAD_H + ST_HEAD_B + ST_BOX_H))]))
    elif maxed:
        ap = SUI.Appends()
        st_next_head(ap, sh.content, "Max level reached - nothing more to unlock", col="gold")
        ap.add(sh.content, SUI.spacer(h=ST_BOX_H))
        parts.append(ap)
    else:
        ap = SUI.Appends()
        st_next_head(ap, sh.content)
        ap.add(sh.content, SUI.panel("SkyyStNextBox", "well", h=ST_BOX_H))
        ap.sets.append(("SkyyStNextHd", "Text", "Level 13 adds"))
        parts.append(ap)
        for i, t in enumerate(nxt[:ST_LINES]):
            parts.append(st_line("SkyyStNextBox", "SkyyStNext%d" % i, t, "buttonText"))
    ap = SUI.Appends()
    st_how(ap, sh.content, "Earn XP by mining stone and ores - rarer ores pay more")
    parts.append(ap)
    if tree:
        parts.append(st_tree())
    whole, left = _sk_whole(parts, "SkyyS", sh, sk_sub_labels(3, skill=name),
                            [("SkyyStNowBox", ST_BOX_H + 2 * SUI.WELL_LIST_PAD - 2 * SUI.WELL_PAD)])
    assert left == SK_CH - (ST_BODY - SK_FOOT_H), "the Stats content: %d px left" % left
    assert SUI.used_width(whole, "SkyyStHowRow") == (SK_IN_W if tree else SK_IN_W - ST_TREE_W), (tree, SUI.used_width(whole, "SkyyStHowRow"))
    return whole


def ov_state(maxed, now, nxt):
    sh = ov_shell()
    parts = []
    ap = SUI.Appends()
    ov_top(ap, sh.content, "Level 12 of 100", "Average of your skills 12.4 - Overall Level 13 at an average of 13.0", 0 if maxed else 240,
           "Skills that count (9)", "Mining 14 - Foraging 9 - Farming 3 - Acrobatics 20 - Alchemy 1 - Smithing 2 - Cooking 0 - Exploration 5 "
           "- Divinity 18 (your class)")
    parts.append(ap)
    for i, t in enumerate(now[:OV_NOW_N]):
        parts.append(st_line("SkyyOvNowBox", "SkyyOvNow%d" % i, t, "white"))
    ap = SUI.Appends()
    if maxed:
        ov_next(ap, sh.content, "Max Overall Level reached", col="gold", box=False)
    else:
        ov_next(ap, sh.content, "Overall Level 13 adds")
    parts.append(ap)
    if not maxed:
        for i, t in enumerate(nxt[:OV_NEXT_N]):
            parts.append(st_line("SkyyOvNextBox", "SkyyOvNext%d" % i, t, "buttonText"))
    ap = SUI.Appends()
    ov_foot(ap, sh.content)
    parts.append(ap)
    whole, left = _sk_whole(parts, "SkyyOv", sh, sk_sub_labels(2))
    assert left == SK_CH - (OV_BODY - SK_FOOT_H), "the Overall content: %d px left" % left
    return whole


_rows9 = [(sl, "Class skill - choose a class with /class", "Your combat skill is your class skill", 0, False) if sl == COMBAT_SLOT
          else (sl, SLOT_LABELS[sl] + "  12", "1.2k / 5k XP to level 13", 200, sl in (0, 1, 2, 12)) for sl in SK_ROW_SLOTS]
_sk_checked = [sk_state_overview(True, _rows9), sk_state_overview(False, _rows9), sk_state_overview(True, _rows9, stats=False),
               sk_state_top([("Skyy", 40, "1.2m"), ("Alex, the 2nd", 12, "12.3k"), ("Sam (profile 2)", 1, "55")], 0,
                            "Your rank #1 of 3 - level 40 - 1.2m XP"),
               sk_state_top([("P%d" % n, 50 - n, "%dk" % (99 - n)) for n in range(12)], -1, "Your rank #11 of 12 - level 39 - 88k XP"),
               sk_state_top([("P%d" % n, 50 - n, "%dk" % (99 - n)) for n in range(7)], 2, "Your rank #3 of 7 - level 48 - 97k XP"),
               sk_state_top([], -1, "You are not ranked yet"),
               st_state("Mining", 300, False, ["+0.25% chance to double the drops of mined blocks"] * 7, ["+0.005% chance"] * 7, False, False, True),
               st_state("Fury", 0, True, ["+1 max Health"], ["+0.2% damage with Berserker weapons"], False, False, False),
               st_state("Combat", 0, False, ["No class yet - choose one with /class to start leveling combat"], [], True, False, False),
               st_state("Cooking", 600, False, ["Food you cook gets stronger"], [], False, True, True),
               st_state("Swordsmanship", 100, False, ["+1 max Health"], ["+0.1 max Health"], False, False, True),
               ov_state(False, ["+6 max Health (0.5 per Overall Level)", "+2.4 max Mana (0.2 per Overall Level)", "Base Mana 10"],
                        ["+0.5 max Health", "+0.2 max Mana"]),
               ov_state(True, ["+50 max Health (0.5 per Overall Level)"], [])]
print("skills pages (kit 1.7 hub pages %d x %d, the sub-tab row, content %d x %d): /skills list %d px (scrolls; rows %s), Top 10 rows %s, "
      "Stats, Overall on %s - %d sample states checked (check_page, assert_proven, assert_menu_page, heights)"
      % (SUI.HUB_PAGE_W, SUI.HUB_PAGE_H, SK_IN_W, SK_CH, SK_HUB_LIST_H, SK_ROW_HS, SK_TOP_HS, KIT_ID, len(_sk_checked)))
''')

# ================================================================================================ SkillsPage: the row sizes + the sub-tab row
P.rep('''page.addField(CtField.make("public int view;", page))
''', '''page.addField(CtField.make("public int view;", page))
# 0.4.47 (Skyy rule 7): the row sizes HubBar.growSize picks from (the skill list; the Top 10 well)
page.addField(CtField.make("public static final int[] ROW_HS = new int[] { %s };" % ", ".join(str(x) for x in SK_ROW_HS), page))
page.addField(CtField.make("public static final int[] TOP_HS = new int[] { %s };" % ", ".join(str(x) for x in SK_TOP_HS), page))
''')
P.rep('''public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ');
}""", page))
''', '''public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ');
}""", page))
# 0.4.47 MENU PATTERN: the ONE sub-tab row of the three Skills tab pages (into #<prefix>Sub, kit HubBar.subTab, 150 px): [Your Stats] (only
# while SkyyMenu's Stats tab - merged into this tab - is published; hub:stats -> openSub) [Skills] (hub:skills = the list) [Overall]
# (skstatov) and with a skill (s >= 0) its breadcrumb [<name>] (skstat<s>) [Top 10] (sttop). sel: 1 Skills, 2 Overall, 3 the skill,
# 4 Top 10; the selected one is drawn Primary and (but Skills) not bound. Returns the number of sub-tabs.
page.addMethod(CtNewMethod.make(f"""
public static int subRow({UCB} b, {UEB} ev, String prefix, int sel, int s, String name) {{
  int i = 0;
  if ({PKG}.HubBar.get("hub:tab:character:stats") instanceof Object[]) {{
    {PKG}.HubBar.subTab(b, ev, prefix, i, "Your Stats", false, "hub:stats", {SK_SUB_W});
    i++;
  }}
  {PKG}.HubBar.subTab(b, ev, prefix, i, "Skills", sel == 1, "hub:skills", {SK_SUB_W});
  i++;
  String a2 = "skstatov";
  if (sel == 2) a2 = null;
  {PKG}.HubBar.subTab(b, ev, prefix, i, "Overall", sel == 2, a2, {SK_SUB_W});
  i++;
  if (s >= 0 && s < {PKG}.SkillDefs.N) {{
    String a3 = "skstat" + s;
    if (sel == 3) a3 = null;
    String nm = name == null ? {PKG}.SkillDefs.LABELS[s] : name;
    {PKG}.HubBar.subTab(b, ev, prefix, i, nm, sel == 3, a3, {SK_SUB_W});
    i++;
    String a4 = "sttop";
    if (sel == 4) a4 = null;
    {PKG}.HubBar.subTab(b, ev, prefix, i, "Top 10", sel == 4, a4, {SK_SUB_W});
    i++;
  }}
  return i;
}}""", page))
''')

# ---- SkillsPage.build
P.rep('''    // the Overall well + OVERALL button, the list well, the hint caption
    boolean stx = {PKG}.HubBar.get("hub:tab:character:stats") instanceof Object[];   // 0.4.45: SkyyMenu's Stats page is here (YOUR STATS)
{SK_OVERVIEW_JAVA}
    if (stx) ev.addEventBinding({BT}.Activating, "#SkyySkSubMe", {EVD}.of("a", "hub:stats"));   // 0.4.45: YOUR STATS = the Stats page
    ev.addEventBinding({BT}.Activating, "#SkyySkSubSk", {EVD}.of("a", "hub:skills"));            // 0.4.45: SKILLS = this list ("self")
''', '''    // 0.4.47: the ONE sub-tab row (Your Stats | Skills | Overall) + the hint beside it; the Overall well + OVERALL button, the list well
    subRow(b, ev, "SkyySkF", 1, -1, null);
{SK_HINT_JAVA}
{SK_OVERVIEW_JAVA}
''')
P.rep('''    int bw = trees ? {SK_XP_W[True]} : {SK_XP_W[False]};
    for (int i = 0; i < rows.length; i++) {{
''', '''    int bw = trees ? {SK_XP_W[True]} : {SK_XP_W[False]};
    int gk = {PKG}.HubBar.growSize(rows.length, {SK_LIST_AVAIL}, ROW_HS, {SUI.ROW_GAP});   // 0.4.47 Skyy rule 7: a short list grows (12 rows: the normal size)
    for (int i = 0; i < rows.length; i++) {{
''')
P.rep('''      int rh = acroRow ? {SK_ACRO_H} : {SK_ROW_H};
''', '''      int rh = ROW_HS[gk] + (acroRow ? {SK_ACRO_H - SK_ROW_H} : 0);   // 0.4.47: {SK_ROW_H} / {SK_ACRO_H} at the normal size
      int tp = (rh - (acroRow ? {SK_ACRO_H} : {SK_ROW_H})) / 2 + {SK_TEXT_TOP};
''')
P.rep('''  b.set("#SkyySkFTitle.Text", "Character - Top 10 - " + {PKG}.SkillDefs.LABELS[s]);   // 0.4.41: the view's title (was the window title)
''', '''  b.set("#SkyySkFTitle.Text", "Character - Top 10 - " + {PKG}.SkillDefs.LABELS[s]);   // 0.4.41: the view's title (was the window title)
  subRow(b, ev, "SkyySkF", 4, s, {PKG}.SkillDefs.LABELS[s]);   // 0.4.47: [Your Stats] [Skills] [Overall] [<Skill>] [Top 10] (selected)
''')
P.rep('''  for (int i = 0; i < n; i++) {{
    Object[] e = (Object[]) rows.get(i);
    long x = ((Long) e[1]).longValue();
    boolean me = {PKG}.SkillStore.pkey(u).equals(e[2]);
{SK_TOP_ROW_JAVA}
  }}
''', '''  int tk = {PKG}.HubBar.growSize(n, {SK_TOP_LIST_H - 2 * SUI.WELL_LIST_PAD}, TOP_HS, {SUI.ROW_GAP});   // 0.4.47 Skyy rule 7: a short Top 10 gets bigger rows
  for (int i = 0; i < n; i++) {{
    Object[] e = (Object[]) rows.get(i);
    long x = ((Long) e[1]).longValue();
    boolean me = {PKG}.SkillStore.pkey(u).equals(e[2]);
    if (tk == 2) {{
{SK_TOP_ROW_JAVA2}
    }} else if (tk == 1) {{
{SK_TOP_ROW_JAVA1}
    }} else {{
{SK_TOP_ROW_JAVA}
    }}
  }}
''')
P.rep('''  // the rank line + the footer (BACK)
{SK_TOP_FOOT_JAVA}
  ev.addEventBinding({BT}.Activating, "#SkyySkBack", {EVD}.of("a", "skback"));
}}"""
''', '''  // the rank line (0.4.47: the footer's back button went - the sub-tab row leads away)
{SK_TOP_FOOT_JAVA}
}}"""
''')
P.rep('''for _piece in (SK_SHELL_JAVA, SK_HUB_JAVA, SK_OVERVIEW_JAVA, SK_ROW_JAVA,''',
      '''for _piece in (SK_SHELL_JAVA, SK_HUB_JAVA, SK_HINT_JAVA, SK_TOP_ROW_JAVA1, SK_TOP_ROW_JAVA2, SK_OVERVIEW_JAVA, SK_ROW_JAVA,''')

# ---- StatsPage.build
P.rep('''{ST_SHELL_JAVA}
{ST_HUB_JAVA}
{ST_TOP_JAVA}
''', '''{ST_SHELL_JAVA}
{ST_HUB_JAVA}
  {PKG}.SkillsPage.subRow(b, ev, "SkyyStF", 3, s, name);   // 0.4.47: [Your Stats] [Skills] [Overall] [<Skill>] (selected) [Top 10]
{ST_TOP_JAVA}
''')
P.rep('''  // the separator + the how-to caption, the footer (< BACK, TOP 10, SKILL TREE when that skill has a tree)
''', '''  // the separator + the how-to caption, SKILL TREE beside it when that skill has a tree (0.4.47: the footer row went - Top 10 is a sub-tab)
''')
P.rep('''{ST_NAV_JAVA}
  ev.addEventBinding({BT}.Activating, "#SkyyStBack", {EVD}.of("a", "stback"));
  ev.addEventBinding({BT}.Activating, "#SkyyStTop", {EVD}.of("a", "sttop"));
''', '''  // 0.4.47: no footer row (its back button went; TOP 10 = the Top 10 sub-tab, sttop)
''')
P.rep('''               ST_MAX_JAVA, ST_LEGACY_GAP_JAVA, ST_HOW_JAVA, ST_NAV_JAVA, ST_TREE_JAVA):''',
      '''               ST_MAX_JAVA, ST_LEGACY_GAP_JAVA, ST_HOW_JAVA, ST_TREE_JAVA):''')

# ---- OverallPage.build
P.rep('''{OV_SHELL_JAVA}
{OV_HUB_JAVA}
{OV_TOP_JAVA}
''', '''{OV_SHELL_JAVA}
{OV_HUB_JAVA}
  {PKG}.SkillsPage.subRow(b, ev, "SkyyOvPage", 2, -1, null);   // 0.4.47: [Your Stats] [Skills] [Overall] (selected)
{OV_TOP_JAVA}
''')
P.rep('''  // the separator, the how-to caption, the footer (BACK)
{OV_FOOT_JAVA}
  ev.addEventBinding({BT}.Activating, "#SkyyOvBack", {EVD}.of("a", "ovback"));
}}"""
''', '''  // the separator, the how-to caption (0.4.47: the footer's back button went - the sub-tab row leads away)
{OV_FOOT_JAVA}
}}"""
''')

# ================================================================================================ the clicks
OLD_ROUTE = '''    String hr = {PKG}.HubBar.handle(this.playerRef, data, "character", "skills");   // 0.4.41 hubs: the bar first (null = not a hub click)
'''
NEW_ROUTE = '''    String hr = {PKG}.HubBar.route(this.playerRef, data, "character", "skills");   // 0.4.41 hubs: the bar first (null = not a hub click); 0.4.47: route = + row 1 (hub:h:<hub>; Character = "self")
'''
STATS_SUB = '''    if ("hub:stats".equals({PKG}.HubBar.jsonStr(data, "a"))) {{   // 0.4.47: the sub-tab YOUR STATS = SkyyMenu's Stats page (a merged tab: openSub)
      String sr = {PKG}.HubBar.openSub(this.playerRef, this.playerRef.getUuid(), "character", "stats");
      if (!sr.equals("bridge") && !sr.equals("command")) this.playerRef.sendMessage({MSG}.raw("[Skills] Your Stats page could not open right now - try /stats."));
      return;
    }}
'''
# StatsPage.handleDataEvent moves below the OverallPage constructor (its new Overall sub-tab opens that page: javassist compiles a call only
# to a constructor that exists already) - otherwise unchanged + YOUR STATS + route + the Overall sub-tab
OLD_ST_EV = cut('''spg.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{''', '''  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("stats page event failed: " + t); }}
}}""", spg))
''')
NEW_ST_EV = sub1(sub1(OLD_ST_EV, OLD_ROUTE, STATS_SUB + NEW_ROUTE), '''    if (p == null) return;
''', '''    if (p == null) return;
    if (data.indexOf("skstatov\\\\"") >= 0) {{ p.getPageManager().openCustomPage(ref, st, new {PKG}.OverallPage(this.playerRef)); return; }}   // 0.4.47: the Overall sub-tab
''')
P.rep(OLD_ST_EV, '''# 0.4.47: StatsPage.handleDataEvent is added below the OverallPage constructor (its Overall sub-tab opens that page)
''')
P.rep('''opg.addConstructor(CtNewConstructor.make(f"""
public OverallPage({PR} pr) {{
  super(pr, {LIFE}.CanDismiss);
}}""", opg))
''', '''opg.addConstructor(CtNewConstructor.make(f"""
public OverallPage({PR} pr) {{
  super(pr, {LIFE}.CanDismiss);
}}""", opg))
# 0.4.47: the Stats page's clicks (moved here from above: the Overall sub-tab needs the OverallPage constructor)
''' + NEW_ST_EV)
OLD_OV_EV = cut('''opg.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{''', '''  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("overall page event failed: " + t); }}
}}""", opg))
''')
P.rep(OLD_OV_EV, sub1(OLD_OV_EV, OLD_ROUTE, STATS_SUB + NEW_ROUTE))
P.rep('''      return;
    }}
''' + OLD_ROUTE + '''    if (hr != null) {{
      if (hr.equals("close")) {{ close(); return; }}
      if (hr.equals("self")) {{ this.view = -1; rebuild(); return; }}
''', '''      return;
    }}
''' + NEW_ROUTE + '''    if (hr != null) {{
      if (hr.equals("close")) {{ close(); return; }}
      if (hr.equals("self")) {{ this.view = -1; rebuild(); return; }}
''')
assert not P.has(OLD_ROUTE), "every Skills page routes through HubBar.route (kit 1.6+: row 1)"

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
