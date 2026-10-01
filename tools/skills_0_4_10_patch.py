"""Derive SkyySkills/build_skyyskills_0.4.10.py from the LIVE generated SkyySkills/build_skyyskills_0.4.9.py (= the tools/deploy_set.py SET
pin since 2026-09-30 17:02; 0.4.9 came from 0.4.8 by tools/skills_0_4_9_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c;
never re-run skills_0_4_5 or older patches). Same style as skills_0_4_9_patch.py: rep(old, new) / cut(a, b, new) with asserted single
anchors, newline-agnostic; 0.4.9 stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_10_patch.py   then   python SkyySkills/build_skyyskills_0.4.10.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.10.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/skills0410/, deleted afterwards)

0.4.10 = CLASS SKILL XP MULTIPLIER. Skyy (2026-10-01, verbatim): "increase the class skill xp you get by a good bit, it levels slower than
everything else." research/Mob-Levels-Plan.md section 7: class weapon skill 25 needs ~3.0M XP (~84,000 kills at combat.perHealth 0.2) and
SkyyGear gates combat gear by that skill (Iron 15, Cobalt 25, Mithril 40).
  1. ONE new Server Setup row (Combat tab, first row): "Class skill XP multiplier" = xp.properties classSkill.xpMultiplier, dec 0-100,
     default 3, live (binding reload, like every SkyySkills scalar). Code default = file default = row default = 3.0 (SkillCfg.CLASS_MULT);
     the loader clamps to the row bounds (NaN / < 0 -> 0, > 100 -> 100, unparsable -> 3). A file without the key gets its own block
     appended ONCE (SkillCfg.ensureClass, the DivCfg.ensureSelf pattern) - no migration, nothing else in the file changes.
  2. ONE helper multiplies EVERY XP gain into a class skill: SkillCfg.classXp(slot, xp) - SkillDefs.isClass(slot) (Archery, Swordsmanship,
     Assassination, Shaman skill, Sorcery, Fury, Divinity) -> xp x CLASS_MULT, the fraction paid by chance (the PartyXp.amount /
     HealXp.amount rule: x2.5 on 1 XP = 2 or 3, on average 2.5); every other slot -> xp unchanged. Every path that writes into a class skill
     (all callers of SkillXp.gain*, read from 0.4.9):
       KillSys (kills)          cx = classXp(slot, combatXp(role, maxHp)): AFTER combat.perHealth / combat.min / combat.max / combat.role /
                                combat.default and the xp multiplier, BEFORE the killer's tree bonus (gain4).
       PartyXp.share            gets that same cx (the killer's kill XP), so each member's share = party.combatShare.fraction x the
                                MULTIPLIED kill XP, multiplied exactly once (PartyXp.one / gain4 do not multiply again).
       BridgeXp.offer           now pays BridgeXp.paid(u, slot, base, grant) = scaled(base) -> classXp -> tree bonus (the old three lines
                                moved into a helper the harness can call). Covers Priest heal XP on others AND on yourself
                                (HealXp.offer -> BridgeXp.offer(DIVINITY)) and any skill:fn:addxp grant into a class skill (an admin may
                                list one in bridge.addxp.skills; the default list has none). bridge.maxXpPerMinute (allow) counts the
                                multiplied XP, as it counts the xp multiplier and tree bonuses.
     NOT multiplied: gathering (blocks, felled trees, crops), Acrobatics, Alchemy, Smithing, Cooking, Exploration (never boosted - Skyy
     Q3), the admin /skills xp (raw: no multiplier, no tree bonus - its own chat line says so), the one-time legacy Combat -> class move.
  3. WHERE THE CAPS SIT (the version that keeps the multiplier honest):
       combat.max (500) is part of the per-kill formula, so the multiplier comes AFTER it: every kill pays exactly 3 x its 0.4.9 XP - a
       2,500 HP boss 500 -> 1,500, a 2 HP critter (combat.min 1) 1 -> 3, a combat.role override 100 -> 300. Multiplying before the clamp
       would cut big kills back to 500 (no gain at all for them) and lifting combat.max to 1500 by hand would still pay a 2 HP critter 1.
       divinity.healXpMaxPerMinute (300, Skyy's lock "cap stays 300 a minute", documented "counted before the xp multiplier") keeps
       counting the BASE heal XP (= the healing: 1,500 HP on others or 1,200 HP on yourself a minute); the multiplier comes after it, so a
       capped Priest earns 900 heal XP a minute at x3 instead of 300. Counting the multiplied XP would leave a busy Priest at 300 (x1).
       bridge.maxXpPerMinute (3,000,000, the broken-caller guard on XP actually paid) and bridge.maxXpPerCall (the caller's request size,
       before any multiplier) are unchanged; the first counts the multiplied XP.
  4. SHOWN: SkillCfg.load's text (= the "xp rules" part of the ready line and the /skills reload reply) says "class skill XP x3"; the
     Stats page of a class skill adds ". Class skill XP x3 on this server" to its how-to line (nothing at x1, "is off" at x0); the Divinity
     heal line shows the effective rates ("Healing pays 0.6 Divinity XP per HP on others, 0.75 on yourself (class skill XP x3, max 900 a
     minute)"; the 0.4.9 text at x1).
  5. ROW HELP made true next to the new row: multiplier (it multiplies every skill but Exploration, kills and grants included - 0.4.9 said
     "Gathering, Acrobatics, Alchemy and Smithing ... not XP from other mods", which the code never did), combat.max (paid before the class
     skill XP multiplier) and divinity.healXpMaxPerMinute (counted before the multipliers). No other row, no number, no generated asset,
     no page layout changes.
Everything else (commands, pages, bridge keys, players files, ManaMig, SPELL GEN, ManaCost / ManaGuard, Overall) is 0.4.9's - asserted below
and by the harness (class bytes 0.4.9 vs 0.4.10).
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.9.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.10.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.9"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
# the source must be the generated 0.4.9 of the EDITED lineage
assert 'VERSION = "0.4.9"' in s and "derived from the generated 0.4.8 by tools/skills_0_4_9_patch.py" in s, "not the live generated 0.4.9"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "classSkill.xpMultiplier" not in s and "CLASS_MULT" not in s and "classXp(" not in s
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    s = s.replace(old, new)


def cut(a, b, new):
    """replace s[index(a) : index(b)] (b itself stays) with new"""
    global s
    assert s.count(a) == 1 and s.count(b) == 1 and s.index(a) < s.index(b), (a[:60], b[:60])
    s = s[:s.index(a)] + new + s[s.index(b):]


def block(a, b):
    assert s.count(a) == 1 and s.count(b) == 1, (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


# blocks that must come out of this patch byte-identical: the pages (all but StatsPage.how), BridgeCfg .. SkillCfg up to load(), the rule
# resolver / scaled / combatXp / SkillStore / SkillClass, the Overall page, ManaMig, ManaGuard, SPELL GEN, SkillXp (gain4 never multiplies),
# HealXp (the cap and its maths), PartyXp's code, BridgeTask, the gathering / harvest systems
KEEP = [block("# ================= /skills page (inline", 'spg.addMethod(CtNewMethod.make(f"""\npublic static String how(int s) {{'),
        block("assert STBARW == SK_BIG_BAR_W", "# ================= OverallPage (0.4.6)"),
        block("# ================= BridgeCfg (0.4)", 'cfg.addMethod(CtNewMethod.make(f"""\npublic static synchronized String load() {{'),
        block('cfg.addMethod(CtNewMethod.make("""\npublic static long[] resolve(String id) {', "# ================= Overall (0.4.6)"),
        block("# ================= OverallPage (0.4.6)", "# ================= 0.4.3 ADMIN CONFIG"),
        block("# ---- ManaMig (point 2)", "# ---- ManaGuard (point 3)"),
        block("# ---- ManaGuard (point 3)", "# ================= SkillKit (0.4.3)"),
        block("# >>> SPELL GEN", "# <<< SPELL GEN"),
        block("# ================= SkillXp: award + level-up", "# ================= Brew (0.4)"),
        block("# ================= HealXp part 1", "# ================= Perks (0.3)"),
        block('hxp.addMethod(CtNewMethod.make(f"""\npublic static boolean offer(', "# ================= PartyXp (0.4.2 stage 2"),
        block('pxp.addField(CtField.make("public static volatile boolean FAILED_ONCE', "# ================= ECS systems"),
        block("# ================= BridgeTask (0.4)", "# BridgeXp.offer (0.4):"),
        block('event_system(bsy, "BreakSys"', "# Combat: DeathComponent added to an NPC killed by a player"),
        block("# ================= DivCfg (0.4.4)", "# the Stats page's Divinity \"Boosts right now\" line (spec 3.6)")]

# ---------------------------------------------------------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.9 - build script (derived from the generated 0.4.8 by tools/skills_0_4_9_patch.py - edit the patch, not this file;
0.4.8 was derived''', '''"""SkyySkills 0.4.10 - build script (derived from the generated 0.4.9 by tools/skills_0_4_10_patch.py - edit the patch, not this file;
0.4.9 was derived from the generated 0.4.8 by tools/skills_0_4_9_patch.py; 0.4.8 was derived''')
HEAD_0410 = '''0.4.10: CLASS SKILL XP MULTIPLIER (Skyy 2026-10-01: "increase the class skill xp you get by a good bit, it levels slower than everything
  else."; full notes in tools/skills_0_4_10_patch.py). ONE new Server Setup row, Combat tab: "Class skill XP multiplier" =
  classSkill.xpMultiplier (dec 0-100, default 3, live; appended once to an xp.properties without it, nothing else in the file changes).
  ONE helper, SkillCfg.classXp(slot, xp), multiplies every XP gain into a class skill (SkillDefs.isClass: Archery, Swordsmanship,
  Assassination, Shaman skill, Sorcery, Fury, Divinity; a fraction is paid by chance): kills (KillSys - AFTER combat.min / combat.max /
  combat.role / combat.default and the xp multiplier, so every kill pays exactly 3 x, a 500 XP kill 1,500; before the tree bonus), the
  party share (a fraction of that same kill XP - multiplied once) and every bridge award into a class skill (BridgeXp.paid inside
  BridgeXp.offer: Priest heal XP on others and on yourself, skill:fn:addxp grants if an admin lists a class skill; before the tree bonus
  and bridge.maxXpPerMinute). divinity.healXpMaxPerMinute keeps counting the BASE heal XP (Skyy's lock "cap stays 300 a minute", counted
  before the xp multiplier): it limits the healing, so a capped Priest earns 900 a minute at x3. Not multiplied: gathering, Acrobatics,
  Alchemy, Smithing, Cooking, Exploration, the admin /skills xp (raw), the legacy Combat move. Shown in SkillCfg.load's text (ready line,
  /skills reload), the class how-to line of the Stats page and the Divinity heal line (effective rates). Row help of multiplier /
  combat.max / divinity.healXpMaxPerMinute says where they sit.
'''
rep('''by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
0.4.9: EVERY CAST CHECKS WHAT IT SPENDS''', '''by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
''' + HEAD_0410 + '''0.4.9: EVERY CAST CHECKS WHAT IT SPENDS''')
rep('VERSION = "0.4.9"\n', 'VERSION = "0.4.10"\n')

# ---------------------------------------------------------------------------------------------------------------- point 1: the default block
rep('''OVL_LIT = json.dumps(OVL_DEFAULTS)
''', '''OVL_LIT = json.dumps(OVL_DEFAULTS)
# 0.4.10 (Skyy 2026-10-01: "increase the class skill xp you get by a good bit"): the class skill XP multiplier. Appended once to a file
# without classSkill.xpMultiplier (SkillCfg.ensureClass, the DivCfg.ensureSelf pattern); the code default (SkillCfg.CLASS_MULT) is the
# same number. No comment line here may look like a "#key=value" template line (the config kit uncomments those in place).
import re as _cre
CLS_MULT_DEF = "3.0"
CLS_L = []
CLS_L.append("# ---------- Class skill XP (SkyySkills 0.4.10) ----------")
CLS_L.append("# Comments must stay on their own lines.")
CLS_L.append("# The class skill XP multiplier: every XP gain into a class skill (Archery, Swordsmanship, Sorcery, Fury, Divinity, later")
CLS_L.append("# Assassination and the Shaman skill) is multiplied by it - kills, the party share, Priest heal XP (on others and on yourself)")
CLS_L.append("# and class skill XP another mod grants. It comes after each source's own numbers: after combat.min, combat.max and")
CLS_L.append("# combat.role (a 500 XP kill pays 1500 at 3) and after divinity.healXpMaxPerMinute (that cap counts the healing, before any")
CLS_L.append("# multiplier). It stacks with the XP multiplier at the top of this file; bridge.maxXpPerMinute counts the multiplied XP.")
CLS_L.append("# A fraction is paid by chance (2.5 times 1 XP = 2 or 3 XP). 0 = no class skill XP at all. Gathering, Acrobatics, Alchemy,")
CLS_L.append("# Smithing, Cooking and Exploration XP are not changed by it, and the admin /skills xp stays raw.")
CLS_L.append("classSkill.xpMultiplier=" + CLS_MULT_DEF)
L.append("")
L.extend(CLS_L)
CLS_DEFAULTS = "\\n".join(CLS_L) + "\\n"
assert all(ord(ch) < 128 for ch in CLS_DEFAULTS) and '"' not in CLS_DEFAULTS
assert [_ln for _ln in CLS_L if not _ln.startswith("#")] == ["classSkill.xpMultiplier=" + CLS_MULT_DEF]
assert not any(_cre.match(r"#\\s*[A-Za-z][A-Za-z0-9._-]*\\s*[=:]\\s*\\S+\\s*$", _ln) for _ln in CLS_L), "a comment looks like a template line"
CLS_LIT = json.dumps(CLS_DEFAULTS)
''')

# ---------------------------------------------------------------------------------------------------------------- point 2: SkillCfg
rep('''cfg.addField(CtField.make("public static volatile double MULT = 1.0;", cfg))
''', '''cfg.addField(CtField.make("public static volatile double MULT = 1.0;", cfg))
# 0.4.10: classSkill.xpMultiplier (the loader clamps it to the row bounds 0-100) and the block ensureClass appends to an old file
cfg.addField(CtField.make("public static volatile double CLASS_MULT = " + CLS_MULT_DEF + ";", cfg))
cfg.addField(CtField.make("public static final String CLASS_DEFAULTS = " + CLS_LIT + ";", cfg))
''')
CFG_0410 = '''# 0.4.10 (tools/skills_0_4_10_patch.py point 1): append the class skill XP block once to a file without classSkill.xpMultiplier (the
# DivCfg.ensureSelf pattern; this load reads the code default 3.0 for the missing key, the next load reads the appended line)
cfg.addMethod(CtNewMethod.make(f"""
public static void ensureClass(java.util.Properties p) {{
  if (p.getProperty("classSkill.xpMultiplier") != null) return;
  try {{
    java.nio.file.Files.write(FILE, ("\\\\n" + CLASS_DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    info("xp.properties: appended the class skill XP section (classSkill.xpMultiplier={CLS_MULT_DEF})");
  }} catch (Throwable t) {{ warn("could not append the class skill XP section to xp.properties: " + t); }}
}}""", cfg))
# 0.4.10 point 2: THE class skill XP multiplier - every XP gain into a class skill goes through here (KillSys for kills and so the party
# share, BridgeXp.paid for heals and grants). xp x CLASS_MULT for a class slot, the fraction paid by chance (PartyXp.amount rule; a product
# within 1e-9 of a whole number counts as that number, so 1.1 x 10 is 11, never 12); any other slot, or xp <= 0, unchanged / 0.
cfg.addMethod(CtNewMethod.make(f"""
public static long classXp(int slot, long xp) {{
  if (xp <= 0L) return 0L;
  if (!{PKG}.SkillDefs.isClass(slot)) return xp;
  double m = CLASS_MULT;
  if (m == 1.0) return xp;
  if (!(m > 0.0)) return 0L;
  double x = (double) xp * m;
  if (x >= 9.0E15) return 9000000000000000L;
  double r = Math.rint(x);
  if (Math.abs(x - r) < 1.0E-9) x = r;
  long w = (long) Math.floor(x);
  double f = x - (double) w;
  if (f > 0.0 && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < f) w++;
  return w;
}}""", cfg))
# "x3" / "x2.5" / "x0" (load text, ready line)
cfg.addMethod(CtNewMethod.make(f"""
public static String classText() {{
  return "x" + {PKG}.DivCfg.num(CLASS_MULT);
}}""", cfg))
# the Stats page's class how-to line ends with this: "" at x1, ". Class skill XP x3 on this server", ". Class skill XP is off on this server"
cfg.addMethod(CtNewMethod.make(f"""
public static String classHow() {{
  double m = CLASS_MULT;
  if (m == 1.0) return "";
  if (!(m > 0.0)) return ". Class skill XP is off on this server";
  return ". Class skill XP x" + {PKG}.DivCfg.num(m) + " on this server";
}}""", cfg))
'''
rep('''cfg.addMethod(CtNewMethod.make(f"""
public static synchronized String load() {{''', CFG_0410 + '''cfg.addMethod(CtNewMethod.make(f"""
public static synchronized String load() {{''')
rep('''    {PKG}.OverallCfg.ensureDefaults(p);
''', '''    {PKG}.OverallCfg.ensureDefaults(p);
    ensureClass(p);
''')
rep('''    C_DEFAULT = lng(p, "combat.default", 5L);
''', '''    C_DEFAULT = lng(p, "combat.default", 5L);
    double cm = dbl(p, "classSkill.xpMultiplier", {CLS_MULT_DEF});
    CLASS_MULT = (Double.isNaN(cm) || cm < 0.0) ? 0.0 : (cm > 100.0 ? 100.0 : cm);
''')
rep('''" role rule(s), acrobatics "''', '''" role rule(s), class skill XP " + classText() + ", acrobatics "''')

# ---------------------------------------------------------------------------------------------------------------- point 2: kills (+ the party share)
rep('''    long cx = {PKG}.SkillCfg.combatXp(role, maxHp);
    {PKG}.SkillXp.gain(pr, slot, cx);
    {PKG}.PartyXp.share(pr, k, s, cx);''', '''    long cx = {PKG}.SkillCfg.classXp(slot, {PKG}.SkillCfg.combatXp(role, maxHp));
    {PKG}.SkillXp.gain(pr, slot, cx);
    {PKG}.PartyXp.share(pr, k, s, cx);''')
rep('''# Combat: DeathComponent added to an NPC killed by a player
''', '''# Combat: DeathComponent added to an NPC killed by a player
# 0.4.10: cx = the kill XP (combat.* clamps, then the xp multiplier) x the class skill XP multiplier (SkillCfg.classXp; slot is always a
# class slot - killSlot); the party share is a fraction of this same cx, so it is multiplied exactly once
''')

# ---------------------------------------------------------------------------------------------------------------- point 2: bridge awards (heals, grants)
rep('''# multiplier, no tree bonus (still inside bridge.maxXpPerMinute).
bxp.addMethod(CtNewMethod.make(f"""''', '''# multiplier, no tree bonus (still inside bridge.maxXpPerMinute).
# 0.4.10: what an accepted offer pays = paid(): the xp multiplier, then the class skill XP multiplier (SkillCfg.classXp: Priest heal XP on
# others / on yourself and grants into a class skill; any other slot unchanged), then the tree bonus. bridge.maxXpPerMinute (allow) counts
# this paid number; bridge.maxXpPerCall and divinity.healXpMaxPerMinute (HealXp.take, before this call) count the base. Any thread, no I/O.
bxp.addMethod(CtNewMethod.make(f"""
public static long paid(java.util.UUID u, int slot, long base, boolean grant) {{
  if (base <= 0L || slot < 0 || slot >= {PKG}.SkillDefs.N) return 0L;
  boolean canBoost = {PKG}.SkillDefs.boostable(slot);
  long amt = canBoost ? {PKG}.SkillCfg.scaled(base) : base;
  if (canBoost) amt = {PKG}.SkillCfg.classXp(slot, amt);
  if (canBoost && (!grant || {PKG}.SkillBonus.grantBonus(slot))) amt = {PKG}.SkillBonus.boost(u, slot, amt);
  return amt;
}}""", bxp))
bxp.addMethod(CtNewMethod.make(f"""''')
rep('''  boolean canBoost = {PKG}.SkillDefs.boostable(slot);
  long amt = canBoost ? {PKG}.SkillCfg.scaled(base) : base;
  if (canBoost && (!grant || {PKG}.SkillBonus.grantBonus(slot))) amt = {PKG}.SkillBonus.boost(u, slot, amt);
  if (amt <= 0L) return 0L;
  if (!allow(u, amt))''', '''  long amt = paid(u, slot, base, grant);
  if (amt <= 0L) return 0L;
  if (!allow(u, amt))''')
rep('''# keeps it for the rest of the window - fails closed, see the header). Any thread, no I/O, never throws.
hxp.addMethod(CtNewMethod.make(f"""
public static boolean offer(''', '''# keeps it for the rest of the window - fails closed, see the header). Any thread, no I/O, never throws.
# 0.4.10: unchanged - the cap still counts the BASE heal XP (the healing); BridgeXp.offer -> BridgeXp.paid applies the xp multiplier and the
# class skill XP multiplier after it (a capped Priest earns divinity.healXpMaxPerMinute x 3 at the default x3)
hxp.addMethod(CtNewMethod.make(f"""
public static boolean offer(''')

# ---------------------------------------------------------------------------------------------------------------- point 4: Stats page texts
rep('''  return "Earn XP by defeating monsters with " + c + " weapons" + (w == null ? "" : " - " + w) + {PKG}.PartyXp.howText();''',
    '''  return "Earn XP by defeating monsters with " + c + " weapons" + (w == null ? "" : " - " + w) + {PKG}.PartyXp.howText() + {PKG}.SkillCfg.classHow();''')
cut('''# the Stats page's Divinity "Boosts right now" line (spec 3.6)
''', "# ================= XbowCfg (0.4.5)", '''# the Stats page's Divinity "Boosts right now" line (spec 3.6). 0.4.10: the EFFECTIVE rates with the class skill XP multiplier (the cap counts
# the base heal XP, so a capped minute pays cap x the multiplier); at x1 exactly the 0.4.9 text
dvc.addMethod(CtNewMethod.make(f"""
public static String statsLine() {{
  if (!on()) return "Divinity XP from healing is off on this server";
  double m = {PKG}.SkillCfg.CLASS_MULT;
  if (m == 1.0) return "Healing pays " + num(PER_HP) + " Divinity XP per HP on others, " + num(PER_HP_SELF) + " on yourself" + (MAX_MIN > 0L ? " (max " + MAX_MIN + " a minute)" : "");
  if (!(m > 0.0)) return "Healing pays no Divinity XP on this server (class skill XP x0)";
  return "Healing pays " + num(PER_HP * m) + " Divinity XP per HP on others, " + num(PER_HP_SELF * m) + " on yourself (class skill XP x" + num(m) + (MAX_MIN > 0L ? ", max " + num((double) MAX_MIN * m) + " a minute" : "") + ")";
}}""", dvc))

''')

# ---------------------------------------------------------------------------------------------------------------- point 1 + 5: config rows
rep('''    ("multiplier", "XP multiplier", "general", "dec", "1.0", "0", "100", "", "x", "live,danger",
     "Gathering, Acrobatics, Alchemy and Smithing XP times this (not XP from other mods, not Exploration).", "reload"),''',
    '''    ("multiplier", "XP multiplier", "general", "dec", "1.0", "0", "100", "", "x", "live,danger",
     "Every skill's XP times this - kills, heals and other mods' grants too (not Exploration).", "reload"),''')
rep('''    # ---- combat (class skill XP per kill)
    ("combat.perHealth",''', '''    # ---- combat (class skill XP per kill)
    # 0.4.10 (Skyy 2026-10-01): every XP gain into a class skill x this (SkillCfg.classXp) - after combat.max and the heal cap
    ("classSkill.xpMultiplier", "Class skill XP multiplier", "combat", "dec", CLS_MULT_DEF, "0", "100", "", "x", "live",
     "Class skill XP from kills, party shares and Priest heals times this, on top of the XP multiplier.", "reload"),
    ("combat.perHealth",''')
rep('''     "Most class XP one kill pays (an NPC role's own XP beats it). Under the minimum, every kill pays it.", "reload"),''',
    '''     "Most class XP one kill pays before the class skill XP multiplier (an NPC role's own XP beats it).", "reload"),''')
rep('''     "Most Divinity XP healing pays one Priest in 60 s (0 = no limit). Kills are not counted.", "reload"),''',
    '''     "Most heal XP per Priest in 60 s, before the XP multipliers (0 = no limit). Kills are not counted.", "reload"),''')
rep('''assert len(CFG_ROWS) == 173, ("0.4.5 had 159 rows + 10 Overall Level / base Mana rows (Overall-Level-Spec 4.9) + divinity.healXpPerHpSelf + "
                              "3 crossbow extras (meter, sound, hint); 0.4.8: - mana.magicBase / mana.magicClasses + the mana.classBase "
                              "table + the read-only spell.manaDivisor, got %d" % len(CFG_ROWS))   # 0.4.6 / 0.4.8''',
    '''assert len(CFG_ROWS) == 174, ("0.4.5 had 159 rows + 10 Overall Level / base Mana rows (Overall-Level-Spec 4.9) + divinity.healXpPerHpSelf + "
                              "3 crossbow extras (meter, sound, hint); 0.4.8: - mana.magicBase / mana.magicClasses + the mana.classBase "
                              "table + the read-only spell.manaDivisor; 0.4.10: + classSkill.xpMultiplier, got %d" % len(CFG_ROWS))   # 0.4.6 / 0.4.8 / 0.4.10
# 0.4.10: the new key once in CFG_ROWS (Combat tab, the first combat row), in the default file and in its own appended block (an old file
# gets it too), and nowhere else; row / code / file default agree
assert sum(1 for _r in CFG_ROWS if _r[0] == "classSkill.xpMultiplier") == 1 and _dp.get("classSkill.xpMultiplier") == CLS_MULT_DEF \\
    and ("\\nclassSkill.xpMultiplier=" + CLS_MULT_DEF + "\\n") in ("\\n" + CLS_DEFAULTS)
assert [_r[0] for _r in CFG_ROWS if _r[2] == "combat"][0] == "classSkill.xpMultiplier"
assert [_r for _r in CFG_ROWS if _r[0] == "classSkill.xpMultiplier"][0][3:10] == ("dec", CLS_MULT_DEF, "0", "100", "", "x", "live")''')
rep('''for _nm, _txt in (("DIV", DIV_DEFAULTS), ("DIVS", DIVS_DEFAULTS), ("XBOW", XBOW_DEFAULTS), ("XBOWX", XBOWX_DEFAULTS), ("OVL", OVL_DEFAULTS)):''',
    '''for _nm, _txt in (("DIV", DIV_DEFAULTS), ("DIVS", DIVS_DEFAULTS), ("XBOW", XBOW_DEFAULTS), ("XBOWX", XBOWX_DEFAULTS), ("OVL", OVL_DEFAULTS),
                  ("CLS", CLS_DEFAULTS)):''')

# ---------------------------------------------------------------------------------------------------------------- manifest
rep('''Priests earn Divinity XP for healing others and themselves.''',
    '''Priests earn Divinity XP for healing others and themselves. Class skills earn 3x XP by default (Class skill XP multiplier in Server Setup: kills, party shares and Priest heals; gathering skills unchanged).''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
for k in KEEP:
    assert s.count(k) == 1, "a block that must stay byte-identical changed: " + k[:100]
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "systems / commands changed"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
# the multiplier has exactly two call sites in code (KillSys, BridgeXp.paid) besides its own definition; nothing else writes class XP
assert s.count("{PKG}.SkillCfg.classXp(") == 2 and s.count("public static long classXp(int slot, long xp)") == 1
assert s.count("long amt = paid(u, slot, base, grant);") == 1 and s.count("{PKG}.SkillCfg.scaled(base)") == 1
assert s.count("ensureClass(p);") == 1 and s.count("CLASS_MULT = (Double.isNaN(cm)") == 1
assert s.index("public static long classXp(int slot, long xp)") < s.index("public static synchronized String load() {{")
assert s.index("public static String num(double v)") < s.index("public static String classText()"), "DivCfg.num must exist first"
assert s.index("public static long paid(java.util.UUID u, int slot, long base, boolean grant)") < s.index(
    "public static long offer(java.util.UUID u, int slot, long base, String source, String expect")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars")
