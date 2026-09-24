"""SkyySacks 0.1.3 - build script (javassist via jpype).
Run:   python build_skyysacks_0.6.0.py            -> SkyySacks/SkyySacks-0.1.1.jar
       python build_skyysacks_0.6.0.py --deploy   -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world
Fixes vs 0.1 (code review 2026-09-22): no item loss/dupe - sweep removes exactly `take` from the slot via
removeItemStackFromSlot(slot, qty) and only credits the pool when the transaction succeeded; withdraw only
debits what was really added (remainder respected); pool load is race-free; atomic file writes; disk I/O moved
off the world thread (dirty set + 10s saver); /sacks page is built inline (no .ui files, no underscores in IDs) with TextButtons + paging;
ticker cancelled on shutdown; failures logged. 0.1.4: self-test join grant removed (sweep + page verified in-game 2026-09-22).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import json

VERSION = "0.6.6"
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

for c, m in ((PLA, "getInventory"), (INV, "getStorage"), (IC, "getItemStack"), (IC, "removeItemStackFromSlot"), (IC, "addItemStack"),
             (IS, "getItemId"), (IS, "getQuantity"), (WLD, "execute"), (IST, "getRemainder"), (ISS, "succeeded"), (EVD, "of"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"), (OCU, "registerSimple"), (CRP, "getAvailableRecipesForCategory"),
             (CRM, "getInputMaterials"), (CRR, "getInput"), (FCC, "getAssetMap"), (IC, "countRemovableMaterial"), (IC, "removeMaterials"), (INV, "getCombinedBackpackStorageHotbar"), (SIC, "addOrDropItemStack")):
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
pl   = pool.makeClass(PKG + ".SkyySacksPlugin", pool.get(JP))

ROWS = 12

# ================= SackDefs =================
defs.addField(CtField.make('public static final String[] CATS = new String[] { "Mining", "Foraging", "Farming" };', defs))
defs.addMethod(CtNewMethod.make("""
public static String catOf(String itemId) {
  if (itemId == null) return null;
  if (itemId.startsWith("Skyy_Sack_")) return null;
  if (itemId.startsWith("Ore_") || itemId.startsWith("Rubble_") || itemId.startsWith("Rock_") || itemId.startsWith("Soil_")) return "Mining";
  if (itemId.startsWith("Wood_") || itemId.equals("Ingredient_Stick") || itemId.equals("Ingredient_Fibre") || itemId.equals("Ingredient_Tree_Bark")) return "Foraging";
  if (itemId.startsWith("Plant_") || itemId.startsWith("Food_") || itemId.startsWith("Fish_")) return "Farming";
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
sp.addMethod(CtNewMethod.make("""
public static void exempt(java.util.UUID u, String item, long ms) {
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) EXEMPT.get(u);
  if (m == null) { m = new java.util.concurrent.ConcurrentHashMap(); java.util.concurrent.ConcurrentHashMap prev = (java.util.concurrent.ConcurrentHashMap) EXEMPT.putIfAbsent(u, m); if (prev != null) m = prev; }
  m.put(item, Long.valueOf(System.currentTimeMillis() + ms));
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static boolean isExempt(java.util.UUID u, String item) {
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) EXEMPT.get(u);
  if (m == null) return false;
  Long until = (Long) m.get(item);
  if (until == null) return false;
  if (until.longValue() < System.currentTimeMillis()) { m.remove(item); return false; }
  return true;
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static void clearExempt(java.util.UUID u) {
  EXEMPT.remove(u);
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyySacks] " + msg); } catch (Throwable t) { }
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static java.util.Map pool(java.util.UUID u) {
  java.util.Map m = (java.util.Map) POOLS.get(u);
  if (m != null) return m;
  m = new java.util.concurrent.ConcurrentHashMap();
  try {
    java.nio.file.Path f = DIR.resolve(u.toString() + ".properties");
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
  } catch (Throwable t) { warn("could not load pool for " + u + ": " + t); }
  java.util.Map prev = (java.util.Map) POOLS.putIfAbsent(u, m);
  return prev != null ? prev : m;
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static void save(java.util.UUID u) {
  try {
    java.util.Map m = (java.util.Map) POOLS.get(u);
    if (m == null) return;
    java.util.Properties p = new java.util.Properties();
    java.util.Iterator it = m.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      p.setProperty((String) e.getKey(), String.valueOf(((Long) e.getValue()).longValue()));
    }
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(u.toString() + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyySacks pool"); } finally { out.close(); }
    java.nio.file.Files.move(tmp, DIR.resolve(u.toString() + ".properties"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  } catch (Throwable t) { warn("could not save pool for " + u + ": " + t); }
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static void flushDirty() {
  java.util.Iterator it = DIRTY.keySet().iterator();
  while (it.hasNext()) {
    java.util.UUID u = (java.util.UUID) it.next();
    it.remove();
    save(u);
  }
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static long get(java.util.UUID u, String item) {
  Long v = (Long) pool(u).get(item);
  return v == null ? 0L : v.longValue();
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static synchronized void add(java.util.UUID u, String item, long n) {
  java.util.Map m = pool(u);
  Long v = (Long) m.get(item);
  long nv = (v == null ? 0L : v.longValue()) + n;
  if (nv <= 0L) m.remove(item); else m.put(item, Long.valueOf(nv));
  DIRTY.put(u, Boolean.TRUE);
}""", sp))
sp.addMethod(CtNewMethod.make(f"""
public static long catTotal(java.util.UUID u, String cat) {{
  long t = 0L;
  java.util.Iterator it = pool(u).entrySet().iterator();
  while (it.hasNext()) {{
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (cat.equals({PKG}.SackDefs.catOf((String) e.getKey()))) t += ((Long) e.getValue()).longValue();
  }}
  return t;
}}""", sp))

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
public static int sweep({PLA} p, java.util.UUID u, String onlyCat, boolean allContainers) {{
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
      if (!allContainers && {PKG}.SackPool.isExempt(u, id)) continue;
      Integer catCap = (Integer) caps.get(cat);
      if (catCap == null) continue;
      long have = {PKG}.SackPool.get(u, id);
      long room = (long) catCap.intValue() - have;
      if (room <= 0L) continue;
      int qty = it.getQuantity();
      int take = (long) qty < room ? qty : (int) room;
      if (take <= 0) continue;
      {ISS} tx = stor.removeItemStackFromSlot(s, take);
      if (tx == null || !tx.succeeded()) continue;
      {IS} rem = tx.getRemainder();
      int removed = take - (rem == null ? 0 : rem.getQuantity());
      if (removed > 0) {{ {PKG}.SackPool.add(u, id, (long) removed); moved += removed; }}
    }}
  }}
  return moved;
}}""", swp))
# withdraw up to n of an item into STORAGE; returns how many actually left the pool
swp.addMethod(CtNewMethod.make(f"""
public static int withdraw({PLA} p, java.util.UUID u, String id, int n) {{
  long have = {PKG}.SackPool.get(u, id);
  if (have <= 0L || n <= 0) return 0;
  String cat = {PKG}.SackDefs.catOf(id);
  if (cat == null || !caps(p.getInventory()).containsKey(cat)) return 0;
  int take = (long) n < have ? n : (int) have;
  {IST} tx = p.getInventory().getStorage().addItemStack(new {IS}(id, take));
  {IS} rem = tx == null ? null : tx.getRemainder();
  int added = (tx == null || !tx.succeeded()) ? 0 : take - (rem == null ? 0 : rem.getQuantity());
  if (added > 0) {{ {PKG}.SackPool.add(u, id, -(long) added); {PKG}.SackPool.exempt(u, id, 600000L); }}
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
    sweep(p, pr.getUuid(), null, false);
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
sav.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{ {PKG}.SackPool.flushDirty(); }} catch (Throwable t) {{ }}
}}""", sav))

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
public static synchronized void write(java.util.UUID u, String recipe, int requested, int done, boolean flag, int given, String audit) {
  try {
    if (FILE == null) return;
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    String line = new java.util.Date().toString() + " " + u + " " + recipe + " requested=" + requested + " done=" + done + " flag=" + flag + " given=" + given + audit + System.lineSeparator();
    java.nio.file.Files.write(FILE, line.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { }
}""", clog))

# CraftPage fields + constructor first (SacksPage references it)
cpg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap ONLY = new java.util.concurrent.ConcurrentHashMap();", cpg))
cpg.addField(CtField.make("public String tab;", cpg))
cpg.addField(CtField.make("public int pageNo;", cpg))
cpg.addField(CtField.make("public String info;", cpg))
cpg.addField(CtField.make("public java.util.ArrayList rows;", cpg))
cpg.addField(CtField.make("public java.util.ArrayList tabs;", cpg))
cpg.addConstructor(CtNewConstructor.make(f"""
public CraftPage({PR} pr, String tab) {{
  super(pr, {LIFE}.CanDismiss);
  this.tab = tab; this.pageNo = 0; this.info = "";
}}""", cpg))

# ================= SacksPage (SkyBlock-style: tabs, capacity, 9x4 icon grid, pick up all / deposit all) =================
page.addField(CtField.make("public String cat;", page))
page.addField(CtField.make("public String[] cells;", page))
page.addField(CtField.make("public String info;", page))
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
public String pickCat(java.util.UUID u, java.util.HashMap caps) {{
  String[] cats = {PKG}.SackDefs.CATS;
  if (this.cat != null && caps.containsKey(this.cat)) return this.cat;
  for (int c = 0; c < cats.length; c++) if (caps.containsKey(cats[c]) && {PKG}.SackPool.catTotal(u, cats[c]) > 0L) return cats[c];
  for (int c = 0; c < cats.length; c++) if (caps.containsKey(cats[c])) return cats[c];
  return null;
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
  java.util.HashMap caps = player == null ? new java.util.HashMap() : {PKG}.SweepTask.caps(player.getInventory());
  this.cat = pickCat(u, caps);
  if (this.cat == null) {{
    b.appendInline((String) null, "Group #SkyySacks {{ Anchor: (Width: 560, Height: 160); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 12); LayoutMode: Top; }}");
    b.appendInline("#SkyySacks", "Label {{ Anchor: (Height: 40); Text: \\"Pocket Dimension\\"; Style: (FontSize: 20, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    b.appendInline("#SkyySacks", "Label {{ Anchor: (Height: 60); Text: \\"You need a magic bag on you to reach in. Craft a Mining or Foraging or Farming bag at a workbench.\\"; Style: (FontSize: 14, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center, Wrap: true); }}");
    this.cells = new String[36];
    return;
  }}
  Integer capObj = (Integer) caps.get(this.cat);
  long capacity = capObj == null ? 0L : (long) capObj.intValue();
  long stored = {PKG}.SackPool.catTotal(u, this.cat);
  String bs = "Style: TextButtonStyle(Default: (Background: #5a4420, LabelStyle: (FontSize: 15, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 15, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 15, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  String tabOn = "Style: TextButtonStyle(Default: (Background: #e0b060, LabelStyle: (FontSize: 15, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #f0c878, LabelStyle: (FontSize: 15, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #b08040, LabelStyle: (FontSize: 15, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  b.appendInline((String) null, "Group #SkyySacks {{ Anchor: (Width: 900, Height: 600); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyySacks", "Group {{ Anchor: (Height: 2); Background: #e0b060; }}");
  b.appendInline("#SkyySacks", "Group #SkyySTabs {{ Anchor: (Height: 46); LayoutMode: Left; Padding: (Top: 8); }}");
  String[] cats = {PKG}.SackDefs.CATS;
  for (int c = 0; c < cats.length; c++) {{
    if (!caps.containsKey(cats[c])) continue;
    boolean sel = cats[c].equals(this.cat);
    b.appendInline("#SkyySTabs", "TextButton #SkyySTab" + cats[c] + " {{ Anchor: (Width: 175, Height: 36); Text: \\"" + cats[c] + "\\"; " + (sel ? tabOn : bs) + " }}");
    b.appendInline("#SkyySTabs", "Label {{ Anchor: (Width: 8, Height: 36); Text: \\"\\"; }}");
    ev.addEventBinding({BT}.Activating, "#SkyySTab" + cats[c], {EVD}.of("a", "tab:" + cats[c]));
  }}
  b.appendInline("#SkyySTabs", "Label {{ Anchor: (Width: 26, Height: 36); Text: \\"\\"; }}");
  b.appendInline("#SkyySTabs", "TextButton #SkyySTabCraft {{ Anchor: (Width: 145, Height: 36); Text: \\"Craft\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyySTabCraft", {EVD}.of("a", "craft"));
  b.appendInline("#SkyySacks", "Label #SkyySCap {{ Anchor: (Height: 34); Text: \\"" + safe(this.cat + " bag - holds up to " + capacity + " of each item - " + stored + " stored") + "\\"; Style: (FontSize: 18, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  java.util.ArrayList entries = new java.util.ArrayList();
  java.util.Iterator it = {PKG}.SackPool.pool(u).entrySet().iterator();
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
    for (int i = 0; i < 36; i++) {{
      if (this.cells == null || this.cells[i] == null) continue;
      int n = 0;
      if (data.indexOf("cell:" + i + ":stack\\"") >= 0) n = 64;
      else if (data.indexOf("cell:" + i + ":one\\"") >= 0) n = 1;
      if (n == 0) continue;
      int added = {PKG}.SweepTask.withdraw(player, u, this.cells[i], n);
      this.info = added > 0 ? ("took " + added + " " + this.cells[i]) : "storage is full";
      {PKG}.SackPool.save(u);
      rebuild();
      return;
    }}
    if (data.indexOf("pickall\\"") >= 0) {{
      int total = 0;
      for (int i = 0; i < 36; i++) {{
        if (this.cells[i] == null) continue;
        int added; int guard = 0;
        do {{ added = {PKG}.SweepTask.withdraw(player, u, this.cells[i], 64); total += added; guard++; }} while (added > 0 && guard < 64);
      }}
      this.info = total > 0 ? ("picked up " + total + " items") : "storage is full";
      {PKG}.SackPool.save(u);
      rebuild();
      return;
    }}
    if (data.indexOf("depall\\"") >= 0) {{
      {PKG}.SackPool.clearExempt(u);
      int moved = {PKG}.SweepTask.sweep(player, u, this.cat, true);
      this.info = moved > 0 ? ("deposited " + moved + " items") : "nothing to deposit (or sack full)";
      {PKG}.SackPool.save(u);
      rebuild();
      return;
    }}
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("sacks page event failed: " + t); }}
}}""", page))

# ================= SacksCmd =================
cmd.addConstructor(CtNewConstructor.make("""
public SacksCmd() {
  super("sacks", "Open your pocket dimension (needs a magic bag on you)");
  addAliases(new String[] { "pd", "bags" });
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
mir.addConstructor(CtNewConstructor.make(f"""
public BagMirror() {{
  this.cont = new {SIC}((short) 36);
  this.slotIds = new String[36];
  this.slotQty = new int[36];
  this.sig = "";
}}""", mir))
mir.addMethod(CtNewMethod.make(f"""
public static {PKG}.BagMirror of(java.util.UUID u) {{
  {PKG}.BagMirror m = ({PKG}.BagMirror) MIRRORS.get(u);
  if (m == null) {{ m = new {PKG}.BagMirror(); {PKG}.BagMirror prev = ({PKG}.BagMirror) MIRRORS.putIfAbsent(u, m); if (prev != null) m = prev; }}
  return m;
}}""", mir))
# apply consumption: anything missing from the mirror vs. what we put there left the pool (the bench took it)
mir.addMethod(CtNewMethod.make(f"""
public int sync(java.util.UUID u) {{
  int consumed = 0;
  for (int i = 0; i < 36; i++) {{
    if (this.slotIds[i] == null) continue;
    {IS} it = this.cont.getItemStack((short) i);
    int actual = (it == null || it.isEmpty()) ? 0 : it.getQuantity();
    if (actual < this.slotQty[i]) {{ int d = this.slotQty[i] - actual; {PKG}.SackPool.add(u, this.slotIds[i], -(long) d); consumed += d; }}
  }}
  return consumed;
}}""", mir))
# rebuild the mirror from the pool: only categories the player carries a bag for; up to 4 stacks per item, 36 slots
mir.addMethod(CtNewMethod.make(f"""
public String rebuild(java.util.UUID u, java.util.HashMap caps) {{
  try {{ this.cont.clear(); }} catch (Throwable t) {{ }}
  for (int i = 0; i < 36; i++) {{ this.slotIds[i] = null; this.slotQty[i] = 0; }}
  StringBuilder sb = new StringBuilder();
  int slot = 0;
  java.util.ArrayList entries = new java.util.ArrayList({PKG}.SackPool.pool(u).entrySet());
  java.util.Collections.sort(entries, new {PKG}.CountCmp());
  for (int e = 0; e < entries.size() && slot < 36; e++) {{
    java.util.Map.Entry en = (java.util.Map.Entry) entries.get(e);
    String id = (String) en.getKey();
    long cnt = ((Long) en.getValue()).longValue();
    String cat = {PKG}.SackDefs.catOf(id);
    if (cat == null || !caps.containsKey(cat) || cnt <= 0L) continue;
    int max = 64;
    try {{ {IS} probe = new {IS}(id, 1); if (probe.getItem() != null && probe.getItem().getMaxStack() > 0) max = probe.getItem().getMaxStack(); }} catch (Throwable t) {{ }}
    int stacks = 0;
    while (cnt > 0L && stacks < 4 && slot < 36) {{
      int q = cnt < (long) max ? (int) cnt : max;
      this.cont.setItemStackForSlot((short) slot, new {IS}(id, q));
      this.slotIds[slot] = id; this.slotQty[slot] = q;
      sb.append(id).append('=').append(q).append(';');
      cnt -= q; slot++; stacks++;
    }}
  }}
  return sb.toString();
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

# ================= CraftLinkTask (world thread, every 300ms per player) =================
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
      {PKG}.BagMirror m = {PKG}.BagMirror.of(u);
      int consumed = m.sync(u);
      java.util.HashMap caps = {PKG}.SweepTask.caps(p.getInventory());
      String sig = m.rebuild(u, caps);
      {MERS} sec = (({MCW}) w).getExtraResourcesSection();
      if (sec == null) continue;
      {IC} existing = sec.getItemContainer();
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
      if (consumed > 0) {PKG}.SackPool.save(u);
    }}
    if (!any) {{
      {PKG}.BagMirror m = ({PKG}.BagMirror) {PKG}.BagMirror.MIRRORS.get(u);
      if (m != null) {{ int c = m.sync(u); if (c > 0) {PKG}.SackPool.save(u); {PKG}.BagMirror.MIRRORS.remove(u); }}
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
    Integer cur = (Integer) out.get(bench);
    if (cur == null || cur.intValue() < tier) out.put(bench, Integer.valueOf(tier));
  }}
  return out;
}}""", cpg))
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
cpg.addMethod(CtNewMethod.make(f"""
public java.util.ArrayList buildTabs({PLA} p, java.util.UUID u) {{
  java.util.ArrayList t = new java.util.ArrayList();
  java.util.Iterator it = {FCC}.getAssetMap().getAssetMap().values().iterator();
  java.util.ArrayList fc = new java.util.ArrayList();
  while (it.hasNext()) {{ {FCC} c = ({FCC}) it.next(); fc.add(c); }}
  for (int i = 0; i < fc.size(); i++) {{ {FCC} c = ({FCC}) fc.get(i); t.add(new String[] {{ "F:" + c.getId(), pretty(c.getId()) }}); }}
  java.util.HashMap acc = accessories(p, u);
  java.util.ArrayList benches = new java.util.ArrayList(acc.keySet());
  java.util.Collections.sort(benches);
  String[] roman = new String[] {{ "", "I", "II", "III", "IV", "V", "VI", "VII", "VIII" }};
  for (int bi = 0; bi < benches.size(); bi++) {{
    String bench = (String) benches.get(bi);
    int tier = ((Integer) acc.get(bench)).intValue();
    String label = pretty(bench).replace(" Bench", "").replace("bench", "") + (tier > 0 && tier < roman.length ? " " + roman[tier] : "");
    t.add(new String[] {{ "B:" + bench + ":" + tier, label }});
  }}
  if (!collectionRecipes(u).isEmpty()) t.add(new String[] {{ "C:", "Collections" }});
  return t;
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public java.util.ArrayList recipesFor(String tabId, java.util.UUID u) {{
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.TreeSet ids = new java.util.TreeSet();
  if (tabId.startsWith("F:")) {{
    java.util.Set s = {CRP}.getAvailableRecipesForCategory("Fieldcraft", tabId.substring(2));
    if (s != null) ids.addAll(s);
  }} else if (tabId.startsWith("B:")) {{
    String bench = tabId.substring(2); int tier = 1;
    int colon = bench.indexOf(':');
    if (colon >= 0) {{ try {{ tier = Integer.parseInt(bench.substring(colon + 1)); }} catch (Throwable e) {{ }} bench = bench.substring(0, colon); }}
    java.util.Iterator it = {CRR}.getAssetMap().getAssetMap().values().iterator();
    while (it.hasNext()) {{
      {CRR} r = ({CRR}) it.next();
      {BRQ}[] br = r.getBenchRequirement();
      if (br == null) continue;
      for (int i = 0; i < br.length; i++) {{
        if (br[i] == null || !bench.equalsIgnoreCase(String.valueOf(br[i].id))) continue;
        int need = br[i].requiredTierLevel;
        if (need <= 0) need = 1;
        if (need <= tier) {{ ids.add(r.getId()); break; }}
      }}
    }}
  }} else if (tabId.startsWith("C:")) {{
    ids.addAll(collectionRecipes(u));
  }}
  java.util.Iterator ii = ids.iterator();
  while (ii.hasNext()) {{
    Object r = {CRR}.getAssetMap().getAsset(ii.next());
    if (r != null) out.add(r);
  }}
  return out;
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static {CIC} materials({PLA} p, java.util.UUID u) {{
  {PKG}.BagMirror m = {PKG}.BagMirror.of(u);
  m.sync(u);
  m.rebuild(u, {PKG}.SweepTask.caps(p.getInventory()));
  return new {CIC}(new {IC}[] {{ p.getInventory().getCombinedBackpackStorageHotbar(), m.cont }});
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
cpg.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
  String bs = "Style: TextButtonStyle(Default: (Background: #1d3a5f, LabelStyle: (FontSize: 13, TextColor: #dceeff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #2f5a8f, LabelStyle: (FontSize: 13, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #0f2038, LabelStyle: (FontSize: 13, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  String on = "Style: TextButtonStyle(Default: (Background: #7fb0e0, LabelStyle: (FontSize: 13, TextColor: #06192a, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #a0c8f0, LabelStyle: (FontSize: 13, TextColor: #06192a, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #5f90c0, LabelStyle: (FontSize: 13, TextColor: #06192a, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  b.appendInline((String) null, "Group #SkyyCraft {{ Anchor: (Width: 1000, Height: 830); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyyCraft", "Group {{ Anchor: (Height: 2); Background: #7fb0e0; }}");
  b.appendInline("#SkyyCraft", "Label {{ Anchor: (Height: 34); Text: \\"Crafting\\"; Style: (FontSize: 19, RenderBold: true, TextColor: #e6f2ff, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  if (p == null) return;
  this.tabs = buildTabs(p, u);
  if (this.tab == null && this.tabs.size() > 0) this.tab = ((String[]) this.tabs.get(0))[0];
  int tabRow = 0; int inRow = 0;
  b.appendInline("#SkyyCraft", "Group #SkyyCTabs0 {{ Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 4); }}");
  b.appendInline("#SkyyCTabs0", "TextButton #SkyyCBags {{ Anchor: (Width: 150, Height: 32); Text: \\"< Back to bags\\"; " + bs + " }}");
  b.appendInline("#SkyyCTabs0", "Label {{ Anchor: (Width: 14, Height: 32); Text: \\"\\"; }}");
  ev.addEventBinding({BT}.Activating, "#SkyyCBags", {EVD}.of("a", "bags"));
  for (int i = 0; i < this.tabs.size(); i++) {{
    int cap = tabRow == 0 ? 6 : 8;
    if (inRow >= cap) {{ tabRow++; inRow = 0; b.appendInline("#SkyyCraft", "Group #SkyyCTabs" + tabRow + " {{ Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 4); }}"); }}
    String[] t = (String[]) this.tabs.get(i);
    boolean sel = t[0].equals(this.tab);
    b.appendInline("#SkyyCTabs" + tabRow, "TextButton #SkyyCTab" + i + " {{ Anchor: (Width: 110, Height: 32); Text: \\"" + {PKG}.SacksPage.safe(t[1]) + "\\"; " + (sel ? on : bs) + " }}");
    b.appendInline("#SkyyCTabs" + tabRow, "Label {{ Anchor: (Width: 6, Height: 32); Text: \\"\\"; }}");
    ev.addEventBinding({BT}.Activating, "#SkyyCTab" + i, {EVD}.of("a", "tab:" + i));
    inRow++;
  }}
  b.appendInline("#SkyyCraft", "Label {{ Anchor: (Height: 22); Text: \\"Materials are counted from your inventory and your magic bags.\\"; Style: (FontSize: 13, TextColor: #9fb8d0, HorizontalAlignment: Center); }}");
  java.util.ArrayList raw = this.tab == null ? new java.util.ArrayList() : recipesFor(this.tab, u);
  {CIC} mats = materials(p, u);
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
    b.appendInline("#SkyyCTxt" + i, "Label {{ Anchor: (Height: 27); Text: \\"" + {PKG}.SacksPage.safe(pretty(outId) + (outq != null && outq.getQuantity() > 1 ? " x" + outq.getQuantity() : "")) + "\\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + (lim > 0 ? "#ffffff" : "#8a97a8") + ", VerticalAlignment: Center); }}");
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
  if (this.rows.size() == 0) b.appendInline("#SkyyCraft", "Label {{ Anchor: (Height: 30); Text: \\"No recipes here yet.\\"; Style: (FontSize: 15, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
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
    if (data.indexOf("\\"prev\\"") >= 0) {{ this.pageNo--; rebuild(); return; }}
    if (data.indexOf("\\"next\\"") >= 0) {{ this.pageNo++; rebuild(); return; }}
    if (data.indexOf("\\"onlyc\\"") >= 0) {{ if (Boolean.TRUE.equals(ONLY.get(u))) ONLY.remove(u); else ONLY.put(u, Boolean.TRUE); this.pageNo = 0; rebuild(); return; }}
    {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (p == null) return;
    if (data.indexOf("\\"bags\\"") >= 0) {{ p.getPageManager().openCustomPage(ref, st, new {PKG}.SacksPage(this.playerRef, (String) null)); return; }}
    for (int i = 0; this.tabs != null && i < this.tabs.size(); i++) {{
      if (data.indexOf("tab:" + i + "\\"") >= 0) {{ this.tab = ((String[]) this.tabs.get(i))[0]; this.pageNo = 0; this.info = ""; rebuild(); return; }}
    }}
    int c = data.indexOf("craft:");
    if (c < 0) return;
    int e = data.indexOf('\\"', c);
    String[] parts = data.substring(c + 6, e).split(":");
    int idx = Integer.parseInt(parts[0]); int want = Integer.parseInt(parts[1]);
    if (this.rows == null || idx < 0 || idx >= this.rows.size()) return;
    {CRR} r = ({CRR}) this.rows.get(idx);
    {CIC} mats = materials(p, u);
    int lim = limit(r, mats);
    int qty = want == 0 ? lim : (want < lim ? want : lim);
    if (qty <= 0) {{ this.info = "not enough materials"; rebuild(); return; }}
    java.util.List inputs = {CRM}.getInputMaterials(r, qty);
    int n = inputs == null ? 0 : inputs.size();
    if (n == 0) {{ this.info = "this recipe has no inputs"; rebuild(); return; }}
    if (!mats.canRemoveMaterials(inputs)) {{ this.info = "not enough materials"; rebuild(); return; }}
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
    {PKG}.BagMirror m = {PKG}.BagMirror.of(u);
    int consumed = m.sync(u);
    if (consumed > 0) {PKG}.SackPool.save(u);
    {MQ}[] outs = r.getOutputs();
    {MQ} outq = r.getPrimaryOutput();
    if ((outs == null || outs.length == 0) && outq != null) outs = new {MQ}[] {{ outq }};
    int given = 0;
    if (done > 0 && outs != null) {{
      for (int k = 0; k < outs.length; k++) {{
        if (outs[k] == null || outs[k].getItemId() == null) continue;
        long total = (long) outs[k].getQuantity() * (long) done; if (total > 100000L) total = 100000L;
        {SIC}.addOrDropItemStack(st, ref, p.getInventory().getCombinedStorageHotbarBackpack(), new {IS}(outs[k].getItemId(), (int) total));
        given += (int) total;
      }}
    }}
    {PKG}.CraftLog.write(u, String.valueOf(r.getId()), qty, done, flag, given, audit.toString());
    if (done > 0 && given == 0) {PKG}.SackPool.warn("craft: " + done + " crafts of " + r.getId() + " paid but the recipe has no item output (" + u + ")");
    String nm = pretty(outq == null ? "?" : outq.getItemId());
    if (done == qty) this.info = "crafted " + qty + " x " + nm + (consumed > 0 ? " (" + consumed + " from bags)" : "");
    else if (done > 0) this.info = "crafted " + done + " of " + qty + " x " + nm + " - extra materials were returned";
    else this.info = "could not remove the materials - nothing was used";
    rebuild();
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("craft page event failed: " + t); }}
}}""", cpg))

# ================= CraftCmd (/craft) =================
ccmd.addConstructor(CtNewConstructor.make("""
public CraftCmd() {
  super("craft", "Open inventory crafting (materials from your inventory and your magic bags)");
  addAliases(new String[] { "recipes" });
}""", ccmd))
ccmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new {PKG}.CraftPage(pr, (String) null));
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("/craft failed: " + t); pr.sendMessage({MSG}.raw("[SkyySacks] could not open crafting")); }}
}}""", ccmd))

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture saver;", pl))
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture crafter;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyySacksPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.SackPool.LOG = getLogger();
  {PKG}.SackPool.DIR = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("pools");
  {PKG}.CraftLog.FILE = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("crafts.log");
  getCommandRegistry().registerCommand(new {PKG}.SacksCmd());
  getCommandRegistry().registerCommand(new {PKG}.CraftCmd());
  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacks", new {PKG}.SacksPageFactory((String) null));
  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksMining", new {PKG}.SacksPageFactory("Mining"));
  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksForaging", new {PKG}.SacksPageFactory("Foraging"));
  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksFarming", new {PKG}.SacksPageFactory("Farming"));
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SackTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
  this.saver = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SackSaver(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);
  this.crafter = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.CraftTick(), 1000L, 300L, java.util.concurrent.TimeUnit.MILLISECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyySacks] {VERSION} ready - /pd, /craft, right-click a magic bag; workbenches craft from your bags");
}}""", pl))
pl.addMethod(CtNewMethod.make(f"""
protected void shutdown() {{
  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
  try {{ if (this.saver != null) this.saver.cancel(false); }} catch (Throwable t) {{ }}
  try {{ if (this.crafter != null) this.crafter.cancel(false); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackPool.flushDirty(); }} catch (Throwable t) {{ }}
  super.shutdown();
}}""", pl))

for c in (defs, sp, swp, tick, sav, cmp, page, cmd, fac, mir, clt, ctk, rcmp, clog, cpg, ccmd, pl):
    c.writeFile(OUT)
print("classes written")

# ================= assets =================
BTN_STYLE = """@Btn = TextButtonStyle(
  Default: (Background: #5a4420, LabelStyle: (FontSize: 12, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)),
  Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)),
  Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center))
);
"""
rows = ""
for i in range(ROWS):
    rows += """    Group #s_row_%d {
      Anchor: (Height: 26);
      LayoutMode: Left;
      Padding: (Vertical: 2);
      Visible: false;
      Label #s_name_%d { Anchor: (Width: 330, Height: 22); Style: (FontSize: 11, TextColor: #ffffff, VerticalAlignment: Center); Text: ""; }
      TextButton #s_%d_w1 { Anchor: (Width: 56, Height: 22); Text: "Get 1"; Style: @Btn; }
      Label { Anchor: (Width: 6, Height: 22); Text: ""; }
      TextButton #s_%d_w64 { Anchor: (Width: 62, Height: 22); Text: "Get 64"; Style: @Btn; }
    }
""" % (i, i, i, i)
SACKS_UI = BTN_STYLE + """
Group {
  Anchor: (Full: 0);
  Group #SkyySacks {
    Anchor: (Horizontal: 0, Vertical: 0, Width: 560, Height: 470);
    Background: #0b1524(0.94);
    Padding: (Horizontal: 14, Vertical: 10);
    LayoutMode: Top;
    Group { Anchor: (Height: 2); Background: #e0b060; }
    Label { Anchor: (Height: 26); Style: (FontSize: 15, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); Text: "SkyySacks"; }
    Label #s_caps { Anchor: (Height: 16); Style: (FontSize: 11, TextColor: #c9b89a, HorizontalAlignment: Center); Text: ""; }
    Label #s_empty { Anchor: (Height: 30); Visible: false; Style: (FontSize: 12, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); Text: "Nothing pooled yet - carry a sack and pick things up!"; }
%s    Group {
      Anchor: (Height: 28);
      LayoutMode: Left;
      Padding: (Top: 4);
      TextButton #s_prev { Anchor: (Width: 60, Height: 22); Text: "< Prev"; Style: @Btn; }
      Label #s_page { Anchor: (Width: 120, Height: 22); Style: (FontSize: 10, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center); Text: ""; }
      TextButton #s_next { Anchor: (Width: 60, Height: 22); Text: "Next >"; Style: @Btn; }
    }
  }
}
""" % rows

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
mats = {"Mining": "Ingredient_Bar_Copper", "Foraging": "Wood_Oak_Trunk", "Farming": "Food_Bread"}
for cat in ("Mining", "Foraging", "Farming"):
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
        what = {"Mining": "ore, rubble, rock and soil", "Foraging": "logs, planks, sticks, fibre and bark", "Farming": "plants, food and fish"}[cat]
        desc = "A magic bag that opens onto your pocket dimension. Holds up to %s of each %s item (%s). Matching items in your storage are pulled in automatically. Right-click to reach in. You need a bag on you to reach in, but nothing is ever lost." % (format(caps, ","), cat.lower(), what)
        lang.append("items.Skyy_Sack_%s_%s.description=%s" % (cat, tier, desc))
        lang.append("server.items.Skyy_Sack_%s_%s.description=%s" % (cat, tier, desc))
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"  # key items.<Id>.name in server.lang (pattern from Tamework)

jar = os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)
B.assemble(jar, B.manifest("SkyySacks", VERSION, "SkyBlock-style sacks: craft a sack, matching pickups pool automatically, /sacks to view and withdraw. Zero dependencies.", PKG + ".SkyySacksPlugin"), OUT, files)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyySacks.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyySacks" % VERSION, disable_prefix="Skyy:")
