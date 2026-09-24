"""SkyyHud 0.2 - build script (javassist via jpype).
Run:   python build_skyyhud_0.2.py            -> SkyyHud/SkyyHud-0.2.jar
       python build_skyyhud_0.2.py --deploy   -> also copies to Mods/SkyyHud.jar and enables "Skyy:0.2 SkyyHud" in the HUD mod world
Changes vs 0.1.x: no bisect markers, no test auto-open, editor uses TextButton + EventData payloads,
/skyyhud (alias /shud) opens the editor; /skyyhud export | import <code> | reset for layout codes.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.2.4"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
HUD = "com.hypixel.hytale.server.core.entity.entities.player.hud.CustomUIHud"
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
WTR = "com.hypixel.hytale.server.core.modules.time.WorldTimeResource"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
ARG = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
OPT = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
MSG = "com.hypixel.hytale.server.core.Message"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
ANC = "com.hypixel.hytale.server.core.ui.Anchor"
VAL = "com.hypixel.hytale.server.core.ui.Value"

for c, m in ((PLA, "getComponentType"), (HSV, "SCHEDULED_EXECUTOR"), (UEB, "addEventBinding"), (EVD, "of"),
             (PR, "getHeadRotation"), (WTR, "getGameTime"), (ANC, "setHorizontal"), (CTX, "provided"),
             ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "openCustomPage")):
    B.probe(pool, c, m)
pool.get(OPT)  # class must exist

PKG = "com.skyy.hud"
wl   = pool.makeClass(PKG + ".WLayout")
lst  = pool.makeClass(PKG + ".LayoutStore")
wid  = pool.makeClass(PKG + ".Widgets")
hudc = pool.makeClass(PKG + ".HudMain", pool.get(HUD))
page = pool.makeClass(PKG + ".EditorPage", pool.get(PAGE))
cmd  = pool.makeClass(PKG + ".HudCmd", pool.get(APC))
tick = pool.makeClass(PKG + ".TickTask")
rdy  = pool.makeClass(PKG + ".SkyyHudReady")
pl   = pool.makeClass(PKG + ".SkyyHudPlugin", pool.get(JP))
att  = pool.makeClass(PKG + ".AttachTask")

IDS = ["Coords", "Dir", "Zone", "Gclock", "Rclock", "Day", "Session", "Online"]
ACTS = ["Tog", "Tl", "T", "Tr", "L", "C", "R", "Bl", "B2", "Br", "Xm", "Xp", "Ym", "Yp", "Sm", "Sp"]
ACT_LABEL = {"Tog": "On/Off", "Tl": "TL", "T": "T", "Tr": "TR", "L": "L", "C": "C", "R": "R", "Bl": "BL", "B2": "B", "Br": "BR",
             "Xm": "X-", "Xp": "X+", "Ym": "Y-", "Yp": "Y+", "Sm": "S-", "Sp": "S+"}
DEFAULTS = {"Coords": (True, "tl", 8, 8), "Dir": (True, "t", 0, 8), "Zone": (True, "tr", 8, 8), "Gclock": (True, "bl", 8, 40),
            "Rclock": (False, "bl", 8, 70), "Day": (False, "br", 8, 40), "Session": (False, "br", 8, 70), "Online": (False, "tr", 8, 40)}
LABELS = {"Coords": "Coordinates", "Dir": "Compass", "Zone": "Zone", "Gclock": "Game Clock", "Rclock": "Real Clock",
          "Day": "Day Counter", "Session": "Session Time", "Online": "Players Online"}
ACTS_JAVA = ", ".join('"%s"' % a for a in ACTS)
ACT_LABELS_JAVA = ", ".join('"%s"' % ACT_LABEL[a] for a in ACTS)

# ================= WLayout =================
for f in ("public boolean en;", "public String anchor;", "public int dx;", "public int dy;", "public int scale;"):
    wl.addField(CtField.make(f, wl))
wl.addConstructor(CtNewConstructor.make("""
public WLayout(boolean en, String anchor, int dx, int dy, int scale) {
  this.en = en; this.anchor = anchor; this.dx = dx; this.dy = dy; this.scale = scale;
}""", wl))
wl.addMethod(CtNewMethod.make("""
public String ser() { return (en ? "1" : "0") + "," + anchor + "," + dx + "," + dy + "," + scale; }""", wl))
wl.addMethod(CtNewMethod.make("""
public static boolean validAnchor(String a) {
  return a.equals("tl") || a.equals("t") || a.equals("tr") || a.equals("l") || a.equals("c") || a.equals("r") || a.equals("bl") || a.equals("b") || a.equals("br");
}""", wl))
wl.addMethod(CtNewMethod.make(f"""
public static {PKG}.WLayout parse(String s, {PKG}.WLayout def) {{
  try {{
    String[] p = s.trim().split(",");
    String a = p[1].trim();
    if (!validAnchor(a)) return def;
    int dx = Integer.parseInt(p[2].trim()); int dy = Integer.parseInt(p[3].trim()); int sc = Integer.parseInt(p[4].trim());
    if (dx < 0) dx = 0;
    if (dy < 0) dy = 0;
    if (sc < 50) sc = 50;
    if (sc > 200) sc = 200;
    return new {PKG}.WLayout("1".equals(p[0].trim()), a, dx, dy, sc);
  }} catch (Throwable t) {{ return def; }}
}}""", wl))

# ================= Widgets =================
wid.addField(CtField.make('public static final String[] IDS = new String[] { %s };' % ", ".join('"%s"' % i for i in IDS), wid))
def_lines = "\n".join('  if (id.equals("%s")) return new %s.WLayout(%s, "%s", %d, %d, 100);' % (i, PKG, str(d[0]).lower(), d[1], d[2], d[3]) for i, d in DEFAULTS.items())
wid.addMethod(CtNewMethod.make(f"""
public static {PKG}.WLayout def(String id) {{
{def_lines}
  return new {PKG}.WLayout(false, "tl", 8, 8, 100);
}}""", wid))
label_lines = "\n".join('  if (id.equals("%s")) return "%s";' % (i, l) for i, l in LABELS.items())
wid.addMethod(CtNewMethod.make(f"""
public static String label(String id) {{
{label_lines}
  return id;
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static String text(String id, {PR} pr, long joinMs) {{
  try {{
    if (id.equals("Coords")) {{
      com.hypixel.hytale.math.vector.Transform t = pr.getTransform();
      if (t == null) return "X ? Y ? Z ?";
      org.joml.Vector3d p = t.getPosition();
      return "X " + (int) Math.floor(p.x) + "  Y " + (int) Math.floor(p.y) + "  Z " + (int) Math.floor(p.z);
    }}
    if (id.equals("Dir")) {{
      com.hypixel.hytale.math.vector.Rotation3f r = pr.getHeadRotation();
      if (r == null) return "?";
      float yaw = r.yaw();
      yaw = yaw % 360.0f;
      if (yaw < 0.0f) yaw += 360.0f;
      String[] dirs = new String[] {{ "S", "SW", "W", "NW", "N", "NE", "E", "SE" }};
      int idx = ((int) Math.floor((double) ((yaw + 22.5f) / 45.0f))) % 8;
      return dirs[idx];
    }}
    if (id.equals("Zone")) {{
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) return "?";
      {WLD} w = {UNI}.get().getWorld(wu);
      return w == null ? "?" : w.getName();
    }}
    if (id.equals("Gclock") || id.equals("Day")) {{
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
      if (id.equals("Day")) return "Day " + (ms / dayMs);
      long inDay = ms % dayMs;
      long hh = inDay / 3600000L;
      long mm = (inDay % 3600000L) / 60000L;
      return (hh < 10 ? "0" : "") + hh + ":" + (mm < 10 ? "0" : "") + mm;
    }}
    if (id.equals("Rclock")) {{
      java.time.LocalTime n = java.time.LocalTime.now();
      int h = n.getHour(); int m = n.getMinute();
      return (h < 10 ? "0" : "") + h + ":" + (m < 10 ? "0" : "") + m;
    }}
    if (id.equals("Session")) {{
      long s = (System.currentTimeMillis() - joinMs) / 1000L;
      long h = s / 3600L; long m = (s % 3600L) / 60L;
      return h > 0 ? (h + "h " + m + "m") : (m + "m " + (s % 60L) + "s");
    }}
    if (id.equals("Online")) return {UNI}.get().getPlayers().size() + " online";
  }} catch (Throwable t) {{ return "?"; }}
  return "?";
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static {ANC} buildAnchor({PKG}.WLayout l) {{
  {ANC} a = new {ANC}();
  Integer dx = Integer.valueOf(l.dx); Integer dy = Integer.valueOf(l.dy);
  int w = 180 * l.scale / 100; int h = 26 * l.scale / 100;
  a.setWidth({VAL}.of(Integer.valueOf(w)));
  a.setHeight({VAL}.of(Integer.valueOf(h)));
  String an = l.anchor;
  if (an.equals("tl")) {{ a.setTop({VAL}.of(dy)); a.setLeft({VAL}.of(dx)); }}
  else if (an.equals("t")) {{ a.setTop({VAL}.of(dy)); a.setHorizontal({VAL}.of(dx)); }}
  else if (an.equals("tr")) {{ a.setTop({VAL}.of(dy)); a.setRight({VAL}.of(dx)); }}
  else if (an.equals("l")) {{ a.setVertical({VAL}.of(dy)); a.setLeft({VAL}.of(dx)); }}
  else if (an.equals("c")) {{ a.setVertical({VAL}.of(dy)); a.setHorizontal({VAL}.of(dx)); }}
  else if (an.equals("r")) {{ a.setVertical({VAL}.of(dy)); a.setRight({VAL}.of(dx)); }}
  else if (an.equals("bl")) {{ a.setBottom({VAL}.of(dy)); a.setLeft({VAL}.of(dx)); }}
  else if (an.equals("b")) {{ a.setBottom({VAL}.of(dy)); a.setHorizontal({VAL}.of(dx)); }}
  else {{ a.setBottom({VAL}.of(dy)); a.setRight({VAL}.of(dx)); }}
  return a;
}}""", wid))

wid.addMethod(CtNewMethod.make(f"""
public static String anchorSrc({PKG}.WLayout l) {{
  int w = 180 * l.scale / 100; int h = 26 * l.scale / 100;
  String a = l.anchor; String m;
  if (a.equals("tl")) m = "Top: " + l.dy + ", Left: " + l.dx;
  else if (a.equals("t")) m = "Top: " + l.dy + ", Horizontal: " + l.dx;
  else if (a.equals("tr")) m = "Top: " + l.dy + ", Right: " + l.dx;
  else if (a.equals("l")) m = "Vertical: " + l.dy + ", Left: " + l.dx;
  else if (a.equals("c")) m = "Vertical: " + l.dy + ", Horizontal: " + l.dx;
  else if (a.equals("r")) m = "Vertical: " + l.dy + ", Right: " + l.dx;
  else if (a.equals("bl")) m = "Bottom: " + l.dy + ", Left: " + l.dx;
  else if (a.equals("b")) m = "Bottom: " + l.dy + ", Horizontal: " + l.dx;
  else m = "Bottom: " + l.dy + ", Right: " + l.dx;
  return "(" + m + ", Width: " + w + ", Height: " + h + ")";
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static String widgetSrc(String id, {PKG}.WLayout l) {{
  int fs = 12 * l.scale / 100; if (fs < 6) fs = 6;
  return "Group #SkyyW" + id + " {{ Anchor: " + anchorSrc(l) + "; Background: #0b1524(0.72); Label #SkyyW" + id + "Txt {{ Anchor: (Full: 0); Text: \\"\\"; Style: (FontSize: " + fs + ", RenderBold: true, TextColor: #eaf6ff, HorizontalAlignment: Center, VerticalAlignment: Center); }} }}";
}}""", wid))

# ================= LayoutStore =================
lst.addField(CtField.make("public static java.nio.file.Path DIR;", lst))
lst.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();", lst))
lst.addMethod(CtNewMethod.make(f"""
public static java.util.Map get(java.util.UUID u) {{
  java.util.Map m = (java.util.Map) CACHE.get(u);
  if (m != null) return m;
  m = new java.util.concurrent.ConcurrentHashMap();
  String[] ids = {PKG}.Widgets.IDS;
  try {{
    java.nio.file.Path f = DIR.resolve(u.toString() + ".properties");
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {{
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try {{ p.load(in); }} finally {{ in.close(); }}
      for (int i = 0; i < ids.length; i++) {{
        String v = p.getProperty(ids[i]);
        {PKG}.WLayout d = {PKG}.Widgets.def(ids[i]);
        m.put(ids[i], v == null ? d : {PKG}.WLayout.parse(v, d));
      }}
    }}
  }} catch (Throwable t) {{ }}
  for (int i = 0; i < ids.length; i++) if (!m.containsKey(ids[i])) m.put(ids[i], {PKG}.Widgets.def(ids[i]));
  java.util.Map prev = (java.util.Map) CACHE.putIfAbsent(u, m);
  return prev != null ? prev : m;
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
    java.nio.file.Path tmp = DIR.resolve(u.toString() + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try {{ p.store(out, "SkyyHud layout"); }} finally {{ out.close(); }}
    java.nio.file.Files.move(tmp, DIR.resolve(u.toString() + ".properties"), new java.nio.file.CopyOption[] {{ java.nio.file.StandardCopyOption.REPLACE_EXISTING }});
  }} catch (Throwable t) {{ }}
}}""", lst))
lst.addMethod(CtNewMethod.make(f"""
public static String export(java.util.UUID u) {{
  java.util.Map m = get(u);
  StringBuilder sb = new StringBuilder();
  String[] ids = {PKG}.Widgets.IDS;
  for (int i = 0; i < ids.length; i++) {{
    {PKG}.WLayout l = ({PKG}.WLayout) m.get(ids[i]);
    if (l == null) continue;
    if (sb.length() > 0) sb.append(";");
    sb.append(ids[i]).append("=").append(l.ser());
  }}
  return sb.toString();
}}""", lst))
lst.addMethod(CtNewMethod.make(f"""
public static int importCode(java.util.UUID u, String code) {{
  java.util.Map m = get(u);
  int n = 0;
  String[] parts = code.trim().split(";");
  for (int i = 0; i < parts.length; i++) {{
    int eq = parts[i].indexOf('=');
    if (eq <= 0) continue;
    String id = parts[i].substring(0, eq).trim();
    if (!m.containsKey(id)) continue;
    {PKG}.WLayout l = {PKG}.WLayout.parse(parts[i].substring(eq + 1), null);
    if (l == null) continue;
    m.put(id, l); n++;
  }}
  if (n > 0) save(u);
  return n;
}}""", lst))
lst.addMethod(CtNewMethod.make(f"""
public static void reset(java.util.UUID u) {{
  java.util.Map m = get(u);
  String[] ids = {PKG}.Widgets.IDS;
  for (int i = 0; i < ids.length; i++) m.put(ids[i], {PKG}.Widgets.def(ids[i]));
  save(u);
}}""", lst))

# ================= HudMain =================
hudc.addField(CtField.make("public java.util.UUID uuid;", hudc))
hudc.addField(CtField.make("public long joinMs;", hudc))
hudc.addField(CtField.make("public final java.util.concurrent.ConcurrentHashMap last = new java.util.concurrent.ConcurrentHashMap();", hudc))
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
    if (!l.en) continue;
    String t = {PKG}.Widgets.text(ids[i], pr, this.joinMs);
    String prev = (String) this.last.get(ids[i]);
    if (full || prev == null || !prev.equals(t)) {{
      this.last.put(ids[i], t);
      b.set("#SkyyW" + ids[i] + "Txt.Text", t);
    }}
  }}
}}""", hudc))
hudc.addMethod(CtNewMethod.make(f"""
protected void build({UCB} b) {{
  // 0.2.3: whole HUD sent inline (pattern from EndlessLeveling DungeonQueueHud) - no .ui document lookup on the client.
  b.appendInline((String) null, "Group #SkyyHudRoot {{ Anchor: (Full: 0); }}");
  java.util.Map m = {PKG}.LayoutStore.get(this.uuid);
  String[] ids = {PKG}.Widgets.IDS;
  for (int i = 0; i < ids.length; i++) {{
    {PKG}.WLayout l = ({PKG}.WLayout) m.get(ids[i]);
    if (l == null || !l.en) continue;
    b.appendInline("#SkyyHudRoot", {PKG}.Widgets.widgetSrc(ids[i], l));
  }}
  this.last.clear();
  fill(b, true);
}}""", hudc))
hudc.addMethod(CtNewMethod.make(f"""
public void tick() {{
  try {{
    {UCB} b = new {UCB}();
    fill(b, false);
    if (b.getCommands().length > 0) update(false, b);
  }} catch (Throwable t) {{ }}
}}""", hudc))
hudc.addMethod(CtNewMethod.make("""
public void rebuild() {
  try { show(); } catch (Throwable t) { }
}""", hudc))

# ================= Plugin (part A) =================
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
    if (pr == null || !pr.isValid()) {{ it.remove(); {PKG}.LayoutStore.CACHE.remove(e.getKey()); continue; }}
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
  return (l.en ? "ON   " : "off   ") + l.anchor.toUpperCase() + "   x" + l.dx + "  y" + l.dy + "   " + l.scale + "%";
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  b.appendInline((String) null, "Group #SkyyEditorRoot {{ Anchor: (Full: 0); }}");
  b.appendInline("#SkyyEditorRoot", "Group #SkyyEditor {{ Anchor: (Horizontal: 0, Vertical: 0, Width: 700, Height: 480); Background: #0b1524(0.94); Padding: (Horizontal: 14, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyyEditor", "Group {{ Anchor: (Height: 2); Background: #7fe07f; }}");
  b.appendInline("#SkyyEditor", "Label {{ Anchor: (Height: 26); Text: \\"SkyyHud Editor\\"; Style: (FontSize: 15, RenderBold: true, TextColor: #eaffea, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyEditor", "Label {{ Anchor: (Height: 14); Text: \\"On/Off - anchor (TL T TR L C R BL B BR) - nudge X/Y by 10 - scale S. Changes apply instantly. /skyyhud export | import | reset\\"; Style: (FontSize: 10, TextColor: #9fb8d0, HorizontalAlignment: Center); }}");
  String[] ids = {PKG}.Widgets.IDS;
  String[] acts = new String[] {{ {ACTS_JAVA} }};
  String[] labels = new String[] {{ {ACT_LABELS_JAVA} }};
  String bs = "Style: TextButtonStyle(Default: (Background: #1d3a5f, LabelStyle: (FontSize: 10, TextColor: #dceeff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #2f5a8f, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #0f2038, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  for (int i = 0; i < ids.length; i++) {{
    b.appendInline("#SkyyEditor", "Group #SkyyERow" + ids[i] + " {{ Anchor: (Height: 48); LayoutMode: Top; Padding: (Vertical: 2); }}");
    b.appendInline("#SkyyERow" + ids[i], "Group #SkyyEHead" + ids[i] + " {{ Anchor: (Height: 18); LayoutMode: Left; }}");
    b.appendInline("#SkyyEHead" + ids[i], "Label {{ Anchor: (Width: 130, Height: 18); Text: \\"" + {PKG}.Widgets.label(ids[i]) + "\\"; Style: (FontSize: 11, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyEHead" + ids[i], "Label #SkyyEInfo" + ids[i] + " {{ Anchor: (Width: 400, Height: 18); Text: \\"" + rowInfo(ids[i]) + "\\"; Style: (FontSize: 10, TextColor: #9fb8d0, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyERow" + ids[i], "Group #SkyyEBtns" + ids[i] + " {{ Anchor: (Height: 24); LayoutMode: Left; }}");
    for (int a = 0; a < acts.length; a++) {{
      int w = a == 0 ? 54 : 36;
      b.appendInline("#SkyyEBtns" + ids[i], "TextButton #SkyyE" + ids[i] + acts[a] + " {{ Anchor: (Width: " + w + ", Height: 22); Text: \\"" + labels[a] + "\\"; " + bs + " }}");
      ev.addEventBinding({BT}.Activating, "#SkyyE" + ids[i] + acts[a], {EVD}.of("a", ids[i] + ":" + acts[a]));
    }}
  }}
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    String[] ids = {PKG}.Widgets.IDS;
    String[] acts = new String[] {{ {ACTS_JAVA} }};
    String wid2 = null; String act = null;
    for (int i = 0; i < ids.length && wid2 == null; i++) {{
      for (int a = 0; a < acts.length; a++) {{
        if (data.indexOf(ids[i] + ":" + acts[a] + "\\"") >= 0 || data.indexOf("#SkyyE" + ids[i] + acts[a] + "\\"") >= 0) {{ wid2 = ids[i]; act = acts[a]; break; }}
      }}
    }}
    if (wid2 == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    java.util.Map m = {PKG}.LayoutStore.get(u);
    {PKG}.WLayout l = ({PKG}.WLayout) m.get(wid2);
    if (l == null) return;
    if (act.equals("Tog")) l.en = !l.en;
    else if (act.equals("Xm")) l.dx -= 10;
    else if (act.equals("Xp")) l.dx += 10;
    else if (act.equals("Ym")) l.dy -= 10;
    else if (act.equals("Yp")) l.dy += 10;
    else if (act.equals("Sm")) l.scale -= 10;
    else if (act.equals("Sp")) l.scale += 10;
    else if (act.equals("B2")) l.anchor = "b";
    else l.anchor = act.toLowerCase();
    if (l.dx < 0) l.dx = 0;
    if (l.dy < 0) l.dy = 0;
    if (l.scale < 50) l.scale = 50;
    if (l.scale > 200) l.scale = 200;
    {PKG}.LayoutStore.save(u);
    plugin.rebuildFor(u);
    {UCB} b = new {UCB}();
    b.set("#SkyyEInfo" + wid2 + ".Text", rowInfo(wid2));
    sendUpdate(b);
  }} catch (Throwable t) {{ }}
}}""", page))

# ================= HudCmd =================
cmd.addField(CtField.make(f"public {PKG}.SkyyHudPlugin plugin;", cmd))
cmd.addField(CtField.make(f"public {OPT} actionArg;", cmd))
cmd.addField(CtField.make(f"public {OPT} codeArg;", cmd))
cmd.addConstructor(CtNewConstructor.make(f"""
public HudCmd({PKG}.SkyyHudPlugin p) {{
  super("skyyhud", "SkyyHud: open the HUD editor, or export/import/reset your layout");
  addAliases(new String[] {{ "shud" }});
  this.plugin = p;
  this.actionArg = withOptionalArg("action", "export | import | reset (omit to open the editor)", {ARG}.STRING);
  this.codeArg = withOptionalArg("code", "layout code (for import)", {ARG}.GREEDY_STRING);
}}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    String action = ctx.provided(this.actionArg) ? String.valueOf(ctx.get(this.actionArg)).toLowerCase() : "";
    java.util.UUID u = pr.getUuid();
    if (action.equals("export")) {{
      pr.sendMessage({MSG}.raw("[SkyyHud] layout code: " + {PKG}.LayoutStore.export(u)));
      return;
    }}
    if (action.equals("import")) {{
      if (!ctx.provided(this.codeArg)) {{ pr.sendMessage({MSG}.raw("[SkyyHud] usage: /skyyhud import <code>")); return; }}
      int n = {PKG}.LayoutStore.importCode(u, String.valueOf(ctx.get(this.codeArg)));
      if (n > 0) this.plugin.rebuildFor(u);
      pr.sendMessage({MSG}.raw("[SkyyHud] imported " + n + " widget layout(s)"));
      return;
    }}
    if (action.equals("reset")) {{
      {PKG}.LayoutStore.reset(u);
      this.plugin.rebuildFor(u);
      pr.sendMessage({MSG}.raw("[SkyyHud] layout reset to defaults"));
      return;
    }}
    if (action.length() > 0) {{ pr.sendMessage({MSG}.raw("[SkyyHud] unknown action '" + action + "' (export | import <code> | reset)")); return; }}
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) {{ pr.sendMessage({MSG}.raw("[SkyyHud] player entity not found")); return; }}
    if (!this.plugin.huds.containsKey(u)) this.plugin.attach(pr);
    player.getPageManager().openCustomPage(ref, store, new {PKG}.EditorPage(pr, this.plugin));
  }} catch (Throwable t) {{
    pr.sendMessage({MSG}.raw("[SkyyHud] error: " + t));
  }}
}}""", cmd))

# ================= TickTask =================
tick.addInterface(pool.get("java.lang.Runnable"))
tick.addField(CtField.make(f"public {PKG}.SkyyHudPlugin plugin;", tick))
tick.addConstructor(CtNewConstructor.make(f"public TickTask({PKG}.SkyyHudPlugin p) {{ this.plugin = p; }}", tick))
tick.addMethod(CtNewMethod.make("""
public void run() {
  try { plugin.tickAll(); } catch (Throwable t) { }
}""", tick))

# ================= AttachTask (delayed, channel-gated HUD open; pattern from EndlessLeveling) =================
att.addInterface(pool.get("java.lang.Runnable"))
att.addField(CtField.make(f"public {PKG}.SkyyHudPlugin plugin;", att))
att.addField(CtField.make(f"public {PR} pr;", att))
att.addField(CtField.make("public boolean onWorld;", att))
att.addField(CtField.make("public int calm;", att))
att.addField(CtField.make("public int tries;", att))
att.addConstructor(CtNewConstructor.make(f"public AttachTask({PKG}.SkyyHudPlugin p, {PR} pr) {{ this.plugin = p; this.pr = pr; this.onWorld = false; this.calm = 0; this.tries = 0; }}", att))
att.addMethod(CtNewMethod.make(f"""
public void later(long ms) {{
  this.onWorld = false;
  {HSV}.SCHEDULED_EXECUTOR.schedule(this, ms, java.util.concurrent.TimeUnit.MILLISECONDS);
}}""", att))
att.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (pr == null || !pr.isValid()) return;
    if (!this.onWorld) {{
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) {{ if (++this.tries < 240) later(500L); return; }}
      {WLD} w = {UNI}.get().getWorld(wu);
      if (w == null) {{ if (++this.tries < 240) later(500L); return; }}
      this.onWorld = true;
      w.execute(this);
      return;
    }}
    {REF} r = pr.getReference();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    {PLA} player = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    if (player == null) {{ if (++this.tries < 240) later(500L); return; }}
    boolean writable = true;
    try {{
      com.hypixel.hytale.server.core.io.PacketHandler ph = player.getPlayerConnection();
      com.hypixel.hytale.protocol.io.ChannelConnection ch = ph == null ? null : ph.getChannel(com.hypixel.hytale.protocol.NetworkChannel.WorldMap);
      writable = ch == null || ch.isWritable();
    }} catch (Throwable t) {{ writable = true; }}
    if (writable) this.calm++; else this.calm = 0;
    if (this.calm < 3) {{ if (++this.tries < 240) later(500L); return; }}
    this.plugin.attach(pr);
  }} catch (Throwable t) {{ }}
}}""", att))

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
    new {PKG}.AttachTask(plugin, pr).later(1500L);
  }} catch (Throwable t) {{ }}
}}""", rdy))

# ================= Plugin (part B: lifecycle) =================
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.LayoutStore.DIR = getDataDirectory().resolve("layouts");
  getEventRegistry().registerGlobal({PRE}.class, new {PKG}.SkyyHudReady(this));
  getCommandRegistry().registerCommand(new {PKG}.HudCmd(this));
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.TickTask(this), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyHud] {VERSION} ready - /skyyhud (alias /shud)");
}}""", pl))
pl.addMethod(CtNewMethod.make("""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  this.huds.clear();
  super.shutdown();
}""", pl))

for c in (wl, lst, wid, hudc, page, cmd, tick, att, rdy, pl):
    c.writeFile(OUT)
print("classes written")

# ================= UI documents =================
def anchor_src(a, dx, dy, w=180, h=26):
    m = {"tl": "Top: %d, Left: %d", "t": "Top: %d, Horizontal: %d", "tr": "Top: %d, Right: %d",
         "l": "Vertical: %d, Left: %d", "c": "Vertical: %d, Horizontal: %d", "r": "Vertical: %d, Right: %d",
         "bl": "Bottom: %d, Left: %d", "b": "Bottom: %d, Horizontal: %d", "br": "Bottom: %d, Right: %d"}[a] % (dy, dx)
    return "(%s, Width: %d, Height: %d)" % (m, w, h)

HUD_UI = "Group #SkyyHudRoot {\n  Anchor: (Full: 0);\n\n"
for i in IDS:
    en, a, dx, dy = DEFAULTS[i]
    HUD_UI += """  Group #w_%s {
    Anchor: %s;
    Visible: %s;
    Background: #0b1524(0.72);
    Label #w_%s_t {
      Anchor: (Full: 0);
      Style: (FontSize: 12, RenderBold: true, TextColor: #eaf6ff, HorizontalAlignment: Center, VerticalAlignment: Center);
      Text: "";
    }
  }

""" % (i, anchor_src(a, dx, dy), str(en).lower(), i)
HUD_UI += "}\n"

BTN_STYLE = """@Btn = TextButtonStyle(
  Default: (Background: #1d3a5f, LabelStyle: (FontSize: 10, TextColor: #dceeff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)),
  Hovered: (Background: #2f5a8f, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)),
  Pressed: (Background: #0f2038, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center))
);
"""
rows = ""
for i in IDS:
    btns = ""
    for a in ACTS:
        w = 54 if a == "tog" else 34
        btns += '        TextButton #e_%s_%s { Anchor: (Width: %d, Height: 22); Text: "%s"; Style: @Btn; }\n' % (i, a, w, ACT_LABEL[a])
    rows += """    Group #e_row_%s {
      Anchor: (Height: 48);
      LayoutMode: Top;
      Padding: (Vertical: 2);
      Group {
        Anchor: (Height: 18);
        LayoutMode: Left;
        Label { Anchor: (Width: 130, Height: 18); Style: (FontSize: 11, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); Text: "%s"; }
        Label #e_info_%s { Anchor: (Width: 400, Height: 18); Style: (FontSize: 10, TextColor: #9fb8d0, VerticalAlignment: Center); Text: ""; }
      }
      Group {
        Anchor: (Height: 24);
        LayoutMode: Left;
%s      }
    }
""" % (i, LABELS[i], i, btns)

EDITOR_UI = BTN_STYLE + """
Group {
  Anchor: (Full: 0);
  Group #SkyyHudEditor {
    Anchor: (Horizontal: 0, Vertical: 0, Width: 680, Height: 470);
    Background: #0b1524(0.94);
    Padding: (Horizontal: 14, Vertical: 10);
    LayoutMode: Top;
    Group { Anchor: (Height: 2); Background: #7fe07f; }
    Label { Anchor: (Height: 26); Style: (FontSize: 15, RenderBold: true, TextColor: #eaffea, HorizontalAlignment: Center, VerticalAlignment: Center); Text: "SkyyHud Editor"; }
    Label { Anchor: (Height: 14); Style: (FontSize: 10, TextColor: #9fb8d0, HorizontalAlignment: Center); Text: "On/Off - anchor (TL T TR L C R BL B BR) - nudge X/Y by 10 - scale S. Changes apply instantly. /skyyhud export | import | reset"; }
%s  }
}
""" % rows

jar = os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)
# 0.2.1: packs that contain ONLY .ui files (ours, ClockHud) are never found by the client from cache;
# every working HUD mod ships at least one PNG in its asset pack. Ship a tiny icon + a pixel texture.
png_root = open(os.path.join(HERE, "icon-256.png"), "rb").read()
png_dot = open(os.path.join(HERE, "skyyhud_dot.png"), "rb").read()
B.assemble(jar, B.manifest("SkyyHud", VERSION, "SkyyHud: customizable server-side HUD. 8 widgets, per-player layouts, /skyyhud editor + layout codes. Zero dependencies.", PKG + ".SkyyHudPlugin"),
           OUT, {"Common/UI/Custom/SkyyHud/dot.png": png_dot, "icon-256.png": png_root})
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyHud.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyHud" % VERSION, disable_prefix="Skyy:")
