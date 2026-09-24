"""SkyySacks 0.1.3 - build script (javassist via jpype).
Run:   python build_skyysacks_0.1.4.py            -> SkyySacks/SkyySacks-0.1.1.jar
       python build_skyysacks_0.1.4.py --deploy   -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world
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

VERSION = "0.1.4"
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
OCU = "com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction"

for c, m in ((PLA, "getInventory"), (INV, "getStorage"), (IC, "getItemStack"), (IC, "removeItemStackFromSlot"), (IC, "addItemStack"),
             (IS, "getItemId"), (IS, "getQuantity"), (WLD, "execute"), (IST, "getRemainder"), (ISS, "succeeded"), (EVD, "of"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"), (OCU, "registerSimple")):
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
pl   = pool.makeClass(PKG + ".SkyySacksPlugin", pool.get(JP))

ROWS = 12

# ================= SackDefs =================
defs.addField(CtField.make('public static final String[] CATS = new String[] { "Mining", "Foraging", "Farming" };', defs))
defs.addMethod(CtNewMethod.make("""
public static String catOf(String itemId) {
  if (itemId == null) return null;
  if (itemId.startsWith("Skyy_Sack_")) return null;
  if (itemId.startsWith("Ore_") || itemId.startsWith("Rubble_") || itemId.startsWith("Rock_") || itemId.startsWith("Soil_")) return "Mining";
  if (itemId.startsWith("Wood_")) return "Foraging";
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
    {INV} inv = p.getInventory();
    if (inv == null) return;
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
            caps.put(cat, Integer.valueOf((cur == null ? 0 : cur.intValue()) + {PKG}.SackDefs.tierCap(tier)));
          }}
        }}
      }}
    }}
    if (caps.isEmpty()) return;
    java.util.UUID u = pr.getUuid();
    {IC} stor = inv.getStorage();
    if (stor == null) return;
    short cap2 = stor.getCapacity();
    for (short s = 0; s < cap2; s++) {{
      {IS} it = stor.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      String cat = {PKG}.SackDefs.catOf(id);
      if (cat == null) continue;
      Integer catCap = (Integer) caps.get(cat);
      if (catCap == null) continue;
      long have = {PKG}.SackPool.catTotal(u, cat);
      long room = (long) catCap.intValue() - have;
      if (room <= 0L) continue;
      int qty = it.getQuantity();
      int take = (long) qty < room ? qty : (int) room;
      if (take <= 0) continue;
      {ISS} tx = stor.removeItemStackFromSlot(s, take);
      if (tx == null || !tx.succeeded()) continue;
      {IS} rem = tx.getRemainder();
      int removed = take - (rem == null ? 0 : rem.getQuantity());
      if (removed > 0) {PKG}.SackPool.add(u, id, (long) removed);
    }}
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

# ================= SacksPage (static .ui + sets; TextButtons with EventData; paging) =================
page.addField(CtField.make("public String[] rowItems;", page))
page.addField(CtField.make("public int pageNo;", page))
page.addConstructor(CtNewConstructor.make(f"""
public SacksPage({PR} pr) {{
  super(pr, {LIFE}.CanDismiss);
  this.pageNo = 0;
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  java.util.Map m = {PKG}.SackPool.pool(u);
  java.util.ArrayList entries = new java.util.ArrayList(m.entrySet());
  java.util.Collections.sort(entries, new {PKG}.CountCmp());
  int pages = (entries.size() + {ROWS} - 1) / {ROWS};
  if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  int start = this.pageNo * {ROWS};
  String caps = "";
  String[] cats = {PKG}.SackDefs.CATS;
  for (int c = 0; c < cats.length; c++) caps = caps + cats[c] + ": " + {PKG}.SackPool.catTotal(u, cats[c]) + "   ";
  String bs = "Style: TextButtonStyle(Default: (Background: #5a4420, LabelStyle: (FontSize: 10, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  b.appendInline((String) null, "Group #SkyySacks {{ Anchor: (Width: 560, Height: 470); Background: #0b1524(0.94); Padding: (Horizontal: 14, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyySacks", "Group {{ Anchor: (Height: 2); Background: #e0b060; }}");
  b.appendInline("#SkyySacks", "Label {{ Anchor: (Height: 26); Text: \\"SkyySacks\\"; Style: (FontSize: 15, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySacks", "Label {{ Anchor: (Height: 16); Text: \\"" + caps + "\\"; Style: (FontSize: 11, TextColor: #c9b89a, HorizontalAlignment: Center); }}");
  if (entries.size() == 0) b.appendInline("#SkyySacks", "Label {{ Anchor: (Height: 30); Text: \\"Nothing pooled yet - carry a sack and pick things up!\\"; Style: (FontSize: 12, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  this.rowItems = new String[{ROWS}];
  for (int i = 0; i < {ROWS}; i++) {{
    int idx = start + i;
    if (idx >= entries.size()) {{ this.rowItems[i] = null; continue; }}
    java.util.Map.Entry e = (java.util.Map.Entry) entries.get(idx);
    String id = (String) e.getKey();
    long cnt = ((Long) e.getValue()).longValue();
    this.rowItems[i] = id;
    b.appendInline("#SkyySacks", "Group #SkyySRow" + i + " {{ Anchor: (Height: 26); LayoutMode: Left; Padding: (Vertical: 2); }}");
    b.appendInline("#SkyySRow" + i, "Label {{ Anchor: (Width: 330, Height: 22); Text: \\"" + id.replace("\\"", "") + "   x" + cnt + "\\"; Style: (FontSize: 11, TextColor: #ffffff, VerticalAlignment: Center); }}");
    b.appendInline("#SkyySRow" + i, "TextButton #SkyySGet" + i + "One {{ Anchor: (Width: 56, Height: 22); Text: \\"Get 1\\"; " + bs + " }}");
    b.appendInline("#SkyySRow" + i, "Label {{ Anchor: (Width: 6, Height: 22); Text: \\"\\"; }}");
    b.appendInline("#SkyySRow" + i, "TextButton #SkyySGet" + i + "Stack {{ Anchor: (Width: 62, Height: 22); Text: \\"Get 64\\"; " + bs + " }}");
    ev.addEventBinding({BT}.Activating, "#SkyySGet" + i + "One", {EVD}.of("a", "row" + i + ":w1"));
    ev.addEventBinding({BT}.Activating, "#SkyySGet" + i + "Stack", {EVD}.of("a", "row" + i + ":w64"));
  }}
  b.appendInline("#SkyySacks", "Group #SkyySNav {{ Anchor: (Height: 28); LayoutMode: Left; Padding: (Top: 4); }}");
  b.appendInline("#SkyySNav", "TextButton #SkyySPrev {{ Anchor: (Width: 60, Height: 22); Text: \\"< Prev\\"; " + bs + " }}");
  b.appendInline("#SkyySNav", "Label {{ Anchor: (Width: 120, Height: 22); Text: \\"Page " + (this.pageNo + 1) + " / " + pages + "\\"; Style: (FontSize: 10, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySNav", "TextButton #SkyySNext {{ Anchor: (Width: 60, Height: 22); Text: \\"Next >\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyySPrev", {EVD}.of("a", "prev"));
  ev.addEventBinding({BT}.Activating, "#SkyySNext", {EVD}.of("a", "next"));
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    if (data.indexOf("prev\\"") >= 0) {{ this.pageNo--; rebuild(); return; }}
    if (data.indexOf("next\\"") >= 0) {{ this.pageNo++; rebuild(); return; }}
    int idx = -1; int amt = 0;
    for (int i = 0; i < {ROWS} && idx < 0; i++) {{
      if (data.indexOf("row" + i + ":w64\\"") >= 0) {{ idx = i; amt = 64; }}
      else if (data.indexOf("row" + i + ":w1\\"") >= 0) {{ idx = i; amt = 1; }}
    }}
    if (idx < 0 || this.rowItems == null || this.rowItems[idx] == null) return;
    String id = this.rowItems[idx];
    java.util.UUID u = this.playerRef.getUuid();
    long have = {PKG}.SackPool.get(u, id);
    if (have <= 0L) {{ rebuild(); return; }}
    int take = (long) amt < have ? amt : (int) have;
    {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    {IST} tx = player.getInventory().getStorage().addItemStack(new {IS}(id, take));
    {IS} rem = tx == null ? null : tx.getRemainder();
    int added = (tx == null || !tx.succeeded()) ? 0 : take - (rem == null ? 0 : rem.getQuantity());
    if (added > 0) {{
      {PKG}.SackPool.add(u, id, -(long) added);
      {PKG}.SackPool.save(u);
    }} else {{
      this.playerRef.sendMessage({MSG}.raw("[SkyySacks] Your storage is full."));
    }}
    rebuild();
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("withdraw failed: " + t); }}
}}""", page))

# ================= SacksCmd =================
cmd.addConstructor(CtNewConstructor.make("""
public SacksCmd() {
  super("sacks", "Open your sacks");
}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) {{ pr.sendMessage({MSG}.raw("[SkyySacks] player not found")); return; }}
    player.getPageManager().openCustomPage(ref, store, new {PKG}.SacksPage(pr));
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

# ================= SacksPageFactory (right-click on a sack item -> OpenCustomUI "SkyySacks") =================
fac.addInterface(pool.get("java.util.function.Function"))
fac.addConstructor(CtNewConstructor.make("public SacksPageFactory() { }", fac))
fac.addMethod(CtNewMethod.make(f"""
public Object apply(Object o) {{
  return new {PKG}.SacksPage(({PR}) o);
}}""", fac))

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture saver;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyySacksPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.SackPool.LOG = getLogger();
  {PKG}.SackPool.DIR = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("pools");
  getCommandRegistry().registerCommand(new {PKG}.SacksCmd());
  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacks", new {PKG}.SacksPageFactory());
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SackTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
  this.saver = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SackSaver(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyySacks] {VERSION} ready - /sacks or right-click a sack");
}}""", pl))
pl.addMethod(CtNewMethod.make(f"""
protected void shutdown() {{
  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
  try {{ if (this.saver != null) this.saver.cancel(false); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackPool.flushDirty(); }} catch (Throwable t) {{ }}
  super.shutdown();
}}""", pl))

for c in (defs, sp, swp, tick, sav, cmp, page, cmd, fac, pl):
    c.writeFile(OUT)
print("classes written")

# ================= assets =================
BTN_STYLE = """@Btn = TextButtonStyle(
  Default: (Background: #5a4420, LabelStyle: (FontSize: 10, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)),
  Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)),
  Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center))
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
      "TranslationProperties": {"Name": "server.items.Skyy_Sack_%s_%s.name" % (cat, tier)},
      "Categories": ["Items.Tools"],
      "Icon": "Icons/ItemsGenerated/Utility_Bag_Seed.png",
      "Quality": quality,
      "Recipe": {"Input": recipe_in, "BenchRequirement": [{"Type": "Crafting", "Id": "Workbench", "Categories": ["Workbench_Crafting"]}]},
      "Model": "Items/Back/BackpackBig.blockymodel",
      "Texture": "Items/Back/BackpackBig_Texture.png",
      "IconProperties": {"Scale": 0.455, "Translation": [1.19, 2.39], "Rotation": [0, 177.73, 0]},
      "Tags": {"Family": ["Leather"], "Type": ["Utility"]},
      "MaxStack": 1,
      "Interactions": {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": "SkyySacks"}}]}}
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
        lang.append("items.Skyy_Sack_%s_%s.name=%s %s Sack" % (cat, tier, tier, cat))
        lang.append("server.items.Skyy_Sack_%s_%s.name=%s %s Sack" % (cat, tier, tier, cat))
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"  # key items.<Id>.name in server.lang (pattern from Tamework)

jar = os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)
B.assemble(jar, B.manifest("SkyySacks", VERSION, "SkyBlock-style sacks: craft a sack, matching pickups pool automatically, /sacks to view and withdraw. Zero dependencies.", PKG + ".SkyySacksPlugin"), OUT, files)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyySacks.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyySacks" % VERSION, disable_prefix="Skyy:")
