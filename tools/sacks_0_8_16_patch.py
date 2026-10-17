"""Derive SkyySacks/build_skyysacks_0.8.16.py from the SET pin 0.8.15 (the GENERATED build_skyysacks_0.8.15.py; edit THIS file, then
regenerate: python tools/sacks_0_8_16_patch.py; never re-run sacks_0_8_15_patch.py on top of it). The chain: ... -> sacks_0_8_15_patch.py ->
0.8.15 (generated, the SET pin) -> this patch -> 0.8.16. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.8.15 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_16_patch.py   then   python SkyySacks/build_skyysacks_0.8.16.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.16.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.16 = round small16 (2026-10-16; Skyy "work through the small things and the next up list"), two answers of docs/answered/bags.md:
  A. SEEDS / SAPLINGS TOGGLES - popup Q "BAGS: seeds / saplings from a harvest go to the Void, so replanting means pulling them out. Keep?"
     -> "add a toggle for each. (seeds in farming. saplings in foraging where they belong. )"
     1. Saplings (Plant_Sapling_*, the 34 vanilla saplings - the same rule as SkyyBazaar 0.1.15's Foraging tab) belong to the FORAGING
        category now (homeOf; were Farming as Plant_*). The pool is keyed by item id, so saplings already stored simply show (and count)
        in Foraging from now on - nothing moves, nothing is deleted. Seeds (Plant_Seeds_*: crop seeds, Eternal seeds, seed bags) stay Farming.
     2. Two PLAYER switches in /settings (the SkyyMenu Settings registry, tab "sacks", default ON = the 0.8.15 behaviour):
        "Seeds go into the Void" (sacks.seedsVoid, Farming) and "Saplings go into the Void" (sacks.saplingsVoid, Foraging). OFF = auto-pickup
        (block drops, harvests, mob drops) puts them in the INVENTORY (never the Void; the ground only when the inventory is full, as for
        any item) and the 2 s sweep + Deposit all leave them in the inventory. The Deposit button with an amount (one picked item) still
        stores them on purpose. Read through SackPool.keepFlags (settings:fn:get, every 2 s tick per online player = part of the sweep
        signature, so switching back ON sweeps them in at once); SackDefs.intake(uuid, id) = catOf + the switches.
        The Settings registry is per PLAYER (the same on every profile), like every other /settings switch.
  B. PICKUP POPUP + FEED LOOK - popup Q "BAGS: the vanilla 'picked up' popup still flashes next to our feed card. Keep it?" -> "hide it.
     but try to make our feed look more like the vanilla or better. right now its meh at best."
     1. HIDING IT IS POSSIBLE SERVER-SIDE (proof, HytaleServer.jar bytecode): the popup is Player.notifyPickupItem(...) ->
        NotificationUtil.sendNotification(packetHandler, Message "server.general.pickedUpItem", null, item) and is sent ONLY when
        world.getGameplayConfig().getShowItemPickupNotifications() is true (GameplayConfig field `protected boolean
        showItemPickupNotifications`; World.getGameplayConfig = GameplayConfig.getAssetMap().getAsset(worldConfig.getGameplayConfig()), else
        GameplayConfig.DEFAULT). The pickup SOUND is played after that check, so it stays. PopupHide sets that field to false on every
        loaded GameplayConfig asset + DEFAULT (reflection; re-applied every 10 s, so a re-loaded asset is caught) and back to true when the
        switch goes off. Server-wide (the setting is per world gameplay config, not per player). Callers it silences: walking over an item
        (PlayerItemEntityPickupSystem), F-harvest / interactive pickups (ItemUtils), the builder pickup tool, barter shop purchases
        (BarterPage), objective item rewards (GiveItemsCompletion checks the same flag).
        Server Setup -> SkyyVoid and Crafting -> Auto-pickup -> "Hide the vanilla pickup popup" (pickup.hidePopup, default ON, live).
     2. OUR FEED CARD TEXT, vanilla-like: the vanilla popup shows just the item (icon + name); our card now shows the item name alone when
        it went where it should (the Void, or the inventory for a non-Void item), and a short note only when something needs you:
        "<name> - Void full, rest in inventory" / "<name> - inventory full, on the ground" (was "<name> > Void", "> Void + inventory",
        " - full, at your feet"). The card's frame, colours, icon and count ("  x12") are drawn by SkyyHud (feed:fn:push) - a deeper
        restyle of the card itself is a SkyyHud round (not this round's file).
  No saved-data change, no command change, no new bridge key written; one new class (PopupHide). The kit 1.7 Void and /craft pages are
  unchanged (the 0.8.15 harness NEW phase runs again on this jar).
ROLLBACK to 0.8.15: safe (saplings show in Farming again - same stored stacks; the switches vanish = everything into the Void; the vanilla
popup shows again after the next server start - the GameplayConfig field is only changed in memory).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.15.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.16.py"))
assert P.has('VERSION = "0.8.15"\n') and P.has('VoidHubOpen') and not P.has("PopupHide"), "not the live generated SkyySacks 0.8.15"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.16 = round small16"):].rstrip() + "\n"

# ================================================================================================ header, version
P.rep('''ROLLBACK to 0.8.14: safe (the old pages come back; SkyyMenu's stand-in Pocket tab returns when our tab is gone).
"""
''', '''ROLLBACK to 0.8.14: safe (the old pages come back; SkyyMenu's stand-in Pocket tab returns when our tab is gone).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.15"\n', 'VERSION = "0.8.16"\n')

# ================================================================================================ A1. saplings -> Foraging
P.rep('''PD_HOLDS = {"Mining": "ore, rubble, rock, soil and crystals",
            "Foraging": "logs, planks, sticks, fibre, bark and tree sap",''', '''PD_HOLDS = {"Mining": "ore, rubble, rock, soil and crystals",
            "Foraging": "logs, planks, sticks, fibre, bark, tree sap and saplings",   # 0.8.16: + saplings (Skyy "saplings in foraging")''')
P.rep('''  if (itemId.startsWith("Wood_") || itemId.equals("Ingredient_Stick") || itemId.equals("Ingredient_Fibre") || itemId.equals("Ingredient_Tree_Bark") || itemId.equals("@SAP@")) return "Foraging";
''', '''  if (itemId.startsWith("Wood_") || itemId.equals("Ingredient_Stick") || itemId.equals("Ingredient_Fibre") || itemId.equals("Ingredient_Tree_Bark") || itemId.equals("@SAP@")) return "Foraging";
  // 0.8.16 (Skyy "saplings in foraging where they belong"): the saplings leave Farming (stored stacks just show in Foraging now)
  if (itemId.startsWith("Plant_Sapling_")) return "Foraging";
''')

# ================================================================================================ A2. the per-player switches
P.rep('''defs.addMethod(CtNewMethod.make("""
public static String catOf(String itemId) {
  String c = homeOf(itemId);
  if (c != null && !COOKED_FARM && cooked(itemId)) return null;
  return c;
}""", defs))
''', '''defs.addMethod(CtNewMethod.make("""
public static String catOf(String itemId) {
  String c = homeOf(itemId);
  if (c != null && !COOKED_FARM && cooked(itemId)) return null;
  return c;
}""", defs))
# 0.8.16 (Skyy "add a toggle for each"): KEEPOUT = player uuid -> Integer (1 seeds stay out, 2 saplings stay out), written by
# SackPool.keepFlags on every 2 s tick (the /settings switches sacks.seedsVoid / sacks.saplingsVoid); absent = both go into the Void.
# intake(u, id) = where a NEW pickup / sweep item may go: catOf + the player's switches (null = it stays in the inventory)
defs.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap KEEPOUT = new java.util.concurrent.ConcurrentHashMap();", defs))
defs.addMethod(CtNewMethod.make("""
public static int keepKind(String itemId) {
  if (itemId == null) return 0;
  if (itemId.startsWith("Plant_Seeds_")) return 1;
  if (itemId.startsWith("Plant_Sapling_")) return 2;
  return 0;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static String intake(java.util.UUID u, String itemId) {
  String c = catOf(itemId);
  if (c == null || u == null) return c;
  int kd = keepKind(itemId);
  if (kd == 0) return c;
  Object f = KEEPOUT.get(u.toString());
  if (f instanceof Integer && (((Integer) f).intValue() & kd) != 0) return null;
  return c;
}""", defs))
''')
P.rep('''# profile:epoch:<uuid> as a long; -1 = absent (SkyyProfiles missing, or it has not published this player: contract 3 "Epoch").
''', '''# 0.8.16: the seeds / saplings switches of one player (settings:fn:get; no SkyyMenu = ON) -> SackDefs.KEEPOUT; returns the flags
sp.addMethod(CtNewMethod.make("""
public static int keepFlags(java.util.UUID u) {
  if (u == null) return 0;
  int f = (notifyOn(u, "sacks.seedsVoid") ? 0 : 1) | (notifyOn(u, "sacks.saplingsVoid") ? 0 : 2);
  if (f == 0) @PKG@.SackDefs.KEEPOUT.remove(u.toString());
  else @PKG@.SackDefs.KEEPOUT.put(u.toString(), Integer.valueOf(f));
  return f;
}""".replace("@PKG@", PKG), sp))
# profile:epoch:<uuid> as a long; -1 = absent (SkyyProfiles missing, or it has not published this player: contract 3 "Epoch").
''')
P.rep('''  sb.append(cfgSig());
  return sb.toString();''', '''  sb.append(@PKG@.SackPool.keepFlags(u)).append('|');   // 0.8.16: the seeds / saplings switches (a change re-sweeps)
  sb.append(cfgSig());
  return sb.toString();''')
# the sweep (2 s auto sweep + Deposit all) and every auto-pickup (PickGive.voidRoom: block / mob drops, harvests) ask intake
P.rep('''public static int sweep({PLA} p, String k, String onlyCat, boolean allContainers, java.util.HashMap swept, java.util.HashMap capsIn, java.util.HashMap heldIn) {{
  {INV} inv = p.getInventory();
  if (inv == null) return 0;
''', '''public static int sweep({PLA} p, String k, String onlyCat, boolean allContainers, java.util.HashMap swept, java.util.HashMap capsIn, java.util.HashMap heldIn) {{
  {INV} inv = p.getInventory();
  if (inv == null) return 0;
  java.util.UUID su = null;   // 0.8.16: the player's seeds / saplings switches (SackDefs.intake)
  try {{ su = p.getPlayerRef().getUuid(); }} catch (Throwable tu) {{ su = null; }}
''')
P.rep('''      String cat = {PKG}.SackDefs.catOf(id);
      if (cat == null) continue;
      if (!allContainers && c < 2''', '''      String cat = {PKG}.SackDefs.intake(su, id);   // 0.8.16: catOf + the seeds / saplings switches
      if (cat == null) continue;
      if (!allContainers && c < 2''')
P.rep('''  if (s.getItemId().startsWith("Skyy_Sack_") || !@PKG@.SweepTask.plainFresh(s)) return 0L;
  String cat = @PKG@.SackDefs.catOf(s.getItemId());''', '''  if (s.getItemId().startsWith("Skyy_Sack_") || !@PKG@.SweepTask.plainFresh(s)) return 0L;
  String cat = @PKG@.SackDefs.intake(u, s.getItemId());   // 0.8.16: seeds / saplings stay in the inventory when the player switched them off''')
P.rep('''  {PKG}.SackPool.regSetting("sacks.benchFuel", "Furnace out of fuel", "sacks", true, "Your Furnace ran out of fuel - once until you add more");
''', '''  {PKG}.SackPool.regSetting("sacks.benchFuel", "Furnace out of fuel", "sacks", true, "Your Furnace ran out of fuel - once until you add more");
  // 0.8.16 (Skyy "add a toggle for each. (seeds in farming. saplings in foraging where they belong. )"): ON = into the Void (as before)
  {PKG}.SackPool.regSetting("sacks.seedsVoid", "Seeds go into the Void", "sacks", true, "Off: seeds you pick up stay in your inventory for replanting (Farming)");
  {PKG}.SackPool.regSetting("sacks.saplingsVoid", "Saplings go into the Void", "sacks", true, "Off: saplings you pick up stay in your inventory for replanting (Foraging)");
''')

# ================================================================================================ B1. hide the vanilla pickup popup
P.rep('''scfg.addField(CtField.make("public static volatile int PICK_SHARE = 50;", scfg))
''', '''scfg.addField(CtField.make("public static volatile int PICK_SHARE = 50;", scfg))
# 0.8.16 (Skyy "hide it."): pickup.hidePopup - PopupHide switches the GameplayConfig showItemPickupNotifications flag off (live)
scfg.addField(CtField.make("public static volatile boolean HIDE_POPUP = true;", scfg))
''')
P.rep('''  boolean ch = first || on != PICK_ON || bl != PICK_BLOCKS || mo != PICK_MOBS || sh != PICK_SHARE;
''', '''  HIDE_POPUP = boolKey(p, "pickup.hidePopup", true);   // 0.8.16: PopupHide applies it on the next tick (hand edit + reload)
  boolean ch = first || on != PICK_ON || bl != PICK_BLOCKS || mo != PICK_MOBS || sh != PICK_SHARE;
''')
P.rep('''    "#pickup.killerShare=50",
''', '''    "#pickup.killerShare=50",
    "# Hide the vanilla pickup popup (true or false): the game's own 'picked up' popups are switched off for everyone (the Void feed",
    "# cards from SkyyHud show what you picked up; the pickup sound stays). false: the vanilla popups show as before.",
    "#pickup.hidePopup=true",
''')
P.rep('''    ("pickup.killerShare", "Killer's extra share", "pickup", "int", "50", "0", "100", "", "%", "live",
     "Top damager gets the full drop. A different killer gets this % of a second roll. 0 = none.",
     "field:SackCfg.PICK_SHARE@config.properties:pickup.killerShare"),
''', '''    ("pickup.killerShare", "Killer's extra share", "pickup", "int", "50", "0", "100", "", "%", "live",
     "Top damager gets the full drop. A different killer gets this % of a second roll. 0 = none.",
     "field:SackCfg.PICK_SHARE@config.properties:pickup.killerShare"),
    # 0.8.16 (Skyy "hide it."): live - the after= hook applies it at once, the 2 s tick keeps it applied
    ("pickup.hidePopup", "Hide the vanilla pickup popup", "pickup", "bool", "true", "", "", "", "", "live",
     "On: the game's own 'picked up' popups are hidden (the feed cards show pickups). Off: they show.",
     "field:SackCfg.HIDE_POPUP@config.properties:pickup.hidePopup;after=SackCfg.popupChanged"),
''')
GC = "com.hypixel.hytale.server.core.asset.type.gameplay.GameplayConfig"
P.rep('''# ================= SackTick (scheduler thread -> dispatch to world threads) =================
''', '''# ================= 0.8.16 PopupHide: the vanilla item pickup popup off (GameplayConfig.showItemPickupNotifications, see the docstring B1)
phd = pool.makeClass(PKG + ".PopupHide")
for _f in ("public static java.lang.reflect.Field F;", "public static final java.util.ArrayList FLIPPED = new java.util.ArrayList();",
           "public static volatile int LAST = -1;", "public static volatile int N = 0;", "public static volatile int COUNT = 0;",
           "public static volatile boolean WARNED = false;", "public static volatile String STATE = \\"not applied yet\\";"):
    phd.addField(CtField.make(_f, phd))
phd.addMethod(CtNewMethod.make(r\'\'\'
public static java.lang.reflect.Field field() throws Exception {
  if (F == null) {
    java.lang.reflect.Field f = @GC@.class.getDeclaredField("showItemPickupNotifications");
    f.setAccessible(true);
    F = f;
  }
  return F;
}\'\'\'.replace("@GC@", "@GCNAME@"), phd))
# every loaded GameplayConfig asset + DEFAULT; hide -> false (remembered), show -> the remembered ones back to true. Returns how many changed (-1 = failed)
phd.addMethod(CtNewMethod.make(r\'\'\'
public static synchronized int apply() {
  boolean hide = @PKG@.SackCfg.HIDE_POPUP;
  LAST = hide ? 1 : 0;
  try {
    java.lang.reflect.Field f = field();
    java.util.ArrayList all = new java.util.ArrayList();
    try {
      java.util.Map m = @GC@.getAssetMap().getAssetMap();
      if (m != null) all.addAll(m.values());
    } catch (Throwable t0) { }
    if (@GC@.DEFAULT != null) all.add(@GC@.DEFAULT);
    int n = 0;
    if (hide) {
      for (int i = 0; i < all.size(); i++) {
        Object g = all.get(i);
        if (g == null || !f.getBoolean(g)) continue;
        f.setBoolean(g, false);
        boolean seen = false;
        for (int j = 0; j < FLIPPED.size(); j++) if (FLIPPED.get(j) == g) seen = true;
        if (!seen) FLIPPED.add(g);
        n++;
      }
    } else {
      for (int j = 0; j < FLIPPED.size(); j++) {
        Object g = FLIPPED.get(j);
        if (g != null && !f.getBoolean(g)) { f.setBoolean(g, true); n++; }
      }
      FLIPPED.clear();
    }
    COUNT = all.size();
    STATE = (hide ? "hidden" : "shown") + " (" + all.size() + " gameplay configs)";
    if (n > 0 && @PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] vanilla item pickup popup " + (hide ? "HIDDEN" : "shown again") + " - " + n + " gameplay config(s) changed (Server Setup -> Auto-pickup -> Hide the vanilla pickup popup)");
    return n;
  } catch (Throwable t) {
    STATE = "FAILED (" + t + ")";
    if (!WARNED) { WARNED = true; @PKG@.SackPool.warn("could not switch the vanilla pickup popup (GameplayConfig.showItemPickupNotifications) - it keeps showing: " + t); }
    return -1;
  }
}\'\'\'.replace("@GC@", "@GCNAME@").replace("@PKG@", PKG), phd))
# the 2 s SackTick: at once when the switch changed, else every 10 s (an asset reload makes new GameplayConfig objects)
phd.addMethod(CtNewMethod.make(r\'\'\'
public static void tick() {
  int want = @PKG@.SackCfg.HIDE_POPUP ? 1 : 0;
  N = N + 1;
  if (want != LAST || N % 5 == 0) apply();
}\'\'\'.replace("@PKG@", PKG), phd))
# after= hook of the pickup.hidePopup row (the kit set SackCfg.HIDE_POPUP already)
scfg.addMethod(CtNewMethod.make(r\'\'\'
public static void popupChanged(String key) {
  @PKG@.PopupHide.apply();
}\'\'\'.replace("@PKG@", PKG), scfg))

# ================= SackTick (scheduler thread -> dispatch to world threads) =================
'''.replace("@GCNAME@", GC))
P.rep('''public void run() {{
  try {{
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      // 0.7.18 (audit 9b): only a player with something to do costs a world hop''', '''public void run() {{
  try {{ {PKG}.PopupHide.tick(); }} catch (Throwable tp) {{ }}   // 0.8.16: the vanilla pickup popup switch (B1)
  try {{
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      // 0.7.18 (audit 9b): only a player with something to do costs a world hop''')
P.rep('''          vho):   # 0.8.15: VoidHubOpen (HubBar is kit 1.7 now)
''', '''          vho,    # 0.8.15: VoidHubOpen (HubBar is kit 1.7 now)
          phd):   # 0.8.16: PopupHide
''')

# ================================================================================================ B2. the feed card text
P.rep('''public static String text(String nm, long[] r, int qty) {
  String t;
  if (r[2] > 0L) t = nm + " - full, at your feet";
  else if (r[0] >= (long) qty) t = nm + " > Void";
  else if (r[0] > 0L) t = nm + " > Void + inventory";
  else t = nm;''', '''public static String text(String nm, long[] r, int qty) {
  // 0.8.16 (Skyy "make our feed look more like the vanilla or better"): the item name alone, like the vanilla popup; a note only when
  // something needs the player (the Void category full, the inventory full)
  String t;
  if (r[2] > 0L) t = nm + " - inventory full, on the ground";
  else if (r[0] > 0L && r[0] < (long) qty) t = nm + " - Void full, rest in inventory";
  else t = nm;''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.16 adds no system / command"
P.finish()
