"""Derive SkyySacks/build_skyysacks_0.8.31.py from the SET pin 0.8.30 (the GENERATED build_skyysacks_0.8.30.py; edit THIS file, then
regenerate: python tools/sacks_0_8_31_patch.py; never re-run sacks_0_8_30_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.30 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_31_patch.py   then   python SkyySacks/build_skyysacks_0.8.31.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.31.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.31 (2026-10-25) = AUTO-COMPACT FIX (round compfix). Skyy (SkyySacks 0.8.30, Storage > Pocket > Farming, Auto-compact On, "4 of 25 items
  unlocked", 4,955 Essence of Life / 1,658 Carrot / 566 Lettuce / 537 Wheat loose): "my auto compact isnt working" + "my carrots and lettuce
  arnt compacting either" + "ohhh i relogged and it worked" + "Except for the essence, that didn't work." + (Life Essence Concentrated
  selected) "this is what we use instead of an enchanted version for essence of life" + "have it read every few minuets, or update on
  unlock, so you don t have this issue again".
  FOUND (live data, read-only copies): (1) crops: the compactor itself is right - VoidCompact.run on a scratch copy of the live pool / pd /
     config with the player's unlocked recipes compacts Wheat / Carrot / Lettuce at once; Skyy_Ench_Wheat_Recipe_Generated_0 WAS unlocked
     (Skyy crafted it at 19:15). After the restart (19:35) crafts.log shows VOID-COMPACT at 19:36:37 and then every 2 s. Between the purchase
     (19:23) and the shutdown (19:35) NOTHING compacted ("auto-compact this run: 0 Enchanted made") and nothing warned: the 2 s sweep did not
     run. The sweep's SackTick sat on HytaleServer.SCHEDULED_EXECUTOR - ONE thread (Executors.newSingleThreadScheduledExecutor, read from
     the server jar's <clinit>) shared by the engine and every mod; in the same session SkyyShards' idle unload (ShTick, the same thread)
     never unloaded the empty shard world after 01:22 (it does 120 s after empty in both other sessions). So that shared thread was held by
     some task; our sweep (auto-compact, stack refill, deposits by sweep, recipe sync) waited with it. Which task held it is not known
     (UNVERIFIED - the watchdog below names the stall in the log next time). (2) Essence of Life: no pair at all - 0.8.30's pairs are
     tools/skyyench.py TABLE rows, and the Life Essence row is retired (Skyy 10-16: use the vanilla Greater Essence of Life =
     Ingredient_Life_Essence_Concentrated, VANILLA_ENCH; vanilla recipe 100 Essence of Life -> 1 at the Farmer's Workbench, no knowledge).
  1. THE SWEEP ON OUR OWN THREAD: SackTick (the 2 s sweep dispatcher: needs() + w.execute(SweepTask)) is scheduled on SackPool.WRITER (our
     private daemon thread) instead of the shared scheduler, so another mod's stuck task can no longer stop auto-compact. WATCHDOG
     (SackBeat): each tick puts one tiny task on the shared scheduler (only when the last one ran); not run for 30 s = one WARN naming it
     ("the server's shared scheduler ... has not run for N s"), and an INFO when it runs again. CraftTick / ProcTick stay where they were.
  2. VANILLA PAIRS (tools/skyyench.py VANILLA_ENCH): Ingredient_Life_Essence -> Ingredient_Life_Essence_Concentrated, 100 : 1 (the vanilla
     recipe's own ratio), both in Farming. No recipe to unlock, so it counts as unlocked once the player's Life Essence collection is at
     tier I or higher (coll:fn:tier - the same tier I every crop's Enchanted recipe has since SkyyCollections 0.2.28). Only the COMPACTOR
     and the page use it: crafting / Unpack / the bag upgrade do not open Greater Essence of Life (it is a vanilla item vanilla recipes
     use - left as it is; follow-up if wanted).
  3. UNLOCKS ARE READ AT ONCE + A SAFETY RE-READ: the unlocked list is read from coll:recipes on every sweep (unchanged; a changed list
     already re-sweeps), and the sweep signature now also holds SkyyCollections' coll:<uuid> summary (tiers / recipes), so ANY collection
     tier-up re-sweeps within 2 s (the vanilla pairs have no recipe to change). Every pd.compact.recheck seconds (Server Setup, default 180,
     0 = off) every online player's cached unlocked list is dropped and re-read and they are swept.
  4. COMPACT RIGHT AWAY: a Pay (buy) or Turn on click compacts that bag at once on the page's own thread (VoidCompact.runNow), not only on
     the next sweep; the result line says how many were made. Login: the first sweep after joining already compacts (unchanged).
  5. THE PAGE SAYS WHAT IS UNLOCKED: the Auto-compact box (On) lists the unlocked items by name ("On for 5 of 26: Wheat, Carrot, Lettuce,
     Potato, Essence of Life") and the closest locked one with the collection tier that unlocks it ("Next: Pumpkin at Pumpkin I (0/15)",
     from coll:fn:where). A selected item in a bag with Auto-compact says "Auto-compacts (unlocked)" or "Locked: <collection> <tier> (n/m)".
  Upgrade card (Skyy asked): "Carrot 1,658 / 1,000" with 16 loose Carrot is right - since 0.8.30 fixer 2 the bag upgrade counts loose +
  100 x each Enchanted Carrot (and pays by opening the fewest), the same rule crafting uses. Unchanged.
  No saved-data change; new Server Setup row pd.compact.recheck (a missing line = 180, no migration). ROLLBACK to 0.8.30: safe alone (the
  row line stays in config.properties, unknown to 0.8.30; already made Greater Essence of Life stays - it is a vanilla item).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.30.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.31.py"))
assert P.has('VERSION = "0.8.30"\n') and P.has("VoidCompact") and not P.has("SackBeat"), "not the live generated SkyySacks 0.8.30"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.31 (2026-10-25)"):].rstrip() + "\n"

# the 0.8.30 docstring ends with its ACCEPTED note; the 0.8.31 note follows it
P.rep('''  once on the writer) can leave the upgrade bought without the coins taken - the player-favouring direction, same trade-off as the shops.
"""
''', '''  once on the writer) can leave the upgrade bought without the coins taken - the player-favouring direction, same trade-off as the shops.
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.30"\n', 'VERSION = "0.8.31"\n')

# ---------------------------------------------------------------- classes
P.rep('''tick = pool.makeClass(PKG + ".SackTick")
''', '''tick = pool.makeClass(PKG + ".SackTick")
sbeat = pool.makeClass(PKG + ".SackBeat")   # 0.8.31: the shared-scheduler watchdog
''')
P.rep('''          vcm,    # 0.8.30: VoidCompact
''', '''          vcm,    # 0.8.30: VoidCompact
          sbeat,  # 0.8.31: SackBeat
''')

# ---------------------------------------------------------------- the vanilla pairs + the recheck row
P.rep('''print("0.8.30 auto-compact: %d base -> Enchanted pairs (skipped resource-type rows: %s)" % (
    len(CMP_PAIRS), ", ".join(t[0] for t in EN.TABLE if t[1] != "I")))
''', '''print("0.8.30 auto-compact: %d base -> Enchanted pairs (skipped resource-type rows: %s)" % (
    len(CMP_PAIRS), ", ".join(t[0] for t in EN.TABLE if t[1] != "I")))
# 0.8.31 (tools/sacks_0_8_31_patch.py): the collections whose Enchanted item is a VANILLA item (EN.VANILLA_ENCH - Skyy 10-16: Greater Essence
# of Life) compact too: base = the retired row's base item, ratio = the vanilla recipe's 100, unlocked = the collection at tier CMP_VTIER+
_RET_BASE = dict((_r[3], _r[2]) for _i, _r in EN.RETIRED_C1)
CMP_VPAIRS = [(_RET_BASE[_c], _v, _c) for _c, (_v, _cat) in sorted(EN.VANILLA_ENCH.items())]
CMP_VTIER, CMP_RECHECK_DEF = 1, 180
assert CMP_VPAIRS == [("Ingredient_Life_Essence", "Ingredient_Life_Essence_Concentrated", "LifeEssence")], CMP_VPAIRS
assert not set(b for b, _e, _c in CMP_VPAIRS) & set(b for b, _e in CMP_PAIRS), "0.8.31: a vanilla pair's base is no Enchanted base"
print("0.8.31 auto-compact: + %d vanilla pair(s): %s (unlocked at collection tier %d)" % (
    len(CMP_VPAIRS), ", ".join("%s -> %s" % (b, e) for b, e, _c in CMP_VPAIRS), CMP_VTIER))
''')
P.rep('''                     "public static volatile int CMP_LEVEL = %d;" % CMP_LEVEL_DEF]
''', '''                     "public static volatile int CMP_LEVEL = %d;" % CMP_LEVEL_DEF]
                  + ["public static volatile int CMP_RECHECK = %d;" % CMP_RECHECK_DEF]   # 0.8.31
''')
P.rep('''             '  CMP_LEVEL = intKey(p, "pd.compact.level", %d, 1, 100);' % CMP_LEVEL_DEF]
''', '''             '  CMP_LEVEL = intKey(p, "pd.compact.level", %d, 1, 100);' % CMP_LEVEL_DEF,
             '  CMP_RECHECK = intKey(p, "pd.compact.recheck", %d, 0, 3600);' % CMP_RECHECK_DEF]   # 0.8.31
''')
P.rep('''                           + ["CMP_ON", "CRAFT_OPEN", "CMP_LEVEL"] + ["CMP_COINS_" + c.upper() for c in PD_CATS])   # 0.8.30
''', '''                           + ["CMP_ON", "CRAFT_OPEN", "CMP_LEVEL"] + ["CMP_COINS_" + c.upper() for c in PD_CATS]   # 0.8.30
                           + ["CMP_RECHECK"])   # 0.8.31
''')
P.rep('''    "#pd.compact.on=true", "#bags.craftOpen=true", "#pd.compact.level=%d" % CMP_LEVEL_DEF] + [''',
      '''    "# pd.compact.recheck = seconds between safety re-reads of every online player's unlocked list (0 = off).",   # 0.8.31
    "#pd.compact.on=true", "#bags.craftOpen=true", "#pd.compact.level=%d" % CMP_LEVEL_DEF, "#pd.compact.recheck=%d" % CMP_RECHECK_DEF] + [''')
P.rep('''           "The price below x the coin curve at this level (10 = x1). Higher = dearer.", "CMP_LEVEL"),
''', '''           "The price below x the coin curve at this level (10 = x1). Higher = dearer.", "CMP_LEVEL"),
    # 0.8.31 (Skyy "have it read every few minuets, or update on unlock, so you don t have this issue again")
    _pdrow("pd.compact.recheck", "Auto-compact re-check (seconds)", "void", "int", str(CMP_RECHECK_DEF), "0", "3600", "s", "live,adv",
           "Every this many seconds each online player's unlocked list is re-read and compacted. 0 = off.", "CMP_RECHECK"),
''')

# ---------------------------------------------------------------- VoidCompact: the vanilla pairs
P.rep('''vcm.addField(CtField.make('public static final String RSUF = "_Recipe_Generated_0";', vcm))
''', '''vcm.addField(CtField.make('public static final String RSUF = "_Recipe_Generated_0";', vcm))
# 0.8.31: the vanilla pairs (EN.VANILLA_ENCH) - compactor + page only; VCOLL = the collection whose tier VTIER+ unlocks it
vcm.addField(CtField.make("public static final String[] VBASE = " + _jarr([b for b, _e, _c in CMP_VPAIRS]) + ";", vcm))
vcm.addField(CtField.make("public static final String[] VENCH = " + _jarr([e for _b, e, _c in CMP_VPAIRS]) + ";", vcm))
vcm.addField(CtField.make("public static final String[] VCOLL = " + _jarr([c for _b, _e, c in CMP_VPAIRS]) + ";", vcm))
vcm.addField(CtField.make("public static final int VTIER = %d;" % CMP_VTIER, vcm))
''')
P.rep('''    if (coll != null && !coll.contains(ENCH[i] + RSUF)) continue;
    n++;
  }
  return n;
}"""), vcm))
''', '''    if (coll != null && !coll.contains(ENCH[i] + RSUF)) continue;
    n++;
  }
  // 0.8.31: + the vanilla pairs (only in the total - their unlock is a collection tier, see pairsU)
  if (coll == null) for (int j = 0; j < VBASE.length; j++) if (cat.equals(@PKG@.SackDefs.homeOf(VBASE[j])) && @PKG@.SackDefs.homeOf(VENCH[j]) != null) n++;
  return n;
}"""), vcm))
# 0.8.31: the player's tier of a collection (SkyyCollections coll:fn:tier {UUID, collection id}); -1 = unknown
vcm.addMethod(CtNewMethod.make(jt(r"""
public static int vtier(java.util.UUID u, String cid) {
  if (u == null || cid == null) return -1;
  try {
    java.util.function.Function g = fn("coll:fn:tier");
    Object r = g == null ? null : g.apply(new Object[] { u, cid });
    return r instanceof Number ? ((Number) r).intValue() : -1;
  } catch (Throwable t) { return -1; }
}"""), vcm))
# 0.8.31: combined pair index i (0 .. BASE.length - 1 = the Enchanted rows, then the vanilla pairs)
vcm.addMethod(CtNewMethod.make(jt(r"""
public static int np() { return BASE.length + VBASE.length; }"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static String baseAt(int i) { return i < BASE.length ? BASE[i] : VBASE[i - BASE.length]; }"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static String enchAt(int i) { return i < BASE.length ? ENCH[i] : VENCH[i - BASE.length]; }"""), vcm))
# is pair i unlocked for player u (coll = their coll:recipes set): an Enchanted row = its recipe id is in it; a vanilla pair = the tier
vcm.addMethod(CtNewMethod.make(jt(r"""
public static boolean unl(java.util.UUID u, int i, java.util.Set coll) {
  if (i < BASE.length) return coll != null && coll.contains(ENCH[i] + RSUF);
  return vtier(u, VCOLL[i - BASE.length]) >= VTIER;
}"""), vcm))
# the pair a base item belongs to (-1 = none)
vcm.addMethod(CtNewMethod.make(jt(r"""
public static int pairOf(String b) {
  int x = idxBase(b);
  if (x >= 0) return x;
  for (int j = 0; b != null && j < VBASE.length; j++) if (VBASE[j].equals(b)) return BASE.length + j;
  return -1;
}"""), vcm))
# how many pairs of bag ci are unlocked for u (both kinds)
vcm.addMethod(CtNewMethod.make(jt(r"""
public static int pairsU(java.util.UUID u, int ci, java.util.Set coll) {
  if (ci < 0 || ci >= @PKG@.SackDefs.CATS.length) return 0;
  String cat = @PKG@.SackDefs.CATS[ci];
  int n = 0;
  for (int i = 0; i < np(); i++) {
    if (!cat.equals(@PKG@.SackDefs.homeOf(baseAt(i))) || @PKG@.SackDefs.homeOf(enchAt(i)) == null) continue;
    if (unl(u, i, coll)) n++;
  }
  return n;
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static String roman(int t) {
  String[] r = new String[] { "", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X" };
  return (t >= 0 && t < r.length) ? r[t] : ("T" + t);
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static String nm(String id) {
  String n = null;
  try { n = @PKG@.SackDefs.dname(id); } catch (Throwable t) { n = null; }
  return n == null || n.length() == 0 ? id : n;
}"""), vcm))
# why pair i is locked: {collection name, tier, threshold, count} ("" when unknown); a vanilla pair = its collection at VTIER
vcm.addMethod(CtNewMethod.make(jt(r"""
public static String[] why(java.util.UUID u, int i) {
  if (i >= BASE.length) {
    String c = VCOLL[i - BASE.length];
    long n = -1L;
    try { java.util.function.Function g = fn("coll:fn:count"); Object r = g == null ? null : g.apply(new Object[] { u, c }); if (r instanceof Number) n = ((Number) r).longValue(); } catch (Throwable t) { }
    return new String[] { nm(VBASE[i - BASE.length]), String.valueOf(VTIER), "", n < 0L ? "" : String.valueOf(n) };
  }
  String[] p = @PKG@.KnowSync.where(u, ENCH[i] + RSUF);
  if (p == null) return null;
  return new String[] { p[1], p[2], p[3], p[4] };
}"""), vcm))
vcm.addMethod(CtNewMethod.make(jt(r"""
public static String whyText(String[] w) {
  if (w == null) return "its collection (/collections)";
  int t = 0;
  try { t = Integer.parseInt(w[1].trim()); } catch (Throwable x) { t = 0; }
  String s = w[0] + " " + roman(t);
  if (w[2].length() > 0 && w[3].length() > 0) s = s + " (" + w[3] + "/" + w[2] + ")";
  return s;
}"""), vcm))
# THE PAGE LINE (bag ci, Auto-compact on): the unlocked items by name, then the closest locked one and the tier that unlocks it
vcm.addMethod(CtNewMethod.make(jt(r"""
public static String names(java.util.UUID u, int ci, java.util.Set coll, int cap) {
  if (ci < 0 || ci >= @PKG@.SackDefs.CATS.length) return "";
  String cat = @PKG@.SackDefs.CATS[ci];
  StringBuilder sb = new StringBuilder();
  int un = 0; int all = 0; int more = 0;
  int best = -1; double bestR = -1.0; String[] bestW = null;
  for (int i = 0; i < np(); i++) {
    if (!cat.equals(@PKG@.SackDefs.homeOf(baseAt(i))) || @PKG@.SackDefs.homeOf(enchAt(i)) == null) continue;
    all++;
    if (unl(u, i, coll)) {
      un++;
      String n = nm(baseAt(i));
      if (sb.length() + n.length() + 2 <= cap) { if (sb.length() > 0) sb.append(", "); sb.append(n); } else more++;
      continue;
    }
    String[] w = why(u, i);
    double r = 0.0;
    try { if (w != null && w[2].length() > 0) r = Double.parseDouble(w[3]) / Math.max(1.0, Double.parseDouble(w[2])); } catch (Throwable x) { r = 0.0; }
    if (best < 0 || r > bestR) { best = i; bestR = r; bestW = w; }
  }
  String s = "On for " + un + " of " + all + (un > 0 ? ": " + sb.toString() + (more > 0 ? " +" + more : "") : "") + ".";
  if (best >= 0) s = s + " Next: " + nm(baseAt(best)) + " at " + whyText(bestW) + ".";
  else if (all > 0) s = s + " Everything here is unlocked.";
  return s;
}"""), vcm))
# the selected item's line (a base of a pair in a bag with Auto-compact on): "" otherwise
vcm.addMethod(CtNewMethod.make(jt(r"""
public static String stateOf(java.util.UUID u, String k, String id) {
  int i = pairOf(id);
  if (i < 0) return "";
  int ci = @PKG@.SackDefs.catIndex(@PKG@.SackDefs.homeOf(id));
  if (ci < 0 || !active(k, ci)) return "";
  if (unl(u, i, @PKG@.KnowSync.collShared(u))) return "Auto-compacts (unlocked)";
  return "Locked: " + whyText(why(u, i));
}"""), vcm))
''')
# the compactor walks both kinds of pairs
P.rep('''  for (int i = 0; i < BASE.length; i++) {
    String b = BASE[i];
    String e = ENCH[i];
    int ci = @PKG@.SackDefs.catIndex(@PKG@.SackDefs.homeOf(b));
    if (ci < 0 || !active(k, ci)) continue;
    String ce = @PKG@.SackDefs.homeOf(e);
    int ei = @PKG@.SackDefs.catIndex(ce);
    if (ei < 0 || !coll.contains(e + RSUF)) continue;''', '''  for (int i = 0; i < np(); i++) {   // 0.8.31: + the vanilla pairs
    String b = baseAt(i);
    String e = enchAt(i);
    int ci = @PKG@.SackDefs.catIndex(@PKG@.SackDefs.homeOf(b));
    if (ci < 0 || !active(k, ci)) continue;
    String ce = @PKG@.SackDefs.homeOf(e);
    int ei = @PKG@.SackDefs.catIndex(ce);
    if (ei < 0) continue;
    if (@PKG@.SackPool.get(k, b) < RATIO) continue;
    if (!unl(u, i, coll)) continue;''')
# compact right away (page clicks) + the safety re-read clock
P.rep('''# fixer: undo a not-paid purchase line (in memory + on disk now; a failed save stays dirty and the writer retries it)
''', '''# 0.8.31: compact NOW (the page's Pay / Turn on click, world thread) - the same run as the sweep's, its own capacity map; never throws
vcm.addMethod(CtNewMethod.make(jt(r"""
public static long runNow(java.util.UUID u, String k) {
  try { return run(u, k, @PKG@.VoidStore.capsK(u, k)); }
  catch (Throwable t) { @PKG@.KnowSync.warnOnce("auto-compact (page click) failed - the next sweep retries: " + t); return 0L; }
}"""), vcm))
# fixer: undo a not-paid purchase line (in memory + on disk now; a failed save stays dirty and the writer retries it)
''')

# ---------------------------------------------------------------- the page
P.rep('''    int un = @PKG@.VoidCompact.pairsIn(ci, cs0);
    kcol = kon ? "@C:have@" : "@C:caption@";
    t1 = kon ? "Auto-compact: On" : "Auto-compact: Paused";
    t2 = kon ? (un + " of " + pairs + " items unlocked: each 100 -> 1 Enchanted. Crafting opens them.")
             : "Bought - nothing compacts here until you turn it on.";
    if (kon && "Mining".equals(cat)) t2 = un + " of " + pairs + " unlocked: 100 -> 1 Enchanted. Not yet: Rubble, Sand, Crystal.";   // fixer''',
      '''    kcol = kon ? "@C:have@" : "@C:caption@";
    t1 = kon ? "Auto-compact: On" : "Auto-compact: Paused";
    // 0.8.31: the unlocked items by name + the closest locked one and the collection tier that unlocks it
    t2 = kon ? @PKG@.VoidCompact.names(u, ci, cs0, "Mining".equals(cat) ? 40 : 60)
             : "Bought - nothing compacts here until you turn it on.";
    if (kon && "Mining".equals(cat)) t2 = t2 + " Not yet: Rubble, Sand, Crystal.";   // fixer''')
P.rep('''    if (@PKG@.VoidCompact.idxEnch(sel) >= 0)   // 0.8.30: what one Enchanted item holds
      b.set("#SkyyVSelCount.Text", "In the Void " + num(@PKG@.SackPool.get(k, sel)) + " (100 each) - on you " + num((long) @PKG@.VoidStore.countIn(inv, sel, false)));''',
      '''    if (@PKG@.VoidCompact.idxEnch(sel) >= 0)   // 0.8.30: what one Enchanted item holds
      b.set("#SkyyVSelCount.Text", "In the Void " + num(@PKG@.SackPool.get(k, sel)) + " (100 each) - on you " + num((long) @PKG@.VoidStore.countIn(inv, sel, false)));
    String cst = @PKG@.VoidCompact.stateOf(u, k, sel);   // 0.8.31: does this item auto-compact here (or what unlocks it)
    if (cst.length() > 0)
      b.set("#SkyyVSelCount.Text", "In the Void " + num(@PKG@.SackPool.get(k, sel)) + " - on you " + num((long) @PKG@.VoidStore.countIn(inv, sel, false)) + ". " + cst);''')
P.rep('''      this.info = cci < 0 ? "-Bad click" : (buyIt ? @PKG@.VoidCompact.buyAt(u, k, cci, shown) : @PKG@.VoidCompact.toggle(u, k, cci));
''', '''      this.info = cci < 0 ? "-Bad click" : (buyIt ? @PKG@.VoidCompact.buyAt(u, k, cci, shown) : @PKG@.VoidCompact.toggle(u, k, cci));
      if (this.info != null && this.info.startsWith("+")) {   // 0.8.31: bought / turned on -> compact that bag right now
        long cm = @PKG@.VoidCompact.runNow(u, k);
        if (cm > 0L) this.info = this.info + " - " + num(cm) + " Enchanted made now";
      }
''')

# ---------------------------------------------------------------- the sweep: our own thread, the watchdog, the re-read, tier-ups re-sweep
P.rep('''  Object cr = b.get("coll:recipes:" + us);
  sb.append(cr == null ? 0 : cr.hashCode()).append('|');
''', '''  Object cr = b.get("coll:recipes:" + us);
  sb.append(cr == null ? 0 : cr.hashCode()).append('|');
  Object cs = b.get("coll:" + us);   // 0.8.31: SkyyCollections' summary (tiers / recipes) - any tier-up re-sweeps (the vanilla pairs)
  sb.append(cs == null ? 0 : cs.hashCode()).append('|');
''')
P.rep('''# ================= SackTick (scheduler thread -> dispatch to world threads) =================
tick.addInterface(pool.get("java.lang.Runnable"))
''', '''# ================= 0.8.31 SackBeat: the shared-scheduler watchdog =================
# SackTick (now on SackPool.WRITER, our own thread) puts ONE SackBeat on HytaleServer.SCHEDULED_EXECUTOR - the engine's single shared
# thread - whenever the last one ran. Not run for STALL_MS = one WARN (another mod's task holds that thread; our sweep goes on), INFO back.
sbeat.addInterface(pool.get("java.lang.Runnable"))
for _f in ("public static volatile boolean QUEUED = false;", "public static volatile long SENT = 0L;", "public static volatile boolean STALLED = false;",
           "public static volatile long STALL_MS = 30000L;",
           "public static final java.util.concurrent.atomic.AtomicLong STALLS = new java.util.concurrent.atomic.AtomicLong();",
           "public static volatile long LASTRE = 0L;",   # the pd.compact.recheck clock (recheckDue)
           "public static final java.util.concurrent.atomic.AtomicLong RECHECKS = new java.util.concurrent.atomic.AtomicLong();"):
    sbeat.addField(CtField.make(_f, sbeat))
sbeat.addConstructor(CtNewConstructor.make("public SackBeat() { }", sbeat))
sbeat.addMethod(CtNewMethod.make(jt(r\'\'\'
public void run() {
  long late = System.currentTimeMillis() - SENT;
  QUEUED = false;
  if (STALLED) {
    STALLED = false;
    try { if (@PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] the server's shared scheduler runs again (after " + (late / 1000L) + " s)"); } catch (Throwable t) { }
  }
}\'\'\'), sbeat))
# true once every pd.compact.recheck seconds (SackTick: every online player's unlocked list is re-read and they are swept)
sbeat.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean recheckDue(long now) {
  int s = @PKG@.SackCfg.CMP_RECHECK;
  if (s <= 0 || !@PKG@.SackCfg.CMP_ON) return false;
  if (LASTRE == 0L) { LASTRE = now; return false; }
  if (now - LASTRE < (long) s * 1000L) return false;
  LASTRE = now;
  return true;
}\'\'\'), sbeat))
sbeat.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void check(long now) {
  if (!QUEUED) {
    QUEUED = true;
    SENT = now;
    try { com.hypixel.hytale.server.core.HytaleServer.SCHEDULED_EXECUTOR.execute(new @PKG@.SackBeat()); } catch (Throwable t) { QUEUED = false; }
    return;
  }
  if (!STALLED && now - SENT >= STALL_MS) {
    STALLED = true;
    STALLS.incrementAndGet();
    @PKG@.SackPool.warn("the server's shared scheduler (HytaleServer.SCHEDULED_EXECUTOR - ONE thread for the engine and every mod) has not run a task for " + ((now - SENT) / 1000L) + " s: another mod's task is holding it (timers on it wait). SkyySacks keeps its 2 s sweep (auto-compact, refill) on its own thread.");
  }
}\'\'\'), sbeat))

# ================= SackTick (0.8.31: on SackPool.WRITER, our own thread -> dispatch to world threads) =================
tick.addInterface(pool.get("java.lang.Runnable"))
''')
P.rep('''  try {{ {PKG}.PopupHide.tick(); }} catch (Throwable tp) {{ }}   // 0.8.16: the vanilla pickup popup switch (B1)
  try {{
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      // 0.7.18 (audit 9b): only a player with something to do costs a world hop
      java.util.UUID u0 = pr.getUuid();
''', '''  try {{ {PKG}.PopupHide.tick(); }} catch (Throwable tp) {{ }}   // 0.8.16: the vanilla pickup popup switch (B1)
  long now0 = System.currentTimeMillis();
  try {{ {PKG}.SackBeat.check(now0); }} catch (Throwable tb) {{ }}   // 0.8.31: the shared-scheduler watchdog
  boolean re = false;
  try {{ re = {PKG}.SackBeat.recheckDue(now0); }} catch (Throwable tr) {{ re = false; }}   // 0.8.31: pd.compact.recheck
  try {{
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      // 0.7.18 (audit 9b): only a player with something to do costs a world hop
      java.util.UUID u0 = pr.getUuid();
      if (re && u0 != null) {{ {PKG}.KnowSync.COLLC.remove(u0); {PKG}.SweepTask.INVDIRTY.put(u0, Boolean.TRUE); {PKG}.SackBeat.RECHECKS.incrementAndGet(); }}   // 0.8.31
''')
P.rep('''  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SackTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
''', '''  // 0.8.31: the 2 s sweep dispatcher runs on OUR thread (the shared scheduler was held by another task for 12 minutes on 10-25: no sweep, no auto-compact)
  this.ticker = {PKG}.SackPool.WRITER.scheduleAtFixedRate(new {PKG}.SackTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
''')
P.rep('''  try {{ {PKG}.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] auto-compact this run: " + {PKG}.VoidCompact.MADE.get() + " Enchanted made, " + {PKG}.VoidCompact.OPENED.get() + " opened by crafting"); }} catch (Throwable t) {{ }}   // 0.8.30''',
      '''  try {{ {PKG}.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] auto-compact this run: " + {PKG}.VoidCompact.MADE.get() + " Enchanted made, " + {PKG}.VoidCompact.OPENED.get() + " opened by crafting, " + {PKG}.SackBeat.RECHECKS.get() + " re-checks; shared scheduler stalls seen: " + {PKG}.SackBeat.STALLS.get()); }} catch (Throwable t) {{ }}   // 0.8.30 / 0.8.31''')
P.rep('''off until bought (" + {PKG}.VoidCompact.BASE.length + " Enchanted items); crafting opens Enchanted items: " + {PKG}.SackCfg.CRAFT_OPEN);''',
      '''off until bought (" + {PKG}.VoidCompact.BASE.length + " Enchanted items + " + {PKG}.VoidCompact.VBASE.length + " vanilla: Essence of Life -> Greater Essence of Life); crafting opens Enchanted items: " + {PKG}.SackCfg.CRAFT_OPEN + "; re-check every " + {PKG}.SackCfg.CMP_RECHECK + " s; the 2 s sweep on its own thread (0.8.31)");''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.31 adds no system / command"
P.finish()
