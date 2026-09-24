# one-off (2026-09-23): derive SkyyHud/build_skyyhud_0.3.0.py from 0.2.9 - LUNAR-STYLE EDITOR v2.
# Canvas = inline `ItemGrid #SkyyECanvas` (16 x 9 cells = a 1080p screen at 1/3 scale, SlotSize 40), AreItemsDraggable, slots
# pushed as server `ItemGridSlot`s (one chip per ON widget, empty ItemGridSlot elsewhere). `Dropped` on the grid moves the
# widget (SourceSlotId -> widget, SlotIndex -> cell -> anchor + offsets); `SlotClicking` selects a widget -> a control bar
# with X (hide), cog (settings page), < > ^ v nudge, Size-/Size+. Hidden widgets listed as buttons to turn on.
# Settings page: On/Off, size presets, anchor presets, background on/off. Profiles: /skyyhud profile save|load|list|delete <name>.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.2.9.py")
dst = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.0.py")
s = open(src, encoding="utf8").read()
s = s.replace('VERSION = "0.2.9"', 'VERSION = "0.3.0"').replace("build_skyyhud_0.2.9.py", "build_skyyhud_0.3.0.py")

def replace_section(text, start_marker, end_marker, new_body):
    a = text.index(start_marker); b = text.index(end_marker, a)
    return text[:a] + new_body + text[b:]

# ---- constants
s = s.replace('VAL = "com.hypixel.hytale.server.core.ui.Value"',
'''VAL = "com.hypixel.hytale.server.core.ui.Value"
IGS = "com.hypixel.hytale.server.core.ui.ItemGridSlot"
IS  = "com.hypixel.hytale.server.core.inventory.ItemStack"''')
s = s.replace('("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "openCustomPage")):\n    B.probe(pool, c, m)',
              '("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "openCustomPage"), (IGS, "setItemStack"), (IGS, "setName")):\n    B.probe(pool, c, m)')
s = s.replace('page = pool.makeClass(PKG + ".EditorPage", pool.get(PAGE))',
              'page = pool.makeClass(PKG + ".EditorPage", pool.get(PAGE))\nsett = pool.makeClass(PKG + ".SettingsPage", pool.get(PAGE))')

# ---- WLayout: background flag (bg) serialised as 6th field, default on
s = s.replace('wl.addField(CtField.make(f, wl))', 'wl.addField(CtField.make(f, wl))\nwl.addField(CtField.make("public boolean bg;", wl))', 1)
s = s.replace('''public WLayout(boolean en, String anchor, int dx, int dy, int scale) {
  this.en = en; this.anchor = anchor; this.dx = dx; this.dy = dy; this.scale = scale;
}''', '''public WLayout(boolean en, String anchor, int dx, int dy, int scale) {
  this.en = en; this.anchor = anchor; this.dx = dx; this.dy = dy; this.scale = scale; this.bg = true;
}''')
s = s.replace('public String ser() { return (en ? "1" : "0") + "," + anchor + "," + dx + "," + dy + "," + scale; }',
              'public String ser() { return (en ? "1" : "0") + "," + anchor + "," + dx + "," + dy + "," + scale + "," + (bg ? "1" : "0"); }')
s = s.replace('''    return new {PKG}.WLayout("1".equals(p[0].trim()), a, dx, dy, sc);
  }} catch (Throwable t) {{ return def; }}''', '''    {PKG}.WLayout w = new {PKG}.WLayout("1".equals(p[0].trim()), a, dx, dy, sc);
    if (p.length > 5) w.bg = "1".equals(p[5].trim());
    return w;
  }} catch (Throwable t) {{ return def; }}''')
# widgetSrc honours bg
s = s.replace('return "Group #SkyyW" + id + " {{ Anchor: " + anchorSrc(l) + "; Background: #0b1524(0.72); Label #SkyyW" + id + "Txt',
              'return "Group #SkyyW" + id + " {{ Anchor: " + anchorSrc(l) + "; " + (l.bg ? "Background: #0b1524(0.72); " : "") + "Label #SkyyW" + id + "Txt')
assert '(l.bg ? "Background' in s, "widgetSrc bg"

# ---- Widgets: chip item per widget + cell <-> layout maths (1080p reference, 16x9 cells of 120x120)
s = s.replace('# ================= LayoutStore =================', '''wid.addMethod(CtNewMethod.make("""
public static String chipItem(String id) {
  if (id.equals("Coords")) return "Ingredient_Crystal_White";
  if (id.equals("Zone")) return "Weapon_Shield_Orbis_Knight";
  if (id.equals("Gclock")) return "Potion_Health_Lesser";
  if (id.equals("Rclock")) return "Ingredient_Fire_Essence";
  if (id.equals("Day")) return "Ingredient_Life_Essence";
  if (id.equals("Session")) return "Weapon_Staff_Bronze";
  if (id.equals("Online")) return "Weapon_Shortbow_Crude";
  if (id.equals("Coins")) return "Ingredient_Bar_Copper";
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
  String hz = col <= 5 ? "l" : (col >= 10 ? "r" : "c");
  String vt = row <= 2 ? "t" : (row >= 6 ? "b" : "c");
  if (hz.equals("l")) l.dx = x; else if (hz.equals("r")) l.dx = 1920 - w - x; else l.dx = x + w / 2 - 960;
  if (vt.equals("t")) l.dy = y; else if (vt.equals("b")) l.dy = 1080 - h - y; else l.dy = y + h / 2 - 540;
  if (vt.equals("t")) l.anchor = hz.equals("l") ? "tl" : (hz.equals("r") ? "tr" : "t");
  else if (vt.equals("b")) l.anchor = hz.equals("l") ? "bl" : (hz.equals("r") ? "br" : "b");
  else l.anchor = hz.equals("l") ? "l" : (hz.equals("r") ? "r" : "c");
  if (l.dx < 0 && !hz.equals("c")) l.dx = 0;
  if (l.dy < 0 && !vt.equals("c")) l.dy = 0;
}}""", wid))

# ================= LayoutStore =================''', 1)

# ---- LayoutStore: profiles
s = s.replace('''# ================= HudMain =================''', '''lst.addMethod(CtNewMethod.make(f"""
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

# ================= HudMain =================''', 1)

# ---- EditorPage v2 + SettingsPage
editor = r'''# ================= EditorPage v2 (Lunar-style: drag canvas + selected-widget bar) =================
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
  String bs = "{BTN}";
  b.appendInline((String) null, "Group #SkyyEditor {{ Anchor: (Width: 700, Height: 560); Background: #0b1524(0.94); Padding: (Horizontal: 14, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyyEditor", "Group {{ Anchor: (Height: 2); Background: #7fe07f; }}");
  b.appendInline("#SkyyEditor", "Label {{ Anchor: (Height: 24); Text: \\"SkyyHud Editor\\"; Style: (FontSize: 15, RenderBold: true, TextColor: #eaffea, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyEditor", "Label {{ Anchor: (Height: 14); Text: \\"Drag a widget to move it. Click one to select it. The canvas is your screen at 1/3 scale.\\"; Style: (FontSize: 10, TextColor: #9fb8d0, HorizontalAlignment: Center); }}");
  b.appendInline("#SkyyEditor", "Group #SkyyECanvasWrap {{ Anchor: (Height: 366); }}");
  b.appendInline("#SkyyECanvasWrap", "ItemGrid #SkyyECanvas {{ Anchor: (Horizontal: 0, Top: 3, Width: 640, Height: 360); SlotsPerRow: 16; AreItemsDraggable: true; Style: (SlotSize: 40, SlotIconSize: 30, SlotSpacing: 0); }}");
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
  b.appendInline("#SkyyEditor", "Label #SkyyEInfo {{ Anchor: (Height: 18); Text: \\"" + selInfo().replace('\\"', ' ') + "\\"; Style: (FontSize: 11, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyEditor", "Group #SkyyEBar {{ Anchor: (Height: 30); LayoutMode: Left; Padding: (Top: 4); }}");
  if (this.sel != null) {{
    String[] acts = new String[] {{ "Lt", "Rt", "Up", "Dn", "Sm", "Sp", "Hide", "Cog" }};
    String[] labels = new String[] {{ "<", ">", "^", "v", "Size-", "Size+", "X hide", "Settings" }};
    for (int a = 0; a < acts.length; a++) {{
      int w = a < 4 ? 34 : (a < 6 ? 52 : 72);
      b.appendInline("#SkyyEBar", "TextButton #SkyyEB" + acts[a] + " {{ Anchor: (Width: " + w + ", Height: 24); Text: \\"" + labels[a] + "\\"; " + bs + " }}");
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
  b.appendInline("#SkyyEditor", "Label {{ Anchor: (Height: 14); Text: \\"" + (this.info == null ? "" : this.info.replace('\\"', ' ')) + "   /skyyhud export | import | reset | profile save|load|list <name>\\"; Style: (FontSize: 9, TextColor: #6f8498, HorizontalAlignment: Center); }}");
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
sett.addField(CtField.make(f"public {PKG}.SkyyHudPlugin plugin;", sett))
sett.addField(CtField.make("public String wid;", sett))
sett.addConstructor(CtNewConstructor.make(f"""
public SettingsPage({PR} pr, {PKG}.SkyyHudPlugin plugin, String wid) {{
  super(pr, {LIFE}.CanDismiss);
  this.plugin = plugin;
  this.wid = wid;
}}""", sett))
sett.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  {PKG}.WLayout l = ({PKG}.WLayout) {PKG}.LayoutStore.get(u).get(this.wid);
  String bs = "{BTN}";
  String on = "{TABON}";
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
sett.addMethod(CtNewMethod.make("""
public static int jsonAfter(String data, String key) {
  int p = data.indexOf("\\"" + key);
  if (p < 0) return -1;
  int i = p + 1 + key.length(); int j = i;
  while (j < data.length() && Character.isDigit(data.charAt(j))) j++;
  try { return Integer.parseInt(data.substring(i, j)); } catch (Throwable t) { return -1; }
}""", sett))

'''
BTN = 'Style: TextButtonStyle(Default: (Background: #1d3a5f, LabelStyle: (FontSize: 10, TextColor: #dceeff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #2f5a8f, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #0f2038, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));'
TABON = 'Style: TextButtonStyle(Default: (Background: #7fe07f, LabelStyle: (FontSize: 10, TextColor: #062a06, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #a0f0a0, LabelStyle: (FontSize: 10, TextColor: #062a06, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #5fb05f, LabelStyle: (FontSize: 10, TextColor: #062a06, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));'
editor = editor.replace("{BTN}", BTN).replace("{TABON}", TABON)
s = replace_section(s, "# ================= EditorPage =================", "# ================= HudCmd =================", editor)

# ---- LayoutStore.debug -> server log (via plugin logger)
s = s.replace('lst.addField(CtField.make("public static java.nio.file.Path DIR;", lst))',
'''lst.addField(CtField.make("public static java.nio.file.Path DIR;", lst))
lst.addField(CtField.make("public static com.hypixel.hytale.logger.HytaleLogger LOG;", lst))
lst.addMethod(CtNewMethod.make("""
public static void debug(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyHud] " + msg); } catch (Throwable t) { }
}""", lst))''')
s = s.replace('  {PKG}.LayoutStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyHud").resolve("layouts");',
              '  {PKG}.LayoutStore.LOG = getLogger();\n  {PKG}.LayoutStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyHud").resolve("layouts");')

# ---- HudCmd: profile subcommands
old = '''    if (action.length() > 0) {{ pr.sendMessage({MSG}.raw("[SkyyHud] unknown action '" + action + "' (export | import <code> | reset)")); return; }}'''
assert old in s, "hudcmd unknown action"
s = s.replace(old, '''    if (action.equals("profile")) {{
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
    if (action.length() > 0) {{ pr.sendMessage({MSG}.raw("[SkyyHud] unknown action '" + action + "' (export | import <code> | reset | profile ...)")); return; }}''')
s = s.replace('this.actionArg = withOptionalArg("action", "export | import | reset (omit to open the editor)", {ARG}.STRING);',
              'this.actionArg = withOptionalArg("action", "export | import | reset | profile (omit to open the editor)", {ARG}.STRING);')
s = s.replace('this.codeArg = withOptionalArg("code", "layout code (for import)", {ARG}.GREEDY_STRING);',
              'this.codeArg = withOptionalArg("code", "layout code (import) or: save|load|delete <name> | list (profile)", {ARG}.GREEDY_STRING);')

# ---- class list
s = s.replace('for c in (wl, lst, wid, hudc, page, cmd, tick, att, rdy, pl):', 'for c in (wl, lst, wid, hudc, page, sett, cmd, tick, att, rdy, pl):')
assert "sett, cmd" in s, "class list"
open(dst, "w", encoding="utf8").write(s)
print("wrote", dst)
