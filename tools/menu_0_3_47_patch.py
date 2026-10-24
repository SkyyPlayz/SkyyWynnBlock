"""Derive SkyyMenu/build_skyymenu_0.3.47.py from the LIVE SkyyMenu 0.3.46 (python tools/menu_0_3_47_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_46_patch.py -> 0.3.46 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.47. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.46 (nothing else changed). Line endings kept. The harness SkyyMenu/test_skyymenu_0.3.47.py is its own file.

0.3.47 (2026-10-23) = UNSPENT TREE POINTS ON RIGHT NOW (LEAN round menu047). Skyy 2026-10-23 (screenshot of SkyWynn Menu > Home, Right now:
  'Quest: Birch Log collection II >', '1 mystery bag to identify >'): "make sure the right now tab shows unspent points in the skill tree too".
  1. READ: SkyyTrees' existing per-player bridge String tree:<uuid> = "Mining:<spent>/<points>,Foraging:...,Class:<spent>/<points>" (TreeFx
     postTree, re-posted every second by TreeTick - plain java.lang, no SkyyTrees change). Free = points - spent; only trees with free > 0.
     No SkyyTrees / no tree:<uuid> / a bad entry = that entry (or every row) left out, never a throw.
  2. ROWS (Home > Right now, after the quest + mystery bag rows, before the mods' home:alert rows; AL_SHOW 8 in all): the TR_SHOW (3) trees
     with the most free points, ties in SkyyTrees' order: "5 unspent points in Mining  >" ("1 unspent point in ..."; the class tree =
     "... in your class tree"). More than TR_SHOW trees = one more row "and N more trees with points  >" (Character > Trees, the tab).
  3. CLICK: a tree row runs /tree <name> AS THE PLAYER (runCmd: installed + permission checked, grid emptied = the one answer packet, the
     command opens SkyyTrees' TreePage on that tree and remembers it as the last tree - the same page the Trees tab opens, which also falls
     back to /tree). The class row = /tree class. /tree missing = the Trees tab (openTab character:trees). Tree names: letters only.
  GAP (UNVERIFIED -> reported): SkyyTrees 0.6.0's tree:<uuid> lists the 9 0.3 trees + Class only, so Beastmastery's free points are not
  readable without a SkyyTrees change (append ",Beastmastery:<spent>/<points>" to postTree) - this build shows it as soon as Trees posts it.
  SAVED DATA: none. No new class / command / system. ROLLBACK to 0.3.46: safe alone (the rows go away).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.46.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.47.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.3.46"\n') and P.has("tools/menu_0_3_46_patch.py") and not P.has("treeRows"), "not the generated SkyyMenu 0.3.46 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.47: Home > Right now shows unspent skill / class tree points (Skyy 2026-10-23): the top 3 trees by free points from SkyyTrees'
       tree:<uuid> bridge + "and N more trees", each row opens that tree (/tree <name>) (notes: tools/menu_0_3_47_patch.py).
  CHECKED: see SkyyMenu/test_skyymenu_0.3.47.py.
''')
P.rep('VERSION = "0.3.46"\n', 'VERSION = "0.3.47"\n')

# ---------- the cap + its texts fit a Right now line
P.rep('''AL_MAX, AL_SHOW = 40, 8                      # an alert line: at most 40 characters (fits its 252 px button at 11 px); at most 8 lines (3 per mod)
''', '''AL_MAX, AL_SHOW = 40, 8                      # an alert line: at most 40 characters (fits its 252 px button at 11 px); at most 8 lines (3 per mod)
TR_SHOW = 3                                  # 0.3.47: Right now lists the 3 trees with the most unspent points (+ "and N more trees")
assert all(len(_t) <= AL_MAX for _t in ("999 unspent points in your class tree", "999 unspent points in Exploration",
                                         "and 99 more trees with points")), "0.3.47: the tree rows fit a Right now line"
assert 2 + TR_SHOW + 1 <= AL_SHOW, "0.3.47: quest + bags + the tree rows leave room in Right now"
''')
P.rep('''               ("AL_MAX", AL_MAX), ("AL_SHOW", AL_SHOW), ("YOU_BAR_W", YOU_BAR_W),
''', '''               ("AL_MAX", AL_MAX), ("AL_SHOW", AL_SHOW), ("YOU_BAR_W", YOU_BAR_W), ("TR_SHOW", TR_SHOW),   # 0.3.47: + TR_SHOW
''')

# ---------- MenuPage: the tree rows (before nowRows), the rows in nowRows, the click
P.rep('''M(page, r"""
public java.util.ArrayList nowRows(@REF@ ref, @ST@ st) {
  java.util.ArrayList out = new java.util.ArrayList();
  String q = questLine(this.playerRef.getUuid());
  if (q != null) out.add(new String[] { q, "world:quests" });
  int nb = unidBags(ref, st);
  if (nb > 0) out.add(new String[] { nb + (nb == 1 ? " mystery bag to identify" : " mystery bags to identify"), "smithing:identify" });
  java.util.ArrayList al = alerts();''', '''# 0.3.47 UNSPENT TREE POINTS (Skyy 2026-10-23 "make sure the right now tab shows unspent points in the skill tree too"): SkyyTrees' bridge
# String tree:<uuid> = "<Tree>:<spent>/<points>,...,Class:<spent>/<points>" (posted every second); free = points - spent > 0. The TR_SHOW
# trees with the most free points (ties keep SkyyTrees' order), then "and N more trees with points" -> Character > Trees. Rows {text, target}:
# target "tree:<name lower case>" (alertClick -> /tree <name>). No / bad bridge value = no rows; a bad entry is skipped; never throws.
M(page, r"""
public static boolean okTree(String n) {
  if (n == null || n.length() == 0 || n.length() > 24) return false;
  for (int i = 0; i < n.length(); i++) { if (!Character.isLetter(n.charAt(i))) return false; }
  return true;
}""")
M(page, r"""
public static java.util.ArrayList treeRows(java.util.UUID u) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (u == null) return out;
  Object o = null;
  try { o = @PKG@.MenuUtil.bridge().get("tree:" + u.toString()); } catch (Throwable t) { o = null; }
  if (!(o instanceof String)) return out;
  java.util.ArrayList nm = new java.util.ArrayList();
  java.util.ArrayList fr = new java.util.ArrayList();
  String[] es = ((String) o).split(",");
  for (int i = 0; i < es.length; i++) {
    String e = es[i].trim();
    int c = e.indexOf(':');
    int sl = c < 0 ? -1 : e.indexOf('/', c + 1);
    if (c <= 0 || sl < 0) continue;
    String n = e.substring(0, c).trim();
    if (!okTree(n)) continue;
    int f = 0;
    try { f = Integer.parseInt(e.substring(sl + 1).trim()) - Integer.parseInt(e.substring(c + 1, sl).trim()); } catch (Throwable t) { f = 0; }
    if (f <= 0) continue;
    int at = fr.size();
    for (int j = 0; j < fr.size(); j++) { if (((Integer) fr.get(j)).intValue() < f) { at = j; break; } }
    nm.add(at, n);
    fr.add(at, Integer.valueOf(f));
  }
  int k = nm.size() < @PKG@.MenuData.TR_SHOW ? nm.size() : @PKG@.MenuData.TR_SHOW;
  for (int i = 0; i < k; i++) {
    String n = (String) nm.get(i);
    int f = ((Integer) fr.get(i)).intValue();
    String where = n.equals("Class") ? "your class tree" : n;
    out.add(new String[] { @PKG@.MenuUtil.clip(f + (f == 1 ? " unspent point in " : " unspent points in ") + where, @PKG@.MenuData.AL_MAX), "tree:" + n.toLowerCase() });
  }
  int more = nm.size() - k;
  if (more > 0) out.add(new String[] { "and " + more + (more == 1 ? " more tree with points" : " more trees with points"), "character:trees" });
  return out;
}""")
M(page, r"""
public java.util.ArrayList nowRows(@REF@ ref, @ST@ st) {
  java.util.ArrayList out = new java.util.ArrayList();
  String q = questLine(this.playerRef.getUuid());
  if (q != null) out.add(new String[] { q, "world:quests" });
  int nb = unidBags(ref, st);
  if (nb > 0) out.add(new String[] { nb + (nb == 1 ? " mystery bag to identify" : " mystery bags to identify"), "smithing:identify" });
  java.util.ArrayList tr = treeRows(this.playerRef.getUuid());   // 0.3.47: unspent tree points
  for (int i = 0; i < tr.size() && out.size() < @PKG@.MenuData.AL_SHOW; i++) out.add(tr.get(i));
  java.util.ArrayList al = alerts();''')
P.rep('''  String t = this.alertT[i] == null ? "" : this.alertT[i];
  if (t.equals("edit")) { openTab(ref, st, "settings", "layout"); return; }
''', '''  String t = this.alertT[i] == null ? "" : this.alertT[i];
  if (t.equals("edit")) { openTab(ref, st, "settings", "layout"); return; }
  if (t.startsWith("tree:")) { openTree(ref, st, t.substring(5)); return; }   // 0.3.47: an unspent-points row
''')
P.rep('''M(page, r"""
public void alertClick(@REF@ ref, @ST@ st, String n) {''', '''# 0.3.47: a tree row of Right now -> /tree <name> as the player (runCmd: installed + permission, the grid emptied, SkyyTrees opens its
# TreePage on that tree = the Trees tab's page); /tree missing or a bad name = the Trees tab itself
M(page, r"""
public void openTree(@REF@ ref, @ST@ st, String n) {
  if (!okTree(n) || @PKG@.MenuUtil.cmd("tree") == null) { openTab(ref, st, "character", "trees"); return; }
  runCmd(ref, st, "tree " + n, true);
}""")
M(page, r"""
public void alertClick(@REF@ ref, @ST@ st, String n) {''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.47 adds no system / command"
_i = P.s.index
assert _i("public static boolean okTree(") < _i("public static java.util.ArrayList treeRows(") < _i("public java.util.ArrayList nowRows(")
assert _i("public void runCmd(") < _i("public void openTab(") < _i("public void openTree(") < _i("public void alertClick(")
P.finish()
