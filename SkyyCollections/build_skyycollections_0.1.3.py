"""SkyyCollections 0.1.3 - build script
0.1.3: recipe unlocks published to the bridge (coll:recipes:<uuid>), auto rule + unlocks.properties, /collections unlocks|reload. (javassist via jpype).
Run:   python build_skyycollections_0.1.2.py            -> SkyyCollections/SkyyCollections-0.1.1.jar
       python build_skyycollections_0.1.2.py --deploy   -> also copies to Mods/SkyyCollections.jar and enables it in the HUD mod world
Fixes vs 0.1 (code review 2026-09-22): page build() is public and fully inline (no .ui files, no underscores in IDs), saver cancelled + final
flush on shutdown, race-free counts() load, atomic file writes, streams closed on error paths, BlockType id cast,
friendlier names in chat/page, failures logged.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1.3"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PAGE= "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
LIFE= "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
MSG = "com.hypixel.hytale.server.core.Message"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
OA  = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
CRR = "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe"
MQ  = "com.hypixel.hytale.server.core.inventory.MaterialQuantity"
UCB = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
UEB = "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"
EES = "com.hypixel.hytale.component.system.EntityEventSystem"
ACH = "com.hypixel.hytale.component.ArchetypeChunk"
CB  = "com.hypixel.hytale.component.CommandBuffer"
EV  = "com.hypixel.hytale.component.system.EcsEvent"
BBE = "com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent"
QRY = "com.hypixel.hytale.component.query.Query"
BTY = "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType"
LOG = "com.hypixel.hytale.logger.HytaleLogger"

for c, m in ((CRR, "getInput"), (CRR, "getAssetMap"), (MQ, "getItemId"), (UNI, "getPlayers"), (PR, "hasPermission"), ("com.hypixel.hytale.server.core.command.system.CommandContext", "provided"),
             (BBE, "getBlockType"), (BTY, "getId"), (ACH, "getReferenceTo"), (HSV, "SCHEDULED_EXECUTOR"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"), ("com.hypixel.hytale.component.Archetype", "empty")):
    B.probe(pool, c, m)

PKG = "com.skyy.collections"
store = pool.makeClass(PKG + ".CollStore")
sysc  = pool.makeClass(PKG + ".CollSystem", pool.get(EES))
unl   = pool.makeClass(PKG + ".CollUnlocks")
sav   = pool.makeClass(PKG + ".CollSaver")
ccmp  = pool.makeClass(PKG + ".CollCmp")
page  = pool.makeClass(PKG + ".CollPage", pool.get(PAGE))
cmd   = pool.makeClass(PKG + ".CollCmd", pool.get(APC))
pl    = pool.makeClass(PKG + ".SkyyCollectionsPlugin", pool.get(JP))
ROWS = 14

# ================= CollStore =================
store.addField(CtField.make("public static java.nio.file.Path DIR;", store))
store.addField(CtField.make(f"public static {LOG} LOG;", store))
store.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DATA = new java.util.concurrent.ConcurrentHashMap();", store))
store.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();", store))
store.addField(CtField.make("public static final long[] TIERS = new long[] { 50L, 250L, 1000L, 5000L, 20000L };", store))
store.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyCollections] " + msg); } catch (Throwable t) { }
}""", store))
store.addMethod(CtNewMethod.make("""
public static java.util.Map counts(java.util.UUID u) {
  java.util.Map m = (java.util.Map) DATA.get(u);
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
        try { m.put(k, Long.valueOf(Long.parseLong(p.getProperty(k).trim()))); } catch (Throwable t) { }
      }
    }
  } catch (Throwable t) { warn("could not load counts for " + u + ": " + t); }
  java.util.Map prev = (java.util.Map) DATA.putIfAbsent(u, m);
  return prev != null ? prev : m;
}""", store))
store.addMethod(CtNewMethod.make("""
public static void save(java.util.UUID u) {
  try {
    java.util.Map m = (java.util.Map) DATA.get(u);
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
    try { p.store(out, "SkyyCollections"); } finally { out.close(); }
    java.nio.file.Files.move(tmp, DIR.resolve(u.toString() + ".properties"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  } catch (Throwable t) { warn("could not save counts for " + u + ": " + t); }
}""", store))
store.addMethod(CtNewMethod.make("""
public static void flushDirty() {
  java.util.Iterator it = DIRTY.keySet().iterator();
  while (it.hasNext()) {
    java.util.UUID u = (java.util.UUID) it.next();
    it.remove();
    save(u);
  }
}""", store))
store.addMethod(CtNewMethod.make("""
public static int tierOf(long n) {
  int t = 0;
  for (int i = 0; i < TIERS.length; i++) if (n >= TIERS[i]) t = i + 1;
  return t;
}""", store))
store.addMethod(CtNewMethod.make("""
public static String roman(int t) {
  String[] r = new String[] { "0", "I", "II", "III", "IV", "V" };
  return t >= 0 && t < r.length ? r[t] : String.valueOf(t);
}""", store))
store.addMethod(CtNewMethod.make("""
public static String pretty(String id) {
  if (id == null) return "?";
  String s = id.replace('_', ' ');
  int q = s.indexOf(':');
  if (q >= 0 && q + 1 < s.length()) s = s.substring(q + 1);
  return s;
}""", store))
# returns new tier if a milestone was crossed, else 0
store.addMethod(CtNewMethod.make("""
public static synchronized int bump(java.util.UUID u, String id, long n) {
  java.util.Map m = counts(u);
  Long v = (Long) m.get(id);
  long oldv = v == null ? 0L : v.longValue();
  long newv = oldv + n;
  m.put(id, Long.valueOf(newv));
  DIRTY.put(u, Boolean.TRUE);
  int ot = tierOf(oldv); int nt = tierOf(newv);
  return nt > ot ? nt : 0;
}""", store))

# ================= CollUnlocks (bridge publisher) =================
unl.addField(CtField.make("public static java.nio.file.Path FILE;", unl))
unl.addField(CtField.make("public static volatile boolean AUTO = true;", unl))
unl.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap TABLE = new java.util.concurrent.ConcurrentHashMap();", unl))
unl.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBLISHED = new java.util.concurrent.ConcurrentHashMap();", unl))
unl.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", unl))
unl.addMethod(CtNewMethod.make(f"""
public static synchronized void load() {{
  TABLE.clear();
  try {{
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {{
      java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
      String text = "# SkyyCollections recipe unlocks\\n"
        + "# auto=true : a recipe unlocks when one of its inputs reaches tier I (50 collected) and every input you have started\\n"
        + "#             collecting is at tier I or better (inputs you never collected are ignored)\\n"
        + "# explicit  : <CollectionId>.<tier 1-5>=RecipeId,RecipeId   e.g.  Rock_Stone.2=Rock_Stone_Brick\\n"
        + "# collection ids are the BLOCK ids you break (see /collections); recipe ids are CraftingRecipe asset ids (/craft shows names)\\n"
        + "auto=true\\n";
      java.nio.file.Files.write(FILE, text.getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    }}
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try {{ p.load(in); }} finally {{ in.close(); }}
    AUTO = !"false".equalsIgnoreCase(String.valueOf(p.getProperty("auto", "true")).trim());
    java.util.Enumeration en = p.propertyNames();
    while (en.hasMoreElements()) {{
      String k = ((String) en.nextElement()).trim();
      if (k.equals("auto")) continue;
      int dot = k.lastIndexOf('.');
      if (dot <= 0) continue;
      try {{
        int tier = Integer.parseInt(k.substring(dot + 1));
        if (tier < 1 || tier > 5) continue;
        TABLE.put(k, p.getProperty(k).trim());
      }} catch (Throwable t) {{ }}
    }}
  }} catch (Throwable t) {{ {PKG}.CollStore.warn("could not load unlocks.properties: " + t); }}
}}""", unl))
unl.addMethod(CtNewMethod.make(f"""
public static java.util.TreeSet compute(java.util.Map counts) {{
  java.util.TreeSet out = new java.util.TreeSet();
  if (counts == null || counts.isEmpty()) return out;
  try {{
    java.util.Iterator it = TABLE.entrySet().iterator();
    while (it.hasNext()) {{
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      String k = (String) e.getKey();
      int dot = k.lastIndexOf('.');
      String coll = k.substring(0, dot);
      int tier = Integer.parseInt(k.substring(dot + 1));
      Long c = (Long) counts.get(coll);
      if (c == null || {PKG}.CollStore.tierOf(c.longValue()) < tier) continue;
      String[] ids = ((String) e.getValue()).split(",");
      for (int i = 0; i < ids.length; i++) if (ids[i].trim().length() > 0) out.add(ids[i].trim());
    }}
    if (!AUTO) return out;
    long t1 = {PKG}.CollStore.TIERS[0];
    java.util.Iterator rit = {CRR}.getAssetMap().getAssetMap().values().iterator();
    while (rit.hasNext()) {{
      {CRR} r = ({CRR}) rit.next();
      if (r == null) continue;
      {MQ}[] in = r.getInput();
      if (in == null || in.length == 0) continue;
      boolean anyTier = false; boolean blocked = false;
      for (int i = 0; i < in.length; i++) {{
        if (in[i] == null) continue;
        String id = in[i].getItemId();
        if (id == null) continue;
        Long c = (Long) counts.get(id);
        if (c == null || c.longValue() <= 0L) continue;
        if (c.longValue() >= t1) anyTier = true; else blocked = true;
      }}
      if (anyTier && !blocked) {{ String rid = (String) r.getId(); if (rid != null) out.add(rid); }}
    }}
  }} catch (Throwable t) {{ {PKG}.CollStore.warn("unlock compute failed: " + t); }}
  return out;
}}""", unl))
unl.addMethod(CtNewMethod.make(f"""
public static int publish(java.util.UUID u) {{
  try {{
    java.util.TreeSet ids = compute({PKG}.CollStore.counts(u));
    StringBuilder sb = new StringBuilder();
    java.util.Iterator it = ids.iterator();
    while (it.hasNext()) {{ if (sb.length() > 0) sb.append(','); sb.append((String) it.next()); }}
    bridge().put("coll:recipes:" + u.toString(), sb.toString());
    PUBLISHED.put(u, Integer.valueOf(ids.size()));
    return ids.size();
  }} catch (Throwable t) {{ {PKG}.CollStore.warn("publish failed for " + u + ": " + t); return 0; }}
}}""", unl))
unl.addMethod(CtNewMethod.make(f"""
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
}}""", unl))
unl.addMethod(CtNewMethod.make("""
public static void republishAll() {
  java.util.Iterator it = new java.util.ArrayList(PUBLISHED.keySet()).iterator();
  while (it.hasNext()) publish((java.util.UUID) it.next());
}""", unl))

# ================= CollSystem (BreakBlockEvent listener) =================
sysc.addConstructor(CtNewConstructor.make(f"public CollSystem() {{ super({BBE}.class); }}", sysc))
sysc.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return com.hypixel.hytale.component.Archetype.empty();
}}""", sysc))
sysc.addMethod(CtNewMethod.make(f"""
public void handle(int idx, {ACH} chunk, {ST} st, {CB} buf, {EV} ev) {{
  try {{
    {BBE} e = ({BBE}) ev;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    {BTY} bt = e.getBlockType();
    if (bt == null) return;
    String id = (String) bt.getId();
    if (id == null) return;
    java.util.UUID u = pr.getUuid();
    int newTier = {PKG}.CollStore.bump(u, id, 1L);
    if (newTier > 0) {{
      int before = {PKG}.CollUnlocks.PUBLISHED.containsKey(u) ? ((Integer) {PKG}.CollUnlocks.PUBLISHED.get(u)).intValue() : 0;
      int now = {PKG}.CollUnlocks.publish(u);
      pr.sendMessage({MSG}.raw("Collection milestone! " + {PKG}.CollStore.pretty(id) + " " + {PKG}.CollStore.roman(newTier) + (now > before ? "  +" + (now - before) + " recipe(s) unlocked - /craft" : "")));
    }}
  }} catch (Throwable t) {{ {PKG}.CollStore.warn("break handler failed: " + t); }}
}}""", sysc))

sav.addInterface(pool.get("java.lang.Runnable"))
sav.addConstructor(CtNewConstructor.make("public CollSaver() { }", sav))
sav.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{ {PKG}.CollStore.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CollUnlocks.publishOnline(); }} catch (Throwable t) {{ }}
}}""", sav))

ccmp.addInterface(pool.get("java.util.Comparator"))
ccmp.addConstructor(CtNewConstructor.make("public CollCmp() { }", ccmp))
ccmp.addMethod(CtNewMethod.make("""
public int compare(Object a, Object b) {
  long x = ((Long) ((java.util.Map.Entry) a).getValue()).longValue();
  long y = ((Long) ((java.util.Map.Entry) b).getValue()).longValue();
  if (x != y) return x > y ? -1 : 1;
  return ((String) ((java.util.Map.Entry) a).getKey()).compareTo((String) ((java.util.Map.Entry) b).getKey());
}""", ccmp))

# ================= CollPage (static file + sets only) =================
page.addConstructor(CtNewConstructor.make(f"public CollPage({PR} pr) {{ super(pr, {LIFE}.CanDismiss); }}", page))
page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  java.util.ArrayList entries = new java.util.ArrayList({PKG}.CollStore.counts(u).entrySet());
  java.util.Collections.sort(entries, new {PKG}.CollCmp());
  int n = entries.size() < {ROWS} ? entries.size() : {ROWS};
  String summary = entries.size() == 0 ? "Nothing collected yet - go break some blocks!" : (entries.size() + " collections tracked" + (entries.size() > {ROWS} ? " (top {ROWS} shown)" : ""));
  b.appendInline((String) null, "Group #SkyyColl {{ Anchor: (Width: 560, Height: 460); Background: #0b1524(0.94); Padding: (Horizontal: 14, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyyColl", "Group {{ Anchor: (Height: 2); Background: #b48fe0; }}");
  b.appendInline("#SkyyColl", "Label {{ Anchor: (Height: 26); Text: \\"Collections\\"; Style: (FontSize: 15, RenderBold: true, TextColor: #f0e6ff, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyColl", "Label {{ Anchor: (Height: 16); Text: \\"" + summary + "\\"; Style: (FontSize: 11, TextColor: #c0b3d6, HorizontalAlignment: Center); }}");
  for (int i = 0; i < n; i++) {{
    java.util.Map.Entry e = (java.util.Map.Entry) entries.get(i);
    String id = (String) e.getKey();
    long cnt = ((Long) e.getValue()).longValue();
    int tier = {PKG}.CollStore.tierOf(cnt);
    long next = tier < 5 ? {PKG}.CollStore.TIERS[tier] : 0L;
    String prog = tier >= 5 ? "MAX" : (cnt + " / " + next);
    String name = {PKG}.CollStore.pretty(id).replace("\\"", "");
    b.appendInline("#SkyyColl", "Group #SkyyCRow" + i + " {{ Anchor: (Height: 24); LayoutMode: Left; }}");
    b.appendInline("#SkyyCRow" + i, "Label {{ Anchor: (Width: 330, Height: 20); Text: \\"" + name + "  " + {PKG}.CollStore.roman(tier) + "\\"; Style: (FontSize: 11, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyCRow" + i, "Label {{ Anchor: (Width: 170, Height: 20); Text: \\"" + prog + "\\"; Style: (FontSize: 11, TextColor: #9fd8a2, VerticalAlignment: Center); }}");
  }}
}}""", page))

# ================= command =================
cmd.addField(CtField.make(f"public {OA} actionArg;", cmd))
cmd.addConstructor(CtNewConstructor.make(f"""
public CollCmd() {{
  super("collections", "View your collections; /collections unlocks | reload");
  addAliases(new String[] {{ "coll" }});
  this.actionArg = withOptionalArg("action", "unlocks | reload", {ATY}.STRING);
}}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    if (ctx.provided(this.actionArg)) {{
      String a = String.valueOf(ctx.get(this.actionArg)).trim().toLowerCase();
      if (a.equals("unlocks") || a.equals("recipes")) {{
        java.util.TreeSet ids = {PKG}.CollUnlocks.compute({PKG}.CollStore.counts(pr.getUuid()));
        {PKG}.CollUnlocks.publish(pr.getUuid());
        StringBuilder sb = new StringBuilder();
        java.util.Iterator it = ids.iterator(); int n = 0;
        while (it.hasNext() && n < 12) {{ if (sb.length() > 0) sb.append(", "); sb.append({PKG}.CollStore.pretty((String) it.next())); n++; }}
        pr.sendMessage({MSG}.raw("[Collections] " + ids.size() + " recipe(s) unlocked" + (ids.size() > 0 ? ": " + sb + (ids.size() > 12 ? ", ..." : "") + "  -> /craft (Collections tab)" : ". Break blocks to reach tier I (50) of a material.")));
        return;
      }}
      if (a.equals("reload")) {{
        if (!pr.hasPermission("skyycollections.admin")) {{ pr.sendMessage({MSG}.raw("[Collections] no permission")); return; }}
        {PKG}.CollUnlocks.load();
        {PKG}.CollUnlocks.republishAll();
        pr.sendMessage({MSG}.raw("[Collections] unlocks.properties reloaded (" + {PKG}.CollUnlocks.TABLE.size() + " explicit rule(s), auto=" + {PKG}.CollUnlocks.AUTO + ")"));
        return;
      }}
    }}
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new {PKG}.CollPage(pr));
  }} catch (Throwable t) {{
    {PKG}.CollStore.warn("/collections failed: " + t);
    pr.sendMessage({MSG}.raw("[SkyyCollections] could not open the page"));
  }}
}}""", cmd))

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture saver;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyyCollectionsPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.CollStore.LOG = getLogger();
  {PKG}.CollStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyCollections").resolve("counts");
  {PKG}.CollUnlocks.FILE = getDataDirectory().resolveSibling("Skyy_SkyyCollections").resolve("unlocks.properties");
  {PKG}.CollUnlocks.load();
  getEntityStoreRegistry().registerSystem(new {PKG}.CollSystem());
  getCommandRegistry().registerCommand(new {PKG}.CollCmd());
  this.saver = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.CollSaver(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyCollections] {VERSION} ready - break blocks, /collections to view, unlocks auto=" + {PKG}.CollUnlocks.AUTO + " explicit=" + {PKG}.CollUnlocks.TABLE.size());
}}""", pl))
pl.addMethod(CtNewMethod.make(f"""
protected void shutdown() {{
  try {{ if (this.saver != null) this.saver.cancel(false); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CollStore.flushDirty(); }} catch (Throwable t) {{ }}
  super.shutdown();
}}""", pl))

for c in (store, unl, sysc, sav, ccmp, page, cmd, pl):
    c.writeFile(OUT)
print("classes written")

rows = "\n".join("""    Group #c_row_%d {
      Anchor: (Height: 24);
      LayoutMode: Left;
      Visible: false;
      Label #c_name_%d { Anchor: (Width: 330, Height: 20); Style: (FontSize: 11, RenderBold: true, TextColor: #ffffff); Text: ""; }
      Label #c_prog_%d { Anchor: (Width: 170, Height: 20); Style: (FontSize: 11, TextColor: #9fd8a2); Text: ""; }
    }""" % (i, i, i) for i in range(ROWS))
COLL_UI = """Group {
  Anchor: (Full: 0);
  Group #SkyyCollections {
    Anchor: (Horizontal: 0, Vertical: 0, Width: 560, Height: 460);
    Background: #0b1524(0.94);
    Padding: (Horizontal: 14, Vertical: 10);
    LayoutMode: Top;
    Group { Anchor: (Height: 2); Background: #b48fe0; }
    Label { Anchor: (Height: 26); Style: (FontSize: 15, RenderBold: true, TextColor: #f0e6ff, Alignment: Center); Text: "Collections"; }
    Label #c_summary { Anchor: (Height: 16); Style: (FontSize: 11, TextColor: #c0b3d6, Alignment: Center); Text: ""; }
%s
  }
}
""" % rows

jar = os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)
B.assemble(jar, B.manifest("SkyyCollections", VERSION, "SkyWynn collections: every block you break counts toward per-item milestones (I-V). /collections to view. Collection tiers unlock recipes for the SkyySacks craft page (auto rule + unlocks.properties).", PKG + ".SkyyCollectionsPlugin"),
           OUT, {})  # page built inline (no .ui files: see memory hytale-ui-rules)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyCollections.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyCollections" % VERSION, disable_prefix="Skyy:")
