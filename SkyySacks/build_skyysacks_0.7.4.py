"""SkyySacks 0.7.4 - build script (javassist via jpype).
Run:   python build_skyysacks_0.7.4.py            -> SkyySacks/SkyySacks-0.7.4.jar
       python build_skyysacks_0.7.4.py --deploy   -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world
Fixes vs 0.1 (code review 2026-09-22): no item loss/dupe - sweep removes exactly `take` from the slot via
removeItemStackFromSlot(slot, qty) and only credits the pool when the transaction succeeded; withdraw only
debits what was really added (remainder respected); pool load is race-free; atomic file writes; disk I/O moved
off the world thread (dirty set + 10s saver); /sacks page is built inline (no .ui files, no underscores in IDs) with TextButtons + paging;
ticker cancelled on shutdown; failures logged. 0.1.4: self-test join grant removed (sweep + page verified in-game 2026-09-22).
0.7.0: craft tabs Crafting | Alchemy | Furnace | Tannery | Collections; Furnace/Tannery are timed processing queues with fuel,
offline progress and an output slot (Skyy_SkyySacks/processing/<uuid>.properties); BagMirror.sync idempotent (no double bag deduction).
0.7.2: per-profile storage (tools/PROFILES-CONTRACT.md): pools/<pkey>.properties, processing/<pkey>.properties, crafts.log lines
carry the pkey; pool/exemption/processing/BagMirror caches keyed by the pkey String; sweep, pages, bench link and processing resolve
the pkey once per run (a bench mirror keeps its key and is retired into its own pool on a switch); 6s settle window after a switch
(no sweep, page item moves refused); ProcTask checks profile:epoch:<uuid> every second (flush saves, log, notice on an open page).
Review fixes: the bench link uses settledKey and parks the mirror (bag materials off the open bench) while a switch settles; the craft
page never builds a mirror for an unsettled key; world-thread pool saves go through SackPool.saveSoon (SackSaver thread); PROFILE log
lines are queued (CraftLog.later) and written by the SackSaver.
Integration fixes (SkyyProfiles 0.1 semantics): settledKey also pauses item moves while profile:busy:<uuid> is set (crash recovery
at join), while SkyyProfiles is installed but published no epoch for the player (unreadable players file) and while the pool file
cannot be read (a failed read is no longer cached as an empty pool that the next save wrote over the file); absent epoch = baseline;
settle window 6s (covers the acc:has / coll:recipes republish); failed pool saves stay dirty; shutdown syncs open bench mirrors.
Derived by tools/sacks_0_7_2_patch.py. Without SkyyProfiles pkey = uuid = profile 1: same files, same behaviour.
0.7.3 (derived from 0.7.2 by tools/sacks_0_7_3_patch.py - edit the patch, not this file): craft tabs Crafting | Smithing | Farming |
Furnace | Tannery | Collections (no Alchemy tab); search box (TextField, Enter or Search, Clear; config craftSearch in
Skyy_SkyySacks/config.properties, re-read without a restart; /craft <words>); retired Alchemy/Cooking/Campfire bench accessories
unlock nothing and timed/table-only recipes never craft instantly (also on the Collections tab; Salvage stays instant - Skyy's
crafting layout lock); bench-aware bag mirror (the open
bench's ingredients fill the 36 slots first; the craft page does the same); Furnace units pay Smithing XP through skill:fn:craftxp
(ledger Furnace.xpDone, paid once the profile is settled); graded Skyy_Cook_* dishes pool into the Farming bag; the Furnace /
Tannery tab has a Refresh button instead of the ~2 s self-refresh (periodic page updates make PageManager drop clicks).
0.7.4 (derived from 0.7.3 by tools/sacks_0_7_4_patch.py - edit the patch, not this file): Campfire accessory tab (Skyy 2026-09-24:
the Campfire accessory is back as an emergency cook) - shown while acc:has lists Skyy_Accessory_Campfire_T<n>, after Farming; lists
exactly the Campfire-bench recipes whose output is in SkyyCooking's cook:campfire:ids (without SkyyCooking: every Campfire-bench
recipe, plain output, no XP); instant from inventory + bags like Crafting; each click calls cook:fn:campfire once after the materials
are removed and gives the id it returns instead of the primary output (null / missing / unknown item = plain output); SkyyCooking pays
the Cooking XP (x0.5) and grades the dish (x0.75 of the Cooking bonus); the tab does not report skill:fn:craftxp. The Campfire stays a
retired bench everywhere else (Crafting / Smithing / Farming / search / Collections keep no cooked food).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import json

VERSION = "0.7.4"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PAGE= "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
LIFE= "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime"
UCB = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
UEB = "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"
EVD = "com.hypixel.hytale.server.core.ui.builder.EventData"
BT  = "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType"
PRE = "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
MSG = "com.hypixel.hytale.server.core.Message"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
INV = "com.hypixel.hytale.server.core.inventory.Inventory"
IC  = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
IS  = "com.hypixel.hytale.server.core.inventory.ItemStack"
IST = "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction"
ISS = "com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction"
LOG = "com.hypixel.hytale.logger.HytaleLogger"
MCW = "com.hypixel.hytale.server.core.entity.entities.player.windows.MaterialContainerWindow"
MERS= "com.hypixel.hytale.server.core.entity.entities.player.windows.MaterialExtraResourcesSection"
WIN = "com.hypixel.hytale.server.core.entity.entities.player.windows.Window"
WM  = "com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager"
SIC = "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"
CIC = "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer"
IQ  = "com.hypixel.hytale.protocol.ItemQuantity"
CRP = "com.hypixel.hytale.builtin.crafting.CraftingPlugin"
CRM = "com.hypixel.hytale.builtin.crafting.component.CraftingManager"
CRR = "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe"
FCC = "com.hypixel.hytale.server.core.asset.type.item.config.FieldcraftCategory"
MQ  = "com.hypixel.hytale.server.core.inventory.MaterialQuantity"
BRQ = "com.hypixel.hytale.protocol.BenchRequirement"
OPT = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"
OCU = "com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction"
PB  = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.ProcessingBench"
PEO = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.ProcessingBench$ExtraOutput"
BEN = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.Bench"
BTL = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.BenchTierLevel"
BLT = "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType"
ITM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
IRT = "com.hypixel.hytale.protocol.ItemResourceType"
PGM = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"
# 0.7.3
AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
BWN = "com.hypixel.hytale.server.core.entity.entities.player.windows.BlockWindow"
BUR = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.BenchUpgradeRequirement"
BTP = "com.hypixel.hytale.protocol.BenchType"
# 0.7.4: the creative flag passed to cook:fn:campfire (SkyyCooking 0.1.1 reads the same enum)
GM  = "com.hypixel.hytale.protocol.GameMode"

for c, m in ((PLA, "getInventory"), (INV, "getStorage"), (IC, "getItemStack"), (IC, "removeItemStackFromSlot"), (IC, "addItemStack"),
             (IS, "getItemId"), (IS, "getQuantity"), (WLD, "execute"), (IST, "getRemainder"), (ISS, "succeeded"), (EVD, "of"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"), (OCU, "registerSimple"), (CRP, "getAvailableRecipesForCategory"),
             (CRM, "getInputMaterials"), (CRR, "getInput"), (FCC, "getAssetMap"), (IC, "countRemovableMaterial"), (IC, "removeMaterials"), (INV, "getCombinedBackpackStorageHotbar"), (SIC, "addOrDropItemStack")):
    B.probe(pool, c, m)
for c, m in ((CRR, "getTimeSeconds"), (PB, "getExtraOutput"), (PB, "getFuel"), (BEN, "getTierLevel"), (BTL, "getCraftingTimeReductionModifier"),
             (BLT, "getBench"), (ITM, "getFuelQuality"), (ITM, "getResourceTypes"), (PEO, "isIgnoredFuelSource"), (PEO, "getPerFuelItemsConsumed"),
             (PAGE, "sendUpdate"), (PGM, "getCustomPage"), (UCB, "set"), (IC, "getCapacity"), (IC, "getMatchingResourceType"),
             (MQ, "isItemExcluded"), (MQ, "getResourceTypeId")):
    B.probe(pool, c, m)
# 0.7.3: bench-aware mirror, Processing check, search box (Validating + "@SearchQuery" event data), /craft <words>
for c, m in ((CRP, "getBenchRecipes"), (BWN, "getBlockType"), (BEN, "getUpgradeRequirement"), (BUR, "getInput"), (BRQ, "type"),
             (BTP, "Processing"), (BT, "Validating"), (EVD, "append"), (UEB, "addEventBinding"), (AC, "setAllowsExtraArguments"),
             (CTX, "getInputString"), (UCB, "set"), (MQ, "getItemId")):
    B.probe(pool, c, m)
# 0.7.4: Campfire tab (creative flag for cook:fn:campfire, primary output swap)
for c, m in ((PLA, "getGameMode"), (GM, "Creative"), (CRR, "getOutputs"), (CRR, "getPrimaryOutput"), (CRR, "getBenchRequirement")):
    B.probe(pool, c, m)

PKG = "com.skyy.sacks"
defs = pool.makeClass(PKG + ".SackDefs")
sp   = pool.makeClass(PKG + ".SackPool")
swp  = pool.makeClass(PKG + ".SweepTask")
tick = pool.makeClass(PKG + ".SackTick")
sav  = pool.makeClass(PKG + ".SackSaver")
cmp  = pool.makeClass(PKG + ".CountCmp")
page = pool.makeClass(PKG + ".SacksPage", pool.get(PAGE))
cmd  = pool.makeClass(PKG + ".SacksCmd", pool.get(APC))
grt  = pool.makeClass(PKG + ".GrantTask")
srd  = pool.makeClass(PKG + ".SackReady")
fac  = pool.makeClass(PKG + ".SacksPageFactory")
mir  = pool.makeClass(PKG + ".BagMirror")
clt  = pool.makeClass(PKG + ".CraftLinkTask")
ctk  = pool.makeClass(PKG + ".CraftTick")
clog = pool.makeClass(PKG + ".CraftLog")
rcmp = pool.makeClass(PKG + ".RecipeCmp")
cpg  = pool.makeClass(PKG + ".CraftPage", pool.get(PAGE))
ccmd = pool.makeClass(PKG + ".CraftCmd", pool.get(APC))
pjob = pool.makeClass(PKG + ".ProcJob")
pben = pool.makeClass(PKG + ".ProcBench")
pst  = pool.makeClass(PKG + ".ProcStore")
ptk  = pool.makeClass(PKG + ".ProcTask")
ptick= pool.makeClass(PKG + ".ProcTick")
cfac = pool.makeClass(PKG + ".CraftPageFactory")
scfg = pool.makeClass(PKG + ".SackCfg")
pl   = pool.makeClass(PKG + ".SkyySacksPlugin", pool.get(JP))

# ================= SackDefs =================
defs.addField(CtField.make('public static final String[] CATS = new String[] { "Mining", "Foraging", "Farming", "Combat" };', defs))
defs.addMethod(CtNewMethod.make("""
public static String catOf(String itemId) {
  if (itemId == null) return null;
  if (itemId.startsWith("Skyy_Sack_")) return null;
  // 0.7.3 (research/Cooking-Skill-Spec.md 3.4): graded dishes (the Grade is in the id, no metadata) go to the Farming bag; the
  // Skyy_Cook_Recipe_* recipe-variant items never do. A cook:prefix bridge value (SkyyCooking) is honoured when it starts with Skyy_Cook.
  if (itemId.startsWith("Skyy_")) {
    if (itemId.startsWith("Skyy_Cook_Recipe_")) return null;
    if (itemId.startsWith("Skyy_Cook_")) return "Farming";
    try {
      Object b = System.getProperties().get("skyy.bridge");
      Object p = (b instanceof java.util.Map) ? ((java.util.Map) b).get("cook:prefix") : null;
      if (p instanceof String && ((String) p).startsWith("Skyy_Cook") && itemId.startsWith((String) p)) return "Farming";
    } catch (Throwable t) { }
    return null;
  }
  if (itemId.startsWith("Ore_") || itemId.startsWith("Rubble_") || itemId.startsWith("Rock_") || itemId.startsWith("Soil_")) return "Mining";
  if (itemId.startsWith("Wood_") || itemId.equals("Ingredient_Stick") || itemId.equals("Ingredient_Fibre") || itemId.equals("Ingredient_Tree_Bark")) return "Foraging";
  if (itemId.startsWith("Plant_") || itemId.startsWith("Food_") || itemId.startsWith("Fish_")) return "Farming";
  if (itemId.startsWith("Ingredient_Life_Essence") || itemId.equals("Ingredient_Poop")) return "Farming";
  if (itemId.startsWith("Ingredient_Bone") || itemId.startsWith("Ingredient_Hide_") || itemId.startsWith("Ingredient_Chitin")
      || itemId.startsWith("Ingredient_Sac_") || itemId.startsWith("Ingredient_Feathers") || itemId.startsWith("Ingredient_Fabric_Scrap_")
      || itemId.equals("Ingredient_Voidheart") || itemId.equals("Ingredient_Powder_Boom")
      || (itemId.startsWith("Ingredient_") && itemId.endsWith("_Essence"))) return "Combat";
  return null;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static int tierCap(String tier) {
  if (tier.equals("Small")) return 640;
  if (tier.equals("Medium")) return 2240;
  if (tier.equals("Large")) return 20160;
  return 0;
}""", defs))

# ================= SackPool =================
sp.addField(CtField.make("public static java.nio.file.Path DIR;", sp))
sp.addField(CtField.make(f"public static {LOG} LOG;", sp))
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap POOLS = new java.util.concurrent.ConcurrentHashMap();", sp))
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();", sp))
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap EXEMPT = new java.util.concurrent.ConcurrentHashMap();", sp))
sp.addField(CtField.make("public static final Object SAVELOCK = new Object();", sp))
# integration fix: 6 s, not 3 - the switch is one world-thread task, but acc:has / coll:recipes follow the new profile only on
# the next SkyyAccessories / SkyyCollections republish (up to their 5 s ticks); craft clicks wait until those are current.
sp.addField(CtField.make("public static final long SETTLE_MS = 6000L;", sp))
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEENEPOCH = new java.util.concurrent.ConcurrentHashMap();", sp))
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEENKEY = new java.util.concurrent.ConcurrentHashMap();", sp))
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CHANGEDAT = new java.util.concurrent.ConcurrentHashMap();", sp))
# integration fix: pool keys whose file could not be read (key -> time of the last failed read; never cached as an empty pool) and
# players whose profile state is unknown (SkyyProfiles installed, no profile:epoch published) - both only for warn-once + retry pacing.
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BADPOOL = new java.util.concurrent.ConcurrentHashMap();", sp))
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap UNKNOWN = new java.util.concurrent.ConcurrentHashMap();", sp))
# 0.7.2 profile contract (tools/PROFILES-CONTRACT.md): bridge + pkey helper exactly as the contract gives it. Without SkyyProfiles
# pkey(u) = u.toString() = profile 1 (the pre-0.7.2 file names). Per-player bridge values we READ (acc:has, coll:recipes) stay keyed by UUID.
sp.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  Object b = System.getProperties().get("skyy.bridge");
  if (b instanceof java.util.Map) return (java.util.Map) b;
  return java.util.Collections.EMPTY_MAP;
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""", sp))
# profile:epoch:<uuid> as a long; -1 = absent (SkyyProfiles missing, or it has not published this player: contract 3 "Epoch").
# An absent epoch carries no information - going from or to -1 is never treated as a profile change (contract 4.2).
sp.addMethod(CtNewMethod.make("""
public static long epoch(java.util.UUID u) {
  try {
    Object e = bridge().get("profile:epoch:" + u.toString());
    if (e instanceof Number) return ((Number) e).longValue();
    if (e != null) return Long.parseLong(String.valueOf(e).trim());
  } catch (Throwable t) { }
  return -1L;
}""", sp))
# settledKey(u) is added below pool() (it needs ready(k)); see "integration fixes" further down.
sp.addMethod(CtNewMethod.make("""
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
sp.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyySacks] " + msg); } catch (Throwable t) { }
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static java.util.Map pool(String k) {
  java.util.Map m = (java.util.Map) POOLS.get(k);
  if (m != null) return m;
  m = new java.util.concurrent.ConcurrentHashMap();
  try {
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
      java.util.Enumeration en = p.propertyNames();
      while (en.hasMoreElements()) {
        String k = (String) en.nextElement();
        try { long v = Long.parseLong(p.getProperty(k).trim()); if (v > 0L) m.put(k, Long.valueOf(v)); } catch (Throwable t) { }
      }
    }
  } catch (Throwable t) {
    java.util.Map again = (java.util.Map) POOLS.get(k);
    if (again != null) return again;
    if (BADPOOL.put(k, Long.valueOf(System.currentTimeMillis())) == null) warn("could not load pool for " + k + " - file left untouched, item moves for this profile paused until it reads (retry every 2s): " + t);
    return m;
  }
  if (BADPOOL.remove(k) != null) warn("pool for " + k + " reads again - item moves resumed");
  java.util.Map prev = (java.util.Map) POOLS.putIfAbsent(k, m);
  return prev != null ? prev : m;
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static void saveNow(String k) {
  try {
    java.util.Map m = (java.util.Map) POOLS.get(k);
    if (m == null) return;
    java.util.Properties p = new java.util.Properties();
    java.util.Iterator it = m.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      p.setProperty((String) e.getKey(), String.valueOf(((Long) e.getValue()).longValue()));
    }
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyySacks pool"); } finally { out.close(); }
    java.nio.file.Files.move(tmp, DIR.resolve(k + ".properties"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  } catch (Throwable t) { DIRTY.put(k, Boolean.TRUE); warn("could not save pool for " + k + " (kept dirty - retried by the next save): " + t); }
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static void save(String k) {
  synchronized (SAVELOCK) { saveNow(k); }
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static void flushDirty() {
  java.util.ArrayList ks = new java.util.ArrayList(DIRTY.keySet());
  for (int i = 0; i < ks.size(); i++) {
    String k = (String) ks.get(i);
    DIRTY.remove(k);
    save(k);
  }
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static long get(String k, String item) {
  Long v = (Long) pool(k).get(item);
  return v == null ? 0L : v.longValue();
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static synchronized void add(String k, String item, long n) {
  java.util.Map m = pool(k);
  Long v = (Long) m.get(item);
  long nv = (v == null ? 0L : v.longValue()) + n;
  if (nv <= 0L) m.remove(item); else m.put(item, Long.valueOf(nv));
  DIRTY.put(k, Boolean.TRUE);
}""", sp))
sp.addMethod(CtNewMethod.make(f"""
public static long catTotal(String k, String cat) {{
  long t = 0L;
  java.util.Iterator it = pool(k).entrySet().iterator();
  while (it.hasNext()) {{
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (cat.equals({PKG}.SackDefs.catOf((String) e.getKey()))) t += ((Long) e.getValue()).longValue();
  }}
  return t;
}}""", sp))

# integration fix: true when the pool of key k is loaded (or its file does not exist yet). A pool whose file could not be read is
# retried at most every 2 s; until it reads, settledKey pauses every item move for that key (nothing can be written over the file).
sp.addMethod(CtNewMethod.make("""
public static boolean ready(String k) {
  if (k == null) return false;
  if (POOLS.containsKey(k)) return true;
  Long bad = (Long) BADPOOL.get(k);
  if (bad != null && System.currentTimeMillis() - bad.longValue() < 2000L) return false;
  pool(k);
  return POOLS.containsKey(k);
}""", sp))
# The ONE gate of every item move between the live inventory and a pool (sweep, Sacks page clicks, craft/processing clicks, bench
# link): the active key, or null = paused (sweep skips, clicks are refused, the bench mirror is parked). Paused while:
#  - SkyyProfiles is installed (profile:fn:key) but published no profile:epoch:<uuid> for this player: unreadable players file with no
#    good copy, where the Function falls back to profile 1 while the live inventory may be profile N (contract 4.4 / 5);
#  - SETTLE_MS after the epoch or the key changed (baseline = first value seen; absent epochs are no change, contract 4.2) - the other
#    mods republish acc:has / coll:recipes for the new profile in that time;
#  - profile:busy:<uuid> is present (contract 4.5): a crash recovery is pending at join and will reload the inventory from a snapshot,
#    so a sweep before it would duplicate items (a switch sets it too, but inside one world-thread task we never run in);
#  - the pool file of the key cannot be read (ready).
# Without SkyyProfiles: no epoch, no busy flag, key = uuid - only the pool-file check applies.
sp.addMethod(CtNewMethod.make("""
public static String settledKey(java.util.UUID u) {
  if (u == null) return null;
  java.util.Map b = bridge();
  long e = epoch(u);
  String k = pkey(u);
  if (e < 0L && (b.get("profile:fn:key") instanceof java.util.function.Function)) {
    if (UNKNOWN.putIfAbsent(u, Boolean.TRUE) == null) warn("SkyyProfiles is installed but published no profile:epoch for " + u + " (unreadable players file, or SkyyProfiles failed to start) - bag item moves paused for this player until it does");
    return null;
  }
  if (UNKNOWN.remove(u) != null) warn("profile state of " + u + " is known again - bag item moves resumed");
  Long le = (Long) SEENEPOCH.put(u, Long.valueOf(e));
  String lk = (String) SEENKEY.put(u, k);
  long now = System.currentTimeMillis();
  boolean moved = le != null && le.longValue() >= 0L && e >= 0L && le.longValue() != e;
  if (moved || (lk != null && !lk.equals(k))) CHANGEDAT.put(u, Long.valueOf(now));
  Long t = (Long) CHANGEDAT.get(u);
  if (t != null) {
    if (now - t.longValue() < SETTLE_MS) return null;
    CHANGEDAT.remove(u);
  }
  if (b.get("profile:busy:" + u.toString()) != null) return null;
  if (!ready(k)) return null;
  return k;
}""", sp))

# ================= SackCfg (0.7.3): Skyy_SkyySacks/config.properties - read at setup, re-read by the SackSaver when the file changes =================
# craftSearch=false removes the inline TextField from the craft page without a rebuild (in case it does not parse on a client).
scfg.addField(CtField.make("public static java.nio.file.Path FILE;", scfg))
scfg.addField(CtField.make("public static long MTIME = -1L;", scfg))
scfg.addField(CtField.make("public static boolean WARNED = false;", scfg))
scfg.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicBoolean SEARCH = new java.util.concurrent.atomic.AtomicBoolean(true);", scfg))
scfg.addMethod(CtNewMethod.make("""
public static synchronized void reload() {
  try {
    if (FILE == null) return;
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
      String nl = System.lineSeparator();
      String txt = "# SkyySacks settings - re-read about every 10 seconds when this file changes (no restart and no rebuild needed)." + nl
        + "# craftSearch=false removes the search box from the /craft page (use it if the craft page stops opening on your client)." + nl
        + "# /craft followed by words still searches when the box is off." + nl
        + "craftSearch=true" + nl;
      // review fix: tmp + fsync + atomic rename (ProcStore.save pattern), so a crash mid-write never leaves a truncated config.properties
      java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp");
      java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
      try { out.write(txt.getBytes("UTF-8")); out.flush(); out.getFD().sync(); } finally { out.close(); }
      try { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }); }
      catch (Throwable am) { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
    }
    long mt = java.nio.file.Files.getLastModifiedTime(FILE, new java.nio.file.LinkOption[0]).toMillis();
    if (mt == MTIME) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    boolean on = !"false".equalsIgnoreCase(p.getProperty("craftSearch", "true").trim());
    boolean first = MTIME < 0L;
    MTIME = mt;
    WARNED = false;
    if (first || on != SEARCH.get()) {
      try { if (com.skyy.sacks.SackPool.LOG != null) com.skyy.sacks.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: craft page search box " + (on ? "ON" : "OFF") + " (" + FILE + ")"); } catch (Throwable t2) { }
    }
    SEARCH.set(on);
  } catch (Throwable t) {
    if (!WARNED) { WARNED = true; com.skyy.sacks.SackPool.warn("could not read " + FILE + " - keeping craftSearch=" + SEARCH.get() + ": " + t); }
  }
}""", scfg))

# ================= Processing (0.7.0): timed Furnace / Tannery queues - our own per-player state, no block entity =================
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
# 0.7.3 Smithing: paid Furnace units per recipe not yet reported through skill:fn:craftxp (persisted as <bench>.xpDone)
pben.addField(CtField.make("public java.util.LinkedHashMap xpDone;", pben))
pben.addField(CtField.make("public static final int XP_CAP = 10000;", pben))
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
  this.xpDone = new java.util.LinkedHashMap();
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
  // 0.7.3 Smithing (research/Smithing-Smelting-Spec.md 4.1): only a PAID Furnace unit counts - never the no-output fallback,
  // burnOne (charcoal), cancel() or unloadFuel(); ProcTask.drainXp reports it once the profile is settled
  else if ("Furnace".equalsIgnoreCase(this.bench)) {{
    Integer cx = (Integer) this.xpDone.get(j.recipe);
    if (cx == null || cx.intValue() < XP_CAP) addTo(this.xpDone, j.recipe, 1);
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
pben.addMethod(CtNewMethod.make("""
public synchronized java.util.ArrayList xpList() {
  java.util.ArrayList l = new java.util.ArrayList();
  java.util.Iterator it = this.xpDone.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    l.add(new Object[] { e.getKey(), e.getValue() });
  }
  return l;
}""", pben))
pben.addMethod(CtNewMethod.make("""
public synchronized void takeXp(String id, int n) {
  if (id == null || n <= 0) return;
  Integer cur = (Integer) this.xpDone.get(id);
  if (cur == null) return;
  int v = cur.intValue() - n;
  if (v <= 0) this.xpDone.remove(id); else this.xpDone.put(id, Integer.valueOf(v));
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
  p.setProperty(b + "xpDone", ser(this.xpDone));
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
  this.xpDone.clear(); parseInto(this.xpDone, p.getProperty(b + "xpDone"), 1);
  java.util.Iterator xi = new java.util.ArrayList(this.xpDone.keySet()).iterator();
  while (xi.hasNext()) {{ Object xk = xi.next(); if (((Integer) this.xpDone.get(xk)).intValue() > XP_CAP) this.xpDone.put(xk, Integer.valueOf(XP_CAP)); }}
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

# ProcStore = per-profile benches (0.7.2: keyed by pkey), persisted in Skyy_SkyySacks/processing/<pkey>.properties (tmp + fsync + atomic move)
pst.addField(CtField.make("public static java.nio.file.Path DIR;", pst))
pst.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap STATES = new java.util.concurrent.ConcurrentHashMap();", pst))
pst.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();", pst))
pst.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BROKEN = new java.util.concurrent.ConcurrentHashMap();", pst))
pst.addField(CtField.make('public static final String[] BENCHES = new String[] { "Furnace", "Tannery" };', pst))
pst.addMethod(CtNewMethod.make(f"""
public static synchronized java.util.Map load(String k) {{
  java.util.Map m = (java.util.Map) STATES.get(k);
  if (m != null) return m;
  m = new java.util.concurrent.ConcurrentHashMap();
  java.nio.file.Path f = DIR == null ? null : DIR.resolve(k + ".properties");
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
    BROKEN.put(k, Boolean.TRUE);
    {PKG}.SackPool.warn("processing: could not read " + f + " - left untouched, furnace/tannery disabled for " + k + " until restart: " + t);
  }}
  STATES.put(k, m);
  return m;
}}""", pst))
pst.addMethod(CtNewMethod.make(f"""
public static java.util.Map all(String k) {{
  java.util.Map m = (java.util.Map) STATES.get(k);
  return m != null ? m : load(k);
}}""", pst))
pst.addMethod(CtNewMethod.make(f"""
public static {PKG}.ProcBench get(String k, String bench) {{
  if (k == null || bench == null) return null;
  return ({PKG}.ProcBench) all(k).get(bench);
}}""", pst))
pst.addMethod(CtNewMethod.make(f"""
public static {PKG}.ProcBench of(String k, String bench) {{
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) all(k);
  {PKG}.ProcBench pb = ({PKG}.ProcBench) m.get(bench);
  if (pb != null) return pb;
  pb = new {PKG}.ProcBench(bench);
  pb.clock = System.currentTimeMillis();
  Object prev = m.putIfAbsent(bench, pb);
  return prev != null ? ({PKG}.ProcBench) prev : pb;
}}""", pst))
pst.addMethod(CtNewMethod.make(f"""
public static boolean pending(String k, String bench) {{
  {PKG}.ProcBench pb = get(k, bench);
  return pb != null && pb.pending();
}}""", pst))
pst.addMethod(CtNewMethod.make("""
public static void markDirty(String k) { DIRTY.put(k, Boolean.TRUE); }""", pst))
pst.addMethod(CtNewMethod.make(f"""
public static synchronized boolean save(String k) {{
  if (k == null || DIR == null || BROKEN.containsKey(k)) return false;
  java.util.Map m = (java.util.Map) STATES.get(k);
  if (m == null) return false;
  DIRTY.remove(k);
  try {{
    java.util.Properties p = new java.util.Properties();
    p.setProperty("version", "1");
    java.util.Iterator it = m.values().iterator();
    while (it.hasNext()) {{ {PKG}.ProcBench pb = ({PKG}.ProcBench) it.next(); pb.toProps(p); }}
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
    java.nio.file.Path dst = DIR.resolve(k + ".properties");
    java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
    try {{ p.store(out, "SkyySacks processing - Furnace/Tannery queues, fuel and output slots"); out.flush(); out.getFD().sync(); }} finally {{ out.close(); }}
    try {{ java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] {{ java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }}); }}
    catch (Throwable am) {{ java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] {{ java.nio.file.StandardCopyOption.REPLACE_EXISTING }}); }}
    return true;
  }} catch (Throwable t) {{
    DIRTY.put(k, Boolean.TRUE);
    {PKG}.SackPool.warn("processing: could not save " + k + ": " + t);
    return false;
  }}
}}""", pst))
pst.addMethod(CtNewMethod.make("""
public static void flushDirty() {
  java.util.ArrayList ks = new java.util.ArrayList(DIRTY.keySet());
  for (int i = 0; i < ks.size(); i++) save((String) ks.get(i));
}""", pst))

# ================= SweepTask (runs ON world thread; no disk I/O) =================
swp.addInterface(pool.get("java.lang.Runnable"))
swp.addField(CtField.make(f"public {PR} pr;", swp))
swp.addField(CtField.make("public java.util.UUID expectedWorld;", swp))
swp.addConstructor(CtNewConstructor.make(f"public SweepTask({PR} pr, java.util.UUID w) {{ this.pr = pr; this.expectedWorld = w; }}", swp))
# capacity per category = sum of sack tiers carried anywhere (storage + hotbar + backpack)
swp.addMethod(CtNewMethod.make(f"""
public static java.util.HashMap caps({INV} inv) {{
  java.util.HashMap caps = new java.util.HashMap();
  {IC}[] scan = new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }};
  for (int c = 0; c < scan.length; c++) {{
    {IC} cont = scan[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {{
      {IS} it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if (id != null && id.startsWith("Skyy_Sack_")) {{
        String[] parts = id.split("_");
        if (parts.length >= 4) {{
          String cat = parts[2]; String tier = parts[3];
          Integer cur = (Integer) caps.get(cat);
          int tc = {PKG}.SackDefs.tierCap(tier);
          if (cur == null || cur.intValue() < tc) caps.put(cat, Integer.valueOf(tc));
        }}
      }}
    }}
  }}
  return caps;
}}""", swp))
# sweep matching items into the pool. onlyCat == null -> every category; allContainers -> hotbar + backpack too. Returns items moved.
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
# withdraw up to n of an item into STORAGE; returns how many actually left the pool
swp.addMethod(CtNewMethod.make(f"""
public static int withdraw({PLA} p, String k, String id, int n) {{
  long have = {PKG}.SackPool.get(k, id);
  if (have <= 0L || n <= 0) return 0;
  String cat = {PKG}.SackDefs.catOf(id);
  if (cat == null || !caps(p.getInventory()).containsKey(cat)) return 0;
  int take = (long) n < have ? n : (int) have;
  {IST} tx = p.getInventory().getStorage().addItemStack(new {IS}(id, take));
  {IS} rem = tx == null ? null : tx.getRemainder();
  int added = (tx == null || !tx.succeeded()) ? 0 : take - (rem == null ? 0 : rem.getQuantity());
  if (added > 0) {{ {PKG}.SackPool.add(k, id, -(long) added); {PKG}.SackPool.exempt(k, id, 600000L); }}
  return added;
}}""", swp))
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
    sweep(p, k, null, false);
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("sweep failed: " + t); }}
}}""", swp))

# ================= SackTick (scheduler thread -> dispatch to world threads) =================
tick.addInterface(pool.get("java.lang.Runnable"))
tick.addConstructor(CtNewConstructor.make("public SackTick() { }", tick))
tick.addMethod(CtNewMethod.make(f"""
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
      w.execute(new {PKG}.SweepTask(pr, wu));
    }}
  }} catch (Throwable t) {{ }}
}}""", tick))

sav.addInterface(pool.get("java.lang.Runnable"))
sav.addConstructor(CtNewConstructor.make("public SackSaver() { }", sav))

cmp.addInterface(pool.get("java.util.Comparator"))
cmp.addConstructor(CtNewConstructor.make("public CountCmp() { }", cmp))
cmp.addMethod(CtNewMethod.make("""
public int compare(Object a, Object b) {
  long x = ((Long) ((java.util.Map.Entry) a).getValue()).longValue();
  long y = ((Long) ((java.util.Map.Entry) b).getValue()).longValue();
  if (x != y) return x > y ? -1 : 1;
  return ((String) ((java.util.Map.Entry) a).getKey()).compareTo((String) ((java.util.Map.Entry) b).getKey());
}""", cmp))

# ================= RecipeCmp: craftable first, then material progression, then name =================
rcmp.addInterface(pool.get("java.util.Comparator"))
rcmp.addConstructor(CtNewConstructor.make("public RecipeCmp() { }", rcmp))
rcmp.addMethod(CtNewMethod.make("""
public static int tierOf(String id) {
  if (id == null) return 0;
  String[] m = new String[] { "Crude", "Copper", "Bronze", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium" };
  for (int i = m.length - 1; i >= 0; i--) if (id.indexOf(m[i]) >= 0) return i;
  return 0;
}""", rcmp))
rcmp.addMethod(CtNewMethod.make("""
public int compare(Object a, Object b) {
  Object[] x = (Object[]) a; Object[] y = (Object[]) b;
  boolean cx = ((Integer) x[1]).intValue() > 0; boolean cy = ((Integer) y[1]).intValue() > 0;
  if (cx != cy) return cx ? -1 : 1;
  int tx = ((Integer) x[2]).intValue(); int ty = ((Integer) y[2]).intValue();
  if (tx != ty) return tx < ty ? -1 : 1;
  return ((String) x[3]).compareTo((String) y[3]);
}""", rcmp))

# ================= CraftLog (append-only audit of every craft-page craft) =================
clog.addField(CtField.make("public static java.nio.file.Path FILE;", clog))
clog.addMethod(CtNewMethod.make("""
public static synchronized void write(String k, String recipe, int requested, int done, boolean flag, int given, String audit) {
  try {
    if (FILE == null) return;
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    String line = new java.util.Date().toString() + " " + k + " " + recipe + " requested=" + requested + " done=" + done + " flag=" + flag + " given=" + given + audit + System.lineSeparator();
    java.nio.file.Files.write(FILE, line.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { }
}""", clog))
clog.addMethod(CtNewMethod.make("""
public static synchronized void line(String k, String text) {
  try {
    if (FILE == null) return;
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    String l = new java.util.Date().toString() + " " + k + " " + text + System.lineSeparator();
    java.nio.file.Files.write(FILE, l.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { }
}""", clog))

# 0.7.2 review fix: log lines from world-thread hot paths (a profile switch, a retired or parked bench mirror) are queued here
# (timestamped when queued) and written by the SackSaver on the scheduler thread - no file append inside a world-thread task.
clog.addField(CtField.make("public static final java.util.concurrent.ConcurrentLinkedQueue PENDING = new java.util.concurrent.ConcurrentLinkedQueue();", clog))
clog.addMethod(CtNewMethod.make("""
public static void later(String k, String text) {
  PENDING.offer(new java.util.Date().toString() + " " + k + " " + text + System.lineSeparator());
}""", clog))
clog.addMethod(CtNewMethod.make("""
public static synchronized void drain() {
  try {
    Object o = PENDING.poll();
    if (o == null) return;
    StringBuilder sb = new StringBuilder();
    while (o != null) { sb.append((String) o); o = PENDING.poll(); }
    if (FILE == null) return;
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(FILE, sb.toString().getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { }
}""", clog))
# SackSaver.run() (constructor added above): processing files, pool files, then the queued log lines - all on the scheduler thread.
sav.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{ {PKG}.ProcStore.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackPool.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CraftLog.drain(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackCfg.reload(); }} catch (Throwable t) {{ }}
}}""", sav))
# 0.7.2 review fix: pool saves from world-thread code (Sacks page clicks, bench link, instant craft, mirror retire/park) mark the
# key dirty and run the SackSaver on the scheduler thread right away (same pattern as CraftPage.saveSoon for processing); only
# when the scheduler refuses the task (server shutting down) is it run inline.
sp.addMethod(CtNewMethod.make(f"""
public static void saveSoon(String k) {{
  if (k != null) DIRTY.put(k, Boolean.TRUE);
  try {{ {HSV}.SCHEDULED_EXECUTOR.execute(new {PKG}.SackSaver()); }}
  catch (Throwable t) {{ new {PKG}.SackSaver().run(); }}
}}""", sp))

# CraftPage fields + constructor first (SacksPage references it)
cpg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap ONLY = new java.util.concurrent.ConcurrentHashMap();", cpg))
cpg.addField(CtField.make("public String tab;", cpg))
cpg.addField(CtField.make("public int pageNo;", cpg))
cpg.addField(CtField.make("public String info;", cpg))
cpg.addField(CtField.make("public java.util.ArrayList rows;", cpg))
cpg.addField(CtField.make("public java.util.ArrayList tabs;", cpg))
cpg.addField(CtField.make("public String[] fuelIds;", cpg))
cpg.addField(CtField.make("public String key;", cpg))
cpg.addField(CtField.make("public String noticeKey;", cpg))
cpg.addField(CtField.make("public boolean settling;", cpg))
# 0.7.3: the active search ("" = none); lives only on this page instance
cpg.addField(CtField.make("public String query;", cpg))
cpg.addField(CtField.make("public static java.util.HashSet BENCHIDS;", cpg))
cpg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap ACCWARN = new java.util.concurrent.ConcurrentHashMap();", cpg))
cpg.addConstructor(CtNewConstructor.make(f"""
public CraftPage({PR} pr, String tab) {{
  super(pr, {LIFE}.CanDismiss);
  this.tab = tab; this.pageNo = 0; this.info = ""; this.query = "";
}}""", cpg))

# ================= SacksPage (SkyBlock-style: tabs, capacity, 9x4 icon grid, pick up all / deposit all) =================
page.addField(CtField.make("public String cat;", page))
page.addField(CtField.make("public String[] cells;", page))
page.addField(CtField.make("public String info;", page))
page.addField(CtField.make("public String key;", page))
page.addField(CtField.make("public String noticeKey;", page))
page.addConstructor(CtNewConstructor.make(f"""
public SacksPage({PR} pr, String cat) {{
  super(pr, {LIFE}.CanDismiss);
  this.cat = cat;
  this.info = "";
}}""", page))
page.addMethod(CtNewMethod.make("""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ');
}""", page))
page.addMethod(CtNewMethod.make(f"""
public String pickCat(String k, java.util.HashMap caps) {{
  String[] cats = {PKG}.SackDefs.CATS;
  if (this.cat != null && caps.containsKey(this.cat)) return this.cat;
  for (int c = 0; c < cats.length; c++) if (caps.containsKey(cats[c]) && {PKG}.SackPool.catTotal(k, cats[c]) > 0L) return cats[c];
  for (int c = 0; c < cats.length; c++) if (caps.containsKey(cats[c])) return cats[c];
  return null;
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  String k = {PKG}.SackPool.pkey(u);
  this.key = null;
  {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
  java.util.HashMap caps = player == null ? new java.util.HashMap() : {PKG}.SweepTask.caps(player.getInventory());
  this.cat = pickCat(k, caps);
  if (this.cat == null) {{
    b.appendInline((String) null, "Group #SkyySacks {{ Anchor: (Width: 560, Height: 160); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 12); LayoutMode: Top; }}");
    b.appendInline("#SkyySacks", "Label {{ Anchor: (Height: 40); Text: \\"Pocket Dimension\\"; Style: (FontSize: 20, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    b.appendInline("#SkyySacks", "Label {{ Anchor: (Height: 60); Text: \\"You need a magic bag on you to reach in. Craft a Mining, Foraging, Farming or Combat bag at a workbench.\\"; Style: (FontSize: 14, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center, Wrap: true); }}");
    this.cells = new String[36];
    return;
  }}
  this.key = k;
  Integer capObj = (Integer) caps.get(this.cat);
  long capacity = capObj == null ? 0L : (long) capObj.intValue();
  long stored = {PKG}.SackPool.catTotal(k, this.cat);
  String bs = "Style: TextButtonStyle(Default: (Background: #5a4420, LabelStyle: (FontSize: 15, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 15, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 15, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  String tabOn = "Style: TextButtonStyle(Default: (Background: #e0b060, LabelStyle: (FontSize: 15, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #f0c878, LabelStyle: (FontSize: 15, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #b08040, LabelStyle: (FontSize: 15, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  b.appendInline((String) null, "Group #SkyySacks {{ Anchor: (Width: 900, Height: 600); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyySacks", "Group {{ Anchor: (Height: 2); Background: #e0b060; }}");
  b.appendInline("#SkyySacks", "Group #SkyySTabs {{ Anchor: (Height: 46); LayoutMode: Left; Padding: (Top: 8); }}");
  String[] cats = {PKG}.SackDefs.CATS;
  for (int c = 0; c < cats.length; c++) {{
    if (!caps.containsKey(cats[c])) continue;
    boolean sel = cats[c].equals(this.cat);
    b.appendInline("#SkyySTabs", "TextButton #SkyySTab" + cats[c] + " {{ Anchor: (Width: 150, Height: 36); Text: \\"" + cats[c] + "\\"; " + (sel ? tabOn : bs) + " }}");
    b.appendInline("#SkyySTabs", "Label {{ Anchor: (Width: 8, Height: 36); Text: \\"\\"; }}");
    ev.addEventBinding({BT}.Activating, "#SkyySTab" + cats[c], {EVD}.of("a", "tab:" + cats[c]));
  }}
  b.appendInline("#SkyySTabs", "Label {{ Anchor: (Width: 26, Height: 36); Text: \\"\\"; }}");
  b.appendInline("#SkyySTabs", "TextButton #SkyySTabCraft {{ Anchor: (Width: 145, Height: 36); Text: \\"Craft\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyySTabCraft", {EVD}.of("a", "craft"));
  b.appendInline("#SkyySacks", "Label #SkyySCap {{ Anchor: (Height: 34); Text: \\"" + safe(this.cat + " bag - holds up to " + capacity + " of each item - " + stored + " stored") + "\\"; Style: (FontSize: 18, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  java.util.ArrayList entries = new java.util.ArrayList();
  java.util.Iterator it = {PKG}.SackPool.pool(k).entrySet().iterator();
  while (it.hasNext()) {{
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (this.cat.equals({PKG}.SackDefs.catOf((String) e.getKey()))) entries.add(e);
  }}
  java.util.Collections.sort(entries, new {PKG}.CountCmp());
  this.cells = new String[36];
  for (int r = 0; r < 4; r++) {{
    b.appendInline("#SkyySacks", "Group #SkyySRow" + r + " {{ Anchor: (Height: 92); LayoutMode: Left; Padding: (Top: 6); }}");
    for (int c = 0; c < 9; c++) {{
      int idx = r * 9 + c;
      if (idx < entries.size()) {{
        java.util.Map.Entry e = (java.util.Map.Entry) entries.get(idx);
        String id = (String) e.getKey();
        long cnt = ((Long) e.getValue()).longValue();
        this.cells[idx] = id;
        b.appendInline("#SkyySRow" + r, "Button #SkyySCell" + idx + " {{ Anchor: (Width: 86, Height: 86); Style: ButtonStyle( Default: ( Background: #1d3a5f ), Hovered: ( Background: #2f5a8f ), Disabled: ( Background: #1a2c3c ) ); ItemIcon {{ Anchor: (Width: 64, Height: 64, Left: 11, Top: 5); ItemId: \\"" + safe(id) + "\\"; }} Label {{ Anchor: (Width: 80, Height: 18, Right: 4, Bottom: 3); Text: \\"" + cnt + "\\"; Style: (FontSize: 14, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: End); }} }}");
        ev.addEventBinding({BT}.Activating, "#SkyySCell" + idx, {EVD}.of("a", "cell:" + idx + ":stack"));
        ev.addEventBinding({BT}.RightClicking, "#SkyySCell" + idx, {EVD}.of("a", "cell:" + idx + ":one"));
      }} else {{
        this.cells[idx] = null;
        b.appendInline("#SkyySRow" + r, "Group {{ Anchor: (Width: 86, Height: 86); Background: #142030(0.9); }}");
      }}
      b.appendInline("#SkyySRow" + r, "Label {{ Anchor: (Width: 6, Height: 86); Text: \\"\\"; }}");
    }}
  }}
  b.appendInline("#SkyySacks", "Label #SkyySInfo {{ Anchor: (Height: 30); Text: \\"" + safe(this.info) + "\\"; Style: (FontSize: 15, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySacks", "Group #SkyySAct {{ Anchor: (Height: 48); LayoutMode: Left; Padding: (Top: 8); }}");
  b.appendInline("#SkyySAct", "TextButton #SkyySPickAll {{ Anchor: (Width: 200, Height: 38); Text: \\"Pick up all\\"; " + bs + " }}");
  b.appendInline("#SkyySAct", "Label {{ Anchor: (Width: 14, Height: 38); Text: \\"\\"; }}");
  b.appendInline("#SkyySAct", "TextButton #SkyySDepAll {{ Anchor: (Width: 200, Height: 38); Text: \\"Deposit all\\"; " + bs + " }}");
  b.appendInline("#SkyySAct", "Label {{ Anchor: (Width: 14, Height: 38); Text: \\"\\"; }}");
  b.appendInline("#SkyySAct", "Label {{ Anchor: (Width: 420, Height: 38); Text: \\"left click takes a stack - right click takes one\\"; Style: (FontSize: 14, TextColor: #8fa4b8, VerticalAlignment: Center); }}");
  ev.addEventBinding({BT}.Activating, "#SkyySPickAll", {EVD}.of("a", "pickall"));
  ev.addEventBinding({BT}.Activating, "#SkyySDepAll", {EVD}.of("a", "depall"));
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    String[] cats = {PKG}.SackDefs.CATS;
    for (int c = 0; c < cats.length; c++) {{
      if (data.indexOf("tab:" + cats[c] + "\\"") >= 0) {{ this.cat = cats[c]; this.info = ""; rebuild(); return; }}
    }}
    if (data.indexOf("\\"craft\\"") >= 0) {{
      {PLA} pl0 = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
      if (pl0 != null) pl0.getPageManager().openCustomPage(ref, st, new {PKG}.CraftPage(this.playerRef, (String) null));
      return;
    }}
    for (int i = 0; i < 36; i++) {{
      if (this.cells == null || this.cells[i] == null) continue;
    }}
    {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    String k = {PKG}.SackPool.settledKey(u);
    if (k == null) {{ this.info = "bags paused (profile loading or switching) - try again in a moment"; rebuild(); return; }}
    if (this.key != null && !this.key.equals(k)) {{ this.info = "your profile changed - this page now shows it"; rebuild(); return; }}
    for (int i = 0; i < 36; i++) {{
      if (this.cells == null || this.cells[i] == null) continue;
      int n = 0;
      if (data.indexOf("cell:" + i + ":stack\\"") >= 0) n = 64;
      else if (data.indexOf("cell:" + i + ":one\\"") >= 0) n = 1;
      if (n == 0) continue;
      int added = {PKG}.SweepTask.withdraw(player, k, this.cells[i], n);
      this.info = added > 0 ? ("took " + added + " " + this.cells[i]) : "storage is full";
      {PKG}.SackPool.saveSoon(k);
      rebuild();
      return;
    }}
    if (data.indexOf("pickall\\"") >= 0) {{
      int total = 0;
      for (int i = 0; i < 36; i++) {{
        if (this.cells[i] == null) continue;
        int added; int guard = 0;
        do {{ added = {PKG}.SweepTask.withdraw(player, k, this.cells[i], 64); total += added; guard++; }} while (added > 0 && guard < 64);
      }}
      this.info = total > 0 ? ("picked up " + total + " items") : "storage is full";
      {PKG}.SackPool.saveSoon(k);
      rebuild();
      return;
    }}
    if (data.indexOf("depall\\"") >= 0) {{
      {PKG}.SackPool.clearExempt(k);
      int moved = {PKG}.SweepTask.sweep(player, k, this.cat, true);
      this.info = moved > 0 ? ("deposited " + moved + " items") : "nothing to deposit (or sack full)";
      {PKG}.SackPool.saveSoon(k);
      rebuild();
      return;
    }}
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("sacks page event failed: " + t); }}
}}""", page))

# 0.7.2: the active profile changed while this page is open (ProcTask, world thread). set() only on a label the last build
# created (same pattern as CraftPage.live - no re-append from a tick); the next click rebuilds for the new profile.
page.addMethod(CtNewMethod.make(f"""
public void profileNotice(String k) {{
  if (this.key == null || k == null || k.equals(this.noticeKey)) return;
  this.noticeKey = k;
  {UCB} c = new {UCB}();
  c.set("#SkyySInfo.Text", "Your profile changed - click a tab to refresh this page");
  sendUpdate(c, false);
}}""", page))

# ================= SacksCmd =================
cmd.addConstructor(CtNewConstructor.make("""
public SacksCmd() {
  super("sacks", "Open your pocket dimension (needs a magic bag on you)");
  addAliases(new String[] { "pd", "bags" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) {{ pr.sendMessage({MSG}.raw("[SkyySacks] player not found")); return; }}
    // EXPERIMENT 0.3.0: open with an (empty) container window so the client shows the player inventory below the page (chest style)
    com.hypixel.hytale.server.core.entity.entities.player.windows.Window[] wins = new com.hypixel.hytale.server.core.entity.entities.player.windows.Window[] {{ new com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow(new com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer((short) 9)) }};
    boolean ok = player.getPageManager().openCustomPageWithWindows(ref, store, new {PKG}.SacksPage(pr, (String) null), wins);
    if (!ok) pr.sendMessage({MSG}.raw("[SkyySacks] openCustomPageWithWindows returned false"));
  }} catch (Throwable t) {{
    {PKG}.SackPool.warn("/sacks failed: " + t);
    pr.sendMessage({MSG}.raw("[SkyySacks] could not open the sacks page"));
  }}
}}""", cmd))

# ==== SELF-TEST: GrantTask + SackReady (strip once verified in-game) ====
grt.addInterface(pool.get("java.lang.Runnable"))
grt.addField(CtField.make(f"public {PR} pr;", grt))
grt.addField(CtField.make("public boolean onWorld;", grt))
grt.addField(CtField.make("public int tries;", grt))
grt.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap GRANTED = new java.util.concurrent.ConcurrentHashMap();", grt))
grt.addConstructor(CtNewConstructor.make(f"public GrantTask({PR} pr) {{ this.pr = pr; this.onWorld = false; this.tries = 0; }}", grt))
grt.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (pr == null || !pr.isValid()) return;
    if (!this.onWorld) {{
      java.util.UUID wu = pr.getWorldUuid();
      {WLD} w = wu == null ? null : {UNI}.get().getWorld(wu);
      if (w == null) {{ if (++this.tries < 20) {HSV}.SCHEDULED_EXECUTOR.schedule(this, 1L, java.util.concurrent.TimeUnit.SECONDS); return; }}
      this.onWorld = true;
      w.execute(this);
      return;
    }}
    java.util.UUID u = pr.getUuid();
    if (GRANTED.putIfAbsent(u, Boolean.TRUE) != null) return;
    {REF} r = pr.getReference();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    if (p == null) return;
    {IC} stor = p.getInventory().getStorage();
    {IST} t1 = stor.addItemStack(new {IS}("Skyy_Sack_Mining_Small", 1));
    {IST} t2 = stor.addItemStack(new {IS}("Ore_Copper", 64));
    {IST} t3 = stor.addItemStack(new {IS}("Ore_Iron", 32));
    boolean ok = t1 != null && t1.succeeded() && t2 != null && t2.succeeded() && t3 != null && t3.succeeded();
    pr.sendMessage({MSG}.raw(ok ? "[SkyySacks test] granted: Small Mining Sack + copper/iron ore into STORAGE - the ore should vanish into the sack within ~4s. /sacks to view."
                                : "[SkyySacks test] grant partly failed (storage full?) - check the server log."));
    if (!ok) {PKG}.SackPool.warn("self-test grant not fully added for " + u);
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("self-test grant failed: " + t); }}
}}""", grt))
srd.addInterface(pool.get("java.util.function.Consumer"))
srd.addConstructor(CtNewConstructor.make("public SackReady() { }", srd))
srd.addMethod(CtNewMethod.make(f"""
public void accept(Object ev) {{
  try {{
    {PRE} e = ({PRE}) ev;
    {REF} r = e.getPlayerRef();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    {HSV}.SCHEDULED_EXECUTOR.schedule(new {PKG}.GrantTask(pr), 4L, java.util.concurrent.TimeUnit.SECONDS);
  }} catch (Throwable t) {{ }}
}}""", srd))

# ================= SacksPageFactory (right-click on a sack item -> OpenCustomUI "SkyySacks<Cat>") =================
fac.addInterface(pool.get("java.util.function.Function"))
fac.addField(CtField.make("public String cat;", fac))
fac.addConstructor(CtNewConstructor.make("public SacksPageFactory(String cat) { this.cat = cat; }", fac))
fac.addMethod(CtNewMethod.make(f"""
public Object apply(Object o) {{
  return new {PKG}.SacksPage(({PR}) o, this.cat);
}}""", fac))

# ================= BagMirror (per player: SimpleItemContainer mirroring the pool for bench crafting) =================
mir.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap MIRRORS = new java.util.concurrent.ConcurrentHashMap();", mir))
mir.addField(CtField.make(f"public {SIC} cont;", mir))
mir.addField(CtField.make("public String[] slotIds;", mir))
mir.addField(CtField.make("public int[] slotQty;", mir))
mir.addField(CtField.make(f"public {CIC} combined;", mir))
mir.addField(CtField.make("public Object vanilla;", mir))
mir.addField(CtField.make("public String sig;", mir))
mir.addField(CtField.make("public String key;", mir))
mir.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LASTKEY = new java.util.concurrent.ConcurrentHashMap();", mir))
# 0.7.3: bench id -> Set of wanted ingredient ids / resource type ids; item id -> String[] of its resource type ids
mir.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap WANTED = new java.util.concurrent.ConcurrentHashMap();", mir))
mir.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap RTS = new java.util.concurrent.ConcurrentHashMap();", mir))
mir.addConstructor(CtNewConstructor.make(f"""
public BagMirror(String key) {{
  this.key = key;
  this.cont = new {SIC}((short) 36);
  this.slotIds = new String[36];
  this.slotQty = new int[36];
  this.sig = "";
}}""", mir))
mir.addMethod(CtNewMethod.make(f"""
public static {PKG}.BagMirror of(String k) {{
  {PKG}.BagMirror m = ({PKG}.BagMirror) MIRRORS.get(k);
  if (m == null) {{ m = new {PKG}.BagMirror(k); {PKG}.BagMirror prev = ({PKG}.BagMirror) MIRRORS.putIfAbsent(k, m); if (prev != null) m = prev; }}
  return m;
}}""", mir))
# apply consumption: anything missing from the mirror vs. what we put there left the pool (the bench took it)
mir.addMethod(CtNewMethod.make(f"""
public int sync() {{
  int consumed = 0;
  for (int i = 0; i < 36; i++) {{
    if (this.slotIds[i] == null) continue;
    {IS} it = this.cont.getItemStack((short) i);
    int actual = (it == null || it.isEmpty()) ? 0 : it.getQuantity();
    if (actual < this.slotQty[i]) {{ int d = this.slotQty[i] - actual; {PKG}.SackPool.add(this.key, this.slotIds[i], -(long) d); consumed += d; this.slotQty[i] = actual; }}
  }}
  return consumed;
}}""", mir))
# 0.7.3 bench-aware mirror (research/Smithing-Smelting-Spec.md 7.3): the ingredient item ids and resource type ids a bench can use -
# every input of CraftingPlugin.getBenchRecipes(bench) plus the bench's tier-upgrade materials - cached per bench id (non-empty only).
mir.addMethod(CtNewMethod.make(f"""
public static void addInputs(java.util.Set s, {MQ}[] in) {{
  for (int i = 0; in != null && i < in.length; i++) {{
    if (in[i] == null) continue;
    if (in[i].getItemId() != null) s.add(in[i].getItemId());
    else if (in[i].getResourceTypeId() != null) s.add(in[i].getResourceTypeId());
  }}
}}""", mir))
mir.addMethod(CtNewMethod.make(f"""
public static java.util.Set wantedFor(Object w) {{
  try {{
    if (!(w instanceof {BWN})) return null;
    {BLT} bt = (({BWN}) w).getBlockType();
    if (bt == null) return null;
    {BEN} b = bt.getBench();
    if (b == null || b.getId() == null) return null;
    String key = b.getId().toLowerCase();
    Object c = WANTED.get(key);
    if (c != null) return (java.util.Set) c;
    java.util.HashSet s = new java.util.HashSet();
    java.util.List l = {CRP}.getBenchRecipes(b);
    for (int i = 0; l != null && i < l.size(); i++) {{
      Object o = l.get(i);
      if (o instanceof {CRR}) addInputs(s, (({CRR}) o).getInput());
    }}
    for (int t = 1; t <= 10; t++) {{
      {BUR} ur = null;
      try {{ ur = b.getUpgradeRequirement(t); }} catch (Throwable e) {{ ur = null; }}
      if (ur != null) addInputs(s, ur.getInput());
    }}
    if (!s.isEmpty()) WANTED.put(key, s);
    return s;
  }} catch (Throwable t) {{ return null; }}
}}""", mir))
mir.addMethod(CtNewMethod.make(f"""
public static String[] rtsOf(String id) {{
  Object c = RTS.get(id);
  if (c != null) return (String[]) c;
  String[] out = new String[0];
  try {{
    {ITM} it = {PKG}.ProcBench.item(id);
    if (it == null) return out;
    {IRT}[] r = it.getResourceTypes();
    java.util.ArrayList l = new java.util.ArrayList();
    for (int i = 0; r != null && i < r.length; i++) if (r[i] != null && r[i].id != null) l.add(r[i].id);
    out = (String[]) l.toArray(new String[0]);
    RTS.put(id, out);
  }} catch (Throwable t) {{ }}
  return out;
}}""", mir))
mir.addMethod(CtNewMethod.make("""
public static boolean wants(java.util.Set s, String id) {
  if (s == null || id == null) return false;
  if (s.contains(id)) return true;
  String[] r = rtsOf(id);
  for (int i = 0; i < r.length; i++) if (s.contains(r[i])) return true;
  return false;
}""", mir))
# rebuild the mirror from the pool: only categories the player carries a bag for; up to 4 stacks per item, 36 slots.
# 0.7.3: `wanted` (item ids / resource type ids the open bench or the craft page can use; null = none) goes first - one stack of every
# wanted item, then wanted items up to 4 stacks, then everything else by count (the old order) - so big piles of stone or logs can no
# longer crowd a bench's ingredients out of the 36 slots. sync() before every rebuild keeps the pool accounting exact.
mir.addMethod(CtNewMethod.make(f"""
public String rebuild(java.util.HashMap caps, java.util.Set wanted) {{
  try {{ this.cont.clear(); }} catch (Throwable t) {{ }}
  for (int i = 0; i < 36; i++) {{ this.slotIds[i] = null; this.slotQty[i] = 0; }}
  StringBuilder sb = new StringBuilder();
  java.util.ArrayList entries = new java.util.ArrayList({PKG}.SackPool.pool(this.key).entrySet());
  java.util.Collections.sort(entries, new {PKG}.CountCmp());
  int n = entries.size();
  String[] ids = new String[n];
  long[] left = new long[n];
  int[] max = new int[n];
  int[] stacks = new int[n];
  boolean[] want = new boolean[n];
  for (int e = 0; e < n; e++) {{
    java.util.Map.Entry en = (java.util.Map.Entry) entries.get(e);
    String id = (String) en.getKey();
    long cnt = ((Long) en.getValue()).longValue();
    String cat = {PKG}.SackDefs.catOf(id);
    if (cat == null || !caps.containsKey(cat) || cnt <= 0L) continue;
    ids[e] = id;
    left[e] = cnt;
    int mx = 64;
    try {{ {IS} probe = new {IS}(id, 1); if (probe.getItem() != null && probe.getItem().getMaxStack() > 0) mx = probe.getItem().getMaxStack(); }} catch (Throwable t) {{ }}
    max[e] = mx;
    want[e] = wanted != null && wants(wanted, id);
  }}
  int slot = 0;
  for (int pass = 0; pass < 3 && slot < 36; pass++) {{
    int lim = pass == 0 ? 1 : 4;
    for (int e = 0; e < n && slot < 36; e++) {{
      if (ids[e] == null) continue;
      if (pass < 2 && !want[e]) continue;
      if (pass == 2 && want[e]) continue;
      while (left[e] > 0L && stacks[e] < lim && slot < 36) {{
        int q = left[e] < (long) max[e] ? (int) left[e] : max[e];
        this.cont.setItemStackForSlot((short) slot, new {IS}(ids[e], q));
        this.slotIds[slot] = ids[e]; this.slotQty[slot] = q;
        sb.append(ids[e]).append('=').append(q).append(';');
        left[e] = left[e] - (long) q;
        slot++;
        stacks[e] = stacks[e] + 1;
      }}
    }}
  }}
  return sb.toString();
}}""", mir))
mir.addMethod(CtNewMethod.make("""
public String rebuild(java.util.HashMap caps) {
  return rebuild(caps, (java.util.Set) null);
}""", mir))
# 0.7.2: a bench mirror belongs to ONE profile key. When the active key changes, the old mirror is synced into its own pool
# (what a bench took before the switch), saved and dropped; CraftLinkTask swaps it out of any open bench window in the same run.
mir.addMethod(CtNewMethod.make(f"""
public static {PKG}.BagMirror retireOther(java.util.UUID u, String k) {{
  String old = (String) LASTKEY.put(u, k);
  if (old == null || old.equals(k)) return null;
  {PKG}.BagMirror m = ({PKG}.BagMirror) MIRRORS.remove(old);
  if (m == null) return null;
  int c = m.sync();
  {PKG}.CraftLog.later(old, "PROFILE bench mirror retired - active key now " + k + " consumed=" + c);
  {PKG}.SackPool.saveSoon(old);
  return m;
}}""", mir))
# 0.7.2 review fix: drop everything the mirror offers (call sync() first - it accounts what the bench already took).
mir.addMethod(CtNewMethod.make(f"""
public void empty() {{
  try {{ this.cont.clear(); }} catch (Throwable t) {{ }}
  for (int i = 0; i < 36; i++) {{ this.slotIds[i] = null; this.slotQty[i] = 0; }}
  this.sig = "";
}}""", mir))
mir.addMethod(CtNewMethod.make("""
public boolean holds() {
  for (int i = 0; i < 36; i++) if (this.slotIds[i] != null) return true;
  return false;
}""", mir))
# 0.7.2 review fix (settle window): while SackPool.settledKey(u) is null CraftLinkTask calls only this. The player's last bench
# mirror (LASTKEY) is synced into its OWN pool; if it still offers anything it is emptied, and every open bench it is attached to
# gets setValid(false), which makes BenchWindow.getExtraResourcesSection() re-feed the vanilla nearby-chest resources
# (CraftingManager.feedExtraResourcesSection; every MaterialContainerWindow is a BenchWindow); if no re-feed happened the emptied
# mirror stays attached with no extra materials. An emptied mirror returns right away on the next 300ms runs (no repeat updates).
# No key is fed and no mirror is rebuilt until the switch settles, so a bench cannot use bag items across profiles.
mir.addMethod(CtNewMethod.make(f"""
public static int park({WM} wm, java.util.List wins, java.util.UUID u) {{
  String lk = (String) LASTKEY.get(u);
  if (lk == null) return 0;
  {PKG}.BagMirror m = ({PKG}.BagMirror) MIRRORS.get(lk);
  if (m == null) return 0;
  int consumed = m.sync();
  if (consumed > 0) {PKG}.SackPool.saveSoon(lk);
  if (!m.holds()) return consumed;
  m.empty();
  int parked = 0;
  for (int i = 0; wins != null && i < wins.size(); i++) {{
    Object w = wins.get(i);
    if (!(w instanceof {MCW})) continue;
    {MERS} sec = (({MCW}) w).getExtraResourcesSection();
    if (sec == null) continue;
    {IC} existing = sec.getItemContainer();
    if (existing == null || (existing != m.combined && existing != m.cont)) continue;
    parked++;
    sec.setValid(false);
    sec = (({MCW}) w).getExtraResourcesSection();
    if (sec != null && !sec.isValid()) {{ sec.setExtraMaterials(new {IQ}[0]); sec.setValid(true); }}
    if (wm != null) {{
      try {{ wm.updateWindow(({WIN}) w); }} catch (Throwable t) {{ {PKG}.SackPool.warn("craft link: park updateWindow failed: " + t); }}
    }}
  }}
  if (parked > 0) {{
    {PKG}.SackPool.warn("craft link: profile switch settling - bag materials taken off " + parked + " open bench window(s) (key " + lk + ", consumed=" + consumed + ")");
    {PKG}.CraftLog.later(lk, "PROFILE switch settling - bag materials taken off " + parked + " open bench window(s) consumed=" + consumed);
  }}
  return consumed;
}}""", mir))
mir.addMethod(CtNewMethod.make(f"""
public {IQ}[] quantities() {{
  java.util.LinkedHashMap sum = new java.util.LinkedHashMap();
  for (int i = 0; i < 36; i++) {{
    if (this.slotIds[i] == null) continue;
    Integer cur = (Integer) sum.get(this.slotIds[i]);
    sum.put(this.slotIds[i], Integer.valueOf((cur == null ? 0 : cur.intValue()) + this.slotQty[i]));
  }}
  {IQ}[] out = new {IQ}[sum.size()];
  java.util.Iterator it = sum.entrySet().iterator(); int k = 0;
  while (it.hasNext()) {{ java.util.Map.Entry e = (java.util.Map.Entry) it.next(); out[k++] = new {IQ}((String) e.getKey(), ((Integer) e.getValue()).intValue()); }}
  return out;
}}""", mir))
mir.addMethod(CtNewMethod.make(f"""
public static int syncAll() {{
  int n = 0;
  java.util.Iterator it = MIRRORS.values().iterator();
  while (it.hasNext()) {{
    try {{ n += (({PKG}.BagMirror) it.next()).sync(); }} catch (Throwable t) {{ }}
  }}
  return n;
}}""", mir))

# ================= CraftLinkTask (world thread, every 300ms per player) =================
# 0.7.2 review fix: the key comes from SackPool.settledKey. While a profile switch settles (null) the task only parks the mirror
# (BagMirror.park) and returns: no retireOther, no rebuild, nothing fed to the bench for ANY key until the switch has settled.
clt.addInterface(pool.get("java.lang.Runnable"))
clt.addField(CtField.make(f"public {PR} pr;", clt))
clt.addField(CtField.make("public java.util.UUID expectedWorld;", clt))
clt.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DBG = new java.util.concurrent.ConcurrentHashMap();", clt))
clt.addConstructor(CtNewConstructor.make(f"public CraftLinkTask({PR} pr, java.util.UUID w) {{ this.pr = pr; this.expectedWorld = w; }}", clt))
clt.addMethod(CtNewMethod.make(f"""
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
    java.util.UUID u = pr.getUuid();
    String k = {PKG}.SackPool.settledKey(u);
    if (k == null) {{
      {WM} wm0 = p.getWindowManager();
      java.util.List wins0 = null;
      if (wm0 != null) wins0 = wm0.getWindows();
      {PKG}.BagMirror.park(wm0, wins0, u);
      return;
    }}
    {PKG}.BagMirror stale = {PKG}.BagMirror.retireOther(u, k);
    {WM} wm = p.getWindowManager();
    if (wm == null) return;
    java.util.List wins = wm.getWindows();
    boolean any = false;
    if (wins != null && wins.size() > 0 && !DBG.containsKey(u)) {{
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < wins.size(); i++) {{ Object w0 = wins.get(i); sb.append(w0 == null ? "null" : w0.getClass().getName()).append(w0 instanceof {MCW} ? "[MCW] " : " "); }}
      {PKG}.SackPool.warn("craft link: windows=" + sb + " caps=" + {PKG}.SweepTask.caps(p.getInventory()).keySet());
      DBG.put(u, Boolean.TRUE);
    }}
    if (wins == null || wins.isEmpty()) DBG.remove(u);
    for (int i = 0; wins != null && i < wins.size(); i++) {{
      Object w = wins.get(i);
      if (!(w instanceof {MCW})) continue;
      any = true;
      {PKG}.BagMirror m = {PKG}.BagMirror.of(k);
      int consumed = m.sync();
      java.util.HashMap caps = {PKG}.SweepTask.caps(p.getInventory());
      String sig = m.rebuild(caps, {PKG}.BagMirror.wantedFor(w));
      {MERS} sec = (({MCW}) w).getExtraResourcesSection();
      if (sec == null) continue;
      {IC} existing = sec.getItemContainer();
      if (stale != null && existing != null && (existing == stale.combined || existing == stale.cont)) existing = ({IC}) stale.vanilla;
      boolean ours = existing != null && (existing == m.combined || existing == m.cont);
      if (!ours) {{
        if (existing == null) {{ m.vanilla = null; m.combined = new {CIC}(new {IC}[] {{ m.cont }}); }}
        else {{ m.vanilla = existing; m.combined = new {CIC}(new {IC}[] {{ existing, m.cont }}); }}
      }}
      sec.setItemContainer(m.combined);
      sec.setExtraMaterials(m.quantities());
      sec.setValid(true);
      if (!ours || consumed > 0 || !sig.equals(m.sig)) {{
        m.sig = sig;
        try {{ wm.updateWindow(({WIN}) w); {PKG}.SackPool.warn("craft link: fed " + m.quantities().length + " item types to " + w.getClass().getSimpleName() + " (existing=" + (existing == null ? "null" : existing.getClass().getSimpleName()) + ", consumed=" + consumed + ")"); }}
        catch (Throwable t) {{ {PKG}.SackPool.warn("craft link: updateWindow failed: " + t); }}
      }}
      if (consumed > 0) {PKG}.SackPool.saveSoon(k);
    }}
    if (!any) {{
      {PKG}.BagMirror m = ({PKG}.BagMirror) {PKG}.BagMirror.MIRRORS.get(k);
      if (m != null) {{ int c = m.sync(); if (c > 0) {PKG}.SackPool.saveSoon(k); {PKG}.BagMirror.MIRRORS.remove(k); }}
    }}
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("craft link failed: " + t); }}
}}""", clt))

ctk.addInterface(pool.get("java.lang.Runnable"))
ctk.addConstructor(CtNewConstructor.make("public CraftTick() { }", ctk))
ctk.addMethod(CtNewMethod.make(f"""
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
      w.execute(new {PKG}.CraftLinkTask(pr, wu));
    }}
  }} catch (Throwable t) {{ }}
}}""", ctk))

# ================= CraftPage (inventory crafting v1: Fieldcraft + bench accessories + collection unlocks) =================

cpg.addMethod(CtNewMethod.make("""
public static String pretty(String id) {
  if (id == null) return "?";
  String s = id.replace('_', ' ');
  int q = s.indexOf(':');
  if (q >= 0 && q + 1 < s.length()) s = s.substring(q + 1);
  return s;
}""", cpg))
# 0.7.3: bench accessories retired with the table-only Alchemy / Cooking call (orchestrator decision 4: the Campfire too - its 3 recipes
# are cooked food). Their acc:has entries unlock nothing and their recipes never craft instantly.
# 0.7.4: the Campfire STAYS retired here (Crafting / Smithing / Farming / search / Collections keep no cooked food); its accessory only
# opens the separate Campfire tab (campfireTier / campRecipes below), where SkyyCooking grades the dish.
cpg.addMethod(CtNewMethod.make("""
public static boolean retiredBench(String id) {
  return id != null && (id.equalsIgnoreCase("Alchemybench") || id.equalsIgnoreCase("Cookingbench") || id.equalsIgnoreCase("Campfire"));
}""", cpg))
# 0.7.3 search: lower-case words of letters and digits (max 40 chars); every word must appear in the item name or id
cpg.addMethod(CtNewMethod.make("""
public static String cleanQuery(String q) {
  if (q == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < q.length() && sb.length() < 40; i++) {
    char c = q.charAt(i);
    if (Character.isLetterOrDigit(c)) sb.append(Character.toLowerCase(c));
    else if (sb.length() > 0 && sb.charAt(sb.length() - 1) != ' ') sb.append(' ');
  }
  return sb.toString().trim();
}""", cpg))
cpg.addMethod(CtNewMethod.make("""
public static boolean nameMatches(String q, String outId) {
  if (q == null || q.length() == 0) return true;
  if (outId == null) return false;
  String name = pretty(outId).toLowerCase() + " " + outId.toLowerCase().replace('_', ' ');
  String[] w = q.split(" ");
  for (int i = 0; i < w.length; i++) {
    String x = w[i].trim();
    if (x.length() > 0 && name.indexOf(x) < 0) return false;
  }
  return true;
}""", cpg))
# 0.7.3: one string value out of the page event JSON (the TextField value arrives as "@SearchQuery": "..."); handles escaped quotes,
# backslashes and unicode escapes (quote = char 34, backslash = char 92, so no escape sequences are needed here)
cpg.addMethod(CtNewMethod.make("""
public static String jsonStr(String data, String key) {
  if (data == null || key == null) return "";
  String qt = String.valueOf((char) 34);
  int i = data.indexOf(qt + key + qt);
  if (i < 0) return "";
  i = data.indexOf(':', i + key.length() + 2);
  if (i < 0) return "";
  i++;
  while (i < data.length() && Character.isWhitespace(data.charAt(i))) i++;
  if (i >= data.length() || data.charAt(i) != 34) return "";
  i++;
  StringBuilder sb = new StringBuilder();
  while (i < data.length() && sb.length() < 200) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) {
      char n = data.charAt(i + 1);
      if (n == 'u' && i + 5 < data.length()) {
        try { sb.append((char) Integer.parseInt(data.substring(i + 2, i + 6), 16)); } catch (Throwable t) { }
        i += 6;
        continue;
      }
      if (n == 'n' || n == 'r' || n == 't' || n == 'b' || n == 'f') sb.append(' '); else sb.append(n);
      i += 2;
      continue;
    }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
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
# accessory item ids the player carries anywhere -> bench ids granted
cpg.addMethod(CtNewMethod.make(f"""
public static java.util.HashMap accessories({PLA} p, java.util.UUID u) {{
  java.util.HashMap out = new java.util.HashMap();
  java.util.ArrayList ids = new java.util.ArrayList();
  // only accessories EQUIPPED in the SkyyAccessories bag count (Skyy: "when you have the accessory in your accessory bag")
  try {{
    Object b = System.getProperties().get("skyy.bridge");
    Object v = b == null ? null : ((java.util.Map) b).get("acc:has:" + u.toString());
    if (v != null) {{
      String[] parts = String.valueOf(v).split(",");
      for (int i = 0; i < parts.length; i++) if (parts[i].trim().length() > 0) ids.add(parts[i].trim());
    }}
  }} catch (Throwable t) {{ }}
  for (int i = 0; i < ids.size(); i++) {{
    String id = (String) ids.get(i);
    if (id.equals("Skyy_Accessory_Bag") || !id.startsWith("Skyy_Accessory_")) continue;
    String tail = id.substring("Skyy_Accessory_".length());
    String bench = tail; int tier = 1;
    int t = tail.lastIndexOf("_T");
    if (t > 0 && t + 2 < tail.length()) {{
      try {{ tier = Integer.parseInt(tail.substring(t + 2)); bench = tail.substring(0, t); }} catch (Throwable e) {{ }}
    }}
    if (bench.length() == 0) continue;
    if (retiredBench(bench)) continue;  // 0.7.3: retired accessories (Alchemy, Cooking, Campfire) unlock nothing
    if (!knownBench(bench) && ACCWARN.putIfAbsent(id, Boolean.TRUE) == null) {PKG}.SackPool.warn("accessory " + id + " in acc:has names no crafting bench (" + bench + ") - it unlocks nothing; the Omni must be published as one Skyy_Accessory_<Bench>_T<n> entry per bench");
    Integer cur = (Integer) out.get(bench);
    if (cur == null || cur.intValue() < tier) out.put(bench, Integer.valueOf(tier));
  }}
  return out;
}}""", cpg))
# ---- 0.7.4 Campfire accessory tab (Skyy 2026-09-24: the Campfire accessory comes back as an emergency cook; SkyyCooking 0.1.1 contract) ----
cpg.addField(CtField.make("public static long CAMPWARN;", cpg))
# highest Skyy_Accessory_Campfire tier listed in acc:has:<uuid> (0 = none). A separate parse on purpose: accessories() keeps skipping the
# retired Campfire, so it never unlocks recipes in the merged tabs, search or Collections - it only opens the Campfire tab.
cpg.addMethod(CtNewMethod.make("""
public static int campfireTier(java.util.UUID u) {
  int best = 0;
  try {
    Object b = System.getProperties().get("skyy.bridge");
    Object v = (b instanceof java.util.Map) ? ((java.util.Map) b).get("acc:has:" + u.toString()) : null;
    if (v == null) return 0;
    String[] parts = String.valueOf(v).split(",");
    for (int i = 0; i < parts.length; i++) {
      String id = parts[i].trim();
      if (!id.startsWith("Skyy_Accessory_")) continue;
      String tail = id.substring("Skyy_Accessory_".length());
      String bench = tail;
      int tier = 1;
      int ti = tail.lastIndexOf("_T");
      if (ti > 0 && ti + 2 < tail.length()) {
        try { tier = Integer.parseInt(tail.substring(ti + 2)); bench = tail.substring(0, ti); } catch (Throwable e) { }
      }
      if (bench.equalsIgnoreCase("Campfire") && tier > best) best = tier;
    }
  } catch (Throwable x) { }
  return best;
}""", cpg))
# the dish ids SkyyCooking's cook:fn:campfire accepts (bridge String cook:campfire:ids, comma separated); null = SkyyCooking not loaded
cpg.addMethod(CtNewMethod.make("""
public static java.util.HashSet campIds() {
  try {
    Object b = System.getProperties().get("skyy.bridge");
    Object v = (b instanceof java.util.Map) ? ((java.util.Map) b).get("cook:campfire:ids") : null;
    if (!(v instanceof String)) return null;
    java.util.HashSet s = new java.util.HashSet();
    String[] parts = ((String) v).split(",");
    for (int i = 0; i < parts.length; i++) if (parts[i].trim().length() > 0) s.add(parts[i].trim());
    return s;
  } catch (Throwable t) { return null; }
}""", cpg))
# a Campfire-bench recipe: the same test SkyyCooking's isCampfire makes ("Campfire".equals(BenchRequirement.id))
cpg.addMethod(CtNewMethod.make(f"""
public static boolean campfireRecipe({CRR} r) {{
  if (r == null) return false;
  {BRQ}[] br = r.getBenchRequirement();
  for (int i = 0; br != null && i < br.length; i++) if (br[i] != null && "Campfire".equals(br[i].id)) return true;
  return false;
}}""", cpg))
# the Campfire tab's recipe ids: Campfire-bench recipes up to the accessory tier whose primary output is in cook:campfire:ids (exactly the
# dishes cook:fn:campfire accepts); without SkyyCooking every Campfire-bench recipe (the vanilla ones - plain output, no XP)
cpg.addMethod(CtNewMethod.make(f"""
public static java.util.TreeSet campRecipes(java.util.UUID u) {{
  java.util.TreeSet ids = new java.util.TreeSet();
  int tier = campfireTier(u);
  if (tier <= 0) return ids;
  java.util.HashSet ok = campIds();
  java.util.Iterator it = {CRR}.getAssetMap().getAssetMap().values().iterator();
  while (it.hasNext()) {{
    {CRR} r = ({CRR}) it.next();
    {BRQ}[] br = r.getBenchRequirement();
    if (br == null) continue;
    boolean fits = false;
    for (int i = 0; i < br.length; i++) {{
      if (br[i] == null || !"Campfire".equals(br[i].id)) continue;
      int need = br[i].requiredTierLevel; if (need <= 0) need = 1;
      if (need <= tier) fits = true;
    }}
    if (!fits) continue;
    if (ok != null) {{
      {MQ} po = r.getPrimaryOutput();
      String oid = po == null ? null : po.getItemId();
      if (oid == null || !ok.contains(oid)) continue;
    }}
    ids.add(r.getId());
  }}
  return ids;
}}""", cpg))
# Grade of a graded dish id (Skyy_Cook_<dish>_G<c>); 0 = plain / not a graded id
cpg.addMethod(CtNewMethod.make("""
public static int gradeOfId(String id) {
  if (id == null || !id.startsWith("Skyy_Cook_")) return 0;
  int g = id.lastIndexOf("_G");
  if (g < 0 || g + 2 >= id.length()) return 0;
  try { return Integer.parseInt(id.substring(g + 2)); } catch (Throwable t) { return 0; }
}""", cpg))
# THE bridge call (SkyyCooking 0.1.1 cook:fn:campfire, its suggested SkyySacks call): world thread, AFTER the materials were removed, once
# per click with the finished crafts (crafts 0 = preview: no XP, no chat). Returns the item id to give INSTEAD of the primary output (same
# quantity), or null = give the plain output (Function missing, null / non-String answer, an id that is not a loaded item, a throw).
# SkyyCooking pays the Cooking XP (x campfire.xpFactor) inside the call and applies its own busy / profile-key / creative rules.
cpg.addMethod(CtNewMethod.make(f"""
public static String campCall({PLA} p, java.util.UUID u, String k, {CRR} r, int crafts) {{
  try {{
    Object f = {PKG}.SackPool.bridge().get("cook:fn:campfire");
    if (!(f instanceof java.util.function.Function)) return null;
    Boolean cr = null;
    try {{ if (p != null) cr = Boolean.valueOf(p.getGameMode() == {GM}.Creative); }} catch (Throwable gm) {{ cr = null; }}
    Object got = ((java.util.function.Function) f).apply(new Object[] {{ u, String.valueOf(r.getId()), Integer.valueOf(crafts), k, cr }});
    if (!(got instanceof String)) return null;
    String id = ((String) got).trim();
    if (id.length() == 0 || {PKG}.ProcBench.item(id) == null) return null;
    return id;
  }} catch (Throwable t) {{
    long now = System.currentTimeMillis();
    if (now - CAMPWARN > 60000L) {{ CAMPWARN = now; {PKG}.SackPool.warn("campfire tab: cook:fn:campfire failed (plain output given): " + t); }}
    return null;
  }}
}}""", cpg))
# what a craft on this row gives right now (PREVIEW call, crafts 0) - appended to the row name
cpg.addMethod(CtNewMethod.make(f"""
public static String campRowNote({PLA} p, java.util.UUID u, String k, {CRR} r) {{
  if (campIds() == null) return "  - plain food (SkyyCooking is not installed)";
  int g = gradeOfId(campCall(p, u, k, r, 0));
  return g > 0 ? ("  - comes out Grade " + g) : "  - comes out plain";
}}""", cpg))
# the tab's emergency-cook line (Skyy: 50% XP, 75% of the buffs the Cooking skill adds); shown with set(), so commas and colons are safe
cpg.addMethod(CtNewMethod.make("""
public static String campNote() {
  if (campIds() == null) return "Campfire accessory = quick emergency cooking: plain food and no Cooking XP (SkyyCooking is not installed).";
  return "Campfire accessory = emergency cook: 50% Cooking XP, 75% of your cooking bonus. A Cooking Bench gives the full Grade and XP.";
}""", cpg))
# collection unlocks published by SkyyCollections via the JVM bridge: "coll:recipes:<uuid>" -> "id,id,id"
cpg.addMethod(CtNewMethod.make("""
public static java.util.HashSet collectionRecipes(java.util.UUID u) {
  java.util.HashSet out = new java.util.HashSet();
  try {
    Object b = System.getProperties().get("skyy.bridge");
    if (b == null) return out;
    Object v = ((java.util.Map) b).get("coll:recipes:" + u.toString());
    if (v == null) return out;
    String[] parts = String.valueOf(v).split(",");
    for (int i = 0; i < parts.length; i++) if (parts[i].trim().length() > 0) out.add(parts[i].trim());
  } catch (Throwable t) { }
  return out;
}""", cpg))
# tabs: list of String[]{tabId, label} ; recipes for a tab: list of CraftingRecipe
cpg.addMethod(CtNewMethod.make("""
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
# benches with their own TIMED tab (0.7.3: Furnace and Tannery only - Alchemy is table only now)
cpg.addMethod(CtNewMethod.make("""
public static boolean separateBench(String id) {
  return id != null && (id.equalsIgnoreCase("Furnace") || id.equalsIgnoreCase("Tannery"));
}""", cpg))
# 0.7.3 review fix: the one Processing (timed in vanilla) bench that crafts INSTANTLY in the merged tabs. Skyy's crafting layout lock
# (HANDOFF "Crafting layout + OMNI"): Crafting = Fieldcraft + every equipped bench accessory except Alchemy, Furnace, Tannery -
# "... Campfire, Salvage all merged, instant". The Campfire is retired since (orchestrator decision 4); Salvage is not.
cpg.addMethod(CtNewMethod.make("""
public static boolean instantProc(String id) {
  return id != null && id.equalsIgnoreCase("Salvagebench");
}""", cpg))
# 0.7.3 (research/Smithing-Smelting-Spec.md 6.3): true when EVERY bench requirement of the recipe is a retired table-only bench or a timed
# Processing bench other than Salvagebench (Furnace, Tannery, Campfire) - such a recipe is never crafted instantly (instant tabs, search,
# Collections).
cpg.addMethod(CtNewMethod.make(f"""
public static boolean tableOnly({CRR} r) {{
  {BRQ}[] br = r.getBenchRequirement();
  if (br == null) return false;
  boolean any = false;
  for (int i = 0; i < br.length; i++) {{
    if (br[i] == null) continue;
    any = true;
    if (!retiredBench(br[i].id) && (br[i].type != {BTP}.Processing || instantProc(br[i].id))) return false;
  }}
  return any;
}}""", cpg))
# only == null -> every equipped bench except the timed ones (Furnace, Tannery and any Processing requirement but Salvagebench) and the
# retired ones (the merged Crafting / Smithing / Farming set); else just that bench. Up to the accessory tier.
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
      if (retiredBench(br[i].id)) continue;
      if (only == null) {{ if (separateBench(br[i].id) || (br[i].type == {BTP}.Processing && !instantProc(br[i].id))) continue; }}
      else if (!only.equalsIgnoreCase(br[i].id)) continue;
      int tier = accTier(acc, br[i].id);
      if (tier <= 0) continue;
      int need = br[i].requiredTierLevel; if (need <= 0) need = 1;
      if (need <= tier) {{ ids.add(r.getId()); break; }}
    }}
  }}
  return ids;
}}""", cpg))
# 0.7.3: tab ids are A:craft / A:smith / A:farm / P:<bench> / C: only (review fix: the legacy F: / B: ids are gone - buildTabs never emits
# them and build() replaces an unknown tab id with the first tab).
# 0.7.3: every recipe id the merged tabs can show (Fieldcraft + equipped non-timed benches); tabGroup() splits it into the three tabs
cpg.addMethod(CtNewMethod.make(f"""
public static java.util.TreeSet craftSet(java.util.UUID u) {{
  java.util.TreeSet ids = new java.util.TreeSet();
  java.util.Iterator fi = {FCC}.getAssetMap().getAssetMap().values().iterator();
  while (fi.hasNext()) {{
    {FCC} fc = ({FCC}) fi.next();
    java.util.Set fs = {CRP}.getAvailableRecipesForCategory("Fieldcraft", fc.getId());
    if (fs != null) ids.addAll(fs);
  }}
  ids.addAll(benchRecipes(u, (String) null));
  return ids;
}}""", cpg))
# 0.7.3 (Skyy's craft-page call): 2 = Farming (every Farmingbench recipe, farm tools included), 1 = Smithing (primary output Tool_*,
# Weapon_* or Armor_* - every material, wood and crude included), 0 = Crafting (everything else)
cpg.addMethod(CtNewMethod.make(f"""
public static int tabGroup({CRR} r) {{
  {BRQ}[] br = r.getBenchRequirement();
  for (int i = 0; br != null && i < br.length; i++) if (br[i] != null && "Farmingbench".equalsIgnoreCase(br[i].id)) return 2;
  {MQ} po = r.getPrimaryOutput();
  String id = po == null ? null : po.getItemId();
  if (id != null && (id.startsWith("Tool_") || id.startsWith("Weapon_") || id.startsWith("Armor_"))) return 1;
  return 0;
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public java.util.ArrayList buildTabs({PLA} p, java.util.UUID u, String k) {{
  java.util.ArrayList t = new java.util.ArrayList();
  java.util.HashMap acc = accessories(p, u);
  t.add(new String[] {{ "A:craft", "Crafting" }});
  t.add(new String[] {{ "A:smith", "Smithing" }});
  if (accTier(acc, "Farmingbench") > 0) t.add(new String[] {{ "A:farm", "Farming" }});
  // 0.7.4: the Campfire accessory (emergency cook through SkyyCooking) - its own tab, never merged
  if (campfireTier(u) > 0) t.add(new String[] {{ "K:camp", "Campfire" }});
  for (int i = 0; i < {PKG}.ProcStore.BENCHES.length; i++) {{
    String bn = {PKG}.ProcStore.BENCHES[i];
    if (accTier(acc, bn) > 0 || {PKG}.ProcStore.pending(k, bn)) t.add(new String[] {{ "P:" + bn, bn }});
  }}
  if (!collectionRecipes(u).isEmpty()) t.add(new String[] {{ "C:", "Collections" }});
  return t;
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public java.util.ArrayList recipesFor(String tabId, java.util.UUID u) {{
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.TreeSet ids = new java.util.TreeSet();
  int grp = -1;
  if (tabId.equals("A:craft")) grp = 0;
  else if (tabId.equals("A:smith")) grp = 1;
  else if (tabId.equals("A:farm")) grp = 2;
  if (grp >= 0) {{
    ids.addAll(craftSet(u));
  }} else if (tabId.startsWith("P:")) {{
    ids.addAll(benchRecipes(u, tabId.substring(2)));
  }} else if (tabId.startsWith("C:")) {{
    ids.addAll(collectionRecipes(u));
  }} else if (tabId.equals("K:camp")) {{
    ids.addAll(campRecipes(u));
  }}
  boolean timed = tabId.startsWith("P:");
  // 0.7.4: the Campfire tab is the ONE instant tab that shows Campfire (timed, retired-bench) recipes - campRecipes picked them
  boolean camp = tabId.equals("K:camp");
  java.util.Iterator ii = ids.iterator();
  while (ii.hasNext()) {{
    Object o = {CRR}.getAssetMap().getAsset(ii.next());
    if (!(o instanceof {CRR})) continue;
    {CRR} rc = ({CRR}) o;
    if (!timed && !camp && tableOnly(rc)) continue;
    if (camp && !campfireRecipe(rc)) continue;
    if (grp >= 0 && tabGroup(rc) != grp) continue;
    out.add(rc);
  }}
  return out;
}}""", cpg))
# 0.7.3 search: Crafting + Smithing + Farming together (the whole merged set), every typed word in the output item's name or id
cpg.addMethod(CtNewMethod.make(f"""
public java.util.ArrayList searchRecipes(java.util.UUID u, String q) {{
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.Iterator ii = craftSet(u).iterator();
  while (ii.hasNext()) {{
    Object o = {CRR}.getAssetMap().getAsset(ii.next());
    if (!(o instanceof {CRR})) continue;
    {CRR} rc = ({CRR}) o;
    if (tableOnly(rc)) continue;
    {MQ} po = rc.getPrimaryOutput();
    if (nameMatches(q, po == null ? String.valueOf(rc.getId()) : po.getItemId())) out.add(rc);
  }}
  return out;
}}""", cpg))
# 0.7.3 bench-aware mirror for the craft page: what the shown recipes (view), the clicked recipe (craft / queue) or the loaded fuel can use
cpg.addMethod(CtNewMethod.make(f"""
public static java.util.HashSet wantedOf(java.util.List recipes) {{
  java.util.HashSet s = new java.util.HashSet();
  for (int i = 0; recipes != null && i < recipes.size(); i++) {{
    Object o = recipes.get(i);
    if (o instanceof {CRR}) {PKG}.BagMirror.addInputs(s, (({CRR}) o).getInput());
  }}
  return s;
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static java.util.HashSet wantedOne({CRR} r) {{
  java.util.HashSet s = new java.util.HashSet();
  if (r != null) {PKG}.BagMirror.addInputs(s, r.getInput());
  return s;
}}""", cpg))
cpg.addMethod(CtNewMethod.make("""
public static java.util.HashSet procWanted(java.util.List recipes) {
  java.util.HashSet s = wantedOf(recipes);
  s.add("Fuel");
  return s;
}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static {CIC} materialsFor({PLA} p, String k, java.util.Set wanted) {{
  {PKG}.BagMirror m = {PKG}.BagMirror.of(k);
  m.sync();
  m.rebuild({PKG}.SweepTask.caps(p.getInventory()), wanted);
  return new {CIC}(new {IC}[] {{ p.getInventory().getCombinedBackpackStorageHotbar(), m.cont }});
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static {CIC} materials({PLA} p, String k) {{
  return materialsFor(p, k, (java.util.Set) null);
}}""", cpg))
# 0.7.2 review fix: counts for the page VIEW. While a profile switch settles (this.settling, set by build() from
# SackPool.settledKey) only the inventory is counted and no BagMirror is built or synced for the not-yet-settled key; every
# click that moves items calls materialsFor(p, k, ...) itself with the one settled key it checked.
cpg.addMethod(CtNewMethod.make(f"""
public {CIC} viewMats({PLA} p, String k, java.util.Set wanted) {{
  if (this.settling) return new {CIC}(new {IC}[] {{ p.getInventory().getCombinedBackpackStorageHotbar() }});
  return materialsFor(p, k, wanted);
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static int limit({CRR} r, {IC} c) {{
  {MQ}[] in = r.getInput();
  if (in == null || in.length == 0) return 0;
  int lim = Integer.MAX_VALUE;
  for (int i = 0; i < in.length; i++) {{
    int q = in[i].getQuantity(); if (q <= 0) continue;
    int have = c.countRemovableMaterial(in[i]);
    int l = have / q;
    if (l < lim) lim = l;
  }}
  return lim == Integer.MAX_VALUE ? 0 : lim;
}}""", cpg))
# ---- 0.7.0 processing helpers (Furnace / Tannery tabs) ----
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
public static void saveSoon(String k) {{
  {PKG}.ProcStore.markDirty(k);
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
public static String procQueue({PLA} p, {ST} st, {REF} ref, String k, String bench, int tier, {CRR} r, int want) {{
  if ({PKG}.ProcStore.BROKEN.containsKey(k)) return "your " + bench + " data could not be loaded - nothing was taken";
  {PKG}.ProcBench pb = {PKG}.ProcStore.of(k, bench);
  long now = System.currentTimeMillis();
  pb.advance(now);
  int room = {PKG}.ProcBench.QUEUE_CAP - pb.queued();
  if (room <= 0) return "the " + bench + " queue is full (" + {PKG}.ProcBench.QUEUE_CAP + " units)";
  {CIC} mats = materialsFor(p, k, wantedOne(r));
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
  {PKG}.BagMirror m = {PKG}.BagMirror.of(k);
  int consumed = m.sync();
  saveSoon(k);
  {PKG}.CraftLog.line(k, "QUEUE " + bench + " " + r.getId() + " requested=" + qty + " queued=" + queuedN + " unitMs=" + unit + " tier=" + tier + " fromBags=" + consumed + audit);
  {MQ} outq = r.getPrimaryOutput();
  String nm = pretty(outq == null ? String.valueOf(r.getId()) : outq.getItemId());
  if (queuedN <= 0) return "could not take the materials - nothing was used";
  return "queued " + queuedN + " x " + nm + " in the " + bench + (queuedN < qty ? " (" + (qty - queuedN) + " fewer than asked - the rest was returned)" : "") + (consumed > 0 ? " - " + consumed + " from bags" : "");
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static String procFuel({PLA} p, {ST} st, {REF} ref, String k, String bench, String id) {{
  if ({PKG}.ProcStore.BROKEN.containsKey(k)) return "your " + bench + " data could not be loaded - nothing was taken";
  if ({PKG}.ProcBench.fuelQuality(id) <= 0.0) return pretty(id) + " does not burn";
  {PKG}.ProcBench pb = {PKG}.ProcStore.of(k, bench);
  pb.advance(System.currentTimeMillis());
  int room = {PKG}.ProcBench.FUEL_CAP - pb.fuelCount();
  if (room <= 0) return "the fuel slot is full (" + {PKG}.ProcBench.FUEL_CAP + " items)";
  {CIC} mats = materialsFor(p, k, java.util.Collections.singleton(id));
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
  {PKG}.BagMirror m = {PKG}.BagMirror.of(k);
  int consumed = m.sync();
  saveSoon(k);
  {PKG}.CraftLog.line(k, "FUEL " + bench + " " + id + " asked=" + n + " loaded=" + took + " count " + before + "->" + after + " fromBags=" + consumed);
  return took > 0 ? ("loaded " + took + " " + pretty(id) + " into the " + bench) : "could not take the fuel";
}}""", cpg))
# collect: storage first (getCombinedStorageHotbarBackpack), only what fits, verified by counting; the rest stays in the output slot
cpg.addMethod(CtNewMethod.make(f"""
public static String procCollect({PLA} p, {ST} st, {REF} ref, String k, String bench) {{
  {PKG}.ProcBench pb = {PKG}.ProcStore.get(k, bench);
  if (pb == null) return "nothing to collect yet";
  if (pb.advance(System.currentTimeMillis()) > 0) {PKG}.ProcStore.markDirty(k);
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
  saveSoon(k);
  {PKG}.CraftLog.line(k, "COLLECT " + bench + " given=" + given + " left=" + left + audit);
  if (given == 0) return "your inventory is full - nothing collected";
  return "collected " + given + " items" + (left > 0 ? " - inventory full, " + left + " still waiting in the " + bench : "");
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static String procCancel({PLA} p, {ST} st, {REF} ref, String k, String bench) {{
  {PKG}.ProcBench pb = {PKG}.ProcStore.get(k, bench);
  if (pb == null) return "nothing queued";
  pb.advance(System.currentTimeMillis());
  if (pb.queued() <= 0) return "nothing queued";
  int n = pb.cancel();
  saveSoon(k);
  {PKG}.CraftLog.line(k, "CANCEL " + bench + " units=" + n + " (their inputs went to the output slot)");
  return "cancelled " + n + " units - " + procCollect(p, st, ref, k, bench);
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static String procUnload({PLA} p, {ST} st, {REF} ref, String k, String bench) {{
  {PKG}.ProcBench pb = {PKG}.ProcStore.get(k, bench);
  if (pb == null) return "no fuel loaded";
  pb.advance(System.currentTimeMillis());
  int n = pb.unloadFuel();
  if (n <= 0) return "no unburned fuel loaded";
  saveSoon(k);
  {PKG}.CraftLog.line(k, "UNLOAD " + bench + " fuel=" + n + " (to the output slot)");
  return "unloaded " + n + " fuel - " + procCollect(p, st, ref, k, bench);
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public void buildProc({UCB} b, {UEB} ev, {PLA} p, java.util.UUID u, String k) {{
  String bs = "Style: TextButtonStyle(Default: (Background: #1d3a5f, LabelStyle: (FontSize: 13, TextColor: #dceeff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #2f5a8f, LabelStyle: (FontSize: 13, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #0f2038, LabelStyle: (FontSize: 13, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  String on = "Style: TextButtonStyle(Default: (Background: #7fb0e0, LabelStyle: (FontSize: 13, TextColor: #06192a, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #a0c8f0, LabelStyle: (FontSize: 13, TextColor: #06192a, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #5f90c0, LabelStyle: (FontSize: 13, TextColor: #06192a, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  String bench = this.tab.substring(2);
  int tier = accTier(accessories(p, u), bench);
  boolean broken = {PKG}.ProcStore.BROKEN.containsKey(k);
  {PKG}.ProcBench pb = {PKG}.ProcStore.get(k, bench);
  if (pb != null && pb.advance(System.currentTimeMillis()) > 0) {PKG}.ProcStore.markDirty(k);
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
  java.util.ArrayList raw = (tier > 0 && !broken) ? recipesFor(this.tab, u) : new java.util.ArrayList();
  {CIC} mats = viewMats(p, k, procWanted(raw));
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
  b.appendInline("#SkyyCNav", "Label {{ Anchor: (Width: 8, Height: 34); Text: \\"\\"; }}");
  b.appendInline("#SkyyCNav", "TextButton #SkyyPRefresh {{ Anchor: (Width: 110, Height: 34); Text: \\"Refresh\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyPRefresh", {EVD}.of("a", "prefresh"));
}}""", cpg))
# 0.7.3: CraftPage.live() (the ~2 s Furnace / Tannery self-refresh from ProcTask) and its liveOn / liveSig / liveAt state are gone -
# periodic page updates make PageManager drop clicks; the tab has a Refresh button (handleProc "prefresh").
cpg.addMethod(CtNewMethod.make(f"""
public boolean handleProc({REF} ref, {ST} st, {PLA} p, java.util.UUID u, String k, String data) {{
  if (this.tab == null || !this.tab.startsWith("P:")) return false;
  String bench = this.tab.substring(2);
  if (data.indexOf("\\"prefresh\\"") >= 0) {{ this.info = ""; rebuild(); return true; }}
  if (data.indexOf("\\"pcollect\\"") >= 0) {{ this.info = procCollect(p, st, ref, k, bench); rebuild(); return true; }}
  if (data.indexOf("\\"pcancel\\"") >= 0) {{ this.info = procCancel(p, st, ref, k, bench); rebuild(); return true; }}
  if (data.indexOf("\\"punload\\"") >= 0) {{ this.info = procUnload(p, st, ref, k, bench); rebuild(); return true; }}
  int f = data.indexOf("pfuel:");
  if (f >= 0) {{
    int e = data.indexOf('\\"', f);
    int i = Integer.parseInt(data.substring(f + 6, e));
    if (this.fuelIds != null && i >= 0 && i < this.fuelIds.length && this.fuelIds[i] != null) this.info = procFuel(p, st, ref, k, bench, this.fuelIds[i]);
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
      else this.info = procQueue(p, st, ref, k, bench, tier, ({CRR}) this.rows.get(idx), want);
    }}
    rebuild();
    return true;
  }}
  return false;
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
  String bs = "Style: TextButtonStyle(Default: (Background: #1d3a5f, LabelStyle: (FontSize: 13, TextColor: #dceeff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #2f5a8f, LabelStyle: (FontSize: 13, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #0f2038, LabelStyle: (FontSize: 13, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  String on = "Style: TextButtonStyle(Default: (Background: #7fb0e0, LabelStyle: (FontSize: 13, TextColor: #06192a, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #a0c8f0, LabelStyle: (FontSize: 13, TextColor: #06192a, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #5f90c0, LabelStyle: (FontSize: 13, TextColor: #06192a, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  b.appendInline((String) null, "Group #SkyyCraft {{ Anchor: (Width: 1000, Height: 830); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyyCraft", "Group {{ Anchor: (Height: 2); Background: #7fb0e0; }}");
  b.appendInline("#SkyyCraft", "Label {{ Anchor: (Height: 34); Text: \\"Crafting\\"; Style: (FontSize: 19, RenderBold: true, TextColor: #e6f2ff, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  this.key = null;
  this.settling = false;
  if (p == null) return;
  String k = {PKG}.SackPool.settledKey(u);
  if (k == null) {{
    this.settling = true;
    k = {PKG}.SackPool.pkey(u);
    if (this.info == null || this.info.length() == 0) this.info = "bags paused (profile loading or switching) - bag counts come back in a moment";
  }} else if (this.info != null && this.info.startsWith("bags paused")) this.info = "";
  this.key = k;
  this.tabs = buildTabs(p, u, k);
  boolean known = false;
  for (int i = 0; this.tab != null && i < this.tabs.size(); i++) if (this.tab.equals(((String[]) this.tabs.get(i))[0])) known = true;
  if (!known && this.tabs.size() > 0) {{ this.tab = ((String[]) this.tabs.get(0))[0]; this.pageNo = 0; }}
  // 0.7.3: a search shows Crafting + Smithing + Farming results together, so no tab is highlighted while it is active
  boolean searching = this.query != null && this.query.length() > 0 && this.tab != null && this.tab.startsWith("A:");
  int tabRow = 0; int inRow = 0;
  b.appendInline("#SkyyCraft", "Group #SkyyCTabs0 {{ Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 4); }}");
  b.appendInline("#SkyyCTabs0", "TextButton #SkyyCBags {{ Anchor: (Width: 150, Height: 32); Text: \\"< Back to bags\\"; " + bs + " }}");
  b.appendInline("#SkyyCTabs0", "Label {{ Anchor: (Width: 14, Height: 32); Text: \\"\\"; }}");
  ev.addEventBinding({BT}.Activating, "#SkyyCBags", {EVD}.of("a", "bags"));
  for (int i = 0; i < this.tabs.size(); i++) {{
    int cap = tabRow == 0 ? 6 : 8;
    if (inRow >= cap) {{ tabRow++; inRow = 0; b.appendInline("#SkyyCraft", "Group #SkyyCTabs" + tabRow + " {{ Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 4); }}"); }}
    String[] t = (String[]) this.tabs.get(i);
    boolean sel = t[0].equals(this.tab) && !searching;
    b.appendInline("#SkyyCTabs" + tabRow, "TextButton #SkyyCTab" + i + " {{ Anchor: (Width: 110, Height: 32); Text: \\"" + {PKG}.SacksPage.safe(t[1]) + "\\"; " + (sel ? on : bs) + " }}");
    b.appendInline("#SkyyCTabs" + tabRow, "Label {{ Anchor: (Width: 6, Height: 32); Text: \\"\\"; }}");
    ev.addEventBinding({BT}.Activating, "#SkyyCTab" + i, {EVD}.of("a", "tab:" + i));
    inRow++;
  }}
  // 0.7.3 search row (Crafting / Smithing / Farming tabs): inline TextField (vanilla PluginListPage / Common.ui @TextField keys only),
  // Enter (Validating) or Search sends "@SearchQuery" = the field's Value; the rebuild puts the query back with set("#SkyyCSearch.Value").
  // craftSearch=false in config.properties leaves the TextField out (a /craft <words> search still shows its Clear button).
  boolean srow = false;
  if (this.tab != null && this.tab.startsWith("A:") && ({PKG}.SackCfg.SEARCH.get() || searching)) {{
    srow = true;
    b.appendInline("#SkyyCraft", "Group #SkyyCSearchRow {{ Anchor: (Height: 42); LayoutMode: Left; Padding: (Top: 4); }}");
    if ({PKG}.SackCfg.SEARCH.get()) {{
      b.appendInline("#SkyyCSearchRow", "Group #SkyyCSearchBox {{ Anchor: (Width: 420, Height: 34); Background: #16263a; }}");
      b.appendInline("#SkyyCSearchBox", "TextField #SkyyCSearch {{ Anchor: (Full: 0); Padding: (Horizontal: 10); MaxLength: 40; PlaceholderText: \\"Search items - type a name and press Enter\\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 14); Style: (TextColor: #ffffff, FontSize: 14); }}");
      if (searching) b.set("#SkyyCSearch.Value", this.query);
      b.appendInline("#SkyyCSearchRow", "Label {{ Anchor: (Width: 8, Height: 34); Text: \\"\\"; }}");
      b.appendInline("#SkyyCSearchRow", "TextButton #SkyyCSearchGo {{ Anchor: (Width: 100, Height: 34); Text: \\"Search\\"; " + bs + " }}");
      b.appendInline("#SkyyCSearchRow", "Label {{ Anchor: (Width: 6, Height: 34); Text: \\"\\"; }}");
      ev.addEventBinding({BT}.Validating, "#SkyyCSearch", {EVD}.of("a", "csearch").append("@SearchQuery", "#SkyyCSearch.Value"), false);
      ev.addEventBinding({BT}.Activating, "#SkyyCSearchGo", {EVD}.of("a", "csearch").append("@SearchQuery", "#SkyyCSearch.Value"));
    }}
    b.appendInline("#SkyyCSearchRow", "TextButton #SkyyCSearchClear {{ Anchor: (Width: 90, Height: 34); Text: \\"Clear\\"; " + bs + " }}");
    ev.addEventBinding({BT}.Activating, "#SkyyCSearchClear", {EVD}.of("a", "cclear"));
    b.appendInline("#SkyyCSearchRow", "Label #SkyyCSearchInfo {{ Anchor: (Width: 330, Height: 34); Text: \\"\\"; Style: (FontSize: 13, TextColor: #9fb8d0, VerticalAlignment: Center); }}");
  }}
  b.appendInline("#SkyyCraft", "Label {{ Anchor: (Height: 22); Text: \\"Materials are counted from your inventory and your magic bags.\\"; Style: (FontSize: 13, TextColor: #9fb8d0, HorizontalAlignment: Center); }}");
  // 0.7.4 Campfire tab: the emergency-cook line (text by set(), so the comma and colon are safe - the search info label pattern)
  boolean campTab = this.tab != null && this.tab.equals("K:camp");
  if (campTab) {{
    b.appendInline("#SkyyCraft", "Label #SkyyCCampNote {{ Anchor: (Height: 24); Text: \\"\\"; Style: (FontSize: 14, RenderBold: true, TextColor: #ffc080, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    b.set("#SkyyCCampNote.Text", campNote());
  }}
  if (this.tab != null && this.tab.startsWith("P:")) {{ buildProc(b, ev, p, u, k); return; }}
  java.util.ArrayList raw = this.tab == null ? new java.util.ArrayList() : (searching ? searchRecipes(u, this.query) : recipesFor(this.tab, u));
  {CIC} mats = viewMats(p, k, wantedOf(raw));
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
  int per = 9;
  int pages = (this.rows.size() + per - 1) / per; if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1; if (this.pageNo < 0) this.pageNo = 0;
  int start = this.pageNo * per;
  for (int i = start; i < this.rows.size() && i < start + per; i++) {{
    {CRR} r = ({CRR}) this.rows.get(i);
    {MQ} outq = r.getPrimaryOutput();
    String outId = outq == null ? "?" : outq.getItemId();
    int lim = limit(r, mats);
    // 0.7.4: what a Campfire-tab craft gives right now (cook:fn:campfire preview - no XP, no chat)
    String cnote = campTab ? campRowNote(p, u, k, r) : "";
    StringBuilder need = new StringBuilder();
    {MQ}[] in = r.getInput();
    for (int k = 0; in != null && k < in.length; k++) {{
      if (need.length() > 0) need.append("   ");
      String nm = in[k].getItemId() != null ? pretty(in[k].getItemId()) : (in[k].getResourceTypeId() != null ? in[k].getResourceTypeId() : "?");
      need.append(nm).append(" ").append(mats.countRemovableMaterial(in[k])).append("/").append(in[k].getQuantity());
    }}
    b.appendInline("#SkyyCraft", "Group #SkyyCRow" + i + " {{ Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); " + (lim > 0 ? "Background: #10233a(0.9); " : "Background: #0e1826(0.6); ") + "}}");
    b.appendInline("#SkyyCRow" + i, "Group {{ Anchor: (Width: 56, Height: 54); ItemIcon {{ Anchor: (Width: 46, Height: 46, Left: 5, Top: 4); ItemId: \\"" + {PKG}.SacksPage.safe(outId) + "\\"; }} }}");
    b.appendInline("#SkyyCRow" + i, "Group #SkyyCTxt" + i + " {{ Anchor: (Width: 600, Height: 54); LayoutMode: Top; }}");
    b.appendInline("#SkyyCTxt" + i, "Label {{ Anchor: (Height: 27); Text: \\"" + {PKG}.SacksPage.safe(pretty(outId) + (outq != null && outq.getQuantity() > 1 ? " x" + outq.getQuantity() : "") + cnote) + "\\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + (lim > 0 ? "#ffffff" : "#8a97a8") + ", VerticalAlignment: Center); }}");
    b.appendInline("#SkyyCTxt" + i, "Label {{ Anchor: (Height: 23); Text: \\"" + {PKG}.SacksPage.safe(need.toString()) + "\\"; Style: (FontSize: 12, TextColor: " + (lim > 0 ? "#9fd8a2" : "#c07070") + ", VerticalAlignment: Center); }}");
    b.appendInline("#SkyyCRow" + i, "TextButton #SkyyCCraft" + i + " {{ Anchor: (Width: 82, Height: 34); Text: \\"Craft\\"; " + bs + " }}");
    b.appendInline("#SkyyCRow" + i, "Label {{ Anchor: (Width: 6, Height: 34); Text: \\"\\"; }}");
    b.appendInline("#SkyyCRow" + i, "TextButton #SkyyCTen" + i + " {{ Anchor: (Width: 66, Height: 34); Text: \\"x10\\"; " + bs + " }}");
    b.appendInline("#SkyyCRow" + i, "Label {{ Anchor: (Width: 6, Height: 34); Text: \\"\\"; }}");
    b.appendInline("#SkyyCRow" + i, "TextButton #SkyyCAll" + i + " {{ Anchor: (Width: 76, Height: 34); Text: \\"All " + lim + "\\"; " + bs + " }}");
    ev.addEventBinding({BT}.Activating, "#SkyyCCraft" + i, {EVD}.of("a", "craft:" + i + ":1"));
    ev.addEventBinding({BT}.Activating, "#SkyyCTen" + i, {EVD}.of("a", "craft:" + i + ":10"));
    ev.addEventBinding({BT}.Activating, "#SkyyCAll" + i, {EVD}.of("a", "craft:" + i + ":0"));
  }}
  if (this.rows.size() == 0) b.appendInline("#SkyyCraft", "Label {{ Anchor: (Height: 30); Text: \\"" + {PKG}.SacksPage.safe(searching ? ("Nothing matches " + this.query + " in Crafting, Smithing or Farming.") : (campTab ? "No campfire dishes are loaded." : "No recipes here yet.")) + "\\"; Style: (FontSize: 15, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  if (srow) b.set("#SkyyCSearchInfo.Text", searching ? ("  " + this.rows.size() + " found in Crafting, Smithing and Farming") : "  searches Crafting, Smithing and Farming");
  b.appendInline("#SkyyCraft", "Label #SkyyCInfo {{ Anchor: (Height: 26); Text: \\"" + {PKG}.SacksPage.safe(this.info) + "\\"; Style: (FontSize: 14, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyCraft", "Group #SkyyCNav {{ Anchor: (Height: 42); LayoutMode: Left; Padding: (Top: 6); }}");
  b.appendInline("#SkyyCNav", "TextButton #SkyyCPrev {{ Anchor: (Width: 92, Height: 34); Text: \\"< Prev\\"; " + bs + " }}");
  b.appendInline("#SkyyCNav", "Label {{ Anchor: (Width: 160, Height: 34); Text: \\"Page " + (this.pageNo + 1) + " / " + pages + "\\"; Style: (FontSize: 13, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyCNav", "TextButton #SkyyCNext {{ Anchor: (Width: 92, Height: 34); Text: \\"Next >\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyCPrev", {EVD}.of("a", "prev"));
  ev.addEventBinding({BT}.Activating, "#SkyyCNext", {EVD}.of("a", "next"));
  b.appendInline("#SkyyCNav", "Label {{ Anchor: (Width: 40, Height: 34); Text: \\"\\"; }}");
  b.appendInline("#SkyyCNav", "TextButton #SkyyCOnly {{ Anchor: (Width: 230, Height: 34); Text: \\"Craftable only: " + (Boolean.TRUE.equals(ONLY.get(u)) ? "ON" : "OFF") + "\\"; " + (Boolean.TRUE.equals(ONLY.get(u)) ? on : bs) + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyCOnly", {EVD}.of("a", "onlyc"));
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    // 0.7.3 search: only the search bindings carry "@SearchQuery" (the typed text), so it is handled before any payload match -
    // typed words can never be read as another button's payload
    if (data.indexOf("\\"@SearchQuery\\"") >= 0) {{
      this.query = cleanQuery(jsonStr(data, "@SearchQuery"));
      this.pageNo = 0;
      this.info = this.query.length() == 0 ? "type a word (for example iron or sword) and press Enter or Search" : "";
      rebuild();
      return;
    }}
    if (data.indexOf("\\"cclear\\"") >= 0) {{ this.query = ""; this.pageNo = 0; this.info = ""; rebuild(); return; }}
    if (data.indexOf("\\"prev\\"") >= 0) {{ this.pageNo--; rebuild(); return; }}
    if (data.indexOf("\\"next\\"") >= 0) {{ this.pageNo++; rebuild(); return; }}
    if (data.indexOf("\\"onlyc\\"") >= 0) {{ if (Boolean.TRUE.equals(ONLY.get(u))) ONLY.remove(u); else ONLY.put(u, Boolean.TRUE); this.pageNo = 0; rebuild(); return; }}
    {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (p == null) return;
    if (data.indexOf("\\"bags\\"") >= 0) {{ p.getPageManager().openCustomPage(ref, st, new {PKG}.SacksPage(this.playerRef, (String) null)); return; }}
    for (int i = 0; this.tabs != null && i < this.tabs.size(); i++) {{
      if (data.indexOf("tab:" + i + "\\"") >= 0) {{ this.tab = ((String[]) this.tabs.get(i))[0]; this.pageNo = 0; this.info = ""; this.query = ""; rebuild(); return; }}
    }}
    String k = {PKG}.SackPool.settledKey(u);
    if (k == null) {{ this.info = "bags paused (profile loading or switching) - try again in a moment"; rebuild(); return; }}
    if (this.key != null && !this.key.equals(k)) {{ this.info = "your profile changed - this page now shows it"; this.pageNo = 0; rebuild(); return; }}
    if (handleProc(ref, st, p, u, k, data)) return;
    int c = data.indexOf("craft:");
    if (c < 0) return;
    int e = data.indexOf('\\"', c);
    String[] parts = data.substring(c + 6, e).split(":");
    int idx = Integer.parseInt(parts[0]); int want = Integer.parseInt(parts[1]);
    if (this.rows == null || idx < 0 || idx >= this.rows.size()) return;
    {CRR} r = ({CRR}) this.rows.get(idx);
    // 0.7.4 Campfire tab: still equipped and still a Campfire-bench recipe at click time (acc:has can change while the page is open)
    boolean campTab = "K:camp".equals(this.tab);
    if (campTab && (campfireTier(u) <= 0 || !campfireRecipe(r))) {{ this.info = "equip the Campfire accessory in your accessory bag to cook here"; rebuild(); return; }}
    {CIC} mats = materialsFor(p, k, wantedOne(r));
    int lim = limit(r, mats);
    int qty = want == 0 ? lim : (want < lim ? want : lim);
    if (qty <= 0) {{ this.info = "not enough materials"; rebuild(); return; }}
    java.util.List inputs = {CRM}.getInputMaterials(r, qty);
    int n = inputs == null ? 0 : inputs.size();
    if (n == 0) {{ this.info = "this recipe has no inputs"; rebuild(); return; }}
    if (!mats.canRemoveMaterials(inputs)) {{ this.info = "not enough materials"; rebuild(); return; }}
    java.util.HashMap snapB = snapshot(mats);
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
    {PKG}.BagMirror m = {PKG}.BagMirror.of(k);
    int consumed = m.sync();
    if (consumed > 0) {PKG}.SackPool.saveSoon(k);
    {MQ}[] outs = r.getOutputs();
    {MQ} outq = r.getPrimaryOutput();
    if ((outs == null || outs.length == 0) && outq != null) outs = new {MQ}[] {{ outq }};
    // 0.7.4: ONE cook:fn:campfire call per click, after the materials were removed, with the finished crafts and the settled key;
    // its String answer replaces the primary output id (same quantity). null = plain output. SkyyCooking pays the Cooking XP.
    String campId = null;
    if (campTab && done > 0) campId = campCall(p, u, k, r, done);
    int given = 0;
    if (done > 0 && outs != null) {{
      for (int k = 0; k < outs.length; k++) {{
        if (outs[k] == null || outs[k].getItemId() == null) continue;
        long total = (long) outs[k].getQuantity() * (long) done; if (total > 100000L) total = 100000L;
        String gid = outs[k].getItemId();
        if (campId != null && outq != null && gid.equals(outq.getItemId())) gid = campId;
        {SIC}.addOrDropItemStack(st, ref, p.getInventory().getCombinedStorageHotbarBackpack(), new {IS}(gid, (int) total));
        given += (int) total;
      }}
    }}
    if (campTab) audit.append(" campfire=").append(campId == null ? "plain" : campId);
    {PKG}.CraftLog.write(k, String.valueOf(r.getId()), qty, done, flag, given, audit.toString());
    // 0.7.3 (research/Alchemy-Skill-Spec.md 7.3 item 1): report crafts SkyySacks completed itself; SkyySkills decides the skill and
    // pays 0 for anything that is not an Alchemy / Furnace recipe (neither is left in /craft). No-op without SkyySkills 0.4.
    // 0.7.4: not for the Campfire tab - SkyyCooking pays its Cooking XP inside cook:fn:campfire (and without SkyyCooking it pays none)
    if (done > 0 && !campTab) {{
      try {{
        Object xf = {PKG}.SackPool.bridge().get("skill:fn:craftxp");
        if (xf instanceof java.util.function.Function) ((java.util.function.Function) xf).apply(new Object[] {{ u, String.valueOf(r.getId()), Integer.valueOf(done), "sacks:craft", k }});
      }} catch (Throwable t) {{ }}
    }}
    if (done > 0 && given == 0) {PKG}.SackPool.warn("craft: " + done + " crafts of " + r.getId() + " paid but the recipe has no item output (" + u + ")");
    String nm = pretty(outq == null ? "?" : outq.getItemId());
    if (campTab) {{ int cg = gradeOfId(campId); nm = nm + (cg > 0 ? " Grade " + cg : " (plain)"); }}
    if (done == qty) this.info = "crafted " + qty + " x " + nm + (consumed > 0 ? " (" + consumed + " from bags)" : "");
    else if (done > 0) this.info = "crafted " + done + " of " + qty + " x " + nm + " - extra materials were returned";
    else this.info = "could not remove the materials - nothing was used";
    rebuild();
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("craft page event failed: " + t); }}
}}""", cpg))

# 0.7.2: the active profile changed while the craft page is open (ProcTask, world thread): one set() per profile change, never
# periodic; the next click rebuilds the page for the new profile.
cpg.addMethod(CtNewMethod.make(f"""
public void profileNotice(String k) {{
  if (this.key == null || k == null || k.equals(this.noticeKey)) return;
  this.noticeKey = k;
  {UCB} c = new {UCB}();
  c.set("#SkyyCInfo.Text", "Your profile changed - click a tab to refresh this page");
  sendUpdate(c, false);
}}""", cpg))

# ================= CraftCmd (/craft) =================
ccmd.addConstructor(CtNewConstructor.make("""
public CraftCmd() {
  super("craft", "Open inventory crafting (materials from your inventory and your magic bags) - /craft <words> opens it searching");
  addAliases(new String[] { "recipes" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  setAllowsExtraArguments(true);
}""", ccmd))
# 0.7.3: words after /craft (or /recipes) open the page already searching (SkyyRolls 0.1.2 pattern: extra arguments allowed, the words read
# from ctx.getInputString(); a leading command word is dropped). Works when craftSearch=false hides the search box.
ccmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    String line = "";
    try {{ line = ctx.getInputString(); }} catch (Throwable t) {{ line = ""; }}
    if (line == null) line = "";
    String q = line.trim();
    if (q.startsWith("/")) q = q.substring(1).trim();
    int sp = q.indexOf(' ');
    String head = (sp < 0 ? q : q.substring(0, sp)).toLowerCase();
    if (head.equals("craft") || head.equals("recipes")) q = sp < 0 ? "" : q.substring(sp + 1);
    {PKG}.CraftPage cp = new {PKG}.CraftPage(pr, (String) null);
    cp.query = {PKG}.CraftPage.cleanQuery(q);
    player.getPageManager().openCustomPage(ref, store, cp);
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("/craft failed: " + t); pr.sendMessage({MSG}.raw("[SkyySacks] could not open crafting")); }}
}}""", ccmd))

# ================= CraftPageFactory (OpenCustomUI page ids -> craft page on a tab) =================
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
ptk.addField(CtField.make("public static long XPWARN;", ptk))
ptk.addField(CtField.make("public static final int XP_CALL = 1000;", ptk))
ptk.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();", ptk))
ptk.addConstructor(CtNewConstructor.make(f"public ProcTask({PR} pr, java.util.UUID w) {{ this.pr = pr; this.expectedWorld = w; }}", ptk))
# 0.7.2 profile contract rule 3: remember the last profile:epoch:<uuid> seen per player. SkyySacks publishes no per-player bridge
# values, so "republish" = flush every dirty pool/processing file (the old profile's included) off the world thread right away and
# log the switch; an open page built for another key is told in run(). Without SkyyProfiles the epoch stays absent: never fires.
# Integration fix: an absent epoch (-1) is not remembered, so the first published value is a baseline (contract 4.2), not a change.
# Review fix: the log line is queued (CraftLog.later) BEFORE the SackSaver is scheduled, which writes it off the world thread.
ptk.addMethod(CtNewMethod.make(f"""
public static boolean epochCheck(java.util.UUID u, String k) {{
  long ep = {PKG}.SackPool.epoch(u);
  if (ep < 0L) return false;
  Long last = (Long) EPOCH.put(u, Long.valueOf(ep));
  if (last == null || last.longValue() == ep) return false;
  {PKG}.CraftLog.later(k, "PROFILE epoch " + last + " -> " + ep + " - bags, furnace and tannery now use this key");
  try {{ {HSV}.SCHEDULED_EXECUTOR.execute(new {PKG}.SackSaver()); }} catch (Throwable t) {{ }}
  return true;
}}""", ptk))
# 0.7.3 Smithing (research/Smithing-Smelting-Spec.md 4.1, research/Alchemy-Skill-Spec.md 7.2): pay the Furnace units ProcBench.finishUnit
# counted, once per recipe per run, through SkyySkills' skill:fn:craftxp {uuid, recipeId, count, "sacks:furnace", expectKey}. Only when the
# key this run advanced is the settled key (a switch has settled; the same gate as the bench link). A Number answer drains exactly the
# reported count (units finished meanwhile stay); no function (SkyySkills missing or older than 0.4) or an error keeps the ledger.
# At most XP_CALL units per call (the rest goes on the next 1 s run): SkyySkills answers 0 (= drop it) for a call over its
# bridge.maxXpPerCall (500k base XP, checked before its multiplier), so a big ledger (up to XP_CAP = 10,000 units of a
# 50 XP bar, or a raised smithing.xp.* value) must never go out in one call and be dropped.
# The bridge call runs with no lock of ours held (xpList / takeXp are separate synchronized calls).
ptk.addMethod(CtNewMethod.make(f"""
public static void drainXp(java.util.UUID u, String k, {PKG}.ProcBench pb) {{
  java.util.ArrayList l = pb.xpList();
  if (l.isEmpty()) return;
  if (!k.equals({PKG}.SackPool.settledKey(u))) return;
  Object f = {PKG}.SackPool.bridge().get("skill:fn:craftxp");
  if (!(f instanceof java.util.function.Function)) return;
  for (int i = 0; i < l.size(); i++) {{
    Object[] e = (Object[]) l.get(i);
    String recipe = (String) e[0];
    int n = ((Integer) e[1]).intValue();
    if (n <= 0) continue;
    if (n > XP_CALL) n = XP_CALL;
    Object got = null;
    try {{
      got = ((java.util.function.Function) f).apply(new Object[] {{ u, recipe, Integer.valueOf(n), "sacks:furnace", k }});
    }} catch (Throwable t) {{
      long now = System.currentTimeMillis();
      if (now - XPWARN > 60000L) {{ XPWARN = now; {PKG}.SackPool.warn("smithing xp: skill:fn:craftxp failed (ledger kept, retried): " + t); }}
      return;
    }}
    if (got instanceof Number) {{
      pb.takeXp(recipe, n);
      {PKG}.ProcStore.markDirty(k);
      {PKG}.CraftLog.later(k, "SMITHING " + recipe + " x" + n + " -> " + ((Number) got).longValue() + " xp");
    }}
  }}
}}""", ptk))
ptk.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (pr == null || !pr.isValid()) return;
    java.util.UUID nowWorld = pr.getWorldUuid();
    if (nowWorld == null || !nowWorld.equals(this.expectedWorld)) return;
    java.util.UUID u = pr.getUuid();
    String k = {PKG}.SackPool.pkey(u);
    epochCheck(u, k);
    java.util.Map m = null;
    if (!{PKG}.ProcStore.BROKEN.containsKey(k)) m = {PKG}.ProcStore.all(k);
    long now = System.currentTimeMillis();
    java.util.Iterator it = m == null ? java.util.Collections.EMPTY_LIST.iterator() : m.values().iterator();
    while (it.hasNext()) {{
      {PKG}.ProcBench pb = ({PKG}.ProcBench) it.next();
      int had = pb.queued();
      int d = pb.advance(now);
      if (d > 0) {PKG}.ProcStore.markDirty(k);
      if (had > 0 && pb.queued() == 0) {{
        String[] ds = pb.describe(0, true);
        pr.sendMessage({MSG}.raw("[SkyySacks] Your " + pb.bench + " is done. " + ds[3] + " - open /craft to collect."));
        {PKG}.CraftLog.line(k, "DONE " + pb.bench + " queue finished - " + ds[3]);
      }} else if (pb.fuelWarnOnce()) {{
        pr.sendMessage({MSG}.raw("[SkyySacks] Your " + pb.bench + " ran out of fuel - load more in /craft."));
      }}
    }}
    if (m != null) {{
      Object fo = m.get("Furnace");
      if (fo instanceof {PKG}.ProcBench) drainXp(u, k, ({PKG}.ProcBench) fo);
    }}
    {REF} r = pr.getReference();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    if (p == null) return;
    Object pg = p.getPageManager().getCustomPage();
    if (pg instanceof {PKG}.CraftPage) {{
      {PKG}.CraftPage cp = ({PKG}.CraftPage) pg;
      if (cp.key != null && !cp.key.equals(k)) cp.profileNotice(k);
    }} else if (pg instanceof {PKG}.SacksPage) {{
      {PKG}.SacksPage sk = ({PKG}.SacksPage) pg;
      if (sk.key != null && !sk.key.equals(k)) sk.profileNotice(k);
    }}
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

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture saver;", pl))
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture crafter;", pl))
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture procTicker;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyySacksPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.SackPool.LOG = getLogger();
  {PKG}.SackPool.DIR = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("pools");
  {PKG}.CraftLog.FILE = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("crafts.log");
  {PKG}.ProcStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("processing");
  {PKG}.SackCfg.FILE = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("config.properties");
  {PKG}.SackCfg.reload();
  getCommandRegistry().registerCommand(new {PKG}.SacksCmd());
  getCommandRegistry().registerCommand(new {PKG}.CraftCmd());
  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacks", new {PKG}.SacksPageFactory((String) null));
  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksMining", new {PKG}.SacksPageFactory("Mining"));
  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksForaging", new {PKG}.SacksPageFactory("Foraging"));
  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksFarming", new {PKG}.SacksPageFactory("Farming"));
  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksCombat", new {PKG}.SacksPageFactory("Combat"));
  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksCraft", new {PKG}.CraftPageFactory((String) null));
  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksAlchemy", new {PKG}.CraftPageFactory("A:craft"));
  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksFurnace", new {PKG}.CraftPageFactory("P:Furnace"));
  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksTannery", new {PKG}.CraftPageFactory("P:Tannery"));
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SackTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
  this.saver = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SackSaver(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);
  this.crafter = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.CraftTick(), 1000L, 300L, java.util.concurrent.TimeUnit.MILLISECONDS);
  this.procTicker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.ProcTick(), 3L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyySacks] {VERSION} ready - /pd, /craft (Crafting, Smithing, Farming, Campfire accessory tab - emergency cook graded by SkyyCooking cook:fn:campfire, search, timed Furnace/Tannery queues - Furnace pays Smithing XP, Collections), right-click a magic bag; benches craft from your bags (their ingredients first); storage per profile (pkey)");
}}""", pl))
pl.addMethod(CtNewMethod.make(f"""
protected void shutdown() {{
  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
  try {{ if (this.saver != null) this.saver.cancel(false); }} catch (Throwable t) {{ }}
  try {{ if (this.crafter != null) this.crafter.cancel(false); }} catch (Throwable t) {{ }}
  try {{ if (this.procTicker != null) this.procTicker.cancel(false); }} catch (Throwable t) {{ }}
  try {{ int c = {PKG}.BagMirror.syncAll(); if (c > 0) {PKG}.SackPool.warn("shutdown: " + c + " bag items used by open benches debited"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.ProcStore.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackPool.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CraftLog.drain(); }} catch (Throwable t) {{ }}
  super.shutdown();
}}""", pl))

for c in (defs, sp, scfg, pjob, pben, pst, swp, tick, sav, cmp, page, cmd, fac, mir, clt, ctk, rcmp, clog, cpg, ccmd, cfac, ptk, ptick, pl):
    c.writeFile(OUT)
print("classes written")

# ================= assets =================
# (0.7.3 review fix: the dead pre-inline bag page markup - underscore ids, never shipped - was deleted; every page is built inline)

def sack_item(cat, tier, quality, recipe_in):
    return {
      "TranslationProperties": {"Name": "server.items.Skyy_Sack_%s_%s.name" % (cat, tier), "Description": "server.items.Skyy_Sack_%s_%s.description" % (cat, tier)},
      "Categories": ["Items.Tools"],
      "Icon": "Icons/ItemsGenerated/Utility_Bag_Seed.png",
      "Quality": quality,
      "Recipe": {"Input": recipe_in, "BenchRequirement": [{"Type": "Crafting", "Id": "Workbench", "Categories": ["Workbench_Crafting"]}]},
      "Model": "Items/Back/BackpackBig.blockymodel",
      "Texture": "Items/Back/BackpackBig_Texture.png",
      "IconProperties": {"Scale": 0.455, "Translation": [1.19, 2.39], "Rotation": [0, 177.73, 0]},
      "Tags": {"Family": ["Leather"], "Type": ["Utility"]},
      "MaxStack": 1,
      "Interactions": {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": "SkyySacks" + cat}}]}}
    }
files = {}  # pages are built inline (no .ui files: see memory hytale-ui-rules)
lang = []
mats = {"Mining": "Ingredient_Bar_Copper", "Foraging": "Wood_Oak_Trunk", "Farming": "Food_Bread", "Combat": "Ingredient_Bone_Fragment"}
for cat in ("Mining", "Foraging", "Farming", "Combat"):
    items = {
        "Small":  sack_item(cat, "Small", "Common",   [{"ItemId": "Ingredient_Bolt_Wool", "Quantity": 3}, {"ItemId": mats[cat], "Quantity": 4}]),
        "Medium": sack_item(cat, "Medium", "Uncommon", [{"ItemId": "Skyy_Sack_%s_Small" % cat, "Quantity": 1}, {"ItemId": "Ingredient_Bolt_Linen", "Quantity": 3}]),
        "Large":  sack_item(cat, "Large", "Rare",     [{"ItemId": "Skyy_Sack_%s_Medium" % cat, "Quantity": 1}, {"ItemId": "Ingredient_Bolt_Silk", "Quantity": 3}]),
    }
    for tier, node in items.items():
        files["Server/Item/Items/Utility/Skyy_Sack_%s_%s.json" % (cat, tier)] = json.dumps(node, indent=2)
        lang.append("items.Skyy_Sack_%s_%s.name=%s %s Bag" % (cat, tier, tier, cat))
        lang.append("server.items.Skyy_Sack_%s_%s.name=%s %s Bag" % (cat, tier, tier, cat))
        caps = {"Small": 640, "Medium": 2240, "Large": 20160}[tier]
        what = {"Mining": "ore, rubble, rock and soil", "Foraging": "logs, planks, sticks, fibre and bark", "Farming": "plants, food and cooked dishes, fish and life essence", "Combat": "bones, hides, feathers, essences, venom sacs, chitin and fabric scraps"}[cat]
        desc = "A magic bag that opens onto your pocket dimension. Holds up to %s of each %s item (%s). Matching items in your storage are pulled in automatically. Right-click to reach in. You need a bag on you to reach in, but nothing is ever lost." % (format(caps, ","), cat.lower(), what)
        lang.append("items.Skyy_Sack_%s_%s.description=%s" % (cat, tier, desc))
        lang.append("server.items.Skyy_Sack_%s_%s.description=%s" % (cat, tier, desc))
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"  # key items.<Id>.name in server.lang (pattern from Tamework)

jar = os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)
B.assemble(jar, B.manifest("SkyySacks", VERSION, "SkyBlock-style sacks: craft a sack, matching pickups pool automatically, /sacks to view and withdraw. Zero dependencies.", PKG + ".SkyySacksPlugin"), OUT, files)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyySacks.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyySacks" % VERSION, disable_prefix="Skyy:")
