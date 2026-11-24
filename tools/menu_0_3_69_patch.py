"""Derive SkyyMenu/build_skyymenu_0.3.69.py + SkyyMenu/test_skyymenu_0.3.69.py from the SET pin SkyyMenu 0.3.68 (generated - never re-run
its patch). Run:  python tools/menu_0_3_69_patch.py   then   python SkyyMenu/build_skyymenu_0.3.69.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.69.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run). No other mod needed (no new bridge op).

0.3.69 (2026-11-24, round oldmenu1) = THE OLD MENU SWITCH. Skyy's words (docs/answered/ui.md 2026-11-22, LOCKED 'RETIRE THE OLD MENU'): "when
everything is in the new system id like to disable the old menu compleatly, so instead of adding things like the full tree button, just build it
all into the new system and remove the old "Full tree""; 2026-11-23 "looks better. go head and build everything on your list."
  1. SERVER SETUP 'Old SkyWynn menu' (menu.oldMenu, config.properties oldMenu, live). Default ON: the new screen does NOT yet cover every old
     page (the survey in the round report + OLD_LEFT below = the follow-up rounds). OFF = every entry point of the OLD HUB opens the new screen
     instead: the Walk key (Alt) / the double-tap crouch 'Open menu' (HotkeyOpen), /skymenu (+ its aliases), the SkyWynn Menu item
     (MenuPageFactory), the hub commands /character (-> Skills) /storage (-> Inventory) /market (-> Market) /travel (-> World) /social
     (-> Social) /crafting (-> Inventory), /settings (-> Settings), the '< Menu' / Home of every old SkyyMenu page (Stats, Settings, Server
     Setup, Admin page) and, on an old Teleport / Players / Mods page still reached from the new screen, its Back, Home and the other hubs of
     its strip. A tab that cannot open (an older mod) = the Inventory tab; the Inventory too = the old menu (never a dead button).
     Server Setup stays reachable: Settings tab > Open Server Setup (admins) and /modconfig - neither is switched off.
     FIXER (critics): an old Teleport / Players / Mods page's Back / Home / '< Menu' lands on ITS tab (World / Social / Settings - hubName()),
     not the Inventory; the Server Setup hint says some buttons still open old pages.
  2. THE SETTINGS TAB covers the old Settings page completely since 0.3.64 (the same rows, search, pages, crouch choice, Reset all - the old
     page's SetStore writes): its 'Full page' button is gone (the coins keep their place). The other links stay until their follow-up round
     (OLD_LEFT; the harness fails on any link not in that list - a ratchet).
  3. "FULL TREE" LEFTOVERS (Skyy: "remove the old "Full tree""): the inventory's Right now 'unspent tree points' row (tree:<name>) opens that
     skill's page with its inline tree (Class = Combat) instead of the old Trees hub (the hub only for a tree no skill owns); the skill page's
     NO TREE text no longer names the gone 'Full tree' button.
No saved data, no new class / command / system / picture / lang key (MenuHub, MenuCfg, MenuPage members + call sites only).
ROLLBACK to 0.3.68: safe alone (the oldMenu line in config.properties is ignored there; the Settings tab gets its Full page back).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.68.py"), os.path.join(MOD, "build_skyymenu_0.3.69.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.68.py"), os.path.join(MOD, "test_skyymenu_0.3.69.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.68"\n') and P.has("public void fillWork(") and not P.has("OLD_MENU"), "not the generated SkyyMenu 0.3.68 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")


def rep_nth(PP, old, new):
    """the FIRST of several identical anchors (each new text is unique, so finish() undoes them in reverse order)"""
    assert PP.s.count(old) >= 1 and PP.s.count(new) == 0 and new not in old, "rep_nth anchor: " + old[:120]
    PP.s = PP.s.replace(old, new, 1)
    PP.changes.append((new, old))


# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.68: THE SKILL PAGE WORKSHOP''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.69: THE OLD MENU SWITCH: Server Setup 'Old SkyWynn menu' (menu.oldMenu, default ON until every old page is in the new screen); OFF = Alt,
       the crouch, /skymenu, the menu item, /character /storage /market /travel /social /crafting /settings and every old Home / Back open the
       new screen's matching tab; the Settings tab's Full page is gone (it covers the old Settings page) (notes: tools/menu_0_3_69_patch.py).
       CHECKED: SkyyMenu/test_skyymenu_0.3.69.py.
0.3.68: THE SKILL PAGE WORKSHOP''')
P.rep('VERSION = "0.3.68"\n', 'VERSION = "0.3.69"\n')

# ---------- the Server Setup row + the default file line
P.rep('''     "field:MenuCfg.INV_RARITY@config.properties:inventoryRarity"),
''', '''     "field:MenuCfg.INV_RARITY@config.properties:inventoryRarity"),
    # 0.3.69 (oldmenu1; Skyy 11-22 "id like to disable the old menu compleatly"): ON until every old page is in the new screen (round report)
    ("menu.oldMenu", "Old SkyWynn menu", "menu", "bool", "true", "", "", "", "", "live",
     "Off: Alt, /skymenu, the item, hub commands open the new screen (some buttons still open old pages).",
     "field:MenuCfg.OLD_MENU@config.properties:oldMenu"),
''')
P.rep('''    "inventoryRarity=true",
]) + "\\n"''', '''    "inventoryRarity=true",
    "",
    "# oldMenu = the old SkyWynn menu (true or false). false = the Walk key (Alt), the crouch, /skymenu, the menu item, the hub commands",
    "# and /settings open the new screen's matching tab instead (Server Setup stays: Settings tab - Open Server Setup, or /modconfig).",
    "oldMenu=true",
]) + "\\n"''')

# ---------- MenuCfg.OLD_MENU + its load; MenuHub's three seams as STUBS here (their callers compile before the new screens exist) -
# their real bodies are set at the end, once SkillPage / PetsTab / MarketTab / WorldTab / SocialTab / SettingsTab / InvState are compiled
P.rep('''F(mcfg, "public static volatile boolean INV_RARITY = true;")                            # 0.3.66: Server Setup (menu.inventory.rarity)
''', '''F(mcfg, "public static volatile boolean INV_RARITY = true;")                            # 0.3.66: Server Setup (menu.inventory.rarity)
F(mcfg, "public static volatile boolean OLD_MENU = true;")                              # 0.3.69: Server Setup (menu.oldMenu)
# 0.3.69 (oldmenu1): MenuHub.home / newAt / itemPage - stubs now, bodies set before the plugin (OLD_SEAMS below)
M(mhub, "public static boolean home(@REF@ ref, @ST@ st, @PR@ pr) { return false; }")
M(mhub, "public static boolean newAt(@REF@ ref, @ST@ st, @PR@ pr, String hub, String via) { return false; }")
M(mhub, "public static Object itemPage(@PR@ pr) { return null; }")
''')
P.rep('''WALK_COOLDOWN_MS = 400L; INV_REPLACE = true; INV_RARITY = true; return; }''',
      '''WALK_COOLDOWN_MS = 400L; INV_REPLACE = true; INV_RARITY = true; OLD_MENU = true; return; }''')
P.rep('''    INV_RARITY = flag(p, "inventoryRarity", true);                        // 0.3.66
''', '''    INV_RARITY = flag(p, "inventoryRarity", true);                        // 0.3.66
    OLD_MENU = flag(p, "oldMenu", true);                                  // 0.3.69 (missing = ON, every server today)
''')

# ---------- the old pages' '< Menu' / Home (Stats x2, Settings x2, Server Setup, Admin page): the old menu, or the new screen while it is off
for _i, _v in enumerate(("hm", "pm", "hm", "pm", "p", "p")):
    rep_nth(P, '''if (%s != null) %s.getPageManager().openCustomPage(ref, st, new @PKG@.MenuPage(this.playerRef, "main"));''' % (_v, _v),
            '''if (%s != null) @PKG@.MenuHub.home(ref, st, this.playerRef);   // 0.3.69 (oldmenu1 H%d): the old menu, or the new screen while it is off''' % (_v, _i + 1))
assert 'new @PKG@.MenuPage(this.playerRef, "main")' not in P.s, "0.3.69: every old page's Home goes through MenuHub.home"

# ---------- the old Teleport / Players / Mods page (still reached from the new screen): Back, Home and another hub of its strip = the new screen
P.rep('''  if (act.equals("back")) { goBack(); rebuild(); return; }
  if (act.equals("prev")) {''', '''  if (act.equals("back")) { if (!this.view.equals("player") && leaveOld(ref, st, hubName())) return; goBack(); rebuild(); return; }   // 0.3.69
  if (act.equals("prev")) {''')
P.rep('''    if (h.equals("home")) { leaveEdit(); open("main"); rebuild(); return; }
    if (h.equals(myHub)) {''', '''    if (h.equals("home")) { leaveEdit(); if (leaveOld(ref, st, hubName())) return; open("main"); rebuild(); return; }   // 0.3.69
    if (h.equals(myHub)) {''')
P.rep('''  if (a.equals("hub:back")) { leaveEdit(); open("main"); rebuild(); return; }''',
      '''  if (a.equals("hub:back")) { leaveEdit(); if (leaveOld(ref, st, hubName())) return; open("main"); rebuild(); return; }   // 0.3.69''')
P.rep('''M(page, r"""
public void openHub(@REF@ ref, @ST@ st, String h) {''', '''# 0.3.69 (oldmenu1): the old menu switched off = this page's way back to the main tiles opens the new screen's matching tab instead (the grid
# emptied first, the 0.1.3 stuck-tooltip rule of every hand-off); false = the switch is on, or no new screen could open (the old way then)
M(page, r"""
public boolean leaveOld(@REF@ ref, @ST@ st, String hub) {
  if (@PKG@.MenuCfg.OLD_MENU) return false;
  clearGrid();
  if (@PKG@.MenuHub.newAt(ref, st, this.playerRef, hub, "old menu")) return true;
  this.cleared = false;
  return false;
}""")
M(page, r"""
public void openHub(@REF@ ref, @ST@ st, String h) {''')
P.rep('''public void openHub(@REF@ ref, @ST@ st, String h) {
  int hi = @PKG@.MenuHub.hubIndex(h);
  if (hi < 0) { this.status = @PKG@.MenuData.HUB_TXT_FAIL; rebuild(); return; }''', '''public void openHub(@REF@ ref, @ST@ st, String h) {
  int hi = @PKG@.MenuHub.hubIndex(h);
  if (hi < 0) { this.status = @PKG@.MenuData.HUB_TXT_FAIL; rebuild(); return; }
  if (leaveOld(ref, st, h)) return;   // 0.3.69: the old menu off = that hub's new tab''')

# ---------- /settings, the hub commands, /skymenu, the hotkey (Alt + crouch), the menu item
P.rep('''    player.getPageManager().openCustomPage(ref, store, new @PKG@.SettingsPage(pr, -1));''',
      '''    if (!@PKG@.MenuCfg.OLD_MENU && @PKG@.MenuHub.newAt(ref, store, pr, "settings", "/settings")) return;   // 0.3.69: the old menu off = the Settings tab
    player.getPageManager().openCustomPage(ref, store, new @PKG@.SettingsPage(pr, -1));''')
for _h, _c in (("character", "character"), ("storage", "storage"), ("market", "market"), ("world", "travel"), ("social", "social"), ("smithing", "crafting")):
    P.rep('''  @PKG@.MenuHub.run(pr, "%s");\n}"""''' % _h,
          '''  if (!@PKG@.MenuCfg.OLD_MENU && @PKG@.MenuHub.newAt(ref, store, pr, "%s", "/%s")) return;   // 0.3.69: the old menu off = the new tab
  @PKG@.MenuHub.run(pr, "%s");\n}"""''' % (_h, _c, _h))
P.rep('''    player.getPageManager().openCustomPage(ref, store, new @PKG@.MenuPage(pr, "main"));
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("/skymenu failed: " + t);''', '''    if (!@PKG@.MenuHub.home(ref, store, pr)) pr.sendMessage(@MSG@.raw("[Menu] Could not open the menu."));   // 0.3.69: the old menu, or the new screen
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("/skymenu failed: " + t);''')
P.rep('''    pm.openCustomPage(r, st, new @PKG@.MenuPage(this.pr, "main"));
    OPENED = OPENED + 1L;''', '''    if (!@PKG@.MenuHub.home(r, st, this.pr)) return;   // 0.3.69: the old menu, or the new screen while it is off
    OPENED = OPENED + 1L;''')
P.rep('''public Object apply(Object o) {
  return new @PKG@.MenuPage((@PR@) o, "main");
}""")''', '''public Object apply(Object o) {
  Object n = @PKG@.MenuHub.itemPage((@PR@) o);   // 0.3.69: the old menu off = the new screen (null = the old menu)
  return n != null ? n : new @PKG@.MenuPage((@PR@) o, "main");
}""")''')

# ---------- 0.3.69 FIXER (Skyy: "remove the old "Full tree""): the skill page's NO TREE text named the gone Full tree button; the inventory's
# Right now 'unspent tree points' row opened the old Trees hub - now that skill's page (its inline tree; the Class tree = Combat)
P.rep('''tdetail(b, new String[] { "NO TREE", "", "Full tree opens every skill tree you have.", perksLine(), "", "", ab });''',
      '''tdetail(b, new String[] { "NO TREE", "", "This skill has no tree yet - pick another skill on the right.", perksLine(), "", "", ab });   // 0.3.69''')
P.rep('''  if (hub.equals("tree")) { openHub("character", "trees", "your trees"); return; }
  openHub(hub, tab, hub.equals("world") ? "Quests" : "that page");''', '''  if (hub.equals("tree")) {   // 0.3.69 (oldmenu1): that skill's page with its inline tree (Class = Combat), not the old Trees hub
    String sk = null;
    for (int k = 0; k < @PKG@.SkillData.ORDER.length; k++) { if (@PKG@.SkillData.TREE[k].equalsIgnoreCase(tab)) sk = @PKG@.SkillData.ORDER[k]; }
    @PKG@.SkillPage sp = null;
    if (sk != null) {
      try { sp = @PKG@.SkillPage.open(this.pref, this.pst, this.playerRef, sk, "inventory"); } catch (Throwable ex) { sp = null; @PKG@.MenuUtil.warn("inventory: the skill page failed: " + ex); }
    }
    if (sp != null) { this.answered = true; if (!still()) finish("skills"); return; }
    openHub("character", "trees", "your trees");
    return;
  }
  openHub(hub, tab, hub.equals("world") ? "Quests" : "that page");''')

# ---------- the SETTINGS TAB: no Full page (the screen IS the old Settings page since 0.3.64); the coins keep their place
P.rep('''    # ---- the top bar: the same 7 tabs (Settings selected), Full page, coins, the X
    top = SG + "Top"''', '''    # ---- the top bar: the same 7 tabs (Settings selected), coins, the X (0.3.69: no Full page - this screen covers the old Settings page)
    top = SG + "Top"''')
P.rep('''    sp = IV_IW - len(IV_TABS) * (IV_TAB_W + IV_TAB_GAP) - 120 - 8 - cw_ - IV_X - 8
    assert sp >= 0, sp
    ap.append(("#" + top, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + top, G_.glass_button(SG + "Full", "Full page", "secondary", w=120, h=34, size=13, anchor={"right": 8, "top": 7})))
    ap.append(("#" + top, lab(SG + "Coins",''', '''    sp = IV_IW - len(IV_TABS) * (IV_TAB_W + IV_TAB_GAP) - cw_ - IV_X - 8   # 0.3.69: + the 128 px of the Full page button
    assert sp >= 0, sp
    ap.append(("#" + top, "Group { Anchor: (Width: %d); }" % sp))
    ap.append(("#" + top, lab(SG + "Coins",''')
P.rep('''[("#" + SG + "Close", "close"), ("#" + SG + "Full", "full"),
                                                                                  ("#" + SG + "Pp", "pg:-1")''',
      '''[("#" + SG + "Close", "close"),
                                                                                  ("#" + SG + "Pp", "pg:-1")''')
P.rep('''SG_DYN = (["Coins", "Close", "Full", "Cap",''', '''SG_DYN = (["Coins", "Close", "Cap",''')
P.rep('''_sg_ids = set(i_ for _p, mk_ in SG_AP for i_ in SUI._static_ids(mk_))
''', '''_sg_ids = set(i_ for _p, mk_ in SG_AP for i_ in SUI._static_ids(mk_))
assert SG + "Full" not in _sg_ids and not [b_ for b_ in SG_BINDS if b_[1] == "full"], "0.3.69: the settings screen has no Full page (no old Settings page link)"
''')
P.rep('''    if (a.equals("full")) { hub("settings", "settings", "the Settings page"); return; }
''', '''    // 0.3.69 (oldmenu1): no Full page here - this screen covers the old Settings page (a forged 'full' falls through)
''')

# ---------- the seams' real bodies (every new screen + InvState compiled by now) + the leftover old-page links (the ratchet)
P.rep('''# ================= plugin =================
''', '''# ================= 0.3.69 (oldmenu1) OLD_SEAMS: MenuHub.home / newAt / itemPage (stubs since MenuCfg; callers: /skymenu, HotkeyOpen, the hub
# commands, /settings, MenuPageFactory, the old pages' Home / Back). World thread (a command / a page event / the hotkey task / OpenCustomUI).
# newAt(hub): character = the Skills tab (the last skill page), pets / market / world / social / settings = that tab, anything else (storage,
# smithing, "") = the Inventory tab; a tab that cannot open (an older mod: MarketTab / PetsTab need their bridge) = the Inventory tab.
def _old_body(cls, name, src):
    ms_ = [m_ for m_ in cls.getDeclaredMethods() if str(m_.getName()) == name]
    assert len(ms_) == 1, "0.3.69: the stub " + name
    ms_[0].setBody(jv(src))
_old_body(mhub, "newAt", r"""{
  if ($1 == null || $2 == null || $3 == null) return false;
  String h = $4 == null ? "" : $4;
  String via = $5 == null ? "old menu" : $5;
  Object pg = null;
  try {
    if (h.equals("character")) pg = @PKG@.SkillPage.open($1, $2, $3, @PKG@.SkillPage.lastOf($3.getUuid()), via);
    else if (h.equals("pets")) pg = @PKG@.PetsTab.open($1, $2, $3, via);
    else if (h.equals("market")) pg = @PKG@.MarketTab.open($1, $2, $3, via);
    else if (h.equals("world")) pg = @PKG@.WorldTab.open($1, $2, $3, via);
    else if (h.equals("social")) pg = @PKG@.SocialTab.open($1, $2, $3, via);
    else if (h.equals("settings")) pg = @PKG@.SettingsTab.open($1, $2, $3, via);
  } catch (Throwable t) { pg = null; @PKG@.MenuUtil.warn("the new screen (" + h + ") could not open: " + t); }
  if (pg == null) {
    try { pg = @PKG@.InvState.openPage($1, $2, $3, via); } catch (Throwable t) { pg = null; @PKG@.MenuUtil.warn("the inventory screen could not open: " + t); }
  }
  return pg != null;
}""")
_old_body(mhub, "home", r"""{
  if ($1 == null || $2 == null || $3 == null) return false;
  if (!@PKG@.MenuCfg.OLD_MENU && newAt($1, $2, $3, "", "old menu")) return true;
  try {
    @PLA@ p = (@PLA@) $2.getComponent($1, @PLA@.getComponentType());
    if (p == null) return false;
    p.getPageManager().openCustomPage($1, $2, new @PKG@.MenuPage($3, "main"));
    return true;
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not open the SkyWynn Menu: " + t); return false; }
}""")
_old_body(mhub, "itemPage", r"""{
  if (@PKG@.MenuCfg.OLD_MENU || $1 == null) return null;
  return new @PKG@.InvPage($1, "menu item");
}""")
# THE LEFTOVER OLD-PAGE LINKS of the new screen (follow-up rounds, round report): every hub(...) / openHub(...) call left in the new screens'
# classes, as (hub, tab). The harness re-scans the generated script: a link that is not in this list fails it (a ratchet - each follow-up round
# takes rows out as it brings the page in). Settings > Settings is gone (0.3.69). settings:setup = Server Setup (admins) stays on purpose.
OLD_LEFT = sorted(set([
    ("character", "trees"), ("character", "accessories"), ("character", "collections"), ("character", "pets"), ("character", "stats"),
    ("character", "profiles"), ("market", "bazaar"), ("market", "merchants"), ("storage", "bank"), ("storage", "pocket"), ("world", "teleport"),
    ("world", "island"), ("world", "explore"), ("world", "quests"), ("social", "players"), ("social", "party"), ("social", "guild"),
    ("settings", "mods"), ("settings", "setup"), ("smithing", "recipes")]))
print("0.3.69 old menu: Server Setup menu.oldMenu (default ON), %d leftover old-page links in the new screen (follow-up rounds)" % len(OLD_LEFT))

# ================= plugin =================
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.69: no system / command"
_i = P.s.index
assert _i('M(mhub, "public static boolean home(@REF@ ref, @ST@ st, @PR@ pr) { return false; }")') < _i('@PKG@.MenuHub.home(ref, st, this.playerRef);   // 0.3.69 (oldmenu1 H1)') \
    and _i("public boolean leaveOld(@REF@ ref, @ST@ st, String hub) {") < _i('if (leaveOld(ref, st, h)) return;') \
    and _i('_old_body(mhub, "newAt"') > _i("public static @PKG@.SettingsTab open(@REF@ ref, @ST@ st, @PR@ pr, String via) {") \
    and _i('_old_body(mhub, "newAt"') > _i("public static @PKG@.SkillPage open(@REF@ ref, @ST@ st, @PR@ pr, String sk, String via) {"), \
    "0.3.69: stubs before their callers, real bodies after the new screens"
P.finish()


# ======================================================================= the HARNESS (every 0.3.68 check runs again on the 0.3.69 jar, plus OLD1)
def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


EXPECT_69 = '''EXPECT = {   # 0.3.69: the old menu switch (MenuHub seams, MenuCfg, the entry points), the Settings tab without Full page, the version strings
@@EXPECT@@
}
'''
HARNESS_OLD1_STATIC = r'''    # ---- OLD1 (0.3.69; Skyy 11-22 "id like to disable the old menu compleatly"): the static scan of every old-page link left in the new screens
    K.check('("menu.oldMenu", "Old SkyWynn menu"' in g and "oldMenu=true" in g and 'OLD_MENU = flag(p, "oldMenu", true)' in g,
            "OLD1 STATIC the Server Setup row (default ON), the file line, the load (missing = ON)")
    K.check('new @PKG@.MenuPage(this.playerRef, "main")' not in g and g.count('new @PKG@.MenuPage(') == o.count('new @PKG@.MenuPage(') - 7,
            "OLD1 STATIC every old Home / the hotkey / /skymenu go through MenuHub.home (the only 'main' opens left: MenuHub.home + the item fallback + the layout tab)")
    K.check(all(('MenuHub.newAt(ref, store, pr, "%s", "/%s")' % hc_) in g for hc_ in (("character", "character"), ("storage", "storage"), ("market", "market"),
                                                                                       ("world", "travel"), ("social", "social"), ("smithing", "crafting"), ("settings", "settings"))),
            "OLD1 STATIC /character /storage /market /travel /social /crafting /settings open the new tab while the old menu is off")
    i_new_ = g.index("# ================= 0.3.50 THE INVENTORY SCREEN")
    i_end_ = g.index("# ================= 0.3.69 (oldmenu1) OLD_SEAMS")
    links_ = sorted(set(re.findall(r'(?:openHub|hub)\("([a-z]+)", "([a-z]+)"', g[i_new_:i_end_])))
    m_left_ = re.search(r"OLD_LEFT = sorted\(set\(\[(.*?)\]\)\)", g, re.S)
    left_ = sorted(set(re.findall(r'\("([a-z]+)", "([a-z]+)"\)', m_left_.group(1)))) if m_left_ else []
    K.check(links_ == left_ and ("settings", "settings") not in links_ and ("settings", "setup") in links_,
            "OLD1 SCAN every old-page link left in the new screens = the OLD_LEFT follow-up list, nothing else; the old Settings page link is gone; Server Setup kept (%d: %s; extra %s, gone %s)"
            % (len(links_), links_, sorted(set(links_) - set(left_)), sorted(set(left_) - set(links_))))
    K.check("Full tree opens every skill tree you have." not in g and "This skill has no tree yet - pick another skill on the right." in g
            and 'if (hub.equals("tree")) {   // 0.3.69 (oldmenu1)' in g and "(some buttons still open old pages)" in g
            and g.count("leaveOld(ref, st, hubName())") == 3 and 'leaveOld(ref, st, "")' not in g,
            "OLD1 FIX STATIC no 'Full tree' text left; the Right now tree row = the skill page; old pages go back to their own tab; the Setup hint")
    K.check('("#" + SG + "Full", "full")' not in g and 'hub("settings", "settings", "the Settings page")' not in g
            and "0.3.69: the settings screen has no Full page (no old Settings page link)" in g, "OLD1 STATIC the Settings tab has no Full page (markup, binding, handler)")
'''
HARNESS_OLD1_CFG = r'''    r3 = str(Fn.cmdSetConsole("menu.oldMenu", "false"))
    K.check(not bool(CFG.OLD_MENU), "OLD1 CFG Server Setup 'Old SkyWynn menu' OFF sets the switch at once (live): %s" % r3)
    r4 = str(Fn.cmdSetConsole("menu.oldMenu", "true"))
    K.check(bool(CFG.OLD_MENU), "OLD1 CFG ON again: %s" % r4)
'''
HARNESS_OLD1 = r'''    with open(os.path.join(md, "config.properties"), "w", encoding="latin-1") as f_:
        f_.write("giveItem=false\noldMenu=false\n")
    CFG.load()
    K.check(not bool(CFG.OLD_MENU), "OLD1 CFG MenuCfg.load reads oldMenu=false")
    with open(os.path.join(md, "config.properties"), "w", encoding="latin-1") as f_:
        f_.write("giveItem=false\n")
    CFG.load()
    K.check(bool(CFG.OLD_MENU), "OLD1 CFG a file without the key (every server today) = ON (the old menu stays)")
    os.remove(os.path.join(md, "config.properties"))
    CFG.load()
    K.check(bool(CFG.OLD_MENU), "OLD1 CFG no file = ON")
    # ---- OLD1 EXECUTED: every entry point of the old hub, the switch both ways, on a fresh stand-in player (no bridges: the tabs that need
    # one fall back to the Inventory tab)
    PGEc = JClass(PH + "protocol.packets.interface_.Page")
    PO = E.player(uid=UUIDc(0x69, 0x69), name="SkyyOldMenu")
    byU.put(PO.pr.getUuid(), PO.pr)
    for f_ in PO.pr.getClass().getDeclaredFields():   # the hotkey task reads pr.getReference()
        if str(f_.getType().getSimpleName()) == "Ref" and not JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()):
            f_.setAccessible(True)
            f_.set(PO.pr, PO.ref)

    def o_cur():
        c_ = PO.pm.getCustomPage()
        return None if c_ is None else str(c_.getClass().getSimpleName())

    def o_clear():
        E.pump(PO)
        PO.pm.setPage(PO.ref, PO.st, getattr(PGEc, "None_"))
        PO.seen = len(E.sent(PO))   # a SetPage None needs no acknowledgement

    def o_cmd(cls_):
        o_clear()
        m_ = [x_ for x_ in JV(cls_).class_.getDeclaredMethods() if str(x_.getName()) == "execute"][0]
        m_.setAccessible(True)
        f0_ = len(E.sent(PO))
        m_.invoke(Ucls.allocateInstance(JV(cls_).class_), _JA(JClass("java.lang.Object"))([None, PO.st, PO.ref, PO.pr, None]))
        E.pump(PO)
        return o_cur(), len(pages(PO, f0_))

    for on_, what_ in ((True, "ON"), (False, "OFF")):
        CFG.OLD_MENU = on_
        o_clear()
        f0_ = len(E.sent(PO))
        K.check(bool(MH.home(PO.ref, PO.st, PO.pr)) and o_cur() == ("MenuPage" if on_ else "InvPage") and len(pages(PO, f0_)) == 1,
                "OLD1 HOME old menu %s: MenuHub.home = %s, ONE packet (%s)" % (what_, "the old menu" if on_ else "the new screen (Inventory)", o_cur()))
        o_clear()
        n_ = JV("MenuPageFactory")().apply(PO.pr)
        K.check(str(n_.getClass().getSimpleName()) == ("MenuPage" if on_ else "InvPage"), "OLD1 ITEM old menu %s: the menu item opens %s" % (what_, n_.getClass().getSimpleName()))
        for cls_, want_ in (("MenuCmd", "InvPage"), ("HubCharCmd", "SkillPage"), ("HubStorageCmd", "InvPage"), ("HubMarketCmd", "MarketTab|InvPage"),
                            ("HubTravelCmd", "WorldTab"), ("HubSocialCmd", "SocialTab"), ("HubCraftCmd", "InvPage"), ("SettingsCmd", "SettingsTab")):
            cur_, n_ = o_cmd(cls_)
            if on_:
                ok_ = cur_ not in ("InvPage", "SkillPage", "MarketTab", "WorldTab", "SocialTab", "SettingsTab", "PetsTab")
                K.check(ok_ and (cls_ != "MenuCmd" or cur_ == "MenuPage") and (cls_ != "SettingsCmd" or cur_ == "SettingsPage"),
                        "OLD1 CMD old menu ON: %s = the old route as 0.3.68 (%s)" % (cls_, cur_))
            else:
                K.check(cur_ in want_.split("|") and n_ >= 1, "OLD1 CMD old menu OFF: %s = the new screen's tab %s (%s, %d packets)" % (cls_, want_, cur_, n_))
        # the hotkey (Alt / crouch 'Open menu'): the HotkeyOpen task on the world thread
        o_clear()
        MHK_ = JV("MenuHotkey")
        on0_ = bool(MHK_.ON)
        MHK_.ON = True
        try:
            JV("HotkeyOpen")(PO.pr).run()
        finally:
            MHK_.ON = on0_
        E.pump(PO)
        K.check(o_cur() == ("MenuPage" if on_ else "InvPage"), "OLD1 KEY old menu %s: the hotkey opens %s" % (what_, o_cur()))
        # an old page still reached from the new screen (the Teleport page): its Back / Home / another hub of its strip
        for vw_, act_, want_ in (("tp", "back", "WorldTab"), ("tp", "hub:h:home", "WorldTab"), ("tp", "hub:back", "WorldTab"), ("tp", "hub:h:social", "SocialTab"),
                                 ("players", "hub:back", "SocialTab"), ("players", "back", "SocialTab"), ("mods", "hub:back", "SettingsTab")):
            o_clear()
            mp_ = JV("MenuPage")(PO.pr, vw_)
            PO.pm.openCustomPage(PO.ref, PO.st, mp_)
            E.pump(PO)
            f0_ = len(E.sent(PO))
            if act_ == "back":
                mp_.click(PO.ref, PO.st, 0, "back")
            else:
                mp_.hubClick(PO.ref, PO.st, json.dumps({"a": act_}))
            E.pump(PO)
            if on_:
                K.check(o_cur() == "MenuPage" or act_ == "hub:h:social", "OLD1 OLDPAGE old menu ON: %s on the %s page = the old menu as 0.3.68 (%s)" % (act_, vw_, o_cur()))
            else:
                K.check(o_cur() == want_ and len(pages(PO, f0_)) >= 1, "OLD1 OLDPAGE old menu OFF: %s on the %s page = its own new tab (%s, want %s)" % (act_, vw_, o_cur(), want_))
    # FIX (Skyy "remove the old "Full tree""): the Right now 'unspent tree points' row = that skill's page (its inline tree), Class = Combat
    for tgt_, sk_ in (("tree:mining", "Mining"), ("tree:class", "Combat"), ("tree:beastmastery", "Beastmastery")):
        o_clear()
        ipN_ = JV("InvState").openPage(PO.ref, PO.st, PO.pr, "test")
        E.pump(PO)
        ipN_.nowT = _JA(JClass("java.lang.String"))([tgt_])
        ipN_.nowGo(0)
        E.pump(PO)
        cN_ = PO.pm.getCustomPage()
        K.check(o_cur() == "SkillPage" and str(cN_.skill) == sk_ and bool(ipN_.closed),
                "OLD1 NOW the Right now row %s = the %s skill page, not the old Trees hub (%s %s)" % (tgt_, sk_, o_cur(), None if cN_ is None or o_cur() != "SkillPage" else cN_.skill))
    # never a dead button: the old menu OFF but no new screen can open (no player component) = the old way, nothing thrown
    CFG.OLD_MENU = False
    K.check(not bool(MH.newAt(None, PO.st, PO.pr, "market", "t")) and not bool(MH.home(None, PO.st, PO.pr)), "OLD1 SAFE no ref = nothing opened, no throw")
    # Server Setup stays reachable with the old menu off: the Settings tab's Open Server Setup still opens it for an admin
    POA = E.player(uid=E.OP, name="SkyyOldOp")
    byU.put(POA.pr.getUuid(), POA.pr)
    sgA_ = JV("SettingsTab").open(POA.ref, POA.st, POA.pr, "test")
    E.pump(POA)
    sgA_.handleDataEvent(POA.ref, POA.st, json.dumps({"a": "setup"}))
    E.pump(POA)
    curA_ = POA.pm.getCustomPage()
    K.check(curA_ is not None and str(curA_.getClass().getSimpleName()) == "AdminPage", "OLD1 SETUP old menu OFF: the Settings tab's Open Server Setup = Server Setup (%s)"
            % (None if curA_ is None else curA_.getClass().getSimpleName()))
    # the Settings tab's forged 'full' (the button is gone) = nothing opened
    sgB_ = JV("SettingsTab").open(PO.ref, PO.st, PO.pr, "test")
    E.pump(PO)
    f0_ = len(E.sent(PO))
    sgB_.handleDataEvent(PO.ref, PO.st, json.dumps({"a": "full"}))
    E.pump(PO)
    K.check(o_cur() == "SettingsTab" and len(pages(PO, f0_)) <= 1, "OLD1 SAFE a forged Full page on the Settings tab opens no old page (%s)" % o_cur())
    CFG.OLD_MENU = True
'''
T.rep('''"""Harness for SkyyMenu 0.3.68 (the skill page workshop; tools/menu_0_3_68_patch.py, round skl2).''',
      '''"""Harness for SkyyMenu 0.3.69 (the old menu switch; tools/menu_0_3_69_patch.py, round oldmenu1).
GENERATED by tools/menu_0_3_69_patch.py from the 0.3.68 harness (edit the patch, not this file): every 0.3.68 check runs again on the
0.3.69 jar (TAB6: the Settings tab's Full page is gone - only the Mods page link is checked), plus
  OLD1 STATIC  the Server Setup row 'Old SkyWynn menu' (default ON) + file line + load; every old Home / hotkey / /skymenu through MenuHub.home;
               the hub commands + /settings open the new tab while off; the SCAN: every old-page link left in the new screens = OLD_LEFT
               (the follow-up list, a ratchet), the old Settings page link gone, Server Setup kept
       CFG     Server Setup menu.oldMenu through the config kit (live), MenuCfg.load (oldMenu=false / missing key = ON / no file = ON)
       EXECUTED (stand-in player, the switch ON then OFF): MenuHub.home, the menu item (MenuPageFactory), /skymenu /character /storage
               /market /travel /social /crafting /settings (the command classes' own execute), the hotkey task (HotkeyOpen), the old
               Teleport page's Back / Home / < Menu / another hub; ON = the 0.3.68 route, OFF = the new screen's tab, ONE packet; no ref =
               nothing, no throw; Server Setup still opens from the Settings tab; a forged Full page opens nothing
       FIX     old Teleport / Players / Mods page Back / Home / < Menu = their own tab (World / Social / Settings); the Right now tree row =
               the skill page (Class = Combat); no 'Full tree' text; the Server Setup hint
The 0.3.68 harness text follows:
Harness for SkyyMenu 0.3.68 (the skill page workshop; tools/menu_0_3_68_patch.py, round skl2).''')
T.rep('VERSION = "0.3.68"\nJAR', 'VERSION = "0.3.69"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.67.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.68.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.67.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.68.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_68_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_69_patch.py")')
T.rep('"scratch", "skl2", "menu"', '"scratch", "oldmenu1", "menu"')
T.rep('ADDED = []   # 0.3.68: no new class\n', 'ADDED = []   # 0.3.69: no new class\n')
EXPECT_BODY = '''    "MenuHub": ["+m home", "+m itemPage", "+m newAt"],
    "MenuCfg": ["+f OLD_MENU", "~<clinit>", "~m init", "~m load"],
    "MenuPage": ["+m leaveOld", "~m click", "~m hubClick", "~m openHub"],
    "MenuCmd": ["~m execute"], "SettingsCmd": ["~m execute"], "HubCharCmd": ["~m execute"], "HubStorageCmd": ["~m execute"],
    "HubMarketCmd": ["~m execute"], "HubTravelCmd": ["~m execute"], "HubSocialCmd": ["~m execute"], "HubCraftCmd": ["~m execute"],
    "HotkeyOpen": ["~m run"], "MenuPageFactory": ["~m apply"], "StatsPage": ["~m handleDataEvent"], "SettingsPage": ["~m handleDataEvent"],
    "AdminPage": ["~m openMenu"], "OpsPage": ["~<clinit>", "~m openMenu"],
    "SettingsTab": ["~m build", "~m handleDataEvent"], "SettingsTabData": ["~<clinit>"],
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],   # the new row (kit tables)
    "SkyyMenuPlugin": ["~m setup"], "MenuData": ["~<clinit>"],
    "InvPage": ["~m nowGo"], "SkillPage": ["~m fillMap"],   # FIXER: the Right now tree row, the NO TREE text'''
T.rep(cut(T.s, 'EXPECT = {   # 0.3.68:', 'if "--expect-dump" in sys.argv:'), EXPECT_69.replace("@@EXPECT@@", EXPECT_BODY))
T.rep('''    K.check(g.count('VERSION = "0.3.68"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.69"') == 1, "S VERSION")
''' + HARNESS_OLD1_STATIC.rstrip("\n"))
# TAB6: the Settings tab's Full page is gone (0.3.69) - only the Mods page link is a link now
T.rep('''    for a_, what, want_ in (("full", "Full page", "SettingsPage"), ("mods", "Mods page", None)):''',
      '''    for a_, what, want_ in (("mods", "Mods page", None),):   # 0.3.69: no Full page on the Settings tab (OLD1)''')
T.rep('''    K.check(bool(CFG.INV_REPLACE), "CFG: ON again: %s" % r2)
''', '''    K.check(bool(CFG.INV_REPLACE), "CFG: ON again: %s" % r2)
''' + HARNESS_OLD1_CFG)
T.rep('''    K.check(bool(CFG.INV_REPLACE), "CFG: no file = ON")
''', '''    K.check(bool(CFG.INV_REPLACE), "CFG: no file = ON")
''' + HARNESS_OLD1)
if T.dst:
    T.finish()
