# one-off (2026-09-22): cross-mod bridge without dependencies.
# SkyyCoins 0.1.2 publishes balances into a JVM-global map kept in System properties ("skyy.bridge", key "coins:<uuid>").
# SkyyHud 0.2.6 adds a "Coins" widget that reads it (shows "-" when SkyyCoins is not installed).
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BRIDGE_JAVA = '''
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}'''

# ---- Coins 0.1.2 ----
src = os.path.join(ROOT, "SkyyCoins", "build_skyycoins_0.1.1.py"); dst = os.path.join(ROOT, "SkyyCoins", "build_skyycoins_0.1.2.py")
s = open(src, encoding="utf8").read().replace('VERSION = "0.1.1"', 'VERSION = "0.1.2"').replace("build_skyycoins_0.1.1.py", "build_skyycoins_0.1.2.py")
s = s.replace('SkyyCoins 0.1.1 - build script', 'SkyyCoins 0.1.2 - build script')
s = s.replace('/deathpenalty with no argument shows the current setting.\n"""', '/deathpenalty with no argument shows the current setting.\n0.1.2: publishes balances to the JVM bridge (System property "skyy.bridge", key "coins:<uuid>") so SkyyHud can show a Coins widget without a dependency.\n"""')
anchor = 'cs.addMethod(CtNewMethod.make("""\npublic static void warn(String msg) {'
assert anchor in s
s = s.replace(anchor, 'cs.addMethod(CtNewMethod.make("""' + BRIDGE_JAVA + '""", cs))\n' + anchor, 1)
# publish on load (after reading file) and on set
old_load = '      if (v != null) BAL.put(u, Long.valueOf(Long.parseLong(v.trim())));\n    }\n    LOADED.put(u, Boolean.TRUE);'
assert old_load in s
s = s.replace(old_load, '      if (v != null) BAL.put(u, Long.valueOf(Long.parseLong(v.trim())));\n    }\n    LOADED.put(u, Boolean.TRUE);\n    Long cur = (Long) BAL.get(u);\n    bridge().put("coins:" + u.toString(), cur == null ? Long.valueOf(0L) : cur);')
old_set = '  load(u);\n  BAL.put(u, Long.valueOf(v));\n  try {'
assert old_set in s
s = s.replace(old_set, '  load(u);\n  BAL.put(u, Long.valueOf(v));\n  bridge().put("coins:" + u.toString(), Long.valueOf(v));\n  try {')
open(dst, "w", encoding="utf8").write(s); print("wrote", dst)

# ---- HUD 0.2.6 ----
src = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.2.5.py"); dst = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.2.6.py")
s = open(src, encoding="utf8").read().replace('VERSION = "0.2.5"', 'VERSION = "0.2.6"').replace("build_skyyhud_0.2.5.py", "build_skyyhud_0.2.6.py")
s = s.replace('IDS = ["Coords", "Dir", "Zone", "Gclock", "Rclock", "Day", "Session", "Online"]',
              'IDS = ["Coords", "Dir", "Zone", "Gclock", "Rclock", "Day", "Session", "Online", "Coins"]')
s = s.replace('"Session": (False, "br", 8, 70), "Online": (False, "tr", 8, 40)}',
              '"Session": (False, "br", 8, 70), "Online": (False, "tr", 8, 40), "Coins": (True, "br", 8, 8)}')
s = s.replace('"Day": "Day Counter", "Session": "Session Time", "Online": "Players Online"}',
              '"Day": "Day Counter", "Session": "Session Time", "Online": "Players Online", "Coins": "Coins"}')
old_text = '    if (id.equals("online")) return {UNI}.get().getPlayers().size() + " online";'
if old_text not in s:
    old_text = '    if (id.equals("Online")) return {UNI}.get().getPlayers().size() + " online";'
assert old_text in s, "online branch not found"
s = s.replace(old_text, old_text + '''
    if (id.equals("Coins")) {{
      Object o = null;
      try {{ Object b = System.getProperties().get("skyy.bridge"); if (b != null) o = ((java.util.Map) b).get("coins:" + pr.getUuid().toString()); }} catch (Throwable t) {{ o = null; }}
      if (o == null) return "Coins: -";
      return "Coins: " + java.text.NumberFormat.getIntegerInstance(java.util.Locale.US).format(((Long) o).longValue());
    }}''')
# editor page height: 9 rows now
s = s.replace('Group #SkyyEditor {{ Anchor: (Width: 700, Height: 480);', 'Group #SkyyEditor {{ Anchor: (Width: 700, Height: 530);')
open(dst, "w", encoding="utf8").write(s); print("wrote", dst)
