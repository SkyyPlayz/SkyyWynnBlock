"""Derive SkyySkills/build_skyyskills_0.4.46.py from the GENERATED SkyySkills 0.4.45 (build_skyyskills_0.4.45.py = the tools/deploy_set.py SET
pin; 0.4.45 came from 0.4.44 by tools/skills_0_4_45_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with
0.4.45 (nothing else changed); 0.4.45 stays untouched, its line endings are kept (tools/soundpass_gen.Patch).
Run:  python tools/skills_0_4_46_patch.py   then   python SkyySkills/build_skyyskills_0.4.46.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.46.py
(0.4.46 was first reserved for the T1 tool-upgrade round - that round becomes 0.4.47.)
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

NOTE = '''0.4.46 (2026-10-16) = LOG FIX: the asset-pack checks no longer WARN while the packs are still loading (round logfix; Skyy's standing rule
  "check the logs after every play session, fix ours"). Live boot 2026-10-16 15:12 (Saves/NewBetaTest server log): the first read at
  START_S (10 s) ran while the per-pack asset loading was still going and WARNed "Spell costs: 24 of 24 item overrides are NOT active -
  Hytale:Hytale wins", "Cast checks: 8 of 8 ..." and "Mana stat ... NOT the one in effect", though the smoke log and SkyyArmory's own later
  pack check show Skyy's overrides won.
  ManaGuard.packTick -> packStep (the decision, harness-callable): a check whose read says "info" (active) is logged INFO and done as
  before; a read that says "warn" (another pack wins / the live Mana stat differs / a staff not from SkyyArmory) is only REMEMBERED and the
  check runs again every 10 s; only when the existing PACK_MAX (6) tries are used up does a still-remembered WARN go to the log (once).
  Same rule for all four: Spell costs (items), Cast checks (interactions), Mana stat, Staff handover. Unreadable to the end = the old
  "not checked" INFO. Texts, START_S, PACK_MAX, the 10 s step: unchanged. No gameplay change, no saved data, no command, no setting.
  ROLLBACK to 0.4.45: safe (only the boot WARNs come back).
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.45.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.46.py"))
assert P.has('VERSION = "0.4.45"') and P.has("SkyySkSubRow") and not P.has("packStep"), "not the generated SkyySkills 0.4.45 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

# ================================================================================================ docstring + version
P.rep('''"""SkyySkills 0.4.45 - build script (derived from the generated 0.4.44 by tools/skills_0_4_45_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.46 - build script (derived from the generated 0.4.45 by tools/skills_0_4_46_patch.py - edit the patch, not this file;
''' + NOTE + '''  CHECKED: SkyySkills/test_skyyskills_0.4.46.py.
0.4.45 was derived from the generated 0.4.44 by tools/skills_0_4_45_patch.py;
''')
P.rep('VERSION = "0.4.45"', 'VERSION = "0.4.46"')

# ================================================================================================ the pending WARN texts
P.rep('''mgd.addField(CtField.make('public static volatile String PACK_LAST = "";', mgd))
''', '''mgd.addField(CtField.make('public static volatile String PACK_LAST = "";', mgd))
# 0.4.46: the newest WARN text of a check that is not done yet ("" = none) - logged only once PACK_MAX tries are used up
mgd.addField(CtField.make('public static volatile String PACK_PEND = "";', mgd))
mgd.addField(CtField.make('public static volatile String INT_PEND = "";', mgd))
mgd.addField(CtField.make('public static volatile String MANA_PEND = "";', mgd))
mgd.addField(CtField.make('public static volatile String ARM_PEND = "";', mgd))
''')

# ================================================================================================ packTick -> packStep (WARN on the last try only)
OLD_TICK = '''# 0.4.9: both checks (the items as in 0.4.8, the interactions new), each logged once as soon as it is readable; after PACK_MAX tries the
# unreadable one says so
mgd.addMethod(CtNewMethod.make(f"""
public static void packTick() {{
  PACK_TRIES++;
  if (!ITEMS_DONE) {{
    String[] r = packCheck();
    if (r[0].length() > 0) {{
      ITEMS_DONE = true;
      PACK_LAST = r[1];
      if ("warn".equals(r[0])) {PKG}.SkillCfg.warn(r[1]);
      else {PKG}.SkillCfg.info(r[1]);
    }}
  }}
  if (!INT_DONE) {{
    String[] q = intCheck();
    if (q[0].length() > 0) {{
      INT_DONE = true;
      INT_LAST = q[1];
      if ("warn".equals(q[0])) {PKG}.SkillCfg.warn(q[1]);
      else {PKG}.SkillCfg.info(q[1]);
    }}
  }}
  if (!MANA_DONE) {{   // 0.4.31: the live Mana stat vs the generated Mana.json
    String[] q2 = manaCheck();
    if (q2[0].length() > 0) {{
      MANA_DONE = true;
      MANA_LAST = q2[1];
      if ("warn".equals(q2[0])) {PKG}.SkillCfg.warn(q2[1]);
      else {PKG}.SkillCfg.info(q2[1]);
    }}
  }}
  if (!ARM_DONE) {{   // 0.4.15: the staff handover - which pack the 8 SkyyArmory-owned staffs come from
    String[] a = armCheck();
    if (a[0].length() > 0) {{
      ARM_DONE = true;
      ARM_LAST = a[1];
      if ("warn".equals(a[0])) {PKG}.SkillCfg.warn(a[1]);
      else if ("info".equals(a[0])) {PKG}.SkillCfg.info(a[1]);
    }}
  }}
  if (ITEMS_DONE && INT_DONE && ARM_DONE && MANA_DONE) {{   // 0.4.31: + MANA_DONE
    PACK_DONE = true;
    return;
  }}
  if (PACK_TRIES >= PACK_MAX) {{
    PACK_DONE = true;
    if (!MANA_DONE) {{
      MANA_LAST = "Mana stat: the game's Mana stat could not be read to check it against the Mana.json this jar ships - not checked";
      {PKG}.SkillCfg.info(MANA_LAST);
    }}
    if (!ARM_DONE) {{
      ARM_LAST = "Staff handover: the game's item assets could not be read to see which pack the " + {PKG}.ManaCost.ARM_IDS.length + " SkyyArmory-owned staffs come from - not checked";
      {PKG}.SkillCfg.info(ARM_LAST);
    }}
    if (!ITEMS_DONE) {{
      PACK_LAST = "Spell costs /" + {PKG}.ManaCost.DIVISOR + ": the game's item assets could not be read to see which pack each of the " + {PKG}.ManaCost.N + " overridden items comes from - not checked";
      {PKG}.SkillCfg.info(PACK_LAST);
    }}
    if (!INT_DONE) {{
      INT_LAST = "Cast checks /" + {PKG}.ManaCost.DIVISOR + ": the game's interaction assets could not be read to see which pack each of the " + {PKG}.ManaCost.INT_N + " overridden interactions comes from - not checked";
      {PKG}.SkillCfg.info(INT_LAST);
    }}
  }}
}}""", mgd))
'''
NEW_TICK = '''# 0.4.9: both checks (the items as in 0.4.8, the interactions new), each logged once as soon as it is readable; after PACK_MAX tries the
# unreadable one says so.
# 0.4.46 (log fix): the first reads run while the per-pack asset loading is still going (vanilla Hytale:Hytale is the winner until the later
# packs land), so a "warn" read is only remembered (*_PEND) and the check runs again every 10 s; an "info" read (active) ends it at once;
# when PACK_MAX tries are used up a still-remembered WARN is logged (once), else the old "not checked" INFO. packStep = the decision (one
# answer per check, null = that check is done and was not read); packTick reads the checks that are not done.
mgd.addMethod(CtNewMethod.make(f"""
public static void packStep(String[] r, String[] q, String[] q2, String[] a) {{
  PACK_TRIES++;
  if (!ITEMS_DONE && r != null) {{
    if ("warn".equals(r[0])) PACK_PEND = r[1];
    else if (r[0].length() > 0) {{
      ITEMS_DONE = true;
      PACK_LAST = r[1];
      {PKG}.SkillCfg.info(r[1]);
    }}
  }}
  if (!INT_DONE && q != null) {{
    if ("warn".equals(q[0])) INT_PEND = q[1];
    else if (q[0].length() > 0) {{
      INT_DONE = true;
      INT_LAST = q[1];
      {PKG}.SkillCfg.info(q[1]);
    }}
  }}
  if (!MANA_DONE && q2 != null) {{   // 0.4.31: the live Mana stat vs the generated Mana.json
    if ("warn".equals(q2[0])) MANA_PEND = q2[1];
    else if (q2[0].length() > 0) {{
      MANA_DONE = true;
      MANA_LAST = q2[1];
      {PKG}.SkillCfg.info(q2[1]);
    }}
  }}
  if (!ARM_DONE && a != null) {{   // 0.4.15: the staff handover - which pack the 8 SkyyArmory-owned staffs come from
    if ("warn".equals(a[0])) ARM_PEND = a[1];
    else if (a[0].length() > 0) {{
      ARM_DONE = true;
      ARM_LAST = a[1];
      if ("info".equals(a[0])) {PKG}.SkillCfg.info(a[1]);
    }}
  }}
  if (ITEMS_DONE && INT_DONE && ARM_DONE && MANA_DONE) {{   // 0.4.31: + MANA_DONE
    PACK_DONE = true;
    return;
  }}
  if (PACK_TRIES >= PACK_MAX) {{
    PACK_DONE = true;
    if (!MANA_DONE) {{
      MANA_DONE = true;
      if (MANA_PEND.length() > 0) {{ MANA_LAST = MANA_PEND; {PKG}.SkillCfg.warn(MANA_LAST); }}
      else {{
        MANA_LAST = "Mana stat: the game's Mana stat could not be read to check it against the Mana.json this jar ships - not checked";
        {PKG}.SkillCfg.info(MANA_LAST);
      }}
    }}
    if (!ARM_DONE) {{
      ARM_DONE = true;
      if (ARM_PEND.length() > 0) {{ ARM_LAST = ARM_PEND; {PKG}.SkillCfg.warn(ARM_LAST); }}
      else {{
        ARM_LAST = "Staff handover: the game's item assets could not be read to see which pack the " + {PKG}.ManaCost.ARM_IDS.length + " SkyyArmory-owned staffs come from - not checked";
        {PKG}.SkillCfg.info(ARM_LAST);
      }}
    }}
    if (!ITEMS_DONE) {{
      ITEMS_DONE = true;
      if (PACK_PEND.length() > 0) {{ PACK_LAST = PACK_PEND; {PKG}.SkillCfg.warn(PACK_LAST); }}
      else {{
        PACK_LAST = "Spell costs /" + {PKG}.ManaCost.DIVISOR + ": the game's item assets could not be read to see which pack each of the " + {PKG}.ManaCost.N + " overridden items comes from - not checked";
        {PKG}.SkillCfg.info(PACK_LAST);
      }}
    }}
    if (!INT_DONE) {{
      INT_DONE = true;
      if (INT_PEND.length() > 0) {{ INT_LAST = INT_PEND; {PKG}.SkillCfg.warn(INT_LAST); }}
      else {{
        INT_LAST = "Cast checks /" + {PKG}.ManaCost.DIVISOR + ": the game's interaction assets could not be read to see which pack each of the " + {PKG}.ManaCost.INT_N + " overridden interactions comes from - not checked";
        {PKG}.SkillCfg.info(INT_LAST);
      }}
    }}
  }}
}}""", mgd))
mgd.addMethod(CtNewMethod.make("""
public static void packTick() {
  String[] r = null;
  String[] q = null;
  String[] q2 = null;
  String[] a = null;
  if (!ITEMS_DONE) r = packCheck();
  if (!INT_DONE) q = intCheck();
  if (!MANA_DONE) q2 = manaCheck();
  if (!ARM_DONE) a = armCheck();
  packStep(r, q, q2, a);
}""", mgd))
'''
P.rep(OLD_TICK, NEW_TICK)

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
