import jpype, sys, os, zipfile, json
from jdk4py import JAVA_HOME
jpype.startJVM(str(JAVA_HOME/"lib"/"server"/"libjvm.so"), "--add-opens=java.base/java.lang=ALL-UNNAMED", classpath=["/tmp/javassist/javassist.jar"])
J = jpype.JClass
ClassPool, CtField, CtNewMethod, CtNewConstructor = J("javassist.ClassPool"), J("javassist.CtField"), J("javassist.CtNewMethod"), J("javassist.CtNewConstructor")
REL = sys.argv[1]
pool = ClassPool(False); pool.appendSystemPath(); pool.appendClassPath(REL)
OUT = "/tmp/skyyhud2_classes"; os.system(f"rm -rf {OUT}"); os.makedirs(OUT)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
HUD = "com.hypixel.hytale.server.core.entity.entities.player.hud.CustomUIHud"
PAGE= "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
LIFE= "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime"
UCB = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
UEB = "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"
BT  = "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType"
PRE = "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
WTR = "com.hypixel.hytale.server.core.modules.time.WorldTimeResource"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
MSG = "com.hypixel.hytale.server.core.Message"
HSV = "com.hypixel.hytale.server.core.HytaleServer"

# --- probe PageManager open method + Player componentType + HytaleServer executor field ---
pm = pool.get("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager")
open_m = None
for m in pm.getDeclaredMethods():
    sig = str(m.getSignature())
    if "CustomUIPage" in sig and sig.endswith(")V") or "Page;)" in sig:
        print("PM method:", m.getName(), sig[:100])
        if open_m is None and "open" in str(m.getName()).lower(): open_m = str(m.getName())
assert open_m, "no page-open method found"
print("USING PageManager." + open_m)
pla = pool.get(PLA)
assert any(str(m.getName()) == "getComponentType" for m in pla.getMethods()), "Player.getComponentType missing"
hs = pool.get(HSV)
assert any(str(f.getName()) == "SCHEDULED_EXECUTOR" for f in hs.getFields()), "SCHEDULED_EXECUTOR missing"

PKG = "com.skyy.hud"
# pre-declare
wl   = pool.makeClass(PKG + ".WLayout")
lst  = pool.makeClass(PKG + ".LayoutStore")
wid  = pool.makeClass(PKG + ".Widgets")
hudc = pool.makeClass(PKG + ".HudMain", pool.get(HUD))
page = pool.makeClass(PKG + ".EditorPage", pool.get(PAGE))
cmd  = pool.makeClass(PKG + ".HudCmd", pool.get(APC))
tick = pool.makeClass(PKG + ".TickTask")
rdy  = pool.makeClass(PKG + ".SkyyHudReady")
pl   = pool.makeClass(PKG + ".SkyyHudPlugin", pool.get(JP))
eot  = pool.makeClass(PKG + ".EditorOpenTask")

# ================= WLayout =================
wl.addField(CtField.make("public boolean en;", wl))
wl.addField(CtField.make("public String anchor;", wl))
wl.addField(CtField.make("public int dx;", wl))
wl.addField(CtField.make("public int dy;", wl))
wl.addField(CtField.make("public int scale;", wl))
wl.addConstructor(CtNewConstructor.make("""
public WLayout(boolean en, String anchor, int dx, int dy, int scale) {
  this.en = en; this.anchor = anchor; this.dx = dx; this.dy = dy; this.scale = scale;
}""", wl))
wl.addMethod(CtNewMethod.make("""
public String ser() { return (en ? "1" : "0") + "," + anchor + "," + dx + "," + dy + "," + scale; }""", wl))
wl.addMethod(CtNewMethod.make(f"""
public static {PKG}.WLayout parse(String s, {PKG}.WLayout def) {{
  try {{
    String[] p = s.split(",");
    return new {PKG}.WLayout("1".equals(p[0]), p[1], Integer.parseInt(p[2]), Integer.parseInt(p[3]), Integer.parseInt(p[4]));
  }} catch (Throwable t) {{ return def; }}
}}""", wl))

# ================= Widgets (registry + text providers) =================
wid.addField(CtField.make('public static final String[] IDS = new String[] { "coords", "dir", "zone", "gclock", "rclock", "day", "session", "online" };', wid))
wid.addMethod(CtNewMethod.make(f"""
public static {PKG}.WLayout def(String id) {{
  if (id.equals("coords"))  return new {PKG}.WLayout(true,  "tl", 8,  8,  100);
  if (id.equals("dir"))     return new {PKG}.WLayout(true,  "t",  0,  8,  100);
  if (id.equals("zone"))    return new {PKG}.WLayout(true,  "tr", 8,  8,  100);
  if (id.equals("gclock"))  return new {PKG}.WLayout(true,  "bl", 8,  40, 100);
  if (id.equals("rclock"))  return new {PKG}.WLayout(false, "bl", 8,  70, 100);
  if (id.equals("day"))     return new {PKG}.WLayout(false, "br", 8,  40, 100);
  if (id.equals("session")) return new {PKG}.WLayout(false, "br", 8,  70, 100);
  if (id.equals("online"))  return new {PKG}.WLayout(false, "tr", 8,  40, 100);
  return new {PKG}.WLayout(false, "tl", 8, 8, 100);
}}""", wid))
wid.addMethod(CtNewMethod.make("""
public static String label(String id) {
  if (id.equals("coords"))  return "Coordinates";
  if (id.equals("dir"))     return "Compass";
  if (id.equals("zone"))    return "Zone";
  if (id.equals("gclock"))  return "Game Clock";
  if (id.equals("rclock"))  return "Real Clock";
  if (id.equals("day"))     return "Day Counter";
  if (id.equals("session")) return "Session Time";
  if (id.equals("online"))  return "Players Online";
  return id;
}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static String text(String id, {PR} pr, long joinMs) {{
  try {{
    if (id.equals("coords")) {{
      com.hypixel.hytale.math.vector.Transform t = pr.getTransform();
      if (t == null) return "X ? Y ? Z ?";
      org.joml.Vector3d p = t.getPosition();
      return "X " + (int) Math.floor(p.x) + "  Y " + (int) Math.floor(p.y) + "  Z " + (int) Math.floor(p.z);
    }}
    if (id.equals("dir")) {{
      com.hypixel.hytale.math.vector.Rotation3f r = pr.getHeadRotation();
      if (r == null) return "?";
      float yaw = r.yaw();
      yaw = yaw % 360.0f; if (yaw < 0.0f) yaw += 360.0f;
      String[] dirs = new String[] {{ "S", "SW", "W", "NW", "N", "NE", "E", "SE" }};
      int idx = ((int) Math.floor((double) ((yaw + 22.5f) / 45.0f))) % 8;
      return dirs[idx];
    }}
    if (id.equals("zone")) {{
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) return "?";
      {WLD} w = {UNI}.get().getWorld(wu);
      return w == null ? "?" : w.getName();
    }}
    if (id.equals("gclock") || id.equals("day")) {{
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) return "--:--";
      {WLD} w = {UNI}.get().getWorld(wu);
      if (w == null) return "--:--";
      {ST} st = w.getEntityStore().getStore();
      {WTR} tr = ({WTR}) st.getResource({WTR}.getResourceType());
      if (tr == null) return "--:--";
      java.time.Instant gi = tr.getGameTime();
      long ms = gi.toEpochMilli();
      long dayMs = 86400000L;
      if (id.equals("day")) return "Day " + (ms / dayMs);
      long inDay = ms % dayMs;
      long hh = inDay / 3600000L; long mm = (inDay % 3600000L) / 60000L;
      return (hh < 10 ? "0" : "") + hh + ":" + (mm < 10 ? "0" : "") + mm;
    }}
    if (id.equals("rclock")) {{
      java.time.LocalTime n = java.time.LocalTime.now();
      int h = n.getHour(); int m = n.getMinute();
      return (h < 10 ? "0" : "") + h + ":" + (m < 10 ? "0" : "") + m;
    }}
    if (id.equals("session")) {{
      long s = (System.currentTimeMillis() - joinMs) / 1000L;
      long h = s / 3600L; long m = (s % 3600L) / 60L;
      return h > 0 ? (h + "h " + m + "m") : (m + "m " + (s % 60L) + "s");
    }}
    if (id.equals("online")) return {UNI}.get().getPlayers().size() + " online";
  }} catch (Throwable t) {{ return "?"; }}
  return "?";
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static String anchorSrc(String a, int dx, int dy, int w, int h) {{
  if (a.equals("tl")) return "(Top: " + dy + ", Left: " + dx + ", Width: " + w + ", Height: " + h + ")";
  if (a.equals("t"))  return "(Top: " + dy + ", Horizontal: " + dx + ", Width: " + w + ", Height: " + h + ")";
  if (a.equals("tr")) return "(Top: " + dy + ", Right: " + dx + ", Width: " + w + ", Height: " + h + ")";
  if (a.equals("l"))  return "(Vertical: " + dy + ", Left: " + dx + ", Width: " + w + ", Height: " + h + ")";
  if (a.equals("c"))  return "(Vertical: " + dy + ", Horizontal: " + dx + ", Width: " + w + ", Height: " + h + ")";
  if (a.equals("r"))  return "(Vertical: " + dy + ", Right: " + dx + ", Width: " + w + ", Height: " + h + ")";
  if (a.equals("bl")) return "(Bottom: " + dy + ", Left: " + dx + ", Width: " + w + ", Height: " + h + ")";
  if (a.equals("b"))  return "(Bottom: " + dy + ", Horizontal: " + dx + ", Width: " + w + ", Height: " + h + ")";
  return "(Bottom: " + dy + ", Right: " + dx + ", Width: " + w + ", Height: " + h + ")";
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static String widgetSrc(String id, {PKG}.WLayout l) {{
  int fs = 12 * l.scale / 100; if (fs < 6) fs = 6;
  int w = 180 * l.scale / 100; int h = 26 * l.scale / 100;
  StringBuilder sb = new StringBuilder();
  sb.append("Group #w_").append(id).append(" {{ ");
  sb.append("Anchor: ").append(anchorSrc(l.anchor, l.dx, l.dy, w, h)).append("; ");
  sb.append("Background: #0b1524(0.72); ");
  sb.append("Label #w_").append(id).append("_t {{ Anchor: (Full: 0); Style: (FontSize: ").append(fs);
  sb.append(", RenderBold: true, TextColor: #eaf6ff, HorizontalAlignment: Center, VerticalAlignment: Center); Text: \\"?\\"; }} ");
  sb.append("}}");
  return sb.toString();
}}""", wid))

wid.addMethod(CtNewMethod.make(f"""
public static com.hypixel.hytale.server.core.ui.Anchor buildAnchor({PKG}.WLayout l) {{
  com.hypixel.hytale.server.core.ui.Anchor a = new com.hypixel.hytale.server.core.ui.Anchor();
  Integer dx = Integer.valueOf(l.dx); Integer dy = Integer.valueOf(l.dy);
  int w = 180 * l.scale / 100; int h = 26 * l.scale / 100;
  a.setWidth(com.hypixel.hytale.server.core.ui.Value.of(Integer.valueOf(w)));
  a.setHeight(com.hypixel.hytale.server.core.ui.Value.of(Integer.valueOf(h)));
  String an = l.anchor;
  if (an.equals("tl")) {{ a.setTop(com.hypixel.hytale.server.core.ui.Value.of(dy)); a.setLeft(com.hypixel.hytale.server.core.ui.Value.of(dx)); }}
  else if (an.equals("t")) {{ a.setTop(com.hypixel.hytale.server.core.ui.Value.of(dy)); a.setHorizontal(com.hypixel.hytale.server.core.ui.Value.of(dx)); }}
  else if (an.equals("tr")) {{ a.setTop(com.hypixel.hytale.server.core.ui.Value.of(dy)); a.setRight(com.hypixel.hytale.server.core.ui.Value.of(dx)); }}
  else if (an.equals("l")) {{ a.setVertical(com.hypixel.hytale.server.core.ui.Value.of(dy)); a.setLeft(com.hypixel.hytale.server.core.ui.Value.of(dx)); }}
  else if (an.equals("c")) {{ a.setVertical(com.hypixel.hytale.server.core.ui.Value.of(dy)); a.setHorizontal(com.hypixel.hytale.server.core.ui.Value.of(dx)); }}
  else if (an.equals("r")) {{ a.setVertical(com.hypixel.hytale.server.core.ui.Value.of(dy)); a.setRight(com.hypixel.hytale.server.core.ui.Value.of(dx)); }}
  else if (an.equals("bl")) {{ a.setBottom(com.hypixel.hytale.server.core.ui.Value.of(dy)); a.setLeft(com.hypixel.hytale.server.core.ui.Value.of(dx)); }}
  else if (an.equals("b")) {{ a.setBottom(com.hypixel.hytale.server.core.ui.Value.of(dy)); a.setHorizontal(com.hypixel.hytale.server.core.ui.Value.of(dx)); }}
  else {{ a.setBottom(com.hypixel.hytale.server.core.ui.Value.of(dy)); a.setRight(com.hypixel.hytale.server.core.ui.Value.of(dx)); }}
  return a;
}}""", wid))

# ================= LayoutStore =================
lst.addField(CtField.make("public static java.nio.file.Path DIR;", lst))
lst.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();", lst))
lst.addMethod(CtNewMethod.make(f"""
public static java.util.Map get(java.util.UUID u) {{
  java.util.Map m = (java.util.Map) CACHE.get(u);
  if (m != null) return m;
  m = new java.util.concurrent.ConcurrentHashMap();
  try {{
    java.nio.file.Path f = DIR.resolve(u.toString() + ".properties");
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {{
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      p.load(in); in.close();
      String[] ids = {PKG}.Widgets.IDS;
      for (int i = 0; i < ids.length; i++) {{
        String v = p.getProperty(ids[i]);
        {PKG}.WLayout d = {PKG}.Widgets.def(ids[i]);
        m.put(ids[i], v == null ? d : {PKG}.WLayout.parse(v, d));
      }}
    }} else {{
      String[] ids = {PKG}.Widgets.IDS;
      for (int i = 0; i < ids.length; i++) m.put(ids[i], {PKG}.Widgets.def(ids[i]));
    }}
  }} catch (Throwable t) {{
    String[] ids = {PKG}.Widgets.IDS;
    for (int i = 0; i < ids.length; i++) if (!m.containsKey(ids[i])) m.put(ids[i], {PKG}.Widgets.def(ids[i]));
  }}
  CACHE.put(u, m);
  return m;
}}""", lst))
lst.addMethod(CtNewMethod.make(f"""
public static void save(java.util.UUID u) {{
  try {{
    java.util.Map m = get(u);
    java.util.Properties p = new java.util.Properties();
    String[] ids = {PKG}.Widgets.IDS;
    for (int i = 0; i < ids.length; i++) {{
      {PKG}.WLayout l = ({PKG}.WLayout) m.get(ids[i]);
      if (l != null) p.setProperty(ids[i], l.ser());
    }}
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(DIR.resolve(u.toString() + ".properties"), new java.nio.file.OpenOption[0]);
    p.store(out, "SkyyHud layout");
    out.close();
  }} catch (Throwable t) {{ }}
}}""", lst))

# ================= HudMain =================
hudc.addField(CtField.make("public java.util.UUID uuid;", hudc))
hudc.addField(CtField.make("public long joinMs;", hudc))
hudc.addField(CtField.make("public final java.util.HashMap last = new java.util.HashMap();", hudc))
hudc.addConstructor(CtNewConstructor.make(f"""
public HudMain({PR} pr) {{
  super(pr, "skyyhud_main");
  this.uuid = pr.getUuid();
  this.joinMs = System.currentTimeMillis();
}}""", hudc))
hudc.addMethod(CtNewMethod.make(f"""
public void fill({UCB} b, boolean full) {{
  java.util.Map m = {PKG}.LayoutStore.get(this.uuid);
  {PR} pr = getPlayerRef();
  String[] ids = {PKG}.Widgets.IDS;
  for (int i = 0; i < ids.length; i++) {{
    {PKG}.WLayout l = ({PKG}.WLayout) m.get(ids[i]);
    if (l == null) continue;
    if (full) {{
      b.set("#w_" + ids[i] + ".Visible", l.en);
      if (l.en) b.setObject("#w_" + ids[i] + ".Anchor", {PKG}.Widgets.buildAnchor(l));
    }}
    if (!l.en) continue;
    String t = {PKG}.Widgets.text(ids[i], pr, this.joinMs);
    String prev = (String) this.last.get(ids[i]);
    if (full || prev == null || !prev.equals(t)) {{
      this.last.put(ids[i], t);
      b.set("#w_" + ids[i] + "_t.Text", t);
    }}
  }}
}}""", hudc))
hudc.addMethod(CtNewMethod.make(f"""
protected void build({UCB} b) {{
  b.append("Hud/SkyyHud.ui");
  this.last.clear();
  fill(b, true);
}}""", hudc))
hudc.addMethod(CtNewMethod.make(f"""
public void tick() {{
  try {{
    {UCB} b = new {UCB}();
    int before = b.getCommands().length;
    fill(b, false);
    if (b.getCommands().length > before) update(false, b);
  }} catch (Throwable t) {{ }}
}}""", hudc))
hudc.addMethod(CtNewMethod.make(f"""
public void rebuild() {{
  try {{ show(); }} catch (Throwable t) {{ }}
}}""", hudc))

# ==== Plugin part A (fields/ctor/attach/rebuildFor/tickAll) ====
pl.addField(CtField.make("public final java.util.concurrent.ConcurrentHashMap huds = new java.util.concurrent.ConcurrentHashMap();", pl))
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyyHudPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void attach({PR} pr) {{
  try {{
    {PKG}.HudMain h = new {PKG}.HudMain(pr);
    this.huds.put(pr.getUuid(), h);
    h.show();
  }} catch (Throwable t) {{
    getLogger().at(java.util.logging.Level.WARNING).log("[SkyyHud] attach failed: " + t);
  }}
}}""", pl))
pl.addMethod(CtNewMethod.make(f"""
public void rebuildFor(java.util.UUID u) {{
  {PKG}.HudMain h = ({PKG}.HudMain) this.huds.get(u);
  if (h != null) h.rebuild();
}}""", pl))
pl.addMethod(CtNewMethod.make(f"""
public void tickAll() {{
  java.util.Iterator it = this.huds.entrySet().iterator();
  while (it.hasNext()) {{
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    {PKG}.HudMain h = ({PKG}.HudMain) e.getValue();
    {PR} pr = h.getPlayerRef();
    if (pr == null || !pr.isValid()) {{ it.remove(); continue; }}
    h.tick();
  }}
}}""", pl))
# ================= EditorPage =================
page.addField(CtField.make(f"public {PKG}.SkyyHudPlugin plugin;", page))
page.addConstructor(CtNewConstructor.make(f"""
public EditorPage({PR} pr, {PKG}.SkyyHudPlugin plugin) {{
  super(pr, {LIFE}.CanDismiss);
  this.plugin = plugin;
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public String rowInfo(String id) {{
  java.util.Map m = {PKG}.LayoutStore.get(this.playerRef.getUuid());
  {PKG}.WLayout l = ({PKG}.WLayout) m.get(id);
  if (l == null) return "?";
  return (l.en ? "ON " : "off ") + l.anchor.toUpperCase() + "  x" + l.dx + " y" + l.dy + "  " + l.scale + "%";
}}""", page))

page.addMethod(CtNewMethod.make(f"""
protected void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  b.append("Pages/SkyyHudEditor.ui");
  String[] ids = {PKG}.Widgets.IDS;
  String[] acts = new String[] {{ "tog", "tl", "t", "tr", "l", "c", "r", "bl", "b2", "br", "xm", "xp", "ym", "yp", "sm", "sp" }};
  for (int i = 0; i < ids.length; i++) {{
    b.set("#e_info_" + ids[i] + ".Text", rowInfo(ids[i]));
    for (int a = 0; a < acts.length; a++) {{
      ev.addEventBinding({BT}.Activating, "#e_" + ids[i] + "_" + acts[a]);
    }}
  }}
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    int p = data.indexOf("#e_");
    if (p < 0) return;
    String s = data.substring(p + 3);
    int q = s.indexOf('_');
    if (q < 0) return;
    String wid2 = s.substring(0, q);
    String act = s.substring(q + 1);
    int e = 0;
    while (e < act.length() && (Character.isLetterOrDigit(act.charAt(e)) || act.charAt(e) == '+' || act.charAt(e) == '-')) e++;
    act = act.substring(0, e);
    java.util.UUID u = this.playerRef.getUuid();
    java.util.Map m = {PKG}.LayoutStore.get(u);
    {PKG}.WLayout l = ({PKG}.WLayout) m.get(wid2);
    if (l == null) return;
    if (act.equals("tog")) l.en = !l.en;
    else if (act.equals("xm")) l.dx -= 10;
    else if (act.equals("xp")) l.dx += 10;
    else if (act.equals("ym")) l.dy -= 10;
    else if (act.equals("yp")) l.dy += 10;
    else if (act.equals("sm")) {{ l.scale -= 10; if (l.scale < 50) l.scale = 50; }}
    else if (act.equals("sp")) {{ l.scale += 10; if (l.scale > 200) l.scale = 200; }}
    else if (act.equals("b2")) l.anchor = "b";
    else l.anchor = act;
    if (l.dx < 0) l.dx = 0;
    if (l.dy < 0) l.dy = 0;
    {PKG}.LayoutStore.save(u);
    plugin.rebuildFor(u);
    {UCB} b = new {UCB}();
    b.set("#e_info_" + wid2 + ".Text", rowInfo(wid2));
    sendUpdate(b);
  }} catch (Throwable t) {{ }}
}}""", page))

# ================= HudCmd =================
cmd.addField(CtField.make(f"public {PKG}.SkyyHudPlugin plugin;", cmd))
cmd.addConstructor(CtNewConstructor.make(f"""
public HudCmd({PKG}.SkyyHudPlugin p) {{
  super("hud", "Open the SkyyHud editor");
  addAliases(new String[] {{ "skyyhud" }});
  this.plugin = p;
}}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) {{ pr.sendMessage({MSG}.raw("SkyyHud: player entity not found")); return; }}
    if (!this.plugin.huds.containsKey(pr.getUuid())) this.plugin.attach(pr);
    player.getPageManager().openCustomPage(ref, store, new {PKG}.EditorPage(pr, this.plugin));
  }} catch (Throwable t) {{
    pr.sendMessage({MSG}.raw("SkyyHud editor error: " + t));
  }}
}}""", cmd))

# ================= TickTask =================
tick.addInterface(pool.get("java.lang.Runnable"))
tick.addField(CtField.make(f"public {PKG}.SkyyHudPlugin plugin;", tick))
tick.addConstructor(CtNewConstructor.make(f"public TickTask({PKG}.SkyyHudPlugin p) {{ this.plugin = p; }}", tick))
tick.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{ plugin.tickAll(); }} catch (Throwable t) {{ }}
}}""", tick))

# ==== EditorOpenTask (TEST: auto-opens editor after join) ====
eot.addInterface(pool.get("java.lang.Runnable"))
eot.addField(CtField.make(f"public {PKG}.SkyyHudPlugin plugin;", eot))
eot.addField(CtField.make(f"public {PR} pr;", eot))
eot.addField(CtField.make("public boolean onWorld;", eot))
eot.addConstructor(CtNewConstructor.make(f"public EditorOpenTask({PKG}.SkyyHudPlugin p, {PR} pr) {{ this.plugin = p; this.pr = pr; this.onWorld = false; }}", eot))
eot.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (!this.onWorld) {{
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) return;
      {WLD} w = com.hypixel.hytale.server.core.universe.Universe.get().getWorld(wu);
      if (w == null) return;
      this.onWorld = true;
      w.execute(this);
      return;
    }}
    {REF} r = pr.getReference();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    {PLA} player = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(r, st, new {PKG}.EditorPage(pr, this.plugin));
  }} catch (Throwable t) {{ }}
}}""", eot))


# ================= Ready consumer =================
rdy.addInterface(pool.get("java.util.function.Consumer"))
rdy.addField(CtField.make(f"public {PKG}.SkyyHudPlugin plugin;", rdy))
rdy.addConstructor(CtNewConstructor.make(f"public SkyyHudReady({PKG}.SkyyHudPlugin p) {{ this.plugin = p; }}", rdy))
rdy.addMethod(CtNewMethod.make(f"""
public void accept(Object ev) {{
  try {{
    {PRE} e = ({PRE}) ev;
    {REF} r = e.getPlayerRef();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    plugin.attach(pr);
    {HSV}.SCHEDULED_EXECUTOR.schedule(new {PKG}.EditorOpenTask(plugin, pr), 5L, java.util.concurrent.TimeUnit.SECONDS);
  }} catch (Throwable t) {{ }}
}}""", rdy))


# ==== Plugin part B (setup) ====
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.LayoutStore.DIR = getDataDirectory().resolve("layouts");
  getEventRegistry().registerGlobal({PRE}.class, new {PKG}.SkyyHudReady(this));
  getCommandRegistry().registerCommand(new {PKG}.HudCmd(this));
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.TickTask(this), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.WARNING).log("[SkyyHud] 0.1.3-selftest - HUD+editor auto-attach on join");
}}""", pl))

for c in (wl, lst, wid, hudc, page, cmd, tick, rdy, eot, pl): c.writeFile(OUT)
print("classes written")

HUD_UI = """Group #SkyyHudRoot {
  Anchor: (Full: 0);

  Group #w_coords {
    Anchor: (Top: 8, Left: 8, Width: 180, Height: 26);
    Visible: true;
    Background: #0b1524(0.72);
    Label #w_coords_t {
      Anchor: (Full: 0);
      Style: (FontSize: 12, RenderBold: true, TextColor: #eaf6ff, Alignment: Center);
      Text: "";
    }
  }

  Group #w_dir {
    Anchor: (Top: 8, Horizontal: 0, Width: 180, Height: 26);
    Visible: true;
    Background: #0b1524(0.72);
    Label #w_dir_t {
      Anchor: (Full: 0);
      Style: (FontSize: 12, RenderBold: true, TextColor: #eaf6ff, Alignment: Center);
      Text: "";
    }
  }

  Group #w_zone {
    Anchor: (Top: 8, Right: 8, Width: 180, Height: 26);
    Visible: true;
    Background: #0b1524(0.72);
    Label #w_zone_t {
      Anchor: (Full: 0);
      Style: (FontSize: 12, RenderBold: true, TextColor: #eaf6ff, Alignment: Center);
      Text: "";
    }
  }

  Group #w_gclock {
    Anchor: (Bottom: 40, Left: 8, Width: 180, Height: 26);
    Visible: true;
    Background: #0b1524(0.72);
    Label #w_gclock_t {
      Anchor: (Full: 0);
      Style: (FontSize: 12, RenderBold: true, TextColor: #eaf6ff, Alignment: Center);
      Text: "";
    }
  }

  Group #w_rclock {
    Anchor: (Bottom: 70, Left: 8, Width: 180, Height: 26);
    Visible: false;
    Background: #0b1524(0.72);
    Label #w_rclock_t {
      Anchor: (Full: 0);
      Style: (FontSize: 12, RenderBold: true, TextColor: #eaf6ff, Alignment: Center);
      Text: "";
    }
  }

  Group #w_day {
    Anchor: (Bottom: 40, Right: 8, Width: 180, Height: 26);
    Visible: false;
    Background: #0b1524(0.72);
    Label #w_day_t {
      Anchor: (Full: 0);
      Style: (FontSize: 12, RenderBold: true, TextColor: #eaf6ff, Alignment: Center);
      Text: "";
    }
  }

  Group #w_session {
    Anchor: (Bottom: 70, Right: 8, Width: 180, Height: 26);
    Visible: false;
    Background: #0b1524(0.72);
    Label #w_session_t {
      Anchor: (Full: 0);
      Style: (FontSize: 12, RenderBold: true, TextColor: #eaf6ff, Alignment: Center);
      Text: "";
    }
  }

  Group #w_online {
    Anchor: (Top: 40, Right: 8, Width: 180, Height: 26);
    Visible: false;
    Background: #0b1524(0.72);
    Label #w_online_t {
      Anchor: (Full: 0);
      Style: (FontSize: 12, RenderBold: true, TextColor: #eaf6ff, Alignment: Center);
      Text: "";
    }
  }

}
"""
EDITOR_UI = """Group {
  Anchor: (Full: 0);
  Group #SkyyHudEditor {
    Anchor: (Horizontal: 0, Vertical: 0, Width: 660, Height: 500);
    Background: #0b1524(0.94);
    Padding: (Horizontal: 14, Vertical: 10);
    LayoutMode: Top;
    Group { Anchor: (Height: 2); Background: #7fe07f; }
    Label { Anchor: (Height: 26); Style: (FontSize: 15, RenderBold: true, TextColor: #eaffea, Alignment: Center); Text: "SkyyHud Editor"; }
    Label { Anchor: (Height: 14); Style: (FontSize: 10, TextColor: #9fb8d0, Alignment: Center); Text: "On/Off - anchor - nudge - scale. Changes apply instantly."; }
    Group #e_row_coords {
      Anchor: (Height: 52);
      LayoutMode: Top;
      Padding: (Vertical: 2);
      Group {
        Anchor: (Height: 16);
        LayoutMode: Left;
        Label { Anchor: (Width: 150, Height: 16); Style: (FontSize: 11, RenderBold: true, TextColor: #ffffff); Text: "Coordinates"; }
        Label #e_info_coords { Anchor: (Width: 300, Height: 16); Style: (FontSize: 11, TextColor: #9fd8a2); Text: ""; }
      }
      Group {
        Anchor: (Height: 26);
        LayoutMode: Left;
        Group #e_coords_tog { Anchor: (Width: 54, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "On/Off"; } }
        Group #e_coords_tl { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "TL"; } }
        Group #e_coords_t { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "T"; } }
        Group #e_coords_tr { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "TR"; } }
        Group #e_coords_l { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "L"; } }
        Group #e_coords_c { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "C"; } }
        Group #e_coords_r { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "R"; } }
        Group #e_coords_bl { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "BL"; } }
        Group #e_coords_b2 { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "B"; } }
        Group #e_coords_br { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "BR"; } }
        Group #e_coords_xm { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "X-"; } }
        Group #e_coords_xp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "X+"; } }
        Group #e_coords_ym { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "Y-"; } }
        Group #e_coords_yp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "Y+"; } }
        Group #e_coords_sm { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "S-"; } }
        Group #e_coords_sp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "S+"; } }
      }
    }
    Group #e_row_dir {
      Anchor: (Height: 52);
      LayoutMode: Top;
      Padding: (Vertical: 2);
      Group {
        Anchor: (Height: 16);
        LayoutMode: Left;
        Label { Anchor: (Width: 150, Height: 16); Style: (FontSize: 11, RenderBold: true, TextColor: #ffffff); Text: "Compass"; }
        Label #e_info_dir { Anchor: (Width: 300, Height: 16); Style: (FontSize: 11, TextColor: #9fd8a2); Text: ""; }
      }
      Group {
        Anchor: (Height: 26);
        LayoutMode: Left;
        Group #e_dir_tog { Anchor: (Width: 54, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "On/Off"; } }
        Group #e_dir_tl { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "TL"; } }
        Group #e_dir_t { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "T"; } }
        Group #e_dir_tr { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "TR"; } }
        Group #e_dir_l { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "L"; } }
        Group #e_dir_c { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "C"; } }
        Group #e_dir_r { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "R"; } }
        Group #e_dir_bl { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "BL"; } }
        Group #e_dir_b2 { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "B"; } }
        Group #e_dir_br { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "BR"; } }
        Group #e_dir_xm { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "X-"; } }
        Group #e_dir_xp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "X+"; } }
        Group #e_dir_ym { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "Y-"; } }
        Group #e_dir_yp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "Y+"; } }
        Group #e_dir_sm { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "S-"; } }
        Group #e_dir_sp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "S+"; } }
      }
    }
    Group #e_row_zone {
      Anchor: (Height: 52);
      LayoutMode: Top;
      Padding: (Vertical: 2);
      Group {
        Anchor: (Height: 16);
        LayoutMode: Left;
        Label { Anchor: (Width: 150, Height: 16); Style: (FontSize: 11, RenderBold: true, TextColor: #ffffff); Text: "Zone"; }
        Label #e_info_zone { Anchor: (Width: 300, Height: 16); Style: (FontSize: 11, TextColor: #9fd8a2); Text: ""; }
      }
      Group {
        Anchor: (Height: 26);
        LayoutMode: Left;
        Group #e_zone_tog { Anchor: (Width: 54, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "On/Off"; } }
        Group #e_zone_tl { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "TL"; } }
        Group #e_zone_t { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "T"; } }
        Group #e_zone_tr { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "TR"; } }
        Group #e_zone_l { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "L"; } }
        Group #e_zone_c { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "C"; } }
        Group #e_zone_r { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "R"; } }
        Group #e_zone_bl { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "BL"; } }
        Group #e_zone_b2 { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "B"; } }
        Group #e_zone_br { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "BR"; } }
        Group #e_zone_xm { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "X-"; } }
        Group #e_zone_xp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "X+"; } }
        Group #e_zone_ym { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "Y-"; } }
        Group #e_zone_yp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "Y+"; } }
        Group #e_zone_sm { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "S-"; } }
        Group #e_zone_sp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "S+"; } }
      }
    }
    Group #e_row_gclock {
      Anchor: (Height: 52);
      LayoutMode: Top;
      Padding: (Vertical: 2);
      Group {
        Anchor: (Height: 16);
        LayoutMode: Left;
        Label { Anchor: (Width: 150, Height: 16); Style: (FontSize: 11, RenderBold: true, TextColor: #ffffff); Text: "Game Clock"; }
        Label #e_info_gclock { Anchor: (Width: 300, Height: 16); Style: (FontSize: 11, TextColor: #9fd8a2); Text: ""; }
      }
      Group {
        Anchor: (Height: 26);
        LayoutMode: Left;
        Group #e_gclock_tog { Anchor: (Width: 54, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "On/Off"; } }
        Group #e_gclock_tl { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "TL"; } }
        Group #e_gclock_t { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "T"; } }
        Group #e_gclock_tr { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "TR"; } }
        Group #e_gclock_l { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "L"; } }
        Group #e_gclock_c { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "C"; } }
        Group #e_gclock_r { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "R"; } }
        Group #e_gclock_bl { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "BL"; } }
        Group #e_gclock_b2 { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "B"; } }
        Group #e_gclock_br { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "BR"; } }
        Group #e_gclock_xm { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "X-"; } }
        Group #e_gclock_xp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "X+"; } }
        Group #e_gclock_ym { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "Y-"; } }
        Group #e_gclock_yp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "Y+"; } }
        Group #e_gclock_sm { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "S-"; } }
        Group #e_gclock_sp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "S+"; } }
      }
    }
    Group #e_row_rclock {
      Anchor: (Height: 52);
      LayoutMode: Top;
      Padding: (Vertical: 2);
      Group {
        Anchor: (Height: 16);
        LayoutMode: Left;
        Label { Anchor: (Width: 150, Height: 16); Style: (FontSize: 11, RenderBold: true, TextColor: #ffffff); Text: "Real Clock"; }
        Label #e_info_rclock { Anchor: (Width: 300, Height: 16); Style: (FontSize: 11, TextColor: #9fd8a2); Text: ""; }
      }
      Group {
        Anchor: (Height: 26);
        LayoutMode: Left;
        Group #e_rclock_tog { Anchor: (Width: 54, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "On/Off"; } }
        Group #e_rclock_tl { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "TL"; } }
        Group #e_rclock_t { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "T"; } }
        Group #e_rclock_tr { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "TR"; } }
        Group #e_rclock_l { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "L"; } }
        Group #e_rclock_c { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "C"; } }
        Group #e_rclock_r { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "R"; } }
        Group #e_rclock_bl { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "BL"; } }
        Group #e_rclock_b2 { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "B"; } }
        Group #e_rclock_br { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "BR"; } }
        Group #e_rclock_xm { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "X-"; } }
        Group #e_rclock_xp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "X+"; } }
        Group #e_rclock_ym { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "Y-"; } }
        Group #e_rclock_yp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "Y+"; } }
        Group #e_rclock_sm { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "S-"; } }
        Group #e_rclock_sp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "S+"; } }
      }
    }
    Group #e_row_day {
      Anchor: (Height: 52);
      LayoutMode: Top;
      Padding: (Vertical: 2);
      Group {
        Anchor: (Height: 16);
        LayoutMode: Left;
        Label { Anchor: (Width: 150, Height: 16); Style: (FontSize: 11, RenderBold: true, TextColor: #ffffff); Text: "Day Counter"; }
        Label #e_info_day { Anchor: (Width: 300, Height: 16); Style: (FontSize: 11, TextColor: #9fd8a2); Text: ""; }
      }
      Group {
        Anchor: (Height: 26);
        LayoutMode: Left;
        Group #e_day_tog { Anchor: (Width: 54, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "On/Off"; } }
        Group #e_day_tl { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "TL"; } }
        Group #e_day_t { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "T"; } }
        Group #e_day_tr { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "TR"; } }
        Group #e_day_l { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "L"; } }
        Group #e_day_c { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "C"; } }
        Group #e_day_r { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "R"; } }
        Group #e_day_bl { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "BL"; } }
        Group #e_day_b2 { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "B"; } }
        Group #e_day_br { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "BR"; } }
        Group #e_day_xm { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "X-"; } }
        Group #e_day_xp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "X+"; } }
        Group #e_day_ym { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "Y-"; } }
        Group #e_day_yp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "Y+"; } }
        Group #e_day_sm { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "S-"; } }
        Group #e_day_sp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "S+"; } }
      }
    }
    Group #e_row_session {
      Anchor: (Height: 52);
      LayoutMode: Top;
      Padding: (Vertical: 2);
      Group {
        Anchor: (Height: 16);
        LayoutMode: Left;
        Label { Anchor: (Width: 150, Height: 16); Style: (FontSize: 11, RenderBold: true, TextColor: #ffffff); Text: "Session Time"; }
        Label #e_info_session { Anchor: (Width: 300, Height: 16); Style: (FontSize: 11, TextColor: #9fd8a2); Text: ""; }
      }
      Group {
        Anchor: (Height: 26);
        LayoutMode: Left;
        Group #e_session_tog { Anchor: (Width: 54, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "On/Off"; } }
        Group #e_session_tl { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "TL"; } }
        Group #e_session_t { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "T"; } }
        Group #e_session_tr { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "TR"; } }
        Group #e_session_l { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "L"; } }
        Group #e_session_c { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "C"; } }
        Group #e_session_r { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "R"; } }
        Group #e_session_bl { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "BL"; } }
        Group #e_session_b2 { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "B"; } }
        Group #e_session_br { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "BR"; } }
        Group #e_session_xm { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "X-"; } }
        Group #e_session_xp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "X+"; } }
        Group #e_session_ym { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "Y-"; } }
        Group #e_session_yp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "Y+"; } }
        Group #e_session_sm { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "S-"; } }
        Group #e_session_sp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "S+"; } }
      }
    }
    Group #e_row_online {
      Anchor: (Height: 52);
      LayoutMode: Top;
      Padding: (Vertical: 2);
      Group {
        Anchor: (Height: 16);
        LayoutMode: Left;
        Label { Anchor: (Width: 150, Height: 16); Style: (FontSize: 11, RenderBold: true, TextColor: #ffffff); Text: "Players Online"; }
        Label #e_info_online { Anchor: (Width: 300, Height: 16); Style: (FontSize: 11, TextColor: #9fd8a2); Text: ""; }
      }
      Group {
        Anchor: (Height: 26);
        LayoutMode: Left;
        Group #e_online_tog { Anchor: (Width: 54, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "On/Off"; } }
        Group #e_online_tl { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "TL"; } }
        Group #e_online_t { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "T"; } }
        Group #e_online_tr { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "TR"; } }
        Group #e_online_l { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "L"; } }
        Group #e_online_c { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "C"; } }
        Group #e_online_r { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "R"; } }
        Group #e_online_bl { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "BL"; } }
        Group #e_online_b2 { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "B"; } }
        Group #e_online_br { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "BR"; } }
        Group #e_online_xm { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "X-"; } }
        Group #e_online_xp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "X+"; } }
        Group #e_online_ym { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "Y-"; } }
        Group #e_online_yp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "Y+"; } }
        Group #e_online_sm { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "S-"; } }
        Group #e_online_sp { Anchor: (Width: 34, Height: 22); Background: #1d3a5f; Label { Anchor: (Full: 0); Style: (FontSize: 10, TextColor: #dceeff, Alignment: Center); Text: "S+"; } }
      }
    }
  }
}
"""
manifest = {
  "Group": "Skyy",
  "Name": "0.1.3 SkyyHud",
  "Version": "0.1.3",
  "Description": "SkyyHud: fully customizable server-side HUD. 8 widgets, per-player layouts, /skyyhud editor. Zero dependencies.",
  "Authors": [{"Name": "Skyy"}],
  "ServerVersion": "*",
  "DisabledByDefault": False,
  "IncludesAssetPack": True,
  "Main": "com.skyy.hud.SkyyHudPlugin"
}
jar = "/tmp/SkyyHud2.jar"
with zipfile.ZipFile(jar, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("manifest.json", json.dumps(manifest, indent=2))
    z.writestr("Common/UI/Custom/Hud/SkyyHud.ui", HUD_UI)
    z.writestr("Common/UI/Custom/Pages/SkyyHudEditor.ui", EDITOR_UI)
    for root, _, files in os.walk(OUT):
        for f in files:
            if f.endswith(".class"):
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, OUT).replace(os.sep, "/"))
print("assembled", jar, os.path.getsize(jar), "bytes")
