"""Derive SkyySkills/build_skyyskills_0.4.48.py from the GENERATED SkyySkills 0.4.47 (build_skyyskills_0.4.47.py = the tools/deploy_set.py SET
pin; 0.4.47 came from 0.4.46 by tools/skills_0_4_47_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with
0.4.47 (nothing else changed); 0.4.47 stays untouched, its line endings are kept (tools/soundpass_gen.Patch).
Run:  python tools/skills_0_4_48_patch.py   then   python SkyySkills/build_skyyskills_0.4.48.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.48.py
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

NOTE = '''0.4.48 (2026-10-16) = round T1 (tool upgrades), the SkyySkills part: TOOL FORTUNE UNCAPPED (research/Collections-Tools-Redesign-Spec.md
  6.1 + 8). Skyy (docs/answered/economy.md + gear.md 2026-10-16): "(past 100% chance to drop double, it goes to a triple drop chance. so
  200% is guaranteed 3 drops. no max %)" + "i wouldnt cap either. and id make the fortune caps really high too."
  1. perk.fortuneMax default 2.0 -> 0 = NO cap (any value above 0 is still a cap; an admin's perk.doubleDropMax BELOW 1 stays a hard cap
     for tool Fortune too, exactly as 0.4.26). The code clamp Math.min(10.0, ...) went. Semantics unchanged: the whole part = sure extra
     drops, the rest a chance (1.0 = always 2 drops, 2.0 = always 3, 2.5 = 3 + 50 % of a 4th). Server Setup row max 10 -> 1000.
  2. New row perk.fortuneGuard (default 100, 1 - 10000): the most extra drops one break / harvest can give (Perks.extras clamps at it
     instead of 10) - a safety stop, not a balance cap.
  3. BULK EXTRA DROPS: n = 1 extra drop -> exactly as 0.4.47 (one doubled() with a fresh breakDrops / harvestDrops roll). n >= 2 -> ONE
     doubled() with the engine's BlockHarvestUtils.getDrops(bt, q x n, itemId, dropListId) (the same arguments breakDrops / harvestDrops
     use, quantity x n: a drop list is rolled q x n times, a direct item is one ItemStack(itemId, q x n) - bytecode 2026-10-16), stacks of
     one kind merged (ItemStack.isStackableWith) and split at the item's max stack (Item.getMaxStack, 64 if unknown). The sickle's
     per-crop Fortune does the same (its copies x n). The Fortune indicator / sound / collDouble see ONE group. Long math, quantity <= 1000000.
  4. MIGRATION Fm48Mig (PROJECT-RULES 4; Pd44Mig's reviewed machinery): ONCE on an EXISTING xp.properties (setup, right after
     Pd44Mig, before SkillCfg.load): a one-line perk.fortuneMax=2.0 (or 2) as the LAST entry of the key -> 0; an admin's other value kept
     (INFO); no line = nothing (the new code default 0 applies); config-history copy first (CfgHist.snapshot + HealMig.mgSaved), one
     config-changes.log line (Undo), the marker comment at the end (a fresh default file carries it), Properties check (only that key),
     bytes / line endings kept; a failure = WARN, file untouched, retried next start.
  No saved player data change, no new command / system. ROLLBACK to 0.4.47: 0.4.47 reads perk.fortuneMax=0 as a cap of 0, i.e. tool
  Fortune adds NOTHING above the old double-drop chance - before rolling Skills below 0.4.48 set perk.fortuneMax back to 2.0 (Server
  Setup -> Changes -> Undo); perk.fortuneGuard is ignored by 0.4.47 (harmless).
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.47.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.48.py"))
assert P.has('VERSION = "0.4.47"') and P.has("packStep") and not P.has("Fm48Mig"), "not the generated SkyySkills 0.4.47 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")


def cut(start, end):
    """the exact text of P.s from start up to and including end (start unique)"""
    assert P.s.count(start) == 1, "start anchor count %d: %s" % (P.s.count(start), start[:120])
    i = P.s.index(start)
    j = P.s.index(end, i)
    return P.s[i:j + len(end)]


def sub1(text, old, new):
    """text.replace(old, new) with old exactly once in text"""
    assert text.count(old) == 1, "inner anchor count %d: %s" % (text.count(old), old[:120])
    return text.replace(old, new, 1)


# ================================================================================================ docstring + version
P.rep('''"""SkyySkills 0.4.47 - build script (derived from the generated 0.4.46 by tools/skills_0_4_47_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.48 - build script (derived from the generated 0.4.47 by tools/skills_0_4_48_patch.py - edit the patch, not this file;
''' + NOTE + '''  CHECKED: SkyySkills/test_skyyskills_0.4.48.py.
0.4.47 was derived from the generated 0.4.46 by tools/skills_0_4_47_patch.py;
''')
P.rep('VERSION = "0.4.47"', 'VERSION = "0.4.48"')

# ================================================================================================ engine probes (the bulk extra drops)
P.rep('''MV.probe(B, pool)
''', '''MV.probe(B, pool)
for c, m in ((IS, "withQuantity"), (IS, "getItem"), (IS, "isStackableWith"), (IS, "getQuantity"), (ITM, "getMaxStack")):   # 0.4.48: Perks.bulk
    B.probe(pool, c, m)
''')

# ================================================================================================ the default file (PERK_L) + the marker
FM48_MARK_ID = "SkyySkills 0.4.48 Fortune uncapped"
P.rep('''PERK_L.append("# fortuneMax (0.4.26): the most extra-drop chance once a SkyyGear tool's Fortune is added (2 = up to two extra drops, 1 = never more than one); a doubleDropMax below 1 caps tool Fortune too")
PERK_L.append("perk.fortuneMax=2.0")
''', '''PERK_L.append("# fortuneMax (0.4.26): the most extra drops once a SkyyGear tool's Fortune is added. 0 = no cap (the 0.4.48 default).")
PERK_L.append("# The whole part gives sure extra drops, the rest is a chance: 1.0 = always 2 drops, 2.0 = always 3, 2.5 = 3 + half a 4th.")
PERK_L.append("# Any value above 0 is a cap (2 = up to two extra drops); a doubleDropMax below 1 caps tool Fortune too.")
PERK_L.append("perk.fortuneMax=0")
PERK_L.append("# fortuneGuard (0.4.48): the most extra drops one break or harvest can give - a safety stop (1 to 10000).")
PERK_L.append("perk.fortuneGuard=100")
FM48_MARK_ID = "''' + FM48_MARK_ID + '''"
FM48_MARK = "# SkyySkills 0.4.48 Fortune uncapped: fortuneMax 0 means no cap (the old default was 2.0, at most two extra drops)."
assert "=" not in FM48_MARK and ":" in FM48_MARK and len(FM48_MARK) <= 140 and all(ord(_ch) < 128 for _ch in FM48_MARK)
PERK_L.append(FM48_MARK)   # 0.4.48: Fm48Mig's run-once marker (a fresh file is never migrated)
''')

# ================================================================================================ PerkCfg: no clamp at 10, FORT_MAX 0 = no cap, GUARD
P.rep('''for _decl in ("boolean ENABLED = true", "double DD_MAX = 1.0", "double FORT_MAX = 2.0", "boolean DD_MSG = true",''',
      '''for _decl in ("boolean ENABLED = true", "double DD_MAX = 1.0", "double FORT_MAX = 0.0", "int GUARD = 100", "boolean DD_MSG = true",''')
P.rep('''  FORT_MAX = Math.min(10.0, rate(p, "perk.fortuneMax", 2.0));   // 0.4.26: the cap once a SkyyGear tool's Fortune is added
''', '''  FORT_MAX = rate(p, "perk.fortuneMax", 0.0);   // 0.4.26: the cap once a SkyyGear tool's Fortune is added; 0.4.48: default 0 = no cap, no clamp at 10
  long gd = {PKG}.SkillCfg.lng(p, "perk.fortuneGuard", 100L);   // 0.4.48: the most extra drops one break / harvest gives (1 - 10000)
  GUARD = gd < 1L ? 1 : (gd > 10000L ? 10000 : (int) gd);
''')

# ================================================================================================ Perks.fortune / extras
P.rep('''  double t = base + g;
  double cap = @PKG@.PerkCfg.DD_MAX < 1.0 ? @PKG@.PerkCfg.DD_MAX : @PKG@.PerkCfg.FORT_MAX;
  if (cap < base) cap = base;
  if (t > cap) t = cap;
  return t > 0.0 ? t : 0.0;
''', '''  double t = base + g;
  if (@PKG@.PerkCfg.DD_MAX < 1.0 || @PKG@.PerkCfg.FORT_MAX > 0.0) {   // 0.4.48: perk.fortuneMax 0 (the default) = no cap
    double cap = @PKG@.PerkCfg.DD_MAX < 1.0 ? @PKG@.PerkCfg.DD_MAX : @PKG@.PerkCfg.FORT_MAX;
    if (cap < base) cap = base;
    if (t > cap) t = cap;
  }
  return t > 0.0 ? t : 0.0;
''')
P.rep('''# (t = 0.4: one extra 40 % of the time - exactly 0.4.25's single draw; t = 1.5: one always + a second 50 %); at most 10
perk.addMethod(CtNewMethod.make(J14(r"""
public static int extras(double t, double r) {
  if (!(t > 0.0) || Double.isNaN(t)) return 0;
  if (t > 10.0) t = 10.0;
  int w = (int) Math.floor(t);
  double f = t - (double) w;
  int n = w + (r < f ? 1 : 0);
  return n > 10 ? 10 : n;
}"""), perk))
''', '''# (t = 0.4: one extra 40 % of the time - exactly 0.4.25's single draw; t = 1.5: one always + a second 50 %); 0.4.48: at most
# perk.fortuneGuard (default 100; 0.4.26 - 0.4.47: 10)
perk.addMethod(CtNewMethod.make(J14(r"""
public static int extras(double t, double r) {
  if (!(t > 0.0) || Double.isNaN(t)) return 0;
  int gd = @PKG@.PerkCfg.GUARD;
  if (gd < 1) gd = 1;
  if (t >= (double) gd) return gd;
  int w = (int) Math.floor(t);
  double f = t - (double) w;
  int n = w + (r < f ? 1 : 0);
  return n > gd ? gd : n;
}"""), perk))
''')

# ================================================================================================ Perks: the bulk drops (n >= 2 in ONE call)
P.rep('''  return {BHU}.getDrops(bt, 1, h.getItemId(), h.getDropListId());
}}""", perk))
''', '''  return {BHU}.getDrops(bt, 1, h.getItemId(), h.getDropListId());
}}""", perk))
# 0.4.48 BULK EXTRA DROPS (Collections-Tools-Redesign-Spec 8): n >= 2 extra drops = ONE fresh roll with the quantity x n (getDrops rolls a
# drop list that many times and makes one ItemStack(itemId, quantity) for a direct item - bytecode 2026-10-16), then bulk(): stacks of one
# kind merged, split at the item's max stack. PURE qtyN: q x m in long math, at most 1000000 (the guard keeps m <= 10000).
perk.addMethod(CtNewMethod.make(J14(r"""
public static int qtyN(int q, int m) {
  if (q <= 0 || m <= 0) return 0;
  long v = (long) q * (long) m;
  return v > 1000000L ? 1000000 : (int) v;
}"""), perk))
perk.addMethod(CtNewMethod.make(J14(r"""
public static java.util.List breakDropsN(@BTY@ bt, int m) {
  if (bt == null || m < 1) return null;
  @BGA@ g = bt.getGathering();
  if (g == null || toolDependent(g)) return null;
  @BBD@ br = g.getBreaking();
  if (g.isSoft()) {
    if (br != null) return null;
    @SBD@ so = g.getSoft();
    if (so == null) return null;
    return @BHU@.getDrops(bt, qtyN(1, m), so.getItemId(), so.getDropListId());
  }
  if (br == null) return null;
  int q = br.getQuantity();
  if (q <= 0) return null;
  return @BHU@.getDrops(bt, qtyN(q, m), br.getItemId(), br.getDropListId());
}"""), perk))
perk.addMethod(CtNewMethod.make(J14(r"""
public static java.util.List harvestDropsN(@BTY@ bt, int m) {
  if (bt == null || m < 1) return null;
  @BGA@ g = bt.getGathering();
  if (g == null) return null;
  @HDT@ h = g.getHarvest();
  if (h == null) return null;
  return @BHU@.getDrops(bt, qtyN(1, m), h.getItemId(), h.getDropListId());
}"""), perk))
# the item's max stack (Item.getMaxStack); unknown / below 1 / throws = 64
perk.addMethod(CtNewMethod.make(J14(r"""
public static int maxStack(@IS@ s) {
  try {
    if (s == null) return 64;
    @ITM@ it = s.getItem();
    int m = it == null ? 0 : it.getMaxStack();
    return m < 1 ? 64 : m;
  } catch (Throwable t) { return 64; }
}"""), perk))
# PURE: q split into stacks of at most mx (250, 100 -> 100, 100, 50); q <= 0 -> none
perk.addMethod(CtNewMethod.make(J14(r"""
public static int[] splitQ(long q, int mx) {
  if (q <= 0L) return new int[0];
  if (mx < 1) mx = 64;
  long c = (q + (long) mx - 1L) / (long) mx;
  int[] out = new int[(int) c];
  for (int i = 0; i < out.length; i++) {
    long take = q > (long) mx ? (long) mx : q;
    out[i] = (int) take;
    q = q - take;
  }
  return out;
}"""), perk))
# the drops of ONE bulk roll: ItemStacks of one kind (isStackableWith) merged, each kind split at its max stack; empty / non-ItemStack
# entries dropped (give() skips them anyway); null in = null out
perk.addMethod(CtNewMethod.make(J14(r"""
public static java.util.List bulk(java.util.List src) {
  if (src == null) return null;
  int n0 = src.size();
  java.util.ArrayList kinds = new java.util.ArrayList();
  long[] qs = new long[n0 > 0 ? n0 : 1];
  for (int i = 0; i < n0; i++) {
    Object o = src.get(i);
    if (!(o instanceof @IS@)) continue;
    @IS@ s = (@IS@) o;
    if (s.isEmpty() || s.getItemId() == null || s.getQuantity() <= 0) continue;
    int at = -1;
    for (int j = 0; j < kinds.size() && at < 0; j++) {
      boolean same = false;
      try { same = ((@IS@) kinds.get(j)).isStackableWith(s); } catch (Throwable t) { same = false; }
      if (same) at = j;
    }
    if (at < 0) { kinds.add(s); qs[kinds.size() - 1] = (long) s.getQuantity(); }
    else qs[at] = qs[at] + (long) s.getQuantity();
  }
  java.util.ArrayList out = new java.util.ArrayList();
  for (int j = 0; j < kinds.size(); j++) {
    @IS@ s = (@IS@) kinds.get(j);
    int[] parts = splitQ(qs[j], maxStack(s));
    for (int k = 0; k < parts.length; k++) out.add(s.withQuantity(parts[k]));
  }
  return out;
}"""), perk))
# the sickle's per-crop copies x n (fresh ItemStack(id, quantity x n), no metadata - like Sickle.copies)
perk.addMethod(CtNewMethod.make(J14(r"""
public static java.util.List timesN(java.util.List src, int m) {
  if (src == null) return null;
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < src.size(); i++) {
    Object o = src.get(i);
    if (!(o instanceof @IS@)) continue;
    @IS@ s = (@IS@) o;
    if (s.isEmpty() || s.getItemId() == null) continue;
    int q = qtyN(s.getQuantity(), m);
    if (q > 0) out.add(new @IS@(s.getItemId(), q));
  }
  return out;
}"""), perk))
''')

# ---- breakDouble / harvestDouble: n == 1 exactly as before, n >= 2 one bulk call
P.rep('''    int n = rolls(pr.getUuid(), row, {PKG}.SkillStore.level(pr.getUuid(), row), {PKG}.SkillCfg.familyId(bt));
    for (int i = 0; i < n; i++) doubled(pr, breakDrops(bt), row, world);
''', '''    int n = rolls(pr.getUuid(), row, {PKG}.SkillStore.level(pr.getUuid(), row), {PKG}.SkillCfg.familyId(bt));
    if (n == 1) doubled(pr, breakDrops(bt), row, world);
    else if (n >= 2) doubled(pr, bulk(breakDropsN(bt, n)), row, world);   // 0.4.48: ONE roll of n x the drops (not n loops)
''')
P.rep('''    int n = rolls(pr.getUuid(), row, {PKG}.SkillStore.level(pr.getUuid(), row), {PKG}.SkillCfg.familyId(bt));   // 0.4.26: + tool Fortune
    for (int i = 0; i < n; i++) doubled(pr, harvestDrops(bt), row, world);
''', '''    int n = rolls(pr.getUuid(), row, {PKG}.SkillStore.level(pr.getUuid(), row), {PKG}.SkillCfg.familyId(bt));   // 0.4.26: + tool Fortune
    if (n == 1) doubled(pr, harvestDrops(bt), row, world);
    else if (n >= 2) doubled(pr, bulk(harvestDropsN(bt, n)), row, world);   // 0.4.48: ONE roll of n x the drops (not n loops)
''')
P.rep('''      for (int q = 0; q < fx; q++) @PKG@.Perks.doubled(pr, copies((java.util.List) sg[1]), @PKG@.SkillDefs.FARMING, wn);
''', '''      if (fx == 1) @PKG@.Perks.doubled(pr, copies((java.util.List) sg[1]), @PKG@.SkillDefs.FARMING, wn);
      else if (fx >= 2) @PKG@.Perks.doubled(pr, @PKG@.Perks.bulk(@PKG@.Perks.timesN((java.util.List) sg[1], fx)), @PKG@.SkillDefs.FARMING, wn);   // 0.4.48: one bulk call
''')

# ================================================================================================ Server Setup rows
P.rep('''    ("perk.fortuneMax", "Fortune cap with tools", "perks", "dec", "2.0", "0", "10", "", "", "live",
     "Extra-drop cap with tool Fortune: 2 = up to two extra drops. Used while the cap above is 1.", "reload"),
''', '''    ("perk.fortuneMax", "Fortune cap with tools", "perks", "dec", "0", "0", "1000", "", "", "live",
     "0 = no cap. Else the tool Fortune extra-drop cap (2 = up to two). Used while the cap above is 1.", "reload"),
    # 0.4.48: the safety stop for uncapped Fortune
    ("perk.fortuneGuard", "Fortune extra drops guard", "perks", "int", "100", "1", "10000", "", "", "live,adv",
     "The most extra drops one break or harvest can give (a safety stop for uncapped Fortune).", "reload"),
''')
P.rep('''assert len(CFG_ROWS) == 271, ("0.4.44: + acro.rollKey''', '''assert len(CFG_ROWS) == 272, ("0.4.48: + perk.fortuneGuard; 0.4.44: + acro.rollKey''')
P.rep('''assert DEFAULTS.count(PD44_MARK_ID) == 1 and _dp.get("acro.perfectDodge.windowMs") == "100" and _dp.get("ranching.maxXpPerMinute") == "1000000"
''', '''assert DEFAULTS.count(PD44_MARK_ID) == 1 and _dp.get("acro.perfectDodge.windowMs") == "100" and _dp.get("ranching.maxXpPerMinute") == "1000000"
assert DEFAULTS.count(FM48_MARK_ID) == 1 and _dp.get("perk.fortuneMax") == "0" and _dp.get("perk.fortuneGuard") == "100"   # 0.4.48
_k48 = [_r[0] for _r in CFG_ROWS]
assert _k48.index("perk.fortuneGuard") == _k48.index("perk.fortuneMax") + 1 and _k48.count("perk.fortuneGuard") == 1
''')

# ================================================================================================ Fm48Mig (Pd44Mig's machinery, one key)
P.rep('''pd44 = pool.makeClass(PKG + ".Pd44Mig")        # 0.4.44: the one-time perfect dodge 50 -> 100 ms + XP caps -> 1000000 update of an existing xp.properties
''', '''pd44 = pool.makeClass(PKG + ".Pd44Mig")        # 0.4.44: the one-time perfect dodge 50 -> 100 ms + XP caps -> 1000000 update of an existing xp.properties
fm48 = pool.makeClass(PKG + ".Fm48Mig")        # 0.4.48: the one-time perk.fortuneMax 2.0 -> 0 (no cap) update of an existing xp.properties
''')
PD = cut('''pd44.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(PD44_MARK_ID), pd44))''',
         '''    @PKG@.SkillCfg.warn("could not update xp.properties for 0.4.44 (perfect dodge 100 ms, XP caps; the file is used as it is): " + t);
    return "";
  }
}"""), pd44))
''')
FM = PD
FM = sub1(FM, '''pd44.addField(CtField.make('public static final String[] KEYS = new String[] { "acro.perfectDodge.windowMs", "acro.perfectDodge.maxXpPerMinute", "ranching.maxXpPerMinute" };', pd44))
pd44.addField(CtField.make('public static final String[] OLDS = new String[] { "50", "50", "200" };', pd44))
pd44.addField(CtField.make('public static final String[] NEWS = new String[] { "100", "1000000", "1000000" };', pd44))
pd44.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.44";', pd44))
assert ("\\n" + DEFAULTS).count("\\nacro.perfectDodge.windowMs=100\\n") == 1 and ("\\n" + DEFAULTS).count("\\nranching.maxXpPerMinute=1000000\\n") == 1
''', '''pd44.addField(CtField.make('public static final String[] KEYS = new String[] { "perk.fortuneMax" };', pd44))
pd44.addField(CtField.make('public static final String[] OLDS = new String[] { "2.0" };', pd44))
pd44.addField(CtField.make('public static final String[] ALTS = new String[] { "2" };', pd44))   # the old default written as 2
pd44.addField(CtField.make('public static final String[] NEWS = new String[] { "0" };', pd44))
pd44.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.48";', pd44))
assert ("\\n" + DEFAULTS).count("\\nperk.fortuneMax=0\\n") == 1
''')
FM = sub1(FM, '''  return -1;
}"""), pd44))
''', '''  return -1;
}"""), pd44))
# the old default, as written by 0.4.26 - 0.4.47 (2.0) or by hand (2)
pd44.addMethod(CtNewMethod.make(J14(r"""
public static boolean isOld(int x, String v) {
  if (x < 0 || x >= KEYS.length || v == null) return false;
  return v.equals(OLDS[x]) || v.equals(ALTS[x]);
}"""), pd44))
''')
FM = sub1(FM, "mig[i] = eff[i] != null && !multi[i] && eff[i].equals(OLDS[i]);", "mig[i] = eff[i] != null && !multi[i] && isOld(i, eff[i]);")
FM = sub1(FM, "if (mig[i]) { rows.add(KEYS[i]); rows.add(OLDS[i]); rows.add(NEWS[i]); }", "if (mig[i]) { rows.add(KEYS[i]); rows.add(eff[i]); rows.add(NEWS[i]); }")
FM = sub1(FM, '''" kept (an admin's value) - the 0.4.44 default is " + NEWS[i]''', '''" kept (an admin's value) - the 0.4.48 default is " + NEWS[i] + " (no cap)"''')
FM = sub1(FM, "@PKG@.CfgFile.value(l, k).trim().equals(OLDS[x2])", "isOld(x2, @PKG@.CfgFile.value(l, k).trim())")
FM = FM.replace("perfect dodge 100 ms, XP caps", "tool Fortune uncapped").replace("perfect dodge / XP cap update", "Fortune cap update")
FM = FM.replace("0.4.44", "0.4.48").replace("PD44_MARK", "FM48_MARK").replace("pd44", "fm48")
assert "dodge" not in FM and "Pd44" not in FM and "0.4.44" not in FM, "Fm48Mig: a Pd44Mig leftover"
P.rep(PD, PD + '''
# ---- Fm48Mig (0.4.48, PROJECT-RULES section 4; Pd44Mig's reviewed machinery, one key): ONCE on an EXISTING xp.properties, setup() right
# after Pd44Mig.run, BEFORE SkillCfg.load. Nothing to do = no file or a comment line holding MARK_ID. When the LAST perk.fortuneMax entry
# is a one-line entry holding exactly the old default (2.0, or 2), every such one-line entry -> 0 (no cap; value text only); any other value
# kept (INFO); NO line = nothing (the new code default 0 applies). The marker goes at the end; config-history copy first; one
# config-changes.log line (Undo); Properties check (only that key differs); atomicWrite. A failure = WARN, file untouched, retried next start.
''' + FM)
P.rep('''  {PKG}.Pd44Mig.run();        // 0.4.44: untouched perfect dodge 50 ms / caps 50 / 200 -> 100 ms / 1000000, once; History first
''', '''  {PKG}.Pd44Mig.run();        // 0.4.44: untouched perfect dodge 50 ms / caps 50 / 200 -> 100 ms / 1000000, once; History first
  {PKG}.Fm48Mig.run();        // 0.4.48: untouched perk.fortuneMax 2.0 -> 0 (tool Fortune uncapped), once; History first
''')

# ================================================================================================ T1 critic note: bulk extra drops stay OUT of Collections
P.rep('''  DD_COLLECTIONS = {PKG}.SkillCfg.bool(p, "collections.doubleDrops", false);''',
      '''  DD_COLLECTIONS = {PKG}.SkillCfg.bool(p, "collections.doubleDrops", false);   // 0.4.48 (T1 critic): stays OFF by default - Fortune's bulk extra drops never count in SkyyCollections, so they never raise collection tool points (coll:fn:toolPts)''')

# ================================================================================================ write the new class
P.rep('''          rbcm, snd39, rbs39, pd44,
          hubb, hopen, fort42, ftask42, hpr43, hprfn43, even43):   # 0.4.43:''', '''          rbcm, snd39, rbs39, pd44, fm48,
          hubb, hopen, fort42, ftask42, hpr43, hprfn43, even43):   # 0.4.48: + Fm48Mig; 0.4.43:''')

# ================================================================================================ the ready line
P.rep('''"; tool Fortune (SkyyGear skill:bonus source gear) up to " + {PKG}.DivCfg.num({PKG}.PerkCfg.FORT_MAX) + " extra drops in total; ''',
      '''"; tool Fortune (SkyyGear skill:bonus source gear) " + ({PKG}.PerkCfg.FORT_MAX > 0.0 ? "up to " + {PKG}.DivCfg.num({PKG}.PerkCfg.FORT_MAX) + " extra drops in total" : "uncapped") + " (guard " + {PKG}.PerkCfg.GUARD + " extra drops a break, n extra drops = one bulk roll); ''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
