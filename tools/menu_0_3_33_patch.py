"""Derive SkyyMenu/build_skyymenu_0.3.33.py from the LIVE SkyyMenu 0.3.32 (python tools/menu_0_3_33_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_32_patch.py -> 0.3.32 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.33. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.32 (nothing else changed). The harness SkyyMenu/test_skyymenu_0.3.33.py is its own file.

0.3.33 (2026-10-16) = round hubchar, THE CHARACTER HUB MERGES (with SkyySkills 0.4.45, SkyyTrees 0.3.19, SkyyClasses 0.1.33).
Skyy 2026-10-16 popup "HUBS: Character hub tabs stay separate, or merge like your 10-10 pick (Stats+Skills, Trees+Abilities,
Collections+Recipes; Bank+Vault, Bazaar+Auction House)?" -> "Merge now"; "menu merge first. mod compress later."; LOCKED 2026-10-10 "Stats +
Skills, Trees + Abilities, ..." (docs/answered/ui.md); 2026-10-15 "id do skills as the default one for this, but each page should keep its
own to open it, its just hidden by default."; 2026-10-16 "make sure we dont have any duplicates".
  1. STATS IS PART OF THE SKILLS TAB (kit skyyui MERGED TABS, tools/skyyui.py HUB_MERGED): hub:tab:character:stats stays published (every
     shortcut, /stats, /profilestats and saved pin keeps opening the Stats page) but as a MERGED tab - element 5 = HubHide (FALSE while
     SkyySkills' Skills tab is published, so no Character strip of any jar draws a Stats tab; TRUE without SkyySkills: Stats stays a tab of
     its own), element 7 = "skills" (its host). The Character strip: Skills, Trees, Pets, Accessories, Collections, Profiles.
  2. THE STATS PAGE = the Skills tab's "Your Stats" sub-view: its strip shows SKILLS selected (HubBar.selOf); a new first row under the
     strip holds the two sub-tabs [YOUR STATS] (active) [SKILLS] and the page's old caption line beside them (the caption's own row is
     gone, so the page grows 8 px: 1114 x 966 -> 1114 x 974). YOUR STATS = this page (status cleared); SKILLS = the Skills tab (/skills).
  3. SHORTCUTS + PAGES: + Add still lists Stats (right after Skills) and Class (right after Trees) - a merged page is never "locked"; its
     tooltip says "Character > Skills > Stats - part of the Skills tab."; a shortcut / Right-now row / tab click opens a merged page
     through HubBar.openSub (its open Function, else its command; its hide Function is not asked). The Class stand-in tab (0.3.30) is not
     put any more (Class is part of Trees; SkyyClasses 0.1.33 puts its own merged tab).
  No saved data, no command, no setting. ROLLBACK to 0.3.32: with SkyySkills / SkyyTrees / SkyyClasses back to 0.4.44 / 0.3.18 / 0.1.32
  together (deploy_set rule) - the Stats tab comes back.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.32.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.33.py"))
assert P.has('VERSION = "0.3.32"\n') and P.has("MenuOnce") and not P.has("HubHide"), "not the generated SkyyMenu 0.3.32 script"
CMD0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.33: HUBCHAR (notes: tools/menu_0_3_33_patch.py; docs/answered/ui.md 2026-10-16 HUB MERGES NOW): Stats is part of the Skills tab (a
       merged tab - kit skyyui HUB_MERGED: still published for shortcuts / commands, never drawn in a strip); the Stats page shows Skills
       selected + the sub-tabs YOUR STATS / SKILLS; + Add keeps Stats and Class; merged pages open through HubBar.openSub.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.33.py.
''')
P.rep('VERSION = "0.3.32"\n', 'VERSION = "0.3.33"\n')

# ---- the Stats page's sub-tab row (YOUR STATS | SKILLS + the old caption beside them)
P.rep('''ST_W, ST_H = 1114, 966               # 0.3.28: the hub shell (sky padding 24 + the 52 px tab strip) around 0.3.27's body (1066 x 828)
''', '''ST_W, ST_H = 1114, 974               # 0.3.28: the hub shell (sky padding 24 + the 52 px tab strip) around 0.3.27's body (1066 x 828)
                                     # 0.3.33: + 8 (the sub-tab row 32 + 4 replaces the 24 px caption row and grows it)
ST_SUBTABS = ("Your Stats", "Skills")  # 0.3.33: the Skills tab's two sub-views (Skyy 2026-10-16 "Merge now": Stats + Skills = one tab)
ST_SUBTAB_W, ST_SUBROW_B, ST_SUBCAP_L = 130, 4, 12
''')
P.rep('''    sh = SUI.hub_shell("SkyyStatF", ST_W, ST_H, "character", body_id="SkyyStat", row=True)    # 0.3.29: kit 1.6 row 1 (0.3.28: Character > Stats)
    assert (sh.inner_w, sh.inner_h) == (1100 - 2 * SUI.CONTENT_PAD, 900 - SUI.TITLE_H - 2 * SUI.CONTENT_PAD), "0.3.28: the stats body = 0.3.27's"
    ap, body, IW = sh.appends, sh.body, sh.inner_w
    used = []
    used.append(ap.add(body, SUI.label("SkyyStatHead", "", "heading", h=30, size=20, wrap=False)))
    used.append(ap.add(body, SUI.label("SkyyStatSub", "", "caption", h=24, size=ST_SRC_FS)))
''', '''    sh = SUI.hub_shell("SkyyStatF", ST_W, ST_H, "character", body_id="SkyyStat", row=True)    # 0.3.29: kit 1.6 row 1 (0.3.28: Character > Stats)
    assert (sh.inner_w, sh.inner_h) == (1100 - 2 * SUI.CONTENT_PAD, 908 - SUI.TITLE_H - 2 * SUI.CONTENT_PAD), "0.3.33: the stats body = 0.3.27's + 8"
    ap, body, IW = sh.appends, sh.body, sh.inner_w
    used = []
    # 0.3.33: the sub-tab row FIRST under the strip - YOUR STATS (this page, active) | SKILLS (the Skills tab) + the caption beside them
    used.append(ap.add(body, SUI.group("SkyyStatSubRow", "Left", h=SUI.BTN_SMALL_H, anchor={"bottom": ST_SUBROW_B})))
    ap.add("SkyyStatSubRow", SUI.button("SkyyStatSubMe", ST_SUBTABS[0], "primary", "small", w=ST_SUBTAB_W))
    ap.add("SkyyStatSubRow", SUI.button("SkyyStatSubSk", ST_SUBTABS[1], "secondary", "small", w=ST_SUBTAB_W, anchor={"left": SUI.TAB_GAP}))
    _capw = IW - 2 * ST_SUBTAB_W - SUI.TAB_GAP - ST_SUBCAP_L
    assert SUI.text_width(ST_SUB, ST_SRC_FS) <= _capw, "0.3.33: the caption fits beside the sub-tabs"
    ap.add("SkyyStatSubRow", SUI.label("SkyyStatSub", "", "caption", w=_capw, h=SUI.BTN_SMALL_H, size=ST_SRC_FS, anchor={"left": ST_SUBCAP_L}))
    used.append(ap.add(body, SUI.label("SkyyStatHead", "", "heading", h=30, size=20, wrap=False)))
''')
P.rep('''ST_HUB_JAVA = SUI.java_hub_build(ST_SH, "stats", cls="@PKG@.HubBar")
''', '''ST_HUB_JAVA = SUI.java_hub_build(ST_SH, "stats", cls="@PKG@.HubBar")
# 0.3.33: the strip shows the HOST selected (Skills) while Stats is a merged tab (HubBar.selOf; Stats itself when SkyySkills is not loaded)
assert ST_HUB_JAVA.count('"character", "stats", ') == 1
ST_HUB_JAVA = ST_HUB_JAVA.replace('"character", "stats", ', '"character", @PKG@.HubBar.selOf("character", "stats"), ')
''')
P.rep('''assert ST_HUB_JAVA.startswith('@PKG@.HubBar.build2(b, ev, "SkyyStatF", "character", "stats", 1066,') and ST_HUB_JAVA.endswith(", 6, %d);" % (ST_W - 50))''',
      '''assert ST_HUB_JAVA.startswith('@PKG@.HubBar.build2(b, ev, "SkyyStatF", "character", @PKG@.HubBar.selOf("character", "stats"), 1066,') and ST_HUB_JAVA.endswith(", 6, %d);" % (ST_W - 50))''')
P.rep('''  for (int t = 0; t < @PKG@.StatsCalc.TABS.length; t++) ev.addEventBinding(@BT@.Activating, "#SkyyStatTab" + t, @EVD@.of("a", "ttab" + t));
''', '''  for (int t = 0; t < @PKG@.StatsCalc.TABS.length; t++) ev.addEventBinding(@BT@.Activating, "#SkyyStatTab" + t, @EVD@.of("a", "ttab" + t));
  ev.addEventBinding(@BT@.Activating, "#SkyyStatSubMe", @EVD@.of("a", "hub:stats"));    // 0.3.33: YOUR STATS = this page (the "self" click)
  ev.addEventBinding(@BT@.Activating, "#SkyyStatSubSk", @EVD@.of("a", "hub:skills"));   // 0.3.33: SKILLS = the Skills tab (its open / command)
''')

# ---- the kit's MERGED TABS Java in OUR HubBar + the hide Function class
P.rep('''hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True)   # 0.3.29: kit 1.6 (row 1, tab icons, default tab)
MADE.append(hubb)
''', '''hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True, sub=True)   # 0.3.29: kit 1.6; 0.3.33: + merged tabs
MADE.append(hubb)
mhh = SUI.install_hub_hide(pool, PKG + ".HubHide", CtField, CtNewMethod, CtNewConstructor)     # 0.3.33: a merged tab's hide Function
MADE.append(mhh)
''')
P.rep('''         hubb, mhub, mho, mhv, hcch, hcst, hcmk, hctr, hcso, hccr, mal, mvo, mvv, pl)   # 0.3.28: the hub classes; 0.3.29: MenuAlert; 0.3.30: MenuVt*''',
      '''         hubb, mhub, mho, mhv, hcch, hcst, hcmk, hctr, hcso, hccr, mal, mvo, mvv, mhh, pl)   # 0.3.28: the hub classes; 0.3.29: MenuAlert; 0.3.30: MenuVt*; 0.3.33: HubHide''')

# ---- data: Menu's own merged tab (Stats -> its host Skills); no stand-in for a merged contract tab (Class)
P.rep('''F(dat, "public static final String[] HT_LABEL = %s;" % jarr([OWN_LABEL.get(r[1], r[3]) for r in HUB_OWN]))   # 0.3.29: layout -> Edit shortcuts
''', '''F(dat, "public static final String[] HT_LABEL = %s;" % jarr([OWN_LABEL.get(r[1], r[3]) for r in HUB_OWN]))   # 0.3.29: layout -> Edit shortcuts
HT_HOST = [SUI.hub_merged_host(r[0], r[1]) or "" for r in HUB_OWN]   # 0.3.33: "" = a tab of its own; else the tab it is part of
assert [(r[1], x) for r, x in zip(HUB_OWN, HT_HOST) if x] == [("stats", "skills")], "0.3.33: Stats is Menu's only merged tab (part of Skills)"
F(dat, "public static final String[] HT_HOST = %s;" % jarr(HT_HOST))
''')
P.rep('''assert ("smithing", "recipes", 5, "Crafting", "craft") in VT and ("smithing", "gear", 10, "Smithing", "smithing") in VT
''', '''assert ("smithing", "recipes", 5, "Crafting", "craft") in VT and ("smithing", "gear", 10, "Smithing", "smithing") in VT
# 0.3.33: a MERGED contract tab gets no stand-in (Class is part of Trees - SkyyClasses 0.1.33 puts its own merged tab)
VT = [_r for _r in VT if SUI.hub_merged_host(_r[0], _r[1]) is None]
assert ("character", "class") not in [(_r[0], _r[1]) for _r in VT]
''')
P.rep('''    Object vis = null;
    if (@PKG@.MenuData.HT_VIS[j]) vis = new @PKG@.MenuHubVis(@PKG@.MenuData.HT_TAB[j]);
    Object[] e = @PKG@.HubBar.putIcon(@PKG@.MenuData.HT_HUB[j], @PKG@.MenuData.HT_TAB[j], "SkyyMenu", @PKG@.MenuData.HT_LABEL[j], @PKG@.MenuData.HT_ORDER[j],
                                  c.length() == 0 ? null : c, new @PKG@.MenuHubOpen(@PKG@.MenuData.HT_TAB[j]), vis, @PKG@.MenuData.HT_HUB[j] + "_" + @PKG@.MenuData.HT_TAB[j]);   // 0.3.30: + its tab icon
''', '''    Object vis = null;
    if (@PKG@.MenuData.HT_VIS[j]) vis = new @PKG@.MenuHubVis(@PKG@.MenuData.HT_TAB[j]);
    String host = @PKG@.MenuData.HT_HOST[j];
    Object[] e = null;
    if (host.length() > 0) {   // 0.3.33: a MERGED tab (Stats -> part of Skills): published, never drawn in a strip while its host is there
      e = @PKG@.HubBar.putSub(@PKG@.MenuData.HT_HUB[j], @PKG@.MenuData.HT_TAB[j], "SkyyMenu", @PKG@.MenuData.HT_LABEL[j], @PKG@.MenuData.HT_ORDER[j],
                              c.length() == 0 ? null : c, new @PKG@.MenuHubOpen(@PKG@.MenuData.HT_TAB[j]), new @PKG@.HubHide(@PKG@.MenuData.HT_HUB[j], host),
                              @PKG@.MenuData.HT_HUB[j] + "_" + @PKG@.MenuData.HT_TAB[j], host);
    } else {
      e = @PKG@.HubBar.putIcon(@PKG@.MenuData.HT_HUB[j], @PKG@.MenuData.HT_TAB[j], "SkyyMenu", @PKG@.MenuData.HT_LABEL[j], @PKG@.MenuData.HT_ORDER[j],
                               c.length() == 0 ? null : c, new @PKG@.MenuHubOpen(@PKG@.MenuData.HT_TAB[j]), vis, @PKG@.MenuData.HT_HUB[j] + "_" + @PKG@.MenuData.HT_TAB[j]);   // 0.3.30: + its tab icon
    }
''')

# ---- shortcuts: a merged page is never "locked"; its text names the tab it is part of
P.rep('''    Object[] e = (Object[]) o;
    String lab = (e[1] instanceof String) ? @PKG@.HubBar.clean((String) e[1]) : tb;
    if (!@PKG@.HubBar.visible(e, me)) return new String[] { icon, lab, "", "", null, "perm" };
    String cmd = (e[3] instanceof String) ? (String) e[3] : "";
    String body = @PKG@.MenuData.HUB_TITLE[hi] + " > " + lab + " - a page of the " + @PKG@.MenuData.HUB_TITLE[hi] + " hub." + (cmd.length() > 0 ? "\\nCommand: /" + cmd : "");
''', '''    Object[] e = (Object[]) o;
    String lab = (e[1] instanceof String) ? @PKG@.HubBar.clean((String) e[1]) : tb;
    String host = @PKG@.HubBar.hostOf(e);   // 0.3.33: a merged page (Stats in Skills, Class in Trees) is never locked
    if (host == null && !@PKG@.HubBar.visible(e, me)) return new String[] { icon, lab, "", "", null, "perm" };
    String cmd = (e[3] instanceof String) ? (String) e[3] : "";
    String body = @PKG@.MenuData.HUB_TITLE[hi] + " > " + lab + " - a page of the " + @PKG@.MenuData.HUB_TITLE[hi] + " hub." + (cmd.length() > 0 ? "\\nCommand: /" + cmd : "");
    Object ho = host == null ? null : @PKG@.HubBar.get("hub:tab:" + h + ":" + host);
    if (ho instanceof Object[] && ((Object[]) ho).length >= 6) {
      Object[] he = (Object[]) ho;
      String hl = (he[1] instanceof String) ? @PKG@.HubBar.clean((String) he[1]) : host;
      body = @PKG@.MenuData.HUB_TITLE[hi] + " > " + hl + " > " + lab + " - part of the " + hl + " tab." + (cmd.length() > 0 ? "\\nCommand: /" + cmd : "");
    }
''')
P.rep('''      java.util.ArrayList t = @PKG@.HubBar.tabs(@PKG@.MenuData.HUB_ID[i], me);
      for (int j = 0; j < t.size(); j++) tk.add("tab:" + @PKG@.MenuData.HUB_ID[i] + ":" + (String) ((Object[]) t.get(j))[0]);
    }
''', '''      java.util.ArrayList t = @PKG@.HubBar.tabs(@PKG@.MenuData.HUB_ID[i], me);
      for (int j = 0; j < t.size(); j++) tk.add("tab:" + @PKG@.MenuData.HUB_ID[i] + ":" + (String) ((Object[]) t.get(j))[0]);
      // 0.3.33: every MERGED page keeps its own shortcut (Skyy 2026-10-15 "each page should keep its own to open it"), right after its host
      java.util.ArrayList sx = @PKG@.HubBar.subTabs(@PKG@.MenuData.HUB_ID[i], me);
      for (int j = 0; j < sx.size(); j++) {
        Object[] x = (Object[]) sx.get(j);
        String k2 = "tab:" + @PKG@.MenuData.HUB_ID[i] + ":" + (String) x[0];
        if (tk.contains(k2)) continue;
        int at = tk.indexOf("tab:" + @PKG@.MenuData.HUB_ID[i] + ":" + (String) x[2]);
        if (at < 0) tk.add(k2); else tk.add(at + 1, k2);
      }
    }
''')
P.rep('''  String r = @PKG@.HubBar.open(this.playerRef, this.playerRef.getUuid(), h, tb);
  if ("command".equals(r)) { @PKG@.RefreshTask.schedule(this, this.playerRef, 900L); return; }''',
      '''  String r = @PKG@.HubBar.openSub(this.playerRef, this.playerRef.getUuid(), h, tb);   // 0.3.33: a merged page opens too (= open() for the others)
  if ("command".equals(r)) { @PKG@.RefreshTask.schedule(this, this.playerRef, 900L); return; }''')

assert P.s.count("registerCommand(") == CMD0 and P.s.count("registerSystem(") == SYS0, "no command / system added in the script text"
P.finish()
