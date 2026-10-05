"""Derive SkyySkills/build_skyyskills_0.4.16.py from the LIVE generated SkyySkills/build_skyyskills_0.4.15.py (= the tools/deploy_set.py SET
pin; 0.4.15 came from 0.4.14 by tools/skills_0_4_15_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_15_patch.py: rep(old, new) with asserted single anchors, newline-agnostic;
0.4.15 stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_16_patch.py   then   python SkyySkills/build_skyyskills_0.4.16.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.16.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/sk0416/, deleted afterwards)

0.4.16 = MINING'S OWN LEVEL LIST + LEADERBOARDS SKIP DELETED PROFILES (Skyy LOCKED 2026-10-04 "for mining specifically id start a little
lower, and make it scale slower ... id rather players see the xp cost go up than their xp gain go down", OK'd 2026-10-05 "Yes, build it";
docs/answered/skills.md):

(1) PER-SKILL LEVEL LISTS. New Server Setup table levels.skill ("Own XP list per skill", Levels tab, right after the class rows; entries =
    a non-class skill name (Mining, Foraging, Farming, Acrobatics, Alchemy, Smithing, Cooking, Exploration - the legacy Combat slot and the
    class skills are refused: class skills have levels.class), value = the XP per level list (1-100 whole numbers above 0, the levels= rules;
    check= SkillLv.checkEntry), live + danger). A listed skill levels on ITS list (SkillDefs.cumOf -> OWN[slot]); every other non-class
    skill keeps the general levels= list, class skills keep levels.class. Default: Mining = 10 + 5L + 1.5L^2 XP per level rounded half up
    (L1 17, L5 73, L10 210, L20 710, L50 4,010, L100 15,510; Mining 10 after 955 XP, 20 after 5,560, 30 after 16,815, 50 after 71,275,
    100 after 533,800). MINING_PER below is the one Python list (the default file, the migration and the asserts all read it).
(2) MINING LEAVES THE GATHERING PACE BOOST: gather.boost.skills default Mining,Foraging,Farming -> Foraging,Farming (the default file, the
    row default, GatherPace.DEFAULT_SKILLS / its first values). XP per block never shrinks as Mining levels; only the cost rises.
(3) ONE-TIME CONFIG UPDATE (SkillLvMig, setup after ClassManaMig.run, BEFORE SkillCfg.load; PROJECT-RULES section 4): an existing
    xp.properties without the block marker gets (a) gather.boost.skills=Mining,Foraging,Farming -> Foraging,Farming ONLY when its last live
    line is a one-line entry holding exactly that old default (an admin's value is kept + one INFO line saying Mining still gets the boost),
    (b) the block (marker comment + levels.skill.Mining) appended after the last line in the file's own line ending - only the marker when
    the file already has a levels.skill. line. A Properties check (only those keys change), config-history copy first (HealMig.mgKit +
    CfgHist.snapshot + mgSaved), the kit's atomicWrite, one config-changes.log line per change (Undo: gather back to the old list; the
    Mining entry removed), one INFO line. The marker comment = run once (an admin who removes the Mining entry keeps it removed).
(4) LEVELS RECOMPUTED FROM SAVED XP, NORMAL REWARDS (OwnCurve, file Skyy_SkyySkills/own-levels.properties, the ClassCurve 0.4.12 pattern):
    XP is never changed - levels always come from saved XP. The first start where a skill has its own list scans every players/*.properties
    once (read-only) and records pending.<profile key>=slot:level before:level now for each profile whose level differs from its level on the
    general list (= what 0.4.15 showed); slots= remembers which skills were scanned (a list added later for another skill scans that skill
    once). The profile's first second online (Perks.tick) or its next XP gain in that skill (SkillXp.gain4) delivers it ONCE (PENDING.remove):
    UP = the normal level-up coins of every level above the PAID MARKER (SkillStore.payOwedK: coinsPerLevel x level, the marker only moves
    after SkyyCoins really paid - nothing is ever paid twice; unpaid levels stay owed for the normal late payout) + one chat line + the
    Overall level up; DOWN = one chat line only ("XP kept, nothing taken back; levels up to <marker> pay no coins again").
    LEVEL DROP (safest behaviour, nothing stored is changed): coins are never taken back; the paid marker stays where it is, so re-levelling
    pays nothing until the player passes the old highest paid level (then the normal coins per new level); XP and the paid marker on disk are
    untouched (a rollback to 0.4.15 restores the old levels exactly). Everything else reads the level live: perks (max Health / Stamina,
    double drops, Mining speed) and the Overall level shrink with it; SkyyTrees keeps every owned node (tree points come from the level - a
    lower level shows a negative balance: buying blocked, respec free, nothing refunded or lost - SkyyTrees 0.3.1's own rule); SkyyGear tool
    levels: a pickaxe above the new Mining level cannot break blocks until the level is back (the item is kept; no SkyyGear change here);
    Mining Dust comes from total XP and never changes. Nothing is unlocked by a Mining level inside SkyySkills (the crossbow unlock is
    Archery's). LIVE DATA (read 2026-10-05): every profile with Mining XP RISES (none drops) - see the harness's live table.
(5) LEADERBOARDS SKIP DELETED / ARCHIVED PROFILES (exactly SkyyCollections 0.2.6 CollTop): SkillTop.stateFn = skyy.bridge
    "profile:fn:state"; SkillTop.gone = true only on the exact answer "pending" (deleted, inside the undo window) or "archived"; no
    SkyyProfiles, null, any other answer or a throwing call = shown as before. Applied to every row (files on disk + profiles in memory)
    before sorting, so the rank and the "of N" count skip them too.
NOT in this build: the mob curve's SkyySkills part (0.4.17); a level floor (a drop is allowed by design - Skyy: "levels recomputed from saved
XP"); the Stats page does not name the list (the XP-to-next numbers come from it).
"""
import difflib
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.15.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.16.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.15"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.15"' in s and "derived from the generated 0.4.14 by tools/skills_0_4_15_patch.py" in s, "not the live generated 0.4.15"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
for _x in ('".SkillLv"', '".SkillLvMig"', '".OwnCurve"', "levels.skill", "MINING_PER", "SKL_L", "profile:fn:state", "own-levels.properties"):
    assert _x not in s, "0.4.15 already has " + _x
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
OLDS = []


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    i = s.index(old)
    j = s.find(LF, i + len(old))
    OLDS.append(s[s.rfind(LF, 0, i) + 1:(j if j >= 0 else len(s))])
    s = s.replace(old, new)


def after(anchor, add):
    rep(anchor, anchor + add)


def before(anchor, add):
    rep(anchor, add + anchor)


def block(a, b):
    assert s.count(a) == 1 and s.count(b) == 1 and s.index(a) < s.index(b), (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


# the Mining list (Skyy 2026-10-04 / 05): 10 + 5L + 1.5L^2 rounded half up = (21 + 10L + 3L^2) // 2 in whole numbers
MINING_PER = [(21 + 10 * L + 3 * L * L) // 2 for L in range(1, 101)]
assert MINING_PER == [int(math.floor(10 + 5 * L + 1.5 * L * L + 0.5)) for L in range(1, 101)]
assert (MINING_PER[0], MINING_PER[4], MINING_PER[9], MINING_PER[19], MINING_PER[49], MINING_PER[99]) == (17, 73, 210, 710, 4010, 15510)
assert sum(MINING_PER[:10]) == 955 and sum(MINING_PER[:20]) == 5560 and len(MINING_PER) == 100

KEEP = [block("# >>> SPELL GEN", "# <<< SPELL GEN"),
        block("# ================= ManaRegen (0.4.12)", "# AcroSys: EntityTickingSystem on Player entities"),
        block("# ================= Xbow part 1 (0.4.5)", "# ================= ClassCurve (0.4.12)"),
        block("# ================= 0.4.2 FELLED TREES", "# FellCredit (spec 2.6)"),
        block("# ================= skill:fn:addxp (0.4)", "# ================= leaderboard ================="),
        block("# ================= OverallPage (0.4.6)", "# ================= 0.4.3 ADMIN CONFIG"),
        block("# ---- 0.4.5 Xbow part 2", "# ================= ManaRegen (0.4.12)"),
        block("# ================= CombatDmgSys (0.3)", "# ================= PlacedStore"),
        block("# ================= RollSys (0.4.14)", "# ================= CombatDmgSys (0.3)"),
        block("# ================= Sickle (0.4.14, research/Tool-Levels-Spec.md question 3)", "# ================= Brew.extraPotion (0.4)"),
        block("# ================= MobXp maths (0.4.14)", "# ================= PartyXp (0.4.2 stage 2"),
        block("# ================= SkillStore: per-player XP", "# ================= SkillClass (0.3)"),
        block("# ================= Overall (0.4.6)", "# ================= skill:fn:overall (0.4.6, spec 4.8)"),
        block("# ---- HealMig (0.4.11 point 5)", "# ---- DocMig (0.4.14, fix (5))"),
        block("# ================= ClassMana part 1 (0.4.15", "# ================= BridgeCfg (0.4)"),
        block("# ================= SkillKit (0.4.3)", "# ================= commands =================")]

# ---------------------------------------------------------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.15 - build script (derived from the generated 0.4.14 by tools/skills_0_4_15_patch.py - edit the patch, not this file;
0.4.14 was derived''', '''"""SkyySkills 0.4.16 - build script (derived from the generated 0.4.15 by tools/skills_0_4_16_patch.py - edit the patch, not this file;
0.4.15 was derived from the generated 0.4.14 by tools/skills_0_4_15_patch.py; 0.4.14 was derived''')
HEAD_0416 = '''0.4.16: MINING'S OWN LEVEL LIST + LEADERBOARDS SKIP DELETED PROFILES (Skyy LOCKED 2026-10-04, OK 2026-10-05; full notes in
  tools/skills_0_4_16_patch.py).
  PER-SKILL LISTS: config table levels.skill (Server Setup > Skills > Levels > "Own XP list per skill"): a listed non-class skill levels on
     its own XP-per-level list (SkillDefs.OWN / cumOf); default Mining = 10 + 5L + 1.5L^2 (Mining 10 at 955 XP, 20 at 5,560). Mining left
     the gathering pace boost (gather.boost.skills default Foraging,Farming). An existing xp.properties gets both ONCE (SkillLvMig: only a
     gather line still at the old default changes; History copy first, change-log lines with Undo, marker comment).
  LEVELS FROM SAVED XP: XP is never changed. OwnCurve (own-levels.properties) scans once per newly listed skill and tells each profile
     once: a higher level pays the normal level-up coins of every level above the paid marker (exactly once), a lower level takes nothing
     back and pays nothing again until the old paid marker is passed.
  LEADERBOARDS: deleted (pending) and archived profiles (SkyyProfiles profile:fn:state) are left out, like SkyyCollections 0.2.6.
  CHECKED in a bare JVM (SkyySkills/test_skyyskills_0.4.16.py, -Xverify:all, scratch under tools/dev/scratch deleted afterwards).
'''
before("0.4.15: MAX MANA PER CLASS LEVEL + THE STAFF HANDOVER (Skyy 2026-10-03; research/SkyyArmory-Spec.md section 15; full notes in\n", HEAD_0416)
rep('VERSION = "0.4.15"\n', 'VERSION = "0.4.16"\n')

# ---------------------------------------------------------------------------------------------------------------- default xp.properties
rep('N14_L.append("gather.boost.skills=Mining,Foraging,Farming")', 'N14_L.append("gather.boost.skills=Foraging,Farming")   # 0.4.16: Mining has its own level list')
SKL_PY = r'''# 0.4.16 (Skyy LOCKED 2026-10-04 / OK 2026-10-05): own XP-per-level lists per skill - ONE block at the end of a fresh file; SkillLvMig appends
# it ONCE to an existing file (only when no comment line holds SKL_MARK_ID). MINING_PER = 10 + 5L + 1.5L^2 rounded half up (one place).
import math as _m16
MINING_PER = [(21 + 10 * _L + 3 * _L * _L) // 2 for _L in range(1, 101)]
assert MINING_PER == [int(_m16.floor(10 + 5 * _L + 1.5 * _L * _L + 0.5)) for _L in range(1, 101)]
assert sum(MINING_PER[:10]) == 955 and sum(MINING_PER[:20]) == 5560 and MINING_PER[-1] == 15510
SKL_DEF = [("Mining", ",".join(str(_x) for _x in MINING_PER))]
SKL_MARK_ID = "Own level list per skill (SkyySkills 0.4.16)"
SKL_HEAD = []
SKL_HEAD.append("# ---------- " + SKL_MARK_ID + " ----------")
SKL_HEAD.append("# Comments must stay on their own lines.")
SKL_HEAD.append("# A skill listed here (one line per skill: levels.skill.<Skill>=<list>) levels on its OWN list instead of the levels list:")
SKL_HEAD.append("# the XP each level needs, level 1 first, comma separated; the number of entries is its max level (1 to 100). Class skills")
SKL_HEAD.append("# use levels.class. Saved XP never changes: a changed list moves levels - new levels pay the normal level-up coins once, a")
SKL_HEAD.append("# lower level takes nothing back. Skyy 2026-10-05: Mining = 10 + 5L + 1.5L^2 XP per level (Mining 10 after 955 XP, 20")
SKL_HEAD.append("# after 5560), and Mining left the gathering pace boost (gather.boost.skills) - the cost rises instead of the boost fading.")
SKL_L = list(SKL_HEAD)
for _sk, _sv in SKL_DEF:
    SKL_L.append("levels.skill.%s=%s" % (_sk, _sv))
L.append("")
L.extend(SKL_L)
SKL_DEFAULTS = "\n".join(SKL_L) + "\n"
SKL_HEAD_TEXT = "\n".join(SKL_HEAD) + "\n"
assert all(ord(ch) < 128 for ch in SKL_DEFAULTS) and '"' not in SKL_DEFAULTS and "\\" not in SKL_DEFAULTS
assert not any(_cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln) for _ln in SKL_L), "a comment looks like a template line"
SKL_KEYS = [_ln.split("=", 1)[0] for _ln in SKL_L if not _ln.startswith("#")]
assert SKL_KEYS == ["levels.skill.Mining"] and sum(1 for _ln in SKL_L if SKL_MARK_ID in _ln) == 1
SKL_LIT = json.dumps(SKL_DEFAULTS)
SKL_HEAD_LIT = json.dumps(SKL_HEAD_TEXT)
'''
after("CMAN_LIT = json.dumps(CMAN_DEFAULTS)\n", SKL_PY)

# ---------------------------------------------------------------------------------------------------------------- GatherPace defaults
rep('''gpc.addField(CtField.make('public static final String DEFAULT_SKILLS = "Mining,Foraging,Farming";', gpc))''',
    '''gpc.addField(CtField.make('public static final String DEFAULT_SKILLS = "Foraging,Farming";', gpc))   # 0.4.16: Mining has its own level list''')
rep('''for _d in ("public static volatile boolean[] SLOTS = new boolean[] { true, true, true };", 'public static volatile String TEXT = "Mining,Foraging,Farming";',''',
    '''for _d in ("public static volatile boolean[] SLOTS = new boolean[] { false, true, true };", 'public static volatile String TEXT = "Foraging,Farming";',''')

# ---------------------------------------------------------------------------------------------------------------- SkillDefs: own lists
rep('''# 0.4.12: THE per-slot lookup - the cumulative table a storage slot levels on (class slots: ECUM, every other slot: the general CUM)
defs.addMethod(CtNewMethod.make("""
public static long[] cumOf(int s) {
  return isClass(s) ? ECUM : CUM;
}""", defs))''', '''# 0.4.16: OWN = per storage slot its own CUMULATIVE table (long[]) or null = the general CUM; class slots are never set (they have ECUM).
# Replaced as a whole (volatile) by setOwn (SkillLv.read, under SkillCfg.load) - a reader sees the old or the new set, never a mix.
defs.addField(CtField.make("public static volatile Object[] OWN = new Object[%d];" % len(SLOT_NAMES), defs))
defs.addMethod(CtNewMethod.make("""
public static void setOwn(Object[] cums) {
  Object[] o = new Object[N];
  if (cums != null) for (int i = 0; i < N && i < cums.length; i++) if (cums[i] != null && !isClass(i)) o[i] = cums[i];
  OWN = o;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static long[] own(int s) {
  Object[] o = OWN;
  if (s < 0 || s >= o.length || o[s] == null) return null;
  return (long[]) o[s];
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static boolean hasOwn(int s) {
  return own(s) != null;
}""", defs))
# 0.4.12: THE per-slot lookup - the cumulative table a storage slot levels on (class slots: ECUM; 0.4.16: a slot with its own list: that
# list; every other slot: the general CUM)
defs.addMethod(CtNewMethod.make("""
public static long[] cumOf(int s) {
  if (isClass(s)) return ECUM;
  long[] c = own(s);
  return c != null ? c : CUM;
}""", defs))''')

# ---------------------------------------------------------------------------------------------------------------- SkillLv (config reader)
SKILLLV = r'''# ================= SkillLv (0.4.16): the levels.skill table - own XP-per-level lists per non-class skill (before SkillCfg.load) =================
# levels.skill.<Skill>=<list>: entry = a non-class skill (NAMES or LABELS, any case; the legacy Combat slot is refused), value = the levels=
# rules (1-100 whole numbers above 0, each at most 1e15). A bad line is left out (that skill keeps the general list) with one WARN per new
# problem text. read() hands SkillDefs ONE new set (setOwn).
slv.addField(CtField.make('public static final String PREFIX = "levels.skill.";', slv))
slv.addField(CtField.make('public static volatile String TEXT = "";', slv))
slv.addField(CtField.make('public static volatile String WARNED = "";', slv))
slv.addMethod(CtNewMethod.make(J14(r"""
public static int slotOf(String e) {
  if (e == null) return -1;
  String t = e.trim();
  if (t.length() == 0) return -1;
  for (int s = 0; s < @PKG@.SkillDefs.N; s++) {
    if (s == @PKG@.SkillDefs.COMBAT || @PKG@.SkillDefs.isClass(s)) continue;
    if (@PKG@.SkillDefs.NAMES[s].equalsIgnoreCase(t) || @PKG@.SkillDefs.LABELS[s].equalsIgnoreCase(t)) return s;
  }
  return -1;
}"""), slv))
slv.addMethod(CtNewMethod.make(J14(r"""
public static long[] parse(String v) {
  if (v == null) return null;
  String t = v.trim();
  if (t.length() == 0) return null;
  String[] ps = t.split(",");
  if (ps.length < 1 || ps.length > 100) return null;
  long[] r = new long[ps.length];
  for (int i = 0; i < ps.length; i++) {
    long x = 0L;
    try { x = Long.parseLong(ps[i].trim()); } catch (Throwable e) { return null; }
    if (x <= 0L || x > 1000000000000000L) return null;
    r[i] = x;
  }
  return r;
}"""), slv))
slv.addMethod(CtNewMethod.make(J14(r"""
public static long[] cum(long[] per) {
  long[] c = new long[per.length + 1];
  c[0] = 0L;
  for (int i = 0; i < per.length; i++) c[i + 1] = c[i] + per[i];
  return c;
}"""), slv))
# the table lines -> {Object[] cumulative tables by slot, String text, String problems}; keys sorted (of two spellings of one skill the first
# in sort order - capital letters first - wins, the other is reported)
slv.addMethod(CtNewMethod.make(J14(r"""
public static Object[] parseTable(java.util.Properties p) {
  Object[] o = new Object[@PKG@.SkillDefs.N];
  int[] len = new int[@PKG@.SkillDefs.N];
  StringBuilder bad = new StringBuilder();
  java.util.Iterator it = new java.util.TreeSet(p.stringPropertyNames()).iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith(PREFIX)) continue;
    String e = k.substring(PREFIX.length()).trim();
    String shown = e.length() > 40 ? e.substring(0, 40) + "..." : e;
    int s = slotOf(e);
    if (s < 0) { if (bad.length() > 0) bad.append("; "); bad.append(shown + " is not a skill that can have its own list (left out)"); continue; }
    if (o[s] != null) { if (bad.length() > 0) bad.append("; "); bad.append(@PKG@.SkillDefs.LABELS[s] + " is listed twice (" + shown + " left out)"); continue; }
    long[] per = parse(p.getProperty(k));
    if (per == null) { if (bad.length() > 0) bad.append("; "); bad.append(shown + ": not a list of 1 to 100 whole numbers above 0 (left out - the general list)"); continue; }
    o[s] = cum(per);
    len[s] = per.length;
  }
  StringBuilder sb = new StringBuilder();
  for (int s = 0; s < o.length; s++) {
    if (o[s] == null) continue;
    if (sb.length() > 0) sb.append(", ");
    sb.append(@PKG@.SkillDefs.LABELS[s]).append(" (").append(len[s]).append(" levels)");
  }
  return new Object[] { o, sb.toString(), bad.toString() };
}"""), slv))
slv.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  Object[] t = parseTable(p);
  @PKG@.SkillDefs.setOwn((Object[]) t[0]);
  TEXT = (String) t[1];
  String w = ((String) t[2]).length() > 0 ? "Own XP list per skill: " + (String) t[2] : "";
  if (w.length() > 0 && !w.equals(WARNED)) @PKG@.SkillCfg.warn(w);
  WARNED = w;
}"""), slv))
slv.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  return TEXT.length() > 0 ? TEXT : "none";
}"""), slv))
# check= hook of the table (key "levels.skill[<entry>]", value = the typed list or null for a removal; also run for hand-edited lines)
slv.addMethod(CtNewMethod.make(J14(r"""
public static String checkEntry(String key, String value) {
  if (value == null || key == null) return null;
  String e = key;
  int a = key.indexOf('[');
  int b = key.lastIndexOf(']');
  if (a >= 0 && b > a) e = key.substring(a + 1, b);
  if (slotOf(e) < 0) {
    if (e.length() > 40) e = e.substring(0, 40) + "...";
    return "Unknown skill " + e + " - use Mining, Foraging, Farming, Acrobatics, Alchemy, Smithing, Cooking or Exploration (class skills use the class list).";
  }
  if (parse(value) == null) return "Write 1 to 100 whole numbers above 0, separated by commas: the XP for level 1, level 2, ...";
  return null;
}"""), slv))

'''
before("# ================= BridgeCfg (0.4): bridge.* keys (skill:fn:addxp / skill:fn:craftxp) =================\n", SKILLLV)

# SkillCfg.load reads it right after the max Mana table (the tables are set under the same load); the load summary names it
rep('''    {PKG}.ClassMana.read(p);    // 0.4.15: max Mana per class level (the mana.classPerLevel table)
''', '''    {PKG}.ClassMana.read(p);    // 0.4.15: max Mana per class level (the mana.classPerLevel table)
    {PKG}.SkillLv.read(p);      // 0.4.16: own XP-per-level lists (the levels.skill table; Mining by default)
''')
rep('''", max Mana per class level " + {PKG}.ClassMana.text() + (bad > 0 ? ", " + bad + " bad line(s) skipped" : "");''',
    '''", max Mana per class level " + {PKG}.ClassMana.text() + ", own level lists " + {PKG}.SkillLv.text() + (bad > 0 ? ", " + bad + " bad line(s) skipped" : "");''')

# ---------------------------------------------------------------------------------------------------------------- OwnCurve (notice + rewards)
OWNCURVE = r'''# ================= OwnCurve (0.4.16): the one-time notice when a skill gets its own level list + the normal rewards of the levels it gave ======
# FILE = Skyy_SkyySkills/own-levels.properties (the ClassCurve 0.4.12 pattern). The first start where a skill has its own list (SkillDefs.hasOwn)
# and the file does not name it in slots= scans every players/*.properties once (read-only) for THAT skill and records
# pending.<profile key>=<slot>:<level on the general list>:<level on its own list> for each profile where the two differ (up or down);
# slots= then names it, so it is never scanned again (a later own list for another skill scans that one). No own list and no file = nothing
# written. Delivered ONCE per profile (PENDING.remove), on the world thread: a higher level pays the normal level-up coins of every level
# above the PAID MARKER (payOwedK - the marker only moves after SkyyCoins paid; nothing is ever paid twice), the Overall level up and ONE
# chat line; a lower level only the chat line (XP and the paid marker stay as they are - nothing is taken back, levels up to the marker pay
# no coins again).
own.addField(CtField.make("public static java.nio.file.Path FILE;", own))
own.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();", own))
own.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DONE = new java.util.concurrent.ConcurrentHashMap();", own))
own.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SAVE = new java.util.concurrent.ConcurrentHashMap();", own))
own.addField(CtField.make("public static volatile boolean READY = false;", own))
own.addField(CtField.make("public static volatile boolean DIRTY = false;", own))
own.addField(CtField.make("public static volatile String SCANNED = null;", own))
own.addField(CtField.make('public static volatile String SLOTS = "";', own))
own.addField(CtField.make('public static final String NAME = "own-levels.properties";', own))
own.addField(CtField.make('public static final String HEAD1 = "# SkyySkills own level lists (0.4.16, Skyy 2026-10-05) - written when a skill first gets its own level list; do not edit (deleted = the next start scans again: the notice again, the coins never twice)";', own))
own.addField(CtField.make('public static final String HEAD2 = "# pending.<profile key> = slot:level before:level now - told (and paid for new levels) the next time that profile plays; done.<profile key> = told; slots = the skills scanned";', own))
own.addMethod(CtNewMethod.make(J14(r"""
public static String stamp() {
  return new java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss").format(new java.util.Date());
}"""), own))
own.addMethod(CtNewMethod.make(J14(r"""
public static String one(Object v) {
  return String.valueOf(v).replace('\n', ' ').replace('\r', ' ');
}"""), own))
# one player file -> "slot:general:own,..." for every wanted slot whose level on its own list differs from its level on the general list
own.addMethod(CtNewMethod.make(J14(r"""
public static String moves(java.util.Properties p, boolean[] want) {
  StringBuilder sb = new StringBuilder();
  for (int s = 0; s < @PKG@.SkillDefs.N && s < want.length; s++) {
    if (!want[s]) continue;
    long x = 0L;
    try { x = Long.parseLong(String.valueOf(p.getProperty(@PKG@.SkillDefs.NAMES[s], "0")).trim()); } catch (Throwable t) { x = 0L; }
    if (x <= 0L) continue;
    int old = @PKG@.SkillDefs.generalLevel(x);
    int nw = @PKG@.SkillDefs.levelOf(s, x);
    if (nw == old) continue;
    if (sb.length() > 0) sb.append(',');
    sb.append(s).append(':').append(old).append(':').append(nw);
  }
  return sb.toString();
}"""), own))
own.addMethod(CtNewMethod.make(J14(r"""
public static synchronized boolean write() {
  DIRTY = false;
  try {
    StringBuilder sb = new StringBuilder();
    sb.append(HEAD1).append('\n').append(HEAD2).append('\n');
    sb.append("scanned=").append(one(SCANNED == null ? "" : SCANNED)).append('\n');
    sb.append("slots=").append(one(SLOTS)).append('\n');
    java.util.Iterator it = new java.util.TreeMap(PENDING).entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      sb.append("pending.").append(e.getKey()).append('=').append(one(e.getValue())).append('\n');
    }
    it = new java.util.TreeMap(DONE).entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      sb.append("done.").append(e.getKey()).append('=').append(one(e.getValue())).append('\n');
    }
    java.nio.file.Path tmp = FILE.resolveSibling(NAME + ".tmp");
    java.nio.file.Files.write(tmp, sb.toString().getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
    @PKG@.SkillStore.moveRetry(tmp, FILE);
    return true;
  } catch (Throwable t) {
    DIRTY = true;
    @PKG@.SkillCfg.warn("could not write " + NAME + " (retried): " + t);
    return false;
  }
}"""), own))
# setup(), right after SkillCfg.load (the lists are loaded) and ClassCurve.start, before any player joins. Returns the INFO text ("" = none).
own.addMethod(CtNewMethod.make(J14(r"""
public static synchronized String start(java.nio.file.Path base) {
  PENDING.clear();
  DONE.clear();
  SAVE.clear();
  READY = false;
  DIRTY = false;
  SCANNED = null;
  SLOTS = "";
  if (base == null) return "";
  FILE = base.resolve(NAME);
  try {
    boolean[] want = new boolean[@PKG@.SkillDefs.N];
    for (int s = 0; s < want.length; s++) want[s] = @PKG@.SkillDefs.hasOwn(s);
    boolean had = java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0]);
    if (had) {
      java.util.Properties p = @PKG@.SkillStore.readLocked(FILE);
      java.util.Iterator it = p.stringPropertyNames().iterator();
      while (it.hasNext()) {
        String k = (String) it.next();
        String v = p.getProperty(k);
        if (k.startsWith("pending.") && k.length() > 8) PENDING.put(k.substring(8), v);
        else if (k.startsWith("done.") && k.length() > 5) DONE.put(k.substring(5), v);
      }
      SCANNED = p.getProperty("scanned");
      if (SCANNED == null || SCANNED.trim().length() == 0) {
        PENDING.clear();
        @PKG@.SkillCfg.warn(NAME + " has no scanned= line - nobody is told about own level lists (delete the file to scan again)");
        return "";
      }
      SLOTS = String.valueOf(p.getProperty("slots", "")).trim();
      String[] ss = SLOTS.split(",");
      for (int i = 0; i < ss.length; i++) {
        String t = ss[i].trim();
        for (int s = 0; s < want.length; s++) if (t.length() > 0 && @PKG@.SkillDefs.NAMES[s].equalsIgnoreCase(t)) want[s] = false;
      }
    }
    StringBuilder names = new StringBuilder();
    for (int s = 0; s < want.length; s++) if (want[s]) { if (names.length() > 0) names.append(','); names.append(@PKG@.SkillDefs.NAMES[s]); }
    if (names.length() == 0) {
      if (!had) return "";
      READY = true;
      return PENDING.isEmpty() ? "" : "own level lists: " + PENDING.size() + " profile(s) still to be told";
    }
    int files = 0;
    int bad = 0;
    int moved = 0;
    java.io.File[] fs = null;
    if (@PKG@.SkillStore.DIR != null) fs = @PKG@.SkillStore.DIR.toFile().listFiles();
    if (fs != null) for (int i = 0; i < fs.length; i++) {
      String fn = fs[i].getName();
      if (!fn.endsWith(".properties") || !fs[i].isFile()) continue;
      String k = fn.substring(0, fn.length() - 11);
      try {
        java.util.Properties p = @PKG@.SkillStore.readLocked(fs[i].toPath());
        files++;
        String r = moves(p, want);
        if (r.length() > 0) {
          Object e = PENDING.get(k);
          PENDING.put(k, e instanceof String && ((String) e).length() > 0 ? ((String) e) + "," + r : r);
          moved++;
        }
      } catch (Throwable t) {
        bad++;
        @PKG@.SkillCfg.warn("own level lists: could not read " + fn + " (" + t + ") - that profile is not told");
      }
    }
    SLOTS = SLOTS.length() > 0 ? SLOTS + "," + names.toString() : names.toString();
    SCANNED = stamp() + " " + files + " profile file(s) for " + names.toString() + (bad > 0 ? ", " + bad + " unreadable" : "");
    if (!write()) {
      PENDING.clear();
      DIRTY = false;
      @PKG@.SkillCfg.warn("own level lists: " + NAME + " could not be written - nobody is told this run; the next start scans again");
      return "";
    }
    READY = true;
    String msg = "own level lists (" + names.toString() + "): " + files + " profile file(s) scanned, " + moved + " with a different level now - each is told once the next time it plays (new levels pay the normal level-up coins once; a lower level takes nothing back)";
    @PKG@.SkillCfg.info(msg);
    return msg;
  } catch (Throwable t) {
    READY = false;
    DIRTY = false;
    @PKG@.SkillCfg.warn("own level lists: start failed (nobody is told this run): " + t);
    return "";
  }
}"""), own))
own.addMethod(CtNewMethod.make(J14(r"""
public static void deliver(@PR@ pr, java.util.UUID u, String k, String e) {
  try {
    long[] d = @PKG@.SkillStore.dataK(k, u);
    String[] parts = e.split(",");
    int[] sl = new int[parts.length];
    int[] was = new int[parts.length];
    int[] now = new int[parts.length];
    int n = 0;
    StringBuilder lines = new StringBuilder();
    StringBuilder sum = new StringBuilder();
    long coins = 0L;
    long first = -1L;
    long last = -1L;
    int ups = 0;
    for (int i = 0; i < parts.length; i++) {
      String[] f = parts[i].trim().split(":");
      if (f.length < 3) continue;
      int s = -1;
      int old = 0;
      try { s = Integer.parseInt(f[0].trim()); old = Integer.parseInt(f[1].trim()); } catch (Throwable t) { s = -1; }
      if (s < 0 || s >= @PKG@.SkillDefs.N || @PKG@.SkillDefs.isClass(s)) continue;
      int lv = @PKG@.SkillDefs.levelOf(s, @PKG@.SkillStore.rd(d, s));
      if (lv == old) continue;
      if (lines.length() > 0) lines.append("; ");
      lines.append(@PKG@.SkillDefs.LABELS[s]).append(" is now level ").append(lv).append(" (was ").append(old).append(")");
      if (lv > old) {
        ups++;
        long[] paid = null;
        if (@PKG@.SkillStore.owesK(k, u, s)) paid = @PKG@.SkillStore.payOwedK(k, u, s);
        if (paid != null) {
          // review F1: the new paid marker reaches disk NOW (the save flushDirty does, here on the world thread right after coins:fn:add),
          // so a crash before the next 10 s flush cannot pay the same burst again; a failed save stays dirty and is retried by the flush
          if (!@PKG@.SkillStore.save(k)) @PKG@.SkillStore.DIRTY.put(k, Boolean.TRUE);
          coins += paid[2];
          if (first < 0L || paid[0] < first) first = paid[0];
          if (paid[1] > last) last = paid[1];
        }
      } else {
        long pm = @PKG@.SkillStore.rd(d, @PKG@.SkillDefs.N + s);
        lines.append(" - your XP is kept and nothing is taken back");
        if (pm > (long) lv) lines.append(pm > (long) lv + 1L ? "; levels " + (lv + 1) + " to " + pm + " were paid already and pay no coins again" : "; level " + pm + " was paid already and pays no coins again");
      }
      if (sum.length() > 0) sum.append(", ");
      sum.append(@PKG@.SkillDefs.NAMES[s]).append(' ').append(old).append(" -> ").append(lv);
      sl[n] = s;
      was[n] = old;
      now[n] = lv;
      n++;
    }
    if (n == 0) {
      DONE.put(k, stamp() + " nothing to tell (no level differs any more)");
      DIRTY = true;
      return;
    }
    String c = "";
    if (coins > 0L) c = ups == 1 ? " - +" + @PKG@.SkillDefs.fmt(coins) + " coins for " + (first == last ? "level " + first : "levels " + first + " to " + last) : " - +" + @PKG@.SkillDefs.fmt(coins) + " coins for the new levels";
    pr.sendMessage(@MSG@.raw("[Skills] Skill level list updated: " + lines.toString() + c).color("#ffc800"));
    for (int i = 0; i < n; i++) if (now[i] > was[i]) @PKG@.Overall.levelUp(pr, u, sl[i], (long) was[i], (long) now[i]);
    @PKG@.SkillStore.publish(u);
    @PKG@.SkillStore.DIRTY.put(k, Boolean.TRUE);
    SAVE.put(k, Boolean.TRUE);
    DONE.put(k, stamp() + " " + sum.toString() + (coins > 0L ? " +" + coins + " coins" : ""));
    DIRTY = true;
    @PKG@.SkillCfg.info("own level lists: told " + k + " - " + sum.toString() + (coins > 0L ? ", paid " + coins + " coins" : ""));
  } catch (Throwable t) {
    DONE.put(k, stamp() + " failed: " + t);
    DIRTY = true;
    @PKG@.SkillCfg.warn("own level list notice failed for " + k + ": " + t);
  }
}"""), own))
# world thread (Perks.tick every second; SkillXp.gain4 before an award in a skill with its own list): nothing pending -> return at once;
# waits while profile:busy (Xbow.busy) and the session hold (Overall.hold), like ClassCurve.tick
own.addMethod(CtNewMethod.make(J14(r"""
public static void tick(@PR@ pr, java.util.UUID u) {
  if (!READY || PENDING.isEmpty() || pr == null || u == null) return;
  String k = @PKG@.SkillStore.pkey(u);
  Object e = PENDING.get(k);
  if (!(e instanceof String)) return;
  if (@PKG@.Xbow.busy(u)) return;
  if (@PKG@.Overall.hold(u, pr, System.currentTimeMillis())) return;
  if (PENDING.remove(k) == null) return;
  deliver(pr, u, k, (String) e);
}"""), own))
own.addMethod(CtNewMethod.make(J14(r"""
public static void flush() {
  if (!READY || !DIRTY) return;
  java.util.Iterator it = new java.util.ArrayList(SAVE.keySet()).iterator();
  boolean ok = true;
  while (it.hasNext()) {
    String k = (String) it.next();
    SAVE.remove(k);
    if (!@PKG@.SkillStore.save(k)) { SAVE.put(k, Boolean.TRUE); ok = false; }
  }
  if (ok) write();
}"""), own))

'''
before("# ================= GatherPace.apply (0.4.14): earned gathering XP x the pace multiplier of the skill's CURRENT level (world thread: SkillXp.gain4's\n", OWNCURVE)
rep('''  if ({PKG}.SkillDefs.isClass(skill)) {PKG}.ClassCurve.tick(pr, u);   // 0.4.12: a pending class skill curve notice comes first (once)
''', '''  if ({PKG}.SkillDefs.isClass(skill)) {PKG}.ClassCurve.tick(pr, u);   // 0.4.12: a pending class skill curve notice comes first (once)
  else if ({PKG}.SkillDefs.hasOwn(skill)) {PKG}.OwnCurve.tick(pr, u);   // 0.4.16: a pending own level list notice comes first (once)
''')
rep('''    {PKG}.ClassCurve.tick(pr, u);   // 0.4.12: the one-time class skill curve notice + its level-up rewards (only while one is pending)
''', '''    {PKG}.ClassCurve.tick(pr, u);   // 0.4.12: the one-time class skill curve notice + its level-up rewards (only while one is pending)
    {PKG}.OwnCurve.tick(pr, u);     // 0.4.16: the one-time own level list notice + the rewards of new levels (only while one is pending)
''')
rep('''  try {{ {PKG}.ClassCurve.flush(); }} catch (Throwable t) {{ }}   // 0.4.12: the class skill curve record (only after a notice was told)
''', '''  try {{ {PKG}.ClassCurve.flush(); }} catch (Throwable t) {{ }}   // 0.4.12: the class skill curve record (only after a notice was told)
  try {{ {PKG}.OwnCurve.flush(); }} catch (Throwable t) {{ }}     // 0.4.16: the own level list record (only after a notice was told)
''')
rep('''  try {{ {PKG}.ClassCurve.flush(); }} catch (Throwable t) {{ }}   // 0.4.12
''', '''  try {{ {PKG}.ClassCurve.flush(); }} catch (Throwable t) {{ }}   // 0.4.12
  try {{ {PKG}.OwnCurve.flush(); }} catch (Throwable t) {{ }}     // 0.4.16
''')

# ---------------------------------------------------------------------------------------------------------------- leaderboards
before('''# rows: Object[]{name, Long xp, profile key (0.3.2; = uuidString for profile 1)}, sorted, all profiles on disk + in memory; cached 30s
''', '''# 0.4.16: SkyyProfiles' profile:fn:state (tools/PROFILES-CONTRACT.md) - the bridge Function, or null when SkyyProfiles is missing
top.addMethod(CtNewMethod.make(J14(r"""
public static java.util.function.Function stateFn() {
  try {
    Object f = @PKG@.SkillStore.bridge().get("profile:fn:state");
    if (f instanceof java.util.function.Function) return (java.util.function.Function) f;
  } catch (Throwable t) { }
  return null;
}"""), top))
# 0.4.16 (= SkyyCollections 0.2.6 CollTop.gone): a deleted (pending: inside the undo window) or archived profile is left out of the lists;
# anything else (no SkyyProfiles, active / inactive, null, another answer, a throwing call) is shown - 0.4.15's list
top.addMethod(CtNewMethod.make(J14(r"""
public static boolean gone(java.util.function.Function sf, String key) {
  if (sf == null || key == null) return false;
  try {
    Object r = sf.apply(key);
    return "pending".equals(r) || "archived".equals(r);
  } catch (Throwable t) { return false; }
}"""), top))
''')
rep('''  java.util.ArrayList rows = new java.util.ArrayList(m.values());
  java.util.Collections.sort(rows, new {PKG}.TopCmp());''', '''  java.util.ArrayList rows = new java.util.ArrayList();
  java.util.function.Function sf = stateFn();   // 0.4.16: deleted / archived profiles are left out (SkyyCollections 0.2.6)
  java.util.Iterator vi = m.values().iterator();
  while (vi.hasNext()) {{ Object[] row = (Object[]) vi.next(); if (!gone(sf, (String) row[2])) rows.add(row); }}
  java.util.Collections.sort(rows, new {PKG}.TopCmp());''')

# ---------------------------------------------------------------------------------------------------------------- SkillLvMig
SLMIG = r'''# ---- SkillLvMig (0.4.16): Mining's own level list + Mining out of the gathering pace reach an EXISTING xp.properties ONCE. setup() only,
# after ClassManaMig.run, BEFORE SkillCfg.load and CfgPub.start. Nothing to do = no file (load() writes the 0.4.16 default) or a comment line
# holding MARK_ID (done before). Else: (a) gather.boost.skills - when its LAST live line is a one-line entry holding exactly the old default
# Mining,Foraging,Farming, every one-line entry holding that text gets Foraging,Farming (value text only; key, separator, CR kept); an
# admin's value is kept (one INFO line when it still lists Mining); (b) the block (the marker + levels.skill.Mining) appended after the last
# line in the file's own line ending (only the marker when the file already has a levels.skill. line). A Properties check (only those keys
# change), config-history copy first (HealMig.mgKit + CfgHist.snapshot + mgSaved), the kit's atomicWrite, one config-changes.log line per
# change (Undo: the old gather list back / the Mining entry removed), one INFO line. A failure = WARN, file untouched, retried next start.
slm.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(SKL_MARK_ID), slm))
slm.addField(CtField.make("public static final String BLOCK = " + SKL_LIT + ";", slm))
slm.addField(CtField.make("public static final String HEAD = " + SKL_HEAD_LIT + ";", slm))
slm.addField(CtField.make("public static final String[] KEYS = %s;" % jarr([_k for _k, _v in SKL_DEF]), slm))
slm.addField(CtField.make("public static final String[] VALS = %s;" % jarr([_v for _k, _v in SKL_DEF]), slm))
slm.addField(CtField.make('public static final String GKEY = "gather.boost.skills";', slm))
slm.addField(CtField.make('public static final String GOLD = "Mining,Foraging,Farming";', slm))
slm.addField(CtField.make('public static final String GNEW = "Foraging,Farming";', slm))
slm.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.16";', slm))
slm.addMethod(CtNewMethod.make(J14(r"""
public static boolean hasTableKey(java.util.Properties p) {
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) if (((String) it.next()).startsWith(@PKG@.SkillLv.PREFIX)) return true;
  return false;
}"""), slm))
slm.addMethod(CtNewMethod.make(J14(r"""
public static boolean listsMining(String v) {
  if (v == null) return false;
  String[] ps = v.split(",");
  for (int i = 0; i < ps.length; i++) if (@PKG@.GatherPace.slotOf(ps[i]) == @PKG@.SkillDefs.MINING) return true;
  return false;
}"""), slm))
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser): null = nothing to do (the marker is in a comment line,
# or the text cannot be read as Properties); else { new text, String[] { key, old, new }* (the change-log rows), String kept note ("" = none),
# Boolean gather changed, Boolean block entries added }. Never throws for any text.
slm.addMethod(CtNewMethod.make(J14(r"""
public static Object[] plan(String text) {
  if (text == null) return null;
  java.util.Properties p = new java.util.Properties();
  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { return null; }
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  String eff = null;
  boolean multi = false;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    if (GKEY.equals(@PKG@.CfgFile.key(s))) { eff = @PKG@.CfgFile.value(l, k).trim(); multi = e > k; }
    k = e + 1;
  }
  boolean mig = eff != null && !multi && eff.equals(GOLD);
  String kept = "";
  if (eff != null && !mig && listsMining(eff)) kept = GKEY + "=" + @PKG@.CfgRows.oneLine(eff) + " kept (an admin's value) - Mining still gets the early gathering XP boost on top of its own level list; Skyy's 0.4.16 default is " + GNEW + " (Server Setup -> Skills -> Gathering -> Gathering pace skills)";
  StringBuilder sb = new StringBuilder(text.length() + BLOCK.length() + 64);
  k = 0;
  boolean firstOut = true;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    int e2 = @PKG@.CfgFile.isComment(s2) ? k : @PKG@.CfgFile.end(l, k);
    if (mig && e2 == k && !@PKG@.CfgFile.isComment(s2) && GKEY.equals(@PKG@.CfgFile.key(s2)) && @PKG@.CfgFile.value(l, k).trim().equals(GOLD)) {
      if (!firstOut) sb.append('\n');
      sb.append(s2.substring(0, @PKG@.CfgFile.valStart(s2))).append(GNEW).append(raw[k].endsWith("\r") ? "\r" : "");
      firstOut = false;
    } else {
      for (int q = k; q <= e2; q++) {
        if (!firstOut) sb.append('\n');
        sb.append(raw[q]);
        firstOut = false;
      }
    }
    k = e2 + 1;
  }
  String body = sb.toString();
  boolean hk = hasTableKey(p);
  boolean crlf = text.indexOf("\r\n") >= 0;
  String nl = crlf ? "\r\n" : "\n";
  String b = hk ? HEAD : BLOCK;
  if (crlf) b = b.replace("\n", "\r\n");
  String pre = (body.length() == 0 || body.endsWith("\n")) ? nl : nl + nl;
  String last = body.endsWith("\n") ? body.substring(0, body.length() - 1) : body;
  if (last.endsWith("\r")) last = last.substring(0, last.length() - 1);
  int bs = 0;
  for (int i = last.length() - 1; i >= 0 && last.charAt(i) == '\\'; i--) bs++;
  if (bs % 2 == 1 && body.endsWith("\n")) pre = pre + nl;
  java.util.ArrayList rows = new java.util.ArrayList();
  if (mig) { rows.add(GKEY); rows.add(GOLD); rows.add(GNEW); }
  if (!hk) for (int i = 0; i < KEYS.length; i++) { rows.add("levels.skill[" + KEYS[i] + "]"); rows.add("(none)"); rows.add(VALS[i]); }
  return new Object[] { body + pre + b, (String[]) rows.toArray(new String[0]), kept, Boolean.valueOf(mig), Boolean.valueOf(!hk) };
}"""), slm))
# only the planned keys may change: every old key keeps its value (gather.boost.skills: exactly GNEW when changed), exactly the default
# entries are new when the block entries were added
slm.addMethod(CtNewMethod.make(J14(r"""
public static boolean sameAfter(byte[] old, byte[] nb, boolean mig, boolean added) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties b = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    b.load(new java.io.ByteArrayInputStream(nb));
    if (b.size() != a.size() + (added ? KEYS.length : 0)) return false;
    java.util.Iterator it = a.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      String want = a.getProperty(k);
      if (mig && GKEY.equals(k)) want = GNEW;
      String got = b.getProperty(k);
      if (got == null || !got.equals(want)) return false;
    }
    if (added) for (int i = 0; i < KEYS.length; i++) {
      String y = b.getProperty(@PKG@.SkillLv.PREFIX + KEYS[i]);
      if (y == null || !y.equals(VALS[i]) || a.getProperty(@PKG@.SkillLv.PREFIX + KEYS[i]) != null) return false;
    }
    return true;
  } catch (Throwable t) { return false; }
}"""), slm))
slm.addMethod(CtNewMethod.make(J14(r"""
public static String logLine(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}"""), slm))
slm.addMethod(CtNewMethod.make(J14(r"""
public static synchronized String run() {
  java.nio.file.Path f = @PKG@.SkillCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = plan(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    boolean mig = ((Boolean) r[3]).booleanValue();
    boolean added = ((Boolean) r[4]).booleanValue();
    if (!sameAfter(old, data, mig, added)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.16 (Mining's own level list): the update would change another setting (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = @PKG@.HealMig.fileIdx();
    if (fi < 0) return "";
    @PKG@.HealMig.mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, "before the 0.4.16 Mining level list update");
    if (!@PKG@.HealMig.mgSaved(fi, old)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.16 (Mining's own level list): the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[1];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(logLine(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    StringBuilder what = new StringBuilder();
    if (added) what.append("added Mining's own level list (levels.skill.Mining: 10 + 5L + 1.5L^2 XP per level, Mining 10 at 955 XP, 20 at 5560)");
    if (mig) { if (what.length() > 0) what.append("; "); what.append(GKEY + " " + GOLD + " -> " + GNEW + " (Mining leaves the early gathering XP boost)"); }
    if (what.length() == 0) what.append("no setting changed (a levels.skill table and the gathering list were already set by an admin) - 0.4.16 marker added");
    String msg = "xp.properties updated for 0.4.16: " + what.toString() + " - nothing else changed; the old file is in config-history and Server Setup -> Changes can undo each line";
    @PKG@.SkillCfg.info(msg);
    String kept = (String) r[2];
    if (kept.length() > 0) { @PKG@.SkillCfg.info(kept); msg = msg + "\n" + kept; }
    return msg;
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("could not update xp.properties for 0.4.16 (Mining's own level list; the file is used as it is): " + t);
    return "";
  }
}"""), slm))

'''
before("# ---- ManaGuard (point 3): WARN once per class whose base Mana is below the Mana cost of a weapon in its class kit. Scheduler thread\n", SLMIG)

# ---------------------------------------------------------------------------------------------------------------- config rows
rep('''    ("levels", "XP per level, other skills (list)", "levels", "text", LEVELS_TEXT, "1", "2000", "", "", "live,danger,adv",
     "XP each level of every skill but the class skills needs, level 1 first; the count is the max level.",''',
    '''    ("levels", "XP per level, other skills (list)", "levels", "text", LEVELS_TEXT, "1", "2000", "", "", "live,danger,adv",
     "XP per level for skills without an own list (not class skills), level 1 first; count = max level.",''')
rep('''     "On: class skills use the list of the other skills again (the old, slower curve; levels drop back).",
     "reload;confirm=on"),
''', '''     "On: class skills use the list of the other skills again (the old, slower curve; levels drop back).",
     "reload;confirm=on"),
    # 0.4.16 (Skyy LOCKED 2026-10-04 / OK 2026-10-05): own XP-per-level lists per non-class skill (Mining = 10 + 5L + 1.5L^2 by default)
    ("levels.skill", "Own XP list per skill", "levels", "table", "", "", "2000", "text;type;XP per level (list)", "", "live,danger",
     "A listed skill levels on its own list (level 1 first). XP is kept; new levels pay coins once.", "reload;check=SkillLv.checkEntry"),
''')
rep('''    ("gather.boost.skills", "Gathering pace skills", "gathering", "text", "Mining,Foraging,Farming", "", "300", "", "", "live",
     "Skills whose earned XP gets the early boost below (Mining, Foraging, Farming), comma separated.", "reload;check=GatherPace.checkSkills"),''',
    '''    ("gather.boost.skills", "Gathering pace skills", "gathering", "text", "Foraging,Farming", "", "300", "", "", "live",
     "Skills whose earned XP gets the early boost below (Mining, Foraging, Farming), comma separated.", "reload;check=GatherPace.checkSkills"),''')
rep('''for _tk, _pfx in (("block", "block."), ("prefix", "prefix."), ("suffix", "suffix."), ("alchemy.xp", "alchemy.xp."), ("smithing.xp", "smithing.xp."),
                 ("mana.classBase", "mana.classBase."), ("mana.classPerLevel", "mana.classPerLevel.")):   # 0.4.15: + the class level table''',
    '''for _tk, _pfx in (("block", "block."), ("prefix", "prefix."), ("suffix", "suffix."), ("alchemy.xp", "alchemy.xp."), ("smithing.xp", "smithing.xp."),
                 ("mana.classBase", "mana.classBase."), ("mana.classPerLevel", "mana.classPerLevel."),   # 0.4.15: + the class level table
                 ("levels.skill", "levels.skill.")):   # 0.4.16: + the own level lists''')
rep('''assert len(CFG_ROWS) == 196, (''', '''assert len(CFG_ROWS) == 197, (''')
rep('''                              "mana.classPerLevel table, got %d" % len(CFG_ROWS))''',
    '''                              "mana.classPerLevel table; 0.4.16: + the levels.skill table, got %d" % len(CFG_ROWS))''')
rep('''                  ("CLS", CLS_DEFAULTS), ("CURVE", CURVE_DEFAULTS), ("MREG", MREG_DEFAULTS), ("N14", N14_DEFAULTS), ("CMAN", CMAN_DEFAULTS)):''',
    '''                  ("CLS", CLS_DEFAULTS), ("CURVE", CURVE_DEFAULTS), ("MREG", MREG_DEFAULTS), ("N14", N14_DEFAULTS), ("CMAN", CMAN_DEFAULTS),
                  ("SKL", SKL_DEFAULTS)):   # 0.4.16''')
before('''kit = CFG.emit(pool, PKG, MOD="SkyySkills", TITLE="Skills", VERSION=VERSION,''', '''# 0.4.16: the own level list table - its default entry in the default file AND in the SKL block (SkillLvMig appends it to an old file), right
# after the class rows; no other row key inside its family; the gathering pace default without Mining (row = file = GatherPace)
assert _dp.get("levels.skill.Mining") == ",".join(str(_x) for _x in MINING_PER) and sorted(_k for _k in _dp if _k.startswith("levels.skill.")) == SKL_KEYS
_k16 = [_r[0] for _r in CFG_ROWS]
assert _k16.count("levels.skill") == 1 and _k16[_k16.index("levels.class.sameAsOthers") + 1] == "levels.skill"
assert not any(_k.startswith("levels.skill") for _k in _k16 if _k != "levels.skill")
assert _dp.get("gather.boost.skills") == "Foraging,Farming" == [_r for _r in CFG_ROWS if _r[0] == "gather.boost.skills"][0][4]
assert DEFAULTS.endswith("\\n" + SKL_DEFAULTS)
''')

# ---------------------------------------------------------------------------------------------------------------- classes + plugin
rep('''cmig = pool.makeClass(PKG + ".ClassManaMig")
''', '''cmig = pool.makeClass(PKG + ".ClassManaMig")
# 0.4.16: own level lists per skill (SkillLv: the levels.skill table), their one-time notice + rewards (OwnCurve) and the one-time config update
# of an existing xp.properties (SkillLvMig: Mining's list + Mining out of the gathering pace)
slv  = pool.makeClass(PKG + ".SkillLv")
own  = pool.makeClass(PKG + ".OwnCurve")
slm  = pool.makeClass(PKG + ".SkillLvMig")
''')
rep('''          cman, cmig):   # 0.4.11: + HealMig;''', '''          cman, cmig,
          slv, own, slm):   # 0.4.16: + SkillLv, OwnCurve, SkillLvMig; 0.4.11: + HealMig;''')
after("  {PKG}.ClassManaMig.run();   // 0.4.15: the max Mana per class level lines into an existing xp.properties, once; History first\n",
      "  {PKG}.SkillLvMig.run();     // 0.4.16: Mining's own level list + Mining out of the gathering pace into an existing xp.properties, once; History first\n")
after("  String curve = {PKG}.ClassCurve.start(base);   // 0.4.12: the first 0.4.12 start records once which profiles' class levels rose\n",
      "  String ownc = {PKG}.OwnCurve.start(base);     // 0.4.16: the first start with an own level list records once which profiles' levels moved\n")
rep('''"; max Mana per class level " + {PKG}.ClassMana.text() + "; staff handover''',
    '''"; max Mana per class level " + {PKG}.ClassMana.text() + "; own level lists " + {PKG}.SkillLv.text() + (ownc.length() > 0 ? " (" + ownc + ")" : "") + "; leaderboards skip deleted / archived profiles" + "; staff handover''')
rep('''Mining, Foraging and Farming XP x3 to level 10, easing to x1.5 by level 20;''',
    '''Foraging and Farming XP x3 to level 10, easing to x1.5 by level 20; Mining levels on its own list (10 + 5L + 1.5L^2 XP per level: Mining 10 at 955 XP, 20 at 5,560; Server Setup: Own XP list per skill) - saved XP is kept, players are told once, new levels pay the normal coins once and a lower level takes nothing back;''')
rep('''Level ups pay SkyyCoins. /skills.''', '''Level ups pay SkyyCoins. /skills (Top 10 lists leave out deleted and archived profiles).''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
for k in KEEP:
    assert s.count(k) == 1, "a block that must stay byte-identical changed: " + k[:100]
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "systems / commands: 0.4.16 adds none"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
_ix = lambda t: s.index(t)
# methods before callers (javassist compiles each method body when it is added)
assert _ix("public static long[] own(int s)") < _ix("public static boolean hasOwn(int s)") < _ix("public static long[] cumOf(int s) {\n  if (isClass(s)) return ECUM;")
assert _ix("public static long[] cumOf(int s) {\n  if (isClass(s)) return ECUM;") < _ix("public static int maxOf(int s)")
assert _ix("public static Object[] parseTable(java.util.Properties p) {\n  Object[] o = new Object[") < _ix("public static void read(java.util.Properties p) {\n  Object[] t = parseTable(p);\n  @PKG@.SkillDefs.setOwn(")
assert _ix("{PKG}.SkillLv.read(p);") > _ix("public static void read(java.util.Properties p) {\n  Object[] t = parseTable(p);\n  @PKG@.SkillDefs.setOwn(")
assert _ix("{PKG}.SkillDefs.setClassTable(cper,") < _ix("{PKG}.SkillLv.read(p);")
assert _ix("public static void deliver(@PR@ pr, java.util.UUID u, String k, String e) {\n  try {\n    long[] d = @PKG@.SkillStore.dataK(k, u);\n    String[] parts = e.split(\",\");\n    int[] sl = new int[parts.length];\n    int[] was = new int[parts.length];\n    int[] now = new int[parts.length];\n    int n = 0;\n    StringBuilder lines = new StringBuilder();\n    StringBuilder sum = new StringBuilder();\n    long coins = 0L;\n    long first = -1L;\n    long last = -1L;\n    int ups")
assert _ix("own.addMethod(CtNewMethod.make(J14(r\"\"\"\npublic static void tick(") < _ix("{PKG}.OwnCurve.tick(pr, u);   // 0.4.16: a pending own level list")
assert _ix("public static void levelUp({PR} pr, java.util.UUID u, int skill, long oldLv, long newLv)") < _ix("@PKG@.Overall.levelUp(pr, u, sl[i], (long) was[i], (long) now[i]);")
assert _ix("public static boolean gone(java.util.function.Function sf, String key)") < _ix("java.util.function.Function sf = stateFn();   // 0.4.16")
assert _ix("public static Object[] plan(String text) {\n  if (text == null) return null;\n  java.util.Properties p = new java.util.Properties();\n  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { return null; }\n  String[] raw") < _ix("public void setup() {{")
assert s.index("{PKG}.ClassManaMig.run();") < s.index("{PKG}.SkillLvMig.run();") < s.index("String rules = {PKG}.SkillCfg.load();") < s.index("String curve = {PKG}.ClassCurve.start(base);") < s.index("String ownc = {PKG}.OwnCurve.start(base);")
assert _ix("public static int slotOf(String t) {\n  if (t == null) return -1;\n  String x = t.trim();") < _ix("public static boolean listsMining(String v)")
assert s.count("{PKG}.OwnCurve.flush();") == 2 and s.count("{PKG}.OwnCurve.tick(pr, u);") == 2
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed]
assert not _bad, "0.4.15 lines changed outside the planned places: %r" % _bad[:5]
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.15,", len(_gone), "0.4.15 lines replaced,",
      sum(op[4] - op[3] for op in _hunks) - len(_gone), "lines added net;", len(OLDS), "anchors")
