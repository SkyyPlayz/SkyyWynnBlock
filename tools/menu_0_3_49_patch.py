"""Derive SkyyMenu/build_skyymenu_0.3.49.py from the LIVE SkyyMenu 0.3.48 (python tools/menu_0_3_49_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_48_patch.py -> 0.3.48 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.49. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.48 (nothing else changed). Line endings kept. The harness SkyyMenu/test_skyymenu_0.3.49.py is its own file.

0.3.49 (2026-11-01) = AUGMENTS ROUND A4 "charts" (research/Augments-Spec.md 6.1 row A4, LEAN; LOOKS ONLY). Skyy (docs/answered/gear.md
  2026-10-25 AUGMENTS REPLACE POWDERS): "i want all the elements to interact realistically" + POISON AUGMENT "add it as an augment. but its a
  weapon modifier. NOT an element." The engine is live in SkyyClasses 0.1.51+ (A1); this round only SHOWS it on Character > Skills > YOUR STATS.
  1. REACTIONS = the real matrix (spec 5.2 as SkyyClasses 0.1.52's engine runs it - elemEarth / elemThunder / elemWater / elemFire / elemAir):
     a chart row = the element that hits (Earth .. Air, Wynn order), a column = the state the target already has (Burning, Wet, Chilled /
     Frozen, Shocked, Quaked, Gusted), the last column = the state that hit itself causes; reaction words in the hitting element's colour
     (tools/skyyelem.py COLORS = Style Guide 15), plain effects soft white, "-" dim. Then one row per reaction (the 15 of Classes RX_NAMES -
     build-checked) with its live number, and the rules row (one word a hit, reactCd). Replaces 0.3.45's four "later" rows.
  2. ELEMENT STATES (new section): Burning, Wet, Chilled, Frozen, Shocked, Quaked, Gusted - one line each - + Poisoned (a MODIFIER) + bosses.
     Every number is SkyyClasses' live Server Setup value: the three text rows ab.Elements / ab.ElemStates / ab.Reactions .numbers
     (config:fn:SkyyClasses "get"; key=value lists, a missing key = its default). The defaults here are cross-checked against the SET
     SkyyClasses script at build time.
  3. ELEMENT POWER on Your Stats (Elements section): NO bridge gives the per-element Power yet (SkyyGear's GearAug.power() is only in its
     tooltip) - so the row says where to see it (the weapon tooltip's ELEMENT POWER) + the rule; it reads gear:fn:elemPower apply(UUID) ->
     "Earth:0,Thunder:3,Water:0,Fire:6,Air:0" the moment a SkyyGear round publishes it (PROPOSED contract, reported; nothing publishes it
     today). Imbue: classes:fn:imbue apply(UUID) ("Fire;30" while it runs) -> "+5 Fire". The "Element states" row: on / class statuses
     only / off, from classes:fn:elemHit (SkyyClasses 0.1.51+), its elem.on row and SkyyGear's Boolean gear:elemStates. Engine missing /
     off = the states + reactions heads say it is not running here.
  4. POISON = a modifier: the Poison row says "modifier, not an element", the states list calls Poisoned a modifier, the reactions end
     with "Poison: no reactions".
  No new click (Refresh stays the one packet). Lang keys: none. SAVED DATA: none. No new class / command / system.
  ROLLBACK to 0.3.48: safe alone (the "later" reactions rows come back).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.48.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.49.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.3.48"\n') and P.has("tools/menu_0_3_48_patch.py") and not P.has("EL_MX"), "not the generated SkyyMenu 0.3.48 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.49: Augments A4 charts on Your Stats: the real reaction matrix + one row per reaction, the element states list, Element Power +
       Imbue + whether the states run, Poison shown as a modifier - every number SkyyClasses' live value (notes: tools/menu_0_3_49_patch.py).
       CHECKED: see SkyyMenu/test_skyymenu_0.3.49.py.
''')
P.rep('VERSION = "0.3.48"\n', 'VERSION = "0.3.49"\n')

# ---------- the section heads (Elements note, the Reactions note; + the Element states head at [6], [7] so 0.3.45's indices stay)
P.rep('''EL_HEADS = [("Elements", "Your element damage (held weapon) and Defence."),
            ("Strong and weak", "A mob's plate shows its element - use the one that beats it."),
            ("Reactions", "Planned as class tree nodes - not in the game yet.")]
''', '''EL_HEADS = [("Elements", "Your element damage (held weapon), Defence and Element Power."),          # 0.3.49: + Power
            ("Strong and weak", "A mob's plate shows its element - use the one that beats it."),
            ("Reactions", "Hit a target that has a state: row = your hit, column = its state."),     # 0.3.49 (A4): the real matrix
            ("Element states", "What a hit leaves on a target, at Power 5 (10 = double).")]   # 0.3.49 (A4): new
''')

# ---------- the A4 data (texts with {group.key} = SkyyClasses' live numbers; E = ab.Elements, S = ab.ElemStates, R = ab.Reactions)
P.rep('''EL_NOGEAR = "needs SkyyGear 0.3.39 (element damage + Defence)"
''', '''EL_NOGEAR = "needs SkyyGear 0.3.39 (element damage + Defence)"
# 0.3.49 (Augments A4): SkyyClasses' numbers rows (one Server Setup text row per group, "key=value,..."; a missing key = its default)
EL_NROW = [("E", "ab.Elements.numbers"), ("S", "ab.ElemStates.numbers"), ("R", "ab.Reactions.numbers")]
EL_NDEF = {"E.burnTime": 4.0, "E.burnStacks": 3.0, "E.chillSlow": 15.0, "E.chillTime": 3.0, "E.freezeAt": 3.0, "E.freezeWindow": 3.0,
           "E.freezeTime": 1.5, "E.shockVuln": 5.0, "E.shockTime": 3.0, "E.shockRange": 3.0, "E.staggerTime": 0.4, "E.staggerEvery": 3.0,
           "E.staggerDef": 10.0, "E.staggerDefTime": 4.0, "E.gustKb": 1.0, "E.bossCc": 50.0,
           "S.burnPct": 2.0, "S.wetTime": 6.0, "S.shockPct": 30.0, "S.flinchEvery": 2.0, "S.windswept": 2.0, "S.bossImmune": 8.0,
           "S.reactCd": 1.0, "S.chainMax": 3.0, "S.chainRange": 4.0, "S.mudSlow": 25.0, "S.mudTime": 3.0, "S.sandWeaken": 10.0,
           "S.sandTime": 3.0, "S.fanStacks": 4.0,
           "R.steam": 25.0, "R.douse": 25.0, "R.melt": 50.0, "R.shatter": 50.0, "R.electrocute": 50.0, "R.elecFlinch": 0.4,
           "R.grounded": 30.0, "R.sandblast": 20.0, "R.fanned": 50.0, "R.fanBurn": 25.0, "R.fanTime": 50.0, "R.stormJumps": 1.0,
           "R.stormRange": 2.0, "R.wildRange": 3.0, "R.classPart": 30.0}
EL_IMBUE_POWER = 5                         # SkyyGear 0.3.52+: "+5 while Imbue of that element runs" (spec 4.2)
# the states (spec 5.1 as SkyyClasses 0.1.52 runs them): name, value, what it does
EL_STATES = [("Burning", "{E.burnTime}s, {E.burnStacks} stacks", "Fire hit: {S.burnPct}% of the hit a second, Water / Earth end it"),
             ("Wet", "{S.wetTime}s", "Water hit, swimming or rain: can't burn - sets up Thunder and ice"),
             ("Chilled", "-{E.chillSlow}% speed", "Water on Wet, {E.chillTime}s - {E.freezeAt} Chills in {E.freezeWindow}s = Frozen"),
             ("Frozen", "{E.freezeTime}s", "can't move - Fire melts it, Earth shatters it"),
             ("Shocked", "+{E.shockVuln}% taken", "Thunder hit, {E.shockTime}s: {S.shockPct}% jumps {E.shockRange} blocks, flinch every {S.flinchEvery} hits"),
             ("Quaked", "{E.staggerTime}s stun", "every {E.staggerEvery} Earth hits: -{E.staggerDef}% Defence for {E.staggerDefTime}s"),
             ("Gusted", "+{E.gustKb} block push", "Air hit: heavy hits lift - Windswept {S.windswept}s for combos"),
             ("Poisoned", "modifier", "Poison lines: damage over time, stacks - not an element"),
             ("Bosses", "{E.bossCc}% CC", "stun / freeze / flinch shorter, then {S.bossImmune}s immune, never pushed")]
EL_STATE_NAMES = ["Burning", "Wet", "Chilled", "Frozen", "Shocked", "Quaked", "Gusted"]
assert [s_[0] for s_ in EL_STATES[:7]] == EL_STATE_NAMES
# the matrix (row = the hitting element in Wynn order, its own state, then the 6 columns: (cell, is a reaction word))
EL_MX_COLS = ["Burning", "Wet", "Chilled / Frozen", "Shocked", "Quaked", "Gusted"]
EL_MX_HEAD = ("Your hit", "It causes")
EL_MX = [("Earth", "Quaked", [("Smother", 1), ("Mud", 1), ("Shatter", 1), ("Grounded", 1), ("-", 0), ("Sandblast", 1)]),
         ("Thunder", "Shocked", [("-", 0), ("Electrocute", 1), ("-", 0), ("Refresh", 0), ("Grounded", 1), ("Storm", 1)]),
         ("Water", "Wet, Chilled", [("Douse", 1), ("Chill", 0), ("Chill x2", 0), ("Conduct", 1), ("Mud", 1), ("-", 0)]),
         ("Fire", "Burning", [("+1 stack", 0), ("Steam", 1), ("Thaw / Melt", 1), ("-", 0), ("-", 0), ("Fanned", 1)]),
         ("Air", "Gusted", [("Wildfire", 1), ("Wind Chill", 1), ("Chill +1", 0), ("Storm", 1), ("Sandblast", 1), ("Push x1.5", 0)])]
# the reactions, one row each (name, value, what happens)
EL_RXL = [("Steam", "+{R.steam}%", "Fire on Wet: a burst of the Fire part - Wet ends, no Burning"),
          ("Thaw", "Wet", "Fire on Chilled: the Chill ends and the target is Wet"),
          ("Melt", "+{R.melt}%", "Fire on Frozen: of the Fire part - the ice ends, target Wet"),
          ("Fanned", "+{R.fanned}% time", "Fire on Gusted: Burning lasts longer, holds {S.fanStacks} stacks"),
          ("Douse", "+{R.douse}%", "Water on Burning: of the Water part - fire out, target Wet"),
          ("Conduct", "{S.shockPct}% jumps", "Water on Shocked: to {S.chainMax} Wet enemies in {S.chainRange} blocks"),
          ("Mud", "-{S.mudSlow}% speed", "Earth on Wet or Water on Quaked: slowed {S.mudTime}s"),
          ("Electrocute", "+{R.electrocute}%", "Thunder on Wet: flinch {R.elecFlinch}s, chains to {S.chainMax} Wet enemies"),
          ("Grounded", "+{R.grounded}%", "Earth + Thunder (Shocked or Quaked): the Shock ends"),
          ("Storm", "+{R.stormJumps} jump", "Thunder + Air: the Shock jumps {R.stormRange} blocks further"),
          ("Smother", "all at once", "Earth on Burning: the fire ends, its damage left lands now"),
          ("Shatter", "+{R.shatter}%", "Earth on Frozen: of the Earth part - the ice breaks"),
          ("Sandblast", "+{R.sandblast}%", "Earth on Gusted or Air on Quaked: target deals -{S.sandWeaken}% {S.sandTime}s"),
          ("Wildfire", "+{R.fanBurn}% burn", "Air on Burning: +{R.fanTime}% time, spreads {R.wildRange} blocks"),
          ("Wind Chill", "Chilled", "Air on Wet: the target is Chilled")]
EL_RULES = [("One a hit", "", "one reaction word a hit (the strongest), the same one once a {S.reactCd}s"),
            ("Poison", "no reactions", "a weapon modifier, not an element - nothing reacts with it")]
# Element Power + whether the states run (SkyyClasses classes:fn:elemHit, its elem.on, SkyyGear gear:elemStates)
EL_PWHOW = "see your weapon's tooltip: augment tiers + 3 a rolled line"
EL_STV = ["off", "off", "class only", "on"]
EL_STT = ["needs SkyyClasses 0.1.51 (the element states engine)",
          "off in Server Setup, Classes, Abilities tab",          # fix 2: the tab + the row's own label
          "class statuses only - weapon hits: Server Setup, Gear",
          "your element hits put the states below on targets"]
# fix 4: class statuses (Imbue...) hit at Power 5 with only R.classPart % of the hit as the element part - shown while "class only"
EL_CLASSN = ("Class hits", "{R.classPart}% element", "class statuses (Imbue...): Power 5, this % of the hit")
EL_PMAX = 10                               # fix 3: SkyyClasses clamps Element Power to 10 (show what the engine uses)
EL_OFF = "Not running on this server - see Element states above."
_ph = re.compile(r"\\{([A-Z]\\.\\w+)\\}")


def _fill(t, nums):
    return _ph.sub(lambda m_: (lambda v: str(int(v)) if v == int(v) else repr(v))(nums[m_.group(1)]), t)


for _t in [x for r_ in EL_STATES + EL_RXL + EL_RULES + [EL_CLASSN] for x in r_]:
    for _k in _ph.findall(_t):
        assert _k in EL_NDEF, "0.3.49: no default for {%s}" % _k
    assert all(32 <= ord(c_) < 127 for c_ in _t) and not any(c_ in _t for c_ in '";<>\\\\'), "0.3.49: MenuUtil.safe would change: " + _t
assert sorted(EL_NDEF) == sorted(set(k_ for r_ in EL_STATES + EL_RXL + EL_RULES + [EL_CLASSN] for x in r_ for k_ in _ph.findall(x))), "0.3.49: every default is used"
for _r in EL_STATES + EL_RXL + EL_RULES + [EL_CLASSN]:          # StatsCalc.add clips name 32 / value 24 / the line to LINE_MAX: the defaults fit unclipped
    _v, _s = _fill(_r[1], EL_NDEF), _fill(_r[2], EL_NDEF)
    assert len(_r[0]) <= 32 and len(_v) <= 24 and len(_r[0]) + len(_v) + len(_s) + 2 <= ST_LINE_MAX, "0.3.49: row too long: %s | %s | %s" % (_r[0], _v, _s)
for _n, _v, _t in [("Element states", "class only", t_) for t_ in EL_STT] + [("Element Power", "-", EL_PWHOW),
                   ("Element Power", "held weapon", "Earth 10, Thunder 10, Water 10, Fire 10, Air 10"),
                   ("Element Power", "none", "no element Power on your held weapon"), ("Imbue", "+5 Thunder", "Element Power while your Imbue runs")]:
    assert len(_n) + len(_v) + len(_t) + 2 <= ST_LINE_MAX, _t          # StatsCalc.add would clip it
assert len(EL_MX) == 5 and [m_[0] for m_ in EL_MX] == EL.NAMES and all(len(m_[2]) == 6 for m_ in EL_MX), "0.3.49: 5 rows x 6 columns, Wynn order"
assert len(EL_MX_COLS) == 6
EL_RXW = sorted(set(c_ for m_ in EL_MX for c_, rx in m_[2] if rx))
# the matrix and the reaction list name the same reactions (Thaw / Melt = one cell, two reactions)
assert set(w_ for c_ in EL_RXW for w_ in c_.split(" / ")) == set(r_[0] for r_ in EL_RXL), "0.3.49: every matrix reaction has its row and back"
# cross-check against the SET SkyyClasses script: the reaction names (RX_NAMES) + every default number
_cls_ver = dict(_LIVE).get("SkyyClasses") if _LIVE else None
_cls_py = os.path.join(B.PROJECT, "SkyyClasses", "build_skyyclasses_%s.py" % _cls_ver) if _cls_ver else None
if _cls_py and os.path.isfile(_cls_py):
    _ct = open(_cls_py, encoding="utf-8").read()
    _rxm = re.search(r"RX_NAMES = (\\[[^\\]]*\\])", _ct)
    assert _rxm, "SkyyClasses %s has no RX_NAMES (the element reactions)" % _cls_ver
    _rxn = _ast.literal_eval(_rxm.group(1))
    assert sorted(_rxn) == sorted(r_[0].upper() for r_ in EL_RXL), "0.3.49: SkyyClasses %s reactions %s != the page's" % (_cls_ver, _rxn)
    _grp = {"E": "Elements", "S": "ElemStates", "R": "Reactions"}
    for _k, _d in sorted(EL_NDEF.items()):
        _m = re.search(r'_n\\("ab\\.%s\\.%s", "\\w+", "dec", ([0-9.]+),' % (_grp[_k[0]], _k[2:]), _ct)
        assert _m, "SkyyClasses %s has no number ab.%s.%s" % (_cls_ver, _grp[_k[0]], _k[2:])
        assert float(_m.group(1)) == _d, "0.3.49: SkyyClasses %s ab.%s.%s default %s, the page says %s" % (_cls_ver, _grp[_k[0]], _k[2:], _m.group(1), _d)
    assert '_r("ab.%s.numbers" % _aid' in _ct, "0.3.49: SkyyClasses keeps one numbers text row per group (ab.<Group>.numbers)"
    print("stats page: %d element numbers + %d reactions checked against SkyyClasses %s" % (len(EL_NDEF), len(_rxn), _cls_ver))
else:
    print("WARNING stats page: no SET SkyyClasses script found - the element numbers were not cross-checked")
''')
assert P.s.index("import ast as _ast\n") < P.s.index("    _rxn = _ast.literal_eval(_rxm.group(1))\n"), "0.3.49: _ast is imported before the cross-check"

# ---------- the widths: matrix cells / headers, the value + source columns (after stats_page() gave ST_SRC_W / ST_CELL_W)
P.rep('''ST_SHELL_JAVA = ST_SH.java("b")
''', '''# 0.3.49 (A4): every element-chart text fits its label (the client's own font tables; numbers at their defaults, then 3 digits)
for _t in EL_MX_COLS:
    assert SUI.text_width(_t, ST_COLH_FS) <= ST_CELL_W - 8, "0.3.49: matrix column head too wide: " + _t
for _m in EL_MX:
    assert SUI.text_width("%s hit" % _m[0], ST_NAME_FS, bold=True) <= ST_NAME_W - 8 and SUI.text_width(_m[1], ST_VAL_FS, bold=True) <= ST_TOT_W - 8, _m
    for _c, _rx in _m[2]:
        assert len(_c) <= 16 and SUI.text_width(_c, ST_CELL_FS, bold=True) <= ST_CELL_W - 8, "0.3.49: matrix cell too wide: " + _c
assert SUI.text_width(EL_MX_HEAD[0], ST_COLH_FS) <= ST_NAME_W - 8 and SUI.text_width(EL_MX_HEAD[1], ST_COLH_FS) <= ST_TOT_W - 8
_big = dict((k_, 999.0) for k_ in EL_NDEF)
for _r in EL_STATES + EL_RXL + EL_RULES + [EL_CLASSN, ("Element Power", "held weapon", EL_PWHOW), ("Imbue", "+5 Thunder", "Element Power while your Imbue runs")] \\
        + [("Element states", v_, t_) for v_, t_ in zip(EL_STV, EL_STT)]:
    assert SUI.text_width(_r[0], ST_NAME_FS, bold=True) <= ST_NAME_W - 8, "0.3.49: name too wide: " + _r[0]
    for _nums in (EL_NDEF, _big):
        assert SUI.text_width(_fill(_r[1], _nums), ST_VAL_FS, bold=True) <= ST_TOT_W - 8, "0.3.49: value too wide: " + _fill(_r[1], _nums)
        assert SUI.text_width(_fill(_r[2], _nums), ST_SRC_FS) <= ST_SRC_W, "0.3.49: source too wide: " + _fill(_r[2], _nums)
ST_SHELL_JAVA = ST_SH.java("b")
''')

# ---------- StatsCalc fields (EL_RX = the 0.3.45 planned list goes)
P.rep('''F(scl, "public static final String[] EL_RX = %s;" % jarr([_x for _r in EL.REACTIONS for _x in (_r[0], _r[1] + ": " + _r[2])]))
''', '''# 0.3.49 (A4): the numbers rows + defaults, the states / matrix / reaction / rule rows, the Power + states-on texts
F(scl, "public static final String[] EL_NROW = %s;" % jarr([_x for _g in EL_NROW for _x in _g]))
F(scl, "public static final String[] EL_NK = %s;" % jarr(sorted(EL_NDEF)))
F(scl, "public static final double[] EL_NV = new double[] { %s };" % ", ".join(repr(float(EL_NDEF[_k])) for _k in sorted(EL_NDEF)))
F(scl, "public static final String[] EL_ST = %s;" % jarr([_x for _r in EL_STATES for _x in _r]))
F(scl, "public static final String[] EL_MXH = %s;" % jarr(EL_MX_COLS + list(EL_MX_HEAD)))
F(scl, "public static final String[] EL_MX = %s;" % jarr([_x for _m in EL_MX for _x in ["%s hit" % _m[0], _m[1]] + [_c for _c, _rx in _m[2]]]))
F(scl, "public static final String[] EL_MXC = %s;" % jarr([EL.COLORS[_m[0]] for _m in EL_MX]))
F(scl, "public static final String[] EL_RXW = %s;" % jarr(EL_RXW))
F(scl, "public static final String[] EL_RXL = %s;" % jarr([_x for _r in EL_RXL for _x in _r]))
F(scl, "public static final String[] EL_RULE = %s;" % jarr([_x for _r in EL_RULES for _x in _r]))
F(scl, "public static final String[] EL_STV = %s;" % jarr(EL_STV))
F(scl, "public static final String[] EL_STT = %s;" % jarr(EL_STT))
F(scl, "public static final String EL_PWHOW = %s;" % jstr(EL_PWHOW))
F(scl, "public static final String EL_OFF = %s;" % jstr(EL_OFF))
F(scl, "public static final int EL_IMBP = %d;" % EL_IMBUE_POWER)
F(scl, "public static final String[] EL_CLN = %s;" % jarr(list(EL_CLASSN)))
F(scl, "public static final int EL_PMAX = %d;" % EL_PMAX)
''')

# ---------- the matrix row (a table row + its element colour at [9]) and its cell colour
P.rep('''M(scl, r"""
public static void tparts(java.util.ArrayList rows, String name, String unit,''', '''# 0.3.49 (A4): a reaction-matrix row = a table row + [9] the hitting element's colour; its cells: a reaction word in that colour, a plain
# effect soft white, "-" dim (StatsPage.build picks rxCol for a 10-string row)
M(scl, r"""
public static void rxrow(java.util.ArrayList rows, String name, String total, String[] cells, String col) {
  trow(rows, name, total, cells);
  String[] t = (String[]) rows.remove(rows.size() - 1);
  String[] r = new String[10];
  System.arraycopy(t, 0, r, 0, 9);
  r[9] = col;
  rows.add(r);
}""")
M(scl, r"""
public static String rxCol(String[] r, int k) {
  String t = r[3 + k];
  if (t == null || t.length() == 0 || "-".equals(t)) return "@DIM@";
  for (int i = 0; i < EL_RXW.length; i++) if (EL_RXW[i].equals(t)) return r.length > 9 && r[9] != null ? r[9] : "@ABS@";
  return "@ABS@";
}""".replace("@DIM@", ST_DIM).replace("@ABS@", ST_ABS))
M(scl, r"""
public static void tparts(java.util.ArrayList rows, String name, String unit,''')

# ---------- the helpers right before elemRows (after elemIdx / elemTotals): numbers, {key} fill, the engine state, Element Power + Imbue
P.rep('''M(scl, r"""
public static void elemRows(java.util.ArrayList out, java.util.UUID u) {''', '''# 0.3.49 (A4): SkyyClasses' live numbers: the defaults, then its three "key=value,..." Server Setup rows (config:fn:SkyyClasses "get");
# only the keys this page shows, a bad / missing value keeps the default. Any thread, never throws.
M(scl, r"""
public static String elNum(double v) {
  if (Double.isNaN(v) || Double.isInfinite(v)) return "0";
  double x = v;
  if (x > 1.0E6) x = 1.0E6;
  if (x < -1.0E6) x = -1.0E6;
  double q = Math.round(x * 100.0) / 100.0;
  if (q == Math.floor(q)) return String.valueOf((long) q);
  return String.valueOf(q);
}""")
M(scl, r"""
public static java.util.HashMap elNums() {
  java.util.HashMap m = new java.util.HashMap();
  for (int i = 0; i < EL_NK.length && i < EL_NV.length; i++) m.put(EL_NK[i], Double.valueOf(EL_NV[i]));
  for (int g = 0; g + 1 < EL_NROW.length; g += 2) {
    String s = null;
    try { s = cfg("SkyyClasses", EL_NROW[g + 1]); } catch (Throwable t) { s = null; }
    if (s == null) continue;
    String[] p = s.split(",");
    for (int i = 0; i < p.length; i++) {
      int e = p[i].indexOf('=');
      if (e <= 0) continue;
      String k = EL_NROW[g] + "." + p[i].substring(0, e).trim();
      if (!m.containsKey(k)) continue;
      double d = Double.NaN;
      try { d = Double.parseDouble(p[i].substring(e + 1).trim()); } catch (Throwable t) { d = Double.NaN; }
      if (Double.isNaN(d) || Double.isInfinite(d)) continue;
      m.put(k, Double.valueOf(d));
    }
  }
  return m;
}""")
M(scl, r"""
public static String elFill(String t, java.util.HashMap m) {
  if (t == null || t.indexOf('{') < 0) return t;
  StringBuilder b = new StringBuilder();
  int i = 0;
  while (i < t.length()) {
    char ch = t.charAt(i);
    int e = ch == '{' ? t.indexOf('}', i) : -1;
    if (e < 0) { b.append(ch); i++; continue; }
    Object o = m == null ? null : m.get(t.substring(i + 1, e));
    b.append(o instanceof Double ? elNum(((Double) o).doubleValue()) : "?");
    i = e + 1;
  }
  return b.toString();
}""")
# 0 = no SkyyClasses 0.1.51 engine, 1 = its elem.on is off, 2 = class statuses only (SkyyGear sends no weapon hits), 3 = on
M(scl, r"""
public static int elState() {
  if (!(br().get("classes:fn:elemHit") instanceof java.util.function.Function)) return 0;
  if (!cfgOn("SkyyClasses", "elem.on", true)) return 1;
  return Boolean.TRUE.equals(br().get("gear:elemStates")) ? 3 : 2;
}""")
# Element Power: gear:fn:elemPower apply(UUID) -> "Earth:0,Thunder:3,..." (PROPOSED - no SkyyGear publishes it yet: then the rule row);
# Imbue: classes:fn:imbue apply(UUID) -> "Fire;30" while it runs; then the states-on row
M(scl, r"""
public static void elemPower(java.util.ArrayList out, java.util.UUID u, int st) {
  Object pw = u == null ? null : call("gear:fn:elemPower", u);
  if (!(pw instanceof String)) add(out, "Element Power", "-", EL_PWHOW);
  else {
    StringBuilder sb = new StringBuilder();
    String[] ps = ((String) pw).split(",");
    for (int i = 0; i < ps.length; i++) {
      int c = ps[i].indexOf(':');
      if (c <= 0) continue;
      int e = elemIdx(ps[i].substring(0, c));
      if (e < 0) continue;
      int v = 0;
      try { v = Integer.parseInt(ps[i].substring(c + 1).trim()); } catch (Throwable t) { v = 0; }
      if (v <= 0) continue;
      if (sb.length() > 0) sb.append(", ");
      sb.append(EL_N[e]).append(' ').append(v > EL_PMAX ? EL_PMAX : v);
    }
    if (sb.length() == 0) add(out, "Element Power", "none", "no element Power on your held weapon");
    else add(out, "Element Power", "held weapon", sb.toString());          // the states head says 5 = base, 10 = double
  }
  Object im = u == null ? null : call("classes:fn:imbue", u);
  if (im instanceof String) {
    String s = (String) im;
    int sc = s.indexOf(';');
    int e = elemIdx(sc < 0 ? s : s.substring(0, sc));
    if (e >= 0) add(out, "Imbue", "+" + EL_IMBP + " " + EL_N[e], "Element Power while your Imbue runs");
  }
  int k = st < 0 || st >= EL_STV.length ? 0 : st;
  add(out, "Element states", EL_STV[k], EL_STT[k]);
}""")
M(scl, r"""
public static void elemRows(java.util.ArrayList out, java.util.UUID u) {''')

# ---------- elemRows: Poison = a modifier, Element Power after the element rows, the states section, the real reactions
P.rep('''      if ("Poison".equals(nm)) { add(out, "Poison", v + "% over " + num(cfgNum("SkyyGear", "poison.time", 10.0)) + "s", "of each hit you land - every source stacks"); continue; }''',
      '''      if ("Poison".equals(nm)) { add(out, "Poison", v + "% over " + num(cfgNum("SkyyGear", "poison.time", 10.0)) + "s", "modifier, not an element: of each hit, stacks, no reactions"); continue; }   // 0.3.49''')
P.rep('''  int[] w = wheelOf(br().get("mob:elem:wheel"));
  int[] n = elemNums(br().get("mob:elem:numbers"));
  int[] pos = new int[5];''', '''  int est = elState();          // 0.3.49 (A4): Element Power, Imbue, whether the states run
  elemPower(out, u, est);
  int[] w = wheelOf(br().get("mob:elem:wheel"));
  int[] n = elemNums(br().get("mob:elem:numbers"));
  int[] pos = new int[5];''')
P.rep('''  out.add(new String[] { null, EL_HEAD[4], EL_HEAD[5] });
  for (int i = 0; i + 1 < EL_RX.length; i += 2) add(out, EL_RX[i], "later", EL_RX[i + 1]);
}""")''', '''  java.util.HashMap nm = elNums();          // 0.3.49 (A4): the states, then the real reactions (SkyyClasses' live numbers)
  boolean run = est >= 2;
  out.add(new String[] { null, EL_HEAD[6], run ? EL_HEAD[7] : EL_OFF });
  if (est == 2) add(out, EL_CLN[0], elFill(EL_CLN[1], nm), elFill(EL_CLN[2], nm));   // fix 4: class hits use only part of the hit
  for (int i = 0; i + 2 < EL_ST.length; i += 3) add(out, EL_ST[i], elFill(EL_ST[i + 1], nm), elFill(EL_ST[i + 2], nm));
  out.add(new String[] { null, EL_HEAD[4], run ? EL_HEAD[5] : EL_OFF });
  out.add(new String[] { null, null, "", EL_MXH[0], EL_MXH[1], EL_MXH[2], EL_MXH[3], EL_MXH[4], EL_MXH[5], EL_MXH[6], EL_MXH[7] });
  for (int k = 0; k < 5 && 8 * k + 7 < EL_MX.length; k++) {
    String[] cells = new String[6];
    for (int m = 0; m < 6; m++) cells[m] = EL_MX[8 * k + 2 + m];
    rxrow(out, EL_MX[8 * k], EL_MX[8 * k + 1], cells, k < EL_MXC.length ? EL_MXC[k] : null);
  }
  for (int i = 0; i + 2 < EL_RXL.length; i += 3) add(out, EL_RXL[i], elFill(EL_RXL[i + 1], nm), elFill(EL_RXL[i + 2], nm));
  for (int i = 0; i + 2 < EL_RULE.length; i += 3) add(out, EL_RULE[i], elFill(EL_RULE[i + 1], nm), elFill(EL_RULE[i + 2], nm));
}""")''')
P.rep('''  elemRows(out, u);     // 0.3.45 (elem1): Elements, Strong and weak, Reactions
''', '''  elemRows(out, u);     // 0.3.45 (elem1): Elements, Strong and weak, Reactions (0.3.49: + Element states before Reactions)
''')

# ---------- StatsPage.build: a matrix row's cells take its element colour
P.rep('''        String cc = @PKG@.StatsCalc.cellCol(r[3 + ck], ck);''',
      '''        String cc = r.length >= 10 ? @PKG@.StatsCalc.rxCol(r, ck) : @PKG@.StatsCalc.cellCol(r[3 + ck], ck);   // 0.3.49: matrix rows''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.49 adds no system / command"
_i = P.s.index
assert _i("public static void trow(") < _i("public static void rxrow(") < _i("public static String rxCol(") < _i("public static void elemRows(")
assert _i("public static String cfg(String mod") < _i("public static java.util.HashMap elNums()") < _i("public static String elFill(") \
    < _i("public static int elState()") < _i("public static void elemPower(")
assert _i("public static boolean cfgOn(") < _i("public static int elState()") and _i("public static Object call(String key") < _i("public static void elemPower(")
assert _i("public static int elemIdx(") < _i("public static int[] elemNums(") < _i("public static void elemPower(") < _i("public static void elemRows(")
P.finish()
