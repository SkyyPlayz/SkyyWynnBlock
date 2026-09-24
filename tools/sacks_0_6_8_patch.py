"""Derive SkyySacks/build_skyysacks_0.6.8.py from 0.6.7.
0.6.8 (Skyy: "instead of making all the different crafting things their own page, put almost all of them together into one crafting tab"):
craft page tabs are now  Crafting | Processing | Collections.
 - Crafting  = every Fieldcraft (pocket) recipe + every recipe of every equipped bench accessory whose BenchRequirement type is not
               Processing, up to that accessory's tier.
 - Processing = recipes of equipped Processing-type benches (Furnace, Campfire, Tannery, Salvage) up to tier; tab only shown if non-empty.
 - Collections = unchanged.
The 0.6.6 sort (craftable first, material progression, name) and the Craftable-only toggle apply to the merged lists.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.6.7.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.6.8.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:90]
    s = s.replace(old, new, count)


rep('VERSION = "0.6.7"', 'VERSION = "0.6.8"')
s = s.replace('"""SkyySacks 0.6.7', '"""SkyySacks 0.6.8' + LF + '0.6.8: craft tabs merged into Crafting | Processing | Collections.' + LF, 1)

# new helper benchRecipes, inserted right before buildTabs (so buildTabs and recipesFor can call it)
bt_start = s.index('cpg.addMethod(CtNewMethod.make(f"""' + LF + 'public java.util.ArrayList buildTabs(')
helper = LF.join([
    'cpg.addMethod(CtNewMethod.make(f"""',
    'public static java.util.TreeSet benchRecipes(java.util.UUID u, boolean processing) {{',
    '  java.util.TreeSet ids = new java.util.TreeSet();',
    '  java.util.HashMap acc = accessories(({PLA}) null, u);',
    '  if (acc.isEmpty()) return ids;',
    '  java.util.Iterator it = {CRR}.getAssetMap().getAssetMap().values().iterator();',
    '  while (it.hasNext()) {{',
    '    {CRR} r = ({CRR}) it.next();',
    '    {BRQ}[] br = r.getBenchRequirement();',
    '    if (br == null) continue;',
    '    for (int i = 0; i < br.length; i++) {{',
    '      if (br[i] == null || br[i].id == null) continue;',
    '      Integer tier = null;',
    '      java.util.Iterator ki = acc.keySet().iterator();',
    '      while (ki.hasNext()) {{ String k = (String) ki.next(); if (k.equalsIgnoreCase(br[i].id)) {{ tier = (Integer) acc.get(k); break; }} }}',
    '      if (tier == null) continue;',
    '      boolean proc = "Processing".equals(String.valueOf(br[i].type));',
    '      if (proc != processing) continue;',
    '      int need = br[i].requiredTierLevel; if (need <= 0) need = 1;',
    '      if (need <= tier.intValue()) {{ ids.add(r.getId()); break; }}',
    '    }}',
    '  }}',
    '  return ids;',
    '}}""", cpg))',
    '',
])
s = s[:bt_start] + helper + s[bt_start:]

# buildTabs: Crafting | Processing | Collections
b1 = s.index('public java.util.ArrayList buildTabs(')
b2 = s.index('}}""", cpg))', b1)
s = s[:b1] + LF.join([
    'public java.util.ArrayList buildTabs({PLA} p, java.util.UUID u) {{',
    '  java.util.ArrayList t = new java.util.ArrayList();',
    '  t.add(new String[] {{ "A:craft", "Crafting" }});',
    '  if (!benchRecipes(u, true).isEmpty()) t.add(new String[] {{ "A:proc", "Processing" }});',
    '  if (!collectionRecipes(u).isEmpty()) t.add(new String[] {{ "C:", "Collections" }});',
    '  return t;',
    '',
]) + s[b2:]

# recipesFor: handle the merged tabs (old F:/B: ids still work)
rep('  if (tabId.startsWith("F:")) {{' + LF + '    java.util.Set s = {CRP}.getAvailableRecipesForCategory("Fieldcraft", tabId.substring(2));',
    LF.join([
        '  if (tabId.equals("A:craft")) {{',
        '    java.util.Iterator fi = {FCC}.getAssetMap().getAssetMap().values().iterator();',
        '    while (fi.hasNext()) {{',
        '      {FCC} fc = ({FCC}) fi.next();',
        '      java.util.Set fs = {CRP}.getAvailableRecipesForCategory("Fieldcraft", fc.getId());',
        '      if (fs != null) ids.addAll(fs);',
        '    }}',
        '    ids.addAll(benchRecipes(u, false));',
        '  }} else if (tabId.equals("A:proc")) {{',
        '    ids.addAll(benchRecipes(u, true));',
        '  }} else if (tabId.startsWith("F:")) {{',
        '    java.util.Set s = {CRP}.getAvailableRecipesForCategory("Fieldcraft", tabId.substring(2));',
    ]))

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
