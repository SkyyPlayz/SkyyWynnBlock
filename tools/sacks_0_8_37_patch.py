"""Derive SkyySacks/build_skyysacks_0.8.37.py from the SET pin 0.8.36 (the GENERATED build_skyysacks_0.8.36.py; edit THIS file, then
regenerate: python tools/sacks_0_8_37_patch.py; never re-run sacks_0_8_36_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.36 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_37_patch.py   then   python SkyySacks/build_skyysacks_0.8.37.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.37.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.37 (2026-11-08) = INGOTS FIRST ON THE FURNACE TAB (tag sk837; Skyy: "filter ingots to the top, in order of tier").
  CraftPage.buildProc, Furnace bench only: a recipe whose PRIMARY OUTPUT is an ingot (Ingredient_Bar_* or an Enchanted metal, the 18 Skyy_Ench_<metal> rows of tools/skyyench.py whose base is a bar,
  alloys included) gets RecipeCmp.furnaceKey / furnaceName instead of sortKey / sortName; every other row keeps today's key, so it keeps today's order below the ingots. RecipeCmp.compare is untouched.
  furnaceKey = the bar's tier (tierKey of the plain bar, tools/tier_tags.py) minus 1,000,000,000: always below every sortKey (those are never negative), so no other row can get between.
  furnaceName = the plain bar's sortName + " 0" (plain) or " 1" (Enchanted): each Enchanted ingot sits directly after its plain ingot. A bar with no tier (Silver, Gold, Prisma - Skyy left them untagged) comes after every
  tiered ingot and before the non-ingots, so the list starts at T1 Copper.
  A locked (greyed) alloy keeps its place: the key is decided before and without the lock. A recipe with no primary output is never an ingot, whatever its recipe id says.
  The Tannery, Crafting, Gear, Farming, Campfire, Collections and the search all still use sortKey / sortName.
  No saved-data change, no config row, no system / command, no bridge key. ROLLBACK to 0.8.36: safe alone (the Furnace list goes back to tier then name; nothing is stored).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.36.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.37.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.8.36"\n') and P.has("VOID-SELL") and not P.has("furnaceKey"), "not the live generated SkyySacks 0.8.36"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.37 (2026-11-08)"):].rstrip() + "\n"

P.rep('''so a Bazaar round built on this pin must follow the move (its Mining tab -> Smithing).
"""
''', '''so a Bazaar round built on this pin must follow the move (its Mining tab -> Smithing).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.36"\n', 'VERSION = "0.8.37"\n')
P.rep('''; Enchanted metals in Smithing, Pocket Sell, real names (0.8.36)");''', '''; Enchanted metals in Smithing, Pocket Sell, real names (0.8.36); Furnace ingots first (0.8.37)");''')

# ---- RecipeCmp: the Furnace keys (compare itself is not touched)
P.rep('''# 0.8.11 (PROJECT-RULES 4): tier, then name - no craftable-first any more (rows that cannot be made are greyed out; "Craftable only" hides them)
''', '''# 0.8.37 (Skyy "filter ingots to the top, in order of tier"): the Furnace tab's keys; the Enchanted metals come from tools/skyyench.py at build time (METAL_ENCH, 0.8.36)
ING_BASE = [_t[2] for _t in _HOME_TABLE if _t[2].startswith("Ingredient_Bar_")]
assert len(ING_BASE) == len(METAL_ENCH) == 18 and ING_BASE[METAL_ENCH.index("Skyy_Ench_Lead")] == "Ingredient_Bar_Lead_SkyWynn" and ING_BASE[METAL_ENCH.index("Skyy_Ench_Electrum")] == "Ingredient_Bar_Electrum_SkyWynn", (METAL_ENCH, ING_BASE)
assert all((_e in TT.ROWS) == (_b in TT.ROWS) and (_e not in TT.ROWS or TT.tier(_e) == TT.tier(_b)) for _e, _b in zip(METAL_ENCH, ING_BASE)), "0.8.37: an Enchanted metal no longer has its bar's tier in tools/tier_tags.py - it would leave its plain ingot"
rcmp.addField(CtField.make("public static final String[] ING_ENCH = %s;" % _jsa(METAL_ENCH), rcmp))
rcmp.addField(CtField.make("public static final String[] ING_BASE = %s;" % _jsa(ING_BASE), rcmp))
# the plain bar of an ingot id (itself for a bar, its base for an Enchanted metal), null = not an ingot
rcmp.addMethod(CtNewMethod.make("""
public static String ingotOf(String id) {
  if (id == null) return null;
  if (id.startsWith("Ingredient_Bar_")) return id;
  if (!id.startsWith("Skyy_Ench_")) return null;
  for (int i = 0; i < ING_ENCH.length; i++) if (ING_ENCH[i].equals(id)) return ING_BASE[i];
  return null;
}""", rcmp))
# an ingot: its bar's tier, below every sortKey (never negative); no tier (Silver, Gold, Prisma) = after the tiered ingots. Anything else: sortKey as ever
rcmp.addMethod(CtNewMethod.make("""
public static int furnaceKey(String id) {
  String b = ingotOf(id);
  if (b == null) return sortKey(id);
  int t = tierKey(b);
  return (t > 0 ? t : 999) - 1000000000;
}""", rcmp))
# an ingot: its bar's name, the plain one first and its Enchanted form right after. Anything else: sortName as ever
rcmp.addMethod(CtNewMethod.make("""
public static String furnaceName(String id) {
  String b = ingotOf(id);
  if (b == null) return sortName(id);
  return sortName(b) + (b.equals(id) ? " 0" : " 1");
}""", rcmp))
# 0.8.11 (PROJECT-RULES 4): tier, then name - no craftable-first any more (rows that cannot be made are greyed out; "Craftable only" hides them)
''')

# ---- CraftPage.buildProc: the Furnace only (the same line in the instant tabs' build is not touched)
P.rep('''  java.util.ArrayList ent = new java.util.ArrayList();
  for (int i = 0; i < raw.size(); i++) {
    @CRR@ r0 = (@CRR@) raw.get(i);
    int l0 = limit(r0, mats);
    if (@PKG@.ProcBench.alloyNeed(r0) > ctier) l0 = 0;   // 0.8.20: a locked alloy is never "can make"
''', '''  java.util.ArrayList ent = new java.util.ArrayList();
  boolean furn = "Furnace".equalsIgnoreCase(bench);   // 0.8.37: ingots first, on this bench only
  for (int i = 0; i < raw.size(); i++) {
    @CRR@ r0 = (@CRR@) raw.get(i);
    int l0 = limit(r0, mats);
    if (@PKG@.ProcBench.alloyNeed(r0) > ctier) l0 = 0;   // 0.8.20: a locked alloy is never "can make"
''')
P.rep('''    if (!alloyOk(r0, aKnown, aColl)) l0 = 0;   // 0.8.24: nor an Enchanted alloy smelt the collections have not unlocked
    if (only && l0 <= 0) continue;
    @MQ@ o0 = r0.getPrimaryOutput();
    String id0 = o0 == null ? String.valueOf(r0.getId()) : o0.getItemId();
    ent.add(new Object[] { r0, Integer.valueOf(l0), Integer.valueOf(@PKG@.RecipeCmp.sortKey(id0)), @PKG@.RecipeCmp.sortName(id0) });   // 0.8.11: tier, then name
''', '''    if (!alloyOk(r0, aKnown, aColl)) l0 = 0;   // 0.8.24: nor an Enchanted alloy smelt the collections have not unlocked
    if (only && l0 <= 0) continue;
    @MQ@ o0 = r0.getPrimaryOutput();
    String id0 = o0 == null ? String.valueOf(r0.getId()) : o0.getItemId();
    boolean ing0 = furn && o0 != null;   // 0.8.37: a recipe with no output keeps its old place, whatever its recipe id says
    ent.add(new Object[] { r0, Integer.valueOf(l0), Integer.valueOf(ing0 ? @PKG@.RecipeCmp.furnaceKey(id0) : @PKG@.RecipeCmp.sortKey(id0)), ing0 ? @PKG@.RecipeCmp.furnaceName(id0) : @PKG@.RecipeCmp.sortName(id0) });   // 0.8.11: tier, then name
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.37 adds no system / command"
_i = P.s.index
assert _i("public static int sortKey(") < _i("public static String sortName(") < _i("public static String ingotOf(") < _i("public static int furnaceKey(") < _i("public static String furnaceName(") < _i("public void buildProc("), "0.8.37: methods before callers"
P.finish()
