"""Derive SkyySacks/build_skyysacks_0.7.3.py from 0.7.2 (edit THIS file, then regenerate: python tools/sacks_0_7_3_patch.py).
0.7.3 (Skyy 2026-09-23 22:55 craft-page call + research/Smithing-Smelting-Spec.md + research/Cooking-Skill-Spec.md):
 - Craft tabs: < Back to bags | Crafting | Smithing | Farming | Furnace | Tannery | Collections. No Alchemy tab (Alchemy and Cooking are
   table only). The merged recipe set (Fieldcraft + every equipped bench that is not timed/retired) is split by CraftPage.tabGroup():
   Farming = every Farmingbench recipe (hoes, sickles, watering can included), Smithing = primary output Tool_* / Weapon_* / Armor_*
   (all materials, wood and crude too), Crafting = everything else. Farming shows when a Farming Bench accessory is equipped.
 - Search (SkyySacks-Plan.md "Craft page tabs + search"): inline TextField + Search + Clear on the Crafting / Smithing / Farming tabs.
   Enter (Validating) or the Search button sends EventData "@SearchQuery" = "#SkyyCSearch.Value" (vanilla CommandListPage /
   ServerFileBrowser pattern); the page rebuilds with the TextField Value set to the query (ServerFileBrowser set("<id>.Value")).
   Every typed word must appear in the item name/id; results come from Crafting + Smithing + Farming together. No per-keystroke
   updates (PageManager drops clicks while an update is unacknowledged). Behind a config switch: Skyy_SkyySacks/config.properties
   craftSearch=true|false, re-read by the SackSaver (10 s) when the file changes - no restart, no rebuild. /craft <words> opens the page
   already searching (works with the box switched off; setAllowsExtraArguments + ctx.getInputString, the SkyyRolls 0.1.2 pattern).
 - Retired bench accessories (Alchemybench, Cookingbench, Campfire - orchestrator decision 4): ignored in acc:has, never unlock recipes.
   Instant tabs (Crafting / Smithing / Farming / search / Collections) drop a recipe when EVERY bench requirement is a retired bench or
   a timed Processing bench (Furnace, Tannery, Campfire) - CraftPage.tableOnly(); the merged set also skips those requirements.
   Salvagebench is a Processing bench in vanilla too, but it stays merged and INSTANT (Skyy's crafting layout lock, HANDOFF "Crafting
   layout + OMNI": "... Campfire, Salvage all merged, instant"; SkyyAccessories 0.4.2 keeps the Salvage Bench accessory active and in
   the Omni recipe) - CraftPage.instantProc(). Collections-unlocked recipes get that bench check too (SkyyCollections' unlocks are not
   bench-filtered).
   The old OpenCustomUI page id SkyySacksAlchemy now opens the Crafting tab.
 - Bench-aware bag mirror (spec 7.3): BagMirror.rebuild(caps, wanted) fills the 36 slots with the open bench's ingredients first (one
   stack of every wanted item, then wanted items up to 4 stacks, then the old largest-pile-first order). CraftLinkTask takes the wanted
   set from the open BlockWindow's bench (CraftingPlugin.getBenchRecipes(bench) inputs + tier-upgrade materials, cached per bench id);
   the /craft page does the same with the recipes it shows (view), the one recipe clicked (craft / queue) or the fuel loaded.
 - Furnace tab Smithing XP (spec 4.1 + research/Alchemy-Skill-Spec.md 7.2): ProcBench.finishUnit counts paid Furnace units per recipe
   (xpDone, persisted as Furnace.xpDone, capped at 10000 per recipe); ProcTask pays them once per run through skill:fn:craftxp
   {u, recipeId, count, "sacks:furnace", key} only when the key it advanced is SackPool.settledKey(u); a Number answer drains exactly the
   paid count; no function = ledger kept. Tannery units and cancelled/unloaded/refunded items never count. Instant crafts report
   "sacks:craft" (Alchemy spec 7.3 item 1; pays 0 today since no Alchemy/Furnace recipe is left in /craft).
 - Cooking: graded dishes (Skyy_Cook_* ids, not the Skyy_Cook_Recipe_* variant items; plus a cook:prefix bridge value starting with
   Skyy_Cook) pool into the Farming bag (SackDefs.catOf).
 - Round UI rule "never send periodic page updates": the Furnace / Tannery tab no longer refreshes itself every ~2 s (CraftPage.live()
   and its liveOn / liveSig / liveAt state are removed; PageManager drops clicks while an update is unacknowledged) - it has a Refresh
   button instead.
 - Review fixes: the dead pre-inline SACKS_UI markup (underscore ids like s_row_N / s_caps - never shipped, files = {} is what
   B.assemble gets) and its ROWS constant are deleted; the unreachable legacy F: / B: tab branches of recipesFor are gone (an unknown
   tab id already falls back to the first tab in build()); config.properties is created as a .tmp file, fsynced, then renamed.
Every 0.7.2 profile / busy / settle rule is untouched: settledKey stays the one gate of every item move, the craft page still counts
inventory only while a switch settles, the bench link still only parks the mirror while settling.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.2.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.3.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert s.count(old) >= 1, "anchor missing: " + old[:90]
    assert count != 1 or s.count(old) == 1, "anchor not unique: " + old[:90]
    s = s.replace(old, new, count)


def blk(sig, pairs, after=None):
    """Replace inside ONE method source block only: from `sig` (searched after `after`) to the next '\"\"\", '."""
    global s
    base = s.index(after) if after else 0
    i = s.index(sig, base)
    j = s.index('""", ', i)
    b = s[i:j]
    for old, new in pairs:
        assert b.count(old) == 1, "anchor missing/not unique in block %r: %r" % (sig[:60], old[:80])
        b = b.replace(old, new)
    s = s[:i] + b + s[j:]


def swap(start, end, new):
    """Replace the text from the unique `start` marker up to and including the first `end` after it."""
    global s
    assert s.count(start) == 1, "start marker missing/not unique: " + start[:90]
    i = s.index(start)
    j = s.index(end, i) + len(end)
    s = s[:i] + new + s[j:]


# ---------------- docstring + version ----------------
rep('"""SkyySacks 0.7.2 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.2.py            -> SkyySacks/SkyySacks-0.7.2.jar' + LF
    + '       python build_skyysacks_0.7.2.py --deploy   -> also',
    '"""SkyySacks 0.7.3 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.3.py            -> SkyySacks/SkyySacks-0.7.3.jar' + LF
    + '       python build_skyysacks_0.7.3.py --deploy   -> also')
rep('Derived by tools/sacks_0_7_2_patch.py. Without SkyyProfiles pkey = uuid = profile 1: same files, same behaviour.' + LF + '"""',
    'Derived by tools/sacks_0_7_2_patch.py. Without SkyyProfiles pkey = uuid = profile 1: same files, same behaviour.' + LF
    + '0.7.3 (derived from 0.7.2 by tools/sacks_0_7_3_patch.py - edit the patch, not this file): craft tabs Crafting | Smithing | Farming |' + LF
    + 'Furnace | Tannery | Collections (no Alchemy tab); search box (TextField, Enter or Search, Clear; config craftSearch in' + LF
    + 'Skyy_SkyySacks/config.properties, re-read without a restart; /craft <words>); retired Alchemy/Cooking/Campfire bench accessories' + LF
    + 'unlock nothing and timed/table-only recipes never craft instantly (also on the Collections tab; Salvage stays instant - Skyy\'s' + LF
    + 'crafting layout lock); bench-aware bag mirror (the open' + LF
    + 'bench\'s ingredients fill the 36 slots first; the craft page does the same); Furnace units pay Smithing XP through skill:fn:craftxp' + LF
    + '(ledger Furnace.xpDone, paid once the profile is settled); graded Skyy_Cook_* dishes pool into the Farming bag; the Furnace /' + LF
    + 'Tannery tab has a Refresh button instead of the ~2 s self-refresh (periodic page updates make PageManager drop clicks).' + LF + '"""')
rep('VERSION = "0.7.2"', 'VERSION = "0.7.3"')

# ---------------- constants + probes ----------------
rep('PGM = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"' + LF,
    'PGM = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"' + LF
    + '# 0.7.3' + LF
    + 'AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"' + LF
    + 'BWN = "com.hypixel.hytale.server.core.entity.entities.player.windows.BlockWindow"' + LF
    + 'BUR = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.BenchUpgradeRequirement"' + LF
    + 'BTP = "com.hypixel.hytale.protocol.BenchType"' + LF)
rep('             (MQ, "isItemExcluded"), (MQ, "getResourceTypeId")):' + LF + '    B.probe(pool, c, m)' + LF,
    '             (MQ, "isItemExcluded"), (MQ, "getResourceTypeId")):' + LF + '    B.probe(pool, c, m)' + LF
    + '# 0.7.3: bench-aware mirror, Processing check, search box (Validating + "@SearchQuery" event data), /craft <words>' + LF
    + 'for c, m in ((CRP, "getBenchRecipes"), (BWN, "getBlockType"), (BEN, "getUpgradeRequirement"), (BUR, "getInput"), (BRQ, "type"),' + LF
    + '             (BTP, "Processing"), (BT, "Validating"), (EVD, "append"), (UEB, "addEventBinding"), (AC, "setAllowsExtraArguments"),' + LF
    + '             (CTX, "getInputString"), (UCB, "set"), (MQ, "getItemId")):' + LF
    + '    B.probe(pool, c, m)' + LF)
rep('cfac = pool.makeClass(PKG + ".CraftPageFactory")' + LF,
    'cfac = pool.makeClass(PKG + ".CraftPageFactory")' + LF
    + 'scfg = pool.makeClass(PKG + ".SackCfg")' + LF)

# ---------------- SackDefs.catOf: graded dishes -> Farming ----------------
rep('  if (itemId.startsWith("Skyy_Sack_")) return null;' + LF,
    r'''  if (itemId.startsWith("Skyy_Sack_")) return null;
  // 0.7.3 (research/Cooking-Skill-Spec.md 3.4): graded dishes (the Grade is in the id, no metadata) go to the Farming bag; the
  // Skyy_Cook_Recipe_* recipe-variant items never do. A cook:prefix bridge value (SkyyCooking) is honoured when it starts with Skyy_Cook.
  if (itemId.startsWith("Skyy_")) {
    if (itemId.startsWith("Skyy_Cook_Recipe_")) return null;
    if (itemId.startsWith("Skyy_Cook_")) return "Farming";
    try {
      Object b = System.getProperties().get("skyy.bridge");
      Object p = (b instanceof java.util.Map) ? ((java.util.Map) b).get("cook:prefix") : null;
      if (p instanceof String && ((String) p).startsWith("Skyy_Cook") && itemId.startsWith((String) p)) return "Farming";
    } catch (Throwable t) { }
    return null;
  }
''')

# ---------------- SackCfg (config switch for the search box) ----------------
rep('# ================= Processing (0.7.0): timed Furnace / Tannery queues - our own per-player state, no block entity =================' + LF,
    r'''# ================= SackCfg (0.7.3): Skyy_SkyySacks/config.properties - read at setup, re-read by the SackSaver when the file changes =================
# craftSearch=false removes the inline TextField from the craft page without a rebuild (in case it does not parse on a client).
scfg.addField(CtField.make("public static java.nio.file.Path FILE;", scfg))
scfg.addField(CtField.make("public static long MTIME = -1L;", scfg))
scfg.addField(CtField.make("public static boolean WARNED = false;", scfg))
scfg.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicBoolean SEARCH = new java.util.concurrent.atomic.AtomicBoolean(true);", scfg))
scfg.addMethod(CtNewMethod.make("""
public static synchronized void reload() {
  try {
    if (FILE == null) return;
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
      String nl = System.lineSeparator();
      String txt = "# SkyySacks settings - re-read about every 10 seconds when this file changes (no restart and no rebuild needed)." + nl
        + "# craftSearch=false removes the search box from the /craft page (use it if the craft page stops opening on your client)." + nl
        + "# /craft followed by words still searches when the box is off." + nl
        + "craftSearch=true" + nl;
      // review fix: tmp + fsync + atomic rename (ProcStore.save pattern), so a crash mid-write never leaves a truncated config.properties
      java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp");
      java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
      try { out.write(txt.getBytes("UTF-8")); out.flush(); out.getFD().sync(); } finally { out.close(); }
      try { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }); }
      catch (Throwable am) { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
    }
    long mt = java.nio.file.Files.getLastModifiedTime(FILE, new java.nio.file.LinkOption[0]).toMillis();
    if (mt == MTIME) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    boolean on = !"false".equalsIgnoreCase(p.getProperty("craftSearch", "true").trim());
    boolean first = MTIME < 0L;
    MTIME = mt;
    WARNED = false;
    if (first || on != SEARCH.get()) {
      try { if (com.skyy.sacks.SackPool.LOG != null) com.skyy.sacks.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: craft page search box " + (on ? "ON" : "OFF") + " (" + FILE + ")"); } catch (Throwable t2) { }
    }
    SEARCH.set(on);
  } catch (Throwable t) {
    if (!WARNED) { WARNED = true; com.skyy.sacks.SackPool.warn("could not read " + FILE + " - keeping craftSearch=" + SEARCH.get() + ": " + t); }
  }
}""", scfg))

# ================= Processing (0.7.0): timed Furnace / Tannery queues - our own per-player state, no block entity =================
''')

# ---------------- ProcBench: Smithing XP ledger (xpDone) ----------------
rep('pben.addField(CtField.make("public java.util.LinkedHashMap out;", pben))' + LF,
    'pben.addField(CtField.make("public java.util.LinkedHashMap out;", pben))' + LF
    + '# 0.7.3 Smithing: paid Furnace units per recipe not yet reported through skill:fn:craftxp (persisted as <bench>.xpDone)' + LF
    + 'pben.addField(CtField.make("public java.util.LinkedHashMap xpDone;", pben))' + LF
    + 'pben.addField(CtField.make("public static final int XP_CAP = 10000;", pben))' + LF)
rep('  this.out = new java.util.LinkedHashMap();' + LF + '  this.needsFuel = benchNeedsFuel(bench);' + LF,
    '  this.out = new java.util.LinkedHashMap();' + LF + '  this.xpDone = new java.util.LinkedHashMap();' + LF
    + '  this.needsFuel = benchNeedsFuel(bench);' + LF)
blk('public synchronized void finishUnit({PKG}.ProcJob j) {{', [
    ('    {PKG}.SackPool.warn("processing: recipe " + j.recipe + " has no item output any more - its inputs went to the output slot");' + LF
     + '  }}' + LF,
     '    {PKG}.SackPool.warn("processing: recipe " + j.recipe + " has no item output any more - its inputs went to the output slot");' + LF
     + '  }}' + LF
     + '  // 0.7.3 Smithing (research/Smithing-Smelting-Spec.md 4.1): only a PAID Furnace unit counts - never the no-output fallback,' + LF
     + '  // burnOne (charcoal), cancel() or unloadFuel(); ProcTask.drainXp reports it once the profile is settled' + LF
     + '  else if ("Furnace".equalsIgnoreCase(this.bench)) {{' + LF
     + '    Integer cx = (Integer) this.xpDone.get(j.recipe);' + LF
     + '    if (cx == null || cx.intValue() < XP_CAP) addTo(this.xpDone, j.recipe, 1);' + LF
     + '  }}' + LF),
])
rep('pben.addMethod(CtNewMethod.make(f"""' + LF + 'public synchronized long queueMs() {{' + LF,
    r'''pben.addMethod(CtNewMethod.make("""
public synchronized java.util.ArrayList xpList() {
  java.util.ArrayList l = new java.util.ArrayList();
  java.util.Iterator it = this.xpDone.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    l.add(new Object[] { e.getKey(), e.getValue() });
  }
  return l;
}""", pben))
pben.addMethod(CtNewMethod.make("""
public synchronized void takeXp(String id, int n) {
  if (id == null || n <= 0) return;
  Integer cur = (Integer) this.xpDone.get(id);
  if (cur == null) return;
  int v = cur.intValue() - n;
  if (v <= 0) this.xpDone.remove(id); else this.xpDone.put(id, Integer.valueOf(v));
}""", pben))
''' + 'pben.addMethod(CtNewMethod.make(f"""' + LF + 'public synchronized long queueMs() {{' + LF)
blk('public synchronized void toProps(java.util.Properties p) {{', [
    ('  p.setProperty(b + "out", ser(this.out));' + LF,
     '  p.setProperty(b + "out", ser(this.out));' + LF + '  p.setProperty(b + "xpDone", ser(this.xpDone));' + LF),
])
blk('public synchronized void fromProps(java.util.Properties p) {{', [
    ('  this.out.clear(); parseInto(this.out, p.getProperty(b + "out"), 1);' + LF,
     '  this.out.clear(); parseInto(this.out, p.getProperty(b + "out"), 1);' + LF
     + '  this.xpDone.clear(); parseInto(this.xpDone, p.getProperty(b + "xpDone"), 1);' + LF
     + '  java.util.Iterator xi = new java.util.ArrayList(this.xpDone.keySet()).iterator();' + LF
     + '  while (xi.hasNext()) {{ Object xk = xi.next(); if (((Integer) this.xpDone.get(xk)).intValue() > XP_CAP) this.xpDone.put(xk, Integer.valueOf(XP_CAP)); }}' + LF),
])

# ---------------- SackSaver: config re-read ----------------
rep('  try {{ {PKG}.CraftLog.drain(); }} catch (Throwable t) {{ }}' + LF + '}}""", sav))' + LF,
    '  try {{ {PKG}.CraftLog.drain(); }} catch (Throwable t) {{ }}' + LF
    + '  try {{ {PKG}.SackCfg.reload(); }} catch (Throwable t) {{ }}' + LF + '}}""", sav))' + LF)

# ---------------- CraftPage: search query field ----------------
rep('cpg.addField(CtField.make("public boolean settling;", cpg))' + LF,
    'cpg.addField(CtField.make("public boolean settling;", cpg))' + LF
    + '# 0.7.3: the active search ("" = none); lives only on this page instance' + LF
    + 'cpg.addField(CtField.make("public String query;", cpg))' + LF)
# 0.7.3 review fix: live() is deleted below, so its state goes too
rep('cpg.addField(CtField.make("public boolean liveOn;", cpg))' + LF
    + 'cpg.addField(CtField.make("public String liveSig;", cpg))' + LF
    + 'cpg.addField(CtField.make("public long liveAt;", cpg))' + LF, '')
rep('  this.tab = tab; this.pageNo = 0; this.info = "";' + LF + '}}""", cpg))' + LF,
    '  this.tab = tab; this.pageNo = 0; this.info = ""; this.query = "";' + LF + '}}""", cpg))' + LF)

# ---------------- BagMirror: bench-aware rebuild ----------------
rep('mir.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LASTKEY = new java.util.concurrent.ConcurrentHashMap();", mir))' + LF,
    'mir.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LASTKEY = new java.util.concurrent.ConcurrentHashMap();", mir))' + LF
    + '# 0.7.3: bench id -> Set of wanted ingredient ids / resource type ids; item id -> String[] of its resource type ids' + LF
    + 'mir.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap WANTED = new java.util.concurrent.ConcurrentHashMap();", mir))' + LF
    + 'mir.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap RTS = new java.util.concurrent.ConcurrentHashMap();", mir))' + LF)
swap('# rebuild the mirror from the pool: only categories the player carries a bag for; up to 4 stacks per item, 36 slots' + LF,
     '}}""", mir))' + LF,
     r'''# 0.7.3 bench-aware mirror (research/Smithing-Smelting-Spec.md 7.3): the ingredient item ids and resource type ids a bench can use -
# every input of CraftingPlugin.getBenchRecipes(bench) plus the bench's tier-upgrade materials - cached per bench id (non-empty only).
mir.addMethod(CtNewMethod.make(f"""
public static void addInputs(java.util.Set s, {MQ}[] in) {{
  for (int i = 0; in != null && i < in.length; i++) {{
    if (in[i] == null) continue;
    if (in[i].getItemId() != null) s.add(in[i].getItemId());
    else if (in[i].getResourceTypeId() != null) s.add(in[i].getResourceTypeId());
  }}
}}""", mir))
mir.addMethod(CtNewMethod.make(f"""
public static java.util.Set wantedFor(Object w) {{
  try {{
    if (!(w instanceof {BWN})) return null;
    {BLT} bt = (({BWN}) w).getBlockType();
    if (bt == null) return null;
    {BEN} b = bt.getBench();
    if (b == null || b.getId() == null) return null;
    String key = b.getId().toLowerCase();
    Object c = WANTED.get(key);
    if (c != null) return (java.util.Set) c;
    java.util.HashSet s = new java.util.HashSet();
    java.util.List l = {CRP}.getBenchRecipes(b);
    for (int i = 0; l != null && i < l.size(); i++) {{
      Object o = l.get(i);
      if (o instanceof {CRR}) addInputs(s, (({CRR}) o).getInput());
    }}
    for (int t = 1; t <= 10; t++) {{
      {BUR} ur = null;
      try {{ ur = b.getUpgradeRequirement(t); }} catch (Throwable e) {{ ur = null; }}
      if (ur != null) addInputs(s, ur.getInput());
    }}
    if (!s.isEmpty()) WANTED.put(key, s);
    return s;
  }} catch (Throwable t) {{ return null; }}
}}""", mir))
mir.addMethod(CtNewMethod.make(f"""
public static String[] rtsOf(String id) {{
  Object c = RTS.get(id);
  if (c != null) return (String[]) c;
  String[] out = new String[0];
  try {{
    {ITM} it = {PKG}.ProcBench.item(id);
    if (it == null) return out;
    {IRT}[] r = it.getResourceTypes();
    java.util.ArrayList l = new java.util.ArrayList();
    for (int i = 0; r != null && i < r.length; i++) if (r[i] != null && r[i].id != null) l.add(r[i].id);
    out = (String[]) l.toArray(new String[0]);
    RTS.put(id, out);
  }} catch (Throwable t) {{ }}
  return out;
}}""", mir))
mir.addMethod(CtNewMethod.make("""
public static boolean wants(java.util.Set s, String id) {
  if (s == null || id == null) return false;
  if (s.contains(id)) return true;
  String[] r = rtsOf(id);
  for (int i = 0; i < r.length; i++) if (s.contains(r[i])) return true;
  return false;
}""", mir))
# rebuild the mirror from the pool: only categories the player carries a bag for; up to 4 stacks per item, 36 slots.
# 0.7.3: `wanted` (item ids / resource type ids the open bench or the craft page can use; null = none) goes first - one stack of every
# wanted item, then wanted items up to 4 stacks, then everything else by count (the old order) - so big piles of stone or logs can no
# longer crowd a bench's ingredients out of the 36 slots. sync() before every rebuild keeps the pool accounting exact.
mir.addMethod(CtNewMethod.make(f"""
public String rebuild(java.util.HashMap caps, java.util.Set wanted) {{
  try {{ this.cont.clear(); }} catch (Throwable t) {{ }}
  for (int i = 0; i < 36; i++) {{ this.slotIds[i] = null; this.slotQty[i] = 0; }}
  StringBuilder sb = new StringBuilder();
  java.util.ArrayList entries = new java.util.ArrayList({PKG}.SackPool.pool(this.key).entrySet());
  java.util.Collections.sort(entries, new {PKG}.CountCmp());
  int n = entries.size();
  String[] ids = new String[n];
  long[] left = new long[n];
  int[] max = new int[n];
  int[] stacks = new int[n];
  boolean[] want = new boolean[n];
  for (int e = 0; e < n; e++) {{
    java.util.Map.Entry en = (java.util.Map.Entry) entries.get(e);
    String id = (String) en.getKey();
    long cnt = ((Long) en.getValue()).longValue();
    String cat = {PKG}.SackDefs.catOf(id);
    if (cat == null || !caps.containsKey(cat) || cnt <= 0L) continue;
    ids[e] = id;
    left[e] = cnt;
    int mx = 64;
    try {{ {IS} probe = new {IS}(id, 1); if (probe.getItem() != null && probe.getItem().getMaxStack() > 0) mx = probe.getItem().getMaxStack(); }} catch (Throwable t) {{ }}
    max[e] = mx;
    want[e] = wanted != null && wants(wanted, id);
  }}
  int slot = 0;
  for (int pass = 0; pass < 3 && slot < 36; pass++) {{
    int lim = pass == 0 ? 1 : 4;
    for (int e = 0; e < n && slot < 36; e++) {{
      if (ids[e] == null) continue;
      if (pass < 2 && !want[e]) continue;
      if (pass == 2 && want[e]) continue;
      while (left[e] > 0L && stacks[e] < lim && slot < 36) {{
        int q = left[e] < (long) max[e] ? (int) left[e] : max[e];
        this.cont.setItemStackForSlot((short) slot, new {IS}(ids[e], q));
        this.slotIds[slot] = ids[e]; this.slotQty[slot] = q;
        sb.append(ids[e]).append('=').append(q).append(';');
        left[e] = left[e] - (long) q;
        slot++;
        stacks[e] = stacks[e] + 1;
      }}
    }}
  }}
  return sb.toString();
}}""", mir))
mir.addMethod(CtNewMethod.make("""
public String rebuild(java.util.HashMap caps) {
  return rebuild(caps, (java.util.Set) null);
}""", mir))
''')

# ---------------- CraftLinkTask: feed the open bench's ingredients first ----------------
rep('      String sig = m.rebuild(caps);' + LF,
    '      String sig = m.rebuild(caps, {PKG}.BagMirror.wantedFor(w));' + LF)

# ---------------- CraftPage helpers: retired benches, search ----------------
rep('cpg.addMethod(CtNewMethod.make(f"""' + LF + 'public static synchronized boolean knownBench(String bench) {{' + LF,
    r'''# 0.7.3: bench accessories retired with the table-only Alchemy / Cooking call (orchestrator decision 4: the Campfire too - its 3 recipes
# are cooked food). Their acc:has entries unlock nothing and their recipes never craft instantly.
cpg.addMethod(CtNewMethod.make("""
public static boolean retiredBench(String id) {
  return id != null && (id.equalsIgnoreCase("Alchemybench") || id.equalsIgnoreCase("Cookingbench") || id.equalsIgnoreCase("Campfire"));
}""", cpg))
# 0.7.3 search: lower-case words of letters and digits (max 40 chars); every word must appear in the item name or id
cpg.addMethod(CtNewMethod.make("""
public static String cleanQuery(String q) {
  if (q == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < q.length() && sb.length() < 40; i++) {
    char c = q.charAt(i);
    if (Character.isLetterOrDigit(c)) sb.append(Character.toLowerCase(c));
    else if (sb.length() > 0 && sb.charAt(sb.length() - 1) != ' ') sb.append(' ');
  }
  return sb.toString().trim();
}""", cpg))
cpg.addMethod(CtNewMethod.make("""
public static boolean nameMatches(String q, String outId) {
  if (q == null || q.length() == 0) return true;
  if (outId == null) return false;
  String name = pretty(outId).toLowerCase() + " " + outId.toLowerCase().replace('_', ' ');
  String[] w = q.split(" ");
  for (int i = 0; i < w.length; i++) {
    String x = w[i].trim();
    if (x.length() > 0 && name.indexOf(x) < 0) return false;
  }
  return true;
}""", cpg))
# 0.7.3: one string value out of the page event JSON (the TextField value arrives as "@SearchQuery": "..."); handles escaped quotes,
# backslashes and unicode escapes (quote = char 34, backslash = char 92, so no escape sequences are needed here)
cpg.addMethod(CtNewMethod.make("""
public static String jsonStr(String data, String key) {
  if (data == null || key == null) return "";
  String qt = String.valueOf((char) 34);
  int i = data.indexOf(qt + key + qt);
  if (i < 0) return "";
  i = data.indexOf(':', i + key.length() + 2);
  if (i < 0) return "";
  i++;
  while (i < data.length() && Character.isWhitespace(data.charAt(i))) i++;
  if (i >= data.length() || data.charAt(i) != 34) return "";
  i++;
  StringBuilder sb = new StringBuilder();
  while (i < data.length() && sb.length() < 200) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) {
      char n = data.charAt(i + 1);
      if (n == 'u' && i + 5 < data.length()) {
        try { sb.append((char) Integer.parseInt(data.substring(i + 2, i + 6), 16)); } catch (Throwable t) { }
        i += 6;
        continue;
      }
      if (n == 'n' || n == 'r' || n == 't' || n == 'b' || n == 'f') sb.append(' '); else sb.append(n);
      i += 2;
      continue;
    }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""", cpg))
''' + 'cpg.addMethod(CtNewMethod.make(f"""' + LF + 'public static synchronized boolean knownBench(String bench) {{' + LF)
rep('    if (bench.length() == 0) continue;' + LF + '    if (!knownBench(bench)',
    '    if (bench.length() == 0) continue;' + LF
    + '    if (retiredBench(bench)) continue;  // 0.7.3: retired accessories (Alchemy, Cooking, Campfire) unlock nothing' + LF
    + '    if (!knownBench(bench)')

# ---------------- CraftPage: tabs, recipe sets, materials (separateBench .. viewMats rewritten) ----------------
swap('# benches with their own tab (not merged into Crafting)' + LF,
     'public {CIC} viewMats({PLA} p, String k) {{' + LF
     + '  if (this.settling) return new {CIC}(new {IC}[] {{ p.getInventory().getCombinedBackpackStorageHotbar() }});' + LF
     + '  return materials(p, k);' + LF + '}}""", cpg))' + LF,
     r'''# benches with their own TIMED tab (0.7.3: Furnace and Tannery only - Alchemy is table only now)
cpg.addMethod(CtNewMethod.make("""
public static boolean separateBench(String id) {
  return id != null && (id.equalsIgnoreCase("Furnace") || id.equalsIgnoreCase("Tannery"));
}""", cpg))
# 0.7.3 review fix: the one Processing (timed in vanilla) bench that crafts INSTANTLY in the merged tabs. Skyy's crafting layout lock
# (HANDOFF "Crafting layout + OMNI"): Crafting = Fieldcraft + every equipped bench accessory except Alchemy, Furnace, Tannery -
# "... Campfire, Salvage all merged, instant". The Campfire is retired since (orchestrator decision 4); Salvage is not.
cpg.addMethod(CtNewMethod.make("""
public static boolean instantProc(String id) {
  return id != null && id.equalsIgnoreCase("Salvagebench");
}""", cpg))
# 0.7.3 (research/Smithing-Smelting-Spec.md 6.3): true when EVERY bench requirement of the recipe is a retired table-only bench or a timed
# Processing bench other than Salvagebench (Furnace, Tannery, Campfire) - such a recipe is never crafted instantly (instant tabs, search,
# Collections).
cpg.addMethod(CtNewMethod.make(f"""
public static boolean tableOnly({CRR} r) {{
  {BRQ}[] br = r.getBenchRequirement();
  if (br == null) return false;
  boolean any = false;
  for (int i = 0; i < br.length; i++) {{
    if (br[i] == null) continue;
    any = true;
    if (!retiredBench(br[i].id) && (br[i].type != {BTP}.Processing || instantProc(br[i].id))) return false;
  }}
  return any;
}}""", cpg))
# only == null -> every equipped bench except the timed ones (Furnace, Tannery and any Processing requirement but Salvagebench) and the
# retired ones (the merged Crafting / Smithing / Farming set); else just that bench. Up to the accessory tier.
cpg.addMethod(CtNewMethod.make(f"""
public static java.util.TreeSet benchRecipes(java.util.UUID u, String only) {{
  java.util.TreeSet ids = new java.util.TreeSet();
  java.util.HashMap acc = accessories(({PLA}) null, u);
  if (acc.isEmpty()) return ids;
  java.util.Iterator it = {CRR}.getAssetMap().getAssetMap().values().iterator();
  while (it.hasNext()) {{
    {CRR} r = ({CRR}) it.next();
    {BRQ}[] br = r.getBenchRequirement();
    if (br == null) continue;
    for (int i = 0; i < br.length; i++) {{
      if (br[i] == null || br[i].id == null) continue;
      if (retiredBench(br[i].id)) continue;
      if (only == null) {{ if (separateBench(br[i].id) || (br[i].type == {BTP}.Processing && !instantProc(br[i].id))) continue; }}
      else if (!only.equalsIgnoreCase(br[i].id)) continue;
      int tier = accTier(acc, br[i].id);
      if (tier <= 0) continue;
      int need = br[i].requiredTierLevel; if (need <= 0) need = 1;
      if (need <= tier) {{ ids.add(r.getId()); break; }}
    }}
  }}
  return ids;
}}""", cpg))
# 0.7.3: tab ids are A:craft / A:smith / A:farm / P:<bench> / C: only (review fix: the legacy F: / B: ids are gone - buildTabs never emits
# them and build() replaces an unknown tab id with the first tab).
# 0.7.3: every recipe id the merged tabs can show (Fieldcraft + equipped non-timed benches); tabGroup() splits it into the three tabs
cpg.addMethod(CtNewMethod.make(f"""
public static java.util.TreeSet craftSet(java.util.UUID u) {{
  java.util.TreeSet ids = new java.util.TreeSet();
  java.util.Iterator fi = {FCC}.getAssetMap().getAssetMap().values().iterator();
  while (fi.hasNext()) {{
    {FCC} fc = ({FCC}) fi.next();
    java.util.Set fs = {CRP}.getAvailableRecipesForCategory("Fieldcraft", fc.getId());
    if (fs != null) ids.addAll(fs);
  }}
  ids.addAll(benchRecipes(u, (String) null));
  return ids;
}}""", cpg))
# 0.7.3 (Skyy's craft-page call): 2 = Farming (every Farmingbench recipe, farm tools included), 1 = Smithing (primary output Tool_*,
# Weapon_* or Armor_* - every material, wood and crude included), 0 = Crafting (everything else)
cpg.addMethod(CtNewMethod.make(f"""
public static int tabGroup({CRR} r) {{
  {BRQ}[] br = r.getBenchRequirement();
  for (int i = 0; br != null && i < br.length; i++) if (br[i] != null && "Farmingbench".equalsIgnoreCase(br[i].id)) return 2;
  {MQ} po = r.getPrimaryOutput();
  String id = po == null ? null : po.getItemId();
  if (id != null && (id.startsWith("Tool_") || id.startsWith("Weapon_") || id.startsWith("Armor_"))) return 1;
  return 0;
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public java.util.ArrayList buildTabs({PLA} p, java.util.UUID u, String k) {{
  java.util.ArrayList t = new java.util.ArrayList();
  java.util.HashMap acc = accessories(p, u);
  t.add(new String[] {{ "A:craft", "Crafting" }});
  t.add(new String[] {{ "A:smith", "Smithing" }});
  if (accTier(acc, "Farmingbench") > 0) t.add(new String[] {{ "A:farm", "Farming" }});
  for (int i = 0; i < {PKG}.ProcStore.BENCHES.length; i++) {{
    String bn = {PKG}.ProcStore.BENCHES[i];
    if (accTier(acc, bn) > 0 || {PKG}.ProcStore.pending(k, bn)) t.add(new String[] {{ "P:" + bn, bn }});
  }}
  if (!collectionRecipes(u).isEmpty()) t.add(new String[] {{ "C:", "Collections" }});
  return t;
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public java.util.ArrayList recipesFor(String tabId, java.util.UUID u) {{
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.TreeSet ids = new java.util.TreeSet();
  int grp = -1;
  if (tabId.equals("A:craft")) grp = 0;
  else if (tabId.equals("A:smith")) grp = 1;
  else if (tabId.equals("A:farm")) grp = 2;
  if (grp >= 0) {{
    ids.addAll(craftSet(u));
  }} else if (tabId.startsWith("P:")) {{
    ids.addAll(benchRecipes(u, tabId.substring(2)));
  }} else if (tabId.startsWith("C:")) {{
    ids.addAll(collectionRecipes(u));
  }}
  boolean timed = tabId.startsWith("P:");
  java.util.Iterator ii = ids.iterator();
  while (ii.hasNext()) {{
    Object o = {CRR}.getAssetMap().getAsset(ii.next());
    if (!(o instanceof {CRR})) continue;
    {CRR} rc = ({CRR}) o;
    if (!timed && tableOnly(rc)) continue;
    if (grp >= 0 && tabGroup(rc) != grp) continue;
    out.add(rc);
  }}
  return out;
}}""", cpg))
# 0.7.3 search: Crafting + Smithing + Farming together (the whole merged set), every typed word in the output item's name or id
cpg.addMethod(CtNewMethod.make(f"""
public java.util.ArrayList searchRecipes(java.util.UUID u, String q) {{
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.Iterator ii = craftSet(u).iterator();
  while (ii.hasNext()) {{
    Object o = {CRR}.getAssetMap().getAsset(ii.next());
    if (!(o instanceof {CRR})) continue;
    {CRR} rc = ({CRR}) o;
    if (tableOnly(rc)) continue;
    {MQ} po = rc.getPrimaryOutput();
    if (nameMatches(q, po == null ? String.valueOf(rc.getId()) : po.getItemId())) out.add(rc);
  }}
  return out;
}}""", cpg))
# 0.7.3 bench-aware mirror for the craft page: what the shown recipes (view), the clicked recipe (craft / queue) or the loaded fuel can use
cpg.addMethod(CtNewMethod.make(f"""
public static java.util.HashSet wantedOf(java.util.List recipes) {{
  java.util.HashSet s = new java.util.HashSet();
  for (int i = 0; recipes != null && i < recipes.size(); i++) {{
    Object o = recipes.get(i);
    if (o instanceof {CRR}) {PKG}.BagMirror.addInputs(s, (({CRR}) o).getInput());
  }}
  return s;
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static java.util.HashSet wantedOne({CRR} r) {{
  java.util.HashSet s = new java.util.HashSet();
  if (r != null) {PKG}.BagMirror.addInputs(s, r.getInput());
  return s;
}}""", cpg))
cpg.addMethod(CtNewMethod.make("""
public static java.util.HashSet procWanted(java.util.List recipes) {
  java.util.HashSet s = wantedOf(recipes);
  s.add("Fuel");
  return s;
}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static {CIC} materialsFor({PLA} p, String k, java.util.Set wanted) {{
  {PKG}.BagMirror m = {PKG}.BagMirror.of(k);
  m.sync();
  m.rebuild({PKG}.SweepTask.caps(p.getInventory()), wanted);
  return new {CIC}(new {IC}[] {{ p.getInventory().getCombinedBackpackStorageHotbar(), m.cont }});
}}""", cpg))
cpg.addMethod(CtNewMethod.make(f"""
public static {CIC} materials({PLA} p, String k) {{
  return materialsFor(p, k, (java.util.Set) null);
}}""", cpg))
# 0.7.2 review fix: counts for the page VIEW. While a profile switch settles (this.settling, set by build() from
# SackPool.settledKey) only the inventory is counted and no BagMirror is built or synced for the not-yet-settled key; every
# click that moves items calls materialsFor(p, k, ...) itself with the one settled key it checked.
cpg.addMethod(CtNewMethod.make(f"""
public {CIC} viewMats({PLA} p, String k, java.util.Set wanted) {{
  if (this.settling) return new {CIC}(new {IC}[] {{ p.getInventory().getCombinedBackpackStorageHotbar() }});
  return materialsFor(p, k, wanted);
}}""", cpg))
''')

# ---------------- processing clicks: bench-aware materials ----------------
blk('public static String procQueue(', [
    ('  {CIC} mats = materials(p, k);' + LF, '  {CIC} mats = materialsFor(p, k, wantedOne(r));' + LF),
])
blk('public static String procFuel(', [
    ('  {CIC} mats = materials(p, k);' + LF, '  {CIC} mats = materialsFor(p, k, java.util.Collections.singleton(id));' + LF),
])
blk('public void buildProc(', [
    ('  {CIC} mats = viewMats(p, k);' + LF,
     '  java.util.ArrayList raw = (tier > 0 && !broken) ? recipesFor(this.tab, u) : new java.util.ArrayList();' + LF
     + '  {CIC} mats = viewMats(p, k, procWanted(raw));' + LF),
    ('  java.util.ArrayList raw = (tier > 0 && !broken) ? recipesFor(this.tab, u) : new java.util.ArrayList();' + LF
     + '  boolean only = ',
     '  boolean only = '),
])

# ---------------- Furnace / Tannery tab: no periodic page updates (round UI rule) - a Refresh button instead ----------------
# PageManager drops every page click while an update is unacknowledged, so the ~2 s live() set() refresh from ProcTask could swallow a
# Collect / Queue click. ProcTask no longer calls live() (profileNotice - one update per profile change - stays); the tab gets Refresh.
blk('public void buildProc(', [
    ('  this.liveSig = d[0] + "|" + d[1] + "|" + d[2] + "|" + d[3] + "|" + d[4];' + LF
     + '  this.liveAt = System.currentTimeMillis();' + LF + '  this.liveOn = !broken;' + LF, ''),
    ('  ev.addEventBinding({BT}.Activating, "#SkyyCOnly", {EVD}.of("a", "onlyc"));' + LF,
     '  ev.addEventBinding({BT}.Activating, "#SkyyCOnly", {EVD}.of("a", "onlyc"));' + LF
     + '  b.appendInline("#SkyyCNav", "Label {{ Anchor: (Width: 8, Height: 34); Text: \\\\"\\\\"; }}");' + LF
     + '  b.appendInline("#SkyyCNav", "TextButton #SkyyPRefresh {{ Anchor: (Width: 110, Height: 34); Text: \\\\"Refresh\\\\"; " + bs + " }}");' + LF
     + '  ev.addEventBinding({BT}.Activating, "#SkyyPRefresh", {EVD}.of("a", "prefresh"));' + LF),
])
# review fix: delete live() itself (it was left in the class, unreachable) so no later patch can wire a periodic update back in
swap('# live refresh from ProcTask (world thread): set() only - Text + Visible on elements the last build created, never re-appends' + LF,
     '  sendUpdate(c, false);' + LF + '}}""", cpg))' + LF,
     '# 0.7.3: CraftPage.live() (the ~2 s Furnace / Tannery self-refresh from ProcTask) and its liveOn / liveSig / liveAt state are gone -' + LF
     + '# periodic page updates make PageManager drop clicks; the tab has a Refresh button (handleProc "prefresh").' + LF)
rep('# 0.7.2: the active profile changed while the craft page is open (ProcTask, world thread): set() only, live() stops for the' + LF
    + '# old key (it checks this.key); the next click rebuilds the page for the new profile.' + LF,
    '# 0.7.2: the active profile changed while the craft page is open (ProcTask, world thread): one set() per profile change, never' + LF
    + '# periodic; the next click rebuilds the page for the new profile.' + LF)
blk('public boolean handleProc(', [
    ('  if (data.indexOf("\\\\"pcollect\\\\"") >= 0)',
     '  if (data.indexOf("\\\\"prefresh\\\\"") >= 0) {{ this.info = ""; rebuild(); return true; }}' + LF
     + '  if (data.indexOf("\\\\"pcollect\\\\"") >= 0)'),
])
rep('      if (cp.key != null && !cp.key.equals(k)) cp.profileNotice(k); else cp.live(r, st);' + LF,
    '      if (cp.key != null && !cp.key.equals(k)) cp.profileNotice(k);' + LF)

# ---------------- CraftPage.build: search row, search results ----------------
SEARCH_ROW = r'''  // 0.7.3 search row (Crafting / Smithing / Farming tabs): inline TextField (vanilla PluginListPage / Common.ui @TextField keys only),
  // Enter (Validating) or Search sends "@SearchQuery" = the field's Value; the rebuild puts the query back with set("#SkyyCSearch.Value").
  // craftSearch=false in config.properties leaves the TextField out (a /craft <words> search still shows its Clear button).
  boolean srow = false;
  if (this.tab != null && this.tab.startsWith("A:") && ({PKG}.SackCfg.SEARCH.get() || searching)) {{
    srow = true;
    b.appendInline("#SkyyCraft", "Group #SkyyCSearchRow {{ Anchor: (Height: 42); LayoutMode: Left; Padding: (Top: 4); }}");
    if ({PKG}.SackCfg.SEARCH.get()) {{
      b.appendInline("#SkyyCSearchRow", "Group #SkyyCSearchBox {{ Anchor: (Width: 420, Height: 34); Background: #16263a; }}");
      b.appendInline("#SkyyCSearchBox", "TextField #SkyyCSearch {{ Anchor: (Full: 0); Padding: (Horizontal: 10); MaxLength: 40; PlaceholderText: \\"Search items - type a name and press Enter\\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 14); Style: (TextColor: #ffffff, FontSize: 14); }}");
      if (searching) b.set("#SkyyCSearch.Value", this.query);
      b.appendInline("#SkyyCSearchRow", "Label {{ Anchor: (Width: 8, Height: 34); Text: \\"\\"; }}");
      b.appendInline("#SkyyCSearchRow", "TextButton #SkyyCSearchGo {{ Anchor: (Width: 100, Height: 34); Text: \\"Search\\"; " + bs + " }}");
      b.appendInline("#SkyyCSearchRow", "Label {{ Anchor: (Width: 6, Height: 34); Text: \\"\\"; }}");
      ev.addEventBinding({BT}.Validating, "#SkyyCSearch", {EVD}.of("a", "csearch").append("@SearchQuery", "#SkyyCSearch.Value"), false);
      ev.addEventBinding({BT}.Activating, "#SkyyCSearchGo", {EVD}.of("a", "csearch").append("@SearchQuery", "#SkyyCSearch.Value"));
    }}
    b.appendInline("#SkyyCSearchRow", "TextButton #SkyyCSearchClear {{ Anchor: (Width: 90, Height: 34); Text: \\"Clear\\"; " + bs + " }}");
    ev.addEventBinding({BT}.Activating, "#SkyyCSearchClear", {EVD}.of("a", "cclear"));
    b.appendInline("#SkyyCSearchRow", "Label #SkyyCSearchInfo {{ Anchor: (Width: 330, Height: 34); Text: \\"\\"; Style: (FontSize: 13, TextColor: #9fb8d0, VerticalAlignment: Center); }}");
  }}
'''
blk('public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{', [
    ('  this.liveOn = false;' + LF, ''),
    ('  if (!known && this.tabs.size() > 0) {{ this.tab = ((String[]) this.tabs.get(0))[0]; this.pageNo = 0; }}' + LF,
     '  if (!known && this.tabs.size() > 0) {{ this.tab = ((String[]) this.tabs.get(0))[0]; this.pageNo = 0; }}' + LF
     + '  // 0.7.3: a search shows Crafting + Smithing + Farming results together, so no tab is highlighted while it is active' + LF
     + '  boolean searching = this.query != null && this.query.length() > 0 && this.tab != null && this.tab.startsWith("A:");' + LF),
    ('    boolean sel = t[0].equals(this.tab);' + LF, '    boolean sel = t[0].equals(this.tab) && !searching;' + LF),
    ('    inRow++;' + LF + '  }}' + LF, '    inRow++;' + LF + '  }}' + LF + SEARCH_ROW),
    ('  java.util.ArrayList raw = this.tab == null ? new java.util.ArrayList() : recipesFor(this.tab, u);' + LF
     + '  {CIC} mats = viewMats(p, k);' + LF,
     '  java.util.ArrayList raw = this.tab == null ? new java.util.ArrayList() : (searching ? searchRecipes(u, this.query) : recipesFor(this.tab, u));' + LF
     + '  {CIC} mats = viewMats(p, k, wantedOf(raw));' + LF),
    ('Text: \\\\"No recipes here yet.\\\\"; Style:',
     'Text: \\\\"" + {PKG}.SacksPage.safe(searching ? ("Nothing matches " + this.query + " in Crafting, Smithing or Farming.") : "No recipes here yet.") + "\\\\"; Style:'),
    ('  b.appendInline("#SkyyCraft", "Label #SkyyCInfo {{',
     '  if (srow) b.set("#SkyyCSearchInfo.Text", searching ? ("  " + this.rows.size() + " found in Crafting, Smithing and Farming") : "  searches Crafting, Smithing and Farming");' + LF
     + '  b.appendInline("#SkyyCraft", "Label #SkyyCInfo {{'),
], after='public boolean handleProc(')

# ---------------- CraftPage.handleDataEvent: search / clear, tab click clears it, bench-aware craft, craftxp report ----------------
blk('public void handleDataEvent({REF} ref, {ST} st, String data) {{', [
    ('    java.util.UUID u = this.playerRef.getUuid();' + LF,
     '    java.util.UUID u = this.playerRef.getUuid();' + LF
     + '    // 0.7.3 search: only the search bindings carry "@SearchQuery" (the typed text), so it is handled before any payload match -' + LF
     + '    // typed words can never be read as another button\'s payload' + LF
     + '    if (data.indexOf("\\\\"@SearchQuery\\\\"") >= 0) {{' + LF
     + '      this.query = cleanQuery(jsonStr(data, "@SearchQuery"));' + LF
     + '      this.pageNo = 0;' + LF
     + '      this.info = this.query.length() == 0 ? "type a word (for example iron or sword) and press Enter or Search" : "";' + LF
     + '      rebuild();' + LF
     + '      return;' + LF
     + '    }}' + LF
     + '    if (data.indexOf("\\\\"cclear\\\\"") >= 0) {{ this.query = ""; this.pageNo = 0; this.info = ""; rebuild(); return; }}' + LF),
    ('this.tab = ((String[]) this.tabs.get(i))[0]; this.pageNo = 0; this.info = ""; rebuild(); return;',
     'this.tab = ((String[]) this.tabs.get(i))[0]; this.pageNo = 0; this.info = ""; this.query = ""; rebuild(); return;'),
    ('    {CIC} mats = materials(p, k);' + LF, '    {CIC} mats = materialsFor(p, k, wantedOne(r));' + LF),
    ('    {PKG}.CraftLog.write(k, String.valueOf(r.getId()), qty, done, flag, given, audit.toString());' + LF,
     '    {PKG}.CraftLog.write(k, String.valueOf(r.getId()), qty, done, flag, given, audit.toString());' + LF
     + '    // 0.7.3 (research/Alchemy-Skill-Spec.md 7.3 item 1): report crafts SkyySacks completed itself; SkyySkills decides the skill and' + LF
     + '    // pays 0 for anything that is not an Alchemy / Furnace recipe (neither is left in /craft). No-op without SkyySkills 0.4.' + LF
     + '    if (done > 0) {{' + LF
     + '      try {{' + LF
     + '        Object xf = {PKG}.SackPool.bridge().get("skill:fn:craftxp");' + LF
     + '        if (xf instanceof java.util.function.Function) ((java.util.function.Function) xf).apply(new Object[] {{ u, String.valueOf(r.getId()), Integer.valueOf(done), "sacks:craft", k }});' + LF
     + '      }} catch (Throwable t) {{ }}' + LF
     + '    }}' + LF),
], after='public boolean handleProc(')

# ---------------- /craft <words> ----------------
swap('ccmd.addConstructor(CtNewConstructor.make("""' + LF + 'public CraftCmd() {' + LF,
     '}}""", ccmd))' + LF,
     r'''ccmd.addConstructor(CtNewConstructor.make("""
public CraftCmd() {
  super("craft", "Open inventory crafting (materials from your inventory and your magic bags) - /craft <words> opens it searching");
  addAliases(new String[] { "recipes" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  setAllowsExtraArguments(true);
}""", ccmd))
# 0.7.3: words after /craft (or /recipes) open the page already searching (SkyyRolls 0.1.2 pattern: extra arguments allowed, the words read
# from ctx.getInputString(); a leading command word is dropped). Works when craftSearch=false hides the search box.
ccmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    String line = "";
    try {{ line = ctx.getInputString(); }} catch (Throwable t) {{ line = ""; }}
    if (line == null) line = "";
    String q = line.trim();
    if (q.startsWith("/")) q = q.substring(1).trim();
    int sp = q.indexOf(' ');
    String head = (sp < 0 ? q : q.substring(0, sp)).toLowerCase();
    if (head.equals("craft") || head.equals("recipes")) q = sp < 0 ? "" : q.substring(sp + 1);
    {PKG}.CraftPage cp = new {PKG}.CraftPage(pr, (String) null);
    cp.query = {PKG}.CraftPage.cleanQuery(q);
    player.getPageManager().openCustomPage(ref, store, cp);
  }} catch (Throwable t) {{ {PKG}.SackPool.warn("/craft failed: " + t); pr.sendMessage({MSG}.raw("[SkyySacks] could not open crafting")); }}
}}""", ccmd))
''')

# ---------------- ProcTask: pay the Smithing ledger ----------------
rep('ptk.addField(CtField.make("public static long LASTWARN;", ptk))' + LF,
    'ptk.addField(CtField.make("public static long LASTWARN;", ptk))' + LF
    + 'ptk.addField(CtField.make("public static long XPWARN;", ptk))' + LF
    + 'ptk.addField(CtField.make("public static final int XP_CALL = 1000;", ptk))' + LF)
rep('ptk.addMethod(CtNewMethod.make(f"""' + LF + 'public void run() {{' + LF + '  try {{' + LF + '    if (pr == null || !pr.isValid()) return;' + LF
    + '    java.util.UUID nowWorld = pr.getWorldUuid();' + LF + '    if (nowWorld == null || !nowWorld.equals(this.expectedWorld)) return;' + LF
    + '    java.util.UUID u = pr.getUuid();' + LF + '    String k = {PKG}.SackPool.pkey(u);' + LF + '    epochCheck(u, k);' + LF,
    r'''# 0.7.3 Smithing (research/Smithing-Smelting-Spec.md 4.1, research/Alchemy-Skill-Spec.md 7.2): pay the Furnace units ProcBench.finishUnit
# counted, once per recipe per run, through SkyySkills' skill:fn:craftxp {uuid, recipeId, count, "sacks:furnace", expectKey}. Only when the
# key this run advanced is the settled key (a switch has settled; the same gate as the bench link). A Number answer drains exactly the
# reported count (units finished meanwhile stay); no function (SkyySkills missing or older than 0.4) or an error keeps the ledger.
# At most XP_CALL units per call (the rest goes on the next 1 s run): SkyySkills answers 0 (= drop it) for a call over its
# bridge.maxXpPerCall (500k base XP, checked before its multiplier), so a big ledger (up to XP_CAP = 10,000 units of a
# 50 XP bar, or a raised smithing.xp.* value) must never go out in one call and be dropped.
# The bridge call runs with no lock of ours held (xpList / takeXp are separate synchronized calls).
ptk.addMethod(CtNewMethod.make(f"""
public static void drainXp(java.util.UUID u, String k, {PKG}.ProcBench pb) {{
  java.util.ArrayList l = pb.xpList();
  if (l.isEmpty()) return;
  if (!k.equals({PKG}.SackPool.settledKey(u))) return;
  Object f = {PKG}.SackPool.bridge().get("skill:fn:craftxp");
  if (!(f instanceof java.util.function.Function)) return;
  for (int i = 0; i < l.size(); i++) {{
    Object[] e = (Object[]) l.get(i);
    String recipe = (String) e[0];
    int n = ((Integer) e[1]).intValue();
    if (n <= 0) continue;
    if (n > XP_CALL) n = XP_CALL;
    Object got = null;
    try {{
      got = ((java.util.function.Function) f).apply(new Object[] {{ u, recipe, Integer.valueOf(n), "sacks:furnace", k }});
    }} catch (Throwable t) {{
      long now = System.currentTimeMillis();
      if (now - XPWARN > 60000L) {{ XPWARN = now; {PKG}.SackPool.warn("smithing xp: skill:fn:craftxp failed (ledger kept, retried): " + t); }}
      return;
    }}
    if (got instanceof Number) {{
      pb.takeXp(recipe, n);
      {PKG}.ProcStore.markDirty(k);
      {PKG}.CraftLog.later(k, "SMITHING " + recipe + " x" + n + " -> " + ((Number) got).longValue() + " xp");
    }}
  }}
}}""", ptk))
''' + 'ptk.addMethod(CtNewMethod.make(f"""' + LF + 'public void run() {{' + LF + '  try {{' + LF + '    if (pr == null || !pr.isValid()) return;' + LF
    + '    java.util.UUID nowWorld = pr.getWorldUuid();' + LF + '    if (nowWorld == null || !nowWorld.equals(this.expectedWorld)) return;' + LF
    + '    java.util.UUID u = pr.getUuid();' + LF + '    String k = {PKG}.SackPool.pkey(u);' + LF + '    epochCheck(u, k);' + LF)
rep('        pr.sendMessage({MSG}.raw("[SkyySacks] Your " + pb.bench + " ran out of fuel - load more in /craft."));' + LF
    + '      }}' + LF + '    }}' + LF,
    '        pr.sendMessage({MSG}.raw("[SkyySacks] Your " + pb.bench + " ran out of fuel - load more in /craft."));' + LF
    + '      }}' + LF + '    }}' + LF
    + '    if (m != null) {{' + LF
    + '      Object fo = m.get("Furnace");' + LF
    + '      if (fo instanceof {PKG}.ProcBench) drainXp(u, k, ({PKG}.ProcBench) fo);' + LF
    + '    }}' + LF)

# ---------------- plugin: config, old Alchemy page id, ready line ----------------
rep('  {PKG}.ProcStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("processing");' + LF,
    '  {PKG}.ProcStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("processing");' + LF
    + '  {PKG}.SackCfg.FILE = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("config.properties");' + LF
    + '  {PKG}.SackCfg.reload();' + LF)
rep('"SkyySacksAlchemy", new {PKG}.CraftPageFactory("A:alch"));',
    '"SkyySacksAlchemy", new {PKG}.CraftPageFactory("A:craft"));')
rep('ready - /pd, /craft (Crafting, Alchemy, timed Furnace/Tannery queues), right-click a magic bag; workbenches craft from your bags; storage per profile (pkey)',
    'ready - /pd, /craft (Crafting, Smithing, Farming, search, timed Furnace/Tannery queues - Furnace pays Smithing XP, Collections), right-click a magic bag; benches craft from your bags (their ingredients first); storage per profile (pkey)')
rep('for c in (defs, sp, pjob,', 'for c in (defs, sp, scfg, pjob,')

# ---------------- review fix: delete the dead pre-inline markup (BTN_STYLE / rows / SACKS_UI) and its ROWS constant ----------------
# Unused since the inline pages (files = {} is what B.assemble gets; SACKS_UI was never written into the jar), but it declared element
# ids with underscores (s_row_N, s_name_N, s_N_w1, s_caps, s_prev, ...) - HANDOFF section 2 rule 1 - and read like working page markup.
swap('BTN_STYLE = """@Btn = TextButtonStyle(' + LF, '""" % rows' + LF + LF,
     '# (0.7.3 review fix: the dead pre-inline bag page markup - underscore ids, never shipped - was deleted; every page is built inline)' + LF + LF)
rep(LF + 'ROWS = 12' + LF, '')

# ---------------- assets: Farming bag text mentions cooked dishes ----------------
rep('"Farming": "plants, food, fish and life essence"', '"Farming": "plants, food and cooked dishes, fish and life essence"')

# ---------------- checks ----------------
assert '"A:alch"' not in s, "Alchemy tab left"
assert "m.rebuild(caps);" not in s and "materials(p, k);" not in s, "a mirror rebuild without the wanted set is left"
assert s.count("public static String settledKey(java.util.UUID u) {") == 1, "settledKey changed"
assert 'b.get("profile:busy:" + u.toString()) != null) return null;' in s, "busy gate lost"
assert "    String k = {PKG}.SackPool.settledKey(u);" + LF + "    if (k == null) {{" + LF + "      {WM} wm0" in s, "CraftLinkTask not on settledKey"
assert s.count("{BT}.Validating") == 1 and s.count('.append("@SearchQuery", "#SkyyCSearch.Value")') == 2, "search bindings"
assert s.index("public static synchronized void reload() {") < s.index("try {{ {PKG}.SackCfg.reload(); }}"), "SackCfg after SackSaver"
assert s.index("public static boolean retiredBench(String id) {") < s.index("public static java.util.HashMap accessories("), "retiredBench order"
assert s.index("public static void addInputs(java.util.Set s,") < s.index("public static java.util.HashSet wantedOf("), "addInputs order"
assert s.index("public synchronized java.util.ArrayList xpList() {") < s.index("public static void drainXp("), "xpList order"
assert s.count("public String rebuild(java.util.HashMap caps, java.util.Set wanted) {{") == 1
assert "SackCfg.SEARCH.get()" in s and "setAllowsExtraArguments(true);" in s
assert "cp.live(" not in s and '"prefresh"' in s, "periodic live() refresh still wired"
# review fixes
assert "public void live(" not in s and "this.liveOn" not in s and "this.liveSig" not in s and "this.liveAt" not in s, "live() refresh state left"
assert 'CtField.make("public boolean liveOn;"' not in s and 'CtField.make("public String liveSig;"' not in s, "live() fields left"
assert "SACKS_UI =" not in s and "BTN_STYLE =" not in s and "#s_" not in s and "ROWS = " not in s and "range(ROWS)" not in s, "dead pre-inline markup left"
assert 'tabId.startsWith("F:")' not in s and 'tabId.startsWith("B:")' not in s, "legacy F: / B: tab branches left"
assert "Files.write(FILE, txt.getBytes" not in s and 'FILE.resolveSibling(FILE.getFileName().toString() + ".tmp")' in s, "config.properties not written atomically"
assert s.index("public static boolean instantProc(String id) {") < s.index("public static boolean tableOnly("), "instantProc order"
assert s.count("instantProc(br[i].id)") == 2, "Salvagebench exemption missing in tableOnly / benchRecipes"

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
