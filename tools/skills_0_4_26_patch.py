"""Derive SkyySkills/build_skyyskills_0.4.26.py from the LIVE generated SkyySkills/build_skyyskills_0.4.25.py (= the tools/deploy_set.py SET
pin; 0.4.25 came from 0.4.24 by tools/skills_0_4_25_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_25_patch.py: rep(old, new) with asserted single anchors, newline-agnostic; 0.4.25
stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_26_patch.py   then   python SkyySkills/build_skyyskills_0.4.26.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.26.py   (bare JVM, -Xverify:all; scratch tools/dev/scratch/tools01/skills0426, deleted)

0.4.26 = TOOL FORTUNE + skill:dmg (Skyy 2026-10-05 "axes and pickaxes have the levels, now they need to actually do something." + 2026-10-09
"tools still dont have chopping speed, and foraging fortune. or tree feller"; SkyyGear 0.2.12 is the other half - tools/gear_0_2_12_patch.py):
(1) TOOL FORTUNE REUSES THE DOUBLE-DROP PATH ("reused, never a second system"): SkyyGear 0.2.12 posts the held gathering tool's Fortune as
    source "gear" in the shared skill:bonus:<uuid> map (dd.<skill> = Fortune / 100; 1 Fortune = +1 % chance of one extra drop, SkyBlock
    style). Perks.fortune = the live double-drop chance WITHOUT that source (level perk + every other source - the trees -, capped at
    perk.doubleDropMax exactly as before) + the tool's part, capped at the NEW row perk.fortuneMax (default 2.0 = up to two extra drops;
    1.0 = the old "never above one"; a tool never pushes the total below the old chance; fix round: a perk.doubleDropMax below 1 stays a
    hard cap for the tool part too, perk.fortuneMax only applies while doubleDropMax is 1). The tool part only counts on the blocks the
    source's only.<skill> names (SkyyGear: pickaxe Rock_ / Rubble_ / Ore_, shovel Soil_ = sand + gravel; fix round, critic B1). Perks.extras: the whole part = guaranteed extra
    drops, the rest = a chance for one more (1.5 = one sure + 50 %). The three roll sites (breakDouble: broken blocks + felled logs;
    harvestDouble: F-harvest; the sickle swing) now give the drops that many times (each extra is rolled again, like the second drop
    always was). Placed blocks never double (breakDouble's tracked rule, counted in FN[2]); doubleDropOnly (Foraging: _Trunk = logs only)
    still filters. Without SkyyGear 0.2.12 (no "gear" source) every roll is exactly 0.4.25's (one draw against the same chance).
(2) skill:dmg:<uuid> = the class balance damage % of the active profile's class at its class level (ClassPower table 6, the number
    CombatDmgSys already adds - 0.4.25 ClassPower.boostDmg) as a Double PERCENT, same rules as skill:def:<uuid>: set by Perks.tick every
    second, rounded to 0.01, removed at 0 and when the player leaves (SkillDef.retain). For a later SkyyMenu Stats row.
New row perk.fortuneMax (Server Setup -> Skills -> Perks; a fresh xp.properties lists it under perk.doubleDropMax). A live file without the
line reads the default 2.0 - no one-time update, no live default changes. No new class, system, command or saved data. Rolling back to
0.4.25 is safe (SkyyGear's "gear" source then counts inside perk.doubleDropMax like a tree source; skill:dmg stops being published).
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.25.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.26.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.25"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.25"' in s and "derived from the generated 0.4.24 by tools/skills_0_4_25_patch.py" in s, "not the live generated 0.4.25"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
for _x in ("perk.fortuneMax", "FORT_MAX", "skill:dmg:", "ddExcept"):
    assert _x not in s, "0.4.25 already has " + _x
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
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


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyySkills 0.4.25 - build script (derived from the generated 0.4.24 by tools/skills_0_4_25_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.26 - build script (derived from the generated 0.4.25 by tools/skills_0_4_26_patch.py - edit the patch, not this file;
0.4.25 was derived from the generated 0.4.24 by tools/skills_0_4_25_patch.py; ''')
rep('''0.4.25: THE CLASS POWER SPLIT + SKILL STAT PERKS (Skyy 2026-10-08, docs/answered/skills.md; research/Class-Power-Split.md; full notes in
''', '''0.4.26: TOOL FORTUNE + skill:dmg (Skyy 2026-10-05 / 2026-10-09 "tools still dont have chopping speed, and foraging fortune"; full notes in
  tools/skills_0_4_26_patch.py; the other half is SkyyGear 0.2.12). The held tool's Fortune (SkyyGear's skill:bonus source "gear") is
  rolled through the SAME double-drop path: the whole part = guaranteed extra drops, the rest a chance (new row perk.fortuneMax, default 2);
  without SkyyGear 0.2.12 every roll is 0.4.25's. Placed blocks never double. skill:dmg:<uuid> = the class balance damage % (Double, the
  skill:def rules) for a later SkyyMenu Stats row. No migration (a missing perk.fortuneMax line = its default), no new class / system.
0.4.25: THE CLASS POWER SPLIT + SKILL STAT PERKS (Skyy 2026-10-08, docs/answered/skills.md; research/Class-Power-Split.md; full notes in
''')
rep('VERSION = "0.4.25"', 'VERSION = "0.4.26"')
rep('''sickle swings pay Farming XP and roll double drops (Server Setup).''',
    '''sickle swings pay Farming XP and roll double drops (Server Setup); a SkyyGear tool's Fortune adds extra drops through the same perk (above 100 = a sure extra drop).''')

# ---------------------------------------------------------------------------------------------------------------- the row + the fresh file
rep('''PERK_L.append("perk.doubleDropMax=1.0")
''', '''PERK_L.append("perk.doubleDropMax=1.0")
PERK_L.append("# fortuneMax (0.4.26): the most extra-drop chance once a SkyyGear tool's Fortune is added (2 = up to two extra drops, 1 = never more than one); a doubleDropMax below 1 caps tool Fortune too")
PERK_L.append("perk.fortuneMax=2.0")
''')
rep('''    ("perk.doubleDropMax", "Double drop chance cap", "perks", "dec", "1.0", "0", "1", "", "", "live",
     "The double-drop chance never goes above this (1 = 100%), tree Fortune included.", "reload"),
''', '''    ("perk.doubleDropMax", "Double drop chance cap", "perks", "dec", "1.0", "0", "1", "", "", "live",
     "Double-drop chance cap (1 = 100%), tree Fortune included. Below 1 it caps tool Fortune too.", "reload"),
    # 0.4.26: the cap once a SkyyGear tool's Fortune is added (whole part = sure extra drops, the rest a chance)
    ("perk.fortuneMax", "Fortune cap with tools", "perks", "dec", "2.0", "0", "10", "", "", "live",
     "Extra-drop cap with tool Fortune: 2 = up to two extra drops. Used while the cap above is 1.", "reload"),
''')
rep('assert len(CFG_ROWS) == 227, ("0.4.5 had', 'assert len(CFG_ROWS) == 228, ("0.4.26: + perk.fortuneMax; 0.4.5 had')
rep('''for _decl in ("boolean ENABLED = true", "double DD_MAX = 1.0", "boolean DD_MSG = true",''',
    '''for _decl in ("boolean ENABLED = true", "double DD_MAX = 1.0", "double FORT_MAX = 2.0", "boolean DD_MSG = true",''')
rep('''  DD_MAX = Math.min(1.0, rate(p, "perk.doubleDropMax", 1.0));
''', '''  DD_MAX = Math.min(1.0, rate(p, "perk.doubleDropMax", 1.0));
  FORT_MAX = Math.min(10.0, rate(p, "perk.fortuneMax", 2.0));   // 0.4.26: the cap once a SkyyGear tool's Fortune is added
''')

# ---------------------------------------------------------------------------------------------------------------- SkillBonus: split the "gear" source
after('''public static double dd(java.util.UUID u, int row) {{
  if (row < 0 || row > {PKG}.SkillDefs.FARMING) return 0.0;
  double s = sum(u, "dd." + key(row));
  if (s <= 0.0) return 0.0;
  return s > 1.0 ? 1.0 : s;
}}""", sbn))
''', '''# 0.4.26 TOOL FORTUNE: one source's dd.<skill> (the "gear" source = SkyyGear 0.2.12's held tool Fortune / 100), 0..100; 0 with
# bridge.bonus.enabled=false like every source
sbn.addMethod(CtNewMethod.make(J14(r"""
public static double ddOf(java.util.UUID u, int row, String src) {
  if (u == null || src == null || row < 0 || row > @PKG@.SkillDefs.FARMING || !@PKG@.BridgeCfg.BONUS) return 0.0;
  java.util.Map m = sources(u);
  if (m == null) return 0.0;
  try {
    Object v = m.get(src);
    if (!(v instanceof java.util.Map)) return 0.0;
    Object n = ((java.util.Map) v).get("dd." + key(row));
    if (!(n instanceof Number)) return 0.0;
    double d = ((Number) n).doubleValue();
    if (Double.isNaN(d) || Double.isInfinite(d) || !(d > 0.0)) return 0.0;
    return d > 100.0 ? 100.0 : d;
  } catch (Throwable t) { return 0.0; }
}"""), sbn))
# 0.4.26 fix round (critic B1): a source's only.<skill> = the block ids its dd.<skill> counts on (comma list, matched like
# perk.<skill>.doubleDropOnly); null = every block of that skill. SkyyGear posts it for pickaxes (rock + ore) and shovels (sand + gravel).
sbn.addMethod(CtNewMethod.make(J14(r"""
public static String onlyOf(java.util.UUID u, int row, String src) {
  if (u == null || src == null || row < 0 || row > @PKG@.SkillDefs.FARMING) return null;
  java.util.Map m = sources(u);
  if (m == null) return null;
  try {
    Object v = m.get(src);
    if (!(v instanceof java.util.Map)) return null;
    Object o = ((java.util.Map) v).get("only." + key(row));
    if (!(o instanceof String)) return null;
    String t = ((String) o).trim();
    return t.length() == 0 ? null : t;
  } catch (Throwable t) { return null; }
}"""), sbn))
# 0.4.26: dd.<skill> of every OTHER source (the trees ...), clamped 0..1 like dd - so the old double-drop chance is unchanged
sbn.addMethod(CtNewMethod.make(J14(r"""
public static double ddExcept(java.util.UUID u, int row, String src) {
  if (u == null || row < 0 || row > @PKG@.SkillDefs.FARMING || !@PKG@.BridgeCfg.BONUS) return 0.0;
  java.util.Map m = sources(u);
  if (m == null) return 0.0;
  String k = "dd." + key(row);
  double s = 0.0;
  try {
    java.util.Iterator it = m.keySet().iterator();
    while (it.hasNext()) {
      Object sk = it.next();
      if (src != null && src.equals(sk)) continue;
      Object v = m.get(sk);
      if (!(v instanceof java.util.Map)) continue;
      Object n = ((java.util.Map) v).get(k);
      if (!(n instanceof Number)) continue;
      double d = ((Number) n).doubleValue();
      if (Double.isNaN(d) || Double.isInfinite(d)) continue;
      s = s + d;
    }
  } catch (Throwable t) { return 0.0; }
  if (s <= 0.0) return 0.0;
  return s > 1.0 ? 1.0 : s;
}"""), sbn))
''')

# ---------------------------------------------------------------------------------------------------------------- Perks: fortune / extras / rolls
rep('''perk.addField(CtField.make("public static boolean DD_FAILED_ONCE = false;", perk))
''', '''perk.addField(CtField.make("public static boolean DD_FAILED_ONCE = false;", perk))
# 0.4.26 counters: 0 rolls with a chance, 1 extra drops given out (whole + chance), 2 placed blocks refused (never double)
perk.addField(CtField.make("public static final long[] FN = new long[3];", perk))
''')
after('''public static double chanceU(java.util.UUID u, int row, int lvl) {{
  if (row < 0 || row > {PKG}.SkillDefs.FARMING) return 0.0;
  double c = chance(row, lvl) + {PKG}.SkillBonus.dd(u, row);
  if (c > {PKG}.PerkCfg.DD_MAX) c = {PKG}.PerkCfg.DD_MAX;
  return c < 0.0 ? 0.0 : c;
}}""", perk))
''', '''# 0.4.26 TOOL FORTUNE (tools/skills_0_4_26_patch.py): the total extra-drop chance = the 0.4.25 chance without the "gear" source (level perk +
# every other source, capped at perk.doubleDropMax as before) + SkyyGear's held tool Fortune / 100, capped at perk.fortuneMax (never below
# the old chance). 1.5 = one sure extra drop + 50 % for a second one.
# Fix round: (critic B1) the tool part only counts on the blocks SkyyGear's only.<skill> names (a shovel never on stone / ore; fam null =
# not on a filtered tool); (critics A1/B2) an admin's perk.doubleDropMax BELOW 1 stays a hard cap for tool Fortune too - perk.fortuneMax
# only widens the cap while doubleDropMax is at its 1.0 maximum.
perk.addMethod(CtNewMethod.make(J14(r"""
public static boolean onlyHit(String o, String fam) {
  if (o == null) return true;
  if (fam == null) return false;
  String[] ps = o.split(",");
  for (int i = 0; i < ps.length; i++) {
    String p = ps[i].trim();
    if (p.length() > 0 && fam.indexOf(p) >= 0) return true;
  }
  return false;
}"""), perk))
perk.addMethod(CtNewMethod.make(J14(r"""
public static double fortune(java.util.UUID u, int row, int lvl, String fam) {
  if (row < 0 || row > @PKG@.SkillDefs.FARMING) return 0.0;
  double base = chance(row, lvl) + @PKG@.SkillBonus.ddExcept(u, row, "gear");
  if (base > @PKG@.PerkCfg.DD_MAX) base = @PKG@.PerkCfg.DD_MAX;
  if (!(base > 0.0)) base = 0.0;
  double g = @PKG@.SkillBonus.ddOf(u, row, "gear");
  if (g > 0.0 && !onlyHit(@PKG@.SkillBonus.onlyOf(u, row, "gear"), fam)) g = 0.0;
  double t = base + g;
  double cap = @PKG@.PerkCfg.DD_MAX < 1.0 ? @PKG@.PerkCfg.DD_MAX : @PKG@.PerkCfg.FORT_MAX;
  if (cap < base) cap = base;
  if (t > cap) t = cap;
  return t > 0.0 ? t : 0.0;
}"""), perk))
# without a block (fam null): a filtered tool part never counts
perk.addMethod(CtNewMethod.make(J14(r"""
public static double fortune(java.util.UUID u, int row, int lvl) {
  return fortune(u, row, lvl, (String) null);
}"""), perk))
# PURE: how many extra drops a total chance t gives for a uniform draw r in [0,1): the whole part always + one more when r < the rest
# (t = 0.4: one extra 40 % of the time - exactly 0.4.25's single draw; t = 1.5: one always + a second 50 %); at most 10
perk.addMethod(CtNewMethod.make(J14(r"""
public static int extras(double t, double r) {
  if (!(t > 0.0) || Double.isNaN(t)) return 0;
  if (t > 10.0) t = 10.0;
  int w = (int) Math.floor(t);
  double f = t - (double) w;
  int n = w + (r < f ? 1 : 0);
  return n > 10 ? 10 : n;
}"""), perk))
''')
rep('''# tracked = the block cannot have been placed by a player (ripe crops, or the placed-block tracker is on and cleared it)
perk.addMethod(CtNewMethod.make(f"""
public static void breakDouble({PR} pr, int row, {BTY} bt, String world, boolean tracked) {{
  try {{
    if (!tracked || row < 0 || row > {PKG}.SkillDefs.FARMING || bt == null) return;
    double c = chanceU(pr.getUuid(), row, {PKG}.SkillStore.level(pr.getUuid(), row));
    if (c <= 0.0 || !matches(row, {PKG}.SkillCfg.familyId(bt))) return;
    if (java.util.concurrent.ThreadLocalRandom.current().nextDouble() >= c) return;
    doubled(pr, breakDrops(bt), row, world);
  }} catch (Throwable t) {{''', '''# 0.4.26: how many extra drops this break / harvest gives (0.4.25 drew once against chanceU; this draws once against Perks.fortune)
perk.addMethod(CtNewMethod.make(J14(r"""
public static int rolls(java.util.UUID u, int row, int lvl, String fam) {
  double t = fortune(u, row, lvl, fam);
  if (!(t > 0.0) || !matches(row, fam)) return 0;
  int n = extras(t, java.util.concurrent.ThreadLocalRandom.current().nextDouble());
  FN[0] = FN[0] + 1L;
  FN[1] = FN[1] + (long) n;
  return n;
}"""), perk))
# tracked = the block cannot have been placed by a player (ripe crops, or the placed-block tracker is on and cleared it)
perk.addMethod(CtNewMethod.make(f"""
public static void breakDouble({PR} pr, int row, {BTY} bt, String world, boolean tracked) {{
  try {{
    if (!tracked) {{ FN[2] = FN[2] + 1L; return; }}   // 0.4.26: placed blocks never double (counted for the harness)
    if (row < 0 || row > {PKG}.SkillDefs.FARMING || bt == null) return;
    int n = rolls(pr.getUuid(), row, {PKG}.SkillStore.level(pr.getUuid(), row), {PKG}.SkillCfg.familyId(bt));
    for (int i = 0; i < n; i++) doubled(pr, breakDrops(bt), row, world);
  }} catch (Throwable t) {{''')
rep('''    int row = {PKG}.SkillDefs.FARMING;
    if (bt == null) return;
    double c = chanceU(pr.getUuid(), row, {PKG}.SkillStore.level(pr.getUuid(), row));
    if (c <= 0.0 || !matches(row, {PKG}.SkillCfg.familyId(bt))) return;
    if (java.util.concurrent.ThreadLocalRandom.current().nextDouble() >= c) return;
    doubled(pr, harvestDrops(bt), row, world);''', '''    int row = {PKG}.SkillDefs.FARMING;
    if (bt == null) return;
    int n = rolls(pr.getUuid(), row, {PKG}.SkillStore.level(pr.getUuid(), row), {PKG}.SkillCfg.familyId(bt));   // 0.4.26: + tool Fortune
    for (int i = 0; i < n; i++) doubled(pr, harvestDrops(bt), row, world);''')
rep('''      double c = @PKG@.Perks.chanceU(u, @PKG@.SkillDefs.FARMING, @PKG@.SkillStore.level(u, @PKG@.SkillDefs.FARMING));
      if (c > 0.0 && @PKG@.Perks.matches(@PKG@.SkillDefs.FARMING, (String) info[2]) && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < c)
        @PKG@.Perks.doubled(pr, copies((java.util.List) sg[1]), @PKG@.SkillDefs.FARMING, wn);''',
    '''      int fx = @PKG@.Perks.rolls(u, @PKG@.SkillDefs.FARMING, @PKG@.SkillStore.level(u, @PKG@.SkillDefs.FARMING), (String) info[2]);   // 0.4.26: + tool Fortune
      for (int q = 0; q < fx; q++) @PKG@.Perks.doubled(pr, copies((java.util.List) sg[1]), @PKG@.SkillDefs.FARMING, wn);''')

# ---------------------------------------------------------------------------------------------------------------- skill:dmg:<uuid>
after('''public static double boostDef(java.util.UUID u, long[] d) {
  try {
    String cls = @PKG@.Overall.classOf(u);
    return boost(5, cls, classLevel(cls, d));
  } catch (Throwable t) { return 0.0; }
}"""), cpw))
''', '''# 0.4.26 skill:dmg:<uuid>: the class balance damage % (table 6, what CombatDmgSys adds through boostDmg) of the active profile's class at its
# class level - a PERCENT (5.0 = +5 %), 0 without a class / with the balance off
cpw.addMethod(CtNewMethod.make(J14(r"""
public static double dmgPct(java.util.UUID u, long[] d) {
  try {
    String cls = @PKG@.Overall.classOf(u);
    return boost(6, cls, classLevel(cls, d));
  } catch (Throwable t) { return 0.0; }
}"""), cpw))
''')
rep('''for _d in ("public static final java.util.concurrent.ConcurrentHashMap DEF = new java.util.concurrent.ConcurrentHashMap();",
''', '''for _d in ("public static final java.util.concurrent.ConcurrentHashMap DEF = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap DMGP = new java.util.concurrent.ConcurrentHashMap();",   # 0.4.26 skill:dmg
''')
after('''  Double dv = Double.valueOf(x);
  DEF.put(u, dv);
  if (!dv.equals(br.get(k))) br.put(k, dv);
}"""), sdef))
''', '''# 0.4.26 skill:dmg:<uuid> = the class balance damage % (Double), the skill:def rules: rounded to 0.01, removed at 0 and when the player leaves
sdef.addMethod(CtNewMethod.make(J14(r"""
public static void setDmg(java.util.UUID u, double v) {
  if (u == null) return;
  double x = (Double.isNaN(v) || Double.isInfinite(v) || v < 0.0) ? 0.0 : (v > 100000.0 ? 100000.0 : v);
  x = (double) Math.round(x * 100.0) / 100.0;
  String k = "skill:dmg:" + u.toString();
  java.util.Map br = @PKG@.SkillStore.bridge();
  if (!(x > 0.0)) {
    DMGP.remove(u);
    br.remove(k);
    return;
  }
  Double dv = Double.valueOf(x);
  DMGP.put(u, dv);
  if (!dv.equals(br.get(k))) br.put(k, dv);
}"""), sdef))
sdef.addMethod(CtNewMethod.make(J14(r"""
public static double dmgOf(java.util.UUID u) {
  Object o = u == null ? null : DMGP.get(u);
  return o instanceof Double ? ((Double) o).doubleValue() : 0.0;
}"""), sdef))
''')
rep('''    if (online.contains(u)) continue;
    DEF.remove(u);
    br.remove("skill:def:" + u.toString());
  }
}"""), sdef))''', '''    if (online.contains(u)) continue;
    DEF.remove(u);
    br.remove("skill:def:" + u.toString());
  }
  java.util.Iterator it2 = new java.util.ArrayList(DMGP.keySet()).iterator();   // 0.4.26 skill:dmg:<uuid>
  while (it2.hasNext()) {
    Object u2 = it2.next();
    if (online.contains(u2)) continue;
    DMGP.remove(u2);
    br.remove("skill:dmg:" + u2.toString());
  }
}"""), sdef))''')
rep('''    {PKG}.SkillDef.set(u, (double) total({PKG}.PerkCfg.DEF, lv) + {PKG}.ClassPower.boostDef(u, {PKG}.SkillStore.data(u)));   // 0.4.25: skill Defense
''', '''    {PKG}.SkillDef.set(u, (double) total({PKG}.PerkCfg.DEF, lv) + {PKG}.ClassPower.boostDef(u, {PKG}.SkillStore.data(u)));   // 0.4.25: skill Defense
    {PKG}.SkillDef.setDmg(u, {PKG}.ClassPower.dmgPct(u, {PKG}.SkillStore.data(u)));   // 0.4.26: skill:dmg:<uuid> (class balance damage %)
''')
rep('''+ {PKG}.SkillDef.text() + "; leaderboards skip deleted / archived profiles"''',
    '''+ {PKG}.SkillDef.text() + "; tool Fortune (SkyyGear skill:bonus source gear) up to " + {PKG}.DivCfg.num({PKG}.PerkCfg.FORT_MAX) + " extra drops in total; bridge skill:dmg:<uuid> (class balance damage %)" + "; leaderboards skip deleted / archived profiles"''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "0.4.26 adds no system and no command"
assert "chanceU(pr.getUuid()" not in s and "Perks.chanceU(u, @PKG@.SkillDefs.FARMING" not in s, "a roll site still draws against chanceU"
_ix = s.index
assert _ix("public static double ddExcept(") < _ix("public static double fortune(java.util.UUID u, int row, int lvl)") < _ix("public static int rolls(")
assert _ix("public static boolean matches(int row, String fam)") < _ix("public static int rolls(") < _ix("public static void breakDouble(")
assert _ix("public static double dmgPct(") < _ix("{PKG}.SkillDef.setDmg(u, {PKG}.ClassPower.dmgPct(")
assert _ix("public static void setDmg(") < _ix("{PKG}.SkillDef.setDmg(u, {PKG}.ClassPower.dmgPct(")
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed]
assert not _bad, "0.4.25 lines changed outside the planned places: %r" % _bad[:5]
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.25,", len(_gone), "0.4.25 lines replaced,",
      sum(op[4] - op[3] for op in _hunks) - len(_gone), "lines added net;", len(OLDS), "anchors")
