"""Derive SkyySacks/build_skyysacks_0.8.18.py from the SET pin 0.8.17 (the GENERATED build_skyysacks_0.8.17.py; edit THIS file, then
regenerate: python tools/sacks_0_8_18_patch.py; never re-run sacks_0_8_17_patch.py on top of it). The chain: ... -> sacks_0_8_17_patch.py ->
0.8.17 (generated, the SET pin) -> this patch -> 0.8.18. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.8.17 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_18_patch.py   then   python SkyySacks/build_skyysacks_0.8.18.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.18.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.18 = round FP1 (2026-10-17, Potion Flask + Food Pouch; research/Flask-Pouch-Spec.md 2.3 + 4.3). Skyy (docs/answered/skills.md
2026-10-16): healing potions and food go into the Flask / Pouch "automatically like our pockets" - "auto like the void, with a toggle";
"Cooked only" (raw food stays in the Void). SkyyCooking 0.1.11 owns both items and publishes the bridge key supply:fn:claims
(Function, Object[] {UUID player, String itemId} -> Boolean.TRUE when the Flask / Pouch takes that id NOW: auto-fill on for that
player's profile, not full, a fillable id; else FALSE / null; cheap + thread-safe). Absent (Cooking older / missing) = 0.8.17 behaviour.
  A. EATING BEATS STORING (SackPool.claimed = one ask; a Throwable = not claimed, warned once): before an id goes into the Void,
     - SweepTask.sweep (the 2 s sweep AND Deposit all): a claimed id stays in the inventory (asked once per distinct id per sweep pass,
       a memo map inside the pass; only for ids the Void would take); while a pass left claimed items behind (SweepTask.SUPSEEN) sigOf
       changes every 10 s, so the sweep looks again (a Pouch that got full / switched off lets the Void have them as before);
     - PickGive.split (every auto-pickup straight to the Void: block / mob drops, pet kills + felled logs (pickup2 with SkyyMobs), late
       felled-log drops): a claimed id goes into the player's STORAGE first (counted before / after), then the Void takes what did not
       fit (as before), then the vanilla pickup container (hotbar), then the feet - every move counted, the 0.8.3 undo covers all of it;
       PickGive.deliver passes the storage container (new 5-argument split; the 4-argument one = no storage, behaves as before);
     - PickHarv.move (F-harvest / sickle pickups the engine already put in the inventory): a claimed id is left there;
     - SackBridge.deposit (sacks:fn:deposit, Requip putting a hotbar stack away): a claimed id is refused (0 = it stays in the slot, the
       caller's documented "did not fit" path).
     Unchanged on purpose: the page's per-item Deposit button (an explicit choice of that item), PickHarv.onDrop (a FULL inventory
     threw the rest - the Void takes it as before, nothing else has room), raw food (claims answers FALSE unless SkyyCooking's
     supplies.pouchRaw is on).
  B. THE TWO LIFELONG ITEMS NEVER ENTER THE VOID: SackDefs.supplyItem(id) = the prefixes Skyy_Flask_ / Skyy_Food_Pouch_; homeOf -> null
     for them (so catOf / intake / voidRoom / sweep / Deposit / sacks:fn:deposit / the pages / the bench lists never route, store, list or
     sell them, whatever rule might match later).
  Saved data: none changed; no command / system / class / bridge key added. ROLLBACK to 0.8.17: safe (claimed ids go into the Void again;
  the Flask / Pouch already never matched a Void rule).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.17.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.18.py"))
assert P.has('VERSION = "0.8.17"\n') and P.has("fishPickTok") and not P.has("supply:fn:claims"), "not the live generated SkyySacks 0.8.17"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.18 = round FP1"):].rstrip() + "\n"

# ================================================================================================ header, version
P.rep('''  hint counts the Void fish; same pool files).
"""
''', '''  hint counts the Void fish; same pool files).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.17"\n', 'VERSION = "0.8.18"\n')

# ================================================================================================ B. the two lifelong items never pool
P.rep('''defs.addMethod(CtNewMethod.make(EN.sacks_home_java(), defs))
defs.addMethod(CtNewMethod.make("""
public static String homeOf(String itemId) {
  if (itemId == null) return null;
  if (itemId.startsWith("Skyy_Sack_")) return null;
''', '''defs.addMethod(CtNewMethod.make(EN.sacks_home_java(), defs))
# 0.8.18 (tools/sacks_0_8_18_patch.py B): SkyyCooking's Potion Flask + Food Pouch (lifelong, may carry metadata) never enter the Void
defs.addMethod(CtNewMethod.make("""
public static boolean supplyItem(String itemId) {
  return itemId != null && (itemId.startsWith("Skyy_Flask_") || itemId.startsWith("Skyy_Food_Pouch_"));
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static String homeOf(String itemId) {
  if (itemId == null) return null;
  if (itemId.startsWith("Skyy_Sack_")) return null;
  if (supplyItem(itemId)) return null;   // 0.8.18: the Flask / Pouch - never routed, stored, listed or sold
''')

# ================================================================================================ A. SackPool.claimed (one ask)
P.rep('''sp.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyySacks] " + msg); } catch (Throwable t) { }
}""", sp))
''', '''sp.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyySacks] " + msg); } catch (Throwable t) { }
}""", sp))
# 0.8.18 (tools/sacks_0_8_18_patch.py A): supply:fn:claims (SkyyCooking 0.1.11) - TRUE = the player's Flask / Pouch takes this id now, so
# it stays in (or goes to) the inventory instead of the Void. Absent / FALSE / null / a Throwable (warned once) = not claimed. memo = the
# caller's per-pass cache (id -> Boolean; null = no cache).
sp.addField(CtField.make("public static volatile boolean CLAIMWARN = false;", sp))
sp.addMethod(CtNewMethod.make("""
public static boolean claimed(java.util.UUID u, String id, java.util.HashMap memo) {
  if (u == null || id == null) return false;
  if (memo != null) {
    Object c = memo.get(id);
    if (c instanceof Boolean) return ((Boolean) c).booleanValue();
  }
  boolean r = false;
  try {
    Object f = bridge().get("supply:fn:claims");
    if (f instanceof java.util.function.Function) r = Boolean.TRUE.equals(((java.util.function.Function) f).apply(new Object[] { u, id }));
  } catch (Throwable t) {
    r = false;
    if (!CLAIMWARN) { CLAIMWARN = true; warn("supply:fn:claims failed (logged once; those items route into the Void as before): " + t); }
  }
  if (memo != null) memo.put(id, r ? Boolean.TRUE : Boolean.FALSE);
  return r;
}""", sp))
''')

# ================================================================================================ A. the sweep (2 s sweep + Deposit all)
P.rep('''  int moved = 0;
  // 0.8.10: the automatic sweep also takes whole fish from the hotbar + backpack''', '''  int moved = 0;
  java.util.HashMap supm = new java.util.HashMap();   // 0.8.18: supply:fn:claims answers, asked once per id in this pass
  // 0.8.10: the automatic sweep also takes whole fish from the hotbar + backpack''')
P.rep('''      if (onlyCat != null && !onlyCat.equals(cat)) continue;
''', '''      if (onlyCat != null && !onlyCat.equals(cat)) continue;
      if (stor != inv.getHotbar() && (it.getMetadata() == null || it.getMetadata().isEmpty()) && {PKG}.SackPool.claimed(su, id, supm)) continue;   // 0.8.18: the Flask / Pouch take it (eating beats storing) - it stays; only a plain storage / backpack stack is asked (review: a hotbar / metadata stack is never stranded)
''')

# a sweep that left claimed items in the storage re-runs every 10 s (sigOf) while they are there - the Flask / Pouch normally take them at
# once (an inventory change wakes the sweep anyway); once claims answers FALSE (full / auto-fill off) the Void gets them as before
P.rep('''# sweep matching items into the pool. onlyCat == null''', '''# 0.8.18: SUPSEEN = player uuid -> TRUE while their last sweep pass left claimed (supply:fn:claims) items in the inventory
swp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SUPSEEN = new java.util.concurrent.ConcurrentHashMap();", swp))
# sweep matching items into the pool. onlyCat == null''')
P.rep('''  return moved;
}}""", swp))
swp.addMethod(CtNewMethod.make(f"""
public static int sweep({PLA} p, String k, String onlyCat, boolean allContainers, java.util.HashMap swept) {{''', '''  if (su != null) {{ if (supm.containsValue(Boolean.TRUE)) SUPSEEN.put(su.toString(), Boolean.TRUE); else SUPSEEN.remove(su.toString()); }}   // 0.8.18
  return moved;
}}""", swp))
swp.addMethod(CtNewMethod.make(f"""
public static int sweep({PLA} p, String k, String onlyCat, boolean allContainers, java.util.HashMap swept) {{''')
P.rep('''  sb.append(@PKG@.SackPool.keepFlags(u)).append('|');   // 0.8.16''', '''  sb.append(SUPSEEN.containsKey(us) ? System.currentTimeMillis() / 10000L : 0L).append('|');   // 0.8.18: claimed items held = re-sweep every 10 s
  sb.append(@PKG@.SackPool.keepFlags(u)).append('|');   // 0.8.16''')

# ================================================================================================ A. auto-pickup straight to the Void
P.rep('''# THE SPLIT: Void first (booked), then the inventory; long[] { to the Void, to the inventory, left over } or null = nothing moved
pgv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long[] split(java.util.UUID u, String k, @IS@ s, @IC@ inv) {
  if (s == null || s.isEmpty() || s.getItemId() == null || s.getQuantity() <= 0) return null;
  String id = s.getItemId();
  int total = s.getQuantity();
  long room = voidRoom(u, k, s);
  long toVoid = room < (long) total ? room : (long) total;
  long booked = 0L;
  long toInv = 0L;
  try {
    if (toVoid > 0L) { @PKG@.SackPool.add(k, id, toVoid); booked = toVoid; }
    if (FAULT == 1) throw new IllegalStateException("harness fault 1 (after the Void booking)");
    long rest = (long) total - toVoid;
    if (rest > 0L && inv != null) {
      long before = countId(inv, id);
      try { inv.addItemStack(s.withQuantity((int) rest)); }
      finally { toInv = countId(inv, id) - before; }
      if (toInv < 0L) toInv = 0L;
      if (toInv > rest) throw new IllegalStateException("the inventory gained " + toInv + " of " + id + " but only " + rest + " were given");
    }
    if (FAULT == 2) throw new IllegalStateException("harness fault 2 (after the inventory add)");
    return new long[] { toVoid, toInv, (long) total - toVoid - toInv };
  } catch (Throwable t) {
    undo(k, s, inv, booked, toInv);
    @PKG@.SackPool.warn("auto-pickup of " + total + " " + id + " failed and was rolled back (the drop stays where it fell): " + t);
    return null;
  }
}\'\'\'), pgv))
''', '''# THE SPLIT: Void first (booked), then the inventory; long[] { to the Void, to the inventory, left over } or null = nothing moved
# 0.8.18 (tools/sacks_0_8_18_patch.py A): an id the Flask / Pouch claim (supply:fn:claims) goes into stor (the player's storage; null =
# inv) FIRST, then the Void takes what did not fit, then inv (the vanilla pickup container) the rest; every move counted, one undo
pgv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long[] split(java.util.UUID u, String k, @IS@ s, @IC@ inv, @IC@ stor) {
  if (s == null || s.isEmpty() || s.getItemId() == null || s.getQuantity() <= 0) return null;
  String id = s.getItemId();
  int total = s.getQuantity();
  long room = voidRoom(u, k, s);
  boolean sup = room > 0L && (s.getMetadata() == null || s.getMetadata().isEmpty()) && @PKG@.SackPool.claimed(u, id, (java.util.HashMap) null);   // review: plain stacks only
  @IC@ first = sup ? (stor != null ? stor : inv) : (@IC@) null;
  long toVoid = (sup && first != null) ? 0L : (room < (long) total ? room : (long) total);   // review LOW 7: no container at all = the Void as before
  long booked = 0L;
  long toInv = 0L;
  long toFirst = 0L;
  try {
    if (first != null) {
      long b0 = countId(first, id);
      try { first.addItemStack(s.withQuantity(total)); }
      finally { toFirst = countId(first, id) - b0; }
      if (toFirst < 0L) toFirst = 0L;
      if (toFirst > (long) total) throw new IllegalStateException("the storage gained " + toFirst + " of " + id + " but only " + total + " were given");
      long lo = (long) total - toFirst;
      toVoid = room < lo ? room : lo;
    }
    if (toVoid > 0L) { @PKG@.SackPool.add(k, id, toVoid); booked = toVoid; }
    if (FAULT == 1) throw new IllegalStateException("harness fault 1 (after the Void booking)");
    long rest = (long) total - toFirst - toVoid;
    if (rest > 0L && inv != null && inv != first) {
      long before = countId(inv, id);
      try { inv.addItemStack(s.withQuantity((int) rest)); }
      finally { toInv = countId(inv, id) - before; }
      if (toInv < 0L) toInv = 0L;
      if (toInv > rest) throw new IllegalStateException("the inventory gained " + toInv + " of " + id + " but only " + rest + " were given");
    }
    if (FAULT == 2) throw new IllegalStateException("harness fault 2 (after the inventory add)");
    return new long[] { toVoid, toFirst + toInv, (long) total - toVoid - toFirst - toInv };
  } catch (Throwable t) {
    undo(k, s, inv, booked, toInv);
    if (toFirst > 0L && first != null) {
      try { first.removeItemStack(s.withQuantity((int) (toFirst > (long) total ? (long) total : toFirst))); }   // review LOW 6: never more than the drop
      catch (Throwable t2) { @PKG@.SackPool.warn("auto-pickup rollback could not take " + toFirst + " " + id + " back out of a storage: " + t2); }
    }
    @PKG@.SackPool.warn("auto-pickup of " + total + " " + id + " failed and was rolled back (the drop stays where it fell): " + t);
    return null;
  }
}\'\'\'), pgv))
pgv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long[] split(java.util.UUID u, String k, @IS@ s, @IC@ inv) {
  return split(u, k, s, inv, (@IC@) null);
}\'\'\'), pgv))
''')
P.rep('''    @IC@ inv = pickInv(st, pref, s);
    long[] r = split(owner, k, s, inv);
''', '''    @IC@ inv = pickInv(st, pref, s);
    @IC@ stor = null;   // 0.8.18: a claimed id (Flask / Pouch) goes into the storage first
    try {
      @PLA@ pp = (@PLA@) st.getComponent(pref, @PLA@.getComponentType());
      stor = (pp == null || pp.getInventory() == null) ? (@IC@) null : pp.getInventory().getStorage();
    } catch (Throwable ts0) { stor = null; }
    long[] r = split(owner, k, s, inv, stor);
''')
P.rep('''  long room = @PKG@.PickGive.voidRoom(u, k, s);
  long m = room < want ? room : want;
  if (m <= 0L) return 0L;
  String id = s.getItemId();
''', '''  long room = @PKG@.PickGive.voidRoom(u, k, s);
  long m = room < want ? room : want;
  if (m <= 0L) return 0L;
  if ((s.getMetadata() == null || s.getMetadata().isEmpty()) && @PKG@.SackPool.claimed(u, s.getItemId(), (java.util.HashMap) null)) return 0L;   // 0.8.18: the Flask / Pouch take it - it stays (plain stacks only)
  String id = s.getItemId();
''')

# ================================================================================================ A. sacks:fn:deposit (Requip)
P.rep('''  String cat = @PKG@.SackDefs.catOf(id);
  if (cat == null) return 0L;
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) return 0L;
  @PLA@ p = playerOf(u);
''', '''  String cat = @PKG@.SackDefs.catOf(id);
  if (cat == null) return 0L;
  if (@PKG@.SackPool.claimed(u, id, (java.util.HashMap) null)) return 0L;   // 0.8.18: the Flask / Pouch take it - it stays in the slot
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) return 0L;
  @PLA@ p = playerOf(u);
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.18 adds no system / command"
P.finish()
