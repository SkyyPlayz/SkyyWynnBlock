"""Derive SkyySkills/build_skyyskills_0.4.35.py from the LIVE generated SkyySkills/build_skyyskills_0.4.34.py (= the tools/deploy_set.py SET
pin; 0.4.34 came from 0.4.33 by tools/skills_0_4_34_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; 0.4.34 stays untouched, its line endings are kept.
Run:  python tools/skills_0_4_35_patch.py   then   python SkyySkills/build_skyyskills_0.4.35.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.35.py --dir tools/dev/scratch/<yours>/sk   (bare JVM, -Xverify:all)

0.4.35 (2026-10-13) = REBIRTH ROUND R1 (research/cloud/Rebirth-Spec.md section 6 R1; Skyy's answers docs/answered/economy.md 2026-10-13
REBIRTH: Q3 "acrobatics yes, exploration, no.", Q11 "recommended curve. (tracks xp gained past max lvl, for bonus points.)", Q12 "+10
levels, +1 rank") + the gathering tier-gate follow-up (research/Gathering-Shards-Spec.md 4.3: "M = T + 1 harvests at half XP").
  RUN XP - CHECKED FIRST: SkyySkills ALREADY counts and stores every XP point past the max level. SkillStore.bump adds the full amount to
    the saved total (players/<pkey>.properties <Skill>=<total XP>, per profile) with no cap; only the LEVEL is capped (SkillDefs.levelIn
    stops at the table's last level). Nothing else ever lowers or sets a total (bump is the only writer). So the run XP of a skill = its
    saved total XP: XP gained since the profile started (and, from R3 on, since the last rebirth, which sets the total back to 0). NO new
    run.<Skill> lines, no saved-data change, no migration (a second counter would only ever hold the same number). Other mods read it
    through the new bridge function skill:fn:run (below).
  LEVEL CAPS FROM THE BRIDGE (rebirth:fn:cap, SkyyRebirth 0.1+): SkillCap asks apply(Object[] { String pkey, String saved skill name
    (SkillDefs.NAMES: Mining, Combat.Archer, ...), Integer today's cap }) -> Integer cap, once per profile per 5 s (cached per pkey; a new
    function object = a fresh ask), on the caller's thread, memory only. No SkyyRebirth / null / not a number / an answer below today's cap
    / a throwing function = today's cap (one WARN per JVM); a null / non-number answer (SkyyRebirth still reading that profile's file)
    is kept only SkillCap.RETRY = 250 ms, then asked again (fix round: never a cached 'no raise' for 5 s after a join). The raise is kept as levels above today's cap (at most 1000), so a Server
    Setup level-table change still moves the base. Levels above a table's last level cost the XP of that table's LAST level each (flat;
    UNVERIFIED balance - the Balance Workbench sets real numbers when rebirth goes live). EXPLORATION never asks (it never resets, Skyy
    Q3), Acrobatics does. Where the capped level is used: SkillStore.level (perks, Fortune, the gathering pace, combat damage, mob XP
    gaps - everything that read the level), the level ups in addK / gain4 (+ their coin rewards: owesK / payLocked pay up to the capped
    level of the profile key k whose data is paid (fix round: payLocked / payGuarded take k), through the same paid marker - nothing is ever paid twice), the default paid marker of a file without one, skill:<uuid>,
    skill:fn:level, the XP chat line / party line progress, the "next:" / "is now MAX level" line, the /skills rows and the Stats page
    ("level 105 of 110"). The Overall Level keeps the table levels (Overall.levelUp gets the levels clamped to the table max, so a level
    above the table never shows a false OVERALL LEVEL UP); the leaderboards and the one-time curve notices keep the table levels too.
    With no SkyyRebirth, or every profile at 0 rebirths (all of SkyyRebirth 0.1), every number is exactly 0.4.34's (harness: every slot,
    every level boundary, SkillDefs.levelCap / needCap / intoCap / progressCap = levelOf / needFor / intoLevel / progress).
  skill:fn:run (NEW): apply(Object[] { UUID or String pkey, String skill }) -> Object[] { Integer level (capped), Integer cap, Long run XP
    (= the saved total), Long XP from 0 to the cap, Boolean resets on rebirth (false = Exploration), String saved skill name } or null.
    skill = any /skills name, a class skill, "combat" (the class row) or "class" (the profile's class skill; UUID only). A UUID reads the
    active profile (loads its file like skill:fn:level); a pkey that is not loaded is read from its file under the IO lock and NOT cached.
    A String must be a profile key (<uuid> or <uuid>-p<n>; fix round: anything else = null, never a path). Any thread, never throws.
  HALF FARMING XP ONE TIER UP (docs/answered/gear.md 2026-10-13 TOOL SPEED; SkyyGear 0.3.1 publishes gear:fn:farmTier): a crop broken
    with a hoe / sickle one or two tiers below the crop (gear:fn:farmTier answers 1; 2 = refused - it cannot break, but if it ever did it
    is halved too) pays HALF its Farming XP (FarmTier.scale: an odd amount gives the last point 50 % of the time), before the gathering
    pace and the tree Wisdom. Asked with Object[] { UUID, the block id (BreakBlockEvent block type id; a sickle swing: the crop's family
    id), the held item id }. No SkyyGear 0.3+, its gate off (it answers -1), a hand / non-farming tool (-1), 0 = normal: full XP. Covers
    a broken crop (BreakTask) and a sickle swing (Sickle.award: the held sickle is remembered by SickleSys in Sickle.HELD, pruned with
    the other sickle contexts). F-harvests by hand are never gated (spec 4.3). No Fortune change here (SkyyGear's own tool Fortune rule).
    Fix round: the factor is the Server Setup row farming.tierUpXpFactor (Skills -> gathering, default 0.5, 0-1, live; 1 = off and
    SkyyGear is not asked). No line is written into xp.properties until an admin changes it (a missing line = 0.5).
  ROLLBACK to 0.4.34 is safe: no saved data, no migration (0.4.34 ignores a farming.tierUpXpFactor line); the caps go back to the tables (0.4.34 ignores rebirth:fn:cap).
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.34.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.35.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.34"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.34"' in s and "derived from the generated 0.4.33 by tools/skills_0_4_34_patch.py" in s, "not the live generated 0.4.34"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "mrt = pool.makeClass(PKG + \".MsgRoute\")" in s, "not 0.4.34 (MsgRoute missing)"
OLDS = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    OLDS.append(old)


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.35 (2026-10-13)"):].rstrip() + "\n"

# ---------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.34 - build script (derived from the generated 0.4.33 by tools/skills_0_4_34_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.35 - build script (derived from the generated 0.4.34 by tools/skills_0_4_35_patch.py - edit the patch, not this file;
0.4.34 was derived from the generated 0.4.33 by tools/skills_0_4_34_patch.py;
''')
rep('''0.4.34 (2026-10-13) = CHAT OVERFLOW -> FEED''', NOTE.replace("\n", "\n  ").rstrip() + '''
  CHECKED: SkyySkills/test_skyyskills_0.4.35.py.
0.4.34 (2026-10-13) = CHAT OVERFLOW -> FEED''')
rep('VERSION = "0.4.34"', 'VERSION = "0.4.35"')

# ---------------------------------------------------------------- SkillDefs: rebirthResets + the capped level maths (pure)
rep('''defs.addMethod(CtNewMethod.make("""
public static String progress(int s, long total) {
  long need = needFor(s, total);
  if (need <= 0L) return "MAX";
  return fmt(intoLevel(s, total)) + "/" + fmt(need);
}""", defs))
''', '''defs.addMethod(CtNewMethod.make("""
public static String progress(int s, long total) {
  long need = needFor(s, total);
  if (need <= 0L) return "MAX";
  return fmt(intoLevel(s, total)) + "/" + fmt(need);
}""", defs))
# ================= 0.4.35 REBIRTH CAPS (research/cloud/Rebirth-Spec.md 3.1 / 4.3; Skyy Q3 "acrobatics yes, exploration, no."): pure maths =====
# rebirthResets = the slot is reset by a rebirth (and its cap rises): every slot but Exploration. levelCap / intoCap / needCap / progressCap =
# levelOf / intoLevel / needFor / progress with a per-profile cap: a cap at or below the table's max = EXACTLY the table answer; above it,
# every extra level costs the table's LAST level's XP (stepTop; flat - UNVERIFIED balance). cumAt = the total XP a level starts at.
defs.addMethod(CtNewMethod.make("""
public static boolean rebirthResets(int s) {
  return s >= 0 && s < N && s != EXPLORATION;
}""", defs))
defs.addField(CtField.make("public static final int CAP_EXTRA_MAX = 1000;", defs))
defs.addMethod(CtNewMethod.make("""
public static long stepTop(long[] c) {
  int max = c.length - 1;
  long st = max >= 1 ? c[max] - c[max - 1] : 1L;
  return st > 0L ? st : 1L;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static int capMax(int s, int cap) {
  int m = maxOf(s);
  return cap > m ? cap : m;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static long cumAt(int s, int lv) {
  long[] c = cumOf(s);
  int max = c.length - 1;
  if (lv <= 0) return c[0];
  if (lv <= max) return c[lv];
  long extra = (long) (lv - max);
  long st = stepTop(c);
  if (st > (Long.MAX_VALUE - c[max]) / extra) return Long.MAX_VALUE;
  return c[max] + st * extra;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static int levelCap(int s, long total, int cap) {
  long[] c = cumOf(s);
  int max = c.length - 1;
  int l = levelIn(c, total);
  if (cap <= max || l < max) return l;
  long over = (total - c[max]) / stepTop(c);
  long lv = (long) max + over;
  return lv >= (long) cap ? cap : (int) lv;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static long intoCap(int s, long total, int cap) {
  return total - cumAt(s, levelCap(s, total, cap));
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static long needCap(int s, long total, int cap) {
  int l = levelCap(s, total, cap);
  if (l >= capMax(s, cap)) return 0L;
  return cumAt(s, l + 1) - cumAt(s, l);
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static String progressCap(int s, long total, int cap) {
  long need = needCap(s, total, cap);
  if (need <= 0L) return "MAX";
  return fmt(intoCap(s, total, cap)) + "/" + fmt(need);
}""", defs))
''')

# ---------------------------------------------------------------- SkillCap: the per-profile cap from rebirth:fn:cap (before SkillClass / readFile)
rep('''# ================= SkillClass (0.3): the player's class from SkyyClasses (bridge), class combat rules =================
''', '''# ================= 0.4.35 SkillCap: the per-profile level cap from SkyyRebirth's rebirth:fn:cap (research/cloud/Rebirth-Spec.md 4.3) =================
# CACHE = pkey -> Object[]{Long asked ms, int[] levels above today's cap per slot, the Function asked}: one ask per profile per TTL ms (a new
# function object = asked again). Memory only, any thread, never throws. No SkyyRebirth = no ask, today's caps (= 0.4.34 everywhere).
scap = pool.makeClass(PKG + ".SkillCap")
for _d in ("public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();",
           "public static volatile long TTL = 5000L;", "public static volatile long RETRY = 250L;", "public static volatile boolean WARNED = false;",
           "public static final java.util.concurrent.atomic.AtomicLong ASKS = new java.util.concurrent.atomic.AtomicLong();"):
    scap.addField(CtField.make(_d, scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static int[] fetch(java.util.function.Function f, String k) {
  int n = @PKG@.SkillDefs.N;
  int[] ex = new int[n + 1];
  for (int s = 0; s < n; s++) {
    if (!@PKG@.SkillDefs.rebirthResets(s)) continue;
    int base = @PKG@.SkillDefs.maxOf(s);
    try {
      ASKS.incrementAndGet();
      Object r = f.apply(new Object[] { k, @PKG@.SkillDefs.NAMES[s], Integer.valueOf(base) });
      if (r instanceof Number) {
        long v = ((Number) r).longValue() - (long) base;
        if (v < 0L) v = 0L;
        if (v > (long) @PKG@.SkillDefs.CAP_EXTRA_MAX) v = (long) @PKG@.SkillDefs.CAP_EXTRA_MAX;
        ex[s] = (int) v;
      } else {
        ex[n] = 1;   // fix round: no answer yet (SkyyRebirth still reading the profile's file) - kept RETRY ms only, not TTL
      }
    } catch (Throwable t) {
      if (!WARNED) { WARNED = true; @PKG@.SkillCfg.warn("rebirth:fn:cap (SkyyRebirth) failed - today's level caps apply (logged once): " + t); }
    }
  }
  return ex;
}"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static int extra(String k, int s) {
  if (k == null || !@PKG@.SkillDefs.rebirthResets(s)) return 0;
  Object f = @PKG@.SkillStore.bridge().get("rebirth:fn:cap");
  if (!(f instanceof java.util.function.Function)) return 0;
  long now = System.currentTimeMillis();
  Object o = CACHE.get(k);
  int[] ex = null;
  if (o instanceof Object[]) {
    Object[] e = (Object[]) o;
    if (e.length > 2 && e[2] == f) {
      int[] c = (int[]) e[1];
      long ttl = (c.length > @PKG@.SkillDefs.N && c[@PKG@.SkillDefs.N] != 0) ? RETRY : TTL;
      if (now - ((Long) e[0]).longValue() < ttl) ex = c;
    }
  }
  if (ex == null) {
    ex = fetch((java.util.function.Function) f, k);
    if (CACHE.size() > 4096) CACHE.clear();
    CACHE.put(k, new Object[] { Long.valueOf(now), ex, f });
  }
  return s < ex.length ? ex[s] : 0;
}"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static int cap(String k, int s) {
  if (s < 0 || s >= @PKG@.SkillDefs.N) return 0;
  return @PKG@.SkillDefs.maxOf(s) + extra(k, s);
}"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static int level(String k, int s, long total) {
  if (s < 0 || s >= @PKG@.SkillDefs.N) return 0;
  return @PKG@.SkillDefs.levelCap(s, total, cap(k, s));
}"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static long need(String k, int s, long total) {
  return @PKG@.SkillDefs.needCap(s, total, cap(k, s));
}"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static long into(String k, int s, long total) {
  return @PKG@.SkillDefs.intoCap(s, total, cap(k, s));
}"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static String progress(String k, int s, long total) {
  return @PKG@.SkillDefs.progressCap(s, total, cap(k, s));
}"""), scap))
# the same for a player's ACTIVE profile (pkey per call: one bridge read)
scap.addMethod(CtNewMethod.make(J14(r"""
public static int capU(java.util.UUID u, int s) { return cap(@PKG@.SkillStore.pkey(u), s); }"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static int levelU(java.util.UUID u, int s, long total) { return level(@PKG@.SkillStore.pkey(u), s, total); }"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static long needU(java.util.UUID u, int s, long total) { return need(@PKG@.SkillStore.pkey(u), s, total); }"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static long intoU(java.util.UUID u, int s, long total) { return into(@PKG@.SkillStore.pkey(u), s, total); }"""), scap))
scap.addMethod(CtNewMethod.make(J14(r"""
public static String progressU(java.util.UUID u, int s, long total) { return progress(@PKG@.SkillStore.pkey(u), s, total); }"""), scap))
# ================= SkillClass (0.3): the player's class from SkyyClasses (bridge), class combat rules =================
''')

# ---------------------------------------------------------------- SkillStore: the capped level everywhere a level is decided
rep('''  for (int i = 0; i < {PKG}.SkillDefs.N; i++) if (d[{PKG}.SkillDefs.N + i] < 0L) d[{PKG}.SkillDefs.N + i] = (long) {PKG}.SkillDefs.levelOf(i, d[i]);''',
    '''  for (int i = 0; i < {PKG}.SkillDefs.N; i++) if (d[{PKG}.SkillDefs.N + i] < 0L) d[{PKG}.SkillDefs.N + i] = (long) {PKG}.SkillCap.level(k, i, d[i]);   // 0.4.35: the profile's cap''')
rep('''public static int level(java.util.UUID u, int skill) {{
  if (skill < 0 || skill >= {PKG}.SkillDefs.N) return 0;
  return {PKG}.SkillDefs.levelOf(skill, data(u)[skill]);
}}''', '''public static int level(java.util.UUID u, int skill) {{
  if (skill < 0 || skill >= {PKG}.SkillDefs.N) return 0;
  String k = pkey(u);
  return {PKG}.SkillCap.level(k, skill, dataK(k, u)[skill]);   // 0.4.35: the profile's cap (rebirth:fn:cap)
}}''')
rep('''public static String levelsOf(java.util.UUID u, long[] d) {{
  int cs = {PKG}.SkillClass.slot(u);''', '''public static String levelsOf(java.util.UUID u, long[] d) {{
  int cs = {PKG}.SkillClass.slot(u);
  String pk = pkey(u);   // 0.4.35: the levels at the profile's caps''')
rep('''    sb.append({PKG}.SkillDefs.LABELS[order[i]]).append(':').append({PKG}.SkillDefs.levelOf(order[i], d[order[i]]));''',
    '''    sb.append({PKG}.SkillDefs.LABELS[order[i]]).append(':').append({PKG}.SkillCap.level(pk, order[i], d[order[i]]));''')
rep('''    sb.append(',').append({PKG}.SkillDefs.LABELS[s]).append(':').append({PKG}.SkillDefs.levelOf(s, d[s]));''',
    '''    sb.append(',').append({PKG}.SkillDefs.LABELS[s]).append(':').append({PKG}.SkillCap.level(pk, s, d[s]));''')
rep('''  return new long[] {{ (long) {PKG}.SkillDefs.levelOf(skill, ba[0]), (long) {PKG}.SkillDefs.levelOf(skill, ba[1]), ba[1] }};''',
    '''  return new long[] {{ (long) {PKG}.SkillCap.level(k, skill, ba[0]), (long) {PKG}.SkillCap.level(k, skill, ba[1]), ba[1] }};   // 0.4.35: capped''')
rep('''  return rd(d, {PKG}.SkillDefs.N + skill) < (long) {PKG}.SkillDefs.levelOf(skill, rd(d, skill));''',
    '''  return rd(d, {PKG}.SkillDefs.N + skill) < (long) {PKG}.SkillCap.level(k, skill, rd(d, skill));   // 0.4.35: capped''')
# fix round (critic): the cap comes from the profile key k whose data d is paid (owesK / payOwedK's k) - never the active profile at
# payout time (a profile switch in between would pay profile A's XP at profile B's cap)
rep('''public static long[] payLocked(java.util.UUID u, int skill, long[] d) {{''',
    '''public static long[] payLocked(String k, java.util.UUID u, int skill, long[] d) {{''')
rep('''  int lv = {PKG}.SkillDefs.levelOf(skill, rd(d, skill));
  boolean stop = false;''', '''  int lv = {PKG}.SkillCap.level(k, skill, rd(d, skill));   // 0.4.35: up to the cap of profile k (the paid marker still pays each level once)
  boolean stop = false;''')
rep('''public static long[] payGuarded(java.util.UUID u, int skill, long[] d) {
  synchronized (d) { return payLocked(u, skill, d); }''', '''public static long[] payGuarded(String k, java.util.UUID u, int skill, long[] d) {
  synchronized (d) { return payLocked(k, u, skill, d); }''')
rep('''  long[] res = payGuarded(u, skill, d);''', '''  long[] res = payGuarded(k, u, skill, d);''')

# ---------------------------------------------------------------- the XP lines, the level-up line, the Overall clamp
rep('''    sb.append("+").append({PKG}.SkillDefs.fmt(p[i])).append(" ").append({PKG}.SkillDefs.LABELS[i]).append(" XP (").append({PKG}.SkillDefs.progress(i, d[i])).append(")");''',
    '''    sb.append("+").append({PKG}.SkillDefs.fmt(p[i])).append(" ").append({PKG}.SkillDefs.LABELS[i]).append(" XP (").append({PKG}.SkillCap.progressU(u, i, d[i])).append(")");''')
rep('''    sb.append("+").append({PKG}.SkillDefs.fmt(p[i])).append(" ").append({PKG}.SkillClass.skillName(u, i)).append(" XP (").append({PKG}.SkillDefs.progress(i, d[i])).append(")");''',
    '''    sb.append("+").append({PKG}.SkillDefs.fmt(p[i])).append(" ").append({PKG}.SkillClass.skillName(u, i)).append(" XP (").append({PKG}.SkillCap.progressU(u, i, d[i])).append(")");''')
rep('''    long need = {PKG}.SkillDefs.needFor(skill, r[2]);
    if (lvOn) pr.sendMessage({MSG}.raw(need > 0L ? "  next: " + sk + " " + (r[1] + 1L) + " at " + {PKG}.SkillDefs.progress(skill, r[2]) + " XP - /skills" : "  " + sk + " is now MAX level!").color("#c8b070"));
    {PKG}.Overall.levelUp(pr, u, skill, r[0], r[1]);''', '''    long need = {PKG}.SkillCap.need(k, skill, r[2]);   // 0.4.35: the profile's cap
    if (lvOn) pr.sendMessage({MSG}.raw(need > 0L ? "  next: " + sk + " " + (r[1] + 1L) + " at " + {PKG}.SkillCap.progress(k, skill, r[2]) + " XP - /skills" : "  " + sk + " is now MAX level!").color("#c8b070"));
    long tmax = (long) {PKG}.SkillDefs.maxOf(skill);   // 0.4.35: the Overall Level counts the table levels (no false OVERALL LEVEL UP above it)
    {PKG}.Overall.levelUp(pr, u, skill, Math.min(r[0], tmax), Math.min(r[1], tmax));''')

# ---------------------------------------------------------------- /skills rows + the Stats page
rep('''      long total = d[sl];
      int lv = {PKG}.SkillDefs.levelOf(sl, total);
      long cur = {PKG}.SkillDefs.intoLevel(sl, total);
      long need = {PKG}.SkillDefs.needFor(sl, total);''', '''      long total = d[sl];
      int lv = {PKG}.SkillCap.levelU(u, sl, total);   // 0.4.35: the profile's cap
      long cur = {PKG}.SkillCap.intoU(u, sl, total);
      long need = {PKG}.SkillCap.needU(u, sl, total);''')
rep('''  long total = d[s];
  int lv = {PKG}.SkillDefs.levelOf(s, total);
  long cur = {PKG}.SkillDefs.intoLevel(s, total);
  long need = {PKG}.SkillDefs.needFor(s, total);
  int fill = need > 0L ? (int) ({STBARW}L * cur / need) : {STBARW};''', '''  long total = d[s];
  int lv = {PKG}.SkillCap.levelU(u, s, total);   // 0.4.35: the profile's cap
  long cur = {PKG}.SkillCap.intoU(u, s, total);
  long need = {PKG}.SkillCap.needU(u, s, total);
  int fill = need > 0L ? (int) ({STBARW}L * cur / need) : {STBARW};''')
rep('''  b.set("#SkyyStTitle.Text", legacy ? "Combat - no class" : name + " - level " + lv + " of " + {PKG}.SkillDefs.maxOf(s));''',
    '''  b.set("#SkyyStTitle.Text", legacy ? "Combat - no class" : name + " - level " + lv + " of " + {PKG}.SkillCap.capU(u, s));''')

# ---------------------------------------------------------------- FarmTier (before the Sickle block: Sickle.award calls it)
rep('''# ================= Sickle (0.4.14, research/Tool-Levels-Spec.md question 3): sickle swing harvests pay Farming XP + roll double drops =================
''', '''# ================= 0.4.35 FarmTier: half Farming XP one tier above your hoe / sickle (SkyyGear 0.3.1 gear:fn:farmTier; Gathering-Shards-Spec 4.3) ===
# ask(u, block id, held item id) = gear:fn:farmTier's answer (-1 not gated, 0 normal, 1 above your tier, 2 refused); no SkyyGear / not a
# number / throws (one WARN per JVM) = -1. apply = half the XP when the answer is 1 or 2 (half: an odd amount pays its last point 50 %).
ftr = pool.makeClass(PKG + ".FarmTier")
for _d in ("public static volatile boolean WARNED = false;",
           "public static final java.util.concurrent.atomic.AtomicLong ASKED = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong HALVED = new java.util.concurrent.atomic.AtomicLong();"):
    ftr.addField(CtField.make(_d, ftr))
ftr.addMethod(CtNewMethod.make(J14(r"""
public static int ask(java.util.UUID u, String bid, String held) {
  if (bid == null) return -1;
  Object f = @PKG@.SkillStore.bridge().get("gear:fn:farmTier");
  if (!(f instanceof java.util.function.Function)) return -1;
  try {
    ASKED.incrementAndGet();
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, bid, held });
    return r instanceof Number ? ((Number) r).intValue() : -1;
  } catch (Throwable t) {
    if (!WARNED) { WARNED = true; @PKG@.SkillCfg.warn("gear:fn:farmTier (SkyyGear) failed - full Farming XP (logged once): " + t); }
    return -1;
  }
}"""), ftr))
ftr.addMethod(CtNewMethod.make(J14(r"""
public static long half(long amt, double r) {
  if (amt <= 0L) return amt;
  long h = amt / 2L;
  if ((amt % 2L) != 0L && r < 0.5) h++;
  return h;
}"""), ftr))
# fix round (critic: the 0.5 was hard-coded): amt x f, the fraction paid by chance r (f 0.5 = half exactly as above; f >= 1 = amt; f <= 0 = 0)
ftr.addMethod(CtNewMethod.make(J14(r"""
public static long scale(long amt, double f, double r) {
  if (amt <= 0L) return amt;
  if (!(f > 0.0)) return 0L;
  if (f >= 1.0) return amt;
  double x = (double) amt * f;
  long w = (long) Math.floor(x);
  double fr = x - (double) w;
  if (fr > 0.0 && r < fr) w++;
  return w;
}"""), ftr))
# Server Setup -> Skills -> gathering "Farming XP one tier above your tool" (farming.tierUpXpFactor, Sickle.TIER_XP, default 0.5); 1 = off
# (SkyyGear is not even asked)
ftr.addMethod(CtNewMethod.make(J14(r"""
public static long apply(java.util.UUID u, String bid, String held, long amt) {
  if (amt <= 0L) return amt;
  double f = @PKG@.Sickle.TIER_XP;
  if (f >= 1.0) return amt;
  if (ask(u, bid, held) < 1) return amt;
  HALVED.incrementAndGet();
  return scale(amt, f, java.util.concurrent.ThreadLocalRandom.current().nextDouble());
}"""), ftr))
# BreakTask: the broken block's type id + the item the breaker held (the event keeps both)
ftr.addMethod(CtNewMethod.make(J14(r"""
public static long breakXp(java.util.UUID u, @BBE@ ev, long amt) {
  if (ev == null) return amt;
  String bid = null;
  String held = null;
  try { @BTY@ bt = ev.getBlockType(); bid = bt == null ? null : bt.getId(); } catch (Throwable t) { bid = null; }
  try { @IS@ h = ev.getItemInHand(); held = (h == null || h.isEmpty()) ? null : h.getItemId(); } catch (Throwable t) { held = null; }
  return apply(u, bid, held, amt);
}"""), ftr))
# ================= Sickle (0.4.14, research/Tool-Levels-Spec.md question 3): sickle swing harvests pay Farming XP + roll double drops =================
''')
rep('''           "public static final long BREAK_NS = 250000000L;", "public static final long WINDOW_MS = 2000L;"):''',
    '''           "public static final long BREAK_NS = 250000000L;", "public static final long WINDOW_MS = 2000L;",
           "public static final java.util.concurrent.ConcurrentHashMap HELD = new java.util.concurrent.ConcurrentHashMap();",   # 0.4.35: UUID -> the sickle id of the last swing (FarmTier)
           "public static volatile double TIER_XP = 0.5;"):   # 0.4.35 fix round: farming.tierUpXpFactor (FarmTier.apply)''')
# fix round: the factor is a Server Setup row (read with the other farming.* keys; a missing line = 0.5, clamped 0-1, a bad number = 0.5)
rep('''  ON = @PKG@.SkillCfg.bool(p, "farming.sickle.enabled", true);
''', '''  ON = @PKG@.SkillCfg.bool(p, "farming.sickle.enabled", true);
  double tf = @PKG@.SkillCfg.dbl(p, "farming.tierUpXpFactor", 0.5);
  TIER_XP = Double.isNaN(tf) ? 0.5 : (tf < 0.0 ? 0.0 : (tf > 1.0 ? 1.0 : tf));   // 0.4.35 fix round
''')
rep('''     "_Trunk -> Foraging:6. The longest matching start or end of an id wins.", "reload;check=SkillKit.checkRule"),
''', '''     "_Trunk -> Foraging:6. The longest matching start or end of an id wins.", "reload;check=SkillKit.checkRule"),
    ("farming.tierUpXpFactor", "Farming XP one tier above your tool", "gathering", "dec", "0.5", "0", "1", "", "x", "live",
     "A crop above your hoe / sickle tier (SkyyGear gate) pays its Farming XP times this. 1 = off.", "reload"),
''')
rep('''assert len(CFG_ROWS) == 228, ("0.4.26: + perk.fortuneMax;''',
    '''assert len(CFG_ROWS) == 229, ("0.4.35: + farming.tierUpXpFactor; 0.4.26: + perk.fortuneMax;''')
# the default file of a FRESH install carries the line (the kit's rule: every row key is in the default file). An existing xp.properties
# is NOT touched (no ensure / append - a missing line reads 0.5; the kit adds the line when an admin changes the row).
rep(r'''L.extend(N14_L)
N14_DEFAULTS = "\n".join(N14_L) + "\n"
''', r'''L.extend(N14_L)
L.append("")   # 0.4.35: Farming XP one tier above your tool (fresh files only; an existing file without the line reads the default 0.5)
L.append("# ---------- Farming one tier above your tool (SkyySkills 0.4.35) ----------")
L.append("# A crop one or two tiers above your hoe or sickle (the SkyyGear tier gate) pays its Farming XP times this factor.")
L.append("# 1 turns it off. Hand harvests (F) are never changed.")
L.append("farming.tierUpXpFactor=0.5")
N14_DEFAULTS = "\n".join(N14_L) + "\n"
''')
rep('''  BRK.keySet().retainAll(online);
  USE.keySet().retainAll(online);
  PEND.keySet().retainAll(online);
}"""), skl))''', '''  BRK.keySet().retainAll(online);
  USE.keySet().retainAll(online);
  PEND.keySet().retainAll(online);
  HELD.keySet().retainAll(online);
}"""), skl))''')
rep('''    long amt = @PKG@.SkillCfg.scaled(((Long) info[0]).longValue());
''', '''    long amt = @PKG@.SkillCfg.scaled(((Long) info[0]).longValue());
    amt = @PKG@.FarmTier.apply(u, (String) info[2], (String) HELD.get(u), amt);   // 0.4.35: half XP one tier above the sickle
''')
rep('''    {PKG}.Sickle.add(u, e, w);""")''', '''    {PKG}.Sickle.HELD.put(u, h.getItemId());   // 0.4.35: the sickle of this swing (FarmTier)
    {PKG}.Sickle.add(u, e, w);""")''')
rep('''    {PKG}.SkillXp.gain(pr, (int) this.rule[0], this.rule[1]);''', '''    long bamt = this.rule[1];
    if ((int) this.rule[0] == {PKG}.SkillDefs.FARMING) bamt = {PKG}.FarmTier.breakXp(this.u, this.ev, bamt);   // 0.4.35: half XP one tier up
    {PKG}.SkillXp.gain(pr, (int) this.rule[0], bamt);''')

# ---------------------------------------------------------------- skill:fn:run (after skill:fn:level)
rep('''# ================= 0.4.34 MsgRoute: chat / feed / off per message kind (tools/skyyroute.py; SkyyHud 0.3.20+ bridge API) =================
mrt = pool.makeClass(PKG + ".MsgRoute")''', '''# ================= 0.4.35 skill:fn:run: apply(Object[]{UUID or String pkey, String skill}) -> Object[]{Integer level, Integer cap, Long run XP,
# Long XP from 0 to the cap, Boolean resets on rebirth, String saved skill name} or null (research/cloud/Rebirth-Spec.md 3.5 / 4.2). Run XP =
# the saved total (SkyySkills never caps the stored XP; a rebirth - R3 - sets it back to 0). "class" = the profile's class skill (UUID only).
# A pkey that is not loaded is read from its file under the IO lock and not kept. Any thread, never throws.
srun = pool.makeClass(PKG + ".SkillRunFn")
srun.addInterface(pool.get("java.util.function.Function"))
srun.addConstructor(CtNewConstructor.make("public SkillRunFn() { }", srun))
# fix round (critic): a String argument must be a profile key (<uuid> or <uuid>-p<n>, tools/PROFILES-CONTRACT.md) - never a path like
# ../../x that would make readFile read outside players/ (same rule as SkyyRebirth's RbStore.validKey)
srun.addMethod(CtNewMethod.make(J14(r"""
public static boolean validKey(String k) {
  return k != null && k.length() >= 36 && k.length() <= 48 && k.matches("[0-9a-fA-F-]{36}(-p[0-9]{1,4})?");
}"""), srun))
srun.addMethod(CtNewMethod.make(J14(r"""
public static Object[] readOffline(String k) {
  Object[] got;
  synchronized (@PKG@.SkillStore.IO) { got = @PKG@.SkillStore.readFile(k, null); }
  return got;
}"""), srun))
srun.addMethod(CtNewMethod.make(J14(r"""
public Object apply(Object arg) {
  try {
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 2 || a[1] == null) return null;
    java.util.UUID u = null;
    String k = null;
    if (a[0] instanceof java.util.UUID) { u = (java.util.UUID) a[0]; k = @PKG@.SkillStore.pkey(u); }
    else if (a[0] instanceof String && validKey(((String) a[0]).trim())) k = ((String) a[0]).trim();   // fix round: a profile key only (no path)
    if (k == null) return null;
    String nm = String.valueOf(a[1]).trim();
    int s;
    if ("class".equalsIgnoreCase(nm)) {
      if (u == null) return null;
      s = @PKG@.SkillClass.slot(u);
    } else {
      s = @PKG@.SkillDefs.indexOf(nm);
      if (s == @PKG@.SkillDefs.COMBAT && u != null) s = @PKG@.SkillClass.rowSlot(u, s);
    }
    if (s < 0 || s >= @PKG@.SkillDefs.N) return null;
    long[] d = (long[]) @PKG@.SkillStore.DATA.get(k);
    if (d == null && u != null) d = @PKG@.SkillStore.dataK(k, u);
    if (d == null) d = (long[]) readOffline(k)[0];
    long total = @PKG@.SkillStore.rd(d, s);
    int cap = @PKG@.SkillCap.cap(k, s);
    return new Object[] { Integer.valueOf(@PKG@.SkillDefs.levelCap(s, total, cap)), Integer.valueOf(cap), Long.valueOf(total),
                          Long.valueOf(@PKG@.SkillDefs.cumAt(s, cap)), Boolean.valueOf(@PKG@.SkillDefs.rebirthResets(s)), @PKG@.SkillDefs.NAMES[s] };
  } catch (Throwable t) { return null; }
}"""), srun))

# ================= 0.4.34 MsgRoute: chat / feed / off per message kind (tools/skyyroute.py; SkyyHud 0.3.20+ bridge API) =================
mrt = pool.makeClass(PKG + ".MsgRoute")''')

# ---------------------------------------------------------------- plugin: bridge key, shutdown, ready line
rep('''  {PKG}.SkillStore.bridge().put("skill:fn:regenblock", new {PKG}.RegenBlockFn());   // 0.4.30: SkyyArmory's Soul Bindings block natural Mana regen
''', '''  {PKG}.SkillStore.bridge().put("skill:fn:regenblock", new {PKG}.RegenBlockFn());   // 0.4.30: SkyyArmory's Soul Bindings block natural Mana regen
  {PKG}.SkillStore.bridge().put("skill:fn:run", new {PKG}.SkillRunFn());   // 0.4.35: run XP + the capped level for SkyyRebirth
''')
rep('''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:regenblock"); }} catch (Throwable t) {{ }}   // 0.4.30
''', '''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:regenblock"); }} catch (Throwable t) {{ }}   // 0.4.30
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:run"); }} catch (Throwable t) {{ }}   // 0.4.35
''')
rep('''+ "; leaderboards skip deleted / archived profiles" + ''',
    '''+ "; leaderboards skip deleted / archived profiles" + "; level caps " + ({PKG}.SkillStore.bridge().get("rebirth:fn:cap") instanceof java.util.function.Function ? "from SkyyRebirth (rebirth:fn:cap)" : "from the level tables (SkyyRebirth not loaded yet)") + ", XP past max counts (skill:fn:run), Exploration never resets" + "; Farming one or two tiers above your hoe / sickle pays x" + {PKG}.Sickle.TIER_XP + " XP (farming.tierUpXpFactor; gear:fn:farmTier " +({PKG}.SkillStore.bridge().get("gear:fn:farmTier") instanceof java.util.function.Function ? "found" : "not loaded yet") + ")" + ''')

# ---------------------------------------------------------------- write the new classes
rep('''          rbf, pset, sio, polm, mrt):   # 0.4.34: + MsgRoute;''', '''          rbf, pset, sio, polm, mrt, scap, ftr, srun):   # 0.4.35: + SkillCap, FarmTier, SkillRunFn; 0.4.34: + MsgRoute;''')

# ---------------------------------------------------------------- checks
assert s.count("SkillCap.level(") == 8, s.count("SkillCap.level(")
assert s.count("FarmTier.") >= 3
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed and not any(_o in ln for _o in OLDS if LF not in _o)]
assert not _bad, "0.4.34 lines changed outside the planned places: %r" % _bad[:5]
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.34,", len(_gone), "0.4.34 lines replaced;", len(OLDS), "anchors")
