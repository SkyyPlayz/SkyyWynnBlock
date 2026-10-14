"""Derive SkyyTrees/build_skyytrees_0.3.8.py from the LIVE generated SkyyTrees/build_skyytrees_0.3.7.py (the tools/deploy_set.py SET pin).
Run:  python tools/trees_0_3_8_patch.py   then   python SkyyTrees/build_skyytrees_0.3.8.py   (never --deploy: coordinated deploy)
      then python SkyyTrees/test_skyytrees_0.3.8.py --dir <tools/dev/scratch/<task>/...> (bare JVM)
EDITED-SCRIPTS RULE (commit ab75b6c): the lineage is Skyy's EDITED 0.2.3 -> trees_0_2_4_patch.py -> ... -> trees_0_3_7_patch.py -> the
generated 0.3.7 read here; tools/trees_0_2_3_patch.py and older are NEVER re-run. Edit THIS file, never the generated build script.

0.3.8 = MONK + ASSASSIN ABILITY NODES + REBIRTH R5 (with SkyyClasses 0.1.23; Skyy 2026-10-14 "Link ability's to the ability buttons, and
enable the class skill trees ..." + "Basically we are making our own runes and modifiers, then controlling them in the skill tree ..." +
M10 "Priest + Monk + Assassin, then ..."; research/cloud/Rebirth-Spec.md section 6 R5).
WHAT CHANGES:
  - THE MONK + ASSASSIN A / M NODES: A1-A4 name their abilities (Monk Flowing Form / Palm Strike / Cyclone Kick / the Ability 1 alt =
    Hundred Fists or Still Water; Assassin Cloak + First Strike / Toxin / God Killer / Vanishing Act - the Assassin's only Ability 1 alt),
    M<n>A / M<n>B their modifier slots. Like Mage + Priest they are free (0 AP) and buyable once SkyyClasses 0.1.23 lists them
    (tree:reads:SkyyClasses). Path node texts SkyyClasses 0.1.23 applies with a stand-in: Monk Iron Fist (crit = x1.5), Serenity (Awed
    enemies deal 15 % less - their attack speed has no server knob).
  - THE ABILITY DETAIL: a REBIRTH UPGRADE to place (SkyyClasses 0.1.23 rb.pick, one per rebirth per ability) turns every modifier row's
    button into "Max Up" - a click places it on that modifier (class:fn:abilDo rbpick: it may level one step past its top).
  - REBIRTH R5 - the participant rebirth:part:trees (TreeRb; SkyyRebirth 0.2's two-phase protocol, the SkyyCoins 0.1.7 CoinRb shape),
    apply(Object[] { op, pkey, txid, ... }) -> String, never throws:
      measure  "ok:nodes=<skill-tree nodes to clear>;classPicks=<owned class nodes>" (nothing written)
      prepare  measure + a BACKUP of players/<pkey>.properties (rebirth-backup/<pkey>/<txid>/, last 3 kept) + the STAGED file
               rebirth/<pkey>.rb-<txid>.properties (tx, pkey, the facts; tmp + fsync + atomic rename). An older txid's staged file is
               deleted (refused while rebirth:fn:decision says it committed).
      commit   in memory under the TreeStore lock, then ONE fsync'd atomic write: every bought node of the skill trees cleared (Mining,
               Foraging, Farming, Cooking, Acrobatics, Alchemy, Smithing - NOT Exploration, Rebirth-Spec 7.2 U5), their off flags + the
               Dust credit cleared (no Dust refund, Skyy Q4); every class tree KEEPS its picks, remembered in purchase order
               (Class.<Class>.order) with the rebirth gate on (Class.<Class>.rb=1); rb.lastTx = txid. "done" when already applied.
      abort    deletes the staged file (refused once committed); status = committed / staged / none.
    THE REBIRTH GATE (Skyy Q5 "remember and come back"): while Class.<Class>.rb=1 a class node works only while your AP cover it - the
      picks are walked in purchase order and every paid node counts until one does not fit (that one and the later paid ones wait;
      free nodes - the A / M ability nodes, the TS switch - always work). New paid nodes cannot be bought while picks wait ("they come
      back first"). The order: Class.<Class>.order, kept by every buy / undo / respec from now on (a file without it = table order).
    DUST x rebirth:fn:dustmult (Skyy Q4 "first rebirth gives 2x all dust"): every tree's earned Dust (not the credit) x SkyyRebirth's
      multiplier for the profile and tree (1 when SkyyRebirth is missing or answers nothing).
    SkyyRebirth must add "trees" to its part list (RbJournal.PARTS) - another round's file.
  FIX ROUND (critics 2026-10-14): a rebirth-gated class respec costs the level its OWNED picks need (TreeClass.rbPriceLvl, never
    free / cheap after a rebirth); the Dust multiplier keeps SkyyRebirth's last answer when it goes silent, and a negative Dust balance
    skips the respec cooldown only on a real answer (TreeCalc.dustKnown) for a rebirthed profile; the rebirth backup is the in-memory
    state; the rebirth line is short enough for the detail well (asserted); the no-abilities text names all four classes.
  New saved lines: rb.lastTx, Class.<Class>.order, Class.<Class>.rb (a profile's file only after a rebirth or a class buy). No setting,
  command or migration.
  FIX ROUND 2: the gated respec price also at class level 0 (right after a rebirth); picks above the AP cap are priced at the cap level;
    Max Up shows only on an unlocked modifier.
  ROLLBACK 0.3.8 -> 0.3.7: NEVER after a rebirth has run (0.3.7 has no gate: the kept picks are ungated, a negative AP balance makes the
  class respec free with no cooldown). Before any rebirth: safe - 0.3.7 keeps the Class.<Class>.order / .rb lines as unknown lines (the gate is off: every kept pick works
  at once) and drops rb.lastTx on its next save; the Monk / Assassin A / M nodes become "coming" again (nothing spent - they are free).
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.3.7.py")
dst = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.3.8.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
CR, LF = chr(13), chr(10)
s = raw.decode("utf8").replace(CR + LF, LF)
assert 'VERSION = "0.3.7"' in s and "GENERATED by tools/trees_0_3_7_patch.py from the LIVE build_skyytrees_0.3.6.py" in s, \
    "build_skyytrees_0.3.7.py is not the live 0.3.7 of the edited lineage"
assert "TreeRb" not in s and "rebirth:part:trees" not in s, "0.3.7 already has the 0.3.8 parts"
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
CHANGES = []


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.8 = MONK"):HEAD.index("  ROLLBACK 0.3.8")].rstrip()

# ================================================================================================================ header + version
rep('''"""SkyyTrees 0.3.7 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
GENERATED by tools/trees_0_3_7_patch.py from the LIVE build_skyytrees_0.3.6.py (the SET pin) - edit the patch, not this file. 0.3.6
was GENERATED''', '''"""SkyyTrees 0.3.8 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
GENERATED by tools/trees_0_3_8_patch.py from the LIVE build_skyytrees_0.3.7.py (the SET pin) - edit the patch, not this file. 0.3.7
was GENERATED by tools/trees_0_3_7_patch.py from the LIVE build_skyytrees_0.3.6.py. 0.3.6
was GENERATED''')
rep('''0.3.7 (2026-10-14; notes: tools/trees_0_3_7_patch.py) ''', '''0.3.8 (2026-10-14; notes: tools/trees_0_3_8_patch.py) ''' + NOTE[len("0.3.8 = "):].replace(LF, LF + "    ") + '''
  CHECKED: SkyyTrees/test_skyytrees_0.3.8.py (bare JVM: class compare vs 0.3.7, -Xverify:all, the Monk / Assassin nodes with the real
    SkyyClasses 0.1.23, the rebirth part (measure / prepare / commit / done / abort / status, a crash at every step), the rebirth gate,
    the Dust multiplier, the Max Up button, the access audit, start twice on a copy of the live data).

=== SkyyTrees 0.3.7 notes (history; still true unless 0.3.8 above says otherwise) ===
0.3.7 (2026-10-14; notes: tools/trees_0_3_7_patch.py) ''')
rep('''Run:   python build_skyytrees_0.3.7.py            -> SkyyTrees/SkyyTrees-0.3.7.jar
       python build_skyytrees_0.3.7.py --deploy   -> also''', '''Run:   python build_skyytrees_0.3.8.py            -> SkyyTrees/SkyyTrees-0.3.8.jar
       python build_skyytrees_0.3.8.py --deploy   -> also''')
rep('VERSION = "0.3.7"', 'VERSION = "0.3.8"')

# ================================================================================================================ the Monk + Assassin ability lines
rep('''            ("Sanctuary or Grace", "Enables your Ability 1 alt: Sanctuary or Martyr's Grace", "Ability 1 Alt", "your Ability 1 alt")],
}''', '''            ("Sanctuary or Grace", "Enables your Ability 1 alt: Sanctuary or Martyr's Grace", "Ability 1 Alt", "your Ability 1 alt")],
 # 0.3.8 (SkyyClasses 0.1.23)
 "Monk": [("Flowing Form", "Enables Flowing Form (ability line 1)", "Flowing Form", "Flowing Form"),
          ("Palm Strike", "Enables Palm Strike (ability line 2)", "Palm Strike", "Palm Strike"),
          ("Cyclone Kick", "Enables Cyclone Kick (ability line 3)", "Cyclone Kick", "Cyclone Kick"),
          ("Fists or Still Water", "Enables your Ability 1 alt: Hundred Fists or Still Water", "Ability 1 Alt", "your Ability 1 alt")],
 "Assassin": [("Cloak", "Enables Cloak + First Strike (ability line 1)", "Cloak", "Cloak + First Strike"),
              ("Toxin", "Enables Toxin (ability line 2)", "Toxin", "Toxin"),
              ("God Killer", "Enables God Killer (ability line 3)", "God Killer", "God Killer"),
              ("Vanishing Act", "Enables your Ability 1 alt: Vanishing Act", "Vanishing Act", "Vanishing Act")],
}''')
# the path texts SkyyClasses 0.1.23 applies with a stand-in (SkyyGear has no crit door; mob attack speed has no server knob)
rep('''   ("Iron Fist", "K", 0, "Every third Palm Strike on one target crits - cooldown +1 s", None, None)], [''',
    '''   ("Iron Fist", "K", 0, "Every third Palm Strike on one target crits (x1.5) - cooldown +1 s", None, None)], [''')
rep('''   ("Serenity", "K", 0, "Awed enemies attack 15% slower and hesitate 2 s - max combo 18", None, None)]),''',
    '''   ("Serenity", "K", 0, "Awed enemies deal 15% less and hesitate 2 s - max combo 18", None, None)]),''')

# ================================================================================================================ TreeData / TreeStore: order, gate, txid
rep('''F(dat, "public String[] cret = new String[%d];" % NC)               # 0.3.3: the retired ids copy = the run-once marker (Class.<Class>.retired)''',
    '''F(dat, "public String[] cret = new String[%d];" % NC)               # 0.3.3: the retired ids copy = the run-once marker (Class.<Class>.retired)
F(dat, "public String[] corder = new String[%d];" % NC)             # 0.3.8: the class picks in purchase order (Class.<Class>.order; null = table order)
F(dat, "public boolean[] crb = new boolean[%d];" % NC)              # 0.3.8: the rebirth gate (Class.<Class>.rb=1): picks work while the AP cover them
F(dat, "public String rbTx;")                                       # 0.3.8: rb.lastTx - the last rebirth applied to this profile
F(dat, "public java.util.UUID uid;")                                # 0.3.8: the owner (the rebirth gate reads their class level)''')
rep('''      boolean known = cfield.length() == 0 || cfield.equals("respecAt") || cfield.equals("on") || cfield.equals("freeRespec") || cfield.equals("notice") || cfield.equals("retired");''',
    '''      boolean known = cfield.length() == 0 || cfield.equals("respecAt") || cfield.equals("on") || cfield.equals("freeRespec") || cfield.equals("notice") || cfield.equals("retired")
        || cfield.equals("order") || cfield.equals("rb");   // 0.3.8''')
rep('''      else if (cfield.equals("notice")) { try { int nx = Integer.parseInt(cv.trim()); d.cnote[ci] = nx < 0 ? 0 : (nx > 1000 ? 1000 : nx); } catch (Throwable t8) { } }
      else d.cret[ci] = cv;''', '''      else if (cfield.equals("notice")) { try { int nx = Integer.parseInt(cv.trim()); d.cnote[ci] = nx < 0 ? 0 : (nx > 1000 ? 1000 : nx); } catch (Throwable t8) { } }
      else if (cfield.equals("order")) d.corder[ci] = cv.trim();   // 0.3.8
      else if (cfield.equals("rb")) d.crb[ci] = "1".equals(cv.trim());   // 0.3.8
      else d.cret[ci] = cv;''')
rep('''    String nm = p.getProperty("name");
    if (nm != null && nm.trim().length() > 0) d.name = nm.trim();''', '''    String nm = p.getProperty("name");
    if (nm != null && nm.trim().length() > 0) d.name = nm.trim();
    String rtx = p.getProperty("rb.lastTx");   // 0.3.8
    if (rtx != null && rtx.trim().length() > 0) d.rbTx = rtx.trim();''')
rep('''    if (d.cret[ci] != null) p.setProperty("Class." + @PKG@.TreeClass.CLASSES[ci] + ".retired", d.cret[ci]);''',
    '''    if (d.cret[ci] != null) p.setProperty("Class." + @PKG@.TreeClass.CLASSES[ci] + ".retired", d.cret[ci]);
    if (d.corder[ci] != null && d.corder[ci].length() > 0) p.setProperty("Class." + @PKG@.TreeClass.CLASSES[ci] + ".order", d.corder[ci]);   // 0.3.8
    if (d.crb[ci]) p.setProperty("Class." + @PKG@.TreeClass.CLASSES[ci] + ".rb", "1");''')
rep('''  for (int j = 0; j < d.cextra.size(); j++) {
    String[] kv = (String[]) d.cextra.get(j);
    if (p.getProperty(kv[0]) == null) p.setProperty(kv[0], kv[1]);
  }
  return p;''', '''  for (int j = 0; j < d.cextra.size(); j++) {
    String[] kv = (String[]) d.cextra.get(j);
    if (p.getProperty(kv[0]) == null) p.setProperty(kv[0], kv[1]);
  }
  if (d.rbTx != null) p.setProperty("rb.lastTx", d.rbTx);   // 0.3.8
  return p;''')
rep('''public static synchronized @PKG@.TreeData install(String k, java.util.UUID u, @PKG@.TreeData d) {
  @PKG@.TreeData cur = (@PKG@.TreeData) DATA.get(k);
  if (cur != null) return cur;
  OWNER.put(k, u);''', '''public static synchronized @PKG@.TreeData install(String k, java.util.UUID u, @PKG@.TreeData d) {
  @PKG@.TreeData cur = (@PKG@.TreeData) DATA.get(k);
  if (cur != null) return cur;
  if (d != null && d.uid == null) d.uid = u;   // 0.3.8: the rebirth gate reads the owner's class level
  OWNER.put(k, u);''')
# the purchase order follows every class write (buy / undo / respec)
rep('''public static synchronized void setClassOwn(@PKG@.TreeData d, int ci, int n, boolean v) {
  if (d == null || ci < 0 || ci >= @PKG@.TreeClass.NC || n < 0 || n >= @PKG@.TreeClass.NN) return;
  d.cown[ci * @PKG@.TreeClass.NN + n] = v;
}""")''', '''public static synchronized void setClassOwn(@PKG@.TreeData d, int ci, int n, boolean v) {
  if (d == null || ci < 0 || ci >= @PKG@.TreeClass.NC || n < 0 || n >= @PKG@.TreeClass.NN) return;
  boolean was = d.cown[ci * @PKG@.TreeClass.NN + n];
  d.cown[ci * @PKG@.TreeClass.NN + n] = v;
  if (was == v) return;
  d.corder[ci] = @PKG@.TreeDefs.orderEdit(d.corder[ci], @PKG@.TreeClass.NID[n], v);   // 0.3.8: the purchase order
}""")''')
rep('''  for (int n = 0; n < @PKG@.TreeClass.NN; n++) { d.cown[ci * @PKG@.TreeClass.NN + n] = false; d.con[ci * @PKG@.TreeClass.NN + n] = false; }
  d.crespecAt[ci] = now;''', '''  for (int n = 0; n < @PKG@.TreeClass.NN; n++) { d.cown[ci * @PKG@.TreeClass.NN + n] = false; d.con[ci * @PKG@.TreeClass.NN + n] = false; }
  d.crespecAt[ci] = now;
  d.corder[ci] = null;   // 0.3.8: a respec frees everything - no pick waits any more
  d.crb[ci] = false;''')
# pure helpers in TreeDefs (bare-JVM tested): the order list edit
rep('''# ---- 0.3 part 2: TreeClass constants (the template of the Python block above, class-major where a value is per class)''',
    '''# 0.3.8: the purchase order "A1,P1,T1" - add an id at the end / take it out
M(defs, r"""
public static String orderEdit(String csv, String id, boolean add) {
  StringBuilder b = new StringBuilder();
  boolean seen = false;
  if (csv != null && csv.length() > 0) {
    String[] p = csv.split(",");
    for (int i = 0; i < p.length; i++) {
      String t = p[i].trim();
      if (t.length() == 0) continue;
      if (t.equals(id)) { if (!add || seen) continue; seen = true; }
      if (b.length() > 0) b.append(',');
      b.append(t);
    }
  }
  if (add && !seen) { if (b.length() > 0) b.append(','); b.append(id); }
  return b.length() == 0 ? null : b.toString();
}""")
# ---- 0.3 part 2: TreeClass constants (the template of the Python block above, class-major where a value is per class)''')

# ================================================================================================================ the rebirth gate
rep('''M(cls, r"""
public static boolean[] intact(@PKG@.TreeData d, int ci) {
  if (d == null || ci < 0 || ci >= NC || d.bad) return new boolean[NN];
  return intactOf(ownOf(d, ci), ci);
}""")''', '''# 0.3.8 REBIRTH GATE (Skyy Q5 "remember and come back"): the picks in purchase order; the paid ones count while the AP cover them
M(cls, r"""
public static boolean[] coveredBy(boolean[] own, int ci, String order, int apAll) {
  boolean[] r = new boolean[NN];
  if (own == null || ci < 0 || ci >= NC) return r;
  boolean[] done = new boolean[NN];
  int[] seq = new int[NN];
  int ns = 0;
  if (order != null && order.length() > 0) {
    String[] p = order.split(",");
    for (int i = 0; i < p.length; i++) {
      int n = nodeIdx(p[i].trim());
      if (n < 0 || done[n] || !own[n]) continue;
      done[n] = true;
      seq[ns] = n;
      ns++;
    }
  }
  for (int n = 0; n < NN; n++) if (own[n] && !done[n]) { done[n] = true; seq[ns] = n; ns++; }
  int cum = 0;
  boolean stop = false;
  for (int i = 0; i < ns; i++) {
    int n = seq[i];
    int c = @PKG@.TreeCfg.C_AP[ci * NN + n];
    if (c <= 0) { r[n] = true; continue; }
    if (!stop && cum + c <= apAll) { cum = cum + c; r[n] = true; }
    else stop = true;
  }
  return r;
}""")
M(cls, r"""
public static boolean[] covered(@PKG@.TreeData d, int ci, boolean[] own) {
  if (d == null || ci < 0 || ci >= NC || !d.crb[ci] || d.uid == null) return own;
  int lv = level(d.uid, ci);
  if (lv < 0) return own;   // no SkyySkills answer: no gate (as before 0.3.8)
  return coveredBy(own, ci, d.corder[ci], ap(lv));
}""")
M(cls, r"""
public static int waiting(@PKG@.TreeData d, int ci) {
  if (d == null || ci < 0 || ci >= NC || !d.crb[ci]) return 0;
  boolean[] own = ownOf(d, ci);
  boolean[] cov = covered(d, ci, own);
  int n0 = 0;
  for (int n = 0; n < NN; n++) if (own[n] && !cov[n] && @PKG@.TreeCfg.C_AP[ci * NN + n] > 0) n0++;
  return n0;
}""")
M(cls, r"""
public static boolean[] intact(@PKG@.TreeData d, int ci) {
  if (d == null || ci < 0 || ci >= NC || d.bad) return new boolean[NN];
  return intactOf(covered(d, ci, ownOf(d, ci)), ci);   // 0.3.8: the rebirth gate
}""")''')
rep('''  if (@PKG@.TreeClass.isSwitch(n) && own[n] && it[n]) return flip(u, d, ci, n, probe);   // 0.3.3''',
    '''  if (@PKG@.TreeClass.isSwitch(n) && own[n] && it[n]) return flip(u, d, ci, n, probe);   // 0.3.3
  int wt = (!own[n] && @PKG@.TreeCfg.C_AP[ci * @PKG@.TreeClass.NN + n] > 0) ? @PKG@.TreeClass.waiting(d, ci) : 0;   // 0.3.8: kept rebirth picks come back first
  if (wt > 0) return wt + (wt == 1 ? " kept pick waits" : " kept picks wait") + " for your Ability Points - they come back first (in the order you bought them), then you can buy more" + suffix(probe);''')
rep('''  int cost = @PKG@.TreeCfg.C_AP[ci * @PKG@.TreeClass.NN + n];
  @PKG@.TreeStore.setClassOwn(d, ci, n, true);
  if (@PKG@.TreeClass.isSwitch(n)) @PKG@.TreeStore.setOn(d, ci, n, false);   // 0.3.3 fix: a bought switch starts OFF = party only (the LOCKED default)''',
    '''  int cost = @PKG@.TreeCfg.C_AP[ci * @PKG@.TreeClass.NN + n];
  @PKG@.TreeStore.setClassOwn(d, ci, n, true);
  if (@PKG@.TreeClass.isSwitch(n)) @PKG@.TreeStore.setOn(d, ci, n, false);   // 0.3.3 fix: a bought switch starts OFF = party only (the LOCKED default)''')

# ================================================================================================================ Dust x the rebirth multiplier
rep('''  r[2] = dustEarned(t, xp(u, t, lvl)) + (d == null ? 0L : d.credit[t]);   // 0.2.4: + the Double Jump move credit''',
    '''  r[2] = Math.round((double) dustEarned(t, xp(u, t, lvl)) * dustMult(u, t)) + (d == null ? 0L : d.credit[t]);   // 0.2.4: + the Double Jump move credit; 0.3.8: x rebirth''')
rep('''M(calc, r"""
public static long dustEarned(int t, long xp) {''', '''# 0.3.8 (Rebirth-Spec 3.4, Skyy Q4): SkyyRebirth's Dust multiplier for this profile + tree (rebirth:fn:dustmult; 1 = none). Cached 2 s.
F(calc, "public static final java.util.concurrent.ConcurrentHashMap DMULT = new java.util.concurrent.ConcurrentHashMap();")
F(calc, "public static final java.util.concurrent.ConcurrentHashMap DLAST = new java.util.concurrent.ConcurrentHashMap();")   # FIX: last answer per profile + tree
M(calc, r"""
public static double dustMult(java.util.UUID u, int t) {
  if (u == null || t < 0 || t >= @PKG@.TreeDefs.NT) return 1.0;
  try {
    String k = @PKG@.TreeStore.pkey(u) + "|" + t;
    long now = System.currentTimeMillis();
    Object o = DMULT.get(k);
    if (o instanceof double[] && now - (long) ((double[]) o)[1] < 2000L && now >= (long) ((double[]) o)[1]) return ((double[]) o)[0];
    double m = 1.0;
    boolean ok = false;
    java.util.function.Function f = fn("rebirth:fn:dustmult");
    if (f != null) {
      Object r = null;
      try { r = f.apply(new Object[] { @PKG@.TreeStore.pkey(u), @PKG@.TreeDefs.TREES[t] }); } catch (Throwable e2) { r = null; }
      if (r instanceof Number) {
        ok = true;
        double x = ((Number) r).doubleValue();
        if (x >= 1.0 && x <= 100.0) m = x;
      }
    }
    // FIX (critic: a missing / silent SkyyRebirth dropped a rebirthed player's Dust to x1 = a negative balance = a free respec): no answer
    // -> the last answer seen for this profile + tree (kept until restart); [2] = 1 when SkyyRebirth answered (dustKnown)
    if (ok) DLAST.put(k, new double[] { m });
    else { Object lg = DLAST.get(k); if (lg instanceof double[]) m = ((double[]) lg)[0]; }
    if (DMULT.size() > 4096) DMULT.clear();
    if (DLAST.size() > 65536) DLAST.clear();
    DMULT.put(k, new double[] { m, (double) now, ok ? 1.0 : 0.0 });
    return m;
  } catch (Throwable e) { return 1.0; }
}""")
# FIX (critic): true when SkyyRebirth answered the Dust multiplier for this profile + tree (the free negative-balance respec trusts only that)
M(calc, r"""
public static boolean dustKnown(java.util.UUID u, int t) {
  dustMult(u, t);
  Object o = DMULT.get(@PKG@.TreeStore.pkey(u) + "|" + t);
  return o instanceof double[] && ((double[]) o).length > 2 && ((double[]) o)[2] > 0.5;
}""")
M(calc, r"""
public static long dustEarned(int t, long xp) {''')

# ================================================================================================================ the Max Up button (a rebirth upgrade)
rep('''for _t in ("Equip", "Double", "In slot", "Taken", "Locked"):
    assert SUI.text_width(_t, 14, True, upper=True) + 2 * SUI.BTN_SMALL_PAD <= TRC_AD_BTN_W, _t''',
    '''for _t in ("Equip", "Double", "In slot", "Taken", "Locked", "Max Up"):   # 0.3.8: + the rebirth upgrade
    assert SUI.text_width(_t, 14, True, upper=True) + 2 * SUI.BTN_SMALL_PAD <= TRC_AD_BTN_W, _t
# 0.3.8 FIX (critic: the rebirth line overflowed #SkyyTrAdM, a bold 13 px upper-case section in the 440 px detail well = 422 px usable)
assert SUI.text_width("Rebirth: 1000 upgrades - press Max Up", 13, True, upper=True) <= 422 - 16''')
rep('''            chain(["rs == 0", "rs == 1", "rs == 2", "rs == 3"], "SkyyTrAr" + k_, [
                SUI.button("SkyyTrAq" + k_, "Locked", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8}, disabled=True),
                SUI.button("SkyyTrAq" + k_, "In slot", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8}, disabled=True),
                SUI.button("SkyyTrAq" + k_, "Double", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8}),
                SUI.button("SkyyTrAq" + k_, "Taken", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8}, disabled=True),
                SUI.button("SkyyTrAq" + k_, "Equip", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8})])]''',
    '''            chain(["rs == 5", "rs == 0", "rs == 1", "rs == 2", "rs == 3"], "SkyyTrAr" + k_, [
                SUI.button("SkyyTrAq" + k_, "Max Up", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8}),   # 0.3.8: a rebirth upgrade
                SUI.button("SkyyTrAq" + k_, "Locked", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8}, disabled=True),
                SUI.button("SkyyTrAq" + k_, "In slot", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8}, disabled=True),
                SUI.button("SkyyTrAq" + k_, "Double", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8}),
                SUI.button("SkyyTrAq" + k_, "Taken", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8}, disabled=True),
                SUI.button("SkyyTrAq" + k_, "Equip", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8})])]''')
rep('''    String cur = msl == 0 ? e0 : e1;
    boolean slotOpen = msl < aslots;''', '''    String cur = msl == 0 ? e0 : e1;
    boolean slotOpen = msl < aslots;
    int rbp = 0;   // 0.3.8: rebirth upgrades to place on this ability (SkyyClasses 0.1.23 head field 10)
    try { if (ah.length > 10) rbp = Integer.parseInt(ah[10].trim()); } catch (Throwable x2) { rbp = 0; }''')
rep('''    b.set("#SkyyTrAdM.Text", slotOpen ? "Modifier slot " + (msl + 1) + (cur.length() > 0 ? " - now " + cur : " - empty") : "Modifier slot " + (msl + 1) + " - unlock M" + ((Integer) ap[ab0 + 5]).intValue() + (msl == 0 ? "A" : "B") + " in the tree");''',
    '''    b.set("#SkyyTrAdM.Text", rbp > 0 ? "Rebirth: " + rbp + " upgrade" + (rbp == 1 ? "" : "s") + " - press Max Up" : (slotOpen ? "Modifier slot " + (msl + 1) + (cur.length() > 0 ? " - now " + cur : " - empty") : "Modifier slot " + (msl + 1) + " - unlock M" + ((Integer) ap[ab0 + 5]).intValue() + (msl == 0 ? "A" : "B") + " in the tree"));''')
rep('''      int rs = (!slotOpen || !un) ? 0 : (inThis ? 1 : (inOther && "1".equals(f[11]) ? 2 : (inOther ? 3 : 4)));''',
    '''      int rs = (!slotOpen || !un) ? 0 : (inThis ? 1 : (inOther && "1".equals(f[11]) ? 2 : (inOther ? 3 : 4)));
      if (rbp > 0 && un) rs = 5;   // 0.3.8: place the rebirth upgrade first (FIX 2: only on an unlocked modifier; the slot does not matter -
                                   // the extra level belongs to the modifier of this ability, not to a slot)''')
rep('''      if (rs == 2 || rs == 4) ev.addEventBinding(@BT@.Activating, "#SkyyTrAq" + k, @EVD@.of("a", "trme" + k));''',
    '''      if (rs == 2 || rs == 4) ev.addEventBinding(@BT@.Activating, "#SkyyTrAq" + k, @EVD@.of("a", "trme" + k));
      if (rs == 5) ev.addEventBinding(@BT@.Activating, "#SkyyTrAq" + k, @EVD@.of("a", "trmx" + k));   // 0.3.8''')
rep('''  if (act.equals("unequip")) return said(@PKG@.TreeClass.ado(u, "unequip", id, String.valueOf(this.mslot), csv));
  return "";''', '''  if (act.equals("unequip")) return said(@PKG@.TreeClass.ado(u, "unequip", id, String.valueOf(this.mslot), csv));
  if (act.equals("rbpick")) {   // 0.3.8: a rebirth upgrade -> +1 max level on that modifier
    String[] rows = @PKG@.TreeClass.amods(u, id, csv);
    if (rows == null || k + 1 >= rows.length) return "Ability: that modifier is gone - try again";
    String mid = rows[k + 1].split("\\\\|", -1)[0];
    return said(@PKG@.TreeClass.ado(u, "rbpick", id, mid, csv));
  }
  return "";''')
rep('''        if (data.indexOf("trme" + mk + "\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "equip", this.aslot, mk); rebuild(); return; }''',
    '''        if (data.indexOf("trme" + mk + "\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "equip", this.aslot, mk); rebuild(); return; }
        if (data.indexOf("trmx" + mk + "\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "rbpick", this.aslot, mk); rebuild(); return; }   // 0.3.8''')

# ================================================================================================================ TreeRb: rebirth:part:trees
rep('''# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")''', '''# ================= 0.3.8 TreeRb: the rebirth participant rebirth:part:trees (Rebirth-Spec 4.2 / 4.3 / 5.2 / 5.3; the SkyyCoins 0.1.7 shape) ====
trb = pool.makeClass(PKG + ".TreeRb")
trb.addInterface(pool.get("java.util.function.Function"))
C(trb, "public TreeRb() { }")
F(trb, "public static final java.util.concurrent.atomic.AtomicLong APPLIED = new java.util.concurrent.atomic.AtomicLong();")
F(trb, "public static volatile int FAIL_WRITE = 0;")   # HARNESS SEAM ONLY: the next N commit writes answer failed
M(trb, r"""
public static java.nio.file.Path home() {
  java.nio.file.Path d = @PKG@.TreeStore.DIR;
  return d == null ? null : d.getParent();
}""")
M(trb, r"""
public static boolean validKey(String k) {
  return k != null && k.length() >= 36 && k.length() <= 48 && k.matches("[0-9a-fA-F-]{36}(-p[0-9]{1,4})?");
}""")
M(trb, r"""
public static boolean validTx(String tx) {
  return tx != null && tx.matches("tx[0-9]{13}-[0-9a-f]{6}");
}""")
M(trb, r"""
public static java.util.UUID owner(String k) {
  try { return java.util.UUID.fromString(k.substring(0, 36)); } catch (Throwable t) { return null; }
}""")
M(trb, r"""
public static java.nio.file.Path staged(String k, String tx) {
  return home().resolve("rebirth").resolve(k + ".rb-" + tx + ".properties");
}""")
M(trb, r"""
public static void writeProps(java.nio.file.Path f, java.util.Properties p, String comment) throws java.io.IOException {
  java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
  java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
  try { p.store(out, comment); out.flush(); out.getFD().sync(); } finally { out.close(); }
  @PKG@.TreeStore.moveRetry(tmp, f);
}""")
M(trb, r"""
public static java.util.Properties readProps(java.nio.file.Path f) {
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return null;
    return @PKG@.TreeStore.readLocked(f);
  } catch (Throwable t) { return null; }
}""")
M(trb, r"""
public static void deleteTree(java.io.File f) {
  if (f == null) return;
  java.io.File[] c = f.listFiles();
  if (c != null) for (int i = 0; i < c.length; i++) deleteTree(c[i]);
  f.delete();
}""")
M(trb, r"""
public static String decision(String tx) {
  try {
    Object f = @PKG@.TreeStore.bridge().get("rebirth:fn:decision");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(tx);
      if (r instanceof String) return (String) r;
    }
  } catch (Throwable t) { }
  return "unknown";
}""")
M(trb, r"""
public static String cleanStale(String k, String tx) {
  java.io.File[] fs = home().resolve("rebirth").toFile().listFiles();
  if (fs == null) return null;
  String pre = k + ".rb-";
  for (int i = 0; i < fs.length; i++) {
    String nm = fs[i].getName();
    if (!nm.startsWith(pre)) continue;
    String old;
    if (nm.endsWith(".properties")) old = nm.substring(pre.length(), nm.length() - 11);
    else if (nm.endsWith(".properties.tmp")) old = nm.substring(pre.length(), nm.length() - 15);
    else continue;
    if (old.equals(tx)) continue;
    if ("commit".equals(decision(old))) return "err:an older rebirth of this profile is still finishing (" + old + ")";
    fs[i].delete();
  }
  return null;
}""")
# the trees a rebirth clears: every template tree but Exploration (Rebirth-Spec 7.2 U5 - its XP and Dust stay)
M(trb, r"""
public static boolean resets(int t) {
  return t >= 0 && t < @PKG@.TreeDefs.NT && !"Exploration".equals(@PKG@.TreeDefs.TREES[t]);
}""")
M(trb, r"""
public static int[] count(@PKG@.TreeData d) {
  int[] r = new int[2];
  if (d == null) return r;
  for (int i = 0; i < @PKG@.TreeDefs.N; i++) if (resets(i / 12) && d.lv[i] > 0) r[0] = r[0] + 1;
  for (int j = 0; j < d.cown.length; j++) if (d.cown[j]) r[1] = r[1] + 1;
  return r;
}""")
M(trb, r"""
public static @PKG@.TreeData dataOf(String k) {
  java.util.UUID u = owner(k);
  if (u == null) return null;
  return @PKG@.TreeStore.dataK(k, u);
}""")
M(trb, r"""
public static void backup(String k, String tx) throws java.io.IOException {
  java.nio.file.Path dir = home().resolve("rebirth-backup").resolve(k);
  java.nio.file.Path f = @PKG@.TreeStore.DIR.resolve(k + ".properties");
  java.nio.file.Files.createDirectories(dir.resolve(tx), new java.nio.file.attribute.FileAttribute[0]);
  java.util.Properties mem = @PKG@.TreeStore.snap(k);   // FIX (critic): memory first - an unsaved buy / Dust credit is in the backup too
  if (mem != null) writeProps(dir.resolve(tx).resolve(k + ".properties"), mem, "SkyyTrees rebirth backup of players/" + k + ".properties before " + tx + " - restore by hand while the server is stopped");
  else if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
    synchronized (@PKG@.TreeStore.IO) {
      java.nio.file.Files.copy(f, dir.resolve(tx).resolve(k + ".properties"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    }
  }
  java.io.File[] all = dir.toFile().listFiles();
  if (all == null || all.length <= 3) return;
  java.util.Arrays.sort(all);
  for (int i = 0; i < all.length - 3; i++) deleteTree(all[i]);
}""")
M(trb, r"""
public static String prepare(String k, String tx, boolean write) {
  @PKG@.TreeData d = dataOf(k);
  if (d == null) return "err:bad profile key";
  if (d.bad) return "err:the tree file of " + k + " cannot be read";
  if (tx.equals(d.rbTx)) return "err:already committed";
  int[] c = count(d);
  String facts = "ok:nodes=" + c[0] + ";classPicks=" + c[1];
  if (!write) return facts;
  String st = cleanStale(k, tx);
  if (st != null) return st;
  try {
    backup(k, tx);
    java.util.Properties sp = new java.util.Properties();
    sp.setProperty("tx", tx);
    sp.setProperty("pkey", k);
    sp.setProperty("nodes", String.valueOf(c[0]));
    sp.setProperty("classPicks", String.valueOf(c[1]));
    writeProps(staged(k, tx), sp, "SkyyTrees rebirth " + tx + " - staged (the tree file is untouched until the commit)");
  } catch (Throwable t) { return "err:could not write the staged file: " + t; }
  return facts;
}""")
# the reset itself, under the TreeStore monitor (the same lock every tree write takes)
M(sto, r"""
public static synchronized void rbReset(@PKG@.TreeData d, String tx) {
  for (int i = 0; i < @PKG@.TreeDefs.N; i++) {
    if (!@PKG@.TreeRb.resets(i / 12)) continue;
    d.lv[i] = 0;
    d.off[i] = false;
  }
  for (int t = 0; t < @PKG@.TreeDefs.NT; t++) if (@PKG@.TreeRb.resets(t)) d.credit[t] = 0L;
  for (int ci = 0; ci < @PKG@.TreeClass.NC; ci++) {
    boolean any = false;
    for (int n = 0; n < @PKG@.TreeClass.NN; n++) if (d.cown[ci * @PKG@.TreeClass.NN + n]) any = true;
    if (!any) continue;
    String o = d.corder[ci];
    for (int n = 0; n < @PKG@.TreeClass.NN; n++) if (d.cown[ci * @PKG@.TreeClass.NN + n]) o = @PKG@.TreeDefs.orderEdit(o, @PKG@.TreeClass.NID[n], true);
    d.corder[ci] = o;
    d.crb[ci] = true;
  }
  d.rbTx = tx;
}""")
M(trb, r"""
public static boolean flush(String k) {
  if (FAIL_WRITE > 0) { FAIL_WRITE = FAIL_WRITE - 1; return false; }
  return @PKG@.TreeStore.saveSync(k);
}""")
M(trb, r"""
public static String commit(String k, String tx) {
  @PKG@.TreeData d = dataOf(k);
  if (d == null) return "err:bad profile key";
  if (d.bad) return "err:the tree file of " + k + " cannot be read";
  java.nio.file.Path sp = staged(k, tx);
  if (tx.equals(d.rbTx)) {
    if (!flush(k)) return "err:could not save the tree file of " + k + " (retried)";
    try { java.nio.file.Files.deleteIfExists(sp); } catch (Throwable t) { }
    return "done";
  }
  java.util.Properties p = readProps(sp);
  if (p == null || !tx.equals(p.getProperty("tx"))) return "err:no staged file for " + tx;
  @PKG@.TreeStore.rbReset(d, tx);
  if (!flush(k)) {
    @PKG@.TreeStore.dirty(k);
    return "err:could not save the tree file of " + k + " (the reset is in memory; retried)";
  }
  try { java.nio.file.Files.deleteIfExists(sp); } catch (Throwable t) { }
  java.util.UUID u = owner(k);
  try { if (u != null && k.equals(@PKG@.TreeStore.pkey(u))) @PKG@.TreeFx.refresh(u); } catch (Throwable t) { }
  APPLIED.incrementAndGet();
  return "ok";
}""")
M(trb, r"""
public static String abort(String k, String tx) {
  @PKG@.TreeData d = dataOf(k);
  if (d != null && tx.equals(d.rbTx)) return "err:already committed";
  try {
    java.nio.file.Path sp = staged(k, tx);
    java.nio.file.Files.deleteIfExists(sp);
    java.nio.file.Files.deleteIfExists(sp.resolveSibling(sp.getFileName().toString() + ".tmp"));
  } catch (Throwable t) { return "err:" + t; }
  return "done";
}""")
M(trb, r"""
public static String status(String k, String tx) {
  @PKG@.TreeData d = dataOf(k);
  if (d != null && tx.equals(d.rbTx)) return "committed";
  return java.nio.file.Files.exists(staged(k, tx), new java.nio.file.LinkOption[0]) ? "staged" : "none";
}""")
M(trb, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return "err:bad arguments";
    Object[] a = (Object[]) o;
    if (a.length < 3 || !(a[0] instanceof String) || !(a[1] instanceof String) || !(a[2] instanceof String)) return "err:bad arguments";
    String op = (String) a[0];
    String k = ((String) a[1]).trim();
    String tx = (String) a[2];
    if (!validKey(k)) return "err:bad profile key";
    if (!validTx(tx)) return "err:bad txid";
    if (@PKG@.TreeStore.DIR == null || home() == null) return "err:SkyyTrees is not started";
    if ("measure".equals(op)) return prepare(k, tx, false);
    if ("prepare".equals(op)) return prepare(k, tx, true);
    if ("commit".equals(op)) return commit(k, tx);
    if ("abort".equals(op)) return abort(k, tx);
    if ("status".equals(op)) return status(k, tx);
    return "err:unknown op " + op;
  } catch (Throwable t) { return "err:" + t; }
}""")

# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")''')
# a fsync'd save of one profile (the rebirth commit): TreeStore.saveNow's shape with the tmp synced first
rep('''M(sto, r"""
public static boolean saveNow(String k) {''', '''M(sto, r"""
public static boolean saveSync(String k) {
  java.util.Properties p = snap(k);
  if (p == null || DIR == null) return false;
  try {
    synchronized (IO) {
      java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Path tmp = DIR.resolve(k + ".properties.rbtmp");
      java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
      try { p.store(out, "SkyyTrees - one profile's tree levels (rebirth write)"); out.flush(); out.getFD().sync(); } finally { out.close(); }
      moveRetry(tmp, DIR.resolve(k + ".properties"));
    }
    DIRTY.remove(k);
    return true;
  } catch (Throwable t) { @PKG@.TreeCfg.warn("could not save tree file " + k + " (rebirth): " + t); return false; }
}""")
M(sto, r"""
public static boolean saveNow(String k) {''')
rep('''  b.put("tree:fn:abil", @PKG@.TreeStore.AFN);   // 0.3.7: SkyyClasses 0.1.22 - the intact class nodes (its ability gate)''',
    '''  b.put("tree:fn:abil", @PKG@.TreeStore.AFN);   // 0.3.7: SkyyClasses 0.1.22 - the intact class nodes (its ability gate)
  @PKG@.TreeStore.RBFN = new @PKG@.TreeRb();
  b.put("rebirth:part:trees", @PKG@.TreeStore.RBFN);   // 0.3.8: the rebirth participant (SkyyRebirth's two-phase commit)''')
rep('''    if (@PKG@.TreeStore.AFN != null) b.remove("tree:fn:abil", @PKG@.TreeStore.AFN);   // 0.3.7''',
    '''    if (@PKG@.TreeStore.AFN != null) b.remove("tree:fn:abil", @PKG@.TreeStore.AFN);   // 0.3.7
    if (@PKG@.TreeStore.RBFN != null) b.remove("rebirth:part:trees", @PKG@.TreeStore.RBFN);   // 0.3.8''')
rep('''F(sto, "public static Object AFN;")   # 0.3.7: tree:fn:abil''', '''F(sto, "public static Object AFN;")   # 0.3.7: tree:fn:abil
F(sto, "public static Object RBFN;")  # 0.3.8: rebirth:part:trees''')
rep('''ALL = (defs, cfg, dat, sto, stk, calc, cls, fx, swg, msg, abil, gat, tfn, afn, bfn, ffn, dmg, tick, svr, ops, cops, page, kitc, mig, mig32, mig33, vcmd, qcmd, rcmd, scmd, pcmd, cmd, pl)''',
    '''ALL = (defs, cfg, dat, sto, stk, calc, cls, fx, swg, msg, abil, gat, tfn, afn, bfn, ffn, dmg, tick, svr, ops, cops, page, kitc, mig, mig32, mig33, vcmd, qcmd, rcmd, scmd, pcmd, cmd, trb, pl)   # 0.3.8: + TreeRb''')

# ================================================================================================================ FIX ROUND (critics 2026-10-14)
# A1: after a rebirth (Class.<Class>.rb=1) the gated picks made a class respec free / cheap - the price follows the OWNED picks, at least the
# class level whose AP pay for them (the level that bought them)
rep('''  boolean[] it = @PKG@.TreeClass.intact(d, ci);
  int sp = @PKG@.TreeClass.spent(it, ci);
  if (sp <= 0) return 0L;
  if (@PKG@.TreeClass.ap(lvl) - sp < 0) return 0L;
  return @PKG@.TreeClass.respecPrice(lvl);''', '''  if (d.crb[ci]) return @PKG@.TreeClass.respecPrice(@PKG@.TreeClass.rbPriceLvl(d, ci, lvl));   // 0.3.8 fix: kept picks are paid for
  boolean[] it = @PKG@.TreeClass.intact(d, ci);
  int sp = @PKG@.TreeClass.spent(it, ci);
  if (sp <= 0) return 0L;
  if (@PKG@.TreeClass.ap(lvl) - sp < 0) return 0L;
  return @PKG@.TreeClass.respecPrice(lvl);''')
rep('''M(cls, r"""
public static long respecPrice(int lvl) {''', '''# 0.3.8 fix: the respec price level of a rebirth-gated class tree = the class level whose AP cover every OWNED pick, never below the
# level now (0 = nothing paid is owned)
M(cls, r"""
public static int rbPriceLvl(@PKG@.TreeData d, int ci, int lvl) {
  if (d == null || ci < 0 || ci >= NC) return 0;
  int so = spent(intactOf(ownOf(d, ci), ci), ci);
  if (so <= 0) return 0;
  int L = lvl < 1 ? 1 : lvl;
  int capAp = ap(1000000);   // FIX 2 (critic): picks above the AP cap (an admin lowered class.ap.max) = priced at the cap level, never ~5000 levels
  if (so > capAp) so = capAp;
  int top = L + 5000;
  while (ap(L) < so && L < top) L++;
  return L;
}""")
M(cls, r"""
public static long respecPrice(int lvl) {''')
rep('''(price > 0L ? "it costs " + @PKG@.TreeDefs.grp(price) + " coins (" + @PKG@.TreeClass.CSKILL[ci] + " " + lvl + " x " + @PKG@.TreeCfg.C_RESPEC_PER + ")" : "free"));''',
    '''(price > 0L ? "it costs " + @PKG@.TreeDefs.grp(price) + " coins (" + @PKG@.TreeClass.CSKILL[ci] + " " + (@PKG@.TreeCfg.C_RESPEC_PER > 0 ? price / @PKG@.TreeCfg.C_RESPEC_PER : (long) lvl) + " x " + @PKG@.TreeCfg.C_RESPEC_PER + ")" : "free"));''')
# A3: a negative Dust balance respecs a skill tree free only while SkyyRebirth answers the multiplier (or the profile never rebirthed)
rep('''  boolean neg = bal[0] < bal[1] || bal[2] < bal[3];''',
    '''  boolean neg = bal[0] < bal[1] || (bal[2] < bal[3] && (d.rbTx == null || @PKG@.TreeCalc.dustKnown(u, t)));   // 0.3.8 fix: no free respec off a missing Dust multiplier''')
# FIX 2 (critic): a rebirth leaves the class at level 0 until its first XP - the gated price must not be skipped by the lvl < 1 return
rep('''  if (probe || d == null || d.bad || ci < 0 || lvl < 1) return 0L;
  if (freeOf(d, ci, probe)) return 0L;
  if (d.crb[ci]) return @PKG@.TreeClass.respecPrice(@PKG@.TreeClass.rbPriceLvl(d, ci, lvl));   // 0.3.8 fix: kept picks are paid for''',
    '''  if (probe || d == null || d.bad || ci < 0) return 0L;
  if (freeOf(d, ci, probe)) return 0L;
  if (d.crb[ci]) return @PKG@.TreeClass.respecPrice(@PKG@.TreeClass.rbPriceLvl(d, ci, lvl));   // 0.3.8 fix: kept picks are paid for (also at level 0)
  if (lvl < 1) return 0L;''')
# C4: the Monk and the Assassin have theirs too
rep('''  if ("noabil".equals(st)) return CLASSES[ci] + " abilities come in a later build - the Mage and the Priest have theirs first.";''',
    '''  if ("noabil".equals(st)) return CLASSES[ci] + " abilities come in a later build - the Mage, Priest, Monk and Assassin have theirs.";''')

# ================================================================================================================ done
assert s.count("registerSystem(") == REG0, "no new system"
assert s.count("registerCommand(") == CMD0, "no new command"
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote %s (%d changes, %d lines)" % (dst, len(CHANGES), s.count(LF)))
