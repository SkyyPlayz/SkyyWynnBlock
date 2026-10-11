"""Derive SkyyMenu/build_skyymenu_0.3.13.py from the LIVE SkyyMenu 0.3.12 (python tools/menu_0_3_13_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_12_patch.py -> 0.3.12 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch, never re-build it) -> this patch -> 0.3.13. 0.3.12's files stay untouched. The harness
SkyyMenu/test_skyymenu_0.3.13.py is its own file (it runs test_skyymenu_0.3.12.py on the new jar next to a control run = every old check
carried forward, plus the new sections).

0.3.13 = THE MONK SKILL IS "ZEN" + THE CLASS BALANCE DAMAGE ON THE STATS PAGE. Skyy's own words: "Show skill Defense and the class-balance
damage % on the Stats page (a small SkyyMenu build)? -> Yes, next (Recommended)" (0.3.12 did the Defense half) and the Monk skill name
LOCKED 2026-10-08 (docs/answered/classes.md popup batch 1: 'MONK skill name "Zen" (rename from Discipline ...)').
  1. ZEN: CLASS_SKILLS' Monk entry Discipline -> Zen (the class texts of the Mods list: the SkyySkills entry; the main menu Skills tile).
     The Java CLASS_SKILLS (StatsCalc.isClassSkill - which skill:<uuid> entries are class skills on the Skills tab) = the 7 names + the
     OLD label "Discipline", so a SkyySkills 0.4.26 next to this menu still files its Monk row under the class skills (internal match
     only - the label shown is whatever SkyySkills publishes).
  2. CLASS WEAPON DAMAGE: SkyySkills 0.4.26 publishes skill:dmg:<uuid> = the class balance damage % (a Double PERCENT, the skill:def rules:
     rounded to 0.01, removed at 0 and when the player leaves). StatsCalc.skillDmg(u) reads it exactly like skillDef: a Double > 0 (NaN /
     infinite / <= 0 / missing / any other type = 0; above 100000 = 100000). StatsCalc.classDamage: 0 -> EXACTLY 0.3.12's row; else total
     = level part (level x perk.combat.damagePerLevel x 100, 0 with perk.enabled off) + the class balance %, breakdown
     "<skill> level N +L%, Class balance +X%" (SkyySkills' CombatDmgSys adds both into one multiplier - Perks.damage + boostDmg).
  3. ROUND_PINS = this round (SkyySkills 0.4.26 -> 0.4.27, SkyyClasses 0.1.14 -> 0.1.15, SkyyTrees 0.3.4 -> 0.3.5, SkyyProfiles 0.1.7 ->
     0.1.8); MODS_VERSIONS names those four versions (NOT a version catch-up: every other entry stays 0.3.12's).
  4. No saved data, no setting, no layout change (same rows, same page).
Every change below is recorded (CHANGES) and undone at the end to prove the generated script is 0.3.12 outside them, byte for byte.
"""
import os
import re
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.12.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.13.py")
tsrc = os.path.join(ROOT, "SkyyMenu", "test_skyymenu_0.3.12.py")
tdst = os.path.join(ROOT, "SkyyMenu", "test_skyymenu_0.3.13.py")
CR, LF = chr(13), chr(10)


def load(p):
    raw = open(p, encoding="utf8", newline="").read()
    return raw.replace(CR + LF, LF), (CR + LF if (CR + LF) in raw else LF)


s, NL = load(src)
OLD = s
assert 'VERSION = "0.3.12"' in s and "0.3.12: THE STATS PAGE DEFENSE ROW" in s and "skill:dmg:" not in s, "not the generated 0.3.12 script"
CHANGES = []            # (new text, old text) of every change, in order: undone at the end


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


# THIS ROUND: the mods that deploy together with this SkyyMenu (mod: (the SET version now, the round's version))
ROUND = {"SkyySkills": ("0.4.26", "0.4.27"), "SkyyClasses": ("0.1.14", "0.1.15"), "SkyyTrees": ("0.3.4", "0.3.5"),
         "SkyyProfiles": ("0.1.7", "0.1.8")}
_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyMenu") != "0.3.12":
    print("NOTE: tools/deploy_set.py SET pins SkyyMenu %s, this patch derives from 0.3.12" % _set.get("SkyyMenu"))
for _m, (_frm, _to) in ROUND.items():
    if _set is not None and _set.get(_m) != _frm:
        print("NOTE: tools/deploy_set.py SET pins %s %s, this round replaces %s" % (_m, _set.get(_m), _frm))

# the key + its meaning come from SkyySkills 0.4.26 (the SET pin): fail the patch if that script stops publishing it this way
_sk = open(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.26.py"), encoding="utf8").read()
assert 'String k = "skill:dmg:" + u.toString();' in _sk and _sk.count("Double dv = Double.valueOf(x);") == 2 \
    and _sk.count("(v > 100000.0 ? 100000.0 : v)") == 2 and "{PKG}.SkillDef.setDmg(u, {PKG}.ClassPower.dmgPct(u, {PKG}.SkillStore.data(u)));" in _sk, \
    "SkyySkills 0.4.26 no longer publishes skill:dmg:<uuid> as a Double percent (0..100000)"
assert "double bonus = {PKG}.Perks.damage(clv) + {PKG}.ClassPower.boostDmg(slot, clv);" in _sk, "SkyySkills adds the class balance % differently now"
# the Zen names come from this round's SkyySkills / SkyyClasses scripts
_sk27 = open(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.27.py"), encoding="utf8").read()
_cl15 = open(os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.15.py"), encoding="utf8").read()
assert '("Monk", "Zen", "Weapon_Staff_Bo_Wood", "#f08a30")' in _sk27 and '{"name": "Monk", "skill": "Zen",' in _cl15, "the round's Zen names"

# ================================================================================================ docstring + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.12: THE STATS PAGE DEFENSE ROW''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.13: THE MONK SKILL IS ZEN + CLASS BALANCE DAMAGE ON THE STATS PAGE (notes: tools/menu_0_3_13_patch.py; Skyy LOCKED 2026-10-08 Monk
       skill "Zen"; "Show skill Defense and the class-balance damage % on the Stats page ... -> Yes, next (Recommended)"): CLASS_SKILLS
       Monk = Zen (Mods texts, Skills tile); Stats page Class Weapon Damage = level part + SkyySkills 0.4.26's skill:dmg:<uuid> (a
       Double percent), breakdown "Class balance +X%"; without it (older / no SkyySkills, any other type) the row is exactly 0.3.12's.
       ROUND_PINS = SkyySkills 0.4.27, SkyyClasses 0.1.15, SkyyTrees 0.3.5, SkyyProfiles 0.1.8 (deploy together). No saved data.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.13.py (every 0.3.12 check carried forward + K7 0.3.12 -> 0.3.13 + ZN the Zen texts + DM the
  Class Weapon Damage row).
0.3.12: THE STATS PAGE DEFENSE ROW''')
rep('VERSION = "0.3.12"\n', 'VERSION = "0.3.13"\n')

# ================================================================================================ MODS_VERSIONS: the round's four versions
for _m, (_frm, _to) in sorted(ROUND.items()):
    _old = re.findall(r'"%s": "([0-9.]+)"' % _m, s[s.index("MODS_VERSIONS = {"):s.index("MODS = [")])
    assert len(_old) == 1, (_m, _old)
    rep('"%s": "%s",' % (_m, _old[0]), '"%s": "%s",' % (_m, _to))

# ================================================================================================ the class roster + texts (Zen)
rep('''CLASS_SKILLS   = ["Archery", "Swordsmanship", "Sorcery", "Fury", "Divinity", "Assassination", "Discipline"]      # the weapon skill of each CLASS_PLAYABLE class
''', '''# 0.3.13: the Monk's skill is Zen (Skyy LOCKED 2026-10-08; SkyyClasses 0.1.15, SkyySkills 0.4.27)
CLASS_SKILLS   = ["Archery", "Swordsmanship", "Sorcery", "Fury", "Divinity", "Assassination", "Zen"]      # the weapon skill of each CLASS_PLAYABLE class
# 0.3.13: OLD class skill labels a SkyySkills before 0.4.27 still publishes in skill:<uuid> (StatsCalc.isClassSkill only - never shown by us)
CLASS_SKILLS_OLD = ["Discipline"]
''')
rep('''         "or Discipline) and more. "''', '''         "or Zen) and more. "''')
rep('''Sorcery, Fury, Divinity, Assassination or Discipline, on its own XP curve) - level up and pay coins.''',
    '''Sorcery, Fury, Divinity, Assassination or Zen, on its own XP curve) - level up and pay coins.''')
rep('''assert "Assassination or Discipline" in _bym["SkyySkills"]["desc"] and len(_bym["SkyySkills"]["desc"]) <= 390, "0.3.9: the Skills text"
''', '''assert "Assassination or Zen" in _bym["SkyySkills"]["desc"] and len(_bym["SkyySkills"]["desc"]) <= 390, "0.3.9: the Skills text (0.3.13: Zen)"
assert "Discipline" not in " ".join(m["desc"] for m in MODS) + " ".join(" ".join(e[4]) for e in ENTRIES), "0.3.13: no Mods / menu text names Discipline"
''')
rep('''           "Swordsmanship 100, Assassination 100, Discipline 100, Sorcery 100"):''',
    '''           "Swordsmanship 100, Assassination 100, Zen 100, Sorcery 100",
           "Swordsmanship level 100 +20%, Class balance +12.5%"):   # 0.3.13: the Class Weapon Damage row with skill:dmg''')
rep('''F(scl, "public static final String[] CLASS_SKILLS = %s;" % jarr(CLASS_SKILLS))
''', '''F(scl, "public static final String[] CLASS_SKILLS = %s;" % jarr(CLASS_SKILLS + CLASS_SKILLS_OLD))   # 0.3.13: + the old Monk label
''')

# ================================================================================================ ROUND_PINS + the patch name
rep('''# 0.3.12: EMPTY - reads SkyySkills 0.4.25's skill:def:<uuid> (already the SET pin); without it the Defense row is 0.3.11's.
ROUND_PINS = {}
''', '''# 0.3.12: EMPTY - reads SkyySkills 0.4.25's skill:def:<uuid> (already the SET pin); without it the Defense row is 0.3.11's.
# 0.3.13: deploys WITH SkyySkills 0.4.27 + SkyyClasses 0.1.15 + SkyyTrees 0.3.5 + SkyyProfiles 0.1.8 (the Monk skill Zen;
# tools/menu_0_3_13_patch.py ROUND). If one of them does not ship, set its MODS_VERSIONS entry back and drop it here.
ROUND_PINS = %s
''' % repr(dict((m, ROUND[m]) for m in sorted(ROUND))))
rep('_PATCH = "tools/menu_0_3_10_patch.py"', '_PATCH = "tools/menu_0_3_13_patch.py"')

# ================================================================================================ StatsCalc: skillDmg + classDamage
rep('''M(scl, r"""
public static void classDamage(java.util.ArrayList rows, java.util.UUID u, java.util.HashMap sk) {
  if (classSyncing(u)) { add(rows, "Class Weapon Damage", "-", "class syncing, Refresh in a moment"); return; }
  String cs = classSkill(u);
  if (cs == null) { add(rows, "Class Weapon Damage", "-", "no class on this profile yet"); return; }
  double lvl = get(sk, cs);
  double rate = cfgOn("SkyySkills", "perk.enabled", true) ? cfgNum("SkyySkills", "perk.combat.damagePerLevel", 0.002) : 0.0;
  add(rows, "Class Weapon Damage", signed(lvl * rate * 100.0) + "%", cs + " level " + (int) lvl + ", with your class weapons");
}""")
''', '''# 0.3.13: the class balance damage % SkyySkills 0.4.26 publishes (skill:dmg:<uuid> = Double PERCENT, the skill:def rules). Only a Double > 0
# counts (NaN / infinite / any other type / missing = 0; the SkyySkills clamp 100000 kept); below 0.05 (the part() floor) = the row is exactly 0.3.12's.
M(scl, r"""
public static double skillDmg(java.util.UUID u) {
  try {
    Object o = u == null ? null : br().get("skill:dmg:" + u.toString());
    if (!(o instanceof Double)) return 0.0;
    double v = ((Double) o).doubleValue();
    if (Double.isNaN(v) || Double.isInfinite(v) || !(v > 0.0)) return 0.0;
    return v > 100000.0 ? 100000.0 : v;
  } catch (Throwable t) { return 0.0; }
}""")
M(scl, r"""
public static void classDamage(java.util.ArrayList rows, java.util.UUID u, java.util.HashMap sk) {
  if (classSyncing(u)) { add(rows, "Class Weapon Damage", "-", "class syncing, Refresh in a moment"); return; }
  String cs = classSkill(u);
  if (cs == null) { add(rows, "Class Weapon Damage", "-", "no class on this profile yet"); return; }
  double lvl = get(sk, cs);
  double rate = cfgOn("SkyySkills", "perk.enabled", true) ? cfgNum("SkyySkills", "perk.combat.damagePerLevel", 0.002) : 0.0;
  double cb = skillDmg(u);
  if (!(cb >= 0.05)) {
    add(rows, "Class Weapon Damage", signed(lvl * rate * 100.0) + "%", cs + " level " + (int) lvl + ", with your class weapons");
    return;
  }
  double lp = lvl * rate * 100.0;
  StringBuilder sb = new StringBuilder();
  sb.append(cs).append(" level ").append((int) lvl);
  if (Math.abs(lp) >= 0.05) sb.append(' ').append(signed(lp)).append('%');
  part(sb, "Class balance", cb, "%");
  add(rows, "Class Weapon Damage", signed(lp + cb) + "%", sb.toString());
}""")
''')

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
_mv = s[s.index("MODS_VERSIONS = {"):s.index("MODS = [")]
assert all(_mv.count('"%s": "%s",' % (m, to)) == 1 for m, (frm, to) in ROUND.items()), "the round's versions in MODS_VERSIONS"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.12 outside the recorded changes"
assert s.index("public static void part(") < s.index("public static double skillDmg(") < s.index("public static void classDamage(") \
    < s.index("classDamage(rows, u, kv("), "methods before callers"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.12 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
