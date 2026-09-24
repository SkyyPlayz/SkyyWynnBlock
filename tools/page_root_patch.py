# one-off (2026-09-22): pages must have a root Group with only Width/Height in its Anchor (the page system centres it),
# not a Full-anchored wrapper + centred child (that rendered full-screen, top-left). Pattern from SkillHudSettings.ui
# (`Group #Root { Anchor: (Width: 824, Height: 800); ... }`) and BetterMap ConfigMenu.ui.
# Derives: SkyyHud 0.2.4 -> 0.2.5, SkyySacks 0.1.2 (in place), SkyyCollections 0.1.1 -> 0.1.2.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def bump(src, dst, old_v, new_v):
    s = open(src, encoding="utf8").read()
    s = s.replace('VERSION = "%s"' % old_v, 'VERSION = "%s"' % new_v)
    s = s.replace(os.path.basename(src), os.path.basename(dst))
    return s

# ---- SkyyHud 0.2.5 ----
src = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.2.4.py"); dst = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.2.5.py")
s = bump(src, dst, "0.2.4", "0.2.5")
old = '''  b.appendInline((String) null, "Group #SkyyEditorRoot {{ Anchor: (Full: 0); }}");
  b.appendInline("#SkyyEditorRoot", "Group #SkyyEditor {{ Anchor: (Horizontal: 0, Vertical: 0, Width: 700, Height: 480); Background: #0b1524(0.94); Padding: (Horizontal: 14, Vertical: 10); LayoutMode: Top; }}");'''
assert old in s, "hud editor root not found"
s = s.replace(old, '''  b.appendInline((String) null, "Group #SkyyEditor {{ Anchor: (Width: 700, Height: 480); Background: #0b1524(0.94); Padding: (Horizontal: 14, Vertical: 10); LayoutMode: Top; }}");''')
open(dst, "w", encoding="utf8").write(s); print("wrote", dst)

# ---- SkyySacks 0.1.2 (in place) ----
p = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.1.2.py"); s = open(p, encoding="utf8").read()
old = '''  b.appendInline((String) null, "Group #SkyySacksRoot {{ Anchor: (Full: 0); }}");
  b.appendInline("#SkyySacksRoot", "Group #SkyySacks {{ Anchor: (Horizontal: 0, Vertical: 0, Width: 560, Height: 470); Background: #0b1524(0.94); Padding: (Horizontal: 14, Vertical: 10); LayoutMode: Top; }}");'''
assert old in s, "sacks root not found"
s = s.replace(old, '''  b.appendInline((String) null, "Group #SkyySacks {{ Anchor: (Width: 560, Height: 470); Background: #0b1524(0.94); Padding: (Horizontal: 14, Vertical: 10); LayoutMode: Top; }}");''')
open(p, "w", encoding="utf8").write(s); print("patched", p)

# ---- SkyyCollections 0.1.2 ----
src = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.1.1.py"); dst = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.1.2.py")
s = bump(src, dst, "0.1.1", "0.1.2")
old = '''  b.appendInline((String) null, "Group #SkyyCollRoot {{ Anchor: (Full: 0); }}");
  b.appendInline("#SkyyCollRoot", "Group #SkyyColl {{ Anchor: (Horizontal: 0, Vertical: 0, Width: 560, Height: 460); Background: #0b1524(0.94); Padding: (Horizontal: 14, Vertical: 10); LayoutMode: Top; }}");'''
assert old in s, "collections root not found"
s = s.replace(old, '''  b.appendInline((String) null, "Group #SkyyColl {{ Anchor: (Width: 560, Height: 460); Background: #0b1524(0.94); Padding: (Horizontal: 14, Vertical: 10); LayoutMode: Top; }}");''')
open(dst, "w", encoding="utf8").write(s); print("wrote", dst)
