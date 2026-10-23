"""Derive SkyyMobs/build_skyymobs_0.1.17.py from the GENERATED 0.1.16 (build_skyymobs_0.1.16.py = the tools/deploy_set.py SET pin, made by
tools/mobs_0_1_16_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with 0.1.16
(tools/soundpass_gen.Patch); line endings kept.
Run:  python tools/mobs_0_1_17_patch.py   then   python SkyyMobs/build_skyymobs_0.1.17.py   then   python SkyyMobs/test_skyymobs_0.1.17.py
Edit THIS file, never the generated script (never --deploy).

0.1.17 (2026-10-22) = WYNN ELEMENTS, THE MOB SIDE (FULL round elem1 with SkyyGear 0.3.39, SkyyClasses 0.1.46, SkyyPets 0.4.10, SkyyAccessories
  0.5.32, SkyyMenu 0.3.45 - pin + roll back TOGETHER). research/Wynn-Elements-Build-Spec.md sections 2.1, 3.3, 4.1, 5, 8 + Skyy's answers
  (docs/answered/gear.md 2026-10-18): Q5 "Yes (Recommended)" (Resist -25 / Weak +25 / bosses -50 on their own element / never immune / the
  Fire + Frost dragons keep their element), Q7 "show what elements the mob has/ uses. so if its a fire mob, it shows fire above it, and the
  player has to know from that, that it is weak to water. (we can make a chart showing which elements each element is strong and weak to",
  Q4 Defence "Now" (so mobs deal element damage in the same build). Shared names / colours / wheel: tools/skyyelem.py.
  1. ROW elem.mobs "Mob elements" (Server Setup -> Mobs -> Elements, text, max 2000; the bosses.roles text style because the kit's key
     tables refuse * in an entry): comma separated "Match=Own" or "Match=Own/Resist/Weak" (Match = a role id or MobGlob pattern - any case,
     exact, Prefix*, *Part*; Own / Resist / Weak = Earth / Thunder / Water / Fire / Air / none; an empty Resist = the own element, an empty
     Weak = the element that beats it on the wheel). The most specific match wins (most literal characters, then the first entry). Default:
     the vanilla elemental families (every pattern matches a vanilla 0.7.2 role, build-checked): frost / ice mobs Water (Yeti, Frost Golem,
     Frost Skeletons / Zombies weak to Fire - "ice melts", the ONE exception the chart lists), burnt / ember / firesteel / magma Fire, sand /
     earth / root / Scarak / Cactee Earth, thunder crystals + spirits + the Void Thunder, Pterodactyl + Windwalker Air, fish Water, Dragon_Fire
     Fire, Dragon_Frost Water - all on the pure wheel (fix round elem1fix: Skyy Q7 "the player has to know from that, that it is weak to
     water" = the plate + the chart must tell the weakness; plain skeletons / zombies neutral). A refused word / pattern -> check= hook.
  2. ROWS elem.weak 25 %, elem.resist 25 %, elem.bossResist 50 % (a boss - bosses.roles + the pack bosses - hit with its OWN element),
     elem.mobShare 30 % (that share of an elemental mob's hit on a player is its element), elem.plate (bool, true), elem.wheel
     ("Earth>Thunder>Water>Fire>Air", check= hook: the 5 names once each). All live (after=MobCfg.elemEdit; the table + plate rows re-apply
     the loaded mobs through derive's signature so their plates change at once).
  3. BRIDGE mob:fn:elem apply(Object[]{ String roleId, String element }) -> Integer % (+weak, -bossResist, -resist or 0; unknown role /
     element / bad args = 0; "Lightning" / "Wind" read as Thunder / Air), cached per role + element until the next edit;
     mob:fn:elemOf apply(String roleId) -> the own element name or null; Strings mob:elem:wheel (the wheel) and mob:elem:numbers (+ Boolean mob:elem:custom = elem.mobs is not the default, elem1fix2)
     ("25;25;50" = weak;resist;boss, SkyyMenu's chart). Any thread, never throws; removed in shutdown.
  4. MOB ELEMENT HITS (spec 3.3, D5): LevelDamage (Filter, before armour; the existing system - no new system): a mob with an own element hits a
     PLAYER for amount - cut, cut = (amount x mobShare %) x D / (S + D), D = gear:fn:elemDef {player UUID, element} (SkyyGear 0.3.39: worn
     armour + charms + pets element Defence), S = gear:elem:defScale (Integer, absent = 100). No SkyyGear / no Defence = exactly 0.1.16's
     damage; Defence only ever lowers a hit; the cause is never changed (vanilla Fire resistances on real Fire hits stay). Unlevelled mobs
     too (the One hit at most branch).
  5. NAME PLATE (spec 8, D8): a levelled mob with an own element shows " - Fire" after its plate text (elem.plate on); a plate.format holding
     the new token {element} puts it there instead (no file update: the default format is unchanged, the element is appended - so no
     one-time migration is needed). With the trial colour markup on, the element part takes the element's colour (tools/skyyelem.py).
  6. Ready line: "elements: N rows, wheel Earth>..., mob share 30 %". /mobs inspect is unchanged.
  SAVED DATA: none (new rows: a file without the line = the default; no migration). One new tab (Elements), 3 new classes (MobElem, MobElemFn,
  MobElemOfFn), no new command / system.
  ROLLBACK to 0.1.16: alone it is safe (no saved data; the rows are ignored, plates lose the element) - but roll back with the elem1 set
  (SkyyGear 0.3.39 turns armour element Defence on only because mobs deal element damage here, Skyy Q4 "Now").
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.16.py"), os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.17.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.1.16"') and P.s.startswith('"""SkyyMobs 0.1.16 - build script') and not P.has("MobElem"), "not the SET pin 0.1.16"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("pool.makeClass(")
HEAD = open(os.path.abspath(__file__), encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.17 (2026-10-22)"):].rstrip() + "\n\n"

P.rep('''"""SkyyMobs 0.1.16 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_16_patch.py from the SET pin 0.1.15 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.16.py -> SkyyMobs/SkyyMobs-0.1.16.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.16.py
''', '''"""SkyyMobs 0.1.17 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_17_patch.py from the SET pin 0.1.16 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.17.py -> SkyyMobs/SkyyMobs-0.1.17.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.17.py
''' + NOTE)
P.rep('VERSION = "0.1.16"', 'VERSION = "0.1.17"')

# ---------- the defaults (Python, checked against the vanilla roles)
P.rep('''P4_RANK_DOC = [''', '''# 0.1.17 (elem1): the mob element table (research/Wynn-Elements-Build-Spec.md 4.1; names / wheel / colours: tools/skyyelem.py)
import skyyelem as EL
ELEM_ROWS = [("Skeleton_Burnt*", "Fire"), ("Zombie_Burnt", "Fire"),          # elem1fix: the pure wheel except "ice melts" (the chart's one exception)
             ("Skeleton_Frost*", "Water/Water/Fire"), ("Zombie_Frost", "Water/Water/Fire"), ("Spirit_Frost", "Water"), ("Bat_Ice", "Water"),
             ("Yeti", "Water/Water/Fire"), ("Golem_Crystal_Frost", "Water/Water/Fire"), ("Dragon_Frost", "Water"),
             ("Skeleton_Sand*", "Earth"), ("Dungeon_Skeleton_Sand*", "Earth"), ("Zombie_Sand", "Earth"),
             ("Golem_Crystal_Sand", "Earth"), ("Golem_Crystal_Earth", "Earth"), ("Spirit_Root", "Earth"),
             ("Scarak*", "Earth"), ("Dungeon_Scarak*", "Earth"), ("Cactee", "Earth"),
             ("Golem_Crystal_Flame", "Fire"), ("Golem_Firesteel", "Fire"), ("Emberwulf", "Fire"), ("Spirit_Ember", "Fire"),
             ("Toad_Rhino_Magma", "Fire"), ("Dragon_Fire", "Fire"), ("Golem_Crystal_Thunder", "Thunder"), ("Spirit_Thunder", "Thunder"),
             ("*Void*", "Thunder"), ("Pterodactyl", "Air"), ("Feran_Windwalker", "Air"), ("Fen_Stalker", "Water"),
             ("Piranha*", "Water"), ("Shark*", "Water"), ("Frostgill", "Water"), ("Eel_Moray", "Water")]
ELEM_MOBS_DEF = ", ".join("%s=%s" % _r for _r in ELEM_ROWS)
ELEM_NUM_DEF = {"weak": 25, "resist": 25, "bossResist": 50, "mobShare": 30}


def elem_parse(v):
    """the Python mirror of MobElem.parse: [(pattern lower, spec, own, resist, weak)] with '' = none; raises on a bad entry"""
    out = []
    for _e in (v or "").split(","):
        _e = _e.strip()
        if not _e:
            continue
        _m, _s, _w = _e.partition("=")
        assert _s and _m.strip() and "=" not in _w, _e
        _p = _w.split("/")
        assert len(_p) in (1, 3), _e
        _own = EL.norm(_p[0])
        _res = _own if len(_p) == 1 or not _p[1].strip() else EL.norm(_p[1])
        _wk = (EL.beats(_own) if _own else "") if len(_p) == 1 or not _p[2].strip() else EL.norm(_p[2])
        assert None not in (_own, _res, _wk), _e
        out.append((_m.strip().lower(), len(_m.replace("*", "").strip()), _own, _res, _wk))
    return out


def elem_row(rows, role):
    best, bs = None, -1
    for _r in rows:
        if _r[1] > bs and glob(_r[0], role):
            best, bs = _r, _r[1]
    return best


def elem_mod(rows, role, e, boss):
    """the Python mirror of MobElem.mod at the default numbers"""
    _r = elem_row(rows, role)
    if _r is None or not e:
        return 0
    if e == _r[4]:
        return ELEM_NUM_DEF["weak"]
    if boss and e == _r[2]:
        return -ELEM_NUM_DEF["bossResist"]
    if e == _r[3]:
        return -ELEM_NUM_DEF["resist"]
    return 0


_EROWS = elem_parse(ELEM_MOBS_DEF)
assert len(_EROWS) == len(ELEM_ROWS) and len(ELEM_MOBS_DEF) <= 2000 and all(ord(_c) < 127 for _c in ELEM_MOBS_DEF)
for _r in ELEM_ROWS:
    assert any(glob(_r[0], _n) for _n in VANILLA), "0.1.17: elem.mobs pattern %s matches no vanilla role" % _r[0]
assert elem_row(_EROWS, "Skeleton_Burnt_Knight")[2] == "Fire" and elem_row(_EROWS, "Skeleton_Frost_Archer")[2] == "Water", "most specific wins"
assert elem_mod(_EROWS, "Yeti", "Fire", False) == 25 and elem_mod(_EROWS, "Yeti", "Water", False) == -25, "spec 10.6: Yeti Fire +25, Water -25"
assert elem_mod(_EROWS, "Dragon_Fire", "Fire", True) == -50 and elem_mod(_EROWS, "Dragon_Fire", "Water", True) == 25, "spec 10.6: the Fire dragon"
assert elem_mod(_EROWS, "Trork_Warrior", "Fire", False) == 0 and elem_mod(_EROWS, "Skeleton", "Fire", False) == 0 and elem_mod(_EROWS, "Skeleton", "Water", False) == 0
assert elem_mod(_EROWS, "Golem_Crystal_Flame", "Water", False) == 25 and elem_mod(_EROWS, "Crawler_Void", "Earth", False) == 25 and elem_mod(_EROWS, "Crawler_Void", "Fire", False) == 0
# elem1fix (Skyy Q7: the plate's element tells the weakness): every row's weakness is the wheel's, except the "ice melts" rows the Menu chart names
_ICE = ("Skeleton_Frost*", "Zombie_Frost", "Yeti", "Golem_Crystal_Frost")
for _r in _EROWS:
    if _r[2]:
        assert _r[3] == _r[2] and (_r[4] == EL.beats(_r[2])) != (_r[0] in [_x.lower() for _x in _ICE]), "elem1fix: %s off the wheel" % _r[0]
_elem_cover = sorted(set(_n for _n in VANILLA for _r in ELEM_ROWS if glob(_r[0], _n) and _r[1].split("/")[0] != "none"))
print("0.1.17 elements: %d elem.mobs rows (%d chars), %d vanilla roles with an own element" % (len(ELEM_ROWS), len(ELEM_MOBS_DEF), len(_elem_cover)))
P4_RANK_DOC = [''')
P.rep('''CFG_LINES += PACK_DOC16 + ["%s=%s" % (_r[0], _r[1]) for _r in PACK_ROWS16]          # 0.1.16 (packprep): the pack rows (absent in an older file = the default)''',
      '''CFG_LINES += PACK_DOC16 + ["%s=%s" % (_r[0], _r[1]) for _r in PACK_ROWS16]          # 0.1.16 (packprep): the pack rows (absent in an older file = the default)
CFG_LINES += ["# Elements (SkyyMobs 0.1.17): elem.mobs = Match=Own or Match=Own/Resist/Weak (Earth Thunder Water Fire Air none; blank = the wheel).",
              "# A mob takes elem.weak % more from the element it is weak to, elem.resist % less from its resist (a boss elem.bossResist % less",
              "# from its own element); elem.mobShare % of an elemental mob's hit on a player is its element (element Defence lowers that part).",
              "elem.mobs=" + ELEM_MOBS_DEF, "elem.weak=%d" % ELEM_NUM_DEF["weak"], "elem.resist=%d" % ELEM_NUM_DEF["resist"],
              "elem.bossResist=%d" % ELEM_NUM_DEF["bossResist"], "elem.mobShare=%d" % ELEM_NUM_DEF["mobShare"], "elem.plate=true",
              "elem.wheel=" + EL.WHEEL_DEF]          # 0.1.17 (elem1): the element rows (absent in an older file = the default)''')

# ---------- the rows (Elements tab, after Ranks)
P.rep('''CFG_TITLE = "Mobs"
''', '''# 0.1.17 (elem1): the Elements tab (research/Wynn-Elements-Build-Spec.md 5) - every row live (MobCfg.elemEdit re-applies the loaded mobs)
CFG_CATS.insert(CFG_CATS.index(("rank", "Ranks")) + 1, ("elem", "Elements"))
CFG_ROWS += [
    ("elem.mobs", "Mob elements", "elem", "text", ELEM_MOBS_DEF, "", "2000", "", "", "live",
     "Role or Prefix*=Element or =Element/Resist/Weak (blank = wheel). Earth Thunder Water Fire Air none.",
     "field:MobCfg.ELEM_MOBS;after=MobCfg.elemEdit;check=MobHooks.checkElemMobs"),
    ("elem.weak", "Weak: extra damage", "elem", "int", str(ELEM_NUM_DEF["weak"]), "0", "100", "", "%", "live",
     "A mob takes this much more from the element that beats it (only that element's part of the hit).",
     "field:MobCfg.ELEM_WEAK;after=MobCfg.elemEdit"),
    ("elem.resist", "Resist: damage cut", "elem", "int", str(ELEM_NUM_DEF["resist"]), "0", "90", "", "%", "live",
     "A mob takes this much less from its resist element (its own one unless the row says another).",
     "field:MobCfg.ELEM_RESIST;after=MobCfg.elemEdit"),
    ("elem.bossResist", "Boss: own element cut", "elem", "int", str(ELEM_NUM_DEF["bossResist"]), "0", "90", "", "%", "live",
     "A boss takes this much less from its OWN element (never immune). Bosses = Boss roles + pack bosses.",
     "field:MobCfg.ELEM_BOSS;after=MobCfg.elemEdit"),
    ("elem.mobShare", "Mob hit dealt as its element", "elem", "int", str(ELEM_NUM_DEF["mobShare"]), "0", "100", "", "%", "live",
     "This share of an elemental mob's hit on a player is its element; element Defence cuts that part.",
     "field:MobCfg.ELEM_SHARE;after=MobCfg.elemEdit"),
    ("elem.plate", "Element on the name plate", "elem", "bool", "true", "", "", "", "", "live",
     "A Fire mob's plate ends with - Fire (or shows it where {element} sits in the nameplate text).",
     "field:MobCfg.ELEM_PLATE;after=MobCfg.elemEdit"),
    ("elem.wheel", "Element wheel", "elem", "text", EL.WHEEL_DEF, "", "60", "", "", "live",
     "Each element beats the next, the last beats the first. A mob is weak to the one that beats its own.",
     "field:MobCfg.ELEM_WHEEL;after=MobCfg.elemEdit;check=MobHooks.checkWheel"),
]
assert _dp.get("plate.format") == FORMAT_DEF and "{element}" not in FORMAT_DEF, "0.1.17: the default plate format is unchanged (no migration)"
CFG_TITLE = "Mobs"
''')
P.rep('''     "{level} = the level, {name} = the mob's name. Must hold {level}.",''',
      '''     "{level} = level, {name} = name, {element} = - Fire (else at the end). Must hold {level}.",''')

# ---------- MobCfg fields
P.rep('''          "public static volatile int PACK_FIXED = 0;"):
    F(cfg, f)
''', '''          "public static volatile int PACK_FIXED = 0;"):
    F(cfg, f)
# 0.1.17 (elem1): the element rows
for f in ("public static volatile String ELEM_MOBS = %s;" % jstr(ELEM_MOBS_DEF), "public static volatile int ELEM_WEAK = %d;" % ELEM_NUM_DEF["weak"],
          "public static volatile int ELEM_RESIST = %d;" % ELEM_NUM_DEF["resist"], "public static volatile int ELEM_BOSS = %d;" % ELEM_NUM_DEF["bossResist"],
          "public static volatile int ELEM_SHARE = %d;" % ELEM_NUM_DEF["mobShare"], "public static volatile boolean ELEM_PLATE = true;",
          "public static volatile String ELEM_WHEEL = %s;" % jstr(EL.WHEEL_DEF)):
    F(cfg, f)
''')

# ---------- the classes
P.rep('''mss = pool.makeClass(PKG + ".SpoilsSys", pool.get(G["ETS"]))   # 0.1.15: ... the death system (after DropDeathItems)
''', '''mss = pool.makeClass(PKG + ".SpoilsSys", pool.get(G["ETS"]))   # 0.1.15: ... the death system (after DropDeathItems)
mel = pool.makeClass(PKG + ".MobElem")       # 0.1.17 (elem1): the element table, the wheel, the modifiers, the mob element hit cut
mef = pool.makeClass(PKG + ".MobElemFn")     # 0.1.17: mob:fn:elem
meo = pool.makeClass(PKG + ".MobElemOfFn")   # 0.1.17: mob:fn:elemOf
''')
P.rep('''ALL = [lg, gb, bd, mi, cfg, lv, hk, dm, dmu, fn, ps, sc, pt, rf, mh, mc, mm, gp, gd, gdu, ifn, m14, lat, mcr, crs, cfn, sfn, bfn, m11, m12, mp4, msp, mss]''',
      '''ALL = [lg, gb, bd, mi, cfg, lv, hk, dm, dmu, fn, ps, sc, pt, rf, mh, mc, mm, gp, gd, gdu, ifn, m14, lat, mcr, crs, cfn, sfn, bfn, m11, m12, mp4, msp, mss, mel, mef, meo]''')

# ---------- MobElem (before MobCfg.apply / elemEdit call it; it uses MobCfg's fields + isBoss + MobGlob)
P.rep('''M(cfg, r"""
public static synchronized void apply(java.util.Properties c, java.util.Properties b) {''', '''# 0.1.17 (elem1): MobElem - the element table (elem.mobs), the wheel, mob:fn:elem's modifier, the mob element hit cut. Element index =
# Wynn order (0 Earth, 1 Thunder, 2 Water, 3 Fire, 4 Air; -1 none, -2 unknown); every String on the bridge is a Wynn name.
for _f in ("public static final String[] NAMES = %s;" % ("new String[] { " + ", ".join(jstr(_n) for _n in EL.NAMES) + " }"),
           "public static final String[] HEX = %s;" % ("new String[] { " + ", ".join(jstr(EL.COLORS[_n]) for _n in EL.NAMES) + " }"),
           "public static volatile Object[] TAB = null;",          # { String[] pattern (lower), int[] spec, int[] own, int[] resist, int[] weak }
           "public static volatile int[] WORD = new int[] { 0, 1, 2, 3, 4 };",          # wheel position -> element
           "public static volatile int[] WPOS = new int[] { 0, 1, 2, 3, 4 };",          # element -> wheel position
           "public static volatile java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();",
           "public static volatile boolean ANY = false;",          # some row has an own element and elem.mobShare > 0 (LevelDamage's fast exit)
           "public static volatile int ROWS = 0;"):
    F(mel, _f)
M(mel, r"""
public static int idx(String s) {
  if (s == null) return -2;
  String t = s.trim();
  if (t.length() == 0 || t.equalsIgnoreCase("none") || t.equals("-")) return -1;
  for (int i = 0; i < NAMES.length; i++) if (NAMES[i].equalsIgnoreCase(t)) return i;
  if (t.equalsIgnoreCase("Lightning")) return 1;
  if (t.equalsIgnoreCase("Wind")) return 4;
  return -2;
}""")
M(mel, "public static String name(int e) { return e >= 0 && e < 5 ? NAMES[e] : \\"\\"; }")
# the wheel text -> wheel position -> element (null = not the 5 names once each)
M(mel, r"""
public static int[] wheelOf(String v) {
  if (v == null) return null;
  String[] p = v.split(">", -1);
  if (p.length != 5) return null;
  int[] w = new int[5];
  boolean[] seen = new boolean[5];
  for (int i = 0; i < 5; i++) {
    int e = idx(p[i]);
    if (e < 0 || seen[e]) return null;
    seen[e] = true;
    w[i] = e;
  }
  return w;
}""")
M(mel, r"""
public static int beatsIn(int[] word, int e) {
  if (e < 0 || e > 4 || word == null) return -1;
  for (int i = 0; i < 5; i++) if (word[i] == e) return word[(i + 4) % 5];
  return -1;
}""")
# one entry "Match=Own[/Resist/Weak]" -> int[] { own, resist, weak } (-1 none) or null + why[0] (the check= hook and the loader share it)
M(mel, r"""
public static int[] entry(String e, int[] word, String[] why) {
  int q = e.indexOf('=');
  if (q <= 0 || e.indexOf('=', q + 1) >= 0) { why[0] = "'" + e + "' needs Match=Element (one = sign)."; return null; }
  if (e.substring(0, q).trim().length() == 0 || e.substring(0, q).trim().replace("*", "").length() == 0) { why[0] = "'" + e + "' needs a role id or pattern before =."; return null; }
  String[] p = e.substring(q + 1).split("/", -1);
  if (p.length != 1 && p.length != 3) { why[0] = "'" + e + "': write Element or Element/Resist/Weak."; return null; }
  int own = idx(p[0]);
  if (own < -1) { why[0] = "'" + p[0].trim() + "' is no element (Earth Thunder Water Fire Air none)."; return null; }
  int res = own;
  int weak = own < 0 ? -1 : beatsIn(word, own);
  if (p.length == 3) {
    if (p[1].trim().length() > 0) { res = idx(p[1]); if (res < -1) { why[0] = "'" + p[1].trim() + "' is no element."; return null; } }
    if (p[2].trim().length() > 0) { weak = idx(p[2]); if (weak < -1) { why[0] = "'" + p[2].trim() + "' is no element."; return null; } }
  }
  return new int[] { own, res, weak };
}""")
# the whole text: null = fine, else the first problem
M(mel, r"""
public static String err(String v, String wheel) {
  if (v == null) return null;
  int[] w = wheelOf(wheel);
  if (w == null) w = WORD;
  String[] parts = v.split(",");
  String[] why = new String[1];
  for (int i = 0; i < parts.length; i++) {
    String e = parts[i].trim();
    if (e.length() == 0) continue;
    if (entry(e, w, why) == null) return why[0];
  }
  return null;
}""")
M(mel, r"""
public static Object[] parse(String v, int[] word) {
  java.util.ArrayList pt = new java.util.ArrayList();
  java.util.ArrayList ev = new java.util.ArrayList();
  String[] parts = (v == null ? "" : v).split(",");
  String[] why = new String[1];
  for (int i = 0; i < parts.length; i++) {
    String e = parts[i].trim();
    if (e.length() == 0) continue;
    int[] r = entry(e, word, why);
    if (r == null) { @PKG@.MobLog.warnOnce("elem:" + e, "elem.mobs: " + why[0] + " - that entry is skipped"); continue; }
    pt.add(e.substring(0, e.indexOf('=')).trim().toLowerCase());
    ev.add(r);
  }
  int n = pt.size();
  String[] pat = new String[n];
  int[] sp = new int[n], own = new int[n], res = new int[n], wk = new int[n];
  for (int i = 0; i < n; i++) {
    pat[i] = (String) pt.get(i);
    sp[i] = @PKG@.MobGlob.spec(pat[i]);
    int[] r = (int[]) ev.get(i);
    own[i] = r[0]; res[i] = r[1]; wk[i] = r[2];
  }
  return new Object[] { pat, sp, own, res, wk };
}""")
M(mel, r"""
public static java.util.Map bridge() {
  try {
    Object o = System.getProperties().get("skyy.bridge");
    return o instanceof java.util.Map ? (java.util.Map) o : null;
  } catch (Throwable t) { return null; }
}""")
M(mel, r"""
public static String wheelText() {
  int[] w = WORD;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < 5; i++) { if (i > 0) sb.append('>'); sb.append(NAMES[w[i]]); }
  return sb.toString();
}""")
M(mel, r"""
public static synchronized void derive() {
  int[] w = wheelOf(@PKG@.MobCfg.ELEM_WHEEL);
  if (w == null) {
    @PKG@.MobLog.warnOnce("elemwheel:" + @PKG@.MobCfg.ELEM_WHEEL, "elem.wheel '" + @PKG@.MobCfg.ELEM_WHEEL + "' is not the 5 elements once each - using @WHEEL@");
    w = wheelOf("@WHEEL@");
  }
  int[] pos = new int[5];
  for (int i = 0; i < 5; i++) pos[w[i]] = i;
  WORD = w;
  WPOS = pos;
  Object[] t = parse(@PKG@.MobCfg.ELEM_MOBS, w);
  int[] own = (int[]) t[2];
  boolean any = false;
  for (int i = 0; i < own.length; i++) if (own[i] >= 0) any = true;
  TAB = t;
  ROWS = own.length;
  ANY = any && @PKG@.MobCfg.ELEM_SHARE > 0;
  CACHE = new java.util.concurrent.ConcurrentHashMap();
  java.util.Map b = bridge();
  if (b != null) {
    try {
      b.put("mob:elem:wheel", wheelText());
      b.put("mob:elem:numbers", @PKG@.MobCfg.ELEM_WEAK + ";" + @PKG@.MobCfg.ELEM_RESIST + ";" + @PKG@.MobCfg.ELEM_BOSS);
      String em = @PKG@.MobCfg.ELEM_MOBS;          // elem1fix2: TRUE = the admin edited Mob elements (SkyyMenu's chart then names no default exceptions)
      b.put("mob:elem:custom", Boolean.valueOf(em == null || !@DEFMOBS@.equals(em.trim())));
    } catch (Throwable x) { }
  }
}""".replace("@WHEEL@", EL.WHEEL_DEF).replace("@DEFMOBS@", jstr(ELEM_MOBS_DEF)))
# the row of a role: the most literal characters, the first entry on a tie; -1 = none
M(mel, r"""
public static int row(String role) {
  Object[] t = TAB;
  if (t == null || role == null) return -1;
  String[] p = (String[]) t[0];
  int[] sp = (int[]) t[1];
  String k = role.toLowerCase();
  int best = -1, bs = -1;
  for (int i = 0; i < p.length; i++) if (sp[i] > bs && @PKG@.MobGlob.glob(p[i], k)) { best = i; bs = sp[i]; }
  return best;
}""")
M(mel, r"""
public static int ownOf(String role) {
  int r = row(role);
  if (r < 0) return -1;
  return ((int[]) TAB[2])[r];
}""")
M(mel, "public static String word(String role) { return name(ownOf(role)); }")
M(mel, r"""
public static String hex(String role) {
  int e = ownOf(role);
  return e >= 0 ? HEX[e] : "#ffffff";
}""")
# spec 4.1: +weak when e is the row's Weak; -bossResist when a boss is hit with its OWN element; -resist when e is its Resist; else 0
M(mel, r"""
public static int mod(String role, int e) {
  if (role == null || e < 0 || e > 4) return 0;
  Object[] t = TAB;
  int r = row(role);
  if (r < 0 || t == null) return 0;
  int own = ((int[]) t[2])[r];
  int res = ((int[]) t[3])[r];
  int wk = ((int[]) t[4])[r];
  if (wk >= 0 && e == wk) return @PKG@.MobCfg.ELEM_WEAK;
  if (own >= 0 && e == own && @PKG@.MobCfg.isBoss(role)) return -@PKG@.MobCfg.ELEM_BOSS;
  if (res >= 0 && e == res) return -@PKG@.MobCfg.ELEM_RESIST;
  return 0;
}""")
M(mel, r"""
public static Integer modOf(String role, String elem) {
  int e = idx(elem);
  if (role == null || e < 0) return Integer.valueOf(0);
  java.util.concurrent.ConcurrentHashMap c = CACHE;
  String k = e + "|" + role;
  Object o = c.get(k);
  if (o instanceof Integer) return (Integer) o;
  Integer v = Integer.valueOf(mod(role, e));
  if (c.size() > 4096) c.clear();
  c.put(k, v);
  return v;
}""")
# the player's element Defence from SkyyGear (gear:fn:elemDef {UUID, element}); 0 = none / no SkyyGear / a failure
M(mel, r"""
public static int defOf(java.util.UUID u, int e) {
  java.util.Map b = bridge();
  if (b == null || u == null || e < 0) return 0;
  Object f = b.get("gear:fn:elemDef");
  if (!(f instanceof java.util.function.Function)) return 0;
  try {
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, NAMES[e] });
    if (r instanceof Number) { int d = ((Number) r).intValue(); return d > 0 ? d : 0; }
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("elemdef", "gear:fn:elemDef failed (" + t + ") - element hits count as 0 Defence"); }
  return 0;
}""")
M(mel, r"""
public static double scale() {
  java.util.Map b = bridge();
  Object o = b == null ? null : b.get("gear:elem:defScale");
  if (o instanceof Number) { double s = ((Number) o).doubleValue(); if (s >= 1.0) return s; }
  return 100.0;
}""")
# spec 3.3: amount - (amount x share %) x D / (S + D); D = 0 -> exactly amount
M(mel, r"""
public static double cutBy(double amt, int share, int d, double s) {
  if (!(amt > 0.0) || share <= 0 || d <= 0 || !(s > 0.0)) return amt;
  double part = amt * (double) share / 100.0;
  double cut = part * (double) d / (s + (double) d);
  double r = amt - cut;
  return r < 0.0 ? 0.0 : r;
}""")
M(mel, r"""
public static double cutHit(String role, java.util.UUID u, double amt) {
  if (!ANY || role == null || u == null || !(amt > 0.0)) return amt;
  int e = ownOf(role);
  if (e < 0) return amt;
  int d = defOf(u, e);
  if (d <= 0) return amt;
  return cutBy(amt, @PKG@.MobCfg.ELEM_SHARE, d, scale());
}""")
M(mel, r"""
public static String text() {
  return ROWS + " element rows, wheel " + wheelText() + ", weak +" + @PKG@.MobCfg.ELEM_WEAK + " %, resist -" + @PKG@.MobCfg.ELEM_RESIST + " %, boss own -" + @PKG@.MobCfg.ELEM_BOSS
    + " %, mob share " + @PKG@.MobCfg.ELEM_SHARE + " %, plates " + (@PKG@.MobCfg.ELEM_PLATE ? "on" : "off") + " (mob:fn:elem, mob:fn:elemOf)";
}""")
# mob:fn:elem / mob:fn:elemOf (any thread, never throw)
mef.addInterface(pool.get("java.util.function.Function"))
C(mef, "public MobElemFn() { }")
M(mef, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return Integer.valueOf(0);
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[0] instanceof String) || !(a[1] instanceof String)) return Integer.valueOf(0);
    return @PKG@.MobElem.modOf((String) a[0], (String) a[1]);
  } catch (Throwable t) { return Integer.valueOf(0); }
}""")
meo.addInterface(pool.get("java.util.function.Function"))
C(meo, "public MobElemOfFn() { }")
M(meo, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof String)) return null;
    String w = @PKG@.MobElem.word((String) o);
    return w.length() == 0 ? null : w;
  } catch (Throwable t) { return null; }
}""")
# the after= hook of every element row: the table / wheel / numbers in force at once, then derive (its signature re-applies the loaded mobs'
# plates when the table or the plate switch changed)
M(cfg, r"""
public static void elemEdit(String key) {
  @PKG@.MobElem.derive();
  derive(key);
}""")
M(cfg, r"""
public static synchronized void apply(java.util.Properties c, java.util.Properties b) {''')
P.rep('''  bosses(null);
  RANK_ELITE_ROLES''', '''  bosses(null);
  ELEM_MOBS = c.getProperty("elem.mobs", @ELMDEF@).trim();          // 0.1.17 (elem1): a file without a line = the default
  ELEM_WEAK = intOf(c.getProperty("elem.weak"), @ELW@, 0, 100);
  ELEM_RESIST = intOf(c.getProperty("elem.resist"), @ELR@, 0, 90);
  ELEM_BOSS = intOf(c.getProperty("elem.bossResist"), @ELB@, 0, 90);
  ELEM_SHARE = intOf(c.getProperty("elem.mobShare"), @ELS@, 0, 100);
  ELEM_PLATE = bool(c.getProperty("elem.plate"), true);
  ELEM_WHEEL = c.getProperty("elem.wheel", @ELWH@).trim();
  @PKG@.MobElem.derive();
  RANK_ELITE_ROLES''')
P.rep('''   .replace("@PBDEF@", jstr(PACK_BOSS_DEF))''', '''   .replace("@ELMDEF@", jstr(ELEM_MOBS_DEF)).replace("@ELW@", str(ELEM_NUM_DEF["weak"])).replace("@ELR@", str(ELEM_NUM_DEF["resist"]))
   .replace("@ELB@", str(ELEM_NUM_DEF["bossResist"])).replace("@ELS@", str(ELEM_NUM_DEF["mobShare"])).replace("@ELWH@", jstr(EL.WHEEL_DEF))          # 0.1.17
   .replace("@PBDEF@", jstr(PACK_BOSS_DEF))''')
# the health / plate signature: + the element table and the plate switch (an edit re-applies the loaded mobs = their plates)
P.rep('''RANK_MINI_HP + "|" + RANK_BOSS_BASE + "|" + BOSS_ROLES + "|" + PACK_BOSSES + "|" + PACK_MINIS + "|" + PACK_MOBS + "|" + PACK_NEVER;          // 0.1.16''',
      '''RANK_MINI_HP + "|" + RANK_BOSS_BASE + "|" + BOSS_ROLES + "|" + PACK_BOSSES + "|" + PACK_MINIS + "|" + PACK_MOBS + "|" + PACK_NEVER          // 0.1.16
    + "|elem|" + ELEM_MOBS + "|" + ELEM_PLATE;          // 0.1.17: the element plates''')

# ---------- the check= hooks
P.rep('''# 0.1.10: Zone top levels in Server Setup (value null = back to the default)''', '''# 0.1.17 (elem1): Mob elements + Element wheel in Server Setup (value null = back to the default)
M(mh, r"""
public static String checkElemMobs(String key, String value) {
  if (value == null) return null;
  return @PKG@.MobElem.err(value, @PKG@.MobCfg.ELEM_WHEEL);
}""")
M(mh, r"""
public static String checkWheel(String key, String value) {
  if (value == null) return null;
  if (@PKG@.MobElem.wheelOf(value) == null) return "Write the 5 elements once each with > between, like Earth>Thunder>Water>Fire>Air.";
  return null;
}""")
# 0.1.10: Zone top levels in Server Setup (value null = back to the default)''')

# ---------- the mob element hit (LevelDamage)
P.rep('''    if (!lvd && @PKG@.MobCfg.HIT_CAP <= 0) return;''', '''    if (!lvd && @PKG@.MobCfg.HIT_CAP <= 0 && !@PKG@.MobElem.ANY) return;          // 0.1.17: + an elemental mob's hit''')
P.rep('''      if (c1 < (double) a1) { @PKG@.MobCfg.hitNote(an.getRoleName(), i == null ? 0 : i.level, (double) a1, c1, vmax1); d.setAmount((float) c1); }
      return;''', '''      if (c1 < (double) a1) { @PKG@.MobCfg.hitNote(an.getRoleName(), i == null ? 0 : i.level, (double) a1, c1, vmax1); d.setAmount((float) c1); }
      double e1 = @PKG@.MobElem.cutHit(an.getRoleName(), vp.getUuid(), (double) d.getAmount());          // 0.1.17: element Defence on the element part
      if (e1 < (double) d.getAmount()) d.setAmount((float) e1);
      return;''')
P.rep('''      if (capped < amt) { @PKG@.MobCfg.hitNote(i.role, i.level, amt, capped, vmax); amt = capped; }
    }
    float out = (float) amt;''', '''      if (capped < amt) { @PKG@.MobCfg.hitNote(i.role, i.level, amt, capped, vmax); amt = capped; }
    }
    amt = @PKG@.MobElem.cutHit(i.role, vp.getUuid(), amt);          // 0.1.17 (elem1): element Defence on the element part of the hit
    float out = (float) amt;''')

# ---------- the plate
P.rep('''public static String plateText(int level, String name) {
  String f = @PKG@.MobCfg.FORMAT;
  if (f == null || f.indexOf("{level}") < 0) f = "[Lv {level}] {name}";
  String t = f.replace("{level}", String.valueOf(level)).replace("{name}", name == null ? "" : name).trim();
  if (!@PKG@.MobCfg.COLOR_ON) return t;
  return markup(t, hexFor(level), @PKG@.MobCfg.MARKUP);
}""")''', '''public static String plateText(int level, String name) {
  String f = @PKG@.MobCfg.FORMAT;
  if (f == null || f.indexOf("{level}") < 0) f = "[Lv {level}] {name}";
  String t = f.replace("{element}", "").replace("{level}", String.valueOf(level)).replace("{name}", name == null ? "" : name).trim();          // 0.1.17
  if (!@PKG@.MobCfg.COLOR_ON) return t;
  return markup(t, hexFor(level), @PKG@.MobCfg.MARKUP);
}""")
# 0.1.17 (elem1, spec 8): + the mob's OWN element - " - Fire" where the format holds {element}, else at the end (elem.plate on); with the trial
# colour markup an appended element part takes the element's colour
M(lv, r"""
public static String plateText(int level, String name, String role) {
  String el = @PKG@.MobCfg.ELEM_PLATE ? @PKG@.MobElem.word(role) : "";
  if (el.length() == 0) return plateText(level, name);
  String f = @PKG@.MobCfg.FORMAT;
  if (f == null || f.indexOf("{level}") < 0) f = "[Lv {level}] {name}";
  String part = " - " + el;
  boolean tok = f.indexOf("{element}") >= 0;
  String t = f.replace("{element}", part).replace("{level}", String.valueOf(level)).replace("{name}", name == null ? "" : name).trim();
  if (!@PKG@.MobCfg.COLOR_ON) return tok ? t : t + part;
  String m = markup(t, hexFor(level), @PKG@.MobCfg.MARKUP);
  return tok ? m : m + markup(part, @PKG@.MobElem.hex(role), @PKG@.MobCfg.MARKUP);
}""")''')
P.rep('''  String[] parts = f.replace("{name}", "{level}").split(java.util.regex.Pattern.quote("{level}"), -1);''',
      '''  String[] parts = f.replace("{name}", "{level}").replace("{element}", "{level}").split(java.util.regex.Pattern.quote("{level}"), -1);          // 0.1.17: + {element}''')
P.rep('''  else setPlate(h, st, r, plateText(level, name));''', '''  else setPlate(h, st, r, plateText(level, name, role));          // 0.1.17: + the element''')
P.rep('''      @PKG@.MobLevel.setPlate(null, st, r, @PKG@.MobLevel.plateText(((@PKG@.MobInfo) o).level, ((@PKG@.MobInfo) o).name));''',
      '''      @PKG@.MobLevel.setPlate(null, st, r, @PKG@.MobLevel.plateText(((@PKG@.MobInfo) o).level, ((@PKG@.MobInfo) o).name, ((@PKG@.MobInfo) o).role));          // 0.1.17''')

# ---------- setup / shutdown / ready line
P.rep('''  @PKG@.MobLevel.bridge().put("mob:fn:boss", new @PKG@.MobBossFn());   // 0.1.10: boss / zone / credited players (SkyyGear's Mythic bags)''',
      '''  @PKG@.MobLevel.bridge().put("mob:fn:boss", new @PKG@.MobBossFn());   // 0.1.10: boss / zone / credited players (SkyyGear's Mythic bags)
  @PKG@.MobLevel.bridge().put("mob:fn:elem", new @PKG@.MobElemFn());   // 0.1.17 (elem1): Weak / Resist / boss % of a role for an element (SkyyGear, SkyyClasses)
  @PKG@.MobLevel.bridge().put("mob:fn:elemOf", new @PKG@.MobElemOfFn());   // 0.1.17: a role's own element
  @PKG@.MobElem.derive();   // 0.1.17: mob:elem:wheel + mob:elem:numbers''')
P.rep('''+ @PKG@.MobCfg.bossText() + "; " + @PKG@.MobSpoils.text()''', '''+ @PKG@.MobCfg.bossText() + "; elements: " + @PKG@.MobElem.text() + "; " + @PKG@.MobSpoils.text()''')
P.rep('''  try { @PKG@.MobLevel.bridge().remove("mob:fn:boss"); } catch (Throwable t) { }   // 0.1.10''',
      '''  try { @PKG@.MobLevel.bridge().remove("mob:fn:boss"); } catch (Throwable t) { }   // 0.1.10
  try { java.util.Map eb = @PKG@.MobLevel.bridge(); eb.remove("mob:fn:elem"); eb.remove("mob:fn:elemOf"); eb.remove("mob:elem:wheel"); eb.remove("mob:elem:numbers"); eb.remove("mob:elem:custom"); } catch (Throwable t) { }   // 0.1.17''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 and P.s.count("pool.makeClass(") == CLS0 + 3, "0.1.17 adds 3 classes, no command / system"
_i = P.s.index
assert _i("public static boolean isBoss(String role)") < _i("public static int mod(String role, int e)") < _i("public static void elemEdit(String key)") \
    < _i("public static synchronized void apply(java.util.Properties c, java.util.Properties b)") < _i("public static String plateText(int level, String name, String role)")
P.finish()
