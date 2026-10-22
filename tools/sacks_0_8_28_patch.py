"""Derive SkyySacks/build_skyysacks_0.8.28.py from the SET pin 0.8.27 (the GENERATED build_skyysacks_0.8.27.py; edit THIS file, then
regenerate: python tools/sacks_0_8_28_patch.py; never re-run sacks_0_8_27_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.27 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_28_patch.py   then   python SkyySacks/build_skyysacks_0.8.28.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.28.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.28 (2026-10-22) = THE REAL LOCK REASON FOR /smithing (bridge sacks:fn:craftWhy). Skyy's 10-22 screenshots: Armor Bench II equipped in
  Void Charms, yet /smithing > Mining Armor > Bronze Set says "Needs the Armor Bench I accessory in your Void Charms" and every Craft button
  says LOCKED ("still says its locked, even though i have the charm"). ROOT CAUSE (not an accessory bug): the bench-accessory rule passes
  (Armor_Bench tier 2 >= the recipe's tier 1 - CraftPage.benchRecipes); the Bronze Mining set recipes SkyyGear_Recipe_Armor_Bronze_<Slot>
  are KnowledgeRequired and SkyyCollections grants them only at Copper V AND Iron V (Skyy's profile: Copper IV 201, Iron IV 228), so
  KnowSync.allowed leaves them out of sacks:fn:craftList - and SkyyGear's GearSmith.lockWhy blames the bench accessory for ANY recipe missing
  from that list. SkyyGear could not tell why; this round gives it the answer:
  1. sacks:fn:craftWhy {UUID player, String recipeId} -> String, the same rule as sacks:fn:craftList / the /craft page (SackBridge.whyCode):
       null                                  = allowed here (or cannot tell: bad arguments / an error - keep your own text)
       "unknown"                             = no such recipe;  "paused" = the player is not online
       "table"                               = only at its table (timed)
       "bench|<benchId>|<need>|<have>"       = the bench accessory is missing / too low (have 0 = none equipped)
       "know|<CollId>|<Name>|<tier>|<threshold>|<count>" = a recipe not unlocked yet; the fields are SkyyCollections' coll:fn:where answer
                                               for it (the first collection that lists it - an alloy recipe also needs its other input
                                               collection at the same tier); just "know" when Collections cannot tell
     SkyyGear (a later round) should show "know" as the collection line instead of the accessory line.
  2. CraftPage.tierOk(acc, bench, need) = the accessory tier test, now ONE method used by benchRecipes (behaviour identical: tier > 0 and
     need (0 = 1) <= tier) and by whyCode - the harness runs it for every bench x tier.
  Every other bench accessory was checked against Assets.zip: Workbench, Armor_Bench, Weapon_Bench, Farmingbench, Arcanebench,
  Furniture_Bench, Loombench, Salvagebench match their recipes' bench ids exactly, any tier counts as "at least" (no exact-id match
  anywhere). Furnace / Tannery / Campfire are timed (own tabs). Side finding (not changed): 4 vanilla Utility recipes (Helipack, Leather /
  Medium Backpack, Quiver) name the bench "ArmorBench" (no underscore), which no bench accessory unlocks.
  Saved data / config / commands / systems: none changed; one bridge key added. ROLLBACK to 0.8.27: safe (the key disappears; SkyyGear
  falls back to its own text).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.27.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.28.py"))
assert P.has('VERSION = "0.8.27"\n') and P.has("SackMig0826") and not P.has("utilCounts") and not P.has("craftWhy\", new"), \
    "not the live generated SkyySacks 0.8.27"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.28 (2026-10-22)"):].rstrip() + "\n"

P.rep('''  config change. ROLLBACK to 0.8.26: safe (the WARN comes back).
"""
''', '''  config change. ROLLBACK to 0.8.26: safe (the WARN comes back).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.27"\n', 'VERSION = "0.8.28"\n')

# 2. the one accessory tier test (benchRecipes + whyCode)
P.rep('''    if (k.equalsIgnoreCase(bench)) { int t = ((Integer) acc.get(k)).intValue(); if (t > best) best = t; }
  }
  return best;
}""", cpg))
''', '''    if (k.equalsIgnoreCase(bench)) { int t = ((Integer) acc.get(k)).intValue(); if (t > best) best = t; }
  }
  return best;
}""", cpg))
# 0.8.28: THE accessory tier test (an equipped tier counts for every recipe up to it; need 0 = 1) - benchRecipes and SackBridge.whyCode
cpg.addMethod(CtNewMethod.make("""
public static boolean tierOk(java.util.HashMap acc, String bench, int need) {
  int tier = accTier(acc, bench);
  if (need <= 0) need = 1;
  return tier > 0 && need <= tier;
}""", cpg))
''')
P.rep('''      int tier = accTier(acc, br[i].id);
      if (tier <= 0) continue;
      int need = br[i].requiredTierLevel; if (need <= 0) need = 1;
      if (need <= tier) {{ ids.add(r.getId()); break; }}
''', '''      if (tierOk(acc, br[i].id, br[i].requiredTierLevel)) {{ ids.add(r.getId()); break; }}   // 0.8.28: the one tier test
''')

# 1. sacks:fn:craftWhy
P.rep('''  if (!@PKG@.KnowSync.allowed(r, u, @PKG@.KnowSync.known(p), coll)) return "you have not unlocked this recipe";
  return null;
}"""), sbr))
''', '''  if (!@PKG@.KnowSync.allowed(r, u, @PKG@.KnowSync.known(p), coll)) return "you have not unlocked this recipe";
  return null;
}"""), sbr))
# 0.8.28: the bench a recipe would need an accessory for in the merged tabs (the benchRecipes(u, null) filter): Object[] { id, Integer need }
# of the first such requirement, null = none (Fieldcraft / timed / retired only)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static Object[] benchNeed(@CRR@ r) {
  if (r == null) return null;
  @BRQ@[] br = r.getBenchRequirement();
  if (br == null) return null;
  for (int i = 0; i < br.length; i++) {
    if (br[i] == null || br[i].id == null || br[i].id.equalsIgnoreCase("Fieldcraft")) continue;
    if (@PKG@.CraftPage.retiredBench(br[i].id) || @PKG@.CraftPage.separateBench(br[i].id)) continue;
    if (br[i].type == @BTP@.Processing && !@PKG@.CraftPage.instantProc(br[i].id)) continue;
    int need = br[i].requiredTierLevel;
    if (need <= 0) need = 1;
    return new Object[] { br[i].id, Integer.valueOf(need) };
  }
  return null;
}"""), sbr))
# 0.8.28 sacks:fn:craftWhy (patch docstring): WHY craftList leaves a recipe out - the craftWhy order (table, Collections tab, bench set, knowledge)
sbr.addMethod(CtNewMethod.make(jt(r"""
public static String whyCode(java.util.UUID u, String rid) {
  if (u == null || rid == null) return null;
  Object o = @CRR@.getAssetMap().getAsset(rid);
  if (!(o instanceof @CRR@)) return "unknown";
  @CRR@ r = (@CRR@) o;
  @PLA@ p = playerOf(u);
  if (p == null) return "paused";
  if (@PKG@.CraftPage.tableOnly(r)) return "table";
  java.util.HashSet coll = @PKG@.CraftPage.collectionRecipes(u);
  if (coll.contains(rid)) return null;
  if (!@PKG@.CraftPage.craftSet(u).contains(rid)) {
    Object[] b = benchNeed(r);
    if (b == null) return "bench||1|0";
    String bid = (String) b[0];
    int have = @PKG@.CraftPage.accTier(@PKG@.CraftPage.accessories((@PLA@) null, u), bid);
    return "bench|" + bid + "|" + b[1] + "|" + have;
  }
  if (!@PKG@.KnowSync.allowed(r, u, @PKG@.KnowSync.known(p), coll)) {
    String[] w = @PKG@.KnowSync.where(u, rid);
    if (w == null || w.length < 5) return "know";
    return "know|" + w[0] + "|" + w[1] + "|" + w[2] + "|" + w[3] + "|" + w[4];
  }
  return null;
}"""), sbr))
''')
P.rep('''public static Object dflt(int mode) {
  if (mode == 7 || mode == 8) return null;''', '''public static Object dflt(int mode) {
  if (mode == 7 || mode == 8 || mode == 18) return null;   // 0.8.28: 18 craftWhy''')
P.rep('''    String s1 = (String) a[1];
    if (mode == 8) return craftHave(u, s1);''', '''    String s1 = (String) a[1];
    if (mode == 18) return whyCode(u, s1);   // 0.8.28 sacks:fn:craftWhy
    if (mode == 8) return craftHave(u, s1);''')
P.rep('''    if (this.mode >= 14) return @PKG@.SackBridge.fishCall(this.mode, o);''',
      '''    if (this.mode == 18) return @PKG@.SackBridge.call2(this.mode, o);   // 0.8.28: sacks:fn:craftWhy (before the fish modes)
    if (this.mode >= 14) return @PKG@.SackBridge.fishCall(this.mode, o);''')
P.rep('''  return (this.mode == 3 || this.mode == 12 || this.mode == 13 || this.mode == 14 || this.mode == 17) ? null''',
      '''  return (this.mode == 3 || this.mode == 12 || this.mode == 13 || this.mode == 14 || this.mode == 17 || this.mode == 18) ? null''')
P.rep('''  sbr0.put("sacks:fn:fishTaken", new {PKG}.SackFn(17));   // token round: did that take reach the disk
''', '''  sbr0.put("sacks:fn:fishTaken", new {PKG}.SackFn(17));   // token round: did that take reach the disk
  sbr0.put("sacks:fn:craftWhy", new {PKG}.SackFn(18));   // 0.8.28: why craftList leaves a recipe out (SkyyGear's /smithing lock note)
''')
assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.28 adds no system / command"
P.finish()
