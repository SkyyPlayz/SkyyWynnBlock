"""Derive SkyySacks/build_skyysacks_0.8.4.py from the SET pin 0.8.3 (the GENERATED build_skyysacks_0.8.3.py; edit THIS file, then
regenerate: python tools/sacks_0_8_4_patch.py; never re-run sacks_0_8_3_patch.py on top of it).
Run:  python tools/sacks_0_8_4_patch.py   then   python SkyySacks/build_skyysacks_0.8.4.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.4.py   (every 0.8.3 no-dupe proof + the 0.8.4 paths below)

0.8.4 = AUTO-PICKUP FOLLOW-UPS (docs/answered/bags.md 2026-10-13 AUTO-PICKUP, Skyy word for word: "ohhh yeahhh! in hypixle skyblock,
items go straight in your inventory, they never fall on the ground. can we do that too?" + "both. more loot to top damager."; overnight
go-ahead "work through your list, i need to go to bed."). Pairs with SkyyMobs 0.1.8 (deploy together).

1. PET KILLS -> THE OWNER. PickDeathMark.killer: a killing blow whose Damage$EntitySource is not a player but a creature SkyyPets names
   as a player's pet / summon (bridge pets:fn:ownerOf: entity UUID -> owner UUID or String; PickBook.petOwner) counts as the OWNER's
   killing blow; SkyyMobs 0.1.8 credits the pet's damage to the owner too, so "top damager" = owner + pet. Everything after that is
   0.8.3's rule unchanged: the owner must be online in the SAME world (PickBook.here) - an owner who is offline or in another world gets
   nothing and the drop stays on the ground exactly as vanilla (never duplicated, never handed to someone else). SkyyPets 0.2.4 pets do
   not fight (Invulnerable + Intangible, no attack role) and SkyyPets has no pets:fn:ownerOf yet - SkyyPets 0.4 (kill credit) adds the
   key, or rewrites a pet's Damage source to the owner (the P7 probe path), which 0.8.3 already treats as the owner's own blow.

2. F-HARVEST (and every other "interactive" pickup) -> THE VOID FIRST. The engine hands F-harvested crops (FarmingUtil.giveDrops <-
   HarvestCropInteraction, sickle swings too) and F-picked loose blocks (BlockHarvestUtils.performPickupByInteraction) straight to the
   player through ItemUtils.interactivelyPickupItem (VERIFIED 0.7 bytecode): fire InteractivelyPickupItemEvent on the player (cancellable),
   re-read its stack, Player.giveItem = the vanilla pickup container (InventoryUtils.getContainerForItemPickup), the remainder that did
   not fit -> ItemUtils.dropItem -> throwItem, which fires the cancellable DropItemEvent$Drop on the player and then spawns the thrown
   stack. SkyySkills (sickle XP), SkyyCollections (crop collections) and SkyyQuests (gather / collect) READ that event later on the world
   thread and skip a cancelled one - so 0.8.4 never cancels or changes it (cancelling would cost the player XP, collections and quests).
   Instead:
     PickHarvSys (InteractivelyPickupItemEvent, players): notes the event + the pickup container's count of that item BEFORE giveItem,
       queues ONE PickHarvTask per player (World.execute = after the interaction, after every listener) and opens a 100 ms overflow
       window for that item + amount.
     PickDropSys (DropItemEvent$Drop, players): only inside that window, same item, at most the harvested amount (the giveItem remainder
       of a full inventory): books what the Void takes and CANCELS the throw (all fit) or shrinks the thrown stack to the rest (it lands
       at the player's feet as vanilla). A player's own Q-drop never matches (no window).
     PickHarvTask: for every NOT-cancelled event: arrived = the container's count now - before (never more than the event's stack) ->
       PickHarv.move books min(arrived, Void room) and takes exactly that out of the same container (measured before / after: booked =
       what really left; a fault puts the items back and un-books). Result: Void first, then the inventory, the feet only when both are
       full - the same rule as block drops. Void full = the items simply stay in the inventory (vanilla).
   Rules shared with 0.8.3: pickup.on + pickup.blocks (its help already says "harvested"); nothing moves while the player's item moves
   are paused (SackPool.settledKey null: profile switch / crash recovery / shutdown); plain stacks only (voidRoom = the /pd Deposit rule;
   cooked food stays out unless bags.cookedFood); island pickup rules for the thrown overflow (island:perm:fn "pickup"). The vanilla
   "picked up" popup still shows for what reached the inventory (it comes from giveItem; changing the event would break the readers
   above); our feed card says where it went ("Wheat > Void"); our sound is skipped (vanilla already played one).
   FIX ROUND (critics): the popup is Player.notifyPickupItem, called by interactivelyPickupItem right after giveItem (VERIFIED 0.7
   bytecode) and gated only by the world's GameplayConfig ShowItemPickupNotifications (world-wide) - no per-item way to skip it without
   changing the event; our cards do not spam (flush merges per item per tick, SkyyHud merges the same item within feed.mergeSecs).
   The overflow window also needs the pickup container to be FULL for that item (canAddItemStack(1) false): a Q-drop removes its
   stack from the inventory before the throw (InventoryPacketHandler, VERIFIED), so it never matches. A pending harvest list older
   than HSTALE_NS (5 s: its task never ran, e.g. a world torn down) is dropped and a fresh task queued, so a player can never get
   stuck with no harvest move. the pickup.blocks Server Setup help now says what Off does for harvests (they stay in the inventory).

3. SKYYQUESTS 'collect' (read SkyyQuests/build_skyyquests_0.2.py, not edited): "collect" is an alias of "gather" = it counts the
   InteractivelyPickupItemEvent itself (QEvTask, cancel-checked) and quest:fn:event calls - never items held in the inventory. 0.8.4
   leaves that event untouched, so F-harvests sent to the Void still count. No SkyyQuests change needed.

Lag (research/Code-Structure-Audit.md): event-driven only - one map write per interactive pickup, one World.execute per player per tick
with pickups, the drop check is one map read; no tick scan, no file on the world thread (the pool is saved by the private writer).
Classes: new PickHarv, PickHarvTask, PickHarvSys, PickDropSys; PickBook (+ petOwner, + HARV_OK / DROP_OK, ~ state / stats);
PickDeathMark (~ killer); the plugin (~ setup: 2 systems). No new row, file, command, bridge key or saved-data format; rollback to 0.8.3
safe (harvests go to the inventory again; pet kills stop counting for their owner).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "SkyySacks")
src = os.path.join(HERE, "build_skyysacks_0.8.3.py")
dst = os.path.join(HERE, "build_skyysacks_0.8.4.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.8.3"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"
assert 'VERSION = "0.8.3"' in s and "PickGive" in s and "PickHarv" not in s, "not the live generated 0.8.3"
SYS0 = s.count("registerSystem(")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:90]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:90])
    s = s.replace(old, new)


GONE_OK = set()


def gone(*lines):
    for ln in lines:
        GONE_OK.add(ln)


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''Server Setup > SkyyVoid and Crafting > Auto-pickup. Details: the patch docstring.
"""
''', '''Server Setup > SkyyVoid and Crafting > Auto-pickup. Details: the patch docstring.
0.8.4 (derived from 0.8.3 by tools/sacks_0_8_4_patch.py - edit the patch, not this file; auto-pickup follow-ups): a mob killed by a
player's pet / summon gives its loot to the pet's OWNER (SkyyPets bridge pets:fn:ownerOf; owner offline / in another world = vanilla);
F-harvested crops and F-picked loose blocks go to the Void first (the inventory part is moved right after the engine's own giveItem, the
overflow of a full inventory is caught before it is thrown) - the pickup event other mods count is never changed. Details: the patch.
"""
''')
rep('VERSION = "0.8.3"\n', 'VERSION = "0.8.4"\n')
gone('VERSION = "0.8.3"')

# ---------------------------------------------------------------------------------------------------------------- engine aliases
rep('''            "I18N": "com.hypixel.hytale.server.core.modules.i18n.I18nModule",
''', '''            "I18N": "com.hypixel.hytale.server.core.modules.i18n.I18nModule",
            # 0.8.4: the interactive pickup (F-harvest / F-pickup) and the throw of its overflow (VERIFIED 0.7 bytecode)
            "IPE": "com.hypixel.hytale.server.core.event.events.ecs.InteractivelyPickupItemEvent",
            "DIE": "com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$Drop",
''')

# ---------------------------------------------------------------------------------------------------------------- classes
rep('''pss = pool.makeClass(PKG + ".PickShareSys", pool.get(_JT["ETS"]))
''', '''pss = pool.makeClass(PKG + ".PickShareSys", pool.get(_JT["ETS"]))
# 0.8.4: pet kills -> owner (PickBook.petOwner), F-harvest -> the Void first (tools/sacks_0_8_4_patch.py docstring)
phv = pool.makeClass(PKG + ".PickHarv")
pht = pool.makeClass(PKG + ".PickHarvTask")
phs = pool.makeClass(PKG + ".PickHarvSys", pool.get(EES))
pds = pool.makeClass(PKG + ".PickDropSys", pool.get(EES))
''')

# ---------------------------------------------------------------------------------------------------------------- PickBook.petOwner (before PickDeathMark.killer)
rep('''# SkyyMobs 0.1.7 mob:fn:credit (take): Object[] { top, topDamage, total, killing blow, players } or null
''', '''# 0.8.4: the OWNER of a pet / summon creature (SkyyPets bridge pets:fn:ownerOf: entity UUID -> owner UUID or String) or null; no key =
# null at once; a key that throws or answers anything but a UUID = null (never the wrong player)
pbk.addField(CtField.make("public static volatile boolean HARV_OK = false;", pbk))
pbk.addField(CtField.make("public static volatile boolean DROP_OK = false;", pbk))
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static java.util.UUID petOwner(@ST@ st, @REF@ r) {
  Object f = @PKG@.SackPool.bridge().get("pets:fn:ownerOf");
  if (!(f instanceof java.util.function.Function) || st == null || r == null) return null;
  try {
    @UUIDC@ uc = (@UUIDC@) st.getComponent(r, @UUIDC@.getComponentType());
    if (uc == null || uc.getUuid() == null) return null;
    Object o = ((java.util.function.Function) f).apply(uc.getUuid());
    if (o instanceof java.util.UUID) return (java.util.UUID) o;
    if (o instanceof String) return java.util.UUID.fromString(((String) o).trim());
    return null;
  } catch (Throwable t) { return null; }
}\'\'\'), pbk))
# SkyyMobs 0.1.7 mob:fn:credit (take): Object[] { top, topDamage, total, killing blow, players } or null
''')
rep('''    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    return pr == null ? null : pr.getUuid();
  } catch (Throwable t) { return null; }
}\'\'\'), pdm))''', '''    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr != null) return pr.getUuid();
    return @PKG@.PickBook.petOwner(st, r);   // 0.8.4: a pet's / summon's killing blow = its owner's
  } catch (Throwable t) { return null; }
}\'\'\'), pdm))''')
gone("    return pr == null ? null : pr.getUuid();")

# state / stats name the new paths
rep('''    + (@PKG@.SackPool.bridge().get("mob:fn:credit") instanceof java.util.function.Function ? "SkyyMobs" : "killer only (no mob:fn:credit yet)") + ")";''',
    '''    + (@PKG@.SackPool.bridge().get("mob:fn:credit") instanceof java.util.function.Function ? "SkyyMobs" : "killer only (no mob:fn:credit yet)")
    + ", pets " + (@PKG@.SackPool.bridge().get("pets:fn:ownerOf") instanceof java.util.function.Function ? "count for their owner" : "not fighting yet (no pets:fn:ownerOf)")
    + ", F-harvest " + (HARV_OK && @PKG@.SackCfg.PICK_BLOCKS ? "Void first" : "OFF") + (DROP_OK ? "" : " (no overflow catch)") + ")";''')
rep('''    + N.get(12) + " contested, " + N.get(8) + " rolled back";''', '''    + N.get(12) + " contested, " + N.get(8) + " rolled back; F-harvest " + N.get(14) + " items to the Void (+ " + N.get(15)
    + " caught before a full inventory threw them)";''')
rep('''# 12 contested claims (review fix 3), 13 skipped while item moves are paused for that player (review fix 1)
''', '''# 12 contested claims (review fix 3), 13 skipped while item moves are paused for that player (review fix 1)
# 0.8.4: 14 F-harvest items moved to the Void, 15 overflow items caught before the throw
''')

# ---------------------------------------------------------------------------------------------------------------- the harvest code (after the 0.8.3 block)
HARV = r'''
# ================= 0.8.4 F-HARVEST -> THE VOID FIRST (tools/sacks_0_8_4_patch.py docstring, point 2) =================
for _c, _m in ((_JT["IPE"], "getItemStack"), (_JT["IPE"], "isCancelled"), (_JT["DIE"], "getItemStack"), (_JT["DIE"], "setItemStack"),
               (_JT["DIE"], "setCancelled"), (_JT["DIE"], "isCancelled"), (WLD, "execute"), (IC, "removeItemStack"), (IC, "canAddItemStack")):
    B.probe(pool, _c, _m)
# PickHarvTask (fields + constructor first: PickHarv.note queues it; run() after PickHarv.flush): Runnable on the world thread
pht.addInterface(pool.get("java.lang.Runnable"))
pht.addField(CtField.make("public java.util.UUID u;", pht))
pht.addField(CtField.make(jt("public @ST@ st;"), pht))
pht.addField(CtField.make("public long moved;", pht))
pht.addConstructor(CtNewConstructor.make(jt("public PickHarvTask(java.util.UUID u, @ST@ st) { this.u = u; this.st = st; this.moved = -1L; }"), pht))
# PickHarv: HPEND = player UUID -> ArrayList of Object[] { event, item id, Long count before giveItem, the pickup container } (world thread);
# HCUR = player UUID -> Object[] { item id, Long amount, Long nanoTime } = the overflow window of the newest pickup
for _f in ("public static final java.util.concurrent.ConcurrentHashMap HPEND = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap HCUR = new java.util.concurrent.ConcurrentHashMap();",
           "public static final long WINDOW_NS = 100000000L;",
           # fix round: player UUID -> Long nanoTime the pending task was queued; a list older than HSTALE_NS is never appended to
           "public static final java.util.concurrent.ConcurrentHashMap HPT = new java.util.concurrent.ConcurrentHashMap();",
           "public static final long HSTALE_NS = 5000000000L;",
           # harness seam (always null in the game): Consumer of the PickHarvTask instead of World.execute
           "public static volatile java.util.function.Consumer EXEC;"):
    phv.addField(CtField.make(_f, phv))
# move up to want of s from cont into the Void (book first, then take out exactly; what really left = what stays booked). Returns moved.
# Faults (harness): 4 after the booking, 5 after the removal -> the items go back into cont and the booking is undone.
phv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long move(java.util.UUID u, String k, @IS@ s, @IC@ cont, long want) {
  if (u == null || k == null || s == null || cont == null || want <= 0L) return 0L;
  long room = @PKG@.PickGive.voidRoom(u, k, s);
  long m = room < want ? room : want;
  if (m <= 0L) return 0L;
  String id = s.getItemId();
  long booked = 0L;
  long removed = 0L;
  try {
    @PKG@.SackPool.add(k, id, m);
    booked = m;
    if (@PKG@.PickGive.FAULT == 4) throw new IllegalStateException("harness fault 4 (after the harvest booking)");
    long c0 = @PKG@.PickGive.countId(cont, id);
    try { cont.removeItemStack(s.withQuantity((int) m)); }
    finally { removed = c0 - @PKG@.PickGive.countId(cont, id); }
    if (removed < 0L) removed = 0L;
    if (removed > m) throw new IllegalStateException("the inventory lost " + removed + " of " + id + " but only " + m + " were taken");
    if (@PKG@.PickGive.FAULT == 5) throw new IllegalStateException("harness fault 5 (after the harvest removal)");
    if (removed < m) @PKG@.SackPool.add(k, id, removed - m);
    return removed;
  } catch (Throwable t) {
    if (removed > 0L) {
      try { cont.addItemStack(s.withQuantity((int) removed)); }
      catch (Throwable t2) { @PKG@.SackPool.warn("auto-pickup (harvest) rollback could not put " + removed + " " + id + " back: " + t2); }
    }
    if (booked > 0L) @PKG@.SackPool.add(k, id, -booked);
    @PKG@.PickBook.n(8, 1L);
    @PKG@.SackPool.warn("auto-pickup of a harvested " + id + " failed and was rolled back (it stays in the inventory): " + t);
    return 0L;
  }
}\'\'\'), phv))
# PickHarvSys (world thread, inside the engine's interactivelyPickupItem, BEFORE giveItem): note it, count before, open the window
phv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean note(@ST@ st, @REF@ pref, java.util.UUID u, Object ev, @IS@ s) {
  if (st == null || pref == null || u == null || ev == null || s == null || s.isEmpty() || s.getItemId() == null) return false;
  @IC@ cont = @PKG@.PickGive.pickInv(st, pref, s);
  long before = cont == null ? 0L : @PKG@.PickGive.countId(cont, s.getItemId());
  long now = System.nanoTime();
  HCUR.put(u, new Object[] { s.getItemId(), Long.valueOf((long) s.getQuantity()), Long.valueOf(now), cont });
  Object[] rec = new Object[] { ev, s.getItemId(), Long.valueOf(before), cont };
  Object o = HPEND.get(u);
  Object qt = HPT.get(u);
  if (o instanceof java.util.ArrayList && qt instanceof Long && now - ((Long) qt).longValue() <= HSTALE_NS) { ((java.util.ArrayList) o).add(rec); return true; }
  if (o != null) @PKG@.PickBook.warnOnce("pick10", "auto-pickup: a harvest move never ran (its world closed?) - dropped it, those items stay in the inventory (logged once)");
  java.util.ArrayList l = new java.util.ArrayList();
  l.add(rec);
  HPEND.put(u, l);
  HPT.put(u, Long.valueOf(now));
  @PKG@.PickHarvTask task = new @PKG@.PickHarvTask(u, st);
  try {
    java.util.function.Consumer ex = EXEC;
    if (ex != null) ex.accept(task);
    else ((@EST@) st.getExternalData()).getWorld().execute(task);
  } catch (Throwable t) { HPEND.remove(u); HPT.remove(u); HCUR.remove(u); throw new IllegalStateException("could not queue the harvest move: " + t); }
  return true;
}\'\'\'), phv))
# PickDropSys: the giveItem remainder of a full inventory, thrown right after the pickup (same item, at most that amount, 100 ms window)
# -> the Void takes what it can: all = the throw is cancelled, part = the thrown stack shrinks. Returns items taken (0 = untouched).
phv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long onDrop(@ST@ st, @REF@ pref, @PR@ pr, @DIE@ e) {
  if (st == null || pr == null || e == null || e.isCancelled()) return 0L;
  java.util.UUID u = pr.getUuid();
  Object[] c = null;
  if (u != null) c = (Object[]) HCUR.get(u);
  if (c == null) return 0L;
  if (System.nanoTime() - ((Long) c[2]).longValue() > WINDOW_NS) { HCUR.remove(u); return 0L; }
  @IS@ s = e.getItemStack();
  if (s == null || s.isEmpty() || s.getItemId() == null || !s.getItemId().equals(c[0])) return 0L;
  long q = (long) s.getQuantity();
  if (q <= 0L || q > ((Long) c[1]).longValue()) return 0L;
  // fix round: only a real giveItem remainder - the pickup container cannot take even 1 more (a Q-drop has just made room)
  if (c.length < 4 || !(c[3] instanceof @IC@) || ((@IC@) c[3]).canAddItemStack(s.withQuantity(1))) return 0L;
  HCUR.remove(u);
  if (!@PKG@.SackCfg.PICK_ON || !@PKG@.SackCfg.PICK_BLOCKS) return 0L;
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) { @PKG@.PickBook.n(13, 1L); return 0L; }
  if (@PKG@.PickGive.denied(u, @PKG@.PickBook.world(st.getExternalData()))) { @PKG@.PickBook.n(7, 1L); return 0L; }
  long room = @PKG@.PickGive.voidRoom(u, k, s);
  long m = room < q ? room : q;
  if (m <= 0L) return 0L;
  @PKG@.SackPool.add(k, s.getItemId(), m);
  try {
    if (@PKG@.PickGive.FAULT == 6) throw new IllegalStateException("harness fault 6 (before the throw update)");
    if (m >= q) e.setCancelled(true);
    else e.setItemStack(s.withQuantity((int) (q - m)));
  } catch (Throwable t) {
    @PKG@.SackPool.add(k, s.getItemId(), -m);
    @PKG@.PickBook.n(8, 1L);
    @PKG@.SackPool.warn("auto-pickup (harvest overflow) failed and was rolled back (it is thrown as vanilla): " + t);
    return 0L;
  }
  @PKG@.VoidStore.noteIntake(k, @PKG@.SackDefs.catIndex(@PKG@.SackDefs.catOf(s.getItemId())), m);
  try { @PKG@.SackPool.saveSoon(k); } catch (Throwable ts) { @PKG@.SackPool.DIRTY.put(k, Boolean.TRUE); }
  @PKG@.PickBook.n(15, m);
  @PKG@.PickGive.tell(u, pr, s.getItemId(), (int) q, new long[] { m, 0L, q - m });
  return m;
}\'\'\'), phv))
# PickHarvTask (World.execute, after the interaction and every listener): every NOT-cancelled pickup of this player -> the Void first.
# Returns items moved.
phv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long flush(@ST@ st, java.util.UUID u) {
  if (u == null || st == null) return 0L;
  Object o = HPEND.remove(u);
  HPT.remove(u);
  HCUR.remove(u);
  if (!(o instanceof java.util.ArrayList) || st == null) return 0L;
  if (!@PKG@.SackCfg.PICK_ON || !@PKG@.SackCfg.PICK_BLOCKS) return 0L;
  java.util.ArrayList l = (java.util.ArrayList) o;
  @REF@ pref = @PKG@.PickBook.here(u, st);
  if (pref == null) { @PKG@.PickBook.n(11, 1L); return 0L; }
  String k = @PKG@.SackPool.settledKey(u);
  if (k == null) { @PKG@.PickBook.n(13, 1L); return 0L; }
  // one entry per item id: Object[] { sample stack, Long amount, Long count before (the first pickup's), container }
  java.util.LinkedHashMap by = new java.util.LinkedHashMap();
  for (int i = 0; i < l.size(); i++) {
    Object[] rec = (Object[]) l.get(i);
    if (!(rec[0] instanceof @IPE@) || rec[3] == null) continue;
    @IPE@ e = (@IPE@) rec[0];
    if (e.isCancelled()) continue;
    @IS@ s = e.getItemStack();
    if (s == null || s.isEmpty() || s.getItemId() == null || !s.getItemId().equals(rec[1]) || s.getQuantity() <= 0) continue;
    Object[] a = (Object[]) by.get(rec[1]);
    if (a == null) by.put(rec[1], new Object[] { s, Long.valueOf((long) s.getQuantity()), rec[2], rec[3] });
    else a[1] = Long.valueOf(((Long) a[1]).longValue() + (long) s.getQuantity());
  }
  if (by.isEmpty()) return 0L;
  try { @PKG@.BagMirror.beforeTake(k); } catch (Throwable tb) { }
  @PR@ pr = null;
  try { pr = (@PR@) st.getComponent(pref, @PR@.getComponentType()); } catch (Throwable tp) { pr = null; }
  long total = 0L;
  java.util.Iterator it = by.values().iterator();
  while (it.hasNext()) {
    Object[] a = (Object[]) it.next();
    @IS@ s = (@IS@) a[0];
    @IC@ cont = (@IC@) a[3];
    long amount = ((Long) a[1]).longValue();
    long arrived = @PKG@.PickGive.countId(cont, s.getItemId()) - ((Long) a[2]).longValue();
    if (arrived > amount) arrived = amount;
    if (arrived <= 0L) continue;
    long moved = move(u, k, s, cont, arrived);
    if (moved <= 0L) continue;
    total += moved;
    @PKG@.VoidStore.noteIntake(k, @PKG@.SackDefs.catIndex(@PKG@.SackDefs.catOf(s.getItemId())), moved);
    @PKG@.PickBook.n(14, moved);
    // vanilla's own pickup popup + sound already ran for these (giveItem): only our card, no second sound
    if (u != null) @PKG@.PickGive.SND.put(u, Long.valueOf(System.currentTimeMillis()));
    @PKG@.PickGive.tell(u, pr, s.getItemId(), (int) arrived, new long[] { moved, arrived - moved, 0L });
  }
  if (total > 0L) { try { @PKG@.SackPool.saveSoon(k); } catch (Throwable ts) { @PKG@.SackPool.DIRTY.put(k, Boolean.TRUE); } }
  return total;
}\'\'\'), phv))
# PickHarvTask.run (fields + constructor above, before PickHarv.note queues it)
pht.addMethod(CtNewMethod.make(jt(r\'\'\'
public void run() {
  try { this.moved = @PKG@.PickHarv.flush(this.st, this.u); }
  catch (Throwable t) { @PKG@.PickHarv.HPEND.remove(this.u); @PKG@.PickHarv.HPT.remove(this.u); @PKG@.PickBook.warnOnce("pick7", "auto-pickup: harvest move failed (logged once; harvests stay in the inventory): " + t); }
}\'\'\'), pht))
# PickHarvSys: InteractivelyPickupItemEvent on a player (F-harvest, sickle swing, F-pickup of a loose block) - never cancels or changes it
phs.addConstructor(CtNewConstructor.make(jt("public PickHarvSys() { super(@IPE@.class); }"), phs))
phs.addMethod(CtNewMethod.make(jt("public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }"), phs))
phs.addMethod(CtNewMethod.make(jt(r\'\'\'
public void handle(int idx, @ACH@ chunk, @ST@ st, @CBF@ buf, @EVE@ ev) {
  try {
    if (!@PKG@.SackCfg.PICK_ON || !@PKG@.SackCfg.PICK_BLOCKS || !(ev instanceof @IPE@)) return;
    @IPE@ e = (@IPE@) ev;
    if (e.isCancelled()) return;
    @IS@ s = e.getItemStack();
    if (s == null || s.isEmpty() || s.getItemId() == null) return;
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
    if (pr == null || pr.getUuid() == null) return;
    @PKG@.PickHarv.note(st, chunk.getReferenceTo(idx), pr.getUuid(), e, s);
  } catch (Throwable t) { @PKG@.PickBook.warnOnce("pick8", "auto-pickup: harvest note failed (logged once; harvests go to the inventory): " + t); }
}\'\'\'), phs))
# PickDropSys: DropItemEvent$Drop on a player - only the overflow of a pickup that just happened (PickHarv.onDrop)
pds.addConstructor(CtNewConstructor.make(jt("public PickDropSys() { super(@DIE@.class); }"), pds))
pds.addMethod(CtNewMethod.make(jt("public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }"), pds))
pds.addMethod(CtNewMethod.make(jt(r\'\'\'
public void handle(int idx, @ACH@ chunk, @ST@ st, @CBF@ buf, @EVE@ ev) {
  try {
    if (!(ev instanceof @DIE@) || @PKG@.PickHarv.HCUR.isEmpty()) return;
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.PickHarv.onDrop(st, chunk.getReferenceTo(idx), pr, (@DIE@) ev);
  } catch (Throwable t) { @PKG@.PickBook.warnOnce("pick9", "auto-pickup: harvest overflow check failed (logged once; it is thrown as vanilla): " + t); }
}\'\'\'), pds))

'''
HARV = HARV.replace(chr(92) + "'" + chr(92) + "'" + chr(92) + "'", "'" * 3)
rep('''# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))''', HARV.lstrip("\n") + '''# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))''')

# ---------------------------------------------------------------------------------------------------------------- plugin setup / shutdown
rep('''      try {{ getEntityStoreRegistry().registerSystem(new {PKG}.PickShareSys()); }}
      catch (Throwable tp4) {{ {PKG}.SackPool.warn("auto-pickup: the killer's share could not be ordered after DropDeathItems - the top damager still gets the drop, a different killer gets no extra share this start: " + tp4); }}
    }}
  }}
''', '''      try {{ getEntityStoreRegistry().registerSystem(new {PKG}.PickShareSys()); }}
      catch (Throwable tp4) {{ {PKG}.SackPool.warn("auto-pickup: the killer's share could not be ordered after DropDeathItems - the top damager still gets the drop, a different killer gets no extra share this start: " + tp4); }}
    }}
  }}
  // 0.8.4: F-harvest -> the Void first (ONE registerSystem per class); the overflow catch only with the harvest note
  try {{ getEntityStoreRegistry().registerSystem(new {PKG}.PickHarvSys()); {PKG}.PickBook.HARV_OK = true; }}
  catch (Throwable tp5) {{ {PKG}.SackPool.warn("auto-pickup: the harvest hook could not be registered - F-harvests go to the inventory this start: " + tp5); }}
  if ({PKG}.PickBook.HARV_OK) {{
    try {{ getEntityStoreRegistry().registerSystem(new {PKG}.PickDropSys()); {PKG}.PickBook.DROP_OK = true; }}
    catch (Throwable tp6) {{ {PKG}.SackPool.warn("auto-pickup: the harvest overflow catch could not be registered - a full inventory throws the rest as vanilla: " + tp6); }}
  }}
''')
rep('''  try {{ {PKG}.PickBook.CL.clear(); {PKG}.PickBook.RINGS.clear(); {PKG}.PickBook.SHARE.clear(); {PKG}.PickBook.DONE.clear(); }} catch (Throwable t) {{ }}
''', '''  try {{ {PKG}.PickBook.CL.clear(); {PKG}.PickBook.RINGS.clear(); {PKG}.PickBook.SHARE.clear(); {PKG}.PickBook.DONE.clear(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.PickHarv.HPEND.clear(); {PKG}.PickHarv.HPT.clear(); {PKG}.PickHarv.HCUR.clear(); }} catch (Throwable t) {{ }}   // 0.8.4
''')
rep('''          pcl, prg, pbk, pgv, pdl, pis, pbs, pdm, pss):   # 0.8.3: auto-pickup
''', '''          pcl, prg, pbk, pgv, pdl, pis, pbs, pdm, pss,   # 0.8.3: auto-pickup
          phv, pht, phs, pds):   # 0.8.4: harvest -> Void first
''')
gone('''          pcl, prg, pbk, pgv, pdl, pis, pbs, pdm, pss):   # 0.8.3: auto-pickup''')

# ---------------------------------------------------------------------------------------------------------------- texts (fix round)
rep('''     "Mined, chopped and harvested blocks, felled trees too. Off: they drop on the ground.",''',
    '''     "Mined, chopped, felled and harvested. Off: blocks drop on the ground, harvests go to the inventory.",''')
gone('''     "Mined, chopped and harvested blocks, felled trees too. Off: they drop on the ground.",''')

# ---------------------------------------------------------------------------------------------------------------- guards
assert s.count("registerSystem(") == SYS0 + 2, "exactly two new registerSystem calls"
assert s.index("public static java.util.UUID petOwner(") < s.index("PickBook.petOwner(st, r)")
assert s.index("public static long move(") < s.index("long moved = move(u, k, s, cont, arrived)")
assert s.index("public static boolean note(") < s.index("PickHarv.note(st, chunk")
assert s.index("public static long onDrop(") < s.index("PickHarv.onDrop(st, chunk")
assert s.index("public static long flush(") < s.index("PickHarv.flush(this.st")
assert s.index("public static long[] split(java.util.UUID u") < s.index("public static long move(")   # PickGive helpers come first
_gone = sorted(ln for ln in set(OLD.split(LF)) - set(s.split(LF)))
_bad = [ln for ln in _gone if ln not in GONE_OK and '"killer only (no mob:fn:credit yet)") + ")";' not in ln
        and '" contested, " + N.get(8) + " rolled back";' not in ln]
assert not _bad, "0.8.3 lines lost by accident: %s" % _bad[:5]
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.8.3 had %d)" % (s.count(LF), OLD.count(LF)))
