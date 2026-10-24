"""wc15 - WEAPONCRAFT x1.5 (2026-10-24, round wc15: SkyyGear 0.3.45 + SkyyMobs 0.1.19 + SkyyClasses 0.1.48). Owner: Skyy (they/them).

WHY (docs/answered/classes.md 2026-10-23 CLASS TREE REBUILD BUILT): "Weaponcraft (old Combat) per-rank numbers to be raised ~x1.5 in a
follow-up Gear / Mobs / Pets / Accessories balance round (they give ~40-47 % of their old share at Lv 50 at 1 point a level)". Skyy
2026-10-24: "dont worry about usage, work through your whole list". The class tree rebuild (SkyyTrees 0.6.0) folded the Combat skill tree
into every class's third branch "Weaponcraft": 1 point a class level now buys class AND Combat ranks, so an even build owns 28-34 % of
the class tree at Lv 50 (python tools/balance_model.py --p10) where the old Combat skill owned 50 of its 70 live ranks (71 %).

WHAT: the per-rank number (and its ceiling = per x max rank x top count, tools/trees_v3_effects.py natural()) of every Weaponcraft row
that THIS round's mods apply and that no budget / cap holds back, x1.5 (ROWS): SkyyGear 5 (Hone Edge, Weak Spot, Crit Mastery, Gear
Resonance, Weapon Tempering), SkyyMobs 5 (Scavenger, Coin Purse, Rare Drop, Boss Hunter, Lucky Kill), SkyyClasses 3 (Iron Will, Thick Skin,
Reprisal). HELD (not raised, until Skyy answers): Accessory Plates (SkyyAccessories: Weaponcraft max Health 10 -> 13.75 % > TREE_HP_MAX
10 %), the SkyyClasses hit rows (Combat Focus, Finisher, Trophy Hunter, Edge of the Legend: 34 -> 51 % > dmgCap 40) and Second Wind
(15 -> 22.5 % > its 20 % limit). Rows of other builders' mods are not here: Pet Fang (SkyyPets, round bm1, held at x1.3 by TREE_XP_MAX),
Toughness / Momentum (SkyyTrees), Rally / Battle Insight (SkyySkills). So 14 of the branch's 24 rows move (13 here + Fang): an even
build's raised rows give ~60-70 % of their old Lv 50 share (40-47 % x 1.5), the rest stay at 40-47 %.
Numbers SkyyGear applies to whole-% stats round half up (Math.round in combat0 / weaponInto, unchanged): Crit Mastery rank 1 = 5, rank 3 =
14; Weapon Tempering rank 1 on 1 step = 2.

HOW (no shared-table edit while other builders import tools/trees_v3_effects.py): each build script calls apply(V3E, "<Mod>") right after
its `import trees_v3_effects`; apply() swaps that mod's rows in the in-memory EFFECTS list (old -> new; a row already new is left alone, so
once the main session folds these numbers into tools/trees_v3_effects.py apply() is a no-op), re-runs V3E.check() (every tree budget), and
appends the run-once MARK to that mod's fresh trees.properties text (cfg_text). Everything the build generates from the table (built-in
numbers, Server Setup rows + help, the seeded file) then carries the new numbers. An existing Skyy_<Mod>/trees.properties is updated ONCE by
java() (PROJECT-RULES 4): only a line still holding the old default moves (a custom value is kept + logged), History copy verified first,
one change-log line per moved line (Undo in Server Setup -> Changes), the marker last, bytes + line endings kept. A missing line = the new
built-in number (nothing to do).

FOLLOW-UP for the main session (not this round's files): fold ROWS' NEW numbers into tools/trees_v3_effects.py EFFECTS (then apply() is a
no-op); the /tree page texts in tools/trees_v3_data.py (bm1's SkyyTrees file) for the 13 rows + a SkyyTrees rebuild in the same set ("(rounded
to whole %)" on Crit Mastery / Weapon Tempering); the balance_model.py P10 OPEN row text ("per-rank numbers are unchanged"); INDEX.md
entries for tools/wc15.py + tools/wc15_harness.py; HELD rows only after Skyy's answer (budget lift in trees_v3_effects.py + model row).
"""

# (tree, branch, id, effect, OLD per rank, NEW per rank) in EFFECT units (trees_v3_effects.py); the OLD = the 0.3.44 / 0.1.18 / 0.5.32 default
ROWS = {
    "SkyyGear": [
        ("Combat", 1, "r1a", "dmg", 2.0, 3.0),          # Hone Edge: +2 -> +3 % weapon damage a rank (5 ranks: 10 -> 15)
        ("Combat", 1, "r1b", "cc", 2.0, 3.0),           # Weak Spot: +2 -> +3 % crit chance a rank (3: 6 -> 9)
        ("Combat", 1, "r4a", "cd", 3.0, 4.5),           # Crit Mastery: +3 -> +4.5 % crit damage a rank (3: 9 -> 13.5)
        ("Combat", 1, "r4b", "dmg", 2.0, 3.0),          # Gear Resonance: +2 -> +3 % damage a rank per combat armor piece (3 x 4: 24 -> 36)
        ("Combat", 1, "r5b", "dmg", 1.0, 1.5),          # Weapon Tempering: +1 -> +1.5 % a rank per weapon step over Iron (4 x 5: 20 -> 30)
    ],
    "SkyyMobs": [
        ("Combat", 3, "r1a", "drop", 2.0, 3.0),         # Scavenger: 2 -> 3 % a rank, 1 more loot item (5: 10 -> 15)
        ("Combat", 3, "r1b", "coins", 3.0, 4.5),        # Coin Purse: 3 -> 4.5 % a rank, a kill pays coins (3: 9 -> 13.5)
        ("Combat", 3, "r3b", "rare", 1.0, 1.5),         # Rare Drop: 1 -> 1.5 % a rank, 1 more rarest item (3: 3 -> 4.5)
        ("Combat", 3, "r4a", "bossRoll", 3.0, 4.5),     # Boss Hunter: 3 -> 4.5 % a rank, boss loot again (3: 9 -> 13.5)
        ("Combat", 3, "r5a", "dbl", 2.0, 3.0),          # Lucky Kill: 2 -> 3 % a rank, double loot (3: 6 -> 9)
    ],
    "SkyyClasses": [   # fixer 2 (critic 3 finding 3): the SkyyClasses Weaponcraft rows that no cap holds back
        ("Combat", 2, "r1b", "kbRes", 3.0, 4.5),        # Iron Will: 3 -> 4.5 % knockback resistance a rank (3: 9 -> 13.5)
        ("Combat", 2, "r3a", "drAll", 2.0, 3.0),        # Thick Skin: 2 -> 3 % damage reduction a rank (4: 8 -> 12; the class-tree sum stays under drCap 35)
        ("Combat", 2, "r3b", "thorns", 3.0, 4.5),       # Reprisal: 3 -> 4.5 % of a melee hit taken dealt back a rank (3: 9 -> 13.5; model row <= 15)
    ],
}
# HELD until Skyy answers (fixer 2, critic 3 finding 2): x1.5 would break a budget the spec set (research/Combat-Into-Class-Spec.md 7 +
# tools/trees_v3_effects.py check(); the same care bm1 took holding Pet Fang inside TREE_XP_MAX). apply() refuses a HELD mod. To ship one:
# Skyy's yes -> move the row into ROWS (+ VERSIONS) and lift the budget in trees_v3_effects.py + the balance_model.py row together.
HELD = {
    "SkyyAccessories": [
        ("Combat", 2, "r4a", "hpp", 0.005, 0.0075),     # Accessory Plates 0.5 -> 0.75 %: Weaponcraft max Health 10 -> 13.75 % > TREE_HP_MAX 10 %
    ],
    "SkyyClasses": [
        ("Combat", 1, "r1.free", "dmg", 3.0, 4.5),      # Combat Focus / Finisher / Trophy Hunter / Edge: the hit rows sum 34 -> 51 > dmgCap 40
        ("Combat", 1, "r3a", "dmgLow", 4.0, 6.0),
        ("Combat", 1, "r5a", "dmgBoss", 3.0, 4.5),
        ("Combat", 1, "r6", "dmgLow", 10.0, 15.0),
        ("Combat", 2, "r3c", "lowHeal", 5.0, 7.5),      # Second Wind 15 -> 22.5 % > its 20 % limit (balance_model P10 row)
    ],
}
X = 1.5
VERSIONS = {"SkyyGear": "0.3.45", "SkyyMobs": "0.1.19", "SkyyClasses": "0.1.48"}
MARK_ID = "wc15 Weaponcraft x1.5"


def mark(mod):
    """the run-once marker line (a comment; plain ASCII, no backslash - cfg_text's rule)"""
    return ("# %s (%s %s, 2026-10-24): the Weaponcraft per-rank numbers are x1.5; lines still on the old default were raised once "
            "(Undo: Server Setup -> Changes)." % (MARK_ID, mod, VERSIONS[mod]))


def _row_index(V3E, r):
    hits = [i for i, e in enumerate(V3E.EFFECTS) if (e[0], e[1], e[2], e[4]) == r[:4]]
    assert len(hits) == 1, ("wc15: one EFFECTS row", r, hits)
    return hits[0]


def check_rows():
    for mod, rs in ROWS.items():
        assert mod in VERSIONS
        for r in rs:
            assert r[0] == "Combat" and abs(r[5] - r[4] * X) < 1e-12, ("wc15: x1.5", r)
    shipped = set((m, r[1], r[2], r[3]) for m, rs in ROWS.items() for r in rs)
    assert not [r for m, rs in HELD.items() for r in rs if (m, r[1], r[2], r[3]) in shipped], "wc15: a row is both shipped and HELD"


def apply(V3E, mod):
    """swap mod's Weaponcraft rows to NEW in V3E.EFFECTS (in place; a NEW row stays) + the marker on mod's fresh trees.properties text.
    Returns the number of rows swapped (0 once the shared table holds NEW)."""
    check_rows()
    assert mod in ROWS, ("wc15: %s is HELD (tools/wc15.py HELD: x1.5 would break a budget until Skyy answers) - do not build its wc15 version" % mod)
    n = 0
    for r in ROWS[mod]:
        i = _row_index(V3E, r)
        e = V3E.EFFECTS[i]
        assert e[3] == mod, ("wc15: the row's applier", e)
        if abs(e[5] - r[5]) < 1e-12:
            continue
        assert abs(e[5] - r[4]) < 1e-12, ("wc15: the row holds neither the old nor the new number", e, r)
        V3E.EFFECTS[i] = (e[0], e[1], e[2], e[3], e[4], r[5], e[6], e[7])
        n += 1
    if not getattr(V3E, "_wc15_text", None):
        V3E._wc15_text = V3E.cfg_text
        V3E._wc15_mods = set()

        def cfg_text(applier, where=None):
            t = V3E._wc15_text(applier, where)
            if applier in V3E._wc15_mods:
                t = t + mark(applier) + "\n"
            return t
        V3E.cfg_text = cfg_text
    V3E._wc15_mods.add(mod)
    for r in ROWS[mod]:
        e = V3E.EFFECTS[_row_index(V3E, r)]
        assert abs(V3E.vmax(e) - V3E.natural(e)) < 1e-12, ("wc15: no default ceiling cuts the top rank", e)
    assert MARK_ID in V3E.cfg_text(mod) and V3E.cfg_text(mod).count(MARK_ID) == 1
    V3E.check()   # fixer 2 (critic 3 finding 2): every tree budget (Health / XP / move ...) still holds with the raised rows
    return n


def _disp(V3E, eff, v):
    return V3E._n(v * V3E.unit(eff))


def mig_rows(V3E, mod):
    """[(file key, OLD text, NEW text, OLD number, NEW number)] - .per and .max of every row (display units: what the file holds)"""
    out = []
    for r in ROWS[mod]:
        e = V3E.EFFECTS[_row_index(V3E, r)]
        ck = V3E.ckey(e)
        sm = 1.0 if e[6] is None else float(e[7])
        top = V3E.maxrank(e[0], e[1], e[2]) * sm
        for suf, o, n in ((".per", r[4], r[5]), (".max", r[4] * top, r[5] * top)):
            out.append((ck + suf, _disp(V3E, r[3], o), _disp(V3E, r[3], n), float(_disp(V3E, r[3], o)), float(_disp(V3E, r[3], n))))
    return out


def _jstr(s):
    assert "\\" not in s and '"' not in s and "\n" not in s
    return '"' + s + '"'


def _jarr(xs):
    return "new String[] { %s }" % ", ".join(_jstr(x) for x in xs)


def java(V3E, mod, log_cls, info_target, warn_target):
    """(fields, methods) of the one-time trees.properties update, to add to an EXISTING class of mod AFTER the config kit's emit()
    (it calls CfgFile / CfgRows / CfgHist / CfgLog). Only the @PKG@ token is left for the mod's own token helper. Entry point:
    public static String migrateWc15(java.nio.file.Path dir) - dir = the mod's Skyy_<Mod> folder (the kit HOME); setup() calls it
    BEFORE the loader reads trees.properties (loadV3) and BEFORE CfgPub.start. Returns the INFO text ("" = nothing done)."""
    mr = mig_rows(V3E, mod)
    who = "%s %s update (wc15)" % (mod, VERSIONS[mod])
    fields = [
        "public static final String[] WC_KEY = %s;" % _jarr([m[0] for m in mr]),
        "public static final double[] WC_OLD = new double[] { %s };" % ", ".join(repr(m[3]) for m in mr),
        "public static final String[] WC_OLDT = %s;" % _jarr([m[1] for m in mr]),
        "public static final String[] WC_NEW = %s;" % _jarr([m[2] for m in mr]),
        "public static final double[] WC_NEWN = new double[] { %s };" % ", ".join(repr(m[4]) for m in mr),
        "public static final String WC_MARK = %s;" % _jstr(mark(mod)),
        "public static final String WC_MARK_ID = %s;" % _jstr(MARK_ID),
        "public static final String WC_WHO = %s;" % _jstr(who),
    ]
    methods = [
# a file number: the double, NaN for anything else (blank, words, NaN / Infinity)
r"""
public static double wcNum(String s) {
  if (s == null) return Double.NaN;
  try {
    double v = Double.parseDouble(s.trim());
    if (Double.isNaN(v) || Double.isInfinite(v)) return Double.NaN;
    return v;
  } catch (Throwable t) { return Double.NaN; }
}""",
r"""
public static boolean wcEq(double a, double b) {
  if (Double.isNaN(a) || Double.isNaN(b)) return false;
  double d = a - b;
  if (d < 0.0) d = -d;
  double m = b < 0.0 ? -b : b;
  if (m < 1.0) m = 1.0;
  return d <= 1e-9 * m;
}""",
# PURE TEXT STEP (no file access): null = the marker is already in a comment line (a fresh file carries it). Per WC_KEY: the LAST entry
# (the one java.util.Properties keeps) is rewritten when it is ONE line holding exactly the old default (value text only: key, separator
# and the line's own CR kept); a value already on the new default is quiet; any other value is kept + noted; a missing key = the new
# built-in number (nothing written). The marker line goes at the END (before the final line break; CRLF when the file uses CRLF).
# returns { new text, change count (Integer), notes String[], log rows String[] (key, old, new)..., props String[] (key, new)... }
r"""
public static Object[] wcUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  for (int i = 0; i < l.size(); i++) {
    String t0 = ((String) l.get(i)).trim();
    if ((t0.startsWith("#") || t0.startsWith("!")) && t0.indexOf(WC_MARK_ID) >= 0) return null;
  }
  java.util.Properties pp = new java.util.Properties();
  try { pp.load(new java.io.StringReader(text)); } catch (Throwable x) { }
  int nk = WC_KEY.length;
  int[] last = new int[nk];
  boolean[] one = new boolean[nk];
  for (int i = 0; i < nk; i++) last[i] = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) { k++; continue; }
    int e = @PKG@.CfgFile.end(l, k);
    String key = @PKG@.CfgFile.key(s);
    for (int i = 0; key != null && i < nk; i++) {
      if (WC_KEY[i].equals(key)) { last[i] = k; one[i] = e == k; }
    }
    k = e + 1;
  }
  int nch = 0;
  java.util.HashMap at = new java.util.HashMap();
  java.util.ArrayList notes = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  java.util.ArrayList props = new java.util.ArrayList();
  for (int i = 0; i < nk; i++) {
    String ov = pp.getProperty(WC_KEY[i]);
    if (ov == null) continue;
    double v = wcNum(ov);
    if (last[i] >= 0 && one[i] && wcEq(v, WC_OLD[i]) && wcEq(wcNum(@PKG@.CfgFile.value(l, last[i])), WC_OLD[i])) {
      at.put(Integer.valueOf(last[i]), WC_NEW[i]);
      nch++;
      rows.add(WC_KEY[i]);
      rows.add(@PKG@.CfgRows.oneLine(ov.trim()));
      rows.add(WC_NEW[i]);
      props.add(WC_KEY[i]);
      props.add(WC_NEW[i]);
    } else if (!wcEq(v, WC_NEWN[i])) {
      notes.add(WC_KEY[i] + "=" + @PKG@.CfgRows.oneLine(ov.trim()) + " kept (not the old default " + WC_OLDT[i] + ", or not one plain line) - the new default is " + WC_NEW[i]);
    }
  }
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    Object nv = at.get(Integer.valueOf(i));
    if (nv != null) {
      String s2 = (String) l.get(i);
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + (String) nv + (raw[i].endsWith("\r") ? "\r" : ""));
    } else out.add(raw[i]);
  }
  if (out.size() > 0 && ((String) out.get(out.size() - 1)).length() == 0) out.add(out.size() - 1, WC_MARK + cr);
  else {
    String lst = out.size() == 0 ? "" : (String) out.get(out.size() - 1);
    if (out.size() > 0 && cr.length() > 0 && !lst.endsWith("\r")) out.set(out.size() - 1, lst + "\r");
    out.add(WC_MARK + cr);
    out.add("");
  }
  StringBuilder sb = new StringBuilder(text.length() + 256);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), Integer.valueOf(nch), (String[]) notes.toArray(new String[0]), (String[]) rows.toArray(new String[0]), (String[]) props.toArray(new String[0]) };
}""",
# the update changes ONLY the planned keys (java.util.Properties of old + planned values == Properties of the new bytes)
r"""
public static boolean wcSame(byte[] old, byte[] nb, String[] props) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties b = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    b.load(new java.io.ByteArrayInputStream(nb));
    for (int i = 0; i + 1 < props.length; i += 2) a.setProperty(props[i], props[i + 1]);
    return a.equals(b);
  } catch (Throwable t) { return false; }
}""",
# the kit's file number of trees.properties (its History copies), -1 = none
r"""
public static int wcFile() {
  for (int k = 0; k < @PKG@.CfgRows.FILES.length; k++) {
    String f = @PKG@.CfgRows.FILES[k];
    if (f.equals("trees.properties") || f.endsWith("/trees.properties")) return k;
  }
  return -1;
}""",
# the config kit's own files, before CfgPub.start (which sets the same values again): History + change log in the kit HOME (Skyy_<Mod>)
r"""
public static void wcKit(java.nio.file.Path home) {
  @PKG@.CfgRows.HOME = home;
  if (@PKG@.CfgRows.LOG == null) @PKG@.CfgRows.LOG = @PKG@.@LOGCLS@.LOG;
  @PKG@.CfgHist.init();
  @PKG@.CfgLog.init();
}""",
# CfgHist.snapshot swallows its own errors: the copies themselves are checked (exactly these bytes - the new copy, or the newest when equal)
r"""
public static boolean wcSaved(int f, byte[] old) {
  String[] have = @PKG@.CfgHist.list(f);
  for (int i = have.length - 1; i >= 0; i--) {
    try {
      if (java.util.Arrays.equals(java.nio.file.Files.readAllBytes(@PKG@.CfgHist.bak(f, have[i])), old)) return true;
    } catch (Throwable x) { }
  }
  return false;
}""",
# one config-changes.log line in the kit's format: time, who, uuid, via, key, old, new, status (ok = Server Setup -> Changes offers Undo)
r"""
public static String wcLog(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + WC_WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + @PKG@.CfgRows.oneLine(o) + "\t" + @PKG@.CfgRows.oneLine(n) + "\tok";
}""",
r"""
public static synchronized String migrateWc15(java.nio.file.Path dir) {
  if (dir == null) return "";
  java.nio.file.Path f = dir.resolve("trees.properties");
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = wcUpdate(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    if (!wcSame(old, data, (String[]) r[4])) {
      @WARN@("trees.properties NOT updated to the Weaponcraft x1.5 numbers: the update would change another setting (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = wcFile();
    if (fi < 0) {
      @WARN@("trees.properties NOT updated to the Weaponcraft x1.5 numbers: the config kit does not list the file (the file is used as it is)");
      return "";
    }
    wcKit(dir);
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WC_WHO, "before the Weaponcraft x1.5 update (wc15)");
    if (!wcSaved(fi, old)) {
      @WARN@("trees.properties NOT updated to the Weaponcraft x1.5 numbers: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(wcLog(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    int nch = ((Integer) r[1]).intValue();
    String[] notes = (String[]) r[2];
    String msg = nch > 0
      ? "trees.properties: " + nch + " Weaponcraft lines raised x1.5 (only lines still on the old default; Undo in Server Setup -> Changes; the old file is in config-history)"
      : "trees.properties: the Weaponcraft x1.5 marker was added - no value changed";
    @INFO@(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < notes.length; i++) { @INFO@(notes[i]); all.append('\n').append(notes[i]); }
    return all.toString();
  } catch (Throwable t) {
    @WARN@("could not update trees.properties to the Weaponcraft x1.5 numbers (the file is used as it is): " + t);
    return "";
  }
}""",
    ]
    methods = [m.replace("@LOGCLS@", log_cls).replace("@INFO@", info_target).replace("@WARN@", warn_target) for m in methods]
    return fields, methods


check_rows()
