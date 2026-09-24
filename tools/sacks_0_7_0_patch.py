"""Derive SkyySacks/build_skyysacks_0.7.0.py from 0.6.8.
0.7.0 (Skyy 2026-09-23: "keep the furnace and tannery as accessories, but have it open a furnace you have to load things into and
take time like normal, instead of instant crafting. keep alchemy its own thing, but combine all the other work benches into one
crafting tab."):
 - craft page tabs:  < Back to bags | Crafting | Alchemy | Furnace | Tannery | Collections
     Crafting    = every Fieldcraft recipe + every equipped bench accessory's recipes up to its tier, EXCEPT Alchemybench, Furnace
                   and Tannery (Workbench, Armor, Weapon, Cooking, Farming, Furniture, Loom, Arcane, Campfire, Salvage... merged, instant).
     Alchemy     = Alchemybench recipes up to tier, instant (only with an Alchemybench accessory equipped).
     Furnace /   = TIMED processing (only with the accessory equipped, or while that bench still holds queued items / outputs / fuel):
     Tannery       queue a recipe x N -> inputs leave inventory + magic bags (count-verified) and wait in the queue; each unit takes the
                   recipe's TimeSeconds * (1 - the bench tier's CraftingTimeReductionModifier) (exact vanilla formula, tier = accessory
                   tier at queue time); the Furnace burns fuel like the vanilla one (items with ResourceType "Fuel", FuelQuality = burn
                   seconds per item, ExtraOutput charcoal every PerFuelItemsConsumed non-ignored fuel items); the Tannery needs no fuel
                   (its vanilla bench has no fuel slot). Finished items wait in the output slot until Collect (storage first, only
                   what fits, the rest stays). Cancel moves every unfinished unit's inputs to the output slot and collects.
                   Time is wall-clock: queues keep running while the page is closed, while offline and across restarts
                   (state = per-bench clock + progress; the simulation is replayed on next tick/open), persisted atomically in
                   Skyy_SkyySacks/processing/<uuid>.properties. Every queue/fuel/collect/cancel/unload/done is logged to crafts.log.
     Collections = unchanged.
 - BagMirror.sync is now idempotent (records what it already deducted). 0.6.8 deducted bag-sourced craft inputs twice: once right
   after removeMaterials and again in the rebuild's materials() call.
 - OpenCustomUI page ids SkyySacksCraft / SkyySacksFurnace / SkyySacksTannery / SkyySacksAlchemy open the craft page on that tab
   (for a future right-click on the accessory items; nothing uses them yet).
 - review fixes (2026-09-23):
   * instant crafts (Crafting + Alchemy tabs) pay by the literal removed-items diff (CraftPage.reserve): any surplus goes back as the
     very items that were taken, resource-type inputs ("any Wood_Trunk", "any Rock") included - 0.6.8 logged those "LOST".
   * Furnace/Tannery clicks never write to disk on the world thread: CraftPage.saveSoon marks ProcStore dirty and runs SackSaver on the
     scheduler thread right away. SackSaver flushes ProcStore BEFORE SackPool; SackPool.save is serialized on SackPool.SAVELOCK.
   * ProcBench.config remembers a failed Bench lookup for 30s only (no session-long "no bench"); advance() re-reads needsFuel while it
     is false, so a lookup that missed during startup heals by itself.
   * ProcBench.advance finishes a unit whose time already ran in full before it asks for more fuel.
   * accessories() warns once per acc:has id whose bench has no recipes (e.g. a literal Skyy_Accessory_Omni; SkyyAccessories 0.4
     publishes the Omni expanded into one Skyy_Accessory_<Bench>_T<max> entry per bench, which needs no change here).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.6.8.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.0.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:90])
    s = s.replace(old, new, count)


def after(anchor, text):
    rep(anchor, anchor + text)


def before(anchor, text):
    rep(anchor, text + anchor)


def replace_cpg_method(sig, new_block):
    """Replace the whole cpg.addMethod(...) block whose Java source starts with `sig`."""
    global s
    head = 'cpg.addMethod(CtNewMethod.make(f"""' + LF + sig
    assert s.count(head) == 1, "method head not unique: " + sig
    a = s.index(head)
    tail = '}}""", cpg))' + LF
    b = s.index(tail, a) + len(tail)
    s = s[:a] + new_block + s[b:]


# ---------------------------------------------------------------- version + docstring
rep('VERSION = "0.6.8"', 'VERSION = "0.7.0"')
after('failures logged. 0.1.4: self-test join grant removed (sweep + page verified in-game 2026-09-22).' + LF,
      '0.7.0: craft tabs Crafting | Alchemy | Furnace | Tannery | Collections; Furnace/Tannery are timed processing queues with fuel,' + LF +
      'offline progress and an output slot (Skyy_SkyySacks/processing/<uuid>.properties); BagMirror.sync idempotent (no double bag deduction).' + LF)

# ---------------------------------------------------------------- engine constants + probes
after('OCU = "com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction"' + LF, r'''PB  = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.ProcessingBench"
PEO = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.ProcessingBench$ExtraOutput"
BEN = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.Bench"
BTL = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.BenchTierLevel"
BLT = "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType"
ITM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
IRT = "com.hypixel.hytale.protocol.ItemResourceType"
PGM = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"
''')
after('    B.probe(pool, c, m)' + LF, r'''for c, m in ((CRR, "getTimeSeconds"), (PB, "getExtraOutput"), (PB, "getFuel"), (BEN, "getTierLevel"), (BTL, "getCraftingTimeReductionModifier"),
             (BLT, "getBench"), (ITM, "getFuelQuality"), (ITM, "getResourceTypes"), (PEO, "isIgnoredFuelSource"), (PEO, "getPerFuelItemsConsumed"),
             (PAGE, "sendUpdate"), (PGM, "getCustomPage"), (UCB, "set"), (IC, "getCapacity"), (IC, "getMatchingResourceType"),
             (MQ, "isItemExcluded"), (MQ, "getResourceTypeId")):
    B.probe(pool, c, m)
''')

# ---------------------------------------------------------------- new classes
before('pl   = pool.makeClass(PKG + ".SkyySacksPlugin", pool.get(JP))' + LF, r'''pjob = pool.makeClass(PKG + ".ProcJob")
pben = pool.makeClass(PKG + ".ProcBench")
pst  = pool.makeClass(PKG + ".ProcStore")
ptk  = pool.makeClass(PKG + ".ProcTask")
ptick= pool.makeClass(PKG + ".ProcTick")
cfac = pool.makeClass(PKG + ".CraftPageFactory")
''')

# ---------------------------------------------------------------- ProcJob / ProcBench / ProcStore (before SweepTask; SackSaver uses ProcStore)
PROC = r'''# ================= Processing (0.7.0): timed Furnace / Tannery queues - our own per-player state, no block entity =================
# ProcJob = one queue entry: <count> units of <recipe>, each taking <unitMs>, each unit paid with <inputs> ("ItemId*qty;ItemId*qty").
pjob.addField(CtField.make("public String recipe;", pjob))
pjob.addField(CtField.make("public int count;", pjob))
pjob.addField(CtField.make("public long unitMs;", pjob))
pjob.addField(CtField.make("public String inputs;", pjob))
pjob.addConstructor(CtNewConstructor.make("""
public ProcJob(String recipe, int count, long unitMs, String inputs) {
  this.recipe = recipe; this.count = count; this.unitMs = unitMs; this.inputs = inputs == null ? "" : inputs;
}""", pjob))

# ProcBench = one player's Furnace or Tannery. Wall-clock simulation: advance(now) replays the time since `clock`.
pben.addField(CtField.make("public static final int QUEUE_CAP = 256;", pben))
pben.addField(CtField.make("public static final int FUEL_CAP = 1000;", pben))
pben.addField(CtField.make("public static final int OUT_CAP = 20000;", pben))
pben.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CFG = new java.util.concurrent.ConcurrentHashMap();", pben))
pben.addField(CtField.make("public static java.util.ArrayList FUELS;", pben))
pben.addField(CtField.make("public String bench;", pben))
pben.addField(CtField.make("public long clock;", pben))
pben.addField(CtField.make("public long progress;", pben))
pben.addField(CtField.make("public long fuelMs;", pben))
pben.addField(CtField.make("public int extra;", pben))
pben.addField(CtField.make("public long finished;", pben))
pben.addField(CtField.make("public boolean needsFuel;", pben))
pben.addField(CtField.make("public boolean warnedFuel;", pben))
pben.addField(CtField.make("public java.util.ArrayList queue;", pben))
pben.addField(CtField.make("public java.util.LinkedHashMap fuel;", pben))
pben.addField(CtField.make("public java.util.LinkedHashMap out;", pben))
pben.addMethod(CtNewMethod.make("""
public static String nm(String id) {
  if (id == null) return "?";
  String s = id.replace('_', ' ');
  int q = s.indexOf(':');
  if (q >= 0 && q + 1 < s.length()) s = s.substring(q + 1);
  return s;
}""", pben))
pben.addMethod(CtNewMethod.make("""
public static String roman(int t) {
  String[] r = new String[] { "", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X" };
  if (t >= 0 && t < r.length) return r[t];
  return "T" + t;
}""", pben))
pben.addMethod(CtNewMethod.make("""
public static String dur(long ms) {
  if (ms < 0L) ms = 0L;
  long s = (ms + 999L) / 1000L;
  if (s < 60L) return s + "s";
  long m = s / 60L; s = s % 60L;
  if (m < 60L) return m + "m " + s + "s";
  long h = m / 60L; m = m % 60L;
  return h + "h " + m + "m";
}""", pben))
# the vanilla ProcessingBench config (Bench_Furnace.json / Bench_Tannery.json BlockType.Bench), found by Bench.Id.
# Only a hit is cached for good; a miss or a failed scan is remembered for 30s only (review fix), so a lookup made before the
# BlockType assets finished loading heals by itself instead of disabling fuel and tier speed until the next restart.
pben.addMethod(CtNewMethod.make(f"""
public static {PB} config(String bench) {{
  if (bench == null) return null;
  String key = bench.toLowerCase();
  Object c = CFG.get(key);
  if (c instanceof {PB}) return ({PB}) c;
  if (c instanceof Long && System.currentTimeMillis() - ((Long) c).longValue() < 30000L) return null;
  {PB} found = null;
  try {{
    java.util.Iterator it = {BLT}.getAssetMap().getAssetMap().values().iterator();
    while (it.hasNext()) {{
      Object o = it.next();
      if (!(o instanceof {BLT})) continue;
      {BEN} b = (({BLT}) o).getBench();
      if (b == null || !(b instanceof {PB})) continue;
      String bid = b.getId();
      if (bid != null && bid.equalsIgnoreCase(bench)) {{ found = ({PB}) b; break; }}
    }}
  }} catch (Throwable t) {{
    CFG.put(key, Long.valueOf(System.currentTimeMillis()));
    {PKG}.SackPool.warn("processing: bench lookup failed for " + bench + " (retry in 30s): " + t);
    return null;
  }}
  if (found == null) CFG.put(key, Long.valueOf(System.currentTimeMillis())); else CFG.put(key, found);
  return found;
}}""", pben))
# vanilla ProcessingBenchBlock.getRecipeTimeSeconds: time - time * tierLevel.CraftingTimeReductionModifier
pben.addMethod(CtNewMethod.make(f"""
public static float reduction(String bench, int tier) {{
  if (tier <= 0) return 0.0f;
  {PB} c = config(bench);
  if (c == null) return 0.0f;
  {BTL} tl = null;
  for (int t = tier; t >= 1 && tl == null; t--) tl = c.getTierLevel(t);
  if (tl == null) return 0.0f;
  float r = tl.getCraftingTimeReductionModifier();
  if (r < 0.0f) r = 0.0f;
  if (r > 0.95f) r = 0.95f;
  return r;
}}""", pben))
pben.addMethod(CtNewMethod.make(f"""
public static long unitMs({CRR} r, String bench, int tier) {{
  double t = (double) r.getTimeSeconds();
  if (t < 0.0) t = 0.0;
  double red = (double) reduction(bench, tier);
  long v = Math.round((t - t * red) * 1000.0);
  return v < 0L ? 0L : v;
}}""", pben))
pben.addMethod(CtNewMethod.make(f"""
public static boolean benchNeedsFuel(String bench) {{
  {PB} c = config(bench);
  if (c == null) return false;
  Object[] f = c.getFuel();
  return f != null && f.length > 0;
}}""", pben))
pben.addMethod(CtNewMethod.make(f"""
public static {ITM} item(String id) {{
  if (id == null) return null;
  try {{ Object o = {ITM}.getAssetMap().getAsset(id); if (o instanceof {ITM}) return ({ITM}) o; }} catch (Throwable t) {{ }}
  return null;
}}""", pben))
# vanilla fuel slot = ResourceTypeId "Fuel"; ProcessingBenchBlock.consumeOneFuel adds consumed * Item.getFuelQuality() seconds
pben.addMethod(CtNewMethod.make(f"""
public static double fuelQualityOf({ITM} it) {{
  if (it == null) return 0.0;
  {IRT}[] rts = it.getResourceTypes();
  boolean fuel = false;
  for (int i = 0; rts != null && i < rts.length; i++) if (rts[i] != null && "Fuel".equals(rts[i].id)) fuel = true;
  if (!fuel) return 0.0;
  double q = it.getFuelQuality();
  return q > 0.0 ? q : 0.0;
}}""", pben))
pben.addMethod(CtNewMethod.make(f"""
public static double fuelQuality(String id) {{
  return fuelQualityOf(item(id));
}}""", pben))
pben.addMethod(CtNewMethod.make(f"""
public static synchronized java.util.ArrayList fuels() {{
  if (FUELS != null) return FUELS;
  java.util.ArrayList out = new java.util.ArrayList();
  try {{
    java.util.Iterator it = {ITM}.getAssetMap().getAssetMap().values().iterator();
    while (it.hasNext()) {{
      Object o = it.next();
      if (!(o instanceof {ITM})) continue;
      if (fuelQualityOf(({ITM}) o) > 0.0) out.add(String.valueOf((({ITM}) o).getId()));
    }}
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("processing: fuel scan failed: " + t); return out; }}
  java.util.Collections.sort(out);
  FUELS = out;
  return out;
}}""", pben))
pben.addMethod(CtNewMethod.make("""
public static void addTo(java.util.LinkedHashMap m, String id, int n) {
  if (id == null || n <= 0) return;
  Integer cur = (Integer) m.get(id);
  long v = (long) (cur == null ? 0 : cur.intValue()) + (long) n;
  if (v > 2000000000L) v = 2000000000L;
  m.put(id, Integer.valueOf((int) v));
}""", pben))
pben.addMethod(CtNewMethod.make("""
public static int total(java.util.LinkedHashMap m) {
  long t = 0L;
  java.util.Iterator it = m.values().iterator();
  while (it.hasNext()) t += (long) ((Integer) it.next()).intValue();
  return t > 2000000000L ? 2000000000 : (int) t;
}""", pben))
pben.addMethod(CtNewMethod.make("""
public static String ser(java.util.Map m) {
  StringBuilder sb = new StringBuilder();
  java.util.Iterator it = m.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (sb.length() > 0) sb.append(';');
    sb.append((String) e.getKey()).append('*').append(((Integer) e.getValue()).intValue());
  }
  return sb.toString();
}""", pben))
pben.addMethod(CtNewMethod.make("""
public static void parseInto(java.util.LinkedHashMap m, String s, int mult) {
  if (s == null || mult <= 0) return;
  String[] parts = s.split(";");
  for (int i = 0; i < parts.length; i++) {
    String p = parts[i].trim();
    int star = p.lastIndexOf('*');
    if (star <= 0) continue;
    try {
      long v = (long) Integer.parseInt(p.substring(star + 1).trim()) * (long) mult;
      if (v > 2000000000L) v = 2000000000L;
      addTo(m, p.substring(0, star), (int) v);
    } catch (Throwable t) { }
  }
}""", pben))
pben.addMethod(CtNewMethod.make("""
public static long pl(java.util.Properties p, String k) {
  try { String v = p.getProperty(k); return v == null ? 0L : Long.parseLong(v.trim()); } catch (Throwable t) { return 0L; }
}""", pben))
pben.addMethod(CtNewMethod.make(f"""
public static String outName(String recipeId) {{
  try {{
    Object o = {CRR}.getAssetMap().getAsset(recipeId);
    if (o instanceof {CRR}) {{ {MQ} q = (({CRR}) o).getPrimaryOutput(); if (q != null && q.getItemId() != null) return nm(q.getItemId()); }}
  }} catch (Throwable t) {{ }}
  return nm(recipeId);
}}""", pben))
pben.addConstructor(CtNewConstructor.make("""
public ProcBench(String bench) {
  this.bench = bench;
  this.clock = 0L; this.progress = 0L; this.fuelMs = 0L; this.extra = 0; this.finished = 0L;
  this.queue = new java.util.ArrayList();
  this.fuel = new java.util.LinkedHashMap();
  this.out = new java.util.LinkedHashMap();
  this.needsFuel = benchNeedsFuel(bench);
  this.warnedFuel = false;
}""", pben))
pben.addMethod(CtNewMethod.make(f"""
public synchronized int queued() {{
  int n = 0;
  for (int i = 0; i < this.queue.size(); i++) n += (({PKG}.ProcJob) this.queue.get(i)).count;
  return n;
}}""", pben))
pben.addMethod(CtNewMethod.make("""
public synchronized int outTotal() { return total(this.out); }""", pben))
pben.addMethod(CtNewMethod.make("""
public synchronized int fuelCount() { return total(this.fuel); }""", pben))
pben.addMethod(CtNewMethod.make("""
public synchronized boolean pending() { return !this.queue.isEmpty() || !this.out.isEmpty() || !this.fuel.isEmpty(); }""", pben))
pben.addMethod(CtNewMethod.make("""
public synchronized boolean fuelWarnOnce() {
  if (!this.needsFuel || this.queue.isEmpty() || this.fuelMs > 0L || !this.fuel.isEmpty() || this.warnedFuel) return false;
  this.warnedFuel = true;
  return true;
}""", pben))
pben.addMethod(CtNewMethod.make("""
public synchronized void addOut(String id, int n) { addTo(this.out, id, n); }""", pben))
pben.addMethod(CtNewMethod.make("""
public synchronized void addFuel(String id, int n) { addTo(this.fuel, id, n); this.warnedFuel = false; }""", pben))
pben.addMethod(CtNewMethod.make(f"""
public synchronized void addJob(String recipe, int count, long unitMs, String inputs, long now) {{
  if (recipe == null || count <= 0) return;
  String in = inputs == null ? "" : inputs;
  if (this.queue.isEmpty()) {{ this.progress = 0L; this.clock = now; }}
  {PKG}.ProcJob last = null;
  if (!this.queue.isEmpty()) last = ({PKG}.ProcJob) this.queue.get(this.queue.size() - 1);
  if (last != null && last.recipe.equals(recipe) && last.unitMs == unitMs && last.inputs.equals(in)) last.count = last.count + count;
  else this.queue.add(new {PKG}.ProcJob(recipe, count, unitMs, in));
}}""", pben))
# light the next fuel item (vanilla consumeOneFuel incl. the ExtraOutput byproduct); false = no fuel left
pben.addMethod(CtNewMethod.make(f"""
public synchronized boolean burnOne() {{
  int guard = 0;
  while (!this.fuel.isEmpty() && guard < 100000) {{
    guard++;
    java.util.Map.Entry e = (java.util.Map.Entry) this.fuel.entrySet().iterator().next();
    String id = (String) e.getKey();
    int q = ((Integer) e.getValue()).intValue();
    if (q <= 1) this.fuel.remove(id); else this.fuel.put(id, Integer.valueOf(q - 1));
    if (q <= 0) continue;
    double fq = fuelQuality(id);
    if (fq <= 0.0) {{ addTo(this.out, id, 1); continue; }}
    this.fuelMs = this.fuelMs + Math.round(fq * 1000.0);
    try {{
      {PB} c = config(this.bench);
      {PEO} eo = null;
      if (c != null) eo = c.getExtraOutput();
      {ITM} itm = item(id);
      if (eo != null && itm != null && !eo.isIgnoredFuelSource(itm)) {{
        this.extra = this.extra + 1;
        int per = eo.getPerFuelItemsConsumed(); if (per <= 0) per = 1;
        if (this.extra >= per) {{
          this.extra = 0;
          {MQ}[] outs = eo.getOutputs();
          for (int i = 0; outs != null && i < outs.length; i++) {{
            if (outs[i] == null || outs[i].getItemId() == null) continue;
            int n = outs[i].getQuantity(); if (n <= 0) n = 1;
            addTo(this.out, outs[i].getItemId(), n);
          }}
        }}
      }}
    }} catch (Throwable t) {{ }}
    return true;
  }}
  return false;
}}""", pben))
pben.addMethod(CtNewMethod.make(f"""
public synchronized void finishUnit({PKG}.ProcJob j) {{
  boolean paid = false;
  try {{
    Object ro = {CRR}.getAssetMap().getAsset(j.recipe);
    if (ro instanceof {CRR}) {{
      {CRR} r = ({CRR}) ro;
      {MQ}[] outs = r.getOutputs();
      {MQ} prim = r.getPrimaryOutput();
      if ((outs == null || outs.length == 0) && prim != null) outs = new {MQ}[] {{ prim }};
      for (int k = 0; outs != null && k < outs.length; k++) {{
        if (outs[k] == null || outs[k].getItemId() == null) continue;
        int n = outs[k].getQuantity(); if (n <= 0) n = 1;
        addTo(this.out, outs[k].getItemId(), n);
        paid = true;
      }}
    }}
  }} catch (Throwable t) {{ }}
  if (!paid) {{
    parseInto(this.out, j.inputs, 1);
    {PKG}.SackPool.warn("processing: recipe " + j.recipe + " has no item output any more - its inputs went to the output slot");
  }}
  j.count = j.count - 1;
  if (j.count <= 0) this.queue.remove(0);
  this.progress = 0L;
  this.finished = this.finished + 1L;
}}""", pben))
# replay wall-clock time since `clock`; fuel burns only while a unit is processing; returns units finished
pben.addMethod(CtNewMethod.make(f"""
public synchronized int advance(long now) {{
  if (!this.needsFuel) this.needsFuel = benchNeedsFuel(this.bench);
  if (this.clock <= 0L) this.clock = now;
  long dt = now - this.clock;
  if (dt < 0L) dt = 0L;
  this.clock = now;
  int done = 0;
  int guard = 0;
  while (!this.queue.isEmpty() && guard < 500000) {{
    guard++;
    {PKG}.ProcJob j = ({PKG}.ProcJob) this.queue.get(0);
    if (j.count <= 0) {{ this.queue.remove(0); this.progress = 0L; continue; }}
    if (total(this.out) >= OUT_CAP) break;
    long need = j.unitMs - this.progress;
    // review fix: a unit whose time already ran in full (its last fuel ran out on that same step) finishes without lighting more fuel
    if (need <= 0L && j.unitMs > 0L) {{ finishUnit(j); done++; continue; }}
    if (this.needsFuel && this.fuelMs <= 0L && !burnOne()) break;
    if (need <= 0L) {{ finishUnit(j); done++; continue; }}
    if (dt <= 0L) break;
    long step = dt < need ? dt : need;
    if (this.needsFuel) {{
      if (step > this.fuelMs) step = this.fuelMs;
      this.fuelMs = this.fuelMs - step;
    }}
    this.progress = this.progress + step;
    dt = dt - step;
  }}
  if (this.queue.isEmpty()) this.progress = 0L;
  return done;
}}""", pben))
# cancel: every unfinished unit's inputs (the running one included) go to the output slot; returns units cancelled
pben.addMethod(CtNewMethod.make(f"""
public synchronized int cancel() {{
  int n = 0;
  for (int i = 0; i < this.queue.size(); i++) {{
    {PKG}.ProcJob j = ({PKG}.ProcJob) this.queue.get(i);
    if (j.count <= 0) continue;
    parseInto(this.out, j.inputs, j.count);
    n += j.count;
  }}
  this.queue.clear();
  this.progress = 0L;
  return n;
}}""", pben))
pben.addMethod(CtNewMethod.make("""
public synchronized int unloadFuel() {
  int n = total(this.fuel);
  java.util.Iterator it = this.fuel.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    addTo(this.out, (String) e.getKey(), ((Integer) e.getValue()).intValue());
  }
  this.fuel.clear();
  return n;
}""", pben))
pben.addMethod(CtNewMethod.make("""
public synchronized java.util.ArrayList outList() {
  java.util.ArrayList l = new java.util.ArrayList();
  java.util.Iterator it = this.out.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    l.add(new Object[] { e.getKey(), e.getValue() });
  }
  return l;
}""", pben))
pben.addMethod(CtNewMethod.make("""
public synchronized void takeOut(String id, int n) {
  if (id == null || n <= 0) return;
  Integer cur = (Integer) this.out.get(id);
  if (cur == null) return;
  int v = cur.intValue() - n;
  if (v <= 0) this.out.remove(id); else this.out.put(id, Integer.valueOf(v));
}""", pben))
pben.addMethod(CtNewMethod.make(f"""
public synchronized long queueMs() {{
  long t = 0L;
  for (int i = 0; i < this.queue.size(); i++) {{
    {PKG}.ProcJob j = ({PKG}.ProcJob) this.queue.get(i);
    t += j.unitMs * (long) j.count;
  }}
  t -= this.progress;
  return t < 0L ? 0L : t;
}}""", pben))
pben.addMethod(CtNewMethod.make("""
public synchronized long fuelTotalMs() {
  long t = this.fuelMs;
  java.util.Iterator it = this.fuel.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    t += Math.round(fuelQuality((String) e.getKey()) * 1000.0) * (long) ((Integer) e.getValue()).intValue();
  }
  return t;
}""", pben))
# UI text (no , : ; { } " so inline and set() show the same): [0] bench/tier/fuel, [1] running unit, [2] queue, [3] output slot, [4] percent
pben.addMethod(CtNewMethod.make(f"""
public synchronized String[] describe(int tier, boolean equipped) {{
  String[] d = new String[5];
  StringBuilder s0 = new StringBuilder();
  s0.append(this.bench);
  if (tier > 0) s0.append(" ").append(roman(tier));
  float red = reduction(this.bench, tier);
  if (red > 0.0f) s0.append(" - ").append(Math.round(red * 100.0f)).append(" percent faster");
  if (!equipped) s0.append(" - accessory not equipped (queued items still finish)");
  if (this.needsFuel) s0.append(" - fuel ").append(dur(fuelTotalMs())).append(" (").append(total(this.fuel)).append(" items loaded)");
  else s0.append(" - needs no fuel");
  d[0] = s0.toString();
  int pct = 0;
  if (this.queue.isEmpty()) d[1] = "Idle - queue something below";
  else {{
    {PKG}.ProcJob h = ({PKG}.ProcJob) this.queue.get(0);
    long left = h.unitMs - this.progress; if (left < 0L) left = 0L;
    if (h.unitMs > 0L) pct = (int) ((this.progress * 100L) / h.unitMs);
    if (pct > 100) pct = 100;
    if (pct < 0) pct = 0;
    String verb = "Processing ";
    if ("Furnace".equalsIgnoreCase(this.bench)) verb = "Smelting ";
    if ("Tannery".equalsIgnoreCase(this.bench)) verb = "Tanning ";
    String state = dur(left) + " left";
    if (total(this.out) >= OUT_CAP) state = "OUTPUT FULL - collect to continue";
    else if (this.needsFuel && this.fuelMs <= 0L && this.fuel.isEmpty()) state = "OUT OF FUEL - load fuel to continue";
    d[1] = verb + outName(h.recipe) + " - " + state + " - whole queue " + dur(queueMs());
  }}
  StringBuilder s2 = new StringBuilder("Queue - ");
  if (this.queue.isEmpty()) s2.append("empty");
  for (int i = 0; i < this.queue.size() && i < 4; i++) {{
    {PKG}.ProcJob j = ({PKG}.ProcJob) this.queue.get(i);
    if (i > 0) s2.append(" + ");
    s2.append(outName(j.recipe)).append(" x").append(j.count);
  }}
  if (this.queue.size() > 4) s2.append(" + ").append(this.queue.size() - 4).append(" more");
  s2.append("   (").append(queued()).append(" / ").append(QUEUE_CAP).append(" units)");
  d[2] = s2.toString();
  StringBuilder s3 = new StringBuilder("Ready - ");
  if (this.out.isEmpty()) s3.append("nothing yet");
  int k = 0;
  java.util.Iterator it = this.out.entrySet().iterator();
  while (it.hasNext()) {{
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (k == 5) {{ s3.append(" + more"); break; }}
    if (k > 0) s3.append(" + ");
    s3.append(((Integer) e.getValue()).intValue()).append(" ").append(nm((String) e.getKey()));
    k++;
  }}
  d[3] = s3.toString();
  d[4] = String.valueOf(pct);
  return d;
}}""", pben))
pben.addMethod(CtNewMethod.make(f"""
public synchronized void toProps(java.util.Properties p) {{
  String b = this.bench + ".";
  p.setProperty(b + "clock", String.valueOf(this.clock));
  p.setProperty(b + "progress", String.valueOf(this.progress));
  p.setProperty(b + "fuelMs", String.valueOf(this.fuelMs));
  p.setProperty(b + "extra", String.valueOf(this.extra));
  p.setProperty(b + "finished", String.valueOf(this.finished));
  p.setProperty(b + "fuel", ser(this.fuel));
  p.setProperty(b + "out", ser(this.out));
  p.setProperty(b + "q.n", String.valueOf(this.queue.size()));
  for (int i = 0; i < this.queue.size(); i++) {{
    {PKG}.ProcJob j = ({PKG}.ProcJob) this.queue.get(i);
    p.setProperty(b + "q." + i + ".recipe", j.recipe);
    p.setProperty(b + "q." + i + ".count", String.valueOf(j.count));
    p.setProperty(b + "q." + i + ".unitMs", String.valueOf(j.unitMs));
    p.setProperty(b + "q." + i + ".inputs", j.inputs);
  }}
}}""", pben))
pben.addMethod(CtNewMethod.make(f"""
public synchronized void fromProps(java.util.Properties p) {{
  String b = this.bench + ".";
  this.clock = pl(p, b + "clock");
  this.progress = pl(p, b + "progress"); if (this.progress < 0L) this.progress = 0L;
  this.fuelMs = pl(p, b + "fuelMs"); if (this.fuelMs < 0L) this.fuelMs = 0L;
  this.extra = (int) pl(p, b + "extra");
  this.finished = pl(p, b + "finished");
  this.fuel.clear(); parseInto(this.fuel, p.getProperty(b + "fuel"), 1);
  this.out.clear(); parseInto(this.out, p.getProperty(b + "out"), 1);
  this.queue.clear();
  int n = (int) pl(p, b + "q.n");
  for (int i = 0; i < n && i < 100000; i++) {{
    String r = p.getProperty(b + "q." + i + ".recipe");
    int c = (int) pl(p, b + "q." + i + ".count");
    long um = pl(p, b + "q." + i + ".unitMs"); if (um < 0L) um = 0L;
    String in = p.getProperty(b + "q." + i + ".inputs");
    if (r != null && c > 0) this.queue.add(new {PKG}.ProcJob(r, c, um, in));
  }}
}}""", pben))

# ProcStore = per-player benches, persisted in Skyy_SkyySacks/processing/<uuid>.properties (tmp + fsync + atomic move)
pst.addField(CtField.make("public static java.nio.file.Path DIR;", pst))
pst.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap STATES = new java.util.concurrent.ConcurrentHashMap();", pst))
pst.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();", pst))
pst.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BROKEN = new java.util.concurrent.ConcurrentHashMap();", pst))
pst.addField(CtField.make('public static final String[] BENCHES = new String[] { "Furnace", "Tannery" };', pst))
pst.addMethod(CtNewMethod.make(f"""
public static synchronized java.util.Map load(java.util.UUID u) {{
  java.util.Map m = (java.util.Map) STATES.get(u);
  if (m != null) return m;
  m = new java.util.concurrent.ConcurrentHashMap();
  java.nio.file.Path f = DIR == null ? null : DIR.resolve(u.toString() + ".properties");
  try {{
    if (f != null && java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {{
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try {{ p.load(in); }} finally {{ in.close(); }}
      for (int i = 0; i < BENCHES.length; i++) {{
        if (p.getProperty(BENCHES[i] + ".clock") == null) continue;
        {PKG}.ProcBench pb = new {PKG}.ProcBench(BENCHES[i]);
        pb.fromProps(p);
        m.put(BENCHES[i], pb);
      }}
    }}
  }} catch (Throwable t) {{
    BROKEN.put(u, Boolean.TRUE);
    {PKG}.SackPool.warn("processing: could not read " + f + " - left untouched, furnace/tannery disabled for " + u + " until restart: " + t);
  }}
  STATES.put(u, m);
  return m;
}}""", pst))
pst.addMethod(CtNewMethod.make(f"""
public static java.util.Map all(java.util.UUID u) {{
  java.util.Map m = (java.util.Map) STATES.get(u);
  return m != null ? m : load(u);
}}""", pst))
pst.addMethod(CtNewMethod.make(f"""
public static {PKG}.ProcBench get(java.util.UUID u, String bench) {{
  if (u == null || bench == null) return null;
  return ({PKG}.ProcBench) all(u).get(bench);
}}""", pst))
pst.addMethod(CtNewMethod.make(f"""
public static {PKG}.ProcBench of(java.util.UUID u, String bench) {{
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) all(u);
  {PKG}.ProcBench pb = ({PKG}.ProcBench) m.get(bench);
  if (pb != null) return pb;
  pb = new {PKG}.ProcBench(bench);
  pb.clock = System.currentTimeMillis();
  Object prev = m.putIfAbsent(bench, pb);
  return prev != null ? ({PKG}.ProcBench) prev : pb;
}}""", pst))
pst.addMethod(CtNewMethod.make(f"""
public static boolean pending(java.util.UUID u, String bench) {{
  {PKG}.ProcBench pb = get(u, bench);
  return pb != null && pb.pending();
}}""", pst))
pst.addMethod(CtNewMethod.make("""
public static void markDirty(java.util.UUID u) { DIRTY.put(u, Boolean.TRUE); }""", pst))
pst.addMethod(CtNewMethod.make(f"""
public static synchronized boolean save(java.util.UUID u) {{
  if (u == null || DIR == null || BROKEN.containsKey(u)) return false;
  java.util.Map m = (java.util.Map) STATES.get(u);
  if (m == null) return false;
  DIRTY.remove(u);
  try {{
    java.util.Properties p = new java.util.Properties();
    p.setProperty("version", "1");
    java.util.Iterator it = m.values().iterator();
    while (it.hasNext()) {{ {PKG}.ProcBench pb = ({PKG}.ProcBench) it.next(); pb.toProps(p); }}
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(u.toString() + ".properties.tmp");
    java.nio.file.Path dst = DIR.resolve(u.toString() + ".properties");
    java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
    try {{ p.store(out, "SkyySacks processing - Furnace/Tannery queues, fuel and output slots"); out.flush(); out.getFD().sync(); }} finally {{ out.close(); }}
    try {{ java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] {{ java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }}); }}
    catch (Throwable am) {{ java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] {{ java.nio.file.StandardCopyOption.REPLACE_EXISTING }}); }}
    return true;
  }} catch (Throwable t) {{
    DIRTY.put(u, Boolean.TRUE);
    {PKG}.SackPool.warn("processing: could not save " + u + ": " + t);
    return false;
  }}
}}""", pst))
pst.addMethod(CtNewMethod.make("""
public static void flushDirty() {
  java.util.Iterator it = DIRTY.keySet().iterator();
  while (it.hasNext()) {
    java.util.UUID u = (java.util.UUID) it.next();
    save(u);
  }
}""", pst))

'''
before('# ================= SweepTask (runs ON world thread; no disk I/O) =================' + LF, PROC)

# ---------------------------------------------------------------- SackSaver also flushes processing state
# review fix: ProcStore FIRST, then SackPool (persistence-ordering rule: a crash between the two can duplicate queued inputs, never lose
# them). SackSaver is also the one-shot flush CraftPage.saveSoon runs on the scheduler thread after every Furnace/Tannery click.
rep('  try {{ {PKG}.SackPool.flushDirty(); }} catch (Throwable t) {{ }}' + LF + '}}""", sav))',
    '  try {{ {PKG}.ProcStore.flushDirty(); }} catch (Throwable t) {{ }}' + LF +
    '  try {{ {PKG}.SackPool.flushDirty(); }} catch (Throwable t) {{ }}' + LF + '}}""", sav))')

# ---------------------------------------------------------------- SackPool.save serialized (review fix)
# saves now also run on the scheduler thread after Furnace/Tannery clicks while the world thread still saves after instant crafts;
# both write <uuid>.properties.tmp, so one writer at a time on SAVELOCK (a separate lock: SackPool.add never waits on the disk).
after('sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap EXEMPT = new java.util.concurrent.ConcurrentHashMap();", sp))' + LF,
      'sp.addField(CtField.make("public static final Object SAVELOCK = new Object();", sp))' + LF)
rep('sp.addMethod(CtNewMethod.make("""' + LF + 'public static void save(java.util.UUID u) {' + LF + '  try {' + LF,
    'sp.addMethod(CtNewMethod.make("""' + LF + 'public static void saveNow(java.util.UUID u) {' + LF + '  try {' + LF)
after('  } catch (Throwable t) { warn("could not save pool for " + u + ": " + t); }' + LF + '}""", sp))' + LF,
      'sp.addMethod(CtNewMethod.make("""' + LF + 'public static void save(java.util.UUID u) {' + LF +
      '  synchronized (SAVELOCK) { saveNow(u); }' + LF + '}""", sp))' + LF)

# ---------------------------------------------------------------- CraftLog.line (free-form audit line)
after('}""", clog))' + LF, r'''clog.addMethod(CtNewMethod.make("""
public static synchronized void line(java.util.UUID u, String text) {
  try {
    if (FILE == null) return;
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    String l = new java.util.Date().toString() + " " + u + " " + text + System.lineSeparator();
    java.nio.file.Files.write(FILE, l.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { }
}""", clog))
''')

# ---------------------------------------------------------------- BagMirror.sync idempotent (fixes the 0.6.8 double deduction)
rep('if (actual < this.slotQty[i]) {{ int d = this.slotQty[i] - actual; {PKG}.SackPool.add(u, this.slotIds[i], -(long) d); consumed += d; }}',
    'if (actual < this.slotQty[i]) {{ int d = this.slotQty[i] - actual; {PKG}.SackPool.add(u, this.slotIds[i], -(long) d); consumed += d; this.slotQty[i] = actual; }}')

# ---------------------------------------------------------------- CraftPage fields for the live processing view
after('cpg.addField(CtField.make("public java.util.ArrayList tabs;", cpg))' + LF, r'''cpg.addField(CtField.make("public boolean liveOn;", cpg))
cpg.addField(CtField.make("public String liveSig;", cpg))
cpg.addField(CtField.make("public long liveAt;", cpg))
cpg.addField(CtField.make("public String[] fuelIds;", cpg))
cpg.addField(CtField.make("public static java.util.HashSet BENCHIDS;", cpg))
cpg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap ACCWARN = new java.util.concurrent.ConcurrentHashMap();", cpg))
''')

# ---------------------------------------------------------------- accessories(): warn once per acc:has id whose bench has no recipes (review fix)
# SkyyAccessories 0.4 publishes the Omni EXPANDED (one Skyy_Accessory_<Bench>_T<max> per bench, never the Omni id itself), so nothing here
# parses it; if a literal Skyy_Accessory_Omni (or any id naming no crafting bench) ever shows up, the log says why it unlocks nothing.
# BENCHIDS = every BenchRequirement.id in the recipe assets (lower case), built once; an empty or failed scan is not cached (never warns).
before('# accessory item ids the player carries anywhere -> bench ids granted' + LF, r'''cpg.addMethod(CtNewMethod.make(f"""
public static synchronized boolean knownBench(String bench) {{
  if (bench == null) return false;
  if (BENCHIDS == null) {{
    java.util.HashSet s = new java.util.HashSet();
    try {{
      java.util.Iterator it = {CRR}.getAssetMap().getAssetMap().values().iterator();
      while (it.hasNext()) {{
        {CRR} r = ({CRR}) it.next();
        {BRQ}[] br = r.getBenchRequirement();
        for (int i = 0; br != null && i < br.length; i++) if (br[i] != null && br[i].id != null) s.add(br[i].id.toLowerCase());
      }}
    }} catch (Throwable t) {{ return true; }}
    if (s.isEmpty()) return true;
    BENCHIDS = s;
  }}
  return BENCHIDS.contains(bench.toLowerCase());
}}""", cpg))
''')
after('    if (bench.length() == 0) continue;' + LF,
      '    if (!knownBench(bench) && ACCWARN.putIfAbsent(id, Boolean.TRUE) == null) {PKG}.SackPool.warn("accessory " + id + " in acc:has names no crafting bench (" + bench + ") - it unlocks nothing; the Omni must be published as one Skyy_Accessory_<Bench>_T<n> entry per bench");' + LF)

# ---------------------------------------------------------------- benchRecipes(u, String only) + helpers
replace_cpg_method('public static java.util.TreeSet benchRecipes(java.util.UUID u, boolean processing) {{', r'''cpg.addMethod(CtNewMethod.make("""
public static int accTier(java.util.HashMap acc, String bench) {
  int best = 0;
  if (acc == null || bench == null) return 0;
  java.util.Iterator ki = acc.keySet().iterator();
  while (ki.hasNext()) {
    String k = (String) ki.next();
    if (k.equalsIgnoreCase(bench)) { int t = ((Integer) acc.get(k)).intValue(); if (t > best) best = t; }
  }
  return best;
}""", cpg))
# benches with their own tab (not merged into Crafting)
cpg.addMethod(CtNewMethod.make("""
public static boolean separateBench(String id) {
  return id != null && (id.equalsIgnoreCase("Alchemybench") || id.equalsIgnoreCase("Furnace") || id.equalsIgnoreCase("Tannery"));
}""", cpg))
# only == null -> every equipped bench except the separate ones (the merged Crafting tab); else just that bench. Up to the accessory tier.
cpg.addMethod(CtNewMethod.make(f"""
public static java.util.TreeSet benchRecipes(java.util.UUID u, String only) {{
  java.util.TreeSet ids = new java.util.TreeSet();
  java.util.HashMap acc = accessories(({PLA}) null, u);
  if (acc.isEmpty()) return ids;
  java.util.Iterator it = {CRR}.getAssetMap().getAssetMap().values().iterator();
  while (it.hasNext()) {{
    {CRR} r = ({CRR}) it.next();
    {BRQ}[] br = r.getBenchRequirement();
    if (br == null) continue;
    for (int i = 0; i < br.length; i++) {{
      if (br[i] == null || br[i].id == null) continue;
      if (only == null) {{ if (separateBench(br[i].id)) continue; }}
      else if (!only.equalsIgnoreCase(br[i].id)) continue;
      int tier = accTier(acc, br[i].id);
      if (tier <= 0) continue;
      int need = br[i].requiredTierLevel; if (need <= 0) need = 1;
      if (need <= tier) {{ ids.add(r.getId()); break; }}
    }}
  }}
  return ids;
}}""", cpg))
''')

# ---------------------------------------------------------------- tabs: Crafting | Alchemy | Furnace | Tannery | Collections
replace_cpg_method('public java.util.ArrayList buildTabs({PLA} p, java.util.UUID u) {{', r'''cpg.addMethod(CtNewMethod.make(f"""
public java.util.ArrayList buildTabs({PLA} p, java.util.UUID u) {{
  java.util.ArrayList t = new java.util.ArrayList();
  java.util.HashMap acc = accessories(p, u);
  t.add(new String[] {{ "A:craft", "Crafting" }});
  if (accTier(acc, "Alchemybench") > 0) t.add(new String[] {{ "A:alch", "Alchemy" }});
  for (int i = 0; i < {PKG}.ProcStore.BENCHES.length; i++) {{
    String bn = {PKG}.ProcStore.BENCHES[i];
    if (accTier(acc, bn) > 0 || {PKG}.ProcStore.pending(u, bn)) t.add(new String[] {{ "P:" + bn, bn }});
  }}
  if (!collectionRecipes(u).isEmpty()) t.add(new String[] {{ "C:", "Collections" }});
  return t;
}}""", cpg))
''')

rep('    ids.addAll(benchRecipes(u, false));' + LF + '  }} else if (tabId.equals("A:proc")) {{' + LF + '    ids.addAll(benchRecipes(u, true));' + LF,
    '    ids.addAll(benchRecipes(u, (String) null));' + LF + '  }} else if (tabId.equals("A:alch")) {{' + LF +
    '    ids.addAll(benchRecipes(u, "Alchemybench"));' + LF + '  }} else if (tabId.startsWith("P:")) {{' + LF +
    '    ids.addAll(benchRecipes(u, tabId.substring(2)));' + LF)

# ---------------------------------------------------------------- processing actions + view (before CraftPage.build)
PROCPAGE = r'''# ---- 0.7.0 processing helpers (Furnace / Tannery tabs) ----
cpg.addMethod(CtNewMethod.make(f"""
public static java.util.HashMap snapshot({IC} c) {{
  java.util.HashMap m = new java.util.HashMap();
  short cap = c.getCapacity();
  for (short s = 0; s < cap; s++) {{
    {IS} it = c.getItemStack(s);
    if (it == null || it.isEmpty()) continue;
    String id = it.getItemId();
    if (id == null) continue;
    Integer cur = (Integer) m.get(id);
    m.put(id, Integer.valueOf((cur == null ? 0 : cur.intValue()) + it.getQuantity()));
  }}
  return m;
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static int countItem({IC} c, String id) {{
  int n = 0;
  short cap = c.getCapacity();
  for (short s = 0; s < cap; s++) {{
    {IS} it = c.getItemStack(s);
    if (it == null || it.isEmpty()) continue;
    if (id.equals(it.getItemId())) n += it.getQuantity();
  }}
  return n;
}}""", cpg))
cpg.addMethod(CtNewMethod.make("""
public static java.util.LinkedHashMap removedItems(java.util.HashMap before, java.util.HashMap after) {
  java.util.LinkedHashMap d = new java.util.LinkedHashMap();
  java.util.Iterator it = before.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    int b0 = ((Integer) e.getValue()).intValue();
    Integer a = (Integer) after.get(e.getKey());
    int a0 = a == null ? 0 : a.intValue();
    if (b0 > a0) d.put(e.getKey(), Integer.valueOf(b0 - a0));
  }
  return d;
}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static void giveBack({ST} st, {REF} ref, {PLA} p, String id, int n) {{
  if (id == null || n <= 0) return;
  {SIC}.addOrDropItemStack(st, ref, p.getInventory().getCombinedStorageHotbarBackpack(), new {IS}(id, n));
}}""", cpg))
# review fix: Furnace/Tannery clicks never touch the disk on the world thread. Mark dirty (cheap) and run the SackSaver the 10s timer uses
# on the scheduler thread right away (ProcStore first, then SackPool - BagMirror.sync already marked the pool dirty); only when the
# scheduler refuses the task (server shutting down) is it run inline.
cpg.addMethod(CtNewMethod.make(f"""
public static void saveSoon(java.util.UUID u) {{
  {PKG}.ProcStore.markDirty(u);
  try {{ {HSV}.SCHEDULED_EXECUTOR.execute(new {PKG}.SackSaver()); }}
  catch (Throwable t) {{ new {PKG}.SackSaver().run(); }}
}}""", cpg))
# units of resource type `rt` one `id` item counts for (the engine's own ItemContainer.getMatchingResourceType + its quantity); 0 = not that type
cpg.addMethod(CtNewMethod.make(f"""
public static int rtUnits(String id, String rt) {{
  if (id == null || rt == null) return 0;
  try {{
    {ITM} it = {PKG}.ProcBench.item(id);
    if (it == null) return 0;
    {IRT} m = {IC}.getMatchingResourceType(it, rt);
    return m == null ? 0 : m.quantity;
  }} catch (Throwable t) {{ return 0; }}
}}""", cpg))
# review fix (instant crafts): what is left of the literally removed items `took` after paying `done` crafts of `inputs` (per[i] each), or
# null when they do not cover `done` crafts. Exact item ids first, then resource types (whole items, counted in the engine's units), then
# any other material kind from what is left. Whatever is left is surplus and goes back as exactly those items - nothing is "LOST".
cpg.addMethod(CtNewMethod.make(f"""
public static java.util.LinkedHashMap reserve(java.util.LinkedHashMap took, java.util.List inputs, int[] per, int done) {{
  java.util.LinkedHashMap left = new java.util.LinkedHashMap();
  left.putAll(took);
  int k = inputs.size();
  long[] need = new long[k];
  for (int i = 0; i < k; i++) need[i] = (long) per[i] * (long) done;
  for (int pass = 0; pass < 3; pass++) {{
    for (int i = 0; i < k; i++) {{
      if (need[i] <= 0L) continue;
      {MQ} mq = ({MQ}) inputs.get(i);
      String iid = mq.getItemId();
      String rt = mq.getResourceTypeId();
      if (pass == 0 && iid == null) continue;
      if (pass == 1 && (iid != null || rt == null)) continue;
      if (pass == 2 && (iid != null || rt != null)) continue;
      java.util.ArrayList keys = new java.util.ArrayList(left.keySet());
      for (int j = 0; j < keys.size() && need[i] > 0L; j++) {{
        String id = (String) keys.get(j);
        long q = 1L;
        if (pass == 0) {{ if (!id.equals(iid)) continue; }}
        else {{
          if (mq.isItemExcluded(id)) continue;
          if (pass == 1) {{ q = (long) rtUnits(id, rt); if (q <= 0L) continue; }}
        }}
        int h = ((Integer) left.get(id)).intValue();
        long want = (need[i] + q - 1L) / q;
        int use = want < (long) h ? (int) want : h;
        need[i] = need[i] - (long) use * q;
        if (h - use <= 0) left.remove(id); else left.put(id, Integer.valueOf(h - use));
      }}
    }}
  }}
  for (int i = 0; i < k; i++) if (need[i] > 0L) return null;
  return left;
}}""", cpg))
# queue up to `want` units (0 = all): inputs leave inventory + bags with counted removal (0.6.4 rule); resource-type inputs
# (Sands, Rock_*) are taken one unit at a time so the exact items are recorded for Cancel.
cpg.addMethod(CtNewMethod.make(f"""
public static String procQueue({PLA} p, {ST} st, {REF} ref, java.util.UUID u, String bench, int tier, {CRR} r, int want) {{
  if ({PKG}.ProcStore.BROKEN.containsKey(u)) return "your " + bench + " data could not be loaded - nothing was taken";
  {PKG}.ProcBench pb = {PKG}.ProcStore.of(u, bench);
  long now = System.currentTimeMillis();
  pb.advance(now);
  int room = {PKG}.ProcBench.QUEUE_CAP - pb.queued();
  if (room <= 0) return "the " + bench + " queue is full (" + {PKG}.ProcBench.QUEUE_CAP + " units)";
  {CIC} mats = materials(p, u);
  int lim = limit(r, mats);
  int qty = want <= 0 ? lim : (want < lim ? want : lim);
  if (qty > room) qty = room;
  if (qty <= 0) return "not enough materials";
  {MQ}[] rin = r.getInput();
  boolean res = false;
  for (int i = 0; rin != null && i < rin.length; i++) if (rin[i] != null && rin[i].getItemId() == null) res = true;
  long unit = {PKG}.ProcBench.unitMs(r, bench, tier);
  int queuedN = 0; int guard = 0;
  StringBuilder audit = new StringBuilder();
  while (queuedN < qty && guard < 400) {{
    guard++;
    int n = res ? 1 : (qty - queuedN);
    java.util.List inputs = {CRM}.getInputMaterials(r, n);
    int k = inputs == null ? 0 : inputs.size();
    if (k == 0) {{ audit.append(" no-inputs"); break; }}
    if (!mats.canRemoveMaterials(inputs)) break;
    java.util.HashMap snapB = snapshot(mats);
    int[] before = new int[k]; int[] per = new int[k]; int[] removed = new int[k];
    for (int i = 0; i < k; i++) {{
      {MQ} mq = ({MQ}) inputs.get(i);
      before[i] = mats.countRemovableMaterial(mq);
      per[i] = mq.getQuantity() / n; if (per[i] <= 0) per[i] = 1;
    }}
    Object tx = mats.removeMaterials(inputs);
    boolean flag = tx != null && ((com.hypixel.hytale.server.core.inventory.transaction.Transaction) tx).succeeded();
    int done = n;
    for (int i = 0; i < k; i++) {{
      removed[i] = before[i] - mats.countRemovableMaterial(({MQ}) inputs.get(i)); if (removed[i] < 0) removed[i] = 0;
      int c2 = removed[i] / per[i]; if (c2 < done) done = c2;
    }}
    if (done < 0) done = 0;
    java.util.LinkedHashMap took = removedItems(snapB, snapshot(mats));
    String unitInputs = "";
    if (done > 0 && !res) {{
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < k; i++) {{
        {MQ} mq = ({MQ}) inputs.get(i);
        if (sb.length() > 0) sb.append(';');
        sb.append(mq.getItemId()).append('*').append(per[i]);
        int extra = removed[i] - done * per[i];
        if (extra > 0) {{ giveBack(st, ref, p, mq.getItemId(), extra); audit.append(" returned ").append(mq.getItemId()).append('*').append(extra); }}
      }}
      unitInputs = sb.toString();
    }} else if (done > 0) {{
      unitInputs = {PKG}.ProcBench.ser(took);
    }}
    if (done <= 0 || unitInputs.length() == 0) {{
      java.util.Iterator ti = took.entrySet().iterator();
      while (ti.hasNext()) {{
        java.util.Map.Entry e = (java.util.Map.Entry) ti.next();
        giveBack(st, ref, p, (String) e.getKey(), ((Integer) e.getValue()).intValue());
        audit.append(" refunded ").append(e.getKey()).append('*').append(e.getValue());
      }}
      audit.append(" flag=").append(flag);
      break;
    }}
    pb.addJob(String.valueOf(r.getId()), done, unit, unitInputs, now);
    queuedN += done;
    audit.append(" [").append(done).append("x ").append(unitInputs).append(" flag=").append(flag).append("]");
    if (done < n) break;
  }}
  {PKG}.BagMirror m = {PKG}.BagMirror.of(u);
  int consumed = m.sync(u);
  saveSoon(u);
  {PKG}.CraftLog.line(u, "QUEUE " + bench + " " + r.getId() + " requested=" + qty + " queued=" + queuedN + " unitMs=" + unit + " tier=" + tier + " fromBags=" + consumed + audit);
  {MQ} outq = r.getPrimaryOutput();
  String nm = pretty(outq == null ? String.valueOf(r.getId()) : outq.getItemId());
  if (queuedN <= 0) return "could not take the materials - nothing was used";
  return "queued " + queuedN + " x " + nm + " in the " + bench + (queuedN < qty ? " (" + (qty - queuedN) + " fewer than asked - the rest was returned)" : "") + (consumed > 0 ? " - " + consumed + " from bags" : "");
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static String procFuel({PLA} p, {ST} st, {REF} ref, java.util.UUID u, String bench, String id) {{
  if ({PKG}.ProcStore.BROKEN.containsKey(u)) return "your " + bench + " data could not be loaded - nothing was taken";
  if ({PKG}.ProcBench.fuelQuality(id) <= 0.0) return pretty(id) + " does not burn";
  {PKG}.ProcBench pb = {PKG}.ProcStore.of(u, bench);
  pb.advance(System.currentTimeMillis());
  int room = {PKG}.ProcBench.FUEL_CAP - pb.fuelCount();
  if (room <= 0) return "the fuel slot is full (" + {PKG}.ProcBench.FUEL_CAP + " items)";
  {CIC} mats = materials(p, u);
  {MQ} one = new {MQ}(id, (String) null, (String) null, 1, (org.bson.BsonDocument) null);
  int have = mats.countRemovableMaterial(one);
  int n = have < 64 ? have : 64;
  if (n > room) n = room;
  if (n <= 0) return "you have no " + pretty(id);
  java.util.ArrayList l = new java.util.ArrayList();
  l.add(new {MQ}(id, (String) null, (String) null, n, (org.bson.BsonDocument) null));
  if (!mats.canRemoveMaterials(l)) return "could not take the fuel";
  int before = mats.countRemovableMaterial(one);
  Object tx = mats.removeMaterials(l);
  int after = mats.countRemovableMaterial(one);
  int took = before - after; if (took < 0) took = 0;
  if (took > 0) pb.addFuel(id, took);
  {PKG}.BagMirror m = {PKG}.BagMirror.of(u);
  int consumed = m.sync(u);
  saveSoon(u);
  {PKG}.CraftLog.line(u, "FUEL " + bench + " " + id + " asked=" + n + " loaded=" + took + " count " + before + "->" + after + " fromBags=" + consumed);
  return took > 0 ? ("loaded " + took + " " + pretty(id) + " into the " + bench) : "could not take the fuel";
}}""", cpg))
# collect: storage first (getCombinedStorageHotbarBackpack), only what fits, verified by counting; the rest stays in the output slot
cpg.addMethod(CtNewMethod.make(f"""
public static String procCollect({PLA} p, {ST} st, {REF} ref, java.util.UUID u, String bench) {{
  {PKG}.ProcBench pb = {PKG}.ProcStore.get(u, bench);
  if (pb == null) return "nothing to collect yet";
  if (pb.advance(System.currentTimeMillis()) > 0) {PKG}.ProcStore.markDirty(u);
  java.util.ArrayList l = pb.outList();
  if (l.isEmpty()) return "nothing to collect yet";
  {IC} dst = p.getInventory().getCombinedStorageHotbarBackpack();
  int given = 0; int left = 0;
  StringBuilder audit = new StringBuilder();
  for (int i = 0; i < l.size(); i++) {{
    Object[] e = (Object[]) l.get(i);
    String id = (String) e[0];
    int want = ((Integer) e[1]).intValue();
    int max = 64;
    try {{ {IS} probe = new {IS}(id, 1); if (probe.getItem() != null && probe.getItem().getMaxStack() > 0) max = probe.getItem().getMaxStack(); }} catch (Throwable t) {{ }}
    int moved = 0; int guard = 0;
    while (moved < want && guard < 2000) {{
      guard++;
      int n = want - moved; if (n > max) n = max;
      int before = countItem(dst, id);
      dst.addItemStack(new {IS}(id, n));
      int added = countItem(dst, id) - before;
      if (added < 0) added = 0;
      if (added > n) added = n;
      if (added > 0) pb.takeOut(id, added);
      moved += added;
      if (added < n) break;
    }}
    given += moved; left += want - moved;
    audit.append(" ").append(id).append('=').append(moved).append('/').append(want);
  }}
  saveSoon(u);
  {PKG}.CraftLog.line(u, "COLLECT " + bench + " given=" + given + " left=" + left + audit);
  if (given == 0) return "your inventory is full - nothing collected";
  return "collected " + given + " items" + (left > 0 ? " - inventory full, " + left + " still waiting in the " + bench : "");
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static String procCancel({PLA} p, {ST} st, {REF} ref, java.util.UUID u, String bench) {{
  {PKG}.ProcBench pb = {PKG}.ProcStore.get(u, bench);
  if (pb == null) return "nothing queued";
  pb.advance(System.currentTimeMillis());
  if (pb.queued() <= 0) return "nothing queued";
  int n = pb.cancel();
  saveSoon(u);
  {PKG}.CraftLog.line(u, "CANCEL " + bench + " units=" + n + " (their inputs went to the output slot)");
  return "cancelled " + n + " units - " + procCollect(p, st, ref, u, bench);
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static String procUnload({PLA} p, {ST} st, {REF} ref, java.util.UUID u, String bench) {{
  {PKG}.ProcBench pb = {PKG}.ProcStore.get(u, bench);
  if (pb == null) return "no fuel loaded";
  pb.advance(System.currentTimeMillis());
  int n = pb.unloadFuel();
  if (n <= 0) return "no unburned fuel loaded";
  saveSoon(u);
  {PKG}.CraftLog.line(u, "UNLOAD " + bench + " fuel=" + n + " (to the output slot)");
  return "unloaded " + n + " fuel - " + procCollect(p, st, ref, u, bench);
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public void buildProc({UCB} b, {UEB} ev, {PLA} p, java.util.UUID u) {{
  String bs = "Style: TextButtonStyle(Default: (Background: #1d3a5f, LabelStyle: (FontSize: 13, TextColor: #dceeff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #2f5a8f, LabelStyle: (FontSize: 13, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #0f2038, LabelStyle: (FontSize: 13, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  String on = "Style: TextButtonStyle(Default: (Background: #7fb0e0, LabelStyle: (FontSize: 13, TextColor: #06192a, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #a0c8f0, LabelStyle: (FontSize: 13, TextColor: #06192a, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #5f90c0, LabelStyle: (FontSize: 13, TextColor: #06192a, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  String bench = this.tab.substring(2);
  int tier = accTier(accessories(p, u), bench);
  boolean broken = {PKG}.ProcStore.BROKEN.containsKey(u);
  {PKG}.ProcBench pb = {PKG}.ProcStore.get(u, bench);
  if (pb != null && pb.advance(System.currentTimeMillis()) > 0) {PKG}.ProcStore.markDirty(u);
  {PKG}.ProcBench view = pb != null ? pb : new {PKG}.ProcBench(bench);
  String[] d = view.describe(tier, tier > 0);
  String stat = broken ? ("Your " + bench + " file could not be read - it was left untouched. Tell an admin.") : d[0];
  b.appendInline("#SkyyCraft", "Label #SkyyPStat {{ Anchor: (Height: 24); Text: \\"" + {PKG}.SacksPage.safe(stat) + "\\"; Style: (FontSize: 14, RenderBold: true, TextColor: #ffd9a0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyCraft", "Label #SkyyPProg {{ Anchor: (Height: 22); Text: \\"" + {PKG}.SacksPage.safe(d[1]) + "\\"; Style: (FontSize: 13, TextColor: #e6f2ff, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyCraft", "Group #SkyyPBarRow {{ Anchor: (Height: 18); LayoutMode: Left; Padding: (Top: 2); }}");
  b.appendInline("#SkyyPBarRow", "Label {{ Anchor: (Width: 84, Height: 14); Text: \\"\\"; }}");
  b.appendInline("#SkyyPBarRow", "Group #SkyyPBar {{ Anchor: (Width: 800, Height: 14); LayoutMode: Left; Background: #1a2838; }}");
  int pct = 0;
  try {{ pct = Integer.parseInt(d[4]); }} catch (Throwable t) {{ }}
  int seg = pct / 5;
  for (int i = 0; i < 20; i++) b.appendInline("#SkyyPBar", "Group #SkyyPSeg" + i + " {{ Anchor: (Width: 40, Height: 14); Background: #e0a040; Visible: " + (i < seg ? "true" : "false") + "; }}");
  b.appendInline("#SkyyCraft", "Label #SkyyPQueue {{ Anchor: (Height: 22); Text: \\"" + {PKG}.SacksPage.safe(d[2]) + "\\"; Style: (FontSize: 12, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyCraft", "Group #SkyyPOutRow {{ Anchor: (Height: 44); LayoutMode: Left; Padding: (Top: 4); }}");
  b.appendInline("#SkyyPOutRow", "Label #SkyyPOut {{ Anchor: (Width: 520, Height: 36); Text: \\"" + {PKG}.SacksPage.safe(d[3]) + "\\"; Style: (FontSize: 14, RenderBold: true, TextColor: #9fd8a2, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyPOutRow", "TextButton #SkyyPCollect {{ Anchor: (Width: 130, Height: 34); Text: \\"Collect\\"; " + bs + " }}");
  b.appendInline("#SkyyPOutRow", "Label {{ Anchor: (Width: 8, Height: 34); Text: \\"\\"; }}");
  b.appendInline("#SkyyPOutRow", "TextButton #SkyyPCancel {{ Anchor: (Width: 150, Height: 34); Text: \\"Cancel queue\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyPCollect", {EVD}.of("a", "pcollect"));
  ev.addEventBinding({BT}.Activating, "#SkyyPCancel", {EVD}.of("a", "pcancel"));
  {CIC} mats = materials(p, u);
  this.fuelIds = new String[4];
  if (view.needsFuel) {{
    b.appendInline("#SkyyPOutRow", "Label {{ Anchor: (Width: 8, Height: 34); Text: \\"\\"; }}");
    b.appendInline("#SkyyPOutRow", "TextButton #SkyyPUnload {{ Anchor: (Width: 130, Height: 34); Text: \\"Unload fuel\\"; " + bs + " }}");
    ev.addEventBinding({BT}.Activating, "#SkyyPUnload", {EVD}.of("a", "punload"));
    b.appendInline("#SkyyCraft", "Group #SkyyPFuelRow {{ Anchor: (Height: 44); LayoutMode: Left; Padding: (Top: 4); }}");
    b.appendInline("#SkyyPFuelRow", "Label {{ Anchor: (Width: 110, Height: 34); Text: \\"Load fuel\\"; Style: (FontSize: 14, RenderBold: true, TextColor: #ffd9a0, VerticalAlignment: Center); }}");
    java.util.ArrayList fl = {PKG}.ProcBench.fuels();
    java.util.ArrayList have = new java.util.ArrayList();
    for (int i = 0; i < fl.size(); i++) {{
      String fid = (String) fl.get(i);
      int c = mats.countRemovableMaterial(new {MQ}(fid, (String) null, (String) null, 1, (org.bson.BsonDocument) null));
      if (c > 0) have.add(new Object[] {{ fid, Integer.valueOf(c) }});
    }}
    boolean[] used = new boolean[have.size()];
    int shown = 0;
    for (int sI = 0; sI < 4; sI++) {{
      int bi = -1; int bc = 0;
      for (int i = 0; i < have.size(); i++) {{
        if (used[i]) continue;
        int c = ((Integer) ((Object[]) have.get(i))[1]).intValue();
        if (c > bc) {{ bc = c; bi = i; }}
      }}
      if (bi < 0) break;
      used[bi] = true;
      String fid = (String) ((Object[]) have.get(bi))[0];
      this.fuelIds[sI] = fid;
      int n = bc < 64 ? bc : 64;
      b.appendInline("#SkyyPFuelRow", "TextButton #SkyyPFuel" + sI + " {{ Anchor: (Width: 200, Height: 34); Text: \\"" + {PKG}.SacksPage.safe(pretty(fid) + " x" + n) + "\\"; " + bs + " }}");
      b.appendInline("#SkyyPFuelRow", "Label {{ Anchor: (Width: 6, Height: 34); Text: \\"\\"; }}");
      ev.addEventBinding({BT}.Activating, "#SkyyPFuel" + sI, {EVD}.of("a", "pfuel:" + sI));
      shown++;
    }}
    if (shown == 0) b.appendInline("#SkyyPFuelRow", "Label {{ Anchor: (Width: 820, Height: 34); Text: \\"No fuel on you or in your bags - logs, planks, sticks and charcoal burn.\\"; Style: (FontSize: 13, TextColor: #c07070, VerticalAlignment: Center); }}");
  }}
  java.util.ArrayList raw = (tier > 0 && !broken) ? recipesFor(this.tab, u) : new java.util.ArrayList();
  boolean only = Boolean.TRUE.equals(ONLY.get(u));
  java.util.ArrayList ent = new java.util.ArrayList();
  for (int i = 0; i < raw.size(); i++) {{
    {CRR} r0 = ({CRR}) raw.get(i);
    int l0 = limit(r0, mats);
    if (only && l0 <= 0) continue;
    {MQ} o0 = r0.getPrimaryOutput();
    String id0 = o0 == null ? String.valueOf(r0.getId()) : o0.getItemId();
    ent.add(new Object[] {{ r0, Integer.valueOf(l0), Integer.valueOf({PKG}.RecipeCmp.tierOf(id0)), id0 == null ? "" : id0 }});
  }}
  java.util.Collections.sort(ent, new {PKG}.RecipeCmp());
  this.rows = new java.util.ArrayList();
  for (int i = 0; i < ent.size(); i++) this.rows.add(((Object[]) ent.get(i))[0]);
  int room = {PKG}.ProcBench.QUEUE_CAP - view.queued();
  if (room < 0) room = 0;
  int per = 7;
  int pages = (this.rows.size() + per - 1) / per; if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1; if (this.pageNo < 0) this.pageNo = 0;
  int start = this.pageNo * per;
  for (int i = start; i < this.rows.size() && i < start + per; i++) {{
    {CRR} r = ({CRR}) this.rows.get(i);
    {MQ} outq = r.getPrimaryOutput();
    String outId = outq == null ? "?" : outq.getItemId();
    int lim = limit(r, mats);
    int allN = lim < room ? lim : room;
    StringBuilder need = new StringBuilder();
    {MQ}[] in = r.getInput();
    for (int k = 0; in != null && k < in.length; k++) {{
      if (need.length() > 0) need.append("   ");
      String nm = in[k].getItemId() != null ? pretty(in[k].getItemId()) : (in[k].getResourceTypeId() != null ? in[k].getResourceTypeId() : "?");
      need.append(nm).append(" ").append(mats.countRemovableMaterial(in[k])).append("/").append(in[k].getQuantity());
    }}
    need.append("   - ").append({PKG}.ProcBench.dur({PKG}.ProcBench.unitMs(r, bench, tier))).append(" each");
    b.appendInline("#SkyyCraft", "Group #SkyyCRow" + i + " {{ Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); " + (lim > 0 ? "Background: #10233a(0.9); " : "Background: #0e1826(0.6); ") + "}}");
    b.appendInline("#SkyyCRow" + i, "Group {{ Anchor: (Width: 56, Height: 54); ItemIcon {{ Anchor: (Width: 46, Height: 46, Left: 5, Top: 4); ItemId: \\"" + {PKG}.SacksPage.safe(outId) + "\\"; }} }}");
    b.appendInline("#SkyyCRow" + i, "Group #SkyyCTxt" + i + " {{ Anchor: (Width: 600, Height: 54); LayoutMode: Top; }}");
    b.appendInline("#SkyyCTxt" + i, "Label {{ Anchor: (Height: 27); Text: \\"" + {PKG}.SacksPage.safe(pretty(outId) + (outq != null && outq.getQuantity() > 1 ? " x" + outq.getQuantity() : "")) + "\\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + (lim > 0 ? "#ffffff" : "#8a97a8") + ", VerticalAlignment: Center); }}");
    b.appendInline("#SkyyCTxt" + i, "Label {{ Anchor: (Height: 23); Text: \\"" + {PKG}.SacksPage.safe(need.toString()) + "\\"; Style: (FontSize: 12, TextColor: " + (lim > 0 ? "#9fd8a2" : "#c07070") + ", VerticalAlignment: Center); }}");
    b.appendInline("#SkyyCRow" + i, "TextButton #SkyyPQ" + i + " {{ Anchor: (Width: 82, Height: 34); Text: \\"Queue\\"; " + bs + " }}");
    b.appendInline("#SkyyCRow" + i, "Label {{ Anchor: (Width: 6, Height: 34); Text: \\"\\"; }}");
    b.appendInline("#SkyyCRow" + i, "TextButton #SkyyPTen" + i + " {{ Anchor: (Width: 66, Height: 34); Text: \\"x10\\"; " + bs + " }}");
    b.appendInline("#SkyyCRow" + i, "Label {{ Anchor: (Width: 6, Height: 34); Text: \\"\\"; }}");
    b.appendInline("#SkyyCRow" + i, "TextButton #SkyyPAll" + i + " {{ Anchor: (Width: 76, Height: 34); Text: \\"All " + allN + "\\"; " + bs + " }}");
    ev.addEventBinding({BT}.Activating, "#SkyyPQ" + i, {EVD}.of("a", "pq:" + i + ":1"));
    ev.addEventBinding({BT}.Activating, "#SkyyPTen" + i, {EVD}.of("a", "pq:" + i + ":10"));
    ev.addEventBinding({BT}.Activating, "#SkyyPAll" + i, {EVD}.of("a", "pq:" + i + ":0"));
  }}
  if (this.rows.size() == 0) b.appendInline("#SkyyCraft", "Label {{ Anchor: (Height: 30); Text: \\"" + (tier > 0 ? "No recipes here yet." : ("Equip a " + bench + " accessory in your accessory bag to queue more.")) + "\\"; Style: (FontSize: 15, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyCraft", "Label #SkyyCInfo {{ Anchor: (Height: 26); Text: \\"" + {PKG}.SacksPage.safe(this.info) + "\\"; Style: (FontSize: 14, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyCraft", "Group #SkyyCNav {{ Anchor: (Height: 42); LayoutMode: Left; Padding: (Top: 6); }}");
  b.appendInline("#SkyyCNav", "TextButton #SkyyCPrev {{ Anchor: (Width: 92, Height: 34); Text: \\"< Prev\\"; " + bs + " }}");
  b.appendInline("#SkyyCNav", "Label {{ Anchor: (Width: 160, Height: 34); Text: \\"Page " + (this.pageNo + 1) + " / " + pages + "\\"; Style: (FontSize: 13, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyCNav", "TextButton #SkyyCNext {{ Anchor: (Width: 92, Height: 34); Text: \\"Next >\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyCPrev", {EVD}.of("a", "prev"));
  ev.addEventBinding({BT}.Activating, "#SkyyCNext", {EVD}.of("a", "next"));
  b.appendInline("#SkyyCNav", "Label {{ Anchor: (Width: 40, Height: 34); Text: \\"\\"; }}");
  b.appendInline("#SkyyCNav", "TextButton #SkyyCOnly {{ Anchor: (Width: 230, Height: 34); Text: \\"Craftable only: " + (only ? "ON" : "OFF") + "\\"; " + (only ? on : bs) + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyCOnly", {EVD}.of("a", "onlyc"));
  this.liveSig = d[0] + "|" + d[1] + "|" + d[2] + "|" + d[3] + "|" + d[4];
  this.liveAt = System.currentTimeMillis();
  this.liveOn = !broken;
}}""", cpg))
# live refresh from ProcTask (world thread): set() only - Text + Visible on elements the last build created, never re-appends
# (a re-append under the cursor is what crashed the client in 0.2.3); at most every ~2s and only when the text changed, because
# PageManager drops page clicks while an update is unacknowledged.
cpg.addMethod(CtNewMethod.make(f"""
public void live({REF} ref, {ST} st) {{
  if (!this.liveOn || this.tab == null || !this.tab.startsWith("P:")) return;
  long now = System.currentTimeMillis();
  if (now - this.liveAt < 1900L) return;
  java.util.UUID u = this.playerRef.getUuid();
  String bench = this.tab.substring(2);
  {PKG}.ProcBench pb = {PKG}.ProcStore.get(u, bench);
  if (pb == null) return;
  int tier = accTier(accessories(({PLA}) null, u), bench);
  String[] d = pb.describe(tier, tier > 0);
  String sig = d[0] + "|" + d[1] + "|" + d[2] + "|" + d[3] + "|" + d[4];
  if (sig.equals(this.liveSig)) return;
  this.liveSig = sig;
  this.liveAt = now;
  int seg = 0;
  try {{ seg = Integer.parseInt(d[4]) / 5; }} catch (Throwable t) {{ }}
  {UCB} c = new {UCB}();
  c.set("#SkyyPStat.Text", d[0]);
  c.set("#SkyyPProg.Text", d[1]);
  c.set("#SkyyPQueue.Text", d[2]);
  c.set("#SkyyPOut.Text", d[3]);
  for (int i = 0; i < 20; i++) c.set("#SkyyPSeg" + i + ".Visible", i < seg);
  sendUpdate(c, false);
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public boolean handleProc({REF} ref, {ST} st, {PLA} p, java.util.UUID u, String data) {{
  if (this.tab == null || !this.tab.startsWith("P:")) return false;
  String bench = this.tab.substring(2);
  if (data.indexOf("\\"pcollect\\"") >= 0) {{ this.info = procCollect(p, st, ref, u, bench); rebuild(); return true; }}
  if (data.indexOf("\\"pcancel\\"") >= 0) {{ this.info = procCancel(p, st, ref, u, bench); rebuild(); return true; }}
  if (data.indexOf("\\"punload\\"") >= 0) {{ this.info = procUnload(p, st, ref, u, bench); rebuild(); return true; }}
  int f = data.indexOf("pfuel:");
  if (f >= 0) {{
    int e = data.indexOf('\\"', f);
    int i = Integer.parseInt(data.substring(f + 6, e));
    if (this.fuelIds != null && i >= 0 && i < this.fuelIds.length && this.fuelIds[i] != null) this.info = procFuel(p, st, ref, u, bench, this.fuelIds[i]);
    rebuild();
    return true;
  }}
  int q = data.indexOf("pq:");
  if (q >= 0) {{
    int e = data.indexOf('\\"', q);
    String[] parts = data.substring(q + 3, e).split(":");
    int idx = Integer.parseInt(parts[0]); int want = Integer.parseInt(parts[1]);
    if (this.rows != null && idx >= 0 && idx < this.rows.size()) {{
      int tier = accTier(accessories(p, u), bench);
      if (tier <= 0) this.info = "equip a " + bench + " accessory to queue";
      else this.info = procQueue(p, st, ref, u, bench, tier, ({CRR}) this.rows.get(idx), want);
    }}
    rebuild();
    return true;
  }}
  return false;
}}""", cpg))
'''
before('cpg.addMethod(CtNewMethod.make(f"""' + LF + 'public void build(', PROCPAGE)

# ---------------------------------------------------------------- CraftPage.build: live flag, unknown-tab reset, Furnace/Tannery view
rep('  if (p == null) return;' + LF + '  this.tabs = buildTabs(p, u);' + LF +
    '  if (this.tab == null && this.tabs.size() > 0) this.tab = ((String[]) this.tabs.get(0))[0];' + LF,
    '  this.liveOn = false;' + LF + '  if (p == null) return;' + LF + '  this.tabs = buildTabs(p, u);' + LF +
    '  boolean known = false;' + LF +
    '  for (int i = 0; this.tab != null && i < this.tabs.size(); i++) if (this.tab.equals(((String[]) this.tabs.get(i))[0])) known = true;' + LF +
    '  if (!known && this.tabs.size() > 0) {{ this.tab = ((String[]) this.tabs.get(0))[0]; this.pageNo = 0; }}' + LF)
rep('magic bags.\\\\"; Style: (FontSize: 13, TextColor: #9fb8d0, HorizontalAlignment: Center); }}");' + LF + '  java.util.ArrayList raw = ',
    'magic bags.\\\\"; Style: (FontSize: 13, TextColor: #9fb8d0, HorizontalAlignment: Center); }}");' + LF +
    '  if (this.tab != null && this.tab.startsWith("P:")) {{ buildProc(b, ev, p, u); return; }}' + LF + '  java.util.ArrayList raw = ')

# ---------------------------------------------------------------- CraftPage.handleDataEvent: Furnace/Tannery actions
before('    int c = data.indexOf("craft:");' + LF, '    if (handleProc(ref, st, p, u, data)) return;' + LF)

# ---------------------------------------------------------------- CraftPage.handleDataEvent: instant craft pays by the removed-items diff (review fix)
# 0.6.8 inferred each input's surplus as removed - done * per and could not hand back a resource-type surplus (it logged "LOST"). Now the
# literal before/after snapshot diff of the material container is split by reserve(): `done` is lowered until the removed items really
# cover it (count-based done can over-count when one item satisfies two inputs), and every item not paid for goes back as itself.
# Serves the merged Crafting tab and the Alchemy tab (945 recipes in the assets have a ResourceTypeId input, e.g. Wood_Trunk, Rock).
rep(r'''    int[] before = new int[n]; int[] per = new int[n];
    for (int i = 0; i < n; i++) {{
      {MQ} mq = ({MQ}) inputs.get(i);
      before[i] = mats.countRemovableMaterial(mq);
      per[i] = mq.getQuantity() / qty; if (per[i] <= 0) per[i] = 1;
    }}
    Object tx = mats.removeMaterials(inputs);
    boolean flag = tx != null && ((com.hypixel.hytale.server.core.inventory.transaction.Transaction) tx).succeeded();
    int[] after = new int[n]; int done = qty;
    for (int i = 0; i < n; i++) {{
      after[i] = mats.countRemovableMaterial(({MQ}) inputs.get(i));
      int removed = before[i] - after[i]; if (removed < 0) removed = 0;
      int c2 = removed / per[i]; if (c2 < done) done = c2;
    }}
    if (done < 0) done = 0;
    StringBuilder audit = new StringBuilder();
    for (int i = 0; i < n; i++) {{
      {MQ} mq = ({MQ}) inputs.get(i);
      int removed = before[i] - after[i]; if (removed < 0) removed = 0;
      int extra = removed - done * per[i];
      String mid = mq.getItemId() != null ? mq.getItemId() : ("res:" + mq.getResourceTypeId());
      audit.append(" ").append(mid).append("=").append(before[i]).append("->").append(after[i]);
      if (extra > 0) {{
        if (mq.getItemId() != null) {{ {SIC}.addOrDropItemStack(st, ref, p.getInventory().getCombinedStorageHotbarBackpack(), new {IS}(mq.getItemId(), extra)); audit.append("(returned ").append(extra).append(")"); }}
        else {{ audit.append("(LOST ").append(extra).append(" resource items)"); {PKG}.SackPool.warn("craft: " + extra + " x " + mid + " removed beyond " + done + " crafts for " + u + " - resource type, cannot return"); }}
      }}
    }}
''', r'''    java.util.HashMap snapB = snapshot(mats);
    int[] before = new int[n]; int[] per = new int[n];
    for (int i = 0; i < n; i++) {{
      {MQ} mq = ({MQ}) inputs.get(i);
      before[i] = mats.countRemovableMaterial(mq);
      per[i] = mq.getQuantity() / qty; if (per[i] <= 0) per[i] = 1;
    }}
    Object tx = mats.removeMaterials(inputs);
    boolean flag = tx != null && ((com.hypixel.hytale.server.core.inventory.transaction.Transaction) tx).succeeded();
    int[] after = new int[n]; int done = qty;
    for (int i = 0; i < n; i++) {{
      after[i] = mats.countRemovableMaterial(({MQ}) inputs.get(i));
      int removed = before[i] - after[i]; if (removed < 0) removed = 0;
      int c2 = removed / per[i]; if (c2 < done) done = c2;
    }}
    if (done < 0) done = 0;
    java.util.LinkedHashMap took = removedItems(snapB, snapshot(mats));
    java.util.LinkedHashMap left = reserve(took, inputs, per, done);
    if (left == null) {{
      int lo = 0; int hi = done - 1;
      done = 0;
      left = reserve(took, inputs, per, 0);
      while (lo <= hi) {{
        int md = (lo + hi) / 2;
        java.util.LinkedHashMap l2 = reserve(took, inputs, per, md);
        if (l2 != null) {{ done = md; left = l2; lo = md + 1; }} else hi = md - 1;
      }}
    }}
    StringBuilder audit = new StringBuilder();
    for (int i = 0; i < n; i++) {{
      {MQ} mq = ({MQ}) inputs.get(i);
      String mid = mq.getItemId() != null ? mq.getItemId() : ("res:" + mq.getResourceTypeId());
      audit.append(" ").append(mid).append("=").append(before[i]).append("->").append(after[i]);
    }}
    java.util.Iterator li = left.entrySet().iterator();
    while (li.hasNext()) {{
      java.util.Map.Entry le = (java.util.Map.Entry) li.next();
      int back = ((Integer) le.getValue()).intValue();
      if (back <= 0) continue;
      giveBack(st, ref, p, (String) le.getKey(), back);
      audit.append(" returned ").append((String) le.getKey()).append('*').append(back);
    }}
''')

# ---------------------------------------------------------------- CraftPageFactory + ProcTask + ProcTick (after CraftPage, before plugin)
TICK = r'''# ================= CraftPageFactory (OpenCustomUI page ids -> craft page on a tab) =================
cfac.addInterface(pool.get("java.util.function.Function"))
cfac.addField(CtField.make("public String tab;", cfac))
cfac.addConstructor(CtNewConstructor.make("public CraftPageFactory(String tab) { this.tab = tab; }", cfac))
cfac.addMethod(CtNewMethod.make(f"""
public Object apply(Object o) {{
  return new {PKG}.CraftPage(({PR}) o, this.tab);
}}""", cfac))

# ================= ProcTask (world thread, every 1s per player): advance Furnace/Tannery, notify, refresh an open Furnace/Tannery tab =================
ptk.addInterface(pool.get("java.lang.Runnable"))
ptk.addField(CtField.make(f"public {PR} pr;", ptk))
ptk.addField(CtField.make("public java.util.UUID expectedWorld;", ptk))
ptk.addField(CtField.make("public static long LASTWARN;", ptk))
ptk.addConstructor(CtNewConstructor.make(f"public ProcTask({PR} pr, java.util.UUID w) {{ this.pr = pr; this.expectedWorld = w; }}", ptk))
ptk.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (pr == null || !pr.isValid()) return;
    java.util.UUID nowWorld = pr.getWorldUuid();
    if (nowWorld == null || !nowWorld.equals(this.expectedWorld)) return;
    java.util.UUID u = pr.getUuid();
    if ({PKG}.ProcStore.BROKEN.containsKey(u)) return;
    java.util.Map m = {PKG}.ProcStore.all(u);
    if (m.isEmpty()) return;
    long now = System.currentTimeMillis();
    java.util.Iterator it = m.values().iterator();
    while (it.hasNext()) {{
      {PKG}.ProcBench pb = ({PKG}.ProcBench) it.next();
      int had = pb.queued();
      int d = pb.advance(now);
      if (d > 0) {PKG}.ProcStore.markDirty(u);
      if (had > 0 && pb.queued() == 0) {{
        String[] ds = pb.describe(0, true);
        pr.sendMessage({MSG}.raw("[SkyySacks] Your " + pb.bench + " is done. " + ds[3] + " - open /craft to collect."));
        {PKG}.CraftLog.line(u, "DONE " + pb.bench + " queue finished - " + ds[3]);
      }} else if (pb.fuelWarnOnce()) {{
        pr.sendMessage({MSG}.raw("[SkyySacks] Your " + pb.bench + " ran out of fuel - load more in /craft."));
      }}
    }}
    {REF} r = pr.getReference();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    if (p == null) return;
    Object pg = p.getPageManager().getCustomPage();
    if (pg instanceof {PKG}.CraftPage) (({PKG}.CraftPage) pg).live(r, st);
  }} catch (Throwable t) {{
    long now2 = System.currentTimeMillis();
    if (now2 - LASTWARN > 60000L) {{ LASTWARN = now2; {PKG}.SackPool.warn("processing tick failed: " + t); }}
  }}
}}""", ptk))

ptick.addInterface(pool.get("java.lang.Runnable"))
ptick.addConstructor(CtNewConstructor.make("public ProcTick() { }", ptick))
ptick.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) continue;
      {WLD} w = {UNI}.get().getWorld(wu);
      if (w == null) continue;
      w.execute(new {PKG}.ProcTask(pr, wu));
    }}
  }} catch (Throwable t) {{ }}
}}""", ptick))

'''
before('# ================= plugin =================' + LF, TICK)

# ---------------------------------------------------------------- plugin wiring
after('pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture crafter;", pl))' + LF,
      'pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture procTicker;", pl))' + LF)
after('  {PKG}.CraftLog.FILE = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("crafts.log");' + LF,
      '  {PKG}.ProcStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("processing");' + LF)
after('  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksCombat", new {PKG}.SacksPageFactory("Combat"));' + LF,
      '  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksCraft", new {PKG}.CraftPageFactory((String) null));' + LF +
      '  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksAlchemy", new {PKG}.CraftPageFactory("A:alch"));' + LF +
      '  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksFurnace", new {PKG}.CraftPageFactory("P:Furnace"));' + LF +
      '  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksTannery", new {PKG}.CraftPageFactory("P:Tannery"));' + LF)
after('  this.crafter = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.CraftTick(), 1000L, 300L, java.util.concurrent.TimeUnit.MILLISECONDS);' + LF,
      '  this.procTicker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.ProcTick(), 3L, 1L, java.util.concurrent.TimeUnit.SECONDS);' + LF)
rep('ready - /pd, /craft, right-click a magic bag; workbenches craft from your bags',
    'ready - /pd, /craft (Crafting, Alchemy, timed Furnace/Tannery queues), right-click a magic bag; workbenches craft from your bags')
after('  try {{ if (this.crafter != null) this.crafter.cancel(false); }} catch (Throwable t) {{ }}' + LF,
      '  try {{ if (this.procTicker != null) this.procTicker.cancel(false); }} catch (Throwable t) {{ }}' + LF +
      '  try {{ {PKG}.ProcStore.flushDirty(); }} catch (Throwable t) {{ }}' + LF)
rep('for c in (defs, sp, swp, tick, sav, cmp, page, cmd, fac, mir, clt, ctk, rcmp, clog, cpg, ccmd, pl):' + LF,
    'for c in (defs, sp, pjob, pben, pst, swp, tick, sav, cmp, page, cmd, fac, mir, clt, ctk, rcmp, clog, cpg, ccmd, cfac, ptk, ptick, pl):' + LF)

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
