"""Derive SkyySacks/build_skyysacks_0.8.21.py from the SET pin 0.8.20 (the GENERATED build_skyysacks_0.8.20.py; edit THIS file, then
regenerate: python tools/sacks_0_8_21_patch.py; never re-run sacks_0_8_20_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.20 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_21_patch.py   then   python SkyySacks/build_skyysacks_0.8.21.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.21.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.21 (2026-10-17) = SMELTING FORTUNE in the /craft Furnace (round fortune F3, research/Metals-Tools-Fortune-Spec.md 2.2 / 2.3 / 2.4 / 5 F3).
Skyy 2026-10-17 (docs/answered/gear.md METALS BUILD DEFAULTS): "Yes, all defaults (Recommended)" incl. "Smelting Fortune on alloys too but
only on ore you mined yourself (blocks the Bazaar loop)"; Cobb's metals spec 5: Smelting Fortune = only the smelting skill tree, only the
smelt step, +10% a level, drops = 1 + floor(F) + one more with chance (F mod 1).
  1. VALUE: F = tree:fn:bonus.apply(Object[] { UUID, "Smithing.SSmelt" }) (SkyyTrees; Double, 1.0 = 100 percent; F1 makes it 0.10 a level),
     read ONCE when the units are QUEUED (procQueue) and stored on the job (ProcJob.sf) - a respec after queuing changes nothing. Only while
     the bench's key is the player's ACTIVE profile key (SackPool.pkey); no SkyyTrees / not a Number / NaN / <= 0 = no Fortune (= 0.8.20).
     SkyySacks now lists the node: tree:reads:SkyySacks = "Smithing.SSmelt" (the SkyyTrees reader contract - without it the node stays
     "coming"), published while smelt.fortune.enabled is on, removed when it is switched off and at shutdown. Critic L4: ONE writer -
     SackCfg.readsValue() builds the whole comma list of the nodes SkyySacks applies (a later node is added there, never a second put).
  2. WHICH SMELTS (ProcBench.sfKind, decided at queue time): the Furnace bench only, primary output an Ingredient_Bar_*, every input a plain
     item id (no resource type), none Skyy_Ench_*; (1) an ORE ROW = exactly one input and it is an Ore_* item; (2) an ALLOY ROW = a SkyyAlloy
     recipe (0.8.20 alloyNeed > 0) whose inputs are all Ingredient_Bar_* (smelt.fortune.alloys). Never the Tannery, Salvagebench, Enchanted
     un-compress, charcoal, cooking, totems or the Auto-Smelt Pole (none of them is a Furnace ProcBench unit).
  3. MINED-ORE BUDGET (smelt.fortune.minedOnly, default on - blocks buy ore -> smelt -> sell): per queued batch the units that get Fortune
     = what SkyySkills grants through skill:fn:oreBudget.apply(Object[] { UUID, String oreId, Integer n }) -> Integer granted (0..n; F2's
     contract, research/Metals-Tools-Fortune-Spec.md 2.3). Ore row: the input ore id, n = units x its quantity. Alloy row (builder reading of
     "only on ore you mined yourself"): each input bar's ore (the Furnace recipe that makes that bar from one Ore_* input, smallest ore id,
     cached; critic L5: x that recipe's ore per bar, rounded up) is asked in turn for what the previous one granted; critic M1: what an
     earlier ore granted above the final count is given straight back (skill:fn:oreBudget with n < 0 = give back, SkyySkills 0.4.50), so
     e.g. Bronze with Copper budget but no Tin budget burns no Copper budget; a bar without such an ore recipe = no Fortune for that alloy
     (nothing is asked). Budget is only asked when F > 0. NO bridge / not a Number / an exception = 0 granted = NO Fortune (units smelt 1:1). minedOnly
     off = every eligible unit gets Fortune. The rest of a batch smelts 1:1 in the same job (ProcJob.fu = Fortune units still to finish).
  4. THE ROLL (ProcBench.finishUnit, once per finished unit, only when that unit's output was paid): while job.fu > 0 the unit uses one of
     them (fu - 1) and rolls extras = floor(F) + (random < F - floor(F)), F clamped to smelt.fortune.guard (default 100 = most extra bars per
     unit); the extras x the primary output quantity go into the output slot as more of the SAME bar. smelt.fortune.enabled off = no roll
     (live: an emergency switch also stops units already queued). Logged per bench through the in-memory ledger sfDone -> ProcTask.drainSf ->
     crafts.log "SMELT-FORTUNE <recipe> +N extra bars"; the queue writes "SMELT-FORTUNE queued <recipe> fortune units=a/b F=..% budget=..".
  ITEM SAFETY: extras are created ONLY in finishUnit, only for a paid unit, only while fu > 0, and fu is lowered in the same synchronized
  call (fu <= count kept) - a unit is finished once (0.8.20 loop unchanged), so a unit can never roll twice; cancel returns the inputs of the
  unfinished units exactly as in 0.8.20 (their fu is dropped, no bar; critic M1: the dropped fu's mined-ore budget is given back through
  skill:fn:oreBudget n = -(fu x ore per unit) per ore, inside the synchronized cancel so once - only for fu that came from the budget,
  ProcJob.fb, saved as q.<i>.fb); unloadFuel / burnOne / Eternal Flame / the Furnace Charm / Charcoal
  ledger / Smithing XP are untouched (charm = time + fuel only). Server stop: fu / sf are saved with the job (q.<i>.sf / q.<i>.fu, only
  when fu > 0), a restart continues them; a hand-edited fu is clamped to the job's count. The no-output fallback (recipe gone) gives no
  budget back (its ore cost cannot be read any more) - never an item.
  Server Setup (Furnace and Tannery): smelt.fortune.enabled / .alloys / .minedOnly (true / true / true), smelt.fortune.guard 100 (0-1000);
  all live. Saved data: + q.<i>.sf / q.<i>.fu in Skyy_SkyySacks/processing/<pkey>.properties. No command / system / permission added.
  ROLLBACK to 0.8.20: safe - older Sacks ignores q.<i>.sf / fu (the queued units smelt 1:1, only the extras are lost), the reads flag goes.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.20.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.21.py"))
assert P.has('VERSION = "0.8.20"\n') and P.has("public static int alloyNeed(") and P.has('"acc:smelt:"'), "not the live generated SkyySacks 0.8.20"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.21 (2026-10-17)"):].rstrip() + "\n"
SF_NODE = "Smithing.SSmelt"

# ---- header, version
P.rep('''  applying, an unpaid collDone ledger is dropped at the next save (only uncredited Charcoal collection counts are lost, never items).
"""
''', '''  applying, an unpaid collDone ledger is dropped at the next save (only uncredited Charcoal collection counts are lost, never items).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.20"\n', 'VERSION = "0.8.21"\n')

# ---- config: the four Server Setup fields (SackCfg, before every reader), the file reader, the reads flag
P.rep('''scfg.addField(CtField.make("public static volatile int PICK_SHARE = 50;", scfg))
''', '''scfg.addField(CtField.make("public static volatile int PICK_SHARE = 50;", scfg))
# 0.8.21 Smelting Fortune (tools/sacks_0_8_21_patch.py): smelt.fortune.enabled / .alloys / .minedOnly / .guard (live, bound by the kit)
scfg.addField(CtField.make("public static volatile boolean SF_ON = true;", scfg))
scfg.addField(CtField.make("public static volatile boolean SF_ALLOYS = true;", scfg))
scfg.addField(CtField.make("public static volatile boolean SF_MINED = true;", scfg))
scfg.addField(CtField.make("public static volatile int SF_GUARD = 100;", scfg))
scfg.addField(CtField.make('public static final String SF_READS = "tree:reads:SkyySacks";', scfg))
scfg.addField(CtField.make("public static volatile String READS_PUT;", scfg))
scfg.addField(CtField.make('public static final String SF_NODE = "%s";', scfg))
''' % SF_NODE)
P.rep('''# 0.8.0: the live Void settings as one string (SweepTask.cfgSig: a changed row re-sweeps every player once)''', '''# 0.8.21: tree:reads:SkyySacks lists Smithing.SSmelt while Smelting Fortune is on (the SkyyTrees reader contract), removed when off.
# critic L4: ONE writer - readsValue() builds the whole comma list of every node SkyySacks applies right now (a later node adds its key
# HERE, never a second put that would overwrite this one); READS_PUT = the value we put (removed only while it is still ours)
scfg.addMethod(CtNewMethod.make("""
public static String readsValue() {
  StringBuilder sb = new StringBuilder();
  if (SF_ON) sb.append(SF_NODE);
  return sb.toString();
}""", scfg))
scfg.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void sfPub() {
  try {
    java.util.Map b = @PKG@.SackPool.bridgeW();
    String v = readsValue();
    if (v.length() > 0) { b.put(SF_READS, v); READS_PUT = v; }
    else if (READS_PUT != null) { b.remove(SF_READS, READS_PUT); READS_PUT = null; }
  } catch (Throwable t) { }
}\'\'\'), scfg))
scfg.addMethod(CtNewMethod.make("""
public static void sfUnpub() {
  try { String v = READS_PUT; if (v != null) com.skyy.sacks.SackPool.bridgeW().remove(SF_READS, v); READS_PUT = null; } catch (Throwable t) { }
}""", scfg))
scfg.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void sfKeys(java.util.Properties p, boolean first) {
  boolean on = boolKey(p, "smelt.fortune.enabled", true);
  boolean al = boolKey(p, "smelt.fortune.alloys", true);
  boolean mo = boolKey(p, "smelt.fortune.minedOnly", true);
  int g = intKey(p, "smelt.fortune.guard", 100, 0, 1000);
  boolean ch = first || on != SF_ON || al != SF_ALLOYS || mo != SF_MINED || g != SF_GUARD;
  SF_ON = on;
  SF_ALLOYS = al;
  SF_MINED = mo;
  SF_GUARD = g;
  sfPub();
  if (!ch) return;
  try { if (@PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: Smelting Fortune " + (on ? ("ON in the /craft Furnace (alloys " + (al ? "on" : "off") + ", " + (mo ? "only ore you mined yourself (skill:fn:oreBudget)" : "any ore") + ", at most " + g + " extra bars a unit)") : "OFF (smelt.fortune.enabled - every unit smelts 1:1)")); } catch (Throwable t) { }
}\'\'\'), scfg))
scfg.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void sfChanged(String key) {
  sfPub();
  try { if (@PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: " + key + " changed - Smelting Fortune " + (SF_ON ? "ON" : "OFF") + ", alloys " + SF_ALLOYS + ", mined ore only " + SF_MINED + ", guard " + SF_GUARD); } catch (Throwable t) { }
}\'\'\'), scfg))
# 0.8.0: the live Void settings as one string (SweepTask.cfgSig: a changed row re-sweeps every player once)''')
P.rep('''    pickKeys(p, first);     // 0.8.3: auto-pickup
''', '''    pickKeys(p, first);     // 0.8.3: auto-pickup
    sfKeys(p, first);       // 0.8.21: Smelting Fortune
''')

# ---- ProcJob: the snapshot (sf = Fortune as a fraction, 1.0 = 100 percent) + the units of this job that still get it (fu <= count)
P.rep('''pjob.addField(CtField.make("public String inputs;", pjob))
''', '''pjob.addField(CtField.make("public String inputs;", pjob))
pjob.addField(CtField.make("public double sf;", pjob))   # 0.8.21: Smelting Fortune read at queue time (tree:fn:bonus Smithing.SSmelt)
pjob.addField(CtField.make("public int fu;", pjob))      # 0.8.21: units of this job that still roll it (the mined-ore budget granted)
pjob.addField(CtField.make("public boolean fb;", pjob))  # critic M1: fu was taken from skill:fn:oreBudget (cancel gives it back)
''')

# ---- ProcBench: the log ledger + the Smelting Fortune helpers (after alloyNeed, before addJob / finishUnit)
P.rep('''pben.addField(CtField.make("public static final int COLL_CAP = 1000000;", pben))
''', '''pben.addField(CtField.make("public static final int COLL_CAP = 1000000;", pben))
# 0.8.21: extra bars made by Smelting Fortune per recipe since the last ProcTask pass (memory only - a crafts.log line, never an item)
pben.addField(CtField.make("public java.util.LinkedHashMap sfDone;", pben))
pben.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap ORE_OF = new java.util.concurrent.ConcurrentHashMap();", pben))
pben.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap ORE_N = new java.util.concurrent.ConcurrentHashMap();", pben))
''')
P.rep('''  if (req <= 0 || req > 5) return 5;
  return req;
}}""", pben))
''', '''  if (req <= 0 || req > 5) return 5;
  return req;
}}""", pben))
# 0.8.21 SMELTING FORTUNE (tools/sacks_0_8_21_patch.py docstring 2): 0 = none, 1 = an ore row (one Ore_* input), 2 = an alloy row (bars)
pben.addMethod(CtNewMethod.make(f"""
public static int sfKind({CRR} r, String bench) {{
  if (r == null || !{PKG}.SackCfg.SF_ON || !"Furnace".equalsIgnoreCase(bench)) return 0;
  {MQ} po = r.getPrimaryOutput();
  String oid = po == null ? null : po.getItemId();
  if (oid == null || !oid.startsWith("Ingredient_Bar_")) return 0;
  {MQ}[] in = r.getInput();
  if (in == null || in.length == 0) return 0;
  int ore = 0;
  int bar = 0;
  for (int i = 0; i < in.length; i++) {{
    if (in[i] == null || in[i].getItemId() == null) return 0;   // a resource-type input: never
    String id = in[i].getItemId();
    if (id.startsWith("Skyy_Ench_")) return 0;
    if (id.startsWith("Ore_")) ore++;
    else if (id.startsWith("Ingredient_Bar_")) bar++;
    else return 0;
  }}
  if (alloyNeed(r) > 0) return {PKG}.SackCfg.SF_ALLOYS && ore == 0 && bar == in.length ? 2 : 0;
  return in.length == 1 && ore == 1 ? 1 : 0;
}}""", pben))
# the ore a bar is smelted from (the Furnace recipe making it from exactly one Ore_* input; smallest ore id); null = none
pben.addMethod(CtNewMethod.make(f"""
public static String oreOfBar(String bar) {{
  if (bar == null) return null;
  Object c = ORE_OF.get(bar);
  if (c instanceof String) return ((String) c).length() == 0 ? null : (String) c;
  String best = null;
  int bestN = 1;
  try {{
    java.util.Iterator it = {CRR}.getAssetMap().getAssetMap().values().iterator();
    while (it.hasNext()) {{
      Object o = it.next();
      if (!(o instanceof {CRR})) continue;
      {CRR} r = ({CRR}) o;
      {MQ} po = r.getPrimaryOutput();
      if (po == null || !bar.equals(po.getItemId())) continue;
      {MQ}[] in = r.getInput();
      if (in == null || in.length != 1 || in[0] == null || in[0].getItemId() == null || !in[0].getItemId().startsWith("Ore_")) continue;
      {BRQ}[] br = r.getBenchRequirement();
      boolean fur = false;
      for (int i = 0; br != null && i < br.length; i++) if (br[i] != null && br[i].id != null && br[i].id.equalsIgnoreCase("Furnace")) fur = true;
      if (!fur) continue;
      String id = in[0].getItemId();
      if (best == null || id.compareTo(best) < 0) {{
        best = id;
        int q = in[0].getQuantity(); if (q <= 0) q = 1;
        int oq = po.getQuantity(); if (oq <= 0) oq = 1;
        bestN = (q + oq - 1) / oq;   // critic L5: ore per bar (rounded up - never fewer ore than the bar cost)
      }}
    }}
  }} catch (Throwable t) {{ return null; }}
  if (best != null) ORE_N.put(bar, Integer.valueOf(bestN));
  ORE_OF.put(bar, best == null ? "" : best);
  return best;
}}""", pben))
pben.addMethod(CtNewMethod.make("""
public static int oreQtyOfBar(String bar) {
  if (oreOfBar(bar) == null) return 0;
  Object n = ORE_N.get(bar);
  return n instanceof Integer && ((Integer) n).intValue() > 0 ? ((Integer) n).intValue() : 1;
}""", pben))
# F = tree:fn:bonus("Smithing.SSmelt") of u, only for its ACTIVE profile key k; 0 = none (no SkyyTrees, not a Number, NaN, <= 0)
pben.addMethod(CtNewMethod.make(f"""
public static double sfValue(java.util.UUID u, String k) {{
  if (u == null || k == null) return 0.0;
  try {{
    if (!k.equals({PKG}.SackPool.pkey(u))) return 0.0;
    Object f = {PKG}.SackPool.bridge().get("tree:fn:bonus");
    if (!(f instanceof java.util.function.Function)) return 0.0;
    Object r = ((java.util.function.Function) f).apply(new Object[] {{ u, {PKG}.SackCfg.SF_NODE }});
    if (!(r instanceof Number)) return 0.0;
    double v = ((Number) r).doubleValue();
    if (Double.isNaN(v) || v <= 0.0) return 0.0;
    if (v > 1000.0) v = 1000.0;
    return v;
  }} catch (Throwable t) {{ return 0.0; }}
}}""", pben))
# skill:fn:oreBudget (SkyySkills F2): { UUID, oreId, Integer n } -> granted 0..n; anything else = 0 (no bridge = NO Fortune)
pben.addMethod(CtNewMethod.make(f"""
public static int sfBudget(java.util.UUID u, String ore, int n) {{
  if (u == null || ore == null || n <= 0) return 0;
  try {{
    Object f = {PKG}.SackPool.bridge().get("skill:fn:oreBudget");
    if (!(f instanceof java.util.function.Function)) return 0;
    Object r = ((java.util.function.Function) f).apply(new Object[] {{ u, ore, Integer.valueOf(n) }});
    if (!(r instanceof Number)) return 0;
    long g = ((Number) r).longValue();
    if (g <= 0L) return 0;
    return g > (long) n ? n : (int) g;
  }} catch (Throwable t) {{ return 0; }}
}}""", pben))
# critic M1: give `n` ore of budget back (skill:fn:oreBudget with -n; SkyySkills 0.4.50 adds it back); no bridge = nothing to give
pben.addMethod(CtNewMethod.make(f"""
public static void sfGive(java.util.UUID u, String ore, int n) {{
  if (u == null || ore == null || n <= 0) return;
  try {{
    Object f = {PKG}.SackPool.bridge().get("skill:fn:oreBudget");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(new Object[] {{ u, ore, Integer.valueOf(-n) }});
  }} catch (Throwable t) {{ }}
}}""", pben))
# the ores one unit of r costs: {String[] ore ids, int[] ore per unit}; alloys = each bar's ore x its ore-per-bar (critic L5); null = none
pben.addMethod(CtNewMethod.make(f"""
public static Object[] sfOres({CRR} r, boolean alloy) {{
  if (r == null) return null;
  {MQ}[] in = r.getInput();
  if (in == null || in.length == 0) return null;
  String[] ores = new String[in.length];
  int[] per = new int[in.length];
  for (int i = 0; i < in.length; i++) {{
    if (in[i] == null || in[i].getItemId() == null) return null;
    int q = in[i].getQuantity(); if (q <= 0) q = 1;
    if (!alloy) {{ ores[i] = in[i].getItemId(); per[i] = q; }}
    else {{
      ores[i] = oreOfBar(in[i].getItemId());
      if (ores[i] == null) return null;   // a bar with no ore recipe
      per[i] = q * oreQtyOfBar(in[i].getItemId());
    }}
  }}
  return new Object[] {{ ores, per }};
}}""", pben))
# the units of a batch of `done` that get Fortune: all of them (mined off) or what the mined-ore budget grants (docstring 3).
# critic M1: whatever an earlier ore granted above the final count (a later ore was short) is given straight back
pben.addMethod(CtNewMethod.make(f"""
public static int sfGrant({CRR} r, int kind, java.util.UUID u, int done, boolean mined) {{
  if (r == null || kind <= 0 || done <= 0) return 0;
  if (!mined) return done;
  Object[] o = sfOres(r, kind == 2);
  if (o == null) return 0;   // nothing asked
  String[] ores = (String[]) o[0];
  int[] per = (int[]) o[1];
  int[] took = new int[ores.length];
  int g = done;
  for (int i = 0; i < ores.length && g > 0; i++) {{
    took[i] = sfBudget(u, ores[i], g * per[i]);
    g = took[i] / per[i];
  }}
  if (g < 0) g = 0;
  for (int i = 0; i < ores.length; i++) {{
    int back = took[i] - g * per[i];
    if (back > 0) sfGive(u, ores[i], back);
  }}
  return g;
}}""", pben))
# critic M1: give back the budget of `fu` units of recipe id rid (cancel); returns the ore given back
pben.addMethod(CtNewMethod.make(f"""
public static int sfRefund(java.util.UUID u, String rid, int fu) {{
  if (u == null || rid == null || fu <= 0) return 0;
  try {{
    Object ro = {CRR}.getAssetMap().getAsset(rid);
    if (!(ro instanceof {CRR})) return 0;
    {CRR} r = ({CRR}) ro;
    Object[] o = sfOres(r, alloyNeed(r) > 0);
    if (o == null) return 0;
    String[] ores = (String[]) o[0];
    int[] per = (int[]) o[1];
    int n = 0;
    for (int i = 0; i < ores.length; i++) {{ sfGive(u, ores[i], fu * per[i]); n += fu * per[i]; }}
    return n;
  }} catch (Throwable t) {{ return 0; }}
}}""", pben))
# extras of one unit: floor(F) + (roll < F mod 1), F and the result clamped to smelt.fortune.guard
pben.addMethod(CtNewMethod.make(f"""
public static int sfExtras(double f, double roll) {{
  int g = {PKG}.SackCfg.SF_GUARD;
  if (g <= 0 || !(f > 0.0)) return 0;
  if (f > (double) g) f = (double) g;
  double w = Math.floor(f);
  int x = (int) w;
  if (roll < f - w) x++;
  return x > g ? g : x;
}}""", pben))
''')

# ---- constructor: the log ledger
P.rep('''  this.collDone = new java.util.LinkedHashMap();
  this.needsFuel = benchNeedsFuel(bench);''', '''  this.collDone = new java.util.LinkedHashMap();
  this.sfDone = new java.util.LinkedHashMap();
  this.needsFuel = benchNeedsFuel(bench);''')

# ---- addJob -> addJobF (the snapshot + the Fortune units; a merge only with the same snapshot)
P.rep('''public synchronized void addJob(String recipe, int count, long unitMs, String inputs, long now) {{
  if (recipe == null || count <= 0) return;
  String in = inputs == null ? "" : inputs;
  if (this.queue.isEmpty()) {{ this.progress = 0L; this.clock = now; }}
  {PKG}.ProcJob last = null;
  if (!this.queue.isEmpty()) last = ({PKG}.ProcJob) this.queue.get(this.queue.size() - 1);
  if (last != null && last.recipe.equals(recipe) && last.unitMs == unitMs && last.inputs.equals(in)) last.count = last.count + count;
  else this.queue.add(new {PKG}.ProcJob(recipe, count, unitMs, in));
}}""", pben))''', '''public synchronized void addJobF(String recipe, int count, long unitMs, String inputs, long now, double sf, int fu, boolean fb) {{
  if (recipe == null || count <= 0) return;
  String in = inputs == null ? "" : inputs;
  if (fu < 0 || !(sf > 0.0)) fu = 0;
  if (fu > count) fu = count;
  if (fu == 0) {{ sf = 0.0; fb = false; }}
  if (this.queue.isEmpty()) {{ this.progress = 0L; this.clock = now; }}
  {PKG}.ProcJob last = null;
  if (!this.queue.isEmpty()) last = ({PKG}.ProcJob) this.queue.get(this.queue.size() - 1);
  // 0.8.21: a merge keeps one snapshot per job (both without Fortune units, or the same F)
  if (last != null && last.recipe.equals(recipe) && last.unitMs == unitMs && last.inputs.equals(in)
      && (fu == 0 || last.fu <= 0 || (last.sf == sf && last.fb == fb))) {{
    last.count = last.count + count;
    if (fu > 0) {{ last.sf = sf; last.fb = fb; last.fu = last.fu + fu; }}
  }} else {{
    {PKG}.ProcJob nj = new {PKG}.ProcJob(recipe, count, unitMs, in);
    nj.sf = sf; nj.fu = fu; nj.fb = fb;
    this.queue.add(nj);
  }}
}}""", pben))
pben.addMethod(CtNewMethod.make("""
public void addJob(String recipe, int count, long unitMs, String inputs, long now) { addJobF(recipe, count, unitMs, inputs, now, 0.0, 0, false); }""", pben))''')

# ---- finishUnit: the roll (paid units only, once per unit, while fu > 0)
P.rep('''        int n = outs[k].getQuantity(); if (n <= 0) n = 1;
        addTo(this.out, outs[k].getItemId(), n);
        paid = true;
      }}
    }}
  }} catch (Throwable t) {{ }}''', '''        int n = outs[k].getQuantity(); if (n <= 0) n = 1;
        addTo(this.out, outs[k].getItemId(), n);
        paid = true;
      }}
      // 0.8.21 SMELTING FORTUNE: one Fortune unit used per paid unit; extras = more of the same bar (docstring 4)
      if (paid && j.fu > 0 && "Furnace".equalsIgnoreCase(this.bench)) {{
        j.fu = j.fu - 1;
        String pid = prim == null ? null : prim.getItemId();
        if ({PKG}.SackCfg.SF_ON && pid != null && pid.startsWith("Ingredient_Bar_")) {{
          int x = sfExtras(j.sf, java.util.concurrent.ThreadLocalRandom.current().nextDouble());
          if (x > 0) {{
            int pq = prim.getQuantity(); if (pq <= 0) pq = 1;
            addTo(this.out, pid, x * pq);
            Integer sd = (Integer) this.sfDone.get(j.recipe);
            if (sd == null || sd.intValue() < 1000000) addTo(this.sfDone, j.recipe, x * pq);
          }}
        }}
      }}
    }}
  }} catch (Throwable t) {{ }}''')
P.rep('''  j.count = j.count - 1;
  if (j.count <= 0) this.queue.remove(0);''', '''  j.count = j.count - 1;
  if (j.fu > j.count) j.fu = j.count < 0 ? 0 : j.count;   // 0.8.21: fu <= count (the no-output fallback uses none)
  if (j.count <= 0) this.queue.remove(0);''')
# the log ledger, taken and cleared in one call (ProcTask.drainSf)
P.rep('''pben.addMethod(CtNewMethod.make("""
public synchronized void takeColl(String id, int n) {''', '''pben.addMethod(CtNewMethod.make("""
public synchronized java.util.ArrayList sfTake() {
  java.util.ArrayList l = new java.util.ArrayList();
  java.util.Iterator it = this.sfDone.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    l.add(new Object[] { e.getKey(), e.getValue() });
  }
  this.sfDone.clear();
  return l;
}""", pben))
pben.addMethod(CtNewMethod.make("""
public synchronized void takeColl(String id, int n) {''')

# ---- critic M1: cancel gives the cancelled Fortune units' mined-ore budget back (inside the synchronized cancel - once; fu cleared)
P.rep('''    if (j.count <= 0) continue;
    parseInto(this.out, j.inputs, j.count);
    n += j.count;
  }}
  this.queue.clear();''', '''    if (j.count <= 0) continue;
    parseInto(this.out, j.inputs, j.count);
    n += j.count;
    if (j.fu > 0 && j.fb && this.key != null && this.key.length() >= 36) {{
      try {{ sfRefund(java.util.UUID.fromString(this.key.substring(0, 36)), j.recipe, j.fu); }} catch (Throwable t) {{ }}
    }}
    j.fu = 0;
  }}
  this.queue.clear();''')

# ---- describe: the head job's Fortune on the running line
P.rep('''    d[1] = verb + outName(h.recipe) + " - " + state + " - whole queue " + dur(queueMs());''',
      '''    d[1] = verb + outName(h.recipe) + " - " + state + " - whole queue " + dur(queueMs());
    if (h.fu > 0) d[1] = d[1] + " - Smelting Fortune " + Math.round(h.sf * 100.0) + " percent on " + h.fu + " of them";   // 0.8.21''')

# ---- saved: q.<i>.sf / q.<i>.fu (only with Fortune units left)
P.rep('''    p.setProperty(b + "q." + i + ".inputs", j.inputs);
''', '''    p.setProperty(b + "q." + i + ".inputs", j.inputs);
    if (j.fu > 0) {{ p.setProperty(b + "q." + i + ".sf", String.valueOf(j.sf)); p.setProperty(b + "q." + i + ".fu", String.valueOf(j.fu)); if (j.fb) p.setProperty(b + "q." + i + ".fb", "1"); }}
''')
P.rep('''    if (r != null && c > 0) this.queue.add(new {PKG}.ProcJob(r, c, um, in));
''', '''    if (r != null && c > 0) {{
      {PKG}.ProcJob lj = new {PKG}.ProcJob(r, c, um, in);
      int lfu = (int) pl(p, b + "q." + i + ".fu");   // 0.8.21: Fortune units left (clamped 0..count)
      double lsf = 0.0;
      try {{ String sv = p.getProperty(b + "q." + i + ".sf"); if (sv != null) lsf = Double.parseDouble(sv.trim()); }} catch (Throwable t) {{ lsf = 0.0; }}
      if (Double.isNaN(lsf) || lsf <= 0.0 || lfu <= 0) {{ lsf = 0.0; lfu = 0; }}
      if (lsf > 1000.0) lsf = 1000.0;
      if (lfu > c) lfu = c;
      lj.sf = lsf; lj.fu = lfu;
      lj.fb = lfu > 0 && "1".equals(p.getProperty(b + "q." + i + ".fb"));   // critic M1: only budget-taken units are given back
      this.queue.add(lj);
    }}
''')

# ---- procQueue: the snapshot + the budget per batch, the log line, the player's message
P.rep('''  long unit = {PKG}.ProcBench.unitMs(r, bench, tier);
  int queuedN = 0; int guard = 0;
  StringBuilder audit = new StringBuilder();''', '''  long unit = {PKG}.ProcBench.unitMs(r, bench, tier);
  // 0.8.21 SMELTING FORTUNE: which smelt (sfKind), F read ONCE now (sfValue), the mined-ore budget per batch below (sfGrant)
  int sfk = res ? 0 : {PKG}.ProcBench.sfKind(r, bench);
  java.util.UUID su = null;
  double sfv = 0.0;
  if (sfk > 0) {{
    try {{ su = java.util.UUID.fromString(k.substring(0, 36)); }} catch (Throwable tu) {{ su = null; }}
    sfv = {PKG}.ProcBench.sfValue(su, k);
  }}
  int sfu = 0;
  boolean sfm = {PKG}.SackCfg.SF_MINED;   // one reading for the whole click (the grant + the job's give-back flag)
  int queuedN = 0; int guard = 0;
  StringBuilder audit = new StringBuilder();''')
P.rep('''    pb.addJob(String.valueOf(r.getId()), done, unit, unitInputs, now);
    queuedN += done;''', '''    int fu = sfv > 0.0 ? {PKG}.ProcBench.sfGrant(r, sfk, su, done, sfm) : 0;   // 0.8.21: after the items were taken, never before
    sfu += fu;
    pb.addJobF(String.valueOf(r.getId()), done, unit, unitInputs, now, sfv, fu, sfm);
    queuedN += done;''')
P.rep('''  {MQ} outq = r.getPrimaryOutput();
  String nm = pretty(outq == null ? String.valueOf(r.getId()) : outq.getItemId());
  if (queuedN <= 0) return "could not take the materials - nothing was used";
  return "queued " + queuedN + " x " + nm + " in the " + bench + (queuedN < qty ? " (" + (qty - queuedN) + " fewer than asked - the rest was returned)" : "") + (consumed > 0 ? " - " + consumed + " from the Void" : "");''',
      '''  if (sfk > 0 && sfv > 0.0 && queuedN > 0) {PKG}.CraftLog.line(k, "SMELT-FORTUNE queued " + r.getId() + " fortune units=" + sfu + "/" + queuedN + " F=" + Math.round(sfv * 100.0) + "% budget=" + (sfm ? "mined ore (skill:fn:oreBudget " + ({PKG}.SackPool.bridge().get("skill:fn:oreBudget") != null ? "found" : "MISSING - no Fortune") + ")" : "off - every unit"));
  {MQ} outq = r.getPrimaryOutput();
  String nm = pretty(outq == null ? String.valueOf(r.getId()) : outq.getItemId());
  if (queuedN <= 0) return "could not take the materials - nothing was used";
  String sfMsg = "";   // 0.8.21
  if (sfu > 0) sfMsg = " - Smelting Fortune " + Math.round(sfv * 100.0) + " percent on " + sfu + (sfu < queuedN ? " of them (ore you mined yourself)" : "");
  else if (sfk > 0 && sfv > 0.0) sfMsg = " - no Smelting Fortune (only ore you mined yourself counts)";
  return "queued " + queuedN + " x " + nm + " in the " + bench + (queuedN < qty ? " (" + (qty - queuedN) + " fewer than asked - the rest was returned)" : "") + (consumed > 0 ? " - " + consumed + " from the Void" : "") + sfMsg;''')

# ---- ProcTask: the SMELT-FORTUNE result lines
P.rep('''# 0.8.20: one pass over the ledger with coll:fn:add `f` (no lock of ours held during the call); returns the count credited, -1 = refused /''',
      '''# 0.8.21: the Smelting Fortune extras of this bench since the last pass -> crafts.log (queued, written by the SackSaver)
ptk.addMethod(CtNewMethod.make(f"""
public static void drainSf(String k, {PKG}.ProcBench pb) {{
  java.util.ArrayList l = pb.sfTake();
  for (int i = 0; i < l.size(); i++) {{
    Object[] e = (Object[]) l.get(i);
    {PKG}.CraftLog.later(k, "SMELT-FORTUNE " + e[0] + " +" + e[1] + " extra bars");
  }}
}}""", ptk))
# 0.8.20: one pass over the ledger with coll:fn:add `f` (no lock of ours held during the call); returns the count credited, -1 = refused /''')
P.rep('''      if (fo instanceof {PKG}.ProcBench) {{ drainXp(u, k, ({PKG}.ProcBench) fo); drainColl(u, k, ({PKG}.ProcBench) fo); }}''',
      '''      if (fo instanceof {PKG}.ProcBench) {{ drainXp(u, k, ({PKG}.ProcBench) fo); drainColl(u, k, ({PKG}.ProcBench) fo); drainSf(k, ({PKG}.ProcBench) fo); }}''')

# ---- Server Setup rows (Furnace and Tannery) + the template lines of a new config.properties
P.rep('''] + ["#%s=%d" % (k, d) for (k, _f, d, _lo, _hi) in _BENCH_KEYS]
SACK_CFG_TEXT = ''', '''] + ["#%s=%d" % (k, d) for (k, _f, d, _lo, _hi) in _BENCH_KEYS] + [
    "# Smelting Fortune (the Smithing tree's Smelting Fortune node): extra bars when a player smelts ore (and alloys) in the /craft Furnace.",
    "# minedOnly=true: only for ore that player mined themselves (SkyySkills keeps the count). guard = most extra bars a unit.",
    "#smelt.fortune.enabled=true", "#smelt.fortune.alloys=true", "#smelt.fortune.minedOnly=true", "#smelt.fortune.guard=100"]
SACK_CFG_TEXT = ''')
P.rep('''SACK_CFG_ROWS += PICK_ROWS
''', '''SACK_CFG_ROWS += PICK_ROWS
# 0.8.21 Smelting Fortune (research/Metals-Tools-Fortune-Spec.md 2.4): all live - procQueue / finishUnit read the SackCfg fields
SF_ROWS = [
    ("smelt.fortune.enabled", "Smelting Fortune", "benches", "bool", "true", "", "", "", "", "live",
     "On: the Smithing tree's Smelting Fortune gives extra bars in the /craft Furnace. Off: every bar 1:1.",
     "field:SackCfg.SF_ON@config.properties:smelt.fortune.enabled;after=SackCfg.sfChanged"),
    ("smelt.fortune.alloys", "Smelting Fortune on alloys", "benches", "bool", "true", "", "", "", "", "live",
     "On: alloy bars (Bronze, Dusk ...) can roll extra bars too. Off: ore to bar only.",
     "field:SackCfg.SF_ALLOYS@config.properties:smelt.fortune.alloys;after=SackCfg.sfChanged"),
    ("smelt.fortune.minedOnly", "Only on ore you mined yourself", "benches", "bool", "true", "", "", "", "", "live",
     "On: Fortune only for ore the player mined (blocks buy ore, smelt, sell). Off: any ore.",
     "field:SackCfg.SF_MINED@config.properties:smelt.fortune.minedOnly;after=SackCfg.sfChanged"),
    ("smelt.fortune.guard", "Most extra bars per unit", "benches", "int", "100", "0", "1000", "", "", "live,adv",
     "Safety limit on extra bars one smelted unit can give. 0 = Smelting Fortune never gives any.",
     "field:SackCfg.SF_GUARD@config.properties:smelt.fortune.guard;after=SackCfg.sfChanged"),
]
for _r in SF_ROWS:
    assert len(_r[1]) <= 40 and len(_r[10]) <= 100, (_r[0], len(_r[1]), len(_r[10]))
SACK_CFG_ROWS += SF_ROWS
''')

# ---- shutdown: the reads flag goes
P.rep('''  try {{ {PKG}.CfgPub.shutdown(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] auto-pickup this run: "''',
      '''  try {{ {PKG}.CfgPub.shutdown(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackCfg.sfUnpub(); }} catch (Throwable t) {{ }}   // 0.8.21: tree:reads:SkyySacks
  try {{ {PKG}.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] auto-pickup this run: "''')
# ---- the ready line names it
P.rep('''the Void's Deposit all fills every bag; " + {PKG}.PdOnce.statusText());''',
      '''the Void's Deposit all fills every bag; Smelting Fortune " + ({PKG}.SackCfg.SF_ON ? "on" : "OFF") + " (tree:fn:bonus Smithing.SSmelt, skill:fn:oreBudget " + ({PKG}.SackCfg.SF_MINED ? "required" : "off") + "); " + {PKG}.PdOnce.statusText());''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.21 adds no system / command"
P.finish()
