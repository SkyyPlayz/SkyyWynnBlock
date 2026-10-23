"""Derive SkyyMenu/build_skyymenu_0.3.45.py from the LIVE SkyyMenu 0.3.44 (python tools/menu_0_3_45_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_44_patch.py -> 0.3.44 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.45. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.44 (nothing else changed). Line endings kept. The harness SkyyMenu/test_skyymenu_0.3.45.py is its own file.

0.3.45 (2026-10-22) = WYNN ELEMENTS ON YOUR STATS + THE SKILL-TREE COMBAT ROWS IN THE TREES COLUMN (FULL round elem1 with SkyyMobs 0.1.17,
  SkyyGear 0.3.39, SkyyClasses 0.1.46, SkyyPets 0.4.10, SkyyAccessories 0.5.32 - pin + roll back TOGETHER). research/Wynn-Elements-Build-Spec.md
  section 9 + Skyy (docs/answered/gear.md 2026-10-18 Q7): "we can make a chart showing which elements each element is strong and weak to.
  and another showing what reactions cause what" + "work through your whole list."
  1. YOUR STATS gains three sections after Gathering (the one scroll list with headings, Menu-Pattern M4 - no new menu, no new sub-tab: the
     Skills sub-view belongs to SkyySkills):
     a) ELEMENTS: one row per element "Fire  9% / 12 Def" (damage % of your hits with the HELD weapon - weapon, charms, pets, trees, the
        weapon / charm gate applied, no Imbue - and your Defence against that element) + "Poison  20% over 10s" (gear:fn:elemTotals,
        SkyyGear 0.3.39; read once on open / Refresh, never periodic). Without it one row says which SkyyGear it needs.
     b) STRONG AND WEAK - the chart: a column header "Earth mob .. Air mob" and one row per element of yours: "+25%" (green) on the mob
        element yours beats, "-25%" (red) on its own element, "-" (dim) elsewhere; the total column "beats Air"; then the wheel line
        in words ("Earth, Thunder, Water, Fire, Air - each beats the next, Air beats Earth": the page text filter has no '>'; mob:elem:wheel), the boss rule (mob:elem:numbers, "-50%"), the exceptions (ice melts: Yeti / Frost Golems / frost skeletons weak to
        Fire). Defaults (tools/skyyelem.py) when SkyyMobs 0.1.17 is not there.
     c) REACTIONS (later): Wildfire, Shatter, Steam, Quake - "later", planned class tree nodes (Skyy Q6 "Later, as tree nodes").
     The by-source column header row takes its own labels when a row carries them (11 strings) - the old rows keep Stat | Base .. | Total.
  2. TREES COLUMN + TOTAL: SkyyGear 0.3.39's own Skill Trees 3 combat rows (Hone Edge, Weak Spot, Crit Mastery, Resonance, Weapon
     Tempering for the held weapon) arrive as gear:trees:<uuid> ("str:4,cc:3,...") and join the Trees column (with SkyyTrees' gear:extras);
     the legend's Total note now only names the Rebirth bonuses as missing.
  SAVED DATA: none. No new class / command / system.
  ROLLBACK to 0.3.44: safe alone (the sections go, the Trees column loses SkyyGear's own rows again).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import skyyelem as EL

HEAD = open(os.path.abspath(__file__), encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.45 (2026-10-22)"):].rstrip() + "\n"

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.44.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.45.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.3.44"\n') and P.has("tools/menu_0_3_44_patch.py") and not P.has("gear:fn:elemTotals"), "not the generated SkyyMenu 0.3.44 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.45: Wynn elements on Your Stats (Elements rows, the strong / weak chart, the planned reactions) + SkyyGear's own Skill Trees 3 combat rows
       in the Trees column (notes: tools/menu_0_3_45_patch.py).
  CHECKED: see SkyyMenu/test_skyymenu_0.3.45.py.
''')
P.rep('VERSION = "0.3.44"\n', 'VERSION = "0.3.45"\nimport skyyelem as EL          # 0.3.45 (elem1): the one element table (tools/skyyelem.py)\n')

# ---------- the texts (checked against the row width)
P.rep('''ST_LEGEND_TOTAL = ("Total", "the parts above; some tree and Rebirth bonuses are not counted yet")''',
      '''ST_LEGEND_TOTAL = ("Total", "the parts above; the Rebirth damage / defence bonus is not counted yet")          # 0.3.45: + SkyyGear's tree rows (gear:trees)
# 0.3.45 (elem1): the element sections (research/Wynn-Elements-Build-Spec.md 9) - texts + the chart header labels
EL_HEADS = [("Elements", "Your element damage (held weapon) and Defence."),
            ("Strong and weak", "A mob's plate shows its element - use the one that beats it."),
            ("Reactions", "Planned as class tree nodes - not in the game yet.")]
EL_COLS = ["%s mob" % _n for _n in EL.NAMES] + [""]
EL_COLH = ("Your element", "Beats")
EL_EXC = "Yeti, Frost Golems, frost skeletons + zombies: weak to Fire"          # elem1fix: = SkyyMobs 0.1.17 _ICE ("ice melts"), the only rows off the wheel
assert len("Exceptions") + len(EL_EXC) + 2 <= ST_LINE_MAX, EL_EXC
EL_NOGEAR = "needs SkyyGear 0.3.39 (element damage + Defence)"
for _h, _t in EL_HEADS:
    assert len(_h) + len(_t) + 2 <= ST_LINE_MAX, _t
assert all(SUI.text_width(_t, ST_COLH_FS) <= 150 - 8 for _t in EL_COLS), "0.3.45: a chart column head is too wide"
assert SUI.text_width(EL_COLH[0], ST_COLH_FS) <= ST_NAME_W - 8 and SUI.text_width(EL_COLH[1], ST_COLH_FS) <= ST_TOT_W - 8
for _r in EL.REACTIONS:
    assert len(_r[0]) + len("later") + len(_r[1] + ": " + _r[2]) + 2 <= ST_LINE_MAX, _r''')

# ---------- the Java tables
P.rep('''F(scl, "public static final String[] LEG_TOTAL = %s;" % jarr(list(ST_LEGEND_TOTAL)))   # fix pass: the Total caveat''',
      '''F(scl, "public static final String[] LEG_TOTAL = %s;" % jarr(list(ST_LEGEND_TOTAL)))   # fix pass: the Total caveat
# 0.3.45 (elem1): the element sections
F(scl, "public static final String[] EL_N = %s;" % jarr(EL.NAMES))
F(scl, "public static final String EL_WHEEL = %s;" % jstr(EL.WHEEL_DEF))
F(scl, "public static final String[] EL_HEAD = %s;" % jarr([_x for _h in EL_HEADS for _x in _h]))
F(scl, "public static final String[] EL_COLS = %s;" % jarr(EL_COLS + list(EL_COLH)))
F(scl, "public static final String[] EL_RX = %s;" % jarr([_x for _r in EL.REACTIONS for _x in (_r[0], _r[1] + ": " + _r[2])]))
F(scl, "public static final String EL_EXC = %s;" % jstr(EL_EXC))
F(scl, "public static final String EL_NOGEAR = %s;" % jstr(EL_NOGEAR))''')

# ---------- 2: SkyyGear's own tree rows into the Trees column
P.rep('''  java.util.HashMap m = new java.util.HashMap();
  if (u == null || !listed(br().get("tree:reads:SkyyGear"), "gear:extras")) return m;''', '''  java.util.HashMap m = new java.util.HashMap();
  if (u == null) return m;
  java.util.HashMap gt = kv(br().get("gear:trees:" + u.toString()));          // 0.3.45: SkyyGear 0.3.39's own Skill Trees 3 combat rows
  java.util.Iterator gti = gt.keySet().iterator();
  while (gti.hasNext()) { String gk = (String) gti.next(); m.put(gk, Double.valueOf(get(m, gk) + get(gt, gk))); }
  if (!listed(br().get("tree:reads:SkyyGear"), "gear:extras")) return m;''')

# ---------- 1: the element sections (before allRows calls them)
P.rep('''# 0.3.35: Your Stats = ONE scroll list - each section (Main, Combat, Gathering) = a head row {null, name, note} + its stat rows''',
      '''# 0.3.45 (elem1): the element sections - a row "Fire 9% / 12 Def" per element + Poison (gear:fn:elemTotals), the strong / weak chart
# (custom column header row: 11 strings {null, null, "", 6 labels, name label, total label}), the wheel / boss / exception lines, the reactions
M(scl, r"""
public static String elemTotals(java.util.UUID u) {
  Object f = br().get("gear:fn:elemTotals");
  if (!(f instanceof java.util.function.Function) || u == null) return null;
  try {
    Object r = ((java.util.function.Function) f).apply(u);
    return r instanceof String ? (String) r : null;
  } catch (Throwable t) { return null; }
}""")
M(scl, r"""
public static int elemIdx(String s) {
  if (s == null) return -1;
  String t = s.trim();
  for (int i = 0; i < EL_N.length; i++) if (EL_N[i].equalsIgnoreCase(t)) return i;
  return -1;
}""")
M(scl, r"""
public static int[] wheelOf(Object o) {
  String s = o instanceof String ? (String) o : EL_WHEEL;
  String[] p = s.split(">");
  int[] w = new int[5];
  boolean[] seen = new boolean[5];
  if (p.length != 5) return wheelOf(EL_WHEEL);
  for (int i = 0; i < 5; i++) {
    int e = elemIdx(p[i]);
    if (e < 0 || seen[e]) return o instanceof String ? wheelOf(null) : new int[] { 0, 1, 2, 3, 4 };
    seen[e] = true;
    w[i] = e;
  }
  return w;
}""")
M(scl, r"""
public static int[] elemNums(Object o) {
  int[] n = new int[] { 25, 25, 50 };
  if (!(o instanceof String)) return n;
  String[] p = ((String) o).split(";");
  for (int i = 0; i < 3 && i < p.length; i++) {
    try { int v = Integer.parseInt(p[i].trim()); if (v >= 0 && v <= 1000) n[i] = v; } catch (Throwable t) { }
  }
  return n;
}""")
M(scl, r"""
public static void elemRows(java.util.ArrayList out, java.util.UUID u) {
  out.add(new String[] { null, EL_HEAD[0], EL_HEAD[1] });
  String tx = elemTotals(u);
  if (tx == null) add(out, "Elements", "-", br().get("gear:fn:elemTotals") == null ? EL_NOGEAR : "Refresh in a second");
  else {
    String[] ps = tx.split(",");
    for (int i = 0; i < ps.length; i++) {
      int c = ps[i].indexOf(':');
      if (c <= 0) continue;
      String nm = ps[i].substring(0, c).trim();
      String v = ps[i].substring(c + 1).trim();
      if ("Poison".equals(nm)) { add(out, "Poison", v + "% over " + num(cfgNum("SkyyGear", "poison.time", 10.0)) + "s", "of each hit you land - every source stacks"); continue; }
      int sl = v.indexOf('/');
      if (sl < 0 || elemIdx(nm) < 0) continue;
      add(out, nm, v.substring(0, sl) + "% / " + v.substring(sl + 1) + " Def", "damage % of your hits / Defence vs " + nm);
    }
  }
  int[] w = wheelOf(br().get("mob:elem:wheel"));
  int[] n = elemNums(br().get("mob:elem:numbers"));
  int[] pos = new int[5];
  for (int i = 0; i < 5; i++) pos[w[i]] = i;
  out.add(new String[] { null, EL_HEAD[2], EL_HEAD[3] });
  out.add(new String[] { null, null, "", EL_COLS[0], EL_COLS[1], EL_COLS[2], EL_COLS[3], EL_COLS[4], EL_COLS[5], EL_COLS[6], EL_COLS[7] });
  for (int k = 0; k < 5; k++) {
    int y = w[k];
    int beat = w[(k + 1) % 5];
    String[] cells = new String[6];
    for (int m = 0; m < 5; m++) cells[m] = m == beat ? "+" + n[0] + "%" : (m == y ? "-" + n[1] + "%" : "-");
    cells[5] = "";
    trow(out, "Your " + EL_N[y], "beats " + EL_N[beat], cells);
  }
  StringBuilder wl = new StringBuilder();          // MenuUtil.safe turns '>' into ']' - the wheel in words
  for (int i = 0; i < 5; i++) { if (i > 0) wl.append(", "); wl.append(EL_N[w[i]]); }
  wl.append(" - each beats the next, ").append(EL_N[w[4]]).append(" beats ").append(EL_N[w[0]]);
  add(out, "Wheel", "", wl.toString());
  add(out, "Bosses", "-" + n[2] + "%", "a boss takes that much less from its own element");
  add(out, "Exceptions", "", Boolean.TRUE.equals(br().get("mob:elem:custom")) ? "your own table (Server Setup, Mobs, Elements)" : EL_EXC);          // elem1fix2: SkyyMobs' mob:elem:custom = an edited table
  out.add(new String[] { null, EL_HEAD[4], EL_HEAD[5] });
  for (int i = 0; i + 1 < EL_RX.length; i += 2) add(out, EL_RX[i], "later", EL_RX[i + 1]);
}""")
# 0.3.35: Your Stats = ONE scroll list - each section (Main, Combat, Gathering) = a head row {null, name, note} + its stat rows''')
P.rep('''  out.add(new String[] { null, LEG_HEAD[0], LEG_HEAD[1] });     // 0.3.44: the Sources legend''',
      '''  elemRows(out, u);     // 0.3.45 (elem1): Elements, Strong and weak, Reactions
  out.add(new String[] { null, LEG_HEAD[0], LEG_HEAD[1] });     // 0.3.44: the Sources legend''')
# the column header row: its own labels when it carries them
P.rep('''        b.set("#SkyyStatC" + i + "n" + ck + ".Text", @PKG@.StatsCalc.COLS[ck]);
      }''', '''        b.set("#SkyyStatC" + i + "n" + ck + ".Text", r.length >= 11 ? r[3 + ck] : @PKG@.StatsCalc.COLS[ck]);          // 0.3.45: the chart's own labels
      }''')
P.rep('''      b.set("#SkyyStatN" + i + ".Text", @PKG@.StatsCalc.COL_STAT);
      b.set("#SkyyStatV" + i + ".Text", @PKG@.StatsCalc.COL_TOTAL);''', '''      b.set("#SkyyStatN" + i + ".Text", r.length >= 11 ? r[9] : @PKG@.StatsCalc.COL_STAT);
      b.set("#SkyyStatV" + i + ".Text", r.length >= 11 ? r[10] : @PKG@.StatsCalc.COL_TOTAL);''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.45 adds no system / command"
_i = P.s.index
assert _i("public static void trow(java.util.ArrayList rows") < _i("public static void elemRows(") < _i("public static java.util.ArrayList allRows(")
P.finish()
