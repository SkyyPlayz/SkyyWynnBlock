"""Derive SkyyEssentials/build_skyyessentials_0.1.4.py from 0.1.3 (python tools/essentials_0_1_4_patch.py, then build the result).
0.1.4 (2026-09-25 HOTFIX, found while fixing SkyyAuctions 0.1.1): the /trade page showed the other player's offer as ItemGridSlots built
from the REAL ItemStacks. A stack with metadata (SkyyRolls rolls / ItemDisplay) makes the client disconnect ("CustomUI Set command couldn't
set value ... Failed to convert JSON value (Object) to specified type (ClientItemMetadata)", seen with SkyyAuctions 0.1). The grid now gets a
metadata-free copy (same item id + quantity = same icon); for a stack that had metadata, the slot's own tooltip (setName / setDescription,
plain text) carries the item's display name and description, so rolled stats stay visible in the trade. Nothing else changes.
From 0.1.4 on this mod uses patch scripts (edit the patch, never the generated file).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyEssentials", "build_skyyessentials_0.1.3.py")
dst = os.path.join(ROOT, "SkyyEssentials", "build_skyyessentials_0.1.4.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:100])
    s = s.replace(old, new, 1)


rep('VERSION = "0.1.3"', 'VERSION = "0.1.4"')
rep('''# read-only grid slots from a SNAPSHOT (never the live container); the real ItemStack gives the native item tooltip
M(tst, r"""
public static java.util.ArrayList gridSlots(@IS@[] a) {
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < a.length; i++) {
    @IGS@ g = null;
    if (a[i] != null && !a[i].isEmpty()) g = new @IGS@(a[i]); else g = new @IGS@();
    g.setActivatable(false);
    l.add(g);
  }
  return l;
}""")''', '''# read-only grid slots from a SNAPSHOT (never the live container). 0.1.4: a grid slot must NEVER carry item metadata (the client
# disconnects: ClientItemMetadata) - the slot gets a metadata-free copy, and a stack that had metadata shows its display name +
# description (plain text, e.g. SkyyRolls rolls) through the slot's own tooltip
M(tst, r"""
public static String rawOf(@MSG@ m) {
  if (m == null) return null;
  try { String r = m.getRawText(); return (r == null || r.trim().length() == 0) ? null : r; } catch (Throwable t) { return null; }
}""")
M(tst, r"""
public static @IGS@ gridSlot(@IS@ s) {
  if (s == null || s.isEmpty()) return new @IGS@();
  @IGS@ g = new @IGS@(new @IS@(s.getItemId(), s.getQuantity()));
  try {
    if (s.getMetadata() != null) {
      String n = rawOf(s.getDisplayName());
      String d = rawOf(s.getDisplayDescription());
      if (n != null) g.setName(n);
      if (d != null) g.setDescription(d);
    }
  } catch (Throwable t) { }
  return g;
}""")
M(tst, r"""
public static java.util.ArrayList gridSlots(@IS@[] a) {
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < a.length; i++) {
    @IGS@ g = gridSlot(a[i]);
    g.setActivatable(false);
    l.add(g);
  }
  return l;
}""")''')
first = s.index('"""') + 3
s = s[:first] + ("0.1.4 (2026-09-25): HOTFIX - /trade offer grids get metadata-free item copies (a rolled item would disconnect the client:\n"
                 "  ClientItemMetadata); rolled items show their name + description in the slot tooltip. Notes in tools/essentials_0_1_4_patch.py.\n") + s[first:]
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
