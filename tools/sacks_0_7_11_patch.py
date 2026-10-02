"""Derive SkyySacks/build_skyysacks_0.7.11.py from the SET pin 0.7.10 (edit THIS file, then regenerate: python tools/sacks_0_7_11_patch.py).
0.7.11 = THREE CHANGES, all Skyy's answers of 2026-10-02 (OPEN-QUESTIONS.md "Q&A with Skyy 2026-10-02", rounds 2-4 + the R9 build order):
 A. WITHDRAW AMOUNT (R3, replaces the 10-minute exemption SackPool.exempt 600000 ms): "auto-collect LEAVES ALONE THE AMOUNT YOU TOOK (take
    out 512 stone -> up to 512 stone stay in your inventory; placing blocks lowers it; anything above it, e.g. newly mined, still goes in;
    no timer; Deposit all resets)". SackPool.KEPT = profile key -> (item id -> Long). Every withdraw (click, right click, Pick up all) and
    every stack refill adds what really left the pool; a withdraw first counts the item's hotbar + backpack stacks as kept (DECISION: the
    sweep never takes those, so a stack taken out while some sit in the hotbar - Hytale's default pickup spot - must not be swept back
    in their place). Each 2 s tick (world thread, settled key) first lowers kept to what the player
    carries (storage + hotbar + backpack: blocks placed, items used, dropped or stored away), then the automatic sweep (main inventory
    only, as before) leaves up to kept[item] of what the player carries alone and collects only what is above it. "Deposit all" clears
    kept for that tab's items (homeOf == the tab) and deposits everything as before. Memory only: a relog (the new KeptQuit
    PlayerDisconnectEvent listener) and a profile switch (SackPool.settledKey sees the key / epoch change) reset it.
 B. STACK AUTO-REFILL (R3 + R4): "stacks you are using AUTO-REFILL from the bag every few seconds (grab one stack of stone, build, it
    tops back up to full - never go back to the bag)", a per-player 3-way setting on the bag page: HOTBAR ONLY (default) / FULL
    INVENTORY / OFF, persisted per player in Skyy_SkyySacks/refill.properties (RefillPref, uuid=hotbar|full|off, written by the SackSaver
    thread only when a player changes it). Every 2 s, after the sweep: every existing stack (hotbar; FULL: hotbar + main inventory +
    backpack) of an item the player USED since the last tick (the item's carried count went down without our own moves: a block placed,
    food eaten, a craft) that is below its max stack size is topped up from that item's pool when the player carries a bag of its type
    (homeOf, like withdraw) and the pool has more. Never an empty slot, never a stack with metadata, never a non-stacking item; the slot
    is read before and after (ItemContainer.addItemStackToSlot, the engine's merge) and exactly what it gained leaves the pool and adds
    to kept, so the sweep never pulls it back. No ping-pong: an item whose bag is full while the main inventory still holds more of it
    than kept is not refilled (it would only free room the next sweep fills again), and while one of the player's bench windows is open
    with a bag mirror for the key (the mirror offers pool items to that bench) the refill waits and keeps the used items pending (taking
    them out could let the bench use them twice); a mirror left behind with no open bench is synced and dropped first (review fix 9). The
    page row says the refill pauses while a bench is open (review fix 1: vanilla benches do NOT use the bags yet - SkyySacks 0.7.12).
    DECISION (where the spec left room - see the build report): "each existing stack ... is topped up" is applied to the stacks the
    player is USING (Skyy's own words in R3). Hytale's default pickup location is the HOTBAR for every item kind (PlayerSettings
    defaults, VERIFIED bytecode), so a literal "every partial stack" refill would turn every picked-up bone, ore or log that lands in a
    free hotbar slot into a full stack pulled out of the bag.
 C. BAGS ADD UP (R3 / R4): "carrying 2-3 bags of the same type ADDS their space together" - SweepTask.caps sums every carried bag of a
    type (a stack of n bags counts n times; long math, capped at Integer.MAX_VALUE); the Mythic Omni Bag adds its CAP_OMNI to every
    type on top of the other bags. Every caps() caller keeps using it (sweep, withdraw, Deposit all, bench link, /craft, the tabs);
    lowering the space never deletes pooled items (the sweep only stops intake). The bag page shows the total and how many bags make it
    up ("Mining - 3 bags - up to 21,440 of each item" + "From 3 bags: 2 Normal + 1 Legendary - their space adds up").
UI: the new bag page row is built with the shared vanilla kit tools/skyyui.py (setting_row + three small tertiary buttons, the selected
one on Tertiary_Active - the kit's documented on_off fallback widened to three; a caption line); the page root grows 640 -> 690 px.
Also VERSION 0.7.11, the Server Setup help of the Unique bag row and the config template comment say bags add up. Unchanged: item
classification, recipes, assets, the Workbench tab, /craft, Furnace / Tannery, the bench link (class compare in the harness, section I).
REVIEW FIXES (the 0.7.11 review, 2026-10-02 - numbers = its findings): (1) the refill help lines, the "no bag" page hint and the ready log
no longer say that vanilla benches use your bags (false until 0.7.12, research/Bag-Craft-Link-Fix.md); the lines say the refill pauses
while a bench is open. (4) Only a KEY change (a profile switch) resets the kept counts - a new epoch with the same key (a profile
created, /profileadmin setclass of the active one: same profile, same inventory) keeps them. (8) Server Setup -> Bags and Crafting rows
bags.refill (master switch, default on = Skyy's 3-way choice works) and bags.refillDefault (the mode of players who never picked one,
default hotbar = Skyy's default); the page row shows the player's choice and says when the server turned the refill off. (9) The refill
waits only while a bench window (MaterialContainerWindow) is really open; a bag mirror left behind with no open bench is synced first
(what a bench took is booked) and dropped - exactly CraftLinkTask's no-bench branch - so a failed bench link can no longer pause the
refill until a restart. (10) A quitting player's unsaved pool is written at once (KeptQuit -> SackPool.saveSoon: the engine saves the
inventory at disconnect), and a shutdown latch (SackPool.CLOSED, set first in shutdown(), checked in settledKey = the one gate of every
item move) stops sweeps, refills and clicks after shutdown() began. (11) Stale "best bag" comments. (13) An EMPTY metadata document
counts as no metadata (the refill merges with a copy of it, so the engine's stackable check matches); any real metadata is still never
touched. KNOWN EDGES, as the spec reads (documented, unchanged): a withdraw from a FULL bag while spare items of that item sit in the main
inventory is a net no-op - the sweep fills the room the withdraw freed from the spare, which is above kept (review 5); placing and mining
the same item inside one 2 s window net out (review 6); a stash round trip (take out, store in a chest - kept drops to 0 - take back)
sweeps the stack back in (review 7). FOR SKYY (not changed): bags add up without a limit (54 Normal bags hold more than a Legendary -
review 2), and an idle partial stack tops up only once it is used (the DECISION above - review 3).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.10.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.11.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert s.count(old) >= 1, "anchor missing: " + old[:90]
    assert count != 1 or s.count(old) == 1, "anchor not unique: " + old[:90]
    s = s.replace(old, new, count)


assert 'VERSION = "0.7.10"' in s and "skyywbtab" in s and "RefillPref" not in s and "SackPool.KEPT" not in s, \
    "the source must be the generated 0.7.10 script"
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")

# ================= docstring + version =================
rep('"""SkyySacks 0.7.10 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.10.py           -> SkyySacks/SkyySacks-0.7.10.jar' + LF
    + '       python build_skyysacks_0.7.10.py --deploy  -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world' + LF,
    '"""SkyySacks 0.7.11 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.11.py           -> SkyySacks/SkyySacks-0.7.11.jar' + LF
    + '       python build_skyysacks_0.7.11.py --deploy  -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world' + LF)
rep('bags never vanish without it). Ingredients, outputs and KnowledgeRequired unchanged.' + LF + '"""' + LF,
    'bags never vanish without it). Ingredients, outputs and KnowledgeRequired unchanged.' + LF
    + '0.7.11 (derived from 0.7.10 by tools/sacks_0_7_11_patch.py - edit the patch, not this file; Skyy 2026-10-02, OPEN-QUESTIONS Q&A rounds' + LF
    + '2-4): (A) KEPT counts replace the 10-minute exemption - every withdraw / Pick up all / refill adds to SackPool.KEPT[pkey][item] (a' + LF
    + 'withdraw first counts that item\'s hotbar + backpack stacks as kept: the sweep never takes those), the' + LF
    + '2 s sweep (main inventory) leaves up to that many of what the player carries and collects only what is above it, kept drops to what' + LF
    + 'the player carries, Deposit all clears that tab\'s kept counts, a relog (KeptQuit) or profile switch (settledKey) resets them' + LF
    + '(memory only). (B) STACK AUTO-REFILL, a per-player 3-way setting on the bag page (Hotbar only = default / Full inventory / Off,' + LF
    + 'Skyy_SkyySacks/refill.properties): every 2 s the stacks of items the player used since the last tick (hotbar; Full: + main inventory +' + LF
    + 'backpack) top up from the pool when that bag is carried; never an empty slot or a stack with metadata; counted; adds to kept; skipped' + LF
    + 'while that bag is full and spare items sit in the main inventory, and while a bench window is open. (C) BAGS ADD UP - caps()' + LF
    + 'sums every carried bag of a type, the Mythic Omni Bag adds CAP_OMNI to every type; the page shows the total and the bags behind it.' + LF
    + 'Review fixes (2026-10-02): no text claims that vanilla benches use the bags (0.7.12 makes them); only a key change resets kept (a' + LF
    + 'same-key epoch keeps it); Server Setup rows bags.refill (master switch) + bags.refillDefault; the refill pauses only while a bench' + LF
    + 'window is really open (a left-over mirror is synced and dropped); a quitting player\'s pool is saved at once; shutdown latch' + LF
    + 'SackPool.CLOSED (settledKey); an empty metadata document counts as none. Known edges: tools/sacks_0_7_11_patch.py docstring.' + LF
    + '"""' + LF)
rep('VERSION = "0.7.10"', 'VERSION = "0.7.11"')
rep('import skyywbtab as WB  # 0.7.10: the Workbench tab "Accessories & Bags" (one source with SkyyAccessories 0.5.2, the owner)' + LF,
    'import skyywbtab as WB  # 0.7.10: the Workbench tab "Accessories & Bags" (one source with SkyyAccessories 0.5.2, the owner)' + LF
    + 'import skyyui as SUI     # 0.7.11: the shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md) for the new stack refill row' + LF)
rep('PRE = "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent"' + LF,
    'PRE = "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent"' + LF
    + 'PDE = "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent"   # 0.7.11: KeptQuit (relog resets the kept counts)' + LF)
rep('''       "PR": PR, "MSG": MSG, "CRR": CRR, "MQ": MQ, "CRP": CRP, "PCD": PCD, "ITM": ITM, "SIC": SIC, "HSV": HSV}''',
    '''       "PR": PR, "MSG": MSG, "CRR": CRR, "MQ": MQ, "CRP": CRP, "PCD": PCD, "ITM": ITM, "SIC": SIC, "HSV": HSV,
       "PDE": PDE, "WM": WM, "MCW": MCW}   # 0.7.11 (+ WM / MCW: SweepTask.benchFed, review fix 9)''')

# ================= API probes (0.7.11) =================
rep('''for c, m in ((CRR, "isKnowledgeRequired"), (PLA, "getPlayerConfigData"), (PCD, "getKnownRecipes"), (PCD, "setKnownRecipes"),
             (CRP, "sendKnownRecipes"), (IS, "withQuality"), (IS, "getQualityIndex"), (IS, "getItem"), (ITM, "getQualityIndex"),
             (IC, "setItemStackForSlot"), (MSG, "color")):
    B.probe(pool, c, m)
''', '''for c, m in ((CRR, "isKnowledgeRequired"), (PLA, "getPlayerConfigData"), (PCD, "getKnownRecipes"), (PCD, "setKnownRecipes"),
             (CRP, "sendKnownRecipes"), (IS, "withQuality"), (IS, "getQualityIndex"), (IS, "getItem"), (ITM, "getQualityIndex"),
             (IC, "setItemStackForSlot"), (MSG, "color")):
    B.probe(pool, c, m)
# 0.7.11 (VERIFIED bytecode 2026-10-02): the stack refill merges into an existing slot with ItemContainer.addItemStackToSlot(short,
# ItemStack) (InternalContainerUtilItemStack: an empty slot takes the stack, a stackable one gains min(maxStack - qty, qty), a
# non-stackable one - other metadata / durability / quality - refuses), skips a stack whose metadata document has entries (review fix 13:
# ItemStack(id, qty, doc) keeps the document as given and isStackableWith compares it with BsonDocument.equals, so an EMPTY document is
# merged with a copy of itself - VERIFIED bytecode) and Item.getMaxStack() <= 1; the relog reset listens to PlayerDisconnectEvent.getPlayerRef()
# through PluginBase.getEventRegistry().registerGlobal (SkyyClasses' ClassQuit); review fix 9 reads Player.getWindowManager().getWindows()
# (a list copy of the open windows) for an open MaterialContainerWindow (the bench windows CraftLinkTask feeds)
for c, m in ((IC, "addItemStackToSlot"), (IS, "getMetadata"), (IS, "isStackableWith"), (ITM, "getMaxStack"), (PDE, "getPlayerRef"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "getEventRegistry"), ("com.hypixel.hytale.event.EventRegistry", "registerGlobal"),
             (INV, "getHotbar"), (INV, "getBackpack"), (PLA, "getWindowManager"), (WM, "getWindows"), ("org.bson.BsonDocument", "isEmpty")):
    B.probe(pool, c, m)
''')

# ================= new classes =================
rep('''snot = pool.makeClass(PKG + ".SackNotice")
''', '''snot = pool.makeClass(PKG + ".SackNotice")
# 0.7.11: RefillPref = the per-player stack refill mode (refill.properties); KeptQuit = the PlayerDisconnectEvent listener (relog resets kept)
rfp = pool.makeClass(PKG + ".RefillPref")
kq = pool.makeClass(PKG + ".KeptQuit")
''')

# ================= A. SackPool: KEPT replaces EXEMPT =================
rep('''sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap EXEMPT = new java.util.concurrent.ConcurrentHashMap();", sp))
''', '''# 0.7.11 (Skyy R3 2026-10-02 - replaces the 10-minute exemption timer): KEPT = profile key -> (item id -> Long) = how many of an item the
# player took out (withdraw, Pick up all, stack refill) and may keep in the inventory: the 2 s sweep leaves up to that many alone.
# KEPTKEY = player uuid -> the key whose kept counts that player used last (the quit listener forgets them). The stack refill's "stacks you
# are using" memory: SEENQ = uuid -> (item id -> Long carried at the end of the last sweep tick), PENDQ = uuid -> HashSet of item ids used
# while a bench was fed from the bags (refilled once it closes). All memory only: reset on relog (KeptQuit), on a profile switch
# (settledKey) and by a restart - like the exemption they replace.
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap KEPT = new java.util.concurrent.ConcurrentHashMap();", sp))
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap KEPTKEY = new java.util.concurrent.ConcurrentHashMap();", sp))
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEENQ = new java.util.concurrent.ConcurrentHashMap();", sp))
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PENDQ = new java.util.concurrent.ConcurrentHashMap();", sp))
# 0.7.11 review fix 10 (shutdown latch): true from the first line of SkyySacksPlugin.shutdown() (false again in setup()). settledKey - the one
# gate of every item move between an inventory and a pool - answers null then: no sweep, no refill, no click and no bench feed can move
# items after the final pool save (a world-thread task already queued would otherwise run after it and its move would never be saved).
sp.addField(CtField.make("public static volatile boolean CLOSED = false;", sp))
''')
rep('''sp.addMethod(CtNewMethod.make("""
public static void exempt(String k, String item, long ms) {
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) EXEMPT.get(k);
  if (m == null) { m = new java.util.concurrent.ConcurrentHashMap(); java.util.concurrent.ConcurrentHashMap prev = (java.util.concurrent.ConcurrentHashMap) EXEMPT.putIfAbsent(k, m); if (prev != null) m = prev; }
  m.put(item, Long.valueOf(System.currentTimeMillis() + ms));
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static boolean isExempt(String k, String item) {
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) EXEMPT.get(k);
  if (m == null) return false;
  Long until = (Long) m.get(item);
  if (until == null) return false;
  if (until.longValue() < System.currentTimeMillis()) { m.remove(item); return false; }
  return true;
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static void clearExempt(String k) {
  EXEMPT.remove(k);
}""", sp))
''', '''# 0.7.11 the KEPT counts (field comment above). keptMap(k, create) = that key's map (null when absent and create is false).
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static java.util.concurrent.ConcurrentHashMap keptMap(String k, boolean create) {
  if (k == null) return null;
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) KEPT.get(k);
  if (m == null && create) {
    m = new java.util.concurrent.ConcurrentHashMap();
    java.util.concurrent.ConcurrentHashMap prev = (java.util.concurrent.ConcurrentHashMap) KEPT.putIfAbsent(k, m);
    if (prev != null) m = prev;
  }
  return m;
}\'\'\'), sp))
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long kept(String k, String item) {
  if (item == null) return 0L;
  java.util.concurrent.ConcurrentHashMap m = keptMap(k, false);
  if (m == null) return 0L;
  Long v = (Long) m.get(item);
  return v == null ? 0L : v.longValue();
}\'\'\'), sp))
# what really left the pool into the inventory (withdraw, Pick up all, stack refill): kept[item] += n
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void keep(String k, String item, long n) {
  if (k == null || item == null || n <= 0L) return;
  java.util.concurrent.ConcurrentHashMap m = keptMap(k, true);
  Long v = (Long) m.get(item);
  m.put(item, Long.valueOf((v == null ? 0L : v.longValue()) + n));
}\'\'\'), sp))
# withdraw: the item's hotbar + backpack stacks count as kept before the taken amount is added (kept[item] = max(kept, n))
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void raiseKept(String k, String item, long n) {
  if (k == null || item == null || n <= 0L) return;
  java.util.concurrent.ConcurrentHashMap m = keptMap(k, true);
  Long v = (Long) m.get(item);
  if (v == null || v.longValue() < n) m.put(item, Long.valueOf(n));
}\'\'\'), sp))
# Deposit all: forget the kept counts of that tab's items (homeOf == cat); returns how many entries went
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int clearKeptCat(String k, String cat) {
  java.util.concurrent.ConcurrentHashMap m = keptMap(k, false);
  if (m == null || cat == null) return 0;
  int n = 0;
  java.util.ArrayList ids = new java.util.ArrayList(m.keySet());
  for (int i = 0; i < ids.size(); i++) {
    String id = (String) ids.get(i);
    if (cat.equals(@PKG@.SackDefs.homeOf(id))) { m.remove(id); n++; }
  }
  return n;
}\'\'\'), sp))
# the stack refill's memory of a player (what they carried at the last tick + items used while a bench held the bags)
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void forgetSeen(java.util.UUID u) {
  if (u == null) return;
  SEENQ.remove(u);
  PENDQ.remove(u);
}\'\'\'), sp))
# relog: the player left (KeptQuit) - their kept counts and refill memory go (the last key used and the current one)
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void forgetKept(java.util.UUID u) {
  if (u == null) return;
  Object lk = KEPTKEY.remove(u);
  if (lk instanceof String) KEPT.remove(lk);
  try { KEPT.remove(pkey(u)); } catch (Throwable t) { }
  forgetSeen(u);
}\'\'\'), sp))
# a profile switch (settledKey saw a new KEY - review fix 4: a new epoch with the same key keeps them): both keys' kept counts and the
# player's refill memory go
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void dropKept(java.util.UUID u, String oldKey, String newKey) {
  if (oldKey != null) KEPT.remove(oldKey);
  if (newKey != null) KEPT.remove(newKey);
  forgetSeen(u);
}\'\'\'), sp))
''')
rep('''  if (moved || (lk != null && !lk.equals(k))) CHANGEDAT.put(u, Long.valueOf(now));
''', '''  if (moved || (lk != null && !lk.equals(k))) CHANGEDAT.put(u, Long.valueOf(now));
  // 0.7.11: a profile SWITCH (the key changed) also resets the kept counts of both keys and the refill memory (memory only, like the
  // 10-minute exemption they replace) - the inventory now belongs to another profile. Review fix 4: a new epoch with the SAME key (a
  // profile created, /profileadmin setclass of the active one, PROFILES-CONTRACT 3) keeps them - same profile, same inventory; the
  // settle window above still applies to it.
  if (lk != null && !lk.equals(k)) dropKept(u, lk, k);
''')
# review fix 10: the shutdown latch - nothing moves once SkyySacksPlugin.shutdown() began (SackPool.CLOSED)
rep('''#  - the pool file of the key cannot be read (ready).
''', '''#  - the pool file of the key cannot be read (ready);
#  - 0.7.11 review fix 10: the plugin is shutting down (SackPool.CLOSED, set first in shutdown()).
''')
rep('''public static String settledKey(java.util.UUID u) {
  if (u == null) return null;
''', '''public static String settledKey(java.util.UUID u) {
  if (u == null) return null;
  if (CLOSED) return null;
''')

# ================= C. the config texts say bags add up =================
rep('''    "# Rare / Legendary (old Large) bag holds; bag.omni is the Mythic Omni Bag, for every bag type (the best bag a player carries counts).",''',
    '''    "# Rare / Legendary (old Large) bag holds; bag.omni is the Mythic Omni Bag, for every bag type. The bags a player carries add up.",''')
rep('''                        "Most of each item a Unique bag (the old Medium) holds. The best bag carried counts."),''',
    '''                        "Most of each item a Unique bag (the old Medium) holds. Carried bags of a type add up."),''')

# ================= review fix 8: the server owner's stack refill switches (Server Setup -> Bags and Crafting) =================
# PROJECT-RULES 4 ("everything a server owner might change is editable in game"): bags.refill = the master switch (default on: every
# player's 3-way choice works; off = no stack refill for anyone - the choices are kept for when it is back on) and bags.refillDefault =
# the mode of players who never picked one (default hotbar = Skyy's R4 default). Bound fields on SackCfg (they exist before the kit's
# emit; RefillPref - compiled later - reads them); SackCfg.reload reads both keys from the file (hand edits); the after= hook logs a change.
RF_CFG_HELP = ("On: each player picks Hotbar only, Full inventory or Off on the bag page. Off: no refill for anyone.",
               "Players who never picked a mode on the bag page get this one (Hotbar only is the default).")
assert all(len(h) <= 100 for h in RF_CFG_HELP), "the kit's help limit is 100 characters"
rep('''scfg.addField(CtField.make("public static volatile boolean FREE_RECIPES = false;", scfg))
''', '''scfg.addField(CtField.make("public static volatile boolean FREE_RECIPES = false;", scfg))
# 0.7.11 review fix 8: bags.refill (the stack refill master switch) + bags.refillDefault (hotbar | full | off), bound fields: by the kit
scfg.addField(CtField.make("public static volatile boolean REFILL_ON = true;", scfg))
scfg.addField(CtField.make('public static volatile String REFILL_DEF = "hotbar";', scfg))
''')
rep('''    "#bags.cookedFood=false",
''', '''    "#bags.cookedFood=false",
    "# Stack refill (true or false): true lets every player pick Hotbar only, Full inventory or Off on the bag page; false turns it off.",
    "#bags.refill=true",
    "# The stack refill of players who never picked one: hotbar (Hotbar only), full (Full inventory) or off.",
    "#bags.refillDefault=hotbar",
''')
rep('''     "field:SackDefs.COOKED_FARM@config.properties:bags.cookedFood;after=SackCfg.cookedChanged"),
''', '''     "field:SackDefs.COOKED_FARM@config.properties:bags.cookedFood;after=SackCfg.cookedChanged"),
    # 0.7.11 review fix 8 (PROJECT-RULES 4): the owner's stack refill switches - live (RefillPref.mode reads them on every 2 s tick)
    ("bags.refill", "Stack refill from bags", "bags", "bool", "true", "", "", "", "", "live",
     "%s",
     "field:SackCfg.REFILL_ON@config.properties:bags.refill;after=SackCfg.refillChanged"),
    ("bags.refillDefault", "Stack refill default", "bags", "choice", "hotbar", "", "", "hotbar|Hotbar only,full|Full inventory,off|Off", "",
     "live", "%s",
     "field:SackCfg.REFILL_DEF@config.properties:bags.refillDefault;after=SackCfg.refillChanged"),
''' % RF_CFG_HELP)
# SackCfg.reload (the hand-edit RELOAD) reads both keys AFTER every 0.7.10 key through refillKeys (its own method: reload keeps its
# 0.7.10 locals and their slots - harness section I compares the code); an unknown default word = hotbar + one warning per file change
rep('''scfg.addMethod(CtNewMethod.make("""
public static synchronized void reload() {''', '''# 0.7.11 review fix 8: the stack refill owner keys of config.properties (bags.refill / bags.refillDefault) for reload() below; first = the
# first load (one log line then and on every change)
scfg.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void refillKeys(java.util.Properties p, boolean first) {
  boolean ro = boolKey(p, "bags.refill", true);
  String rd = String.valueOf(p.getProperty("bags.refillDefault", "hotbar")).trim().toLowerCase();
  if (rd.length() == 0) rd = "hotbar";
  if (!rd.equals("hotbar") && !rd.equals("full") && !rd.equals("off")) {
    @PKG@.SackPool.warn("config.properties: bags.refillDefault=" + rd + " is not hotbar, full or off - using hotbar");
    rd = "hotbar";
  }
  boolean changed = first || ro != REFILL_ON || !rd.equals(REFILL_DEF);
  REFILL_ON = ro;
  REFILL_DEF = rd;
  if (!changed) return;
  try { if (@PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: stack refill " + (ro ? ("ON (each player picks Hotbar only / Full inventory / Off on the bag page; players who never picked one: " + rd + ")") : "OFF for every player (bags.refill)")); } catch (Throwable t) { }
}\'\'\'), scfg))
scfg.addMethod(CtNewMethod.make("""
public static synchronized void reload() {''')
rep('''    pubFree();
  } catch (Throwable t) {
    if (!WARNED) { WARNED = true; com.skyy.sacks.SackPool.warn("could not read " + FILE + " - keeping craftSearch=" + SEARCH.get() + ", free bag recipes " + FREE_RECIPES + " and the current caps: " + t); }''',
    '''    refillKeys(p, first);   // 0.7.11 review fix 8: the stack refill owner switches (Server Setup rows bags.refill / bags.refillDefault)
    pubFree();
  } catch (Throwable t) {
    if (!WARNED) { WARNED = true; com.skyy.sacks.SackPool.warn("could not read " + FILE + " - keeping craftSearch=" + SEARCH.get() + ", free bag recipes " + FREE_RECIPES + " and the current caps: " + t); }''')
# the after= hook of both rows (the kit set the field already; the next 2 s tick and the next page view use it): one log line
rep('''# ================= KnowSync (0.7.7, research/Bag-Restructure-Spec.md 5.2 / 5.3): the bag recipe knowledge =================
''', '''# 0.7.11 review fix 8: after= hook of the bags.refill / bags.refillDefault rows (the kit set the field already; the next 2 s tick uses it)
scfg.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void refillChanged(String key) {
  try {
    if (@PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: stack refill " + (REFILL_ON ? ("ON - players who never picked a mode on the bag page get " + REFILL_DEF) : "OFF for every player (their choices are kept for when it is back on)"));
  } catch (Throwable t) { }
}\'\'\'), scfg))

# ================= KnowSync (0.7.7, research/Bag-Restructure-Spec.md 5.2 / 5.3): the bag recipe knowledge =================
''')

# ================= B. RefillPref (after SackNotice, before Processing) =================
rep('''# ================= Processing (0.7.0): timed Furnace / Tannery queues - our own per-player state, no block entity =================
''', '''# ================= RefillPref (0.7.11, Skyy R4 2026-10-02): the per-player STACK REFILL mode =================
# 0 = hotbar only (the default: no line for the player), 1 = full inventory (hotbar + main inventory + backpack), 2 = off. Per PLAYER (not
# per profile), chosen on the bag page, saved in Skyy_SkyySacks/refill.properties (uuid=hotbar|full|off) by the SackSaver thread - never on
# the world thread, and only after a player changed it (no file until then). An unknown word in the file reads as the default and is
# written back unchanged; an unreadable file is left untouched and the choices are remembered for this session only (SackNotice pattern).
# Review fix 8: "the default" = Server Setup bags.refillDefault (SackCfg.REFILL_DEF, hotbar unless the owner changed it); with bags.refill
# off (SackCfg.REFILL_ON false) mode() is off for everyone while choice() - what the page shows - keeps each player's pick.
RF_WORDS = ("hotbar", "full", "off")
RF_LABELS = ("Hotbar only", "Full inventory", "Off")
# the one-line explanation under the row. Review fix 1: no bench claim - vanilla benches do NOT use the bags yet (research/Bag-Craft-Link-
# Fix.md, SkyySacks 0.7.12), and the refill itself waits while a bench window is open (SweepTask.benchFed), so FULL tops up after the bench
# closes (Skyy's FULL use case: brewing / cooking / crafting from the inventory)
RF_HELP = ("A hotbar stack you use tops back up from your bags every 2 seconds (paused while a bench is open).",
           "Any stack you use - hotbar, inventory or backpack - tops back up every 2 seconds (paused while a bench is open).",
           "Stacks never top up by themselves - take items out on this page when you need them.")
RF_OFFSRV = "Stack refill is turned off on this server - your choice is kept for when it is back on."
assert len(RF_WORDS) == len(RF_LABELS) == len(RF_HELP) == 3
assert not any("enches already" in h or "enches still" in h or "use your bags" in h for h in RF_HELP + (RF_OFFSRV,)), "review fix 1"
rfp.addField(CtField.make("public static java.nio.file.Path FILE;", rfp))
rfp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap MODES = new java.util.concurrent.ConcurrentHashMap();", rfp))
rfp.addField(CtField.make("public static volatile boolean DIRTY = false;", rfp))
rfp.addField(CtField.make("public static boolean BROKEN = false;", rfp))
rfp.addField(CtField.make("public static boolean SAVEWARNED = false;", rfp))
rfp.addField(CtField.make("public static final String[] WORDS = " + _jarr(RF_WORDS) + ";", rfp))
rfp.addField(CtField.make("public static final String[] LABELS = " + _jarr(RF_LABELS) + ";", rfp))
rfp.addField(CtField.make("public static final String[] HELP = new String[] { " + ", ".join(jlit(h) for h in RF_HELP) + " };", rfp))
rfp.addField(CtField.make("public static final String OFFSRV = " + jlit(RF_OFFSRV) + ";", rfp))   # review fix 8: bags.refill off
rfp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int parse(String v) {
  if (v == null) return -1;
  String w = v.trim().toLowerCase();
  for (int i = 0; i < WORDS.length; i++) if (WORDS[i].equals(w)) return i;
  return -1;
}\'\'\'), rfp))
rfp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void load() {
  try {
    if (FILE == null || !java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    java.util.Enumeration en = p.propertyNames();
    int bad = 0;
    while (en.hasMoreElements()) {
      String k = (String) en.nextElement();
      String v = p.getProperty(k);
      MODES.put(k, v);
      if (parse(v) < 0) bad++;
    }
    if (bad > 0) @PKG@.SackPool.warn(FILE + ": " + bad + " line(s) are not hotbar, full or off - those players get the default (Server Setup bags.refillDefault); the lines are kept");
  } catch (Throwable t) {
    BROKEN = true;
    @PKG@.SackPool.warn("could not read " + FILE + " - stack refill choices are remembered for this session only (the file is left untouched): " + t);
  }
}\'\'\'), rfp))
# review fix 8: defMode() = the owner's default (bags.refillDefault; an unknown word = hotbar), choice(u) = the player's own pick or that
# default (what the page row shows), mode(u) = what the 2 s tick uses: off for everyone while bags.refill is off, else choice(u)
rfp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int defMode() {
  int d = parse(@PKG@.SackCfg.REFILL_DEF);
  return d < 0 ? 0 : d;
}\'\'\'), rfp))
rfp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int choice(java.util.UUID u) {
  if (u == null) return defMode();
  Object v = MODES.get(u.toString());
  int m = (v instanceof String) ? parse((String) v) : -1;
  return m < 0 ? defMode() : m;
}\'\'\'), rfp))
rfp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int mode(java.util.UUID u) {
  if (!@PKG@.SackCfg.REFILL_ON) return 2;
  return choice(u);
}\'\'\'), rfp))
rfp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean set(java.util.UUID u, int m) {
  if (u == null || m < 0 || m >= WORDS.length) return false;
  Object prev = MODES.put(u.toString(), WORDS[m]);
  if (!BROKEN && !WORDS[m].equals(prev)) DIRTY = true;
  return true;
}\'\'\'), rfp))
rfp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized void save() {
  if (!DIRTY || BROKEN || FILE == null) return;
  DIRTY = false;
  try {
    java.util.Properties p = new java.util.Properties();
    java.util.Iterator it = MODES.entrySet().iterator();
    while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); p.setProperty((String) e.getKey(), String.valueOf(e.getValue())); }
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp");
    java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
    try { p.store(out, "SkyySacks stack refill per player (uuid=hotbar|full|off; no line = the Server Setup default bags.refillDefault)"); out.flush(); out.getFD().sync(); } finally { out.close(); }
    try { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }); }
    catch (Throwable am) { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
  } catch (Throwable t) {
    DIRTY = true;
    if (!SAVEWARNED) { SAVEWARNED = true; @PKG@.SackPool.warn("could not save " + FILE + " (retried by the next save): " + t); }
  }
}\'\'\'), rfp))

# ================= Processing (0.7.0): timed Furnace / Tannery queues - our own per-player state, no block entity =================
''')

# ================= KeptQuit after SackPool.saveSoon (review fix 10 calls it; javassist: methods before callers) =================
rep('''# CraftPage fields + constructor first (SacksPage references it)
''', '''# ================= KeptQuit (0.7.11): a player who leaves gets fresh kept counts next time (relog = reset, Skyy R3) =================
# PlayerDisconnectEvent (registerGlobal in setup, the SkyyClasses ClassQuit pattern; PlayerReadyEvent is no login signal - it fires on
# every world switch, and a world switch keeps the kept counts). Only ConcurrentHashMap removals: safe on any thread.
# Review fix 10: the engine saves the player's inventory at disconnect, while the pool waits for the 10 s SackSaver - so the pool of the
# key the player's last 2 s tick used (KEPTKEY, read before forgetKept drops it) is written at once when it has unsaved moves (stack
# refills, sweeps): SackPool.saveSoon runs the SackSaver on the scheduler thread (never file work on this network thread unless the
# scheduler refuses the task at shutdown). A crash right after a quit can then no longer bring refilled items back into the bag.
kq.addInterface(pool.get("java.util.function.Consumer"))
kq.addConstructor(CtNewConstructor.make("public KeptQuit() { }", kq))
kq.addMethod(CtNewMethod.make(jt(r\'\'\'
public void accept(Object ev) {
  try {
    @PR@ pr = ((@PDE@) ev).getPlayerRef();
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    Object lk = u == null ? null : @PKG@.SackPool.KEPTKEY.get(u);
    @PKG@.SackPool.forgetKept(u);
    if (lk instanceof String && @PKG@.SackPool.DIRTY.containsKey(lk)) @PKG@.SackPool.saveSoon((String) lk);
  } catch (Throwable t) { }
}\'\'\'), kq))

# CraftPage fields + constructor first (SacksPage references it)
''')

# ================= C. SweepTask: bags add up =================
rep('''# 0.7.7 best bag per category (research/Bag-Restructure-Spec.md 5.5): the highest cap wins (bags never add up); on a tie the higher rarity
# rank (1-4 = Normal..Legendary, 6 = the Mythic Omni Bag) is kept for the page colour. Skyy_Sack_Omni offers CAP_OMNI to EVERY category in
# SackDefs.CATS (a later sixth bag type needs no change). A stack whose type or tier word is unknown is skipped (spec 12.2: 0.7.6 made such
# a type "carried" with cap 0). offerId is the whole rule for one item id (a pure function the bare-JVM test calls); scan() only walks
# storage, hotbar and backpack. Every caller keeps using caps(): sweep, withdraw, Deposit all, the bench link, the craft page, the tabs.
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void offer(java.util.HashMap caps, java.util.HashMap ranks, String cat, int cap, int rank) {
  Integer cur = (Integer) caps.get(cat);
  if (cur != null) {
    if (cur.intValue() > cap) return;
    if (cur.intValue() == cap) {
      Integer cr = (Integer) ranks.get(cat);
      if (cr != null && cr.intValue() >= rank) return;
    }
  }
  caps.put(cat, Integer.valueOf(cap));
  ranks.put(cat, Integer.valueOf(rank));
}\'\'\'), swp))
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void offerId(String id, java.util.HashMap caps, java.util.HashMap ranks) {
  if (id == null || !id.startsWith("Skyy_Sack_")) return;
  String[] cats = @PKG@.SackDefs.CATS;
  if (id.equals(@PKG@.SackDefs.OMNI)) {
    for (int k = 0; k < cats.length; k++) offer(caps, ranks, cats[k], @PKG@.SackDefs.CAP_OMNI, 6);
    return;
  }
  String[] parts = id.split("_");
  if (parts.length != 4 || @PKG@.SackDefs.catIndex(parts[2]) < 0) return;
  int rank = @PKG@.SackDefs.tierRank(parts[3]);
  if (rank <= 0) return;
  offer(caps, ranks, parts[2], @PKG@.SackDefs.tierCap(parts[3]), rank);
}\'\'\'), swp))
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void scan(@INV@ inv, java.util.HashMap caps, java.util.HashMap ranks) {
  if (inv == null) return;
  @IC@[] conts = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  for (int c = 0; c < conts.length; c++) {
    @IC@ cont = conts[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      offerId(it.getItemId(), caps, ranks);
    }
  }
}\'\'\'), swp))
''', '''# 0.7.11 BAGS ADD UP (Skyy R3 / R4 2026-10-02: "carrying 2-3 bags of the same type ADDS their space together"; 0.7.7-0.7.10 kept only
# the best one): every carried bag of a type adds its cap - a stack of n bags counts n times (bags are MaxStack 1 in game) - in long
# math, capped at Integer.MAX_VALUE. Skyy_Sack_Omni adds CAP_OMNI to EVERY category in SackDefs.CATS on top of the other bags (a later
# sixth bag type needs no change). ranks keeps the highest rarity rank per type (1-4 = Normal..Legendary, 6 = the Mythic Omni Bag) for
# the page colour; counts (optional) = type -> int[TIERS.length + 1] bags per rarity, the Omni last, for the page's "From 3 bags" line.
# A stack whose type or tier word is unknown is skipped (spec 12.2). bagOf is the whole rule for one stack (a pure function the bare-JVM
# test calls); scanN only walks storage, hotbar and backpack. Every caller keeps using caps(): sweep, withdraw, Deposit all, the bench
# link, the craft page, the tabs - lowering the space never deletes pooled items (the sweep only stops intake at the cap).
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void addBag(java.util.HashMap caps, java.util.HashMap ranks, java.util.HashMap counts, String cat, int cap, int rank, int n) {
  if (cat == null || n <= 0) return;
  Integer cur = (Integer) caps.get(cat);
  long sum = (cur == null ? 0L : (long) cur.intValue()) + (long) cap * (long) n;
  if (sum > 2147483647L) sum = 2147483647L;
  if (sum < 0L) sum = 0L;
  caps.put(cat, Integer.valueOf((int) sum));
  Integer cr = (Integer) ranks.get(cat);
  if (cr == null || cr.intValue() < rank) ranks.put(cat, Integer.valueOf(rank));
  if (counts == null) return;
  int top = @PKG@.SackDefs.TIERS.length;
  int[] c = (int[]) counts.get(cat);
  if (c == null) { c = new int[top + 1]; counts.put(cat, c); }
  int at = rank > top ? top : rank - 1;
  if (at < 0) at = 0;
  long nv = (long) c[at] + (long) n;
  c[at] = nv > 2147483647L ? 2147483647 : (int) nv;
}\'\'\'), swp))
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void bagOf(String id, int n, java.util.HashMap caps, java.util.HashMap ranks, java.util.HashMap counts) {
  if (id == null || n <= 0 || !id.startsWith("Skyy_Sack_")) return;
  String[] cats = @PKG@.SackDefs.CATS;
  if (id.equals(@PKG@.SackDefs.OMNI)) {
    for (int k = 0; k < cats.length; k++) addBag(caps, ranks, counts, cats[k], @PKG@.SackDefs.CAP_OMNI, 6, n);
    return;
  }
  String[] parts = id.split("_");
  if (parts.length != 4 || @PKG@.SackDefs.catIndex(parts[2]) < 0) return;
  int rank = @PKG@.SackDefs.tierRank(parts[3]);
  if (rank <= 0) return;
  addBag(caps, ranks, counts, parts[2], @PKG@.SackDefs.tierCap(parts[3]), rank, n);
}\'\'\'), swp))
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void scanN(@INV@ inv, java.util.HashMap caps, java.util.HashMap ranks, java.util.HashMap counts) {
  if (inv == null) return;
  @IC@[] conts = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  for (int c = 0; c < conts.length; c++) {
    @IC@ cont = conts[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      bagOf(it.getItemId(), it.getQuantity(), caps, ranks, counts);
    }
  }
}\'\'\'), swp))
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void scan(@INV@ inv, java.util.HashMap caps, java.util.HashMap ranks) {
  scanN(inv, caps, ranks, (java.util.HashMap) null);
}\'\'\'), swp))
''')

# ================= A. SweepTask: carried / keptDrop / the kept-aware sweep / sweepLeft =================
rep('''# sweep matching items into the pool. onlyCat == null -> every category; allContainers -> hotbar + backpack too. Returns items moved.
swp.addMethod(CtNewMethod.make(f"""
public static int sweep({PLA} p, String k, String onlyCat, boolean allContainers) {{
  {INV} inv = p.getInventory();
  if (inv == null) return 0;
  java.util.HashMap caps = caps(inv);
  if (caps.isEmpty()) return 0;
  int moved = 0;
  {IC}[] conts = allContainers ? new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }} : new {IC}[] {{ inv.getStorage() }};
  for (int c = 0; c < conts.length; c++) {{
    {IC} stor = conts[c];
    if (stor == null) continue;
    short cap2 = stor.getCapacity();
    for (short s = 0; s < cap2; s++) {{
      {IS} it = stor.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      String cat = {PKG}.SackDefs.catOf(id);
      if (cat == null) continue;
      if (onlyCat != null && !onlyCat.equals(cat)) continue;
      if (!allContainers && {PKG}.SackPool.isExempt(k, id)) continue;
      Integer catCap = (Integer) caps.get(cat);
      if (catCap == null) continue;
      long have = {PKG}.SackPool.get(k, id);
      long room = (long) catCap.intValue() - have;
      if (room <= 0L) continue;
      int qty = it.getQuantity();
      int take = (long) qty < room ? qty : (int) room;
      if (take <= 0) continue;
      {ISS} tx = stor.removeItemStackFromSlot(s, take);
      if (tx == null || !tx.succeeded()) continue;
      {IS} rem = tx.getRemainder();
      int removed = take - (rem == null ? 0 : rem.getQuantity());
      if (removed > 0) {{ {PKG}.SackPool.add(k, id, (long) removed); moved += removed; }}
    }}
  }}
  return moved;
}}""", swp))
''', '''# 0.7.11: how many of each item the player carries (storage + hotbar + backpack, the containers caps() scans): item id -> Long
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static java.util.HashMap carried(@INV@ inv) {
  java.util.HashMap out = new java.util.HashMap();
  if (inv == null) return out;
  @IC@[] conts = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  for (int c = 0; c < conts.length; c++) {
    @IC@ cont = conts[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if (id == null) continue;
      Long v = (Long) out.get(id);
      out.put(id, Long.valueOf((v == null ? 0L : v.longValue()) + (long) it.getQuantity()));
    }
  }
  return out;
}\'\'\'), swp))
# 0.7.11: kept drops to what the player carries (have = carried(inv)): blocks placed, items used, dropped or stored away lower it; an item
# no longer carried loses its entry. Returns how many entries changed. Never raises a count.
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int keptDrop(java.util.HashMap have, String k) {
  java.util.concurrent.ConcurrentHashMap m = @PKG@.SackPool.keptMap(k, false);
  if (m == null || m.isEmpty()) return 0;
  int n = 0;
  java.util.ArrayList ids = new java.util.ArrayList(m.keySet());
  for (int i = 0; i < ids.size(); i++) {
    String id = (String) ids.get(i);
    Long kv = (Long) m.get(id);
    if (kv == null) continue;
    Long hv = have == null ? null : (Long) have.get(id);
    long h = hv == null ? 0L : hv.longValue();
    if (h < kv.longValue()) {
      if (h <= 0L) m.remove(id); else m.put(id, Long.valueOf(h));
      n++;
    }
  }
  return n;
}\'\'\'), swp))
# sweep matching items into the pool. onlyCat == null -> every category; allContainers -> hotbar + backpack too. Returns items moved.
# 0.7.11 KEPT: the automatic sweep (main inventory only, allContainers false) leaves up to SackPool.kept(k, id) of what the player carries
# (storage + hotbar + backpack) alone and collects only what is above it - take out 512 stone, up to 512 stay; mine 10 more and the 10 go
# in. Deposit all (allContainers; the button cleared that tab's kept counts first) takes everything, as before. swept (optional) gets
# item id -> Long moved.
swp.addMethod(CtNewMethod.make(f"""
public static int sweep({PLA} p, String k, String onlyCat, boolean allContainers, java.util.HashMap swept) {{
  {INV} inv = p.getInventory();
  if (inv == null) return 0;
  java.util.HashMap caps = caps(inv);
  if (caps.isEmpty()) return 0;
  java.util.HashMap left = null;
  if (!allContainers) {{
    java.util.concurrent.ConcurrentHashMap km = {PKG}.SackPool.keptMap(k, false);
    if (km != null && !km.isEmpty()) {{
      java.util.HashMap held = carried(inv);
      left = new java.util.HashMap();
      java.util.Iterator ki = km.entrySet().iterator();
      while (ki.hasNext()) {{
        java.util.Map.Entry ke = (java.util.Map.Entry) ki.next();
        Long hv = (Long) held.get(ke.getKey());
        long ex = (hv == null ? 0L : hv.longValue()) - ((Long) ke.getValue()).longValue();
        left.put(ke.getKey(), Long.valueOf(ex < 0L ? 0L : ex));
      }}
    }}
  }}
  int moved = 0;
  {IC}[] conts = allContainers ? new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }} : new {IC}[] {{ inv.getStorage() }};
  for (int c = 0; c < conts.length; c++) {{
    {IC} stor = conts[c];
    if (stor == null) continue;
    short cap2 = stor.getCapacity();
    for (short s = 0; s < cap2; s++) {{
      {IS} it = stor.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      String cat = {PKG}.SackDefs.catOf(id);
      if (cat == null) continue;
      if (onlyCat != null && !onlyCat.equals(cat)) continue;
      Integer catCap = (Integer) caps.get(cat);
      if (catCap == null) continue;
      long have = {PKG}.SackPool.get(k, id);
      long room = (long) catCap.intValue() - have;
      if (room <= 0L) continue;
      Long ex = left == null ? null : (Long) left.get(id);
      if (ex != null && ex.longValue() < room) room = ex.longValue();
      if (room <= 0L) continue;
      int qty = it.getQuantity();
      int take = (long) qty < room ? qty : (int) room;
      if (take <= 0) continue;
      {ISS} tx = stor.removeItemStackFromSlot(s, take);
      if (tx == null || !tx.succeeded()) continue;
      {IS} rem = tx.getRemainder();
      int removed = take - (rem == null ? 0 : rem.getQuantity());
      if (removed > 0) {{
        {PKG}.SackPool.add(k, id, (long) removed);
        moved += removed;
        if (ex != null) left.put(id, Long.valueOf(ex.longValue() - (long) removed));
        if (swept != null) {{ Long sv = (Long) swept.get(id); swept.put(id, Long.valueOf((sv == null ? 0L : sv.longValue()) + (long) removed)); }}
      }}
    }}
  }}
  return moved;
}}""", swp))
swp.addMethod(CtNewMethod.make(f"""
public static int sweep({PLA} p, String k, String onlyCat, boolean allContainers) {{
  return sweep(p, k, onlyCat, allContainers, (java.util.HashMap) null);
}}""", swp))
# 0.7.11: the item ids the automatic sweep still wants from the main inventory but cannot take - their bag is full: the main inventory
# holds some and the player carries more than kept. Read AFTER the sweep. The stack refill skips them: refilling would only free room
# that the next sweep fills again from the main inventory (pool -> stack -> pool ping-pong).
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static java.util.HashSet sweepLeft(@INV@ inv, String k, java.util.HashMap caps) {
  java.util.HashSet out = new java.util.HashSet();
  if (inv == null || caps == null || caps.isEmpty()) return out;
  @IC@ stor = inv.getStorage();
  if (stor == null) return out;
  java.util.HashMap held = null;
  short cap = stor.getCapacity();
  for (short s = 0; s < cap; s++) {
    @IS@ it = stor.getItemStack(s);
    if (it == null || it.isEmpty()) continue;
    String id = it.getItemId();
    if (id == null || out.contains(id)) continue;
    String cat = @PKG@.SackDefs.catOf(id);
    if (cat == null || !caps.containsKey(cat)) continue;
    if (held == null) held = carried(inv);
    Long hv = (Long) held.get(id);
    if ((hv == null ? 0L : hv.longValue()) - @PKG@.SackPool.kept(k, id) > 0L) out.add(id);
  }
  return out;
}\'\'\'), swp))
''')
rep('''  if (added > 0) {{ {PKG}.SackPool.add(k, id, -(long) added); {PKG}.SackPool.exempt(k, id, 600000L); }}
''', '''  // 0.7.11: what really left the pool is KEPT (the sweep leaves up to that many alone; no timer). The item's hotbar + backpack stacks -
  // which the sweep never takes - count as kept first: taking a stack while you hold some in the hotbar (Hytale's default pickup spot)
  // must not make the sweep pull the new stack back in their place
  if (added > 0) {{
    {PKG}.SackPool.add(k, id, -(long) added);
    {PKG}.SackPool.raiseKept(k, id, (long) countIn(p.getInventory().getHotbar(), id) + (long) countIn(p.getInventory().getBackpack(), id));
    {PKG}.SackPool.keep(k, id, (long) added);
  }}
''')
# 0.7.11: how many of an item one container holds (withdraw: the hotbar + backpack part of the kept count)
rep('''# withdraw up to n of an item into STORAGE; returns how many actually left the pool
''', '''# 0.7.11: how many of an item one container holds
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int countIn(@IC@ cont, String id) {
  if (cont == null || id == null) return 0;
  int n = 0;
  short cap = cont.getCapacity();
  for (short s = 0; s < cap; s++) {
    @IS@ it = cont.getItemStack(s);
    if (it == null || it.isEmpty()) continue;
    if (id.equals(it.getItemId())) n += it.getQuantity();
  }
  return n;
}\'\'\'), swp))
# withdraw up to n of an item into STORAGE; returns how many actually left the pool
''')
# SweepTask.run moves below the BagMirror section (items() reads BagMirror.MIRRORS, a field javassist must see first)
rep('''swp.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (pr == null || !pr.isValid()) return;
    java.util.UUID nowWorld = pr.getWorldUuid();
    if (nowWorld == null || !nowWorld.equals(this.expectedWorld)) return;
    {REF} r = pr.getReference();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    if (p == null) return;
    String k = {PKG}.SackPool.settledKey(pr.getUuid());
    if (k == null) return;
    // 0.7.7 (research/Bag-Restructure-Spec.md 5.2 / 5.6 / 5.8), settled key only, world thread: the bag recipe knowledge follows coll:recipes,
    // carried bags get their rarity look, the one-time notice - each step on its own, so one failure never stops the sweep
    java.util.UUID u = pr.getUuid();
    try {{ {PKG}.KnowSync.sync(r, st, p, u); }} catch (Throwable t1) {{ {PKG}.KnowSync.warnOnce("bag recipe knowledge sync failed: " + t1); }}
    try {{ restamp(p.getInventory()); }} catch (Throwable t2) {{ {PKG}.KnowSync.warnOnce("bag rarity restamp failed: " + t2); }}
    try {{ if (!{PKG}.SackNotice.seen(u)) {PKG}.SackNotice.check(pr, u, k, !caps(p.getInventory()).isEmpty()); }} catch (Throwable t3) {{ }}
    sweep(p, k, null, false);
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("sweep failed: " + t); }}
}}""", swp))
''', '''# 0.7.11: SweepTask.refill / items / run follow the BagMirror section (items() reads BagMirror.MIRRORS)
''')

# ================= B. refill / items / run (after BagMirror) =================
rep('''# ================= CraftLinkTask (world thread, every 300ms per player) =================
''', '''# ================= 0.7.11 SweepTask (continued): STACK AUTO-REFILL + the 2 s item tick =================
# refill (Skyy R3 / R4 2026-10-02: "stacks you are using AUTO-REFILL from the bag every few seconds"): mode 0 = hotbar only, 1 = full
# inventory (hotbar + main inventory + backpack); inUse = the item ids the player used since the last tick. Every existing stack of such
# an item in those containers that is below its max stack size is topped up from the pool when the player carries a bag of its type
# (homeOf, like withdraw) and the pool has more: never an empty slot, never a stack with metadata, never a non-stacking item (max stack
# 1); ItemContainer.addItemStackToSlot merges into that slot only, the slot is read before and after and exactly what it gained leaves
# the pool and adds to KEPT (the sweep never pulls it back; more than asked - impossible by the engine's code - is undone and logged).
# Review fix 13: "metadata" = a document WITH entries; an empty document (nothing in it) counts as none - the stack is merged with a copy
# of that empty document (isStackableWith compares documents with equals, so a plain stack would be refused).
# skip = SweepTask.sweepLeft (bag full, spare items in the main inventory). done (optional) gets item id -> Long refilled. Returns items moved.
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int refill(@PLA@ p, String k, int mode, java.util.Set inUse, java.util.Set skip, java.util.HashMap done) {
  if (p == null || k == null || mode < 0 || mode > 1 || inUse == null || inUse.isEmpty()) return 0;
  @INV@ inv = p.getInventory();
  if (inv == null) return 0;
  java.util.HashMap caps = caps(inv);
  if (caps.isEmpty()) return 0;
  @IC@[] conts = mode == 1 ? new @IC@[] { inv.getHotbar(), inv.getStorage(), inv.getBackpack() } : new @IC@[] { inv.getHotbar() };
  int total = 0;
  for (int c = 0; c < conts.length; c++) {
    @IC@ cont = conts[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if (id == null || !inUse.contains(id)) continue;
      if (skip != null && skip.contains(id)) continue;
      String cat = @PKG@.SackDefs.homeOf(id);
      if (cat == null || !caps.containsKey(cat)) continue;
      long have = @PKG@.SackPool.get(k, id);
      if (have <= 0L) continue;
      org.bson.BsonDocument md = it.getMetadata();
      if (md != null && !md.isEmpty()) continue;
      @ITM@ item = it.getItem();
      int max = item == null ? 0 : item.getMaxStack();
      int q = it.getQuantity();
      if (max <= 1 || q <= 0 || q >= max) continue;
      int want = max - q;
      if ((long) want > have) want = (int) have;
      cont.addItemStackToSlot(s, md == null ? new @IS@(id, want) : new @IS@(id, want, md));
      @IS@ after = cont.getItemStack(s);
      int got = (after == null || after.isEmpty() || !id.equals(after.getItemId())) ? 0 : after.getQuantity() - q;
      if (got > want) {
        cont.setItemStackForSlot(s, it);
        @PKG@.SackPool.warn("stack refill: slot " + s + " (" + id + ") gained " + got + " of " + want + " asked - undone");
        continue;
      }
      if (got <= 0) continue;
      @PKG@.SackPool.add(k, id, -(long) got);
      @PKG@.SackPool.keep(k, id, (long) got);
      total += got;
      if (done != null) {
        Long dv = (Long) done.get(id);
        done.put(id, Long.valueOf((dv == null ? 0L : dv.longValue()) + (long) got));
      }
    }
  }
  return total;
}\'\'\'), swp))
# Review fix 9: is a bench fed from the bags right now? true = a BagMirror exists for the key AND one of the player's open windows is a
# MaterialContainerWindow (the bench windows CraftLinkTask attaches mirrors to). A mirror with no open bench window (the bench just closed,
# the /craft page's last view, or a bench link that failed before removing it) is synced first - sync() books what a bench took out of it
# into the pool, idempotent, world thread like CraftLinkTask - and dropped (exactly CraftLinkTask's no-bench branch), so the refill below
# reads the right pool and a failed bench link can no longer pause the refill until a restart. A sync that throws leaves the mirror and
# skips this refill (the caller logs it once): never a refill on top of consumption that is not booked yet.
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean benchFed(@PLA@ p, String k) {
  if (k == null) return false;
  @PKG@.BagMirror m = (@PKG@.BagMirror) @PKG@.BagMirror.MIRRORS.get(k);
  if (m == null) return false;
  @WM@ wm = p == null ? null : p.getWindowManager();
  java.util.List wins = wm == null ? null : wm.getWindows();
  for (int i = 0; wins != null && i < wins.size(); i++) if (wins.get(i) instanceof @MCW@) return true;
  int c = m.sync();
  if (c > 0) @PKG@.SackPool.saveSoon(k);
  @PKG@.BagMirror.MIRRORS.remove(k, m);
  return false;
}\'\'\'), swp))
# items(): the item work of one 2 s tick for a SETTLED key (world thread; run() below gets the key from SackPool.settledKey, the one gate:
# nothing happens while a profile loads, switches or is busy): (1) "used" = the items the player now carries fewer of than at the end of
# the last tick (SEENQ - our own moves happen before that snapshot, so they never count) + the items still pending; (2) kept drops to
# what the player carries; (3) the automatic sweep; (4) the stack refill of the used items (mode from RefillPref; off = nothing). While a
# bench is fed from the bags (benchFed: a mirror for the key AND an open bench window) the refill waits and the used items stay pending in
# PENDQ: the mirror offers pool items to that bench, so taking them out here could let the bench use them twice. (5) the new SEENQ
# snapshot. Returns {swept, refilled}.
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int[] items(@PLA@ p, String k, java.util.UUID u) {
  int[] out = new int[] { 0, 0 };
  if (p == null || k == null) return out;
  @INV@ inv = p.getInventory();
  if (inv == null) return out;
  if (u != null) @PKG@.SackPool.KEPTKEY.put(u, k);
  java.util.HashMap before = carried(inv);
  java.util.HashSet used = new java.util.HashSet();
  java.util.HashMap seen = u == null ? null : (java.util.HashMap) @PKG@.SackPool.SEENQ.get(u);
  if (seen != null) {
    java.util.Iterator si = seen.entrySet().iterator();
    while (si.hasNext()) {
      java.util.Map.Entry se = (java.util.Map.Entry) si.next();
      Long now = (Long) before.get(se.getKey());
      if ((now == null ? 0L : now.longValue()) < ((Long) se.getValue()).longValue()) used.add(se.getKey());
    }
  }
  java.util.HashSet pend = u == null ? null : (java.util.HashSet) @PKG@.SackPool.PENDQ.remove(u);
  if (pend != null) used.addAll(pend);
  try { keptDrop(before, k); } catch (Throwable t1) { @PKG@.KnowSync.warnOnce("kept count update failed: " + t1); }
  try { out[0] = sweep(p, k, (String) null, false); } catch (Throwable t0) { @PKG@.SackPool.warn("sweep failed: " + t0); }
  int mode = @PKG@.RefillPref.mode(u);
  if (mode != 2 && !used.isEmpty()) {
    try {
      if (benchFed(p, k)) { if (u != null) @PKG@.SackPool.PENDQ.put(u, used); }
      else out[1] = refill(p, k, mode, used, sweepLeft(inv, k, caps(inv)), (java.util.HashMap) null);
    } catch (Throwable t2) { @PKG@.KnowSync.warnOnce("stack refill failed: " + t2); }
  }
  if (u != null) @PKG@.SackPool.SEENQ.put(u, carried(inv));
  return out;
}\'\'\'), swp))
swp.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (pr == null || !pr.isValid()) return;
    java.util.UUID nowWorld = pr.getWorldUuid();
    if (nowWorld == null || !nowWorld.equals(this.expectedWorld)) return;
    {REF} r = pr.getReference();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    if (p == null) return;
    String k = {PKG}.SackPool.settledKey(pr.getUuid());
    if (k == null) return;
    // 0.7.7 (research/Bag-Restructure-Spec.md 5.2 / 5.6 / 5.8), settled key only, world thread: the bag recipe knowledge follows coll:recipes,
    // carried bags get their rarity look, the one-time notice - each step on its own, so one failure never stops the sweep
    java.util.UUID u = pr.getUuid();
    try {{ {PKG}.KnowSync.sync(r, st, p, u); }} catch (Throwable t1) {{ {PKG}.KnowSync.warnOnce("bag recipe knowledge sync failed: " + t1); }}
    try {{ restamp(p.getInventory()); }} catch (Throwable t2) {{ {PKG}.KnowSync.warnOnce("bag rarity restamp failed: " + t2); }}
    try {{ if (!{PKG}.SackNotice.seen(u)) {PKG}.SackNotice.check(pr, u, k, !caps(p.getInventory()).isEmpty()); }} catch (Throwable t3) {{ }}
    // 0.7.11: kept counts + the sweep + the stack refill (items above)
    items(p, k, u);
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("sweep failed: " + t); }}
}}""", swp))

# ================= CraftLinkTask (world thread, every 300ms per player) =================
''')

# ================= SackSaver + shutdown save the refill choices =================
rep('''  try {{ {PKG}.SackNotice.save(); }} catch (Throwable t) {{ }}
}}""", sav))''', '''  try {{ {PKG}.SackNotice.save(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.RefillPref.save(); }} catch (Throwable t) {{ }}   // 0.7.11: the stack refill choices (only after a player changed one)
}}""", sav))''')
rep('''  try {{ {PKG}.SackNotice.save(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CfgPub.shutdown(); }} catch (Throwable t) {{ }}''', '''  try {{ {PKG}.SackNotice.save(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.RefillPref.save(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CfgPub.shutdown(); }} catch (Throwable t) {{ }}''')

# ================= SacksPage: the bag count line, the refill row, the clicks =================
rep('''page.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int rankOf(java.util.HashMap ranks, String cat) {''', '''# 0.7.11 BAGS ADD UP on the page: how many bags make up a type's space (c = SweepTask.scanN counts: bags per rarity, the Omni last) and the
# line under the cap line - "From 1 Legendary bag - another bag of this type adds its space" / "From 3 bags: 2 Normal + 1 Legendary -
# their space adds up" (shown with set(): punctuation is safe)
page.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int bagCount(int[] c) {
  if (c == null) return 0;
  long n = 0L;
  for (int i = 0; i < c.length; i++) if (c[i] > 0) n += (long) c[i];
  return n > 2147483647L ? 2147483647 : (int) n;
}\'\'\'), page))
page.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String bagsLine(int[] c) {
  int n = bagCount(c);
  if (n <= 0) return "";
  int top = @PKG@.SackDefs.TIERS.length;
  String omni = @PKG@.SackDefs.RAR_NAME[@PKG@.SackDefs.RAR_NAME.length - 1] + " Omni";
  if (n == 1) {
    for (int i = 0; i < c.length; i++) {
      if (c[i] <= 0) continue;
      if (i >= top) return "From the " + @PKG@.SackDefs.bagName(@PKG@.SackDefs.OMNI) + " - any other bag you carry adds its space";
      return "From 1 " + @PKG@.SackDefs.RAR_NAME[i] + " bag - another bag of this type adds its space";
    }
    return "";
  }
  StringBuilder sb = new StringBuilder();
  sb.append("From ").append(n).append(" bags: ");
  boolean first = true;
  for (int i = 0; i < c.length; i++) {
    if (c[i] <= 0) continue;
    if (!first) sb.append(" + ");
    first = false;
    sb.append(c[i]).append(' ').append(i >= top ? omni : @PKG@.SackDefs.RAR_NAME[i]);
  }
  sb.append(" - their space adds up");
  return sb.toString();
}\'\'\'), page))
# 0.7.11 the STACK REFILL row (a per-player setting, every view of the page): the kit's settings row with three small tertiary buttons,
# the chosen one on Tertiary_Active (skyyui.on_off widened to three), and a one-line explanation. ids SkyySRefill*; events refill:<word>.
SUI.verify()
KIT_ID = SUI.kit_id()
RF_SUF = ("Hotbar", "Full", "Off")                      # button id suffixes, in RefillPref.WORDS order
RF_ROW_LABEL = "Stack refill from your bags"
RF_BTN_W, RF_GAP, RF_LABEL_W, RF_HELP_H = 176, 6, 380, 24
RF_ROW = SUI.setting_row("SkyySRefill", "SkyySRefillLbl", label_w=RF_LABEL_W, gap=0)
RF_BTNS = [tuple(SUI.button("SkyySRefill" + RF_SUF[i], RF_LABELS[i], "tertiary", "small", w=RF_BTN_W, selected=sel,
                            anchor={"top": (SUI.SETTING_ROW_H - SUI.BTN_SMALL_H) // 2, "left": RF_GAP if i else 0})
                 for sel in (True, False)) for i in range(3)]
RF_HELP_LBL = SUI.label("SkyySRefillHelp", "", "caption", h=RF_HELP_H, align="Center")
SUI.assert_proven([RF_ROW, RF_HELP_LBL] + [mk for pair in RF_BTNS for mk in pair], what="SkyySacks stack refill row")
RF_ROW_H, RF_W = SUI.outer_size(RF_ROW)[1], 1000 - 2 * 17
assert RF_ROW_H == SUI.SETTING_ROW_H and SUI.outer_size(RF_HELP_LBL)[1] == RF_HELP_H
assert 16 + RF_LABEL_W + 3 * RF_BTN_W + 2 * RF_GAP <= RF_W, "the refill row is wider than the page body"
assert SUI.text_width(RF_ROW_LABEL, 18) <= RF_LABEL_W, "the row label does not fit"
for _h in RF_HELP + (RF_OFFSRV,):
    assert SUI.text_width(_h, SUI.fs(12)) <= RF_W - 8, "refill help line too wide for one line: " + _h
# the page height (root 690, was 640): body = 690 - 38 title bar - 25 padding = 627. Carried view: 44 tabs + 1 + 22 grey-tab note + 34 cap
# + 22 bags line + 26 next + 4 x 78 grid + 28 info + 44 actions + 44 refill row + 24 help = 601. Not-carried view: 541 (0.7.7) + 68 = 609.
assert 44 + 1 + 22 + 34 + 22 + 26 + 4 * 78 + 28 + 44 + RF_ROW_H + RF_HELP_H <= 690 - 38 - 25
assert 541 + RF_ROW_H + RF_HELP_H <= 690 - 38 - 25
RF_JAVA = "\\n".join(["  " + SUI.java_append("SkyySBody", RF_ROW), "  " + SUI.java_set("SkyySRefillLbl", "Text", RF_ROW_LABEL)]
                    + ["  " + SUI.java_append("SkyySRefill", SUI.choose("rmode == %d" % i, RF_BTNS[i][0], RF_BTNS[i][1])) for i in range(3)]
                    + ['  ev.addEventBinding(@BT@.Activating, "#SkyySRefill%s", @EVD@.of("a", "refill:%s"));' % (RF_SUF[i], RF_WORDS[i])
                       for i in range(3)]
                    + ["  " + SUI.java_append("SkyySBody", RF_HELP_LBL)])
page.addMethod(CtNewMethod.make(jt(r\'\'\'
public void refillRow(@UCB@ b, @UEB@ ev, int rmode) {
@RFJAVA@
  int m = rmode < 0 || rmode >= @PKG@.RefillPref.HELP.length ? 0 : rmode;
  b.set("#SkyySRefillHelp.Text", @PKG@.SackCfg.REFILL_ON ? @PKG@.RefillPref.HELP[m] : @PKG@.RefillPref.OFFSRV);
}\'\'\'.replace("@RFJAVA@", RF_JAVA)), page))
# 0.7.11: the bags line under the cap line (kit label: the page's 14 px #96a9be line look)
BAGS_LBL = SUI.label("SkyySBags", "", "default", h=22, size=14, col="text", align="Center")
SUI.assert_proven([BAGS_LBL], what="SkyySacks bags line")
BAGS_JAVA = SUI.java_append("SkyySBody", BAGS_LBL)
page.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int rankOf(java.util.HashMap ranks, String cat) {''')
rep('''  b.appendInline((String) null, "Group #SkyySacks { Anchor: (Width: 1000, Height: 640); }");''',
    '''  b.appendInline((String) null, "Group #SkyySacks { Anchor: (Width: 1000, Height: 690); }");''')
rep('''  if (!this.carried) { buildNoBag(b, player, k, caps, u); return; }''',
    '''  int rmode = @PKG@.RefillPref.choice(u);   // review fix 8: the player's pick (or the server default); the help line says when it is off
  if (!this.carried) { buildNoBag(b, player, k, caps, u); refillRow(b, ev, rmode); return; }''')
rep('''  String bagWord = rank > @PKG@.SackDefs.TIERS.length ? @PKG@.SackDefs.bagName(@PKG@.SackDefs.OMNI) : (@PKG@.SackDefs.RAR_NAME[ri] + " bag");
  b.appendInline("#SkyySBody", "Label #SkyySCap { Anchor: (Height: 34); Text: \\"\\"; Style: (FontSize: 18, RenderBold: true, TextColor: " + @PKG@.SackDefs.RAR_PAGE[ri] + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyySCap.Text", this.cat + " - " + bagWord + " - up to " + num(capacity) + " of each item - " + num(stored) + " stored");
''', '''  // 0.7.11: bags add up - the cap line names how many bags make the space, the line below says which
  java.util.HashMap counts = new java.util.HashMap();
  if (player != null) @PKG@.SweepTask.scanN(player.getInventory(), new java.util.HashMap(), new java.util.HashMap(), counts);
  int[] bc = (int[]) counts.get(this.cat);
  int nb = bagCount(bc);
  String bagWord = nb > 1 ? (nb + " bags") : (rank > @PKG@.SackDefs.TIERS.length ? @PKG@.SackDefs.bagName(@PKG@.SackDefs.OMNI) : (@PKG@.SackDefs.RAR_NAME[ri] + " bag"));
  b.appendInline("#SkyySBody", "Label #SkyySCap { Anchor: (Height: 34); Text: \\"\\"; Style: (FontSize: 18, RenderBold: true, TextColor: " + @PKG@.SackDefs.RAR_PAGE[ri] + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyySCap.Text", this.cat + " - " + bagWord + " - up to " + num(capacity) + " of each item - " + num(stored) + " stored");
@BAGSJAVA@
  b.set("#SkyySBags.Text", bagsLine(bc));
''')
rep('''  ev.addEventBinding(@BT@.Activating, "#SkyySPickAll", @EVD@.of("a", "pickall"));
  ev.addEventBinding(@BT@.Activating, "#SkyySDepAll", @EVD@.of("a", "depall"));
}\'\'\'), page))''', '''  ev.addEventBinding(@BT@.Activating, "#SkyySPickAll", @EVD@.of("a", "pickall"));
  ev.addEventBinding(@BT@.Activating, "#SkyySDepAll", @EVD@.of("a", "depall"));
  refillRow(b, ev, rmode);
}\'\'\'.replace("@BAGSJAVA@", "  " + BAGS_JAVA)), page))''')
rep('''    // 0.7.5: the how-to-craft view (a bag the player does not carry) has no item buttons - a stray event only refreshes it
    if (!this.carried) {{ rebuild(); return; }}''', '''    // 0.7.11: the stack refill choice (a per-player setting, every view; no item moves, so no settled key needed); saved by the SackSaver
    for (int m = 0; m < {PKG}.RefillPref.WORDS.length; m++) {{
      if (data.indexOf("refill:" + {PKG}.RefillPref.WORDS[m] + "\\\\"") >= 0) {{
        {PKG}.RefillPref.set(u, m);
        this.info = "Stack refill: " + {PKG}.RefillPref.LABELS[m] + ({PKG}.SackCfg.REFILL_ON ? "" : " (turned off on this server for now)");
        {PKG}.SackPool.saveSoon((String) null);
        rebuild();
        return;
      }}
    }}
    // 0.7.5: the how-to-craft view (a bag the player does not carry) has no item buttons - a stray event only refreshes it
    if (!this.carried) {{ rebuild(); return; }}''')
rep('''      {PKG}.SackPool.clearExempt(k);
      int moved = {PKG}.SweepTask.sweep(player, k, this.cat, true);''', '''      // 0.7.11: Deposit all forgets this tab's kept counts (and the refill memory: the deposited stacks are no "use")
      {PKG}.SackPool.clearKeptCat(k, this.cat);
      {PKG}.SackPool.forgetSeen(u);
      int moved = {PKG}.SweepTask.sweep(player, k, this.cat, true);''')

rep('''# dynamic text goes through set(). Height budget inside the 577 px body: 44 tabs + 1 + 22 grey-tab note + 34 + 46 + 28 + 80 + 30 + 28 +
# 5 x 26 ladder + 30 + 28 + 40 = 541.''', '''# dynamic text goes through set(). Height budget inside the 577 px body: 44 tabs + 1 + 22 grey-tab note + 34 + 46 + 28 + 80 + 30 + 28 +
# 5 x 26 ladder + 30 + 28 + 40 = 541. 0.7.11: + the stack refill row 44 + help 24 = 609 of the 627 px body (root 690).''')
rep('''# carried at its cap. Height budget of the carried view: 44 + 1 + 22 + 34 + 26 + 4 x 78 + 28 + 44 = 511 of the 577 px body (640 root -
# 38 title bar - 25 padding); the root anchor has only Width / Height.''', '''# carried at its cap. Height budget of the carried view: 44 + 1 + 22 + 34 + 26 + 4 x 78 + 28 + 44 = 511 of the 577 px body (640 root -
# 38 title bar - 25 padding); the root anchor has only Width / Height. 0.7.11: root 690 (body 627) for the bags line 22 + the stack refill
# row 44 + help 24 = 601; the cap line names how many bags make the space ("3 bags"), the refill row closes both views.''')
# review fix 11: stale "best bag" comments (bags add up since 0.7.11; the tab colour = the rarest bag of that type carried)
rep('''# 0.7.7 render(): the vanilla frame, the five tabs (rarity colour of the best bag carried; grey = not carried), then the carried view (cap''',
    '''# 0.7.7 render(): the vanilla frame, the five tabs (rarity colour of the rarest bag of that type carried; grey = not carried), then the carried view (cap''')
rep('''# never refused, it only swaps the row's usual danger question for this one (an upgrade would lower the cap; gameplay stays right because
# the best bag carried counts). The kit ignores a "?" answer on import / restore. value = the kit's canonical whole number. The question
# stays under the kit's 200-character limit even with 7-digit caps.''', '''# never refused, it only swaps the row's usual danger question for this one (an upgrade would lower the cap; nothing breaks - since 0.7.11
# the carried bags of a type add up, so keeping the old bag too keeps its space). The kit ignores a "?" answer on import / restore. value =
# the kit's canonical whole number. The question stays under the kit's 200-character limit even with 7-digit caps.''')
# review fix 1: the "no bag" view's hint said a Workbench uses the bag materials - false until 0.7.12 (research/Bag-Craft-Link-Fix.md);
# the SkyySacks /craft page does craft from the bags (CraftPage.materialsFor)
rep('''  b.set("#SkyySNbHint.Text", "A Workbench can use the materials in the bags you carry. Unlocked bag recipes are also on the Collections tab of /craft.");''',
    '''  b.set("#SkyySNbHint.Text", "/craft can use the materials in the bags you carry. Unlocked bag recipes are also on the Collections tab of /craft.");''')

# ================= plugin: load the refill choices, the quit listener, the ready line =================
rep('''  {PKG}.SackNotice.load();
  {PKG}.SackCfg.pubFree();''', '''  {PKG}.SackNotice.load();
  // 0.7.11: the per-player stack refill mode (refill.properties, written by the SackSaver only after a player changed it) and the quit
  // listener that forgets a leaving player's kept counts (a relog starts fresh, like the 10-minute exemption they replace)
  {PKG}.RefillPref.FILE = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("refill.properties");
  {PKG}.RefillPref.load();
  getEventRegistry().registerGlobal({PDE}.class, new {PKG}.KeptQuit());
  {PKG}.SackPool.CLOSED = false;   // review fix 10: the shutdown latch opens again (a plugin started again in the same JVM)
  {PKG}.SackCfg.pubFree();''')
# review fix 10: the shutdown latch closes FIRST - settledKey answers null from here on, so no world-thread task that is still queued (a 2 s
# tick, a bench feed, a page click) moves items after the final pool save below
rep('''protected void shutdown() {{
  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}''', '''protected void shutdown() {{
  {PKG}.SackPool.CLOSED = true;   // 0.7.11 review fix 10: the shutdown latch (SackPool.settledKey answers null from here on)
  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}''')
# review fix 1: the ready line no longer says "benches craft from your bags" (false until 0.7.12) - /craft does
rep('''right-click a magic bag; benches craft from your bags (their ingredients first); storage per profile (pkey); settings: SkyWynn Menu -> Server Setup -> Bags and Crafting (skyysacks.admin) or Skyy_SkyySacks/config.properties");''',
    '''right-click a magic bag; /craft crafts from your bags (vanilla benches do not show bag materials yet); withdrawn items stay in your inventory (kept counts, no timer); stack refill from your bags (Hotbar only / Full inventory / Off on the bag page; owner switches bags.refill / bags.refillDefault); carried bags of a type add up; storage per profile (pkey); settings: SkyWynn Menu -> Server Setup -> Bags and Crafting (skyysacks.admin) or Skyy_SkyySacks/config.properties; UI kit {KIT_ID}");''')
rep('''for c in (defs, sp, scfg, ksync, snot, pjob, pben, pst, swp, tick, sav, cmp, page, cmd, fac, mir, clt, ctk, rcmp, clog, cpg, ccmd, cfac, ptk, ptick, pl):
    c.writeFile(OUT)
''', '''for c in (defs, sp, scfg, ksync, snot, rfp, kq, pjob, pben, pst, swp, tick, sav, cmp, page, cmd, fac, mir, clt, ctk, rcmp, clog, cpg, ccmd, cfac, ptk, ptick, pl):
    c.writeFile(OUT)   # 0.7.11: + RefillPref, KeptQuit
''')

# ================= self-checks =================
assert 'VERSION = "0.7.11"' in s and "EXEMPT" not in s.split('"""', 2)[2] and "isExempt" not in s and "clearExempt" not in s and "600000L" not in s
assert s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0, "no new command or ECS system"
assert s.count("registerGlobal(") == 1 and s.count("new {PKG}.KeptQuit()") == 1
assert s.count("public void run() {{") >= 1 and s.count("items(p, k, u);") == 1 and "sweep(p, k, null, false);" not in s
assert s.count("@BAGSJAVA@") == 2 and s.count("@RFJAVA@") == 2 and s.count("refillRow(b, ev, rmode);") == 2
for _a, _b in (("public static java.util.concurrent.ConcurrentHashMap keptMap(", "public static String settledKey("),
               ("public static void dropKept(", "public static String settledKey("),
               ("rfp = pool.makeClass(", "# ================= RefillPref (0.7.11"),
               ("# ================= RefillPref (0.7.11", "# ================= SweepTask (runs ON world thread"),
               ("public static void scanN(", "public static java.util.HashMap caps("),
               ("public static java.util.HashMap carried(", "public static int sweep({PLA} p, String k, String onlyCat, boolean allContainers, java.util.HashMap swept)"),
               ("public static java.util.HashSet sweepLeft(", "public static int refill("),
               ("mir.addField(CtField.make(\"public static final java.util.concurrent.ConcurrentHashMap MIRRORS", "public static int[] items("),
               ("public static int refill(", "public static int[] items("), ("public static int[] items(", "    items(p, k, u);"),
               ("public void refillRow(", "public void render("), ("public static String bagsLine(", "public void render("),
               ("# ================= KeptQuit", "# ================= plugin ================="),
               # review fixes: benchFed before its caller, KeptQuit after SackPool.saveSoon (javassist: methods before callers), the refill
               # owner fields before SackCfg.reload / RefillPref read them
               ("public static boolean benchFed(", "public static int[] items("),
               ("public static void saveSoon(String k) {{", "# ================= KeptQuit (0.7.11)"),
               ("public static volatile boolean REFILL_ON = true;", "public static synchronized void reload() {"),
               ("public static void refillChanged(String key) {", "kit = CFG.emit(")):
    assert 0 <= s.find(_a) < s.find(_b), "order: %s before %s" % (_a[:50], _b[:50])
# review fix 1: no text claims that vanilla benches use the bags (false until 0.7.12)
assert "benches craft from your bags" not in s and "A Workbench can use the materials" not in s and "Benches already use" not in s \
    and "Benches still use" not in s, "review fix 1"
# review fix 4: only a key change resets kept (the epoch-only change keeps it)
assert "if (lk != null && !lk.equals(k)) dropKept(u, lk, k);" in s and "dropKept(u, lk, k); }" not in s, "review fix 4"
# review fix 8: the owner rows + their template lines
assert s.count('("bags.refill", "Stack refill from bags"') == 1 and s.count('("bags.refillDefault", "Stack refill default"') == 1 \
    and s.count('"#bags.refill=true",') == 1 \
    and s.count('"#bags.refillDefault=hotbar",') == 1 and s.count("    refillKeys(p, first);") == 1, "review fix 8"
# review fix 9: the refill pause looks at the open windows
assert "benchFed(p, k)" in s and "BagMirror.MIRRORS.containsKey(k)" not in s, "review fix 9"
# review fix 10: the shutdown latch (set first in shutdown, reset in setup, checked in settledKey) + the quit save
assert s.count("{PKG}.SackPool.CLOSED = true;") == 1 and s.count("{PKG}.SackPool.CLOSED = false;") == 1 and s.count("if (CLOSED) return null;") == 1 \
    and "@PKG@.SackPool.saveSoon((String) lk);" in s, "review fix 10"
# review fix 11: no stale "best bag" comment
assert "the best bag carried counts" not in s and "rarity colour of the best bag carried" not in s, "review fix 11"
# review fix 13: an empty metadata document counts as none
assert "if (md != null && !md.isEmpty()) continue;" in s and "if (it.getMetadata() != null) continue;" not in s, "review fix 13"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
