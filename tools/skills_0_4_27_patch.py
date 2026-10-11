"""Derive SkyySkills/build_skyyskills_0.4.27.py from the LIVE generated SkyySkills/build_skyyskills_0.4.26.py (= the tools/deploy_set.py SET
pin; 0.4.26 came from 0.4.25 by tools/skills_0_4_26_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_26_patch.py: rep(old, new) with asserted single anchors, newline-agnostic; 0.4.26
stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_27_patch.py   then   python SkyySkills/build_skyyskills_0.4.27.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.27.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch, deleted)

0.4.27 = THE MONK SKILL IS "ZEN" (Skyy LOCKED 2026-10-08, docs/answered/classes.md popup batch 1: 'MONK skill name "Zen" (rename from
Discipline - small 3-mod rebuild: SkyyClasses + SkyySkills + SkyyProfiles / Menu where named)'; research/classes/Monk.md "LOCKED Zen").
DISPLAY TEXT ONLY - every saved key stays:
  - the Monk's storage slot 8 keeps its saved key Combat.Shaman (players/<pkey>.properties never change; SkillBonus keys = NAMES, not
    labels: xp.combat.shaman / dd.* unchanged); only its LABEL "Discipline" -> "Zen" (SkillDefs.LABELS = /skills rows, the Stats page,
    the skill:<uuid> level string, level-up chat, leaderboards).
  - "discipline" becomes an ALIAS of the Monk slot (SkillDefs.ALIAS_FROM / aliasIdx / indexOf): /skills discipline, /skills top
    discipline, /xp ... discipline and EVERY bridge caller that still says "Discipline" (skill:fn:level from SkyyTrees 0.3.4,
    SkyyMobs / SkyyGear passing SkyyClasses 0.1.14's class:skill "Discipline") keep resolving to the Monk slot. "Zen" itself is the label
    (exact match; prefixes of 3+ letters as before - no other label starts with "zen").
  - help / usage / manifest texts name Zen.
  No config key, no saved data, no migration, no new class / system / command. Rolling back to 0.4.26 is safe (labels only).
PAIRING: deploy WITH SkyyClasses 0.1.15 (class:skill = "Zen"): SkyyMobs / SkyyGear pass class:skill to skill:fn:level, and 0.4.26 does
not know "Zen" (STOP rule for tools/deploy_set.py: SkyyClasses 0.1.15+ needs SkyySkills 0.4.27+). 0.4.27 with SkyyClasses 0.1.14 works
(alias) - only SkyyHud's class line would show "-" (it looks the class:skill name up in the skill:<uuid> labels) until Classes moves too.
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.26.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.27.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.26"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.26"' in s and "derived from the generated 0.4.25 by tools/skills_0_4_26_patch.py" in s, "not the live generated 0.4.26"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert '"Zen"' not in s and '("discipline", "Monk")' not in s, "0.4.26 already has the Zen rename"
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
rep('''"""SkyySkills 0.4.26 - build script (derived from the generated 0.4.25 by tools/skills_0_4_26_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.27 - build script (derived from the generated 0.4.26 by tools/skills_0_4_27_patch.py - edit the patch, not this file;
0.4.26 was derived from the generated 0.4.25 by tools/skills_0_4_26_patch.py; ''')
rep('''0.4.26: TOOL FORTUNE + skill:dmg (Skyy 2026-10-05 / 2026-10-09 "tools still dont have chopping speed, and foraging fortune"; full notes in
''', '''0.4.27: THE MONK SKILL IS "ZEN" (Skyy LOCKED 2026-10-08; full notes in tools/skills_0_4_27_patch.py). Display text only: slot 8's label
  "Discipline" -> "Zen" (saved key Combat.Shaman KEPT, no data / config / bonus key changes); "discipline" is an alias of the Monk slot
  (commands + every bridge caller that still says Discipline). Deploy WITH SkyyClasses 0.1.15 (its class:skill says "Zen"; 0.4.26 cannot
  resolve that name). No migration, no new class / system / command. CHECKED: SkyySkills/test_skyyskills_0.4.27.py (-Xverify:all).
0.4.26: TOOL FORTUNE + skill:dmg (Skyy 2026-10-05 / 2026-10-09 "tools still dont have chopping speed, and foraging fortune"; full notes in
''')
rep('VERSION = "0.4.26"', 'VERSION = "0.4.27"')

# ---------------------------------------------------------------------------------------------------------------- the label + the alias
rep('''              ("Monk", "Discipline", "Weapon_Staff_Bo_Wood", "#f08a30"),   # 0.4.21: the Shaman slot (saved key Combat.Shaman KEPT)
''', '''              ("Monk", "Zen", "Weapon_Staff_Bo_Wood", "#f08a30"),   # 0.4.21: the Shaman slot (saved key Combat.Shaman KEPT); 0.4.27: Discipline -> Zen
''')
rep('''SKILL_ALIASES = [("shaman", "Monk"), ("shamans", "Monk"), ("shaman skill", "Monk")]
''', '''SKILL_ALIASES = [("shaman", "Monk"), ("shamans", "Monk"), ("shaman skill", "Monk")]
# 0.4.27 (Skyy LOCKED 2026-10-08 "Zen"): the old label of the Monk slot - commands and bridge callers that still say Discipline
SKILL_ALIASES += [("discipline", "Monk")]
''')
rep('''assert SLOT_LABELS[14:] == ["Fury", "Divinity"] and SLOT_LABELS[8] == "Discipline" and SLOT_NAMES[8] == "Combat.Shaman"   # 0.4.21: renamed, key kept
''', '''assert SLOT_LABELS[14:] == ["Fury", "Divinity"] and SLOT_LABELS[8] == "Zen" and SLOT_NAMES[8] == "Combat.Shaman"   # 0.4.21: renamed, key kept; 0.4.27 Zen
assert not [l for l in SLOT_LABELS if l.lower() != "zen" and l.lower().startswith("zen")], "0.4.27: 'zen' must be a unique label prefix"
''')

# 0.4.27 fixer 2 (critic: "/skills dis | disc | discip opened the Monk page in 0.4.26, 'unknown skill' in 0.4.27"): a 3+ letter prefix
# of the OLD label still resolves to the Monk slot, checked AFTER every label / class prefix (so nothing that resolved in 0.4.26 changes)
rep('''    for (int i = 0; i < CLASSES.length; i++) if (CLASSES[i].toLowerCase().startsWith(t)) return classSlot(i);
  }
  return -1;
}""", defs))''', '''    for (int i = 0; i < CLASSES.length; i++) if (CLASSES[i].toLowerCase().startsWith(t)) return classSlot(i);
    if ("discipline".startsWith(t)) return classSlot(aliasIdx("discipline"));
  }
  return -1;
}""", defs))''')

# ---------------------------------------------------------------------------------------------------------------- texts
rep('''sorcery, fury, divinity, assassination, discipline. /skills stats also opens overall."));''',
    '''sorcery, fury, divinity, assassination, zen. /skills stats also opens overall."));''')
rep('''Priest Divinity / Assassin Assassination / Monk Discipline";''', '''Priest Divinity / Assassin Assassination / Monk Zen";''')
rep('''| sorcery | fury | divinity | assassination | discipline", {ATY}.STRING);''', '''| sorcery | fury | divinity | assassination | zen", {ATY}.STRING);''', 2)
rep('''| sorcery | fury | divinity | assassination | discipline | overall (the Overall Level page)", {ATY}.STRING);''',
    '''| sorcery | fury | divinity | assassination | zen | overall (the Overall Level page)", {ATY}.STRING);''')
rep('''(SkyyClasses: Archery, Swordsmanship, Sorcery, Fury, Divinity, Assassination, Discipline) to level 100.''',
    '''(SkyyClasses: Archery, Swordsmanship, Sorcery, Fury, Divinity, Assassination, Zen) to level 100.''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "0.4.27 adds no system and no command"
_code = LF.join(ln.split("#")[0] if ln.lstrip().startswith("#") or "   # " in ln else ln
                for ln in s[s.index('VERSION = "0.4.27"'):].split(LF))
assert "discipline" not in _code.replace('("discipline", "Monk")', "").replace('if ("discipline".startsWith(t)) return classSlot(aliasIdx("discipline"));', "").lower(), "0.4.27: a Discipline text is left in the code"
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed]
assert not _bad, "0.4.26 lines changed outside the planned places: %r" % _bad[:5]
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.26,", len(_gone), "0.4.26 lines replaced,",
      sum(op[4] - op[3] for op in _hunks) - len(_gone), "lines added net;", len(OLDS), "anchors")
