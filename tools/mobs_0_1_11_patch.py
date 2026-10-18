"""Derive SkyyMobs/build_skyymobs_0.1.11.py from the GENERATED 0.1.10 (build_skyymobs_0.1.10.py = the tools/deploy_set.py SET pin, made by
tools/mobs_0_1_10_patch.py). Every anchor is asserted; at the end every change is undone on a copy and compared with 0.1.10; line endings kept.
Run:  python tools/mobs_0_1_11_patch.py [--out <path>]   then   python SkyyMobs/build_skyymobs_0.1.11.py   then
      python SkyyMobs/test_skyymobs_0.1.11.py      (never --deploy; --static = the text checks only, no jars needed)
Edit THIS file, never the generated script. --out writes the result somewhere else (the harness's determinism check).

0.1.11 (2026-10-18) = ONE HIT AT MOST ON BY DEFAULT + NO MYTHIC FROM ELITES (research/Beta-Bugs-Triage-2026-10-17.md bug 3, round R2).
  Bug 3 (Skyy's beta video): "golem one-shots with no attack animation". The live config has strength.hitCap=0 (off), so nothing stops one
  big (or several queued) levelled hits from killing a full-HP player. Skyy's rule (PROJECT-RULES 4 + docs/answered): Mythic only from FULL
  bosses - elite skeletons are not full bosses.
  1. ONE HIT AT MOST (strength.hitCap): default 0 (off) -> 35 (% of the victim's max Health, before armour; the triage's value: a full-HP
     player survives at least two hits of any levelled mob, three before armour rounding; vanilla Golem_Crystal hits at Lv 10 are ~20 =
     20 % of a 100-HP player, so normal fights are not clipped). The cap is SHAPE-INDEPENDENT: LevelDamage applies it after the level
     multiplier for Level curve AND Per level (0.1.4 already did - the missing cap on the curve path was the MULTIPLIER cap dmgCap, which
     stays Per level only by design; the hit cap is the safety on both). Now one pure method MobCfg.capHit(amount, victim max) (the harness
     executes it on both shapes) + MobCfg.hitNote: one INFO line at most every 5 s when the cap clips a hit ("[SkyyMobs] one hit at most:
     <role> Lv <n> hit <raw> -> <capped> (35% of max Health <max>)") - the triage's debug line, for the in-game test.
     A config without the line = 35 (code default); the fresh default file carries strength.hitCap=35. MobMig14 (0.1.4, for pre-0.1.4
     files) still adds strength.hitCap=0 byte for byte - MobMig11 below then moves it like any untouched line.
  2. BOSS ROLES (bosses.roles, 0.1.10's mob:fn:boss for SkyyGear's Mythic bags): default "Goblin_Duke*, Trork_Chieftain, Dragon_*,
     Skeleton_Elite*, *_Boss*" -> "Goblin_Duke*, Trork_Chieftain, Dragon_*, *_Boss*" (elites give no Mythic bag). Elite skeletons stay in
     levels.exclude (unchanged - they still get no level, like every built-in boss / elite).
  3. MIGRATION MobMig11 (PROJECT-RULES 4; MobMig 0.1.1's reviewed machinery, its helpers reused: MobMig.sameAfter / fileIdx / mgKit /
     mgSaved): ONCE on an EXISTING config.properties (setup, after MobMig14, before MobCfg.load). A key whose LAST entry is a one-line entry
     holding exactly the old default (strength.hitCap=0, bosses.roles=<the 0.1.10 text>) -> the new default (value text only); an admin's
     own value kept (INFO line); no line = nothing (the new code default applies - Skyy's live file has no bosses.roles line); the marker
     line above the first such entry (+ its comment run); verified config-history copy first; one config-changes.log line per change (Undo
     in Server Setup -> Changes); bytes + line endings kept. A fresh file carries the marker (never migrated).
SAVED DATA: none besides that one config update. No new command, no new system, no new bridge key (asserted below).
ROLLBACK 0.1.11 -> 0.1.10: safe. The migrated lines stay (0.1.10 reads hitCap 35 / the shorter Boss roles as admin values); Undo them in
Server Setup -> Changes first if the old behaviour is wanted back.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.10.py")
DST = os.path.join(ROOT, "SkyyMobs", "build_skyymobs_0.1.11.py")
if "--out" in sys.argv:
    DST = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.1.10"' in s and s.startswith('"""SkyyMobs 0.1.10 - build script'), "build_skyymobs_0.1.10.py is not the SET pin 0.1.10"
assert "MobMig11" not in s and "capHit" not in s and "HITCAP_DEF" not in s
SYS0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
PUT0 = s.count("bridge().put(")
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.11 (2026-10-18)"):].rstrip() + "\n\n"

# ================================================================================================================ header + version
rep('''"""SkyyMobs 0.1.10 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_10_patch.py from the SET pin 0.1.9 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.10.py -> SkyyMobs/SkyyMobs-0.1.10.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.10.py   (--static: the text checks only)

''', '''"""SkyyMobs 0.1.11 - build script (javassist via jpype). GENERATED by tools/mobs_0_1_11_patch.py from the SET pin 0.1.10 - edit the
patch, never this file. Run: python SkyyMobs/build_skyymobs_0.1.11.py -> SkyyMobs/SkyyMobs-0.1.11.jar (never --deploy).
Test: python SkyyMobs/test_skyymobs_0.1.11.py   (--static: the text checks only)

''' + NOTE + '''0.1.10 (the base, everything below is still true unless 0.1.11 above says otherwise):
''')
rep('VERSION = "0.1.10"', 'VERSION = "0.1.11"')

# ================================================================================================================ the class list
rep('''bfn = pool.makeClass(PKG + ".MobBossFn")   # 0.1.10: mob:fn:boss (who is a boss, which zone, who hurt it - SkyyGear's Mythic bags)
pl = pool.makeClass(PKG + ".SkyyMobsPlugin", pool.get(G["JP"]))
ALL = [lg, gb, bd, mi, cfg, lv, hk, dm, dmu, fn, ps, sc, pt, rf, mh, mc, mm, gp, gd, gdu, ifn, m14, lat, mcr, crs, cfn, sfn, bfn]
''', '''bfn = pool.makeClass(PKG + ".MobBossFn")   # 0.1.10: mob:fn:boss (who is a boss, which zone, who hurt it - SkyyGear's Mythic bags)
m11 = pool.makeClass(PKG + ".MobMig11")    # 0.1.11: the one-time hit cap 0 -> 35 + Boss roles without elites update of config.properties
pl = pool.makeClass(PKG + ".SkyyMobsPlugin", pool.get(G["JP"]))
ALL = [lg, gb, bd, mi, cfg, lv, hk, dm, dmu, fn, ps, sc, pt, rf, mh, mc, mm, gp, gd, gdu, ifn, m14, lat, mcr, crs, cfn, sfn, bfn, m11]
''')

# ================================================================================================================ 1. the hit cap default
rep('''HITCAP_DOC = "# One hit at most: a levelled mob's hit on a player (before armour) is at most this % of the player's max Health; 0 is off."
''', '''HITCAP_DOC = "# One hit at most: a levelled mob's hit on a player (before armour) is at most this % of the player's max Health; 0 is off."
# 0.1.11 (triage bug 3, golem one-shots): One hit at most is ON by default - 35 % of the victim's max Health (a full-HP player survives
# two hits of any levelled mob). MobMig14 (pre-0.1.4 files) still adds the 0.1.4 line strength.hitCap=0; MobMig11 moves it like any other.
HITCAP_DEF = 35
HITCAP_OLD = 0
''')
rep('''def mg14_groups(shape):
    """(file key or family prefix ending '.', [lines]) in file order: the block the update (and the fresh default file) puts right after
    the last strength.* entry. A group is left out when its key (any case) / any key of its family is already in the file."""
    G = [("strength.shape", [SHAPE_DOC, "strength.shape=" + shape]),
         ("strength.dmgFloor", [DMGFLOOR_DOC, "strength.dmgFloor=0"]),
         ("strength.hitCap", [HITCAP_DOC, "strength.hitCap=0"])]
''', '''def mg14_groups(shape, hitcap=0):
    """(file key or family prefix ending '.', [lines]) in file order: the block the update (and the fresh default file) puts right after
    the last strength.* entry. A group is left out when its key (any case) / any key of its family is already in the file.
    0.1.11: hitcap = the strength.hitCap value written (MobMig14 keeps 0.1.4's 0; the fresh default file gets HITCAP_DEF)."""
    G = [("strength.shape", [SHAPE_DOC, "strength.shape=" + shape]),
         ("strength.dmgFloor", [DMGFLOOR_DOC, "strength.dmgFloor=0"]),
         ("strength.hitCap", [HITCAP_DOC, "strength.hitCap=%d" % hitcap])]
''')
rep('''    MG14_MARK] + [ln for _key, _lines in mg14_groups(SHAPE_DEF) for ln in _lines] + [''',
    '''    MG14_MARK] + [ln for _key, _lines in mg14_groups(SHAPE_DEF, HITCAP_DEF) for ln in _lines] + [''')
rep('''"public static volatile int DMG_FLOOR = 0;", "public static volatile int HIT_CAP = 0;",''',
    '''"public static volatile int DMG_FLOOR = 0;", "public static volatile int HIT_CAP = %d;" % HITCAP_DEF,   # 0.1.11: 0 -> 35''')
rep('''  HIT_CAP = intOf(c.getProperty("strength.hitCap"), 0, 0, 100);''',
    '''  HIT_CAP = intOf(c.getProperty("strength.hitCap"), @HITCAP@, 0, 100);   // 0.1.11: a file without the line = 35 (was 0)''')
rep('''    # 0.1.4 (spec 1.6, both default off - Skyy 2026-10-05: no damage floor): players only, in LevelDamage''',
    '''    # 0.1.4 (spec 1.6, both default off - Skyy 2026-10-05: no damage floor): players only, in LevelDamage. 0.1.11: hitCap ON (35) by default''')
rep('''    ("strength.hitCap", "One hit at most", "strength", "int", "0", "0", "100", "", "%", "live,danger",''',
    '''    ("strength.hitCap", "One hit at most", "strength", "int", str(HITCAP_DEF), "0", "100", "", "%", "live,danger",''')
rep('''assert (T["STEPH"], T["STEPD"], T["HPCAP"], T["DMGCAP"]) == ("0.06", "0.03", "6.0", "3.5")
''', '''assert (T["STEPH"], T["STEPD"], T["HPCAP"], T["DMGCAP"]) == ("0.06", "0.03", "6.0", "3.5")
T["HITCAP"] = str(HITCAP_DEF)   # 0.1.11
assert T["HITCAP"] == "35"
''')
# the cap as one pure method (both strength shapes) + the throttled INFO line when it clips a hit
rep('''# 0.1.2: the floor factor max(1, floor / base) (1 when the floor is off or the base unknown) and the health amount = the 0.1.1 level
''', '''# 0.1.11: One hit at most (strength.hitCap) as one pure method - LevelDamage calls it after the level multiplier and the level gap, for
# BOTH strength shapes (Level curve and Per level): at most HIT_CAP % of the victim's max Health; 0 / an unknown max = no cap
F(cfg, "public static volatile long HIT_NOTE_AT = 0L;")
M(cfg, r"""
public static double capHit(double amt, float vmax) {
  int hc = HIT_CAP;
  if (hc <= 0 || !(vmax > 0.0f)) return amt;
  double cap = (double) hc / 100.0 * (double) vmax;
  return amt > cap ? cap : amt;
}""")
# 0.1.2: the floor factor max(1, floor / base) (1 when the floor is off or the base unknown) and the health amount = the 0.1.1 level
''')
rep('''    int hc = @PKG@.MobCfg.HIT_CAP;
    if (hc > 0) {
      @ESM@ vm = (@ESM@) buf.getComponent(vr, @ESM@.getComponentType());
      @ESV@ hv = vm == null ? null : vm.get(@DST@.getHealth());
      float vmax = hv == null ? 0.0f : hv.getMax();
      if (vmax > 0.0f) {
        double cap = (double) hc / 100.0 * (double) vmax;
        if (amt > cap) amt = cap;
      }
    }
''', '''    if (@PKG@.MobCfg.HIT_CAP > 0) {   // 0.1.11: MobCfg.capHit, both strength shapes; a clipped hit -> MobCfg.hitNote (INFO, 5 s apart)
      @ESM@ vm = (@ESM@) buf.getComponent(vr, @ESM@.getComponentType());
      @ESV@ hv = vm == null ? null : vm.get(@DST@.getHealth());
      float vmax = hv == null ? 0.0f : hv.getMax();
      double capped = @PKG@.MobCfg.capHit(amt, vmax);
      if (capped < amt) { @PKG@.MobCfg.hitNote(i.role, i.level, amt, capped, vmax); amt = capped; }
    }
''')

NUM2 = 'M(cfg, "public static String num2(double d) { String s = String.valueOf(Math.round(d * 100.0) / 100.0); return s.endsWith(\\".0\\") ? s.substring(0, s.length() - 2) : s; }")\n'
rep(NUM2, NUM2 + '''# 0.1.11: one INFO line at most every 5 s when the cap clips a hit (triage bug 3's debug line: role, level, raw, final, victim max Health)
M(cfg, r"""
public static void hitNote(String role, int level, double raw, double out, float vmax) {
  long now = System.currentTimeMillis();
  if (now - HIT_NOTE_AT < 5000L) return;
  HIT_NOTE_AT = now;
  @PKG@.MobLog.info("one hit at most: " + role + " Lv " + level + " hit " + num2(raw) + " -> " + num2(out) + " (" + HIT_CAP + "% of max Health " + num2((double) vmax) + ")");
}""")
''')

# ================================================================================================================ 2. Boss roles without elites
rep('''BOSS_ROLES_DEF = ", ".join(BOSSES + ["*_Boss*"])
assert BOSS_ROLES_DEF == "Goblin_Duke*, Trork_Chieftain, Dragon_*, Skeleton_Elite*, *_Boss*", BOSS_ROLES_DEF
''', '''BOSS_ROLES_010 = ", ".join(BOSSES + ["*_Boss*"])   # the 0.1.10 default (what MobMig11 moves)
assert BOSS_ROLES_010 == "Goblin_Duke*, Trork_Chieftain, Dragon_*, Skeleton_Elite*, *_Boss*", BOSS_ROLES_010
# 0.1.11: elites are no bosses (Skyy's rule: Mythic only from full bosses) - Skeleton_Elite* out of the Boss roles default
NOT_BOSSES = ["Skeleton_Elite*"]
BOSS_ROLES_DEF = ", ".join([b for b in BOSSES if b not in NOT_BOSSES] + ["*_Boss*"])
assert BOSS_ROLES_DEF == "Goblin_Duke*, Trork_Chieftain, Dragon_*, *_Boss*", BOSS_ROLES_DEF
''')
rep('''    assert not matches(BOSSES, _n) or matches(BOSS_PATS, _n), "0.1.10: Boss roles misses the built-in boss " + _n
''', '''    assert not matches(BOSSES, _n) or matches(BOSS_PATS, _n) or matches(NOT_BOSSES, _n), "0.1.10: Boss roles misses the built-in boss " + _n
    assert not (matches(NOT_BOSSES, _n) and matches(BOSS_PATS, _n)), "0.1.11: an elite would still count as a boss: " + _n
''')
rep('''assert not matches(BOSS_PATS, "Trork_Warrior") and not matches(BOSS_PATS, "Skeleton_Fighter") and not matches(BOSS_PATS, "Goblin_Scrapper")
''', '''assert not matches(BOSS_PATS, "Trork_Warrior") and not matches(BOSS_PATS, "Skeleton_Fighter") and not matches(BOSS_PATS, "Goblin_Scrapper")
assert not matches(BOSS_PATS, "Skeleton_Elite_Knight") and not matches(BOSS_PATS, "skeleton_elite")   # 0.1.11
''')

# ================================================================================================================ 3. MobMig11: marker + the fresh file
rep('''    "bosses.zoneTops=" + BOSS_TOPS_DEF,
]
CFG_TEXT = "\\n".join(CFG_LINES) + "\\n"
''', '''    "bosses.zoneTops=" + BOSS_TOPS_DEF,
    MG11_MARK,          # 0.1.11: the fresh file carries MobMig11's run-once marker (never migrated)
]
CFG_TEXT = "\\n".join(CFG_LINES) + "\\n"
assert CFG_TEXT.count(MG11_MARK_ID) == 1 and "\\nstrength.hitCap=%d\\n" % HITCAP_DEF in CFG_TEXT and "\\nbosses.roles=" + BOSS_ROLES_DEF + "\\n" in CFG_TEXT
''')
rep('''assert MG14_MARK_ID not in MG_MARK and MG_MARK_ID not in MG14_MARK
''', '''assert MG14_MARK_ID not in MG_MARK and MG_MARK_ID not in MG14_MARK
# 0.1.11: MobMig11's marker (fresh file + every updated file), History title, change-log name
MG11_MARK_ID = "SkyyMobs 0.1.11 hit cap update"
MG11_MARK = "# %s (2026-10-18): one hit at most %d%% of max Health by default; elite skeletons are no bosses (no Mythic bags)" % (MG11_MARK_ID, HITCAP_DEF)
MG11_WHO = "SkyyMobs 0.1.11"
MG11_WHAT = "before the 0.1.11 hit cap update"
for _t in (MG11_MARK,):
    assert _t.startswith("# ") and "=" not in _t and all(32 <= ord(_c) < 127 for _c in _t) and '"' not in _t and "@" not in _t, _t
assert MG11_MARK_ID not in MG_MARK + MG14_MARK and MG_MARK_ID not in MG11_MARK and MG14_MARK_ID not in MG11_MARK
''')

MIG11 = r'''# ---------------------------------------------------------------- MobMig11 (0.1.11): the one-time hit cap + Boss roles update of config.properties
# PROJECT-RULES 4: only a key whose LAST entry is a one-line entry holding exactly its old default moves (value text only: key, separator and
# CR stay); an admin's own value is kept (INFO); no line = nothing (the code default is 0.1.11's); a verified History copy first
# (MobMig.mgKit / mgSaved); one config-changes.log line per moved key (Undo in Server Setup -> Changes); the run-once marker on its own line
# above the first such entry and the comment lines directly on top of it (else above line 0); every other byte and the line endings kept.
# setup() runs it after MobMig14.run and BEFORE MobCfg.load. Plain java.* + the kit's classes: a bare JVM runs it on scratch copies.
MG11_ROWS = [("strength.hitCap", str(HITCAP_OLD), str(HITCAP_DEF), "one hit never takes more than %d%% of a player's max Health" % HITCAP_DEF),
             ("bosses.roles", BOSS_ROLES_010, BOSS_ROLES_DEF, "elite skeletons give no Mythic bags - Mythic only from full bosses")]
for _d in ("public static final String[] KEY = %s;" % _jarr([t[0] for t in MG11_ROWS]),
           "public static final String[] OLD = %s;" % _jarr([t[1] for t in MG11_ROWS]),
           "public static final String[] NEW = %s;" % _jarr([t[2] for t in MG11_ROWS]),
           "public static final String[] WHY = %s;" % _jarr([t[3] for t in MG11_ROWS]),
           "public static final String MARK = %s;" % jstr(MG11_MARK),
           "public static final String MARK_ID = %s;" % jstr(MG11_MARK_ID),
           "public static final String WHO = %s;" % jstr(MG11_WHO),
           "public static final String WHAT = %s;" % jstr(MG11_WHAT)):
    F(m11, _d)
M(m11, r"""
public static int idx(String k) {
  if (k == null) return -1;
  for (int i = 0; i < KEY.length; i++) if (KEY[i].equals(k)) return i;
  return -1;
}""")
# pure text step (ISO-8859-1 chars in and out; the kit's own parser). null = the marker is already in a comment line. Else
# { new text, "strength.hitCap 0 -> 35, ..." or "", String[] kept notes, String[] { key, old, new }* }. Never throws for any text.
M(m11, r"""
public static Object[] update(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int n = KEY.length;
  String[] eff = new String[n];
  boolean[] multi = new boolean[n];
  int first = -1;
  int above = -1;
  int run = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MARK_ID) >= 0) return null;
      if (s.trim().length() == 0) run = -1;
      else if (run < 0) run = k;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    int m = idx(@PKG@.CfgFile.key(s));
    if (m >= 0) {
      if (first < 0) { first = k; above = run >= 0 ? run : k; }
      eff[m] = @PKG@.CfgFile.value(l, k).trim();
      multi[m] = e > k;
    }
    run = -1;
    k = e + 1;
  }
  boolean[] mig = new boolean[n];
  StringBuilder chg = new StringBuilder();
  java.util.ArrayList kept = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < n; i++) {
    if (eff[i] == null) continue;
    if (!multi[i] && eff[i].equals(OLD[i])) {
      mig[i] = true;
      if (chg.length() > 0) chg.append(", ");
      chg.append(KEY[i]).append(' ').append(OLD[i]).append(" -> ").append(NEW[i]);
      rows.add(KEY[i]);
      rows.add(OLD[i]);
      rows.add(NEW[i]);
    } else if (multi[i] || !eff[i].equals(NEW[i])) {
      kept.add(KEY[i] + "=" + @PKG@.CfgRows.oneLine(eff[i]) + " kept (an admin's value) - the 0.1.11 default is " + NEW[i] + " (" + WHY[i] + "); Server Setup -> Mobs");
    }
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) {
      out.add(raw[k]);
      k++;
      continue;
    }
    int e2 = @PKG@.CfgFile.end(l, k);
    int m2 = idx(@PKG@.CfgFile.key(s2));
    if (m2 >= 0 && mig[m2] && e2 == k && @PKG@.CfgFile.value(l, k).trim().equals(OLD[m2])) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + NEW[m2] + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  int at = first >= 0 ? above : 0;
  String crA = at + 1 < raw.length ? (raw[at].endsWith("\r") ? "\r" : "") : cr;
  out.add(at, MARK + crA);
  StringBuilder sb = new StringBuilder(text.length() + MARK.length() + 256);
  for (int i = 0; i < out.size(); i++) {
    if (i > 0) sb.append('\n');
    sb.append((String) out.get(i));
  }
  return new Object[] { sb.toString(), chg.toString(), (String[]) kept.toArray(new String[0]), (String[]) rows.toArray(new String[0]) };
}""")
M(m11, r"""
public static String mgLog(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}""")
# setup(): returns the INFO lines joined by \n ("" = nothing done: no file - MobCfg.load writes the 0.1.11 default with the marker -,
# marker already there, or a failure: WARN, file untouched, retried at the next start)
M(m11, r"""
public static synchronized String run(java.nio.file.Path dir) {
  if (dir == null) return "";
  java.nio.file.Path f = dir.resolve("config.properties");
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    String[] rows = (String[]) r[3];
    if (!@PKG@.MobMig.sameAfter(old, data, rows)) {
      @PKG@.MobLog.warn("config.properties NOT updated for the 0.1.11 hit cap: the update would change more than its lines (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = @PKG@.MobMig.fileIdx();
    if (fi < 0) return "";
    @PKG@.MobMig.mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, WHAT);
    if (!@PKG@.MobMig.mgSaved(fi, old)) {
      @PKG@.MobLog.warn("config.properties NOT updated for the 0.1.11 hit cap: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(mgLog(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "config.properties updated for 0.1.11 (one hit at most on, elites are no bosses): " + chg + " (the old file is in config-history; Server Setup -> Changes can undo each line)";
    else msg = "config.properties: no hit cap / Boss roles line still had its old default - no value changed (0.1.11 update marker added; the old file is in config-history)";
    @PKG@.MobLog.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { @PKG@.MobLog.info(kept[i]); all.append('\n').append(kept[i]); }
    return all.toString();
  } catch (Throwable t) {
    @PKG@.MobLog.warn("could not update config.properties for the 0.1.11 hit cap (the file is used as it is): " + t);
    return "";
  }
}""")

'''
rep('''# ---------------------------------------------------------------- MobCmds: the command bodies (world thread: AbstractPlayerCommand runs there)
''', MIG11 + '''# ---------------------------------------------------------------- MobCmds: the command bodies (world thread: AbstractPlayerCommand runs there)
''')
rep('''  if (mg14.length() > 0) mg = mg.length() > 0 ? mg + "\\n" + mg14 : mg14;
''', '''  if (mg14.length() > 0) mg = mg.length() > 0 ? mg + "\\n" + mg14 : mg14;
  String mg11 = @PKG@.MobMig11.run(dir);   // 0.1.11: untouched hit cap 0 -> 35 + Boss roles without elites (once; History first; Undo in Server Setup)
  if (mg11.length() > 0) mg = mg.length() > 0 ? mg + "\\n" + mg11 : mg11;
''')

# ================================================================================================================ guards
assert s.count("registerSystem(") == SYS0, "no new system"
assert s.count("registerCommand(") == CMD0, "no new command"
assert s.count("bridge().put(") == PUT0, "no new bridge key"
_i = s.index
assert _i("HITCAP_DEF = 35") < _i("def mg14_groups(shape, hitcap=0):") < _i("assert MG14_MARK_ID not in MG_MARK") < _i('MG11_MARK_ID = "') \
    < _i("BOSS_ROLES_DEF = \", \".join([b for b") < _i("    MG11_MARK,          # 0.1.11") < _i("public static double capHit(") \
    < _i("public static void hitNote(") < _i("@PKG@.MobCfg.capHit(amt, vmax)") < _i("public static Object[] mgUpdate(String text)") \
    < _i("F(m14, _d)") < _i("F(m11, _d)") < _i("public void setup() {") < _i("@PKG@.MobMig11.run(dir)")
assert _i("MobMig14.run(dir)") < _i("MobMig11.run(dir)") < _i("@PKG@.MobCfg.load();\n  @PKG@.MobCfg.ON_HEALTH")
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.1.10 outside the recorded changes"
compile(s, DST, "exec")
with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(s.replace(LF, NL) if NL != LF else s)
print("wrote %s (%d lines; 0.1.10 had %d; %d changes)" % (os.path.relpath(DST, ROOT), s.count(LF), OLD.count(LF), len(CHANGES)))
