"""Derive SkyySkills/build_skyyskills_0.4.38.py from the LIVE generated SkyySkills/build_skyyskills_0.4.37.py (= the tools/deploy_set.py SET
pin; 0.4.37 came from 0.4.36 by tools/skills_0_4_37_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; 0.4.37 stays untouched, its line endings are kept.
Run:  python tools/skills_0_4_38_patch.py   then   python SkyySkills/build_skyyskills_0.4.38.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.38.py --dir tools/dev/scratch/<yours>/sk   (bare JVM, -Xverify:all)

0.4.38 (2026-10-14) = ECONOMY ROUND econ38, the SkyySkills part (Skyy's popup 2026-10-14 "0.8 per rebirth (Recommended)" -
docs/answered/economy.md 2026-10-14 REBIRTH coin factor; Skyy 2026-10-14 "Run everything you can in parallel" = the RESUME Next list):
  (1) REBIRTH LEVEL COINS x0.8: rebirth.coinFactor default 0.9 -> 0.8 (80 % after rebirth 1, 64 % after 2 ... ~11 % after 10): the
      fresh xp.properties line, the code defaults (SkillCfg.RB_COIN, a bad / missing number) and the Server Setup row default. ONE-TIME
      MIGRATION RbCoinMig (PROJECT-RULES section 4; PollMig's reviewed machinery): ONCE on an EXISTING xp.properties, in setup() right
      after PollMig.run and BEFORE SkillCfg.load / CfgPub.start. Nothing to do = no file (load() writes the 0.4.38 default, marker
      included) or a comment line holding the marker id (done before). Else, per logical line (the kit's own parser):
        - rebirth.coinFactor whose LAST entry is a one-line entry holding exactly 0.9 (the old default) -> every such one-line entry 0.8
          (value text only; key, separator, CR kept);
        - NO rebirth.coinFactor line at all (a file from before 0.4.36 - the live test world's file: it read the 0.9 code default) ->
          the line rebirth.coinFactor=0.8 is APPENDED (the old effective value was the untouched default);
        - any other value (an admin's choice, a continued entry) is KEPT (an INFO line).
      Either change = one config-changes.log line rebirth.coinFactor 0.9 -> 0.8 (Server Setup -> Changes -> Undo = 0.9). The marker
      comment goes right under the (last) rebirth.coinFactor entry (or the appended one), in the file's own line ending. Properties
      check (only rebirth.coinFactor differs / is added), config-history copy FIRST (verified), atomicWrite. A failure = WARN, the
      file is untouched and the next start tries again. Profiles' saved data is never touched (coins already paid stay paid; the
      factor applies to the NEXT level-up coins after a rebirth).
  (2) /skills SHOWS FISHING, RANCHING AND ORCHARD (0.4.37 left them out for room): the overview lists 12 rows - Mining, Foraging,
      Farming, Fishing, Ranching, Orchard, Alchemy, Smithing, Cooking, Acrobatics, Exploration, the class row (SkillDefs.ROW_SLOTS =
      SKILL_ROW_SLOTS, one Python list for the rows and the list-well budget). Same vanilla kit rows (62 px, the Acrobatics row 82 px);
      the page grows 786 -> 973 px high (the kit ceiling is 980: fits a 1080 screen with the window ornaments) by the 3 rows and two
      8 px gaps made 4 px (under the Overall well, above the hint). Each new row has its STATS button (the Stats page of that skill,
      0.4.37 already draws it); no TREE button yet (SkyyTrees has no Fishing tree; Ranching / Orchard share the Farming tree - the
      Farming row's TREE button). The Top 10 view gets the extra height for its list well.
  (3) REBIRTH FACTS FOR THE FARMING ARM: the participant's facts (measure / prepare) add arm.ranching and arm.orchard (run XP / XP to
      the cap / level / cap of those slots, the arm.farming format). Additive: SkyyRebirth 0.3 reads arm.<its 8 arms> only and ignores
      them; SkyyRebirth 0.3.1+ feeds its Farming arm from arm.farming + arm.ranching + arm.orchard (research/Gathering-Shards-Spec.md
      5.3 "one shared Farming tree"). Nothing else in the participant changes (x.<slot> lines, commit, abort, status, backups).
  ROLLBACK to 0.4.37: safe. 0.4.37 reads rebirth.coinFactor=0.8 from the file as the admin's value (keeps 0.8); its /skills shows 9
  rows again; a staged rebirth with arm.ranching / arm.orchard facts commits the same (facts are only read by SkyyRebirth).
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.37.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.38.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.37"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.37"' in s and "derived from the generated 0.4.36 by tools/skills_0_4_37_patch.py" in s, "not the live generated 0.4.37"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert 'fm3  = pool.makeClass(PKG + ".Farm3")' in s, "not 0.4.37 (Farm3 missing)"
OLDS = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    OLDS.append(old)


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.38 (2026-10-14)"):].rstrip() + "\n"

# ---------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.37 - build script (derived from the generated 0.4.36 by tools/skills_0_4_37_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.38 - build script (derived from the generated 0.4.37 by tools/skills_0_4_38_patch.py - edit the patch, not this file;
0.4.37 was derived from the generated 0.4.36 by tools/skills_0_4_37_patch.py;
''')
rep('''0.4.37 (2026-10-14) = PERFECT DODGE in our roll''', NOTE.replace("\n", "\n  ").rstrip() + '''
  CHECKED: SkyySkills/test_skyyskills_0.4.38.py.
0.4.37 (2026-10-14) = PERFECT DODGE in our roll''')
rep('VERSION = "0.4.37"', 'VERSION = "0.4.38"')

# ---------------------------------------------------------------- (1) rebirth.coinFactor 0.9 -> 0.8: fresh file, code defaults, Server Setup row
rep('''L.append("# After a rebirth the level-up coins pay again, times rebirth.coinFactor once per rebirth (0.9 = 90 % after 1, 81 % after 2).")
L.append("rebirth.coinFactor=0.9")
''', '''L.append("# After a rebirth the level-up coins pay again, times rebirth.coinFactor once per rebirth (0.8 = 80 % after 1, 64 % after 2).")
# 0.4.38 (Skyy 2026-10-14 popup "0.8 per rebirth (Recommended)"): the default 0.9 -> 0.8; RbCoinMig's run-once marker sits under the line
RBC_MARK_ID = "SkyySkills 0.4.38 rebirth level coins x0.8"
RBC_MARK = "# SkyySkills 0.4.38 rebirth level coins x0.8: level-up coins after a rebirth pay x rebirth.coinFactor per rebirth (the old default was 0.9)."
assert "=" not in RBC_MARK and ":" in RBC_MARK and len(RBC_MARK) <= 140 and all(ord(_ch) < 128 for _ch in RBC_MARK)
L.append("rebirth.coinFactor=0.8")
L.append(RBC_MARK)
''')
rep('''cfg.addField(CtField.make("public static volatile double RB_COIN = 0.9;", cfg))   # 0.4.36: rebirth.coinFactor (level coins x this ^ rebirths)''',
    '''cfg.addField(CtField.make("public static volatile double RB_COIN = 0.8;", cfg))   # 0.4.36: rebirth.coinFactor (level coins x this ^ rebirths); 0.4.38: 0.9 -> 0.8''')
rep('''    double rbc = dbl(p, "rebirth.coinFactor", 0.9);   // 0.4.36: a bad / missing number = 0.9, clamped 0 - 1
    RB_COIN = Double.isNaN(rbc) ? 0.9 : (rbc < 0.0 ? 0.0 : (rbc > 1.0 ? 1.0 : rbc));''',
    '''    double rbc = dbl(p, "rebirth.coinFactor", 0.8);   // 0.4.36: a bad / missing number = the default (0.4.38: 0.8), clamped 0 - 1
    RB_COIN = Double.isNaN(rbc) ? 0.8 : (rbc < 0.0 ? 0.0 : (rbc > 1.0 ? 1.0 : rbc));''')
rep('''    ("rebirth.coinFactor", "Level coins after each rebirth", "general", "dec", "0.9", "0", "1", "", "x", "live",
     "After a rebirth level coins pay again, x this per rebirth (0.9: 90 %, then 81 %...). 1 = full coins.", "reload"),''',
    '''    ("rebirth.coinFactor", "Level coins after each rebirth", "general", "dec", "0.8", "0", "1", "", "x", "live",
     "After a rebirth level coins pay again, x this per rebirth (0.8: 80 %, then 64 %...). 1 = full coins.", "reload"),''')

# ---------------------------------------------------------------- (1) RbCoinMig: the class
rep('''polm = pool.makeClass(PKG + ".PollMig")        # 0.4.32 E: the one-time fell.pollMs 200 -> 500 update of an existing xp.properties
''', '''polm = pool.makeClass(PKG + ".PollMig")        # 0.4.32 E: the one-time fell.pollMs 200 -> 500 update of an existing xp.properties
rbcm = pool.makeClass(PKG + ".RbCoinMig")      # 0.4.38: the one-time rebirth.coinFactor 0.9 -> 0.8 update of an existing xp.properties
''')
RBCM = r'''

# ---- RbCoinMig (0.4.38, PROJECT-RULES section 4; PollMig's reviewed machinery): ONCE on an EXISTING xp.properties, setup() right after
# PollMig.run, BEFORE SkillCfg.load and CfgPub.start. Nothing to do = no file (load() writes the 0.4.38 default, marker included) or a
# comment line holding MARK_ID (done before). Else, per logical line (the kit's own parser): rebirth.coinFactor whose LAST entry is a
# one-line entry holding exactly 0.9 (the old default) -> every such one-line entry 0.8 (value text only; key, separator, CR kept); NO
# rebirth.coinFactor entry at all (a file older than 0.4.36: it read the 0.9 code default) -> rebirth.coinFactor=0.8 appended; any other
# value is kept (an INFO line). A change = one config-changes.log line (Undo = 0.9). The marker goes right under the last (or the
# appended) entry, or at the end, in the file's own line ending. Properties check (only rebirth.coinFactor differs / is added),
# config-history copy first, atomicWrite. A failure = WARN, file untouched, retried at the next start.
rbcm.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(RBC_MARK_ID), rbcm))
rbcm.addField(CtField.make("public static final String MARK = %s;" % json.dumps(RBC_MARK), rbcm))
rbcm.addField(CtField.make('public static final String KEY = "rebirth.coinFactor";', rbcm))
rbcm.addField(CtField.make('public static final String OLD = "0.9";', rbcm))
rbcm.addField(CtField.make('public static final String NEW = "0.8";', rbcm))
rbcm.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.38";', rbcm))
assert DEFAULTS.count(RBC_MARK_ID) == 1 and ("\n" + DEFAULTS).count("\nrebirth.coinFactor=0.8\n" + RBC_MARK + "\n") == 1
assert "\nrebirth.coinFactor=0.9" not in "\n" + DEFAULTS
# pure text step (ISO-8859-1 chars in and out). null = nothing to do; else { new text, String[] { key, old, new }* (the change-log rows),
# Boolean updated, String kept note ("" = none), Boolean appended }. Never throws for any text.
rbcm.addMethod(CtNewMethod.make(J14(r"""
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
  int lastEnd = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    if (KEY.equals(@PKG@.CfgFile.key(s))) { eff = @PKG@.CfgFile.value(l, k).trim(); multi = e > k; lastEnd = e; }
    k = e + 1;
  }
  boolean add = eff == null;
  boolean mig = add || (!multi && eff.equals(OLD));
  String kept = !mig ? KEY + "=" + @PKG@.CfgRows.oneLine(p.getProperty(KEY)) + " kept (an admin's value) - the 0.4.38 default is 0.8" : "";
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  java.util.ArrayList out = new java.util.ArrayList();
  boolean placed = false;
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    if (mig && !add && KEY.equals(@PKG@.CfgFile.key(s2)) && e2 == k && @PKG@.CfgFile.value(l, k).trim().equals(OLD)) {
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + NEW + (raw[k].endsWith("\r") ? "\r" : ""));
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    if (e2 == lastEnd && e2 + 1 < raw.length) {
      out.add(MARK + (raw[e2].endsWith("\r") ? "\r" : cr));
      placed = true;
    }
    k = e2 + 1;
  }
  StringBuilder sb = new StringBuilder(text.length() + 256);
  for (int i = 0; i < out.size(); i++) {
    if (i > 0) sb.append('\n');
    sb.append((String) out.get(i));
  }
  String body = sb.toString();
  if (!placed) {
    String nl = cr + "\n";
    String pre = (body.length() == 0 || body.endsWith("\n")) ? "" : nl;
    String last = body.endsWith("\n") ? body.substring(0, body.length() - 1) : body;
    if (last.endsWith("\r")) last = last.substring(0, last.length() - 1);
    int bs = 0;
    for (int i = last.length() - 1; i >= 0 && last.charAt(i) == '\\'; i--) bs++;
    if (bs % 2 == 1) pre = pre + nl;
    body = body + pre + (add ? KEY + "=" + NEW + nl : "") + MARK + nl;
  }
  String[] rows = mig ? new String[] { KEY, OLD, NEW } : new String[0];
  return new Object[] { body, rows, Boolean.valueOf(mig), kept, Boolean.valueOf(add) };
}"""), rbcm))
# only rebirth.coinFactor may differ (exactly 0.8 when updated) or be added (exactly 0.8); nothing else added or removed
rbcm.addMethod(CtNewMethod.make(J14(r"""
public static boolean sameAfter(byte[] old, byte[] nb, boolean mig, boolean add) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties n = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    n.load(new java.io.ByteArrayInputStream(nb));
    if (n.size() != a.size() + (add ? 1 : 0)) return false;
    if (add && (a.getProperty(KEY) != null || !NEW.equals(n.getProperty(KEY)))) return false;
    java.util.Iterator it = a.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      String want = a.getProperty(k);
      if (mig && KEY.equals(k)) want = NEW;
      String got = n.getProperty(k);
      if (got == null || !got.equals(want)) return false;
    }
    return true;
  } catch (Throwable t) { return false; }
}"""), rbcm))
rbcm.addMethod(CtNewMethod.make(J14(r"""
public static String logLine(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}"""), rbcm))
rbcm.addMethod(CtNewMethod.make(J14(r"""
public static synchronized String run() {
  java.nio.file.Path f = @PKG@.SkillCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = plan(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    boolean mig = ((Boolean) r[2]).booleanValue();
    boolean add = ((Boolean) r[4]).booleanValue();
    if (!sameAfter(old, data, mig, add)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.38 (rebirth level coins x0.8): the update would change another setting (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = @PKG@.HealMig.fileIdx();
    if (fi < 0) return "";
    @PKG@.HealMig.mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, "before the 0.4.38 rebirth level coins update");
    if (!@PKG@.HealMig.mgSaved(fi, old)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.38 (rebirth level coins x0.8): the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[1];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(logLine(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String msg = "xp.properties updated for 0.4.38: " + (mig ? KEY + " 0.9 -> 0.8" + (add ? " (line added - the file had none and used 0.9)" : "") + " (level-up coins after a rebirth pay 80 % per rebirth; Server Setup -> Changes -> Undo = 0.9)" : "no setting changed - 0.4.38 marker added") + " - the old file is in config-history";
    @PKG@.SkillCfg.info(msg);
    String kept = (String) r[3];
    if (kept.length() > 0) { @PKG@.SkillCfg.info(kept); return msg + "\n" + kept; }
    return msg;
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("could not update xp.properties for 0.4.38 (rebirth level coins x0.8; the file is used as it is): " + t);
    return "";
  }
}"""), rbcm))
'''
rep('''    @PKG@.SkillCfg.warn("could not update xp.properties for 0.4.32 (falling tree check every 500 ms; the file is used as it is): " + t);
    return "";
  }
}"""), polm))
''', '''    @PKG@.SkillCfg.warn("could not update xp.properties for 0.4.32 (falling tree check every 500 ms; the file is used as it is): " + t);
    return "";
  }
}"""), polm))''' + RBCM)
rep('''  {PKG}.PollMig.run();        // 0.4.32: untouched fell.pollMs 200 -> 500 in an existing xp.properties, once; History first
''', '''  {PKG}.PollMig.run();        // 0.4.32: untouched fell.pollMs 200 -> 500 in an existing xp.properties, once; History first
  {PKG}.RbCoinMig.run();      // 0.4.38: untouched rebirth.coinFactor 0.9 (or no line) -> 0.8 in an existing xp.properties, once; History first
''')

# ---------------------------------------------------------------- (2) /skills: 12 rows (Fishing / Ranching / Orchard after Farming)
rep('''SKILL_ROW_SLOTS = [0, 1, 2, 10, 11, 12, 4, 13, 3]
''', '''SKILL_ROW_SLOTS = [0, 1, 2, 16, 17, 18, 10, 11, 12, 4, 13, 3]   # 0.4.38: + Fishing, Ranching, Orchard after Farming (12 rows)
assert [SLOT_NAMES[_x] for _x in SKILL_ROW_SLOTS[3:6]] == ["Fishing", "Ranching", "Orchard"]
''')
rep('''SK_ROW_SLOTS = SKILL_ROW_SLOTS                                         # = SkillDefs.ROW_SLOTS (formatted from the same list): 9 rows''',
    '''SK_ROW_SLOTS = SKILL_ROW_SLOTS                                         # = SkillDefs.ROW_SLOTS (formatted from the same list): 12 rows (0.4.38)''')
rep('''SK_OV_H, SK_OV_M = SUI.BTN_H + 2 * SUI.WELL_PAD, 8                     # the Overall well (60) + 8 under it''',
    '''SK_OV_H, SK_OV_M = SUI.BTN_H + 2 * SUI.WELL_PAD, 4                     # the Overall well (60) + 4 under it (0.4.38: 8 -> 4 for 12 rows)''')
rep('''SK_HINT_H, SK_HINT_M = SUI.fs(12) + 10, 8                              # the caption line under the list''',
    '''SK_HINT_H, SK_HINT_M = SUI.fs(12) + 10, 4                              # the caption line under the list (0.4.38: 4 over it, was 8)''')
rep('''assert (SK_H, STATS_H, OV_H) == (786, 848, 689) and SK_LIST_H == 613 and SK_TOP_LIST_H == 594, (SK_H, STATS_H, OV_H, SK_LIST_H, SK_TOP_LIST_H)''',
    '''assert (SK_H, STATS_H, OV_H) == (973, 848, 689) and SK_LIST_H == 808 and SK_TOP_LIST_H == 781, (SK_H, STATS_H, OV_H, SK_LIST_H, SK_TOP_LIST_H)   # 0.4.38: 12 rows
assert SK_H <= SUI.MAX_PAGE_H, "the /skills page must fit a 1080 px screen (%d > %d)" % (SK_H, SUI.MAX_PAGE_H)''')

# ---------------------------------------------------------------- (3) the participant's facts: arm.ranching + arm.orchard (additive)
rep('''           'public static final String[] ARMS = new String[] { "class", "foraging", "mining", "smithing", "alchemy", "farming", "fishing", "cooking" };'):''',
    '''           'public static final String[] ARMS = new String[] { "class", "foraging", "mining", "smithing", "alchemy", "farming", "fishing", "cooking" };',
           # 0.4.38: the Farming arm's other two pools (facts only; SkyyRebirth 0.3.1+ adds them to arm.farming, 0.3 ignores them)
           'public static final String[] XARMS = new String[] { "ranching", "orchard" };'):''')
rep('''    p.setProperty("arm." + ARMS[i], total + "/" + @PKG@.SkillDefs.cumAt(s, cap) + "/" + @PKG@.SkillDefs.levelCap(s, total, cap) + "/" + cap);
  }
  return p;''', '''    p.setProperty("arm." + ARMS[i], total + "/" + @PKG@.SkillDefs.cumAt(s, cap) + "/" + @PKG@.SkillDefs.levelCap(s, total, cap) + "/" + cap);
  }
  for (int j = 0; j < XARMS.length; j++) {   // 0.4.38: arm.ranching / arm.orchard (same format) for SkyyRebirth's Farming arm
    int s2 = @PKG@.SkillDefs.indexOf(XARMS[j]);
    if (s2 < 0 || s2 >= n) continue;
    long t2 = @PKG@.SkillStore.rd(d, s2);
    int c2 = @PKG@.SkillCap.cap(k, s2);
    p.setProperty("arm." + XARMS[j], t2 + "/" + @PKG@.SkillDefs.cumAt(s2, c2) + "/" + @PKG@.SkillDefs.levelCap(s2, t2, c2) + "/" + c2);
  }
  return p;''')

# ---------------------------------------------------------------- the ready line, the class list
rep('''+ "; rebirth participant rebirth:part:skills (level coins after a rebirth x" + {PKG}.SkillCfg.RB_COIN + " per rebirth, rebirth.coinFactor; the class-weapon bonus counts the table levels only)" + ''',
    '''+ "; rebirth participant rebirth:part:skills (level coins after a rebirth x" + {PKG}.SkillCfg.RB_COIN + " per rebirth, rebirth.coinFactor; the class-weapon bonus counts the table levels only; facts arm.ranching + arm.orchard for the Farming arm)" + "; /skills lists " + {PKG}.SkillDefs.ROW_SLOTS.length + " rows (Fishing, Ranching, Orchard included)" + ''')
rep('''          pdg, pds, pdsu, pcs, rch, rps, rds, rtk, fm3):   # 0.4.37: + PDodge,''',
    '''          pdg, pds, pdsu, pcs, rch, rps, rds, rtk, fm3,
          rbcm):   # 0.4.38: + RbCoinMig; 0.4.37: + PDodge,''')

# ---------------------------------------------------------------- checks
assert s.index("public static Object[] plan(String text) {\n  if (text == null) return null;\n  java.util.Properties p = new java.util.Properties();\n  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { return null; }\n  String[] raw") > s.index("rbcm = pool.makeClass")
assert s.index("{PKG}.PollMig.run();") < s.index("{PKG}.RbCoinMig.run();") < s.index("String rules = {PKG}.SkillCfg.load();")
assert s.index("RBC_MARK_ID = ") < s.index("DEFAULTS = \"\\n\".join(L)")
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed and not any(_o in ln for _o in OLDS if LF not in _o)]
assert not _bad, "0.4.37 lines changed outside the planned places: %r" % _bad[:5]
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.37,", len(_gone), "0.4.37 lines replaced;", len(OLDS), "anchors")
