import jpype, sys, os, zipfile, json
from jdk4py import JAVA_HOME
jpype.startJVM(str(JAVA_HOME/"lib"/"server"/"libjvm.so"), "--add-opens=java.base/java.lang=ALL-UNNAMED", classpath=["/tmp/javassist/javassist.jar"])
J = jpype.JClass
ClassPool, CtField, CtNewMethod, CtNewConstructor = J("javassist.ClassPool"), J("javassist.CtField"), J("javassist.CtNewMethod"), J("javassist.CtNewConstructor")
REL = sys.argv[1]
pool = ClassPool(False); pool.appendSystemPath(); pool.appendClassPath(REL)
OUT = "/tmp/skyysacks_classes"; os.system(f"rm -rf {OUT}"); os.makedirs(OUT)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PAGE= "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
LIFE= "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime"
UCB = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
UEB = "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"
BT  = "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType"
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

# API asserts
for cn, mem in ((PLA, "getInventory"), (INV, "getStorage"), (IC, "getItemStack"), (IC, "removeItemStackFromSlot"), (IC, "addItemStack"), (IS, "getItemId"), (IS, "getQuantity"), (WLD, "execute")):
    c = pool.get(cn)
    assert any(str(m.getName()) == mem for m in c.getMethods()), f"missing {cn}.{mem}"
print("API check OK")

PKG = "com.skyy.sacks"
defs = pool.makeClass(PKG + ".SackDefs")
sp   = pool.makeClass(PKG + ".SackPool")
pl   = pool.makeClass(PKG + ".SkyySacksPlugin", pool.get(JP))
swp  = pool.makeClass(PKG + ".SweepTask")
tick = pool.makeClass(PKG + ".SackTick")
page = pool.makeClass(PKG + ".SacksPage", pool.get(PAGE))
cmd  = pool.makeClass(PKG + ".SacksCmd", pool.get(APC))
cmp  = pool.makeClass(PKG + ".CountCmp")
grt  = pool.makeClass(PKG + ".GrantTask")
srd  = pool.makeClass(PKG + ".SackReady")

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
  return 20160;
}""", defs))

# ================= SackPool =================
sp.addField(CtField.make("public static java.nio.file.Path DIR;", sp))
sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap POOLS = new java.util.concurrent.ConcurrentHashMap();", sp))
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
      p.load(in); in.close();
      java.util.Enumeration en = p.propertyNames();
      while (en.hasMoreElements()) {
        String k = (String) en.nextElement();
        try { m.put(k, Long.valueOf(Long.parseLong(p.getProperty(k)))); } catch (Throwable t) { }
      }
    }
  } catch (Throwable t) { }
  POOLS.put(u, m);
  return m;
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static void save(java.util.UUID u) {
  try {
    java.util.Map m = pool(u);
    java.util.Properties p = new java.util.Properties();
    java.util.Iterator it = m.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      p.setProperty((String) e.getKey(), String.valueOf(((Long) e.getValue()).longValue()));
    }
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(DIR.resolve(u.toString() + ".properties"), new java.nio.file.OpenOption[0]);
    p.store(out, "SkyySacks pool");
    out.close();
  } catch (Throwable t) { }
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static long get(java.util.UUID u, String item) {
  Long v = (Long) pool(u).get(item);
  return v == null ? 0L : v.longValue();
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static void add(java.util.UUID u, String item, long n) {
  java.util.Map m = pool(u);
  Long v = (Long) m.get(item);
  long nv = (v == null ? 0L : v.longValue()) + n;
  if (nv <= 0L) m.remove(item); else m.put(item, Long.valueOf(nv));
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

# ================= SweepTask (runs ON world thread) =================
swp.addInterface(pool.get("java.lang.Runnable"))
swp.addField(CtField.make(f"public {PR} pr;", swp))
swp.addConstructor(CtNewConstructor.make(f"public SweepTask({PR} pr) {{ this.pr = pr; }}", swp))
swp.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (pr == null || !pr.isValid()) return;
    {REF} r = pr.getReference();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    if (p == null) return;
    {INV} inv = p.getInventory();
    if (inv == null) return;
    // capacity per category from sack items in storage+hotbar+backpack
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
    // sweep STORAGE only (hotbar left alone on purpose)
    java.util.UUID u = pr.getUuid();
    {IC} stor = inv.getStorage();
    if (stor == null) return;
    boolean changed = false;
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
      long take = qty < room ? (long) qty : room;
      Object tx = stor.removeItemStackFromSlot(s);
      {PKG}.SackPool.add(u, id, take);
      changed = true;
      if ((long) qty > take) {{
        stor.addItemStack(new {IS}(id, (int) ((long) qty - take)));
      }}
    }}
    if (changed) {PKG}.SackPool.save(u);
  }} catch (Throwable t) {{ }}
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
      w.execute(new {PKG}.SweepTask(pr));
    }}
  }} catch (Throwable t) {{ }}
}}""", tick))

# comparator class
cmp.addInterface(pool.get("java.util.Comparator"))
cmp.addConstructor(CtNewConstructor.make("public CountCmp() { }", cmp))
cmp.addMethod(CtNewMethod.make("""
public int compare(Object a, Object b) {
  long x = ((Long) ((java.util.Map.Entry) a).getValue()).longValue();
  long y = ((Long) ((java.util.Map.Entry) b).getValue()).longValue();
  return x == y ? 0 : (x > y ? -1 : 1);
}""", cmp))


# ================= SacksPage =================
page.addField(CtField.make("public String[] rowItems;", page))
page.addConstructor(CtNewConstructor.make(f"""
public SacksPage({PR} pr) {{
  super(pr, {LIFE}.CanDismiss);
}}""", page))
page.addMethod(CtNewMethod.make(f"""
protected void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  java.util.Map m = {PKG}.SackPool.pool(u);
  java.util.ArrayList entries = new java.util.ArrayList(m.entrySet());
  java.util.Collections.sort(entries, new {PKG}.CountCmp());
  int n = entries.size() < 12 ? entries.size() : 12;
  this.rowItems = new String[n];
  StringBuilder doc = new StringBuilder();
  doc.append("Group {{ Anchor: (Horizontal: 0, Vertical: 0, Width: 560, Height: 470); Background: #0b1524(0.94); Padding: (Horizontal: 14, Vertical: 10); LayoutMode: Top; ");
  doc.append("Group {{ Anchor: (Height: 2); Background: #e0b060; }} ");
  doc.append("Label {{ Anchor: (Height: 26); Text: \\"SkyySacks\\"; Style: (FontSize: 15, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }} ");
  String caps = "";
  String[] cats = {PKG}.SackDefs.CATS;
  for (int c = 0; c < cats.length; c++) {{
    caps = caps + cats[c] + ": " + {PKG}.SackPool.catTotal(u, cats[c]) + "   ";
  }}
  doc.append("Label {{ Anchor: (Height: 16); Text: \\"").append(caps).append("\\"; Style: (FontSize: 11, TextColor: #c9b89a, HorizontalAlignment: Center); }} ");
  if (n == 0) {{
    doc.append("Label {{ Anchor: (Height: 30); Text: \\"Nothing pooled yet - carry a sack and pick things up!\\"; Style: (FontSize: 12, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }} ");
  }}
  for (int i = 0; i < n; i++) {{
    java.util.Map.Entry e = (java.util.Map.Entry) entries.get(i);
    String id = (String) e.getKey();
    long cnt = ((Long) e.getValue()).longValue();
    this.rowItems[i] = id;
    doc.append("Group {{ Anchor: (Height: 28); LayoutMode: Left; Padding: (Vertical: 2); ");
    doc.append("Label {{ Anchor: (Width: 300, Height: 24); Text: \\"").append(id).append("  x").append(cnt).append("\\"; Style: (FontSize: 11, TextColor: #ffffff, VerticalAlignment: Center); }} ");
    doc.append("Group #s_").append(i).append("_w1 {{ Anchor: (Width: 46, Height: 22); Background: #1d3a5f; Label {{ Anchor: (Full: 0); Text: \\"Get 1\\"; Style: (FontSize: 10, TextColor: #dceeff, HorizontalAlignment: Center, VerticalAlignment: Center); }} }} ");
    doc.append("Group #s_").append(i).append("_w64 {{ Anchor: (Width: 52, Height: 22); Background: #1d3a5f; Label {{ Anchor: (Full: 0); Text: \\"Get 64\\"; Style: (FontSize: 10, TextColor: #dceeff, HorizontalAlignment: Center, VerticalAlignment: Center); }} }} ");
    doc.append("}} ");
  }}
  doc.append("}}");
  b.appendInline((String) null, doc.toString());
  for (int i = 0; i < n; i++) {{
    ev.addEventBinding({BT}.Activating, "#s_" + i + "_w1");
    ev.addEventBinding({BT}.Activating, "#s_" + i + "_w64");
  }}
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    int p = data.indexOf("#s_");
    if (p < 0) return;
    String s = data.substring(p + 3);
    int q = s.indexOf("_w");
    if (q < 0) return;
    int idx = Integer.parseInt(s.substring(0, q));
    int amt = s.startsWith("64", q + 2) ? 64 : 1;
    if (this.rowItems == null || idx < 0 || idx >= this.rowItems.length) return;
    String id = this.rowItems[idx];
    java.util.UUID u = this.playerRef.getUuid();
    long have = {PKG}.SackPool.get(u, id);
    if (have <= 0L) return;
    long take = amt < have ? (long) amt : have;
    {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    Object tx = player.getInventory().getStorage().addItemStack(new {IS}(id, (int) take));
    {PKG}.SackPool.add(u, id, -take);
    {PKG}.SackPool.save(u);
    rebuild();
  }} catch (Throwable t) {{ }}
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
    if (player == null) {{ pr.sendMessage({MSG}.raw("SkyySacks: player not found")); return; }}
    player.getPageManager().openCustomPage(ref, store, new {PKG}.SacksPage(pr));
  }} catch (Throwable t) {{
    pr.sendMessage({MSG}.raw("SkyySacks error: " + t));
  }}
}}""", cmd))


# ==== TEST: GrantTask + SackReady ====
grt.addInterface(pool.get("java.lang.Runnable"))
grt.addField(CtField.make(f"public {PR} pr;", grt))
grt.addField(CtField.make("public boolean onWorld;", grt))
grt.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap GRANTED = new java.util.concurrent.ConcurrentHashMap();", grt))
grt.addConstructor(CtNewConstructor.make(f"public GrantTask({PR} pr) {{ this.pr = pr; this.onWorld = false; }}", grt))
grt.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (!this.onWorld) {{
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) return;
      {WLD} w = {UNI}.get().getWorld(wu);
      if (w == null) return;
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
    stor.addItemStack(new {IS}("Skyy_Sack_Mining_Small", 1));
    stor.addItemStack(new {IS}("Ore_Copper", 64));
    stor.addItemStack(new {IS}("Ore_Iron", 32));
    pr.sendMessage(com.hypixel.hytale.server.core.Message.raw("[SkyySacks test] granted: Small Mining Sack + copper/iron ore into storage - watch them pool. /sacks to view."));
  }} catch (Throwable t) {{ }}
}}""", grt))
srd.addInterface(pool.get("java.util.function.Consumer"))
srd.addConstructor(CtNewConstructor.make("public SackReady() { }", srd))
srd.addMethod(CtNewMethod.make(f"""
public void accept(Object ev) {{
  try {{
    com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent e = (com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent) ev;
    {REF} r = e.getPlayerRef();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    {HSV}.SCHEDULED_EXECUTOR.schedule(new {PKG}.GrantTask(pr), 4L, java.util.concurrent.TimeUnit.SECONDS);
  }} catch (Throwable t) {{ }}
}}""", srd))

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyySacksPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.SackPool.DIR = getDataDirectory().resolve("pools");
  getCommandRegistry().registerCommand(new {PKG}.SacksCmd());
  getEventRegistry().registerGlobal(com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent.class, new {PKG}.SackReady());
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SackTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.WARNING).log("[SkyySacks] 0.1-selftest ready - test items grant on join");
}}""", pl))

for c in (defs, sp, swp, tick, cmp, page, cmd, grt, srd, pl): c.writeFile(OUT)
print("classes written")

# ================= assets + jar =================
def sack_item(cat, tier, quality, recipe_in):
    return {
      "TranslationProperties": {"Name": f"server.items.Skyy_Sack_{cat}_{tier}.name"},
      "Categories": ["Items.Tools"],
      "Icon": "Icons/ItemsGenerated/Utility_Bag_Seed.png",
      "Quality": quality,
      "Recipe": {"Input": recipe_in, "BenchRequirement": [{"Type": "Crafting", "Id": "Workbench", "Categories": ["Workbench_Crafting"]}]},
      "Model": "Items/Back/BackpackBig.blockymodel",
      "Texture": "Items/Back/BackpackBig_Texture.png",
      "IconProperties": {"Scale": 0.455, "Translation": [1.19, 2.39], "Rotation": [0, 177.73, 0]},
      "Tags": {"Family": ["Leather"], "Type": ["Utility"]},
      "MaxStack": 1
    }
items, lang = {}, []
mats = {"Mining": "Ingredient_Bar_Copper", "Foraging": "Wood_Oak_Trunk", "Farming": "Food_Bread"}
for cat in ("Mining", "Foraging", "Farming"):
    items[f"Skyy_Sack_{cat}_Small"]  = sack_item(cat, "Small", "Common",   [{"ItemId": "Ingredient_Bolt_Wool", "Quantity": 3}, {"ItemId": mats[cat], "Quantity": 4}])
    items[f"Skyy_Sack_{cat}_Medium"] = sack_item(cat, "Medium", "Uncommon", [{"ItemId": f"Skyy_Sack_{cat}_Small", "Quantity": 1}, {"ItemId": "Ingredient_Bolt_Linen", "Quantity": 3}])
    items[f"Skyy_Sack_{cat}_Large"]  = sack_item(cat, "Large", "Rare",     [{"ItemId": f"Skyy_Sack_{cat}_Medium", "Quantity": 1}, {"ItemId": "Ingredient_Bolt_Silk", "Quantity": 3}])
    for tier in ("Small", "Medium", "Large"):
        lang.append(f"server.items.Skyy_Sack_{cat}_{tier}.name = {tier} {cat} Sack")
        lang.append(f"Skyy_Sack_{cat}_{tier}.name = {tier} {cat} Sack")
manifest = {
  "Group": "Skyy", "Name": "0.1 SkyySacks", "Version": "0.1.0",
  "Description": "SkyBlock-style sacks: craft a sack, matching pickups pool automatically, /sacks to view and withdraw. Zero dependencies.",
  "Authors": [{"Name": "Skyy"}], "ServerVersion": "*", "DisabledByDefault": False,
  "IncludesAssetPack": True, "Main": "com.skyy.sacks.SkyySacksPlugin"
}
jar = "/tmp/SkyySacks.jar"
with zipfile.ZipFile(jar, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("manifest.json", json.dumps(manifest, indent=2))
    for iid, node in items.items():
        z.writestr(f"Server/Item/Items/Utility/{iid}.json", json.dumps(node, indent=2))
    z.writestr("Server/Languages/en-US/Items.lang", "\n".join(lang) + "\n")
    for root, _, files in os.walk(OUT):
        for f in files:
            if f.endswith(".class"):
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, OUT).replace(os.sep, "/"))
print("assembled", jar, os.path.getsize(jar), "bytes")
