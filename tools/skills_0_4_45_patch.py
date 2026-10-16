"""Derive SkyySkills/build_skyyskills_0.4.45.py from the GENERATED SkyySkills 0.4.44 (build_skyyskills_0.4.44.py = the tools/deploy_set.py SET
pin; 0.4.44 came from 0.4.43 by tools/skills_0_4_44_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with
0.4.44 (nothing else changed); 0.4.44 stays untouched, its line endings are kept (tools/soundpass_gen.Patch).
Run:  python tools/skills_0_4_45_patch.py   then   python SkyySkills/build_skyyskills_0.4.45.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.45.py
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

NOTE = '''0.4.45 (2026-10-16) = STATS + SKILLS ARE ONE TAB, the SkyySkills half (round hubchar, with SkyyMenu 0.3.33, SkyyTrees 0.3.19, SkyyClasses
  0.1.33). Skyy 2026-10-16 popup "HUBS: Character hub tabs stay separate, or merge like your 10-10 pick (Stats+Skills, Trees+Abilities,
  Collections+Recipes; Bank+Vault, Bazaar+Auction House)?" -> "Merge now"; "menu merge first. mod compress later."; LOCKED 2026-10-10
  "Stats + Skills, Trees + Abilities, ..." (docs/answered/ui.md). SkyyMenu 0.3.33 makes its Stats tab a MERGED tab of this Skills tab
  (kit skyyui HUB_MERGED: still published, never drawn in a strip), so the Character strip shows one SKILLS tab for both.
  1. /skills (the skill list) gets a sub-tab row FIRST under the strip: [YOUR STATS] [SKILLS] (Skills active) with the old hint caption
     beside them (its own line under the list is gone). YOUR STATS opens SkyyMenu's Stats page through HubBar.openSub (the kit's merged
     tab open: its open Function, else /stats) and shows only while hub:tab:character:stats is published (else a blank of its width);
     SKILLS = the skill list (the tab's "self" click). The scrolling list well 749 -> 743 px (still 11 rows and most of the 12th at once);
     the page stays 974 x 980. The Top 10 view, a skill's Stats page and the Overall page are unchanged (Skills selected, their own Back).
  2. HubBar = the kit's with the MERGED TABS methods (install_hub_bar(sub=True): hostOf / putSub / openSub / selOf / subTabs).
  No gameplay change, no saved data, no command, no setting. ROLLBACK to 0.4.44: safe (the sub-tab row goes; with SkyyMenu 0.3.33 the
  Stats page is then reached by /stats or a shortcut only - roll SkyyMenu back to 0.3.32 together, deploy_set rule).
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.44.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.45.py"))
assert P.has('VERSION = "0.4.44"') and P.has("Pd44Mig") and not P.has("SkyySkSubRow"), "not the generated SkyySkills 0.4.44 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

# ================================================================================================ docstring + version
P.rep('''"""SkyySkills 0.4.44 - build script (derived from the generated 0.4.43 by tools/skills_0_4_44_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.45 - build script (derived from the generated 0.4.44 by tools/skills_0_4_45_patch.py - edit the patch, not this file;
''' + NOTE + '''  CHECKED: SkyySkills/test_skyyskills_0.4.45.py.
0.4.44 was derived from the generated 0.4.43 by tools/skills_0_4_44_patch.py;
''')
P.rep('VERSION = "0.4.44"', 'VERSION = "0.4.45"')

# ================================================================================================ the kit HubBar with the merged-tab methods
P.rep('''hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod)
hopen = pool.makeClass(PKG + ".SkillsHubOpen")''', '''hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, sub=True)   # 0.4.45: + the kit's MERGED TABS methods (openSub)
hopen = pool.makeClass(PKG + ".SkillsHubOpen")''')

# ================================================================================================ the sub-tab row (YOUR STATS | SKILLS + the hint)
P.rep('''SK_HUB_LIST_H = SK_HUB_BODY - (SK_OV_H + SK_OV_M) - (SK_HINT_M + SK_HINT_H)               # 749 (0.4.40: the fixed SK_LIST_H 808)
''', '''SK_SUB_W, SK_SUB_B, SK_SUB_CAP_L = 130, 3, 12                                          # 0.4.45: the sub-tab row (2 small tabs, 3 under it)
SK_SUB_TABS = ("Your Stats", "Skills")                                                   # 0.4.45: the Skills tab's two sub-views (Stats + Skills)
SK_HUB_LIST_H = SK_HUB_BODY - (SUI.BTN_SMALL_H + SK_SUB_B) - (SK_OV_H + SK_OV_M)        # 743 (0.4.44: 749 with the hint line under it)
''')
P.rep('''assert (SK_HUB_W, SK_HUB_BODY, SK_HUB_LIST_H, SK_TOP_LIST_H, STATS_HUB_H, OV_HUB_H) == (974, 842, 749, 722, 914, 755), "0.4.41 hub sizes"''',
      '''assert (SK_HUB_W, SK_HUB_BODY, SK_HUB_LIST_H, SK_TOP_LIST_H, STATS_HUB_H, OV_HUB_H) == (974, 842, 743, 722, 914, 755), "0.4.41 / 0.4.45 hub sizes"
assert SUI.text_width(SK_HINT, 12) <= SK_IN_W - 2 * SK_SUB_W - SUI.TAB_GAP - SK_SUB_CAP_L, "0.4.45: the hint fits beside the sub-tabs"''')
P.rep('''def sk_overview(ap, body):
    """The overview's static parts: the Overall well (#SkyySkOvRow: #SkyySkOv + the OVERALL button #SkyySkOvStat), the list well
    #SkyySkList (the rows go in there) and the hint caption. #SkyySkOv's text is b.set by the kept 0.4.6 line."""
    ap.add(body, SUI.panel("SkyySkOvRow", "well", h=SK_OV_H, layout="Left", anchor={"bottom": SK_OV_M}))''',
      '''def sk_overview(ap, body):
    """The overview's static parts: 0.4.45 the sub-tab row #SkyySkSubRow (YOUR STATS #SkyySkSubMe - only while J("stx"): SkyyMenu's Stats
    tab is published, else a blank Group of the same id -, SKILLS #SkyySkSubSk active, the hint caption #SkyySkHint beside them), the Overall well (#SkyySkOvRow: #SkyySkOv +
    the OVERALL button #SkyySkOvStat), the list well #SkyySkList (the rows go in there). #SkyySkOv's text is b.set by the kept 0.4.6 line."""
    ap.add(body, SUI.group("SkyySkSubRow", "Left", h=SUI.BTN_SMALL_H, anchor={"bottom": SK_SUB_B}))
    ap.add("SkyySkSubRow", SUI.choose(SUI.J("stx", "true"), SUI.button("SkyySkSubMe", SK_SUB_TABS[0], "secondary", "small", w=SK_SUB_W),
                                      SUI.group("SkyySkSubMe", None, w=SK_SUB_W, h=SUI.BTN_SMALL_H)))   # a blank with the same id (choose rule)
    ap.add("SkyySkSubRow", SUI.button("SkyySkSubSk", SK_SUB_TABS[1], "primary", "small", w=SK_SUB_W, anchor={"left": SUI.TAB_GAP}))
    ap.text("SkyySkSubRow", "SkyySkHint", SK_HINT, "caption", w=SK_IN_W - 2 * SK_SUB_W - SUI.TAB_GAP - SK_SUB_CAP_L, h=SUI.BTN_SMALL_H,
            anchor={"left": SK_SUB_CAP_L})
    ap.add(body, SUI.panel("SkyySkOvRow", "well", h=SK_OV_H, layout="Left", anchor={"bottom": SK_OV_M}))''')
P.rep('''    ap.add(body, SUI.scroll_list("SkyySkList", w=SK_IN_W, h=SK_HUB_LIST_H, well=True))   # 0.4.41: scrolls (0.4.40: the fixed 808 px well)
    ap.text(body, "SkyySkHint", SK_HINT, "caption", h=SK_HINT_H, align="Center", anchor={"top": SK_HINT_M})
''', '''    ap.add(body, SUI.scroll_list("SkyySkList", w=SK_IN_W, h=SK_HUB_LIST_H, well=True))   # 0.4.41: scrolls (0.4.40: the fixed 808 px well)
''')
P.rep('''    // the Overall well + OVERALL button, the list well, the hint caption
{SK_OVERVIEW_JAVA}
''', '''    // the Overall well + OVERALL button, the list well, the hint caption
    boolean stx = {PKG}.HubBar.get("hub:tab:character:stats") instanceof Object[];   // 0.4.45: SkyyMenu's Stats page is here (YOUR STATS)
{SK_OVERVIEW_JAVA}
    if (stx) ev.addEventBinding({BT}.Activating, "#SkyySkSubMe", {EVD}.of("a", "hub:stats"));   // 0.4.45: YOUR STATS = the Stats page
    ev.addEventBinding({BT}.Activating, "#SkyySkSubSk", {EVD}.of("a", "hub:skills"));            // 0.4.45: SKILLS = this list ("self")
''')
P.rep('''    String hr = {PKG}.HubBar.handle(this.playerRef, data, "character", "skills");   // 0.4.41 hubs: the bar first (null = not a hub click)
    if (hr != null) {{
      if (hr.equals("close")) {{ close(); return; }}
      if (hr.equals("self")) {{ this.view = -1; rebuild(); return; }}''',
      '''    if ("hub:stats".equals({PKG}.HubBar.jsonStr(data, "a"))) {{   // 0.4.45: YOUR STATS = SkyyMenu's Stats page (a merged tab: openSub)
      String sr = {PKG}.HubBar.openSub(this.playerRef, this.playerRef.getUuid(), "character", "stats");
      if (!sr.equals("bridge") && !sr.equals("command")) this.playerRef.sendMessage({MSG}.raw("[Skills] Your Stats page could not open right now - try /stats."));
      return;
    }}
    String hr = {PKG}.HubBar.handle(this.playerRef, data, "character", "skills");   // 0.4.41 hubs: the bar first (null = not a hub click)
    if (hr != null) {{
      if (hr.equals("close")) {{ close(); return; }}
      if (hr.equals("self")) {{ this.view = -1; rebuild(); return; }}''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
