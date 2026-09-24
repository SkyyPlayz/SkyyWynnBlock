"""Derive SkyySacks/build_skyysacks_0.6.2.py from 0.6.1.
0.6.2: bag page (SacksPage) scaled up ~35% (Skyy: "please scale this menu up"): 86 px cells, 64 px icons, bigger tabs/buttons/text.
       CraftPage.accessories() ignores any acc:has id that is not a Skyy_Accessory_ bench accessory (defensive, for talismans).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.6.1.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.6.2.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)

def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:90]
    s = s.replace(old, new, count)

rep('VERSION = "0.6.1"', 'VERSION = "0.6.2"')
s = s.replace('"""SkyySacks 0.6.1', '"""SkyySacks 0.6.2\n0.6.2: bag page scaled up ~35%; CraftPage ignores non-bench ids in acc:has.\n', 1)

# ---- scale only inside SacksPage.build
a = s.index('page.addMethod(CtNewMethod.make(f"""\npublic void build(')
b = s.index('}}""", page))', a)
body = s[a:b]
R = [
 ('Anchor: (Width: 420, Height: 120)', 'Anchor: (Width: 560, Height: 160)'),
 ('Label {{ Anchor: (Height: 30); Text: \\\\"Pocket Dimension\\\\"; Style: (FontSize: 16,', 'Label {{ Anchor: (Height: 40); Text: \\\\"Pocket Dimension\\\\"; Style: (FontSize: 20,'),
 ('Label {{ Anchor: (Height: 44); Text: \\\\"You need a magic bag', 'Label {{ Anchor: (Height: 60); Text: \\\\"You need a magic bag'),
 ('Style: (FontSize: 11, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center, Wrap: true)', 'Style: (FontSize: 14, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center, Wrap: true)'),
 ('FontSize: 12, TextColor: #ffe9c9, RenderBold: true', 'FontSize: 15, TextColor: #ffe9c9, RenderBold: true'),
 ('FontSize: 12, TextColor: #ffffff, RenderBold: true', 'FontSize: 15, TextColor: #ffffff, RenderBold: true'),
 ('FontSize: 12, TextColor: #1a1000, RenderBold: true', 'FontSize: 15, TextColor: #1a1000, RenderBold: true'),
 ('Anchor: (Width: 660, Height: 470)', 'Anchor: (Width: 900, Height: 600)'),
 ('Group #SkyySTabs {{ Anchor: (Height: 34); LayoutMode: Left; Padding: (Top: 6); }}', 'Group #SkyySTabs {{ Anchor: (Height: 46); LayoutMode: Left; Padding: (Top: 8); }}'),
 ('" {{ Anchor: (Width: 130, Height: 28); Text: \\\\"" + cats[c]', '" {{ Anchor: (Width: 175, Height: 36); Text: \\\\"" + cats[c]'),
 ('"Label {{ Anchor: (Width: 6, Height: 28); Text: \\\\"\\\\"; }}"', '"Label {{ Anchor: (Width: 8, Height: 36); Text: \\\\"\\\\"; }}"'),
 ('"Label {{ Anchor: (Width: 20, Height: 28); Text: \\\\"\\\\"; }}"', '"Label {{ Anchor: (Width: 26, Height: 36); Text: \\\\"\\\\"; }}"'),
 ('TextButton #SkyySTabCraft {{ Anchor: (Width: 110, Height: 28);', 'TextButton #SkyySTabCraft {{ Anchor: (Width: 145, Height: 36);'),
 ('Label #SkyySCap {{ Anchor: (Height: 24);', 'Label #SkyySCap {{ Anchor: (Height: 34);'),
 ('Style: (FontSize: 14, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }}");\n  java.util.ArrayList entries', 'Style: (FontSize: 18, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }}");\n  java.util.ArrayList entries'),
 ('" {{ Anchor: (Height: 66); LayoutMode: Left; Padding: (Top: 4); }}"', '" {{ Anchor: (Height: 92); LayoutMode: Left; Padding: (Top: 6); }}"'),
 ('" {{ Anchor: (Width: 62, Height: 62); Style: ButtonStyle(', '" {{ Anchor: (Width: 86, Height: 86); Style: ButtonStyle('),
 ('ItemIcon {{ Anchor: (Width: 46, Height: 46, Left: 8, Top: 4);', 'ItemIcon {{ Anchor: (Width: 64, Height: 64, Left: 11, Top: 5);'),
 ('Label {{ Anchor: (Width: 58, Height: 14, Right: 3, Bottom: 2); Text: \\\\"" + cnt + "\\\\"; Style: (FontSize: 11,', 'Label {{ Anchor: (Width: 80, Height: 18, Right: 4, Bottom: 3); Text: \\\\"" + cnt + "\\\\"; Style: (FontSize: 14,'),
 ('"Group {{ Anchor: (Width: 62, Height: 62); Background: #142030(0.9); }}"', '"Group {{ Anchor: (Width: 86, Height: 86); Background: #142030(0.9); }}"'),
 ('"Label {{ Anchor: (Width: 4, Height: 62); Text: \\\\"\\\\"; }}"', '"Label {{ Anchor: (Width: 6, Height: 86); Text: \\\\"\\\\"; }}"'),
 ('Label #SkyySInfo {{ Anchor: (Height: 22);', 'Label #SkyySInfo {{ Anchor: (Height: 30);'),
 ('Style: (FontSize: 12, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center); }}");\n  b.appendInline("#SkyySacks", "Group #SkyySAct', 'Style: (FontSize: 15, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center); }}");\n  b.appendInline("#SkyySacks", "Group #SkyySAct'),
 ('Group #SkyySAct {{ Anchor: (Height: 36); LayoutMode: Left; Padding: (Top: 6); }}', 'Group #SkyySAct {{ Anchor: (Height: 48); LayoutMode: Left; Padding: (Top: 8); }}'),
 ('TextButton #SkyySPickAll {{ Anchor: (Width: 150, Height: 28);', 'TextButton #SkyySPickAll {{ Anchor: (Width: 200, Height: 38);'),
 ('TextButton #SkyySDepAll {{ Anchor: (Width: 150, Height: 28);', 'TextButton #SkyySDepAll {{ Anchor: (Width: 200, Height: 38);'),
 ('"Label {{ Anchor: (Width: 10, Height: 28); Text: \\\\"\\\\"; }}"', '"Label {{ Anchor: (Width: 14, Height: 38); Text: \\\\"\\\\"; }}"'),
 ('"Label {{ Anchor: (Width: 300, Height: 28); Text: \\\\"left click takes a stack - right click takes one\\\\"; Style: (FontSize: 11,', '"Label {{ Anchor: (Width: 420, Height: 38); Text: \\\\"left click takes a stack - right click takes one\\\\"; Style: (FontSize: 14,'),
]
for old, new in R:
    n = body.count(old)
    assert n >= 1, "SacksPage anchor missing: " + old[:90]
    body = body.replace(old, new)
s = s[:a] + body + s[b:]

# ---- defensive: only bench accessories become craft tabs
rep('    if (id.equals("Skyy_Accessory_Bag")) continue;', '    if (id.equals("Skyy_Accessory_Bag") || !id.startsWith("Skyy_Accessory_")) continue;')

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
