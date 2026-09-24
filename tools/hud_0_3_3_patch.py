"""Derive SkyyHud/build_skyyhud_0.3.3.py from 0.3.2.
0.3.3: green frame marks the screen edge on the canvas; the editor canvas shows LIVE WIDGET PREVIEWS (same text, font, colour and background as the HUD, at the canvas' 2/3 scale)
under each drag handle instead of random item icons. The drag handle is one neutral icon for every widget (dragging only works on
ItemGrid slots, so a handle must stay). Overlay order is switchable because the engine's hit-testing is unknown:
  /skyyhud preview back   (default) previews are drawn BEHIND the grid (safe for dragging; may be hidden by slot backgrounds)
  /skyyhud preview front  previews drawn in front (always visible; test whether dragging still works)
  /skyyhud preview off
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.2.py")
dst = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.3.py")
s = open(src, encoding="utf8").read()

def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:90]
    s = s.replace(old, new, count)

rep('VERSION = "0.3.2"', 'VERSION = "0.3.3"')

# one neutral drag handle for every widget
start = s.index('public static String chipItem(String id) {')
end = s.index('}""", wid))', start) + len('}""", wid))')
s = s[:start] + '''public static String chipItem(String id) {
  return "Ingredient_Crystal_White";
}""", wid))''' + s[end:]

# preview mode field + preview builder on the editor page (declared before build())
rep('page = pool.makeClass(PKG + ".EditorPage", pool.get(PAGE))',
    'page = pool.makeClass(PKG + ".EditorPage", pool.get(PAGE))\npage.addField(CtField.make(\'public static volatile String PREVIEW = "back";\', page))')

rep('''  b.appendInline("#SkyyEditor", "Label {{ Anchor: (Height: 14); Text: \\\\"Drag a widget to move it. Click one to select it. The canvas is your screen at 2/3 scale.\\\\"; Style: (FontSize: 10, TextColor: #9fb8d0, HorizontalAlignment: Center); }}");''',
    '''  b.appendInline("#SkyyEditor", "Label {{ Anchor: (Height: 14); Text: \\\\"Drag a handle to move its widget - the text under it is a live preview. Click a handle to select it. The canvas is your screen at 2/3 scale.\\\\"; Style: (FontSize: 10, TextColor: #9fb8d0, HorizontalAlignment: Center); }}");''')

old_block_start = s.index('  b.appendInline("#SkyyECanvasWrap", "ItemGrid #SkyyECanvas')
old_block_end = s.index('  b.set("#SkyyECanvas.Slots", slots);') + len('  b.set("#SkyyECanvas.Slots", slots);')
new_block = '''  this.cellWidget = new String[144];
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
  String grid = "ItemGrid #SkyyECanvas {{ Anchor: (Horizontal: 0, Top: 3, Width: 1280, Height: 720); SlotsPerRow: 16; AreItemsDraggable: true; Style: (SlotSize: 80, SlotIconSize: 56, SlotSpacing: 0); }}";
  String mode = PREVIEW == null ? "back" : PREVIEW;
  if (mode.equals("front")) {{ b.appendInline("#SkyyECanvasWrap", grid); appendPreviews(b, m); }}
  else {{ if (!mode.equals("off")) appendPreviews(b, m); b.appendInline("#SkyyECanvasWrap", grid); }}
  b.appendInline("#SkyyECanvasWrap", "Group #SkyyEBorder {{ Anchor: (Horizontal: 0, Top: 3, Width: 1280, Height: 720); }}");
  b.appendInline("#SkyyEBorder", "Group {{ Anchor: (Left: 0, Top: 0, Width: 1280, Height: 3); Background: #7fe07f; }}");
  b.appendInline("#SkyyEBorder", "Group {{ Anchor: (Left: 0, Top: 717, Width: 1280, Height: 3); Background: #7fe07f; }}");
  b.appendInline("#SkyyEBorder", "Group {{ Anchor: (Left: 0, Top: 0, Width: 3, Height: 720); Background: #7fe07f; }}");
  b.appendInline("#SkyyEBorder", "Group {{ Anchor: (Left: 1277, Top: 0, Width: 3, Height: 720); Background: #7fe07f; }}");
  b.appendInline("#SkyyEBorder", "Label {{ Anchor: (Left: 8, Top: 4, Width: 400, Height: 14); Text: \\\\"screen edge\\\\"; Style: (FontSize: 9, TextColor: #7fe07f); }}");
  b.set("#SkyyECanvas.Slots", slots);'''
s = s[:old_block_start] + new_block + s[old_block_end:]

# appendPreviews method, inserted right before the editor build() method
build_anchor = s.index('page.addMethod(CtNewMethod.make(f"""\npublic void build(')
preview_method = '''page.addMethod(CtNewMethod.make(f"""
public static String esc(String t) {{
  if (t == null) return "";
  return t.replace('\\\\\\\\', ' ').replace('"', ' ').replace('{{', '(').replace('}}', ')').replace(';', ',');
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void appendPreviews({UCB} b, java.util.Map m) {{
  b.appendInline("#SkyyECanvasWrap", "Group #SkyyEPrev {{ Anchor: (Horizontal: 0, Top: 3, Width: 1280, Height: 720); }}");
  long now = System.currentTimeMillis();
  for (int cell = 0; cell < 144; cell++) {{
    String id = this.cellWidget[cell];
    if (id == null) continue;
    {PKG}.WLayout l = ({PKG}.WLayout) m.get(id);
    if (l == null) continue;
    int col = cell % 16; int row = cell / 16;
    int w = 120 * l.scale / 100; int h = 17 * l.scale / 100; if (h < 12) h = 12;
    int fs = 8 * l.scale / 100; if (fs < 6) fs = 6;
    int left = col * 80; if (left + w > 1280) left = 1280 - w;
    int top = row * 80 + 64; if (top + h > 720) top = 720 - h;
    String text;
    try {{ text = {PKG}.Widgets.text(id, this.playerRef, now); }} catch (Throwable t) {{ text = {PKG}.Widgets.label(id); }}
    b.appendInline("#SkyyEPrev", "Group #SkyyEPv" + id + " {{ Anchor: (Left: " + left + ", Top: " + top + ", Width: " + w + ", Height: " + h + "); " + (l.bg ? "Background: #0b1524(0.72); " : "") + "Label {{ Anchor: (Full: 0); Text: \\\\"" + esc(text) + "\\\\"; Style: (FontSize: " + fs + ", RenderBold: true, TextColor: #eaf6ff, HorizontalAlignment: Center, VerticalAlignment: Center); }} }}");
  }}
}}""", page))
'''
s = s[:build_anchor] + preview_method + s[build_anchor:]

# /skyyhud preview front|back|off
rep('''    if (action.equals("profile")) {{''', '''    if (action.equals("preview")) {{
      String v = ctx.provided(this.codeArg) ? String.valueOf(ctx.get(this.codeArg)).trim().toLowerCase() : "";
      if (!v.equals("front") && !v.equals("back") && !v.equals("off")) {{ pr.sendMessage({MSG}.raw("[SkyyHud] editor previews are '" + {PKG}.EditorPage.PREVIEW + "'. /skyyhud preview front | back | off")); return; }}
      {PKG}.EditorPage.PREVIEW = v;
      pr.sendMessage({MSG}.raw("[SkyyHud] editor previews: " + v + " (reopen the editor)"));
      return;
    }}
    if (action.equals("profile")) {{''')
rep('"export | import | reset | profile (omit to open the editor)"', '"export | import | reset | profile | preview (omit to open the editor)"')

open(dst, "w", encoding="utf8").write(s)
print("wrote", dst)
