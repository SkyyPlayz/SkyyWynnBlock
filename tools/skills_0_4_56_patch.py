"""Derive SkyySkills/build_skyyskills_0.4.56.py from the GENERATED SkyySkills 0.4.55 (build_skyyskills_0.4.55.py = the tools/deploy_set.py SET
pin; 0.4.55 came from 0.4.54 by tools/skills_0_4_55_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with
0.4.55 (nothing else changed); 0.4.55 stays untouched, its line endings are kept (tools/soundpass_gen.Patch).
Run:  python tools/skills_0_4_56_patch.py   then   python SkyySkills/build_skyyskills_0.4.56.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.56.py
"""
import os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import trees_v3_effects as V3E

OLD_XS = "Mining,Foraging,Farming,Cooking"
NEW_XS = "Mining,Foraging,Farming,Cooking,Alchemy,Smithing"
_CI = [e for e in V3E.rows("SkyySkills") if e[4] == "class.xp"]
assert len(_CI) == 1 and V3E.rows("SkyySkills") == _CI, "0.4.56: SkyySkills applies exactly Combat Insight"
CI = _CI[0]

NOTE = '''0.4.56 (2026-10-20) = SKILL TREES 3 R3b, the SkyySkills part (tools/trees_v3_effects.py; with SkyyPets 0.4.5, SkyyGear 0.3.32,
  SkyyAccessories 0.5.28, SkyyFishing 0.1.11, SkyyCooking 0.1.14, SkyyExploration 0.3.1). Skyy (2026-10-18): "i want all the skill trees to
  follow the same general pattern" + the four power sources rule.
  1. COMBAT INSIGHT (Combat tree, Spoils b3 r5b; "Combat tree shares the class level", default 2026-10-20): +2 % class skill XP a rank, added
     to the class slots' XP bonus (SkillBonus.xpBonus, next to Class Wisdom; the 0..5 clamp holds). The rank comes from SkyyTrees:
     tree:fn:level { UUID, "''' + V3E.key(CI[0], CI[1], CI[2]) + '''" } -> Integer (clamped to its max 5; SkyyTrees 0.4.0 answers 0 = no
     change until its v3 hook build). The class slots also take the skill:bonus key xp.combat (SkyyPets 0.4.5 Pet Fang: +2 % combat XP per
     Combat pet tier) - both only while bridge.bonus.enabled is on.
  2. ALCHEMY + SMITHING GET WISDOM: bridge.bonus.xpSkills default ''' + OLD_XS + ''' -> ''' + NEW_XS + ''' so the
     Alchemy tree's Master Distiller (SkyyTrees' xp.alchemy from the 0.3 Alchemy Wisdom node it aliases) and the pet rows Pet Herbalist
     (xp.alchemy) / Pet Hammer (xp.smithing) raise the XP you earn at the Alchemy Bench / Furnace / crafts (gain2, skill:fn:craftxp).
     Fishing is NOT added: every Fishing XP is a skill:fn:addxp GRANT, and bridge.bonus.addxpSkills would also boost SkyyCollections /
     SkyyQuests / SkyyShards Fishing rewards (they stay exact) - so the Fishing tree's Pet Angler stays "coming soon" (R3b report).
     MIGRATION Xp56Mig (PROJECT-RULES 4; Fm48Mig's reviewed machinery, one key): ONCE on an EXISTING xp.properties (setup, right after
     En54Mig, before SkillCfg.load): a one-line bridge.bonus.xpSkills=''' + OLD_XS + ''' (the old default; also written with spaces) as
     the LAST entry of the key -> ''' + NEW_XS + '''; an admin's other value kept (INFO); no line = nothing (the new code default
     applies); config-history copy first (CfgHist.snapshot + HealMig.mgSaved), one config-changes.log line (Undo), the marker comment at the
     end (a fresh default file carries it), Properties check (only that key), bytes / line endings kept; a failure = WARN, file untouched,
     retried next start.
  3. tree:reads:SkyySkills = "''' + V3E.reads_csv("SkyySkills") + '''" (put at setup, our value removed at shutdown): Combat Insight
     and the 0.3 Alchemy.PWisdom alias (SkyyTrees 0.4.0 already names SkyySkills its reader - Master Distiller turns buyable with this jar).
  No saved player data change, no new command / system. ROLLBACK to 0.4.55: harmless - 0.4.55 reads the migrated xpSkills line as an
  ordinary list (Alchemy / Smithing Wisdom keep working there too), ignores Combat Insight and the reader list (the upgrades show coming
  soon again); Server Setup -> Changes -> Undo restores the old xpSkills line.
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.55.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.56.py"))
assert P.has('VERSION = "0.4.55"') and P.has("En54Mig"), "not the generated SkyySkills 0.4.55 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

P.rep('''"""SkyySkills 0.4.55 - build script (derived from the generated 0.4.54 by tools/skills_0_4_55_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.56 - build script (derived from the generated 0.4.55 by tools/skills_0_4_56_patch.py - edit the patch, not this file;
''' + NOTE + '''  CHECKED: SkyySkills/test_skyyskills_0.4.56.py.
0.4.55 was derived from the generated 0.4.54 by tools/skills_0_4_55_patch.py;
''')
P.rep('VERSION = "0.4.55"', 'VERSION = "0.4.56"')
P.rep('BONUS_XP_SKILLS = "%s"   # 0.4 trees bridge: skills whose XP the skill:bonus xp.<skill> entries raise' % OLD_XS,
      'BONUS_XP_SKILLS = "%s"   # 0.4 trees bridge: skills whose XP the skill:bonus xp.<skill> entries raise; 0.4.56: + Alchemy, Smithing (Skill Trees 3)\n'
      'import trees_v3_effects as V3E   # 0.4.56: Skill Trees 3 R3b - the skill-tree rows SkyySkills applies (the one table)\n'
      'XP56_OLD, XP56_NEW = %s, BONUS_XP_SKILLS' % (NEW_XS, repr(OLD_XS)))
P.rep('''FM48_MARK_ID = "SkyySkills 0.4.48 Fortune uncapped"''', '''XP56_MARK_ID = "SkyySkills 0.4.56 Alchemy and Smithing Wisdom"
XP56_MARK = "# SkyySkills 0.4.56 Alchemy and Smithing Wisdom: bridge.bonus.xpSkills lists Alchemy and Smithing (Skill Trees 3 XP rows)."
assert "=" not in XP56_MARK and ":" in XP56_MARK and len(XP56_MARK) <= 140 and all(ord(_ch) < 128 for _ch in XP56_MARK)
FM48_MARK_ID = "SkyySkills 0.4.48 Fortune uncapped"''')
P.rep('''BRIDGE_L.append("bridge.bonus.addxpSkills=" + BONUS_ADDXP_SKILLS)
''', '''BRIDGE_L.append("bridge.bonus.addxpSkills=" + BONUS_ADDXP_SKILLS)
BRIDGE_L.append(XP56_MARK)   # 0.4.56: Xp56Mig's run-once marker (a fresh file is never migrated)
''')
P.rep('''en54 = pool.makeClass(PKG + ".En54Mig")        # 0.4.54: the one-time Enchanted alloy Smithing XP lines appended to an existing xp.properties
''', '''en54 = pool.makeClass(PKG + ".En54Mig")        # 0.4.54: the one-time Enchanted alloy Smithing XP lines appended to an existing xp.properties
xp56 = pool.makeClass(PKG + ".Xp56Mig")        # 0.4.56: the one-time bridge.bonus.xpSkills + Alchemy, Smithing update of an existing xp.properties
sv3 = pool.makeClass(PKG + ".SkillV3")         # 0.4.56: Skill Trees 3 R3b - the ranks SkyySkills reads (Combat Insight) + tree:reads:SkyySkills
''')

# ---------------------------------------------------------------------------------------------------- Xp56Mig = Fm48Mig's block, one key
_a = "# ---- Fm48Mig (0.4.48, PROJECT-RULES section 4;"
_b = "# ---- Zo49Mig (0.4.49, PROJECT-RULES section 4;"
assert P.s.count(_a) == 1 and P.s.count(_b) == 1
FM = P.s[P.s.index(_a):P.s.index(_b)]
XP = FM.replace("fm48", "xp56").replace("FM48_MARK", "XP56_MARK")
for old, new in [
        ("# ---- Fm48Mig (0.4.48, PROJECT-RULES section 4; Pd44Mig's reviewed machinery, one key): ONCE on an EXISTING xp.properties, setup() right\n"
         "# after Pd44Mig.run, BEFORE SkillCfg.load.",
         "# ---- Xp56Mig (0.4.56, PROJECT-RULES section 4; Fm48Mig's reviewed machinery, one key): ONCE on an EXISTING xp.properties, setup() right\n"
         "# after En54Mig.run, BEFORE SkillCfg.load."),
        ("When the LAST perk.fortuneMax entry\n# is a one-line entry holding exactly the old default (2.0, or 2), every such one-line entry -> 0 (no cap; value text only); any other value\n# kept (INFO); NO line = nothing (the new code default 0 applies).",
         "When the LAST bridge.bonus.xpSkills\n# entry is a one-line entry holding exactly the old default (with or without spaces), every such one-line entry -> the 0.4.56 list (value\n# text only); any other value kept (INFO); NO line = nothing (the new code default applies)."),
        ("""'public static final String[] KEYS = new String[] { "perk.fortuneMax" };'""", """'public static final String[] KEYS = new String[] { "bridge.bonus.xpSkills" };'"""),
        ("""'public static final String[] OLDS = new String[] { "2.0" };'""", """'public static final String[] OLDS = new String[] { "%s" };' % XP56_OLD"""),
        ("""'public static final String[] ALTS = new String[] { "2" };'""", """'public static final String[] ALTS = new String[] { "%s" };' % XP56_OLD.replace(",", ", ")"""),
        ("""'public static final String[] NEWS = new String[] { "0" };'""", """'public static final String[] NEWS = new String[] { "%s" };' % XP56_NEW"""),
        ("""'public static final String WHO = "SkyySkills 0.4.48";'""", """'public static final String WHO = "SkyySkills 0.4.56";'"""),
        ('''assert ("\\n" + DEFAULTS).count("\\nperk.fortuneMax=0\\n") == 1''', '''assert ("\\n" + DEFAULTS).count("\\nbridge.bonus.xpSkills=" + XP56_NEW + "\\n") == 1'''),
        ("# the old default, as written by 0.4.26 - 0.4.47 (2.0) or by hand (2)", "# the old default, as 0.4.0 - 0.4.55 wrote it, or typed with spaces after the commas"),
        ('" kept (an admin\'s value) - the 0.4.48 default is " + NEWS[i] + " (no cap)"', '" kept (an admin\'s value) - the 0.4.56 default is " + NEWS[i] + " (Alchemy and Smithing get Wisdom)"'),
        ("xp.properties NOT updated for 0.4.48 (tool Fortune uncapped): the update would change", "xp.properties NOT updated for 0.4.56 (Alchemy and Smithing Wisdom): the update would change"),
        ('"before the 0.4.48 Fortune cap update"', '"before the 0.4.56 Alchemy and Smithing Wisdom update"'),
        ("xp.properties NOT updated for 0.4.48 (tool Fortune uncapped): the old file could not", "xp.properties NOT updated for 0.4.56 (Alchemy and Smithing Wisdom): the old file could not"),
        ('"xp.properties updated for 0.4.48: "', '"xp.properties updated for 0.4.56: "'),
        ('"no setting changed - 0.4.48 marker added"', '"no setting changed - 0.4.56 marker added"'),
        ("could not update xp.properties for 0.4.48 (tool Fortune uncapped; the file is used as it is)", "could not update xp.properties for 0.4.56 (Alchemy and Smithing Wisdom; the file is used as it is)"),
        ]:
    assert XP.count(old) == 1, ("Xp56Mig: anchor", old[:90])
    XP = XP.replace(old, new)
assert "0.4.48" not in XP and "ortune" not in XP and "2.0" not in XP, [l for l in XP.split("\n") if "0.4.48" in l or "ortune" in l][:5]
P.rep(_b, XP + _b)

# ---------------------------------------------------------------------------------------------------- SkillV3 (before xpBonus calls it)
V3 = '''# 0.4.56 SkillV3: Skill Trees 3 R3b - the rank SkyySkills reads from SkyyTrees (tree:fn:level { UUID, "Skill.<Tree>.b<n>.<id>" } -> Integer,
# clamped to the upgrade's max; 0 = none / not live / no SkyyTrees / a bad answer) and the class XP the Combat tree adds
sv3.addField(CtField.make("public static final String KEY_CI = %s;" % json.dumps(V3E.key("Combat", 3, "r5b")), sv3))
sv3.addField(CtField.make("public static final int MAX_CI = %d;" % V3E.maxrank("Combat", 3, "r5b"), sv3))
sv3.addField(CtField.make("public static final double PER_CI = %r;" % float([_e for _e in V3E.rows("SkyySkills") if _e[4] == "class.xp"][0][5]), sv3))
sv3.addField(CtField.make("public static final String READS = %s;" % json.dumps(V3E.reads_csv("SkyySkills")), sv3))
sv3.addField(CtField.make('public static final String READS_KEY = "tree:reads:SkyySkills";', sv3))
sv3.addMethod(CtNewMethod.make(J14(r"""
public static int rank(java.util.UUID u, String key, int max) {
  if (u == null || key == null) return 0;
  try {
    Object f = @PKG@.SkillStore.bridge().get("tree:fn:level");
    if (!(f instanceof java.util.function.Function)) return 0;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
    if (!(r instanceof Number)) return 0;
    int n = ((Number) r).intValue();
    if (n <= 0) return 0;
    return n > max ? max : n;
  } catch (Throwable t) { return 0; }
}"""), sv3))
# the class slots' extra XP bonus (a fraction): Combat Insight + every source's xp.combat (SkyyPets Pet Fang); 0 with bridge.bonus.enabled off
sv3.addMethod(CtNewMethod.make(J14(r"""
public static double classXp(java.util.UUID u) {
  if (u == null || !@PKG@.BridgeCfg.BONUS) return 0.0;
  double s = PER_CI * (double) rank(u, KEY_CI, MAX_CI) + @PKG@.SkillBonus.sum(u, "xp.combat");
  if (Double.isNaN(s) || Double.isInfinite(s)) return 0.0;
  return s;
}"""), sv3))
sv3.addMethod(CtNewMethod.make(J14(r"""
public static void reads(boolean on) {
  try {
    if (on) @PKG@.SkillStore.bridge().put(READS_KEY, READS);
    else @PKG@.SkillStore.bridge().remove(READS_KEY, READS);
  } catch (Throwable t) { }
}"""), sv3))
'''
P.rep('''# XP bonus fraction of one slot: only slots listed in bridge.bonus.xpSkills, sum over all sources clamped 0..5 (spec 9.3)
''', V3 + '''# XP bonus fraction of one slot: only slots listed in bridge.bonus.xpSkills, sum over all sources clamped 0..5 (spec 9.3)
''')
P.rep('''  double s = (slot >= on.length || !on[slot]) ? 0.0 : sum(u, "xp." + key(slot));
  s = s + rb;''', '''  double s = (slot >= on.length || !on[slot]) ? 0.0 : sum(u, "xp." + key(slot));
  s = s + rb;
  if ({PKG}.SkillDefs.isClass(slot)) s = s + {PKG}.SkillV3.classXp(u);   // 0.4.56: Combat Insight + xp.combat (Pet Fang)''')
P.rep('''  {PKG}.En54Mig.run();        // 0.4.54: the Enchanted alloy Smithing XP lines into an existing xp.properties, once; History first
''', '''  {PKG}.En54Mig.run();        // 0.4.54: the Enchanted alloy Smithing XP lines into an existing xp.properties, once; History first
  {PKG}.Xp56Mig.run();        // 0.4.56: untouched bridge.bonus.xpSkills -> + Alchemy, Smithing (Skill Trees 3 Wisdom rows), once; History first
''')
P.rep('''  {PKG}.SkillStore.bridge().put("skill:fn:level", new {PKG}.SkillFn());
''', '''  {PKG}.SkillStore.bridge().put("skill:fn:level", new {PKG}.SkillFn());
  {PKG}.SkillV3.reads(true);   // 0.4.56: tree:reads:SkyySkills (Combat Insight + the Alchemy.PWisdom alias)
''')
P.rep('''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:level"); }} catch (Throwable t) {{ }}
''', '''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:level"); }} catch (Throwable t) {{ }}
  {PKG}.SkillV3.reads(false);   // 0.4.56: only our own value (never throws)
''')
P.rep('''assert DEFAULTS.count(FM48_MARK_ID) == 1 and _dp.get("perk.fortuneMax") == "0" and _dp.get("perk.fortuneGuard") == "100"   # 0.4.48
''', '''assert DEFAULTS.count(FM48_MARK_ID) == 1 and _dp.get("perk.fortuneMax") == "0" and _dp.get("perk.fortuneGuard") == "100"   # 0.4.48
assert DEFAULTS.count(XP56_MARK_ID) == 1 and _dp.get("bridge.bonus.xpSkills") == XP56_NEW   # 0.4.56
''')
P.rep("rbcm, snd39, rbs39, pd44, fm48, zo49, fl50, mn52, nc53, fa53, en54, lvf,",
      "rbcm, snd39, rbs39, pd44, fm48, zo49, fl50, mn52, nc53, fa53, en54, xp56, sv3, lvf,")

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
print("wrote SkyySkills/build_skyyskills_0.4.56.py (%d changes)" % len(P.changes))
