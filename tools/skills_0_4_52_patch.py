"""Derive SkyySkills/build_skyyskills_0.4.52.py from the GENERATED SkyySkills 0.4.51 (build_skyyskills_0.4.51.py = the tools/deploy_set.py SET
pin; 0.4.51 came from 0.4.50 by tools/skills_0_4_51_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with
0.4.51 (nothing else changed); 0.4.51 stays untouched, its line endings are kept (tools/soundpass_gen.Patch).
Run:  python tools/skills_0_4_52_patch.py   then   python SkyySkills/build_skyyskills_0.4.52.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.52.py
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

# (class, old, new) in CLASS_MANA_DEF / OverallCfg.TCLASSES order; regen keys (key, old, new)
PER = [("Archer", 2, 1), ("Warrior", 2, 1), ("Assassin", 2, 1), ("Monk", 2, 1), ("Mage", 10, 9.5), ("Berserker", 2, 1), ("Priest", 5, 4.5),
       ("Spellblade", 4, 3)]
REGEN = [("mana.regen.inCombat", "75", "65"), ("mana.regen.perLevel", "7", "5"), ("mana.onHitCooldownMs", "500", "750")]
MN_KEYS = [("mana.classPerLevel." + _c, str(_o), str(_n)) for _c, _o, _n in PER] + REGEN
assert len(MN_KEYS) == 11 and len(set(_k for _k, _o, _n in MN_KEYS)) == 11

NOTE = '''0.4.52 (2026-10-18) = LESS MANA (Skyy 2026-10-18 docs/answered/skills.md: "(and i think we need to scale down how much mana you get as you
  level, and mana regen a little. cause ive never ran out of mana on any class i tested."). The model + per-class table: research/Mana-Budget-
  2026-10-18.md (sustained 30 s fight in combat, both equipped abilities on cooldown, casters + a charged shot every 3 s / 2 s).
  1. MAX MANA PER CLASS LEVEL (mana.classPerLevel, class order kept): Archer 2 -> 1, Warrior 2 -> 1, Assassin 2 -> 1, Monk 2 -> 1, Mage 10 -> 9.5,
     Berserker 2 -> 1, Priest 5 -> 4.5, Spellblade 4 -> 3. Mage 9.5 / Priest 4.5 are the lowest values that keep SkyyArmory 0.1.34's Mana check
     quiet (a Mithril staff 170 = 39.9 % of a Sorcery-40 pool, a Mithril wand 85 = 38.2 % of a Divinity-40 pool; check.share 40) - lower needs
     that check moved first (follow-up). Skyy's 2026-10-03 "+5 max Mana per Divinity level" lock is superseded by this 2026-10-18 request.
  2. MANA REGEN, a little: in-combat refill mana.regen.inCombat 75 -> 65 %; regen growth per class level mana.regen.perLevel 7 -> 5 % (above
     mana.regen.fromLevel 20, unchanged); Mana on hit (fighters' refill) mana.onHitCooldownMs 500 -> 750 ms (2 -> 1.33 a second at most).
     Vanilla's 3.33 a second out of combat (Skyy's M11 lock) and the class balance regen table are unchanged.
     Per class, in combat, before -> after (no gear / tree / accessory boosts): Lv 10 2.5 -> 2.2, Lv 25 3.4 -> 2.7-2.8, Lv 40 6.0-6.2 -> 4.4-4.5,
     Lv 55 8.7-8.8 -> 6.0-6.1 Mana a second (+ fighters' on-hit 2 -> 1.33).
     Max Mana (class skill only, Overall = half the class level), Lv 10 / 25 / 40 / 55, before -> after:
       Archer    46 / 80 / 114 / 148 -> 36 / 55 / 74 / 93        Mage       146 / 298 / 450 / 602 -> 141 / 286 / 430 / 575
       Warrior   43 / 77 / 110 / 144 -> 33 / 52 / 70 / 89        Berserker   34 /  68 / 101 / 135 ->  24 /  43 /  61 /  80
       Assassin  46 / 79 / 113 / 146 -> 36 / 54 / 73 / 91        Priest      93 / 170 / 247 / 324 ->  88 / 158 / 227 / 297
       Monk      43 / 76 / 110 / 143 -> 33 / 51 / 70 / 88        Spellblade  75 / 137 / 200 / 263 ->  65 / 112 / 160 / 208
     One rotation (the dearest A1 + A2 pair of every shape, at its unlock level) still fits every class's pool.
     Time to empty (in combat the whole time, both equipped abilities cast on cooldown), before -> after: fighters + Spellblade never (their
     abilities cost 0.3 - 2 Mana a second, below any regen); Mage / Priest + a charged shot every 3 / 2 s with the level's band weapon
     15 / 14 s at Lv 10 and 4 - 9 s from Lv 25 (the weapon ladder decides - unchanged); with the Wood starter weapon Mage 42 -> 30 s (Lv 10),
     never -> 90 s (Lv 25), Priest 28 -> 24 s, 120 -> 72 s. Follow-ups outside SkyySkills: research/Mana-Budget-2026-10-18.md section 4.
  3. MIGRATION Mn52Mig (PROJECT-RULES 4; a clone of Fl50Mig / Pd44Mig's reviewed machinery): ONCE on an EXISTING xp.properties (setup, right
     after Fl50Mig, before SkillCfg.load): each of the 11 keys (the 8 mana.classPerLevel.<Class> entries + the 3 regen keys) whose LAST entry
     is a one-line entry holding exactly the old default -> the new default (value text only); an admin's own value kept (INFO); no line =
     nothing (a missing table entry stays missing; the plain keys then use the new code defaults); the marker at the end; config-history copy
     first; one config-changes.log line per change (Undo in Server Setup -> Changes); bytes + line endings kept. A fresh file carries the
     marker (never migrated). PerkMig's 0.4.25 rewrite of an untouched mana.regen.inCombat=50 now lands on 65 (today's default).
  Server Setup rows unchanged (same keys / categories / bounds; only their defaults + help numbers). No saved player data, no new command,
  system or bridge. CHECKED: SkyySkills/test_skyyskills_0.4.52.py.
  ROLLBACK to 0.4.51: safe (no saved data). The migrated lines keep the new numbers (0.4.51 reads them as admin values) - Undo them in
  Server Setup -> Changes first if the old numbers are wanted back.
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.51.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.52.py"))
assert P.has('VERSION = "0.4.51"') and P.has("Fl50Mig") and P.has("MOVEMENT 2") and not P.has("Mn52Mig"), "not the generated SkyySkills 0.4.51 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

# ================================================================================================ docstring + version
P.rep('''"""SkyySkills 0.4.51 - build script (derived from the generated 0.4.50 by tools/skills_0_4_51_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.52 - build script (derived from the generated 0.4.51 by tools/skills_0_4_52_patch.py - edit the patch, not this file;
''' + NOTE + '''0.4.51 was derived from the generated 0.4.50 by tools/skills_0_4_51_patch.py;
''')
P.rep('VERSION = "0.4.51"', 'VERSION = "0.4.52"')

# ================================================================================================ 1. max Mana per class level
P.rep("CLASS_MANA_DEF = [('Archer', 2), ('Warrior', 2), ('Assassin', 2), ('Monk', 2), ('Mage', 10), ('Berserker', 2), ('Priest', 5), ('Spellblade', 4)]",
      "CLASS_MANA_DEF = %r   # 0.4.52 (Skyy 2026-10-18 \"scale down how much mana you get as you level\"): was 2 / 2 / 2 / 2 / 10 / 2 / 5 / 4"
      % [(_c, _n) for _c, _o, _n in PER])
P.rep('''CMAN_L.append("# 2026-10-03: Priest 5 (the metal wands); Mage 10 (the staffs cost twice the wand's Mana). 0 to 100 per level. The Base Mana")''',
      '''CMAN_L.append("# 2026-10-18 (less Mana per level): Mage 9.5, Priest 4.5, Spellblade 3, fighters 1. 0 to 100 per level. The Base Mana")''')
P.rep('''    CMAN_L.append("mana.classPerLevel.%s=%d" % (_cc, _cv))''', '''    CMAN_L.append("mana.classPerLevel.%s=%s" % (_cc, _cv))   # 0.4.52: %s (Mage 9.5, Priest 4.5)''')
P.rep('''assert dict(CLASS_MANA_DEF).get("Priest") == 5, "Skyy's lock 2026-10-03: Priest +5 max Mana per Divinity level"''',
      '''assert dict(CLASS_MANA_DEF).get("Priest") == 4.5, "Skyy 2026-10-18 (less Mana per level) supersedes the 2026-10-03 Priest +5 lock"''')
P.rep('''", ".join("%d.0" % _v for _c, _v in CLASS_MANA_DEF), cman))''', '''", ".join(repr(float(_v)) for _c, _v in CLASS_MANA_DEF), cman))   # 0.4.52: 9.5 / 4.5''')
P.rep('''    assert _dp.get("mana.classPerLevel." + _cc) == str(_cv) and ("\\nmana.classPerLevel.%s=%d\\n" % (_cc, _cv)) in ("\\n" + CMAN_DEFAULTS), _cc''',
      '''    assert _dp.get("mana.classPerLevel." + _cc) == str(_cv) and ("\\nmana.classPerLevel.%s=%s\\n" % (_cc, _cv)) in ("\\n" + CMAN_DEFAULTS), _cc''')
P.rep('''     "Max Mana a listed class gains per level of its own class skill (Mage 10, Priest 5, fighters 2).", "reload;check=ClassMana.checkEntry"),''',
      '''     "Max Mana a listed class gains per level of its own class skill (Mage 9.5, Priest 4.5, fighters 1).", "reload;check=ClassMana.checkEntry"),''')

# ================================================================================================ 2. regen
P.rep('''MREG_DEF = "75"   # 0.4.25 (Skyy 2026-10-08 "mana regen from the various sources"): was 50''',
      '''MREG_DEF = "65"   # 0.4.52 (Skyy 2026-10-18 "and mana regen a little"): was 75 (0.4.25 Skyy 2026-10-08 "mana regen from the various sources": was 50)''')
P.rep('''MREG_L.append("# a charge. mana.regen.inCombat (Skyy 2026-10-08: 75) is how fast Mana refills in combat, as a percent of the normal refill;")''',
      '''MREG_L.append("# a charge. mana.regen.inCombat (65 since 2026-10-18) is how fast Mana refills in combat, as a percent of the normal refill;")''')
P.rep('''KXP_PER_DEF, KXP_FROM_DEF = "7", "20"''', '''KXP_PER_DEF, KXP_FROM_DEF = "5", "20"   # 0.4.52 (Skyy 2026-10-18 "and mana regen a little"): perLevel was 7''')
P.rep('''            "# mana.regen.fromLevel (7 and 20: class level 30 = +70 percent, 40 = +140 percent). It is one more Mana Regen boost, in and",''',
      '''            "# mana.regen.fromLevel (5 and 20: class level 30 = +50 percent, 40 = +100 percent). It is one more Mana Regen boost, in and",''')
P.rep('''P25_HIT_CD = "500"''', '''P25_HIT_CD = "750"   # 0.4.52 (Skyy 2026-10-18 "and mana regen a little"): was 500 (twice a second)''')
P.rep('''     "At most one Mana-on-hit per player in this many milliseconds (500 = twice a second).", "reload"),''',
      '''     "At most one Mana-on-hit per player in this many milliseconds (500 = twice a second, 750 default).", "reload"),''')
P.rep('''('mana.regen.inCombat', '50', '75')]''', '''('mana.regen.inCombat', '50', MREG_DEF)]   # 0.4.52: an untouched 0.4.24 50 lands on today's default''')
P.rep('''assert _dp.get("mana.base") == "25" and _dp.get("mana.regen.inCombat") == "75" and''',
      '''assert _dp.get("mana.base") == "25" and _dp.get("mana.regen.inCombat") == MREG_DEF == "65" and''')

# ================================================================================================ 3. Mn52Mig
MN52_MARK_ID = "SkyySkills 0.4.52 less Mana"
MN52_MARK = "# SkyySkills 0.4.52 less Mana: per class level fighters 1, Mage 9.5, Priest 4.5, Spellblade 3; regen 65 / 5, on-hit 750 ms."
assert "=" not in MN52_MARK and ":" in MN52_MARK and len(MN52_MARK) <= 140 and all(ord(_ch) < 128 for _ch in MN52_MARK)
P.rep('''DEFAULTS = "\\n".join(L) + "\\n"
assert all(ord(ch) < 128 for ch in DEFAULTS)
''', '''MN52_MARK_ID = "''' + MN52_MARK_ID + '''"
MN52_MARK = "''' + MN52_MARK + '''"
MN52_KEYS = ''' + repr(MN_KEYS) + '''
L.append("")
L.append(MN52_MARK)   # 0.4.52: Mn52Mig's run-once marker - only a FRESH file has it (no block an older migration appends carries it)
DEFAULTS = "\\n".join(L) + "\\n"
assert all(ord(ch) < 128 for ch in DEFAULTS)
assert DEFAULTS.count(MN52_MARK_ID) == 1 and all(("\\n" + DEFAULTS).count("\\n%s=%s\\n" % (_k, _n)) == 1 for _k, _o, _n in MN52_KEYS)   # 0.4.52
''')
P.rep('''"\\n" + G43_DEFAULTS + "\\n" + G44_DEFAULTS)   # 0.4.44: + G44;''', '''"\\n" + G43_DEFAULTS + "\\n" + G44_DEFAULTS + "\\n" + MN52_MARK + "\\n")   # 0.4.52: + the Mn52Mig marker; 0.4.44: + G44;''')
P.rep('''fl50 = pool.makeClass(PKG + ".Fl50Mig")        # 0.4.50: the one-time felled-tree search limits update of an existing xp.properties
''', '''fl50 = pool.makeClass(PKG + ".Fl50Mig")        # 0.4.50: the one-time felled-tree search limits update of an existing xp.properties
mn52 = pool.makeClass(PKG + ".Mn52Mig")        # 0.4.52: the one-time less-Mana update (class Mana per level + regen) of an existing xp.properties
''')
_a = P.s.index('fl50.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(FL50_MARK_ID), fl50))')
_e = P.s.index('could not update xp.properties for 0.4.50', _a)
_e = P.s.index('}"""), fl50))\n', _e) + len('}"""), fl50))\n')
CL = P.s[_a:_e]


def _sub(t, o, n):
    assert t.count(o) >= 1, o
    return t.replace(o, n)


CL = _sub(CL, "json.dumps(FL50_MARK_ID)", "json.dumps(MN52_MARK_ID)")
CL = _sub(CL, "json.dumps(FL50_MARK)", "json.dumps(MN52_MARK)")
CL = _sub(CL, '''fl50.addField(CtField.make('public static final String[] KEYS = new String[] { "fell.radius", "fell.maxLogs", "fell.maxLeaves", "fell.maxReads" };', fl50))''',
          "fl50.addField(CtField.make('public static final String[] KEYS = new String[] { %s };', fl50))" % ", ".join('"%s"' % _k for _k, _o, _n in MN_KEYS))
CL = _sub(CL, '''fl50.addField(CtField.make('public static final String[] OLDS = new String[] { "8", "256", "384", "8000" };', fl50))''',
          "fl50.addField(CtField.make('public static final String[] OLDS = new String[] { %s };', fl50))" % ", ".join('"%s"' % _o for _k, _o, _n in MN_KEYS))
CL = _sub(CL, '''fl50.addField(CtField.make('public static final String[] NEWS = new String[] { "16", "1024", "2048", "40000" };', fl50))''',
          "fl50.addField(CtField.make('public static final String[] NEWS = new String[] { %s };', fl50))" % ", ".join('"%s"' % _n for _k, _o, _n in MN_KEYS))
CL = _sub(CL, '''assert all(("\\n" + DEFAULTS).count("\\n%s=%s\\n" % (_k, _n)) == 1 for _k, _o, _n in [('fell.radius', '8', '16'), ('fell.maxLogs', '256', '1024'), ('fell.maxLeaves', '384', '2048'), ('fell.maxReads', '8000', '40000')])''',
          '''assert all(("\\n" + DEFAULTS).count("\\n%s=%s\\n" % (_k, _n)) == 1 for _k, _o, _n in MN52_KEYS)''')
# a line already holding the NEW default (a block an older migration appended this start) is not "an admin's value"
CL = _sub(CL, '''    else if (eff[i] != null) kept.append(''', '''    else if (eff[i] != null && !(eff[i].equals(NEWS[i]) && !multi[i])) kept.append(''')
CL = _sub(CL, '"SkyySkills 0.4.50"', '"SkyySkills 0.4.52"')
CL = _sub(CL, "0.4.50 (felled tree search limits; the file", "0.4.52 (less Mana; the file")
CL = _sub(CL, "0.4.50 (felled tree search limits)", "0.4.52 (less Mana)")
CL = _sub(CL, "the 0.4.50 default is", "the 0.4.52 default is")
CL = _sub(CL, "before the 0.4.50 felled tree search update", "before the 0.4.52 less Mana update")
CL = _sub(CL, "updated for 0.4.50:", "updated for 0.4.52:")
CL = _sub(CL, "0.4.50 marker added", "0.4.52 marker added")
CL = CL.replace("fl50", "mn52")
assert "0.4.50" not in CL and "fl50" not in CL and "FL50" not in CL and "fell." not in CL, [l for l in CL.splitlines() if "50" in l or "fell" in l][:5]
MN_JAVA = """
# ---- Mn52Mig (0.4.52, PROJECT-RULES section 4; a clone of Fl50Mig / Pd44Mig's reviewed machinery): ONCE on an EXISTING xp.properties,
# setup() right after Fl50Mig.run, BEFORE SkillCfg.load. The 8 mana.classPerLevel.<Class> entries + mana.regen.inCombat / perLevel +
# mana.onHitCooldownMs: when a key's LAST entry is a one-line entry holding exactly the old default -> the new one; any other value kept
# (INFO; a line already at the new default is not reported); no line = nothing. The marker at the end; config-history copy first; one
# config-changes.log line per change (Undo); Properties check; atomicWrite.
""" + CL
P.rep('''
# ================= SkillIO.run (0.4.32 C): the SkyySkills-IO jobs''', MN_JAVA + '''
# ================= SkillIO.run (0.4.32 C): the SkyySkills-IO jobs''')
P.rep('''  {PKG}.Fl50Mig.run();        // 0.4.50: untouched felled-tree search limits 8 / 256 / 384 / 8000 -> 16 / 1024 / 2048 / 40000, once; History first
''', '''  {PKG}.Fl50Mig.run();        // 0.4.50: untouched felled-tree search limits 8 / 256 / 384 / 8000 -> 16 / 1024 / 2048 / 40000, once; History first
  {PKG}.Mn52Mig.run();        // 0.4.52: untouched class Mana per level + Mana regen defaults -> the lower 0.4.52 ones, once; History first
''')
P.rep('''          rbcm, snd39, rbs39, pd44, fm48, zo49, fl50, ob50,''', '''          rbcm, snd39, rbs39, pd44, fm48, zo49, fl50, mn52, ob50,''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
print("wrote SkyySkills/build_skyyskills_0.4.52.py (%d changes)" % len(P.changes))
