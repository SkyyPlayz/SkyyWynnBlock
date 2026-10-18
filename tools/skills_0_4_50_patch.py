"""Derive SkyySkills/build_skyyskills_0.4.50.py from the GENERATED SkyySkills 0.4.49 (build_skyyskills_0.4.49.py = the tools/deploy_set.py SET
pin; 0.4.49 came from 0.4.48 by tools/skills_0_4_49_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with
0.4.49 (nothing else changed); 0.4.49 stays untouched, its line endings are kept (tools/soundpass_gen.Patch).
Run:  python tools/skills_0_4_50_patch.py   then   python SkyySkills/build_skyyskills_0.4.50.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.50.py
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

NOTE = '''0.4.50 (2026-10-17) = round "fortune" builder F2 (research/Metals-Tools-Fortune-Spec.md 2.1 - 2.4 + section 5 row F2), the SkyySkills half.
  Skyy 2026-10-17 (docs/answered/gear.md): "Yes, all defaults (Recommended)" to the spec's questions - Fortune +10 % a level, no total cap,
  "Smelting Fortune on alloys too but only on ore you mined yourself (blocks the Bazaar loop)", Rich Veins stays a separate small roll.
  1. MINING FORTUNE = TOOL + TREE, NO CAP (Perks.fortune, Mining row only): the "trees" source's dd.mining (SkyyTrees MFortune) leaves the
     capped part (level perk + accessories + pets + armor, perk.doubleDropMax) and joins the UNCAPPED tool part ("gear"): t = min(perk +
     others, doubleDropMax) + gear + trees. Example: tool +150 % + tree +50 % = 2.0 -> always 3 drops. New row perk.treeFortuneUncapped
     (default true; off = 0.4.49's maths). An admin's perk.doubleDropMax BELOW 1 and perk.fortuneMax above 0 still cap the total (unchanged
     rule). Foraging / Farming unchanged. Rich Veins (MVeins, an EXTRA node of SkyyTrees) is not a dd.mining source - untouched.
  2. MINED-ORE BUDGET (spec 2.3 Bazaar loop): per profile, per raw ore item id (Ore_*): +1 per raw ore a Mining-XP break gave (the block's
     drops re-rolled once by Perks.breakDrops, only for blocks whose id starts Ore_) and + every Ore_* of the Mining Fortune extras. Only
     blocks that can double count (natural blocks: the placed-block tracker is on and the block was not placed; creative never pays).
     Each ore id is capped at smelt.fortune.budgetMax (new row, default 100000; 0 = nothing remembered). Saved in the profile's player file
     players/<pkey>.properties as ore.<id>=<n> lines (same atomic save as the XP). BRIDGE skill:fn:oreBudget (any thread):
       apply(Object[]{ UUID player, String oreId, Integer n }) -> Integer
       n > 0: TAKE up to n from the ACTIVE profile's budget of oreId, returns how many were granted (0..n; the caller smelts the rest 1:1)
       n = 0: returns the balance, takes nothing          n < 0: gives -n back (a cancelled queued unit), returns how many were added
       bad arguments / not an Ore_ id / SkyySkills not started = 0. Never throws, never calls another mod. (SkyySacks F3 calls it at queue time.)
  3. PLACED FURNACE SWITCH smelt.fortune.placed (new row, default OFF - same as the Furnace Charm: the placed furnace has no per-player job
     and take-out can be repeated). On: taking bars out of a placed Furnace's output (the Smithing XP path, needs smithing.vanillaFurnace)
     rolls Smelting Fortune F = tree:fn:bonus("Smithing.SSmelt") per bar - only for a 1 ore -> 1 bar Furnace recipe and only for units the
     mined-ore budget grants (always mined-only here); extras = floor(F) + (r < F mod 1) per unit (perk.fortuneGuard), one stack, storage first.
  4. FEED BRIDGE skill:fn:fortunefeed (any thread): apply(Object[]{ UUID player, String itemId, Number extra }) -> Boolean: TRUE = queued for
     the player's 0.4.42 Fortune indicator (message kind "fortune": feed card "Smelting Fortune! Iron Bar  x3" or the chat line "Smelting
     Fortune! +3 Iron Bar", grouped 1.5 s like Fortune!; the player's msg.fortune / skills.doubleDrop switches apply), FALSE = hidden / bad args.
  CONFIG: 3 new rows (perk.treeFortuneUncapped, smelt.fortune.placed, smelt.fortune.budgetMax); a fresh xp.properties lists them; an existing
  file without them uses the code defaults (no line changes - no migration needed: no old default is rewritten). SAVED DATA: new ore.* keys
  in the player file only (no existing key changes; a profile starts with budget 0 - ore mined before 0.4.50 smelts 1:1).
  5. FELLED TREES IN ZONE WORLDS (Skyy's bug 2026-10-17, The Fens: "its dropping items again"; the 21:23 server log: skill:fn:felledBy null,
     0 refused / 0 at feet - the logs past the search cap were never claimed, so SkyySacks' auto-pickup could not deliver them): the felled-tree
     search limits fell.radius 8 -> 16, fell.maxLogs 256 -> 1024, fell.maxLeaves 384 -> 2048, fell.maxReads 8000 -> 40000 (the clamps
     already allowed these; vanilla zone trees have 300 - 700+ logs). MIGRATION Fl50Mig (PROJECT-RULES 4; Pd44Mig's reviewed machinery):
     ONCE on an EXISTING xp.properties (setup, right after Zo49Mig, before SkillCfg.load): each of the four keys whose LAST entry is a
     one-line entry holding exactly the old default -> the new default (value text only); an admin's own value kept (INFO); no line =
     nothing (the new code default applies); the marker at the end; config-history copy first; one config-changes.log line per change (Undo
     in Server Setup -> Changes); bytes + line endings kept. Server Setup: fell.radius + fell.maxLogs leave the advanced list (shown always).
     Cost: measured by test_skyyskills_0.4.50.py phase FL (ms per fell on the biggest vanilla tree prefabs).
  ROLLBACK to 0.4.49: harmless for saves - 0.4.49 ignores ore.* and drops them on its next save of that profile (the budget is lost, nothing
  else); the tree Mining Fortune goes back under the 100 % cap; skill:fn:oreBudget is gone (SkyySacks 0.8.21 must then give no Fortune bars).
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.49.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.50.py"))
assert P.has('VERSION = "0.4.49"') and P.has("Zo49Mig") and not P.has("OreBud"), "not the generated SkyySkills 0.4.49 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

# ================================================================================================ docstring + version
P.rep('''"""SkyySkills 0.4.49 - build script (derived from the generated 0.4.48 by tools/skills_0_4_49_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.50 - build script (derived from the generated 0.4.49 by tools/skills_0_4_50_patch.py - edit the patch, not this file;
''' + NOTE + '''  CHECKED: SkyySkills/test_skyyskills_0.4.50.py.
0.4.49 was derived from the generated 0.4.48 by tools/skills_0_4_49_patch.py;
''')
P.rep('VERSION = "0.4.49"', 'VERSION = "0.4.50"')

# ================================================================================================ the default file + Server Setup rows
P.rep('''PERK_L.append("perk.fortuneGuard=100")
''', '''PERK_L.append("perk.fortuneGuard=100")
PERK_L.append("# treeFortuneUncapped (0.4.50): true = the skill tree's Mining Fortune adds with the tool's Fortune, no cap (100 percent = one sure")
PERK_L.append("# extra drop). false = the tree part stays under doubleDropMax with the level perk (the 0.4.49 maths).")
PERK_L.append("perk.treeFortuneUncapped=true")
''')
P.rep('''SMITH_L.append("smithing.smeltDefault=1")
''', '''SMITH_L.append("smithing.smeltDefault=1")
SMITH_L.append("# Smelting Fortune (0.4.50; the roll itself is SkyySacks' /craft Furnace tab). placed = also when you take bars out of a placed")
SMITH_L.append("# Furnace (off: that furnace has no per-player job). budgetMax = per ore kind and profile, the most mined ore remembered")
SMITH_L.append("# for Smelting Fortune (only ore you mined yourself gets Fortune bars; 0 = none remembered).")
SMITH_L.append("smelt.fortune.placed=false")
SMITH_L.append("smelt.fortune.budgetMax=100000")
''')
P.rep('''    ("perk.fortuneGuard", "Fortune extra drops guard", "perks", "int", "100", "1", "10000", "", "", "live,adv",
     "The most extra drops one break or harvest can give (a safety stop for uncapped Fortune).", "reload"),
''', '''    ("perk.fortuneGuard", "Fortune extra drops guard", "perks", "int", "100", "1", "10000", "", "", "live,adv",
     "The most extra drops one break or harvest can give (a safety stop for uncapped Fortune).", "reload"),
    # 0.4.50 (Metals-Tools-Fortune-Spec 2.1): the tree's Mining Fortune joins the tool's, no cap
    ("perk.treeFortuneUncapped", "Tree Mining Fortune uncapped", "perks", "bool", "true", "", "", "", "", "live",
     "On: the tree's Mining Fortune adds with the tool's, no cap. Off: capped with the level perk.", "reload"),
''')
P.rep('''    ("smithing.smeltDefault", "Other smelted items", "crafting", "int", "1", "0", "1000000000", "", "", "live",
     "Smithing XP per item for every other Furnace output (0 = none).", "reload"),
''', '''    ("smithing.smeltDefault", "Other smelted items", "crafting", "int", "1", "0", "1000000000", "", "", "live",
     "Smithing XP per item for every other Furnace output (0 = none).", "reload"),
    # 0.4.50 (Metals-Tools-Fortune-Spec 2.2 / 2.3): Smelting Fortune at placed furnaces + the mined-ore budget
    ("smelt.fortune.placed", "Smelting Fortune at placed furnaces", "crafting", "bool", "false", "", "", "", "", "live",
     "On: bars taken out of a placed Furnace roll Smelting Fortune too (only ore you mined).", "reload"),
    ("smelt.fortune.budgetMax", "Most mined ore remembered", "crafting", "int", "100000", "0", "100000000", "", "", "live,adv",
     "Per ore kind and profile: mined ore that can still get Smelting Fortune bars.", "reload"),
''')
P.rep('''assert len(CFG_ROWS) == 272, ("0.4.48: + perk.fortuneGuard;''', '''assert len(CFG_ROWS) == 275, ("0.4.50: + perk.treeFortuneUncapped, smelt.fortune.placed, smelt.fortune.budgetMax; 0.4.48: + perk.fortuneGuard;''')
P.rep('''assert DEFAULTS.count(ZO_MARK_ID) == 1 and''', '''assert _dp.get("perk.treeFortuneUncapped") == "true" and _dp.get("smelt.fortune.placed") == "false" and _dp.get("smelt.fortune.budgetMax") == "100000"   # 0.4.50
assert DEFAULTS.count(ZO_MARK_ID) == 1 and''')

# ================================================================================================ PerkCfg / SmithCfg fields + reads
P.rep('''for _decl in ("boolean ENABLED = true", "double DD_MAX = 1.0", "double FORT_MAX = 0.0", "int GUARD = 100", "boolean DD_MSG = true",''',
      '''for _decl in ("boolean ENABLED = true", "double DD_MAX = 1.0", "double FORT_MAX = 0.0", "int GUARD = 100", "boolean TREE_UNCAP = true", "boolean DD_MSG = true",''')
P.rep('''  GUARD = gd < 1L ? 1 : (gd > 10000L ? 10000 : (int) gd);
''', '''  GUARD = gd < 1L ? 1 : (gd > 10000L ? 10000 : (int) gd);
  TREE_UNCAP = {PKG}.SkillCfg.bool(p, "perk.treeFortuneUncapped", true);   // 0.4.50: the tree's Mining Fortune joins the uncapped tool part
''')
P.rep('''for _decl in ("boolean ENABLED = true", "boolean VANILLA = true", "double ORE_FACTOR = 1.0", "long DEFAULT = 1L",''',
      '''for _decl in ("boolean ENABLED = true", "boolean VANILLA = true", "double ORE_FACTOR = 1.0", "long DEFAULT = 1L", "boolean PLACED = false", "long BUDGET_MAX = 100000L",''')
P.rep('''  long d = {PKG}.SkillCfg.lng(p, "smithing.smeltDefault", 1L);
  DEFAULT = d < 0L ? 0L : d;
''', '''  long d = {PKG}.SkillCfg.lng(p, "smithing.smeltDefault", 1L);
  DEFAULT = d < 0L ? 0L : d;
  PLACED = {PKG}.SkillCfg.bool(p, "smelt.fortune.placed", false);   // 0.4.50: Smelting Fortune at placed furnaces (default off)
  long bm = {PKG}.SkillCfg.lng(p, "smelt.fortune.budgetMax", 100000L);   // 0.4.50: the mined-ore budget cap per ore id and profile
  BUDGET_MAX = bm < 0L ? 0L : (bm > 100000000L ? 100000000L : bm);
''')

# ================================================================================================ SmithCfg.oreOf: the ore of a 1 ore -> 1 bar Furnace recipe
P.rep('''smc.addMethod(CtNewMethod.make("""
public static long forOutput(String id) {''', '''# 0.4.50: the raw ore of a strict 1 ore -> 1 bar Furnace recipe of this output (the placed-furnace Smelting Fortune); anything else null
smc.addMethod(CtNewMethod.make(J14(r"""
public static String oreOf(String id) {
  if (id == null || !id.startsWith("Ingredient_Bar_")) return null;
  try {
    java.util.List l = @CRPL@.getBenchRecipes(@BTP@.Processing, "Furnace");
    for (int i = 0; l != null && i < l.size(); i++) {
      Object o = l.get(i);
      if (!(o instanceof @CRR@)) continue;
      @CRR@ r = (@CRR@) o;
      @MQ@ po = r.getPrimaryOutput();
      if (po == null || !id.equals(po.getItemId()) || po.getQuantity() != 1) continue;
      @MQ@[] in = r.getInput();
      if (in == null || in.length != 1 || in[0] == null || in[0].getQuantity() != 1) continue;
      String ore = in[0].getItemId();
      if (ore != null && ore.startsWith("Ore_")) return ore;   // SkillStore.oreId is compiled later; OreBud.ask checks it
    }
  } catch (Throwable t) { @PKG@.SkillCfg.warn("smithing: could not look up the Furnace recipe of " + id + ": " + t); }
  return null;
}"""), smc))
smc.addMethod(CtNewMethod.make("""
public static long forOutput(String id) {''')

# ================================================================================================ SkillStore: the ore budget in the player file
P.rep('''sto.addField(CtField.make("public static volatile java.util.Map BRIDGE;", sto))''',
      '''sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap ORE = new java.util.concurrent.ConcurrentHashMap();", sto))   # 0.4.50: pkey -> HashMap ore id -> long[1] (the mined-ore budget)
sto.addField(CtField.make("public static volatile java.util.Map BRIDGE;", sto))''')
P.rep('''# player file (players/<pkey>.properties, 0.3.2) -> {long[2*N] data, String name, Boolean quiet}.''', '''# 0.4.50 MINED-ORE BUDGET (Metals-Tools-Fortune-Spec 2.3): per profile key, per raw ore item id. Mutated only under the SkillStore lock
# (snap() reads it under the same lock); saved as ore.<id>=<n> in the player file. The caller loads the profile first (dataK), so an
# entry is never created before install() put the file's copy.
sto.addMethod(CtNewMethod.make(J14(r"""
public static boolean oreId(String id) {
  if (id == null || id.length() < 5 || id.length() > 96 || !id.startsWith("Ore_")) return false;
  for (int i = 0; i < id.length(); i++) {
    char c = id.charAt(i);
    if (!(c >= 'A' && c <= 'Z' || c >= 'a' && c <= 'z' || c >= '0' && c <= '9' || c == '_')) return false;
  }
  return true;
}"""), sto))
sto.addMethod(CtNewMethod.make(J14(r"""
public static synchronized java.util.HashMap oreMap(String k) {
  Object o = ORE.get(k);
  if (o instanceof java.util.HashMap) return (java.util.HashMap) o;
  java.util.HashMap m = new java.util.HashMap();
  ORE.put(k, m);
  return m;
}"""), sto))
# + n, at most max per ore id (256 ids per profile); the amount actually added
sto.addMethod(CtNewMethod.make(J14(r"""
public static synchronized long oreAdd(String k, String id, long n, long max) {
  if (k == null || !oreId(id) || n <= 0L) return 0L;
  java.util.HashMap m = oreMap(k);
  long[] c = (long[]) m.get(id);
  long have = c == null ? 0L : c[0];
  long room = (max < 0L ? 0L : max) - have;
  if (room <= 0L) return 0L;
  long add = n < room ? n : room;
  if (c == null) {
    if (m.size() >= 256) return 0L;
    c = new long[1];
    m.put(id, c);
  }
  c[0] = have + add;
  DIRTY.put(k, Boolean.TRUE);
  return add;
}"""), sto))
# - up to n; the amount actually taken
sto.addMethod(CtNewMethod.make(J14(r"""
public static synchronized long oreTake(String k, String id, long n) {
  if (k == null || !oreId(id) || n <= 0L) return 0L;
  java.util.HashMap m = oreMap(k);
  long[] c = (long[]) m.get(id);
  if (c == null || c[0] <= 0L) return 0L;
  long t = n < c[0] ? n : c[0];
  c[0] = c[0] - t;
  if (c[0] <= 0L) m.remove(id);
  DIRTY.put(k, Boolean.TRUE);
  return t;
}"""), sto))
sto.addMethod(CtNewMethod.make(J14(r"""
public static synchronized long oreGet(String k, String id) {
  if (k == null || !oreId(id)) return 0L;
  Object o = ORE.get(k);
  if (!(o instanceof java.util.HashMap)) return 0L;
  long[] c = (long[]) ((java.util.HashMap) o).get(id);
  return c == null ? 0L : c[0];
}"""), sto))
# player file (players/<pkey>.properties, 0.3.2) -> {long[2*N] data, String name, Boolean quiet}.''')
P.rep('''  String rbtx = null;   // 0.4.36: rb.lastTx
''', '''  String rbtx = null;   // 0.4.36: rb.lastTx
  java.util.HashMap ore = new java.util.HashMap();   // 0.4.50: ore.<id>=<n> (the mined-ore budget)
''')
P.rep('''      if (rt != null && rt.trim().length() > 0) rbtx = rt.trim();
    }}
''', '''      if (rt != null && rt.trim().length() > 0) rbtx = rt.trim();
      java.util.Iterator oi = p.stringPropertyNames().iterator();
      while (oi.hasNext()) {{
        String pk = (String) oi.next();
        if (!pk.startsWith("ore.") || !oreId(pk.substring(4)) || ore.size() >= 256) continue;
        try {{ long ov = Long.parseLong(p.getProperty(pk).trim()); if (ov > 0L) ore.put(pk.substring(4), new long[] {{ ov }}); }} catch (Throwable t) {{ }}
      }}
    }}
''')
P.rep('''  return new Object[] {{ d, nm, Boolean.valueOf(quiet), rbtx }};''', '''  return new Object[] {{ d, nm, Boolean.valueOf(quiet), rbtx, ore }};''')
P.rep('''  if (got.length > 3 && got[3] instanceof String) RBTX.put(k, got[3]);   // 0.4.36
''', '''  if (got.length > 3 && got[3] instanceof String) RBTX.put(k, got[3]);   // 0.4.36
  if (got.length > 4 && got[4] instanceof java.util.HashMap) ORE.put(k, got[4]);   // 0.4.50: the mined-ore budget
  else ORE.put(k, new java.util.HashMap());
''')
P.rep('''    p.setProperty({PKG}.SkillDefs.NAMES[i] + ".paid", String.valueOf(d[{PKG}.SkillDefs.N + i]));
  }}
  return p;
}}""", sto))''', '''    p.setProperty({PKG}.SkillDefs.NAMES[i] + ".paid", String.valueOf(d[{PKG}.SkillDefs.N + i]));
  }}
  Object om = ORE.get(k);   // 0.4.50: the mined-ore budget, in the SAME write as the XP
  if (om instanceof java.util.HashMap) {{
    java.util.Iterator oi = ((java.util.HashMap) om).keySet().iterator();
    while (oi.hasNext()) {{
      String id = (String) oi.next();
      long[] c = (long[]) ((java.util.HashMap) om).get(id);
      if (c != null && c[0] > 0L) p.setProperty("ore." + id, String.valueOf(c[0]));
    }}
  }}
  return p;
}}""", sto))''')

# ================================================================================================ SkillBonus.ddExcept2 (two sources left out)
P.rep('''# SkyyTrees publishes tree:fn:level in its setup and removes it in its shutdown: its presence = the trees are installed''',
      '''# 0.4.50: dd.<skill> of every source but a and b, clamped 0..1 like ddExcept (the capped part of Mining Fortune without tool + tree)
sbn.addMethod(CtNewMethod.make(J14(r"""
public static double ddExcept2(java.util.UUID u, int row, String a, String b) {
  if (u == null || row < 0 || row > @PKG@.SkillDefs.FARMING || !@PKG@.BridgeCfg.BONUS) return 0.0;
  java.util.Map m = sources(u);
  if (m == null) return 0.0;
  String k = "dd." + key(row);
  double s = 0.0;
  try {
    java.util.Iterator it = m.keySet().iterator();
    while (it.hasNext()) {
      Object sk = it.next();
      if (a != null && a.equals(sk) || b != null && b.equals(sk)) continue;
      Object v = m.get(sk);
      if (!(v instanceof java.util.Map)) continue;
      Object n = ((java.util.Map) v).get(k);
      if (!(n instanceof Number)) continue;
      double d = ((Number) n).doubleValue();
      if (Double.isNaN(d) || Double.isInfinite(d)) continue;
      s = s + d;
    }
  } catch (Throwable t) { return 0.0; }
  if (s <= 0.0) return 0.0;
  return s > 1.0 ? 1.0 : s;
}"""), sbn))
# SkyyTrees publishes tree:fn:level in its setup and removes it in its shutdown: its presence = the trees are installed''')

# ================================================================================================ Perks.fortune: the tree part uncapped (Mining)
P.rep('''public static double fortune(java.util.UUID u, int row, int lvl, String fam) {
  if (row < 0 || row > @PKG@.SkillDefs.FARMING) return 0.0;
  double base = chance(row, lvl) + @PKG@.SkillBonus.ddExcept(u, row, "gear");
  if (base > @PKG@.PerkCfg.DD_MAX) base = @PKG@.PerkCfg.DD_MAX;
  if (!(base > 0.0)) base = 0.0;
  double g = @PKG@.SkillBonus.ddOf(u, row, "gear");
  if (g > 0.0 && !onlyHit(@PKG@.SkillBonus.onlyOf(u, row, "gear"), fam)) g = 0.0;
  double t = base + g;''', '''public static double fortune(java.util.UUID u, int row, int lvl, String fam) {
  if (row < 0 || row > @PKG@.SkillDefs.FARMING) return 0.0;
  boolean tu = row == @PKG@.SkillDefs.MINING && @PKG@.PerkCfg.TREE_UNCAP;   // 0.4.50: Mining Fortune = tool + tree, added, no cap
  double base = chance(row, lvl) + (tu ? @PKG@.SkillBonus.ddExcept2(u, row, "gear", "trees") : @PKG@.SkillBonus.ddExcept(u, row, "gear"));
  if (base > @PKG@.PerkCfg.DD_MAX) base = @PKG@.PerkCfg.DD_MAX;
  if (!(base > 0.0)) base = 0.0;
  double g = @PKG@.SkillBonus.ddOf(u, row, "gear");
  if (g > 0.0 && !onlyHit(@PKG@.SkillBonus.onlyOf(u, row, "gear"), fam)) g = 0.0;
  double tr = tu ? @PKG@.SkillBonus.ddOf(u, row, "trees") : 0.0;   // the tree node counts on every Mining block (as before)
  double t = base + g + tr;''')

# ================================================================================================ OreBud (before breakDouble, its caller)
P.rep('''fm48 = pool.makeClass(PKG + ".Fm48Mig")        # 0.4.48: the one-time perk.fortuneMax 2.0 -> 0 (no cap) update of an existing xp.properties
''', '''fm48 = pool.makeClass(PKG + ".Fm48Mig")        # 0.4.48: the one-time perk.fortuneMax 2.0 -> 0 (no cap) update of an existing xp.properties
ob50 = pool.makeClass(PKG + ".OreBud")         # 0.4.50: the mined-ore budget (counting, the skill:fn:oreBudget answer, the placed-furnace roll)
obfn50 = pool.makeClass(PKG + ".OreBudgetFn")  # 0.4.50: bridge skill:fn:oreBudget
smf50 = pool.makeClass(PKG + ".SmFeed")        # 0.4.50: the Smelting Fortune line (grouped like Fortune!)
smft50 = pool.makeClass(PKG + ".SmFeedTask")   # 0.4.50: its one-shot send task
sffn50 = pool.makeClass(PKG + ".FortuneFeedFn")  # 0.4.50: bridge skill:fn:fortunefeed
sftk50 = pool.makeClass(PKG + ".SmeltFortTask")  # 0.4.50: the placed-furnace Smelting Fortune (world thread)
''')
OB_JAVA = '''# ================= 0.4.50 OreBud: the mined-ore budget (Metals-Tools-Fortune-Spec 2.3, the Bazaar loop guard) =================
for _d in ("public static volatile boolean WARNED = false;",
           "public static final java.util.concurrent.atomic.AtomicLong MINED = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong EXTRA = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong ASKS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong TAKEN = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong BACK = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong PLACED = new java.util.concurrent.atomic.AtomicLong();"):
    ob50.addField(CtField.make(_d, ob50))
ob50.addMethod(CtNewMethod.make(J14(r"""
public static void warn(String what, Throwable t) {
  if (WARNED) return;
  WARNED = true;
  @PKG@.SkillCfg.warn("mined-ore budget: " + what + " failed (logged once): " + t);
}"""), ob50))
# the Ore_* stacks of a drop list into the ACTIVE profile's budget (each id capped at smelt.fortune.budgetMax); the amount added
ob50.addMethod(CtNewMethod.make(J14(r"""
public static long addList(java.util.UUID u, java.util.List drops) {
  if (u == null || drops == null || drops.isEmpty()) return 0L;
  long got = 0L;
  try {
    String k = @PKG@.SkillStore.pkey(u);
    @PKG@.SkillStore.dataK(k, u);
    long max = @PKG@.SmithCfg.BUDGET_MAX;
    for (int i = 0; i < drops.size(); i++) {
      Object o = drops.get(i);
      if (!(o instanceof @IS@)) continue;
      @IS@ is = (@IS@) o;
      if (is.isEmpty() || is.getQuantity() <= 0 || !@PKG@.SkillStore.oreId(is.getItemId())) continue;
      got = got + @PKG@.SkillStore.oreAdd(k, is.getItemId(), (long) is.getQuantity(), max);
    }
  } catch (Throwable t) { warn("counting mined ore", t); }
  return got;
}"""), ob50))
# BreakTask (world thread): a natural Mining-XP block whose id starts Ore_ - its own drops re-rolled once (Perks.breakDrops: the drop list
# of an ore block is fixed, e.g. Ore_Iron_Stone = 1 Ore_Iron + 1 cobble); tool-dependent drops = nothing counted
ob50.addMethod(CtNewMethod.make(J14(r"""
public static long mined(java.util.UUID u, @BTY@ bt) {
  if (u == null || bt == null) return 0L;
  try {
    String bid = bt.getId();
    if (bid == null || !bid.startsWith("Ore_")) return 0L;
    long n = addList(u, @PKG@.Perks.breakDrops(bt));
    if (n > 0L) MINED.addAndGet(n);
    return n;
  } catch (Throwable t) { warn("an ore break", t); return 0L; }
}"""), ob50))
# Perks.breakDouble: the Mining Fortune extras (only natural blocks reach it) count too
ob50.addMethod(CtNewMethod.make(J14(r"""
public static long extras(java.util.UUID u, int row, java.util.List drops) {
  if (row != @PKG@.SkillDefs.MINING) return 0L;
  long n = addList(u, drops);
  if (n > 0L) EXTRA.addAndGet(n);
  return n;
}"""), ob50))
# skill:fn:oreBudget's answer: n > 0 take up to n (granted), 0 = the balance, < 0 give -n back (added, capped)
ob50.addMethod(CtNewMethod.make(J14(r"""
public static long ask(java.util.UUID u, String id, long n) {
  if (u == null || !@PKG@.SkillStore.oreId(id) || @PKG@.SkillStore.DIR == null) return 0L;
  ASKS.incrementAndGet();
  String k = @PKG@.SkillStore.pkey(u);
  @PKG@.SkillStore.dataK(k, u);
  if (n > 0L) {
    long t = @PKG@.SkillStore.oreTake(k, id, n);
    TAKEN.addAndGet(t);
    return t;
  }
  if (n == 0L) return @PKG@.SkillStore.oreGet(k, id);
  long b = @PKG@.SkillStore.oreAdd(k, id, -n, @PKG@.SmithCfg.BUDGET_MAX);
  BACK.addAndGet(b);
  return b;
}"""), ob50))
# the Smelting Fortune of the player's skill tree (SkyyTrees tree:fn:bonus "Smithing.SSmelt", a fraction: 1.0 = one sure extra bar); 0 without
ob50.addMethod(CtNewMethod.make(J14(r"""
public static double smeltF(java.util.UUID u) {
  try {
    Object f = @PKG@.SkillStore.bridge().get("tree:fn:bonus");
    if (!(f instanceof java.util.function.Function)) return 0.0;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, "Smithing.SSmelt" });
    if (!(r instanceof Number)) return 0.0;
    double d = ((Number) r).doubleValue();
    return (Double.isNaN(d) || Double.isInfinite(d) || d <= 0.0) ? 0.0 : d;
  } catch (Throwable t) { return 0.0; }
}"""), ob50))
# PURE: the extra bars of `units` budget-granted units at Fortune f, draws from rnd (per unit: whole part sure + one more when r < the rest,
# Perks.extras = perk.fortuneGuard per unit); at most 1000000
ob50.addMethod(CtNewMethod.make(J14(r"""
public static long extraBars(double f, long units, java.util.Random rnd) {
  if (!(f > 0.0) || units <= 0L || rnd == null) return 0L;
  long x = 0L;
  long n = units > 100000L ? 100000L : units;
  for (long i = 0L; i < n; i++) {
    x = x + (long) @PKG@.Perks.extras(f, rnd.nextDouble());
    if (x >= 1000000L) return 1000000L;
  }
  return x;
}"""), ob50))
# the placed-furnace roll (smelt.fortune.placed): got bars of id taken out; only a 1 ore -> 1 bar recipe, only budget-granted units
ob50.addMethod(CtNewMethod.make(J14(r"""
public static long placedExtras(java.util.UUID u, String id, int got) {
  if (!@PKG@.SmithCfg.PLACED || u == null || got <= 0) return 0L;
  double f = smeltF(u);
  if (!(f > 0.0)) return 0L;
  String ore = @PKG@.SmithCfg.oreOf(id);
  if (ore == null) return 0L;
  long g = ask(u, ore, (long) got);
  long x = extraBars(f, g, java.util.concurrent.ThreadLocalRandom.current());
  if (x > 0L) PLACED.addAndGet(x);
  return x;
}"""), ob50))
# bridge skill:fn:oreBudget  apply(Object[]{ UUID, String oreId, Integer n }) -> Integer (see the 0.4.50 notes; never throws, 0 on bad args)
obfn50.addInterface(pool.get("java.util.function.Function"))
obfn50.addConstructor(CtNewConstructor.make("public OreBudgetFn() { }", obfn50))
obfn50.addMethod(CtNewMethod.make(J14(r"""
public Object apply(Object arg) {
  try {
    if (!(arg instanceof Object[])) return Integer.valueOf(0);
    Object[] a = (Object[]) arg;
    if (a.length < 3 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof String) || !(a[2] instanceof Number)) return Integer.valueOf(0);
    long n = ((Number) a[2]).longValue();
    if (n > 1000000000L) n = 1000000000L;
    if (n < -1000000000L) n = -1000000000L;
    long r = @PKG@.OreBud.ask((java.util.UUID) a[0], ((String) a[1]).trim(), n);
    if (r > 2147483647L) r = 2147483647L;
    return Integer.valueOf(r < 0L ? 0 : (int) r);
  } catch (Throwable t) { @PKG@.OreBud.warn("skill:fn:oreBudget", t); return Integer.valueOf(0); }
}"""), obfn50))
ob50.addMethod(CtNewMethod.make(J14(r"""
public static String stats() {
  return "mined " + MINED.get() + ", Fortune extras " + EXTRA.get() + ", asks " + ASKS.get() + ", taken " + TAKEN.get() + ", given back " + BACK.get() + ", placed-furnace extra bars " + PLACED.get();
}"""), ob50))
'''
P.rep('''# 0.4.26: how many extra drops this break / harvest gives (0.4.25 drew once against chanceU; this draws once against Perks.fortune)
''', OB_JAVA + '''# 0.4.26: how many extra drops this break / harvest gives (0.4.25 drew once against chanceU; this draws once against Perks.fortune)
''')
# extras(...) is defined before this point? Perks.extras is added right after Perks.fortune (above breakDrops) - checked below
assert P.s.index("public static int extras(double t, double r)") < P.s.index("public static long extraBars(")

# ================================================================================================ breakDouble: the Fortune extras count in the budget
P.rep('''    int n = rolls(pr.getUuid(), row, {PKG}.SkillStore.level(pr.getUuid(), row), {PKG}.SkillCfg.familyId(bt));
    if (n == 1) doubled(pr, breakDrops(bt), row, world);
    else if (n >= 2) doubled(pr, bulk(breakDropsN(bt, n)), row, world);   // 0.4.48: ONE roll of n x the drops (not n loops)
''', '''    int n = rolls(pr.getUuid(), row, {PKG}.SkillStore.level(pr.getUuid(), row), {PKG}.SkillCfg.familyId(bt));
    if (n == 1) {{
      java.util.List xl = breakDrops(bt);
      {PKG}.OreBud.extras(pr.getUuid(), row, xl);   // 0.4.50: Mining Fortune ore extras count in the mined-ore budget
      doubled(pr, xl, row, world);
    }} else if (n >= 2) {{
      java.util.List xn = bulk(breakDropsN(bt, n));   // 0.4.48: ONE roll of n x the drops (not n loops)
      {PKG}.OreBud.extras(pr.getUuid(), row, xn);   // 0.4.50
      doubled(pr, xn, row, world);
    }}
''')

# ================================================================================================ BreakTask: the base ore of a natural Mining break
P.rep('''    {PKG}.SkillXp.gain(pr, {PKG}.Farm3.route((int) this.rule[0], rbt == null ? null : rbt.getId()), bamt);
''', '''    {PKG}.SkillXp.gain(pr, {PKG}.Farm3.route((int) this.rule[0], rbt == null ? null : rbt.getId()), bamt);
    if ((int) this.rule[0] == {PKG}.SkillDefs.MINING && (this.rule[2] == 0L || {PKG}.SkillCfg.IGNORE_PLACED)) {PKG}.OreBud.mined(this.u, rbt);   // 0.4.50: the mined-ore budget (natural blocks only)
''')

# ================================================================================================ SmFeed + SmFeedTask + the two bridge Functions (after Fortune)
SF_JAVA = '''# ================= 0.4.50 SmFeed: the Smelting Fortune line (bridge skill:fn:fortunefeed; Fortune's grouping, message kind "fortune") =====
for _d in ("public static final java.util.concurrent.ConcurrentHashMap GRP = new java.util.concurrent.ConcurrentHashMap();",
           "public static volatile long WIN = 1500L;", "public static volatile long MAX_AGE = 4000L;",
           "public static volatile boolean MANUAL = false;",      # HARNESS SEAM ONLY (false): no SmFeedTask is scheduled
           "public static final java.util.concurrent.atomic.AtomicLong HITS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong FEEDS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong CHATS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong OFFS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong SILENT = new java.util.concurrent.atomic.AtomicLong();"):
    smf50.addField(CtField.make(_d, smf50))
smft50.addInterface(pool.get("java.lang.Runnable"))
smft50.addField(CtField.make("public java.util.UUID u;", smft50))
smft50.addConstructor(CtNewConstructor.make("public SmFeedTask(java.util.UUID u) { this.u = u; }", smft50))
smf50.addMethod(CtNewMethod.make(J14(r"""
public static synchronized boolean add(java.util.UUID u, String id, long q, long now) {
  Object[] g = (Object[]) GRP.get(u);
  boolean opened = false;
  if (g == null) {
    g = new Object[] { new java.util.LinkedHashMap(), new long[] { now, now } };
    GRP.put(u, g);
    opened = true;
  }
  java.util.LinkedHashMap m = (java.util.LinkedHashMap) g[0];
  long[] c = (long[]) m.get(id);
  if (c == null) {
    if (m.size() >= 32) return opened;
    c = new long[1];
    m.put(id, c);
  }
  long t = c[0] + q;
  c[0] = t > 999999999L ? 999999999L : t;
  ((long[]) g[1])[1] = now;
  return opened;
}"""), smf50))
smf50.addMethod(CtNewMethod.make(J14(r"""
public static synchronized long due(java.util.UUID u, long now) {
  Object[] g = (Object[]) GRP.get(u);
  if (g == null) return -1L;
  long[] t = (long[]) g[1];
  long a = t[1] + WIN - now;
  long b = t[0] + MAX_AGE - now;
  long w = a < b ? a : b;
  return w > 0L ? w : 0L;
}"""), smf50))
smf50.addMethod(CtNewMethod.make(J14(r"""
public static synchronized Object[] take(java.util.UUID u) {
  Object[] g = (Object[]) GRP.remove(u);
  if (g == null) return null;
  java.util.LinkedHashMap m = (java.util.LinkedHashMap) g[0];
  int n = m.size();
  if (n == 0) return null;
  String[] ids = new String[n];
  long[] qs = new long[n];
  java.util.Iterator it = m.keySet().iterator();
  int i = 0;
  while (it.hasNext() && i < n) {
    Object k = it.next();
    ids[i] = (String) k;
    qs[i] = ((long[]) m.get(k))[0];
    i++;
  }
  return new Object[] { ids, qs };
}"""), smf50))
smf50.addMethod(CtNewMethod.make(J14(r"""
public static String cardText(String[] ids) {
  if (ids == null || ids.length == 0) return "";
  return "Smelting Fortune! " + @PKG@.Fortune.name(ids[0]) + (ids.length > 1 ? ", +" + (ids.length - 1) + " more" : "");
}"""), smf50))
smf50.addMethod(CtNewMethod.make(J14(r"""
public static String chatLine(String[] ids, long[] qs) {
  if (ids == null || qs == null || ids.length == 0) return "";
  StringBuilder sb = new StringBuilder("Smelting Fortune!");
  int n = ids.length < 4 ? ids.length : 3;
  for (int i = 0; i < n && i < qs.length; i++) sb.append(i == 0 ? " +" : ", +").append(qs[i]).append(' ').append(@PKG@.Fortune.name(ids[i]));
  if (ids.length > n) sb.append(", +").append(ids.length - n).append(" more");
  return sb.toString();
}"""), smf50))
# Fortune.deliver's routing (msg.fortune shown, msg.fortune.feed = feed or chat), its own texts and counters
smf50.addMethod(CtNewMethod.make(J14(r"""
public static String deliver(java.util.UUID u, @PR@ pr, String[] ids, long[] qs) {
  if (u == null || ids == null || qs == null || ids.length == 0 || qs.length == 0) return "none";
  if (!@PKG@.PerkCfg.DD_MSG || !@PKG@.Fortune.setting(u, "msg.fortune")) { OFFS.incrementAndGet(); return "off"; }
  if (@PKG@.Fortune.setting(u, "msg.fortune.feed")) {
    if (@PKG@.MsgRoute.fn("feed:fn:push") == null) { SILENT.incrementAndGet(); return "none"; }
    if (@PKG@.MsgRoute.feed(u, "fortune", ids[0], cardText(ids), qs[0])) { FEEDS.incrementAndGet(); return "feed"; }
  }
  String line = chatLine(ids, qs);
  @PKG@.MsgRoute.said(line);
  CHATS.incrementAndGet();
  if (pr != null) pr.sendMessage(@MSG@.raw(line).color("#b8f0a0"));
  return "chat";
}"""), smf50))
smf50.addMethod(CtNewMethod.make(J14(r"""
public static long step(java.util.UUID u, long now) {
  long w = due(u, now);
  if (w != 0L) return w;
  Object[] t = take(u);
  if (t == null) return -1L;
  try {
    @PR@ pr = @UNI@.get().getPlayer(u);
    if (pr == null || !pr.isValid()) return -1L;
    deliver(u, pr, (String[]) t[0], (long[]) t[1]);
  } catch (Throwable x) { @PKG@.Fortune.warn("the Smelting Fortune line", x); }
  return -1L;
}"""), smf50))
smf50.addMethod(CtNewMethod.make(J14(r"""
public static void sched(java.util.UUID u, long ms) {
  if (MANUAL || u == null) return;
  try {
    @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.SmFeedTask(u), ms, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) {
    GRP.remove(u);
    @PKG@.Fortune.warn("scheduling the Smelting Fortune line", t);
  }
}"""), smf50))
# true = queued for the player's line (shown); false = hidden by their switches / bad arguments
smf50.addMethod(CtNewMethod.make(J14(r"""
public static boolean hit(java.util.UUID u, String id, long q) {
  if (u == null || id == null || id.length() == 0 || q <= 0L) return false;
  try {
    if (!@PKG@.Fortune.shown(u)) { OFFS.incrementAndGet(); return false; }
    HITS.incrementAndGet();
    if (add(u, id, q, System.currentTimeMillis())) sched(u, WIN);
    return true;
  } catch (Throwable t) { @PKG@.Fortune.warn("the Smelting Fortune line", t); return false; }
}"""), smf50))
smf50.addMethod(CtNewMethod.make(J14(r"""
public static String stats() {
  return "hits " + HITS.get() + ", feed " + FEEDS.get() + ", chat " + CHATS.get() + ", off " + OFFS.get() + ", silent " + SILENT.get();
}"""), smf50))
smft50.addMethod(CtNewMethod.make(J14(r"""
public void run() {
  try {
    long w = @PKG@.SmFeed.step(this.u, System.currentTimeMillis());
    if (w > 0L) @HSV@.SCHEDULED_EXECUTOR.schedule(this, w, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) {
    @PKG@.SmFeed.GRP.remove(this.u);
    @PKG@.Fortune.warn("the Smelting Fortune task", t);
  }
}"""), smft50))
# bridge skill:fn:fortunefeed  apply(Object[]{ UUID, String itemId, Number extra }) -> Boolean (TRUE = queued for the player's line)
sffn50.addInterface(pool.get("java.util.function.Function"))
sffn50.addConstructor(CtNewConstructor.make("public FortuneFeedFn() { }", sffn50))
sffn50.addMethod(CtNewMethod.make(J14(r"""
public Object apply(Object arg) {
  try {
    if (!(arg instanceof Object[])) return Boolean.FALSE;
    Object[] a = (Object[]) arg;
    if (a.length < 3 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof String) || !(a[2] instanceof Number)) return Boolean.FALSE;
    long q = ((Number) a[2]).longValue();
    if (q > 999999999L) q = 999999999L;
    return Boolean.valueOf(@PKG@.SmFeed.hit((java.util.UUID) a[0], ((String) a[1]).trim(), q));
  } catch (Throwable t) { return Boolean.FALSE; }
}"""), sffn50))
'''
P.rep('''# "Double drop!" chat line: at most one per feedbackMs per player (count of doubles since the last line), hidden by /skills quiet
''', SF_JAVA + '''# "Double drop!" chat line: at most one per feedbackMs per player (count of doubles since the last line), hidden by /skills quiet
''')
P.rep('''    {PKG}.Fortune.retain(online);   // 0.4.42: Fortune groups / block positions / sparkle stamps of players who left
''', '''    {PKG}.Fortune.retain(online);   // 0.4.42: Fortune groups / block positions / sparkle stamps of players who left
    {PKG}.SmFeed.GRP.keySet().retainAll(online);   // 0.4.50: Smelting Fortune groups of players who left
''')

# ================================================================================================ SmeltFortTask + the SmeltSys hook (placed furnace, switch)
P.rep('''# ================= SmeltSys (0.4): InventoryChangeEvent on the player (vanilla ObjectiveInventoryChangeSystem pattern, Player query) =====
''', '''# ================= 0.4.50 SmeltFortTask: Smelting Fortune for bars taken out of a placed Furnace (smelt.fortune.placed, default off) =====
# items = [String bar id, Integer count, ...]; world thread (world.execute from SmeltSys); the extras as one stack per bar kind, storage first
sftk50.addInterface(pool.get("java.lang.Runnable"))
sftk50.addField(CtField.make("public java.util.UUID u;", sftk50))
sftk50.addField(CtField.make("public java.util.ArrayList items;", sftk50))
sftk50.addField(CtField.make("public String world;", sftk50))
sftk50.addField(CtField.make("public String key;", sftk50))
sftk50.addConstructor(CtNewConstructor.make("""
public SmeltFortTask(java.util.UUID u, java.util.ArrayList items, String world, String key) {
  this.u = u; this.items = items; this.world = world; this.key = key;
}""", sftk50))
sftk50.addMethod(CtNewMethod.make(J14(r"""
public void run() {
  try {
    if (this.items == null || !this.key.equals(@PKG@.SkillStore.pkey(this.u))) return;
    @PR@ pr = @UNI@.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    for (int i = 0; i + 1 < this.items.size(); i += 2) {
      String id = (String) this.items.get(i);
      int got = ((Integer) this.items.get(i + 1)).intValue();
      long x = @PKG@.OreBud.placedExtras(this.u, id, got);
      if (x <= 0L) continue;
      java.util.ArrayList l = new java.util.ArrayList();
      l.add(new @IS@(id, (int) x));
      String what = @PKG@.Perks.give(pr, @PKG@.Perks.bulk(l), this.world);
      if (what != null) @PKG@.SmFeed.hit(this.u, id, x);
    }
  } catch (Throwable t) { @PKG@.OreBud.warn("the placed-furnace Smelting Fortune", t); }
}"""), sftk50))
# ================= SmeltSys (0.4): InventoryChangeEvent on the player (vanilla ObjectiveInventoryChangeSystem pattern, Player query) =====
''')
P.rep('''    long smith = 0L;
    for (int m = 0; m < mv.size(); m++) {{''', '''    long smith = 0L;
    java.util.ArrayList fid = null;   // 0.4.50: bars for the placed-furnace Smelting Fortune (smelt.fortune.placed)
    for (int m = 0; m < mv.size(); m++) {{''')
P.rep('''      if (per > 0L) smith = smith + per * (long) got;
    }}
    if (smith <= 0L) return;''', '''      if (per > 0L) smith = smith + per * (long) got;
      if ({PKG}.SmithCfg.PLACED && id.startsWith("Ingredient_Bar_")) {{
        if (fid == null) fid = new java.util.ArrayList();
        fid.add(id);
        fid.add(Integer.valueOf(got));
      }}
    }}
    if (smith <= 0L && fid == null) return;''')
P.rep('''    java.util.UUID u = pr.getUuid();
    w.execute(new {PKG}.SmeltTask(u, {PKG}.SkillDefs.SMITHING, {PKG}.SkillCfg.scaled(smith), {PKG}.SkillStore.pkey(u)));''', '''    java.util.UUID u = pr.getUuid();
    if (smith > 0L) w.execute(new {PKG}.SmeltTask(u, {PKG}.SkillDefs.SMITHING, {PKG}.SkillCfg.scaled(smith), {PKG}.SkillStore.pkey(u)));
    if (fid != null) w.execute(new {PKG}.SmeltFortTask(u, fid, w.getName(), {PKG}.SkillStore.pkey(u)));   // 0.4.50''')

# ================================================================================================ setup / shutdown: the two bridge functions
P.rep('''  {PKG}.SkillStore.bridge().put("skill:fn:craftxp", new {PKG}.SkillCraftFn());
''', '''  {PKG}.SkillStore.bridge().put("skill:fn:craftxp", new {PKG}.SkillCraftFn());
  {PKG}.SkillStore.bridge().put("skill:fn:oreBudget", new {PKG}.OreBudgetFn());       // 0.4.50: the mined-ore budget (SkyySacks Smelting Fortune)
  {PKG}.SkillStore.bridge().put("skill:fn:fortunefeed", new {PKG}.FortuneFeedFn());   // 0.4.50: the Smelting Fortune line
''')
P.rep('''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:craftxp"); }} catch (Throwable t) {{ }}
''', '''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:craftxp"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:oreBudget"); }} catch (Throwable t) {{ }}     // 0.4.50
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:fortunefeed"); }} catch (Throwable t) {{ }}   // 0.4.50
''')
P.rep('''  try {{ {PKG}.Fortune.GRP.clear(); }} catch (Throwable t) {{ }}   // 0.4.42: a pending FortTask finds nothing to send
''', '''  try {{ {PKG}.Fortune.GRP.clear(); }} catch (Throwable t) {{ }}   // 0.4.42: a pending FortTask finds nothing to send
  try {{ {PKG}.SmFeed.GRP.clear(); }} catch (Throwable t) {{ }}    // 0.4.50
''')
P.rep('''"; tool Fortune (SkyyGear skill:bonus source gear) " + ({PKG}.PerkCfg.FORT_MAX > 0.0''',
      '''"; Mining Fortune = tool + tree " + ({PKG}.PerkCfg.TREE_UNCAP ? "added, uncapped" : "(tree capped)") + "; mined-ore budget (bridge skill:fn:oreBudget, up to " + {PKG}.SmithCfg.BUDGET_MAX + " per ore) + skill:fn:fortunefeed; Smelting Fortune at placed furnaces " + ({PKG}.SmithCfg.PLACED ? "on" : "off") + "; tool Fortune (SkyyGear skill:bonus source gear) " + ({PKG}.PerkCfg.FORT_MAX > 0.0''')


# ================================================================================================ 0.4.50 felled-tree search limits + Fl50Mig
FL_KEYS = [("fell.radius", "8", "16"), ("fell.maxLogs", "256", "1024"), ("fell.maxLeaves", "384", "2048"), ("fell.maxReads", "8000", "40000")]
FL50_MARK_ID = "SkyySkills 0.4.50 felled tree search"
FL50_MARK = "# SkyySkills 0.4.50 felled tree search: radius 16, 1024 logs, 2048 leaves, 40000 reads (old defaults 8, 256, 384, 8000)."
assert "=" not in FL50_MARK and ":" in FL50_MARK and len(FL50_MARK) <= 140 and all(ord(_ch) < 128 for _ch in FL50_MARK)
for _k, _o, _n in FL_KEYS:
    P.rep('FELL_L.append("%s=%s")\n' % (_k, _o), 'FELL_L.append("%s=%s")\n' % (_k, _n))
P.rep('''FELL_L.append("fell.maxReads=40000")
''', '''FELL_L.append("fell.maxReads=40000")
FL50_MARK_ID = "''' + FL50_MARK_ID + '''"
FL50_MARK = "''' + FL50_MARK + '''"
FELL_L.append(FL50_MARK)   # 0.4.50: Fl50Mig's run-once marker (a fresh file is never migrated)
''')
P.rep('''"int RADIUS = 8", "int HEIGHT = 64", "int MAX_LOGS = 256", "int MAX_LEAVES = 384",''', '''"int RADIUS = 16", "int HEIGHT = 64", "int MAX_LOGS = 1024", "int MAX_LEAVES = 2048",''')
P.rep('''             "int MAX_READS = 8000", "int MAX_SNAPS = 10",''', '''             "int MAX_READS = 40000", "int MAX_SNAPS = 10",''')
P.rep('''{PKG}.SkillCfg.lng(p, "fell.radius", 8L), 1L, 16L);''', '''{PKG}.SkillCfg.lng(p, "fell.radius", 16L), 1L, 16L);   // 0.4.50: 8 -> 16''')
P.rep('''{PKG}.SkillCfg.lng(p, "fell.maxLogs", 256L), 1L, 1024L);''', '''{PKG}.SkillCfg.lng(p, "fell.maxLogs", 1024L), 1L, 1024L);   // 0.4.50: 256 -> 1024''')
P.rep('''{PKG}.SkillCfg.lng(p, "fell.maxLeaves", 384L), 0L, 2048L);''', '''{PKG}.SkillCfg.lng(p, "fell.maxLeaves", 2048L), 0L, 2048L);   // 0.4.50: 384 -> 2048''')
P.rep('''{PKG}.SkillCfg.lng(p, "fell.maxReads", 8000L), 100L, 100000L);''', '''{PKG}.SkillCfg.lng(p, "fell.maxReads", 40000L), 100L, 100000L);   // 0.4.50: 8000 -> 40000''')
P.rep('''    ("fell.radius", "Felled search: sideways", "gathering", "int", "8", "1", "16", "", "blocks", "live,adv",''',
      '''    ("fell.radius", "Felled search: sideways", "gathering", "int", "16", "1", "16", "", "blocks", "live",   # 0.4.50: 8 -> 16, shown always''')
P.rep('''    ("fell.maxLogs", "Felled search: most logs", "gathering", "int", "256", "1", "1024", "", "", "live,adv",''',
      '''    ("fell.maxLogs", "Felled search: most logs", "gathering", "int", "1024", "1", "1024", "", "", "live",   # 0.4.50: 256 -> 1024, shown always''')
P.rep('''    ("fell.maxLeaves", "Felled search: most leaves", "gathering", "int", "384", "0", "2048", "", "", "live,adv",''',
      '''    ("fell.maxLeaves", "Felled search: most leaves", "gathering", "int", "2048", "0", "2048", "", "", "live,adv",   # 0.4.50: 384 -> 2048''')
P.rep('''    ("fell.maxReads", "Felled search: block reads", "gathering", "int", "8000", "100", "100000", "", "", "live,adv",''',
      '''    ("fell.maxReads", "Felled search: block reads", "gathering", "int", "40000", "100", "100000", "", "", "live,adv",   # 0.4.50: 8000 -> 40000''')
P.rep('''assert _dp.get("perk.treeFortuneUncapped") == "true"''', '''assert all(_dp.get(_k) == _n for _k, _o, _n in ''' + repr(FL_KEYS) + ''') and DEFAULTS.count(FL50_MARK_ID) == 1   # 0.4.50 felled search
assert _dp.get("perk.treeFortuneUncapped") == "true"''')
# Fl50Mig = a clone of Pd44Mig's reviewed machinery
P.rep('''zo49 = pool.makeClass(PKG + ".Zo49Mig")        # 0.4.49: the one-time zone ores + alloys XP lines appended to an existing xp.properties
''', '''zo49 = pool.makeClass(PKG + ".Zo49Mig")        # 0.4.49: the one-time zone ores + alloys XP lines appended to an existing xp.properties
fl50 = pool.makeClass(PKG + ".Fl50Mig")        # 0.4.50: the one-time felled-tree search limits update of an existing xp.properties
''')
_a = P.s.index('pd44.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(PD44_MARK_ID), pd44))')
_e = P.s.index('could not update xp.properties for 0.4.44', _a)
_e = P.s.index('}"""), pd44))\n', _e) + len('}"""), pd44))\n')
CL = P.s[_a:_e]
CL = CL.replace("json.dumps(PD44_MARK_ID)", "json.dumps(FL50_MARK_ID)").replace("json.dumps(PD44_MARK)", "json.dumps(FL50_MARK)")
def _sub(t, o, n):
    assert t.count(o) >= 1, o
    return t.replace(o, n)
CL = _sub(CL, '''pd44.addField(CtField.make('public static final String[] KEYS = new String[] { "acro.perfectDodge.windowMs", "acro.perfectDodge.maxXpPerMinute", "ranching.maxXpPerMinute" };', pd44))''',
          "pd44.addField(CtField.make('public static final String[] KEYS = new String[] { %s };', pd44))" % ", ".join('"%s"' % _k for _k, _o, _n in FL_KEYS))
CL = _sub(CL, '''pd44.addField(CtField.make('public static final String[] OLDS = new String[] { "50", "50", "200" };', pd44))''',
          "pd44.addField(CtField.make('public static final String[] OLDS = new String[] { %s };', pd44))" % ", ".join('"%s"' % _o for _k, _o, _n in FL_KEYS))
CL = _sub(CL, '''pd44.addField(CtField.make('public static final String[] NEWS = new String[] { "100", "1000000", "1000000" };', pd44))''',
          "pd44.addField(CtField.make('public static final String[] NEWS = new String[] { %s };', pd44))" % ", ".join('"%s"' % _n for _k, _o, _n in FL_KEYS))
CL = _sub(CL, '''assert ("\\n" + DEFAULTS).count("\\nacro.perfectDodge.windowMs=100\\n") == 1 and ("\\n" + DEFAULTS).count("\\nranching.maxXpPerMinute=1000000\\n") == 1''',
          '''assert all(("\\n" + DEFAULTS).count("\\n%s=%s\\n" % (_k, _n)) == 1 for _k, _o, _n in ''' + repr(FL_KEYS) + ''')''')
CL = _sub(CL, '"SkyySkills 0.4.44"', '"SkyySkills 0.4.50"')
CL = _sub(CL, "0.4.44 (perfect dodge 100 ms, XP caps; the file", "0.4.50 (felled tree search limits; the file")
CL = _sub(CL, "0.4.44 (perfect dodge 100 ms, XP caps)", "0.4.50 (felled tree search limits)")
CL = _sub(CL, "the 0.4.44 default is", "the 0.4.50 default is")
CL = _sub(CL, "before the 0.4.44 perfect dodge / XP cap update", "before the 0.4.50 felled tree search update")
CL = _sub(CL, "updated for 0.4.44:", "updated for 0.4.50:")
CL = _sub(CL, "0.4.44 marker added", "0.4.50 marker added")
CL = CL.replace("pd44", "fl50")
assert "0.4.44" not in CL and "pd44" not in CL and "PD44" not in CL, [l for l in CL.splitlines() if "44" in l][:5]
FL_JAVA = """
# ---- Fl50Mig (0.4.50, PROJECT-RULES section 4; a clone of Pd44Mig's reviewed machinery): ONCE on an EXISTING xp.properties, setup() right
# after Zo49Mig.run, BEFORE SkillCfg.load. fell.radius / maxLogs / maxLeaves / maxReads: when a key's LAST entry is a one-line entry holding
# exactly the old default (8 / 256 / 384 / 8000) -> the new one (16 / 1024 / 2048 / 40000); any other value kept (INFO); no line = nothing.
# The marker at the end; config-history copy first; one config-changes.log line per change (Undo); Properties check; atomicWrite.
""" + CL
P.rep('''
# ================= SkillIO.run (0.4.32 C): the SkyySkills-IO jobs''', FL_JAVA + '''
# ================= SkillIO.run (0.4.32 C): the SkyySkills-IO jobs''')
P.rep('''  {PKG}.Zo49Mig.run();        // 0.4.49: the zone ores + alloys XP lines into an existing xp.properties, once; History first
''', '''  {PKG}.Zo49Mig.run();        // 0.4.49: the zone ores + alloys XP lines into an existing xp.properties, once; History first
  {PKG}.Fl50Mig.run();        // 0.4.50: untouched felled-tree search limits 8 / 256 / 384 / 8000 -> 16 / 1024 / 2048 / 40000, once; History first
''')

# ================================================================================================ the class list
P.rep('''          rbcm, snd39, rbs39, pd44, fm48, zo49,
          hubb, hopen, fort42, ftask42, hpr43, hprfn43, even43):   # 0.4.49: + Zo49Mig;''', '''          rbcm, snd39, rbs39, pd44, fm48, zo49, fl50, ob50, obfn50, smf50, smft50, sffn50, sftk50,
          hubb, hopen, fort42, ftask42, hpr43, hprfn43, even43):   # 0.4.50: + Fl50Mig, OreBud, OreBudgetFn, SmFeed, SmFeedTask, FortuneFeedFn, SmeltFortTask; 0.4.49: + Zo49Mig;''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
