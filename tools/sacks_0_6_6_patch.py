"""Derive SkyySacks/build_skyysacks_0.6.6.py from 0.6.5.
0.6.6 craft page sorting (Skyy): recipes you can craft now first, then the game's material progression (crude/basic, copper, bronze,
iron, thorium, cobalt, adamantite, mithril, onyxium), then name; a "Craftable only" toggle (per player, remembered while online).
"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.6.5.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.6.6.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
BS = chr(92)
Q = BS + BS + '"'   # \" as written inside the build script's f-strings


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:90]
    s = s.replace(old, new, count)


rep('VERSION = "0.6.5"', 'VERSION = "0.6.6"')
s = s.replace('"""SkyySacks 0.6.5', '"""SkyySacks 0.6.6' + LF + '0.6.6: craft page sorts craftable first then by material progression; "Craftable only" toggle.' + LF, 1)

# comparator class, declared with the other classes and compiled before CraftPage
rep('clog = pool.makeClass(PKG + ".CraftLog")', 'clog = pool.makeClass(PKG + ".CraftLog")' + LF + 'rcmp = pool.makeClass(PKG + ".RecipeCmp")')
anchor = '# ================= CraftLog (append-only audit of every craft-page craft) ================='
rep(anchor, LF.join([
    '# ================= RecipeCmp: craftable first, then material progression, then name =================',
    'rcmp.addInterface(pool.get("java.util.Comparator"))',
    'rcmp.addConstructor(CtNewConstructor.make("public RecipeCmp() { }", rcmp))',
    'rcmp.addMethod(CtNewMethod.make("""',
    'public static int tierOf(String id) {',
    '  if (id == null) return 0;',
    '  String[] m = new String[] { "Crude", "Copper", "Bronze", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium" };',
    '  for (int i = m.length - 1; i >= 0; i--) if (id.indexOf(m[i]) >= 0) return i;',
    '  return 0;',
    '}""", rcmp))',
    'rcmp.addMethod(CtNewMethod.make("""',
    'public int compare(Object a, Object b) {',
    '  Object[] x = (Object[]) a; Object[] y = (Object[]) b;',
    '  boolean cx = ((Integer) x[1]).intValue() > 0; boolean cy = ((Integer) y[1]).intValue() > 0;',
    '  if (cx != cy) return cx ? -1 : 1;',
    '  int tx = ((Integer) x[2]).intValue(); int ty = ((Integer) y[2]).intValue();',
    '  if (tx != ty) return tx < ty ? -1 : 1;',
    '  return ((String) x[3]).compareTo((String) y[3]);',
    '}""", rcmp))',
    '',
    anchor]))

# per-player toggle state
rep('cpg.addField(CtField.make("public String tab;", cpg))',
    'cpg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap ONLY = new java.util.concurrent.ConcurrentHashMap();", cpg))' + LF +
    'cpg.addField(CtField.make("public String tab;", cpg))')

# sort + filter right after materials are known
rep('  this.rows = this.tab == null ? new java.util.ArrayList() : recipesFor(this.tab, u);' + LF + '  {CIC} mats = materials(p, u);',
    LF.join([
        '  java.util.ArrayList raw = this.tab == null ? new java.util.ArrayList() : recipesFor(this.tab, u);',
        '  {CIC} mats = materials(p, u);',
        '  boolean only = Boolean.TRUE.equals(ONLY.get(u));',
        '  java.util.ArrayList ent = new java.util.ArrayList();',
        '  for (int i = 0; i < raw.size(); i++) {{',
        '    {CRR} r0 = ({CRR}) raw.get(i);',
        '    int l0 = limit(r0, mats);',
        '    if (only && l0 <= 0) continue;',
        '    {MQ} o0 = r0.getPrimaryOutput();',
        '    String id0 = o0 == null ? String.valueOf(r0.getId()) : o0.getItemId();',
        '    ent.add(new Object[] {{ r0, Integer.valueOf(l0), Integer.valueOf({PKG}.RecipeCmp.tierOf(id0)), id0 == null ? "" : id0 }});',
        '  }}',
        '  java.util.Collections.sort(ent, new {PKG}.RecipeCmp());',
        '  this.rows = new java.util.ArrayList();',
        '  for (int i = 0; i < ent.size(); i++) this.rows.add(((Object[]) ent.get(i))[0]);',
    ]))

# toggle button in the nav row + handler
rep('  ev.addEventBinding({BT}.Activating, "#SkyyCNext", {EVD}.of("a", "next"));' + LF + '}}""", cpg))',
    LF.join([
        '  ev.addEventBinding({BT}.Activating, "#SkyyCNext", {EVD}.of("a", "next"));',
        '  b.appendInline("#SkyyCNav", "Label {{ Anchor: (Width: 40, Height: 34); Text: ' + Q + Q + '; }}");',
        '  b.appendInline("#SkyyCNav", "TextButton #SkyyCOnly {{ Anchor: (Width: 230, Height: 34); Text: ' + Q + 'Craftable only: " + (Boolean.TRUE.equals(ONLY.get(u)) ? "ON" : "OFF") + "' + Q + '; " + (Boolean.TRUE.equals(ONLY.get(u)) ? on : bs) + " }}");',
        '  ev.addEventBinding({BT}.Activating, "#SkyyCOnly", {EVD}.of("a", "onlyc"));',
        '}}""", cpg))',
    ]))
rep('    if (data.indexOf("' + BS + BS + '"next' + BS + BS + '"") >= 0) {{ this.pageNo++; rebuild(); return; }}',
    '    if (data.indexOf("' + BS + BS + '"next' + BS + BS + '"") >= 0) {{ this.pageNo++; rebuild(); return; }}' + LF +
    '    if (data.indexOf("' + BS + BS + '"onlyc' + BS + BS + '"") >= 0) {{ if (Boolean.TRUE.equals(ONLY.get(u))) ONLY.remove(u); else ONLY.put(u, Boolean.TRUE); this.pageNo = 0; rebuild(); return; }}')

m = re.search(r'for c in \(([^)]*)\):', s)
assert m and 'clog, cpg' in m.group(1), "class write list not found"
s = s[:m.start(1)] + m.group(1).replace('clog, cpg', 'rcmp, clog, cpg', 1) + s[m.end(1):]

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
