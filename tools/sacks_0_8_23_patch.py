"""Derive SkyySacks/build_skyysacks_0.8.23.py from the SET pin 0.8.22 (the GENERATED build_skyysacks_0.8.22.py; edit THIS file, then
regenerate: python tools/sacks_0_8_23_patch.py; never re-run sacks_0_8_22_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.22 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_23_patch.py   then   python SkyySacks/build_skyysacks_0.8.23.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.23.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.23 (2026-10-18) = THE FURNACE PAGE SHOWS QUEUE, FUEL AND READY (lean round, docs/answered/ui.md 2026-10-18).
Skyy (screenshot of Crafting -> Furnace): "the furnace should show whats in queue, and whats in the fuel. and show the fule section in red if
you dont have enough for the whole queue" + "with a time till done, and show whats ready to collect too".
  1. The two one-line summaries ("Queue - Copper Ingot x53 + ..." and "Ready - 1 Ingredient Charcoal") become THREE side-by-side scroll lists
     (#SkyyPLists, 166 px): QUEUE (one row per queued batch: icon when the recipe's output is known, name, xN, the batch's time, "done in X"
     counted from now with the batches ahead included; the header "Queue 71 / 256 - done in 12m 56s" + Cancel queue), FUEL (one row per
     loaded fuel item: icon, name, xN, its burn time; a "Burning now" row for the lit remainder), READY TO COLLECT (one row per finished item:
     icon, name, xN; the header + Collect). Short lists use bigger rows (skyyui.grow_row_sizes, Skyy rule 7); at most 200 rows, then a line.
  2. The FUEL header = a requirement line (research/Menu-Pattern.md rule 9): "Fuel 16m 10s : queue 12m 56s" GREEN when the loaded fuel's
     burn time (the Furnace Charm's faster burn included) covers the whole queue (equal = enough), RED + "(need 3m 20s)" when it does not.
     A queue row whose "done in" lies past the fuel turns red too. Review fix: green needs 1 ms to spare per queued unit
     (with a Charm fuel bonus advanceC's per-step floor can stall the last unit at exact equality). Benches that need no fuel / the Eternal Flame: "Needs no fuel" (gold).
  3. Unload fuel moves to the end of the Load fuel row (the fuel controls together); Collect / Cancel queue sit on their list's header.
     Every button keeps its id and event (pcollect / pcancel / punload / pfuel:<i> / paddf). The ADD FUEL picker view keeps 0.8.22's layout.
  New ProcBench readers (no state change): outId, queueRows, fuelRows, fuelEffMs, fuelEnough, fuelNeedMs, fuelState, knownId (review
  fix: an id the server does not know - an uninstalled mod's saved id - draws no ItemIcon), itemName (review fix: one proper name in all
  three lists, = outName's). No saved data, no command, no
  config, no lang change. The recipe list below is ~1 row shorter (it scrolls).
  4. (no code change) RecipeCmp's /craft sort table is baked from the COMMITTED tools/tier_tags.py, which gained rows after 0.8.22 was built
     (SkyyGear 0.3.23 forever tools, SkyyArmory 0.1.33 / 0.1.34 metal weapons; rows only, no number moves) - those items now sort by tier too.
     Build with the committed table: on 2026-10-18 another builder's uncommitted TT_VERSION 3 was in the working tree (0.8.22's assert stops).
  ROLLBACK to 0.8.22: safe (page layout only).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.22.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.23.py"))
assert P.has('VERSION = "0.8.22"\n') and P.has('lbl("SkyyPQueue", 1552, 22, L_CAPC)') and P.has("public synchronized long fuelTotalMs() {"), \
    "not the live generated SkyySacks 0.8.22"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
EV0 = sorted(l.strip() for l in P.s.split("\n") if "addEventBinding" in l and '"#SkyyP' in l)
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.23 (2026-10-18)"):].rstrip() + "\n"

# ---- header, version
P.rep('''  ROLLBACK to 0.8.21: safe (sort order + the row tag numbers only).
"""
''', '''  ROLLBACK to 0.8.21: safe (sort order + the row tag numbers only).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.22"\n', 'VERSION = "0.8.23"\n')

# ---- ProcBench readers (after fuelTotalMs; no state change)
P.rep('''    t += Math.round(fuelQuality((String) e.getKey()) * 1000.0) * (long) ((Integer) e.getValue()).intValue();
  }
  return t;
}""", pben))
''', '''    t += Math.round(fuelQuality((String) e.getKey()) * 1000.0) * (long) ((Integer) e.getValue()).intValue();
  }
  return t;
}""", pben))
# 0.8.23 (Skyy "the furnace should show whats in queue, and whats in the fuel. and show the fule section in red if you dont have enough for
# the whole queue" + "with a time till done, and show whats ready to collect too"): readers for the Furnace page's three lists
pben.addMethod(CtNewMethod.make(f"""
public static String outId(String recipeId) {{
  try {{
    Object o = {CRR}.getAssetMap().getAsset(recipeId);
    if (o instanceof {CRR}) {{
      {MQ} q = (({CRR}) o).getPrimaryOutput();
      if (q != null && q.getItemId() != null) return q.getItemId();
    }}
  }} catch (Throwable t) {{ }}
  return null;
}}""", pben))
# (review fix) an id the server knows (an uninstalled mod's saved id never reaches an ItemIcon), null = unknown
pben.addMethod(CtNewMethod.make("""
public static String knownId(String id) {
  if (id == null) return null;
  try { return item(id) != null ? id : null; } catch (Throwable t) { return null; }
}""", pben))
# (review fix) the proper item name for every list (= outName's: the real display name, else the id spelled out)
pben.addMethod(CtNewMethod.make(f"""
public static String itemName(String id) {{
  if (id == null) return "?";
  String dn = {PKG}.SackDefs.dname(id);
  return dn != null ? dn : nm(id);
}}""", pben))
# one row per queued batch: [0] output item id (null = unknown), [1] name, [2] count, [3] this batch's ms (the running unit's progress off),
# [4] done in ms from now (the batches ahead included; the last row = queueMs)
pben.addMethod(CtNewMethod.make(f"""
public synchronized java.util.ArrayList queueRows() {{
  java.util.ArrayList l = new java.util.ArrayList();
  long acc = 0L;
  for (int i = 0; i < this.queue.size(); i++) {{
    {PKG}.ProcJob j = ({PKG}.ProcJob) this.queue.get(i);
    long b = charmMs(j.unitMs, this.cTime) * (long) j.count;
    if (i == 0) b -= this.progress;
    if (b < 0L) b = 0L;
    acc += b;
    l.add(new Object[] {{ outId(j.recipe), outName(j.recipe), Integer.valueOf(j.count), Long.valueOf(b), Long.valueOf(acc) }});
  }}
  return l;
}}""", pben))
# the loaded fuel's burn time as it will really burn (the Furnace Charm's faster burn = describe()'s fuel figure)
pben.addMethod(CtNewMethod.make("""
public synchronized long fuelEffMs() {
  long f = fuelTotalMs();
  if (this.cFuel > 0) f = (f * 100L) / (100L + (long) this.cFuel);
  return f;
}""", pben))
# one row per loaded fuel item: [0] id (null = the lit remainder), [1] name, [2] count (0 = the lit remainder), [3] its burn ms
pben.addMethod(CtNewMethod.make("""
public synchronized java.util.ArrayList fuelRows() {
  java.util.ArrayList l = new java.util.ArrayList();
  long cf = (long) this.cFuel;
  if (this.fuelMs > 0L) l.add(new Object[] { null, "Burning now", Integer.valueOf(0), Long.valueOf(cf > 0L ? (this.fuelMs * 100L) / (100L + cf) : this.fuelMs) });
  java.util.Iterator it = this.fuel.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String id = (String) e.getKey();
    int q = ((Integer) e.getValue()).intValue();
    long ms = Math.round(fuelQuality(id) * 1000.0) * (long) q;
    if (cf > 0L) ms = (ms * 100L) / (100L + cf);
    l.add(new Object[] { id, itemName(id), Integer.valueOf(q), Long.valueOf(ms) });
  }
  return l;
}""", pben))
# Skyy "red if you dont have enough for the whole queue": green only with 1 ms to spare per queued unit (review fix: with a Furnace Charm fuel
# bonus advanceC's per-step floor can stall the last unit at exact equality - 87 of 300k random cases ran dry while equal looked green)
pben.addMethod(CtNewMethod.make("""
public static boolean fuelEnough(long fuelMs, long queueMs, int units) { return fuelMs >= queueMs + (long) (units < 0 ? 0 : units); }""", pben))
# the fuel the whole queue needs (queueMs + 1 ms per queued unit)
pben.addMethod(CtNewMethod.make("""
public synchronized long fuelNeedMs() { return queueMs() + (long) queued(); }""", pben))
# 0 = needs no fuel (the bench, or the Eternal Flame), 1 = the fuel covers the whole queue (green), 2 = short (red)
pben.addMethod(CtNewMethod.make("""
public synchronized int fuelState() {
  if (!this.needsFuel || this.cEternal) return 0;
  return fuelEnough(fuelEffMs(), queueMs(), queued()) ? 1 : 2;
}""", pben))
''')

# ---- the sizes: the three lists replace the queue line (22) + the output row (46)
PL = '''# 0.8.23: the Furnace page's QUEUE / FUEL / READY lists (#SkyyPLists): a 36 px header (+ its button) over a 124 px scroll list, 6 below
PL_HD, PL_LH = 36, 124
PL_H = PL_HD + PL_LH
PL_ADD = PL_H + 6                    # what the lists add to the page (the queue line 22 + the output row 46 go)
PQ_W, PF_W, PR_W = 600, 520, 400     # + two 16 px gaps = the 1552 px content
assert PQ_W + PF_W + PR_W + 2 * 16 == CSH.inner_w
PL_HS = SUI.grow_row_sizes(PL_LH - 8, 36, gap=3)          # Skyy rule 7: a few rows grow (36 / 52 / 55)
assert PL_HS[0] == 36 and PL_HS[2] <= 64, PL_HS
PL_ICO = 48                                                 # the icon frame: row - 6, at most 48
# the text columns of each row (icon frame + 8 + these, inside the well 4 + the scrollbar 12 + the row padding 12)
PQ_WS, PF_WS, PR_WS = [210, 64, 100, 130], [220, 80, 110], [200, 90]
for _w, _ws in ((PQ_W, PQ_WS), (PF_W, PF_WS), (PR_W, PR_WS)):
    assert 12 + PL_ICO + 8 + sum(_ws) <= _w - 8 - 12, (_w, _ws)
'''
P.rep('''CP_BODY_H = {  # 0.8.15: the tallest content of each view (the tabs are the sub-tab row, the foot is the footer) - every one fits CSH.inner_h
    "craft": 40 + 22 + 6 * 98, "camp": 22 + 24 + 6 * 98,           # the search / materials (/ campfire) lines + about 6 rows of 98
    "proc": 22 + 26 + 22 + 18 + 22 + 46 + 42 + 4 * 98,              # the materials line, the Furnace lines (+ fuel) + 4 rows
''', PL + '''CP_BODY_H = {  # 0.8.15: the tallest content of each view (the tabs are the sub-tab row, the foot is the footer) - every one fits CSH.inner_h
    "craft": 40 + 22 + 6 * 98, "camp": 22 + 24 + 6 * 98,           # the search / materials (/ campfire) lines + about 6 rows of 98
    "proc": 22 + 26 + 22 + 18 + PL_ADD + 42 + 3 * 98,               # 0.8.23: the materials line, the Furnace lines, the 3 lists (+ fuel) + 3 rows
''')
P.rep('''_cp_min_list = CSH.inner_h - (22 + 26 + 22 + 18 + 22 + 46 + 42) - 4
''', '''_cp_min_list = CSH.inner_h - (22 + 26 + 22 + 18 + PL_ADD + 42) - 4   # 0.8.23: the 3 lists
''')
# the list markup + the row styles
P.rep('''for _n, _v in CP_CONST.items():
    assert '\\\\' not in _v and "\\n" not in _v, _n
''', '''# 0.8.23: the three scroll lists (kit) + the requirement colours (Menu-Pattern rule 9: green met, red not) + the row name style
for _k, _i in (("PL_PQ", "SkyyPQList"), ("PL_PFF", "SkyyPFuList"), ("PL_PR", "SkyyPRList")):
    _m = SUI.scroll_list(_i, h=PL_LH, well=True)
    assert "TopScrolling" in _m and "Height: %d" % PL_LH in _m
    SUI.check_markup(_m)
    CP_CONST[_k] = _m
CP_CONST.update({"L_OKH": _lst(15, "have", True), "L_BADH": _lst(15, "outOfStock", True), "L_ROWN": _lst(15, "white", True)})
for _n, _v in CP_CONST.items():
    assert '\\\\' not in _v and "\\n" not in _v, _n
''')
P.rep('''cpg.addField(CtField.make("public static final int[] FUELHS = new int[] { %s };" % ", ".join(str(_h) for _h in CP_FUEL_HS), cpg))   # 0.8.15
''', '''cpg.addField(CtField.make("public static final int[] FUELHS = new int[] { %s };" % ", ".join(str(_h) for _h in CP_FUEL_HS), cpg))   # 0.8.15
# 0.8.23: the Furnace page's three lists
cpg.addField(CtField.make("public static final int[] PLHS = new int[] { %s };" % ", ".join(str(_h) for _h in PL_HS), cpg))
for _n, _ws in (("PQWS", PQ_WS), ("PFWS", PF_WS), ("PRWS", PR_WS)):
    cpg.addField(CtField.make("public static final int[] %s = new int[] { %s };" % (_n, ", ".join(str(_x) for _x in _ws)), cpg))
for _n, _v in (("PLH", PL_H), ("PLLH", PL_LH), ("PLADD", PL_ADD), ("PLICO", PL_ICO), ("PLMAX", 200), ("PQW", PQ_W), ("PFW", PF_W), ("PRW", PR_W)):
    cpg.addField(CtField.make("public static final int %s = %d;" % (_n, _v), cpg))
''')

# ---- the row + the lists (before buildProc)
P.rep('''cpg.addMethod(CtNewMethod.make(jt(r"""
public void buildProc(@UCB@ b, @UEB@ ev, @PLA@ p, java.util.UUID u, String k) {''', '''# 0.8.23: one list row - the item icon in a slot frame (a gap when the id is unknown), then the text columns
cpg.addMethod(CtNewMethod.make(jt(r"""
public static void procRow(@UCB@ b, String list, String rid, int rh, String id, String[] tx, int[] w, String[] st) {
  b.appendInline("#" + list, "Group #" + rid + " { Anchor: (Height: " + rh + ", Bottom: 3); LayoutMode: Left; Padding: (Horizontal: 6); Background: " + BG_ROW + "; }");
  int fr = rh - 6;
  if (fr > PLICO) fr = PLICO;
  if (id != null) b.appendInline("#" + rid, "Group { Anchor: (Width: " + fr + ", Height: " + fr + ", Top: " + ((rh - fr) / 2) + "); Padding: (Full: 2); Background: " + BG_SLOT + "; ItemIcon { Anchor: (Width: " + (fr - 4) + ", Height: " + (fr - 4) + "); ItemId: \\"" + @PKG@.SacksPage.safe(id) + "\\"; } }");
  else b.appendInline("#" + rid, gap(fr));
  b.appendInline("#" + rid, gap(8));
  for (int i = 0; i < tx.length && i < w.length; i++) {
    b.appendInline("#" + rid, lbl(rid + "t" + i, w[i], rh, st[i]));
    b.set("#" + rid + "t" + i + ".Text", tx[i] == null ? "" : tx[i]);
  }
}"""), cpg))
# 0.8.23: the list's end - the empty state (Menu-Pattern 3.4: a centred caption line) or "+ N more" past PLMAX rows
cpg.addMethod(CtNewMethod.make(jt(r"""
public static void procEnd(@UCB@ b, String list, String id, int n, int drawn, String empty) {
  if (n == 0) {
    b.appendInline("#" + list, lbl(id + "None", 360, 40, L_CAPC));
    b.set("#" + id + "None.Text", empty);
  } else if (n > drawn) {
    b.appendInline("#" + list, lbl(id + "More", 360, 32, L_CAPC));
    b.set("#" + id + "More.Text", "+ " + (n - drawn) + " more");
  }
}"""), cpg))
# 0.8.23 (Skyy "the furnace should show whats in queue, and whats in the fuel. and show the fule section in red if you dont have enough for
# the whole queue" + "with a time till done, and show whats ready to collect too"): QUEUE | FUEL | READY TO COLLECT, side by side
cpg.addMethod(CtNewMethod.make(jt(r"""
public void procLists(@UCB@ b, @UEB@ ev, @PKG@.ProcBench view) {
  java.util.ArrayList q = view.queueRows();
  java.util.ArrayList f = view.fuelRows();
  java.util.ArrayList r = view.outList();
  long qms = view.queueMs();
  long fms = view.fuelEffMs();
  long fneed = view.fuelNeedMs();
  int fst = view.fuelState();
  long units = 0L;
  b.appendInline("#SkyyCraftBody", "Group #SkyyPLists { Anchor: (Height: " + PLH + ", Bottom: 6); LayoutMode: Left; }");
  // QUEUE: one row per batch, its time + done in (from now); the header = the whole queue's done in + Cancel queue
  b.appendInline("#SkyyPLists", "Group #SkyyPQCol { Anchor: (Width: " + PQW + ", Height: " + PLH + "); LayoutMode: Top; }");
  b.appendInline("#SkyyPQCol", "Group #SkyyPQHd { Anchor: (Height: 36); LayoutMode: Left; }");
  b.appendInline("#SkyyPQHd", lbl("SkyyPQHead", PQW - 178, 32, L_HEAD));
  b.set("#SkyyPQHead.Text", q.isEmpty() ? "Queue - empty" : ("Queue " + view.queued() + " / " + @PKG@.ProcBench.QUEUE_CAP + " - done in " + @PKG@.ProcBench.dur(qms)));
  b.appendInline("#SkyyPQHd", gap(8));
  b.appendInline("#SkyyPQHd", btn("SkyyPCancel", "Cancel queue", 170, 0, B_SEC));
  ev.addEventBinding(@BT@.Activating, "#SkyyPCancel", @EVD@.of("a", "pcancel"));
  b.appendInline("#SkyyPQCol", PL_PQ);
  int n = q.size() < PLMAX ? q.size() : PLMAX;
  int rh = PLHS[@PKG@.HubBar.growSize(n, PLLH - 8, PLHS, 3)];
  for (int i = 0; i < n; i++) {
    Object[] e = (Object[]) q.get(i);
    long done = ((Long) e[4]).longValue();
    units += (long) ((Integer) e[2]).intValue();
    boolean late = fst == 2 && done + units > fms;   // past the loaded fuel (1 ms to spare per unit, as fuelState): red
    procRow(b, "SkyyPQList", "SkyyPQRow" + i, rh, @PKG@.ProcBench.knownId((String) e[0]),
            new String[] { (String) e[1], "x" + String.valueOf(e[2]), @PKG@.ProcBench.dur(((Long) e[3]).longValue()), "done in " + @PKG@.ProcBench.dur(done) },
            PQWS, new String[] { L_ROWN, L_TEXT, L_CAP, late ? L_OUT : L_HAVE });
  }
  procEnd(b, "SkyyPQList", "SkyyPQ", q.size(), n, "Nothing queued - press Queue on a recipe below");
  b.appendInline("#SkyyPLists", gap(16));
  // FUEL: the requirement line (green = covers the whole queue, equal counts; red + need), one row per loaded fuel item
  b.appendInline("#SkyyPLists", "Group #SkyyPFuCol { Anchor: (Width: " + PFW + ", Height: " + PLH + "); LayoutMode: Top; }");
  b.appendInline("#SkyyPFuCol", "Group #SkyyPFuHd { Anchor: (Height: 36); LayoutMode: Left; }");
  b.appendInline("#SkyyPFuHd", lbl("SkyyPFuHead", PFW, 32, fst == 0 ? L_HEAD : (fst == 1 ? L_OKH : L_BADH)));
  String fh;
  if (fst == 0) fh = view.cEternal ? "Eternal Flame - needs no fuel" : "Needs no fuel";
  else {
    fh = "Fuel " + @PKG@.ProcBench.dur(fms) + " : queue " + @PKG@.ProcBench.dur(qms);
    long sh = qms - fms;
    if (sh <= 0L) sh = fneed - fms;   // within the 1 ms per unit margin
    if (fst == 2) fh = fh + "  (need " + @PKG@.ProcBench.dur(sh) + ")";
  }
  b.set("#SkyyPFuHead.Text", fh);
  b.appendInline("#SkyyPFuCol", PL_PFF);
  n = f.size() < PLMAX ? f.size() : PLMAX;
  rh = PLHS[@PKG@.HubBar.growSize(n, PLLH - 8, PLHS, 3)];
  for (int i = 0; i < n; i++) {
    Object[] e = (Object[]) f.get(i);
    String fid = (String) e[0];
    int c = ((Integer) e[2]).intValue();
    procRow(b, "SkyyPFuList", "SkyyPFuRow" + i, rh, @PKG@.ProcBench.knownId(fid),
            new String[] { (String) e[1], c > 0 ? "x" + c : "", @PKG@.ProcBench.dur(((Long) e[3]).longValue()) },
            PFWS, new String[] { L_ROWN, L_TEXT, L_CAP });
  }
  procEnd(b, "SkyyPFuList", "SkyyPFu", f.size(), n, view.needsFuel ? "No fuel loaded - Load fuel or Add fuel below" : "This bench burns no fuel");
  b.appendInline("#SkyyPLists", gap(16));
  // READY TO COLLECT: one row per finished item + Collect
  b.appendInline("#SkyyPLists", "Group #SkyyPRCol { Anchor: (Width: " + PRW + ", Height: " + PLH + "); LayoutMode: Top; }");
  b.appendInline("#SkyyPRCol", "Group #SkyyPRHd { Anchor: (Height: 36); LayoutMode: Left; }");
  b.appendInline("#SkyyPRHd", lbl("SkyyPRHead", PRW - 148, 32, L_HEAD));
  b.set("#SkyyPRHead.Text", r.isEmpty() ? "Ready to collect" : ("Ready to collect - " + view.outTotal()));
  b.appendInline("#SkyyPRHd", gap(8));
  b.appendInline("#SkyyPRHd", btn("SkyyPCollect", "Collect", 140, 0, B_PRI));
  ev.addEventBinding(@BT@.Activating, "#SkyyPCollect", @EVD@.of("a", "pcollect"));
  b.appendInline("#SkyyPRCol", PL_PR);
  n = r.size() < PLMAX ? r.size() : PLMAX;
  rh = PLHS[@PKG@.HubBar.growSize(n, PLLH - 8, PLHS, 3)];
  for (int i = 0; i < n; i++) {
    Object[] e = (Object[]) r.get(i);
    String oid = (String) e[0];
    procRow(b, "SkyyPRList", "SkyyPRRow" + i, rh, @PKG@.ProcBench.knownId(oid), new String[] { @PKG@.ProcBench.itemName(oid), "x" + String.valueOf(e[1]) }, PRWS, new String[] { L_ROWN, L_HAVE });
  }
  procEnd(b, "SkyyPRList", "SkyyPR", r.size(), n, "Nothing ready yet");
}"""), cpg))
cpg.addMethod(CtNewMethod.make(jt(r"""
public void buildProc(@UCB@ b, @UEB@ ev, @PLA@ p, java.util.UUID u, String k) {''')

# ---- buildProc: the lists instead of the queue line + output row (the ADD FUEL picker keeps 0.8.22's lines)
P.rep('''  b.appendInline("#SkyyCraftBody", lbl("SkyyPQueue", 1552, 22, L_CAPC));
  b.set("#SkyyPQueue.Text", d[2]);
  b.appendInline("#SkyyCraftBody", "Group #SkyyPOutRow { Anchor: (Height: 36, Bottom: 6, Top: 4); LayoutMode: Left; }");
  b.appendInline("#SkyyPOutRow", lbl("SkyyPOut", 540, 32, L_HAVE));
  b.set("#SkyyPOut.Text", d[3]);
  b.appendInline("#SkyyPOutRow", btn("SkyyPCollect", "Collect", 140, 0, B_PRI));
  b.appendInline("#SkyyPOutRow", gap(8));
  b.appendInline("#SkyyPOutRow", btn("SkyyPCancel", "Cancel queue", 170, 0, B_SEC));
  ev.addEventBinding(@BT@.Activating, "#SkyyPCollect", @EVD@.of("a", "pcollect"));
  ev.addEventBinding(@BT@.Activating, "#SkyyPCancel", @EVD@.of("a", "pcancel"));
''', '''  boolean picker = this.fuelPick && view.needsFuel && !broken;   // 0.8.23: the ADD FUEL view keeps 0.8.22's two lines (its own sizes)
  if (picker) {
  b.appendInline("#SkyyCraftBody", lbl("SkyyPQueue", 1552, 22, L_CAPC));
  b.set("#SkyyPQueue.Text", d[2]);
  b.appendInline("#SkyyCraftBody", "Group #SkyyPOutRow { Anchor: (Height: 36, Bottom: 6, Top: 4); LayoutMode: Left; }");
  b.appendInline("#SkyyPOutRow", lbl("SkyyPOut", 540, 32, L_HAVE));
  b.set("#SkyyPOut.Text", d[3]);
  b.appendInline("#SkyyPOutRow", btn("SkyyPCollect", "Collect", 140, 0, B_PRI));
  b.appendInline("#SkyyPOutRow", gap(8));
  b.appendInline("#SkyyPOutRow", btn("SkyyPCancel", "Cancel queue", 170, 0, B_SEC));
  ev.addEventBinding(@BT@.Activating, "#SkyyPCollect", @EVD@.of("a", "pcollect"));
  ev.addEventBinding(@BT@.Activating, "#SkyyPCancel", @EVD@.of("a", "pcancel"));
  } else procLists(b, ev, view);   // 0.8.23: QUEUE | FUEL | READY TO COLLECT (Cancel queue + Collect on their headers)
''')
P.rep('''  if (view.needsFuel) {
    b.appendInline("#SkyyPOutRow", gap(8));
    b.appendInline("#SkyyPOutRow", btn("SkyyPUnload", "Unload fuel", 160, 0, B_SEC));
    ev.addEventBinding(@BT@.Activating, "#SkyyPUnload", @EVD@.of("a", "punload"));
    b.appendInline("#SkyyCraftBody", "Group #SkyyPFuelRow { Anchor: (Height: 36, Bottom: 6); LayoutMode: Left; }");''', '''  if (view.needsFuel) {
    if (picker) {
    b.appendInline("#SkyyPOutRow", gap(8));
    b.appendInline("#SkyyPOutRow", btn("SkyyPUnload", "Unload fuel", 160, 0, B_SEC));
    }
    ev.addEventBinding(@BT@.Activating, "#SkyyPUnload", @EVD@.of("a", "punload"));
    b.appendInline("#SkyyCraftBody", "Group #SkyyPFuelRow { Anchor: (Height: 36, Bottom: 6); LayoutMode: Left; }");''')
P.rep('''    b.appendInline("#SkyyPFuelRow", btn("SkyyPAddF", "Add fuel", 150, 0, this.fuelPick ? B_TERON : B_PRI));
    ev.addEventBinding(@BT@.Activating, "#SkyyPAddF", @EVD@.of("a", "paddf"));
  }
''', '''    b.appendInline("#SkyyPFuelRow", btn("SkyyPAddF", "Add fuel", 150, 0, this.fuelPick ? B_TERON : B_PRI));
    ev.addEventBinding(@BT@.Activating, "#SkyyPAddF", @EVD@.of("a", "paddf"));
    if (!picker) {   // 0.8.23: Unload fuel at the end of the Load fuel row (the fuel controls together)
      b.appendInline("#SkyyPFuelRow", gap(12));
      b.appendInline("#SkyyPFuelRow", btn("SkyyPUnload", "Unload fuel", 160, 0, B_SEC));
    }
  }
''')
P.rep('''  if (this.fuelPick && view.needsFuel && !broken) { fuelPicker(b, ev, p, k, bench, view); return; }
  this.usedH = this.usedH + 26 + 22 + 18 + 22 + 46 + (view.needsFuel ? 42 : 0);   // 0.8.14: status, progress, bar, queue, output (+ fuel) lines''',
      '''  if (picker) { fuelPicker(b, ev, p, k, bench, view); return; }
  this.usedH = this.usedH + 26 + 22 + 18 + PLADD + (view.needsFuel ? 42 : 0);   // 0.8.23: status, progress, bar, the 3 lists (+ fuel) lines''')

# the Load fuel row still fits with Unload fuel at its end: label 100 + 4 x 202 + 4 + Add fuel 150 + 12 + 160 (no fuel: 640 + 194 + ...)
assert 100 + 4 + 202 * 4 + 150 + 12 + 160 <= 1552 and 100 + 640 + 194 + 150 + 12 + 160 <= 1552

EV1 = sorted(l.strip() for l in P.s.split("\n") if "addEventBinding" in l and '"#SkyyP' in l)
_old_btn = [l for l in EV0 if any(t in l for t in ('"pcollect"', '"pcancel"', '"punload"', '"paddf"', '"pfuel:"'))]
assert all(EV1.count(l) >= 1 for l in _old_btn), "0.8.23: every old Furnace button keeps its binding"
assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.8.23 adds no system / command"
P.finish()
