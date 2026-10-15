"""Derive SkyySacks/build_skyysacks_0.8.6.py from the SET pin 0.8.5 (the GENERATED build_skyysacks_0.8.5.py; edit THIS file, then
regenerate: python tools/sacks_0_8_6_patch.py; never re-run sacks_0_8_5_patch.py on top of it). Every anchor is asserted; at the end every
change is undone on a copy and compared with 0.8.5 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_6_patch.py   then   python SkyySacks/build_skyysacks_0.8.6.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.6.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.6 = FELLED LOG MISSED BY AUTO-PICKUP (lean round sacks086, 2026-10-15; Skyy tested chopping an Oak with the Crude Hatchet, auto-pickup
on: "the block i broke with my axe went on the ground. the rest went in the inventory.").
Why: the hit block's own drop IS claimed (PickBreakSys). Breaking it wakes the block physics; in the SAME World.tick the chunk store's
BlockPhysicsSystems$Ticking drops the unsupported log right above at (x+0.5, y+1, z+0.5). SkyySkills (0.4.39) snapshots the tree in the
break handler but only COMMITS its felled claims in BreakTask, queued with World.execute - and World.tick runs consumeTaskQueue AFTER the
chunk store tick (bytecode: consumeTaskQueue, entity store tick, chunk store tick, consumeTaskQueue). So for that first physics log
skill:fn:felledBy still answers null, PickBook.match finds nothing and the log stays on the ground. Later logs fall after the commit.
Fix (PickLate, one retry, nothing else changed):
1. PickItemSys.onEntityAdded: match() found NO claim at the item's spot (PickBook.find null), block pickup on, the spot is a block drop
   spot (x / z at .5, y whole) and SkyySkills' skill:fn:felledBy key exists (so felledBy just answered null) -> PickBook.late queues ONE
   PickLate with World.execute: the world's task queue is a FIFO Deque, so it runs right AFTER the already-queued BreakTask.
2. PickLate.run (world thread): the item ref still valid, pickup still on, PickBook.felled() asked AGAIN at the same spot; names a player
   -> counted as a felled-log claim (stats counter 10) and delivered by the existing PickGive.deliver (Void -> inventory -> feet, island
   rules, paused profiles, rollback - all unchanged). Still nobody / ref gone -> nothing happens, the item stays on the ground as before.
   No retry loop, no tick scan; items matched normally (and items when SkyySkills is absent) cost nothing extra.
3. /CRAFT FIRES CraftRecipeEvent$Pre (same round, Skyy: "was still able to craft a copper pickaxe"): the /craft page paid and handed out
   recipes itself, never through CraftingManager.craftItem, so SkyyGear's lifelong no-craft rule (lifelong.noCraft) and craft.belowBand
   never saw it. CraftPage.preCraft fires new CraftRecipeEvent$Pre(recipe, quantity) on the player's ref exactly like craftItem, after
   the material check and BEFORE anything is removed: cancelled (or the check throwing) = nothing used, nothing given, info line
   "this craft was refused - nothing was used" + a crafts.log CRAFT-REFUSED line. Pocket crafting (PocketCraftWindow / vanilla
   FieldCraftingWindow) and the bench link already craft through craftItem (Pre fired - unchanged). Not changed: the Furnace / Tannery
   timed queue (procQueue; no tool recipes) and sacks:fn:craftPay (SkyyGear's Smithing Craft tab, which filters tools itself).
4. No saved-data change, no new command / system / setting / bridge key. ROLLBACK to 0.8.5: safe (that first log stays on the ground and
   /craft stops firing the event).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.5.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.6.py"))
assert P.has('VERSION = "0.8.5"\n') and P.has("SackSnd") and not P.has("PickLate"), "not the live generated SkyySacks 0.8.5"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.6 = FELLED LOG"):].rstrip() + "\n"

# ---------- header + version
P.rep('''4. No saved-data change, no new command, no bridge key written. ROLLBACK to 0.8.4: safe (0.8.4 never reads sounds.properties).
"""
''', '''4. No saved-data change, no new command, no bridge key written. ROLLBACK to 0.8.4: safe (0.8.4 never reads sounds.properties).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.5"\n', 'VERSION = "0.8.6"\n')

# ---------- the class declaration (next to the other auto-pickup classes)
P.rep('''pds = pool.makeClass(PKG + ".PickDropSys", pool.get(EES))
''', '''pds = pool.makeClass(PKG + ".PickDropSys", pool.get(EES))
plt = pool.makeClass(PKG + ".PickLate")   # 0.8.6: the one late retry of an unclaimed block-spot drop (tools/sacks_0_8_6_patch.py)
''')

# ---------- PickLate fields + constructor, then PickBook.late (right after PickBook.match)
P.rep('''# a new item entity (PickItemSys.onEntityAdded): the claim at its exact spot (else a felled log), or into the ring
''', '''# ---- 0.8.6 PickLate (fields + constructor here: PickBook.late queues it; run() comes after PickGive.deliver): Runnable on the world thread
plt.addInterface(pool.get("java.lang.Runnable"))
for _f in (jt("public @REF@ ref;"), jt("public @ST@ st;"), "public String w;", "public double x;", "public double y;", "public double z;",
           "public int result;"):
    plt.addField(CtField.make(_f, plt))
plt.addConstructor(CtNewConstructor.make(jt("public PickLate(@ST@ st, @REF@ ref, String w, double x, double y, double z) { this.st = st; this.ref = ref; this.w = w; this.x = x; this.y = y; this.z = z; this.result = -9; }"), plt))
# a new item entity (PickItemSys.onEntityAdded): the claim at its exact spot (else a felled log), or into the ring
''')
P.rep('''  if (c == null && @PKG@.SackCfg.PICK_MOBS && ref != null) {
    @PKG@.PickRing r = ring(w);
    if (r != null) r.push(ref, x, y, z, now);
  }
  return c;
}\'\'\'), pbk))
''', '''  if (c == null && @PKG@.SackCfg.PICK_MOBS && ref != null) {
    @PKG@.PickRing r = ring(w);
    if (r != null) r.push(ref, x, y, z, now);
  }
  return c;
}\'\'\'), pbk))
# 0.8.6: match() gave null. NO claim at the spot + block pickup on + a block drop spot + SkyySkills' felledBy key present = felledBy just
# answered null (a physics log falling before SkyySkills' BreakTask committed the tree) -> ONE PickLate on the world's FIFO task queue,
# behind that BreakTask. EXEC = harness seam (always null in the game): Consumer of the PickLate instead of World.execute. Returns queued.
pbk.addField(CtField.make("public static volatile java.util.function.Consumer EXEC;", pbk))
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean late(@ST@ st, @REF@ ref, String w, double x, double y, double z, long now) {
  if (st == null || ref == null || w == null || !@PKG@.SackCfg.PICK_BLOCKS || !blockSpot(x, y, z)) return false;
  if (!(@PKG@.SackPool.bridge().get("skill:fn:felledBy") instanceof java.util.function.Function)) return false;
  if (find(w, x, y, z, now) != null) return false;   // a claim was there (contested / pickup kind off): match() decided, no retry
  @PKG@.PickLate t = new @PKG@.PickLate(st, ref, w, x, y, z);
  try {
    java.util.function.Consumer ex = EXEC;
    if (ex != null) ex.accept(t);
    else ((@EST@) st.getExternalData()).getWorld().execute(t);
    return true;
  } catch (Throwable e) { warnOnce("pick11", "auto-pickup: could not queue the late felled-log check (logged once; that drop stays on the ground): " + e); return false; }
}\'\'\'), pbk))
''')

# ---------- PickLate.run (after PickGive.deliver, next to PickDeliver.accept)
P.rep('''  if (o instanceof @ST@) this.result = @PKG@.PickGive.deliver((@ST@) o, this.ref, this.owner, this.kind);
}\'\'\'), pdl))
''', '''  if (o instanceof @ST@) this.result = @PKG@.PickGive.deliver((@ST@) o, this.ref, this.owner, this.kind);
}\'\'\'), pdl))
# ---- 0.8.6 PickLate.run: the item still there + felledBy names a player NOW -> a felled-log claim, delivered like any claimed drop
plt.addMethod(CtNewMethod.make(jt(r\'\'\'
public void run() {
  try {
    if (this.st == null || this.ref == null || !this.ref.isValid()) { this.result = -2; return; }
    if (!@PKG@.SackCfg.PICK_ON || !@PKG@.SackCfg.PICK_BLOCKS) { this.result = -3; return; }
    java.util.UUID f = @PKG@.PickBook.felled(this.w, this.x, this.y, this.z);
    if (f == null) { this.result = -4; return; }
    @PKG@.PickBook.n(10, 1L);
    this.result = @PKG@.PickGive.deliver(this.st, this.ref, f, 1);
  } catch (Throwable t) { @PKG@.PickBook.warnOnce("pick12", "auto-pickup: late felled-log check failed (logged once; that drop stays on the ground): " + t); }
}\'\'\'), plt))
''')

# ---------- the call site: PickItemSys.onEntityAdded (same world name + time for match and the retry)
P.rep('''    @PKG@.PickClaim c = @PKG@.PickBook.match(@PKG@.PickBook.world(st.getExternalData()), p.x, p.y, p.z, ref, System.nanoTime());
    if (c == null) return;
    cb.run(new @PKG@.PickDeliver(ref, c.owner, c.kind, cb));''', '''    String wn = @PKG@.PickBook.world(st.getExternalData());
    long now = System.nanoTime();
    @PKG@.PickClaim c = @PKG@.PickBook.match(wn, p.x, p.y, p.z, ref, now);
    if (c == null) { @PKG@.PickBook.late(st, ref, wn, p.x, p.y, p.z, now); return; }   // 0.8.6: one late felled-log check
    cb.run(new @PKG@.PickDeliver(ref, c.owner, c.kind, cb));''')

# ---------- 0.8.6 (2): /craft fires CraftRecipeEvent$Pre before it pays (Skyy: "was still able to craft a copper pickaxe")
# CraftPage.handleDataEvent removed the materials and handed out the output itself - it never went through CraftingManager.craftItem, so
# no CraftRecipeEvent$Pre: SkyyGear's lifelong no-craft rule (and craft.belowBand) never saw a /craft click. Pocket crafting
# (PocketCraftWindow / vanilla FieldCraftingWindow) and the benches DO go through craftItem (Pre fired, a cancel stops it before any input
# is taken - VERIFIED bytecode). Now /craft fires the same event (new CraftRecipeEvent$Pre(recipe, quantity) on the player's ref, like
# craftItem) after the material check and BEFORE anything is removed; cancelled = nothing paid, nothing given, a crafts.log line.
P.rep('''}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{''', '''}}""", cpg))
# 0.8.6: CraftRecipeEvent$Pre exactly as CraftingManager.craftItem fires it (store.invoke(ref, new Pre(recipe, quantity))); true = go on.
# A throw counts as refused (craftItem would throw too) - one WARN, nothing is paid.
cpg.addMethod(CtNewMethod.make(f"""
public static boolean preCraft({ST} st, {REF} ref, {CRR} r, int qty) {{
  try {{
    com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Pre e = new com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Pre(r, qty);
    st.invoke(ref, e);
    return !e.isCancelled();
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("/craft: the CraftRecipeEvent check failed - the craft was refused, nothing was used: " + t); return false; }}
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{''')
P.rep('''    if (!mats.canRemoveMaterials(inputs)) {{ this.info = "not enough materials"; rebuild(); return; }}
    java.util.HashMap snapB = snapshot(mats);''', '''    if (!mats.canRemoveMaterials(inputs)) {{ this.info = "not enough materials"; rebuild(); return; }}
    // 0.8.6: CraftRecipeEvent$Pre before anything is paid (SkyyGear's lifelong no-craft rule, craft.belowBand); cancelled = nothing used
    if (!preCraft(st, ref, r, qty)) {{
      {PKG}.CraftLog.line(k, "CRAFT-REFUSED " + r.getId() + " x" + qty + " (CraftRecipeEvent$Pre cancelled - nothing used)");
      this.info = "this craft was refused - nothing was used";
      rebuild();
      return;
    }}
    java.util.HashMap snapB = snapshot(mats);''')

# ---------- write the class
P.rep('''          phv, pht, phs, pds):   # 0.8.4: harvest -> Void first
''', '''          phv, pht, phs, pds,   # 0.8.4: harvest -> Void first
          plt):   # 0.8.6: PickLate
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "no system / command added"
_i = P.s.index
assert _i('plt.addConstructor(') < _i("public static boolean late(") < _i("public static int deliver(@ST@ st") < _i("plt.addMethod(") < _i("PickBook.late(st, ref, wn")
P.finish()
