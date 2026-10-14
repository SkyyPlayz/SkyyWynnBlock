"""Derive SkyyTrees/build_skyytrees_0.3.7.py from the LIVE generated SkyyTrees/build_skyytrees_0.3.6.py (the tools/deploy_set.py SET pin).
Run:  python tools/trees_0_3_7_patch.py   then   python SkyyTrees/build_skyytrees_0.3.7.py   (never --deploy: coordinated deploy)
      then python SkyyTrees/test_skyytrees_0.3.7.py --dir <tools/dev/scratch/<task>/...> (bare JVM)
EDITED-SCRIPTS RULE (commit ab75b6c): the lineage is Skyy's EDITED 0.2.3 -> trees_0_2_4_patch.py -> ... -> trees_0_3_6_patch.py -> the
generated 0.3.6 read here; tools/trees_0_2_3_patch.py and older are NEVER re-run. Edit THIS file, never the generated build script.

0.3.7 = THE ABILITY PANEL BESIDE THE CLASS TREE + THE REAL ABILITY NODES (Skyy 2026-10-14: "Link ability's to the ability buttons, and
enable the class skill trees. Add the ability controls and their modifiers to the skill trees, so you can enable, upgrade and customize
them in the skill trees right beside the skill tree." + popup "Panel on the right (Recommended)": a narrower tree grid, the ability panel
beside it - 2 primaries, 2 crouch alts, level, 2 modifier slots each; "Mage + Priest (Recommended)"). With SkyyClasses 0.1.22.
WHAT CHANGES (class tab only; the eight template trees are 0.3.6's byte for byte):
  - THE A / M NODES ARE REAL (page 1, ids unchanged): A1-A4 = ENABLE ability line 1-4 (Mage Meteor / Mana Barrier / Frost Nova / the
    Ability 1 alt = Starfall or Arcane Beam; Priest Sacred Heal / Shield Bubble / Guardian Spirit / Sanctuary or Martyr's Grace), M<n>A /
    M<n>B = that line's 2 MODIFIER SLOTS. They are kind K (class abilities): buyable once SkyyClasses lists them in tree:reads:SkyyClasses
    (0.1.22 lists Mage + Priest; the other classes keep "Comes with the class abilities"). An A node needs NO parent (it is reachable at
    once), only its line's class level (SkyyClasses class:fn:abilUnlock: abil.unlock.a1 / a2 / a2alt / a1alt, 1 / 10 / 20 / 30;
    built-in the same without SkyyClasses). FIX ROUND: every A / M node is FREE (0 AP - Skyy M8 "no need for another set of points";
    the class.nodes AP number of an A / M line is not read), so a player who spent every AP before 0.3.7 is never locked out of their
    abilities (no respec coins) and the 2 modifier slots of an enabled ability are two free clicks.
    The M nodes keep their parents (A -> MA -> MB). A / M nodes are never skipped (waiting) nodes. Their texts name the ability.
  - tree:fn:abil (NEW bridge, for SkyyClasses' gate): Function(UUID) -> String "A1,A2,M1A,T4=10,TS,..." = the player's INTACT class nodes
    (a switch only while ON; "=Amount" when the node's Amount is not 0), or null while class trees are off / the class has no tree / the
    tree file is unreadable (= no gate: SkyyClasses then unlocks by class level, as before).
  - THE CLASS TAB WINDOW is 1600 wide (the kit's widest; the template trees stay 1440): the graph is narrower (9 x 92 px slots, cells 88 x
    84, the state line 13 px), the rune strip's rune cells are gone (the pager stays), and the ABILITY PANEL (a 262 px well) sits between
    the graph and the detail well: your 4 abilities in key order (Primary on Ability 2 / Ability 3, the 2 alts on crouch + the key), each
    a card: the rune icon (click = its details), name + level, the key line, its 2 modifier slots (click = pick that slot) and two buttons:
    Swap (then Move here on another card = trade places; out of combat) and Enable (buys its A node) / Other alt (Starfall <-> Arcane Beam
    once you may choose) / Modifiers. NO tooltips (unproven) - the detail well shows the ability: level + uses to the next level + the
    gain, the selected slot, every modifier of the ability (unlock level, its own level + uses, what it does now and next) with Equip /
    Double / In slot / Taken / Locked, Unequip, and Tree node (back to the node details). Clicking a tree cell also goes back.
  - Every panel action goes through SkyyClasses (class:fn:abilDo / abilPanel / abilMods with this page's own node list, so a node bought a
    second ago counts at once); the probe page shows the panel but refuses its actions.
  - FIX ROUND: the probe page's panel reads the REAL player's tree (tree:fn:abil), so a probe never puts its fake nodes into SkyyClasses'
    1 s tree cache (the real gate + rune mirror).
  - Mage PA3 Phase Step's text = what SkyyClasses 0.1.22 applies (the dome moves with you at full strength, 10 s; the blink part waits).
  No new saved data, setting, command or migration.
  ROLLBACK 0.3.7 -> 0.3.6: safe - owned A / M nodes become "coming" slots again (their AP are not spent; a respec is not needed);
  SkyyClasses 0.1.22 then sees no tree:fn:abil = no gate.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.3.6.py")
dst = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.3.7.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
CR, LF = chr(13), chr(10)
s = raw.decode("utf8").replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.6"' in s and "GENERATED by tools/trees_0_3_6_patch.py from the LIVE build_skyytrees_0.3.5.py" in s, \
    "build_skyytrees_0.3.6.py is not the live 0.3.6 of the edited lineage"
assert "tree:fn:abil" not in s and "SkyyTrAp" not in s, "0.3.6 already has the 0.3.7 parts"
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
CHANGES = []


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:140])
    s = s.replace(old, new)
    CHANGES.append((new, old))


def rep_block(start, end, new):
    """replace s[start .. the end marker, inclusive] (both unique) with new"""
    global s
    assert s.count(start) == 1, "block start count %d: %s" % (s.count(start), start[:100])
    a = s.index(start)
    b = s.index(end, a)
    assert s.count(end, a) >= 1
    b = b + len(end)
    old = s[a:b]
    s = s[:a] + new + s[b:]
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.7 = THE ABILITY PANEL"):HEAD.index("  ROLLBACK 0.3.7")].rstrip()

# ================================================================================================================ header + version
rep('''"""SkyyTrees 0.3.6 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
GENERATED by tools/trees_0_3_6_patch.py from the LIVE build_skyytrees_0.3.5.py (the SET pin) - edit the patch, not this file. 0.3.5
was GENERATED''', '''"""SkyyTrees 0.3.7 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
GENERATED by tools/trees_0_3_7_patch.py from the LIVE build_skyytrees_0.3.6.py (the SET pin) - edit the patch, not this file. 0.3.6
was GENERATED by tools/trees_0_3_6_patch.py from the LIVE build_skyytrees_0.3.5.py. 0.3.5
was GENERATED''')
rep('''0.3.6 (2026-10-13; LIFELONG TOOL PERKS''', '''0.3.7 (2026-10-14; notes: tools/trees_0_3_7_patch.py) ''' + NOTE[len("0.3.7 = "):].replace(LF, LF + "    ") + '''
  CHECKED: SkyyTrees/test_skyytrees_0.3.7.py (bare JVM: class compare vs 0.3.6, -Xverify:all, the A / M node rules + tree:fn:abil + the
    panel build + every panel event EXECUTED with a stand-in SkyyClasses and with the real SkyyClasses 0.1.22, the access audit, start
    twice on a copy of the live data).

=== SkyyTrees 0.3.6 notes (history; still true unless 0.3.7 above says otherwise) ===
0.3.6 (2026-10-13; LIFELONG TOOL PERKS''')
rep('''Run:   python build_skyytrees_0.3.6.py            -> SkyyTrees/SkyyTrees-0.3.6.jar
       python build_skyytrees_0.3.6.py --deploy   -> also''', '''Run:   python build_skyytrees_0.3.7.py            -> SkyyTrees/SkyyTrees-0.3.7.jar
       python build_skyytrees_0.3.7.py --deploy   -> also''')
rep('VERSION = "0.3.6"', 'VERSION = "0.3.7"')

# ================================================================================================================ the A / M node texts
rep('''        elif role == 2:
            name, now = "Ability " + ROMAN[int(nid[1]) - 1], "Ability rune slot - coming with runes (Hytale 0.7)"
        else:
            name, now = "Modifier " + ROMAN[int(nid[1]) - 1] + "-" + nid[2], "Modifier rune slot - coming with runes (Hytale 0.7)"
''', '''        elif role == 2:   # 0.3.7: ENABLE ability line 1-4 (kind K: SkyyClasses applies it once it lists Class.<Class>.A<n>)
            kind = "K"
            ab = CABIL.get(cn)
            if ab:
                name, now = ab[int(nid[1]) - 1][0], ab[int(nid[1]) - 1][1]
                how = "Enables the ability on your keys (SkyyClasses applies it). Free (0 AP), no parent node - only its class level"
            else:
                name, now = "Ability " + ROMAN[int(nid[1]) - 1], "Ability line " + nid[1] + " - comes with this class's abilities"
        else:             # 0.3.7: modifier slot 1 / 2 of ability line n
            kind = "K"
            ab = CABIL.get(cn)
            ln_ = int(nid[1])
            if ab:
                name = ab[ln_ - 1][2] + " Mod " + ("I" if nid[2] == "A" else "II")
                now = "Opens modifier slot " + ("1" if nid[2] == "A" else "2") + " of " + ab[ln_ - 1][3] + " - equip modifiers in the panel"
                how = "Free (0 AP). Modifiers unlock with the ability's own level and level up by use. A stackable one can sit in both slots"
            else:
                name, now = "Modifier " + ROMAN[ln_ - 1] + "-" + nid[2], "Modifier slot - comes with this class's abilities"
''')
rep('''        elif role in (2, 3, 4): how = "Rune slot: with Hytale 0.7 you equip any 2 unlocked abilities at the bench (1 ability + 2 modifiers per line) - nothing to buy before"
''', '''        elif role in (2, 3, 4) and not how: how = "Comes with the class abilities: SkyyClasses lists Class.%s.%s when this class has them - until then it waits" % (cn, nid)
''')
# the ability lines of the classes SkyyClasses 0.1.22 builds (name, Gives text, short name for the M nodes, the name in the M text)
rep('''CPRIEST_TS = (''', '''CABIL = {   # 0.3.7: A1-A4 = ability lines 1-4 (SkyyClasses tiers 0 / 1 / 2 / 3-4): (node name, Gives, M node prefix, M text name)
 "Mage": [("Meteor", "Enables Meteor (ability line 1)", "Meteor", "Meteor"),
          ("Mana Barrier", "Enables Mana Barrier (ability line 2)", "Mana Barrier", "Mana Barrier"),
          ("Frost Nova", "Enables Frost Nova (ability line 3)", "Frost Nova", "Frost Nova"),
          ("Starfall or Beam", "Enables your Ability 1 alt: Starfall or Arcane Beam", "Ability 1 Alt", "your Ability 1 alt")],
 "Priest": [("Sacred Heal", "Enables Sacred Heal (ability line 1)", "Sacred Heal", "Sacred Heal"),
            ("Shield Bubble", "Enables Shield Bubble (ability line 2)", "Shield Bubble", "Shield Bubble"),
            ("Guardian Spirit", "Enables Guardian Spirit (ability line 3, a passive)", "Guardian Spirit", "Guardian Spirit"),
            ("Sanctuary or Grace", "Enables your Ability 1 alt: Sanctuary or Martyr's Grace", "Ability 1 Alt", "your Ability 1 alt")],
}
assert all(len(a[0]) <= 24 and len(a[2] + " Mod II") <= 24 for v in CABIL.values() for a in v)
CABIL_MIN = [1, 10, 20, 30]   # the built-in A1-A4 level gates (SkyyClasses' abil.unlock.* defaults) - class:fn:abilUnlock answers the live ones
CPRIEST_TS = (''')
rep('''   ("Phase Step", "K", 0, "Mana Barrier: blink 5 blocks back, the dome lands where you land - dome 10 s", None, None),''',
    '''   ("Phase Step", "K", 0, "Mana Barrier: the dome moves with you at full strength - dome 10 s", None, None),''')
rep('''    w_ = {1: "Passive - pick one of two", 2: "Ability rune slot", 3: "Modifier rune slot", 4: "Modifier rune slot", 5: "Trunk", 9: "Switch"}.get(r_, "Passive")''',
    '''    w_ = {1: "Passive - pick one of two", 2: "Ability line", 3: "Modifier slot", 4: "Modifier slot", 5: "Trunk", 9: "Switch"}.get(r_, "Passive")''')

# ================================================================================================================ TreeClass rules
# the coming SLOTS are only the elements now (the A / M nodes are kind K, gated by SkyyClasses listing them)
rep('''public static boolean slotComing(int n) {
  if (n < 0 || n >= NN) return false;
  int r = NROLE[n];
  return r == 2 || r == 3 || r == 4 || r == 7;
}''', '''public static boolean slotComing(int n) {
  if (n < 0 || n >= NN) return false;
  return NROLE[n] == 7;   // 0.3.7: the A / M nodes are real (kind K: SkyyClasses applies them)
}''')
# an ability line node / a modifier slot node is never a skipped (waiting) node
rep('''  if (ci < 0 || ci >= NC || n < 0 || n >= NN || slotComing(n) || hidden(ci, n)) return false;
  int k = CK[ci * NN + n];''', '''  if (ci < 0 || ci >= NC || n < 0 || n >= NN || slotComing(n) || hidden(ci, n)) return false;
  if (NROLE[n] >= 2 && NROLE[n] <= 4) return false;   // 0.3.7: ability lines + modifier slots are never passed through
  int k = CK[ci * NN + n];''')
# INTEGRITY: an owned ability line node (role 2) is a root of its own (no parent needed); its modifier slots hang from it
rep('''    for (int n = 0; n < NN; n++) { it[n] = false; ps[n] = false; }
    if (ok[0]) {
      it[0] = true;
      boolean ch = true;''', '''    for (int n = 0; n < NN; n++) { it[n] = false; ps[n] = false; }
    boolean seed = false;
    if (ok[0]) { it[0] = true; seed = true; }
    for (int n = 1; n < NN; n++) if (ok[n] && NROLE[n] == 2) { it[n] = true; seed = true; }   // 0.3.7: an ability line needs no parent
    if (seed) {
      boolean ch = true;''')
rep('''  boolean par = n == 0 || (p1 >= 0 && it[p1]) || (p2 >= 0 && it[p2]);''',
    '''  boolean par = n == 0 || NROLE[n] == 2 || (p1 >= 0 && it[p1]) || (p2 >= 0 && it[p2]);   // 0.3.7: an ability line needs no parent''')
# FIX ROUND (critics; Skyy M8 "no need for another set of points"): the A / M nodes are FREE - the class.nodes AP number of an ability
# line / modifier slot line is not read (a player who spent every AP before 0.3.7 is never locked out of their abilities)
rep('''    // 0.3.1 (Skyy 2026-10-03): a DELETED class.minLevel line''',
    '''    if (@PKG@.TreeClass.NROLE[nn] >= 2 && @PKG@.TreeClass.NROLE[nn] <= 4) {   // 0.3.7 fix round: the A / M nodes are free
      if (cap[j] != 0 && cap[j] != @PKG@.TreeClass.NAP[nn] && cv != null && cv.split(",", -1).length >= 3) { apIgn++; if (apIgnAt.length() == 0) apIgnAt = ck; }   // an admin's own price (not the old default)
      cap[j] = 0;
    }
    // 0.3.1 (Skyy 2026-10-03): a DELETED class.minLevel line''')
rep('''  return what + " - " + ap + " AP" + more;''', '''  return what + " - " + (ap == 0 ? "free" : ap + " AP") + more;   // 0.3.7 second fix round''')
rep('''assert "class.nodes.Archer.R4" not in DEFAULTS''', '''assert "class.nodes.Mage.A1=true,0,0\\n" in DEFAULTS and "class.nodes.Priest.M1B=true,0,0\\n" in DEFAULTS   # 0.3.7 second fix round
assert "class.nodes.Archer.R4" not in DEFAULTS''')
# SECOND FIX ROUND (critics: an admin's AP for an A / M node was ignored silently; Server Setup kept showing AP 1 / 2 for them):
# the default lines write 0, the row help says so, the entry check warns, and a load that ignores a non-0 AP logs it once
rep('''        out.append("class.nodes.%s.%s=true,%d,%d" % (cn, CT_ID[n], c["amt"], CT[n][1]))''',
    '''        out.append("class.nodes.%s.%s=true,%d,%d" % (cn, CT_ID[n], c["amt"], 0 if CT[n][10] in (2, 3, 4) else CT[n][1]))   # 0.3.7: A / M free''')
rep('''      "Entry = node id (ROOT, P1, T2, PA1 ...). On, the node's number and the AP cost. Removed = built-in.",''',
    '''      "Entry = node id (ROOT, P1, PA1 ...). On, number, AP cost (A / M nodes are free). Removed = built-in.",''')
rep('''  if (ap < 0L || ap > 10L) return "AP must be a whole number from 0 to 10 (the whole tree costs 64, players reach 50).";''',
    '''  if (ap < 0L || ap > 10L) return "AP must be a whole number from 0 to 10 (the whole tree costs 64, players reach 50).";
  if (ap != 0L && @PKG@.TreeClass.NROLE[n] >= 2 && @PKG@.TreeClass.NROLE[n] <= 4) return "?" + e + " is an ability / modifier slot node - those are always free, so this AP (" + ap + ") is ignored. Save it anyway?";   // 0.3.7''')
rep('''    F(cfg, "public static volatile %s;" % decl)
''', '''    F(cfg, "public static volatile %s;" % decl)
F(cfg, "public static volatile int AP_IGN = 0;")   # 0.3.7 second fix round: the last load's ignored A / M AP lines (logged when it changes)
''')
rep('''  int cnn = @PKG@.TreeClass.NC * @PKG@.TreeClass.NN;
  boolean[] con = new boolean[cnn];''', '''  int cnn = @PKG@.TreeClass.NC * @PKG@.TreeClass.NN;
  int apIgn = 0;   // 0.3.7 second fix round: non-0 AP lines of A / M nodes (ignored)
  String apIgnAt = "";
  boolean[] con = new boolean[cnn];''')
rep('''  // 0.3.3 fix 2: no class.nodes line of a pair new in 0.3.3''', '''  if (apIgn > 0 && apIgn != AP_IGN) info(apIgn + " class.nodes line(s) set their own AP cost on an A / M ability node (first: " + apIgnAt + ") - those nodes are always free (0.3.7), the AP is ignored.");
  AP_IGN = apIgn;
  // 0.3.3 fix 2: no class.nodes line of a pair new in 0.3.3''')
rep(""""int[] C_AP = " + jint([CT[c["n"]][1] for c in CN]),""",
    """"int[] C_AP = " + jint([0 if CT[c["n"]][10] in (2, 3, 4) else CT[c["n"]][1] for c in CN]),""")   # 0.3.7 fix round: the A / M nodes' built-in AP = 0 too
# ... and a 0 AP node reads "free" (the cell, the buy button, the Cost line; the Priest switch TS was 0 AP already)
rep('''  if (stt == 1) return cost <= 9 ? "Unlock " + cost + " AP" : "Unlock";''',
    '''  if (stt == 1) return cost == 0 ? "Unlock free" : (cost <= 9 ? "Unlock " + cost + " AP" : "Unlock");''')
rep('''  if (stt == 1) return "Unlock - " + cost + " AP";''', '''  if (stt == 1) return cost == 0 ? "Unlock - free" : "Unlock - " + cost + " AP";''')
rep('''  return "Cost: " + (ci < 0 ? @PKG@.TreeClass.NAP[n] : @PKG@.TreeCfg.C_AP[ci * @PKG@.TreeClass.NN + n]) + " AP";''',
    '''  int cap = ci < 0 ? @PKG@.TreeClass.NAP[n] : @PKG@.TreeCfg.C_AP[ci * @PKG@.TreeClass.NN + n];
  return cap == 0 ? "Cost: free" : "Cost: " + cap + " AP";''')
rep('''  int mn = @PKG@.TreeCfg.C_MIN[ci * NN + n];
  if ((lvl < 0 ? 0 : lvl) < mn) return 7;''', '''  int mn = minOf(ci, n);   // 0.3.7: an ability line also needs its class level (SkyyClasses abil.unlock.*)
  if ((lvl < 0 ? 0 : lvl) < mn) return 7;''')
rep('''  if (why == 7) return "Lv " + @PKG@.TreeCfg.C_MIN[ci * NN + n];''', '''  if (why == 7) return "Lv " + minOf(ci, n);''')
rep('''  if (why == 7) return nm + " needs " + CSKILL[ci] + " " + @PKG@.TreeCfg.C_MIN[ci * NN + n] + " (you are " + (lvl < 0 ? 0 : lvl) + ")";''',
    '''  if (why == 7) return nm + " needs " + CSKILL[ci] + " " + minOf(ci, n) + " (you are " + (lvl < 0 ? 0 : lvl) + ")";''')
# the level gate of a node: class.minLevel, and for an ability line the class level SkyyClasses unlocks that line at
rep('''# who still has to ship for node n of class ci ("" = live): rune slots and elements wait for their round; Strength for SkyyGear's reader''',
    '''# 0.3.7: an ability line's level gate = class:fn:abilUnlock (SkyyClasses abil.unlock.a1 / a2 / a2alt / a1alt), built-in 1 / 10 / 20 / 30
F(cls, "public static final int[] ABIL_MIN = %s;" % jint(CABIL_MIN))
M(cls, r"""
public static int abilMin(int n) {
  if (n < 0 || n >= NN || NROLE[n] != 2) return 0;
  int line = NID[n].charAt(1) - '0';
  if (line < 1 || line > 4) return 0;
  java.util.function.Function f = @PKG@.TreeCalc.fn("class:fn:abilUnlock");
  if (f != null) {
    try {
      Object r = f.apply(Integer.valueOf(line));
      if (r instanceof Number) { long v = ((Number) r).longValue(); return v < 0L ? 0 : (v > 1000L ? 1000 : (int) v); }
    } catch (Throwable t) { }
  }
  return ABIL_MIN[line - 1];
}""")
M(cls, r"""
public static int minOf(int ci, int n) {
  if (ci < 0 || ci >= NC || n < 0 || n >= NN) return 0;
  int m = @PKG@.TreeCfg.C_MIN[ci * NN + n];
  int a = abilMin(n);
  return a > m ? a : m;
}""")
# who still has to ship for node n of class ci ("" = live): rune slots and elements wait for their round; Strength for SkyyGear's reader''')

# ================================================================================================================ the node list + the panel bridges
rep('''# "Class.<Class>.<Id>" -> class * NN + node, or -1
''', '''# 0.3.7: the player's INTACT class nodes as one text "A1,A2,M1A,T4=10,TS" (a switch only while ON; "=Amount" when not 0) - SkyyClasses'
# ability gate (tree:fn:abil) and what this page hands to SkyyClasses' panel bridges (so a node bought a moment ago counts at once)
M(cls, r"""
public static String csvOf(@PKG@.TreeData d, boolean[] it, int ci) {
  if (d == null || it == null || ci < 0 || ci >= NC) return null;
  StringBuilder b = new StringBuilder();
  for (int n = 0; n < NN; n++) {
    if (!it[n] || hidden(ci, n)) continue;
    if (isSwitch(n) && !switchOn(d, it, ci, n)) continue;
    if (b.length() > 0) b.append(',');
    b.append(NID[n]);
    int a = @PKG@.TreeCfg.C_AMT[ci * NN + n];
    if (a != 0) b.append('=').append(a);
  }
  return b.toString();
}""")
# tree:fn:abil: null = no gate (class trees off, no class tree, an unreadable tree file)
M(cls, r"""
public static String abilCsv(java.util.UUID u) {
  if (u == null || !@PKG@.TreeCfg.CLASS_ON) return null;
  int ci = classIdx(classOf(u));
  if (ci < 0) return null;
  @PKG@.TreeData d = @PKG@.TreeStore.data(u);
  if (d == null || d.bad) return null;
  return csvOf(d, intact(d, ci), ci);
}""")
# SECOND FIX ROUND (critic: fail-open): tree:fn:abil answers "!err" when the tree data could not be read (missing / bad file, a throw),
# so SkyyClasses keeps its last good answer instead of reading null = "no gate" (every ability enabled)
M(cls, r"""
public static String abilGate(java.util.UUID u) {
  if (u == null || !@PKG@.TreeCfg.CLASS_ON) return null;
  int ci = classIdx(classOf(u));
  if (ci < 0) return null;
  @PKG@.TreeData d = @PKG@.TreeStore.data(u);
  if (d == null || d.bad) return "!err";
  return csvOf(d, intact(d, ci), ci);
}""")
# SkyyClasses 0.1.22's panel bridges (never throw; null = no SkyyClasses / no answer)
M(cls, r"""
public static Object[] apanel(java.util.UUID u, String csv) {
  java.util.function.Function f = @PKG@.TreeCalc.fn("class:fn:abilPanel");
  if (f == null || u == null) return null;
  try {
    Object r = f.apply(new Object[] { u, csv });
    if (r instanceof Object[]) return (Object[]) r;
    return null;
  } catch (Throwable t) { return null; }
}""")
M(cls, r"""
public static String[] amods(java.util.UUID u, String id, String csv) {
  java.util.function.Function f = @PKG@.TreeCalc.fn("class:fn:abilMods");
  if (f == null || u == null || id == null || id.length() == 0) return null;
  try {
    Object r = f.apply(new Object[] { u, id, csv });
    if (r instanceof String[]) return (String[]) r;
    return null;
  } catch (Throwable t) { return null; }
}""")
M(cls, r"""
public static String ado(java.util.UUID u, String act, String a, String b, String csv) {
  java.util.function.Function f = @PKG@.TreeCalc.fn("class:fn:abilDo");
  if (f == null) return "-SkyyClasses is not loaded - abilities cannot change here.";
  try {
    Object r = f.apply(new Object[] { u, act, a, b, csv });
    return r == null ? "-SkyyClasses did not answer - nothing changed." : String.valueOf(r);
  } catch (Throwable t) { return "-SkyyClasses could not do that right now - nothing changed."; }
}""")
# the panel's message when SkyyClasses has nothing to show
M(cls, r"""
public static String apanelMsg(Object[] ap, int ci, String ucls) {
  if (ci < 0) return ucls != null ? "Your class " + ucls + " has no abilities here yet." : "Choose a class to see your abilities here.";
  if (ap == null) return "Your " + CLASSES[ci] + " abilities show here with SkyyClasses 0.1.22 (it is not loaded or did not answer).";
  String st = String.valueOf(ap[0]);
  if ("noabil".equals(st)) return CLASSES[ci] + " abilities come in a later build - the Mage and the Priest have theirs first.";
  if ("noclass".equals(st)) return "Choose a class to see your abilities here.";
  if ("off".equals(st)) return "Class abilities are switched off on this server.";
  return "";
}""")
# "Power" -> one panel text field: the slot j (0 / 1) of card i
M(cls, r"""
public static String slotText(Object[] ap, int i, int j, int line) {
  int b0 = 12 + i * 16;
  int slots = ((Integer) ap[b0 + 14]).intValue();
  if (j >= slots) return "Tree: M" + line + (j == 0 ? "A" : "B");
  String m = String.valueOf(ap[b0 + 10 + j * 2]);
  if (m.length() == 0) return "Empty slot " + (j + 1);
  return m + " " + ((Integer) ap[b0 + 11 + j * 2]).intValue();
}""")
M(cls, r"""
public static String keyText(Object[] ap, int i, int ci) {
  int b0 = 12 + i * 16;
  boolean own = Boolean.TRUE.equals(ap[b0 + 3]);
  boolean en = Boolean.TRUE.equals(ap[b0 + 4]);
  int line = ((Integer) ap[b0 + 5]).intValue();
  String key = i == 0 ? "Primary - Ability 2 key" : (i == 1 ? "Primary - Ability 3 key" : (i == 2 ? "Alt - crouch + Ability 2" : "Alt - crouch + Ability 3"));
  if (!own) {
    String[] ul = String.valueOf(ap[7]).split(",");
    String lv = line >= 1 && line <= ul.length ? ul[line - 1] : "?";
    return "Unlocks at " + CSKILL[ci] + " " + lv;
  }
  if (!en) return "Enable it: tree node A" + line;
  if ("passive".equals(String.valueOf(ap[b0 + 15]))) return "Passive - always on";
  return key;
}""")
M(cls, r"""
public static String nameText(Object[] ap, int i) {
  int b0 = 12 + i * 16;
  String nm = String.valueOf(ap[b0 + 1]);
  if (nm.length() == 0) return "-";
  boolean own = Boolean.TRUE.equals(ap[b0 + 3]);
  return own && Boolean.TRUE.equals(ap[8]) ? nm + "  Lv " + ((Integer) ap[b0 + 6]).intValue() : nm;
}""")
# "Class.<Class>.<Id>" -> class * NN + node, or -1
''')
# TreeAbilFn = tree:fn:abil (any thread, never throws)
rep('''tfn = pool.makeClass(PKG + ".TreeFn")
''', '''tfn = pool.makeClass(PKG + ".TreeFn")
afn = pool.makeClass(PKG + ".TreeAbilFn")   # 0.3.7: tree:fn:abil (SkyyClasses' ability gate)
''')
rep('''bfn.addInterface(pool.get("java.util.function.Function"))
''', '''bfn.addInterface(pool.get("java.util.function.Function"))
afn.addInterface(pool.get("java.util.function.Function"))
C(afn, "public TreeAbilFn() { }")
M(afn, r"""
public Object apply(Object o) {
  if (!(o instanceof java.util.UUID)) return null;
  try { return @PKG@.TreeClass.abilGate((java.util.UUID) o); } catch (Throwable t) { return "!err"; }   // second fix round: "!err" = keep the last
}""")
''')
rep('''F(sto, "public static Object BFN;")
''', '''F(sto, "public static Object BFN;")
F(sto, "public static Object AFN;")   # 0.3.7: tree:fn:abil
''')
rep('''  b.put("tree:fn:bonus", @PKG@.TreeStore.BFN);
''', '''  b.put("tree:fn:bonus", @PKG@.TreeStore.BFN);
  @PKG@.TreeStore.AFN = new @PKG@.TreeAbilFn();
  b.put("tree:fn:abil", @PKG@.TreeStore.AFN);   // 0.3.7: SkyyClasses 0.1.22 - the intact class nodes (its ability gate)
''')
rep('''    if (@PKG@.TreeStore.BFN != null) b.remove("tree:fn:bonus", @PKG@.TreeStore.BFN);
''', '''    if (@PKG@.TreeStore.BFN != null) b.remove("tree:fn:bonus", @PKG@.TreeStore.BFN);
    if (@PKG@.TreeStore.AFN != null) b.remove("tree:fn:abil", @PKG@.TreeStore.AFN);   // 0.3.7
''')
rep('''ALL = (defs, cfg, dat, sto, stk, calc, cls, fx, swg, msg, abil, gat, tfn, bfn, ffn,''', '''ALL = (defs, cfg, dat, sto, stk, calc, cls, fx, swg, msg, abil, gat, tfn, afn, bfn, ffn,''')
# the detail type line names the new node roles
rep('''  else if (r == 2) what = "Ability rune slot";
  else if (r == 3 || r == 4) what = "Modifier rune slot";''', '''  else if (r == 2) what = "Ability line";
  else if (r == 3 || r == 4) what = "Modifier slot";''')

# ================================================================================================================ the class tab (page)
# the cell's state line: 13 px bold in an 86 px line (the narrower 0.3.7 cells)
rep('''    assert SUI.text_width(_tx, 15, True) <= 96, (_tx, SUI.text_width(_tx, 15, True))''',
    '''    assert SUI.text_width(_tx, 13, True) <= 86, (_tx, SUI.text_width(_tx, 13, True))   # 0.3.7: 13 px in the 86 px state line''')
rep_block('''TRC_SLOT_W, TRC_SLOT_H = 104, 88''', '''    return java, marks
''', r'''TRC_SLOT_W, TRC_SLOT_H = 92, 88                  # 0.3.7: a graph slot = the 88 x 84 cell + its 4 px gaps right and below (was 104: the panel needs room)
TRC_CELL_W, TRC_CELL_H, TRC_ICON, TRC_ICON_L = 88, 84, 44, 22
TRC_BAR = 6                                      # the connector bar thickness (spec 10)
TRC_BAR_X = (TRC_CELL_W - TRC_BAR) // 2          # 41: a vertical bar's left edge
TRC_BAR_Y = (TRC_CELL_H - TRC_BAR) // 2          # 39: a horizontal bar's top edge
TRC_STRIP_H, TRC_STRIP_GAP = 64, 8               # the pager strip and the gap under it
TRC_PG_W, TRC_RS_GAP = 196, 24
TRC_BAR_COL, TRC_GOLD = "disabled", "gold"       # grey #797b7c, gold #E8A93B (kit colours)
TRC_SB_W, TRC_SB_H, TRC_SB_L, TRC_SB_T, TRC_SB_SIZE = 86, 20, 1, 64, 13   # the cell's one state line (13 px bold) under the 44 px icon
TRC_GRID_W = 2 * SUI.WELL_LIST_PAD + 9 * TRC_SLOT_W                       # 836
TRC_RSL_W = TRC_GRID_W - 2 * SUI.WELL_LIST_PAD - TRC_PG_W - TRC_RS_GAP     # the page caption left of the pager
# 0.3.7 THE ABILITY PANEL (Skyy "Panel on the right"): a well between the graph and the detail well
TRC_AP_W, TRC_AP_GAP = 262, 12
TRC_AP_IN_W = TRC_AP_W - 2 * SUI.WELL_PAD                                   # 246
TRC_CARD_PAD, TRC_CARD_GAP, TRC_CARD_ROW = 4, 4, 4
TRC_CARD_IN_W = TRC_AP_IN_W - 2 * TRC_CARD_PAD                              # 238
TRC_CARD_ICON = 44
TRC_CARD_TXT_W = TRC_CARD_IN_W - TRC_CARD_ICON - 6                          # 188
TRC_CARD_BTN_W = (TRC_CARD_IN_W - 4) // 2                                   # 117
TRC_CARD_H = 2 * TRC_CARD_PAD + TRC_CARD_ICON + 2 * (TRC_CARD_ROW + SUI.BTN_SMALL_H)   # 124
TRC_AP_TITLE_H, TRC_AP_HINT_H = 28, 40
TRC_W = TRC_GRID_W + TRC_AP_GAP + TRC_AP_W + TR_DET_GAP + TR_DET_W + 2 * SUI.CONTENT_PAD
assert TRC_W <= 1600, TRC_W                                                  # the kit's widest page (the class tab only; the trees stay 1440)
assert SUI.fit([TRC_AP_TITLE_H, TRC_AP_HINT_H + 6] + [TRC_CARD_H + TRC_CARD_GAP] * 4, TR_GRID_H - 2 * SUI.WELL_PAD, "ability panel") >= 0
TRC_AP_NO_H = TR_GRID_H - 2 * SUI.WELL_PAD - TRC_AP_TITLE_H - TRC_AP_HINT_H - 6
TRC_LVL_W = TRC_W - 2 * SUI.CONTENT_PAD - len(TR_TAB_ROWS[0]) * TR_TAB_W - (len(TR_TAB_ROWS[0]) - 1) * TR_TAB_GAP
TRC_NOTE_W = TRC_W - 2 * SUI.CONTENT_PAD - TR_TOK_W - TR_DUST_W
TRC_AD_BTN_W = 112                                                            # the ability detail: a modifier row = text + one small button
TRC_AD_TXT_W = TR_DET_IN_W - TRC_AD_BTN_W - 8
TRC_AD_ROW_H = 44
assert 9 * TRC_SLOT_W == TRC_GRID_W - 2 * SUI.WELL_LIST_PAD and TRC_STRIP_H + TRC_STRIP_GAP + 6 * TRC_SLOT_H == TR_GRID_H - 2 * SUI.WELL_LIST_PAD
assert (TRC_CELL_H - TRC_ICON) // 2 + TRC_ICON <= TRC_SB_T and TRC_SB_T + TRC_SB_H <= TRC_CELL_H and TRC_SB_L + TRC_SB_W <= TRC_CELL_W
assert 44 + 8 + 92 + 8 + 44 == TRC_PG_W and TRC_BAR_X + TRC_BAR + TRC_BAR_X == TRC_CELL_W and TRC_BAR_Y + TRC_BAR + TRC_BAR_Y == TRC_CELL_H
assert TRC_CARD_ICON + 6 + TRC_CARD_TXT_W == TRC_CARD_IN_W and 2 * TRC_CARD_BTN_W + 4 <= TRC_CARD_IN_W
for _t in ("Cancel", "Move here", "Swap", "Locked", "Enable", "Other alt", "Modifiers"):
    assert SUI.text_width(_t, 14, True, upper=True) + 2 * SUI.BTN_SMALL_PAD <= TRC_CARD_BTN_W, _t
for _t in ("Equip", "Double", "In slot", "Taken", "Locked"):
    assert SUI.text_width(_t, 14, True, upper=True) + 2 * SUI.BTN_SMALL_PAD <= TRC_AD_BTN_W, _t
for _t in ("Primary - Ability 3 key", "Alt - crouch + Ability 3", "Enable it: tree node A4", "Unlocks at Divinity 100", "Passive - always on"):
    assert SUI.text_width(_t, 15, False) <= TRC_CARD_TXT_W, _t
for _t in ("Knockback+ 5", "Efficiency 5", "Tree: M4B", "Empty slot 2"):
    assert SUI.text_width("> " + _t, 13, True) <= TRC_CARD_BTN_W - 8, _t
TRC_NEW_IDS = ["SkyyTrNoClass", "SkyyTrRs", "SkyyTrRsL", "SkyyTrPgG", "SkyyTrPgR", "SkyyTrPgP", "SkyyTrPgL", "SkyyTrPgN", "SkyyTrCR0",
               "SkyyTrCS0", "SkyyTrCA0", "SkyyTrC1", "SkyyTrC1Ic", "SkyyTrC1Sb", "SkyyTrCM0", "SkyyTrCU0", "SkyyTrCJ0", "SkyyTrCD0",
               "SkyyTrCG0", "SkyyTrCB0", "SkyyTrUndo",
               # 0.3.7 the ability panel + the ability detail
               "SkyyTrAp", "SkyyTrApT", "SkyyTrApH", "SkyyTrApNo", "SkyyTrAc0", "SkyyTrAa0", "SkyyTrAi0", "SkyyTrAx0", "SkyyTrAn0",
               "SkyyTrAk0", "SkyyTrAm0", "SkyyTrAsa0", "SkyyTrAla0", "SkyyTrAsb0", "SkyyTrAlb0", "SkyyTrAb0", "SkyyTrAw0", "SkyyTrAe0",
               "SkyyTrAdTop", "SkyyTrAdFrame", "SkyyTrAdIcon", "SkyyTrAdN", "SkyyTrAdS", "SkyyTrAdG", "SkyyTrAdM", "SkyyTrAr0", "SkyyTrAt0",
               "SkyyTrAq0", "SkyyTrAdH", "SkyyTrAdB", "SkyyTrAu", "SkyyTrAv", "SkyyTrTab8"]
assert not set(TRC_NEW_IDS) & set(TR_OLD_IDS) and all(SUI.check_id(_i) for _i in TRC_NEW_IDS) and len(set(TRC_NEW_IDS)) == len(TRC_NEW_IDS)

TRC_BUILD = r"""
public void buildClass(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  int t = @PKG@.TreeDefs.NT;
  int nt = t + 1;
  boolean pb = this.probe;
  int ci = pb ? this.pci : @PKG@.TreeClass.classIdx(@PKG@.TreeClass.classOf(u));
  if (ci >= @PKG@.TreeClass.NC) ci = -1;
  String ucls = (pb || ci >= 0) ? null : @PKG@.TreeClass.classOf(u);   // 0.3 fix H: a class this build has no tree for (Assassin, Shaman)
  if (ucls != null && ucls.length() > 20) ucls = ucls.substring(0, 20);
  @PKG@.TreeData d = (pb && this.pd != null) ? this.pd : @PKG@.TreeStore.data(u);
  int lvl = pb ? @PKG@.TreeClassOps.PROBE_LVL : @PKG@.TreeClass.level(u, ci);
  boolean[] own = @PKG@.TreeClass.ownOf(d, ci);
  boolean[] it = @PKG@.TreeClass.intact(d, ci);
  int apAll = ci < 0 ? 0 : @PKG@.TreeClass.ap(lvl < 0 ? 0 : lvl);
  int spent = @PKG@.TreeClass.spent(it, ci);
  int apFree = apAll - spent;
  int cp = this.cpage;
  if (cp < 0 || cp > 1) cp = 0;
  int sel = this.csel;
  if (sel < 0 || sel >= @PKG@.TreeClass.NN) sel = 0;
  if (@PKG@.TreeClass.NPAGE[sel] != cp) sel = @PKG@.TreeClass.firstOf(cp);
  int[] cst = @PKG@.TreeClass.states(own, it, ci, lvl, apFree);
  boolean[] pg = @PKG@.TreeClass.pieceGold(cp, @PKG@.TreeClass.lit(own, it, ci));   // 0.3.1: gold through a skipped node a chain uses
  int st0 = ci < 0 ? 0 : cst[sel];
  String tn = ci < 0 ? "Class" : @PKG@.TreeClass.CLASSES[ci];
  String col = ci < 0 ? @PKG@.TreeDefs.TCOLOR[0] : @PKG@.TreeClass.CCOLOR[ci];
  boolean canUndo = ci >= 0 && (pb || @PKG@.TreeCfg.C_UNDO) && this.undo != null && this.undo.size() > 0;
  boolean freeR = @PKG@.TreeClassOps.freeOf(d, ci, pb);   // 0.3.3: the free respec of the class paths update
  long price = (ci < 0 || lvl < 0 || pb || freeR) ? 0L : @PKG@.TreeClass.respecPrice(lvl);
  boolean sw = ci >= 0 && st0 == 2 && @PKG@.TreeClass.isSwitch(sel);   // 0.3.3: an owned switch - the buy button is Switch
  // 0.3.7: the ability panel's data (SkyyClasses 0.1.22 class:fn:abilPanel with THIS page's node list) and the ability detail
  String acsv = ci < 0 ? null : (pb ? @PKG@.TreeClass.abilCsv(u) : @PKG@.TreeClass.csvOf(d, it, ci));   // fix round: probe = the real tree
  Object[] ap = null;
  if (ci >= 0) ap = @PKG@.TreeClass.apanel(u, acsv);
  boolean apOk = ap != null && ap.length >= 78 && "ok".equals(ap[0]);
  int asl = this.aslot;
  if (asl < 0 || asl > 3) asl = 0;
  int msl = this.mslot;
  if (msl < 0 || msl > 1) msl = 0;
  boolean am = this.amode && apOk && String.valueOf(ap[12 + asl * 16]).length() > 0;
  String[] amr = null;
  if (am) amr = @PKG@.TreeClass.amods(u, String.valueOf(ap[12 + asl * 16]), acsv);
  if (amr == null || amr.length < 1) am = false;
  String[] ah = new String[0];
  if (am) ah = amr[0].split("\\|", -1);
  if (am && ah.length < 10) am = false;
  boolean canPick = apOk && Boolean.TRUE.equals(ap[5]);
{{SHELL}}
{{HEAD}}
  for (int i = 0; i < nt; i++) {
{{TAB}}
    ev.addEventBinding(@BT@.Activating, "#SkyyTrTab" + i, @EVD@.of("a", "trtab" + i));
  }
{{INFO}}
  b.set("#SkyyTrLvl.Text", (lvl < 0 && !pb) ? "SkyySkills missing" : (ci < 0 ? (ucls != null ? ucls + " - no tree yet" : "No class yet") : @PKG@.TreeClass.CSKILL[ci] + " " + lvl));
  b.set("#SkyyTrTok.Text", "Ability Points " + apFree + " of " + apAll);
  b.set("#SkyyTrDust.Text", pb ? "Respec free (probe)" : (freeR ? "Respec free (once)" : (price > 0L ? "Respec " + @PKG@.TreeDefs.grp(price) + " coins" : "Respec free")));
  b.set("#SkyyTrNote.Text", @PKG@.TreeClassOps.note(ci, lvl, it, apFree, pb, d.bad, ucls));
{{GRID}}
  if (ci < 0) {
{{NOCLASS}}
    b.set("#SkyyTrNoClass.Text", ucls != null ? "Your class " + ucls + " has no skill tree yet - it comes in a later build." : "Choose a class with /class - or create a profile - and your class tree opens here. Page 1 is your stat spine and ability nodes, page 2 the trunk and three paths (the first path node you unlock picks your path).");
  } else {
{{STRIP}}
    b.set("#SkyyTrRsL.Text", cp == 0 ? "Page 1 - stats, ability lines and modifier slots" : "Page 2 - trunk and paths (pick one path)");
    b.set("#SkyyTrPgL.Text", "Page " + (cp + 1) + " of 2");
    ev.addEventBinding(@BT@.Activating, "#SkyyTrPgP", @EVD@.of("a", "trpgp"));
    ev.addEventBinding(@BT@.Activating, "#SkyyTrPgN", @EVD@.of("a", "trpgn"));
    int base = cp * @PKG@.TreeClass.NSLOT;
    for (int r = 0; r < 6; r++) {
{{CROW}}
      for (int c = 0; c < 9; c++) {
        int k = r * 9 + c;
        int q = k * 8;
        int sk = @PKG@.TreeClass.SK[base + k];
        int n = @PKG@.TreeClass.SN[base + k];
        int arms = @PKG@.TreeClass.SARMS[base + k];
        if (sk == 1 && @PKG@.TreeClass.hidden(ci, n)) sk = 0;   // 0.3.3: the switch slot of a class without one stays empty
{{SLOT}}
        if (sk == 0) continue;
{{ROWA}}
        if (sk == 1) {
{{CELL}}
          b.set("#SkyyTrC" + (n + 1) + "Sb.Text", @PKG@.TreeClass.cardText2(d, own, it, ci, n, lvl, apFree, cst[n]));
          ev.addEventBinding(@BT@.Activating, "#SkyyTrC" + (n + 1), @EVD@.of("a", "trc" + (n + 1)));
        } else if (sk == 2) {
{{HBAR}}
        } else if (sk == 3) {
{{VBAR}}
        } else {
{{JUNC}}
        }
{{GAPR}}
{{ROWB}}
      }
    }
  }
{{APANEL}}
  if (!apOk) {
{{APNO}}
    b.set("#SkyyTrApNo.Text", @PKG@.TreeClass.apanelMsg(ap, ci, ucls));
  } else {
    b.set("#SkyyTrApH.Text", String.valueOf(ap[10]) + (pb ? " (probe: view only)" : ""));
    for (int i = 0; i < 4; i++) {
      int b0 = 12 + i * 16;
      boolean aown = Boolean.TRUE.equals(ap[b0 + 3]);
      boolean aen = Boolean.TRUE.equals(ap[b0 + 4]);
      int aline = ((Integer) ap[b0 + 5]).intValue();
      boolean selA = am && asl == i;
      String ricon = String.valueOf(ap[b0 + 2]);
      String aicon = ricon.length() > 0 ? ricon : @PKG@.TreeClass.CICON[ci];
      int aact = !aown ? 0 : (!aen ? 1 : (aline == 4 && canPick ? 2 : 3));
{{ACARD}}
      b.set("#SkyyTrAn" + i + ".Text", @PKG@.TreeClass.nameText(ap, i));
      b.set("#SkyyTrAk" + i + ".Text", @PKG@.TreeClass.keyText(ap, i, ci));
      b.set("#SkyyTrAla" + i + ".Text", (am && asl == i && msl == 0 ? "> " : "") + @PKG@.TreeClass.slotText(ap, i, 0, aline));
      b.set("#SkyyTrAlb" + i + ".Text", (am && asl == i && msl == 1 ? "> " : "") + @PKG@.TreeClass.slotText(ap, i, 1, aline));
      ev.addEventBinding(@BT@.Activating, "#SkyyTrAi" + i, @EVD@.of("a", "trab" + i));
      ev.addEventBinding(@BT@.Activating, "#SkyyTrAsa" + i, @EVD@.of("a", "trmsa" + i));
      ev.addEventBinding(@BT@.Activating, "#SkyyTrAsb" + i, @EVD@.of("a", "trmsb" + i));
      ev.addEventBinding(@BT@.Activating, "#SkyyTrAw" + i, @EVD@.of("a", "trsw" + i));
      if (aact > 0) ev.addEventBinding(@BT@.Activating, "#SkyyTrAe" + i, @EVD@.of("a", "tren" + i));
    }
  }
{{DETP}}
  if (!am) {
{{DET}}
    b.set("#SkyyTrDetName.Text", ci < 0 ? @PKG@.TreeClass.NID[sel] : @PKG@.TreeClass.name(ci, sel) + "  (" + @PKG@.TreeClass.NID[sel] + ")");   // 0.3 fix H: never "ROOT  (ROOT)"
    b.set("#SkyyTrDetState.Text", @PKG@.TreeClassOps.stateLine(d, it, st0, ci, sel));
    b.set("#SkyyTrDetNow.Text", @PKG@.TreeClassOps.nowLine(d, it, st0, ci, sel));
    b.set("#SkyyTrDetNext.Text", (ci < 0 ? "" : @PKG@.TreeClassOps.givesLine(ci, sel) + " - ") + @PKG@.TreeClassOps.typeLine(ci, sel));
    b.set("#SkyyTrDetCost.Text", @PKG@.TreeClassOps.costLine(st0, ci, sel));
    b.set("#SkyyTrDetNeed.Text", @PKG@.TreeClassOps.needLine(own, it, ci, sel, lvl, apFree, st0));
    b.set("#SkyyTrDetHow.Text", @PKG@.TreeClassOps.howLine(ci, sel));
{{BUY}}
    b.set("#SkyyTrBuyTx.Text", safe(@PKG@.TreeClassOps.buyText(d, own, it, ci, sel, lvl, apFree, st0)));
    ev.addEventBinding(@BT@.Activating, "#SkyyTrBuy", @EVD@.of("a", "trbuy"));
    ev.addEventBinding(@BT@.Activating, "#SkyyTrUndo", @EVD@.of("a", "trundo"));
  } else {
    int ab0 = 12 + asl * 16;
    String ricon2 = String.valueOf(ap[ab0 + 2]);
    String aicon2 = ricon2.length() > 0 ? ricon2 : @PKG@.TreeClass.CICON[ci];
    int aslots = 0;
    try { aslots = Integer.parseInt(ah[6]); } catch (Throwable x) { aslots = 0; }
    String e0 = ah[7];
    String e1 = ah[8];
    String cur = msl == 0 ? e0 : e1;
    boolean slotOpen = msl < aslots;
{{ADET}}
    b.set("#SkyyTrAdN.Text", ah[1] + "  -  " + ah[4]);
    b.set("#SkyyTrAdS.Text", "Level " + ah[2] + ": " + ah[9]);
    b.set("#SkyyTrAdG.Text", @PKG@.TreeClass.keyText(ap, asl, ci) + ". Uses count when it hits or heals (one per 3 s).");
    b.set("#SkyyTrAdM.Text", slotOpen ? "Modifier slot " + (msl + 1) + (cur.length() > 0 ? " - now " + cur : " - empty") : "Modifier slot " + (msl + 1) + " - unlock M" + ((Integer) ap[ab0 + 5]).intValue() + (msl == 0 ? "A" : "B") + " in the tree");
    for (int k = 0; k < amr.length - 1 && k < 5; k++) {
      String[] f = amr[k + 1].split("\\|", -1);
      if (f.length < 12) continue;
      boolean un = "1".equals(f[3]);
      boolean inThis = f[0].equals(cur);
      boolean inOther = f[0].equals(msl == 0 ? e1 : e0);
      int rs = (!slotOpen || !un) ? 0 : (inThis ? 1 : (inOther && "1".equals(f[11]) ? 2 : (inOther ? 3 : 4)));
{{AROW}}
      b.set("#SkyyTrAt" + k + ".Text", f[1] + (un ? " Lv " + f[4] + " - " + f[9] + ". Next: " + f[10] : " - " + f[9] + ". It gives: " + f[10]));
      if (rs == 2 || rs == 4) ev.addEventBinding(@BT@.Activating, "#SkyyTrAq" + k, @EVD@.of("a", "trme" + k));
    }
    b.set("#SkyyTrAdH.Text", "Modifiers unlock with the ability's own level and level up while equipped (each counted use). A stackable one can sit in both slots from its Lv 2 (double effect). Swap out of combat.");
    ev.addEventBinding(@BT@.Activating, "#SkyyTrAu", @EVD@.of("a", "trmu"));
    ev.addEventBinding(@BT@.Activating, "#SkyyTrAv", @EVD@.of("a", "trtree"));
  }
{{FOOT}}
  b.set("#SkyyTrMsg.Text", this.msg == null ? "" : this.msg);
  ev.addEventBinding(@BT@.Activating, "#SkyyTrBack", @EVD@.of("a", "trback"));
  boolean armed = this.armT == t && System.currentTimeMillis() - this.armAt <= 10000L;
{{RESPEC}}
  ev.addEventBinding(@BT@.Activating, "#SkyyTrRespec", @EVD@.of("a", "trrespec"));
}"""


def class_page_java():
    """TreePage.buildClass(): TRC_BUILD with its {{parts}} from kit calls (every markup recorded for assert_proven). 0.3.7: a 1600 wide
    window, the narrower graph, the ability panel, the ability detail."""
    sh = SUI.page_shell("SkyyTrF", TRC_W, TR_H, "Skill Trees", kind="plain", body_id="SkyyTrRoot")
    body, W = sh.body, sh.inner_w
    marks = list(sh.appends.markups())

    def app(parent, markup):
        marks.append(markup)
        return SUI.java_append(parent, markup)

    def chain(conds, parent, markups):
        out = []
        for n_, mk in enumerate(markups):
            head = ("if (%s) " % conds[n_]) if n_ == 0 else (("else if (%s) " % conds[n_]) if n_ < len(conds) else "else ")
            out.append(head + app(parent, mk))
        return "\n".join(out)

    r, k, nn = SUI.J("r", "0"), SUI.J("k", "0"), SUI.J("n + 1", "1")
    i = SUI.J("i", "0")
    # ---- the tab rows: the template tabs (Secondary here: t == NT) + the class tab chain (Primary)
    tab_java = []
    for n_, name in enumerate(TREES):
        _row = TR_TAB_ROW_OF[n_]
        anc = None if TR_TAB_ROWS[_row][0] == n_ else {"left": TR_TAB_GAP}
        mk = SUI.choose(SUI.J("i == t"), SUI.button("SkyyTrTab%d" % n_, name, "primary", w=TR_TAB_W, anchor=anc),
                        SUI.button("SkyyTrTab%d" % n_, name, "secondary", w=TR_TAB_W, anchor=anc))
        tab_java.append(("if (i == %d) " % n_ if n_ == 0 else "else if (i == %d) " % n_) + app(TR_TAB_ROW_IDS[_row], mk))
    tab_java.append("else if (i == %d) {\n%s\n}" % (len(TREES), class_tab_chain(app)))
    info = [app(body, SUI.group("SkyyTrInfo", "Left", h=TR_INFO_H)),
            app("SkyyTrHead", SUI.label("SkyyTrLvl", "", "rowName", w=TRC_LVL_W, h=TR_HEAD_H, align="End", col=SUI.J("col", TCOLOR[0]))),
            app("SkyyTrInfo", SUI.label("SkyyTrTok", "", "bold", w=TR_TOK_W, h=TR_INFO_H, col="gold")),
            app("SkyyTrInfo", SUI.label("SkyyTrDust", "", "bold", w=TR_DUST_W, h=TR_INFO_H, col="value")),
            app("SkyyTrInfo", SUI.label("SkyyTrNote", "", "default", w=TRC_NOTE_W, h=TR_INFO_H))]
    # ---- the list well with the pager strip and the graph, or the no-class message
    well = SUI.list_well("SkyyTrGrid", TRC_GRID_W, rows=6, row_h=TR_CELL_H, gap=TR_ROW_GAP)
    assert well.inner_w == TRC_GRID_W - 2 * SUI.WELL_LIST_PAD and well.inner_h == TRC_STRIP_H + TRC_STRIP_GAP + 6 * TRC_SLOT_H
    grid = [app(body, SUI.separator("content", anchor={"top": 8, "bottom": 8})),
            app(body, SUI.group("SkyyTrBody", "Left", h=TR_GRID_H)),
            app("SkyyTrBody", well)]
    noclass = app("SkyyTrGrid", SUI.label("SkyyTrNoClass", "", "message", h=well.inner_h, wrap=True))
    strip = [app("SkyyTrGrid", SUI.group("SkyyTrRs", "Left", h=TRC_STRIP_H, anchor={"bottom": TRC_STRIP_GAP})),
             app("SkyyTrRs", SUI.label("SkyyTrRsL", "", "subtitle", w=TRC_RSL_W, h=TRC_STRIP_H))]
    pg_w, pg_gap = 44, 8
    strip += [app("SkyyTrRs", SUI.group("SkyyTrPgG", "Top", w=TRC_PG_W, h=TRC_STRIP_H, anchor={"left": TRC_RS_GAP})),
              app("SkyyTrPgG", SUI.spacer(h=(TRC_STRIP_H - SUI.BTN_SMALL_H) // 2)),
              app("SkyyTrPgG", SUI.group("SkyyTrPgR", "Left", h=SUI.BTN_SMALL_H)),
              chain(["cp > 0"], "SkyyTrPgR", [SUI.button("SkyyTrPgP", "<", "secondary", size="small", w=pg_w),
                                              SUI.button("SkyyTrPgP", "<", "secondary", size="small", w=pg_w, disabled=True)]),
              app("SkyyTrPgR", SUI.label("SkyyTrPgL", "", "bold", w=TRC_PG_W - 2 * pg_w - 2 * pg_gap, h=SUI.BTN_SMALL_H, align="Center", anchor={"left": pg_gap})),
              chain(["cp < 1"], "SkyyTrPgR", [SUI.button("SkyyTrPgN", ">", "secondary", size="small", w=pg_w, anchor={"left": pg_gap}),
                                              SUI.button("SkyyTrPgN", ">", "secondary", size="small", w=pg_w, anchor={"left": pg_gap}, disabled=True)])]
    # ---- the graph: 6 rows of 9 slots; a slot = a Top column: row A (the cell or the bar piece + the right-gap stub) and the bottom-gap stub
    crow = app("SkyyTrGrid", SUI.group("SkyyTrCR" + r, "Left", h=TRC_SLOT_H))
    slot = app("SkyyTrCR" + r, SUI.group("SkyyTrCS" + k, "Top", w=TRC_SLOT_W, h=TRC_SLOT_H))
    rowa = app("SkyyTrCS" + k, SUI.group("SkyyTrCA" + k, "Left", h=TRC_CELL_H))
    node_col = SUI.color_by([("cst[n] == 1", "success"), ("cst[n] == 2", "info"), ("cst[n] == 4", "error")], "disabled")

    def ccell(state, col):
        c = SUI.icon_cell("SkyyTrC" + nn, SUI.J("@PKG@.TreeClass.icon(ci, n)", "Weapon_Sword_Iron"), state=state, icon=TRC_ICON,
                          w=TRC_CELL_W, h=TRC_CELL_H, icon_left=TRC_ICON_L)
        sb = SUI.label("SkyyTrC" + nn + "Sb", "", "rowSub", w=TRC_SB_W, h=TRC_SB_H, size=TRC_SB_SIZE, bold=True, align="Center", col=col,
                       anchor={"left": TRC_SB_L, "top": TRC_SB_T})
        return _tr_in(c, sb)
    cells = chain(["n == sel && !am", "cst[n] == 3 && @PKG@.TreeClass.slotComing(n)"], "SkyyTrCA" + k, [ccell("selected", "white"), ccell(TR_DRAFT_CELL, "disabled"), ccell("normal", node_col)])

    def gold(role):
        return SUI.color_by([("pg[q + %d]" % role, TRC_GOLD)], TRC_BAR_COL)

    def bar(w, h, role):
        return SUI.group(None, None, w=w, h=h, bg=gold(role))
    arm = TRC_CELL_H - TRC_BAR_Y - TRC_BAR
    hbar = [app("SkyyTrCA" + k, SUI.group("SkyyTrCM" + k, "Top", w=TRC_CELL_W, h=TRC_CELL_H)),
            app("SkyyTrCM" + k, SUI.spacer(h=TRC_BAR_Y)),
            app("SkyyTrCM" + k, bar(TRC_CELL_W, TRC_BAR, 0))]
    vbar = [app("SkyyTrCA" + k, SUI.group("SkyyTrCM" + k, "Left", w=TRC_CELL_W, h=TRC_CELL_H)),
            app("SkyyTrCM" + k, SUI.spacer(w=TRC_BAR_X)),
            app("SkyyTrCM" + k, bar(TRC_BAR, TRC_CELL_H, 0))]
    junc = [app("SkyyTrCA" + k, SUI.group("SkyyTrCM" + k, "Top", w=TRC_CELL_W, h=TRC_CELL_H)),
            "if ((arms & 1) != 0) {",
            app("SkyyTrCM" + k, SUI.group("SkyyTrCU" + k, "Left", h=TRC_BAR_Y)),
            app("SkyyTrCU" + k, SUI.spacer(w=TRC_BAR_X)),
            app("SkyyTrCU" + k, bar(TRC_BAR, TRC_BAR_Y, 1)),
            "} else " + app("SkyyTrCM" + k, SUI.spacer(h=TRC_BAR_Y)),
            app("SkyyTrCM" + k, SUI.group("SkyyTrCJ" + k, "Left", h=TRC_BAR)),
            "if ((arms & 2) != 0) " + app("SkyyTrCJ" + k, bar(TRC_BAR_X, TRC_BAR, 2)),
            "else " + app("SkyyTrCJ" + k, SUI.spacer(w=TRC_BAR_X)),
            app("SkyyTrCJ" + k, bar(TRC_BAR, TRC_BAR, 3)),
            "if ((arms & 4) != 0) " + app("SkyyTrCJ" + k, bar(TRC_CELL_W - TRC_BAR_X - TRC_BAR, TRC_BAR, 4)),
            "if ((arms & 8) != 0) {",
            app("SkyyTrCM" + k, SUI.group("SkyyTrCD" + k, "Left", h=arm)),
            app("SkyyTrCD" + k, SUI.spacer(w=TRC_BAR_X)),
            app("SkyyTrCD" + k, bar(TRC_BAR, arm, 5)),
            "}"]
    gapr = ["if (@PKG@.TreeClass.SR[base + k]) {",
            app("SkyyTrCA" + k, SUI.group("SkyyTrCG" + k, "Top", w=TRC_SLOT_W - TRC_CELL_W, h=TRC_CELL_H)),
            app("SkyyTrCG" + k, SUI.spacer(h=TRC_BAR_Y)),
            app("SkyyTrCG" + k, bar(TRC_SLOT_W - TRC_CELL_W, TRC_BAR, 6)),
            "}"]
    rowb = ["if (@PKG@.TreeClass.SD[base + k]) {",
            app("SkyyTrCS" + k, SUI.group("SkyyTrCB" + k, "Left", h=TRC_SLOT_H - TRC_CELL_H)),
            app("SkyyTrCB" + k, SUI.spacer(w=TRC_BAR_X)),
            app("SkyyTrCB" + k, bar(TRC_BAR, TRC_SLOT_H - TRC_CELL_H, 7)),
            "}"]
    # ---- 0.3.7 THE ABILITY PANEL: the title, the key hint, 4 cards (icon + name / key, the 2 modifier slots, Swap + the action)
    apanel = [app("SkyyTrBody", SUI.panel("SkyyTrAp", "well", w=TRC_AP_W, h=TR_GRID_H, anchor={"left": TRC_AP_GAP})),
              app("SkyyTrAp", SUI.label("SkyyTrApT", "Abilities", "subtitle", h=TRC_AP_TITLE_H)),
              app("SkyyTrAp", SUI.label("SkyyTrApH", "", "caption", h=TRC_AP_HINT_H, wrap=True, anchor={"bottom": 6}))]
    apno = app("SkyyTrAp", SUI.label("SkyyTrApNo", "", "message", h=TRC_AP_NO_H, wrap=True))
    name_col = SUI.color_by([("selA", "info"), ("aown && aen", "rowName")], "disabled")
    key_col = SUI.color_by([("aown && !aen", "gold")], "rowSub")

    def acell(state):
        return SUI.icon_cell("SkyyTrAi" + i, SUI.J("aicon", "Weapon_Staff_Iron"), state=state, w=TRC_CARD_ICON, h=TRC_CARD_ICON, icon=TRC_CARD_ICON - 8)

    def mslot(ab, j):
        cell = SUI.icon_cell("SkyyTrAs" + ab + i, None, state="empty", w=TRC_CARD_BTN_W, h=SUI.BTN_SMALL_H,
                             anchor={"left": 4} if j == 1 else None)
        sc = SUI.color_by([("am && asl == i && msl == %d" % j, "gold")], "value")
        lab = SUI.label("SkyyTrAl" + ab + i, "", "rowSub", w=TRC_CARD_BTN_W - 8, h=SUI.BTN_SMALL_H, size=TRC_SB_SIZE, bold=True,
                        align="Center", col=sc, anchor={"left": 4, "top": 0})
        return _tr_in(cell, lab)
    acard = [app("SkyyTrAp", SUI.group("SkyyTrAc" + i, "Top", w=TRC_AP_IN_W, h=TRC_CARD_H, pad=TRC_CARD_PAD, bg="row",
                                        anchor={"bottom": TRC_CARD_GAP})),
             app("SkyyTrAc" + i, SUI.group("SkyyTrAa" + i, "Left", h=TRC_CARD_ICON)),
             chain(["selA"], "SkyyTrAa" + i, [acell("selected"), acell("normal")]),
             app("SkyyTrAa" + i, SUI.group("SkyyTrAx" + i, "Top", w=TRC_CARD_TXT_W, h=TRC_CARD_ICON, anchor={"left": 6})),
             app("SkyyTrAx" + i, SUI.label("SkyyTrAn" + i, "", "rowName", h=24, col=name_col)),
             app("SkyyTrAx" + i, SUI.label("SkyyTrAk" + i, "", "rowSub", h=20, col=key_col)),
             app("SkyyTrAc" + i, SUI.group("SkyyTrAm" + i, "Left", h=SUI.BTN_SMALL_H, anchor={"top": TRC_CARD_ROW})),
             app("SkyyTrAm" + i, mslot("a", 0)),
             app("SkyyTrAm" + i, mslot("b", 1)),
             app("SkyyTrAc" + i, SUI.group("SkyyTrAb" + i, "Left", h=SUI.BTN_SMALL_H, anchor={"top": TRC_CARD_ROW})),
             chain(["this.apend == i", "this.apend >= 0"], "SkyyTrAb" + i, [
                 SUI.button("SkyyTrAw" + i, "Cancel", "secondary", size="small", w=TRC_CARD_BTN_W),
                 SUI.button("SkyyTrAw" + i, "Move here", "secondary", size="small", w=TRC_CARD_BTN_W),
                 SUI.button("SkyyTrAw" + i, "Swap", "secondary", size="small", w=TRC_CARD_BTN_W)]),
             chain(["aact == 0", "aact == 1", "aact == 2"], "SkyyTrAb" + i, [
                 SUI.button("SkyyTrAe" + i, "Locked", "secondary", size="small", w=TRC_CARD_BTN_W, anchor={"left": 4}, disabled=True),
                 SUI.button("SkyyTrAe" + i, "Enable", "secondary", size="small", w=TRC_CARD_BTN_W, anchor={"left": 4}),
                 SUI.button("SkyyTrAe" + i, "Other alt", "secondary", size="small", w=TRC_CARD_BTN_W, anchor={"left": 4}),
                 SUI.button("SkyyTrAe" + i, "Modifiers", "secondary", size="small", w=TRC_CARD_BTN_W, anchor={"left": 4})])]
    # ---- the detail well: the node detail (the template's ids and layout) OR the ability detail (0.3.7)
    fg0 = SUI.color_by([("st0 == 1", "success"), ("st0 == 2", "info"), ("st0 == 4", "error")], "disabled")
    frame = SUI.SLOT_FRAME
    name_w = TR_DET_IN_W - frame - 12
    sec_h = SUI.outer_size(SUI.section(None, "Effect"))[1]
    det_parts = [frame + 10, 26 + 4, sec_h, 44 + 6, 44 + 6, sec_h, 26 + 6, 44 + 6, sec_h, 66]
    buy_parts = [26 + 6, SUI.BTN_H]
    slack = SUI.fit(det_parts + buy_parts, TR_GRID_H - 2 * SUI.WELL_PAD, "class detail well")
    detp = app("SkyyTrBody", SUI.panel("SkyyTrDet", "well", w=TR_DET_W, h=TR_GRID_H, anchor={"left": TR_DET_GAP}))
    det = [app("SkyyTrDet", SUI.group("SkyyTrDetTop", "Left", h=frame, anchor={"bottom": 10})),
           app("SkyyTrDetTop", SUI.item_frame("SkyyTrDetFrame", frame, icon_id="SkyyTrDetIcon",
                                              item=SUI.J("@PKG@.TreeClass.icon(ci, sel)", "Weapon_Sword_Iron"))),
           app("SkyyTrDetTop", SUI.label("SkyyTrDetName", "", "rowName", w=name_w, h=frame, wrap=True, col=fg0, anchor={"left": 12})),
           app("SkyyTrDet", SUI.label("SkyyTrDetState", "", "bold", h=26, col=fg0, anchor={"bottom": 4})),
           app("SkyyTrDet", SUI.section(None, "Effect")),
           app("SkyyTrDet", SUI.label("SkyyTrDetNow", "", "default", h=44, wrap=True, col="value", anchor={"bottom": 6})),
           app("SkyyTrDet", SUI.label("SkyyTrDetNext", "", "default", h=44, wrap=True, anchor={"bottom": 6})),
           app("SkyyTrDet", SUI.section(None, "Cost")),
           app("SkyyTrDet", SUI.label("SkyyTrDetCost", "", "bold", h=26, col="gold", anchor={"bottom": 6})),
           app("SkyyTrDet", SUI.label("SkyyTrDetNeed", "", "default", h=44, wrap=True, col="error", anchor={"bottom": 6})),
           app("SkyyTrDet", SUI.section(None, "How it works")),
           app("SkyyTrDet", SUI.label("SkyyTrDetHow", "", "summary", h=66, wrap=True, max_lines=False))]
    buy_col = SUI.color_by([("st0 == 1", "gold"), ("st0 == 2", "success")], "disabled")
    buy = [app("SkyyTrDet", SUI.label("SkyyTrBuyTx", "", "bold", h=26, col=buy_col, anchor={"top": slack, "bottom": 6})),
           app("SkyyTrDet", SUI.group("SkyyTrBuyRow", "Left", h=SUI.BTN_H)),
           chain(["st0 == 3", "sw", "st0 == 2 || st0 == 4"], "SkyyTrBuyRow", [
               SUI.button("SkyyTrBuy", "Coming soon", "secondary", w=TR_BUY_W, disabled=True),
               SUI.button("SkyyTrBuy", "Switch", "primary", w=TR_BUY_W),
               SUI.button("SkyyTrBuy", "Owned", "secondary", w=TR_BUY_W, disabled=True),
               SUI.choose(SUI.J("st0 == 1"), SUI.button("SkyyTrBuy", "Unlock", "primary", w=TR_BUY_W),
                          SUI.button("SkyyTrBuy", "Unlock", "primary", w=TR_BUY_W, disabled=True))]),
           app("SkyyTrBuyRow", SUI.choose(SUI.J("canUndo"), SUI.button("SkyyTrUndo", "Undo", "secondary", w=TR_BUY_W, anchor={"left": 8}),
                                          SUI.button("SkyyTrUndo", "Undo", "secondary", w=TR_BUY_W, anchor={"left": 8}, disabled=True)))]
    # the ability detail: icon + name / level text, the level line, the key line, the selected slot, the modifier rows, how, the buttons
    ad_parts = [frame + 10, 26 + 4, 44 + 4, sec_h, 5 * (TRC_AD_ROW_H + 4), sec_h, 66, SUI.BTN_H]
    aslack = SUI.fit(ad_parts, TR_GRID_H - 2 * SUI.WELL_PAD, "ability detail well")
    k_ = SUI.J("k", "0")
    adet = [app("SkyyTrDet", SUI.group("SkyyTrAdTop", "Left", h=frame, anchor={"bottom": 10})),
            app("SkyyTrAdTop", SUI.item_frame("SkyyTrAdFrame", frame, icon_id="SkyyTrAdIcon", item=SUI.J("aicon2", "Weapon_Staff_Iron"))),
            app("SkyyTrAdTop", SUI.label("SkyyTrAdN", "", "rowName", w=name_w, h=frame, wrap=True, col="info", anchor={"left": 12})),
            app("SkyyTrDet", SUI.label("SkyyTrAdS", "", "bold", h=26, col="gold", anchor={"bottom": 4})),
            app("SkyyTrDet", SUI.label("SkyyTrAdG", "", "default", h=44, wrap=True, col="value", anchor={"bottom": 4})),
            app("SkyyTrDet", SUI.section("SkyyTrAdM", ""))]
    arow = [app("SkyyTrDet", SUI.group("SkyyTrAr" + k_, "Left", h=TRC_AD_ROW_H, anchor={"bottom": 4})),
            app("SkyyTrAr" + k_, SUI.label("SkyyTrAt" + k_, "", "rowSub", w=TRC_AD_TXT_W, h=TRC_AD_ROW_H, wrap=True)),
            chain(["rs == 0", "rs == 1", "rs == 2", "rs == 3"], "SkyyTrAr" + k_, [
                SUI.button("SkyyTrAq" + k_, "Locked", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8}, disabled=True),
                SUI.button("SkyyTrAq" + k_, "In slot", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8}, disabled=True),
                SUI.button("SkyyTrAq" + k_, "Double", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8}),
                SUI.button("SkyyTrAq" + k_, "Taken", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8}, disabled=True),
                SUI.button("SkyyTrAq" + k_, "Equip", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8})])]
    adet2 = ["if (true) {",
             "}",
             app("SkyyTrDet", SUI.section(None, "How it works")),
             app("SkyyTrDet", SUI.label("SkyyTrAdH", "", "summary", h=66, wrap=True, max_lines=False)),
             app("SkyyTrDet", SUI.group("SkyyTrAdB", "Left", h=SUI.BTN_H, anchor={"top": aslack})),
             app("SkyyTrAdB", SUI.button("SkyyTrAu", "Unequip", "secondary", w=TR_BUY_W)),
             app("SkyyTrAdB", SUI.button("SkyyTrAv", "Tree node", "secondary", w=TR_BUY_W, anchor={"left": 8}))]
    foot = [app(body, SUI.result_line("SkyyTrMsg", SUI.J("infoColor(this.msg)", SUI.COLOR["success"]), h=TR_MSG_H, anchor={"top": 8})),
            app(body, SUI.separator("content", anchor={"top": 8, "bottom": 8})),
            app(body, SUI.group("SkyyTrFoot", "Left", h=TR_FOOT_H)),
            app("SkyyTrFoot", SUI.button("SkyyTrBack", "< Skills", "secondary", w=TR_BACK_W, sound="cancel"))]
    respec = []
    for ci_, cn in enumerate(CLASSES):
        on = SUI.button("SkyyTrRespec", "Click again to respec " + cn, "destructive", w=TR_RESPEC_ON_W,
                        anchor={"left": SUI.right_margin(W - TR_BACK_W, TR_RESPEC_ON_W)})
        off = SUI.button("SkyyTrRespec", "Respec " + cn, "secondary", w=TR_RESPEC_OFF_W,
                         anchor={"left": SUI.right_margin(W - TR_BACK_W, TR_RESPEC_OFF_W)})
        respec.append(("if (ci == %d) " % ci_ if ci_ == 0 else "else if (ci == %d) " % ci_) + app("SkyyTrFoot", SUI.choose(SUI.J("armed"), on, off)))
    respec.append("else " + app("SkyyTrFoot", SUI.button("SkyyTrRespec", "Respec", "secondary", w=TR_RESPEC_OFF_W, disabled=True,
                                                          anchor={"left": SUI.right_margin(W - TR_BACK_W, TR_RESPEC_OFF_W)})))
    parts = {
        "SHELL": sh.java("b"),
        "HEAD": app(body, SUI.group("SkyyTrHead", "Left", h=TR_HEAD_H, anchor={"bottom": TR_TAB_GAP})) + "\n" +
                app(body, SUI.group("SkyyTrHead2", "Left", h=TR_HEAD_H, anchor={"bottom": TR_HEAD_GAP})),
        "TAB": "\n".join(tab_java), "INFO": "\n".join(info), "GRID": "\n".join(grid), "NOCLASS": noclass, "STRIP": "\n".join(strip),
        "CROW": crow, "SLOT": slot, "ROWA": rowa, "CELL": cells, "HBAR": "\n".join(hbar), "VBAR": "\n".join(vbar), "JUNC": "\n".join(junc),
        "GAPR": "\n".join(gapr), "ROWB": "\n".join(rowb), "APANEL": "\n".join(apanel), "APNO": apno, "ACARD": "\n".join(acard),
        "DETP": detp, "DET": "\n".join(det), "BUY": "\n".join(buy), "ADET": "\n".join(adet), "AROW": "\n".join(arow),
        "FOOT": "\n".join(foot), "RESPEC": "\n".join(respec),
    }
    sh.appends.check(TR_PREFIX)
    SUI.assert_proven(marks, what="TreePage class tab")
    indent = {"SHELL": 2, "HEAD": 2, "TAB": 4, "INFO": 2, "GRID": 2, "NOCLASS": 4, "STRIP": 4, "CROW": 6, "SLOT": 8, "ROWA": 8, "CELL": 10,
              "HBAR": 10, "VBAR": 10, "JUNC": 10, "GAPR": 8, "ROWB": 8, "APANEL": 2, "APNO": 4, "ACARD": 6, "DETP": 2, "DET": 4, "BUY": 4,
              "ADET": 4, "AROW": 6, "FOOT": 2, "RESPEC": 2}
    java = TRC_BUILD
    for name, part in parts.items():
        tok = "{{" + name + "}}"
        assert java.count(tok) == 1, "unused / doubled Java part " + name
        java = java.replace(tok, "\n".join((" " * indent[name] + ln) if ln.strip() else ln for ln in part.split("\n")))
    assert not re.findall(r"\{\{[A-Z]+\}\}", java), "unfilled Java placeholder"
    # the ability detail's tail (How it works + the two buttons) goes right after the modifier rows loop
    tail = "\n".join("    " + ln for ln in "\n".join(adet2[2:]).split("\n"))
    anchor_ = '    b.set("#SkyyTrAdH.Text", '
    assert java.count(anchor_) == 1
    java = java.replace(anchor_, tail + "\n" + anchor_)
    for ident in TRC_NEW_IDS[:-1]:
        assert ("#%s {" % ident) in java or ('#%s" + (' % re.sub(r"\d+$", "", ident)) in java or ('#%s" + ' % re.sub(r"\d+(Ic|Sb)?$", "", ident)) in java, \
            "the class page does not create #" + ident
    return java, marks
''')

# ================================================================================================================ TreePage state + events
rep('''F(page, "public java.util.ArrayList undo;")
''', '''F(page, "public java.util.ArrayList undo;")
F(page, "public boolean amode;")   # 0.3.7: the detail well shows the ability of card aslot (modifier slot mslot); apend = the card a Swap started on
F(page, "public int aslot;")
F(page, "public int mslot;")
F(page, "public int apend;")
''')
rep('''  this.undo = new java.util.ArrayList();
  this.armPrice = 0L;
}""")''', '''  this.undo = new java.util.ArrayList();
  this.armPrice = 0L;
  this.amode = false;
  this.aslot = 0;
  this.mslot = 0;
  this.apend = -1;
}""")''')
rep('''TR_INFO_COLOR = SUI.java_color_by_text("infoColor", [''', '''TR_INFO_COLOR = SUI.java_color_by_text("infoColor", [
    ("startsWith", "Done: ", "+"), ("startsWith", "Ability: ", "="),   # 0.3.7: the ability panel's answers''')
# the ability panel's events (instance methods: they read / change this page's state); SkyyClasses answers "+..." / "-..."
rep('''M(page, TR_CBUILD_JAVA)   # 0.3 part 2: the class tab (build() calls it)
''', '''M(page, TR_CBUILD_JAVA)   # 0.3 part 2: the class tab (build() calls it)
M(page, r"""
public static String said(String r) {
  if (r == null || r.length() == 0) return "Ability: no answer";
  if (r.startsWith("+")) return "Done: " + r.substring(1);
  if (r.startsWith("-")) return r.substring(1);
  return r;
}""")
M(page, r"""
public String abilEv(java.util.UUID u, @PKG@.TreeData d, int ci, int lvl, String act, int i, int k) {
  if (this.probe) return "Ability panel actions are off in the probe (probe - not saved)";
  if (ci < 0) return "Choose a class first";
  boolean[] it = @PKG@.TreeClass.intact(d, ci);
  String csv = @PKG@.TreeClass.csvOf(d, it, ci);
  Object[] ap = @PKG@.TreeClass.apanel(u, csv);
  if (ap == null || ap.length < 78 || !"ok".equals(ap[0])) return @PKG@.TreeClass.apanelMsg(ap, ci, null);
  if (act.equals("swap")) {
    if (this.apend < 0) { this.apend = i; return "Ability: pick the card to swap " + String.valueOf(ap[12 + i * 16 + 1]) + " with (or Cancel)"; }
    if (this.apend == i) { this.apend = -1; return "Ability: swap cancelled"; }
    int a = this.apend;
    this.apend = -1;
    return said(@PKG@.TreeClass.ado(u, "swap", String.valueOf(a), String.valueOf(i), csv));
  }
  int b0 = 12 + i * 16;
  String id = String.valueOf(ap[b0]);
  if (act.equals("act")) {
    boolean own = Boolean.TRUE.equals(ap[b0 + 3]);
    boolean en = Boolean.TRUE.equals(ap[b0 + 4]);
    int line = ((Integer) ap[b0 + 5]).intValue();
    if (!own) return @PKG@.TreeClass.keyText(ap, i, ci);
    if (!en) {
      int n = @PKG@.TreeClass.nodeIdx("A" + line);
      this.amode = false;
      this.csel = n;
      this.cpage = 0;
      return @PKG@.TreeClassOps.buy(u, d, ci, lvl, n, this.undo, false);
    }
    if (line == 4 && Boolean.TRUE.equals(ap[5])) return said(@PKG@.TreeClass.ado(u, "pick", "B".equals(String.valueOf(ap[4])) ? "A" : "B", "", csv));
    this.amode = true;
    this.aslot = i;
    return "";
  }
  if (act.equals("equip")) {
    String[] rows = @PKG@.TreeClass.amods(u, id, csv);
    if (rows == null || k + 1 >= rows.length) return "Ability: that modifier is gone - try again";
    String mid = rows[k + 1].split("\\\\|", -1)[0];
    return said(@PKG@.TreeClass.ado(u, "equip", id, this.mslot + ":" + mid, csv));
  }
  if (act.equals("unequip")) return said(@PKG@.TreeClass.ado(u, "unequip", id, String.valueOf(this.mslot), csv));
  return "";
}""")
''')
rep('''      for (int n = 1; n <= @PKG@.TreeClass.NN; n++) {
        if (data.indexOf("trc" + n + "\\"") >= 0) { this.csel = n - 1; this.cpage = @PKG@.TreeClass.NPAGE[n - 1]; this.msg = ""; rebuild(); return; }
      }''', '''      for (int n = 1; n <= @PKG@.TreeClass.NN; n++) {
        if (data.indexOf("trc" + n + "\\"") >= 0) { this.csel = n - 1; this.cpage = @PKG@.TreeClass.NPAGE[n - 1]; this.msg = ""; this.amode = false; rebuild(); return; }
      }
      // 0.3.7: the ability panel (cards 0-3: icon = details, the two modifier slots, Swap, the action button) and the ability detail
      if (data.indexOf("trtree\\"") >= 0) { this.amode = false; this.msg = ""; rebuild(); return; }
      if (data.indexOf("trmu\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "unequip", this.aslot, 0); rebuild(); return; }
      for (int ai = 0; ai < 4; ai++) {
        if (data.indexOf("trab" + ai + "\\"") >= 0) { this.amode = true; this.aslot = ai; this.msg = ""; rebuild(); return; }
        if (data.indexOf("trmsa" + ai + "\\"") >= 0) { this.amode = true; this.aslot = ai; this.mslot = 0; this.msg = ""; rebuild(); return; }
        if (data.indexOf("trmsb" + ai + "\\"") >= 0) { this.amode = true; this.aslot = ai; this.mslot = 1; this.msg = ""; rebuild(); return; }
        if (data.indexOf("trsw" + ai + "\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "swap", ai, 0); rebuild(); return; }
        if (data.indexOf("tren" + ai + "\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "act", ai, 0); rebuild(); return; }
      }
      for (int mk = 0; mk < 5; mk++) {
        if (data.indexOf("trme" + mk + "\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "equip", this.aslot, mk); rebuild(); return; }
      }''')

# ================================================================================================================ checks on the result
assert s.count("registerSystem(") == REG0, "0.3.7 adds no system"
assert s.count("registerCommand(") == CMD0, "command registrations changed"
assert "KEEP=10" in s and "KEEP=20" not in s
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.6 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.3.6
print("wrote", dst, "(%d lines; 0.3.6 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
