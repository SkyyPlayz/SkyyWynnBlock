"""Derive SkyyHud/build_skyyhud_0.3.18.py from the generated 0.3.17 (the SET pin; 0.3.17 is left untouched; line endings preserved).
0.3.18 = the ABILITIES widget = round R2 of research/cloud/Ability-Engine-Plan.md (Skyy's lock, docs/answered/classes.md line 153: "we
decided 4 ability's, 2 active at a time. the 2 you pick are your primary ability's, and work when walking or sprinting. thew other 2 are
set to crouch. so crouching uses your alt ability's." + popup batch 1 line 172 "HUD swaps to alts while crouching").
  - New widget id Abilities ("Abilities"), APPENDED to Widgets.IDS after Seasons (0.3.17 layout files, export codes and profiles load as
    before; 0.3.17 ignores the id). Default ON at tl 8,760 (the left edge, under the default Skills box), box at most 220 x 59 at 100 %.
  - ONE source of truth: SkyyClasses' bridge Function class:fn:abil apply(UUID) (0.1.16: Object[16] = 4 x {name, Long msLeft, Long
    msTotal, state}; 0.1.17: Object[44] + ids, Mana / Stamina costs, affordable, crouching, the unlock levels - the layout is in
    tools/classes_0_1_17_patch.py). The HUD never decides anything itself. TWO rows: the two primaries; while you CROUCH (SkyyClasses'
    world-thread sample) the two crouch alts. Each row: the ability's icon (Show / Hide on the widget's Settings page), its name, and
      ready         its cost ("23 Mana + 2 Stam" - FIX2: both costs; "Free" in creative; "Ready" with SkyyClasses 0.1.16, which sends no costs)
      cooldown      the countdown ("12s", whole seconds rounded up; "2m" past 99 s) + the vanilla ProgressBar under the name, shrinking
                    (msLeft / msTotal - the Combat widget's proven bar)
      unaffordable  GREY (#8b949e, the party grey) with the whole cost ("23 Mana + 2 Stam" - FIX2)
      locked        GREY "Lv 10" (the unlock level; "Locked" with 0.1.16)   soon: GREY "Soon"   passive: "Passive"   empty: GREY "-"
    No class:fn:abil (SkyyClasses missing / older than 0.1.16) or no class with abilities: hidden on the HUD (the Party / Guild / Skills /
    Combat convention); the editor + Settings preview show a sample ("Meteor 23 Mana + 2 Stam" + "Mana Barrier 12s" with its bar) or
    "Needs SkyyClasses 0.1.17" so it can be placed and styled.
  - ICONS (FIX ROUND: OFF by default - Settings "Icons Show" turns them on; see the end of this docstring): the art agent's Mage + Priest ability icons (art/ability-icons/Common/Icons/Abilities/<Class>/<Id>.png, ART-RESUME 4 "Class
    ability icons - Mage + Priest", Skyy: "The ability icons look great, commit them" - our own art, drawn by tools/art/make_ability_icons.py)
    are copied at build time into the jar's asset pack as Common/UI/Custom/SkyyHud/Abil/<Id>.png (64 x 64 PNGs, checked) and drawn as a
    Group Background "SkyyHud/Abil/<Id>.png" (an inline path resolves under Common/UI/Custom/ - the vanilla textures' rule; a PACK picture
    there in a HUD is UNVERIFIED in game -> the Settings row "Icons Show / Hide" is the text fallback). An id without a picture = no icon.
  - Refresh: the existing 1 s HUD tick: the two names, the two right texts and the bar Values are Set when they change (Widgets.barPairs:
    Combat "Bar" as before + Abilities "Bar0" / "Bar1"); the SHAPE (crouch mode, icons, which rows have a bar, grey or not) changes =
    the 0.3.8 shape re-send (at most once per 1.5 s) + the 0.3.9 confirm send, exactly like the Combat widget entering combat.
  - Unchanged: every other widget's markup, texts and editor behaviour; the layout / code / profile format; commands, permissions, the
    admin rows, the config file. No new config row, command or player switch.
FIX ROUND (critics of 2026-10-09):
  - ICONS DEFAULT TO HIDE (names only): a pack picture as a HUD Background is UNVERIFIED and AGENT-BRIEF says trial features stay off
    until Skyy has seen them. The Combat widget's convention: WLayout.opt true (the default, the one a layout line leaves out) = Hide;
    Show = opt false. Settings row "Icons  Show / Hide": Show = #SkyySetOptOff ("optoff"), Hide = #SkyySetOptOn ("opton"). No layout
    format change (0.3.18 never shipped, so no saved opt has the old meaning).
  - (superseded by FIX2) An unaffordable row named only the stat you were short of.
FIX2 (second critics, 2026-10-09): every row with a cost shows BOTH costs ("23 Mana + 2 Stam"; "16 Mana" / "2 Stamina" when only one is
  set), ready in the widget colour, unaffordable grey - Skyy's lock (docs/answered/classes.md line 173) is Mana AND Stamina, so the HUD
  never hides the Stamina part. The box still fits 220 px at 100 % (harness W1 / W8).
Harness: python SkyyHud/test_skyyhud_0.3.18.py (see its docstring). To regenerate, delete SkyyHud/build_skyyhud_0.3.18.py first.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.17.py")
dst = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.18.py")
assert not os.path.exists(dst), "refusing to overwrite " + dst
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:90])
    s = s.replace(old, new)
    CHANGES.append((new, old))


# ---------------- docstring + version ----------------
rep('''"""SkyyHud 0.3.17 - build script (javassist via jpype).
Run:   python build_skyyhud_0.3.17.py            -> SkyyHud/SkyyHud-0.3.17.jar
       (deploys only through tools/deploy_set.py - never pass --deploy here)
''', '''"""SkyyHud 0.3.18 - build script (javassist via jpype).
Run:   python build_skyyhud_0.3.18.py            -> SkyyHud/SkyyHud-0.3.18.jar
       (deploys only through tools/deploy_set.py - never pass --deploy here)
0.3.18 (generated by tools/hud_0_3_18_patch.py from 0.3.17): the ABILITIES widget (research/cloud/Ability-Engine-Plan.md round R2; Skyy:
  4 abilities, 2 primary + 2 crouch alts, "HUD swaps to alts while crouching"). Widget id Abilities APPENDED to Widgets.IDS, default ON at
  tl 8,760; two rows from SkyyClasses' class:fn:abil (the primaries, the alts while you crouch): icon + name + cost / countdown with the
  vanilla ProgressBar; grey when you cannot pay or it is locked ("Lv 10"); hidden without SkyyClasses or a class with abilities. The
  Mage + Priest icons ship in the asset pack (Common/UI/Custom/SkyyHud/Abil/<Id>.png, from art/ability-icons); Settings: Icons Show / Hide.
  Details in tools/hud_0_3_18_patch.py.
''')
rep('VERSION = "0.3.17"', 'VERSION = "0.3.18"')

# ---------------- the widget id + defaults + the Abilities constants + the icons ----------------
rep('''assert IDS[-2:] == ["Minimap", "Seasons"]
''', '''assert IDS[-2:] == ["Minimap", "Seasons"]
# 0.3.18 ABILITIES widget (research/cloud/Ability-Engine-Plan.md R2): APPENDED (old files / codes / profiles keep their meaning); default
# ON at the left edge under the default Skills box; two rows of 20 px + a 4 px bar each at 100 % (3 + 2 x (20 + 4) + 2 + 6 = 59 high)
IDS.append("Abilities")
DEFAULTS["Abilities"] = (True, "tl", 8, 760)
LABELS["Abilities"] = "Abilities"
ABL_TP, ABL_ROW, ABL_BAR, ABL_GAP, ABL_BP, ABL_FS, ABL_ICON, ABL_IGAP = 3, 20, 4, 2, 6, 12, 18, 4
SIZES["Abilities"] = (220, ABL_TP + 2 * (ABL_ROW + ABL_BAR) + ABL_GAP + ABL_BP)
ABL_NEED = "Needs SkyyClasses 0.1.17"
assert IDS[-3:] == ["Minimap", "Seasons", "Abilities"] and SIZES["Abilities"] == (220, 59)
assert (ABL_TP, ABL_ROW, ABL_BAR, ABL_GAP, ABL_BP, ABL_ICON, ABL_IGAP) == (3, 20, 4, 2, 6, 18, 4), "Widgets.bodyH / innerW (not f-strings) spell these out"
# the art agent's Mage + Priest ability icons (our own art, committed under art/ability-icons; ART-RESUME 4): copied into the asset pack at
# build time; a missing file = that ability shows its name only (text fallback)
ABL_ICON_SRC = os.path.join(os.path.dirname(HERE), "art", "ability-icons", "Common", "Icons", "Abilities")
ABL_ICON_IDS = [("Mage", "Meteor"), ("Mage", "ManaBarrier"), ("Mage", "FrostNova"), ("Mage", "Starfall"), ("Mage", "ArcaneBeam"),
                ("Priest", "SacredHeal"), ("Priest", "ShieldBubble"), ("Priest", "GuardianSpirit"), ("Priest", "Sanctuary"), ("Priest", "MartyrsGrace")]
ABL_ICON_DIR = "SkyyHud/Abil/"                      # inline paths resolve under Common/UI/Custom/
ABL_ICONS = {}
for _c, _i in ABL_ICON_IDS:
    _p = os.path.join(ABL_ICON_SRC, _c, _i + ".png")
    if not os.path.isfile(_p):
        print("Abilities widget: no icon for %s (%s) - its name only" % (_i, _p))
        continue
    _b = open(_p, "rb").read()
    assert _b[:8] == b"\\x89PNG\\r\\n\\x1a\\n" and _b[12:16] == b"IHDR", "%s is not a PNG" % _p
    assert (int.from_bytes(_b[16:20], "big"), int.from_bytes(_b[20:24], "big")) == (64, 64), "%s is not 64 x 64" % _p
    ABL_ICONS[_i] = _b
print("Abilities widget icons: %d of %d (%s)" % (len(ABL_ICONS), len(ABL_ICON_IDS), ", ".join(sorted(ABL_ICONS))))
''')

# ---------------- Widgets: fields + multi ----------------
rep('''wid.addField(CtField.make('public static final String CNEED = "%s";' % CMB_NEED, wid))
''', '''wid.addField(CtField.make('public static final String CNEED = "%s";' % CMB_NEED, wid))
# 0.3.18 Abilities: the stand-in line while class:fn:abil is missing, the icon folder, the ids the jar ships a picture for
wid.addField(CtField.make('public static final String ANEED = "%s";' % ABL_NEED, wid))
wid.addField(CtField.make('public static final String ADIR = "%s";' % ABL_ICON_DIR, wid))
wid.addField(CtField.make("public static final String[] AICONS = new String[] { %s };" % ", ".join('"%s"' % i for i in sorted(ABL_ICONS)), wid))
''')
rep('''public static boolean multi(String id) { return "Party".equals(id) || "Guild".equals(id) || "Skills".equals(id) || "Combat".equals(id); }""", wid))''',
    '''public static boolean multi(String id) { return "Party".equals(id) || "Guild".equals(id) || "Skills".equals(id) || "Combat".equals(id) || "Abilities".equals(id); }""", wid))''')

# ---------------- Widgets: the Abilities model (before model(), javassist order) ----------------
ABL_MODEL = r'''# 0.3.18 ABILITIES model (String[14]): [0] SHAPE ("A0" hidden; "A" + mode + icons | row 0 | row 1 - what the markup depends on: crouch
# mode, the icon column, which rows have a bar, grey or not, the icon pictures; "S" = an editor / Settings sample), [1] headline (null =
# hidden), row k at o = 2 + 5k: [o] name, [o+1] right text (cost / countdown / "Lv 10"), [o+2] bar Value "0.000"-"1.000" (null = no
# bar), [o+3] tone ("n" the widget colour, "g" grey), [o+4] icon path (null = none); [12] "p" primaries / "a" alts, [13] "1" icon column.
# ONE source of truth: SkyyClasses' class:fn:abil apply(UUID) (the layout: tools/classes_0_1_17_patch.py); the HUD only shows it.
wid.addMethod(CtNewMethod.make("""
public static boolean abilHave(java.util.Map b) {
  try { return b != null && b.get("class:fn:abil") instanceof java.util.function.Function; } catch (Throwable t) { return false; }
}""", wid))
# the bridge answer, or null (no SkyyClasses / older than 0.1.16 / no class with abilities / an answer shorter than the 0.1.16 16 fields)
wid.addMethod(CtNewMethod.make("""
public static Object[] abilData(java.util.Map b, java.util.UUID u) {
  if (u == null) return null;
  Object f = null;
  try { f = b == null ? null : b.get("class:fn:abil"); } catch (Throwable t) { f = null; }
  if (!(f instanceof java.util.function.Function)) return null;
  try {
    Object r = ((java.util.function.Function) f).apply(u);
    if (r instanceof Object[] && ((Object[]) r).length >= 16) return (Object[]) r;
  } catch (Throwable t) { }
  return null;
}""", wid))
wid.addMethod(CtNewMethod.make("""
public static Object abilAt(Object[] a, int i) {
  if (a == null || i < 0 || i >= a.length) return null;
  return a[i];
}""", wid))
wid.addMethod(CtNewMethod.make("""
public static double abilNumOr(Object o, double d) {
  if (o instanceof Number) return ((Number) o).doubleValue();
  return d;
}""", wid))
# the picture of an ability id the jar ships (Common/UI/Custom/SkyyHud/Abil/<Id>.png), else null (its name only)
wid.addMethod(CtNewMethod.make("""
public static String abilIcon(String id) {
  if (id == null || id.length() == 0) return null;
  for (int i = 0; i < AICONS.length; i++) if (AICONS[i].equals(id)) return ADIR + id + ".png";
  return null;
}""", wid))
# the countdown: whole seconds rounded up ("12s", "1s" in the last second), past 99 s whole minutes rounded up ("2m")
wid.addMethod(CtNewMethod.make("""
public static String abilSecs(long ms) {
  long s = (ms + 999L) / 1000L;
  if (s < 1L) s = 1L;
  if (s > 99L) return ((s + 59L) / 60L) + "m";
  return s + "s";
}""", wid))
wid.addMethod(CtNewMethod.make("""
public static String abilNum(double x) {
  if (!(x >= 0.0) || Double.isInfinite(x)) return "0";
  long r = Math.round(x * 10.0);
  if (r % 10L == 0L) return String.valueOf(r / 10L);
  return (r / 10L) + "." + (r % 10L);
}""", wid))
# FIX2: the WHOLE cost (Skyy's lock: abilities cost Mana AND Stamina): "23 Mana + 2 Stam" when both, else the one that is set
wid.addMethod(CtNewMethod.make("""
public static String abilCost(double mc, double sc) {
  if (mc > 0.0 && sc > 0.0) return abilNum(mc) + " Mana + " + abilNum(sc) + " Stam";
  if (mc > 0.0) return abilNum(mc) + " Mana";
  if (sc > 0.0) return abilNum(sc) + " Stamina";
  return null;
}""", wid))
# one row from bridge slot k into m[o .. o+4]
wid.addMethod(CtNewMethod.make("""
public static void abilRow(Object[] a, int k, boolean icons, String[] m, int o) {
  Object no = abilAt(a, k * 4);
  String name = no instanceof String ? ((String) no).trim() : "";
  Object so = abilAt(a, k * 4 + 3);
  String st = so instanceof String ? (String) so : "empty";
  long left = (long) abilNumOr(abilAt(a, k * 4 + 1), 0.0);
  long total = (long) abilNumOr(abilAt(a, k * 4 + 2), 0.0);
  Object af = abilAt(a, 28 + k);
  boolean cant = af instanceof Boolean && !((Boolean) af).booleanValue();
  double mc = abilNumOr(abilAt(a, 20 + k), -1.0);
  double sc = abilNumOr(abilAt(a, 24 + k), -1.0);
  Object fo = abilAt(a, 36);
  boolean free = fo instanceof Boolean && ((Boolean) fo).booleanValue();
  String status;
  String tone = "n";
  String bar = null;
  if (name.length() == 0 || "empty".equals(st)) { name = "-"; status = ""; tone = "g"; }
  else if ("locked".equals(st)) {
    Object lv = abilAt(a, 38 + k);
    status = lv instanceof Number ? "Lv " + ((Number) lv).longValue() : "Locked";
    tone = "g";
  }
  else if ("soon".equals(st)) { status = "Soon"; tone = "g"; }
  else if ("passive".equals(st)) status = "Passive";
  else if ("cooldown".equals(st) && left > 0L) {
    status = abilSecs(left);
    bar = combatBar(left, total > 0L ? total : left);
    if (cant) tone = "g";
  }
  else if (free) status = "Free";
  else if (cant) {
    status = abilCost(mc, sc);   // FIX2: the whole cost, grey (the vanilla Mana / Stamina bars show which one is short)
    if (status == null) status = abilNum(mc) + " Mana";
    tone = "g";
  }
  else {
    status = abilCost(mc, sc);   // FIX2: "23 Mana + 2 Stam" (both costs); "Ready" when the bridge sends none (SkyyClasses 0.1.16)
    if (status == null) status = "Ready";
  }
  m[o] = name;
  m[o + 1] = status;
  m[o + 2] = bar;
  m[o + 3] = tone;
  Object io = abilAt(a, 16 + k);
  m[o + 4] = icons ? abilIcon(io instanceof String ? (String) io : null) : null;
}""", wid))
wid.addMethod(CtNewMethod.make("""
public static String abilShape(String[] m) {
  StringBuilder sb = new StringBuilder("A");
  sb.append(m[12]).append(m[13]);
  for (int k = 0; k < 2; k++) {
    int o = 2 + 5 * k;
    sb.append("|").append(m[o + 2] != null ? "b" : "-").append(m[o + 3]).append(m[o + 4] == null ? "" : m[o + 4]);
  }
  return sb.toString();
}""", wid))
wid.addMethod(CtNewMethod.make("""
public static String[] abilModelU(java.util.UUID me, boolean icons) {
  String[] m = new String[14];
  m[0] = "A0";
  if (me == null) return m;
  Object[] a = abilData(bridge(), me);
  if (a == null) return m;
  Object co = abilAt(a, 32);
  boolean crouch = co instanceof Boolean && ((Boolean) co).booleanValue();
  int k0 = crouch ? 2 : 0;
  abilRow(a, k0, icons, m, 2);
  abilRow(a, k0 + 1, icons, m, 7);
  m[12] = crouch ? "a" : "p";
  m[13] = (m[6] != null || m[11] != null) ? "1" : "0";
  m[1] = m[3].length() > 0 ? m[2] + " " + m[3] : m[2];
  m[0] = abilShape(m);
  return m;
}""", wid))
'''
rep('''# model() is the MASK-LESS entry (Party / Guild pass their option here): for Skills it gives the BUILT-IN lines. Every Skills caller''',
    ABL_MODEL + '''# model() is the MASK-LESS entry (Party / Guild pass their option here): for Skills it gives the BUILT-IN lines. Every Skills caller''')
rep('''    if ("Combat".equals(id)) return combatModelU(pr.getUuid(), opt);
  }} catch (Throwable t) {{ }}''', '''    if ("Combat".equals(id)) return combatModelU(pr.getUuid(), opt);
    if ("Abilities".equals(id)) return abilModelU(pr.getUuid(), !opt);   // FIX ROUND: opt true (the default) = Icons Hide
  }} catch (Throwable t) {{ }}''')
rep('''  if ("Combat".equals(id)) {{ String[] c = new String[6]; c[0] = "C0"; return c; }}
  String[] m = new String[17];''', '''  if ("Combat".equals(id)) {{ String[] c = new String[6]; c[0] = "C0"; return c; }}
  if ("Abilities".equals(id)) {{ String[] c = new String[14]; c[0] = "A0"; return c; }}
  String[] m = new String[17];''')

# ---------------- Widgets: the editor / Settings stand-in ----------------
rep('''# editor / settings sample lines while not in a party / guild
wid.addMethod(CtNewMethod.make("""
public static String[] sampleU(String id, String me, boolean opt) {
  if ("Skills".equals(id)) return skillsSample();
  if ("Combat".equals(id)) return combatSample();''', r'''# 0.3.18: the Abilities widget's editor / Settings stand-in while it is hidden: a Mage sample ("Meteor 23 Mana", "Mana Barrier 12s" with
# its bar 12 / 30 s) so it can be placed and styled, or "Needs SkyyClasses 0.1.17" while class:fn:abil is missing
wid.addMethod(CtNewMethod.make("""
public static String[] abilSample(boolean icons) {
  String[] m = new String[14];
  m[0] = "S";
  m[12] = "p";
  if (!abilHave(bridge())) {
    m[2] = ANEED; m[3] = ""; m[5] = "n"; m[7] = ""; m[8] = ""; m[10] = "n"; m[13] = "0";
    m[1] = m[2];
    return m;
  }
  m[2] = "Meteor"; m[3] = "23 Mana + 2 Stam"; m[4] = null; m[5] = "n"; m[6] = icons ? abilIcon("Meteor") : null;
  m[7] = "Mana Barrier"; m[8] = "12s"; m[9] = combatBar(12000L, 30000L); m[10] = "n"; m[11] = icons ? abilIcon("ManaBarrier") : null;
  m[13] = (m[6] != null || m[11] != null) ? "1" : "0";
  m[1] = m[2] + " " + m[3];
  return m;
}""", wid))
# editor / settings sample lines while not in a party / guild
wid.addMethod(CtNewMethod.make("""
public static String[] sampleU(String id, String me, boolean opt) {
  if ("Skills".equals(id)) return skillsSample();
  if ("Combat".equals(id)) return combatSample();
  if ("Abilities".equals(id)) return abilSample(!opt);   // FIX ROUND: opt true (the default) = Icons Hide''')

# ---------------- linePairs / innerW / bodyH ----------------
rep('''  if (m != null && m.length > 3 && m[1] != null && "Combat".equals(id)) {
    a.add("N0"); a.add(m[2] == null ? "" : m[2]);
    a.add("S0"); a.add(m[3] == null ? "" : m[3]);
  } else if''', '''  if (m != null && m.length > 3 && m[1] != null && "Combat".equals(id)) {
    a.add("N0"); a.add(m[2] == null ? "" : m[2]);
    a.add("S0"); a.add(m[3] == null ? "" : m[3]);
  } else if (m != null && m.length > 8 && m[1] != null && "Abilities".equals(id)) {
    a.add("N0"); a.add(m[2] == null ? "" : m[2]);
    a.add("S0"); a.add(m[3] == null ? "" : m[3]);
    a.add("N1"); a.add(m[7] == null ? "" : m[7]);
    a.add("S1"); a.add(m[8] == null ? "" : m[8]);
  } else if''')
rep('''  if ("Skills".equals(id)) {{
    int fs = fsOf({SKL_FS}, sc, minFs);
    for (int i = 0;''', '''  if ("Abilities".equals(id)) {{
    int fs = fsOf({ABL_FS}, sc, minFs);
    for (int k = 0; k < 2; k++) {{
      int o = 2 + 5 * k;
      if (m.length <= o + 1) break;
      int lw = textW(m[o], fs, bold);
      String v = m[o + 1];
      if (v != null && v.length() > 0) lw = lw + gap + textW(v, fs, bold);
      if (lw > w) w = lw;
    }}
    if (m.length > 13 && "1".equals(m[13])) {{ int ih = {ABL_ICON} * sc / 100; if (ih < 1) ih = 1; w = w + ih + {ABL_IGAP} * sc / 100; }}
    return w;
  }}
  if ("Skills".equals(id)) {{
    int fs = fsOf({SKL_FS}, sc, minFs);
    for (int i = 0;''')
rep('''  if ("Combat".equals(id)) { int cp = 3 * sc / 100; int cr = 20 * sc / 100; if (m != null && m.length > 4 && m[4] != null) { int cb = 6 * sc / 100; if (cb < 1) cb = 1; return cp + cr + cb + 8 * sc / 100; } return cp + cr + cp; }
''', '''  if ("Combat".equals(id)) { int cp = 3 * sc / 100; int cr = 20 * sc / 100; if (m != null && m.length > 4 && m[4] != null) { int cb = 6 * sc / 100; if (cb < 1) cb = 1; return cp + cr + cb + 8 * sc / 100; } return cp + cr + cp; }
  if ("Abilities".equals(id)) { int ap = 3 * sc / 100; int ar = 20 * sc / 100; int ab = 4 * sc / 100; if (ab < 1) ab = 1; return ap + 2 * (ar + ab) + 2 * sc / 100 + 6 * sc / 100; }
''')

# ---------------- the Abilities markup + barPairs + multiBody ----------------
rep('''# the bar Value text of a shown Combat model (null = no bar: hidden, out of combat, the stand-in, every other widget)
''', r'''# 0.3.18 Abilities markup (FLAT, the widget Group's direct children): per row the icon (a Group with the picture as its Background), the
# name (Start, after the icon column), the right text (End) and, while it cools down, the vanilla ProgressBar under the name. Grey rows =
# the party grey text + grey glow (GREY / GREYG); the rest the widget's own colour and glow
wid.addMethod(CtNewMethod.make(f"""
public static String abilBody(String base, {PKG}.WLayout l, int sc, String[] m, int minFs, int w) {{
  int p = padMl(sc, minFs);
  int tp = {ABL_TP} * sc / 100; int rh = {ABL_ROW} * sc / 100; int gp = {ABL_GAP} * sc / 100;
  int bh = {ABL_BAR} * sc / 100; if (bh < 1) bh = 1;
  int fs = {ABL_FS} * sc / 100; if (fs < minFs) fs = minFs;
  boolean icons = m != null && m.length > 13 && "1".equals(m[13]);
  int ih = {ABL_ICON} * sc / 100; if (ih < 1) ih = 1;
  int x0 = icons ? p + ih + {ABL_IGAP} * sc / 100 : p;
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < 2; k++) {{
    int o = 2 + 5 * k;
    int y = tp + k * (rh + bh + gp);
    String tone = (m == null || m.length <= o + 3 || m[o + 3] == null) ? "n" : m[o + 3];
    boolean grey = "g".equals(tone);
    String col = grey ? GREY : hexOf(l.col);
    String gcol = grey ? GREYG : glowHex(l) + "(0.45)";
    if (icons && m[o + 4] != null) sb.append("Group #").append(base).append("I").append(k).append(" {{ Anchor: (Left: ").append(p).append(", Top: ").append(y + (rh - ih) / 2).append(", Width: ").append(ih).append(", Height: ").append(ih).append("); Background: \\"").append(m[o + 4]).append("\\"; }} ");
    sb.append(lineS(base + "N" + k, x0, y, w, rh, fs, l, col, gcol));
    sb.append(lineE(base + "S" + k, p, y, w, rh, fs, l, col, gcol));
    if (m != null && m.length > o + 2 && m[o + 2] != null) {{
      int bw = w - p - x0; if (bw < 1) bw = 1;
      sb.append("ProgressBar #").append(base).append("Bar").append(k).append(" {{ Anchor: (Left: ").append(x0).append(", Top: ").append(y + rh).append(", Width: ").append(bw).append(", Height: ").append(bh).append("); Background: \\"{CMB_TRACK}\\"; BarTexturePath: \\"{CMB_FILL}\\"; Value: ").append(m[o + 2]).append("; }} ");
    }}
  }}
  return sb.toString();
}}""", wid))
# the bar Value text of a shown Combat model (null = no bar: hidden, out of combat, the stand-in, every other widget)
''')
rep('''public static String barOf(String id, String[] m) {
  if (!"Combat".equals(id) || m == null || m.length < 5 || m[1] == null) return null;
  return m[4];
}""", wid))''', '''public static String barOf(String id, String[] m) {
  if (!"Combat".equals(id) || m == null || m.length < 5 || m[1] == null) return null;
  return m[4];
}""", wid))
# 0.3.18: every bar of a shown model as (element suffix, Value text) pairs: Combat "Bar" (= barOf), Abilities "Bar0" / "Bar1" (rows cooling down)
wid.addMethod(CtNewMethod.make("""
public static String[] barPairs(String id, String[] m) {
  if (m == null || m.length < 2 || m[1] == null) return new String[0];
  if ("Combat".equals(id)) {
    String v = barOf(id, m);
    if (v != null) return new String[] { "Bar", v };
    return new String[0];
  }
  if ("Abilities".equals(id) && m.length > 9) {
    if (m[4] != null && m[9] != null) return new String[] { "Bar0", m[4], "Bar1", m[9] };
    if (m[4] != null) return new String[] { "Bar0", m[4] };
    if (m[9] != null) return new String[] { "Bar1", m[9] };
  }
  return new String[0];
}""", wid))''')
rep('''  if ("Combat".equals(id)) return combatBody(base, l, sc, m, minFs, w);
  if ("Skills".equals(id)) return skillsBody(base, l, sc, m, minFs, w);''', '''  if ("Combat".equals(id)) return combatBody(base, l, sc, m, minFs, w);
  if ("Abilities".equals(id)) return abilBody(base, l, sc, m, minFs, w);
  if ("Skills".equals(id)) return skillsBody(base, l, sc, m, minFs, w);''')

# ---------------- HudMain.fill: every bar (Combat as before, Abilities' two) ----------------
rep('''      String bv = {PKG}.Widgets.barOf(ids[i], mm);
      if (bv != null) {{
        String bk = ids[i] + ":Bar";
        String bp = (String) this.last.get(bk);
        if (full || bp == null || !bp.equals(bv)) {{
          this.last.put(bk, bv);
          float fv = 0.0f;
          try {{ fv = Float.parseFloat(bv); }} catch (Throwable x) {{ fv = 0.0f; }}
          b.set("#SkyyW" + ids[i] + "Bar.Value", fv);
        }}
      }}''', '''      String[] bps = {PKG}.Widgets.barPairs(ids[i], mm);   // 0.3.18: Combat "Bar" (as before) + Abilities "Bar0" / "Bar1"
      for (int q = 0; q + 1 < bps.length; q += 2) {{
        String bk = ids[i] + ":" + bps[q];
        String bv = bps[q + 1];
        String bp = (String) this.last.get(bk);
        if (full || bp == null || !bp.equals(bv)) {{
          this.last.put(bk, bv);
          float fv = 0.0f;
          try {{ fv = Float.parseFloat(bv); }} catch (Throwable x) {{ fv = 0.0f; }}
          b.set("#SkyyW" + ids[i] + bps[q] + ".Value", fv);
        }}
      }}''')

# ---------------- SettingsPage: the preview text + the Icons Show / Hide row ----------------
rep('''  if ("Skills".equals(this.wid) || "Combat".equals(this.wid)) {{
    try {{''', '''  if ("Skills".equals(this.wid) || "Combat".equals(this.wid) || "Abilities".equals(this.wid)) {{
    try {{''')
rep(r'''    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 360, Height: 44); Text: \\"Show adds a grey line out of combat\\"; Style: (FontSize: 16, TextColor: #9fb8d0, VerticalAlignment: Center); }}");
    ev.addEventBinding({BT}.Activating, "#SkyySetOptOn", {EVD}.of("a", "opton"));
    ev.addEventBinding({BT}.Activating, "#SkyySetOptOff", {EVD}.of("a", "optoff"));
  }}''', r'''    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 360, Height: 44); Text: \\"Show adds a grey line out of combat\\"; Style: (FontSize: 16, TextColor: #9fb8d0, VerticalAlignment: Center); }}");
    ev.addEventBinding({BT}.Activating, "#SkyySetOptOn", {EVD}.of("a", "opton"));
    ev.addEventBinding({BT}.Activating, "#SkyySetOptOff", {EVD}.of("a", "optoff"));
  }} else if ("Abilities".equals(this.wid)) {{
    // 0.3.18 Abilities: the ability pictures next to the names - Show or Hide (names only); the Party / Guild / Combat option row's place,
    // ids and payloads. FIX ROUND: Hide = WLayout.opt true = the DEFAULT (pack pictures in a HUD are UNVERIFIED) -> Show = #SkyySetOptOff
    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 60, Height: 44); Text: \\"\\"; }}");
    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 250, Height: 44); Text: \\"Icons\\"; " + rl + " }}");
    b.appendInline("#SkyySetRow2", "TextButton #SkyySetOptOff {{ Anchor: (Width: 104, Height: 44); Text: \\"Show\\"; " + (l.opt ? bs : on) + " }}");
    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 8, Height: 44); Text: \\"\\"; }}");
    b.appendInline("#SkyySetRow2", "TextButton #SkyySetOptOn {{ Anchor: (Width: 104, Height: 44); Text: \\"Hide\\"; " + (l.opt ? on : bs) + " }}");
    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 20, Height: 44); Text: \\"\\"; }}");
    b.appendInline("#SkyySetRow2", "Label {{ Anchor: (Width: 360, Height: 44); Text: \\"Hide shows the ability names only\\"; Style: (FontSize: 16, TextColor: #9fb8d0, VerticalAlignment: Center); }}");
    ev.addEventBinding({BT}.Activating, "#SkyySetOptOn", {EVD}.of("a", "opton"));
    ev.addEventBinding({BT}.Activating, "#SkyySetOptOff", {EVD}.of("a", "optoff"));
  }}''')

# ---------------- the jar: the icons in the asset pack + the description ----------------
rep('''           OUT, {"Common/UI/Custom/SkyyHud/dot.png": png_dot, "icon-256.png": png_root})''',
    '''           OUT, dict([("Common/UI/Custom/SkyyHud/dot.png", png_dot), ("icon-256.png", png_root)]
                     + [("Common/UI/Custom/" + ABL_ICON_DIR + _i + ".png", _b) for _i, _b in sorted(ABL_ICONS.items())]))   # 0.3.18: + the ability icons''')
rep('''"SkyyHud: customizable server-side HUD. 13 widgets (14 with Dynamic Seasons) incl. a round minimap''',
    '''"SkyyHud: customizable server-side HUD. 14 widgets (15 with Dynamic Seasons) incl. Abilities (your two class abilities with icons, cost and cooldown; the crouch alts while you crouch), a round minimap''')

# ---------------- self-checks ----------------
assert '"Seasons", "Abilities"]' in s or 'IDS.append("Abilities")' in s
assert s.count('"Abilities".equals(') >= 10
assert 'b.set("#SkyyW" + ids[i] + bps[q] + ".Value", fv);' in s and 'b.set("#SkyyW" + ids[i] + "Bar.Value", fv);' not in s
assert s.count("#SkyySetOptOn") == 6 and s.count('"opton"') == 3, "the option row ids / payloads: Party / Guild + Combat + Abilities"
assert "class:fn:abil" in s and s.count("class:fn:abil") >= 2
assert "EffectTexturePath" not in s.split("public static String abilBody(")[1].split('}}""", wid))')[0], "no Effect glow in the HUD bars"
# javassist order: helpers before their callers
for a_, b_ in (("public static String combatBar(", "public static void abilRow("), ("public static void abilRow(", "public static String[] abilModelU("),
               ("public static String abilShape(", "public static String[] abilModelU("), ("public static String[] abilModelU(", "public static String[] model("),
               ("public static String[] abilSample(", "public static String[] sampleU("), ("public static String lineS(", "public static String abilBody("),
               ("public static String abilBody(", "public static String multiBody("), ("public static String barOf(", "public static String[] barPairs("),
               ("public static String[] barPairs(", "public boolean fill(")):
    assert s.index(a_) < s.index(b_), "javassist order: %s before %s" % (a_, b_)
assert "KEEP=10" in s and "KEEP=20" not in s
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.17 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines, %d changes)" % (s.count(LF), len(CHANGES)))
