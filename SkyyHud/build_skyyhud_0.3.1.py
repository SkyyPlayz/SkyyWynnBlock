"""SkyyHud 0.2 - build script (javassist via jpype).
Run:   python build_skyyhud_0.2.py            -> SkyyHud/SkyyHud-0.2.jar
       python build_skyyhud_0.2.py --deploy   -> also copies to Mods/SkyyHud.jar and enables "Skyy:0.2 SkyyHud" in the HUD mod world
Changes vs 0.1.x: no bisect markers, no test auto-open, editor uses TextButton + EventData payloads,
/skyyhud (alias /shud) opens the editor; /skyyhud export | import <code> | reset for layout codes.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.3.1"
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
IGS = "com.hypixel.hytale.server.core.ui.ItemGridSlot"
IS  = "com.hypixel.hytale.server.core.inventory.ItemStack"

for c, m in ((PLA, "getComponentType"), (HSV, "SCHEDULED_EXECUTOR"), (UEB, "addEventBinding"), (EVD, "of"),
             (PR, "getHeadRotation"), (WTR, "getGameDateTime"), (ANC, "setHorizontal"), (CTX, "provided"),
             ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "openCustomPage"), (IGS, "setItemStack"), (IGS, "setName")):
    B.probe(pool, c, m)
pool.get(OPT)  # class must exist

PKG = "com.skyy.hud"
wl   = pool.makeClass(PKG + ".WLayout")
lst  = pool.makeClass(PKG + ".LayoutStore")
wid  = pool.makeClass(PKG + ".Widgets")
hudc = pool.makeClass(PKG + ".HudMain", pool.get(HUD))
page = pool.makeClass(PKG + ".EditorPage", pool.get(PAGE))
sett = pool.makeClass(PKG + ".SettingsPage", pool.get(PAGE))
wpg  = pool.makeClass(PKG + ".WidgetsPage", pool.get(PAGE))
cmd  = pool.makeClass(PKG + ".HudCmd", pool.get(APC))
tick = pool.makeClass(PKG + ".TickTask")
rdy  = pool.makeClass(PKG + ".SkyyHudReady")
pl   = pool.makeClass(PKG + ".SkyyHudPlugin", pool.get(JP))
att  = pool.makeClass(PKG + ".AttachTask")

IDS = ["Coords", "Zone", "Gclock", "Rclock", "Day", "Session", "Online", "Coins"]
ACTS = ["Tog", "Tl", "T", "Tr", "L", "C", "R", "Bl", "B2", "Br", "Lt", "Rt", "Up", "Dn", "Sm", "Sp"]
ACT_LABEL = {"Tog": "On/Off", "Tl": "TL", "T": "T", "Tr": "TR", "L": "L", "C": "C", "R": "R", "Bl": "BL", "B2": "B", "Br": "BR",
             "Lt": "<", "Rt": ">", "Up": "^", "Dn": "v", "Sm": "Size-", "Sp": "Size+"}
DEFAULTS = {"Coords": (True, "tl", 8, 8), "Zone": (True, "tr", 8, 8), "Gclock": (True, "bl", 8, 40),
            "Rclock": (False, "bl", 8, 70), "Day": (False, "br", 8, 40), "Session": (False, "br", 8, 70), "Online": (False, "tr", 8, 40), "Coins": (True, "br", 8, 8)}
LABELS = {"Coords": "Coordinates", "Zone": "Zone", "Gclock": "Game Clock", "Rclock": "Real Clock",
          "Day": "Day Counter", "Session": "Session Time", "Online": "Players Online", "Coins": "Coins"}
ACTS_JAVA = ", ".join('"%s"' % a for a in ACTS)
ACT_LABELS_JAVA = ", ".join('"%s"' % ACT_LABEL[a] for a in ACTS)

# ================= WLayout =================
for f in ("public boolean en;", "public String anchor;", "public int dx;", "public int dy;", "public int scale;"):
    wl.addField(CtField.make(f, wl))
wl.addField(CtField.make("public boolean bg;", wl))
wl.addConstructor(CtNewConstructor.make("""
public WLayout(boolean en, String anchor, int dx, int dy, int scale) {
  this.en = en; this.anchor = anchor; this.dx = dx; this.dy = dy; this.scale = scale; this.bg = true;
}""", wl))
wl.addMethod(CtNewMethod.make("""
public String ser() { return (en ? "1" : "0") + "," + anchor + "," + dx + "," + dy + "," + scale + "," + (bg ? "1" : "0"); }""", wl))
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
    if (sc < 50) sc = 50;
    if (sc > 200) sc = 200;
    {PKG}.WLayout w = new {PKG}.WLayout("1".equals(p[0].trim()), a, dx, dy, sc);
    if (p.length > 5) w.bg = "1".equals(p[5].trim());
    return w;
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
      if (id.equals("Day")) {{
        long days = java.time.temporal.ChronoUnit.DAYS.between({WTR}.ZERO_YEAR, tr.getGameTime()) + 1L;
        return "Day " + days;
      }}
      java.time.LocalDateTime dt = tr.getGameDateTime();
      int hh = dt.getHour(); int mm = dt.getMinute();
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
    if (id.equals("Coins")) {{
      Object o = null;
      try {{ Object b = System.getProperties().get("skyy.bridge"); if (b != null) o = ((java.util.Map) b).get("coins:" + pr.getUuid().toString()); }} catch (Throwable t) {{ o = null; }}
      if (o == null) return "Coins: -";
      return "Coins: " + java.text.NumberFormat.getIntegerInstance(java.util.Locale.US).format(((Long) o).longValue());
    }}
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
  return "Group #SkyyW" + id + " {{ Anchor: " + anchorSrc(l) + "; " + (l.bg ? "Background: #0b1524(0.72); " : "") + "Label #SkyyW" + id + "Txt {{ Anchor: (Full: 0); Text: \\"\\"; Style: (FontSize: " + fs + ", RenderBold: true, TextColor: #eaf6ff, HorizontalAlignment: Center, VerticalAlignment: Center); }} }}";
}}""", wid))

wid.addMethod(CtNewMethod.make("""
public static String chipItem(String id) {
  if (id.equals("Coords")) return "Tool_Map";
  if (id.equals("Zone")) return "Furniture_Crude_Sign";
  if (id.equals("Gclock")) return "Deco_Lantern";
  if (id.equals("Rclock")) return "Deco_Scroll";
  if (id.equals("Day")) return "Plant_Seeds_Sunflower";
  if (id.equals("Session")) return "Furniture_Crude_Torch";
  if (id.equals("Online")) return "Furniture_Flag_Orange";
  if (id.equals("Coins")) return "Ingredient_Bar_Gold";
  return "Ingredient_Crystal_White";
}""", wid))
# screen position (top-left corner of the widget, 1080p) from a layout
wid.addMethod(CtNewMethod.make(f"""
public static int[] screenPos({PKG}.WLayout l) {{
  int w = 180 * l.scale / 100; int h = 26 * l.scale / 100;
  String a = l.anchor; int x; int y;
  if (a.equals("tl") || a.equals("l") || a.equals("bl")) x = l.dx;
  else if (a.equals("tr") || a.equals("r") || a.equals("br")) x = 1920 - w - l.dx;
  else x = 960 - w / 2 + l.dx;
  if (a.equals("tl") || a.equals("t") || a.equals("tr")) y = l.dy;
  else if (a.equals("bl") || a.equals("b") || a.equals("br")) y = 1080 - h - l.dy;
  else y = 540 - h / 2 + l.dy;
  return new int[] {{ x, y }};
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static int cellOf({PKG}.WLayout l) {{
  int[] p = screenPos(l);
  int col = (p[0] + 90) / 120; if (col < 0) col = 0; if (col > 15) col = 15;
  int row = (p[1] + 13) / 120; if (row < 0) row = 0; if (row > 8) row = 8;
  return row * 16 + col;
}}""", wid))
# place a widget so that its top-left sits at the cell; anchor edge chosen by which third of the screen the cell is in
wid.addMethod(CtNewMethod.make(f"""
public static void placeAtCell({PKG}.WLayout l, int cell) {{
  int col = cell % 16; int row = cell / 16;
  int x = col * 120; int y = row * 120;
  int w = 180 * l.scale / 100; int h = 26 * l.scale / 100;
  boolean left = col <= 7; boolean top = row <= 4;
  l.dx = left ? x : 1920 - w - x;
  l.dy = top ? y : 1080 - h - y;
  l.anchor = top ? (left ? "tl" : "tr") : (left ? "bl" : "br");
  if (l.dx < 0) l.dx = 0;
  if (l.dy < 0) l.dy = 0;
}}""", wid))

# ================= LayoutStore =================
lst.addField(CtField.make("public static java.nio.file.Path DIR;", lst))
lst.addField(CtField.make("public static com.hypixel.hytale.logger.HytaleLogger LOG;", lst))
lst.addMethod(CtNewMethod.make("""
public static void debug(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyHud] " + msg); } catch (Throwable t) { }
}""", lst))
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

lst.addMethod(CtNewMethod.make(f"""
public static java.nio.file.Path profileDir(java.util.UUID u) {{
  return DIR.resolveSibling("profiles").resolve(u.toString());
}}""", lst))
lst.addMethod(CtNewMethod.make(f"""
public static String cleanName(String n) {{
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < n.length() && sb.length() < 24; i++) {{ char c = n.charAt(i); if (Character.isLetterOrDigit(c) || c == '-') sb.append(c); }}
  return sb.toString();
}}""", lst))
lst.addMethod(CtNewMethod.make(f"""
public static boolean profileSave(java.util.UUID u, String name) {{
  try {{
    String n = cleanName(name); if (n.length() == 0) return false;
    java.nio.file.Path d = profileDir(u);
    java.nio.file.Files.createDirectories(d, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(d.resolve(n + ".txt"), export(u).getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    return true;
  }} catch (Throwable t) {{ return false; }}
}}""", lst))
lst.addMethod(CtNewMethod.make(f"""
public static int profileLoad(java.util.UUID u, String name) {{
  try {{
    String n = cleanName(name); if (n.length() == 0) return -1;
    java.nio.file.Path f = profileDir(u).resolve(n + ".txt");
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return -1;
    String code = new String(java.nio.file.Files.readAllBytes(f), "UTF-8");
    return importCode(u, code);
  }} catch (Throwable t) {{ return -1; }}
}}""", lst))
lst.addMethod(CtNewMethod.make(f"""
public static boolean profileDelete(java.util.UUID u, String name) {{
  try {{ String n = cleanName(name); return java.nio.file.Files.deleteIfExists(profileDir(u).resolve(n + ".txt")); }} catch (Throwable t) {{ return false; }}
}}""", lst))
lst.addMethod(CtNewMethod.make(f"""
public static String profileList(java.util.UUID u) {{
  try {{
    java.nio.file.Path d = profileDir(u);
    if (!java.nio.file.Files.exists(d, new java.nio.file.LinkOption[0])) return "";
    StringBuilder sb = new StringBuilder();
    java.io.File[] fs = d.toFile().listFiles();
    if (fs == null) return "";
    java.util.Arrays.sort(fs);
    for (int i = 0; i < fs.length; i++) {{ String n = fs[i].getName(); if (n.endsWith(".txt")) {{ if (sb.length() > 0) sb.append(", "); sb.append(n.substring(0, n.length() - 4)); }} }}
    return sb.toString();
  }} catch (Throwable t) {{ return ""; }}
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

# WidgetsPage fields + constructor first (EditorPage references it)
wpg.addField(CtField.make(f"public {PKG}.SkyyHudPlugin plugin;", wpg))
wpg.addConstructor(CtNewConstructor.make(f"""
public WidgetsPage({PR} pr, {PKG}.SkyyHudPlugin plugin) {{
  super(pr, {LIFE}.CanDismiss);
  this.plugin = plugin;
}}""", wpg))

# SettingsPage fields + constructor first (EditorPage references it; javassist needs declaration order)
sett.addField(CtField.make(f"public {PKG}.SkyyHudPlugin plugin;", sett))
sett.addField(CtField.make("public String wid;", sett))
sett.addConstructor(CtNewConstructor.make(f"""
public SettingsPage({PR} pr, {PKG}.SkyyHudPlugin plugin, String wid) {{
  super(pr, {LIFE}.CanDismiss);
  this.plugin = plugin;
  this.wid = wid;
}}""", sett))

# ================= EditorPage v2 (Lunar-style: drag canvas + selected-widget bar) =================
page.addField(CtField.make(f"public {PKG}.SkyyHudPlugin plugin;", page))
page.addField(CtField.make("public String sel;", page))
page.addField(CtField.make("public String[] cellWidget;", page))
page.addField(CtField.make("public String info;", page))
page.addConstructor(CtNewConstructor.make(f"""
public EditorPage({PR} pr, {PKG}.SkyyHudPlugin plugin) {{
  super(pr, {LIFE}.CanDismiss);
  this.plugin = plugin;
  this.sel = null;
  this.info = "";
}}""", page))
page.addMethod(CtNewMethod.make("""
public static int jsonInt(String data, String key) {
  int p = data.indexOf("\\"" + key + "\\"");
  if (p < 0) return -1;
  int c = data.indexOf(':', p);
  if (c < 0) return -1;
  int i = c + 1;
  while (i < data.length() && (data.charAt(i) == ' ' || data.charAt(i) == '\\"')) i++;
  int j = i;
  while (j < data.length() && (Character.isDigit(data.charAt(j)) || data.charAt(j) == '-')) j++;
  if (j == i) return -1;
  try { return Integer.parseInt(data.substring(i, j)); } catch (Throwable t) { return -1; }
}""", page))
page.addMethod(CtNewMethod.make(f"""
public String selInfo() {{
  if (this.sel == null) return "Click a widget on the canvas to select it - drag a widget to move it";
  java.util.Map m = {PKG}.LayoutStore.get(this.playerRef.getUuid());
  {PKG}.WLayout l = ({PKG}.WLayout) m.get(this.sel);
  if (l == null) return "?";
  return {PKG}.Widgets.label(this.sel) + "   " + l.anchor.toUpperCase() + "  x" + l.dx + "  y" + l.dy + "   " + l.scale + "%";
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  java.util.Map m = {PKG}.LayoutStore.get(u);
  String[] ids = {PKG}.Widgets.IDS;
  String bs = "Style: TextButtonStyle(Default: (Background: #1d3a5f, LabelStyle: (FontSize: 10, TextColor: #dceeff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #2f5a8f, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #0f2038, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  b.appendInline((String) null, "Group #SkyyEditor {{ Anchor: (Width: 1330, Height: 930); Background: #0b1524(0.96); Padding: (Horizontal: 20, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyyEditor", "Group {{ Anchor: (Height: 2); Background: #7fe07f; }}");
  b.appendInline("#SkyyEditor", "Label {{ Anchor: (Height: 24); Text: \\"SkyyHud Editor\\"; Style: (FontSize: 15, RenderBold: true, TextColor: #eaffea, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyEditor", "Label {{ Anchor: (Height: 14); Text: \\"Drag a widget to move it. Click one to select it. The canvas is your screen at 2/3 scale.\\"; Style: (FontSize: 10, TextColor: #9fb8d0, HorizontalAlignment: Center); }}");
  b.appendInline("#SkyyEditor", "Group #SkyyECanvasWrap {{ Anchor: (Height: 726); }}");
  b.appendInline("#SkyyECanvasWrap", "ItemGrid #SkyyECanvas {{ Anchor: (Horizontal: 0, Top: 3, Width: 1280, Height: 720); SlotsPerRow: 16; AreItemsDraggable: true; Style: (SlotSize: 80, SlotIconSize: 56, SlotSpacing: 0); }}");
  this.cellWidget = new String[144];
  java.util.ArrayList slots = new java.util.ArrayList();
  for (int i = 0; i < 144; i++) slots.add(new {IGS}());
  for (int i = 0; i < ids.length; i++) {{
    {PKG}.WLayout l = ({PKG}.WLayout) m.get(ids[i]);
    if (l == null || !l.en) continue;
    int cell = {PKG}.Widgets.cellOf(l);
    int tries = 0;
    while (this.cellWidget[cell] != null && tries < 144) {{ cell = (cell + 1) % 144; tries++; }}
    this.cellWidget[cell] = ids[i];
    {IGS} gs = new {IGS}(new {IS}({PKG}.Widgets.chipItem(ids[i]), 1));
    gs.setName({PKG}.Widgets.label(ids[i]));
    gs.setDescription("Drag to move. Click to select.");
    gs.setActivatable(true);
    slots.set(cell, gs);
  }}
  b.set("#SkyyECanvas.Slots", slots);
  ev.addEventBinding({BT}.Dropped, "#SkyyECanvas", {EVD}.of("a", "drop"));
  ev.addEventBinding({BT}.SlotClicking, "#SkyyECanvas", {EVD}.of("a", "slot"));
  ev.addEventBinding({BT}.DragCancelled, "#SkyyECanvas", {EVD}.of("a", "dragcancel"));
  {{
    StringBuilder lg = new StringBuilder();
    for (int i = 0; i < ids.length; i++) {{
      {PKG}.WLayout l2 = ({PKG}.WLayout) m.get(ids[i]);
      if (l2 == null || !l2.en) continue;
      if (lg.length() > 0) lg.append("     ");
      lg.append({PKG}.Widgets.label(ids[i])).append(" = ").append({PKG}.Widgets.text(ids[i], this.playerRef, System.currentTimeMillis()));
    }}
    b.appendInline("#SkyyEditor", "Label #SkyyELegend {{ Anchor: (Height: 16); Text: \\"\\"; Style: (FontSize: 10, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    b.set("#SkyyELegend.Text", lg.toString());
  }}
  b.appendInline("#SkyyEditor", "Label #SkyyEInfo {{ Anchor: (Height: 18); Text: \\"" + selInfo().replace('\\"', ' ') + "\\"; Style: (FontSize: 11, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyEditor", "Group #SkyyEBar {{ Anchor: (Height: 30); LayoutMode: Left; Padding: (Top: 4); }}");
  if (this.sel != null) {{
    String[] acts = new String[] {{ "Lt", "Rt", "Up", "Dn", "Sm", "Sp", "Hide", "Cog" }};
    String[] labels = new String[] {{ "<", ">", "^", "v", "Size-", "Size+", "X hide", "Settings" }};
    for (int a = 0; a < acts.length; a++) {{
      int w = a < 4 ? 40 : (a < 6 ? 60 : 90);
      b.appendInline("#SkyyEBar", "TextButton #SkyyEB" + acts[a] + " {{ Anchor: (Width: " + w + ", Height: 26); Text: \\"" + labels[a] + "\\"; " + bs + " }}");
      b.appendInline("#SkyyEBar", "Label {{ Anchor: (Width: 4, Height: 24); Text: \\"\\"; }}");
      ev.addEventBinding({BT}.Activating, "#SkyyEB" + acts[a], {EVD}.of("a", "act:" + acts[a]));
    }}
  }}
  b.appendInline("#SkyyEditor", "Label {{ Anchor: (Height: 14); Text: \\"Hidden widgets - click to show\\"; Style: (FontSize: 10, TextColor: #9fb8d0, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyEditor", "Group #SkyyEOff {{ Anchor: (Height: 28); LayoutMode: Left; Padding: (Top: 2); }}");
  int off = 0;
  for (int i = 0; i < ids.length; i++) {{
    {PKG}.WLayout l = ({PKG}.WLayout) m.get(ids[i]);
    if (l == null || l.en) continue;
    off++;
    b.appendInline("#SkyyEOff", "TextButton #SkyyEOn" + ids[i] + " {{ Anchor: (Width: 78, Height: 22); Text: \\"" + {PKG}.Widgets.label(ids[i]) + "\\"; " + bs + " }}");
    b.appendInline("#SkyyEOff", "Label {{ Anchor: (Width: 4, Height: 22); Text: \\"\\"; }}");
    ev.addEventBinding({BT}.Activating, "#SkyyEOn" + ids[i], {EVD}.of("a", "show:" + ids[i]));
  }}
  if (off == 0) b.appendInline("#SkyyEOff", "Label {{ Anchor: (Width: 300, Height: 22); Text: \\"none\\"; Style: (FontSize: 10, TextColor: #6f8498, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyEditor", "Group #SkyyEFoot {{ Anchor: (Height: 30); LayoutMode: Left; Padding: (Top: 4); }}");
  b.appendInline("#SkyyEFoot", "Label {{ Anchor: (Width: 1100, Height: 26); Text: \\"" + (this.info == null ? "" : this.info.replace('\\"', ' ')) + "   /skyyhud export | import | reset | profile save|load|list <name>\\"; Style: (FontSize: 10, TextColor: #6f8498, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyEFoot", "TextButton #SkyyEWidgets {{ Anchor: (Width: 150, Height: 26); Text: \\"Widgets / Settings\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyEWidgets", {EVD}.of("a", "widgets"));
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    java.util.Map m = {PKG}.LayoutStore.get(u);
    String[] ids = {PKG}.Widgets.IDS;
    if (data.indexOf("\\"drop\\"") >= 0 || data.indexOf("Dropped") >= 0) {{
      int from = jsonInt(data, "SourceSlotId");
      int to = jsonInt(data, "SlotIndex");
      if (from < 0 || to < 0 || from >= 144 || to >= 144 || this.cellWidget == null) {{ {PKG}.LayoutStore.debug("drop payload: " + data); return; }}
      String wid = this.cellWidget[from];
      if (wid == null) return;
      if (this.cellWidget[to] != null && to != from) {{ this.info = "that spot is taken"; rebuild(); return; }}
      {PKG}.WLayout l = ({PKG}.WLayout) m.get(wid);
      if (l == null) return;
      {PKG}.Widgets.placeAtCell(l, to);
      this.sel = wid; this.info = "moved " + {PKG}.Widgets.label(wid);
      {PKG}.LayoutStore.save(u); plugin.rebuildFor(u); rebuild(); return;
    }}
    if (data.indexOf("\\"slot\\"") >= 0) {{
      int idx = jsonInt(data, "SlotIndex");
      if (idx < 0 || idx >= 144 || this.cellWidget == null) {{ {PKG}.LayoutStore.debug("slot payload: " + data); return; }}
      if (this.cellWidget[idx] != null) {{ this.sel = this.cellWidget[idx]; this.info = ""; rebuild(); }}
      return;
    }}
    if (data.indexOf("\\"dragcancel\\"") >= 0) return;
    if (data.indexOf("\\"widgets\\"") >= 0) {{
      {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
      if (player != null) player.getPageManager().openCustomPage(ref, st, new {PKG}.WidgetsPage(this.playerRef, this.plugin));
      return;
    }}
    for (int i = 0; i < ids.length; i++) {{
      if (data.indexOf("show:" + ids[i] + "\\"") >= 0) {{
        {PKG}.WLayout l = ({PKG}.WLayout) m.get(ids[i]);
        if (l != null) {{ l.en = true; this.sel = ids[i]; {PKG}.LayoutStore.save(u); plugin.rebuildFor(u); }}
        rebuild(); return;
      }}
    }}
    if (this.sel == null) return;
    {PKG}.WLayout l = ({PKG}.WLayout) m.get(this.sel);
    if (l == null) return;
    String a = l.anchor;
    boolean rightEdge = a.equals("tr") || a.equals("r") || a.equals("br");
    boolean leftEdge = a.equals("tl") || a.equals("l") || a.equals("bl");
    boolean bottomEdge = a.equals("bl") || a.equals("b") || a.equals("br");
    boolean topEdge = a.equals("tl") || a.equals("t") || a.equals("tr");
    if (data.indexOf("act:Cog\\"") >= 0) {{
      {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
      if (player != null) player.getPageManager().openCustomPage(ref, st, new {PKG}.SettingsPage(this.playerRef, this.plugin, this.sel));
      return;
    }}
    if (data.indexOf("act:Hide\\"") >= 0) {{ l.en = false; this.sel = null; }}
    else if (data.indexOf("act:Lt\\"") >= 0) l.dx += rightEdge ? 10 : -10;
    else if (data.indexOf("act:Rt\\"") >= 0) l.dx += rightEdge ? -10 : 10;
    else if (data.indexOf("act:Up\\"") >= 0) l.dy += bottomEdge ? 10 : -10;
    else if (data.indexOf("act:Dn\\"") >= 0) l.dy += bottomEdge ? -10 : 10;
    else if (data.indexOf("act:Sm\\"") >= 0) l.scale -= 10;
    else if (data.indexOf("act:Sp\\"") >= 0) l.scale += 10;
    else {{ {PKG}.LayoutStore.debug("unknown editor payload: " + data); return; }}
    if ((leftEdge || rightEdge) && l.dx < 0) l.dx = 0;
    if ((topEdge || bottomEdge) && l.dy < 0) l.dy = 0;
    if (l.scale < 50) l.scale = 50;
    if (l.scale > 200) l.scale = 200;
    {PKG}.LayoutStore.save(u); plugin.rebuildFor(u); rebuild();
  }} catch (Throwable t) {{ {PKG}.LayoutStore.debug("editor event failed: " + t); }}
}}""", page))

# ================= SettingsPage (cog) =================

sett.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  {PKG}.WLayout l = ({PKG}.WLayout) {PKG}.LayoutStore.get(u).get(this.wid);
  String bs = "Style: TextButtonStyle(Default: (Background: #1d3a5f, LabelStyle: (FontSize: 10, TextColor: #dceeff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #2f5a8f, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #0f2038, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  String on = "Style: TextButtonStyle(Default: (Background: #7fe07f, LabelStyle: (FontSize: 10, TextColor: #062a06, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #a0f0a0, LabelStyle: (FontSize: 10, TextColor: #062a06, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #5fb05f, LabelStyle: (FontSize: 10, TextColor: #062a06, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  b.appendInline((String) null, "Group #SkyySet {{ Anchor: (Width: 520, Height: 330); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyySet", "Group {{ Anchor: (Height: 2); Background: #7fe07f; }}");
  b.appendInline("#SkyySet", "Label {{ Anchor: (Height: 26); Text: \\"" + {PKG}.Widgets.label(this.wid) + " settings\\"; Style: (FontSize: 15, RenderBold: true, TextColor: #eaffea, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  if (l == null) return;
  b.appendInline("#SkyySet", "Group #SkyySetRow1 {{ Anchor: (Height: 32); LayoutMode: Left; Padding: (Top: 6); }}");
  b.appendInline("#SkyySetRow1", "Label {{ Anchor: (Width: 120, Height: 24); Text: \\"Visible\\"; Style: (FontSize: 12, TextColor: #ffffff, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySetRow1", "TextButton #SkyySetOn {{ Anchor: (Width: 60, Height: 24); Text: \\"ON\\"; " + (l.en ? on : bs) + " }}");
  b.appendInline("#SkyySetRow1", "Label {{ Anchor: (Width: 4, Height: 24); Text: \\"\\"; }}");
  b.appendInline("#SkyySetRow1", "TextButton #SkyySetOff {{ Anchor: (Width: 60, Height: 24); Text: \\"OFF\\"; " + (l.en ? bs : on) + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyySetOn", {EVD}.of("a", "on"));
  ev.addEventBinding({BT}.Activating, "#SkyySetOff", {EVD}.of("a", "off"));
  b.appendInline("#SkyySet", "Group #SkyySetRow2 {{ Anchor: (Height: 32); LayoutMode: Left; Padding: (Top: 6); }}");
  b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 120, Height: 24); Text: \\"Background\\"; Style: (FontSize: 12, TextColor: #ffffff, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySetRow2", "TextButton #SkyySetBgOn {{ Anchor: (Width: 60, Height: 24); Text: \\"ON\\"; " + (l.bg ? on : bs) + " }}");
  b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 4, Height: 24); Text: \\"\\"; }}");
  b.appendInline("#SkyySetRow2", "TextButton #SkyySetBgOff {{ Anchor: (Width: 60, Height: 24); Text: \\"OFF\\"; " + (l.bg ? bs : on) + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyySetBgOn", {EVD}.of("a", "bgon"));
  ev.addEventBinding({BT}.Activating, "#SkyySetBgOff", {EVD}.of("a", "bgoff"));
  b.appendInline("#SkyySet", "Group #SkyySetRow3 {{ Anchor: (Height: 32); LayoutMode: Left; Padding: (Top: 6); }}");
  b.appendInline("#SkyySetRow3", "Label {{ Anchor: (Width: 120, Height: 24); Text: \\"Size " + l.scale + "%\\"; Style: (FontSize: 12, TextColor: #ffffff, VerticalAlignment: Center); }}");
  int[] sizes = new int[] {{ 50, 75, 100, 125, 150, 200 }};
  for (int i = 0; i < sizes.length; i++) {{
    b.appendInline("#SkyySetRow3", "TextButton #SkyySetSz" + sizes[i] + " {{ Anchor: (Width: 52, Height: 24); Text: \\"" + sizes[i] + "%\\"; " + (l.scale == sizes[i] ? on : bs) + " }}");
    b.appendInline("#SkyySetRow3", "Label {{ Anchor: (Width: 4, Height: 24); Text: \\"\\"; }}");
    ev.addEventBinding({BT}.Activating, "#SkyySetSz" + sizes[i], {EVD}.of("a", "sz:" + sizes[i]));
  }}
  b.appendInline("#SkyySet", "Group #SkyySetRow4 {{ Anchor: (Height: 32); LayoutMode: Left; Padding: (Top: 6); }}");
  b.appendInline("#SkyySetRow4", "Label {{ Anchor: (Width: 120, Height: 24); Text: \\"Snap to\\"; Style: (FontSize: 12, TextColor: #ffffff, VerticalAlignment: Center); }}");
  String[] an = new String[] {{ "tl", "t", "tr", "l", "c", "r", "bl", "b", "br" }};
  for (int i = 0; i < an.length; i++) {{
    b.appendInline("#SkyySetRow4", "TextButton #SkyySetAn" + an[i].toUpperCase() + " {{ Anchor: (Width: 36, Height: 24); Text: \\"" + an[i].toUpperCase() + "\\"; " + (l.anchor.equals(an[i]) ? on : bs) + " }}");
    b.appendInline("#SkyySetRow4", "Label {{ Anchor: (Width: 3, Height: 24); Text: \\"\\"; }}");
    ev.addEventBinding({BT}.Activating, "#SkyySetAn" + an[i].toUpperCase(), {EVD}.of("a", "an:" + an[i]));
  }}
  b.appendInline("#SkyySet", "Group #SkyySetRow5 {{ Anchor: (Height: 36); LayoutMode: Left; Padding: (Top: 12); }}");
  b.appendInline("#SkyySetRow5", "TextButton #SkyySetBack {{ Anchor: (Width: 140, Height: 26); Text: \\"Back to editor\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyySetBack", {EVD}.of("a", "back"));
}}""", sett))
sett.addMethod(CtNewMethod.make("""
public static int jsonAfter(String data, String key) {
  int p = data.indexOf("\\"" + key);
  if (p < 0) return -1;
  int i = p + 1 + key.length(); int j = i;
  while (j < data.length() && Character.isDigit(data.charAt(j))) j++;
  try { return Integer.parseInt(data.substring(i, j)); } catch (Throwable t) { return -1; }
}""", sett))
sett.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    {PKG}.WLayout l = ({PKG}.WLayout) {PKG}.LayoutStore.get(u).get(this.wid);
    if (l == null) return;
    if (data.indexOf("\\"back\\"") >= 0) {{
      {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
      if (player != null) {{ {PKG}.EditorPage ep = new {PKG}.EditorPage(this.playerRef, this.plugin); ep.sel = this.wid; player.getPageManager().openCustomPage(ref, st, ep); }}
      return;
    }}
    if (data.indexOf("\\"on\\"") >= 0) l.en = true;
    else if (data.indexOf("\\"off\\"") >= 0) l.en = false;
    else if (data.indexOf("\\"bgon\\"") >= 0) l.bg = true;
    else if (data.indexOf("\\"bgoff\\"") >= 0) l.bg = false;
    else if (data.indexOf("\\"sz:") >= 0) {{ int v = jsonAfter(data, "sz:"); if (v >= 50 && v <= 200) l.scale = v; }}
    else if (data.indexOf("\\"an:") >= 0) {{ int p = data.indexOf("\\"an:") + 4; int q = data.indexOf('\\"', p); String a = data.substring(p, q); if ({PKG}.WLayout.validAnchor(a)) {{ l.anchor = a; l.dx = 8; l.dy = 8; }} }}
    else return;
    {PKG}.LayoutStore.save(u); plugin.rebuildFor(u); rebuild();
  }} catch (Throwable t) {{ {PKG}.LayoutStore.debug("settings event failed: " + t); }}
}}""", sett))


# ================= WidgetsPage (all widgets: ON/OFF + Settings) =================

wpg.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  java.util.Map m = {PKG}.LayoutStore.get(u);
  String[] ids = {PKG}.Widgets.IDS;
  String bs = "Style: TextButtonStyle(Default: (Background: #1d3a5f, LabelStyle: (FontSize: 10, TextColor: #dceeff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #2f5a8f, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #0f2038, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  String on = "Style: TextButtonStyle(Default: (Background: #7fe07f, LabelStyle: (FontSize: 10, TextColor: #062a06, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #a0f0a0, LabelStyle: (FontSize: 10, TextColor: #062a06, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #5fb05f, LabelStyle: (FontSize: 10, TextColor: #062a06, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  b.appendInline((String) null, "Group #SkyyWidgets {{ Anchor: (Width: 520, Height: " + (90 + 36 * ids.length) + "); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyyWidgets", "Group {{ Anchor: (Height: 2); Background: #7fe07f; }}");
  b.appendInline("#SkyyWidgets", "Label {{ Anchor: (Height: 26); Text: \\"Widgets\\"; Style: (FontSize: 15, RenderBold: true, TextColor: #eaffea, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  for (int i = 0; i < ids.length; i++) {{
    {PKG}.WLayout l = ({PKG}.WLayout) m.get(ids[i]);
    boolean en = l != null && l.en;
    b.appendInline("#SkyyWidgets", "Group #SkyyWRow" + ids[i] + " {{ Anchor: (Height: 36); LayoutMode: Left; Padding: (Top: 8); }}");
    b.appendInline("#SkyyWRow" + ids[i], "Label {{ Anchor: (Width: 200, Height: 26); Text: \\"" + {PKG}.Widgets.label(ids[i]) + "\\"; Style: (FontSize: 12, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyWRow" + ids[i], "TextButton #SkyyWOn" + ids[i] + " {{ Anchor: (Width: 60, Height: 26); Text: \\"ON\\"; " + (en ? on : bs) + " }}");
    b.appendInline("#SkyyWRow" + ids[i], "Label {{ Anchor: (Width: 4, Height: 26); Text: \\"\\"; }}");
    b.appendInline("#SkyyWRow" + ids[i], "TextButton #SkyyWOff" + ids[i] + " {{ Anchor: (Width: 60, Height: 26); Text: \\"OFF\\"; " + (en ? bs : on) + " }}");
    b.appendInline("#SkyyWRow" + ids[i], "Label {{ Anchor: (Width: 12, Height: 26); Text: \\"\\"; }}");
    b.appendInline("#SkyyWRow" + ids[i], "TextButton #SkyyWCog" + ids[i] + " {{ Anchor: (Width: 90, Height: 26); Text: \\"Settings\\"; " + bs + " }}");
    ev.addEventBinding({BT}.Activating, "#SkyyWOn" + ids[i], {EVD}.of("a", "on:" + ids[i]));
    ev.addEventBinding({BT}.Activating, "#SkyyWOff" + ids[i], {EVD}.of("a", "off:" + ids[i]));
    ev.addEventBinding({BT}.Activating, "#SkyyWCog" + ids[i], {EVD}.of("a", "cog:" + ids[i]));
  }}
  b.appendInline("#SkyyWidgets", "Group #SkyyWFoot {{ Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 12); }}");
  b.appendInline("#SkyyWFoot", "TextButton #SkyyWBack {{ Anchor: (Width: 140, Height: 26); Text: \\"Back to editor\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyWBack", {EVD}.of("a", "back"));
}}""", wpg))
wpg.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    java.util.Map m = {PKG}.LayoutStore.get(u);
    String[] ids = {PKG}.Widgets.IDS;
    {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (data.indexOf("\\"back\\"") >= 0) {{ if (player != null) player.getPageManager().openCustomPage(ref, st, new {PKG}.EditorPage(this.playerRef, this.plugin)); return; }}
    for (int i = 0; i < ids.length; i++) {{
      {PKG}.WLayout l = ({PKG}.WLayout) m.get(ids[i]);
      if (l == null) continue;
      if (data.indexOf("on:" + ids[i] + "\\"") >= 0) {{ l.en = true; {PKG}.LayoutStore.save(u); plugin.rebuildFor(u); rebuild(); return; }}
      if (data.indexOf("off:" + ids[i] + "\\"") >= 0) {{ l.en = false; {PKG}.LayoutStore.save(u); plugin.rebuildFor(u); rebuild(); return; }}
      if (data.indexOf("cog:" + ids[i] + "\\"") >= 0) {{ if (player != null) player.getPageManager().openCustomPage(ref, st, new {PKG}.SettingsPage(this.playerRef, this.plugin, ids[i])); return; }}
    }}
  }} catch (Throwable t) {{ {PKG}.LayoutStore.debug("widgets page event failed: " + t); }}
}}""", wpg))

# ================= HudCmd =================
cmd.addField(CtField.make(f"public {PKG}.SkyyHudPlugin plugin;", cmd))
cmd.addField(CtField.make(f"public {OPT} actionArg;", cmd))
cmd.addField(CtField.make(f"public {OPT} codeArg;", cmd))
cmd.addConstructor(CtNewConstructor.make(f"""
public HudCmd({PKG}.SkyyHudPlugin p) {{
  super("skyyhud", "SkyyHud: open the HUD editor, or export/import/reset your layout");
  addAliases(new String[] {{ "shud" }});
  this.plugin = p;
  this.actionArg = withOptionalArg("action", "export | import | reset | profile (omit to open the editor)", {ARG}.STRING);
  this.codeArg = withOptionalArg("code", "layout code (import) or: save|load|delete <name> | list (profile)", {ARG}.GREEDY_STRING);
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
    if (action.equals("profile")) {{
      String rest = ctx.provided(this.codeArg) ? String.valueOf(ctx.get(this.codeArg)).trim() : "";
      String sub = rest; String name = "";
      int sp = rest.indexOf(' ');
      if (sp > 0) {{ sub = rest.substring(0, sp); name = rest.substring(sp + 1).trim(); }}
      sub = sub.toLowerCase();
      if (sub.equals("list")) {{ String lst2 = {PKG}.LayoutStore.profileList(u); pr.sendMessage({MSG}.raw("[SkyyHud] profiles: " + (lst2.length() == 0 ? "(none)" : lst2))); return; }}
      if (sub.equals("save")) {{ pr.sendMessage({MSG}.raw({PKG}.LayoutStore.profileSave(u, name) ? "[SkyyHud] saved profile " + {PKG}.LayoutStore.cleanName(name) : "[SkyyHud] usage: /skyyhud profile save <name>")); return; }}
      if (sub.equals("load")) {{ int n = {PKG}.LayoutStore.profileLoad(u, name); if (n > 0) this.plugin.rebuildFor(u); pr.sendMessage({MSG}.raw(n >= 0 ? "[SkyyHud] loaded profile " + {PKG}.LayoutStore.cleanName(name) : "[SkyyHud] no such profile")); return; }}
      if (sub.equals("delete")) {{ pr.sendMessage({MSG}.raw({PKG}.LayoutStore.profileDelete(u, name) ? "[SkyyHud] deleted profile" : "[SkyyHud] no such profile")); return; }}
      pr.sendMessage({MSG}.raw("[SkyyHud] usage: /skyyhud profile save|load|delete <name> | list")); return;
    }}
    if (action.length() > 0) {{ pr.sendMessage({MSG}.raw("[SkyyHud] unknown action '" + action + "' (export | import <code> | reset | profile ...)")); return; }}
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
  {PKG}.LayoutStore.LOG = getLogger();
  {PKG}.LayoutStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyHud").resolve("layouts");
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

for c in (wl, lst, wid, hudc, page, sett, wpg, cmd, tick, att, rdy, pl):
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
