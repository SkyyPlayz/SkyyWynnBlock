import jpype, sys, os, zipfile, json
from jdk4py import JAVA_HOME
jpype.startJVM(str(JAVA_HOME/"lib"/"server"/"libjvm.so"), "--add-opens=java.base/java.lang=ALL-UNNAMED", classpath=["/tmp/javassist/javassist.jar"])
J = jpype.JClass
ClassPool, CtField, CtNewMethod, CtNewConstructor = J("javassist.ClassPool"), J("javassist.CtField"), J("javassist.CtNewMethod"), J("javassist.CtNewConstructor")
REL = sys.argv[1]
pool = ClassPool(False); pool.appendSystemPath(); pool.appendClassPath(REL)
OUT = "/tmp/skyycoll_classes"; os.system(f"rm -rf {OUT}"); os.makedirs(OUT)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
MSG = "com.hypixel.hytale.server.core.Message"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
PAGE= "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
LIFE= "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime"
UCB = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
UEB = "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"
EES = "com.hypixel.hytale.component.system.EntityEventSystem"
ACH = "com.hypixel.hytale.component.ArchetypeChunk"
CB  = "com.hypixel.hytale.component.CommandBuffer"
EV  = "com.hypixel.hytale.component.system.EcsEvent"
BBE = "com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent"
QRY = "com.hypixel.hytale.component.query.Query"

PKG = "com.skyy.collections"
store = pool.makeClass(PKG + ".CollStore")
sysc  = pool.makeClass(PKG + ".CollSystem", pool.get(EES))
page  = pool.makeClass(PKG + ".CollPage", pool.get(PAGE))
ccmp  = pool.makeClass(PKG + ".CollCmp")
cmd   = pool.makeClass(PKG + ".CollCmd", pool.get(APC))
pl    = pool.makeClass(PKG + ".SkyyCollectionsPlugin", pool.get(JP))

# ================= CollStore =================
store.addField(CtField.make("public static java.nio.file.Path DIR;", store))
store.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DATA = new java.util.concurrent.ConcurrentHashMap();", store))
store.addField(CtField.make("public static final long[] TIERS = new long[] { 50L, 250L, 1000L, 5000L, 20000L };", store))
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
      p.load(in); in.close();
      java.util.Enumeration en = p.propertyNames();
      while (en.hasMoreElements()) {
        String k = (String) en.nextElement();
        try { m.put(k, Long.valueOf(Long.parseLong(p.getProperty(k)))); } catch (Throwable t) { }
      }
    }
  } catch (Throwable t) { }
  DATA.put(u, m);
  return m;
}""", store))
store.addMethod(CtNewMethod.make("""
public static void save(java.util.UUID u) {
  try {
    java.util.Map m = counts(u);
    java.util.Properties p = new java.util.Properties();
    java.util.Iterator it = m.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      p.setProperty((String) e.getKey(), String.valueOf(((Long) e.getValue()).longValue()));
    }
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(DIR.resolve(u.toString() + ".properties"), new java.nio.file.OpenOption[0]);
    p.store(out, "SkyyCollections");
    out.close();
  } catch (Throwable t) { }
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
# returns new tier if a milestone was crossed, else 0
store.addMethod(CtNewMethod.make("""
public static int bump(java.util.UUID u, String id, long n) {
  java.util.Map m = counts(u);
  Long v = (Long) m.get(id);
  long oldv = v == null ? 0L : v.longValue();
  long newv = oldv + n;
  m.put(id, Long.valueOf(newv));
  int ot = tierOf(oldv); int nt = tierOf(newv);
  return nt > ot ? nt : 0;
}""", store))

# ================= CollSystem (BreakBlockEvent listener) =================
sysc.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();", sysc))
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
    com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType bt = e.getBlockType();
    if (bt == null) return;
    String id = bt.getId();
    if (id == null) return;
    java.util.UUID u = pr.getUuid();
    int newTier = {PKG}.CollStore.bump(u, id, 1L);
    DIRTY.put(u, Boolean.TRUE);
    if (newTier > 0) {{
      pr.sendMessage({MSG}.raw("Collection milestone! " + id + " " + {PKG}.CollStore.roman(newTier) + " (recipe unlocks land in a later update)"));
    }}
  }} catch (Throwable t) {{ }}
}}""", sysc))

# ================= saver tick =================
sav = pool.makeClass(PKG + ".CollSaver")
sav.addInterface(pool.get("java.lang.Runnable"))
sav.addConstructor(CtNewConstructor.make("public CollSaver() { }", sav))
sav.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    java.util.Iterator it = {PKG}.CollSystem.DIRTY.keySet().iterator();
    while (it.hasNext()) {{
      java.util.UUID u = (java.util.UUID) it.next();
      it.remove();
      {PKG}.CollStore.save(u);
    }}
  }} catch (Throwable t) {{ }}
}}""", sav))

# ================= comparator =================
ccmp.addInterface(pool.get("java.util.Comparator"))
ccmp.addConstructor(CtNewConstructor.make("public CollCmp() { }", ccmp))
ccmp.addMethod(CtNewMethod.make("""
public int compare(Object a, Object b) {
  long x = ((Long) ((java.util.Map.Entry) a).getValue()).longValue();
  long y = ((Long) ((java.util.Map.Entry) b).getValue()).longValue();
  return x == y ? 0 : (x > y ? -1 : 1);
}""", ccmp))

# ================= CollPage (static file + sets only) =================
page.addConstructor(CtNewConstructor.make(f"public CollPage({PR} pr) {{ super(pr, {LIFE}.CanDismiss); }}", page))
page.addMethod(CtNewMethod.make(f"""
protected void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  b.append("Pages/SkyyCollections.ui");
  java.util.UUID u = this.playerRef.getUuid();
  java.util.ArrayList entries = new java.util.ArrayList({PKG}.CollStore.counts(u).entrySet());
  java.util.Collections.sort(entries, new {PKG}.CollCmp());
  int n = entries.size() < 14 ? entries.size() : 14;
  b.set("#c_summary.Text", entries.size() == 0 ? "Nothing collected yet - go break some blocks!" : (entries.size() + " collections tracked"));
  for (int i = 0; i < 14; i++) {{
    if (i < n) {{
      java.util.Map.Entry e = (java.util.Map.Entry) entries.get(i);
      String id = (String) e.getKey();
      long cnt = ((Long) e.getValue()).longValue();
      int tier = {PKG}.CollStore.tierOf(cnt);
      long next = tier < 5 ? {PKG}.CollStore.TIERS[tier] : 0L;
      String prog = tier >= 5 ? "MAX" : (cnt + " / " + next);
      b.set("#c_row_" + i + ".Visible", true);
      b.set("#c_name_" + i + ".Text", id + "  " + {PKG}.CollStore.roman(tier));
      b.set("#c_prog_" + i + ".Text", prog);
    }} else {{
      b.set("#c_row_" + i + ".Visible", false);
    }}
  }}
}}""", page))

# ================= command =================
cmd.addConstructor(CtNewConstructor.make("""
public CollCmd() {
  super("collections", "View your collections");
  addAliases(new String[] { "coll" });
}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new {PKG}.CollPage(pr));
  }} catch (Throwable t) {{
    pr.sendMessage({MSG}.raw("Collections error: " + t));
  }}
}}""", cmd))

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture saver;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyyCollectionsPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.CollStore.DIR = getDataDirectory().resolve("counts");
  getEntityStoreRegistry().registerSystem(new {PKG}.CollSystem());
  getCommandRegistry().registerCommand(new {PKG}.CollCmd());
  this.saver = com.hypixel.hytale.server.core.HytaleServer.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.CollSaver(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.WARNING).log("[SkyyCollections] 0.1 ready - break blocks, /collections to view");
}}""", pl))

for c in (store, sysc, sav, ccmp, page, cmd, pl): c.writeFile(OUT)
print("classes written")

rows = []
for i in range(14):
    rows.append(f"""    Group #c_row_{i} {{
      Anchor: (Height: 24);
      LayoutMode: Left;
      Visible: false;
      Label #c_name_{i} {{ Anchor: (Width: 330, Height: 20); Style: (FontSize: 11, RenderBold: true, TextColor: #ffffff); Text: ""; }}
      Label #c_prog_{i} {{ Anchor: (Width: 170, Height: 20); Style: (FontSize: 11, TextColor: #9fd8a2); Text: ""; }}
    }}""")
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
""" + "\n".join(rows) + """
  }
}
"""
manifest = {
  "Group": "Skyy", "Name": "0.1 SkyyCollections", "Version": "0.1.0",
  "Description": "SkyWynn collections: every block you break counts toward per-item milestones (I-V). /collections to view. Recipe unlocks come later.",
  "Authors": [{"Name": "Skyy"}], "ServerVersion": "*", "DisabledByDefault": False,
  "IncludesAssetPack": True, "Main": "com.skyy.collections.SkyyCollectionsPlugin"
}
with zipfile.ZipFile("/tmp/SkyyCollections.jar", "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("manifest.json", json.dumps(manifest, indent=2))
    z.writestr("Common/UI/Custom/Pages/SkyyCollections.ui", COLL_UI)
    for root, _, files in os.walk(OUT):
        for f in files:
            if f.endswith(".class"):
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, OUT).replace(os.sep, "/"))
print("assembled", os.path.getsize("/tmp/SkyyCollections.jar"))
