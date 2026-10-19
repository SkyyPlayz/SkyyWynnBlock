"""Derive SkyySacks/build_skyysacks_0.8.25.py from the SET pin 0.8.24 (the GENERATED build_skyysacks_0.8.24.py; edit THIS file, then
regenerate: python tools/sacks_0_8_25_patch.py; never re-run sacks_0_8_24_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.24 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_25_patch.py   then   python SkyySacks/build_skyysacks_0.8.25.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.25.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.25 (2026-10-19) = THE OFF-HAND REFILLS TOO (beta bug 11, docs/tests/2026-10-17-beta-bugs.md; research/Beta-Bugs-Triage-2026-10-17.md 11).
Skyy (beta video part 4 09:11, a torch in the off-hand): "Needs to pull from the off-hand if you got one there." + "yes, do the small beta bugs
15, 16, 11, 13".
  1. THE OFF-HAND (Inventory.getUtility(), VERIFIED in HytaleServer.jar) is a stack-refill target like the hotbar, in both refill modes
     (Hotbar only / Full inventory; Off = nothing, bags.refill off = nothing). A stack there of an item you USED since the last 2 s tick
     (its count across hotbar + storage + backpack + off-hand dropped - the same "used" rule as the hotbar, now counting the off-hand too)
     is topped up to its max stack from:
       (a) the Void, like a hotbar stack (the item's Void category, the pool holds some; the bag-full skip list honoured);
       (b) then the player's OWN storage + backpack stacks of the same item (OffhandAutofill's idea - Skyy's Mods folder,
           uk.phyre:OffhandAutofill 0.1.0, licence unknown, so learnt from, not packed). This is what makes a TORCH work: torches have no
           Void category. The hotbar is never a source (those stacks are what you hold).
     An off-hand slot that RAN OUT (held a plain stack of item X at the end of the last tick, empty now, X was used) is refilled with X
     the same way - that is the "torch ran out" case. A slot holding something else, a stack with metadata, a damaged / quality copy
     (plainFresh) or a non-stacking item (max stack 1: shields, the Menu item, Soul Orbs) is never touched.
  2. NO DUPES, NO LOSS: the off-hand slot is read before and after every insert; exactly what it GAINED leaves the source, AFTER the insert
     (pool: SackPool.add(-gained) + the live-mirror rule; inventory: removeItemStackFromSlot(slot, gained), read back - a source that did
     not drop by exactly that much puts BOTH slots back as they were and stops). More than asked = undone. One pass per tick.
  3. Memory only (no saved data): SackPool.SEENU = uuid -> the off-hand item ids at the end of the last tick (forgotten with SEENQ on relog
     / profile switch); SEENQ now includes the off-hand counts. A torch moved from storage to the off-hand forces a full rescan for the
     next tick's snapshot (no false "used").
  No new command / system / setting / bridge key. ROLLBACK to 0.8.24: safe (memory only) - the off-hand simply stops refilling.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.24.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.25.py"))
assert P.has('VERSION = "0.8.24"\n') and P.has("public static int pocketFill(@PLA@ p, String k, java.util.UUID u, java.util.HashMap capsIn, java.util.HashMap done) {") \
    and not P.has("SEENU"), "not the live generated SkyySacks 0.8.24"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.25 (2026-10-19)"):].rstrip() + "\n"

# ---- header, version
P.rep('''  costs naming Beech / Dry / Bottletree logs then count 0.8.23's 5-group log tiers) - Undo them in Server Setup -> Changes first if wanted.
"""
''', '''  costs naming Beech / Dry / Bottletree logs then count 0.8.23's 5-group log tiers) - Undo them in Server Setup -> Changes first if wanted.
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.24"\n', 'VERSION = "0.8.25"\n')

# ---- 3. SEENU: the off-hand ids at the end of the last tick (memory only)
P.rep('''sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEENQ = new java.util.concurrent.ConcurrentHashMap();", sp))
''', '''sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEENQ = new java.util.concurrent.ConcurrentHashMap();", sp))
# 0.8.25 (beta bug 11): SEENU = uuid -> String[] the off-hand (utility) item id per slot at the end of the last sweep tick (null = empty / not
# plain) - an off-hand slot that ran out is refilled with what it held. Memory only, forgotten with SEENQ.
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEENU = new java.util.concurrent.ConcurrentHashMap();", sp))
''')
P.rep('''public static void forgetSeen(java.util.UUID u) {
  if (u == null) return;
  SEENQ.remove(u);
}''', '''public static void forgetSeen(java.util.UUID u) {
  if (u == null) return;
  SEENQ.remove(u);
  SEENU.remove(u);   // 0.8.25
}''')

# ---- 1. + 2. the off-hand refill (SweepTask; before items(), its caller)
OFF = r"""# ================= 0.8.25 THE OFF-HAND REFILL (beta bug 11, Skyy "Needs to pull from the off-hand if you got one there.") =================
# utilCounts / utilIds: the off-hand (Inventory.getUtility()) as item id -> Long, and the plain item id per slot (SEENU)
swp.addMethod(CtNewMethod.make(jt(r'''
public static java.util.HashMap utilCounts(@INV@ inv) {
  java.util.HashMap out = new java.util.HashMap();
  if (inv == null) return out;
  @IC@ ut = inv.getUtility();
  if (ut == null) return out;
  short cap = ut.getCapacity();
  for (short s = 0; s < cap; s++) {
    @IS@ it = ut.getItemStack(s);
    if (it == null || it.isEmpty() || it.getItemId() == null) continue;
    Long v = (Long) out.get(it.getItemId());
    out.put(it.getItemId(), Long.valueOf((v == null ? 0L : v.longValue()) + (long) it.getQuantity()));
  }
  return out;
}'''), swp))
swp.addMethod(CtNewMethod.make(jt(r'''
public static String[] utilIds(@INV@ inv) {
  if (inv == null) return new String[0];
  @IC@ ut = inv.getUtility();
  if (ut == null) return new String[0];
  short cap = ut.getCapacity();
  if (cap < 0) cap = 0;
  String[] out = new String[(int) cap];
  for (short s = 0; s < cap; s++) {
    @IS@ it = ut.getItemStack(s);
    if (it == null || it.isEmpty() || !plainFresh(it)) continue;
    out[s] = it.getItemId();
  }
  return out;
}'''), swp))
# offFill: every off-hand slot holding (or, now empty, last tick holding) a plain stack of a USED item is topped up to its max stack - from
# the Void first (the hotbar refill's rules: the item's category, the pool, skip = sweepLeft), then from the player's storage + backpack
# stacks of that item (plainFresh only; the hotbar is never a source). Each insert is read back; the source pays exactly what the slot
# gained, AFTER the insert; an inventory source that does not drop by exactly that much puts both slots back and stops. Returns
# { from the Void, from the inventory }. World thread (the 2 s sweep). No KEPT change: the off-hand is never swept.
swp.addMethod(CtNewMethod.make(jt(r'''
public static int[] offFill(@PLA@ p, String k, java.util.UUID u, java.util.Set inUse, java.util.Set skip, java.util.HashMap caps) {
  int[] out = new int[] { 0, 0 };
  if (p == null || k == null || inUse == null || inUse.isEmpty()) return out;
  @INV@ inv = p.getInventory();
  if (inv == null) return out;
  @IC@ ut = inv.getUtility();
  if (ut == null) return out;
  String[] last = null;
  if (u != null) last = (String[]) @PKG@.SackPool.SEENU.get(u);
  @PKG@.BagMirror.beforeTake(k);   // live-mirror rule: book what a crafting window took before the pool is read
  @IC@[] srcs = new @IC@[] { inv.getStorage(), inv.getBackpack() };
  short cap = ut.getCapacity();
  for (short s = 0; s < cap; s++) {
    @IS@ it = ut.getItemStack(s);
    boolean empty = it == null || it.isEmpty();
    String id;
    org.bson.BsonDocument md = null;
    int q = 0;
    if (empty) {
      if (last == null || s >= last.length || last[s] == null) continue;
      id = last[s];
    } else {
      id = it.getItemId();
      if (id == null || !plainFresh(it)) continue;
      md = it.getMetadata();
      q = it.getQuantity();
    }
    if (!inUse.contains(id) || id.startsWith("Skyy_Sack_") || @PKG@.SackDefs.supplyItem(id)) continue;
    @ITM@ item = empty ? @PKG@.ProcBench.item(id) : it.getItem();
    int max = item == null ? 0 : item.getMaxStack();
    if (max <= 1 || q >= max) continue;
    // (a) the Void
    String cat = @PKG@.SackDefs.homeOf(id);
    long have = (cat == null || caps == null || !caps.containsKey(cat) || (skip != null && skip.contains(id))) ? 0L : @PKG@.SackPool.get(k, id);
    if (have > 0L) {
      int want = max - q;
      if ((long) want > have) want = (int) have;
      @IS@ b0 = ut.getItemStack(s);
      ut.addItemStackToSlot(s, md == null ? new @IS@(id, want) : new @IS@(id, want, md));
      @IS@ a0 = ut.getItemStack(s);
      int got = (a0 == null || a0.isEmpty() || !id.equals(a0.getItemId())) ? 0 : a0.getQuantity() - q;
      if (got > want) {
        if (b0 == null || b0.isEmpty()) ut.removeItemStackFromSlot(s); else ut.setItemStackForSlot(s, b0);
        @PKG@.SackPool.warn("off-hand refill: slot " + s + " (" + id + ") gained " + got + " of " + want + " asked - undone");
        continue;
      }
      if (got > 0) {
        @PKG@.SackPool.add(k, id, -(long) got);
        @PKG@.BagMirror.afterTake(k, id);   // live-mirror rule: the mirror never offers more than the pool now holds
        out[0] = out[0] + got;
        q += got;
        if (md == null && a0 != null) md = a0.getMetadata();
      }
    }
    // (b) the player's own storage + backpack
    boolean stop = false;
    for (int c = 0; c < srcs.length && q < max && !stop; c++) {
      @IC@ sc = srcs[c];
      if (sc == null) continue;
      short scap = sc.getCapacity();
      for (short s2 = 0; s2 < scap && q < max && !stop; s2++) {
        @IS@ src = sc.getItemStack(s2);
        if (src == null || src.isEmpty() || !id.equals(src.getItemId()) || !plainFresh(src)) continue;
        int take = max - q;
        if (take > src.getQuantity()) take = src.getQuantity();
        @IS@ b1 = ut.getItemStack(s);
        ut.addItemStackToSlot(s, md == null ? new @IS@(id, take) : new @IS@(id, take, md));
        @IS@ a1 = ut.getItemStack(s);
        int got = (a1 == null || a1.isEmpty() || !id.equals(a1.getItemId())) ? 0 : a1.getQuantity() - q;
        if (got <= 0) { stop = true; continue; }   // the slot takes no more
        if (got > take) {
          if (b1 == null || b1.isEmpty()) ut.removeItemStackFromSlot(s); else ut.setItemStackForSlot(s, b1);
          @PKG@.SackPool.warn("off-hand refill: slot " + s + " (" + id + ") gained " + got + " of " + take + " asked - undone");
          return out;
        }
        sc.removeItemStackFromSlot(s2, got);
        @IS@ a2 = sc.getItemStack(s2);
        int left = (a2 == null || a2.isEmpty() || !id.equals(a2.getItemId())) ? 0 : a2.getQuantity();
        if (src.getQuantity() - left != got) {
          sc.setItemStackForSlot(s2, src);
          if (b1 == null || b1.isEmpty()) ut.removeItemStackFromSlot(s); else ut.setItemStackForSlot(s, b1);
          @PKG@.SackPool.warn("off-hand refill: " + id + " from inventory slot " + s2 + " paid " + (src.getQuantity() - left) + " for " + got + " - both slots put back");
          return out;
        }
        out[1] = out[1] + got;
        q += got;
        if (md == null && a1 != null) md = a1.getMetadata();
      }
    }
  }
  return out;
}'''), swp))
"""
P.rep('''# 0.7.12: the 0.7.11 benchFed pause is gone - the live-mirror rule (BagMirror.beforeTake / afterTake inside refill) keeps a bench and the
''', OFF + '''# 0.7.12: the 0.7.11 benchFed pause is gone - the live-mirror rule (BagMirror.beforeTake / afterTake inside refill) keeps a bench and the
''')

# ---- items(): "used" counts the off-hand; the refill step adds the off-hand; the snapshot holds the off-hand
P.rep('''  java.util.HashMap before = carried(inv);
  java.util.HashSet used = new java.util.HashSet();''', '''  java.util.HashMap before = carried(inv);
  java.util.HashMap withU = addCounts(before, utilCounts(inv), 1L);   // 0.8.25: "used" counts the off-hand too
  java.util.HashSet used = new java.util.HashSet();''')
P.rep('''      Long now = (Long) before.get(se.getKey());''', '''      Long now = (Long) withU.get(se.getKey());''')
P.rep('''  if (mode != 2 && !used.isEmpty()) {
    try { out[1] = refill(p, k, mode, used, sweepLeft(inv, k, caps, now), done, caps); }
    catch (Throwable t2) { exact = false; rfail = true; @PKG@.KnowSync.warnOnce("stack refill failed: " + t2); }
  }''', '''  if (mode != 2 && !used.isEmpty()) {
    java.util.Set left = null;
    try { left = sweepLeft(inv, k, caps, now); out[1] = refill(p, k, mode, used, left, done, caps); }
    catch (Throwable t2) { exact = false; rfail = true; @PKG@.KnowSync.warnOnce("stack refill failed: " + t2); }
    // 0.8.25 (beta bug 11): the off-hand, both modes; an inventory -> off-hand move makes the snapshot a real scan
    if (left != null) {
      try {
        int[] off = offFill(p, k, u, used, left, caps);
        out[1] = out[1] + off[0] + off[1];
        if (off[1] > 0) exact = false;
      } catch (Throwable t4) { exact = false; rfail = true; @PKG@.KnowSync.warnOnce("off-hand refill failed: " + t4); }
    }
  }''')
P.rep('''  if (u != null) @PKG@.SackPool.SEENQ.put(u, exact ? addCounts(now, done, 1L) : carried(inv));''',
      '''  if (u != null) {
    @PKG@.SackPool.SEENQ.put(u, addCounts(exact ? addCounts(now, done, 1L) : carried(inv), utilCounts(inv), 1L));   // 0.8.25: + the off-hand
    @PKG@.SackPool.SEENU.put(u, utilIds(inv));
  }''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.25 adds no system / command"
assert P.s.index("public static int[] offFill(") < P.s.index("public static int[] items(@PLA@ p, String k, java.util.UUID u, java.util.HashMap capsIn)")
assert P.s.index("public static boolean plainFresh(") < P.s.index("public static String[] utilIds(")
P.finish()
