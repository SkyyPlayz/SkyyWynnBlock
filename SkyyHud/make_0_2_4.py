# one-off: derive build_skyyhud_0.2.4.py from 0.2.3 (underscore-free IDs, inline editor page)
p = "build_skyyhud_0.2.3.py"; s = open(p, encoding="utf8").read()
s = s.replace('VERSION = "0.2.3"', 'VERSION = "0.2.4"')
s = s.replace('IDS = ["coords", "dir", "zone", "gclock", "rclock", "day", "session", "online"]',
              'IDS = ["Coords", "Dir", "Zone", "Gclock", "Rclock", "Day", "Session", "Online"]')
for old, new in [("coords", "Coords"), ("dir", "Dir"), ("zone", "Zone"), ("gclock", "Gclock"), ("rclock", "Rclock"), ("day", "Day"), ("session", "Session"), ("online", "Online")]:
    s = s.replace('"%s": (' % old, '"%s": (' % new).replace('"%s": "' % old, '"%s": "' % new)
    s = s.replace('id.equals("%s")' % old, 'id.equals("%s")' % new)
s = s.replace('ACTS = ["tog", "tl", "t", "tr", "l", "c", "r", "bl", "b2", "br", "xm", "xp", "ym", "yp", "sm", "sp"]',
              'ACTS = ["Tog", "Tl", "T", "Tr", "L", "C", "R", "Bl", "B2", "Br", "Xm", "Xp", "Ym", "Yp", "Sm", "Sp"]')
s = s.replace('ACT_LABEL = {"tog": "On/Off", "tl": "TL", "t": "T", "tr": "TR", "l": "L", "c": "C", "r": "R", "bl": "BL", "b2": "B", "br": "BR",\n             "xm": "X-", "xp": "X+", "ym": "Y-", "yp": "Y+", "sm": "S-", "sp": "S+"}',
              'ACT_LABEL = {"Tog": "On/Off", "Tl": "TL", "T": "T", "Tr": "TR", "L": "L", "C": "C", "R": "R", "Bl": "BL", "B2": "B", "Br": "BR",\n             "Xm": "X-", "Xp": "X+", "Ym": "Y-", "Yp": "Y+", "Sm": "S-", "Sp": "S+"}')
for old, new in [("tog", "Tog"), ("xm", "Xm"), ("xp", "Xp"), ("ym", "Ym"), ("yp", "Yp"), ("sm", "Sm"), ("sp", "Sp"), ("b2", "B2")]:
    s = s.replace('act.equals("%s")' % old, 'act.equals("%s")' % new)
s = s.replace('    else if (act.equals("B2")) l.anchor = "b";\n    else l.anchor = act;',
              '    else if (act.equals("B2")) l.anchor = "b";\n    else l.anchor = act.toLowerCase();')
s = s.replace('"#w_" + ids[i] + "_t.Text"', '"#SkyyW" + ids[i] + "Txt.Text"')
old_w = 'return "Group #w_" + id + " {{ Anchor: " + anchorSrc(l) + "; Background: #0b1524(0.72); Label #w_" + id + "_t {{ Anchor: (Full: 0); Style: (FontSize: " + fs + ", RenderBold: true, TextColor: #eaf6ff, Alignment: Center); Text: \\\\"\\\\"; }} }}";'
assert old_w in s, "widgetSrc line not found"
s = s.replace(old_w, 'return "Group #SkyyW" + id + " {{ Anchor: " + anchorSrc(l) + "; Background: #0b1524(0.72); Label #SkyyW" + id + "Txt {{ Anchor: (Full: 0); Text: \\\\"\\\\"; Style: (FontSize: " + fs + ", RenderBold: true, TextColor: #eaf6ff, HorizontalAlignment: Center, VerticalAlignment: Center); }} }}";')
s = s.replace('"#e_info_" + ids[i] + ".Text"', '"#SkyyEInfo" + ids[i] + ".Text"')
s = s.replace('"#e_info_" + wid2 + ".Text"', '"#SkyyEInfo" + wid2 + ".Text"')
s = s.replace('data.indexOf("#e_" + ids[i] + "_" + acts[a] + "\\\\"")', 'data.indexOf("#SkyyE" + ids[i] + acts[a] + "\\\\"")')
# editor page: fully inline
start = s.index('page.addMethod(CtNewMethod.make(f"""\npublic void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{')
end = s.index('}}""", page))', start) + len('}}""", page))')
new_build = r'''page.addMethod(CtNewMethod.make(f"""
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
}}""", page))'''
s = s[:start] + new_build + s[end:]
s = s.replace("ACTS_JAVA = \", \".join('\"%s\"' % a for a in ACTS)",
              "ACTS_JAVA = \", \".join('\"%s\"' % a for a in ACTS)\nACT_LABELS_JAVA = \", \".join('\"%s\"' % ACT_LABEL[a] for a in ACTS)")
assert "ACT_LABELS_JAVA =" in s
old_files = 'OUT, {"Common/UI/Custom/Hud/SkyyHud.ui": HUD_UI, "Common/UI/Custom/Pages/SkyyHudEditor.ui": EDITOR_UI,\n                 "Common/UI/Custom/SkyyHud/dot.png": png_dot, "icon-256.png": png_root})'
assert old_files in s
s = s.replace(old_files, 'OUT, {"Common/UI/Custom/SkyyHud/dot.png": png_dot, "icon-256.png": png_root})')
open("build_skyyhud_0.2.4.py", "w", encoding="utf8").write(s)
print("wrote build_skyyhud_0.2.4.py")
