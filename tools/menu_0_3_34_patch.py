"""Derive SkyyMenu/build_skyymenu_0.3.34.py from the LIVE SkyyMenu 0.3.33 (python tools/menu_0_3_34_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_33_patch.py -> 0.3.33 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.34. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.33 (nothing else changed). The harness SkyyMenu/test_skyymenu_0.3.34.py is its own file.

0.3.34 (2026-10-16) = round smithhub (with SkyyGear 0.3.15): the follow-ups of the hub merges.
  1. SAVED SHORTCUTS OF A MERGED-AWAY TAB (Bank + Vault, Bazaar + Auction House): a Home shortcut 'tab:storage:bank' opens the Vault tab
     (tab:storage:vault) and 'tab:market:auctions' runs /ah - instead of drawing as locked / hidden - while the old tab is gone, hidden or
     part of another tab (MenuPage.redirect; an old 'auctionhouse' tile migrates to tab:market:auctions = the same rule). A server where the
     old tab still stands on its own keeps opening it.
  2. TEXTS: the Storage blurb "... your Vault and the Bank." -> "Storage hub: the Void, Requip and your Vault (the Bank's coins are in it)."; the
     Crafting blurb names its four tabs (Skyy 2026-10-16 "Crafting / Smithing / Anvil (Reforge + Identify inside) / Upgrade (your tools)").
  3. STAND-IN TABS follow the kit's merge data (tools/skyyui.py: Identify is part of the Anvil, the Auction House part of the Market tab - no
     stand-in for them) and its labels now (hub_tab_label: the Anvil, Market).
  No saved data, no command, no setting. ROLLBACK to 0.3.33: safe (the old shortcuts draw as locked again).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import skyyui as SUI

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.33.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.34.py"))
assert P.has('VERSION = "0.3.33"\n') and P.has("HubHide") and not P.has("REDIR_FROM"), "not the generated SkyyMenu 0.3.33 script"
CMD0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
assert SUI.hub_merged_host("smithing", "identify") == "reforge" and SUI.hub_merged_host("market", "auctions") == "bazaar", "the kit's merge data"

P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.34: SMITHHUB (notes: tools/menu_0_3_34_patch.py): saved shortcuts of merged-away tabs open where their page went (tab:storage:bank ->
       the Vault tab, tab:market:auctions -> /ah); the Storage / Crafting blurbs; stand-ins follow the kit's merge data + labels.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.34.py.
''')
P.rep('VERSION = "0.3.33"\n', 'VERSION = "0.3.34"\n')

# ---- 2. the blurbs
P.rep('''             "storage": "Storage hub: the Void, Requip, your Vault and the Bank.",''',
      '''             "storage": "Storage hub: the Void, Requip and your Vault (the Bank's coins are in it).",   # 0.3.34''')
P.rep('''             "smithing": "Crafting hub: the crafter and Smithing - gear, anvil, identify, upgrade.",   # 0.3.31''',
      '''             "smithing": "Crafting hub: the crafter, Smithing, the Anvil (reforge, identify) and Upgrade (your tools).",   # 0.3.34''')

# ---- 3. stand-ins: the kit's labels now (the Anvil, Market, Crafting, Smithing)
P.rep('''VT = [_r for _r in VT if SUI.hub_merged_host(_r[0], _r[1]) is None]
assert ("character", "class") not in [(_r[0], _r[1]) for _r in VT]
''', '''VT = [_r for _r in VT if SUI.hub_merged_host(_r[0], _r[1]) is None]
assert ("character", "class") not in [(_r[0], _r[1]) for _r in VT]
# 0.3.34: Identify (part of the Anvil) and the Auction House (part of Market) get no stand-in; every stand-in wears the kit's label now
assert ("smithing", "identify") not in [(_r[0], _r[1]) for _r in VT] and ("market", "auctions") not in [(_r[0], _r[1]) for _r in VT]
VT = [(_h, _t, _o, SUI.hub_tab_label(_h, _t) or _l, _c) for _h, _t, _o, _l, _c in VT]
assert ("smithing", "reforge", 30, "Anvil", "reforge") in VT and ("smithing", "gear", 10, "Smithing", "smithing") in VT
''')

# ---- 1. the redirect table (data) + MenuPage.redirect
REDIR = [("tab:storage:bank", "tab:storage:vault", "Bank", "the Vault tab - the Bank's coins are part of it now"),
         ("tab:market:auctions", "cmd:ah", "Auction House", "the Auction House - part of the Market tab now")]
P.rep('''F(dat, "public static final String[] HUB_BLURB = %s;" % jarr([HUB_BLURB[_h] for _h in SUI.HUBS]))''',
      '''F(dat, "public static final String[] HUB_BLURB = %s;" % jarr([HUB_BLURB[_h] for _h in SUI.HUBS]))
# 0.3.34: a saved shortcut of a merged-away tab -> where its page went (MenuPage.redirect): key, target ("tab:..." or "cmd:<command>"), name, hover
REDIR = ''' + repr(REDIR) + '''
assert all(_f in ["tab:%s:%s" % (_r[0], _r[1]) for _r in SUI.HUB_TABS] and (_t.startswith("cmd:") or _t in ["tab:%s:%s" % (_r[0], _r[1]) for _r in SUI.HUB_TABS]) for _f, _t, _n, _w in REDIR)
F(dat, "public static final String[] REDIR_FROM = %s;" % jarr([_r[0] for _r in REDIR]))
F(dat, "public static final String[] REDIR_TO = %s;" % jarr([_r[1] for _r in REDIR]))
F(dat, "public static final String[] REDIR_NAME = %s;" % jarr([_r[2] for _r in REDIR]))
F(dat, "public static final String[] REDIR_WHY = %s;" % jarr([_r[3] for _r in REDIR]))''')
# redirect(k, me): null = draw / open k itself (its tab stands on its own for this player); else the target - only while the old tab is gone,
# hidden or merged, and the target exists (a tab key published, or a command on this server)
P.rep('''M(page, r"""
public String[] look(String k, boolean admin) {''', '''M(page, r"""
public static String redirect(String k, java.util.UUID me) {
  if (k == null) return null;
  int i = -1;
  for (int j = 0; j < @PKG@.MenuData.REDIR_FROM.length; j++) { if (@PKG@.MenuData.REDIR_FROM[j].equals(k)) i = j; }
  if (i < 0) return null;
  Object o = @PKG@.HubBar.get("hub:tab:" + k.substring(4));
  if (o instanceof Object[] && ((Object[]) o).length >= 6) {
    Object[] e = (Object[]) o;
    if (@PKG@.HubBar.hostOf(e) == null && @PKG@.HubBar.visible(e, me)) return null;
  }
  String to = @PKG@.MenuData.REDIR_TO[i];
  if (to.startsWith("cmd:")) return @PKG@.MenuUtil.cmd(@PKG@.MenuUtil.firstWord(to.substring(4))) != null ? to : null;
  if (to.startsWith("tab:") && @PKG@.HubBar.get("hub:tab:" + to.substring(4)) instanceof Object[]) return to;
  return null;
}""")
M(page, r"""
public static String redirName(String k) {
  for (int j = 0; j < @PKG@.MenuData.REDIR_FROM.length; j++) { if (@PKG@.MenuData.REDIR_FROM[j].equals(k)) return @PKG@.MenuData.REDIR_NAME[j] + "|" + @PKG@.MenuData.REDIR_WHY[j]; }
  return "|";
}""")
M(page, r"""
public String[] look(String k, boolean admin) {''')
P.rep('''  if (k.startsWith("tab:")) {
    int c = k.indexOf(':', 4);
    if (c < 0) return gone(@PKG@.MenuData.ICON_EMPTY, k);
    String h = k.substring(4, c);
    String tb = k.substring(c + 1);
    int hi = @PKG@.MenuHub.hubIndex(h);
    String icon = tabIcon(h, tb);''', '''  if (k.startsWith("tab:")) {
    String rd = redirect(k, me);          // 0.3.34: a merged-away tab draws as where its page went (never locked)
    if (rd != null) {
      int c0 = k.indexOf(':', 4);
      String nw = redirName(k);
      String ic0 = c0 < 0 ? @PKG@.MenuData.ICON_EMPTY : tabIcon(k.substring(4, c0), k.substring(c0 + 1));
      return new String[] { ic0, nw.substring(0, nw.indexOf('|')), "Opens " + nw.substring(nw.indexOf('|') + 1) + "." + (rd.startsWith("cmd:") ? "\\nCommand: /" + rd.substring(4) : ""), "Click to open!", "sc:" + k, "ok" };
    }
    int c = k.indexOf(':', 4);
    if (c < 0) return gone(@PKG@.MenuData.ICON_EMPTY, k);
    String h = k.substring(4, c);
    String tb = k.substring(c + 1);
    int hi = @PKG@.MenuHub.hubIndex(h);
    String icon = tabIcon(h, tb);''')
P.rep('''  if (k.startsWith("tab:")) {
    int c = k.indexOf(':', 4);
    if (c > 4) { openTab(ref, st, k.substring(4, c), k.substring(c + 1)); return; }
  }''', '''  if (k.startsWith("tab:")) {
    String rd = redirect(k, this.playerRef.getUuid());          // 0.3.34: a merged-away tab opens where its page went
    if (rd != null && rd.startsWith("cmd:")) { runCmd(ref, st, rd.substring(4), true); return; }
    String k2 = rd != null ? rd : k;
    int c = k2.indexOf(':', 4);
    if (c > 4) { openTab(ref, st, k2.substring(4, c), k2.substring(c + 1)); return; }
  }''')

assert P.s.count("registerCommand(") == CMD0 and P.s.count("registerSystem(") == SYS0, "no command / system added in the script text"
P.finish()
