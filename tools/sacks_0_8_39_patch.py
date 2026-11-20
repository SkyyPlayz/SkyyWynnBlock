"""Derive SkyySacks/build_skyysacks_0.8.39.py from the SET pin 0.8.38 (the GENERATED build_skyysacks_0.8.38.py; edit THIS file, then
regenerate: python tools/sacks_0_8_39_patch.py; never re-run sacks_0_8_38_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.38 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_39_patch.py   then   python SkyySacks/build_skyysacks_0.8.39.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.39.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.39 (2026-11-20, round inv6) = THE POCKET PANEL'S UPGRADES LINK + AUTO-COMPACT TOGGLE for SkyyMenu 0.3.55's inventory screen (Skyy
  2026-11-20 "Start it now" on 'Start the next inventory round (armour slots, teleports, the rest)?'; the approved inventory-mockup-mining.png
  pocket panel + the 0.8.30 rule "auto compacting ... needs to be an upgrade per bag").
  1. sacks:fn:pocket {UUID, op, category, "", profile token} gets two ops, the SAME gates as the 0.8.38 ops (the player's world thread via
     playerOf, the settled profile key, a token that is not the settled profile's = "-Your profile changed" and nothing changes):
     op "cmpst" -> "=<state>" for that pocket: "x" switched off on this server (Server Setup pd.compact.on), "-" nothing in the bag has an
     Enchanted form, "b" not bought yet, "1" on, "0" paused (reads only - VoidCompact.pairsIn / bought / paused, as the Void page's box);
     op "cmp" = the Void page's OWN Pause / Turn on branch (VoidCompact.toggle: "-Buy Auto-compact for <bag> first" when not bought,
     comp.off.<Category> written by the writer as today) and, when it turned on, VoidCompact.runNow as the page does; "cmp" is refused
     when Server Setup pd.compact.on is OFF (the cmpst gate) and without a profile token (a toggle always names the drawn profile). BUYING stays on the
     Void page (Buy -> Pay / Cancel with the price shown) - no coin is ever taken through the bridge.
  2. sacks:fn:openPocket {UUID, category} -> Boolean (SackFn mode 22, world thread): opens the Void page ON THAT POCKET (new
     SacksPage(pr, category) - the page whose side panel holds the bag's rarity Upgrade box and the Auto-compact Buy box); FALSE = unknown
     pocket / not on this thread / no page (the caller keeps its fallback).
  No saved-data change (comp.off.<Category> is the 0.8.30 line), no config row, no system / command. ROLLBACK to 0.8.38: safe alone (the
  two ops answer "-Unknown pocket action" and openPocket disappears; SkyyMenu 0.3.55 then hides the toggle and opens the Void page).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.38.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.39.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.8.38"\n') and P.has("pocketList") and not P.has("openPocket"), "not the live generated SkyySacks 0.8.38"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.39 (2026-11-20"):].rstrip() + "\n"

P.rep('''  No saved-data change, no config row, no system / command. ROLLBACK to 0.8.37: safe alone (the three keys disappear; SkyyMenu 0.3.53 then
  falls back to the Void button and the Crafting page).
''', '''  No saved-data change, no config row, no system / command. ROLLBACK to 0.8.37: safe alone (the three keys disappear; SkyyMenu 0.3.53 then
  falls back to the Void button and the Crafting page).
''' + NOTE)
P.rep('VERSION = "0.8.38"\n', 'VERSION = "0.8.39"\n')
P.rep('''; pocket tabs + Tannery bridges for the inventory screen (0.8.38)");''',
      '''; pocket tabs + Tannery bridges for the inventory screen (0.8.38); pocket Upgrades link + Auto-compact toggle (0.8.39)");''')

# ---- SackBridge: the compact state + toggle inside pocketAct (after the token + item checks), openPocket after pocketAct
P.rep('''  if (want != null && want.length() > 0 && !want.equals(tok(k))) return "-Your profile changed - the pocket now shows it; pick the item again";
  if (id == null || id.length() == 0) return "-Pick an item in the grid first";
  String r = null;
''', '''  if (want != null && want.length() > 0 && !want.equals(tok(k))) return "-Your profile changed - the pocket now shows it; pick the item again";
  if (id == null || id.length() == 0) return "-Pick an item in the grid first";
  if ("cmpst".equals(op) || "cmp".equals(op)) {   // 0.8.39: the pocket's Auto-compact (id = the category) - the Void page's own box rules
    int ci = @PKG@.SackDefs.catIndex(id);
    if (ci < 0) return "-No such pocket";
    if ("cmpst".equals(op)) {
      if (!@PKG@.SackCfg.CMP_ON) return "=x";
      if (@PKG@.VoidCompact.pairsIn(ci, (java.util.Set) null) <= 0) return "=-";
      if (!@PKG@.VoidCompact.bought(k, ci)) return "=b";
      return @PKG@.VoidCompact.paused(k, ci) ? "=0" : "=1";
    }
    if (!@PKG@.SackCfg.CMP_ON) return "-Auto-compact is switched off on this server";   // the same Server Setup gate as cmpst
    if (want == null || want.length() == 0) return "-Your profile changed - the pocket now shows it; try again";   // a toggle needs the drawn profile's token
    String rc = @PKG@.VoidCompact.toggle(u, k, ci);
    if (rc != null && rc.startsWith("+")) {
      long cm = @PKG@.VoidCompact.runNow(u, k);
      if (cm > 0L) rc = rc + " - " + @PKG@.SacksPage.num(cm) + " Enchanted made now";
    }
    return rc;
  }
  String r = null;
''')
P.rep('''sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object fishCall(int mode, Object o) {''', '''# 0.8.39: the pocket panel's Upgrades link - the Void page on THAT pocket (its rarity Upgrade box + the Auto-compact Buy box), world thread
sbr.addMethod(CtNewMethod.make(jt(r"""
public static Boolean openPocket(java.util.UUID u, String cat) {
  int ci = @PKG@.SackDefs.catIndex(cat);
  if (ci < 0) return Boolean.FALSE;
  @PLA@ p = playerOf(u);
  if (p == null) return Boolean.FALSE;
  try {
    @PR@ pr = @UNI@.get().getPlayer(u);
    if (pr == null || !pr.isValid()) return Boolean.FALSE;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return Boolean.FALSE;
    @ST@ st = r.getStore();
    if (st == null || p.getPageManager() == null) return Boolean.FALSE;
    p.getPageManager().openCustomPage(r, st, new @PKG@.SacksPage(pr, @PKG@.SackDefs.CATS[ci]));
    return Boolean.TRUE;
  } catch (Throwable t) {
    @PKG@.SackPool.warn("sacks:fn:openPocket could not open the Void page: " + t);
    return Boolean.FALSE;
  }
}"""), sbr))
sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object fishCall(int mode, Object o) {''')
# ---- SackFn: mode 22 next to 20 / 21
P.rep('''    if (this.mode == 20 || this.mode == 21) {   // 0.8.38 sacks:fn:pocketList {UUID, cat} / sacks:fn:pocket {UUID, op, id, amount}''',
      '''    if (this.mode == 22) {   // 0.8.39 sacks:fn:openPocket {UUID, cat} -> Boolean
      if (!(o instanceof Object[])) return Boolean.FALSE;
      Object[] a22 = (Object[]) o;
      if (a22.length < 2 || !(a22[0] instanceof java.util.UUID) || !(a22[1] instanceof String)) return Boolean.FALSE;
      return @PKG@.SackBridge.openPocket((java.util.UUID) a22[0], (String) a22[1]);
    }
    if (this.mode == 20 || this.mode == 21) {   // 0.8.38 sacks:fn:pocketList {UUID, cat} / sacks:fn:pocket {UUID, op, id, amount}''')
P.rep('''|| this.mode == 20 || this.mode == 21) ? null : Long.valueOf(this.mode == 0 ? -1L : 0L);   // 0.8.38: the pocket modes answer null on a failure''',
      '''|| this.mode == 20 || this.mode == 21) ? null : (this.mode == 22 ? (Object) Boolean.FALSE : (Object) Long.valueOf(this.mode == 0 ? -1L : 0L));   // 0.8.38: the pocket modes answer null on a failure; 0.8.39: openPocket FALSE''')
P.rep('''  sbr0.put("sacks:fn:openTannery", new {PKG}.CraftHubOpen("Tannery"));   // 0.8.38: the inventory's Tanning tab (UUID -> Boolean; world thread)
''', '''  sbr0.put("sacks:fn:openTannery", new {PKG}.CraftHubOpen("Tannery"));   // 0.8.38: the inventory's Tanning tab (UUID -> Boolean; world thread)
  sbr0.put("sacks:fn:openPocket", new {PKG}.SackFn(22));   // 0.8.39: the pocket panel's Upgrades link (the Void page on that pocket)
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.39 adds no system / command"
_i = P.s.index
assert _i("public static long runNow(") < _i("public static String pocketAct(") and _i("public static String toggle(java.util.UUID u") < _i("public static String pocketAct("), "0.8.39: VoidCompact before pocketAct"
assert _i("public SacksPage({PR} pr, String cat)") < _i("public static Boolean openPocket(") < _i("public static Object fishCall(") < _i("if (this.mode == 22)"), "0.8.39: methods before callers"
P.finish()
