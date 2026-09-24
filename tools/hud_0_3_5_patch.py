"""Derive SkyyHud/build_skyyhud_0.3.5.py from 0.3.4.
0.3.5 (Skyy): Widgets page and per-widget Settings page scaled up ~1.8x ("a lot bigger"); buttons say "Back": the Settings page goes back
to the Widgets list, the Widgets list goes back to the editor.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.4.py")
dst = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.5.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
BS = chr(92)
Q = BS + BS + '"'


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:90]
    s = s.replace(old, new, count)


def scoped(start_marker, end_marker, pairs):
    global s
    a = s.index(start_marker)
    b = s.index(end_marker, a)
    body = s[a:b]
    for old, new in pairs:
        assert old in body, "scoped anchor missing: " + old[:90]
        body = body.replace(old, new)
    s = s[:a] + body + s[b:]


rep('VERSION = "0.3.4"', 'VERSION = "0.3.5"')

# ---- SettingsPage build
scoped('sett.addMethod(CtNewMethod.make(f"""' + LF + 'public void build(', '}}""", sett))', [
    ('LabelStyle: (FontSize: 10,', 'LabelStyle: (FontSize: 17,'),
    ('Anchor: (Width: 520, Height: 330)', 'Anchor: (Width: 940, Height: 440)'),
    ('Label {{ Anchor: (Height: 26); Text: ' + Q + '" + {PKG}.Widgets.label(this.wid) + " settings' + Q + '; Style: (FontSize: 15,',
     'Label {{ Anchor: (Height: 44); Text: ' + Q + '" + {PKG}.Widgets.label(this.wid) + " settings' + Q + '; Style: (FontSize: 26,'),
    ('{{ Anchor: (Height: 32); LayoutMode: Left; Padding: (Top: 6); }}', '{{ Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 12); }}'),
    ('Label {{ Anchor: (Width: 120, Height: 24); Text: ', 'Label {{ Anchor: (Width: 210, Height: 44); Text: '),
    ('Style: (FontSize: 12, TextColor: #ffffff, VerticalAlignment: Center); }}', 'Style: (FontSize: 20, TextColor: #ffffff, VerticalAlignment: Center); }}'),
    ('{{ Anchor: (Width: 60, Height: 24); Text: ' + Q + 'ON' + Q, '{{ Anchor: (Width: 104, Height: 44); Text: ' + Q + 'ON' + Q),
    ('{{ Anchor: (Width: 60, Height: 24); Text: ' + Q + 'OFF' + Q, '{{ Anchor: (Width: 104, Height: 44); Text: ' + Q + 'OFF' + Q),
    ('"Label {{ Anchor: (Width: 4, Height: 24); Text: ' + Q + Q + '; }}"', '"Label {{ Anchor: (Width: 8, Height: 44); Text: ' + Q + Q + '; }}"'),
    ('" {{ Anchor: (Width: 52, Height: 24); Text: ' + Q + '" + sizes[i]', '" {{ Anchor: (Width: 92, Height: 44); Text: ' + Q + '" + sizes[i]'),
    ('" {{ Anchor: (Width: 36, Height: 24); Text: ' + Q + '" + an[i]', '" {{ Anchor: (Width: 66, Height: 44); Text: ' + Q + '" + an[i]'),
    ('"Label {{ Anchor: (Width: 3, Height: 24); Text: ' + Q + Q + '; }}"', '"Label {{ Anchor: (Width: 6, Height: 44); Text: ' + Q + Q + '; }}"'),
    ('Group #SkyySetRow5 {{ Anchor: (Height: 36); LayoutMode: Left; Padding: (Top: 12); }}', 'Group #SkyySetRow5 {{ Anchor: (Height: 70); LayoutMode: Left; Padding: (Top: 20); }}'),
    ('TextButton #SkyySetBack {{ Anchor: (Width: 140, Height: 26); Text: ' + Q + 'Back to editor' + Q,
     'TextButton #SkyySetBack {{ Anchor: (Width: 220, Height: 46); Text: ' + Q + '< Back' + Q),
])
# Settings "back" -> Widgets list
rep('      if (player != null) {{ {PKG}.EditorPage ep = new {PKG}.EditorPage(this.playerRef, this.plugin); ep.sel = this.wid; player.getPageManager().openCustomPage(ref, st, ep); }}',
    '      if (player != null) player.getPageManager().openCustomPage(ref, st, new {PKG}.WidgetsPage(this.playerRef, this.plugin));')

# ---- WidgetsPage build
scoped('wpg.addMethod(CtNewMethod.make(f"""' + LF + 'public void build(', '}}""", wpg))', [
    ('LabelStyle: (FontSize: 10,', 'LabelStyle: (FontSize: 17,'),
    ('Anchor: (Width: 520, Height: " + (90 + 36 * ids.length) + ")', 'Anchor: (Width: 900, Height: " + (150 + 62 * ids.length) + ")'),
    ('Label {{ Anchor: (Height: 26); Text: ' + Q + 'Widgets' + Q + '; Style: (FontSize: 15,', 'Label {{ Anchor: (Height: 44); Text: ' + Q + 'Widgets' + Q + '; Style: (FontSize: 26,'),
    ('" {{ Anchor: (Height: 36); LayoutMode: Left; Padding: (Top: 8); }}"', '" {{ Anchor: (Height: 62); LayoutMode: Left; Padding: (Top: 12); }}"'),
    ('"Label {{ Anchor: (Width: 200, Height: 26); Text: ' + Q + '" + {PKG}.Widgets.label(ids[i]) + "' + Q + '; Style: (FontSize: 12,',
     '"Label {{ Anchor: (Width: 360, Height: 46); Text: ' + Q + '" + {PKG}.Widgets.label(ids[i]) + "' + Q + '; Style: (FontSize: 20,'),
    ('{{ Anchor: (Width: 60, Height: 26); Text: ' + Q + 'ON' + Q, '{{ Anchor: (Width: 104, Height: 46); Text: ' + Q + 'ON' + Q),
    ('{{ Anchor: (Width: 60, Height: 26); Text: ' + Q + 'OFF' + Q, '{{ Anchor: (Width: 104, Height: 46); Text: ' + Q + 'OFF' + Q),
    ('"Label {{ Anchor: (Width: 4, Height: 26); Text: ' + Q + Q + '; }}"', '"Label {{ Anchor: (Width: 8, Height: 46); Text: ' + Q + Q + '; }}"'),
    ('"Label {{ Anchor: (Width: 12, Height: 26); Text: ' + Q + Q + '; }}"', '"Label {{ Anchor: (Width: 22, Height: 46); Text: ' + Q + Q + '; }}"'),
    ('{{ Anchor: (Width: 90, Height: 26); Text: ' + Q + 'Settings' + Q, '{{ Anchor: (Width: 170, Height: 46); Text: ' + Q + 'Settings' + Q),
    ('Group #SkyyWFoot {{ Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 12); }}', 'Group #SkyyWFoot {{ Anchor: (Height: 72); LayoutMode: Left; Padding: (Top: 20); }}'),
    ('TextButton #SkyyWBack {{ Anchor: (Width: 140, Height: 26); Text: ' + Q + 'Back to editor' + Q,
     'TextButton #SkyyWBack {{ Anchor: (Width: 220, Height: 48); Text: ' + Q + '< Back' + Q),
])

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
