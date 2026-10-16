"""Derive SkyySacks/build_skyysacks_0.8.7.py from the SET pin 0.8.6 (the GENERATED build_skyysacks_0.8.6.py; edit THIS file, then
regenerate: python tools/sacks_0_8_7_patch.py; never re-run sacks_0_8_6_patch.py on top of it). Every anchor is asserted; at the end every
change is undone on a copy and compared with 0.8.6 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_7_patch.py   then   python SkyySacks/build_skyysacks_0.8.7.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.7.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.7 = /craft ARTIFACTS TAB (lean round sacks087, 2026-10-15; Skyy, on a /craft screenshot whose Crafting list mixed benches, crates,
torches and 'Skyy Talisman Regeneration Common': "and id add an artifacts tab").
1. The /craft tab row reads < Back to the Void | Crafting | Artifacts | Smithing | Farming | ... | Collections (same tab buttons, same
   wrap: 6 tabs on the first row, the rest on a second row - the row stays inside the 1000-wide page).
2. ARTIFACTS (tab id A:art) lists every accessory recipe of the merged /craft set (Fieldcraft + every equipped non-timed bench, the set
   Crafting / Smithing / Farming / search already use): an output id starting Skyy_Talisman_ (every booster line + the Lantern line) or
   Skyy_Acc (Skyy_Accessory_Bag, the Skyy_Accessory_<Bench>_T<n> bench accessories, the Omni), or any id SkyyAccessories publishes in
   acc:defs (its own list: every rarity of every line + the Lantern; read through the bridge, cached per published value). Those recipes
   leave Crafting (and Farming / Smithing - a Farmingbench talisman is an artifact too); nothing else moves.
3. Everything else is the shared A: tab code, unchanged: the search row (search still covers the whole merged set, its texts now say
   "N found in Crafting, Artifacts, Smithing and Farming"), Craftable only, Craft / x10 / All, the unlock rules (KnowSync.allowed: the
   Lantern recipes are KnowledgeRequired - SkyyAccessories' Tree Sap gate; bags; vanilla knowledge) at view AND click time, and the 0.8.6
   CraftRecipeEvent$Pre veto before anything is paid. The Collections tab and the sacks:fn:craftList bridge are unchanged.
4. No saved-data change, no new command / system / setting / bridge key. ROLLBACK to 0.8.6: safe (the accessory recipes show in Crafting
   again).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.6.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.7.py"))
assert P.has('VERSION = "0.8.6"\n') and P.has("PickLate") and not P.has("A:art"), "not the live generated SkyySacks 0.8.6"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.7 = /craft ARTIFACTS"):].rstrip() + "\n"

# ---------- header + version
P.rep('''4. No saved-data change, no new command / system / setting / bridge key. ROLLBACK to 0.8.5: safe (that first log stays on the ground and
   /craft stops firing the event).
"""
''', '''4. No saved-data change, no new command / system / setting / bridge key. ROLLBACK to 0.8.5: safe (that first log stays on the ground and
   /craft stops firing the event).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.6"\n', 'VERSION = "0.8.7"\n')

# ---------- the artifact test (after tabGroup, before buildTabs)
P.rep('''  if (id != null && (id.startsWith("Tool_") || id.startsWith("Weapon_") || id.startsWith("Armor_"))) return 1;
  return 0;
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public java.util.ArrayList buildTabs(''', '''  if (id != null && (id.startsWith("Tool_") || id.startsWith("Weapon_") || id.startsWith("Armor_"))) return 1;
  return 0;
}}""", cpg))
# 0.8.7 ARTIFACTS tab (Skyy "and id add an artifacts tab"): the item ids SkyyAccessories lists in acc:defs ("<admin>:<family>:<rarity>:<id>:
# <display>:<AP>:<source>" records, comma separated; every rarity of every line + the Lantern), parsed once per published value (the
# bridge value object - SkyyAccessories puts it once in setup()); empty without SkyyAccessories / an unreadable value.
cpg.addField(CtField.make("public static Object ACCDEFSRC;", cpg))
cpg.addField(CtField.make("public static java.util.HashSet ACCDEFS = new java.util.HashSet();", cpg))
cpg.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized java.util.HashSet accDefIds() {
  Object v = null;
  try { v = @PKG@.SackPool.bridge().get("acc:defs"); } catch (Throwable t) { v = null; }
  if (v == ACCDEFSRC) return ACCDEFS;
  java.util.HashSet s = new java.util.HashSet();
  if (v instanceof String) {
    String[] recs = ((String) v).split(",");
    for (int i = 0; i < recs.length; i++) {
      String[] f = recs[i].split(":");
      if (f.length > 3 && f[3].trim().length() > 0) s.add(f[3].trim());
    }
  }
  ACCDEFS = s;
  ACCDEFSRC = v;
  return s;
}\'\'\'), cpg))
# an accessory item id: Skyy_Talisman_* (booster lines + the Lantern line), Skyy_Acc* (the Accessory Bag, Skyy_Accessory_<Bench>_T<n>, the
# Omni), or listed in SkyyAccessories' acc:defs
cpg.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean artifactId(String id) {
  if (id == null) return false;
  if (id.startsWith("Skyy_Talisman_") || id.startsWith("Skyy_Acc")) return true;
  return accDefIds().contains(id);
}\'\'\'), cpg))
# the recipe's primary output is an accessory -> the Artifacts tab (group 3) instead of tabGroup's Crafting / Smithing / Farming
cpg.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean artifact(@CRR@ r) {
  if (r == null) return false;
  @MQ@ po = r.getPrimaryOutput();
  return po != null && artifactId(po.getItemId());
}\'\'\'), cpg))
cpg.addMethod(CtNewMethod.make(f"""
public java.util.ArrayList buildTabs(''')

# ---------- the tab (after Crafting)
P.rep('''  t.add(new String[] {{ "A:craft", "Crafting" }});
  t.add(new String[] {{ "A:smith", "Smithing" }});''', '''  t.add(new String[] {{ "A:craft", "Crafting" }});
  t.add(new String[] {{ "A:art", "Artifacts" }});   // 0.8.7: every accessory recipe (artifact())
  t.add(new String[] {{ "A:smith", "Smithing" }});''')

# ---------- recipesFor: group 3 = Artifacts; artifacts leave the other three
P.rep('''  else if (tabId.equals("A:farm")) grp = 2;
  if (grp >= 0) {{''', '''  else if (tabId.equals("A:farm")) grp = 2;
  else if (tabId.equals("A:art")) grp = 3;   // 0.8.7
  if (grp >= 0) {{''')
P.rep('''    if (grp >= 0 && tabGroup(rc) != grp) continue;''', '''    // 0.8.7: an accessory recipe shows on the Artifacts tab only (never Crafting / Smithing / Farming)
    if (grp >= 0 && (artifact(rc) ? 3 : tabGroup(rc)) != grp) continue;''')

# ---------- the search texts (the search itself already covers the whole merged set, Artifacts included)
P.rep('''  // 0.7.3: a search shows Crafting + Smithing + Farming results together, so no tab is highlighted while it is active''',
      '''  // 0.7.3: a search shows Crafting + Smithing + Farming results together (0.8.7: + Artifacts), so no tab is highlighted while it is active''')
P.rep('''("Nothing matches " + this.query + " in Crafting, Smithing or Farming.")''',
      '''("Nothing matches " + this.query + " in Crafting, Artifacts, Smithing or Farming.")''')
P.rep('''("  " + this.rows.size() + " found in Crafting, Smithing and Farming") : "  searches Crafting, Smithing and Farming");''',
      '''("  " + this.rows.size() + " found in Crafting, Artifacts, Smithing and Farming") : "  searches Crafting, Artifacts, Smithing and Farming");''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "no system / command added"
_i = P.s.index
assert _i("public static synchronized java.util.HashSet accDefIds()") < _i("public static boolean artifactId(") < _i("public static boolean artifact(@CRR@ r)") \
    < _i("public java.util.ArrayList buildTabs(") < _i("public java.util.ArrayList recipesFor(")
P.finish()
