"""Derive SkyySkills/build_skyyskills_0.4.40.py from the LIVE generated SkyySkills/build_skyyskills_0.4.39.py (= the tools/deploy_set.py SET
pin; 0.4.39 came from 0.4.38 by tools/skills_0_4_39_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; 0.4.39 stays untouched, its line endings are kept.
Run:  python tools/skills_0_4_40_patch.py   then   python SkyySkills/build_skyyskills_0.4.40.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.40.py --dir tools/dev/scratch/<yours>/sk   (bare JVM, -Xverify:all)

0.4.40 (2026-10-15) = TREE BUTTONS FOR EVERY TREE SkyyTrees HAS (lean round skills0440; Skyy 2026-10-15, a screenshot of /skills with
TREE buttons only on Mining, Foraging, Farming, Cooking, Acrobatics, Exploration: "eventually i want a tree for every skill."):
  SkyyTrees 0.3.11 already has Alchemy, Smithing and Fishing trees and a class tree, and publishes them on the bridge (tree:names =
  "Mining,Foraging,Farming,Cooking,Acrobatics,Exploration,Alchemy,Smithing,Fishing", + ",Class" while its class.enabled is on), but
  SkillBonus.treeName() only knew the first six, so those rows had no TREE button (0.4.39's note "SkyyTrees has no Fishing tree" was
  stale). Now:
    treeName(slot)   Alchemy -> "alchemy", Smithing -> "smithing", Fishing -> "fishing"; Ranching and Orchard -> "farming" (one shared
                     Farming tree, docs/answered/skills.md 2026-10-11 "they keep one shared farming skill tree"); every class slot
                     (Archery, Swordsmanship, Assassination, Zen, Sorcery, Fury, Divinity) -> "class" (= /tree class, SkyyTrees opens
                     the player's own class tab). Combat (the legacy classless slot) keeps no tree.
    treeAvailable    the button shows only when the RUNNING SkyyTrees lists that tree in tree:names (compared with the tree name, so
                     Ranching / Orchard follow "Farming" and the class row follows "Class" - no hardcoded list of SkyyTrees' trees);
                     without tree:names (SkyyTrees 0.1) the four 0.1 trees (Mining / Foraging / Farming / Cooking; Ranching / Orchard
                     ride on Farming) exactly as before.
    treeFor(u, slot) NEW: treeAvailable + for a class slot it must be the player's CURRENT class (SkillClass.slot) - /tree class always
                     opens your own class tree, so no other class's Stats page gets a button that would open a different tree.
  Callers: the /skills rows (the TREE / TREE-gap columns keep their places - the same SK_TREE_JAVA / SK_TREE_GAP_JAVA pieces) and the
  Stats page's SKILL TREE button use treeFor; the Stats page click maps a Combat view to the player's class slot first (the page itself
  already shows the class skill there).
  No saved-data change, no config / Server Setup change, no new command, no bridge key written (tree:names / tree:fn:level read as before).
  ROLLBACK to 0.4.39: safe (only the extra buttons go away).
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.39.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.40.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.39"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.39"' in s and "derived from the generated 0.4.38 by tools/skills_0_4_39_patch.py" in s, "not the live generated 0.4.39"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "rbs39 = pool.makeClass" in s and "treeFor(" not in s, "not 0.4.39"
OLDS = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    OLDS.append(old)


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.40 (2026-10-15)"):].rstrip() + "\n"

# ---------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.39 - build script (derived from the generated 0.4.38 by tools/skills_0_4_39_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.40 - build script (derived from the generated 0.4.39 by tools/skills_0_4_40_patch.py - edit the patch, not this file;
0.4.39 was derived from the generated 0.4.38 by tools/skills_0_4_39_patch.py;
''')
rep('''0.4.39 (2026-10-14) = REBIRTH WRAP-UP + SOUND PASS round 2, the SkyySkills part''', NOTE.replace("\n", "\n  ").rstrip() + '''
  CHECKED: SkyySkills/test_skyyskills_0.4.40.py.
0.4.39 (2026-10-14) = REBIRTH WRAP-UP + SOUND PASS round 2, the SkyySkills part''')
rep('VERSION = "0.4.39"', 'VERSION = "0.4.40"')

# ---------------------------------------------------------------- SkillBonus.treeName / treeAvailable / treeFor
rep('''# /tree argument of a slot (SkyyTrees 0.1 trees: mining, foraging, farming, cooking; SkyyTrees 0.2 adds acrobatics, exploration);
# null = no tree for that skill. Whether the RUNNING SkyyTrees has that tree = treeAvailable (0.4.1, below).
sbn.addMethod(CtNewMethod.make(f"""
public static String treeName(int slot) {{
  if (slot == {PKG}.SkillDefs.MINING) return "mining";
  if (slot == {PKG}.SkillDefs.FORAGING) return "foraging";
  if (slot == {PKG}.SkillDefs.FARMING) return "farming";
  if (slot == {PKG}.SkillDefs.COOKING) return "cooking";
  if (slot == {PKG}.SkillDefs.ACROBATICS) return "acrobatics";
  if (slot == {PKG}.SkillDefs.EXPLORATION) return "exploration";
  return null;
}}""", sbn))''', '''# /tree argument of a slot (SkyyTrees 0.1 trees: mining, foraging, farming, cooking; SkyyTrees 0.2 adds acrobatics, exploration;
# 0.4.40: SkyyTrees 0.3 alchemy, smithing, class, 0.3.10 fishing; Ranching / Orchard share the Farming tree; every class slot = /tree class,
# which SkyyTrees opens on the player's own class tab); null = no tree for that skill. Whether the RUNNING SkyyTrees has that tree =
# treeAvailable (0.4.1, below); the class check per player = treeFor (0.4.40).
sbn.addMethod(CtNewMethod.make(f"""
public static String treeName(int slot) {{
  if (slot == {PKG}.SkillDefs.MINING) return "mining";
  if (slot == {PKG}.SkillDefs.FORAGING) return "foraging";
  if (slot == {PKG}.SkillDefs.FARMING || slot == {PKG}.SkillDefs.RANCHING || slot == {PKG}.SkillDefs.ORCHARD) return "farming";
  if (slot == {PKG}.SkillDefs.COOKING) return "cooking";
  if (slot == {PKG}.SkillDefs.ACROBATICS) return "acrobatics";
  if (slot == {PKG}.SkillDefs.EXPLORATION) return "exploration";
  if (slot == {PKG}.SkillDefs.ALCHEMY) return "alchemy";
  if (slot == {PKG}.SkillDefs.SMITHING) return "smithing";
  if (slot == {PKG}.SkillDefs.FISHING) return "fishing";
  if ({PKG}.SkillDefs.isClass(slot)) return "class";
  return null;
}}""", sbn))''')
rep('''# 0.4.1: a Tree button for this slot? SkyyTrees running (tree:fn:level) AND its bridge tree:names (SkyyTrees 0.2: comma list of tree
# labels) lists the slot; without tree:names (SkyyTrees 0.1) only its four trees - exactly the 0.4 buttons
sbn.addMethod(CtNewMethod.make(f"""
public static boolean treeAvailable(int slot) {{
  if (slot < 0 || slot >= {PKG}.SkillDefs.N || treeName(slot) == null || !treesOn()) return false;
  Object o = null;
  try {{ o = {PKG}.SkillStore.bridge().get("tree:names"); }} catch (Throwable t) {{ }}
  if (!(o instanceof String)) return slot == {PKG}.SkillDefs.MINING || slot == {PKG}.SkillDefs.FORAGING || slot == {PKG}.SkillDefs.FARMING || slot == {PKG}.SkillDefs.COOKING;
  String[] ps = ((String) o).split(",");
  for (int i = 0; i < ps.length; i++) {{
    String nm = ps[i].trim();
    if (nm.equalsIgnoreCase({PKG}.SkillDefs.LABELS[slot]) || nm.equalsIgnoreCase({PKG}.SkillDefs.NAMES[slot])) return true;
  }}
  return false;
}}""", sbn))''', '''# 0.4.1: a Tree button for this slot? SkyyTrees running (tree:fn:level) AND its bridge tree:names (SkyyTrees 0.2+: comma list of tree
# labels) lists the slot's TREE (0.4.40: compared with treeName, so Ranching / Orchard follow "Farming" and the class slots "Class" - the
# list SkyyTrees publishes decides, nothing hardcoded here); without tree:names (SkyyTrees 0.1) only its four trees - the 0.4 buttons
sbn.addMethod(CtNewMethod.make(f"""
public static boolean treeAvailable(int slot) {{
  if (slot < 0 || slot >= {PKG}.SkillDefs.N) return false;
  String tn = treeName(slot);
  if (tn == null || !treesOn()) return false;
  Object o = null;
  try {{ o = {PKG}.SkillStore.bridge().get("tree:names"); }} catch (Throwable t) {{ }}
  if (!(o instanceof String)) return tn.equals("mining") || tn.equals("foraging") || tn.equals("farming") || tn.equals("cooking");
  String[] ps = ((String) o).split(",");
  for (int i = 0; i < ps.length; i++) {{
    if (ps[i].trim().equalsIgnoreCase(tn)) return true;
  }}
  return false;
}}""", sbn))
# 0.4.40: the /tree argument of a TREE button for this player and slot, null = no button. A class slot only for the player's CURRENT
# class (/tree class always opens your own class tree - never a button on another class's Stats page that opens a different tree)
sbn.addMethod(CtNewMethod.make(f"""
public static String treeFor(java.util.UUID u, int slot) {{
  if (!treeAvailable(slot)) return null;
  if ({PKG}.SkillDefs.isClass(slot)) {{
    if (u == null) return null;
    int cs = -1;
    try {{ cs = {PKG}.SkillClass.slot(u); }} catch (Throwable t) {{ return null; }}
    if (cs != slot) return null;
  }}
  return treeName(slot);
}}""", sbn))''')

# ---------------------------------------------------------------- the /skills rows + the Stats page
rep('''        if ({PKG}.SkillBonus.treeAvailable(sl)) {{
{SK_TREE_JAVA}''', '''        if ({PKG}.SkillBonus.treeFor(u, sl) != null) {{   // 0.4.40: every tree SkyyTrees lists (class row = your class tree)
{SK_TREE_JAVA}''')
rep('''  String tree = {PKG}.SkillBonus.treeAvailable(s) ? {PKG}.SkillBonus.treeName(s) : null;''',
    '''  String tree = {PKG}.SkillBonus.treeFor(u, s);   // 0.4.40: every tree SkyyTrees lists (a class slot: only your current class)''')
rep('''    if (data.indexOf("sttree\\\\"") >= 0) {{ {PKG}.SkillBonus.openTree(this.playerRef, {PKG}.SkillBonus.treeName(this.slot)); return; }}''',
    '''    if (data.indexOf("sttree\\\\"") >= 0) {{
      int ts = this.slot;   // 0.4.40: a Combat view shows the class skill - its tree is the class tree
      if (ts == {PKG}.SkillDefs.COMBAT) {{ int c = {PKG}.SkillClass.slot(this.playerRef.getUuid()); if (c >= 0) ts = c; }}
      {PKG}.SkillBonus.openTree(this.playerRef, {PKG}.SkillBonus.treeName(ts));
      return;
    }}''')

# ---------------------------------------------------------------- checks
_i = s.index
assert _i("public static int slot(java.util.UUID u) {") < _i("public static String treeFor(java.util.UUID u, int slot) {")
assert _i("public static boolean treeAvailable(int slot) {") < _i("public static String treeFor(java.util.UUID u, int slot) {") < _i("SkillBonus.treeFor(u, sl) != null")
assert s.count("{PKG}.SkillBonus.treeAvailable(") == 0 and s.count("{PKG}.SkillBonus.treeFor(") == 2 and S0.count("{PKG}.SkillBonus.treeAvailable(") == 2
assert s.count("registerSystem(") == S0.count("registerSystem(") and s.count("registerCommand(") == S0.count("registerCommand(")
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed and not any(_o in ln for _o in OLDS if LF not in _o)]
assert not _bad, "0.4.39 lines changed outside the planned places: %r" % _bad[:5]
if os.path.exists(dst):
    os.remove(dst)
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.39,", len(_gone), "0.4.39 lines replaced;", len(OLDS), "anchors")
