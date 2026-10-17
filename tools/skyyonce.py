"""skyyonce - LIFELONG ONE-PER-PROFILE ITEMS (round life01, 2026-10-16). A code generator every owner mod's build script imports, so each
jar carries its own copy (the tools/skyycfg.py pattern). Used by SkyyAccessories 0.5.20 (the Accessory Bag), SkyySacks 0.8.12 (the Pocket
Dimension item) and SkyyMenu 0.3.32 (the SkyWynn Menu item).

Skyy 2026-10-16 (docs/answered/gear.md, SECOND ACCESSORY BAG ON ISLAND RESET + LIFELONG BAG / POCKET / MENU ITEM): screenshot after
/island reset - the starter chest held an Accessory Bag while one was already in the inventory - "when island reset, it came with a 2nd
accessory bag.   (yk how you cant loose the tools, and can bring them back with a command. lets do the same to the accessory bag, the
pocket dimension, and the menu item.)"

The three items are OPENERS: they hold nothing of their own (the Accessory Bag's accessories live in the profile's bag file, the Void in
the profile's pool, the menu is a page), so every copy is the same and an extra copy can go without losing anything. Rules (each mod's
Server Setup switch ON = all of them; OFF = the item behaves as before):
  1. NEVER DROPPED: DropItemEvent$PlayerRequest (the Drop key / dragging it out of the inventory or a container window) on the item is
     cancelled before the engine removes anything (InventoryPacketHandler fires it first - the SkyyGear 0.3.0 GearLLDropSys pattern).
     The client's view: for an own section the engine re-sends it (InventoryPacketHandler marks that InventoryComponent dirty after a
     cancelled request - VERIFIED bytecode 2026-10-16); for a container window this marks the window changed.
  2. NEVER ON THE GROUND: DropItemEvent$Drop of the item from a player (death drops when keep-inventory is off, a full-inventory overflow)
     is cancelled and the item comes straight back into the inventory (storage first; full = a chat line naming the recall command).
  3. NEVER STORED: a copy that sits in an open world chest / container window (ContainerBlockWindow, ContainerWindow - trade offers, the
     Vault -, ItemStackContainerWindow) after the player's inventory changed is taken out at once: back into the inventory when the player
     has none, else removed as an extra. FIX ROUND (critic): a WORLD chest (ContainerBlockWindow) may be someone else's - its copies are
     touched only while the viewer's own inventory count just dropped below what their last sweep left (= they put theirs in), at most
     that many; a copy already there is never moved or removed. Personal windows (Vault, trade offer, pouch) always. Combined / delegate containers (they can wrap the player's own sections or another mod's mirror)
     and the player's own sections are never touched; a container of a full inventory keeps it (it comes back once there is room).
  4. ONE PER PROFILE: more than one copy in the inventory (hotbar, storage, backpack, utility, tools) -> one is kept (a copy that carries
     metadata first, else the first in that order), every other copy is removed. HISTORY FIRST: the line naming every removed stack (where,
     how many, its metadata) is written + fsynced to Skyy_<Mod>/lifelong/history.log BEFORE anything is removed (no line = nothing
     removed); each line ends with its UNDO. The first pass of each profile is the ONE-TIME CLEANUP: run-once marker
     Skyy_<Mod>/lifelong/once/<pkey>.done, its own chat line when it removed something.
  5. NEVER SOLD: a market:veto entry (the Auction House + Bazaar contract: owner -> Function(ItemStack) -> reason) refuses the item.
  6. NEVER IN A STARTER KIT: once:item:<id> = Function -> Boolean.TRUE while once_expr holds (default: the switch; SkyyAccessories:
     the switch AND its starter-bag switch): "this mod hands the item to every profile
     itself" - SkyyIslands 0.5.17 leaves such ids out of the starter chest (the 2nd Accessory Bag after /island reset).
  7. RECALL: recall(pr, sections) gives one when the inventory holds none (storage, hotbar, backpack - never dropped), whatever the switch.
  PREFIX MODE (round FP1, 2026-10-17, SkyyCooking's Potion Flask + Food Pouch): emit(..., item_prefix="Skyy_Flask_") - every id that
     starts with the prefix counts as THE item (its loaded variants Skyy_Flask_V_<id> + the Empty id); item= is the id a give / recall
     hands out (the Empty id - the owner mod's sync fixes the variant). A kept copy of any variant is fine. Several prefix items in one
     mod: each gets its own folder Skyy_<Mod>/lifelong/<pfx>/ (history + run-once markers) and its own market:veto entry
     "<Mod>:lifelong:<pfx>"; once:item:<item> AND once:item:<prefix>* are published. Without item_prefix nothing changes (the jars
     built before keep working unchanged).
Profile safety (tools/PROFILES-CONTRACT.md): nothing runs while profile:busy:<uuid> is set (the task retries every 2 s, 30 times); every
rule works on the LIVE inventory only (the active profile's); files are keyed by the storage key (pkey).
When it runs: InventoryChangeEvent on a player (only when there is work: a copy in an open window, two or more copies, a rescue due, or the
profile's one-time pass not done) and PlayerReadyEvent (1.5 s later) -> ONE world-thread task per player (deduplicated).

API (build script, after its own config class exists - ON is a field there, bound by its Server Setup row):
    import skyyonce as ONCE
    LIFE = ONCE.emit(pool, PKG, "AccOnce", item="Skyy_Accessory_Bag", name="Accessory Bag", tag="[Accessories]", recall="/accbag",
                     mod="SkyyAccessories", on_expr=PKG + ".AccDefs.LIFELONG", info_col="#...", warn_col="#...")
    LIFE["classes"]  -> the CtClasses (write them to the class folder)
    LIFE["setup"]    -> Java for setup() (needs the plugin's getLogger() / getDataDirectory() / registries)
    LIFE["shutdown"] -> Java for shutdown()
    LIFE["names"]    -> the simple class names (harness / compare lists)
"""

PR = "com.hypixel.hytale.server.core.universe.PlayerRef"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
INV = "com.hypixel.hytale.server.core.inventory.Inventory"
IC = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
CIC = "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer"
DIC = "com.hypixel.hytale.server.core.inventory.container.DelegateItemContainer"
IS = "com.hypixel.hytale.server.core.inventory.ItemStack"
MSG = "com.hypixel.hytale.server.core.Message"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
EST = "com.hypixel.hytale.server.core.universe.world.storage.EntityStore"
REF = "com.hypixel.hytale.component.Ref"
ST = "com.hypixel.hytale.component.Store"
ACH = "com.hypixel.hytale.component.ArchetypeChunk"
CB = "com.hypixel.hytale.component.CommandBuffer"
EV = "com.hypixel.hytale.component.system.EcsEvent"
QRY = "com.hypixel.hytale.component.query.Query"
EES = "com.hypixel.hytale.component.system.EntityEventSystem"
ICE = "com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent"
DIRQ = "com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$PlayerRequest"
DIE = "com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$Drop"
PRE = "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent"
IUT = "com.hypixel.hytale.server.core.inventory.InventoryUtils"
WMGR = "com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager"
WIN = "com.hypixel.hytale.server.core.entity.entities.player.windows.Window"
ICWN = "com.hypixel.hytale.server.core.entity.entities.player.windows.ItemContainerWindow"
CBW = "com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerBlockWindow"
CWN = "com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow"
ISCW = "com.hypixel.hytale.server.core.entity.entities.player.windows.ItemStackContainerWindow"
BWIN = "com.hypixel.hytale.server.core.entity.entities.player.windows.BlockWindow"
LOG = "com.hypixel.hytale.logger.HytaleLogger"

TOK = {"PR": PR, "PLA": PLA, "INV": INV, "IC": IC, "CIC": CIC, "DIC": DIC, "IS": IS, "MSG": MSG, "WLD": WLD, "EST": EST, "REF": REF,
       "ST": ST, "ACH": ACH, "CB": CB, "EV": EV, "QRY": QRY, "ICE": ICE, "DIRQ": DIRQ, "DIE": DIE, "PRE": PRE, "IUT": IUT, "WMGR": WMGR,
       "WIN": WIN, "ICWN": ICWN, "CBW": CBW, "CWN": CWN, "ISCW": ISCW, "BWIN": BWIN, "LOG": LOG}

# the members every build probes (an engine update that drops one stops the build)
PROBES = [(PR, "getUuid"), (PR, "getUsername"), (PR, "sendMessage"), (PR, "getReference"), (PR, "getWorldUuid"), (PR, "isValid"),
          (PLA, "getInventory"), (PLA, "getWindowManager"), (PLA, "isWaitingForClientReady"), (INV, "getHotbar"), (INV, "getStorage"),
          (INV, "getBackpack"), (INV, "getUtility"), (INV, "getTools"), (IC, "getCapacity"), (IC, "getItemStack"),
          (IC, "removeItemStackFromSlot"), (IC, "addItemStack"), (IS, "getItemId"), (IS, "getQuantity"), (IS, "isEmpty"),
          (IS, "getMetadata"), (WMGR, "getWindows"), (WMGR, "markWindowChanged"), (WIN, "getId"), (ICWN, "getItemContainer"),
          (BWIN, "getX"), (BWIN, "getY"), (BWIN, "getZ"), (DIRQ, "getInventorySectionId"), (DIRQ, "getSlotId"), (DIRQ, "setCancelled"),
          (DIRQ, "isCancelled"), (DIE, "getItemStack"), (DIE, "setCancelled"), (DIE, "isCancelled"), (IUT, "getSectionById"),
          (PRE, "getPlayerRef"), (EST, "getWorld"), (ST, "getExternalData"), (ST, "isInThread"), (ST, "getComponent"),
          (REF, "getStore"), (REF, "isValid"), (ACH, "getReferenceTo"), (ACH, "getComponent"), (MSG, "raw"), (MSG, "color")]


def _sub(src, d):
    for k in sorted(d, key=len, reverse=True):
        src = src.replace("@%s@" % k, d[k])
    assert "@" not in src.replace("@Override", ""), "skyyonce: unreplaced token in: " + src[:300]
    return src


def emit(pool, pkg, pfx, item, name, tag, recall, mod, on_expr, info_col, warn_col, once_expr=None, item_prefix=None):
    from jpype import JClass
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    assert pfx.isalnum() and pfx[0].isupper(), pfx
    if item_prefix is not None:
        assert item_prefix and item.startswith(item_prefix) and all(c_.isalnum() or c_ == "_" for c_ in item_prefix), (item, item_prefix)
    for s_ in (item, name, tag, recall, mod, info_col, warn_col) + ((item_prefix,) if item_prefix else ()):
        assert all(32 <= ord(c_) < 127 for c_ in s_) and '"' not in s_ and "\\" not in s_, s_
    for c_, m_ in PROBES:
        cc = pool.get(c_)
        names = set(str(x.getName()) for x in cc.getMethods())
        if m_ not in names:
            raise SystemExit("skyyonce API probe failed: %s.%s not found" % (c_, m_))
    assert pool.get(WLD).subtypeOf(pool.get("java.util.concurrent.Executor")), "World is no Executor any more"
    for c_ in (CBW, CWN, ISCW):
        assert pool.get(c_).subtypeOf(pool.get(ICWN)), c_ + " is no ItemContainerWindow any more"
    gsb = [m_ for m_ in pool.get(IUT).getDeclaredMethods() if str(m_.getName()) == "getSectionById"]
    assert len(gsb) == 1 and str(gsb[0].getSignature()) == (
        "(Lcom/hypixel/hytale/component/Ref;ILcom/hypixel/hytale/component/ComponentAccessor;)"
        "Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;"), "InventoryUtils.getSectionById changed"
    names = [pfx, pfx + "Task", pfx + "DropSys", pfx + "ThrowSys", pfx + "InvSys", pfx + "Ready", pfx + "Fn"]
    for n_ in names:
        assert pool.getOrNull(pkg + "." + n_) is None, "skyyonce: class %s.%s exists already" % (pkg, n_)
    T = dict(TOK)
    T.update({"PKG": pkg, "P": pkg + "." + pfx, "S": pfx, "ID": item, "NAME": name, "TAG": tag, "RECALL": recall, "MOD": mod, "ON": on_expr,
              "ICOL": info_col, "WCOL": warn_col,
              "ONCE": once_expr or (pkg + "." + pfx + ".on()"),
              "VETO": mod + ":lifelong" + ((":" + pfx) if item_prefix else ""),
              "LDIR": "resolve(\"lifelong\")" + ((".resolve(\"%s\")" % pfx) if item_prefix else ""),
              "IPRE": item_prefix or "",
              "PKEYPUT": ('\n  b.put("once:item:%s*", new %s.%sFn(0));' % (item_prefix, pkg, pfx)) if item_prefix else "",
              "PKEYRM": ('\n    b.remove("once:item:%s*");' % item_prefix) if item_prefix else ""})
    core = pool.makeClass(pkg + "." + pfx)
    task = pool.makeClass(pkg + "." + pfx + "Task")
    drop = pool.makeClass(pkg + "." + pfx + "DropSys", pool.get(EES))
    thr = pool.makeClass(pkg + "." + pfx + "ThrowSys", pool.get(EES))
    invs = pool.makeClass(pkg + "." + pfx + "InvSys", pool.get(EES))
    rdy = pool.makeClass(pkg + "." + pfx + "Ready")
    fn = pool.makeClass(pkg + "." + pfx + "Fn")

    def F(c, src):
        c.addField(CtField.make(_sub(src, T), c))

    def M(c, src):
        c.addMethod(CtNewMethod.make(_sub(src, T), c))

    def C(c, src):
        c.addConstructor(CtNewConstructor.make(_sub(src, T), c))

    # ------------------------------------------------------------------------------------------------ the task (fields + ctor first)
    task.addInterface(pool.get("java.lang.Runnable"))
    F(task, "public @PR@ pr;")
    F(task, "public @WLD@ world;")
    F(task, "public java.util.UUID wu;")
    F(task, "public int tries;")
    C(task, "public @S@Task(@PR@ pr, @WLD@ w, java.util.UUID wu, int tries) { this.pr = pr; this.world = w; this.wu = wu; this.tries = tries; }")
    fn.addInterface(pool.get("java.util.function.Function"))
    F(fn, "public int mode;")
    C(fn, "public @S@Fn(int m) { this.mode = m; }")

    # ------------------------------------------------------------------------------------------------ the core
    F(core, 'public static final String ID = "@ID@";')
    F(core, 'public static final String NAME = "@NAME@";')
    F(core, 'public static final String TAG = "@TAG@";')
    F(core, 'public static final String RECALL = "@RECALL@";')
    F(core, 'public static final String MOD = "@MOD@";')
    F(core, "public static volatile java.nio.file.Path DIR;")
    F(core, "public static volatile @LOG@ LOG;")
    F(core, "public static final java.util.concurrent.ConcurrentHashMap PEND = new java.util.concurrent.ConcurrentHashMap();")     # UUID -> TRUE: a task is queued
    F(core, "public static final java.util.concurrent.ConcurrentHashMap RESCUE = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> Long: a throw was stopped
    F(core, "public static final java.util.concurrent.ConcurrentHashMap DONE = new java.util.concurrent.ConcurrentHashMap();")     # pkey -> TRUE: one-time pass done
    F(core, "public static final java.util.concurrent.ConcurrentHashMap TOLD = new java.util.concurrent.ConcurrentHashMap();")     # uuid:kind -> Long (chat limit)
    # fix round (critic 2): UUID -> Integer, the inventory count the last sweep left (a drop below it while a world chest is open = the
    # player just put THEIR copy in that chest); fix round (critic 3): UUID -> Object[] { epoch, pkey } (the pkey without a bridge call)
    F(core, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")
    F(core, "public static final java.util.concurrent.ConcurrentHashMap PKC = new java.util.concurrent.ConcurrentHashMap();")
    F(core, "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();")   # warn-once keys
    # 0 drops refused, 1 throws stopped, 2 sent home from a window, 3 extra copies removed, 4 rescued, 5 recalled, 6 one-time passes,
    # 7 history write failures (nothing removed), 8 tasks run, 9 left in a window (inventory full)
    F(core, "public static final java.util.concurrent.atomic.AtomicLongArray N = new java.util.concurrent.atomic.AtomicLongArray(10);")
    M(core, "public static boolean on() { return @ON@; }")
    M(core, r"""
public static java.util.Map mkBridge() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o instanceof java.util.Map) return (java.util.Map) o;
  java.util.concurrent.ConcurrentHashMap m = new java.util.concurrent.ConcurrentHashMap();
  System.getProperties().put("skyy.bridge", m);
  return m;
}""")
    M(core, r"""
public static java.util.Map bridge() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o instanceof java.util.Map) return (java.util.Map) o;
  java.util.Map r = null;
  synchronized (System.class) { r = mkBridge(); }
  return r;
}""")
    M(core, r"""
public static String pkey(java.util.UUID u) {
  if (u == null) return "";
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""")
    M(core, r"""
public static String pkeyFast(java.util.UUID u) {
  if (u == null) return "";
  Object ep = null;
  try { ep = bridge().get("profile:epoch:" + u.toString()); } catch (Throwable t) { ep = null; }
  Object[] c = (Object[]) PKC.get(u);
  if (c != null && (c[0] == null ? ep == null : c[0].equals(ep))) return (String) c[1];
  String k = pkey(u);
  if (c != null) LAST.remove(u);          // another profile: the last count was the old profile's
  PKC.put(u, new Object[] { ep, k });
  return k;
}""")
    M(core, r"""
public static boolean busy(java.util.UUID u) {
  if (u == null) return false;
  try { return Boolean.TRUE.equals(bridge().get("profile:busy:" + u.toString())); } catch (Throwable t) { return false; }
}""")
    M(core, r"""
public static void info(String s) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[@MOD@] lifelong @NAME@: " + s); } catch (Throwable t) { }
}""")
    M(core, r"""
public static void warn(String s) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[@MOD@] lifelong @NAME@: " + s); } catch (Throwable t) { }
}""")
    M(core, r"""
public static void warnOnce(String k, String s) {
  if (WARNED.putIfAbsent(k, Boolean.TRUE) == null) warn(s + " (logged once)");
}""")
    # chat, at most once per 5 s per player and kind
    M(core, r"""
public static boolean say(@PR@ pr, String kind, String text, String col) {
  if (pr == null) return false;
  try {
    String k = pr.getUuid() + ":" + kind;
    long now = System.currentTimeMillis();
    Long last = (Long) TOLD.get(k);
    if (last != null && now - last.longValue() < 5000L) return false;
    TOLD.put(k, Long.valueOf(now));
    pr.sendMessage(@MSG@.raw(text).color(col));
    return true;
  } catch (Throwable t) { return false; }
}""")
    if item_prefix:
        F(core, 'public static final String PREFIX = "@IPRE@";')
        M(core, "public static boolean is(@IS@ s) { if (s == null || s.isEmpty()) return false; String i = s.getItemId(); return i != null && i.startsWith(PREFIX); }")
    else:
        M(core, "public static boolean is(@IS@ s) { return s != null && !s.isEmpty() && ID.equals(s.getItemId()); }")
    M(core, r"""
public static int countIn(@IC@ c) {
  if (c == null) return 0;
  int n = 0;
  try {
    short cap = c.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = c.getItemStack(s);
      if (is(it)) n = n + it.getQuantity();
    }
  } catch (Throwable t) { }
  return n;
}""")
    M(core, r"""
public static int count(@IC@[] cs) {
  int n = 0;
  if (cs == null) return 0;
  for (int i = 0; i < cs.length; i++) n = n + countIn(cs[i]);
  return n;
}""")
    # the player's own sections in KEEP order: hotbar, storage, backpack, utility, tools
    M(core, r"""
public static @IC@[] secs(@INV@ inv) {
  if (inv == null) return new @IC@[0];
  return new @IC@[] { inv.getHotbar(), inv.getStorage(), inv.getBackpack(), inv.getUtility(), inv.getTools() };
}""")
    M(core, r"""
public static String secName(int i) {
  String[] n = new String[] { "Hotbar", "Storage", "Backpack", "Utility", "Tools" };
  return i >= 0 && i < n.length ? n[i] : "section " + i;
}""")
    M(core, r"""
public static boolean own(@IC@[] cs, @IC@ c) {
  if (cs == null || c == null) return false;
  for (int i = 0; i < cs.length; i++) if (cs[i] == c) return true;
  return false;
}""")
    M(core, "public static boolean foreign(Object w) { return w instanceof @CBW@ || w instanceof @CWN@ || w instanceof @ISCW@; }")
    M(core, "public static boolean plain(@IC@ c) { return c != null && !(c instanceof @CIC@) && !(c instanceof @DIC@); }")
    # a world / other container of an open window that this rule may take the item out of, or null
    M(core, r"""
public static @IC@ winCont(Object w, @IC@[] cs) {
  if (!foreign(w)) return null;
  @IC@ c = null;
  try { c = ((@ICWN@) w).getItemContainer(); } catch (Throwable t) { c = null; }
  if (!plain(c) || own(cs, c)) return null;
  return c;
}""")
    M(core, r"""
public static int dropped(java.util.UUID u, @IC@[] cs) {
  Integer l = u == null ? null : (Integer) LAST.get(u);
  if (l == null) return 0;
  int d = l.intValue() - count(cs);
  return d > 0 ? d : 0;
}""")
    # fix round (critic 2): a WORLD chest (ContainerBlockWindow) may belong to someone else - its copies are touched only while the
    # viewer's own inventory just dropped below what the last sweep left (= they put theirs in); personal windows (Vault, trade offer,
    # a pouch) always
    M(core, r"""
public static boolean windowsHold(java.util.List ws, @IC@[] cs, java.util.UUID u) {
  if (ws == null) return false;
  boolean dr = dropped(u, cs) > 0;
  for (int i = 0; i < ws.size(); i++) {
    Object o = ws.get(i);
    @IC@ c = winCont(o, cs);
    if (c == null || countIn(c) <= 0) continue;
    if (!(o instanceof @CBW@) || dr) return true;
  }
  return false;
}""")
    M(core, r"""
public static String where(Object w) {
  String s = w == null ? "?" : w.getClass().getSimpleName();
  try { if (w instanceof @BWIN@) s = s + " at " + ((@BWIN@) w).getX() + " " + ((@BWIN@) w).getY() + " " + ((@BWIN@) w).getZ(); } catch (Throwable t) { }
  return s;
}""")
    M(core, r"""
public static int qtyAt(@IC@ c, short sl) {
  try {
    @IS@ s = c.getItemStack(sl);
    return is(s) ? s.getQuantity() : 0;
  } catch (Throwable t) { return 0; }
}""")
    # take n of the item out of one slot; true only when exactly n left it (read back)
    M(core, r"""
public static boolean removeN(@IC@ c, short sl, int n) {
  if (c == null || n <= 0) return n == 0;
  int b = qtyAt(c, sl);
  if (b < n) return false;
  try { c.removeItemStackFromSlot(sl, n); } catch (Throwable t) { return false; }
  return b - qtyAt(c, sl) == n;
}""")
    # ONE into the inventory: storage, then hotbar, then backpack (never dropped); returns how many arrived (1), 0 = full, -1 = error
    M(core, r"""
public static int give(@IC@[] cs) {
  if (cs == null || cs.length < 3) return -1;
  int before = count(cs);
  int[] order = new int[] { 1, 0, 2 };
  boolean any = false;
  for (int k = 0; k < order.length; k++) {
    @IC@ c = cs[order[k]];
    if (c == null) continue;
    any = true;
    try { c.addItemStack(new @IS@(ID, 1)); } catch (Throwable t) { warnOnce("give", "adding one to the inventory failed: " + t); }
    int now = count(cs);
    if (now > before) return now - before;
  }
  return any ? 0 : -1;
}""")
    # undo a give: one copy out again (the last one found, reverse KEEP order)
    M(core, r"""
public static boolean takeOne(@IC@[] cs) {
  if (cs == null) return false;
  for (int i = cs.length - 1; i >= 0; i--) {
    @IC@ c = cs[i];
    if (c == null) continue;
    short cap = c.getCapacity();
    for (int s = cap - 1; s >= 0; s--) if (qtyAt(c, (short) s) > 0) return removeN(c, (short) s, 1);
  }
  return false;
}""")
    M(core, r"""
public static String meta(@IS@ s) {
  try {
    org.bson.BsonDocument d = s == null ? null : s.getMetadata();
    if (d == null || d.isEmpty()) return "none";
    return d.toJson();
  } catch (Throwable t) { return "?"; }
}""")
    M(core, r"""
public static boolean hasMeta(@IS@ s) {
  try { org.bson.BsonDocument d = s == null ? null : s.getMetadata(); return d != null && !d.isEmpty(); } catch (Throwable t) { return false; }
}""")
    M(core, r"""
public static String who(@PR@ pr, String pk) {
  String n = "?";
  try { n = pr.getUsername() + " " + pr.getUuid(); } catch (Throwable t) { }
  return java.time.Instant.now().toString() + " " + n + " profile " + pk;
}""")
    M(core, r"""
public static String undo() {
  return "UNDO: an extra copy holds nothing of its own (the contents live with the profile) - " + RECALL + " gives one back whenever none is left; an admin may also give @ID@ again";
}""")
    M(core, r"""
public static boolean write0(String line) throws Exception {
  java.nio.file.Path d = DIR;
  if (d == null) return false;
  java.nio.file.Files.createDirectories(d, new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path f = d.resolve("history.log");
  byte[] b = (line + "\n").getBytes(java.nio.charset.StandardCharsets.UTF_8);
  java.nio.channels.FileChannel ch = java.nio.channels.FileChannel.open(f, new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.WRITE, java.nio.file.StandardOpenOption.APPEND });
  try {
    java.nio.ByteBuffer bb = java.nio.ByteBuffer.wrap(b);
    while (bb.hasRemaining()) ch.write(bb);
    ch.force(true);
  } finally { ch.close(); }
  return true;
}""")
    # HISTORY FIRST: true = the line is on disk (fsynced); false = nothing may be removed
    M(core, r"""
public static synchronized String writeSync(String line) {
  try { return write0(line) ? null : "no folder"; } catch (Throwable t) { return String.valueOf(t); }
}""")
    M(core, r"""
public static boolean history(String line) {
  String e = writeSync(line);
  if (e == null) return true;
  N.incrementAndGet(7);
  warnOnce("hist", "history.log could not be written (" + e + ") - extra copies are kept until it can");
  return false;
}""")
    M(core, r"""
public static java.nio.file.Path marker(String pk) {
  java.nio.file.Path d = DIR;
  return d == null ? null : d.resolve("once").resolve(pk + ".done");
}""")
    # the one-time pass: true = this profile has not had it yet (no marker in memory or on disk)
    M(core, r"""
public static boolean firstPass(String pk) {
  if (pk == null || pk.length() == 0 || DONE.containsKey(pk)) return false;
  java.nio.file.Path m = marker(pk);
  try { if (m != null && java.nio.file.Files.exists(m, new java.nio.file.LinkOption[0])) { DONE.put(pk, Boolean.TRUE); return false; } } catch (Throwable t) { }
  return true;
}""")
    M(core, r"""
public static void markDone(String pk, String text) {
  DONE.put(pk, Boolean.TRUE);
  N.incrementAndGet(6);
  java.nio.file.Path m = marker(pk);
  if (m == null) return;
  try {
    java.nio.file.Files.createDirectories(m.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = m.resolveSibling(pk + ".tmp");
    java.nio.file.Files.write(tmp, (text + "\n").getBytes(java.nio.charset.StandardCharsets.UTF_8), new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, m, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
  } catch (Throwable t) { warnOnce("marker", "the run-once marker " + m + " could not be written (" + t + ") - the one-time pass runs again after a restart (harmless)"); }
}""")
    # FOUR: more than one copy in the inventory -> keep one, remove the rest (history line first); returns the copies removed
    M(core, r"""
public static int trim(@PR@ pr, @IC@[] cs, String pk) {
  int total = count(cs);
  if (total <= 1) return 0;
  int ks = -1;
  int kl = -1;
  for (int i = 0; i < cs.length && ks < 0; i++) {
    if (cs[i] == null) continue;
    short cap = cs[i].getCapacity();
    for (short s = 0; s < cap && ks < 0; s++) { @IS@ x = cs[i].getItemStack(s); if (is(x) && hasMeta(x)) { ks = i; kl = s; } }
  }
  for (int i = 0; i < cs.length && ks < 0; i++) {
    if (cs[i] == null) continue;
    short cap = cs[i].getCapacity();
    for (short s = 0; s < cap && ks < 0; s++) if (is(cs[i].getItemStack(s))) { ks = i; kl = s; }
  }
  if (ks < 0) return 0;
  StringBuilder w = new StringBuilder();
  for (int i = 0; i < cs.length; i++) {
    if (cs[i] == null) continue;
    short cap = cs[i].getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ x = cs[i].getItemStack(s);
      if (!is(x)) continue;
      int n = (i == ks && s == kl) ? x.getQuantity() - 1 : x.getQuantity();
      if (n <= 0) continue;
      if (w.length() > 0) w.append("; ");
      w.append(n).append(" from ").append(secName(i)).append(" slot ").append(s + 1).append(" meta ").append(meta(x));
    }
  }
  if (!history(who(pr, pk) + " REMOVE " + (total - 1) + " extra @ID@ from the inventory: " + w + " | kept " + secName(ks) + " slot " + (kl + 1) + " | " + undo())) return 0;
  int gone = 0;
  for (int i = 0; i < cs.length; i++) {
    if (cs[i] == null) continue;
    short cap = cs[i].getCapacity();
    for (short s = 0; s < cap; s++) {
      int q = qtyAt(cs[i], s);
      if (q <= 0) continue;
      int n = (i == ks && s == kl) ? q - 1 : q;
      if (n > 0 && removeN(cs[i], s, n)) gone = gone + n;
    }
  }
  int after = count(cs);
  if (after != 1) warn("after removing extra copies " + after + " are left in " + pk + "'s inventory (expected 1)");
  N.addAndGet(3, (long) gone);
  info("removed " + gone + " extra copy(ies) from profile " + pk + " (history.log has them)");
  return gone;
}""")
    # THREE: copies in open world / other containers -> home (none in the inventory) or removed as extras. r = { home, extra, held }
    M(core, r"""
public static void windows(@PR@ pr, @IC@[] cs, java.util.List ws, @WMGR@ wm, String pk, int[] r) {
  if (ws == null) return;
  int budget = dropped(pr.getUuid(), cs);          // fix round (critic 2): copies this player just put into a world chest
  for (int i = 0; i < ws.size(); i++) {
    Object o = ws.get(i);
    @IC@ c = winCont(o, cs);
    if (c == null) continue;
    boolean block = o instanceof @CBW@;
    boolean changed = false;
    short cap = c.getCapacity();
    for (short sl = 0; sl < cap; sl++) {
      int q = qtyAt(c, sl);
      if (q <= 0) continue;
      if (block) {
        if (budget <= 0) continue;                 // a copy that was already there (maybe another player's) - never touched
        if (q > budget) q = budget;
        budget = budget - q;
      }
      @IS@ x = c.getItemStack(sl);
      String at = where(o) + " slot " + (sl + 1);
      if (count(cs) <= 0) {
        int g = give(cs);
        if (g <= 0) { r[2] = r[2] + q; N.incrementAndGet(9); if (block) budget = budget + q; continue; }
        if (q > 1 && !history(who(pr, pk) + " REMOVE " + (q - 1) + " extra @ID@ from " + at + " meta " + meta(x) + " (one went back to the inventory) | " + undo())) { takeOne(cs); if (block) budget = budget + q; continue; }
        if (!removeN(c, sl, q)) { takeOne(cs); if (block) budget = budget + q; warnOnce("winrm", "a copy in " + at + " could not be taken out - left there"); continue; }
        r[0] = r[0] + 1;
        r[1] = r[1] + (q - 1);
        N.incrementAndGet(2);
        if (q > 1) N.addAndGet(3, (long) (q - 1));
        info(pk + ": a copy left in " + at + " went back to the inventory");
        changed = true;
      } else {
        if (!history(who(pr, pk) + " REMOVE " + q + " extra @ID@ from " + at + " meta " + meta(x) + " (the inventory already holds one) | " + undo())) { if (block) budget = budget + q; continue; }
        if (!removeN(c, sl, q)) { warnOnce("winrm", "a copy in " + at + " could not be taken out - left there"); continue; }
        r[1] = r[1] + q;
        N.addAndGet(3, (long) q);
        info(pk + ": removed " + q + " extra copy(ies) from " + at);
        changed = true;
      }
    }
    if (changed && wm != null) { try { wm.markWindowChanged(((@WIN@) o).getId()); } catch (Throwable t) { } }
  }
}""")
    # THE SWEEP over plain objects (the harness runs it on real containers / windows). Returns a short summary.
    M(core, r"""
public static String sweepCore(@PR@ pr, @IC@[] cs, java.util.List ws, @WMGR@ wm, String pk) {
  if (!on()) return "off";
  if (pr == null || cs == null) return "none";
  java.util.UUID u = pr.getUuid();
  if (busy(u)) return "busy";
  boolean first = firstPass(pk);
  int[] r = new int[] { 0, 0, 0 };
  windows(pr, cs, ws, wm, pk, r);
  int ex = trim(pr, cs, pk);
  int resc = 0;
  if (RESCUE.remove(u) != null && count(cs) <= 0) {
    int g = give(cs);
    if (g > 0) { resc = 1; N.incrementAndGet(4); info(pk + ": a dropped copy was stopped - one is back in the inventory"); say(pr, "rescue", TAG + " Your " + NAME + " stays with you - it is back in your inventory.", "@ICOL@"); }
    else say(pr, "rescue", TAG + " Your " + NAME + " could not come back - your inventory is full. Make room and type " + RECALL + ".", "@WCOL@");
  }
  int extra = ex + r[1];
  if (r[0] > 0) say(pr, "home", TAG + " Your " + NAME + " stays with you - it can't be stored, so it went back to your inventory.", "@ICOL@");
  if (r[2] > 0) say(pr, "held", TAG + " Your " + NAME + " can't be stored in a container - make room in your inventory and it comes back.", "@WCOL@");
  if (first) {
    if (extra > 0) say(pr, "first", TAG + " You had " + extra + " extra " + NAME + (extra == 1 ? "" : "s") + " - only one is kept now. Extra copies hold nothing of their own, so nothing is lost.", "@ICOL@");
    markDone(pk, "lifelong @ID@ one-time cleanup " + java.time.Instant.now() + ": " + extra + " extra copy(ies) removed (history.log)");
  } else if (extra > 0) say(pr, "extra", TAG + " An extra " + NAME + " was removed - you keep one (type " + RECALL + " if it is ever missing).", "@ICOL@");
  if (r[2] <= 0) LAST.put(u, Integer.valueOf(count(cs)));          // fix round (critic 2): what this sweep left (a held copy keeps the drop open)
  return "home=" + r[0] + " extra=" + extra + " held=" + r[2] + " rescued=" + resc + (first ? " first" : "");
}""")
    # the world-thread glue: the live player's sections + open windows
    M(core, r"""
public static String sweep(@PR@ pr, @PLA@ p) {
  if (pr == null || p == null) return "none";
  java.util.List ws = null;
  @WMGR@ wm = null;
  try { wm = p.getWindowManager(); ws = wm == null ? null : wm.getWindows(); } catch (Throwable t) { ws = null; }
  return sweepCore(pr, secs(p.getInventory()), ws, wm, pkeyFast(pr.getUuid()));
}""")
    # is there work for a task? (the event path asks before it queues one)
    M(core, r"""
public static boolean needs(java.util.UUID u, @IC@[] cs, java.util.List ws) {
  if (u == null || !on() || PEND.containsKey(u)) return false;
  if (RESCUE.containsKey(u)) return true;
  if (count(cs) > 1) return true;
  if (windowsHold(ws, cs, u)) return true;
  if (!LAST.containsKey(u)) return true;          // never swept this session (sets the count the chest rule compares with)
  return !DONE.containsKey(pkeyFast(u));
}""")
    M(core, r"""
public static boolean schedule(@PR@ pr, @WLD@ w, long delay, int tries) {
  if (pr == null || w == null || !on()) return false;
  java.util.UUID u = null;
  try { u = pr.getUuid(); } catch (Throwable t) { return false; }
  if (u == null || PEND.putIfAbsent(u, Boolean.TRUE) != null) return false;
  try {
    @P@Task t = new @P@Task(pr, w, pr.getWorldUuid(), tries);
    if (delay <= 0L) w.execute(t);
    else java.util.concurrent.CompletableFuture.delayedExecutor(delay, java.util.concurrent.TimeUnit.MILLISECONDS, (java.util.concurrent.Executor) w).execute(t);
    return true;
  } catch (Throwable x) { PEND.remove(u); warnOnce("sched", "a world task could not be queued: " + x); return false; }
}""")
    M(core, r"""
public static @WLD@ worldOf(@ST@ st) {
  try { Object ext = st == null ? null : st.getExternalData(); return ext instanceof @EST@ ? ((@EST@) ext).getWorld() : null; } catch (Throwable t) { return null; }
}""")
    # ONE: the Drop key / drag out (the event + the container it names; the harness passes real ones)
    M(core, r"""
public static boolean onRequest(@DIRQ@ e, @IC@ c, @PR@ pr, @WMGR@ wm) {
  if (e == null || e.isCancelled() || !on() || c == null) return false;
  int sl = (int) e.getSlotId();
  if (sl < 0 || sl >= c.getCapacity()) return false;
  if (!is(c.getItemStack((short) sl))) return false;
  e.setCancelled(true);
  N.incrementAndGet(0);
  if (e.getInventorySectionId() >= 0 && wm != null) { try { wm.markWindowChanged(e.getInventorySectionId()); } catch (Throwable t) { } }
  say(pr, "drop", TAG + " Your " + NAME + " stays with you - it can't be dropped. (Lost it? Type " + RECALL + ".)", "@WCOL@");
  return true;
}""")
    # TWO: a thrown stack of the item (death drop, full-inventory overflow) - stopped; the next sweep puts one back
    M(core, r"""
public static boolean onThrow(@DIE@ e, @PR@ pr) {
  if (e == null || e.isCancelled() || !on()) return false;
  @IS@ s = e.getItemStack();
  if (!is(s)) return false;
  e.setCancelled(true);
  N.incrementAndGet(1);
  if (pr != null) {
    RESCUE.put(pr.getUuid(), Long.valueOf(System.currentTimeMillis()));
    info(pr.getUsername() + ": " + s.getQuantity() + " thrown copy(ies) stopped - the inventory gets one back if it has none");
  }
  return true;
}""")
    # SEVEN: the recall (a command): one into the inventory when it holds none - whatever the switch says
    M(core, r"""
public static String recall(@PR@ pr, @IC@[] cs) {
  if (pr == null || cs == null) return "-none";
  if (busy(pr.getUuid())) return "-busy";
  if (count(cs) > 0) return "=have";
  int g = give(cs);
  if (g > 0) { N.incrementAndGet(5); info(pr.getUsername() + " (" + pkey(pr.getUuid()) + ") got one back with " + RECALL); return "+given"; }
  return g < 0 ? "-error" : "-full";
}""")
    M(core, r"""
public static String recallText(String r) {
  if (r == null) return null;
  if (r.equals("+given")) return TAG + " Here is your " + NAME + " again. It stays with you - it can't be dropped, stored or sold.";
  if (r.equals("-full")) return TAG + " Your inventory is full, so your " + NAME + " could not come back. Make room and type " + RECALL + " again.";
  if (r.equals("-busy")) return TAG + " Your profile is still loading - type " + RECALL + " again in a moment.";
  if (r.equals("-error")) return TAG + " Your " + NAME + " could not be given - the server log has the details.";
  return null;
}""")
    M(core, r"""
public static String statusText() {
  return "lifelong @NAME@ " + (on() ? "on" : "OFF") + " (" + RECALL + "; drops refused " + N.get(0) + ", throws stopped " + N.get(1) + ", back from a container " + N.get(2) + ", extras removed " + N.get(3) + ", recalled " + N.get(5) + ")";
}""")
    M(core, r"""
public static void publish() {
  java.util.Map b = bridge();
  b.put("once:item:@ID@", new @P@Fn(0));@PKEYPUT@
  Object mv = b.get("market:veto");
  if (!(mv instanceof java.util.Map)) {
    b.putIfAbsent("market:veto", new java.util.concurrent.ConcurrentHashMap());
    mv = b.get("market:veto");
  }
  if (mv instanceof java.util.Map) ((java.util.Map) mv).put("@VETO@", new @P@Fn(1));
}""")
    M(core, r"""
public static void unpublish() {
  try {
    java.util.Map b = bridge();
    b.remove("once:item:@ID@");@PKEYRM@
    Object mv = b.get("market:veto");
    if (mv instanceof java.util.Map) ((java.util.Map) mv).remove("@VETO@");
  } catch (Throwable t) { }
  PEND.clear();
  RESCUE.clear();
  LAST.clear();
  PKC.clear();
  TOLD.clear();
}""")

    # ------------------------------------------------------------------------------------------------ task run (calls the core)
    M(task, r"""
public void run() {
  java.util.UUID u = null;
  try {
    u = this.pr.getUuid();
    @P@.PEND.remove(u);
    if (!@P@.on() || !this.pr.isValid()) return;
    java.util.UUID nw = this.pr.getWorldUuid();
    if (nw == null || !nw.equals(this.wu)) return;
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null || !st.isInThread()) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return;
    @P@.N.incrementAndGet(8);
    String res = p.isWaitingForClientReady() ? "busy" : @P@.sweep(this.pr, p);
    if ("busy".equals(res) && this.tries < 30) @P@.schedule(this.pr, this.world, 2000L, this.tries + 1);
  } catch (Throwable t) { @P@.warnOnce("task", "the world task failed: " + t); }
}""")

    # ------------------------------------------------------------------------------------------------ the systems (thin glue)
    def system(cls, ctor, ev_cls, body):
        C(cls, "public %s() { super(%s.class); }" % (ctor, ev_cls))
        M(cls, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
        M(cls, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
%s
  } catch (Throwable t) { @P@.warnOnce("%s", "%s failed: " + t); }
}""" % (body, ctor, ctor))

    system(drop, pfx + "DropSys", DIRQ, r"""
    if (!(ev instanceof @DIRQ@) || !@P@.on()) return;
    @DIRQ@ e = (@DIRQ@) ev;
    if (e.isCancelled()) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @IC@ c = @IUT@.getSectionById(r, e.getInventorySectionId(), st);
    if (c == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (@P@.onRequest(e, c, pr, p == null ? null : p.getWindowManager()) && e.getInventorySectionId() >= 0 && pr != null) @P@.schedule(pr, @P@.worldOf(st), 0L, 0);""")
    system(thr, pfx + "ThrowSys", DIE, r"""
    if (!(ev instanceof @DIE@) || !@P@.on()) return;
    @DIE@ e = (@DIE@) ev;
    if (e.isCancelled() || !@P@.is(e.getItemStack())) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (@P@.onThrow(e, pr) && pr != null) @P@.schedule(pr, @P@.worldOf(st), 0L, 0);""")
    system(invs, pfx + "InvSys", ICE, r"""
    if (!(ev instanceof @ICE@) || !@P@.on()) return;
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
    @PLA@ p = (@PLA@) chunk.getComponent(idx, @PLA@.getComponentType());
    if (pr == null || p == null) return;
    java.util.List ws = null;
    try { ws = p.getWindowManager().getWindows(); } catch (Throwable tw) { ws = null; }
    if (!@P@.needs(pr.getUuid(), @P@.secs(p.getInventory()), ws)) return;
    @P@.schedule(pr, @P@.worldOf(st), 0L, 0);""")

    # PlayerReadyEvent (every world switch): one look 1.5 s later (the one-time pass of a profile that never changed its inventory)
    rdy.addInterface(pool.get("java.util.function.Consumer"))
    C(rdy, "public @S@Ready() { }")
    M(rdy, r"""
public void accept(Object o) {
  try {
    if (!@P@.on() || !(o instanceof @PRE@)) return;
    @REF@ r = ((@PRE@) o).getPlayerRef();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @P@.schedule(pr, @P@.worldOf(st), 1500L, 0);
  } catch (Throwable t) { @P@.warnOnce("ready", "the ready hook failed: " + t); }
}""")

    # once:item:<id> (mode 0) and the market:veto entry (mode 1)
    M(fn, r"""
public Object apply(Object o) {
  try {
    if (this.mode == 0) return Boolean.valueOf(@ONCE@);          // fix round (critic 1): "this mod gives every profile one itself"
    if (this.mode == 1 && @P@.on() && o instanceof @IS@ && @P@.is((@IS@) o)) return "The " + @P@.NAME + " stays with you - it can't be sold.";
  } catch (Throwable t) { }
  return null;
}""")

    setup = _sub(r"""
  // life01: the lifelong @NAME@ (tools/skyyonce.py)
  @P@.LOG = getLogger();
  @P@.DIR = getDataDirectory().resolveSibling("Skyy_@MOD@").@LDIR@;
  getEntityStoreRegistry().registerSystem(new @P@DropSys());
  getEntityStoreRegistry().registerSystem(new @P@ThrowSys());
  getEntityStoreRegistry().registerSystem(new @P@InvSys());
  getEventRegistry().registerGlobal(@PRE@.class, new @P@Ready());
  @P@.publish();
""", T)
    shutdown = _sub("  try { @P@.unpublish(); } catch (Throwable tOnce) { }\n", T)
    return {"classes": [core, task, drop, thr, invs, rdy, fn], "setup": setup, "shutdown": shutdown, "names": names}
