"""Derive SkyyHud/build_skyyhud_0.3.13.py from the LIVE 0.3.12 (the SET pin; 0.3.12 is left untouched; line endings preserved).
0.3.13 = CONTENT-SIZED WIDGET BOXES + the Combat widget's two colours (Skyy 2026-10-03, OPEN-QUESTIONS LOCKED 2026-10-03: "make the game
clock box smaller so it can go closer in a corner. (try to keep the boxes pretty small, whatever the gap above and below for the border,
keep the same gap on the sides." + "combat widget works. (but in the settings add the in combat and out of combat colors.").
  - every widget box is as wide as its text plus the same padding on the left / right as above / below (the visual gap from the box top
    to the top of the letters); widths measured with the vanilla kit's font table (tools/skyyui.py text_width - the client's own Nunito
    Sans glyph advances), generated into the build script by THIS patch (the build itself does not import the kit: its old-style colours
    would flood lint's kit-colour warnings); heights and every saved position stay as they were
  - the clamps keep the old maximum box (WLayout.bw / bh), so a box can never leave the screen and old layouts load with the same numbers
  - the HUD re-sends a widget whose text needs a wider box at once (the proven shape re-send, at most once per 1.5 s) and a narrower one
    after 15 s (no flapping on the 1 s tick); Party stats are measured with the current values padded to the max's digits
  - Combat: "In combat" colour (the old Color row, Default = red) + a new "Out of combat" colour row (Default = the grey), saved as a
    14th layout field only when picked; the Settings page previews both, the editor sample uses them
Harness: python SkyyHud/test_skyyhud_0.3.13.py (bare JVM, see its docstring).
To regenerate, delete SkyyHud/build_skyyhud_0.3.13.py first (the script refuses to overwrite it).
"""
import os
import sys
import json
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyui as SUI      # the vanilla UI kit: ONLY its font table is used here (text_width / line_height / font_table)

src = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.12.py")
dst = os.path.join(ROOT, "SkyyHud", "build_skyyhud_0.3.13.py")
assert not os.path.exists(dst), "refusing to overwrite " + dst
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:90])
    s = s.replace(old, new)


# ---------------- the font numbers (read-only from the client; the kit's own tables) ----------------
# The box widths are measured with the kit: every glyph's advance = skyyui.text_width(ch, 1000, bold) (NunitoSans ExtraBold for bold
# text, Medium otherwise; a glyph the table lacks counts as wide as M - the kit's rule). A build without the client's font tables would
# fall back to the kit's per-class averages, so the patch refuses to run without them (the build needs the game's server jar anyway).
for _bold in (True, False):
    if SUI.font_table("Default", _bold) is None:
        raise SystemExit("the client's font tables are missing (%s) - SkyyHud 0.3.13 measures its boxes with them" % SUI.FONT_DIR)
FIRST, LAST = 32, 255           # printable ASCII + Latin-1 (127-159 are control codes: the table has none -> as wide as M)


def adv_table(bold):
    out = []
    for c in range(FIRST, LAST + 1):
        v = SUI.text_width(chr(c), 1000, bold)
        assert abs(v - round(v)) < 1e-6, "advance of U+%04X is not a whole milli-em: %r" % (c, v)
        out.append(int(round(v)))
    return out


ADV_B, ADV_M = adv_table(True), adv_table(False)
ADV_BX, ADV_MX = int(round(SUI.text_width("M", 1000, True))), int(round(SUI.text_width("M", 1000, False)))
assert ADV_B[ord("0") - FIRST] == 600 and all(ADV_B[ord(d) - FIRST] == 600 for d in "0123456789"), "tabular digits (0.6 em) expected"
assert all(ADV_M[ord(d) - FIRST] == 600 for d in "0123456789")
# the vertical numbers (not in the kit): line height = the kit's line_height (1.364 em); ascender from the same font atlas JSON; cap
# height from the font file's OS/2 table (sCapHeight 705 / 1000 in both weights). The client centres the line box in the label, so
# the caps' top sits CAPK x font above the row's middle: LH / 2 - ascender + cap = 0.682 - 1.011 + 0.705 = 0.376.
FONT_LH = round(SUI.line_height(1, "Default", True), 6)
_fj = json.load(open(os.path.join(SUI.FONT_DIR, "NunitoSans-ExtraBold.json"), encoding="utf-8"))["metrics"]
FONT_ASC = round(abs(float(_fj["ascender"])), 6)


def _cap(path):
    d = open(path, "rb").read()
    tabs = {}
    for i in range(struct.unpack(">H", d[4:6])[0]):
        tag, _cs, off, ln = struct.unpack(">4sIII", d[12 + 16 * i:28 + 16 * i])
        tabs[tag.decode("latin-1")] = (off, ln)
    upem = struct.unpack(">H", d[tabs["head"][0] + 18:tabs["head"][0] + 20])[0]
    o = tabs["OS/2"][0]
    assert struct.unpack(">H", d[o:o + 2])[0] >= 2, "OS/2 table without sCapHeight"
    return struct.unpack(">h", d[o + 88:o + 90])[0] / float(upem)


FONT_CAP = round(_cap(os.path.join(SUI.FONT_DIR, "NunitoSans-ExtraBold.ttf")), 6)
assert abs(_cap(os.path.join(SUI.FONT_DIR, "NunitoSans-Medium.ttf")) - FONT_CAP) < 1e-9, "both weights share the cap height"
assert (FONT_LH, FONT_ASC, FONT_CAP) == (1.364, 1.011, 0.705), "Nunito Sans metrics changed: %s" % ((FONT_LH, FONT_ASC, FONT_CAP),)
CAPK = round(FONT_LH / 2 - FONT_ASC + FONT_CAP, 6)
assert CAPK == 0.376


def pylist(name, vals, per=24):
    rows = [", ".join(str(v) for v in vals[i:i + per]) for i in range(0, len(vals), per)]
    return name + " = [\n    " + ",\n    ".join(rows) + "]\n"


# ---------------- docstring + version ----------------
rep('''"""SkyyHud 0.3.12 - build script (javassist via jpype).
Run:   python build_skyyhud_0.3.12.py            -> SkyyHud/SkyyHud-0.3.12.jar
       (deploys only through tools/deploy_set.py - never pass --deploy here)
0.3.12 (generated by tools/hud_0_3_12_patch.py from 0.3.11): the COMBAT INDICATOR widget''', '''"""SkyyHud 0.3.13 - build script (javassist via jpype).
Run:   python build_skyyhud_0.3.13.py            -> SkyyHud/SkyyHud-0.3.13.jar
       (deploys only through tools/deploy_set.py - never pass --deploy here)
0.3.13 (generated by tools/hud_0_3_13_patch.py from 0.3.12): CONTENT-SIZED WIDGET BOXES + the Combat widget's two colours (Skyy
  2026-10-03, OPEN-QUESTIONS LOCKED 2026-10-03: "make the game clock box smaller so it can go closer in a corner. (try to keep the boxes
  pretty small, whatever the gap above and below for the border, keep the same gap on the sides." + "combat widget works. (but in the
  settings add the in combat and out of combat colors.").
  - EVERY widget box is now as wide as its text plus a padding P on the left and right that equals the gap above / below the text: the
    visual gap from the box top to the top of the letters. The client centres a label's line box (1.364 em) and the caps reach 0.705 em
    above the baseline (1.011 em under the line top), so in a row of height h a font of fs px leaves h / 2 - 0.376 fs above the caps.
    P(size) = round(that) on the widget's own first row (one-line widgets: the 26 x size row, font 12 x size, at least 6; Party / Guild
    / Skills / Combat: their first row, 3 + 20 x size, font 12; the editor uses its own 2/3 size, font at least 5):
        size        50  60  70  75  80  90 100 110 120 125 130 140 150 160 170 180 190 200 %
        P one-line   4   5   6   6   7   8   8   9  10  10  11  12  13  13  14  15  16  17 px
        P multi      4   4   6   6   7   7   8   9  10  10  10  12  12  13  14  15  16  17 px
    Widths are measured with the vanilla kit's font table (tools/skyyui.py text_width: the client's own Nunito Sans advances - ExtraBold
    for bold text, Medium otherwise, a glyph the table lacks as wide as M; digits are tabular 0.6 em, so a clock never changes width),
    copied into Widgets.ADVB / ADVM by tools/hud_0_3_13_patch.py (U+0020 - U+00FF). No fixed wide minimums:
      one-line widgets  text width + 2P (Game Clock "12:30" at 100%: 48 x 26, was 180 x 26; 50%: 24 x 13; 200%: 98 x 52)
      Party / Guild / Skills / Combat   the widest line + 2P: Party name + P + stats (stats measured with each current value padded to
                        the max's digits - "HP 9/100" counts as "HP 100/100", so a fight never resizes it), Guild the widest of its
                        lines, Skills the widest "name  P  level", Combat "In combat  P  6s" (the bar spans the text width). Names
                        start at P, values end at P from the right edge; every line's label reaches past its text to a couple of
                        px from the box edge, so a client drawing a text a little wider than the table never cuts it (one-line
                        labels fill the box: 2P of room).
    Heights are unchanged (they already are text + the same gap: 8.5 px over the caps, 8-9 px under the last baseline at 100%) except
    the Combat widget IN combat: the pad under the bar is 8 px at 100% like the others (box 37 high, was 34 with a 5 px pad).
  - The CLAMPS keep the old maximum box (WLayout.bw x bh: 180 x 26 for the one-line widgets, Party 340, Guild 260, Skills 180, Combat
    180 x 37), and a drawn box is never wider than it - so a box can never leave the screen, and every 0.3.12 layout file, export code,
    profile and server default loads with exactly the same anchor / x / y / size (load-time clamps unchanged; Combat's taller clamp
    box only matters within 3 px of the bottom edge). Positions move only by the padding change: a box keeps its anchored edge (its
    x / y are unchanged) and only the far edge moves in, so one-line text (centred in its box) moves (old width - new width) / 2
    toward the anchored side, and in Party / Guild / Skills / Combat the column next to the anchored edge stays (P from it instead of
    8 px) while the far column moves in by (old width - new width); centred anchors keep their centre. Nothing moves vertically except
    the in-combat Combat box (3 px taller at 100%, growing away from its anchored edge). Game Clock at 100%: its text sits 8 px from
    the box edge (was 74 px: the text moves 66 px toward its corner); at 170% (Skyy's layout) 14 px (was 126 px: 112 px closer).
  - Corners: a widget anchored to a corner with x = y = 0 has its text P px from both screen edges - the Game Clock reaches all four
    corners at every size (drag it into the corner - a drag lands within a cell of it, or exactly in it when dragged past it - and
    finish with the arrows: Step 1 / 5 / 10 / 25 stop at 0; Snap to puts a box 8 px from the edges as before).
  - The editor draws, outlines, picks, drags and snaps the drawn box (EditorPage.widthOf: the width of what the HUD shows now; multi-line
    previews are placed by their anchored edge like the 0.3.9 heights). Arrows / Size / Snap to / clamps use the maximum box exactly as
    in 0.3.12 (byte-identical layouts after the same clicks); a drag drops the drawn box where it was dropped (nearest corner re-picked
    by the drawn box's centre, clamped to the screen).
  - Text that changes length (coordinates, zone, coins, session time ...): the HUD remembers the width each widget was built with
    (HudMain.wb). A tick whose text needs MORE room asks for the shape re-send at once (the proven 0.3.8 path: the whole HUD, at most
    once per 1.5 s - the text may be clipped for that moment); a text that fits a box narrower by a pixel or more for 15 s (SHRINK) asks
    for one re-send that shrinks it. So the box follows its text without re-sending on every tick: a clock never re-sends, coordinates
    when a digit or a sign comes or goes, the session time when the minutes gain a digit. No confirm send for a width change.
  - COMBAT COLOURS: the widget's Settings page has two colour rows with the same 13 choices as every widget: "In combat" (the old Color
    row: WLayout.col, payload col:<key>, Default = the vanilla red #ff6b6b - its swatch shows red now) and "Out of combat" (NEW
    WLayout.ocol, payload ocol:<key>, ids #SkyySetOc<Key>, Default = the grey #8b949e of 0.3.12 - its swatch shows grey). Out of combat
    with a picked colour the text is that colour and glow Same follows it; with Default the line keeps 0.3.12's grey text and quiet
    grey glow byte for byte. Saved per player in the layout line: a 14th field written ONLY when the out-of-combat colour is not
    Default - "en,anchor,x,y,size,bg,col,bold,italic,glow,glowColor,opt,lines,ocol" with lines "-" for a widget without lines
    (e.g. Combat=1,t,0,130,100,1,def,1,0,0,def,1,-,aqua; export codes use ":"). 0.3.12 reads such a line with every other field intact
    and ignores the 14th (parseInt("-") fails inside its own try), so a rollback only loses the out-of-combat colour. Reset style
    puts it back to Default too. The Settings page (1500 x 924 for Combat: 882 px of rows + 20 padding) previews both: "In combat 4s" in the
    in-combat colour and "Out of combat" in the out-of-combat colour, each on the dark and the bright backdrop (the hint says when
    SkyySkills 0.4.13 is missing); the editor's Combat sample (hidden widget) uses the in-combat colour and the real out-of-combat
    line (Out of combat: Show) its colour.
  - Unchanged: the layout / code / profile format of every other field, widget ids, texts, the bridge reads, commands, permissions,
    the admin rows and config file, the 1 s tick, the Combat countdown / bar updates. No new config row, command or player switch.
0.3.12 (generated by tools/hud_0_3_12_patch.py from 0.3.11): the COMBAT INDICATOR widget''')
rep('''VERSION = "0.3.12"''', '''VERSION = "0.3.13"''')

# ---------------- constants: the Combat pad under the bar + the content-sizing numbers ----------------
rep('''CMB_TP, CMB_ROW, CMB_BAR, CMB_BP, CMB_VW, CMB_FS = 3, 20, 6, 5, 40, 12   # top pad, text row, bar, pad under the bar, countdown column, font
SIZES["Combat"] = (180, CMB_TP + CMB_ROW + CMB_BAR + CMB_BP)''', '''# 0.3.13: the pad under the bar is 8 (the side / top padding at 100%, was 5); the countdown column is content-sized (CMB_VW gone)
CMB_TP, CMB_ROW, CMB_BAR, CMB_BP, CMB_FS = 3, 20, 6, 8, 12   # top pad, text row, bar, pad under the bar, font
SIZES["Combat"] = (180, CMB_TP + CMB_ROW + CMB_BAR + CMB_BP)''')
rep('''assert SIZES["Combat"] == (180, 34) and DEFAULTS["Combat"][1] == "t"
assert (CMB_TP, CMB_ROW, CMB_BAR, CMB_BP) == (3, 20, 6, 5), "Widgets.bodyH (not an f-string) spells the Combat maths out as 3 / 20 / 6 / 5"
''', '''assert SIZES["Combat"] == (180, 37) and DEFAULTS["Combat"][1] == "t"
assert (CMB_TP, CMB_ROW, CMB_BAR, CMB_BP) == (3, 20, 6, 8), "Widgets.bodyH (not an f-string) spells the Combat maths out as 3 / 20 / 6 / 8"
# 0.3.13 CONTENT-SIZED BOXES (see the docstring): the padding P is measured on the one-line row (LINE_H high, font LINE_FS at 100%%;
# Party / Guild / Skills / Combat on their own first row, Widgets.padMl);
# the font numbers come from the vanilla kit (tools/skyyui.py font_table / text_width / line_height - the client's Nunito Sans tables),
# copied in by tools/hud_0_3_13_patch.py so this build does not need the kit
LINE_H, LINE_FS = 26, 12
FONT_LH, FONT_ASC, FONT_CAP = %r, %r, %r      # line height, ascender (font atlas JSON), cap height (OS/2 sCapHeight), em
CAPK = %r                                       # LH / 2 - ascender + cap: the caps' top sits CAPK x font above the row's middle
SHRINK_MS = 15000                               # a box narrower by >= 1 px for this long is re-sent smaller (growing is at once)
ADV_FIRST = %d                                  # ADV_B / ADV_M = advances in milli-em of U+%04X..U+%04X (bold = ExtraBold)
''' % (FONT_LH, FONT_ASC, FONT_CAP, CAPK, FIRST, FIRST, LAST) + pylist("ADV_B", ADV_B) + pylist("ADV_M", ADV_M) + '''ADV_BX, ADV_MX = %d, %d                         # any other character: as wide as M (the kit's rule)
assert len(ADV_B) == len(ADV_M) == %d and CAPK == round(FONT_LH / 2 - FONT_ASC + FONT_CAP, 6)
''' % (ADV_BX, ADV_MX, LAST - FIRST + 1))

# ---------------- WLayout: the out-of-combat colour (field 14) ----------------
rep('''for f in ("public int lines;", "public int ldef;"):
    wl.addField(CtField.make(f, wl))
''', '''for f in ("public int lines;", "public int ldef;"):
    wl.addField(CtField.make(f, wl))
# 0.3.13: ocol = the Combat widget's out-of-combat colour (palette key; "def" = the 0.3.12 grey), the layout line's 14th field
wl.addField(CtField.make("public String ocol;", wl))
''')
rep('''  this.lines = -1; this.ldef = -1;
}""", wl))''', '''  this.lines = -1; this.ldef = -1;
  this.ocol = "def";
}""", wl))''')
rep('''public String ser() {
  boolean lx = ldef >= 0 && lines > 0 && lines != ldef;
  String s = (en ? "1" : "0") + "," + anchor + "," + dx + "," + dy + "," + scale + "," + (bg ? "1" : "0");
  if (styleDefault() && opt && !lx) return s;
  s = s + "," + col + "," + (bold ? "1" : "0") + "," + (ital ? "1" : "0") + "," + (glow ? "1" : "0") + "," + gcol;
  if (!lx) {
    if (opt) return s;
    return s + ",0";
  }
  return s + "," + (opt ? "1" : "0") + "," + lines;
}""", wl))''', '''public String ser() {
  boolean lx = ldef >= 0 && lines > 0 && lines != ldef;
  boolean ox = ocol != null && !"def".equals(ocol);
  String s = (en ? "1" : "0") + "," + anchor + "," + dx + "," + dy + "," + scale + "," + (bg ? "1" : "0");
  if (styleDefault() && opt && !lx && !ox) return s;
  s = s + "," + col + "," + (bold ? "1" : "0") + "," + (ital ? "1" : "0") + "," + (glow ? "1" : "0") + "," + gcol;
  if (!lx && !ox) {
    if (opt) return s;
    return s + ",0";
  }
  s = s + "," + (opt ? "1" : "0") + "," + (lx ? String.valueOf(lines) : "-");
  if (!ox) return s;
  return s + "," + ocol;
}""", wl))''')
rep('''    if (p.length > 12) {{ try {{ int lv = Integer.parseInt(p[12].trim()); if (lv > 0) w.lines = lv; }} catch (Throwable x) {{ }} }}
    return w;''', '''    if (p.length > 12) {{ try {{ int lv = Integer.parseInt(p[12].trim()); if (lv > 0) w.lines = lv; }} catch (Throwable x) {{ }} }}
    if (p.length > 13) {{ String o = p[13].trim(); int oi = palIdx(o); if (oi >= 0 && oi < TEXT_N) w.ocol = o; }}
    return w;''')

# ---------------- Widgets: the font table, the padding and the content widths (before anchorSrcWH, javassist order) ----------------
rep('''# 0.3.9: the widget Group's Anchor for a box of w x h (h = the height being sent: one-line hMax, Party / Guild the drawn rows).''',
    r'''# 0.3.13 CONTENT-SIZED BOXES. The vanilla kit's font table (advances in milli-em of U+0020..U+00FF, ExtraBold for bold text, Medium
# otherwise; any other character as wide as M), the padding P and the widths. Pure arithmetic - any thread.
wid.addField(CtField.make("public static final int[] ADVB = new int[] { %s };" % ", ".join(str(v) for v in ADV_B), wid))
wid.addField(CtField.make("public static final int[] ADVM = new int[] { %s };" % ", ".join(str(v) for v in ADV_M), wid))
wid.addField(CtField.make("public static final int ADVBX = %d;" % ADV_BX, wid))
wid.addField(CtField.make("public static final int ADVMX = %d;" % ADV_MX, wid))
wid.addField(CtField.make("public static final double CAPK = %r;" % CAPK, wid))
wid.addField(CtField.make("public static final long SHRINK = %dL;" % SHRINK_MS, wid))
wid.addMethod(CtNewMethod.make(f"""
public static int advOf(char c, boolean bold) {{
  if (c >= {ADV_FIRST} && c < {ADV_FIRST} + ADVB.length) return bold ? ADVB[c - {ADV_FIRST}] : ADVM[c - {ADV_FIRST}];
  return bold ? ADVBX : ADVMX;
}}""", wid))
wid.addMethod(CtNewMethod.make("""
public static int advMilli(String s, boolean bold) {
  if (s == null) return 0;
  int t = 0;
  for (int i = 0; i < s.length(); i++) t += advOf(s.charAt(i), bold);
  return t;
}""", wid))
wid.addMethod(CtNewMethod.make("""
public static int pxOf(int milli, int fs) {
  long v = (long) milli * (long) fs;
  return (int) ((v + 999L) / 1000L);
}""", wid))
# px width of one line of text at fs px, rounded up (the kit's text_width; no kerning - the atlases carry none)
wid.addMethod(CtNewMethod.make("""
public static int textW(String s, int fs, boolean bold) {
  return pxOf(advMilli(s, bold), fs);
}""", wid))
# Party stats: every "a/b" counts with a padded to b's digits ("HP 9/100" is as wide as "HP 100/100" - digits are tabular), so a
# fight never resizes the box; a current value above its max counts as it is
wid.addMethod(CtNewMethod.make("""
public static int textWn(String s, int fs, boolean bold) {
  int t = advMilli(s, bold);
  if (s != null) {
    int n = s.length();
    int i = 0;
    while (i < n) {
      char c = s.charAt(i);
      if (c < '0' || c > '9') { i++; continue; }
      int a = i;
      while (i < n && s.charAt(i) >= '0' && s.charAt(i) <= '9') i++;
      if (i < n && s.charAt(i) == '/') {
        int j = i + 1;
        while (j < n && s.charAt(j) >= '0' && s.charAt(j) <= '9') j++;
        int more = (j - i - 1) - (i - a);
        if (more > 0) t += more * advOf('0', bold);
      }
    }
  }
  return pxOf(t, fs);
}""", wid))
wid.addMethod(CtNewMethod.make("""
public static int fsOf(int base, int sc, int minFs) {
  int fs = base * sc / 100;
  return fs < minFs ? minFs : fs;
}""", wid))
# the visual gap above the caps of an fs px line centred in an h px row: h / 2 - CAPK x fs, rounded, at least 1
wid.addMethod(CtNewMethod.make("""
public static int padOf(int h, int fs) {
  long p = Math.round(h / 2.0 - CAPK * fs);
  return p < 1L ? 1 : (int) p;
}""", wid))
# P at size sc for the one-line widgets: measured on their 26 px row (the HUD passes minFs 6, the editor's 2/3 previews 5)
wid.addMethod(CtNewMethod.make(f"""
public static int padSc(int sc, int minFs) {{
  return padOf({LINE_H} * sc / 100, fsOf({LINE_FS}, sc, minFs));
}}""", wid))
# Party / Guild / Skills / Combat: P measured on their own first row (3 + 20 px at 100%, font 12) - within a pixel of padSc, but it is
# the gap these boxes really have over their first line
wid.addMethod(CtNewMethod.make("""
public static int padMl(int sc, int minFs) {
  long p = Math.round(3 * sc / 100 + (20 * sc / 100) / 2.0 - CAPK * fsOf(12, sc, minFs));
  return p < 1L ? 1 : (int) p;
}""", wid))
# a drawn box is never wider than the clamp box (the old maximum), never below 1
wid.addMethod(CtNewMethod.make(f"""
public static int capW(int w, {PKG}.WLayout l, int sc) {{
  int mx = l.bw * sc / 100;
  if (w > mx) w = mx;
  return w < 1 ? 1 : w;
}}""", wid))
# a one-line widget's box for text t at size sc: the text + P on each side
wid.addMethod(CtNewMethod.make(f"""
public static int lineW({PKG}.WLayout l, String t, int sc, int minFs) {{
  return capW(textW(t, fsOf({LINE_FS}, sc, minFs), l.bold) + 2 * padSc(sc, minFs), l, sc);
}}""", wid))
# a multi-line widget's widest line at size sc (the fonts its body uses; name and value columns P apart)
wid.addMethod(CtNewMethod.make(f"""
public static int innerW(String id, String[] m, int sc, int minFs, boolean bold) {{
  if (m == null) return 0;
  int gap = padMl(sc, minFs);
  int w = 0;
  if ("Combat".equals(id)) {{
    int fs = fsOf({CMB_FS}, sc, minFs);
    w = textW(m.length > 2 ? m[2] : null, fs, bold);
    String v = m.length > 3 ? m[3] : null;
    if (v != null && v.length() > 0) w = w + gap + textW(v, fs, bold);
    return w;
  }}
  if ("Skills".equals(id)) {{
    int fs = fsOf({SKL_FS}, sc, minFs);
    for (int i = 0; i < {PKG}.WLayout.LINE_N && 3 + 2 * i < m.length; i++) {{
      if (m[2 + 2 * i] == null) break;
      String v = m[3 + 2 * i];
      int lw = textW(m[2 + 2 * i], fs, bold);
      if (v != null && v.length() > 0) lw = lw + gap + textW(v, fs, bold);
      if (lw > w) w = lw;
    }}
    return w;
  }}
  int fsT = fsOf(12, sc, minFs); int fsR = fsOf(11, sc, minFs);
  if (m.length > 1 && m[1] != null) w = textW(m[1], fsT, bold);
  if ("Party".equals(id)) {{
    for (int i = 0; i < 5 && 4 + 3 * i < m.length; i++) {{
      if (m[2 + 3 * i] == null) break;
      int lw = textW(m[2 + 3 * i], fsR, bold) + gap + textWn(m[3 + 3 * i], fsR, bold);
      if (lw > w) w = lw;
    }}
    return w;
  }}
  if (m.length >= 6) {{
    int fsN = fsOf(10, sc, minFs);
    int a = textW(m[2], fsR, bold); if (a > w) w = a;
    a = textW(m[3], fsR, bold); if (a > w) w = a;
    if (m[4] != null) {{ a = textW(m[4], fsN, bold); if (a > w) w = a; }}
    if (m[5] != null) {{ a = textW(m[5], fsN, bold); if (a > w) w = a; }}
  }}
  return w;
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static int multiW(String id, {PKG}.WLayout l, String[] m, int sc, int minFs) {{
  return capW(innerW(id, m, sc, minFs, l.bold) + 2 * padMl(sc, minFs), l, sc);
}}""", wid))
# 0.3.9: the widget Group's Anchor for a box of w x h (h = the height being sent: one-line hMax, Party / Guild the drawn rows).''')
rep('''wid.addMethod(CtNewMethod.make(f"""
public static String anchorSrcH({PKG}.WLayout l, int h) {{
  int w = l.bw * l.scale / 100;
  String a = l.anchor;''', '''# 0.3.13: the width is passed in (the drawn box); anchorSrcH keeps the old maximum-box call
wid.addMethod(CtNewMethod.make(f"""
public static String anchorSrcWH({PKG}.WLayout l, int w, int h) {{
  String a = l.anchor;''')
rep('''  return "(" + va + ": " + my + ", " + ha + ": " + mx + ", Width: " + w + ", Height: " + h + ")";
}}""", wid))
''', '''  return "(" + va + ": " + my + ", " + ha + ": " + mx + ", Width: " + w + ", Height: " + h + ")";
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static String anchorSrcH({PKG}.WLayout l, int h) {{
  return anchorSrcWH(l, l.bw * l.scale / 100, h);
}}""", wid))
''')

# ---------------- Widgets: lineAt (a line whose TEXT box is x, w - lineSrc's inset added outside) ----------------
rep('''# rows actually drawn (Party: member lines 0..5, Guild: online-name rows 0..2) and the drawn content height at size sc: ONE formula''',
    '''# 0.3.13: the lines of a multi-line widget in a box w wide with padding p. lineS: Start text that begins exactly at p; lineE: End text
# that ends exactly p before the right edge. Each label reaches past its text to the glow distance d from the box edge (lineSrc insets
# a label by d; the glow copies stay inside the box), so a client that draws a text a few px wider than the font table never cuts it
wid.addMethod(CtNewMethod.make(f"""
public static String lineS(String base, int p, int y, int w, int h, int fs, {PKG}.WLayout l, String color, String gcolor) {{
  int d = (fs * 3 + 12) / 24;
  if (d < 1) d = 1;
  int lw = w - p - d; if (lw < 1) lw = 1;
  return lineSrc(base, p - d, y, lw + 2 * d, h, fs, l, color, gcolor, "Start");
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static String lineE(String base, int p, int y, int w, int h, int fs, {PKG}.WLayout l, String color, String gcolor) {{
  int d = (fs * 3 + 12) / 24;
  if (d < 1) d = 1;
  int lw = w - p - d; if (lw < 1) lw = 1;
  return lineSrc(base, 0, y, lw + 2 * d, h, fs, l, color, gcolor, "End");
}}""", wid))
# rows actually drawn (Party: member lines 0..5, Guild: online-name rows 0..2) and the drawn content height at size sc: ONE formula''')
rep('''  if ("Combat".equals(id)) { int cp = 3 * sc / 100; int cr = 20 * sc / 100; if (m != null && m.length > 4 && m[4] != null) { int cb = 6 * sc / 100; if (cb < 1) cb = 1; return cp + cr + cb + 5 * sc / 100; } return cp + cr + cp; }''',
    '''  if ("Combat".equals(id)) { int cp = 3 * sc / 100; int cr = 20 * sc / 100; if (m != null && m.length > 4 && m[4] != null) { int cb = 6 * sc / 100; if (cb < 1) cb = 1; return cp + cr + cb + 8 * sc / 100; } return cp + cr + cp; }''')

# ---------------- Widgets: the multi-line bodies at a given box width (names at P, values ending P from the right) ----------------
rep('''public static String partyBody(String base, {PKG}.WLayout l, int sc, String[] m, int minFs) {{
  int w = l.bw * sc / 100;
  int sp = 6 * sc / 100; int tp = 3 * sc / 100;
  int th = 20 * sc / 100; int rh = 18 * sc / 100; int nw = 128 * sc / 100;
  int fsT = 12 * sc / 100; if (fsT < minFs) fsT = minFs;
  int fsR = 11 * sc / 100; if (fsR < minFs) fsR = minFs;
  int n = partyRows(m);
  StringBuilder sb = new StringBuilder();
  String col = hexOf(l.col);
  String gcol = glowHex(l) + "(0.45)";
  sb.append(lineSrc(base + "T", sp, tp, w - 2 * sp, th, fsT, l, col, gcol, "Start"));
  for (int i = 0; i < n; i++) {{
    boolean grey = "1".equals(m[4 + 3 * i]);
    String c = grey ? GREY : col;
    String g = grey ? GREYG : gcol;
    int y = tp + th + i * rh;
    sb.append(lineSrc(base + "N" + i, sp, y, nw, rh, fsR, l, c, g, "Start"));
    sb.append(lineSrc(base + "S" + i, sp + nw, y, w - 2 * sp - nw, rh, fsR, l, c, g, "End"));
  }}
  return sb.toString();
}}""", wid))''', '''public static String partyBody(String base, {PKG}.WLayout l, int sc, String[] m, int minFs, int w) {{
  int p = padMl(sc, minFs); int tp = 3 * sc / 100;
  int th = 20 * sc / 100; int rh = 18 * sc / 100;
  int fsT = 12 * sc / 100; if (fsT < minFs) fsT = minFs;
  int fsR = 11 * sc / 100; if (fsR < minFs) fsR = minFs;
  int n = partyRows(m);
  StringBuilder sb = new StringBuilder();
  String col = hexOf(l.col);
  String gcol = glowHex(l) + "(0.45)";
  sb.append(lineS(base + "T", p, tp, w, th, fsT, l, col, gcol));
  for (int i = 0; i < n; i++) {{
    boolean grey = "1".equals(m[4 + 3 * i]);
    String c = grey ? GREY : col;
    String g = grey ? GREYG : gcol;
    int y = tp + th + i * rh;
    sb.append(lineS(base + "N" + i, p, y, w, rh, fsR, l, c, g));
    sb.append(lineE(base + "S" + i, p, y, w, rh, fsR, l, c, g));
  }}
  return sb.toString();
}}""", wid))''')
rep('''public static String guildBody(String base, {PKG}.WLayout l, int sc, String[] m, int minFs) {{
  int w = l.bw * sc / 100;
  int sp = 6 * sc / 100; int tp = 3 * sc / 100;''', '''public static String guildBody(String base, {PKG}.WLayout l, int sc, String[] m, int minFs, int w) {{
  int sp = padMl(sc, minFs); int tp = 3 * sc / 100;''')
rep('''  int iw = w - 2 * sp;
  sb.append(lineSrc(base + "T", sp, tp, iw, th, fsT, l, col, gcol, "Start"));
  sb.append(lineSrc(base + "L", sp, tp + th, iw, rh, fsR, l, col, gcol, "Start"));
  sb.append(lineSrc(base + "O", sp, tp + th + rh, iw, rh, fsR, l, col, gcol, "Start"));
  if (rows > 0) sb.append(lineSrc(base + "A", sp, tp + th + 2 * rh, iw, nh, fsN, l, col, gcol, "Start"));
  if (rows > 1) sb.append(lineSrc(base + "B", sp, tp + th + 2 * rh + nh, iw, nh, fsN, l, col, gcol, "Start"));''',
    '''  sb.append(lineS(base + "T", sp, tp, w, th, fsT, l, col, gcol));
  sb.append(lineS(base + "L", sp, tp + th, w, rh, fsR, l, col, gcol));
  sb.append(lineS(base + "O", sp, tp + th + rh, w, rh, fsR, l, col, gcol));
  if (rows > 0) sb.append(lineS(base + "A", sp, tp + th + 2 * rh, w, nh, fsN, l, col, gcol));
  if (rows > 1) sb.append(lineS(base + "B", sp, tp + th + 2 * rh + nh, w, nh, fsN, l, col, gcol));''')
rep('''public static String skillsBody(String base, {PKG}.WLayout l, int sc, String[] m, int minFs) {{
  int w = l.bw * sc / 100;
  int sp = 6 * sc / 100; int tp = {SKL_TP} * sc / 100;
  int rh = {SKL_ROW} * sc / 100; int vw = {SKL_VW} * sc / 100;
  int fs = {SKL_FS} * sc / 100; if (fs < minFs) fs = minFs;
  int n = skillRows(m);
  StringBuilder sb = new StringBuilder();
  String col = hexOf(l.col);
  String gcol = glowHex(l) + "(0.45)";
  int iw = w - 2 * sp;
  for (int i = 0; i < n; i++) {{
    int y = tp + i * rh;
    String v = m[3 + 2 * i];
    boolean whole = v == null || v.length() == 0;
    sb.append(lineSrc(base + "N" + i, sp, y, whole ? iw : iw - vw, rh, fs, l, col, gcol, "Start"));
    sb.append(lineSrc(base + "S" + i, sp + iw - vw, y, vw, rh, fs, l, col, gcol, "End"));
  }}
  return sb.toString();
}}""", wid))''', '''public static String skillsBody(String base, {PKG}.WLayout l, int sc, String[] m, int minFs, int w) {{
  int sp = padMl(sc, minFs); int tp = {SKL_TP} * sc / 100;
  int rh = {SKL_ROW} * sc / 100;
  int fs = {SKL_FS} * sc / 100; if (fs < minFs) fs = minFs;
  int n = skillRows(m);
  StringBuilder sb = new StringBuilder();
  String col = hexOf(l.col);
  String gcol = glowHex(l) + "(0.45)";
  for (int i = 0; i < n; i++) {{
    int y = tp + i * rh;
    sb.append(lineS(base + "N" + i, sp, y, w, rh, fs, l, col, gcol));
    sb.append(lineE(base + "S" + i, sp, y, w, rh, fs, l, col, gcol));
  }}
  return sb.toString();
}}""", wid))''')
# Combat colours: out of combat the picked out-of-combat colour, or 0.3.12's grey text + quiet grey glow for Default (byte-identical)
rep('''# 0.3.12 Combat colours: in combat the picked palette colour, or red #ff6b6b for "Default"; out of combat the quiet party grey
# (GREY / GREYG); the stand-in line the widget's own colour. Glow "Same" follows the colour actually drawn.
wid.addMethod(CtNewMethod.make(f"""
public static String combatColor({PKG}.WLayout l, String tone) {{
  if ("g".equals(tone)) return GREY;
  if ("r".equals(tone) && "def".equals(l.col)) return CRED;
  return hexOf(l.col);
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static String combatGlow({PKG}.WLayout l, String tone) {{
  if ("g".equals(tone)) return GREYG;
  return ("def".equals(l.gcol) ? combatColor(l, tone) : hexOf(l.gcol)) + "(0.45)";
}}""", wid))''', '''# 0.3.12 Combat colours: in combat the picked palette colour, or red #ff6b6b for "Default"; the stand-in line the widget's own colour.
# 0.3.13: out of combat the picked OUT-OF-COMBAT colour (WLayout.ocol); for "Default" the quiet party grey text + grey glow exactly as
# 0.3.12 drew it (GREY / GREYG). Glow "Same" follows the colour actually drawn.
wid.addMethod(CtNewMethod.make(f"""
public static String combatColor({PKG}.WLayout l, String tone) {{
  if ("g".equals(tone)) return (l.ocol == null || "def".equals(l.ocol)) ? GREY : hexOf(l.ocol);
  if ("r".equals(tone) && "def".equals(l.col)) return CRED;
  return hexOf(l.col);
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static String combatGlow({PKG}.WLayout l, String tone) {{
  if ("g".equals(tone) && (l.ocol == null || "def".equals(l.ocol))) return GREYG;
  return ("def".equals(l.gcol) ? combatColor(l, tone) : hexOf(l.gcol)) + "(0.45)";
}}""", wid))''')
rep('''# one line at the top (name Start, countdown End - the Skills row look) and in combat the vanilla ProgressBar under it, inset like the
# text (6 px a side at 100%); the bar's Value is inline (first render) and b.set by HudMain.fill on every change
wid.addMethod(CtNewMethod.make(f"""
public static String combatBody(String base, {PKG}.WLayout l, int sc, String[] m, int minFs) {{
  int w = l.bw * sc / 100;
  int sp = 6 * sc / 100; int tp = {CMB_TP} * sc / 100;
  int rh = {CMB_ROW} * sc / 100; int vw = {CMB_VW} * sc / 100;
  int fs = {CMB_FS} * sc / 100; if (fs < minFs) fs = minFs;
  int iw = w - 2 * sp;
  String tone = (m == null || m.length < 6 || m[5] == null) ? "n" : m[5];
  String col = combatColor(l, tone);
  String gcol = combatGlow(l, tone);
  String v = (m == null || m.length < 4) ? null : m[3];
  boolean whole = v == null || v.length() == 0;
  StringBuilder sb = new StringBuilder();
  sb.append(lineSrc(base + "N0", sp, tp, whole ? iw : iw - vw, rh, fs, l, col, gcol, "Start"));
  sb.append(lineSrc(base + "S0", sp + iw - vw, tp, vw, rh, fs, l, col, gcol, "End"));''', '''# one line at the top (name Start, countdown End - the Skills row look) and in combat the vanilla ProgressBar under it, as wide as the
# text (0.3.13: from P to P before the right edge); the bar's Value is inline (first render) and b.set by HudMain.fill on every change
wid.addMethod(CtNewMethod.make(f"""
public static String combatBody(String base, {PKG}.WLayout l, int sc, String[] m, int minFs, int w) {{
  int sp = padMl(sc, minFs); int tp = {CMB_TP} * sc / 100;
  int rh = {CMB_ROW} * sc / 100;
  int fs = {CMB_FS} * sc / 100; if (fs < minFs) fs = minFs;
  int iw = w - 2 * sp; if (iw < 1) iw = 1;
  String tone = (m == null || m.length < 6 || m[5] == null) ? "n" : m[5];
  String col = combatColor(l, tone);
  String gcol = combatGlow(l, tone);
  StringBuilder sb = new StringBuilder();
  sb.append(lineS(base + "N0", sp, tp, w, rh, fs, l, col, gcol));
  sb.append(lineE(base + "S0", sp, tp, w, rh, fs, l, col, gcol));''')
rep('''public static String multiBody(String id, String base, {PKG}.WLayout l, int sc, String[] m, int minFs) {{
  if ("Combat".equals(id)) return combatBody(base, l, sc, m, minFs);
  if ("Skills".equals(id)) return skillsBody(base, l, sc, m, minFs);
  if ("Party".equals(id)) return partyBody(base, l, sc, m, minFs);
  return guildBody(base, l, sc, m, minFs);
}}""", wid))
# the widget Group IS the drawn box: Height = bodyH (rows in use), Background on the Group itself like every one-line widget
wid.addMethod(CtNewMethod.make(f"""
public static String multiWidgetSrc(String id, {PKG}.WLayout l, String[] m) {{
  return "Group #SkyyW" + id + " {{ Anchor: " + anchorSrcH(l, bodyH(id, m, l.scale)) + "; " + (l.bg ? "Background: #0b1524(0.72); " : "") + multiBody(id, "SkyyW" + id, l, l.scale, m, 6) + " }}";
}}""", wid))''', '''public static String multiBody(String id, String base, {PKG}.WLayout l, int sc, String[] m, int minFs, int w) {{
  if ("Combat".equals(id)) return combatBody(base, l, sc, m, minFs, w);
  if ("Skills".equals(id)) return skillsBody(base, l, sc, m, minFs, w);
  if ("Party".equals(id)) return partyBody(base, l, sc, m, minFs, w);
  return guildBody(base, l, sc, m, minFs, w);
}}""", wid))
# the widget Group IS the drawn box: Height = bodyH (rows in use), Width = w (0.3.13: multiW, the widest line + 2P), Background on the
# Group itself like every one-line widget
wid.addMethod(CtNewMethod.make(f"""
public static String multiWidgetSrcW(String id, {PKG}.WLayout l, String[] m, int w) {{
  return "Group #SkyyW" + id + " {{ Anchor: " + anchorSrcWH(l, w, bodyH(id, m, l.scale)) + "; " + (l.bg ? "Background: #0b1524(0.72); " : "") + multiBody(id, "SkyyW" + id, l, l.scale, m, 6, w) + " }}";
}}""", wid))''')
rep('''wid.addMethod(CtNewMethod.make(f"""
public static String widgetSrc(String id, {PKG}.WLayout l) {{
  int fs = 12 * l.scale / 100; if (fs < 6) fs = 6;
  int w = l.bw * l.scale / 100; int h = l.bh * l.scale / 100;
  return "Group #SkyyW" + id + " {{ Anchor: " + anchorSrc(l) + "; " + (l.bg ? "Background: #0b1524(0.72); " : "") + textSrc("SkyyW" + id, w, h, fs, l) + " }}";
}}""", wid))''', '''# 0.3.13: a one-line widget at the box width w (lineW of the text it is built with; the text stays centred, P from each side)
wid.addMethod(CtNewMethod.make(f"""
public static String widgetSrcW(String id, {PKG}.WLayout l, int w) {{
  int fs = 12 * l.scale / 100; if (fs < 6) fs = 6;
  int h = l.bh * l.scale / 100;
  return "Group #SkyyW" + id + " {{ Anchor: " + anchorSrcWH(l, w, h) + "; " + (l.bg ? "Background: #0b1524(0.72); " : "") + textSrc("SkyyW" + id, w, h, fs, l) + " }}";
}}""", wid))''')

# ---------------- Widgets: screen maths with the width passed in (the H forms keep the maximum box: clamps, snaps, arrows) ----------
rep('''wid.addMethod(CtNewMethod.make(f"""
public static int[] screenPosH({PKG}.WLayout l, int h) {{
  int w = l.bw * l.scale / 100;
  String a = l.anchor; int x; int y;''', '''wid.addMethod(CtNewMethod.make(f"""
public static int[] screenPosWH({PKG}.WLayout l, int w, int h) {{
  String a = l.anchor; int x; int y;''')
rep('''  return new int[] {{ x, y }};
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static int[] screenPos({PKG}.WLayout l) {{''', '''  return new int[] {{ x, y }};
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static int[] screenPosH({PKG}.WLayout l, int h) {{
  return screenPosWH(l, l.bw * l.scale / 100, h);
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static int[] screenPos({PKG}.WLayout l) {{''')
rep('''public static void setTopLeftH({PKG}.WLayout l, int x, int y, int h) {{
  int w = l.bw * l.scale / 100;
  if (x > 1920 - w) x = 1920 - w;''', '''public static void setTopLeftWH({PKG}.WLayout l, int x, int y, int w, int h) {{
  if (x > 1920 - w) x = 1920 - w;''')
rep('''  else l.dy = y - (540 - h / 2);
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static void clampToScreen({PKG}.WLayout l) {{''', '''  else l.dy = y - (540 - h / 2);
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static void setTopLeftH({PKG}.WLayout l, int x, int y, int h) {{
  setTopLeftWH(l, x, y, l.bw * l.scale / 100, h);
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static void clampToScreen({PKG}.WLayout l) {{''')
rep('''public static void cornerAtH({PKG}.WLayout l, int x, int y, int h) {{
  int w = l.bw * l.scale / 100;
  if (x > 1920 - w) x = 1920 - w;
  if (x < 0) x = 0;
  if (y > 1080 - h) y = 1080 - h;
  if (y < 0) y = 0;
  boolean left = x + w / 2 < 960; boolean top = y + h / 2 < 540;
  l.anchor = top ? (left ? "tl" : "tr") : (left ? "bl" : "br");
  setTopLeftH(l, x, y, h);
}}""", wid))''', '''public static void cornerAtWH({PKG}.WLayout l, int x, int y, int w, int h) {{
  if (x > 1920 - w) x = 1920 - w;
  if (x < 0) x = 0;
  if (y > 1080 - h) y = 1080 - h;
  if (y < 0) y = 0;
  boolean left = x + w / 2 < 960; boolean top = y + h / 2 < 540;
  l.anchor = top ? (left ? "tl" : "tr") : (left ? "bl" : "br");
  setTopLeftWH(l, x, y, w, h);
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static void cornerAtH({PKG}.WLayout l, int x, int y, int h) {{
  cornerAtWH(l, x, y, l.bw * l.scale / 100, h);
}}""", wid))''')
rep('''public static int cellOfH({PKG}.WLayout l, int h) {{
  int[] p = screenPosH(l, h);
  int cx = p[0] + (l.bw * l.scale / 100) / 2; int cy = p[1] + h / 2;''', '''public static int cellOfWH({PKG}.WLayout l, int w, int h) {{
  int[] p = screenPosWH(l, w, h);
  int cx = p[0] + w / 2; int cy = p[1] + h / 2;''')
rep('''  return row * 32 + col;
}}""", wid))
''', '''  return row * 32 + col;
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static int cellOfH({PKG}.WLayout l, int h) {{
  return cellOfWH(l, l.bw * l.scale / 100, h);
}}""", wid))
''')
rep('''public static void moveByCellsH({PKG}.WLayout l, int from, int to, int h) {{
  int[] p = screenPosH(l, h);
  int mx = (to % 32 - from % 32) * 60; int my = (to / 32 - from / 32) * 60;
  cornerAtH(l, p[0] + mx, p[1] + my, h);
}}""", wid))''', '''public static void moveByCellsWH({PKG}.WLayout l, int from, int to, int w, int h) {{
  int[] p = screenPosWH(l, w, h);
  int mx = (to % 32 - from % 32) * 60; int my = (to / 32 - from / 32) * 60;
  cornerAtWH(l, p[0] + mx, p[1] + my, w, h);
}}""", wid))
wid.addMethod(CtNewMethod.make(f"""
public static void moveByCellsH({PKG}.WLayout l, int from, int to, int h) {{
  moveByCellsWH(l, from, to, l.bw * l.scale / 100, h);
}}""", wid))''')
rep('''public static int viewH(String id, {PKG}.WLayout l, {PR} pr) {{
  if (!multi(id)) return hMax(l);
  return bodyH(id, viewModel(id, pr, l), l.scale);
}}""", wid))''', '''public static int viewH(String id, {PKG}.WLayout l, {PR} pr) {{
  if (!multi(id)) return hMax(l);
  return bodyH(id, viewModel(id, pr, l), l.scale);
}}""", wid))
# 0.3.13: the drawn width the editor lays a widget out with (the text / lines it shows now)
wid.addMethod(CtNewMethod.make(f"""
public static int viewW(String id, {PKG}.WLayout l, {PR} pr, long joinMs) {{
  if (multi(id)) return multiW(id, l, viewModel(id, pr, l), l.scale, 6);
  String t = null;
  try {{ t = text(id, pr, joinMs); }} catch (Throwable x) {{ t = null; }}
  if (t == null) t = label(id);
  return lineW(l, t, l.scale, 6);
}}""", wid))''')

# ---------------- HudMain: the built widths + the grow-now / shrink-after-15-s re-send ----------------
rep('''hudc.addField(CtField.make("public long confirmAt;", hudc))
''', '''hudc.addField(CtField.make("public long confirmAt;", hudc))
# 0.3.13: id -> the one-line text build() measured (its first fill sets exactly that), id -> Integer box width build() sent,
# id -> Long time the text first fitted a narrower box (cleared when it fits the built box again or needs more)
hudc.addField(CtField.make("public final java.util.concurrent.ConcurrentHashMap texts = new java.util.concurrent.ConcurrentHashMap();", hudc))
hudc.addField(CtField.make("public final java.util.concurrent.ConcurrentHashMap wb = new java.util.concurrent.ConcurrentHashMap();", hudc))
hudc.addField(CtField.make("public final java.util.concurrent.ConcurrentHashMap narrow = new java.util.concurrent.ConcurrentHashMap();", hudc))
''')
rep('''  this.joinMs = System.currentTimeMillis();
}}""", hudc))
hudc.addMethod(CtNewMethod.make(f"""
public boolean fill({UCB} b, boolean full) {{
  {PR} pr = getPlayerRef();
  String[] ids = {PKG}.Widgets.IDS;
  boolean re = false;''', '''  this.joinMs = System.currentTimeMillis();
}}""", hudc))
# 0.3.13: true = re-send the HUD for widget id: its text needs a wider box than the one sent (at once), or has fitted a narrower one for
# Widgets.SHRINK ms; called by fill on the 1 s tick only (never on a full build)
hudc.addMethod(CtNewMethod.make(f"""
public boolean widthMoved(String id, int need, long now) {{
  Object o = this.wb.get(id);
  if (o == null) return false;
  int have = ((Integer) o).intValue();
  if (need >= have) {{ this.narrow.remove(id); return need > have; }}
  Object t = this.narrow.get(id);
  if (t == null) {{ this.narrow.put(id, Long.valueOf(now)); return false; }}
  return now - ((Long) t).longValue() >= {PKG}.Widgets.SHRINK;
}}""", hudc))
hudc.addMethod(CtNewMethod.make(f"""
public boolean fill({UCB} b, boolean full) {{
  {PR} pr = getPlayerRef();
  String[] ids = {PKG}.Widgets.IDS;
  boolean re = false;
  long now = System.currentTimeMillis();''')
rep('''      if (!sh.equals(mm[0])) {{ re = true; continue; }}
      Object mg = this.built.get(ids[i]);
      if (mg == null) continue;
      int gn = ((Integer) mg).intValue();''', '''      if (!sh.equals(mm[0])) {{ re = true; continue; }}
      Object mg = this.built.get(ids[i]);
      if (mg == null) continue;
      if (!full && ml != null && widthMoved(ids[i], {PKG}.Widgets.multiW(ids[i], ml, mm, ml.scale, 6), now)) re = true;
      int gn = ((Integer) mg).intValue();''')
rep('''    Object g = this.built.get(ids[i]);
    if (g == null) continue;
    String t = {PKG}.Widgets.text(ids[i], pr, this.joinMs);
    String prev = (String) this.last.get(ids[i]);''', '''    Object g = this.built.get(ids[i]);
    if (g == null) continue;
    String t = null;
    if (full) t = (String) this.texts.get(ids[i]);
    if (t == null) t = {PKG}.Widgets.text(ids[i], pr, this.joinMs);
    if (t == null) t = "";
    if (!full) {{
      {PKG}.WLayout ol = ({PKG}.WLayout) {PKG}.LayoutStore.get(this.uuid).get(ids[i]);
      if (ol != null && widthMoved(ids[i], {PKG}.Widgets.lineW(ol, t, ol.scale, 6), now)) re = true;
    }}
    String prev = (String) this.last.get(ids[i]);''')
rep('''  this.built.clear();
  this.shape.clear();
  this.models.clear();
  {PR} pr = getPlayerRef();''', '''  this.built.clear();
  this.shape.clear();
  this.models.clear();
  this.texts.clear();
  this.wb.clear();
  this.narrow.clear();
  {PR} pr = getPlayerRef();''')
rep('''      b.appendInline("#SkyyHudRoot", {PKG}.Widgets.multiWidgetSrc(ids[i], l, mm));
      this.built.put(ids[i], Integer.valueOf({PKG}.Widgets.glowCount(l)));
      continue;
    }}
    b.appendInline("#SkyyHudRoot", {PKG}.Widgets.widgetSrc(ids[i], l));
    this.built.put(ids[i], Integer.valueOf({PKG}.Widgets.glowCount(l)));''', '''      int mw = {PKG}.Widgets.multiW(ids[i], l, mm, l.scale, 6);
      this.wb.put(ids[i], Integer.valueOf(mw));
      b.appendInline("#SkyyHudRoot", {PKG}.Widgets.multiWidgetSrcW(ids[i], l, mm, mw));
      this.built.put(ids[i], Integer.valueOf({PKG}.Widgets.glowCount(l)));
      continue;
    }}
    // 0.3.13: measure the text first - the box is as wide as it (+ P a side); the first fill sets exactly this text
    String t = {PKG}.Widgets.text(ids[i], pr, this.joinMs);
    if (t == null) t = "";
    int ow = {PKG}.Widgets.lineW(l, t, l.scale, 6);
    this.texts.put(ids[i], t);
    this.wb.put(ids[i], Integer.valueOf(ow));
    b.appendInline("#SkyyHudRoot", {PKG}.Widgets.widgetSrcW(ids[i], l, ow));
    this.built.put(ids[i], Integer.valueOf({PKG}.Widgets.glowCount(l)));''')

# ---------------- EditorPage: the drawn widths ----------------
rep('''page.addField(CtField.make("public java.util.HashMap pm;", page))
''', '''page.addField(CtField.make("public java.util.HashMap pm;", page))
# 0.3.13: id -> Integer drawn width (the box the HUD shows now, at HUD size), id -> String the one-line text it was measured with
page.addField(CtField.make("public java.util.HashMap ww;", page))
page.addField(CtField.make("public java.util.HashMap pt;", page))
''')
rep('''public void prepView(java.util.Map m, String[] ids) {{
  this.hh = new java.util.HashMap();
  this.pm = new java.util.HashMap();
  for (int i = 0; i < ids.length; i++) {{
    {PKG}.WLayout l = ({PKG}.WLayout) m.get(ids[i]);
    if (l == null) continue;
    if ({PKG}.Widgets.multi(ids[i])) {{
      String[] mm = {PKG}.Widgets.viewModel(ids[i], this.playerRef, l);
      this.pm.put(ids[i], mm);
      this.hh.put(ids[i], Integer.valueOf({PKG}.Widgets.bodyH(ids[i], mm, l.scale)));
    }} else this.hh.put(ids[i], Integer.valueOf({PKG}.Widgets.hMax(l)));
  }}
}}""", page))''', '''public void prepView(java.util.Map m, String[] ids) {{
  this.hh = new java.util.HashMap();
  this.pm = new java.util.HashMap();
  this.ww = new java.util.HashMap();
  this.pt = new java.util.HashMap();
  long join = System.currentTimeMillis();
  try {{ {PKG}.HudMain hm = ({PKG}.HudMain) this.plugin.huds.get(this.playerRef.getUuid()); if (hm != null) join = hm.joinMs; }} catch (Throwable t) {{ }}
  for (int i = 0; i < ids.length; i++) {{
    {PKG}.WLayout l = ({PKG}.WLayout) m.get(ids[i]);
    if (l == null) continue;
    if ({PKG}.Widgets.multi(ids[i])) {{
      String[] mm = {PKG}.Widgets.viewModel(ids[i], this.playerRef, l);
      this.pm.put(ids[i], mm);
      this.hh.put(ids[i], Integer.valueOf({PKG}.Widgets.bodyH(ids[i], mm, l.scale)));
      this.ww.put(ids[i], Integer.valueOf({PKG}.Widgets.multiW(ids[i], l, mm, l.scale, 6)));
    }} else {{
      String text;
      try {{ text = {PKG}.Widgets.text(ids[i], this.playerRef, join); }} catch (Throwable t) {{ text = {PKG}.Widgets.label(ids[i]); }}
      if (text == null) text = "";
      this.pt.put(ids[i], text);
      this.hh.put(ids[i], Integer.valueOf({PKG}.Widgets.hMax(l)));
      this.ww.put(ids[i], Integer.valueOf({PKG}.Widgets.lineW(l, text, l.scale, 6)));
    }}
  }}
}}""", page))''')
rep('''  return {PKG}.Widgets.viewH(id, l, this.playerRef);
}}""", page))''', '''  return {PKG}.Widgets.viewH(id, l, this.playerRef);
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public int widthOf(String id, {PKG}.WLayout l) {{
  Object o = this.ww == null ? null : this.ww.get(id);
  if (o != null) return ((Integer) o).intValue();
  return {PKG}.Widgets.viewW(id, l, this.playerRef, System.currentTimeMillis());
}}""", page))''')
rep('''    int h = heightOf(ids[i], l);
    int[] p = {PKG}.Widgets.screenPosH(l, h);
    int w = l.bw * l.scale / 100;''', '''    int h = heightOf(ids[i], l);
    int w = widthOf(ids[i], l);
    int[] p = {PKG}.Widgets.screenPosWH(l, w, h);''')
rep('''    boolean displaced = c != {PKG}.Widgets.cellOfH(hl, heightOf(hid, hl));''',
    '''    boolean displaced = c != {PKG}.Widgets.cellOfWH(hl, widthOf(hid, hl), heightOf(hid, hl));''')
rep('''    int hs = heightOf(ids[i], l);
    int[] p = {PKG}.Widgets.screenPosH(l, hs);
    int cw = (l.bw * l.scale / 100) * 2 / 3; int ch = mw ? {PKG}.Widgets.bodyH(ids[i], mm, l.scale * 2 / 3) : (l.bh * l.scale / 100) * 2 / 3;
    int left = p[0] * 2 / 3; int top = p[1] * 2 / 3;
''', '''    int hs = heightOf(ids[i], l);
    int ws = widthOf(ids[i], l);
    int[] p = {PKG}.Widgets.screenPosWH(l, ws, hs);
    int cw = mw ? {PKG}.Widgets.multiW(ids[i], l, mm, l.scale * 2 / 3, 5) : ws * 2 / 3; int ch = mw ? {PKG}.Widgets.bodyH(ids[i], mm, l.scale * 2 / 3) : (l.bh * l.scale / 100) * 2 / 3;
    int left = p[0] * 2 / 3; int top = p[1] * 2 / 3;
    // 0.3.13: a multi-line preview laid out at 2/3 size sits on its anchored edge (right) or centre, like its height (0.3.9)
    if (mw && (l.anchor.equals("tr") || l.anchor.equals("r") || l.anchor.equals("br"))) left = (p[0] + ws) * 2 / 3 - cw;
    else if (mw && (l.anchor.equals("t") || l.anchor.equals("c") || l.anchor.equals("b"))) left = (2 * p[0] + ws) / 3 - cw / 2;
''')
rep('''{PKG}.Widgets.multiBody(ids[i], "SkyyEPv" + ids[i], l, l.scale * 2 / 3, mm, 5) + " }}");''',
    '''{PKG}.Widgets.multiBody(ids[i], "SkyyEPv" + ids[i], l, l.scale * 2 / 3, mm, 5, cw) + " }}");''')
rep('''    String text;
    try {{ text = {PKG}.Widgets.text(ids[i], this.playerRef, join); }} catch (Throwable t) {{ text = {PKG}.Widgets.label(ids[i]); }}
    if (text == null) text = "";
    b.appendInline("#SkyyEPrev", "Group #SkyyEPv" + ids[i]''', '''    String text = this.pt == null ? null : (String) this.pt.get(ids[i]);
    if (text == null) {{ try {{ text = {PKG}.Widgets.text(ids[i], this.playerRef, join); }} catch (Throwable t) {{ text = {PKG}.Widgets.label(ids[i]); }} }}
    if (text == null) text = "";
    b.appendInline("#SkyyEPrev", "Group #SkyyEPv" + ids[i]''')
rep('''    int cell = freeCellNear({PKG}.Widgets.cellOfH(l, heightOf(id, l)));''',
    '''    int cell = freeCellNear({PKG}.Widgets.cellOfWH(l, widthOf(id, l), heightOf(id, l)));''')
rep('''      {PKG}.Widgets.moveByCellsH(l, from, to, heightOf(wid, l));''',
    '''      {PKG}.Widgets.moveByCellsWH(l, from, to, widthOf(wid, l), heightOf(wid, l));''')


# ---------------- SettingsPage: swatches with given colours, the Combat colour rows, content-sized previews ----------------
# the two Combat Default swatches use the build's own palette maths (_mix / _fg, as PAL_HOV / PAL_PRS / PAL_FG)
rep('''# one palette swatch: 84 x 44 cell; the button shows the colour itself (name in a readable dark/light text); the selected one gets
# a white + black ring (visible on every swatch, white and black included)
sett.addMethod(CtNewMethod.make(f"""
public String swatch(String bid, int pi, boolean selected, String label) {{
  String bg = {PKG}.WLayout.PAL_HEX[pi]; String hv = {PKG}.WLayout.PAL_HOV[pi]; String ps = {PKG}.WLayout.PAL_PRS[pi]; String fg = {PKG}.WLayout.PAL_FG[pi];
  String ls''', '''# 0.3.13: the Combat widget's two Default swatches show the colour Default means there: red in combat, grey out of combat (the
# palette's hover / pressed / text maths, as PAL_HOV / PAL_PRS / PAL_FG)
sett.addField(CtField.make("public static final String[] CSW = %s;" % jarr([CMB_RED, _mix(CMB_RED, "#ffffff", 0.3), _mix(CMB_RED, "#000000", 0.25), _fg(CMB_RED)]), sett))
sett.addField(CtField.make("public static final String[] OSW = %s;" % jarr(["#8b949e", _mix("#8b949e", "#ffffff", 0.3), _mix("#8b949e", "#000000", 0.25), _fg("#8b949e")]), sett))
# one palette swatch: 84 x 44 cell; the button shows the colour itself (name in a readable dark/light text); the selected one gets
# a white + black ring (visible on every swatch, white and black included). 0.3.13: swatchHex takes the four colours (swatch = a
# palette entry, byte-identical markup)
sett.addMethod(CtNewMethod.make(f"""
public String swatchHex(String bid, String bg, String hv, String ps, String fg, boolean selected, String label) {{
  String ls''')
rep('''  return "Group {{ Anchor: (Width: 84, Height: 44); " + (selected ? "Background: #ffffff; " : "") + "Group {{ Anchor: (Left: 2, Right: 2, Top: 2, Bottom: 2); " + (selected ? "Background: #000000; " : "") + "TextButton #" + bid + " {{ Anchor: (Left: 2, Right: 2, Top: 2, Bottom: 2); Text: \\\\"" + label + "\\\\"; " + st + " }} }} }}";
}}""", sett))''', '''  return "Group {{ Anchor: (Width: 84, Height: 44); " + (selected ? "Background: #ffffff; " : "") + "Group {{ Anchor: (Left: 2, Right: 2, Top: 2, Bottom: 2); " + (selected ? "Background: #000000; " : "") + "TextButton #" + bid + " {{ Anchor: (Left: 2, Right: 2, Top: 2, Bottom: 2); Text: \\\\"" + label + "\\\\"; " + st + " }} }} }}";
}}""", sett))
sett.addMethod(CtNewMethod.make(f"""
public String swatch(String bid, int pi, boolean selected, String label) {{
  return swatchHex(bid, {PKG}.WLayout.PAL_HEX[pi], {PKG}.WLayout.PAL_HOV[pi], {PKG}.WLayout.PAL_PRS[pi], {PKG}.WLayout.PAL_FG[pi], selected, label);
}}""", sett))''')
rep('''  boolean skl = "Skills".equals(this.wid);
  b.appendInline((String) null, "Group #SkyySet {{ Anchor: (Width: 1500, Height: " + (skl ? 940 : 790) + "); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }}");''',
    '''  boolean skl = "Skills".equals(this.wid);
  // 0.3.13 Combat: + the Out of combat colour row (58) + a second preview row (76): 882 px of rows + 20 padding -> 924 (others 790 / 940)
  boolean cmb = "Combat".equals(this.wid);
  b.appendInline((String) null, "Group #SkyySet {{ Anchor: (Width: 1500, Height: " + (skl ? 940 : (cmb ? 924 : 790)) + "); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }}");''')
rep('''  b.appendInline("#SkyySetRowCol", "Label {{ Anchor: (Width: 200, Height: 44); Text: \\\\"Color\\\\"; " + rl + " }}");
  for (int i = 0; i < {PKG}.WLayout.TEXT_N; i++) {{
    String k = {PKG}.WLayout.PAL_KEYS[i];
    b.appendInline("#SkyySetRowCol", swatch("SkyySetTc" + cap(k), i, i == ci, {PKG}.WLayout.PAL_NAMES[i]));
    b.appendInline("#SkyySetRowCol", "Label {{ Anchor: (Width: 6, Height: 44); Text: \\\\"\\\\"; }}");
    ev.addEventBinding({BT}.Activating, "#SkyySetTc" + cap(k), {EVD}.of("a", "col:" + k));
  }}''', '''  b.appendInline("#SkyySetRowCol", "Label {{ Anchor: (Width: 200, Height: 44); Text: \\\\"" + (cmb ? "In combat" : "Color") + "\\\\"; " + rl + " }}");
  for (int i = 0; i < {PKG}.WLayout.TEXT_N; i++) {{
    String k = {PKG}.WLayout.PAL_KEYS[i];
    b.appendInline("#SkyySetRowCol", (cmb && i == 0) ? swatchHex("SkyySetTc" + cap(k), CSW[0], CSW[1], CSW[2], CSW[3], i == ci, {PKG}.WLayout.PAL_NAMES[i]) : swatch("SkyySetTc" + cap(k), i, i == ci, {PKG}.WLayout.PAL_NAMES[i]));
    b.appendInline("#SkyySetRowCol", "Label {{ Anchor: (Width: 6, Height: 44); Text: \\\\"\\\\"; }}");
    ev.addEventBinding({BT}.Activating, "#SkyySetTc" + cap(k), {EVD}.of("a", "col:" + k));
  }}
  // 0.3.13 Combat: the OUT OF COMBAT colour (WLayout.ocol; Default = the 0.3.12 grey), the same 13 choices, payload ocol:<key>
  if (cmb) {{
    int oi = {PKG}.WLayout.palIdx(l.ocol);
    if (oi < 0 || oi >= {PKG}.WLayout.TEXT_N) oi = 0;
    b.appendInline("#SkyySet", "Group #SkyySetRowOc {{ Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 12); }}");
    b.appendInline("#SkyySetRowOc", "Label {{ Anchor: (Width: 200, Height: 44); Text: \\\\"Out of combat\\\\"; " + rl + " }}");
    for (int i = 0; i < {PKG}.WLayout.TEXT_N; i++) {{
      String k = {PKG}.WLayout.PAL_KEYS[i];
      b.appendInline("#SkyySetRowOc", i == 0 ? swatchHex("SkyySetOc" + cap(k), OSW[0], OSW[1], OSW[2], OSW[3], i == oi, {PKG}.WLayout.PAL_NAMES[i]) : swatch("SkyySetOc" + cap(k), i, i == oi, {PKG}.WLayout.PAL_NAMES[i]));
      b.appendInline("#SkyySetRowOc", "Label {{ Anchor: (Width: 6, Height: 44); Text: \\\\"\\\\"; }}");
      ev.addEventBinding({BT}.Activating, "#SkyySetOc" + cap(k), {EVD}.of("a", "ocol:" + k));
    }}
  }}''')
rep('''    b.appendInline("#SkyySetRowGc", swatch("SkyySetGc" + cap(k), i == 0 ? ci : i, i == gi, i == 0 ? "Same" : {PKG}.WLayout.PAL_NAMES[i]));''',
    '''    b.appendInline("#SkyySetRowGc", (cmb && i == 0 && ci == 0) ? swatchHex("SkyySetGc" + cap(k), CSW[0], CSW[1], CSW[2], CSW[3], i == gi, "Same") : swatch("SkyySetGc" + cap(k), i == 0 ? ci : i, i == gi, i == 0 ? "Same" : {PKG}.WLayout.PAL_NAMES[i]));''')
rep('''  int pw = 180 * l.scale / 100; int ph = 26 * l.scale / 100;
  int fs = 12 * l.scale / 100; if (fs < 6) fs = 6;
  String text = previewText();
  int gn = {PKG}.Widgets.glowCount(l);
  // 0.3.12 Combat: the preview in the colour the HUD draws (red in combat / the picked colour, grey out of combat)
  boolean cmb = "Combat".equals(this.wid);
  String ccol = null; String cglo = null;
  if (cmb) {{
    String tone = "r";
    try {{ String[] cv = {PKG}.Widgets.viewModel(this.wid, this.playerRef, l); if (cv != null && cv.length > 5 && cv[5] != null) tone = cv[5]; }} catch (Throwable x) {{ tone = "r"; }}
    ccol = {PKG}.Widgets.combatColor(l, tone);
    cglo = {PKG}.Widgets.combatGlow(l, tone);
  }}
  b.appendInline("#SkyySet", "Group #SkyySetRowPv {{ Anchor: (Height: 76); LayoutMode: Left; Padding: (Top: 8); }}");
  b.appendInline("#SkyySetRowPv", "Label {{ Anchor: (Width: 200, Height: 60); Text: \\\\"Preview\\\\"; " + rl + " }}");
  String[] pv = new String[] {{ "SkyySetPvA", "SkyySetPvB" }};
  String[] bd = new String[] {{ "#141a22", "#8fb3cf" }};
  for (int j = 0; j < pv.length; j++) {{
    b.appendInline("#SkyySetRowPv", "Group #" + pv[j] + "Wrap {{ Anchor: (Width: 400, Height: 60); Background: " + bd[j] + "; }}");
    b.appendInline("#" + pv[j] + "Wrap", "Group #" + pv[j] + " {{ Anchor: (Left: " + ((400 - pw) / 2) + ", Top: " + ((60 - ph) / 2) + ", Width: " + pw + ", Height: " + ph + "); " + (l.bg ? "Background: #0b1524(0.72); " : "") + (cmb ? {PKG}.Widgets.textSrcC(pv[j], pw, ph, fs, l, ccol, cglo) : {PKG}.Widgets.textSrc(pv[j], pw, ph, fs, l)) + " }}");
    b.appendInline("#SkyySetRowPv", "Label {{ Anchor: (Width: 12, Height: 60); Text: \\\\"\\\\"; }}");
    {PKG}.Widgets.setText(b, "#" + pv[j], gn, text);
  }}
  b.appendInline("#SkyySetRowPv", "Label {{ Anchor: (Width: 360, Height: 60); Text: \\\\"on dark and on bright scenery\\\\"; Style: (FontSize: 15, TextColor: #9fb8d0, VerticalAlignment: Center); }}");''',
    '''  int ph = 26 * l.scale / 100;
  int fs = 12 * l.scale / 100; if (fs < 6) fs = 6;
  int gn = {PKG}.Widgets.glowCount(l);
  String[] bd = new String[] {{ "#141a22", "#8fb3cf" }};
  // 0.3.13: the preview box is as wide as its text (Widgets.lineW, like the HUD). Combat shows TWO rows: "In combat 4s" in the in-combat
  // colour and "Out of combat" in the out-of-combat colour (each on the dark and the bright backdrop; the samples, so they never
  // need a page update); the hints are b.set (they may carry a version number)
  int nrow = cmb ? 2 : 1;
  for (int r = 0; r < nrow; r++) {{
    String row = r == 0 ? "SkyySetRowPv" : "SkyySetRowPvO";
    String text = cmb ? (r == 0 ? "In combat 4s" : "Out of combat") : previewText();
    String tone = r == 0 ? "r" : "g";
    String ccol = cmb ? {PKG}.Widgets.combatColor(l, tone) : null;
    String cglo = cmb ? {PKG}.Widgets.combatGlow(l, tone) : null;
    int pw = {PKG}.Widgets.lineW(l, text, l.scale, 6);
    b.appendInline("#SkyySet", "Group #" + row + " {{ Anchor: (Height: 76); LayoutMode: Left; Padding: (Top: 8); }}");
    b.appendInline("#" + row, "Label {{ Anchor: (Width: 200, Height: 60); Text: \\\\"" + (r == 0 ? "Preview" : "") + "\\\\"; " + rl + " }}");
    String[] pv = r == 0 ? new String[] {{ "SkyySetPvA", "SkyySetPvB" }} : new String[] {{ "SkyySetPvC", "SkyySetPvD" }};
    for (int j = 0; j < pv.length; j++) {{
      b.appendInline("#" + row, "Group #" + pv[j] + "Wrap {{ Anchor: (Width: 400, Height: 60); Background: " + bd[j] + "; }}");
      b.appendInline("#" + pv[j] + "Wrap", "Group #" + pv[j] + " {{ Anchor: (Left: " + ((400 - pw) / 2) + ", Top: " + ((60 - ph) / 2) + ", Width: " + pw + ", Height: " + ph + "); " + (l.bg ? "Background: #0b1524(0.72); " : "") + (cmb ? {PKG}.Widgets.textSrcC(pv[j], pw, ph, fs, l, ccol, cglo) : {PKG}.Widgets.textSrc(pv[j], pw, ph, fs, l)) + " }}");
      b.appendInline("#" + row, "Label {{ Anchor: (Width: 12, Height: 60); Text: \\\\"\\\\"; }}");
      {PKG}.Widgets.setText(b, "#" + pv[j], gn, text);
    }}
    if (!cmb) b.appendInline("#SkyySetRowPv", "Label {{ Anchor: (Width: 360, Height: 60); Text: \\\\"on dark and on bright scenery\\\\"; Style: (FontSize: 15, TextColor: #9fb8d0, VerticalAlignment: Center); }}");
    else {{
      String hid = r == 0 ? "SkyySetPvHintA" : "SkyySetPvHintB";
      b.appendInline("#" + row, "Label #" + hid + " {{ Anchor: (Width: 360, Height: 60); Text: \\\\"\\\\"; Style: (FontSize: 15, TextColor: #9fb8d0, VerticalAlignment: Center); }}");
      b.set("#" + hid + ".Text", r == 1 ? "out of combat - shown when Out of combat is Show" : ({PKG}.Widgets.combatHave({PKG}.Widgets.bridge()) ? "in combat - on dark and on bright scenery" : "in combat - needs SkyySkills 0.4.13"));
    }}
  }}''')
rep('''    else if (data.indexOf("\\\\"rstyle\\\\"") >= 0) {{ l.col = "def"; l.bold = true; l.ital = false; l.glow = false; l.gcol = "def"; }}''',
    '''    else if (data.indexOf("\\\\"rstyle\\\\"") >= 0) {{ l.col = "def"; l.bold = true; l.ital = false; l.glow = false; l.gcol = "def"; l.ocol = "def"; }}
    else if (data.indexOf("\\\\"ocol:") >= 0) {{ if (!"Combat".equals(this.wid)) return; String c = strAfter(data, "\\\\"ocol:"); int ci = {PKG}.WLayout.palIdx(c); if (ci >= 0 && ci < {PKG}.WLayout.TEXT_N) l.ocol = c; else return; }}''')

# ---------------- manifest description ----------------
rep('''"SkyyHud: customizable server-side HUD. 12 widgets incl. Party, Guild, Skills (Overall Level + the skill levels you pick) and a Combat Indicator (red in combat with a countdown and a shrinking bar), per-player layouts''',
    '''"SkyyHud: customizable server-side HUD. 12 widgets incl. Party, Guild, Skills (Overall Level + the skill levels you pick) and a Combat Indicator (a countdown and a shrinking bar, in and out of combat colours), boxes as small as their text, per-player layouts''')

# ---------------- self-checks ----------------
assert 'VERSION = "0.3.13"' in s and "0.3.13 (generated by tools/hud_0_3_13_patch.py from 0.3.12)" in s
assert "multiWidgetSrc(" not in s and "widgetSrc(" not in s.replace("widgetSrcW(", "").replace("WidgetSrcW(", ""), "no caller of the old full-width markup"
assert s.count("anchorSrcWH(") == 4, "anchorSrcWH: defined, the anchorSrcH delegate, the one-line and the multi-line markup"
assert "{CMB_VW}" not in s and "{SKL_VW}" not in s and "128 * sc / 100" not in s, "no fixed value / name columns left"
assert "int w = l.bw * sc / 100;" not in s, "no body takes the maximum box as its width any more"
assert s.count("l.bw * l.scale / 100") == 6, "the maximum box only in the H delegates: anchorSrcH, screenPosH, setTopLeftH, cornerAtH, cellOfH, moveByCellsH"
assert "8 * sc / 100; }" in s and "5 * sc / 100; }" not in s, "the Combat pad under the bar is 8 at 100%"
assert 'SIZES["Combat"] == (180, 37)' in s
assert "if (p.length > 13) {{ String o = p[13].trim();" in s and 'this.ocol = "def";' in s
assert '"\\\\"ocol:"' in s and s.count('"ocol:" + k') == 1 and "SkyySetOc" in s, "the out-of-combat colour row and its payload"
assert 'l.gcol = "def"; l.ocol = "def"; }}' in s, "Reset style resets the out-of-combat colour too"
assert s.count("widthMoved(ids[i]") == 2 and "{PKG}.Widgets.SHRINK" in s, "the tick's width check: multi-line + one-line"
assert "this.wb.put(ids[i], Integer.valueOf(mw));" in s and "this.wb.put(ids[i], Integer.valueOf(ow));" in s
assert "moveByCellsWH(l, from, to, widthOf(wid, l), heightOf(wid, l))" in s and "cellOfWH(l, widthOf(id, l), heightOf(id, l))" in s
assert s.count("textSrcC(") == 2, "textSrcC: defined + the Combat preview rows"
assert "ADV_B = [" in s and "ADV_M = [" in s and "public static final int[] ADVB = new int[]" in s
# javassist order: helpers before their callers
order = ["public static int advOf(", "public static int advMilli(", "public static int pxOf(", "public static int textW(",
         "public static int textWn(", "public static int fsOf(", "public static int padOf(", "public static int padSc(",
         "public static int padMl(", "public static int capW(", "public static int lineW(", "public static int innerW(", "public static int multiW(",
         "public static String anchorSrcWH(", "public static String anchorSrcH(", "public static String lineSrc(",
         "public static String lineS(", "public static String lineE(", "public static int bodyH(", "public static String partyBody(", "public static String guildBody(",
         "public static String skillsBody(", "public static String combatColor(", "public static String combatGlow(",
         "public static String combatBody(", "public static String multiBody(", "public static String multiWidgetSrcW(",
         "public static String widgetSrcW(", "public static int[] screenPosWH(", "public static int[] screenPosH(",
         "public static void setTopLeftWH(", "public static void setTopLeftH(", "public static void clampToScreen(",
         "public static void cornerAtWH(", "public static void cornerAtH(", "public static int cellOfWH(", "public static int cellOfH(",
         "public static void moveByCellsWH(", "public static void moveByCellsH(", "public static int viewH(", "public static int viewW(",
         "public boolean widthMoved(", "public boolean fill(", "protected void build({UCB} b)", "public void prepView(",
         "public int heightOf(", "public int widthOf(", "public String widgetAtCell(", "public void appendPreviews(",
         "public String swatchHex(", "public String swatch(", "public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{\n  java.util.UUID u = this.playerRef.getUuid();\n  {PKG}.WLayout l"]
pos = [s.index(o) for o in order]
assert pos == sorted(pos), "javassist order: %s" % [order[i] for i in range(len(order) - 1) if pos[i] > pos[i + 1]]
assert s.index("public static int multiW(") < s.index("public boolean widthMoved("), "Widgets before HudMain"
assert "KEEP=10" in s and "KEEP=20" not in s
assert "--deploy" in s   # the old deploy block stays as it was (never used: tools/deploy_set.py is the only deploy path)

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(kit font table: %d glyphs x 2 weights, CAPK %s)" % (len(ADV_B), CAPK))
