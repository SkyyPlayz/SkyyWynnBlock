# one-off: derive build_skyyhud_0.2.7.py from 0.2.6
#  - X-/X+/Y-/Y+ become arrow buttons (left/right/up/down) that move the widget on SCREEN regardless of anchor edge
#  - the editor gets a 1/3-scale screen preview at the top showing every ON widget where it sits; refreshed on each click
#  - centred anchors may go negative (offset from centre); edge anchors clamp at 0
p = "build_skyyhud_0.2.6.py"; s = open(p, encoding="utf8").read()
s = s.replace('VERSION = "0.2.6"', 'VERSION = "0.2.7"').replace("build_skyyhud_0.2.6.py", "build_skyyhud_0.2.7.py")

s = s.replace('ACTS = ["Tog", "Tl", "T", "Tr", "L", "C", "R", "Bl", "B2", "Br", "Xm", "Xp", "Ym", "Yp", "Sm", "Sp"]',
              'ACTS = ["Tog", "Tl", "T", "Tr", "L", "C", "R", "Bl", "B2", "Br", "Lt", "Rt", "Up", "Dn", "Sm", "Sp"]')
s = s.replace('"Xm": "X-", "Xp": "X+", "Ym": "Y-", "Yp": "Y+", "Sm": "S-", "Sp": "S+"}',
              '"Lt": "\\u2190", "Rt": "\\u2192", "Up": "\\u2191", "Dn": "\\u2193", "Sm": "S-", "Sp": "S+"}')

old_logic = '''    if (act.equals("Tog")) l.en = !l.en;
    else if (act.equals("Xm")) l.dx -= 10;
    else if (act.equals("Xp")) l.dx += 10;
    else if (act.equals("Ym")) l.dy -= 10;
    else if (act.equals("Yp")) l.dy += 10;
    else if (act.equals("Sm")) l.scale -= 10;
    else if (act.equals("Sp")) l.scale += 10;
    else if (act.equals("B2")) l.anchor = "b";
    else l.anchor = act.toLowerCase();
    if (l.dx < 0) l.dx = 0;
    if (l.dy < 0) l.dy = 0;'''
assert old_logic in s, "logic block not found"
new_logic = '''    String a = l.anchor;
    boolean rightEdge = a.equals("tr") || a.equals("r") || a.equals("br");
    boolean leftEdge = a.equals("tl") || a.equals("l") || a.equals("bl");
    boolean bottomEdge = a.equals("bl") || a.equals("b") || a.equals("br");
    boolean topEdge = a.equals("tl") || a.equals("t") || a.equals("tr");
    if (act.equals("Tog")) l.en = !l.en;
    else if (act.equals("Lt")) l.dx += rightEdge ? 10 : -10;
    else if (act.equals("Rt")) l.dx += rightEdge ? -10 : 10;
    else if (act.equals("Up")) l.dy += bottomEdge ? 10 : -10;
    else if (act.equals("Dn")) l.dy += bottomEdge ? -10 : 10;
    else if (act.equals("Sm")) l.scale -= 10;
    else if (act.equals("Sp")) l.scale += 10;
    else if (act.equals("B2")) l.anchor = "b";
    else l.anchor = act.toLowerCase();
    if ((leftEdge || rightEdge) && l.dx < 0) l.dx = 0;
    if ((topEdge || bottomEdge) && l.dy < 0) l.dy = 0;'''
s = s.replace(old_logic, new_logic)
# WLayout.parse: allow negatives for centred anchors (clamp happens in the editor instead)
s = s.replace('    if (dx < 0) dx = 0;\n    if (dy < 0) dy = 0;\n    if (sc < 50) sc = 50;', '    if (sc < 50) sc = 50;')
# after a click, rebuild the whole page so the preview refreshes (instead of only patching the info label)
old_update = '''    {PKG}.LayoutStore.save(u);
    plugin.rebuildFor(u);
    {UCB} b = new {UCB}();
    b.set("#SkyyEInfo" + wid2 + ".Text", rowInfo(wid2));
    sendUpdate(b);'''
assert old_update in s, "update block not found"
s = s.replace(old_update, '''    {PKG}.LayoutStore.save(u);
    plugin.rebuildFor(u);
    rebuild();''')

# preview panel: scaled copies of the ON widgets. Scale 1/3 of a 1920x1080 screen -> 640x360 panel.
old_hdr = r'''  b.appendInline("#SkyyEditor", "Label {{ Anchor: (Height: 14); Text: \\"On/Off - anchor (TL T TR L C R BL B BR) - nudge X/Y by 10 - scale S. Changes apply instantly. /skyyhud export | import | reset\\"; Style: (FontSize: 10, TextColor: #9fb8d0, HorizontalAlignment: Center); }}");'''
assert old_hdr in s, "header not found"
new_hdr = r'''  b.appendInline("#SkyyEditor", "Label {{ Anchor: (Height: 14); Text: \\"Preview (1/3 scale of a 1080p screen). On/Off - anchor - arrows move 10 px - S scales. /skyyhud export | import | reset\\"; Style: (FontSize: 10, TextColor: #9fb8d0, HorizontalAlignment: Center); }}");
  b.appendInline("#SkyyEditor", "Group #SkyyEPvWrap {{ Anchor: (Height: 366); }}");
  b.appendInline("#SkyyEPvWrap", "Group #SkyyEPv {{ Anchor: (Horizontal: 0, Top: 3, Width: 640, Height: 360); Background: #000000(0.45); }}");
  {{
    java.util.Map pm = {PKG}.LayoutStore.get(this.playerRef.getUuid());
    String[] pids = {PKG}.Widgets.IDS;
    for (int i = 0; i < pids.length; i++) {{
      {PKG}.WLayout pl = ({PKG}.WLayout) pm.get(pids[i]);
      if (pl == null || !pl.en) continue;
      {PKG}.WLayout sc = new {PKG}.WLayout(true, pl.anchor, pl.dx / 3, pl.dy / 3, pl.scale);
      int pw = 60 * pl.scale / 100; int ph = 9 * pl.scale / 100; if (ph < 8) ph = 8;
      String an = {PKG}.Widgets.anchorSrc(sc).replace("Width: " + (180 * pl.scale / 100), "Width: " + pw).replace("Height: " + (26 * pl.scale / 100), "Height: " + ph);
      b.appendInline("#SkyyEPv", "Group #SkyyEPv" + pids[i] + " {{ Anchor: " + an + "; Background: #0b1524(0.9); Label {{ Anchor: (Full: 0); Text: \\"" + {PKG}.Widgets.label(pids[i]) + "\\"; Style: (FontSize: 7, TextColor: #eaf6ff, HorizontalAlignment: Center, VerticalAlignment: Center); }} }}");
    }}
  }}'''
s = s.replace(old_hdr, new_hdr)
# editor box: taller, rows a bit tighter
s = s.replace('Group #SkyyEditor {{ Anchor: (Width: 700, Height: 530);', 'Group #SkyyEditor {{ Anchor: (Width: 720, Height: 840);')
s = s.replace('"Group #SkyyERow" + ids[i] + " {{ Anchor: (Height: 48); LayoutMode: Top; Padding: (Vertical: 2); }}"', '"Group #SkyyERow" + ids[i] + " {{ Anchor: (Height: 44); LayoutMode: Top; Padding: (Vertical: 1); }}"')
open("build_skyyhud_0.2.7.py", "w", encoding="utf8").write(s)
print("wrote build_skyyhud_0.2.7.py")
