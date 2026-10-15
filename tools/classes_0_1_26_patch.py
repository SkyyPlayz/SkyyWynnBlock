"""Derive SkyyClasses/build_skyyclasses_0.1.26.py from the generated 0.1.25 (the SET pin; the EDITED lineage: Skyy's edited 0.1.6 ->
classes_0_1_7_patch.py -> ... -> classes_0_1_25_patch.py -> 0.1.25; classes_0_1_6_patch.py is never re-run). 0.1.25 stays untouched; its
line endings are kept.
Run:  python tools/classes_0_1_26_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.26.py   (never --deploy)
Test: python SkyyClasses/test_skyyclasses_0.1.26.py [--dir <scratch>] [--keep]

0.1.26 (2026-10-15) = THE ABILITY TREE REDESIGN, the SkyyClasses half of R2 + R3 (research/Ability-Tree-Redesign-Spec.md; with SkyyTrees
0.3.13; Skyy 2026-10-15 docs/answered/skills.md "ABILITY TREE REDESIGN" 1-3: "id have the ability's actually be in the skill tree. and thats
how you unlock them. then each ability branches into its modiferss, and each of those thakes an ability point to unlock ..." + "so you click
an ability, click the slot it goes in, then click a modifer and a slot" + "modifiers unlocked in the tee, but not in the ability."):
  (1) THE TREE OWNS THE ABILITIES AND MODIFIERS (spec 4.1 / 4.2): with class trees on (abil.treeGate + SkyyTrees' tree:fn:abil), an ability
    works when its ABILITY node is owned (A1 = tier 0, A2 = tier 1, A3 = the A2-alt, A4a / A4b = the two A1-alts), and a modifier is usable
    on it when its MODIFIER node is owned ("A1.Power" ...) - no ability-level gate any more (mods.unlock stays as the rule without a tree:
    class trees off or no SkyyTrees). The ability LEVEL (uses) still adds power and modifier levels still grow by use from Lv 1. The 2
    modifier slots come with the ability (the old M1A-M4B slot nodes are gone); rebirth slots 3 + 4 stay. The A1-alt pick follows the tree:
    an owned A4b = pick B, A4a = pick A (the stored alt and the loadout rows follow it at the next tree read; the /cast page's alt toggle
    says to use the tree while the tree decides). The level-up line no longer announces new modifiers while the tree owns them.
  (2) THE LATTICE ACTIONS (spec 6.3 / 8): class:fn:abilDo "hold" <ability> [<modifier>] (checks it is yours - nothing changes), "place"
    <ability> <row 0-3> (it goes on that row; the ability that sat there trades places - the 4 rows are p1 p2 a1 a2, casting unchanged),
    "mod" <ability> <slot>:<modifier>, "clearMod" <ability> <slot>, "back"; "rbpick" (Max Up) and "attune" (the Imbue element) stay. The
    old actions swap / pick / equip / unequip are REFUSED with a log line (SkyyTrees 0.3.13 never sends them). Every change out of combat
    only, the same doubling / exclusion rules. class:fn:abilPanel answers 120 fields: the 0.1.25 ones (same places) + [94] the combat
    line, [95..98] usable per row (owned in the tree), [99..102] rebirth upgrades per row, [103..106] the level gain per row, [107..110]
    the keys, [111] the row Elemental Imbue sits in (-1 none), [112] its element, [113] the rebirth slots, [114 / 115] the rebirth slot
    rows, [116..119] the tree node of each row (A1 ... A4b); fix round: [120..124] the rune icon of each ability node (A1 A2 A3 A4a A4b,
    "" = none), [125..128] the stats line of each row (Mana + Stamina + cooldown of the shape it casts) - 129 fields.
  (3) THE PROFILE UPDATE'S FACTS: NEW class:fn:migInfo (String pkey -> "alt=A;Meteor=Power,Radius;..." - per ability the modifiers that were
    USABLE before: ability level >= the mods.unlock step, or equipped; null = the ability file cannot be read now) for SkyyTrees 0.3.13's
    one-time update; the first answer for a profile copies abilities/<pkey>.properties into history/abiltree2/ (the History snapshot of
    spec 7). SkyyClasses' own file is not rewritten by the update (p1 / p2 / a1 / a2, e. / e2. and the uses stay).
  (4) tree:reads:SkyyClasses lists the new node keys (Class.<Class>.A1 .. A4a / A4b and Class.<Class>.A1.Power ...) instead of A1-A4 / M1A-
    M4B. Texts: "buy it in your class tree (node A1, 1 AP)" instead of "Enable".
  REBIRTH R6 (rebirth:part:classes) needs no change: it stores ability levels, never tree node ids.
  FIX ROUND (critics): the History copy has its own lock (never the AbilSave monitor the world thread must not wait on), is verified
    (same length) and migInfo answers null (the update waits) when it fails; the alt sync logs INFO only when the pick changed (else
    limited warnings); no fixed "1 AP" in the texts; the abil.treeGate / mods.unlock help says what the tree does; the panel grows to
    129 fields: [120..124] the rune icon of each ability node, [125..128] the stats line of each row.
  FIX ROUND 2 (critics): a History copy from an EARLIER server run that differs from the ability file is kept as <pkey>.properties.<millis>
    and a fresh copy made (a rollback + a second update: the Undo restores the state right before THIS update; this run's copy is refreshed
    in place, an identical one kept); the panel syncs the alt pick only from a FRESH tree list (a cached one may still be the previous
    class's within 1 s of a class switch - treeCsv syncs its own fresh fetches).
  Saved data: none new (the alt line may change to follow the tree). ROLLBACK to 0.1.25: only together with SkyyTrees below 0.3.13 (their
  ROLLBACK FLOOR) - 0.1.25 reads M1A-M4B for the modifier slots.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.25.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.26.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.25"' in s and "GENERATED by tools/classes_0_1_25_patch.py from the generated 0.1.24" in s, \
    "build_skyyclasses_0.1.25.py is not the generated 0.1.25"
assert "class:fn:migInfo" not in s
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")
CHANGES = []
OLD = s


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:200])
    s = s.replace(old, new)
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.26 (2026-10-15)"):].rstrip()

# ================================================================================================ docstring, version
rep('''"""SkyyClasses 0.1.25 - build script (javassist via jpype). GENERATED by tools/classes_0_1_25_patch.py from the generated 0.1.24 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_24_patch.py -> 0.1.24) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''', '''"""SkyyClasses 0.1.26 - build script (javassist via jpype). GENERATED by tools/classes_0_1_26_patch.py from the generated 0.1.25 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_25_patch.py -> 0.1.25) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''' + NOTE.replace(LF, LF + "  ").replace("  " + LF, LF) + '''
  Notes in tools/classes_0_1_26_patch.py. CHECKED with SkyyClasses/test_skyyclasses_0.1.26.py.
=== 0.1.25 (history; still true unless 0.1.26 above says otherwise) ===
''')
rep('VERSION = "0.1.25"', 'VERSION = "0.1.26"')

# ================================================================================================ (4) the reader list
rep('''TREE_SLOTS = ["A1", "A2", "A3", "A4", "M1A", "M1B", "M2A", "M2B", "M3A", "M3B", "M4A", "M4B"]
TREE_READS = ",".join("Class.%s.%s" % (_c, _n) for _c in ("Mage", "Priest", "Monk", "Assassin", "Warrior", "Berserker", "Archer", "Spellblade") for _n in TREE_SLOTS + TREE_K[_c])''',
    '''# 0.1.26 (the ability tree redesign): the ability nodes (tier 0-4 = A1, A2, A3, A4a, A4b) + one modifier node per modifier ("A1.Power")
LINE_ID = {0: "A1", 1: "A2", 2: "A3", 3: "A4a", 4: "A4b"}
def tree_nodes(c):
    out = []
    for _a in sorted([a for a in ABILS if a[2] == c], key=lambda a: a[3]):
        out.append(LINE_ID[_a[3]])
        out += ["%s.%s" % (LINE_ID[_a[3]], _m) for _m in AB_MODS[_a[0]]]
    return out
TREE_READS = ",".join("Class.%s.%s" % (_c, _n) for _c in ("Mage", "Priest", "Monk", "Assassin", "Warrior", "Berserker", "Archer", "Spellblade") for _n in tree_nodes(_c) + TREE_K[_c])
assert "Class.Mage.A1.Power" in TREE_READS and "Class.Mage.A4b.Pierce" in TREE_READS and "Class.Assassin.A4b" not in TREE_READS and "M1A" not in TREE_READS''')

# ================================================================================================ (1) the tree owns abilities + modifiers
rep('''    if ("!err".equals(csv)) return treeKeep(u, k);
    @PKG@.AbilStore.TREEC.put(u, new Object[] { k, Long.valueOf(now), csv });
    return csv;
  } catch (Throwable t) { return treeKeep(u, k); }
}
""",''', '''    if ("!err".equals(csv)) return treeKeep(u, k);
    @PKG@.AbilStore.TREEC.put(u, new Object[] { k, Long.valueOf(now), csv });
    if (csv != null) syncPick(k, @PKG@.ClassStore.classIndex(u), csv);   // 0.1.26: the A1-alt pick follows the tree (A4a / A4b)
    return csv;
  } catch (Throwable t) { return treeKeep(u, k); }
}
""",''')
rep('''public static boolean lineOn(String csv, int ai) {
  if (!@PKG@.AbilCfg.TREE_GATE || csv == null || ai < 0) return true;
  return @PKG@.AbilModDefs.csvHas(csv, "A" + lineOf(ai));
}
""",
r"""
public static int modSlots(String csv, int ai) {
  if (!@PKG@.AbilCfg.TREE_GATE || csv == null || ai < 0) return 2;
  int l = lineOf(ai);
  int n = 0;
  if (@PKG@.AbilModDefs.csvHas(csv, "M" + l + "A")) n++;
  if (@PKG@.AbilModDefs.csvHas(csv, "M" + l + "B")) n++;
  return n;
}
""",''', '''public static String lineId(int ai) {
  if (ai < 0) return "";
  int t = @PKG@.AbilDefs.TIER[ai];
  return t == 0 ? "A1" : (t == 1 ? "A2" : (t == 2 ? "A3" : (t == 3 ? "A4a" : "A4b")));
}
""",
r"""
public static boolean lineOn(String csv, int ai) {
  if (!@PKG@.AbilCfg.TREE_GATE || csv == null || ai < 0) return true;
  return @PKG@.AbilModDefs.csvHas(csv, lineId(ai));   // 0.1.26: the ABILITY node (A1, A2, A3, A4a, A4b)
}
""",
r"""
public static int modSlots(String csv, int ai) {
  if (!@PKG@.AbilCfg.TREE_GATE || csv == null || ai < 0) return 2;
  return lineOn(csv, ai) ? 2 : 0;   // 0.1.26: the 2 modifier slots come with the ability node (the M1A-M4B slot nodes are gone)
}
""",
r"""
public static boolean modOk(String csv, int ai, int k, int lvl) {
  if (ai < 0 || k < 0 || k >= @PKG@.AbilModDefs.count(ai)) return false;
  if (@PKG@.AbilCfg.TREE_GATE && csv != null) return @PKG@.AbilModDefs.csvHas(csv, lineId(ai) + "." + @PKG@.AbilModDefs.MID[@PKG@.AbilModDefs.at(ai, k)]);   // 0.1.26: its MODIFIER node
  return lvl >= @PKG@.AbilModDefs.unlockAt(k);   // no class tree: the ability level unlocks it (mods.unlock, as before)
}
""",
r"""
public static boolean treeOwnsPick(java.util.UUID u) {
  return @PKG@.AbilCfg.TREE_GATE && treeCsv(u) != null;
}
""",''')
rep('''public static int[] equipped(java.util.Properties p, int ai, int lvl, int slots) {
  int[] r = new int[] { -1, -1, -1, -1 };   // 0.1.25: slots 3 + 4 (rebirth) - e2.<Ability>
  if (ai < 0) return r;
  String id = @PKG@.AbilDefs.IDS[ai];
  String[] e = eqOf4(p, id);
  for (int j = 0; j < 4 && j < slots; j++) {
    int mi = @PKG@.AbilModDefs.find(e[j]);
    int k = @PKG@.AbilModDefs.pos(ai, mi);
    if (mi < 0 || k < 0 || lvl < @PKG@.AbilModDefs.unlockAt(k)) continue;''', '''public static int[] equipped(java.util.Properties p, int ai, int lvl, int slots, String csv) {
  int[] r = new int[] { -1, -1, -1, -1 };   // 0.1.25: slots 3 + 4 (rebirth) - e2.<Ability>
  if (ai < 0) return r;
  String id = @PKG@.AbilDefs.IDS[ai];
  String[] e = eqOf4(p, id);
  for (int j = 0; j < 4 && j < slots; j++) {
    int mi = @PKG@.AbilModDefs.find(e[j]);
    int k = @PKG@.AbilModDefs.pos(ai, mi);
    if (mi < 0 || k < 0 || !modOk(csv, ai, k, lvl)) continue;   // 0.1.26: the tree's modifier node (no tree: the ability level)''')
rep('''    int[] eq = equipped(p, ai, stored, slotsOf(csv, ai, k));   // unlocked modifiers stay unlocked (Skyy 5b); 0.1.25: + rebirth slots''',
    '''    int[] eq = equipped(p, ai, stored, slotsOf(csv, ai, k), csv);   // 0.1.26: the tree decides; 0.1.25: + rebirth slots''')
rep('''    int l0 = alvlk(k, uses);
    int[] eq = @PKG@.AbilCfg.MODS_ON ? equipped(p, ai, l0, slotsOf(treeCsv(u), ai, k)) : new int[] { -1, -1, -1, -1 };''',
    '''    int l0 = alvlk(k, uses);
    String ucsv = treeCsv(u);   // 0.1.26
    int[] eq = @PKG@.AbilCfg.MODS_ON ? equipped(p, ai, l0, slotsOf(ucsv, ai, k), ucsv) : new int[] { -1, -1, -1, -1 };''')
rep('''      String nu = newMods(ai, l0, l1);''', '''      String nu = (@PKG@.AbilCfg.TREE_GATE && ucsv != null) ? "" : newMods(ai, l0, l1);   // 0.1.26: with a class tree the tree unlocks modifiers''')
rep('''      say(pr, @PKG@.AbilDefs.NAMES[ai] + " reached Lv " + l1 + "! " + gainText(ai, l1) + "." + (nu.length() > 0 ? " New modifier: " + nu + " - equip it in /tree class." : ""));''',
    '''      say(pr, @PKG@.AbilDefs.NAMES[ai] + " reached Lv " + l1 + "! " + gainText(ai, l1) + "." + (nu.length() > 0 ? " New modifier: " + nu + " - equip it in /tree class." : ""));   // 0.1.26: nu stays empty with a class tree''')
rep('''    send(pr, (n == 1 ? "Your ability " + names + " is off" : "Your abilities " + names + " are off") + ": open /tree, class tab, and click Enable (free) - then they go on your Ability 2 / 3 keys.", "#ffc800");''',
    '''    send(pr, (n == 1 ? "Your ability " + names + " is not unlocked yet" : "Your abilities " + names + " are not unlocked yet") + ": open /tree, class tab, and buy " + (n == 1 ? "its node" : "their nodes") + " on page 1 - then they go on your Ability 2 / 3 keys.", "#ffc800");   // 0.1.26 (fix round: no fixed AP number)''')
rep('''  String csv = csv0;
  if (useCsv) @PKG@.AbilStore.TREEC.put(u, new Object[] { k, Long.valueOf(now), csv0 });
  else csv = treeCsv(u);
  int lv = level(u, ci);''', '''  String csv = csv0;
  if (useCsv) @PKG@.AbilStore.TREEC.put(u, new Object[] { k, Long.valueOf(now), csv0 });
  else csv = treeCsv(u);
  if (useCsv && csv != null) syncPick(k, ci, csv);   // 0.1.26: the alt pick follows the tree before the rows are read - fix round 2: only a FRESH list (TREEC is not per class; treeCsv syncs its own fresh fetch)
  int lv = level(u, ci);''')
rep('''public static Object[] panel(java.util.UUID u, String csv0, boolean useCsv) {
  Object[] o = new Object[94];   // 0.1.25: + [78 + i * 4 ..] = slot 3 + 4 of card i (name, level, name, level) - SkyyTrees 0.3.10''',
    '''public static Object[] panel(java.util.UUID u, String csv0, boolean useCsv) {
  Object[] o = new Object[129];   // 0.1.25: + [78 + i * 4 ..] = slot 3 + 4 of card i (name, level, name, level) - SkyyTrees 0.3.10; 0.1.26: + [94 .. 128] (the Lattice)''')
rep('''    int[] eq = ai < 0 ? new int[] { -1, -1, -1, -1 } : equipped(p, ai, l, slots);''',
    '''    int[] eq = ai < 0 ? new int[] { -1, -1, -1, -1 } : equipped(p, ai, l, slots, csv);''')
rep('''    if (ai >= 0 && @PKG@.AbilDefs.owns(ai, lv, grant, pick) && !lineOn(csv, ai)) stt = "disabled";   // owned, the tree has not enabled it
    o[b + 15] = stt;
  }''', '''    if (ai >= 0 && @PKG@.AbilDefs.owns(ai, lv, grant, pick) && !lineOn(csv, ai)) stt = "disabled";   // owned, the tree has not enabled it
    o[b + 15] = stt;
    // 0.1.26 THE LATTICE FIELDS: usable (owned in the tree), rebirth upgrades to place, the level gain, the key, the tree node
    boolean us = ai >= 0 && @PKG@.AbilDefs.owns(ai, lv, grant, pick) && lineOn(csv, ai);
    o[95 + i] = Boolean.valueOf(us);
    o[99 + i] = Integer.valueOf(ai < 0 ? 0 : (int) numOf(p, "rb.pick." + id));
    o[103 + i] = ai < 0 ? "" : gainText(ai, le);
    o[107 + i] = @PKG@.AbilDefs.key(i);
    o[116 + i] = lineId(ai);
    o[125 + i] = ai < 0 ? "" : @PKG@.AbilPage.costLine(ai, i, true, ci);   // fix round (critic C7): Mana + Stamina + cooldown of the shape this row casts
    if (us && ai == @PKG@.AbilDefs.IMBUE) o[111] = Integer.valueOf(i);
  }
  for (int t = 0; t < 5; t++) {   // fix round (critic C9): the rune icon of each ability node A1 A2 A3 A4a A4b ("" = none / not loaded) - the unpicked alt too
    int at = @PKG@.AbilDefs.of(ci, t);
    o[120 + t] = (at < 0 || !runeLoaded(@PKG@.AbilDefs.RUNE[at])) ? "" : @PKG@.AbilDefs.RUNE[at];
  }
  o[94] = Boolean.TRUE.equals(o[3]) ? "Change your loadout out of combat" : "";
  if (!(o[111] instanceof Integer)) o[111] = Integer.valueOf(-1);
  o[112] = ((Integer) o[111]).intValue() >= 0 ? attText(k, csv) : "";
  o[113] = Integer.valueOf(rbSlots(k));
  o[114] = Long.valueOf(@PKG@.AbilCfg.RB_SLOT_EVERY);
  o[115] = Long.valueOf(@PKG@.AbilCfg.RB_SLOT_MAX);''')
rep('''  int slots = slotsOf(csv, ai, k);   // 0.1.25: + the rebirth slots
  int[] eq = equipped(p, ai, l, slots);
  String[] st = eqOf4(p, aid);''', '''  int slots = slotsOf(csv, ai, k);   // 0.1.25: + the rebirth slots
  int[] eq = equipped(p, ai, l, slots, csv);   // 0.1.26
  String[] st = eqOf4(p, aid);
  boolean tg = @PKG@.AbilCfg.TREE_GATE && csv != null;   // 0.1.26: the tree owns the modifiers''')
rep('''    int mi = @PKG@.AbilModDefs.at(ai, j);
    int at = @PKG@.AbilModDefs.unlockAt(j);
    long mu = numOf(p, "m." + aid + "." + @PKG@.AbilModDefs.MID[mi]);
    int mxx = (int) numOf(p, "rb.modmax." + aid + "." + @PKG@.AbilModDefs.MID[mi]);   // 0.1.23
    int ml = @PKG@.AbilModDefs.modLevelX(mu, mxx);
    int cnt = (eq[0] == mi ? 1 : 0) + (eq[1] == mi ? 1 : 0) + (eq[2] == mi ? 1 : 0) + (eq[3] == mi ? 1 : 0);   // 0.1.25: 4 slots
    boolean dbl = @PKG@.AbilModDefs.MSTACK[mi] && ml >= 2;
    String now = l >= at ? modText(ai, mi, ml, cnt > 0 ? cnt : 1) : "unlocks at " + @PKG@.AbilDefs.NAMES[ai] + " Lv " + at;
    long nx = @PKG@.AbilModDefs.modNextX(mu, mxx);
    String next = l < at ? modText(ai, mi, 1, 1) : (nx > 0L ? "Lv " + (ml + 1) + ": " + modText(ai, mi, ml + 1, 1) : "top level");
    out[j + 1] = @PKG@.AbilModDefs.MID[mi] + "|" + @PKG@.AbilModDefs.MNAME[mi] + "|" + at + "|" + (l >= at ? "1" : "0") + "|" + ml + "|" + mu + "|" + nx''',
    '''    int mi = @PKG@.AbilModDefs.at(ai, j);
    int at = tg ? 0 : @PKG@.AbilModDefs.unlockAt(j);   // 0.1.26: 0 = the tree unlocks it
    boolean un = modOk(csv, ai, j, l);
    long mu = numOf(p, "m." + aid + "." + @PKG@.AbilModDefs.MID[mi]);
    int mxx = (int) numOf(p, "rb.modmax." + aid + "." + @PKG@.AbilModDefs.MID[mi]);   // 0.1.23
    int ml = @PKG@.AbilModDefs.modLevelX(mu, mxx);
    int cnt = (eq[0] == mi ? 1 : 0) + (eq[1] == mi ? 1 : 0) + (eq[2] == mi ? 1 : 0) + (eq[3] == mi ? 1 : 0);   // 0.1.25: 4 slots
    boolean dbl = @PKG@.AbilModDefs.MSTACK[mi] && ml >= 2;
    String now = un ? modText(ai, mi, ml, cnt > 0 ? cnt : 1) : (tg ? "buy it in your class tree (node " + lineId(ai) + "." + @PKG@.AbilModDefs.MID[mi] + ")" : "unlocks at " + @PKG@.AbilDefs.NAMES[ai] + " Lv " + at);
    long nx = @PKG@.AbilModDefs.modNextX(mu, mxx);
    String next = !un ? modText(ai, mi, 1, 1) : (nx > 0L ? "Lv " + (ml + 1) + ": " + modText(ai, mi, ml + 1, 1) : "top level");
    out[j + 1] = @PKG@.AbilModDefs.MID[mi] + "|" + @PKG@.AbilModDefs.MNAME[mi] + "|" + at + "|" + (un ? "1" : "0") + "|" + ml + "|" + mu + "|" + nx''')
rep('''    int at = @PKG@.AbilModDefs.unlockAt(pos);
    if (l < at) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " unlocks at " + nm + " Lv " + at + " (Lv " + l + " now) - use " + nm + " to level it.";''',
    '''    int at = @PKG@.AbilModDefs.unlockAt(pos);
    if (!modOk(csv, ai, pos, l)) {   // 0.1.26: the tree's modifier node (no tree: the ability level)
      if (@PKG@.AbilCfg.TREE_GATE && csv != null) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " is not unlocked - buy it in your class tree (node " + lineId(ai) + "." + @PKG@.AbilModDefs.MID[mi] + ").";
      return "-" + @PKG@.AbilModDefs.MNAME[mi] + " unlocks at " + nm + " Lv " + at + " (Lv " + l + " now) - use " + nm + " to level it.";
    }''')
rep('''  if (x.equals("swap")) {
    int sa = -1;
    int sb = -1;
    try { sa = Integer.parseInt(a.trim()); sb = Integer.parseInt(b.trim()); } catch (Throwable t) { return "-Pick two slots."; }
    String s = swapSlots(u, sa, sb);
    r = s.startsWith("ok:") ? "+" + s.substring(3) : "-" + s;
  } else if (x.equals("pick")) {
    if (combatMs(u) > 0L) return "-Leave combat first - abilities change only out of combat.";
    String k = @PKG@.ClassCfg.pkey(u);
    boolean can = @PKG@.AbilStore.granted(k) || (long) level(u, ci) >= @PKG@.AbilDefs.unlock(3);
    if (!can) return "-You choose your Ability 1 alt at " + @PKG@.ClassDefs.SKILLS[ci] + " " + @PKG@.AbilDefs.unlock(3) + ".";
    String s = setPick(k, ci, a);
    r = s.startsWith("Your Ability 1 alt is now") ? "+" + s : "-" + s;
  } else if (x.equals("equip")) {
    String v = b == null ? "" : b;
    int c = v.indexOf(':');
    if (c <= 0) return "-Usage: equip <ability> <slot>:<modifier>.";
    int sl = -1;
    try { sl = Integer.parseInt(v.substring(0, c).trim()); } catch (Throwable t) { sl = -1; }
    r = equipMod(u, a, sl, v.substring(c + 1).trim(), csv, false);
  } else if (x.equals("unequip")) {
    int sl = -1;
    try { sl = Integer.parseInt(b.trim()); } catch (Throwable t) { sl = -1; }
    r = equipMod(u, a, sl, "", csv, false);
  } else if (x.equals("rbpick")) {''', '''  if (x.equals("swap") || x.equals("pick") || x.equals("equip") || x.equals("unequip")) {   // 0.1.26: the 0.3.12 panel's actions
    @PKG@.ClassCfg.warnLimited("class:fn:abilDo: the old action '" + x + "' is refused since SkyyClasses 0.1.26 (SkyyTrees 0.3.13 uses hold / place / mod / clearMod / back)");
    return "-This ability panel changed in SkyyClasses 0.1.26 - update SkyyTrees to 0.3.13.";
  } else if (x.equals("hold")) {
    r = holdText(u, ci, a, b, csv);
  } else if (x.equals("place")) {
    int row = -1;
    try { row = Integer.parseInt(b.trim()); } catch (Throwable t) { row = -1; }
    r = placeRow(u, a, row, csv);
  } else if (x.equals("mod")) {
    String v = b == null ? "" : b;
    int c = v.indexOf(':');
    if (c <= 0) return "-Usage: mod <ability> <slot>:<modifier>.";
    int sl = -1;
    try { sl = Integer.parseInt(v.substring(0, c).trim()); } catch (Throwable t) { sl = -1; }
    r = equipMod(u, a, sl, v.substring(c + 1).trim(), csv, false);
  } else if (x.equals("clearmod")) {
    int sl = -1;
    try { sl = Integer.parseInt(b.trim()); } catch (Throwable t) { sl = -1; }
    r = equipMod(u, a, sl, "", csv, false);
  } else if (x.equals("back")) {
    r = "Ability: showing all your abilities";
  } else if (x.equals("rbpick")) {''')
rep('''  String aid = @PKG@.AbilDefs.IDS[ai];
  int at = @PKG@.AbilModDefs.unlockAt(@PKG@.AbilModDefs.pos(ai, mi));   // FIX 2 (critic): never on a locked modifier (the modRows rule)
  if (alvlk(k, numOf(@PKG@.AbilStore.load(k), "u." + aid)) < at) return "-That modifier is still locked - it unlocks at " + @PKG@.AbilDefs.NAMES[ai] + " Lv " + at + ".";''',
    '''  String aid = @PKG@.AbilDefs.IDS[ai];
  int at = @PKG@.AbilModDefs.unlockAt(@PKG@.AbilModDefs.pos(ai, mi));   // FIX 2 (critic): never on a locked modifier (the modRows rule)
  String csvR = treeCsv(u);   // 0.1.26: the tree's modifier node (no tree: the ability level)
  if (!modOk(csvR, ai, @PKG@.AbilModDefs.pos(ai, mi), alvlk(k, numOf(@PKG@.AbilStore.load(k), "u." + aid))))
    return "-That modifier is still locked - " + (@PKG@.AbilCfg.TREE_GATE && csvR != null ? "buy it in your class tree (node " + lineId(ai) + "." + @PKG@.AbilModDefs.MID[mi] + ")." : "it unlocks at " + @PKG@.AbilDefs.NAMES[ai] + " Lv " + at + ".");''')
rep('''    refuse(pr, (s >= 2 ? "No alt yet - " : "") + "enable " + nm + " in your class tree first: /tree class, node A" + lineOf(ai) + " - nothing was spent.");''',
    '''    refuse(pr, (s >= 2 ? "No alt yet - " : "") + "unlock " + nm + " in your class tree first: /tree class, node " + lineId(ai) + " - nothing was spent.");   // 0.1.26''')
rep('''public static int slotsOf(String csv, int ai, String k) {
  if (ai < 0) return 0;''', '''public static int slotsOf(String csv, int ai, String k) {
  if (ai < 0) return 0;
  if (@PKG@.AbilCfg.TREE_GATE && csv != null && !lineOn(csv, ai)) return 0;   // 0.1.26: an ability the tree has not unlocked has no slot''')
rep('''  if (t < 2 && @PKG@.AbilCfg.TREE_GATE) return "unlock M" + lineOf(ai) + (t == 0 ? "A" : "B") + " in your class tree" + (ev > 0L && rb < (int) @PKG@.AbilCfg.RB_SLOT_MAX ? " (or reach rebirth " + ((long) (rb + 1) * ev) + ")" : "");''',
    '''  if (t < 2 && @PKG@.AbilCfg.TREE_GATE) return "unlock " + @PKG@.AbilDefs.NAMES[ai] + " in your class tree first (node " + lineId(ai) + ")";   // 0.1.26: the slots come with the ability''')

# ================================================================================================ (2) + (3) the new late methods
rep('''  pruneD(@PKG@.AbilStore.IMBUE, now, 0, 0);
}
"""
]


def _late_stub(src):''', '''  pruneD(@PKG@.AbilStore.IMBUE, now, 0, 0);
}
""",
# 0.1.26: the A1-alt pick follows the class tree - an owned A4b = pick B, A4a = pick A (setPick moves the loadout rows along); "" = nothing changed
r"""
public static String syncPick(String k, int ci, String csv) {
  if (!@PKG@.AbilCfg.TREE_GATE || csv == null || k == null || ci < 0 || @PKG@.AbilDefs.of(ci, 3) < 0) return "";
  boolean ha = @PKG@.AbilModDefs.csvHas(csv, "A4a");
  boolean hb = @PKG@.AbilModDefs.csvHas(csv, "A4b");
  if (ha == hb) return "";
  if (hb && @PKG@.AbilDefs.of(ci, 4) < 0) return "";
  String want = hb ? "B" : "A";
  if (want.equals(@PKG@.AbilStore.pick(k))) return "";
  String r = setPick(k, ci, want);
  if (r != null && r.startsWith("Your Ability 1 alt is now")) @PKG@.ClassCfg.info("the Ability 1 alt of " + k + " follows the class tree (" + (hb ? "A4b" : "A4a") + "): " + r);
  else @PKG@.ClassCfg.warnLimited("the Ability 1 alt of " + k + " cannot follow the class tree (" + (hb ? "A4b" : "A4a") + ") right now: " + r);   // fix round (critic B4)
  return r;
}
""",
# 0.1.26 class:fn:abilDo "hold": is that ability (and modifier) yours to place? Nothing changes; "Ability: ..." = yes, "-why" = no
r"""
public static String holdText(java.util.UUID u, int ci, String a, String b, String csv) {
  int ai = @PKG@.AbilDefs.find(a);
  if (u == null || ai < 0 || @PKG@.AbilDefs.CLS[ai] != ci) return "-That is not one of your abilities.";
  String k = @PKG@.ClassCfg.pkey(u);
  String nm = @PKG@.AbilDefs.NAMES[ai];
  if (!@PKG@.AbilDefs.owns(ai, level(u, ci), @PKG@.AbilStore.granted(k), @PKG@.AbilStore.pick(k)) || !lineOn(csv, ai))
    return "-" + nm + " is not unlocked yet - buy it in your class tree (node " + lineId(ai) + ").";
  if (b == null || b.trim().length() == 0) return "Ability: holding " + nm + " - click one of the 4 ability slots (the two trade places)";
  int mi = @PKG@.AbilModDefs.find(b);
  int pos = @PKG@.AbilModDefs.pos(ai, mi);
  if (mi < 0 || pos < 0) return "-" + b + " is not a " + nm + " modifier.";
  int l = alvlk(k, numOf(@PKG@.AbilStore.load(k), "u." + @PKG@.AbilDefs.IDS[ai]));
  if (!modOk(csv, ai, pos, l)) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " is not unlocked - buy it in your class tree (node " + lineId(ai) + "." + @PKG@.AbilModDefs.MID[mi] + ").";
  return "Ability: holding " + @PKG@.AbilModDefs.MNAME[mi] + " - click one of " + nm + "'s modifier slots (in its own row)";
}
""",
# 0.1.26 class:fn:abilDo "place": the ability goes on row `row` (0-3 = p1 p2 a1 a2); what sat there trades places (out of combat)
r"""
public static String placeRow(java.util.UUID u, String id, int row, String csv) {
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0 || !@PKG@.AbilDefs.classHas(ci)) return "-Your class has no abilities yet.";
  if (row < 0 || row > 3) return "-Pick one of the 4 ability slots.";
  if (combatMs(u) > 0L) return "-Leave combat first - your loadout changes only out of combat.";
  int ai = @PKG@.AbilDefs.find(id);
  if (ai < 0 || @PKG@.AbilDefs.CLS[ai] != ci) return "-That is not one of your abilities.";
  String k = @PKG@.ClassCfg.pkey(u);
  if (csv != null) syncPick(k, ci, csv);
  int lv = level(u, ci);
  boolean grant = @PKG@.AbilStore.granted(k);
  if (!@PKG@.AbilDefs.owns(ai, lv, grant, @PKG@.AbilStore.pick(k)) || !lineOn(csv, ai)) return "-" + @PKG@.AbilDefs.NAMES[ai] + " is not unlocked yet - buy it in your class tree (node " + lineId(ai) + ").";
  String[] sl = @PKG@.AbilStore.slots(k, ci);
  int from = -1;
  for (int i = 0; i < 4; i++) if (@PKG@.AbilDefs.IDS[ai].equals(sl[i])) from = i;
  if (from < 0) return "-" + @PKG@.AbilDefs.NAMES[ai] + " is not in your loadout right now - try again.";
  if (from == row) return "-" + @PKG@.AbilDefs.NAMES[ai] + " is already on " + @PKG@.AbilDefs.key(row) + ".";
  String[] ns = new String[] { sl[0], sl[1], sl[2], sl[3] };
  ns[row] = sl[from];
  ns[from] = sl[row];
  if (!@PKG@.AbilStore.set(k, new String[] { "p1", "p2", "a1", "a2" }, ns)) return "-Your ability file could not be read - nothing changed (see the server log).";
  @PKG@.AbilStore.saveSoon(k);
  mirrorSoon(u);
  int other = @PKG@.AbilDefs.find(sl[row]);
  boolean oo = other >= 0 && @PKG@.AbilDefs.owns(other, lv, grant, @PKG@.AbilStore.pick(k)) && lineOn(csv, other);
  return "+" + @PKG@.AbilDefs.NAMES[ai] + " is on " + @PKG@.AbilDefs.key(row) + " now" + (oo ? " - " + @PKG@.AbilDefs.NAMES[other] + " moved to " + @PKG@.AbilDefs.key(from) : "") + ".";
}
""",
# 0.1.26 class:fn:migInfo (SkyyTrees 0.3.13's one-time profile update): "alt=A;<Ability>=<Mod>,<Mod>;..." = per ability the modifiers that
# were USABLE before (ability level >= its mods.unlock step, or equipped); null = the ability file cannot be read right now (the update
# waits). The first answer for a profile copies abilities/<pkey>.properties into history/abiltree2/ (spec 7: History first)
r"""
public static String migInfo(String k) {
  if (k == null || k.trim().length() == 0 || @PKG@.AbilStore.DIR == null) return null;
  java.util.Properties p = @PKG@.AbilStore.load(k);
  if (@PKG@.AbilStore.FAILAT.get(k) != null) return null;
  if (!@PKG@.AbilSave.histCopy(k)) return null;   // fix round (critic A1): no verified History copy = no facts = the update waits
  StringBuilder b = new StringBuilder();
  b.append("alt=").append(@PKG@.AbilStore.pick(k));
  for (int ai = 0; ai < @PKG@.AbilDefs.IDS.length; ai++) {
    String id = @PKG@.AbilDefs.IDS[ai];
    int l = alvlk(k, numOf(p, "u." + id));
    String[] e = eqOf4(p, id);
    String us = "";
    for (int j = 0; j < @PKG@.AbilModDefs.count(ai); j++) {
      String mid = @PKG@.AbilModDefs.MID[@PKG@.AbilModDefs.at(ai, j)];
      boolean eq = mid.equalsIgnoreCase(e[0]) || mid.equalsIgnoreCase(e[1]) || mid.equalsIgnoreCase(e[2]) || mid.equalsIgnoreCase(e[3]);
      if (l >= @PKG@.AbilModDefs.unlockAt(j) || eq) us = us + (us.length() > 0 ? "," : "") + mid;
    }
    if (us.length() > 0) b.append(';').append(id).append('=').append(us);
  }
  return b.toString();
}
"""
]


def _late_stub(src):''')
rep('''M(absave, r"""
public static synchronized boolean writeSync(String k) {''', '''# 0.1.26: the History copy of the ability tree update - abilities/<pkey>.properties -> history/abiltree2/<pkey>.properties, once. Fix round
# (critic A1 + B2): its OWN lock (HLOCK - never the AbilSave monitor, whose writes sleep / fsync: the world thread calls this), the bytes read
# once and written through a temp file, then checked (same length); an existing copy: see fix round 2 below. true = the
# copy is there and checked, or there is no abilities file to keep; false = it failed (logged, limited) - migInfo then answers null (waits)
# fix round 2 (critic: a stale History after a rollback + a second update): a copy byte-identical to the file is kept as it is; a DIFFERENT
# copy from an EARLIER server run is kept as <pkey>.properties.<millis> and a fresh copy written (the Undo = the state right before THIS
# update); a different copy from this run (an earlier try of the same waiting update) is refreshed in place - no pile-up
F(absave, "public static final Object HLOCK = new Object();")
F(absave, "public static final long T0 = System.currentTimeMillis();")   # fix round 2: this server run's start
M(absave, r"""
public static boolean histCopy0(String k) {
  java.nio.file.Path DIR = @PKG@.AbilStore.DIR;
  if (DIR == null || k == null) return false;
  try {
    java.nio.file.LinkOption[] no = new java.nio.file.LinkOption[0];
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    java.nio.file.Path h = DIR.getParent().resolve("history").resolve("abiltree2").resolve(k + ".properties");
    boolean src = java.nio.file.Files.exists(f, no);
    boolean hx = java.nio.file.Files.exists(h, no);
    if (hx && !java.nio.file.Files.isRegularFile(h, no)) { @PKG@.ClassCfg.warnLimited("the ability tree update cannot keep abilities/" + k + ".properties: history/abiltree2/" + k + ".properties is not a file (the update waits)"); return false; }
    if (!src) return true;
    byte[] b = java.nio.file.Files.readAllBytes(f);
    if (hx) {
      byte[] o = java.nio.file.Files.readAllBytes(h);
      if (java.util.Arrays.equals(o, b)) return true;
      if (o.length > 0 && java.nio.file.Files.getLastModifiedTime(h, no).toMillis() < T0 - 2000L) {
        java.nio.file.Path kept = h.resolveSibling(h.getFileName().toString() + "." + System.currentTimeMillis());
        java.nio.file.Files.move(h, kept, new java.nio.file.CopyOption[0]);
        @PKG@.ClassCfg.info("the ability tree update: an older History copy (from an earlier server run) is kept as history/abiltree2/" + String.valueOf(kept.getFileName()) + " - a fresh copy is made");
      }
    }
    java.nio.file.Files.createDirectories(h.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = h.resolveSibling(h.getFileName().toString() + ".tmp");
    java.nio.file.Files.write(tmp, b, new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, h, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    if (java.nio.file.Files.isRegularFile(h, no) && java.nio.file.Files.size(h) == (long) b.length) return true;
    @PKG@.ClassCfg.warnLimited("the ability tree update's History copy of abilities/" + k + ".properties is incomplete (the update waits)");
    return false;
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("the ability tree update could not copy abilities/" + k + ".properties into history/abiltree2 (the update waits): " + t); return false; }
}""")
M(absave, r"""
public static boolean histCopy(String k) {
  boolean r = false;
  synchronized (HLOCK) { r = histCopy0(k); }
  return r;
}""")
M(absave, r"""
public static synchronized boolean writeSync(String k) {''')

# ================================================================================================ fix round (critic C4): the Server Setup help texts
rep('''_r("abil.treeGate", "TREE_GATE", "bool", True, "", "", "", "abilk", "Abilities need their class tree node",
   "With class trees on, enable each ability (A1-A4) in /tree class. Off: class level only.")''',
    '''_r("abil.treeGate", "TREE_GATE", "bool", True, "", "", "", "abilk", "Abilities need their class tree node",
   "Class trees on: buy abilities and modifiers as nodes in /tree class. Off: class level only.")''')
rep('''_r("mods.unlock", "MOD_UNLOCK", "text", "2,4,6,8,10", "", "40", "", "abill", "Modifier unlock levels",
   "Ability level for each ability's 1st, 2nd ... 5th modifier.")''',
    '''_r("mods.unlock", "MOD_UNLOCK", "text", "2,4,6,8,10", "", "40", "", "abill", "Modifier unlock levels",
   "No class trees: ability level for each 1st-5th modifier. With trees, modifier nodes unlock them.")''')

# ================================================================================================ /cast list, the /cast page's alt toggle
rep('''    if (st.equals("locked")) tx = @PKG@.AbilDefs.owns(ai, lv, grant, pick) ? "enable it in your class tree (/tree class, node A" + lineOf(ai) + ")" : "unlocks at " + @PKG@.ClassDefs.SKILLS[ci] + " " + @PKG@.AbilDefs.unlock(@PKG@.AbilDefs.TIER[ai]);''',
    '''    if (st.equals("locked")) tx = @PKG@.AbilDefs.owns(ai, lv, grant, pick) ? "unlock it in your class tree (/tree class, node " + lineId(ai) + ")" : "unlocks at " + @PKG@.ClassDefs.SKILLS[ci] + " " + @PKG@.AbilDefs.unlock(@PKG@.AbilDefs.TIER[ai]);   // 0.1.26''')
rep('''    if (data.indexOf("abpick\\"") >= 0) {
      this.pending = -1;''', '''    if (data.indexOf("abpick\\"") >= 0) {
      this.pending = -1;
      if (@PKG@.Abil.treeOwnsPick(u)) { this.info = "Your Ability 1 alt is the A4 node you buy in your class tree (/tree class) - a class respec lets you pick the other one."; rebuild(); return; }   // 0.1.26''')
rep('''    if (data.indexOf("abyes\\"") >= 0) {
      if (!this.pick) return;
      this.pick = false;''', '''    if (data.indexOf("abyes\\"") >= 0) {
      if (!this.pick) return;
      this.pick = false;
      if (@PKG@.Abil.treeOwnsPick(u)) { this.info = "Your Ability 1 alt is the A4 node you buy in your class tree (/tree class)."; rebuild(); return; }   // 0.1.26''')

# ================================================================================================ bridges
rep('''abuf = pool.makeClass(PKG + ".AbilUnlockFn")''', '''# 0.1.26: class:fn:migInfo (SkyyTrees 0.3.13's one-time profile update) - String pkey -> String or null; any thread, never throws
abmi = pool.makeClass(PKG + ".AbilMigFn")
abmi.addInterface(pool.get("java.util.function.Function"))
C(abmi, "public AbilMigFn() { }")
M(abmi, r"""
public Object apply(Object o) {
  try {
    if (o == null) return null;
    return @PKG@.Abil.migInfo(String.valueOf(o).trim());
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("class:fn:migInfo failed: " + t); return null; }
}""")
abuf = pool.makeClass(PKG + ".AbilUnlockFn")''')
rep('''  b.put("class:fn:abilDo", new @PKG@.AbilDoFn());           // 0.1.22: ... swap / pick / equip / unequip (out of combat)''',
    '''  b.put("class:fn:abilDo", new @PKG@.AbilDoFn());           // 0.1.22: ... (0.1.26: hold / place / mod / clearMod / back / rbpick / attune; out of combat)
  b.put("class:fn:migInfo", new @PKG@.AbilMigFn());         // 0.1.26: SkyyTrees 0.3.13's one-time ability tree update (the alt + the usable modifiers)''')
rep('''  try { @PKG@.ClassCfg.bridge().remove("classes:fn:imbue"); } catch (Throwable t) { }       // 0.1.25''',
    '''  try { @PKG@.ClassCfg.bridge().remove("classes:fn:imbue"); } catch (Throwable t) { }       // 0.1.25
  try { @PKG@.ClassCfg.bridge().remove("class:fn:migInfo"); } catch (Throwable t) { }       // 0.1.26''')
rep('''          abimb):                        # 0.1.25: + classes:fn:imbue''', '''          abimb,                         # 0.1.25: + classes:fn:imbue
          abmi):                         # 0.1.26: + class:fn:migInfo''')

# ================================================================================================ checks on the result
assert s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0, "no command / system added"
assert "# @@" not in s and "class:fn:migInfo" in s
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.1.25 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.1.25 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
