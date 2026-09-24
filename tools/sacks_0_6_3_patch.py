"""Derive SkyySacks/build_skyysacks_0.6.3.py from 0.6.2.
0.6.3: craft page (CraftPage) - tabs WRAP onto several rows (Skyy's screenshot: 10 bench tabs overflowed the panel) and the whole page is
       scaled up ~35% like the 0.6.2 bag page.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.6.2.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.6.3.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)

def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:90]
    s = s.replace(old, new, count)

rep('VERSION = "0.6.2"', 'VERSION = "0.6.3"')
s = s.replace('"""SkyySacks 0.6.2', '"""SkyySacks 0.6.3' + LF + '0.6.3: craft page tabs wrap onto rows, craft page scaled ~35%.' + LF, 1)

a = s.index('cpg.addMethod(CtNewMethod.make(f"""' + LF + 'public void build(')
b = s.index('}}""", cpg))', a)
body = s[a:b]
Q = '\\\\"'   # how \" appears inside the Python source of the build script
R = [
 ('LabelStyle: (FontSize: 10,', 'LabelStyle: (FontSize: 13,'),
 ('Anchor: (Width: 720, Height: 620)', 'Anchor: (Width: 1000, Height: 830)'),
 ('Label {{ Anchor: (Height: 26); Text: ' + Q + 'Crafting' + Q + '; Style: (FontSize: 15,', 'Label {{ Anchor: (Height: 34); Text: ' + Q + 'Crafting' + Q + '; Style: (FontSize: 19,'),
 ('Label {{ Anchor: (Height: 16); Text: ' + Q + 'Materials are counted from your inventory and your magic bags.' + Q + '; Style: (FontSize: 10,',
  'Label {{ Anchor: (Height: 22); Text: ' + Q + 'Materials are counted from your inventory and your magic bags.' + Q + '; Style: (FontSize: 13,'),
 ('" {{ Anchor: (Height: 46); LayoutMode: Left; Padding: (Top: 4); "', '" {{ Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); "'),
 ('"Group {{ Anchor: (Width: 42, Height: 42); ItemIcon {{ Anchor: (Width: 36, Height: 36, Left: 3, Top: 3);', '"Group {{ Anchor: (Width: 56, Height: 54); ItemIcon {{ Anchor: (Width: 46, Height: 46, Left: 5, Top: 4);'),
 ('" {{ Anchor: (Width: 420, Height: 42); LayoutMode: Top; }}"', '" {{ Anchor: (Width: 600, Height: 54); LayoutMode: Top; }}"'),
 ('"Label {{ Anchor: (Height: 20); Text: ' + Q + '" + {PKG}.SacksPage.safe(pretty(outId)', '"Label {{ Anchor: (Height: 27); Text: ' + Q + '" + {PKG}.SacksPage.safe(pretty(outId)'),
 ('Style: (FontSize: 12, RenderBold: true, TextColor: " + (lim > 0 ? "#ffffff"', 'Style: (FontSize: 15, RenderBold: true, TextColor: " + (lim > 0 ? "#ffffff"'),
 ('"Label {{ Anchor: (Height: 18); Text: ' + Q + '" + {PKG}.SacksPage.safe(need.toString()) + "' + Q + '; Style: (FontSize: 10,', '"Label {{ Anchor: (Height: 23); Text: ' + Q + '" + {PKG}.SacksPage.safe(need.toString()) + "' + Q + '; Style: (FontSize: 12,'),
 ('" {{ Anchor: (Width: 64, Height: 26); Text: ' + Q + 'Craft' + Q, '" {{ Anchor: (Width: 82, Height: 34); Text: ' + Q + 'Craft' + Q),
 ('" {{ Anchor: (Width: 52, Height: 26); Text: ' + Q + 'x10' + Q, '" {{ Anchor: (Width: 66, Height: 34); Text: ' + Q + 'x10' + Q),
 ('" {{ Anchor: (Width: 52, Height: 26); Text: ' + Q + 'All "', '" {{ Anchor: (Width: 76, Height: 34); Text: ' + Q + 'All "'),
 ('"Label {{ Anchor: (Width: 4, Height: 26); Text: ' + Q + Q + '; }}"', '"Label {{ Anchor: (Width: 6, Height: 34); Text: ' + Q + Q + '; }}"'),
 ('Text: ' + Q + 'No recipes here yet.' + Q + '; Style: (FontSize: 12,', 'Text: ' + Q + 'No recipes here yet.' + Q + '; Style: (FontSize: 15,'),
 ('Label #SkyyCInfo {{ Anchor: (Height: 18);', 'Label #SkyyCInfo {{ Anchor: (Height: 26);'),
 ('+ "' + Q + '; Style: (FontSize: 11, TextColor: #c9b89a', '+ "' + Q + '; Style: (FontSize: 14, TextColor: #c9b89a'),
 ('Group #SkyyCNav {{ Anchor: (Height: 30); LayoutMode: Left; Padding: (Top: 4); }}', 'Group #SkyyCNav {{ Anchor: (Height: 42); LayoutMode: Left; Padding: (Top: 6); }}'),
 ('TextButton #SkyyCPrev {{ Anchor: (Width: 70, Height: 26);', 'TextButton #SkyyCPrev {{ Anchor: (Width: 92, Height: 34);'),
 ('TextButton #SkyyCNext {{ Anchor: (Width: 70, Height: 26);', 'TextButton #SkyyCNext {{ Anchor: (Width: 92, Height: 34);'),
 ('"Label {{ Anchor: (Width: 120, Height: 26); Text: ' + Q + 'Page " + (this.pageNo + 1) + " / " + pages + "' + Q + '; Style: (FontSize: 10,', '"Label {{ Anchor: (Width: 160, Height: 34); Text: ' + Q + 'Page " + (this.pageNo + 1) + " / " + pages + "' + Q + '; Style: (FontSize: 13,'),
]
for old, new in R:
    assert body.count(old) >= 1, "CraftPage anchor missing: " + old[:100]
    body = body.replace(old, new)

# tabs: wrap onto rows (first row starts with the Bags button, 7 tabs; later rows 8 tabs)
old_tabs_start = body.index('  b.appendInline("#SkyyCraft", "Group #SkyyCTabs {{')
old_tabs_end = body.index('  ev.addEventBinding({BT}.Activating, "#SkyyCBags", {EVD}.of("a", "bags"));') + len('  ev.addEventBinding({BT}.Activating, "#SkyyCBags", {EVD}.of("a", "bags"));')
new_tabs = LF.join([
 '  int tabRow = 0; int inRow = 0;',
 '  b.appendInline("#SkyyCraft", "Group #SkyyCTabs0 {{ Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 4); }}");',
 '  b.appendInline("#SkyyCTabs0", "TextButton #SkyyCBags {{ Anchor: (Width: 92, Height: 32); Text: ' + Q + 'Bags' + Q + '; " + bs + " }}");',
 '  b.appendInline("#SkyyCTabs0", "Label {{ Anchor: (Width: 14, Height: 32); Text: ' + Q + Q + '; }}");',
 '  ev.addEventBinding({BT}.Activating, "#SkyyCBags", {EVD}.of("a", "bags"));',
 '  for (int i = 0; i < this.tabs.size(); i++) {{',
 '    int cap = tabRow == 0 ? 7 : 8;',
 '    if (inRow >= cap) {{ tabRow++; inRow = 0; b.appendInline("#SkyyCraft", "Group #SkyyCTabs" + tabRow + " {{ Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 4); }}"); }}',
 '    String[] t = (String[]) this.tabs.get(i);',
 '    boolean sel = t[0].equals(this.tab);',
 '    b.appendInline("#SkyyCTabs" + tabRow, "TextButton #SkyyCTab" + i + " {{ Anchor: (Width: 110, Height: 32); Text: ' + Q + '" + {PKG}.SacksPage.safe(t[1]) + "' + Q + '; " + (sel ? on : bs) + " }}");',
 '    b.appendInline("#SkyyCTabs" + tabRow, "Label {{ Anchor: (Width: 6, Height: 32); Text: ' + Q + Q + '; }}");',
 '    ev.addEventBinding({BT}.Activating, "#SkyyCTab" + i, {EVD}.of("a", "tab:" + i));',
 '    inRow++;',
 '  }}',
])
body = body[:old_tabs_start] + new_tabs + body[old_tabs_end:]
s = s[:a] + body + s[b:]

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
