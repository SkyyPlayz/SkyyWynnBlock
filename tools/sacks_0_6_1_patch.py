"""Derive SkyySacks/build_skyysacks_0.6.1.py from 0.6.0.
0.6.1: craft page bench tabs come from the SkyyAccessories bag (bridge "acc:has:<uuid>" = "Skyy_Accessory_<Bench>_T<n>,...") as well
as accessories carried loose in the inventory; one tab per bench at the highest tier held; recipes filtered by
BenchRequirement.requiredTierLevel <= tier. Tab id "B:<BenchId>:<tier>".
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.6.0.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.6.1.py")
s = open(src, encoding="utf8").read()

def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    s = s.replace(old, new, count)

rep('VERSION = "0.6.0"', 'VERSION = "0.6.1"')
s = s.replace('"""SkyySacks 0.6.0', '"""SkyySacks 0.6.1\n0.6.1: craft page bench tabs from the SkyyAccessories bag (bridge acc:has) + loose accessories, tiered (requiredTierLevel).\n', 1)

# ---- accessories(): HashSet<bench> -> HashMap<bench, Integer tier>, inventory + bridge
start = s.index('public static java.util.HashSet accessories({PLA} p) {{')
end = s.index('}}""", cpg))', start) + len('}}""", cpg))')
new_acc = '''public static java.util.HashMap accessories({PLA} p, java.util.UUID u) {{
  java.util.HashMap out = new java.util.HashMap();
  java.util.ArrayList ids = new java.util.ArrayList();
  // only accessories EQUIPPED in the SkyyAccessories bag count (Skyy: "when you have the accessory in your accessory bag")
  try {{
    Object b = System.getProperties().get("skyy.bridge");
    Object v = b == null ? null : ((java.util.Map) b).get("acc:has:" + u.toString());
    if (v != null) {{
      String[] parts = String.valueOf(v).split(",");
      for (int i = 0; i < parts.length; i++) if (parts[i].trim().length() > 0) ids.add(parts[i].trim());
    }}
  }} catch (Throwable t) {{ }}
  for (int i = 0; i < ids.size(); i++) {{
    String id = (String) ids.get(i);
    if (id.equals("Skyy_Accessory_Bag")) continue;
    String tail = id.substring("Skyy_Accessory_".length());
    String bench = tail; int tier = 1;
    int t = tail.lastIndexOf("_T");
    if (t > 0 && t + 2 < tail.length()) {{
      try {{ tier = Integer.parseInt(tail.substring(t + 2)); bench = tail.substring(0, t); }} catch (Throwable e) {{ }}
    }}
    if (bench.length() == 0) continue;
    Integer cur = (Integer) out.get(bench);
    if (cur == null || cur.intValue() < tier) out.put(bench, Integer.valueOf(tier));
  }}
  return out;
}}""", cpg))'''
s = s[:start] + new_acc + s[end:]

# ---- buildTabs
rep('''  java.util.HashSet acc = accessories(p);
  java.util.Iterator ai = acc.iterator();
  while (ai.hasNext()) {{ String bench = (String) ai.next(); t.add(new String[] {{ "B:" + bench, pretty(bench) }}); }}''',
'''  java.util.HashMap acc = accessories(p, u);
  java.util.ArrayList benches = new java.util.ArrayList(acc.keySet());
  java.util.Collections.sort(benches);
  String[] roman = new String[] {{ "", "I", "II", "III", "IV", "V", "VI", "VII", "VIII" }};
  for (int bi = 0; bi < benches.size(); bi++) {{
    String bench = (String) benches.get(bi);
    int tier = ((Integer) acc.get(bench)).intValue();
    String label = pretty(bench).replace(" Bench", "").replace("bench", "") + (tier > 0 && tier < roman.length ? " " + roman[tier] : "");
    t.add(new String[] {{ "B:" + bench + ":" + tier, label }});
  }}''')

# ---- recipesFor: parse tier + filter requiredTierLevel
rep('''    String bench = tabId.substring(2);
    java.util.Iterator it = {CRR}.getAssetMap().getAssetMap().values().iterator();
    while (it.hasNext()) {{
      {CRR} r = ({CRR}) it.next();
      {BRQ}[] br = r.getBenchRequirement();
      if (br == null) continue;
      for (int i = 0; i < br.length; i++) if (br[i] != null && bench.equalsIgnoreCase(String.valueOf(br[i].id))) {{ ids.add(r.getId()); break; }}
    }}''',
'''    String bench = tabId.substring(2); int tier = 1;
    int colon = bench.indexOf(':');
    if (colon >= 0) {{ try {{ tier = Integer.parseInt(bench.substring(colon + 1)); }} catch (Throwable e) {{ }} bench = bench.substring(0, colon); }}
    java.util.Iterator it = {CRR}.getAssetMap().getAssetMap().values().iterator();
    while (it.hasNext()) {{
      {CRR} r = ({CRR}) it.next();
      {BRQ}[] br = r.getBenchRequirement();
      if (br == null) continue;
      for (int i = 0; i < br.length; i++) {{
        if (br[i] == null || !bench.equalsIgnoreCase(String.valueOf(br[i].id))) continue;
        int need = br[i].requiredTierLevel;
        if (need <= 0) need = 1;
        if (need <= tier) {{ ids.add(r.getId()); break; }}
      }}
    }}''')

open(dst, "w", encoding="utf8").write(s)
print("wrote", dst)
