"""Derive SkyyMenu/build_skyymenu_0.3.9.py from the LIVE SkyyMenu 0.3.8 (python tools/menu_0_3_9_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: 0.3 -> menu_0_3_1_patch.py -> ... -> menu_0_3_8_patch.py -> 0.3.8 (= the
tools/deploy_set.py SET pin, generated - never re-run its patch, never re-build it) -> this patch -> 0.3.9. 0.3.8's files stay untouched.

0.3.9 = CLASS TEXTS ONLY (no behaviour change) for the Assassin + Monk round (Skyy LOCKED 2026-10-07 "1. make the classes"; review fix of
the SkyyClasses 0.1.14 round, critic 3 point 1): deploys TOGETHER with SkyyClasses 0.1.14, SkyySkills 0.4.21 and SkyyProfiles 0.1.6.
  1. The class roster every class text names: CLASS_PLAYABLE = all seven (Assassin + Monk playable), CLASS_LATER = none, CLASS_SKILLS +
     Assassination + Discipline (the Monk skill name is OPEN for Skyy - Monk-Kit-Spec 4 default). The build's "later" check follows
     CLASS_LATER (an empty CLASS_LATER = no Mods text may say a class comes later).
  2. Texts: the SkyyClasses Mods entry (was "... or Priest (the party healer) - Assassin and Shaman later"), the SkyyProfiles entry (the
     class list), the SkyySkills entry (the class skills; "Hypixel-style" and "as you play" dropped to stay inside the 390-character tooltip limit) and the
     main menu Skills tile (the class skills).
  3. ROUND_PINS = this round (SkyyClasses 0.1.13 -> 0.1.14, SkyySkills 0.4.20 -> 0.4.21, SkyyProfiles 0.1.5 -> 0.1.6); MODS_VERSIONS names
     those three versions. NOT a version catch-up: every other MODS_VERSIONS entry stays 0.3.8's (the Mods list was already behind SET -
     Hud, Sacks, Collections, Bank, Bazaar, Gear, Accessories, Mobs, Armory - and SET's three probe mods are not in MODS; that is a later
     text-only round, the live-set check keeps printing those WARNINGs exactly as it does for 0.3.8).
NOT CHANGED: every class but MenuData's data (the harness byte-compares), SET_KNOWN, the menu look, the config kit pin.
Every change below is recorded (CHANGES) and undone at the end to prove the generated script is 0.3.8 outside them, byte for byte.
"""
import os
import re
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.8.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.9.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.8"' in s and "0.3.8: DATA / TEXT ONLY" in s, "not the generated 0.3.8 script"
assert "@@" not in s, "0.3.8 already holds a @@ token"
CHANGES = []            # (new text, old text) of every change, in order: undone at the end


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


# THIS ROUND: the mods that deploy together with this SkyyMenu (mod: (the SET version now, the round's version))
ROUND = {"SkyyClasses": ("0.1.13", "0.1.14"), "SkyySkills": ("0.4.20", "0.4.21"), "SkyyProfiles": ("0.1.5", "0.1.6")}
_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
for _m, (_frm, _to) in ROUND.items():
    if _set is not None and _set.get(_m) != _frm:
        print("NOTE: tools/deploy_set.py SET pins %s %s, this round replaces %s" % (_m, _set.get(_m), _frm))

# ================================================================================================ docstring + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.8: DATA / TEXT ONLY''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.9: CLASS TEXTS ONLY (no behaviour change; notes: tools/menu_0_3_9_patch.py): Assassin + Monk are playable (SkyyClasses 0.1.14,
       SkyySkills 0.4.21 Discipline, SkyyProfiles 0.1.6 - ROUND_PINS, deploy together): CLASS_PLAYABLE = all seven, CLASS_LATER = none,
       CLASS_SKILLS + Assassination + Discipline; the Classes / Profiles / Skills Mods texts + the main menu Skills tile name them. Every
       other Mods version stays 0.3.8's (a version catch-up is a later round).
  CHECKED: see SkyyMenu/test_skyymenu_0.3.9.py (every 0.3.8 check carried forward + F4 the 0.3.9 class texts + K4 0.3.8 -> 0.3.9 data only).
0.3.8: DATA / TEXT ONLY''')
rep('VERSION = "0.3.8"', 'VERSION = "0.3.9"')
rep('"set EXPECTED_KIT through tools/menu_0_3_8_patch.py (or its successor), regenerate, re-test"',
    '"set EXPECTED_KIT through tools/menu_0_3_9_patch.py (or its successor), regenerate, re-test"')

# ================================================================================================ MODS_VERSIONS: the round's three versions
for _m, (_frm, _to) in sorted(ROUND.items()):
    _old = re.findall(r'"%s": "([0-9.]+)"' % _m, s[s.index("MODS_VERSIONS = {"):s.index("MODS = [")])
    assert len(_old) == 1, (_m, _old)
    rep('"%s": "%s",' % (_m, _old[0]), '"%s": "%s",' % (_m, _to))

# ================================================================================================ the class roster
rep('''CLASS_PLAYABLE = ["Archer", "Warrior", "Mage", "Berserker", "Priest"]
CLASS_LATER    = ["Assassin", "Shaman"]
CLASS_SKILLS   = ["Archery", "Swordsmanship", "Sorcery", "Fury", "Divinity"]      # the weapon skill of each CLASS_PLAYABLE class''',
    '''# 0.3.9: SkyyClasses 0.1.14 - Assassin + Monk playable (the Shaman slot is the Monk; its skill name Discipline is OPEN for Skyy)
CLASS_PLAYABLE = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk"]
CLASS_LATER    = []
CLASS_SKILLS   = ["Archery", "Swordsmanship", "Sorcery", "Fury", "Divinity", "Assassination", "Discipline"]      # the weapon skill of each CLASS_PLAYABLE class''')
rep('''assert "later" in _bym["SkyyClasses"]["desc"], "SkyyClasses desc must say which classes come later"''',
    '''# 0.3.9: "later" only while CLASS_LATER names a class (all seven are playable since SkyyClasses 0.1.14)
assert ("later" in _bym["SkyyClasses"]["desc"]) == bool(CLASS_LATER), "SkyyClasses desc says 'later' exactly when a class comes later"
assert "Shaman" not in " ".join(m["desc"] for m in MODS) + " ".join(" ".join(e[4]) for e in ENTRIES), "0.3.9: no Mods / menu text names the Shaman"''')

# ================================================================================================ texts
rep('''     "desc": "Classes: Archer, Warrior, Mage, Berserker or Priest (the party healer) - Assassin and Shaman later. Each class''',
    '''     # 0.3.9: SkyyClasses 0.1.14 - Assassin + Monk playable
     "desc": "Classes: Archer, Warrior, Mage, Berserker, Priest (the party healer), Assassin or Monk. Each class''')
rep('''each profile is its own save with its own class (Archer, Warrior, Mage, Berserker or Priest), island''',
    '''each profile is its own save with its own class (Archer, Warrior, Mage, Berserker, Priest, Assassin or Monk), island''')
rep('''     "desc": "Hypixel-style skills - Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration and your class weapon skill (Archery, Swordsmanship, Sorcery, Fury or Divinity, on its own XP curve) - level up as you play and pay coins.''',
    '''     # 0.3.9: SkyySkills 0.4.21 - Assassination + Discipline ("Hypixel-style" + "as you play" dropped: the 390-character tooltip limit)
     "desc": "Skills - Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration and your class weapon skill (Archery, Swordsmanship, Sorcery, Fury, Divinity, Assassination or Discipline, on its own XP curve) - level up and pay coins.''')
rep('''        ["Your skill levels and XP: gathering, your class weapon skill (Archery, Swordsmanship, Sorcery, Fury or Divinity) and more. "''',
    '''        ["Your skill levels and XP: gathering, your class weapon skill (Archery, Swordsmanship, Sorcery, Fury, Divinity, Assassination "
         "or Discipline) and more. "''')

# ================================================================================================ ROUND_PINS: this round
rep('''ROUND_PINS = {'SkyyTrees': ('0.3.1', '0.3.2')}''',
    '''# 0.3.9: deploys WITH SkyyClasses 0.1.14 + SkyySkills 0.4.21 + SkyyProfiles 0.1.6 (Assassin + Monk; tools/menu_0_3_9_patch.py ROUND).
# 0.3.8's round (SkyyTrees 0.3.2) is pinned in SET now.
ROUND_PINS = %s''' % repr(dict((m, ROUND[m]) for m in sorted(ROUND))))

# ================================================================================================ build checks: 0.3.9 texts
rep('''# 0.3.8: the texts of Gear 0.2.3, Skills 0.4.16, Party 0.1.7 / Essentials 0.1.8, Bazaar 0.1.4 and Trees 0.3 - 0.3.2''',
    '''# 0.3.9: the class texts of SkyyClasses 0.1.14 / SkyySkills 0.4.21 / SkyyProfiles 0.1.6 (Assassin + Monk playable)
assert "Assassin or Monk" in _bym["SkyyClasses"]["desc"] and "Assassin or Monk" in _bym["SkyyProfiles"]["desc"], "0.3.9: Assassin + Monk named"
assert "Assassination or Discipline" in _bym["SkyySkills"]["desc"] and len(_bym["SkyySkills"]["desc"]) <= 390, "0.3.9: the Skills text"
# 0.3.8: the texts of Gear 0.2.3, Skills 0.4.16, Party 0.1.7 / Essentials 0.1.8, Bazaar 0.1.4 and Trees 0.3 - 0.3.2''')

# ================================================================================================ live-set check: patch name
rep('_PATCH = "tools/menu_0_3_8_patch.py"', '_PATCH = "tools/menu_0_3_9_patch.py"')

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
_mv = s[s.index("MODS_VERSIONS = {"):s.index("MODS = [")]
assert all(_mv.count('"%s": "%s",' % (m, to)) == 1 for m, (frm, to) in ROUND.items()), "the round's versions in MODS_VERSIONS"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.8 outside the recorded changes"
compile(s, dst, "exec")
out = s.replace(LF, NL) if NL != LF else s
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.8 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
