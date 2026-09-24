# one-off (2026-09-23): derive SkyyHud/build_skyyhud_0.3.1.py from 0.3.0
#  - drops snap to the four CORNER anchors only, offsets clamped >= 0 (a middle anchor with a negative offset rendered as a
#    full-height bar - Skyy's "clock covered the whole side")
#  - editor at 2/3 scale: 16x9 canvas of 80 px cells = 1280x720; page 1330x930
#  - "Widgets" button bottom-right -> WidgetsPage (every widget: ON/OFF + Settings), Back to editor
#  - matching vanilla item icons per widget + a legend line under the canvas (icon name -> live text)
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.0.py")
dst = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.1.py")
s = open(src, encoding="utf8").read()
s = s.replace('VERSION = "0.3.0"', 'VERSION = "0.3.1"').replace("build_skyyhud_0.3.0.py", "build_skyyhud_0.3.1.py")

def rep(a, b, count=1):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, count)

# --- corner-only placement
rep('''  String hz = col <= 5 ? "l" : (col >= 10 ? "r" : "c");
  String vt = row <= 2 ? "t" : (row >= 6 ? "b" : "c");
  if (hz.equals("l")) l.dx = x; else if (hz.equals("r")) l.dx = 1920 - w - x; else l.dx = x + w / 2 - 960;
  if (vt.equals("t")) l.dy = y; else if (vt.equals("b")) l.dy = 1080 - h - y; else l.dy = y + h / 2 - 540;
  if (vt.equals("t")) l.anchor = hz.equals("l") ? "tl" : (hz.equals("r") ? "tr" : "t");
  else if (vt.equals("b")) l.anchor = hz.equals("l") ? "bl" : (hz.equals("r") ? "br" : "b");
  else l.anchor = hz.equals("l") ? "l" : (hz.equals("r") ? "r" : "c");
  if (l.dx < 0 && !hz.equals("c")) l.dx = 0;
  if (l.dy < 0 && !vt.equals("c")) l.dy = 0;''',
'''  boolean left = col <= 7; boolean top = row <= 4;
  l.dx = left ? x : 1920 - w - x;
  l.dy = top ? y : 1080 - h - y;
  l.anchor = top ? (left ? "tl" : "tr") : (left ? "bl" : "br");
  if (l.dx < 0) l.dx = 0;
  if (l.dy < 0) l.dy = 0;''')

# --- icons
rep('''  if (id.equals("Coords")) return "Ingredient_Crystal_White";
  if (id.equals("Zone")) return "Weapon_Shield_Orbis_Knight";
  if (id.equals("Gclock")) return "Potion_Health_Lesser";
  if (id.equals("Rclock")) return "Ingredient_Fire_Essence";
  if (id.equals("Day")) return "Ingredient_Life_Essence";
  if (id.equals("Session")) return "Weapon_Staff_Bronze";
  if (id.equals("Online")) return "Weapon_Shortbow_Crude";
  if (id.equals("Coins")) return "Ingredient_Bar_Copper";''',
'''  if (id.equals("Coords")) return "Tool_Map";
  if (id.equals("Zone")) return "Furniture_Crude_Sign";
  if (id.equals("Gclock")) return "Deco_Lantern";
  if (id.equals("Rclock")) return "Deco_Scroll";
  if (id.equals("Day")) return "Plant_Seeds_Sunflower";
  if (id.equals("Session")) return "Furniture_Crude_Torch";
  if (id.equals("Online")) return "Furniture_Flag_Orange";
  if (id.equals("Coins")) return "Ingredient_Bar_Gold";''')

# --- editor layout at 2/3 scale + legend + Widgets button
rep('b.appendInline((String) null, "Group #SkyyEditor {{ Anchor: (Width: 700, Height: 560); Background: #0b1524(0.94); Padding: (Horizontal: 14, Vertical: 10); LayoutMode: Top; }}");',
    'b.appendInline((String) null, "Group #SkyyEditor {{ Anchor: (Width: 1330, Height: 930); Background: #0b1524(0.96); Padding: (Horizontal: 20, Vertical: 10); LayoutMode: Top; }}");')
rep('Text: \\\\"Drag a widget to move it. Click one to select it. The canvas is your screen at 1/3 scale.\\\\"',
    'Text: \\\\"Drag a widget to move it. Click one to select it. The canvas is your screen at 2/3 scale.\\\\"')
rep('b.appendInline("#SkyyEditor", "Group #SkyyECanvasWrap {{ Anchor: (Height: 366); }}");',
    'b.appendInline("#SkyyEditor", "Group #SkyyECanvasWrap {{ Anchor: (Height: 726); }}");')
rep('"ItemGrid #SkyyECanvas {{ Anchor: (Horizontal: 0, Top: 3, Width: 640, Height: 360); SlotsPerRow: 16; AreItemsDraggable: true; Style: (SlotSize: 40, SlotIconSize: 30, SlotSpacing: 0); }}"',
    '"ItemGrid #SkyyECanvas {{ Anchor: (Horizontal: 0, Top: 3, Width: 1280, Height: 720); SlotsPerRow: 16; AreItemsDraggable: true; Style: (SlotSize: 80, SlotIconSize: 56, SlotSpacing: 0); }}"')
# legend under the canvas: "Name: live text" for every ON widget (uses set on a label so the text is safe)
rep('''  b.appendInline("#SkyyEditor", "Label #SkyyEInfo {{ Anchor: (Height: 18);''',
'''  {{
    StringBuilder lg = new StringBuilder();
    for (int i = 0; i < ids.length; i++) {{
      {PKG}.WLayout l2 = ({PKG}.WLayout) m.get(ids[i]);
      if (l2 == null || !l2.en) continue;
      if (lg.length() > 0) lg.append("     ");
      lg.append({PKG}.Widgets.label(ids[i])).append(" = ").append({PKG}.Widgets.text(ids[i], this.playerRef, System.currentTimeMillis()));
    }}
    b.appendInline("#SkyyEditor", "Label #SkyyELegend {{ Anchor: (Height: 16); Text: \\\\"\\\\"; Style: (FontSize: 10, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    b.set("#SkyyELegend.Text", lg.toString());
  }}
  b.appendInline("#SkyyEditor", "Label #SkyyEInfo {{ Anchor: (Height: 18);''')
# selected bar: bigger buttons
rep('      int w = a < 4 ? 34 : (a < 6 ? 52 : 72);\n      b.appendInline("#SkyyEBar", "TextButton #SkyyEB" + acts[a] + " {{ Anchor: (Width: " + w + ", Height: 24);',
    '      int w = a < 4 ? 40 : (a < 6 ? 60 : 90);\n      b.appendInline("#SkyyEBar", "TextButton #SkyyEB" + acts[a] + " {{ Anchor: (Width: " + w + ", Height: 26);')
# footer row: hint on the left, Widgets button on the right
rep('''  b.appendInline("#SkyyEditor", "Label {{ Anchor: (Height: 14); Text: \\\\"" + (this.info == null ? "" : this.info.replace('\\\\"', ' ')) + "   /skyyhud export | import | reset | profile save|load|list <name>\\\\"; Style: (FontSize: 9, TextColor: #6f8498, HorizontalAlignment: Center); }}");''',
'''  b.appendInline("#SkyyEditor", "Group #SkyyEFoot {{ Anchor: (Height: 30); LayoutMode: Left; Padding: (Top: 4); }}");
  b.appendInline("#SkyyEFoot", "Label {{ Anchor: (Width: 1100, Height: 26); Text: \\\\"" + (this.info == null ? "" : this.info.replace('\\\\"', ' ')) + "   /skyyhud export | import | reset | profile save|load|list <name>\\\\"; Style: (FontSize: 10, TextColor: #6f8498, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyEFoot", "TextButton #SkyyEWidgets {{ Anchor: (Width: 150, Height: 26); Text: \\\\"Widgets / Settings\\\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyEWidgets", {EVD}.of("a", "widgets"));''')
# handle the Widgets button (before the sel == null guard)
rep('''    if (data.indexOf("\\\\"dragcancel\\\\"") >= 0) return;''',
'''    if (data.indexOf("\\\\"dragcancel\\\\"") >= 0) return;
    if (data.indexOf("\\\\"widgets\\\\"") >= 0) {{
      {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
      if (player != null) player.getPageManager().openCustomPage(ref, st, new {PKG}.WidgetsPage(this.playerRef, this.plugin));
      return;
    }}''')

# --- WidgetsPage: list every widget with ON/OFF + Settings, Back to editor
rep('sett = pool.makeClass(PKG + ".SettingsPage", pool.get(PAGE))', 'sett = pool.makeClass(PKG + ".SettingsPage", pool.get(PAGE))\nwpg  = pool.makeClass(PKG + ".WidgetsPage", pool.get(PAGE))')
widgets_page = r'''
# ================= WidgetsPage (all widgets: ON/OFF + Settings) =================
wpg.addField(CtField.make(f"public {PKG}.SkyyHudPlugin plugin;", wpg))
wpg.addConstructor(CtNewConstructor.make(f"""
public WidgetsPage({PR} pr, {PKG}.SkyyHudPlugin plugin) {{
  super(pr, {LIFE}.CanDismiss);
  this.plugin = plugin;
}}""", wpg))
wpg.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  java.util.Map m = {PKG}.LayoutStore.get(u);
  String[] ids = {PKG}.Widgets.IDS;
  String bs = "{BTN}";
  String on = "{TABON}";
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

# ================= HudCmd ================='''
BTN = 'Style: TextButtonStyle(Default: (Background: #1d3a5f, LabelStyle: (FontSize: 10, TextColor: #dceeff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #2f5a8f, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #0f2038, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));'
TABON = 'Style: TextButtonStyle(Default: (Background: #7fe07f, LabelStyle: (FontSize: 10, TextColor: #062a06, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #a0f0a0, LabelStyle: (FontSize: 10, TextColor: #062a06, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #5fb05f, LabelStyle: (FontSize: 10, TextColor: #062a06, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));'
widgets_page = widgets_page.replace("{BTN}", BTN).replace("{TABON}", TABON)
rep("\n# ================= HudCmd =================", widgets_page)
# WidgetsPage ctor must exist before EditorPage.handleDataEvent references it: move its field+ctor up, like SettingsPage
start = s.index('wpg.addField(CtField.make(f"public {PKG}.SkyyHudPlugin plugin;", wpg))')
end = s.index('}}""", wpg))', start) + len('}}""", wpg))')
block = s[start:end]; s = s[:start] + s[end:]
s = s.replace("# SettingsPage fields + constructor first", "# WidgetsPage fields + constructor first (EditorPage references it)\n" + block + "\n\n# SettingsPage fields + constructor first", 1)
# settings "Back" should return to the widgets list if it came from there? keep: back -> editor (simple)
rep('for c in (wl, lst, wid, hudc, page, sett, cmd, tick, att, rdy, pl):', 'for c in (wl, lst, wid, hudc, page, sett, wpg, cmd, tick, att, rdy, pl):')
open(dst, "w", encoding="utf8").write(s)
print("wrote", dst)
