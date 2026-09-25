"""Derive SkyySacks/build_skyysacks_0.7.6.py from 0.7.5 (edit THIS file, then regenerate: python tools/sacks_0_7_6_patch.py).
0.7.6 = IN-GAME SERVER SETUP + PLAYER SETTINGS (Skyy's rule: everything a server owner might change must be doable in game; the config
file stays and always matches). Sources: research/Server-Setup-Spec.md 4.12 (+ sections 1, 3, 7 and tools/CONFIG-CONTRACT.md) and
research/Settings-Spec.md 3.4 (its "next: 0.7.5" is stale - this is the version after the LIVE 0.7.5).
 - Admin config kit (tools/skyycfg.py, contract v1): config:def:SkyySacks + config:fn:SkyySacks are published at the END of setup(), after
   SackCfg.reload() has loaded Skyy_SkyySacks/config.properties. SkyyMenu 0.3 Server Setup shows the page as "Bags and Crafting"; node
   skyysacks.admin (ops have it through "*"). Same file, same key (craftSearch), nothing else renamed.
   Rows: craftSearch (bool, live; reload:SackCfg.reload - the value lives in the AtomicBoolean SEARCH, so the kit runs the mod's own loader
   right after its write: the change is immediate instead of within ~10 s); bag.small / bag.medium / bag.large (int, live, adv, danger;
   the locked 640 / 2,240 / 20,160 stay the defaults; lowering never deletes pooled items, it only stops intake); bench.queueCap /
   bench.fuelCap / bench.outputCap (int, live, adv; were ProcBench's final QUEUE_CAP 256 / FUEL_CAP 1000 / OUT_CAP 20000).
   Review fix: the bag rows carry check=SackCfg.checkTierOrder - a change that would break Small <= Medium <= Large asks its own question
   ("Bags would be out of order ...") instead of the usual one; it never refuses, and the kit ignores it on import / restore.
   The six caps are now public static volatile ints bound field: (the kit writes them with Field.setInt); SackCfg.reload() is the one
   loader for all seven keys (start-up, the SackSaver's 10 s self-poll, and the kit's RELOAD for hand edits) and clamps to the same bounds
   as the rows. One table (SACK_CAPS in the build script) feeds the fields' initial values, the rows and the loader clamps.
   New installs get the six keys as commented template lines (#bag.small=640 ...) that the kit uncomments in place when an admin changes
   one; an existing 0.7.5 file (craftSearch only) gets the changed line appended under the kit's header. No admin command existed, so none
   is routed; the file's 10 s self-poll stays (it only ever writes the file when it is missing).
 - Player Settings (SkyyMenu 0.2+ registry): sacks.benchDone ("Furnace and Tannery done") and sacks.benchFuel ("Furnace out of fuel"),
   category sacks, default ON, registered in setup() through SackPool.regSetting (a new CREATING bridgeW(); SackPool.bridge() stays
   read-only). ProcTask.run gates ONLY the two sendMessage calls; the DONE crafts.log line and the fuelWarnOnce() latch run as before (the
   latch stays first in its condition, so a hidden warning is still used up and turning the switch back on never replays it).
Defaults = the 0.7.5 constants and ON switches, so nothing changes until an admin or a player changes something. Everything else in
0.7.5 is untouched.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.5.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.6.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert s.count(old) >= 1, "anchor missing: " + old[:90]
    assert count != 1 or s.count(old) == 1, "anchor not unique: " + old[:90]
    s = s.replace(old, new, count)


def seg(start, end, must_have, new):
    """Replace s[start : end) (end exclusive, both anchors unique) after checking the old segment is the one we expect."""
    global s
    assert s.count(start) == 1, "segment start not unique: " + start[:90]
    i = s.index(start)
    j = s.index(end, i)
    assert s.count(end) == 1, "segment end not unique: " + end[:90]
    old = s[i:j]
    for m in must_have:
        assert m in old, "segment %r lacks %r" % (start[:50], m[:80])
    s = s[:i] + new + s[j:]


# ---------------- docstring + version ----------------
rep('"""SkyySacks 0.7.5 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.5.py            -> SkyySacks/SkyySacks-0.7.5.jar' + LF
    + '       python build_skyysacks_0.7.5.py --deploy   -> also',
    '"""SkyySacks 0.7.6 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.6.py            -> SkyySacks/SkyySacks-0.7.6.jar' + LF
    + '       python build_skyysacks_0.7.6.py --deploy   -> also')
rep('(GrantTask / SackReady) is gone from the source; the two longest wrapped texts of the how-to-craft view have room for three lines.' + LF
    + '"""' + LF,
    '(GrantTask / SackReady) is gone from the source; the two longest wrapped texts of the how-to-craft view have room for three lines.' + LF
    + '0.7.6 (derived from 0.7.5 by tools/sacks_0_7_6_patch.py - edit the patch, not this file): IN-GAME SERVER SETUP + PLAYER SETTINGS -' + LF
    + 'the admin config kit (tools/skyycfg.py): SkyyMenu 0.3 Server Setup -> "Bags and Crafting" edits Skyy_SkyySacks/config.properties' + LF
    + '(node skyysacks.admin): craftSearch (live, reload:SackCfg.reload) plus the Small / Medium / Large bag caps (advanced, confirm) and' + LF
    + 'the Furnace / Tannery queue, fuel and output caps (advanced), all live; SackCfg.reload() loads every key and clamps like the rows.' + LF
    + 'A bag change that would break Small <= Medium <= Large asks first (SackCfg.checkTierOrder; never refuses, ignored on import).' + LF
    + 'Player Settings: sacks.benchDone / sacks.benchFuel gate only the two ProcTask chat lines (log line and fuel latch unchanged).' + LF
    + 'Defaults = 0.7.5, so nothing changes until an admin or a player changes something.' + LF
    + '"""' + LF)
rep('VERSION = "0.7.5"', 'VERSION = "0.7.6"')
rep('import skyybuild as B' + LF + 'import json' + LF,
    'import skyybuild as B' + LF + 'import skyycfg as CFG   # 0.7.6: the admin config kit (research/Server-Setup-Spec.md 4.12, tools/CONFIG-CONTRACT.md)' + LF
    + 'import json' + LF)

# ---------------- the config table + template (python, before any class uses it) ----------------
CFG_TABLE = r'''# 0.7.6: THE CAPS TABLE - one source for the public static volatile fields (initial values), the admin config rows (defaults, bounds)
# and SackCfg.reload's clamps, so the file, the page and the running values cannot disagree. Defaults = the 0.7.5 constants (the bag caps
# are Skyy's locked 640 / 2,240 / 20,160). (file key = row key, Java field, default, min, max)
SACK_CAPS = [
    ("bag.small",        "SackDefs.CAP_SMALL",   640, 1, 1000000),
    ("bag.medium",       "SackDefs.CAP_MEDIUM", 2240, 1, 1000000),
    ("bag.large",        "SackDefs.CAP_LARGE", 20160, 1, 1000000),
    ("bench.queueCap",   "ProcBench.QUEUE_CAP",  256, 1, 10000),
    ("bench.fuelCap",    "ProcBench.FUEL_CAP",  1000, 1, 100000),
    ("bench.outputCap",  "ProcBench.OUT_CAP",  20000, 1, 1000000),
]
CAPD = dict((k, d) for (k, _f, d, _lo, _hi) in SACK_CAPS)
assert (CAPD["bag.small"], CAPD["bag.medium"], CAPD["bag.large"]) == (640, 2240, 20160), "the bag caps are locked design numbers"
# Skyy_SkyySacks/config.properties as SackCfg.reload writes it when it is missing (= the kit's DEFAULTS text). The first four lines are the
# 0.7.5 file; the six caps are commented template lines the kit uncomments in place when an admin changes one (a 0.7.5 file without them
# gets the changed line appended under the kit's "changed in game" header). Doc comments carry no "=" so nothing mistakes them for a key.
SACK_CFG_LINES = [
    "# SkyySacks settings - re-read about every 10 seconds when this file changes (no restart and no rebuild needed).",
    "# craftSearch=false removes the search box from the /craft page (use it if the craft page stops opening on your client).",
    "# /craft followed by words still searches when the box is off.",
    "craftSearch=true",
    "# Admins can also change these in game: SkyWynn Menu -> Server Setup -> Bags and Crafting (permission skyysacks.admin).",
    "# Advanced - remove the # in front of a line to change it. Bag caps: the most of EACH item a Small / Medium / Large bag holds",
    "# (the best bag a player carries counts). Lowering one never deletes pooled items, it only stops new ones going in.",
    "# The bag item tooltips keep the built-in numbers (640 / 2,240 / 20,160).",
] + ["#%s=%d" % (k, d) for (k, _f, d, _lo, _hi) in SACK_CAPS[:3]] + [
    "# Furnace and Tannery (each player has their own): queue size in units, fuel slot size in items, output held before it pauses.",
] + ["#%s=%d" % (k, d) for (k, _f, d, _lo, _hi) in SACK_CAPS[3:]]
SACK_CFG_TEXT = "".join(l + chr(10) for l in SACK_CFG_LINES)
def _jcfg_txt():
    """The template as a Java expression: "line" + nl + "line" + nl ... (nl = System.lineSeparator(), as in 0.7.3-0.7.5)."""
    out = []
    for l in SACK_CFG_LINES:
        assert '"' not in l and "\\" not in l, l
        out.append('"%s" + nl' % l)
    return (chr(10) + "        + ").join(out)
def _jfield(k):
    for (fk, f, d, lo, hi) in SACK_CAPS:
        if fk == k:
            return f, d, lo, hi
    raise KeyError(k)
'''
rep(LF + 'PKG = "com.skyy.sacks"' + LF, LF + CFG_TABLE + LF + 'PKG = "com.skyy.sacks"' + LF)

# ---------------- ProcBench caps: public static volatile, declared right after the classes exist (SackCfg.reload writes them) ----------------
rep('pl   = pool.makeClass(PKG + ".SkyySacksPlugin", pool.get(JP))' + LF,
    'pl   = pool.makeClass(PKG + ".SkyySacksPlugin", pool.get(JP))' + LF
    + '# 0.7.6: the Furnace / Tannery caps are admin settings (bench.queueCap / bench.fuelCap / bench.outputCap, SACK_CAPS): public static' + LF
    + '# volatile (the config kit writes them with Field.setInt), declared here, before SackCfg.reload() - their loader - is compiled.' + LF
    + 'for (_k, _f, _d, _lo, _hi) in SACK_CAPS:' + LF
    + '    if _f.startswith("ProcBench."):' + LF
    + '        pben.addField(CtField.make("public static volatile int %s = %d;" % (_f.split(".")[1], _d), pben))' + LF)
rep('pben.addField(CtField.make("public static final int QUEUE_CAP = 256;", pben))' + LF
    + 'pben.addField(CtField.make("public static final int FUEL_CAP = 1000;", pben))' + LF
    + 'pben.addField(CtField.make("public static final int OUT_CAP = 20000;", pben))' + LF,
    '# 0.7.6: QUEUE_CAP / FUEL_CAP / OUT_CAP are declared right after the classes are made (public static volatile, admin settings)' + LF)

# ---------------- SackDefs: bag caps from volatile fields ----------------
rep('''defs.addMethod(CtNewMethod.make("""
public static int tierCap(String tier) {
  if (tier.equals("Small")) return 640;
  if (tier.equals("Medium")) return 2240;
  if (tier.equals("Large")) return 20160;
  return 0;
}""", defs))''',
    '''# 0.7.6: the bag caps are admin settings (bag.small / bag.medium / bag.large, SACK_CAPS): public static volatile, read on every sweep,
# so a change applies at once. Lowering one never deletes pooled items (SweepTask only stops intake at the cap; withdraw ignores it).
for (_k, _f, _d, _lo, _hi) in SACK_CAPS:
    if _f.startswith("SackDefs."):
        defs.addField(CtField.make("public static volatile int %s = %d;" % (_f.split(".")[1], _d), defs))
defs.addMethod(CtNewMethod.make("""
public static int tierCap(String tier) {
  if (tier.equals("Small")) return CAP_SMALL;
  if (tier.equals("Medium")) return CAP_MEDIUM;
  if (tier.equals("Large")) return CAP_LARGE;
  return 0;
}""", defs))''')

# ---------------- SackPool: settings registry helpers (Settings-Spec 1.3 / 3.4) ----------------
rep('''sp.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  Object b = System.getProperties().get("skyy.bridge");
  if (b instanceof java.util.Map) return (java.util.Map) b;
  return java.util.Collections.EMPTY_MAP;
}""", sp))
''',
    '''sp.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  Object b = System.getProperties().get("skyy.bridge");
  if (b instanceof java.util.Map) return (java.util.Map) b;
  return java.util.Collections.EMPTY_MAP;
}""", sp))
# 0.7.6 player Settings (SkyyMenu 0.2+, research/Settings-Spec.md 1.3 / 3.4). bridge() above stays read-only (EMPTY_MAP when absent), so
# regSetting uses a CREATING bridgeW() (the SkillStore.bridge / CfgRows.bridge pattern). No SkyyMenu = no answer = ON (0.7.5 behaviour).
sp.addMethod(CtNewMethod.make("""
public static java.util.Map bridgeW() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static boolean notifyOn(java.util.UUID u, String key) {
  if (u == null || key == null) return true;
  try {
    Object f = bridge().get("settings:fn:get");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  return true;
}""", sp))
sp.addMethod(CtNewMethod.make("""
public static void regSetting(String key, String label, String cat, boolean def, String help) {
  try {
    Object[] a = new Object[] { "SkyySacks", key, label, cat, Boolean.valueOf(def), help };
    java.util.Map br = bridgeW();
    br.put("settings:def:" + key, a);
    Object f = br.get("settings:fn:register");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { }
}""", sp))
''')

# ---------------- SackCfg: the one loader of every config key ----------------
NEW_SCFG = r'''# 0.7.6: SackCfg.reload() is also the admin config kit's RELOAD (hand edits) and the reload routine of the craftSearch row; it loads every
# key (craftSearch + the six SACK_CAPS) and clamps a file value to the row bounds (typed values are refused by the kit, never clamped).
# It writes the file only when it is missing (the template above); the kit owns every other write (line-preserving, logged, versioned).
scfg.addField(CtField.make("public static java.nio.file.Path FILE;", scfg))
scfg.addField(CtField.make("public static long MTIME = -1L;", scfg))
scfg.addField(CtField.make("public static boolean WARNED = false;", scfg))
scfg.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicBoolean SEARCH = new java.util.concurrent.atomic.AtomicBoolean(true);", scfg))
# a whole number from the file ("1,000" and "1_000" read as 1000); missing = the default; not a number = the default + one warning per
# file change; out of range = clamped to the bound + one warning (the kit also logs it status=clamped)
scfg.addMethod(CtNewMethod.make("""
public static int intKey(java.util.Properties p, String k, int def, int lo, int hi) {
  String v0 = p.getProperty(k);
  if (v0 == null) return def;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < v0.length(); i++) {
    char c = v0.charAt(i);
    if (c == ',' || c == '_' || c == ' ' || c == '\\t') continue;
    sb.append(c);
  }
  String v = sb.toString();
  if (v.length() == 0) return def;
  long n = 0L;
  try { n = Long.parseLong(v); }
  catch (Throwable t) { com.skyy.sacks.SackPool.warn("config.properties: " + k + "=" + v0.trim() + " is not a whole number - using " + def); return def; }
  if (n < (long) lo) { com.skyy.sacks.SackPool.warn("config.properties: " + k + "=" + v + " is below " + lo + " - using " + lo); return lo; }
  if (n > (long) hi) { com.skyy.sacks.SackPool.warn("config.properties: " + k + "=" + v + " is above " + hi + " - using " + hi); return hi; }
  return (int) n;
}""", scfg))
scfg.addMethod(CtNewMethod.make("""
public static synchronized void reload() {
  try {
    if (FILE == null) return;
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
      String nl = System.lineSeparator();
      String txt = @TXT@;
      // review fix: tmp + fsync + atomic rename (ProcStore.save pattern), so a crash mid-write never leaves a truncated config.properties
      java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp");
      java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
      try { out.write(txt.getBytes("UTF-8")); out.flush(); out.getFD().sync(); } finally { out.close(); }
      try { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }); }
      catch (Throwable am) { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
    }
    long mt = java.nio.file.Files.getLastModifiedTime(FILE, new java.nio.file.LinkOption[0]).toMillis();
    if (mt == MTIME) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    boolean on = !"false".equalsIgnoreCase(p.getProperty("craftSearch", "true").trim());
    int cs = intKey(p, "bag.small", @D:bag.small@);
    int cm = intKey(p, "bag.medium", @D:bag.medium@);
    int cl = intKey(p, "bag.large", @D:bag.large@);
    int qc = intKey(p, "bench.queueCap", @D:bench.queueCap@);
    int fc = intKey(p, "bench.fuelCap", @D:bench.fuelCap@);
    int oc = intKey(p, "bench.outputCap", @D:bench.outputCap@);
    boolean first = MTIME < 0L;
    MTIME = mt;
    WARNED = false;
    if (first || on != SEARCH.get()) {
      try { if (com.skyy.sacks.SackPool.LOG != null) com.skyy.sacks.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: craft page search box " + (on ? "ON" : "OFF") + " (" + FILE + ")"); } catch (Throwable t2) { }
    }
    boolean capsChanged = cs != com.skyy.sacks.SackDefs.CAP_SMALL || cm != com.skyy.sacks.SackDefs.CAP_MEDIUM || cl != com.skyy.sacks.SackDefs.CAP_LARGE
      || qc != com.skyy.sacks.ProcBench.QUEUE_CAP || fc != com.skyy.sacks.ProcBench.FUEL_CAP || oc != com.skyy.sacks.ProcBench.OUT_CAP;
    SEARCH.set(on);
    com.skyy.sacks.SackDefs.CAP_SMALL = cs;
    com.skyy.sacks.SackDefs.CAP_MEDIUM = cm;
    com.skyy.sacks.SackDefs.CAP_LARGE = cl;
    com.skyy.sacks.ProcBench.QUEUE_CAP = qc;
    com.skyy.sacks.ProcBench.FUEL_CAP = fc;
    com.skyy.sacks.ProcBench.OUT_CAP = oc;
    if (capsChanged) {
      try { if (com.skyy.sacks.SackPool.LOG != null) com.skyy.sacks.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: bag caps (of each item) Small " + cs + ", Medium " + cm + ", Large " + cl + "; Furnace / Tannery queue " + qc + " units, fuel " + fc + ", output " + oc); } catch (Throwable t3) { }
    }
  } catch (Throwable t) {
    if (!WARNED) { WARNED = true; com.skyy.sacks.SackPool.warn("could not read " + FILE + " - keeping craftSearch=" + SEARCH.get() + " and the current caps: " + t); }
  }
}""".replace("@TXT@", _jcfg_txt())
   .replace("@D:bag.small@", "%d, %d, %d" % _jfield("bag.small")[1:])
   .replace("@D:bag.medium@", "%d, %d, %d" % _jfield("bag.medium")[1:])
   .replace("@D:bag.large@", "%d, %d, %d" % _jfield("bag.large")[1:])
   .replace("@D:bench.queueCap@", "%d, %d, %d" % _jfield("bench.queueCap")[1:])
   .replace("@D:bench.fuelCap@", "%d, %d, %d" % _jfield("bench.fuelCap")[1:])
   .replace("@D:bench.outputCap@", "%d, %d, %d" % _jfield("bench.outputCap")[1:]), scfg))
# review fix (0.7.6): the check= hook of the three bag rows. A change that would break Small <= Medium <= Large is never refused, it only
# swaps the row's usual danger question for this one (the /craft upgrade text would advertise a Medium -> Large "upgrade" that lowers the
# cap; gameplay stays right because the best bag carried counts). The kit ignores a "?" answer on import / restore, so a code that raises
# Medium and Large together never depends on the order of its lines. value = the kit's canonical whole number.
scfg.addMethod(CtNewMethod.make("""
public static String fmtN(long n) {
  return java.text.NumberFormat.getIntegerInstance(java.util.Locale.US).format(n);
}""", scfg))
scfg.addMethod(CtNewMethod.make("""
public static String checkTierOrder(String key, String value) {
  if (key == null || value == null) return null;
  int n = 0;
  try { n = Integer.parseInt(value.trim()); } catch (Throwable t) { return null; }
  int s = com.skyy.sacks.SackDefs.CAP_SMALL;
  int m = com.skyy.sacks.SackDefs.CAP_MEDIUM;
  int l = com.skyy.sacks.SackDefs.CAP_LARGE;
  String tier = null;
  int old = 0;
  if (key.equals("bag.small")) { tier = "Small"; old = s; s = n; }
  else if (key.equals("bag.medium")) { tier = "Medium"; old = m; m = n; }
  else if (key.equals("bag.large")) { tier = "Large"; old = l; l = n; }
  else return null;
  if (s <= m && m <= l) return null;
  return "?Bags would be out of order (Small " + fmtN((long) s) + ", Medium " + fmtN((long) m) + ", Large " + fmtN((long) l)
    + "): an upgrade would lower the cap. Change the " + tier + " bag from " + fmtN((long) old) + " to " + fmtN((long) n) + " anyway?";
}""", scfg))

'''
seg('scfg.addField(CtField.make("public static java.nio.file.Path FILE;", scfg))' + LF,
    '# ================= Processing (0.7.0): timed Furnace / Tannery queues',
    ['public static synchronized void reload() {', 'craftSearch=true', 'SEARCH.set(on);'],
    NEW_SCFG)

# ---------------- ProcTask: gate only the two chat lines ----------------
rep('''        String[] ds = pb.describe(0, true);
        pr.sendMessage({MSG}.raw("[SkyySacks] Your " + pb.bench + " is done. " + ds[3] + " - open /craft to collect."));
        {PKG}.CraftLog.line(k, "DONE " + pb.bench + " queue finished - " + ds[3]);
      }} else if (pb.fuelWarnOnce()) {{
        pr.sendMessage({MSG}.raw("[SkyySacks] Your " + pb.bench + " ran out of fuel - load more in /craft."));
      }}''',
    '''        String[] ds = pb.describe(0, true);
        // 0.7.6 player setting sacks.benchDone hides only this line; the DONE log line below always runs
        if ({PKG}.SackPool.notifyOn(u, "sacks.benchDone")) pr.sendMessage({MSG}.raw("[SkyySacks] Your " + pb.bench + " is done. " + ds[3] + " - open /craft to collect."));
        {PKG}.CraftLog.line(k, "DONE " + pb.bench + " queue finished - " + ds[3]);
      }} else if (pb.fuelWarnOnce()) {{
        // 0.7.6 player setting sacks.benchFuel: the fuelWarnOnce() latch above is used either way, so a hidden warning is not replayed
        if ({PKG}.SackPool.notifyOn(u, "sacks.benchFuel")) pr.sendMessage({MSG}.raw("[SkyySacks] Your " + pb.bench + " ran out of fuel - load more in /craft."));
      }}''')

# ---------------- the admin config kit, emitted before the plugin (setup() calls CfgPub) ----------------
KIT_BLOCK = r'''# ================= 0.7.6 admin config kit (research/Server-Setup-Spec.md 4.12, tools/CONFIG-CONTRACT.md) =================
# Skyy_SkyySacks/config.properties stays the file and craftSearch keeps its key. SkyyMenu 0.3 Server Setup lists it as "Bags and Crafting";
# every change is validated, logged (Skyy_SkyySacks/config-changes.log), versioned (config-history) and written line by line. The bound
# fields exist above (SackDefs.CAP_*, ProcBench.*_CAP); SackCfg.reload is the RELOAD (hand edits) and the craftSearch reload routine.
_CAP_ROW = {
    "bag.small":       ("Small bag: most of each item", "bags", "live,adv,danger",
                        "Most of EACH item a Small bag holds. Lowering never deletes pooled items, it only stops intake."),
    "bag.medium":      ("Medium bag: most of each item", "bags", "live,adv,danger",
                        "Most of each item a Medium bag holds (the best bag carried counts). Lowering only stops intake."),
    "bag.large":       ("Large bag: most of each item", "bags", "live,adv,danger",
                        "Most of each item a Large bag holds. Item tooltips keep saying 20,160. Lowering only stops intake."),
    "bench.queueCap":  ("Queue size (units)", "benches", "live,adv",
                        "Most units one player's Furnace or Tannery queue holds. Lowering keeps what is queued."),
    "bench.fuelCap":   ("Fuel slot size (items)", "benches", "live,adv",
                        "Most fuel items one player's bench fuel slot holds. Lowering keeps the fuel already loaded."),
    "bench.outputCap": ("Output held before pausing", "benches", "live,adv",
                        "Output a Furnace or Tannery keeps before it pauses until the player collects. Nothing is lost."),
}
SACK_CFG_CATS = [("craft", "Craft page"), ("bags", "Bags"), ("benches", "Furnace and Tannery")]
SACK_CFG_ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
    ("craftSearch", "Search box on /craft", "craft", "bool", "true", "", "", "", "", "live",
     "Off hides the search box on /craft (for clients that cannot open it). /craft <words> still searches.",
     "reload:SackCfg.reload@config.properties:craftSearch"),
] + [(k, _CAP_ROW[k][0], _CAP_ROW[k][1], "int", str(d), str(lo), str(hi), "", "", _CAP_ROW[k][2], _CAP_ROW[k][3],
      "field:%s@config.properties:%s%s" % (f, k, ";check=SackCfg.checkTierOrder" if k.startswith("bag.") else ""))
     for (k, f, d, lo, hi) in SACK_CAPS]
# review fix: the bag rows ask before an order-breaking change (SackCfg.checkTierOrder; asks, never refuses, ignored on import)
kit = CFG.emit(pool, PKG, MOD="SkyySacks", TITLE="Bags and Crafting", VERSION=VERSION, NODE="skyysacks.admin", CATS=SACK_CFG_CATS,
               ROWS=SACK_CFG_ROWS, FILES=["Skyy_SkyySacks/config.properties"],
               NOTE="Hand edits of the file are also picked up by themselves within about 10 seconds.",
               RELOAD="SackCfg.reload", KEEP=20, DEFAULTS={"config.properties": SACK_CFG_TEXT})
print("config kit: %d rows, files %s" % (kit.info["rows"], ", ".join(kit.info["files"])))

'''
rep(LF + '# ================= plugin =================' + LF, LF + KIT_BLOCK + '# ================= plugin =================' + LF)

# ---------------- plugin setup(): settings + config publication at the END; shutdown(): flush the kit ----------------
rep('''storage per profile (pkey)");
}}""", pl))''',
    '''storage per profile (pkey); settings: SkyWynn Menu -> Server Setup -> Bags and Crafting (skyysacks.admin) or Skyy_SkyySacks/config.properties");
  // 0.7.6 player Settings (research/Settings-Spec.md 2.2 / 3.4): every switch registered here, default ON
  {PKG}.SackPool.regSetting("sacks.benchDone", "Furnace and Tannery done", "sacks", true, "Your Furnace is done - open /craft to collect");
  {PKG}.SackPool.regSetting("sacks.benchFuel", "Furnace out of fuel", "sacks", true, "Your Furnace ran out of fuel - once until you add more");
  // 0.7.6 admin config (tools/CONFIG-CONTRACT.md): config:def:SkyySacks + config:fn:SkyySacks, last, after SackCfg.reload() loaded the file
  {PKG}.CfgPub.start(getDataDirectory().getParent(), getLogger());
}}""", pl))''')
rep('''  try {{ {PKG}.CraftLog.drain(); }} catch (Throwable t) {{ }}
  super.shutdown();''',
    '''  try {{ {PKG}.CraftLog.drain(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CfgPub.shutdown(); }} catch (Throwable t) {{ }}
  super.shutdown();''')
rep('print("classes written")' + LF,
    'kit.write(OUT)   # 0.7.6: deferred kit checks (SackCfg.reload exists, public static), then the 7 kit classes' + LF
    + 'print("classes written (+ %d config kit classes)" % len(kit.classes))' + LF)
# the lang descriptions keep the locked numbers: tie them to the table so a changed default cannot drift from the tooltip text
rep('        caps = {"Small": 640, "Medium": 2240, "Large": 20160}[tier]' + LF,
    '        caps = {"Small": CAPD["bag.small"], "Medium": CAPD["bag.medium"], "Large": CAPD["bag.large"]}[tier]' + LF)

# ================= self-checks =================
assert 'VERSION = "0.7.6"' in s and 'VERSION = "0.7.5"' not in s
assert "public static final int QUEUE_CAP" not in s and "public static final int FUEL_CAP" not in s and "public static final int OUT_CAP" not in s
assert "return 640;" not in s and "return 2240;" not in s and "return 20160;" not in s
# javassist: no forward references - fields before the methods that use them, helpers before callers, kit before the plugin
i_pbcap = s.index('pben.addField(CtField.make("public static volatile int %s = %d;"')
i_defcap = s.index('defs.addField(CtField.make("public static volatile int %s = %d;"')
i_tier = s.index("public static int tierCap(String tier) {")
i_intkey = s.index("public static int intKey(java.util.Properties p, String k, int def, int lo, int hi) {")
i_reload = s.index("public static synchronized void reload() {")
assert i_pbcap < i_reload and i_defcap < i_tier < i_reload and i_intkey < i_reload
# review fix: the bag-order check= hook (asks, never refuses) exists after the bag fields and after its fmtN helper, bound to the bag rows only
i_fmt = s.index("public static String fmtN(long n) {")
i_ord = s.index("public static String checkTierOrder(String key, String value) {")
assert i_defcap < i_fmt < i_ord and s.count("public static String checkTierOrder(") == 1
assert s.count(';check=SackCfg.checkTierOrder" if k.startswith("bag.") else ""') == 1
i_bridge = s.index("public static java.util.Map bridge() {")
i_bw = s.index("public static java.util.Map bridgeW() {")
i_no = s.index("public static boolean notifyOn(java.util.UUID u, String key) {")
i_rs = s.index("public static void regSetting(String key, String label, String cat, boolean def, String help) {")
assert i_bridge < i_bw < i_rs and i_bridge < i_no
i_ptk = s.index("# ================= ProcTask (world thread")
assert i_no < i_ptk
i_kit = s.index("kit = CFG.emit(pool, PKG, MOD=\"SkyySacks\"")
i_pl = s.index("# ================= plugin =================")
i_setup = s.index("public void setup() {{", i_pl)
assert i_reload < i_kit < i_pl < i_setup
assert s.index("c.writeFile(OUT)", i_pl) < s.index("kit.write(OUT)") < s.index("# ================= assets =================")
# setup(): regSetting for both switches, CfgPub.start the LAST statement, after SackCfg.reload()
_setup = s[i_setup:s.index('}}""", pl))', i_setup)]
assert _setup.index("{PKG}.SackCfg.reload();") < _setup.index("{PKG}.CfgPub.start(")
assert _setup.rstrip().endswith("{PKG}.CfgPub.start(getDataDirectory().getParent(), getLogger());")
assert _setup.count("regSetting(") == 2 and '"sacks.benchDone"' in _setup and '"sacks.benchFuel"' in _setup
assert s.count("{PKG}.CfgPub.shutdown();") == 1
# gates: exactly the two sends, the log line and the latch unconditional
assert s.count('{PKG}.SackPool.notifyOn(u, "sacks.benchDone")') == 1 and s.count('{PKG}.SackPool.notifyOn(u, "sacks.benchFuel")') == 1
assert "      }} else if (pb.fuelWarnOnce()) {{" + LF in s
assert "        {PKG}.CraftLog.line(k, \"DONE \" + pb.bench + \" queue finished - \" + ds[3]);" + LF in s
# every 0.7.5 profile / busy / UI rule untouched
assert s.count("public static String settledKey(java.util.UUID u) {") == 1, "settledKey changed"
assert 'b.get("profile:busy:" + u.toString()) != null) return null;' in s, "busy gate lost"
import re as _re
for m in _re.finditer(r"#(SkyyS[A-Za-z0-9_]*)", s):
    assert "_" not in m.group(1), "UI id with underscore: " + m.group(1)
assert "Group #SkyySacks {{ Anchor: (Width: 1000, Height: 600);" in s
assert "cp.live(" not in s and "public void live(" not in s, "periodic refresh came back"

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
