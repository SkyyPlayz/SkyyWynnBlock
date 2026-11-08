"""Derive SkyySacks/build_skyysacks_0.8.35.py from the SET pin 0.8.34 (the GENERATED build_skyysacks_0.8.34.py; edit THIS file, then
regenerate: python tools/sacks_0_8_35_patch.py; never re-run sacks_0_8_34_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.34 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_35_patch.py   then   python SkyySacks/build_skyysacks_0.8.35.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.35.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.35 (2026-11-08) = FURNACE ALL (tag furnall, with SkyyGear 0.3.55; docs/answered/ui.md 2026-11-08, Skyy, screenshot of Crafting -> Furnace, ALL 25 on Copper and
  Iron Ingot: "make the all button actually add all, and put the furnace icon in  smithing and upgrade too so you can open it anywhere you need it.").
  ROOT CAUSE: every /craft count and every /craft payment went through the BagMirror container, which offers only a few stacks of each item: 36 slots shared
  by the whole page's wanted ids (so a Furnace tab with its many inputs got ONE stack = 25 ore: "All 25", "Copper Ore 25/1"), and 4 stacks for one recipe
  (the click: 4 x 25 = "requested=100"). The bags held 1,792 ore.
  1. BagMirror.counts = a COUNT-ONLY container: one (oversized, never paid from) stack per wanted item the pool holds, by the mirror's own rules (bag home, loaded
     item, wants(), the virtual base stacks of BagMirror.virtuals, the Enchanted items). CraftPage.countMats = inventory + that; viewMats (the page's numbers) uses it, so the
     have / need chips and the All label are the true amounts.
  2. procQueue (Furnace / Tannery): lim comes from countMats; the debit runs in rounds - when the mirror's stacks are used up it is synced and rebuilt - so the amount
     debited is exactly the amount queued. Queue room is the only limit; a queue filled to bench.queueCap says so on the status line. The old 400 pass guard (one per
     unit of a resource-type recipe) is gone: every pass queues at least one unit or stops. The per-click audit in crafts.log stops growing at 2,000 characters.
  3. Instant tabs (Crafting, Gear, Farming, Campfire, Collections) had the same cap (it was not a decision: no line in docs/answered asks for it). CraftPage.craftAll runs craftOne in
     rounds up to the true maximum (inventory, Void, Void Charms). DELIBERATE limit on All only: as many crafts as the outputs FIT in the inventory (CraftPage.fitN; at least 1
     as before), because craftOne's addOrDrop would otherwise put a whole bag's worth on the ground. The status line says when the inventory stopped it. x10 and Craft keep
     their numbers and now also reach past the mirror's stacks.
  4. Bridge sacks:fn:openFurnace (UUID -> Boolean; CraftHubOpen("Furnace"), world thread): opens the Furnace sub-tab of the Crafting page. Same gate as the sub-tab
     (a Furnace accessory in the Void Charms, or a Furnace still holding work); FALSE = not opened. SkyyGear 0.3.55 draws the button.
  No saved-data change, no config row, no migration, no new system / command, one new bridge key. ROLLBACK to 0.8.34: safe alone (All back to the mirror's stacks; SkyyGear 0.3.55
  stops drawing its Furnace button when the bridge key is missing).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.34.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.35.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.8.34"\n') and P.has("Skyy_Aug_") and not P.has("countMats"), "not the live generated SkyySacks 0.8.34"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.35 (2026-11-08)"):].rstrip() + "\n"

P.rep('''  stored in a bag stay in the pool (keyed by id) but no longer show / auto-sort until 0.8.34 is back (they are not lost).
"""
''', '''  stored in a bag stay in the pool (keyed by id) but no longer show / auto-sort until 0.8.34 is back (they are not lost).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.34"\n', 'VERSION = "0.8.35"\n')
P.rep('''; SkyyGear augments (Skyy_Aug_*) -> Combat (0.8.34)");''', '''; SkyyGear augments (Skyy_Aug_*) -> Combat (0.8.34); All really adds all, Furnace button bridge (0.8.35)");''')

# ---- 1. the count-only container (after BagMirror.rebuild)
P.rep('''public String rebuild(java.util.HashMap caps) {
  return rebuild(caps, (java.util.Set) null);
}""", mir))
''', '''public String rebuild(java.util.HashMap caps) {
  return rebuild(caps, (java.util.Set) null);
}""", mir))
# 0.8.35 (furnall): the true amounts. A COUNT-ONLY container (never paid from, never shown to a window): one stack per wanted item the pool holds - any size, so the
# engine's own matching (ids, resource types, exclusions) counts everything; the same rules as rebuild (bag home, loaded item, wants(), the virtual base stacks).
# One item is counted up to COUNT_MAX (no int overflow in the engine's sum; far past any queue or inventory).
mir.addField(CtField.make("public static final int COUNT_MAX = 1000000;", mir))
mir.addMethod(CtNewMethod.make(jt(r\'\'\'
public @SIC@ counts(java.util.HashMap caps, java.util.Set wanted) {
  java.util.ArrayList ids = new java.util.ArrayList();
  java.util.ArrayList qty = new java.util.ArrayList();
  if (wanted != null && caps != null) {
    java.util.Iterator it = @PKG@.SackPool.pool(this.key).entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry en = (java.util.Map.Entry) it.next();
      String id = (String) en.getKey();
      long cnt = ((Long) en.getValue()).longValue();
      String cat = @PKG@.SackDefs.homeOf(id);
      if (cat == null || !caps.containsKey(cat) || cnt <= 0L || !wants(wanted, id) || @PKG@.ProcBench.item(id) == null) continue;
      ids.add(id);
      qty.add(Long.valueOf(cnt));
    }
    java.util.ArrayList virt = virtuals(this.key, caps, wanted);
    for (int v = 0; v < virt.size(); v++) {
      Object[] vo = (Object[]) virt.get(v);
      ids.add(vo[0]);
      qty.add(vo[2]);
    }
  }
  int n = ids.size();
  @SIC@ c = new @SIC@((short) (n < 1 ? 1 : n));
  for (int s = 0; s < n; s++) {
    long q = ((Long) qty.get(s)).longValue();
    c.setItemStackForSlot((short) s, new @IS@((String) ids.get(s), q < (long) COUNT_MAX ? (int) q : COUNT_MAX));
  }
  return c;
}\'\'\'), mir))
''')

# ---- 2. the page's numbers + the true limit
P.rep('''  if (this.settling) return new {CIC}(new {IC}[] {{ p.getInventory().getCombinedBackpackStorageHotbar() }});
  return materialsFor(p, k, wanted);
}}""", cpg))
''', '''  if (this.settling) return new {CIC}(new {IC}[] {{ p.getInventory().getCombinedBackpackStorageHotbar() }});
  materialsFor(p, k, wanted);   // 0.8.35: the mirror's layout as before (open bench windows); the numbers come from the true counts
  return countMats(p, k, wanted);
}}""", cpg))
''')
P.rep('''cpg.addMethod(CtNewMethod.make(f"""
public static {CIC} materials({PLA} p, String k) {{
''', '''# 0.8.35 (furnall): the inventory + the true Void amounts - for COUNTING only (BagMirror.counts: never removed from)
cpg.addMethod(CtNewMethod.make(f"""
public static {CIC} countMats({PLA} p, String k, java.util.Set wanted) {{
  {PKG}.BagMirror m = {PKG}.BagMirror.of(k);
  m.sync();
  return new {CIC}(new {IC}[] {{ p.getInventory().getCombinedBackpackStorageHotbar(), m.counts({PKG}.SweepTask.caps(p.getInventory()), wanted) }});
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static {CIC} materials({PLA} p, String k) {{
''')

# ---- 3. procQueue: the true maximum, paid in rounds
P.rep('''  {CIC} mats = materialsFor(p, k, wantedOne(r));
  int lim = limit(r, mats);
  int qty = want <= 0 ? lim : (want < lim ? want : lim);
  if (qty > room) qty = room;
''', '''  java.util.Set w1 = wantedOne(r);
  {CIC} mats = materialsFor(p, k, w1);
  int lim = limit(r, countMats(p, k, w1));   // 0.8.35: the true maximum (every Void stack), the debit below in rounds
  int qty = want <= 0 ? lim : (want < lim ? want : lim);
  if (qty > room) qty = room;
''')
P.rep('''  int queuedN = 0; int guard = 0;
  StringBuilder audit = new StringBuilder();
  while (queuedN < qty && guard < 400) {{
    guard++;
    int n = res ? 1 : (qty - queuedN);
    java.util.List inputs = {CRM}.getInputMaterials(r, n);
''', '''  int queuedN = 0; int guard = 0;
  StringBuilder audit = new StringBuilder();
  // 0.8.35: the mirror holds a few stacks, the queue may want 1,000 units - when its stacks are used up: book them (sync) and rebuild it. Every pass queues at
  // least one unit or stops, so the guard is only a backstop. pk = the key: the old loop's "int k" shadows it inside the block.
  String pk = k;
  int consumed0 = 0;
  {PKG}.BagMirror rm = {PKG}.BagMirror.of(pk);
  while (queuedN < qty && guard < 40000) {{
    guard++;
    int offer = limit(r, mats);
    if (offer <= 0) {{
      consumed0 += rm.sync();
      mats = materialsFor(p, pk, w1);
      offer = limit(r, mats);
      if (offer <= 0) {{ audit.append(" short"); break; }}
    }}
    int n = res ? 1 : ((qty - queuedN) < offer ? (qty - queuedN) : offer);
    java.util.List inputs = {CRM}.getInputMaterials(r, n);
''')
P.rep('''    audit.append(" [").append(done).append("x ").append(unitInputs).append(" flag=").append(flag).append("]");
''', '''    if (audit.length() < 2000) audit.append(" [").append(done).append("x ").append(unitInputs).append(" flag=").append(flag).append("]");   // 0.8.35: a 1,000-unit click stays one short log line
''')
P.rep('''  {PKG}.BagMirror m = {PKG}.BagMirror.of(k);
  int consumed = m.sync();
  saveSoon(k);
  {PKG}.CraftLog.line(k, "QUEUE " + bench + " " + r.getId()''', '''  {PKG}.BagMirror m = {PKG}.BagMirror.of(k);
  int consumed = consumed0 + m.sync();   // 0.8.35: + the rounds
  saveSoon(k);
  {PKG}.CraftLog.line(k, "QUEUE " + bench + " " + r.getId()''')
P.rep('''(consumed > 0 ? " - " + consumed + " from the Void" : "") + sfMsg;
}}""", cpg))
''', '''(consumed > 0 ? " - " + consumed + " from the Void" : "") + sfMsg + (pb.queued() >= {PKG}.ProcBench.QUEUE_CAP ? " - the queue is full (" + {PKG}.ProcBench.QUEUE_CAP + " units)" : "");
}}""", cpg))
''')

# ---- 4. the instant tabs
P.rep('''cpg.addMethod(CtNewMethod.make(jt(r"""
public String craftOne(@REF@ ref, @ST@ st, @PLA@ p, java.util.UUID u, String k, @CRR@ r, int want, boolean campTab) {
''', '''# 0.8.35 (furnall): what the last craftOne really did (craftAll adds the rounds up)
cpg.addField(CtField.make("public int lastDone;", cpg))
cpg.addField(CtField.make("public int lastQty;", cpg))
cpg.addField(CtField.make("public int lastVoid;", cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public String craftOne(@REF@ ref, @ST@ st, @PLA@ p, java.util.UUID u, String k, @CRR@ r, int want, boolean campTab) {
''')
P.rep('''  int consumed = m.sync();
  if (consumed > 0) @PKG@.SackPool.saveSoon(k);
''', '''  int consumed = m.sync();
  if (consumed > 0) @PKG@.SackPool.saveSoon(k);
  this.lastDone = done; this.lastQty = qty; this.lastVoid = consumed;   // 0.8.35
''')
P.rep('''# a hub click that left this page open on screen is answered with a no-op update (the client's "Loading..." ends); never to a replaced page
''', '''# 0.8.35 (furnall): one /craft click (want = 0: All) through as many craftOne rounds as it takes - each round is one mirror's worth, booked and logged by craftOne as ever;
# the first round's refusals (locked, not enough ...) come back unchanged
cpg.addMethod(CtNewMethod.make(jt(r"""
public String craftAll(@REF@ ref, @ST@ st, @PLA@ p, java.util.UUID u, String k, @CRR@ r, int want, boolean campTab) {
  java.util.Set w1 = wantedOne(r);
  @CIC@ cnt = countMats(p, k, w1);
  @SIC@ accC = campTab ? null : @PKG@.AccLink.cont(@PKG@.AccLink.list(u, k), w1);
  @CIC@ all = accC == null ? cnt : new @CIC@(new @IC@[] { cnt, accC });
  int max = limit(r, all);
  int target = want > 0 ? (want < max ? want : max) : fitN(p, r, max);
  if (target <= 0) return craftOne(ref, st, p, u, k, r, want, campTab);
  int total = 0; int fromVoid = 0; int rounds = 0;
  String last = "";
  while (total < target && rounds < 4000) {
    rounds++;
    this.lastDone = 0; this.lastQty = 0; this.lastVoid = 0;
    last = craftOne(ref, st, p, u, k, r, target - total, campTab);
    if (this.lastDone <= 0) break;
    total += this.lastDone;
    fromVoid += this.lastVoid;
    if (this.lastDone < this.lastQty) break;
  }
  @MQ@ outq = r.getPrimaryOutput();
  String msg = rounds <= 1 ? last : ("crafted " + total + " x " + pretty(outq == null ? "?" : outq.getItemId()) + (fromVoid > 0 ? " (" + fromVoid + " from the Void)" : ""));
  if (total > 0 && want == 0 && target < max) msg = msg + " - your inventory is full, " + (max - total) + " more when you make room";
  return msg;
}"""), cpg))
# a hub click that left this page open on screen is answered with a no-op update (the client's "Loading..." ends); never to a replaced page
''')
P.rep('''# 0.8.11: the page view's counts + the Accessory Bag's accessories the shown recipes use (a copy - never crafted from here)
''', '''# 0.8.35 (furnall): can n crafts' outputs all go into the inventory (storage, hotbar, backpack - what craftOne fills)? The largest such n of max, at least 1 (as before: a
# single craft on a full inventory still drops one). DELIBERATE: All must not pour a whole bag's worth on the ground.
cpg.addMethod(CtNewMethod.make(jt(r"""
public static boolean fits(@IC@ dst, @CRR@ r, int n) {
  @MQ@[] outs = r.getOutputs();
  @MQ@ outq = r.getPrimaryOutput();
  if ((outs == null || outs.length == 0) && outq != null) outs = new @MQ@[] { outq };
  java.util.ArrayList l = new java.util.ArrayList();
  for (int q = 0; outs != null && q < outs.length; q++) {
    if (outs[q] == null || outs[q].getItemId() == null) continue;
    long t = (long) outs[q].getQuantity() * (long) n;
    if (t > 100000L) return false;
    l.add(new @IS@(outs[q].getItemId(), (int) t));
  }
  return l.isEmpty() || dst.canAddItemStacks(l);
}"""), cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public static int fitN(@PLA@ p, @CRR@ r, int max) {
  if (max <= 1) return max;
  @IC@ dst = p.getInventory().getCombinedStorageHotbarBackpack();
  if (fits(dst, r, max)) return max;
  int lo = 1; int hi = max;
  while (hi - lo > 1) {
    int md = (lo + hi) >>> 1;
    if (fits(dst, r, md)) lo = md; else hi = md;
  }
  return lo;
}"""), cpg))
# 0.8.11: the page view's counts + the Accessory Bag's accessories the shown recipes use (a copy - never crafted from here)
''')
P.rep('''    this.info = craftOne(ref, st, p, u, k, r, want, "K:camp".equals(this.tab));
''', '''    this.info = craftAll(ref, st, p, u, k, r, want, "K:camp".equals(this.tab));   // 0.8.35: rounds up to the true maximum
''')
P.rep('''    drawRow(b, ev, i, r, mats, lim, campTab ? campRowNote(p, u, k, r) : "", lim, false, "");
''', '''    drawRow(b, ev, i, r, mats, lim, campTab ? campRowNote(p, u, k, r) : "", fitN(p, r, lim), false, "");   // 0.8.35: All = what fits in the inventory
''')

# ---- 5. the Furnace button's bridge (SkyyGear 0.3.55)
P.rep('''chop.addConstructor(CtNewConstructor.make("public CraftHubOpen() { }", chop))
''', '''chop.addField(CtField.make("public String bench;", chop))   # 0.8.35: null = the hub tab; a bench = that sub-tab (sacks:fn:openFurnace)
chop.addConstructor(CtNewConstructor.make("public CraftHubOpen() { }", chop))
chop.addConstructor(CtNewConstructor.make("public CraftHubOpen(String bench) { this.bench = bench; }", chop))
''')
P.rep('''    pm.openCustomPage(r, st, new @PKG@.CraftPage(pr, (String) null));
    return Boolean.TRUE;
''', '''    if (this.bench != null) {   // 0.8.35: the same rule as the sub-tab (CraftPage.buildTabs): a charm, or the bench still holds work
      if (!@PKG@.CraftPage.benchShown(p, (java.util.UUID) o, this.bench)) return Boolean.FALSE;
      pm.openCustomPage(r, st, new @PKG@.CraftPage(pr, "P:" + this.bench));
      return Boolean.TRUE;
    }
    pm.openCustomPage(r, st, new @PKG@.CraftPage(pr, (String) null));
    return Boolean.TRUE;
''')
P.rep('''# ================= CraftCmd (/craft) =================
''', '''# 0.8.35: does the page show this timed bench's sub-tab for the player (buildTabs' rule)?
cpg.addMethod(CtNewMethod.make(jt(r"""
public static boolean benchShown(@PLA@ p, java.util.UUID u, String bench) {
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) k = @PKG@.SackPool.pkey(u);
  return accTier(accessories(p, u), bench) > 0 || @PKG@.ProcStore.pending(k, bench);
}"""), cpg))

# ================= CraftCmd (/craft) =================
''')
P.rep('''  sbr0.put("sacks:fn:count", new {PKG}.SackFn(0));
''', '''  sbr0.put("sacks:fn:openFurnace", new {PKG}.CraftHubOpen("Furnace"));   // 0.8.35: SkyyGear's Furnace button (UUID -> Boolean; world thread)
  sbr0.put("sacks:fn:count", new {PKG}.SackFn(0));
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.35 adds no system / command"
_i = P.s.index
assert _i("public @SIC@ counts(java.util.HashMap caps") < _i("public static {CIC} countMats(") < _i("public {CIC} viewMats(") < _i("public static int fitN(")     < _i("public void renderPage(") < _i("public String craftOne(") < _i("public String craftAll(") < _i("public static boolean benchShown(") < _i("CraftPage.benchShown(p,"), "0.8.35: methods before their callers"
P.finish()
