"""Derive SkyyHud/build_skyyhud_0.3.21.py from the generated 0.3.20 (the SET pin; 0.3.20 is left untouched; line endings preserved).
Run:  python tools/hud_0_3_21_patch.py   then   python SkyyHud/build_skyyhud_0.3.21.py   (never --deploy)
Harness: python SkyyHud/test_skyyhud_0.3.21.py [--dir <scratch>] [--keep]

0.3.21 = the QUEST WIDGET of round Q1 (research/SkyyQuests-Tutorial-Spec.md section 5; the approved mockup research/cloud/ui-mockups-1013/
a_quest_* + Layout-Spec.md sections 1, 2 and 7). Skyy, word for word (docs/answered/ui.md 92): "but a quest widget is essential, we need a
place to quickly and easily tell players what to do next without digging in menus."
  1. New widget id "Quest" (label "Quest Tracker"), APPENDED to Widgets.IDS (0.3.20 layout files, export codes and profiles load as
     before; 0.3.20 ignores the id). Built-in default ON at tl 8,42 (under Coords; the 0.3.20 Party / Guild spots already leave room).
     Players whose saved layout has no Quest line (everyone today) get that spot - unless it touches one of THEIR shown widgets: then the
     first free spot on the tl anchor (Widgets.questPlace: x 8 or 6 px right of a box, y 42 or 6 px under a box, the left half, nearest to
     8,42 first). Saved lines are never moved; the server default layout (hud.defaultLayout) wins when it places Quest.
  2. ONE source of truth: SkyyQuests' quest:fn:hud apply(UUID) -> Object[] {String title, String count, then per shown task: String name,
     String progress, Double frac or null, String where, Integer dir 0-7 or -1, Boolean done} (Layout-Spec 7); 0 tasks = "No active
     quests"; null = hidden. The HUD never decides anything about quests itself (how many tasks, hide when empty, hide the tutorial: all
     SkyyQuests' player switches). REFRESH ON quest:epoch:<uuid>, NEVER PER TICK: the existing 1 s HUD tick (SkyyHud's own thread since
     0.3.19) reads the epoch (one map read); unchanged = the cached model (Widgets.QCACHE), no call. Changed = one quest:fn:hud call
     (a memory read in SkyyQuests). Same shape = text / bar Value / arrow .Visible sets only; a new shape (task count, a done task, a bar or
     an arrow appearing) = the 0.3.8 shape re-send (at most once per 1.5 s). Without SkyyQuests: hidden on the HUD; the editor and the
     Settings page show "Needs SkyyQuests 0.1" (or a sample with SkyyQuests) so it can be placed and styled.
  3. THE LOOK (Layout-Spec section 2, 1:1 at 100 %): 300 wide; 149 / 124 / 99 high for 3 / 2 / 1 tasks (67 for "No active quests");
     the SkyyHud box #0b1524(0.72) + a 1 px gold hairline #E8A93B(0.45) (four 1 px Groups, no texture); padding 10; header = a gold
     diamond + the line name (13, gold #E8A93B) + "3 / 24" (12, #878e9c) right; a gold line #E8A93B(0.35); task 1 = a gold diamond + its
     name (14, #d6e4ee or the widget colour) + "6/10" (14, #ffffff) right + the vanilla ProgressBar (6 px, indented 14; the Combat
     widget's proven textures) + the where line (12, #7caacc): the 8-way NORTH-UP arrow + "NE  42 m  -  Island 2" (no direction = text
     only); tasks 2-3 = a hollow diamond + name (13, #96a9be) + progress (12, #878e9c). A done task = green #39f493 name / progress / where
     ("Done!  +25 coins  +40 Foraging XP") with a green diamond for SkyyQuests' green hold, then the list moves up (SkyyQuests bumps the
     epoch). Long texts end in "..." (the 0.3.13 font tables, at the widget's size). Bold / italic / glow / colour follow the widget's
     Settings like every widget (colour = task 1's name only; the gold / grey / blue roles stay as the mockup).
     DIAMONDS AND ARROWS ARE PIXEL GROUPS (1 px rows of plain Group Backgrounds, the element every HUD widget already uses): HUD pictures
     cannot rotate and a pack picture as a HUD Background is still UNVERIFIED (the 0.3.18 Abilities-icon rule), so the 8 arrows are
     8 small pre-built Group containers (11 x 11 px at 100 %, drawn by this patch from one arrow shape rotated in 45 degree steps) and
     exactly one is Visible - a direction change is ONE .Visible pair of sets, never a re-send. No new texture, no asset.
  4. Unchanged: every other widget's markup, texts and editor behaviour; the layout / code / profile format; commands, permissions, the
     admin rows, the config file. No new config row, command or player switch (the Quest switches live in SkyyQuests).
ROLLBACK: 0.3.21 -> 0.3.20 is safe: 0.3.20 ignores the Quest layout line / export part; nothing else is written.
"""
import os
import math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.20.py")
dst = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.21.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.20"' in s and s.startswith('"""SkyyHud 0.3.20 - build script')
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


# ---------------- the 8 arrow pictures as pixel rows (11 x 11 at 100 %): one arrow shape, rotated in 45 degree steps -----------------
def arrow_rows(k, n=11):
    """the N arrow (head 5 rows, shaft 6 rows) rotated k x 45 degrees clockwise on screen; -> [(x, y, length)] runs of lit pixels"""
    th = math.radians(45 * k)
    c = (n - 1) / 2.0
    lit = []
    for y in range(n):
        row = []
        for x in range(n):
            sx, sy = x - c, y - c
            ax = sx * math.cos(th) + sy * math.sin(th)
            ay = -sx * math.sin(th) + sy * math.cos(th)
            head = -5.2 <= ay <= -0.2 and abs(ax) <= (ay + 5.2) * 0.92 + 0.35
            shaft = -0.2 <= ay <= 5.2 and abs(ax) <= 1.25
            row.append(head or shaft)
        x = 0
        while x < n:
            if row[x]:
                x0 = x
                while x < n and row[x]:
                    x += 1
                lit.append((x0, y, x - x0))
            else:
                x += 1
    return lit


QARR, QARO = [], [0]
for _k in range(8):
    _r = arrow_rows(_k)
    assert 8 <= len(_r) <= 40, (_k, len(_r))
    for _x, _y, _l in _r:
        QARR += [_x, _y, _l]
    QARO.append(len(QARR))
# sanity: N points up (its top row is one centred pixel), S is N upside down, E is N turned right
_N = sorted(arrow_rows(0), key=lambda t: (t[1], t[0]))
assert _N[0] == (5, 0, 1), _N[0]
assert sorted((x, 10 - y, l) for x, y, l in arrow_rows(0)) == sorted(arrow_rows(4)), "S = N mirrored"
assert sorted((10 - y, x, 1) for x, y, l in arrow_rows(0) for x in range(x, x + l)) == sorted((x, y, 1) for x, y, l in arrow_rows(2) for x in range(x, x + l)), "E = N turned right"

# ---------------- docstring + version ----------------
rep('''"""SkyyHud 0.3.20 - build script (javassist via jpype).
Run:   python build_skyyhud_0.3.20.py            -> SkyyHud/SkyyHud-0.3.20.jar
       (deploys only through tools/deploy_set.py - never pass --deploy here)
''', '''"""SkyyHud 0.3.21 - build script (javassist via jpype).
Run:   python build_skyyhud_0.3.21.py            -> SkyyHud/SkyyHud-0.3.21.jar
       (deploys only through tools/deploy_set.py - never pass --deploy here)
0.3.21 (generated by tools/hud_0_3_21_patch.py from 0.3.20): the QUEST WIDGET (research/SkyyQuests-Tutorial-Spec.md section 5, the approved
  mockup research/cloud/ui-mockups-1013/a_quest_*; Skyy: "a quest widget is essential"). Widget id Quest APPENDED to Widgets.IDS, default
  ON at tl 8,42 (a free spot when that touches the player's own widgets; saved layouts never move); data ONLY from SkyyQuests'
  quest:fn:hud, called only when quest:epoch:<uuid> changed (the 1 s tick reads the epoch); 300 x 149 / 124 / 99, header + up to 3 tasks,
  task 1 with the vanilla ProgressBar and the where line (north-up 8-way arrow drawn as pixel Groups + "NE  42 m  -  Island 2"); hidden
  without SkyyQuests. Details in tools/hud_0_3_21_patch.py.
''')
rep('VERSION = "0.3.20"\n', 'VERSION = "0.3.21"\n')

# ---------------- constants ----------------
after('''assert len(MSG_SHOW_HELP) <= 100 and len(MSG_KINDS) == 10
''', '''# 0.3.21 QUEST WIDGET (research/SkyyQuests-Tutorial-Spec.md 5; Layout-Spec.md 2): APPENDED; 300 wide, 149 high with 3 tasks at 100 %
IDS.append("Quest")
DEFAULTS["Quest"] = (True, "tl", 8, 42)
LABELS["Quest"] = "Quest Tracker"
SIZES["Quest"] = (300, 149)
assert IDS[-5:] == ["Minimap", "Seasons", "Abilities", "Feed", "Quest"]
# the mockup's rows at 100 %: pad, header, gap, gold line, gap, task 1 name, gap, bar, gap, where, gap (to task 2 / 3), task 2 / 3 name
QROWS = (10, 18, 6, 1, 7, 18, 4, 6, 4, 15, 8, 17)
assert sum(QROWS[:10]) + QROWS[0] == 99 and 99 + 2 * (QROWS[10] + QROWS[11]) == 149 and 99 + QROWS[10] + QROWS[11] == 124
QNEED = "Needs SkyyQuests 0.1"
QEMPTY = "Pick one at the quest board in the hub"
''')

# ---------------- Widgets: fields + multi ----------------
rep('''wid.addField(CtField.make('public static final String CNEED = "%s";' % CMB_NEED, wid))
''', '''wid.addField(CtField.make('public static final String CNEED = "%s";' % CMB_NEED, wid))
# 0.3.21 Quest widget: the stand-in lines, the 8 arrows as pixel runs (x, y, length) at 100 % (QARO = where each arrow starts in QARR),
# the epoch cache (UUID -> Object[] { epoch, model })
wid.addField(CtField.make('public static final String QNEED = "%s";' % QNEED, wid))
wid.addField(CtField.make('public static final String QEMPTY = "%s";' % QEMPTY, wid))
wid.addField(CtField.make("public static final int[] QARR = new int[] { ''' + ", ".join(str(v) for v in QARR) + ''' };", wid))
wid.addField(CtField.make("public static final int[] QARO = new int[] { ''' + ", ".join(str(v) for v in QARO) + ''' };", wid))
wid.addField(CtField.make("public static final int[] QROWS = new int[] { %s };" % ", ".join(str(v) for v in QROWS), wid))
wid.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap QCACHE = new java.util.concurrent.ConcurrentHashMap();", wid))
wid.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicLong QCALLS = new java.util.concurrent.atomic.AtomicLong();", wid))
''')
rep('''public static boolean multi(String id) { return "Party".equals(id) || "Guild".equals(id) || "Skills".equals(id) || "Combat".equals(id) || "Abilities".equals(id); }""", wid))''',
    '''public static boolean multi(String id) { return "Party".equals(id) || "Guild".equals(id) || "Skills".equals(id) || "Combat".equals(id) || "Abilities".equals(id) || "Quest".equals(id); }""", wid))''')

# ---------------- Widgets: the Quest model (before model(), javassist order; no text measuring here - the cut is in questPairs) ------
Q_MODEL = r'''# 0.3.21 QUEST model (String[23]): [0] SHAPE ("Q0" hidden; "QE" no active quests; "Q" + n + per task its done flag, task 1 also "b"
# bar / "a" arrow), [1] headline (= the title; null = hidden), [2] title, [3] count, [4] task count "1"-"3" or "E", task k at o = 5 + 6k:
# [o] name, [o+1] progress, [o+2] bar Value "0.000"-"1.000" (task 1 only; null = no bar), [o+3] where (task 1 only), [o+4] dir "-1".."7"
# (task 1 only), [o+5] done "1" / "0". ONE source of truth: quest:fn:hud; called only when quest:epoch:<uuid> changed (QCACHE).
FXM(wid, """
public static String qStr(Object o) {
  if (o == null) return "";
  String t = String.valueOf(o);
  return t.length() > 120 ? t.substring(0, 120) : t;
}""")
FXM(wid, """
public static String qShape(String[] m) {
  if ("E".equals(m[4])) return "QE";
  StringBuilder sb = new StringBuilder("Q");
  sb.append(m[4]);
  int n = 0;
  try { n = Integer.parseInt(m[4]); } catch (Throwable t) { n = 0; }
  for (int k = 0; k < n; k++) {
    int o = 5 + 6 * k;
    sb.append("|").append(m[o + 5]);
    if (k == 0) sb.append(m[o + 2] != null ? "b" : "-").append("-1".equals(m[o + 4]) ? "-" : "a");
  }
  return sb.toString();
}""")
# quest:fn:hud's answer -> the model (any malformed answer = hidden)
FXM(wid, """
public static String[] questModelOf(Object r) {
  String[] m = new String[23];
  m[0] = "Q0";
  if (!(r instanceof Object[])) return m;
  Object[] a = (Object[]) r;
  if (a.length < 2) return m;
  m[2] = qStr(a[0]);
  m[3] = qStr(a[1]);
  int n = (a.length - 2) / 6;
  if (n > 3) n = 3;
  if (n <= 0) {
    m[4] = "E";
    m[8] = QEMPTY;
    m[9] = "-1";
    m[1] = m[2];
    m[0] = qShape(m);
    return m;
  }
  for (int k = 0; k < n; k++) {
    int i = 2 + 6 * k;
    int o = 5 + 6 * k;
    m[o] = qStr(a[i]);
    m[o + 1] = qStr(a[i + 1]);
    m[o + 2] = null;
    if (k == 0 && a[i + 2] instanceof Number) {
      double f = ((Number) a[i + 2]).doubleValue();
      if (!(f >= 0.0)) f = 0.0;
      if (f > 1.0) f = 1.0;
      long v = Math.round(f * 1000.0);
      String d = String.valueOf(v);
      while (d.length() < 4) d = "0" + d;
      m[o + 2] = d.substring(0, d.length() - 3) + "." + d.substring(d.length() - 3);
    }
    m[o + 3] = k == 0 ? qStr(a[i + 3]) : "";
    int dir = -1;
    if (k == 0 && a[i + 4] instanceof Number) dir = ((Number) a[i + 4]).intValue();
    if (dir < -1 || dir > 7) dir = -1;
    m[o + 4] = String.valueOf(dir);
    m[o + 5] = Boolean.TRUE.equals(a[i + 5]) ? "1" : "0";
  }
  m[4] = String.valueOf(n);
  m[1] = m[2];
  m[0] = qShape(m);
  return m;
}""")
FXM(wid, """
public static boolean questHave(java.util.Map b) {
  try { return b != null && b.get("quest:fn:hud") instanceof java.util.function.Function; } catch (Throwable t) { return false; }
}""")
# the player's model: quest:fn:hud is asked only when quest:epoch:<uuid> differs from the cached one
FXM(wid, """
public static String[] questModelU(java.util.UUID me) {
  String[] h = new String[23];
  h[0] = "Q0";
  if (me == null) return h;
  java.util.Map b = bridge();
  if (!questHave(b)) return h;
  Object ep = b.get("quest:epoch:" + me.toString());
  Object c = QCACHE.get(me);
  if (ep != null && c instanceof Object[] && ep.equals(((Object[]) c)[0])) return (String[]) ((Object[]) c)[1];
  Object r = null;
  try { QCALLS.incrementAndGet(); r = ((java.util.function.Function) b.get("quest:fn:hud")).apply(me); } catch (Throwable t) { r = null; }
  String[] m = questModelOf(r);
  if (QCACHE.size() > 2048) QCACHE.clear();
  QCACHE.put(me, new Object[] { ep, m });
  return m;
}""")
'''
before('''# model() is the MASK-LESS entry (Party / Guild pass their option here): for Skills it gives the BUILT-IN lines. Every Skills caller''', Q_MODEL)
rep('''    if ("Abilities".equals(id)) return abilModelU(pr.getUuid(), !opt);   // FIX ROUND: opt true (the default) = Icons Hide
  }} catch (Throwable t) {{ }}''', '''    if ("Abilities".equals(id)) return abilModelU(pr.getUuid(), !opt);   // FIX ROUND: opt true (the default) = Icons Hide
    if ("Quest".equals(id)) return questModelU(pr.getUuid());            // 0.3.21
  }} catch (Throwable t) {{ }}''')
rep('''  if ("Abilities".equals(id)) {{ String[] c = new String[14]; c[0] = "A0"; return c; }}
  String[] m = new String[17];''', '''  if ("Abilities".equals(id)) {{ String[] c = new String[14]; c[0] = "A0"; return c; }}
  if ("Quest".equals(id)) {{ String[] c = new String[23]; c[0] = "Q0"; return c; }}
  String[] m = new String[17];''')

# ---------------- the editor / Settings stand-in ----------------
before('''# editor / settings sample lines while not in a party / guild
''', '''# 0.3.21: the Quest widget's editor / Settings stand-in while it is hidden: a tutorial sample (3 tasks, the bar, the arrow) so it can be
# placed and styled, or "Needs SkyyQuests 0.1" while quest:fn:hud is missing
FXM(wid, """
public static String[] questSample() {
  if (!questHave(bridge())) {
    String[] m = questModelOf(new Object[] { QNEED, "" });
    m[0] = "S";
    return m;
  }
  String[] m = questModelOf(new Object[] { "Getting Started", "3 / 24",
      "Chop 10 logs", "6/10", Double.valueOf(0.6), "NE  42 m  -  Island 2", Integer.valueOf(1), Boolean.FALSE,
      "Craft a crafting accessory", "", null, "", Integer.valueOf(-1), Boolean.FALSE,
      "Mine stone and copper", "0/2", null, "", Integer.valueOf(-1), Boolean.FALSE });
  m[0] = "S";
  return m;
}""")
''')
rep('''  if ("Abilities".equals(id)) return abilSample(!opt);   // FIX ROUND: opt true (the default) = Icons Hide
  if (me == null''', '''  if ("Abilities".equals(id)) return abilSample(!opt);   // FIX ROUND: opt true (the default) = Icons Hide
  if ("Quest".equals(id)) return questSample();         // 0.3.21
  if (me == null''')

# ---------------- linePairs (the raw texts; questPairs cuts them to fit) ----------------
rep('''  } else if (m != null && m.length > 1 && m[1] != null && "Skills".equals(id)) {''',
    '''  } else if (m != null && m.length > 22 && m[1] != null && "Quest".equals(id)) {
    a.add("H"); a.add(m[2] == null ? "" : m[2]);
    a.add("C"); a.add(m[3] == null ? "" : m[3]);
    if ("E".equals(m[4])) { a.add("W0"); a.add(m[8] == null ? "" : m[8]); }
    else {
      int n = 0;
      try { n = Integer.parseInt(m[4]); } catch (Throwable t) { n = 0; }
      for (int k = 0; k < n && k < 3; k++) {
        int o = 5 + 6 * k;
        a.add("N" + k); a.add(m[o] == null ? "" : m[o]);
        a.add("S" + k); a.add(m[o + 1] == null ? "" : m[o + 1]);
        if (k == 0) { a.add("W0"); a.add(m[o + 3] == null ? "" : m[o + 3]); }
      }
    }
  } else if (m != null && m.length > 1 && m[1] != null && "Skills".equals(id)) {''')

# ---------------- the fixed width + the heights ----------------
rep('''public static int multiW(String id, {PKG}.WLayout l, String[] m, int sc, int minFs) {{
  return capW(innerW(id, m, sc, minFs, l.bold) + 2 * padMl(sc, minFs), l, sc);''', '''public static int multiW(String id, {PKG}.WLayout l, String[] m, int sc, int minFs) {{
  if ("Quest".equals(id)) return capW(300 * sc / 100, l, sc);     // 0.3.21: the mockup's fixed 300 (texts are cut to fit, never widened)
  return capW(innerW(id, m, sc, minFs, l.bold) + 2 * padMl(sc, minFs), l, sc);''')
before('''# 0.3.11: the Skills height = SKL_TP (3) + rows x SKL_ROW (20) + SKL_TP, the floored parts skillsBody places its lines with (the two''',
       '''# 0.3.21: the Quest rows at size sc (each floored on its own, a 1 px line / bar never below 1) - bodyH and questBody use the same numbers
FXM(wid, """
public static int[] questRows(int sc) {
  int[] r = new int[QROWS.length];
  for (int i = 0; i < r.length; i++) { r[i] = QROWS[i] * sc / 100; if (r[i] < 1) r[i] = 1; }
  return r;
}""")
FXM(wid, """
public static int questH(String[] m, int sc) {
  int[] r = questRows(sc);
  int top = r[0] + r[1] + r[2] + r[3] + r[4];
  if (m == null || m.length < 23 || m[4] == null) return top + r[9] + r[0];
  if ("E".equals(m[4])) return top + r[9] + r[0];
  int n = 1;
  try { n = Integer.parseInt(m[4]); } catch (Throwable t) { n = 1; }
  if (n < 1) n = 1;
  if (n > 3) n = 3;
  return top + r[5] + r[6] + r[7] + r[8] + r[9] + (n - 1) * (r[10] + r[11]) + r[0];
}""")
''')
rep('''public static int bodyH(String id, String[] m, int sc) {
  if ("Skills".equals(id))''', '''public static int bodyH(String id, String[] m, int sc) {
  if ("Quest".equals(id)) return questH(m, sc);
  if ("Skills".equals(id))''')

# ---------------- the Quest markup ----------------
Q_BODY = r'''# 0.3.21 QUEST MARKUP (FLAT, the widget Group's direct children; Layout-Spec 2): the gold hairline (4 x 1 px), the header diamond + H
# (title) + C (count), the gold line, task 1: diamond + N0 / S0 + the ProgressBar Bar0 + the arrow (8 pre-built containers A0-A7, one
# Visible) + W0 (where); tasks 2-3: a hollow diamond + Nk / Sk. Pixel art = plain Groups (no textures). A label box is never lower than
# its font + 8 (centred on its row, so the mockup's tight rows never clip the glyphs).
FXM(wid, """
public static String qRect(int x, int y, int w, int h, String c) {
  return "Group { Anchor: (Left: " + x + ", Top: " + y + ", Width: " + w + ", Height: " + h + "); Background: " + c + "; } ";
}""")
# an 8 x 8 diamond (unit u px a cell) at x, y: filled, or its outline only
FXM(wid, """
public static String qDiamond(int x, int y, int u, String c, boolean hollow) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < 8; i++) {
    int half = i < 4 ? i + 1 : 8 - i;
    int x0 = x + (4 - half) * u;
    int wd = 2 * half * u;
    if (!hollow || i == 0 || i == 7) sb.append(qRect(x0, y + i * u, wd, u, c));
    else { sb.append(qRect(x0, y + i * u, u, u, c)); sb.append(qRect(x0 + wd - u, y + i * u, u, u, c)); }
  }
  return sb.toString();
}""")
FXM(wid, """
public static String qArrows(String base, int x, int y, int u, String c, int dir) {
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < 8; k++) {
    sb.append("Group #").append(base).append("A").append(k).append(" { Anchor: (Left: ").append(x).append(", Top: ").append(y).append(", Width: ").append(11 * u).append(", Height: ").append(11 * u).append("); Visible: ").append(k == dir ? "true" : "false").append("; ");
    for (int j = QARO[k]; j + 2 < QARO[k + 1]; j += 3) sb.append(qRect(QARR[j] * u, QARR[j + 1] * u, QARR[j + 2] * u, u, c));
    sb.append("} ");
  }
  return sb.toString();
}""")
# one text line from x to xr (Start or End aligned) on a row (y, h); the label box is at least fs + 8 high, centred on the row
FXM(wid, """
public static String qLine(String base, int x, int xr, int y, int h, int fs, @PKG@.WLayout l, String col, String align) {
  int d = (fs * 3 + 12) / 24;
  if (d < 1) d = 1;
  int hh = h < fs + 8 ? fs + 8 : h;
  int yy = y - (hh - h) / 2;
  int wd = xr - x; if (wd < 1) wd = 1;
  String g = ("def".equals(l.gcol) ? col : hexOf(l.gcol)) + "(0.45)";
  return lineSrc(base, x - d, yy, wd + 2 * d, hh, fs, l, col, g, align);
}""")
FXM(wid, """
public static String questBody(String base, @PKG@.WLayout l, int sc, String[] m, int minFs, int w) {
  int[] r = questRows(sc);
  int p = r[0];
  int u = (sc + 50) / 100; if (u < 1) u = 1;
  int ind = 14 * sc / 100;
  int h = questH(m, sc);
  StringBuilder sb = new StringBuilder();
  sb.append(qRect(0, 0, w, 1, "#E8A93B(0.45)")).append(qRect(0, h - 1, w, 1, "#E8A93B(0.45)"));
  sb.append(qRect(0, 0, 1, h, "#E8A93B(0.45)")).append(qRect(w - 1, 0, 1, h, "#E8A93B(0.45)"));
  boolean empty = m == null || m.length < 23 || "E".equals(m[4]) || m[4] == null;
  int y = p;
  sb.append(qDiamond(p, y + (r[1] - 8 * u) / 2, u, empty ? "#96a9be" : "#E8A93B", empty));
  int fsT = fsOf(13, sc, minFs); int fsC = fsOf(12, sc, minFs);
  sb.append(qLine(base + "H", p + ind, w - p, y, r[1], fsT, l, empty ? "#96a9be" : "#E8A93B", "Start"));
  sb.append(qLine(base + "C", p + ind, w - p, y, r[1], fsC, l, "#878e9c", "End"));
  y = y + r[1] + r[2];
  sb.append(qRect(p, y, w - 2 * p, r[3], "#E8A93B(0.35)"));
  y = y + r[3] + r[4];
  int fsW = fsOf(12, sc, minFs);
  if (empty) {
    sb.append(qLine(base + "W0", p, w - p, y, r[9], fsW, l, "#878e9c", "Start"));
    return sb.toString();
  }
  int n = 1;
  try { n = Integer.parseInt(m[4]); } catch (Throwable t) { n = 1; }
  boolean d0 = "1".equals(m[10]);
  String green = "#39f493";
  String c1 = d0 ? green : ("def".equals(l.col) ? "#d6e4ee" : hexOf(l.col));
  sb.append(qDiamond(p, y + (r[5] - 8 * u) / 2, u, d0 ? green : "#E8A93B", false));
  int fs1 = fsOf(14, sc, minFs);
  sb.append(qLine(base + "N0", p + ind, w - p, y, r[5], fs1, l, c1, "Start"));
  sb.append(qLine(base + "S0", p + ind, w - p, y, r[5], fs1, l, d0 ? green : "#ffffff", "End"));
  y = y + r[5] + r[6];
  if (m[7] != null) sb.append("ProgressBar #").append(base).append("Bar0 { Anchor: (Left: ").append(p + ind).append(", Top: ").append(y).append(", Width: ").append(w - 2 * p - ind).append(", Height: ").append(r[7]).append("); Background: \\"@QTRACK@\\"; BarTexturePath: \\"@QFILL@\\"; Value: ").append(m[7]).append("; } ");
  y = y + r[7] + r[8];
  int dir = -1;
  try { dir = Integer.parseInt(m[9]); } catch (Throwable t) { dir = -1; }
  int xw = p + ind;
  if (dir >= 0) {
    sb.append(qArrows(base, xw, y + (r[9] - 11 * u) / 2, u, d0 ? green : "#7caacc", dir));
    xw = xw + 11 * u + 4 * sc / 100;
  }
  sb.append(qLine(base + "W0", xw, w - p, y, r[9], fsW, l, d0 ? green : "#7caacc", "Start"));
  y = y + r[9];
  int fs2 = fsOf(13, sc, minFs); int fsP = fsOf(12, sc, minFs);
  for (int k = 1; k < n && k < 3; k++) {
    y = y + r[10];
    int o = 5 + 6 * k;
    boolean dk = "1".equals(m[o + 5]);
    sb.append(qDiamond(p, y + (r[11] - 8 * u) / 2, u, dk ? green : "#96a9be", !dk));
    sb.append(qLine(base + "N" + k, p + ind, w - p, y, r[11], fs2, l, dk ? green : "#96a9be", "Start"));
    sb.append(qLine(base + "S" + k, p + ind, w - p, y, r[11], fsP, l, dk ? green : "#878e9c", "End"));
    y = y + r[11];
  }
  return sb.toString();
}""")
'''
before('''wid.addMethod(CtNewMethod.make(f"""
public static String multiBody(String id, String base, {PKG}.WLayout l, int sc, String[] m, int minFs, int w) {{''', Q_BODY)
rep('''  if ("Abilities".equals(id)) return abilBody(base, l, sc, m, minFs, w);
  if ("Skills".equals(id)) return skillsBody(base, l, sc, m, minFs, w);''', '''  if ("Abilities".equals(id)) return abilBody(base, l, sc, m, minFs, w);
  if ("Quest".equals(id)) return questBody(base, l, sc, m, minFs, w);     // 0.3.21
  if ("Skills".equals(id)) return skillsBody(base, l, sc, m, minFs, w);''')
rep('''  if ("Abilities".equals(id) && m.length > 9) {
    if (m[4] != null && m[9] != null) return new String[] { "Bar0", m[4], "Bar1", m[9] };
    if (m[4] != null) return new String[] { "Bar0", m[4] };
    if (m[9] != null) return new String[] { "Bar1", m[9] };
  }
  return new String[0];
}""", wid))''', '''  if ("Abilities".equals(id) && m.length > 9) {
    if (m[4] != null && m[9] != null) return new String[] { "Bar0", m[4], "Bar1", m[9] };
    if (m[4] != null) return new String[] { "Bar0", m[4] };
    if (m[9] != null) return new String[] { "Bar1", m[9] };
  }
  if ("Quest".equals(id) && m.length > 7 && m[7] != null && !"E".equals(m[4])) return new String[] { "Bar0", m[7] };   // 0.3.21
  return new String[0];
}""", wid))
# 0.3.21: the elements a shown model turns on / off as (element suffix, "1" / "0") pairs: the Quest arrows A0-A7 (exactly one on) - the
# shape carries whether an arrow is drawn at all, so a direction change is .Visible sets only
wid.addMethod(CtNewMethod.make("""
public static String[] visPairs(String id, String[] m) {
  if (!"Quest".equals(id) || m == null || m.length < 23 || m[1] == null || "E".equals(m[4]) || m[9] == null || "-1".equals(m[9])) return new String[0];
  String[] r = new String[16];
  for (int k = 0; k < 8; k++) { r[2 * k] = "A" + k; r[2 * k + 1] = String.valueOf(k).equals(m[9]) ? "1" : "0"; }
  return r;
}""", wid))''')

# ---------------- questPairs: the texts cut to fit (after fitText - javassist order) + pairsSc ----------------
rep('''FXM(wid, """
public static String feedFit(String nm, String cn, int sc, boolean bold) {''', '''# 0.3.21: the Quest texts cut with "..." to the room the markup gives them at size sc (header beside its count, a task name beside its
# progress, the where line after the arrow) - the same font tables as every box width
FXM(wid, """
public static String[] questPairs(String[] m, int sc, boolean bold) {
  String[] a = linePairs("Quest", m);
  int w = 300 * sc / 100;
  int p = 10 * sc / 100; if (p < 1) p = 1;
  int ind = 14 * sc / 100;
  int u = (sc + 50) / 100; if (u < 1) u = 1;
  boolean arrow = m != null && m.length > 9 && m[9] != null && !"-1".equals(m[9]) && !"E".equals(m[4]);
  java.util.HashMap v = new java.util.HashMap();
  for (int i = 0; i + 1 < a.length; i += 2) v.put(a[i], a[i + 1]);
  for (int i = 0; i + 1 < a.length; i += 2) {
    String k = a[i];
    String t = a[i + 1];
    int fs; int room;
    if (k.equals("H")) { fs = fsOf(13, sc, 6); String c = (String) v.get("C"); room = w - 2 * p - ind - (c == null || c.length() == 0 ? 0 : textW(c, fsOf(12, sc, 6), bold) + 8 * sc / 100); }
    else if (k.equals("C") || k.startsWith("S")) continue;
    else if (k.equals("W0")) { fs = fsOf(12, sc, 6); room = w - 2 * p - ("E".equals(m[4]) ? 0 : ind) - (arrow ? 11 * u + 4 * sc / 100 : 0); }
    else {
      fs = fsOf(k.equals("N0") ? 14 : 13, sc, 6);
      String s2 = (String) v.get("S" + k.substring(1));
      room = w - 2 * p - ind - (s2 == null || s2.length() == 0 ? 0 : textW(s2, fsOf(k.equals("N0") ? 14 : 12, sc, 6), bold) + 8 * sc / 100);
    }
    a[i + 1] = fitText(t, room, fs, bold);
  }
  return a;
}""")
FXM(wid, """
public static String[] pairsSc(String id, String[] m, int sc, boolean bold) {
  if ("Quest".equals(id)) return questPairs(m, sc, bold);
  return linePairs(id, m);
}""")
FXM(wid, """
public static String feedFit(String nm, String cn, int sc, boolean bold) {''')

# ---------------- questPlace (the first free spot for a player with no Quest line) + LayoutStore.get ----------------
before('''# ================= LayoutStore =================
''', '''# 0.3.21 Widgets.questPlace: a player whose saved file has no Quest line (everyone before 0.3.21) and whose server default does not place
# it gets the built-in spot tl 8,42 - unless it comes within 4 px of a shown widget's maximum box: then the first free spot on the tl
# anchor (x 8 or 6 px right of a box; y 42 or 6 px under a box; on screen, the left half), the one nearest 8,42 first. true = moved.
FXM(wid, """
public static boolean questPlace(java.util.Map m) {
  @PKG@.WLayout w = (@PKG@.WLayout) m.get("Quest");
  if (w == null || !w.en) return false;
  @PKG@.WLayout d = def("Quest");
  if (!d.anchor.equals(w.anchor) || w.dx != d.dx || w.dy != d.dy || w.scale != d.scale) return false;
  try { java.util.HashMap dm = @PKG@.HudCfg.layoutMap(); if (dm != null && dm.get("Quest") != null) return false; } catch (Throwable t) { }
  int qw = w.bw * w.scale / 100;
  int qh = w.bh * w.scale / 100;
  int n = 0;
  int[] r = new int[4 * (IDS.length + 1)];
  for (int i = 0; i < IDS.length; i++) {
    if ("Quest".equals(IDS[i]) || "Seasons".equals(IDS[i])) continue;
    @PKG@.WLayout o = (@PKG@.WLayout) m.get(IDS[i]);
    if (o == null || !o.en) continue;
    int ow = o.bw * o.scale / 100;
    int oh = hMax(o);
    int[] q = screenPosWH(o, ow, oh);
    r[4 * n] = q[0]; r[4 * n + 1] = q[1]; r[4 * n + 2] = ow; r[4 * n + 3] = oh;
    n = n + 1;
  }
  if (!mmHit(r, n, w.dx, w.dy, qw, qh)) return false;
  int[] cx = new int[n + 1];
  cx[0] = 8;
  for (int i = 0; i < n; i++) cx[i + 1] = r[4 * i] + r[4 * i + 2] + 6;
  int[] cy = new int[n + 1];
  cy[0] = d.dy;
  for (int i = 0; i < n; i++) cy[i + 1] = r[4 * i + 1] + r[4 * i + 3] + 6;
  int best = -1; int bdx = 0; int bdy = 0;
  for (int i = 0; i < cx.length; i++) {
    int dx = cx[i];
    if (dx < 8 || dx + qw > 960) continue;
    for (int j = 0; j < cy.length; j++) {
      int dy = cy[j];
      if (dy < 8 || dy + qh > 1072) continue;
      if (mmHit(r, n, dx, dy, qw, qh)) continue;
      int sc = Math.abs(dy - d.dy) + (dx - 8);
      if (best < 0 || sc < best || (sc == best && Math.abs(dy - d.dy) < Math.abs(bdy - d.dy))) { best = sc; bdx = dx; bdy = dy; }
    }
  }
  if (best < 0) return false;
  w.dx = bdx;
  w.dy = bdy;
  clampToScreen(w);
  return true;
}""")

''')
rep('''  boolean fdf = false;      // 0.3.20: the file has a Feed line
''', '''  boolean fdf = false;      // 0.3.20: the file has a Feed line
  boolean qdf = false;      // 0.3.21: the file has a Quest line
''')
rep('''        if (v != null && "Feed".equals(ids[i])) fdf = true;
''', '''        if (v != null && "Feed".equals(ids[i])) fdf = true;
        if (v != null && "Quest".equals(ids[i])) qdf = true;
''')
rep('''  java.util.Map prev = (java.util.Map) CACHE.putIfAbsent(u, m);
  return prev != null ? prev : m;
}}""", lst))''', '''  // 0.3.21: a quest widget the player never placed takes the first free spot when the built-in one touches their widgets (a COPY)
  if (!qdf) {{
    try {{
      {PKG}.WLayout qw = ({PKG}.WLayout) m.get("Quest");
      if (qw != null) {{
        {PKG}.WLayout qc = {PKG}.WLayout.parse(qw.ser(), qw);
        if (qc != null && qc != qw) {{ m.put("Quest", qc); if (!{PKG}.Widgets.questPlace(m)) m.put("Quest", qw); }}
      }}
    }} catch (Throwable t) {{ }}
  }}
  java.util.Map prev = (java.util.Map) CACHE.putIfAbsent(u, m);
  return prev != null ? prev : m;
}}""", lst))''')

# ---------------- HudMain.fill: the cut texts + the arrow .Visible sets ----------------
rep('''      String[] pairs = {PKG}.Widgets.linePairs(ids[i], mm);''',
    '''      String[] pairs = {PKG}.Widgets.pairsSc(ids[i], mm, ml == null ? 100 : ml.scale, ml == null || ml.bold);   // 0.3.21: Quest texts cut to fit''')
rep('''          b.set("#SkyyW" + ids[i] + bps[q] + ".Value", fv);
        }}
      }}
      continue;''', '''          b.set("#SkyyW" + ids[i] + bps[q] + ".Value", fv);
        }}
      }}
      String[] vps = {PKG}.Widgets.visPairs(ids[i], mm);    // 0.3.21: the Quest arrow (one of A0-A7 visible)
      for (int q = 0; q + 1 < vps.length; q += 2) {{
        String vk = ids[i] + ":" + vps[q];
        String vv = vps[q + 1];
        String vp = (String) this.last.get(vk);
        if (full || vp == null || !vp.equals(vv)) {{
          this.last.put(vk, vv);
          b.set("#SkyyW" + ids[i] + vps[q] + ".Visible", "1".equals(vv));
        }}
      }}
      continue;''')
rep('''      {PKG}.Widgets.setLines(b, "#SkyyEPv" + ids[i], {PKG}.Widgets.glowCount(l), {PKG}.Widgets.linePairs(ids[i], mm));''',
    '''      {PKG}.Widgets.setLines(b, "#SkyyEPv" + ids[i], {PKG}.Widgets.glowCount(l), {PKG}.Widgets.pairsSc(ids[i], mm, l.scale * 2 / 3, l.bold));''')
rep('''  if ("Skills".equals(this.wid) || "Combat".equals(this.wid) || "Abilities".equals(this.wid)) {{
    try {{''', '''  if ("Skills".equals(this.wid) || "Combat".equals(this.wid) || "Abilities".equals(this.wid) || "Quest".equals(this.wid)) {{
    try {{''')

# ---------------- the textures (the Combat widget's proven ProgressBar) + the description ----------------
rep('''_FXT = {"PKG": PKG, "UCB": UCB, "PR": PR, "MSG": MSG,''', '''_FXT = {"QTRACK": "Common/ProgressBar.png", "QFILL": "Common/ProgressBarFill.png", "PKG": PKG, "UCB": UCB, "PR": PR, "MSG": MSG,''')
rep('''"SkyyHud: customizable server-side HUD. 15 widgets (16 with Dynamic Seasons) incl. a Notification Feed''',
    '''"SkyyHud: customizable server-side HUD. 16 widgets (17 with Dynamic Seasons) incl. a Quest Tracker (your next 1-3 quest tasks with progress and where to go - an arrow and the distance; needs SkyyQuests), a Notification Feed''')

# ---------------- self-checks ----------------
assert 'IDS.append("Quest")' in s and s.count('"Quest".equals(') >= 12
assert "CMB_TRACK, CMB_FILL = \"Common/ProgressBar.png\", \"Common/ProgressBarFill.png\"" in s, "the Quest bar uses the Combat widget's proven textures"
assert s.count("pairsSc(") == 3 and s.count("Widgets.linePairs(ids[i], mm)") == 0
for a_, b_ in (("public static String[] questModelOf(", "public static String[] questModelU("), ("public static String[] questModelU(", "public static String[] model("),
               ("public static String[] questSample(", "public static String[] sampleU("), ("public static int[] questRows(", "public static int bodyH("),
               ("public static String lineSrc(", "public static String qLine("), ("public static String questBody(", "public static String multiBody("),
               ("public static String fitText(", "public static String[] questPairs("), ("public static String[] questPairs(", "public static String[] pairsSc("),
               ("public static String[] barPairs(", "public static String[] visPairs("), ("public static boolean mmHit(", "public static boolean questPlace("),
               ("public static boolean questPlace(", "public static java.util.Map get("), ("public static String[] visPairs(", "public boolean fill(")):
    assert s.index(a_) < s.index(b_), "javassist order: %s before %s" % (a_, b_)
assert "KEEP=10" in s and "KEEP=20" not in s
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.20 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines, %d changes)" % (s.count(LF), len(CHANGES)))
