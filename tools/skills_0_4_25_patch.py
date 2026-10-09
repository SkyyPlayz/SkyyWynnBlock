"""Derive SkyySkills/build_skyyskills_0.4.25.py from the LIVE generated SkyySkills/build_skyyskills_0.4.24.py (= the tools/deploy_set.py SET
pin; 0.4.24 came from 0.4.23 by tools/skills_0_4_24_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_17_patch.py: rep(old, new) with asserted single anchors, newline-agnostic; 0.4.24
stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_25_patch.py   then   python SkyySkills/build_skyyskills_0.4.25.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.25.py --dir tools/dev/scratch/<task>/skills0425   (bare JVM, -Xverify:all; the folder is deleted)

0.4.25 = THE CLASS POWER SPLIT + SKILL STAT PERKS (Skyy 2026-10-08, docs/answered/skills.md; research/Class-Power-Split.md is THE SPEC for the
per-class Mana / Stamina numbers - this patch reads its table and stops when the numbers below differ):
  "increase the max stamina from mining a good bit ... at least 20 at lvl 100. swap foraging to giving defense instead of health. at least 20
   at lvl 100 class skill should slightly boost all stats ... a little more to the weak stats, so a lvl 100 class has a lot more balanced
   stats than a lvl 25 or 50." / "definetly add the +2 mana per level for physical classes." / "make sure all classes get a decent amount of
   max mana, and mana regen from the various sources" / "the classes should verry in max mana and stamina, like allocating power" /
   "make the split make sense for the class and how its played."
(1) MINING STAMINA: perk.mining.staminaPerLevel 0.05 -> 0.2 (+20 max Stamina at Mining 100).
(2) FORAGING -> DEFENSE: perk.foraging.healthPerLevel 0.1 -> 0, NEW perk.<skill>.defensePerLevel (foraging 0.2 = +20 at 100, every other
    skill 0). DEFENSE = SkyyGear's own stat and formula: SkyyGear 0.2.11 GearArmorSys (Filter group, AFTER the engine's ArmorDamageReduction)
    multiplies a player's damage from an entity source by scale / (scale + Defense) (combat.defScale, default 100), Defense = the active
    armor's def + the gear:extra:<uuid> def (SkyyAccessories OWNS that key - one writer, it overwrites any other text, so SkyySkills cannot
    publish into it, and no other key is read by SkyyGear). CHOSEN: SkyySkills applies the SAME formula itself, SUMMED with the gear Defense,
    in its own Filter system DefSys, also AFTER ArmorDamageReduction (SystemDependency; unordered fallback DefSysU + one WARN): factor =
    target / applied, target = scale / (scale + G + S), applied = what SkyyGear already did (scale / (scale + G) when its part.stats is on and
    G > 0, else 1), G = def of gear:stats:<uuid> (SkyyGear's active armor) + def of gear:extra:<uuid>, S = the skill Defense; scale and part.stats
    come from SkyyGear's own settings (config:fn:SkyyGear get, re-read every 5 s; without SkyyGear: scale 100, G 0). So a player with gear
    Defense G and skill Defense S takes EXACTLY what SkyyGear would give for G + S (multiplications commute; SkyyGear's armor fix is a ratio).
    Same victims as SkyyGear: players hit from an entity source (mobs, players); never fall / environment damage. NO SkyyGear change.
    Known limit (PvP only): if DefSys runs after SkyyGear's GearTrueSys in a hit, the attacker's True / element damage add-on is cut too
    (mobs carry none). The skill Defense is published as skill:def:<uuid> (Double) for a later SkyyMenu Stats row.
(3) CLASS BALANCE: the class skill adds a little to EVERY stat SkyySkills can change - max Health, max Mana, max Stamina, Defense, class weapon
    damage %, Mana regen % - 0 at level 0 up to the classBoost.<stat>.<Class> table value at level 100 (straight line). Weak stats get more,
    strong ones less (flat stats 3 to 15, damage 2 to 5 %, regen 3 to 15 %) - see BOOST below. perk.combat.healthPerLevel (+0.1 a class level
    for everyone) and perk.combat.damagePerLevel (+0.2 %) are KEPT as the shared part; the class balance is a separate, per-class part on top
    (own modifier keys skyyskill_classboost*, the damage % added into the same one multiplication in CombatDmgSys - nothing counted twice).
(4) CLASS POWER SPLIT (spec table): mana.base 10 -> 25, mana.classBase for every class (Mage 45, Priest 42, Spellblade 33, Archer 24,
    Assassin 24, Monk 21, Warrior 21, Berserker 12), mana.classPerLevel (+2 for the physical classes, Spellblade 4; Mage 10 / Priest 5 kept),
    NEW stamina.classBase.<Class> (max Stamina on top of vanilla's 10) + stamina.classPerLevel.<Class> (per class skill level): MAX / ADDITIVE
    modifier skyyskill_classstamina computed from scratch every second in Perks.ovl (the active profile's class, its own class skill level) -
    a class or profile switch changes it within a second, never stacks, held through the 10 s session start like the class Mana. Spellblade
    (not in SkyyClasses yet) is a valid table entry (OverallCfg.TCLASSES) and just sits in the tables.
(5) MANA REGEN: mana.regen.inCombat 50 -> 75; NEW Mana on hit: a hit that LANDED (ManaHitSys, Inspect group) on a monster with an allowed class
    weapon (the exact combat XP check: SkillClass.slot + consistent + weaponOk) gives mana.onHit.<Class> Mana (Warrior / Berserker / Monk /
    Assassin / Archer 1, Mage / Priest 0) at most once per mana.onHitCooldownMs (500) per player, queued and added on the world thread at the
    next AcroSys tick (no stat write inside the damage dispatch), never above max Mana, nothing while dead, hits on players only with
    mana.onHitVsPlayers=true. Shown as a Mana Regen source ("Mana on hit +1 ...", skill:fn:manaregen sources -> SkyyMenu's Stats page) and
    on the class skill's Stats page; the class balance regen % is the source "class balance".
MIGRATION (PerkMig, PROJECT-RULES 4, setup after AcroMig.run, BEFORE SkillCfg.load): ONCE (marker comment) on an existing xp.properties: lines
    still holding the OLD default are rewritten (perk.mining.staminaPerLevel 0.05 -> 0.2, perk.foraging.healthPerLevel 0.1 -> 0, mana.base
    10 -> 25, mana.classBase.Mage 30 -> 45, mana.classBase.Priest 30 -> 42, mana.regen.inCombat 50 -> 75; numeric compare, one-line entries,
    value text only), an admin's value is kept + logged; missing lines are appended in ONE block (perk.foraging.defensePerLevel, the missing
    mana.classBase / mana.classPerLevel classes, the stamina / Mana on hit / class balance tables); History snapshot first, one
    config-changes.log line with Undo per rewritten value and per added Mana / Defense line, the file's bytes + line endings kept, the kit's
    atomicWrite, a Properties check (only the planned keys differ).
SERVER SETUP: new category "Class Power" (13 rows) + perk.<skill>.defensePerLevel rows (9) = 227 rows.
ROLLBACK below 0.4.25 (fix round): the 4 new MAX modifiers skyyskill_classstamina / _classboosthp / _classboostmana / _classbooststamina are
    saved with the player and 0.4.24 does not know them: switch "Class Stamina" (stamina.class.enabled) and "Class balance boost"
    (classBoost.enabled) off in Server Setup and let players log in once BEFORE rolling back (off = the next second removes them; harness P).
NOT in this build: SkyyMenu's Stats page Defense / Class Weapon Damage rows still read only gear + perk.combat.damagePerLevel (a SkyyMenu
round can read skill:def:<uuid> and the class balance); the Monk "Zen" rename; ability Mana / Stamina costs (SkyyArmory / SkyyClasses).
"""
import difflib
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.24.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.25.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.24"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.24"' in s and "derived from the generated 0.4.23 by tools/skills_0_4_24_patch.py" in s, "not the live generated 0.4.24"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
for _x in ('".PerkMig"', "defensePerLevel", "stamina.classBase", "classBoost.", "mana.onHit", "TCLASSES", '".DefSys"'):
    assert _x not in s, "0.4.24 already has " + _x
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
OLDS = []


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    i = s.index(old)
    j = s.find(LF, i + len(old))
    OLDS.append(s[s.rfind(LF, 0, i) + 1:(j if j >= 0 else len(s))])
    s = s.replace(old, new)


def after(anchor, add):
    rep(anchor, anchor + add)


def before(anchor, add):
    rep(anchor, add + anchor)


# ================================================================================================ THE NUMBERS
CLS = ["Archer", "Warrior", "Assassin", "Monk", "Mage", "Berserker", "Priest", "Spellblade"]   # SkillDefs.CLASSES order + the future class
# research/Class-Power-Split.md "Split per class" (THE SPEC, read-only here): Base Mana, Base Stamina bonus, Mana / level, Stamina / level
SPEC = {"Mage": (45, 4, 10, "0.05"), "Priest": (42, 5, 5, "0.06"), "Spellblade": (33, 7, 4, "0.09"), "Archer": (24, 9, 2, "0.12"),
        "Assassin": (24, 9, 2, "0.12"), "Monk": (21, 10, 2, "0.13"), "Warrior": (21, 10, 2, "0.13"), "Berserker": (12, 12, 2, "0.16")}
_spec = open(os.path.join(ROOT, "research", "Class-Power-Split.md"), encoding="utf8").read()
_seen = {}
for _ln in _spec.splitlines():
    _m = re.match(r"\|\s*([A-Z][a-z]+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|[^|]*\|\s*(\d+)\s*\|\s*\+(\d+)\s*\|\s*(\d+)[^|]*\|\s*([\d.]+)\s*\|", _ln)
    if _m:
        _seen[_m.group(1)] = (int(_m.group(4)), int(_m.group(5)), int(_m.group(6)), _m.group(7))
assert _seen == SPEC, "research/Class-Power-Split.md table changed - update SPEC here first: %r" % _seen
assert re.search(r"\|\s*\(no class\)\s*\|.*\|\s*25 \(mana\.base\)\s*\|", _spec), "the spec's no-class base Mana is not 25 any more"
MANA_BASE_NEW = "25"
MREG_NEW = "75"
# Mana on hit (task + spec "Regen"): melee + Archer 1, casters 0; Spellblade not decided (not listed)
HIT = [("Archer", "1"), ("Warrior", "1"), ("Assassin", "1"), ("Monk", "1"), ("Mage", "0"), ("Berserker", "1"), ("Priest", "0")]
# CLASS BALANCE at class level 100 (0 at level 0, a straight line). Derived from the class chart ratings (tools/dev/scratch/classchart/
# class-balance.html, snapshot 2026-10-08, 1-10: hp / def / mana / best of single target, area, melee, ranged) and the spec's Stamina %:
#   flat (Health from hp, Defense from def, Mana from mana, Stamina from Stamina% / 8): round(3 + (9 - r) x 12 / 7) kept in 3..15
#   damage % (best damage rating): round(2 + (9 - r) x 6 / 7) kept in 2..8 ; Mana regen % (mana rating): the flat rule (3..15 %)
RATINGS = {"Warrior": (9, 10, 3, 6, 65), "Berserker": (8, 6, 3, 9, 80), "Archer": (4, 3, 2, 10, 60), "Mage": (2, 2, 10, 9, 25),
           "Priest": (4, 4, 9, 5, 30), "Monk": (5, 5, 4, 9, 65), "Assassin": (3, 2, 4, 10, 60), "Spellblade": (6, 6, 6, 9, 45)}


def _flat(r):
    return max(3, min(15, int(round(3 + (9 - r) * 12.0 / 7.0))))


def _pct(r):
    return max(2, min(8, int(round(2 + (9 - r) * 6.0 / 7.0))))


BOOST = {}
for _c in CLS:
    _hp, _df, _mn, _dm, _st = RATINGS[_c]
    BOOST[_c] = {"health": _flat(_hp), "mana": _flat(_mn), "stamina": _flat(int(round(_st / 8.0))), "defense": _flat(_df),
                 "damage": _pct(_dm), "regen": _flat(_mn)}
assert [BOOST[_c]["health"] for _c in CLS] == [12, 3, 13, 10, 15, 5, 12, 8]
assert [BOOST[_c]["stamina"] for _c in CLS] == [5, 5, 5, 5, 13, 3, 12, 8]
assert [BOOST[_c]["damage"] for _c in CLS] == [2, 5, 2, 2, 2, 2, 5, 2]
BOOST_STATS = ["health", "mana", "stamina", "defense", "damage", "regen"]
# the chart may have moved on since the snapshot: say so (never a stop - the numbers above are this build's defaults)
try:
    _ch = open(os.path.join(ROOT, "tools", "dev", "scratch", "classchart", "class-balance.html"), encoding="utf8").read()
    for _c in CLS:
        _m = re.search(r'name: "%s".*?r: \{ speed: \d+, hp: (\d+), def: (\d+), mana: (\d+), st: (\d+), aoe: (\d+), melee: (\d+), range: (\d+)' % _c, _ch, re.S)
        if _m:
            _now = (int(_m.group(1)), int(_m.group(2)), int(_m.group(3)), max(int(_m.group(i)) for i in (4, 5, 6, 7)))
            if _now != RATINGS[_c][:4]:
                print("NOTE: the class chart's %s ratings are now %s (this build used %s) - the class balance defaults may want a look" % (_c, _now, RATINGS[_c][:4]))
except OSError:
    print("NOTE: the class chart is not here - class balance defaults from the 2026-10-08 snapshot")

# ================================================================================================ docstring + version
rep('''"""SkyySkills 0.4.24 - build script (derived from the generated 0.4.23 by tools/skills_0_4_24_patch.py - edit the patch, not this file;
0.4.23 was derived''', '''"""SkyySkills 0.4.25 - build script (derived from the generated 0.4.24 by tools/skills_0_4_25_patch.py - edit the patch, not this file;
0.4.24 was derived from the generated 0.4.23 by tools/skills_0_4_24_patch.py; 0.4.23 was derived''')
HEAD_0425 = '''0.4.25: THE CLASS POWER SPLIT + SKILL STAT PERKS (Skyy 2026-10-08, docs/answered/skills.md; research/Class-Power-Split.md; full notes in
  tools/skills_0_4_25_patch.py). Mining +0.2 max Stamina a level (was 0.05); Foraging gives Defense (+0.2 a level, SkyyGear's Defense formula
  summed with the gear Defense - DefSys, AFTER ArmorDamageReduction) instead of Health; the class skill adds a little to every stat, more to
  the class's weak ones (class balance tables, 0 at level 0 -> full at 100); per-class Base Mana / Mana per level / max Stamina / Stamina per
  level (the power split; mana.base 25); in-combat Mana regen 75 %; Mana on hit with class weapons (ManaHitSys, 0.5 s cooldown). PerkMig:
  once, untouched old defaults rewritten + missing lines appended, History first, Undo lines. Server Setup category "Class Power".
  ROLLBACK below 0.4.25: switch "Class Stamina" and "Class balance boost" off in Server Setup and let players log in once (skyyskill_classstamina
  and skyyskill_classboosthp / _classboostmana / _classbooststamina are saved with the player; 0.4.24 never removes them).
  CHECKED in a bare JVM (SkyySkills/test_skyyskills_0.4.25.py, -Xverify:all).
'''
before('0.4.24: THE WOOD WAND SIGNATURE (Skyy 2026-10-08 "Wand can shoot a shot that ricochets through eight enemies"; full notes in\n', HEAD_0425)
rep('VERSION = "0.4.24"', 'VERSION = "0.4.25"')

# ================================================================================================ default file: changed defaults
rep('''PERK_L.append("#   applied as MAX modifiers skyyskill_health / skyyskill_stamina / skyyskill_mana; vanilla max: 100 health, 10 stamina)")
''', '''PERK_L.append("#   applied as MAX modifiers skyyskill_health / skyyskill_stamina / skyyskill_mana; vanilla max: 100 health, 10 stamina)")
PERK_L.append("#   perk.<skill>.defensePerLevel = Defense per level (0.4.25): hits from monsters and players x 100 / (100 + Defense), summed with")
PERK_L.append("#   the SkyyGear Defense of your armor and accessories (SkyyGear's own formula and Defense curve setting)")
''')
rep('PERK_L.append("perk.mining.staminaPerLevel=0.05")\n', 'PERK_L.append("perk.mining.staminaPerLevel=0.2")   # 0.4.25 (Skyy 2026-10-08): +20 at Mining 100\n')
rep('PERK_L.append("perk.foraging.healthPerLevel=0.1")\n', '''PERK_L.append("perk.foraging.healthPerLevel=0")      # 0.4.25 (Skyy 2026-10-08): Foraging gives Defense instead of Health
PERK_L.append("perk.foraging.defensePerLevel=0.2")   # 0.4.25: +20 Defense at Foraging 100
''')
rep('OVL_L.append("mana.base=10")\n', 'OVL_L.append("mana.base=%s")   # 0.4.25 (research/Class-Power-Split.md: no class = 25)\n' % MANA_BASE_NEW)
rep('''CLASS_BASE_DEF = [('Mage', 30), ('Priest', 30)]   # 0.4.8 (Skyy 2026-09-30): enough Mana for the starter weapons (Mage staff 10 a cast, Priest wand 5)
''', '''# 0.4.25 (research/Class-Power-Split.md, Skyy 2026-10-08 "make the split make sense for the class"): every class, in OverallCfg.TCLASSES
# order (SkillDefs.CLASSES + Spellblade, which SkyyClasses does not have yet); was Mage 30, Priest 30 (0.4.8)
CLASS_BASE_DEF = %r
''' % [(_c, SPEC[_c][0]) for _c in CLS])
rep('''CLASS_MANA_DEF = [("Mage", 10), ("Priest", 5)]
''', '''# 0.4.25 (Skyy 2026-10-08 "definetly add the +2 mana per level for physical classes"; spec table): + the physical classes 2, Spellblade 4
CLASS_MANA_DEF = %r
''' % [(_c, SPEC[_c][2]) for _c in CLS])
rep('MREG_DEF = "50"\n', 'MREG_DEF = "%s"   # 0.4.25 (Skyy 2026-10-08 "mana regen from the various sources"): was 50\n' % MREG_NEW)
rep('''MREG_L.append("# a charge. mana.regen.inCombat (Skyy 2026-10-02: 50) is how fast Mana refills in combat, as a percent of the normal refill;")''',
    '''MREG_L.append("# a charge. mana.regen.inCombat (Skyy 2026-10-08: 75) is how fast Mana refills in combat, as a percent of the normal refill;")''')
rep('''assert [_c for _c, _v in CLASS_MANA_DEF] == [_c[0] for _c in CLASS_ROWS if _c[0] in dict(CLASS_MANA_DEF)], "CLASS_MANA_DEF must follow SkillDefs.CLASSES order"''',
    '''assert [_c for _c, _v in CLASS_MANA_DEF] == [_c for _c in [_r[0] for _r in CLASS_ROWS] + FUTURE_CLASSES if _c in dict(CLASS_MANA_DEF)], "CLASS_MANA_DEF must follow OverallCfg.TCLASSES order"''')
rep('''assert all(_c in [_r[0] for _r in CLASS_ROWS] for _c, _v in CLASS_BASE_DEF)''',
    '''assert all(_c in [_r[0] for _r in CLASS_ROWS] + FUTURE_CLASSES for _c, _v in CLASS_BASE_DEF)   # 0.4.25: + Spellblade (TCLASSES)''')

# ================================================================================================ default file: the 0.4.25 block
P25_PY = r'''# 0.4.25 (research/Class-Power-Split.md, Skyy 2026-10-08): the class power split's Stamina side, Mana on hit and the class balance - ONE block at
# the end of a fresh file; PerkMig appends the lines an existing file lacks ONCE (under the same marker). Spellblade is not a SkyyClasses class
# yet: its lines just sit in the tables (OverallCfg.TCLASSES accepts it).
FUTURE_CLASSES = ["Spellblade"]
P25_MARK_ID = "SkyySkills 0.4.25 class power split"
P25_STA_BASE = %(sb)r
P25_STA_PER = %(sp)r
P25_HIT = %(hit)r
P25_HIT_CD = "500"
P25_BOOST = %(boost)r
P25_BOOST_STATS = %(bst)r
P25_HEAD = ["# ---------- " + P25_MARK_ID + " (Mana vs Stamina, class balance, Mana on hit) ----------",
            "# Comments must stay on their own lines.",
            "# CLASS STAMINA: a class gets stamina.classBase on top of vanilla's 10 max Stamina, plus stamina.classPerLevel per level of its",
            "# own class skill (Warrior 0.13 = +13 at 100). Its Mana side = Base Mana by class + Max Mana per class level (mana.* lines).",
            "# MANA ON HIT: a hit on a monster with your class weapon gives mana.onHit.<Class> Mana back, at most once per",
            "# mana.onHitCooldownMs milliseconds, never above max Mana; hits on players only when mana.onHitVsPlayers is true.",
            "# CLASS BALANCE: your class skill adds a little to every stat - 0 at level 0 up to the classBoost numbers at level 100 - more",
            "# to the class's weak stats, so a level 100 class is more balanced. health / mana / stamina / defense are flat amounts, damage",
            "# is percent more class weapon damage (vs monsters, like perk.combat.damagePerLevel) and regen is percent more Mana regen."]
P25_LINES = (["stamina.class.enabled=true"] + ["stamina.classBase.%%s=%%s" %% _x for _x in P25_STA_BASE] + ["stamina.classPerLevel.%%s=%%s" %% _x for _x in P25_STA_PER]
             + ["mana.onHitCooldownMs=" + P25_HIT_CD, "mana.onHitVsPlayers=false"] + ["mana.onHit.%%s=%%s" %% _x for _x in P25_HIT] + ["classBoost.enabled=true"]
             + ["classBoost.%%s.%%s=%%d" %% (_st, _c, P25_BOOST[_c][_st]) for _st in P25_BOOST_STATS for _c in [_x[0] for _x in P25_STA_BASE]])
P25_L = P25_HEAD + P25_LINES
L.append("")
L.extend(P25_L)
P25_DEFAULTS = "\n".join(P25_L) + "\n"
assert all(ord(ch) < 128 for ch in P25_DEFAULTS) and '"' not in P25_DEFAULTS and "\\" not in P25_DEFAULTS
assert not any(_cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln) for _ln in P25_L), "a comment looks like a template line"
P25_KEYS = [_ln.split("=", 1)[0] for _ln in P25_LINES]
assert len(P25_KEYS) == len(set(P25_KEYS)) == 1 + 8 + 8 + 2 + 7 + 1 + 6 * 8 and sum(1 for _ln in P25_L if P25_MARK_ID in _ln) == 1
assert all(len(_ln) <= 140 for _ln in P25_L)
P25_HEAD_LIT = json.dumps("\n".join(P25_HEAD) + "\n")
''' % {"sb": [(_c, str(SPEC[_c][1])) for _c in CLS], "sp": [(_c, SPEC[_c][3]) for _c in CLS], "hit": HIT, "boost": BOOST, "bst": BOOST_STATS}
after('''assert MREG_DOC_OLD != MREG_DOC_NEW and MREG_DOC_NEW in MREG_L and MREG_DOC_OLD not in MREG_L and "charging" not in MREG_DOC_OLD.replace("never while charging", "")
''', P25_PY)
# FUTURE_CLASSES is used by the CLASS_BASE_DEF / CLASS_MANA_DEF asserts above the block: define it early as well (same value)
before("# 0.4.25 (research/Class-Power-Split.md, Skyy 2026-10-08 \"make the split make sense for the class\"): every class, in OverallCfg.TCLASSES\n",
       "FUTURE_CLASSES = [\"Spellblade\"]   # 0.4.25: classes the tables accept before SkyyClasses has them (OverallCfg.TCLASSES)\n")

# the modifier keys: + the 0.4.25 class Stamina / class balance keys (all start skyyskill_class: SkyyMenu's Stats page groups them as Class)
rep('''OVL_KEYS = ["skyyskill_basemana", "skyyskill_overallhp", "skyyskill_overallmana", "skyyskill_classmana"]   # 0.4.15: + max Mana per class level
assert len(set(OVL_KEYS)) == 4 and all(k.startswith("skyyskill_") for k in OVL_KEYS)''',
    '''OVL_KEYS = ["skyyskill_basemana", "skyyskill_overallhp", "skyyskill_overallmana", "skyyskill_classmana",   # 0.4.15: + max Mana per class level
            "skyyskill_classstamina", "skyyskill_classboosthp", "skyyskill_classboostmana", "skyyskill_classbooststamina"]   # 0.4.25
assert len(set(OVL_KEYS)) == 8 and all(k.startswith("skyyskill_") for k in OVL_KEYS) and all(k.startswith("skyyskill_class") for k in OVL_KEYS[3:])''')

# ================================================================================================ OverallCfg: Spellblade in the class tables
rep('''ovc.addField(CtField.make('public static final String TABLE_PREFIX = "mana.classBase.";', ovc))
''', '''ovc.addField(CtField.make('public static final String TABLE_PREFIX = "mana.classBase.";', ovc))
# 0.4.25: the classes a class table accepts = SkillDefs.CLASSES + the classes SkyyClasses does not have yet (Spellblade) - their lines just
# sit in the tables until the class exists (no class skill = level 0)
ovc.addField(CtField.make("public static final String[] TCLASSES = %s;" % jarr([_c[0] for _c in CLASS_ROWS] + FUTURE_CLASSES), ovc))
''')
rep("""  String x = {PKG}.SkillDefs.canonName(t.trim());
  for (int k = 0; k < {PKG}.SkillDefs.CLASSES.length; k++) if ({PKG}.SkillDefs.CLASSES[k].equalsIgnoreCase(x)) return {PKG}.SkillDefs.CLASSES[k];
  return null;""", """  String x = {PKG}.SkillDefs.canonName(t.trim());
  for (int k = 0; k < TCLASSES.length; k++) if (TCLASSES[k].equalsIgnoreCase(x)) return TCLASSES[k];   // 0.4.25: + Spellblade
  return null;""")
rep("""public static Object[] mkTable(String[] c, double[] b) {{
  int n = {PKG}.SkillDefs.CLASSES.length;""", """public static Object[] mkTable(String[] c, double[] b) {{
  int n = TCLASSES.length;   // 0.4.25: SkillDefs.CLASSES + Spellblade, in that order""")
rep("""      if ({PKG}.SkillDefs.CLASSES[k].equals(x) && !has[k]) {{ has[k] = true; v[k] = b[i]; cnt++; }}""",
    """      if (TCLASSES[k].equals(x) && !has[k]) {{ has[k] = true; v[k] = b[i]; cnt++; }}""")
rep("""    oc[j] = {PKG}.SkillDefs.CLASSES[k];
    ob[j] = v[k];""", """    oc[j] = TCLASSES[k];
    ob[j] = v[k];""")
rep('''  if (canonClass(e) != null) return null;
  if (e.length() > 40) e = e.substring(0, 40) + "...";
  return "Unknown class " + e + " - use Archer, Warrior, Mage, Berserker, Priest, Assassin or Monk.";''',
    '''  if (canonClass(e) != null) return null;
  if (e.length() > 40) e = e.substring(0, 40) + "...";
  return "Unknown class " + e + " - use Archer, Warrior, Mage, Berserker, Priest, Assassin, Monk or Spellblade.";''')
rep('''  if (@PKG@.OverallCfg.canonClass(e) != null) return null;
  if (e.length() > 40) e = e.substring(0, 40) + "...";
  return "Unknown class " + e + " - use Archer, Warrior, Mage, Berserker, Priest, Assassin or Monk.";''',
    '''  if (@PKG@.OverallCfg.canonClass(e) != null) return null;
  if (e.length() > 40) e = e.substring(0, 40) + "...";
  return "Unknown class " + e + " - use Archer, Warrior, Mage, Berserker, Priest, Assassin, Monk or Spellblade.";''')
rep('for _decl in ("boolean MANA_ON = true", "double BASE = 10.0", "boolean ON = true",',
    'for _decl in ("boolean MANA_ON = true", "double BASE = %s.0", "boolean ON = true",' % MANA_BASE_NEW)
rep('''  BASE = clampD({PKG}.SkillCfg.dbl(p, "mana.base", 10.0), 10.0, 0.0, 10000.0);''',
    '''  BASE = clampD({PKG}.SkillCfg.dbl(p, "mana.base", %s.0), %s.0, 0.0, 10000.0);   // 0.4.25: default 25 (was 10)''' % (MANA_BASE_NEW, MANA_BASE_NEW))

# ================================================================================================ PerkCfg: + Defense, new defaults
rep('''"boolean WEAPON_ONLY = true", "double[] HP = new double[] { 0.0, 0.1, 0.25, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0 }",
              "double[] STA = new double[] { 0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1 }",''',
    '''"boolean WEAPON_ONLY = true", "double[] HP = new double[] { 0.0, 0.0, 0.25, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0 }",
              "double[] STA = new double[] { 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1 }",
              "double[] DEF = new double[] { 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 }", ''')
rep('''  double[] dhp = new double[] {{ 0.0, 0.1, 0.25, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0 }};
  double[] dsta = new double[] {{ 0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1 }};''',
    '''  double[] dhp = new double[] {{ 0.0, 0.0, 0.25, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0 }};   // 0.4.25: Foraging 0 (it gives Defense)
  double[] dsta = new double[] {{ 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1 }};   // 0.4.25: Mining 0.2
  double[] ddef = new double[] {{ 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 }};   // 0.4.25: Foraging 0.2 Defense''')
rep('''  double[] mana = new double[nk];
  double[] dd = new double[nk];''', '''  double[] mana = new double[nk];
  double[] def = new double[nk];
  double[] dd = new double[nk];''')
rep('''    mana[i] = rate(p, k + "manaPerLevel", dmana[i]);
''', '''    mana[i] = rate(p, k + "manaPerLevel", dmana[i]);
    def[i] = rate(p, k + "defensePerLevel", ddef[i]);
''')
rep('''  HP = hp; STA = sta; MANA = mana; DD = dd; ONLY = only;''', '''  HP = hp; STA = sta; MANA = mana; DEF = def; DD = dd; ONLY = only;''')

# ================================================================================================ config readers (before SkillCfg.load)
CFG25 = r'''# ================= 0.4.25 ClassTbl / ClassPower part 1 / ManaHit part 1: the class power split tables (before SkillCfg.load) =================
# ClassTbl = the generic class table reader of the 0.4.25 tables (the ClassMana.parseTable rules with the table's prefix and bound): entries
# are class names in any case (OverallCfg.canonClass: SkillDefs.CLASSES + Spellblade), stored in the TCLASSES spelling / order; a line that is
# not a class or not a number is left out and reported; values clamped to 0..max. -> {String[], double[], String text, String problems}
ctb.addMethod(CtNewMethod.make(J14(r"""
public static Object[] parse(java.util.Properties p, String prefix, double max) {
  java.util.ArrayList cs = new java.util.ArrayList();
  java.util.ArrayList bs = new java.util.ArrayList();
  StringBuilder bad = new StringBuilder();
  java.util.Iterator it = new java.util.TreeSet(p.stringPropertyNames()).iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith(prefix)) continue;
    String e = k.substring(prefix.length()).trim();
    String c = @PKG@.OverallCfg.canonClass(e);
    String raw = p.getProperty(k);
    String shown = e.length() > 40 ? e.substring(0, 40) + "..." : e;
    if (c == null) { if (bad.length() > 0) bad.append("; "); bad.append(shown + " is not a class (left out)"); continue; }
    if (cs.contains(c)) { if (bad.length() > 0) bad.append("; "); bad.append(c + " is listed twice (" + shown + " left out)"); continue; }
    double v = Double.NaN;
    try { v = Double.parseDouble(raw.trim()); } catch (Throwable t) { v = Double.NaN; }
    if (Double.isNaN(v) || Double.isInfinite(v)) {
      if (bad.length() > 0) bad.append("; ");
      String rv = raw == null ? "" : raw.trim();
      bad.append(shown + "=" + (rv.length() > 20 ? rv.substring(0, 20) + "..." : rv) + " is not a number (left out)");
      continue;
    }
    cs.add(c);
    bs.add(Double.valueOf(@PKG@.OverallCfg.clampD(v, 0.0, 0.0, max)));
  }
  String[] c2 = new String[cs.size()];
  double[] b2 = new double[cs.size()];
  for (int i = 0; i < c2.length; i++) { c2[i] = (String) cs.get(i); b2[i] = ((Double) bs.get(i)).doubleValue(); }
  Object[] t = @PKG@.OverallCfg.mkTable(c2, b2);
  return new Object[] { t[0], t[1], t[2], bad.toString() };
}"""), ctb))
# the entry of a class (any case) in a table snapshot {String[], double[], ...}; 0 = not listed / no table
ctb.addMethod(CtNewMethod.make(J14(r"""
public static double get(Object[] t, String cls) {
  if (t == null || cls == null) return 0.0;
  String x = cls.trim();
  String[] c = (String[]) t[0];
  double[] b = (double[]) t[1];
  for (int i = 0; i < c.length && i < b.length; i++) if (c[i].equalsIgnoreCase(x)) return b[i];
  return 0.0;
}"""), ctb))
# check= hook of every 0.4.25 class table (key "<table>[<entry>]", value = the canonical text or null for a removal; also run for hand-edited
# lines): the entry must be a class (Spellblade included); the bounds are the row's own
ctb.addMethod(CtNewMethod.make(J14(r"""
public static String checkEntry(String key, String value) {
  if (value == null || key == null) return null;
  String e = key;
  int a = key.indexOf('[');
  int b = key.lastIndexOf(']');
  if (a >= 0 && b > a) e = key.substring(a + 1, b);
  if (@PKG@.OverallCfg.canonClass(e) != null) return null;
  if (e.length() > 40) e = e.substring(0, 40) + "...";
  return "Unknown class " + e + " - use Archer, Warrior, Mage, Berserker, Priest, Assassin, Monk or Spellblade.";
}"""), ctb))
# ClassPower: T = ONE snapshot Object[8] of table snapshots: 0 stamina.classBase, 1 stamina.classPerLevel, 2..7 classBoost.<health, mana, stamina,
# defense, damage, regen> (null = not read yet = the default tables; a file without the lines = empty tables = nothing). STA_ON / B_ON = the
# two switches.
cpw.addField(CtField.make("public static final String[] PREFIX = %s;" % jarr(["stamina.classBase.", "stamina.classPerLevel."] + ["classBoost.%s." % _st for _st in P25_BOOST_STATS]), cpw))
cpw.addField(CtField.make("public static final double[] MAX = new double[] { 1000.0, 100.0, 1000.0, 1000.0, 1000.0, 1000.0, 100.0, 1000.0 };", cpw))
cpw.addField(CtField.make('public static final String[] LABEL = new String[] { "Max Stamina by class", "Max Stamina per class level", "Class balance: Health", "Class balance: Mana", "Class balance: Stamina", "Class balance: Defense", "Class balance: damage", "Class balance: Mana regen" };', cpw))
cpw.addField(CtField.make("public static final String[] DEF_CLS = %s;" % jarr([_c for _c, _v in P25_STA_BASE]), cpw))
cpw.addField(CtField.make("public static final double[] D0 = new double[] { %s };" % ", ".join(repr(float(_v)) for _c, _v in P25_STA_BASE), cpw))
cpw.addField(CtField.make("public static final double[] D1 = new double[] { %s };" % ", ".join(repr(float(_v)) for _c, _v in P25_STA_PER), cpw))
for _i, _st in enumerate(P25_BOOST_STATS):
    cpw.addField(CtField.make("public static final double[] D%d = new double[] { %s };" % (_i + 2, ", ".join("%d.0" % P25_BOOST[_c][_st] for _c, _v in P25_STA_BASE)), cpw))
for _d in ("public static volatile boolean STA_ON = true;", "public static volatile boolean B_ON = true;", "public static volatile Object[] T = null;",
           'public static volatile String WARNED = "";', "public static boolean FAILED_ONCE = false;"):
    cpw.addField(CtField.make(_d, cpw))
cpw.addMethod(CtNewMethod.make(J14(r"""
public static double[] defVals(int i) {
  if (i == 0) return D0;
  if (i == 1) return D1;
  if (i == 2) return D2;
  if (i == 3) return D3;
  if (i == 4) return D4;
  if (i == 5) return D5;
  if (i == 6) return D6;
  return D7;
}"""), cpw))
cpw.addMethod(CtNewMethod.make(J14(r"""
public static Object[] defaults() {
  Object[] a = new Object[PREFIX.length];
  for (int i = 0; i < a.length; i++) a[i] = @PKG@.OverallCfg.mkTable(DEF_CLS, defVals(i));
  return a;
}"""), cpw))
cpw.addMethod(CtNewMethod.make(J14(r"""
public static Object[] t(int i) {
  Object[] a = T;
  if (a == null) {
    a = defaults();
    T = a;
  }
  return (Object[]) a[i];
}"""), cpw))
cpw.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  STA_ON = @PKG@.SkillCfg.bool(p, "stamina.class.enabled", true);
  B_ON = @PKG@.SkillCfg.bool(p, "classBoost.enabled", true);
  Object[] a = new Object[PREFIX.length];
  StringBuilder w = new StringBuilder();
  for (int i = 0; i < a.length; i++) {
    Object[] r = @PKG@.ClassTbl.parse(p, PREFIX[i], MAX[i]);
    a[i] = new Object[] { r[0], r[1], r[2] };
    String bad = (String) r[3];
    if (bad.length() > 0) {
      if (w.length() > 0) w.append(" | ");
      w.append(LABEL[i]).append(": ").append(bad);
    }
  }
  T = a;
  String ws = w.toString();
  if (ws.length() > 0 && !ws.equals(WARNED)) @PKG@.SkillCfg.warn(ws);
  WARNED = ws;
}"""), cpw))
cpw.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  String st = (String) t(0)[2];
  return "class Stamina " + (STA_ON ? (st.length() > 0 ? st : "none listed") + " + per level" : "off") + ", class balance " + (B_ON ? "on" : "off");
}"""), cpw))
# ManaHit part 1: mana.onHit.<Class> (Mana a landed class weapon hit gives back), mana.onHitCooldownMs, mana.onHitVsPlayers
mhit.addField(CtField.make('public static final String TABLE_PREFIX = "mana.onHit.";', mhit))
mhit.addField(CtField.make("public static final String[] DEF_CLS = %s;" % jarr([_c for _c, _v in P25_HIT]), mhit))
mhit.addField(CtField.make("public static final double[] DEF_V = new double[] { %s };" % ", ".join("%s.0" % _v for _c, _v in P25_HIT), mhit))
for _d in ("public static volatile Object[] TBL = null;", "public static volatile long CD = %sL;" % P25_HIT_CD, "public static volatile boolean PVP = false;",
           'public static volatile String WARNED = "";', "public static boolean FAILED_ONCE = false;",
           "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap PEND = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.atomic.AtomicLong GIVEN = new java.util.concurrent.atomic.AtomicLong();"):
    mhit.addField(CtField.make(_d, mhit))
mhit.addMethod(CtNewMethod.make(J14(r"""
public static Object[] tbl() {
  Object[] t = TBL;
  if (t == null) {
    t = @PKG@.OverallCfg.mkTable(DEF_CLS, DEF_V);
    TBL = t;
  }
  return t;
}"""), mhit))
mhit.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  Object[] r = @PKG@.ClassTbl.parse(p, TABLE_PREFIX, 1000.0);
  TBL = new Object[] { r[0], r[1], r[2] };
  String w = ((String) r[3]).length() > 0 ? "Mana per class weapon hit: " + (String) r[3] : "";
  if (w.length() > 0 && !w.equals(WARNED)) @PKG@.SkillCfg.warn(w);
  WARNED = w;
  long cd = @PKG@.SkillCfg.lng(p, "mana.onHitCooldownMs", @P25_HIT_CD@L);
  CD = cd < 0L ? 0L : (cd > 60000L ? 60000L : cd);
  PVP = @PKG@.SkillCfg.bool(p, "mana.onHitVsPlayers", false);
}"""), mhit))
mhit.addMethod(CtNewMethod.make(J14(r"""
public static double perHit(String cls) {
  return @PKG@.ClassTbl.get(tbl(), cls);
}"""), mhit))
mhit.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  String t = (String) tbl()[2];
  return (t.length() > 0 ? t : "none listed") + " per hit, every " + CD + " ms" + (PVP ? ", also on players" : ", monsters only");
}"""), mhit))

'''
before("# ================= SkillLv (0.4.16): the levels.skill table - own XP-per-level lists per non-class skill (before SkillCfg.load) =================\n", CFG25)
# J14 needs P25_HIT_CD as a token value
rep('''  {PKG}.ClassMana.read(p);    // 0.4.15: max Mana per class level (the mana.classPerLevel table)
''', '''  {PKG}.ClassMana.read(p);    // 0.4.15: max Mana per class level (the mana.classPerLevel table)
    {PKG}.ClassPower.read(p);   // 0.4.25: class Stamina + the class balance tables
    {PKG}.ManaHit.read(p);      // 0.4.25: Mana on hit
''')
rep('''", own level lists " + {PKG}.SkillLv.text() + (bad > 0 ? ", " + bad + " bad line(s) skipped" : "");''',
    '''", own level lists " + {PKG}.SkillLv.text() + ", " + {PKG}.ClassPower.text() + ", Mana on hit " + {PKG}.ManaHit.text() + (bad > 0 ? ", " + bad + " bad line(s) skipped" : "");''')

# ================================================================================================ runtime (after ClassMana part 2)
RT25 = r'''# ================= 0.4.25 ClassPower part 2 / ManaHit part 2 / SkillDef: the per-player amounts (Perks, ManaRegen, CombatDmgSys, the damage systems) =================
# the class skill level of a class in the profile data d (0: no class, no data, a class without a class skill - Spellblade)
cpw.addMethod(CtNewMethod.make(J14(r"""
public static int classLevel(String cls, long[] d) {
  if (cls == null || d == null) return 0;
  int s = @PKG@.SkillClass.slotOfClass(cls);
  if (s < 0 || s >= @PKG@.SkillDefs.N || s >= d.length) return 0;
  return @PKG@.SkillDefs.levelOf(s, d[s]);
}"""), cpw))
# 0 at level 0 -> 1 at level 100 (a straight line; higher levels stay 1)
cpw.addMethod(CtNewMethod.make(J14(r"""
public static double frac(int lv) {
  if (lv <= 0) return 0.0;
  return lv >= 100 ? 1.0 : (double) lv / 100.0;
}"""), cpw))
# the class's max Stamina bonus at a class level: stamina.classBase + stamina.classPerLevel x level (0 while the switch is off)
cpw.addMethod(CtNewMethod.make(J14(r"""
public static float stamFor(String cls, int lv) {
  if (!STA_ON || cls == null) return 0.0f;
  double v = @PKG@.ClassTbl.get(t(0), cls) + @PKG@.ClassTbl.get(t(1), cls) * (double) (lv > 0 ? lv : 0);
  return v > 0.0 ? @PKG@.Overall.round2(v) : 0.0f;
}"""), cpw))
# class balance table i (2 Health, 3 Mana, 4 Stamina, 5 Defense, 6 damage %, 7 Mana regen %) at a class level
cpw.addMethod(CtNewMethod.make(J14(r"""
public static double boost(int i, String cls, int lv) {
  if (!B_ON || cls == null) return 0.0;
  double v = @PKG@.ClassTbl.get(t(i), cls);
  if (!(v > 0.0)) return 0.0;
  return v * frac(lv);
}"""), cpw))
# Perks.ovl (world thread): {class Stamina, balance Health, balance Mana, balance Stamina} for the ACTIVE profile's class (Overall.classOf: the
# ClassMana rule) and that class's own skill level; null = an error (Perks.ovl then leaves the saved modifiers alone - no dip)
cpw.addMethod(CtNewMethod.make(J14(r"""
public static float[] amounts(java.util.UUID u, long[] d) {
  try {
    String cls = @PKG@.Overall.classOf(u);
    int lv = classLevel(cls, d);
    return new float[] { stamFor(cls, lv), @PKG@.Overall.round2(boost(2, cls, lv)), @PKG@.Overall.round2(boost(3, cls, lv)), @PKG@.Overall.round2(boost(4, cls, lv)) };
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.SkillCfg.warn("class power amounts failed (logged once, the saved values are kept): " + t); }
    return null;
  }
}"""), cpw))
# the class balance Defense of the active profile's class (Perks.tick -> SkillDef)
cpw.addMethod(CtNewMethod.make(J14(r"""
public static double boostDef(java.util.UUID u, long[] d) {
  try {
    String cls = @PKG@.Overall.classOf(u);
    return boost(5, cls, classLevel(cls, d));
  } catch (Throwable t) { return 0.0; }
}"""), cpw))
# CombatDmgSys: the class balance damage as a fraction (0.05 = +5 %) for the class of this class skill slot at that level
cpw.addMethod(CtNewMethod.make(J14(r"""
public static double boostDmg(int slot, int lv) {
  if (!@PKG@.SkillDefs.isClass(slot)) return 0.0;
  int ci = @PKG@.SkillDefs.classIdx(slot);
  if (ci < 0 || ci >= @PKG@.SkillDefs.CLASSES.length) return 0.0;
  return boost(6, @PKG@.SkillDefs.CLASSES[ci], lv) / 100.0;
}"""), cpw))
# ManaRegen (any thread): the class balance Mana regen % - the ManaRegen.classPct way (SkillClass.slot, the profile data in memory, no file read)
cpw.addMethod(CtNewMethod.make(J14(r"""
public static double boostRegen(java.util.UUID u) {
  try {
    if (u == null || !B_ON) return 0.0;
    int s = @PKG@.SkillClass.slot(u);
    if (s < 0 || s >= @PKG@.SkillDefs.N) return 0.0;
    long[] d = (long[]) @PKG@.SkillStore.DATA.get(@PKG@.SkillStore.pkey(u));
    if (d == null || s >= d.length) return 0.0;
    return boost(7, @PKG@.SkillDefs.CLASSES[@PKG@.SkillDefs.classIdx(s)], @PKG@.SkillDefs.levelOf(s, @PKG@.SkillStore.rd(d, s)));
  } catch (Throwable t) { return 0.0; }
}"""), cpw))
# the class skill's Stats page: now "+24 max Mana (2 per level), +21 max Stamina (9 + 0.12 per level) - Archer"; next "+2 max Mana, +0.12 max
# Stamina"; null = nothing (not a class skill, both parts off / 0). Replaces 0.4.15's Mana-only line (ClassMana.statsLine) - one line for both.
cpw.addMethod(CtNewMethod.make(J14(r"""
public static String powerLine(int s, int lv, boolean next) {
  if (!@PKG@.SkillDefs.isClass(s)) return null;
  int ci = @PKG@.SkillDefs.classIdx(s);
  if (ci < 0 || ci >= @PKG@.SkillDefs.CLASSES.length) return null;
  String cls = @PKG@.SkillDefs.CLASSES[ci];
  double mper = @PKG@.OverallCfg.MANA_ON ? @PKG@.ClassMana.perLevel(cls) : 0.0;
  double sb = STA_ON ? @PKG@.ClassTbl.get(t(0), cls) : 0.0;
  double sper = STA_ON ? @PKG@.ClassTbl.get(t(1), cls) : 0.0;
  StringBuilder b = new StringBuilder();
  if (next) {
    if (mper > 0.0) b.append("+").append(@PKG@.Overall.num(mper)).append(" max Mana");
    if (sper > 0.0) { if (b.length() > 0) b.append(", "); b.append("+").append(@PKG@.Overall.num(sper)).append(" max Stamina"); }
    return b.length() > 0 ? b.toString() : null;
  }
  if (mper > 0.0 && lv > 0) b.append("+").append(@PKG@.Overall.num((double) @PKG@.Overall.round2(mper * (double) lv))).append(" max Mana (").append(@PKG@.Overall.num(mper)).append(" per level)");
  double st = (double) stamFor(cls, lv);
  if (st > 0.0) {
    if (b.length() > 0) b.append(", ");
    b.append("+").append(@PKG@.Overall.num(st)).append(" max Stamina (");
    if (sb > 0.0) b.append(@PKG@.Overall.num(sb)).append(sper > 0.0 ? " + " : "");
    if (sper > 0.0) b.append(@PKG@.Overall.num(sper)).append(" per level");
    b.append(")");
  }
  if (b.length() == 0) return null;
  return b.toString() + " - " + cls;
}"""), cpw))
# "Class balance: +6 Health, +7.5 Mana, +2.5 Stamina, +6.5 Defense, +1% damage, +7.5% Mana regen" (now only; null = off / level 0 / nothing)
cpw.addMethod(CtNewMethod.make(J14(r"""
public static String boostLine(int s, int lv, boolean next) {
  if (next || !B_ON || lv <= 0 || !@PKG@.SkillDefs.isClass(s)) return null;
  int ci = @PKG@.SkillDefs.classIdx(s);
  if (ci < 0 || ci >= @PKG@.SkillDefs.CLASSES.length) return null;
  String cls = @PKG@.SkillDefs.CLASSES[ci];
  String[] w = new String[] { " Health", " Mana", " Stamina", " Defense", "% damage", "% Mana regen" };
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < w.length; i++) {
    double v = (double) @PKG@.Overall.round2(boost(i + 2, cls, lv));
    if (!(v > 0.0)) continue;
    if (b.length() > 0) b.append(", ");
    b.append("+").append(@PKG@.Overall.num(v)).append(w[i]);
  }
  return b.length() == 0 ? null : "Class balance: " + b.toString();
}"""), cpw))
# ---- ManaHit part 2: a landed class weapon hit queues Mana (ManaHitSys, Inspect group); AcroSys adds it on the world thread
# pure: what may be added to cur of max (never above max, nothing at / over max, nothing for amt <= 0 or no Mana pool)
mhit.addMethod(CtNewMethod.make(J14(r"""
public static float grant(float cur, float max, float amt) {
  if (!(amt > 0.0f) || !(max > 0.0f) || !(cur < max)) return 0.0f;
  float room = max - cur;
  return amt < room ? amt : room;
}"""), mhit))
# a landed hit of player u (class cls; pvp = the target is a player) at now ms: the Mana it queues, 0 = none (no Mana for the class, a player
# target while mana.onHitVsPlayers is off, or inside the per-player cooldown). The damage dispatch thread = the world thread (one world per player).
mhit.addMethod(CtNewMethod.make(J14(r"""
public static float offer(java.util.UUID u, String cls, boolean pvp, long now) {
  if (u == null || cls == null) return 0.0f;
  if (pvp && !PVP) return 0.0f;
  double a = perHit(cls);
  if (!(a > 0.0)) return 0.0f;
  Object l = LAST.get(u);
  if (l instanceof Long) {
    long dt = now - ((Long) l).longValue();
    if (dt >= 0L && dt < CD) return 0.0f;
  }
  LAST.put(u, Long.valueOf(now));
  Object o = PEND.get(u);
  float cur = o instanceof Float ? ((Float) o).floatValue() : 0.0f;
  PEND.put(u, Float.valueOf(cur + (float) a));
  return (float) a;
}"""), mhit))
# the combat XP weapon rule (SkillClass.killSlot without its chat lines): SkyyClasses present, the profile's class in sync, a class skill, an
# allowed class weapon in the main hand / utility slot (SkillClass.weaponOk) -> offer
mhit.addMethod(CtNewMethod.make(J14(r"""
public static float hit(java.util.UUID u, boolean pvp, @CAC@ acc, @REF@ att, long now) {
  if (u == null) return 0.0f;
  if (pvp && !PVP) return 0.0f;
  int slot = @PKG@.SkillClass.slot(u);
  if (slot < 0 || !@PKG@.SkillDefs.isClass(slot) || !@PKG@.SkillClass.consistent(u)) return 0.0f;
  java.util.function.Function f = @PKG@.SkillClass.allowedFn();
  if (f == null) return 0.0f;
  String cls = @PKG@.SkillDefs.CLASSES[@PKG@.SkillDefs.classIdx(slot)];
  if (!(perHit(cls) > 0.0)) return 0.0f;
  if (!@PKG@.SkillClass.weaponOk(u, slot, f, acc, att)) return 0.0f;
  return offer(u, cls, pvp, now);
}"""), mhit))
# world thread (AcroSys.tick, every tick): the queued Mana goes in - never above max Mana, dropped while dead; returns what was added
mhit.addMethod(CtNewMethod.make(J14(r"""
public static float apply(java.util.UUID u, @CB@ cb, @REF@ ref) {
  if (u == null || PEND.isEmpty()) return 0.0f;
  Object o = PEND.remove(u);
  if (!(o instanceof Float)) return 0.0f;
  try {
    if (cb.getComponent(ref, @DTH@.getComponentType()) != null) return 0.0f;
    @ESM@ m = (@ESM@) cb.getComponent(ref, @ESM@.getComponentType());
    if (m == null) return 0.0f;
    int mi = @DST@.getMana();
    @ESV@ v = m.get(mi);
    if (v == null) return 0.0f;
    float g = grant(v.get(), v.getMax(), ((Float) o).floatValue());
    if (g > 0.0f) {
      m.addStatValue(mi, g);
      GIVEN.incrementAndGet();
    }
    return g;
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.SkillCfg.warn("Mana on hit failed (logged once): " + t); }
    return 0.0f;
  }
}"""), mhit))
mhit.addMethod(CtNewMethod.make(J14(r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  PEND.remove(u);
  LAST.remove(u);
}"""), mhit))
mhit.addMethod(CtNewMethod.make(J14(r"""
public static void retain(java.util.Set online) {
  PEND.keySet().retainAll(online);
  LAST.keySet().retainAll(online);
}"""), mhit))
# the Mana Regen source line (skill:fn:manaregen sources; no "=" so SkyyMenu shows it as it is): "Mana on hit +1 (class weapon, every 0.5 s)"
mhit.addMethod(CtNewMethod.make(J14(r"""
public static String sourceText(java.util.UUID u) {
  try {
    int s = @PKG@.SkillClass.slot(u);
    if (s < 0 || !@PKG@.SkillDefs.isClass(s)) return null;
    double a = perHit(@PKG@.SkillDefs.CLASSES[@PKG@.SkillDefs.classIdx(s)]);
    if (!(a > 0.0)) return null;
    return "Mana on hit +" + @PKG@.Overall.num(a) + " (class weapon, every " + @PKG@.Overall.num((double) CD / 1000.0) + " s)";
  } catch (Throwable t) { return null; }
}"""), mhit))
mhit.addMethod(CtNewMethod.make(J14(r"""
public static String statsLine(int s, boolean next) {
  if (next || !@PKG@.SkillDefs.isClass(s)) return null;
  String cls = @PKG@.SkillDefs.CLASSES[@PKG@.SkillDefs.classIdx(s)];
  double a = perHit(cls);
  if (!(a > 0.0)) return null;
  return "+" + @PKG@.Overall.num(a) + " Mana per hit with " + cls + " weapons (every " + @PKG@.Overall.num((double) CD / 1000.0) + " s" + (PVP ? ")" : ", monsters only)");
}"""), mhit))
# ---- SkillDef: the skill Defense (Foraging + every skill's perk.<skill>.defensePerLevel + the class balance Defense), applied with SkyyGear's
# formula summed with the gear Defense (tools/skills_0_4_25_patch.py point 2). DEF = UUID -> Double (Perks.tick, every second); bridge
# skill:def:<uuid> = the same Double (removed at 0 and when the player leaves). SkyyGear's scale + part.stats: config:fn:SkyyGear get, every 5 s.
for _d in ("public static final java.util.concurrent.ConcurrentHashMap DEF = new java.util.concurrent.ConcurrentHashMap();",
           "public static volatile boolean GON = true;", "public static volatile double GSC = 100.0;", "public static volatile long GAT = 0L;",
           "public static volatile boolean GFN = false;", "public static boolean FAILED_ONCE = false;"):
    sdef.addField(CtField.make(_d, sdef))
sdef.addMethod(CtNewMethod.make(J14(r"""
public static double of(java.util.UUID u) {
  Object o = u == null ? null : DEF.get(u);
  return o instanceof Double ? ((Double) o).doubleValue() : 0.0;
}"""), sdef))
sdef.addMethod(CtNewMethod.make(J14(r"""
public static void set(java.util.UUID u, double v) {
  if (u == null) return;
  double x = (Double.isNaN(v) || Double.isInfinite(v) || v < 0.0) ? 0.0 : (v > 100000.0 ? 100000.0 : v);
  x = (double) Math.round(x * 100.0) / 100.0;
  String k = "skill:def:" + u.toString();
  java.util.Map br = @PKG@.SkillStore.bridge();
  if (!(x > 0.0)) {
    DEF.remove(u);
    br.remove(k);
    return;
  }
  Double dv = Double.valueOf(x);
  DEF.put(u, dv);
  if (!dv.equals(br.get(k))) br.put(k, dv);
}"""), sdef))
# the def part of a SkyyGear stat text ("str:40,def:12,cc:5" - SkyyGear's parseExtra rules: whole numbers, each part and the sum within
# +-1,000,000, bad parts skipped); 0 = none
sdef.addMethod(CtNewMethod.make(J14(r"""
public static double defOf(Object o) {
  if (!(o instanceof String)) return 0.0;
  String[] ps = ((String) o).split(",");
  long acc = 0L;
  for (int i = 0; i < ps.length; i++) {
    String p = ps[i].trim();
    int c = p.indexOf(':');
    if (c <= 0 || !p.substring(0, c).trim().equals("def")) continue;
    try {
      double v = Double.parseDouble(p.substring(c + 1).trim());
      if (Double.isNaN(v) || Double.isInfinite(v)) continue;
      if (v > 1000000.0) v = 1000000.0;
      if (v < -1000000.0) v = -1000000.0;
      acc = acc + (long) Math.floor(v);
      if (acc > 1000000L) acc = 1000000L;
      if (acc < -1000000L) acc = -1000000L;
    } catch (Throwable t) { }
  }
  return (double) acc;
}"""), sdef))
# the gear Defense SkyyGear applies to this player: its own active armor (gear:stats:<uuid>) + the accessory part (gear:extra:<uuid>)
sdef.addMethod(CtNewMethod.make(J14(r"""
public static double gearDef(java.util.UUID u) {
  if (u == null) return 0.0;
  java.util.Map br = @PKG@.SkillStore.bridge();
  return defOf(br.get("gear:stats:" + u.toString())) + defOf(br.get("gear:extra:" + u.toString()));
}"""), sdef))
# SkyyGear's Defense curve (combat.defScale, 1-100000, default 100) and part switch (part.stats, default on) - read over its config op "get"
# every 5 s (any thread; the kit's get never throws, never calls another mod). Without SkyyGear: scale 100, no gear Defense.
sdef.addMethod(CtNewMethod.make(J14(r"""
public static void gearCfg(long now) {
  long at = GAT;
  if (at != 0L && now >= at && now - at < 5000L) return;
  GAT = now;
  try {
    Object f = @PKG@.SkillStore.bridge().get("config:fn:SkyyGear");
    if (!(f instanceof java.util.function.Function)) { GFN = false; GON = true; GSC = 100.0; return; }
    GFN = true;
    java.util.function.Function fn = (java.util.function.Function) f;
    Object ps = fn.apply(new Object[] { "get", "part.stats" });
    GON = !(ps instanceof String) || !((String) ps).trim().equalsIgnoreCase("false");
    Object sc = fn.apply(new Object[] { "get", "combat.defScale" });
    double v = 100.0;
    if (sc instanceof String) {
      try { v = Double.parseDouble(((String) sc).trim()); } catch (Throwable t) { v = 100.0; }
    }
    if (Double.isNaN(v) || v < 1.0) v = 100.0;
    if (v > 100000.0) v = 100000.0;
    GSC = v;
  } catch (Throwable t) {
    GON = true;
    GSC = 100.0;
  }
}"""), sdef))
# PURE: the extra damage factor for skill Defense s next to gear Defense g (SkyyGear: x scale / (scale + g) when its stats part is on and g > 0):
# target = scale / (scale + (on ? g : 0) + s) when that sum is above 0, applied = what SkyyGear did; factor = target / applied, kept in 0..1
sdef.addMethod(CtNewMethod.make(J14(r"""
public static double factor(double g, double s, double scale, boolean on) {
  if (!(s > 0.0) || !(scale > 0.0)) return 1.0;
  double gg = on ? g : 0.0;
  double applied = (on && g > 0.0) ? scale / (scale + g) : 1.0;
  double tot = gg + s;
  double target = tot > 0.0 ? scale / (scale + tot) : 1.0;
  double f = target / applied;
  if (Double.isNaN(f) || f > 1.0) return 1.0;
  return f < 0.0 ? 0.0 : f;
}"""), sdef))
# DefSys (Filter group, AFTER ArmorDamageReduction): a player victim u, damage from an entity source (SkyyGear's GearArmorSys rule) -> the
# amount x factor; returns the factor (1 = unchanged)
sdef.addMethod(CtNewMethod.make(J14(r"""
public static double reduce(@DMG@ d, java.util.UUID u, long now) {
  if (d == null || u == null || d.isCancelled()) return 1.0;
  if (!(d.getSource() instanceof @DES@)) return 1.0;
  double sk = of(u);
  if (!(sk > 0.0)) return 1.0;
  gearCfg(now);
  double f = factor(gearDef(u), sk, GSC, GON);
  if (f < 1.0) {
    float a = d.getAmount();
    if (a > 0.0f) d.setAmount((float) ((double) a * f));
  }
  return f;
}"""), sdef))
sdef.addMethod(CtNewMethod.make(J14(r"""
public static void retain(java.util.Set online) {
  java.util.Iterator it = new java.util.ArrayList(DEF.keySet()).iterator();
  java.util.Map br = @PKG@.SkillStore.bridge();
  while (it.hasNext()) {
    Object u = it.next();
    if (online.contains(u)) continue;
    DEF.remove(u);
    br.remove("skill:def:" + u.toString());
  }
}"""), sdef))
sdef.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  return "skill Defense (Foraging + class balance) with SkyyGear's Defense formula (scale " + @PKG@.Overall.num(GSC) + (GFN ? (GON ? ", summed with gear Defense)" : ", gear stats off)") : ", SkyyGear not read yet)");
}"""), sdef))

'''
before("# ================= skill:fn:overall (0.4.6, spec 4.8): apply(UUID) or apply(Object[]{UUID}) -> Object[]{Integer level, Integer averageTenths,\n", RT25)

# ================================================================================================ ClassMana.breakdown: + the class balance Mana
rep('''  float k = modAmt(m, mi, "skyyskill_mana");
  float rest = max - tm - b - c - o - k;''', '''  float k = modAmt(m, mi, "skyyskill_mana");
  float cb = modAmt(m, mi, "skyyskill_classboostmana");   // 0.4.25: the class balance Mana
  float rest = max - tm - b - c - o - k - cb;''')
rep('''  sb.append(" + skill perks ").append(@PKG@.Overall.num((double) k));
''', '''  sb.append(" + skill perks ").append(@PKG@.Overall.num((double) k));
  if (cb != 0.0f) sb.append(" + class balance ").append(@PKG@.Overall.num((double) cb));
''')

# ================================================================================================ Perks: modifiers + Defense + switch
rep('''    if (cmn >= 0.0f) mod(m, mi, "skyyskill_classmana", cmn);           // 0 = removed (no class level Mana); -1 = an error: the saved one stays
''', '''    if (cmn >= 0.0f) mod(m, mi, "skyyskill_classmana", cmn);           // 0 = removed (no class level Mana); -1 = an error: the saved one stays
    float[] cpw = {PKG}.ClassPower.amounts(u, {PKG}.SkillStore.data(u));   // 0.4.25: class Stamina + the class balance (null = an error: saved ones stay)
    if (cpw != null) {{
      int si = {DST}.getStamina();
      mod(m, si, "skyyskill_classstamina", cpw[0]);
      mod(m, hi, "skyyskill_classboosthp", cpw[1]);
      mod(m, mi, "skyyskill_classboostmana", cpw[2]);
      mod(m, si, "skyyskill_classbooststamina", cpw[3]);
    }}
''')
rep('''    int[] lv = levels(u);
    {PKG}.Brew.setBonus(u, lv[5]);
''', '''    int[] lv = levels(u);
    {PKG}.Brew.setBonus(u, lv[5]);
    {PKG}.SkillDef.set(u, (double) total({PKG}.PerkCfg.DEF, lv) + {PKG}.ClassPower.boostDef(u, {PKG}.SkillStore.data(u)));   // 0.4.25: skill Defense
''')
rep('''  {PKG}.Overall.forget(u);
}}""", perk))''', '''  {PKG}.Overall.forget(u);
  {PKG}.ManaHit.forget(u);   // 0.4.25: Mana on hit queued / timed for the old profile
}}""", perk))''')

# ================================================================================================ CombatDmgSys: + the class balance damage %
rep('''    if (!{PKG}.PerkCfg.ENABLED || {PKG}.PerkCfg.DMG <= 0.0) return;
    Object src = d.getSource();''', '''    if (!({PKG}.PerkCfg.ENABLED && {PKG}.PerkCfg.DMG > 0.0) && !{PKG}.ClassPower.B_ON) return;   // 0.4.25: or the class balance
    Object src = d.getSource();''')
rep('''    double bonus = {PKG}.Perks.damage({PKG}.SkillStore.level(u, slot));''',
    '''    int clv = {PKG}.SkillStore.level(u, slot);
    double bonus = {PKG}.Perks.damage(clv) + {PKG}.ClassPower.boostDmg(slot, clv);   // 0.4.25: + the class balance damage % (one multiplication)''')

# ================================================================================================ ManaRegen: class balance regen + Mana on hit source
rep('''  double sum = classPct(u);   // 0.4.17: + the class level perk (one more source, inside the same clamp)''',
    '''  double sum = classPct(u) + com.skyy.skills.ClassPower.boostRegen(u);   // 0.4.17: + the class level perk; 0.4.25: + the class balance regen (same clamp)''')
rep('''  double cp = classPct(u);   // 0.4.17: the class level perk is listed as "class level"
  if (!(o instanceof java.util.Map) && !(cp > 0.0)) return new String[0];
  java.util.TreeMap t = o instanceof java.util.Map ? new java.util.TreeMap((java.util.Map) o) : new java.util.TreeMap();
  if (cp > 0.0) t.put("class level", Double.valueOf(cp));
  String[] r = new String[t.size()];''', '''  double cp = classPct(u);   // 0.4.17: the class level perk is listed as "class level"
  double cbr = {PKG}.ClassPower.boostRegen(u);   // 0.4.25: the class balance regen = "class balance"
  String mh = u == null ? null : {PKG}.ManaHit.sourceText(u);   // 0.4.25: "Mana on hit +1 (...)" - a line without "=" (not a percent)
  if (!(o instanceof java.util.Map) && !(cp > 0.0) && !(cbr > 0.0) && mh == null) return new String[0];
  java.util.TreeMap t = o instanceof java.util.Map ? new java.util.TreeMap((java.util.Map) o) : new java.util.TreeMap();
  if (cp > 0.0) t.put("class level", Double.valueOf(cp));
  if (cbr > 0.0) t.put("class balance", Double.valueOf(cbr));
  String[] r = new String[t.size() + (mh != null ? 1 : 0)];
  if (mh != null) r[r.length - 1] = mh;''')
rep('''  while (it.hasNext() && i < r.length) {{
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    double v = ((Number) e.getValue()).doubleValue();''', '''  while (it.hasNext() && i < t.size()) {{
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    double v = ((Number) e.getValue()).doubleValue();''')

# ================================================================================================ AcroSys: the queued Mana on hit
rep('''    {PKG}.ManaRegen.tick(u, store, cb, ref, dt);   // 0.4.12: Mana regen in combat (own 0.2 s clock, own try; first, so no call below can skip it)
''', '''    {PKG}.ManaRegen.tick(u, store, cb, ref, dt);   // 0.4.12: Mana regen in combat (own 0.2 s clock, own try; first, so no call below can skip it)
    {PKG}.ManaHit.apply(u, cb, ref);   // 0.4.25: Mana on hit queued by ManaHitSys (own try; never above max Mana)
''')
rep('''    {PKG}.Sickle.retain(online);   // 0.4.14: the sickle swing contexts and this tick's pickups
''', '''    {PKG}.Sickle.retain(online);   // 0.4.14: the sickle swing contexts and this tick's pickups
    {PKG}.ManaHit.retain(online);  // 0.4.25: Mana on hit queue + cooldown
    {PKG}.SkillDef.retain(online); // 0.4.25: skill Defense + its skill:def:<uuid> bridge key
''')

# ================================================================================================ the two damage systems
SYS25 = r'''# ================= 0.4.25 DefSys / DefSysU / ManaHitSys =================
# DefSys: DamageEventSystem in the FILTER group, players only, AFTER the engine's DamageSystems$ArmorDamageReduction (SkyyGear's GearArmorSys
# place: both multiply after armor, so the order between them does not matter) -> SkillDef.reduce. DefSysU = the unordered fallback (one
# registerSystem per class; registered only when the ordered one could not be).
dsy.addField(CtField.make("public java.util.Set deps;", dsy))
dsy.addField(CtField.make("public static boolean FAILED_ONCE = false;", dsy))
dsy.addField(CtField.make('public static final String ADR = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction";', dsy))
dsy.addConstructor(CtNewConstructor.make(J14(r"""
public DefSys(boolean ordered) {
  super();
  if (ordered) this.deps = java.util.Collections.singleton(new @SDEP@(@DORD@.AFTER, Class.forName(ADR)));
  else this.deps = java.util.Collections.EMPTY_SET;
}"""), dsy))
dsy.addMethod(CtNewMethod.make(J14(r"""
public @QRY@ getQuery() {
  return (@QRY@) @PLA@.getComponentType();
}"""), dsy))
dsy.addMethod(CtNewMethod.make(J14(r"""
public @SYG@ getGroup() {
  return @DMM@.get().getFilterDamageGroup();
}"""), dsy))
dsy.addMethod(CtNewMethod.make(J14(r"""
public java.util.Set getDependencies() {
  return this.deps;
}"""), dsy))
dsy.addMethod(CtNewMethod.make(J14(r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@)) return;
    @DMG@ d = (@DMG@) ev;
    if (d.isCancelled()) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.SkillDef.reduce(d, pr.getUuid(), System.currentTimeMillis());
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.SkillCfg.warn("skill Defense failed (logged once): " + t); }
  }
}"""), dsy))
dsyu.addConstructor(CtNewConstructor.make("public DefSysU() { super(false); }", dsyu))
# ManaHitSys: DamageEventSystem in the INSPECT group (after ApplyDamage: the hit LANDED - not cancelled, amount above 0), any target; the
# attacker = the EntitySource's Ref (projectiles: their shooter) with a PlayerRef; a player target only with mana.onHitVsPlayers; never a
# stat write here (ManaHit queues, AcroSys adds)
mhs.addConstructor(CtNewConstructor.make("public ManaHitSys() { super(); }", mhs))
mhs.addField(CtField.make("public static boolean FAILED_ONCE = false;", mhs))
mhs.addMethod(CtNewMethod.make(J14(r"""
public @QRY@ getQuery() {
  return @QRY@.any();
}"""), mhs))
mhs.addMethod(CtNewMethod.make(J14(r"""
public @SYG@ getGroup() {
  return @DMM@.get().getInspectDamageGroup();
}"""), mhs))
mhs.addMethod(CtNewMethod.make(J14(r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@)) return;
    @DMG@ d = (@DMG@) ev;
    if (d.isCancelled() || !(d.getAmount() > 0.0f)) return;
    Object src = d.getSource();
    if (!(src instanceof @DES@)) return;
    @REF@ att = ((@DES@) src).getRef();
    if (att == null || !att.isValid()) return;
    @PR@ pr = (@PR@) buf.getComponent(att, @PR@.getComponentType());
    if (pr == null) return;
    @REF@ tr = chunk.getReferenceTo(idx);
    if (tr != null && tr.equals(att)) return;
    boolean pvp = tr != null && st.getComponent(tr, @PR@.getComponentType()) != null;
    @PKG@.ManaHit.hit(pr.getUuid(), pvp, buf, att, System.currentTimeMillis());
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.SkillCfg.warn("Mana on hit (damage check) failed (logged once): " + t); }
  }
}"""), mhs))

'''
before("# ================= PlacedStore: positions of player-placed blocks, per world =================\n", SYS25)

# ================================================================================================ the Stats page lines
rep('''  stat(out, {PKG}.PerkCfg.MANA[row], lv, next, "max Mana");
  String cmn = {PKG}.ClassMana.statsLine(s, lv, next);   // 0.4.15: max Mana per class level (Priest 5 per Divinity level, Mage 10 per Sorcery level)
  if (cmn != null) out.add(cmn);''', '''  stat(out, {PKG}.PerkCfg.MANA[row], lv, next, "max Mana");
  stat(out, {PKG}.PerkCfg.DEF[row], lv, next, "Defense (less damage taken)");   // 0.4.25: Foraging Defense
  String cmn = {PKG}.ClassPower.powerLine(s, lv, next);   // 0.4.25: class Mana + Stamina per level in ONE line (was 0.4.15's Mana-only ClassMana.statsLine)
  if (cmn != null) out.add(cmn);
  String cbl = {PKG}.ClassPower.boostLine(s, lv, next);   // 0.4.25: the class balance (now only)
  if (cbl != null) out.add(cbl);''')
rep('''    if (dm > 0.0) out.add("+" + pc(dm) + " damage with " + {PKG}.SkillDefs.CLASSES[{PKG}.SkillDefs.classIdx(s)] + " weapons" + ({PKG}.PerkCfg.DMG_PVP ? "" : " (against monsters)"));
  }}
''', '''    if (dm > 0.0) out.add("+" + pc(dm) + " damage with " + {PKG}.SkillDefs.CLASSES[{PKG}.SkillDefs.classIdx(s)] + " weapons" + ({PKG}.PerkCfg.DMG_PVP ? "" : " (against monsters)"));
  }}
  String mhl = {PKG}.ManaHit.statsLine(s, next);   // 0.4.25: Mana on hit
  if (mhl != null) out.add(mhl);
''')

# ================================================================================================ PerkMig (the one-time config update)
_RW = [("perk.mining.staminaPerLevel", "0.05", "0.2"), ("perk.foraging.healthPerLevel", "0.1", "0"), ("mana.base", "10", MANA_BASE_NEW),
       ("mana.classBase.Mage", "30", str(SPEC["Mage"][0])), ("mana.classBase.Priest", "30", str(SPEC["Priest"][0])), ("mana.regen.inCombat", "50", MREG_NEW)]
PMIG = r'''# ---- PerkMig (0.4.25, PROJECT-RULES section 4): ONCE on an EXISTING xp.properties, setup() after AcroMig.run, BEFORE SkillCfg.load and CfgPub.start.
# Nothing to do = no file (load() writes the 0.4.25 default) or a comment line holding MARK_ID (done before). Else, per logical line (the kit's own
# parser): each RW key whose LAST entry is a one-line entry holding the OLD default (numeric compare) -> every one-line entry of it holding that
# number gets the NEW one (value text only; key, separator, CR kept) + a config-changes.log line (Undo = the old value); any other value is kept
# (one INFO line). ONE block appended after the last line in the file's own line ending: the header (marker) + only the lines it lacks -
# perk.foraging.defensePerLevel (only when the file has perk.* lines; else load appends the whole 0.4.25 perk section), the missing
# mana.classBase classes (only with overall.enabled; else load appends the whole Overall section), the missing mana.classPerLevel classes (only
# when the file has such a line - an emptied table stays empty), every missing class Stamina / Mana on hit / class balance line; a table entry
# counts as present in any spelling of its class. Change-log lines (Undo) for the rewritten values and the added Mana / Defense lines.
# Properties check (only the planned keys differ), config-history copy first, the kit's atomicWrite. A failure = WARN, file untouched, retried.
pmig.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(P25_MARK_ID), pmig))
pmig.addField(CtField.make("public static final String HEAD = " + P25_HEAD_LIT + ";", pmig))
_PRW = @@RW@@
pmig.addField(CtField.make("public static final String[] RW_KEY = %s;" % jarr([_k for _k, _o, _n in _PRW]), pmig))
pmig.addField(CtField.make("public static final String[] RW_OLD = %s;" % jarr([_o for _k, _o, _n in _PRW]), pmig))
pmig.addField(CtField.make("public static final String[] RW_NEW = %s;" % jarr([_n for _k, _o, _n in _PRW]), pmig))
assert all(("\n" + _k + "=" + _n + "\n") in ("\n" + DEFAULTS) for _k, _o, _n in _PRW), "a rewrite's new value is not the default file's"
# the lines an old file may lack: key, value, family prefix ("" = a plain key), class, group (0 always, 1 needs a perk.* key, 2 needs
# overall.enabled, 3 needs a mana.classPerLevel. key), change-log key ("" = none) and its Undo value
_PADD = [("perk.foraging.defensePerLevel", "0.2", "", "", 1, "perk.foraging.defensePerLevel", "0")]
_PADD += [("mana.classBase.%s" % _c, str(_v), "mana.classBase.", _c, 2, "mana.classBase[%s]" % _c, "(none)") for _c, _v in CLASS_BASE_DEF]
_PADD += [("mana.classPerLevel.%s" % _c, str(_v), "mana.classPerLevel.", _c, 3, "mana.classPerLevel[%s]" % _c, "(none)") for _c, _v in CLASS_MANA_DEF]
for _ln in P25_LINES:
    _k, _v = _ln.split("=", 1)
    _pre = next((_p for _p in ["stamina.classBase.", "stamina.classPerLevel.", "mana.onHit."] + ["classBoost.%s." % _st for _st in P25_BOOST_STATS] if _k.startswith(_p)), "")
    _PADD.append((_k, _v, _pre, _k[len(_pre):] if _pre else "", 0, "", ""))
assert len(set(_a[0] for _a in _PADD)) == len(_PADD) and all(_cre.match(r"^[A-Za-z][A-Za-z0-9._-]*$", _a[0]) for _a in _PADD)
assert all(("\n" + _a[0] + "=" + _a[1] + "\n") in ("\n" + DEFAULTS) for _a in _PADD), "an added line is not the default file's"
for _nm, _ix in (("ADD_KEY", 0), ("ADD_VAL", 1), ("ADD_PRE", 2), ("ADD_CLS", 3), ("ADD_LOG", 5), ("ADD_OLD", 6)):
    pmig.addField(CtField.make("public static final String[] %s = %s;" % (_nm, jarr([_a[_ix] for _a in _PADD])), pmig))
pmig.addField(CtField.make("public static final int[] ADD_GRP = new int[] { %s };" % ", ".join(str(_a[4]) for _a in _PADD), pmig))
pmig.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.25";', pmig))
pmig.addMethod(CtNewMethod.make(J14(r"""
public static boolean numEq(String a, String b) {
  if (a == null || b == null) return false;
  try {
    double x = Double.parseDouble(a.trim());
    double y = Double.parseDouble(b.trim());
    return !Double.isNaN(x) && !Double.isInfinite(x) && Math.abs(x - y) < 1.0E-9;
  } catch (Throwable t) { return false; }
}"""), pmig))
pmig.addMethod(CtNewMethod.make(J14(r"""
public static int rwIdx(String key) {
  if (key == null) return -1;
  for (int i = 0; i < RW_KEY.length; i++) if (RW_KEY[i].equals(key)) return i;
  return -1;
}"""), pmig))
pmig.addMethod(CtNewMethod.make(J14(r"""
public static boolean hasPrefix(java.util.Properties p, String pre) {
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) if (((String) it.next()).startsWith(pre)) return true;
  return false;
}"""), pmig))
pmig.addMethod(CtNewMethod.make(J14(r"""
public static boolean present(java.util.Properties p, int j) {
  if (p.getProperty(ADD_KEY[j]) != null) return true;
  if (ADD_PRE[j].length() == 0) return false;
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith(ADD_PRE[j])) continue;
    String c = @PKG@.OverallCfg.canonClass(k.substring(ADD_PRE[j].length()).trim());
    if (c != null && c.equalsIgnoreCase(ADD_CLS[j])) return true;
  }
  return false;
}"""), pmig))
pmig.addMethod(CtNewMethod.make(J14(r"""
public static boolean groupOk(java.util.Properties p, int g) {
  if (g == 1) return hasPrefix(p, "perk.");
  if (g == 2) return p.getProperty("overall.enabled") != null;
  if (g == 3) return hasPrefix(p, "mana.classPerLevel.");
  return true;
}"""), pmig))
# pure text step (ISO-8859-1 chars in and out). null = nothing to do (the marker is in a comment line, or the text cannot be read as
# Properties); else { new text, String[] { key, old, new }* (the change-log rows), boolean[] rewritten, boolean[] added, String kept notes }.
pmig.addMethod(CtNewMethod.make(J14(r"""
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
  int n = RW_KEY.length;
  String[] eff = new String[n];
  boolean[] multi = new boolean[n];
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    int ri = rwIdx(@PKG@.CfgFile.key(s));
    if (ri >= 0) { eff[ri] = @PKG@.CfgFile.value(l, k).trim(); multi[ri] = e > k; }
    k = e + 1;
  }
  boolean[] rw = new boolean[n];
  StringBuilder kept = new StringBuilder();
  for (int i = 0; i < n; i++) {
    rw[i] = eff[i] != null && !multi[i] && numEq(eff[i], RW_OLD[i]);
    if (eff[i] != null && !rw[i] && !numEq(eff[i], RW_NEW[i])) {
      if (kept.length() > 0) kept.append("; ");
      kept.append(RW_KEY[i]).append("=").append(@PKG@.CfgRows.oneLine(eff[i])).append(" kept (an admin's value; the 0.4.25 default is ").append(RW_NEW[i]).append(")");
    }
  }
  boolean[] add = new boolean[ADD_KEY.length];
  for (int j = 0; j < add.length; j++) add[j] = groupOk(p, ADD_GRP[j]) && !present(p, j);
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  StringBuilder sb = new StringBuilder(text.length() + 4096);
  k = 0;
  boolean first = true;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) {
      if (!first) sb.append('\n');
      sb.append(raw[k]);
      first = false;
      k++;
      continue;
    }
    int e2 = @PKG@.CfgFile.end(l, k);
    int r2 = rwIdx(@PKG@.CfgFile.key(s2));
    if (r2 >= 0 && rw[r2] && e2 == k && numEq(@PKG@.CfgFile.value(l, k), RW_OLD[r2])) {
      if (!first) sb.append('\n');
      sb.append(s2.substring(0, @PKG@.CfgFile.valStart(s2))).append(RW_NEW[r2]).append(raw[k].endsWith("\r") ? "\r" : "");
      first = false;
    } else {
      for (int q = k; q <= e2; q++) {
        if (!first) sb.append('\n');
        sb.append(raw[q]);
        first = false;
      }
    }
    k = e2 + 1;
  }
  String body = sb.toString();
  StringBuilder blk = new StringBuilder(HEAD);
  for (int j = 0; j < add.length; j++) if (add[j]) blk.append(ADD_KEY[j]).append('=').append(ADD_VAL[j]).append('\n');
  String nl = cr + "\n";
  String b = blk.toString();
  if (cr.length() > 0) b = b.replace("\n", "\r\n");
  String pre = (body.length() == 0 || body.endsWith("\n")) ? nl : nl + nl;
  String last = body.endsWith("\n") ? body.substring(0, body.length() - 1) : body;
  if (last.endsWith("\r")) last = last.substring(0, last.length() - 1);
  int bs = 0;
  for (int i = last.length() - 1; i >= 0 && last.charAt(i) == '\\'; i--) bs++;
  if (bs % 2 == 1 && body.endsWith("\n")) pre = pre + nl;
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < n; i++) if (rw[i]) { rows.add(RW_KEY[i]); rows.add(@PKG@.CfgRows.oneLine(eff[i])); rows.add(RW_NEW[i]); }
  for (int j = 0; j < add.length; j++) if (add[j] && ADD_LOG[j].length() > 0) { rows.add(ADD_LOG[j]); rows.add(ADD_OLD[j]); rows.add(ADD_VAL[j]); }
  return new Object[] { body + pre + b, (String[]) rows.toArray(new String[0]), rw, add, kept.toString() };
}"""), pmig))
# only the planned keys differ: every old key keeps its value except a rewritten one (exactly its new value), the added keys are new and hold
# exactly their value, nothing else is new
pmig.addMethod(CtNewMethod.make(J14(r"""
public static boolean sameAfter(byte[] old, byte[] nb, boolean[] rw, boolean[] add) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties n = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    n.load(new java.io.ByteArrayInputStream(nb));
    int na = 0;
    for (int j = 0; j < add.length; j++) if (add[j]) na++;
    if (n.size() != a.size() + na) return false;
    java.util.Iterator it = a.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      String want = a.getProperty(k);
      int i = rwIdx(k);
      if (i >= 0 && rw[i]) want = RW_NEW[i];
      String got = n.getProperty(k);
      if (got == null || !got.equals(want)) return false;
    }
    for (int j = 0; j < add.length; j++) {
      if (!add[j]) continue;
      if (a.getProperty(ADD_KEY[j]) != null || !ADD_VAL[j].equals(n.getProperty(ADD_KEY[j]))) return false;
    }
    return true;
  } catch (Throwable t) { return false; }
}"""), pmig))
pmig.addMethod(CtNewMethod.make(J14(r"""
public static String logLine(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}"""), pmig))
pmig.addMethod(CtNewMethod.make(J14(r"""
public static synchronized String run() {
  java.nio.file.Path f = @PKG@.SkillCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = plan(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    boolean[] rw = (boolean[]) r[2];
    boolean[] add = (boolean[]) r[3];
    if (!sameAfter(old, data, rw, add)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.25 (class power split): the update would change another setting (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = @PKG@.HealMig.fileIdx();
    if (fi < 0) return "";
    @PKG@.HealMig.mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, "before the 0.4.25 class power split update");
    if (!@PKG@.HealMig.mgSaved(fi, old)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.25 (class power split): the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[1];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(logLine(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    StringBuilder what = new StringBuilder();
    for (int i = 0; i < rw.length; i++) {
      if (!rw[i]) continue;
      if (what.length() > 0) what.append(", ");
      what.append(RW_KEY[i]).append(" ").append(RW_OLD[i]).append(" -> ").append(RW_NEW[i]);
    }
    int na = 0;
    for (int j = 0; j < add.length; j++) if (add[j]) na++;
    String msg = "xp.properties updated for 0.4.25 (class power split): " + (what.length() > 0 ? what.toString() : "no default changed") + "; " + na + " line(s) added (Foraging Defense, the missing Base Mana / Mana per level classes, class Stamina, Mana on hit, class balance) - the old file is in config-history, Server Setup -> Changes can undo each changed value";
    @PKG@.SkillCfg.info(msg);
    String kept = (String) r[4];
    if (kept.length() > 0) {
      @PKG@.SkillCfg.info("xp.properties 0.4.25: " + kept);
      return msg + "\n" + kept;
    }
    return msg;
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("could not update xp.properties for 0.4.25 (class power split; the file is used as it is): " + t);
    return "";
  }
}"""), pmig))

'''.replace("@@RW@@", repr(_RW))
before("# ---- ManaGuard (point 3): WARN once per class whose base Mana is below the Mana cost of a weapon in its class kit. Scheduler thread\n", PMIG)

# ================================================================================================ config rows
rep('''CFG_CATS = [("parts", "Parts"), ("general", "General"), ("levels", "Levels"), ("gathering", "Gathering"), ("combat", "Combat"),
            ("acrobatics", "Acrobatics"), ("perks", "Perks"), ("overall", "Overall and Mana"), ("crafting", "Crafting")]''',
    '''CFG_CATS = [("parts", "Parts"), ("general", "General"), ("levels", "Levels"), ("gathering", "Gathering"), ("combat", "Combat"),
            ("acrobatics", "Acrobatics"), ("perks", "Perks"), ("overall", "Overall and Mana"), ("power", "Class Power"), ("crafting", "Crafting")]   # 0.4.25: + Class Power''')
rep('''_PDEF = {"healthPerLevel": ["0", "0.1", "0.25", "0.1", "0", "0", "0", "0", "0"],
         "staminaPerLevel": ["0.05", "0", "0", "0", "0", "0", "0", "0", EXPL_STA_DEF],
         "manaPerLevel": ["0", "0", "0", "0", "0", "0.2", "0", "0", "0"]}
_PWORD = {"healthPerLevel": "health", "staminaPerLevel": "stamina", "manaPerLevel": "mana"}''',
    '''_PDEF = {"healthPerLevel": ["0", "0", "0.25", "0.1", "0", "0", "0", "0", "0"],          # 0.4.25: Foraging 0 (Defense instead)
         "staminaPerLevel": ["0.2", "0", "0", "0", "0", "0", "0", "0", EXPL_STA_DEF],     # 0.4.25: Mining 0.2
         "manaPerLevel": ["0", "0", "0", "0", "0", "0.2", "0", "0", "0"],
         "defensePerLevel": ["0", "0.2", "0", "0", "0", "0", "0", "0", "0"]}             # 0.4.25: Foraging Defense
_PWORD = {"healthPerLevel": "health", "staminaPerLevel": "stamina", "manaPerLevel": "mana", "defensePerLevel": "Defense"}''')
rep('''    for _st in ("healthPerLevel", "staminaPerLevel", "manaPerLevel"):
        _key = "perk.%s.%s" % (_k, _st)
        _d = _PDEF[_st][_i]
        _in = ("\\n" + _key + "=") in ("\\n" + DEFAULTS)
        _help = "Max %s added per %s level (all skills add up)." % (_PWORD[_st], _who)''',
    '''    for _st in ("healthPerLevel", "staminaPerLevel", "manaPerLevel", "defensePerLevel"):   # 0.4.25: + Defense
        _key = "perk.%s.%s" % (_k, _st)
        _d = _PDEF[_st][_i]
        _in = ("\\n" + _key + "=") in ("\\n" + DEFAULTS)
        _help = "Max %s added per %s level (all skills add up)." % (_PWORD[_st], _who)
        if _st == "defensePerLevel":
            _help = "Defense per %s level (all skills add up; hits x 100 / (100 + Defense), like gear)." % _who''')
rep('''        CFG_ROWS.append((_key, "%s: max %s per level" % (_lab, _PWORD[_st]), "perks", "dec", _d, "0", "10", "", "", "live" if _in else "live,adv",
                         _help, "reload"))''',
    '''        CFG_ROWS.append((_key, ("%s: Defense per level" % _lab) if _st == "defensePerLevel" else "%s: max %s per level" % (_lab, _PWORD[_st]),
                         "perks", "dec", _d, "0", "10", "", "", "live" if _in else "live,adv", _help, "reload"))''')
rep('''    ("mana.base", "Base Mana for everyone", "overall", "dec", "10", "0", "10000", "", "", "live",
     "Max Mana every player starts with, unless Base Mana by class lists their class (vanilla gives 0).", "reload"),''',
    '''    ("mana.base", "Base Mana for everyone", "overall", "dec", "%s", "0", "10000", "", "", "live",
     "Max Mana every player starts with, unless Base Mana by class lists their class (vanilla gives 0).", "reload"),''' % MANA_BASE_NEW)
rep('''     "Max Mana a listed class starts with, instead of the base above (Mage 30 = 3 staff casts).", "reload;check=OverallCfg.checkClassBase"),''',
    '''     "Max Mana a listed class starts with, instead of the base above (Mage 45 ... Berserker 12).", "reload;check=OverallCfg.checkClassBase"),''')
rep('''     "Max Mana a listed class gains per level of its own class skill (Priest: Divinity, Mage: Sorcery).", "reload;check=ClassMana.checkEntry"),''',
    '''     "Max Mana a listed class gains per level of its own class skill (Mage 10, Priest 5, fighters 2).", "reload;check=ClassMana.checkEntry"),''')
rep('''    ("mana.regen.show", "Mana Regen: show mine", "overall", "action", "", "", "", "Show my Mana Regen", "", "live",
     "Your Mana Regen boosts (other mods register them, none yet) and the refill in and out of combat.",
     "action:ManaRegen.showAction"),
]''', '''    ("mana.regen.show", "Mana Regen: show mine", "overall", "action", "", "", "", "Show my Mana Regen", "", "live",
     "Your Mana Regen boosts (other mods register them, none yet) and the refill in and out of combat.",
     "action:ManaRegen.showAction"),
]
# 0.4.25 (research/Class-Power-Split.md, Skyy 2026-10-08): the "Class Power" category - class Stamina, Mana on hit, the class balance
CFG_ROWS += [
    ("stamina.class.enabled", "Class Stamina", "power", "bool", "true", "", "", "", "", "live",
     "On: each class gets its max Stamina bonus and Stamina per class level from the two tables below.", "reload"),
    ("stamina.classBase", "Max Stamina by class", "power", "table", "", "0", "1000", "dec;type;Stamina", "", "live",
     "Max Stamina a listed class gets on top of vanilla's 10 (Berserker 12, Mage 4).", "reload;check=ClassTbl.checkEntry"),
    ("stamina.classPerLevel", "Max Stamina per class level", "power", "table", "", "0", "100", "dec;type;Stamina per level", "", "live",
     "Max Stamina a listed class gains per level of its own class skill (Warrior 0.13 = +13 at 100).", "reload;check=ClassTbl.checkEntry"),
    ("mana.onHit", "Mana per class weapon hit", "power", "table", "", "0", "1000", "dec;type;Mana", "", "live",
     "Mana a landed hit with your class weapon gives back (fighters and Archer 1, casters 0).", "reload;check=ClassTbl.checkEntry"),
    ("mana.onHitCooldownMs", "Mana on hit: wait between", "power", "int", P25_HIT_CD, "0", "60000", "", "ms", "live",
     "At most one Mana-on-hit per player in this many milliseconds (500 = twice a second).", "reload"),
    ("mana.onHitVsPlayers", "Mana on hit vs players", "power", "bool", "false", "", "", "", "", "live,danger",
     "On: hits on players also give Mana back (off = monsters only).", "reload;confirm=on"),
    ("classBoost.enabled", "Class balance boost", "power", "bool", "true", "", "", "", "", "live",
     "On: the class skill adds a little to every stat, more to the class's weak ones (tables below).", "reload"),
    ("classBoost.health", "Class balance: Health at 100", "power", "table", "", "0", "1000", "dec;type;Health", "", "live",
     "Max Health the class skill adds at level 100 (0 at level 0, a straight line between).", "reload;check=ClassTbl.checkEntry"),
    ("classBoost.mana", "Class balance: Mana at 100", "power", "table", "", "0", "1000", "dec;type;Mana", "", "live",
     "Max Mana the class skill adds at level 100 (0 at level 0, a straight line between).", "reload;check=ClassTbl.checkEntry"),
    ("classBoost.stamina", "Class balance: Stamina at 100", "power", "table", "", "0", "1000", "dec;type;Stamina", "", "live",
     "Max Stamina the class skill adds at level 100 (0 at level 0, a straight line between).", "reload;check=ClassTbl.checkEntry"),
    ("classBoost.defense", "Class balance: Defense at 100", "power", "table", "", "0", "1000", "dec;type;Defense", "", "live",
     "Defense the class skill adds at level 100 (hits x 100 / (100 + Defense), with gear Defense).", "reload;check=ClassTbl.checkEntry"),
    ("classBoost.damage", "Class balance: damage at 100", "power", "table", "", "0", "100", "dec;type;Damage %", "", "live",
     "Percent more class weapon damage vs monsters at level 100 (on top of the class damage perk).", "reload;check=ClassTbl.checkEntry"),
    ("classBoost.regen", "Class balance: Mana regen at 100", "power", "table", "", "0", "1000", "dec;type;Mana regen %", "", "live",
     "Percent more Mana regen at level 100 (one more Mana Regen source, in and out of combat).", "reload;check=ClassTbl.checkEntry"),
]''')
rep('''                 ("levels.skill", "levels.skill."), ("combat.levelCurve", "combat.levelCurve.")):   # 0.4.16: + the own level lists; 0.4.17: + the kill XP level curve''',
    '''                 ("levels.skill", "levels.skill."), ("combat.levelCurve", "combat.levelCurve."),   # 0.4.16: + the own level lists; 0.4.17: + the kill XP level curve
                 ("stamina.classBase", "stamina.classBase."), ("stamina.classPerLevel", "stamina.classPerLevel."), ("mana.onHit", "mana.onHit."),   # 0.4.25
                 ("classBoost.health", "classBoost.health."), ("classBoost.mana", "classBoost.mana."), ("classBoost.stamina", "classBoost.stamina."),
                 ("classBoost.defense", "classBoost.defense."), ("classBoost.damage", "classBoost.damage."), ("classBoost.regen", "classBoost.regen.")):''')
rep('''assert len(_absent) == 21, _absent''', '''assert len(_absent) == 29, _absent   # 0.4.25: + 8 zero defensePerLevel rows''')
rep('''assert len(CFG_ROWS) == 205, (''', '''assert len(CFG_ROWS) == 227, (''')
rep('''"fromLevel; 0.4.18: + the read-only acro.roll; 0.4.19: + acro.dodgeMinMove; 0.4.20: + acro.dodgeTap / acro.dodgeTapMs, got %d" % len(CFG_ROWS))''',
    '''"fromLevel; 0.4.18: + the read-only acro.roll; 0.4.19: + acro.dodgeMinMove; 0.4.20: + acro.dodgeTap / acro.dodgeTapMs; 0.4.25: + 9 "
                              "perk.<skill>.defensePerLevel + the 13 Class Power rows, got %d" % len(CFG_ROWS))''')
rep('''assert DEFAULTS.endswith("\\n" + SKL_DEFAULTS + "\\n" + KXP_DEFAULTS)   # 0.4.17: the KXP block follows the 0.4.16 block
''', '''assert DEFAULTS.endswith("\\n" + SKL_DEFAULTS + "\\n" + KXP_DEFAULTS + "\\n" + P25_DEFAULTS)   # 0.4.17: the KXP block follows the 0.4.16 block; 0.4.25: + P25
# 0.4.25: every Class Power row once, its scalar defaults = the P25 block; the table defaults = P25 lines; the defense rows; the new defaults
_k25 = [_r[0] for _r in CFG_ROWS]
for _k, _d in (("stamina.class.enabled", "true"), ("mana.onHitCooldownMs", P25_HIT_CD), ("mana.onHitVsPlayers", "false"), ("classBoost.enabled", "true")):
    assert _k25.count(_k) == 1 and _dp.get(_k) == _d == [_r for _r in CFG_ROWS if _r[0] == _k][0][4] and ("\\n%s=%s\\n" % (_k, _d)) in ("\\n" + P25_DEFAULTS), _k
assert [_r[0] for _r in CFG_ROWS if _r[2] == "power"] == ["stamina.class.enabled", "stamina.classBase", "stamina.classPerLevel", "mana.onHit",
                                                         "mana.onHitCooldownMs", "mana.onHitVsPlayers", "classBoost.enabled"] + ["classBoost." + _st for _st in P25_BOOST_STATS]
assert all(_dp.get("stamina.classBase." + _c) == _v for _c, _v in P25_STA_BASE) and all(_dp.get("stamina.classPerLevel." + _c) == _v for _c, _v in P25_STA_PER)
assert all(_dp.get("mana.onHit." + _c) == _v for _c, _v in P25_HIT)
assert all(_dp.get("classBoost.%s.%s" % (_st, _c)) == str(P25_BOOST[_c][_st]) for _st in P25_BOOST_STATS for _c, _v in P25_STA_BASE)
assert _dp.get("perk.mining.staminaPerLevel") == "0.2" and _dp.get("perk.foraging.healthPerLevel") == "0" and _dp.get("perk.foraging.defensePerLevel") == "0.2"
assert _dp.get("mana.base") == "@@MB@@" and _dp.get("mana.regen.inCombat") == "@@MR@@" and _k25.count("perk.foraging.defensePerLevel") == 1
'''.replace("@@MB@@", MANA_BASE_NEW).replace("@@MR@@", MREG_NEW))
rep('''                  ("SKL", SKL_DEFAULTS)):   # 0.4.16''', '''                  ("SKL", SKL_DEFAULTS), ("P25", P25_DEFAULTS)):   # 0.4.16; 0.4.25: + P25''')

# ================================================================================================ classes + plugin
rep('''amg  = pool.makeClass(PKG + ".AcroMig")
''', '''amg  = pool.makeClass(PKG + ".AcroMig")
# 0.4.25: the class power split (config readers, per-player amounts), skill Defense, Mana on hit, their two damage systems, the one-time update
ctb  = pool.makeClass(PKG + ".ClassTbl")
cpw  = pool.makeClass(PKG + ".ClassPower")
mhit = pool.makeClass(PKG + ".ManaHit")
sdef = pool.makeClass(PKG + ".SkillDef")
dsy  = pool.makeClass(PKG + ".DefSys", pool.get(DEVS))
dsyu = pool.makeClass(PKG + ".DefSysU", dsy)
mhs  = pool.makeClass(PKG + ".ManaHitSys", pool.get(DEVS))
pmig = pool.makeClass(PKG + ".PerkMig")
''')
rep('''          kxm, amg):   # 0.4.19: + AcroMig;''', '''          kxm, amg,
          ctb, cpw, mhit, sdef, dsy, dsyu, mhs, pmig):   # 0.4.25: + ClassTbl, ClassPower, ManaHit, SkillDef, DefSys, DefSysU, ManaHitSys, PerkMig; 0.4.19: + AcroMig;''')
after("  {PKG}.AcroMig.run();        // 0.4.19: untouched acro.maxXpPerMinute 240 -> 0 + acro.dodgeMinMove into an existing xp.properties, once; History first\n",
      "  {PKG}.PerkMig.run();        // 0.4.25: the class power split - untouched old defaults rewritten + missing lines added, once; History first\n")
rep('''  try {{
    getEntityStoreRegistry().registerSystem(new {PKG}.RollSys());   // 0.4.14: roll landings, BEFORE the engine's FallDamagePlayers
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("could not register RollSys (roll landings): " + t + " - rolled landings pay as before until the next restart");
  }}
''', '''  try {{
    getEntityStoreRegistry().registerSystem(new {PKG}.RollSys());   // 0.4.14: roll landings, BEFORE the engine's FallDamagePlayers
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("could not register RollSys (roll landings): " + t + " - rolled landings pay as before until the next restart");
  }}
  try {{
    getEntityStoreRegistry().registerSystem(new {PKG}.DefSys(true));   // 0.4.25: skill Defense, AFTER ArmorDamageReduction (SkyyGear's Defense place)
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("could not order DefSys after ArmorDamageReduction (" + t + ") - unordered fallback: skill Defense still applies");
    try {{ getEntityStoreRegistry().registerSystem(new {PKG}.DefSysU()); }} catch (Throwable t2) {{ {PKG}.SkillCfg.warn("could not register DefSysU - no skill Defense this start: " + t2); }}
  }}
  try {{
    getEntityStoreRegistry().registerSystem(new {PKG}.ManaHitSys());   // 0.4.25: Mana on hit (Inspect group: hits that landed)
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("could not register ManaHitSys - no Mana on hit this start: " + t);
  }}
''')
rep('''"; own level lists " + {PKG}.SkillLv.text() + (ownc.length() > 0 ? " (" + ownc + ")" : "")''',
    '''"; own level lists " + {PKG}.SkillLv.text() + (ownc.length() > 0 ? " (" + ownc + ")" : "") + "; " + {PKG}.ClassPower.text() + "; Mana on hit " + {PKG}.ManaHit.text() + "; " + {PKG}.SkillDef.text()''')
rep('''Mages and Priests can cast their starter weapons from level 1 (Base Mana 10, Mage and Priest 30 - Base Mana by class in Server Setup)''',
    '''every class gets its own share of Mana and Stamina (the class power split: Base Mana 25 without a class, Mage 45 ... Berserker 12, max Stamina by class + per class level - Server Setup: Class Power)''')
rep('''Mana refills in combat at 50% (Server Setup: In-combat Mana regen; vanilla stops it for 6 s after a hit)''',
    '''Mana refills in combat at 75% (Server Setup: In-combat Mana regen; vanilla stops it for 6 s after a hit) and class weapon hits on monsters give Mana back (fighters and Archers +1, every 0.5 s)''')
rep('''Priests gain +5 max Mana per Divinity level and Mages +10 per Sorcery level (Server Setup: Max Mana per class level)''',
    '''Priests gain +5 max Mana per Divinity level, Mages +10 per Sorcery level and the fighters +2 (Server Setup: Max Mana per class level); the class skill also adds a little to every stat, more to the class's weak ones (class balance); Mining adds max Stamina and Foraging Defense (SkyyGear's Defense formula)''')

# ================================================================================================ checks + write
assert s.count("registerSystem(") == REG0 + 3 and s.count("registerCommand(") == CMD0, "systems: 0.4.25 adds DefSys / DefSysU / ManaHitSys; no command"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
_ix = lambda t: s.index(t)
# methods before callers (javassist compiles each method body when it is added)
assert _ix("public static Object[] parse(java.util.Properties p, String prefix, double max)") < _ix("Object[] r = @PKG@.ClassTbl.parse(p, PREFIX[i], MAX[i]);")
assert _ix("public static double get(Object[] t, String cls)") < _ix("public static double perHit(String cls)")
assert _ix("public static Object[] defaults()") < _ix("public static Object[] t(int i)") < _ix("public static void read(java.util.Properties p) {\n  STA_ON")
assert _ix("public static double[] defVals(int i)") < _ix("public static Object[] defaults()")
assert _ix("public static void read(java.util.Properties p) {\n  STA_ON") < _ix("    {PKG}.ClassPower.read(p);   // 0.4.25")
assert _ix("public static void read(java.util.Properties p) {\n  Object[] r = @PKG@.ClassTbl.parse(p, TABLE_PREFIX, 1000.0);") < _ix("    {PKG}.ManaHit.read(p);      // 0.4.25")
assert _ix("public static String canonClass(String t) {{") < _ix("public static Object[] parse(java.util.Properties p, String prefix, double max)")
assert _ix("public static Object[] mkTable(String[] c, double[] b) {{") < _ix("public static Object[] parse(java.util.Properties p, String prefix, double max)")
assert _ix("public static int classLevel(String cls, long[] d)") < _ix("public static float[] amounts(java.util.UUID u, long[] d)")
assert _ix("public static double frac(int lv)") < _ix("public static double boost(int i, String cls, int lv)") < _ix("public static float[] amounts(java.util.UUID u, long[] d)")
assert _ix("public static float stamFor(String cls, int lv)") < _ix("public static float[] amounts(java.util.UUID u, long[] d)") < _ix("public static String powerLine(int s, int lv, boolean next)")
assert _ix("public static String classOf(") < _ix("public static float[] amounts(java.util.UUID u, long[] d)")
assert _ix("public static float round2(double v)") < _ix("public static float stamFor(String cls, int lv)")
assert _ix("public static double perLevel(String cls)") < _ix("public static String powerLine(int s, int lv, boolean next)")
assert _ix("public static float grant(float cur, float max, float amt)") < _ix("public static float apply(java.util.UUID u, @CB@ cb, @REF@ ref)")
assert _ix("public static float offer(java.util.UUID u, String cls, boolean pvp, long now)") < _ix("public static float hit(java.util.UUID u, boolean pvp, @CAC@ acc, @REF@ att, long now)")
assert _ix("public static boolean weaponOk(java.util.UUID u, int slot, java.util.function.Function f, {CAC} acc, {REF} att) {{") < _ix("public static float hit(java.util.UUID u, boolean pvp, @CAC@ acc, @REF@ att, long now)")
assert _ix("public static double defOf(Object o)") < _ix("public static double gearDef(java.util.UUID u)") < _ix("public static double reduce(@DMG@ d, java.util.UUID u, long now)")
assert _ix("public static void gearCfg(long now)") < _ix("public static double reduce(@DMG@ d, java.util.UUID u, long now)")
assert _ix("public static double factor(double g, double s, double scale, boolean on)") < _ix("public static double reduce(@DMG@ d, java.util.UUID u, long now)")
assert _ix("public static void set(java.util.UUID u, double v)") < _ix("    {PKG}.SkillDef.set(u, (double) total(")
assert _ix("public static float[] amounts(java.util.UUID u, long[] d)") < _ix("    float[] cpw = {PKG}.ClassPower.amounts(")
assert _ix("public static double boostDmg(int slot, int lv)") < _ix("double bonus = {PKG}.Perks.damage(clv) + {PKG}.ClassPower.boostDmg(slot, clv);")
assert _ix("public static double boostRegen(java.util.UUID u)") < _ix("double sum = classPct(u) + com.skyy.skills.ClassPower.boostRegen(u);")
assert _ix("public static String sourceText(java.util.UUID u)") < _ix("String mh = u == null ? null : {PKG}.ManaHit.sourceText(u);")
assert _ix("public static float apply(java.util.UUID u, @CB@ cb, @REF@ ref)") < _ix("    {PKG}.ManaHit.apply(u, cb, ref);   // 0.4.25")
assert _ix("public static void retain(java.util.Set online) {\n  PEND.keySet()") < _ix("    {PKG}.ManaHit.retain(online);")
assert _ix("public static void retain(java.util.Set online) {\n  java.util.Iterator it = new java.util.ArrayList(DEF.keySet())") < _ix("    {PKG}.SkillDef.retain(online);")
assert _ix("public static void forget(java.util.UUID u) {\n  if (u == null) return;\n  PEND.remove(u);") < _ix("  {PKG}.ManaHit.forget(u);   // 0.4.25")
assert _ix("public static double reduce(@DMG@ d, java.util.UUID u, long now)") < _ix("    @PKG@.SkillDef.reduce(d, pr.getUuid(), System.currentTimeMillis());")
assert _ix("public static float hit(java.util.UUID u, boolean pvp, @CAC@ acc, @REF@ att, long now)") < _ix("    @PKG@.ManaHit.hit(pr.getUuid(), pvp, buf, att, System.currentTimeMillis());")
assert _ix("public DefSys(boolean ordered) {") < _ix('dsyu.addConstructor(CtNewConstructor.make("public DefSysU() { super(false); }", dsyu))')
assert _ix("public static String powerLine(int s, int lv, boolean next)") < _ix("String cmn = {PKG}.ClassPower.powerLine(s, lv, next);")
assert _ix("public static String boostLine(int s, int lv, boolean next)") < _ix("String cbl = {PKG}.ClassPower.boostLine(s, lv, next);")
assert _ix("public static String statsLine(int s, boolean next)") < _ix("String mhl = {PKG}.ManaHit.statsLine(s, next);")
assert _ix("public static String text() {\n  String st = (String) t(0)[2];") < _ix("{PKG}.ClassPower.text() + \", Mana on hit \"")
assert _ix("public static String text() {\n  return \"skill Defense") < _ix("{PKG}.SkillDef.text()")
assert _ix("public static Object[] plan(String text) {\n  if (text == null) return null;\n  java.util.Properties p = new java.util.Properties();\n  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { return null; }\n  String[] raw = text.split(\"\\n\", -1);\n  java.util.ArrayList l = new java.util.ArrayList();\n  for (int i = 0; i < raw.length; i++) {\n    String s0 = raw[i];\n    if (s0.endsWith(\"\\r\")) s0 = s0.substring(0, s0.length() - 1);\n    l.add(s0);\n  }\n  int n = RW_KEY.length;") < _ix('pmig.addMethod(CtNewMethod.make(J14(r"""\npublic static boolean sameAfter(byte[] old, byte[] nb, boolean[] rw, boolean[] add)')
assert s.index("{PKG}.AcroMig.run();") < s.index("{PKG}.PerkMig.run();") < s.index("String rules = {PKG}.SkillCfg.load();")
for _c in ("ctb", "cpw", "mhit", "sdef", "dsy", "dsyu", "mhs", "pmig"):
    assert s.index('%s = pool.makeClass(' % _c.ljust(4)) < s.index("%s.add" % _c), _c
assert s.index('dsy  = pool.makeClass(PKG + ".DefSys", pool.get(DEVS))') > s.index('DEVS= "com.hypixel.hytale.server.core.modules.entity.damage.DamageEventSystem"')
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed]
assert not _bad, "0.4.24 lines changed outside the planned places: %r" % _bad[:5]
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.24,", len(_gone), "0.4.24 lines replaced,",
      sum(op[4] - op[3] for op in _hunks) - len(_gone), "lines added net;", len(OLDS), "anchors")
print("class balance at level 100 (Health / Mana / Stamina / Defense / damage % / regen %):")
for _c in CLS:
    print("  %-10s %s" % (_c, " / ".join(str(BOOST[_c][_st]) for _st in BOOST_STATS)))
