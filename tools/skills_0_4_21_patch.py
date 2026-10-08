"""Derive SkyySkills/build_skyyskills_0.4.21.py from the LIVE generated SkyySkills/build_skyyskills_0.4.20.py (= the tools/deploy_set.py SET
pin; 0.4.20 came from 0.4.19 by tools/skills_0_4_20_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_20_patch.py: rep(old, new) with asserted single anchors, newline-agnostic; 0.4.20
stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_21_patch.py   then   python SkyySkills/build_skyyskills_0.4.21.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.21.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/classes014/, deleted afterwards)

0.4.21 = THE MONK + ASSASSIN CLASS SKILLS (Skyy LOCKED 2026-10-07 "1. make the classes"; research/cloud/Monk-Kit-Spec.md 4 + 8.4: "the
Shaman placeholder skill slot 8 - rename, not a new slot"). Deploy TOGETHER with SkyyClasses 0.1.14 (the Monk class), SkyyProfiles 0.1.6.
(1) THE CLASS ROW: SkillDefs.CLASSES[3] "Shaman" -> "Monk", label (LABELS[8]) "Shaman skill" -> "Discipline" (Monk-Kit-Spec 4 default -
    OPEN for Skyy), icon Weapon_Staff_Bo_Wood, colour #f08a30 (gear.md LOCKED 2026-10-06). THE SAVED KEY STAYS: storage slot 8 keeps
    NAMES[8] = "Combat.Shaman" (players/<pkey>.properties lines Combat.Shaman / Combat.Shaman.paid) - no data file is rewritten, no XP
    can be lost or doubled. Assassination (slot 7, Combat.Assassin) already exists and had no "not playable" gate in SkySkills (XP
    follows SkyyClasses' class:<uuid> + class:fn:allowed + class:weapons:<Class>, which SkyyClasses 0.1.14 opens).
(2) THE OLD NAME IS AN ALIAS (read side only): SkillDefs.ALIAS_FROM {"shaman", "shamans", "shaman skill"} -> the Monk. SkillDefs.indexOf
    (every skill-name lookup: /skills top|stats <skill>, skill:fn:xp / skill:fn:level from other mods - SkyyGuilds' default xpSkills
    list still says "Shaman"), SkillDefs.canonName (class names: SkillClass.slotOfClass, SkillClass.consistent - a SkyyProfiles that still
    publishes profile:class = Shaman matches SkyyClasses' class:<uuid> = Monk, no pause) and OverallCfg.canonClass (the mana.classBase /
    mana.classPerLevel table keys: a "Shaman" line counts for the Monk).
(3) SkillClass.weaponsText: "Weapon_Staff_Bo_" reads "Bo" and a word already listed is not repeated (the Monk's
    Weapon_Staff_Bo_,Weapon_Fist_,Weapon_Bo_ = "Bo / Fist", not "Staff Bo / Fist / Bo").
(4) Texts: the unknown-class / unknown-skill lines, the /skills skill argument help, the Combat row's how-to line and the built-in kit
    table (ManaGuard's fallback: Monk = Weapon_Staff_Bo_Wood:1). The xp.properties COMMENT lines that still say "the Shaman skill" are
    left as they are (the class-XP / curve blocks are appended to old files by marker - changing their text would re-append them).
NOT in this build: no migration, no new row / key / system / command / asset, no change to any saved key.
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.20.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.21.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.20"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.20"' in s and "derived from the generated 0.4.19 by tools/skills_0_4_20_patch.py" in s, "not the live generated 0.4.20"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "ALIAS_FROM" not in s and '"Monk"' not in s, "0.4.20 already knows the Monk"
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


def block(a, b):
    assert s.count(a) == 1 and s.count(b) == 1 and s.index(a) < s.index(b), (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


# blocks that must stay byte-identical (0.4.20 code this build does not touch)
KEEP = [block("# >>> SPELL GEN", "# <<< SPELL GEN"),
        block("# ================= Xbow part 1 (0.4.5)", "# ================= ClassCurve (0.4.12)"),
        block("# ================= 0.4.2 FELLED TREES", "# FellCredit (spec 2.6)"),
        block("# ================= skill:fn:addxp (0.4)", "# ================= leaderboard ================="),
        block("# ================= OverallPage (0.4.6)", "# ================= 0.4.3 ADMIN CONFIG"),
        block("# ---- 0.4.5 Xbow part 2", "# ================= ManaRegen (0.4.12)"),
        block("# ================= CombatDmgSys (0.3)", "# ================= PlacedStore"),
        block("# ================= RollSys (0.4.14)", "# ================= CombatDmgSys (0.3)"),
        block("# ================= SkillStore: per-player XP", "# ================= SkillClass (0.3)"),
        block("# ---- HealMig (0.4.11 point 5)", "# ---- DocMig (0.4.14, fix (5))"),
        block("# ================= OwnCurve (0.4.16)", "# ================= GatherPace.apply (0.4.14)"),
        block("# ---- SkillLvMig (0.4.16)", "# ---- ManaGuard (point 3)"),
        block("# ================= 0.4.18 DODGE ROLL", "# ---- 0.4.18 dodge roll conflict check"),
        block("# ---- AcroMig (0.4.19", "# ---- ManaGuard (point 3)"),
        block("# 0.4.18: a \"dodge\" = any of the 4 roll effects", "# sliding XP cap (review fix)")]
# the xp.properties default text must stay byte-identical (the appended blocks are found by their text / markers)
for _blk in ("CLS_L.append(", "CURVE_L.append(", "HEAL_DOC = ["):
    assert _blk in s

# ---------------------------------------------------------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.20 - build script (derived from the generated 0.4.19 by tools/skills_0_4_20_patch.py - edit the patch, not this file;
0.4.19 was derived''', '''"""SkyySkills 0.4.21 - build script (derived from the generated 0.4.20 by tools/skills_0_4_21_patch.py - edit the patch, not this file;
0.4.20 was derived from the generated 0.4.19 by tools/skills_0_4_20_patch.py; 0.4.19 was derived''')
HEAD_0421 = '''0.4.21: THE MONK + ASSASSIN CLASS SKILLS (Skyy LOCKED 2026-10-07 "make the classes"; full notes in tools/skills_0_4_21_patch.py). Deploy
  TOGETHER with SkyyClasses 0.1.14. Class row 3 "Shaman" -> "Monk", slot 8 label "Shaman skill" -> "Discipline" (icon Bo staff, #f08a30);
  the saved key Combat.Shaman is KEPT (no data rewrite). "Shaman" / "Shaman skill" stay aliases of the Monk / Discipline (skill and
  class lookups, the mana class tables). weaponsText reads the Bo staffs as "Bo". Texts. No migration, no new row / key / asset.
  CHECKED in a bare JVM (SkyySkills/test_skyyskills_0.4.21.py, -Xverify:all, scratch under tools/dev/scratch deleted afterwards).
'''
before('0.4.20: THE SPRINT-TAP ROLL (Skyy LOCKED 2026-10-06 roll trigger = "Tap the sprint key"; full notes in tools/skills_0_4_20_patch.py). Keeps\n',
       HEAD_0421)
rep('VERSION = "0.4.20"\n', 'VERSION = "0.4.21"\n')

# ---------------------------------------------------------------------------------------------------------------- (1) the class row
rep('''              ("Shaman", "Shaman skill", "Weapon_Deployable_Slowness_Totem", "#ff7a5c"),''',
    '''              ("Monk", "Discipline", "Weapon_Staff_Bo_Wood", "#f08a30"),   # 0.4.21: the Shaman slot (saved key Combat.Shaman KEPT)''')
rep('''_ROSTER = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Shaman"]''',
    '''_ROSTER = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk"]   # 0.4.21: SkyyClasses 0.1.14 (Shaman -> Monk)
# 0.4.21: the storage key of a class row whose class was renamed - the saved XP keeps its key (players/<pkey>.properties never change)
CLASS_SAVED_KEY = {"Monk": "Combat.Shaman"}
# 0.4.21: old names -> today's (read side only): skill names -> the slot, class names -> the class
SKILL_ALIASES = [("shaman", "Monk"), ("shamans", "Monk"), ("shaman skill", "Monk")]''')
rep('''    _SL[CLASS_SLOT[_i]] = ("Combat." + _c[0], _c[1], _c[2], _c[3])''',
    '''    _SL[CLASS_SLOT[_i]] = (CLASS_SAVED_KEY.get(_c[0], "Combat." + _c[0]), _c[1], _c[2], _c[3])   # 0.4.21: a renamed class keeps its key''')
rep('''assert SLOT_LABELS[14:] == ["Fury", "Divinity"] and SLOT_LABELS[8] == "Shaman skill"''',
    '''assert SLOT_LABELS[14:] == ["Fury", "Divinity"] and SLOT_LABELS[8] == "Discipline" and SLOT_NAMES[8] == "Combat.Shaman"   # 0.4.21: renamed, key kept
assert [c[0] for c in CLASS_ROWS][3] == "Monk" and CLASS_SLOT[3] == 8 and SLOT_ICONS[8] == "Weapon_Staff_Bo_Wood" and SLOT_COLORS[8] == "#f08a30"
assert all(a not in [l.lower() for l in SLOT_LABELS] + [n.lower() for n in SLOT_NAMES] + [c[0].lower() for c in CLASS_ROWS] for a, _ in SKILL_ALIASES)''')

# ---------------------------------------------------------------------------------------------------------------- (2) the aliases (SkillDefs)
rep('''defs.addField(CtField.make("public static final String[] CLASSES = %s;" % jarr([c[0] for c in CLASS_ROWS]), defs))
''', '''defs.addField(CtField.make("public static final String[] CLASSES = %s;" % jarr([c[0] for c in CLASS_ROWS]), defs))
# 0.4.21: old names -> the index into CLASSES of today's class (the Shaman slot is the Monk); lower case, matched exactly after trim
defs.addField(CtField.make("public static final String[] ALIAS_FROM = %s;" % jarr([a for a, _ in SKILL_ALIASES]), defs))
defs.addField(CtField.make("public static final int[] ALIAS_TO = new int[] { %s };" % ", ".join(str([c[0] for c in CLASS_ROWS].index(n)) for _, n in SKILL_ALIASES), defs))
''')
rep('''defs.addMethod(CtNewMethod.make("""
public static int indexOf(String s) {
  if (s == null) return -1;
  String t = s.trim().toLowerCase();
  if (t.length() == 0) return -1;
  for (int i = 0; i < LABELS.length; i++) if (LABELS[i].toLowerCase().equals(t) || NAMES[i].toLowerCase().equals(t)) return i;
  for (int i = 0; i < CLASSES.length; i++) if (CLASSES[i].toLowerCase().equals(t)) return classSlot(i);
''', '''# 0.4.21: an old class / skill name -> the index into CLASSES of today's class, -1 = none (exact, any case, trimmed)
defs.addMethod(CtNewMethod.make("""
public static int aliasIdx(String s) {
  if (s == null) return -1;
  String t = s.trim().toLowerCase();
  for (int i = 0; i < ALIAS_FROM.length && i < ALIAS_TO.length; i++) if (ALIAS_FROM[i].equals(t)) return ALIAS_TO[i];
  return -1;
}""", defs))
# 0.4.21: a class name as SkyyClasses / SkyyProfiles publish it -> today's spelling ("Shaman" -> "Monk"); anything else unchanged
defs.addMethod(CtNewMethod.make("""
public static String canonName(String c) {
  int a = aliasIdx(c);
  return a >= 0 ? CLASSES[a] : c;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static int indexOf(String s) {
  if (s == null) return -1;
  String t = s.trim().toLowerCase();
  if (t.length() == 0) return -1;
  for (int i = 0; i < LABELS.length; i++) if (LABELS[i].toLowerCase().equals(t) || NAMES[i].toLowerCase().equals(t)) return i;
  for (int i = 0; i < CLASSES.length; i++) if (CLASSES[i].toLowerCase().equals(t)) return classSlot(i);
  if (aliasIdx(t) >= 0) return classSlot(aliasIdx(t));
''')
# SkillClass: class names through canonName
rep('''public static int slotOfClass(String c) {{
  if (c == null) return -1;
  String t = c.trim();''', '''public static int slotOfClass(String c) {{
  if (c == null) return -1;
  String t = {PKG}.SkillDefs.canonName(c.trim());''')
rep('''    String c = className(u);
    if (c != null && c.equalsIgnoreCase(pc)) {{ resync(u); return true; }}''',
    '''    String c = className(u);
    if (c != null && {PKG}.SkillDefs.canonName(c).equalsIgnoreCase({PKG}.SkillDefs.canonName(pc))) {{ resync(u); return true; }}''')
# OverallCfg.canonClass (the mana tables)
rep('''public static String canonClass(String t) {{
  if (t == null) return null;
  String x = t.trim();''', '''public static String canonClass(String t) {{
  if (t == null) return null;
  String x = {PKG}.SkillDefs.canonName(t.trim());''')

# review fix (critic 2 point 4): Overall.classOf = today's class name - a SkyyProfiles that still publishes profile:class = Shaman (0.1.5
# with a Shaman profile) reads as the Monk for the by-class Base Mana tables (OverallCfg.listed / baseFor), the Mana lines and the HUD
rep('''    if (o instanceof String && ((String) o).trim().length() > 0) return ((String) o).trim();
  }} catch (Throwable t) {{ }}
  return {PKG}.SkillClass.className(u);''', '''    if (o instanceof String && ((String) o).trim().length() > 0) return {PKG}.SkillDefs.canonName(((String) o).trim());
  }} catch (Throwable t) {{ }}
  return {PKG}.SkillDefs.canonName({PKG}.SkillClass.className(u));''')
# ---------------------------------------------------------------------------------------------------------------- (3) weaponsText
rep('''      w = w.replace('_', ' ').trim();
      if (w.length() == 0) continue;
      if (sb.length() > 0) sb.append(" / ");
      sb.append(w);''', '''      w = w.replace('_', ' ').trim();
      if (w.equals("Staff Bo")) w = "Bo";   // 0.4.21: the vanilla Bo staffs (Weapon_Staff_Bo_) are Monk weapons
      if (w.length() == 0) continue;
      if ((" / " + sb.toString() + " / ").indexOf(" / " + w + " / ") >= 0) continue;   // 0.4.21: a word once
      if (sb.length() > 0) sb.append(" / ");
      sb.append(w);''')

# ---------------------------------------------------------------------------------------------------------------- (4) texts
rep('''  return "Unknown class " + b + " - use Archer, Warrior, Mage, Berserker, Priest, Assassin or Shaman.";''',
    '''  return "Unknown class " + b + " - use Archer, Warrior, Mage, Berserker, Priest, Assassin or Monk.";''')
rep('''  return "Unknown class " + e + " - use Archer, Warrior, Mage, Berserker, Priest, Assassin or Shaman.";''',
    '''  return "Unknown class " + e + " - use Archer, Warrior, Mage, Berserker, Priest, Assassin or Monk.";''', count=2)
rep('''a class skill: archery, swordsmanship, sorcery, fury, divinity, assassination, shaman. /skills stats also opens overall."''',
    '''a class skill: archery, swordsmanship, sorcery, fury, divinity, assassination, discipline. /skills stats also opens overall."''')
rep('''| archery | swordsmanship | sorcery | fury | divinity | assassination | shaman", {ATY}.STRING);''',
    '''| archery | swordsmanship | sorcery | fury | divinity | assassination | discipline", {ATY}.STRING);''', count=2)
rep('''| archery | swordsmanship | sorcery | fury | divinity | assassination | shaman | overall (the Overall Level page)", {ATY}.STRING);''',
    '''| archery | swordsmanship | sorcery | fury | divinity | assassination | discipline | overall (the Overall Level page)", {ATY}.STRING);''')
rep('''Mage Sorcery / Berserker Fury / Priest Divinity (Assassin and Shaman later)";''',
    '''Mage Sorcery / Berserker Fury / Priest Divinity / Assassin Assassination / Monk Discipline";''')
rep('''('Assassin', 'Weapon_Daggers_Crude:1'), ('Shaman', ''), ('Mage', 'Weapon_Staff_Wood:1')''',
    '''('Assassin', 'Weapon_Daggers_Crude:1'), ('Monk', 'Weapon_Staff_Bo_Wood:1'), ('Mage', 'Weapon_Staff_Wood:1')''')
rep('''your class combat skill (SkyyClasses: Archery, Swordsmanship, Sorcery, Fury, Divinity)''',
    '''your class combat skill (SkyyClasses: Archery, Swordsmanship, Sorcery, Fury, Divinity, Assassination, Discipline)''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
for k in KEEP:
    assert s.count(k) == 1, "a block that must stay byte-identical changed: " + k[:100]
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "systems / commands: 0.4.21 adds none"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
_ix = lambda t: s.index(t)
assert _ix("public static int aliasIdx(") < _ix("public static String canonName(") < _ix("public static int indexOf(String s)") < _ix("public static int slotOfClass(")
assert _ix("public static String canonName(") < _ix("public static String canonClass(")
# the default xp.properties text is untouched: every CLS_L / CURVE_L / HEAL_DOC line of 0.4.20 is still there, byte for byte
for _ln in S0.split(LF):
    if _ln.startswith(("CLS_L.append(", "CURVE_L.append(", "HEAL_DOC = [")):
        assert s.count(_ln) == S0.count(_ln), "a default-file line changed: " + _ln[:100]
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed]
assert not _bad, "0.4.20 lines changed outside the planned places: %r" % _bad[:5]
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.20,", len(_gone), "0.4.20 lines replaced,",
      sum(op[4] - op[3] for op in _hunks) - len(_gone), "lines added net;", len(OLDS), "anchors")
