"""Derive SkyySkills/build_skyyskills_0.4.11.py from the LIVE generated SkyySkills/build_skyyskills_0.4.10.py (= the tools/deploy_set.py SET
pin; 0.4.10 came from 0.4.9 by tools/skills_0_4_10_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_10_patch.py: rep(old, new) / cut(a, b, new) with asserted single anchors,
newline-agnostic; 0.4.10 stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_11_patch.py   then   python SkyySkills/build_skyyskills_0.4.11.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.11.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/skills0411/, deleted afterwards)

0.4.11 = PRIEST HEAL XP IS THE XP THE PLAYER GETS. Skyy (2026-10-01, verbatim): "make healing others give 1xp per hp, and self gives 1.25
xp per hp healed." (after reading "Healing pays 0.6 Divinity XP per HP on others, 0.75 on yourself (class skill XP x3, max 900 a minute)"
on the Divinity skill page; OPEN-QUESTIONS LOCKED 2026-10-01: 1 / 1.25 what the player gets, the healing XP cap stays 900 a minute, kill
XP unchanged).
DESIGN (the cleanest of the two the task offered): the three heal rows become the FINAL heal XP - Priest heal XP no longer goes through
the class skill XP multiplier (0.4.10's classSkill.xpMultiplier, default 3):
    divinity.healXpPerHp         0.2 -> 1      Divinity XP per HP healed on others
    divinity.healXpPerHpSelf     0.25 -> 1.25  Divinity XP per HP healed on yourself
    divinity.healXpMaxPerMinute  300 -> 900    most heal XP a Priest gets in 60 s
  so all three rows read the number the player gets (no 0.3333 values, no maths). The other way (keep base rows, show final values) would
  need rows that show one number and store another, and a cap that silently changes whenever the class multiplier row is edited.
  What the multiplier still does: kills, the party share and class skill grants (skill:fn:addxp) - unchanged from 0.4.10. At x1 or x5 a
  Priest still gets exactly 1 / 1.25 per HP and at most 900 a minute from healing; only their KILL XP changes (x1: a 100 HP kill 20,
  x5: 100). The general "XP multiplier" row (multiplier, default 1) and the player's own tree XP bonus still come after the heal cap, as
  they did in every version (the row help says "kills, heals and other mods' grants too"); at the defaults they change nothing.
  1. CODE: BridgeXp.paidX(u, slot, base, grant, cls) / offerX(..., grant, cls) = 0.4.10's paid / offer with one switch: cls false skips
     SkillCfg.classXp. paid(...) / offer(...) keep their signatures and pass cls = true (grants, crafting, Exploration - byte-for-byte
     0.4.10's maths). HealXp.offer (the only heal path: skill:fn:healxp -> HealXp.offer) calls offerX(..., false, false). The cap
     (HealXp.take, divinity.healXpMaxPerMinute) still counts heal XP before the xp multiplier = the final heal XP at the defaults.
     DivCfg code defaults 1.0 / 1.25 / 900 (= file = row defaults).
  2. SHOWN: the Divinity Stats page line (DivCfg.statsLine) is the plain rates again: "Healing pays 1 Divinity XP per HP on others, 1.25 on
     yourself (max 900 a minute)" at any class skill XP multiplier; only a general XP multiplier other than 1 shows effective numbers
     ("... 2 ..., 2.5 on yourself (XP multiplier x2, max 1800 a minute)"; x0: "Healing pays no Divinity XP on this server (XP multiplier
     x0)"). The ready line (DivCfg.text) reads the new values ("1 XP per HP healed on others, 1.25 on yourself, up to 900 a minute").
  3. ROWS (Combat tab): the three heal rows get the new defaults, help "the XP the Priest gets ... not multiplied by the class skill XP
     multiplier"; healXpPerHp's label says "on others" (like the self row says "on self"); classSkill.xpMultiplier's help drops
     "Priest heals". No row added or removed (174), no other row, no generated asset, no page layout changes.
  4. DEFAULT FILE: the heal blocks carry 1 / 1.25 / 900 and comments that say healing is not multiplied; the class skill XP block's
     comment drops heal XP; a marker comment (HEAL_MARK) above the Divinity block, so a fresh file never updates.
  5. ONE-TIME UPDATE of an existing xp.properties (HealMig.run, setup() after ManaMig.run and BEFORE SkillCfg.load and the config kit;
     the SkyyClasses 0.1.10 migrate0110 / SkyyGear 0.1.1 machinery method for method): a heal key whose effective line (the last one, a
     one-line entry) still holds EXACTLY the old default text 0.2 / 0.25 / 300 gets the new default (value text only: key, separator, CR
     kept); any other value is kept and logged ("... kept (an admin's value) - it now counts as the XP the Priest gets ..."); a missing
     line stays missing (the new code default applies). The 0.4.10 DEFAULT comment lines that 0.4.11 rewrites (HEAL_DOC, exact whole-line
     matches only) get the 0.4.11 text; edited comments stay. The new text must parse to the same Properties except the updated keys (else
     WARN, untouched). CfgHist.snapshot keeps the old file as a History version ("before the 0.4.11 heal XP update") and the rewrite only
     happens once config-history really holds those bytes (else WARN, untouched, the next start retries); CfgRows.atomicWrite (ISO-8859-1
     bytes in and out, CRLF kept); one config-changes.log line per changed key in the kit's scalar-row format (name "SkyySkills 0.4.11",
     via update) so Server Setup -> Changes can Undo each. Runs once: the marker comment on its own line above the Divinity block (above
     the comment run directly on top of the first divinity.healXp.enabled / heal key line), else at the top of the file; a file holding
     the marker is never touched again. The OLD LOCK "Cap stays 300 a minute" (2026-09-25) meant the base cap at x1 - the player-facing
     900 a minute stays; the default comment that said it is one of the rewritten lines.
Everything else (kills / KillSys, the party share, grants, gathering, commands, pages, bridge keys incl. skill:fn:healxp = the SkyyClasses
0.1.10 contract, players files, ManaMig, SPELL GEN, ManaCost / ManaGuard, Overall) is 0.4.10's - asserted below and by the harness (class
bytes 0.4.10 vs 0.4.11).
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.10.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.11.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.10"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
# the source must be the generated 0.4.10 of the EDITED lineage
assert 'VERSION = "0.4.10"' in s and "derived from the generated 0.4.9 by tools/skills_0_4_10_patch.py" in s, "not the live generated 0.4.10"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "HealMig" not in s and "paidX(" not in s and "offerX(" not in s and "HEAL_MARK" not in s
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


# blocks that must come out of this patch byte-identical: the pages, the rule resolver / scaled / combatXp / classXp, SkillStore /
# SkillClass, Overall, ManaMig, ManaGuard, SPELL GEN, SkillXp, HealXp part 1 (the cap maths), PartyXp, BridgeTask, KillSys + the gathering
# systems, skill:fn:addxp, skill:fn:healxp's code (the SkyyClasses contract)
KEEP = [block("# ================= /skills page (inline", "# ================= OverallPage (0.4.6)"),
        block('cfg.addMethod(CtNewMethod.make("""\npublic static long[] resolve(String id) {', "# ================= Overall (0.4.6)"),
        block("# ================= OverallPage (0.4.6)", "# ================= 0.4.3 ADMIN CONFIG"),
        block("# ---- ManaMig (point 2)", "# ---- ManaGuard (point 3)"),
        block("# ---- ManaGuard (point 3)", "# ================= SkillKit (0.4.3)"),
        block("# >>> SPELL GEN", "# <<< SPELL GEN"),
        block("# ================= SkillXp: award + level-up", "# ================= Brew (0.4)"),
        block("# ================= HealXp part 1", "# ================= Perks (0.3)"),
        block('pxp.addField(CtField.make("public static volatile boolean FAILED_ONCE', "# ================= ECS systems"),
        block("# ================= BridgeTask (0.4)", "# BridgeXp.offer (0.4):"),
        block("# ================= ECS systems", "# ================= EnvSys (0.4.2, Tree-Fall-Spec 2.4)"),   # BreakSys .. KillSys
        # skill:fn:healxp's whole code (selfArg + apply): the SkyyClasses 0.1.10 contract
        block('hfn.addConstructor(CtNewConstructor.make("public SkillHealFn() { }", hfn))', "# ================= skill:fn:craftxp (0.4)")]

# ---------------------------------------------------------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.10 - build script (derived from the generated 0.4.9 by tools/skills_0_4_10_patch.py - edit the patch, not this file;
0.4.9 was derived''', '''"""SkyySkills 0.4.11 - build script (derived from the generated 0.4.10 by tools/skills_0_4_11_patch.py - edit the patch, not this file;
0.4.10 was derived from the generated 0.4.9 by tools/skills_0_4_10_patch.py; 0.4.9 was derived''')
HEAD_0411 = '''0.4.11: PRIEST HEAL XP IS THE XP THE PLAYER GETS (Skyy 2026-10-01: "make healing others give 1xp per hp, and self gives 1.25 xp per hp
  healed."; full notes in tools/skills_0_4_11_patch.py). The three heal rows are the FINAL heal XP - healing no longer goes through the
  class skill XP multiplier: divinity.healXpPerHp 0.2 -> 1, divinity.healXpPerHpSelf 0.25 -> 1.25, divinity.healXpMaxPerMinute 300 -> 900
  (what a Priest gets at the defaults, any class skill XP multiplier). BridgeXp.paidX / offerX (cls switch; paid / offer = cls true, the
  0.4.10 maths for grants / crafting); HealXp.offer -> offerX(..., false). Kills, the party share and grants keep the class skill XP
  multiplier. The Divinity Stats line: "Healing pays 1 Divinity XP per HP on others, 1.25 on yourself (max 900 a minute)" (effective
  numbers only when the general XP multiplier is not 1). Row help / default comments say healing is not multiplied. One-time update of
  an existing xp.properties (HealMig.run before SkillCfg.load): untouched 0.2 / 0.25 / 300 lines -> 1 / 1.25 / 900, an admin's values
  kept and logged, the 0.4.10 default comment lines rewritten (exact matches), History version first (verified), one change-log line
  per key (Undo), marker comment = runs once, ISO-8859-1 / CRLF byte-safe.
'''
rep('''by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
0.4.10: CLASS SKILL XP MULTIPLIER''', '''by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
''' + HEAD_0411 + '''0.4.10: CLASS SKILL XP MULTIPLIER''')
rep('VERSION = "0.4.10"\n', 'VERSION = "0.4.11"\n')

# ---------------------------------------------------------------------------------------------------------------- point 4: default file
# (0.4.10 default comment line, 0.4.11 line) - the default blocks get the new line; HealMig rewrites an EXACT old line of an existing file
HEAL_DOC = [
    ("# LOCKED Skyy 2026-09-25: healing themself pays 0.25 XP per HP (was 0). Others stay 0.2. Cap stays 300 a minute.",
     "# LOCKED Skyy 2026-10-01 (SkyySkills 0.4.11): 1 XP per HP on others, 1.25 on yourself, at most 900 a minute - what the Priest gets."),
    ("# healXpMaxPerMinute: most heal XP per Priest in one 60 second window, counted before the xp",
     "# healXpMaxPerMinute: most heal XP per Priest in one 60 second window. Heal XP is NOT multiplied by classSkill.xpMultiplier;"),
    ("# multiplier (0 = no limit). Kills pay Divinity XP like every class skill (combat.* keys) and are not counted here.",
     "# the xp multiplier comes after the cap (0 = no limit). Kills pay Divinity XP like every class skill and are not counted here."),
    ("# Both count against divinity.healXpMaxPerMinute.",
     "# Both count against divinity.healXpMaxPerMinute. Both are the XP the Priest gets (0.4.11: not multiplied by classSkill.xpMultiplier)."),
    ("# The class skill XP multiplier: every XP gain into a class skill (Archery, Swordsmanship, Sorcery, Fury, Divinity, later",
     "# The class skill XP multiplier: XP gains into a class skill (Archery, Swordsmanship, Sorcery, Fury, Divinity, later"),
    ("# Assassination and the Shaman skill) is multiplied by it - kills, the party share, Priest heal XP (on others and on yourself)",
     "# Assassination and the Shaman skill) are multiplied by it - kills, the party share and class skill XP another mod grants."),
    ("# and class skill XP another mod grants. It comes after each source's own numbers: after combat.min, combat.max and",
     "# Priest heal XP is NOT multiplied (SkyySkills 0.4.11): the divinity heal XP numbers above are what the Priest gets."),
    ("# combat.role (a 500 XP kill pays 1500 at 3) and after divinity.healXpMaxPerMinute (that cap counts the healing, before any",
     "# It comes after each kill's own numbers: after combat.min, combat.max and combat.role (a 500 XP kill pays 1500 at 3)."),
    ("# multiplier). It stacks with the XP multiplier at the top of this file; bridge.maxXpPerMinute counts the multiplied XP.",
     "# It stacks with the XP multiplier at the top of this file; bridge.maxXpPerMinute counts the multiplied XP."),
    ("# A fraction is paid by chance (2.5 times 1 XP = 2 or 3 XP). 0 = no class skill XP at all. Gathering, Acrobatics, Alchemy,",
     "# A fraction is paid by chance (2.5 times 1 XP = 2 or 3 XP). 0 = no class skill XP from kills. Gathering, Acrobatics, Alchemy,"),
]
_TPL = re.compile(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$")
for _o, _n in HEAL_DOC:
    assert _o != _n and _n.startswith("# ") and all(32 <= ord(c) < 127 for c in _n) and '"' not in _n and "\\" not in _n, _n
    assert not _TPL.match(_n), "a new comment looks like a #key=value template line: " + _n
for _o, _n in HEAL_DOC[:3]:
    rep('DIV_L.append("%s")\n' % _o, 'DIV_L.append("%s")\n' % _n)
rep('DIVS_L.append("%s")\n' % HEAL_DOC[3][0], 'DIVS_L.append("%s")\n' % HEAL_DOC[3][1])
for _o, _n in HEAL_DOC[4:]:
    rep('CLS_L.append("%s")\n' % _o, 'CLS_L.append("%s")\n' % _n)
rep('''DIV_L.append("divinity.healXpPerHp=0.2")
DIV_L.append("divinity.healXpMaxPerMinute=300")
L.append("")
L.extend(DIV_L)
''', '''DIV_L.append("divinity.healXpPerHp=" + HEAL_PER_HP_DEF)
DIV_L.append("divinity.healXpMaxPerMinute=" + HEAL_MAX_DEF)
L.append("")
L.append(HEAL_MARK)   # 0.4.11: the default file carries the heal XP update marker (HealMig never touches a fresh file); NOT in DIV_L
L.extend(DIV_L)
''')
rep('DIVS_L.append("divinity.healXpPerHpSelf=0.25")\n', 'DIVS_L.append("divinity.healXpPerHpSelf=" + HEAL_SELF_DEF)\n')
rep('''# 0.4.4: Divinity XP from Priest heals (research/Classes-Berserker-Priest-Spec.md 3.4 / 3.5). Appended once to a file without
# divinity.healXp.enabled (DivCfg.ensureDefaults).
DIV_L = []
''', '''# 0.4.11 (Skyy 2026-10-01: "make healing others give 1xp per hp, and self gives 1.25 xp per hp healed."): the heal rows are the FINAL heal
# XP (not multiplied by classSkill.xpMultiplier). Defaults shared by the file, the rows, DivCfg and HealMig.
HEAL_PER_HP_DEF, HEAL_SELF_DEF, HEAL_MAX_DEF = "1", "1.25", "900"
assert (float(HEAL_PER_HP_DEF), float(HEAL_SELF_DEF), int(HEAL_MAX_DEF)) == (1.0, 1.25, 900)
# HealMig's one-time update: (key, the 0.4.10 default text, the 0.4.11 default text, what the value means now)
HEAL_MG = [("divinity.healXpPerHp", "0.2", HEAL_PER_HP_DEF, "the Divinity XP per HP healed on others the Priest gets"),
           ("divinity.healXpPerHpSelf", "0.25", HEAL_SELF_DEF, "the Divinity XP per HP healed on themself the Priest gets"),
           ("divinity.healXpMaxPerMinute", "300", HEAL_MAX_DEF, "the most heal XP the Priest gets in a minute")]
# the marker comment (in the 0.4.11 default file above the Divinity block and in every updated file): a doc comment with spaces and no "=",
# so the config kit never takes it for a "#key=value" template line; HealMig looks for HEAL_MARK_ID in comment lines only
HEAL_MARK_ID = "SkyySkills 0.4.11 heal XP update"
HEAL_MARK = ("# %s (Skyy 2026-10-01): divinity.healXpPerHp, divinity.healXpPerHpSelf and divinity.healXpMaxPerMinute are the Divinity XP "
             "the Priest gets (defaults 1, 1.25 and 900 a minute) - the class skill XP multiplier no longer applies to healing" % HEAL_MARK_ID)
# the 0.4.10 default comment lines 0.4.11 rewrote (old, new): HealMig replaces an EXACT old line of an existing file with the new one
HEAL_DOC = ''' + repr(HEAL_DOC) + '''
assert all(32 <= ord(_c) < 127 for _c in HEAL_MARK) and "=" not in HEAL_MARK and HEAL_MARK.startswith("# ") and '"' not in HEAL_MARK
assert not any(HEAL_MARK_ID in _n for _o, _n in HEAL_DOC) and len(set(_o for _o, _n in HEAL_DOC)) == len(HEAL_DOC)
# 0.4.4: Divinity XP from Priest heals (research/Classes-Berserker-Priest-Spec.md 3.4 / 3.5). Appended once to a file without
# divinity.healXp.enabled (DivCfg.ensureDefaults).
DIV_L = []
''')
rep('''CLS_DEFAULTS = "\\n".join(CLS_L) + "\\n"
''', '''CLS_DEFAULTS = "\\n".join(CLS_L) + "\\n"
# 0.4.11: every rewritten comment line is in a 0.4.11 default block, no old one is left in them
assert all(_n in DIV_L + DIVS_L + CLS_L and _o not in DIV_L + DIVS_L + CLS_L for _o, _n in HEAL_DOC)
''')

# ---------------------------------------------------------------------------------------------------------------- point 1: DivCfg defaults
rep('''for decl in ("boolean ON = true", "double PER_HP = 0.2", "long MAX_MIN = 300L", "double PER_HP_SELF = 0.25"):''',
    '''# 0.4.11: the FINAL heal XP defaults (= HEAL_PER_HP_DEF / HEAL_MAX_DEF / HEAL_SELF_DEF; asserted)
assert (HEAL_PER_HP_DEF, HEAL_MAX_DEF, HEAL_SELF_DEF) == ("1", "900", "1.25")
for decl in ("boolean ON = true", "double PER_HP = 1.0", "long MAX_MIN = 900L", "double PER_HP_SELF = 1.25"):''')
rep('''  double r = {PKG}.SkillCfg.dbl(p, "divinity.healXpPerHp", 0.2);''', '''  double r = {PKG}.SkillCfg.dbl(p, "divinity.healXpPerHp", 1.0);''')
rep('''  double rs = {PKG}.SkillCfg.dbl(p, "divinity.healXpPerHpSelf", 0.25);''', '''  double rs = {PKG}.SkillCfg.dbl(p, "divinity.healXpPerHpSelf", 1.25);''')
rep('''  long m = {PKG}.SkillCfg.lng(p, "divinity.healXpMaxPerMinute", 300L);''', '''  long m = {PKG}.SkillCfg.lng(p, "divinity.healXpMaxPerMinute", 900L);''')
rep('''    {PKG}.SkillCfg.info("xp.properties: appended the Divinity self-heal section (divinity.healXpPerHpSelf=0.25)");''',
    '''    {PKG}.SkillCfg.info("xp.properties: appended the Divinity self-heal section (divinity.healXpPerHpSelf={HEAL_SELF_DEF})");''')

# ---------------------------------------------------------------------------------------------------------------- point 2: the Stats line
cut('''# the Stats page's Divinity "Boosts right now" line (spec 3.6). 0.4.10: the EFFECTIVE rates''', "# ================= XbowCfg (0.4.5)",
    '''# the Stats page's Divinity "Boosts right now" line (spec 3.6). 0.4.11: heal XP is not multiplied by the class skill XP multiplier, so the
# rows ARE what the Priest gets: "Healing pays 1 Divinity XP per HP on others, 1.25 on yourself (max 900 a minute)" (the 0.4.9 text) at
# any class skill XP multiplier. Only the general XP multiplier (SkillCfg.MULT, after the cap) shows effective numbers when it is not 1.
dvc.addMethod(CtNewMethod.make(f"""
public static String statsLine() {{
  if (!on()) return "Divinity XP from healing is off on this server";
  double m = {PKG}.SkillCfg.MULT;
  if (m == 1.0) return "Healing pays " + num(PER_HP) + " Divinity XP per HP on others, " + num(PER_HP_SELF) + " on yourself" + (MAX_MIN > 0L ? " (max " + MAX_MIN + " a minute)" : "");
  if (!(m > 0.0)) return "Healing pays no Divinity XP on this server (XP multiplier x0)";
  return "Healing pays " + num(PER_HP * m) + " Divinity XP per HP on others, " + num(PER_HP_SELF * m) + " on yourself (XP multiplier x" + num(m) + (MAX_MIN > 0L ? ", max " + num((double) MAX_MIN * m) + " a minute" : "") + ")";
}}""", dvc))

''')

# ---------------------------------------------------------------------------------------------------------------- point 1: BridgeXp + HealXp
rep('''# 0.4.10: what an accepted offer pays = paid(): the xp multiplier, then the class skill XP multiplier (SkillCfg.classXp: Priest heal XP on
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
}}""", bxp))''', '''# 0.4.10: what an accepted offer pays = paid(): the xp multiplier, then the class skill XP multiplier (SkillCfg.classXp: grants into a class
# skill; any other slot unchanged), then the tree bonus. bridge.maxXpPerMinute (allow) counts this paid number; bridge.maxXpPerCall and
# divinity.healXpMaxPerMinute (HealXp.take, before this call) count the base. Any thread, no I/O.
# 0.4.11: paidX(..., cls) - cls false skips the class skill XP multiplier (Priest heal XP: HealXp.offer -> offerX(..., false)); paid = cls true
bxp.addMethod(CtNewMethod.make(f"""
public static long paidX(java.util.UUID u, int slot, long base, boolean grant, boolean cls) {{
  if (base <= 0L || slot < 0 || slot >= {PKG}.SkillDefs.N) return 0L;
  boolean canBoost = {PKG}.SkillDefs.boostable(slot);
  long amt = canBoost ? {PKG}.SkillCfg.scaled(base) : base;
  if (canBoost && cls) amt = {PKG}.SkillCfg.classXp(slot, amt);
  if (canBoost && (!grant || {PKG}.SkillBonus.grantBonus(slot))) amt = {PKG}.SkillBonus.boost(u, slot, amt);
  return amt;
}}""", bxp))
bxp.addMethod(CtNewMethod.make("""
public static long paid(java.util.UUID u, int slot, long base, boolean grant) {
  return paidX(u, slot, base, grant, true);
}""", bxp))''')
rep('''bxp.addMethod(CtNewMethod.make(f"""
public static long offer(java.util.UUID u, int slot, long base, String source, String expect, {CRR} rc, int units, boolean grant) {{''',
    '''# 0.4.11: offerX = 0.4.10's offer with the cls switch (paidX); offer(...) = offerX(..., true) for every caller but HealXp.offer
bxp.addMethod(CtNewMethod.make(f"""
public static long offerX(java.util.UUID u, int slot, long base, String source, String expect, {CRR} rc, int units, boolean grant, boolean cls) {{''')
rep('''  long amt = paid(u, slot, base, grant);
  if (amt <= 0L) return 0L;
  if (!allow(u, amt)) {{ warnLimited(u, "bridge.maxXpPerMinute " + {PKG}.BridgeCfg.PER_MIN + " reached - refused " + amt + " XP from " + source); return -1L; }}
  w.execute(new {PKG}.BridgeTask(u, slot, amt, k, source == null ? "?" : source, rc, units));
  return amt;
}}""", bxp))
''', '''  long amt = paidX(u, slot, base, grant, cls);
  if (amt <= 0L) return 0L;
  if (!allow(u, amt)) {{ warnLimited(u, "bridge.maxXpPerMinute " + {PKG}.BridgeCfg.PER_MIN + " reached - refused " + amt + " XP from " + source); return -1L; }}
  w.execute(new {PKG}.BridgeTask(u, slot, amt, k, source == null ? "?" : source, rc, units));
  return amt;
}}""", bxp))
bxp.addMethod(CtNewMethod.make(f"""
public static long offer(java.util.UUID u, int slot, long base, String source, String expect, {CRR} rc, int units, boolean grant) {{
  return offerX(u, slot, base, source, expect, rc, units, grant, true);
}}""", bxp))
''')
rep('''# 0.4.10: unchanged - the cap still counts the BASE heal XP (the healing); BridgeXp.offer -> BridgeXp.paid applies the xp multiplier and the
# class skill XP multiplier after it (a capped Priest earns divinity.healXpMaxPerMinute x 3 at the default x3)
''', '''# 0.4.11: heal XP is FINAL - BridgeXp.offerX(..., cls false) skips the class skill XP multiplier; the cap counts the heal XP before the
# general xp multiplier and the tree bonus (= what the Priest gets at the defaults: 1 / 1.25 per HP, at most 900 a minute)
''')
rep('''    try {{ r = {PKG}.BridgeXp.offer(u, {PKG}.SkillDefs.DIVINITY, base, source, expect, null, 0, false); }} catch (Throwable t) {{ r = -1L; }}''',
    '''    try {{ r = {PKG}.BridgeXp.offerX(u, {PKG}.SkillDefs.DIVINITY, base, source, expect, null, 0, false, false); }} catch (Throwable t) {{ r = -1L; }}''')
rep('''# HP was healed on the healer themself (divinity.healXpPerHpSelf, 0.25); absent / FALSE = on others (divinity.healXpPerHp, 0.2). One cap.''',
    '''# HP was healed on the healer themself (divinity.healXpPerHpSelf, 0.25; 0.4.11: 1.25 final); absent / FALSE = on others (divinity.healXpPerHp,
# 0.2; 0.4.11: 1 final). One cap (0.4.11: 900 final a minute).''')
rep('''# 0.4.10 point 2: THE class skill XP multiplier - every XP gain into a class skill goes through here (KillSys for kills and so the party
# share, BridgeXp.paid for heals and grants).''', '''# 0.4.10 point 2: THE class skill XP multiplier - every XP gain into a class skill goes through here (KillSys for kills and so the party
# share, BridgeXp.paid for grants; 0.4.11: NOT Priest heal XP - HealXp.offer -> BridgeXp.offerX(..., cls false)).''')

# ---------------------------------------------------------------------------------------------------------------- point 3: rows
rep('''     "Class skill XP from kills, party shares and Priest heals times this, on top of the XP multiplier.", "reload"),''',
    '''     "Kill and party-share class skill XP times this, on top of the XP multiplier. Not Priest heals.", "reload"),''')
rep('''    # 0.4.4 Divinity XP from Priest heals (skill:fn:healxp, SkyyClasses 0.1.6); kills pay Fury / Divinity through the rows above
    ("divinity.healXpPerHp", "Divinity XP per HP healed", "combat", "dec", "0.2", "0", "100", "", "", "live",
     "XP per 1 HP a Priest heals on OTHER party members (healing themself: the next row).", "reload"),
    # 0.4.6 (LOCKED Skyy 2026-09-25): self-heals pay their own rate, inside the same per-minute cap
    ("divinity.healXpPerHpSelf", "Divinity XP per HP healed on self", "combat", "dec", "0.25", "0", "100", "", "", "live",
     "XP per 1 HP a Priest heals on themself (locked default 0.25). Counts against the cap below too.", "reload"),
    ("divinity.healXpMaxPerMinute", "Divinity heal XP per minute", "combat", "int", "300", "0", "1000000000", "", "", "live",
     "Most heal XP per Priest in 60 s, before the XP multipliers (0 = no limit). Kills are not counted.", "reload"),''',
    '''    # 0.4.4 Divinity XP from Priest heals (skill:fn:healxp, SkyyClasses 0.1.6); kills pay Fury / Divinity through the rows above
    # 0.4.11 (LOCKED Skyy 2026-10-01): the three heal rows are the FINAL heal XP (not multiplied by the class skill XP multiplier)
    ("divinity.healXpPerHp", "Divinity XP per HP healed on others", "combat", "dec", HEAL_PER_HP_DEF, "0", "100", "", "", "live",
     "XP the Priest gets per 1 HP healed on other party members. Not multiplied by class skill XP.", "reload"),
    # 0.4.6 (LOCKED Skyy 2026-09-25): self-heals pay their own rate, inside the same per-minute cap
    ("divinity.healXpPerHpSelf", "Divinity XP per HP healed on self", "combat", "dec", HEAL_SELF_DEF, "0", "100", "", "", "live",
     "XP the Priest gets per 1 HP healed on themself. Not multiplied by class skill XP. Counts in the cap.", "reload"),
    ("divinity.healXpMaxPerMinute", "Divinity heal XP per minute", "combat", "int", HEAL_MAX_DEF, "0", "1000000000", "", "", "live",
     "Most heal XP a Priest gets in 60 s (0 = no limit). Not multiplied by class skill XP. No kill XP.", "reload"),''')
rep('''for _k in ("divinity.healXp.enabled", "divinity.healXpPerHp", "divinity.healXpMaxPerMinute"):
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _k in _dp, _k
''', '''for _k in ("divinity.healXp.enabled", "divinity.healXpPerHp", "divinity.healXpMaxPerMinute"):
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _k in _dp, _k
# 0.4.11: row default = file default = HealMig's new value for each heal key; the default file holds the marker once, above the Divinity block
for _k, _o, _n, _w in HEAL_MG:
    assert [_r[4] for _r in CFG_ROWS if _r[0] == _k] == [_n] and _dp.get(_k) == _n and _o != _n, _k
assert L.count(HEAL_MARK) == 1 and L[L.index(HEAL_MARK) + 1] == DIV_L[0] and HEAL_MARK not in DIV_L + DIVS_L + CLS_L
''')

# ---------------------------------------------------------------------------------------------------------------- manifest
rep('''Class skills earn 3x XP by default (Class skill XP multiplier in Server Setup: kills, party shares and Priest heals; gathering skills unchanged).''',
    '''Class skills earn 3x XP from kills by default (Class skill XP multiplier in Server Setup: kills and party shares; gathering skills unchanged). Priest heal XP is what the Priest gets: 1 per HP on others, 1.25 on yourself, up to 900 a minute (Server Setup).''')

# ---------------------------------------------------------------------------------------------------------------- point 5: HealMig
HMIG = r'''
# ---- HealMig (0.4.11 point 5): the one-time heal XP update of an existing xp.properties (Skyy 2026-10-01). setup() only, after ManaMig.run
# and BEFORE SkillCfg.load and CfgPub.start. The SkyyClasses 0.1.10 migrate0110 machinery method for method (reviewed + live): pure text
# step mgUpdate on the config kit's own parser (CfgFile.isComment / key / value / end / valStart), a Properties check (only the updated
# keys differ), CfgHist.snapshot + mgSaved (no rewrite unless config-history really holds the old bytes), CfgRows.atomicWrite, one
# config-changes.log line per changed key (Server Setup -> Changes -> Undo), one INFO line (+ one per kept value).
hmig = pool.makeClass(PKG + ".HealMig")
for _d in ("public static final String[] MG_KEY = %s;" % jarr([t[0] for t in HEAL_MG]),
           "public static final String[] MG_OLD = %s;" % jarr([t[1] for t in HEAL_MG]),
           "public static final String[] MG_NEW = %s;" % jarr([t[2] for t in HEAL_MG]),
           "public static final String[] MG_WHY = %s;" % jarr([t[3] for t in HEAL_MG]),
           "public static final String[] DOC_OLD = %s;" % jarr([t[0] for t in HEAL_DOC]),
           "public static final String[] DOC_NEW = %s;" % jarr([t[1] for t in HEAL_DOC]),
           "public static final String MG_MARK = %s;" % json.dumps(HEAL_MARK),
           "public static final String MG_MARK_ID = %s;" % json.dumps(HEAL_MARK_ID),
           'public static final String MG_WHO = "SkyySkills 0.4.11";',
           'public static final String ANCHOR = "divinity.healXp.enabled";'):
    hmig.addField(CtField.make(_d, hmig))
assert all('"' not in x and "\\" not in x for t in HEAL_MG + HEAL_DOC for x in t)
HMIG_JAVA = [r"""
public static int mgIdx(String k) {
  if (k == null) return -1;
  for (int i = 0; i < MG_KEY.length; i++) if (MG_KEY[i].equals(k)) return i;
  return -1;
}""", r"""
public static int docIdx(String body) {
  for (int i = 0; i < DOC_OLD.length; i++) if (DOC_OLD[i].equals(body)) return i;
  return -1;
}""",
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser). null = the marker is already in a comment line
# (nothing to do). Else { new text, "divinity.healXpPerHp 0.2 -> 1, ...", String[] kept notes, String[] { key, old, new }*, Integer docs }.
# A heal key whose LAST live line (the one Properties keeps) is a one-line entry holding exactly the old text is updated: every one-line
# entry of it holding the old text gets the new value (value text only: key, separator and CR stay). Anything else is kept: an admin's
# value (noted unless it already is the new default), a continued entry (noted), a missing line (silent). A comment line that is exactly
# a DOC_OLD line becomes its DOC_NEW line (CR kept). Marker: on its own line above the first divinity.healXp.enabled / heal key entry -
# above the whole run of comment lines directly on top of it - else above line 0. Lines are scanned from the start of a logical line, so a
# continued entry's tail is never taken for a comment. Never throws for any text.
r"""
public static Object[] mgUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int n = MG_KEY.length;
  String[] eff = new String[n];
  boolean[] multi = new boolean[n];
  int first = -1;
  int above = -1;
  int run = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MG_MARK_ID) >= 0) return null;
      if (s.trim().length() == 0) run = -1;
      else if (run < 0) run = k;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    String key = @PKG@.CfgFile.key(s);
    int m = mgIdx(key);
    if (first < 0 && (m >= 0 || ANCHOR.equals(key))) { first = k; above = run >= 0 ? run : k; }
    if (m >= 0) {
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
    if (!multi[i] && eff[i].equals(MG_OLD[i])) {
      mig[i] = true;
      if (chg.length() > 0) chg.append(", ");
      chg.append(MG_KEY[i]).append(' ').append(MG_OLD[i]).append(" -> ").append(MG_NEW[i]);
      rows.add(MG_KEY[i]);
      rows.add(MG_OLD[i]);
      rows.add(MG_NEW[i]);
    } else if (multi[i] || !eff[i].equals(MG_NEW[i])) {
      kept.add(MG_KEY[i] + "=" + @PKG@.CfgRows.oneLine(eff[i]) + " kept (an admin's value) - it now counts as " + MG_WHY[i] + " (0.4.10 multiplied it by the class skill XP multiplier); the 0.4.11 default is " + MG_NEW[i]);
    }
  }
  java.util.ArrayList out = new java.util.ArrayList();
  int docs = 0;
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) {
      int d = docIdx(s2);
      if (d >= 0) {
        out.add(DOC_NEW[d] + (raw[k].endsWith("\r") ? "\r" : ""));
        docs++;
      } else out.add(raw[k]);
      k++;
      continue;
    }
    int e2 = @PKG@.CfgFile.end(l, k);
    int m2 = mgIdx(@PKG@.CfgFile.key(s2));
    if (m2 >= 0 && mig[m2] && e2 == k && @PKG@.CfgFile.value(l, k).trim().equals(MG_OLD[m2])) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + MG_NEW[m2] + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  int at = first >= 0 ? above : 0;
  String crA = at + 1 < raw.length ? (raw[at].endsWith("\r") ? "\r" : "") : cr;
  out.add(at, MG_MARK + crA);
  StringBuilder sb = new StringBuilder(text.length() + MG_MARK.length() + 256);
  for (int i = 0; i < out.size(); i++) {
    if (i > 0) sb.append('\n');
    sb.append((String) out.get(i));
  }
  return new Object[] { sb.toString(), chg.toString(), (String[]) kept.toArray(new String[0]), (String[]) rows.toArray(new String[0]), Integer.valueOf(docs) };
}""",
# the update may change nothing but the updated keys' values: both texts as java.util.Properties - same keys, same values, the updated keys
# exactly their new value (a marker / comment line can never change a value; this guards the parser corner cases)
r"""
public static boolean sameAfter(byte[] old, byte[] nb, String[] rows) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties b = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    b.load(new java.io.ByteArrayInputStream(nb));
    if (a.size() != b.size()) return false;
    java.util.Iterator it = a.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      String want = a.getProperty(k);
      for (int i = 0; i + 2 < rows.length; i += 3) if (rows[i].equals(k)) want = rows[i + 2];
      String got = b.getProperty(k);
      if (got == null || !got.equals(want)) return false;
    }
    return true;
  } catch (Throwable t) { return false; }
}""",
r"""
public static int fileIdx() {
  for (int k = 0; k < @PKG@.CfgRows.FILES.length; k++) if (@PKG@.CfgRows.FILES[k].endsWith("/xp.properties")) return k;
  return -1;
}""",
# the config kit's own files for the update, before CfgPub.start (which sets the same values again): history + change log live in the
# folder of xp.properties (the kit's HOME, Skyy_SkyySkills)
r"""
public static void mgKit(java.nio.file.Path home) {
  @PKG@.CfgRows.HOME = home;
  if (@PKG@.CfgRows.LOG == null) @PKG@.CfgRows.LOG = @PKG@.SkillCfg.LOG;
  @PKG@.CfgHist.init();
  @PKG@.CfgLog.init();
}""",
# CfgHist.snapshot swallows its own errors, so after it the update checks that config-history really holds a copy with exactly these
# bytes (the new copy, or the newest one when snapshot skipped an equal file) - the copies themselves, not index.log
r"""
public static boolean mgSaved(int f, byte[] old) {
  String[] have = @PKG@.CfgHist.list(f);
  for (int i = have.length - 1; i >= 0; i--) {
    try {
      if (java.util.Arrays.equals(java.nio.file.Files.readAllBytes(@PKG@.CfgHist.bak(f, have[i])), old)) return true;
    } catch (Throwable x) { }
  }
  return false;
}""",
# one config-changes.log line in the kit's scalar-row format (CfgLog.add without its per-line INFO; the key column = the row key, so
# Server Setup -> Changes undoes it with a plain set back to the old value)
r"""
public static String mgLog(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + MG_WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}""",
# setup(): the file before this update becomes a History version (KEEP 10, verified by mgSaved before the rewrite), the new text is
# written with the kit's atomicWrite (ISO-8859-1 bytes), one change-log line per updated key, one INFO line (+ one per kept value).
# Returns the INFO line(s) joined by \n ("" = nothing done: no file - load() writes the 0.4.11 default with the marker -, marker already
# there, or a failure - WARN, file untouched, retried at the next start)
r"""
public static synchronized String run() {
  java.nio.file.Path f = @PKG@.SkillCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = mgUpdate(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    String[] rows = (String[]) r[3];
    if (!sameAfter(old, data, rows)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for the 0.4.11 heal XP: the update would change more than the heal XP lines (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = fileIdx();
    if (fi < 0) return "";
    mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), MG_WHO, "before the 0.4.11 heal XP update");
    if (!mgSaved(fi, old)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for the 0.4.11 heal XP: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(mgLog(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    int docs = ((Integer) r[4]).intValue();
    String dt = docs > 0 ? "; " + docs + " outdated default comment line(s) updated" : "";
    String msg = null;
    if (chg.length() > 0) msg = "xp.properties updated for the 0.4.11 heal XP (Priest heal XP is what the Priest gets - no class skill XP multiplier): " + chg + dt + " (the old file is in config-history; Server Setup -> Changes can undo each line)";
    else msg = "xp.properties: no divinity heal XP line still had its 0.4.10 default - no value changed" + dt + " (0.4.11 heal XP marker added; the old file is in config-history)";
    @PKG@.SkillCfg.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { @PKG@.SkillCfg.info(kept[i]); all.append('\n').append(kept[i]); }
    return all.toString();
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("could not update xp.properties for the 0.4.11 heal XP (the file is used as it is): " + t);
    return "";
  }
}"""]
for _src in HMIG_JAVA:
    hmig.addMethod(CtNewMethod.make(_src.replace("@PKG@", PKG), hmig))

'''
rep('''# ---- ManaGuard (point 3): WARN once per class whose base Mana''', HMIG.lstrip("\n") + '''# ---- ManaGuard (point 3): WARN once per class whose base Mana''')
rep('''          mcost, mmig, mgd):
    c.writeFile(OUT)
''', '''          mcost, mmig, mgd, hmig):   # 0.4.11: + HealMig
    c.writeFile(OUT)
''')
rep('''  {PKG}.ManaMig.run();   // 0.4.8: mana.magicBase / mana.magicClasses -> Base Mana by class, once, before the file is read and the kit starts
''', '''  {PKG}.ManaMig.run();   // 0.4.8: mana.magicBase / mana.magicClasses -> Base Mana by class, once, before the file is read and the kit starts
  {PKG}.HealMig.run();   // 0.4.11: untouched heal XP lines 0.2 / 0.25 / 300 -> 1 / 1.25 / 900 (final heal XP), once; History first
''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
for k in KEEP:
    assert s.count(k) == 1, "a block that must stay byte-identical changed: " + k[:100]
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "systems / commands changed"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
# the class skill XP multiplier keeps its two call sites (KillSys, BridgeXp.paidX - now behind cls); heal XP is the only cls-false caller
assert s.count("{PKG}.SkillCfg.classXp(") == 2 and s.count("if (canBoost && cls) amt = {PKG}.SkillCfg.classXp(slot, amt);") == 1
assert s.count("{PKG}.BridgeXp.offerX(") == 1 and s.count("offerX(u, slot, base, source, expect, rc, units, grant, true)") == 1
assert "BridgeXp.offer(u, {PKG}.SkillDefs.DIVINITY" not in s
assert s.index("public static long paidX(") < s.index("public static long paid(java.util.UUID u") < s.index("public static long offerX(") \
    < s.index("public static long offer(java.util.UUID u, int slot, long base, String source, String expect, {CRR} rc, int units, boolean grant)")
assert s.index("public static long offerX(") < s.index("public static boolean offer(java.util.UUID u, double hp"), "offerX before HealXp.offer"
assert s.index('hmig = pool.makeClass(PKG + ".HealMig")') > s.index("kit = CFG.emit(") and \
    s.index('hmig = pool.makeClass(PKG + ".HealMig")') < s.index("public void setup() {{"), "HealMig after the kit, before setup"
assert s.index("{PKG}.ManaMig.run();") < s.index("{PKG}.HealMig.run();") < s.index("String rules = {PKG}.SkillCfg.load();")
assert "0.2" not in block("# 0.4.11 (LOCKED Skyy 2026-10-01): the three heal rows", "    # ---- acrobatics (+ Double Jump)")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars")
