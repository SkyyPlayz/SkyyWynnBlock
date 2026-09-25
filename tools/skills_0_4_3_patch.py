"""Derive SkyySkills/build_skyyskills_0.4.3.py from 0.4.2 (same style as skills_0_4_2_patch.py: rep(old, new) with asserted single anchors,
newline-agnostic; 0.4.2 stays untouched, its CRLF line endings are preserved). Edit THIS file, not the generated script.
0.4.3 = the in-game server setup round (research/Server-Setup-Spec.md 4.9 + 5.7, tools/CONFIG-CONTRACT.md) + the player Settings
switches (research/Settings-Spec.md 1.3 + 3.1):
 - ADMIN CONFIG (tools/skyycfg.py, copied into the jar): config:def:SkyySkills + config:fn:SkyySkills published at the END of setup()
   after SkillCfg.load(); one file (Skyy_SkyySkills/xp.properties, file names and keys unchanged), node skyyskills.admin, 8 categories
   (parts, general, levels, gathering, combat, acrobatics, perks, crafting). Every row binds reload: (the file line changes, then the kit
   runs SkillKit.reload = SkillCfg.load + Acro.djPublish, the /skills reload path), the 6 key families are reload: tables (block. /
   prefix. / suffix. / combat.role. / alchemy.xp. / smithing.xp.). Nine master keys are part switches (spec 3). Defaults = the numbers
   the loader uses today (a build assert compares every row default with the default xp.properties text).
 - CURVE ACTIONS (spec 5.7): "Level curve size" (% of the default curve) and "Max level" are int rows with a custom: binding (SkillKit):
   they read the kit's current levels= value, rewrite the list (scale every level / cut or extend along the default curve's shape), apply
   it in memory, hand the new levels= line to the kit (written, versioned, logged) and arm the kit's reload routine. v1 kit action rows
   carry no typed value, so the "N" comes from the row's own TextField (spec 4.9 asks for exactly that).
 - upgradeLevels (the 0.3 migration of the old 50-level default) now only runs for a file written by 0.1 / 0.2 (no perk.* key yet), so
   "Max level 50" (= the first 50 default levels = the old table) is no longer silently turned back into 100 levels at the next load.
 - /skills reload also runs the kit's reload op first (hand edits are logged via=file), then reloads exactly as before.
 - PLAYER SETTINGS: SkillStore.notifyOn / regSetting / moveQuiet (spec 3.1 helper), six switches registered in setup()
   (skills.xpGain, skills.levelUp, skills.doubleDrop, skills.extraPotion, skills.combatHints, rewards.late); gates only on the chat
   sends (SkillMsg.note, gain4 level-up + late payout lines, SkillClass.tellOnce, Perks.doubled, Brew.extraPotion) plus the two 0.4.2
   lines /skills quiet used to hide (Fell "Tree felled" and PartyXp "[Party] +N XP" -> skills.xpGain); /skills quiet becomes the
   shortcut of spec 3.1 while SkyyMenu's registry exists (today's toggle without it). No refusing switch here.
Run:  python tools/skills_0_4_3_patch.py   then   python SkyySkills/build_skyyskills_0.4.3.py   (NO --deploy: coordinated deploy)
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.2.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.3.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.2"
s = raw.decode("utf8").replace("\r\n", "\n")
REG0 = s.count("registerSystem(")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:100]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:100])
    s = s.replace(old, new)


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


# ================================================================ header / version
rep('''"""SkyySkills 0.4.2 - build script (derived from 0.4.1 by tools/skills_0_4_2_patch.py - edit the patch, not this file;
0.4.1 was derived from 0.4 by tools/skills_0_4_1_patch.py, 0.4 from 0.3.2 by tools/skills_0_4_patch.py, 0.3.2 from 0.3.1 by
tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
0.4.2 (research/Tree-Fall-Spec.md''', '''"""SkyySkills 0.4.3 - build script (derived from 0.4.2 by tools/skills_0_4_3_patch.py - edit the patch, not this file;
0.4.2 was derived from 0.4.1 by tools/skills_0_4_2_patch.py, 0.4.1 from 0.4 by tools/skills_0_4_1_patch.py, 0.4 from 0.3.2 by
tools/skills_0_4_patch.py, 0.3.2 from 0.3.1 by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
0.4.3 (research/Server-Setup-Spec.md 4.9 + 5.7 - SERVER SETUP IN GAME; research/Settings-Spec.md 1.3 + 3.1 - PLAYER SETTINGS). Builds on
  0.4.2 and changes NO default behaviour: every number, switch and message is the same until an admin changes something.
  ADMIN CONFIG (tools/skyycfg.py, contract tools/CONFIG-CONTRACT.md; SkyyMenu 0.3 Server Setup shows it as "Skills"):
    config:def:SkyySkills / config:fn:SkyySkills / config:epoch:SkyySkills, published at the END of setup() after SkillCfg.load().
    File Skyy_SkyySkills/xp.properties (names and keys unchanged), node skyyskills.admin, categories parts / general / levels /
    gathering / combat / acrobatics / perks / crafting. Rows bind reload: - the kit changes only that line of xp.properties (comments and
    order kept), versions the file (config-history/, 20 copies), logs config-changes.log, then runs SkillKit.reload (= SkillCfg.load +
    Acro.djPublish, exactly what /skills reload does). Tables (key families, reload:): block. / prefix. / suffix. (column Skill:XP or none,
    check= SkillKit.checkRule = the loader's own parseRule / explRule), combat.role. (XP), alchemy.xp. / smithing.xp. (XP, entries must be
    item ids, add by typing or holding the item). Parts (live,part,danger - confirm only when switched OFF): acro.enabled,
    acro.doubleJump.enabled, perk.enabled, alchemy.enabled, smithing.smelt.enabled, exploration.enabled, fell.enabled,
    party.combatShare.enabled, bridge.bonus.enabled. Typed values are refused outside the loader's clamp ranges (files are still clamped
    by the loader as before). A build assert compares every row default with the default xp.properties text; the 21 per-skill perk
    stats that are NOT in the default file (they read 0) are adv rows with default 0 (PerkCfg's own defaults).
    Level curve (spec 5.7): "Level curve size" (int %, custom: SkillKit) = the levels= list as a percent of the default curve over the
    same number of levels; setting N rescales every level to N% (so it can be undone by setting the old value) - "Max level" (int 1-100,
    custom: SkillKit) cuts the list or extends it along the default curve's shape (joined at the last kept level; the default list
    extends back to exactly the default). A cut remembers the full list in memory (SkillKit.TAIL / LAST, this server run): raising Max
    level again while the list is still what the last Max level change left (Undo included) gives the cut levels back EXACTLY, also for a
    hand-edited or imported curve; after a restart or any other change of the list, History restores an exact older list. Both read the
    kit's current levels= value (pending edits included), apply the new table at once (SkillDefs.setTable), hand the levels= line to the
    kit and arm the kit's reload routine (CfgFile.addReloads; again 200 ms later through SkillKitArm on the scheduler, which also sets
    CfgFile.force so a save + reload cycle runs even when no save is due - a save that took the first arm before the line existed, or
    that wrote the line before the re-arm, can never leave the running table behind the file; kit gap: wants() ignores a pure arm).
    Players keep their XP; a lower max shows MAX, raising it again gives the levels back.
    upgradeLevels (0.3 migration of the old 50-level default) now runs only for a file without perk.* keys (written by 0.1 / 0.2), so
    "Max level 50" from the default list (identical to the old table) is not silently undone at the next load.
    /skills reload keeps its reply and effect: it first runs the kit's reload op (hand edits logged via=file, pending in-game changes
    written), then SkillCfg.load() + Acro.djPublish() as before. The file is read twice ON PURPOSE: the kit's reload op merges on the
    caller thread and, only when it found hand edits (or in-game edits were pending), runs SkillKit.reload once more on its save task
    shortly after the reply; the synchronous load keeps the 0.4.2 reply text. Both are idempotent (SkillCfg.load is synchronized).
    Plugin shutdown flushes the kit (CfgPub.shutdown) first.
    Row help: combat.min / combat.max say that an inverted pair pays every kill the maximum (no cross-check: an import that raises both
    must not be refused); perk.exploration.staminaPerLevel says SkyyExploration 0.2.1+ shows it on /explore (read over config:fn get).
  PLAYER SETTINGS (Settings-Spec 3.1): SkillStore.moveQuiet / notifyOn / regSetting. setup() registers skills.xpGain, skills.levelUp,
    skills.doubleDrop, skills.extraPotion, skills.combatHints (tab skills) and rewards.late (tab coins, shared with SkyyCollections,
    identical label / help). Gates (only the chat send; XP, coins, drops, throttles and latches run as before): SkillMsg.note +XP line,
    gain4 SKILL LEVEL UP + next: lines (levelUp) and the late coin line (rewards.late), SkillClass.tellOnce before claimTold (combatHints),
    Perks.doubled (doubleDrop), Brew.extraPotion (extraPotion), and the two 0.4.2 lines /skills quiet hid: the "Tree felled" summary and
    the "[Party] +N XP" line (skills.xpGain). Without SkyyMenu every switch reads ON and /skills quiet works as before; with it the
    first message check moves an old quiet=true profile flag to the three switches (onlyIfUnset) and /skills quiet flips them.
    Admin master switches still win (feedback, perk.doubleDropMessage, fell.message, party.combatShare.message).
  CHECKED in a bare JVM (2026-09-25, scratch harness under tools/dev/scratch/r4-skyyskills, deleted afterwards): all 80 classes load +
    initialise under -Xverify:all; SkillCfg.load writes the default file; CfgPub.start publishes config:def (contract 1, 151 rows, 8
    categories) + config:fn; every scalar row reads its default on a fresh file; status ok; the prefix table lists 47 entries; levels.max
    60 asks first (danger), cuts the file list to the first 60 default levels, max 60 at once and after the reload routine; levels.scale
    110 -> level 1 = 55 (x1.1 in file + table), back to 100 = the list exactly, the same value twice = "already" (no compounding); max 100
    extends back to exactly the default; a 200% list extends at 200%; max 50 survives SkillCfg.load; a 0.1-era file (no perk.*) with the
    old 50 table still upgrades, a 0.3+ one keeps 50; multiplier 2 / trigger jump (skill:dj:key republished) / fell.enabled applied by the
    reload routine; part OFF asks, ON does not; ignorePlaced OFF and creativeXp ON ask; typed values outside the clamps refused
    (feedbackMs 100, fell.radius 17, 1.5 in an int row); check hooks (levels 0,5 / 101 entries refused, 10,20,30 accepted then Default;
    Exploration and unknown skills refused in the bonus lists, allowed in bridge.addxp.skills; alchemy.tierXp with 6 entries or a word);
    tables: block add (the loader's EXACT has it) / remove, Exploration and Combat rules refused, prefix tset, combat.role add (ROLE has
    it); export code; config-changes.log, config-history copies, versions; History restore preview lists no "not restored" curve row;
    comments kept; notifyOn without SkyyMenu (all ON; quiet hides only xpGain / doubleDrop / extraPotion) and with a fake registry
    (its answers used, quiet moved once with onlyIfUnset); regSetting writes settings:def.
  FIX ROUND (2026-09-25, review findings; second scratch harness, 26 checks, deleted afterwards): 80 classes under -Xverify:all; fresh
    file byte-identical; max 50 survives SkillCfg.load; a NON-uniform 100-level list: max 60 -> 40 -> 100 and 40 -> 60 -> 50 -> 100 give
    the exact list back; after a curve-size change or a hand edit (kit reload op) the raise follows the default shape; an 80 list cut to
    50 and raised to 90 = 51-80 exact + 81-90 along the default; the default list 60 -> 100 = exactly the default. Race replayed
    deterministically: an unrelated dirty save taking the arm between customSet and the kit's levels= edit puts the 100 table back, the
    levels= save then runs no reload, a plain re-arm (no force) leaves the table behind the file, SkillKitArm.run (force) brings table ==
    file; a spare forced re-arm changes nothing. Help texts of combat.min / combat.max / perk.exploration.staminaPerLevel / levels.max.
  UNVERIFIED (needs the game): the "Skills" page in SkyyMenu 0.3 Server Setup (8 tabs, 151 rows, table views, the curve rows' TextField +
    Set / Less / More); entry=item on alchemy.xp / smithing.xp against the live item map (the bare JVM has none); the kit saves and
    SkillKitArm on HytaleServer.SCHEDULED_EXECUTOR; /skills reload's kit reload op with a real admin; every Settings gate with SkyyMenu 0.3
    (level-up / next / late-coin lines, combat hints, double drop, extra potion, Tree felled, [Party]), the /skills quiet shortcut and the
    quiet move on a real profile.
0.4.2 (research/Tree-Fall-Spec.md''')
rep('''Run:   python build_skyyskills_0.4.2.py            -> SkyySkills/SkyySkills-0.4.2.jar
       python build_skyyskills_0.4.2.py --deploy   -> also copies''', '''Run:   python build_skyyskills_0.4.3.py            -> SkyySkills/SkyySkills-0.4.3.jar
       python build_skyyskills_0.4.3.py --deploy   -> also copies''')
rep('VERSION = "0.4.2"', 'VERSION = "0.4.3"')
after('''import skyymove as MV   # shared Skyy movement protocol (MoveSync class source; also used by SkyyAccessories 0.3)
''', '''import skyycfg as CFG   # 0.4.3: the admin config registry kit (tools/CONFIG-CONTRACT.md), generated into this jar
''')

# ================================================================ classes
after('''pft  = pool.makeClass(PKG + ".PartyFlushTask")
''', '''# 0.4.3: admin config hooks (reload routine, check= hooks, the custom: curve rows) - compiled after CFG.emit (they call CfgFn)
skit = pool.makeClass(PKG + ".SkillKit")
karm = pool.makeClass(PKG + ".SkillKitArm")
''')

# ================================================================ upgradeLevels: only for a 0.1 / 0.2 file (no perk.* key yet)
rep('''public static void upgradeLevels(java.util.Properties p) {{
  if (!OLD_LEVELS.equals(squash(p.getProperty("levels")))) return;
''', '''public static void upgradeLevels(java.util.Properties p) {{
  if (!OLD_LEVELS.equals(squash(p.getProperty("levels")))) return;
  java.util.Enumeration pe = p.propertyNames();
  while (pe.hasMoreElements()) {{
    if (String.valueOf(pe.nextElement()).startsWith("perk.")) return;
  }}
''')

# ================================================================ SkillStore: the Settings registry helpers (Settings-Spec 1.3 / 3.1)
after('''public static boolean quiet(java.util.UUID u) {
  return QUIET.containsKey(pkey(u));
}""", sto))
''', '''# 0.4.3 player Settings registry (SkyyMenu 0.2+, research/Settings-Spec.md 1.3 / 3.1). No SkyyMenu = no answer = today's behaviour:
# every switch ON except the three /skills quiet always hid (quiet still hides them). With SkyyMenu the old per-profile quiet flag is
# moved ONCE to the three switches (onlyIfUnset) at the first message check.
sto.addMethod(CtNewMethod.make(f"""
public static void moveQuiet(java.util.UUID u) {{
  String k = pkey(u);
  if (!QUIET.containsKey(k)) return;
  Object f = bridge().get("settings:fn:set");
  if (!(f instanceof java.util.function.Function)) return;
  java.util.function.Function sf = (java.util.function.Function) f;
  int ok = 0;
  if (Boolean.TRUE.equals(sf.apply(new Object[] {{ u, "skills.xpGain", Boolean.FALSE, Boolean.TRUE }}))) ok++;
  if (Boolean.TRUE.equals(sf.apply(new Object[] {{ u, "skills.doubleDrop", Boolean.FALSE, Boolean.TRUE }}))) ok++;
  if (Boolean.TRUE.equals(sf.apply(new Object[] {{ u, "skills.extraPotion", Boolean.FALSE, Boolean.TRUE }}))) ok++;
  if (ok == 3 && QUIET.remove(k) != null) {{ DIRTY.put(k, Boolean.TRUE); {PKG}.SkillCfg.info("moved /skills quiet of " + k + " to /settings"); }}
}}""", sto))
sto.addMethod(CtNewMethod.make("""
public static boolean notifyOn(java.util.UUID u, String key) {
  if (u == null || key == null) return true;
  try {
    Object f = bridge().get("settings:fn:get");
    if (f instanceof java.util.function.Function) {
      moveQuiet(u);
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  if (key.equals("skills.xpGain") || key.equals("skills.doubleDrop") || key.equals("skills.extraPotion")) return !quiet(u);
  return true;
}""", sto))
sto.addMethod(CtNewMethod.make("""
public static void regSetting(String key, String label, String cat, boolean def, String help) {
  try {
    Object[] a = new Object[] { "SkyySkills", key, label, cat, Boolean.valueOf(def), help };
    java.util.Map br = bridge();
    br.put("settings:def:" + key, a);
    Object f = br.get("settings:fn:register");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { }
}""", sto))
''')

# ================================================================ gates (only the sendMessage; the work stays)
rep('''  if (!{PKG}.SkillCfg.FEEDBACK) return;
  java.util.UUID u = pr.getUuid();
  if ({PKG}.SkillStore.quiet(u)) return;
''', '''  if (!{PKG}.SkillCfg.FEEDBACK) return;
  java.util.UUID u = pr.getUuid();
  if (!{PKG}.SkillStore.notifyOn(u, "skills.xpGain")) return;
''')
rep('''  java.util.UUID u = pr.getUuid();
  if ({PKG}.SkillStore.quiet(u)) return;
  if (add(u, slot, amt, from)) send(pr);
''', '''  java.util.UUID u = pr.getUuid();
  if (!{PKG}.SkillStore.notifyOn(u, "skills.xpGain")) return;
  if (add(u, slot, amt, from)) send(pr);
''')
rep('''  if (what == null || !{PKG}.PerkCfg.DD_MSG) return;
  java.util.UUID u = pr.getUuid();
  if ({PKG}.SkillStore.quiet(u)) return;
''', '''  if (what == null || !{PKG}.PerkCfg.DD_MSG) return;
  java.util.UUID u = pr.getUuid();
  if (!{PKG}.SkillStore.notifyOn(u, "skills.doubleDrop")) return;
''')
rep('''    if (what == null || {PKG}.SkillStore.quiet(u)) return;''',
    '''    if (what == null || !{PKG}.SkillStore.notifyOn(u, "skills.extraPotion")) return;''')
rep('''    if (fromWorld && {PKG}.FellCfg.MESSAGE && W.credited > 0 && !{PKG}.SkillStore.quiet(W.u)) {{''',
    '''    if (fromWorld && {PKG}.FellCfg.MESSAGE && W.credited > 0 && {PKG}.SkillStore.notifyOn(W.u, "skills.xpGain")) {{''')
rep('''public static void tellOnce({PR} pr, int bit, String text) {{
  try {{
    if (claimTold(pr.getUuid(), bit))''', '''public static void tellOnce({PR} pr, int bit, String text) {{
  try {{
    if (!{PKG}.SkillStore.notifyOn(pr.getUuid(), "skills.combatHints")) return;
    if (claimTold(pr.getUuid(), bit))''')
rep('''  if (r[1] > r[0]) {{
    {PKG}.SkillMsg.send(pr);
    {PKG}.PartyXp.send(pr);
    for (long lv = r[0] + 1L; lv <= r[1]; lv++) {{''', '''  if (r[1] > r[0]) {{
    {PKG}.SkillMsg.send(pr);
    {PKG}.PartyXp.send(pr);
    boolean lvOn = {PKG}.SkillStore.notifyOn(u, "skills.levelUp");
    for (long lv = r[0] + 1L; lv <= r[1]; lv++) {{''')
rep('''      pr.sendMessage({MSG}.raw("SKILL LEVEL UP  " + sk + " " + (lv - 1L) + " -> " + lv + reward).color("#ffc800"));''',
    '''      if (lvOn) pr.sendMessage({MSG}.raw("SKILL LEVEL UP  " + sk + " " + (lv - 1L) + " -> " + lv + reward).color("#ffc800"));''')
rep('''    pr.sendMessage({MSG}.raw(need > 0L ? "  next: " + sk''', '''    if (lvOn) pr.sendMessage({MSG}.raw(need > 0L ? "  next: " + sk''')
rep('''  if (paid != null && paid[2] > shown) pr.sendMessage(''', '''  if (paid != null && paid[2] > shown && {PKG}.SkillStore.notifyOn(u, "rewards.late")) pr.sendMessage(''')

# ================================================================ /skills quiet = the Settings shortcut (Settings-Spec 3.1)
rep('''protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  boolean q = {PKG}.SkillStore.toggleQuiet(pr.getUuid());''', '''protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  java.util.UUID u = pr.getUuid();
  Object f = {PKG}.SkillStore.bridge().get("settings:fn:set");
  if (f instanceof java.util.function.Function) {{
    java.util.function.Function sf = (java.util.function.Function) f;
    boolean anyOn = {PKG}.SkillStore.notifyOn(u, "skills.xpGain") || {PKG}.SkillStore.notifyOn(u, "skills.doubleDrop") || {PKG}.SkillStore.notifyOn(u, "skills.extraPotion");
    Boolean nv = anyOn ? Boolean.FALSE : Boolean.TRUE;
    int ok = 0;
    if (Boolean.TRUE.equals(sf.apply(new Object[] {{ u, "skills.xpGain", nv }}))) ok++;
    if (Boolean.TRUE.equals(sf.apply(new Object[] {{ u, "skills.doubleDrop", nv }}))) ok++;
    if (Boolean.TRUE.equals(sf.apply(new Object[] {{ u, "skills.extraPotion", nv }}))) ok++;
    if (ok < 3) {{ pr.sendMessage({MSG}.raw("[Skills] Could not save your settings - try again or tell an admin.")); return; }}
    pr.sendMessage({MSG}.raw(anyOn ? "[Skills] XP, double-drop and extra-potion messages hidden (level ups still show). One switch per message: /settings" : "[Skills] XP, double-drop and extra-potion messages shown. One switch per message: /settings"));
    return;
  }}
  boolean q = {PKG}.SkillStore.toggleQuiet(pr.getUuid());''')

# ================================================================ /skills reload: the kit's reload op first (hand edits logged), then as before
rep('''  String res = {PKG}.SkillCfg.load();
  {PKG}.Acro.djPublish();
  pr.sendMessage({MSG}.raw("[Skills] xp.properties reloaded: " + res));''', '''  // 0.4.3: xp.properties is read twice ON PURPOSE. The kit's reload op merges hand edits (logged via=file) and, only when it found some
  // or in-game edits were pending, runs SkillKit.reload again on its save task right after this reply; the synchronous load below keeps
  // the 0.4.2 reply text. Both passes are idempotent (SkillCfg.load is synchronized) - not an oversight.
  String kr = "";
  try {{
    Object o = new {PKG}.CfgFn().apply(new Object[] {{ "reload", pr.getUuid(), pr.getUsername(), "command" }});
    if (o instanceof Object[] && ((Object[]) o).length > 2 && ((Object[]) o)[2] != null) kr = " (" + String.valueOf(((Object[]) o)[2]) + ")";
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("config kit reload failed: " + t); }}
  String res = {PKG}.SkillCfg.load();
  {PKG}.Acro.djPublish();
  pr.sendMessage({MSG}.raw("[Skills] xp.properties reloaded: " + res + kr));''')

# ================================================================ the admin config schema + SkillKit (before the commands: ReloadCmd calls CfgFn)
KIT = r'''# ================= 0.4.3 ADMIN CONFIG (research/Server-Setup-Spec.md 4.9 + 5.7; tools/CONFIG-CONTRACT.md; kit = tools/skyycfg.py) =================
# Row = (key, label, category, type, default, min, max, opts, unit, flags, help, binding). Row key = file key of xp.properties (never
# renamed). Every scalar binds reload: (file line, then SkillKit.reload = the /skills reload path); min / max = the loader's clamps (typed
# values outside are refused; hand-edited files are still clamped by the loader). Defaults = what the loader uses today: checked below
# against the default xp.properties text (DEFAULTS), and the rows absent from it against PerkCfg's code defaults (0).
LEVELS_TEXT = ",".join(str(x) for x in LEVELS)
CFG_CATS = [("parts", "Parts"), ("general", "General"), ("levels", "Levels"), ("gathering", "Gathering"), ("combat", "Combat"),
            ("acrobatics", "Acrobatics"), ("perks", "Perks"), ("crafting", "Crafting")]
_LP = "live,part,danger"
CFG_ROWS = [
    # ---- parts (spec 3: the existing master keys; confirm only when switched OFF)
    ("acro.enabled", "Acrobatics", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: no Acrobatics XP and no movement bonuses (speed, jump, fall, dodge). Levels are kept.", "reload"),
    ("acro.doubleJump.enabled", "Double Jump", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: the Acrobatics tree's Double Jump node does nothing. Tree points are kept.", "reload"),
    ("perk.enabled", "Skill perks", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: no max health / stamina / mana, double drops or class damage from skill levels.", "reload"),
    ("alchemy.enabled", "Alchemy", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: the Alchemy Bench pays no Alchemy XP and the brewer perks stop. Levels are kept.", "reload"),
    ("smithing.smelt.enabled", "Smithing from smelting", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: the Furnace and the /craft Furnace tab pay no Smithing XP. Levels are kept.", "reload"),
    ("exploration.enabled", "Exploration XP", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: Exploration XP from SkyyExploration is refused. Levels are kept.", "reload"),
    ("fell.enabled", "Felled trees", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: only the log you break pays; logs that fall with the tree pay nothing.", "reload"),
    ("party.combatShare.enabled", "Party combat XP share", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: party members no longer get a share of a kill's class XP.", "reload"),
    ("bridge.bonus.enabled", "Skill tree bonuses", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: SkyyTrees Wisdom (more XP) and Fortune (double drops) nodes are ignored.", "reload"),
    # ---- general
    ("multiplier", "XP multiplier", "general", "dec", "1.0", "0", "100", "", "x", "live,danger",
     "Gathering, Acrobatics, Alchemy and Smithing XP times this (not XP from other mods, not Exploration).", "reload"),
    ("coinsPerLevel", "Coins per level up", "general", "int", "100", "0", "1000000000", "step=50", "coins", "live,danger",
     "A level up pays this x the new level in coins (needs SkyyCoins).", "reload"),
    ("feedback", "XP chat lines", "general", "bool", "true", "", "", "", "", "live",
     "Off: no '+12 Mining XP' lines for anyone. Each player can also hide them in /settings.", "reload"),
    ("feedbackMs", "XP line at most every", "general", "int", "2000", "500", "600000", "", "ms", "live,adv",
     "One combined +XP chat line per player per this many ms.", "reload"),
    ("creativeXp", "XP in creative mode", "general", "bool", "false", "", "", "", "", "live,danger",
     "On: players in creative mode earn skill XP too (easy to farm).", "reload;confirm=on"),
    ("ignorePlaced", "No XP from placed blocks", "general", "bool", "true", "", "", "", "", "live,danger",
     "Off lets players farm XP by placing and breaking blocks. Crops always pay when ripe.", "reload;confirm=off"),
    ("farmingNeedsRipe", "Crops pay only when ripe", "general", "bool", "true", "", "", "", "", "live",
     "Off: breaking a crop at any growth stage pays Farming XP.", "reload"),
    ("harvestCooldownMs", "Harvest XP per block every", "general", "int", "5000", "3000", "600000", "", "ms", "live,adv",
     "F-harvest and ripe crops: one block pays at most once per this many ms.", "reload"),
    ("party.combatShare.fraction", "Party share of kill XP", "general", "dec", "0.5", "0", "1", "", "", "live",
     "Share of the killer's class XP each nearby party member gets (0.5 = half). The killer keeps all.", "reload"),
    ("party.combatShare.radius", "Party share range", "general", "dec", "48", "1", "512", "", "blocks", "live",
     "Members within this many blocks of the killer, in the same world, get the share.", "reload"),
    ("party.combatShare.treeBonus", "Party share gets tree bonus", "general", "bool", "true", "", "", "", "", "live",
     "The member's own skill-tree XP bonus applies to their share.", "reload"),
    ("party.combatShare.message", "Party share chat line", "general", "bool", "true", "", "", "", "", "live",
     "The '[Party] +6 Archery XP from Skyy's kill' line. Players can also hide it in /settings.", "reload"),
    ("bridge.bonus.xpSkills", "Skills Wisdom nodes boost", "general", "text", BONUS_XP_SKILLS, "", "500", "", "", "live",
     "Skills whose XP SkyyTrees Wisdom nodes raise, comma separated. Never Exploration.", "reload;check=SkillKit.checkSkills"),
    ("bridge.bonus.addxpSkills", "Granted XP that gets Wisdom", "general", "text", BONUS_ADDXP_SKILLS, "", "500", "", "", "live,adv",
     "XP other mods grant gets the Wisdom bonus only in these skills (Cooking).", "reload;check=SkillKit.checkSkills"),
    ("bridge.addxp.skills", "Skills other mods may grant", "general", "text", BRIDGE_SKILLS, "", "500", "", "", "live,adv",
     "Skills skill:fn:addxp may pay (Collections rewards, Cooking). Exploration is always allowed.", "reload;check=SkillKit.checkSkills"),
    ("bridge.maxXpPerCall", "Largest XP grant per call", "general", "int", "500000", "1", "1000000000000", "", "", "live,adv",
     "A guard against a broken mod: one grant from another mod asks for at most this much.", "reload"),
    ("bridge.maxXpPerMinute", "Granted XP per player per minute", "general", "int", "3000000", "0", "1000000000000000", "", "", "live,adv",
     "All XP other mods grant to one player in a minute (0 = no cap).", "reload"),
    # ---- levels (the list first: import / restore apply rows in this order, the two curve rows read it)
    ("levels", "XP per level (list)", "levels", "text", LEVELS_TEXT, "1", "2000", "", "", "live,danger,adv",
     "XP each level needs, level 1 first; the count is the max level (1-100). Easier: the two rows below.",
     "reload;check=SkillKit.checkLevels"),
    ("levels.scale", "Level curve size", "levels", "int", "100", "10", "1000", "step=5", "%", "live,danger",
     "XP every level needs as % of the default curve (110 = 10% more). Rewrites the XP per level list.", "custom:SkillKit"),
    ("levels.max", "Max level", "levels", "int", "100", "1", "100", "step=5", "", "live,danger",
     "Cuts or extends the list (new levels follow the default curve, cut ones come back until a restart).", "custom:SkillKit"),
    # ---- gathering: the XP rules (key families) + felled trees
    ("block", "XP by exact block id", "gathering", "table", "", "", "", "text;type;Skill:XP or none", "", "live",
     "Exact id -> Mining:5 (Mining, Foraging or Farming) or none. Beats every other rule.", "reload;check=SkillKit.checkRule"),
    ("prefix", "XP by start of block id", "gathering", "table", "", "", "", "text;type;Skill:XP or none", "", "live",
     "Ore_Iron -> Mining:8. The longest matching start or end of an id wins.", "reload;check=SkillKit.checkRule"),
    ("suffix", "XP by end of block id", "gathering", "table", "", "", "", "text;type;Skill:XP or none", "", "live",
     "_Trunk -> Foraging:6. The longest matching start or end of an id wins.", "reload;check=SkillKit.checkRule"),
    ("fell.xpFactor", "Felled log XP", "gathering", "dec", "1.0", "0", "5", "", "x", "live",
     "A log that falls with the tree pays its hand-break Foraging XP times this.", "reload"),
    ("fell.leaves", "Felled leaves pay", "gathering", "bool", "true", "", "", "", "", "live",
     "Leaves that fall with the tree pay too (their XP times the leaf factor).", "reload"),
    ("fell.leafXpFactor", "Felled leaf XP", "gathering", "dec", "1.0", "0", "5", "", "x", "live",
     "A falling leaf pays its hand-break XP times this.", "reload"),
    ("fell.needLeaves", "Felled tree needs leaves", "gathering", "bool", "true", "", "", "", "", "live",
     "Only a tree touching natural leaves pays (never a log wall or a placed log tower).", "reload"),
    ("fell.underTrunk", "Digging under a trunk fells", "gathering", "bool", "true", "", "", "", "", "live",
     "Breaking the block under a trunk fells the tree and pays the same.", "reload"),
    ("fell.doubleDrops", "Felled logs roll double drops", "gathering", "bool", "true", "", "", "", "", "live",
     "Each falling log rolls the Foraging double-drop perk.", "reload"),
    ("fell.collections", "Felled logs count in Collections", "gathering", "bool", "true", "", "", "", "", "live",
     "Each falling log counts in SkyyCollections (source skills:felled).", "reload"),
    ("fell.nodes", "Felled logs roll tree nodes", "gathering", "bool", "true", "", "", "", "", "live",
     "Each falling log rolls the SkyyTrees per-log nodes (skill:on:felled).", "reload"),
    ("fell.message", "Tree felled chat line", "gathering", "bool", "true", "", "", "", "", "live",
     "'Tree felled: 19 logs (+156 Foraging XP)'. Players can hide it in /settings (Skill XP gains).", "reload"),
    ("fell.disabledWorlds", "No felled XP in these worlds", "gathering", "text", "", "", "2000", "", "", "live",
     "Comma list of exact world names where felled trees never pay.", "reload"),
    ("fell.extraTrees", "Also apple trees + extra trunks", "gathering", "bool", "false", "", "", "", "", "live",
     "Also pay apple fruit trees and the Bamboo / Ice Trunk_Full blocks Hytale's tree lists miss.", "reload"),
    ("placed.skipSaplings", "Planted saplings count as natural", "gathering", "bool", "true", "", "", "", "", "live",
     "A planted sapling is not marked as placed, so a replanted tree's base log pays.", "reload"),
    ("collections.doubleDrops", "Double drops count in Collections", "gathering", "bool", "false", "", "", "", "", "live",
     "Items from the double-drop perk also count in SkyyCollections (source skills:double).", "reload"),
    ("fell.radius", "Felled search: sideways", "gathering", "int", "8", "1", "16", "", "blocks", "live,adv",
     "How far sideways from the cut a tree's logs are searched.", "reload"),
    ("fell.height", "Felled search: height", "gathering", "int", "64", "1", "128", "", "blocks", "live,adv",
     "How far above the cut a tree's logs are searched.", "reload"),
    ("fell.maxLogs", "Felled search: most logs", "gathering", "int", "256", "1", "1024", "", "", "live,adv",
     "Most logs one felled tree can pay.", "reload"),
    ("fell.maxLeaves", "Felled search: most leaves", "gathering", "int", "384", "0", "2048", "", "", "live,adv",
     "Most leaves one felled tree can pay.", "reload"),
    ("fell.maxReads", "Felled search: block reads", "gathering", "int", "8000", "100", "100000", "", "", "live,adv",
     "Block reads per tree search (a server-load guard).", "reload"),
    ("fell.maxSnapshotsPerSecond", "Tree searches per second", "gathering", "int", "10", "1", "100", "", "", "live,adv",
     "Per player (a server-load guard).", "reload"),
    ("fell.maxWatchesPerPlayer", "Falling trees per player", "gathering", "int", "4", "1", "64", "", "", "live,adv",
     "Trees one player can have falling at the same time.", "reload"),
    ("fell.maxWatches", "Falling trees on the server", "gathering", "int", "64", "1", "1024", "", "", "live,adv",
     "Trees falling at the same time, all players together.", "reload"),
    ("fell.pollMs", "Falling tree checked every", "gathering", "int", "200", "50", "1000", "", "ms", "live,adv",
     "How often a falling tree is checked.", "reload"),
    ("fell.quietMs", "Falling tree done when still for", "gathering", "int", "3000", "500", "10000", "", "ms", "live,adv",
     "A falling tree that stays still this long is finished.", "reload"),
    ("fell.maxWatchMs", "Falling tree longest watch", "gathering", "int", "60000", "1000", "600000", "", "ms", "live,adv",
     "A falling tree is never watched longer than this.", "reload"),
    ("fell.memoryMs", "Remember who felled a tree", "gathering", "int", "60000", "0", "600000", "", "ms", "live,adv",
     "For other mods (skill:fn:felledBy).", "reload"),
    ("fell.debug", "Felled trees debug log", "gathering", "bool", "false", "", "", "", "", "live,adv",
     "One server-log line per tree search and per felled tree.", "reload"),
    # ---- combat (class skill XP per kill)
    ("combat.perHealth", "Combat XP per max health", "combat", "dec", "0.2", "0", "1000", "", "", "live",
     "Class XP per NPC kill = its max health x this, kept between the minimum and maximum below.", "reload"),
    ("combat.min", "Combat XP minimum", "combat", "int", "1", "0", "1000000000", "", "", "live",
     "Least class XP one kill pays. Keep it at or below the maximum, or every kill pays the maximum.", "reload"),
    ("combat.max", "Combat XP maximum", "combat", "int", "500", "0", "1000000000", "", "", "live",
     "Most class XP one kill pays (an NPC role's own XP beats it). Under the minimum, every kill pays it.", "reload"),
    ("combat.default", "Combat XP if health unknown", "combat", "int", "5", "0", "1000000000", "", "", "live",
     "Used when the NPC's max health cannot be read.", "reload"),
    ("combat.role", "Combat XP by NPC role", "combat", "table", "", "0", "1000000000", "int;type;XP", "", "live",
     "Exact XP for one NPC role. The server log names each new role on its first kill.", "reload"),
    ("combat.classWeaponOnly", "Only class weapons earn XP", "combat", "bool", "true", "", "", "", "", "live",
     "On: only the class's own weapons earn combat XP. Off: anything SkyyClasses lets the class use.", "reload"),
    # ---- acrobatics (+ Double Jump)
    ("acro.sprintXpPerBlock", "XP per block sprinted", "acrobatics", "dec", "0.25", "0", "100", "", "", "live",
     "Measured from the server position; teleports and launches pay nothing.", "reload"),
    ("acro.runXpPerBlock", "XP per block run", "acrobatics", "dec", "0.15", "0", "100", "", "", "live", "", "reload"),
    ("acro.walkXpPerBlock", "XP per block walked", "acrobatics", "dec", "0.05", "0", "100", "", "", "live",
     "Walking or sneaking.", "reload"),
    ("acro.maxSpeed", "Fastest paid movement", "acrobatics", "dec", "30", "5", "1000", "", "", "live,adv",
     "Blocks per second; a faster move (launch, lag burst) pays nothing.", "reload"),
    ("acro.teleportBlocks", "Teleport guard", "acrobatics", "dec", "8", "2", "1000", "", "blocks", "live,adv",
     "A move longer than this in one tick pays nothing.", "reload"),
    ("acro.jumpXp", "XP per jump", "acrobatics", "dec", "2", "0", "100000", "", "", "live",
     "At most one paid jump per cooldown, and only after moving (no XP for jumping in place).", "reload"),
    ("acro.jumpCooldownMs", "Paid jump cooldown", "acrobatics", "int", "800", "200", "600000", "", "ms", "live,adv", "", "reload"),
    ("acro.jumpMinMove", "Move between paid jumps", "acrobatics", "dec", "2.0", "0", "1000", "", "blocks", "live,adv", "", "reload"),
    ("acro.fallDamageXp", "XP per point of fall damage", "acrobatics", "dec", "10", "0", "100000", "", "", "live",
     "Only survived falls that hurt pay (counted as if you had 100 max health).", "reload"),
    ("acro.fallXpMax", "Most XP per landing", "acrobatics", "dec", "2000", "0", "1000000000", "", "", "live", "", "reload"),
    ("acro.fallMaxXpPerMinute", "Fall XP per minute cap", "acrobatics", "dec", "3000", "0", "1000000000", "", "", "live",
     "All fall XP in any 60 seconds (0 = no fall XP). Its own cap.", "reload"),
    ("acro.dodgeXp", "XP per dodge", "acrobatics", "dec", "3", "0", "100000", "", "", "live", "", "reload"),
    ("acro.dodgeCooldownMs", "Paid dodge cooldown", "acrobatics", "int", "400", "100", "600000", "", "ms", "live,adv", "", "reload"),
    ("acro.maxXpPerMinute", "Move XP per minute cap", "acrobatics", "dec", "240", "0", "1000000000", "", "", "live",
     "Running, jumping and dodging XP together in any 60 seconds.", "reload"),
    ("acro.feedbackMs", "Acrobatics XP line every", "acrobatics", "int", "30000", "2000", "3600000", "", "ms", "live,adv",
     "The +Acrobatics XP chat line shows at most once per this many ms.", "reload"),
    ("acro.speedPerLevel", "Speed per level", "acrobatics", "dec", "0.01", "0", "10", "", "", "live",
     "Share of vanilla speed added per Acrobatics level (0.01 = +1%).", "reload"),
    ("acro.jumpBlocksPerLevel", "Jump height per level", "acrobatics", "dec", "0.015", "0", "10", "", "blocks", "live", "", "reload"),
    ("acro.fallReductionPerLevel", "Less fall damage per level", "acrobatics", "dec", "0.005", "0", "1", "", "", "live",
     "0.005 = 0.5% less fall damage per level, up to the cap below.", "reload"),
    ("acro.fallReductionMax", "Fall damage reduction cap", "acrobatics", "dec", "0.8", "0", "1", "", "", "live", "", "reload"),
    ("acro.dodgeBoost", "Dodge push bonus", "acrobatics", "bool", "true", "", "", "", "", "live",
     "Off: no extra dodge push (dodge XP stays).", "reload"),
    ("acro.dodgeForce", "Dodge push force", "acrobatics", "dec", "13", "0", "1000", "", "", "live,adv",
     "The vanilla dodge force is 13.", "reload"),
    ("acro.dodgeBoostPerLevel", "Dodge push per level", "acrobatics", "dec", "0.004", "0", "1", "", "", "live", "", "reload"),
    ("acro.dodgeBoostMax", "Dodge push cap", "acrobatics", "dec", "0.5", "0", "2", "", "", "live", "", "reload"),
    ("acro.treeDodgeMax", "Tree dodge nodes cap", "acrobatics", "dec", "0.25", "0", "2", "", "", "live",
     "Most dodge push the Acrobatics tree's dodge nodes can add.", "reload"),
    ("acro.doubleJump.trigger", "Double Jump key", "acrobatics", "choice", "crouch", "", "", "crouch|Crouch,jump|Jump,both|Both", "",
     "live", "The key pressed in mid-air. Jump only works if the client reports it (spec test 5.0).", "reload"),
    ("acro.doubleJump.maxJumps", "Air jumps per airtime", "acrobatics", "int", "1", "1", "5", "", "", "live",
     "They recharge when you land, climb, swim or touch water.", "reload"),
    ("acro.doubleJump.maxFraction", "Air jump height cap", "acrobatics", "dec", "1.0", "0", "1.5", "", "", "live",
     "A share of the player's own jump height; the tree node's value is capped here.", "reload"),
    ("acro.doubleJump.maxBlocks", "Air jump height cap in blocks", "acrobatics", "dec", "3.5", "0.5", "10", "", "blocks", "live",
     "", "reload"),
    ("acro.doubleJump.forwardPush", "Air jump forward push", "acrobatics", "dec", "2.0", "0", "10", "", "", "live",
     "Extra blocks per second along the way you are moving.", "reload"),
    ("acro.doubleJump.stamina", "Air jump Stamina cost", "acrobatics", "dec", "2.0", "0", "1000", "", "", "live",
     "Too little Stamina = no air jump (the charge is kept).", "reload"),
    ("acro.doubleJump.staminaRegenDelay", "Stamina regen pause", "acrobatics", "dec", "0.3", "0", "10", "", "s", "live,adv",
     "0 = off.", "reload"),
    ("acro.doubleJump.cooldownMs", "Air jump cooldown", "acrobatics", "int", "250", "0", "60000", "", "ms", "live,adv", "", "reload"),
    ("acro.doubleJump.minAirMs", "Air time before an air jump", "acrobatics", "int", "100", "0", "5000", "", "ms", "live,adv",
     "", "reload"),
    ("acro.doubleJump.maxFallSpeed", "No air jump falling faster than", "acrobatics", "dec", "0", "-1000", "1000", "", "", "live,adv",
     "Blocks per second. 0 = the world's roll speed (vanilla 21), below 0 = no limit.", "reload"),
    ("acro.doubleJump.xp", "Acrobatics XP per air jump", "acrobatics", "dec", "0", "0", "1000", "", "", "live",
     "Counts against the move XP per minute cap.", "reload"),
    ("acro.doubleJump.fx", "Air jump sound + particles", "acrobatics", "bool", "true", "", "", "", "", "live", "", "reload"),
    ("acro.doubleJump.debug", "Double Jump debug chat", "acrobatics", "bool", "false", "", "", "", "", "live,adv",
     "Admins (skyyskills.admin) see a chat line per crouch / jump edge in mid-air.", "reload"),
    # ---- perks (the per-level flat layer)
    ("perk.doubleDropMax", "Double drop chance cap", "perks", "dec", "1.0", "0", "1", "", "", "live",
     "The double-drop chance never goes above this (1 = 100%), tree Fortune included.", "reload"),
    ("perk.doubleDropMessage", "Double drop chat line", "perks", "bool", "true", "", "", "", "", "live",
     "'Double drop x3!'. Players can also hide it in /settings.", "reload"),
]
# perk.<skill>.healthPerLevel / staminaPerLevel / manaPerLevel for all nine perk rows (PerkCfg.KEYS order, PerkCfg defaults), then the
# double-drop pair for the three gathering skills and the class damage pair; rows whose key is not in the default file (default 0) are adv
_PK = [("mining", "Mining"), ("foraging", "Foraging"), ("farming", "Farming"), ("combat", "Combat"), ("acrobatics", "Acrobatics"),
       ("alchemy", "Alchemy"), ("smithing", "Smithing"), ("cooking", "Cooking"), ("exploration", "Exploration")]
_PDEF = {"healthPerLevel": ["0", "0.1", "0.25", "0.1", "0", "0", "0", "0", "0"],
         "staminaPerLevel": ["0.05", "0", "0", "0", "0", "0", "0", "0", EXPL_STA_DEF],
         "manaPerLevel": ["0", "0", "0", "0", "0", "0.2", "0", "0", "0"]}
_PWORD = {"healthPerLevel": "health", "staminaPerLevel": "stamina", "manaPerLevel": "mana"}
_PDD = {"mining": ("0.005", ""), "foraging": ("0.005", "_Trunk"), "farming": ("0.005", "")}
for _i, (_k, _lab) in enumerate(_PK):
    _who = "your class skill" if _k == "combat" else _lab
    for _st in ("healthPerLevel", "staminaPerLevel", "manaPerLevel"):
        _key = "perk.%s.%s" % (_k, _st)
        _d = _PDEF[_st][_i]
        _in = ("\n" + _key + "=") in ("\n" + DEFAULTS)
        _help = "Max %s added per %s level (all skills add up)." % (_PWORD[_st], _who)
        if _key == "perk.exploration.staminaPerLevel":   # SkyyExploration 0.2.1+ reads this row over config:fn:SkyySkills op get (spec 4.18;
            # 0.2 still shows its own display.staminaPerLevel copy): the help must hold for both until the coordinator pins 0.2.1
            _help = "Max stamina per Exploration level. SkyyExploration 0.2.1+ shows this value on its /explore card."
        CFG_ROWS.append((_key, "%s: max %s per level" % (_lab, _PWORD[_st]), "perks", "dec", _d, "0", "10", "", "", "live" if _in else "live,adv",
                         _help, "reload"))
    if _k in _PDD:
        CFG_ROWS.append(("perk.%s.doubleDropPerLevel" % _k, "%s: double drop per level" % _lab, "perks", "dec", _PDD[_k][0], "0", "1", "", "",
                         "live", "Chance per level that a block paying %s XP drops twice (0.005 = 0.5%%)." % _lab, "reload"))
        CFG_ROWS.append(("perk.%s.doubleDropOnly" % _k, "%s: double drops only for" % _lab, "perks", "text", _PDD[_k][1], "", "2000", "", "",
                         "live", "Comma list of id parts: only blocks whose id contains one can double. Empty = all.", "reload"))
    if _k == "combat":
        CFG_ROWS.append(("perk.combat.damagePerLevel", "Class weapon damage per level", "perks", "dec", "0.002", "0", "1", "", "", "live",
                         "Extra damage with class weapons per class level (0.002 = +0.2%, +20% at 100).", "reload"))
        CFG_ROWS.append(("perk.combat.damageVsPlayers", "Class damage bonus vs players", "perks", "bool", "false", "", "", "", "",
                         "live,danger", "On: the class damage bonus also applies when hitting players.", "reload;confirm=on"))
CFG_ROWS += [
    # ---- crafting: alchemy + smithing
    ("alchemy.xp", "Alchemy XP per brew", "crafting", "table", "", "0", "1000000000000", "int;both;XP", "", "live",
     "Alchemy XP per finished Alchemy Bench craft, by output item (0 = none).", "reload;entry=item"),
    ("alchemy.tierXp", "Alchemy XP, unlisted recipes", "crafting", "text", ",".join(str(x) for x in ALCH_TIER), "1", "200", "", "", "live",
     "By bench tier I to V, comma separated, for Alchemy Bench recipes not in the table.", "reload;check=SkillKit.checkTier"),
    ("perk.alchemy.durationPerLevel", "Potion duration per level", "crafting", "dec", "0.01", "0", "10", "", "", "live",
     "Potion effects you drink last longer per Alchemy level (0.01 = +1%).", "reload"),
    ("perk.alchemy.durationMax", "Potion duration cap", "crafting", "dec", "1.0", "0", "10", "", "", "live",
     "The duration bonus never goes above this (1 = +100%).", "reload"),
    ("perk.alchemy.extend", "Effects that last longer", "crafting", "text", ",".join(ALCH_EXTEND), "", "2000", "", "", "live,adv",
     "Effect ids the duration perk may grow (instant heals cannot), comma separated.", "reload"),
    ("perk.alchemy.extraPotionPerLevel", "Extra potion chance per level", "crafting", "dec", "0.002", "0", "1", "", "", "live",
     "Chance per Alchemy level to brew one extra potion (0.002 = 0.2%).", "reload"),
    ("perk.alchemy.extraPotionMax", "Extra potion chance cap", "crafting", "dec", "0.25", "0", "1", "", "", "live", "", "reload"),
    ("perk.alchemy.extraPotionOnly", "Extra potion only for", "crafting", "text", "Potion_,Weapon_Bomb_", "", "2000", "", "", "live,adv",
     "Output id starts that can give an extra potion, comma separated.", "reload"),
    ("perk.alchemy.extraPotionNever", "Never an extra potion for", "crafting", "text", "Potion_Empty", "", "2000", "", "", "live,adv",
     "Output id starts that never give one, comma separated.", "reload"),
    ("smithing.vanillaFurnace", "Vanilla Furnace pays Smithing", "crafting", "bool", "true", "", "", "", "", "live",
     "Off: only the /craft Furnace tab (SkyySacks) pays Smithing XP.", "reload"),
    ("smithing.xp", "Smithing XP per smelted item", "crafting", "table", "", "0", "1000000000000", "int;both;XP", "", "live",
     "Smithing XP per finished smelted item, by output item (0 = none).", "reload;entry=item"),
    ("smithing.oreFactor", "Unlisted bar: ore XP factor", "crafting", "dec", "1.0", "0", "100", "", "x", "live",
     "An unlisted Ingredient_Bar_* pays the Mining XP of its ore times this (at least 1).", "reload"),
    ("smithing.smeltDefault", "Other smelted items", "crafting", "int", "1", "0", "1000000000", "", "", "live",
     "Smithing XP per item for every other Furnace output (0 = none).", "reload"),
]
# defaults = today's behaviour: every scalar row's default equals the default xp.properties line; the rows absent from it are exactly the
# 21 zero perk stats (PerkCfg's code default for them is 0.0)
from decimal import Decimal as _Dec
_dp = {}
for _ln in DEFAULTS.split("\n"):
    _t = _ln.strip()
    if _t and not _t.startswith("#") and "=" in _t:
        _dp[_t.split("=", 1)[0].strip()] = _t.split("=", 1)[1].strip()
_absent = []
for _r in CFG_ROWS:
    if _r[3] in ("table", "link", "action") or not _r[11].startswith("reload"):
        continue
    if _r[0] not in _dp:
        _absent.append(_r[0])
        assert _r[3] == "dec" and _r[4] == "0" and _r[0].startswith("perk.") and "adv" in _r[9], "row %s: not in the default file" % _r[0]
        continue
    _fv = _dp[_r[0]]
    if _r[3] in ("int", "dec"):
        assert _Dec(_fv) == _Dec(_r[4]), "row %s default %s != file %s" % (_r[0], _r[4], _fv)
    else:
        assert _fv == _r[4], "row %s default %r != file %r" % (_r[0], _r[4], _fv)
assert len(_absent) == 21, _absent
for _tk, _pfx in (("block", "block."), ("prefix", "prefix."), ("suffix", "suffix."), ("alchemy.xp", "alchemy.xp."), ("smithing.xp", "smithing.xp.")):
    assert any(_k.startswith(_pfx) for _k in _dp), "table %s has no default entries" % _tk
print("config rows: %d (%d tables), %d not in the default file (zero perk stats, adv)" % (len(CFG_ROWS), sum(1 for _r in CFG_ROWS if _r[3] == "table"), len(_absent)))
kit = CFG.emit(pool, PKG, MOD="SkyySkills", TITLE="Skills", VERSION=VERSION, NODE="skyyskills.admin", CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=["Skyy_SkyySkills/xp.properties"], RELOAD="SkillKit.reload", KEEP=20, DEFAULTS={"xp.properties": DEFAULTS},
               NOTE="Hand edits of xp.properties: /skills reload. Levels tab: curve size % and max level.")

# ================= SkillKit (0.4.3): reload routine, check= hooks, the custom: level-curve rows (spec 5.7) =================
# The kit calls these by reflection with no kit lock held (tools/CONFIG-CONTRACT.md guarantee 6); SkillKit takes no lock of its own
# except SkillDefs.setTable's (SkillCfg.load takes SkillCfg then SkillDefs, never the other way round) and its class lock around TAIL
# (tailFor / keepTail call nothing else, so no lock is ever taken inside it).
skit.addMethod(CtNewMethod.make(f"""
public static String reload() {{
  String r = {PKG}.SkillCfg.load();
  {PKG}.Acro.djPublish();
  return r;
}}""", skit))
# a levels= value -> long[] (1-100 entries, each > 0), else null (the loader's own rule: a bad list = the default table)
skit.addMethod(CtNewMethod.make("""
public static long[] parseList(String v) {
  if (v == null) return null;
  String t = v.trim();
  if (t.length() == 0) return null;
  String[] ps = t.split(",");
  if (ps.length < 1 || ps.length > 100) return null;
  long[] r = new long[ps.length];
  for (int i = 0; i < ps.length; i++) {
    long x = 0L;
    try { x = Long.parseLong(ps[i].trim()); } catch (Throwable e) { return null; }
    if (x <= 0L) return null;
    r[i] = x;
  }
  return r;
}""", skit))
# the list the curve rows start from: the kit's current levels= value (in-game edits still waiting for the 500 ms save included), else
# the running table
skit.addMethod(CtNewMethod.make(f"""
public static long[] curList() {{
  try {{
    Object o = new {PKG}.CfgFn().apply(new Object[] {{ "get", "levels" }});
    if (o instanceof String) {{
      long[] r = parseList((String) o);
      if (r != null) return r;
    }}
  }} catch (Throwable t) {{ }}
  long[] p = {PKG}.SkillDefs.PER;
  long[] c = new long[p.length];
  for (int i = 0; i < p.length; i++) c[i] = p[i];
  return c;
}}""", skit))
# total XP of the list as a percent of the default table over the same number of levels
skit.addMethod(CtNewMethod.make(f"""
public static long pctOf(long[] l) {{
  long[] d = {PKG}.SkillDefs.DEFAULT_PER;
  double a = 0.0;
  double b = 0.0;
  for (int i = 0; i < l.length; i++) {{
    a += (double) l[i];
    b += (double) (i < d.length ? d[i] : d[d.length - 1]);
  }}
  if (b <= 0.0) return 100L;
  return Math.round(a * 100.0 / b);
}}""", skit))
skit.addMethod(CtNewMethod.make("""
public static String join(long[] l) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < l.length; i++) {
    if (i > 0) sb.append(',');
    sb.append(l[i]);
  }
  return sb.toString();
}""", skit))
# cut to n levels, or extend: level i (0-based) = default[i] x (last kept level / default of that level) - the default list extends back
# to exactly the default
skit.addMethod(CtNewMethod.make(f"""
public static long[] withMax(long[] cur, int n) {{
  long[] d = {PKG}.SkillDefs.DEFAULT_PER;
  int len = cur.length;
  long[] r = new long[n];
  int li = len - 1 < d.length ? len - 1 : d.length - 1;
  double base = (double) d[li];
  double f = base > 0.0 ? (double) cur[len - 1] / base : 1.0;
  for (int i = 0; i < n; i++) {{
    if (i < len) {{ r[i] = cur[i]; continue; }}
    long di = i < d.length ? d[i] : d[d.length - 1];
    long v = Math.round((double) di * f);
    r[i] = v < 1L ? 1L : v;
  }}
  return r;
}}""", skit))
# TAIL = the full list before the last "Max level" cut, LAST = the list the last "Max level" change left (this server run only, in
# memory). While the list is still exactly LAST (so it starts with the kept levels), raising Max level again - Undo included - gives the
# cut levels back with their real values (a hand-edited or imported curve is not reshaped along the default curve); successive cuts
# (100 -> 60 -> 40) keep the longest list. Any other change of the list (curve size, the list row, a hand edit, History, an import) makes
# it differ from LAST, so the memory is ignored and the next cut starts a new one. SkillKit's class lock guards only these two arrays
# (no other lock is taken inside).
skit.addField(CtField.make("public static long[] TAIL = null;", skit))
skit.addField(CtField.make("public static long[] LAST = null;", skit))
skit.addMethod(CtNewMethod.make("""
public static boolean sameList(long[] a, long[] b) {
  if (a == null || b == null || a.length != b.length) return false;
  for (int i = 0; i < a.length; i++) if (a[i] != b[i]) return false;
  return true;
}""", skit))
skit.addMethod(CtNewMethod.make("""
public static synchronized long[] tailFor(long[] cur) {
  long[] t = TAIL;
  if (t == null || t.length <= cur.length || !sameList(cur, LAST)) return cur;
  for (int i = 0; i < cur.length; i++) if (t[i] != cur[i]) return cur;
  return t;
}""", skit))
skit.addMethod(CtNewMethod.make("""
public static synchronized void keepTail(long[] cur) {
  if (tailFor(cur) != cur) return;
  long[] c = new long[cur.length];
  for (int i = 0; i < cur.length; i++) c[i] = cur[i];
  TAIL = c;
}""", skit))
skit.addMethod(CtNewMethod.make("""
public static synchronized void setLast(long[] l) {
  long[] c = new long[l.length];
  for (int i = 0; i < l.length; i++) c[i] = l[i];
  LAST = c;
}""", skit))
# every level x (pct / current percent): the list's size becomes pct % of the default, its shape is kept; null = an entry above 1e15
skit.addMethod(CtNewMethod.make(f"""
public static long[] scaledTo(long[] cur, long pct) {{
  long[] d = {PKG}.SkillDefs.DEFAULT_PER;
  double a = 0.0;
  double b = 0.0;
  for (int i = 0; i < cur.length; i++) {{
    a += (double) cur[i];
    b += (double) (i < d.length ? d[i] : d[d.length - 1]);
  }}
  if (a <= 0.0 || b <= 0.0) return null;
  double f = ((double) pct / 100.0) * b / a;
  long[] r = new long[cur.length];
  for (int i = 0; i < cur.length; i++) {{
    double v = (double) cur[i] * f;
    if (v > 1.0E15) return null;
    long x = Math.round(v);
    r[i] = x < 1L ? 1L : x;
  }}
  return r;
}}""", skit))
# a custom: row's file lines never run a reload routine by themselves (kit v1), so the curve rows arm the global one for the next save of
# xp.properties: after the atomic write SkillCfg.load re-reads the file, so the running table always ends up equal to the file
skit.addMethod(CtNewMethod.make(f"""
public static void armReload() {{
  try {{
    java.util.HashSet s = new java.util.HashSet();
    s.add({PKG}.CfgRows.RELOAD);
    {PKG}.CfgFile.addReloads(0, s);
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not arm the xp.properties reload: " + t); }}
}}""", skit))
# ... and once more 200 ms later (after the kit has put the levels= line in memory): a save that happened to take the first arm before
# the line existed cannot leave the running table behind the file (set add is idempotent; saveSoon does nothing while a save is due).
# force: the kit's CfgFile.wants() ignores a pure reload arm (RLD without a dirty line - kit gap, reported), so if the dirty save that
# wrote the levels= line already ran before this re-arm (an unrelated save was due, or the scheduler ran this late), a plain saveSoon
# would find nothing to do and leave the arm waiting for the next unrelated edit. force makes that save run (the same force + reload arm
# the kit's own reload op uses): it merges the disk file (no diff = no log line), takes the arm and runs SkillKit.reload after the write.
# When the levels= save is still due, force just joins it (one save, one reload).
karm.addInterface(pool.get("java.lang.Runnable"))
karm.addConstructor(CtNewConstructor.make("public SkillKitArm() { }", karm))
karm.addMethod(CtNewMethod.make(f"""
public void run() {{
  {PKG}.SkillKit.armReload();
  try {{
    {PKG}.CfgFile.force(0);
    {PKG}.CfgFile.saveSoon(0);
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not re-arm the xp.properties reload: " + t); }}
}}""", karm))
skit.addMethod(CtNewMethod.make(f"""
public static void armLater() {{
  try {{ {HSV}.SCHEDULED_EXECUTOR.schedule(new {PKG}.SkillKitArm(), 200L, java.util.concurrent.TimeUnit.MILLISECONDS); }}
  catch (Throwable t) {{ }}
}}""", skit))
skit.addMethod(CtNewMethod.make("""
public static String customGet(String key) {
  long[] l = curList();
  if ("levels.max".equals(key)) return String.valueOf(l.length);
  if ("levels.scale".equals(key)) return String.valueOf(pctOf(l));
  return null;
}""", skit))
skit.addMethod(CtNewMethod.make(f"""
public static Object[] customSet(String key, String value) {{
  long n = -1L;
  try {{ n = Long.parseLong(value.trim()); }} catch (Throwable t) {{ return new Object[] {{ "bad", null, "Must be a whole number." }}; }}
  long[] cur = curList();
  int len = cur.length;
  long[] nl = null;
  String msg = "";
  if ("levels.max".equals(key)) {{
    if (n < 1L || n > 100L) return new Object[] {{ "bad", null, "Must be a whole number from 1 to 100." }};
    long[] src = cur;
    if (n < (long) len) keepTail(cur);
    else if (n > (long) len) src = tailFor(cur);
    nl = withMax(src, (int) n);
    setLast(nl);
    int back = src.length < (int) n ? src.length : (int) n;
    if (n < (long) len) msg = "Max level: " + n + " (was " + len + ") - levels above " + n + " removed; players keep their XP; raising it again gives them back exactly (until a restart or another curve change). Saved (applies now).";
    else if (n > (long) len && back > len) msg = "Max level: " + n + " (was " + len + ") - levels " + (len + 1) + " to " + back + " back with the XP they had before the cut" + (back < (int) n ? ", " + (back + 1) + " to " + n + " added along the default curve" : "") + ". Saved (applies now).";
    else if (n > (long) len) msg = "Max level: " + n + " (was " + len + ") - levels " + (len + 1) + " to " + n + " added along the default curve. Saved (applies now).";
    else msg = "Max level is already " + n + ".";
  }} else if ("levels.scale".equals(key)) {{
    if (n < 10L || n > 1000L) return new Object[] {{ "bad", null, "Must be a whole number from 10 to 1000%." }};
    nl = scaledTo(cur, n);
    if (nl == null) return new Object[] {{ "bad", null, "That would make a level need more than 1000000000000000 XP." }};
    msg = "Level curve size: " + pctOf(nl) + "% of the default - level 1 needs " + {PKG}.SkillDefs.fmt(nl[0]) + " XP, level " + nl.length + " needs " + {PKG}.SkillDefs.fmt(nl[nl.length - 1]) + ". Saved (applies now).";
  }} else {{
    return new Object[] {{ "unknown", null, "Unknown setting: " + key + "." }};
  }}
  {PKG}.SkillDefs.setTable(nl);
  armReload();
  armLater();
  String val = "levels.max".equals(key) ? String.valueOf(nl.length) : String.valueOf(pctOf(nl));
  return new Object[] {{ "ok", val, msg, new String[] {{ "levels", join(nl) }} }};
}}""", skit))
# History restore: the two curve rows follow the restored copy's levels= line (the levels row itself is restored first, row order)
skit.addMethod(CtNewMethod.make(f"""
public static String customRead(String key, java.util.Map vals) {{
  long[] l = null;
  try {{
    Object o = vals == null ? null : vals.get("levels");
    if (o instanceof String) l = parseList((String) o);
  }} catch (Throwable t) {{ l = null; }}
  if (l == null) l = {PKG}.SkillDefs.DEFAULT_PER;
  if ("levels.max".equals(key)) return String.valueOf(l.length);
  if ("levels.scale".equals(key)) return String.valueOf(pctOf(l));
  return null;
}}""", skit))
# ---- check= hooks: null = fine, text = refused with that reason (the kit keeps what the admin typed)
skit.addMethod(CtNewMethod.make("""
public static String checkLevels(String key, String v) {
  if (v == null) return null;
  String t = v.trim();
  String[] ps = t.split(",");
  if (t.length() == 0 || ps.length > 100) return "Write 1 to 100 numbers separated by commas: the XP for level 1, level 2, ...";
  long[] l = parseList(t);
  if (l == null) return "Every entry must be a whole number above 0, separated by commas.";
  for (int i = 0; i < l.length; i++) if (l[i] > 1000000000000000L) return "Level " + (i + 1) + " asks for more than 1000000000000000 XP.";
  return null;
}""", skit))
skit.addMethod(CtNewMethod.make(f"""
public static String checkRule(String key, String v) {{
  if (v == null) return null;
  if ({PKG}.SkillCfg.explRule(v)) return "Exploration XP only comes from other mods (SkyyExploration), never from blocks.";
  if ({PKG}.SkillCfg.parseRule(v) == null) return "Write Skill:XP with Mining, Foraging or Farming (like Mining:5), or none.";
  return null;
}}""", skit))
skit.addMethod(CtNewMethod.make(f"""
public static String checkSkills(String key, String v) {{
  if (v == null) return null;
  boolean bonus = key != null && key.startsWith("bridge.bonus.");
  String[] ps = v.split(",");
  for (int i = 0; i < ps.length; i++) {{
    String t = ps[i].trim();
    if (t.length() == 0) continue;
    int hit = -1;
    for (int s = 0; s < {PKG}.SkillDefs.N; s++) if ({PKG}.SkillDefs.NAMES[s].equalsIgnoreCase(t) || {PKG}.SkillDefs.LABELS[s].equalsIgnoreCase(t)) hit = s;
    if (hit < 0 || hit == {PKG}.SkillDefs.COMBAT) return "Unknown skill: " + t + ". Use names like Mining, Foraging, Farming, Alchemy, Smithing, Cooking.";
    if (bonus && hit == {PKG}.SkillDefs.EXPLORATION) return "Exploration never gets XP bonuses (Skyy's rule) - leave it out.";
  }}
  return null;
}}""", skit))
skit.addMethod(CtNewMethod.make("""
public static String checkTier(String key, String v) {
  if (v == null) return null;
  String t = v.trim();
  String[] ps = t.split(",");
  if (t.length() == 0 || ps.length > 5) return "Write 1 to 5 whole numbers separated by commas (bench tier I to V).";
  for (int i = 0; i < ps.length; i++) {
    long x = -1L;
    try { x = Long.parseLong(ps[i].trim()); } catch (Throwable e) { return "Every entry must be a whole number (0 or more)."; }
    if (x < 0L) return "Every entry must be a whole number (0 or more).";
  }
  return null;
}""", skit))

'''
before('''# ================= commands =================
''', KIT)

# ================================================================ plugin: Settings registration + config publication at the END of setup()
rep('''+ (fallOwner ? "" : "; fall damage bonuses are applied by " + {PKG}.MoveSync.bridge().get({PKG}.MoveSync.OWNER_FALL)));
}}""", pl))''', '''+ (fallOwner ? "" : "; fall damage bonuses are applied by " + {PKG}.MoveSync.bridge().get({PKG}.MoveSync.OWNER_FALL)));
  {PKG}.SkillStore.regSetting("skills.xpGain", "Skill XP gains", "skills", true, "+12 Mining XP (340/500) while you gather, fight, smelt, brew and move");
  {PKG}.SkillStore.regSetting("skills.levelUp", "Skill level-ups", "skills", true, "SKILL LEVEL UP with the coins it paid and the XP for the next level");
  {PKG}.SkillStore.regSetting("skills.doubleDrop", "Double drops", "skills", true, "Double drop x3! from the Mining, Foraging and Farming perks");
  {PKG}.SkillStore.regSetting("skills.extraPotion", "Extra potions", "skills", true, "Extra potion! from the Alchemy perk");
  {PKG}.SkillStore.regSetting("skills.combatHints", "No combat XP hints", "skills", true, "Why a kill gave no combat XP - once per reason each session");
  {PKG}.SkillStore.regSetting("rewards.late", "Late reward payouts", "coins", true, "Coins and XP paid later because another mod was not ready");
  {PKG}.CfgPub.start(getDataDirectory().getParent(), getLogger());
}}""", pl))''')
rep('''  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.flushDirty(); }} catch (Throwable t) {{ }}''', '''  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CfgPub.shutdown(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.flushDirty(); }} catch (Throwable t) {{ }}''')
rep('''fcf, fdf, frd, fsn, fwt, fel, fdr, fcr, ffn, esy, pcg, pxp, pft):
    c.writeFile(OUT)
print("classes written")''', '''fcf, fdf, frd, fsn, fwt, fel, fdr, fcr, ffn, esy, pcg, pxp, pft, skit, karm):
    c.writeFile(OUT)
kit.write(OUT)   # 0.4.3: the kit's deferred checks (SkillKit hooks) + its 7 classes
print("classes written")''')
rep('''Stats page per skill. Skill tree bonuses''', '''Stats page per skill. Every setting editable in game (SkyWynn Menu Server Setup, optional) and per-player chat switches (/settings, optional). Skill tree bonuses''')

# ================================================================ post-conditions
assert s.count('VERSION = "0.4.3"') == 1 and "0.4.2 - build script" not in s
assert s.count("import skyycfg as CFG") == 1 and s.count("kit = CFG.emit(") == 1 and s.count("kit.write(OUT)") == 1
assert s.index("kit = CFG.emit(") < s.index("skit.addMethod(") < s.index("# ================= commands =================")
assert s.index("public static String reload() {{") > s.index("public static void djPublish() {{")   # SkillKit.reload calls Acro.djPublish
assert s.index("# ================= commands =================") < s.index('new {PKG}.CfgFn().apply(new Object[] {{ "reload"')
assert s.count("{PKG}.CfgPub.start(getDataDirectory().getParent(), getLogger());") == 1 and s.count("{PKG}.CfgPub.shutdown();") == 1
# config publication is the LAST statement of setup() (after SkillCfg.load and the settings registration)
_su = s[s.index("public void setup() {{"):]
_su = _su[:_su.index('}}""", pl))')]
assert _su.rstrip().endswith("{PKG}.CfgPub.start(getDataDirectory().getParent(), getLogger());")
assert _su.index("{PKG}.SkillCfg.load();") < _su.index("regSetting(") < _su.index("CfgPub.start(")
for _k in ("skills.xpGain", "skills.levelUp", "skills.doubleDrop", "skills.extraPotion", "skills.combatHints", "rewards.late"):
    assert _su.count('regSetting("%s"' % _k) == 1, _k
for _k in ("party.invites", "tpa.requests", "msg.private"):
    assert _k not in s, "refusing switch built: " + _k
# every former quiet() gate became a notifyOn gate; quiet() stays only in its definition and notifyOn's no-SkyyMenu fallback
assert s.count("SkillStore.quiet(") == 0 and s.count("!quiet(u)") == 1 and s.count("public static boolean quiet(java.util.UUID u)") == 1
for _k, _n in (("skills.xpGain", 5), ("skills.levelUp", 1), ("skills.doubleDrop", 2), ("skills.extraPotion", 2), ("skills.combatHints", 1), ("rewards.late", 1)):
    assert s.count('notifyOn(') and s.count('"%s"' % _k) >= _n, _k
assert s.count("if (lvOn) pr.sendMessage(") == 2 and s.count('boolean lvOn = {PKG}.SkillStore.notifyOn(u, "skills.levelUp");') == 1
assert s.index("public static boolean notifyOn(java.util.UUID u, String key)") < s.index("public static void tellOnce({PR} pr, int bit, String text)")
assert s.index("public static void moveQuiet(java.util.UUID u)") < s.index("public static boolean notifyOn(java.util.UUID u, String key)")
assert s.count('if (String.valueOf(pe.nextElement()).startsWith("perk.")) return;') == 1
assert "skit, karm):" in s and s.count("registerSystem(") == REG0   # no new ECS system
for ident in re.findall(r"#(Skyy[A-Za-z0-9_]*)", s):
    assert "_" not in ident, "UI id with an underscore: " + ident
assert "--deploy" in s   # the script keeps its optional deploy switch; this workflow never passes it
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.4.2
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == "\r\n" else "LF"))
