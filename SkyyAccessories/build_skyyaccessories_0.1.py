"""SkyyAccessories 0.1 - build script (javassist via jpype). Accessory bag + bench accessories (Skyy's design 2026-09-23).
Run:   python build_skyyaccessories_0.1.py            -> SkyyAccessories/SkyyAccessories-0.1.jar
       python build_skyyaccessories_0.1.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Design (pattern copied from TerrariaAddons' AccessoryPouchSharedContainer: per-player container persisted to a file, opened from the
item's Secondary interaction; effects are checked, never "applied"):
 - Item Skyy_Accessory_Bag (Fieldcraft recipe): right-click -> page "SkyyAccBag" (/accessories or /acc also opens it).
   6 slots stored in Skyy_SkyyAccessories/bags/<uuid>.properties (slot0..slot5 = item id). Equip moves the item out of your
   inventory into the bag; Unequip gives it back (if your storage is full the item stays in the bag).
 - Bench accessories Skyy_Accessory_<BenchId>_T<n>: one per bench tier. T1 = the bench item + 4 copper bars at a Workbench;
   T(n+1) = T(n) + exactly the materials the real bench needs to upgrade to that tier (from the bench's TierLevels).
   Only one accessory per bench fits in the bag; equipping a higher tier hands the lower one back.
 - Bridge: "acc:has:<uuid>" -> "id,id" (what is in the bag) republished on every change and for every online player (5s tick);
   "acc:fn:has" -> java.util.function.Function apply(Object[]{UUID, String itemId}) -> Boolean. SkyySacks 0.6.1 reads acc:has to
   add a craft-page tab per bench accessory (recipes filtered by BenchRequirement.requiredTierLevel <= accessory tier).
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
MSG = "com.hypixel.hytale.server.core.Message"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
LOG = "com.hypixel.hytale.logger.HytaleLogger"
PAGE= "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
LIFE= "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime"
UCB = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
UEB = "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"
EVD = "com.hypixel.hytale.server.core.ui.builder.EventData"
BT  = "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
INV = "com.hypixel.hytale.server.core.inventory.Inventory"
IC  = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
IS  = "com.hypixel.hytale.server.core.inventory.ItemStack"
IST = "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction"
ISS = "com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction"
OCU = "com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction"

for c, m in ((PLA, "getInventory"), (INV, "getStorage"), (INV, "getHotbar"), (INV, "getBackpack"), (IC, "getItemStack"), (IC, "removeItemStackFromSlot"),
             (IC, "addItemStack"), (IC, "getCapacity"), (OCU, "registerSimple"), (HSV, "SCHEDULED_EXECUTOR"), (UNI, "getPlayers"),
             (PAGE, "rebuild"), ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):
    B.probe(pool, c, m)

PKG = "com.skyy.accessories"
dfs  = pool.makeClass(PKG + ".AccDefs")
st_  = pool.makeClass(PKG + ".AccStore")
fn   = pool.makeClass(PKG + ".AccFn")
page = pool.makeClass(PKG + ".AccPage", pool.get(PAGE))
fac  = pool.makeClass(PKG + ".AccPageFactory")
cmd  = pool.makeClass(PKG + ".AccCmd", pool.get(APC))
tick = pool.makeClass(PKG + ".AccTick")
pl   = pool.makeClass(PKG + ".SkyyAccessoriesPlugin", pool.get(JP))

# (benchId, bench item id, display name, tiers, [upgrade materials to reach T2, T3, ...])
BENCHES = [
    ("Workbench",      "Bench_WorkBench", "Workbench",      3, [[("Ingredient_Bar_Copper", 30), ("Ingredient_Bar_Iron", 20), ("Ingredient_Fabric_Scrap_Linen", 20)],
                                                               [("Ingredient_Bar_Thorium", 30), ("Ingredient_Bar_Cobalt", 20), ("Ingredient_Leather_Heavy", 30), ("Ingredient_Fabric_Scrap_Shadoweave", 50), ("Ingredient_Fire_Essence", 25)]]),
    ("Armor_Bench",    "Bench_Armour",    "Armor Bench",    3, [[("Ingredient_Bar_Copper", 20), ("Ingredient_Bone_Fragment", 20), ("Ingredient_Leather_Medium", 20), ("Wood_Azure_Trunk", 100)],
                                                               [("Ingredient_Bar_Thorium", 25), ("Ingredient_Bar_Cobalt", 25), ("Ingredient_Fabric_Scrap_Shadoweave", 40), ("Ingredient_Chitin_Sturdy", 40), ("Ingredient_Voidheart", 3)]]),
    ("Weapon_Bench",   "Bench_Weapon",    "Weapon Bench",   3, [[("Ingredient_Bar_Iron", 20), ("Ingredient_Leather_Light", 30), ("Ingredient_Fabric_Scrap_Linen", 30), ("Ingredient_Sac_Venom", 15)],
                                                               [("Ingredient_Bar_Thorium", 25), ("Ingredient_Bar_Cobalt", 25), ("Ingredient_Fire_Essence", 20), ("Ingredient_Ice_Essence", 40), ("Ingredient_Void_Essence", 100)]]),
    ("Alchemybench",   "Bench_Alchemy",   "Alchemy Bench",  4, [[("Ingredient_Bar_Silver", 5), ("Ingredient_Bar_Gold", 10), ("Ingredient_Sac_Venom", 10), ("Rock_Gem_Emerald", 1)],
                                                               [("Ingredient_Bar_Silver", 10), ("Ingredient_Bar_Gold", 20), ("Ingredient_Chitin_Sturdy", 20), ("Rock_Gem_Zephyr", 1)],
                                                               [("Ingredient_Bar_Silver", 20), ("Ingredient_Bar_Gold", 40), ("Ingredient_Fabric_Scrap_Shadoweave", 30), ("Rock_Gem_Sapphire", 1)]]),
    ("Farmingbench",   "Bench_Farming",   "Farming Bench",  7, [[("Ingredient_Life_Essence", 50), ("Plant_Crop_Wheat_Item", 5), ("Plant_Crop_Lettuce_Item", 5), ("Wood_Softwood_Trunk", 5)],
                                                               [("Ingredient_Life_Essence_Concentrated", 1), ("Plant_Crop_Carrot_Item", 10), ("Plant_Crop_Corn_Item", 10), ("Wood_Lightwood_Trunk", 10)],
                                                               [("Ingredient_Life_Essence_Concentrated", 2), ("Plant_Crop_Cauliflower_Item", 20), ("Plant_Crop_Turnip_Item", 20), ("Wood_Hardwood_Trunk", 20)],
                                                               [("Ingredient_Life_Essence_Concentrated", 3), ("Plant_Crop_Aubergine_Item", 30), ("Plant_Crop_Pumpkin_Item", 30), ("Wood_Drywood_Trunk", 30)],
                                                               [("Ingredient_Life_Essence_Concentrated", 4), ("Plant_Crop_Tomato_Item", 40), ("Plant_Crop_Chilli_Item", 40), ("Wood_Darkwood_Trunk", 40)],
                                                               [("Ingredient_Life_Essence_Concentrated", 5), ("Plant_Crop_Cotton_Item", 50), ("Plant_Crop_Rice_Item", 50), ("Wood_Redwood_Trunk", 50)]]),
    ("Furnace",        "Bench_Furnace",   "Furnace",        2, [[("Ingredient_Bar_Copper", 5), ("Ingredient_Bar_Iron", 5), ("Ingredient_Bar_Thorium", 5), ("Ingredient_Bar_Cobalt", 5)]]),
    ("Tannery",        "Bench_Tannery",   "Tannery",        2, [[("Ingredient_Leather_Light", 5), ("Ingredient_Leather_Medium", 5), ("Ingredient_Leather_Heavy", 5), ("Ingredient_Chitin_Sturdy", 5)]]),
    ("Arcanebench",    "Bench_Arcane",    "Arcane Bench",   1, []),
    ("Cookingbench",   "Bench_Cooking",   "Cooking Bench",  1, []),
    ("Furniture_Bench","Bench_Furniture", "Furniture Bench",1, []),
    ("Loombench",      "Bench_Loom",      "Loom",           1, []),
    ("Salvagebench",   "Bench_Salvage",   "Salvage Bench",  1, []),
    ("Campfire",       "Bench_Campfire",  "Campfire",       1, []),
]
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII"]
BAG = "Skyy_Accessory_Bag"
CAP = 6

# ================= AccDefs =================
bench_ids = ", ".join('"%s"' % b[0] for b in BENCHES)
bench_names = ", ".join('"%s"' % b[2] for b in BENCHES)
dfs.addField(CtField.make('public static final String BAG = "%s";' % BAG, dfs))
dfs.addField(CtField.make('public static final String[] BENCH_IDS = new String[] { %s };' % bench_ids, dfs))
dfs.addField(CtField.make('public static final String[] BENCH_NAMES = new String[] { %s };' % bench_names, dfs))
dfs.addMethod(CtNewMethod.make("""
public static boolean isAccessory(String id) {
  return id != null && id.startsWith("Skyy_Accessory_") && !id.equals(BAG);
}""", dfs))
# "Skyy_Accessory_Workbench_T2" -> "Workbench" ; ids without _T<n> -> whole tail
dfs.addMethod(CtNewMethod.make("""
public static String benchOf(String id) {
  if (!isAccessory(id)) return null;
  String tail = id.substring("Skyy_Accessory_".length());
  int t = tail.lastIndexOf("_T");
  if (t > 0) {
    boolean digits = t + 2 < tail.length();
    for (int i = t + 2; i < tail.length(); i++) if (!Character.isDigit(tail.charAt(i))) digits = false;
    if (digits) return tail.substring(0, t);
  }
  return tail;
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static int tierOf(String id) {
  if (!isAccessory(id)) return 0;
  int t = id.lastIndexOf("_T");
  if (t < 0 || t + 2 >= id.length()) return 1;
  try { return Integer.parseInt(id.substring(t + 2)); } catch (Throwable e) { return 1; }
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static String roman(int t) {
  String[] r = new String[] { "", "I", "II", "III", "IV", "V", "VI", "VII", "VIII" };
  return t >= 0 && t < r.length ? r[t] : String.valueOf(t);
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static String pretty(String id) {
  String b = benchOf(id);
  if (b == null) return id == null ? "?" : id;
  for (int i = 0; i < BENCH_IDS.length; i++) if (BENCH_IDS[i].equals(b)) return BENCH_NAMES[i] + " " + roman(tierOf(id));
  return b.replace('_', ' ') + " " + roman(tierOf(id));
}""", dfs))

# ================= AccStore =================
st_.addField(CtField.make("public static java.nio.file.Path DIR;", st_))
st_.addField(CtField.make(f"public static {LOG} LOG;", st_))
st_.addField(CtField.make("public static final int CAP = %d;" % CAP, st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BAGS = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBLISHED = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyAccessories] " + msg); } catch (Throwable t) { }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static synchronized String[] slots(java.util.UUID u) {
  String[] s = (String[]) BAGS.get(u);
  if (s != null) return s;
  s = new String[CAP];
  try {
    java.nio.file.Path f = DIR.resolve(u.toString() + ".properties");
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
      for (int i = 0; i < CAP; i++) {
        String v = p.getProperty("slot" + i);
        if (v != null && v.trim().length() > 0) s[i] = v.trim();
      }
    }
  } catch (Throwable t) { warn("could not load bag for " + u + ": " + t); }
  BAGS.put(u, s);
  return s;
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static synchronized void publish(java.util.UUID u) {
  String[] s = slots(u);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length; i++) if (s[i] != null) { if (sb.length() > 0) sb.append(','); sb.append(s[i]); }
  bridge().put("acc:has:" + u.toString(), sb.toString());
  PUBLISHED.put(u, Boolean.TRUE);
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static synchronized void save(java.util.UUID u) {
  try {
    String[] s = slots(u);
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.util.Properties p = new java.util.Properties();
    for (int i = 0; i < s.length; i++) if (s[i] != null) p.setProperty("slot" + i, s[i]);
    java.nio.file.Path tmp = DIR.resolve(u.toString() + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyyAccessories bag"); } finally { out.close(); }
    java.nio.file.Files.move(tmp, DIR.resolve(u.toString() + ".properties"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  } catch (Throwable t) { warn("could not save bag for " + u + ": " + t); }
  publish(u);
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static synchronized boolean has(java.util.UUID u, String id) {
  String[] s = slots(u);
  for (int i = 0; i < s.length; i++) if (id != null && id.equals(s[i])) return true;
  return false;
}""", st_))
# equips id; returns the item id that was displaced (same bench, lower/equal tier) or "" when a free slot was used, or null when the bag is full / a better one is in
st_.addMethod(CtNewMethod.make(f"""
public static synchronized String equip(java.util.UUID u, String id) {{
  String[] s = slots(u);
  String bench = {PKG}.AccDefs.benchOf(id);
  int tier = {PKG}.AccDefs.tierOf(id);
  for (int i = 0; i < s.length; i++) {{
    if (s[i] == null) continue;
    if (bench != null && bench.equals({PKG}.AccDefs.benchOf(s[i]))) {{
      if ({PKG}.AccDefs.tierOf(s[i]) >= tier) return null;
      String old = s[i]; s[i] = id; save(u); return old;
    }}
  }}
  for (int i = 0; i < s.length; i++) if (s[i] == null) {{ s[i] = id; save(u); return ""; }}
  return null;
}}""", st_))
st_.addMethod(CtNewMethod.make("""
public static synchronized String unequip(java.util.UUID u, int idx) {
  String[] s = slots(u);
  if (idx < 0 || idx >= s.length || s[idx] == null) return null;
  String id = s[idx]; s[idx] = null; save(u); return id;
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static synchronized void put(java.util.UUID u, int idx, String id) {
  String[] s = slots(u);
  if (idx < 0 || idx >= s.length) return;
  s[idx] = id; save(u);
}""", st_))
st_.addMethod(CtNewMethod.make(f"""
public static void publishOnline() {{
  try {{
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      online.add(u);
      if (!PUBLISHED.containsKey(u)) publish(u);
    }}
    PUBLISHED.keySet().retainAll(online);
  }} catch (Throwable t) {{ }}
}}""", st_))

# ================= AccFn (bridge function acc:fn:has) =================
fn.addInterface(pool.get("java.util.function.Function"))
fn.addConstructor(CtNewConstructor.make("public AccFn() { }", fn))
fn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    Object[] a = (Object[]) arg;
    return Boolean.valueOf({PKG}.AccStore.has((java.util.UUID) a[0], String.valueOf(a[1])));
  }} catch (Throwable t) {{ return Boolean.FALSE; }}
}}""", fn))

# ================= AccPage =================
page.addField(CtField.make("public String info;", page))
page.addField(CtField.make("public String[] invIds;", page))
page.addConstructor(CtNewConstructor.make(f"""
public AccPage({PR} pr) {{
  super(pr, {LIFE}.CanDismiss);
  this.info = "";
}}""", page))
page.addMethod(CtNewMethod.make("""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ');
}""", page))
# accessory item ids carried in storage/hotbar/backpack (distinct)
page.addMethod(CtNewMethod.make(f"""
public static java.util.ArrayList carried({PLA} p) {{
  java.util.ArrayList out = new java.util.ArrayList();
  {INV} inv = p.getInventory();
  if (inv == null) return out;
  {IC}[] scan = new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }};
  for (int c = 0; c < scan.length; c++) {{
    {IC} cont = scan[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {{
      {IS} it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if ({PKG}.AccDefs.isAccessory(id) && !out.contains(id)) out.add(id);
    }}
  }}
  return out;
}}""", page))
# remove one of item id from any inventory section; true when removed
page.addMethod(CtNewMethod.make(f"""
public static boolean takeOne({PLA} p, String id) {{
  {INV} inv = p.getInventory();
  if (inv == null) return false;
  {IC}[] scan = new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }};
  for (int c = 0; c < scan.length; c++) {{
    {IC} cont = scan[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {{
      {IS} it = cont.getItemStack(s);
      if (it == null || it.isEmpty() || !id.equals(it.getItemId())) continue;
      {ISS} tx = cont.removeItemStackFromSlot(s, 1);
      if (tx != null && tx.succeeded()) return true;
    }}
  }}
  return false;
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public static boolean giveOne({PLA} p, String id) {{
  try {{
    {IST} tx = p.getInventory().getStorage().addItemStack(new {IS}(id, 1));
    if (tx != null && tx.succeeded()) return true;
    tx = p.getInventory().getHotbar().addItemStack(new {IS}(id, 1));
    if (tx != null && tx.succeeded()) return true;
    {IC} bp = p.getInventory().getBackpack();
    if (bp == null) return false;
    tx = bp.addItemStack(new {IS}(id, 1));
    return tx != null && tx.succeeded();
  }} catch (Throwable t) {{ return false; }}
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
  String[] s = {PKG}.AccStore.slots(u);
  String bs = "Style: TextButtonStyle(Default: (Background: #5a4420, LabelStyle: (FontSize: 12, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  b.appendInline((String) null, "Group #SkyyAcc {{ Anchor: (Width: 620, Height: 500); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyyAcc", "Group {{ Anchor: (Height: 2); Background: #8fd0ff; }}");
  b.appendInline("#SkyyAcc", "Label {{ Anchor: (Height: 30); Text: \\"Accessory Bag\\"; Style: (FontSize: 16, RenderBold: true, TextColor: #e6f4ff, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyAcc", "Label {{ Anchor: (Height: 18); Text: \\"Bench accessories in here let /craft make that bench's recipes from your inventory.\\"; Style: (FontSize: 11, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  for (int i = 0; i < s.length; i++) {{
    b.appendInline("#SkyyAcc", "Group #SkyyAccSlot" + i + " {{ Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 4); Background: #142030(0.9); }}");
    if (s[i] != null) {{
      b.appendInline("#SkyyAccSlot" + i, "Group {{ Anchor: (Width: 40, Height: 36); ItemIcon {{ Anchor: (Width: 32, Height: 32, Left: 4, Top: 2); ItemId: \\"" + safe(s[i]) + "\\"; }} }}");
      b.appendInline("#SkyyAccSlot" + i, "Label {{ Anchor: (Width: 380, Height: 36); Text: \\"" + safe({PKG}.AccDefs.pretty(s[i])) + "\\"; Style: (FontSize: 13, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }}");
      b.appendInline("#SkyyAccSlot" + i, "TextButton #SkyyAccUn" + i + " {{ Anchor: (Width: 120, Height: 30); Text: \\"Unequip\\"; " + bs + " }}");
      ev.addEventBinding({BT}.Activating, "#SkyyAccUn" + i, {EVD}.of("a", "un:" + i));
    }} else {{
      b.appendInline("#SkyyAccSlot" + i, "Label {{ Anchor: (Width: 560, Height: 36); Text: \\"  empty slot\\"; Style: (FontSize: 12, TextColor: #5f7a90, VerticalAlignment: Center); }}");
    }}
  }}
  b.appendInline("#SkyyAcc", "Label {{ Anchor: (Height: 22); Text: \\"Accessories in your inventory\\"; Style: (FontSize: 12, RenderBold: true, TextColor: #c9dff0, VerticalAlignment: Center); }}");
  java.util.ArrayList inv = player == null ? new java.util.ArrayList() : carried(player);
  this.invIds = new String[inv.size()];
  if (inv.isEmpty()) b.appendInline("#SkyyAcc", "Label {{ Anchor: (Height: 20); Text: \\"  none - craft a bench accessory at a Workbench (bench + 4 copper bars)\\"; Style: (FontSize: 11, TextColor: #5f7a90, VerticalAlignment: Center); }}");
  for (int i = 0; i < inv.size() && i < 4; i++) {{
    String id = (String) inv.get(i);
    this.invIds[i] = id;
    b.appendInline("#SkyyAcc", "Group #SkyyAccInv" + i + " {{ Anchor: (Height: 36); LayoutMode: Left; Padding: (Top: 2); }}");
    b.appendInline("#SkyyAccInv" + i, "Group {{ Anchor: (Width: 40, Height: 34); ItemIcon {{ Anchor: (Width: 30, Height: 30, Left: 5, Top: 2); ItemId: \\"" + safe(id) + "\\"; }} }}");
    b.appendInline("#SkyyAccInv" + i, "Label {{ Anchor: (Width: 380, Height: 34); Text: \\"" + safe({PKG}.AccDefs.pretty(id)) + "\\"; Style: (FontSize: 12, TextColor: #ffffff, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyAccInv" + i, "TextButton #SkyyAccEq" + i + " {{ Anchor: (Width: 120, Height: 28); Text: \\"Equip\\"; " + bs + " }}");
    ev.addEventBinding({BT}.Activating, "#SkyyAccEq" + i, {EVD}.of("a", "eq:" + i));
  }}
  b.appendInline("#SkyyAcc", "Label #SkyyAccInfo {{ Anchor: (Height: 22); Text: \\"" + safe(this.info) + "\\"; Style: (FontSize: 12, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    for (int i = 0; i < {PKG}.AccStore.CAP; i++) {{
      if (data.indexOf("un:" + i + "\\"") < 0) continue;
      String id = {PKG}.AccStore.unequip(u, i);
      if (id == null) return;
      if (!giveOne(player, id)) {{ {PKG}.AccStore.put(u, i, id); this.info = "your inventory is full"; }}
      else this.info = "unequipped " + {PKG}.AccDefs.pretty(id);
      rebuild(); return;
    }}
    for (int i = 0; i < 4; i++) {{
      if (data.indexOf("eq:" + i + "\\"") < 0) continue;
      if (this.invIds == null || i >= this.invIds.length || this.invIds[i] == null) return;
      String id = this.invIds[i];
      if (!takeOne(player, id)) {{ this.info = "could not find " + {PKG}.AccDefs.pretty(id) + " in your inventory"; rebuild(); return; }}
      String res = {PKG}.AccStore.equip(u, id);
      if (res == null) {{ giveOne(player, id); this.info = "bag is full, or a better " + {PKG}.AccDefs.pretty(id) + " is already equipped"; rebuild(); return; }}
      if (res.length() > 0) {{ if (!giveOne(player, res)) {{ this.info = "equipped " + {PKG}.AccDefs.pretty(id) + " (old one dropped: inventory full)"; }} else this.info = "upgraded to " + {PKG}.AccDefs.pretty(id) + ", " + {PKG}.AccDefs.pretty(res) + " returned"; }}
      else this.info = "equipped " + {PKG}.AccDefs.pretty(id);
      rebuild(); return;
    }}
  }} catch (Throwable t) {{ {PKG}.AccStore.warn("bag page event failed: " + t); }}
}}""", page))

fac.addInterface(pool.get("java.util.function.Function"))
fac.addConstructor(CtNewConstructor.make("public AccPageFactory() { }", fac))
fac.addMethod(CtNewMethod.make(f"""
public Object apply(Object o) {{
  return new {PKG}.AccPage(({PR}) o);
}}""", fac))

# ================= /accessories =================
cmd.addConstructor(CtNewConstructor.make("""
public AccCmd() {
  super("accessories", "Open your accessory bag");
  addAliases(new String[] { "acc", "accbag" });
}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new {PKG}.AccPage(pr));
  }} catch (Throwable t) {{
    {PKG}.AccStore.warn("/accessories failed: " + t);
    pr.sendMessage({MSG}.raw("[Accessories] could not open the bag"));
  }}
}}""", cmd))

tick.addInterface(pool.get("java.lang.Runnable"))
tick.addConstructor(CtNewConstructor.make("public AccTick() { }", tick))
tick.addMethod(CtNewMethod.make(f"public void run() {{ {PKG}.AccStore.publishOnline(); }}", tick))

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyyAccessoriesPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.AccStore.LOG = getLogger();
  {PKG}.AccStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("bags");
  {OCU}.registerSimple(this, {PKG}.SkyyAccessoriesPlugin.class, "SkyyAccBag", new {PKG}.AccPageFactory());
  getCommandRegistry().registerCommand(new {PKG}.AccCmd());
  {PKG}.AccStore.bridge().put("acc:fn:has", new {PKG}.AccFn());
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.AccTick(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyAccessories] {VERSION} ready - /accessories, right-click the Accessory Bag; %d bench accessories" );
}}""" % (len(BENCHES) and sum(b[3] for b in BENCHES)), pl))
pl.addMethod(CtNewMethod.make("""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { com.skyy.accessories.AccStore.bridge().remove("acc:fn:has"); } catch (Throwable t) { }
  super.shutdown();
}""", pl))

for c in (dfs, st_, fn, page, fac, cmd, tick, pl):
    c.writeFile(OUT)
print("classes written")

# ================= assets: items + lang =================
def item(iid, icon, quality, recipe_in, bench_req, page_id=None):
    node = {
      "TranslationProperties": {"Name": "server.items.%s.name" % iid, "Description": "server.items.%s.description" % iid},
      "Categories": ["Items.Tools"],
      "Icon": icon,
      "Quality": quality,
      "Recipe": {"Input": recipe_in, "BenchRequirement": bench_req},
      "Model": "Items/Back/BackpackBig.blockymodel",
      "Texture": "Items/Back/BackpackBig_Texture.png",
      "IconProperties": {"Scale": 0.455, "Translation": [1.19, 2.39], "Rotation": [0, 177.73, 0]},
      "Tags": {"Family": ["Leather"], "Type": ["Utility"]},
      "MaxStack": 1,
    }
    if page_id:
        node["Interactions"] = {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": page_id}}]}}
    return node

WB_REQ = [{"Type": "Crafting", "Id": "Workbench", "Categories": ["Workbench_Crafting"]}]
FIELD_REQ = [{"Type": "Crafting", "Id": "Fieldcraft", "Categories": ["Tools"]}]
QUAL = ["Common", "Common", "Uncommon", "Rare", "Rare", "Rare", "Rare", "Rare"]
files = {}
lang = []
files["Server/Item/Items/Utility/%s.json" % BAG] = json.dumps(item(BAG, "Icons/ItemsGenerated/Utility_Bag_Seed.png", "Uncommon",
    [{"ResourceTypeId": "Wood_Trunk", "Quantity": 4}, {"ItemId": "Ingredient_Fabric_Scrap_Cotton", "Quantity": 4}], FIELD_REQ, "SkyyAccBag"), indent=2)
lang.append("items.%s.name=Accessory Bag" % BAG); lang.append("server.items.%s.name=Accessory Bag" % BAG)
d = "Right-click to open. Holds up to %d accessories. Bench accessories in it let /craft make that bench's recipes straight from your inventory." % CAP
lang.append("items.%s.description=%s" % (BAG, d)); lang.append("server.items.%s.description=%s" % (BAG, d))
count = 0
for bench_id, bench_item, name, tiers, ups in BENCHES:
    for t in range(1, tiers + 1):
        iid = "Skyy_Accessory_%s_T%d" % (bench_id, t)
        if t == 1:
            rin = [{"ItemId": bench_item, "Quantity": 1}, {"ItemId": "Ingredient_Bar_Copper", "Quantity": 4}]
        else:
            rin = [{"ItemId": "Skyy_Accessory_%s_T%d" % (bench_id, t - 1), "Quantity": 1}] + [{"ItemId": m, "Quantity": q} for m, q in ups[t - 2]]
        icon = "Icons/ItemsGenerated/%s.png" % ("Bench_Architects" if bench_item == "Bench_Builders" else bench_item)
        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(item(iid, icon, QUAL[min(t, 7)], rin, WB_REQ), indent=2)
        disp = "%s Accessory %s" % (name, ROMAN[t]) if tiers > 1 else "%s Accessory" % name
        lang.append("items.%s.name=%s" % (iid, disp)); lang.append("server.items.%s.name=%s" % (iid, disp))
        d = "Put it in your Accessory Bag to craft %s recipes%s from your inventory with /craft.%s" % (
            name, (" up to tier %s" % ROMAN[t]) if tiers > 1 else "",
            (" Upgrade it with the same materials the bench needs for tier %s." % ROMAN[t + 1]) if t < tiers else "")
        lang.append("items.%s.description=%s" % (iid, d)); lang.append("server.items.%s.description=%s" % (iid, d))
        count += 1
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"
print("accessory items:", count)

jar = os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)
B.assemble(jar, B.manifest("SkyyAccessories", VERSION, "SkyWynn accessory bag: equip bench accessories so /craft (SkyySacks) can make that bench's recipes from your inventory. Zero dependencies.", PKG + ".SkyyAccessoriesPlugin"), OUT, files)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyAccessories.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyAccessories" % VERSION, disable_prefix="Skyy:")
