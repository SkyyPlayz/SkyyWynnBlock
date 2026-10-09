"""Derive SkyySkills/build_skyyskills_0.4.28.py from the LIVE generated SkyySkills/build_skyyskills_0.4.27.py (= the tools/deploy_set.py SET
pin; 0.4.27 came from 0.4.26 by tools/skills_0_4_27_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_27_patch.py: rep(old, new) with asserted single anchors, newline-agnostic; 0.4.27
stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_28_patch.py   then   python SkyySkills/build_skyyskills_0.4.28.py   (NO --deploy: coordinated deploy)
Test: python SkyyClasses/test_skyyclasses_0.1.16.py (its SK section loads this jar next to SkyyClasses 0.1.16; bare JVM, -Xverify:all)

0.4.28 = ABILITY DAMAGE COUNTS AS CLASS DAMAGE (research/cloud/Ability-Engine-Plan.md "For the local session" 3: "How SkyySkills credits
class XP for a kill made by ability damage while the caster holds a non-class item ... a Meteor kill may pay the wrong skill or none.
Decide in R1"; SkyyClasses 0.1.16 = the ability engine, round R1). Skyy's lock behind it: the weapon is checked when the ability is CAST
(an ability keeps working after a weapon swap - the plan's accepted default 4).
  - SkillClass.abilCaster(Object damage) = SkyyClasses 0.1.16's bridge class:fn:abilhit (the Damage objects its ability engine created ->
    the casting player; missing bridge / not ability damage = null). VERIFIED in HytaleServer.jar: DamageSystems$ApplyDamage hands the
    SAME Damage object to DeathComponent.tryAddComponent, so KillSys' getDeathInfo() is the object SkyyClasses tagged.
  - SkillClass.weaponOrAbil(u, slot, f, acc, att, damage): ability damage cast by this player = a class weapon (the cast already checked
    the class weapon in hand); anything else = weaponOk exactly as before.
  - KILL XP: KillSys calls the new killSlot(pr, acc, att, damage) (the old 3-argument killSlot = the same with no damage) - the only
    change is weaponOk -> weaponOrAbil, so a Meteor kill pays Sorcery even if the Mage already swapped to food. Mob level / party share
    / class XP multiplier unchanged (they follow the slot).
  - THE CLASS DAMAGE PERK (CombatDmgSys: the skill-level damage perk + the class balance damage %) applies to ability damage the same way.
  - Mana on hit (ManaHit, fighters + Archers) is NOT changed: no fighter ability exists yet (decide with their round).
  No config key, no saved data, no migration, no new class / system / command. Without SkyyClasses 0.1.16 (no class:fn:abilhit) every
  path is 0.4.27's. Rolling back to 0.4.27 is safe (ability kills after a weapon swap then pay no XP).
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.27.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.28.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.27"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.27"' in s and "derived from the generated 0.4.26 by tools/skills_0_4_27_patch.py" in s, "not the live generated 0.4.27"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "class:fn:abilhit" not in s, "0.4.27 already reads class:fn:abilhit"
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


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyySkills 0.4.27 - build script (derived from the generated 0.4.26 by tools/skills_0_4_27_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.28 - build script (derived from the generated 0.4.27 by tools/skills_0_4_28_patch.py - edit the patch, not this file;
0.4.27 was derived from the generated 0.4.26 by tools/skills_0_4_27_patch.py; ''')
rep('''0.4.27: THE MONK SKILL IS "ZEN" (Skyy LOCKED 2026-10-08; full notes in tools/skills_0_4_27_patch.py). Display text only: slot 8's label
''', '''0.4.28: ABILITY DAMAGE COUNTS AS CLASS DAMAGE (SkyyClasses 0.1.16 ability engine R1; full notes in tools/skills_0_4_28_patch.py). Damage
  that SkyyClasses' class:fn:abilhit names as cast by the attacker passes the class weapon test (the weapon was checked at the cast):
  KillSys (kill XP of a Meteor kill after a weapon swap) and CombatDmgSys (the class damage perk). Without SkyyClasses 0.1.16 nothing
  changes. No config key, saved data, migration, class, system or command. CHECKED: SkyyClasses/test_skyyclasses_0.1.16.py section SK.
0.4.27: THE MONK SKILL IS "ZEN" (Skyy LOCKED 2026-10-08; full notes in tools/skills_0_4_27_patch.py). Display text only: slot 8's label
''')
rep('VERSION = "0.4.27"', 'VERSION = "0.4.28"')

# ---------------------------------------------------------------------------------------------------------------- the ability test
rep('''# storage slot that earns this kill's combat XP, or -1 (and the reason is told once): SkyyClasses present, a class, a known class,
# a class weapon
scls.addMethod(CtNewMethod.make(f"""
public static int killSlot({PR} pr, {CAC} acc, {REF} att) {{
  java.util.UUID u = pr.getUuid();''', '''# 0.4.28: the player who CAST the ability that made this Damage (SkyyClasses 0.1.16+ bridge class:fn:abilhit; null = not ability damage,
# or no SkyyClasses 0.1.16). Never throws.
scls.addMethod(CtNewMethod.make(f"""
public static java.util.UUID abilCaster(Object d) {{
  if (d == null) return null;
  try {{
    Object f = {PKG}.SkillStore.bridge().get("class:fn:abilhit");
    if (!(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply(d);
    return r instanceof java.util.UUID ? (java.util.UUID) r : null;
  }} catch (Throwable t) {{ return null; }}
}}""", scls))
# 0.4.28: ability damage cast by THIS player counts as a class weapon hit (SkyyClasses checked the class weapon when it was cast; the
# player may hold something else when it lands); everything else = weaponOk, unchanged
scls.addMethod(CtNewMethod.make(f"""
public static boolean weaponOrAbil(java.util.UUID u, int slot, java.util.function.Function f, {CAC} acc, {REF} att, Object d) {{
  java.util.UUID c = abilCaster(d);
  if (c != null && u != null && c.equals(u)) return {PKG}.SkillDefs.isClass(slot);
  return weaponOk(u, slot, f, acc, att);
}}""", scls))
# storage slot that earns this kill's combat XP, or -1 (and the reason is told once): SkyyClasses present, a class, a known class,
# a class weapon (0.4.28: or the class's own ability - d = the killing Damage)
scls.addMethod(CtNewMethod.make(f"""
public static int killSlot({PR} pr, {CAC} acc, {REF} att, Object d) {{
  java.util.UUID u = pr.getUuid();''')
rep('''  if (!weaponOk(u, s, f, acc, att)) {{
    String w = weaponsText({PKG}.SkillDefs.CLASSES[{PKG}.SkillDefs.classIdx(s)]);''', '''  if (!weaponOrAbil(u, s, f, acc, att, d)) {{
    String w = weaponsText({PKG}.SkillDefs.CLASSES[{PKG}.SkillDefs.classIdx(s)]);''')
rep('''    tellOnce(pr, 8, "Only kills with your " + c + " weapons" + (w == null ? "" : " (" + w + ")") + " earn " + skillName(u, s) + " XP.");
    return -1;
  }}
  return s;
}}""", scls))''', '''    tellOnce(pr, 8, "Only kills with your " + c + " weapons" + (w == null ? "" : " (" + w + ")") + " earn " + skillName(u, s) + " XP.");
    return -1;
  }}
  return s;
}}""", scls))
scls.addMethod(CtNewMethod.make(f"""
public static int killSlot({PR} pr, {CAC} acc, {REF} att) {{
  return killSlot(pr, acc, att, null);
}}""", scls))''')
rep('''    int slot = {PKG}.SkillClass.killSlot(pr, b, k);''', '''    int slot = {PKG}.SkillClass.killSlot(pr, b, k, d);   // 0.4.28: + the Damage (an ability kill passes the weapon test)''')
rep('''    if (!{PKG}.SkillClass.weaponOk(u, slot, f, buf, att)) return;
    float a = d.getAmount();''', '''    if (!{PKG}.SkillClass.weaponOrAbil(u, slot, f, buf, att, d)) return;   // 0.4.28: ability damage = the class's own power
    float a = d.getAmount();''')
rep('''kills with class weapons (nearby SkyyParty members get a share in their own class skill)''',
    '''kills with class weapons or class abilities (nearby SkyyParty members get a share in their own class skill)''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "0.4.28 adds no system and no command"
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed]
assert not _bad, "0.4.27 lines changed outside the planned places: %r" % _bad[:5]
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.27,", len(_gone), "0.4.27 lines replaced,",
      sum(op[4] - op[3] for op in _hunks) - len(_gone), "lines added net;", len(OLDS), "anchors")
